# Agent Prompt — 21.11 Prose that is true at HEAD: the F2 class swept, the corpus disclosures re-derived, four ungated claims given teeth

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.11 — Prose that is true at HEAD: the F2 class swept, the corpus disclosures re-derived, four ungated claims given teeth, anchored to F2, F3, F4 and the routed walker item — audits/audit-phase-20-close.md:115-121 (F2, the two stale narrations "whose own committed pins already disagree with them"), :125-152 (F3, the three front-door budgets and the ruling that "a budget nothing can fail is prose — Craft rule 2 applied to a documentation target"), :154-177 (F4, whose *prose* half was corrected in the close PR and whose *gate-coverage* half — "adding `audits/README.md` to `_LADDER_TIP_DOCUMENTS` … wants its own perturbation case" — is what lands here), :408 (`eval/replay_walk.py` performs no substrate check; "the one-line fix is the now-public `orchestrator.replay.retired_levers_stamped_off`", routed with 20.37's merge record `a9952d29`). A-15 [ADJUSTED, P1] — audits/review-2026-08-26/A/collated-findings.md:1912-1990 (the finding, its four measurements and the verifier's independent re-run, including the root cause `git diff 2df33ca4 efcd43b8 -- replays/ml_corpus/README.md` → one word changed, "baseline-6 substrate" → "baseline-7 substrate", with every number left as recorded on the baseline-6 bytes; and the verifier's correction that *nothing* in the 4p pair matches, since README's `(S4, C4)` impostor cells are `(8/39, 5/40)` and HEAD's S4 `5/40` merely coincides with the README's C4 cell). B-47 [ADJUSTED, P3] — audits/review-2026-08-26/B/collated-findings.md:2493-2520, whose verifier keeps ONLY the comment half: `BAKEOFF_BASELINE_ID` "is SPECIFIED as correct, not stale", audits/audit-phase-20-baseline-7.md §10.2 says it "names the baseline the bake-off is GROUNDED on, not the substrate baseline", and moving it is an explicitly routed item of the ML re-ground — cited here as the EVIDENCE for a routing, not as work: assembly moved B-47's comment block to Task 21.17 so it travels with the constant, and this contract's F2 slot is `docs/history.md`'s stale "## In progress: phase 20" heading (`:160`, `:170`) instead. A second F2-class site, found at the #403 merge: `docs/glossary.md:66` reads "Thirteen have graduated and one live toggle remains" where the live registry at HEAD gives TWENTY-ONE graduated and THREE live toggles (`impostor_roll_call`, `last_seen_from_sightings`, `vent_single_mint` — the latter two added by 21.4 #403 and 21.5 #404) — swept here with the same treatment, and the corrected sentence must state the CURRENT truth on both halves, not only the graduated count. B-50 [ADJUSTED, P2] — audits/review-2026-08-26/B/collated-findings.md:2639-2700, with both verifier corrections binding: the stale-site count is ~25 not 29 (`:9`, `:27`, `:83`, `:127` are correct historical references) and `tests/scripts/test_record_ml_corpus.py` re-asserts five of the stale operator strings verbatim, so the sweep is not a free `sed` pass. **Anchors re-verified at HEAD `4002f19b`:** the orchestrator/game.py F2 site is CLOSED by 21.1 (#406) and is no longer owned here: the five-paragraph changelog is gone, replaced by an intent-first block at `:365-377` whose archive sentence (`:372-374`, "The committed sample sets stamp v4 and resolve through tests/fixtures/prompt_archive/qwen3_6_27b_v4/ until the adopting record retires that entry") is TRUE at HEAD — the directory exists on disk and `tests/meetings/test_prompt_byte_golden.py:183` `ARCHIVED_PROMPT_VERSION_SETS` holds the `qwen3_6_27b_v4` entry with the bump-in-flight window OPEN (live registry v5, committed sets v4); frontend/src/lib/bodies.test.ts:9 still reads "0 phantom frames vs 1,182 of 1,769 on `9p2i`" while its two cases at `:447` and `:465` assert `frames: 1217` with `phantomFrames: 0` and `phantomFrames: 668, phantomBodies: 1371`; eval/watchability.py:908-913 says `BAKEOFF_BASELINE_ID` "still reads ``baseline-5``" against training/bakeoff/harness.py:181 `BAKEOFF_BASELINE_ID: Final[str] = "baseline-6"`, with `_DEFAULT_BASELINE_ID: Final[str] = "baseline-7"` on the next line at `:914`; scripts/check_doc_facts.py:237-242 `_LADDER_TIP_DOCUMENTS` is `(_README, _GLOSSARY, _HISTORY, _READING_GUIDE)` and audits/README.md:265 (one "ladder tip" phrase in the file, naming baseline 7) is outside it, while `grep -n word scripts/check_doc_facts.py` still finds no budget of any kind; `wc -w README.md docs/reading-guide.md docs/ml-program.md docs/lessons.md` reads 3,487 / 1,303 / 2,063 / 1,491; `grep -c "baseline-6\|baseline 6" scripts/record_ml_corpus.sh` is 28 at HEAD after 21.10's rewrite (24 stale + 4 historical), against the PIN BLOCK now at `:112-137` ("the baseline-7 substrate … the qwen3_6_27b prompt set at v4 … the twenty-one retired always-on levers", the v4 and one-toggle clauses themselves now stale) and `:167` `REQUIRED_PROMPT_VERSIONS`, and `uv run python -c "from orchestrator.replay import SUBSTRATE_FLAG_KEYS,_RETIRED_ALWAYS_ON_LEVERS,TOGGLEABLE_SUBSTRATE_FLAG_KEYS as T; print(len(SUBSTRATE_FLAG_KEYS), len(_RETIRED_ALWAYS_ON_LEVERS), T)"` prints `24 21 ('impostor_roll_call', 'last_seen_from_sightings', 'vent_single_mint')`; replays/ml_corpus/README.md:104-126 is the disclosures header (`:107` "Every number below was recomputed from the committed bytes", `:112` "at the same baseline-7 substrate"), `:131` "707/707", `:140` "986", `:255-277` item 8, `:279-291` item 9; tests/eval/test_deduction_metrics.py:498 and :535 are the two docstrings that quote the stale figures beside asserts that pin the current ones; eval/replay_walk.py:214-227 `WalkViolationKind`, :235-253 `WalkViolation`, :257-294 `ReplayWalkConfig` (whose `verify_action_dispositions` field 21.3 added at `:280` — no collision with the new field name), :85-120 the PROFILE TABLE the new option must join, :407-420 (`read_all_entries`, then the `game_end` row is already in hand) and eval/funnel.py:240-247 `_WALK_CONFIG`, the profile shared by BOTH funnel walks — UNMOVED, the DoD's `:240` still exact; orchestrator/replay.py:834-869 `substrate_stamp_mismatches`, :778 `retired_levers_stamped_off` (now zero production callers) and :1373 `read_substrate_flags`, with audits/workflows/extract_gameplay_facts.py:2170-2185 the precedent refusal.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-prose-truth`
**Depends on:** 21.1, 21.6, 21.7, 21.10
**Section refs:** F2, F3, F4 and the routed walker item — audits/audit-phase-20-close.md:115-121 (F2, the two stale narrations "whose own committed pins already disagree with them"), :125-152 (F3, the three front-door budgets and the ruling that "a budget nothing can fail is prose — Craft rule 2 applied to a documentation target"), :154-177 (F4, whose *prose* half was corrected in the close PR and whose *gate-coverage* half — "adding `audits/README.md` to `_LADDER_TIP_DOCUMENTS` … wants its own perturbation case" — is what lands here), :408 (`eval/replay_walk.py` performs no substrate check; "the one-line fix is the now-public `orchestrator.replay.retired_levers_stamped_off`", routed with 20.37's merge record `a9952d29`). A-15 [ADJUSTED, P1] — audits/review-2026-08-26/A/collated-findings.md:1912-1990 (the finding, its four measurements and the verifier's independent re-run, including the root cause `git diff 2df33ca4 efcd43b8 -- replays/ml_corpus/README.md` → one word changed, "baseline-6 substrate" → "baseline-7 substrate", with every number left as recorded on the baseline-6 bytes; and the verifier's correction that *nothing* in the 4p pair matches, since README's `(S4, C4)` impostor cells are `(8/39, 5/40)` and HEAD's S4 `5/40` merely coincides with the README's C4 cell). B-47 [ADJUSTED, P3] — audits/review-2026-08-26/B/collated-findings.md:2493-2520, whose verifier keeps ONLY the comment half: `BAKEOFF_BASELINE_ID` "is SPECIFIED as correct, not stale", audits/audit-phase-20-baseline-7.md §10.2 says it "names the baseline the bake-off is GROUNDED on, not the substrate baseline", and moving it is an explicitly routed item of the ML re-ground — cited here as the EVIDENCE for a routing, not as work: assembly moved B-47's comment block to Task 21.17 so it travels with the constant, and this contract's F2 slot is `docs/history.md`'s stale "## In progress: phase 20" heading (`:160`, `:170`) instead. A second F2-class site, found at the #403 merge: `docs/glossary.md:66` reads "Thirteen have graduated and one live toggle remains" where the live registry at HEAD gives TWENTY-ONE graduated and THREE live toggles (`impostor_roll_call`, `last_seen_from_sightings`, `vent_single_mint` — the latter two added by 21.4 #403 and 21.5 #404) — swept here with the same treatment, and the corrected sentence must state the CURRENT truth on both halves, not only the graduated count. B-50 [ADJUSTED, P2] — audits/review-2026-08-26/B/collated-findings.md:2639-2700, with both verifier corrections binding: the stale-site count is ~25 not 29 (`:9`, `:27`, `:83`, `:127` are correct historical references) and `tests/scripts/test_record_ml_corpus.py` re-asserts five of the stale operator strings verbatim, so the sweep is not a free `sed` pass. **Anchors re-verified at HEAD `4002f19b`:** the orchestrator/game.py F2 site is CLOSED by 21.1 (#406) and is no longer owned here: the five-paragraph changelog is gone, replaced by an intent-first block at `:365-377` whose archive sentence (`:372-374`, "The committed sample sets stamp v4 and resolve through tests/fixtures/prompt_archive/qwen3_6_27b_v4/ until the adopting record retires that entry") is TRUE at HEAD — the directory exists on disk and `tests/meetings/test_prompt_byte_golden.py:183` `ARCHIVED_PROMPT_VERSION_SETS` holds the `qwen3_6_27b_v4` entry with the bump-in-flight window OPEN (live registry v5, committed sets v4); frontend/src/lib/bodies.test.ts:9 still reads "0 phantom frames vs 1,182 of 1,769 on `9p2i`" while its two cases at `:447` and `:465` assert `frames: 1217` with `phantomFrames: 0` and `phantomFrames: 668, phantomBodies: 1371`; eval/watchability.py:908-913 says `BAKEOFF_BASELINE_ID` "still reads ``baseline-5``" against training/bakeoff/harness.py:181 `BAKEOFF_BASELINE_ID: Final[str] = "baseline-6"`, with `_DEFAULT_BASELINE_ID: Final[str] = "baseline-7"` on the next line at `:914`; scripts/check_doc_facts.py:237-242 `_LADDER_TIP_DOCUMENTS` is `(_README, _GLOSSARY, _HISTORY, _READING_GUIDE)` and audits/README.md:265 (one "ladder tip" phrase in the file, naming baseline 7) is outside it, while `grep -n word scripts/check_doc_facts.py` still finds no budget of any kind; `wc -w README.md docs/reading-guide.md docs/ml-program.md docs/lessons.md` reads 3,487 / 1,303 / 2,063 / 1,491; `grep -c "baseline-6\|baseline 6" scripts/record_ml_corpus.sh` is 28 at HEAD after 21.10's rewrite (24 stale + 4 historical), against the PIN BLOCK now at `:112-137` ("the baseline-7 substrate … the qwen3_6_27b prompt set at v4 … the twenty-one retired always-on levers", the v4 and one-toggle clauses themselves now stale) and `:167` `REQUIRED_PROMPT_VERSIONS`, and `uv run python -c "from orchestrator.replay import SUBSTRATE_FLAG_KEYS,_RETIRED_ALWAYS_ON_LEVERS,TOGGLEABLE_SUBSTRATE_FLAG_KEYS as T; print(len(SUBSTRATE_FLAG_KEYS), len(_RETIRED_ALWAYS_ON_LEVERS), T)"` prints `24 21 ('impostor_roll_call', 'last_seen_from_sightings', 'vent_single_mint')`; replays/ml_corpus/README.md:104-126 is the disclosures header (`:107` "Every number below was recomputed from the committed bytes", `:112` "at the same baseline-7 substrate"), `:131` "707/707", `:140` "986", `:255-277` item 8, `:279-291` item 9; tests/eval/test_deduction_metrics.py:498 and :535 are the two docstrings that quote the stale figures beside asserts that pin the current ones; eval/replay_walk.py:214-227 `WalkViolationKind`, :235-253 `WalkViolation`, :257-294 `ReplayWalkConfig` (whose `verify_action_dispositions` field 21.3 added at `:280` — no collision with the new field name), :85-120 the PROFILE TABLE the new option must join, :407-420 (`read_all_entries`, then the `game_end` row is already in hand) and eval/funnel.py:240-247 `_WALK_CONFIG`, the profile shared by BOTH funnel walks — UNMOVED, the DoD's `:240` still exact; orchestrator/replay.py:834-869 `substrate_stamp_mismatches`, :778 `retired_levers_stamped_off` (now zero production callers) and :1373 `read_substrate_flags`, with audits/workflows/extract_gameplay_facts.py:2170-2185 the precedent refusal.
**Complexity:** Medium
**Record impact:** none
**Measurement:** `uv run python scripts/check_doc_facts.py` exits 0 at HEAD; `uv run pytest tests/scripts/test_check_doc_facts.py tests/eval/test_replay_walk.py tests/scripts/test_record_ml_corpus.py tests/eval/test_deduction_metrics.py -q` green, each of the four new gates red on its own planted perturbation; `git grep -nI "baseline-6\|baseline 6" scripts/record_ml_corpus.sh` returns only the four historical citations (`:9` the audit filename, `:27` and `:89` the Task-18.13 wall-clock notes, `:133` the deliberate refusal example inside the pin block); the PR quotes every re-derived corpus-disclosure cell beside the value it replaces, with the command that produced it.

