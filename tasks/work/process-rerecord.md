# Re-record the shown sample set once, after the substrate wave

**Status:** done

## Outcome

The committed recordings are re-recorded once, at HEAD, after
[the route claim](alibi-as-route.md),
[the grounded SKIP and the labelling guards](grounded-skip-and-guard-labels.md)
and [the weighing channel](ballot-weighing-channel.md) have merged. One window,
one record audit, no per-card re-record. The process scorecard is recomputed on
the new bytes beside a before column committed in advance, the spectator tour is
re-pointed at games the new bytes support, and the front door's derived prose,
floors and stamps are re-derived rather than relabelled. The card decides
nothing: it publishes cells, no bar and no verdict
([`audits/audit-phase-21-rerecord.md`](../../audits/audit-phase-21-rerecord.md),
"What this record is, and what it decides"), and role-correct ejection is
reported beside every cell and gates nothing.

## Evidence

[The direction of 2026-09-19](../direction-2026-09-19-process-over-outcome.md)
is this card's D7: one re-record, after the substrate cards land, at `$0`. Its
sections 8 and 9 are the yardstick and the plan this card measures into, and
section 12 records the owner's rulings. Every metric name below is defined by
[the process scorecard](process-scorecard.md) and by nothing else; this card
runs that tool, it does not redefine a row. `AGENTS.md:71-73` holds prompt-byte
and detector changes to an adopting record, which
[`docs/glossary.md`](../../docs/glossary.md)`:45-51` defines as the recording
that adopts a change rather than a label applied afterwards.

**What the committed recordings cost, from their own `llm_calls` rows** (games
are the `MANIFEST.md` row counts):

| set | games | calls | tokens | cost |
|---|---|---|---|---|
| `replays/samples/9p2i` | 50 | 1,740 | 8,134,860 | `$0.0000` |
| `replays/samples/4p1i` | 50 | 234 | 671,145 | `$0.0000` |
| `replays/ml_corpus/9p2i` | 150 | 5,039 | 23,804,796 | `$0.0000` |
| `replays/ml_corpus/4p1i` | 50 | 258 | 743,786 | `$0.0000` |
| **total** | **300** | **7,271** | **33,354,587** | **`$0.0000`** |

```
uv run python -c 'import glob,json,sys
for d in sys.argv[1:]:
  c=t=0; u=0.0
  for p in glob.glob(d+"/replay-seed-*.jsonl"):
   for r in map(json.loads,open(p)):
    for k in r.get("llm_calls") or []:
     c+=1; t+=k["input_tokens"]+k["output_tokens"]; u+=k["cost_usd"]
  print(d,c,t,u)' replays/samples/{9p2i,4p1i} replays/ml_corpus/{9p2i,4p1i}
```

**Wall time.** The last window recorded the same 300 games in 11h54m28s, inside
a committed 12h41m-23h46m bracket (that record's §2, as every bare § below is),
across about 15h48m elapsed; about 3h43m went dead to a provider-side `HTTP 529`
kill and a reaped background task (§2.6 of
[the adopting record](../../audits/audit-phase-21-adopting-record.md)), the
stall [`owner-decisions-2026-09-07.md`](../owner-decisions-2026-09-07.md)`:284`
sizes a margin from.

**The set list is not free to choose, which is why all four are re-recorded.**
`scripts/check_doc_facts.py:2221-2237` fails when the four sets it names at
`:297-302` disagree on the recording model, the prompt-set token
`<family>.<version>` or the substrate-flag stamp: "one provenance line cannot
describe two substrates". The wave bumps `orchestrator/game.py:397`
`PROMPT_VERSION_SETS`'s `qwen3_6_27b` entry off `v5` (`:424`), so a set left
behind stamps `qwen3_6_27b.v5` under a tree resolving the wave's versions and
the gate goes red. `scripts/record_ml_corpus.sh:166` pins
`REQUIRED_PROMPT_VERSIONS_BASE` to those four `v5` strings and refuses rows
recorded off it at the freeze (`:76-89`), so a corpus left behind can never be
extended or seed-repaired again. Including it costs about 8h and no dollars;
the alternative is editing an invariant gate to save flat-rate time.

**The owner's confirmation (2026-09-20).** The direction memo's decision D7
spoke of about four hours for one sample set; this card measured the project's
actual recording procedure and specifies every committed set under the ceilings
in Constraints. The coordinator put that difference to the owner, who confirmed
the ceilings explicitly on 2026-09-20, in the coordinator's session: 9,500 model
calls, 43,000,000 input and 2,200,000 output tokens, a 16 h recording wall
inside a 24 h window, at `$0.00` marginal. The confirmation covers the
recording spend only. Merging this card's pull request makes the new bytes the
shown baseline, and that merge stays the owner's.

## Acceptance

- [x] The before column is computed and committed **before the first seed
  stages**, on the still-committed bytes, with the tool
  [the process scorecard](process-scorecard.md) ships; D4 and D6 invalidate
  comparisons against these recordings, so a back-filled column would be a
  reconstruction. Cross-checks reproducible today: EJECT cited 526/527 and
  1,498/1,499; grounded SKIP **0 of 1,359** (342 + 1,017 over the two 9p2i
  sets); guard-redirected ballots 57/2,516 and 23/869; crew EJECTs off the
  suspicion argmax 81 of 1,270, of which 7 are role-correct.
- [x] Four sets are recorded in the leg order `samples/9p2i` to
  `ml_corpus/9p2i` to `samples/4p1i` to `ml_corpus/4p1i`, at the **same seeds
  as today**: samples `0-49`, `ml_corpus/9p2i` `1000-1149`, `ml_corpus/4p1i`
  `1000-1049`. Hosted models do not byte-reproduce fresh generation
  (`record_ml_corpus.sh:53-56`), so the comparison is per-set and distributional
  rather than per-seed; the seeds are held constant because both recorders drive
  locked ranges whose finalize asserts the exact set before freezing (`:33-34`,
  `:93`), and because the manufactured-contradiction exhibit at seed 41 needs a
  successor in the same set rather than a replacement band.
- [x] The recorders are used as they stand, the version pin being their only
  edit. `AILIBI_NUM_PLAYERS=9 AILIBI_NUM_IMPOSTORS=2 AILIBI_TASKS_PER_CREWMATE=2
  AILIBI_SAMPLE_DIR=replays/samples/9p2i` with its `AILIBI_MANIFEST` and
  `bash scripts/refresh_samples.sh --full --expect-levers ""`
  (`scripts/refresh_samples.sh:43-46`, `:56-64`) for the sample legs;
  `bash scripts/record_ml_corpus.sh --set <set> --expect-levers ""` for the
  corpus legs. Both compose `scripts/run_tournament.py`, untouched (`:36-38`);
  `REQUIRED_PROMPT_VERSIONS_BASE` (`:166`) advances to the wave's four version
  strings here and nowhere earlier.
- [x] Each leg previews with `--dry-run` and pastes its resolved configuration
  into the audit, a preflight refusal being reported rather than worked around;
  each set's prior bytes move aside and are preserved, because both recorders
  read a present in-range replay as already recorded; and
  `scripts/measure_baseline.py --honesty` runs on every leg's first completed
  seed before the rest queues, a raise being a STOP and a probe that folds a
  meeting-free game recorded VACUOUS and re-run (§0.2 rules 3 to 5).
- [x] Every leg is gated before the next begins and its range checkpoint-pushed:
  `scripts/validity_gate.py <set-dir> --expected-model Qwen/Qwen3.6-27B
  --require-zero-cost --expected-prompt-versions <the four KEY=VER pairs>` exits
  0 with all ten checks named individually (`scripts/validity_gate.py:12-16`),
  and `bash scripts/verify_samples.sh <set-dir>` reconstructs byte-identically
  in a **bare** shell with no `AILIBI_*` export. A partial record is not a
  baseline: if the window closes, the record stops at a set boundary and names
  the legs that exist. Every `(deadline_default)` row is a failed recording
  whose seed re-records, cause logged as it happens, five over 250 completed
  games last time (§5); no seed on disk re-records for any other reason.
- [x] The derived views are rebuilt, never hand-edited: four
  `tournament-eval-report.json` files through
  `scripts/build_sample_report.py --sample-dir <set>`; `splits.json` and the
  FROZEN line for the corpus sets by their recorder;
  `replays/samples/9p2i/results-rubric-score.json` by the rubric step at
  `refresh_samples.sh:1049-1066`, whose failure means the refresh is incomplete;
  and `tests/fixtures/phase10/corrected_w2_baseline.json` via `--baseline-out`.
- [x] The audit publishes one before/after table with a row per memo-section-8
  metric, each row named and computed by
  [the process scorecard](process-scorecard.md): grounded decision rate split
  EJECT/SKIP, argmax-independence (the deviation share **and** its accuracy),
  manufactured-contradiction rate, unexplained-decision rate, evidence quality
  mix, rationale faithfulness, agent-authored share, wrong-but-believable rate,
  and role-correct ejection **reported beside, gating nothing**. Two rows carry
  their reading in the cell: grounded SKIP before is `0` **by instruction**
  (`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:268`, `:259`), and
  agent-authored after is `1.0` **by construction** once the guards label rather
  than re-aim. Neither is a measured gain; neither is left blank.
- [x] The manufactured-contradiction row reads **both** claim shapes: its basis
  test is version-gated over as-recorded bytes, single-room envelopes on the old
  recordings and ordered segments on the new, so no old recording is re-scored
  under the new rule. The card names the function owning the split and pins it
  with a planted fixture of each shape.
- [x] The tour is re-pointed by
  [the spectator card](spectator-tour-and-alternatives.md)'s measured criterion
  re-run on the new bytes; every `FEATURED_GAMES` label
  (`frontend/src/components/ReplayPicker.tsx:94`) is true of the game it names,
  spoiler rule intact; and `cd frontend && npm run e2e` is green, its head-card
  guard binding the promise to the rendered evidence count in both directions
  (`frontend/e2e/journey.spec.ts:455-463`) and turning red on a planted
  mismatched blurb. The last re-record falsified that card (§5.1.1c).
- [x] The ladder tip moves with a record, not a relabel. The audit is
  `audits/audit-<YYYY-MM-DD>-process-rerecord.md`, dated the day leg 1 opens,
  and says "the ladder tip stands at baseline 9";
  `scripts/check_doc_facts.py:235` `_LADDER_TIP_AUDIT` is repointed at it in the
  same pull request, and that script exits 0 with `README.md:23` and `:109`,
  `docs/glossary.md:42` and `:55` and `eval/vote_correctness.py:36-39`
  re-derived. `eval/watchability.py` gains a `baseline-9` block beside `:962`'s,
  both rosters' floors measured from the new bytes, and `:1050`
  `_DEFAULT_BASELINE_ID` advances; `training/bakeoff/harness.py:188`
  `BAKEOFF_BASELINE_ID` does **not**, naming the baseline the ML fits are
  ground on.
- [x] The adoption is routed, not taken: the pull request states that the
  owner's merge adopts baseline 9 and publishes it, because
  `.github/workflows/pages.yml:12-15` rebuilds the demo bundle on every push to
  `main` and `AGENTS.md:21-26` calls a featured-list change a publication
  decision. The card reports and waits; it never merges itself.

## Constraints

**What the owner's merge authorizes, and nothing beyond it.** Provider
`featherless`, model `Qwen/Qwen3.6-27B` exactly
(`llm/featherless_client.py:147`), the default endpoint,
`AILIBI_PROMPT_SET=qwen3_6_27b`, and the bare slate (`--expect-levers ""`, so
all five live toggles at `orchestrator/replay.py:1053-1061` resolve OFF). Each
ceiling is a hard stop, near 1.35x the measured table above to cover the wave's
larger ballot prompt and the re-recorded seeds:

| limit | measured today | authorized |
|---|---|---|
| model calls | 7,271 | 9,500 |
| input tokens | 31,756,112 | 43,000,000 [raised, 2026-09-22 — see below] |
| output tokens | 1,598,475 | 2,200,000 |
| recording wall | about 12h05m | 16 h |
| elapsed window | about 15h48m | 24 h |
| marginal cost | `$0.0000` | `$0.00` |

The cost is `$0.00` marginal against the flat-rate Featherless subscription,
whose standing fee is already paid and is not incurred by this run;
`AGENTS.md:89-92` requires the statement even on flat-rate service.

**Amendment, 2026-09-22 — the input ceiling.** The owner, relayed verbatim by
the orchestrator: *"Raise the input ceiling to 46M"*. The authorized input-token
ceiling is therefore **46,000,000**, and the `43,000,000` above is left as
recorded rather than rewritten. What prompted it: the first ten seeds of leg 1
measured **210,195 input tokens per game**, read as 1.357x the previous
record's per-game input and projected to **43.09 M** over all 300 games — over
the original ceiling by a margin too thin to record against. **Every other
ceiling is unchanged**: 9,500 model calls, 2,200,000 output tokens, a 16 h
recording wall inside a 24 h window, `$0.00` marginal. The stop rule and the
per-leg budget accounting read 46,000,000 from here on.

The record's own re-derivation lands lower and is published beside it
(`audits/audit-2026-09-22-process-rerecord.md` section 0.4a): matched seed by
seed against the preserved old bytes the input ratio is **1.2532**, not 1.357.
The 1.357 is not a per-game ratio: it reproduces only as 43.09 M / 31,756,112,
where 43.09 M = 210,195 x 205, and how the 205 was derived could not be
reproduced. [Corrected in review: this paragraph first said the 1.357
divides a 9p2i per-game cost by the previous record's all-four-set average,
which gives 210,195 / 105,854 = 1.986, not 1.357.] On the
matched ratio the run projects 39.8 M input, 6,917 calls and 1.77 M output,
inside every ceiling including the original. [Corrected at the close: that
ten-seed projection was too optimistic. A corpus game costs more input than a
sample one, the per-set projection at 111 of 300 games was about 42.2 M (98% of
the original 43 M), and the actual landed at 41,556,280 (96.6% of it) — so the
raise was needed, not headroom. The actual is published against 46,000,000.]

**The stop rule.** Stop and report to the owner, before the next leg, on: any
recorded `cost_usd` other than `0.0000`; a leg past 1.5x its projected wall; a
named-not-to-move cell moving at all; a hard provider refusal surviving the
eight-attempt retry budget (`record_ml_corpus.sh:31`), checkpointed and resumed
on the owner's clearance as the `HTTP 402` was (§1.1, §10); and a **stall**, no
completed seed for 45 minutes, where the batch is killed and re-run, or a fresh
operator relaunched from the pushed checkpoint. A seed on disk never re-records
to recover from a stall.

**The freeze and the retention.** From the first seed until this pull request
merges, nothing merges into `engine/`, `agents/`, `meetings/`, `observation/`,
`orchestrator/` or the prompt set, and the audit shows the window's `git log`
rather than asserting it (§0.4, §8). Nothing is archived into the tree: the
baseline-8 bytes stay reachable in git history at the named pre-merge parent,
`docs/artifacts.md:226-228` keeps both replay families whole in git so a second
in-tree copy would be a duplicate registry row rather than a backup, and class
(c) is for evidence that is not a canonical set (`:185-200`). The operator keeps
one out-of-tree copy for the before column and never commits it (§7).

**Non-goals.** No pre-registration, bar or verdict, and no attribution of a cell
to one wave card: everything lands in one window and the record says so (§0.5).
No new lever, no held-out band (the generator is not run and band 2100-2999
stays unseen), no re-scoring of history, no edit to the substrate under record.

## Expected scope

The four recorded sets, `replay-seed-*.jsonl`, `MANIFEST.md`,
`tournament-eval-report.json`, plus `splits.json` for the corpus sets and
`results-rubric-score.json` for `samples/9p2i`. `scripts/record_ml_corpus.sh`
(the version pin only), `scripts/check_doc_facts.py` (`_LADDER_TIP_AUDIT` only),
`eval/watchability.py`, `eval/vote_correctness.py`,
`tests/fixtures/phase10/corrected_w2_baseline.json` (regenerated),
`frontend/src/components/ReplayPicker.tsx` and `frontend/e2e/journey.spec.ts`,
`README.md`, `docs/glossary.md`, `docs/artifacts.md`, `audits/README.md`, the
new record audit, `tasks/README.md`'s inventory sentence, and this card. Not in
scope: `scripts/run_tournament.py`, `scripts/refresh_samples.sh`, the engine,
the agents, the meeting layer and the prompt set. Delivered on
`work/process-rerecord` and one pull request into `main`, merged as a merge
commit or a fast-forward and never squashed, with the commit trailer
`Card: tasks/work/process-rerecord.md` and a checkpoint commit per completed
leg. Every acceptance item that adds a gate carries a planted failure.

Order, identical on all seven cards, and this card is LAST. WAVE 1 is parallel
and changes no agent behaviour: [the scorecard](process-scorecard.md),
[the spectator tour](spectator-tour-and-alternatives.md) and
[the candidate close](close-deduction-candidate-evaluation.md); the close
merges FIRST so the substrate wave's `GENERATOR_SOURCES` edits owe no restamp
to a retired band. The SUBSTRATE WAVE is serial, all three moving the
`qwen3_6_27b` prompt stamps and the ballot or claim schema:
[alibi as a route](alibi-as-route.md), then
[grounded SKIP and guard labels](grounded-skip-and-guard-labels.md), then
[the weighing channel](ballot-weighing-channel.md). This card starts once all
three have merged, taking `ReplayPicker.tsx` and its journey from the spectator
card and the measurement module from the scorecard card. Deferred and in no
card: the body freshness band, an impostor who reports a body, the `docs/`
front door.

## Record impact

This is the wave's adopting record and it replaces every committed recording.
The shipped default behaviour it adopts, the route claim, the grounded SKIP,
the labelling guards, the weighing channel and the bumped prompt set, is
**intended by the owner's rulings of 2026-09-19** and departs deliberately from
the default-OFF-lever rule at `AGENTS.md:71-73`: these are repairs the owner
accepted as a set, not levers under test, so they ship unconditional and
graduate at this recording.

The committed recordings keep loading and verifying **until this card replaces
them**: `bash scripts/verify_samples.sh` and the four
`scripts/build_sample_report.py --sample-dir <set> --check` runs
(`tasks/post-merge-plan.md:148-152`) gate every wave card before this one, each
reading the older recorded shapes as recorded, and gate the new bytes
afterwards. Nothing recomputes over old recordings under a new rule: the
scorecard's version-gated basis test reads each recording as recorded, and
recorded manifests read as-recorded.

Bytes that move, and what recomputes: `docs/artifacts.md:97` the
`replays/samples/` row (today 61 MB / 107 files), `:98` `replays/ml_corpus/`
(161 MB / 209 files), `:101` `tests/fixtures/` (2,098,563 bytes / 29 files,
whose prompt-archive prose the alibi card rewrote and this card closes again)
and `:109` `audits/` (26,522,872 bytes / 328 files), each re-derived from disk;
the ladder tip where the acceptance names it; and the demo bundle, republished
on the merge. Prior records and their verdicts are preserved: baseline 8 keeps
its history and loses only its claim to be current.

## Validation

`scripts/validity_gate.py <set-dir> --expected-model Qwen/Qwen3.6-27B
--require-zero-cost --expected-prompt-versions <pairs>` per leg;
`bash scripts/verify_samples.sh` bare, which walks every committed sample set
(`scripts/verify_samples.sh:35-48`), plus the same script with each
`replays/ml_corpus/<set>`; the four
`scripts/build_sample_report.py --sample-dir <set> --check` runs exiting 0;
`uv run python scripts/check_doc_facts.py`, `scripts/validate_task_docs.py`,
`scripts/gen_frontend_types.py --check` and `scripts/verify_ml_evidence.py`
offline, never `--complete`; `uv run pytest tests/orchestrator/` in a fresh
interpreter; `cd frontend && npm run e2e`; and `bash scripts/check.sh` run whole
in a clean worktree so no gate after the first failure is masked. The only live
provider calls are the authorized recording legs above.

## Results

**Delivered: the four sets re-recorded at the same seeds, 300 of 300 games in
one window, gated leg by leg, and everything derived from them rebuilt or
re-derived. It decides nothing.** The record is
[`audits/audit-2026-09-22-process-rerecord.md`](../../audits/audit-2026-09-22-process-rerecord.md):
the before column committed before the first seed (§1), the legs, gates and
spend (§2, §3), the one before/after table over the nine process rows (§4), the
events (§5), the tour and the ladder (§6), and what it does not discharge (§7).
Design sections this card measures into:
[the direction of 2026-09-19](../direction-2026-09-19-process-over-outcome.md)
section 7 (how it should work), section 8 (the yardstick, one table row per
metric) and section 12 (rulings D1 and D7, and the 2026-09-20 ceilings
addendum); [the process scorecard](process-scorecard.md) for every row
definition; [the spectator card](spectator-tour-and-alternatives.md) for the
featured criterion and the head-card guard. **The owner's merge adopts baseline
9 and publishes it** (`.github/workflows/pages.yml` rebuilds the demo on every
push to `main`); this card reports and waits.

### The after column (pooled over the four sets; per set in the record §4.1)

| # | row | before | after |
|---|---|---|---|
| 1 | grounded, EJECT | 2078/2146 = 0.9683 | 2083/2098 = 0.9929 |
| 1 | grounded, SKIP | 0/1485 **by instruction** | 351/1532 = 0.2291 |
| 1 | grounded, all ballots | 2078/3631 = 0.5723 | 2434/3630 = 0.6705 |
| 2 | deviating crew EJECTs | 116/1811 = 6.4% | 178/1775 = 10.0% |
| 2 | role-correct, followers vs deviators (chance) | 94.5% vs 7.8% (31.6%) | 96.2% vs 9.6% (31.5%) |
| 3 | manufactured contradiction (num/den; not evaluable) | 159/192; 32 | 0/74; 74 — **measured nothing** |
| 4 | unexplained decisions | 20/3631 = 0.0055 | 17/3630 = 0.0047 |
| 5 | evidence mix vent / contradiction / first-hand / hearsay / unevidenced | 333/10/75/8/3 of 429 | 326/5/70/10/0 of 411 |
| 6 | rationale faithfulness (tokens; not evaluable) | 2874/2874; 757 | 3015/3017 = 0.9993; 613 |
| 7 | agent-authored share | 3531/3631 = 0.9725 | 3609/3630 = 0.9942 |
| 8 | wrong-but-believable — reported, never penalised | 383/2146 = 0.1785 | 462/2098 = 0.2202 |
| 9 | role-correct ejection — **beside, gating nothing** | 383/429 = 0.8928 | 369/411 = 0.8978 |

**Row 3 with its census** (record §4.3): the evaluable denominator is ZERO — 42
of the 74 alibi-class flags rest on a multi-stay route, which
`eval.process_scorecard._flag_scored_claim_truth` refuses by design, and 32 name
no self-alibi speaker (the same 32, set by set, as before). The absolute census
carries the reading instead: alibi-class flags 192 → 74 over 672 → 676
meetings (0.2857 → 0.1095 per meeting) while vent flags held 453 → 455;
self-alibi claims 1,003 with 0 multi-stay → 1,021 with 959 multi-stay (0.9393).
The shape split is pinned by the scorecard card's planted fixtures of each shape
(`tests/eval/test_process_scorecard.py`, a one-segment route scored, a part-true
multi-segment route not evaluable, a re-cut stay unchanged).

**Row 7 is not 1.0.** The card expected 1.0 by construction once the guards
label rather than re-aim. What IS zero by construction is the evidence-judgement
rewrites the wave retired (`under_gate_redirect` 83 and `uncited_coerced` 6
before, 0 after). The two rewrites the grounded-SKIP card kept on purpose remain:
`invalid_target` 8 (an illegal target cannot be tallied) and `teammate_coerced`
13 (the teammate firewall). So the guarantee is "no ballot was re-aimed on an
evidence judgement", and the share is 0.9942.

### Spend, against the ceilings (record §2)

| leg | set | recording wall | calls | input | output | cost |
|---|---|---|---|---|---|---|
| 1 | `samples/9p2i` | 2h24m55s | 1,694 | 9,850,930 | 422,941 | `$0.0000` |
| 2 | `ml_corpus/9p2i` | 7h45m05s | 5,084 | 30,053,852 | 1,298,156 | `$0.0000` |
| 3 | `samples/4p1i` | 20m44s | 234 | 782,265 | 51,657 | `$0.0000` |
| 4 | `ml_corpus/4p1i` | 22m44s | 258 | 869,233 | 54,411 | `$0.0000` |
| **total** | 300 games | **10h53m28s** (window 11h05m48s) | **7,270** / 9,500 | **41,556,280** / 46,000,000 | **1,827,165** / 2,200,000 | `$0.0000` |

Counted from the committed bytes' own `llm_calls` rows (the command in
Evidence); it omits the three discarded first attempts of the leg-2 seed
repairs, `$0.0000` like every call. Input reached 96.6% of the original 43 M
ceiling, so the owner's raise was needed (the Amendment above is corrected).

