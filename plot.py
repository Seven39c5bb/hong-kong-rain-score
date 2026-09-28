# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib==3.10.8"]
# ///
"""Turn the committed daily observations into a reproducible rainfall score."""

import calendar
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from rainfall import YEAR, load_readings, statistics

OUT = Path(__file__).resolve().parent / "out"
PAPER = "#f5f2e9"
INK = "#17394a"
MUTED = "#677772"
RULE = "#d7ddd5"
ACCENT = "#b94e2e"
RAIN = "#29667a"
MAX_LENGTH = 3.9
SCALE_MM = 400
LEFT, RIGHT = 14.8, 81.0


def rain_length(mm):
    """A shared square-root scale makes light rain visible without clipping peaks."""
    value = float(mm)
    if not math.isfinite(value) or not 0 <= value <= SCALE_MM:
        raise ValueError(f"Rainfall {value} falls outside the labelled 0–{SCALE_MM} mm scale.")
    return MAX_LENGTH * math.sqrt(value / SCALE_MM)


def main():
    readings = load_readings()
    stats = statistics(readings)
    peak = stats["peak"]
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "path",
                         "svg.hashsalt": "hong-kong-rain-score-2025"})
    fig = plt.figure(figsize=(12, 16.8), facecolor=PAPER)
    ax = fig.add_axes([0, 0, 1, 1], xlim=(0, 100), ylim=(0, 140))
    ax.set_axis_off()

    def text(x, y, label, size=10, color=INK, **kwargs):
        return ax.text(x, y, label, fontsize=size, color=color, va="center", **kwargs)

    def rule(y, color=RULE):
        ax.plot([6, 94], [y, y], color=color, lw=0.7)

    text(6, 133, "FIELD NOTES   /   HONG KONG OBSERVATORY", 10, weight="bold")
    text(94, 133, "01  /  RAINFALL", 9, ha="right", color=MUTED)
    text(5.7, 123, "Rain score.", 53, weight="bold")
    text(94, 124, str(YEAR), 33, ha="right", color=ACCENT)
    text(6, 114.5, "A year of rain, written one day at a time.", 16)
    text(6, 110.8, "365 daily observations · one station · Hong Kong local dates", 9.5, color=MUTED)
    rule(107.5, INK)

    text(6, 102.7, f"{stats['total_mm']:,.1f} mm", 23, weight="bold")
    text(6, 98.7, "ANNUAL NUMERIC TOTAL*", 8.3, color=MUTED)
    text(39, 102.7, f"{stats['july_september_percent']:.0f}%", 23, weight="bold")
    text(39, 98.7, "FELL IN JULY–SEPTEMBER*", 8.3, color=MUTED)
    text(72, 102.7, f"{peak.mm} mm", 23, color=ACCENT, weight="bold")
    text(72, 98.7, f"WETTEST DAY  /  {peak.day.day:02d} {calendar.month_abbr[peak.day.month].upper()}", 8.3, color=MUTED)

    text(6, 94.5, "MONTH", 7.5, color=MUTED)
    text(LEFT, 94.5, "DAY OF MONTH  →", 7.5, color=MUTED)
    text(94, 94.5, "TOTAL / mm*", 7.5, ha="right", color=MUTED)
    step = (RIGHT - LEFT) / 30
    for day in range(1, 32):
        x = LEFT + (day - 1) * step
        text(x, 91.8, f"{day:02d}", 7.3, color=MUTED, ha="center")

    for month in range(1, 13):
        y = 89 - (month - 1) * 5
        days_in_month = calendar.monthrange(YEAR, month)[1]
        text(6, y - 0.5, calendar.month_abbr[month].upper(), 10, weight="bold")
        ax.plot([LEFT - 0.65, RIGHT + 0.65], [y, y], color=RULE, lw=0.55, zorder=0)
        total = stats["monthly_mm"][month - 1]
        text(94, y - 0.5, f"{total:,.1f}", 11, ha="right", weight="bold" if month in (7, 8, 9) else "normal")
        for day in range(days_in_month + 1, 32):
            x = LEFT + (day - 1) * step
            ax.add_patch(Rectangle((x - 0.65, y - MAX_LENGTH), 1.3, MAX_LENGTH + 0.45,
                                   facecolor="#e9e9e1", edgecolor="none", zorder=0))

    # The loop over the actual observations: one record controls one mark.
    for reading in readings:
        x = LEFT + (reading.day.day - 1) * step
        y = 89 - (reading.day.month - 1) * 5
        if reading.kind == "trace":
            ax.scatter(x, y, s=10, facecolors=PAPER, edgecolors=MUTED, linewidths=0.7, zorder=3)
        elif reading.kind == "missing":
            ax.scatter(x, y, s=12, marker="x", color=ACCENT)
        elif reading.mm == 0:
            ax.scatter(x, y, s=3.5, color=MUTED, zorder=3)
        else:
            length = rain_length(reading.mm)
            color = ACCENT if reading.day == peak.day else RAIN
            ax.plot([x, x], [y, y - length], color=color, lw=2.1, solid_capstyle="round", zorder=2)
    rule(28.9, INK)

    text(6, 25.5, "READING THE SCORE", 9, weight="bold")
    text(6, 22.4, "Longer strokes mean more rain.", 10)
    text(6, 20, "Length uses a square-root scale, identical in all months.", 8.5, color=MUTED)
    text(6, 17.7, "Four times the rain makes a stroke twice as long.", 8.5, color=MUTED)
    legend_y = 25
    for x, value in [(65, 10), (75, 100), (85, 300)]:
        ax.plot([x, x], [legend_y, legend_y - rain_length(value)], color=RAIN, lw=2.1, solid_capstyle="round")
        text(x + 1.3, legend_y - 0.5, f"{value} mm", 8)

    ax.scatter(6.2, 14.2, s=5, color=MUTED)
    text(7.5, 14.2, f"0 mm · {stats['zero_days']} days", 8.5)
    ax.scatter(30, 14.2, s=12, facecolors=PAPER, edgecolors=MUTED, linewidths=0.7)
    text(31.5, 14.2, f"Trace <0.05 mm · {stats['trace_days']} days", 8.5)
    ax.add_patch(Rectangle((65, 13.55), 1.2, 1.3, facecolor="#e9e9e1", edgecolor="none"))
    text(67, 14.2, "Date outside the month", 8.5)
    rule(11.1)
    text(6, 8.6, "* Totals and the seasonal share exclude unquantified Trace amounts. No daily rainfall values are missing.", 7.8, color=MUTED)
    text(6, 6.4, "Source: Hong Kong Observatory, Daily Extract of Meteorological Observations, 2025. Snapshot: 28 Sep 2026.", 7.8, color=MUTED)
    text(6, 4.2, "One station cannot describe the whole city. Daily totals hide when, and how intensely, rain fell within each day.", 7.8, color=MUTED)

    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "rain-score.png", dpi=180, facecolor=PAPER, metadata={"Title": "Hong Kong Rain Score, 2025"})
    fig.savefig(OUT / "rain-score.svg", facecolor=PAPER, metadata={"Date": None, "Title": "Hong Kong Rain Score, 2025"})
    plt.close(fig)
    print(f"365 days plotted. {stats['total_mm']} mm, excluding traces.")
    print("Saved out/rain-score.png and out/rain-score.svg")


if __name__ == "__main__":
    main()
