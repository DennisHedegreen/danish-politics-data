#!/usr/bin/env python3
"""
Fetch Danish Folketing election data from Danmarks Statistik API.
Tables: FVKOM (votes per municipality), FVPANDEL (party vote share)
Source: api.statbank.dk — CC 4.0 BY
"""

import requests
import json
import csv
import os
from pathlib import Path

BASE_URL = "https://api.statbank.dk/v1"
OUT_DIR = Path(__file__).parent / "denmark" / "folketing"


def fetch_table(table_id, variables):
    url = f"{BASE_URL}/data/{table_id}/CSV"
    payload = {
        "table": table_id,
        "format": "CSV",
        "lang": "en",
        "variables": variables
    }
    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.text


def save(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  saved: {path}")


def main():
    print("Fetching FVKOM — votes per municipality (2007-2022)")
    fvkom = fetch_table("FVKOM", [
        {"code": "VALRES", "values": ["*"]},
        {"code": "OMRÅDE", "values": ["*"]},
        {"code": "Tid",    "values": ["*"]}
    ])
    save(OUT_DIR / "fvkom_votes_by_municipality.csv", fvkom)

    print("Fetching FVPANDEL — party vote share (2007-2022)")
    fvpandel = fetch_table("FVPANDEL", [
        {"code": "VALRES", "values": ["*"]},
        {"code": "OMRÅDE", "values": ["*"]},
        {"code": "Tid",    "values": ["*"]}
    ])
    save(OUT_DIR / "fvpandel_party_share.csv", fvpandel)

    print("\nDone. Files in:", OUT_DIR)


if __name__ == "__main__":
    main()