### Decisions and deviations

1. **The sample legs ran as two `--seeds` phases, not one `--full` pass.** The
   honesty probe must run on a leg's first completed seed before the rest queues,
   and `scripts/refresh_samples.sh` re-records a replay already on disk, so a
   `--full` pass after the probe would re-record seed 0. Each sample leg ran
   `--seeds 0`, the probe, then `--seeds 1..49`; canonicality (exactly seeds
   0-49, 50 MANIFEST rows, no alias) was checked explicitly instead of by
   `--full`'s sweep. The corpus legs ran as written.
2. **`audits/workflows/extract_gameplay_facts.py`'s suspicion-row pattern was
   widened (ee9c8dcf)** — routed work, the weighing card's deviation 5: the
   trust column it required was deleted by that card, so the narrowed pattern
   matched nothing and zeroed the rubric's arcs silently. Proven to re-score no
   history: over 6,779 preserved pre-record prompts and 14,599 parsed rows, 0
   mismatches; pinned by `tests/experiments/test_gameplay_facts_suspicion_row.py`
   (formatted at 3eba9495, which `ruff format --check` had flagged).
3. **The rubric is complete by this card's letter and degraded by a
   pre-existing defect.** The rubric step (`refresh_samples.sh:1049-1066`) was
   re-run ALONE on the final bytes; both commands exit 0 and it scores 0.0 on
   all 50 games, because the extractor's self-check "re-derived genuine-class ==
   shipped compute_genuine_class_conversion (supplied 1/0, converted 1/0)"
   FAILS and `experiments/lab/rubric_score.py::_facts_integrity_ok` floors every
   game. Committed as what the shipped tool computes. Its provenance now matches
   the recording, so the served rubric is fresh and every 9p2i card shows a
   0/100 pacing badge (record §7.3). Neither the featured criterion nor the
   head-card guard reads it.
4. **The owner raised the input ceiling to 46,000,000 on 2026-09-22** (the
   Amendment above), relayed verbatim. The run needed it: 41,556,280 actual.
5. **The four eval reports are delivered gzipped — the owner's decision of
   2026-09-22.** `ml_corpus/9p2i`'s report reached 102.70 MB against GitHub's
   100 MB limit and its push was refused. Sizes 102.70 → 8.92 MB, 33.86 → 2.89,
   3.71 → 0.50, 3.37 → 0.46. Proven three ways per set (record §3.5): the sha256
   of the pre-change bytes equals the sha256 of the decompressed archive, and a
   fresh in-memory rebuild (`build_sample_report.py --check`) is consistent.
   `eval/report_io.py` is the one reader and writer; `tests/eval/test_report_io.py`
   pins determinism and a planted wrong-payload archive. Its follow-through at
   this close: `scripts/check_doc_facts.py`'s per-game trigger reader still
   opened the report as plain text (fixed, 5d3b7a60), and many tests read the
   report by the old name (converted to `eval/report_io`, listed below).
6. **`scripts/run_tournament.py`'s staged per-run sidecar stays uncompressed**:
   nothing reads it, it is per-seed and never committed, and converting it would
   reach into the staging and resume machinery the recording depends on.
7. **`meetings/schemas.py:1171` is a docstring naming
   `tournament-eval-report.json`, left as it is**: the only mention inside a
   frozen directory, not a reader, and the freeze forbids the edit.
8. **`scripts/check_doc_facts.py` changed beyond `_LADDER_TIP_AUDIT`**, each
   forced by the record (5d3b7a60): the gzip reader above; the other
   record-tracking constants (`_PROOF_PARTITION_AUDIT`, `_WIN_SPLIT_HEADER`,
   `_BEFORE_COLUMN_HEADER`); a fixed `_FINDING_BASE_AUDIT` so two checks of the
   phase-21 adopting record read the tip of its own day; and the prompt-set
   agreement gate, which assumed one `<family>.<version>` per recording and read
   the wave's v6 + v8 stamp as two substrates — it now compares each row's token
   SET across every row of every set, with five planted cases (craft rule 2).
9. **The W2 baseline fixture's producer is `build_sample_report.py
   --baseline-out`** (the flag `tests/eval/test_gate_spec_metrics.py` names;
   `measure_baseline.py` has none). 83148aa6.
10. **The v5 prompt archive is retired** (a4bbee7f), following the previous
    re-record's retirement of v4: every one of the 676 committed meetings stamps
    the live v6 + v8 set.
11. **The scorecard publisher's provenance sentence was rewritten**
    (`scripts/publish_process_scorecard.py`, 946ab7ba): it called the committed
    sets "before the substrate wave", which this record made false. No row or
    definition moved.
12. **The three public cases were re-curated** (b064bcff), a publication
    change: the payload binds each case to its replay's hash, so the re-record
    suppressed all three by design. Case 1 (seed 23 meeting 0) still holds and
    was re-pinned; the other two described meetings the new bytes changed and
    were replaced on featured games (seed 29 meeting 1, "unsupported"; seed 0
    meeting 1, "unresolved"), every sentence now verified mechanically by
    `_check_case`. The source link points at 9bae2b03, which stays reachable
    only if this pull request lands as a merge commit.
13. **The featured strip** (1bf839da): 9p2i 13 → 0 (13's label was falsified),
    46 → 29 (46 now establishes nothing), 23's second clause dropped (the two
    alibi flags it contrasted are gone — the route claim's thesis on the head
    game); record §6.1.
14. **`eval/watchability.py` gains a measured `baseline-9` block and the default
    advances** (b3b007bf); `training/bakeoff/harness.py` `BAKEOFF_BASELINE_ID`
    stays `baseline-8`, naming the corpus the ML fits are ground on.
15. **The ML pins.** Task 21.17 deleted the STALE amnesty the previous re-record
    used, so no row can honestly be marked a declared gap. Re-derived where a
    test measures the corpus without a fitted artifact; every test that loads a
    fit through its corpus fence, or asserts a frozen fit equals the live
    corpus, is left red (below and record §7.3). The FIRST follow-up routed to
    the owner is the re-ground, successor of Task 21.17, on the same bytes.
16. **Attribution.** This close's commits carry `Co-Authored-By: Claude Opus
    5.5`, the model that wrote them; the recording commits before it carry the
    earlier operator's trailer. The review-fix round's commits after `e89509e1`
    carry the trailer the coordinator set for that round,
    `Co-Authored-By: Claude Fable 5.1`.
17. **`replays/samples/4p1i/MANIFEST.md` stamps a commit no clone can
    resolve.** All 50 rows stamp `git_sha` `5c75028e`. That is leg 2's first
    commit, which carried the 102.70 MB report. The push refused it, and it
    was re-made without the report as `7fd7040f`. It was never pushed and no
    ref holds it. Leg 3's recorder runs all started between the two commits,
    and `scripts/refresh_samples.sh:693` reads `HEAD` once per run. The two
    commits share the parent `820704be`, and
    `git diff --stat 5c75028e 7fd7040f` shows one difference only:
    `replays/ml_corpus/9p2i/tournament-eval-report.json`, 235,845 lines
    deleted. The deleted report's sha256 is `9b17bf9c…`, the bytes the gzipped
    report delivers. So the recording code state is `7fd7040f`. The MANIFEST is
    left as recorded, not hand-edited. The record discloses this in §5 event 5,
    with the commands.
18. **Four exhibits frozen, not re-recorded** (review round, 70e49468). Four
    tests asserted on shapes that the route claim or the labelling guards
    removed from every committed meeting, and the first close left them red.
    They are the seed-41 envelope meeting, the two-author `alibi_conflict`
    flags, the legacy one-room alibi, and a rewritten ballot naming a player on
    a game's last meeting. Each shape's baseline-8 recording is now frozen from
    39a568c6 under `tests/fixtures/baseline8_exhibits/`, and the tests read the
    frozen copy with every assertion unchanged. The README there gives each
    file's source, transform (verbatim, or model calls emptied) and sha256, plus
    a snippet that rebuilds the five files byte for byte from git. The precedent
    is `tests/fixtures/v3_policy_reconstruction/`. The flip search's
    `_STATEMENT_PAIR_CONVICTIONS` is re-pinned to the empty set its walk
    measures. Its baseline-8 loss statement is asserted on the frozen seed-41
    line, apart from the ejectee's role, which a meeting line does not carry and
    which is kept as prose. Record §6.4.
19. **The corpus disclosures re-derived** (2660f4fc).
    `replays/ml_corpus/README.md` items 2-9 held baseline-8 figures under a
    baseline-9 heading. They are re-derived through the section's three folds:
    the eval reports, an `eval.replay_walk` walk under `eval.kill_craft`'s
    profile, and direct counts over the replay rows. Run over the preserved
    baseline-8 bytes, the same derivation reproduces every baseline-8 figure
    except item 7's "looser phrase net reaches 46 and 159". That net's phrase
    list was never committed, no candidate net reproduces 46 and 159 (the
    nearest read 45 and 154), and so the figure is dropped rather than guessed.
    The sentence claiming the gate re-derives items 1, 8 and 9 now names the
    nine cells `scripts/check_doc_facts.py` gates: item 1's meeting total and
    item 8's eight coverage pairs.

### Verification

Re-run in the review round in a fresh worktree, in a bare shell (no
`AILIBI_*` export, no `.env`), with each exit code captured directly. The runs
used `8e6b62eb` plus the recomputed `audits/` registry row, before this
Results edit. `scripts/validate_task_docs.py` was re-run after the edit, and the
key scan was taken last, over the head that carries this line:

```
bash scripts/check.sh (whole)                          EXIT 1 — pytest, below
  ruff check .                                         All checks passed
  ruff format --check .                                521 files already formatted
  lint-imports                                         4 contracts kept, 0 broken
  scripts/validate_task_docs.py                        390 phase tasks + 390 prompts; 73 work cards
  scripts/generate_prompts.py --check                  all 390 prompts in sync
  mypy .                                               no issues in 492 source files
  pytest -n auto --dist loadfile                       8,241 passed, 20 skipped, 3 xfailed;
                                                       43 failed + 9 errors = the 52 red tests below
  (set -e stops check.sh at pytest, so its frontend leg was run on its own:)
cd frontend && npm run lint / tsc:check / test / build EXIT 0 each; vitest 558 passed in 20 files
cd frontend && npm run e2e                             EXIT 0; 13 passed, 3 skipped (the README
                                                       media-capture suite, skipped by design)