Six committed surfaces state numbers that this repo's own committed pins already contradict. That
is one defect class, not six items, and its shape is always the same: prose restates a value that
lives somewhere else, and then the value moves. Craft rule 5 asks a claim to name the mechanism that
enforces it; every site below instead copied a number and left no way to notice when the copy went
wrong. The Phase-20 close named two of them as F2, measured three ungated word budgets as F3, found
the audits index stating a ladder tip no gate could reach as F4, and routed a walker with no
substrate check at all. The 2026-08-26 registers then found two more sites of exactly the same
class, one of them P1.

The P1 is A-15, and it is the reason this is a task rather than a chore. `replays/ml_corpus/README.md`
opens its Capability-disclosures section with *"Every number below was recomputed from the committed
bytes"* (`:107`) and labels the four measured sets as recorded "at the same baseline-7 substrate"
(`:112`). The label is the only thing that moved: the verifier reproduced every item-8 numerator and
denominator exactly against `git show 2df33ca4:` — the baseline-6 bytes — and none against HEAD, and
`git diff 2df33ca4 efcd43b8 -- replays/ml_corpus/README.md` shows the section's sole change at the
adopting record was `baseline-6 substrate` → `baseline-7 substrate`. The staleness is not confined
to item 8. Item 1's *"707/707 meetings are crew-triggered"* reads 668 on HEAD — 152 + 432 + 40 + 44,
summed here from the four committed `tournament-eval-report.json` files' own
`deduction.public_response_coverage` macro-meeting counts. Item 2's *"986 recorded `kill` actions"*
is 1,011 submitted. And item 9's *"798 resolved kills"* is provably the baseline-6 sum:
177 + 505 + 61 + 55 = 798 exactly, while `tests/eval/test_kill_craft.py` now asserts
`kills_total == 526  # was 505` (`:69`), `== 65  # was 61` (`:127`), `crew_witnessed_kills == 16
# was 12` (`:70`) and `== 3  # was 6` (`:101`). Those `# was` markers are the record's own
handwriting: the pins WERE re-derived at the baseline-7 record and the README was not, so the
section's boast that its *"Resolved counts match the committed kill-craft pins exactly (177/505/61)"*
is false against the file it names.

