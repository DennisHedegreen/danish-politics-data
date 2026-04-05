from __future__ import annotations

import random
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from core.correlation import compute_correlation_result, corr_strength_label
from core.presentation import (
    METRIC_PHRASES,
    METRIC_SHORT_LABELS,
    PARTY_NAME_MODES,
    format_party_code,
    format_party_name,
    render_bar_chart,
    render_compact_dataframe,
    render_country_sidebar_footer,
    render_national_trend_chart,
    render_profile_cards,
)


EXCLUDE = lambda s: (
    s.str.startswith("Province") | s.str.startswith("Region") |
    (s == "All Denmark") | (s == "Christiansø")
)
FACTOR_DIR = Path("denmark/factors")

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


def is_available(country_config, runtime_context):
    return country_config.municipal_vote_path.exists() and country_config.factor_dir.exists()


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


def build_finding(corr, factor_name, metric_label, party, year, merged, party_name_mode, country_config, known_parties):
    from core.correlation import is_valid_correlation

    if not is_valid_correlation(corr):
        return "weak", "RESULT UNAVAILABLE", "Result unavailable", \
            "The correlation value for this selection could not be computed reliably. No pattern claim should be made for this result.", \
            None, \
            f"Correlation unavailable · {len(merged)} municipalities · {municipal_vote_source_label(year)}"

    abs_r = abs(corr)
    ranked = merged.sort_values("metric")
    low10 = ranked.head(10)["share"].mean()
    high10 = ranked.tail(10)["share"].mean()
    p_short = format_party_name(party, metadata=country_config.party_metadata, mode=party_name_mode, prose=True)
    m_short = METRIC_PHRASES.get(factor_name, metric_label.lower())

    note = f"Pearson r = {corr:.2f} · {len(merged)} municipalities · {municipal_vote_source_label(year)}"

    if abs_r < 0.30:
        return (
            "weak",
            "NO PATTERN",
            "No consistent pattern found.",
            f"The data shows no consistent relationship between {m_short} and votes for {p_short} across {len(merged)} municipalities. "
            f"If you were looking for a story here — the data does not support it.",
            None,
            note,
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
        return "strong", f"STRONG PATTERN · r = {corr:.2f}", f"Municipalities with {direction} {m_short} tend to vote more for {p_short}.", concrete, copy_sentence, note
    if abs_r >= 0.50:
        return "moderate", f"MODERATE PATTERN · r = {corr:.2f}", f"Municipalities with {direction} {m_short} tend to vote more for {p_short}.", concrete, copy_sentence, note
    return "weak", f"WEAK PATTERN · r = {corr:.2f}", f"Municipalities with {direction} {m_short} show a weak tendency toward {p_short}.", concrete, copy_sentence, note


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
        frame.columns = ["party", "municipality", "year", "share"]
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
    df = df.melt(id_vars=["year", "date", "total_valid"], value_vars=cols, var_name="party", value_name="votes")
    df["party"] = df["party"].str.replace("party_", "").str.upper()
    df = df.dropna(subset=["votes"])
    df["share"] = (df["votes"] / df["total_valid"] * 100).round(1)
    return df


@st.cache_data
def load_population():
    path = FACTOR_DIR / "population.csv"
    if path.exists():
        df = pd.read_csv(path)
        df["year"] = df["year"].astype(int)
        return exclude_public_special_cases(df.rename(columns={"value": "population"}))
    df = pd.read_csv("denmark/socioeconomic/folk1a_population_annual.csv", sep=";", encoding="utf-8-sig")
    df = df[~EXCLUDE(df["OMRÅDE"])].copy()
    df["year"] = df["TID"].str[:4].astype(int)
    return df[["OMRÅDE", "TID", "year", "INDHOLD"]].rename(columns={"OMRÅDE": "municipality", "INDHOLD": "population"})


@st.cache_data
def load_factor_file(filename):
    path = FACTOR_DIR / filename
    if not path.exists():
        return pd.DataFrame(columns=["municipality", "year", "value"])
    df = pd.read_csv(path)
    df["year"] = df["year"].astype(int)
    return exclude_public_special_cases(df)


def load_bundle(country_config, runtime_context):
    return {
        "mun": load_municipal(),
        "nat": load_national(),
        "pop_df": load_population(),
        "income_df": load_factor_file("income.csv"),
        "social_df": load_factor_file("welfare_per_1000.csv"),
        "crime_df": load_factor_file("crime_per_1000.csv"),
        "cars_df": load_factor_file("cars_per_1000.csv"),
        "divorce_df": load_factor_file("divorces_per_1000.csv"),
        "commute_df": load_factor_file("commute_distance_km.csv"),
        "education_df": load_factor_file("education.csv"),
        "age65_df": load_factor_file("age65_pct.csv"),
        "employment_df": load_factor_file("employment_per_1000.csv"),
        "turnout_df": load_factor_file("turnout_pct.csv"),
        "immigration_df": load_factor_file("immigration_share_pct.csv"),
        "density_df": load_factor_file("population_density.csv"),
        "unemployment_df": load_factor_file("unemployment_pct.csv"),
        "owner_occupied_df": load_factor_file("owner_occupied_dwelling_share_pct.csv"),
        "detached_houses_df": load_factor_file("detached_house_dwelling_share_pct.csv"),
        "one_person_households_df": load_factor_file("one_person_household_share_pct.csv"),
    }


def get_metric_series(metric_key, year, _population, _income, _social, _crime, _cars, _divorces, _commute, _employment, _education, _age65, _turnout, _immigration, _density, _unemployment, _owner_occupied, _detached_houses, _one_person_households):
    mapping = {
        "population": (_population, "population"),
        "education": (_education, "value"),
        "age65": (_age65, "value"),
        "income": (_income, "value"),
        "commute": (_commute, "value"),
        "employment": (_employment, "value"),
        "social": (_social, "value"),
        "crime": (_crime, "value"),
        "cars": (_cars, "value"),
        "divorces": (_divorces, "value"),
        "turnout": (_turnout, "value"),
        "immigration": (_immigration, "value"),
        "density": (_density, "value"),
        "unemployment": (_unemployment, "value"),
        "owner_occupied": (_owner_occupied, "value"),
        "detached_houses": (_detached_houses, "value"),
        "one_person_households": (_one_person_households, "value"),
    }
    frame, value_col = mapping.get(metric_key, (pd.DataFrame(), "value"))
    if frame.empty:
        return pd.DataFrame()
    df = frame[frame["year"] == year][["municipality", value_col]].copy()
    df["metric"] = df[value_col]
    return df[["municipality", "metric"]]


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
def precompute_all_correlations():
    _mun = load_municipal()
    _pop_df = load_population()
    _income_df = load_factor_file("income.csv")
    _social_df = load_factor_file("welfare_per_1000.csv")
    _crime_df = load_factor_file("crime_per_1000.csv")
    _cars_df = load_factor_file("cars_per_1000.csv")
    _divorce_df = load_factor_file("divorces_per_1000.csv")
    _commute_df = load_factor_file("commute_distance_km.csv")
    _employment_df = load_factor_file("employment_per_1000.csv")
    _education_df = load_factor_file("education.csv")
    _age65_df = load_factor_file("age65_pct.csv")
    _turnout_df = load_factor_file("turnout_pct.csv")
    _immigration_df = load_factor_file("immigration_share_pct.csv")
    _density_df = load_factor_file("population_density.csv")
    _unemployment_df = load_factor_file("unemployment_pct.csv")
    _owner_occupied_df = load_factor_file("owner_occupied_dwelling_share_pct.csv")
    _detached_houses_df = load_factor_file("detached_house_dwelling_share_pct.csv")
    _one_person_households_df = load_factor_file("one_person_household_share_pct.csv")
    rows = []
    for year in sorted(_mun["year"].unique()):
        for party in sorted(_mun["party"].unique()):
            votes = _mun[(_mun["year"] == year) & (_mun["party"] == party)][["municipality", "share"]]
            if votes.empty:
                continue
            for m_name, m_label, m_key, _ in METRIC_OPTIONS:
                ms = get_metric_series(m_key, year, _pop_df, _income_df, _social_df, _crime_df, _cars_df, _divorce_df, _commute_df, _employment_df, _education_df, _age65_df, _turnout_df, _immigration_df, _density_df, _unemployment_df, _owner_occupied_df, _detached_houses_df, _one_person_households_df)
                if ms.empty or "municipality" not in ms.columns:
                    continue
                merged = votes.merge(ms, on="municipality", how="inner")
                computed = compute_correlation_result(merged, factor=m_name, party=party, year=year, mode="precompute")
                if not computed["valid"]:
                    continue
                rows.append({"year": year, "party": party, "factor": m_name, "label": m_label, "r": computed["r"]})
    return pd.DataFrame(rows)


def top_national_parties(national_df, top_n=5):
    if national_df.empty:
        return []
    latest_year = int(national_df["year"].max())
    latest = national_df[national_df["year"] == latest_year].copy()
    latest["share"] = pd.to_numeric(latest["share"], errors="coerce")
    latest = latest.dropna(subset=["share"]).sort_values("share", ascending=False)
    return latest["party"].head(top_n).tolist()


def ordered_national_parties(national_df):
    if national_df.empty:
        return []
    latest_year = int(national_df["year"].max())
    latest = national_df[national_df["year"] == latest_year].copy()
    latest["share"] = pd.to_numeric(latest["share"], errors="coerce")
    latest = latest.dropna(subset=["share"]).sort_values("share", ascending=False)
    ordered = latest["party"].tolist()
    remainder = sorted([party for party in national_df["party"].dropna().unique().tolist() if party not in ordered])
    return ordered + remainder


def render(country_config, selected_country_label, runtime_context):
    bundle = load_bundle(country_config, runtime_context)
    mun = bundle["mun"]
    nat = bundle["nat"]
    pop_df = bundle["pop_df"]
    income_df = bundle["income_df"]
    social_df = bundle["social_df"]
    crime_df = bundle["crime_df"]
    cars_df = bundle["cars_df"]
    divorce_df = bundle["divorce_df"]
    commute_df = bundle["commute_df"]
    education_df = bundle["education_df"]
    age65_df = bundle["age65_df"]
    employment_df = bundle["employment_df"]
    turnout_df = bundle["turnout_df"]
    immigration_df = bundle["immigration_df"]
    density_df = bundle["density_df"]
    unemployment_df = bundle["unemployment_df"]
    owner_occupied_df = bundle["owner_occupied_df"]
    detached_houses_df = bundle["detached_houses_df"]
    one_person_households_df = bundle["one_person_households_df"]

    all_party_names = sorted(mun["party"].unique())
    all_election_years = sorted(mun["year"].unique())
    default_explore_year = 2022 if 2022 in all_election_years else all_election_years[-1]
    municipal_election_range_label = f"{all_election_years[0]}–{all_election_years[-1]}"

    with st.sidebar:
        st.markdown('<div class="hr-wordmark">HEDEGREEN RESEARCH<span class="dot"> ●</span></div>', unsafe_allow_html=True)
        st.markdown("**Danish Politics Data**")
        st.markdown(
            "<p style='font-size:0.75rem;color:#6a6a7a;line-height:1.6;margin-top:0.3rem;'>"
            "National vote trends 1953–2022. Municipality vote share 2007–2026, with the 2026 layer bridged from the official VALG export."
            "</p>",
            unsafe_allow_html=True
        )
        st.divider()
        party_name_mode = st.selectbox("Party names", PARTY_NAME_MODES, index=1)
        st.divider()
        page = st.radio("nav", ["Explore", "Compare municipalities", "By Municipality", "National trends", "About & sources"],
                        label_visibility="collapsed")
        st.divider()
        render_country_sidebar_footer(country_config)

    if page == "Explore":
        if "cx_factors" not in st.session_state:
            st.session_state["cx_factors"] = ["Income"]
        if "cx_factors_widget" not in st.session_state:
            st.session_state["cx_factors_widget"] = st.session_state.get("cx_factors", ["Income"])
        if "cx_year" not in st.session_state:
            st.session_state["cx_year"] = default_explore_year
        if "cx_all_parties" not in st.session_state:
            st.session_state["cx_all_parties"] = True
        if "cx_parties" not in st.session_state:
            st.session_state["cx_parties"] = []
        if "cx_parties_widget" not in st.session_state:
            st.session_state["cx_parties_widget"] = st.session_state.get("cx_parties", [])
        if "cx_year_seen" not in st.session_state:
            st.session_state["cx_year_seen"] = st.session_state["cx_year"]
        if "cx_parties_seen_for_year" not in st.session_state:
            st.session_state["cx_parties_seen_for_year"] = []

        def _available_metric_keys(selected_year):
            return available_metric_keys_for_year(
                selected_year, pop_df, income_df, social_df, crime_df, cars_df, divorce_df, commute_df, employment_df, education_df, age65_df, turnout_df, immigration_df, density_df, unemployment_df, owner_occupied_df, detached_houses_df, one_person_households_df,
            )

        def _available_parties(selected_year):
            return available_parties_for_year(selected_year, mun)

        def _normalize_factor_widget_state(selected_year):
            available = _available_metric_keys(selected_year)
            selected = [m for m in st.session_state.get("cx_factors_widget", []) if m in available]
            if available and not selected:
                selected = [available[0]]
            st.session_state["cx_factors_widget"] = selected
            st.session_state["cx_factors"] = selected
            return available

        def _normalize_party_widget_state(selected_year):
            parties = _available_parties(selected_year)
            previous_year = st.session_state.get("cx_year_seen")
            previous_parties = st.session_state.get("cx_parties_seen_for_year", [])
            year_changed = previous_year != selected_year
            selected = [p for p in st.session_state.get("cx_parties_widget", []) if p in parties]
            if st.session_state.get("cx_all_parties"):
                selected = parties
            elif year_changed:
                newly_available = [p for p in parties if p not in previous_parties]
                if newly_available:
                    selected = [
                        party for party in parties
                        if party in set(selected) | set(newly_available)
                    ]
            st.session_state["cx_parties_widget"] = selected
            st.session_state["cx_parties"] = selected
            st.session_state["cx_year_seen"] = selected_year
            st.session_state["cx_parties_seen_for_year"] = parties
            return parties

        def _on_explore_year_change():
            selected_year = st.session_state["cx_year"]
            _normalize_factor_widget_state(selected_year)
            _normalize_party_widget_state(selected_year)

        def _on_explore_all_parties_change():
            _normalize_party_widget_state(st.session_state["cx_year"])

        if st.session_state.get("_surprise_pending"):
            st.session_state["cx_year"] = st.session_state.pop("_surprise_year")
            st.session_state["cx_factors_widget"] = st.session_state.pop("_surprise_factors")
            st.session_state["cx_parties_widget"] = st.session_state.pop("_surprise_parties")
            st.session_state["cx_factors"] = st.session_state["cx_factors_widget"]
            st.session_state["cx_parties"] = st.session_state["cx_parties_widget"]
            st.session_state["cx_all_parties"] = False
            del st.session_state["_surprise_pending"]

        st.markdown("<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>Danish Politics Data</p>", unsafe_allow_html=True)
        st.title("Is there a pattern?")
        st.markdown(
            "<p style='font-size:0.95rem;color:#5a5a6a;margin-bottom:2rem;'>"
            "Pick one or more factors, one or more parties, and an election year. Then find out."
            "</p>", unsafe_allow_html=True
        )

        st.markdown('<div class="step-label">Step 1 — Which election year?</div>', unsafe_allow_html=True)
        cx_year = st.select_slider("year", options=all_election_years, key="cx_year", label_visibility="collapsed", on_change=_on_explore_year_change)

        available_metric_keys = _available_metric_keys(cx_year)
        parties_for_year = _available_parties(cx_year)
        if st.session_state.get("cx_factors_widget") is None:
            st.session_state["cx_factors_widget"] = []
        if st.session_state.get("cx_parties_widget") is None:
            st.session_state["cx_parties_widget"] = []

        st.markdown('<div class="step-label" style="margin-top:1rem;">Step 2 — What factors are available for that year?</div>', unsafe_allow_html=True)
        if available_metric_keys:
            if not st.session_state.get("cx_factors_widget"):
                st.session_state["cx_factors_widget"] = [available_metric_keys[0]]
            cx_metric_keys = st.multiselect(
                "Factors",
                available_metric_keys,
                key="cx_factors_widget",
                label_visibility="collapsed",
                placeholder="Select one or more factors",
            )
        else:
            cx_metric_keys = []
            st.markdown("<p style='font-size:0.74rem;color:#8888a0;margin-bottom:0;'>No usable municipality factor layer is available for that election year yet.</p>", unsafe_allow_html=True)
        st.session_state["cx_factors"] = cx_metric_keys

        st.markdown('<div class="step-label" style="margin-top:1rem;">Step 3 — Pick a party</div>', unsafe_allow_html=True)
        all_toggle = st.checkbox("All parties", key="cx_all_parties", on_change=_on_explore_all_parties_change)
        if all_toggle:
            cx_parties = parties_for_year
        else:
            cx_parties = st.multiselect(
                "Parties",
                parties_for_year,
                key="cx_parties_widget",
                format_func=lambda p: format_party_name(p, metadata=country_config.party_metadata, mode=party_name_mode, compact=True, include_code=True),
                label_visibility="collapsed",
                placeholder="Select one or more parties",
            )
            if not cx_parties:
                st.markdown("<p style='font-size:0.74rem;color:#8888a0;margin-top:0.45rem;margin-bottom:0;'>No party is currently selected. Municipality-level pattern analysis requires at least one party selection.</p>", unsafe_allow_html=True)
        st.session_state["cx_parties"] = cx_parties
        st.session_state["cx_year_seen"] = cx_year
        st.session_state["cx_parties_seen_for_year"] = parties_for_year

        st.markdown('<div class="step-label" style="margin-top:1rem;">Step 4 — Highlight a specific municipality? (optional)</div>', unsafe_allow_html=True)
        all_munis_explore = ["— none —"] + sorted(mun["municipality"].unique())
        cx_highlight = st.selectbox("highlight", all_munis_explore, key="cx_highlight", label_visibility="collapsed")
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
                all_corr_df = precompute_all_correlations()
                interesting = all_corr_df[all_corr_df["r"].abs() >= 0.40]
                if not interesting.empty:
                    mode = random.choice(["single", "multi_factor", "multi_party"])
                    anchor = interesting.sample(1).iloc[0]
                    s_year = int(anchor["year"])
                    if mode == "single":
                        factors = [anchor["factor"]]
                        parties = [anchor["party"]]
                    elif mode == "multi_factor":
                        same = interesting[(interesting["party"] == anchor["party"]) & (interesting["year"] == s_year)]
                        same = same.reindex(same["r"].abs().sort_values(ascending=False).index)
                        factors = same["factor"].tolist()[:3] if len(same) >= 2 else [anchor["factor"]]
                        parties = [anchor["party"]]
                    else:
                        same = interesting[(interesting["factor"] == anchor["factor"]) & (interesting["year"] == s_year)]
                        same = same.reindex(same["r"].abs().sort_values(ascending=False).index)
                        factors = [anchor["factor"]]
                        parties = same["party"].tolist()[:3] if len(same) >= 2 else [anchor["party"]]
                    st.session_state["_surprise_year"] = s_year
                    st.session_state["_surprise_factors"] = factors
                    st.session_state["_surprise_parties"] = parties
                    st.session_state["_surprise_pending"] = True
                    st.session_state["explore_show"] = True
                    st.rerun()

        if st.session_state.get("explore_show"):
            s_year, s_parties, s_metric_keys = cx_year, cx_parties, cx_metric_keys

            if not s_metric_keys or not s_parties:
                st.markdown(
                    '<div class="finding weak"><div class="strength-tag">SELECTION INCOMPLETE</div><div class="headline">This analysis cannot run yet.</div><div class="body">A municipality-level correlation requires at least one factor and at least one party selection. No result should be inferred from an empty selection state.</div></div>',
                    unsafe_allow_html=True
                )
                return

            results = []
            for party in s_parties:
                votes = mun[(mun["year"] == s_year) & (mun["party"] == party)][["municipality", "share"]]
                for mk in s_metric_keys:
                    m_info = next(m for m in METRIC_OPTIONS if m[0] == mk)
                    m_label = m_info[1]
                    ms = get_metric_series(m_info[2], s_year, pop_df, income_df, social_df, crime_df, cars_df, divorce_df, commute_df, employment_df, education_df, age65_df, turnout_df, immigration_df, density_df, unemployment_df, owner_occupied_df, detached_houses_df, one_person_households_df)
                    if ms.empty or "municipality" not in ms.columns:
                        continue
                    merged = votes.merge(ms, on="municipality", how="inner")
                    if merged.empty:
                        continue
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
                    '<div class="finding weak"><div class="strength-tag">NO DATA</div><div class="headline">This combination has no data.</div><div class="body">The selected factor is not available for this election year. Try a different year or factor.</div></div>',
                    unsafe_allow_html=True
                )
                return

            st.markdown("<div style='margin:2rem 0 0.5rem;border-top:2px solid #0d0d14;'><span style='font-size:0.58rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#0d0d14;background:#f5f5f7;padding:0 0.6rem;position:relative;top:-0.7rem;'>RESULT</span></div>", unsafe_allow_html=True)

            def finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note, context_label=None):
                ctx = f'<div class="copy-label" style="margin-bottom:0.3rem;">{context_label}</div>' if context_label else ""
                copy_block = ""
                if copy_sentence:
                    copy_label = "Use with caution:" if strength_tag.startswith("WEAK PATTERN") else "Write this as:"
                    copy_block = f'<div class="copy-label">{copy_label}</div><div class="copy-box">{copy_sentence}</div>'
                return f'<div class="finding {strength_cls}"><div class="strength-tag">{strength_tag}</div>{ctx}<div class="headline">{headline}</div><div class="body">{concrete}</div>{copy_block}<div class="footnote">{note}</div></div>'

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

            if len(s_parties) == 1 and len(s_metric_keys) == 1:
                row = results[0]
                if not row["valid"]:
                    invalid_body = f"{invalid_result_detail(row['reason'])} No pattern claim should be made for this result."
                    st.markdown(f'<div class="finding weak"><div class="strength-tag">RESULT UNAVAILABLE</div><div class="headline">Result unavailable</div><div class="body">{invalid_body}</div></div>', unsafe_allow_html=True)
                    return
                strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(row["r"], row["factor"], row["label"], row["party"], s_year, row["merged"], party_name_mode, country_config, all_party_names)
                st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note), unsafe_allow_html=True)
                how_to_read()

                metric_short = METRIC_SHORT_LABELS.get(row["factor"], row["label"])
                ranked_data = row["merged"].sort_values("metric").rename(columns={"municipality": "Municipality", "share": "Vote %", "metric": metric_short})
                tab_lo, tab_hi = st.tabs([f"Lowest {metric_short}", f"Highest {metric_short}"])
                with tab_lo:
                    st.markdown(f"<p style='font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.3rem;'>Lowest {metric_short} →</p>", unsafe_allow_html=True)
                    render_compact_dataframe(ranked_data.head(10))
                with tab_hi:
                    st.markdown(f"<p style='font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.3rem;'>Highest {metric_short} →</p>", unsafe_allow_html=True)
                    render_compact_dataframe(ranked_data.tail(10).sort_values(metric_short, ascending=False))

                if highlight_muni:
                    h_row = row["merged"][row["merged"]["municipality"] == highlight_muni]
                    if not h_row.empty:
                        h_metric = h_row["metric"].iloc[0]
                        h_share = h_row["share"].iloc[0]
                        sorted_all = row["merged"].sort_values("metric").reset_index(drop=True)
                        h_rank = sorted_all[sorted_all["municipality"] == highlight_muni].index[0] + 1
                        st.markdown(
                            f'<div style="border:1px solid #22d966;padding:0.8rem 1.1rem;margin-bottom:1rem;background:#f4fef8;"><span style="font-size:0.58rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:#22d966;">HIGHLIGHTED: {highlight_muni}</span><br><span style="font-size:0.88rem;color:#0d0d14;">{row["label"]}: <strong>{h_metric:.1f}</strong> &nbsp;·&nbsp; Vote share: <strong>{h_share:.1f}%</strong> &nbsp;·&nbsp; Rank {h_rank} of {len(sorted_all)} municipalities by {metric_short.lower()}</span></div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.caption(f"No data for {highlight_muni} in {s_year}.")

                st.markdown("<p style='font-size:0.75rem;color:#aaaabc;margin-top:1rem;'>Each dot = one municipality. Named dots = extremes.</p>", unsafe_allow_html=True)
                scatter_df = row["merged"].copy()
                scatter_df["vote_share"] = pd.to_numeric(scatter_df["share"], errors="coerce")
                scatter_df["metric_value"] = pd.to_numeric(scatter_df["metric"], errors="coerce")
                scatter_df = scatter_df.dropna(subset=["vote_share", "metric_value"]).copy()
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
                points_normal = base.transform_filter(alt.datum.highlighted == False).mark_circle(size=55, color="#22d966", opacity=0.65)
                points_highlight = base.transform_filter(alt.datum.highlighted == True).mark_circle(size=120, color="#e63946", opacity=1.0)
                labels = base.mark_text(align="left", dx=5, dy=-4, fontSize=10, color="#5a5a6a").encode(text="label:N")
                st.altair_chart((points_normal + points_highlight + labels).properties(height=350), use_container_width=True)
                with st.expander(f"See all {len(ranked_data)} municipalities"):
                    render_compact_dataframe(ranked_data.sort_values("Vote %", ascending=False))
            elif len(s_parties) == 1 and len(s_metric_keys) > 1:
                party = s_parties[0]
                valid_results = [r for r in results if r["valid"]]
                if not valid_results:
                    st.markdown('<div class="finding weak"><div class="strength-tag">NO VALID RESULT</div><div class="headline">No valid correlation result available</div><div class="body">None of the selected factor-party combinations produced a valid correlation value. No strongest signal is shown.</div></div>', unsafe_allow_html=True)
                    return
                ranked = sorted(valid_results, key=lambda x: abs(float(x["r"])), reverse=True)
                summary = pd.DataFrame([{"Factor": r["factor"], "Label": METRIC_SHORT_LABELS.get(r["factor"], r["factor"]), "r": r["r"], "Strength": r["strength"]} for r in ranked])
                st.markdown("<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.3rem;'>Results are ranked by correlation strength (absolute value). Positive = more votes where factor is higher. Negative = more votes where factor is lower.</p>", unsafe_allow_html=True)
                render_bar_chart(summary, "Label", "r", tooltip_label="Factor", full_label_col="Factor")
                meaningful = [r for r in ranked if abs(float(r["r"])) >= 0.30]
                no_pattern = [r for r in ranked if abs(float(r["r"])) < 0.30]
                if not meaningful:
                    meaningful = [ranked[0]]
                for row in meaningful:
                    strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(row["r"], row["factor"], row["label"], party, s_year, row["merged"], party_name_mode, country_config, all_party_names)
                    st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note), unsafe_allow_html=True)
                if no_pattern:
                    st.markdown(f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.5rem;'>No pattern found for: {', '.join(r['factor'] for r in no_pattern)} (abs(r) below 0.30).</p>", unsafe_allow_html=True)
                how_to_read()
                with st.expander("See full ranking table"):
                    render_compact_dataframe(summary[["Factor", "r", "Strength"]])
            elif len(s_parties) > 1 and len(s_metric_keys) == 1:
                valid_results = [r for r in results if r["valid"]]
                if not valid_results:
                    st.markdown('<div class="finding weak"><div class="strength-tag">NO VALID RESULT</div><div class="headline">No valid correlation result available</div><div class="body">None of the selected factor-party combinations produced a valid correlation value. No strongest signal is shown.</div></div>', unsafe_allow_html=True)
                    return
                ranked = sorted(valid_results, key=lambda x: abs(float(x["r"])), reverse=True)
                summary = pd.DataFrame([{"Party": format_party_name(r["party"], metadata=country_config.party_metadata, mode=party_name_mode, compact=True, include_code=True), "Party_full": format_party_name(r["party"], metadata=country_config.party_metadata, mode=party_name_mode, include_code=True), "r": r["r"], "Strength": r["strength"]} for r in ranked])
                st.markdown("<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.3rem;'>Results are ranked by correlation strength (absolute value). Positive = more votes where factor is higher. Negative = more votes where factor is lower.</p>", unsafe_allow_html=True)
                render_bar_chart(summary, "Party", "r", tooltip_label="Party", full_label_col="Party_full")
                meaningful = [r for r in ranked if abs(float(r["r"])) >= 0.30]
                no_pattern = [r for r in ranked if abs(float(r["r"])) < 0.30]
                if not meaningful:
                    meaningful = [ranked[0]]
                for row in meaningful:
                    strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(row["r"], row["factor"], row["label"], row["party"], s_year, row["merged"], party_name_mode, country_config, all_party_names)
                    st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note), unsafe_allow_html=True)
                if no_pattern:
                    no_pattern_names = ", ".join(format_party_name(r["party"], metadata=country_config.party_metadata, mode=party_name_mode, compact=True) for r in no_pattern)
                    st.markdown(f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.5rem;'>No pattern found for: {no_pattern_names} (abs(r) below 0.30).</p>", unsafe_allow_html=True)
                how_to_read()
                with st.expander("See full ranking table"):
                    render_compact_dataframe(summary[["Party_full", "r", "Strength"]], rename_map={"Party_full": "Party"})
            else:
                valid_results = [r for r in results if r["valid"]]
                if not valid_results:
                    st.markdown('<div class="finding weak"><div class="strength-tag">NO VALID RESULT</div><div class="headline">No valid correlation result available</div><div class="body">None of the selected factor-party combinations produced a valid correlation value. No strongest signal is shown.</div></div>', unsafe_allow_html=True)
                    return
                top = max(valid_results, key=lambda x: abs(float(x["r"])))
                strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(top["r"], top["factor"], top["label"], top["party"], s_year, top["merged"], party_name_mode, country_config, all_party_names)
                st.markdown("<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.5rem;'>Showing highest correlation across selected factors and parties. Use the full correlation table to inspect all results.</p>", unsafe_allow_html=True)
                st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note, context_label=f"Strongest signal: {format_party_name(top['party'], metadata=country_config.party_metadata, mode=party_name_mode, compact=True)} × {top['factor']}"), unsafe_allow_html=True)
                other_count = len(valid_results) - 1
                if other_count > 0:
                    st.markdown(f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.3rem;'>{other_count} other signal{'s' if other_count > 1 else ''} exist — see full correlation table.</p>", unsafe_allow_html=True)
                how_to_read()
                with st.expander("See full correlation table"):
                    flat = [{"Party": format_party_name(r["party"], metadata=country_config.party_metadata, mode=party_name_mode, include_code=True), "Factor": r["factor"], "r": r["r"]} for r in valid_results]
                    flat_df = pd.DataFrame(flat).assign(abs_r=lambda d: d["r"].abs()).sort_values("abs_r", ascending=False).drop(columns="abs_r").reset_index(drop=True)
                    render_compact_dataframe(flat_df)

    elif page == "Compare municipalities":
        st.markdown("<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>Danish Politics Data</p>", unsafe_allow_html=True)
        st.title("Compare two municipalities")
        st.markdown("<p style='font-size:0.95rem;color:#5a5a6a;margin-bottom:1.5rem;'>Pick two municipalities. See how their voting patterns and socioeconomic profiles differ.</p>", unsafe_allow_html=True)

        all_munis = sorted(mun["municipality"].unique())
        col1, col2 = st.columns(2)
        with col1:
            mun_a = st.selectbox("Municipality A", all_munis, index=0)
        with col2:
            mun_b = st.selectbox("Municipality B", all_munis, index=1)

        if mun_a == mun_b:
            st.warning("Select two different municipalities.")
            return

        st.markdown("## Voting patterns")

        votes_a = mun[mun["municipality"] == mun_a].pivot_table(index="year", columns="party", values="share")
        votes_b = mun[mun["municipality"] == mun_b].pivot_table(index="year", columns="party", values="share")
        common = votes_a.columns.intersection(votes_b.columns)
        diff_abs = (votes_a[common] - votes_b[common]).abs()
        top_parties = diff_abs.mean().sort_values(ascending=False).head(6).index.tolist()

        gap_df = (votes_a[top_parties] - votes_b[top_parties]).round(1)
        gap_chart_df = pd.DataFrame({
            "Party": [format_party_name(p, metadata=country_config.party_metadata, mode=party_name_mode, compact=True, include_code=True) for p in top_parties],
            "Party_full": [format_party_name(p, metadata=country_config.party_metadata, mode=party_name_mode, include_code=True) for p in top_parties],
            "Gap": [gap_df[p].mean() for p in top_parties],
        })

        st.markdown(
            f"<p style='font-size:0.82rem;color:#6a6a7a;margin-bottom:0.5rem;'>Percentage point gap in vote share: <strong>{mun_a}</strong> minus <strong>{mun_b}</strong>. Positive bar = {mun_a} votes more for that party. Negative = {mun_b} does.</p>",
            unsafe_allow_html=True
        )
        render_bar_chart(gap_chart_df, "Party", "Gap", tooltip_label="Party", full_label_col="Party_full")

        max_gap_row = gap_chart_df.iloc[gap_chart_df["Gap"].abs().idxmax()]
        max_gap_party = max_gap_row["Party_full"]
        max_gap_val = round(float(max_gap_row["Gap"]), 1)
        direction = mun_a if max_gap_val > 0 else mun_b
        st.markdown(
            f'<div class="finding moderate"><div class="headline">Biggest difference: {max_gap_party}</div><div class="body">On average across all elections, <strong>{direction}</strong> votes <strong>{abs(max_gap_val):.1f} percentage points more</strong> for {max_gap_party} than the other municipality.</div><div class="footnote">Based on {municipal_election_range_label} municipality elections · Danmarks Statistik (2007–2022) + official VALG bridge (2026)</div></div>',
            unsafe_allow_html=True
        )

        with st.expander("See full vote history for both municipalities"):
            display_columns = [format_party_name(p, metadata=country_config.party_metadata, mode=party_name_mode, compact=True, include_code=True) for p in top_parties]
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

        st.markdown("## Socioeconomic profile")
        st.markdown("<p style='font-size:0.82rem;color:#6a6a7a;margin-bottom:0.8rem;'>Current municipality profile using the most recent available data for each metric. Years may differ by metric. Per-1,000 and percentage factors are shown directly from the normalized public factor layer.</p>", unsafe_allow_html=True)

        def latest_val(df, municipality, year_col="year", val_col="value"):
            sub = df[df["municipality"] == municipality]
            if sub.empty:
                return None, None
            yr = sub[year_col].max()
            v = sub[sub[year_col] == yr][val_col]
            return (float(v.values[0]) if len(v) > 0 else None), int(yr)

        profile_rows = []
        metric_specs = [
            ("Population", pop_df, "population", "{:,.0f}", ""),
            ("Higher education (%)", education_df, "value", "{:.1f}", "%"),
            ("Avg. disposable income (DKK)", income_df, "value", "{:,.0f}", ""),
            ("Avg. commute distance (km)", commute_df, "value", "{:.1f}", ""),
            ("Full-time employees per 1,000", employment_df, "value", "{:.1f}", ""),
            ("Welfare recipients per 1,000", social_df, "value", "{:.1f}", ""),
            ("Reported crimes per 1,000", crime_df, "value", "{:.1f}", ""),
            ("Passenger cars per 1,000", cars_df, "value", "{:.1f}", ""),
            ("Divorces per 1,000", divorce_df, "value", "{:.1f}", ""),
            ("Aged 65+ (%)", age65_df, "value", "{:.1f}", "%"),
            ("Turnout (%)", turnout_df, "value", "{:.1f}", "%"),
            ("Residents without Danish origin (%)", immigration_df, "value", "{:.1f}", "%"),
            ("Population density (per km²)", density_df, "value", "{:.1f}", ""),
            ("Unemployment (%)", unemployment_df, "value", "{:.1f}", "%"),
            ("Owner-occupied dwellings (%)", owner_occupied_df, "value", "{:.1f}", "%"),
            ("Detached/farmhouse dwellings (%)", detached_houses_df, "value", "{:.1f}", "%"),
            ("One-person households (%)", one_person_households_df, "value", "{:.1f}", "%"),
        ]
        for label, frame, value_col, fmt, suffix in metric_specs:
            val_a, yr = latest_val(frame, mun_a, val_col=value_col)
            val_b, _ = latest_val(frame, mun_b, val_col=value_col)
            if val_a is not None and val_b is not None:
                profile_rows.append({"Metric": label, mun_a: f"{fmt.format(val_a)}{suffix}", mun_b: f"{fmt.format(val_b)}{suffix}", "Year": yr})
        if profile_rows:
            render_profile_cards(profile_rows, mun_a, mun_b)
            with st.expander("See profile as full table"):
                st.dataframe(pd.DataFrame(profile_rows), use_container_width=True, hide_index=True)
        else:
            st.info("Socioeconomic data not available for this combination.")
        st.markdown("<p style='font-size:0.68rem;color:#aaaabc;margin-top:1rem;'>Source: Danmarks Statistik (CC 4.0 BY) · Correlation ≠ causation</p>", unsafe_allow_html=True)

    elif page == "By Municipality":
        st.subheader("By Municipality")
        st.markdown("<p style='color:#6a6a7a;font-size:0.82rem;margin-bottom:1.2rem;'>Pick a party and a year. See all 98 municipalities ranked by vote share.</p>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            year = st.selectbox("Election year", sorted(mun["year"].unique(), reverse=True))
        with col2:
            parties_for_year = available_parties_for_year(year, mun)
            party = st.selectbox("Party", parties_for_year, format_func=lambda p: format_party_name(p, metadata=country_config.party_metadata, mode=party_name_mode, include_code=True))
        filtered = mun[(mun["year"] == year) & (mun["party"] == party)].sort_values("share", ascending=False)
        top = filtered.iloc[0]
        bottom = filtered.iloc[-1]
        avg = filtered["share"].mean()
        st.markdown(f"<p style='font-size:0.82rem;color:#3a3a4a;margin-bottom:0.8rem;'><strong>Highest:</strong> {top['municipality']} ({top['share']}%) &nbsp;·&nbsp; <strong>Lowest:</strong> {bottom['municipality']} ({bottom['share']}%) &nbsp;·&nbsp; <strong>Avg:</strong> {avg:.1f}%</p>", unsafe_allow_html=True)
        render_compact_dataframe(filtered[["municipality", "share"]].rename(columns={"municipality": "Municipality", "share": "Vote %"}))
        with st.expander("Show full municipality bar chart"):
            st.bar_chart(filtered.set_index("municipality")["share"])

    elif page == "National trends":
        st.subheader("National vote share, 1953–2022")
        st.markdown("<p style='color:#6a6a7a;font-size:0.82rem;margin-bottom:1rem;'>25 elections across 70 years. Select which parties to compare.</p>", unsafe_allow_html=True)
        parties_nat = ordered_national_parties(nat)
        default_nat = [party for party in top_national_parties(nat, top_n=5) if party in parties_nat]
        selected = st.multiselect("Parties", parties_nat, default=default_nat, format_func=lambda p: format_party_code(p, metadata=country_config.party_metadata, known_parties=all_party_names, mode=party_name_mode, compact=True))
        if selected:
            chart_df = nat[nat["party"].isin(selected)].copy()
            chart_df["party_label"] = chart_df["party"].apply(lambda code: format_party_code(code, metadata=country_config.party_metadata, known_parties=all_party_names, mode=party_name_mode, compact=True))
            pivot = chart_df.pivot_table(index="year", columns="party_label", values="share")
            render_national_trend_chart(chart_df, "year", "party_label", "share")
            table = pivot.round(1).astype(object).where(pivot.notna(), "—")
            st.dataframe(table, use_container_width=True)

    elif page == "About & sources":
        st.subheader("About & Sources")
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
- Party name mode changes only labels in the interface. Data values and party IDs stay the same.
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
