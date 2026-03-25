# Methodology — Danish Politics Data

## What this tool is

A data exploration tool for journalists and researchers. It cross-references Danish Folketing election results with socioeconomic municipal data from Danmarks Statistik.

The tool surfaces patterns. It does not explain them.

---

## What this tool is not

- It is not a prediction model.
- It is not an argument for any political position.
- It does not assign cause. A correlation between income and votes does not mean income causes voting behaviour — it means they move together across municipalities.
- It does not fill in missing data. If data is unavailable for a combination, nothing is shown.

---

## Data sources

| Dataset | Source | Coverage | Table |
|---|---|---|---|
| Folketing vote share per municipality | Danmarks Statistik | 2007, 2011, 2015, 2019, 2022 | FVPANDEL |
| National vote counts 1953–2022 | Straubinger/folketingsvalg (GitHub) | 1953–2022 | — |
| Avg. disposable income | Danmarks Statistik | 1987–2024 | INDKP101 |
| Social assistance recipients | Danmarks Statistik | 2007–present | AUK01 |
| Reported crimes | Danmarks Statistik | 2007–present | STRAF11 |
| Passenger cars | Danmarks Statistik | 2007–present | BIL707 |
| Divorces | Danmarks Statistik | 2007–present | SKI125 |
| Full-time employed per municipality | Danmarks Statistik | 2007–2022 (election quarters) | LBESK69 |
| Population (for per-capita) | Danmarks Statistik | 2008–2022 (election quarters) | FOLK1A |

All data from Danmarks Statistik is published under **CC 4.0 BY**.
Attribution: Danmarks Statistik, www.dst.dk

---

## How cross-referencing works

### Election year → population year

Per-capita metrics (welfare, crime, cars, divorces) require a population figure. We use the population from the quarter closest to the election:

| Election | Population quarter used |
|---|---|
| 2007 | 2008 Q1 |
| 2011 | 2011 Q1 |
| 2015 | 2015 Q1 |
| 2019 | 2019 Q1 |
| 2022 | 2022 Q1 |

### Social assistance (quarterly → annual)

Social assistance data is quarterly. We use Q4 of the election year as the reference quarter, which gives the full-year picture.

### Crime (quarterly → annual sum)

Crime data is reported quarterly. We sum all quarters within the election year to get an annual figure before normalising per capita.

### Income

Income is annual. We use the figure for the election year directly. No per-capita adjustment — the metric is already per-person (avg. disposable income in DKK).

### Geographic coverage

- **Municipality level**: 98 municipalities (kommuner) as defined after the 2007 kommunalreform.
- **Excluded rows**: National total ("All Denmark"), regional totals, and province aggregates are excluded from all municipal analysis.

---

## Correlation methodology

We use **Pearson r** to measure the linear relationship between a socioeconomic metric and party vote share across the 98 municipalities.

### Interpretation scale

| r value | Interpretation | What you can write |
|---|---|---|
| ±0.70 or above | Strong | "Data shows a clear pattern." |
| ±0.50–0.70 | Moderate | "There is a tendency." |
| ±0.30–0.50 | Weak | "A weak link exists — verify with other sources." |
| Below ±0.30 | None | Do not write a pattern claim. The data does not support it. |

### Direction

- **Positive r**: Both variables go up together (e.g. more cars per capita → more votes for the party).
- **Negative r**: They go in opposite directions (e.g. higher income → fewer votes).

---

## Bias rules

These rules apply to how the tool presents findings:

1. **All parties are treated equally.** No party is excluded, highlighted, or ranked above others in the interface by default.
2. **The raw r value is always shown.** Journalists can see the exact number, not just a label.
3. **Causation is never claimed.** Every finding includes the note: "This is a correlation, not a cause."
4. **The source is always cited.** Every finding includes the exact dataset and licence.
5. **No selective filtering.** If a metric shows no pattern (r < 0.30), that result is shown — not hidden.
6. **The tool does not editorialize headlines.** The headlines ("A tendency is visible") are based solely on the r value threshold — not on whether the result is politically convenient.

---

## Known limitations

- **Pre-2007 municipal data**: The 2007 kommunalreform merged 271 municipalities into 98. Municipal-level socioeconomic data before 2007 is not comparable on a like-for-like basis and is therefore not included.
- **2026 election**: The March 24, 2026 election is not yet in Statistikbanken. It is expected 3–4 months after the election. Real-time results were available at valg.dk on election night.
- **Correlation ≠ causation**: Repeated here because it cannot be overstated.
- **Ecological fallacy**: Municipal-level patterns do not tell you how individual voters behave. A municipality with high income voting less for the Social Democrats does not mean that wealthy individuals vote against them.
- **Missing data**: Not all metrics are available for all years or all municipalities. Small municipalities may have suppressed values in some datasets.

---

## What data is not yet included

| Metric | Source | Notes |
|---|---|---|
| Education level | Danmarks Statistik (UDDANNELSE) | Available at municipality level |
| Age distribution | Danmarks Statistik (FOLK1) | Available by municipality and age group |
| Urban/rural classification | Danmarks Statistik | Useful for controlling for urbanisation |
| Voter turnout | Danmarks Statistik (FVKOM) | Available at municipality level |
| Unemployment rate | Danmarks Statistik (LBESK69) | Integrated as "Full-time employed per 1,000" |
| Immigration share | Danmarks Statistik | Available at municipality level |
| 2026 election results | valg.dk / Statistikbanken | Available after ~July 2026 |

---

## Reproducibility

All data is fetched from public APIs. The fetch script is `fetch_dst.py`. The Straubinger dataset is available at github.com/Straubinger/folketingsvalg.

To reproduce: run `fetch_dst.py`, then `streamlit run app.py`.

---

*Hedegreen Research — hedegreenresearch.com*