bash scripts/verify_samples.sh                         EXIT 0; 50 + 50 verified clean
bash scripts/verify_samples.sh replays/ml_corpus/9p2i  EXIT 0; 150 verified clean
bash scripts/verify_samples.sh replays/ml_corpus/4p1i  EXIT 0; 50 verified clean
scripts/build_sample_report.py --sample-dir <set> --check, all four sets   EXIT 0 each
scripts/publish_process_scorecard.py --check           EXIT 0, consistent
scripts/check_doc_facts.py                             EXIT 0
scripts/validate_task_docs.py (after this edit)        EXIT 0
scripts/generate_prompts.py --check                    EXIT 0
scripts/gen_frontend_types.py --check                  EXIT 0
uv run pytest tests/orchestrator/ (fresh interpreter)  586 passed, 3 xfailed
scripts/verify_ml_evidence.py (offline, never --complete)   EXIT 1; 61 checks: OK 37,
                                                       FAIL 12, ABSENT 7, INFO 5 — the 12 are the
                                                       corpus rows of record §7.3
scripts/measure_featured_criterion.py                  EXIT 0; eligible openers 32/50 and 19/50
scripts/measure_baseline.py --watchability --json      EXIT 0; baseline-9 default: referee and
                                                       supply floors pass on both sets, every
                                                       gauge at exact equality
git log --oneline 39a568c6..HEAD -- engine agents meetings observation orchestrator
                                                       (empty: the freeze held)
git log --oneline 39a568c6..origin/main                (empty: main did not move)
count-only key scan over every added or changed byte   427 files, 307,038,663 bytes, 0 matches
  (git diff --name-only --diff-filter=AM 39a568c6..HEAD at the head carrying this line;
   gzipped reports decompressed; the five patterns each fire once on a planted key)
```

The planted failures this close added or re-proved: the prompt-set agreement
gate's five cases (a whole set on another ballot version, one row on another
version, one row with fewer tokens, a lead-in missing a token, the committed
stamp passing); the featured-label claims, each with its own planted case; the
head-card guard in both directions (1 failed / 7 passed, and 2 failed / 6
passed, each restored byte-identically and green); the `role_proof` isolating
case (weakening the clause: 1 failed / 51 passed); 18 planted defects against
the public cases' checks, all refused, 4 kept as a test; and the key scan's five
patterns, each firing once on a planted key.

### Limitations

- **Tests left red: 52, listed under "Left red" at the end of this section.**
  `bash scripts/check.sh` does not pass. The ML set (43) fails for one cause,
  the fits' corpus; nine more fail because the new bytes falsified what they
  assert, and re-pinning them would have meant deleting or weakening an
  assertion. Eight more were red at the first close and now read frozen
  baseline-8 exhibits or a re-pinned empty set (decision 18). Each is listed with its reason, and in the record §6.4 and §7.3.
  By AGENTS.md a card is done only when `check.sh` passes; this card is marked
  done on the coordinator's instruction with every red named, and the owner
  decides whether it stays done until the re-ground and the §6.4 rulings land.
- **The rubric is zeros** and the viewer shows 0/100 badges (decision 3).
- **Row 3 is not evaluable on these bytes**; the per-stay basis test is the
  third follow-up routed to the owner.
- **The ML fits are not grounded on these bytes** (decision 15). A finding for
  the re-ground: the freshly fitted ballot surrogate scores 46/52 top-1, above
  the documented "honest ceiling" of 41/52 (gap −0.0962, pinned as measured).
- **Legibility residual.** A contradiction evidence row reads `not first-hand:
  <subject> stated it at this table`, and the sentence beside it is the
  detector's, not the subject's; pinned by the weighing card, and a prompt-byte
  change is frozen under this record.
- **A pre-existing leak the wave recorded for the owner**: a flag description's
  `[weak signal: ungrounded sighting]` vocabulary is chosen by the speaker's
  private record and rendered to every voter (23 of 60 generated meetings moved
  when only others' private records changed). Not a wave item.
- **Stale labels the freeze or the recorder keeps**: both corpus FROZEN lines
  say "baseline-8 re-record" (hard-coded at `scripts/record_ml_corpus.sh:1066`);
  `meetings/manager.py` prose cites retired-marker counts these bytes do not
  carry. Record §7.2.
- **Restatements for the owner to confirm** (listed below with the `RESTATED:`
  and `RE-ANCHOR:` prefixes): where a pinned example no longer carried its
  shape, the same property was re-stated on a game that does, by measurement.
- **Frozen exhibits are history, not the record** (decision 18): the tests
  that read them prove the detector, the reduction and the loader still behave
  on a recorded baseline-8 shape. They say nothing about how often the shape
  occurs on baseline 9, where it does not occur.
- **The corpus disclosures were re-derived by a script that is not
  committed** (decision 19). It implements the README's three folds, and on the
  preserved baseline-8 bytes it reproduces every figure the section held except
  the dropped looser net. The README's own fold commands are the committed
  method, and they cover a subset of the cells.

### Every changed expectation

Old is the value at `main` 39a568c6 (baseline 8). New is the value at f4961ad1, re-derived from the baseline-9 bytes through the production computation the test itself calls. Unprefixed bullets are value re-pins. The prefixes mark the other kinds of change:

- **GZIP:** a report read or write moved to `eval/report_io.py`.
- **RE-ANCHOR:** an example seed, meeting or set was replaced by measurement; the property is the same.
- **RESTATED:** a property was re-stated on the new bytes. Each one needs owner review.
- **RETIRED:** part of the retirement of the v5 prompt archive.
- **PLANTED:** a new planted failure was added.
- **FIXTURE:** a fixture derivation was fixed; no value moved.
- **FROZEN:** added in the review round (70e49468). The test now reads a frozen baseline-8 exhibit under `tests/fixtures/baseline8_exhibits/` instead of the committed corpus, because no committed meeting carries its shape any more. No assertion changed. The README there gives each file's source at 39a568c6, its transform and its sha256.

`[owner review]` marks a re-pin whose property now holds only vacuously or whose verdict flipped. Where one bullet carries several floats, they are rounded to 4 d.p. The test file holds the exact value, and its `# was` comment holds the old one.

Where a value re-pin names no other reason, the reason is the record itself: the four sets were re-recorded at the same seeds on the substrate wave's bytes, so the census moved, and the new value was read off the production computation.

#### tests/_helpers/committed.py
- FROZEN: new `BASELINE8_EXHIBITS` path and `frozen_meetings(name)` reader, which refuses a file holding anything but meeting lines. It pins no value.

#### tests/agents/test_absence_prior.py
- GZIP: `TestAbsencePriorOnCommittedBytes.roles_by_seed` reads through `read_set_report_text` (134b10de).
- `test_meeting_census`: total_meetings 151 -> 145. The re-recorded samples/9p2i set holds 145 meetings.
- `test_nonempty_absent_meeting_count`: 48 -> 55. More meetings leave a living player publicly unplaced.
- `test_absent_set_size_distribution`: histogram ((0,103),(1,48)) -> ((0,90),(1,54),(2,1)); absent_max 1 -> 2. One meeting now leaves two players unplaced.
- `test_recorded_vent_flag_census`: vent_flag_meetings 68 -> 70; vent_flag_count 90 is unchanged. The same 90 vent flags now fall across 70 meetings.
- `test_vent_double_count_population`: ((0,124),(1,27)) -> ((0,112),(1,33)); meetings 27 -> 33. More vent-sighted subjects are also priced absent.
- `test_widened_absent_set_size_distribution`: ((0,130),(1,21)) -> ((0,122),(1,23)); widened_nonempty_absent 21 -> 23. It follows the two cells above.

#### tests/agents/test_beliefs.py
- GZIP: both `roles_by_seed` fixtures read through `read_set_report_text` (134b10de).
- RE-ANCHOR: `TestRelevanceGatedFoldOnCommittedBytes` (3 tests): `_SEED` 37 -> 34, `_SUBJECT` p-2 -> p-9, `_GATED` [0.5, 0.55, 0.55] -> [0.5, 0.55, 0.5375]; `_UNGATED` is unchanged. Seed-37 p-2 no longer lifts (gated == ungated). Seed 34 p-9 is the one crewmate with the class's shape, found by census.
- `TestEvidenceQualityLiftOnCommittedBytes::test_no_crew_row_reaches_certain_guilt_set_wide`: `_MAX_CREW_RENDER` 0.95 -> 0.9. This is the measured set-wide crew maximum over 2,588 rows, and it is still < 1.0.
- `TestReporterExculpationOnCommittedBytes::test_measured_corpus_census_and_zero_self_report`: report_ejections 85 -> 80. There are fewer ejections at body meetings.
- `…::test_damp_effect_on_innocent_reporter_lifts`: (kept, already_sub_gate, hard_convicted) (2, 3, 2) -> (4, 1, 2). The same seven innocent-reporter meetings split differently.
- `…::test_zero_hard_flag_backed_convictions_change_outcome`: len(report_ejections) 85 -> 80. Same census as above.

#### tests/agents/test_beliefs_hard_evidence_gate.py
- GZIP: `roles_by_seed` (134b10de).
- `test_report_ejection_census`: the funnel and counterfactual report ejections 85 -> 80.
- `test_soft_only_split_by_role`: kept CREWMATE 1 -> 0; still_over IMPOSTOR 12 -> 8; soft_only_total 18 -> 13. already_sub_gate (5) and hard_backed (67) are unchanged. On baseline 9 the clamp neutralises no crew mis-eject.

#### tests/agents/test_impostor_policy.py
- `test_free_zero_witness_kills_declined_pins`: after (8, 237) -> (9, 232); fellow_defer 6 -> 7; decisions_reconstructed 1826 -> 1754; in_vent 119 -> 109. These are the re-recorded impostor decision streams.
- `test_no_recorded_kill_is_lost`: samples/9p2i 229 -> 223, ml_corpus/9p2i 678 -> 703, samples/4p1i 64 -> 68. Reproduced still equals recorded on all four sets.
- `test_ghost_top_decisions_pin_on_every_set`: [(3,1826),(4,5584),(0,536),(0,526)] -> [(5,1754),(5,5748),(0,558),(0,531)]; samples/9p2i unseen_death 3 -> 5. ghost_top_ejected is still 0.
- RE-ANCHOR: `test_seed_7_refutes_a_living_lead_and_keeps_it_dropped` is renamed `test_seed_20_…`. The example moves from seed 7 p-2 at ticks 13/14 (lead p-1, own room LABS) to seed 20 p-8 at ticks 5/6 (lead p-5 in WEST_HALL, own room WEST_HALL -> ADMIN). Seed 7 p-2 no longer decides at tick 13; seed 20 is the first "stand in the room, then leave" match found by search.

#### tests/agents/test_memory_meeting_history.py
- `_COUNTERFACTUAL_CENSUS`: samples/9p2i (869, 411, 406, 24, 8) -> (845, 401, 396, 24, 11); ml_corpus/9p2i (2516, 1186, 1160, 78, 44) -> (2539, 1247, 1163, 183, 42). The 4p1i rows are unchanged. These are the re-recorded ballot renders.
- `test_the_census_totals_reproduce_the_review_counts`: (renders, gained) (3631, 1597) -> (3630, 1648); stale_vents 52 -> 53. These are sums of the rows above.

#### tests/agents/test_reported_testimony.py
- `test_reported_rows_survive_in_every_candidate_bucket` (left red on its 0.80 floor): renders 2516 -> 2539. By bucket (<=60 / 61-100 / 101-150 / >150), offered goes 11484/14982/7316/3341 -> 8983/21947/16547/7539 and kept goes 11484/14965/7295/3214 -> 8983/21612/14824/5927. The offered rows in the two buckets past 100 candidates more than doubled (10,657 -> 24,086).

#### tests/api/fixtures/evidence_mechanisms.py
- `PROVENANCE_IMPOSSIBLE_SIGHTING.anchors[0].flags` (9p2i seed 23 M1): the two weak flags on p-4 -> (). The meeting now carries no flag; status FLIPPED is kept.
- `CONTENT_VS_OWN_MEMORY_MISS.anchors[0]` (9p2i seed 12 M0): ejected_player_id p-5 -> p-2, and the two weak flags on p-5 -> (). The meeting ejects crewmate p-2 on no flag; status PARTLY FLIPPED is kept.

#### tests/api/test_cost_integrity.py
- GZIP: `test_api_rebinds_serialized_verification_to_actual_recording` plants its report with `write_report_text(report_path(tmp_path), …)`.

#### tests/api/test_eval.py
- GZIP: `test_tournament_report_present_returns_200` writes through `write_report_text(report_path(…))`, and the module docstring names `.json.gz`.
- `test_committed_4p1i_report_validates_against_current_model`: total_ejections 24 -> 20, ejection_accuracy 20/24 -> 20/20, crewmate_ejections 4 -> 0. samples/4p1i no longer ejects a crewmate.

#### tests/api/test_eval_routes.py
- GZIP: the `served_failed_call` fixture and three tests (`test_served_payload_no_longer_validates_as_raw_report`, `test_served_report_includes_meeting_rate`, `test_served_payload_exposes_no_engine_state_field`) write the gzipped report. The first and third had been passing vacuously against the 404 body.

#### tests/api/test_evidence_mechanisms.py
- `test_provenance_impossible_sighting_no_longer_mints_its_flag`: [weak_signal, weak_signal] plus all-weak -> `meeting.contradictions == ()`. Seed 23 M1 has no flag, so this is a strictly stronger assertion (the baseline-7 form).
- `test_content_vs_own_memory_miss_defangs_the_flag_but_still_ejects`: two weak flags -> `()`; ejectee p-5 -> p-2, still a CREWMATE. Seed 12 M0 ejects a different crewmate, on no flag.
- RE-ANCHOR: `test_the_flip_search_finds_exactly_the_named_meetings`: the planted source moves from seed-12 M0 `contradictions[1]`, which no longer exists, to `_PLANTED_SOURCE = (9, 0, 0)`: the only flag of seed 9 M0, weak alibi_vs_sighting on crewmate p-1. The source is now pre-asserted and the plant runs before the walk.
- `_STATEMENT_PAIR_CONVICTIONS` (review round, 70e49468): {`headless-seed-41:meeting-2`} -> `frozenset()`. The walk finds no statement-pair wrongful conviction on baseline 9, and the test's own comment says a meeting leaving the set means the pin needs revisiting. Empty is the stricter growth tripwire, because any meeting convicting this way now fails it. The planted case still proves the predicate fires. The test is green.
- FROZEN: the two baseline-8 loss statements move off the committed walk. The flag kinds are asserted on the frozen seed-41 line through the loader's own projection (`api.replay_loader._contradiction_view`): two STRONG cross-statement `alibi_vs_sighting` flags naming the ejected p-9. The ejectee's CREWMATE role is not in a meeting line, so it is kept as history prose rather than asserted, as the review finding allowed. The now-unused role map of the walk is removed.

#### tests/api/test_evidence_taxonomy.py
- `_EXPECTED_COUNTS` (role_proof / cross_statement / weak_signal): samples/9p2i 90/7/50 -> 90/6/11, ml_corpus/9p2i 315/8/126 -> 317/13/44, and ml_corpus/4p1i weak 1 -> 0. Far fewer weak alibi flags on the route-claim bytes.
- `test_corpus_wide_totals`: 453/177/15 (645 flags) -> 455/55/19 (529 flags).
- `test_endpoint_render_classes`: self_linked/two_turns/same_turn 453/126/66 -> 455/70/4, of 529.
- RESTATED: `test_seed_47_is_entirely_weak_signal` is renamed `test_corpus_seed_1135_innocent_ejection_is_entirely_weak_signal`.
  - It moves from samples seed 47 M2 to ml_corpus/9p2i seed 1135 M0.
  - That meeting is EJECTED, the ejectee is a CREWMATE, the categories are {weak_signal}, and one flag names the ejectee.
  - Seed 47 now has one meeting, and samples/9p2i has no innocent ejected on weak-only flags.
  - The body had pinned {role_proof} since baseline 7.

#### tests/api/test_main.py
- FIXTURE: `_mixed_substrate_set` restamps every row that carries `substrate_flags`, not only game_over. Baseline-9 recordings also stamp the first tick row, and a footer-only restamp was refused earlier as a contradiction.

#### tests/api/test_observation_references.py
- RE-ANCHOR: `test_genuine_citations_keep_source_identity_and_separate_scene_time`. Seed 46 M3's memories now cite nothing, so the two params move to seed 4 M0:
  - (46, 3, p-9, p-9:29:3, saw_player_move, p-1, 29, 28) -> (4, 0, p-5, p-5:7:1, saw_player_move, p-1, 7, 6);
  - (46, 3, p-3, p-3:29:1, saw_player, p-4, 29, 28) -> (4, 0, p-1, p-1:7:1, saw_player, p-3, 7, 6);
  - text "p-3 saw p-4 in CAFETERIA with p-9." -> "p-1 saw p-3 in EAST_HALL with p-9.", and the move CAFETERIA->EAST_HALL -> ENGINEERING->EAST_HALL.

#### tests/api/test_public_results.py
- `test_current_summary_is_bounded_and_source_checked`:
  - (games, completed, crew, impostor, task wins) (50, 50, 35, 15, 0) -> (50, 50, 39, 11, 1);
  - (meetings, ejections, impostor, innocent) (151, 95, 82, 13) -> (145, 90, 81, 9);
  - proof (68, 68, 27, 14) -> (70, 70, 20, 11).
- The same test: dates 2026-08-30 -> 2026-09-22 and source commit 5006a32f -> 9bae2b03. The cases are now pinned as (classification, meeting): (supported, 23 m0), (unsupported, 29 m1), (unresolved, 0 m1).
- RE-ANCHOR: `test_a_changed_case_projection_cannot_keep_its_prose`: the altered memory (seed 46, M3, p-3) -> (seed 29, M1, p-7). This follows the re-curated case.
- PLANTED: new `test_a_case_sentence_the_recording_no_longer_shows_withholds_publication[not-an-emergency|route-refuted|skip-not-chosen|flag-names-p-1]`. Each param breaks one fact a case sentence rests on, and each must raise "Curated case".
- RESTATED: `test_historical_summary_never_invents_a_default_factory`: the canonical groups' agent_factory_kind None -> "scripted". The "never invents" property moves to a tmp copy of seed 0 with the stamp removed, where the factory and clock stay None. Baseline-9 recordings stamp the factory.

