# Closed unexecuted: the gameplay-facts extractor was not widened to a declared era

**Status:** done

## Outcome

CLOSED UNEXECUTED on 2026-10-09, as superseded. That day the owner ruled, verbatim: "Merge both when verified and
retire the memo's D14 list" (decision memo 8.9). The ruling retires the list, G27 among it, and does not dispatch this
card's optional widening, which its Constraints left to the owner's word under D14. Its other job, the W0 -> W1 -> W2
rows, is on the retired list: the baselines memo's G27 row (Part 3.1) deletes the three Phase-10 fixtures and first
replaces the extractor's reading of them with one history line, and 8.9 lands the whole list as one retirement card.
Nothing below was built. The rest of this card is the contract as it stood at `225d2b77`, kept unchanged as the
record of what was proposed; the Results say what closed and what stays.

On 2026-10-06 the owner ruled on the shown set's rubric, verbatim: "Profile as recommended, decisive, and ship the
shelf". Rubric version 2 is the role-blind game-shape profile of the design memo
(`/Users/danielkeinan/.claude/projects/-Users-danielkeinan-projects-AiLibi/rubric-design-2026-10-06/rubric-design-memo.md`,
Part 2), published by `rubric-v2-profile` from the census carrier. Version 1 (R1-R7, the weighted geomean, the
scalar railroad floor and `experiments/lab/rubric_score.py --set-dir`) is retired for the `stage-b-r2` era and kept
as baseline-9 lab history. This card used to widen the extractor so that version 1 could be served for the era. That
purpose is gone; the refresh step, the viewer copy, the bundle and the served file's registry row are the profile
card's. The extractor still refuses the era by name, and three things still reach it:
- **The W fixtures.** Its W0 -> W1 -> W2 rows read `tests/fixtures/phase10/corrected_w{0,1,2}_baseline.json`, those
  files' only code consumer outside tests (the baselines memo's G27), so retiring them under D14 is coupled to it.
- **The facts path.** Its temp facts JSON is where the gameplay-data audit workflows start, and what the refresh
  script's rubric step ran until the profile card rewires that step to its own publisher. After the rewire the
  refresh script runs no extractor.
- **The referee's historical mode.** The frozen `historical_15_2` mode of `eval/watchability.py` has one
  cross-implementation check: the baseline-9 fixture, held to itself. A row for the shown era needs an extractor
  that reads the era.

This card exists for those consumers. It is optional and dispatches only if the owner rules so under D14. When it
is done:
- The extractor reads a recording under its own recorded config. It names, field by field, the settings it reads,
  and refuses any other by name before its first advance. It runs the recorded engine, reset, rebuttal and regroup.
- Version 1 is never served for `stage-b-r2`. The facts stay a temp file. The era's only committed output is one lab
  file, `experiments/lab/results-rubric-geomean.stage-b-r2.json`: the extractor's correctness witness against the
  frozen referee, re-derived on every run. It holds the era's per-game version-1 geomean reading (each game's score,
  floor multiplier and r1, r2, r3 and r7 sub-scores, the shape of `experiments/lab/results-rubric-geomean.json`), lab
  only and never served: the labelled-history option of the design memo's Part 3.
- The W0 -> W1 -> W2 rows are deleted with one history line. The extractor reads nothing under
  `tests/fixtures/phase10/`, so D14 can retire those fixtures without touching it.
- Baseline-9 history does not move, and the widened extractor still reproduces it from its own bytes. Nothing ships.

## Evidence

Every `path:line` is at `76270d6c` (labelled as such) and is re-anchored by its symbol at dispatch. The extractor
and its two refusal tests, the lab scorer, the refresh script, the cooldown and arm gates, `engine/`, `agents/`,
`meetings/`, `orchestrator/`, every `eval/` module the extractor imports and `replays/samples/9p2i` are
byte-identical between `59bbd1be`, where this card was first written, and `76270d6c` (`git diff --stat` over those
paths prints nothing). Every count is count-only, keyed by (set, meeting), re-measured at `76270d6c` by the scratch
probes named below (about 3 s each, not committed), and re-measured at dispatch; the dispatch figure governs. No
prompt, transcript or seed-band prefix was printed.

