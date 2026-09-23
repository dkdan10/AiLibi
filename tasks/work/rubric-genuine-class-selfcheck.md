# Read the genuine class off the record so the served rubric scores again

**Status:** done

## Outcome

The committed 9p2i interestingness rubric
(`replays/samples/9p2i/results-rubric-score.json`) and its two lab copies
(`experiments/lab/results-rubric-score.json`,
`experiments/lab/results-rubric-geomean.json`) read 0.0 on all 50 games. The
cause is one of the gameplay extractor's seventeen self-checks,
`re-derived genuine-class == shipped compute_genuine_class_conversion
(supplied 1/0, converted 1/0): FAIL`, because
`experiments/lab/rubric_score.py::_facts_integrity_ok` floors every game on any
failing self-check. `/eval/rubric`, the ReplayPicker highlights and
`scripts/build_demo_bundle.py` all serve that file, so merging the baseline-9
record as it stood would publish 0/100 on every 9-player demo card.

This card decides which side of that check is wrong, fixes it there, keeps the
check a gate that fails on the defect it exists for, and regenerates the three
derived files on the SAME baseline-9 bytes. No recording byte moves. After it,
every self-check passes and the rubric floors only per game, by its own design.

It lands into `work/process-rerecord` (PR #477) before that record merges, by
the owner's delegation of 2026-09-23, verbatim: "Go with your recommendation.
Merge when you assess it is ready. Then open up the next re-ground card after."
The recommendation was to fix the self-check and regenerate the highlights on
the same bytes before merging, so the demo never publishes 0/100 badges.

## Evidence

- The record routed this as item 2 of
  [`audits/audit-2026-09-22-process-rerecord.md`](../../audits/audit-2026-09-22-process-rerecord.md)
  §7.1 and described it in §2.1b. The previous record routed the same check as
  item (a) of FINDING 2 in
  [`audits/audit-phase-21-rerecord.md`](../../audits/audit-phase-21-rerecord.md),
  where it read `supplied 1/0, converted 0/0` on the baseline-8 bytes.
- The one-home definition is
  `eval/vote_correctness.py::GenuineClassConversionReport` and
  `genuine_class_subjects`. A (meeting, impostor) pair is supplied when the
  meeting's RECORDED flags carry a non-endpoint, non-proxy `alibi_vs_sighting`
  naming that impostor. Task 21.7 (`97940156`, #400) moved the definition onto
  the record because a transcript-only re-run misses the recording-time
  detector's trigger kind and three private grounding channels.
- Before 21.7, `genuine_class_subjects` ran
  `detect_contradictions(meeting.transcript, roster=ballot voters)`
  (`git show 97940156^:eval/vote_correctness.py`). The extractor's
  `_genuine_subjects` ran that same call and was never moved, which makes it an
  era-frozen replica. The docstring it kept still claimed it was "exactly the
  compute_genuine_class_conversion definition". This replica had drifted once
  before, missing the 10.10 proxy-intra-turn band.
- `tests/eval/test_recorded_flag_census.py` sweeps only `eval/` and
  `training/`. It exempts the extractor by location because the extractor's
  re-derivation spine is a counterfactual on purpose. The genuine class,
  though, is the one place the extractor claims to equal the shipped gate.
- Consumers of the regenerated files: `api/routes/eval.py` (`/eval/rubric`) via
  `api/replay_loader.py::_rubric_is_stale`; `frontend/src/components/HighlightCard.tsx`
  and `ReplayPicker.tsx`; `scripts/build_demo_bundle.py::_trimmed_rubric`;
  `tests/api/test_sets.py`; and the lab-parity pin
  `tests/eval/test_watchability.py::test_historical_15_2_geomean_parity_frozen_pin_on_9p2i`.
  Nothing reads the extractor's genuine-class facts except the extractor
  itself (`git grep` on `genuine_subjects`, `is_genuine_class` and
  `genuine_class_crosscheck` outside it finds only historical Markdown).

## Acceptance

- [x] **The wrong side is named with evidence.** Folded three ways over each
  set, the shipped fold and the record fold agree and the replica is the one
  that differs. Baseline 9: shipped 0/0, record 0/0, replica 1/1. The replica's
  only impostor pair is seed 7 meeting 0, p-2, whom that meeting ejected. Its
  genuine subject set differs from the record's on 20 of 145 meetings (27 rows
  against 4). Baseline 8 (`39a568c6`): shipped 0/0, record 0/0, replica 1/0
  (seed 38 meeting 0, p-3, not ejected), with 19 of 151 meetings differing
  (19 rows against 7). That is the phase-21 audit's line. The shipped function
  is not the wrong side, so `eval/vote_correctness.py` and every published
  figure it feeds are untouched.
- [x] **The extractor reads the record by the one-home rule.** The replica
  `_genuine_subjects` is deleted, along with its two now-unused band imports.
  The walk passes each raw recorded row through the loader's own mapping
  (`eval.balance_eval._trigger_kind_index` and `_meeting_report_from_entry`)
  into `eval.vote_correctness.genuine_class_subjects`, and hands the result to
  `_analyze_meeting` as `genuine_subjects`. Planted:
  `test_a_transcript_rerun_in_place_of_the_record_fails_the_check` substitutes
  the deleted replica. The extractor then prints exactly
  `(supplied 1/0, converted 1/0): FAIL`, raises a blocking
  `GENUINE-CROSSCHECK` finding, `_facts_integrity_ok` returns False, and all
  50 of 50 rubric rows score 0.0. At head the same line reads
  `(supplied 0/0, converted 0/0): OK`.
- [x] **The check stays a real gate, and fails on one pair.**
  `test_one_pair_of_disagreement_fails_the_check_by_exactly_that_pair` adds one
  supplied-and-converted pair to the shipped side. It FAILs by exactly (1, 1)
  whatever bytes are committed. Red before, green after: on the pre-card
  extractor all 3 tests in
  `tests/experiments/test_gameplay_facts_genuine_class.py` fail, by different
  routes. One is the FAIL line, one an AttributeError, since no one-home seam
  exists to plant into. The third is a coincidental match: the replica's 1/1
  equals the perturbed 0+1/0+1. With the fix, 3 of 3 pass.
- [x] **Every self-check passes.** 17 lines, 0 containing FAIL: 16 read OK and
  the 17th is the informational effective-deflection line
  (`W2 fixture match: True`). Before the fix, 15 read OK and 1 read FAIL. Only
  genuine-class fields move in the facts JSON (56 JSON paths, all genuine-class
  or self-check).
- [x] **The rubric is regenerated on the same bytes, deterministically.** The
  rubric step ran alone, twice, into separate temp dirs, and the three files
  are byte-identical across runs (sha256 `b1ba0741…` set rubric, `9fabd9ad…`
  lab rubric, `f53ea38b…` lab geomean). The rubric's provenance key is the
  set's manifest sha, `27646d67`, unchanged. Before: 50 of 50 games at 0.0
  (min, median and max all 0.0). After: 5 of 50 at 0.0, min 0.0, median 50.7,
  max 83.5, mean 50.54. All five zeros (seeds 6, 12, 13, 38 and 39) are the
  rubric's own per-game railroad floor: each ejected one crewmate, and none
  holds a friendly-fire kill.
- [x] **Consumers agree, and their pins bite on the old state.**
  `test_the_served_rubric_is_fresh_and_floors_only_per_game` replaces the pin
  that asserted all 50 served scores floored. It keeps `stale is False` (the
  producer's `_set_manifest_sha` equals the loader's `_manifest_git_sha`) and
  pins the zero set to {6, 12, 13, 38, 39}. On the pre-card rubric it is red
  (all 50 seeds zeroed).
  The watchability parity pin drops its floor/score exclusion: all 11 columns
  match the lab on all 50 rows, and the lab and module agree on mean 50.54,
  median 50.7 and the floored set. On the pre-card rubric it is red at
  seed 0 `floor_multiplier` (1.0 against 0.0).
  `scripts/build_demo_bundle.py` bakes 4 non-zero 9p2i rows for the featured
  seeds (23: 68.7, 29: 67.6, 0: 55.5, 2: 1.3); the pre-card file carried 0.0
  for all four. Vitest 558 of 558 passed, including `HighlightCard.test.tsx`.
  Playwright passed 13 with 3 skipped, both pre-existing.
- [x] **Freeze held.** Against `39a568c6`, `git diff --stat` over `engine`,
  `agents` (with `agents/strategic/prompts/`), `meetings`, `observation`,
  `orchestrator`, `training` and `llm` is empty; `eval/` is untouched. No
  recording, ML fit, artifact or training file changes.

## Constraints

- Stacked on `work/process-rerecord` at `87c6abfe`. It lands before that record
  merges and changes nothing the record measured. It is a derived-view
  regeneration: no re-record, no re-score of history and no live provider call.
  No step asked for `FEATHERLESS_API_KEY`, and this worktree holds no `.env`.
- The record's freeze is inherited: `engine/`, `agents/`, `meetings/`,
  `observation/`, `orchestrator/` and `agents/strategic/prompts/` stay
  byte-identical to `39a568c6`. No ML fit, artifact or training file changes.
  Role-correct ejection gates nothing.
- `eval/vote_correctness.py` is protected by `scripts/check_doc_facts.py`
  (`:36-39`) and feeds the front door. It could change only after a STOP-and-
  report on every published figure it would move. It turned out to be the
  right side, so it is untouched.
- Only the rubric step of `scripts/refresh_samples.sh` (`:1049-1066`) ran. The
  whole refresh script, `scripts/record_ml_corpus.sh` and a live
  `scripts/run_tournament.py` did not.
- The phase-21 audit's routed item (b) is not this card's. That item is the
  scorer's all-or-nothing floor, where one failing self-check zeroes a whole
  set. It is left as routed; see Results.

## Expected scope

- `audits/workflows/extract_gameplay_facts.py`: delete the replica, wire the
  recorded genuine class through the walk, and correct the prose that described
  the re-run as the definition or as a no-op.
- `tests/experiments/test_gameplay_facts_genuine_class.py` (new): the green
  case and the two planted cases.
- `tests/api/test_sets.py` and `tests/eval/test_watchability.py`: the two pins
  that recorded the floored state, moved on purpose.
- The three derived rubric files, regenerated.
- `docs/artifacts.md`: the rows whose bytes moved.
- One dated line in the re-record audit's §7.1 item 2.
- `tasks/README.md` card inventory, and this card.

## Record impact

- **Derived files:** three regenerate:
  `replays/samples/9p2i/results-rubric-score.json`,
  `experiments/lab/results-rubric-score.json` and
  `experiments/lab/results-rubric-geomean.json`.
- **Unchanged:** no recording byte, manifest, eval report, process scorecard
  or front-door figure moves, and none of them reads the rubric. No re-record,
  no re-score of history.
- **Registry rows, recomputed from `git ls-files` with the change staged:**
  - `replays/samples/`: 107 files and 41,936,026 → 41,936,072 bytes
    (39.99 MiB). The row's "40 MB / 107 files" stands.
  - `audits/`: 26,633,740 → 26,632,967 tracked bytes, still 329 files. The
    row is restated.
  - `experiments/lab/` + `experiments/model_probe/`: 164 files and
    6,592,054 → 6,591,637 bytes (6.29 MiB). The row read "7.3 MB", a figure
    blob sizes never supported (6.28 MiB at `a250e3c1`, which wrote it), so it
    is restated as "6.3 MB / 164 files".
- **Publication:** `.github/workflows/pages.yml` rebuilds the demo bundle on
  every push to `main`, so this changes what the record's merge publishes:
  scored highlight cards instead of 0/100. That publication is inside the
  owner's delegation quoted above.

## Validation

- Diagnosis: the census snippet in Results, over `replays/samples/9p2i` and
  over the baseline-8 set restored with
  `git archive 39a568c6 replays/samples/9p2i`.
- The rubric step alone, twice, with `cmp` across the runs:
  `PYTHONPATH=. uv run python audits/workflows/extract_gameplay_facts.py >/dev/null && uv run python experiments/lab/rubric_score.py "$TMPDIR/ailibi-gameplay-facts-9p2i.json" --set-dir replays/samples/9p2i`.
- Targeted: `uv run pytest tests/experiments/test_gameplay_facts_genuine_class.py`,
  the two moved pins, and the same pins and new tests run against the pre-card
  extractor and rubric for the red half.
- `scripts/build_demo_bundle.py --out <tmp>`; `npm --prefix frontend test`;
  `cd frontend && npm run e2e`.
- `bash scripts/verify_samples.sh`; the four
  `scripts/build_sample_report.py --sample-dir <set> --check`;
  `scripts/publish_process_scorecard.py --check`; `scripts/check_doc_facts.py`;
  `scripts/validate_task_docs.py`; `scripts/generate_prompts.py --check`;
  `scripts/verify_ml_evidence.py` offline (never `--complete`); and
  `bash scripts/check.sh` with its exit code captured directly.

## Results

**Delivered.** The wrong side was the extractor's re-derivation. It now reads
the genuine class off the record through the one-home rule. All seventeen
self-checks pass, and the three derived rubric files are regenerated on the
unchanged baseline-9 bytes.

**References.** The design sections are:
- [`docs/architecture.md`](../../docs/architecture.md) "Packages": `eval/`
  folds recordings strictly, and `experiments/` writes separate artifacts.
- The same file's "Determinism and the substrate ladder": the recording is the
  reproducibility boundary, which is why the census is read off it.
- [`experiments/lab/report-rubric-design.md`](../../experiments/lab/report-rubric-design.md)
  §3 "Hard floors", the floor this card stops tripping wholesale.
- The Task-21.7 definition in `eval/vote_correctness.py`.

**Decision: the extractor was wrong, and not the shipped metric, and not the
check.** The census below shows the chain:

1. The shipped fold and the one-home rule over the record agree on both
   baselines.
2. The only computation that departs is the extractor's roster-only re-run.
3. That re-run is byte-for-byte the pre-21.7 shipped definition.

So the check did compare one quantity, as it claims, but its extractor side
went stale when 21.7 moved the definition. "Unlike units" would describe the
symptom, not the cause. The fix therefore makes the extractor import the rule
rather than re-implement it. The replica drifted twice, at 10.10 and at 21.7;
an import cannot.

**Why the gate is still real.** After the fix both sides share the classifier.
What the check now discriminates is any replica or re-derivation creeping back
into the extractor, which is the planted historical case. It also catches
divergence in the extractor's own walk: the meeting set it reaches, the
re-seeded roles and the eject outcome it joins. The one-pair perturbation shows
the comparison has no slack.

**Census command** (committed bytes only, count-only output; `PYTHONPATH=.`,
argument is a 9p2i-shaped set dir):

```python
import importlib, json, sys
from pathlib import Path
from engine.world import load_canonical_map
from eval.balance_eval import load_tournament_report
from eval.vote_correctness import compute_genuine_class_conversion as shipped_fold
from eval.vote_correctness import genuine_class_subjects as record_rule
from meetings.transcript import detect_contradictions as detect
from meetings.transcript import WEAK_REASON_ENDPOINT_TICK as E
from meetings.transcript import WEAK_REASON_PROXY_INTRA_TURN as P
from meetings.transcript import WEAK_REASON_RETARGETED_PROXY as R
from orchestrator.seeder import seed_initial_state
fx = importlib.import_module("audits.workflows.extract_gameplay_facts")
d = Path(sys.argv[1]); ro = json.loads((d / "roster.json").read_text()); m = load_canonical_map()
k = dict(num_players=int(ro["num_players"]), num_impostors=int(ro["num_impostors"]), tasks_per_crewmate=int(ro["tasks_per_crewmate"]))
roles = {int(p.stem.rsplit("-", 1)[1]): {i: q.role for i, q in seed_initial_state(seed=int(p.stem.rsplit("-", 1)[1]), game_map=m, **k).players.items()} for p in d.glob("replay-seed-*.jsonl")}
rep = load_tournament_report(d, roles_by_seed=roles, tasks_per_crewmate=k["tasks_per_crewmate"], game_map=m)
def rerun(mt):  # the pre-card extractor replica
    out = set()
    for f in detect(mt.transcript, roster=frozenset(b.voter for b in mt.ballots)):
        if f.kind == "alibi_vs_sighting" and not any(w in f.description for w in (E, R, P)):
            out.update(f.subjects)
    return frozenset(out)
n = differ = rows_rec = rows_re = spine = flags_rec = flags_spine = 0; pairs = {"record": [0, 0], "rerun": [0, 0]}
key = lambda fs: sorted((f.kind, tuple(f.subjects), f.description) for f in fs if f.kind != "vent_sighting")
for g in rep.games:
    for mt in g.meetings:
        a, b = record_rule(mt), rerun(mt); n += 1; differ += a != b; rows_rec += len(a); rows_re += len(b)
        for name, subj in (("record", a), ("rerun", b)):
            for s in subj:
                if g.roles[s] == "IMPOSTOR":
                    pairs[name][0] += 1; pairs[name][1] += mt.outcome == "EJECTED" and mt.ejected_player_id == s
        sp = detect(mt.transcript, roster=frozenset(b.voter for b in mt.ballots), trigger_kind=mt.trigger, vent_witness_records=fx._vent_records_from_recorded_flags(mt))
        spine += key(mt.contradictions) != key(sp); flags_rec += len(key(mt.contradictions)); flags_spine += len(key(sp))
s = shipped_fold(rep)
print(f"meetings {n}; genuine subject sets differ {differ}; rows record {rows_rec} rerun {rows_re}; "
      f"impostor pairs shipped {s.supplied}/{s.converted} record {pairs['record'][0]}/{pairs['record'][1]} "
      f"rerun {pairs['rerun'][0]}/{pairs['rerun'][1]}; spine differs {spine} (non-vent flags record {flags_rec} spine {flags_spine})")
```

The census output on each set:

- Baseline 9: meetings 145; genuine subject sets differ 20; rows record 4,
  re-run 27; impostor pairs shipped 0/0, record 0/0, re-run 1/1; spine differs
  22 (non-vent flags record 17, spine 41).
- Baseline 8: meetings 151; differ 19; rows 7 against 19; pairs 0/0, 0/0 and
  1/0; spine differs 25 (57 against 63).

The spine line is why the prose of `_rederive_meeting_contradictions` is
corrected. It claimed the re-run is "a byte-for-byte no-op" for an unchanged
detector, and on these bytes it differs from the record on 22 meetings.

**Moved pins, on purpose.**
- `test_the_served_rubric_is_fresh_but_every_score_is_floored` said it would
  have to be moved on the day the extractor was reconciled. It becomes
  `test_the_served_rubric_is_fresh_and_floors_only_per_game`.
- The watchability parity pin's comment said the floor/score exclusion "has to
  be dropped deliberately", and it is dropped.

**Gate**, run on the final tree with every exit code captured directly:

```
bash scripts/check.sh                                   EXIT 1 (the inherited red, below), 310 s
  ruff check . / ruff format --check .                  pass; 522 files formatted
  lint-imports                                          4 contracts kept, 0 broken
  scripts/validate_task_docs.py                         390 phase tasks + 390 prompts; 74 work cards
  scripts/generate_prompts.py --check                   pass
  mypy .                                                no issues in 493 source files
  pytest -n auto --dist loadfile                        8,246 passed, 20 skipped, 3 xfailed;
                                                        41 failed + 9 errors
frontend leg (set -e skips it after pytest; run alone:
  npm run lint && tsc:check && test && build)           EXIT 0; vitest 558/558
cd frontend && npm run e2e                              EXIT 0; 13 passed, 3 skipped
bash scripts/verify_samples.sh                          EXIT 0; 50 + 50 verified clean
scripts/build_sample_report.py --check, four sets       EXIT 0 each (samples 9p2i/4p1i,
                                                        ml_corpus 9p2i/4p1i)
scripts/publish_process_scorecard.py --check            EXIT 0, consistent
scripts/check_doc_facts.py                              EXIT 0
scripts/gen_frontend_types.py --check                   EXIT 0
scripts/verify_ml_evidence.py (offline, never --complete)  EXIT 1; 61 checks: OK 37, FAIL 12,
                                                        ABSENT 7, INFO 5 (identical to the
                                                        record's; the 12 are its §7.3 corpus
                                                        rows); replays/samples/, audits/ and
                                                        experiments/lab/ rows read OK
test_verify_ml_evidence.py registry-row + cheap-legs    2 passed
scripts/build_demo_bundle.py --out <tmp>                EXIT 0; 9p2i rubric rows non-zero
git diff --stat 39a568c6 -- engine agents meetings observation orchestrator training llm
                                                        empty (the freeze held)
git log 39a568c6..origin/main; 87c6abfe..origin/work/process-rerecord
                                                        both empty (neither base moved)
count-only key scan over the staged diff                11 files, 0 matches
```

**Red set.** The red set at this head is exactly the 50 default-tier ids the
re-record card lists under "Left red": 41 failed and 9 errors, with `comm -3`
against that list empty. This card turns no inherited red green, because none
of them reads the rubric. It adds no red. The two rubric pins that recorded the
floored state were green at the base and are green, moved, here. The three new
tests are the +3 in the passed count (8,243 at the record, 8,246 here).

**Limitations.**
- **`bash scripts/check.sh` does not pass.** It exits 1 on exactly the 50
  default-tier tests (41 failed + 9 errors) that the stacked base card
  `tasks/work/process-rerecord.md` lists under "Left red". This card inherits
  them, adds none and turns none green. None of them reads the rubric. Their
  causes, the fits' corpus and assertions the new bytes falsified, wait on the
  ML re-ground or an owner ruling, which the record's freeze keeps out of this
  card. By AGENTS.md a card is done only when
  `check.sh` passes, and `docs/workflow.md` defines Verified as the combined
  gate passing, so this card is not Verified. It is marked done under the same
  exception as its base card (its Limitations): on the coordinator's
  instruction, with every red named there. The owner's delegation of
  2026-09-23 covers when to merge, not this rule. So the owner decides whether
  this card stays done until the re-ground turns those 50 green, or goes back
  to active. After this item was added (card prose only), `check.sh` was
  re-run: EXIT 1, 8,246 passed, the same 41 failed + 9 errors, `comm -3`
  empty. The Gate block's script, frontend, e2e and bundle checks were re-run
  with the same results, and the rubric step, run once more, changed no
  committed byte.
- The planted historical case pins the baseline-9 line
  `(supplied 1/0, converted 1/0)`. A re-record that removes the replica's
  divergence has to re-anchor that exhibit on its own bytes. The one-pair
  perturbation does not depend on the bytes.
- On these bytes the shipped genuine pair is 0/0. The check therefore proves
  agreement on an empty class here, and the planted cases are what show it
  discriminates.
- The scorer's all-or-nothing integrity floor (phase-21 audit FINDING 2,
  routed (b)) is untouched. One failing self-check still zeroes a whole set
  with no partial signal in the served file. That remains a routed scorer bug
  in its own right.
- Delivery states: Implemented. It is not Verified: the acceptance checks
  pass, but the combined gate is red on the inherited 50 alone (first item).
  Independent review, owner review and merge are pending. Adoption does not
  apply.
