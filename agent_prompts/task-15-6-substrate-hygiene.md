# Agent Prompt — 15.6 Substrate hygiene: latent hazards, dead code, single-homed constants, firewall contracts

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.6 — Substrate hygiene: latent hazards, dead code, single-homed constants, firewall contracts, anchored to tasks/post-phase-14-clean-up.md H6; audits/post-phase-14-pause.md §3 (dead StrategicReasoner, constant homing, import contracts), §4.1 (the raw-vs-rendered [0.595, 0.60) band); meetings/manager.py:2486-2498 (the redirect guard); eval/_suspicion_parse.py:54 (the deliberate re-declaration). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-substrate-hygiene`
**Depends on:** 15.4
**Section refs:** tasks/post-phase-14-clean-up.md H6; audits/post-phase-14-pause.md §3 (dead StrategicReasoner, constant homing, import contracts), §4.1 (the raw-vs-rendered [0.595, 0.60) band); meetings/manager.py:2486-2498 (the redirect guard); eval/_suspicion_parse.py:54 (the deliberate re-declaration)
**Complexity:** Integration

Close the known latent hazards before the phase builds on the surfaces they sit in. Four items, each
small, bundled because they share files with each other and nothing else. (1) **The
raw-vs-rendered gate band:** the ballot-redirect guard recomputes the §4.6 verdict from RAW suspicion
floats while the prompt renders `"%.2f"` — a raw value in `[0.595, 0.60)` displays as 0.60 (the model
reads MUST-vote) while the guard reads MUST-skip; make guard and render agree (compare on the rendered
2dp value), pinned by fixtures across the band. (2) **Single-home the manager surface `agents/` imports:**
`DEFAULT_SKIP_CONFIDENCE_THRESHOLD` lives inside 3-KLoC `meetings/manager.py` and is imported UPWARD by
`agents/` (`crewmate_policy.py:86`) — and so are the render-contract types: `agents/strategic/prompts/
loader.py:76-81` imports `ReportPromptRenderer`, `StatementPromptRenderer`, `SuspicionEntry`, and
`VotePromptRenderer` from `meetings.manager`, so re-homing the constant alone would NOT make the
`agents ↛ meetings.manager` contract satisfiable. Move the constant to a new leaf
`meetings/constants.py` AND the four render-contract types to a new leaf `meetings/render_contract.py`
(pure typing/pydantic surface, no manager import), update both importers (`manager.py` re-exports may
remain for internal use; `agents/` must import only the leaves), and add the pin test the pause audit
asked for: eval's deliberately re-declared `SKIP_SUSPICION_THRESHOLD` must equal the threshold the
current baseline was recorded under. (3)
**Delete the dead `StrategicReasoner` island** (~2.7 KLoC: `agents/strategic/reasoner.py`,
`agents/strategic/output_schemas.py`, its 1820-line test) — instantiated only by its own test, never by
production, and it reads as a live alternate meeting path to every explorer; the triggered-LLM design
idea stays recorded in DESIGN.md §4 for a future phase, but the unwired code goes. (4) **Add the two
clean import contracts + de-stale AGENTS.md:** `observation ↛ agents/meetings/llm` and (now enabled by
item 2) `agents ↛ meetings.manager` in `.importlinter`; and fix AGENTS.md's stale doctrine — the
canonical eval provider is Featherless `Qwen/Qwen3-32B` (not Ollama `qwen3.5:9b`), and the GitHub-
tooling section's absolute claims are rewritten environment-neutral (the current text asserts `gh` is
always available and MCP GitHub tools always fail — false in at least one active dispatch environment).

**Files in scope:**
- meetings/constants.py (new: the gate constant's single home)
- meetings/render_contract.py (new: the render-Protocol + SuspicionEntry leaf home)
- meetings/manager.py (redirect-guard band region + constant/render-contract re-home — disjoint from 15.4's validation region and 15.5's vote-surface region)
- agents/strategic/prompts/loader.py (import the render contract from meetings.render_contract + scrub the stale StrategicReasoner docstring reference at :5; 15.5's kwarg region comes later)
- agents/strategic/prompts/__init__.py (scrub the stale StrategicReasoner docstring reference at :6)
- llm/budgeted_client.py (module docstring reference at :3 only — the last live `StrategicReasoner` mention outside the island and the two prompt-module docstrings)
- agents/tactical/crewmate_policy.py (import the constant from meetings.constants)
- agents/strategic/reasoner.py (DELETE)
- agents/strategic/output_schemas.py (DELETE)
- tests/agents/test_strategic_reasoner.py (DELETE)
- .importlinter (two firewall contracts + the root/config change they require — `meetings` and `llm` must become checkable via root_packages or include_external_packages, else lint-imports errors before evaluating the contracts; 15.8 extends the SAME root_packages block later, strictly behind its dependency edge on this task)
- meetings/schemas.py (stale output_schemas docstring pointer region at :20 — behind the 15.4 edge; the doc currently directs contributors to re-export new strategic types in the module this task deletes)
- AGENTS.md (provider + GitHub-tooling de-stale)
- tests/meetings/test_manager_gate_band.py (new: the [0.595, 0.60) fixtures)
- tests/eval/test_suspicion_parse_pin.py (new: the eval-constant pin)

**Files NOT in scope:**
- eval/_suspicion_parse.py (the re-declaration is deliberate and stays; it gets a PIN TEST, not an import)
- meetings/voting.py (tally untouched; it receives the threshold as a parameter already)
- DESIGN.md + AGENT_IMPLEMENTATION.md (owner-side; the generator bars task agents from them)
- agents/strategic/prompts/qwen3_32b/ and the other template-set directories (template text belongs to 15.4/15.5, and template bodies are provenance-versioned — the retired `qwen3_5_9b` set's stale prose comments (its vote_ballot.j2 mentions the deleted `output_schemas` module; its impostor_report.j2 says "strategic reasoner" in lowercase prose) stay frozen rather than forcing a pointless version bump on a retired set; the grep-zero DoD is on the literal `StrategicReasoner` symbol, which no template contains)

**Definition of done:**
- [ ] Guard-vs-render agreement: for raw suspicion values across `[0.55, 0.65]` including the
  `[0.595, 0.60)` band, the redirect guard's verdict equals the rendered-value verdict (fixture-pinned);
  committed sets still byte-verify (reconstruction re-feeds recorded actions, so OFF-path bytes are
  untouched — asserted by `verify_samples.sh`).
- [ ] `DEFAULT_SKIP_CONFIDENCE_THRESHOLD` has exactly one definition home (`meetings/constants.py`);
  `meetings/manager.py` and `agents/tactical/crewmate_policy.py` import it; the eval pin test fails if
  eval's re-declared threshold ever diverges from the constants home.
- [ ] The render-contract types (`ReportPromptRenderer`, `StatementPromptRenderer`, `SuspicionEntry`,
  `VotePromptRenderer`) live in `meetings/render_contract.py`; `agents/strategic/prompts/loader.py`
  imports NOTHING from `meetings.manager` (a grep-zero assertion in the test suite, plus the KEPT
  contract).
- [ ] The StrategicReasoner island is deleted; a repo-wide grep for `StrategicReasoner` returns zero
  references in LIVE code — imports, instantiations, and the stale docstring mentions in
  `agents/strategic/prompts/loader.py:5` / `agents/strategic/prompts/__init__.py:6` /
  `llm/budgeted_client.py:3` (historical mentions in closed task docs and audits stay, and the
  provenance-frozen template bodies contain only lowercase prose, never the symbol); the suite
  passes without it.
- [ ] `uv run lint-imports` reports every configured contract KEPT, including the two added here
  (`observation ↛ agents/meetings/llm`, `agents ↛ meetings.manager`) — three contracts alongside the
  pre-existing `agents ↛ engine`; 15.8 adds the fourth (`agents ↛ training`) strictly AFTER this task
  lands, behind the dependency edge that exists to serialize the shared root_packages
  block. The config change this requires is part of the task:
  today's root_packages (`agents, engine, observation`) cannot express a forbidden `meetings.manager` /
  `llm` target — lint-imports errors on external forbidden modules — so `meetings` and `llm` join
  root_packages (or `include_external_packages` is set), verified by the KEPT run.
- [ ] `meetings/schemas.py`'s module docstring no longer directs contributors to re-export strategic
  output types in the deleted `agents/strategic/output_schemas.py`.
- [ ] AGENTS.md names Featherless/`Qwen/Qwen3-32B` as the canonical eval provider and describes GitHub
  tooling capability-neutrally (try `gh`, fall back to the environment's GitHub integration; no absolute
  claims about either).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Keep both new modules leaves: `meetings/constants.py` stdlib-only, `meetings/render_contract.py`
typing/pydantic/schemas-only (Protocols and the `SuspicionEntry` DTO are pure surface — moving them is
mechanical; `meetings/manager.py` may import them back and re-export for internal callers, but the
dependency direction `agents → leaf` is what makes the `agents ↛ meetings.manager` contract
satisfiable). For the band fix, prefer quantize-then-compare (round the raw float to the rendered 2dp
grid before the gate comparison) over widening the gate — it makes guard and model read the same number
by construction. The deletion is mechanical but verify the island's edges first: `rg -n
"StrategicReasoner|output_schemas"` across the tree (ripgrep, per the repo tooling doctrine — not
recursive grep), including docs and task-doc Public-types claims
from old phases (historical claims in closed phase docs stay — only live code references must go to
zero).

## Public types this task introduces
- `meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD`
- `meetings.render_contract.ReportPromptRenderer`
- `meetings.render_contract.StatementPromptRenderer`
- `meetings.render_contract.SuspicionEntry`
- `meetings.render_contract.VotePromptRenderer`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

The band fix changes LIVE meeting behavior only inside the band (recorded replays reconstruct from
recorded actions, so committed bytes are safe), but any test that pins redirect-guard behavior on
synthetic mid-band values must be re-pinned deliberately, not silently. The manager edit sits in a file
15.4 also touches and 15.5 will touch after this task — the dependency chain (15.4 → this → 15.5)
serializes the three, so rebase on 15.4 and leave the vote-surface region clean for 15.5. Deleting
2.7 KLoC is low-risk precisely because nothing imports it — but confirm that with the grep, don't
assume it.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.schemas"`

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
Open a PR from branch `phase-15-substrate-hygiene` with a title like `task 15.6: substrate hygiene: latent hazards, dead code, single-homed constants, firewall contracts`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/post-phase-14-clean-up.md H6; audits/post-phase-14-pause.md §3 (dead StrategicReasoner, constant homing, import contracts), §4.1 (the raw-vs-rendered [0.595, 0.60) band); meetings/manager.py:2486-2498 (the redirect guard); eval/_suspicion_parse.py:54 (the deliberate re-declaration)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