This matters past bookkeeping because item 8 is the section the ML program reads to learn what the
impostor tell is. As written it tells a fitter that impostors lie in whereabouts about half the time
(58/120 = 48.3%, 155/342 = 45.3%) — a rich, learnable deception signal. Both the finder and the
verifier reconstructed the truth two independent ways, from the engine's own rendered route line and
from a from-scratch tick replay, and got ~99% truthful for BOTH roles (pooled crewmate
2,701/2,722 = 0.9923, impostor 391/395 = 0.9899). The real tell is the *absent* observation, and the
README understates it too, quoting 49.0%/50.0% coverage against a crew baseline of 99.6%/99.7% where
the committed bytes give 47.5%/45.3% against a crew baseline of exactly 100.0%. Task 21.17 re-fits on
this corpus. It must not read this page first.

F2's two sites are smaller and one of them is bigger than it looks. `frontend/src/lib/bodies.test.ts:9`
is a single sentence: the negative control is described with the baseline-6 census (1,182 of 1,769)
while the two cases beneath it pin 1,217 frames and 668 phantom frames on the bytes they actually
walk. The gate is correct and bites; only its header sentence lies, so this is a one-line truth-up.
`orchestrator/game.py` is not one line. Lines 355-390 are a five-paragraph changelog of every prompt
bump from 16.13 forward, and two of its paragraphs tell the reader that committed samples still stamp
v1 and v3 and re-render through archived bodies under `tests/fixtures/prompt_archive/` "until 16.17
re-records" and "until the adopting record retires that entry". Both records happened; the directory
does not exist; and the archive registry those sentences describe does not live in this file at all —
it is `ARCHIVED_PROMPT_VERSION_SETS` in `tests/meetings/test_prompt_byte_golden.py:184`, currently
`{}` and correctly documented as EMPTY at `:178-181`. Craft rule 1 is the fix, not a patch: source
files are not changelogs, so the block collapses to what the mapping IS and one trailing provenance
line, and the two false sentences leave with it.

