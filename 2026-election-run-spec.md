# 2026 Election Run Spec

## Purpose

Bridge the private analysis machine and `Danish Politics Data` by bringing the 2026 Danish
Folketing election into the system in two forms:

- a finer internal election layer at official sub-municipal resolution
- a normalized municipality-level export that the public politics tool can read later

The important rule is:

The public tool does not become the raw truth engine.
It reads a reduced export from a stricter internal election layer.

## Why this run exists

`Danish Politics Data` currently uses municipality-level DST tables through 2022.

That is still correct for the current public tool.
But the 2026 election already exists in official systems even if the familiar Statistikbanken
tables are not yet updated.

This run is therefore the first concrete bridge between:

- the private Denmark-first analysis machine
- the existing politics tool
- the 2026 official election cycle

## Execution state

### First pass completed — 30 March 2026

The first operational 2026 bridge is no longer hypothetical.

Chosen first fetch path:

- `data.valg.dk` / official `VALG` public export

What was built:

- `fetch_valg_2026.py`
- `denmark/folketing/fv2026_party_share_by_municipality.csv`
- `denmark/folketing/fv2026_votes_by_municipality.csv`
- `denmark/folketing/fv2026_manifest.json`

What the first pass proved:

- the official public export already exposes `Fintælling` results per `afstemningsområde`
- the polling-area geography includes municipality code, polling-place name, and address
- 2026 can already be normalized into a municipality-safe export without waiting for the familiar Statistikbanken municipality tables
- the first bridge covered `1314` result files and `98` municipalities

What is still not solved by this first pass:

- the broader municipality indicator layer is not yet refreshed to a fully current 2026 footing
- the public tool still needs a later decision on whether 2026 should stay as a bridged year or later be swapped to canonical DST municipality tables when they arrive
- the finer polling-area layer is not yet held as a richer internal reusable store beyond the first generated bridge outputs and manifest

## Primary question

How do we ingest official 2026 Folketing election data at a finer internal resolution and
normalize it into a municipality-level export that is compatible with `Danish Politics Data`
without lying about status or precision?

## Hard rules

### 1. Official only

No newspapers.
No wiki tables.
No unofficial spreadsheets as primary election source.

Allowed source classes:

- Danmarks Statistik
- official Danish Election Database
- official `VALG` public data export
- Ministry / election authority material where relevant

### 2. Separate internal from public

Internal election data may be finer than municipality level.

Public export for `Danish Politics Data` must remain municipality-compatible and easy to reason
about.

### 3. Preserve status

Every 2026 election snapshot must carry one status:

- `official_preliminary`
- `official_final_fintaelling`
- `dst_public_final`

Do not flatten these into one fake certainty layer.

### 4. Keep the public tool method honest

Until the municipality-level 2026 export is stable, `Danish Politics Data` should not pretend
that 2026 is just another DST year identical to 2007-2022.

## Source priority

### Priority A — Danish Election Database

Use when 2026 is available in the official election database.

Why this is the preferred internal source:

- official and open
- supports extraction at polling-station level
- can also aggregate to larger units such as constituencies or municipalities
- designed for cross-time geographic comparison

Reference:

- https://valgdatabase.dst.dk/
- https://valgdatabase.dst.dk/about
- https://valgdatabase.dst.dk/data

### Priority B — `VALG` public SFTP export

This is the path chosen for the first operational pass.

Why this matters:

- official public data path
- supports geography, turnout, candidates, results, and party-vote-distribution files
- preliminary results are released by polling area on election night
- final count results are typically released by polling area the day after the election

Reference:

- https://valg.dk/assets/guides/sftp-guide-public/VALG%20-%20Vejledning%20til%20hent%20af%20valgdata%20%28Offentligheden%29.pdf

### Priority C — Statistikbanken municipality tables

Use later as the public canonical municipality layer when the familiar DST tables catch up.

This is the point where the public tool can return to a more standard update path.

Reference:

