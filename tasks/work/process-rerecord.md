# Re-record the shown sample set once, after the substrate wave

**Status:** ready

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

- [ ] The before column is computed and committed **before the first seed
  stages**, on the still-committed bytes, with the tool
  [the process scorecard](process-scorecard.md) ships; D4 and D6 invalidate
  comparisons against these recordings, so a back-filled column would be a
  reconstruction. Cross-checks reproducible today: EJECT cited 526/527 and
  1,498/1,499; grounded SKIP **0 of 1,359** (342 + 1,017 over the two 9p2i
  sets); guard-redirected ballots 57/2,516 and 23/869; crew EJECTs off the
  suspicion argmax 81 of 1,270, of which 7 are role-correct.
- [ ] Four sets are recorded in the leg order `samples/9p2i` to
  `ml_corpus/9p2i` to `samples/4p1i` to `ml_corpus/4p1i`, at the **same seeds
  as today**: samples `0-49`, `ml_corpus/9p2i` `1000-1149`, `ml_corpus/4p1i`
  `1000-1049`. Hosted models do not byte-reproduce fresh generation
  (`record_ml_corpus.sh:53-56`), so the comparison is per-set and distributional
  rather than per-seed; the seeds are held constant because both recorders drive
  locked ranges whose finalize asserts the exact set before freezing (`:33-34`,
  `:93`), and because the manufactured-contradiction exhibit at seed 41 needs a
  successor in the same set rather than a replacement band.
- [ ] The recorders are used as they stand, the version pin being their only
  edit. `AILIBI_NUM_PLAYERS=9 AILIBI_NUM_IMPOSTORS=2 AILIBI_TASKS_PER_CREWMATE=2
  AILIBI_SAMPLE_DIR=replays/samples/9p2i` with its `AILIBI_MANIFEST` and
  `bash scripts/refresh_samples.sh --full --expect-levers ""`
  (`scripts/refresh_samples.sh:43-46`, `:56-64`) for the sample legs;
  `bash scripts/record_ml_corpus.sh --set <set> --expect-levers ""` for the
  corpus legs. Both compose `scripts/run_tournament.py`, untouched (`:36-38`);
  `REQUIRED_PROMPT_VERSIONS_BASE` (`:166`) advances to the wave's four version
  strings here and nowhere earlier.
- [ ] Each leg previews with `--dry-run` and pastes its resolved configuration
  into the audit, a preflight refusal being reported rather than worked around;
  each set's prior bytes move aside and are preserved, because both recorders
  read a present in-range replay as already recorded; and
  `scripts/measure_baseline.py --honesty` runs on every leg's first completed
  seed before the rest queues, a raise being a STOP and a probe that folds a
  meeting-free game recorded VACUOUS and re-run (§0.2 rules 3 to 5).
- [ ] Every leg is gated before the next begins and its range checkpoint-pushed:
  `scripts/validity_gate.py <set-dir> --expected-model Qwen/Qwen3.6-27B
  --require-zero-cost --expected-prompt-versions <the four KEY=VER pairs>` exits
  0 with all ten checks named individually (`scripts/validity_gate.py:12-16`),
  and `bash scripts/verify_samples.sh <set-dir>` reconstructs byte-identically
  in a **bare** shell with no `AILIBI_*` export. A partial record is not a
  baseline: if the window closes, the record stops at a set boundary and names
  the legs that exist. Every `(deadline_default)` row is a failed recording
  whose seed re-records, cause logged as it happens, five over 250 completed
  games last time (§5); no seed on disk re-records for any other reason.
- [ ] The derived views are rebuilt, never hand-edited: four
  `tournament-eval-report.json` files through
  `scripts/build_sample_report.py --sample-dir <set>`; `splits.json` and the
  FROZEN line for the corpus sets by their recorder;
  `replays/samples/9p2i/results-rubric-score.json` by the rubric step at
  `refresh_samples.sh:1049-1066`, whose failure means the refresh is incomplete;
  and `tests/fixtures/phase10/corrected_w2_baseline.json` via `--baseline-out`.
- [ ] The audit publishes one before/after table with a row per memo-section-8
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
- [ ] The manufactured-contradiction row reads **both** claim shapes: its basis
  test is version-gated over as-recorded bytes, single-room envelopes on the old
  recordings and ordered segments on the new, so no old recording is re-scored
  under the new rule. The card names the function owning the split and pins it
  with a planted fixture of each shape.
- [ ] The tour is re-pointed by
  [the spectator card](spectator-tour-and-alternatives.md)'s measured criterion
  re-run on the new bytes; every `FEATURED_GAMES` label
  (`frontend/src/components/ReplayPicker.tsx:94`) is true of the game it names,
  spoiler rule intact; and `cd frontend && npm run e2e` is green, its head-card
  guard binding the promise to the rendered evidence count in both directions
  (`frontend/e2e/journey.spec.ts:455-463`) and turning red on a planted
  mismatched blurb. The last re-record falsified that card (§5.1.1c).
- [ ] The ladder tip moves with a record, not a relabel. The audit is
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
- [ ] The adoption is routed, not taken: the pull request states that the
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
| input tokens | 31,756,112 | 43,000,000 |
| output tokens | 1,598,475 | 2,200,000 |
| recording wall | about 12h05m | 16 h |
| elapsed window | about 15h48m | 24 h |
| marginal cost | `$0.0000` | `$0.00` |

The cost is `$0.00` marginal against the flat-rate Featherless subscription,
whose standing fee is already paid and is not incurred by this run;
`AGENTS.md:89-92` requires the statement even on flat-rate service.

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
