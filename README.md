# Marketing Dashboard

Inteligentní nástroj pro analýzu dat s podporou Claude AI. Automaticky načítá CSV soubory, generuje statistické analýzy a vytváří insights.

## ✨ Vlastnosti

- 📊 Automatická analýza CSV souborů
- 📈 Deskriptivní statistika a trendy
- 🔍 Detekce anomálií
- 📝 Generování reportů
- 🤖 Integrace s Claude AI
- 💾 Podpora více datových formátů

## 🚀 Instalace

```bash
git clone https://github.com/A-Matiska/Data-analyst-claude.git
cd Data-analyst-claude
pip install -r requirements.txt
```

## 📖 Použití

```python
from src.analyzer import DataAnalyzer

# Načti a analyzuj data
analyzer = DataAnalyzer('data/your_file.csv')
summary = analyzer.generate_summary()
print(summary)
```

### Příklady

```bash
# Analýza jediného souboru
python -m src.analyzer data/sample.csv

# Analýza více souborů
python -m src.analyzer data/*.csv
```

## 📣 Napojení na Google Ads

Projekt umí stáhnout data přímo z Google Ads API (např. z účtu **panopro**)
a rovnou je zanalyzovat.

### 1. Co budeš potřebovat

| Údaj | Kde ho získáš |
|------|---------------|
| **Developer token** | Google Ads → nástroje → API Center (na MCC účtu) |
| **OAuth2 client_id + client_secret** | Google Cloud Console → Credentials → OAuth client (typ *Desktop app*) |
| **Refresh token** | Vygeneruje přiložený skript `python -m src.generate_refresh_token` (viz níže) |
| **login_customer_id** | ID správcovského (MCC) účtu, bez pomlek |
| **customer_id** | ID účtu *panopro*, ze kterého stahuješ data |

### 2. Konfigurace

Zkopíruj šablony a doplň své hodnoty (oba soubory jsou v `.gitignore`,
takže se tokeny nikdy nedostanou do gitu):

```bash
cp google-ads.yaml.example google-ads.yaml   # tokeny pro API
cp .env.example .env                          # GOOGLE_ADS_CUSTOMER_ID + ANTHROPIC_API_KEY
```

#### Vygenerování refresh_token

Do `google-ads.yaml` vyplň `developer_token`, `client_id` a `client_secret`,
pak spusť skript — otevře prohlížeč, přihlásíš se Google účtem s přístupem
k účtu *panopro* a token se rovnou zapíše do `google-ads.yaml`:

```bash
python -m src.generate_refresh_token --update-yaml
```

> 💡 OAuth client musí být v Google Cloud Console typu **Desktop app**.

### 3. Použití

```python
from src import GoogleAdsConnector

# Konfigurace se načte z google-ads.yaml; customer_id z .env nebo přímo:
connector = GoogleAdsConnector(customer_id="123-456-7890")

# Výkon kampaní za posledních 30 dní jako pandas DataFrame
df = connector.fetch_campaign_performance(days=30)

# Další hotové reporty:
df = connector.fetch_keyword_performance(days=30)   # klíčová slova
df = connector.fetch_ad_performance(days=30)        # inzeráty
df = connector.fetch_daily_trends(days=30)          # denní trend (časová řada)

# Rovnou souhrnná analýza (statistiky, outliers, chybějící hodnoty)
connector.to_analyzer(df, name="panopro").print_report()

# Nebo libovolný vlastní GAQL dotaz
df = connector.search("SELECT campaign.name, metrics.clicks FROM campaign")
```

Z příkazové řádky:

```bash
# Nejdřív ověř připojení (minimální živé volání, vypíše dostupné účty)
python -m src.gads --check

# Stáhne kampaně a uloží do CSV + vytiskne report
python -m src.gads --customer-id 123-456-7890 --days 30 --csv data/panopro.csv

# Jiný report: campaigns (default) | keywords | ads | trends
python -m src.gads --report keywords --days 30
```

> ⚠️ Ceny vrací Google Ads v *micros* (1 000 000 = 1 jednotka měny).
> Konektor je automaticky převede (`cost_micros` → `cost`).

## 🤖 AI insighty (Claude)

Analyzovaná data umí komentovat přímo Claude — vrátí srozumitelné insighty
a doporučení. Klíč dej do `.env` jako `ANTHROPIC_API_KEY` (je v `.gitignore`):

```python
from src import GoogleAdsConnector, DataAnalyzer

# Z Google Ads dat:
connector = GoogleAdsConnector(customer_id="123-456-7890")
df = connector.fetch_campaign_performance(days=30)
print(connector.to_analyzer(df, name="panopro").ai_insights(extra="e-shop"))

# Nebo z jakéhokoli CSV:
print(DataAnalyzer("data/panopro.csv").ai_insights())
```

Z příkazové řádky (CSV → analýza → AI insighty):

```bash
python -m src.ai data/panopro.csv
```

