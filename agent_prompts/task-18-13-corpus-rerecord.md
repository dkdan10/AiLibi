# Agent Prompt — 18.13 The corpus re-record at baseline 6 (operator ~21–22h, $0)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.13 — The corpus re-record at baseline 6 (operator ~21–22h, $0), anchored to scripts/record_ml_corpus.sh (the pin block moves to the baseline-6 substrate); replays/ml_corpus/README.md; tasks/phase-17.md 17.9 (the runbook this reprises); audits/audit-phase-17-close.md §5 (the staleness rule this discharges). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-corpus-rerecord`
**Depends on:** 18.12
**Section refs:** scripts/record_ml_corpus.sh (the pin block moves to the baseline-6 substrate); replays/ml_corpus/README.md; tasks/phase-17.md 17.9 (the runbook this reprises); audits/audit-phase-17-close.md §5 (the staleness rule this discharges)
**Complexity:** Integration

The long pole, re-run at the adopted layer: 150-game 9p2i + 50-game 4p1i, seeds 1000+, the
same `seed % 5` split rule, freeze-path staging, MANIFEST provenance exact. Duration
honesty: baseline-5 ran ~14–15 h and the roll-call round adds ~36% meeting calls — plan
**~18–20 h** with checkpoint-push (commit-and-push completed seed ranges so a container
reclaim never loses a leg). The README refreshes end-to-end; the Q3 canary-denominator
restoration re-states (the corpus is again canonical from this record; the 18.12 samples are
the continuity anchor).

**Files in scope:**
- replays/ml_corpus/9p2i/ + replays/ml_corpus/4p1i/ (the re-recorded bytes + MANIFESTs + splits.json)
- replays/ml_corpus/README.md (full substrate refresh)
- scripts/record_ml_corpus.sh (the substrate pin flip + duration note)
- tests/eval/ (the corpus-pinned cells ONLY — test_watchability.py / test_watchability_reanchor.py corpus verdicts and the 18.1/18.2/18.3 instrument corpus pins; samples pins moved at 18.12)
- tests/training/test_bakeoff_harness.py; (corpus-derived re-pins ONLY — the constant flips are 18.14's)
- tests/training/test_surrogate_runner.py; (corpus-derived re-pins ONLY — the re-fit is 18.14's)
- tests/training/test_crew_options.py (corpus-derived re-pins ONLY)
- tests/training/test_goodhart_probe.py; (corpus-derived re-pins ONLY)
- tests/scripts/test_record_ml_corpus.py

**Files NOT in scope:**
- replays/samples/ (18.12's record — pinned)
- training/ (18.14/18.15 consume)

**Definition of done:**
- [ ] Both corpus sets recorded at baseline 6, validity gate PASS with exact provenance (model, versions, the ruled substrate flags, $0), byte-identical reconstruction, splits regenerated non-degenerate under the same rule.
- [ ] The README and the recorder script agree on every operative line (substrate, env, duration), the Q3 restoration is stated, and the conversion/deception-instrument reads over the new corpus are quoted in the PR.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The 17.9 runbook verbatim plus the checkpoint-push discipline. THIS IS A LOCAL OPERATOR
SESSION (the owner's machine, not a dispatch container — chosen to remove container-reclaim
risk from the ~22 h leg): run `bash scripts/setup_env.sh` first, export ONLY the recording
environment (`AILIBI_LLM_PROVIDER=featherless`, `AILIBI_PROMPT_SET=qwen3_6_27b`,
`AILIBI_SEED_MAX_ATTEMPTS=8`, `FEATHERLESS_API_KEY`) — the four graduated levers are
always-on in code and need no env; `AILIBI_IMPOSTOR_ROLL_CALL` must stay UNSET (the
recorder's preflight refuses it ON); work on the contract branch `phase-18-corpus-rerecord`
from current `main`. Checkpoint-push stays mandatory as crash/interruption insurance:
commit-and-push each completed seed range even though reclaim risk is gone. One arm the
local credential RE-OPENS: the annotated-tag half of the Q5 convention (dispatch
environments refuse tag pushes — the 16.14 limitation; locally
`git tag -a phase-18-corpus-<sha>` is available at the owner's discretion, with the
FROZEN-line shas remaining the operative guarantee either way). 4p1i first, then the 9p2i
long leg sharded across 2 staggered workers with jittered backoff. Context corrections from the 18.12
verification: the record's truth is `audits/audit-phase-18-baseline-6.md` — PR #300's BODY
quotes superseded first-cut numbers from before the vent-widening fix re-record; never cite
the PR body. Two cells this corpus gives their first powered read: the vent variant's
STRONG yield (samples read 6, one under the pre-registered [7,28] bracket — an adjudicated
near-miss; the corpus is the first large-N read) and the absence-prior top-churn (not
re-measured on the baseline-6 samples; last measurement is the gate's 4/75). The audit §2
false-vouch split (34 with grounded 14 / fabricated 4) is internally underdetermined as
printed — this corpus re-derivation states the partition cleanly. The `record_ml_corpus.sh`
relabel routed by PR #300 lands here.

## Integration risk

The mixed-date MANIFEST precedent applies across a multi-day session. Corpus-pinned
training tests move; re-pin only what this record moves and leave the bar/surrogate
constants to 18.14 (the 17.9/17.11 split, kept).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.tactical.learned.crew_forward"`
- `uv run python -c "import agents.tactical.learned.factory"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import eval.off_menu"`
- `uv run python -c "import eval.kill_craft"`
- `uv run python -c "import eval.deception_instruments"`

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
Open a PR from branch `phase-18-corpus-rerecord` with a title like `task 18.13: the corpus re-record at baseline 6 (operator ~21–22h, $0)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing scripts/record_ml_corpus.sh (the pin block moves to the baseline-6 substrate); replays/ml_corpus/README.md; tasks/phase-17.md 17.9 (the runbook this reprises); audits/audit-phase-17-close.md §5 (the staleness rule this discharges)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
