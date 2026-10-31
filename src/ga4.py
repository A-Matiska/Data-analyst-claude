"""GA4 konektor — čte data webu (poptávky, tržby) napříč VŠEMI kanály, ne jen z reklam.

Použití:
  python -m src.ga4 --list                                  # vypíše dostupné GA4 property
  python -m src.ga4 --property 123456789 --events           # top události za období
  python -m src.ga4 --property 123456789 --event generate_lead   # rozpad události podle kanálu
  python -m src.ga4 --property 123456789 --trzby            # nákupy a tržby podle kanálu
  (místo --property lze alias: --web panopro / --web karavan, pokud je v google-apis.yaml
   řádek `property_panopro: <id>` / `property_karavan: <id>`)

Token: google-apis.yaml (scope analytics.readonly) — generuje generate_google_apis_token.py.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
TOKEN_YAML = ROOT / "google-apis.yaml"
DATA_API = "https://analyticsdata.googleapis.com/v1beta"
ADMIN_API = "https://analyticsadmin.googleapis.com/v1beta"


def _yaml_vals(path: Path) -> dict:
    vals = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line and not line.strip().startswith("#"):
            k, v = line.split(":", 1)
            vals[k.strip()] = v.strip()
    return vals


def _access_token() -> str:
    cfg = _yaml_vals(TOKEN_YAML)
    r = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": cfg["client_id"],
            "client_secret": cfg["client_secret"],
            "refresh_token": cfg["refresh_token"],
            "grant_type": "refresh_token",
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["access_token"]


class Ga4Connector:
    def __init__(self):
        self._tok = _access_token()
        self._hdr = {"Authorization": f"Bearer {self._tok}"}

    def list_properties(self) -> pd.DataFrame:
        rows, page = [], None
        while True:
            params = {"pageSize": 200, **({"pageToken": page} if page else {})}
            r = requests.get(f"{ADMIN_API}/accountSummaries", headers=self._hdr, params=params, timeout=60)
            r.raise_for_status()
            js = r.json()
            for acc in js.get("accountSummaries", []):
                for p in acc.get("propertySummaries", []):
                    rows.append({
                        "ucet": acc.get("displayName"),
                        "property_id": p["property"].split("/")[1],
                        "nazev": p.get("displayName"),
                    })
            page = js.get("nextPageToken")
            if not page:
                break
        return pd.DataFrame(rows)

    def _run_report(self, prop: str, body: dict) -> pd.DataFrame:
        r = requests.post(f"{DATA_API}/properties/{prop}:runReport", headers=self._hdr, json=body, timeout=120)
        r.raise_for_status()
        js = r.json()
        dims = [d["name"] for d in js.get("dimensionHeaders", [])]
        mets = [m["name"] for m in js.get("metricHeaders", [])]
        rows = []
        for row in js.get("rows", []):
            rec = {d: v["value"] for d, v in zip(dims, row.get("dimensionValues", []))}
            for m, v in zip(mets, row.get("metricValues", [])):
                try:
                    rec[m] = float(v["value"])
                except ValueError:
                    rec[m] = v["value"]
            rows.append(rec)
        return pd.DataFrame(rows)

    def top_events(self, prop: str, days: int = 30) -> pd.DataFrame:
        return self._run_report(prop, {
            "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
            "dimensions": [{"name": "eventName"}],
            "metrics": [{"name": "eventCount"}],
            "orderBys": [{"metric": {"metricName": "eventCount"}, "desc": True}],
            "limit": 40,
        })

    def event_by_channel(self, prop: str, event: str, days: int = 30) -> pd.DataFrame:
        return self._run_report(prop, {
            "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
            "dimensions": [{"name": "sessionDefaultChannelGroup"}],
            "metrics": [{"name": "eventCount"}],
            "dimensionFilter": {"filter": {"fieldName": "eventName",
                                           "stringFilter": {"value": event}}},
            "orderBys": [{"metric": {"metricName": "eventCount"}, "desc": True}],
        })

    def revenue_by_channel(self, prop: str, days: int = 30) -> pd.DataFrame:
        return self._run_report(prop, {
            "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
            "dimensions": [{"name": "sessionDefaultChannelGroup"}],
            "metrics": [{"name": "transactions"}, {"name": "purchaseRevenue"}, {"name": "sessions"}],
            "orderBys": [{"metric": {"metricName": "purchaseRevenue"}, "desc": True}],
        })


def _resolve_property(args) -> str:
    if args.property:
        return args.property
    if args.web:
        cfg = _yaml_vals(TOKEN_YAML)
        key = f"property_{args.web}"
        if key in cfg:
            return cfg[key]
        sys.exit(f"Alias '{args.web}' není v google-apis.yaml (chybí řádek `{key}: <id>`). "
                 f"Najdi id přes --list a řádek doplň.")
    sys.exit("Zadej --property <id>, --web <alias>, nebo --list.")


def main():
    ap = argparse.ArgumentParser(description="GA4 čtečka (poptávky a tržby napříč kanály)")
    ap.add_argument("--list", action="store_true", help="vypíše dostupné GA4 property")
    ap.add_argument("--property", help="GA4 property id")
    ap.add_argument("--web", help="alias z google-apis.yaml (property_<alias>)")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--events", action="store_true", help="top události za období")
    ap.add_argument("--event", help="rozpad konkrétní události podle kanálu")
    ap.add_argument("--trzby", action="store_true", help="nákupy a tržby podle kanálu")
    args = ap.parse_args()

    c = Ga4Connector()
    if args.list:
        df = c.list_properties()
        print(df.to_string(index=False) if len(df) else "(žádné property)")
        return
    prop = _resolve_property(args)
    if args.event:
        df = c.event_by_channel(prop, args.event, args.days)
        title = f"Událost '{args.event}' podle kanálu ({args.days} dní)"
    elif args.trzby:
        df = c.revenue_by_channel(prop, args.days)
        title = f"Tržby podle kanálu ({args.days} dní)"
    else:
        df = c.top_events(prop, args.days)
        title = f"Top události ({args.days} dní)"
    print(f"=== {title} — property {prop} ===")
    print(df.to_string(index=False) if len(df) else "(žádná data)")


if __name__ == "__main__":
    main()
