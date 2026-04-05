# Danish Politics Data

> Sorry — the live Streamlit app is not functioning reliably right now. If you want to debug it, investigate the code, or send a fix, you are very welcome.

A public reading surface for Danish Folketing results at municipality level, paired with the current municipality-safe Danish factor layer.

This repo is the Denmark-only public surface rebuilt from the internal World-politics-data engine. It keeps the newer app shell while exposing only Denmark data, Denmark methodology, and Denmark-specific public notes.

## Public door

- TID door: `https://hedegreenresearch.com/tid/danish-politics-data/`
- GitHub repo: `https://github.com/DennisHedegreen/danish-politics-data`

## Current scope

- Election type: `Folketing`
- Municipality election years: `2007`, `2011`, `2015`, `2019`, `2022`, `2026`
- National trend years: `1953–2022`
- Public geography: `municipality`
- Current public factors: `population`, `education`, `income`, `commute distance`, `employment`, `welfare`, `crime`, `cars`, `age65`, `turnout`, `immigration share`, `population density`, `unemployment`, `owner-occupied housing`, `detached houses`, `one-person households`

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## What this repo is not

- Not a broader politics product beyond the declared Denmark scope
- Not a prediction model
- Not an explanation engine
- Not a person-level voter model
- Not a claim that the `2026` bridge is already a normal Statistikbanken year

## Intentionally missing

- `Divorces` until the municipality-total source path is trustworthy
- `Urban/rural classification` as a public numeric factor
- Any false backfilling of the closed `BOL101` years

## Data sources

- Election source: `Danmarks Statistik + official VALG 2026 bridge`
- Secondary source: `Straubinger/folketingsvalg`
- Statistics source: `Danmarks Statistik`

## Repo structure

```text
app.py               Single-country public wrapper
engine_app.py        Shared app shell extracted from the internal engine
correlation_utils.py Shared correlation helpers
country_registry.py  Single-country registry for this public surface
denmark/               Country data pack and scope notes
provenance/          Public-safe manifests copied from the internal engine
tests/               Country-surface smoke tests
```

## Source of truth

This repo is a public country surface. The shared internal source tree still exists separately and remains the source of truth for shell changes and future extraction work.
