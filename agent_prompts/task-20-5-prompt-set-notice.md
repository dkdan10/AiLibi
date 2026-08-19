# Agent Prompt — 20.5 First-run quiet: the prompt-set notice and its documentation

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.5 — First-run quiet: the prompt-set notice and its documentation, anchored to C/B1 (audits/review-2026-08-19/C/collated-portfolio.md §B item B1, ruled GOOD-top in §D3); audits/review-2026-08-19/C/x1-front-door-reproduction.md §1 (the "Noise observed on every run" note under the command table) + §5 MUST-3; audits/review-2026-08-19/C/p1-backend-hiring-manager.md §2 ("reads like a misconfiguration"), §4 and §7 GOOD-6; C-83 + C-126 + C-130 (audits/review-2026-08-19/B/collated-findings.md); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 0.5 and audits/review-2026-08-19/D/cross-track-map.md §"0. Front-door pre-wave"; anchors re-verified at HEAD — agents/strategic/prompts/loader.py:145-167 (`_notify_bare_prompt_set_fallback`, the stderr print), :170-201 (`resolve_prompt_set`, the emitter call at :200), :238 (`_ENV` built at import); orchestrator/game.py:910 (`build_default_meeting_runner`'s bare `resolve_prompt_set()`) vs :915 (`prompt_versions_for_set(active_prompt_set)`, explicit and therefore silent); llm/provider.py:31 (`ENV_PROVIDER`), :42 (`PROVIDER_FAKE`), :302-306 (the default/strip/lower resolution expression and the fake branch it selects); llm/fake_provider.py:8-11 + meetings/manager.py:1380-1382, :1863-1865 (both client call sites pass a Pydantic `schema`); orchestrator/replay.py:93-103 (the deliberately mirrored 18.10 resolver and the reason the loader is not imported there); tests/agents/test_prompt_loader.py:78-152 (`TestBareEnvironmentFallbackIsLoud`, the Task-19.6 pins); .env.example:29 (`AILIBI_LLM_PROVIDER=fake`); AGENTS.md:48 ("No global state"), :112 ("Environment setup"), :127-146 (the LLM-providers bullet); tasks/phase-19.md Task 19.6 (the notice's origin; its Files-NOT-in-scope routed the env-var documentation to Task 19.1, which never carried it). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-prompt-set-notice`
**Depends on:** none (root)
**Section refs:** C/B1 (audits/review-2026-08-19/C/collated-portfolio.md §B item B1, ruled GOOD-top in §D3); audits/review-2026-08-19/C/x1-front-door-reproduction.md §1 (the "Noise observed on every run" note under the command table) + §5 MUST-3; audits/review-2026-08-19/C/p1-backend-hiring-manager.md §2 ("reads like a misconfiguration"), §4 and §7 GOOD-6; C-83 + C-126 + C-130 (audits/review-2026-08-19/B/collated-findings.md); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 0.5 and audits/review-2026-08-19/D/cross-track-map.md §"0. Front-door pre-wave"; anchors re-verified at HEAD — agents/strategic/prompts/loader.py:145-167 (`_notify_bare_prompt_set_fallback`, the stderr print), :170-201 (`resolve_prompt_set`, the emitter call at :200), :238 (`_ENV` built at import); orchestrator/game.py:910 (`build_default_meeting_runner`'s bare `resolve_prompt_set()`) vs :915 (`prompt_versions_for_set(active_prompt_set)`, explicit and therefore silent); llm/provider.py:31 (`ENV_PROVIDER`), :42 (`PROVIDER_FAKE`), :302-306 (the default/strip/lower resolution expression and the fake branch it selects); llm/fake_provider.py:8-11 + meetings/manager.py:1380-1382, :1863-1865 (both client call sites pass a Pydantic `schema`); orchestrator/replay.py:93-103 (the deliberately mirrored 18.10 resolver and the reason the loader is not imported there); tests/agents/test_prompt_loader.py:78-152 (`TestBareEnvironmentFallbackIsLoud`, the Task-19.6 pins); .env.example:29 (`AILIBI_LLM_PROVIDER=fake`); AGENTS.md:48 ("No global state"), :112 ("Environment setup"), :127-146 (the LLM-providers bullet); tasks/phase-19.md Task 19.6 (the notice's origin; its Files-NOT-in-scope routed the env-var documentation to Task 19.1, which never carried it)
**Complexity:** Small
**Record impact:** none — stderr diagnostics and documentation only; no rendered prompt byte moves, no recorded `prompt_versions` stamp moves, no detector output moves, pinned by the prompt byte-golden and `verify_samples.sh`.
**Measurement:** with `env -u AILIBI_PROMPT_SET -u AILIBI_LLM_PROVIDER`, each of the three front-door commands emits ZERO stderr lines — `uv run python scripts/run_game.py --seed 42 --replay-path <tmp>` (2 notice lines at HEAD), `bash scripts/verify_samples.sh` (2), `uv run python scripts/run_tournament.py --num-games 5 --output-dir <tmp>` (6); `uv run pytest tests/agents/test_prompt_loader.py -q` green with the real-provider leg asserting exactly one notice line per process; `bash scripts/verify_samples.sh` 100/100 clean; `uv run python scripts/check_doc_facts.py` green.

The first thing a stranger sees when they run this project is a warning about a variable
this project documents nowhere. Every front-door command prints
`agents.strategic.prompts.loader: AILIBI_PROMPT_SET is unset — falling back to the frozen
reference set 'qwen3_5_9b', two generations behind the operational baseline 'qwen3_6_27b'`
on stderr, and it is the ONLY thing on stderr. Re-measured at HEAD in this planning
session, bare-environment: `run_game.py` prints it twice, `verify_samples.sh` twice, the
README's own five-game tournament six times — matching the review's counts
(audits/review-2026-08-19/C/x1-front-door-reproduction.md §1). `AILIBI_PROMPT_SET` appears
zero times in README.md, .env.example, AGENTS.md and docs/architecture.md (grep count 0 in
each, re-verified at HEAD). Five of six portfolio personas said they would not star the repo
today (audits/review-2026-08-19/D/FINAL-synthesis.md §4), and the one who ran the
determinism demo recorded that the first output "reads like a misconfiguration"
(audits/review-2026-08-19/C/p1-backend-hiring-manager.md §2). A
reproducibility pitch whose first line is an unexplained warning is spending its strongest
asset on nothing.

The notice is not wrong — it is untargeted. Task 19.6 added it for a real reason: the
default set VALUE must stay `qwen3_5_9b` for byte-identity with every committed render,
while every operational surface runs `qwen3_6_27b`, so a bare shell used to take a
two-generations-old prompt family with no signal at all. That reasoning holds for a real
provider and evaporates under the fake one. Both client call sites that can reach a
provider pass a Pydantic `schema` (meetings/manager.py:1382 `MeetingTurn`, :1865
`VoteBallot`), and with a schema the fake builds a minimal valid instance by introspecting
the model rather than reading the prompt's wording (llm/fake_provider.py:8-11) — so "two
generations behind the operational baseline", a claim about MODEL behaviour, describes a
risk that cannot exist on the default path. The set does still select which template bytes
render and which `prompt_versions` a recording stamps, which is exactly why this task
DOCUMENTS the variable rather than deleting the notice: the honest fix is to make the
notice fire where it means something and to name the knob where a reader will look.

The second defect is volume. The notice fires once per resolution point, and the resolution
points are per-process and per-game: the import-time `_ENV` build (loader.py:238) plus one
per `build_default_meeting_runner` call (orchestrator/game.py:910). That is why a five-game
tournament prints six lines. Under a real provider the message is worth saying once; saying
it once per game is the same noise with a better excuse. This task makes it once per
process. That reverses a deliberate 19.6 ruling recorded in the emitter's own docstring
(loader.py:149-150: no warn-once flag, because that would be module-level mutable state
under AGENTS.md:48), so the reversal is recorded in place of that sentence, not stacked on
top of it: AGENTS.md:48 forbids module-level mutable state that OWNS state the program
reads back; a de-duplication cache for a stderr diagnostic owns nothing, changes no return
value, and is resettable — and the tests reset it explicitly rather than depending on
collection order.

Nothing here moves a byte the record depends on. C-126 (audits/review-2026-08-19/B/collated-findings.md)
counted `.env.example` documenting 11 of 43 `AILIBI_*` names; this task closes the one the
front door prints. C-83's separate finding — that the loader's import-time `_ENV` side
effect is what forces `orchestrator/replay.py:93-103` to mirror the 18.10 resolver
byte-for-byte instead of importing it — is NOT addressed here and must not be: removing the
import-time build changes what a stray prompt-set export does to every replay-only consumer,
which is a different task with a different blast radius. This task adds no import-time work
beyond two constant imports.

**Files in scope:**
- agents/strategic/prompts/loader.py; (silence the notice when `AILIBI_LLM_PROVIDER` resolves to the fake provider; emit at most once per process otherwise; the docstring ruling)
- tests/agents/test_prompt_loader.py; (both provider branches, the once-per-process pin, the env grid, and the reset seam the Task-19.6 pins now need)
- .env.example; (document `AILIBI_PROMPT_SET` beside `AILIBI_LLM_PROVIDER` at :29 — the default, the operational baseline, where the registered names live, and that the notice is expected under a real provider)
- AGENTS.md; (one sentence naming the variable in the Environment-setup LLM-providers bullet at :127-146)

**Files NOT in scope:**
- README.md (the front-door rewrite owns it and carries the documented variable there; this task must not pre-empt that text)
- orchestrator/game.py (the prompt-version registry and the runner's resolution points are unchanged — the gate lives at the emitter, not at the call sites)
- orchestrator/replay.py (the mirrored 18.10 resolver and C-83's import-time-side-effect finding are a separate defect; `_ENV` at loader.py:238 stays exactly as it is)
- llm/provider.py (read for `ENV_PROVIDER` / `PROVIDER_FAKE` and the resolution expression at :302; imported, never re-implemented, never edited)
- any `.j2` prompt template and any prompt-set directory (prompt-template edits belong to the phase's single prompt-set bump task and to no other)
- scripts/check_doc_facts.py (no new checked fact is added here; it must stay green over the edited `.env.example`)
- tests/conftest.py (pinning the whole `AILIBI_*` env surface for the suite is another contract's file)

**Definition of done:**
- [ ] With `AILIBI_LLM_PROVIDER` unset or resolving to the fake provider, `resolve_prompt_set` takes the default and emits NOTHING on stderr; with `AILIBI_PROMPT_SET` unset and the provider resolving to `anthropic`, `ollama` or `featherless`, the one-line notice still prints — both branches pinned in `tests/agents/test_prompt_loader.py`.
- [ ] The notice prints at most ONCE per process on the real-provider path: a test drives at least three fallback resolutions under a real-provider env mapping and asserts exactly one stderr line, and a companion test asserts the FIRST resolution still emits (the gate can fail — AGENTS.md craft rule 2).
- [ ] Suppression never consumes the one allowed emission: a fake-provider resolution followed by a real-provider resolution in the same process still prints the notice once — pinned.
- [ ] The provider gate uses `ENV_PROVIDER` and `PROVIDER_FAKE` imported from `llm.provider` (no mirrored string literal in the loader) and its verdict agrees with `llm.provider.build_default_client`'s branch selection over the env grid `unset`, `"fake"`, `"FAKE"`, `" fake "`, `""`, `"anthropic"`, `"ollama"`, `"featherless"` — pinned as a table-driven test; the provider is read from the SAME `env` mapping the prompt set is resolved from, never from `os.environ` when a mapping was passed.
- [ ] The Task-19.6 pins at `tests/agents/test_prompt_loader.py:78-152` still assert the notice, via an explicit documented reset of the once-per-process seam in a fixture; no test in the file depends on collection order or on whether the import-time `_ENV` build already fired.
- [ ] `.env.example` documents `AILIBI_PROMPT_SET` in the LLM-provider section immediately after `AILIBI_LLM_PROVIDER=fake` (:29) as a COMMENTED example line — never an active assignment — naming the default set, the operational baseline set, `orchestrator/game.py::PROMPT_VERSION_SETS` as the enumerable source of the registered names, that an unknown name fails loud, and that the notice under a real provider is expected rather than a misconfiguration; AGENTS.md's Environment-setup LLM-providers bullet names the variable in one sentence.
- [ ] The emitter's docstring states the current rule in intent-first form (fake provider: silent; real provider: once per process) with at most one trailing provenance line, and the Task-19.6 sentence refusing a warn-once flag is REPLACED by the ruling this task makes — AGENTS.md craft rules 1 and 3, and the graduation-sweep convention applied to a reversed decision.
- [ ] Record impact none is proven, not asserted: `bash scripts/verify_samples.sh` reports 100/100 clean and `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` is green, so no rendered prompt byte and no recorded `prompt_versions` stamp moved; `uv run python scripts/check_doc_facts.py` stays green over the edited `.env.example`.
- [ ] The PR quotes the before/after stderr line counts for all three front-door commands run with `env -u AILIBI_PROMPT_SET -u AILIBI_LLM_PROVIDER` (before: 2, 2, 6 — all of them this notice; after: 0, 0, 0) and the same three commands under `AILIBI_LLM_PROVIDER=featherless` (after: 1, 1, 1).
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
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-20-prompt-set-notice` with a title like `task 20.5: first-run quiet: the prompt-set notice and its documentation`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing C/B1 (audits/review-2026-08-19/C/collated-portfolio.md §B item B1, ruled GOOD-top in §D3); audits/review-2026-08-19/C/x1-front-door-reproduction.md §1 (the "Noise observed on every run" note under the command table) + §5 MUST-3; audits/review-2026-08-19/C/p1-backend-hiring-manager.md §2 ("reads like a misconfiguration"), §4 and §7 GOOD-6; C-83 + C-126 + C-130 (audits/review-2026-08-19/B/collated-findings.md); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 0.5 and audits/review-2026-08-19/D/cross-track-map.md §"0. Front-door pre-wave"; anchors re-verified at HEAD — agents/strategic/prompts/loader.py:145-167 (`_notify_bare_prompt_set_fallback`, the stderr print), :170-201 (`resolve_prompt_set`, the emitter call at :200), :238 (`_ENV` built at import); orchestrator/game.py:910 (`build_default_meeting_runner`'s bare `resolve_prompt_set()`) vs :915 (`prompt_versions_for_set(active_prompt_set)`, explicit and therefore silent); llm/provider.py:31 (`ENV_PROVIDER`), :42 (`PROVIDER_FAKE`), :302-306 (the default/strip/lower resolution expression and the fake branch it selects); llm/fake_provider.py:8-11 + meetings/manager.py:1380-1382, :1863-1865 (both client call sites pass a Pydantic `schema`); orchestrator/replay.py:93-103 (the deliberately mirrored 18.10 resolver and the reason the loader is not imported there); tests/agents/test_prompt_loader.py:78-152 (`TestBareEnvironmentFallbackIsLoud`, the Task-19.6 pins); .env.example:29 (`AILIBI_LLM_PROVIDER=fake`); AGENTS.md:48 ("No global state"), :112 ("Environment setup"), :127-146 (the LLM-providers bullet); tasks/phase-19.md Task 19.6 (the notice's origin; its Files-NOT-in-scope routed the env-var documentation to Task 19.1, which never carried it)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
