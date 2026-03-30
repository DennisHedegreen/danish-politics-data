import csv
import unittest
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FACTOR_DIR = ROOT / "denmark" / "factors"


def read_rows(name):
    path = FACTOR_DIR / name
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class FactorContractsTests(unittest.TestCase):
    def test_population_has_2026_full_municipality_coverage(self):
        rows = read_rows("population.csv")
        munis = {row["municipality"] for row in rows if row["year"] == "2026"}
        self.assertEqual(len(munis), 98)

    def test_turnout_values_stay_between_zero_and_hundred(self):
        rows = read_rows("turnout_pct.csv")
        self.assertTrue(rows)
        for row in rows:
            value = float(row["value"])
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 100.0)

    def test_turnout_covers_expected_election_years(self):
        rows = read_rows("turnout_pct.csv")
        years = sorted({int(row["year"]) for row in rows})
        self.assertEqual(years, [2007, 2011, 2015, 2019, 2022])

    def test_immigration_share_covers_2026(self):
        rows = read_rows("immigration_share_pct.csv")
        self.assertTrue(rows)
        years = {int(row["year"]) for row in rows}
        self.assertIn(2026, years)
        munis_2026 = {row["municipality"] for row in rows if row["year"] == "2026"}
        self.assertEqual(len(munis_2026), 98)

    def test_population_density_has_unique_municipality_year_rows(self):
        rows = read_rows("population_density.csv")
        seen = set()
        for row in rows:
            key = (row["municipality"], row["year"])
            self.assertNotIn(key, seen)
            seen.add(key)

    def test_unemployment_is_not_partial_2026(self):
        rows = read_rows("unemployment_pct.csv")
        years = {int(row["year"]) for row in rows}
        self.assertNotIn(2026, years)


if __name__ == "__main__":
    unittest.main()
