"""Unit tests for the Evaluation enum."""

import unittest
from soliddriver_checks.api.common import Evaluation


class TestEvaluation(unittest.TestCase):
    """Test cases for Evaluation enum."""

    def test_enum_values(self):
        """Test that enum values are correct."""
        self.assertEqual(Evaluation.PASS.value, 1)
        self.assertEqual(Evaluation.WARNING.value, 2)
        self.assertEqual(Evaluation.ERROR.value, 3)

    def test_str_representation(self):
        """Test string representation of enum values."""
        self.assertEqual(str(Evaluation.PASS), "PASS")
        self.assertEqual(str(Evaluation.WARNING), "WARNING")
        self.assertEqual(str(Evaluation.ERROR), "ERROR")

    def test_int_conversion(self):
        """Test integer conversion of enum values."""
        self.assertEqual(int(Evaluation.PASS), 1)
        self.assertEqual(int(Evaluation.WARNING), 2)
        self.assertEqual(int(Evaluation.ERROR), 3)

    def test_to_json(self):
        """Test JSON serialization of enum values."""
        pass_json = Evaluation.PASS.to_json()
        self.assertEqual(pass_json, {"level": "PASS", "value": 1})

        warning_json = Evaluation.WARNING.to_json()
        self.assertEqual(warning_json, {"level": "WARNING", "value": 2})

        error_json = Evaluation.ERROR.to_json()
        self.assertEqual(error_json, {"level": "ERROR", "value": 3})

    def test_enum_comparison(self):
        """Test that enum values can be compared."""
        self.assertLess(Evaluation.PASS.value, Evaluation.WARNING.value)
        self.assertLess(Evaluation.WARNING.value, Evaluation.ERROR.value)
        self.assertEqual(max([Evaluation.PASS.value, Evaluation.WARNING.value]),
                        Evaluation.WARNING.value)

    def test_enum_uniqueness(self):
        """Test that all enum values are unique."""
        values = [e.value for e in Evaluation]
        self.assertEqual(len(values), len(set(values)))


if __name__ == '__main__':
    unittest.main()
