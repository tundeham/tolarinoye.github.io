# Personal academic website: Dr. Tunde Olarinoye

A minimal, scientific-style personal website and online CV, generated from plain
YAML files and hosted **for free on GitHub Pages**.

- **One-page portfolio**: profile, impact, experience, education, publications, talks, activities, contact
- **Printable CV** at `/cv/`; "Download PDF" uses the browser's print-to-PDF with A4 print styles
- **Light & dark mode**, mobile-friendly, accessible, no cookies, no trackers, no external fonts (GDPR-friendly)
- **SEO for researchers**: meta/OpenGraph tags, `schema.org/Person` structured data, sitemap, robots.txt
- **Imprint & privacy page** (German *Impressum* template)

---

## 1. Why this setup?

| Option | Cost | Maintenance | Verdict |
|---|---|---|---|
| **Static site + GitHub Pages** (this project) | Free, custom domain, HTTPS | None: no server, no database, no updates | ✅ Best fit for a CV site |
| Django on PythonAnywhere / Render | Free tier limited (subdomain only, sleeps, expiring) | Server, DB, security patches | Overkill for mostly static content |
| WordPress.com free | Free with ads and a `wordpress.com` subdomain | Plugins/updates | Less control, ads look unprofessional |

The build script uses **Jinja2**, whose template syntax (`{% extends %}`, `{% block %}`,
`{{ var }}`, `{% for %}`) is nearly identical to Django templates, so it should feel familiar.
Content is kept separate from design: you edit **YAML**, never HTML.

---

## 2. Project structure

```
personal_website/
├── content/                 ← EDIT THESE to update the site
│   ├── profile.yaml         name, tagline, about, impact numbers, links, site URL
│   ├── experience.yaml      professional positions
│   ├── education.yaml       degrees
│   ├── expertise.yaml       competency cards (expertise & leadership)
│   ├── projects.yaml        flagship initiatives shown under Impact
│   ├── consulting.yaml      services, ways to engage, audiences ("Work with me")
│   ├── publications.yaml    papers, thesis, datasets (auto-sorted, your name auto-bolded)
│   ├── presentations.yaml   talks & posters
│   └── activities.yaml      teaching, service, skills, languages
├── templates/               Jinja2 HTML templates (Django-like)
│   ├── base.html            shared layout: head/SEO, navigation, footer
│   ├── index.html           home page sections
│   ├── cv.html              printable CV
│   ├── legal.html           Impressum / privacy
│   ├── 404.html
│   └── _macros.html         reusable snippets (citations, links, icons)
├── static/                  css/, js/, img/ (copied as-is)
├── build.py                 the generator (≈200 lines)
├── requirements.txt
└── .github/workflows/deploy.yml   auto-deploy to GitHub Pages
```

`_site/` is the generated output. It is ignored by git and rebuilt automatically.

---

## 3. Run it locally

```bash
cd ~/MyProjects/personal_website

# one-time: create the virtual environment (already done on this machine)
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# each new terminal: activate the environment (prompt shows "(.venv)")
source .venv/bin/activate

# preview with live rebuild
python build.py --serve
# → open http://localhost:8000. Edits to content/templates/static rebuild automatically
#   (refresh the browser to see them).

deactivate                       # when done (optional)
```

> In VS Code, `.vscode/settings.json` selects `.venv` as the interpreter and activates it
> automatically in new terminals, so you can type `python build.py --serve` directly.

---

## 4. Editing content

All files are commented. Typical tasks:

**Add a publication** (`content/publications.yaml`):
```yaml
- type: article            # article | preprint | thesis | dataset | chapter | report
  year: 2025
  authors: ["Olarinoye, T.", "Doe, J."]     # quote each name
  title: My new paper
  venue: Journal of Hydrology
  details: "640, 131234"
  doi: 10.1016/j.jhydrol.2025.131234
  open_access: true
  # optional: pdf, data, code, url
```
Publications are sorted automatically, numbered, filterable by type, and your surname is
highlighted. The impact section counts articles and talks automatically.

**Add a job:** add an entry at the top of `content/experience.yaml` and set `end: ""` for "Present".

**Replace the placeholder portrait:** save a square image (≈600×600 px) as `static/img/profile.jpg`
(`.png`/`.webp` also work) and rebuild. It is picked up automatically, with no config change.
The placeholder is `static/img/profile-placeholder.svg`.

