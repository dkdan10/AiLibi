# Stage-B candidate round 2 — the balance round, its record and its assessment (2026-10-01)

Card: [`tasks/work/stage-b-record-r2.md`](../tasks/work/stage-b-record-r2.md).
Frozen head: `main` at `e87403b7`, the merge of PR #493, the kill-cooldown card.
Branch `work/stage-b-record-r2`, one pull request into `main`, merged by the
owner.

This record makes one 50-seed candidate round: seeds 0-49 of the 9-player
sample roster (9 players, 2 impostors, 2 tasks per crewmate), recorded once on
featherless `Qwen/Qwen3.6-27B` with the prompt set `qwen3_6_27b`, the bare
substrate slate and one declared experiment config, into
`replays/candidates/stage-b-r2/9p2i/`. The config is round 1's, with one more
field: the impostor kill cooldown, raised from the map's 4 ticks to 6. It
reads the round against questions fixed before the first seed, in three
columns that are never pooled: s9 at baseline 9, round 1 and round 2. The
ladder tip stands at baseline 9; the round adopts nothing, publishes nothing,
and the next step is the owner's.

Role-correct ejection and the win split are reported beside the readings and
gate nothing (ruling D1 of
[the direction of 2026-09-19](../tasks/direction-2026-09-19-process-over-outcome.md)
section 12).

## 1. Pre-registration

This section is committed before the first seed, in the `coordination:` commit
the card calls P, and it is never rewritten. A correction lands as a dated
addendum after it, in a later section. The recording checkout is detached at P
itself, so every MANIFEST row of the round stamps P's short sha and
`git merge-base --is-ancestor P <that sha>` exits 0.

### 1.1 The owner's rulings, verbatim and dated

On **2026-09-24**, the record ruling (memo 0.1; round 1's audit 1.1):

> Let's not re-record all 300 seeds each time. When it's time to record, record
> the smaller group of 50 seeds, assess if the implementations have been
> effective and resulted in desired results. Also it is understood that updating
> the vent and body reset logic will probably have a substantial effect on
> previous limits and statistics around the baseline voting results, that is
> okay.

On **2026-09-27**, round 1's ceilings (round 1's audit 1.1):

> Confirm the ceilings, v1 and the envelope as proposed

On **2026-09-28**, the wall (round 1's audit 4.1):

> Raise the wall to 12h in an 18h window and resume. Make sure it allows for a pause.

On **2026-10-01**, round 2 (memo section 7):

> Merge.  Adopt all 7 non-balance arms. And run a balance round

The last is the live-call authorization for this round, under round 1's
ceilings as amended on 2026-09-28 (1.6), as memo section 7 applies it.

### 1.2 What adoption means, and the orchestrator's application

Memo section 7 adopts the seven arms in the sense the direction addendum of
2026-10-01 defines, verbatim: "(declared ON in every later round; defaults
untouched; the shown set moves by the era-keyed promotion once a round sits
inside the envelope)". The addendum adds that "the project's documents describe
them as the current game". A missing key keeps its historical meaning, so the
four baseline-9 sets and round 1 keep verifying byte for byte.

The orchestrator's application, in memo section 7 (not the owner's words):
`look_and_wait` stays; round 2 is a balance round with "exactly one dial, a
recorded kill-cooldown override field on the engine layer, first value 6 ticks
against the map's 4, with a pre-registered round-3 rule (win share above 0.60
at 6 names 8; below 0.20 names 5), the same eight arms, the same amended
ceilings, the same pause mechanism, and its own candidate directory".

### 1.3 The orchestrator's two rulings of 2026-10-01

Ruled by the orchestrator on 2026-10-01, under the owner's delegation, and
reported to the owner the same day; verbatim from the card's Constraints:

> - the round-3 rule as written above stands. Memo 7 states its first two branches; its third, the
>   promotion branch, is the orchestrator's application of memo 7's adoption meaning: it NAMES the
>   era-keyed promotion of round 2 as the shown set, and the promotion itself stays a separate card and a
>   publication decision the owner takes at that time. An owner amendment before P changes the table, the
>   rule sentence and `readings.py` with it, at P.
> - the probe is the two-seed probe: seeds 0-1 as one leg on the leg's two workers, then 2-6, 7-11 and so
>   on to 42-46, then 47-49; or, if seeds 0-1 hold no meeting or no fired rebuttal, an extension naming
>   seeds 2-3 only, then 4-8, 9-13 and so on to 44-48, then 49. Reason: round 1's single seed 0 projected
>   11.64 h by itself against a round that took 3.55 h, because one seed's wall carries the provider's
>   latency of the moment and a one-worker figure for a two-worker leg; two seeds on the leg's own two
>   workers give the wall projection a basis that matches how the leg runs. The re-projection rule itself
>   is unchanged. If the owner overrules either ruling before P, P records the amendment instead.

No owner amendment of either ruling, of the ceilings or of the dial's value
reached this record before P, so the table (1.9), the rule sentence (1.10) and
the readings command (1.12) stand as the card states them. The probe lines of
the card's Validation (`--seeds 0`, an extension `--seeds 1,2,3`, batches from
`--seeds 1,2,3,4,5`) are the round-1 pattern and are superseded by the second
ruling; the leg runs the lists in 1.8.

