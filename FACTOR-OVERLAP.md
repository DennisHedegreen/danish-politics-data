# Factor Overlap — Wave 2 First Pass

## Purpose

Check whether the first Wave 2 factors are mostly saying the same structural thing.

Current set:

- commute distance
- owner-occupied housing share
- detached-house dwelling share
- one-person household share

Rule:

Overlap is a warning about interpretation, not an automatic reason to remove a factor.

---

## Method

Pairwise Pearson correlations were measured directly on the normalized municipality-safe factor files in `denmark/factors/`.

Two views were used:

1. election-year overlap
   only years that matter directly to the public politics tool
2. all common years
   the full shared municipality-year surface for each pair

Important:

- `owner_occupied_housing` currently has no `2021` or `2022`, because DST keeps those years closed in `BOL101`
- housing factors start in `2010`
- no missing years were backfilled

---

## Election-Year Overlap

### 2011

- commute vs owner-occupied: `r = 0.618`
- commute vs detached: `r = 0.716`
- commute vs one-person: `r = -0.335`
- owner-occupied vs detached: `r = 0.888`
- owner-occupied vs one-person: `r = -0.619`
- detached vs one-person: `r = -0.427`

### 2015

- commute vs owner-occupied: `r = 0.564`
- commute vs detached: `r = 0.697`
- commute vs one-person: `r = -0.234`
- owner-occupied vs detached: `r = 0.877`
- owner-occupied vs one-person: `r = -0.522`
- detached vs one-person: `r = -0.281`

### 2019

- commute vs owner-occupied: `r = 0.541`
- commute vs detached: `r = 0.715`
- commute vs one-person: `r = -0.132`
- owner-occupied vs detached: `r = 0.842`
- owner-occupied vs one-person: `r = -0.468`
- detached vs one-person: `r = -0.174`

### 2022

- commute vs detached: `r = 0.735`
- commute vs one-person: `r = -0.069`
- detached vs one-person: `r = -0.162`

`owner_occupied_housing` is unavailable in `2022`.

---

## All Common Years

- commute vs owner-occupied: `r = 0.519`
- commute vs detached: `r = 0.686`
- commute vs one-person: `r = -0.143`
- owner-occupied vs detached: `r = 0.853`
- owner-occupied vs one-person: `r = -0.521`
- detached vs one-person: `r = -0.250`

---

## Reading

### 1. Owner-occupied and detached-house share overlap strongly

This is the clearest overlap in the Wave 2 batch.

Across both election years and all common years, `owner_occupied_housing` and `detached_house_share` stay in the `0.84–0.89` range.

That is strong enough that they should be read as closely related structural geography.

They are not identical, but they are not independent signals either.

### 2. Commute distance tracks detached-house geography more than it tracks one-person households

`commute_distance_km` and `detached_house_share` stay around `0.69–0.74`.

That suggests commute distance is partly carrying the same suburban / exurban spatial structure as detached-house dwelling share.

It is still less redundant than the owner-occupied vs detached pair.

### 3. One-person households are different enough to keep

`one_person_households` does not collapse into the other three.

It has:

- a moderate negative relationship to owner-occupied housing
- a weaker negative relationship to detached-house share
- only weak overlap with commute distance

That makes it the clearest non-redundant addition in the Wave 2 batch.

---

## Practical Conclusion

Do not remove factors automatically.

But do not pretend they are equally independent.

Working reading for the public tool:

- `owner-occupied housing` and `detached houses` belong to the same broad housing-structure family
- `commute distance` is related to that family, but not collapsed into it
- `one-person households` adds something meaningfully different

---

## Next Honest Step

If this tool grows another explanation layer later, it should not describe all four Wave 2 factors as separate worlds.

The next good move would be:

- keep all four public
- but treat `owner-occupied` and `detached` as a visibly related pair in later interpretation or article framing
- then decide whether the next withheld line to unlock is:
  - correct municipality-total divorces
  - or a non-fake public urban/rural handling path
