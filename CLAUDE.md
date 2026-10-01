# Project: Data Analyst

Česká platforma pro analýzu dat: automatická analýza CSV (statistiky, anomálie, trendy), stahování výkonu kampaní z Google Ads API (GAQL) a AI insighty přes Claude. UI je Streamlit dashboard. Hlavní use-case: marketingová analytika účtu „panopro".

> **Aktuální stav práce:** viz [docs/STATUS.md](docs/STATUS.md) — kde jsme skončili / co dál.

## Commands
- Install: `pip install -r requirements.txt`
- Run dashboard: `streamlit run src/dashboard.py` (http://localhost:8501)
- Analýza CSV: `python -m src.analyzer data/soubor.csv`
- AI insighty: `python -m src.ai data/soubor.csv`
- Google Ads: `python -m src.gads --check` (test připojení) | `python -m src.gads --report keywords --days 30` | `--customer-id … --csv data/out.csv`
- OAuth token: `python -m src.generate_refresh_token --update-yaml`
- Deploy: push do GitHub (A-Matiska/Data-analyst-claude) → Streamlit Community Cloud auto-redeploy; alternativně Azure App Service (DEPLOY_AZURE.md)

## Where things live
- src/analyzer.py   jádro analýzy (pandas, statistiky, anomálie)
- src/gads.py       Google Ads konektor (GAQL: kampaně/keywords/ads/trendy)
- src/ai.py         Claude insighty (Anthropic API)
- src/dashboard.py  Streamlit UI (upload CSV, grafy, AI insighty)
- data/             vstupní CSV | reports/ generované reporty
- DEPLOY.md / DEPLOY_AZURE.md  návody na nasazení

## Rules
- Tajnosti jen lokálně (obojí v .gitignore): .env (ANTHROPIC_API_KEY, GOOGLE_ADS_CUSTOMER_ID) a google-ads.yaml (developer_token, client_id/secret, refresh_token, login_customer_id).
- Google Ads vrací náklady v mikros (1 000 000 = 1 jednotka) — konektor převádí automaticky; login_customer_id je MCC účet, customer_id cílový účet.
- Na Streamlit Cloud vždy nastavit APP_PASSWORD secret — bez něj kdokoli s URL čerpá API kredity.
- Citlivá data analyzovat lokálně (upload na dashboard jde přes Streamlit servery).
