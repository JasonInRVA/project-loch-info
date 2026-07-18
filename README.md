# Project Loch Public Archive

Durable, neutral public archive for public records concerning Google's proposed Project Loch data center campus in Chesterfield County, Virginia.

## Purpose

This repository is preservation-first.

- Every archived public document is stored locally in the repository.
- Older records are retained even when later materials appear to supersede or revise them.
- Each catalog entry links to the archived repository copy and an official source.
- SHA-256 hashes are published for archived PDFs.
- The site distinguishes applicant assertions, agency comments, established facts, and unresolved questions.

## Scope boundary

This archive tracks **Project Loch** first.

- Loch records are in-scope by default.
- Records for Project Skye, Project Peanut, or other data center projects are added only when they contain clear Loch-crossover evidence.
- Loch-crossover evidence means one or more of the following: (1) shared infrastructure dependencies, (2) regulatory interpretations likely reused for Loch, or (3) material contradictions, clarifications, or gaps in the Loch record.
- Parallel records that do not add Loch-specific signal are normally treated as out-of-scope for this repository stage.

## Current archive status

As of July 2026, this repository includes:

- Core Loch permitting records from the VMRC `26-0171` additional-documents docket currently posted online.
- Core Loch federal notice records for USACE `NAO-2026-00182` (public notice context and attachments package).
- Loch-related county public records already archived in this repo (agenda/minutes/presentation items tied to Project Loch approvals and context).
- Loch-supporting context captures added under the Loch-first crossover rule (for example, selected Upper Magnolia context files and DEQ PEEP provenance captures).

## Known missing records

These records are referenced in archived source material and are likely extant, but are not yet archived locally.

### Core missing (Loch-direct)

- DEQ SSWD request-level trail for `SSWD-000659` (request package, correspondence history, and outcome artifact).
- DEQ enclosures cited in Request 1: Property Access Agreement and Single-and-Complete Worksheet.
- Applicant response package received by DEQ on `2026-03-16`.
- Applicant response package received by DEQ on `2026-06-03`.
- Attachments referenced in the `2026-07-02` response package (Attachment 1, Attachment 2, enclosed mitigation plan, and cited bank-support files).

### Supporting missing (Loch-context)

- Any request-level DEQ/PEEP export artifacts that explicitly show Loch `26-0171` and `SSWD-000659` status rows (beyond current high-level public export capture).
- Additional county/EDA supporting attachments only where they add unique Loch-specific evidence beyond already archived records.

## Active acquisition plan

1. Obtain `SSWD-000659` request-level records via DEQ public export/records channels.
2. Obtain Loch DEQ-referenced enclosures and response sets not present in VMRC `26-0171` public postings.
3. Use cross-reference checks (VMRC IDs, DEQ request metadata, USACE citations) to verify each retrieved file maps to Loch and not only parallel non-Loch workflows.
4. Continue excluding Skye/Peanut materials unless they provide clear Loch-crossover evidence under the scope boundary above.

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