**What the ruling moved off this card.** The design memo's reproduction script (`rubric-v2-repro.py`, beside the
memo; run from the repository root with `.venv/bin/python`) reads the census carrier, not the extractor. It exited
0 in 6.1 s at `76270d6c`. Tripwire T1 under the decisive quantifier trips seed 26, meeting index 2, only; "every"
trips none and "any" trips two (seeds 26 and 41). The ejecting ballots are 282 `supported` and 2 `off_target`.
`uv run python scripts/publish_gameplay_census.py --check` reports the census pages consistent with the committed
recordings. Neither needs this card. The memo's Part 3 splits the held card in two: this one (its Card A) and
`rubric-v2-profile` (its Card B).

**Who reaches the extractor** (at `76270d6c`):
- `scripts/refresh_samples.sh:1123-1166` runs it only inside the rubric step, and skips the era with one named line
  (`:1137-1138`; dry run `:585-589`). The profile card rewires that step.
- `_cross_era_trajectory` (`audits/workflows/extract_gameplay_facts.py:673-779`) reads the three fixtures
  (`:698-703`). It is called at `:3520`, carried into the facts at `:4548` and quoted by a self-check line at
  `:3822-3828`. A missing fixture reads as `{"present": False}` (`:702-703`), so deleting the fixtures first would
  degrade the rows silently. `git grep cross_era` finds no reader outside the extractor. On the era (under the
  widening below) the block compares the shown set's live row with `corrected_w2_baseline.json`, a frozen
  baseline-9 anchor (`tests/eval/test_gate_spec_metrics.py:111-119`): effective deflection False, genuine class
  True. It compares two eras and describes neither.
- `tests/eval/test_watchability.py:130-168` holds the baseline-9 geomean fixture to itself; its docstring says the
  extractor "does not read the promoted era" (`:139-140`). The audit workflows start from the extractor
  (`audits/workflows/gameplay-data-audit-v2.workflow.js:603`, `:827-828`; `forward-redesign.workflow.js:336-337`);
  they are dated prompt text and stay as written. Beyond those, three `tests/experiments/test_gameplay_facts_*.py`
  modules, `tests/eval/test_recorded_arm_readers.py:1660-1699` and comment lines in four other tests name it. No
  production surface reads it for the era.

**The refusal, and what it hides.** `refuse_experiment_settings` (`:184-206`, called at `:2152`) exits at the first
seed with any setting off its default, which on the shown set is seed 0. The extractor seeds at `:2135-2141`,
advances at `:2265` and applies meetings at `:2781-2786`, none of them with the recording's settings. Probe 1
imports the module and replaces the refusal with a no-op. The run records 1,885 invariant failures (1,801 tick-hash,
81 post-meeting-hash, 3 other), and 3 of its 16 self-checks fail.

**The minimal widening, measured.** Probe 2 wraps the module's three engine bindings. The seeding and every advance
take `engine_arguments(recorded_experiment_config(entries))` (`orchestrator/experiment_config.py:338-369`). Every
applied meeting takes the same values plus the recorded `meeting_reset`. On the shown set it reads 16 of 16
self-checks OK and no invariant failure. Its findings:
- 44 cross-room rejections (`REJ`, high) and 99 dead-actor rejections (`REJ`, informational), the kinds the walk
  always reports;
- 114 `OPTIN` and 3 `TERM` high findings, one per meeting (117). At authoring on `59bbd1be`, on identical bytes,
  each was traced to the meeting's last reply, the one `meetings.rebuttal.select_bounded_rebuttal` re-derives from
  the turns before it.

Probe 3 reads the same recordings and probe 2's facts:
- The regroup: 67 of 117 meetings carry derived regroup ticks. The re-derived flags are 78 with or without them, and
  no meeting's flags differ.
