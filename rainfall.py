# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Read and validate HKO's 2025 daily rainfall; never access the network."""

import calendar
import json
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

YEAR = 2025
HERE = Path(__file__).resolve().parent
SOURCE = HERE / "data" / "dailyExtract_2025.xml"
RAIN_COLUMN = 8  # Zero-based. The committed source HTML labels this Total Rainfall (mm).


@dataclass(frozen=True)
class Reading:
    day: date
    mm: Decimal | None
    kind: str  # measured, trace, or missing; trace is NOT a fabricated number.


def parse_amount(value):
    """Preserve qualitative trace/missing states; reject unknown or incomplete values."""
    value = value.strip()
    if value == "Trace":
        return None, "trace"
    if value == "***":
        return None, "missing"
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"Unrecognised rainfall value: {value!r}") from exc
    if not amount.is_finite() or amount < 0:
        raise ValueError(f"Invalid rainfall amount: {value!r}")
    return amount, "measured"


def load_readings(path=SOURCE):
    """Require a complete calendar and cross-check daily sums against HKO's totals."""
    document = json.loads(Path(path).read_bytes())
    readings, months = [], set()
    for block in document["stn"]["data"]:
        month = int(block["month"])
        if month not in range(1, 13) or month in months:
            raise ValueError(f"Invalid or repeated month: {month}")
        months.add(month)
        month_readings, published_total = [], None
        for row in block["dayData"]:
            if len(row) != 12:
                raise ValueError(f"Expected 12 source columns, got {len(row)}")
            label = row[0].strip()
            if label == "Mean/Total":
                published_total = Decimal(row[RAIN_COLUMN].strip())
                continue
            if label == "Normal":
                continue  # A climatological reference, never a day of 2025.
            if not label.isdigit():
                raise ValueError(f"Unexpected source row: {label!r}")
            amount, kind = parse_amount(row[RAIN_COLUMN])
            month_readings.append(Reading(date(YEAR, month, int(label)), amount, kind))
        if published_total is None:
            raise ValueError(f"Month {month} has no published total for validation.")
        if not any(r.kind == "missing" for r in month_readings):
            calculated = sum((r.mm for r in month_readings if r.mm is not None), Decimal(0))
            if calculated != published_total:
                raise ValueError(f"Month {month}: daily sum {calculated} != HKO total {published_total}")
        readings.extend(month_readings)
    readings.sort(key=lambda r: r.day)
    expected = [date(YEAR, 1, 1) + timedelta(days=i)
                for i in range(366 if calendar.isleap(YEAR) else 365)]
    if [r.day for r in readings] != expected:
        raise ValueError("Dates are missing, duplicated, or outside the requested year.")
    return readings


def statistics(readings):
    """Calculate totals from numeric amounts only, leaving traces unquantified."""
    if any(r.kind == "missing" for r in readings):
        raise ValueError("Missing rainfall: annual statistics would be incomplete; inspect the source.")
    measured = [r for r in readings if r.mm is not None]
    monthly = [sum((r.mm for r in measured if r.day.month == m), Decimal(0))
               for m in range(1, 13)]
    total = sum(monthly, Decimal(0))
    if total <= 0:
        raise ValueError("A positive annual total is needed for the seasonal comparison.")
    return {
        "monthly_mm": monthly, "total_mm": total,
        "peak": max(measured, key=lambda r: r.mm),
        "july_september_percent": 100 * sum(monthly[6:9]) / total,
        "trace_days": sum(r.kind == "trace" for r in readings),
        "zero_days": sum(r.mm == 0 for r in measured),
        "measurable_rain_days": sum(r.mm > 0 for r in measured),
    }


def main():
    readings = load_readings()
    stats = statistics(readings)
    print(f"{len(readings)} daily records; all 12 monthly totals match HKO.")
    print(f"First record: {readings[0]}")
    print(f"Numeric rainfall total: {stats['total_mm']} mm; trace days: {stats['trace_days']}")
    print(f"Peak: {stats['peak'].day}, {stats['peak'].mm} mm")
    print(f"July–September share: {stats['july_september_percent']:.2f}%")


if __name__ == "__main__":
    main()
