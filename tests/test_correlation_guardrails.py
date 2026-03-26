import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from correlation_utils import correlation_band, corr_strength_label, is_valid_correlation


class CorrelationGuardrailTests(unittest.TestCase):
    def test_is_valid_correlation_none(self):
        self.assertFalse(is_valid_correlation(None))

    def test_is_valid_correlation_nan(self):
        self.assertFalse(is_valid_correlation(float("nan")))

    def test_is_valid_correlation_inf(self):
        self.assertFalse(is_valid_correlation(float("inf")))

    def test_is_valid_correlation_negative_inf(self):
        self.assertFalse(is_valid_correlation(-float("inf")))

    def test_is_valid_correlation_regular_positive(self):
        self.assertTrue(is_valid_correlation(0.48))

    def test_is_valid_correlation_regular_negative(self):
        self.assertTrue(is_valid_correlation(-0.81))

    def test_is_valid_correlation_out_of_range(self):
        self.assertFalse(is_valid_correlation(1.2))

    def test_correlation_band_invalid_is_none(self):
        self.assertIsNone(correlation_band(float("nan")))

    def test_correlation_band_weak(self):
        self.assertEqual(correlation_band(0.34), "weak")

    def test_correlation_band_none(self):
        self.assertEqual(correlation_band(0.10), "none")

    def test_corr_strength_label_invalid(self):
        self.assertEqual(corr_strength_label(float("nan")), "Unavailable")


if __name__ == "__main__":
    unittest.main()