#### tests/api/test_replay_loader.py
- FIXTURE: `_stamp_committed_9p2i_seed` and `_mixed_substrate_set` restamp every row that carries `substrate_flags`. Same cause as test_main; five tests were refused with observation_version_mismatch before this.
- `test_committed_9p2i_fake_tasks_emergencies_and_repairs_are_named`: fake tasks 373 -> 365, PRETEND_TASK 365 -> 354, BLOCKED 8 -> 11, repair REPAIR 26 -> 22 (BLOCKED 12). All 11 BLOCKED share a tick with a meeting.
- `test_committed_turn_marker_census_and_zero_served_leak`: 9p2i (869, 2, {invalid_accusation_target: 2}) -> (845, 1, {…: 1}). There is still zero served leak.

#### tests/api/test_sets.py
- RESTATED: `test_the_served_rubric_reads_stale_against_the_rerecorded_manifest` is renamed `test_the_served_rubric_is_fresh_but_every_score_is_floored`.
  - git_head != manifest -> ==, and stale True -> False.
  - It adds: 50 rows, every score 0.0, and some r1_decisive > 0.
  - The rubric was regenerated (83148aa6), and the extractor self-check floors every score.
- `test_featured_seeds_exist_in_their_committed_sets`: the 9p2i featured set {2, 13, 23, 46} -> {0, 2, 23, 29}. The heads and 4p1i {2, 11, 29} are unchanged.
- RE-ANCHOR: `test_featured_head_criterion_rejects_a_head_that_establishes_nothing` re-labels the 9p2i params to each seed's new first-meeting shape:
  - 13 -> "ejects a CREWMATE on no flag";
  - 44 -> "ejects an IMPOSTOR on no flag at all", and 12 -> "ejects a CREWMATE on no flag at all";
  - 10 -> "no ejection anywhere".
- The same test adds and moves params:
  - new 9p2i 36 carries 13's old shape;
  - new 9p2i 7 (ejects an impostor on cross_statement flags) is the isolating case;
  - 4p1i 29 -> "the one meeting skips".
- RE-ANCHOR: `test_seed_10_isolates_the_role_proof_clause` -> `test_seed_7_isolates_the_role_proof_clause`, with the same five facts. Seed 10 no longer ejects. The tour worker checked by hand that weakening the clause fails exactly this case.
- RE-ANCHOR: `test_featured_seed_13_card_states_the_served_turn_shape` -> `test_featured_seed_0_card_states_the_served_meeting_shape`. Turns (7, 6, 5) -> (8, 7, 6), and it adds per-meeting flag kinds and label wording. Seed 0 took seed 13's slot on the strip.
- PLANTED: the `_assert_featured_counts` vocabulary gains new count words and three flag claims (vent / only weak signals / contradictions). Each claim is checked against the served flags and has its own planted strip-the-flags case. The params go from 6 featured games -> all 7.

#### tests/api/test_view_model.py
- RESTATED: `test_gate_marker_chips_on_committed_9p2i_bytes`: nulled 3 -> 0 and redirected 23 -> 0. It adds `len(ballots) == 845` and `invalid_target == 3`. The anchor moves from the seed-22 M0 under_gate_redirect chip to the seed-7 M0 invalid_target chip (target SKIP). Ruling D6 retired the redirect guard.
- RE-ANCHOR: `test_finale_pins_committed_eject_decided_game`: seed 18 -> seed 7, final_tick 13 unchanged.
  - Decisive beats -> [(6,kill,p-2,p-4),(10,ej,p-3,p-2),(11,kill,p-7,p-9),(13,ej,p-6,p-7)].
  - Impostors (p-5,p-7) -> (p-2,p-7).
  - p-7's final vote p-8 -> p-6, still False. The None recap moves p-3 -> p-4.
  - Seed 18's ejected impostor now SKIPs.
- RESTATED: `test_finale_pins_committed_wrong_ejection_game`: seed 47 -> seed 5.
  - final_tick 42 -> 25; ejections [(25,p-9)] -> [(8,p-3),(14,p-1)]; skipped [7,14,26,32] -> [13].
  - The surviving crewmate's vote moves p-7 -> p-5 and is now judged False (was True).
  - It adds: the voters naming p-1 are {p-2,p-4,p-5,p-9}, all False, and p-3 and p-4 are IMPOSTORs.
  - Seed 47 is now a crew task win, and baseline 8's "True" element exists in no parity game.
- FROZEN: `test_finale_recap_flags_a_rewritten_ballot_and_withholds_judgment` takes a new `rewritten_ballot_loader` over the frozen baseline-8 `samples/9p2i` seed 11 and its roster. On baseline 9 all 21 target rewrites (8 `invalid_target`, 13 `teammate_coerced`) tally SKIP, so no committed game ends on a rewritten ballot naming a player. The assertions are unchanged, and the test is green.

#### tests/eval/test_accusation_calibration.py
- GZIP: `_committed_calibration` and `test_the_committed_guard_drop_reconciles_against_the_vote_curve` read through `read_set_report_text`.
- `_COMMITTED_SPLIT` (`test_committed_sets_pin_the_accuser_role_split`), ece and n for pooled / crew / impostor:
  - samples/9p2i 0.2978/738, 0.1751/550, 0.6758/188 -> 0.3031/750, 0.1896/567, 0.6746/183;
  - ml_corpus/9p2i 0.2785/2153, 0.1636/1624, 0.6791/529 -> 0.2863/2290, 0.1686/1720, 0.6754/570;
  - samples/4p1i 0.2947/103, 0.1231/65, 0.6408/38 -> 0.2486/110, 0.1120/71, 0.6256/39;
  - ml_corpus/4p1i 0.2875/120, 0.1006/77, 0.6453/43 -> 0.2772/116, 0.1048/73, 0.6442/43.
- `test_the_4p1i_impostor_curves_are_honestly_low_power`: populated_bins are now pinned per set. samples/4p1i stays 4; ml_corpus/4p1i 4 -> 3. Both are still < 5 and low_power.
- RESTATED: `test_the_committed_guard_drop_reconciles_against_the_vote_curve`.
  - The assertion `guard_authored_excluded > 0` on every set becomes exact per-set drops plus `any(drop > 0)`.
  - The drops: ml_corpus/4p1i 2 -> 0, ml_corpus/9p2i 67 -> 1, samples/4p1i 1 -> 0, samples/9p2i 26 -> 0.
  - The guard now authors one binnable ballot in the whole corpus.

#### tests/eval/test_deception_instruments.py
- `test_corpus_nine_is_the_audit_census`, first half:
  - meetings 439 -> 449; accusations 529 -> 570; frame meetings 431 -> 446;
  - crew/impostor/no-eject 29/252/158 -> 32/241/176;
  - vouch 405 -> 409; frame-vouch obs 48 -> 59; frame-vouch total 89 -> 101.
- Same test, second half:
  - corroboration 1039 -> 1040 (impostor 157 -> 148);
  - subject events 43 -> 49; companion join 37/11 -> 50/9;
  - frame conversions 26/431 -> 31/446; alibis 97/86 -> 112/104.
- Same test, deflection: events/survivals/active/effective/named/third-party/skip-saved 402/150/141/70/26/44/71 -> 411/170/161/91/45/46/70; teammate denominator 529 -> 570, numerator still 0.
- `test_sample_nine_full_pins`:
  - meetings 151 -> 145; accusations 188 -> 183; frame meetings 150 -> 142; eject 13/82/56 -> 9/81/55;
  - vouch 136 -> 123; corroboration 324 -> 347; frame conversions 9/150 -> 8/142; alibis 37/31 -> 41/39;
  - deflection 132/51/50/38/18/20/12 -> 122/42/40/25/15/10/15.
- `test_sample_four_full_pins`: frame 38 -> 39; crew eject 4 -> 0; vouch 7 -> 2. The frame-vouch corroboration rate 0.0 -> None (denominator 0). Frame conversions 4/38 -> 0/39 (advisory); alibis 4/4 -> 1/1; deflection events 33 -> 37, skip-saved 10 -> 16.
- `test_corpus_four_full_pins`: eject 0/29/14 -> 1/27/15. Vouch obs 2 -> 0, so the frame-vouch obs rate -> None. Frame conversions 0/43 -> 1/43; deflection events 40 -> 42, skip-saved 9 -> 13.

#### tests/eval/test_deduction_metrics.py
- GZIP: `_committed()` and `test_block_round_trips_through_json` read through `read_set_report_text`.
- `test_samples_9p2i_meeting_flag_partition`: meetings 151 -> 145; flagged 68 -> 70 (all impostor); unflagged 83 -> 75 (impostor/innocent 14/13 -> 11/9); accuracy 14/27 -> 11/20.
- `test_samples_9p2i_ejectee_proof_partition`: ejections 95 -> 90; proof-present 68 -> 70; non-direct 27 -> 20; accuracy 14/27 -> 11/20; correct 82 -> 81.
- RESTATED: `test_the_two_partitions_are_not_interchangeable`: the totals re-pin 95 -> 90, 68/68 -> 70/70 and 27/27 -> 20/20.
  - On samples/9p2i the two partitions are now the same set.
  - The C5 inequality moves to corpus 9p2i: flagged-meeting ejections 213 vs proof-present 211 (new fixture `corpus_9p2i`).
- `test_corpus_9p2i_cross_tab_twins`:
  - meetings 439 -> 449; flagged 220 -> 215 (impostor 211, innocent 0 -> 2); unflagged 219 -> 234 (30/30);
  - ejections 281 -> 273; proof 220 -> 211; non-direct 32/61 -> 30/62; correct 252 -> 241.
- `test_4p_sets_cross_tab`: samples ejections 24 -> 20, unflagged innocent 4 -> 0, non-direct 5 -> 1; corpus ejections 29 -> 28, non-direct denominator 3 -> 2.
- `_EXPECTED_CATEGORY_COUNTS`: samples/9p2i (90,7,50) -> (90,6,11); ml_corpus/9p2i (315,8,126) -> (317,13,44); ml_corpus/4p1i (28,0,1) -> (28,0,0).
- `test_every_committed_flag_classifies_identically_on_both_surfaces`: 147 + 449 -> 107 + 374 flags, all agreeing.
- `test_roll_call_coverage_split_under_both_estimators`:
  - samples crew 651/651 -> 635/635, impostor 106/218 -> 104/210, pooled 0.4862 -> 0.4952, macro 0.4536 -> 0.4655;
  - corpus crew 1880 -> 1888, impostor 292/636 -> 298/651, macro 0.4203 -> 0.4165.
- `test_roll_call_coverage_4p_sets`: impostor turns, samples (6,39) -> (2,39) and corpus (3,43) -> (1,43).
- `test_thirteen_engine_redirected_ejects_reproduces`: redirected 23 -> 0, redirected ejects 23 -> 0, ballots 869 -> 845, share 23/869 -> 0/845. The redirect class is empty on all four sets.
- `test_weak_flag_only_conviction_lands_on_the_audit_exhibit`: samples flag-named 75 -> 72, weak-only 6 -> 0 (innocent 5 -> 0, impostor 1 -> 0); corpus flag-named 223 -> 214, weak-only 3 -> 2 (innocent 3 -> 2).
- RESTATED: `test_seed_47_is_the_sample_weak_only_conviction`: the samples list goes from 6 rows to [], and the exhibit moves to the corpus's two: (1016, M0, p-8) and (1135, M0, p-2), both innocent. The samples set has no weak-only conviction.
- `test_turn_ballot_consistency_pins`:
  - samples accusing 738 -> 750, consistent 402 -> 399, skip 277 -> 299, other 57 -> 49, invalid 2 -> 3, unwound 21 -> 3;
  - corpus accusing 2149 -> 2286, consistent 1175 -> 1209, skip 809 -> 910, invalid 2 -> 5, unwound 62 -> 9.
- RESTATED: `test_consistency_is_scored_against_the_authored_target`: scored 738 -> 750, naive 392 -> 399, consistent 402 -> 399, unwound 21 -> 3.
  - It adds naive_skip 302 and inconsistent_skip 299, with their difference equal to unwound.
  - The disagreement moved from the consistent count to the SKIP bucket.
- `TestTheRedactionRecognizerIsGenerationAware::test_the_live_body_is_what_the_committed_bytes_carry`: carried 2 -> 1.
- `test_scaffold_leakage_reproduces_the_19_8_disclosure`: partner-naming ballots, samples (36,218) -> (41,210) and corpus (137,636) -> (124,651). Role statements: samples 10 -> 12, corpus 39 -> 36, corpus/4p1i 8 -> 3.
- `test_self_kill_disclosure_is_counted`: samples self-kill 6 -> 12, omniscient 45 -> 59, crew control 1 -> 0; corpus 17 -> 32, 169 -> 172, crew control 2 -> 3.
- `test_the_pre_guard_body_is_the_parsed_field_not_the_raw_envelope`: envelope hits 530 -> 501.
- `test_guard_preserved_omniscient_rate_has_its_own_denominator`: rate (0,70) -> (0,17); guard-marked 80 -> 20; share 80/2516 -> 20/2539.
- `test_machinery_quotation_reproduces_the_19_8_disclosure`: vocabulary ballots, samples 0 -> 4 and corpus 11 -> 15. Quotations stay 0.
- `test_guard_originated_stale_rationales_are_rare_not_absent` (samples/9p2i param): expected 1 -> 0 `[owner review: the class is absent on all four sets; the test name is now false]`.
- `test_guard_marker_counts`: samples marked/rewrites 30/27 -> 6/4; corpus 80/70 -> 20/17.
- `test_witnessed_supply_adopts_the_kill_craft_pins`: corpus (532,18) -> (550,16); samples-9p2i (182,3) -> (175,3); samples-4p1i (62,1) -> (66,1).
- `test_wilson_cell_rejects_a_hand_edited_interval`: good cell (14,27) -> (11,20). `test_wilson_cell_rejects_a_wrong_advisory_flag`: weak-only numerator 6 -> 0, still advisory.
- `test_block_round_trips_through_json`: proof_present_ejections 68 -> 70.
- `_ORACLE_CENSUS` claim-reason bases: samples/9p2i 1062 -> 1097, ml_corpus/9p2i 3192 -> 3330, samples/4p1i 127 -> 136, ml_corpus/4p1i 145 -> 142. The register stays 0.
- `test_the_crew_omniscient_control_is_one_on_each_9p2i_set`: samples 1 -> 0, corpus 2 -> 3 `[owner review: the name is now false]`.

#### tests/eval/test_evidence_honesty.py
- `test_the_same_mismatch_is_counted_when_fidelity_is_not_asserted`: S4 crew_false (0,79) -> (1,79).
- `test_i2_false_crew_self_placement_pins`:
  - crew_false S9 (6,660) -> (5,679), C9 (20,1920) -> (17,2003), S4 (0,79) -> (1,79), C4 (1,89) -> (0,87);
  - agent-frame S9 (3,660) -> (2,679); impostor_false S9 (0,106) -> (1,110); copyable S9 (39,660) -> (34,679).
- `test_i3_sole_flag_precision_pins`: per-victim [(0,1),0…] -> [(0,0),(1,1),(0,0),(0,0)]; (meetings, ejections, crewmates) (1,1,1) -> (1,1,0). The S9 base (1,5) -> (0,0), and a corpus base (1,7) is added. The class moved from samples to the corpus.
- `test_i4_grounded_sighting_side_pins`: sides [2,0,0,0] -> [0,1,0,0]; S9 cells (2,2) -> (0,0); C9 at_tick (0,0) -> (0,1) and within_2 (0,0) -> (1,1); a C9 within_1 (1,1) pin is added.
- `test_i5_fabricated_completion_pins`: S9 (0,311) -> (0,271); C9 (0,986) -> (0,854).
- `test_i6_adjacent_room_strong_share_pins`: per-set [(0,2),0…] -> [(0,0),(1,1),(0,0),(0,0)]; distance_two 2 -> 0; single_tick_window 0 -> 1.
- `test_i7_movement_origin_flag_pins`: [(0,30),(5,80),…] -> [(0,8),(2,32),(0,0),(0,0)]; pooled (5,110) -> (2,40); truthful 5 -> 2; S9 move-backed and spoke-destination 13 -> 0.
- `test_i8_marker_contamination_pins` / `test_i9_singular_persona_pins`: S9 turns 869 -> 845, prompts 1740 -> 1694; C9 turns 2516 -> 2539, prompts 5039 -> 5084. All numerators stay 0.
- `test_i10_meeting_physicality_pins`:
  - venting [(27,151),(60,439),…] -> [(29,145),(63,449),…]; killed [(19,151),(56,439),…] -> [(18,145),(63,449),…];
  - pooled 96/672 and 78/672 -> 101/676 and 84/676;
  - S9 body-triggered 141 -> 135; body-killed [(19,141),(56,407),…] -> [(18,135),(63,416),…]; S9 rate 0.1348 -> 0.1333.
