# Agent Prompt — 21.15 THE COMBINED RE-RECORD (operator, ~23 h, $0): four sets on the corrected substrate, the record audit, the re-pins

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.15 — THE COMBINED RE-RECORD (operator, ~23 h, $0): four sets on the corrected substrate, the record audit, the re-pins, anchored to the Wave-0 register entries whose repairs ride these bytes — `audits/review-2026-08-26/A/collated-findings.md` A-14 (CONFIRMED, P1: on the 668 meeting-trigger ticks, 2,166 of 35,350 recorded actions — 6.13%, including 36 kills, 99 reports, 112 vents and 17 emergency calls — are recorded as submitted and never applied), A-31 (CONFIRMED: all 1,505 witness-side vent memories minted twice, and 27 of 27 heard-without-witnessed rows are impostors the teammate firewall leaked through), A-6, A-17, A-34, A-1, and A-15 (ADJUSTED, P1: the corpus README's whole Capability-disclosures section is baseline-6 arithmetic carried forward under a one-word substrate relabel — every item-8 figure reproduces exactly against `2df33ca4` and none against HEAD; item 1's 707 meetings is 668 on HEAD and item 2's 986 kill actions is 1,011 submitted); `audits/review-2026-08-26/B/collated-findings.md` B-8 (CONFIRMED: the belief line contradicts the agent's own sightings in 19% of rendered rows), B-6 (CONFIRMED: four live consumers re-derive contradictions without the private grounding channels), B-10 (ADJUSTED, P2: the pinned `flags_per_meeting` floors and their measured composition — `samples/9p2i` 92 persisted vent + 42 re-derived transcript = 134 over 152 meetings = 0.881578947368421; `ml_corpus/9p2i` 308 + 123 = 431 over 432; `samples/4p1i` 20 + 0 = 20 over 40; `ml_corpus/4p1i` 28 + 1 = 29 over 44), B-46 and B-20 (the STALE amnesty's exact declared digest pair and the five tests around it), B-18, B-19, B-23, B-51, B-52 (the recorder hardening this record runs on). `audits/audit-phase-20-baseline-7.md` §0.1 (the pre-committed bracket 22.2 h / 26.3 h from measured tokens), §0.2 (the recording protocol, the three carried operating notes, and the first-seed honesty probe per leg with a raise defined as a STOP), §0.3 (the actual: 300 games in 23h25m42s at $0.0000), §0.4 (two `(deadline_default)` re-records repaired in 12m33s), §6 (the pre-registered rule returned FINDING; bars 1 and 2 MISSED), §6.1 (**THE OWNER'S ADOPTION RULING — an owner override of a FINDING verdict**, and its "What no surface may say" clause), §8 (the referee floors), §10.1 (the substrate question, and the census lesson: start from a repo-wide grep, not a `tests/`-scoped one — `frontend/src/lib/bodies.test.ts` recomputes a corpus digest on every run), §10.2 (what that record deliberately did not discharge: the ML re-ground, the declared grounding gap, the dropped `samples/9p2i` MANIFEST disclosure block, and the production-side duplicate `alibi_vs_sighting` mint that rides inside the bytes), §10.3 (the three re-derivations that lost a claim, with their pinned divergence counts); `audits/audit-phase-20-close.md` F1 (the campaign tier RED at close HEAD: 9 failed, 308 passed) and F2 (`frontend/src/lib/bodies.test.ts:9`, a census header stale against its own pins). Anchors re-verified at HEAD `d8ec0a1c`: `orchestrator/replay.py:524-546` (`_RETIRED_ALWAYS_ON_LEVERS`, twenty-one keys), `:568-570` (`_TOGGLEABLE_LEVER_RESOLVERS`, ONE entry — `impostor_roll_call`), `:578-589` (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS` / `SUBSTRATE_FLAG_KEYS`), `:591` (`substrate_flag_snapshot`), `:651` (`substrate_slate_mismatches`); `scripts/refresh_samples.sh:36-37` (`AILIBI_SAMPLE_DIR`, `AILIBI_MANIFEST` defaulting under it), `:248-260` (`--expect-levers` parse; an explicitly empty value means the bare slate), `:291-326` (the preflight, delegating the comparison to `substrate_slate_mismatches`), `:441` and `:461` (worker and attempt defaults, 2 and 4), `:566` / `:588` (`REQUIRED_PROMPT_SET="qwen3_6_27b"`, `REQUIRED_SET_OWNER_MODEL="Qwen/Qwen3.6-27B"`), `:1030-1038` (the post-record eval-report rebuild) and `:1040-1074` (the rubric refresh, whose failure is declared to make the refresh incomplete); `scripts/record_ml_corpus.sh:107-166` (the pin block — already baseline-7-shaped, `REQUIRED_PROMPT_VERSIONS` at `:156` naming all four templates), `:345-392` (`write_splits`, the `seed % 5` rule), `:607-710` (`check_replay_provenance`, the `deadline_default` refusal at `:669-676`); `scripts/validity_gate.py:77-93` and `eval/validity.py:24-56` (the ten named checks); `eval/watchability.py:538` (`_BASELINE_SUPPLY_FLOORS`), `:841-905` (the baseline-7 block and its worked derivation), `:914` (`_DEFAULT_BASELINE_ID`); `scripts/verify_ml_evidence.py:182-206` (`_DECLARED_GROUNDING_GAP` and `_is_declared_grounding_gap` — one pair of digests, and any other mismatch FAILS); `scripts/check_doc_facts.py:203` (`_LADDER_TIP_AUDIT`), `:237-242` (`_LADDER_TIP_DOCUMENTS`), `:538-560` (the record-read parser's heading, table header and win-split header tokens), `:1119` / `:1722` / `:1784` / `:1922` / `:2027` / `:2587` / `:3006` / `:3077` (ladder tip, audits index, results agreement, result sources, conviction partition, `record_partition`, verdict figures, featured exhibits); `tests/meetings/test_prompt_byte_golden.py:183` (`ARCHIVED_PROMPT_VERSION_SETS = {}`, and `tests/fixtures/prompt_archive/` does not exist) with the perturbation leg at `:1162-1184` (victim: the LIVE `qwen3_6_27b/crewmate_report.j2`); `tests/meetings/test_contradictions.py:3146` (`_COMMITTED_MEETINGS = 668  # baseline 6: 707`); `tests/eval/test_deduction_metrics.py:152` and `:179` (the `# was …` convention this sweep keeps); `frontend/src/lib/bodies.test.ts:441-511` over `bodies.fixture.json`; `docs/artifacts.md:107` (`7.9 MB / 158 files`, and `git ls-files audits` = 158); `docs/glossary.md:38-59` (the definitions of *baseline N* and *the ladder tip*); `replays/ml_corpus/README.md:104-126` + `:255-277` (the disclosures) and `:296-313` (the leg table); `replays/samples/9p2i/MANIFEST.md` (twenty-one flag keys, four `qwen3_6_27b.v4` templates, `fsm-default`, `2026-08-25`, `0.0000`); AGENTS.md:91-124 (the craft rules). Census re-run at HEAD: `grep -rln 'replays/samples\|replays/ml_corpus' tests/` = 41 files; the same pattern repo-wide over `*.py`, `*.ts`, `*.tsx`, `*.json` and `*.sh`, excluding `replays/`, `audits/` and `node_modules/`, = 94 files (the 41 among them).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-rerecord`
**Depends on:** 21.7, 21.8, 21.9, 21.11, 21.12, 21.14, 21.16
**Section refs:** the Wave-0 register entries whose repairs ride these bytes — `audits/review-2026-08-26/A/collated-findings.md` A-14 (CONFIRMED, P1: on the 668 meeting-trigger ticks, 2,166 of 35,350 recorded actions — 6.13%, including 36 kills, 99 reports, 112 vents and 17 emergency calls — are recorded as submitted and never applied), A-31 (CONFIRMED: all 1,505 witness-side vent memories minted twice, and 27 of 27 heard-without-witnessed rows are impostors the teammate firewall leaked through), A-6, A-17, A-34, A-1, and A-15 (ADJUSTED, P1: the corpus README's whole Capability-disclosures section is baseline-6 arithmetic carried forward under a one-word substrate relabel — every item-8 figure reproduces exactly against `2df33ca4` and none against HEAD; item 1's 707 meetings is 668 on HEAD and item 2's 986 kill actions is 1,011 submitted); `audits/review-2026-08-26/B/collated-findings.md` B-8 (CONFIRMED: the belief line contradicts the agent's own sightings in 19% of rendered rows), B-6 (CONFIRMED: four live consumers re-derive contradictions without the private grounding channels), B-10 (ADJUSTED, P2: the pinned `flags_per_meeting` floors and their measured composition — `samples/9p2i` 92 persisted vent + 42 re-derived transcript = 134 over 152 meetings = 0.881578947368421; `ml_corpus/9p2i` 308 + 123 = 431 over 432; `samples/4p1i` 20 + 0 = 20 over 40; `ml_corpus/4p1i` 28 + 1 = 29 over 44), B-46 and B-20 (the STALE amnesty's exact declared digest pair and the five tests around it), B-18, B-19, B-23, B-51, B-52 (the recorder hardening this record runs on). `audits/audit-phase-20-baseline-7.md` §0.1 (the pre-committed bracket 22.2 h / 26.3 h from measured tokens), §0.2 (the recording protocol, the three carried operating notes, and the first-seed honesty probe per leg with a raise defined as a STOP), §0.3 (the actual: 300 games in 23h25m42s at $0.0000), §0.4 (two `(deadline_default)` re-records repaired in 12m33s), §6 (the pre-registered rule returned FINDING; bars 1 and 2 MISSED), §6.1 (**THE OWNER'S ADOPTION RULING — an owner override of a FINDING verdict**, and its "What no surface may say" clause), §8 (the referee floors), §10.1 (the substrate question, and the census lesson: start from a repo-wide grep, not a `tests/`-scoped one — `frontend/src/lib/bodies.test.ts` recomputes a corpus digest on every run), §10.2 (what that record deliberately did not discharge: the ML re-ground, the declared grounding gap, the dropped `samples/9p2i` MANIFEST disclosure block, and the production-side duplicate `alibi_vs_sighting` mint that rides inside the bytes), §10.3 (the three re-derivations that lost a claim, with their pinned divergence counts); `audits/audit-phase-20-close.md` F1 (the campaign tier RED at close HEAD: 9 failed, 308 passed) and F2 (`frontend/src/lib/bodies.test.ts:9`, a census header stale against its own pins). Anchors re-verified at HEAD `d8ec0a1c`: `orchestrator/replay.py:524-546` (`_RETIRED_ALWAYS_ON_LEVERS`, twenty-one keys), `:568-570` (`_TOGGLEABLE_LEVER_RESOLVERS`, ONE entry — `impostor_roll_call`), `:578-589` (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS` / `SUBSTRATE_FLAG_KEYS`), `:591` (`substrate_flag_snapshot`), `:651` (`substrate_slate_mismatches`); `scripts/refresh_samples.sh:36-37` (`AILIBI_SAMPLE_DIR`, `AILIBI_MANIFEST` defaulting under it), `:248-260` (`--expect-levers` parse; an explicitly empty value means the bare slate), `:291-326` (the preflight, delegating the comparison to `substrate_slate_mismatches`), `:441` and `:461` (worker and attempt defaults, 2 and 4), `:566` / `:588` (`REQUIRED_PROMPT_SET="qwen3_6_27b"`, `REQUIRED_SET_OWNER_MODEL="Qwen/Qwen3.6-27B"`), `:1030-1038` (the post-record eval-report rebuild) and `:1040-1074` (the rubric refresh, whose failure is declared to make the refresh incomplete); `scripts/record_ml_corpus.sh:107-166` (the pin block — already baseline-7-shaped, `REQUIRED_PROMPT_VERSIONS` at `:156` naming all four templates), `:345-392` (`write_splits`, the `seed % 5` rule), `:607-710` (`check_replay_provenance`, the `deadline_default` refusal at `:669-676`); `scripts/validity_gate.py:77-93` and `eval/validity.py:24-56` (the ten named checks); `eval/watchability.py:538` (`_BASELINE_SUPPLY_FLOORS`), `:841-905` (the baseline-7 block and its worked derivation), `:914` (`_DEFAULT_BASELINE_ID`); `scripts/verify_ml_evidence.py:182-206` (`_DECLARED_GROUNDING_GAP` and `_is_declared_grounding_gap` — one pair of digests, and any other mismatch FAILS); `scripts/check_doc_facts.py:203` (`_LADDER_TIP_AUDIT`), `:237-242` (`_LADDER_TIP_DOCUMENTS`), `:538-560` (the record-read parser's heading, table header and win-split header tokens), `:1119` / `:1722` / `:1784` / `:1922` / `:2027` / `:2587` / `:3006` / `:3077` (ladder tip, audits index, results agreement, result sources, conviction partition, `record_partition`, verdict figures, featured exhibits); `tests/meetings/test_prompt_byte_golden.py:183` (`ARCHIVED_PROMPT_VERSION_SETS = {}`, and `tests/fixtures/prompt_archive/` does not exist) with the perturbation leg at `:1162-1184` (victim: the LIVE `qwen3_6_27b/crewmate_report.j2`); `tests/meetings/test_contradictions.py:3146` (`_COMMITTED_MEETINGS = 668  # baseline 6: 707`); `tests/eval/test_deduction_metrics.py:152` and `:179` (the `# was …` convention this sweep keeps); `frontend/src/lib/bodies.test.ts:441-511` over `bodies.fixture.json`; `docs/artifacts.md:107` (`7.9 MB / 158 files`, and `git ls-files audits` = 158); `docs/glossary.md:38-59` (the definitions of *baseline N* and *the ladder tip*); `replays/ml_corpus/README.md:104-126` + `:255-277` (the disclosures) and `:296-313` (the leg table); `replays/samples/9p2i/MANIFEST.md` (twenty-one flag keys, four `qwen3_6_27b.v4` templates, `fsm-default`, `2026-08-25`, `0.0000`); AGENTS.md:91-124 (the craft rules). Census re-run at HEAD: `grep -rln 'replays/samples\|replays/ml_corpus' tests/` = 41 files; the same pattern repo-wide over `*.py`, `*.ts`, `*.tsx`, `*.json` and `*.sh`, excluding `replays/`, `audits/` and `node_modules/`, = 94 files (the 41 among them).
**Complexity:** Integration
**Record impact:** the record itself — this task writes the committed replay bytes and every pin derived from them.
**Measurement:** `bash scripts/verify_samples.sh` (bare) reports 100/100 on the new samples bytes; `uv run python scripts/validity_gate.py <set> --expected-model Qwen/Qwen3.6-27B --require-zero-cost` PASS on each of the four sets, all ten checks named individually in the audit; `uv run python scripts/verify_ml_evidence.py` (FULL, never `--fast`, which samples eight seeds per set) green with reconstruction 300/300 across the four declared sets; `uv run python scripts/measure_baseline.py --honesty <set>`, `--solvability <set>` and `--watchability` print the cells the record audit tabulates, cell for cell; `uv run pytest` and `bash scripts/check.sh` green in a CLEAN worktree — every output pasted into the PR Summary.

This is Wave 1's one record and the only task in it that writes committed replay bytes. Four sets,
300 games, in the value order the baseline-7 record fixed and this one keeps —
`replays/samples/9p2i` → `replays/ml_corpus/9p2i` → `replays/samples/4p1i` →
`replays/ml_corpus/4p1i` — every leg on Featherless `Qwen/Qwen3.6-27B` non-thinking at $0, every
leg gated before the next one starts.

The reason it has to run is the disease this phase exists to cure. The Wave-1a repairs change what
the engine records and what a model is shown: the oracle voice leaves the templates, structured
testimony survives to the ballot, discarded actions stop being recorded as if they happened
(A-14: 2,166 of 35,350 recorded actions, 6.13%, including 36 kills), the belief line stops
contradicting the agent's own sightings (B-8: 19% of rendered rows), and each witnessed vent is
minted once instead of twice (A-31: 1,505 double mints, with 27 audible copies leaking through the
teammate firewall). Until this record runs, every instrument, the ML corpus, the front door and the
spectator read bytes produced by code that no longer exists. That is exactly the failure A-15
documents in the corpus README, where a re-record moved the bytes and one word was changed in the
disclosures section while every number stayed behind — a green artifact certifying a document it
contradicts. A repair that never reaches the record is a repair the project cannot see.

**The record decides nothing, and the contract is written so it cannot.** There is no
pre-registration, there are no bars, and there is no verdict. Nothing graduates: the substrate slate
is identical to the committed one — the twenty-one retired levers unconditional,
`impostor_roll_call` OFF — so `--expect-levers` is passed EMPTY (the bare slate,
`scripts/refresh_samples.sh:248-260`) on every leg, and the `flags` column of every new MANIFEST row
must come out byte-identical to today's twenty-one-key string. That equality is the cheapest
available proof that the substrate did not move while the bytes did.

The inherited framing is stated once here and repeated verbatim in the audit: **baseline 7 is canon
by explicit owner override of a FINDING verdict** — the pre-registered rule returned FINDING because
bars 1 and 2 were missed, that read is immutable, and no surface this task writes may state or imply
that those bars passed (`audits/audit-phase-20-baseline-7.md` §6.1). This record inherits that
substrate and adopts nothing of its own.

Attribution is impossible by construction here, and the audit must say so plainly rather than let a
reader assume otherwise. Every behavioural repair the wave landed, plus the prompt-set bump, arrives
in one recording window, so no cell's movement is attributable to any single one of them. That is
the correct trade: none of these changes is a lever, nothing is being decided on the cells, and
buying a 23-hour window per unconditional bug fix would be an expensive answer to a question nobody
needs. The Wave-2 levers get their own record precisely because those DO decide something.

What replaces a verdict is a pre-committed expectation. Before the first seed stages, the audit's §0
records, from the smoke's five seeds, the expected DIRECTION of every cell the Wave-1a repairs
touch, and — more usefully — the list of cells expected NOT to move at all. A named-not-to-move cell
that moves further than the smoke's own per-seed spread is a STOP-and-report to the owner, not a
footnote written afterwards. A prediction made after the numbers are in is not a prediction.

The clock is planned from measurement, not from this title. The baseline-7 record took 23h25m42s for
the same 300 games, inside a bracket of 22.2 h and 26.3 h committed in advance from measured tokens
(`audits/audit-phase-20-baseline-7.md` §0.1, §0.3). The bumped prompt set changes tokens per meeting
call, so the smoke's measured tokens-per-call and aggregate tokens-per-second are what this record's
projection is re-derived from — written into §0 BEFORE the first seed, with the per-leg actual read
against it afterwards. Two Featherless seed workers is the configuration, capped by the provider at
two inference units per 27B request, not by the recorder.

The sweep after the bytes is the widest half of the task and the half that is always
under-budgeted. `grep -rln 'replays/samples\|replays/ml_corpus' tests/` returns 41 files at HEAD,
and the repo-wide count over source, scripts and frontend is 94 — which is the census the last
record learned to use the hard way, when a frontend fixture that recomputes a corpus digest on every
run was missed by a `tests/`-scoped grep (§10.1). Budget it as its own leg.

Finally, the record mints **baseline 8**: a numbered reference recording is "one recording of the
sample sets under a stated set of behavioural settings" and the ladder tip is "the newest reference
recording" (`docs/glossary.md:38-59`), so bytes recorded under corrected code and a bumped prompt set
are a new one. Minting it is bookkeeping, not promotion — baseline 8 adopts nothing, graduates
nothing and reads no bar, and it inherits baseline 7's substrate exactly as that substrate was
adopted: by explicit owner override of a FINDING verdict. But it DOES succeed it. From this merge
the ladder tip is baseline 8, and every tip-bearing surface says so; baseline 7 keeps its history —
the FINDING, the two missed bars, the override that adopted it anyway — and loses only its claim to
be the current recording. Writing it any other way leaves two documents answering "which bytes are
canon" differently, which is the defect class this phase opened against.

**Files in scope:**
- replays/samples/9p2i/; (the baseline-8 record: replay bytes, MANIFEST, tournament-eval-report.json, results-rubric-score.json, README)
- replays/samples/4p1i/; (same)
- replays/ml_corpus/9p2i/; (same, plus splits.json regenerated under the unchanged `seed % 5` rule)
- replays/ml_corpus/4p1i/; (same)
- replays/ml_corpus/README.md; (the leg table at :296-313 re-derived from this record's actuals, and the Capability-disclosures section recomputed from these bytes — A-15's whole section, not item 8 alone)
- audits/audit-phase-21-rerecord.md; (new: the record audit — protocol, per-leg actuals against the pre-committed projection, validity gates, the substrate stamp, every instrument cell before and after, the re-record log, what this record does not discharge)
- eval/watchability.py; (a `baseline-8` block in `_BASELINE_SUPPLY_FLOORS` pinned from these bytes with the same population-relative derivation and its vent/transcript split stated per B-10; `_DEFAULT_BASELINE_ID` moves; the baseline-7 block stays, frozen, as history)
- scripts/verify_ml_evidence.py; (ONE constant: `_DECLARED_GROUNDING_GAP`'s right-hand digest re-stamped to the new corpus fingerprint, so the declared gap keeps naming a real pair of digests; the amnesty itself is not touched and dies at the re-ground)
- scripts/check_doc_facts.py; (`_LADDER_TIP_AUDIT` repointed at this record's audit, and the record-read parser taught to locate a published-cell section as well as a pre-registered bar section — the minimum the gates force, nothing else)
- README.md; (the MINIMUM cells the doc-fact gates force when the recorded figures move: the sample-provenance paragraph, the win-rate row, the citation-compliance row, the conviction-partition row and the ladder-tip sentence — the narrative reading and the before/after column stay with the post-record results task)
- docs/reading-guide.md; (the SAME minimum cells and nothing else — `check_results_agreement` (:1784) compares the two tables row by row)
- docs/glossary.md; (the two ladder-tip sentences, which `check_ladder_tip` (:1119) scans)
- docs/history.md; (the same one-line ladder-tip mention)
- frontend/src/lib/bodies.fixture.json; (regenerated by the recipe committed at the top of its own test file)
- frontend/src/lib/bodies.test.ts; (the census constants that fold from the new bytes — named here rather than left to the sweep, because the 20.36 §10.1 miss was exactly a committed frontend fixture nobody re-pinned)
- frontend/src/lib/contradictions.fixture.json; (the same treatment — regenerated by its own committed recipe and its derived counts re-pinned; the second half of the same census)
- engine/tick.py; (POST-RECORDING ONLY: `superseded_meeting_tick` is DELETED once the new census reads zero — the expiry the repair's own test docstring names)
- eval/replay_walk.py; (the same expiry: the replay allowance at the tick-hash check is deleted with it)
- api/replay_loader.py; (the same expiry, second call site)
- training/surrogate/dataset.py; (the same expiry, third call site)
- tests/engine/test_win_ordering_census.py; (DELETED at the expiry — a census whose answer is structurally zero is not a gate)
- tests/_helpers/test_committed_single_home.py; (the census test's `UNCACHED_BY_DESIGN` entry leaves with it)
- tests/eval/; (the byte-coupled re-pins: the deduction cross-tab cells, the honesty cell families, the solvability and watchability pins, the funnel and V&J instrument pins — old value kept in a comment beside the new one)
- tests/meetings/; (the committed-population pins, `_COMMITTED_MEETINGS` and every census that sums to it, the classified-divergence pins, and the prompt-archive retirement)
- tests/api/; (the manifest-fingerprint, rubric and served-bytes pins)
- tests/agents/; (the committed-bytes pins in the memory and testimony tests)
- tests/scripts/; (the manifest-writer, sample-report and evidence-verifier pins, plus the perturbation case proving the widened record-read locator still fails on a drifted cell)
- tests/training/; (only the corpus-fingerprint tripwires that name the live corpus; the staleness caps stay keyed to the artifacts' own fit-side count and are NOT re-pinned to the live one)

**Files NOT in scope:**
- every production package that produces recorded behaviour — engine/, agents/, meetings/, observation/, orchestrator/, agents/strategic/prompts/ (frozen for the recording window; a record that edits the thing it is recording is not a record, and a routed fix reopens the window and restarts the smoke). The ONE exception is the win-ordering expiry named in scope above: `engine.tick.superseded_meeting_tick` and its three call sites are a replay-only inverse that exists to read PRE-repair bytes, so deleting them after the last seed lands changes no recorded behaviour and cannot reopen the window. It is sequenced after the recording exactly as the prompt-archive retirement is, and the audit states the order
- eval/evidence_honesty.py, eval/deduction_metrics.py, eval/solvability.py, eval/vote_correctness.py, eval/meeting_quality.py (the instruments are READ here and never redefined — a cell re-implemented at the record makes before and after incomparable)
- training/ artifacts, fits and harness (the ML re-ground is the named follow-up that consumes this corpus; the campaign tier stays red across this record and is not papered over here)
- scripts/record_ml_corpus.sh, scripts/refresh_samples.sh (the recorders are hardened, re-pinned to the bumped template map and swept for stale substrate prose UPSTREAM of the smoke, and frozen through the window; this task runs them and reports what they printed. The one line this leaves behind is the corpus recorder's header note quoting the measured baseline-6/7 leg durations: this record's actuals live in its audit, and the header's refresh is routed to the post-record task rather than done twice in one phase — the audit names it)
- frontend/src/components/ReplayPicker.tsx (the curated featured strip is re-watched, not re-curated: a blurb this record falsifies is named in the audit and routed to the post-record results task, because Wave 2 replaces these bytes again)
- replays/samples/9p2i/MANIFEST.md's hand-maintained disclosure block (dropped at the last refresh and declared re-measure-not-restore; it stays absent, and the corpus README's disclosures are the section this record re-derives)
- audits/README.md and docs/artifacts.md (the `audits/README.md` index line and the `docs/artifacts.md` `audits/`-row bump ride this PR as the standing index amendment — the 20.34 precedent — not as scope entries; both counts are re-read at implementation time, never hard-pinned)

**Definition of done:**
- [ ] All four committed sets are re-recorded in the value order the previous record fixed (`samples/9p2i` → `ml_corpus/9p2i` → `samples/4p1i` → `ml_corpus/4p1i`, the corpus 9p2i leg ahead of both 4p1i legs because that is where the conviction cell's denominator is) on the corrected substrate at the bumped prompt set, each leg passing `scripts/validity_gate.py <set> --expected-model Qwen/Qwen3.6-27B --require-zero-cost` with all ten checks named individually in the audit before the next leg starts, each reconstructing byte-identically under a BARE environment, and each completed seed range checkpoint-pushed before the next begins.
- [ ] The recorded substrate is read out of the `game_over` rows rather than out of the launching shell and equals the committed slate exactly — the twenty-one retired levers True, `impostor_roll_call` False — and the `flags` column of every new MANIFEST row is byte-identical to the committed twenty-one-key string, quoted in the audit as the proof that nothing graduated here.
- [ ] `--expect-levers` is passed EMPTY on every leg including the `--dry-run` preview, and the preflight's resolved-configuration block (provider, prompt set, roster, sample dir, worker count, retry budget) is pasted into the audit as the recorded configuration; a preflight refusal is reported as the guard working and the run restarted, never worked around.
- [ ] The wall-clock projection is written into the audit's §0 BEFORE the first seed stages, re-derived from the smoke's measured tokens per meeting call and aggregate tokens per second at two workers, and the per-leg ACTUAL is read against it afterwards with the total and the `$0.0000` cost stated.
- [ ] `scripts/measure_baseline.py --honesty` runs on the FIRST completed seed of EVERY leg before the rest of that leg queues, with a raise or an unfoldable cell family defined as a STOP; a probe that folds a game with no meetings in it is recorded as VACUOUS and re-run, never counted as a pass.
- [ ] The STOP rule is pre-committed in §0 and executed as written: the expected direction of every cell the Wave-1a repairs touch, and the named list of cells expected NOT to move; a named-not-to-move cell that moves by more than the smoke's per-seed spread is a STOP-and-report to the owner before the next leg, with the recording paused rather than continued under a note.
- [ ] Two movements are PRE-DECLARED in §0, before the first seed, so a corrected instrument cannot read as a surprise and trip the STOP rule. First, the wait-share cells fall because the action tally stops counting actions the engine discarded behind a meeting trigger: crew `0.1046` → approximately `0.0990` and impostor `0.1000` → approximately `0.0982` on the committed reference. The declaration is directional and approximate ON PURPOSE — the exact landing point is a property of the new bytes, and only a movement in the OPPOSITE direction, or one materially past the declared magnitude, is a STOP. Second, the `last_seen`-argmax agreement cell reads red by construction on the committed bytes (a belief line contradicting the same prompt's own sighting rows) and the corrected render makes it readable at all; §0 states which of the two it is BEFORE the record, so an improvement that is really a repaired instrument is never published as a behavioural gain.
- [ ] The before/after instrument table carries the `last_seen`-argmax agreement cell explicitly, with the "before" column labelled RED-BY-CONSTRUCTION and its denominator stated, rather than omitted because the old instrument could not produce a number. A cell that had no honest before is published with that fact in the cell, never left blank and never back-filled.
- [ ] The corpus-disclosure gate is discharged on the new bytes and named in this DoD rather than assumed: `uv run python scripts/check_doc_facts.py` exits 0 with the `replays/ml_corpus/README.md` Capability-disclosures section republished from these bytes, and the PR quotes the exit code beside the regenerated section's numerators and denominators.
- [ ] The win-ordering expiry is executed AFTER the last seed lands and the census is re-derived, not assumed: `tests/engine/test_win_ordering_census.py` is run against the NEW committed sets and reads zero decided meeting-trigger ticks, and only then are `engine.tick.superseded_meeting_tick`, its three call sites (`eval/replay_walk.py`, `api/replay_loader.py`, `training/surrogate/dataset.py`), the census test itself and its `UNCACHED_BY_DESIGN` entry deleted — retire means delete, no wrapper left behind. The PR quotes the zero census and `grep -rn superseded_meeting_tick .` returning nothing outside `audits/` and `tasks/`. If the census does NOT read zero the deletion does not happen: the surviving case is reported to the owner with its seed and tick, and the mechanism stays with a dated note naming what kept it alive.
- [ ] Every `(deadline_default)` row is treated as a FAILED recording and the seed re-records; every re-record is logged with its cause AS IT HAPPENS, and the audit states the count per leg beside the baseline-7 record's 2 of 150 and the baseline-6 record's 10 of 150.
- [ ] The record audit publishes every instrument cell BEFORE and AFTER with denominators — the deduction cross-tab, the ten honesty cell families, solvability, watchability supply, vote correctness and the meeting population — each labelled as a published cell and NOT as a bar: this record pre-registered nothing and no cell carries a verdict. The audit states baseline 7's history exactly — it was adopted by explicit owner override of a FINDING verdict, bars 1 and 2 missed, nothing re-priced — AND states that this record supersedes it as the reference recording: the ladder tip is now baseline 8. Those two sentences are not in tension and the audit must carry both. The constraint that binds this phase is about the BARS story (no surface may state or imply that bars 1 or 2 passed), not about the tip's succession: a maintenance re-record adopts nothing and rules on nothing, but it does replace the bytes, and a document claiming baseline 7 is still the tip after that would be the second source of truth this record exists to prevent.
- [ ] The audit names the co-intervention explicitly — every behavioural repair the wave landed, plus the prompt-set bump, in one window — so no cell's movement is attributable to a single repair, with the list of what landed and the sentence that attribution is impossible by construction.
- [ ] A `baseline-8` block is added to `eval/watchability.py::_BASELINE_SUPPLY_FLOORS` pinned from these bytes — all three gauges with their raw numerators, the vent/transcript split of `flags_per_meeting` stated in the pin comment per B-10, the population-relative derivation worked through to the equality point — and self-consistency is demonstrated by scoring the record against its own floors at exact equality; `_DEFAULT_BASELINE_ID` moves to `"baseline-8"`, the baseline-7 block stays as history, and the training-side selection constants deliberately lag with the audit naming the task that moves them.
- [ ] The prompt archive the bump created retires: its registry entry returns to empty and its fixture bodies are deleted once no committed set stamps the old template versions, with `tests/meetings/test_prompt_byte_golden.py` still walking every committed meeting through the live registry alone and still failing on a one-byte perturbation of a live template — the perturbation leg is run and its red output quoted in the PR.
- [ ] The byte-coupled re-pin sweep is executed as a census, starting from a REPO-WIDE grep rather than a `tests/`-scoped one (41 files under `tests/`, 94 repo-wide at HEAD), with the old value kept in a comment beside each new one, and `uv run pytest` green with no `xfail` added to absorb a moved number. The census explicitly reaches `frontend/`: BOTH `frontend/src/lib/bodies.fixture.json` (with `bodies.test.ts`'s constants) and `frontend/src/lib/contradictions.fixture.json` are regenerated by their own committed recipes and their derived counts re-pinned, and `cd frontend && npm run test` is green. Naming them is not belt-and-braces — the 20.36 record's §10.1 miss was a committed frontend fixture that a `tests/`-scoped sweep never looked at.
- [ ] `replays/ml_corpus/README.md` is refreshed end to end: the leg table from this record's actuals, and the whole Capability-disclosures section recomputed from these bytes with each numerator, denominator and the frame used for the whereabouts-match cell stated — A-15's finding is that the section, not item 8 alone, was carried forward unrecomputed, and the audit records which figures moved and by how much.
- [ ] `scripts/verify_ml_evidence.py`'s declared grounding gap names the NEW corpus fingerprint, so the gap stays one exact pair of digests and any other mismatch still FAILS; the audit states that the fits are now stale against a second corpus, that the amnesty is not widened here, and that the re-ground is the task which deletes it.
- [ ] The doc-fact couplings are discharged with the MINIMUM cell edits and no narrative rewriting: `_LADDER_TIP_AUDIT` points at this record's audit, the audit carries the exact sentence form the checker parses with the tip at baseline 8, the conviction-partition and win-rate cells are re-derived, README and the reading guide agree row by row, and the widened record-read locator ships with a perturbation case proving it still fails on a drifted cell.
- [ ] Each set's `tournament-eval-report.json` and `results-rubric-score.json` are regenerated from the new bytes by the committed recipes, the served rubric reads FRESH (producer fingerprint equals loader fingerprint), and the curated featured strip is re-watched with every blurb this record falsifies named in the audit and routed rather than silently kept.
- [ ] The audit carries a section stating what this record does NOT discharge: the ML re-ground and the campaign tier, the Wave-2 lever record, the narrative half of the front door, the corpus recorder's header duration note, and any production-side carry that rides inside these bytes.
- [ ] The freeze is shown to have held rather than asserted: the audit lists, from `git log` over the recording window, every commit that landed in engine/, agents/, meetings/, observation/, orchestrator/ or the prompt set between the smoke's GO and this PR — the expected list is empty, and a non-empty one means the window reopened and the record restarts.
- [ ] `bash scripts/verify_samples.sh` (bare) reports 100/100 on the new samples bytes and `uv run python scripts/verify_ml_evidence.py` (full, never `--fast`) reports reconstruction 300/300 across the four declared sets, both outputs pasted into the PR Summary.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — read the smoke report before touching a terminal, and copy its numbers forward rather than
re-deriving them. It owns the measured tokens per call, the aggregate tokens per second, the
observed lever and coverage census, and the directional read on the honesty cells. This record's §0
projection and its named-not-to-move list are built from that report and committed to the audit
before the first seed stages. Where this record's reading and the smoke's disagree, the
disagreement is a finding, not a rounding.

Step 2 — this is a LOCAL operator session on the owner's machine, not a dispatch container: a
multi-day leg must not be exposed to container reclaim. Run `bash scripts/setup_env.sh`, then export
the recording environment in ONE block before any worker process starts — provider, prompt set,
meeting model, roster, sample dir, `AILIBI_REFRESH_WORKERS=2`, `AILIBI_SEED_MAX_ATTEMPTS=8` — and
nothing else. Confirm no `AILIBI_*` lever export is set, since the whole slate is unconditional now
and `impostor_roll_call` must stay unset. `FEATHERLESS_API_KEY` comes from the repo-root `.env` and
is never echoed into a log, a report or the PR.

Step 3 — preview, then record, one leg at a time. `--dry-run` with `--expect-levers ""` first; paste
the resolved-configuration block into the audit; then the same command without `--dry-run`. The
preflight compares the live slate against the declared one through
`orchestrator.replay.substrate_slate_mismatches` — the one comparison the wrapper, the record and
the audit all use rather than re-derive — so a refusal means a stale export was caught before the
23-hour spend, which is the guard working. Move each set's prior bytes ASIDE before its leg rather
than recording over them, and preserve rather than delete them for the duration: both recorders'
skip scans treat a present in-range replay as already recorded, and the corpus recorder's freeze
guard judges every replay against the declared template map, so a leftover replay at the old
template versions either skips a seed or refuses the freeze at the end of a multi-hour leg.

Step 4 — gate, probe, push, repeat, in that order. The validity gate is NOT a measurement gate: it
passed all ten checks on a set the honesty instrument could not fold at all, which is what cost the
previous phase its smoke. So after the first completed seed of every leg, run
`scripts/measure_baseline.py --honesty` against it and read the fold before queueing the rest. Run
the gate and the instruments in a shell carrying the same environment as the recording; the loader
refuses a cross-substrate reconstruction. After each leg: gate with both flags, reconstruct
byte-identically under a BARE environment, diff the recorded substrate snapshot against the intended
slate key by key, then commit and push that seed range.

Step 5 — read everything before writing anything into the audit's cell tables, then write the tables
in one pass. Compute all four sets' cells with the instrument emitters, tabulate before and after
with denominators, and only then write the prose around them. Two rules bind the prose: no cell is
called a bar, and no sentence implies the previous phase's bars passed. The published cells are
descriptive; the phase's decisions live in the Wave-2 record.

Step 6 — the floor block. Copy the baseline-7 block's shape exactly: three `FloorPin` values with
their raw numerators in the comment, the vent-versus-transcript split of `flags_per_meeting` stated
(B-10's whole surviving point is that a merged gauge hides which component supplies it), the
population-relative derivation worked through, and the self-consistency PASS pasted. A numerator of
1 or 0 makes its gauge ADVISORY under the standing rare-event rule; say so rather than pinning a
floor that cannot fail.

Step 7 — the sweep, as a census rather than a chase. Start from the repo-wide grep, list every
asserted constant that reads committed bytes, and work top to bottom keeping the old value in a
comment beside the new one. Four families are easy to miss: the committed-population pins whose
docstrings still narrate an older count, the classified-divergence pins the last record introduced,
the frontend fixture with its own regeneration recipe, and the corpus-fingerprint tripwires — of
which only the ones naming the LIVE corpus move; the staleness caps stay keyed to the artifacts'
own fit-side count, because asserting a stale cap against the live count is how a stale cap gets
laundered as a current one. Run the suite in a CLEAN worktree: a concurrent session in the same
checkout produces false failures on the import-linter and hash-pin gates, which is exactly the noise
that makes a sweep of this size go wrong.

Step 8 — the doc-fact couplings fire the moment the bytes land, and the minimum is genuinely
minimal. The provenance checker re-derives README's refresh date, win rates, model and prompt-set
version from the MANIFESTs this record rewrites, and its win-rate sweep runs FILE-WIDE; the results
tables in README and the reading guide are compared row by row; the citation row is re-derived from
an instrument pin this record moves; and the record-read parser reads the ladder-tip audit for the
conviction cells. Move exactly those cells and the ladder-tip sentences, and leave every narrative
sentence to the post-record task that owns it. The parser change is two tokens and one perturbation
case — a gate nobody can fail is prose.

Step 9 — the audit is the deliverable that outlives the bytes. Mirror the baseline-7 audit's section
shape: §0 projection and actual, the validity gates, the recorded substrate stamp, the cell tables
before and after, the re-record log with causes, the provenance tuple, the decisions, what this
record does not discharge, and a method section that reproduces every derived figure offline at $0.
Cite the audit for the record's truth, never the PR body — PR bodies quote first-cut numbers and
have already caused one downstream citation error in this repository's history.

## Integration risk

The re-pin sweep is the widest half of this task and the census is bigger than it looks: 41 files
under `tests/` and 94 repo-wide at HEAD. The previous record learned this by missing a frontend
fixture that recomputes a corpus digest on every run. Budget the sweep as its own leg, start from
the repo-wide grep, and run the full suite in a clean worktree before the record commit is cut.

The freeze is this contract's to declare and Wave 1's parallel work is what makes it affordable. From
the smoke's GO until this PR merges, nothing may merge into engine/, agents/, meetings/,
observation/, orchestrator/ or the prompt set. The instrument, gate and prose tasks running beside
this one carry **Record impact:** none and land freely — that is why the wave was split that way. A
routed fix inside the frozen trees REOPENS the window: the smoke runs again from zero, on the
changed source, with every number re-derived. One coordination item is worth checking before the
first seed: if the mover-scenario diagnosis routes a FIX rather than a re-pin, the tactical policy
that drives every recorded game changes, and it must land BEFORE the smoke or these bytes record a
mover that HEAD no longer has.

The corpus fingerprint moves, and one constant has to move with it. The declared grounding gap names
exactly two digests, and any mismatch that is not that pair FAILS by design — so leaving the
right-hand digest at the old corpus turns the evidence command and its real-repo tests red for a
bookkeeping reason rather than a defect. Re-stamp it, do not widen the amnesty, and do not delete
it: the re-ground owns the deletion, and the assertion that must survive that deletion is that a
fingerprint MISMATCH fails.

Repointing the ladder-tip audit is a real coupling and not a cosmetic one. The fact checker locates
the record's read by heading, reads its pooled cells out of a labelled table, and holds README's
conviction-partition row and the reading guide's mirror to them; it also re-derives the win-rate
row's history column from the record's own win-split table, whose header names the previous
baseline. A maintenance record has no bars to put under those headings, so the locator is widened by
the minimum needed to find a published-cell section — with a perturbation case proving it still
bites — and the audit publishes the cells in the shape the checker reads. Get the orchestrator's
ruling on this and on the baseline-8 naming BEFORE dispatch: the alternative is to leave the tip at
baseline 7, and then the front door keeps quoting cells measured on bytes that no longer exist,
which is the exact defect A-15 documents.

A partial record is not a baseline. Checkpoint-push each completed seed range, never commit a
half-set as canonical, and if the window closes mid-run stop at a set boundary with the audit
stating which legs exist and which do not.

Finally, the doctrinal risk, which is the mirror of the previous record's. That one had to resist
adopting on a missed bar. This one has to resist reading a verdict into cells nobody pre-registered:
if a cell moves in a flattering direction, it is still only a published cell, and if it moves in an
unflattering one, it is published unchanged and routed. The bars in this phase belong to the Wave-2
record.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.rewards"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.replay_walk.ReplayWalkConfig"`
- `uv run python -c "import engine.tick"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import eval.watchability.SupplyFloors"`
- `uv run python -c "import eval.vj_instruments"`
- `uv run python -c "import eval.vj_instruments.VJInstrumentReport"`
- `uv run python -c "import eval.vj_instruments.VJMeetingRow"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import frontend/src/lib/contradictions"`
- `uv run python -c "import check_doc_facts"`

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
Open a PR from branch `phase-21-rerecord` with a title like `task 21.15: the combined re-record (operator, ~23 h, $0): four sets on the corrected substrate, the record audit, the re-pins`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing the Wave-0 register entries whose repairs ride these bytes — `audits/review-2026-08-26/A/collated-findings.md` A-14 (CONFIRMED, P1: on the 668 meeting-trigger ticks, 2,166 of 35,350 recorded actions — 6.13%, including 36 kills, 99 reports, 112 vents and 17 emergency calls — are recorded as submitted and never applied), A-31 (CONFIRMED: all 1,505 witness-side vent memories minted twice, and 27 of 27 heard-without-witnessed rows are impostors the teammate firewall leaked through), A-6, A-17, A-34, A-1, and A-15 (ADJUSTED, P1: the corpus README's whole Capability-disclosures section is baseline-6 arithmetic carried forward under a one-word substrate relabel — every item-8 figure reproduces exactly against `2df33ca4` and none against HEAD; item 1's 707 meetings is 668 on HEAD and item 2's 986 kill actions is 1,011 submitted); `audits/review-2026-08-26/B/collated-findings.md` B-8 (CONFIRMED: the belief line contradicts the agent's own sightings in 19% of rendered rows), B-6 (CONFIRMED: four live consumers re-derive contradictions without the private grounding channels), B-10 (ADJUSTED, P2: the pinned `flags_per_meeting` floors and their measured composition — `samples/9p2i` 92 persisted vent + 42 re-derived transcript = 134 over 152 meetings = 0.881578947368421; `ml_corpus/9p2i` 308 + 123 = 431 over 432; `samples/4p1i` 20 + 0 = 20 over 40; `ml_corpus/4p1i` 28 + 1 = 29 over 44), B-46 and B-20 (the STALE amnesty's exact declared digest pair and the five tests around it), B-18, B-19, B-23, B-51, B-52 (the recorder hardening this record runs on). `audits/audit-phase-20-baseline-7.md` §0.1 (the pre-committed bracket 22.2 h / 26.3 h from measured tokens), §0.2 (the recording protocol, the three carried operating notes, and the first-seed honesty probe per leg with a raise defined as a STOP), §0.3 (the actual: 300 games in 23h25m42s at $0.0000), §0.4 (two `(deadline_default)` re-records repaired in 12m33s), §6 (the pre-registered rule returned FINDING; bars 1 and 2 MISSED), §6.1 (**THE OWNER'S ADOPTION RULING — an owner override of a FINDING verdict**, and its "What no surface may say" clause), §8 (the referee floors), §10.1 (the substrate question, and the census lesson: start from a repo-wide grep, not a `tests/`-scoped one — `frontend/src/lib/bodies.test.ts` recomputes a corpus digest on every run), §10.2 (what that record deliberately did not discharge: the ML re-ground, the declared grounding gap, the dropped `samples/9p2i` MANIFEST disclosure block, and the production-side duplicate `alibi_vs_sighting` mint that rides inside the bytes), §10.3 (the three re-derivations that lost a claim, with their pinned divergence counts); `audits/audit-phase-20-close.md` F1 (the campaign tier RED at close HEAD: 9 failed, 308 passed) and F2 (`frontend/src/lib/bodies.test.ts:9`, a census header stale against its own pins). Anchors re-verified at HEAD `d8ec0a1c`: `orchestrator/replay.py:524-546` (`_RETIRED_ALWAYS_ON_LEVERS`, twenty-one keys), `:568-570` (`_TOGGLEABLE_LEVER_RESOLVERS`, ONE entry — `impostor_roll_call`), `:578-589` (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS` / `SUBSTRATE_FLAG_KEYS`), `:591` (`substrate_flag_snapshot`), `:651` (`substrate_slate_mismatches`); `scripts/refresh_samples.sh:36-37` (`AILIBI_SAMPLE_DIR`, `AILIBI_MANIFEST` defaulting under it), `:248-260` (`--expect-levers` parse; an explicitly empty value means the bare slate), `:291-326` (the preflight, delegating the comparison to `substrate_slate_mismatches`), `:441` and `:461` (worker and attempt defaults, 2 and 4), `:566` / `:588` (`REQUIRED_PROMPT_SET="qwen3_6_27b"`, `REQUIRED_SET_OWNER_MODEL="Qwen/Qwen3.6-27B"`), `:1030-1038` (the post-record eval-report rebuild) and `:1040-1074` (the rubric refresh, whose failure is declared to make the refresh incomplete); `scripts/record_ml_corpus.sh:107-166` (the pin block — already baseline-7-shaped, `REQUIRED_PROMPT_VERSIONS` at `:156` naming all four templates), `:345-392` (`write_splits`, the `seed % 5` rule), `:607-710` (`check_replay_provenance`, the `deadline_default` refusal at `:669-676`); `scripts/validity_gate.py:77-93` and `eval/validity.py:24-56` (the ten named checks); `eval/watchability.py:538` (`_BASELINE_SUPPLY_FLOORS`), `:841-905` (the baseline-7 block and its worked derivation), `:914` (`_DEFAULT_BASELINE_ID`); `scripts/verify_ml_evidence.py:182-206` (`_DECLARED_GROUNDING_GAP` and `_is_declared_grounding_gap` — one pair of digests, and any other mismatch FAILS); `scripts/check_doc_facts.py:203` (`_LADDER_TIP_AUDIT`), `:237-242` (`_LADDER_TIP_DOCUMENTS`), `:538-560` (the record-read parser's heading, table header and win-split header tokens), `:1119` / `:1722` / `:1784` / `:1922` / `:2027` / `:2587` / `:3006` / `:3077` (ladder tip, audits index, results agreement, result sources, conviction partition, `record_partition`, verdict figures, featured exhibits); `tests/meetings/test_prompt_byte_golden.py:183` (`ARCHIVED_PROMPT_VERSION_SETS = {}`, and `tests/fixtures/prompt_archive/` does not exist) with the perturbation leg at `:1162-1184` (victim: the LIVE `qwen3_6_27b/crewmate_report.j2`); `tests/meetings/test_contradictions.py:3146` (`_COMMITTED_MEETINGS = 668  # baseline 6: 707`); `tests/eval/test_deduction_metrics.py:152` and `:179` (the `# was …` convention this sweep keeps); `frontend/src/lib/bodies.test.ts:441-511` over `bodies.fixture.json`; `docs/artifacts.md:107` (`7.9 MB / 158 files`, and `git ls-files audits` = 158); `docs/glossary.md:38-59` (the definitions of *baseline N* and *the ladder tip*); `replays/ml_corpus/README.md:104-126` + `:255-277` (the disclosures) and `:296-313` (the leg table); `replays/samples/9p2i/MANIFEST.md` (twenty-one flag keys, four `qwen3_6_27b.v4` templates, `fsm-default`, `2026-08-25`, `0.0000`); AGENTS.md:91-124 (the craft rules). Census re-run at HEAD: `grep -rln 'replays/samples\|replays/ml_corpus' tests/` = 41 files; the same pattern repo-wide over `*.py`, `*.ts`, `*.tsx`, `*.json` and `*.sh`, excluding `replays/`, `audits/` and `node_modules/`, = 94 files (the 41 among them).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
