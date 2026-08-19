# Agent Prompt — 4.17 Refresh-samples workflow + verify-samples + MANIFEST

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.17 — Refresh-samples workflow + verify-samples + MANIFEST, anchored to DESIGN.md §9, DESIGN.md §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-refresh-samples-workflow`
**Depends on:** 4.16 merged
**Section refs:** DESIGN.md §9, DESIGN.md §11.4
**Complexity:** Medium

Phase 5 Task 5.8 (prompt regression test suite) needs a fixture system
that captures (prompt template version, seed, model response) tuples
and can be regenerated when prompt changes ship intentionally. Today
the only sample-management mechanism is "ran a tournament once, copied
files into `replays/samples/`." That's not a workflow; it's an artifact.

This task ships the workflow: `scripts/refresh_samples.sh` regenerates
samples with three modes, `scripts/verify_samples.sh` does a free
CPU re-play through the loader to catch state-hash drift without API
spend, and `replays/samples/MANIFEST.md` records provenance for every
sample so Phase 5 metric outputs can be attributed to a specific prompt
version + model snapshot.

**Three refresh modes:**

- `--full` — Re-run the full 50-game tournament; replaces all samples.
  Real-provider spend ~$1; takes ~3 minutes wall clock. Use when a
  Phase 5 prompt-version delta makes the existing samples stale.
- `--meetings` — Re-run only the 4 meeting-bearing seeds (22, 24, 26,
  49 in the current sample set; let the script derive these
  dynamically from `MANIFEST.md`). ~$0.10 spend; ~30s wall clock. Use
  when the only thing that changed is meeting-prompt-relevant.
- `--seeds N,N,N` — Re-run a specific subset. Custom spend. Use for
  one-off prompt-debug or regression-test-fixture generation.

**Verify-samples (CPU only, no API):**

`scripts/verify_samples.sh` walks every JSONL in `replays/samples/`,
loads it through `api.replay_loader.ReplayLoader`, and asserts the
state-hash chain reconstructs cleanly. If any sample's recorded
state-hash diverges from the engine-playback reconstruction, the
script fails loud with the sample id and the divergent tick. Detects
silent drift from engine changes that violate the byte-identity
contract.

**MANIFEST.md provenance:**

`replays/samples/MANIFEST.md` is a markdown table maintained by
`refresh_samples.sh`. Columns: seed, model id (e.g.
`claude-sonnet-4-6`), prompt template versions in play (the union of
`prompt_versions` maps across the sample's meetings, formatted as
`accusation_round.v2, crewmate_report.v1, ...`), refresh timestamp,
git commit at refresh time, total cost, decisive outcome
(`CREWMATES` / `IMPOSTORS` / `null`). The script appends a row per
sample on `--full` or `--meetings`; on `--seeds`, it updates the
matching rows.

**Out of scope** (explicit decisions deferred):

- **`MANIFEST.md` enforcement at load time.** This task ships the
  provenance log; reading it programmatically (e.g. asserting the
  current prompt version matches the manifest before computing a
  metric) is a 5.8 concern.
- **Cost projection / budget enforcement.** The script reports actual
  spend after the refresh; pre-flight budget check is a follow-up if
  refresh runs balloon in cost.
- **Per-replay re-record of specific LLM call responses.** Phase 5.8
  may want this for prompt regression fixtures, but it's a separate
  surface from the bulk-sample refresh — defer to 5.8 elaboration.

**Files in scope:**
- scripts/refresh_samples.sh
- scripts/verify_samples.sh
- replays/samples/MANIFEST.md
- tests/scripts/test_refresh_samples.py (or similar; verifies argparse + dry-run modes)
- tests/scripts/test_verify_samples.py
- README.md (one-paragraph addition under "Watch a replay" about the refresh workflow)

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/replay.py (frozen at 4.16)
- orchestrator/ everything else
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md
- pyproject.toml
- uv.lock
- tasks/
- agent_prompts/
- audits/
- open_issues.md
- replays/samples/*.jsonl (the sample contents themselves — do NOT regenerate as part of THIS task; the workflow is delivered, but the user runs it when needed)
- scripts/setup_env.sh
- scripts/check.sh
- scripts/run_game.py
- scripts/run_tournament.py (consumed; not modified beyond what 4.16 changes)
- scripts/run_spectator.sh
- scripts/generate_prompts.py
- scripts/validate_task_docs.py
- tests/agents/
- tests/engine/
- tests/llm/
- tests/meetings/
- tests/observation/
- tests/orchestrator/
- tests/api/
- tests/eval/
- tests/test_firewall.py

**Definition of done:**
- [ ] **`scripts/refresh_samples.sh` exists and is executable.** Implements `--full`, `--meetings`, `--seeds N,N,N` modes per the description above. Modes are mutually exclusive; passing more than one is an error. Default mode (no flags): print usage and exit non-zero.
- [ ] **Real-provider preflight.** Before any API call, the script verifies `ANTHROPIC_API_KEY` is set and prints the prefix (first 8 chars). Exits non-zero if unset.
- [ ] **Cost transparency.** After the refresh completes, the script prints total spend (sum of `LLMCallRecord.cost_usd` across all written replays). Captured in MANIFEST.md.
- [ ] **MANIFEST.md schema.** Markdown table with columns: `seed | model | prompt_versions | refreshed_at | git_sha | cost_usd | winner`. Table sorted by seed ascending. Script idempotent in the row-update path (running the same `--seeds 22` twice produces the same MANIFEST output).
- [ ] **`scripts/verify_samples.sh` exists and is executable.** Walks every `replays/samples/replay-seed-*.jsonl`, invokes `ReplayLoader.load_replay`, asserts the state-hash chain reconstructs without divergence. Failure mode: prints sample id + divergent tick + expected/actual hashes, exits non-zero.
- [ ] **`replays/samples/MANIFEST.md` committed** with rows for the existing 50 samples (the implementing agent generates this by inspecting the existing samples; do NOT re-refresh as part of THIS task).
- [ ] **README addition.** One paragraph under the "Watch a replay" section explaining the refresh workflow with one example command. Keep concise.
- [ ] **Unit tests via `pytest`.** Argparse coverage for refresh_samples (each mode parses correctly, mutually-exclusive flags error). Dry-run mode if implemented (`--dry-run` prints planned actions without API calls). Verify-samples can be tested against a fixture with a deliberately-corrupted state-hash; assert the script detects it.
- [ ] **Smoke run.** Run `bash scripts/verify_samples.sh` against the current `replays/samples/` directory; assert exit 0 (all 50 samples reconstruct cleanly under the current engine). Paste output into `## Decisions`.
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The `refresh_samples.sh` script wraps `scripts/run_tournament.py` (which 4.16 just hardened with `--force`). High-level shape:

