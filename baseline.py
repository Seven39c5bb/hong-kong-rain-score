# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib==3.10.8"]
# ///
"""Keep the first, linear daily chart as a check on the designed rain score."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from rainfall import YEAR, load_readings

OUT = Path(__file__).resolve().parent / "out"


def main():
    readings = load_readings()
    fig, ax = plt.subplots(figsize=(12, 4.5), layout="constrained")
    for reading in readings:
        if reading.kind == "measured":
            ax.bar(reading.day, float(reading.mm), width=1, color="#234b60")
        elif reading.kind == "trace":
            ax.plot(reading.day, 0, marker="o", markersize=3,
                    markerfacecolor="none", markeredgecolor="#a45437")
        else:
            ax.plot(reading.day, 0, marker="x", color="#a45437")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.set(title=f"Hong Kong Observatory: daily rainfall, {YEAR}",
           xlabel="Date (Hong Kong local calendar)", ylabel="Daily rainfall (mm)", ylim=(0, 400))
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(0, -0.23, "Linear scale. Open circles mark Trace (<0.05 mm), not zero rainfall. Source: HKO Daily Extract.",
            transform=ax.transAxes, fontsize=9)
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "baseline.png", dpi=160)
    plt.close(fig)
    print("Saved out/baseline.png")


if __name__ == "__main__":
    main()