- https://api.statbank.dk/v1/data/FVKOM/CSV
- https://api.statbank.dk/v1/data/FVPANDEL/CSV

## Resolution model

### Internal raw layer

Preferred lowest unit:

- `afstemningsomraade` / polling area

If not available in the first pass:

- `opstillingskreds`

Fallback only if needed:

- `kommune`

The point is to hold 2026 internally at a finer level than the public tool.

### Internal normalized layer

Each internal election unit should be mapped to:

- polling area id if available
- municipality id
- constituency id
- storkreds id
- election date
- source snapshot id
- status

### Public export layer

Aggregate the internal layer to municipality level and export two public-tool-compatible files:

- `fv2026_votes_by_municipality.csv`
- `fv2026_party_share_by_municipality.csv`

These should mirror the public shape already used by:

- `fvkom_votes_by_municipality.csv`
- `fvpandel_party_share.csv`

## Required files

### Internal raw

Examples:

- raw SFTP JSON dumps or raw election-database extract files
- untouched snapshot metadata
- geometry / geography reference files for the election

### Internal normalized

Examples:

- normalized polling-area result table
- normalized party code table
- polling-area to municipality map
- validation totals

### Public export

Examples:

- municipality vote counts by party
- municipality vote share by party

## Normalization contract

### Entity keys

Need stable keys for:

- party
- polling area
- municipality
- constituency
- storkreds
- election

### Party normalization

Need a party mapping layer that can survive:

- official letter codes
- full party names
- candidate lists
- possible new or extinct party labels in 2026

### Geographic normalization

Need an explicit mapping from polling-area-level results to municipality.

Do not rely on human-readable strings alone.

### Status normalization

The same election can exist in multiple stages.

Keep them separate:

- preliminary count
- final count
- later DST municipality tables

## Validation rules

Before any export reaches the public politics tool:

1. Municipality totals must sum correctly from the internal finer layer.
2. National totals from the municipality export must match the official national totals for the
   same status snapshot.
3. Party-code mappings must be explicitly verified.
4. Blank, invalid, and other non-party vote categories must be handled deliberately.
5. The export must be tagged with election date, source, and status.

## First run output

The first serious run should produce:

### 1. Source note

What official source path was used for 2026.

### 2. Snapshot note

What was captured, when, and with what status.

### 3. Internal normalization result

A table proving that the finer election layer was normalized successfully.

### 4. Municipality export

The first 2026 municipality files in a format `Danish Politics Data` can later read.

### 5. Validation memo

Short internal note covering:

- what matched
- what did not
- what remains provisional
- what should not yet be exposed publicly

## First success criteria

This run is successful when:

- 2026 official election data is captured from an official source
- it exists internally at finer-than-municipality resolution
- it can be aggregated to municipality cleanly
- the municipality export can be compared against the public 2007-2022 format
- no part of the process hides whether the data is preliminary or final

## Future questions unlocked by this bridge

Once 2026 election data exists internally at finer-than-municipality resolution, the machine can
later ask much better questions than the public municipality tool can.

Examples:

- does turnout change when the number of polling places in a municipality changes over time?
- do merged or relocated polling places appear to change turnout locally?
- do some municipalities become structurally harder to vote in even when the top-line municipal
  turnout still looks normal?
- are there mismatches between polling-place geography and the social or demographic structure of
  the surrounding areas?
- do specific parties gain or lose more in places where voting access appears more friction-heavy?
- can polling-place type, address context, or later geocoded location data reveal hidden
  institutional patterns that municipality aggregates smooth away?

These are not claims yet.
They are examples of why the finer internal layer matters.

## Explicit non-goals

- no immediate public UI release
- no automatic merge into the public tool before validation
- no fake claim that 2026 is already just another fully settled DST year
- no cross-domain anomaly work yet beyond what is needed to prove the data bridge

## Immediate next implementation question

Which official 2026 source is quickest and cleanest to operationalize first:

- `valgdatabase.dst.dk`
- `data.valg.dk` public SFTP export

That decision should be made before any fetch script is written.
