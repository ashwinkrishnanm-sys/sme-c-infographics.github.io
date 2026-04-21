# Automated Page Updates — Exploration

> **Status:** spike on branch `explore/automated-page-updates`. Not yet merged.

This document is the living design record for an exploration into automating
updates of the HTML infographics in this repo. The goal is to layer more
automation on top of the existing **site chrome** scripts (`ensure-tracking.py`,
`ensure-back-button.py`, `generate-manifest.py`) so that content stays fresh,
links stay healthy, styling stays consistent, and bulk edits are safe — without
changing the fork-and-upload contributor flow described in
[adding-an-infographic-to-the-website.md](adding-an-infographic-to-the-website.md).

## Scope

In scope:

- **Inventory & audit** — a read-only report of what's on every page.
- **Freshness checks** — broken links, deprecated product names.
- **Chrome expansion** — `<meta>` description, Open Graph tags, favicon, a11y
  checks. Same idempotent, marker-based, `--check`-capable pattern as the
  existing scripts.
- **LLM-assisted content refresh** — report-only suggestions; humans still
  write.
- **Bulk templating** — a generic idempotent "find block / replace block"
  helper for site-wide edits.

Out of scope (for this branch):

- Rewriting the CoWork authoring path.
- Adopting a static-site generator.
- Moving off GitHub Pages.
- Changing the fork-and-upload contributor flow.

## Design principles (ported from the existing chrome scripts)

Every script that modifies pages must:

1. Be **idempotent** — running twice in a row is a no-op on the second run.
2. Carry a **version marker** (e.g. `/* smec-meta v1 */`) so future schema
   bumps are detectable.
3. Support a **`--check` mode** that exits non-zero when a file is missing the
   expected state, without modifying anything. Matches
   [scripts/ensure-tracking.py](../scripts/ensure-tracking.py) and
   [scripts/ensure-back-button.py](../scripts/ensure-back-button.py).
4. **Skip redirect stubs** (pages with `<meta http-equiv="refresh">`) and the
   root `index.html` library landing page.
5. **Skip** the `.git`, `node_modules`, and `.github` directories.

Every read-only auditing/reporting script should emit machine-readable output
(JSON) so results can be diffed over time and surfaced as CI artifacts.

## Phased plan

- **Phase 1 — Discovery:** `scripts/audit-pages.py` produces an inventory JSON.
- **Phase 2 — Freshness:** `scripts/check-links.py`,
  `scripts/check-deprecated-terms.py`, `scripts/terminology.json`.
- **Phase 3 — Chrome expansion:** `scripts/ensure-meta.py`,
  `scripts/ensure-favicon.py`, `scripts/ensure-a11y.py`.
- **Phase 4 — LLM content refresh (report-only):**
  `scripts/suggest-content-updates.py` + monthly scheduled workflow that opens
  a tracking issue.
- **Phase 5 — Bulk templating:** `scripts/apply-template-change.py`.
- **Phase 6 — CI wiring:** extend `ensure-site-chrome.yml` and
  `fix-site-chrome-pr.yml`; add `audit-site.yml` (warn-only on PRs) and
  `content-freshness-report.yml` (monthly).
- **Phase 7 — Docs:** finalize this document, update `README.md` pointers.

Findings from each phase are appended below as the spike progresses.

## Findings

_(filled in as phases land)_