- The prompt classes: 120 opening, 420 opt-in, 271 reply and 691 vote calls, none unclassified. Every vote call
  parses at least one suspicion row (3,101 in all). The composite `v8` prompt stamps never reach the extractor,
  which reads no prompt-version field.
- Version 1's interestingness reading of the era (the served file's shape), for the lab only (never served, never
  committed): 50 rows, mean 25.1, median 18.4, top 86.2, and 16 games at 0, all from the railroad floor. Win shapes:
  impostor-win 24, eject-decided 13, stopwatch-some-eject 10, stopwatch-no-eject 3. The geomean witness this card
  does commit is a second per-game version-1 reading of the era (Acceptance, the witness item).
- The geomean body equals `compute_game_score(..., historical_15_2=True)` (`eval/watchability.py:2265`) on all 50
  games and all eleven `_PARITY_KEYS` (`tests/eval/test_watchability.py:65-77`), to 1e-6.

**Baseline 9 from its own bytes.** Probe 4 runs on a `git archive d41c9006 replays/samples/9p2i` export. The export
carries the retired served file (blob `4879637e`) at the very path the scorer wrote, so it was moved aside first.
The extractor exits 0, and none of its 17 self-check lines fails. Four values equal the retired file's four keys:
`interestingness(facts)`, `_set_manifest_sha` (`27646d67`), `recording_fingerprint` and the seedset. The JSON
rebuilt from them is byte-identical to the retired file. `geomean_validation(facts)` equals the frozen fixture's
body. The scorer reads no `cross_era_trajectory` key, so the reproduction does not depend on the rows this card
deletes. Nor does it need `regen_for_set` or `--set-dir` (`experiments/lab/rubric_score.py:1337`, `:1381`), which
the profile card deletes.

**The arms, and what each asks of the extraction.**

| recorded setting | layer | what the extractor must do |
|---|---|---|
| `redistribution_policy` (default in the era) | engine | take it from the helper at every advance and every meeting, as every reader does |
| `kill_cooldown_ticks` 6 | engine | take it from the helper at the seeding, every advance and every meeting; without it the hashes diverge |
| `vent_witness_rule` physical | engine | take it from the helper; no extractor fact reads a witness event (vent channels are rebuilt from recorded flags, `:437-521`) |
| `meeting_reset` hub_with_grace | orchestrator | pass it to every applied meeting; pass the derived regroup ticks to the contradiction re-derivation, as the live manager does (`meetings/manager.py:1476-1484`) |
| `bounded_rebuttal_version` 1 | meeting | accept exactly the one trailing reply the selector picks (`walk_chain`, `meetings/transcript.py:487`); today it reads as 117 protocol findings |
| `report_body_handle_version` 1 | orchestrator | nothing: it changes only a report's trigger text, which no fact reads |
| `ballot_kill_row_version` 1, `impostor_ballot_version` 1 | meeting | prompt composition only; the slot classifier and the suspicion-graph parse (`:572-634`) must keep classifying |
| `vent_exit_policy` look_and_wait, `vent_entry_policy` own_fresh_kill | tactical | nothing: they reach the walk as recorded actions, and no policy is re-run |
| `route_lines_version` (`route-lines-field`'s field, under the name it merges with; not in the shown era) | meeting | prompt composition only; the vote-slot classifier and the suspicion-graph parse must classify a ballot prompt that carries the routes block |

The regroup ticks and the prompt classification read as no-ops on these bytes (probe 3). They are kept because the
live game has them. The route-lines row has no committed era to measure on; it is planted on a scripted route-lines
recording (Acceptance, the first item and the arm item).

**What goes false when the extractor reads the era** (at `76270d6c`, outside dated history):
- The refusal's own tests and docstrings: `tests/experiments/test_gameplay_facts_refuses_experiments.py` (whole);
  `tests/experiments/test_gameplay_facts_genuine_class.py:18-21`, `:100-109`;
  `tests/eval/test_recorded_arm_readers.py:1660-1661`, `:1692-1699` (the "extractor" copy case);
  `tests/eval/test_watchability.py:139-140`.
- Lines on surfaces the profile card rewrites: `api/routes/eval.py:235-236`;
  `frontend/src/components/ReplayPicker.tsx:19-21`; `frontend/e2e/evidence-journey.ts:58-59`;
  `scripts/refresh_samples.sh:586`, `:1133-1138`; `tests/api/test_sets.py:331-332`, `:456`;
  `tests/scripts/test_build_demo_bundle.py:313-314`; `tests/scripts/test_refresh_samples.py:2239`. Whatever of
  these survives the profile card's merge is fixed here.
- The lab report's run line (`experiments/lab/report-rubric-interestingness.md:65-69`) names `--set-dir` and the
  unkeyed outputs. The profile card fixes the `--set-dir` half, and this card the output name.

**The alternatives weighed.**
- **(a) Widen the extractor: contracted, optional.** The measured cost is three threaded calls, the reset, the
  rebuttal acceptance and the regroup ticks. It buys an extractor the audit workflows can point at the shown era,
  an era-keyed parity row for the frozen referee, and a baseline-9 reproduction that stays runnable.
- **(b) Drop it.** This card closes as superseded with one history line, and D14's G27 card deletes
  `_cross_era_trajectory` itself. The era-keyed parity row is never built.
- **Not taken: moving the extractor onto `eval/replay_walk.py`.** That would put the threading in one place, but
  moving a 4,670-line fold is a refactor with its own byte-parity contract. The helper threading reaches the same
  engine values and is pinned by the same scan. The held card's options for serving version 1 (the referee's facts,
  an era-neutral facts source) fell with version 1.

