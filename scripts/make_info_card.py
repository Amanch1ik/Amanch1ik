#!/usr/bin/env python3
"""info-card.svg : a neofetch-style panel that prints next to the portrait, line by line.
Progressive enhancement: every line's base state is fully visible; the CSS reveal only adds
an intro where the browser animates <img> SVGs. So it is NEVER blank, even without animation.
Set STATIC=1 to emit a frozen frame with no animation.
"""
import os

OUT = "info-card.svg"
# always static: GitHub rasterizes animated <img> SVGs at t=0 and would render blank lines.
STATIC = True

BG      = "#0d1117"
BORDER  = "#30363d"
USER    = "#3fb950"   # green  user
HOST    = "#58a6ff"   # blue   host
KEY     = "#58a6ff"   # blue   keys
VAL     = "#c9d1d9"   # light  values
DIM     = "#6e7681"   # dim    punctuation / rule
FS      = 15
CHARW   = FS * 0.60
LH      = FS * 1.72
PADX    = 26
PADTOP  = 58

TITLE = ("amanbol", "github")

ROWS = [
    ("Role",    "QA Engineer"),
    ("Now",     "Manual + Automation testing"),
    ("Focus",   "Web · Mobile · API"),
    ("Types",   "Functional · Regression · E2E"),
    ("Tools",   "Postman · Selenium · Playwright"),
    ("Stack",   "Python · pytest · SQL"),
    ("Track",   "Bug reports · Test cases · CI"),
    ("Based",   "Bishkek, Kyrgyzstan"),
    ("Links",   "Portfolio · LeetCode · Instagram"),
]
ANSI = ["#484f58", "#f85149", "#3fb950", "#d29922",
        "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]

KEYW = max(len(k) for k, _ in ROWS) + 1


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


longest = max(len(TITLE[0]) + 1 + len(TITLE[1]),
              max(KEYW + 2 + len(v) for _, v in ROWS))
W = round(PADX * 2 + longest * CHARW) + 8
n_body = len(ROWS)
H = round(PADTOP + (n_body + 2.4) * LH + 34)

out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
]
if not STATIC:
    out.append(
        '<style>'
        '@keyframes sl{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}'
        # base fully visible; "forwards" never applies the opacity:0 start frame before/without
        # playback -> a paused or non-animating <img> still shows every line
        '.r{animation:sl .34s cubic-bezier(.3,0,.2,1) forwards}'
        '@media(prefers-reduced-motion:reduce){.r{animation:none}}'
        '</style>'
    )
out.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{BG}" stroke="{BORDER}"/>')

# title bar (static): traffic dots + label
out.append('<circle cx="24" cy="26" r="6" fill="#f85149"/>')
out.append('<circle cx="44" cy="26" r="6" fill="#d29922"/>')
out.append('<circle cx="64" cy="26" r="6" fill="#3fb950"/>')
out.append(
    f'<text x="{W-PADX}" y="31" text-anchor="end" font-size="12.5" fill="{DIM}" '
    f'xml:space="preserve">~ neofetch</text>'
)


def cls(delay):
    return '' if STATIC else f' class="r" style="animation-delay:{delay}s"'


# user@host
y = PADTOP
out.append(
    f'<text x="{PADX}" y="{y:.1f}" font-size="{FS}"{cls(0.0)} xml:space="preserve">'
    f'<tspan fill="{USER}" font-weight="700">{TITLE[0]}</tspan>'
    f'<tspan fill="{DIM}">@</tspan>'
    f'<tspan fill="{HOST}" font-weight="700">{TITLE[1]}</tspan></text>'
)
# rule
y += LH * 0.72
out.append(
    f'<text x="{PADX}" y="{y:.1f}" font-size="{FS}" fill="{DIM}"{cls(0.09)} '
    f'xml:space="preserve">{"─" * longest}</text>'
)
# body
for i, (k, v) in enumerate(ROWS):
    delay = round(0.18 + i * 0.1, 3)
    y += LH
    keypad = (k + ":").ljust(KEYW + 1)
    out.append(
        f'<text x="{PADX}" y="{y:.1f}" font-size="{FS}"{cls(delay)} xml:space="preserve">'
        f'<tspan fill="{KEY}" font-weight="600">{keypad}</tspan>'
        f'<tspan fill="{VAL}">{esc(v)}</tspan></text>'
    )
# ANSI swatches
y += LH * 0.9
sq, gap = 15, 4
delay = round(0.18 + n_body * 0.1 + 0.1, 3)
out.append(f'<g{cls(delay)}>')
for r in range(2):
    for c in range(8):
        x = PADX + c * (sq + gap)
        yy = y + r * (sq + gap)
        op = 1.0 if r == 0 else 0.55
        out.append(f'<rect x="{x}" y="{yy:.1f}" width="{sq}" height="{sq}" rx="3" fill="{ANSI[c]}" opacity="{op}"/>')
out.append('</g>')

out.append('</svg>')
open(OUT, "w").write("\n".join(out))
print(f"wrote {OUT}  svg {W}x{H}  static={STATIC}")
