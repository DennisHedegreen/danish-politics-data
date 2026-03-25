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

## What is not here yet

- **2026 results**: The March 24, 2026 election. Statistikbanken typically publishes 3-4 months after the election. Real-time results were available at valg.dk (KOMBIT) on election night.
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
| valg.dk (KOMBIT) | Real-time + 2026 results | valg.dk | CSV export |
| electionresources.org | National + district, historical | electionresources.org/dk | CSV |

## License

All data from Danmarks Statistik is published under Creative Commons Attribution 4.0 (CC 4.0 BY).
Attribution: Danmarks Statistik, www.dst.dk
