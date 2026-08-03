# Agent Prompt — 19.18 The tier map, the freeze-label sweep, and the reopening checklist

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.18 — The tier map, the freeze-label sweep, and the reopening checklist, anchored to audits/audit-phase-19-triage.md §7 items 19+21 [C] and the label halves of 29 [S-Claude] + 31 [L / source-specific] + locked decisions 2 and 3; §8 rows 21–22 (the reopen caveats; the component channels); audits/audit-phase-18-close.md §7 (the ledger long tail to freeze-label: items 5–8, 10–14) and §6.1 L10 (the Red-Queen context); eval/off_menu.py:12-34 (its own vacuity docstring); eval/deception_instruments.py (no non-test consumer — verified); eval/_suspicion_parse.py:9-13 + eval/meeting_quality.py:276-283 + eval/vote_correctness.py:566-571 (the rendered-prose scrapes to label frozen) [S-Claude — sites re-verified at HEAD]; training/surrogate/runner.py:105/:164/:383 with its live importers (training/composed_runner.py:122-124, training/bakeoff/harness.py) — the standalone-vs-dependency boundary 19.19 implements. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-tier-map`
**Depends on:** 19.5, 19.9 (the second edge is experiments/ serialization — `rubric_score.py` is LIVE, stays unlabeled, and belongs to the curation task)
**Section refs:** audits/audit-phase-19-triage.md §7 items 19+21 [C] and the label halves of 29 [S-Claude] + 31 [L / source-specific] + locked decisions 2 and 3; §8 rows 21–22 (the reopen caveats; the component channels); audits/audit-phase-18-close.md §7 (the ledger long tail to freeze-label: items 5–8, 10–14) and §6.1 L10 (the Red-Queen context); eval/off_menu.py:12-34 (its own vacuity docstring); eval/deception_instruments.py (no non-test consumer — verified); eval/_suspicion_parse.py:9-13 + eval/meeting_quality.py:276-283 + eval/vote_correctness.py:566-571 (the rendered-prose scrapes to label frozen) [S-Claude — sites re-verified at HEAD]; training/surrogate/runner.py:105/:164/:383 with its live importers (training/composed_runner.py:122-124, training/bakeoff/harness.py) — the standalone-vs-dependency boundary 19.19 implements
**Complexity:** Medium

The ruling is made (locked decision 2); this task writes it down where the next agent
will trip over it. `training/README.md` (new): the component-by-component
keep/freeze/retire table with the measured basis per row — surrogate RANKING kept (46/60
top-1) vs the standalone decision arm retired (96/96 held-out SKIP; the FACTORY and the
class stay wherever the composed runner's verification fence and the harness consume
them — `training/composed_runner.py:266`, `training/bakeoff/harness.py:159` — and what
retires is the surrogate-ONLY runner exposure 19.19's consumer grep proves free; state
the boundary explicitly); the composed
runner frozen optional-diagnostic (0.8646 decision / 0.7917 exact, zero-LLM Goodhart
substrate caveat); the conviction model kept (0.9375 CONVERSION-LABEL accuracy — the
terminology ruling); ES core + champion acceptance kept; crew stack frozen
(clean negative); coevo/campaign machinery frozen; realpath retired (19.19). Record what
the program POSITIVELY learned (N1/N2 with their z-scores; the clean negatives) so the
tier map is findings, not just plumbing. The REOPENING CHECKLIST section implements
locked decision 3: both routes, the four mandatory pre-campaign checks, decide-at-
proposal. The freeze-label sweep: a standard FROZEN header (naming this map) on every
frozen module — coevo/, scenarios.py, anchor_study.py, the fidelity harnesses,
experiments/, off_menu, deception_instruments, the rendered-prose metric sites (labeled
"frozen — unreliable under prompt-shape change"), the watchability referee (frozen with
the champion opt-in path it serves), the bash recorders, and an engine note for the
byte-frozen RNG-draw apparatus — plus the phase-18 ledger long tail labeled in place
(recorder lock-race, `deadline_default` gaps, `composed_artifact_dir` escape,
campaign-plan overwrite, selector delegation convention, resume map refusal,
`WORK_DIR_OWNED_NAMES`), each label naming its close-audit anchor. Labels and docs only —
zero behavior bytes.

**Files in scope:**
- training/README.md (new)
- training/coevo/; (FROZEN headers only)
- training/scenarios.py; (same)
- training/anchor_study.py; (same)
- training/conviction/fidelity.py; (FROZEN header only)
- training/surrogate/fidelity.py; (FROZEN header only)
- training/composed_runner.py; (the frozen optional-diagnostic label)
- training/crew/; (FROZEN headers only — the crew stack is the FREEZE column's clean negative)
- training/surrogate/runner.py; (the standalone-vs-dependency boundary label — 19.19 does the code)
- experiments/; (FROZEN headers — EXCEPT experiments/lab/rubric_score.py, which is live and owned by the curation task; it gets no frozen header)
- eval/off_menu.py; (label)
- eval/deception_instruments.py; (label)
- eval/_suspicion_parse.py; (the frozen-metric label)
- eval/meeting_quality.py; (the scrape-site label lines only)
- eval/vote_correctness.py; (same)
- eval/watchability.py; (the referee freeze label only — floors untouched)
- scripts/record_ml_corpus.sh; (freeze header + the ledger labels)
- scripts/refresh_samples.sh; (freeze header)
- engine/tick.py; (the byte-frozen RNG-apparatus note only)

**Files NOT in scope:**
- training/realpath.py (19.19 deletes it — do not label a file being retired)
- tests/ (marker/tiering implementation is 19.27's, driven by this map)
- training/reports/ (19.20's errata)

**Definition of done:**
- [ ] Verify-then-label for the S-Claude scrape sites: confirm each rendered-prose scrape at HEAD before labeling it (sites re-verified by the planning session; re-run the grep in-session).
- [ ] `training/README.md` names every disputed component with its ruling, measured basis, and consumer boundary; the reopening checklist carries both routes + all four checks + the decide-at-proposal rule; N1/N2 and the clean negatives are recorded as retained findings.
- [ ] Every frozen module opens with the standard header naming the map; every ledger long-tail item is labeled at its anchor; a repo grep for the header proves coverage matches the map's FREEZE column exactly.
- [ ] Zero behavior bytes: the diff is docs, comments, and docstrings only.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

One header format, stated in training/README.md and repeated verbatim:
`FROZEN (Phase 19 tier map, training/README.md): <one-line reason>. Bug fixes and
evidence readers only; no new search.` The tier table's rows should quote the exact
numbers from the committed reports (recompute nothing — cite `report-ballot-surrogate.md`
etc. by line). The reopening checklist's four checks come from triage §8 row 21 — quote
the mechanism, not just the name.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
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
Open a PR from branch `phase-19-tier-map` with a title like `task 19.18: the tier map, the freeze-label sweep, and the reopening checklist`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 items 19+21 [C] and the label halves of 29 [S-Claude] + 31 [L / source-specific] + locked decisions 2 and 3; §8 rows 21–22 (the reopen caveats; the component channels); audits/audit-phase-18-close.md §7 (the ledger long tail to freeze-label: items 5–8, 10–14) and §6.1 L10 (the Red-Queen context); eval/off_menu.py:12-34 (its own vacuity docstring); eval/deception_instruments.py (no non-test consumer — verified); eval/_suspicion_parse.py:9-13 + eval/meeting_quality.py:276-283 + eval/vote_correctness.py:566-571 (the rendered-prose scrapes to label frozen) [S-Claude — sites re-verified at HEAD]; training/surrogate/runner.py:105/:164/:383 with its live importers (training/composed_runner.py:122-124, training/bakeoff/harness.py) — the standalone-vs-dependency boundary 19.19 implements), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
