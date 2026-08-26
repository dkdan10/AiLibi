# Agent Prompt — 20.41 Tail truth: verifiable-shaped claims, the reading guide's anchors, and the finalist raw slate's status

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.41 — Tail truth: verifiable-shaped claims, the reading guide's anchors, and the finalist raw slate's status, anchored to audits/review-2026-08-19/C/collated-portfolio.md §B9 (verifiable-shaped claims and the three named wobbles), §B10 (the finalist raw slate), §B3 (the reading guide's `file:line` citations — ALREADY CLOSED at HEAD by Task 20.12, PR #371: the guide was rewritten to heading anchors and the zero is gate-pinned by `scripts/check_doc_facts.py::check_guide_line_citations`, so nothing is left for this task there); audits/review-2026-08-19/C/x1-front-door-reproduction.md reproduction row 1 (the unmentioned `r1.audit.jsonl` sidecar, 38,881 B beside two 50,337-byte replays), GOOD-9, GOOD-11, GOOD-12 and the "ADR-0001 vs README" note; audits/review-2026-08-19/C/p2-ml-research-lead.md §3:33 (weakest-3 item 3: the 449-game slate behind the adoption ruling is not in the repo) and §7:94 (the GOOD item: commit or explicitly de-scope it); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 row 3.6. Re-verified at HEAD: README.md:117 ("recorded verbatim in ADR-0001", now under the `## What it is` heading — re-locate by the heading; the front-door rework moved it from :72) vs docs/adr/0001-three-load-bearing-decisions.md:5 (author Codex), :14 (target 2 Hz), :16 (≤ 100 LLM calls) and DESIGN.md §0 (whose call-target sentence carries a parenthetical the ADR drops); docs/deployment.md:7, :38, :184, :209 (bare `audit C-C-1 / C-C-2 / C-C-4` — Task 20.7's Pages section pushed the two headings down from :104, :129) resolving to audits/audit-2026-05-30-0059-mvp-close.md:53-55 + :164; scripts/run_game.py:46-49 and orchestrator/game.py:1660-1666 (the `<replay-stem>.audit.jsonl` default, now the `else` arm of the no-replay guard added at :1651-1659) with README.md:38-43 (the determinism block — ONE command block now, under `## Verify it yourself in one minute`; the duplicate at :119-120 is gone) and .gitignore:31 + docs/artifacts.md:113 (class (d)); docs/artifacts.md:106, :112, :123, :150-163; training/reports/report-finalist-eval.md:115-118, :569 (§9.2 as-recorded paths), :1066-1070, :2618-2684 (§19, the Task 19.21 erratum); training/reports/results-finalist-eval.jsonl (9 rows carrying `/Users/danielkeinan/ailibi-campaign-1826/…`); scripts/verify_ml_evidence.py:109-111, :120, :516-526 (`read_pinned_sha`), :529 (`read_slate_ruling`), :2293, :2346; tests/scripts/test_verify_ml_evidence.py:212 (the real-tree section header), :264-269 (`test_availability_registry_covers_the_document`), :968-1000 (`test_the_loss_path_may_omit_the_slate_manifest`), :1075-1104 (`test_complete_accepts_a_manifestless_recorded_loss_end_to_end`); audits/audit-phase-19-close.md:52 ("OK: 2953/2953 files match 476a1f85…"), :387.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-tail-truth`
**Depends on:** 20.38, 20.40 — the results prose settles the README and the reading guide on the new bytes first, so this task edits final wording rather than a draft; and the lessons page plus the curated review index claim the last README real estate, so the tail sentences are stable before they are made checkable.
**Section refs:** audits/review-2026-08-19/C/collated-portfolio.md §B9 (verifiable-shaped claims and the three named wobbles), §B10 (the finalist raw slate), §B3 (the reading guide's `file:line` citations — ALREADY CLOSED at HEAD by Task 20.12, PR #371: the guide was rewritten to heading anchors and the zero is gate-pinned by `scripts/check_doc_facts.py::check_guide_line_citations`, so nothing is left for this task there); audits/review-2026-08-19/C/x1-front-door-reproduction.md reproduction row 1 (the unmentioned `r1.audit.jsonl` sidecar, 38,881 B beside two 50,337-byte replays), GOOD-9, GOOD-11, GOOD-12 and the "ADR-0001 vs README" note; audits/review-2026-08-19/C/p2-ml-research-lead.md §3:33 (weakest-3 item 3: the 449-game slate behind the adoption ruling is not in the repo) and §7:94 (the GOOD item: commit or explicitly de-scope it); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 row 3.6. Re-verified at HEAD: README.md:117 ("recorded verbatim in ADR-0001", now under the `## What it is` heading — re-locate by the heading; the front-door rework moved it from :72) vs docs/adr/0001-three-load-bearing-decisions.md:5 (author Codex), :14 (target 2 Hz), :16 (≤ 100 LLM calls) and DESIGN.md §0 (whose call-target sentence carries a parenthetical the ADR drops); docs/deployment.md:7, :38, :184, :209 (bare `audit C-C-1 / C-C-2 / C-C-4` — Task 20.7's Pages section pushed the two headings down from :104, :129) resolving to audits/audit-2026-05-30-0059-mvp-close.md:53-55 + :164; scripts/run_game.py:46-49 and orchestrator/game.py:1660-1666 (the `<replay-stem>.audit.jsonl` default, now the `else` arm of the no-replay guard added at :1651-1659) with README.md:38-43 (the determinism block — ONE command block now, under `## Verify it yourself in one minute`; the duplicate at :119-120 is gone) and .gitignore:31 + docs/artifacts.md:113 (class (d)); docs/artifacts.md:106, :112, :123, :150-163; training/reports/report-finalist-eval.md:115-118, :569 (§9.2 as-recorded paths), :1066-1070, :2618-2684 (§19, the Task 19.21 erratum); training/reports/results-finalist-eval.jsonl (9 rows carrying `/Users/danielkeinan/ailibi-campaign-1826/…`); scripts/verify_ml_evidence.py:109-111, :120, :516-526 (`read_pinned_sha`), :529 (`read_slate_ruling`), :2293, :2346; tests/scripts/test_verify_ml_evidence.py:212 (the real-tree section header), :264-269 (`test_availability_registry_covers_the_document`), :968-1000 (`test_the_loss_path_may_omit_the_slate_manifest`), :1075-1104 (`test_complete_accepts_a_manifestless_recorded_loss_end_to_end`); audits/audit-phase-19-close.md:52 ("OK: 2953/2953 files match 476a1f85…"), :387.
**Complexity:** Small
**Record impact:** post-record
**Measurement:** `uv run python scripts/verify_ml_evidence.py --complete` green with the PR quoting the slate's availability row verbatim (`OK` on the commit path, `INFO … LOST (recorded …)` on the de-scope path); `uv run python scripts/check_doc_facts.py` green; `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` green including the new erratum-pin test and its perturbation leg; `grep -n 'audit C-C-' docs/deployment.md` shows every hit naming its source audit file.

