# Agent Prompt — 19.13 Proof above the fold + the static demo artifact

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.13 — Proof above the fold + the static demo artifact, anchored to audits/audit-phase-19-triage.md §7 item 14 [C]; docs/deployment.md:10-33 (the unauthenticated-GM-view trust boundary — preserved verbatim in spirit); docker-compose.yml:31-37 (loopback binding); the verified gap: `vite build` output is never served, no StaticFiles mount, no screenshot/GIF anywhere in README. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-demo-artifact`
**Depends on:** 19.1, 19.9, 19.10, 19.16
**Section refs:** audits/audit-phase-19-triage.md §7 item 14 [C]; docs/deployment.md:10-33 (the unauthenticated-GM-view trust boundary — preserved verbatim in spirit); docker-compose.yml:31-37 (loopback binding); the verified gap: `vite build` output is never served, no StaticFiles mount, no screenshot/GIF anywhere in README
**Complexity:** Medium

The strongest surface has no visual proof and no shippable artifact. Two deliverables:
(a) proof above the fold — a screenshot and a short capture (≤60 s GIF/video) of the
featured 9p2i journey placed at the top of README with three reproducible-claim commands
under them; (b) `scripts/build_demo_bundle.py` — a self-contained static demo: the built
frontend plus pre-baked JSON for the featured replays only, no API process, no GM
surface, playable from any static file server. The client gains a static-data mode (a
data-source seam reading pre-baked `./data/*.json` when built for the bundle).
`docs/deployment.md` documents the bundle as the ONLY sanctioned public artifact and
keeps the live API loopback-only; binding `0.0.0.0` remains forbidden.

**Files in scope:**
- README.md
- docs/deployment.md
- docs/media/ (new — the committed captures)
- scripts/build_demo_bundle.py (new)
- frontend/src/api/client.ts; (the static-data seam only)
- frontend/vite.config.ts; (the bundle build mode, if needed)
- tests/scripts/test_build_demo_bundle.py (new)

**Files NOT in scope:**
- api/ (no StaticFiles mount — the bundle replaces the need; the live API's posture is unchanged)
- docker-compose.yml (loopback stance stands)

**Definition of done:**
- [ ] `scripts/build_demo_bundle.py` builds offline from committed bytes into one directory; opening it via a static server plays the featured journey end-to-end (pause → finale) with zero API calls (test asserts no non-static fetch paths in bundle mode).
- [ ] README opens with the capture + screenshot and three commands that reproduce top claims (determinism double-run, verify_samples, the spectator boot); media files are committed at reasonable size (< a few MB total).
- [ ] deployment.md documents the bundle path and restates the loopback boundary; the words that forbid exposing the GM API survive.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The seam in `client.ts` should be one base-resolution function (static mode ⇒ relative
`./data/…`), not a parallel client. Bake only the featured seeds + the picker/rubric
metadata they need — the bundle's weight budget is a demo, not the corpus. Capture the
GIF with the headless Chromium already in the environment; keep it under ~15 s of
footage at modest resolution to respect the media budget.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-19-demo-artifact` with a title like `task 19.13: proof above the fold + the static demo artifact`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 14 [C]; docs/deployment.md:10-33 (the unauthenticated-GM-view trust boundary — preserved verbatim in spirit); docker-compose.yml:31-37 (loopback binding); the verified gap: `vite build` output is never served, no StaticFiles mount, no screenshot/GIF anywhere in README), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
