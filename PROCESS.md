# Process · Hong Kong Rain Score

## Tools and authorship

This project was developed with **Codex** from OpenAI. The student asked the assistant to read the course brief, propose a direction, and then implement the proposed Hong Kong rainfall score. Codex located the source, wrote the Python scripts and this documentation draft, and performed the initial data checks and visual review. The student accepted the overall project direction; the detailed implementation and wording here are assistant-produced and remain available for the student's own review. This record does not claim that the student manually wrote or independently checked the code.

Python's standard library handles fetching, JSON, dates, exact decimal sums, and source hashes. Matplotlib draws the baseline and final images. Git records actual stages of development. The files began with the instructor's assignment 2 template at commit `98f77c391bb955febd3258b4c7d95b0b92922710`, downloaded on 28 September 2026; the template's temperature scripts and placeholder text were replaced.

## What was kept, and why

The assistant proposed a twelve-row rainfall score: one month per line and one mark per day. The student accepted that direction. It keeps the calendar legible and gives the work a visual rhythm without adding invented observations. A warm paper background, blue rain strokes, and one orange peak highlight support that reading.

The implementation keeps HKO's `Trace` state as a distinct open circle. HKO defines it as less than 0.05 mm. Preserving that category is more honest than guessing an exact amount or treating it as a dry day. The parser uses exact decimal arithmetic and verifies the twelve monthly sums against the totals published in the same file.

## What was rejected or corrected, and why

1. **An assumed rainfall API.** Codex first tried a `CLMRF` endpoint by analogy with the temperature example. HKO returned an invalid-parameter response. That response was not used as data. The assistant inspected the official documentation, then the Daily Extract page, and followed the annual-file URL actually used by that page.
2. **Trusting a file extension.** The annual file ends in `.xml`, but HKO's own page parses it as JSON. The original bytes and extension are preserved; the parser follows the contents rather than assuming XML.
3. **Using summary rows as daily observations.** Every month includes `Mean/Total` and `Normal` rows. They are not extra days. The totals are used for validation and the climatological references are excluded from the drawing. Unknown row labels raise an error instead of being silently skipped.
4. **A linear scale for the final twelve-line score.** A conventional linear chart was created first and retained as `out/baseline.png`. The 368.9 mm peak leaves little room for light rainfall at the compact scale of one month row. The final design uses a shared square-root length scale, with examples and explicit wording. This improves visibility but compresses differences between large amounts; the numeric monthly totals preserve a directly readable reference.
5. **Unnecessary interactive features.** A self-contained PNG and SVG satisfy the brief and embed reliably in the README. A web page and animation would add work without helping the specific question about annual concentration.

## Validation and limits

The source snapshot contains 365 unique dates covering the whole of 2025. There are 133 positive numeric days, 179 zero days, and 53 trace days. All twelve daily sums match HKO's monthly totals. The numeric annual total is 2,558.7 mm and the July–September share is 80.88%. The loader rejects duplicate or omitted dates, malformed/negative numeric values, unexpected rows, and inconsistent totals. A missing rainfall value is represented explicitly, but stops publication of annual statistics rather than producing an incomplete total without notice.

The plotting scripts read local files only. `fetch.py` checks the cache before any request and verifies cached bytes against the provenance hashes. A fresh machine may need internet once for `uv` to install Matplotlib; after dependencies are cached, neither the source data nor plot generation needs a network connection.

Validation included eight deliberately corrupted source copies: a duplicate date, an omitted date, a negative amount, a non-finite amount, an incomplete-data flag, an unknown summary row, an inconsistent monthly sum, and a missing rainfall value. Each was rejected. The committed source hashes also matched their manifest. Both the baseline and final PNG were visually inspected for layout and labels, and the final plot was regenerated with `uv` in offline mode.

The source is a single station, so it cannot describe rainfall across every district. Daily totals hide hourly timing and intensity. Traces remain unquantified, and square-root line lengths are not proportional to raw millimetres. These limitations are also stated on the image and in the README.

## Development history

On 28 September 2026, the work proceeded through source acquisition and parsing, a first linear plot, and the designed score plus documentation. Each stage is committed with its real timestamp. **The assignment requires work across more than one day.** Today's commits cannot establish that; a genuine review or improvement on a later day is still needed. No timestamps are backdated, and inherited template commits are not counted as the student's development history.