### 1.4 The declared config

One line plus a newline, 316 bytes: round 1's 290-byte file with
`, "kill_cooldown_ticks": 6` inserted before the closing brace.

```
{"format_version": 1, "meeting_reset": "hub_with_grace", "vent_exit_policy": "look_and_wait", "vent_entry_policy": "own_fresh_kill", "vent_witness_rule": "physical", "bounded_rebuttal_version": 1, "report_body_handle_version": 1, "ballot_kill_row_version": 1, "impostor_ballot_version": 1, "kill_cooldown_ticks": 6}
```

`shasum -a 256` on those bytes prints

```
0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b
```

which equals the card's figure (round 1's prints
`4f0c4dd4779cd38f69194b6735221d86bf7c6944fe12769a3971e38e4e46d6c7`). At `F`
the bytes, read by `scripts/_declared_experiment.py`'s loader, validate as a
`RecordedExperimentConfig` whose fields off their default are exactly nine:
round 1's eight (`meeting_reset`, `vent_exit_policy`,
`bounded_rebuttal_version`, `vent_witness_rule`, `vent_entry_policy`,
`report_body_handle_version`, `ballot_kill_row_version`,
`impostor_ballot_version`) and `kill_cooldown_ticks`. `FIELD_LAYER` assigns the
cooldown `engine`, `OMITTED_AT_DEFAULT` holds it, and `engine_arguments`
returns `{'redistribution_policy': 'lowest_id', 'vent_witness_rule':
'physical', 'kill_cooldown_ticks': 6}`. `prompt_versions_for_set("qwen3_6_27b",
experiment_config=...)` serves round 1's four stamps:
`accusation_round.qwen3_6_27b.v6`, `crewmate_report.qwen3_6_27b.v6`,
`impostor_report.qwen3_6_27b.v6` and
`vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1+vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1`.
`self_report` stays False, `contextual_self_report_version` and
`evidence_reasoning_version` stay None, and the substrate slate is bare
(`--expect-levers ""`).

The file is not committed at P: a round directory without its set directory
fails the candidate test. A later commit on this branch adds it at
`replays/candidates/stage-b-r2/experiment-config.json`, and its sha256 must
equal the line above. Until then each checkout that reads it holds an
untracked copy whose `shasum -a 256` is checked against that line before the
dry run and every gate; a mismatch stops the card. No pytest and no
`check.sh` run beside an untracked copy.

### 1.5 The frozen head and the three checkouts

`F` is `e87403b7`. P is the commit that adds this section; its tree differs from
`F`'s only in this audit, its `audits/README.md` row and the re-derived
`audits/` row of `docs/artifacts.md`, so the code every seed runs is `F`'s.

- **Recording**: a fresh worktree detached at P, outside the repository's
  working tree, with `uv sync --frozen` and no `.env`, which runs only the
  recorder. No pytest, no `check.sh` and no commit run there, so the
  recorder's one `git rev-parse --short HEAD` per run reads P for every leg.
- **Verification**: the pre-spend at `F` runs in this branch's worktree while
  it is still at `F` with a clean status, before P is committed.
- **Delivery**: the `work/stage-b-record-r2` worktree, which receives each
  checkpoint's copy of the recorded bytes and runs every gate after each leg,
  in a bare shell. Its code is `F`'s: the branch adds only documents and the
  round's bytes.

From the first seed to the merge nothing merges into `engine/`, `agents/` (the
prompt set included), `meetings/`, `observation/`, `orchestrator/`, `eval/`,
`api/`, `scripts/` or `llm/`; if `main` moves there, the record stops and asks.
Otherwise `main` is merged in and every gate re-runs.

### 1.6 The ceilings, and the re-projection

Round 1's ceilings as amended on 2026-09-28 (round 1's audit 4.2), unchanged:

| limit | ceiling | hard stop at 90% |
|---|---|---|
| model calls | **2,800** | 2,520 |
| input tokens | **17,500,000** | 15,750,000 |
| output tokens | **750,000** | 675,000 |
| recording wall | **12 h** summed over sittings, each sitting inside an **18 h** elapsed window | **10.8 h** summed (38,880 s) |
| marginal cost | **$0.00** | any `cost_usd` other than 0.0000 |

The cost is marginal against the flat-rate Featherless subscription, whose
standing fee is already paid and is not incurred by this run. Recording wall is
each leg's own "Refresh complete in" figure, summed over sittings; the time
between legs, spent on gates and checkpoints, counts only against the
sitting's 18 h window, which opens with that sitting's first seed.