- `test_the_agent_clock_is_proved_on_every_committed_set`: checked [2984,9407,375,415] -> [2996,9725,382,417] (sum 13181 -> 13520); stamped [77,300,16,27] -> [76,301,18,27].
- `test_render_budget_pins`: snapshots 1740 -> 1694; lines 63624 -> 64193; mean 36.5655 -> 37.8943; testimony rows 25628 -> 34450; buckets 17340/6882/1406 -> 24804/7392/2254.
- `test_self_placement_coverage_pins`: crew claims S9 660 -> 679, C9 1920 -> 2003, C4 89 -> 87. `test_the_completed_task_row_names_the_engine_truth_room`: completion rows S9 559 -> 417, C9 1731 -> 1331.
- `test_the_trail_s_budget_cost_is_measured_not_assumed`: (869, 5342, 0) -> (845, 5115, 0).
- `_REDERIVED_MEETINGS` S9 126 -> 123 and C9 369 -> 382; `_COMMITTED_MEETING_TOTAL` 672 -> 676; spoken transitions 1606 -> 1480. These are the recoverable meetings of the new sets.
- `test_the_origin_spoken_flags_stop_minting`: per-set [(20,37),(40,83)] -> [(24,35),(60,86)]; (60,120) -> (84,121); origin_strong 0 -> 23; (dissolved, survives) (59,1) -> (84,0); move-backed (11,0) -> (5,0).
- `test_the_price_of_the_lever_in_the_other_direction`: new flags [14,43,0,0] -> [0,10,0,0]; strong 6 -> 0; crewmate/impostor 48/9 -> 7/3; engine-true 10 -> 5; strong a-v-s off/on 21/27 -> 42/19.
- `test_the_grounded_off_leg_is_the_recorded_substrate`: strong_off 21 -> 42; strong_move 27 -> 19. `test_the_corridor_off_leg_is_the_recorded_substrate`: strong_off 21 -> 42.
- `test_the_grounded_lever_prices_the_prosecution_class`: strong_grounded [0,0,0,0] -> [1,5,0,0]; sides (0,0) -> (6,6); OFF subjects (20,1) -> (41,10); grounded subjects (0,0) -> (6,6); vent strong 453 -> 455.
- `test_the_grounded_lever_composed_with_the_movement_lever`: strong_both 2 -> 1; strong_grounded 0 -> 6; sides (2,1) -> (1,1); subjects (1,0) -> (1,1).
- `test_the_sole_flag_wrongful_ejections_lose_their_strong_flag`: (victims, impostors) (4,0) -> (1,1); crewmate victims 4 -> 0; still-strong 1 -> 0 `[owner review: vacuous, since the one sole-flag victim is an impostor]`.
- `test_i6_adjacent_room_strong_share_off_and_on`: OFF = ON [(0,7),(2,14),…] -> [(5,7),(24,35),…]; pooled (2,21) -> (29,42).
- `test_no_committed_prompt_carries_a_tagged_meeting_frame`: tagged rows 25628 -> 34450 (bare still 0).
- `test_the_coalesced_render_budget_cells`: snapshots 869 -> 845; rows 31797 -> 32037; mean 36.5903 -> 37.9136; sightings 16574 -> 12771; covered 26275 -> 20629; chars 3044260 -> 3162472.
- The same file's constants: `_COMMITTED_OFF_MEAN` 36.5655 -> 37.8943 and `_COALESCED_ROW_PIN` 36.5903 -> 37.9136.
- The two left-red tests keep their measured halves: `test_the_instrument_and_the_detector_read_one_adjacency_rule` kept 2 -> 29, and `test_the_band_change_not_the_fold_is_what_costs_first_hand_coverage` fold-only rows 31702 -> 32123, covered 29894 -> 28359.

#### tests/eval/test_funnel.py
- `test_funnel_reproduces_report_meeting_count`: 141 -> 135 body-report meetings.
- `test_funnel_reproduces_oracle_stage`: mean 2.83 -> 2.82; killer_in_set 127 -> 120; pm1 mean 2.23 -> 2.25; singleton_pm1 38 -> 33; unique_killer_pm1 33 -> 27; le2_pm1 89 -> 85.
- `test_funnel_reproduces_possession_stage`: vent_witnessed 97 -> 95; killer_at_scene 32 -> 35; last_seen_with_killer 44 -> 39; hard_clue_held 115 -> 112.
- `test_funnel_reproduces_transmission_stage`:
  - vent_mentioned 61 -> 71; vent_meetings 97 -> 95; report_ejections 85 -> 80;
  - outside-small-set votes 18 -> 14; small-set ejections 54 -> 51;
  - structured vent 64 -> 69; killer placement 26 -> 22; killer_accused 98 -> 86.

#### tests/eval/test_funnel_pooling.py
- `test_9p2i_pooling_reads_the_live_roll_call_channel`: meetings 151 -> 145; claims 766 -> 789; coverage 0.8659 -> 0.8674; lies detected 26 -> 8 (rate 0.0339 -> 0.0101).
- `test_9p2i_pooling_reproduces_baseline_5_exactly`: vouch 868 -> 824 (rate 0.5974 -> 0.5540); grounded 0.5170 -> 0.4760; share 0.8635 -> 0.8609; absence mean 0.3179 -> 0.3862; histogram {0:103,1:48} -> {0:90,1:54,2:1}; per_meeting 151 -> 145.
- `test_4p1i_pooling_reproduces_baseline_5_exactly`: claims 85 -> 81 (coverage 0.7179 -> 0.6838); vouch 58 -> 62 (0.3419 -> 0.3846); grounded 0.1709 -> 0.1880; share 0.5 -> 0.4889; absence 0.6410 -> 0.7179; histogram {0:14,1:25} -> {0:11,1:28}.
- `test_9p2i_pooling_roll_call_breakdown_reproduces_baseline_5`:
  - placed crew 651 -> 635, impostor 106 -> 104 (coverage 0.4536 -> 0.4655);
  - opening/reply/opt-in 153/79/534 -> 157/69/563;
  - asked/answered 869/757 -> 845/739.
- `test_4p1i_pooling_roll_call_breakdown_reproduces_baseline_5`: impostor placed 6 -> 2 (0.1538 -> 0.0513); reply 9 -> 4; opt-in 37 -> 38; answered 84 -> 80 (0.7179 -> 0.6838).

#### tests/eval/test_gate_metrics.py
- GZIP: `_COMMITTED_FLAT_REPORT`/`_COMMITTED_9P2I_REPORT` = `report_path(…)`; the reads go through `read_report_text`/`load_report`.
- `test_committed_9p2i_report_pins_the_audited_gate_metrics`:
  - supplied 75 -> 74, converted 69 -> 70; witnessed vent 73/68 -> 74/70; whereabouts lie 2/1 -> 1/0;
  - accused-impostor events 132 -> 122, survivals 51 -> 42, rendered_met 18 -> 16, unevidenced 33 -> 26.
- `test_committed_flat_4p1i_report_pins_the_gate_metrics`: events 33 -> 37; survivals 13 -> 17; rendered_met 3 -> 4; unevidenced 10 -> 13.

#### tests/eval/test_gate_spec_metrics.py
- GZIP: `_COMMITTED_9P2I_REPORT = report_path(…)`, read through `read_report_text`.
- `TestCommittedW2GateSpecPins::test_multi_signal_conversion_reads_18_of_64`: impostor ejections 82 -> 81; multi 27 -> 22; single 55 -> 59. The name keeps its history.
- `…::test_supply_gauges_read_the_corrected_instrument`:
  - meetings 151 -> 145; flags 57 -> 17 (weak 50 -> 11, strong 7 -> 6); zero-contradiction 126 -> 135;
  - genuine subject 7 -> 4; subjects crew/impostor 50/7 -> 13/4; accused meetings 118 -> 111; over-gate rows 432 -> 421.

#### tests/eval/test_kill_craft.py
- `test_corpus_kill_counts_and_histograms`: kills 532 -> 550; crew_witnessed 18 -> 16; co_present {0:532} -> {0:550}; one_hop 0-3 234/126/110/57 -> 249/131/111/54.
- `test_corpus_means_and_correlations`: mean one-hop witnessed 1.8333 -> 1.6875, unwitnessed 0.9844 -> 0.9551; point-biserial one-hop 0.1409 -> 0.1146.
- `test_samples_9p2i_fold1`: kills 182 -> 175; one_hop 0/1/3 79/43/15 -> 76/41/13; mean unwitnessed 1.0279 -> 1.0233; point-biserial 0.1452 -> 0.1491.
- `test_samples_4p1i_fold1`: kills 62 -> 66; one_hop 0/1 46/15 -> 49/16; mean unwitnessed 0.2623 -> 0.2615; point-biserial 0.1932 -> 0.1886.
- `test_corpus_entropy_crew_cells`: decisions 18707 -> 18867; mce 0.7686 -> 0.7802; mue 1.0967 -> 1.1050.
  - none|solo decisions 6700 -> 6838: do_task 4040 -> 4094, move 1930 -> 1987, repair 34 -> 39, report 305 -> 314, wait 383 -> 396; entropy 1.4465 -> 1.4572.
- `test_corpus_entropy_impostor_cells`: decisions 5584 -> 5748; mce 0.6108 -> 0.6224; mue 1.9217 -> 1.9237.
  - ready|pair decisions 743 -> 819: kill 652 -> 673, move 72 -> 122, sabotage absent -> 1, vent 17 -> 21; entropy 0.6394 -> 0.8105.
- `test_samples_9p2i_entropy`: crew 6060 -> 5886 (mce 0.7681 -> 0.7648, mue 1.0859 -> 1.0856); impostor 1826 -> 1754 (0.6147 -> 0.6226, 1.9132 -> 1.8912).
- `test_samples_4p1i_entropy`: crew 1373 -> 1417 (0.6437 -> 0.6485, 1.0696 -> 1.0700); impostor 536 -> 558 (0.5301 -> 0.5336, 1.7000 -> 1.6837).

#### tests/eval/test_meeting_quality.py
- GZIP: `_COMMITTED_9P2I_REPORT`/`_COMMITTED_4P1I_REPORT` = `report_path(…)`; four reads through `read_report_text`.
- `test_committed_9p2i_recompute_pins_the_coerced_bucket`, stored: missed_skip 80 -> 77, threshold_inversions 37 -> 27, impostor voters 42 -> 48.
- Same test, recomputed:
  - ejections 95 -> 90 (impostor 82 -> 81); accused 118 -> 111, converted 82 -> 81;
  - skip 342 -> 349, correct 262 -> 272, missed 80 -> 77, invalid_target 1 -> 2.
- `test_committed_4p1i_recompute_has_no_coerced_and_is_unchanged`: skip 66 -> 68; correct 53 -> 54; missed 13 -> 14; impostor voters 10 -> 8; inversions 3 -> 6; ejections 24 -> 20.
- `test_committed_recount_pins_the_by_cause_table`: the 9p2i param 37/37/5/30/7/0/28/1/8 -> 27/27/9/22/5/0/26/0/1, and the 4p1i param 3/3/0/3/0/0/3/0/0 -> 6/6/0/4/2/0/6/0/0.

#### tests/eval/test_off_menu.py
- `test_samples_four_all_on_menu` / `…nine…` / `test_corpus_four…` / `…nine…`: impostor decisions 536 -> 558, 1826 -> 1754, 526 -> 531, 5584 -> 5748. off_menu stays 0 everywhere.

#### tests/eval/test_replay_walk.py
- FIXTURE: `test_retired_lever_stamp_check_is_an_option` and `test_funnel_profile_bites_a_retired_lever_stamped_off` tamper through a new `_restamp` helper that rewrites every row carrying the stamp (row 0 and the footer). A footer-only tamper is now refused as a contradiction.
- RESTATED: `test_a_prefix_stamped_with_a_retired_lever_off_is_refused`: the precondition "substrate_flags not in the first row" (committed bytes stamped only the footer) -> "row 0 carries the footer's factory kind and substrate stamp". The `agent_factory_kind` plant is dropped because row 0 now carries it.

#### tests/eval/test_report_io.py
- PLANTED: new module (134b10de) for the gzipped report. It covers determinism (no mtime or filename in the header; identical bytes twice), the exact round trip and streaming. Its failure cases: a missing archive raises, an unconverted legacy `.json` is named rather than read, and a tampered archive decompresses to different bytes.

#### tests/eval/test_report_schema.py
- GZIP: `test_a_committed_report_whose_clock_is_a_json_boolean_is_refused` reads samples/4p1i through `read_set_report_text`. This alone fixed it; no value moved.

#### tests/eval/test_reporter_justice.py
- `test_the_meeting_census`: meetings 672 -> 676; body-report 620 -> 623; emergency 52 -> 53. `test_the_reporter_is_a_crewmate_in_every_body_report`: 620 -> 623.
- `test_the_ejection_ledger_reproduces_the_records_published_totals`: ejections 429 -> 411; innocent 46 -> 42; impostor 383 -> 369. These reproduce audit §4.1 row 9 and §6.2.
- `test_the_reporters_share_of_the_innocent_ejections`: reporter 34 -> 37, all innocent; share 34/46 -> 37/42.
- `test_the_per_slot_rates_and_the_relative_risk`: reporter (34,620) -> (37,623); innocent non-reporter (12,1859) -> (4,1841); impostor (331,856) -> (318,863); relative risk 8.495 -> 27.334.
- `test_speech_shares`: impostor (520,739) -> (553,771), crew (521,2129) -> (582,2228). `test_ballot_shares`: crew (160,2479) -> (239,2464), impostor (103,856) -> (108,863).
- `test_the_exculpation_is_rendered_far_more_often_than_it_is_used`: rationales 3335 -> 3327, mentioning 82 -> 61, hinge 13 -> 7. Speech turns 3335 -> 3327, mentioning 309 -> 296, hinge 5 -> 8, by reporter 1 -> 0.
- `test_the_split_by_role`: meetings 118 -> 122; crew/impostor slots 74/71 -> 72/76; slots 145 -> 148.
- `test_the_render_names_every_headline_cell`: "body report 620" -> "623", "34 reporter (… 73.9% …)" -> "37 reporter (37 … 88.1% …)", "34/620" -> "37/623", "12/1859" -> "4/1841", "71 IMPOSTOR" -> "76 IMPOSTOR".
- RE-ANCHOR: `test_an_undefined_relative_risk_is_never_reported_as_zero`: `_SETS[1]` -> `_SETS[3]` (ml_corpus/4p1i); reporter ejections 4 -> 1. samples/4p1i no longer ejects an innocent.
- RE-ANCHOR: `test_no_innocent_ejection_of_either_kind_reads_as_undefined`: `_SETS[3]` -> `_SETS[1]` (samples/4p1i). ml_corpus/4p1i now ejects one innocent.

#### tests/eval/test_solvability.py
- `test_samples_9p2i_cells`:
  - body meetings 141 -> 135; ejections 85 -> 80; killer_in_set (127,141) -> (120,135);
  - singleton (26,141) -> (21,135), correct (21,26) -> (16,21); at_most_two (52,141) -> (46,135), contains (45,52) -> (39,46);
  - cleared (16,85) -> (12,80); last-kill anchor (132,141) -> (129,135).
- `test_samples_4p1i_cells`: ejections 21 -> 17; cleared (0,21) -> (0,17).
- `test_corpus_9p2i_cells`:
  - body 407 -> 416; ejections 249 -> 241; killer (358,407) -> (368,416);
  - singleton (55,407) -> (52,416), correct (52,55) -> (49,52); at_most_two (133,407) -> (127,416), contains (111,133) -> (107,127);
  - cleared (47,249) -> (50,241); last-kill (386,407) -> (391,416).
- `test_corpus_4p1i_cells`: ejections 22 -> 21; cleared (0,22) -> (0,21).
- `test_pooled_denominators_and_headline_cells`:
  - body 620 -> 623; ejections 377 -> 359; killer (557,620) -> (560,623);
  - singleton (90,620) -> (82,623), correct (82,90) -> (74,82); at_most_two (194,620) -> (182,623), contains (165,194) -> (155,182);
  - cleared (63,377) -> (62,359); last-kill (590,620) -> (592,623).

#### tests/eval/test_validity.py
- `test_meeting_rate_passes_on_committed`, `test_no_duplicate_meeting_rows_passes`, `test_run_validity_gate_reproduces_9p2i_close`: resolved meetings 151 -> 145.

#### tests/eval/test_vj_instruments.py
- `test_9p2i_zero_flag_channel_pins`:
  - meetings 151 -> 145; convictions 95 -> 90; zero-flag 20 -> 18 (crew 7 -> 8, impostor 13 -> 10);
  - typed split hard/soft/unattributed 2/17/1 -> 5/9/4; proxy split hard/soft/sub-gate 6/8/6 -> 10/3/5.
- `test_9p2i_soft_hard_split_cross_checks`: provenance and rendered rows 3819 -> 3618; agreements 16 -> 13; disagreements 4 -> 5.
- `test_9p2i_j1_clamp_exempt_rows_pinned`: rows 3819 -> 3618. exempt_rows [] -> three rows, seed 19 meeting 3, voters p-3, p-4 and p-5 on p-1. The census refilled, and each row was checked as a by-design clamp.
- `test_9p2i_citation_compliance_pins`:
  - ballots 869 -> 845; skip 342 -> 349; eject 527 -> 496; turn citations 474 -> 478; obs citations 150 -> 235;
  - cited eject 526 -> 496 (compliance 526/527 -> 496/496); nulled reason/obs 1/3 -> 0/0.
- `test_9p2i_ballot_calibration_pins_the_baseline_5_cell`: total 527 -> 496; ECE 0.1615 -> 0.1461; Brier 0.1913 -> 0.1752.
- `test_9p2i_voice_tier_pins`:
  - ballots 869 -> 845; guard-excluded 2 -> 1; voice 867 -> 844; echo 2 -> 0; skeleton share 0.0150 -> 0.0130;
  - distinct skeletons 850 -> 830 (ratio 0.9804 -> 0.9834); distinct_1 0.0990 -> 0.0985; distinct_2 0.3481 -> 0.3422.
- `test_9p2i_pooling_rides_the_same_report`: whereabouts 766 -> 789; vouch 868 -> 824; per_meeting 151 -> 145.
- `test_4p1i_reproduces_baseline_5_exactly`:
  - convictions 24 -> 20; zero-flag 5 -> 1 (crew 4 -> 0); hard/unattributed/no-row 2/1/1 -> 0/0/0; agreements 4 -> 0;
  - rendered rows 133 -> 137; valid turn citations 44 -> 47; cited eject 51 -> 49;
  - ECE 0.1216 -> 0.0939; Brier 0.1149 -> 0.0971; skeletons 117 -> 115 (ratio 1.0 -> 0.9829).