**Positioning for senior roles & consulting:** edit `expertise.yaml` (what you bring, with
factual proof points), `projects.yaml` (flagship initiatives and their outcomes) and
`consulting.yaml` (services you offer and who you work with). Optional `memberships`, `awards`
and `peer_review` blocks in `activities.yaml` appear once filled in. Keep claims factual and
checkable. The build prints a reminder while any `TODO` is left in `content/`.

**Contact links:** fill `email`, `orcid`, `scholar`, `researchgate`, `github` in `profile.yaml`.
Empty ones are hidden. E-mail addresses are entity-encoded to deter simple spam bots.

**YAML tips:** indentation matters (spaces, not tabs). Quote any text containing `: `
or starting with special characters, e.g. `title: "Karst: a review"`.

---

## 5. Design customisation

- **Colours**: in `static/css/style.css`, change `--accent` (light and dark variants at the top).
- **Fonts**: system font stacks (serif headings, sans body, mono metadata), so no external requests.
- **Sections**: reorder or remove blocks in `templates/index.html` (each is clearly delimited)
  and update the nav links in `templates/base.html`.
- **Hero figure**: the "Fig. 1" hydrograph is generated in `build.py → hydrograph_path()`:
  a synthetic karst spring with fast (conduit) and slow (matrix) recession. Tweak `events` to
  change its shape.

---

## 6. Publish on GitHub Pages (free)

1. **Create a GitHub account** if needed. Your username determines the free URL.
2. **Create a repository** named exactly `<username>.github.io` (gives `https://<username>.github.io/`).
   Any other repo name also works, but the URL becomes `https://<username>.github.io/<repo>/`.
3. Set `site.url` in `content/profile.yaml` to that URL.
4. Push the project:
   ```bash
   cd ~/MyProjects/personal_website
   git init -b main
   git add .
   git commit -m "Initial website"
   git remote add origin https://github.com/<username>/<username>.github.io.git
   git push -u origin main
   ```
5. In the repository: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
6. The workflow in `.github/workflows/deploy.yml` builds and deploys on every push.
   Watch progress under the **Actions** tab. The site is live within about a minute.

From then on, **updating your site = edit YAML → commit → push.**
(You can even edit YAML directly in the GitHub web editor.)

### Optional: custom domain (≈10–15 €/year, e.g. `olarinoye.com`)
1. Buy a domain from any registrar (INWX, Namecheap, Cloudflare, …).
2. At the registrar add DNS records: four `A` records for the apex domain pointing to
   `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`, plus a
   `CNAME` for `www` → `<username>.github.io`.
3. In **Settings → Pages → Custom domain**, enter the domain and tick **Enforce HTTPS**.
4. Update `site.url` in `profile.yaml`.

---

## 7. After launch: make it work as a PR tool

- [ ] Add the URL to **LinkedIn** (Contact info → Website), **ORCID** (Websites & social links),
      **Google Scholar**, ResearchGate, your e-mail signature and conference slides.
- [ ] Submit the sitemap (`<site>/sitemap.xml`) in **Google Search Console** so searches
      for your name find the site.
- [ ] Keep publications in sync with ORCID/Scholar; add each new paper as it appears.
- [ ] Before applications, open `/cv/` → **Download PDF** for an always-current CV.
- [ ] Optional later: a "News" or "Blog" section, a datasets/software section (e.g. WoKaS),
      or privacy-friendly analytics (GoatCounter, free, cookie-less).

---

## 8. Legal note (Germany)

Because the site is professional in nature and you are based in Germany, an **Impressum**
(§ 5 DDG) and a short privacy statement are advisable. A template is in
`templates/legal.html`: fill in your postal address. This is not legal advice. Set
`site.show_legal_page: false` in `profile.yaml` to remove the page.

---

## 9. Content to verify (TODO)

Content was compiled from public sources (ICWRGC profile, journal records). LinkedIn could
not be read automatically. Search for `TODO` in `content/` and check in particular:

- Start year of the ICWRGC position and year the Ph.D. was awarded
- Exact titles of the conference talks (currently condensed)
- Deltares internship description; any earlier positions (2011–2015)
- E-mail, ORCID, Google Scholar, GitHub links; languages; GIS skill
- Publications since 2022 and the FreiDok link to the thesis
- Your postal address in the Impressum
