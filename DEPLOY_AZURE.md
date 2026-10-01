# Nasazení na Azure App Service (Python + Streamlit)

Tento návod nasadí dashboard na **Azure App Service** (běží na tvém Azure, profesionální, vlastní doména). Po propojení s GitHubem se každá změna v `main` nasadí sama (přes GitHub Actions).

> ⚠️ Kroky v Azure portálu musíš udělat přihlášená do svého Azure účtu.
> Kód a konfigurace v repozitáři jsou už připravené (`startup.sh`,
> `requirements.txt`, `src/dashboard.py`).

## 1. Vytvoř Web App

1. Jdi na <https://portal.azure.com> → přihlas se.
2. Nahoře do vyhledávání napiš **App Services** → **Create** → **Web App**.
3. Vyplň:
   - **Resource Group**: vyber existující (klidně stejnou jako panopro-advisor) nebo vytvoř novou.
   - **Name**: např. `panopro-data-analyst` (bude v adrese `…azurewebsites.net`).
   - **Publish**: **Code**
   - **Runtime stack**: **Python 3.12**
   - **Operating System**: **Linux**
   - **Region**: nejbližší (např. West Europe)
   - **Pricing plan**: **B1** (Basic) pro plynulý běh; levnější je **F1 (Free)**, ale usadná a má limity.
4. **Review + create** → **Create**. Počkej na dokončení (~1 min).

## 2. Nastav spouštění (Startup Command)

1. Otevři vytvořenou Web App → vlevo **Configuration** → záložka **General settings**.
2. **Startup Command**: zadej
   ```bash
   startup.sh
   ```
3. **Web sockets**: přepni na **On** (Streamlit je potřebuje).
4. **Always on**: **On** (aby appka neusínala; dostupné na B1 a výš).
5. **Save**.

## 3. Nastav tajné hodnoty (API klíč, heslo)

