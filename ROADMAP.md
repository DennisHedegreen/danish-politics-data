# Roadmap — Danish Politics Data

Internal working roadmap.

Not a product promise.
Not a public launch document.
Just the next real passes in the right order.

Core rule:

> Trust before polish.

If a result is weak, say it is weak.
If a factor fails, fail honestly.
If a view looks clean but lies, it is broken.

---

## Current state

Already tightened:

- invalid / non-finite correlations no longer produce pattern claims
- strongest-signal logic excludes invalid rows
- public municipality logic is aligned to 98
- the blank Income scatter path has been hardened
- `Divorces` now fails for a clearer reason instead of being forced into output
- party labels can switch between Danish / English / Both
- compact chart and table labels are less hostile on mobile

Still open:

- raw `None` values in historical UI
- deeper mobile table friction
- compare-view wording and layout polish
- methodology / source notes that should be clearer in public
- Wave 2 housing / commute factors
- proper municipality-total divorce source

---

## Phase 1 — Trust Cleanup

Status: active

Goal:
Close the remaining small credibility leaks before adding more data.

Tasks:

- Remove raw `None` values from national trends tables
- Replace with `—` or blank cells in public UI
- Manually verify the 98-municipality rule across:
  - result cards
  - footnotes
  - ranking views
  - `See all X municipalities`
- Manually verify that valid scatter cases always render points
- Check that invalid-factor messaging stays honest and specific

Done when:

- no raw programming values leak into public UI
- no count drift remains
- no valid result card can sit above a blank scatter plot

---

## Phase 2 — Mobile Structure

Status: queued

Goal:
Make the tool workable on a phone without turning it into a different app.

Tasks:

- Reduce horizontal pressure in municipality tables
- Decide where mobile should prefer:
  - compact table first
  - chart first
  - or expandable detail
- Revisit `By municipality` on mobile:
  - current chart is dense
  - summary line is strong
  - table may deserve priority
- Revisit `Compare municipalities` profile section:
  - keep structure
  - reduce friction
  - do not hide useful detail behind aesthetics

Rule:

Do not solve mobile by shrinking type into nonsense.

---

## Phase 3 — Research-Reader Polish

Status: queued

Goal:
Tighten the public reading layer without softening the method.

Tasks:

- Replace “the other municipality” with direct municipality names in compare summaries
- Clarify that municipality profile data uses the most recent available year for each metric
- Add a short About / Sources note:
  - `Correlation ≠ causation`
  - years may differ by metric in structural profiles
- Review factor wording that still sounds machine-made or compressed
- Check that party-label mode stays coherent across:
  - selectors
  - result cards
  - ranking tables
  - chart tooltips

---

## Phase 4 — New Factors

Status: active first pass

Goal:
Grow the public factor layer without turning the tool into a messy table dump.

Factors:

Wave 1 now landed:

1. Population
2. Voter turnout
3. Immigration share
4. Population density
5. Unemployment

Still not honest enough for public release:

6. Urban/rural classification as a numeric correlation factor
7. Correct municipality-total divorces rebuild

Wave 2 now partly landed:

8. Average commute distance
9. Share owner-occupied housing
10. Share living in detached houses
13. Single-person household share

Still queued from the old Wave 2 list:

11. Apartment share
12. Students share

Required before implementation for any new factor:

- identify exact Statistikbanken table
- choose exact municipality-level definition
- document denominator and interpretation
- verify coverage
- verify plausible value ranges
- check municipality key consistency

Required after integration:

- single-party mode works
- multi-party mode works
- multi-factor mode works
- scatter plot works
- tables work
- weak / no-pattern handling still works

Rule:

No new factor enters the UI until it has earned first-class status.
If the source path is wrong, the factor should disappear rather than survive as a lie.

---

## Phase 5 — Overlap And Redundancy

Status: first pass completed

Goal:
Measure overlap between the first Wave 2 factors once they exist together.

Tasks:

- compute pairwise correlations between:
  - commute distance
  - owner-occupied housing
  - detached-house share
  - one-person household share
- note strong overlap if present
- do not auto-remove factors just because they overlap

Purpose:

Avoid pretending three factors say three unrelated things if they mostly track the same structural geography.

