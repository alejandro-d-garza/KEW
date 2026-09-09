"""Tests for queue wait estimation."""

import unittest

from kew.analytics import QueueEstimator


class QueueEstimatorTests(unittest.TestCase):
    """Verify estimator calculations and validation."""

    def test_estimate_seconds(self) -> None:
        """Scale a person count by configured service time."""
        self.assertEqual(QueueEstimator(seconds_per_person=45).estimate_seconds(4), 180)

    def test_rejects_negative_values(self) -> None:
        """Reject invalid physical quantities."""
        for seconds, people in ((-1, 1), (1, -1)):
            with self.subTest(seconds=seconds, people=people), self.assertRaises(ValueError):
                QueueEstimator(seconds_per_person=seconds).estimate_seconds(people)


if __name__ == "__main__":
    unittest.main()
