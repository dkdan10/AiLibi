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

## 2. The pre-spend, at `F` and before the first seed

Nothing in this section called a provider. Every command ran in a bare shell
(`env | grep -c '^AILIBI_'` printed 0) unless it names its own exports, in this
branch's worktree while it was still at `F` with a clean status, except the dry
run (2.7), which ran in the recording checkout at P. Scratch outputs lived
outside the repository; every census here is count-only.

### 2.1 The preflight

- `git grep -n WAVE_ARMS_PENDING -- '*.py'` at `F`: no output, exit 1.
- The declared file, read through `scripts/_declared_experiment.py`'s own
  loader: sha256 `0c02fa61…5c192b` (1.4); nine fields off their default, round
  1's eight and `kill_cooldown_ticks`; `FIELD_LAYER["kill_cooldown_ticks"]` is
  `engine`, `OMITTED_AT_DEFAULT` holds it, and `engine_arguments` returns
  `kill_cooldown_ticks: 6` beside `vent_witness_rule: 'physical'` instead of
  raising; `prompt_versions_for_set("qwen3_6_27b", experiment_config=...)`
  serves round 1's four stamps, equal to what round 1's own config serves.
- Proof, two perturbations of the same payload: with one unknown key added,
  validation is refused (`extra_forbidden`, `('unknown_switch',)`); with
  `kill_cooldown_ticks` removed, the fields off their default number 8, and the
  config equals round 1's.
- The kill-cooldown card's refusals pass at `F`:
  `tests/orchestrator/test_experiment_arms.py::test_an_engine_field_the_helper_does_not_thread_is_refused[kill_cooldown_ticks]`
  (an unthreaded cooldown is refused by the helper),
  `tests/engine/test_kill_cooldown_override.py::test_an_invalid_value_raises_at_every_entry_point_before_any_change`
  (0, -3, `True` and 6.0 at the eight entry points) and
  `tests/engine/test_kill_cooldown_override.py::test_advance_tick_refuses_before_applying_any_action`,
  in the run of 2.8.

### 2.2 The before columns

- **s9.** `publish_gameplay_census.py --set-dir replays/samples/9p2i
  --json-stdout` exited 0 and equals the `samples/9p2i` entry of
  `docs/gameplay-census.json` in 998 of 998 leaves;
  `publish_process_scorecard.py --set-dir replays/samples/9p2i --json-stdout`
  exited 0 and equals the shipped entry in 108 of 108. `measure_baseline.py
  replays/samples/9p2i --honesty --json` exited 0. The readings command prints
  the same s9 column on the shipped file and on the `--set-dir` section
  (`cmp` equal). Proof: against a copy of the shipped census whose
  `kill_cooldowns_differing_from_recorded` denominator is raised by one, the
  leaf comparison prints one difference
  (`cells.kill_cooldowns_differing_from_recorded.denominator: set-dir=275
  shipped=276`) and exits 1; against a copy of the shipped scorecard whose
  `grounded_skip` numerator is raised by one, it prints
  `grounded_skip.numerator: set-dir=79 shipped=80` and exits 1.
- **Round 1.** The census, scorecard and honesty modes on
  `replays/candidates/stage-b-r1/9p2i` each exited 0, and the validity gate
  with round 1's declared config, `--expected-seeds 0-49` and
  `--require-one-recording-sha` exited 0 with its ten checks PASS (the
  betrayal check 0 over 717). A count-only comparison script holding every
  count round 1's audit section 6 states (6.1's scorecard rows, 6.2's Conf.
  cells, readings and reported cells, 6.3's envelope, 6.4's split) and the
  card's balance row compares 83 counts: 83 equal, 0 differing, exit 0. No
  round-1 count moved. Proof: against a copy of the round-1 census whose
  `impostor_cooldown_zero_at_open` numerator is raised by one, it prints
  `impostor_cooldown_zero_at_open: re-measured (85, 203), audit states (84,
  203)` and exits 1.
- **The cooldown cell on both.** s9 reads 0/275 against the map's 4 (round
  start 100, after a kill 175, no regroup write); round 1 reads 0/487 against
  4 (100, 227 and 160 at a regroup).
- **The tally** prints `1694 9850930 422941 0.0` on `replays/samples/9p2i` and
  `1556 9344346 433660 0.0` on round 1, the anchors' own figures.

### 2.3 The readings and re-projection proofs

`readings.py` (1.12) on scratch copies of the round-1 census section, with
round 1's honesty file:

| copy | command | result |
|---|---|---|
| unedited | `--after --round-3-rule` | exit 0; the last line `round-3 rule: names round 3 at kill_cooldown_ticks = 8` (34/50) |
| the cooldown table's `regroup` row removed | `--after --round-3-rule` | exit 1; `Conf.: BREACH (no write counted at regroup)` and `Conf. misses: kill_cooldown_writes_by_writer.regroup` |
| `stale_report_meetings` numerator raised by one | `--after --round-3-rule` | exit 1; `Conf. misses: stale_report_meetings` |
| `impostor_wins` numerator set to 20 | `--after --round-3-rule` | exit 0; `round-3 rule: names the era-keyed promotion of round 2, for the owner to decide` |
| the same, with the report row of `innocent_opener_ejections_by_trigger` set to 13 (13/118 = 0.110) | `--after --round-3-rule` | exit 0; `envelope: flagged above 0.104` and `round-3 rule: names no step` |

`reproject.py` (1.13) on a scratch copy of round 1's seeds 0-10, against
`replays/samples/9p2i`:

| copy and wall | result |
|---|---|
| unedited, 3,633 s | exit 0; calls 1,551, input 9,325,616, output 433,102, wall 16,514 s = 4.59 h: round 1's own 10-seed figures (its audit 5.4) |
| 60,000 output tokens added to one call of seed 0, 3,633 s | exit 1; output 678,541 (100.5% of the 675,000 stop) `STOP`, and `STOP: output` |
| unedited, 9,000 s | exit 1; wall 40,909 s = 11.36 h `STOP`, and `STOP: wall` |

### 2.4 The fake dress rehearsal

Seeds 0-49 on the declared config, recorded with `AILIBI_LLM_PROVIDER=fake`
into a scratch directory outside the repository:

```
AILIBI_LLM_PROVIDER=fake AILIBI_PROMPT_SET=qwen3_6_27b AILIBI_NUM_PLAYERS=9 \
AILIBI_NUM_IMPOSTORS=2 AILIBI_TASKS_PER_CREWMATE=2 AILIBI_SAMPLE_DIR=<scratch>/9p2i \
AILIBI_MANIFEST=<scratch>/9p2i/MANIFEST.md AILIBI_REFRESH_WORKERS=4 \
  bash scripts/refresh_samples.sh --full --expect-levers "" --experiment-config <scratch config copy>
```

Exit 0: 50 of 50 seeds in 25 s, `$0.0000`, 132 meetings, the report rebuilt,
every MANIFEST row naming `e87403b7`. The tally prints `1652 6409973 94990
0.0`. Each instrument then exited 0 on it:

| instrument | result |
|---|---|
| `validity_gate.py <dir> --require-zero-cost --expected-prompt-versions <the four pairs> --expected-experiment-config <config> --expected-seeds 0-49 --require-one-recording-sha` | exit 0; all ten checks PASS |
| `bash scripts/verify_samples.sh <dir>` | exit 0; "All 50 samples verified clean." |
| the golden's directory walk (`walk_directory`, count-only runner) | exit 0; 50 seeds, 132 meetings, 1,652 prompts, 0 not reproduced, 0 miscounted meetings |
| `publish_gameplay_census.py --set-dir <dir> --json-stdout` | exit 0; through the readings command with `--after`, all 17 Conf. cells read 0, and the cooldown cell reads 0/591 with a write at all three writers: round start 100, after a kill 227, at a regroup 264 |
| `publish_process_scorecard.py --set-dir <dir> --json-stdout` | exit 0 |
| `measure_baseline.py <dir> --honesty --json` | exit 0; no raise |
| `scan_recording_packets.py <dir>` | exit 0 |

The Conf. cells on the rehearsal: `vent_exits_seen_only_from_room_left` 0/86,
`vent_band_resting_only_on_room_left` 0/0, `surfacings_before_cap_in_view`
0/86, `trips_longer_than_cap` 0/68, `vent_entries_not_after_own_fresh_kill`
0/165, `stale_report_meetings` 0/128, `report_corpses_older_than_last_close`
0/78, `play_resumes_with_impostor_in_vent` 0/132, `play_resumes_with_corpse`
0/132, `kills_in_grace_window_after_regroup` 0/141 (T+1 to T+6),
`rebuttals_differing_from_selector` 0/0, `meetings_with_second_repeat_speaker`
0/132, `report_openings_with_kill_tick_handle` 0/128,
`own_kill_rows_breaching` 0/25, `recorded_teammate_ballot_targets` 0/264,
`impostor_openers` 0/132 and `kill_cooldowns_differing_from_recorded` 0/591. A
fake meeting fires no rebuttal, so the meeting arms are proved by 2.5, not here.

