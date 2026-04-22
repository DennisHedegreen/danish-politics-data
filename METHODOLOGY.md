# Methodology - Danish Politics Data

## Purpose

Danish Politics Data is a public reading surface for Danish Folketing data. It pairs party vote share with municipality-level factors and shows correlation patterns that can be checked, questioned, and reported carefully.

The tool does not explain voting behavior. It helps find patterns worth investigating.

## Unit Of Analysis

The unit of analysis is the municipality. Each row used in a correlation represents a municipality in one election year, with:

- one party vote-share value
- one factor value
- one shared municipality geography layer

The app does not model individuals, households, polling districts, candidates, campaigns, or local events.

## Pearson Correlation In This Tool

The app uses Pearson correlation (`r`) to summarize how two numeric municipality-level series move together:

- party vote share
- selected factor value

`r` ranges from `-1` to `1`.

- `1` means the two values rise together perfectly in the observed municipalities.
- `0` means no linear relationship is visible in this calculation.
- `-1` means one value rises as the other falls perfectly in the observed municipalities.

The app rounds displayed `r` values for readability.

## Positive And Negative Results

A positive result means the party tends to have higher vote share in municipalities where the factor is higher.

A negative result means the party tends to have higher vote share in municipalities where the factor is lower.

This direction is descriptive. It is not a claim about cause, motive, voter identity, or political strategy.

## Strength Labels

The app groups correlation values into rough reading bands:

- `0.70+`: strong
- `0.50-0.69`: moderate
- `0.30-0.49`: weak
- below `0.30`: no clear pattern

The bands are guide rails, not scientific proof thresholds. A strong number can still be misleading if the data context is weak.

## Missingness And Availability

Missing factor-year combinations are not backfilled just to make the interface look complete. If a factor is unavailable for a year, it should be hidden or marked unavailable rather than silently estimated.

The 2026 layer is a bridge layer. It is useful for public reading, but it is not treated as a normal mature long-series year.

## Public Factor Policy

Factors are public only when the current surface can defend their coverage and meaning. Some material can exist internally before it belongs in the public app.

Currently withheld or constrained:

- divorces, until the municipality-total source path is trustworthy
- urban/rural classification as a numeric public correlation factor
- false backfills for closed or source-problem years
- fine-resolution bridge inputs that do not belong in this public repo

## Interpretation Guardrails

Responsible reading:

- "In 2022, the party tended to do better in municipalities with higher X."
- "This is a pattern worth checking against geography, party history, and local context."
- "The result is municipality-level and does not describe individual voters."

Irresponsible reading:

- "X caused people to vote for the party."
- "Voters with X characteristic voted this way."
- "The model predicts the next election."

## Municipality-Level Limitations

Municipalities are large, mixed units. A municipality can contain urban and rural areas, high and low income groups, older and younger voters, and different local political histories. A municipality-level correlation can hide variation inside the municipality.

This creates ecological fallacy risk: a pattern about places must not be converted into a claim about individual people.

## Sources

- Election source: `Danmarks Statistik + official VALG 2026 bridge`
- Secondary national trend source: `Straubinger/folketingsvalg`
- Statistics source: `Danmarks Statistik`
- Provenance notes: [provenance/](provenance/)
