import unittest
from collections import Counter
from datetime import date

from scheduler import generate_schedule, slots_for_night


class DutySchedulerTests(unittest.TestCase):
    def setUp(self):
        self.people = [f"P{i:03d}" for i in range(1, 61)]

    def test_overnight_slots(self):
        slots = list(slots_for_night(date(2026, 11, 1)))
        self.assertEqual(len(slots), 12)
        self.assertEqual(slots[0][0].hour, 20)
        self.assertEqual(slots[-1][1].hour, 8)
        self.assertEqual(slots[-1][1].day, 2)

    def test_month_and_nightly_uniqueness(self):
        rows, totals, counts = generate_schedule(2026, 11, self.people)
        self.assertEqual(len(rows), 30 * 12)
        for day in set(r["night"] for r in rows):
            assigned = [r["person"] for r in rows if r["night"] == day]
            self.assertEqual(len(assigned), len(set(assigned)))
        self.assertEqual(sum(counts.values()), 360)
        self.assertEqual(sum(totals.values()), sum(r["fatigue_weight"] for r in rows))

    def test_unavailable_exclusion(self):
        rows, _, _ = generate_schedule(
            2026, 11, self.people, {"2026-11-03": ["P001", "P002"]}
        )
        self.assertFalse(any(
            r["night"] == "2026-11-03" and r["person"] in {"P001", "P002"}
            for r in rows
        ))

    def test_insufficient_staff(self):
        with self.assertRaises(ValueError):
            generate_schedule(2026, 11, self.people, {
                "2026-11-01": self.people[:49]
            })


if __name__ == "__main__":
    unittest.main()
