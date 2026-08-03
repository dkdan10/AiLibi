# Agent Prompt — 6.1 Harden the deployment surface (docker-compose bind + CORS posture)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-6.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 6.1 — Harden the deployment surface (docker-compose bind + CORS posture), anchored to Audit C-C-1, C-C-2, C-C-4; DESIGN.md §1.1, §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-6.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-6-deploy-surface-hardening`
**Depends on:** none
**Section refs:** Audit C-C-1, C-C-2, C-C-4; DESIGN.md §1.1, §7
**Complexity:** Small

The spectator API serves the full GM view — every hidden-information field
(roles, kill attribution, vent state, rendered prompts) with no authentication,
by deliberate design for local single-user spectating. `scripts/run_spectator.sh`
correctly defaults its bind to `127.0.0.1`, but `docker-compose.yml` starts
uvicorn with `--host 0.0.0.0` (lines 13–14) and publishes the port to the host
(line 21), so `docker compose up` exposes every hidden field to the LAN
(audit C-C-1, the single highest-urgency operational finding). There is also no
CORS posture anywhere in `api/` (C-C-2): security relies entirely on the Vite
dev-server same-origin proxy, which exists only under `npm run dev`.

This task makes the local-only privilege model explicit and safe-by-default. It
binds docker-compose to the loopback interface, adds a documented CORS posture,
and records a deploy note stating that the unauthenticated GM-view API must sit
behind authentication and network isolation before any all-interfaces bind. The
rate-limiting concern (C-C-4) is documented as a pre-exposure requirement, not
coded — it lives behind the same "exposed beyond localhost" boundary and touches
`api/replay_loader.py`, which is owned by Task 6.6; do not edit that file here.

CORS handling is additive and must default to a closed posture: if a cross-origin
allowlist is configured (via an environment variable), install
`CORSMiddleware` with that explicit allowlist; if unset, install no permissive
middleware (same-origin static serving needs none). Never ship `allow_origins=
["*"]`.

**Files in scope:**
- docker-compose.yml
- api/main.py
- docs/deployment.md
- tests/api/test_app_config.py

**Files NOT in scope:**
- api/replay_loader.py (rate limiting is documented here, coded in Task 6.6 territory; do not edit the loader)
- api/routes/
- api/schemas.py
- README.md (README drift is Task 6.8)
- scripts/run_spectator.sh (already correct)
- frontend/

**Definition of done:**
- [ ] `docker-compose.yml` binds uvicorn to `127.0.0.1` (loopback) rather than `0.0.0.0`, OR documents in an adjacent comment that the all-interfaces bind is deliberate and gated behind a reverse proxy; the default committed state must not expose the GM view to non-loopback interfaces.
- [ ] `api/main.py` installs `CORSMiddleware` ONLY when a cross-origin allowlist is supplied via an environment variable (e.g. `AILIBI_CORS_ORIGINS`, comma-separated); when unset, no permissive CORS middleware is added. No `allow_origins=["*"]` anywhere.
- [ ] `docs/deployment.md` states: the API is an unauthenticated GM view; it is safe only on loopback or behind auth + network isolation; the production CORS posture (same-origin static serving needs no CORS, cross-origin requires the closed allowlist); and that an edge rate limiter and a short-TTL negative-lookup cache are prerequisites before any network exposure (C-C-4), to be implemented when the exposure path is built.
- [ ] `tests/api/test_app_config.py` asserts the default app installs no permissive CORS middleware, and that supplying `AILIBI_CORS_ORIGINS` installs a closed allowlist (no wildcard).
- [ ] No behavior change to any route handler or DTO; the local `npm run dev` + spectator flow is unaffected.
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
Open a PR from branch `phase-6-deploy-surface-hardening` with a title like `task 6.1: harden the deployment surface (docker-compose bind + cors posture)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing Audit C-C-1, C-C-2, C-C-4; DESIGN.md §1.1, §7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
