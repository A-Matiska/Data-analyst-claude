"""
Vygeneruje OAuth2 refresh_token pro Google Ads API.

Spustí OAuth2 flow (otevře prohlížeč), přihlásíš se Google účtem, který má
přístup k účtu panopro, a skript vypíše (a volitelně rovnou zapíše do
google-ads.yaml) refresh_token.

Použití:
    # client_id/secret se vezmou z google-ads.yaml (pokud tam už jsou)
    python -m src.generate_refresh_token

    # nebo z JSON staženého z Google Cloud Console (typ Desktop app)
    python -m src.generate_refresh_token --client-secrets-file client_secret.json

    # nebo přímo z argumentů
    python -m src.generate_refresh_token --client-id XXX --client-secret YYY

    # a rovnou token zapsat do google-ads.yaml
    python -m src.generate_refresh_token --update-yaml
"""

import argparse
import json
from pathlib import Path

# Google Ads API vyžaduje tento OAuth scope
SCOPES = ["https://www.googleapis.com/auth/adwords"]

DEFAULT_YAML = "google-ads.yaml"


def _client_config_from_pair(client_id: str, client_secret: str) -> dict:
    """Sestaví 'installed' client config z dvojice client_id / client_secret."""
    return {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }


def _read_yaml(path: str):
    """Načte google-ads.yaml, nebo vrátí None když neexistuje."""
    p = Path(path)
    if not p.exists():
        return None
    import yaml

    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_client_config(args) -> dict:
    """Zjistí client config pro OAuth flow z argumentů nebo souborů."""
    # 1) JSON z Cloud Console (obsahuje klíč "installed" nebo "web")
    if args.client_secrets_file:
        with open(args.client_secrets_file, "r", encoding="utf-8") as f:
            return json.load(f)
    # 2) přímo z argumentů
    if args.client_id and args.client_secret:
        return _client_config_from_pair(args.client_id, args.client_secret)
    # 3) z google-ads.yaml
    cfg = _read_yaml(args.update_yaml or DEFAULT_YAML)
    if cfg and cfg.get("client_id") and cfg.get("client_secret"):
        return _client_config_from_pair(cfg["client_id"], cfg["client_secret"])
    raise SystemExit(
        "Chybí client_id/client_secret. Zadej --client-secrets-file, nebo "
        "--client-id a --client-secret, nebo je dej do google-ads.yaml."
    )


def update_yaml_refresh_token(path: str, refresh_token: str):
    """Zapíše refresh_token do google-ads.yaml (zachová ostatní řádky)."""
    p = Path(path)
    lines = p.read_text(encoding="utf-8").splitlines() if p.exists() else []

    out = []
    written = False
    for line in lines:
        if line.strip().startswith("refresh_token:"):
            out.append(f"refresh_token: {refresh_token}")
            written = True
        else:
            out.append(line)
    if not written:
        out.append(f"refresh_token: {refresh_token}")

    p.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Vygeneruje OAuth2 refresh_token pro Google Ads API."
    )
    parser.add_argument(
        "--client-secrets-file", help="JSON klienta z Google Cloud Console"
    )
    parser.add_argument("--client-id", help="OAuth2 client_id")
    parser.add_argument("--client-secret", help="OAuth2 client_secret")
    parser.add_argument(
        "--update-yaml",
        nargs="?",
        const=DEFAULT_YAML,
        help=f"Zapíše token do google-ads.yaml (default {DEFAULT_YAML})",
    )
    parser.add_argument(
        "--port", type=int, default=0, help="Port lokálního serveru (0 = náhodný)"
    )
    args = parser.parse_args()

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as exc:
        raise SystemExit(
            "Chybí 'google-auth-oauthlib'. Spusť: pip install google-ads"
        ) from exc

    client_config = load_client_config(args)

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    # otevře prohlížeč a zachytí návrat na http://localhost
    # access_type=offline + prompt=consent zaručí, že se vrátí refresh_token
    flow.run_local_server(
        port=args.port,
        access_type="offline",
        prompt="consent",
    )
    creds = flow.credentials

    print("\n" + "=" * 60)
    print("[OK] refresh_token vygenerován:")
    print(creds.refresh_token)
    print("=" * 60)

    if args.update_yaml:
        update_yaml_refresh_token(args.update_yaml, creds.refresh_token)
        print(f"[OK] Zapsáno do {args.update_yaml}")
    else:
        print("Vlož ho do google-ads.yaml jako:  refresh_token: <token>")


if __name__ == "__main__":
    main()