> 💡 Používá model `claude-opus-4-8` přes oficiální Anthropic SDK. Klíč nikdy
> nedávej do gitu — patří jen do `.env`.

## 📊 Interaktivní dashboard (Streamlit)

Vizuální rozhraní v prohlížeči — nahraješ/vybereš CSV, uvidíš přehled,
statistiky a grafy, a na jedno tlačítko k tomu Claude doplní AI insighty.

```bash
streamlit run src/dashboard.py
```

Otevře se v prohlížeči (typicky http://localhost:8501). V levém panelu vyber
zdroj dat: nahraj CSV, vyber soubor ze složky `data/`, nebo (když je
nakonfigurovaný `google-ads.yaml` — viz výše) zvol **Google Ads (živě)** a
dashboard si data stáhne přímo z API, bez ručního exportu. Pro AI insighty
stačí mít `ANTHROPIC_API_KEY` v `.env`.

Nasazení do cloudu (Streamlit Community Cloud, Azure) nemá soubor
`google-ads.yaml` na disku — přihlašovací údaje se pak berou ze Secrets
(`GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_CLIENT_ID`,
`GOOGLE_ADS_CLIENT_SECRET`, `GOOGLE_ADS_REFRESH_TOKEN`,
`GOOGLE_ADS_LOGIN_CUSTOMER_ID`, `GOOGLE_ADS_CUSTOMER_ID`) — viz DEPLOY.md.

## 💰 Náklady a časová náročnost

> Orientační hodnoty pro plánování (kurz ~24 Kč/USD). Skutečnost závisí na
> objemu dat, četnosti AI insightů a zvolené variantě hostingu.

### Nákladové položky (provozní, měsíčně)

| Položka | Popis | Orientační náklad |
|---------|-------|-------------------|
| **Hosting** | kde web běží | **0 Kč** (free tiery) až **~350 Kč/měs** (Azure App Service B1) |
| **Claude API (Anthropic)** | AI insighty, platba za použití | **jednotky Kč** / insight → **desítky–nižší stovky Kč/měs** |
| **Živá data z Google Ads** | napojení přímo v dashboardu (`src/gads.py`) | **0 Kč** (v ceně Google Ads API, žádná další služba není potřeba) |
| **Vlastní doména** (volitelné) | adresa místo `*.streamlit.app` | **~200–400 Kč/rok** (.cz) |
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
| Google Ads: Basic access, 15 000 operací/den | Nad limitem API na zbytek dne odmítá další dotazy (`RESOURCE_EXHAUSTED`) | Požádat o Standard access (vyšší limit, zdarma) | 0 Kč |
| Vysoký objem AI insightů | Anthropic účet narazí na rate limit tieru, nebo faktura roste | Kratší souhrn dat, méně časté generování, levnější model (Sonnet/Haiku) | závisí na objemu |

### Když něco nesedí

- **AI insighty nefungují**: chybí nebo je neplatný `ANTHROPIC_API_KEY` v `.env`.
- **Napojení na Google Ads selže**: zkontroluj `google-ads.yaml` (`developer_token`, `client_id`, `client_secret`, `refresh_token`) a že `login_customer_id` / `customer_id` jsou bez pomlek.
- **`DEVELOPER_TOKEN_NOT_APPROVED`**: Google Ads developer token ještě nemá schválený Basic access — použij testovací účet, nebo počkej na schválení.

## 📁 Struktura projektu

```
├── src/
│   ├── analyzer.py            # Hlavní analyzer pro data
│   ├── gads.py               # Konektor na Google Ads API
│   ├── ai.py                 # Claude AI insighty (Anthropic API)
│   ├── dashboard.py          # Interaktivní dashboard (Streamlit)
│   ├── generate_refresh_token.py  # OAuth2 refresh_token generátor
│   └── utils.py              # Pomocné funkce
├── data/                     # Složka pro vaše CSV data
├── reports/                  # Vygenerované reporty
├── google-ads.yaml.example   # Šablona konfigurace Google Ads
├── .env.example              # Šablona proměnných prostředí
├── requirements.txt          # Python závislosti
└── README.md                 # Tato dokumentace
```

## 🛠️ Technologie

- **Python 3.8+**
- **pandas** — manipulace s daty
- **numpy** — numerické výpočty
- **matplotlib** — vizualizace
- **google-ads** — napojení na Google Ads API
- **anthropic** — AI insighty přes Claude
- **streamlit** — interaktivní dashboard

## 📝 Příspěvky

Přispívání je vítáno! Prosím:

1. Forkuj projekt
2. Vytvoř feature branch (`git checkout -b feature/amazing-feature`)
3. Commitni změny (`git commit -m 'Add amazing feature'`)
4. Pushni branch (`git push origin feature/amazing-feature`)
5. Otevři Pull Request

## 📄 Licence

MIT License — viz LICENSE soubor

## 👤 Autor

Andrea Matis (@A-Matiska)

---

**Poznámka:** Tohoto projektu lze používat pro analýzu vlastních CSV data. Stačí umístit soubory do složky `data/`.