## Acceptance

- [x] **Closed unexecuted on 2026-10-09, as superseded; nothing was built.** The extractor still refuses the shown
  era by name (`refuse_experiment_settings`, `audits/workflows/extract_gameplay_facts.py:184`, called at `:2152`, at
  `225d2b77`). No read list, threading, `--sample-dir`, lab witness, registry row or test was added or changed. Its
  W0 -> W1 -> W2 rows (`_cross_era_trajectory`, `:673`, reading `tests/fixtures/phase10/` at `:698-703`) are left to
  the D14 retirement card, under the baselines memo's G27 row.
  - Mechanism: at the closing commit, which lands before the D14 retirement card merges, a count-only `git grep -c`
    for the two `def` lines in the extractor prints 2, and `git ls-files` for the era's witness file prints nothing
    (both commands are in Results, as readings at that commit; once the retirement merges, the grep prints 1).
    `scripts/validate_task_docs.py` (`:160-164`) accepts a `done` card only with every box checked and a non-empty
    `## Results`.
  - Planted: this card with one former item restored unchecked fails that validator with "done card has unchecked
    acceptance items", and with its Results emptied fails with "done card needs ## Results with evidence".
  - The fourteen items this card carried are in the repository history:
    `git show 225d2b77:tasks/work/rubric-extractor-era.md`.

## Constraints

**Status and dispatch.** The validator accepts three statuses, `ready`, `active` and `done`
(`scripts/validate_task_docs.py:45`, `_CARD_STATUSES`). Until 2026-10-09 this card was `ready`, meaning the contract
was complete, not that dispatch was authorized: it was to dispatch only on the owner's word under D14 (Part 4, D14,
the G27 item, of the baselines memo,
`/Users/danielkeinan/.claude/projects/-Users-danielkeinan-projects-AiLibi/baselines-2026-10-03/baselines-memo.md`),
and otherwise to close as superseded with one history line, D14's G27 card deleting `_cross_era_trajectory` itself.
The word was "retire the memo's D14 list" (decision memo 8.9), so it closed that way on 2026-10-09: `done`, with a
title and Results that say it closed unexecuted, the form the house used for `held-out-prefix-freeze-6` (`034cad1d`).

**Order.**
- It dispatches from a `main` that holds the merge of `rubric-v2-profile`. That card deletes `regen_for_set` and
  `--set-dir` (and holds the deletion with its own test), rewires the refresh step, and owns every served surface.
  This card writes none of those, and it branches from `main` only after that merge, so the order on
  `experiments/lab/rubric_score.py`, `report-rubric-interestingness.md` and `scripts/refresh_samples.sh` is fixed:
  the profile card first, then this card.
