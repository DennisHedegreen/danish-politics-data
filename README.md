# Danish Politics Data

A data exploration tool for journalists and researchers. Cross-references Danish Folketing election results with socioeconomic municipal data.

Built by [Hedegreen Research](https://hedegreenresearch.com).

---

## What it does

Pick a factor (income, education, crime, cars, welfare, divorces, employment, age 65+), an election year (2007–2022), and one or more parties. The tool computes the Pearson correlation across all 98 Danish municipalities and tells you whether a pattern exists — and how strong it is.

**It surfaces patterns. It does not explain them.**

---

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

To re-fetch all data from Danmarks Statistik:

```bash
python fetch_dst.py
```

---

## Data sources

| Dataset | Source | Table | Licence |
|---|---|---|---|
| Party vote share per municipality | Danmarks Statistik | FVPANDEL | CC 4.0 BY |
| Raw votes per municipality | Danmarks Statistik | FVKOM | CC 4.0 BY |
| National votes 1953–2022 | Straubinger/folketingsvalg | — | — |
| Avg. disposable income | Danmarks Statistik | INDKP101 | CC 4.0 BY |
| Social assistance recipients | Danmarks Statistik | AUK01 | CC 4.0 BY |
| Reported crimes | Danmarks Statistik | STRAF11 | CC 4.0 BY |
| Passenger cars | Danmarks Statistik | BIL707 | CC 4.0 BY |
| Divorces | Danmarks Statistik | SKI125 | CC 4.0 BY |
| Full-time employed | Danmarks Statistik | LBESK69 | CC 4.0 BY |
| Population | Danmarks Statistik | FOLK1A | CC 4.0 BY |
| Higher education share | Danmarks Statistik | HFUDD11 | CC 4.0 BY |

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
fetch_dst.py                    Fetches/updates data from Danmarks Statistik API
requirements.txt
METHODOLOGY.md                  Scientific methodology, bias rules, limitations
FLOW.md                         UI and logic flow documentation
denmark/
  folketing/                    Election results (FVPANDEL, FVKOM, Straubinger)
  socioeconomic/                Municipal socioeconomic data (income, crime, etc.)
```