Proof: gated against round 1's config, the gate exits 1 and fails
`cost_and_provenance_exact` on 50 of 50 games, each line naming the recorded
`kill_cooldown_ticks` that round 1's config lacks.

### 2.5 The scripted rehearsal

At `F`, round 1's scripted and ballot-arm cases pass:
`tests/_helpers/test_scripted_meeting.py` (the one rebuttal),
`tests/meetings/test_ballot_arms.py` (impostor EJECTs with and without a row
pointing toward the target, the kill row, the teammate coercion,
`test_without_the_coercion_the_betrayal_check_fails` and
`test_the_golden_fails_when_a_bound_arm_value_is_dropped`) and
`tests/eval/test_recorded_arm_readers.py`, in the run of 2.8; and the golden's
`test_the_scripted_rebuttal_game_re_renders_byte_equal`, whose perturbed half
drops the recorded evidence profile and leaves the rebuttal call unconsumed,
`test_dropping_the_recorded_reset_fails_the_meeting_post_hash` and
`test_the_kill_row_gate_forced_on_fails_the_golden_at_the_kill_holders`, all
passed (6 passed with `test_the_retired_guard_pins_are_keyed_by_the_path_under_replays`
and the two audit-index cases).

The scratch scripted game, recorded from the declared file. The ballot card's
whole script (`record_ballot_arms_game`, seed 26) takes the declared config,
but under the longer cooldown the game runs differently: before the first
ballot, crewmate p-1 has not watched p-3 kill, so the script's first ballot,
which must cite that kill row, raises (`the ballot prompt serves no
own_kill_row row about p-3`). The helper refuses rather than record an id the
voter was not served, as it is built to. So the rehearsal recorded the same
seed through the same helper (`record_game` with `ScriptedMeetingClient`) with
the ballot card's two scripted accusations and its four scripted ballots that
cite nothing (the teammate ballot the meeting layer coerces to a skip, an
impostor ballot naming a crewmate without a row, and two crewmate ballots
below the tally's floor):

| check | result |
|---|---|
| the recording | 3 meetings; both scripted accusations fired; recorded config `0c02fa61…` on every row |
| `verify_samples.sh <dir>` (the plain loader) | "All 1 samples verified clean." |
| census `--set-dir` | exit 0; the 2 rebuttals counted once each: `meetings_with_repeat_speaker` 2/3, `meetings_with_second_repeat_speaker` 0/3, `rebuttals_differing_from_selector` 0/2, beneficiaries "the opener, answering an impostor" 2; authored teammate targets 1/6 and recorded 0/6; the cooldown cell 0/12 with writes at round start 2, after a kill 4 and at a regroup 6; every Conf. cell 0 |
| scorecard `--set-dir` | exit 0 |
| `validity_gate.py <dir> --require-zero-cost --expected-prompt-versions <the four pairs> --expected-experiment-config <config> --expected-seeds 26 --require-one-recording-sha` | exit 0; ten checks PASS |
| the golden's directory walk | 3 meetings, 40 prompts, 0 not reproduced, 0 miscounted meetings |
| honesty and the packet scan | exit 0 each |

The kill row and an impostor EJECT do not occur in this one game (no voter
watched a kill before a ballot, and no scripted impostor EJECT landed); they
are proved by the ballot-arm cases above.

### 2.6 The lab attribution matrix

```
uv run python -m experiments.tactical_gameplay --output <scratch>/lab-F.json --split development \
  --arms baseline vent_risk vent_physical vent_look_and_wait vent_own_fresh_kill stage_b_full \
    stage_b_full_minus_look_and_wait stage_b_full_minus_own_fresh_kill \
    stage_b_full_minus_physical stage_b_full_minus_hub_with_grace \
    stage_b_full_kill_cooldown_6 stage_b_full_kill_cooldown_8
```

Run at `F` (`git_head` `e87403b778649dae35a0a09e297752160d92d0c1`,
`source_sha256` `3da4e260f08d4e59f2ba9daa7d18ffb8a28e67a08fad28cc71c88c0568a0a197`)
on development seeds 1000-1007 of both rosters, with the lab's injected
deterministic fake: no provider, no spend, written to scratch. **Proof:** the
ten round-1 arms' rows equal `audits/tactical-gameplay/stage-b-r1-frozen-head.json`
field for field: 14,052 fields compared, 0 differing. Against a copy with one
counter edited (`stage_b_full`, 9p2i seed 1000, `applied:IMPOSTOR:kill` 5 to 6)
the comparison prints that one field and exits 1. The output's only new
top-level key is `ticks_to_parity`; it stays in scratch, and
`audits/tactical-gameplay/` is not edited.

The cooldown arms, mechanical attribution only (fake outcomes are not
model-quality evidence), 9p2i then 4p1i:

| arm | games | games ending at impostor parity | parity tick rows min / median / max | kills | impostor wins |
|---|---|---|---|---|---|
| `stage_b_full` (the map's 4) | 8; 8 | 8; 7 | 26 / 35.5 / 58; 14 / 17 / 19 | 40; 15 | 8; 7 |
| `stage_b_full_kill_cooldown_6` | 8; 8 | 7; 1 | 30 / 44 / 68; 18 / 18 / 18 | 39; 8 | 7; 1 |
| `stage_b_full_kill_cooldown_8` | 8; 8 | 3; 0 | 49 / 52 / 58; n/a | 30; 2 | 3; 0 |

### 2.7 The dry run, in the recording checkout at P

The recording checkout is a worktree detached at P (`43b5ee45`), outside the
repository's working tree, with `uv sync --frozen`, no `.env`, and an
untracked copy of the declared file at
`replays/candidates/stage-b-r2/experiment-config.json` whose `shasum -a 256`
prints `0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b`. The
recording shell's exports (1.8), and nothing else (the dry run ran under
`env -i` with only `HOME`, `PATH` and `TERM` beside them):

```
bash scripts/refresh_samples.sh --full --expect-levers "" \
  --experiment-config replays/candidates/stage-b-r2/experiment-config.json --dry-run
```

Exit 0, and its resolved configuration (the model-coupling, registry,
lever-preflight, per-seed stage and full-mode clean-up lines and the full seed
list elided; the run printed them):

```
[dry-run] Experiment config: replays/candidates/stage-b-r2/experiment-config.json (sha256 0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b)
[dry-run] Experiment config settings: meeting_reset='hub_with_grace', vent_exit_policy='look_and_wait', bounded_rebuttal_version=1, vent_witness_rule='physical', vent_entry_policy='own_fresh_kill', report_body_handle_version=1, ballot_kill_row_version=1, impostor_ballot_version=1, kill_cooldown_ticks=6
[dry-run] Experiment switch exports: none
[dry-run] mode: full
[dry-run] roster: num_players=9 num_impostors=2 tasks_per_crewmate=2
[dry-run] roster descriptor: would ensure replays/candidates/stage-b-r2/9p2i/roster.json = {num_players: 9, num_impostors: 2, tasks_per_crewmate: 2} (fails loud if an existing one disagrees)
[dry-run] sample dir: replays/candidates/stage-b-r2/9p2i
[dry-run] provider: featherless
[dry-run] preflight: would require FEATHERLESS_API_KEY (hosted run; $0 provider-keyed cost)
[dry-run] meeting model: Qwen/Qwen3.6-27B
[dry-run] prompt set: qwen3_6_27b
[dry-run] substrate flags: expected levers ON = (none — the bare slate: every live toggle OFF); every other live toggle OFF; the graduated levers unconditional ON
[dry-run] seed workers: 2 parallel (each records one seed, then pulls the next available seed from the queue; Featherless: 2 units per 32B request → 4-unit cap)
[dry-run] seed crash-retry: up to 8 attempt(s) per seed on a transport/crash error (recorded parse failures are non-fatal)
[dry-run]   AILIBI_LLM_PROVIDER=featherless uv run python scripts/run_tournament.py --start-seed <seed> --num-games 1 --output-dir <stage> --num-players 9 --num-impostors 2 --tasks-per-crewmate 2 --force --experiment-config <stage-dir>/experiment-config.json
[dry-run] experiment config: would copy replays/candidates/stage-b-r2/experiment-config.json into the stage directory once, if it still reads sha256 0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b, and pass that copy to every seed
[dry-run] manifest: replays/candidates/stage-b-r2/9p2i/MANIFEST.md
[dry-run] eval report: would rebuild replays/candidates/stage-b-r2/9p2i/tournament-eval-report.json.gz from the refreshed replays (scripts/build_sample_report.py; $0, no provider)
[dry-run] no API calls made; no files written.
Substrate slate OK: expected levers ON = (none — the bare slate: every live toggle OFF); every other live toggle OFF; the graduated levers unconditional ON.
```

The porcelain status read the same one line before and after the dry run, the
untracked declared copy (`?? replays/candidates/stage-b-r2/`), and with
untracked files hidden it read 0 lines: the dry run wrote nothing. Proof: the
same dry run with a stray `AILIBI_BOUNDED_REBUTTAL=1` exported exits 1 with
"Refused: the environment exports AILIBI_BOUNDED_REBUTTAL. A recording takes
its experimental switches only from a declared config file
(--experiment-config), so unset these variables before recording. Nothing was
staged."

### 2.8 The planted proofs at `F`

```
.venv/bin/pytest -q -n 6 tests/engine/test_kill_cooldown_override.py tests/eval/test_kill_cooldown_readers.py \
  tests/orchestrator/test_experiment_arms.py tests/orchestrator/test_experiment_config.py \
  tests/eval/test_gameplay_census.py tests/scripts/test_candidate_sets.py \
  tests/_helpers/test_scripted_meeting.py tests/meetings/test_ballot_arms.py tests/eval/test_recorded_arm_readers.py
```

844 passed, exit 0. Among them: the census card's planted breach per Conf.
cell (`test_every_guarded_cell_has_a_planted_pair` and the 19
`test_a_breach_raises_with_the_setting_on_and_publishes_with_it_off` cases);
the kill-cooldown card's planted breaches,
`test_a_write_left_at_the_maps_value_breaches_the_cell_naming_its_writer[round_start-orchestrator.seeder]`,
`[after_kill-engine.tick]` and `[regroup-engine.meeting_reset]`,
`test_a_kill_at_meeting_plus_five_breaches_the_grace_window_at_six` and
`test_the_same_kill_in_the_default_cooldown_era_raises_nothing`
(`tests/eval/test_kill_cooldown_readers.py`); and the record-plumbing card's
planted round perturbations in `tests/scripts/test_candidate_sets.py`
(`test_one_byte_of_the_config_fails_the_declared_sha`,
`test_a_missing_seed_fails`, `test_a_foreign_recording_sha_fails`,
`test_a_mixed_config_fails`, `test_one_edited_report_cell_fails` and the rest).
The golden and audit-index cases of 2.5 ran separately: 6 passed, exit 0,
among them `test_audits_index_ladder_tip_drift_detected` and
`test_unindexed_audit_detected`.

### 2.9 The key, and the count-only scan

`FEATHERLESS_API_KEY` lives only in the main checkout's untracked `.env`. Its
one line was copied by a `grep` whose output went straight to the file and was
never printed, into a mode-0600 file in a mode-0700 directory outside every
checkout; a count-only `grep -c` on the source found 1 matching line, and on
the copy 1 non-empty value. Every live leg runs `uv run --env-file <that file>
bash scripts/refresh_samples.sh ...`; no step reads `.env` itself.

The scan (`keyscan.py`, count-only, gzip decompressed) counts seven patterns
over every file changed since `F` (committed, staged or untracked): the exact
value, its first eight characters (what the recorder prints into its own log),
and five generic credential shapes (a key assignment, a bearer token, two
secret-key prefixes and an API-key field). Before the pre-spend push it read 0
over the 5 files changed since `F`. Proof: one planted scratch file per
pattern, each scanned alone, fires its own pattern and exits 1 (the exact-value
plant, gzip-compressed, also fires the prefix and one generic shape); the
plants were deleted after the run.

## 3. The probe (2026-10-01)

### 3.1 Seeds 0-1, and the failed seed

The sitting's 18 h window opened with the probe's first seed at
2026-10-01T10:55:33Z; it closes at 2026-10-02T04:55:33Z. The pause file was
absent. Seeds 0-1 recorded as one leg on the leg's two workers in the
recording checkout at P, with the shell of 1.8 and the key passed by
`uv run --env-file`:

```
<the 1.8 exports> uv run --env-file <key file> bash scripts/refresh_samples.sh \
  --seeds 0,1 --expect-levers "" --experiment-config replays/candidates/stage-b-r2/experiment-config.json
```

It exited 0 at 11:06:27Z: "Refresh complete in 10m53s" (653 s), seed 0 in 646 s
and seed 1 in 653 s, `$0.0000`, no retry and no `WARN` line in the run log.

**Event: seed 1, a `(deadline_default)` re-record, cause logged as it
happened.** The probe's validity gate failed `cost_and_provenance_exact`
(`model provenance ['(deadline_default)', 'Qwen/Qwen3.6-27B'] != expected`),
and `grep -l deadline_default` named seed 1. Seed 1 held one `failed_call` row
of type `deadline_default` in its second meeting, at tick 29, whose message
reads "opt_in turn (turn 4) defaulted (validation); p-6 submitted no turn",
beside one `ValidationError` row at the same meeting and tick (an alibi claim
whose route segments overlapped). It is round 1's seed-31 event again: the
opt-in turn's answer failed validation and the turn fell back to a default
instead of model output. Every conformance cell still read 0 on it. By 1.7's
failed-seed rule the husk was moved out of the set, outside the repository,
and seed 1 alone was re-recorded at P (11:07:37Z to 11:14:07Z, "Refresh
complete in 6m29s", 389 s, exit 0, no `failed_call` row). The husk had spent 45
calls, 282,575 input and 12,531 output at `0.0000`; that spend is counted in
the round's spend (5.2) and is not in the set.

### 3.2 The probe's gates

Run in the delivery checkout on its copy of seeds 0-1, in a bare shell (0
`AILIBI_*` exports), with the declared file's sha256 re-checked
(`0c02fa61…5c192b`):

| gate | result |
|---|---|
| `validity_gate.py <dir> --expected-model Qwen/Qwen3.6-27B --require-zero-cost --expected-prompt-versions <the four pairs> --expected-experiment-config <config> --expected-seeds 0-1 --require-one-recording-sha` | exit 0; all ten checks PASS (first run, before the re-record: exit 1 on `cost_and_provenance_exact`, 3.1) |
| `bash scripts/verify_samples.sh <dir>` | exit 0; "All 2 samples verified clean." |
| the golden's directory walk | exit 0; 7 meetings, 85 prompts, 0 not reproduced, 0 miscounted meetings |
| census `--set-dir <dir> --json-stdout` | exit 0; through the readings command with `--after`, every Conf. cell reads 0, and the cooldown cell 0/21 with writes at round start 4, after a kill 9 and at a regroup 8 |
| scorecard `--set-dir <dir> --json-stdout` | exit 0 |
| `measure_baseline.py <dir> --honesty --json` | exit 0; no raise |
| `scan_recording_packets.py <dir>` | exit 0 |
| `grep -l deadline_default` | 0 files |
| MANIFEST | one `git_sha`, `43b5ee45` (P) |
| the key scan | 0 over the 10 files changed since `F` |

Seeds 0-1 held 7 meetings and a fired rebuttal in each of them
(`meetings_with_repeat_speaker` 7/7, `rebuttals_differing_from_selector` 0/7),
so the probe did not extend, and the batches ran the first list of 1.8. The
counts of two games are no reading and none is drawn here.

### 3.3 The re-projection after the probe

By 1.6's rule over seeds 0-1 (s9's seeds 0-1: 78 calls, 475,960 input and
19,093 output), with the summed recording wall of the probe and the re-record:

| limit | round 2 / s9, seeds 0-1 | projected | share of the 90% stop |
|---|---|---|---|
| model calls | 85 / 78 | 1,846 | 73.3% |
| input tokens | 546,811 / 475,960 | 11,317,331 | 71.9% |
| output tokens | 23,202 / 19,093 | 513,962 | 76.1% |
| recording wall | 1,042 s / 2 seeds x 50 | 26,050 s = 7.24 h | against the 10.8 h stop |
| marginal cost | every `cost_usd` is 0.0 | | |

Every figure was inside its stop. The probe's projected wall is 7.24 h, so 1.5
times it (10.86 h) lies past the 10.8 h stop, which binds first, as in round 1;
the probe leg's own 653 s alone would have projected 4.53 h. For context only:
over round 1's seeds 0-1 the round ran 1.31x the calls, 1.31x the input and
1.25x the output. Before the re-record, with the husk still in the set, the
same rule read calls 2,020 (80.1%), input 12,555,817 (79.7%) and output 578,468
(85.7%), also inside every stop.

The probe was checkpointed as `0509b45d` after a count-only key scan.

## 4. The batches (2026-10-01, one sitting)

### 4.1 The legs

Each batch was `uv run --env-file <key file> bash scripts/refresh_samples.sh
--seeds <the batch> --expect-levers "" --experiment-config
replays/candidates/stage-b-r2/experiment-config.json` with the 1.8 exports, in
the recording checkout still detached at P (`43b5ee45`); the untracked declared
copy read `0c02fa61…5c192b` before every leg (the leg runner refuses a
mismatch), and the pause file was checked before every leg and was absent each
time, so the sitting never paused. Wall is the recorder's own "Refresh
complete in" figure; calls and tokens are the tally of the leg's seeds as they
stand in the committed set. No leg ran pytest or `check.sh` in the recording
checkout, and no commit was made there.

| leg | seeds | UTC | recording wall | calls | input | output | checkpoint |
|---|---|---|---|---|---|---|---|
| probe | 0-1 | 10:55:33-11:06:27 | 653 s | 85 (seed 1 as re-recorded) | 546,811 | 23,202 | `0509b45d` |
| seed 1 again | 1 | 11:07:37-11:14:07 | 389 s | (in the probe) | | | `0509b45d` |
| batch 1 | 2-6 | 11:15:51-11:31:17 | 924 s | 135 | 831,947 | 39,026 | `e720632d` |
| batch 2 | 7-11 | 11:32:41-11:49:13 | 990 s | 152 | 891,880 | 38,876 | `415ba1fe` |
| batch 3 | 12-16 | 11:50:28-12:08:31 | 1,081 s | 130 | 769,106 | 35,277 | `2af09014` |
| batch 4 | 17-21 | 12:09:24-12:32:03 | 1,358 s | 168 | 1,033,852 | 47,287 | `51924fc2` |
| batch 5 | 22-26 | 12:32:57-12:58:29 | 1,529 s | 162 | 1,000,010 | 46,729 | `eac32e55` |
| batch 6 | 27-31 | 12:59:35-13:12:09 | 751 s | 115 | 682,603 | 33,225 | `eb2d1eca` |
| batch 7 | 32-36 | 13:13:12-13:29:49 | 994 s | 145 (seed 36 as re-recorded) | 903,622 | 41,112 | `fd577159` |
| seed 36 again | 36 | 13:30:44-13:34:55 | 247 s | (in batch 7) | | | `fd577159` |
| batch 8 | 37-41 | 13:36:19-13:56:22 | 1,199 s | 173 | 1,068,824 | 47,817 | `fd5868d1` |
| batch 9 | 42-46 | 13:57:26-14:24:26 | 1,616 s | 114 | 684,873 | 33,487 | `3004a3e2` |
| batch 10 | 47-49 | 14:26:15-14:46:15 | 1,196 s | 123 | 774,352 | 32,232 | `a8e22538` |
| **the round** | 0-49 | | **12,927 s** | **1,502** | **9,187,880** | **418,270** | |

After every leg, in the delivery checkout and a bare shell (0 `AILIBI_*`
exports): the validity gate with the declared config and `--expected-seeds
0-N`, `verify_samples.sh`, the golden's walk, the census (every Conf. cell read
0 at every checkpoint, the cooldown cell at all three writers), the scorecard
fold, `measure_baseline.py --honesty` (no raise at any checkpoint),
`scan_recording_packets.py`, the tally, the re-projection and the count-only
key scan (0 at every push) all exited 0, except the two gate failures of 4.2,
each cleared by the failed-seed rule before its checkpoint was committed. Every
checkpoint's MANIFEST named the one sha `43b5ee45`.

