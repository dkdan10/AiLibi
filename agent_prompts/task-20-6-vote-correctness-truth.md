# Agent Prompt — 20.6 vote_correctness tells the truth: docstring, doc-fact pin, and the six zero-flag ejections

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.6 — vote_correctness tells the truth: docstring, doc-fact pin, and the six zero-flag ejections, anchored to C-113 (audits/review-2026-08-19/B/eval-and-scripts.md §F2; audits/review-2026-08-19/B/collated-findings.md row C-113; audits/review-2026-08-19/D/FINAL-synthesis.md §2 row 12 [D-VERIFIED], §4 wave-0 item 0.7, ruling R8; audits/review-2026-08-19/D/synth-credibility.md §row 7; audits/review-2026-08-19/D/cross-track-map.md C-113 row); audits/audit-phase-20-planning.md:75-76 (the phase's wave-0 slate names this task); eval/vote_correctness.py:11-25 (the module-docstring paragraph; :17 "structurally pinned to 1.0", :19-21 "any value below 1.0 … a detector/recording bug to chase"), :90-94 (the same claim restated for the 9.5 baseline), :224-231 (`VoteCorrectnessReport`'s class docstring repeats the pin), :182 (`KILL_WITNESS_TICK_WINDOW`), :320 (`compute_vote_correctness`), :393/:406/:412 (`_has_real_evidence` and its two disjuncts); replays/samples/9p2i/tournament-eval-report.json → `impostor_ejections=78, evidence_backed_impostor_ejections=72, vote_correctness_rate=0.9230769230769231`; replays/samples/4p1i/tournament-eval-report.json → 10/10 = 1.0; replays/ml_corpus/9p2i/tournament-eval-report.json → 235/248 = 0.9475806451612904; replays/ml_corpus/4p1i/tournament-eval-report.json → 20/20 = 1.0; tests/eval/test_vote_correctness.py:1869-1922 (the committed-9p2i pin ALREADY asserts 72/78 at :1914 — the module's prose contradicts its own test file); meetings/manager.py:2004-2019 (the citation-gate comment block and its call site) and :3259-3350 (`guard_ballot_citation`: "A flagged target is convictable uncited … the ballot cites NOTHING" — a zero-flag EJECT that cites a turn or an observation id passes), meetings/constants.py:55-70 (the gate is unconditional since the 16.17 baseline-5 record); eval/vj_instruments.py:12, :93-106, :737 (Task 16.10 already instruments the zero-flag conviction channel with a typed provenance split); scripts/check_doc_facts.py:125-171 (`main` / `check_facts`), :172 (`check_sample_provenance`, the per-check shape), :595 (`read_document`, the `--repo-root` convention); tests/scripts/test_check_doc_facts.py:29-52 (`_COPIED` + the `doc_tree` perturbation fixture), :71-78 (the both-sides contract); README.md:194 (the metric's only README mention — a one-line description that carries NO structural-1.0 claim: C-113's README leg is refuted); frontend/src/components/TournamentDashboard.tsx:226-228 and :241 (the repeating surface — the copy pass owns it, not this task); AGENTS.md:83-102 (craft rules 1, 2, 5). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-vote-correctness-truth`
**Depends on:** none (root)
**Section refs:** C-113 (audits/review-2026-08-19/B/eval-and-scripts.md §F2; audits/review-2026-08-19/B/collated-findings.md row C-113; audits/review-2026-08-19/D/FINAL-synthesis.md §2 row 12 [D-VERIFIED], §4 wave-0 item 0.7, ruling R8; audits/review-2026-08-19/D/synth-credibility.md §row 7; audits/review-2026-08-19/D/cross-track-map.md C-113 row); audits/audit-phase-20-planning.md:75-76 (the phase's wave-0 slate names this task); eval/vote_correctness.py:11-25 (the module-docstring paragraph; :17 "structurally pinned to 1.0", :19-21 "any value below 1.0 … a detector/recording bug to chase"), :90-94 (the same claim restated for the 9.5 baseline), :224-231 (`VoteCorrectnessReport`'s class docstring repeats the pin), :182 (`KILL_WITNESS_TICK_WINDOW`), :320 (`compute_vote_correctness`), :393/:406/:412 (`_has_real_evidence` and its two disjuncts); replays/samples/9p2i/tournament-eval-report.json → `impostor_ejections=78, evidence_backed_impostor_ejections=72, vote_correctness_rate=0.9230769230769231`; replays/samples/4p1i/tournament-eval-report.json → 10/10 = 1.0; replays/ml_corpus/9p2i/tournament-eval-report.json → 235/248 = 0.9475806451612904; replays/ml_corpus/4p1i/tournament-eval-report.json → 20/20 = 1.0; tests/eval/test_vote_correctness.py:1869-1922 (the committed-9p2i pin ALREADY asserts 72/78 at :1914 — the module's prose contradicts its own test file); meetings/manager.py:2004-2019 (the citation-gate comment block and its call site) and :3259-3350 (`guard_ballot_citation`: "A flagged target is convictable uncited … the ballot cites NOTHING" — a zero-flag EJECT that cites a turn or an observation id passes), meetings/constants.py:55-70 (the gate is unconditional since the 16.17 baseline-5 record); eval/vj_instruments.py:12, :93-106, :737 (Task 16.10 already instruments the zero-flag conviction channel with a typed provenance split); scripts/check_doc_facts.py:125-171 (`main` / `check_facts`), :172 (`check_sample_provenance`, the per-check shape), :595 (`read_document`, the `--repo-root` convention); tests/scripts/test_check_doc_facts.py:29-52 (`_COPIED` + the `doc_tree` perturbation fixture), :71-78 (the both-sides contract); README.md:194 (the metric's only README mention — a one-line description that carries NO structural-1.0 claim: C-113's README leg is refuted); frontend/src/components/TournamentDashboard.tsx:226-228 and :241 (the repeating surface — the copy pass owns it, not this task); AGENTS.md:83-102 (craft rules 1, 2, 5)
**Complexity:** Small
**Record impact:** none
**Measurement:** `uv run python scripts/check_doc_facts.py` exits 0; `uv run pytest tests/eval/test_vote_correctness.py tests/scripts/test_check_doc_facts.py -q` green; the census pin lists exactly 6 non-evidence-backed impostor ejections over replays/samples/9p2i (seeds 4, 17, 18, 22, 29, 40) and exactly 8 zero-naming-flag ones (those six plus seeds 26 and 38, which the kill-witness-chain disjunct backs); the two perturbation legs in tests/scripts/test_check_doc_facts.py each fail with a message naming the drifted fact.

The repo's thesis is that its prose and its committed bytes never disagree, and this is the
one place a reader can catch them disagreeing in under a minute. `eval/vote_correctness.py`
opens by declaring `vote_correctness_rate` **"structurally pinned to 1.0"**, with the
operational rule that "any value below 1.0 on a recorded set means an impostor ejection
happened WITHOUT its own triggering evidence — a detector/recording bug to chase"
(:17-21, restated at :90-94 and again in the `VoteCorrectnessReport` class docstring at
:224-231). The committed flagship artifact reads **0.9230769** (72 of 78 impostor
ejections evidence-backed). A reader who follows the docstring files a bug; a reader who
reads the test file finds the number already pinned at `tests/eval/test_vote_correctness.py:1914`
— the module's own regression test has been asserting 72/78 while its docstring called that
value impossible. Nothing in the repo surfaces the contradiction.

The mechanism sentence is the part that is actually false. The docstring's argument is that
"the §4.6 vote gate only crosses the eject threshold when the contradiction detector flagged
the ejected player" (:12-16), so `evidence_backed_impostor_ejections == impostor_ejections`
by construction. That has not been true since the Task 16.6 citation gate: `guard_ballot_citation`
(meetings/manager.py:3259-3350) coerces a zero-flag EJECT ballot to SKIP **only when it cites
nothing** — a zero-flag target convicted on a ballot citing a transcript turn or a private
observation id is legal by design, and the gate has been unconditional since the 16.17
baseline-5 record (meetings/constants.py:55-70). The re-derivation at HEAD shows exactly that
shape: in all six of the 9p2i counter-examples the meeting recorded **zero** `ContradictionRef`
rows and the eject ballots cited a transcript turn (seed 4's three ejectors all cite
`headless-seed-4:meeting-2:turn-2`). The claim is not a recording bug; it is a stale claim
about a substrate two phases old.

Re-derived at HEAD with the module's own predicate over the four committed reports:
samples/9p2i 72/78 = 0.923 (6 not evidence-backed), ml_corpus/9p2i 235/248 = 0.9476 (13 not
evidence-backed), samples/4p1i 10/10 = 1.0, ml_corpus/4p1i 20/20 = 1.0. The six 9p2i
counter-examples are seeds 4, 17, 18, 22, 29 and 40 — matching the review's probe
(audits/review-2026-08-19/B/eval-and-scripts.md §F2) seed for seed. One correction the review
did not draw: **eight** impostor ejections carry no naming `ContradictionRef` at all; two of
them (seeds 26 and 38) are rescued by `_has_kill_witness_chain`, the metric's second disjunct.
"Zero-flag" and "not evidence-backed" are therefore different populations, and a census that
conflates them would re-import the confusion this task exists to remove.

The review's ruling R8 (audits/review-2026-08-19/D/FINAL-synthesis.md §R8) narrows the blast
radius: the "README sells it as the circularity guard" leg is **refuted** — README.md:194
carries only a neutral one-line description of what the analyzer asks, with no pinned value.
Do not edit README.md. The one repeating user-facing surface is the Tournament tooltip
(frontend/src/components/TournamentDashboard.tsx:226-228, :241, "the live §4.6 pipeline pins
it to 1.0 by construction"); the Phase-20 spectator copy pass owns that string and lands
independently of this task, so this task's doc-fact check must NOT scan frontend copy — a
check that did would go red on `main` until the copy pass merged, and both tasks are roots.

This task ships three things and no behaviour: an honest docstring, a check that bites when
the prose and the data diverge again, and a pinned census of the counter-examples with a
stated classification rule so the next reader inherits an answer instead of an anomaly. Zero
production bytes move — no analyzer arithmetic changes, no report is regenerated, no replay
is touched — so `Record impact: none`, and the two byte pins (the prompt byte-golden and
`scripts/verify_samples.sh`) are unaffected by construction.

**Files in scope:**
- eval/vote_correctness.py; (docstring and comment lines ONLY — the module docstring's pin paragraph, the :90-94 restatement, and the `VoteCorrectnessReport` class docstring; zero behaviour bytes)
- scripts/check_doc_facts.py; (a fourth check: the module's documented semantics against the committed reports' recomputed values)
- tests/scripts/test_check_doc_facts.py; (the committed tree passes; the two perturbation legs fail, each naming the drifted fact)
- tests/eval/test_vote_correctness.py; (the census of the six non-evidence-backed and eight zero-naming-flag impostor ejections over samples/9p2i, each classified under a stated rule)

**Files NOT in scope:**
- README.md (its only mention carries no structural-1.0 claim — ruling R8 refutes that leg; the front-door rewrite owns the file and depends on this task's recorded wording)
- frontend/src/components/TournamentDashboard.tsx (the tooltip repeats the claim; the spectator copy pass owns it and lands independently — the new check must not read frontend copy)
- replays/ (bytes never move; the four committed reports are read, never rewritten)
- eval/vote_correctness.py's executable body — `compute_vote_correctness`, `_has_real_evidence`, `_has_naming_contradiction`, `_has_kill_witness_chain`, `KILL_WITNESS_TICK_WINDOW` (the arithmetic is correct; only its description is wrong)
- eval/vj_instruments.py (the Task 16.10 zero-flag channel is read as the reference definition, never edited)
- scripts/check.sh (`check_doc_facts` deliberately runs via pytest, not the gate script; wiring it in is a separate decision)

**Definition of done:**
- [ ] `eval/vote_correctness.py`'s module docstring and `VoteCorrectnessReport` class docstring state what the metric measures (the evidence-backed share of impostor ejections, under the two named disjuncts) and what a sub-1.0 value means on this substrate — that a zero-flag EJECT citing a transcript turn or an observation id is legal since the Task 16.6 citation gate — and a repo grep for "structurally pinned", "pinned to 1.0" and "pins it to 1.0" over `eval/` returns nothing; the PR quotes the grep.
- [ ] The rewritten paragraphs lead with intent per AGENTS.md craft rule 1: at most one trailing provenance line each, and the module-docstring line count (155 at HEAD) is quoted before and after in the PR. A whole-module prose sweep is explicitly NOT required — only the paragraphs this task rewrites.
- [ ] The docstring states the committed values in a single machine-checkable sentence per sample set, each stamped with its set and the baseline-6 record, and the four values agree with the committed reports (samples/9p2i 72/78, samples/4p1i 10/10, ml_corpus/9p2i 235/248, ml_corpus/4p1i 20/20).
- [ ] `scripts/check_doc_facts.py` gains `check_vote_correctness_sentinel`, wired into `check_facts`, which (a) re-derives each committed report's `evidence_backed_impostor_ejections / impostor_ejections` from the JSON under `--repo-root` and requires the docstring's stamped sentence for that set to carry the recomputed numerator, denominator and rate, and (b) fails when the docstring asserts a structural pin the data contradicts. The rate is RE-DERIVED at run time, never a literal in the checker, so a future re-record only re-stamps the docstring.
- [ ] `tests/scripts/test_check_doc_facts.py` proves the check bites both ways (craft rule 2): `check_facts(_REPO_ROOT) == []` on the committed tree; perturbing the copied `eval/vote_correctness.py` to reinstate a structural-pin sentence fails with a message naming the phrase; perturbing the copied `replays/samples/9p2i/tournament-eval-report.json` rate fails with a message naming the set and both values. The `_COPIED` fixture list grows by exactly the files the new check reads.
- [ ] `tests/eval/test_vote_correctness.py` pins a census over the committed samples/9p2i report: exactly 6 impostor ejections fail `_has_real_evidence` (seeds 4, 17, 18, 22, 29, 40, with meeting id, tick and ejectee), and exactly 8 carry no naming `ContradictionRef` (those six plus seeds 26 and 38, which the kill-witness chain backs). The two populations are asserted separately and the test docstring says why they differ.
- [ ] Each of the six is classified **detector miss** or **rhetoric-only conviction** under one rule stated in the test docstring, and the rule is decidable from recorded bytes alone: detector-miss iff the meeting's transcript contains the structured pair the detector is specified to flag against the ejectee (a `SawPlayerObservation` / `WhereaboutsClaim` conflict or a vent sighting naming them) while `contradictions` mints nothing for that subject; rhetoric-only otherwise (the eject ballots cite turns that carry no such pair). The counts per class are pinned; whichever way the six split, the split is a recorded finding, not a code change.
- [ ] No production behaviour changes: the `eval/vote_correctness.py` diff is comment and docstring lines only (the PR quotes `git diff -U0 eval/vote_correctness.py` showing no executable line), and `bash scripts/verify_samples.sh` plus the prompt byte-golden stay green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Public types this task introduces
- `check_doc_facts.check_vote_correctness_sentinel`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-20-vote-correctness-truth` with a title like `task 20.6: vote_correctness tells the truth: docstring, doc-fact pin, and the six zero-flag ejections`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing C-113 (audits/review-2026-08-19/B/eval-and-scripts.md §F2; audits/review-2026-08-19/B/collated-findings.md row C-113; audits/review-2026-08-19/D/FINAL-synthesis.md §2 row 12 [D-VERIFIED], §4 wave-0 item 0.7, ruling R8; audits/review-2026-08-19/D/synth-credibility.md §row 7; audits/review-2026-08-19/D/cross-track-map.md C-113 row); audits/audit-phase-20-planning.md:75-76 (the phase's wave-0 slate names this task); eval/vote_correctness.py:11-25 (the module-docstring paragraph; :17 "structurally pinned to 1.0", :19-21 "any value below 1.0 … a detector/recording bug to chase"), :90-94 (the same claim restated for the 9.5 baseline), :224-231 (`VoteCorrectnessReport`'s class docstring repeats the pin), :182 (`KILL_WITNESS_TICK_WINDOW`), :320 (`compute_vote_correctness`), :393/:406/:412 (`_has_real_evidence` and its two disjuncts); replays/samples/9p2i/tournament-eval-report.json → `impostor_ejections=78, evidence_backed_impostor_ejections=72, vote_correctness_rate=0.9230769230769231`; replays/samples/4p1i/tournament-eval-report.json → 10/10 = 1.0; replays/ml_corpus/9p2i/tournament-eval-report.json → 235/248 = 0.9475806451612904; replays/ml_corpus/4p1i/tournament-eval-report.json → 20/20 = 1.0; tests/eval/test_vote_correctness.py:1869-1922 (the committed-9p2i pin ALREADY asserts 72/78 at :1914 — the module's prose contradicts its own test file); meetings/manager.py:2004-2019 (the citation-gate comment block and its call site) and :3259-3350 (`guard_ballot_citation`: "A flagged target is convictable uncited … the ballot cites NOTHING" — a zero-flag EJECT that cites a turn or an observation id passes), meetings/constants.py:55-70 (the gate is unconditional since the 16.17 baseline-5 record); eval/vj_instruments.py:12, :93-106, :737 (Task 16.10 already instruments the zero-flag conviction channel with a typed provenance split); scripts/check_doc_facts.py:125-171 (`main` / `check_facts`), :172 (`check_sample_provenance`, the per-check shape), :595 (`read_document`, the `--repo-root` convention); tests/scripts/test_check_doc_facts.py:29-52 (`_COPIED` + the `doc_tree` perturbation fixture), :71-78 (the both-sides contract); README.md:194 (the metric's only README mention — a one-line description that carries NO structural-1.0 claim: C-113's README leg is refuted); frontend/src/components/TournamentDashboard.tsx:226-228 and :241 (the repeating surface — the copy pass owns it, not this task); AGENTS.md:83-102 (craft rules 1, 2, 5)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