Current first-pass result:

- `owner-occupied housing` and `detached-house share` overlap strongly
- `commute distance` tracks detached-house geography clearly, but less tightly
- `one-person household share` remains different enough to justify keeping

See `FACTOR-OVERLAP.md`.

---

## Phase 6 — Outreach Readiness

Status: later

Goal:
Know when the tool is strong enough for another round of public use.

Checklist:

- trust cleanup closed
- mobile pass acceptable
- no raw `None`
- no count ambiguity
- no broken valid scatter cases
- sources page honest and current
- changelog updated
- manual test pass completed

Then:

- commit
- push
- decide whether to send again

---

## Phase 6A — 2026 Election Bridge

Status: first pass completed

Goal:
Bring the 2026 Folketing election into the internal system at finer-than-municipality resolution
and normalize it into a municipality export that the public tool can eventually read.

Tasks:

- done:
  - chose `data.valg.dk` as the first operational 2026 source path
  - captured the official 2026 fine-count export at polling-area resolution
  - normalized party codes into the public-tool party label layer
  - mapped polling-area results to municipalities through official geography files
  - produced the first municipality-level exports:
    - `fv2026_party_share_by_municipality.csv`
    - `fv2026_votes_by_municipality.csv`
    - `fv2026_manifest.json`
  - verified municipality coverage and vote totals in the first bridge pass
- still open:
  - decide whether to refresh the wider municipality indicator layer for 2026 now or keep 2026 as a partly bridged year for a while
  - decide how long the public tool should keep the bridged municipality layer before later DST municipality tables, if and when they arrive
  - decide whether to keep a richer reusable internal polling-area store instead of only the municipality bridge outputs

Rule:

Do not push 2026 into the public tool as if it were just another ordinary Statistikbanken year.

Purpose underneath:

This is the first real bridge between the private analysis machine and `Danish Politics Data`.

---

## Phase 6B — Normalized Public Factor Layer

Status: first pass completed

Goal:
Split the politics data system into:

- a public-safe provenance layer
- a normalized public municipality factor layer that the app reads directly

Completed in this pass:

- added `provenance/`
- added `denmark/factors/`
- moved the app toward normalized factor CSVs instead of raw DST table logic
- added first public wave beyond the older eight-factor framing:
  - population
  - turnout
  - immigration share
  - population density
  - unemployment
- kept `2026` partial instead of faking full factor coverage

Still open:

- lock the correct divorce source
- decide how to represent urban/rural classification honestly in a correlation-first public UI
- add the Wave 2 housing / commute / household batch

---

## Phase 7 — International Data Mapping

Status: later

Goal:
Test whether Danish Politics Data is really a local one-off or the first instance of a wider tool family.

Tasks:

- Identify which countries have municipality-level or equivalent local election data that is public enough to work with
- Identify which countries also expose compatible structural data:
  - income
  - education
  - welfare
  - crime
  - housing
  - age structure
- Note where geography, election systems, and administrative units make direct comparison unrealistic
- Separate:
  - countries with real expansion potential
  - countries with partial data only
  - countries where the idea breaks on missing public infrastructure
- Keep this as a research map first, not a rollout promise

Question underneath:

Is this a Danish tool, or the first solved case of a broader public-data pattern reader?

---

## Phase 8 — Internal Research Model

Status: later

Goal:
Build a stricter internal version of the tool for Dennis's own research where the system does not optimize for public-facing language first.

Principle:

The public tool still needs careful wording, trust cues, and readable summaries.
The internal model should care less about packaging and more about raw structural reading.

Possible characteristics:

- more factor combinations
- rougher outputs
- less UI explanation
- faster comparison workflows
- more willingness to expose intermediate states
- less dependence on polished language

Rule:

Do not confuse the public instrument with the internal research engine.
They can share data and logic without being the same product.

---

## Non-goals

Not doing:

- full i18n rewrite
- predictive modelling
- causal claims
- cosmetic redesign for its own sake
- adding many new factors just to look richer

---

## Working principle

This tool should feel like a research instrument.

Not a dashboard with opinions.
Not a prototype with good intentions.
Not a polished lie.

Sharper is better than nicer.
