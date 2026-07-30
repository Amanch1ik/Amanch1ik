#!/usr/bin/env python3
"""source-prepped.png -> amanbol-ascii.svg : a monochrome ASCII portrait that prints itself
row by row. Progressive enhancement: the base state shows the whole portrait; the CSS reveal
only adds a top-to-bottom intro where the browser animates <img> SVGs — so it is NEVER blank.
"""
from PIL import Image

SRC   = "source-prepped.png"
OUT   = "amanbol-ascii.svg"
COLS  = 90
RAMP  = " .`:-=+*cs#%@"          # bright (sparse) -> dark (dense)
CHAR_ASPECT = 0.52
FS    = 13
CHARW = FS * 0.60
CHARH = FS * 1.08
PADX, PADY = 26, 22
INK   = "#adbac7"
BG    = "#0d1117"
STAGGER = 0.03                   # per-row reveal delay


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


img = Image.open(SRC).convert("L")
w, h = img.size
rows = max(1, round(COLS * (h / w) * CHAR_ASPECT))
small = img.resize((COLS, rows))
px = small.load()

n = len(RAMP)
lines = []
for y in range(rows):
    row = []
    for x in range(COLS):
        b = px[x, y]
        idx = round((255 - b) / 255 * (n - 1))
        row.append(RAMP[idx])
    lines.append("".join(row).rstrip())

W = round(COLS * CHARW + 2 * PADX)
H = round(rows * CHARH + 2 * PADY)

out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
]
# Row-by-row spring reveal via TRANSFORM only (never opacity/clip to zero) + a one-time
# diagonal shine that sweeps across once. Browsers that animate <img> SVGs print the portrait
# line by line and get the shine; any static-poster context shows the whole portrait (at most
# shifted a few px, shine parked off-frame) — never blank.
SWEEP = round(W + 0.34 * W)
out.append(
    '<style>'
    '@keyframes ln{from{transform:translateY(-7px) scale(.99)}to{transform:none}}'
    f'@keyframes shine{{0%{{transform:translateX(0) skewX(-14deg)}}30%{{transform:translateX({SWEEP}px) skewX(-14deg)}}100%{{transform:translateX({SWEEP}px) skewX(-14deg)}}}}'
    'text.l{animation:ln .55s cubic-bezier(.34,1.32,.5,1) both}'
    '.shine{animation:shine 5s cubic-bezier(.5,0,.25,1) .6s infinite}'
    '@media(prefers-reduced-motion:reduce){text.l,.shine{animation:none}}'
    '</style>'
)
out.append(
    '<defs><linearGradient id="sh" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#ffffff" stop-opacity="0"/>'
    '<stop offset="0.5" stop-color="#ffffff" stop-opacity="0.13"/>'
    '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/>'
    f'</linearGradient><clipPath id="pw"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>'
)
out.append(f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>')

for i, line in enumerate(lines):
    if not line:
        continue
    baseline = PADY + i * CHARH + CHARH * 0.82
    delay = round(i * STAGGER, 3)
    out.append(
        f'<text class="l" style="animation-delay:{delay}s" x="{PADX:.1f}" y="{baseline:.2f}" '
        f'xml:space="preserve" font-size="{FS}" fill="{INK}" '
        f'letter-spacing="{CHARW - FS*0.6:.3f}">{esc(line)}</text>'
    )

# diagonal shine band, parked off the left edge; sweeps across once (accent, not content)
band = round(0.22 * W)
out.append(
    f'<rect class="shine" clip-path="url(#pw)" x="{-band}" y="{-0.15*H:.0f}" '
    f'width="{band}" height="{1.3*H:.0f}" fill="url(#sh)"/>'
)

out.append('</svg>')
open(OUT, "w").write("\n".join(out))
print(f"wrote {OUT}  grid {COLS}x{rows}  svg {W}x{H}")
