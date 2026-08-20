# Agent Prompt — 20.13 The results stated once: docs/ml-program.md, the README results table, and the comparator-defect errata

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.13 — The results stated once: docs/ml-program.md, the README results table, and the comparator-defect errata, anchored to audits/review-2026-08-19/C/collated-portfolio.md §A6 (state the results once — MUST for the research lead, GOOD for three more personas; the concrete fix names both halves, the README table and the ≤2-page page); audits/review-2026-08-19/C/p2-ml-research-lead.md §3 Weakest-1 ("no artifact tells the ML story in the standard research shape … `training/README.md` is a tier map, not that document") + §6 ("the single change that would most raise it") + §7 MUST-2; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 rows 1.7 and 1.8 (the two roadmap items this task implements), §2 row 5 (the "(suspicion, trust, alibi)" claim graded UNDERMINED) and §2 row 9 (the win edge graded CAVEAT — "the method holds, one input is contaminated"); audits/review-2026-08-19/B/collated-findings.md C-72 (`trust` never written; `## Open contradictions` rendered in 0 of 1,656 replay renders); audits/review-2026-08-19/B/verdicts.md C-3 (CONFIRMED **and understated** — 190/415 = 45.8 % of free zero-witness kills declined over the 50 committed 9p2i seeds, 168/168 of them on an exact 1.0 score tie broken by the lower id; the reconstruction replays `decide()` against the recorded bytes with an empty `policy_would_kill_but_action_differs` bucket); audits/review-2026-08-19/A/verdicts.md G-12 (CONFIRMED-BUG — 10,335 impostor decisions re-run offline with 0 mismatches; ghost-top 303/2461 = 12.3 % on samples/9p2i, 555/6663 = 8.3 % on ml_corpus/9p2i, 0/632 and 0/579 across the two 4p1i sets; seed 36 provably thrown) — **both rates are now committed pins**, landed by 20.15 (PR #365): tests/agents/test_impostor_policy.py:1812-1864 (`TestCommittedCorpusTargetingPins` — 190/415 with the 168 / 15 / 7 / 0 decline-reason split, ghost-top 303/2461, 555/6663, 0/632, 0/579, 222 ejected / 81 unseen on samples/9p2i, 0 reconstruction mismatches over 10,335 decisions) computed by eval/evidence_honesty.py's I-11 cells, with audits/audit-phase-20-preregistration.md:174-175 stating all four sets [VERIFIED]; README.md:83 (the belief-state sentence as 20.12 left it — the "(suspicion, trust, alibi)" wording is already gone, so this leg is verify-only), :88-96 (the "What the measurements said" section and table 20.12 built, whose 100/100, 520/520 and 87 % rows this task keeps), :100 (the marked anchor `<!-- ANCHOR: a later contract adds the ML program's paragraph, titled by its result, plus the table's before/after column. -->` this task fills), :107 (the numberless "Four learned tactical policies each beat the scripted one on wins" sentence — the "+0.12 to +0.30" and "+0.16" figures no longer appear in README and now live only in the two close audits); docs/adr/0001-three-load-bearing-decisions.md:18 (decision 3 — "trust scores, alibi map, suspicion graph"); agents/memory/beliefs.py:1111 (`adjust_trust` — the definition is the only non-test occurrence in the tree; seven callers, all under `tests/`), :1493 (`record_contradiction` inside `apply_contradiction_rule` at :1340 — the write lands on the derived result, not the persistent store) with agents/memory/store.py:1811 (the `## Open contradictions:` block that renders); audits/audit-phase-19-close.md §4.1 (pooled 310/310 = 1.000 with direct proof vs 46/125 = 0.368 without; 79/79 of innocent ejections in the non-direct cell); audits/audit-phase-18-close.md:78-84 (the four-arm table: win 0.52 / 0.56 / 0.38 / 0.42857 vs the fresh same-seed `p18-fsm-comparator` 13/50 = 0.26, referee FAIL ×4), :105 ("+0.12 to +0.30"); audits/audit-phase-17-close.md:25 and :60 (`utility-es` win 0.52 = 26/50, Δ +0.16 over the same-seed FSM 0.36, referee FAIL on two gauges); audits/audit-phase-18-flip-emergence.md:466-481 (N1 witnessed-kill rate 30/197 = 0.15228 vs 8/174 = 0.04598, z = +3.370; N2 co-present kills 20/197 = 0.10152 vs 0/174, z = +4.321; both NOT-DEMONSTRATED because clause (c) is unsatisfiable by construction); docs/reading-guide.md:11-22 (§1 "The numbers worth knowing" — the canonical numbers table after the 20.12 trim, rows at :15-22), :57-84 (§3 "What the corpus demonstrates — and what it does not", the 165-meeting cross-tab 68/2 flagged vs 10/21 unflagged at :74-77), :102 (the marked anchor `<!-- ANCHOR: a later contract adds the research-shaped ML page and links it here. -->`; the old §6 ML story was cut in the trim and the file now has five sections); training/README.md:1 (the title — a disposition ledger), :128-165 (§3 what the program positively learned); agents/tactical/learned/forward.py:14 (the 19-weight linear scorer, no numpy/torch), :111 (`ENCODER_VERSION = "impostor-option-features-v1"`), :114 (`GENOME_LENGTH` = 18 features + bias); training/env.py:1-40 (the rollout env drives the real `HeadlessGame`; the legal-action mask is derived from `engine/rules.py`); training/rewards.py:16-26 (the corrected shaping claim — telescoping is not invariance); eval/watchability.py:9-20 (SELECTION-ONLY — the referee is a champion gate and is NEVER a training reward); scripts/paired_stats.py:1-36 (stdlib-only exact McNemar + Wilson, written so a fresh clone reproduces the cells); training/reports/report-finalist-eval.md:2493 (the §18 errata form — additive, dated, nothing above it rewritten). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-results-page`
**Depends on:** 20.12 (the front-door rewrite lands first — this task fills the results section and the ML paragraph that rewrite leaves anchored, and quotes the reading guide only after its trim); also after 20.11 (the engine-rule line both tasks add to the design record lands first)
**Section refs:** audits/review-2026-08-19/C/collated-portfolio.md §A6 (state the results once — MUST for the research lead, GOOD for three more personas; the concrete fix names both halves, the README table and the ≤2-page page); audits/review-2026-08-19/C/p2-ml-research-lead.md §3 Weakest-1 ("no artifact tells the ML story in the standard research shape … `training/README.md` is a tier map, not that document") + §6 ("the single change that would most raise it") + §7 MUST-2; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 rows 1.7 and 1.8 (the two roadmap items this task implements), §2 row 5 (the "(suspicion, trust, alibi)" claim graded UNDERMINED) and §2 row 9 (the win edge graded CAVEAT — "the method holds, one input is contaminated"); audits/review-2026-08-19/B/collated-findings.md C-72 (`trust` never written; `## Open contradictions` rendered in 0 of 1,656 replay renders); audits/review-2026-08-19/B/verdicts.md C-3 (CONFIRMED **and understated** — 190/415 = 45.8 % of free zero-witness kills declined over the 50 committed 9p2i seeds, 168/168 of them on an exact 1.0 score tie broken by the lower id; the reconstruction replays `decide()` against the recorded bytes with an empty `policy_would_kill_but_action_differs` bucket); audits/review-2026-08-19/A/verdicts.md G-12 (CONFIRMED-BUG — 10,335 impostor decisions re-run offline with 0 mismatches; ghost-top 303/2461 = 12.3 % on samples/9p2i, 555/6663 = 8.3 % on ml_corpus/9p2i, 0/632 and 0/579 across the two 4p1i sets; seed 36 provably thrown) — **both rates are now committed pins**, landed by 20.15 (PR #365): tests/agents/test_impostor_policy.py:1812-1864 (`TestCommittedCorpusTargetingPins` — 190/415 with the 168 / 15 / 7 / 0 decline-reason split, ghost-top 303/2461, 555/6663, 0/632, 0/579, 222 ejected / 81 unseen on samples/9p2i, 0 reconstruction mismatches over 10,335 decisions) computed by eval/evidence_honesty.py's I-11 cells, with audits/audit-phase-20-preregistration.md:174-175 stating all four sets [VERIFIED]; README.md:83 (the belief-state sentence as 20.12 left it — the "(suspicion, trust, alibi)" wording is already gone, so this leg is verify-only), :88-96 (the "What the measurements said" section and table 20.12 built, whose 100/100, 520/520 and 87 % rows this task keeps), :100 (the marked anchor `<!-- ANCHOR: a later contract adds the ML program's paragraph, titled by its result, plus the table's before/after column. -->` this task fills), :107 (the numberless "Four learned tactical policies each beat the scripted one on wins" sentence — the "+0.12 to +0.30" and "+0.16" figures no longer appear in README and now live only in the two close audits); docs/adr/0001-three-load-bearing-decisions.md:18 (decision 3 — "trust scores, alibi map, suspicion graph"); agents/memory/beliefs.py:1111 (`adjust_trust` — the definition is the only non-test occurrence in the tree; seven callers, all under `tests/`), :1493 (`record_contradiction` inside `apply_contradiction_rule` at :1340 — the write lands on the derived result, not the persistent store) with agents/memory/store.py:1811 (the `## Open contradictions:` block that renders); audits/audit-phase-19-close.md §4.1 (pooled 310/310 = 1.000 with direct proof vs 46/125 = 0.368 without; 79/79 of innocent ejections in the non-direct cell); audits/audit-phase-18-close.md:78-84 (the four-arm table: win 0.52 / 0.56 / 0.38 / 0.42857 vs the fresh same-seed `p18-fsm-comparator` 13/50 = 0.26, referee FAIL ×4), :105 ("+0.12 to +0.30"); audits/audit-phase-17-close.md:25 and :60 (`utility-es` win 0.52 = 26/50, Δ +0.16 over the same-seed FSM 0.36, referee FAIL on two gauges); audits/audit-phase-18-flip-emergence.md:466-481 (N1 witnessed-kill rate 30/197 = 0.15228 vs 8/174 = 0.04598, z = +3.370; N2 co-present kills 20/197 = 0.10152 vs 0/174, z = +4.321; both NOT-DEMONSTRATED because clause (c) is unsatisfiable by construction); docs/reading-guide.md:11-22 (§1 "The numbers worth knowing" — the canonical numbers table after the 20.12 trim, rows at :15-22), :57-84 (§3 "What the corpus demonstrates — and what it does not", the 165-meeting cross-tab 68/2 flagged vs 10/21 unflagged at :74-77), :102 (the marked anchor `<!-- ANCHOR: a later contract adds the research-shaped ML page and links it here. -->`; the old §6 ML story was cut in the trim and the file now has five sections); training/README.md:1 (the title — a disposition ledger), :128-165 (§3 what the program positively learned); agents/tactical/learned/forward.py:14 (the 19-weight linear scorer, no numpy/torch), :111 (`ENCODER_VERSION = "impostor-option-features-v1"`), :114 (`GENOME_LENGTH` = 18 features + bias); training/env.py:1-40 (the rollout env drives the real `HeadlessGame`; the legal-action mask is derived from `engine/rules.py`); training/rewards.py:16-26 (the corrected shaping claim — telescoping is not invariance); eval/watchability.py:9-20 (SELECTION-ONLY — the referee is a champion gate and is NEVER a training reward); scripts/paired_stats.py:1-36 (stdlib-only exact McNemar + Wilson, written so a fresh clone reproduces the cells); training/reports/report-finalist-eval.md:2493 (the §18 errata form — additive, dated, nothing above it rewritten)
**Complexity:** Medium
**Record impact:** none (documentation and errata only — no rendered, detector, replay or report byte moves, so nothing here waits on the Phase-20 adopting record)
**Measurement:** `uv run python scripts/paired_stats.py training/reports/results-finalist-eval.jsonl` reproduces every McNemar cell the results table states (ea4bc955 17/4 p=0.0072; bfd145cb 20/5 p=0.0041; shipped 6d327dcb 15/9 p=0.3075 n.s.; 7f73929d 12/3 p=0.0352, failing Bonferroni α=0.0125), output pasted into the PR Summary; `uv run python scripts/check_doc_facts.py` green; `uv run pytest tests/scripts/test_check_doc_facts.py -q` green; `wc -w docs/ml-program.md` ≤ ~1,400.

The repo's best numbers are the ones it never states. The 19.14 partition, committed and
re-quoted at `audits/audit-phase-19-close.md` §4.1, reads: **310/310 = 1.000 conviction
accuracy where the substrate hands the crew direct proof, 46/125 = 0.368 where it does not,
and 79 of 79 innocent ejections in the non-direct cell.** That is the sharpest measured
statement in the project — a social-deduction environment whose convictions are perfect on
engine-certified evidence and worse than a coin flip on inference — and the README states
none of it. Four portfolio personas independently reached for the same repair
(`audits/review-2026-08-19/C/collated-portfolio.md` §A6): the research lead called the
missing artifact "the single change that would most raise it"
(`audits/review-2026-08-19/C/p2-ml-research-lead.md` §6), having spent forty minutes to
find that `training/README.md`'s own title is a keep/freeze/retire disposition ledger
(`training/README.md:1`) and that the program summary he wanted is §3, buried past ~150
lines of tier tables. The numbers themselves are fine: the review re-derived the McNemar
table and the vent cross-tab from committed files with stdlib and got exact agreement. The
defect is location and shape, and it is repaired with text.

This task writes the two artifacts the review names. `docs/ml-program.md` (new, ≤2 pages) tells
the ML story in the standard research shape: problem; environment (observation, action mask
and reward in one paragraph plus one inline figure — the rollout env drives the real
`HeadlessGame` with the mask derived from `engine/rules.py`, `training/env.py:1-40`, and the
shaping term telescopes without being policy-invariant, `training/rewards.py:16-26`); method
(ES over a 19-weight linear utility scorer — 18 features plus bias on the
`impostor-option-features-v1` basis, `agents/tactical/learned/forward.py:14`, `:111`, `:114`
— with the referee as a SELECTION gate and never a training reward,
`eval/watchability.py:9-20`); one results table (arm · impostor win vs the same-seed
comparator · exact McNemar p · referee verdict) built from
`audits/audit-phase-18-close.md:78-84` and reproduced by `scripts/paired_stats.py`; N1 and N2
framed as what they are — a learned impostor discovering that witnessed kills are cheap
because the conviction engine convicts on vent proof, i.e. specification gaming of a
social-deduction referee (`audits/audit-phase-18-flip-emergence.md:466-481`); limitations
(one model, one prompt set, n=50, the bar's construction, the finalist raw slate off-repo);
and related work, so a reader can place the environment. The README gains the results table
under "What the measurements said" — the rows the review lists, each with its committed
source and, where the number is volatile, its baseline and record date — plus one ML
paragraph titled by its result rather than by its process.

Two claims get corrected in the same pass because they are the ones a hostile reader breaks
first. **The memory claim.** `docs/adr/0001-three-load-bearing-decisions.md:18` still
advertises a three-channel belief state (20.12 already removed the claim from README, whose
:83 now reads "a belief state derived from it"); `trust` has no production writer at HEAD
(`agents/memory/beliefs.py:1111` is the definition, and the only other callers in the tree are
seven under `tests/`), and the contradictions block at `agents/memory/store.py:1811` rendered
in 0 of 1,656 replay renders the review sampled — the `record_contradiction` call at
`agents/memory/beliefs.py:1493` writes a derived state inside `apply_contradiction_rule`, and
nothing persists it (`audits/review-2026-08-19/B/collated-findings.md` C-72;
`audits/review-2026-08-19/D/FINAL-synthesis.md` §2 row 5 grades the claim UNDERMINED). The
README needed no further repair on this claim — 20.12 already dropped the three-channel
wording, so this task only re-verifies it at HEAD; the ADR is a record of a 2026-05-01 decision and gets an
additive dated note, never a rewrite.

And **the comparator claim.** The "+0.12 to +0.30" and "+0.16" win edges over the same-seed
scripted FSM no longer appear in README (20.12 cut the figures; :107 now states the edge in
words), but both close audits record the cells and are the surface a reader reaches. The review found
the comparator carries two identified target-selection defects, both 9p2i-only, both depressing
the FSM: the kill seam re-validates only `targets[0]`, so **190/415 = 45.8 %** of free
zero-witness kills are declined — 168 of the 190 in the ranking branch's exact-1.0 score tie
broken by the lower player id, the other 22 in the named fellow-defer (15) and cover (7)
branches with none unattributed (`audits/review-2026-08-19/B/verdicts.md` C-3, verdict CONFIRMED
and understated); and the dead-set is built only from seen bodies, so an ejected player stays
targetable and the mover spends **303/2461 = 12.3 %** (samples/9p2i) and **555/6663 = 8.3 %**
(ml_corpus/9p2i) of its decisions topping its target list with someone the whole table watched
get ejected — **0/632 and 0/579 across the two 4p1i sets** — with seed 36 a demonstrably thrown game
(`audits/review-2026-08-19/A/verdicts.md` G-12, verdict CONFIRMED-BUG; 10,335 decisions re-run
offline with 0 mismatches against the recorded action stream). A project whose thesis is that it
does not publish numbers it knows are confounded cannot leave this unstated: the honest paragraph
lands in `docs/ml-program.md` and, as additive dated errata in the form
`training/reports/report-finalist-eval.md:2493` established, in both close audits. This task
states the confound; the mover repair and the re-measurement on corrected bytes are separate,
later contracts, and the errata say so.

**Files in scope:**
- docs/ml-program.md; (new — problem; environment: observation/action-mask/reward in one paragraph plus one inline figure; method: ES over the 19-weight utility scorer with the referee as selection gate, not reward; one results table: arm, win vs the same-seed FSM, McNemar p, referee verdict; N1/N2 framed as referee exploitation / specification gaming; limitations: one model, n=50, bar construction, raw finalist slate off-repo, the comparator defects; related work)
- README.md; (the "What the measurements said" section — the results table with its sources and baseline stamps, one ML paragraph titled by its result, and the memory-claim wording; no other section moves)
- docs/adr/0001-three-load-bearing-decisions.md; (an additive dated note only — the ADR text is a record of a 2026-05-01 decision and is appended to, never rewritten)
- training/README.md; (program-summary-first, the tier map second, the reopening checklist last; a pointer to docs/ml-program.md as the entry point)
- audits/audit-phase-18-close.md; (an additive dated erratum naming the comparator defects with the measured rates and their instruments)
- audits/audit-phase-17-close.md; (the same erratum for that close's win-edge figures)
- scripts/check_doc_facts.py; (the results table's new numbers checked against their committed sources)
- tests/scripts/test_check_doc_facts.py
- DESIGN.md; (the §6.6 target-not-as-built caption only — historical content untouched)
- docs/reading-guide.md; (TWO edits only: the numbers-table row(s) mirroring whatever this task adds to the README results table — `scripts/check_doc_facts.py::check_results_agreement` fails any README results row with no identical-figure match in the guide's canonical table — and the marked anchor at :102, replaced by a link to docs/ml-program.md; the 20.12 trim is not re-opened)

**Files NOT in scope:**
- training/ code and artifacts (nothing retrains and nothing is re-fit; every number is quoted from a committed report or audit and re-derived with `scripts/paired_stats.py`)
- docs/reading-guide.md beyond the two edits named in scope (the 20.12 trim owns the rest of the file; this task quotes it, never re-shapes it)
- eval/ (no new instrument here — 20.15 already landed the comparator rates as committed pins; this task quotes eval/evidence_honesty.py's I-11 cells, it does not extend them)
- agents/tactical/impostor_policy.py (the defects are STATED, not repaired; the repair is a separate Wave-2 contract and the errata name it as routed)
- docs/media/ and the architecture SVG (the architecture-exhibit contract owns that asset; this page's figure is inline)
- replays/ and training/reports/*.jsonl (committed measurement bytes are read, never edited)

**Definition of done:**
- [ ] `docs/ml-program.md` exists in research shape — problem, environment (with one inline figure; no new asset file), method, one results table, N1/N2, limitations, related work — at ≤2 pages (`wc -w` ≤ ~1,400, quoted in the PR), and every number in it carries an inline citation to a committed path with a line or section anchor.
- [ ] The results table's four learned arms and the comparator match `audits/audit-phase-18-close.md:78-84` cell for cell, and each arm's paired p comes from `uv run python scripts/paired_stats.py training/reports/results-finalist-eval.jsonl` re-run in-session (output pasted into the PR), with the shipped champion's 15/9 p=0.3075 stated as not significant rather than elided.
- [ ] N1 and N2 are stated with their cells (30/197 = 0.15228 vs 8/174 = 0.04598, z = +3.370; 20/197 = 0.10152 vs 0/174, z = +4.321), framed as specification gaming of the referee, AND with the NOT-DEMONSTRATED ruling and the clause-(c)-unsatisfiable reason in the same breath — the framing never upgrades the claim.
- [ ] README's "What the measurements said" table (built by 20.12 at README.md:88-96) states, each row with its committed source — the 100/100, 520/520 and 87 % rows already exist and are re-verified rather than rewritten, and every row this task ADDS is mirrored with an identical claim string and figure in docs/reading-guide.md's numbers table so `check_results_agreement` stays green: 100/100 committed replays reconstruct byte-identically; 520/520 eject ballots carry a valid citation, followed by the one-sentence qualification that valid means resolvable, not supported; the proof-vs-inference cross-tab 310/310 = 1.000 against 46/125 = 0.368 with 79/79 innocent ejections in the non-direct cell; the 87 % vent-sighting cross-tab (68/78 correct 9p ejections; the 165-meeting 2×2 — 70 flagged → 68/2, 95 unflagged → 10/21) with "general social deduction: NOT demonstrated" as the row's own reading; and one ML paragraph whose title is its result, written in place of the marked anchor at README.md:100 (four learned arms beat the same-seed comparator on wins, none was adopted, and why the gate is right to say so), with docs/reading-guide.md:102's anchor likewise replaced by a link to the new page.
- [ ] Every volatile number the README table states carries its baseline and record date inline; the PR lists which rows are machine-checked by `scripts/check_doc_facts.py` today and which are stamped-only, so the unchecked set is recorded rather than silent.
- [ ] README's belief-state sentence (README.md:83, as 20.12 left it) is re-verified at HEAD as asserting no live three-channel state — no README edit is due here unless that re-verification finds one — and `docs/adr/0001-three-load-bearing-decisions.md` carries an additive dated note stating that `trust` is a present-but-unwritten channel at HEAD (the definition at `agents/memory/beliefs.py:1111`, callers only under `tests/`) and that the rendered contradictions block appeared in 0 of 1,656 sampled renders — with the grep and the render count quoted in the PR as the verify-then-fix step.
- [ ] The comparator-defect paragraph exists in `docs/ml-program.md` and as an additive dated erratum in BOTH close audits, quoting 45.8 % (190/415 free zero-witness kills declined, 168 of them in the ranking branch's exact-1.0 id tie-break, 15 fellow-defer, 7 cover, 0 unattributed) and the 8–12 % ghost-top band (303/2461 = 12.3 % samples/9p2i, 555/6663 = 8.3 % corpus/9p2i, 0/632 and 0/579 on the two 4p1i sets), naming as the source the committed pins 20.15 landed — `tests/agents/test_impostor_policy.py::TestCommittedCorpusTargetingPins` over `eval/evidence_honesty.py`'s I-11 cells, with the 2026-08-19 review as their origin — and stating that the mover repair is Task 20.32 and the re-measurement Task 20.38, and saying plainly which direction the confound runs (the comparator is depressed, so the learned arms' win edge is an upper bound).
- [ ] Both errata are additive and dated: `git diff` on the two audit files shows appended lines only, no verdict, table cell or hash above the erratum heading altered, and the PR quotes the diffstat.
- [ ] `training/README.md` opens with the program summary and a pointer to `docs/ml-program.md`, with the tier map second and the reopening checklist last; the freeze-header coverage registry and every existing section body survive the reorder unchanged (verified by a word-level diff quoted in the PR).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Everything this page needs already exists in the tree; the job is selection and shape, not
research. Write from `docs/reading-guide.md` §1 and §3 (the 20.12 trim cut the old §6 ML story), `training/README.md` §3,
`audits/audit-phase-19-input-claude.md` §6 (the frank retrospective, including its own
"roughly 20 % of the apparatus delivered ~90 % of the decision value" line — quoting the
project's self-criticism is the credibility move, not a risk),
`audits/audit-phase-18-flip-emergence.md` §8.3 for N1/N2, and `audits/audit-phase-19-close.md`
§4.1 for the proof cells. Add no number you cannot cite to a committed path.

Step 1 — verify-then-fix on the memory claim before writing a word of it: run the greps
(`adjust_trust` and `record_contradiction` across the production packages, then across
`tests/`) and confirm at HEAD what is written and what is not. State exactly what you find,
including that a `record_contradiction` call does exist on a derived belief state; the honest
sentence is "not persisted", not "never called".

Step 2 — the results table is a quote, never a computation. Read the arm cells from the
close audit's table and re-run `scripts/paired_stats.py` for the p-values; if any cell
disagrees with the audit, stop and record the disagreement in the PR rather than picking a
number.

Step 3 — the figure is inline (a fenced diagram block inside the page), because the media
directory belongs to the architecture-exhibit contract. Keep it to the loop a reader needs:
seed → real `HeadlessGame` rollout with the interposed intent selector → per-episode record →
ES over the 19-weight genome → referee gate → accept or reject. Do not draw the whole
training package.

Step 4 — the errata copy the established form: a heading naming the coordination, the date,
the task, and "additive, no in-place rewrites"; then the anchor, then numbered items, then an
explicit item recording what the erratum does NOT touch. Say in the erratum which direction
the bias runs and what is unaffected (the referee verdicts, the NO-FLIP rulings and the
pre-registration ordering all stand — the defects depress the comparator, so the win edge is
an upper bound and the referee failures are, if anything, understated).

Step 5 — the README table rows the front-door rewrite already machine-checks stay as they
are; for the rows this task adds, prefer a stamped quote with its committed path over an
invented check. Two merged checks bite here: a row added to the README table must also be
added to `docs/reading-guide.md`'s numbers table with the identical claim string and figure or
`check_results_agreement` fails, and any private-dialect term the new ML paragraph introduces
must sit inside a `docs/glossary.md` link on its FIRST README occurrence
(`check_dialect_terms`). Record the split in the PR. If a row's number is cheap to check and
the existing checker can take it without touching its file, say so in the PR as a routed
follow-up rather than editing a file outside this scope.

Step 6 — `training/README.md` is a reorder plus a pointer, not a rewrite. Move §3 to the
front as the program summary, keep every other section's body byte-identical, and let
`docs/ml-program.md` carry the narrative. Its FROZEN header and the freeze-coverage registry
must survive.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import check_doc_facts"`
- `uv run python -c "import eval.leak_scan"`

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
Open a PR from branch `phase-20-results-page` with a title like `task 20.13: the results stated once: docs/ml-program.md, the readme results table, and the comparator-defect errata`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/C/collated-portfolio.md §A6 (state the results once — MUST for the research lead, GOOD for three more personas; the concrete fix names both halves, the README table and the ≤2-page page); audits/review-2026-08-19/C/p2-ml-research-lead.md §3 Weakest-1 ("no artifact tells the ML story in the standard research shape … `training/README.md` is a tier map, not that document") + §6 ("the single change that would most raise it") + §7 MUST-2; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 rows 1.7 and 1.8 (the two roadmap items this task implements), §2 row 5 (the "(suspicion, trust, alibi)" claim graded UNDERMINED) and §2 row 9 (the win edge graded CAVEAT — "the method holds, one input is contaminated"); audits/review-2026-08-19/B/collated-findings.md C-72 (`trust` never written; `## Open contradictions` rendered in 0 of 1,656 replay renders); audits/review-2026-08-19/B/verdicts.md C-3 (CONFIRMED **and understated** — 190/415 = 45.8 % of free zero-witness kills declined over the 50 committed 9p2i seeds, 168/168 of them on an exact 1.0 score tie broken by the lower id; the reconstruction replays `decide()` against the recorded bytes with an empty `policy_would_kill_but_action_differs` bucket); audits/review-2026-08-19/A/verdicts.md G-12 (CONFIRMED-BUG — 10,335 impostor decisions re-run offline with 0 mismatches; ghost-top 303/2461 = 12.3 % on samples/9p2i, 555/6663 = 8.3 % on ml_corpus/9p2i, 0/632 and 0/579 across the two 4p1i sets; seed 36 provably thrown) — **both rates are now committed pins**, landed by 20.15 (PR #365): tests/agents/test_impostor_policy.py:1812-1864 (`TestCommittedCorpusTargetingPins` — 190/415 with the 168 / 15 / 7 / 0 decline-reason split, ghost-top 303/2461, 555/6663, 0/632, 0/579, 222 ejected / 81 unseen on samples/9p2i, 0 reconstruction mismatches over 10,335 decisions) computed by eval/evidence_honesty.py's I-11 cells, with audits/audit-phase-20-preregistration.md:174-175 stating all four sets [VERIFIED]; README.md:83 (the belief-state sentence as 20.12 left it — the "(suspicion, trust, alibi)" wording is already gone, so this leg is verify-only), :88-96 (the "What the measurements said" section and table 20.12 built, whose 100/100, 520/520 and 87 % rows this task keeps), :100 (the marked anchor `<!-- ANCHOR: a later contract adds the ML program's paragraph, titled by its result, plus the table's before/after column. -->` this task fills), :107 (the numberless "Four learned tactical policies each beat the scripted one on wins" sentence — the "+0.12 to +0.30" and "+0.16" figures no longer appear in README and now live only in the two close audits); docs/adr/0001-three-load-bearing-decisions.md:18 (decision 3 — "trust scores, alibi map, suspicion graph"); agents/memory/beliefs.py:1111 (`adjust_trust` — the definition is the only non-test occurrence in the tree; seven callers, all under `tests/`), :1493 (`record_contradiction` inside `apply_contradiction_rule` at :1340 — the write lands on the derived result, not the persistent store) with agents/memory/store.py:1811 (the `## Open contradictions:` block that renders); audits/audit-phase-19-close.md §4.1 (pooled 310/310 = 1.000 with direct proof vs 46/125 = 0.368 without; 79/79 of innocent ejections in the non-direct cell); audits/audit-phase-18-close.md:78-84 (the four-arm table: win 0.52 / 0.56 / 0.38 / 0.42857 vs the fresh same-seed `p18-fsm-comparator` 13/50 = 0.26, referee FAIL ×4), :105 ("+0.12 to +0.30"); audits/audit-phase-17-close.md:25 and :60 (`utility-es` win 0.52 = 26/50, Δ +0.16 over the same-seed FSM 0.36, referee FAIL on two gauges); audits/audit-phase-18-flip-emergence.md:466-481 (N1 witnessed-kill rate 30/197 = 0.15228 vs 8/174 = 0.04598, z = +3.370; N2 co-present kills 20/197 = 0.10152 vs 0/174, z = +4.321; both NOT-DEMONSTRATED because clause (c) is unsatisfiable by construction); docs/reading-guide.md:11-22 (§1 "The numbers worth knowing" — the canonical numbers table after the 20.12 trim, rows at :15-22), :57-84 (§3 "What the corpus demonstrates — and what it does not", the 165-meeting cross-tab 68/2 flagged vs 10/21 unflagged at :74-77), :102 (the marked anchor `<!-- ANCHOR: a later contract adds the research-shaped ML page and links it here. -->`; the old §6 ML story was cut in the trim and the file now has five sections); training/README.md:1 (the title — a disposition ledger), :128-165 (§3 what the program positively learned); agents/tactical/learned/forward.py:14 (the 19-weight linear scorer, no numpy/torch), :111 (`ENCODER_VERSION = "impostor-option-features-v1"`), :114 (`GENOME_LENGTH` = 18 features + bias); training/env.py:1-40 (the rollout env drives the real `HeadlessGame`; the legal-action mask is derived from `engine/rules.py`); training/rewards.py:16-26 (the corrected shaping claim — telescoping is not invariance); eval/watchability.py:9-20 (SELECTION-ONLY — the referee is a champion gate and is NEVER a training reward); scripts/paired_stats.py:1-36 (stdlib-only exact McNemar + Wilson, written so a fresh clone reproduces the cells); training/reports/report-finalist-eval.md:2493 (the §18 errata form — additive, dated, nothing above it rewritten)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
