# Changelog — Danish Politics Data

---

## 2026-03-26 — Mobile structure pass for dense views

- Explore single-result extremes now use tabs instead of side-by-side tables.
- Compare municipalities now uses municipality tabs for vote history.
- The structural profile in Compare municipalities now renders as compact metric cards, with the full table preserved behind an expander.
- By municipality now shows the ranked table first and moves the full 98-bar chart behind an expander.

Reason:
Some views were still using dense desktop structure in places where the data itself was fine but the reading flow was not.

---

## 2026-03-26 — Historical table cleanup and clearer profile framing

- The national trends table now shows `—` where party data is absent instead of leaking raw missing-value emptiness.
- The municipality profile text in Compare municipalities now says plainly that it uses the most recent available year for each metric.
- The About page no longer locks itself to a fixed dataset count and now states the main method limits more directly.

Reason:
Small trust leaks matter. Public UI should not expose implementation artifacts or vague year logic.

---

## 2026-03-26 — Mobile presentation and party-label display pass

- Added a display toggle for party labels: `Danish`, `English`, `Both`.
- Applied that display layer across selectors, result summaries, ranking tables, and compact chart contexts.
- Replaced some default charts with explicit Altair charts so compact labels and fuller tooltips can coexist.
- Tightened a few clumsy factor labels and reduced some mobile spacing pressure.

Reason:
The app is in English, but the political entities are Danish. The label layer needed to become a deliberate display choice instead of a fixed compromise.

---

## 2026-03-26 — Municipality consistency and factor-specific reliability

- The public municipality frame is now fixed to 98.
- `Christiansø` is excluded consistently from the public municipality vote layer and the factor layers that were still drifting.
- The Explore scatter path now uses stable internal numeric fields instead of relying on longer visible labels as chart columns.
- `Divorces` stays unavailable where the current data collapses to no usable municipality variation, but the app now says that more clearly.

Rule preserved:

> No valid `r` = no pattern claim.

Reason:
The point was not to make more output appear.
The point was to stop weak joins, weak counts, and weak plotting from pretending to be findings.

---

## 2026-03-26 — Correlation guardrails for invalid results

### What changed and why

This update was driven by a validity problem in the result layer.

The tool could still render a narrative finding even when the underlying Pearson correlation was invalid, missing, or non-finite. That meant the UI could drift into pattern language without a trustworthy correlation value underneath it.

The fix was simple in principle:

> No valid `r` = no pattern claim.

---

### Added a reusable validation layer

- Introduced `correlation_utils.py`
- Added a shared `is_valid_correlation()` check
- Added a shared correlation-band helper
- Added a single guarded correlation compute path

**Why:** Validation should happen once, not separately inside each UI branch.

---

### Invalid results no longer render as findings

If a result is invalid, the app now shows an unavailable state instead of a pattern card.

That means invalid results no longer produce:

- `STRONG / MODERATE / WEAK / NO PATTERN` labels
- narrative pattern summaries
- copy-ready “Write this as” text
- strongest-signal selection

**Why:** Invalid is not weak. Invalid is unknown.

---

### Ranking now excludes invalid correlations

Multi-result views now filter invalid rows before ranking.

That means:

- strongest-signal logic only runs on valid results
- all-invalid selections produce a neutral no-valid-result state
- invalid rows no longer compete with real signals

**Why:** Ranking before validation can turn a compute failure into a false headline.

---

### Copy rules tightened

- `Write this as` is no longer shown for `NO PATTERN`
- invalid results do not produce copy-ready language
- weak results now use more cautious wording

**Why:** The tool should not generate smooth journalist-ready sentences when the underlying statistical footing is weak or unavailable.

---

### Added basic tests

- Added a first test file covering:
  - `None`
  - `NaN`
  - `inf`
  - out-of-range values
  - valid positive / negative values
  - invalid label fallback

**Why:** These are small tests, but this is exactly the kind of logic that should not silently regress later.

---

## 2026-03-25 — Language and threshold revision

### What changed and why

This update was driven by a review of the tool's language and logic. The goal was to make the tool more honest — not by changing the data or the underlying correlations, but by removing language that went beyond what the data actually shows.

---

### Threshold raised from r ≥ 0.20 to abs(r) ≥ 0.30

**Before:** Any correlation with abs(r) ≥ 0.20 was shown as a finding.

**After:** Only abs(r) ≥ 0.30 triggers a finding. Results below that threshold are reported as "no consistent pattern found."

**Why:** 0.20 is too low a bar for reporting a pattern to journalists. At that level the relationship is weak enough that it risks producing narratives the data cannot support.

---

### Strength scale updated

**Before:** Strong ≥ 0.65 · Moderate ≥ 0.40 · Weak ≥ 0.20

**After:** Strong ≥ 0.70 · Moderate ≥ 0.50 · Weak ≥ 0.30

**Why:** More conservative thresholds. Harder to reach "strong". The scale is now documented in METHODOLOGY.md and treated as fixed — not adjustable by the user.

All thresholds apply to absolute correlation values. Negative correlations are ranked and filtered by strength, not by sign.

---

### Language corrections

Several phrases were removed or replaced because they went beyond what correlation data can support:

| Before | After | Reason |
|---|---|---|
| "tend to vote significantly more" | "tend to vote more" | "significantly" is a judgement, not a data point |
| "The pattern holds across all 98 municipalities" | "Based on data from 98 Danish municipalities" | Correlation ≠ every municipality follows the pattern |
| "no meaningful link" | "no consistent relationship" | "meaningful" is undefined in the system |
| Copy sentence: "r below 0.20" | "abs(r) below 0.30" | Consistent with actual threshold logic |

---

### UI changes

- **Removed "Strongest factor / Also factor" labels** from multi-factor results. The ranking already communicates importance. Explicit labels introduced a bias toward the top result.
- **Factor overlap note** moved from below individual cards to after all cards. The note describes a relationship between factors — it should not appear to belong to one specific card.
- **Added factor overlap detection** (Case B): when two selected factors have abs(r) ≥ 0.60 between them, a note is shown: *"X and Y tend to move together across municipalities (r = ...)."*
- **Case D (multiple factors + multiple parties)**: Added explanatory text above the result and a count of other signals. Full correlation table now shows a flat list sorted by abs(r) descending instead of a party × factor matrix.

---

### What did not change

- All data sources and data logic are unchanged.
- All correlation calculations are unchanged.
- The underlying Pearson r values are identical.
- No data was added or removed.

---

*Hedegreen Research — hedegreenresearch.com*
