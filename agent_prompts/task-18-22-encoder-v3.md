# Agent Prompt — 18.22 Encoder v3 + within-kind target resolution (free-policy family)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.22 — Encoder v3 + within-kind target resolution (free-policy family), anchored to audits/audit-phase-18-planning.md §4 (#14) + the dive findings (the PR #242 lexical-tie limit at policy_es.py:214-221; encoder gaps: witness-awareness, meeting-history, claimed-location); agents/tactical/features.py:88, 125-143, 176-187 (the versioned layout + golden pins); training/bakeoff/policy_es.py:97-106 (input-dim auto-resize). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-encoder-v3`
**Depends on:** 18.19, 18.30
**Section refs:** audits/audit-phase-18-planning.md §4 (#14) + the dive findings (the PR #242 lexical-tie limit at policy_es.py:214-221; encoder gaps: witness-awareness, meeting-history, claimed-location); agents/tactical/features.py:88, 125-143, 176-187 (the versioned layout + golden pins); training/bakeoff/policy_es.py:97-106 (input-dim auto-resize)
**Complexity:** Medium

The perception upgrade locked decision 5 sequenced here: an additive, versioned encoder v3
(the v2 layout untouched and still pinned) adding the deception-relevant channels the dive
priced — per-target witness-co-presence at decision time, meeting-history scalars (meetings
survived, prior ejection outcomes) fed from the meeting-concluded hook, and per-player
last-seen recency the belief slots do not carry — plus within-kind target resolution for
the masked head (per-target KILL scoring, closing the lexical-tie limit). Firewall-legal
throughout (agent-own packet + memory only); pure-Python; the golden layout test extends to
v3.

**Files in scope:**
- agents/tactical/features.py (the additive v3 encoder + golden layout)
- agents/memory/store.py (the meeting-history memory channel the v3 encoder reads — populated at the existing deterministic meeting-conclusion fold; today `absorb_meeting_evidence` records no per-meeting outcome history the encoder can consume)
- agents/memory/working.py (the channel's typed carrier, if the design places it there)
- orchestrator/game.py; (the meeting-concluded hook payload ONLY — `_notify_meeting_concluded`/`note_meeting_concluded` carry the public meeting outcome the memory channel folds; today the hook updates only the emergency tracker)
- training/crew/scorer.py; (the `_CrewCandidateAgent.note_meeting_concluded` signature widening ONLY — the wrapper implements the exact current keyword-only signature and would TypeError on the widened payload)
- training/env.py; (the same hook-signature widening ONLY — its wrapper at :454 also implements the exact current signature)
- agents/tactical/learned/; (the learned wrappers' hook signature widening ONLY, if they override the hook)
- training/bakeoff/policy_es.py (the per-target head + v3 selection)
- tests/agents/test_memory_meeting_history.py (new — the channel's fold fixtures, firewall-legality)
- tests/training/test_bakeoff_harness.py; (encoder/head fixtures ONLY — the v3 golden pins, mask/tie fixtures)

**Files NOT in scope:**
- agents/tactical/learned/forward.py + the committed champion weights (the shipping champion's forward pass and artifact are untouched — only wrapper hook SIGNATURES may move, per the in-scope entry)
- training/bakeoff/utility_es.py (the menu family does not move)

**Definition of done:**
- [ ] Encoder v2 output is byte-identical everywhere (golden pins unchanged); v3 is additive, versioned, firewall-legal (no engine/other-agent state — the leak-style provenance test extends), with its layout golden-pinned.
- [ ] The per-target head resolves within-kind ties by learned score (lexical fallback only on exact score ties), fixture-pinned including the masked-legality invariant; a v3-featured policy-es trains end-to-end on the miniature budget.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Meeting-history needs a small memory-side channel populated from the concluded hook before
the encoder can read it — keep that channel in the agent's own memory store (firewall-clean
by construction) and quantize everything through the established integer-grid helpers (the
§6.3 residue hazard).

## Public types this task introduces
- `agents.tactical.features.encode_features_v3`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.conviction.serving"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.conviction.model"`
- `uv run python -c "import training.conviction.dataset"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.tactical.learned.crew_forward"`
- `uv run python -c "import agents.tactical.learned.factory"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import eval.off_menu"`
- `uv run python -c "import eval.kill_craft"`
- `uv run python -c "import eval.deception_instruments"`
- `uv run python -c "import training.coevo.factory"`
- `uv run python -c "import training.coevo.rollout"`

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
Open a PR from branch `phase-18-encoder-v3` with a title like `task 18.22: encoder v3 + within-kind target resolution (free-policy family)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §4 (#14) + the dive findings (the PR #242 lexical-tie limit at policy_es.py:214-221; encoder gaps: witness-awareness, meeting-history, claimed-location); agents/tactical/features.py:88, 125-143, 176-187 (the versioned layout + golden pins); training/bakeoff/policy_es.py:97-106 (input-dim auto-resize)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