B-47 is the same disease at a third site and this contract does NOT fix it — assembly routed it
away, and the reason is worth stating because it is the general rule. Its verifier keeps only the
comment half: `eval/watchability.py:908-914` says `BAKEOFF_BASELINE_ID` "still reads
``baseline-5``" when it reads `baseline-6`, in a note whose entire job is to tell the next
re-ground which constant lags. The constant itself is **not** stale —
audits/audit-phase-20-baseline-7.md §10.2 rules it correct, because it names the baseline the
bake-off is grounded on rather than the substrate baseline, and moving it is a named item of the ML
re-ground. A note rewritten HERE would describe a constant that has not moved yet and would need
editing again the moment it did; the comment block and the value it describes belong in one commit,
so both are Task 21.17's. `eval/watchability.py`'s bake-off-lag block is out of scope in this
contract, and the F2 slot it would have filled is taken by `docs/history.md`'s "## In progress:
phase 20" heading at `:160` and `:170` — a document that announces a phase the repository closed at
`d8ec0a1c`, which is the same defect class on the front door's own reading path.

B-50 is the fourth site. `scripts/record_ml_corpus.sh` carries a correct
baseline-7 PIN BLOCK (`:105-115`) inside ~25 lines of baseline-6 narration, three of which the
operator reads at record time, including `:913` printing "resolves to the baseline-6 map" followed by
four `v4` version strings. Four of the 29 grep hits are correct historical references (`:9` an audit
filename, `:27` and `:83` Task-18.13 wall-clock notes, `:127` the deliberate refusal example inside
the correct pin block) and stay exactly as written. Five stale strings are re-asserted verbatim every
run by `tests/scripts/test_record_ml_corpus.py` (`:325`, `:498`, `:525`, `:586`, `:627`), so those
assertions move in the same commit or the suite goes red. The header's "thirteen retired always-on
levers" is wrong by eight: the live registry reads 21 retired and THREE toggleable
(`impostor_roll_call`, `last_seen_from_sightings`, `vent_single_mint`). The PIN BLOCK is no
longer wholly correct either — `:123-124` still says "the one surviving live toggle
(impostor_roll_call)", which 21.4 and 21.5 falsified, and `:120` still says "the qwen3_6_27b
prompt set at v4" while `REQUIRED_PROMPT_VERSIONS` at `:167` was bumped to v5 by 21.1. Both
are the same defect class and are swept here.

