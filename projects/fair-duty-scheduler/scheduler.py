"""Illustrative reconstruction of a survey-weighted overnight duty scheduler.

This is not the original code deployed during military service.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import json
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

# Demonstration values, NOT actual survey results.
FATIGUE_WEIGHTS = (1, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2, 1)


def slots_for_night(day: date):
    """Return 12 hourly shifts starting at 20:00 on day."""
    start = datetime(day.year, day.month, day.day, 20)
    for hour, weight in enumerate(FATIGUE_WEIGHTS):
        begin = start + timedelta(hours=hour)
        yield begin, begin + timedelta(hours=1), weight


def generate_schedule(year: int, month: int, people: list[str],
                      unavailable: dict[str, list[str]] | None = None):
    """Greedy allocation minimizing projected accumulated fatigue.

    Each person can work at most once per night. Dates in 'unavailable'
    correspond to the day when the overnight shift begins.
    """
    if not people or len(set(people)) != len(people):
        raise ValueError("People must be a nonempty list of unique IDs")
    if len(people) < len(FATIGUE_WEIGHTS):
        raise ValueError("At least 12 people required for distinct nightly slots")
    unavailable = unavailable or {}
    known = set(people)
    if any(not isinstance(v, list) or any(p not in known for p in v)
           for v in unavailable.values()):
        raise ValueError("Unavailable entries must contain known person IDs")

    totals = {p: 0 for p in people}
    counts = Counter({p: 0 for p in people})
    rows = []
    days = calendar.monthrange(year, month)[1]
    for day_number in range(1, days + 1):
        day = date(year, month, day_number)
        blocked = set(unavailable.get(day.isoformat(), []))
        if len(known - blocked) < 12:
            raise ValueError(f"Not enough available staff on {day}")
        used = set()
        for start, end, weight in slots_for_night(day):
            eligible = [p for p in people if p not in blocked and p not in used]
            # Rotating tie-breaker avoids permanently favoring the first ID.
            rotation = (day_number - 1) % len(people)
            order = {p: (i - rotation) % len(people) for i, p in enumerate(people)}
            person = min(eligible, key=lambda p: (totals[p] + weight, counts[p], order[p]))
            totals[person] += weight
            counts[person] += 1
            used.add(person)
            rows.append({
                "night": day.isoformat(),
                "start": start.isoformat(timespec="minutes"),
                "end": end.isoformat(timespec="minutes"),
                "person": person,
                "fatigue_weight": weight,
            })
    return rows, totals, counts


def main():
    parser = argparse.ArgumentParser(description="Monthly overnight duty scheduler demo")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--people", type=int, default=60)
    parser.add_argument("--unavailable", type=Path)
    parser.add_argument("--output", type=Path, default=Path("schedule.csv"))
    args = parser.parse_args()
    if args.people < 12:
        parser.error("--people must be at least 12")
    blocked = {}
    if args.unavailable:
        blocked = json.loads(args.unavailable.read_text(encoding="utf-8"))
        if not isinstance(blocked, dict):
            parser.error("unavailable JSON must be an object")
    people = [f"P{i:03d}" for i in range(1, args.people + 1)]
    rows, totals, counts = generate_schedule(args.year, args.month, people, blocked)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} assignments to {args.output}")
    print(f"Fatigue score range: {min(totals.values())}–{max(totals.values())}")
    print(f"Assignment count range: {min(counts.values())}–{max(counts.values())}")


if __name__ == "__main__":
    main()
