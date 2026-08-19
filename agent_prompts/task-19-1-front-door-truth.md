# Agent Prompt — 19.1 The front-door truth sweep + generated-fact checks

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

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
generator itself is not touched here. The DISPATCH surface is already truthful: the
planning PR neutralized the template's authority line via AGENTS.md indirection
("AGENTS.md names the authoritative architecture routing" — true before this task, and
after it the routing lands on docs/architecture.md), so this task's demotion needs NO
template or prompt regeneration. The onboarding plan gets the demotion treatment:
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
- [ ] AGENT_IMPLEMENTATION.md's authority prose matches the demoted routing (a grep for its "single source of truth" claims returns only historical-context usages, none normative); AGENTS.md's routing (which the neutral dispatch template defers to) lands on docs/architecture.md.
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
Open a PR from branch `phase-19-front-door-truth` with a title like `task 19.1: the front-door truth sweep + generated-fact checks`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 1 [C; §8 rows 6, 16]; README.md:13 (219 PRs / ~2,500 tests), :48 vs :100 (the ladder-tip self-contradiction), :69 (the 0.938 mislabel), :104 ("intentionally minimal"), :158-175 (no Node/npm); AGENTS.md:16-19 (DESIGN.md declared authoritative), :64-79 (three-providers + stale baseline text); llm/README.md:32 (two providers) vs llm/provider.py:41-44 (four); .env.example:63-186 (six retired levers as LIVE default-OFF; zero `AILIBI_IMPOSTOR_ROLL_CALL`) vs orchestrator/replay.py:531-545 (`_RETIRED_ALWAYS_ON_LEVERS`), :570-572 (`_TOGGLEABLE_LEVER_RESOLVERS`), :590-625; scripts/generate_prompts.py:131-137 (the DESIGN.md constraint rule); the three reproducibility scopes (audit-phase-19-input-codex.md §6.1)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
