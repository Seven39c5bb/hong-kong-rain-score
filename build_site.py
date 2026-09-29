# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib==3.10.8"]
# ///
"""Build a self-contained website from the committed HKO snapshot, without fetching."""

import calendar
import html
import json
import shutil
from pathlib import Path

from plot import main as draw_poster, rain_length, MAX_LENGTH
from rainfall import YEAR, load_readings, statistics

HERE = Path(__file__).resolve().parent
SITE = HERE / "site"
ROW_HEIGHT = 62
STROKE_HEIGHT = 47
FIRST_X, STEP = 116, 25


def day_label(reading):
    """Describe qualitative traces without inventing a numerical rainfall amount."""
    if reading.kind == "trace":
        amount = "Trace, less than 0.05 mm"
    elif reading.mm == 0:
        amount = "0 mm, no recorded rainfall"
    else:
        amount = f"{reading.mm} mm"
    return f"{reading.day.strftime('%d %B %Y')}: {amount}"


def score_svg(readings, stats):
    """Each SVG mark comes from one actual daily observation."""
    parts = ['<svg class="score-svg" viewBox="0 0 1000 817" role="group" aria-label="Daily rainfall score, 2025">',
             '<text class="column-label" x="12" y="17">MONTH</text>',
             '<text class="column-label" x="116" y="17">DAY OF MONTH</text>',
             '<text class="column-label" text-anchor="end" x="984" y="17">TOTAL / mm*</text>']
    for day in range(1, 32):
        parts.append(f'<text class="day-label" text-anchor="middle" x="{FIRST_X + (day-1)*STEP}" y="41">{day:02}</text>')
    peak_date = stats['peak'].day.isoformat()
    for month in range(1, 13):
        y = 65 + (month - 1) * ROW_HEIGHT
        parts.append(f'<g class="month-row" data-month="{month}"><text class="month-label" x="12" y="{y+4}">{calendar.month_abbr[month].upper()}</text>')
        parts.append(f'<line class="baseline" x1="103" x2="879" y1="{y}" y2="{y}"/>')
        total = stats['monthly_mm'][month - 1]
        parts.append(f'<text class="month-total" text-anchor="end" x="984" y="{y+4}">{total:,.1f}</text>')
        for day in range(calendar.monthrange(YEAR, month)[1] + 1, 32):
            x = FIRST_X + (day - 1) * STEP
            parts.append(f'<rect class="no-date" x="{x-7}" y="{y-5}" width="14" height="{STROKE_HEIGHT+5}"/>')
        for reading in (r for r in readings if r.day.month == month):
            x = FIRST_X + (reading.day.day - 1) * STEP
            date_string = reading.day.isoformat()
            label = html.escape(day_label(reading), quote=True)
            selected = date_string == peak_date
            parts.append(f'<g class="day-mark{" selected" if selected else ""}" data-date="{date_string}" data-kind="{reading.kind}" data-value="{reading.mm if reading.mm is not None else ""}" data-y="{y}" tabindex="{0 if selected else -1}" role="button" aria-label="{label}" aria-pressed="{str(selected).lower()}">')
            parts.append(f'<title>{label}</title><rect class="hit-area" x="{x-11}" y="{y-9}" width="22" height="58" rx="5"/>')
            if reading.kind == "trace":
                parts.append(f'<circle class="trace" cx="{x}" cy="{y}" r="2.5"/>')
            elif reading.mm == 0:
                parts.append(f'<circle class="zero" cx="{x}" cy="{y}" r="1.7"/>')
            else:
                length = STROKE_HEIGHT * rain_length(reading.mm) / MAX_LENGTH
                parts.append(f'<line class="rain{" peak" if selected else ""}" x1="{x}" x2="{x}" y1="{y}" y2="{y+length:.4f}"/>')
            parts.append('</g>')
        parts.append('</g>')
    parts.append('</svg>')
    return '\n'.join(parts)


def main():
    readings = load_readings()
    stats = statistics(readings)
    draw_poster()
    SITE.mkdir(exist_ok=True)
    replacements = {
        '{{SCORE}}': score_svg(readings, stats),
        '{{TOTAL}}': f"{stats['total_mm']:,.1f}",
        '{{SHARE}}': f"{stats['july_september_percent']:.2f}",
        '{{PEAK}}': str(stats['peak'].mm),
        '{{TRACE_DAYS}}': str(stats['trace_days']),
        '{{ZERO_DAYS}}': str(stats['zero_days']),
        '{{DATA}}': json.dumps([{'date': r.day.isoformat(), 'kind': r.kind,
                                 'mm': float(r.mm) if r.mm is not None else None,
                                 'label': day_label(r)} for r in readings]).replace('</', '<\\/'),
    }
    template = (HERE / 'assets' / 'site.html').read_text(encoding='utf-8')
    for key, value in replacements.items():
        template = template.replace(key, value)
    if '{{' in template:
        raise ValueError('Unfilled website template field.')
    (SITE / 'index.html').write_text(template, encoding='utf-8')
    for filename in ('site.css', 'site.js'):
        shutil.copyfile(HERE / 'assets' / filename, SITE / filename)
    for filename in ('rain-score.png', 'rain-score.svg', 'baseline.png'):
        shutil.copyfile(HERE / 'out' / filename, SITE / filename)
    shutil.copyfile(HERE / 'data' / 'dailyExtract_2025.xml', SITE / 'dailyExtract_2025.xml')
    print('Built site/index.html from 365 committed observations. No network requests.')


if __name__ == '__main__':
    main()
