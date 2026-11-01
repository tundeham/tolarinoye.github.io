#!/usr/bin/env python3
"""Build the static website.

    content/*.yaml  +  templates/*.html  +  static/   →   _site/

Usage
    python build.py            # build once into _site/
    python build.py --serve    # build, serve on http://localhost:8000 and rebuild on change
"""
from __future__ import annotations

import argparse
import datetime as dt
import functools
import http.server
import json
import math
import shutil
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUT = ROOT / "_site"

# template name → output path
PAGES = {
    "index.html": "index.html",
    "cv.html": "cv/index.html",
    "legal.html": "legal/index.html",
    "404.html": "404.html",
}

PUB_TYPE_LABELS = {
    "article": "Journal articles",
    "preprint": "Preprints",
    "chapter": "Book chapters",
    "dataset": "Datasets",
    "report": "Reports",
    "thesis": "Theses",
}


# --------------------------------------------------------------------------- content
def load_content() -> dict:
    data = {f.stem: yaml.safe_load(f.read_text(encoding="utf-8")) or {} for f in sorted(CONTENT.glob("*.yaml"))}
    pubs = sorted(data.get("publications", []), key=lambda p: (-int(p.get("year", 0)), p.get("title", "")))
    data["publications"] = pubs
    data["pub_types"] = [(t, PUB_TYPE_LABELS.get(t, t.title())) for t in dict.fromkeys(p.get("type", "article") for p in pubs)]
    data["stats"] = {
        "articles": sum(p.get("type") == "article" for p in pubs),
        "talks": len(data.get("presentations", [])),
        "first_year": min((int(p["year"]) for p in pubs if p.get("year")), default=None),
    }
    data["profile"]["photo"], data["profile"]["photo_is_placeholder"] = find_photo(data["profile"].get("photo"))
    return data


def find_photo(configured: str | None) -> tuple[str, bool]:
    """Use the configured photo, else static/img/profile.{jpg,jpeg,png,webp}, else the placeholder."""
    if configured and (STATIC / configured).exists():
        return configured, False
    for ext in ("jpg", "jpeg", "png", "webp"):
        if (STATIC / "img" / f"profile.{ext}").exists():
            return f"img/profile.{ext}", False
    return "img/profile_photo.PNG", True


def warn_todos() -> None:
    """Remind about unfinished content (the site still builds)."""
    n = sum(f.read_text(encoding="utf-8").count("TODO") for f in CONTENT.glob("*.yaml"))
    if n:
        print(f"! {n} TODO marker(s) left in content/: run  grep -rn TODO content  to review")


# --------------------------------------------------------------------------- filters
def authors_filter(authors: list[str], surname: str) -> Markup:
    """Join author names and bold the site owner's name."""
    out = []
    for a in authors:
        a_html = escape(a)
        out.append(Markup(f'<strong class="me">{a_html}</strong>') if surname and a.startswith(surname) else a_html)
    return Markup(", ").join(out)


def obfuscate_email(addr: str) -> Markup:
    """Encode e-mail as HTML entities (stops the simplest scrapers)."""
    return Markup("".join(f"&#{ord(c)};" for c in addr))


def daterange(start, end) -> str:
    start, end = str(start or "").strip(), str(end or "").strip()
    if not end:
        return f"{start} – Present"
    return start if start == end else f"{start} – {end}"


