# Public Factor Layer

This folder is the normalized municipality-safe factor layer used by `app.py`.

Rule:

- the public app reads from here
- raw DST pulls do not belong here
- every file should already be normalized to the post-2007 municipality layer

Typical columns:

- `municipality`
- `year`
- `value`

Population also carries `reference_period` because the election-year bridge does not always use the same time grain.
