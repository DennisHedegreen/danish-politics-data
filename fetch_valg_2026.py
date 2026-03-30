#!/usr/bin/env python3
"""
Fetch and aggregate the official 2026 Folketing election from data.valg.dk.

This script keeps the finer polling-area source as the upstream truth, but writes
municipality-level exports in the same broad CSV shape that the existing public
tool already understands.
"""

from __future__ import annotations

import csv
import json
import shlex
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "denmark" / "folketing"
REMOTE_ROOT = "sftp://Valg:Valg@data.valg.dk/data/folketingsvalg-135-24-03-2026"
REMOTE_RESULTS_DIR = f"{REMOTE_ROOT}/valgresultater/"
REMOTE_KOMMUNE_JSON = f"{REMOTE_ROOT}/geografi/Kommune-190320261917.json"
REMOTE_AFST_JSON = f"{REMOTE_ROOT}/geografi/Afstemningsomraade-190320261917.json"

EXISTING_SHARE_CSV = OUT_DIR / "fvpandel_party_share.csv"
OUT_SHARE_CSV = OUT_DIR / "fv2026_party_share_by_municipality.csv"
OUT_VOTES_CSV = OUT_DIR / "fv2026_votes_by_municipality.csv"
OUT_MANIFEST_JSON = OUT_DIR / "fv2026_manifest.json"

YEAR = "2026"

# The current public tool already uses these display names.
MUNICIPALITY_NAME_ALIASES = {
    "København": "Copenhagen",
}