# --------------------------------------------------------------------------- hydrograph art
def hydrograph_path(width: int = 1200, height: int = 220, n: int = 600) -> dict:
    """Synthetic karst-spring hydrograph: baseflow + storm events, each recessing with a
    fast (conduit) and a slow (matrix) exponential component. Returns SVG path strings."""
    events = [(0.04, 0.55), (0.16, 0.95), (0.23, 0.35), (0.37, 0.7), (0.52, 0.45),
              (0.58, 1.0), (0.71, 0.3), (0.80, 0.8), (0.93, 0.5)]
    q = []
    for i in range(n):
        t = i / n
        v = 0.08 + 0.03 * math.sin(2 * math.pi * t)  # seasonal baseflow
        for t0, a in events:
            dtau = t - t0
            if dtau >= 0:
                v += a * (0.75 * math.exp(-dtau / 0.012) + 0.25 * math.exp(-dtau / 0.09))
            elif dtau > -0.004:  # steep rising limb
                v += a * (1 + dtau / 0.004)
        q.append(v)
    qmax = max(q)
    pts = [(i * width / (n - 1), height - 8 - (v / qmax) * (height - 24)) for i, v in enumerate(q)]
    line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = line + f" L{width},{height} L0,{height} Z"
    return {"line": line, "area": area, "width": width, "height": height}


# --------------------------------------------------------------------------- build
def make_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters.update(authors=authors_filter, obfuscate=obfuscate_email, daterange=daterange, tojson_ld=lambda d: Markup(json.dumps(d, ensure_ascii=False, indent=2)))
    return env


def json_ld(data: dict) -> dict:
    """schema.org Person: helps search engines and scholarly crawlers understand the page."""
    p = data["profile"]
    same_as = [v for k, v in p.get("links", {}).items() if v and k != "email"]
    ld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": p["name"],
        "honorificPrefix": p.get("honorific") or None,
        "jobTitle": p["headline"],
        "alumniOf": [{"@type": "CollegeOrUniversity", "name": e["institution"]} for e in data.get("education", [])],
        "knowsAbout": p.get("research_interests", []),
        "url": p["site"]["url"],
        "sameAs": same_as,
    }
    return {k: v for k, v in ld.items() if v}


def build() -> None:
    t0 = time.perf_counter()
    data = load_content()
    warn_todos()
    env = make_env()
    site_url = data["profile"]["site"]["url"].rstrip("/")
    ctx = {
        **data,
        "hydro": hydrograph_path(),
        "json_ld": json_ld(data),
        "build_date": dt.date.today(),
        "site_url": site_url,
    }

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT)

    for tpl, dest in PAGES.items():
        if tpl == "legal.html" and not data["profile"]["site"].get("show_legal_page"):
            continue
        # relative asset paths so the site works on any (sub)path; the 404 page can be
        # served at any URL depth, so it gets an absolute one instead
        root = urlparse(site_url).path.rstrip("/") + "/" if tpl == "404.html" else "../" * dest.count("/") or "./"
        html = env.get_template(tpl).render(**ctx, page=tpl, root=root)
        target = OUT / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")

    # SEO / hosting helpers
    urls = [d.removesuffix("index.html") for d in PAGES.values() if d not in ("404.html", "legal/index.html") and (OUT / d).exists()]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{site_url}/{u}</loc><lastmod>{ctx['build_date']}</lastmod></url>\n" for u in urls)
        + "</urlset>\n",
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n", encoding="utf-8")
    (OUT / ".nojekyll").touch()  # tell GitHub Pages not to run Jekyll
    print(f"✓ built {len(PAGES)} pages → {OUT.relative_to(ROOT)}/ in {time.perf_counter() - t0:.2f}s")


# --------------------------------------------------------------------------- dev server
def _snapshot() -> dict:
    return {p: p.stat().st_mtime for d in (CONTENT, TEMPLATES, STATIC) for p in d.rglob("*") if p.is_file()}


def watch() -> None:
    last = _snapshot()
    while True:
        time.sleep(1)
        now = _snapshot()
        if now != last:
            last = now
            try:
                build()
            except Exception as exc:  # keep serving on template/YAML errors
                print(f"✗ build failed: {exc}")


def serve(port: int) -> None:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    threading.Thread(target=watch, daemon=True).start()
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"→ serving on http://localhost:{port}  (Ctrl+C to stop; edits rebuild automatically)")
        httpd.serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--serve", action="store_true", help="serve locally and rebuild on changes")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    build()
    if args.serve:
        serve(args.port)