The remaining three items are gates, and they exist because Craft rule 2 says a gate nobody can fail
is prose. F4's prose half was already corrected — audits/README.md:265 now reads "which is why the
ladder tip stands at baseline 7" — but the reason it went wrong is untouched: `check_ladder_tip`
scans only `_LADDER_TIP_DOCUMENTS`, and the audits index is not in it. Adding it is one line, and it
is green today (the file's single "ladder tip" phrase names baseline 7 and nothing else). F3 is the
budget ruling: three front-door word budgets were written into contract Measurement fields, none was
enforceable, and all three were already over at the merge of the contract that set them. This
contract executes the ruling the planning PR ratifies — the aspirational targets are replaced by
enforceable ceilings pinned just above the counts at HEAD, gated in `check_doc_facts.py`, and allowed
to move only downward without an owner-ratified contract. `docs/lessons.md`'s 800–1,500 band is the
one budget HEAD satisfies and is carried through unchanged, which is precisely why gating it costs
nothing and proves the mechanism. And the walker: `eval/replay_walk.py` performs no substrate check,
so `compute_pooling_funnel` and the VJ instruments would re-derive always-on rules over
earlier-substrate bytes without noticing. the shared comparison is `orchestrator.replay.substrate_stamp_mismatches`, introduced by 21.10 (#405)
as "the shared comparison behind every substrate refusal", and `audits/workflows/extract_gameplay_facts.py:2170-2185`
already shows the refusal it enables — filtering `TOGGLEABLE_SUBSTRATE_FLAG_KEYS` out of its
`.differing` to isolate the retired half; the
walker's locked design forbids a mandatory check, so this ships as one more profile OPTION, default
off, turned on by the shared funnel/vj profile.

Nothing here moves a recorded byte. `**Record impact:** none` is literal: no prompt template, no
detector, no engine rule, and no committed replay is touched, and the corpus disclosures are
recomputed *over the bytes as committed* rather than re-recorded. One consequence must be stated
plainly rather than discovered later — Task 21.15 re-records all four sets, so the numbers this task
republishes will move again the moment it lands. That is the point of shipping the re-derivation as a
gate: after this task the disclosures section cannot be relabelled without its arithmetic, and
21.15's own acceptance run will say so. Context for the surfaces this task edits: baseline 7 is canon
by explicit owner override of a FINDING verdict — bars 1 and 2 were missed and neither was re-priced
— and no sentence written here may say or imply otherwise.

**Files in scope:**
- replays/ml_corpus/README.md; (the Capability-disclosures section re-derived from the committed bytes — items 1, 2, 8 and 9 at minimum, plus the section header's provenance sentence)
- scripts/check_doc_facts.py; (the audits index joins `_LADDER_TIP_DOCUMENTS`; the front-door budgets; the corpus-disclosure re-derivation)
- tests/scripts/test_check_doc_facts.py; (one planted perturbation per new gate, in the existing `doc_tree` fixture)
- frontend/src/lib/bodies.test.ts; (the header sentence at `:9`, re-derived from the two cases beneath it)
- docs/glossary.md; (the graduated-lever and live-toggle counts at `:66`, re-derived from the registry — that one sentence only; RATIFIED at merge: the re-anchored Section refs instructed this edit but this list never gained the file, and the implementer correctly kept the edit and asked)
- docs/history.md; (the "## In progress: phase 20" heading at `:160` and `:170` reads the closed phase — heading and its one sentence only, no narrative rewrite)
- eval/replay_walk.py; (the retired-lever profile option and its violation kind)
- eval/funnel.py; (`_WALK_CONFIG` at `:240` turns the option on for both funnel walks)
- tests/eval/test_replay_walk.py; (the planted stamped-OFF case, both profile directions)
- scripts/record_ml_corpus.sh; (the ~25 stale narration sites; the runtime echoes derive from the constants)
- tests/scripts/test_record_ml_corpus.py; (the five verbatim stderr assertions move in lockstep)
- tests/eval/test_deduction_metrics.py; (the two docstrings at `:493` and `:530` — docstrings only, no assert changes)

**Files NOT in scope:**
- training/bakeoff/harness.py (`BAKEOFF_BASELINE_ID` is ruled CORRECT at HEAD by audits/audit-phase-20-baseline-7.md §10.2; moving it is a named item of the ML re-ground, and doing it here would break `tests/training/test_bakeoff_harness.py:164-174`)
- eval/watchability.py (B-47's bake-off-lag comment block at `:908-914` is Task 21.17's, routed there at assembly so the note and the constant it describes move in ONE commit; this contract quotes the routing in its PR and edits no line of the file)
- audits/audit-phase-20-baseline-7.md and audits/audit-phase-20-close.md (dated records; the false clause at baseline-7.md:576-579 — "the recorder pin blocks and the corpus README all re-derived from these bytes" — is quoted and corrected in the PR description, never rewritten in place)
- README.md, docs/reading-guide.md, docs/ml-program.md, docs/lessons.md (this task gates the budgets; it does not trim the prose, and the ceilings are set so no trim is required to go green)
- training/reports/report-ballot-surrogate.md (B-50's sibling "thirteen retired always-on levers" line at `:23`; the ML re-ground re-publishes this report, so fixing it here would be re-published over)
- tests/meetings/test_prompt_byte_golden.py (its archive prose is ACCURATE at HEAD — the registry carries `qwen3_6_27b_v4` and the module docstring documents the bump-in-flight window as OPEN (21.1 #406) — and the byte-golden is the prompt-set task's file)
- replays/samples/, replays/ml_corpus/*.jsonl (no re-record; the disclosures are recomputed over the bytes exactly as committed)
- agents/strategic/prompts/ (no prompt template is touched by this task)
- tasks/phase-20.md (historical contracts; their Measurement-field targets are superseded by the ratified ruling, not edited)
- orchestrator/replay.py (`retired_levers_stamped_off` is consumed as-is; no signature moves)

**Definition of done:**
- [ ] `replays/ml_corpus/README.md`'s Capability-disclosures section is re-derived from the committed bytes and every changed cell is quoted in the PR beside the value it replaced, with the command that produced it. At minimum item 1's meeting/opening/submission counts, item 2's submitted-kill total and its per-set non-resolving split, item 8's four coverage pairs AND its whereabouts-match cell, and item 9's resolved-kill and crew-witnessed totals. Item 8's whereabouts-match cell states its frame explicitly and, if the ~48%/79.5% figures cannot be reproduced in EITHER frame, it is retired with a sentence saying so rather than carried forward — the verifier reproduced ~99% truthfulness for both roles in both frames.
- [ ] The section's own header stops asserting provenance it cannot prove: the "Every number below was recomputed from the committed bytes" sentence names the gate that re-derives it, and the item-2 sentence claiming the resolved counts "match the committed kill-craft pins exactly (177/505/61)" is re-derived against `tests/eval/test_kill_craft.py:69/:100/:127` as they read at HEAD (526 / 177 / 65).
- [ ] `check_doc_facts.check_corpus_disclosures` re-derives the section's headline cells from `replays/ml_corpus/{4p1i,9p2i}` and `replays/samples/{4p1i,9p2i}` `tournament-eval-report.json` and fails on disagreement, so the section cannot be relabelled without its arithmetic again. A perturbation case in `tests/scripts/test_check_doc_facts.py` edits one number in the fixture's README copy and asserts the specific error — the gate must be shown failing, not asserted to work.
- [ ] `orchestrator/game.py`'s prompt-version registry comment block states what the mapping IS and carries at most one trailing provenance line; the two sentences promising an archive at `tests/fixtures/prompt_archive/` are gone, and `git grep -nI "prompt_archive" -- . ':!audits' ':!tasks' ':!agent_prompts'` returns only the three accurate lines in `tests/meetings/test_prompt_byte_golden.py`. No value in `PROMPT_VERSION_SETS` changes.
- [ ] `frontend/src/lib/bodies.test.ts:9` states the census its own two cases assert (1,217 frames; 0 phantom frames for the shipped rule, 668 for the retired accumulate rule) and `npm --prefix frontend test` stays green with no assertion edited.
- [ ] `docs/history.md` no longer announces a closed phase as running: the "## In progress: phase 20" heading at `:160` and its sentence at `:170` read the phase's actual state (CLOSED 2026-08-26 at `d8ec0a1c`, `audits/audit-phase-20-close.md`), the heading and that one sentence being the whole edit — the paragraph's narrative and the lever-graduation provenance beneath it are left exactly as written, and NO phase-21 section is added (README.md's phase table at `:201` already carries the open phase-21 row, which is what `check_phase_coverage` reads), and `uv run python scripts/check_doc_facts.py` still exits 0.
- [ ] `eval/watchability.py` is UNCHANGED in this PR — `git diff --name-only` does not list it — and the PR states in one line that B-47's comment block travels with `BAKEOFF_BASELINE_ID` at Task 21.17 rather than being half-fixed here.
- [ ] `scripts/check_doc_facts.py`'s `_LADDER_TIP_DOCUMENTS` includes `audits/README.md`, and a perturbation case flips the fixture's copy of that entry to name baseline 6 and asserts the resulting error names the file and the line. `uv run python scripts/check_doc_facts.py` still exits 0 at HEAD.
- [ ] `check_doc_facts.check_front_door_budgets` enforces one word budget per front-door page — `README.md` ≤ 3,550, `docs/reading-guide.md` ≤ 1,350, `docs/ml-program.md` ≤ 2,150, `docs/lessons.md` 800–1,500 — measured the way F3 measured them (`wc -w` semantics), with the constants' docstring recording that a ceiling may be lowered by any contract and raised only by an owner-ratified one. A perturbation case pads the fixture's README past its ceiling and asserts the error; a second asserts the `docs/lessons.md` FLOOR bites, since a range budget with only a ceiling is half a gate.
- [ ] The four counts at HEAD are stated in the PR (`wc -w README.md docs/reading-guide.md docs/ml-program.md docs/lessons.md` → 3,487 / 1,303 / 2,063 / 1,491) alongside each new ceiling, so the headroom the ruling grants is visible rather than implied.
- [ ] `eval/replay_walk.py` gains `ReplayWalkConfig.reject_retired_levers_stamped_off` (default `False`) and a `retired_levers_stamped_off` member of `WalkViolationKind`; the check runs once per walk, before the first advance, against the recording's `game_over` stamp via `orchestrator.replay.retired_levers_stamped_off`, and an UNSTAMPED recording is skipped exactly as that function documents. The module docstring's "NO check is core-mandatory" claim stays true.
- [ ] `eval/funnel.py:240`'s `_WALK_CONFIG` sets the new option, so both funnel walks and the VJ instruments refuse legacy-substrate bytes; `tests/eval/test_replay_walk.py` gains a planted case that rewrites a throwaway recording's `game_over` `substrate_flags` to stamp a retired lever OFF and asserts the ON profile violates with that kind while the OFF profile still walks it clean — the same perturbation shape the file already uses for the forged winner.
- [ ] `scripts/record_ml_corpus.sh`'s narration matches its own PIN BLOCK: `git grep -nI "baseline-6\|baseline 6" scripts/record_ml_corpus.sh` returns only `:9`, `:27`, `:83` and `:127`, the four correct historical references. The header's "all four templates at v3" and "the thirteen retired always-on levers" read the committed truth, and the three operator-facing lines (`:185` usage, `:791` dry-run, `:913` preflight) derive from `$REQUIRED_PROMPT_VERSIONS` / the pin-block constants rather than restating a version or a count in prose.
- [ ] `tests/scripts/test_record_ml_corpus.py`'s five verbatim stderr assertions (`:324`, `:486`, `:513`, `:574`, `:615`) move with the strings they pin and `uv run pytest tests/scripts/test_record_ml_corpus.py -q` is green; the PR states that these assertions were re-asserting the stale labels every run, which is why the sweep was not a `sed` pass.
- [ ] `tests/eval/test_deduction_metrics.py`'s two docstrings stop claiming agreement with a document they contradict: `:493`'s "byte for byte" sentence and `:530`'s quoted 4p pair are re-written against the republished README, with every `assert` and every `# was` marker left exactly as committed.
- [ ] The PR quotes audits/audit-phase-20-baseline-7.md:576-579 and states which half of it was false — the recorder PIN BLOCK *was* re-derived at the record; the recorder's surrounding narration and the corpus README were not — without editing the audit.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — write the four perturbations first, and watch each fail at HEAD before the gate exists. This
is the whole point of the task; a gate added before its planted case proves nothing. The fixture in
`tests/scripts/test_check_doc_facts.py` already copies every file three of them need — `README.md`,
`docs/reading-guide.md`, `docs/ml-program.md`, `docs/lessons.md`, `audits/README.md`,
`replays/ml_corpus/{4p1i,9p2i}/tournament-eval-report.json` and
`replays/samples/{4p1i,9p2i}/tournament-eval-report.json` are all in `_COPIED` (`:32-63`), so a
perturbation is a `read_text` / `replace` / `write_text` on the tmp tree followed by
`check_doc_facts.check_facts(tmp_root)`. The four eval reports are symlinked rather than copied above
the size threshold, so perturb the README, never the report.

Step 2 — the disclosures. Do the arithmetic BEFORE writing a word of prose, from the shipped
instruments where they exist. `deduction.public_response_coverage` in each set's
`tournament-eval-report.json` gives item 8's four coverage pairs directly and its
`crew_macro_meetings` summed over the four sets gives item 1's meeting count; the resolved-kill and
crew-witnessed totals for three of the four sets are already pinned in
`tests/eval/test_kill_craft.py:69/:70/:100/:101/:127/:128`, and only `replays/ml_corpus/4p1i` needs a
fresh recount. For the whereabouts-match cell, note the verifier's trap explicitly: the engine's
rendered route line writes a vent as "a vent in ROOM", and normalising that segment to `ROOM` is what
separates a 92.3% reading from the true ~98%. State the frame you used in the published sentence.

Step 3 — `check_corpus_disclosures`. Keep it narrow and mechanical. Parse the bold numerators the
section already writes (`**723/726**`-shaped cells), re-derive the same cells from the four reports,
and report a disagreement per cell with the README line number. Register it in `check_facts`
(`scripts/check_doc_facts.py:712-737`) beside the other `repo_root`-taking checks. Resist the urge to
re-derive item 9's histogram here — the kill-craft pins already gate it, and a gate that duplicates a
gate is the thing this phase is cleaning up. The section's provenance sentence should name this
function, which is Craft rule 5 satisfied rather than asserted.

Step 4 — the two one-liners and the two comment rewrites. `_LADDER_TIP_DOCUMENTS` gains one entry;
confirm first with `git grep -nIc -i "ladder tip" audits/README.md` that the file holds exactly one
phrase and that `sentence_around` picks up only "baseline 7" from it — the preceding markdown link
`[audit-phase-20-baseline-7.md](...)` sits in the previous sentence, which is why this lands green.
For `orchestrator/game.py`, delete the changelog and keep one line naming what the mapping is and the
record that last moved it; do not touch `_bespoke_versions(...)` or any value. For
`eval/watchability.py:908-913`, the smallest honest note is one sentence pointing at
`training.bakeoff.harness.BAKEOFF_BASELINE_ID` and audits/audit-phase-20-baseline-7.md §10.2 for why
it deliberately lags — with no number in it at all.

Step 5 — the walker. `walk_replay` already has the `game_end` row in hand at `eval/replay_walk.py:394-396`
before it seeds, so the check is four lines there: if the option is set and
`retired_levers_stamped_off(game_end.substrate_flags if game_end is not None else None)` is non-empty,
`_violate(...)`. `WalkViolation` (`:224-240`) has no field for a lever list; add one with a default
rather than overloading `actual`, so the consumer's message can name the levers the way
`audits/workflows/extract_gameplay_facts.py:2169-2180` names them. Then flip the flag in
`eval/funnel.py:240` — that one config object is shared by both funnel walks, so the two consumers
the close audit named are covered by a single line. Leave `eval/validity.py:478` and
`eval/leak_scan.py:823` alone: widening the no-check factory profile is exactly the behaviour change
the module's locked decision forbids. The planted case follows the forged-winner pattern already in
`tests/eval/test_replay_walk.py:468-472` — rewrite the `game_over` row's `substrate_flags`, then drain
under both profiles.

Step 6 — the recorder sweep, last, because it is the one with a suite pinning it. Work from the
verifier's own line list rather than a blanket substitution, and re-run
`git grep -nI "baseline-6\|baseline 6" scripts/record_ml_corpus.sh` after each pass until only `:9`,
`:27`, `:83` and `:127` remain. Change the five assertions in `tests/scripts/test_record_ml_corpus.py`
in the same commit as the strings they pin. Where a line is an operator-facing `echo`, prefer deleting
the label over correcting it: `:913` becomes "resolves to the locked map ($REQUIRED_PROMPT_VERSIONS)"
and the four version strings speak for themselves. Do NOT touch the `v4` version strings themselves —
the prompt-set task owns those, and this sweep is about the baseline label and the lever count.
Finally, re-read the whole file for the lever count and derive the word "twenty-one" from
`len(_RETIRED_ALWAYS_ON_LEVERS)` in the PR's evidence rather than from this contract.

## Public types this task introduces
- `check_doc_facts.check_front_door_budgets`
- `check_doc_facts.check_corpus_disclosures`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import engine.tick"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import training.rewards"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import agents.strategic.prompts.loader"`

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
Open a PR from branch `phase-21-prose-truth` with a title like `task 21.11: prose that is true at head: the f2 class swept, the corpus disclosures re-derived, four ungated claims given teeth`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing F2, F3, F4 and the routed walker item — audits/audit-phase-20-close.md:115-121 (F2, the two stale narrations "whose own committed pins already disagree with them"), :125-152 (F3, the three front-door budgets and the ruling that "a budget nothing can fail is prose — Craft rule 2 applied to a documentation target"), :154-177 (F4, whose *prose* half was corrected in the close PR and whose *gate-coverage* half — "adding `audits/README.md` to `_LADDER_TIP_DOCUMENTS` … wants its own perturbation case" — is what lands here), :408 (`eval/replay_walk.py` performs no substrate check; "the one-line fix is the now-public `orchestrator.replay.retired_levers_stamped_off`", routed with 20.37's merge record `a9952d29`). A-15 [ADJUSTED, P1] — audits/review-2026-08-26/A/collated-findings.md:1912-1990 (the finding, its four measurements and the verifier's independent re-run, including the root cause `git diff 2df33ca4 efcd43b8 -- replays/ml_corpus/README.md` → one word changed, "baseline-6 substrate" → "baseline-7 substrate", with every number left as recorded on the baseline-6 bytes; and the verifier's correction that *nothing* in the 4p pair matches, since README's `(S4, C4)` impostor cells are `(8/39, 5/40)` and HEAD's S4 `5/40` merely coincides with the README's C4 cell). B-47 [ADJUSTED, P3] — audits/review-2026-08-26/B/collated-findings.md:2493-2520, whose verifier keeps ONLY the comment half: `BAKEOFF_BASELINE_ID` "is SPECIFIED as correct, not stale", audits/audit-phase-20-baseline-7.md §10.2 says it "names the baseline the bake-off is GROUNDED on, not the substrate baseline", and moving it is an explicitly routed item of the ML re-ground — cited here as the EVIDENCE for a routing, not as work: assembly moved B-47's comment block to Task 21.17 so it travels with the constant, and this contract's F2 slot is `docs/history.md`'s stale "## In progress: phase 20" heading (`:160`, `:170`) instead. A second F2-class site, found at the #403 merge: `docs/glossary.md:66` reads "Thirteen have graduated and one live toggle remains" where the live registry at HEAD gives TWENTY-ONE graduated and THREE live toggles (`impostor_roll_call`, `last_seen_from_sightings`, `vent_single_mint` — the latter two added by 21.4 #403 and 21.5 #404) — swept here with the same treatment, and the corrected sentence must state the CURRENT truth on both halves, not only the graduated count. B-50 [ADJUSTED, P2] — audits/review-2026-08-26/B/collated-findings.md:2639-2700, with both verifier corrections binding: the stale-site count is ~25 not 29 (`:9`, `:27`, `:83`, `:127` are correct historical references) and `tests/scripts/test_record_ml_corpus.py` re-asserts five of the stale operator strings verbatim, so the sweep is not a free `sed` pass. **Anchors re-verified at HEAD `4002f19b`:** the orchestrator/game.py F2 site is CLOSED by 21.1 (#406) and is no longer owned here: the five-paragraph changelog is gone, replaced by an intent-first block at `:365-377` whose archive sentence (`:372-374`, "The committed sample sets stamp v4 and resolve through tests/fixtures/prompt_archive/qwen3_6_27b_v4/ until the adopting record retires that entry") is TRUE at HEAD — the directory exists on disk and `tests/meetings/test_prompt_byte_golden.py:183` `ARCHIVED_PROMPT_VERSION_SETS` holds the `qwen3_6_27b_v4` entry with the bump-in-flight window OPEN (live registry v5, committed sets v4); frontend/src/lib/bodies.test.ts:9 still reads "0 phantom frames vs 1,182 of 1,769 on `9p2i`" while its two cases at `:447` and `:465` assert `frames: 1217` with `phantomFrames: 0` and `phantomFrames: 668, phantomBodies: 1371`; eval/watchability.py:908-913 says `BAKEOFF_BASELINE_ID` "still reads ``baseline-5``" against training/bakeoff/harness.py:181 `BAKEOFF_BASELINE_ID: Final[str] = "baseline-6"`, with `_DEFAULT_BASELINE_ID: Final[str] = "baseline-7"` on the next line at `:914`; scripts/check_doc_facts.py:237-242 `_LADDER_TIP_DOCUMENTS` is `(_README, _GLOSSARY, _HISTORY, _READING_GUIDE)` and audits/README.md:265 (one "ladder tip" phrase in the file, naming baseline 7) is outside it, while `grep -n word scripts/check_doc_facts.py` still finds no budget of any kind; `wc -w README.md docs/reading-guide.md docs/ml-program.md docs/lessons.md` reads 3,487 / 1,303 / 2,063 / 1,491; `grep -c "baseline-6\|baseline 6" scripts/record_ml_corpus.sh` is 28 at HEAD after 21.10's rewrite (24 stale + 4 historical), against the PIN BLOCK now at `:112-137` ("the baseline-7 substrate … the qwen3_6_27b prompt set at v4 … the twenty-one retired always-on levers", the v4 and one-toggle clauses themselves now stale) and `:167` `REQUIRED_PROMPT_VERSIONS`, and `uv run python -c "from orchestrator.replay import SUBSTRATE_FLAG_KEYS,_RETIRED_ALWAYS_ON_LEVERS,TOGGLEABLE_SUBSTRATE_FLAG_KEYS as T; print(len(SUBSTRATE_FLAG_KEYS), len(_RETIRED_ALWAYS_ON_LEVERS), T)"` prints `24 21 ('impostor_roll_call', 'last_seen_from_sightings', 'vent_single_mint')`; replays/ml_corpus/README.md:104-126 is the disclosures header (`:107` "Every number below was recomputed from the committed bytes", `:112` "at the same baseline-7 substrate"), `:131` "707/707", `:140` "986", `:255-277` item 8, `:279-291` item 9; tests/eval/test_deduction_metrics.py:498 and :535 are the two docstrings that quote the stale figures beside asserts that pin the current ones; eval/replay_walk.py:214-227 `WalkViolationKind`, :235-253 `WalkViolation`, :257-294 `ReplayWalkConfig` (whose `verify_action_dispositions` field 21.3 added at `:280` — no collision with the new field name), :85-120 the PROFILE TABLE the new option must join, :407-420 (`read_all_entries`, then the `game_end` row is already in hand) and eval/funnel.py:240-247 `_WALK_CONFIG`, the profile shared by BOTH funnel walks — UNMOVED, the DoD's `:240` still exact; orchestrator/replay.py:834-869 `substrate_stamp_mismatches`, :778 `retired_levers_stamped_off` (now zero production callers) and :1373 `read_substrate_flags`, with audits/workflows/extract_gameplay_facts.py:2170-2185 the precedent refusal.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
