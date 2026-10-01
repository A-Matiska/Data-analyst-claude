---
name: data-analyst-ops
description: Provozní úkony pro Data Analyst platformu — stažení dat z Google Ads, spuštění analýzy/AI insightů, nastavení OAuth tokenu, deploy dashboardu. Použij v tomto projektu, když uživatel chce stáhnout kampaně, analyzovat CSV, obnovit Google Ads přístup nebo nasadit dashboard.
---

# Data Analyst Ops — provoz Data Analyst platformy

## Stažení dat z Google Ads

1. Ověřit připojení: `python -m src.gads --check`
2. Stáhnout report: `python -m src.gads --report keywords --days 30 --csv data/vystup.csv` (report: campaigns | keywords | ads | trends)
3. `login_customer_id` je MCC (manažerský) účet, `customer_id` je cílový účet — nezaměňovat.
4. Náklady přicházejí v mikros (1 000 000 = 1 Kč/jednotka) — konektor převádí automaticky, není třeba ručně přepočítávat.

## Obnova OAuth přístupu

Pokud `--check` selže s chybou autorizace:
1. `python -m src.generate_refresh_token --update-yaml` — otevře prohlížeč, po přihlášení zapíše nový refresh_token do `google-ads.yaml`.
2. Vyžaduje desktop OAuth2 klienta (ne web/SPA) v Google Cloud Console.

## Analýza a AI insighty

- Rychlá analýza CSV: `python -m src.analyzer data/soubor.csv`
- AI insighty (Claude): `python -m src.ai data/soubor.csv`
- Interaktivně: `streamlit run src/dashboard.py` → upload CSV, grafy, AI insighty v prohlížeči na :8501

## Deploy dashboardu

**Streamlit Community Cloud (výchozí):**
1. `git push` do `A-Matiska/Data-analyst-claude`
2. Streamlit Cloud auto-redeploy z main file `src/dashboard.py`
3. V Secrets (TOML formát) musí být `ANTHROPIC_API_KEY` a **`APP_PASSWORD`** — bez hesla je dashboard veřejný a kdokoli s URL čerpá API kredity.

**Azure App Service (alternativa):** postup v `DEPLOY_AZURE.md`, běží na portu 8000 přes `startup.sh`.

## Pravidla

- `.env` a `google-ads.yaml` jen lokálně, v `.gitignore` — obsahují API klíč a Google Ads credentials.
- Citlivá data zpracovávat lokálně, ne přes veřejný Streamlit dashboard (upload jde přes Streamlit servery).
