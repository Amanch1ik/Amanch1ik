#!/usr/bin/env python3
"""info-card.svg : a neofetch-style panel that prints next to the portrait, line by line.
Set STATIC=1 for a frozen frame (local Quick Look). GitHub plays the animated version.
"""
import os

OUT = "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

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
PADTOP  = 58          # room for the title bar

TITLE = ("amanbol", "github")   # user@host

ROWS = [
    ("Role",    "Full-Stack Developer"),
    ("Now",     "Web · Mobile · AI products"),
    ("Focus",   "SaaS · CRM · AI bots · Automation"),
    ("Stack",   "Python · TypeScript · C# · React"),
    ("Backend", "FastAPI · Django · .NET · Node"),
    ("Infra",   "Docker · PostgreSQL · Linux · CI/CD"),
    ("Shipped", "20+ products · LMS in production"),
    ("Based",   "Bishkek, Kyrgyzstan"),
    ("Links",   "Portfolio · LeetCode · Instagram"),
]
ANSI = ["#484f58", "#f85149", "#3fb950", "#d29922",
        "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]

KEYW = max(len(k) for k, _ in ROWS) + 1


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---- geometry ----
longest = max(len(TITLE[0]) + 1 + len(TITLE[1]),
              max(KEYW + 2 + len(v) for _, v in ROWS))
W = round(PADX * 2 + longest * CHARW) + 8
n_body = len(ROWS)
H = round(PADTOP + (n_body + 2.4) * LH + 34)   # +rule +swatches

out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
]
out.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{BG}" stroke="{BORDER}"/>')

# title bar: traffic-light dots + user@host
out.append(f'<circle cx="24" cy="26" r="6" fill="#f85149"/>')
out.append(f'<circle cx="44" cy="26" r="6" fill="#d29922"/>')
out.append(f'<circle cx="64" cy="26" r="6" fill="#3fb950"/>')
out.append(
    f'<text x="{W-PADX}" y="31" text-anchor="end" font-size="12.5" fill="{DIM}" '
    f'xml:space="preserve">~ neofetch</text>'
)

def anim(delay):
    if STATIC:
        return ('', '1')
    a = (f'<animate attributeName="opacity" from="0" to="1" begin="{delay}s" dur="0.32s" fill="freeze"/>'
         f'<animateTransform attributeName="transform" type="translate" from="-10 0" to="0 0" '
         f'begin="{delay}s" dur="0.32s" fill="freeze" calcMode="spline" keySplines="0.3 0 0.2 1" keyTimes="0;1"/>')
    return (a, '0')

# user@host line
d0, o0 = anim(0.0)
y = PADTOP
out.append(
    f'<text x="{PADX}" y="{y:.1f}" font-size="{FS}" opacity="{o0}" xml:space="preserve">'
    f'<tspan fill="{USER}" font-weight="700">{TITLE[0]}</tspan>'
    f'<tspan fill="{DIM}">@</tspan>'
    f'<tspan fill="{HOST}" font-weight="700">{TITLE[1]}</tspan>{d0}</text>'
)
# rule
d1, o1 = anim(0.09)
y += LH * 0.72
rule = "─" * (longest)
out.append(
    f'<text x="{PADX}" y="{y:.1f}" font-size="{FS}" fill="{DIM}" opacity="{o1}" '
    f'xml:space="preserve">{rule}{d1}</text>'
)

# body rows
for i, (k, v) in enumerate(ROWS):
    delay = round(0.18 + i * 0.11, 3)
    d, o = anim(delay)
    y += LH
    keypad = (k + ":").ljust(KEYW + 1)
    out.append(
        f'<text x="{PADX}" y="{y:.1f}" font-size="{FS}" opacity="{o}" xml:space="preserve">'
        f'<tspan fill="{KEY}" font-weight="600">{keypad}</tspan>'
        f'<tspan fill="{VAL}">{esc(v)}</tspan>{d}</text>'
    )

# ANSI swatch rows (neofetch signature)
y += LH * 0.9
sq = 15
gap = 4
delay = round(0.18 + n_body * 0.11 + 0.1, 3)
d, o = anim(delay)
out.append(f'<g opacity="{o}">')
for r in range(2):
    for c in range(8):
        idx = c if r == 0 else c  # same eight, two tones via opacity
        x = PADX + c * (sq + gap)
        yy = y + r * (sq + gap)
        op = 1.0 if r == 0 else 0.55
        out.append(f'<rect x="{x}" y="{yy:.1f}" width="{sq}" height="{sq}" rx="3" fill="{ANSI[idx]}" opacity="{op}"/>')
out.append(f'{d}</g>')

out.append('</svg>')
open(OUT, "w").write("\n".join(out))
print(f"wrote {OUT}  svg {W}x{H}  static={STATIC}")
