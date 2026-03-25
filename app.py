import streamlit as st
import pandas as pd
import altair as alt
import random

st.set_page_config(page_title="Danish Politics Data", layout="wide", initial_sidebar_state="expanded")

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
</style>
""", unsafe_allow_html=True)

# ── helpers ───────────────────────────────────────────────────────────────────

EXCLUDE = lambda s: (
    s.str.startswith("Province") | s.str.startswith("Region") |
    (s == "All Denmark") | (s == "Christiansø")
)
ELECTION_TO_POP = {2007:"2008Q1", 2011:"2011Q1", 2015:"2015Q1", 2019:"2019Q1", 2022:"2022Q1"}

def build_finding(corr, metric_label, party, year, merged):
    abs_r  = abs(corr)
    ranked = merged.sort_values("metric")
    low10  = ranked.head(10)["share"].mean()
    high10 = ranked.tail(10)["share"].mean()
    p_short = party.split(". ", 1)[-1] if ". " in party else party
    m_short = metric_label.lower()

    note = f"Pearson r = {corr:.2f} · {len(merged)} municipalities · Danmarks Statistik (CC 4.0 BY)"

    if abs_r < 0.20:
        return (
            "weak",
            "NO PATTERN",
            f"No pattern found.",
            f"The data shows no consistent relationship between {m_short} and votes for {p_short} across {len(merged)} municipalities. "
            f"If you were looking for a story here — the data does not support it.",
            f"Write: <em>\"Data from {len(merged)} Danish municipalities shows no meaningful link between {m_short} and support for {p_short} in {year}.\"</em>",
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
    copy_sentence = (
        f"Write: <em>\"In the {year} election, municipalities with {direction} {m_short} "
        f"gave on average {gap:.1f} percentage points more to {p_short}. "
        f"The pattern holds across all {len(merged)} Danish municipalities. "
        f"(Source: Danmarks Statistik, CC 4.0 BY)\"</em>"
    )

    if abs_r >= 0.65:
        return "strong",   "STRONG PATTERN · r = {:.2f}".format(corr),   "Municipalities with {direction} {m} tend to vote significantly more for {p}.".format(direction=direction, m=m_short, p=p_short), concrete, copy_sentence, note
    elif abs_r >= 0.40:
        return "moderate", "MODERATE PATTERN · r = {:.2f}".format(corr), "Municipalities with {direction} {m} tend to vote more for {p}.".format(direction=direction, m=m_short, p=p_short),              concrete, copy_sentence, note
    else:
        return "weak",     "WEAK PATTERN · r = {:.2f}".format(corr),     "A weak tendency: municipalities with {direction} {m} lean slightly toward {p}.".format(direction=direction, m=m_short, p=p_short), concrete, copy_sentence, note

# ── data loaders ──────────────────────────────────────────────────────────────

@st.cache_data
def load_municipal():
    df = pd.read_csv("denmark/folketing/fvpandel_party_share.csv", sep=";", encoding="utf-8-sig")
    df.columns = ["party","municipality","year","share"]
    df["year"] = df["year"].astype(int)
    return df[(df["party"] != "Total") & (df["municipality"] != "All Denmark")]

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
    df = pd.read_csv("denmark/socioeconomic/folk1a_population_annual.csv", sep=";", encoding="utf-8-sig")
    df = df[~EXCLUDE(df["OMRÅDE"])].copy()
    df["year"] = df["TID"].str[:4].astype(int)
    return df[["OMRÅDE","TID","year","INDHOLD"]].rename(columns={"OMRÅDE":"municipality","INDHOLD":"population"})

@st.cache_data
def load_income():
    df = pd.read_csv("denmark/socioeconomic/indkp101_income_by_municipality.csv", sep=";", encoding="utf-8-sig")
    df = df[~EXCLUDE(df["OMRÅDE"])][["OMRÅDE","TID","INDHOLD"]].rename(
        columns={"OMRÅDE":"municipality","TID":"year","INDHOLD":"value"}).copy()
    df["year"] = df["year"].astype(int)
    return df

@st.cache_data
def load_social():
    df = pd.read_csv("denmark/socioeconomic/auk01_social_assistance.csv", sep=";", encoding="utf-8-sig")
    df = df[~EXCLUDE(df["OMRÅDE"]) & df["TID"].str.endswith("Q4")].copy()
    df["year"] = df["TID"].str[:4].astype(int)
    return df[["OMRÅDE","year","INDHOLD"]].rename(columns={"OMRÅDE":"municipality","INDHOLD":"value"})

@st.cache_data
def load_crime():
    df = pd.read_csv("denmark/socioeconomic/straf11_crime_by_municipality.csv", sep=";", encoding="utf-8-sig")
    df = df[~EXCLUDE(df["OMRÅDE"])].copy()
    df["year"] = df["TID"].str[:4].astype(int)
    return df.groupby(["OMRÅDE","year"])["INDHOLD"].sum().reset_index().rename(
        columns={"OMRÅDE":"municipality","INDHOLD":"value"})

@st.cache_data
def load_cars():
    df = pd.read_csv("denmark/socioeconomic/bil707_cars_by_municipality.csv", sep=";", encoding="utf-8-sig")
    df = df[~EXCLUDE(df["OMRÅDE"])][["OMRÅDE","TID","INDHOLD"]].rename(
        columns={"OMRÅDE":"municipality","TID":"year","INDHOLD":"value"}).copy()
    df["year"] = df["year"].astype(int)
    return df

@st.cache_data
def load_divorces():
    df = pd.read_csv("denmark/socioeconomic/ski125_divorces_by_municipality.csv", sep=";", encoding="utf-8-sig")
    df = df[~EXCLUDE(df["BOPAEGT1"])][["BOPAEGT1","TID","INDHOLD"]].rename(
        columns={"BOPAEGT1":"municipality","TID":"year","INDHOLD":"value"}).copy()
    df["year"] = df["year"].astype(int)
    return df

@st.cache_data
def load_education():
    df = pd.read_csv("denmark/socioeconomic/hfudd11_higher_edu_pct.csv")
    df["year"] = df["year"].astype(int)
    return df  # columns: municipality, year, value (% with higher education)

@st.cache_data
def load_age65():
    df = pd.read_csv("denmark/socioeconomic/folk1a_pct_65plus.csv")
    df["year"] = df["year"].astype(int)
    return df  # columns: municipality, year, value (% aged 65+)

@st.cache_data
def load_employment():
    df = pd.read_csv("denmark/socioeconomic/lbesk69_employees_by_municipality.csv", sep=";", encoding="utf-8-sig")
    df = df[~EXCLUDE(df["BOPKOM"])][["BOPKOM","TID","INDHOLD"]].rename(
        columns={"BOPKOM":"municipality","INDHOLD":"value"}).copy()
    # Keep only the election quarters (matching ELECTION_TO_POP)
    election_quarters = {"2008Q1": 2007, "2011Q1": 2011, "2015Q1": 2015, "2019Q1": 2019, "2022Q1": 2022}
    df = df[df["TID"].isin(election_quarters)].copy()
    df["year"] = df["TID"].map(election_quarters)
    return df[["municipality","year","value"]]

mun           = load_municipal()
nat           = load_national()
pop_df        = load_population()
income_df     = load_income()
social_df     = load_social()
crime_df      = load_crime()
cars_df       = load_cars()
divorce_df    = load_divorces()
employment_df = load_employment()
education_df  = load_education()
age65_df      = load_age65()

# ── sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="hr-wordmark">HEDEGREEN RESEARCH<span class="dot"> ●</span></div>', unsafe_allow_html=True)
    st.markdown("**Danish Politics Data**")
    st.markdown(
        "<p style='font-size:0.75rem;color:#6a6a7a;line-height:1.6;margin-top:0.3rem;'>"
        "Folketing elections 1953–2022, cross-referenced with income, crime, welfare, cars, and divorce data."
        "</p>", unsafe_allow_html=True
    )
    st.divider()
    page = st.radio("nav", ["Explore", "Compare municipalities", "By Municipality", "National trends", "About & sources"],
                    label_visibility="collapsed")
    st.divider()
    st.markdown(
        "<p style='font-size:0.65rem;color:#aaaabc;line-height:1.6;'>"
        "Data: Danmarks Statistik (CC 4.0 BY)<br>Straubinger/folketingsvalg<br><br>"
        "Built by Hedegreen Research"
        "</p>", unsafe_allow_html=True
    )

# ── Explore (guided discovery) ────────────────────────────────────────────────

METRIC_OPTIONS = [
    ("Education",   "Share with higher education (%)",           "education",   "Do more educated municipalities vote differently?"),
    ("Income",      "Avg. disposable income (DKK per person)",   "income",      "Do wealthier municipalities vote differently?"),
    ("Employment",  "Full-time employed per 1,000 residents",    "employment",  "Do areas with higher employment vote differently?"),
    ("Welfare",     "Social assistance recipients per 1,000",    "social",      "Do areas with more people on benefits vote differently?"),
    ("Crime",       "Reported crimes per 1,000 residents",       "crime",       "Is there a link between crime rates and voting patterns?"),
    ("Cars",        "Passenger cars per 1,000 residents",        "cars",        "Do car-heavy (rural) areas vote differently from urban ones?"),
    ("Divorces",    "Divorces per 1,000 residents",              "divorces",    "Does social stability correlate with voting behaviour?"),
    ("Age 65+",     "Share aged 65 or above (%)",                "age65",       "Do older municipalities vote differently?"),
]
ALL_METRIC_KEYS    = [m[0] for m in METRIC_OPTIONS]
ALL_PARTY_NAMES    = sorted(mun["party"].unique())
ALL_ELECTION_YEARS = sorted(mun["year"].unique())

def get_metric_series(metric_key, year, pop, _income, _social, _crime, _cars, _divorces, _employment, _education, _age65):
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
    elif metric_key == "employment":
        df = _employment[_employment["year"] == year][["municipality","value"]].merge(pop, on="municipality").copy()
        df["metric"] = (df["value"] / df["population"] * 1000).round(1)
        return df[["municipality","metric"]]
    elif metric_key == "social":
        df = _social[_social["year"] == year][["municipality","value"]].merge(pop, on="municipality").copy()
        df["metric"] = (df["value"] / df["population"] * 1000).round(2)
        return df[["municipality","metric"]]
    elif metric_key == "crime":
        df = _crime[_crime["year"] == year][["municipality","value"]].merge(pop, on="municipality").copy()
        df["metric"] = (df["value"] / df["population"] * 1000).round(1)
        return df[["municipality","metric"]]
    elif metric_key == "cars":
        df = _cars[_cars["year"] == year][["municipality","value"]].merge(pop, on="municipality").copy()
        df["metric"] = (df["value"] / df["population"] * 1000).round(1)
        return df[["municipality","metric"]]
    elif metric_key == "divorces":
        df = _divorces[_divorces["year"] == year][["municipality","value"]].merge(pop, on="municipality").copy()
        df["metric"] = (df["value"] / df["population"] * 1000).round(2)
        return df[["municipality","metric"]]
    return pd.DataFrame()

def corr_strength_label(r):
    a = abs(r)
    direction = "↑" if r > 0 else "↓"
    if a >= 0.65: return f"{direction} Strong ({r:.2f})"
    if a >= 0.40: return f"{direction} Moderate ({r:.2f})"
    if a >= 0.20: return f"{direction} Weak ({r:.2f})"
    return f"None ({r:.2f})"

@st.cache_data
def precompute_all_correlations(_mun, _pop_df, _income_df, _social_df, _crime_df, _cars_df, _divorce_df, _employment_df, _education_df, _age65_df):
    rows = []
    for year in sorted(_mun["year"].unique()):
        pop_key = ELECTION_TO_POP.get(year, f"{year}Q1")
        pop = _pop_df[_pop_df["TID"] == pop_key][["municipality","population"]]
        for party in sorted(_mun["party"].unique()):
            votes = _mun[(_mun["year"] == year) & (_mun["party"] == party)][["municipality","share"]]
            if votes.empty: continue
            for m_name, m_label, m_key, _ in METRIC_OPTIONS:
                ms = get_metric_series(m_key, year, pop, _income_df, _social_df, _crime_df, _cars_df, _divorce_df, _employment_df, _education_df, _age65_df)
                if ms.empty or "municipality" not in ms.columns: continue
                merged = votes.merge(ms, on="municipality", how="inner")
                if len(merged) < 10: continue
                r = float(merged["share"].corr(merged["metric"]))
                rows.append({"year": year, "party": party, "factor": m_name, "label": m_label, "r": round(r, 2)})
    return pd.DataFrame(rows)

all_corr_df = precompute_all_correlations(mun, pop_df, income_df, social_df, crime_df, cars_df, divorce_df, employment_df, education_df, age65_df)

if page == "Explore":

    # Initialise session state defaults (must happen before widgets render)
    if "cx_factors" not in st.session_state:
        st.session_state["cx_factors"] = ["Income"]
    if "cx_year" not in st.session_state:
        st.session_state["cx_year"] = ALL_ELECTION_YEARS[-1]
    if "cx_parties" not in st.session_state:
        st.session_state["cx_parties"] = ["A. The Social Democratic Party"]

    # Apply surprise values BEFORE widgets render (Streamlit requires this order)
    if st.session_state.get("_surprise_pending"):
        st.session_state["cx_year"]    = st.session_state.pop("_surprise_year")
        st.session_state["cx_factors"] = st.session_state.pop("_surprise_factors")
        st.session_state["cx_parties"] = st.session_state.pop("_surprise_parties")
        del st.session_state["_surprise_pending"]

    st.markdown("<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>Danish Politics Data</p>", unsafe_allow_html=True)
    st.title("Is there a pattern?")
    st.markdown(
        "<p style='font-size:0.95rem;color:#5a5a6a;margin-bottom:2rem;'>"
        "Pick one or more factors, one or more parties, and an election year. Then find out."
        "</p>", unsafe_allow_html=True
    )

    # ── Step 1: metrics (pills / toggles) ────────────────────────────────────
    st.markdown('<div class="step-label">Step 1 — What factors are you curious about?</div>', unsafe_allow_html=True)
    cx_metric_keys = st.pills(
        "factors", ALL_METRIC_KEYS, key="cx_factors",
        selection_mode="multi",
        label_visibility="collapsed"
    )

    # ── Step 2: year ──────────────────────────────────────────────────────────
    st.markdown('<div class="step-label" style="margin-top:1rem;">Step 2 — Which election year?</div>', unsafe_allow_html=True)
    cx_year = st.select_slider("year", options=ALL_ELECTION_YEARS, key="cx_year",
                               label_visibility="collapsed")

    # ── Step 3: parties (multi) ───────────────────────────────────────────────
    st.markdown('<div class="step-label" style="margin-top:1rem;">Step 3 — Which parties? (pick one or more, or all)</div>', unsafe_allow_html=True)
    all_toggle = st.checkbox("All parties")
    if all_toggle:
        cx_parties = ALL_PARTY_NAMES
    else:
        cx_parties = st.multiselect("parties", ALL_PARTY_NAMES, key="cx_parties",
                                    label_visibility="collapsed")

    # ── Step 4: highlight a municipality (optional) ───────────────────────────
    st.markdown('<div class="step-label" style="margin-top:1rem;">Step 4 — Highlight a specific municipality? (optional)</div>', unsafe_allow_html=True)
    all_munis_explore = ["— none —"] + sorted(mun["municipality"].unique())
    cx_highlight = st.selectbox("highlight", all_munis_explore, key="cx_highlight",
                                label_visibility="collapsed")
    highlight_muni = None if cx_highlight == "— none —" else cx_highlight

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    col_main, col_surprise = st.columns([3, 1])
    with col_main:
        if st.button("Show me what the data reveals →", type="primary", use_container_width=True):
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
            st.warning("Select at least one factor and one party.")
            st.stop()

        pop_key = ELECTION_TO_POP.get(s_year, f"{s_year}Q1")
        pop     = pop_df[pop_df["TID"] == pop_key][["municipality","population"]]

        # Build correlation matrix: rows=parties, cols=metrics
        results = []
        for party in s_parties:
            votes = mun[(mun["year"] == s_year) & (mun["party"] == party)][["municipality","share"]]
            for mk in s_metric_keys:
                m_info  = next(m for m in METRIC_OPTIONS if m[0] == mk)
                m_label = m_info[1]
                ms = get_metric_series(m_info[2], s_year, pop, income_df, social_df, crime_df, cars_df, divorce_df, employment_df, education_df, age65_df)
                if ms.empty or "municipality" not in ms.columns:
                    continue
                merged  = votes.merge(ms, on="municipality", how="inner")
                if merged.empty: continue
                r = merged["share"].corr(merged["metric"])
                results.append({"party": party, "factor": mk, "label": m_label, "r": round(r, 2),
                                 "merged": merged, "strength": corr_strength_label(r)})

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
            return (
                f'<div class="finding {strength_cls}">'
                f'<div class="strength-tag">{strength_tag}</div>'
                f'{ctx}'
                f'<div class="headline">{headline}</div>'
                f'<div class="body">{concrete}</div>'
                f'<div class="copy-label">Write this as:</div>'
                f'<div class="copy-box">{copy_sentence}</div>'
                f'<div class="footnote">{note}</div>'
                f'</div>'
            )

        def how_to_read():
            with st.expander("How to read this result"):
                st.markdown("""
