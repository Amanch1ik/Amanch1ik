#!/usr/bin/env python3
"""Auto-populate the Featured Projects section of README.md.

Sources (no manual input required):
  1. Public repos owned by GITHUB_USER (not forks, not archived, not the profile repo).
  2. Repos where GITHUB_USER has merged pull requests (contributions).
  3. Private repos owned by the user — only if PORTFOLIO_PAT (or GH_TOKEN with repo
     scope) is provided. Names/languages only — no description, no topics.

Optional override file `projects.yml`:
  exclude: [repo-name, owner/name, ...]
  manual:  [ {name, role, category, ...} ]   # NDA projects you want shown by hand
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # projects.yml is optional


# ────────────────────────── Configuration ──────────────────────────

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
CONFIG = ROOT / "projects.yml"

GITHUB_USER = "Amanch1ik"
PROFILE_REPO = f"{GITHUB_USER}/{GITHUB_USER}"
MAX_OWN_REPOS = 8
MAX_CONTRIB_REPOS = 4

START_MARKER = "<!-- PROJECTS:START -->"
END_MARKER = "<!-- PROJECTS:END -->"

TOKEN = os.environ.get("PORTFOLIO_PAT") or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")


# ────────────────────────── Tech badge data ──────────────────────────

# (display, bg-hex, logo-color, simple-icons slug)
TECH: dict[str, tuple[str, str, str, str]] = {
    "nestjs": ("NestJS", "E0234E", "white", "nestjs"),
    "react": ("React", "20232A", "61DAFB", "react"),
    "nextjs": ("Next.js", "000000", "white", "nextdotjs"),
    "next.js": ("Next.js", "000000", "white", "nextdotjs"),
    "vite": ("Vite", "646CFF", "white", "vite"),
    "tailwind": ("Tailwind", "06B6D4", "white", "tailwindcss"),
    "tailwindcss": ("Tailwind", "06B6D4", "white", "tailwindcss"),
    "vue": ("Vue.js", "4FC08D", "white", "vuedotjs"),
    "svelte": ("Svelte", "FF3E00", "white", "svelte"),
    "node": ("Node.js", "339933", "white", "nodedotjs"),
    "node.js": ("Node.js", "339933", "white", "nodedotjs"),
    "nodejs": ("Node.js", "339933", "white", "nodedotjs"),
    "express": ("Express", "000000", "white", "express"),
    "django": ("Django", "092E20", "white", "django"),
    "flask": ("Flask", "000000", "white", "flask"),
    "fastapi": ("FastAPI", "009688", "white", "fastapi"),
    "symfony": ("Symfony", "000000", "white", "symfony"),
    "laravel": ("Laravel", "FF2D20", "white", "laravel"),
    "dotnet": (".NET", "512BD4", "white", "dotnet"),
    ".net": (".NET", "512BD4", "white", "dotnet"),
    "postgresql": ("PostgreSQL", "4169E1", "white", "postgresql"),
    "postgres": ("PostgreSQL", "4169E1", "white", "postgresql"),
    "mysql": ("MySQL", "4479A1", "white", "mysql"),
    "mongodb": ("MongoDB", "47A248", "white", "mongodb"),
    "sqlite": ("SQLite", "003B57", "white", "sqlite"),
    "redis": ("Redis", "DC382D", "white", "redis"),
    "rabbitmq": ("RabbitMQ", "FF6600", "white", "rabbitmq"),
    "kafka": ("Kafka", "231F20", "white", "apachekafka"),
    "docker": ("Docker", "2496ED", "white", "docker"),
    "kubernetes": ("Kubernetes", "326CE5", "white", "kubernetes"),
    "k8s": ("Kubernetes", "326CE5", "white", "kubernetes"),
    "nginx": ("Nginx", "009639", "white", "nginx"),
    "linux": ("Linux", "FCC624", "black", "linux"),
    "git": ("Git", "F05032", "white", "git"),
    "github": ("GitHub", "181717", "white", "github"),
    "python": ("Python", "3776AB", "white", "python"),
    "javascript": ("JavaScript", "F7DF1E", "black", "javascript"),
    "js": ("JavaScript", "F7DF1E", "black", "javascript"),
    "typescript": ("TypeScript", "3178C6", "white", "typescript"),
    "ts": ("TypeScript", "3178C6", "white", "typescript"),
    "csharp": ("C%23", "239120", "white", "csharp"),
    "c#": ("C%23", "239120", "white", "csharp"),
    "cpp": ("C%2B%2B", "00599C", "white", "cplusplus"),
    "c++": ("C%2B%2B", "00599C", "white", "cplusplus"),
    "go": ("Go", "00ADD8", "white", "go"),
    "golang": ("Go", "00ADD8", "white", "go"),
    "rust": ("Rust", "000000", "white", "rust"),
    "php": ("PHP", "777BB4", "white", "php"),
    "ruby": ("Ruby", "CC342D", "white", "ruby"),
    "java": ("Java", "ED8B00", "white", "openjdk"),
    "tensorflow": ("TensorFlow", "FF6F00", "white", "tensorflow"),
    "pytorch": ("PyTorch", "EE4C2C", "white", "pytorch"),
    "openai": ("OpenAI", "412991", "white", "openai"),
    "html": ("HTML5", "E34F26", "white", "html5"),
    "css": ("CSS3", "1572B6", "white", "css3"),
    "scss": ("Sass", "CC6699", "white", "sass"),
    "sass": ("Sass", "CC6699", "white", "sass"),
    "graphql": ("GraphQL", "E10098", "white", "graphql"),
    "celery": ("Celery", "37814A", "white", "celery"),
    "supabase": ("Supabase", "3FCF8E", "white", "supabase"),
    "firebase": ("Firebase", "FFCA28", "black", "firebase"),
    "vercel": ("Vercel", "000000", "white", "vercel"),
    "aws": ("AWS", "232F3E", "FF9900", "amazonaws"),
    "gcp": ("GCP", "4285F4", "white", "googlecloud"),
    "telegram": ("Telegram", "26A5E4", "white", "telegram"),
    "aiogram": ("aiogram", "26A5E4", "white", "telegram"),
    "flutter": ("Flutter", "02569B", "white", "flutter"),
    "dart": ("Dart", "0175C2", "white", "dart"),
    "swift": ("Swift", "F05138", "white", "swift"),
    "kotlin": ("Kotlin", "7F52FF", "white", "kotlin"),
    "shell": ("Shell", "4EAA25", "white", "gnubash"),
    "bash": ("Bash", "4EAA25", "white", "gnubash"),
    "powershell": ("PowerShell", "5391FE", "white", "powershell"),
    "jupyter notebook": ("Jupyter", "F37626", "white", "jupyter"),
    "jupyter": ("Jupyter", "F37626", "white", "jupyter"),
    "dockerfile": ("Docker", "2496ED", "white", "docker"),
    "makefile": ("Make", "A42E2B", "white", "gnu"),
}

LINK_ICONS: dict[str, str] = {
    "github": "github",
    "gitlab": "gitlab",
    "linkedin": "linkedin",
    "youtube": "youtube",
    "instagram": "instagram",
    "twitter": "x",
    "x": "x",
    "app store": "appstore",
    "appstore": "appstore",
    "play store": "googleplay",
    "google play": "googleplay",
    "лендинг": "vercel",
    "landing": "vercel",
    "сайт": "googlechrome",
    "website": "googlechrome",
    "статья": "medium",
    "article": "medium",
    "medium": "medium",
    "habr": "habr",
    "хабр": "habr",
    "demo": "googlechrome",
    "демо": "googlechrome",
    "docs": "readthedocs",
    "документация": "readthedocs",
    "pypi": "pypi",
    "npm": "npm",
    "repo": "github",
    "репо": "github",
}

LOCK_ICON = (
    "https://img.shields.io/badge/-Private-0D1117?style=flat"
    "&logo=lock&logoColor=4FC3F7&labelColor=0D1117"
)
CONTRIB_ICON = (
    "https://img.shields.io/badge/-Contributor-0D1117?style=flat"
    "&logo=git&logoColor=4FC3F7&labelColor=0D1117"
)

MAX_STACK_ITEMS = 3
MAX_LINKS = 2
CARD_HEIGHT = 130


# ────────────────────────── HTTP ──────────────────────────

def gh_get(path: str, params: dict | None = None) -> Any:
    """GET helper for the GitHub API."""
    url = f"https://api.github.com{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", f"{GITHUB_USER}-portfolio-bot")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            reset = e.headers.get("X-RateLimit-Reset")
            wait = max(0, int(reset) - int(time.time())) if reset else 0
            print(f"Rate limit hit on {path}; reset in {wait}s", file=sys.stderr)
        else:
            print(f"HTTP {e.code} on {path}: {e.reason}", file=sys.stderr)
        return None


# ────────────────────────── Data fetch ──────────────────────────

def fetch_own_repos() -> list[dict]:
    visibility = "all" if TOKEN else "public"
    repos: list[dict] = []
    page = 1
    while True:
        batch = gh_get(
            f"/users/{GITHUB_USER}/repos" if not TOKEN else "/user/repos",
            {"per_page": 100, "page": page, "sort": "updated",
             **({"affiliation": "owner", "visibility": visibility} if TOKEN else {})},
        )
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def fetch_contributed_repos() -> list[dict]:
    """Repos (not owned by user) where user has merged PRs."""
    repo_names: dict[str, int] = {}  # full_name → pr_count
    page = 1
    while page <= 3:  # cap pagination
        result = gh_get(
            "/search/issues",
            {
                "q": f"author:{GITHUB_USER} is:pr is:merged",
                "per_page": 100,
                "page": page,
            },
        )
        if not result or "items" not in result:
            break
        for item in result["items"]:
            repo_url = item.get("repository_url", "")
            full = repo_url.replace("https://api.github.com/repos/", "")
            if not full or full.startswith(f"{GITHUB_USER}/"):
                continue
            repo_names[full] = repo_names.get(full, 0) + 1
        if len(result["items"]) < 100:
            break
        page += 1
        time.sleep(1)  # search API stricter rate limit

    repos: list[dict] = []
    for full, pr_count in repo_names.items():
        data = gh_get(f"/repos/{full}")
        if data and not data.get("private"):
            data["__pr_count"] = pr_count
            repos.append(data)
    return repos


def fetch_languages(full_name: str) -> list[str]:
    data = gh_get(f"/repos/{full_name}/languages")
    if not data:
        return []
    return sorted(data, key=lambda k: data[k], reverse=True)[:5]


# ────────────────────────── Filtering & scoring ──────────────────────────

def categorize(repo: dict, langs: list[str]) -> str:
    topics = [t.lower() for t in (repo.get("topics") or [])]
    if any(t in topics for t in ("telegram-bot", "bot", "aiogram")):
        return "Telegram Bot"
    if any(t in topics for t in ("ai", "ml", "machine-learning", "llm", "nlp")):
        return "AI / ML"
    if any(t in topics for t in ("api", "backend", "rest", "graphql")):
        return "Backend"
    if any(t in topics for t in ("frontend", "ui", "web")):
        return "Frontend"
    if any(t in topics for t in ("game", "gamedev")):
        return "Game"
    if any(t in topics for t in ("cli", "tool", "tools")):
        return "Tooling"
    main = (langs[0] if langs else repo.get("language") or "").lower()
    return {
        "python": "Python",
        "typescript": "TypeScript",
        "javascript": "JavaScript",
        "c#": "C#",
        "go": "Go",
        "rust": "Rust",
    }.get(main, "Project")


def own_score(repo: dict) -> float:
    stars = repo.get("stargazers_count", 0)
    size = min(repo.get("size", 0) / 1000, 50)  # KB → soft cap
    updated = repo.get("pushed_at", "") or repo.get("updated_at", "")
    recency = 0
    if updated:
        try:
            from datetime import datetime, timezone
            dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            days = (datetime.now(timezone.utc) - dt).days
            recency = max(0, 20 - days / 30)  # active in last ~600 days
        except Exception:
            pass
    return stars * 10 + size + recency


def contrib_score(repo: dict) -> float:
    return repo.get("stargazers_count", 0) * 5 + repo.get("__pr_count", 0) * 4


# ────────────────────────── Rendering ──────────────────────────

def shield(label: str, color: str, logo: str | None = None,
           logo_color: str = "white", label_color: str | None = None) -> str:
    text = label.replace("-", "--").replace("_", "__").replace(" ", "%20")
    url = f"https://img.shields.io/badge/{text}-{color}?style=for-the-badge"
    if logo:
        url += f"&logo={urllib.parse.quote(logo)}&logoColor={urllib.parse.quote(logo_color)}"
    if label_color:
        url += f"&labelColor={urllib.parse.quote(label_color)}"
    return url


def tech_badge(name: str) -> str:
    """Compact flat-square technology badge."""
    key = name.strip().lower()
    if key in TECH:
        display, bg, fg, logo = TECH[key]
        url = (f"https://img.shields.io/badge/{display}-{bg}?style=flat"
               f"&logo={urllib.parse.quote(logo)}&logoColor={urllib.parse.quote(fg)}")
        return f'<img src="{url}" alt="{name}" height="20"/>'
    safe = name.strip().replace(" ", "%20")
    return f'<img src="https://img.shields.io/badge/{safe}-30363D?style=flat" alt="{name}" height="20"/>'


def link_badge(label: str, url: str) -> str:
    logo = LINK_ICONS.get(label.strip().lower(), "googlechrome")
    badge_url = (f"https://img.shields.io/badge/{urllib.parse.quote(label)}-1F2937?style=flat"
                 f"&logo={urllib.parse.quote(logo)}&logoColor=white&labelColor=0D1117")
    return f'<a href="{url}" target="_blank"><img src="{badge_url}" alt="{label}" height="20"/></a>'


def render_cell(p: dict) -> str:
    name = p["name"]
    meta = " · ".join(filter(None, [p.get("category"), p.get("role"), str(p.get("period") or "")]))
    stack = (p.get("stack") or [])[:MAX_STACK_ITEMS]
    links = (p.get("links") or [])[:MAX_LINKS]
    private = bool(p.get("private"))
    contributor = bool(p.get("contributor"))

    title_icons: list[str] = []
    if private:
        title_icons.append(f'<img src="{LOCK_ICON}" alt="Private" height="18"/>')
    if contributor:
        title_icons.append(f'<img src="{CONTRIB_ICON}" alt="Contributor" height="18"/>')

    parts = [f'<td width="50%" valign="top" height="{CARD_HEIGHT}">']
    title = f"<b>{name}</b>"
    if title_icons:
        title = " ".join(title_icons) + " " + title
    parts.append(title + "<br/>")
    if meta:
        parts.append(f"<sub>{meta}</sub><br/><br/>")
    if stack:
        parts.append(" ".join(tech_badge(t) for t in stack) + "<br/>")
    if links:
        parts.append("<br/>" + " ".join(link_badge(l["label"], l["url"]) for l in links))
    parts.append("</td>")
    return "\n".join(parts)


def render_section(projects: list[dict]) -> str:
    if not projects:
        body = '<sub>пусто</sub>'
    else:
        rows = []
        for i in range(0, len(projects), 2):
            pair = projects[i:i + 2]
            cells = "\n".join(render_cell(p) for p in pair)
            if len(pair) == 1:
                cells += f'\n<td width="50%" height="{CARD_HEIGHT}"></td>'
            rows.append(f"<tr>\n{cells}\n</tr>")
        body = '<table width="100%">\n' + "\n".join(rows) + '\n</table>'
    return f"{START_MARKER}\n\n{body}\n\n{END_MARKER}"


# ────────────────────────── Pipeline ──────────────────────────

def repo_to_project(repo: dict, *, contributor: bool = False) -> dict:
    full = repo.get("full_name") or f"{GITHUB_USER}/{repo.get('name', '')}"
    langs = fetch_languages(full)
    is_private = bool(repo.get("private"))

    # NDA-safe: for private repos, do not leak description/topics — only name + langs.
    desc = "" if is_private else (repo.get("description") or "").strip()

    links: list[dict[str, str]] = []
    if not is_private:
        links.append({"label": "GitHub" if not contributor else "Repo", "url": repo["html_url"]})
        if repo.get("homepage"):
            links.append({"label": "Сайт", "url": repo["homepage"]})

    from datetime import datetime
    year = ""
    pushed = repo.get("pushed_at") or repo.get("created_at") or ""
    if pushed:
        try:
            year = str(datetime.fromisoformat(pushed.replace("Z", "+00:00")).year)
        except Exception:
            pass

    return {
        "name": repo.get("name") or full.split("/")[-1],
        "category": categorize(repo, langs),
        "role": "Author" if not contributor else "Contributor",
        "period": year,
        "description": desc,
        "stack": langs,
        "links": links,
        "private": is_private,
        "contributor": contributor,
        "_score": contrib_score(repo) if contributor else own_score(repo),
    }


def load_overrides() -> tuple[set[str], list[dict]]:
    if not CONFIG.exists() or yaml is None:
        return set(), []
    try:
        data = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        print(f"Warning: failed to parse projects.yml: {e}", file=sys.stderr)
        return set(), []
    exclude = {x.lower() for x in (data.get("exclude") or [])}
    manual = data.get("manual") or []
    return exclude, manual


def main() -> int:
    exclude, manual = load_overrides()

    print(f"Fetching own repos for {GITHUB_USER}...", file=sys.stderr)
    own_raw = fetch_own_repos() or []
    own_filtered = [
        r for r in own_raw
        if not r.get("fork")
        and not r.get("archived")
        and r.get("full_name") != PROFILE_REPO
        and r.get("name", "").lower() not in exclude
        and r.get("full_name", "").lower() not in exclude
    ]

    print(f"Fetching contributions...", file=sys.stderr)
    contrib_raw = fetch_contributed_repos() or []
    contrib_filtered = [
        r for r in contrib_raw
        if not r.get("archived")
        and r.get("name", "").lower() not in exclude
        and r.get("full_name", "").lower() not in exclude
    ]

    own_projects = [repo_to_project(r) for r in own_filtered]
    own_projects.sort(key=lambda p: p["_score"], reverse=True)
    own_projects = own_projects[:MAX_OWN_REPOS]

    contrib_projects = [repo_to_project(r, contributor=True) for r in contrib_filtered]
    contrib_projects.sort(key=lambda p: p["_score"], reverse=True)
    contrib_projects = contrib_projects[:MAX_CONTRIB_REPOS]

    manual_projects = [{**p, "_score": p.get("priority", 999_999)} for p in manual]

    all_projects = manual_projects + own_projects + contrib_projects
    all_projects.sort(key=lambda p: p["_score"], reverse=True)

    print(f"Rendering {len(all_projects)} project(s) "
          f"(manual={len(manual_projects)}, own={len(own_projects)}, contrib={len(contrib_projects)})",
          file=sys.stderr)

    new_block = render_section(all_projects)
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL)
    if not pattern.search(text):
        print(f"Markers not found in README.md", file=sys.stderr)
        return 2

    new_text = pattern.sub(new_block, text)
    if new_text == text:
        print("README already up to date")
        return 0
    README.write_text(new_text, encoding="utf-8")
    print(f"README updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
