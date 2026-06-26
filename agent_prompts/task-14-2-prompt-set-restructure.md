# Agent Prompt — 14.2 Per-model prompt-set restructure (pin the 9B set byte-identically)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.2 — Per-model prompt-set restructure (pin the 9B set byte-identically), anchored to DESIGN.md §11.4 (replay provenance / prompt_versions); agents/strategic/prompts/loader.py; orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS`, `:266-271`); owner decision 2026-06-25 (per-model prompt sets). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-prompt-set-restructure`
**Depends on:** none
**Section refs:** DESIGN.md §11.4 (replay provenance / prompt_versions); agents/strategic/prompts/loader.py; orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS`, `:266-271`); owner decision 2026-06-25 (per-model prompt sets)
**Complexity:** Medium

Introduce a per-model prompt-set directory layer so the right templates load for the right model. Move the
four existing templates VERBATIM (no content edit) into `agents/strategic/prompts/qwen3_5_9b/`, pinning them
as the frozen 9B reference set. Parameterize the loader by a `prompt_set` selector (env `AILIBI_PROMPT_SET`,
default `qwen3_5_9b` for backward-compatible rendering), building the Jinja `Environment` /
`FileSystemLoader` against the selected subdir. Add a per-set version registry ALONGSIDE the existing
`DEFAULT_PROMPT_VERSIONS`, keeping that symbol and the 9B set's recorded values (`crewmate_report.v8`,
`accusation_round.v9`, `impostor_report_v6`, `vote_ballot/v7`) byte-identically unchanged — so the committed
replays AND the existing `prompt_versions` assertions in `tests/orchestrator/` + `tests/scripts/` stay green
without edits. A new-model replay is distinguished by its OWN version strings plus the recorded model id, not
by prefixing the 9B set's keys/values. Because the move is content-preserving and the 9B recorded metadata is
unchanged, the committed 4p1i/9p2i samples reconstruct byte-identical with ZERO re-record. The prompt SET
(templates) is orthogonal to the 13.5 substrate-flag config: 13.5 changed no `.j2` and bumped no version, so
the byte-identical pin is independent of which substrate flags are ON (the corrected substrate is a
render-INPUT dimension, handled in 14.4/14.7, not a template change).

**Files in scope:**
- agents/strategic/prompts/qwen3_5_9b/crewmate_report.j2 (moved verbatim from the flat path)
- agents/strategic/prompts/qwen3_5_9b/impostor_report.j2 (moved verbatim)
- agents/strategic/prompts/qwen3_5_9b/accusation_round.j2 (moved verbatim)
- agents/strategic/prompts/qwen3_5_9b/vote_ballot.j2 (moved verbatim)
- agents/strategic/prompts/loader.py (the `prompt_set` selector + per-set Environment resolution; the template-name constants stay, the directory varies)
- orchestrator/game.py (add a per-set version registry alongside `DEFAULT_PROMPT_VERSIONS`; the 9B set's recorded `prompt_versions` keys/values are unchanged; additive only — preserve the merged 13.5 flag wiring, e.g. `unfreeze_memory_enabled()` / `ENV_UNFREEZE_MEMORY` at `:714-735` and the testimony read at `:1656`)
- tests/agents/test_prompt_loader.py (new or extended: the default set resolves to `qwen3_5_9b` and renders byte-identically; a second set loads; an unknown set fails loud)

**Files NOT in scope:**
- the four template BODIES (content frozen — pure move, zero byte change; any rewording is 14.5's new set)
- replays/samples/ (no re-record; the move must not require one)
- meetings/manager.py + agents/strategic/reasoner.py (call sites consume the loader callables unchanged)
- llm/ (provider work is 14.1)

**Definition of done:**
- [ ] The four templates live under `agents/strategic/prompts/qwen3_5_9b/` with byte-identical content; the `qwen3_5_9b` set renders byte-identically to the pre-move templates (a rendered-output equality test pins this).
- [ ] The loader takes a `prompt_set` selector defaulting to `qwen3_5_9b` (via `AILIBI_PROMPT_SET`); an unknown set raises (no silent fallback); a second (empty-stub) set is loadable to prove the seam.
- [ ] A per-set version registry is added alongside `DEFAULT_PROMPT_VERSIONS`; the 9B set's recorded `prompt_versions` keys/values are byte-identically unchanged, so the existing assertions in `tests/orchestrator/test_replay_meetings.py`, `tests/orchestrator/test_meeting_integration.py`, and `tests/scripts/test_manifest_writer.py` stay green WITHOUT edits; committed 4p1i + 9p2i reconstruct byte-identical with NO re-record (`scripts/verify_samples.sh` + `eval/prompt_regression.py` exact-match hold).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Keep template bytes identical — this is a `git mv` plus a loader/registry change, nothing more. The loader's
`_TEMPLATE_DIR` (`loader.py:57`) becomes per-set: resolve `prompt_set` to a subdir and build the
`FileSystemLoader` against it; the `*_TEMPLATE` filename constants are unchanged. Keep `DEFAULT_PROMPT_VERSIONS`
(`orchestrator/game.py:266-271`) as the 9B default mapping with its EXACT current values and add a registry
alongside (e.g. `PROMPT_VERSION_SETS = {"qwen3_5_9b": DEFAULT_PROMPT_VERSIONS, ...}`) that the runner selects
by active set. Do NOT prefix or reformat the 9B set's keys/values — `tests/orchestrator/test_replay_meetings.py:390-415`,
`tests/orchestrator/test_meeting_integration.py:2320`, and `tests/scripts/test_manifest_writer.py` pin them and
the committed replays store them verbatim; provenance for a new set comes from its own version strings + the
recorded model id. Determinism is the acceptance bar:
reconstruction reads recorded prompt bytes, so a content-preserving move keeps the committed samples valid —
prove it with `verify_samples` rather than asserting it.

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-14-prompt-set-restructure` with a title like `task 14.2: per-model prompt-set restructure (pin the 9b set byte-identically)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.4 (replay provenance / prompt_versions); agents/strategic/prompts/loader.py; orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS`, `:266-271`); owner decision 2026-06-25 (per-model prompt sets)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
