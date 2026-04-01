import streamlit as st
import pandas as pd
import altair as alt
import random
from pathlib import Path

from correlation_utils import correlation_band, corr_strength_label, compute_correlation_result, is_valid_correlation

embedded_mode = str(st.query_params.get("embedded", "")).lower() in {"1", "true", "yes"}
st.set_page_config(
    page_title="Danish Politics Data",
    layout="wide",
    initial_sidebar_state="collapsed" if embedded_mode else "expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&display=swap');

html, body, [class*="css"] { font-family: 'JetBrains Mono', monospace !important; }

section[data-testid="stSidebar"] {
    background: #ffffff !important; border-right: 1px solid #e0e0e8 !important;
    min-width: 240px !important; max-width: 280px !important;
}
section[data-testid="stSidebar"] .block-container { padding: 2rem 1.4rem !important; }
.main .block-container { padding-top: 2.5rem; padding-left: 3rem; padding-right: 3rem; max-width: 960px; }

h1 {
    font-family: 'Crimson Pro', Georgia, serif !important;
    font-size: 2.1rem !important; font-weight: 300 !important;
    color: #0d0d14 !important; line-height: 1.2 !important; margin-bottom: 0.3rem !important;
}
h2 {
    font-size: 0.7rem !important; font-weight: 500 !important; letter-spacing: 0.12em !important;
    text-transform: uppercase !important; color: #22d966 !important;
    border-bottom: 1px solid #e8e8f0 !important; padding-bottom: 0.4rem !important;
    margin-top: 2rem !important; margin-bottom: 0.8rem !important;
}
p { font-size: 0.88rem !important; line-height: 1.75 !important; color: #3a3a4a !important; }
.stCaption p { color: #8888a0 !important; font-size: 0.68rem !important; }
.stRadio > label { display: none !important; }
.stSelectbox label, .stMultiSelect label {
    font-size: 0.65rem !important; font-weight: 500 !important;
    letter-spacing: 0.09em !important; text-transform: uppercase !important; color: #8888a0 !important;
}
hr { border-color: #e0e0e8 !important; margin: 1.5rem 0 !important; }
.hr-wordmark {
    font-size: 0.58rem; font-weight: 500; letter-spacing: 0.18em;
    text-transform: uppercase; color: #aaaabc; margin-bottom: 1.6rem;
}
.hr-wordmark .dot { color: #22d966; }

/* Metric tiles */
.metric-tile {
    border: 1px solid #e0e0e8; padding: 1.1rem 1.2rem; margin-bottom: 0.5rem;
    background: #fff; line-height: 1.5;
}
.metric-tile.selected { border-color: #22d966; background: #f4fef8; }
.metric-tile .q { font-size: 0.92rem; font-weight: 400; color: #0d0d14; margin-bottom: 0.2rem; }
.metric-tile .hint { font-size: 0.72rem; color: #8888a0; }

/* Step labels */
.step-label {
    font-size: 0.6rem; font-weight: 500; letter-spacing: 0.14em;
    text-transform: uppercase; color: #aaaabc; margin-bottom: 0.5rem;
}

/* Finding reveal */
.finding {
    padding: 1.4rem 1.6rem; margin: 1.5rem 0;
    border-left: 3px solid #22d966; background: #f4fef8;
    animation: fadeIn 0.5s ease;
}
.finding.moderate { border-color: #3d8ef0; background: #f2f6ff; }
.finding.weak { border-color: #d0d0dc; background: #f8f8fb; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
.finding .strength-tag {
    font-size: 0.58rem; font-weight: 700; letter-spacing: 0.18em;
    text-transform: uppercase; color: #22d966; margin-bottom: 0.5rem;
}
.finding.moderate .strength-tag { color: #3d8ef0; }
.finding.weak .strength-tag { color: #aaaabc; }
.finding .headline {
    font-family: 'Crimson Pro', Georgia, serif;
    font-size: 1.4rem; font-weight: 400; color: #0d0d14;
    line-height: 1.3; margin-bottom: 0.7rem;
}
.finding .body { font-size: 0.88rem; color: #2a2a3a; line-height: 1.75; }
.finding .copy-box {
    font-size: 0.8rem; color: #2a2a3a; line-height: 1.7;
    background: #fff; border: 1px solid #d0d0dc;
    padding: 0.8rem 1rem; margin-top: 0.9rem;
}
.finding .copy-label {
    font-size: 0.55rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #aaaabc; margin-bottom: 0.3rem;
}
.finding .footnote { font-size: 0.68rem; color: #aaaabc; margin-top: 0.8rem; }

/* Source items */
.source-item { font-size: 0.72rem; color: #6a6a7a; padding: 0.4rem 0; border-bottom: 1px solid #f0f0f5; line-height: 1.5; }
.source-item strong { color: #0d0d14; font-weight: 500; }
.data-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 0.75rem;
    margin: 0.8rem 0 0.4rem;
}
.data-card {
    border: 1px solid #e0e0e8;
    background: #fff;
    padding: 0.9rem 1rem;
}
.data-card .metric {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #8888a0;
    margin-bottom: 0.45rem;
}
.data-card .value-line {
    font-size: 0.84rem;
    line-height: 1.6;
    color: #1d1d28;
}
.data-card .year {
    margin-top: 0.45rem;
    font-size: 0.67rem;
    color: #8888a0;
}

@media (max-width: 900px) {
    .main .block-container { padding-top: 1.2rem; padding-left: 1rem; padding-right: 1rem; max-width: 100%; }
    section[data-testid="stSidebar"] { min-width: 100% !important; max-width: 100% !important; }
    h1 { font-size: 1.65rem !important; }
    .finding { padding: 1rem 1rem; }
    .finding .headline { font-size: 1.18rem; }
    .data-card-grid { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)

# ── helpers ───────────────────────────────────────────────────────────────────

EXCLUDE = lambda s: (
    s.str.startswith("Province") | s.str.startswith("Region") |
    (s == "All Denmark") | (s == "Christiansø")
)
FACTOR_DIR = Path("denmark/factors")


def exclude_public_special_cases(df, column="municipality"):
    return df[~df[column].isin(["All Denmark", "Christiansø"])].copy()


def invalid_result_detail(reason):
    if reason == "zero_variance_metric":
        return "The selected factor has no usable municipality variation for this year after preprocessing."
    if reason == "zero_variance_share":
        return "The selected party has no usable municipality variation for this year."
    if reason == "insufficient_rows":
        return "There are too few overlapping municipality rows to compute a reliable correlation."
    return "The correlation value for this selection could not be computed reliably."


def municipal_vote_source_label(year):
    if year == 2026:
        return "Official VALG 2026 municipality bridge + Danmarks Statistik indicators"
    return "Danmarks Statistik (CC 4.0 BY)"


def municipal_vote_source_inline(year):
    if year == 2026:
        return "Official VALG 2026 municipality bridge for vote share + Danmarks Statistik for the selected indicator"
    return "Danmarks Statistik, CC 4.0 BY"


PARTY_METADATA = {
    "A": {"danish": "Socialdemokratiet", "english": "The Social Democrats", "short_danish": "Soc.dem.", "short_english": "Soc. Dems"},
    "B": {"danish": "Radikale Venstre", "english": "The Danish Social-Liberal Party", "short_danish": "Radikale", "short_english": "Soc. Liberals"},
    "C": {"danish": "Det Konservative Folkeparti", "english": "The Conservative People's Party", "short_danish": "Konservative", "short_english": "Conservatives"},
    "D": {"danish": "Nye Borgerlige", "english": "The New Right", "short_danish": "Nye Borgerlige", "short_english": "New Right"},
    "E": {"danish": "Klaus Riskær Pedersen", "english": "Klaus Riskær Pedersen", "short_danish": "Riskær", "short_english": "Riskær"},
    "F": {"danish": "Socialistisk Folkeparti", "english": "The Socialist People's Party", "short_danish": "SF", "short_english": "Socialist PP"},
    "H": {"danish": "Borgernes Parti", "english": "The Citizens' Party", "short_danish": "Borgernes Parti", "short_english": "Citizens' Party"},
    "I": {"danish": "Liberal Alliance", "english": "Liberal Alliance", "short_danish": "LA", "short_english": "Liberal Alliance"},
    "K": {"danish": "Kristendemokraterne", "english": "Christian Democrats", "short_danish": "KD", "short_english": "Christian Dems"},
    "M": {"danish": "Moderaterne", "english": "The Moderates", "short_danish": "Moderaterne", "short_english": "Moderates"},
    "O": {"danish": "Dansk Folkeparti", "english": "The Danish People's Party", "short_danish": "DF", "short_english": "Danish PP"},
    "P": {"danish": "Stram Kurs", "english": "Hard Line", "short_danish": "Stram Kurs", "short_english": "Hard Line"},
    "Q": {"danish": "Frie Grønne", "english": "Independent Greens", "short_danish": "Frie Grønne", "short_english": "Ind. Greens"},
    "V": {"danish": "Venstre", "english": "Venstre (Liberal Party of Denmark)", "short_danish": "Venstre", "short_english": "Venstre"},
    "Å": {"danish": "Alternativet", "english": "The Alternative", "short_danish": "Alternativet", "short_english": "Alternative"},
    "Æ": {"danish": "Danmarksdemokraterne", "english": "The Danish Democrats", "short_danish": "Danmarksdem.", "short_english": "Danish Dems"},
    "Ø": {"danish": "Enhedslisten", "english": "The Red-Green Alliance", "short_danish": "Enhedslisten", "short_english": "Red-Green"},
    "Independent candidates": {"danish": "Løsgængere", "english": "Independent candidates", "short_danish": "Løsgængere", "short_english": "Independents"},
}

PARTY_NAME_MODES = ["Danish", "English", "Both"]

METRIC_SHORT_LABELS = {
    "Population": "Population",
    "Education": "Higher edu. %",
    "Income": "Income",
    "Commute distance": "Commute km",
    "Employment": "Employed / 1k",
    "Welfare": "Welfare / 1k",
    "Crime": "Crime / 1k",
    "Cars": "Cars / 1k",
    "Age 65+": "Age 65+ %",
    "Turnout": "Turnout %",
    "Immigration share": "Immigration %",
    "Population density": "Population / km²",
    "Unemployment": "Unemployment %",
    "Owner-occupied housing": "Owner-occ. %",
    "Detached houses": "Detached %",
    "One-person households": "1-person %",
}

METRIC_PHRASES = {
    "Population": "population size",
    "Education": "higher education share",
    "Income": "disposable income",
    "Commute distance": "average commute distance",
    "Employment": "full-time employment",
    "Welfare": "social assistance use",
    "Crime": "reported crime",
    "Cars": "car ownership",
    "Age 65+": "share aged 65+",
    "Turnout": "voter turnout",
    "Immigration share": "immigration share",
    "Population density": "population density",
    "Unemployment": "unemployment rate",
    "Owner-occupied housing": "owner-occupied housing share",
    "Detached houses": "detached-house dwelling share",
    "One-person households": "one-person household share",
}


def party_parts(raw_party):
    if raw_party in PARTY_METADATA and raw_party == "Independent candidates":
        meta = PARTY_METADATA[raw_party]
        return None, meta
    if ". " in raw_party:
        code, english_source = raw_party.split(". ", 1)
        meta = PARTY_METADATA.get(code, {}).copy()
        if not meta:
            meta = {
                "danish": english_source,
                "english": english_source,
                "short_danish": english_source,
                "short_english": english_source,
            }
        return code, meta
    meta = PARTY_METADATA.get(raw_party, {
        "danish": raw_party,
        "english": raw_party,
        "short_danish": raw_party,
        "short_english": raw_party,
    })
    return None, meta


def format_party_name(raw_party, mode="English", compact=False, include_code=False, prose=False):
    code, meta = party_parts(raw_party)
    danish = meta["short_danish"] if compact else meta["danish"]
    english = meta["short_english"] if compact else meta["english"]

    if mode == "Danish":
        label = danish
    elif mode == "Both":
        label = f"{danish} ({english})" if prose else f"{danish} / {english}"
    else:
        label = english

    if include_code and code:
        return f"{code}. {label}"
    return label


def format_party_code(code, mode="English", compact=False):
    for raw in ALL_PARTY_NAMES if "ALL_PARTY_NAMES" in globals() else []:
        party_code, _ = party_parts(raw)
        if party_code == code:
            return format_party_name(raw, mode=mode, compact=compact, include_code=True)
    return code


def render_bar_chart(df, label_col, value_col, tooltip_label=None, full_label_col=None):
    chart_df = df.copy()
    order = chart_df[label_col].tolist()
    tooltip_fields = [alt.Tooltip(label_col, title=tooltip_label or label_col)]
    if full_label_col and full_label_col in chart_df.columns:
        tooltip_fields = [alt.Tooltip(full_label_col, title=tooltip_label or full_label_col)]
    tooltip_fields.append(alt.Tooltip(value_col, format=".2f", title=value_col))
    chart = alt.Chart(chart_df).mark_bar().encode(
        y=alt.Y(f"{label_col}:N", sort=order, title=None),
        x=alt.X(f"{value_col}:Q", title=value_col),
        color=alt.condition(alt.datum[value_col] >= 0, alt.value("#22d966"), alt.value("#3d8ef0")),
        tooltip=tooltip_fields,
    ).properties(height=max(220, len(chart_df) * 34))
    st.altair_chart(chart, use_container_width=True)


def render_compact_dataframe(df, rename_map=None):
    table = df.copy()
    if rename_map:
        table = table.rename(columns=rename_map)
    st.dataframe(table, use_container_width=True, hide_index=True)


def render_profile_cards(rows, label_a, label_b):
    cards = []
    for row in rows:
        cards.append(
            "<div class='data-card'>"
            f"<div class='metric'>{row['Metric']}</div>"
            f"<div class='value-line'><strong>{label_a}:</strong> {row[label_a]}</div>"
            f"<div class='value-line'><strong>{label_b}:</strong> {row[label_b]}</div>"
            f"<div class='year'>Year: {row['Year']}</div>"
            "</div>"
        )
    st.markdown(f"<div class='data-card-grid'>{''.join(cards)}</div>", unsafe_allow_html=True)

def build_finding(corr, factor_name, metric_label, party, year, merged, party_name_mode):
    if not is_valid_correlation(corr):
        return "weak", "RESULT UNAVAILABLE", "Result unavailable", \
            "The correlation value for this selection could not be computed reliably. No pattern claim should be made for this result.", \
            None, \
            f"Correlation unavailable · {len(merged)} municipalities · {municipal_vote_source_label(year)}"

    abs_r  = abs(corr)
    ranked = merged.sort_values("metric")
    low10  = ranked.head(10)["share"].mean()
    high10 = ranked.tail(10)["share"].mean()
    p_short = format_party_name(party, mode=party_name_mode, prose=True)
    m_short = METRIC_PHRASES.get(factor_name, metric_label.lower())

    note = f"Pearson r = {corr:.2f} · {len(merged)} municipalities · {municipal_vote_source_label(year)}"

    if abs_r < 0.30:
        return (
            "weak",
            "NO PATTERN",
            f"No consistent pattern found.",
            f"The data shows no consistent relationship between {m_short} and votes for {p_short} across {len(merged)} municipalities. "
            f"If you were looking for a story here — the data does not support it.",
            None,
            note
        )

    if corr < 0:
        direction = "lower"
        more_avg, less_avg = low10, high10
        low_label, high_label = "lowest", "highest"
    else:
        direction = "higher"
        more_avg, less_avg = high10, low10
        low_label, high_label = "highest", "lowest"

    gap = round(abs(more_avg - less_avg), 1)

    concrete = (
        f"Municipalities with {direction} {m_short} tend to vote more for {p_short}. "
        f"The gap is <strong>{gap:.1f} percentage points</strong>: "
        f"the 10 municipalities with the {low_label} {m_short} gave <strong>{more_avg:.1f}%</strong> to {p_short} in {year}, "
        f"compared to {less_avg:.1f}% in the 10 with the {high_label}."
    )
    if abs_r >= 0.70:
        copy_sentence = (
            f"Write: <em>\"In the {year} election, municipalities with {direction} {m_short} "
            f"gave on average {gap:.1f} percentage points more to {p_short}. "
            f"Based on data from {len(merged)} Danish municipalities. "
            f"(Source: {municipal_vote_source_inline(year)})\"</em>"
        )
    elif abs_r >= 0.50:
        copy_sentence = (
            f"Write: <em>\"In the {year} election, municipalities with {direction} {m_short} "
            f"tended to give more support to {p_short}. "
            f"Based on data from {len(merged)} Danish municipalities. "
            f"(Source: {municipal_vote_source_inline(year)})\"</em>"
        )
    else:
        copy_sentence = (
            f"Use with caution: <em>\"At municipality level, there is a weak association between {direction} {m_short} "
            f"and vote share for {p_short} in {year}. This does not explain why the pattern exists. "
            f"Based on data from {len(merged)} Danish municipalities. (Source: {municipal_vote_source_inline(year)})\"</em>"
        )

    if abs_r >= 0.70:
        return "strong",   "STRONG PATTERN · r = {:.2f}".format(corr),   "Municipalities with {direction} {m} tend to vote more for {p}.".format(direction=direction, m=m_short, p=p_short), concrete, copy_sentence, note
    elif abs_r >= 0.50:
        return "moderate", "MODERATE PATTERN · r = {:.2f}".format(corr), "Municipalities with {direction} {m} tend to vote more for {p}.".format(direction=direction, m=m_short, p=p_short), concrete, copy_sentence, note
    else:
        return "weak",     "WEAK PATTERN · r = {:.2f}".format(corr),     "Municipalities with {direction} {m} show a weak tendency toward {p}.".format(direction=direction, m=m_short, p=p_short), concrete, copy_sentence, note

# ── data loaders ──────────────────────────────────────────────────────────────

@st.cache_data
def load_municipal():
    frames = []
    share_files = [
        Path("denmark/folketing/fvpandel_party_share.csv"),
        Path("denmark/folketing/fv2026_party_share_by_municipality.csv"),
    ]
    for share_file in share_files:
        if not share_file.exists():
            continue
        frame = pd.read_csv(share_file, sep=";", encoding="utf-8-sig")
        frame.columns = ["party","municipality","year","share"]
        frames.append(frame)

    if not frames:
        return pd.DataFrame(columns=["party", "municipality", "year", "share"])

    df = pd.concat(frames, ignore_index=True)
    df["year"] = df["year"].astype(int)
    df = df[(df["party"] != "Total") & (df["municipality"] != "All Denmark")].copy()
    return exclude_public_special_cases(df)

@st.cache_data
def load_national():
    df = pd.read_csv("denmark/folketing/straubinger_votes_1953_2022.csv")
    cols = [c for c in df.columns if c.startswith("party_")]
    df = df.melt(id_vars=["year","date","total_valid"], value_vars=cols, var_name="party", value_name="votes")
    df["party"] = df["party"].str.replace("party_","").str.upper()
    df = df.dropna(subset=["votes"])
    df["share"] = (df["votes"] / df["total_valid"] * 100).round(1)
    return df

@st.cache_data
def load_population():
    path = FACTOR_DIR / "population.csv"
    if path.exists():
        df = pd.read_csv(path)
        df["year"] = df["year"].astype(int)
        return exclude_public_special_cases(
            df.rename(columns={"value": "population"})
        )
    df = pd.read_csv("denmark/socioeconomic/folk1a_population_annual.csv", sep=";", encoding="utf-8-sig")
    df = df[~EXCLUDE(df["OMRÅDE"])].copy()
    df["year"] = df["TID"].str[:4].astype(int)
    return df[["OMRÅDE","TID","year","INDHOLD"]].rename(columns={"OMRÅDE":"municipality","INDHOLD":"population"})

@st.cache_data
def load_factor_file(filename):
    path = FACTOR_DIR / filename
    if not path.exists():
        return pd.DataFrame(columns=["municipality", "year", "value"])
    df = pd.read_csv(path)
    df["year"] = df["year"].astype(int)
    return exclude_public_special_cases(df)

@st.cache_data
def load_income():
    return load_factor_file("income.csv")

@st.cache_data
def load_social():
    return load_factor_file("welfare_per_1000.csv")

@st.cache_data
def load_crime():
    return load_factor_file("crime_per_1000.csv")

@st.cache_data
def load_cars():
    return load_factor_file("cars_per_1000.csv")

@st.cache_data
def load_divorces():
    return load_factor_file("divorces_per_1000.csv")

@st.cache_data
def load_commute_distance():
    return load_factor_file("commute_distance_km.csv")

@st.cache_data
def load_education():
    return load_factor_file("education.csv")

@st.cache_data
def load_age65():
    return load_factor_file("age65_pct.csv")

@st.cache_data
def load_employment():
    return load_factor_file("employment_per_1000.csv")

@st.cache_data
def load_turnout():
    return load_factor_file("turnout_pct.csv")

@st.cache_data
def load_immigration():
    return load_factor_file("immigration_share_pct.csv")

@st.cache_data
def load_population_density():
    return load_factor_file("population_density.csv")

@st.cache_data
def load_unemployment():
    return load_factor_file("unemployment_pct.csv")

@st.cache_data
def load_owner_occupied_housing():
    return load_factor_file("owner_occupied_dwelling_share_pct.csv")

@st.cache_data
def load_detached_houses():
    return load_factor_file("detached_house_dwelling_share_pct.csv")

@st.cache_data
def load_one_person_households():
    return load_factor_file("one_person_household_share_pct.csv")

mun           = load_municipal()
nat           = load_national()
pop_df        = load_population()
income_df     = load_income()
social_df     = load_social()
crime_df      = load_crime()
cars_df       = load_cars()
divorce_df    = load_divorces()
commute_df    = load_commute_distance()
employment_df = load_employment()
education_df  = load_education()
age65_df      = load_age65()
turnout_df    = load_turnout()
immigration_df = load_immigration()
density_df    = load_population_density()
unemployment_df = load_unemployment()
owner_occupied_df = load_owner_occupied_housing()
detached_houses_df = load_detached_houses()
one_person_households_df = load_one_person_households()

# ── sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="hr-wordmark">HEDEGREEN RESEARCH<span class="dot"> ●</span></div>', unsafe_allow_html=True)
    st.markdown("**Danish Politics Data**")
    st.markdown(
        "<p style='font-size:0.75rem;color:#6a6a7a;line-height:1.6;margin-top:0.3rem;'>"
        "National vote trends 1953–2022. Municipality vote share 2007–2026, with the 2026 layer bridged from the official VALG export."
        "</p>", unsafe_allow_html=True
    )
    st.divider()
    party_name_mode = st.selectbox("Party names", PARTY_NAME_MODES, index=1)
    st.caption("Display labels only. Data and party IDs stay the same.")
    st.divider()
    page = st.radio("nav", ["Explore", "Compare municipalities", "By Municipality", "National trends", "About & sources"],
                    label_visibility="collapsed")
    st.divider()
    st.markdown(
        "<p style='font-size:0.65rem;color:#aaaabc;line-height:1.6;'>"
        "Data: Danmarks Statistik + official VALG 2026 bridge<br>Straubinger/folketingsvalg<br><br>"
        "Built by Hedegreen Research"
        "</p>", unsafe_allow_html=True
    )

# ── Explore (guided discovery) ────────────────────────────────────────────────

METRIC_OPTIONS = [
    ("Population",  "Population (reference count)",               "population",   "Do larger municipalities vote differently?"),
    ("Education",   "Higher education share (%)",                "education",   "Do more educated municipalities vote differently?"),
    ("Income",      "Avg. disposable income (DKK per person)",   "income",      "Do wealthier municipalities vote differently?"),
    ("Commute distance", "Avg. commute distance (km)",           "commute",     "Do long-commute municipalities vote differently?"),
    ("Employment",  "Full-time employees per 1,000 residents",   "employment",  "Do areas with higher employment vote differently?"),
    ("Welfare",     "Social assistance recipients per 1,000 residents", "social", "Do areas with more people on benefits vote differently?"),
    ("Crime",       "Reported crimes per 1,000 residents",       "crime",       "Is there a link between crime rates and voting patterns?"),
    ("Cars",        "Passenger cars per 1,000 residents",        "cars",        "Do car-heavy (rural) areas vote differently from urban ones?"),
    ("Age 65+",     "Share aged 65+ (%)",                        "age65",       "Do older municipalities vote differently?"),
    ("Turnout",     "Votes cast as share of voters (%)",         "turnout",     "Do high-turnout municipalities vote differently?"),
    ("Immigration share", "Residents without Danish origin (%)", "immigration", "Do municipalities with larger immigrant and descendant shares vote differently?"),
    ("Population density", "Residents per km²",                  "density",     "Does dense settlement correlate with voting behaviour?"),
    ("Unemployment", "Full-time unemployment rate (%)",          "unemployment","Do municipalities with higher unemployment vote differently?"),
    ("Owner-occupied housing", "Owner-occupied occupied dwellings (%)", "owner_occupied", "Do municipalities with more owner-occupied housing vote differently?"),
    ("Detached houses", "Detached/farmhouse occupied dwellings (%)", "detached_houses", "Do municipalities with more detached-house living patterns vote differently?"),
    ("One-person households", "Occupied dwellings with 1 person (%)", "one_person_households", "Do municipalities with more one-person households vote differently?"),
]
ALL_METRIC_KEYS    = [m[0] for m in METRIC_OPTIONS]
ALL_PARTY_NAMES    = sorted(mun["party"].unique())
ALL_ELECTION_YEARS = sorted(mun["year"].unique())
DEFAULT_EXPLORE_YEAR = 2022 if 2022 in ALL_ELECTION_YEARS else ALL_ELECTION_YEARS[-1]
MUNICIPAL_ELECTION_RANGE_LABEL = f"{ALL_ELECTION_YEARS[0]}–{ALL_ELECTION_YEARS[-1]}"

def get_metric_series(metric_key, year, _population, _income, _social, _crime, _cars, _divorces, _commute, _employment, _education, _age65, _turnout, _immigration, _density, _unemployment, _owner_occupied, _detached_houses, _one_person_households):
    if metric_key == "population":
        df = _population[_population["year"] == year][["municipality", "population"]].copy()
        df["metric"] = df["population"]
        return df[["municipality", "metric"]]
    if metric_key == "education":
        df = _education[_education["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "age65":
        df = _age65[_age65["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "income":
        df = _income[_income["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "commute":
        df = _commute[_commute["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "employment":
        df = _employment[_employment["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "social":
        df = _social[_social["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "crime":
        df = _crime[_crime["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "cars":
        df = _cars[_cars["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "divorces":
        df = _divorces[_divorces["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "turnout":
        df = _turnout[_turnout["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "immigration":
        df = _immigration[_immigration["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "density":
        df = _density[_density["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "unemployment":
        df = _unemployment[_unemployment["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "owner_occupied":
        df = _owner_occupied[_owner_occupied["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "detached_houses":
        df = _detached_houses[_detached_houses["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "one_person_households":
        df = _one_person_households[_one_person_households["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    return pd.DataFrame()


def metric_has_usable_year_data(metric_frame):
    if metric_frame.empty or "municipality" not in metric_frame.columns or "metric" not in metric_frame.columns:
        return False
    usable = metric_frame.dropna(subset=["metric"]).copy()
    if usable.empty:
        return False
    if usable["municipality"].nunique() < 10:
        return False
    if usable["metric"].nunique() <= 1:
        return False
    return True


def available_metric_keys_for_year(year, _population, _income, _social, _crime, _cars, _divorces, _commute, _employment, _education, _age65, _turnout, _immigration, _density, _unemployment, _owner_occupied, _detached_houses, _one_person_households):
    available = []
    for metric_name, _, metric_key, _ in METRIC_OPTIONS:
        metric_frame = get_metric_series(
            metric_key,
            year,
            _population,
            _income,
            _social,
            _crime,
            _cars,
            _divorces,
            _commute,
            _employment,
            _education,
            _age65,
            _turnout,
            _immigration,
            _density,
            _unemployment,
            _owner_occupied,
            _detached_houses,
            _one_person_households,
        )
        if metric_has_usable_year_data(metric_frame):
            available.append(metric_name)
    return available


def available_parties_for_year(year, municipal_df):
    year_frame = municipal_df[municipal_df["year"] == year].copy()
    if year_frame.empty:
        return []
    year_frame["share"] = pd.to_numeric(year_frame["share"], errors="coerce")
    active = year_frame.groupby("party", dropna=False)["share"].sum(min_count=1).reset_index()
    active = active[active["share"].fillna(0) > 0]
    return sorted(active["party"].unique())

@st.cache_data
def precompute_all_correlations(_mun, _pop_df, _income_df, _social_df, _crime_df, _cars_df, _divorce_df, _commute_df, _employment_df, _education_df, _age65_df, _turnout_df, _immigration_df, _density_df, _unemployment_df, _owner_occupied_df, _detached_houses_df, _one_person_households_df):
    rows = []
    for year in sorted(_mun["year"].unique()):
        for party in sorted(_mun["party"].unique()):
            votes = _mun[(_mun["year"] == year) & (_mun["party"] == party)][["municipality","share"]]
            if votes.empty: continue
            for m_name, m_label, m_key, _ in METRIC_OPTIONS:
                ms = get_metric_series(m_key, year, _pop_df, _income_df, _social_df, _crime_df, _cars_df, _divorce_df, _commute_df, _employment_df, _education_df, _age65_df, _turnout_df, _immigration_df, _density_df, _unemployment_df, _owner_occupied_df, _detached_houses_df, _one_person_households_df)
                if ms.empty or "municipality" not in ms.columns: continue
                merged = votes.merge(ms, on="municipality", how="inner")
                computed = compute_correlation_result(merged, factor=m_name, party=party, year=year, mode="precompute")
                if not computed["valid"]:
                    continue
                rows.append({"year": year, "party": party, "factor": m_name, "label": m_label, "r": computed["r"]})
    return pd.DataFrame(rows)

all_corr_df = precompute_all_correlations(mun, pop_df, income_df, social_df, crime_df, cars_df, divorce_df, commute_df, employment_df, education_df, age65_df, turnout_df, immigration_df, density_df, unemployment_df, owner_occupied_df, detached_houses_df, one_person_households_df)

if page == "Explore":

    # Initialise session state defaults (must happen before widgets render)
    if "cx_factors" not in st.session_state:
        st.session_state["cx_factors"] = ["Income"]
    if "cx_year" not in st.session_state:
        st.session_state["cx_year"] = DEFAULT_EXPLORE_YEAR
    if "cx_all_parties" not in st.session_state:
        st.session_state["cx_all_parties"] = True
    if "cx_parties" not in st.session_state:
        st.session_state["cx_parties"] = []
    if "cx_year_seen" not in st.session_state:
        st.session_state["cx_year_seen"] = st.session_state["cx_year"]
    if "cx_parties_seen_for_year" not in st.session_state:
        st.session_state["cx_parties_seen_for_year"] = []

    # Apply surprise values BEFORE widgets render (Streamlit requires this order)
    if st.session_state.get("_surprise_pending"):
        st.session_state["cx_year"]    = st.session_state.pop("_surprise_year")
        st.session_state["cx_factors"] = st.session_state.pop("_surprise_factors")
        st.session_state["cx_parties"] = st.session_state.pop("_surprise_parties")
        st.session_state["cx_all_parties"] = False
        del st.session_state["_surprise_pending"]

    st.markdown("<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>Danish Politics Data</p>", unsafe_allow_html=True)
    st.title("Is there a pattern?")
    st.markdown(
        "<p style='font-size:0.95rem;color:#5a5a6a;margin-bottom:2rem;'>"
        "Pick one or more factors, one or more parties, and an election year. Then find out."
        "</p>", unsafe_allow_html=True
    )

    # ── Step 1: year ──────────────────────────────────────────────────────────
    st.markdown('<div class="step-label">Step 1 — Which election year?</div>', unsafe_allow_html=True)
    cx_year = st.select_slider("year", options=ALL_ELECTION_YEARS, key="cx_year",
                               label_visibility="collapsed")

    available_metric_keys = available_metric_keys_for_year(
        cx_year,
        pop_df,
        income_df,
        social_df,
        crime_df,
        cars_df,
        divorce_df,
        commute_df,
        employment_df,
        education_df,
        age65_df,
        turnout_df,
        immigration_df,
        density_df,
        unemployment_df,
        owner_occupied_df,
        detached_houses_df,
        one_person_households_df,
    )
    parties_for_year = available_parties_for_year(cx_year, mun)

    current_metric_selection = [m for m in st.session_state.get("cx_factors", []) if m in available_metric_keys]
    if available_metric_keys and not current_metric_selection:
        current_metric_selection = [available_metric_keys[0]]
    st.session_state["cx_factors"] = current_metric_selection

    previous_year = st.session_state.get("cx_year_seen")
    previous_parties_for_year = st.session_state.get("cx_parties_seen_for_year", [])
    year_changed = previous_year != cx_year
    current_party_selection = [p for p in st.session_state.get("cx_parties", []) if p in parties_for_year]
    if st.session_state.get("cx_all_parties"):
        current_party_selection = parties_for_year
    elif year_changed:
        newly_available = [p for p in parties_for_year if p not in previous_parties_for_year]
        if newly_available:
            current_party_selection = [
                party for party in parties_for_year
                if party in set(current_party_selection) | set(newly_available)
            ]
    st.session_state["cx_parties"] = current_party_selection
    st.session_state["cx_year_seen"] = cx_year
    st.session_state["cx_parties_seen_for_year"] = parties_for_year

    # ── Step 2: metrics (year-aware selector) ────────────────────────────────
    st.markdown('<div class="step-label" style="margin-top:1rem;">Step 2 — What factors are available for that year?</div>', unsafe_allow_html=True)
    if available_metric_keys:
        cx_metric_keys = st.pills(
            "factors",
            available_metric_keys,
            key="cx_factors",
            selection_mode="multi",
            label_visibility="collapsed",
        )
    else:
        cx_metric_keys = []
        st.markdown(
            "<p style='font-size:0.74rem;color:#8888a0;margin-bottom:0;'>"
            "No usable municipality factor layer is available for that election year yet."
            "</p>",
            unsafe_allow_html=True,
        )

    # ── Step 3: parties (year-aware quick buttons + advanced multi) ─────────
    st.markdown('<div class="step-label" style="margin-top:1rem;">Step 3 — Pick a party</div>', unsafe_allow_html=True)
    all_toggle = st.checkbox("All parties", key="cx_all_parties")
    if all_toggle:
        cx_parties = parties_for_year
        st.session_state["cx_parties"] = parties_for_year
    else:
        cx_parties = st.pills(
            "parties",
            parties_for_year,
            key="cx_parties",
            selection_mode="multi",
            format_func=lambda p: format_party_name(p, mode=party_name_mode, compact=True, include_code=True),
            label_visibility="collapsed",
        )
        if not cx_parties:
            st.markdown(
                "<p style='font-size:0.74rem;color:#8888a0;margin-top:0.45rem;margin-bottom:0;'>"
                "No party is currently selected. Municipality-level pattern analysis requires at least one party selection."
                "</p>",
                unsafe_allow_html=True,
            )

    # ── Step 4: highlight a municipality (optional) ───────────────────────────
    st.markdown('<div class="step-label" style="margin-top:1rem;">Step 4 — Highlight a specific municipality? (optional)</div>', unsafe_allow_html=True)
    all_munis_explore = ["— none —"] + sorted(mun["municipality"].unique())
    cx_highlight = st.selectbox("highlight", all_munis_explore, key="cx_highlight",
                                label_visibility="collapsed")
    highlight_muni = None if cx_highlight == "— none —" else cx_highlight

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    if cx_year == 2026:
        st.markdown(
            "<p style='font-size:0.74rem;color:#8888a0;margin-top:0.2rem;margin-bottom:0.9rem;'>"
            "2026 municipality vote share comes from an official VALG fine-count aggregation. "
            "The wider municipality indicator refresh is still partial, so some factor combinations remain unavailable."
            "</p>",
            unsafe_allow_html=True,
        )

    col_main, col_surprise = st.columns([3, 1])
    with col_main:
        if st.button("Show me what the data reveals →", type="primary", use_container_width=True, disabled=(not available_metric_keys or not parties_for_year or not cx_parties)):
            st.session_state["explore_show"] = True
    with col_surprise:
        if st.button("Surprise me →", use_container_width=True):
            interesting = all_corr_df[all_corr_df["r"].abs() >= 0.40]
            if not interesting.empty:
                mode = random.choice(["single", "multi_factor", "multi_party"])
                anchor = interesting.sample(1).iloc[0]
                s_year = int(anchor["year"])
                if mode == "single":
                    # Case A: 1 factor, 1 party
                    factors  = [anchor["factor"]]
                    parties  = [anchor["party"]]
                elif mode == "multi_factor":
                    # Case B: top 2–3 factors for a random party in a random year
                    same = interesting[(interesting["party"] == anchor["party"]) &
                                       (interesting["year"]  == s_year)].nlargest(3, "r" if anchor["r"] > 0 else "r")
                    same = same.reindex(same["r"].abs().sort_values(ascending=False).index)
                    factors = same["factor"].tolist() if len(same) >= 2 else [anchor["factor"]]
                    parties = [anchor["party"]]
                else:
                    # Case C: top 2–3 parties for a random factor in a random year
                    same = interesting[(interesting["factor"] == anchor["factor"]) &
                                       (interesting["year"]  == s_year)]
                    same = same.reindex(same["r"].abs().sort_values(ascending=False).index)
                    factors = [anchor["factor"]]
                    parties = same["party"].tolist()[:3] if len(same) >= 2 else [anchor["party"]]
                st.session_state["_surprise_year"]    = s_year
                st.session_state["_surprise_factors"] = factors
                st.session_state["_surprise_parties"] = parties
                st.session_state["_surprise_pending"] = True
                st.session_state["explore_show"] = True
                st.rerun()

    # ── Results ───────────────────────────────────────────────────────────────
    if st.session_state.get("explore_show"):
        s_year, s_parties, s_metric_keys = cx_year, cx_parties, cx_metric_keys

        if not s_metric_keys or not s_parties:
            st.markdown(
                '<div class="finding weak">'
                '<div class="strength-tag">SELECTION INCOMPLETE</div>'
                '<div class="headline">This analysis cannot run yet.</div>'
                '<div class="body">A municipality-level correlation requires at least one factor and at least one party selection. No result should be inferred from an empty selection state.</div>'
                '</div>', unsafe_allow_html=True
            )
            st.stop()

        # Build correlation matrix: rows=parties, cols=metrics
        results = []
        for party in s_parties:
            votes = mun[(mun["year"] == s_year) & (mun["party"] == party)][["municipality","share"]]
            for mk in s_metric_keys:
                m_info  = next(m for m in METRIC_OPTIONS if m[0] == mk)
                m_label = m_info[1]
                ms = get_metric_series(m_info[2], s_year, pop_df, income_df, social_df, crime_df, cars_df, divorce_df, commute_df, employment_df, education_df, age65_df, turnout_df, immigration_df, density_df, unemployment_df, owner_occupied_df, detached_houses_df, one_person_households_df)
                if ms.empty or "municipality" not in ms.columns:
                    continue
                merged  = votes.merge(ms, on="municipality", how="inner")
                if merged.empty: continue
                computed = compute_correlation_result(merged, factor=mk, party=party, year=s_year, mode="explore")
                results.append({
                    "party": party,
                    "factor": mk,
                    "label": m_label,
                    "r": computed["r"],
                    "merged": computed["merged"],
                    "valid": computed["valid"],
                    "n": computed["n"],
                    "reason": computed["reason"],
                    "strength": corr_strength_label(computed["r"])
                })

        if not results:
            st.markdown(
                '<div class="finding weak">'
                '<div class="strength-tag">NO DATA</div>'
                '<div class="headline">This combination has no data.</div>'
                '<div class="body">The selected factor is not available for this election year. Try a different year or factor.</div>'
                '</div>', unsafe_allow_html=True
            )
            st.stop()

        # Visual break before result
        st.markdown(
            "<div style='margin:2rem 0 0.5rem;border-top:2px solid #0d0d14;'>"
            "<span style='font-size:0.58rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;"
            "color:#0d0d14;background:#f5f5f7;padding:0 0.6rem;position:relative;top:-0.7rem;'>RESULT</span>"
            "</div>", unsafe_allow_html=True
        )

        def finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note, context_label=None):
            ctx = f'<div class="copy-label" style="margin-bottom:0.3rem;">{context_label}</div>' if context_label else ""
            copy_block = ""
            if copy_sentence:
                copy_label = "Use with caution:" if strength_tag.startswith("WEAK PATTERN") else "Write this as:"
                copy_block = (
                    f'<div class="copy-label">{copy_label}</div>'
                    f'<div class="copy-box">{copy_sentence}</div>'
                )
            return (
                f'<div class="finding {strength_cls}">'
                f'<div class="strength-tag">{strength_tag}</div>'
                f'{ctx}'
                f'<div class="headline">{headline}</div>'
                f'<div class="body">{concrete}</div>'
                f'{copy_block}'
                f'<div class="footnote">{note}</div>'
                f'</div>'
            )

        def how_to_read():
            with st.expander("How to read this result"):
                st.markdown("""
**STRONG PATTERN (abs(r) ≥ 0.70)** — Write: *"Data from 98 municipalities shows a clear link."*
**MODERATE PATTERN (abs(r) 0.50–0.70)** — Write: *"There is a consistent tendency."*
**WEAK PATTERN (abs(r) 0.30–0.50)** — Use with caution. It is a weak municipality-level association, not an explanation.
**NO PATTERN (abs(r) below 0.30)** — Do not write a pattern claim. The data does not support it.

Positive r = both go up together. Negative r = they go in opposite directions.

*Correlation ≠ cause. The data shows a pattern — not why it exists.*
                """)

        # ── Case A: 1 party, 1 metric → full finding + scatter ───────────────
        if len(s_parties) == 1 and len(s_metric_keys) == 1:
            row = results[0]
            if not row["valid"]:
                invalid_body = (
                    f"{invalid_result_detail(row['reason'])} "
                    "No pattern claim should be made for this result."
                )
                st.markdown(
                    '<div class="finding weak">'
                    '<div class="strength-tag">RESULT UNAVAILABLE</div>'
                    '<div class="headline">Result unavailable</div>'
                    f'<div class="body">{invalid_body}</div>'
                    '</div>', unsafe_allow_html=True
                )
                st.stop()
            strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(
                row["r"], row["factor"], row["label"], row["party"], s_year, row["merged"], party_name_mode)
            st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note),
                        unsafe_allow_html=True)
            how_to_read()

            # Always show the extremes — the concrete municipalities at both ends
            metric_short = METRIC_SHORT_LABELS.get(row["factor"], row["label"])
            ranked_data = row["merged"].sort_values("metric").rename(columns={
                "municipality": "Municipality",
                "share": "Vote %",
                "metric": metric_short
            })
            tab_lo, tab_hi = st.tabs([f"Lowest {metric_short}", f"Highest {metric_short}"])
            with tab_lo:
                st.markdown(
                    f"<p style='font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;"
                    f"color:#aaaabc;margin-bottom:0.3rem;'>Lowest {metric_short} →</p>",
                    unsafe_allow_html=True
                )
                render_compact_dataframe(ranked_data.head(10))
            with tab_hi:
                st.markdown(
                    f"<p style='font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;"
                    f"color:#aaaabc;margin-bottom:0.3rem;'>Highest {metric_short} →</p>",
                    unsafe_allow_html=True
                )
                render_compact_dataframe(ranked_data.tail(10).sort_values(metric_short, ascending=False))

            # ── Highlight callout ──────────────────────────────────────────────
            if highlight_muni:
                h_row = row["merged"][row["merged"]["municipality"] == highlight_muni]
                if not h_row.empty:
                    h_metric = h_row["metric"].iloc[0]
                    h_share  = h_row["share"].iloc[0]
                    # Rank position
                    sorted_all = row["merged"].sort_values("metric").reset_index(drop=True)
                    h_rank = sorted_all[sorted_all["municipality"] == highlight_muni].index[0] + 1
                    st.markdown(
                        f'<div style="border:1px solid #22d966;padding:0.8rem 1.1rem;margin-bottom:1rem;background:#f4fef8;">'
                        f'<span style="font-size:0.58rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:#22d966;">HIGHLIGHTED: {highlight_muni}</span><br>'
                        f'<span style="font-size:0.88rem;color:#0d0d14;">{row["label"]}: <strong>{h_metric:.1f}</strong> &nbsp;·&nbsp; '
                        f'Vote share: <strong>{h_share:.1f}%</strong> &nbsp;·&nbsp; '
                        f'Rank {h_rank} of {len(sorted_all)} municipalities by {metric_short.lower()}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.caption(f"No data for {highlight_muni} in {s_year}.")

            st.markdown("<p style='font-size:0.75rem;color:#aaaabc;margin-top:1rem;'>Each dot = one municipality. Named dots = extremes.</p>", unsafe_allow_html=True)
            scatter_df = row["merged"].copy()
            scatter_df["vote_share"] = pd.to_numeric(scatter_df["share"], errors="coerce")
            scatter_df["metric_value"] = pd.to_numeric(scatter_df["metric"], errors="coerce")
            scatter_df = scatter_df.dropna(subset=["vote_share", "metric_value"]).copy()
            # Label top 5 + bottom 5 by metric, plus the highlighted municipality
            sorted_sc = scatter_df.sort_values("metric_value")
            label_munis = set(sorted_sc.head(5)["municipality"]) | set(sorted_sc.tail(5)["municipality"])
            if highlight_muni:
                label_munis.add(highlight_muni)
            scatter_df["label"] = scatter_df["municipality"].where(scatter_df["municipality"].isin(label_munis), "")
            scatter_df["highlighted"] = scatter_df["municipality"] == (highlight_muni or "")
            base = alt.Chart(scatter_df).encode(
                x=alt.X("metric_value:Q", title=row["label"]),
                y=alt.Y("vote_share:Q", title="Vote share (%)"),
                tooltip=[
                    alt.Tooltip("municipality:N", title="Municipality"),
                    alt.Tooltip("metric_value:Q", title=row["label"]),
                    alt.Tooltip("vote_share:Q", title="Vote share (%)"),
                ]
            )
            points_normal = base.transform_filter(
                alt.datum.highlighted == False
            ).mark_circle(size=55, color="#22d966", opacity=0.65)
            points_highlight = base.transform_filter(
                alt.datum.highlighted == True
            ).mark_circle(size=120, color="#e63946", opacity=1.0)
            labels = base.mark_text(align="left", dx=5, dy=-4, fontSize=10, color="#5a5a6a").encode(
                text="label:N"
            )
            st.altair_chart((points_normal + points_highlight + labels).properties(height=350), use_container_width=True)
            with st.expander(f"See all {len(ranked_data)} municipalities"):
                render_compact_dataframe(ranked_data.sort_values("Vote %", ascending=False))

        # ── Case B: multiple metrics, 1 party → "what predicts this party?" ──
        elif len(s_parties) == 1 and len(s_metric_keys) > 1:
            party = s_parties[0]
            valid_results = [r for r in results if r["valid"]]
            if not valid_results:
                st.markdown(
                    '<div class="finding weak">'
                    '<div class="strength-tag">NO VALID RESULT</div>'
                    '<div class="headline">No valid correlation result available</div>'
                    '<div class="body">None of the selected factor-party combinations produced a valid correlation value. No strongest signal is shown.</div>'
                    '</div>', unsafe_allow_html=True
                )
                st.stop()
            ranked = sorted(valid_results, key=lambda x: abs(float(x["r"])), reverse=True)
            # Bar chart first — most informative view
            summary = pd.DataFrame([{
                "Factor": r["factor"],
                "Label": METRIC_SHORT_LABELS.get(r["factor"], r["factor"]),
                "r": r["r"],
                "Strength": r["strength"],
            } for r in ranked])
            st.markdown("<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.3rem;'>Results are ranked by correlation strength (absolute value). Positive = more votes where factor is higher. Negative = more votes where factor is lower.</p>", unsafe_allow_html=True)
            render_bar_chart(summary, "Label", "r", tooltip_label="Factor", full_label_col="Factor")
            # Compute inter-factor overlaps
            overlap_notes = {}
            if len(s_metric_keys) >= 2:
                factor_series = {}
                for mk in s_metric_keys:
                    m_info = next(m for m in METRIC_OPTIONS if m[0] == mk)
                    ms = get_metric_series(m_info[2], s_year, pop_df, income_df, social_df, crime_df, cars_df, divorce_df, commute_df, employment_df, education_df, age65_df, turnout_df, immigration_df, density_df, unemployment_df, owner_occupied_df, detached_houses_df, one_person_households_df)
                    if not ms.empty:
                        factor_series[mk] = ms.set_index("municipality")["metric"]
                rank_order = {r["factor"]: i for i, r in enumerate(ranked)}
                factor_names = list(factor_series.keys())
                for fi, fa in enumerate(factor_names):
                    for fb in factor_names[fi+1:]:
                        combined = pd.DataFrame({"a": factor_series[fa], "b": factor_series[fb]}).dropna()
                        if len(combined) >= 10:
                            inter_r = round(float(combined["a"].corr(combined["b"])), 2)
                            if abs(inter_r) >= 0.60:
                                higher = fa if rank_order.get(fa, 999) < rank_order.get(fb, 999) else fb
                                lower = fb if higher == fa else fa
                                if lower not in overlap_notes:
                                    overlap_notes[lower] = f"Note: {lower} and {higher} tend to move together across municipalities (r = {inter_r:.2f})."
            # Show a finding box for every factor with |r| ≥ 0.30
            meaningful = [r for r in ranked if abs(float(r["r"])) >= 0.30]
            no_pattern = [r for r in ranked if abs(float(r["r"])) < 0.30]
            if not meaningful:
                meaningful = [ranked[0]]  # always show at least the top one
            for i, row in enumerate(meaningful):
                strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(
                    row["r"], row["factor"], row["label"], party, s_year, row["merged"], party_name_mode)
                st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note),
                            unsafe_allow_html=True)
            if overlap_notes:
                for note_text in overlap_notes.values():
                    st.markdown(
                        f"<p style='font-size:0.72rem;color:#8888a0;margin-top:0.3rem;margin-bottom:0.3rem;'>"
                        f"{note_text}</p>",
                        unsafe_allow_html=True
                    )
            if no_pattern:
                no_pattern_names = ", ".join(r["factor"] for r in no_pattern)
                st.markdown(
                    f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.5rem;'>"
                    f"No pattern found for: {no_pattern_names} (abs(r) below 0.30).</p>",
                    unsafe_allow_html=True
                )
            how_to_read()
            with st.expander("See full ranking table"):
                render_compact_dataframe(summary[["Factor", "r", "Strength"]])

        # ── Case C: multiple parties, 1 metric → "which parties link to X?" ──
        elif len(s_parties) > 1 and len(s_metric_keys) == 1:
            valid_results = [r for r in results if r["valid"]]
            if not valid_results:
                st.markdown(
                    '<div class="finding weak">'
                    '<div class="strength-tag">NO VALID RESULT</div>'
                    '<div class="headline">No valid correlation result available</div>'
                    '<div class="body">None of the selected factor-party combinations produced a valid correlation value. No strongest signal is shown.</div>'
                    '</div>', unsafe_allow_html=True
                )
                st.stop()
            ranked = sorted(valid_results, key=lambda x: abs(float(x["r"])), reverse=True)
            # Bar chart first
            summary = pd.DataFrame([{
                "Party": format_party_name(r["party"], mode=party_name_mode, compact=True, include_code=True),
                "Party_full": format_party_name(r["party"], mode=party_name_mode, include_code=True),
                "r": r["r"],
                "Strength": r["strength"],
            } for r in ranked])
            st.markdown("<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.3rem;'>Results are ranked by correlation strength (absolute value). Positive = more votes where factor is higher. Negative = more votes where factor is lower.</p>", unsafe_allow_html=True)
            render_bar_chart(summary, "Party", "r", tooltip_label="Party", full_label_col="Party_full")
            # Finding box for every party with |r| ≥ 0.30
            meaningful = [r for r in ranked if abs(float(r["r"])) >= 0.30]
            no_pattern = [r for r in ranked if abs(float(r["r"])) < 0.30]
            if not meaningful:
                meaningful = [ranked[0]]
            for i, row in enumerate(meaningful):
                strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(
                    row["r"], row["factor"], row["label"], row["party"], s_year, row["merged"], party_name_mode)
                st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note),
                            unsafe_allow_html=True)
            if no_pattern:
                no_pattern_names = ", ".join(format_party_name(r["party"], mode=party_name_mode, compact=True) for r in no_pattern)
                st.markdown(
                    f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.5rem;'>"
                    f"No pattern found for: {no_pattern_names} (abs(r) below 0.30).</p>",
                    unsafe_allow_html=True
                )
            how_to_read()
            with st.expander("See full ranking table"):
                render_compact_dataframe(summary[["Party_full", "r", "Strength"]], rename_map={"Party_full": "Party"})

        # ── Case D: multiple parties + multiple metrics → matrix ──────────────
        else:
            valid_results = [r for r in results if r["valid"]]
            if not valid_results:
                st.markdown(
                    '<div class="finding weak">'
                    '<div class="strength-tag">NO VALID RESULT</div>'
                    '<div class="headline">No valid correlation result available</div>'
                    '<div class="body">None of the selected factor-party combinations produced a valid correlation value. No strongest signal is shown.</div>'
                    '</div>', unsafe_allow_html=True
                )
                st.stop()
            top = max(valid_results, key=lambda x: abs(float(x["r"])))
            strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(
                top["r"], top["factor"], top["label"], top["party"], s_year, top["merged"], party_name_mode)
            st.markdown(
                "<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.5rem;'>"
                "Showing highest correlation across selected factors and parties. "
                "Use the full correlation table to inspect all results.</p>",
                unsafe_allow_html=True
            )
            st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note,
                                     context_label=f"Strongest signal: {format_party_name(top['party'], mode=party_name_mode, compact=True)} × {top['factor']}"),
                        unsafe_allow_html=True)
            other_count = len(valid_results) - 1
            if other_count > 0:
                st.markdown(
                    f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.3rem;'>"
                    f"{other_count} other signal{'s' if other_count > 1 else ''} exist — see full correlation table.</p>",
                    unsafe_allow_html=True
                )
            how_to_read()
            with st.expander("See full correlation table"):
                flat = [{"Party": format_party_name(r["party"], mode=party_name_mode, include_code=True), "Factor": r["factor"], "r": r["r"]} for r in valid_results]
                flat_df = pd.DataFrame(flat).assign(abs_r=lambda d: d["r"].abs()).sort_values("abs_r", ascending=False).drop(columns="abs_r").reset_index(drop=True)
                render_compact_dataframe(flat_df)

# ── Compare municipalities ────────────────────────────────────────────────────

elif page == "Compare municipalities":
    st.markdown("<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>Danish Politics Data</p>", unsafe_allow_html=True)
    st.title("Compare two municipalities")
    st.markdown(
        "<p style='font-size:0.95rem;color:#5a5a6a;margin-bottom:1.5rem;'>"
        "Pick two municipalities. See how their voting patterns and socioeconomic profiles differ."
        "</p>", unsafe_allow_html=True
    )

    all_munis = sorted(mun["municipality"].unique())
    col1, col2 = st.columns(2)
    with col1:
        mun_a = st.selectbox("Municipality A", all_munis, index=0)
    with col2:
        mun_b = st.selectbox("Municipality B", all_munis, index=1)

    if mun_a == mun_b:
        st.warning("Select two different municipalities.")
        st.stop()

    # ── Voting patterns ───────────────────────────────────────────────────────
    st.markdown("## Voting patterns")

    votes_a = mun[mun["municipality"] == mun_a].pivot_table(index="year", columns="party", values="share")
    votes_b = mun[mun["municipality"] == mun_b].pivot_table(index="year", columns="party", values="share")

    # Parties where they differ most on average
    common = votes_a.columns.intersection(votes_b.columns)
    diff_abs = (votes_a[common] - votes_b[common]).abs()
    top_parties = diff_abs.mean().sort_values(ascending=False).head(6).index.tolist()

    gap_df = (votes_a[top_parties] - votes_b[top_parties]).round(1)
    gap_chart_df = pd.DataFrame({
        "Party": [format_party_name(p, mode=party_name_mode, compact=True, include_code=True) for p in top_parties],
        "Party_full": [format_party_name(p, mode=party_name_mode, include_code=True) for p in top_parties],
        "Gap": [gap_df[p].mean() for p in top_parties],
    })

    st.markdown(
        f"<p style='font-size:0.82rem;color:#6a6a7a;margin-bottom:0.5rem;'>"
        f"Percentage point gap in vote share: <strong>{mun_a}</strong> minus <strong>{mun_b}</strong>. "
        f"Positive bar = {mun_a} votes more for that party. Negative = {mun_b} does.</p>",
        unsafe_allow_html=True
    )
    render_bar_chart(gap_chart_df, "Party", "Gap", tooltip_label="Party", full_label_col="Party_full")

    # Biggest single gap
    max_gap_row = gap_chart_df.iloc[gap_chart_df["Gap"].abs().idxmax()]
    max_gap_party = max_gap_row["Party_full"]
    max_gap_val = round(float(max_gap_row["Gap"]), 1)
    direction = mun_a if max_gap_val > 0 else mun_b
    st.markdown(
        f'<div class="finding moderate">'
        f'<div class="headline">Biggest difference: {max_gap_party}</div>'
        f'<div class="body">On average across all elections, <strong>{direction}</strong> votes '
        f'<strong>{abs(max_gap_val):.1f} percentage points more</strong> for {max_gap_party} than the other municipality.</div>'
        f'<div class="footnote">Based on {MUNICIPAL_ELECTION_RANGE_LABEL} municipality elections · Danmarks Statistik (2007–2022) + official VALG bridge (2026)</div>'
        f'</div>', unsafe_allow_html=True
    )

    with st.expander("See full vote history for both municipalities"):
        display_columns = [format_party_name(p, mode=party_name_mode, compact=True, include_code=True) for p in top_parties]
        votes_a_display = votes_a[top_parties].round(1).copy()
        votes_b_display = votes_b[top_parties].round(1).copy()
        votes_a_display.columns = display_columns
        votes_b_display.columns = display_columns
        tab_a, tab_b = st.tabs([mun_a, mun_b])
        with tab_a:
            st.markdown(f"**{mun_a}**")
            st.dataframe(votes_a_display, use_container_width=True)
        with tab_b:
            st.markdown(f"**{mun_b}**")
            st.dataframe(votes_b_display, use_container_width=True)

    # ── Socioeconomic profile ─────────────────────────────────────────────────
    st.markdown("## Socioeconomic profile")
    st.markdown(
        "<p style='font-size:0.82rem;color:#6a6a7a;margin-bottom:0.8rem;'>"
        "Current municipality profile using the most recent available data for each metric. "
        "Years may differ by metric. Per-1,000 and percentage factors are shown directly from the normalized public factor layer."
        "</p>", unsafe_allow_html=True
    )

    def latest_val(df, municipality, year_col="year", val_col="value"):
        sub = df[df["municipality"] == municipality]
        if sub.empty: return None, None
        yr = sub[year_col].max()
        v = sub[sub[year_col] == yr][val_col]
        return (float(v.values[0]) if len(v) > 0 else None), int(yr)

    def pop_for(municipality):
        sub = pop_df[pop_df["municipality"] == municipality].sort_values(["year", "reference_period"], ascending=False)
        if sub.empty: return None
        return float(sub["population"].values[0])

    pop_a = pop_for(mun_a)
    pop_b = pop_for(mun_b)

    profile_rows = []

    pop_value_a, pop_year = latest_val(pop_df, mun_a, val_col="population")
    pop_value_b, _ = latest_val(pop_df, mun_b, val_col="population")
    if pop_value_a is not None and pop_value_b is not None:
        profile_rows.append({"Metric": "Population", mun_a: f"{pop_value_a:,.0f}", mun_b: f"{pop_value_b:,.0f}", "Year": pop_year})

    edu_a, yr = latest_val(education_df, mun_a)
    edu_b, _  = latest_val(education_df, mun_b)
    if edu_a is not None and edu_b is not None:
        profile_rows.append({"Metric": "Higher education (%)", mun_a: f"{edu_a:.1f}%", mun_b: f"{edu_b:.1f}%", "Year": yr})

    inc_a, yr = latest_val(income_df, mun_a)
    inc_b, _  = latest_val(income_df, mun_b)
    if inc_a is not None and inc_b is not None:
        profile_rows.append({"Metric": "Avg. disposable income (DKK)", mun_a: f"{inc_a:,.0f}", mun_b: f"{inc_b:,.0f}", "Year": yr})

    commute_a, yr = latest_val(commute_df, mun_a)
    commute_b, _  = latest_val(commute_df, mun_b)
    if commute_a is not None and commute_b is not None:
        profile_rows.append({"Metric": "Avg. commute distance (km)", mun_a: f"{commute_a:.1f}", mun_b: f"{commute_b:.1f}", "Year": yr})

    emp_a, yr = latest_val(employment_df, mun_a)
    emp_b, _  = latest_val(employment_df, mun_b)
    if emp_a is not None and emp_b is not None:
        profile_rows.append({"Metric": "Full-time employees per 1,000", mun_a: f"{emp_a:.1f}", mun_b: f"{emp_b:.1f}", "Year": yr})

    soc_a, yr = latest_val(social_df, mun_a)
    soc_b, _  = latest_val(social_df, mun_b)
    if soc_a is not None and soc_b is not None:
        profile_rows.append({"Metric": "Welfare recipients per 1,000", mun_a: f"{soc_a:.1f}", mun_b: f"{soc_b:.1f}", "Year": yr})

    cr_a, yr = latest_val(crime_df, mun_a)
    cr_b, _  = latest_val(crime_df, mun_b)
    if cr_a is not None and cr_b is not None:
        profile_rows.append({"Metric": "Reported crimes per 1,000", mun_a: f"{cr_a:.1f}", mun_b: f"{cr_b:.1f}", "Year": yr})

    car_a, yr = latest_val(cars_df, mun_a)
    car_b, _  = latest_val(cars_df, mun_b)
    if car_a is not None and car_b is not None:
        profile_rows.append({"Metric": "Passenger cars per 1,000", mun_a: f"{car_a:.1f}", mun_b: f"{car_b:.1f}", "Year": yr})

    div_a, yr = latest_val(divorce_df, mun_a)
    div_b, _  = latest_val(divorce_df, mun_b)
    if div_a is not None and div_b is not None:
        profile_rows.append({"Metric": "Divorces per 1,000", mun_a: f"{div_a:.1f}", mun_b: f"{div_b:.1f}", "Year": yr})

    age_a, yr = latest_val(age65_df, mun_a)
    age_b, _  = latest_val(age65_df, mun_b)
    if age_a is not None and age_b is not None:
        profile_rows.append({"Metric": "Aged 65+ (%)", mun_a: f"{age_a:.1f}%", mun_b: f"{age_b:.1f}%", "Year": yr})

    turnout_a, yr = latest_val(turnout_df, mun_a)
    turnout_b, _ = latest_val(turnout_df, mun_b)
    if turnout_a is not None and turnout_b is not None:
        profile_rows.append({"Metric": "Turnout (%)", mun_a: f"{turnout_a:.1f}%", mun_b: f"{turnout_b:.1f}%", "Year": yr})

    imm_a, yr = latest_val(immigration_df, mun_a)
    imm_b, _ = latest_val(immigration_df, mun_b)
    if imm_a is not None and imm_b is not None:
        profile_rows.append({"Metric": "Residents without Danish origin (%)", mun_a: f"{imm_a:.1f}%", mun_b: f"{imm_b:.1f}%", "Year": yr})

    dens_a, yr = latest_val(density_df, mun_a)
    dens_b, _ = latest_val(density_df, mun_b)
    if dens_a is not None and dens_b is not None:
        profile_rows.append({"Metric": "Population density (per km²)", mun_a: f"{dens_a:.1f}", mun_b: f"{dens_b:.1f}", "Year": yr})

    unemp_a, yr = latest_val(unemployment_df, mun_a)
    unemp_b, _ = latest_val(unemployment_df, mun_b)
    if unemp_a is not None and unemp_b is not None:
        profile_rows.append({"Metric": "Unemployment (%)", mun_a: f"{unemp_a:.1f}%", mun_b: f"{unemp_b:.1f}%", "Year": yr})

    owner_a, yr = latest_val(owner_occupied_df, mun_a)
    owner_b, _ = latest_val(owner_occupied_df, mun_b)
    if owner_a is not None and owner_b is not None:
        profile_rows.append({"Metric": "Owner-occupied dwellings (%)", mun_a: f"{owner_a:.1f}%", mun_b: f"{owner_b:.1f}%", "Year": yr})

    detached_a, yr = latest_val(detached_houses_df, mun_a)
    detached_b, _ = latest_val(detached_houses_df, mun_b)
    if detached_a is not None and detached_b is not None:
        profile_rows.append({"Metric": "Detached/farmhouse dwellings (%)", mun_a: f"{detached_a:.1f}%", mun_b: f"{detached_b:.1f}%", "Year": yr})

    one_person_a, yr = latest_val(one_person_households_df, mun_a)
    one_person_b, _ = latest_val(one_person_households_df, mun_b)
    if one_person_a is not None and one_person_b is not None:
        profile_rows.append({"Metric": "One-person households (%)", mun_a: f"{one_person_a:.1f}%", mun_b: f"{one_person_b:.1f}%", "Year": yr})

    if profile_rows:
        render_profile_cards(profile_rows, mun_a, mun_b)
        with st.expander("See profile as full table"):
            st.dataframe(pd.DataFrame(profile_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Socioeconomic data not available for this combination.")

    st.markdown(
        "<p style='font-size:0.68rem;color:#aaaabc;margin-top:1rem;'>"
        "Source: Danmarks Statistik (CC 4.0 BY) · Correlation ≠ causation</p>",
        unsafe_allow_html=True
    )

# ── By Municipality ───────────────────────────────────────────────────────────

elif page == "By Municipality":
    st.subheader("By municipality")
    st.markdown(
        "<p style='color:#6a6a7a;font-size:0.82rem;margin-bottom:1.2rem;'>"
        "Pick a party and a year. See all 98 municipalities ranked by vote share."
        "</p>", unsafe_allow_html=True
    )
    col1, col2 = st.columns(2)
    with col1:
        year  = st.selectbox("Election year", sorted(mun["year"].unique(), reverse=True))
    with col2:
        parties_for_year = available_parties_for_year(year, mun)
        party = st.selectbox("Party", parties_for_year, format_func=lambda p: format_party_name(p, mode=party_name_mode, include_code=True))

    filtered = mun[(mun["year"] == year) & (mun["party"] == party)].sort_values("share", ascending=False)
    top    = filtered.iloc[0]
    bottom = filtered.iloc[-1]
    avg    = filtered["share"].mean()

    st.markdown(
        f"<p style='font-size:0.82rem;color:#3a3a4a;margin-bottom:0.8rem;'>"
        f"<strong>Highest:</strong> {top['municipality']} ({top['share']}%) &nbsp;·&nbsp; "
        f"<strong>Lowest:</strong> {bottom['municipality']} ({bottom['share']}%) &nbsp;·&nbsp; "
        f"<strong>Avg:</strong> {avg:.1f}%</p>",
        unsafe_allow_html=True
    )
    render_compact_dataframe(
        filtered[["municipality","share"]].rename(columns={"municipality": "Municipality", "share":"Vote %"})
    )
    with st.expander("Show full municipality bar chart"):
        st.bar_chart(filtered.set_index("municipality")["share"])

# ── National trends ───────────────────────────────────────────────────────────

elif page == "National trends":
    st.subheader("National vote share, 1953–2022")
    st.markdown(
        "<p style='color:#6a6a7a;font-size:0.82rem;margin-bottom:1rem;'>"
        "25 elections across 70 years. Select which parties to compare."
        "</p>", unsafe_allow_html=True
    )
    parties_nat = sorted(nat["party"].unique())
    selected = st.multiselect("Parties", parties_nat,
                              default=[p for p in ["S","V","DF","EL","M"] if p in parties_nat],
                              format_func=lambda p: format_party_code(p, mode=party_name_mode, compact=True))
    if selected:
        pivot = nat[nat["party"].isin(selected)].pivot_table(index="year", columns="party", values="share")
        pivot = pivot.rename(columns=lambda code: format_party_code(code, mode=party_name_mode, compact=True))
        st.line_chart(pivot)
        table = pivot.round(1).astype(object).where(pivot.notna(), "—")
        st.dataframe(table, use_container_width=True)

# ── About & sources ───────────────────────────────────────────────────────────

elif page == "About & sources":
    st.subheader("About")
    st.markdown("""
National Danish election results 1953–2022, plus municipality-level vote share 2007–2026, cross-referenced with a growing set of municipality-level indicators from Danmarks Statistik.
Built for journalists and researchers. No login required. All data is public and open-licensed (CC 4.0 BY).

Built by [Hedegreen Research](https://hedegreenresearch.com).

**Method note**
- Correlation ≠ causation.
- Some municipality indicators use the most recent available year for that metric, so years can differ in profile-style views.
 - The 2026 municipality vote-share layer is currently bridged from the official `VALG` export before the familiar Statistikbanken municipality tables catch up.
 - Wave 2 commute and housing factors are year-aware by design. Housing coverage starts in `2010`, and owner-occupied housing currently skips `2021–2022` because DST keeps those years closed in `BOL101`.
 - `Divorces` stays withheld from the public factor layer until the municipality-total source path is trustworthy.
    """)
    st.subheader("Data sources")
    st.markdown("""
<div class="source-item"><strong>FVPANDEL</strong> — Party vote share per municipality, 2007–2022. Danmarks Statistik</div>
<div class="source-item"><strong>VALG public export</strong> — Official 2026 fine-count results aggregated from polling-area level to municipality level for the public bridge layer.</div>
<div class="source-item"><strong>Straubinger/folketingsvalg</strong> — National vote counts, 1953–2022. GitHub</div>
<div class="source-item"><strong>INDKP101</strong> — Avg. disposable income per municipality, 1987–2024. Danmarks Statistik</div>
<div class="source-item"><strong>AUK01</strong> — Social assistance recipients per municipality, 2007–present. Danmarks Statistik</div>
<div class="source-item"><strong>STRAF11</strong> — Reported crimes per municipality, 2007–present. Danmarks Statistik</div>
<div class="source-item"><strong>BIL707</strong> — Passenger cars per municipality, 2007–present. Danmarks Statistik</div>
<div class="source-item"><strong>FOLK1AM</strong> — Population per municipality. Danmarks Statistik</div>
<div class="source-item"><strong>FVKOM</strong> — Municipality turnout can be derived from valid + invalid votes versus number of voters. Danmarks Statistik</div>
<div class="source-item"><strong>FOLK1E</strong> — Immigration share at municipality level via herkomst categories. Danmarks Statistik</div>
<div class="source-item"><strong>ARE207</strong> — Area per municipality for density calculations. Danmarks Statistik</div>
<div class="source-item"><strong>AUP02</strong> — Unemployment rate per municipality. Danmarks Statistik</div>
<div class="source-item"><strong>AFSTB4</strong> — Average commute distance by municipality (employed total, ultimo November). Danmarks Statistik</div>
<div class="source-item"><strong>BOL101</strong> — Owner-occupied share within occupied dwellings. Danmarks Statistik</div>
<div class="source-item"><strong>BOL103</strong> — Detached-house share and one-person-household share within occupied dwellings. Danmarks Statistik</div>
    """, unsafe_allow_html=True)
