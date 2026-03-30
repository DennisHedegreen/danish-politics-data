# Internal Raw

This folder exists for bridge or special-source inputs that are worth preserving as raw provenance.

Rule:

- keep raw only for bridge/special runs
- ordinary DST refreshes should normalize and prune instead of accumulating raw snapshots here

Current example:

- the 2026 `VALG` bridge belongs in this family conceptually, even when the current implementation stores its public bridge outputs elsewhere
