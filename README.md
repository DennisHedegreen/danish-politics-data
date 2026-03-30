# Danish Politics Data

A data exploration tool for journalists and researchers. Cross-references Danish Folketing election results with socioeconomic municipal data.

Built by [Hedegreen Research](https://hedegreenresearch.com).

---

## What it does

Pick an election year, one or more parties, and one or more municipality factors from the current public factor layer. That layer now reads from normalized municipality-safe factor files instead of mixing raw DST tables directly into the app.

Current public factors include:

- population
- education
- income
- employment
- welfare
- crime
- cars
- age 65+
- turnout
- immigration share
- population density
- unemployment

`Divorces` remains in the system conceptually, but the public factor is currently withheld until the correct municipality-total source path is locked. Municipality vote share runs from `2007` to `2026`, with `2026` bridged from the official `VALG` export before the familiar Statistikbanken municipality tables catch up. The tool computes the Pearson correlation across all 98 Danish municipalities and tells you whether a pattern exists — and how strong it is.

**It surfaces patterns. It does not explain them.**

---

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

To rebuild the normalized public factor layer:

```bash
python fetch_dst.py
```

To fetch and aggregate the official 2026 election bridge from `data.valg.dk`:

```bash
python fetch_valg_2026.py
```

---

## Data sources

| Dataset | Source | Table | Licence |
|---|---|---|---|
| Party vote share per municipality, 2007–2022 | Danmarks Statistik | FVPANDEL | CC 4.0 BY |
| Party vote share per municipality, 2026 bridge | Official `VALG` public export aggregated from polling-area level | JSON over SFTP | Official public source |
| Raw votes per municipality | Danmarks Statistik | FVKOM | CC 4.0 BY |
| National votes 1953–2022 | Straubinger/folketingsvalg | — | — |
| Avg. disposable income | Danmarks Statistik | INDKP101 | CC 4.0 BY |
| Social assistance recipients | Danmarks Statistik | AUK01 | CC 4.0 BY |
| Reported crimes | Danmarks Statistik | STRAF11 | CC 4.0 BY |
| Passenger cars | Danmarks Statistik | BIL707 | CC 4.0 BY |
| Divorces | Danmarks Statistik | SKI125 | CC 4.0 BY |
| Full-time employed | Danmarks Statistik | LBESK69 | CC 4.0 BY |
| Population | Danmarks Statistik | FOLK1AM + legacy FOLK1A bridge | CC 4.0 BY |
| Higher education share | Danmarks Statistik | HFUDD11 | CC 4.0 BY |
| Voter turnout | Danmarks Statistik | FVKOM-derived | CC 4.0 BY |
| Immigration share | Danmarks Statistik | FOLK1E | CC 4.0 BY |
| Population density | Danmarks Statistik | ARE207 + population bridge | CC 4.0 BY |
| Unemployment rate | Danmarks Statistik | AUP02 | CC 4.0 BY |

All Danmarks Statistik data: **CC 4.0 BY — Danmarks Statistik, www.dst.dk**

---

## What this tool is not

- Not a prediction model
- Not an argument for any political position
- Correlation ≠ causation. A pattern in the data does not mean one variable causes the other.
- Municipal-level patterns do not describe individual voters (ecological fallacy)

See [METHODOLOGY.md](METHODOLOGY.md) for the full scientific methodology, bias rules, and known limitations.

---

## Pages

| Page | What it shows |
|---|---|
| Explore | Guided discovery: pick factor + year + party, find patterns |
| Compare municipalities | Side-by-side socioeconomic and voting profile for two municipalities |
| By Municipality | All data for one municipality across all election years |
| National trends | Vote share trends 1953–2022 at national level |
| About & sources | Data sources, methodology, licence |

---

## Project structure

```
app.py                          Main Streamlit application
fetch_dst.py                    Builds the normalized public factor layer from DST sources
fetch_valg_2026.py              Aggregates the official 2026 VALG export to municipality CSVs
requirements.txt
METHODOLOGY.md                  Scientific methodology, bias rules, limitations
FLOW.md                         UI and logic flow documentation
internal/
  raw/                          Reserved for bridge / special-source raw inputs
provenance/                     Public-safe ingest manifests and provenance notes
denmark/
  factors/                      Normalized public municipality factor layer
  folketing/                    Election results (FVPANDEL, 2026 VALG bridge, FVKOM, Straubinger)
  socioeconomic/                Municipal socioeconomic data (income, crime, etc.)
```
