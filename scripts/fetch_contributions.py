#!/usr/bin/env python3
"""Scrape the public contribution calendar (no token, no GraphQL) -> data/contributions.json.
GitHub serves it as plain HTML at /users/<user>/contributions — the same fragment the
profile page uses. Only requests + beautifulsoup4 needed, so it runs fine in CI.
"""
import json
import os
import re
import sys
import requests
from bs4 import BeautifulSoup

USER = os.environ.get("GH_USER", "Amanch1ik")
OUT = "data/contributions.json"

url = f"https://github.com/users/{USER}/contributions"
html = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"},
    timeout=25,
).text
soup = BeautifulSoup(html, "html.parser")

# count per day id, from the <tool-tip> elements ("N contributions on ..." / "No contributions...")
counts = {}
for tip in soup.find_all("tool-tip"):
    fid = tip.get("for", "")
    txt = tip.get_text(" ", strip=True)
    m = re.match(r"([\d,]+)\s+contribution", txt)
    counts[fid] = int(m.group(1).replace(",", "")) if m else 0

# parse day cells into a weeks grid: weeks[col][row]
grid = {}
max_col = 0
for td in soup.select("td.ContributionCalendar-day"):
    date = td.get("data-date")
    if not date:
        continue
    level = int(td.get("data-level", 0))
    cid = td.get("id", "")
    m = re.search(r"-(\d+)-(\d+)$", cid)
    # id is contribution-day-component-{weekday-row}-{week-col}
    row, col = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    max_col = max(max_col, col)
    grid.setdefault(col, {})[row] = {
        "date": date,
        "level": level,
        "count": counts.get(cid, 0),
    }

weeks = []
for col in range(max_col + 1):
    week = [grid.get(col, {}).get(row) for row in range(7)]
    weeks.append(week)

days = sorted(
    (d for wk in weeks for d in wk if d),
    key=lambda d: d["date"],
)

# streaks + best day
cur = longest = run = 0
for d in days:
    if d["count"] > 0:
        run += 1
        longest = max(longest, run)
    else:
        run = 0
for d in reversed(days):
    if d["count"] > 0:
        cur += 1
    else:
        break
best = max(days, key=lambda d: d["count"]) if days else {"date": "", "count": 0}

# total from the page header (authoritative)
mt = re.search(r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year", html)
total = int(mt.group(1).replace(",", "")) if mt else sum(d["count"] for d in days)

os.makedirs("data", exist_ok=True)
json.dump(
    {
        "username": USER,
        "total": total,
        "current_streak": cur,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "weeks": weeks,
    },
    open(OUT, "w"),
    indent=1,
)
print(f"wrote {OUT}: total={total} weeks={len(weeks)} days={len(days)} "
      f"streak(cur/long)={cur}/{longest} best={best['count']}@{best['date']}")