**STRONG PATTERN (r ≥ 0.65)** — Write: *"Data from 98 municipalities shows a clear link."*
**MODERATE PATTERN (r 0.40–0.65)** — Write: *"There is a consistent tendency."*
**WEAK PATTERN (r 0.20–0.40)** — Mention it, but add: *"the link is not strong."*
**NO PATTERN (r below 0.20)** — Do not write a pattern claim. The data does not support it.

Positive r = both go up together. Negative r = they go in opposite directions.

*Correlation ≠ cause. The data shows a pattern — not why it exists.*
                """)

        # ── Case A: 1 party, 1 metric → full finding + scatter ───────────────
        if len(s_parties) == 1 and len(s_metric_keys) == 1:
            row = results[0]
            strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(
                row["r"], row["label"], row["party"], s_year, row["merged"])
            st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note),
                        unsafe_allow_html=True)
            how_to_read()

            # Always show the extremes — the concrete municipalities at both ends
            ranked_data = row["merged"].sort_values("metric").rename(columns={
                "municipality": "Municipality",
                "share": "Vote share (%)",
                "metric": row["label"]
            })
            col_lo, col_hi = st.columns(2)
            with col_lo:
                st.markdown(
                    f"<p style='font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;"
                    f"color:#aaaabc;margin-bottom:0.3rem;'>Lowest {row['label'].split()[0]} →</p>",
                    unsafe_allow_html=True
                )
                st.dataframe(ranked_data.head(10), use_container_width=True, hide_index=True)
            with col_hi:
                st.markdown(
                    f"<p style='font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;"
                    f"color:#aaaabc;margin-bottom:0.3rem;'>Highest {row['label'].split()[0]} →</p>",
                    unsafe_allow_html=True
                )
                st.dataframe(ranked_data.tail(10).sort_values(row["label"], ascending=False),
                             use_container_width=True, hide_index=True)

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
                        f'Rank {h_rank} of {len(sorted_all)} municipalities by {row["label"].split()[0].lower()}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.caption(f"No data for {highlight_muni} in {s_year}.")

            st.markdown("<p style='font-size:0.75rem;color:#aaaabc;margin-top:1rem;'>Each dot = one municipality. Named dots = extremes.</p>", unsafe_allow_html=True)
            scatter_df = row["merged"].rename(columns={"share": "Vote share (%)", "metric": row["label"]}).copy()
            # Label top 5 + bottom 5 by metric, plus the highlighted municipality
            sorted_sc = scatter_df.sort_values(row["label"])
            label_munis = set(sorted_sc.head(5)["municipality"]) | set(sorted_sc.tail(5)["municipality"])
            if highlight_muni:
                label_munis.add(highlight_muni)
            scatter_df["label"] = scatter_df["municipality"].where(scatter_df["municipality"].isin(label_munis), "")
            scatter_df["highlighted"] = scatter_df["municipality"] == (highlight_muni or "")
            base = alt.Chart(scatter_df).encode(
                x=alt.X(row["label"], title=row["label"]),
                y=alt.Y("Vote share (%)", title="Vote share (%)"),
                tooltip=["municipality", row["label"], "Vote share (%)"]
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
                st.dataframe(ranked_data.sort_values("Vote share (%)", ascending=False),
                             use_container_width=True, hide_index=True)

        # ── Case B: multiple metrics, 1 party → "what predicts this party?" ──
        elif len(s_parties) == 1 and len(s_metric_keys) > 1:
            party = s_parties[0]
            ranked = sorted(results, key=lambda x: abs(x["r"]), reverse=True)
            # Bar chart first — most informative view
            summary = pd.DataFrame([{"Factor": r["factor"], "r": r["r"], "Strength": r["strength"]} for r in ranked])
            st.markdown("<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.3rem;'>All factors ranked. Positive = more votes where factor is higher. Negative = opposite.</p>", unsafe_allow_html=True)
            st.bar_chart(summary.set_index("Factor")["r"])
            # Show a finding box for every factor with |r| ≥ 0.20
            meaningful = [r for r in ranked if abs(r["r"]) >= 0.20]
            no_pattern = [r for r in ranked if abs(r["r"]) < 0.20]
            if not meaningful:
                meaningful = [ranked[0]]  # always show at least the top one
            for i, row in enumerate(meaningful):
                label = f"{'Strongest' if i == 0 else 'Also'} factor: {row['factor']}"
                strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(
                    row["r"], row["label"], party, s_year, row["merged"])
                st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note,
                                         context_label=label),
                            unsafe_allow_html=True)
            if no_pattern:
                no_pattern_names = ", ".join(r["factor"] for r in no_pattern)
                st.markdown(
                    f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.5rem;'>"
                    f"No pattern found for: {no_pattern_names} (r below 0.20).</p>",
                    unsafe_allow_html=True
                )
            how_to_read()
            with st.expander("See full ranking table"):
                st.dataframe(summary, use_container_width=True, hide_index=True)

        # ── Case C: multiple parties, 1 metric → "which parties link to X?" ──
        elif len(s_parties) > 1 and len(s_metric_keys) == 1:
            ranked = sorted(results, key=lambda x: abs(x["r"]), reverse=True)
            # Bar chart first
            summary = pd.DataFrame([{"Party": r["party"].split(". ",1)[-1], "r": r["r"], "Strength": r["strength"]} for r in ranked])
            st.markdown("<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.3rem;'>Positive = more votes where factor is higher. Negative = more votes where factor is lower.</p>", unsafe_allow_html=True)
            st.bar_chart(summary.set_index("Party")["r"])
            # Finding box for every party with |r| ≥ 0.20
            meaningful = [r for r in ranked if abs(r["r"]) >= 0.20]
            no_pattern = [r for r in ranked if abs(r["r"]) < 0.20]
            if not meaningful:
                meaningful = [ranked[0]]
            for i, row in enumerate(meaningful):
                label = f"{'Strongest' if i == 0 else 'Also'} link: {row['party'].split('. ',1)[-1]}"
                strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(
                    row["r"], row["label"], row["party"], s_year, row["merged"])
                st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note,
                                         context_label=label),
                            unsafe_allow_html=True)
            if no_pattern:
                no_pattern_names = ", ".join(r["party"].split(". ",1)[-1] for r in no_pattern)
                st.markdown(
                    f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.5rem;'>"
                    f"No pattern found for: {no_pattern_names} (r below 0.20).</p>",
                    unsafe_allow_html=True
                )
            how_to_read()
            with st.expander("See full ranking table"):
                st.dataframe(summary, use_container_width=True, hide_index=True)

        # ── Case D: multiple parties + multiple metrics → matrix ──────────────
        else:
            top = max(results, key=lambda x: abs(x["r"]))
            strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(
                top["r"], top["label"], top["party"], s_year, top["merged"])
            st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note,
                                     context_label=f"Strongest signal: {top['party'].split('. ',1)[-1]} × {top['factor']}"),
                        unsafe_allow_html=True)
            how_to_read()
            with st.expander("See full correlation table"):
                matrix_data = {}
                for r in results:
                    p_short = r["party"].split(". ",1)[-1]
                    if p_short not in matrix_data:
                        matrix_data[p_short] = {}
                    matrix_data[p_short][r["factor"]] = r["r"]
                matrix_df = pd.DataFrame(matrix_data).T.round(2)
                st.dataframe(matrix_df, use_container_width=True)

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
    gap_df.columns = [p.split(". ", 1)[-1] if ". " in p else p for p in gap_df.columns]

    st.markdown(
        f"<p style='font-size:0.82rem;color:#6a6a7a;margin-bottom:0.5rem;'>"
        f"Percentage point gap in vote share: <strong>{mun_a}</strong> minus <strong>{mun_b}</strong>. "
        f"Positive bar = {mun_a} votes more for that party. Negative = {mun_b} does.</p>",
        unsafe_allow_html=True
    )
    st.bar_chart(gap_df)

    # Biggest single gap
    max_gap_party = gap_df.abs().mean().idxmax()
    max_gap_val = gap_df[max_gap_party].mean().round(1)
    direction = mun_a if max_gap_val > 0 else mun_b
    st.markdown(
        f'<div class="finding moderate">'
        f'<div class="headline">Biggest difference: {max_gap_party}</div>'
        f'<div class="body">On average across all elections, <strong>{direction}</strong> votes '
        f'<strong>{abs(max_gap_val):.1f} percentage points more</strong> for {max_gap_party} than the other municipality.</div>'
        f'<div class="footnote">Based on 2007–2022 elections · Danmarks Statistik (CC 4.0 BY)</div>'
        f'</div>', unsafe_allow_html=True
    )

    with st.expander("See full vote history for both municipalities"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{mun_a}**")
            st.dataframe(votes_a[top_parties].round(1), use_container_width=True)
        with col2:
            st.markdown(f"**{mun_b}**")
            st.dataframe(votes_b[top_parties].round(1), use_container_width=True)

    # ── Socioeconomic profile ─────────────────────────────────────────────────
    st.markdown("## Socioeconomic profile")
    st.markdown(
        "<p style='font-size:0.82rem;color:#6a6a7a;margin-bottom:0.8rem;'>"
        "Most recent available data for each metric. Welfare, crime, cars and divorces shown per 1,000 residents."
        "</p>", unsafe_allow_html=True
    )

    def latest_val(df, municipality, year_col="year", val_col="value"):
        sub = df[df["municipality"] == municipality]
        if sub.empty: return None, None
        yr = sub[year_col].max()
        v = sub[sub[year_col] == yr][val_col]
        return (float(v.values[0]) if len(v) > 0 else None), int(yr)

    def pop_for(municipality):
        sub = pop_df[pop_df["municipality"] == municipality].sort_values("TID", ascending=False)
        if sub.empty: return None
        return float(sub["population"].values[0])

    pop_a = pop_for(mun_a)
    pop_b = pop_for(mun_b)

    profile_rows = []

    edu_a, yr = latest_val(education_df, mun_a)
    edu_b, _  = latest_val(education_df, mun_b)
    if edu_a and edu_b:
        profile_rows.append({"Metric": "Higher education (%)", mun_a: f"{edu_a:.1f}%", mun_b: f"{edu_b:.1f}%", "Year": yr})

    inc_a, yr = latest_val(income_df, mun_a)
    inc_b, _  = latest_val(income_df, mun_b)
    if inc_a and inc_b:
        profile_rows.append({"Metric": "Avg. disposable income (DKK)", mun_a: f"{inc_a:,.0f}", mun_b: f"{inc_b:,.0f}", "Year": yr})

    emp_a, yr = latest_val(employment_df, mun_a)
    emp_b, _  = latest_val(employment_df, mun_b)
    if emp_a and emp_b and pop_a and pop_b:
        profile_rows.append({"Metric": "Full-time employed per 1,000", mun_a: f"{emp_a/pop_a*1000:.1f}", mun_b: f"{emp_b/pop_b*1000:.1f}", "Year": yr})

    soc_a, yr = latest_val(social_df, mun_a)
    soc_b, _  = latest_val(social_df, mun_b)
    if soc_a and soc_b and pop_a and pop_b:
        profile_rows.append({"Metric": "Welfare recipients per 1,000", mun_a: f"{soc_a/pop_a*1000:.1f}", mun_b: f"{soc_b/pop_b*1000:.1f}", "Year": yr})

    cr_a, yr = latest_val(crime_df, mun_a)
    cr_b, _  = latest_val(crime_df, mun_b)
    if cr_a and cr_b and pop_a and pop_b:
        profile_rows.append({"Metric": "Reported crimes per 1,000", mun_a: f"{cr_a/pop_a*1000:.1f}", mun_b: f"{cr_b/pop_b*1000:.1f}", "Year": yr})

    car_a, yr = latest_val(cars_df, mun_a)
    car_b, _  = latest_val(cars_df, mun_b)
    if car_a and car_b and pop_a and pop_b:
        profile_rows.append({"Metric": "Passenger cars per 1,000", mun_a: f"{car_a/pop_a*1000:.1f}", mun_b: f"{car_b/pop_b*1000:.1f}", "Year": yr})

    div_a, yr = latest_val(divorce_df, mun_a)
    div_b, _  = latest_val(divorce_df, mun_b)
    if div_a and div_b and pop_a and pop_b:
        profile_rows.append({"Metric": "Divorces per 1,000", mun_a: f"{div_a/pop_a*1000:.1f}", mun_b: f"{div_b/pop_b*1000:.1f}", "Year": yr})

    age_a, yr = latest_val(age65_df, mun_a)
    age_b, _  = latest_val(age65_df, mun_b)
    if age_a and age_b:
        profile_rows.append({"Metric": "Aged 65+ (%)", mun_a: f"{age_a:.1f}%", mun_b: f"{age_b:.1f}%", "Year": yr})

    if profile_rows:
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
        party = st.selectbox("Party", sorted(mun["party"].unique()))

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
    st.bar_chart(filtered.set_index("municipality")["share"])
    st.dataframe(
        filtered[["municipality","share"]].rename(columns={"share":"vote share (%)"}),
        use_container_width=True, hide_index=True
    )

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
                              default=[p for p in ["S","V","DF","EL","M"] if p in parties_nat])
    if selected:
        pivot = nat[nat["party"].isin(selected)].pivot_table(index="year", columns="party", values="share")
        st.line_chart(pivot)
        st.dataframe(pivot.round(1), use_container_width=True)

# ── About & sources ───────────────────────────────────────────────────────────

elif page == "About & sources":
    st.subheader("About")
    st.markdown("""
