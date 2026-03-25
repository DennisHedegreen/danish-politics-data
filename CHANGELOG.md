# Changelog — Danish Politics Data

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