- The round-3 record also governs timing. `stage-b-record-r3` keeps the rubric cards undispatched until it merges
  ("Wave, order and ownership"), and its F-based gates cover `experiments/`, `scripts/`, `api/` and the `audits/`
  row of `docs/artifacts.md` it re-derives, all of which this card may write. So it never merges between that
  record's F and its merge; under the current record card it dispatches after the record merges, from a `main` that
  holds `rubric-v2-profile`, and only on the owner's D14 word.
- It does not depend on the census carrier; the kill and body victims and the end reason and final task count are
  the profile card's dependency on the cells card.

**Shared files, one writer at a time.**
- `experiments/lab/rubric_score.py`: the profile card first (its deletions; `_set_manifest_sha` stays, `:1309`),
  then this card (the witness naming in `main`). The scoring functions are untouched.
- `experiments/lab/report-rubric-interestingness.md`: the profile card first (the `--set-dir` half of the run line),
  then this card (the output name).
- These are the profile card's files: `scripts/refresh_samples.sh`, `api/routes/eval.py`,
  `frontend/src/components/ReplayPicker.tsx`, `frontend/e2e/evidence-journey.ts`, `tests/api/test_sets.py`,
  `tests/scripts/test_build_demo_bundle.py` and `tests/scripts/test_refresh_samples.py`. After that merge, this card
  edits a comment or copy line there only where the scan finds a surviving sentence, and names it in Results.
- `tests/orchestrator/test_experiment_arms.py` and `tests/eval/test_recorded_arm_readers.py`: `route-lines-field`
  first, then this card. `eval/recorded_settings.py` is that card's; this card only reads `READABLE_SETTINGS`.
- This card's alone: the extractor, its three `tests/experiments/` modules in Expected scope,
  `tests/eval/test_kill_cooldown_readers.py` and `tests/eval/test_watchability.py`. If D14's own card retires the
  baseline-9 pin, it lands before or after this one, never alongside.
- `docs/artifacts.md`: this card's two rows, last, in the merge order (`route-lines-field` and the census card also
  write the lab row, the idle-policy and record cards the `audits/` row). `tasks/README.md` and this card's Status
  line are the orchestrator's.