This phase spent itself on making the loudest claims true. Three quieter ones are
still shaped so that a reader cannot check them, and all three sit on the paths a
stranger actually walks. README.md:117 (`## What it is` — re-locate by the heading;
the front-door rework moved it from :72) says the three load-bearing decisions are
"recorded verbatim in [ADR-0001]"; the ADR's text is not the README's — it carries a
`target 2 Hz` tick rate (docs/adr/0001-three-load-bearing-decisions.md:14), a `≤ 100
LLM calls` per-game target (:16) and an author line reading Codex (:5), and the
README's restatement carries none of the three. docs/deployment.md opens with
`Anchors: audit C-C-1, C-C-2, C-C-4` (:7) and repeats the bare ids in its body (:38)
and in two section headings (:184, :209 — Task 20.7's Pages section pushed them down
from :104, :129); the ids do resolve — to the MVP-close security review,
audits/audit-2026-05-30-0059-mvp-close.md:53-55, listed at :164 —
but only to someone who already knows to grep, which is exactly what the outside
reproduction session recorded
(audits/review-2026-08-19/C/x1-front-door-reproduction.md GOOD-12). And the
determinism demo the README hands every visitor (README.md:38-43 — ONE command block
now, under `## Verify it yourself in one minute`; the duplicate at :119-120 is gone)
leaves a file the README never names: orchestrator/game.py:1660-1666 defaults the
observation audit log to `<replay-stem>.audit.jsonl` beside the replay unless
`--audit-log-path` overrides it (scripts/run_game.py:46-49), so the reproduction
session's very first row logged an unexplained 38,881-byte sidecar next to two
50,337-byte replays (review-measured,
audits/review-2026-08-19/C/x1-front-door-reproduction.md row 1).

