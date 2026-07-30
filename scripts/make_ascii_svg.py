#!/usr/bin/env python3
"""source-prepped.png -> avi-ascii.svg : a monochrome ASCII portrait that prints itself
row by row (SMIL wipe, plays once, freezes). GitHub renders SVG animation, so no JS needed.
"""
from PIL import Image

SRC   = "source-prepped.png"
OUT   = "amanbol-ascii.svg"
COLS  = 90                       # character columns
RAMP  = " .`:-=+*cs#%@"          # bright (sparse) -> dark (dense); leading space = blank
CHAR_ASPECT = 0.52               # monospace cell width / height
FS    = 13                       # glyph font-size (px)
CHARW = FS * 0.60
CHARH = FS * 1.08
PADX, PADY = 26, 22
INK   = "#adbac7"                # one light-gray fill — no rainbow
CURSOR = "#3fb950"               # terminal-green block riding the wipe edge
BG    = "#0d1117"                # dark terminal window, theme-proof
STAGGER = 0.052                  # per-row delay
WIPE  = 0.34                     # per-row wipe duration


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
        b = px[x, y]                         # 0=dark .. 255=white
        idx = round((255 - b) / 255 * (n - 1))
        row.append(RAMP[idx])
    lines.append("".join(row).rstrip())      # trim trailing blanks (shorter wipe)

grid_w = COLS * CHARW
W = round(grid_w + 2 * PADX)
H = round(rows * CHARH + 2 * PADY)

out = []
out.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
)
out.append(f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>')
out.append('<defs>')
for i in range(rows):
    y = PADY + i * CHARH
    rw = max(len(lines[i]), 1) * CHARW
    begin = round(i * STAGGER, 3)
    out.append(
        f'<clipPath id="c{i}"><rect x="{PADX:.1f}" y="{y:.2f}" width="0" height="{CHARH:.2f}">'
        f'<animate attributeName="width" from="0" to="{rw:.1f}" begin="{begin}s" '
        f'dur="{WIPE}s" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1" keyTimes="0;1"/>'
        f'</rect></clipPath>'
    )
out.append('</defs>')

# glyph rows, each revealed through its own clip
for i, line in enumerate(lines):
    if not line:
        continue
    baseline = PADY + i * CHARH + CHARH * 0.82
    out.append(
        f'<text x="{PADX:.1f}" y="{baseline:.2f}" xml:space="preserve" '
        f'font-size="{FS}" fill="{INK}" clip-path="url(#c{i})" '
        f'letter-spacing="{CHARW - FS*0.6:.3f}">{esc(line)}</text>'
    )

# block cursor riding each row's wipe edge, then fading out
for i, line in enumerate(lines):
    if not line:
        continue
    y = PADY + i * CHARH + CHARH * 0.12
    rw = len(line) * CHARW
    begin = round(i * STAGGER, 3)
    out.append(
        f'<rect x="{PADX:.1f}" y="{y:.2f}" width="{CHARW:.1f}" height="{CHARH*0.8:.2f}" fill="{CURSOR}" opacity="0">'
        f'<animate attributeName="x" from="{PADX:.1f}" to="{PADX+rw:.1f}" begin="{begin}s" dur="{WIPE}s" fill="freeze"/>'
        f'<animate attributeName="opacity" values="0;0.9;0.9;0" keyTimes="0;0.02;0.9;1" '
        f'begin="{begin}s" dur="{WIPE}s" fill="freeze"/>'
        f'</rect>'
    )

out.append('</svg>')
open(OUT, "w").write("\n".join(out))
print(f"wrote {OUT}  grid {COLS}x{rows}  svg {W}x{H}")