- Never written here: `eval/gameplay_census.py`, `scripts/publish_gameplay_census.py` and `docs/gameplay-census.*`
  (the census card's); `tests/fixtures/phase10/`, `tests/eval/test_gate_spec_metrics.py` and
  `eval/meeting_quality.py` (D14's); `audits/workflows/*.workflow.js` (dated prompt text).

**Out of scope.**
- Version 1's R-items, weights, floors and scoring functions. No history is re-scored, and version 1's lab results
  stay as history. The served rubric and every viewer surface are the profile card's.
- Any recorded byte: nothing under `replays/` moves, `replays/candidates/stage-b-r1/` included; the ladder tip
  stays at baseline 9. Engine, agent, meeting, orchestrator, LLM and training code; any DTO, schema, loader mapping
  or generated type.
- No new `AILIBI_*` lever, environment switch or experiment field, and no prompt registry or prompt version bump.
  The ML corpus's FROZEN line and every ML artifact stay put, and ML stays on hold (ruling 12).
- No live provider call, recorder run or held-out generator; the untracked `.env` is never read. Censuses are
  count-only, keyed by (set, meeting); no rendered prompt, transcript text or seed-band prefix is printed.

**House rules carried.** The engine stays a pure, deterministic tick, and nothing here touches it; replays stay
byte-identical in their recorded scope, and `agents/` never imports `engine/`. The extractor reads roles as engine
truth, offline and after the fact, and nothing agent-side may import it: `tests/test_firewall.py:381` bans `audits`
and `experiments` from `agents`, `llm`, `meetings` and `observation`, with one planted leg per banned name
(`:507-519`). Role-correctness stays a reported lab reading, never a gate. No module-level mutable state: the read
list and the reason table are immutable constants. Invalid input raises, with no silent fallback. Each new gate
carries a planted case that fails on its claimed defect. Every claim names its enforcing mechanism, and every number
is measured at the head that states it, with its command in Results. Guarantees are stated at the strength
delivered, and a live-tense sentence about old behaviour is fixed in the same pull request. Universal guarantees are
Hypothesis properties; any property that loads the map carries `settings(deadline=None)`. Every sourced constant has
a planted source-change case: the read list from `READABLE_SETTINGS`, the lab key from `eval/eras.py`, the stamp
from the MANIFEST, the slot literals from the era's templates. One writer per file.

**Publication.** Nothing ships. The bundle bakes no extractor output and no lab file, so `pages.yml` republishes an
identical demo. The pull request quotes the empty `diff -rq` between the base and head bundles. The served rubric
is the profile card's.

**Delivery.** The branch is `work/rubric-extractor-era`, delivered as one pull request into `main` and merged by
merge commit or fast-forward, never squash. Each commit body ends with `Card: tasks/work/rubric-extractor-era.md`,
immediately followed by the line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.

## Expected scope

- `audits/workflows/extract_gameplay_facts.py`: the read list and its reason table, the refusal, the threading, the
  reset, the rebuttal acceptance, the regroup ticks, `--sample-dir`, the W-row deletion and the docstring.
- `experiments/lab/rubric_score.py`: the witness naming in `main`, after the profile card's deletions. Its scoring is
  untouched.
- New committed output: `experiments/lab/results-rubric-geomean.stage-b-r2.json`.
- `experiments/lab/report-rubric-interestingness.md`: the run line only.
- Tests: the new `tests/experiments/test_gameplay_facts_era.py`;
  `tests/experiments/test_gameplay_facts_refuses_experiments.py` (rewritten in place for the read-list rule);
  `tests/experiments/test_gameplay_facts_genuine_class.py`; `tests/eval/test_recorded_arm_readers.py`;
  `tests/eval/test_kill_cooldown_readers.py`; `tests/eval/test_watchability.py`;
  `tests/orchestrator/test_experiment_arms.py`.
- `docs/artifacts.md`: two rows.
- Only where the scan finds a surviving sentence, comment or copy text only: `scripts/refresh_samples.sh`,
  `api/routes/eval.py`, `frontend/src/components/ReplayPicker.tsx`, `frontend/e2e/evidence-journey.ts`,
  `tests/api/test_sets.py`, `tests/scripts/test_build_demo_bundle.py`, `tests/scripts/test_refresh_samples.py`.
- This card's Results.

Directly necessary follow-through inside these files is permitted. Any other file belongs to another card or needs
the owner.

## Record impact

- **What is added.** No recorded byte is edited. One era-keyed lab file is added,
  `experiments/lab/results-rubric-geomean.stage-b-r2.json`: the era's per-game version-1 geomean reading, lab only
  and never served. The facts JSON stays a temp file. Nothing is added under `replays/`.
- **What is unchanged.** `bash scripts/verify_samples.sh` and the four `build_sample_report.py --check` runs
  recompute exactly what they did before. The census and scorecard pages do not move.
- **History.** The baseline-9 served rubric stays at `d41c9006`. The two unkeyed lab files stay byte-identical, and
  the frozen pin stays as D14 decides. The baseline-9 reproduction runs in scratch and writes nothing into the tree.
- **Behaviour.** The extractor, an offline audit tool, reads the era and no longer reads the Phase-10 fixtures. No
  agent, engine, meeting or tactical path changes, and no game plays out differently. No scorecard, census,
  evaluation or ML artifact moves.
- **What ships.** Nothing: the bundle diff is empty.
- **The next re-record.** When `replays/samples/9p2i` is next re-recorded or promoted, the witness is regenerated in
  the same change; its currency test goes red until it is.

## Validation

```
# development
uv run pytest tests/experiments/ tests/eval/test_watchability.py tests/eval/test_kill_cooldown_readers.py \
  tests/eval/test_recorded_arm_readers.py tests/orchestrator/test_experiment_arms.py tests/test_firewall.py -q
# the era, from the repository root ($0, no provider), run twice; the second leaves no diff
PYTHONPATH=. uv run python audits/workflows/extract_gameplay_facts.py --sample-dir replays/samples/9p2i >/dev/null
uv run python experiments/lab/rubric_score.py "${TMPDIR:-/tmp}/ailibi-gameplay-facts-9p2i.json"
git status --porcelain     # the stage-b-r2 witness only; nothing under replays/
git diff --exit-code d41c9006 -- experiments/lab/results-rubric-score.json experiments/lab/results-rubric-geomean.json
# baseline 9 from its own bytes, in scratch only
git archive -o <scratch>/b9.tar d41c9006 replays/samples/9p2i && tar -xf <scratch>/b9.tar -C <scratch>
rm <scratch>/replays/samples/9p2i/results-rubric-score.json
test ! -e <scratch>/replays/samples/9p2i/results-rubric-score.json
PYTHONPATH=. uv run python audits/workflows/extract_gameplay_facts.py \
  --sample-dir <scratch>/replays/samples/9p2i >/dev/null                        # exit 0
git show d41c9006:replays/samples/9p2i/results-rubric-score.json > <scratch>/retired.json
uv run python -c "import json, pathlib as p; from experiments.lab import rubric_score as r; \
from orchestrator.recording_fingerprint import recording_fingerprint as fp; d = p.Path('<scratch>/replays/samples/9p2i'); \
f = json.loads(p.Path('${TMPDIR:-/tmp}/ailibi-gameplay-facts-9p2i.json').read_text()); \
new = json.dumps({'seedset': f['seedset'], 'git_head': r._set_manifest_sha(d), 'source_fingerprint': fp(d), \
'interestingness': r.interestingness(f)}, indent=2); g = json.loads(p.Path('experiments/lab/results-rubric-geomean.json').read_text()); \
print(new == p.Path('<scratch>/retired.json').read_text(), all(g[k] == v for k, v in r.geomean_validation(f).items()))"
# True True; planted: with one per-game score changed in <scratch>/retired.json it prints False True
# the sentence scan: empty at the head; on 76270d6c it lists 17 lines in 10 files, plus 1 in the extractor
git grep -n -i -e "extractor does not read" -e "extractor refuses" -e "extractor reads only" \
  -e "read the promoted era" -e "refuses the shown" -e "fixture does not read" \
  -- . ':!audits' ':!tasks' ':!agent_prompts' ':!design'
git grep -n -i -e "extractor reads only" -e "extractor refuses" -- audits/workflows/extract_gameplay_facts.py
# nothing recorded moves; the gates
bash scripts/verify_samples.sh
uv run python scripts/build_sample_report.py --sample-dir <set> --check   # samples and ml_corpus, 9p2i and 4p1i
uv run python scripts/validate_task_docs.py
uv run python scripts/check_doc_facts.py
uv run python scripts/verify_ml_evidence.py        # offline; never --complete
uv run python scripts/build_demo_bundle.py --out <scratch>/before|after && diff -rq <scratch>/before <scratch>/after
bash scripts/check.sh                              # whole, in a clean worktree, real exit code quoted
```

Run `check.sh` to the end rather than stopping at the first failure, because `set -e` masks later gates.

## Results

### Closed unexecuted, 2026-10-09

**The ruling.** On 2026-10-09 the owner ruled, verbatim: "Merge both when verified and retire the memo's D14 list"
(`tasks/decision-2026-09-24-stage-b-wave.md:1601-1622`, section 8.9, at `335cbdc9`). Section 8.9 reads the list as
the baselines memo's Part 4 D14, with D14-T1 to T3, and the RETIRE rows of its Part 3.1, and lands the retirement as
one card whose merge waits for round 3's freeze to lift; its amendment of the same day, verbatim "Keep the
comparison records", takes only the round-1 item off the list. This card's Constraints left its dispatch to the
owner's word under D14 and named the other branch: close as superseded, with D14's G27 card deleting
`_cross_era_trajectory` itself. The word retires and does not widen, so the card closes on that branch, and nothing
in it ran. The closure lands before the retirement card merges, so this card is closed while that card deletes the
rows.

**What supersedes each of its three reasons.**
- The W fixtures. The baselines memo's row "RETIRE, after D6 and D14" (G27, Part 3.1) deletes the three
  `corrected_w*_baseline.json` files with their anchor tests, `WAVE2_GATE_SPEC` and `--baseline-out`, and first
  replaces the extractor's W0 -> W1 -> W2 rows with their one-line history. The profile card, the D6 card, left
  them, so at `225d2b77` they stand at `audits/workflows/extract_gameplay_facts.py:673`, `:698-703`, `:3520`,
  `:3827` and `:4548`. They are the D14 retirement card's: the extractor's reading of the fixtures retires with
  the fixtures.
- The facts path. Since the profile card (PR #504) rewired the refresh script's rubric step to its own publisher,
  the refresh script runs no extractor: `git grep -c extract_gameplay_facts -- scripts/refresh_samples.sh` prints
  nothing at `225d2b77`. The dated audit workflows still start from the extractor (Limitations).
- The referee's historical mode. The era-keyed parity row was option (a) in Evidence; this closure is option (b),
  which never builds it. The baseline-9 pin (`tests/eval/test_watchability.py:131`, held to itself) stays as it is
  unless the D14 retirement card's list retires it; this closure does not decide that.

**What did not move.** No line of the extractor, the lab scorer, its report, a test, `docs/artifacts.md` or any
recording moved, and no lab file was written. The sentences this card would have fixed stay true, because the
extractor still refuses the era: the refusal's own tests and the pin's docstring ("does not read the promoted era",
`tests/eval/test_watchability.py:139-140`). The profile card's open point 4 (`tasks/work/rubric-v2-profile.md:492`)
left this card's fate to the owner's D14 word; section 8.9 and its dated closure line answer it, and that done card
is not edited.

**Delivery states.** Implemented, verified and independently reviewed: not applicable, as no implementation exists.
Merged: the closure is a `docs:` commit on `main`, the AGENTS.md route for contract documents, checked by the
documentation lens alone (decision memo 8.7, item 4). Adopted: not applicable.

**Verification.** At the closing commit, which precedes the D14 retirement card's merge, each command below gives
the output beside it. These are readings at that commit, not standing claims: once the retirement merges,
`_cross_era_trajectory` and the three `tests/fixtures/phase10/corrected_w*_baseline.json` files are gone, the grep
prints `audits/workflows/extract_gameplay_facts.py:1`, `git ls-files tests/fixtures/phase10` no longer lists the three
files, and that card's Results name every path it deleted.

```sh
uv run python scripts/validate_task_docs.py      # passes; tasks/README.md carries the derived inventory sentence
uv run python scripts/check_doc_facts.py         # passes
git grep -c -E 'def (refuse_experiment_settings|_cross_era_trajectory)\(' -- audits/workflows/extract_gameplay_facts.py
                                                 # audits/workflows/extract_gameplay_facts.py:2
git ls-files -- experiments/lab/results-rubric-geomean.stage-b-r2.json   # prints nothing
```

Planted, the validator fails on this card with one former item restored unchecked, and again with this section
emptied, printing the two messages Acceptance quotes.

**Limitations.** The audit workflows that start from the extractor
(`audits/workflows/gameplay-data-audit-v2.workflow.js:603`) still cannot point it at the shown era; an audit of the
era starts from the census carrier (`eval/gameplay_census.py`), which reads it, or from a new card. If the D14
retirement card deleted the fixtures without the extractor's rows, the rows would read each missing file as
`{"present": False}` (`:702-703`), the silent degradation Evidence names, so the extractor half of the G27 row has
to land with the fixtures, in the same card.