```bash
#!/usr/bin/env bash
# scripts/refresh_samples.sh — illustrative

set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 --full | --meetings | --seeds N,N,N
  --full        Re-run all 50 sample seeds (~\$1, ~3 min)
  --meetings    Re-run only seeds that had meetings (~\$0.10, ~30s)
  --seeds X,Y   Re-run a specific subset
EOF
}

case "${1:-}" in
  --full)     seeds=$(seq 0 49 | tr '\n' ',') ;;
  --meetings) seeds=$(_extract_meeting_seeds_from_manifest) ;;
  --seeds)    seeds="${2:?Provide comma-separated seed list}" ;;
  *)          usage; exit 1 ;;
esac

# Preflight: API key required
: "${ANTHROPIC_API_KEY:?ANTHROPIC_API_KEY must be set for sample refresh}"
echo "Using API key prefix: $(echo "$ANTHROPIC_API_KEY" | cut -c1-8)"

# Run the tournament with --force; writes to replays/samples/
uv run python scripts/run_tournament.py \
  --seeds "$seeds" \
  --output-dir replays/samples \
  --force

# Update MANIFEST.md for each refreshed seed
python -m scripts._manifest_writer --seeds "$seeds"

# Print total cost
total=$(python -m scripts._manifest_writer --sum-cost-for-seeds "$seeds")
echo "Refresh complete. Total spend: \$${total}"
```

(The `scripts/_manifest_writer` helper is a small Python module — not a separate task — that reads the new replay JSONLs and writes/updates MANIFEST.md rows. Implementing agent picks the exact split between bash and Python.)

For `verify_samples.sh`:

```bash
#!/usr/bin/env bash
# scripts/verify_samples.sh — illustrative

set -euo pipefail

fail=0
for path in replays/samples/replay-seed-*.jsonl; do
  seed=$(basename "$path" | sed 's/replay-seed-\(.*\)\.jsonl/\1/')
  if ! uv run python -c "
from pathlib import Path
from api.replay_loader import ReplayLoader
ReplayLoader(Path('replays/samples')).load_replay('headless-seed-${seed}')
"; then
    echo "FAIL: seed ${seed}"
    fail=1
  fi
done

if [ "$fail" -eq 1 ]; then
  echo "Sample verification failed. Some samples have drifted from engine determinism."
  exit 1
fi
echo "All samples verified clean."
```

The verify script is the free safety net — it catches drift before any Phase 5 metric computation reads the sample and produces a wrong number.

MANIFEST.md initial structure (illustrative; implementing agent populates from actual sample inspection):

```markdown
# Sample Replay Manifest

Provenance for replays under `replays/samples/`. Updated by
`scripts/refresh_samples.sh`. See [Task 4.17] for the workflow.

| Seed | Model | Prompt Versions | Refreshed At | Git SHA | Cost (USD) | Winner |
|------|-------|-----------------|--------------|---------|------------|--------|
| 0    | claude-sonnet-4-6 | (none — no meetings) | 2026-05-26 | a1b2c3d | 0.0000 | CREWMATES |
| 22   | claude-sonnet-4-6 | accusation_round.v2, crewmate_report.v1, impostor_report.v1, vote_ballot.v1 | 2026-05-26 | a1b2c3d | 0.2080 | CREWMATES |
| ... (rows for each of 50 seeds) |
```

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay.ReplayLog"`
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
Open a PR from branch `phase-4-refresh-samples-workflow` with a title like `task 4.17: refresh-samples workflow + verify-samples + manifest`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §9, DESIGN.md §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
