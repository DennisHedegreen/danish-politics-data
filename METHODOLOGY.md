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
| Folketing vote share per municipality | Official `VALG` public export aggregated from polling-area level | 2026 | JSON over SFTP |
| National vote counts 1953–2022 | Straubinger/folketingsvalg (GitHub) | 1953–2022 | — |
| Avg. disposable income | Danmarks Statistik | 1987–2024 | INDKP101 |
| Social assistance recipients | Danmarks Statistik | 2007–present | AUK01 |
| Reported crimes | Danmarks Statistik | 2007–present | STRAF11 |
| Passenger cars | Danmarks Statistik | 2007–present | BIL707 |
| Divorces | Danmarks Statistik | 2007–present | SKI125 |
| Full-time employed per municipality | Danmarks Statistik | 2007–2022 (election quarters) | LBESK69 |
| Population (reference layer) | Danmarks Statistik | 2008–2026 bridge | FOLK1A + FOLK1AM |
| Voter turnout | Danmarks Statistik | 2007–2022 | FVKOM-derived |
| Immigration share | Danmarks Statistik | 2007–2026 bridge | FOLK1E |
| Population density | Danmarks Statistik | 2007–2026 bridge | ARE207 + population bridge |
| Unemployment rate | Danmarks Statistik | 2007–2024 | AUP02 |

All data from Danmarks Statistik is published under **CC 4.0 BY**.
Attribution: Danmarks Statistik, www.dst.dk

---

## How cross-referencing works

### Election year → population year

Per-capita metrics (welfare, crime, cars, employment and any later per-capita layers) require a population figure. We use the population reference closest to the public election-year bridge:

| Election | Population quarter used |
|---|---|
| 2007 | 2008 Q1 |
| 2011 | 2011 Q1 |
| 2015 | 2015 Q1 |
| 2019 | 2019 Q1 |
| 2022 | 2022 Q1 |
| 2026 | 2026 M02 |

### Social assistance (quarterly → annual)

Social assistance data is quarterly. We use Q4 of the election year as the reference quarter, which gives the full-year picture.

### Crime (quarterly → annual sum)

Crime data is reported quarterly. We sum all quarters within the election year to get an annual figure before normalising per capita.

### Income

Income is annual. We use the figure for the election year directly. No per-capita adjustment — the metric is already per-person (avg. disposable income in DKK).

### Turnout

Turnout is derived from `FVKOM` as:

`(valid votes + invalid votes) / number of voters * 100`

This currently covers the ordinary municipality-election layer through `2022`. The `2026` bridge does not yet include the full municipality voter-count layer, so turnout is not exposed for `2026`.

### Immigration share

Immigration share is derived from `FOLK1E` as the share of municipality residents without Danish origin:

`(total population - persons of Danish origin) / total population * 100`

### Population density

Population density is derived as:

`reference population / area in km²`

using `ARE207` for municipal area and the election-year population bridge layer for the denominator.

### Unemployment

Unemployment uses `AUP02`, which is already expressed as full-time unemployment in percent of the labour force. To keep the public layer honest, the current normalized factor uses annual means for completed years only. Partial `2026` monthly data is therefore not exposed yet.

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
- **2026 election**: The March 24, 2026 election is newer than the municipality-level Statistikbanken tables currently used by this public tool. Official 2026 results can exist earlier in higher-resolution official systems such as the Danish Election Database or the `VALG` public data export before they are folded into the familiar municipality tables.
- **Partial 2026 factor coverage**: `2026` is still a bridge year. Population, cars, immigration share and population density can be surfaced honestly earlier than factors such as turnout, unemployment, welfare, crime, employment or divorces.
- **Correlation ≠ causation**: Repeated here because it cannot be overstated.
- **Ecological fallacy**: Municipal-level patterns do not tell you how individual voters behave. A municipality with high income voting less for the Social Democrats does not mean that wealthy individuals vote against them.
- **Missing data**: Not all metrics are available for all years or all municipalities. Small municipalities may have suppressed values in some datasets.

---

## What data is not yet included

| Metric | Source | Notes |
|---|---|---|
| Urban/rural classification | Danmarks Statistik | Useful for controlling for urbanisation |
| Correct municipality-total divorce factor | Danmarks Statistik | Current local SKI125 slice is not a trustworthy total source |
| Owner-occupied housing share | Danmarks Statistik | Planned Wave 2 factor |
| Detached-house share | Danmarks Statistik | Planned Wave 2 factor |
| Apartment share | Danmarks Statistik | Planned Wave 2 factor |
| Commute distance / time | Danmarks Statistik | Planned Wave 2 factor |
| Students share | Danmarks Statistik | Planned Wave 2 factor |
| Single-person household share | Danmarks Statistik | Planned Wave 2 factor |

---

## Reproducibility

The current public-tool election layer is fetched from public APIs through `fetch_dst.py`, which now also builds the normalized municipality-safe factor layer in `denmark/factors/`. The Straubinger dataset is available at github.com/Straubinger/folketingsvalg.

To reproduce the current public tool: run `fetch_dst.py`, then `streamlit run app.py`.

The 2026 bridge is a separate internal run because it may start from higher-resolution official
sources before the familiar municipality-level Statistikbanken tables catch up. The current bridge script is `fetch_valg_2026.py`.

---

*Hedegreen Research — hedegreenresearch.com*
