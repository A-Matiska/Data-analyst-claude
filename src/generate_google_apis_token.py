"""Vygeneruje refresh token pro Search Console + GA4 (+ Google Ads) v JEDNOM souhlasu.

Použití:  python src/generate_google_apis_token.py
Vezme client_id/client_secret z google-ads.yaml (stávající OAuth aplikace),
otevře prohlížeč pro souhlas a token uloží do google-apis.yaml (google-ads.yaml se NEMĚNÍ).
"""
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/adwords",
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/analytics.readonly",
]
ROOT = Path(__file__).resolve().parent.parent
ADS_YAML = ROOT / "google-ads.yaml"
OUT_YAML = ROOT / "google-apis.yaml"

def yaml_vals(path):
    vals = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line and not line.strip().startswith("#"):
            k, v = line.split(":", 1)
            vals[k.strip()] = v.strip()
    return vals

def main():
    from google_auth_oauthlib.flow import InstalledAppFlow
    ads = yaml_vals(ADS_YAML)
    client_config = {"installed": {
        "client_id": ads["client_id"],
        "client_secret": ads["client_secret"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }}
    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    flow.run_local_server(port=0, access_type="offline", prompt="consent")
    creds = flow.credentials
    OUT_YAML.write_text(
        f"# OAuth pro Search Console + GA4 + Ads (vygenerováno generate_google_apis_token.py)\n"
        f"client_id: {ads['client_id']}\n"
        f"client_secret: {ads['client_secret']}\n"
        f"refresh_token: {creds.refresh_token}\n",
        encoding="utf-8",
    )
    print(f"\n[OK] Token uložen do {OUT_YAML} — google-ads.yaml zůstal beze změny.")

if __name__ == "__main__":
    main()
