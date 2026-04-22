# Danish Politics Data

Danish Politics Data compares Danish Folketing vote shares with municipality-level public factors. It is built for finding reporting leads and visible patterns, not for proving why people vote as they do.

## Public Door

- TID door: `https://hedegreenresearch.com/tid/danish-politics-data/`
- Live app: `https://danish-politics-data-nrfnkgn3zsm4jmhamsxzay.streamlit.app/`
- GitHub repo: `https://github.com/DennisHedegreen/danish-politics-data`

## Declared Scope

- Country: Denmark
- Election type: Folketing
- Unit of analysis: municipality
- Municipality election years: `2007`, `2011`, `2015`, `2019`, `2022`, `2026`
- National trend years: `1953-2022`
- Public factors: population, education, income, commute distance, employment, welfare, crime, cars, age 65+, turnout, immigration share, population density, unemployment, owner-occupied housing, detached houses, one-person households

The `2026` layer is a bridge layer. It is included because it is useful, but it should not be read as a normal long-settled Statistikbanken year.

## What You Can Do

- Compare party vote share with one or more municipality-level factors.
- Read whether the relationship is positive, negative, weak, moderate, or strong.
- Inspect high and low municipalities before turning a pattern into a claim.
- Use the result as a lead for reporting, not as the final story.

## What Not To Infer

- Correlation is not causation.
- Municipality-level patterns do not describe individual voters.
- A strong result does not prove why people voted as they did.
- A weak or missing result does not prove that a factor is irrelevant.
- The app is not a prediction model, campaign tool, or causal engine.

## How To Read Results

Positive correlation means higher party vote share tends to appear in municipalities where the selected factor is higher. Negative correlation means higher party vote share tends to appear where the selected factor is lower. The result is ranked by absolute correlation strength, so `-0.62` is treated as stronger than `0.31`.

Example: if a party has `r = 0.58` with population density in 2022, a responsible reading is: "The party tended to have higher vote shares in denser municipalities in this election year." It is not: "Density made voters choose this party."

## Quick Case

A journalist could start with a strong party-factor result, open the high and low municipality tables, and ask a concrete reporting question: is this a real geographic pattern, a party-history pattern, or just a one-year artifact? The app gives the lead. The reporting still has to do the verification.

See [HOW_TO_READ_RESULTS.md](HOW_TO_READ_RESULTS.md) and [METHODOLOGY.md](METHODOLOGY.md) before using results in public claims.

## Public Sources

- Election source: `Danmarks Statistik + official VALG 2026 bridge`
- Secondary national trend source: `Straubinger/folketingsvalg`
- Statistics source: `Danmarks Statistik`
- Public-safe provenance notes: [provenance/](provenance/)

## Repo Structure

```text
app.py               Single-country public wrapper
engine_app.py        Shared app shell extracted from the internal engine
correlation_utils.py Compatibility import for correlation helpers
core/                Runtime, presentation, correlation, and failure-state helpers
country_registry.py  Denmark-only public registry
denmark/             Denmark data pack and scope notes
provenance/          Public-safe manifests
tests/               Public-surface and logic contract tests
```

## Source Of Truth

This repo is a public country surface. The shared internal source tree still exists separately and remains the source of truth for shell changes and future extraction work. Public claims should cite this repo, its provenance notes, and the named public sources, not private working files.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
