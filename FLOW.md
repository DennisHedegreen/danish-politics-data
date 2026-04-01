# UI Flow — Danish Politics Data

## Overview

Three inputs → one or two action buttons → correlation compute → routing → output panel.

---

## Layer 1: INPUT

| Widget | Type | Values |
|---|---|---|
| Faktorer | Pills (multi-select) | Year-aware public factor layer (population, education, income, commute, employment, welfare, crime, cars, age 65+, turnout, immigration share, density, unemployment, owner-occupied housing, detached houses, one-person households) |
| Valgår | Select slider | 2007, 2011, 2015, 2019, 2022, 2026 |
| Partier | Multi-select + "All parties" toggle | All parties in Folketing data |

---

## Layer 2: ACTION

| Button | Behaviour |
|---|---|
| Show me what data reveals | Runs correlation for current selection, renders results |
| Surprise me → smart-random | Picks a random combination with \|r\| ≥ 0.40 from precomputed cache, sets session state via `_surprise_pending` pattern, reruns |

---

## Layer 3: COMPUTE

`precompute_all_correlations()` runs at startup and caches all ~600 combinations:
- year-aware election years × currently available public factors × active parties = Pearson r per cell
- Cached with `@st.cache_data` — never recomputed during a session
- Used by both "Show me" (live filter) and "Surprise me" (random pick)

---

## Layer 4: ROUTING

Decision: how many factors and parties are selected?

| Case | Condition | Output |
|---|---|---|
| A | 1 party, 1 factor | Single finding box + extremes table + scatter chart with outlier labels |
| B | 1 party, multiple factors | Bar chart (all factors ranked) + finding box per factor with \|r\| ≥ 0.20 |
| C | Multiple parties, 1 factor | Bar chart (all parties ranked) + finding box for strongest party |
| D | Multiple parties, multiple factors | Finding box for strongest combination + full correlation matrix in expander |

---

## Layer 5: OUTPUT

Each finding box contains:

| Element | Content |
|---|---|
| Pattern label | STRONG / MODERATE / WEAK / NO PATTERN + r value |
| Headline | Plain-language summary of direction |
| Description | Concrete numbers: gap in percentage points, top/bottom 10 municipality averages |
| Write this as | Draft journalist sentence, ready to copy |
| Chart | Scatter (Case A) or bar chart (Cases B/C/D) |
| Footnote | Pearson r · n municipalities · Danmarks Statistik (CC 4.0 BY) |
| Outlier labels | Municipality names shown directly on the 5 most extreme dots (Case A scatter) |

---

## Correlation scale

| r | Label | What you can write |
|---|---|---|
| ±0.65+ | STRONG | "Data shows a clear pattern." |
| ±0.40–0.65 | MODERATE | "There is a tendency." |
| ±0.20–0.40 | WEAK | "A weak link — verify with other sources." |
| below ±0.20 | NO PATTERN | Do not write a pattern claim. |

---

## Key technical constraints

- **Streamlit widget keys cannot be modified after instantiation.** "Surprise me" uses a `_surprise_pending` pattern: stores target values under temp keys, copies to widget keys at the top of the next run before any widget renders.
- **Gap = abs(more_avg − less_avg)** — computed after direction assignment to guarantee consistency with displayed numbers.
- **Per-capita metrics** (welfare, crime, cars, employment) are normalised using population from the quarter closest to the election year.
- **Education and Age 65+** are already percentage values — no per-capita normalisation needed.
- **Wave 2 commute + housing factors** stay year-aware. Missing years are hidden instead of backfilled.

---

*Hedegreen Research — hedegreenresearch.com*
