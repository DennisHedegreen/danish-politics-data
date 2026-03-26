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
- three new housing / commute factors

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

Status: research first

Goal:
Add three new factors properly, not decoratively.

Factors:

1. Average commute distance
2. Share owner-occupied housing
3. Share living in detached houses

Required before implementation:

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

---

## Phase 5 — Overlap And Redundancy

Status: blocked on Phase 4

Goal:
Measure overlap between the three new factors once they exist.

Tasks:

- compute pairwise correlations between:
  - commute distance
  - owner-occupied housing
  - detached-house share
- note strong overlap if present
- do not auto-remove factors just because they overlap

Purpose:

Avoid pretending three factors say three unrelated things if they mostly track the same structural geography.

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