1. Vlevo **Configuration** → záložka **Application settings** → **New application setting**.
2. Přidej:

   | Name | Value |
   |------|-------|
   | `ANTHROPIC_API_KEY` | tvůj klíč `sk-ant-...` |
   | `APP_PASSWORD` | zvolené heslo (volitelné) |
   | `WEBSITES_PORT` | `8000` |

   Volitelně, pro zdroj dat **Google Ads (živě)** (stejné hodnoty jako
   v `google-ads.yaml`, viz README.md):
   | Name | Value |
   |------|-------|
   | `GOOGLE_ADS_DEVELOPER_TOKEN` | developer token |
   | `GOOGLE_ADS_CLIENT_ID` | OAuth2 client_id |
   | `GOOGLE_ADS_CLIENT_SECRET` | OAuth2 client_secret |
   | `GOOGLE_ADS_REFRESH_TOKEN` | OAuth2 refresh_token |
   | `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | ID správcovského (MCC) účtu |
   | `GOOGLE_ADS_CUSTOMER_ID` | ID účtu *panopro* |

   > 💡 Tyhle názvy odpovídají standardu knihovny `google-ads` — jako
   > obyčejné proměnné prostředí (na rozdíl od Streamlit Cloud Secrets)
   > je konektor najde automaticky, žádné další nastavení není potřeba.
3. **Save** (appka se restartuje).

## 4. Propoj s GitHubem (automatické nasazení)

1. Vlevo **Deployment Center**.
2. **Source**: **GitHub** → autorizuj → vyber:
   - **Organization**: Traiva2911
   - **Repository**: Data-analyst-claude
   - **Branch**: main
3. **Save**. Azure vytvoří v repozitáři GitHub Actions workflow a spustí první nasazení. První build trvá pár minut (instaluje knihovny).

## 5. Otevři appku

- Nahoře na stránce Web App je **Default domain** (adresa `…azurewebsites.net`).
- Klikni na ni → měl by naskočit dashboard.

Hotovo! 🎉

---

## 💰 Náklady a časová náročnost

> Orientační hodnoty pro plánování (kurz ~24 Kč/USD). Skutečnost závisí na
> objemu dat, četnosti AI insightů a zvolené variantě hostingu.

### Nákladové položky (provozní, měsíčně)

| Položka | Popis | Orientační náklad |
|---------|-------|-------------------|
| **Hosting** | kde web běží | **0 Kč** (free tiery) až **~350 Kč/měs** (Azure App Service B1) |
| **Claude API (Anthropic)** | AI insighty, platba za použití | **jednotky Kč** / insight → **desítky–nižší stovky Kč/měs** |
| **Živá data z Google Ads** | napojení přímo v dashboardu (`src/gads.py`) | **0 Kč** (v ceně Google Ads API, žádná další služba není potřeba) |
| **Vlastní doména** (volitelné) | adresa místo `*.azurewebsites.net` | **~200–400 Kč/rok** (.cz) |
| **SSL / https** | zabezpečení spojení | **0 Kč** (v ceně hostingu) |

> 💡 Claude API se platí **navíc k hostingu**, nezávisle na variantě.
> Levnější model (Sonnet/Haiku) místo Opusu náklady na AI výrazně sníží.

### Kalkulace tokenů Anthropic API

Model `claude-opus-4-8` (viz `src/ai.py`) — oficiální ceny (červenec 2026):

| Parametr | Hodnota |
|----------|---------|
| Input | $5 / 1M tokenů |
| Output | $25 / 1M tokenů |
| Max output tokenů | 4 096 (nastaveno v `src/ai.py`) |
| Adaptivní thinking | zapnuto — přemýšlecí tokeny se počítají jako output |
| Průměrný vstup (souhrn dat v JSON) | ~800–1 500 tokenů (dle počtu sloupců a kategorií) |

**Příklad:** 50 vygenerování AI insightů/měsíc (běžné použití jednoho člověka):

- Input: 50 × 1 200 = 60 000 tokenů → $0,30 (~7 Kč)
- Output: 50 × 1 500 (odhad vč. thinking) = 75 000 tokenů → $1,88 (~45 Kč)
- **Celkem: ~52 Kč/měsíc**

> Při intenzivnějším použití (300 generování/měsíc, víc kampaní/uživatelů)
> → ~310 Kč/měsíc. Toto číslo je součástí řádku „Claude API (Anthropic)"
> v tabulce nákladových položek výše.

### Orientační náklad podle varianty hostingu

| Varianta hostingu | Náklad/měs |
|-------------------|------------|
| Streamlit Community Cloud | **0 Kč** |
| Render / Hugging Face Spaces | **0 Kč** (s uspáváním) až **~180 Kč** (always-on) |
| Azure Container Apps | **~0–200 Kč** (dle provozu) |
| Azure App Service (B1) | **~300–350 Kč** |
| Azure Static Web Apps (React varianta) | **0 Kč** (free tier) |

### Časová náročnost

| Fáze | Náročnost |
|------|-----------|
| Vývoj dashboardu (Python/Streamlit) | **hotovo** ✅ |
| Živé napojení na Google Ads API přímo v dashboardu | **hotovo** ✅ (zdroj dat „Google Ads (živě)“) |
| Implementace / nasazení na web | **15 min – 1 hod** (dle varianty) |
| Přestavba do React + Azure Static Web Apps (jako `panopro-advisor`) | **~3–6 člověkodnů** vývoje |

### Škálovací prahy

| Práh | Co se stane | Řešení | Náklad navíc |
|------|-------------|--------|--------------|
| Streamlit Community Cloud: 7 dní bez návštěvy | Appka „usne", první návštěva čeká ~30–60 s na probuzení | Přejít na Azure App Service s Always On, nebo nechat (jen UX) | 0 Kč, nebo ~300 Kč/měs |
| Azure App Service F1 (Free): 60 CPU minut/den | Appka po vyčerpání limitu přestane do půlnoci (UTC) reagovat | Upgrade na B1 (Basic) | ~300 Kč/měsíc |
| Zapier Free: 100 tasků/měsíc (při automatickém tahání dat) | Automatický tok dat z Google Ads se zastaví | Upgrade na Starter ($29.99/měs) | ~700 Kč/měsíc |
| Vysoký objem AI insightů | Anthropic účet narazí na rate limit tieru, nebo faktura roste | Kratší souhrn dat, méně časté generování, levnější model (Sonnet/Haiku) | závisí na objemu |

### Když něco nesedí

- **Application Error / nenaběhne**: zkontroluj **Log stream** (vlevo v menu). Nejčastěji chybí Startup Command (`bash startup.sh`) nebo `WEBSITES_PORT=8000`.
- **AI insighty nefungují**: chybí `ANTHROPIC_API_KEY` v Application settings.
- **Build dlouho trvá**: `requirements.txt` obsahuje i `google-ads` (nepovinné pro dashboard). Lze ho odebrat pro rychlejší build.
