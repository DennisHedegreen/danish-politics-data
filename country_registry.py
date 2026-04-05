from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent


BASE_FACTOR_CATALOG = {'population': {'label': 'Population',
                'metric_label': 'Population (reference count)',
                'question': 'Do larger municipalities vote differently?',
                'filename': 'population.csv',
                'comparability_status': 'country_local'},
 'education': {'label': 'Education',
               'metric_label': 'Higher education share (%)',
               'question': 'Do more educated municipalities vote differently?',
               'filename': 'education.csv',
               'comparability_status': 'family_mapped'},
 'income': {'label': 'Income',
            'metric_label': 'Avg. disposable income',
            'question': 'Do wealthier municipalities vote differently?',
            'filename': 'income.csv',
            'comparability_status': 'family_mapped'},
 'commute': {'label': 'Commute distance',
             'metric_label': 'Avg. commute distance (km)',
             'question': 'Do long-commute municipalities vote differently?',
             'filename': 'commute_distance_km.csv',
             'comparability_status': 'country_local'},
 'employment': {'label': 'Employment',
                'metric_label': 'Full-time employees per 1,000 residents',
                'question': 'Do areas with higher employment vote differently?',
                'filename': 'employment_per_1000.csv',
                'comparability_status': 'country_local'},
 'social': {'label': 'Welfare',
            'metric_label': 'Social assistance recipients per 1,000 residents',
            'question': 'Do areas with more people on benefits vote '
                        'differently?',
            'filename': 'welfare_per_1000.csv',
            'comparability_status': 'country_local'},
 'crime': {'label': 'Crime',
           'metric_label': 'Reported crimes per 1,000 residents',
           'question': 'Is there a link between crime rates and voting '
                       'patterns?',
           'filename': 'crime_per_1000.csv',
           'comparability_status': 'country_local'},
 'cars': {'label': 'Cars',
          'metric_label': 'Passenger cars per 1,000 residents',
          'question': 'Do car-heavy (rural) areas vote differently from urban '
                      'ones?',
          'filename': 'cars_per_1000.csv',
          'comparability_status': 'country_local'},
 'age65': {'label': 'Age 65+',
           'metric_label': 'Share aged 65+ (%)',
           'question': 'Do older municipalities vote differently?',
           'filename': 'age65_pct.csv',
           'comparability_status': 'family_mapped'},
 'turnout': {'label': 'Turnout',
             'metric_label': 'Votes cast as share of voters (%)',
             'question': 'Do high-turnout municipalities vote differently?',
             'filename': 'turnout_pct.csv',
             'comparability_status': 'family_mapped'},
 'immigration': {'label': 'Immigration share',
                 'metric_label': 'Residents without native-origin majority '
                                 'status (%)',
                 'question': 'Do municipalities with larger immigrant and '
                             'descendant shares vote differently?',
                 'filename': 'immigration_share_pct.csv',
                 'comparability_status': 'country_local'},
 'density': {'label': 'Population density',
             'metric_label': 'Residents per km²',
             'question': 'Does dense settlement correlate with voting '
                         'behaviour?',
             'filename': 'population_density.csv',
             'comparability_status': 'country_local'},
 'unemployment': {'label': 'Unemployment',
                  'metric_label': 'Full-time unemployment rate (%)',
                  'question': 'Do municipalities with higher unemployment vote '
                              'differently?',
                  'filename': 'unemployment_pct.csv',
                  'comparability_status': 'country_local'},
 'owner_occupied': {'label': 'Owner-occupied housing',
                    'metric_label': 'Owner-occupied occupied dwellings (%)',
                    'question': 'Do municipalities with more owner-occupied '
                                'housing vote differently?',
                    'filename': 'owner_occupied_dwelling_share_pct.csv',
                    'comparability_status': 'country_local'},
 'detached_houses': {'label': 'Detached houses',
                     'metric_label': 'Detached/farmhouse occupied dwellings '
                                     '(%)',
                     'question': 'Do municipalities with more detached-house '
                                 'living patterns vote differently?',
                     'filename': 'detached_house_dwelling_share_pct.csv',
                     'comparability_status': 'country_local'},
 'one_person_households': {'label': 'One-person households',
                           'metric_label': 'Occupied dwellings with 1 person '
                                           '(%)',
                           'question': 'Do municipalities with more one-person '
                                       'households vote differently?',
                           'filename': 'one_person_household_share_pct.csv',
                           'comparability_status': 'country_local'}}

