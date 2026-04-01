# Status — Danish Politics Data

## Public now

- municipality vote share `2007–2026`
- national vote trends `1953–2022`
- normalized municipality-safe factor layer in `denmark/factors/`
- year-aware factor availability in the public app
- provenance manifests for public-safe ingest runs

Current public factors:

- population
- education
- income
- average commute distance
- employment
- welfare
- crime
- cars
- age 65+
- turnout
- immigration share
- population density
- unemployment
- owner-occupied housing share
- detached-house dwelling share
- one-person household share

## Honest limits

- `2026` remains a bridge year.
- Commute and housing factors are year-aware and do not extend to `2026`.
- Housing coverage starts in `2010`.
- `BOL101` is missing `2021–2022` because DST currently keeps those years closed due to source problems in BBR.

## Intentionally withheld

- correct municipality-total divorce factor
- urban/rural classification as a numeric public correlation factor
- finer-resolution `2026` raw election inputs

## Public / private boundary

Public on GitHub:

- `denmark/factors/`
- municipality-safe bridge outputs in `denmark/folketing/`
- `provenance/`
- fetch/build scripts
- method / roadmap / changelog

Kept local:

- fine-resolution election raw
- temporary bridge staging
- anything under `internal/raw/` beyond documented public-safe notes