- `test_per_meeting_rows_pair_voice_with_judgment`: ejected rows 95 -> 90.
- `test_cli_vj_json_emits_the_machine_readable_report`: convictions 24 -> 20, zero-flag 5 -> 1, whereabouts 85 -> 81.
- `test_cli_vj_human_render_names_the_gauges`: "5/24" -> "1/20".
- `test_cli_vj_human_render_publishes_a_nonzero_exclusion`: "excluded 2" -> "1", still nonzero; "echo 2/867" -> "echo 0/844".
- RE-ANCHOR: `test_ballot_calibration_matches_the_committed_fold` reads `_CORPUS_NINE` (ml_corpus/9p2i) instead of the `four` fixture. samples/4p1i no longer drops a guard-authored ballot; ml_corpus/9p2i is the only set that does (1 of 1487). The assertions are unchanged.

#### tests/eval/test_vote_correctness.py
- GZIP: `_COMMITTED_9P2I_REPORT`/`_COMMITTED_FLAT_4P1I_REPORT` = `report_path(<set>)`; seven reads through `read_report_text`.
- `test_committed_9p2i_report_pins_the_audited_conversion_values`: ejections 95 -> 90 (impostor 82 -> 81, accuracy 81/90); accused 118 -> 111, conversions 82 -> 81.
- Same test: skip 342 -> 349, correct 262 -> 272, missed 80 -> 77 (impostor voters 42 -> 48, invalid_target 1 -> 2, inversions 37 -> 27); vote_correctness 75/82 -> 76/81; the raw JSON pins follow.
- `_UNBACKED_9P2I`: 7 rows -> 5, namely (6,m3,t43,p-9), (27,m1,t15,p-7), (38,m3,t25,p-4), (40,m2,t15,p-9) and (47,m0,t7,p-1). These are the unbacked impostor ejections on the new bytes.
- `_KILL_WITNESS_ONLY_9P2I`: 6 rows -> 5, namely (14,m0,t7,p-1), (17,m3,t29,p-4), (25,m2,t18,p-6), (26,m0,t6,p-3) and (44,m0,t10,p-5).
- `test_committed_9p2i_censuses_the_unbacked_impostor_ejections`: 82 -> 81; backed 75 -> 76. `…_zero_flag_population_is_wider_than_the_unbacked`: 13 -> 10.
- `test_committed_9p2i_unbacked_ejections_are_all_rhetoric_only`: rhetoric-only 7 -> 5; detector misses stay 0. The property was re-verified on the five.
- `test_committed_9p2i_report_pins_the_successor_instrument`: supplied 75 -> 74; converted 69 -> 70; witnessed vent 73/68 -> 74/70; whereabouts lie 2/1 -> 1/0.

#### tests/eval/test_watchability.py
- `test_baseline_8_floor_pins_equal_the_measured_bytes` -> `test_baseline_9_floor_pins_equal_the_measured_bytes`, which reads baseline-9. Every gauge still equals its floor.
  - 9p2i: 3/182 -> 3/175, 147/151 -> 107/145, 81/128 -> 79/112, 57/151 -> 17/145, 90/151 -> 90/145.
  - 4p1i: 1/62 -> 1/66, 20/33 -> 20/37.
- `test_witnessed_event_rate_is_the_measured_anchor`: 3/182 -> 3/175.
- `test_hardened_patches_fire_on_the_committed_9p2i_bytes`: live-only floored {19} -> {5, 19}; patch1_zeroed set() -> {4, 10, 39, 46}.
- `test_cli_watchability_json_emits_per_game_and_aggregate`: baseline_id baseline-8 -> baseline-9; mean 48.57 -> 47.85.
- RESTATED: `test_historical_15_2_geomean_parity_frozen_pin_on_9p2i`.
  - The fixture git_head != manifest sha becomes == (the rubric was regenerated, 83148aa6).
  - Parity is restored on every column except floor/score: the lab fixture floors all 50 games (mean and median 0.0).
  - This module's mean 50.18 -> 50.54 and median 56.25 -> 50.7; floored 7 games -> exactly {6, 12, 13, 38, 39}.

#### tests/eval/test_watchability_reanchor.py
- `test_fsm_baseline_sets_pass_at_exact_equality_under_the_reanchor`: expected 81/128 and 20/33 -> 79/112 and 20/37.
- `test_remeasured_corpus_sets_at_baseline6_referee_verdicts`: C9 witnessed 0.03383 -> 8/275; flags 1.0228 -> 374/449; conversion 0.6451 -> 78/125.
  - The derived floor 0.6117 -> 0.7511, and conversion passed True -> False `[owner review: verdict flip; "C9 fails, C4 passes" holds]`.
  - C4 conversion 0.7436 -> 9/13, floor 0.1825 -> 0.1890.

#### tests/eval/test_wave2_metrics.py
- `test_committed_w2_reads_64_of_179`: impostor ejections 82 -> 81 and resolved 151 -> 145, so 82/151 -> 81/145.
- `test_committed_w2_reproduces_the_audit_subcount`: events/survivals/active/named/third/effective/skip-saved 132/51/50/18/20/38/12 -> 122/42/40/15/10/25/15.
- `test_committed_w2_tasks_fingerprint_closed`: do_task impostor/crew 365/3021 -> 354/2987; wait share impostor 0.0987 -> 0.0952 and crew 0.0812 -> 0.0693. The "< 2x" property holds.
- `test_committed_bytes_exclude_the_discarded_and_tally_identically`: discarded_excluded 537 -> 530.

#### tests/experiments/test_gameplay_facts_suspicion_row.py
- PLANTED: new module (ee9c8dcf; formatted in 3eba9495). The gameplay extractor's suspicion-row pattern must parse both the trust-suffixed row and the trust-less row. The narrowed pre-fix pattern, kept in the test, must return nothing on the trust-less shape, which is the silent zeroing leg 1 hit.

#### tests/fixtures/baseline8_exhibits/
- FROZEN: new. It holds `seed-41-meeting-2.jsonl` (verbatim), `alibi-conflict-meetings.jsonl` (17 meetings, 21 flags, model calls emptied), `legacy-one-room-alibi-meetings.jsonl` (190 meetings, 292 legacy alibi payloads, model calls emptied), `rewritten-ballot-9p2i/` (seed 11 and roster, verbatim) and a README. The README has a snippet that rebuilds all five files byte for byte from `git show 39a568c6:…`, and the snippet was checked against the committed copies. `docs/artifacts.md` `tests/fixtures/` row: 2,098,348 tracked bytes / 29 files -> 4,064,349 / 35.

#### tests/fixtures/phase10/corrected_w2_baseline.json
- Regenerated by its producer, `scripts/build_sample_report.py --sample-dir replays/samples/9p2i --baseline-out …` (83148aa6), not hand-edited:
  - conversion 82/151 -> 81/145;
  - deflection 132/51/50/38/18/20/12 -> 122/42/40/25/15/10/15;
  - multi-signal 27/82 -> 22/81; impostor-ejection channel sites 82 -> 81.
- Supply gauges: meetings 151 -> 145, flags 57 (50w/7s) -> 17 (11w/6s), zero-contradiction 126 -> 135, genuine 7 -> 4, subjects 50/7 -> 13/4, accused 118 -> 111, over-gate rows 432 -> 421.
- Indistinguishability: do_task impostor/crew 365/3021 -> 354/2987; wait share 0.0987/0.0812 -> 0.0952/0.0693. `test_gate_spec_metrics` reads this fixture. No worker ledger lists this file; the commit message of 83148aa6 does.

#### tests/fixtures/prompt_archive/qwen3_6_27b_v5/
- RETIRED: the six archived v5 bodies are deleted (accusation_round, accusation_round_roll_call, crewmate_report, impostor_report, impostor_report_roll_call, vote_ballot). Every committed recording stamps the live set (v6 templates, v8 ballot).

#### tests/meetings/test_citation_relevance.py
- `TestGuardAndGraderCannotDisagree::test_every_committed_ballot_gets_one_verdict`: compared 578 -> 545.
- RESTATED: same test. `labelled.model_copy(label=None) == ballot` becomes both sides label-stripped. Baseline-9 ballots carry their record-time label (545/545), and 0 fields differ over 545.
- `…::test_the_collision_is_reachable_on_committed_bytes`: colliding 244 -> 212.

#### tests/meetings/test_contradictions.py
- GZIP: `_roles_by_seed` reads through `read_set_report_text`.
- `_COMMITTED_MEETINGS` 672 -> 676; `_MOVEMENT_CHANNEL_DIVERGENCES` 78 -> 69. `_MOVEMENT_CHANNEL_DIVERGING_MEETINGS`: 78 ids -> 69 ids (28 kept, 50 left, 41 new), all movement-sensitive.
- `test_the_divergences_are_the_movement_channel_and_nothing_else`: sensitive 462 -> 451.
- `_SAMPLES_9P2I_EXEMPT_BY_ROLE` {CREWMATE 15, IMPOSTOR 1} -> {CREWMATE 21}; `_BY_CLASS` {alibi 2, whereabouts 14} -> {whereabouts 21}; `_EXEMPT_FLAGS` 17 -> 22; `_SAMPLES_9P2I_REDERIVED` 131 -> 128.
- `test_samples_9p2i_cells`: meetings 151 -> 145.
- `test_the_committed_class_and_the_untouched_kinds`: a-v-s strong/weak 21/99 -> 42/79; a-v-p strong 13 -> 18, and a-v-p weak 7 returns; conflict weak 62 -> 3; vent 453 -> 455.
- `test_the_ungrounded_leg_convicts_on_nothing`: (0,120) -> (0,121). `test_the_env_legs_agree_on_every_committed_meeting`: off_matches samples/9p2i 126 -> 123, ml_corpus/9p2i 369 -> 382.
- `test_the_committed_class_prices_the_corridor`: strong (21,21) -> (42,42); weak (99,99) -> (79,79). Demoted is still 0.
- FROZEN: `_seed_41_entry` reads the frozen baseline-8 line of seed 41 meeting 2 instead of the committed corpus, where the meeting carries 0 flags now. `TestTheAlibiIsARoute` passes 6 of 6 (3 were red, and 2 green ones were running on a meeting that had lost its exhibit), and so does `test_the_honest_seed_41_route_still_mints_nothing`. One comment now says the meeting WAS a movement-channel diverging meeting on baseline 8.

#### tests/meetings/test_manager.py
- GZIP: `TestCommittedBytesLiftPins::test_no_crew_row_is_railroaded_to_certain_guilt` reads through `read_set_report_text`.
- `TestCommittedBytes107FoldPins::test_seed29_m0_pile_on_stop_pin`: folded_total 99 -> 103. voiceless_folds is still [].
- `…::test_seed29_m1_fold_lifts_listeners_over_gate_and_converts`: listeners_over_gate [] -> ["p-9"]. The example shows its titular shape again.
- `TestSingleWitnessInformYieldOnCommittedBytes::test_methodology_reproduces_the_audit_partition`: accused_not_ejected 51 -> 42; over_gate_lost_plurality 18 -> 16.
- `…::test_single_witness_inform_converts_fourteen_of_the_ninety_seven`: informed 9 -> 4; conversions ((26, seed-26 M0, p-3),) -> (). This is a whole-set census.
- `TestMarkerAndFieldAgree::test_the_committed_corpus_is_judged_rather_than_skipped`: seen 3631 -> 3630; judged 100 -> 21; judged meetings 70 -> 21. The retired rewrite reasons are gone.

#### tests/meetings/test_prompt_byte_golden.py
- RETIRED: `ARCHIVED_PROMPT_VERSION_SETS` {qwen3_6_27b_v5: …} -> {} and `ARCHIVED_MAP_CARDS` {qwen3_6_27b_v5: CANONICAL_MAP_CARD} -> {}. The bump-in-flight window closed at this record.
- RETIRED: `test_the_bump_in_flight_window_is_open_on_the_archived_v5_bodies` -> `test_the_bump_in_flight_window_is_closed_and_the_archive_is_empty`. The new test checks that the archive and card pairing are empty, no fixture dir exists, and every stamp equals the live mapping. The retired test was written to fail at this re-record.
- RETIRED: `test_one_byte_template_perturbation_breaks_the_golden`: the victim moves from the archived `qwen3_6_27b_v5/crewmate_report.j2` to the live `qwen3_6_27b/crewmate_report.j2`, because perturbing the archive would now be a no-op.
- `test_every_reconstruction_divergence_is_a_retired_guard`: 9p2i (151, 869, 23, 14) -> (145, 845, 0, 0); 4p1i (39, 117, 1, 1) -> (39, 117, 0, 0) `[owner review: the moved-ballot branch is unexercised on committed bytes]`.

#### tests/meetings/test_reported_testimony_derive.py
- FROZEN: `TestRoutesOverTheCommittedRecord`'s two helpers become `_legacy_meetings` and `_legacy_alibi_payloads`, over the 190 frozen baseline-8 sample meetings (292 one-room alibi payloads). The claim round trip, the served-view check and the reduction check read them. On baseline 9 all 1,021 committed alibis are routes. The whole-line round trip still reads the live sample sets. The assertions are unchanged, and the class is green.

#### tests/meetings/test_transcript.py
- `TestCommittedBytesArtifactCollapse._REPAIRED_SITES`: 11 sites / 15 flags -> {}. No recorded flag is removed on baseline 9. `test_rederivation_diverges_only_at_the_repaired_sites`: recorded/re-derived 54/60 -> 15/39. That test is still red.
- `test_surviving_endpoint_flags_are_weak_banded`: 50 -> 25.
- `test_recorded_conflict_flag_census`: 21 -> 0 `[owner review: the no-strong-conflict check now holds vacuously on samples/9p2i]`.
- `test_strong_flags_surface_under_the_wave_e_substrate`: strong 97 -> 96; weak 50 -> 11.
- `test_no_spawn_window_corroboration_survives_set_wide`: surviving 194 -> 246.
- `test_seed12_m0_derives_no_voice_for_bare_pile_on_p4`: set-wide multi-accuser list 37 rows -> 27 rows. The membership moved with the bytes.
- `test_seed16_m2_derives_two_voices_for_p4`: voices of p-9 ("p-8",) -> ("p-2","p-4","p-8"). The name keeps its history.
- FROZEN: `test_seed25_m0_weak_cross_speaker_conflict_not_retargeted` walks the 17 frozen baseline-8 meetings that hold the 21 `alibi_conflict` flags, instead of samples/9p2i seeds 0-49, which now carry none. It still asserts 21 recorded = 21 re-derived and no proxy-intra-turn marker, and it is green.

#### tests/meetings/test_vote_tally_parity.py
- `test_committed_corpus_counts_are_pinned`: meetings/ballots samples/9p2i 151/869 -> 145/845 and ml_corpus/9p2i 439/2516 -> 449/2539. `test_committed_corpus_totals_are_pinned`: 672/3631 -> 676/3630.
- `test_recorded_outcome_split_exercises_both_branches`: EJECTED 429 -> 411; SKIPPED 243 -> 265.
- `test_committed_guard_marker_counts_are_pinned[…]` (invalid_target / teammate_coerced / under_gate_redirect / invalid_reason_id / invalid_observation_id / uncited_zero_flag):
  - samples/9p2i 2/2/23/1/3/0 -> 3/1/0/0/0/0; samples/4p1i redirect 1 -> 0;
  - ml_corpus/9p2i 2/5/57/4/12/6 -> 5/12/0/0/1/0; ml_corpus/4p1i redirect 2 -> 0;
  - `[owner review: the retired families now read 0]`.
- `test_the_threshold_sweep_actually_moves_outcomes`: ejections at 0.0/0.25/0.5/0.6 429 -> 411, at 0.75 421 -> 405, at 0.9 351 -> 357, at 1.0 181 -> 214.

#### tests/orchestrator/test_experimental_evaluation_integrity.py
- GZIP: `test_candidate_partial_identity_reaches_current_report_and_api` writes through `write_report_text(report_path(…))`.

#### tests/orchestrator/test_public_account_scenario.py
- GZIP: `test_served_report_identity_is_bound_to_actual_recording` writes through `write_report_text(report_path(…))`.

#### tests/orchestrator/test_recording_fingerprint.py
- `test_committed_sets_keep_their_source_fingerprint`:
  - samples/9p2i sha256:85fb119e…d10 -> sha256:cde794abe57af44da0fd3e16652435b7b1af88aaf7310d495cf3108ae80cd09f;
  - samples/4p1i sha256:8bbf89bf…d14 -> sha256:2abab5c07eafb01c5efeef4d1234a77a6b57939a6923f3aee240349e0c0b1566;
  - these move in lockstep with `api/public_results._source_url`.

#### tests/orchestrator/test_replay.py
- `test_every_committed_tick_row_carries_its_dispositions`: rows 6064 -> 6110.

#### tests/orchestrator/test_substrate_binding.py
- FIXTURE: `test_api_profile_mismatch_is_a_controlled_integrity_refusal[testimony]` writes the planted ON on every stamped row, where it used to write only the footer. The refusal is substrate_version_mismatch, as intended.

#### tests/scripts/_goldens/champion_flip_ruling.json (and test_champion_flip_ruling.py)
- The golden is regenerated by `scripts/regen_test_goldens.py`: fsm_comparator_win_rate 0.3 -> 0.22; utility-es win_edge 0.22000000000000003 -> 0.30000000000000004; policy-es -0.27999999999999997 -> -0.2. The 9p2i impostor rate is 11/50; the docstring follows.

#### tests/scripts/test_build_demo_bundle.py
- `test_rubric_is_trimmed_to_the_baked_seeds`: baked stale True -> False; baked per_game [] -> [seed 2], with 50 live rows. The rubric was regenerated fresh.
- `test_summary_covers_full_validated_set_but_links_only_baked_cases`: baked seeds (23, 46) -> (0, 23, 29). These are the games that carry the three re-curated cases.