PARTY_METADATA = {'A': {'native': 'Socialdemokratiet',
       'english': 'The Social Democrats',
       'short_native': 'Soc.dem.',
       'short_english': 'Soc. Dems'},
 'B': {'native': 'Radikale Venstre',
       'english': 'The Danish Social-Liberal Party',
       'short_native': 'Radikale',
       'short_english': 'Soc. Liberals'},
 'C': {'native': 'Det Konservative Folkeparti',
       'english': "The Conservative People's Party",
       'short_native': 'Konservative',
       'short_english': 'Conservatives'},
 'D': {'native': 'Nye Borgerlige',
       'english': 'The New Right',
       'short_native': 'Nye Borgerlige',
       'short_english': 'New Right'},
 'E': {'native': 'Klaus Riskær Pedersen',
       'english': 'Klaus Riskær Pedersen',
       'short_native': 'Riskær',
       'short_english': 'Riskær'},
 'F': {'native': 'Socialistisk Folkeparti',
       'english': "The Socialist People's Party",
       'short_native': 'SF',
       'short_english': 'Socialist PP'},
 'H': {'native': 'Borgernes Parti',
       'english': "The Citizens' Party",
       'short_native': 'Borgernes Parti',
       'short_english': "Citizens' Party"},
 'I': {'native': 'Liberal Alliance',
       'english': 'Liberal Alliance',
       'short_native': 'LA',
       'short_english': 'Liberal Alliance'},
 'K': {'native': 'Kristendemokraterne',
       'english': 'Christian Democrats',
       'short_native': 'KD',
       'short_english': 'Christian Dems'},
 'M': {'native': 'Moderaterne',
       'english': 'The Moderates',
       'short_native': 'Moderaterne',
       'short_english': 'Moderates'},
 'O': {'native': 'Dansk Folkeparti',
       'english': "The Danish People's Party",
       'short_native': 'DF',
       'short_english': 'Danish PP'},
 'P': {'native': 'Stram Kurs',
       'english': 'Hard Line',
       'short_native': 'Stram Kurs',
       'short_english': 'Hard Line'},
 'Q': {'native': 'Frie Grønne',
       'english': 'Independent Greens',
       'short_native': 'Frie Grønne',
       'short_english': 'Ind. Greens'},
 'V': {'native': 'Venstre',
       'english': 'Venstre (Liberal Party of Denmark)',
       'short_native': 'Venstre',
       'short_english': 'Venstre'},
 'Å': {'native': 'Alternativet',
       'english': 'The Alternative',
       'short_native': 'Alternativet',
       'short_english': 'Alternative'},
 'Æ': {'native': 'Danmarksdemokraterne',
       'english': 'The Danish Democrats',
       'short_native': 'Danmarksdem.',
       'short_english': 'Danish Dems'},
 'Ø': {'native': 'Enhedslisten',
       'english': 'The Red-Green Alliance',
       'short_native': 'Enhedslisten',
       'short_english': 'Red-Green'},
 'Independent candidates': {'native': 'Løsgængere',
                            'english': 'Independent candidates',
                            'short_native': 'Løsgængere',
                            'short_english': 'Independents'}}


@dataclass(frozen=True)
class CountryConfig:
    country_id: str
    display_name: str
    adjective: str
    language: str
    statistics_source_name: str
    default_election_type: str
    election_label: str
    public_geography_type: str
    public_geography_label: str
    public_geography_label_plural: str
    public_geography_count: int
    supported_factors: tuple[str, ...]
    supported_elections: tuple[str, ...]
    internal_ready: bool
    public_ready: bool
    municipal_vote_path: Path
    national_vote_path: Path | None
    factor_dir: Path
    party_metadata: dict[str, dict[str, str]]
    source_note: str
    secondary_source_note: str | None = None

    def factor_catalog(self) -> list[dict[str, str]]:
        return [{**BASE_FACTOR_CATALOG[key], "key": key} for key in self.supported_factors]


COUNTRY = CountryConfig(
    country_id='denmark',
    display_name='Denmark',
    adjective='Danish',
    language='English',
    statistics_source_name='Danmarks Statistik',
    default_election_type='folketing',
    election_label='Folketing election',
    public_geography_type='municipality',
    public_geography_label='municipality',
    public_geography_label_plural='municipalities',
    public_geography_count=98,
    supported_factors=('population', 'education', 'income', 'commute', 'employment', 'social', 'crime', 'cars', 'age65', 'turnout', 'immigration', 'density', 'unemployment', 'owner_occupied', 'detached_houses', 'one_person_households'),
    supported_elections=('folketing',),
    internal_ready=True,
    public_ready=True,
    municipal_vote_path=ROOT / "denmark/folketing/fvpandel_party_share.csv",
    national_vote_path=ROOT / "denmark/folketing/straubinger_votes_1953_2022.csv",
    factor_dir=ROOT / "denmark/factors",
    party_metadata=PARTY_METADATA,
    source_note='Danmarks Statistik + official VALG 2026 bridge',
    secondary_source_note='Straubinger/folketingsvalg',
)


def get_country_config(country_id: str) -> CountryConfig:
    if country_id != COUNTRY.country_id:
        raise KeyError(f"Unknown country_id: {country_id}")
    return COUNTRY


def list_public_countries() -> list[CountryConfig]:
    return [COUNTRY]


def list_internal_countries() -> list[CountryConfig]:
    return [COUNTRY]


def country_data_pack_exists(config: CountryConfig) -> bool:
    if not config.municipal_vote_path.exists():
        return False
    if not config.factor_dir.exists():
        return False
    return True


def _normalize_allowed_country_ids(allowed_country_ids: Iterable[str] | None) -> list[str] | None:
    if allowed_country_ids is None:
        return None
    return [country_id.strip().lower() for country_id in allowed_country_ids if country_id.strip()]


def list_exposed_countries(
    allowed_country_ids: Iterable[str] | None = None,
    *,
    allow_internal: bool = False,
    require_data_pack: bool = True,
) -> list[CountryConfig]:
    allowed = _normalize_allowed_country_ids(allowed_country_ids)
    if allowed is None:
        if require_data_pack and not country_data_pack_exists(COUNTRY):
            return []
        return [COUNTRY]
    if COUNTRY.country_id not in allowed:
        return []
    if require_data_pack and not country_data_pack_exists(COUNTRY):
        return []
    return [COUNTRY]


def list_exposed_public_countries(
    allowed_country_ids: Iterable[str] | None = None,
    require_data_pack: bool = True,
) -> list[CountryConfig]:
    return list_exposed_countries(
        allowed_country_ids,
        allow_internal=False,
        require_data_pack=require_data_pack,
    )
