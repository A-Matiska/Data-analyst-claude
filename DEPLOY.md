# Nasazení dashboardu na web

Dashboard (`src/dashboard.py`, Streamlit) lze **zdarma** nasadit na **Streamlit Community Cloud** a sdílet odkazem. Běží pak v prohlížeči na počítači, tabletu i mobilu (responzivní).

## Předpoklady

- Kód na GitHubu (✓ repo `A-Matiska/Data-analyst-claude`).
- Účet na <https://streamlit.io/cloud> (přihlášení přes GitHub, zdarma).
- Anthropic API klíč (pro AI insighty).

## Kroky

1. Jdi na <https://share.streamlit.io> a přihlas se přes GitHub (povol přístup k repozitáři).
2. Klikni **Create app → Deploy a public app from GitHub**.
3. Vyplň:
   - **Repository:** `A-Matiska/Data-analyst-claude`
   - **Branch:** `claude/beautiful-meitner-538oe8` (nebo `main` po sloučení)
   - **Main file path:** `src/dashboard.py`
4. Rozbal **Advanced settings → Secrets** a vlož (formát TOML):
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   APP_PASSWORD = "zvol-si-heslo"

   # Volitelné - jen když chceš i zdroj dat "Google Ads (živě)".
   # Stejné hodnoty jako v google-ads.yaml (viz README.md).
   GOOGLE_ADS_DEVELOPER_TOKEN = "..."
   GOOGLE_ADS_CLIENT_ID = "...apps.googleusercontent.com"
   GOOGLE_ADS_CLIENT_SECRET = "GOCSPX-..."
   GOOGLE_ADS_REFRESH_TOKEN = "1//..."
   GOOGLE_ADS_LOGIN_CUSTOMER_ID = "1234567890"
   GOOGLE_ADS_CUSTOMER_ID = "1234567890"
   ```
5. Klikni **Deploy**. Za chvilku dostaneš veřejnou URL (např. `https://<název>.streamlit.app`).

## 🔒 Bezpečnost (důležité)

- **Nastav `APP_PASSWORD`.** Bez něj je aplikace veřejná a kdokoli s odkazem může klikat na „Vygenerovat AI insighty“ → čerpat tvůj Claude kredit. S heslem si dashboard při otevření vyžádá přístup.
- **API klíč patří jen do Secrets**, nikdy do kódu ani do `.env` v gitu.
- Data, která do dashboardu nahraješ, jdou na servery Streamlitu a (při AI insightu) k Anthropicu. U citlivých dat zvaž, co nahráváš.

## 📱 Responzivní zobrazení

Dashboard používá široké rozložení a tabulky/grafy přes celou šířku, takže se škáluje na desktop, tablet i mobil; na úzkém displeji se karty KPI poskládají pod sebe a postranní panel se schová do menu.

## 🔄 Aktualizace

Po každém pushi do zvolené větve se aplikace **automaticky znovu nasadí**.

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
| Zapier Free: 100 tasků/měsíc (při automatickém tahání dat) | Automatický tok dat z Google Ads se zastaví | Upgrade na Starter ($29.99/měs) | ~700 Kč/měsíc |
| Vysoký objem AI insightů | Anthropic účet narazí na rate limit tieru, nebo faktura roste | Kratší souhrn dat, méně časté generování, levnější model (Sonnet/Haiku) | závisí na objemu |

### Když něco nesedí

- **Aplikace se nenaběhne**: zkontroluj logy (ikona **Manage app → Logs** vpravo dole ve Streamlit Cloud).
- **AI insighty nefungují**: chybí `ANTHROPIC_API_KEY` v **Secrets**.
- **Dashboard je veřejně přístupný**: chybí `APP_PASSWORD` v **Secrets** — bez něj může kdokoli s odkazem čerpat tvůj Claude kredit.

## Alternativy

Stejný dashboard zvládnou i **Hugging Face Spaces**, **Render** nebo **Railway** — postup je obdobný: napoj repo, spouštěcí příkaz `streamlit run src/dashboard.py`, a tajné hodnoty nastav jako proměnné prostředí / secrets.
