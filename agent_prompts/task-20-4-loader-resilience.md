# Agent Prompt — 20.4 The replay listing survives a corrupt or empty replay file

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.4 — The replay listing survives a corrupt or empty replay file, anchored to C-5 (audits/review-2026-08-19/B/collated-findings.md, the C-5 row, P1; full finding audits/review-2026-08-19/B/api.md §2 F1 and §5 "Gaps"; adversarial verdict audits/review-2026-08-19/B/verdicts.md verdict #6 — CONFIRMED, all three sub-claims including the exception typing; roadmap slot audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-0 row 0.4 and §2 credibility row 11 UNDERMINED; audits/review-2026-08-19/D/cross-track-map.md, the C-5 row, RR-free); api/replay_loader.py:703-729 (`list_replays`; the sole guard is `except ReplayLog.CorruptedFileError` at :727, logged at :728), :714-718 (the docstring claim "one bad replay no longer blocks the picker (Audit K-K-8, backend half)"), :731-748 (`load_replay` — the direct-fetch path this task deliberately leaves loud), :750-778 (`cost_summary`; the per-file reduction at :759 has no guard at all), :1683-1686 (`_file_summary`), :1688-1725 (`_read_summary`), :1727-1739 (`_metadata_view`), :1944-1969 (`_replay_paths`), :1985-1997 (`_resolve_path`); orchestrator/replay.py:1137-1187 (`read_all_entries`) with :1165 `raise ValueError(f"invalid replay JSON at line {line_number}")` for a truncated last line and :1190-1207 `_parse_entry` whose four `model_validate` calls raise pydantic `ValidationError` (a `ValueError` subclass) plus bare `ValueError` at :1192 and :1207, and :1146-1148 recording that "Broader corruption hardening (mid-line partial writes, etc.) is deferred"; tests/api/test_replay_loader.py:539-559 (`test_list_replays_skips_corrupted_file_and_logs` — pins the doubled-write branch only, and is the source of the false confidence); AGENTS.md:50 ("No silent fallbacks. If something is invalid, raise."), AGENTS.md:76-110 craft rules 1, 2 and 6. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-loader-resilience`
**Depends on:** none (root)
**Section refs:** C-5 (audits/review-2026-08-19/B/collated-findings.md, the C-5 row, P1; full finding audits/review-2026-08-19/B/api.md §2 F1 and §5 "Gaps"; adversarial verdict audits/review-2026-08-19/B/verdicts.md verdict #6 — CONFIRMED, all three sub-claims including the exception typing; roadmap slot audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-0 row 0.4 and §2 credibility row 11 UNDERMINED; audits/review-2026-08-19/D/cross-track-map.md, the C-5 row, RR-free); api/replay_loader.py:703-729 (`list_replays`; the sole guard is `except ReplayLog.CorruptedFileError` at :727, logged at :728), :714-718 (the docstring claim "one bad replay no longer blocks the picker (Audit K-K-8, backend half)"), :731-748 (`load_replay` — the direct-fetch path this task deliberately leaves loud), :750-778 (`cost_summary`; the per-file reduction at :759 has no guard at all), :1683-1686 (`_file_summary`), :1688-1725 (`_read_summary`), :1727-1739 (`_metadata_view`), :1944-1969 (`_replay_paths`), :1985-1997 (`_resolve_path`); orchestrator/replay.py:1137-1187 (`read_all_entries`) with :1165 `raise ValueError(f"invalid replay JSON at line {line_number}")` for a truncated last line and :1190-1207 `_parse_entry` whose four `model_validate` calls raise pydantic `ValidationError` (a `ValueError` subclass) plus bare `ValueError` at :1192 and :1207, and :1146-1148 recording that "Broader corruption hardening (mid-line partial writes, etc.) is deferred"; tests/api/test_replay_loader.py:539-559 (`test_list_replays_skips_corrupted_file_and_logs` — pins the doubled-write branch only, and is the source of the false confidence); AGENTS.md:50 ("No silent fallbacks. If something is invalid, raise."), AGENTS.md:76-110 craft rules 1, 2 and 6
**Complexity:** Small
**Record impact:** none — read-side listing guard plus tests; no replay bytes, no rendered prompt bytes and no detector output move, so nothing here waits on the Phase-20 adopting record
**Measurement:** `uv run pytest tests/api/test_replay_loader.py -q` green with the three new corrupt-fixture cases; the review's repro directory (a copy of replays/samples/4p1i with one replay truncated by 40 bytes, one emptied, one row typed `"tick": "not-an-int"`) served through `TestClient` now returns 200 from `GET /replays` and `GET /eval/cost-summary` — both 500 at HEAD — with every healthy replay present and one WARNING line per skipped path

`api/replay_loader.py:714-718` promises that "one bad replay no longer blocks the
picker", and `list_replays` delivers that promise for exactly one corruption shape: the
doubled-write `ReplayLog.CorruptedFileError` Task 4.16 detects. Every other way a replay
file goes bad leaves the whole collection unreachable. `orchestrator/replay.py:1165`
raises a bare `ValueError` when the last line is a partial write — precisely the shape a
Ctrl-C'd, OOM-killed or disk-full tournament run leaves behind, because the runner writes
incrementally — and `_parse_entry` (:1190-1207) raises pydantic `ValidationError` for a
schema-invalid row. Neither is a `CorruptedFileError`, so both escape :727 and 500 the
listing. `cost_summary` (:750-778) has no guard at all, so the eval dashboard falls over
with it. The review's repro is decisive
(audits/review-2026-08-19/B/verdicts.md verdict #6): with one truncated, one emptied and
one type-invalid file in a copy of `replays/samples/4p1i`, `GET /replays` and
`GET /eval/cost-summary` both return 500 while `GET /replays/headless-seed-0` still
returns a perfectly healthy 21-tick game — healthy, and unreachable through the listing.
Deleting the truncated file alone still 500s; deleting the invalid one too restores a
200 with four items. One bad byte takes out the set.

The fix is a one-clause widening, and the review verified the typing detail that makes it
a one-clause fix: pydantic v2's `ValidationError` subclasses `ValueError`, so
`except (ReplayLog.CorruptedFileError, ValueError)` at the per-file boundary covers the
truncated line, the schema-invalid row and the unknown-`kind` row together. What matters
is where the boundary sits. This contract rules it explicitly: the LISTING and the COST
SUMMARY degrade — skip the file, log at WARNING with the path and the reason, keep
serving every healthy replay — while a DIRECT `load_replay` of the broken game id keeps
failing loud, exactly as it does at HEAD. Degradation on the collection view, fail-loud
on the item view: the picker stops being hostage to one file, and nobody can fetch a
half-written game and be told it is fine.

The empty-file leg is the one with no ruling anywhere, and it is the leg AGENTS.md:50
speaks to. A zero-byte file parses to zero entries, so `_read_summary` (:1688-1725)
reduces it to `total_ticks=0, winner=None`, `_metadata_view` (:1727-1739) advertises it
in the picker as an ordinary replay, and `cost_summary` counts it in `total_replays` —
diluting `mean_cost_per_replay` for the whole set. The review measured the shape
directly: `read_all_entries(replay-seed-2) -> OK, 0 entries`, and
`GET /replays/headless-seed-2 -> 200 ticks=1 meetings=0`. That is a silent fallback in a
repo whose own rule is "If something is invalid, raise. Do not paper over." A file that
contributes no replay records is not a 0-tick game; it is an unusable file, and this
contract treats it as one on every path.

Two things make this front-door work rather than housekeeping. The README hands a
stranger a tournament command, so the very first artifact a visitor produces is the one
that can break the picker — this is the X1 reproduction path
(audits/review-2026-08-19/D/cross-track-map.md, the C-5 row). And the existing test at
tests/api/test_replay_loader.py:539-559 is worse than no test: it pins the implemented
branch, is named as though it pins the docstring's general claim, and so certifies K-K-8
as fixed. Craft rule 2 applies — the replacement fixtures must be a gate that can fail,
demonstrated by narrowing the guard back to `CorruptedFileError` and watching all three
cases go red. Blast radius (craft rule 6) is small and checked: the only non-test
consumers of these two methods are `api/routes/replays.py:34-42`,
`api/routes/eval.py:183-184` (bare delegates, unchanged) and
`scripts/build_demo_bundle.py:279` (a skipped replay simply does not enter the bundle,
which is the wanted behaviour and is traceable through the WARNING line).

**Files in scope:**
- api/replay_loader.py; (list_replays / cost_summary / the summary reader: catch ValueError, skip zero-byte files, log at WARNING with the path)
- tests/api/test_replay_loader.py; (the three corrupt fixtures: truncated, empty, invalid-row → listing 200 with the healthy replays; the skipped path named in the log)

**Files NOT in scope:**
- orchestrator/replay.py (the reader's CorruptedFileError semantics and the recorded deferral at :1146-1148 are unchanged — the loader decides what to tolerate, the reader keeps raising)
- the routes (api/routes/replays.py, api/routes/eval.py: bare delegates; the fix is in the loader's listing/summary path, and no new exception handler is registered in api/main.py)
- frontend/ (no DTO, no copy, no version bump — the served shapes are identical)
- tests/api/fixtures/sample_replay.py (out of scope: build the three corrupt fixtures inline in the test from `write_sample_replay`'s output rather than adding a shared helper)
- scripts/build_demo_bundle.py (a downstream consumer of `list_replays`, read for blast radius only; the demo bundle belongs to the Pages task)
- replays/ (no committed bytes move; the four committed sets are healthy and must stay green unchanged)

**Definition of done:**
- [ ] `list_replays` and `cost_summary` guard the PER-FILE boundary with `except (ReplayLog.CorruptedFileError, ValueError)`, so a set directory holding a truncated replay, a zero-byte file and a schema-invalid row still lists every healthy replay and still computes a cost summary over the healthy subset — asserted in tests/api/test_replay_loader.py both at the loader level and through `TestClient` (HTTP 200, not 500), for both endpoints.
- [ ] `cost_summary`'s `total_replays` counts only the files it actually reduced, so `mean_cost_per_replay` is no longer diluted by a skipped file — pinned in tests/api/test_replay_loader.py against a directory of two healthy replays plus the three broken ones.
- [ ] Every skipped file is logged exactly once at WARNING naming its path and which class of failure it hit (doubled write / unparseable row / no replay records), distinguishable per class — pinned with `caplog` on the `api.replay_loader` logger; nothing is swallowed silently.
- [ ] A replay file that contributes no replay records — zero-byte, or containing only blank lines — is skipped by the listing and by the cost summary and is never served as a 0-tick game; pinned in tests/api/test_replay_loader.py (the review measured `GET /replays/headless-seed-2 -> 200 ticks=1 meetings=0` at HEAD).
- [ ] The direct-fetch contract is unchanged and now pinned: `load_replay` of the truncated id and of the schema-invalid id still raises out of the loader (a loud 500 through the route), and `load_replay` of the no-record file raises rather than synthesizing a game — so the listing's skip is degradation, never silence.
- [ ] The `list_replays` docstring (api/replay_loader.py:714-718) states the true behaviour: which failure classes are skipped, that they are logged, and that a direct fetch of the same id still fails loud; history is at most one trailing provenance line (craft rule 1), and the K-K-8 sentence no longer over-claims.
- [ ] The gate can fail (craft rule 2): narrowing the guard back to `except ReplayLog.CorruptedFileError` turns all three new cases red, and the PR quotes that run alongside the green one.
- [ ] The four committed sets are unaffected: `uv run pytest tests/api -q` green, including the existing `test_list_replays_skips_corrupted_file_and_logs` doubled-write case and the `list_replays` consumers in tests/api/test_view_model.py, test_leak.py and test_sets.py.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-20-loader-resilience` with a title like `task 20.4: the replay listing survives a corrupt or empty replay file`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing C-5 (audits/review-2026-08-19/B/collated-findings.md, the C-5 row, P1; full finding audits/review-2026-08-19/B/api.md §2 F1 and §5 "Gaps"; adversarial verdict audits/review-2026-08-19/B/verdicts.md verdict #6 — CONFIRMED, all three sub-claims including the exception typing; roadmap slot audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-0 row 0.4 and §2 credibility row 11 UNDERMINED; audits/review-2026-08-19/D/cross-track-map.md, the C-5 row, RR-free); api/replay_loader.py:703-729 (`list_replays`; the sole guard is `except ReplayLog.CorruptedFileError` at :727, logged at :728), :714-718 (the docstring claim "one bad replay no longer blocks the picker (Audit K-K-8, backend half)"), :731-748 (`load_replay` — the direct-fetch path this task deliberately leaves loud), :750-778 (`cost_summary`; the per-file reduction at :759 has no guard at all), :1683-1686 (`_file_summary`), :1688-1725 (`_read_summary`), :1727-1739 (`_metadata_view`), :1944-1969 (`_replay_paths`), :1985-1997 (`_resolve_path`); orchestrator/replay.py:1137-1187 (`read_all_entries`) with :1165 `raise ValueError(f"invalid replay JSON at line {line_number}")` for a truncated last line and :1190-1207 `_parse_entry` whose four `model_validate` calls raise pydantic `ValidationError` (a `ValueError` subclass) plus bare `ValueError` at :1192 and :1207, and :1146-1148 recording that "Broader corruption hardening (mid-line partial writes, etc.) is deferred"; tests/api/test_replay_loader.py:539-559 (`test_list_replays_skips_corrupted_file_and_logs` — pins the doubled-write branch only, and is the source of the false confidence); AGENTS.md:50 ("No silent fallbacks. If something is invalid, raise."), AGENTS.md:76-110 craft rules 1, 2 and 6), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