None of these is a defect in the code; each is a sentence that spends the project's
credibility instead of earning it. A repo whose front door says "verify it yourself"
pays a disproportionate price for a claim that fails on the first check, and the
reproduction session's judgment was that these are the cheapest remaining fixes on
the whole credibility ledger (audits/review-2026-08-19/C/collated-portfolio.md §B9;
audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 row 3.6, "tail polish"). The
standing convention is already written down — claims verifiable-shaped, every
assertion naming the mechanism or the file that settles it — so this task is the
convention applied to its own documentation.

The fourth item, the finalist raw slate, needs its anchor corrected before it can be
acted on. The review reports `training/reports/_finalist_eval_raw` as empty with the
report's rows pointing at `/Users/…`
(audits/review-2026-08-19/C/collated-portfolio.md §B10, carried from
audits/review-2026-08-19/C/p2-ml-research-lead.md §3, itself carried from the
Phase-19 triage). RE-VERIFIED AT HEAD, that anchor has moved: `git ls-files
training/reports/_finalist_eval_raw` now returns exactly one path, `MANIFEST.md` —
Task 19.21's 1,569 per-file digests, registered at docs/artifacts.md:106 — and the
payload itself was folded into the one orphan evidence commit
`evidence/phase-18-coevo` @ `476a1f85492439277350af9708f1d120eb1c0a71` as class-(c)
evidence: 298.157 MiB / 1,569 files (docs/artifacts.md:112 and the paragraph at
:150-163), restored and hash-verified end to end at the Phase-19 close ("OK:
2953/2953 files match 476a1f85…", audits/audit-phase-19-close.md:52), with
`scripts/verify_ml_evidence.py`'s availability leg already carrying both the
recovered row and a recorded-loss ruling (:529 `read_slate_ruling`, :2293, :2346; the
two paths are pinned at tests/scripts/test_verify_ml_evidence.py:264-269 and
:968-1000).

What the review actually caught is still true and still unfixed: the document a
research reader opens does not say any of that.
training/reports/report-finalist-eval.md:115-118 still states the provenance
separation as "the raw recordings … live **outside** the repo tree"; :1066-1070 still
names `~/ailibi-campaign-1826/scoring/<arm>/` as the source of every §16 cell; and
the report's one availability erratum (§19, :2618) still locates the bytes on the
temporary `evidence/raw-slate-staging` ref @ `c27ab7b5…` and says Task 19.22 "folds
them" into `evidence/phase-18-coevo` — a promise recorded with no destination sha, no
restore command and no verification result, so the reader has no way to see it kept.
So the central ML ruling still reads as resting on evidence outside the repo, one
restore command away from being auditable. The nine
`/Users/danielkeinan/ailibi-campaign-1826/…` `replay_set_dir` values in
`training/reports/results-finalist-eval.jsonl` stay verbatim by design (the
as-recorded rule at report :569, §9.2) and are not an edit target — they need an
explanation the reader can follow, not a rewrite.

This task closes all four in one pass, additively, and post-record: it moves no
recorded byte, edits no prompt template, introduces no lever, and changes no
production module. The slate half is written for two outcomes because only the owner
can settle it — the agent prepares both and the owner picks in the PR.

**Files in scope:**
- README.md; (the ADR sentence made true, plus at most one clause in the determinism block naming the sidecar if the rewritten block does not already)
- docs/deployment.md; (the four bare `audit C-C-*` citations resolved to their source file; one short subsection explaining the sidecar and its exposure posture)
- docs/artifacts.md; (the finalist raw slate's class and current status legible from the registry row and its detail paragraph, including the one open owner step)
- training/reports/report-finalist-eval.md; (an additive dated erratum stating where the raw slate lives — the evidence-branch commit and the restore command — or that it is de-scoped, with the reason and the reproducibility boundary)
- scripts/fetch_evidence.sh; (touch ONLY if its usage/help text must point a reader at the new erratum — no behaviour change; leaving it untouched is the expected outcome)
- tests/scripts/test_verify_ml_evidence.py; (the real-tree pin: the erratum's sha equals the manifest pin, or the erratum's loss wording equals the recorded ruling)
- docs/reading-guide.md; (ALREADY DELIVERED at HEAD by Task 20.12, PR #371 — the guide carries zero `path:line` citations and `scripts/check_doc_facts.py::check_guide_line_citations` pins that zero, so leaving it untouched is the expected outcome)
- docs/adr/0001-three-load-bearing-decisions.md; (the "verbatim" claim and the dropped ≤100-call qualifier — an additive dated note)

**Files NOT in scope:**
- DESIGN.md (§0 is the source both the README and the ADR restate; it is evidence here, not an edit target)
- training/reports/results-finalist-eval.jsonl (as-recorded measurement bytes; the report's own §9.2 keeps the recorded paths verbatim — the erratum explains them, nothing rewrites them)
- training/artifacts/coevo/EVIDENCE-MANIFEST.md (the pin and the staging-ref owner step live there; this task points at them and changes neither)
- scripts/verify_ml_evidence.py (the availability leg already carries the slate row and both rulings; the new guard is a test, not a production change)
- scripts/check_doc_facts.py (extended by earlier tasks; this task only runs it)
- scripts/build_demo_bundle.py (the generated bundle README's absolute local path is the hosted-demo task's fix)
- orchestrator/replay.py (no lever is introduced, so there is nothing to register in the substrate stamp; lever registration is a separate task's job in any case)
- agents/strategic/prompts/ (no task in this phase except the single prompt-set bump may edit a template; this task edits none)
- replays/, training/ code (nothing is recorded and no measurement is re-run)

**Definition of done:**
- [ ] README.md:117's "recorded verbatim in ADR-0001" (the `## What it is` section) is replaced by a claim a reader can check in one click: the README restates the decisions and names ADR-0001 (and DESIGN.md §0) as the record, and either restates the two figures the ADR carries — the 2 Hz tick target and the ≤ 100-LLM-calls-per-game target — or says explicitly that the ADR carries them. `grep -n "verbatim" README.md` returns no claim about the ADR, and the PR quotes the before/after sentence.
- [ ] Each of docs/deployment.md's four `audit C-C-*` citations (:7, :38, :184, :209) names its source, `audits/audit-2026-05-30-0059-mvp-close.md`, at least once per section, so no id is resolvable only by grep; the PR quotes `grep -n 'audit C-C-' docs/deployment.md` showing every remaining hit resolved.
- [ ] docs/deployment.md gains one short subsection explaining the `*.audit.jsonl` sidecar: what writes it (the default at orchestrator/game.py, overridable by `--audit-log-path` at scripts/run_game.py), what it holds (the observation-service packet log the firewall's leak scan reads), that it is class (d) and gitignored (.gitignore:31, docs/artifacts.md:113), and — the exposure-relevant part this document exists for — that it is a GM-view artifact that never ships beside the public bundle. If the rewritten README determinism block does not already name the extra file, one clause is added there pointing at this subsection.
- [ ] The finalist raw slate's status is stated where each of its readers lands: docs/artifacts.md's registry row and its class-(c) detail paragraph state the current ruling and the one remaining owner step (the staging-ref deletion that GitHub refused, whose one-command form lives in the coevo evidence manifest §4), and training/reports/report-finalist-eval.md gains a new dated erratum section numbered after §19, following the same "additive, no in-place rewrites" convention §18 and §19 already use.
- [ ] On the COMMIT path the erratum names the pinned commit `evidence/phase-18-coevo` @ its sha, the one restore command, and the verification result it produced, and states in one sentence that §2's "outside the repo tree" separation (:115-118), §16's `~/ailibi-campaign-1826/scoring/<arm>/` sources (:1066-1070) and the nine `/Users/…` `replay_set_dir` values kept verbatim in results-finalist-eval.jsonl per §9.2 all resolve to those pinned bytes. On the DE-SCOPE path the erratum instead records the loss with its date, its reason, and the exact reproducibility boundary (which derived cells remain reproducible from committed rows and which event-level lineage does not), and docs/artifacts.md carries the matching ruling. Neither path rewrites §2, §9.2 or §16 in place.
- [ ] A new test in tests/scripts/test_verify_ml_evidence.py's real-tree section pins the erratum against the machinery: on the commit path the sha named in the report's availability erratum equals `verify_ml_evidence.read_pinned_sha(repo_root)`; on the de-scope path the erratum's loss wording agrees with `verify_ml_evidence.read_slate_ruling(repo_root)`. The test ships with a perturbation leg — a copy of the erratum text with the sha (or the ruling word) altered must FAIL it — so the gate can be seen to fail.
- [ ] `uv run python scripts/verify_ml_evidence.py --complete` is green and the PR quotes the availability leg's slate row verbatim; `uv run python scripts/check_doc_facts.py` is green.
- [ ] scripts/fetch_evidence.sh is unchanged, or its diff is comment/usage text only and the PR says why it was needed; no restore, verify or clean behaviour moves.
- [ ] Every sentence this task adds or changes names the file or command a reader checks it with; the PR's Decisions section lists each one beside that mechanism, and records which slate path the owner chose and on what evidence.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import check_doc_facts"`
- `uv run python -c "import eval.leak_scan"`
- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`
- `uv run python -c "import tests._helpers.committed"`
- `uv run python -c "import eval.validity"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-20-tail-truth` with a title like `task 20.41: tail truth: verifiable-shaped claims, the reading guide's anchors, and the finalist raw slate's status`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/C/collated-portfolio.md §B9 (verifiable-shaped claims and the three named wobbles), §B10 (the finalist raw slate), §B3 (the reading guide's `file:line` citations — ALREADY CLOSED at HEAD by Task 20.12, PR #371: the guide was rewritten to heading anchors and the zero is gate-pinned by `scripts/check_doc_facts.py::check_guide_line_citations`, so nothing is left for this task there); audits/review-2026-08-19/C/x1-front-door-reproduction.md reproduction row 1 (the unmentioned `r1.audit.jsonl` sidecar, 38,881 B beside two 50,337-byte replays), GOOD-9, GOOD-11, GOOD-12 and the "ADR-0001 vs README" note; audits/review-2026-08-19/C/p2-ml-research-lead.md §3:33 (weakest-3 item 3: the 449-game slate behind the adoption ruling is not in the repo) and §7:94 (the GOOD item: commit or explicitly de-scope it); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 row 3.6. Re-verified at HEAD: README.md:117 ("recorded verbatim in ADR-0001", now under the `## What it is` heading — re-locate by the heading; the front-door rework moved it from :72) vs docs/adr/0001-three-load-bearing-decisions.md:5 (author Codex), :14 (target 2 Hz), :16 (≤ 100 LLM calls) and DESIGN.md §0 (whose call-target sentence carries a parenthetical the ADR drops); docs/deployment.md:7, :38, :184, :209 (bare `audit C-C-1 / C-C-2 / C-C-4` — Task 20.7's Pages section pushed the two headings down from :104, :129) resolving to audits/audit-2026-05-30-0059-mvp-close.md:53-55 + :164; scripts/run_game.py:46-49 and orchestrator/game.py:1660-1666 (the `<replay-stem>.audit.jsonl` default, now the `else` arm of the no-replay guard added at :1651-1659) with README.md:38-43 (the determinism block — ONE command block now, under `## Verify it yourself in one minute`; the duplicate at :119-120 is gone) and .gitignore:31 + docs/artifacts.md:113 (class (d)); docs/artifacts.md:106, :112, :123, :150-163; training/reports/report-finalist-eval.md:115-118, :569 (§9.2 as-recorded paths), :1066-1070, :2618-2684 (§19, the Task 19.21 erratum); training/reports/results-finalist-eval.jsonl (9 rows carrying `/Users/danielkeinan/ailibi-campaign-1826/…`); scripts/verify_ml_evidence.py:109-111, :120, :516-526 (`read_pinned_sha`), :529 (`read_slate_ruling`), :2293, :2346; tests/scripts/test_verify_ml_evidence.py:212 (the real-tree section header), :264-269 (`test_availability_registry_covers_the_document`), :968-1000 (`test_the_loss_path_may_omit_the_slate_manifest`), :1075-1104 (`test_complete_accepts_a_manifestless_recorded_loss_end_to_end`); audits/audit-phase-19-close.md:52 ("OK: 2953/2953 files match 476a1f85…"), :387.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
