# Agent Prompt — 19.1 The front-door truth sweep + generated-fact checks

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.1 — The front-door truth sweep + generated-fact checks, anchored to audits/audit-phase-19-triage.md §7 item 1 [C; §8 rows 6, 16]; README.md:13 (219 PRs / ~2,500 tests), :48 vs :100 (the ladder-tip self-contradiction), :69 (the 0.938 mislabel), :104 ("intentionally minimal"), :158-175 (no Node/npm); AGENTS.md:16-19 (DESIGN.md declared authoritative), :64-79 (three-providers + stale baseline text); llm/README.md:32 (two providers) vs llm/provider.py:41-44 (four); .env.example:63-186 (six retired levers as LIVE default-OFF; zero `AILIBI_IMPOSTOR_ROLL_CALL`) vs orchestrator/replay.py:531-545 (`_RETIRED_ALWAYS_ON_LEVERS`), :570-572 (`_TOGGLEABLE_LEVER_RESOLVERS`), :590-625; scripts/generate_prompts.py:131-137 (the DESIGN.md constraint rule); the three reproducibility scopes (audit-phase-19-input-codex.md §6.1). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-front-door-truth`
**Depends on:** 19.3 (the README's cross-platform reproducibility claim states 19.3's measured outcome — portable sampler vs narrowed guarantee — so the front door cannot publish before that outcome exists)
**Section refs:** audits/audit-phase-19-triage.md §7 item 1 [C; §8 rows 6, 16]; README.md:13 (219 PRs / ~2,500 tests), :48 vs :100 (the ladder-tip self-contradiction), :69 (the 0.938 mislabel), :104 ("intentionally minimal"), :158-175 (no Node/npm); AGENTS.md:16-19 (DESIGN.md declared authoritative), :64-79 (three-providers + stale baseline text); llm/README.md:32 (two providers) vs llm/provider.py:41-44 (four); .env.example:63-186 (six retired levers as LIVE default-OFF; zero `AILIBI_IMPOSTOR_ROLL_CALL`) vs orchestrator/replay.py:531-545 (`_RETIRED_ALWAYS_ON_LEVERS`), :570-572 (`_TOGGLEABLE_LEVER_RESOLVERS`), :590-625; scripts/generate_prompts.py:131-137 (the DESIGN.md constraint rule); the three reproducibility scopes (audit-phase-19-input-codex.md §6.1)
**Complexity:** Medium

The repo's front door is documented as false by both audits; this task makes it true and
adds the cheap checks that keep it true. README: replace the stale counts (volatile
absolutes become generated-or-checked facts; the PR count is not re-pinned by hand),
resolve the ladder-tip self-contradiction (baseline 6 is the tip), quote sample provenance
from the manifests (2026-07-20; 4p1i 34% / 9p2i 30%), relabel "decision accuracy 0.938" as
conversion-label accuracy with the 0.8646 composed decision figure beside it, replace the
"intentionally minimal" UI line, add the Node/npm prerequisite, and name the three
reproducibility scopes separately (replay integrity; same-runtime repeatability;
cross-platform optimizer portability — the third currently unsupported, per 19.3).
DESIGN.md: a demotion banner naming its vintage and pointing to a new 2-page
`docs/architecture.md` current-architecture note; AGENTS.md keeps its rules but stops
declaring stale prose authoritative, gains the graduation-sweep convention (rewrite
interior docstrings when a lever graduates — the structural fix for the drift class 19.2
sweeps) and a shallow-clone note. `llm/README.md` rewritten for the four providers with
Featherless canonical. `.env.example` rewritten from the live lever registry (the six
retired levers move to a "graduated — always ON" note; the one live toggle documented).
`scripts/check_doc_facts.py` (new): a cheap offline check that fails when README's checked
claims drift from committed sources (manifest dates/win rates, the lever registry, the
named ladder tip); wiring it into `scripts/check.sh` is NOT in scope (19.7 owns check.sh) —
it runs via pytest. The generator's DESIGN.md rule was already scope-gated in the
planning PR (locked decision 8), so this task's prompt permits the DESIGN.md edits; the
generator itself is not touched here. The demotion must also reach the DISPATCH surface:
`scripts/prompt_template.md.j2:19` currently tells every generated prompt "DESIGN.md is
the source of truth" — rewrite that authority line (AGENTS.md remains the rulebook;
docs/architecture.md is the current-architecture note; DESIGN.md is historical) and
regenerate ALL prompts in the same PR so no dispatched agent is ever told to obey the
document this task demotes. The onboarding plan gets the same treatment:
AGENT_IMPLEMENTATION.md is onboarding-mandatory (AGENTS.md:8-12) and calls DESIGN.md
"the single source of truth" four times (:39-47 and the stale AGENTS template at
:530-537) — update its authority prose so a newly onboarded agent never receives the
demoted routing and the live one in contradiction. The README's third reproducibility
scope quotes 19.3's recorded outcome (the dependency edge exists for exactly this
sentence).

**Files in scope:**
- README.md
- AGENTS.md
- DESIGN.md; (the demotion banner + per-section supersession notes only — the historical content is not rewritten)
- docs/architecture.md (new)
- llm/README.md
- .env.example
- AGENT_IMPLEMENTATION.md; (the authority prose + the stale embedded AGENTS template — historical mechanics stay)
- scripts/prompt_template.md.j2; (the DESIGN.md authority line only)
- agent_prompts/; (regenerated — the authority line changes in every prompt, atomically with the demotion)
- scripts/check_doc_facts.py (new)
- tests/scripts/test_check_doc_facts.py (new)

**Files NOT in scope:**
- scripts/check.sh; (19.7 owns it — the fact check runs as a test)
- scripts/generate_prompts.py (the DESIGN.md scope-gate landed in the planning PR)
- orchestrator/replay.py (the lever registry is read, never edited)
- training/reports/ (report errata belong to 19.20)

**Definition of done:**
- [ ] Every named falsehood above is fixed and no README claim contradicts another README claim or a committed manifest; the three reproducibility scopes are stated; the ES portability caveat matches 19.3's honest wording (coordinate via the scopes text, not via shared files).
- [ ] `scripts/check_doc_facts.py` passes at HEAD, fails when a checked README fact is perturbed (test-pinned both ways), and runs offline in seconds.
- [ ] `.env.example` documents exactly the live toggleable levers from `orchestrator/replay.py:570-572` and labels the `_RETIRED_ALWAYS_ON_LEVERS` set as graduated/always-ON, cross-checked by a test importing the registry.
- [ ] DESIGN.md opens with the demotion banner; `docs/architecture.md` describes the CURRENT layering (engine → observation → agents/meetings ← orchestrator; llm behind the Protocol; eval/api privileged; frontend on generated types) in ≤2 pages; AGENTS.md routes readers to it and carries the graduation-sweep convention.
- [ ] The dispatch template's authority line no longer asserts DESIGN.md as the source of truth; all prompts are regenerated in this PR and `generate_prompts.py --check` is green — a repo grep proves zero generated prompts still carry the old sentence.
- [ ] AGENT_IMPLEMENTATION.md's authority prose matches the demoted routing (a grep for its "single source of truth" claims returns only historical-context usages, none normative).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

For the fact check: prefer deleting volatile absolute counts from README over generating
them; where a number stays (win rates, dates, ladder tip), read it from the
manifest/registry and compare. Do not call the GitHub API — the PR count becomes prose
("300+; see GitHub") or is dropped.

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
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
Open a PR from branch `phase-19-front-door-truth` with a title like `task 19.1: the front-door truth sweep + generated-fact checks`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 1 [C; §8 rows 6, 16]; README.md:13 (219 PRs / ~2,500 tests), :48 vs :100 (the ladder-tip self-contradiction), :69 (the 0.938 mislabel), :104 ("intentionally minimal"), :158-175 (no Node/npm); AGENTS.md:16-19 (DESIGN.md declared authoritative), :64-79 (three-providers + stale baseline text); llm/README.md:32 (two providers) vs llm/provider.py:41-44 (four); .env.example:63-186 (six retired levers as LIVE default-OFF; zero `AILIBI_IMPOSTOR_ROLL_CALL`) vs orchestrator/replay.py:531-545 (`_RETIRED_ALWAYS_ON_LEVERS`), :570-572 (`_TOGGLEABLE_LEVER_RESOLVERS`), :590-625; scripts/generate_prompts.py:131-137 (the DESIGN.md constraint rule); the three reproducibility scopes (audit-phase-19-input-codex.md §6.1)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
