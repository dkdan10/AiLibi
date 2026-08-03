# Agent Prompt — 18.12 The adopting record: baseline 6 (operator ~6–7h, $0)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.12 — The adopting record: baseline 6 (operator ~6–7h, $0), anchored to audits/audit-phase-16-close.md (the baseline-5 adopting-record runbook this reprises); eval/watchability.py:755-762 (the baseline-5 floor block the new block sits beside); audits/audit-phase-17-close.md §3 (the corpus canary anchors the pre-registration reads); the 18.11 ruling (which arms flip). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-baseline-6-record`
**Depends on:** 18.1, 18.2, 18.3, 18.4, 18.11
**Section refs:** audits/audit-phase-16-close.md (the baseline-5 adopting-record runbook this reprises); eval/watchability.py:755-762 (the baseline-5 floor block the new block sits beside); audits/audit-phase-17-close.md §3 (the corpus canary anchors the pre-registration reads); the 18.11 ruling (which arms flip)
**Complexity:** Integration

The meeting-layer record. Flip the ruled arms to unconditional (graduation per the 16.17
slate pattern — the flags become always-on for the shipped arms; unshipped arms stay inert),
re-record `replays/samples/` (9p2i + 4p1i, 50 seeds each) at the new layer, pin the
baseline-6 floor block from the recorded bytes, execute the absence-prior graduation
component of the 18.11 ruling, and write the record audit with the §0 pre-registration
read against the phase-17 close's corpus-denominator anchors. Duration honesty: the
roll-call round adds ~36% meeting calls — plan ~6–7 h. Every byte-coupled committed pin
this record moves is re-pinned in the same PR.

**Files in scope:**
- meetings/manager.py; (the ruled arms' graduation flips ONLY — mechanism bodies froze at Wave 1)
- meetings/transcript.py; (same)
- agents/strategic/prompts/; (same)
- orchestrator/game.py; (the `prompt_versions_for_set` registry graduation flip ONLY — if the impostor-answer arm ships, the variant versions become the default-served entries)
- scripts/refresh_samples.sh (the substrate-lever preflight: the wrapper preflights only prompt/model today — it gains a positive check that the live lever slate equals the RULED shipped/unshipped state, refusing a stale `AILIBI_*` export BEFORE any seed of the ~6-7h record stages)
- tests/scripts/test_refresh_samples.py (the preflight fixtures)
- scripts/record_ml_corpus.sh; (the `REQUIRED_PROMPT_VERSIONS` re-lock ONLY — the recorder's version pin must move WITH the registry or check.sh fails at this PR; the duration/guard edits stay 18.13's)
- tests/scripts/test_record_ml_corpus.py; (the registry-equality pin re-lock ONLY)
- tests/scripts/test_manifest_writer.py (the MANIFEST substrate-flags string pins — the new true flags in recorded bytes)
- agents/memory/beliefs.py (the absence graduation component if ruled)
- orchestrator/replay.py; (the graduation reclassification ONLY — shipped levers move out of `TOGGLEABLE_SUBSTRATE_FLAG_KEYS` so baseline-6 recordings stamp them always-on, never env-toggleable; the snapshot/key ordering follows)
- tests/orchestrator/ (the reclassification pins)
- replays/samples/9p2i/ + replays/samples/4p1i/ (the baseline-6 record)
- eval/watchability.py; (the baseline-6 floor block)
- audits/audit-phase-18-baseline-6.md (new: the record audit)
- tests/eval/; (the byte-coupled committed-bytes re-pins this record moves, incl. the 18.1/18.2/18.3 instrument pins)
- tests/agents/; (the absence counterfactual + prompt-registry re-pins)
- tests/meetings/; (the graduation-flip re-pins)

**Files NOT in scope:**
- replays/ml_corpus/ (18.13's record)
- training/ (18.14 consumes; this task records)

**Definition of done:**
- [ ] Both samples sets recorded at the ruled layer, validity gate PASS (`--expected-model Qwen/Qwen3.6-27B --require-zero-cost`), byte-identical reconstruction under a bare environment, substrate flags in recorded bytes matching the ruling exactly.
- [ ] The baseline-6 floor block is pinned from these bytes with the derivation self-consistency check (referee PASS at exact floor equality on its own record), and the record audit quotes the funnel/V&J/deception-instrument before/after against baseline 5 with the §0 pre-registered canary bands on the corpus denominators.
- [ ] The absence-prior component of the ruling is executed (graduated per the ratified bar, or its stay-OFF restated with the probe cells named).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

THE RULED SLATE (gate audit §9, CREW-ONLY): exactly FOUR levers graduate — the roll-call
round, the endpoint exemption, the vent variant, and the absence prior. `impostor_roll_call`
STAYS a default-OFF toggle, so this contract's "if the impostor-answer arm ships" clauses
read FALSE: the `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS` fold and the game.py registry flip
DO NOT execute, and the recorder `REQUIRED_PROMPT_VERSIONS` re-lock is a no-op (the registry
does not move) — the preflight leg still lands (slate = four ON + impostor_roll_call OFF).
The record audit carries three coordination corrections when quoting the gate's cells (the
17.17 correction pattern — the ratified memo is not rewritten): (a) the CREW-ONLY coverage
z re-computes to +7.07 on the stated n=75 (the quoted +6.93 back-solves to n=72;
conservative, verdict-neutral); (b) the impostor-win z −2.08 is the memo's declared
one-sample-vs-0.36 convention — the pooled two-proportion read vs 18/50 is −1.79
(immaterial: the 0.16 < 0.20 bright-line miss and the self-flag clause decided bar (c));
(c) memo §6's "each bound to its home-module resolver by identity" holds for 3 of 4 — the
`impostor_roll_call` entry is a deliberate local mirror (loader import-cost isolation).
Watch item during the record: the validity gate's `cost_and_provenance_exact` has a known
blindness around the `(deadline_default)` synthetic marker (routed by PR #299 to a future
eval/ contract, unassigned — the close inherits it if unclaimed); a seed whose opening
defaults is a FAILED recording and re-records, per the standing rule. Shipping-layer
expectations for the §0 sanity read are the gate audit §7's CREW-ONLY cells (coverage 1.00,
impostor win 0.32, conversion 0.525) with the vent variant's yield expected in the [7, 28]
bracket — its first live measurement in the shipping combination is THIS record.

The 16.17 close-record runbook is the template (graduation flips + record + floor pins +
byte-coupled re-pin sweep in one PR). Record 4p1i first to validate the pipeline, then the
9p2i leg. The Q5 provenance convention applies (recording sha back-filled on merge; the tag
arm may need the owner's machine).

## Integration risk

The widest byte-coupled re-pin sweep of the phase: every committed-bytes pin over
`replays/samples/` moves (funnel, V&J, conversion partition, absence counterfactual,
deception instruments, kill-craft). Budget the re-pin pass explicitly and run the full
suite before the record commit is cut — a stale pin discovered post-merge is a two-artifact
seam.

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

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-18-baseline-6-record` with a title like `task 18.12: the adopting record: baseline 6 (operator ~6–7h, $0)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-16-close.md (the baseline-5 adopting-record runbook this reprises); eval/watchability.py:755-762 (the baseline-5 floor block the new block sits beside); audits/audit-phase-17-close.md §3 (the corpus canary anchors the pre-registration reads); the 18.11 ruling (which arms flip)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
