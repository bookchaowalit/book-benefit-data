# Upgrade plan — book-benefit-data

Current state: **7/10** (was 5/10 before this pass). Offline contract, adapters and CLI are tested and linted in CI; live capture, source permission and consumers remain unverified by design.

## Backlog

- P0: Push this branch and confirm the new GitHub Actions `CI` workflow is green on both Python versions.
- P1: Strengthen drift markers for `nhs-healthcare-travel-member-benefit`, `govuk-disabled-students-allowance`, `govuk-court-fee-remission` — their `required_markers` are only fragments of the title, so a challenge or error page that repeats the title would pass. Pick body phrases from a captured page (needs a reviewed live capture; not done offline).
- P1: Replace the copy of `cli.py`/`capture.py` scaffolding shared by the sibling `book-*-data` repos with the shared runtime package once it is independently installable (README gate 3).
- P1: Expose `availability` in `demo` fixtures (a v2 demo) so `--open-only` behaviour for continuous benefits is visible without live capture.
- P2: Split the Thai welfare/water adapters out of the monolithic `normalize` into per-source functions with their own fixtures.
- P2: Add a live-capture smoke job only behind an explicit manual trigger and reviewed source permission (never on push).

## Done in this pass

- Added `.github/workflows/ci.yml`: `ruff check`, `pytest` and an offline CLI smoke (`contract`, `validate demo.json`, `demo --open-only`) on Python 3.10 and 3.13.
- Added `[project.optional-dependencies] dev` (pytest, pinned ruff), `[tool.ruff]` and `[tool.pytest.ini_options]` to `pyproject.toml`; fixed import-order lint.
- Added `tests/test_registry.py`: `sources.json` ↔ packaged `source*.json` consistency (product, domain, category in contract, https URLs, interval), source-ID selector rejects traversal/unknown IDs, every marker-driven adapter normalizes a synthetic page into a valid live record and rejects a challenge page, JSON adapters reject non-object payloads, CLI `validate` exit codes do not echo input.
- Removed dead GitHub-Education and Chevening template branches from `capture.normalize`; unknown source IDs now fail closed (`unknown benefit source`).
- GOV.UK Content API adapter rejects non-object JSON with `ValueError` instead of crashing with `AttributeError` (runtime `records` replay only catches ValueError/KeyError/OSError/RuntimeError).
- `--open-only` now honours explicit v2 `availability` windows as the README documented: a started continuous/scheduled benefit with no application deadline is included; not-yet-started or ended windows are excluded; freshness rules unchanged.
- README source list now names all seven sources; stale GitHub/Chevening attribution removed.
