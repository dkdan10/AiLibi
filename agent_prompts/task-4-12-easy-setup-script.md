# Agent Prompt — 4.12 Easy setup for non-technical users

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.12 — Easy setup for non-technical users, anchored to DESIGN.md §7, DESIGN.md §9. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-easy-setup-script`
**Depends on:** 4.11 merged
**Section refs:** DESIGN.md §7, DESIGN.md §9
**Complexity:** Small

Phase 4 is structurally complete: API + DTO inventory + replay loader +
React/Vite/Tailwind/PixiJS frontend + MapView (slice + full) +
MeetingView + ThoughtStream + BeliefMatrix + ReplayControls all
merged, mid-phase DTO audit passed, two audit-derived substrate fixes
(4.7, 4.9) landed clean. The only thing standing between the current
state and the Phase-closing UX acceptance session is the setup
friction: today a non-technical viewer needs to type three commands
across two terminals plus one env var to see the dashboard. This task
collapses that to one command and commits real-provider sample replays
so cloning the repo gives immediate viewable substrate.

Current flow (today):

```bash
bash scripts/setup_env.sh                                           # 1
AILIBI_REPLAY_DIR=./replays uv run uvicorn api.main:app             # 2 (terminal A)
cd frontend && npm run dev                                          # 3 (terminal B)
# then manually open http://localhost:5173
```

Target flow (after this task):

```bash
bash scripts/setup_env.sh                                           # 1 (one-time)
bash scripts/run_spectator.sh                                       # 2 (every time)
# browser opens automatically to a populated replay list
```

The single-command path is the load-bearing UX claim of Phase 4 —
"non-technical viewer can follow a saved replay end-to-end without
reading logs." If setup itself requires reading logs, the claim is
weaker. This task removes that contradiction.

**Real-provider sample replays.** The 50 `replay-seed-*.jsonl` files
at `/tmp/eval-50/` are the actual Phase 3 closing eval evidence (50/50
games, 38% impostor win rate, $0.018 mean cost, $0.886 total spend).
They cannot be cheaply regenerated — re-running the tournament costs
~$1 against the live Anthropic API, and Sonnet 4.6 may drift over
time, so the recorded transcripts are a frozen historical artifact.
Committing them to `replays/samples/` preserves the evidence and gives
cloners immediate substrate without paying for regeneration. Total
size: ~1.6 MB across 50 files; well under any GitHub threshold.

**Out of scope** (explicit decisions deferred):

- **Docker / docker-compose.** DESIGN.md §7 names docker-compose as
  a future option for "Postgres + api + frontend up with one command."
  Adding it would be ~2 hours additional lift and a new dependency
  surface. Defer to Phase 5+ if non-tech users hit native-dependency
  install friction with `uv` and `npm`.
- **Windows support.** macOS + Linux only for this script. Windows
  has different shell, different process management, different
  package manager idioms; bash script targeting cmd/PowerShell is
  a different task. Document Windows as unsupported in the script's
  leading comment.
- **Auto-install of dependencies.** If `uv` or `frontend/node_modules`
  is missing, the script prints a one-line pointer to
  `bash scripts/setup_env.sh` and exits non-zero. It does NOT
  auto-invoke setup_env.sh — installing dependencies without explicit
  consent is a footgun. (User-decided default 2026-05-27 in the
  design thread.)
- **Including `.audit.jsonl` files in the commit.** Those are internal
  leak-test packet logs from the observation firewall infrastructure,
  not user-facing artifacts. Excluded from `replays/samples/` and
  globally gitignored via `**/*.audit.jsonl`.
- **Process supervisor / systemd / launchd integration.** This is a
  dev-loop convenience script, not a production runner. Foreground
  bash with trap-on-EXIT cleanup is sufficient.

**Files in scope:**
- scripts/run_spectator.sh
- api/main.py
- tests/api/test_replay_dir_fallthrough.py
- README.md
- .gitignore
- replays/samples/replay-seed-0.jsonl … replays/samples/replay-seed-49.jsonl (50 files copied from /tmp/eval-50/; do NOT regenerate them — copy the existing artifacts to preserve their real-provider provenance)

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- api/schemas.py (DTOs frozen at 4.1)
- api/replay_loader.py (loader behavior frozen at 4.2; only the env-var resolution in main.py changes)
- api/routes/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md
- AGENTS.md
- pyproject.toml
- uv.lock
- tasks/
- agent_prompts/
- audits/
- open_issues.md
- scripts/setup_env.sh (consumed; not modified)
- scripts/check.sh (consumed; not modified)
- scripts/run_game.py
- scripts/run_tournament.py
- scripts/generate_prompts.py
- scripts/validate_task_docs.py
- tests/agents/
- tests/engine/
- tests/llm/
- tests/meetings/
- tests/observation/
- tests/orchestrator/
- tests/eval/
- tests/api/test_schemas.py
- tests/api/test_routes.py
- tests/api/test_leak.py
- tests/api/test_replay_loader.py
- tests/api/test_replays.py
- tests/api/test_eval.py
- tests/test_firewall.py
- frontend/src/
- frontend/package.json (locked at 4.3; no new deps)

**Definition of done:**
- [ ] **`replays/samples/` committed.** All 50 `replay-seed-*.jsonl` files copied from `/tmp/eval-50/`. NO `.audit.jsonl` files committed.
- [ ] **If `/tmp/eval-50/` is missing, do NOT regenerate.** Stop and report to the user. The artifacts must be located elsewhere (other scratch dir, backup, or the user's archive). Re-running the tournament against the live Anthropic API costs ~$1 AND produces non-identical transcripts (Sonnet 4.6 temperature > 0 + possible model drift), which destroys the Phase 3 evidence chain documented in [audits/audit-2026-05-26-0325-pre-phase-4-real-provider-eval.md](audits/audit-2026-05-26-0325-pre-phase-4-real-provider-eval.md). This is the most expensive failure mode for this task; treat the guardrail seriously.
- [ ] **`.gitignore` updated.** Three additions: `replays/*.jsonl` (user-generated replays in the parent dir are ignored), `!replays/samples/` (negation so committed samples survive), `**/*.audit.jsonl` (internal leak-test logs ignored everywhere).
- [ ] **`api/main.py` fallthrough resolution.** The `AILIBI_REPLAY_DIR` resolution at [api/main.py:16-17](api/main.py#L16) falls through in this priority order: (1) `$AILIBI_REPLAY_DIR` if set and non-empty, (2) `./replays/` if exists and contains at least one `replay-seed-*.jsonl` file, (3) `./replays/samples/` if exists and contains at least one matching file. If none resolve, fail with a clear startup error naming all three paths and suggesting `bash scripts/run_spectator.sh` or `uv run python scripts/run_game.py`.
- [ ] **Startup log of the resolved replay dir.** On successful resolution, `api/main.py` logs one line to stderr (or stdout via the FastAPI/uvicorn logger): `Serving replays from <resolved-path> (<N> replay-seed-*.jsonl found).`. This makes the slot-that-won visible whenever the developer mixes locally-generated replays in `./replays/` with the committed samples in `./replays/samples/` — without it, "why is the UI showing different replays than I expected?" is a silent guessing game.
- [ ] **Unit test `tests/api/test_replay_dir_fallthrough.py`** covers all four resolution paths: env var set, env var unset with `./replays/` populated, env var unset with only `./replays/samples/` populated, all three empty (asserts the error message). Uses pytest `tmp_path` + `monkeypatch` for filesystem isolation.
- [ ] **`scripts/run_spectator.sh` exists and is executable** (`chmod +x` recorded in the commit; verify with `git ls-files --stage scripts/run_spectator.sh`). The script does all of:
  - Print platform check: macOS + Linux supported; print warning and exit on other uname output.
  - Check `command -v uv >/dev/null` and `[ -d frontend/node_modules ]`. If either fails, print `Run bash scripts/setup_env.sh first.` and exit 1. Do NOT invoke setup_env.sh.
  - Check ports 8000 and 5173 are free (`lsof -nP -iTCP:8000 -sTCP:LISTEN`). If bound, print the PID and a `kill <pid>` suggestion, exit 1.
  - Start the API in the background: `uv run uvicorn api.main:app --port 8000 2>&1 | sed 's/^/[api] /' &` and capture the PID.
  - Start the frontend in the background: `(cd frontend && npm run dev) 2>&1 | sed 's/^/[ui] /' &` and capture the PID.
  - Trap on EXIT / INT / TERM: kill both PIDs.
  - Health-check loop: poll `curl -fsS http://localhost:8000/ >/dev/null 2>&1` until 200 or ~30s elapsed. Same for frontend at `http://localhost:5173/`. Print one progress line per second to stderr.
  - On both healthy: print `Open http://localhost:5173 in your browser.` Then attempt platform browser-open: `open` (macOS), `xdg-open` (Linux), fall back to printing-only on failure.
  - Print `Press Ctrl-C to stop.` on the line immediately after the open-in-browser message. Many users won't realize the script is foregrounded and will wonder why their terminal "froze" — this one line removes the confusion.
  - Wait on both child PIDs so the script stays in the foreground until Ctrl-C.
- [ ] **README "Watch a replay" section rewritten.** Collapse the 4-step block to 1 command. Add one paragraph describing what the user will see (50 sample replays from the Phase 3 closing eval, scrubber for ticks, meeting transcripts with ballots and contradictions, per-agent memory snapshots, suspicion heatmap). Keep the existing "Reproduce a game" determinism section unchanged.
- [ ] **Fresh-clone smoke test.** In a sibling directory: `git clone . ../ailibi-smoke && cd ../ailibi-smoke && bash scripts/setup_env.sh && bash scripts/run_spectator.sh`. Confirm the browser opens to a populated replay list with 50 entries. Paste terminal output (last ~30 lines) into `## Decisions` of the PR description.
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (new fallthrough test included).
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas.BeliefEntryView"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.main"`

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
Open a PR from branch `phase-4-easy-setup-script` with a title like `task 4.12: easy setup for non-technical users`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7, DESIGN.md §9), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
