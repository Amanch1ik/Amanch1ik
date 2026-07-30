#!/usr/bin/env python3
"""data/contributions.json -> contrib-heatmap.svg : the 53x7 calendar as rounded boxes that
slide in diagonally on load, then freeze. CSS keyframes live inside the SVG, so GitHub plays it.
"""
import json
from datetime import datetime

DATA = "data/contributions.json"
OUT = "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BG, BORDER = "#0d1117", "#30363d"
DIM, LIGHT, GREEN = "#7d8590", "#c9d1d9", "#3fb950"

CELL, GAP = 12, 3
STEP = CELL + GAP
PAD, LEFT, TOPBAR, MONTHH = 18, 34, 34, 18
FOOTER = 30
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

d = json.load(open(DATA))
weeks = d["weeks"]
nweeks = len(weeks)

grid_w = nweeks * STEP - GAP
grid_h = 7 * STEP - GAP
W = PAD * 2 + LEFT + grid_w
gy0 = PAD + TOPBAR + MONTHH
H = gy0 + grid_h + FOOTER
gx0 = PAD + LEFT


def fmt(n):
    return f"{n:,}"


out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
]
out.append(
    '<style>'
    '@keyframes pop{from{opacity:0;transform:translateY(-5px) scale(.35)}to{opacity:1;transform:none}}'
    # base state is fully visible; "both" hides+reveals only where animation actually runs,
    # so browsers that don't animate <img> SVGs still show the whole grid (never empty).
    'rect.c{animation:pop .55s cubic-bezier(.4,0,.2,1) both;'
    'transform-box:fill-box;transform-origin:center}'
    '@media(prefers-reduced-motion:reduce){rect.c{animation:none}}'
    '</style>'
)
out.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{BG}" stroke="{BORDER}"/>')

# title bar
out.append(
    f'<text x="{PAD}" y="30" font-size="14"><tspan fill="{GREEN}" font-weight="700">amanbol</tspan>'
    f'<tspan fill="{DIM}">@github</tspan><tspan fill="{DIM}"> ~ ./contributions.sh</tspan></text>'
)
out.append(
    f'<text x="{W-PAD}" y="30" text-anchor="end" font-size="13" fill="{LIGHT}">'
    f'{fmt(d["total"])} contributions in the last year</text>'
)

# month labels
last_month = None
month_y = PAD + TOPBAR + 12
for col, wk in enumerate(weeks):
    first = next((x for x in wk if x), None)
    if not first:
        continue
    mo = datetime.strptime(first["date"], "%Y-%m-%d").month
    if mo != last_month:
        x = gx0 + col * STEP
        if x <= W - PAD - 18:
            out.append(f'<text x="{x}" y="{month_y}" font-size="11" fill="{DIM}">{MONTHS[mo-1]}</text>')
        last_month = mo

# weekday labels (Mon / Wed / Fri)
for row, lab in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
    y = gy0 + row * STEP + CELL - 2
    out.append(f'<text x="{PAD}" y="{y}" font-size="10" fill="{DIM}">{lab}</text>')

# cells
maxdelay = 0.0
for col, wk in enumerate(weeks):
    for row in range(7):
        day = wk[row]
        x = gx0 + col * STEP
        y = gy0 + row * STEP
        if not day:
            continue
        color = PALETTE[min(day["level"], 4)]
        delay = round(0.15 + (col + row) * 0.016, 3)
        maxdelay = max(maxdelay, delay)
        tip = f'{day["count"]} on {day["date"]}'
        out.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{color}" style="animation-delay:{delay}s"><title>{tip}</title></rect>'
        )

# footer: streak stats (left) + legend (right)
fy = gy0 + grid_h + 20
out.append(
    f'<text x="{PAD}" y="{fy}" font-size="12" fill="{DIM}">'
    f'<tspan fill="{LIGHT}">{d["current_streak"]}d</tspan> current streak'
    f'<tspan fill="{DIM}">   ·   </tspan>'
    f'<tspan fill="{LIGHT}">{d["longest_streak"]}d</tspan> longest'
    f'<tspan fill="{DIM}">   ·   </tspan>'
    f'<tspan fill="{LIGHT}">{d["best_day"]["count"]}</tspan> best day</text>'
)
# legend Less [][][][][] More
lx = W - PAD - (5 * (11) + 70)
out.append(f'<text x="{lx-6}" y="{fy}" text-anchor="end" font-size="11" fill="{DIM}">Less</text>')
for i, c in enumerate(PALETTE):
    out.append(f'<rect x="{lx + i*13}" y="{fy-9}" width="11" height="11" rx="2.5" fill="{c}"/>')
out.append(f'<text x="{lx + 5*13 + 4}" y="{fy}" font-size="11" fill="{DIM}">More</text>')

out.append('</svg>')
open(OUT, "w").write("\n".join(out))
print(f"wrote {OUT}  svg {W}x{H}  weeks={nweeks}  last-reveal={maxdelay:.2f}s")
