# Sources — Danish Folketing Election Data

## Files in this folder

### fvkom_votes_by_municipality.csv
- **Table**: FVKOM — "Election to the Parliament"
- **Source**: Danmarks Statistik, Statistikbanken API
- **URL**: https://api.statbank.dk/v1/data/FVKOM/CSV
- **Coverage**: 2007, 2011, 2015, 2019, 2022
- **Geographic level**: Municipality (kommune), 98 municipalities + national total
- **Content**: Raw vote counts per party per municipality per election
- **Fields**: VALRES (party or result type), OMRÅDE (municipality), TID (year), INDHOLD (value)
- **License**: CC 4.0 BY — Danmarks Statistik
- **Fetched**: 2026-03-25

### fvpandel_party_share.csv
- **Table**: FVPANDEL — "The Parties share of votes (Election to the Parliament)"
- **Source**: Danmarks Statistik, Statistikbanken API
- **URL**: https://api.statbank.dk/v1/data/FVPANDEL/CSV
- **Coverage**: 2007, 2011, 2015, 2019, 2022
- **Geographic level**: Municipality and national total
- **Content**: Party vote share (percentage) per municipality per election
- **Fields**: VALRES (party), OMRÅDE (area), TID (year), INDHOLD (percentage)
- **License**: CC 4.0 BY — Danmarks Statistik
- **Fetched**: 2026-03-25

### fv2026_party_share_by_municipality.csv
- **Source**: Official `VALG` public export on `data.valg.dk`
- **Upstream resolution**: Polling area / `afstemningsområde`
- **Coverage**: Folketing election, 24 March 2026
- **Geographic level in export**: Municipality, 98 municipalities
- **Method**: Aggregated from official polling-area fine-count JSON files via `fetch_valg_2026.py`
- **Fields**: VALRES (party), OMRÅDE (municipality), TID (year), INDHOLD (percentage)
- **Status**: `official_final_fintaelling`
- **Fetched / built**: 2026-03-30

### fv2026_votes_by_municipality.csv
- **Source**: Official `VALG` public export on `data.valg.dk`
- **Upstream resolution**: Polling area / `afstemningsområde`
- **Coverage**: Folketing election, 24 March 2026
- **Geographic level in export**: Municipality, 98 municipalities
- **Method**: Aggregated from official polling-area fine-count JSON files via `fetch_valg_2026.py`
- **Fields**: VALRES (party or `VALID VOTES`), OMRÅDE (municipality), TID (year), INDHOLD (count)
- **Status**: `official_final_fintaelling`
- **Fetched / built**: 2026-03-30

### fv2026_manifest.json
- **Source**: Generated locally by `fetch_valg_2026.py`
- **Content**: Source path, file counts, polling-area coverage, status, and a sample of municipality metadata for the 2026 bridge
- **Built**: 2026-03-30

## What is not here yet

- **2026 municipality tables in Statistikbanken**: The March 24, 2026 election is newer than the 2007-2022 Statistikbanken municipality files currently used by the public tool. A stricter 2026 bridge should therefore use official higher-resolution sources first, and only later treat Statistikbanken municipality tables as the public canonical layer.
- **Pre-2007 municipal data**: Statistikbanken's municipal breakdown starts at 2007. National-level data back to 1953 is available via Straubinger/folketingsvalg on GitHub.
- **Polling station level**: Available in the Danish Election Database (valgdatabase.dst.dk) from 1979 onwards. Not yet fetched.
- **Candidate-level data**: Not yet included.

### straubinger_votes_1953_2022.csv
- **Source**: github.com/Straubinger/folketingsvalg
- **Coverage**: National level, 1953–2022 (25 elections)
- **Content**: Raw vote counts per party per election
- **Fetched**: 2026-03-25

### straubinger_seats_1953_2022.csv
- **Source**: github.com/Straubinger/folketingsvalg
- **Coverage**: National level, 1953–2022
- **Content**: Seats won per party per election
- **Fetched**: 2026-03-25

### straubinger_share_1953_2022.csv
- **Source**: github.com/Straubinger/folketingsvalg
- **Coverage**: National level, 1953–2022
- **Content**: Vote share (percentage) per party per election
- **Fetched**: 2026-03-25

## Other known sources not yet fetched

| Source | Coverage | URL | Format |
|---|---|---|---|
| Danish Election Database | Polling station level, 1979– | valgdatabase.dst.dk | Web/export |
| `VALG` public data export | Official public election export incl. geography, turnout, results, and party-vote-distribution files during the election period | https://valg.dk/assets/guides/sftp-guide-public/VALG%20-%20Vejledning%20til%20hent%20af%20valgdata%20%28Offentligheden%29.pdf | JSON over SFTP |
| electionresources.org | National + district, historical | electionresources.org/dk | CSV |

## Public factor layer note

The public app now reads a separate normalized factor layer from `denmark/factors/`.

That means:

- election files in this folder remain the vote-side source of truth
- municipality factors are built separately through `fetch_dst.py`
- ordinary DST refreshes should leave a manifest in `provenance/`

## License

All data from Danmarks Statistik is published under Creative Commons Attribution 4.0 (CC 4.0 BY).
Attribution: Danmarks Statistik, www.dst.dk