Danish election results 1953–2022, cross-referenced with seven datasets from Danmarks Statistik.
Built for journalists and researchers. No login required. All data is public and open-licensed (CC 4.0 BY).

Built by [Hedegreen Research](https://hedegreenresearch.com).
    """)
    st.subheader("Data sources")
    st.markdown("""
<div class="source-item"><strong>FVPANDEL</strong> — Party vote share per municipality, 2007–2022. Danmarks Statistik</div>
<div class="source-item"><strong>Straubinger/folketingsvalg</strong> — National vote counts, 1953–2022. GitHub</div>
<div class="source-item"><strong>INDKP101</strong> — Avg. disposable income per municipality, 1987–2024. Danmarks Statistik</div>
<div class="source-item"><strong>AUK01</strong> — Social assistance recipients per municipality, 2007–present. Danmarks Statistik</div>
<div class="source-item"><strong>STRAF11</strong> — Reported crimes per municipality, 2007–present. Danmarks Statistik</div>
<div class="source-item"><strong>BIL707</strong> — Passenger cars per municipality, 2007–present. Danmarks Statistik</div>
<div class="source-item"><strong>SKI125</strong> — Divorces per municipality, 2007–present. Danmarks Statistik</div>
<div class="source-item"><strong>FOLK1A</strong> — Population per municipality (used for per-capita calculations). Danmarks Statistik</div>
    """, unsafe_allow_html=True)
