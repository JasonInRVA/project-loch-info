# Project Loch Public Archive

Durable, neutral public archive for public records concerning Google's proposed Project Loch data center campus in Chesterfield County, Virginia.

## Purpose

This repository is preservation-first.

- Every archived public document is stored locally in the repository.
- Older records are retained even when later materials appear to supersede or revise them.
- Each catalog entry links to the archived repository copy and an official source.
- SHA-256 hashes are published for archived PDFs.
- The site distinguishes applicant assertions, agency comments, established facts, and unresolved questions.

## Official source pages

- U.S. Army Corps of Engineers public notice: https://www.nao.usace.army.mil/Media/Public-Notices/Article/4484789/nao-2026-00182-vmrc-project-loch-chesterfield-county-virginia-wauford-prm-site/
- VMRC JPA 26-0171 docket: https://webapps.mrc.virginia.gov/public/habitat/additionaldocs.php?id=20260171

## Generated archive files

- `docs/manifest.json`
- `docs/manifest.csv`

Both are derived from the actual PDF files under `docs/`, not from prior crawler state.

## Local rebuild

```bash
python3 scripts/build_manifest.py
python3 scripts/validate_site.py
python3 -m http.server 8000
```

Then open `http://127.0.0.1:8000/`.

## GitHub Pages

The published site is expected at:

`https://jasoninrva.github.io/project-loch-info/`