#### tests/scripts/test_build_sample_report.py
- GZIP: `_COMMITTED_REPORT = report_path(…)`; every read and write goes through report_io; the staleness message names `.json.gz`.
- RESTATED: new `_legacy_shaped`/`_legacy_shaped_report` clear the recorded-identity cells and assert projectability. Four tests use them:
  - `test_historical_serialization_preserves_real_attempt_ids`;
  - `…_preserves_existing_cells_and_omits_added_metadata`;
  - `test_current_serialization_cannot_hide_recorded_identity_as_legacy` (7 params);
  - `test_write_report_emits_the_shape_check_compares[legacy]`, which now writes one stripped 9p2i game and compares it with `historical_report_payload`, where it used to rebuild the committed legacy 4p1i report;
  - reason: every committed report is now identity-stamped, so none is projection-eligible, and the historical-projection branch has no committed consumer left.

#### tests/scripts/test_check_doc_facts.py
- GZIP (134b10de): the copied-file list and `_EVAL_REPORT_9P2I/_4P1I` name `.json.gz`.
- GZIP (5d3b7a60): `_read`/`_write` go through report_io for the archive; `_trigger_report` and `test_a_report_without_a_coverage_block_fails_loud` write `REPORT_FILENAME` gzipped.
- FIXTURE: `_COPIED` adds audits/audit-2026-09-22-process-rerecord.md and drops audits/audit-phase-20-baseline-7.md, which is no longer read.
- Record constants:
  - `_PROOF_AUDIT` audit-phase-20-baseline-7.md -> audit-phase-21-rerecord.md, with that record's heading and pooled rows (61/103 | 50/96; 42 | 46; 333/333);
  - `_LADDER_TIP_AUDIT` -> audit-2026-09-22-process-rerecord.md, with new `_TIP_*` rows (50/96 | 43/85; 46 | 42; 326/326) and `_FINDING_BASE_AUDIT`.
- `_PREVIOUS_PARTITION_CELL` "326 / 326 vs 61 / 103" -> "333 / 333 vs 50 / 96"; `_FLAGGED_ROW` yes (68) 68|0 -> yes (70) 70|0; `_UNFLAGGED_ROW` no (83) 14|13 -> no (75) 11|9; `_BASELINE_LINK`/`_BEFORE_COLUMN_LINK` baseline 7 -> 8.
- Refresh dates 2026-08-31 -> 2026-09-22 in eight tests: `test_stale_sample_date_detected`, `test_paragraph_date_drift_…`, `test_duplicate_stale_date_…`, `test_missing_provenance_…`, `test_repeated_claims_…`, `test_stale_guide_record_date_…`, `test_unnumbered_guide_record_date_…` and `test_main_reports_every_failure_at_once`. The guide records "reference recording 8" -> "9".
- Win rate 30% -> 22% and "15/50 = 30%" -> "11/50 = 22%" in six tests: `test_stray_win_rate_…`, `test_in_paragraph_stale_…`, `test_stale_guide_win_rate_…`, `test_stale_ml_page_win_rate_…`, `test_before_column_win_rate_…` and `test_repeated_claims_…`. The stale claim flagged is now 30%.
- Prompt and ladder tip: `test_wrong_prompt_set_version_detected` 'v5' -> 'v6'. Ladder tip baseline 8 -> 9 in `test_stale_ladder_tip_…`, `…_without_baseline_…`, `test_audits_index_…`, `test_glossary_…`, `…_predating_the_substrate_…` and both `…corpus_disclosure_…substrate…` tests; the relabel goes 9 -> 10.
- Vote-correctness stamps: `test_vote_correctness_stamp_drift_detected` 75/82 = 0.9146 -> 76/81 = 0.9383 (drift 74/82 -> 75/81); `test_structural_pin_prose_detected` "(75/82)" -> "(76/81)"; `test_eval_report_rate_drift_detected` rate 0.9146341463414634 -> 0.9382716049382716.
- More stamp tests: `test_vote_correctness_baseline_attribution_drift_detected` baseline-8 -> baseline-9; `test_zero_impostor_ejection_set_wants_an_undefined_rate_stamp` 4p1i crewmate_ejections 4 -> 0; `test_evidence_count_above_its_denominator_fails_loud` evidence_backed 75 -> 76.
- Citation "526 / 527" -> "496 / 496" (drift "525 / 526" -> "495 / 496"; before-column "538 / 538" -> "526 / 527") in `test_citation_figure_derived_from_the_committed_instrument`, `test_instrument_pin_move_reaches_the_front_door`, `test_moved_figure_quoted_without_its_baseline_stamp_detected` and `test_before_column_drift_between_the_two_tables_detected`.
- Vent headline '68 / 82 = 83%' -> '70 / 81 = 86%' (drift '60 / 74 = 81%' -> '60 / 71 = 85%') in `test_vent_headline_derived_from_the_crosstab`. `test_swapped_vent_crosstab_labels_detected`: '14 / 82 = 17%' -> '11 / 81 = 14%', and the 'yes' row 14/13 -> 11/9.
- Vent rows: `test_mislabelled_vent_crosstab_row_fails_loud` and `test_vent_row_without_its_population_fails_loud` label (68) -> (70); `test_guide_crosstab_row_label_held_to_the_pins` label-drift 70/68 -> 72/70.
- Cross-tab prose: `test_unpinned_crosstab_fails_loud` and `test_contradicting_crosstab_pins_fail_loud` 151 -> 145; `test_stale_guide_crosstab_prose_detected` "all 151" -> "all 145".
- Ballot and ratio prose: `test_stale_guide_ballot_prose_detected` and `test_deleted_guide_narrative_fails_loud` 527 -> 496 eject ballots; `test_stale_guide_no_proof_ratio_detected` and `test_deleted_guide_no_proof_ratio_fails_loud` 14 of 27 -> 11 of 20 (drift 15 -> 12).
- Partner ballots: `test_stale_partner_ballot_denominator_detected` 0 of 218/217 -> 0 of 210/209; `test_guide_only_row_losing_its_before_cell_detected` and `test_truncated_row_losing_its_before_cell_detected` "0 of 218 | 0 of 219" -> "0 of 210 | 0 of 218".
- "At baseline 7" -> "At baseline 8" in `test_unlinked_dialect_term_detected`, `test_repeated_results_claim_detected`, `test_moved_figure_quoted_…`, `test_dropped_before_column_fails_loud` and `test_guide_only_row_…`; `test_missing_win_split_table_fails_loud` header baseline-7 -> baseline-8.
- Corpus disclosure: `test_corpus_disclosure_coverage_cell_drift_detected` 651/651 -> 635/635; `…_stale_duplicate_cell_detected` 292/636 -> 298/651; `…_meeting_total_drift_detected` 672/672 -> 676/676.
- Report example: `test_report_example_ejection_count_drift_detected` 95 -> 90; `…_rate_drift_detected` 0.915 -> 0.938; `…_accuracy_drift_detected` 0.863 -> 0.900.
- `test_proof_partition_derived_from_the_previous_record`: the perturbed cell 318/326 -> 325/333, and the expected text '325 / 333 = 0.9760 vs 50 / 96 = 0.5208'.
- `test_published_partition_derived_from_the_record`: 53/96 -> 46/85, expected '326 / 326 vs 46 / 85 = 0.5412'. `test_record_direct_proof_cell_reaches_the_front_door`: 332/333 -> 325/326, expected '325 / 326 = 0.9969 vs 43 / 85 = 0.5059'.
- Headings: `test_missing_record_bar_fails_loud` and `test_missing_previous_record_bar_fails_loud` follow the renamed record headings.
- `test_record_innocent_bar_reaches_the_front_door` now perturbs the record's pooled 42 -> 40 in `_TIP_INNOCENT_POOLED`; it used to perturb baseline 8's 46 -> 40. `test_previous_record_pooled_row_read_by_label_not_position` row "23 | 14" -> "14 | 13". `test_swapped_previous_record_columns_detected`: now 50/96 vs 61/103, expected "333 / 333 vs 61 / 103".
- `test_previous_record_innocent_total_drift_detected` 79/44 -> 42/44 (message "61/103" -> "50/96"). `test_renamed_previous_record_pooled_row_fails_loud` 79/42 -> 42/46.
- `test_innocent_ejections_moved_to_the_wrong_cell_detected` "46 of 46" -> "42 of 42". `test_wrongful_ejection_count_inside_a_longer_number_detected` "(46)" -> "(42)".
- `test_history_cell_naming_the_recording_before_the_previous_one_detected`: the b7 cell "310/310 vs 46/125" -> "326/326 vs 61/103", recomputing to "333/333 vs 50/96".
- Exhibits: `test_guide_exhibit_the_picker_no_longer_carries_detected` and `test_guide_exhibits_follow_a_recurated_picker` seed 46 -> 29; `test_guide_with_too_few_exhibits_fails_loud` now strips seeds 0, 29 and 4p1i 11.
- RESTATED: `test_stale_sample_date_detected` also restores the new audit's file-name link, whose name contains the date, so the perturbation stays about date claims.
- RESTATED: `test_partition_innocent_total_contradicting_its_own_accuracy_detected`:
  - the pooled row is now `_TIP_INNOCENT_POOLED`, with drift 41, and the message reads 43/85;
  - the stale set drops the ML page, which narrates only baseline 8's 46.
- RESTATED: `test_finding_history_cell_disagreeing_with_the_ladder_tip_detected` -> `…_with_its_base_record_detected`, asserting `_FINDING_BASE_AUDIT`. The finding is read against baseline 8, no longer against the tip.
- PLANTED: five new tests for the per-row prompt-stamp invariant:
  - `test_committed_two_version_prompt_set_is_one_substrate`;
  - `test_one_set_on_a_different_prompt_stamp_fails_loud`;
  - `test_one_row_on_a_different_prompt_stamp_fails_loud`;
  - `test_one_row_on_a_subset_of_the_prompt_tokens_fails_loud`;
  - `test_lead_in_naming_one_of_two_prompt_tokens_fails_loud`.

#### tests/scripts/test_counterfactual_phase21.py
- `test_the_baseline_8_tripwire_readings` -> `test_the_baseline_9_tripwire_readings`:
  - T-9a on [2023,2023] -> [2011,2011]; T-9b on [0,936] -> [0,943]; T-9 denominator 2959 -> 2954;
  - B-1m1 [68288,3368] -> [68305,3369]; P-1k [0,96] -> [0,85] and the P-1 denominator 96 -> 85.
- `test_the_block_level_cells_equal_the_byte_cells_on_the_committed_bytes`: R-13 [620,620] -> [623,623]; R-14 [2715,2715] -> [2704,2704]; C-9 [3614,3631] -> [3628,3630]. on == byte_diff still holds.
- `test_a_reconstruction_that_misses_the_record_refuses`: the cited record audits/audit-phase-21-rerecord.md -> audits/audit-2026-09-22-process-rerecord.md. The script's refusal now cites §6.2 of this record (948abae1), and the test followed in f4961ad1.

#### tests/scripts/test_manifest_writer.py
- `test_provenance_meeting_seed`: accusation_round .v5 -> .v6 and vote_ballot .v5 -> .v8.
- `test_rebuild_writes_sorted_rows` (row 22) and `test_rebuild_real_samples_have_50_rows`: accusation_round .v5 -> .v6. The baseline-9 manifests stamp the v6 templates and the v8 ballot.

#### tests/scripts/test_measure_baseline_cli.py
- `test_9p2i_reproduces_baseline_8_exactly` -> `…baseline_9_exactly`:
  - r1 35 -> 38; histogram {EJECT 35, PARITY 15} -> {EJECT 38, PARITY 11, TASKS 1};
  - ejections 95 -> 90 (impostor 82 -> 81, crew 13 -> 9);
  - supplied/converted 75/69 -> 74/70; wins 35/15 -> 39/11 (0.30 -> 0.22); resolved 151 -> 145.
- `test_4p1i_reproduces_baseline_8_exactly` -> `…baseline_9_exactly`: ejections 24 -> 20; crew 4 -> 0; accuracy 20/24 -> 20/20.
- `test_historical_win_census_does_not_certify_recorded_outcomes`: (35, 15) -> (39, 11); 15/50 -> 11/50.
- `test_default_measures_both_canonical_sets`: "35/50" -> "38/50"; "82 impostor / 13 crew of 95" -> "81 / 9 of 90"; canary "0.92 (69/75)" -> "0.9459 (70/74)".
- `test_json_emits_array_of_reports`: 81/90, EJECT 38, r1 38, supplied 74. `test_explicit_dir_measures_one_set`: 20/24 -> 20/20.
- `test_solvability_human_rendering`: 141/85 -> 135/80 body meetings and ejections; killer 0.9007 (127/141) -> 0.8889 (120/135).
  - Singleton 26/141 -> 21/135, correct 21/26 -> 16/21; at most two 52/141 -> 46/135; cleared 16/85 -> 12/80; last-kill 132/141 -> 129/135.
- `test_solvability_json_emits_array`: body 141 -> 135; ejections 85 -> 80; killer 127 -> 120; singleton_correct 21/26 -> 16/21, Wilson [0.5491, 0.8937].
- `test_honesty_human_rendering`:
  - meetings 151 -> 145; clock 2984 -> 2996; I-2 6/660 -> 5/679; I-3, I-4 and I-6 go to None (0/0);
  - I-5 0/311 -> 0/271; I-7 0/30 -> 0/8; I-8 0/869 -> 0/845; I-9 0/1740 -> 0/1694; I-10 27/151 -> 29/145;
  - I-11 8/237 -> 9/232; ghost-top 3/1826 -> 5/1754; budget 36.57 -> 37.89.
- `test_honesty_json_emits_array`: clock 2984 -> 2996; crew_false 6 -> 5; marker (0,1740) -> (0,1694); kill decisions and reproduced 229 -> 223.

#### tests/scripts/test_measure_featured_criterion.py
- `test_alternatives_shape_reads_the_committed_duplicates`: seed 2 (7,13,2,0) -> (7,9,1,0); seed 13 (18,35,1,2) -> (7,10,1,0); seed 23 (26,36,0,0) -> (26,29,0,0). No committed ballot in any of the four sets lists its own target now.

#### tests/scripts/test_process_scorecard.py
- GZIP (134b10de): `test_a_missing_published_file_is_red_rather_than_absent` lists `replays/ml_corpus/9p2i/tournament-eval-report.json.gz`.

#### tests/scripts/test_validity_gate_cli.py
- RETIRED: `test_expected_prompt_versions_fails_a_homogeneous_wrong_pin`: the wrong pin `.replace(".v5", ".v4")` -> `.replace(".v6", ".v5").replace(".v8", ".v7")`. The `_locked_pin` docstring is restated. With the archive empty, `_locked_pin()` reads the live v6/v8 registry, so the old substitution was a no-op.

#### tests/training/test_conviction_model.py
- `test_sample_conversion_census_pins`: samples/9p2i meetings 151 -> 145, attempts 128 -> 112, conversions 81 -> 79; samples/4p1i attempts 33 -> 37.
- `test_corpus_census_pins`: meetings 439 -> 449; ejections 281 -> 273; flags 449 -> 374 (317 vent + 57); attempts 386 -> 375; conversions 249 -> 234; fit-side rows 348 -> 355.

#### tests/training/test_conviction_serving.py
- `_EXPECTED_TEST_MEETINGS` 91 -> 94. These are the held-out test meetings of the re-recorded corpus, and live/offline parity holds on all 94.

#### tests/training/test_model_evidence_provenance.py
- GZIP: `test_inert_report_is_not_a_fit_input` plants the report through `write_report_text(report_path(corpus), …)`.

#### tests/training/test_surrogate_dataset.py
- `test_build_meeting_table_consumes_the_frozen_corpus`: rewritten-target rows on ml_corpus/4p1i 2 -> 0.
- `test_the_ballot_audit_marker_census_over_the_four_committed_sets`:
  - (games, ballots, annotations, marked games) (300,3631,127,70) -> (300,3630,39,26);
  - kinds, before: {redirect 83, invalid_obs 15, teammate 7, redaction 7, invalid_reason 5, uncited 6, invalid_target 4};
  - kinds, after: {invalid_obs 1, teammate 13, redaction 13, invalid_counter_reason 4, invalid_target 8};
  - per_set_rewritten [27,70,1,2] -> [4,17,0,0]; guard_rewrite_reason 100 -> 21.
- `test_the_reporter_column_is_an_exclusion_oracle_the_fit_may_not_read`: CREWMATE reporter cells 3631 -> 3630.
- `test_j1_live_parity_divergence_is_measured_on_the_9p2i_corpus`: meetings 439 -> 449; rows 2516 -> 2539; cells 12772 -> 12760; divergent cells/rows 102/98 -> 82/80; fit/test 77/25 -> 61/21.

#### tests/training/test_surrogate_runner.py
- `test_surrogate_fidelity_reproduces_pinned_numbers`, a re-fit on every fold:
  - scored 91 -> 94; ejection/skip 57/34 -> 52/42; top1/top2 47/54 -> 46/47; predicted skips 89 -> 92;
  - correct skip 34 -> 42; ballot rows 289 -> 286; ceiling 57/47 -> 52/41.
- Same test, rates: top1 0.8246 -> 0.8846; top2 0.9474 -> 0.9038; skip-vs-eject 0.3956 -> 0.4681; always-eject 0.6264 -> 0.5532; max-achievable top1 0.8246 -> 0.7885.
- Same test, calibration: brier/ece 0.0646/0.1078 -> 0.0616/0.1163; ballot brier/ece 0.1225/0.1196 -> 0.1699/0.1488.
- `test_go_no_go_reproduces_the_re_measured_no_go_verdict` and `test_axis_one_still_discriminates_a_weaker_candidate`: top1_bar 0.6184 -> 0.5913; the gap ceiling 0.8246 -> 0.7885. NO-GO holds.
- `test_split_verdict_separates_the_ranking_and_decision_claims`: surrogate/ceiling top1 0.8246/0.8246 -> 0.8846/0.7885; ceiling flag/proximity/belief/reachable 49/52/46/47 -> 41/44/41/41.
  - top1_ceiling_gap 0.0 -> -0.0962 `[owner review: the re-fit surrogate exceeds the "honest ceiling"]`.
