#!/usr/bin/env python3
"""
Fetch and normalize the public Danish Politics Data layer.

Class A refresh:
- fetch official DST tables
- normalize to municipality-safe public factor CSVs
- write a manifest
- do not retain ordinary raw DST snapshots
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parent
FOLKETING_DIR = ROOT / "denmark" / "folketing"
SOCIO_DIR = ROOT / "denmark" / "socioeconomic"
FACTOR_DIR = ROOT / "denmark" / "factors"
INTERNAL_DIR = ROOT / "internal"
RAW_DIR = INTERNAL_DIR / "raw"
PROVENANCE_DIR = ROOT / "provenance"

BASE_URL = "https://api.statbank.dk/v1"
KOMMUNEGRUPPER_CSV_URL = "https://www.dst.dk/klassifikationsbilag/edaa83b4-6045-4708-9493-bff4d71282d8csv_da"

# Keep 2026 explicit and partial: only expose factors that survive validation.
POPULATION_REFERENCE = {
    2007: "2008Q1",
    2011: "2011Q1",
    2015: "2015Q1",
    2019: "2019Q1",
    2022: "2022Q1",
}
EMPLOYMENT_REFERENCE = {
    2007: "2008Q1",
    2011: "2011Q1",
    2015: "2015Q1",
    2019: "2019Q1",
    2022: "2022Q1",
}
IMMIGRATION_REFERENCE = {
    2007: "2008Q1",
    2011: "2011Q1",
    2015: "2015Q1",
    2019: "2019Q1",
    2022: "2022Q1",
    2026: "2026Q1",
}

TABLE_SPECS = {
    "FVKOM": {
        "path": FOLKETING_DIR / "fvkom_votes_by_municipality.csv",
        "variables": [
            {"code": "VALRES", "values": ["*"]},
            {"code": "OMRÅDE", "values": ["*"]},
            {"code": "Tid", "values": ["*"]},
        ],
    },
    "FVPANDEL": {
        "path": FOLKETING_DIR / "fvpandel_party_share.csv",
        "variables": [
            {"code": "VALRES", "values": ["*"]},
            {"code": "OMRÅDE", "values": ["*"]},
            {"code": "Tid", "values": ["*"]},
        ],
    },
    "FOLK1AM": {
        "variables": [
            {"code": "OMRÅDE", "values": ["*"]},
            {"code": "KØN", "values": ["TOT"]},
            {"code": "ALDER", "values": ["IALT"]},
            {"code": "Tid", "values": ["*"]},
        ],
    },
    "ARE207": {
        "variables": [
            {"code": "OMRÅDE", "values": ["*"]},
            {"code": "Tid", "values": ["*"]},
        ],
    },
    "FOLK1E": {
        "variables": [
            {"code": "OMRÅDE", "values": ["*"]},
            {"code": "KØN", "values": ["TOT"]},
            {"code": "ALDER", "values": ["IALT"]},
            {"code": "HERKOMST", "values": ["TOT", "1", "24", "25", "34", "35"]},
            {"code": "Tid", "values": ["*"]},
        ],
    },
    "AUP02": {
        "variables": [
            {"code": "OMRÅDE", "values": ["*"]},
            {"code": "ALDER", "values": ["TOT"]},
            {"code": "KØN", "values": ["TOT"]},
            {"code": "Tid", "values": ["*"]},
        ],
    },
}

LEGACY_LOCAL_TABLES = {
    "INDKP101": SOCIO_DIR / "indkp101_income_by_municipality.csv",
    "AUK01": SOCIO_DIR / "auk01_social_assistance.csv",
    "STRAF11": SOCIO_DIR / "straf11_crime_by_municipality.csv",
    "BIL707": SOCIO_DIR / "bil707_cars_by_municipality.csv",
    "LBESK69": SOCIO_DIR / "lbesk69_employees_by_municipality.csv",
}


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dirs() -> None:
    FACTOR_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROVENANCE_DIR.mkdir(parents=True, exist_ok=True)


def fetch_statbank_csv(table_id: str, variables: list[dict[str, list[str]]], lang: str = "en") -> str:
    url = f"{BASE_URL}/data/{table_id}/CSV"
    payload = {"table": table_id, "format": "CSV", "lang": lang, "variables": variables}
    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    return response.text


def fetch_text(url: str) -> str:
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    return response.text


def csv_from_text(text: str) -> pd.DataFrame:
    return pd.read_csv(StringIO(text), sep=";", encoding="utf-8-sig")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_factor(path: Path, df: pd.DataFrame, sort_cols: list[str] | None = None) -> dict[str, int]:
    path.parent.mkdir(parents=True, exist_ok=True)
    out = df.copy()
    if sort_cols:
        out = out.sort_values(sort_cols).reset_index(drop=True)
    out.to_csv(path, index=False)
    return {
        "rows": int(len(out)),
        "municipalities": int(out["municipality"].nunique()) if "municipality" in out.columns else 0,
        "years": int(out["year"].nunique()) if "year" in out.columns else 0,
    }


def allowed_municipalities() -> set[str]:
    path = FOLKETING_DIR / "fvpandel_party_share.csv"
    if not path.exists():
        return set()
    df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
    return {
        municipality
        for municipality in df["OMRÅDE"].dropna().unique()
        if municipality not in {"All Denmark", "Christiansø"}
    }


def keep_allowed(df: pd.DataFrame, area_col: str, allowed: set[str]) -> pd.DataFrame:
    return df[df[area_col].isin(allowed)].copy()


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def load_legacy_csv(path: Path, sep: str = ";") -> pd.DataFrame:
    return pd.read_csv(path, sep=sep, encoding="utf-8-sig")


def latest_available_month(monthly_population: pd.DataFrame, year: int) -> str | None:
    months = sorted(monthly_population.loc[monthly_population["TID"].str.startswith(str(year)), "TID"].unique())
    return months[-1] if months else None


def build_population_factor(allowed: set[str], monthly_population: pd.DataFrame) -> pd.DataFrame:
    legacy = load_legacy_csv(SOCIO_DIR / "folk1a_population_annual.csv")
    legacy = keep_allowed(legacy, "OMRÅDE", allowed)
    legacy["INDHOLD"] = to_numeric(legacy["INDHOLD"])

    rows = []
    for year, reference_period in POPULATION_REFERENCE.items():
        frame = legacy[legacy["TID"] == reference_period][["OMRÅDE", "INDHOLD"]].copy()
        frame["municipality"] = frame["OMRÅDE"]
        frame["year"] = year
        frame["reference_period"] = reference_period
        frame["value"] = frame["INDHOLD"]
        rows.append(frame[["municipality", "year", "reference_period", "value"]])

    monthly = keep_allowed(monthly_population, "OMRÅDE", allowed)
    monthly["INDHOLD"] = to_numeric(monthly["INDHOLD"])
    period_2026 = latest_available_month(monthly, 2026)
    if period_2026:
        frame = monthly[monthly["TID"] == period_2026][["OMRÅDE", "INDHOLD"]].copy()
        frame["municipality"] = frame["OMRÅDE"]
        frame["year"] = 2026
        frame["reference_period"] = period_2026
        frame["value"] = frame["INDHOLD"]
        rows.append(frame[["municipality", "year", "reference_period", "value"]])

    population = pd.concat(rows, ignore_index=True)
    population["value"] = population["value"].round(0).astype("Int64")
    return population


def build_income_factor(allowed: set[str], income_raw: pd.DataFrame) -> pd.DataFrame:
    df = keep_allowed(income_raw, "OMRÅDE", allowed)
    df = df[
        (df["ENHED"] == "Average income for all people (DKK)")
        & (df["KOEN"] == "Men and women, total")
        & df["INDKOMSTTYPE"].str.startswith("1 Disposable income", na=False)
    ].copy()
    df["year"] = df["TID"].astype(int)
    df["value"] = to_numeric(df["INDHOLD"]).round(0)
    return df[["OMRÅDE", "year", "value"]].rename(columns={"OMRÅDE": "municipality"})


def build_turnout_factor(allowed: set[str], fvkom_raw: pd.DataFrame) -> pd.DataFrame:
    df = keep_allowed(fvkom_raw, "OMRÅDE", allowed)
    df = df[df["VALRES"].isin(["NUMBER OF VOTERS", "VALID VOTES", "INVALID VOTES"])].copy()
    df["INDHOLD"] = to_numeric(df["INDHOLD"])
    pivot = df.pivot_table(index=["OMRÅDE", "TID"], columns="VALRES", values="INDHOLD", aggfunc="first").reset_index()
    pivot = pivot.dropna(subset=["NUMBER OF VOTERS", "VALID VOTES", "INVALID VOTES"]).copy()
    pivot["year"] = pivot["TID"].astype(int)
    pivot["value"] = ((pivot["VALID VOTES"] + pivot["INVALID VOTES"]) / pivot["NUMBER OF VOTERS"] * 100).round(2)
    return pivot[["OMRÅDE", "year", "value"]].rename(columns={"OMRÅDE": "municipality"})


def build_social_factor(allowed: set[str], social_raw: pd.DataFrame, population: pd.DataFrame) -> pd.DataFrame:
    df = keep_allowed(social_raw, "OMRÅDE", allowed)
    df = df[
        (df["YDELSESTYPE"] == "Net unemployed recipients of social assistance")
        & (df["KØN"] == "Total")
        & (df["ALDER"] == "Age, total")
        & df["TID"].str.endswith("Q4")
    ].copy()
    df["year"] = df["TID"].str[:4].astype(int)
    df["value"] = to_numeric(df["INDHOLD"])
    merged = df[["OMRÅDE", "year", "value"]].rename(columns={"OMRÅDE": "municipality"}).merge(
        population[["municipality", "year", "value"]].rename(columns={"value": "population"}),
        on=["municipality", "year"],
        how="inner",
    )
    merged["value"] = (merged["value"] / merged["population"] * 1000).round(2)
    return merged[["municipality", "year", "value"]]


def build_crime_factor(allowed: set[str], crime_raw: pd.DataFrame, population: pd.DataFrame) -> pd.DataFrame:
    df = keep_allowed(crime_raw, "OMRÅDE", allowed)
    df["INDHOLD"] = to_numeric(df["INDHOLD"])
    df["year"] = df["TID"].str[:4].astype(int)
    annual = df.groupby(["OMRÅDE", "year"], as_index=False)["INDHOLD"].sum()
    annual = annual.rename(columns={"OMRÅDE": "municipality", "INDHOLD": "crime_total"})
    merged = annual.merge(
        population[["municipality", "year", "value"]].rename(columns={"value": "population"}),
        on=["municipality", "year"],
        how="inner",
    )
    merged["value"] = (merged["crime_total"] / merged["population"] * 1000).round(2)
    return merged[["municipality", "year", "value"]]


def build_cars_factor(allowed: set[str], cars_raw: pd.DataFrame, population: pd.DataFrame) -> pd.DataFrame:
    df = keep_allowed(cars_raw, "OMRÅDE", allowed)
    df = df[df["BILTYPE"] == "Passenger cars, total"].copy()
    df["year"] = df["TID"].astype(int)
    df["value"] = to_numeric(df["INDHOLD"])
    merged = df[["OMRÅDE", "year", "value"]].rename(columns={"OMRÅDE": "municipality"}).merge(
        population[["municipality", "year", "value"]].rename(columns={"value": "population"}),
        on=["municipality", "year"],
        how="inner",
    )
    merged["value"] = (merged["value"] / merged["population"] * 1000).round(2)
    return merged[["municipality", "year", "value"]]


def build_divorces_factor(allowed: set[str], divorces_raw: pd.DataFrame, population: pd.DataFrame) -> pd.DataFrame:
    df = keep_allowed(divorces_raw, "BOPAEGT1", allowed)
    df = df[
        (df["BOPAEGT2"] == "All Denmark")
        & (df["ALDERAEGT1"] == "Age, total")
        & (df["ALDERAEGT2"] == "Age, total")
        & (df["AGTVAR"] == "Total")
    ].copy()
    df["year"] = df["TID"].astype(int)
    df["value"] = to_numeric(df["INDHOLD"])
    merged = df[["BOPAEGT1", "year", "value"]].rename(columns={"BOPAEGT1": "municipality"}).merge(
        population[["municipality", "year", "value"]].rename(columns={"value": "population"}),
        on=["municipality", "year"],
        how="inner",
    )
    merged["value"] = (merged["value"] / merged["population"] * 1000).round(2)
    return merged[["municipality", "year", "value"]]


def build_employment_factor(allowed: set[str], employment_raw: pd.DataFrame, population: pd.DataFrame) -> pd.DataFrame:
    df = keep_allowed(employment_raw, "BOPKOM", allowed)
    df = df[(df["TAL"] == "Full-time employees") & (df["KØN"] == "Total")].copy()
    df["value"] = to_numeric(df["INDHOLD"])

    rows = []
    for year, period in EMPLOYMENT_REFERENCE.items():
        subset = df[df["TID"] == period][["BOPKOM", "value"]].copy()
        if subset.empty:
            continue
        subset["municipality"] = subset["BOPKOM"]
        subset["year"] = year
        rows.append(subset[["municipality", "year", "value"]])

    annual = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["municipality", "year", "value"])
    merged = annual.merge(
        population[["municipality", "year", "value"]].rename(columns={"value": "population"}),
        on=["municipality", "year"],
        how="inner",
    )
    merged["value"] = (merged["value"] / merged["population"] * 1000).round(2)
    return merged[["municipality", "year", "value"]]


def build_immigration_factor(allowed: set[str], immigration_raw: pd.DataFrame) -> pd.DataFrame:
    df = keep_allowed(immigration_raw, "OMRÅDE", allowed)
    df["INDHOLD"] = to_numeric(df["INDHOLD"])
    df = df[(df["KØN"] == "Total") & (df["ALDER"] == "Age, total")].copy()
    rows = []
    for year, period in IMMIGRATION_REFERENCE.items():
        subset = df[df["TID"] == period][["OMRÅDE", "HERKOMST", "INDHOLD"]].copy()
        if subset.empty:
            continue
        pivot = subset.pivot_table(index="OMRÅDE", columns="HERKOMST", values="INDHOLD", aggfunc="first").reset_index()
        if "Total" not in pivot.columns or "Persons of Danish origin" not in pivot.columns:
            continue
        pivot["year"] = year
        pivot["value"] = ((pivot["Total"] - pivot["Persons of Danish origin"]) / pivot["Total"] * 100).round(2)
        rows.append(pivot[["OMRÅDE", "year", "value"]].rename(columns={"OMRÅDE": "municipality"}))
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["municipality", "year", "value"])


def build_population_density_factor(allowed: set[str], area_raw: pd.DataFrame, population: pd.DataFrame) -> pd.DataFrame:
    df = keep_allowed(area_raw, "OMRÅDE", allowed)
    df["year"] = df["TID"].astype(int)
    df["area_km2"] = to_numeric(df["INDHOLD"])
    area = df[["OMRÅDE", "year", "area_km2"]].rename(columns={"OMRÅDE": "municipality"})
    pop = population.copy()
    pop["area_year"] = pop["reference_period"].astype(str).str[:4].astype(int)
    merged = pop.merge(area, left_on=["municipality", "area_year"], right_on=["municipality", "year"], how="inner")
    merged["value"] = (merged["value"] / merged["area_km2"]).round(2)
    return merged[["municipality", "year_x", "value"]].rename(columns={"year_x": "year"})


def build_unemployment_factor(allowed: set[str], unemployment_raw: pd.DataFrame) -> pd.DataFrame:
    df = keep_allowed(unemployment_raw, "OMRÅDE", allowed)
    df = df[(df["ALDER"] == "Age, total") & (df["KØN"] == "Total")].copy()
    df["month"] = df["TID"].astype(str)
    df["year"] = df["month"].str[:4].astype(int)
    df["value"] = to_numeric(df["INDHOLD"])
    counts = df.groupby(["OMRÅDE", "year"], as_index=False)["month"].nunique().rename(columns={"month": "month_count"})
    annual = df.groupby(["OMRÅDE", "year"], as_index=False)["value"].mean()
    annual = annual.merge(counts, on=["OMRÅDE", "year"], how="left")
    annual = annual[annual["month_count"] >= 12].copy()
    annual["value"] = annual["value"].round(2)
    return annual[["OMRÅDE", "year", "value"]].rename(columns={"OMRÅDE": "municipality"})


def build_urban_group_factor() -> pd.DataFrame:
    text = fetch_text(KOMMUNEGRUPPER_CSV_URL)
    df = pd.read_csv(StringIO(text), sep=";", encoding="utf-8-sig")
    groups = df[df["NIVEAU"] == 1][["KODE", "TITEL"]].rename(columns={"KODE": "group_code", "TITEL": "group_label"})
    members = df[df["NIVEAU"] == 2][["KODE", "TITEL"]].rename(columns={"KODE": "municipality_code", "TITEL": "municipality_raw"})
    out = members.copy()
    out["group_code"] = None
    out["group_label"] = None
    current_group_code = None
    current_group_label = None
    for _, row in df.iterrows():
        if row["NIVEAU"] == 1:
            current_group_code = str(row["KODE"])
            current_group_label = row["TITEL"]
        elif row["NIVEAU"] == 2:
            out.loc[out["municipality_code"] == row["KODE"], "group_code"] = current_group_code
            out.loc[out["municipality_code"] == row["KODE"], "group_label"] = current_group_label
    return out[["municipality_code", "municipality_raw", "group_code", "group_label"]]


def main() -> int:
    ensure_dirs()
    started = utc_now()
    manifest: dict[str, object] = {
        "run_type": "standard_dst_refresh",
        "started_at": started,
        "storage_policy": "normalized_public_outputs_only",
        "tables": {},
        "factors": {},
        "notes": [],
    }

    print("[fetch-dst] loading municipality allowlist")
    allowed = allowed_municipalities()
    if not allowed:
        raise RuntimeError("No existing municipality allowlist found in denmark/folketing/fvpandel_party_share.csv")

    fetched: dict[str, pd.DataFrame] = {}
    for table_id, spec in TABLE_SPECS.items():
        print(f"[fetch-dst] fetching {table_id}")
        csv_text = fetch_statbank_csv(table_id, spec["variables"])
        if "path" in spec:
            write_text(spec["path"], csv_text)
        frame = csv_from_text(csv_text)
        fetched[table_id] = frame
        manifest["tables"][table_id] = {
            "rows": int(len(frame)),
            "columns": list(frame.columns),
            "saved_raw": bool(spec.get("path")),
        }

    for table_id, path in LEGACY_LOCAL_TABLES.items():
        print(f"[fetch-dst] reusing local legacy source for {table_id}")
        frame = load_legacy_csv(path)
        fetched[table_id] = frame
        manifest["tables"][table_id] = {
            "rows": int(len(frame)),
            "columns": list(frame.columns),
            "saved_raw": True,
            "source_mode": "local_legacy",
            "path": str(path.relative_to(ROOT)),
        }

    print("[fetch-dst] building normalized public factor files")
    population = build_population_factor(allowed, fetched["FOLK1AM"])
    manifest["factors"]["population.csv"] = write_factor(
        FACTOR_DIR / "population.csv",
        population,
        ["year", "municipality"],
    )

    income = build_income_factor(allowed, fetched["INDKP101"])
    manifest["factors"]["income.csv"] = write_factor(FACTOR_DIR / "income.csv", income, ["year", "municipality"])

    education = exclude_legacy_special(load_legacy_csv(SOCIO_DIR / "hfudd11_higher_edu_pct.csv", sep=","))
    manifest["factors"]["education.csv"] = write_factor(FACTOR_DIR / "education.csv", education, ["year", "municipality"])

    age65 = exclude_legacy_special(load_legacy_csv(SOCIO_DIR / "folk1a_pct_65plus.csv", sep=","))
    manifest["factors"]["age65_pct.csv"] = write_factor(FACTOR_DIR / "age65_pct.csv", age65, ["year", "municipality"])

    turnout = build_turnout_factor(allowed, fetched["FVKOM"])
    manifest["factors"]["turnout_pct.csv"] = write_factor(FACTOR_DIR / "turnout_pct.csv", turnout, ["year", "municipality"])

    welfare = build_social_factor(allowed, fetched["AUK01"], population)
    manifest["factors"]["welfare_per_1000.csv"] = write_factor(FACTOR_DIR / "welfare_per_1000.csv", welfare, ["year", "municipality"])

    crime = build_crime_factor(allowed, fetched["STRAF11"], population)
    manifest["factors"]["crime_per_1000.csv"] = write_factor(FACTOR_DIR / "crime_per_1000.csv", crime, ["year", "municipality"])

    cars = build_cars_factor(allowed, fetched["BIL707"], population)
    manifest["factors"]["cars_per_1000.csv"] = write_factor(FACTOR_DIR / "cars_per_1000.csv", cars, ["year", "municipality"])

    manifest["notes"].append(
        "Divorces were not rebuilt in this pass because the current local SKI125 extract is not a municipality-total slice. The public app should therefore keep hiding the factor until a correct total-source path is locked."
    )

    employment = build_employment_factor(allowed, fetched["LBESK69"], population)
    manifest["factors"]["employment_per_1000.csv"] = write_factor(FACTOR_DIR / "employment_per_1000.csv", employment, ["year", "municipality"])

    immigration = build_immigration_factor(allowed, fetched["FOLK1E"])
    manifest["factors"]["immigration_share_pct.csv"] = write_factor(
        FACTOR_DIR / "immigration_share_pct.csv",
        immigration,
        ["year", "municipality"],
    )

    density = build_population_density_factor(allowed, fetched["ARE207"], population)
    manifest["factors"]["population_density.csv"] = write_factor(
        FACTOR_DIR / "population_density.csv",
        density,
        ["year", "municipality"],
    )

    unemployment = build_unemployment_factor(allowed, fetched["AUP02"])
    manifest["factors"]["unemployment_pct.csv"] = write_factor(
        FACTOR_DIR / "unemployment_pct.csv",
        unemployment,
        ["year", "municipality"],
    )

    manifest["notes"].append(
        "Urban/rural municipality grouping remains queued and is not emitted by the standard DST refresh yet because the current public correlation layer is numeric and Class A refreshes should not accumulate extra reference raw."
    )

    manifest["completed_at"] = utc_now()
    manifest["public_factor_dir"] = str(FACTOR_DIR.relative_to(ROOT))
    manifest_path = PROVENANCE_DIR / f"dst-refresh-{manifest['completed_at'].replace(':', '').replace('-', '')}.json"
    write_text(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    print(f"[fetch-dst] wrote manifest: {manifest_path.relative_to(ROOT)}")
    print(f"[fetch-dst] factor layer ready in: {FACTOR_DIR.relative_to(ROOT)}")
    return 0


def exclude_legacy_special(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["year"] = out["year"].astype(int)
    return out[~out["municipality"].isin(["All Denmark", "Christiansø"])].copy()


if __name__ == "__main__":
    raise SystemExit(main())