The anchor is the baseline-9 leg of the same seeds (round 1's audit 1.4): 145
meetings, 1,694 calls, 9,850,930 input and 422,941 output tokens, 8,695 s,
$0. The tally (Validation) prints `1694 9850930 422941 0.0` on
`replays/samples/9p2i` and `1556 9344346 433660 0.0` on round 1 at `F`.
Round 1 spent, with its seed-31 husk, 1,586 calls, 9,508,803 input, 441,535
output and 12,776 s (3.55 h), $0: 56.6%, 54.3%, 58.9% and 29.6% of the four
ceilings, so the 90% stops leave 1.59x its calls, 1.66x its input, 1.53x its
output and 3.04x its wall. If longer games come, output is the first stop
they meet.

**Re-projection**, round 1's rule unchanged: after the probe, after 10 seeds
(the first checkpoint holding at least 10 seeds) and at every batch
checkpoint, each count is (the round's total over its completed seeds / the s9
total over the same seeds) x the s9 leg total, and the wall is the summed
recording wall / the completed seeds x 50, each compared with its 90% stop. A
figure past its stop at any of them stops the round. `reproject.py` (1.13)
computes it. Beside each, for context only, the same count ratio against round
1's same seeds is printed; it gates nothing.

### 1.7 The stop rules

Stop and report to the owner, with the partial output and the last checkpoint
pushed, on:

- any `cost_usd` other than 0.0000, or a re-projection past 90% of a ceiling;
- a leg past 1.5x the probe's projected wall, or summed recording wall past
  10.8 h, or a sitting past its 18 h window;
- a provider refusal that survives the 8-attempt budget, or a raise from
  `measure_baseline.py --honesty`;
- any conformance breach: a "Conf." cell of 1.9 that does not read as built,
  the cooldown cell included. It is a code defect, not a result: the fix lands
  under a new arm value, and a fix to the cooldown writers lands as a new
  field, since a recorded `kill_cooldown_ticks` value's meaning is frozen. The
  round re-records from seed 0 under a new declared config, with a dated
  addendum and the owner's clearance.

**Stalls and failed seeds.** A stall is 45 minutes with no completed seed:
kill the batch and re-run it for the seeds not on disk, or relaunch a fresh
operator from the last pushed checkpoint. A seed on disk is never re-recorded
to recover a stall. A `(deadline_default)` row marks a failed recording: move
its husk outside the repository (its spend counts) and re-record that seed
alone at P, logging the cause as it happens. No seed re-records for any other
reason.

### 1.8 The probe, the batches, the pause and the key

**The probe** (the ruling of 1.3): seeds 0-1 record as one leg on the leg's two
workers (`--seeds 0,1`). Then, in the delivery checkout and a bare shell: the
validity gate with the declared config and `--expected-seeds 0-1`,
`verify_samples.sh`, the golden's directory walk, the census conformance cells
(the cooldown cell included), the scorecard fold, `measure_baseline.py
--honesty` (a raise is a STOP) and `scan_recording_packets.py`, then the tally,
the re-projection and the count-only key scan, before any batch queues. If
seeds 0-1 hold no meeting or no fired rebuttal, one extension leg names seeds
2-3 only; seeds 0-3 with a meeting but no rebuttal stop the card.

**The batches**, each naming only the seeds it must record, never `--full`:

- after the two-seed probe: `2-6`, `7-11`, `12-16`, `17-21`, `22-26`, `27-31`,
  `32-36`, `37-41`, `42-46`, `47-49`;
- after an extension to seeds 0-3: `4-8`, `9-13`, `14-18`, `19-23`, `24-28`,
  `29-33`, `34-38`, `39-43`, `44-48`, `49`.

A probed seed is never re-recorded and no seed on disk is named again: the
recorder re-records any seed it is given.

**The pause.** Before each batch the operator checks a pause file outside the
repository (`stage-b-record-r2/PAUSE` in the operator's scratch directory). If
it exists, no batch starts: the key file is deleted, the last checkpoint is
pushed, and the operator log names the seed reached and the next batch. The
next sitting opens a new 18 h window, copies the key again and resumes at the
named batch; its recording wall adds to the sum. A batch in flight finishes and
checkpoints first, so a pause never strands a half-recorded seed.

**After each batch**, in the delivery checkout and a bare shell: the probe's
gates with `--expected-seeds 0-N`, the tally, the re-projection and the key
scan, then a pushed `record:` checkpoint commit.

**The recording shell** sets only round 1's slate with `AILIBI_SAMPLE_DIR` and
`AILIBI_MANIFEST` on this round's set:

```
AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b \
AILIBI_LLM_MEETING_MODEL=Qwen/Qwen3.6-27B AILIBI_NUM_PLAYERS=9 AILIBI_NUM_IMPOSTORS=2 \
AILIBI_TASKS_PER_CREWMATE=2 AILIBI_SAMPLE_DIR=replays/candidates/stage-b-r2/9p2i \
AILIBI_MANIFEST=replays/candidates/stage-b-r2/9p2i/MANIFEST.md \
AILIBI_REFRESH_WORKERS=2 AILIBI_SEED_MAX_ATTEMPTS=8 \
  uv run --env-file <key file> bash scripts/refresh_samples.sh --seeds <the leg's seeds> \
    --expect-levers "" --experiment-config replays/candidates/stage-b-r2/experiment-config.json
```

**The key.** `FEATHERLESS_API_KEY` is copied from the main checkout's untracked
`.env` by a command whose output goes straight to a mode-0600 file in a
mode-0700 directory outside every checkout, and is never printed. It is passed
only by `uv run --env-file`, and the file is deleted at a pause and after the
last push. The recorder prints the key's first eight characters into its run
log; that log stays outside the repository, and no line quoted from it here
carries that line. Every key scan is count-only and must read 0. No rendered
prompt or seed-band prefix is printed anywhere; every census is count-only.

### 1.9 The three columns, and each cell's source

**s9 at baseline 9** is the `samples/9p2i` entry of `docs/gameplay-census.json`
and of `docs/process-scorecard.json`, and `measure_baseline.py
replays/samples/9p2i --honesty --json` for the ballot family. At `F`,
`publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout`
equals the shipped census entry in 998 of 998 leaves, and
`publish_process_scorecard.py --set-dir replays/samples/9p2i --json-stdout`
equals the shipped scorecard entry in 108 of 108.

**Round 1** is round 1's audit section 6, re-measured at `F` by the same
`--set-dir` modes, `measure_baseline.py replays/candidates/stage-b-r1/9p2i
--honesty --json` and the validity gate's betrayal check. At `F` the
re-measure reproduces each of the 83 counts that section 6 and the card's
round-1 column state, with 0 differing (section 2 gives the command).

**Round 2** comes only from these, run on `replays/candidates/stage-b-r2/9p2i`:
`publish_gameplay_census.py --set-dir DIR --json-stdout`,
`publish_process_scorecard.py --set-dir DIR --json-stdout`,
`measure_baseline.py DIR --honesty --json` (ballot cells 3 and 5) and the
validity gate's `no_betrayal_ballots_or_accusations`, read through the
readings command (1.12). A cell no named source counts is "not carried" and is
not measured another way.

"Conf." cells must read exactly as built; a miss is a code defect that stops
the round. "Reported" cells carry no rule. Rates carry Wilson 95% intervals.
No column is pooled with another. Round 2's rules are round 1's verbatim, plus
the cooldown cell, the balance row's two keys and the round-3 rule; the
envelope line no longer names the status-quo fallback for the vent exit, which
memo 7 keeps.

| arm | cell | s9 at baseline 9 | round 1 | round 2 reading |
|---|---|---|---|---|
| physical witness | exits seen only from the room left (`vent_exits_seen_only_from_room_left`); vent-band ejections resting only on them (`vent_band_resting_only_on_room_left`) | 9/85; 8/70 | 0/72; 0/24 | Conf. 0; 0 |
| look and wait | surfacings before the cap with a non-teammate in the inferred-visible set (`surfacings_before_cap_in_view`); trips over the cap (`trips_longer_than_cap`) | 52/85; 0/0 | 0/72; 0/63 | Conf. 0; 0 |
| look and wait | exits seen from the exit room (`vent_exits_seen_from_exit_room`) | 53/85 = 0.624 (0.52-0.72) | 8/72 = 0.111 (0.06-0.20), effective | **effective** at 0.30 or below; **not effective** at 0.52 or above, naming the hidden-travel escalation; **partial** between; n/a with no vent exit |
| look and wait | forced exits (`forced_surfacings`); ticks inside per trip (table `ticks_inside_per_trip`); in-place surfacings a crewmate reaches (`in_place_surfacings_near_crew`); kills within 2 ticks of a surfacing (`kills_soon_after_surfacing`) | 0/0; 85 at 1 tick; 0/0; 3/175 | 13/72; 1 tick 51, 2 ticks 6, 3 ticks 2, 4 ticks 13; 2/37; 0/227 | reported |
| own fresh kill | entries not after the impostor's own fresh kill (`vent_entries_not_after_own_fresh_kill`) | 13/105 | 0/142 | Conf. 0 |
| full reset | stale reports (`stale_report_meetings`); corpses older than the last regroup (`report_corpses_older_than_last_close`); play resumes with a vented impostor (`play_resumes_with_impostor_in_vent`); with a corpse (`play_resumes_with_corpse`); kills in the grace window after a regroup (`kills_in_grace_window_after_regroup`) | 43/135; 0/0; 10/107; 60/107; 0/0 | 0/118; 0/68; 0/110; 0/110; 0/139 (T+1 to T+4) | Conf. 0 each; at cooldown 6 the window is T+1 to T+6 |
| full reset | false resume perceptions; regroup notice present | n/a | not carried | Conf. 0; present every time; **not carried**, resting on mechanism and the golden |
| full reset | skipped report meetings (`skipped_report_meetings`); meetings per game; trips closed by a regroup (`trips_closed_by_regroup`); kill-witness button calls within 6 ticks of a regroup (`kill_witness_button_calls_soon_after_regroup`); dropped trigger-tick events (table `trigger_tick_events_dropped_by_regroup`); meetings opening with an impostor in a vent (`meetings_opening_with_impostor_in_vent`) | 55/135; 2.90; n/a; n/a; n/a; 29/145 | 70/118; 2.48; 46/142; 0/6; Moved 51, TaskProgressed 26, TaskCompleted 6; 66/124 | reported |
| one reply | rebuttals the selector would not have chosen (`rebuttals_differing_from_selector`); meetings with a second repeat-speaker turn (`meetings_with_second_repeat_speaker`) | 0/0; 0/145 | 0/121; 0/124 | Conf. 0; 0 |
| one reply | opener rebuttals answering the charged tick (`opener_rebuttals_answering_charged_tick`); rebuttals that only redirect (`rebuttals_redirect_only`) | n/a (accused openers answered 0/125); n/a | 19/19 (82 not evaluable); 17/121; effective | **effective** if half or more answer; **not effective** below 0.2, or if redirect-only reaches half; **partial** otherwise; **conflicting** if both hold; n/a with none evaluable |
| one reply | accused openers answering (`accused_opener_answers`); beneficiaries (table `rebuttal_beneficiaries`); rebuttals with an alibi, a whereabouts claim, a sighting; accusations against earlier speakers; ballots citing a rebuttal | 0/125; none; n/a; n/a; not carried | 101/112; 71, 30, 17, 3; 104/121, 104/121, 91/121; 121/121; not carried | reported |
| body handle | report openings carrying the kill-tick handle (`report_openings_with_kill_tick_handle`) | 135/135 | 0/118 | Conf. 0 |
| kill row | own-kill rows naming a teammate or held by a non-witness (`own_kill_rows_breaching`) | 0/0 | 0/4 | Conf. 0 |
| kill row | own-kill rows served; cited by their holder (`own_kill_rows_cited_by_holder`); honesty cell 5 | 0; n/a; 4 holders, 3 of 4 citing | 4, present; 3 of 4; 4 holders, 3 of 4 | presence only: **present** when one or more is served |
| impostor ballot | recorded teammate targets (`recorded_teammate_ballot_targets`); the gate's betrayal check | 0/210; 0 of 845 | 0/203; 0 of 717 | Conf. 0; 0 |
| impostor ballot | EJECTs whose only citation is a neutral row (honesty cell 3) | 1/46 | 0/107, the wording holds | **the wording holds** at 0.10 or below; **it does not bind** above 0.25; **between** otherwise; n/a with no impostor EJECT |
| impostor ballot | EJECT share (`impostor_eject_ballots`); labelled supported (`impostor_ejects_labelled_supported`); authored teammate targets (`authored_teammate_ballot_targets`); ejections only impostors carried (`ejections_carried_only_by_impostor_ballots`); `none_held` SKIPs | 46/210; 44/46; 1/210; 0/90; 95/164 | 107/203; 107/107; 16/203; 0/54; not carried | reported |
| self-report off | impostor openers (`impostor_openers`) | 0/145 | 0/124 | Conf. 0 |
| kill cooldown | kill cooldowns that differ from the recorded value (`kill_cooldowns_differing_from_recorded`), with writes by writer at round start, after a kill and at a regroup (table `kill_cooldown_writes_by_writer`) | 0/275 against 4: round start 100, after a kill 175, regroup row empty | 0/487 against 4: round start 100, after a kill 227, at a regroup 160 | Conf. 0 against 6, with a non-empty count at each of the three writers |
| envelope | impostor win share (`impostor_wins`) | 11/50 = 0.22 (0.13-0.35) | 34/50 = 0.68 (0.54-0.79), flagged above 0.60 | non-gating; flagged outside 0.20-0.60; the round-3 rule (1.10) names the step |
| envelope | innocent ejections (`role_correct_ejections`' denominator less its numerator); reporters ejected per report meeting (table `innocent_opener_ejections_by_trigger`'s report row over table `meetings_by_trigger`'s report row); role-correct ejections (`role_correct_ejections`); meetings with vent proof (`meetings_with_vent_proof`); scorecard rows 1-9 | 9 of 90; 7/135; 81/90; 70/145; as published | 15 of 54; 11/118; 39/54; 26/124; round 1's audit 6.1 | non-gating; reporter ejections above 0.104 per report meeting are flagged |
| balance | kills (`kills_seen_by_crew`'s denominator); impostors able to kill when a meeting opened (`impostor_cooldown_zero_at_open`); the win split (`impostor_wins`) | 175; 63/210; 39 crew, 11 impostor | 227; 84/203; 16 crew, 34 impostor | reported |

Every s9 and round-1 value above is what the readings command prints at `F`
(on `docs/gameplay-census.json` and on the round-1 `--set-dir` section), apart
from the betrayal check, which is the validity gate's own line on each set
(0 over 845 ballots on s9, 0 over 717 on round 1), and the `none_held` SKIPs on
s9, the ballot card's own count, carried from round 1's audit. The cooldown
cell reads 0 on both committed columns against the map's 4; s9 has no regroup,
so its regroup row is empty, which the readings command flags only with
`--after`.

### 1.10 The round-3 rule

> **The round-3 rule.** On round 2's point share of impostor wins: above 0.60
> at 6 it names round 3 at `kill_cooldown_ticks = 8`; below 0.20 it names round
> 3 at `kill_cooldown_ticks = 5`; otherwise, with no envelope flag and every
> Conf. cell at 0, it names the era-keyed promotion of round 2 for the owner to
> decide, else no step.

The rule names a step and gates no acceptance item; the win share it reads
gates nothing, as the whole envelope gates nothing. The promotion branch names
the era-keyed promotion of round 2 as the shown set; it does not take it (1.3).
The next card, its spend and any promotion are the owner's. Round 1's readings
stand (a later experiment never changes an earlier verdict), and one key
separates the rounds, so their difference is the dial's, within
hosted-generation noise.

### 1.11 The order of the assessment, and the decision menu

The assessment reads, in this order: the process cells (the scorecard's rows,
three columns); then each arm's Conf. cells and reading by 1.9's rules; then
the cooldown cell; then the envelope and the step the round-3 rule names,
which gates nothing; then role-correct ejection, the balance row and the win
split, gating nothing. Only the Conf. cells and the lab's rows (a mechanical
attribution on development seeds with a fake provider) attribute a mechanism
to one arm.

It gives no verdict. The decision menu: the step the round-3 rule names;
round 1's options for `look_and_wait` alone (adopt through the era-keyed
promotion, iterate under a new value, escalate to hidden travel, fall back to
the status quo); Conf. cells only for the seven adopted arms. If the step is
the promotion, the menu lists the follow-ups this round adds to memo 1's
adoption list for the promoting card: a public-results label for the kill
cooldown (`frontend/src/components/PublicResults.tsx` names each recorded
experiment and has no words for it, so a group set apart only by its cooldown
reads as having no enabled experiment).

### 1.12 The readings command, whole

Saved as `readings.py` and run with `python3` (standard library only; sha256
`1de53d95f88feacaeab4ed76df91c501e0b340ebe3d54558d118bc061a3f5030` as
extracted from the card). It prints counts and rates, never a prompt.

```
python3 readings.py docs/gameplay-census.json honesty-s9.json                                # s9
python3 readings.py census-stage-b-r1.json honesty-stage-b-r1.json --after                   # round 1
python3 readings.py census-stage-b-r2.json honesty-stage-b-r2.json --after --round-3-rule    # round 2
```

```python
"""Print round 2's pre-registered table from its named sources (count-only).

Usage: readings.py CENSUS.json HONESTY.json [--after] [--round-3-rule]

CENSUS.json is one census section: `publish_gameplay_census.py --set-dir DIR
--json-stdout`, or the s9 entry of docs/gameplay-census.json (the s9 column;
the two are equal cell for cell at F). HONESTY.json is
`measure_baseline.py DIR --honesty --json`. With --after, each reading is
computed by the pre-registered rule and the command exits 1 on a Conf. miss;
without it, values only. With --round-3-rule (after --after), the last line
names the step the round-3 rule names.
"""

import json
import math
import sys


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def rate(k, n):
    if n == 0:
        return f"{k}/{n} (n/a)"
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {k / n:.3f} (Wilson {lo:.2f}-{hi:.2f})"


census = json.load(open(sys.argv[1]))
if "sets" in census:
    census = next(s for s in census["sets"] if s["label"] == "samples/9p2i")
honesty = json.load(open(sys.argv[2]))[0]["ballot_conduct"]
after = "--after" in sys.argv
cells = census["cells"]
tables = census["tables"]
misses = []
flags = []


def cell(key):
    c = cells[key]
    return c["numerator"], c["denominator"]


def show(label, key):
    k, n = cell(key)
    ne = cells[key]["not_evaluable"]
    extra = f"; {ne} not evaluable" if ne else ""
    print(f"  {label} [{key}]: {rate(k, n)}{extra}")
    return k, n


def conf(label, key):
    k, n = show(label, key)
    if after:
        print(f"    Conf.: {'reads 0 as built' if k == 0 else 'BREACH'}")
        if k != 0:
            misses.append(key)
    return k, n


print(f"games {census['games']}; meetings {census['meetings']}; "
      f"meetings per game {census['meetings'] / census['games']:.2f}")
print("physical witness")
conf("exits seen only from the room left", "vent_exits_seen_only_from_room_left")
conf("vent-band ejections resting only on them", "vent_band_resting_only_on_room_left")
print("look and wait")
conf("surfacings before the cap with someone in view", "surfacings_before_cap_in_view")
conf("trips over the cap", "trips_longer_than_cap")
show("  beside: exits into a room the impostor could see a crewmate in",
     "vent_exits_into_visibly_occupied_room")
k, n = show("exits seen from the exit room", "vent_exits_seen_from_exit_room")
if after:
    if n == 0:
        print("    reading: n/a (no vent exit)")
    else:
        share = k / n
        verdict = ("effective" if share <= 0.30 else
                   "not effective (names the hidden-travel escalation)" if share >= 0.52
                   else "partial")
        print(f"    reading: {verdict}")
show("forced exits", "forced_surfacings")
print(f"  ticks inside per surfaced trip [ticks_inside_per_trip]: "
      f"{json.dumps(tables['ticks_inside_per_trip']['counts'], sort_keys=True)}")
show("near-body cost: in-place surfacings a crewmate reaches", "in_place_surfacings_near_crew")
show("kills within 2 ticks of the killer's surfacing", "kills_soon_after_surfacing")
print("own fresh kill")
conf("entries not after the impostor's own fresh kill", "vent_entries_not_after_own_fresh_kill")
print("full reset")
conf("stale report meetings", "stale_report_meetings")
conf("reported corpses older than the last regroup", "report_corpses_older_than_last_close")
conf("play resumes with an impostor in a vent", "play_resumes_with_impostor_in_vent")
conf("play resumes with a corpse", "play_resumes_with_corpse")
conf("kills in the grace window after a regroup", "kills_in_grace_window_after_regroup")
show("  beside: kills within 2 ticks of any meeting", "post_meeting_kills_soon_after")
show("skipped report meetings", "skipped_report_meetings")
show("trips closed by a regroup", "trips_closed_by_regroup")
show("kill-witness button calls within 6 ticks of a regroup",
     "kill_witness_button_calls_soon_after_regroup")
print(f"  dropped trigger-tick events [trigger_tick_events_dropped_by_regroup]: "
      f"{json.dumps(tables['trigger_tick_events_dropped_by_regroup']['counts'], sort_keys=True)}")
show("meetings opening with an impostor in a vent", "meetings_opening_with_impostor_in_vent")
print("one reply")
conf("rebuttals the selector would not have chosen", "rebuttals_differing_from_selector")
conf("meetings with two repeat-speaker turns", "meetings_with_second_repeat_speaker")
show("an accused opener answers", "accused_opener_answers")
ka, na = show("opener rebuttals answering the charged tick",
              "opener_rebuttals_answering_charged_tick")
kr, nr = show("rebuttals that only redirect", "rebuttals_redirect_only")
if after:
    effective = na > 0 and ka / na >= 0.5
    not_effective = (na > 0 and ka / na < 0.2) or (nr > 0 and kr / nr >= 0.5)
    if na == 0 and not (nr > 0 and kr / nr >= 0.5):
        print("    reading: n/a (no evaluable opener rebuttal)")
    elif effective and not_effective:
        print("    reading: conflicting (an effective and a not-effective condition both hold)")
    elif effective:
        print("    reading: effective")
    elif not_effective:
        print("    reading: not effective")
    else:
        print("    reading: partial")
show("rebuttals carrying an alibi", "rebuttals_with_alibi")
show("rebuttals carrying a whereabouts claim", "rebuttals_with_whereabouts")
show("rebuttals carrying a sighting", "rebuttals_with_sighting")
show("rebuttal accusations against players who already spoke",
     "rebuttal_accusations_against_earlier_speakers")
print(f"  beneficiaries [rebuttal_beneficiaries]: "
      f"{json.dumps(tables['rebuttal_beneficiaries']['counts'], sort_keys=True)}")
print("body handle")
conf("report openings carrying the kill-tick handle", "report_openings_with_kill_tick_handle")
print("kill row")
conf("own-kill rows naming a teammate or held by a non-witness", "own_kill_rows_breaching")
served = cell("own_kill_rows_breaching")[1]
show("own-kill rows their holder cited", "own_kill_rows_cited_by_holder")
holders = honesty["kill_holders"]
citing = honesty["kill_holders_citing_the_kill"]
print(f"  honesty cell 5: kill holders {holders}; citing the kill "
      f"{rate(citing['numerator'], citing['denominator'])}")
if after:
    print(f"    presence: {'present' if served > 0 else 'absent'} ({served} rows served)")
print("impostor ballot")
conf("recorded teammate ballot targets", "recorded_teammate_ballot_targets")
neutral = honesty["ejects_citing_only_neutral"]
print(f"  honesty cell 3: impostor EJECTs citing only a neutral row "
      f"{rate(neutral['numerator'], neutral['denominator'])}")
if after:
    if neutral["denominator"] == 0:
        print("    reading: n/a (no impostor EJECT)")
    else:
        share = neutral["numerator"] / neutral["denominator"]
        verdict = ("the wording holds" if share <= 0.10 else
                   "it does not bind (a revision under a new value)" if share > 0.25
                   else "between the two readings")
        print(f"    reading: {verdict}")
show("impostor EJECT share", "impostor_eject_ballots")
show("impostor EJECTs labelled supported", "impostor_ejects_labelled_supported")
show("authored teammate targets", "authored_teammate_ballot_targets")
show("ejections whose floor only impostors met", "ejections_carried_only_by_impostor_ballots")
print("self-report off")
conf("impostor openers", "impostor_openers")
print("kill cooldown")
conf("kill cooldowns that differ from the recorded value",
     "kill_cooldowns_differing_from_recorded")
writes = tables["kill_cooldown_writes_by_writer"]["counts"]
print(f"  writes by writer [kill_cooldown_writes_by_writer]: "
      f"{json.dumps(writes, sort_keys=True)}")
if after:
    for writer in ("round_start", "after_kill", "regroup"):
        if writes.get(writer, 0) == 0:
            print(f"    Conf.: BREACH (no write counted at {writer})")
            misses.append(f"kill_cooldown_writes_by_writer.{writer}")
print("envelope (non-gating)")
k, n = show("impostor win share", "impostor_wins")
if after and n:
    share = k / n
    if share > 0.60 or share < 0.20:
        flags.append("win share")
    print(f"    envelope: {'flagged above 0.60' if share > 0.60 else 'flagged below 0.20' if share < 0.20 else 'inside 0.20-0.60'}")
rk, rn = cell("role_correct_ejections")
print(f"  innocent ejections: {rn - rk} of {rn} ejections")
reporters = tables["innocent_opener_ejections_by_trigger"]["counts"].get("report", 0)
report_meetings = tables["meetings_by_trigger"]["counts"].get("report", 0)
print(f"  reporters ejected per report meeting: {rate(reporters, report_meetings)}")
if after and report_meetings:
    per = reporters / report_meetings
    if per > 0.104:
        flags.append("reporter ejections")
    print(f"    envelope: {'flagged above 0.104' if per > 0.104 else 'at or below 0.104'}")
show("role-correct ejections (reported, gates nothing)", "role_correct_ejections")
show("meetings with vent proof", "meetings_with_vent_proof")
print("balance (reported, gates nothing)")
kills = cell("kills_seen_by_crew")[1]
print(f"  kills [kills_seen_by_crew, its denominator]: {kills}")
show("impostors able to kill when a meeting opened", "impostor_cooldown_zero_at_open")
print(f"  the win split [impostor_wins]: {n - k} crew, {k} impostor")
if after and "--round-3-rule" in sys.argv and n:
    share = k / n
    step = ("round 3 at kill_cooldown_ticks = 8" if share > 0.60 else
            "round 3 at kill_cooldown_ticks = 5" if share < 0.20 else
            "the era-keyed promotion of round 2, for the owner to decide"
            if not flags and not misses else "no step")
    print(f"round-3 rule: names {step}")
if misses:
    print(f"Conf. misses: {', '.join(misses)}")
    sys.exit(1)
```

### 1.13 The re-projection command, whole

Saved as `reproject.py` and run with `python3` (standard library only,
count-only; sha256
`0a26f7e2bc9a3a63ed9f926123253c7477fe32a02f670f7671e4e6303d0c733f` as
extracted from the card), as
`python3 reproject.py replays/candidates/stage-b-r2/9p2i replays/samples/9p2i <summed recording wall, s>`.

```python
"""Re-project the round's spend against the 90% stops (count-only).

Usage: reproject.py CAND_DIR S9_DIR SUMMED_WALL_SECONDS

Each count is (the candidate's total over its completed seeds / the s9 total
over the same seeds) x the s9 leg total; the wall is the summed recording wall
/ the completed seeds x 50. Exits 1 when any figure is past its stop.
"""

import glob
import json
import re
import sys

STOPS = {"calls": 2_520, "input": 15_750_000, "output": 675_000}
WALL_STOP = 38_880  # 10.8 h


def tally(directory):
    per_seed = {}
    for path in glob.glob(directory + "/replay-seed-*.jsonl"):
        seed = int(re.search(r"replay-seed-(\d+)\.jsonl$", path).group(1))
        calls = tokens_in = tokens_out = 0
        cost = 0.0
        for row in map(json.loads, open(path)):
            for call in row.get("llm_calls") or []:
                calls += 1
                tokens_in += call["input_tokens"]
                tokens_out += call["output_tokens"]
                cost += call["cost_usd"]
        per_seed[seed] = (calls, tokens_in, tokens_out, cost)
    return per_seed


cand = tally(sys.argv[1])
s9 = tally(sys.argv[2])
wall = float(sys.argv[3])
seeds = sorted(cand)
stops = []
print(f"completed seeds {len(seeds)} ({seeds[0]}-{seeds[-1]})")
for index, name in enumerate(("calls", "input", "output")):
    done = sum(cand[s][index] for s in seeds)
    base = sum(s9[s][index] for s in seeds)
    projected = done / base * sum(v[index] for v in s9.values())
    past = projected > STOPS[name]
    stops += [name] if past else []
    print(f"  {name}: {done} / {base} x s9 = {projected:,.0f} "
          f"({projected / STOPS[name]:.1%} of the {STOPS[name]:,} stop){' STOP' if past else ''}")
wall_projected = wall / len(seeds) * 50
past = wall_projected > WALL_STOP
stops += ["wall"] if past else []
print(f"  wall: {wall:,.0f} s / {len(seeds)} x 50 = {wall_projected:,.0f} s "
      f"= {wall_projected / 3600:.2f} h (stop 10.8 h){' STOP' if past else ''}")
nonzero = [s for s in seeds if cand[s][3] != 0.0]
if nonzero:
    stops.append("cost")
    print(f"  cost: non-zero on seeds {nonzero} STOP")
if stops:
    print(f"STOP: {', '.join(stops)}")
    sys.exit(1)
```

The tally (count-only), round 1's card's Validation command carried whole:

```
uv run python -c 'import glob,json,sys
c=i=o=0; u=0.0
for p in glob.glob(sys.argv[1]+"/replay-seed-*.jsonl"):
  for r in map(json.loads,open(p)):
    for k in r.get("llm_calls") or []:
      c+=1; i+=k["input_tokens"]; o+=k["output_tokens"]; u+=k["cost_usd"]
print(c,i,o,u)' <set dir>
```
