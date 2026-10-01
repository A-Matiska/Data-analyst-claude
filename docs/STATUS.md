# Stav práce — Marketing Dashboard (Data-analyst)

> Krátký „kde jsme skončili / co dál" pro rychlý restart v novém chatu. Není to changelog.

**Aktualizováno:** 2026-10-01

## Kde jsme skončili
- **Živé napojení na Google Ads je hotové, sloučené do `main` a plně funkční** (PR #6, sloučen 2026-10-01). Dashboard má třetí zdroj dat „Google Ads (živě)" vedle CSV uploadu a složky `data/`.
- **Google Ads API Basic Access schválen 2026-08-27** (ticket 6-5664000040768) — 15 000 operací/den, stejný developer token jako v `google-ads.yaml`, žádná další akce potřeba.
- Poslední commity (2026-06-27 až 06-29): rebrand na „Marketing Dashboard" + UI/UX vylepšení (#4), Azure App Service build/deploy workflow, doladění vzhledu. Repo bylo mezitím přejmenováno na `A-Matiska/Data-analyst-claude`.
- Streamlit aplikace.

## Co dál
- Ověřit živé stažení dat na reálném účtu panopro (customer ID 433-578-8566 / 1332463219) přímo v nasazeném dashboardu.
- Deploy jen z `main`; feature práce přes větev/PR.
- Volitelný úklid: nefunkční workflow `.github/workflows/azure-static-web-apps-gray-bay-0f2a15b1e.yml` (vznikl omylem při experimentování s Azure Static Web Apps — nekompatibilní s Python/Streamlit projektem, nikomu nepřekáží, ale je to mrtvý kód).

## Klíčové soubory
- `CLAUDE.md`, `.claude/skills/data-analyst-ops/SKILL.md`, `requirements.txt`, `README.md`