### 4.2 Events

1. **Seed 1, a `(deadline_default)` re-record** (3.1).
2. **Seed 36, a `(deadline_default)` re-record, cause logged as it
   happened.** Batch 7 exited 0, but its gate failed
   `cost_and_provenance_exact` in the same way: seed 36 held one `failed_call`
   row of type `deadline_default` in its third meeting, at tick 42 ("opt_in
   turn (turn 2) defaulted (validation); p-7 submitted no turn"), beside a
   `ValidationError` row at the same meeting and tick (an alibi claim whose
   route segments overlapped). Every conformance cell still read 0 on it. The
   husk was moved outside the repository, and seed 36 alone was re-recorded at
   P (247 s, exit 0, no `failed_call` row) before the checkpoint was committed.
   The husk had spent 41 calls, 255,772 input and 10,291 output at `0.0000`.
3. **One retry, no stall.** In batch 9, seed 45's first attempt failed on an
   empty completion (`RuntimeError: Featherless response carried no choices`,
   which the client refuses to record), and the recorder's second attempt
   recorded it (seed 45 took 1,190 s). This is the transport retry the
   8-attempt budget exists for; it did not survive the budget, so it is no
   stop. The failed attempt's stage was discarded, so its calls are in no
   committed byte and no tally (8). No leg went 45 minutes without a completed
   seed (the longest seed took 1,190 s), the pause file never existed, and no
   other recorder log carries a `WARN` line or a refusal. Across the 50
   committed seeds there is no `failed_call` row at all.
4. **A stale inventory row at one checkpoint.** At `e720632d` the commit
   helper's pattern matched two rows of `docs/artifacts.md`, refused to rewrite
   either, and the commit kept the 63-file candidates row (offline
   `verify_ml_evidence.py` fails that row at that commit). The helper was
   corrected to match the candidates row alone and to stop before committing on
   a failed inventory check; every later checkpoint re-derived the row and
   passed it. No recorded byte was involved.
5. **No stop fired.** Every `cost_usd` is `0.0000`, and no re-projection came
   near a stop (4.3).

### 4.3 The re-projection at every checkpoint

By 1.6's rule; each figure is the projected leg total and its share of the
90% stop. The pre-registered 10-seed re-projection is the first checkpoint
holding at least 10 seeds, seeds 0-11.

| checkpoint | seeds | calls | input | output | summed wall | projected wall |
|---|---|---|---|---|---|---|
| the probe | 0-1 | 1,846 (73.3%) | 11,317,331 (71.9%) | 513,962 (76.1%) | 1,042 s | 7.24 h |
| batch 1 | 0-6 | 1,620 (64.3%) | 9,965,360 (63.3%) | 440,976 (65.3%) | 1,966 s | 3.90 h |
| **batch 2, the 10-seed re-projection** | 0-11 | 1,439 (57.1%) | 8,576,341 (54.5%) | 382,786 (56.7%) | 2,956 s | 3.42 h |
| batch 3 | 0-16 | 1,529 (60.7%) | 9,243,370 (58.7%) | 412,618 (61.1%) | 4,037 s | 3.30 h |
| batch 4 | 0-21 | 1,499 (59.5%) | 9,094,958 (57.7%) | 410,872 (60.9%) | 5,395 s | 3.41 h |
| batch 5 | 0-26 | 1,512 (60.0%) | 9,223,760 (58.6%) | 419,818 (62.2%) | 6,924 s | 3.56 h |
| batch 6 | 0-31 | 1,453 (57.7%) | 8,862,360 (56.3%) | 405,470 (60.1%) | 7,675 s | 3.33 h |
| batch 7 | 0-36 | 1,468 (58.3%) | 8,982,608 (57.0%) | 413,450 (61.3%) | 8,916 s | 3.35 h |
| batch 8 | 0-41 | 1,486 (59.0%) | 9,084,983 (57.7%) | 415,957 (61.6%) | 10,115 s | 3.34 h |
| batch 9 | 0-46 | 1,449 (57.5%) | 8,815,856 (56.0%) | 405,771 (60.1%) | 11,731 s | 3.47 h |
| batch 10 | 0-49 | 1,502 (59.6%) | 9,187,880 (58.3%) | 418,270 (62.0%) | 12,927 s | 3.59 h |

Beside it, for context only: over round 1's same seeds the round ran 1.31x
round 1's calls at the probe, 0.93x at seeds 0-11, and 0.965x the calls,
0.983x the input and 0.965x the output over all 50.

## 5. The round's gates, and its spend

### 5.1 The gates on the whole round

In the delivery checkout, bare shell, at the recorded bytes:

| gate | result |
|---|---|
| `validity_gate.py <round> --expected-model Qwen/Qwen3.6-27B --require-zero-cost --expected-prompt-versions <the four pairs> --expected-experiment-config <config> --expected-seeds 0-49 --require-one-recording-sha` | exit 0, ten checks PASS: `all_games_reach_game_over` (50/50), `meeting_rate_and_resolution` (1.0; 117 resolved, 0 unresolved), `no_duplicate_meeting_rows` (0 of 117), `no_tick_1_kills` (0), `no_friendly_fire_kills` (0), `no_betrayal_ballots_or_accusations` (0 of 691), `no_railroaded_crew_ejections` (0 of 2,341), `no_dangling_primary_reason_id` (0 of 691), `cost_and_provenance_exact` (one model, four prompt versions, the declared config, seeds 0-49, one sha), `byte_identical_reconstruction` (0 drifted) |
| proof: the same gate with `--expected-seeds 0-50` | exit 1: `cost_and_provenance_exact`, "missing [50]" for the replay files and the MANIFEST rows |
| proof: round 1 against this round's config | exit 1: `cost_and_provenance_exact`, 50 lines naming the `kill_cooldown_ticks` round 1 did not record |
| `bash scripts/verify_samples.sh` (bare), then once per set directory | bare: exit 0, four sets clean (the two sample sets and both rounds); `samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i` (150), `ml_corpus/4p1i`, round 1 and this round: each exit 0, all clean |
| `build_sample_report.py --sample-dir <dir> --check`, each of the six | exit 0 each; this round's report gz is the recorder's post-step rebuild through `eval/report_io.py` |
| the golden's directory walk | exit 0: 50 seeds, 117 meetings, 1,502 prompts, 0 not reproduced, 0 miscounted meetings; retired-guard census (117, 691, 0, 0) |
| census `--set-dir <round> --json-stdout` | exit 0: every Conf. cell reads 0 (6.2) |
| scorecard `--set-dir <round> --json-stdout` | exit 0 |
| `measure_baseline.py <round> --honesty --json` | exit 0; no raise |
| `scan_recording_packets.py <round>` | exit 0 |
| `grep -l deadline_default` over the 50 replays | 0 files |
| MANIFEST columns | 50 rows, seeds 0-49: model `Qwen/Qwen3.6-27B`, policy `fsm-default`, `git_sha` `43b5ee45`, cost `0.0000`, the four prompt versions; the flags column equals s9's (one value on every row of each) |
| proof: the round pooled through the census (`fold_set` then `pool`) with s9, and with round 1 | each folds alone; pooled, `GameplayCensusEraError`, "two eras differ in settings; the census never pools across eras", both times |
| `git merge-base --is-ancestor 43b5ee45 43b5ee45` (P against the MANIFEST's one sha); `git merge-base --is-ancestor e87403b7 43b5ee45` (`F` against P) | exit 0 each. Proof: the head `a8e22538` in place of P, exit 1 |
| the pre-registration section at P against the head | 668 lines, 0 differing (the comparison drops the blank line that separates the section from the next heading). Proof: "0.30" edited to "0.31" in one reading of a scratch copy, 2 differing lines, exit 1 |

The freeze held: `git log --oneline e87403b7..HEAD` and `e87403b7..origin/main`
print nothing over `engine agents meetings observation orchestrator eval api
scripts llm` (`main` is still at `e87403b7`); proof, the same pathspec over
`f937dfaa..e87403b7` prints 1 commit, the kill-cooldown card's. `git diff --stat
e87403b7..HEAD` is empty over `replays/samples`, `replays/ml_corpus`, round 1's
directory, `tests/fixtures`, `training`, `api`, `frontend` and the scorecard
and census documents.

### 5.2 The spend against the ceilings

Spent, including the two husks (the set's own tally is `1502 9187880 418270
0.0`):

| limit | the set | the two husks | spent | ceiling | share | 90% stop |
|---|---|---|---|---|---|---|
| model calls | 1,502 | 86 | 1,588 | 2,800 | 56.7% | 2,520 |
| input tokens | 9,187,880 | 538,347 | 9,726,227 | 17,500,000 | 55.6% | 15,750,000 |
| output tokens | 418,270 | 22,822 | 441,092 | 750,000 | 58.8% | 675,000 |
| recording wall | | | 12,927 s (3.59 h), both re-records included | 12 h | 29.9% | 10.8 h |
| marginal cost | $0.0000 | $0.0000 | $0.0000 | $0.00 | | any non-zero |

The round ran in one sitting: its 18 h window opened at 10:55:33Z, and the last
seed finished at 14:46:15Z, 3 h 50 min 42 s into it. The round held 117 meetings
against s9's 145 and round 1's 124 on the same seeds, at 12.84 calls and
78,529 input tokens per meeting. The husks' figures come from the same tally
over the husk files, kept outside the repository. Outside the tally, as for
s9 and round 1: the husks' 5 `failed_call` rows carry 13,511 input and 1,919
output tokens, and the discarded first attempt of seed 45 left no bytes to
count.

### 5.3 Nothing publishes, and the key

- `git diff --stat e87403b7..HEAD` over the committed sets, round 1, fixtures,
  training, `api`, `frontend` and the scorecard and census documents is empty
  (5.1). `publish_process_scorecard.py --check`, `publish_gameplay_census.py
  --check` and `check_doc_facts.py` exit 0, and `scripts/check_doc_facts.py`,
  which holds `_LADDER_TIP_AUDIT`, is unchanged since `F`.
- The demo bundle built at `F` (a worktree detached at `e87403b7`) and at the
  head, each with the sample replays' mtimes pinned to the same instant (the
  loader takes `created_at` from the file mtime), holds 194 files each, and
  `diff -r` exits 0.
- The key scan read 0 at every push, over every file changed since `F`. The
  key file was deleted after the last push; the card's Results records when.

## 6. The assessment

The round-2 column is this round alone, computed only from 1.9's named sources
and never pooled with another column: the census and scorecard `--set-dir
replays/candidates/stage-b-r2/9p2i --json-stdout`, `measure_baseline.py
replays/candidates/stage-b-r2/9p2i --honesty --json` and the validity gate's
`no_betrayal_ballots_or_accusations`. Each reading is what 1.12's command,
unchanged, prints:

```
python3 readings.py census-stage-b-r2.json honesty-stage-b-r2.json --after --round-3-rule   # exit 0
```

Rates carry Wilson 95% intervals. One key separates rounds 1 and 2, but both
are single hosted recordings, so a difference between them is the dial's only
within hosted-generation noise; only the Conf. cells and the lab's rows (2.6)
attribute a mechanism.

### 6.1 The process cells

The scorecard's rows. They move with the game, and none is a gate.

| row | s9 at baseline 9 | round 1 | round 2 |
|---|---|---|---|
| games; meetings; ballots (EJECT, SKIP) | 50; 145; 845 (496, 349) | 50; 124; 717 (387, 330) | 50; 117; 691 (410, 281) |
| 1 grounded decisions, EJECT | 494/496 = 0.996 (0.99-1.00) | 384/387 = 0.992 (0.98-1.00) | 407/410 = 0.993 (0.98-1.00) |
| 1 grounded decisions, SKIP | 79/349 = 0.226 (0.19-0.27) | 54/330 = 0.164 (0.13-0.21) | 44/281 = 0.157 (0.12-0.20) |
| 1 grounded decisions, all ballots | 573/845 = 0.678 (0.65-0.71) | 438/717 = 0.611 (0.57-0.65) | 451/691 = 0.653 (0.62-0.69) |
| 2 EJECTs deviating from the voter's own suspicion argmax | 31/413 = 0.075 (0.05-0.10) | 67/275 = 0.244 (0.20-0.30) | 65/292 = 0.223 (0.18-0.27) |
| 2 role-correct, followers vs deviators (chance) | 359/382 vs 3/31 (0.298) | 200/208 vs 5/67 (0.327) | 215/227 vs 4/65 (0.340) |
| 3 manufactured contradiction | 0/17, all 17 not evaluable | 0/22, all 22 not evaluable | 1/15, 14 not evaluable |
| 4 unexplained decisions | 5/845 = 0.006 | 7/717 = 0.010 | 11/691 = 0.016 (0.01-0.03) |
| 5 evidence-quality mix over ejections | contradiction flag 2, first hand 16, hearsay 2, vent flag 70 (of 90) | 2, 27, 1, 24 (of 54) | 2, 39, 1, 24 (of 66) |
| 6 rationale faithfulness (tokens) | 708/708 (137 not evaluable) | 588/588 (129 not evaluable) | 580/580 (111 not evaluable) |
| 7 agent-authored share | 841/845 = 0.995 (invalid target 3, teammate coerced 1) | 701/717 = 0.978 (teammate coerced 16) | 674/691 = 0.975 (invalid target 1, teammate coerced 16) |
| 8 wrong-but-believable, reported and never penalised | 119/496 = 0.240 | 178/387 = 0.460 | 189/410 = 0.461 |
| 9 role-correct ejection, reported and never a gate | 81/90 = 0.900 | 39/54 = 0.722 | 44/66 = 0.667 (0.55-0.77) |

### 6.2 Each arm: its Conf. cells, then its reading

**Every Conf. cell reads 0 as built**, the cooldown cell included. The census
exits non-zero on any breach; it exited 0 on the round, and the readings
command with `--after` exited 0 with no Conf. miss.

| arm | Conf. cell | s9 at baseline 9 | round 1 | round 2 |
|---|---|---|---|---|
| physical witness | exits seen only from the room left | 9/85 | 0/72 | **0/72** |
| physical witness | vent-band ejections resting only on them | 8/70 | 0/24 | **0/24** |
| look and wait | surfacings before the cap with a non-teammate in the inferred-visible set | 52/85 | 0/72 | **0/72** |
| look and wait | trips over the cap | 0/0 | 0/63 | **0/66** |
| own fresh kill | entries not after the impostor's own fresh kill | 13/105 | 0/142 | **0/140** |
| full reset | stale report meetings | 43/135 | 0/118 | **0/114** |
| full reset | reported corpses older than the last regroup | 0/0 | 0/68 | **0/64** |
| full reset | play resumes with an impostor in a vent | 10/107 | 0/110 | **0/102** |
| full reset | play resumes with a corpse | 60/107 | 0/110 | **0/102** |
| full reset | kills in the grace window after a regroup | 0/0 | 0/139 (T+1 to T+4) | **0/109** (T+1 to T+6) |
| one reply | rebuttals the selector would not have chosen | 0/0 | 0/121 | **0/117** |
| one reply | meetings with a second repeat-speaker turn | 0/145 | 0/124 | **0/117** |
| body handle | report openings carrying the kill-tick handle | 135/135 | 0/118 | **0/114** |
| kill row | own-kill rows naming a teammate or held by a non-witness | 0/0 | 0/4 | **0/23** |
| impostor ballot | recorded teammate ballot targets | 0/210 | 0/203 | **0/200** |
| impostor ballot | the gate's `no_betrayal_ballots_or_accusations` | 0 of 845 | 0 of 717 | **0 of 691** |
| self-report off | impostor openers | 0/145 | 0/124 | **0/117** |

The two full-reset cells no named source carries (false resume perceptions,
the regroup notice) stay **not carried**: what stands behind them is the one
resume helper and the notice fold, re-rendered byte-equal by the golden's walk
over all 1,502 recorded prompts.

**Physical witness.** Conf. cells only; both read 0. As built.

**Look and wait.** Exits seen from the exit room: 53/85 = 0.624 (0.52-0.72),
8/72 = 0.111 (0.06-0.20), and **8/72 = 0.111 (0.06-0.20)**. By 1.9's rule
(0.30 or below) the reading is **effective**. Beside it: exits into a room the
impostor could see a crewmate in, 31/85, 0/72 and 0/72. Reported: forced exits
at the cap 0/0, 13/72 and 5/72 = 0.069 (0.03-0.15); ticks inside per surfaced
trip, s9 85 at 1 tick, round 1 1 tick 51, 2 ticks 6, 3 ticks 2, 4 ticks 13,
round 2 1 tick 49, 2 ticks 3, 3 ticks 15, 4 ticks 5; in-place surfacings a
crewmate reaches 0/0, 2/37 and 2/44 = 0.045 (0.01-0.15); kills within 2 ticks
of the killer's surfacing 3/175, 0/227 and 0/195.

**Own fresh kill.** Conf. cell only; 13/105, 0/142 and 0/140. As built.

**Full reset.** Conf. cells all 0, the grace window now running to T+6;
regroup notice and false resume perceptions not carried (above). Reported:
skipped report meetings 55/135 = 0.407, 70/118 = 0.593 and 51/114 = 0.447
(0.36-0.54); meetings per game 2.90, 2.48 and 2.34; trips closed by a regroup
n/a, 46/142 and 47/140 = 0.336; kill-witness button calls within 6 ticks of a
regroup n/a, 0/6 and 0/3; trigger-tick events a regroup dropped n/a, `Moved`
51, `TaskProgressed` 26, `TaskCompleted` 6, and `Moved` 46, `TaskProgressed` 22,
`TaskCompleted` 10; meetings opening with an impostor in a vent 29/145 = 0.200,
66/124 = 0.532 and 66/117 = 0.564 (0.47-0.65).

**One reply.** Opener rebuttals answering the charged tick with an alibi,
whereabouts or sighting: n/a, 19/19 (82 not evaluable) and **17/18 = 0.944
(0.74-0.99)**, 69 not evaluable; rebuttals that only redirect: n/a, 17/121 and
27/117 = 0.231 (0.16-0.31). By 1.9's rule (half or more answer; redirect-only
below half) the reading is **effective**, resting on the 18 evaluable of 87
opener rebuttals. Reported: an accused opener answered in 0/125, 101/112 and
87/105 = 0.829; rebuttals carrying an alibi 104/121 and 89/117, a whereabouts
claim 104/121 and 89/117, a sighting 91/121 and 79/117; rebuttals accusing a
player who already spoke 121/121 and 116/116; beneficiaries in round 2: the
opener answering an impostor 59, the opener answering a crewmate 28, another
impostor answering a crewmate 28, another crewmate answering an impostor 1,
another crewmate answering a crewmate 1 (round 1: 71, 30, 17, 3). Ballots
citing a rebuttal stay **not carried**.

**Body handle.** Conf. cell only; 135/135, 0/118 and 0/114. As built.

**Kill row.** Conf. cell 0/23. Presence: **present**, 23 own-kill rows served
(round 1: 4). Reported, with no effect reading at this size: the holder cited
its own-kill row in 21 of 23; honesty cell 5, 23 kill holders and 21/23 = 0.913
(0.73-0.98) citing the kill (s9: 4 holders, 3 of 4; round 1: 4 holders, 3 of 4).

**Impostor ballot.** Conf. cells 0. Impostor EJECTs whose only citation is a
neutral row (honesty cell 3): 1/46, 0/107 and **0/111 = 0.000 (0.00-0.03)**.
By 1.9's rule (0.10 or below), **the wording holds**. Reported: impostor EJECT
share 46/210, 107/203 and 111/200 = 0.555 (0.49-0.62); EJECTs labelled
supported 44/46, 107/107 and 111/111; authored teammate targets 1/210, 16/203
and 16/200 (each coerced to a skip, recorded 0); ejections whose floor only
impostor ballots met 0/90, 0/54 and 0/66. SKIPs labelled `none_held` stay
**not carried**.

**Self-report off.** Conf. cell 0/117. As built.

### 6.3 The kill cooldown cell

Kill cooldowns that differ from the recorded value
(`kill_cooldowns_differing_from_recorded`): s9 0/275 against the map's 4
(round start 100, after a kill 175, no regroup write), round 1 0/487 against 4
(100, 227, 160), and **round 2 0/447 against 6, with a count at each of the
three writers: round start 100, after a kill 195, at a regroup 152**. Conf. 0
as built; no writer is empty. The grace-window cell, read at the recorded 6,
counted 0 kills at T+1 to T+6 after any of the round's regroups (6.2).

### 6.4 The envelope, and the step the round-3 rule names (non-gating)

| cell | s9 at baseline 9 | round 1 | round 2 | envelope |
|---|---|---|---|---|
| impostor win share | 11/50 = 0.22 (0.13-0.35) | 34/50 = 0.68 (0.54-0.79), flagged above 0.60 | **24/50 = 0.48 (0.35-0.61)** | inside 0.20-0.60, not flagged |
| innocent ejections | 9 of 90 | 15 of 54 | 22 of 66 | reported |
| reporters ejected per report meeting | 7/135 = 0.052 | 11/118 = 0.093 (0.05-0.16) | **17/114 = 0.149 (0.10-0.23)** | **flagged above 0.104** |
| role-correct ejections | 81/90 | 39/54 | 44/66 | reported (6.5) |
| meetings with vent proof | 70/145 = 0.483 | 26/124 = 0.210 (0.15-0.29) | 24/117 = 0.205 (0.14-0.29) | reported |
| scorecard rows 1-9 | as published | round 1's audit 6.1 | 6.1 | reported |

**The round-3 rule** (1.10) reads the point share of impostor wins, 24/50 =
0.48: it is neither above 0.60 nor below 0.20, so neither cooldown branch
fires. Its third branch names the era-keyed promotion only with no envelope
flag and every Conf. cell at 0. Every Conf. cell reads 0, but the envelope
flags reporter ejections (17/114 = 0.149, above 0.104), so **the rule names no
step**. The readings command's last line reads `round-3 rule: names no step`.
The rule and the envelope gate nothing; what comes next is the owner's.

### 6.5 Role-correct ejection, the balance row and the win split, gating nothing

Role-correct ejections 81/90 = 0.900, 39/54 = 0.722 and 44/66 = 0.667
(0.55-0.77). Kills (the denominator of `kills_seen_by_crew`): 175, 227 and
195. Impostors able to kill when a meeting opened
(`impostor_cooldown_zero_at_open`): 63/210 = 0.300, 84/203 = 0.414 and 54/200 =
0.270 (0.21-0.34). The win split: 39 crew and 11 impostor wins at baseline 9;
16 crew and 34 impostor in round 1; 26 crew and 24 impostor in round 2. All are
reported beside the readings and gate nothing; a wrong ejection on believable
data is the game working (scorecard row 8).

## 7. The decision menu

The audit gives no verdict.

- **The step the round-3 rule names: none.** The win share sits inside the
  envelope, so the rule names no cooldown round; the reporter-ejection flag
  keeps its promotion branch from naming the promotion (6.4). The next card,
  if any, is the owner's to name.
- **`vent_exit_policy = look_and_wait`**, round 1's options for it alone:
  Conf. 0; **effective** again (8/72). The owner chooses **adopt** through the
  era-keyed promotion (the path compatible with the ML hold), **iterate** under
  a new value, **escalate** to hidden travel, or **fall back** to the status
  quo.
- **The seven adopted arms**: Conf. cells only, and every one reads 0
  (6.2): `vent_witness_rule = physical`, `vent_entry_policy = own_fresh_kill`,
  `meeting_reset = hub_with_grace`, `bounded_rebuttal_version = 1`,
  `report_body_handle_version = 1`, `ballot_kill_row_version = 1` and
  `impostor_ballot_version = 1`.
- **`kill_cooldown_ticks = 6`**, the round's one dial: its Conf. cell reads 0
  at all three writers (6.3). The rule names no step for it.

The promoting card's follow-up this round would add to memo 1's adoption list
(a public-results label for the kill cooldown) is listed only when the step is
the promotion, so it is not listed here.

## 8. Limitations

- Hosted generation is not byte-reproducible, so a seed is re-recorded only by
  the failed-seed rule, never to change its bytes. Rounds 1 and 2 differ in one
  key, but each is one hosted recording of 50 games: the win shares' intervals
  (0.54-0.79 and 0.35-0.61) overlap, and the difference between the rounds is
  the dial's only within that noise.
- The arms land together; only the Conf. cells and the lab rows attribute a
  mechanism, and fake and lab rows establish mechanics, not reasoning quality.
- 50 games: the kill row served 23 rows, and the one-reply reading rests on 18
  evaluable opener rebuttals of 87.
- Four pre-registered cells are not carried by any named source (false resume
  perceptions, the regroup notice, ballots citing a rebuttal, `none_held`
  SKIPs).
- The tally counts `llm_calls` rows only, as for s9 and round 1: the husks'
  `failed_call` tokens (13,511 input, 1,919 output) and the calls of seed 45's
  discarded first attempt are outside it. Recording wall and the husks' spend
  come from the recorder's logs and the husk files, kept outside the
  repository; every other count reproduces from the committed bytes with the
  commands above.

## 9. The promotion (2026-10-02)

Card: [`tasks/work/promote-round-2.md`](../tasks/work/promote-round-2.md). A dated
addendum: sections 1 to 8 above are unchanged, byte for byte, from `d41c9006`,
the merge of PR #494 that committed them.

### 9.1 The ruling

The owner ruled on 2026-10-02, verbatim: "1. Merge 2. Promote and run the
diagnostics." The merge is `d41c9006`. This section records the promotion; the
diagnostics are separate, read-only work and gate nothing here.

### 9.2 The rule's reading, and the flag the promoted set carries

The round-3 rule (1.10) named no step. Every Conf. cell read 0 and the impostor
win share, 24/50 = 0.48, sat inside the envelope, but reporters ejected per
report meeting read 17/114 = 0.149 (0.10-0.23), flagged above the pre-registered
0.104, so the rule's promotion branch did not fire (6.4, 7). The owner's ruling
promotes regardless. The flag is a stated limitation of the promoted set; no
reading is re-run or re-worded.

### 9.3 The bytes, file by file

Round 2's 50 replays, `MANIFEST.md`, `roster.json` and report gz moved from
`replays/candidates/stage-b-r2/9p2i/` to `replays/samples/9p2i/`, and the round's
`experiment-config.json` moved beside them, as the era's declared config. Each
file's sha256 at the promoting head equals the candidate file's at `d41c9006`
(`shasum -a 256` over both, compared name by name: 54 files, 0 differing):

| file in `replays/samples/9p2i/` | at `d41c9006` | sha256 |
|---|---|---|
| `MANIFEST.md` | `replays/candidates/stage-b-r2/9p2i/MANIFEST.md` | `78941baa36a6ac33e166e2cae979f1ff424c84dce6956e9e3bab11e0c510758d` |
| `roster.json` | `replays/candidates/stage-b-r2/9p2i/roster.json` | `01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340` |
| `tournament-eval-report.json.gz` | `replays/candidates/stage-b-r2/9p2i/tournament-eval-report.json.gz` | `ce05afee46e85019e5ec98ccfd223705c11654152b711fab55515e0502fafd8c` |
| `replay-seed-0.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-0.jsonl` | `155126d2c1a8c8dfc0876f0347ed399570cc0d29c611e068c12be2720217bc62` |
| `replay-seed-1.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-1.jsonl` | `266fbac33f1971674e108ba8c4da3b8621edc8ead9d971eabc72fe633f494d3a` |
| `replay-seed-2.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-2.jsonl` | `d08bb5da0fc947ea96ea3d1e45aa5b046b0eda0ee2920cb0cfe27b747b64b22b` |
| `replay-seed-3.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-3.jsonl` | `cb6107b392b1ac6d5ad0e7ab6833e165a83e867dee6859eefd281145d79192f1` |
| `replay-seed-4.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-4.jsonl` | `562ca5846f8a29b2444b2c810b42300580f745823c6ab8646f84086be1fcf336` |
| `replay-seed-5.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-5.jsonl` | `01ef9eb75d30f331621fb892d2ccea3ef52b05343873cf3062907a7ff671655b` |
| `replay-seed-6.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-6.jsonl` | `254aa95e2dd6f7698515307d4090454a8e020faadbe8c92758c544c2f9d56de3` |
| `replay-seed-7.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-7.jsonl` | `08b911e579d7539c19850efcb34f075aa8d541f5215f73c9563165855101b01d` |
| `replay-seed-8.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-8.jsonl` | `0a8e56248b053ce44de880ae19111f965054228b18e1764b0e25212198b91e5c` |
| `replay-seed-9.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-9.jsonl` | `f0fdb66ed38945e23e2fe8bd03026e05cf1cf8993117816790ec059c1a2a39a0` |
| `replay-seed-10.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-10.jsonl` | `48cb758e4516ff90754ab4d4699a98e347e234e10f0c1352f1c8e3b79079a64e` |
| `replay-seed-11.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-11.jsonl` | `63792832f75fd2e5ed9beb8839b8c9d9350394ab0c2f11fc8fb82ead2e452657` |
| `replay-seed-12.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-12.jsonl` | `4dc586360f54f8c445de35ede4b4dba076906793621f4e2825a45a9a87f805da` |
| `replay-seed-13.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-13.jsonl` | `1063f3fa59473e3ea55cfb7fca7ac0fd4a0f4ae4af2c9e4268c030960bcae498` |
| `replay-seed-14.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-14.jsonl` | `0b02948a4e25de188a39872567ffa13580f68a6f60dde070c81c0e90f29b4392` |
| `replay-seed-15.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-15.jsonl` | `4374910278c49ea406326164ef0e3028d5c64b0b9712ebf77e72a41c1dd65a01` |
| `replay-seed-16.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-16.jsonl` | `a0c0151ebd58ab2016d82b7abee4fb6b387b40d8239d4831e5d2270e47eb6411` |
| `replay-seed-17.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-17.jsonl` | `239c6821fcdba105e59db0a7d28f2540a92d6dc56e1dd145be2fe14358bfce14` |
| `replay-seed-18.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-18.jsonl` | `b6de226b5dcf3a7b87c7a28041f9909100bc1e8cb61c78159e5e1b64d53aa5c6` |
| `replay-seed-19.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-19.jsonl` | `3c2f045f761eeb5bb5d02c8bfeeae9559cd7999b75937f25572e772949b31e64` |
| `replay-seed-20.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-20.jsonl` | `9eb758b49def9cbff03177242687d9154451a08fe9ae7edd4225b4d5144ec025` |
| `replay-seed-21.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-21.jsonl` | `73396964aee3adaef25dd0aa5b2660aa3a222fdf9d1354058bd04828a8c2beca` |
| `replay-seed-22.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-22.jsonl` | `1f6f7d96fa7ff933965611c43ba7036ab5414849f8b83ab7461a53456ef3108f` |
| `replay-seed-23.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-23.jsonl` | `d298f23ac0ff061ea77bbc44ac6828420a2c33dc156fc11ea56fab3be33b6c50` |
| `replay-seed-24.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-24.jsonl` | `bd7006e7098b61fca0d41f98ad3334d33b2c21337cd16026821736b6e1d1f771` |
| `replay-seed-25.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-25.jsonl` | `6a82683c71e77a8d6dfe7e344168fea18358752071defd5647fc12661c43c6a8` |
| `replay-seed-26.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-26.jsonl` | `442b6db851e87079ae1bdccfc68ebc9a52b6dfbefadcb58dd4d4e76dcf1c2a2a` |
| `replay-seed-27.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-27.jsonl` | `a6e0ca34c12a9091dca11795ee02c27b403af8effec547238cfba25b240b4aa1` |
| `replay-seed-28.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-28.jsonl` | `24523d6e57ff2c020a02f68de04a64b8d5f2b22ffe98248ad5b54d73c9b509a3` |
| `replay-seed-29.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-29.jsonl` | `6606b40aec5f10a6d47971d9d4ef642087e83bca6ba00df48a19728ddb3cbb28` |
| `replay-seed-30.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-30.jsonl` | `8c18a6dc325953ad0b92e2c842fd20bddf7e85350ece9b66a06c130643cd0f94` |
| `replay-seed-31.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-31.jsonl` | `e62391a8d9fd74b519c1aeca780cb7cbcd3ede22a18d563d1d0dc6950c37ec87` |
| `replay-seed-32.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-32.jsonl` | `d71297584feb57b328712982ec4dce8074bb4311e21bb49a65bcad13006000cb` |
| `replay-seed-33.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-33.jsonl` | `4063270a26974de1a0134a6ebd38491b8fceb3b0b6f40b19204da700dcce5f42` |
| `replay-seed-34.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-34.jsonl` | `1a130de676363be202ed2693b7899b20daab368ec46940f860ca9cb487dd020e` |
| `replay-seed-35.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-35.jsonl` | `6ee9459a4da0f0702082e2a66fcfdcf9c85e5f6635957858531497775696b009` |
| `replay-seed-36.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-36.jsonl` | `39123907fe06a01b97f6d1b4a82c29fd03df1113e9a47817f987f22b8e0b048f` |
| `replay-seed-37.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-37.jsonl` | `cf23571d8904a90e6cd1e24f199bf974e3c72cee313754b5d03064bd781fbe21` |
| `replay-seed-38.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-38.jsonl` | `ec88a94b38549d2856b32fd22c9222145c221128f31ffe76b2ffda61046ac54c` |
| `replay-seed-39.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-39.jsonl` | `7f3a88e6fa136ce0f3d365be15c1cfef989a542fbc48ee2bfc4251bfc959440b` |
| `replay-seed-40.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-40.jsonl` | `1530708b78f56d3af1599faf13307d727062423ecb3581e8fe7baee956bda983` |
| `replay-seed-41.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-41.jsonl` | `1b30086fe06f1798f3e8002d15ab88fa9fd4a012154a897779aff077be9633ad` |
| `replay-seed-42.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-42.jsonl` | `60d23f9f7c77158efe691fab69703fce714440d0a08ae1d8273a79b49393508a` |
| `replay-seed-43.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-43.jsonl` | `5c48bda2e0707cfc3430f5c678a154bdef812705940740b3f60a39a79122a983` |
| `replay-seed-44.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-44.jsonl` | `4cd837f4a10045ea46518a60a451bd9b3887e5527bb83583f0af33c27249519d` |
| `replay-seed-45.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-45.jsonl` | `19a01db30cf49770bf56855b233df57ad4112580b440cdf09e73c33cfc2110a4` |
| `replay-seed-46.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-46.jsonl` | `5dbdd08e9ab41267ccedc42632f15c2a41b4670932064330b751d8510ed25af5` |
| `replay-seed-47.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-47.jsonl` | `eaa1dcee4750a72dd20375aea4b918383eeebb04be0c5029fcde28d2e92b0fc8` |
| `replay-seed-48.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-48.jsonl` | `81fe976f0d33862c4a18cb2ee17a2f82d7759a09e3cd8dbf3ed1cd50e9ecc6d1` |
| `replay-seed-49.jsonl` | `replays/candidates/stage-b-r2/9p2i/replay-seed-49.jsonl` | `e121c74f6d0ad752c4b34e47b5759d188d0297589d2cc28bcf95a45604d5bb42` |
| `experiment-config.json` | `replays/candidates/stage-b-r2/experiment-config.json` | `0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b` |

The set's baseline-9 bytes, and its `results-rubric-score.json`, left
`replays/samples/9p2i/` in the same change; they remain at `d41c9006`.

### 9.4 The era, and what did not move

`eval/eras.py` names two eras. **baseline-9** owns `replays/samples/4p1i`,
`replays/ml_corpus/9p2i` and `replays/ml_corpus/4p1i`: the process re-record
([`audit-2026-09-22-process-rerecord.md`](audit-2026-09-22-process-rerecord.md)),
recorded 2026-09-22 with every experimental switch off. **stage-b-r2** owns
`replays/samples/9p2i`: this record, recorded 2026-10-01 under the declared
config `replays/samples/9p2i/experiment-config.json` (sha256
`0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b`, 1.4). The
substrate ladder tip stays at baseline 9: no substrate lever moved, and baseline
10 stays reserved for the full re-record that re-freezes the corpus. No
instrument pools across the two eras. The corpus and every ML artifact keep
their bytes and keys.

### 9.5 The win split

| set | baseline-9 impostor rate | promoted impostor rate |
|---|---|---|
| `samples/9p2i` | 22% (11/50) | **48% (24/50)** |

Read from the set's `MANIFEST.md` `winner` column, at `d41c9006` and at the
promoting head. Win split is not a gate and is published only because the
front door quotes it.

### 9.6 The cells the front door quotes, for the promoted set

Read off the promoted set's eval report, its `deduction.ejectee_proof_cross_tab`
block: 66 ejections, 44 of an impostor and 22 of an innocent. The before column
is the baseline-9 record's own `samples/9p2i` rows
([its §6.2](audit-2026-09-22-process-rerecord.md)). Intervals are Wilson 95%.

#### Published cell 1 — non-direct conviction accuracy

| set | before | after |
|---|---|---|
| `samples/9p2i` | 11/20 = 0.5500 | **20/42 = 0.4762** [0.3336, 0.6228] |

The direct-proof cell for `samples/9p2i` stays perfect: **24/24 = 1.0000**
[0.8620, 1.0], against 70/70 = 1.0000 at baseline 9.

#### Published cell 2 — innocent ejections

| set | before | after |
|---|---|---|
| `samples/9p2i` | 9 | **22** |

Every innocent ejection sits in the non-direct cell: the proof-present cell is
innocent-free, 0 of 24, and 42 − 20 = 22.

### 9.7 The before columns, and the column that no longer reproduces

The process scorecard's before column for `samples/9p2i` is that set's entry of
`docs/process-scorecard.json` at `d41c9006`, carried verbatim in
`docs/process-scorecard-before.json` and pinned by its sha256 in
`eval/process_scorecard.py`; the front door's before cells read the baseline-9
record's rows above. This round's "s9 at baseline 9" column (1.9) reproduces at
`d41c9006`, where those bytes are `replays/samples/9p2i`, and not after the
promotion, whose tree no longer holds them.

### 9.8 Pins re-derived over the baseline-9 era's three sets

`scripts/counterfactual_phase21.py` reads the baseline-9 era's sets only and
refuses `samples/9p2i` by name, so its corroboration pins are re-derived by its
own walk over the three sets; this section is their committed source:

| cell | four baseline-9 sets | three baseline-9 sets |
|---|---|---|
| accused without a first-hand source | 529 / 1,516 | **422 / 1,192** |
| ejected without a first-hand source | 16 / 409 | **12 / 321** |
| ejected on an answering turn | 36 / 411 | **29 / 321** |
| ejected with a walkable pair | 69 / 411 | **56 / 321** |

Its innocent-ejection pins are the baseline-9 record's three per-set cells (32,
0, 1).

### 9.9 The candidate-round rule, and where it departs from the memo

A round whose bytes become a committed set is deleted in the promoting change,
and its record cites the commit that held it: round 2's directory is deleted
here, its bytes held at `d41c9006`. Any other round stays until a later card
names its retirement. Round 1 (`replays/candidates/stage-b-r1/`) stays as the
comparison record that this audit and round 1's both read as a column. This
departs from the decision memo's proposal
([`tasks/decision-2026-09-24-stage-b-wave.md`](../tasks/decision-2026-09-24-stage-b-wave.md)
section 1, item 7) that the card landing round r+1 deletes round r.

### 9.10 What the promoted set does not ship

The gameplay-facts extractor reads only recordings made without experiment
settings, so the set ships no `results-rubric-score.json`, and the 15.2 parity
pin is history until a card widens the extractor. The three curated cases on the
public results page were written against the baseline-9 bytes and are withheld
by their source check; the tour card re-curates them.