- `test_decision_reachability_is_the_tallys_own_gate_quantity`: plurality meetings 91 -> 94; reachability 2/91 -> 2/94.
- `test_fo6_rebaseline_reproduces_pinned_numbers`: top1 14 -> 16; ejection 57 -> 52; skips 91 -> 94; correct skip 34 -> 42; top1/top2 0.2456/0.4561 -> 0.3077/0.5769; skip-vs-eject 0.3736 -> 0.4468.
- `test_the_corpus_rows_the_fit_drops_are_the_whole_rewrite_class`: 9p2i coerced 6 -> 0 and rewritten 70 -> 17; 4p1i rewritten 2 -> 0; fit side 9p2i (5,59) -> (0,11), 4p1i (0,2) -> (0,0); the bound >59 -> >11.
- `test_predicted_ballot_calibration_is_a_distinct_channel`: predicted ballots 110 -> 84; skips 406 -> 442; brier 0.3278 -> 0.2491.

#### frontend/e2e/evidence-journey.ts
- The replay browser's "Earlier scores" banner goes from present to absent. The test now checks for the score legend and for every card named "… interestingness score N of 100". The rubric is fresh, and every score is 0, as pinned in test_sets.
- The pinned source link /5006a32f/ -> /9bae2b03/.
- RE-ANCHOR: the unsupported case moves from seed 46 M3 to seed 29 M1.
  - It now checks the dialog "Meeting at tick 9".
  - Observation tick 29 -> 6; scene frame 28 -> 5; cited observation p-3:29:1 -> p-7:6:2.
  - Cited statement 46:m3:turn-1 ("p-9 · public reply") -> 29:m1:turn-2 ("p-1 · public opt-in"); the missing-id probe p-3:29:missing -> p-7:6:missing.
- RE-ANCHOR: the unresolved case moves from seed 23 M1 to seed 0 M1: dialog "Meeting at tick 12" -> "17"; skip chips 7 -> 5. It adds "skip ×5", "p-1 ×2" and "Skipped — no ejection".

#### frontend/e2e/journey.spec.ts
- Comment only: the head's first meeting "~8 frames in" -> "~11". Measured on 9p2i seed 23.

#### frontend/src/components/BallotCard.tsx
- Doc comment: "27 of 869 ballots list the voter itself and 22 list the target" -> "24 of 845 … list the voter itself; no committed ballot lists the target (0 of 845)". Measured with `measure_featured_criterion.py --alternatives`.

#### frontend/src/components/PrivateReasoning.test.tsx
- Comment: the same count, 27/869 and 22 -> 24/845 and 0. The target entry is now described as constructed.

#### frontend/src/components/ReplayPicker.tsx
- `FEATURED_GAMES`: 9p2i 13 -> 0 and 46 -> 29, each with a new label. The 9p2i 23 label drops "…files that apart from one account merely contradicting another".
  - 13's three-meeting shape is gone, and 46 now has no flag and no ejection.
  - 23's M1 alibi flags are gone.
  - The criterion comment "hand-read" -> "hand-picked".

#### frontend/src/lib/bodies.fixture.json
- Regenerated with the generator in the test's header: corpus_sha256 9p2i fe563f76… -> db66cf99…, 4p1i 8d882af0… -> aef70cb5….

#### frontend/src/lib/bodies.test.ts
- Shipped rule, 9p2i: frames 1289 -> 1208; discoveredFrames and reportBodyEvents 141 -> 136.
- Retired rule, 9p2i: phantom frames/bodies 740/1512 -> 659/1291; room-count mismatches 740 -> 659; discovered 790 -> 709; discovered-after-report 1512 -> 1291; capOverflowFrames 0 -> 1, since one frame now crosses BODY_CAP.
- 4p1i: frames 586 -> 608. Retired-rule phantom frames/bodies/mismatches 51 -> 73; gamesWithPhantom 15 -> 19.

#### frontend/src/lib/contradictions.fixture.json
- Regenerated with the generator in the test's header: the same corpus_sha256 moves as bodies.fixture.json.

#### frontend/src/lib/contradictions.test.ts
- Shipped rule: meetings 190 -> 184; flags 167 -> 127; endpoints 334 -> 254; 9p2i flags 147 -> 107.
- Retired rule: unresolved 26 -> 8 (9p2i 26 -> 8); by category {cross 0, weak 26} -> {cross 1, weak 7}; half-linked 26 -> 8.
- The turns that lost every flag go from 4 (28/0/3, 32/1/4, 46/1/0, 4/3/0) to 3 (0/1/4, 14/1/4, 21/2/2).

#### frontend/src/lib/copy.ts
- Comment: 27/869 and 22 -> 24/845 and 0, as in BallotCard.tsx.

#### frontend/src/stories/MeetingView.stories.tsx
- Comment: 27/869 and 22 -> 24/845 and 0. The comment drops "seed 13's first meeting for the target one", and the target entry is now called a constructed example.

#### Pinned constants outside tests/ that the tests above read
- `scripts/counterfactual_phase21.py`:
  - `COMMITTED_INNOCENT_EJECTIONS` samples/9p2i 13 -> 9, ml_corpus/9p2i 29 -> 32, samples/4p1i 4 -> 0, ml_corpus/4p1i 0 -> 1 (audit §6.2 cell 2);
  - `COMMITTED_CORROBORATION_CELLS` (460,1525)/(10,425)/(33,429)/(79,429) -> (529,1516)/(16,409)/(36,411)/(69,411), re-derived by the script's own walk;
  - the refusal messages re-cite the new audit.
- `eval/watchability.py`:
  - a new baseline-9 floor block, 9p2i 3/175, 107/145, 79/112, 17/145, 90/145 and 4p1i 1/66, 20/39, 20/37, 0/39, 20/39;
  - `_DEFAULT_BASELINE_ID` baseline-8 -> baseline-9 (b3b007bf); `BAKEOFF_BASELINE_ID` is unchanged.
- `api/public_results.py`: `_SOURCE_ROOT` 5006a32f… -> 9bae2b03…; `_source_url` fingerprints as in test_recording_fingerprint; `_SEED_23_SHA` e493a2f6… -> 35ccb242…; `_SEED_46_SHA` is removed; new `_SEED_29_SHA` 06d8fb4c… and `_SEED_0_SHA` 5e0b8421….
- `api/public_results.py` cases: impossible-route (46 M3) -> disputed-route (29 M1), and weak-evidence 23 M1 -> 0 M1.
- `scripts/check_doc_facts.py`:
  - `_LADDER_TIP_AUDIT` -> audit-2026-09-22-process-rerecord.md and `_PROOF_PARTITION_AUDIT` -> audit-phase-21-rerecord.md;
  - `_WIN_SPLIT_HEADER` baseline-7 -> baseline-8 and `_BEFORE_COLUMN_HEADER` "At baseline 7" -> "At baseline 8";
  - a new `_FINDING_BASE_AUDIT`; prompt-set agreement is now compared per row.
- `eval/vote_correctness.py` stamps: samples/9p2i 75/82 = 0.9146 -> 76/81 = 0.9383; ml_corpus/9p2i 227/252 = 0.9008 -> 219/241 = 0.9087; ml_corpus/4p1i 27/29 = 0.9310 -> 26/27 = 0.9630. samples/4p1i 19/20 is unchanged.

#### Left red (not edited)
Unless marked, the assertion that fails was not changed. "(measured half re-pinned)" means the test's measured values were re-pinned and only its semantic assertion fails. The ML reasons used below:
- **[fence]**: the committed fit refuses the re-recorded corpus ("fit corpus or derivation drifted"; fit-corpus fingerprint recorded cc54d3c0…, measured 6536c68c…). This needs the ML re-ground (audit §7.1).
- **[frozen-fit]**: the test asserts a committed fitted artifact against the live corpus, and fixing it would need an edit under training/artifacts.
- **[grounding]**: the test's "ML grounding / fit-corpus identity == OK" control fails for the [fence] reason.

- `tests/agents/test_reported_testimony.py::test_reported_rows_survive_in_every_candidate_bucket` (measured half re-pinned): the 0.80 survival floor fails in the >150 bucket, where 5,927/7,539 = 0.786. It was 0.962 on baseline 8.
- `tests/api/test_view_model.py::test_report_tick_fog_keeps_the_reported_body`: product gap. At seed 13 tick 13, a report and a parity kill land on one tick with no meeting. `api/replay_loader.py` ≈l.1683 re-opens the body only in MEETING phase.
- `tests/eval/test_balance_eval_meeting_runner.py::test_surrogate_runner_factory_drives_zero_cost_diagnostic_tournament`: [fence] (surrogate).
- `tests/eval/test_evidence_honesty.py::test_the_band_change_not_the_fold_is_what_costs_first_hand_coverage` (measured half re-pinned): "fold renders fewer rows" fails, 32,123 vs 32,037. Coverage is still higher.
- `tests/eval/test_evidence_honesty.py::test_the_instrument_and_the_detector_read_one_adjacency_rule` (measured half re-pinned): the min-gap guard fails (gap 0). The kept-STRONG adjacent flags sit on multi-segment routes, where the detector reads the route endpoints and the instrument reads the segment.
- `tests/experiments/test_torch_probe_excluded.py::test_stub_entrant_trains_through_env_and_lands_experiment_tier`: [fence] (conviction).
- `tests/meetings/test_contradictions.py::TestGroundedProsecutionCommittedCensus::test_the_fully_grounded_leg_drops_the_whole_class`: "entirely WEAK" is false. There are 8 STRONG survivors, all on impostors.
- `tests/meetings/test_contradictions.py::TestGroundedProsecutionInjusticeShapes::test_no_committed_ejection_rides_a_strong_sighting_flag`: "class is EMPTY" is false. There are 5 counterexamples, every ejectee an impostor; 1 of them (ml_corpus 1041 m1) is in the recording.
- `tests/meetings/test_transcript.py::TestCommittedBytesArtifactCollapse::test_rederivation_diverges_only_at_the_repaired_sites` (downstream pins re-pinned): 4 re-derived pairings are neither proxy re-targets nor the corridor band (seed 7 m0 ×2, one of them STRONG; seed 32 m0; seed 38 m1).
- `tests/scripts/test_counterfactual_phase21.py::test_the_memo_table_equals_a_live_four_set_run`: the baseline-8 memo differs from the live baseline-9 run in 42 of 43 pooled cells. Owner call: a new table or erratum, or re-scope the gate.
- `tests/scripts/test_counterfactual_phase21.py::test_the_memo_marks_every_advisory_cell`: the same memo, with the fast-set advisory cells unmarked.
- `tests/scripts/test_verify_ml_evidence.py::test_recompute_reads_every_committed_verdict_against_the_live_corpus`: 11 recompute rows FAIL on the corpus change, and the pin is a single measured == committed equality.
- `tests/scripts/test_verify_ml_evidence.py::test_a_perturbed_weight_hash_fails_and_is_named_corpus_independent`: [grounding].
- `tests/scripts/test_verify_ml_evidence.py::test_an_undeclared_corpus_still_fails_the_grounding_row`: [grounding]; the planted half passes.
- `tests/scripts/test_verify_ml_evidence.py::test_historical_verifier_refuses_relabeled_fit_version`: [grounding].
- `tests/scripts/test_verify_ml_evidence.py::test_a_record_keyed_to_other_weights_fails_the_grounding_row`: [grounding].
- `tests/scripts/test_verify_ml_evidence.py::test_perturbed_replay_fails_the_corpus_leg`: [grounding] on the fit-corpus identity control; the perturbed half passes.
- `tests/training/test_bakeoff_harness.py::test_evaluate_candidate_full_row`, `::test_evaluate_candidate_experiment_tier`, `::test_evaluate_candidate_go_serves_the_term_live`, `::test_evaluate_candidate_multi_seed_stamps_the_composed_mean`: [fence] (conviction).
- `tests/training/test_bakeoff_harness.py::test_goodhart_surrogate_rerun_ci_budget`: [fence] (surrogate).
- `tests/training/test_bakeoff_methods.py::test_the_committed_map_elites_pool_is_historical_and_structurally_untouched`: [frozen-fit]. The committed map-elites index stamps the baseline-8 corpus MANIFEST digest (4a25ccdf…, live 8b174cab…).
- `tests/training/test_conviction_model.py::test_committed_artifact_round_trips_and_the_refit_no_longer_matches`: [frozen-fit]. The live fit side has 355 rows, against 348 in the committed record.
- `tests/training/test_conviction_model.py::test_the_committed_verdict_is_the_baseline8_first_evaluation`: [frozen-fit]. The frozen weights give confusion (42,5,2,45), where the pin is (49,3,2,37).
- `tests/training/test_conviction_model.py::test_axis_three_is_a_floor_the_live_model_clears_on_all_three`: [frozen-fit]. There are 94 test meetings and 44 conversions, where the pin is 91 and 51; GO still holds.
- `tests/training/test_goodhart_probe.py::test_conviction_path_report_shape`, `::test_conviction_path_consumption_is_metered_and_quoted`, `::test_conviction_path_verdict_composes_blockers` and `::test_conviction_path_report_round_trips_json` (ERROR at setup): [fence] (conviction).
- `tests/training/test_goodhart_probe.py::test_carried_4p1i_reread`, `::test_carried_reread_requires_the_reference_roster` and `::test_champion_genome_is_additive_for_old_report_json` (ERROR at setup): [fence] (conviction).
- `tests/training/test_goodhart_probe.py::test_conviction_reader_determinism_at_unit_level`: [fence] (conviction).
- `tests/training/test_goodhart_probe.py::test_probe_reruns_end_to_end_on_the_regrounded_surrogate`: [fence] (surrogate).
- `tests/training/test_model_evidence_provenance.py::test_historical_diagnostic_restores_committed_models`: [fence] (surrogate).
- `tests/training/test_surrogate_runner.py::test_full_surrogate_driven_game_meetings_are_real_tallies` and `::test_belief_fold_consumes_surrogate_ballot_roster` (ERROR at setup): [fence] (surrogate).
- `tests/training/test_surrogate_runner.py::test_runner_satisfies_meeting_runner_protocol`, `::test_surrogate_game_is_byte_deterministic` and `::test_fit_corpus_fence_fails_loud_on_substrate_and_key_drift`: [fence] (surrogate).
- `tests/training/test_surrogate_runner.py::test_the_install_gate_refuses_the_committed_no_go_as_a_training_runner` and `::test_fallback_a_trains_today_regardless_of_verdict`: [fence] (surrogate).
- `tests/training/test_surrogate_runner.py::test_factory_rejects_a_loosened_or_foreign_shared_counter` and `::test_cap_is_cumulative_across_fresh_runner_instances`: [fence] (surrogate).
- `tests/training/test_surrogate_runner.py::test_missing_artifact_and_malformed_meeting_id_fail_loud` and `::test_impostor_ballot_never_names_a_fellow_impostor`: [fence] (surrogate).
- `tests/training/test_surrogate_runner.py::test_the_committed_surrogate_is_a_baseline8_fit_on_the_baseline8_corpus`: [frozen-fit]. The live fit side has 355 meetings, against 348 in the record.
- `tests/training/test_surrogate_runner.py::test_committed_artifact_round_trips_and_the_refit_no_longer_matches`: [frozen-fit]. Same 355 vs 348 gap.
- `tests/training/test_surrogate_runner.py::test_the_committed_verdict_is_keyed_on_the_weights_and_reproduces`: [frozen-fit]. The committed verdict.json differs on 16 corpus-derived fields.
- `tests/training/test_surrogate_runner.py::test_bakeoff_reloads_the_committed_artifact_and_reproduces_the_numbers`: [frozen-fit]. The frozen weights now see 94 test views, where the pin has 91.
- `tests/training/test_surrogate_runner.py::test_no_go_verdict_holds_on_live_served_clamped_features`: [frozen-fit]. The first failing line is corpus-only (replaced 25 -> 21), and the rest depends on the frozen fit.

Cross-check against `red2.txt` (66 ids: 57 FAILED and 9 ERROR):
- The 60 ids red at the first close were exactly the ids in red2.txt that were still red. The review round (70e49468) made 8 of them honest without changing an assertion: `TestTheAlibiIsARoute` x3, the seed-25 tripwire, `TestRoutesOverTheCommittedRecord` x2 and the finale recap now read frozen baseline-8 exhibits, and the flip search is re-pinned to its measured empty set. The 52 listed above are exactly the red ids of the review round's `check.sh` run (43 failed + 9 errors), and no id outside the 60 turned red.
- `tests/scripts/test_verify_ml_evidence.py::test_main_runs_the_cheap_legs_green_at_head` and `::test_every_counted_registry_row_matches_the_index` are green after the registry recompute (5718620b, 2a5fde8d): they read the in-tree family inventory row, which lagged the regenerated W2 baseline fixture and the growing audit.
- Four ids in red2.txt are green at f4961ad1:
  - `tests/scripts/test_counterfactual_phase21.py::test_a_reconstruction_that_misses_the_record_refuses`: its asserted citation followed the moved SystemExit.
  - `tests/scripts/test_check_doc_facts.py::test_ml_duplicated_comparator_row_detected`, `::test_ml_invented_arm_row_detected` and `::test_ml_lookalike_comparator_row_detected`: docs/ml-program.md is back inside its word budget. No test was edited.
- red2.txt does not include `tests/experiments/test_fresh_deduction_instrument.py::TestLiveGate::test_no_committed_file_outside_the_module_and_the_manifest_names_the_flag`. It was a transient failure on the uncommitted archive deletion and cleared with a4bbee7f.
- Vitest (558) and Playwright (13 passed, 3 pre-existing skips) are green per the pub worker. red2.txt does not cover them.