def curl_text(url: str) -> str:
    quoted_url = shlex.quote(url)
    result = subprocess.run(
        ["bash", "-lc", f"curl -sL --insecure {quoted_url}"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(f"curl failed for {url}: {stderr or f'code {result.returncode}'}")
    return result.stdout


def list_remote_json_files(url: str) -> list[str]:
    listing = curl_text(url)
    files = []
    for line in listing.splitlines():
        parts = line.split(maxsplit=8)
        if len(parts) < 9:
            continue
        name = parts[8]
        if name in {".", ".."} or not name.endswith(".json"):
            continue
        files.append(name)
    return sorted(files)


def load_party_label_map() -> tuple[dict[str, str], list[str]]:
    code_to_label: dict[str, str] = {}
    ordered_labels: list[str] = []
    seen_labels: set[str] = set()

    with EXISTING_SHARE_CSV.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        for row in reader:
            label = row["VALRES"]
            if label == "Total":
                continue
            if label not in seen_labels:
                ordered_labels.append(label)
                seen_labels.add(label)
            if ". " in label:
                code, _ = label.split(". ", 1)
                code_to_label[code] = label
            elif label == "Independent candidates":
                code_to_label["Independent candidates"] = label

    return code_to_label, ordered_labels


def load_existing_municipalities() -> set[str]:
    names = set()
    with EXISTING_SHARE_CSV.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        for row in reader:
            area = row["OMRÅDE"]
            if area not in {"All Denmark", "Christiansø"}:
                names.add(area)
    return names


def load_kommune_map(existing_municipalities: set[str]) -> dict[int, str]:
    municipalities = json.loads(curl_text(REMOTE_KOMMUNE_JSON))
    code_to_name: dict[int, str] = {}
    unresolved = []

    for item in municipalities:
        if item.get("Udenforkommuneinddeling"):
            continue
        raw_name = item["Navn"]
        display_name = MUNICIPALITY_NAME_ALIASES.get(raw_name, raw_name)
        if display_name not in existing_municipalities:
            unresolved.append((item["Kode"], raw_name, display_name))
        code_to_name[int(item["Kode"])] = display_name

    if unresolved:
        lines = ", ".join(f"{code}:{raw}->{display}" for code, raw, display in unresolved[:10])
        raise RuntimeError(f"Unresolved municipality names against existing dataset: {lines}")

    return code_to_name


def count_polling_areas() -> int:
    return len(json.loads(curl_text(REMOTE_AFST_JSON)))


def aggregate_results(
    result_files: list[str],
    code_to_name: dict[int, str],
    party_label_map: dict[str, str],
) -> tuple[dict[str, int], dict[tuple[str, str], int], dict[str, dict[str, str | int]]]:
    valid_votes_by_municipality: dict[str, int] = defaultdict(int)
    party_votes_by_municipality: dict[tuple[str, str], int] = defaultdict(int)
    municipality_meta: dict[str, dict[str, str | int]] = {}

    for index, filename in enumerate(result_files, start=1):
        if index == 1 or index % 100 == 0 or index == len(result_files):
            print(f"[valg2026] fetching {index}/{len(result_files)}", file=sys.stderr)

        payload = json.loads(curl_text(f"{REMOTE_RESULTS_DIR}{filename}"))

        kommune_code = int(payload["Kommunekode"])
        municipality = code_to_name[kommune_code]
        valid_votes = int(payload["GyldigeStemmer"])
        valid_votes_by_municipality[municipality] += valid_votes

        municipality_meta.setdefault(
            municipality,
            {
                "kommunekode": kommune_code,
                "storkreds": payload["Storkreds"],
                "valgdag": payload["Valgdag"],
                "resultatart": payload["Resultatart"],
            },
        )

        counted_votes = 0

        for party in payload.get("IndenforParti", []):
            code = party.get("Bogstavbetegnelse") or party.get("PartiNavn")
            label = party_label_map.get(code)
            if not label:
                official_name = party.get("PartiNavn", code)
                label = f"{code}. {official_name}" if len(str(code)) == 1 else official_name
                party_label_map[code] = label
            votes = int(party.get("Stemmer", 0))
            counted_votes += votes
            party_votes_by_municipality[(municipality, label)] += votes

        for entry in payload.get("UdenforParti", []):
            label = party_label_map.get("Independent candidates", "Independent candidates")
            votes = int(entry.get("Stemmer", 0))
            counted_votes += votes
            party_votes_by_municipality[(municipality, label)] += votes

        if counted_votes != valid_votes:
            raise RuntimeError(
                f"Vote mismatch in {filename}: parties sum to {counted_votes}, "
                f"but GyldigeStemmer is {valid_votes}"
            )

    return valid_votes_by_municipality, party_votes_by_municipality, municipality_meta


def ordered_2026_party_labels(
    existing_order: list[str],
    observed_pairs: dict[tuple[str, str], int],
) -> list[str]:
    observed = {label for (_, label), votes in observed_pairs.items() if votes > 0}
    labels = [label for label in existing_order if label in observed]
    extras = sorted(observed - set(labels))
    return labels + extras


def write_share_csv(
    municipalities: list[str],
    party_labels: list[str],
    valid_votes_by_municipality: dict[str, int],
    party_votes_by_municipality: dict[tuple[str, str], int],
) -> None:
    with OUT_SHARE_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(["VALRES", "OMRÅDE", "TID", "INDHOLD"])
        for municipality in municipalities:
            valid = valid_votes_by_municipality[municipality]
            writer.writerow(["Total", municipality, YEAR, "100.0"])
            for label in party_labels:
                votes = party_votes_by_municipality.get((municipality, label), 0)
                share = 0.0 if valid == 0 else round(votes / valid * 100, 1)
                writer.writerow([label, municipality, YEAR, f"{share:.1f}"])


def write_votes_csv(
    municipalities: list[str],
    party_labels: list[str],
    valid_votes_by_municipality: dict[str, int],
    party_votes_by_municipality: dict[tuple[str, str], int],
) -> None:
    with OUT_VOTES_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(["VALRES", "OMRÅDE", "TID", "INDHOLD"])
        for municipality in municipalities:
            writer.writerow(["VALID VOTES", municipality, YEAR, valid_votes_by_municipality[municipality]])
            for label in party_labels:
                writer.writerow([label, municipality, YEAR, party_votes_by_municipality.get((municipality, label), 0)])


def write_manifest(
    result_files: list[str],
    polling_area_count: int,
    municipalities: list[str],
    municipality_meta: dict[str, dict[str, str | int]],
) -> None:
    manifest = {
        "election": "folketing-2026-03-24",
        "source": {
            "system": "data.valg.dk",
            "path": REMOTE_ROOT,
            "result_dir": REMOTE_RESULTS_DIR,
            "geography_files": {
                "kommune": REMOTE_KOMMUNE_JSON,
                "afstemningsomraade": REMOTE_AFST_JSON,
            },
        },
        "status": "official_final_fintaelling",
        "year": 2026,
        "result_files": len(result_files),
        "polling_areas_in_geography": polling_area_count,
        "municipalities": len(municipalities),
        "municipality_meta_sample": {name: municipality_meta[name] for name in municipalities[:5]},
    }
    OUT_MANIFEST_JSON.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[valg2026] loading local mappings", file=sys.stderr)
    party_label_map, existing_party_order = load_party_label_map()
    existing_municipalities = load_existing_municipalities()

    print("[valg2026] fetching municipality geography", file=sys.stderr)
    code_to_name = load_kommune_map(existing_municipalities)

    print("[valg2026] listing remote result files", file=sys.stderr)
    result_files = list_remote_json_files(REMOTE_RESULTS_DIR)
    polling_area_count = count_polling_areas()

    valid_votes_by_municipality, party_votes_by_municipality, municipality_meta = aggregate_results(
        result_files=result_files,
        code_to_name=code_to_name,
        party_label_map=party_label_map,
    )

    municipalities = sorted(valid_votes_by_municipality)
    party_labels = ordered_2026_party_labels(existing_party_order, party_votes_by_municipality)

    if len(municipalities) != 98:
        raise RuntimeError(f"Expected 98 municipalities, got {len(municipalities)}")

    print("[valg2026] writing municipality exports", file=sys.stderr)
    write_share_csv(municipalities, party_labels, valid_votes_by_municipality, party_votes_by_municipality)
    write_votes_csv(municipalities, party_labels, valid_votes_by_municipality, party_votes_by_municipality)
    write_manifest(result_files, polling_area_count, municipalities, municipality_meta)

    print(f"[valg2026] wrote {OUT_SHARE_CSV}", file=sys.stderr)
    print(f"[valg2026] wrote {OUT_VOTES_CSV}", file=sys.stderr)
    print(f"[valg2026] wrote {OUT_MANIFEST_JSON}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
