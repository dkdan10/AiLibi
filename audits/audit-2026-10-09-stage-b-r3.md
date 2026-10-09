# Stage-B candidate round 3 — the route lines on the shown set's rules, its record and its assessment (2026-10-09)

Card: [`tasks/work/stage-b-record-r3.md`](../tasks/work/stage-b-record-r3.md).
Frozen head: `main` at `e4fc6cbf`, after the route-lines field (PR #501), the
census's held-data cells (PR #502), the crew idle-policy lab (PR #500) and the
game-shape profile (PR #504) merged, their cards were flipped, and the decision
memo recorded the owner's rulings of 2026-10-09 and the card its dated
amendment. Branch `work/stage-b-record-r3`, one pull request into `main`.

This record makes one 50-seed candidate round: seeds 0-49 of the 9-player
sample roster (9 players, 2 impostors, 2 tasks per crewmate), recorded once on
featherless `Qwen/Qwen3.6-27B` with the prompt set `qwen3_6_27b`, the bare
substrate slate and one declared experiment config, into
`replays/candidates/stage-b-r3/9p2i/`. The config is round 2's, the shown
set's rules, with one more field: `route_lines_version = 1`, which gives each
voter a plain line about the places stated at the table, the same for every
role, listing only the changes of room the station's doors allow within the
ticks between or that the public regroup falls between. It reads the round
against questions fixed before the first seed, in three columns that are never
pooled: round 1, round 2 (the shown set, `replays/samples/9p2i`) and round 3.
Round 1 and the shown set stay byte for byte; nothing publishes; the ladder
tip stands at baseline 9; the round adopts nothing.

Role-correct ejection and the win split are reported beside the readings and
gate nothing (ruling D1 of
[the direction of 2026-09-19](../tasks/direction-2026-09-19-process-over-outcome.md)
section 12). The re-keyed reporter flag gates nothing, and the step rule never
reads it.

## 1. Pre-registration

This section is committed before the first seed, in the `coordination:` commit
the card calls P, and it is never rewritten. An amendment lands as a dated
addendum in a later section and is confirmed again; the recording checkout is
then detached at the commit holding the confirmed text. The recording checkout
is detached at P itself, so every MANIFEST row of the round stamps P's short
sha and `git merge-base --is-ancestor P <that sha>` exits 0. The owner
confirmed the five points the card reserves for them on 2026-10-09, before P
(decision memo 8.7); section 2, the dated addendum the card calls Q, quotes
that confirmation against each point, and the owner's delegation of the step
after the round (memo 8.8). No provider is called before Q is pushed.

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

On **2026-10-02**, round 2's promotion (round 2's audit 9.1):

> 1. Merge 2. Promote and run the diagnostics.

On **2026-10-06**, on the baselines memo (memo 8.1, verbatim):

> 1. Rekey
> 2. What is your recommendation? I slightly lean to spend with narrow field, but would go with your recommendation
> 3. Rebase the rubric. Maybe spend time thinking if it needs to be completely redone with the context from this conversation.
> 4. README should be current and can be a focus in the last steps, once the project is stable.
> 5. Sounds good
> 6. Sounds good
> 7. Sounds good
> 8. Merge when ready

The memo's reading of ruling 2, which follows it there (the orchestrator's
words, not the owner's):

> Ruling 2 asks for the orchestrator's recommendation and defers to it. The recommendation is the narrow field the
> owner leaned to (memo D2 option (a)), so round 3 is authorized on it under that delegation, on the conditions of 8.2
> item 2.

On **2026-10-06**, on the rubric design memo (memo 8.6): "Profile as
recommended, decisive, and ship the shelf". The round reads none of the
profile; it landed before `F` because it writes code this card's freeze and
nothing-moves diff cover.

On **2026-10-09**, twice (memo 8.7 and 8.8). The process amendments and the
round-3 confirmation: "Apply all five redundancy removals and confirm the five
points as proposed". The step after the round: "I will let this session, as
the orchestrator, decide about promoting round 3. Keep what I want for the
project in mind. I lean towards wanting to promote round 3, but if there is an
issue you find with recording, or think it is really a step down in terms of
gameplay, you can make the decision to keep round 2." Section 2 quotes both
sections of the memo whole, point by point.

The live-call authorization for this round is ruling 2 of 2026-10-06, as memo
8.1 and 8.2 item 2 apply it, under the standing ceilings (1.5), on the
conditions of 8.2 item 2 and with the owner's confirmation of 2026-10-09.

### 1.2 The orchestrator's readings of 2026-10-06 (memo 8.2), verbatim

> These are the orchestrator's application, not the owner's words. They bind the cards of round 3.
>
> 1. **The reporter line is re-keyed** (ruling 1; memo D1 option (b)). From the next pre-registration on, the
>    envelope's reporter line reads reporter seats ejected without vent proof against other crewmate seats ejected
>    without vent proof. The census already publishes both per era: on the shown set, 17 of 93 against 5 of 291
>    (`docs/gameplay-census.md:162`, `:165`; `uv run python scripts/publish_gameplay_census.py --check` recomputes
>    them from the recordings). It is a flag the round-3 step rule does not read. While R6 holds every reporter is a
>    crewmate (meetings opened by an impostor: 0 of 117 by construction, `docs/gameplay-census.md:255`), so any
>    reporter line reads role, and a role-reading flag that a step rule branches on is a gate on that step. Its bar
>    is proposed with alternatives by `stage-b-record-r3` and stated by the owner before the first seed. Round 2's
>    reading under the 0.104 line (twice baseline 9's 7 of 135, section 4's envelope row at `:1193`) stands as
>    recorded, and no earlier verdict is re-read. The direction addendum of 2026-10-06 states the rule in general.
> 2. **Round 3 is a spend on the narrow role-blind route field** (ruling 2; memo D2 option (a); the route-check
>    card's branch 3, `tasks/work/route-check-replay.md:1461-1469`).
>    - The field. A new `RecordedExperimentConfig` field: versioned, default off and omitted from the payload at its
>      default, set only from the declared config file, with its own stamp in the replay and readers that thread it
>      or refuse it. Prompt-only, it serves a composite stamp through the spine registry and guarded template blocks,
>      as the ballot arms do: no prompt registry bump, no `AILIBI_*` lever, no environment switch.
>    - What it renders. At most one line per living candidate, the same for every role, holding only two readings:
>      pairs of places stated at the table that the map links within the elapsed ticks, over several hops; and moves
>      that cross the public regroup, which walking cannot decide. A change of room that is neither is left out, never
>      rendered as an impossible move, and a candidate with neither has no line. It never asserts presence or honesty
>      and never points at anyone. The meeting layer labels and never rewrites, and nothing pushes an agent toward the
>      correct answer (direction section 7).
>    - Why this check. On round 2 the route-check replay found 40 misjudged cases (a charge against a pair of places
>      the map or the public regroup reconciles, ending in an ejection), 7 of them at kill-witness meetings. The
>      existing walkable-pair clause reaches 15 of the 40. The recorded `evidence_reasoning_version = 2` reaches 16,
>      and at the recorded ballot budget it never shows a regroup-crossing row. The reference check (c), several hops
>      over the whole map plus alibi stays plus a named regroup crossing, reaches 29 of 40 and 7 of 7: every
>      misjudged innocent ejection (21 of 21) and every ejected witness (5 of 5). Its 11 unreached cases are impostor
>      ejections, 9 resting on a vent sighting. Source: `experiments/lab/results-route-check-replay.json`, column
>      `r2`, `rule_inputs`; `uv run python -m experiments.lab.route_check_replay --check` reproduces it (exit 0 at
>      `76270d6c`, 46 s). Reaching is showing a line, not changing a vote, and no model was run.
>    - The round. Seeds 0-49 of the 9p2i roster into its own candidate directory under `replays/candidates/`. The same
>      eight rules (the seven adopted arms and `vent_exit_policy = look_and_wait`) plus `kill_cooldown_ticks = 6`, so
>      the route field is the round's one dial. `evidence_reasoning_version = 2` is not used, and R6 stays off.
>    - The ceilings. The standing ones: 2,800 calls, 17,500,000 input and 750,000 output tokens (section 4,
>      `:1109-1115`); a 12 h recording wall summed over sittings, each inside an 18 h window (the owner's amendment of
>      2026-09-28, "Raise the wall to 12h in an 18h window and resume. Make sure it allows for a pause."; audit 1.1 and
>      1.6); $0.00 marginal; each with its stop at 90 percent. The stop rules, the stall rule and the freeze of section
>      4 (`:1124-1156`) and of the round-2 record (audit 1.7) apply unchanged. Round 2's spend is the planning figure
>      (1,588 calls, 9,726,227 input, 441,092 output, 3.59 h, $0; audit 5.2), re-measured at the probe.
>    - The conditions, in order. The field card merges. Its planted cases, the fake and scripted rehearsals and the
>      lab rows pass on the declared config before any live seed. The pre-registration lands as its own commit. The
>      owner confirms the pre-registration and the ceilings in their own words. Only then does the first seed run.
>    - The pre-registration names, after the diagnosis (`tasks/diagnosis-2026-10-02/README.md:649-653`) and memo D2:
>      the route-check process count; the kill-witness outcome row; the per-seat ejection table; the impostor win
>      share against 0.20-0.60, watching the 0.20 floor because saved witnesses help the crew; the re-keyed reporter
>      flag; and the first goal's missing held-data cells (memo Part 3.4 items 1 to 3) once a census card carries
>      them. Its step rule, if it has one, names no role-reading flag among its conditions.
>    - Publication. Nothing ships. A candidate round's bytes reach the demo only through a later promotion, and that
>      is the owner's decision.
> 3. **The carrier for the cells round 2 left uncarried** (memo D3; not ruled on 2026-10-06, so this is the
>    orchestrator's reading). False resume perceptions are carried by mechanism and golden, not by a measured count:
>    the shared helper `compose_resume_events` (`orchestrator/replay.py:1427`) with its planted tests, and the
>    golden's byte-equal re-render of all 1,502 recorded round-2 prompts (audit 5.1). Ballots citing a rebuttal read
>    the turn citation as the cell, with the counter slot beside it (57 of 691 and 175 of 691 on the shown set,
>    `docs/gameplay-census.md:299-300`). The regroup notice and the holds-nothing label are census cells from this
>    head on (`:221`, `:331`). Round 2's "not carried" lines stay as recorded (audit 8). The round-3
>    pre-registration names this carrier as a point the owner confirms.
> 4. **ML** (memo D10). The hold of 2026-09-24 (ruling 12) stands.
>    - The free idle-policy lab runs: `crew_idle_policy` set to `hub_wait`, `patrol` and `accompany`, crossed with the
>      adopted rules plus cooldown 6 on development seeds, with the fake provider, $0 and no training (diagnosis card
>      6, `tasks/diagnosis-2026-10-02/README.md:674-684`). Its whereabouts-coverage cell is computed from engine
>      positions the same way for every role, and it is defined before the run.
>    - The role-blind re-pricing of `correct_reports` and `patrol_coverage` is written into `training/README.md`
>      section 7 (`:312-364`) and the comment at `training/rewards.py:301-306`, as a comment-only edit of the class
>      `d1ea113a` merged. Any reopening re-prices the two terms role-blind, under a new `FITNESS_OBJECTIVE_ID`, before
>      any search. No reward value, weight, signature, fit or artifact moves.
>    - The conviction GO (`training/artifacts/conviction/verdict.json:10`, `"fitness_term": "ships"`) folds into that
>      note: a reopening's re-priced objective overrides it, dated and written as an override, never by editing the
>      artifact.
>    - The seed-0 reward pin (`tests/training/test_rewards.py:518`, the byte-identical seed-zero test) stays until a
>      reopening.
>    - The corpus FROZEN line and the ML artifacts do not move; `scripts/verify_ml_evidence.py` runs offline, never
>      with `--complete`.
> 5. **The rubric, the README and the front door** (rulings 3 and 4; memo D6 to D8).
>    - The rubric is held for a design pass, and no card of round 3 carries it. `rubric-extractor-era` (ready,
>      `tasks/work/rubric-extractor-era.md:3`), which keeps the scorer unchanged, is not dispatched as contracted. The
>      owner chose to rebase the rubric (memo D6 option (b): a new rubric version before anything ships for the shown
>      era, the scalar railroad floor replaced by the ballots' grounding labels with its quantifier stated, a task win
>      after an ejection no longer scored 0.0, the role reads demoted) and asked whether it should be redone from the
>      start; the design pass answers that first. D7, whether a wrong-but-believable ejection is ever featured, rides
>      with it. The rubric cards come from that pass.
>    - The README and the front door (memo D8, with its dashboard and viewer halves) are deferred to the last steps,
>      once the project is stable. Until then the README stays current: `scripts/check_doc_facts.py` keeps every
>      figure it checks true, and a card that makes a README sentence false fixes it in the same pull request.

**What stays as memo 8.3 to 8.5 hold it.** ML is held (8.3); the champion-flip
comparator stays at 11 of 50; R6 (impostors never report a body) is kept
through round 3, so every reporter is a crewmate and the reporter cells keep
their meaning across the round. Memo D14's retirements of the era-locked
instruments, pins and fixtures were not ruled (8.5), so nothing is retired on
the strength of this record and `replays/candidates/stage-b-r1/` stays as the
round-1 comparison column. The round declares the balance pair as round 2 did,
and the ladder tip stays at baseline 9 (`eval/eras.py`).

### 1.3 The declared config

One line plus a newline, 342 bytes: round 2's 316-byte declared file
(`replays/samples/9p2i/experiment-config.json`, sha256
`0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b`) with
`, "route_lines_version": 1` inserted before the closing brace. The field
merged under the name the card wrote (`route_lines_version`,
`orchestrator/experiment_config.py`), so the bytes are the card's.

```
{"format_version": 1, "meeting_reset": "hub_with_grace", "vent_exit_policy": "look_and_wait", "vent_entry_policy": "own_fresh_kill", "vent_witness_rule": "physical", "bounded_rebuttal_version": 1, "report_body_handle_version": 1, "ballot_kill_row_version": 1, "impostor_ballot_version": 1, "kill_cooldown_ticks": 6, "route_lines_version": 1}
```

`shasum -a 256` on those bytes prints

```
a788b9eba5e8f2f5d29033fece2d0dc0dbac7d3528ea93c7c7a93327dbc6d57d
```

which equals the card's figure. At `F` the bytes, read by
`scripts/_declared_experiment.py`'s loader, validate as a
`RecordedExperimentConfig` whose fields off their default are exactly ten:
round 2's nine (`meeting_reset`, `vent_exit_policy`,
`bounded_rebuttal_version`, `vent_witness_rule`, `vent_entry_policy`,
`report_body_handle_version`, `ballot_kill_row_version`,
`impostor_ballot_version`, `kill_cooldown_ticks`) and `route_lines_version`,
declared last. `FIELD_LAYER` assigns the route field `meeting`,
`OMITTED_AT_DEFAULT` holds it, and `engine_arguments` returns round 2's
keywords unchanged: `{'redistribution_policy': 'lowest_id',
'vent_witness_rule': 'physical', 'kill_cooldown_ticks': 6}`.
`prompt_versions_for_set("qwen3_6_27b", experiment_config=...)` serves four
stamps: `accusation_round.qwen3_6_27b.v6`, `crewmate_report.qwen3_6_27b.v6`,
`impostor_report.qwen3_6_27b.v6` and
`vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1+vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1+vote_ballot.qwen3_6_27b.v8.route_lines_v1`.
No prompt registry moves: the header marker stays `vote_ballot.qwen3_6_27b.v8`.
`self_report` is False, `evidence_reasoning_version` and
`contextual_self_report_version` are None, and the substrate slate is bare
(`--expect-levers ""`).

The file is not committed at P: a round directory without its set directory
fails the candidate test. The delivery commit adds it at
`replays/candidates/stage-b-r3/experiment-config.json`, and its sha256 must
equal the line above. Until then each checkout that reads it holds an
untracked copy whose `shasum -a 256` is checked against that line before the
dry run and every gate; a mismatch stops the card. No pytest and no
`check.sh` run beside an untracked copy.

### 1.4 The frozen head and the three checkouts

`F` is `e4fc6cbf` (`e4fc6cbff94a154d7eddffebefec3b741c92721b`). It holds
`route-lines-field` (the field, its stamp and readers, its planted cases and
rehearsals, the route-lines instrument and an `r3` column in both route
instruments), `census-held-data-cells` (the held-data cells and the route
field's conformance cells under the keys the table names),
`crew-idle-policy-lab` (its lab arms, capture and `training/` text) and
`rubric-v2-profile` (the game-shape profile), each merged with its card
flipped, then the memo's sections 8.7 and 8.8 and the card's dated amendment naming the
merged census table `holds_nothing_skips_by_source`. P is the commit that adds
this section; its tree differs from `F`'s only in this audit, its
`audits/README.md` row and the re-derived `audits/` row of
`docs/artifacts.md`, so the code every seed runs is `F`'s.

- **Recording**: a fresh worktree detached at P, outside the repository's
  working tree, with `uv sync --frozen` and no `.env`, which runs only the
  recorder. No pytest, no `check.sh` and no commit run there, so the
  recorder's one `git rev-parse --short HEAD` per run reads P for every leg.
- **Verification**: a worktree at `F`; the pre-spend at `F` ran in this
  branch's worktree while it was still at `F` with a clean status, before P.
- **Delivery**: the `work/stage-b-record-r3` worktree, which receives each
  checkpoint's copy of the recorded bytes and runs every gate in a bare shell.
  Its code is `F`'s: the branch adds only documents, the round's bytes, the
  golden's one pin row and the card's Results.

**The freeze.** From the first seed to the merge nothing merges into
`engine/`, `agents/` (the prompt set included), `meetings/`, `observation/`,
`orchestrator/`, `eval/`, `api/`, `scripts/` or `llm/`, or into
`experiments/lab/route_check_replay.py`, `training/`, `experiments/`,
`audits/tactical-gameplay/` or the other paths the card's nothing-moves diff
covers. If `main` moves there, the record stops and asks; otherwise `main` is
merged in and every gate re-runs.

### 1.5 The ceilings, and the re-projection

The standing ceilings of rounds 1 and 2 (round 2's audit 1.6), unchanged:

| limit | ceiling | hard stop at 90% |
|---|---|---|
| model calls | **2,800** | 2,520 |
| input tokens | **17,500,000** | 15,750,000 |
| output tokens | **750,000** | 675,000 |
| recording wall | **12 h** summed over sittings, each sitting inside an **18 h** elapsed window | **10.8 h** summed (38,880 s) |
| marginal cost | **$0.00** (flat-rate Featherless, already paid) | any `cost_usd` other than 0.0000 |

The cost is marginal against the flat-rate Featherless subscription, whose
standing fee is already paid and is not incurred by this run. Recording wall
is each leg's own "Refresh complete in" figure, summed over sittings; the time
between legs, spent on gates and checkpoints, counts only against the
sitting's 18 h window, which opens with that sitting's first seed.

Round 2 spent, with its two husks, 1,588 calls, 9,726,227 input, 441,092
output and 12,927 s (3.59 h), $0 (its audit 5.2): 56.7%, 55.6%, 58.8% and
29.9% of the four ceilings, so the stops leave 1.59x its calls, 1.62x its
input, 1.53x its output and 3.0x its wall. The tally (1.14) prints
`1502 9187880 418270 0.0` on `replays/samples/9p2i` and
`1556 9344346 433660 0.0` on round 1 at `F`. The planning figure for the route
lines' added input is the field card's projection on round-2 bytes, gating
nothing: 331,015 added input tokens on the ballot calls, 9,518,895 in all
against round 2's recorded 9,187,880
(`experiments/lab/results-route-lines-replay.json`, the r2 column's
`all.tokens`; `uv run python -m experiments.lab.route_lines_replay --check`
reproduces it at `F`). It is a share of recorded prompt characters, not a
tokenizer count, and not a prediction of the model.

**Re-projection**, round 2's rule with its anchor moved from the baseline-9
9p2i bytes, which left the tree, to round 2: after the probe, after the first
checkpoint holding at least 10 seeds and at every batch checkpoint, each count
is (the round's total over its completed seeds / round 2's total over the same
seeds) x round 2's leg total, and the wall is the summed recording wall / the
completed seeds x 50, each compared with its 90% stop. A figure past its stop
at any of them stops the round. `reproject.py` (1.14) computes it and refuses a
completed seed with no round-2 seed beside it. The round-1 ratio is context
only and gates nothing.

### 1.6 The stop rules

Stop and report to the owner, with the partial output and the last checkpoint
pushed, on:

- any `cost_usd` other than 0.0000, or a re-projection past 90% of a ceiling;
- a leg past 1.5x the probe's projected wall, summed recording wall past
  10.8 h, or a sitting past its 18 h window;
- a provider refusal that survives the 8-attempt budget, or a raise from
  `measure_baseline.py --honesty`;
- any conformance miss: a "Conf." cell of 1.8 that does not read as built, the
  cooldown cell and the route cells included. It is a code defect, not a
  result: the fix lands under a new field value (a recorded value's meaning is
  frozen), and the round re-records from seed 0 under a new declared config,
  with a dated addendum and the owner's clearance.

**Stalls and failed seeds.** A stall is 45 minutes with no completed seed:
kill the batch and re-run it for the seeds not on disk, or relaunch a fresh
operator from the last pushed checkpoint. A seed on disk is never re-recorded
to recover a stall. A `(deadline_default)` row marks a failed recording: move
its husk outside the repository (its spend counts) and re-record that seed
alone at P, logging the cause as it happens. No seed re-records for any other
reason.

### 1.7 The probe, the batches, the pause and the key

**The dry run**, in the recording checkout at P before the probe, echoes P's
sha256 of the declared file, the ten fields and the bare slate, with
`git status --porcelain --untracked-files=no` at 0 lines; with a stray
`AILIBI_BOUNDED_REBUTTAL=1` exported it exits 1.

**The probe** records seeds 0-1 as one leg on the leg's two workers
(`--seeds 0,1`); its gates (below) run before any batch. If seeds 0-1 hold no
meeting or no served route line, one extension leg names seeds 2-3 only; seeds
0-3 with a ballot and no served route line stop the card.

**The batches** (the operating discipline as the owner's process amendment of
2026-10-09 sets it, memo 8.7 item 5), each a batch of 5 naming only seeds not
on disk, never `--full`:

- after the two-seed probe: `2-6`, `7-11`, `12-16`, `17-21`, `22-26`, `27-31`,
  `32-36`, `37-41`, `42-46`, `47-49`;
- after an extension to seeds 0-3: `4-8`, `9-13`, `14-18`, `19-23`, `24-28`,
  `29-33`, `34-38`, `39-43`, `44-48`, `49`.

A probed seed is never re-recorded and no seed on disk is named again: the
recorder re-records any seed it is given.

**After every batch**, in the delivery checkout and a bare shell: the tally,
the re-projection and the count-only key scan, then a pushed `record:`
checkpoint. **After the probe and after every second batch** (10 seeds),
before that checkpoint: the validity gate with the declared config and
`--expected-seeds 0-N`, `verify_samples.sh`, the golden's directory walk, the
census conformance cells (the cooldown and route cells included), the
scorecard fold, `measure_baseline.py --honesty` (a raise is a stop) and
`scan_recording_packets.py`. A checkpointed seed is never re-recorded, so a
gate failure stops the sitting and names the batches it covers.

**The pause.** Before each batch the operator checks a pause file outside the
repository. If it exists, no batch starts: the key file is deleted, the last
checkpoint is pushed, and the operator log (outside the repository) names the
seed reached and the next batch. The next sitting opens a new 18 h window,
copies the key again and resumes at the named batch; its recording wall adds
to the sum. A batch in flight when a pause is called finishes, runs its gates
and pushes its checkpoint before the pause takes effect; no batch is killed to
pause (a stall is the only kill), so a pause never strands a half-recorded
seed.

**The recording shell** sets only round 2's slate with `AILIBI_SAMPLE_DIR` and
`AILIBI_MANIFEST` on this round's set:

```
AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b \
AILIBI_LLM_MEETING_MODEL=Qwen/Qwen3.6-27B AILIBI_NUM_PLAYERS=9 AILIBI_NUM_IMPOSTORS=2 \
AILIBI_TASKS_PER_CREWMATE=2 AILIBI_SAMPLE_DIR=replays/candidates/stage-b-r3/9p2i \
AILIBI_MANIFEST=replays/candidates/stage-b-r3/9p2i/MANIFEST.md \
AILIBI_REFRESH_WORKERS=2 AILIBI_SEED_MAX_ATTEMPTS=8 \
  uv run --env-file <key file> bash scripts/refresh_samples.sh --seeds <the leg's seeds> \
    --expect-levers "" --experiment-config replays/candidates/stage-b-r3/experiment-config.json
```

**The key.** `FEATHERLESS_API_KEY` is copied programmatically from the main
checkout's untracked `.env` to a mode-0600 file in a mode-0700 directory
outside every checkout, by a command whose output goes straight to that file,
and is never printed or logged. It is passed only by `uv run --env-file`, and
the file is deleted at a pause and when the sitting ends. The recorder prints
the key's first eight characters into its run log; that log stays outside the
repository. Every key scan is count-only (gzip decompressed) and must read 0.
No rendered prompt, transcript text or seed-band prefix is printed anywhere;
every census and scan is count-only, keyed by (set, meeting).

### 1.8 The three columns, and each cell's source

**Round 1** (`replays/candidates/stage-b-r1/9p2i`) and **round 2**
(`replays/samples/9p2i`, era `stage-b-r2`) are computed at `F` through the
production path, never typed: `publish_gameplay_census.py --set-dir DIR
--json-stdout`, `publish_process_scorecard.py --set-dir DIR --json-stdout`,
`measure_baseline.py DIR --honesty --json`, the validity gate's
`no_betrayal_ballots_or_accusations`, and the route-check replay run with
`--set r1=<F>:R1 --set r2=<F>:R2` into scratch, each read through the readings
command (1.13). At `F`, the census and scorecard `--set-dir
replays/samples/9p2i --json-stdout` equal the shipped `samples/9p2i` entries in
1,753 of 1,753 and 108 of 108 leaves (the census page grew from the 1,324
leaves the card counted at `76270d6c` by the held-data and route cells);
every round-1 and round-2 count that round 2's audit section 6 and this card's
Evidence and table state (245 counts) re-measures with 0 differing; and the
route-check replay's r1 and r2 `rule_inputs` equal the committed
`experiments/lab/results-route-check-replay.json` in 24 of 24 leaves. Section 3
gives the commands, their exits and the planted proofs.

**Round 3** comes only from the same commands run on
`replays/candidates/stage-b-r3/9p2i`, the route-check replay at the delivery
head with r1, r2 and r3 columns into scratch, and the route-lines instrument's
r3 column beside it. A cell no named source counts is "not carried" and is not
measured another way.

"Conf." cells must read exactly as built; a miss is a code defect that stops
the round. "Reported" cells carry no rule. Rates carry Wilson 95% intervals.
No column is pooled with another. Every cell is named by its census key; a
cell outside the census names its command. The values below are the card's,
re-measured at `F`; a held-data cell the card marked "measured at F" carries
its `F` value.

| arm | cell | round 1 | round 2 | round 3 reading |
|---|---|---|---|---|
| physical witness | `vent_exits_seen_only_from_room_left`; `vent_band_resting_only_on_room_left` | 0/72; 0/24 | 0/72; 0/24 | Conf. 0; 0 |
| look and wait | `surfacings_before_cap_in_view`; `trips_longer_than_cap` | 0/72; 0/63 | 0/72; 0/66 | Conf. 0; 0 |
| look and wait | `vent_exits_seen_from_exit_room` (beside it `vent_exits_into_visibly_occupied_room`) | 8/72, effective (0/72) | 8/72, effective (0/72) | round 2's rule: effective at 0.30 or below; not effective at 0.52 or above, naming the hidden-travel escalation; partial between; n/a with no vent exit |
| look and wait | `forced_surfacings`; table `ticks_inside_per_trip`; `in_place_surfacings_near_crew`; `kills_soon_after_surfacing` | 13/72; 1 tick 51, 2 ticks 6, 3 ticks 2, 4 ticks 13; 2/37; 0/227 | 5/72; 1 tick 49, 2 ticks 3, 3 ticks 15, 4 ticks 5; 2/44; 0/195 | reported |
| own fresh kill | `vent_entries_not_after_own_fresh_kill` | 0/142 | 0/140 | Conf. 0 |
| full reset | `stale_report_meetings`; `report_corpses_older_than_last_close`; `play_resumes_with_impostor_in_vent`; `play_resumes_with_corpse`; `kills_in_grace_window_after_regroup`; `prompts_missing_a_regroup_notice` | 0/118; 0/68; 0/110; 0/110; 0/139; 0/782 | 0/114; 0/64; 0/102; 0/102; 0/109; 0/722 | Conf. 0 each (grace window T+1 to T+6) |
| full reset | false resume perceptions | not carried | not carried | carried by mechanism and golden, as the owner confirms |
| full reset | `skipped_report_meetings`; `trips_closed_by_regroup`; `kill_witness_button_calls_soon_after_regroup`; table `trigger_tick_events_dropped_by_regroup`; `meetings_opening_with_impostor_in_vent` (beside them `post_meeting_kills_soon_after`) | 70/118; 46/142; 0/6; Moved 51, TaskProgressed 26, TaskCompleted 6; 66/124 (0/139) | 51/114; 47/140; 0/3; Moved 46, TaskProgressed 22, TaskCompleted 10; 66/117 (0/109) | reported |
| one reply | `rebuttals_differing_from_selector`; `meetings_with_second_repeat_speaker` | 0/121; 0/124 | 0/117; 0/117 | Conf. 0; 0 |
| one reply | `opener_rebuttals_answering_charged_tick`; `rebuttals_redirect_only` | 19/19 (82 not evaluable); 17/121; effective | 17/18 (69 not evaluable); 27/117; effective | round 2's rule, verbatim: effective if half or more answer; not effective below 0.2, or if redirect-only reaches half; partial otherwise; conflicting if both hold; n/a with none evaluable |
| one reply | `accused_opener_answers`; `rebuttals_with_alibi`, `rebuttals_with_whereabouts`, `rebuttals_with_sighting`; `rebuttal_accusations_against_earlier_speakers`; table `rebuttal_beneficiaries` | 101/112; 104/121, 104/121, 91/121; 121/121; 71, 30, 17, 3 | 87/105; 89/117, 89/117, 79/117; 116/116; 59, 28, 28, 1, 1 | reported |
| body handle | `report_openings_with_kill_tick_handle` | 0/118 | 0/114 | Conf. 0 |
| kill row | `own_kill_rows_breaching`; rows served (its denominator) | 0/4; 4 | 0/23; 23 | Conf. 0; present when one or more |
| kill row | `own_kill_rows_cited_by_holder`; honesty cell 5 (`kill_holders`, `kill_holders_citing_the_kill`) | 3/4; 4 holders, 3 of 4 | 21/23; 23 holders, 21 of 23 | reported |
| impostor ballot | `recorded_teammate_ballot_targets`; the gate's betrayal check (`validity_gate.py`) | 0/203; 0 of 717 | 0/200; 0 of 691 | Conf. 0; 0 |
| impostor ballot | honesty cell 3 (`ejects_citing_only_neutral`) | 0/107 | 0/111 | round 2's rule: holds at 0.10 or below; does not bind above 0.25; between otherwise; n/a with no impostor EJECT |
| impostor ballot | `impostor_eject_ballots`; `impostor_ejects_labelled_supported`; `authored_teammate_ballot_targets` | 107/203; 107/107; 16/203 | 111/200; 111/111; 16/200 | reported |
| self-report off | `impostor_openers` | 0/124 | 0/117 | Conf. 0 |
| kill cooldown | `kill_cooldowns_differing_from_recorded`, table `kill_cooldown_writes_by_writer` | 0/487 against 4 | 0/447 against 6 (100, 195, 152) | Conf. 0 against 6, a count at each of the three writers |
| route lines | `route_lines_false_to_the_map`; `route_lines_off_the_table`; presence `meetings_with_a_route_line` (beside them `ballots_carrying_route_lines` and tables `route_lines_per_meeting`, `route_steps_by_reading`) | n/a | n/a | Conf. 0; 0; present, a count above 0 (a presence of 0 is a miss) |
| route check | the route-check replay's M and W (`rule_inputs`); the reach of (a), (b) and (c) over M (`rule_inputs.R`) and of (c) over W; beside them the route-lines instrument's served reach on r3 | 29; 0; 8, 8, 20; 0 | 40; 7; 15, 16, 29; 7 | reported as a process count, never a bar on correctness; the step reads M |
| per seat | `reporter_seats_ejected`, `other_crewmate_seats_ejected`, `impostor_seats_ejected`; the same three `_without_vent_proof`; the same three `_with_vent_proof`; `reporters_among_ejected_crewmates`, `reporters_among_crewmate_seats` | 11/118, 2/372, 35/194; 11/98, 2/303, 15/160; 0/20, 0/69, 20/34; 11/13, 118/490 | 17/114, 5/367, 41/195; 17/93, 5/291, 20/158; 0/21, 0/76, 21/37; 17/22, 114/481 | reported; the flag below reads the reporter and other-crewmate cells without vent proof |
| kill witness | `held_kill_witnesses_ejected`; table `held_kill_next_meeting_outcomes`; `held_kill_killers_ejected`, `held_kill_killers_ejected_at_any_later_meeting` | 0/3; killer ejected 3; 3/3, 3/3 | 5/14; witness 5, other 1, no one 2, killer 1, two or more killer 5; 6/14, 8/14 | reported |
| counterfactual | `ejections_undone_with_impostor_ballots_as_skip`; `ejections_undone_with_impostor_ballots_removed`; `ejections_carried_only_by_impostor_ballots`; table `retally_outcome_changes` | 8/54; 2/54; 0/54 | 14/66; 5/66; 0/66 | reported |
| held data | `holds_nothing_skips_naming_no_candidate` (table `holds_nothing_skips_by_source`); `cited_lines_true_to_the_route`, `cited_lines_false_to_the_route` (tables `cited_placements_by_kind_and_verdict`, `supported_ejects_not_checkable_by_reason`) | 0/256; 244/259, 15/259 (the second and third measured at F) | 0/214; 278/281, 3/281 (the second and third measured at F) | reported, each beside its definition |
| held data | `ejections_on_a_reconcilable_pair`; `ejections_charged_on_a_reconcilable_pair`; `witness_meeting_ejections_on_a_reconcilable_pair`; `witness_meeting_ejections_charged_on_a_reconcilable_pair`; `charges_on_a_reconcilable_pair` | 31/54; 29/54; 0/3 (measured at F); 0/3; 265/406 | 41/66; 40/66; 7/12 (measured at F); 7/12; 276/402 | reported; the charged count is the route-check replay's M and its witness form W |
| held data | `skips_holding_nothing`; `ballots_citing_a_rebuttal` with `ballots_countering_with_a_rebuttal` beside | 256/330; 70/707, 150/707 | 214/281; 57/691, 175/691 | reported; for ballots citing a rebuttal the turn citation is the cell and the counter slot sits beside it, as the owner confirms |
| envelope | impostor win share (`impostor_wins`) | 34/50 = 0.68 | 24/50 = 0.48 | non-gating; flagged outside 0.20-0.60 (route lines that save witnesses help the crew, so the floor is watched); read by the step rule |
| envelope | the re-keyed reporter flag (below), `reporter_seats_ejected_without_vent_proof` against `other_crewmate_seats_ejected_without_vent_proof` | relative rate 17.0 | relative rate 10.6 | non-gating; flagged above the confirmed bar; never read by the step rule |
| reported | `role_correct_ejections`; innocent ejections (its denominator less its numerator); `meetings_with_vent_proof`; kills (`kills_seen_by_crew`'s denominator); `impostor_cooldown_zero_at_open`; the win split (`impostor_wins`); scorecard rows 1-9 (`publish_process_scorecard.py --set-dir`) | 39/54; 15; 26/124; 227; 84/203; 16-34 | 44/66; 22; 24/117; 195; 54/200; 26-24 | reported, gating nothing |

Round 2's reading under the old reporter line (17/114 = 0.149, flagged above
0.104) stands as recorded; the readings command does not compute that line and
nothing re-scores round 2. Round 2's 40 is a constant (`ROUND_2_M`), and the
command exits 1 unless the route JSON's r2 column reads it.

### 1.9 The re-keyed reporter flag

`readings.py` reads `reporter_seats_ejected_without_vent_proof` (k1/n1)
against `other_crewmate_seats_ejected_without_vent_proof` (k2/n2); the
relative rate is (k1/n1)/(k2/n2), compared by cross-multiplication in exact
fractions, so no zero is divided by. With k2 = 0, any reporter seat ejected
flags as "reporters alone". **The bar is A, confirmed by the owner on
2026-10-09** (section 2): flagged above twice round 2's relative rate,
2 x 10.64 = 21.28. B and C are recorded beside it as the alternatives the
owner declined, read on the same cells (rates without vent proof; the
baseline-9 column is readable only at `d41c9006`, context only):

| bar | line | baseline-9 9p2i: 7/75 vs 2/243 | round 1: 11/98 vs 2/303 | round 2: 17/93 vs 5/291 |
|---|---|---|---|---|
| **A** (confirmed) twice round 2's relative rate | above 21.28 | 11.3, not flagged | 17.0, not flagged | 10.6, not flagged |
| B (declined) round 2's relative rate itself | above 10.64 | flagged | flagged | at the line, not flagged |
| C (declined) the reporter rate alone (amends the form) | above 17/93 = 0.183 | 0.093, not flagged | 0.112, not flagged | at the line, not flagged |

Why A: the other-crewmate numerators are 2, 2 and 5, so one ejection more or
less moves the relative rate by a factor of 1.25 to 2 (round 2 reads 8.9 with
6, 13.3 with 4); B flags both earlier 9-player columns and would flag noise in
a round that changed nothing; C reads the reporter seat alone, which the
re-keying set aside. The flag is non-gating and the step rule never reads it:
while R6 holds every reporter is a crewmate, so any reporter line reads role
(memo 8.2 item 1). Every reading in this table re-measures at `F` through the
readings command (section 3).

### 1.10 The carrier of round 2's not-carried cells

Of round 2's four not-carried cells (its audit 8), three are census cells now:
the regroup notice (`prompts_missing_a_regroup_notice`, a Conf. cell),
holds-nothing SKIPs (`skips_holding_nothing`, with
`holds_nothing_skips_naming_no_candidate` and the table
`holds_nothing_skips_by_source`), and ballots citing a rebuttal, which read the
turn citation as the cell (`ballots_citing_a_rebuttal`) with the counter slot
beside it (`ballots_countering_with_a_rebuttal`). False resume perceptions have
no count source; their carrier is mechanism and golden: the shared helper
`compose_resume_events` (`orchestrator/replay.py`) with its planted tests, and
the golden's byte-equal re-render of every recorded prompt. Round 2's "not
carried" lines stay as recorded. The owner confirmed this carrier as proposed
on 2026-10-09 (section 2).

### 1.11 The step rule after round 3

The rule, carried whole from the card:

> **The step rule after round 3.** With every Conf. cell at 0, round 3's point share of impostor wins neither above
> 0.60 nor below 0.20, and round 3's misjudged route cases (the route-check replay's M) at or below round 2's 40,
> it names the era-keyed promotion of round 3 as the shown set; otherwise it names round 2 staying shown, with
> round 3 kept as a comparison record. Either step is the owner's to take or override.

`readings.py --step` prints one line by this sentence, computed from the Conf.
misses, `impostor_wins` and M alone. It reads no reporter line and no
role-correct figure: with the flag forced on (reporter numerator 60) or
`role_correct_ejections` edited, the line beginning `step rule:` is
byte-identical to the unedited run's (section 3). The witness subset, the
reach of each check and M per ejection are printed beside M and not read. The
rule gates no acceptance item. The owner confirmed on 2026-10-09 that it may
take the impostor win share as one of its conditions (section 2). The step
itself is taken by the orchestrator, on the owner's criteria and leaning, by
the owner's delegation of 2026-10-09 (memo 8.8, quoted whole in section 2);
the decision is written into this audit with the readings it rests on, and a
promotion is one card and one merge, the merge the owner's because it
publishes (memo 8.7 item 3).

### 1.12 The order of the assessment, and the decision menu

Round 3's column comes only from the census and scorecard `--set-dir
replays/candidates/stage-b-r3/9p2i --json-stdout`, `measure_baseline.py
replays/candidates/stage-b-r3/9p2i --honesty --json`, the gate's betrayal check
and the route-check replay at the delivery head with r1, r2 and r3 columns
into scratch, through `readings.py`. The assessment reads, in this order: the
process cells (the scorecard's rows, three columns); each Conf. cell and
carried reading; the route cells; the cooldown cell; the envelope and the
flag; the route-check count; the step the rule names; the reported rows;
role-correct ejection, the balance and the win split, gating nothing.

It gives no verdict. The decision menu: the step the rule names; for the route
field, adopt by the era-keyed promotion, iterate under a new value, or keep
round 2 shown; Conf. cells only for the other nine fields; with the promotion,
its card's follow-ups (a public-results label for the route field, which
`frontend/src/components/PublicResults.tsx` cannot name today; the era
registry entry; the pin sweep). Pooling round 3 with round 2 or round 1
raises the census era refusal.

### 1.13 The readings command, whole

Saved as `readings.py` and run with `python3` (standard library only,
count-only; sha256
`9e22e40c420e6082b05b55596b0073fbf53c0b5c7e0f22cb04ee76733d257abc` as
extracted from the card at `F`, 15,712 bytes), as
`python3 readings.py CENSUS.json HONESTY.json ROUTE.json --column {r1,r2,r3} [--bar {A,B,C}] [--after] [--step]`.
The assessment passes `--bar A`, the confirmed bar.

```python
"""Print round 3's pre-registered table from its named sources (count-only).

Usage: readings.py CENSUS.json HONESTY.json ROUTE.json --column {r1,r2,r3}
                   [--bar {A,B,C}] [--after] [--step]

CENSUS.json is one census section, `publish_gameplay_census.py --set-dir DIR
--json-stdout`. HONESTY.json is `measure_baseline.py DIR --honesty --json`.
ROUTE.json is the route-check replay's scratch JSON; --column names the column
whose `rule_inputs` are read, and its r2 column must read round 2's M. --bar
names the reporter flag's bar (default A, the proposed one; the assessment
passes the bar the owner confirmed). With --after, each reading is computed by
its pre-registered rule and the command exits 1 on a Conf. miss (an empty
cooldown writer and, on r3, route cells out of scope or a route presence of 0
included); without it, values only. With --step (r3, after --after), the last
line names the step the step rule names, computed from the Conf. misses,
`impostor_wins` and M alone: never from the reporter flag or a role-correct
figure.
"""

import argparse
import json
import math
import sys
from fractions import Fraction

ROUND_2_M = 40  # the route-check replay's misjudged cases on round 2 (committed r2 column)
ROUND_2_RELATIVE = Fraction(17 * 291, 93 * 5)  # 17/93 against 5/291, without vent proof: 10.64
BARS = {
    "A": ("relative", 2 * ROUND_2_RELATIVE, "above twice round 2's relative rate, 21.28"),
    "B": ("relative", ROUND_2_RELATIVE, "above round 2's relative rate, 10.64"),
    "C": ("reporter", Fraction(17, 93), "the reporter rate alone above 17/93 = 0.183"),
}

parser = argparse.ArgumentParser()
parser.add_argument("census")
parser.add_argument("honesty")
parser.add_argument("route")
parser.add_argument("--column", required=True, choices=("r1", "r2", "r3"))
parser.add_argument("--bar", default="A", choices=tuple(BARS))
parser.add_argument("--after", action="store_true")
parser.add_argument("--step", action="store_true")
args = parser.parse_args()
if args.step and not (args.after and args.column == "r3"):
    sys.exit("--step reads round 3: pass --column r3 --after --step")


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


census = json.load(open(args.census))
if "sets" in census:
    sys.exit("CENSUS.json must be one --set-dir section, never the published page")
honesty = json.load(open(args.honesty))[0]["ballot_conduct"]
columns = {column["label"]: column for column in json.load(open(args.route))["columns"]}
if columns["r2"]["rule_inputs"]["M"] != ROUND_2_M:
    sys.exit(f"the route JSON's r2 column reads M {columns['r2']['rule_inputs']['M']}, not {ROUND_2_M}")
route = columns[args.column]["rule_inputs"]
after = args.after
cells = census["cells"]
tables = census["tables"]
misses = []


def cell(key):
    c = cells[key]
    return c["numerator"], c["denominator"]


def show(label, key):
    k, n = cell(key)
    if not cells[key]["in_scope"]:
        print(f"  {label} [{key}]: n/a (out of scope: {cells[key]['scope']})")
        return k, n
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


def table(label, key):
    print(f"  {label} [{key}]: {json.dumps(tables[key]['counts'], sort_keys=True)}")


print(f"column {args.column}; games {census['games']}; meetings {census['meetings']}; "
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
table("ticks inside per surfaced trip", "ticks_inside_per_trip")
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
conf("prompts after a regroup missing an earlier regroup's notice", "prompts_missing_a_regroup_notice")
show("  beside: kills within 2 ticks of any meeting", "post_meeting_kills_soon_after")
show("skipped report meetings", "skipped_report_meetings")
show("trips closed by a regroup", "trips_closed_by_regroup")
show("kill-witness button calls within 6 ticks of a regroup",
     "kill_witness_button_calls_soon_after_regroup")
table("dropped trigger-tick events", "trigger_tick_events_dropped_by_regroup")
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
table("beneficiaries", "rebuttal_beneficiaries")
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
print("route lines")
routed = cells["meetings_with_a_route_line"]["in_scope"]
conf("steps false to the map", "route_lines_false_to_the_map")
conf("lines off the table", "route_lines_off_the_table")
kp, _ = show("meetings with a route line (presence)", "meetings_with_a_route_line")
show("ballots carrying route lines", "ballots_carrying_route_lines")
if routed:
    table("lines per meeting", "route_lines_per_meeting")
    table("steps by reading", "route_steps_by_reading")
if after and args.column == "r3":
    if not routed:
        print("    Conf.: BREACH (the route field is out of scope on round 3)")
        misses.append("route field out of scope")
    elif kp == 0:
        print("    Conf.: BREACH (no route line served: the route field reads absent)")
        misses.append("route field presence 0")
    else:
        print(f"    presence: present ({kp} meetings)")
print("route check (a process count, never a bar on correctness)")
m, w = route["M"], route["W"]
reach = route["R"]
print(f"  misjudged cases M {m}; at witness meetings W {w} (rule_inputs, column {args.column})")
print(f"  reach over M: (a) {reach['a']}, (b) {reach['b']}, (b-snapshot) {reach['b_snapshot']}, "
      f"(c) {reach['c']}; over W: (c) {route['R_W']['c']}")
print("per seat (reported)")
for seat in ("reporter", "other_crewmate", "impostor"):
    for suffix in ("", "_without_vent_proof", "_with_vent_proof"):
        key = f"{seat}_seats_ejected{suffix}"
        show(key.replace("_", " "), key)
show("reporters among ejected crewmates", "reporters_among_ejected_crewmates")
show("reporters among crewmate seats", "reporters_among_crewmate_seats")
print("kill witness (reported)")
show("held kill witnesses ejected", "held_kill_witnesses_ejected")
table("next meeting after a held kill", "held_kill_next_meeting_outcomes")
show("held kills whose killer was ejected at the next meeting", "held_kill_killers_ejected")
show("at any later meeting", "held_kill_killers_ejected_at_any_later_meeting")
print("counterfactual (reported)")
show("ejections undone with impostor ballots as SKIP", "ejections_undone_with_impostor_ballots_as_skip")
show("ejections undone with impostor ballots removed", "ejections_undone_with_impostor_ballots_removed")
show("ejections whose floor only impostors met", "ejections_carried_only_by_impostor_ballots")
table("re-tally outcome changes", "retally_outcome_changes")
print("held data (reported, each beside its definition)")
show("holds-nothing SKIPs whose inputs name no living candidate",
     "holds_nothing_skips_naming_no_candidate")
table("holds-nothing SKIPs naming a candidate, by source",
      "holds_nothing_skips_by_source")
show("cited lines true to the route", "cited_lines_true_to_the_route")
show("cited lines false to the route", "cited_lines_false_to_the_route")
table("cited placements by kind and verdict", "cited_placements_by_kind_and_verdict")
table("supported EJECTs not checkable, by reason", "supported_ejects_not_checkable_by_reason")
show("ejections whose target had a reconcilable pair", "ejections_on_a_reconcilable_pair")
show("ejections charged on a reconcilable pair", "ejections_charged_on_a_reconcilable_pair")
show("  at witness meetings: target had a pair", "witness_meeting_ejections_on_a_reconcilable_pair")
show("  at witness meetings: charged on a pair",
     "witness_meeting_ejections_charged_on_a_reconcilable_pair")
show("charges resting on a reconcilable pair", "charges_on_a_reconcilable_pair")
show("SKIPs labelled as holding nothing", "skips_holding_nothing")
show("ballots citing a rebuttal (the cell)", "ballots_citing_a_rebuttal")
show("  beside: ballots countering with a rebuttal", "ballots_countering_with_a_rebuttal")
print("envelope (non-gating)")
k, n = show("impostor win share", "impostor_wins")
if after and n:
    share = Fraction(k, n)
    print(f"    envelope: {'flagged above 0.60' if share > Fraction(3, 5) else 'flagged below 0.20' if share < Fraction(1, 5) else 'inside 0.20-0.60'}")
k1, n1 = cell("reporter_seats_ejected_without_vent_proof")
k2, n2 = cell("other_crewmate_seats_ejected_without_vent_proof")
form, line, words = BARS[args.bar]
if n1 == 0 or n2 == 0:
    flag = "n/a (no reporter seat or no other crewmate seat without vent proof)"
elif form == "reporter":
    flag = ("flagged" if Fraction(k1, n1) > line else "not flagged") + f" (reporter rate {k1}/{n1})"
elif k2 == 0:
    flag = "flagged, reporters alone" if k1 > 0 else "not flagged (no seat ejected)"
else:
    relative = Fraction(k1 * n2, k2 * n1)
    flagged = k1 * n2 > line * (k2 * n1)  # cross-multiplied, exact
    flag = f"relative rate {float(relative):.1f}, {'flagged' if flagged else 'not flagged'}"
print(f"  the re-keyed reporter flag, bar {args.bar} ({words}): reporter seats {k1}/{n1} against "
      f"other crewmate seats {k2}/{n2} without vent proof: {flag}; never read by the step rule")
print("reported, gating nothing")
rk, rn = show("role-correct ejections", "role_correct_ejections")
print(f"  innocent ejections: {rn - rk} of {rn} ejections")
show("meetings with vent proof", "meetings_with_vent_proof")
print(f"  kills [kills_seen_by_crew, its denominator]: {cell('kills_seen_by_crew')[1]}")
show("impostors able to kill when a meeting opened", "impostor_cooldown_zero_at_open")
print(f"  the win split [impostor_wins]: {n - k} crew, {k} impostor")
if args.step:
    inside = n > 0 and Fraction(1, 5) <= Fraction(k, n) <= Fraction(3, 5)
    step = ("the era-keyed promotion of round 3 as the shown set"
            if not misses and inside and m <= ROUND_2_M
            else "round 2 staying shown, with round 3 kept as a comparison record")
    print(f"step rule: names {step}, the owner's to take or override "
          f"(Conf. misses {len(misses)}; impostor wins {k}/{n}; M {m} against round 2's {ROUND_2_M})")
if misses:
    print(f"Conf. misses: {', '.join(misses)}")
    sys.exit(1)
```

### 1.14 The re-projection command, whole

Saved as `reproject.py` and run with `python3` (standard library only,
count-only; sha256
`0cd632e045dc06725df8bdc07a8320876a219a6af53fe64db5b494543496445c` as
extracted from the card at `F`, 2,365 bytes), as
`python3 reproject.py replays/candidates/stage-b-r3/9p2i replays/samples/9p2i <summed recording wall, s>`.

```python
"""Re-project round 3's spend against the 90% stops (count-only).

Usage: reproject.py CAND_DIR R2_DIR SUMMED_WALL_SECONDS

Each count is (the candidate's total over its completed seeds / round 2's
total over the same seeds) x round 2's leg total; the wall is the summed
recording wall / the completed seeds x 50. Exits 1 when any figure is past its
stop, or when any call's cost is not zero.
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
r2 = tally(sys.argv[2])
wall = float(sys.argv[3])
seeds = sorted(cand)
if not seeds or any(s not in r2 for s in seeds):
    sys.exit("every completed candidate seed must have round 2's seed beside it")
stops = []
print(f"completed seeds {len(seeds)} ({seeds[0]}-{seeds[-1]})")
for index, name in enumerate(("calls", "input", "output")):
    done = sum(cand[s][index] for s in seeds)
    base = sum(r2[s][index] for s in seeds)
    projected = done / base * sum(v[index] for v in r2.values())
    past = projected > STOPS[name]
    stops += [name] if past else []
    print(f"  {name}: {done} / {base} x round 2 = {projected:,.0f} "
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

The tally (count-only), round 2's command carried whole and unchanged:

```
uv run python -c 'import glob,json,sys
c=i=o=0; u=0.0
for p in glob.glob(sys.argv[1]+"/replay-seed-*.jsonl"):
  for r in map(json.loads,open(p)):
    for k in r.get("llm_calls") or []:
      c+=1; i+=k["input_tokens"]; o+=k["output_tokens"]; u+=k["cost_usd"]
print(c,i,o,u)' <set dir>
```

## 2. The owner's confirmation (dated addendum, 2026-10-09)

This section is the `coordination:` commit the card calls Q. Section 1 is
unchanged, byte for byte, from P (`641b4254`). It quotes the owner's ruling
of 2026-10-09 that confirms, as proposed, the five points the card reserves
for the owner, and the owner's delegation of the step after the round. The
confirmation was given before P, on the amended card; it amends nothing in
section 1. By memo 8.7, the recording starts once P and Q are pushed and P is
reviewed; no provider is called before then.

### 2.1 The ruling, verbatim and dated

On **2026-10-09** the owner asked how long the project needs to reach its
finalized state and which redundancies the remaining workflow carries, then
ruled, verbatim:

> Apply all five redundancy removals and confirm the five points as proposed

Memo section 8.7, which records the ruling and applies it, whole:

> The owner asked how long the project needs to reach its finalized state and which redundancies the remaining
> workflow carries, then ruled, verbatim: "Apply all five redundancy removals and confirm the five points as
> proposed". The five removals, in force from this date for every remaining card and for round 3's recording:
>
> 1. **CI is the gate record.** The project gate (`bash scripts/check.sh`) is run by CI on every pushed head; its
>    green run at the exact head, cited by run id in the pull request and the card, stands as the gate record.
>    Workers no longer run it locally at the final head and no longer add a card-only commit to record it. AGENTS.md's
>    requirement that the gate passes is met by that run.
> 2. **Message-argument survivors are nonblocking after the first fix round.** In the bounded review standard, a
>    mutation that replaces a message argument with a constant and survives is reported, and blocks only in the
>    first review round of a card; from the first fix round on it is nonblocking. The behavioural classes (a dropped
>    filter or wrapper, a swapped collection, a comparison made a None test, a role, kind, room or tick read made a
>    constant, a dropped tuple member, swapped branches, a loaded source read as its literal) stay blocking.
> 3. **A promotion is one card.** If round 3 is promoted, the era-keyed promotion and the tour's re-curation are one
>    card, one pull request and one merge (the owner's, because it publishes), not two stacked cards.
> 4. **Document-only changes get the documentation lens only.** A card or commit that changes only documents (a close
>    audit, a card closure, a planning document) is verified by the documentation lens alone.
> 5. **Recording gates every second batch, checkpoints every batch.** In a recording sitting, each batch of five ends
>    with the tally, the re-projection, the count-only key scan and a pushed checkpoint; the full gate set runs after
>    the probe and after every second batch. A checkpointed seed is never re-recorded, so a later gate failure stops
>    the sitting and names the batches it covers. `tasks/work/stage-b-record-r3.md` carries the amendment in its
>    Acceptance, Constraints and Validation.
>
> **The round-3 confirmation, given before P.** The same ruling confirms, as proposed, the five points the record
> card reserves for the owner (8.5): the standing ceilings (2,800 calls; 17,500,000 input and 750,000 output tokens;
> a 12 h recording wall summed over sittings, each inside an 18 h window; $0.00 marginal; each with its stop at 90
> percent); the pre-registration as the card tables it; the reporter flag re-keyed by seat and vent proof with bar A,
> flagged above twice round 2's relative rate (21.28), non-gating and never read by the step rule; the carrier of round
> 2's not-carried cells as the card states it (resume perceptions by the resume helper plus the golden's byte-equal
> re-render; the turn citation as the cell for ballots citing a rebuttal, with the counter slot beside it); and that
> the step rule may take the impostor win share as one of its conditions. The pre-registration commit P is written
> from the amended card; Q, the dated addendum, quotes this confirmation; the recording starts once P and Q are
> pushed and P is reviewed. The step after the round stays the owner's to take or override.

### 2.2 The five points, each against the owner's words

The owner's words for every point, 2026-10-09: "Apply all five redundancy
removals and confirm the five points as proposed". Beside each point, the words of memo 8.7's confirmation paragraph that name it, quoted
verbatim, and the place section 1 states it.

| point the card reserves for the owner | memo 8.7's confirmation, verbatim | section 1 |
|---|---|---|
| 1. the ceilings | "the standing ceilings (2,800 calls; 17,500,000 input and 750,000 output tokens; a 12 h recording wall summed over sittings, each inside an 18 h window; $0.00 marginal; each with its stop at 90 percent)" | 1.5; the stops in 1.6 |
| 2. the pre-registration | "the pre-registration as the card tables it" | the whole of section 1 |
| 3. the reporter flag's form and bar | "the reporter flag re-keyed by seat and vent proof with bar A, flagged above twice round 2's relative rate (21.28), non-gating and never read by the step rule" | 1.9, bar A; B and C declined |
| 4. the carrier of round 2's not-carried cells | "the carrier of round 2's not-carried cells as the card states it (resume perceptions by the resume helper plus the golden's byte-equal re-render; the turn citation as the cell for ballots citing a rebuttal, with the counter slot beside it)" | 1.10 |
| 5. the step rule may read the win share | "that the step rule may take the impostor win share as one of its conditions" | 1.11 |

**How this record applies the five process amendments** (memo 8.7 items 1 to
5). The project gate's record at each pushed head is CI's green run there,
cited by run id in the pull request and the card's Results; no local
`check.sh` runs at the final head and no card-only commit records a gate,
while the targeted suites, the document gates and the instruments' `--check`
runs are still run and quoted (item 1). The recording discipline is 1.7's:
each batch of five ends with the tally, the re-projection, the count-only key
scan and a pushed checkpoint, and the full gate set runs after the probe and
after every second batch (item 5). If the step is the promotion, the era-keyed
promotion and the tour's re-curation are one card and one merge, the owner's
because it publishes (item 3). Items 2 and 4 set the review standard for this
record's pull request.

### 2.3 The step after round 3, delegated to the orchestrator

On **2026-10-09** the owner ruled, verbatim:

> I will let this session, as the orchestrator, decide about promoting round 3. Keep what I want for the project in mind. I lean towards wanting to promote round 3, but if there is an issue you find with recording, or think it is really a step down in terms of gameplay, you can make the decision to keep round 2.

Memo section 8.8, whole:

> The owner ruled, verbatim: "I will let this session, as the orchestrator, decide about promoting round 3. Keep what
> I want for the project in mind. I lean towards wanting to promote round 3, but if there is an issue you find with
> recording, or think it is really a step down in terms of gameplay, you can make the decision to keep round 2."
>
> So the step the record card pre-registers (promote round 3 as the shown set by the era-keyed path if every
> conformance cell is 0, the win share is inside the band and the misjudged route-charge count did not rise;
> otherwise round 2 stays shown and round 3 is a comparison record) is taken by the orchestrator, on the owner's
> criteria and leaning: round 3 is promoted unless the recording carries an issue (a stop rule fired, a conformance
> cell above 0, a gate or scan failure, a ceiling breached, a seed outside the pre-registered protocol) or its
> gameplay is a real step down against the direction (grounded votes, honest process, the genre shape, showability,
> read on the pre-registered table and the census, never on role-correctness). The decision is written into the
> round-3 audit with the readings it rests on, and a promotion is one card and one merge (8.7, item 3), the merge
> still the owner's because it publishes.

So the step 1.11's rule names after the round is taken by the orchestrator on
the owner's criteria and leaning, and written into this audit with the
readings it rests on. The rule itself, its conditions and the table are
unchanged; the rule never reads the reporter flag or a role-correct figure,
and the step reads the pre-registered table and the census, never
role-correctness.

## 3. The pre-spend, at `F` and P, before the first seed

Nothing in this section called a provider. No key was copied, read or
referenced, and the recorder ran only as the dry run (3.6), with no seed.
Every command ran in a bare shell (`env | grep -c '^AILIBI_'` printed 0)
unless it names its own exports: 3.1 to 3.5 in this branch's worktree while
it was still at `F` with a clean status, before P; 3.6 in a recording checkout
detached at P; 3.7 in this worktree at Q. Scratch outputs lived outside the
repository; every census here is count-only, and no prompt, transcript text or
seed-band prefix was printed.

### 3.1 The preflight

- The declared file, made by inserting `, "route_lines_version": 1` before the
  closing brace of `replays/samples/9p2i/experiment-config.json` (316 bytes,
  `0c02fa61…5c192b`): 342 bytes, `a788b9eb…6d57d`, the card's figure (1.3).
- Read through `scripts/_declared_experiment.py`'s own loader at `F`: ten
  fields off their default, round 2's nine in their order and
  `route_lines_version`; the nine equal round 2's file's off-default fields;
  `FIELD_LAYER["route_lines_version"]` is `meeting`; `OMITTED_AT_DEFAULT`
  holds it; `engine_arguments` returns `{'redistribution_policy': 'lowest_id',
  'vent_witness_rule': 'physical', 'kill_cooldown_ticks': 6}`, equal to round
  2's; `prompt_versions_for_set("qwen3_6_27b", env={}, experiment_config=...)`
  serves the four stamps of 1.3; `self_report` False,
  `evidence_reasoning_version` and `contextual_self_report_version` None.
- Proof, two perturbations of the same payload: with one unknown key added
  (`unknown_switch`), validation is refused with pydantic's
  `extra_forbidden` message ("Extra inputs are not permitted") naming the key;
  with `route_lines_version` removed, the config equals round 2's and the
  re-serialized bytes equal round 2's declared file byte for byte.
- The instruments take `r3`: `COLUMN_LABELS` is `("s9", "r1", "r2", "r3")`
  in `experiments/lab/route_check_replay.py`, whose r3 column declares
  `replays/candidates/stage-b-r3/experiment-config.json`, and the route-lines
  instrument orders its columns by the same labels. The held-data and route
  cells exist under their cards' keys: the readings command (1.13) read every
  key it names from the round-1 and round-2 sections without a refusal.
- The field card's refusals pass at `F`, in the run of 3.5:
  `tests/orchestrator/test_experiment_arms.py::test_no_environment_sets_a_config_only_field`
  (no environment switch sets the field) and
  `::test_a_config_only_field_must_equal_the_runners_both_ways[route_lines_version]`
  (a runner and a recorded config that disagree on it are refused both ways),
  `tests/meetings/test_route_lines_arm.py::test_each_instrument_refuses_it_once_the_field_leaves_its_reads`
  (7 cases) and `::test_the_golden_refuses_it_once_the_field_leaves_its_reads`
  (an unthreaded reader refuses it), and
  `::test_the_runner_refuses_it_beside_each_legacy_overlay` (4 cases).

### 3.2 The before columns, computed

```
for d in replays/candidates/stage-b-r1/9p2i replays/samples/9p2i; do n=$(echo "$d" | tr / _)
  .venv/bin/python scripts/publish_gameplay_census.py --set-dir "$d" --json-stdout > <scratch>/census-$n.json
  .venv/bin/python scripts/publish_process_scorecard.py --set-dir "$d" --json-stdout > <scratch>/scorecard-$n.json
  .venv/bin/python scripts/measure_baseline.py "$d" --honesty --json > <scratch>/honesty-$n.json; done
.venv/bin/python -m experiments.lab.route_check_replay --set r1=<F>:replays/candidates/stage-b-r1/9p2i \
  --set r2=<F>:replays/samples/9p2i --out-json <scratch>/route.json --out-report <scratch>/route.md
```

| check | result |
|---|---|
| the six production commands above, and the route-check replay | exit 0 each |
| census `--set-dir replays/samples/9p2i` against the shipped `samples/9p2i` entry of `docs/gameplay-census.json`, leaf for leaf | 1,753 of 1,753 equal, 0 differing, exit 0 |
| scorecard `--set-dir replays/samples/9p2i` against the shipped entry of `docs/process-scorecard.json` | 108 of 108 equal, 0 differing, exit 0 |
| the route-check replay's r1 and r2 `rule_inputs` against the committed `experiments/lab/results-route-check-replay.json` | 24 of 24 leaves equal: r1 M 29, W 0, reach (a) 8, (b) 8, (c) 20, (c) over W 0; r2 M 40, W 7, reach 15, 16, 29, (c) over W 7 |
| `uv run python -m experiments.lab.route_check_replay --check`; `uv run python -m experiments.lab.route_lines_replay --check` | exit 0 each, "reproduced" (47.1 s and 48.2 s) |
| the tally (1.14) | `1556 9344346 433660 0.0` on round 1; `1502 9187880 418270 0.0` on round 2 |
| `validity_gate.py` on each set with its own declared config, `--expected-model Qwen/Qwen3.6-27B --require-zero-cost`, the four prompt-version pairs, `--expected-seeds 0-49 --require-one-recording-sha` | exit 0 each, ten checks PASS; the betrayal check 0 over 717 ballots on round 1 and 0 over 691 on round 2 |
| `python3 readings.py <census> <honesty> <route.json> --column r1 --after`, then `--column r2 --after` | exit 0 each; no Conf. miss; every reading as 1.8 states it |
| a count-only comparison holding every round-1 and round-2 count that round 2's audit section 6 (6.1's scorecard rows, 6.2 to 6.5) and this card's Evidence and table state, read from the readings output, the scorecard and census sections, the gate's line, the tally and the route JSON | 245 of 245 equal, 0 differing, exit 0 |

The 245 include the charged ejections equal to M (29 and 40) and their witness
form equal to W (0 and 7); round 2's old reporter line, read from the census
tables it was defined on (report-meeting ejections of reporters over report
meetings: 11/118 and 17/114), which the readings command does not compute; and
the route-check replay's r2 classes the Evidence names: (c) reaches 21 of 21
misjudged innocent ejections and 5 of 5 ejected witnesses, leaves 11 impostor
ejections unreached, and `evidence_reasoning_version = 2`'s offer holds 4,478
regroup-crossing rows of which it keeps 0. The 9 of those 11 that rest on a
vent sighting are the committed reports' count, reproduced by the two `--check`
runs, not by the comparison. Of the cells the card marked "measured at F":
`holds_nothing_skips_naming_no_candidate` 0/256 and 0/214;
`cited_lines_true_to_the_route` 244/259 and 278/281;
`cited_lines_false_to_the_route` 15/259 and 3/281;
`witness_meeting_ejections_on_a_reconcilable_pair` 0/3 and 7/12. No round-1 or
round-2 count moved.

Proofs, each against a scratch copy with one cell edited:

| copy | result |
|---|---|
| round 2's census section, `holds_nothing_skips_naming_no_candidate` denominator raised by one | `cells.holds_nothing_skips_naming_no_candidate.denominator: set-dir=215 shipped=214`; 1,752 of 1,753; exit 1 |
| round 2's scorecard section, `grounded_skip` numerator raised by one | `grounded_skip.numerator: set-dir=45 shipped=44`; 107 of 108; exit 1 |
| the scratch route JSON, r2 reach (c) set to 30 | `r2.R.c: scratch=30 committed=29`; 23 of 24; exit 1 |
| round 1's census section, `impostor_cooldown_zero_at_open` numerator raised by one, through the readings command | `DIFF r1 impostor_cooldown_zero_at_open: re-measured (85, 203), stated (84, 203)`; 244 of 245; exit 1 |

### 3.3 The readings, flag and re-projection proofs

`readings.py` and `reproject.py` are the card's blocks as extracted at `F`
(sha256 `9e22e40c…57abc` and `0cd632e0…6445c`), byte-equal to 1.13 and 1.14.
The readings proofs run on scratch copies of round 2's census section at `F`
with the route cells put in scope at 0 and presence 12, with round 2's honesty
file, and on the committed route JSON with its r2 column copied as r3:

| copy | command | result |
|---|---|---|
| unedited | `--column r3 --after --step` | exit 0; `step rule: names the era-keyed promotion of round 3 as the shown set, ... (Conf. misses 0; impostor wins 24/50; M 40 against round 2's 40)` |
| presence 0 | the same | exit 1; `Conf.: BREACH (no route line served: the route field reads absent)`, `Conf. misses: route field presence 0` |
| `route_lines_false_to_the_map` numerator 1 | the same | exit 1; `Conf. misses: route_lines_false_to_the_map` |
| `stale_report_meetings` numerator 1 | the same | exit 1; `Conf. misses: stale_report_meetings` |
| r3's M 41 | the same | exit 0; the step line names round 2 staying shown (M 41 against 40) |
| `impostor_wins` 31/50 | the same | exit 0; the step line names round 2 staying shown (31/50) |
| reporter numerator 60 (the flag forced on) | the same | exit 0; the flag reads `relative rate 37.5, flagged`; the `step rule:` line is byte-identical to the unedited run's (`cmp` equal) |
| `role_correct_ejections` numerator 10 | the same | exit 0; the `step rule:` line byte-identical to the unedited run's |
| k2 = 0, k1 = 1 | `--column r3 --after` | exit 0; `flagged, reporters alone` |
| the r2 column's M set to 39 | `--column r3 --after --step` | exit 1; `the route JSON's r2 column reads M 39, not 40` |
| round 2's section | `--column r2 --after --step` | exit 1; `--step reads round 3: pass --column r3 --after --step` |

**The flag on the three sets** (1.9). On round 1 and round 2 the readings
command prints `relative rate 17.0, not flagged` and `relative rate 10.6, not
flagged` under bar A; under bar B it prints `17.0, flagged` on round 1 and
`10.6, not flagged` on round 2; under bar C `not flagged (reporter rate
11/98)` and `not flagged (reporter rate 17/93)`. The baseline-9 column is
read from `d41c9006`'s `replays/samples/9p2i` bytes, extracted with
`git archive d41c9006 replays/samples/9p2i` into scratch and folded by the
census at `F` with `--set-dir` (exit 0; 50 games, 145 meetings; 7/75 against
2/243): bar A `relative rate 11.3, not flagged`, bar B `11.3, flagged`, bar C
`not flagged (reporter rate 7/75)`. Every reading in 1.9's table reproduces.

**The re-projection**, on a scratch copy of round 1's seeds 0-11 against
`replays/samples/9p2i`:

| copy and wall | result |
|---|---|
| unedited, 4,000 s | exit 0; calls 1,619 (401 / 372 x round 2), input 9,978,176, output 470,463, wall 16,667 s = 4.63 h |
| 50,000 output tokens added to one call of seed 0, 4,000 s | exit 1; output 677,314 (100.3% of the 675,000 stop) `STOP`, and `STOP: output` |
| unedited, 9,400 s | exit 1; wall 39,167 s = 10.88 h `STOP`, and `STOP: wall` |
| a copy of seed 0 as seed 77, which round 2 does not hold | exit 1; `every completed candidate seed must have round 2's seed beside it` |

### 3.4 The field's rehearsals, at `F`

The field card's rehearsals are its committed suites: the fake-provider
inertness and the scripted presence.

```
.venv/bin/pytest -q -n 6 tests/meetings/test_route_lines_arm.py tests/meetings/test_route_lines.py \
  tests/experiments/test_route_lines_replay.py
```

199 passed, exit 0. In `tests/meetings/test_route_lines_arm.py`, `-k
'fake_rehearsal or scripted or rehearsal_game or refuse'` selects 40, all
passed: among them
`test_the_fake_rehearsal_is_inert` (round 2's declared file and the same plus
the field record equal rows apart from the config key and the `vote_ballot`
stamp, and serve no block),
`test_the_scripted_rehearsal_serves_both_readings_and_no_step_for_the_left_out_change`,
`test_each_scripted_on_ballot_minus_its_block_is_its_off_twin_and_the_tally_holds`,
`test_every_rehearsal_game_verifies_and_reproduces_through_the_golden`, and the
perturbed halves `test_the_scripted_on_game_walked_without_the_field_fails_at_every_block`
and `test_the_manager_passing_no_lines_fails_the_scripted_on_golden`. CI at
`F`: run 37892577802 (`CI`, push, head `e4fc6cbf`), conclusion success, its
three jobs (project checks, frontend checks, frontend e2e) green.

### 3.5 The planted proofs at `F`

```
.venv/bin/pytest -q -n 6 tests/orchestrator/test_experiment_arms.py tests/orchestrator/test_experiment_config.py \
  tests/eval/test_gameplay_census.py tests/scripts/test_candidate_sets.py tests/meetings/test_ballot_arms.py \
  tests/_helpers/test_scripted_meeting.py tests/eval/test_recorded_arm_readers.py
```

921 passed, exit 0. Among them: the census card's planted breach per guarded
cell (`test_every_guarded_cell_has_a_planted_pair`) and its route conformance
breach, `test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter`,
with `test_every_route_line_cell_and_table_reads_n_a_without_the_setting`; the
record-plumbing card's planted round perturbations in
`tests/scripts/test_candidate_sets.py`; and the field card's refusals of 3.1.
The document gates at P, at Q and on the tree carrying this section: `scripts/verify_ml_evidence.py` offline,
exit 0 (64 checks: 52 OK, 0 FAIL, 7 ABSENT, 5 INFO; the in-tree family
inventory OK with the re-derived `audits/` row), `scripts/check_doc_facts.py`
exit 0, `scripts/validate_task_docs.py` exit 0 (102 work cards), and
`tests/scripts/test_verify_ml_evidence.py` with
`tests/scripts/test_check_doc_facts.py` (415 passed on the tree carrying this
section, among them
`test_audits_index_ladder_tip_drift_detected` and
`test_unindexed_audit_detected`).

### 3.6 The dry run, in the recording checkout at P

A worktree detached at P (`641b4254`), outside the repository's working tree,
with `uv sync --frozen` (exit 0), no `.env`, and an untracked copy of the
declared file at `replays/candidates/stage-b-r3/experiment-config.json` whose
`shasum -a 256` printed
`a788b9eba5e8f2f5d29033fece2d0dc0dbac7d3528ea93c7c7a93327dbc6d57d`. The
recording shell's exports (1.7), and nothing else (`env -i` with only `HOME`,
`PATH` and `TERM` beside them):

```
bash scripts/refresh_samples.sh --full --expect-levers "" \
  --experiment-config replays/candidates/stage-b-r3/experiment-config.json --dry-run
```

Exit 0, and its resolved configuration (the seed list, the model-coupling,
registry and lever-preflight lines, the per-seed stage lines and the full-mode
clean-up line elided; the run printed them):

```
[dry-run] Experiment config: replays/candidates/stage-b-r3/experiment-config.json (sha256 a788b9eba5e8f2f5d29033fece2d0dc0dbac7d3528ea93c7c7a93327dbc6d57d)
[dry-run] Experiment config settings: meeting_reset='hub_with_grace', vent_exit_policy='look_and_wait', bounded_rebuttal_version=1, vent_witness_rule='physical', vent_entry_policy='own_fresh_kill', report_body_handle_version=1, ballot_kill_row_version=1, impostor_ballot_version=1, kill_cooldown_ticks=6, route_lines_version=1
[dry-run] Experiment switch exports: none
[dry-run] mode: full
[dry-run] roster: num_players=9 num_impostors=2 tasks_per_crewmate=2
[dry-run] roster descriptor: would ensure replays/candidates/stage-b-r3/9p2i/roster.json = {num_players: 9, num_impostors: 2, tasks_per_crewmate: 2} (fails loud if an existing one disagrees)
[dry-run] sample dir: replays/candidates/stage-b-r3/9p2i
[dry-run] provider: featherless
[dry-run] preflight: would require FEATHERLESS_API_KEY (hosted run; $0 provider-keyed cost)
[dry-run] meeting model: Qwen/Qwen3.6-27B
[dry-run] prompt set: qwen3_6_27b
[dry-run] substrate flags: expected levers ON = (none — the bare slate: every live toggle OFF); every other live toggle OFF; the graduated levers unconditional ON
[dry-run] seed workers: 2 parallel (each records one seed, then pulls the next available seed from the queue; Featherless: 2 units per 32B request → 4-unit cap)
[dry-run] seed crash-retry: up to 8 attempt(s) per seed on a transport/crash error (recorded parse failures are non-fatal)
[dry-run] experiment config: would copy replays/candidates/stage-b-r3/experiment-config.json into the stage directory once, if it still reads sha256 a788b9eba5e8f2f5d29033fece2d0dc0dbac7d3528ea93c7c7a93327dbc6d57d, and pass that copy to every seed
[dry-run] manifest: replays/candidates/stage-b-r3/9p2i/MANIFEST.md
[dry-run] eval report: would rebuild replays/candidates/stage-b-r3/9p2i/tournament-eval-report.json.gz from the refreshed replays (scripts/build_sample_report.py; $0, no provider)
[dry-run] no API calls made; no files written.
Substrate slate OK: expected levers ON = (none — the bare slate: every live toggle OFF); every other live toggle OFF; the graduated levers unconditional ON.
```

The porcelain status read the same one line before and after the dry run, the
untracked declared copy (`?? replays/candidates/stage-b-r3/`), and with
untracked files hidden it read 0 lines before and after: the dry run wrote
nothing. Proof: the same dry run with a stray `AILIBI_BOUNDED_REBUTTAL=1`
exported exits 1 with "Refused: the environment exports
AILIBI_BOUNDED_REBUTTAL. A recording takes its experimental switches only from
a declared config file (--experiment-config), so unset these variables before
recording. Nothing was staged." The scratch checkout was removed afterwards;
the recording phase opens its own, fresh, at P.

### 3.7 The pre-registration gates

In this worktree at Q (`bb13fbc7`):

| gate | result |
|---|---|
| `git merge-base --is-ancestor e4fc6cbf 641b4254` (F before P); `git merge-base --is-ancestor 641b4254 bb13fbc7` (P before Q) | exit 0 each |
| proof: Q in place of P (`--is-ancestor bb13fbc7 641b4254`); P in place of F (`--is-ancestor 641b4254 e4fc6cbf`) | exit 1 each |
| `git diff --name-only e4fc6cbf 641b4254` | `audits/README.md`, `audits/audit-2026-10-09-stage-b-r3.md`, `docs/artifacts.md`: nothing else in P's tree differs from F's, and the config is not committed |
| `git diff --name-only 641b4254 bb13fbc7` | the audit (section 2 appended) and the `audits/` row of `docs/artifacts.md` re-derived for its length |
| section 1 at P (`git show 641b4254:audits/audit-2026-10-09-stage-b-r3.md`) against the head's | 951 lines each, 0 differing, exit 0. Proof: "0.30" edited to "0.31" in one reading of a scratch copy, 2 differing lines, exit 1 |
| committer dates | P 2026-10-09T02:42:03-04:00, Q 2026-10-09T02:43:47-04:00 |
| `git log --oneline e4fc6cbf..HEAD` and `e4fc6cbf..origin/main` over `engine agents meetings observation orchestrator eval api scripts llm experiments/lab/route_check_replay.py` | 0 commits each. Proof: the same pathspec over `76270d6c..e4fc6cbf` prints 12 commits |
| `git diff --stat e4fc6cbf..HEAD` over the nothing-moves paths (the sample and corpus sets, round 1's directory, `tests/fixtures`, `training`, `api`, `frontend`, `experiments`, `audits/tactical-gameplay` and the census and scorecard documents) | empty |

Q's committer date preceding the probe's start and every MANIFEST
`refreshed_at`, Q before the first `record:` checkpoint, and P against the
MANIFEST's one `git_sha` are checked by the recording phase, after its legs.

**`main` after `F`.** After P was written, `main` moved from `e4fc6cbf` to
`335cbdc9` by two document commits to the decision memo, which add its
section 8.9 (2026-10-09): the owner ruled "Merge both when verified and retire
the memo's D14 list", then, amending it, "Keep the comparison records". Memo
D14's list is retired by its own card, whose merge waits for this record's
merge; `replays/candidates/stage-b-r1/` stays; and a promotion of round 3
keeps round 2's bytes as `replays/candidates/stage-b-r2`. Nothing moved under
the frozen pathspec or the nothing-moves paths, so `main` was merged in
(`d1221611`), as the card's freeze rule says. Section 1 is unchanged: its
statement that nothing is retired on the strength of this record and that
round 1's directory stays holds under 8.9, and 8.9's note on round 2's bytes
is a follow-up for a promotion card, beside 1.12's list, not a change to the
table, the bar, the step rule or the config.

Memo 8.9 also delegates the merge: the promotion card's pull request, if the
orchestrator takes the step (8.8), is merged by the orchestrator once its
reviews pass, publishing through `.github/workflows/pages.yml` under the
owner's delegation. Where section 2 quotes memo 8.8 ("the merge still the
owner's because it publishes"), a promotion's merge is now the
orchestrator's under 8.9; section 2 stays as quoted, since it records the
words of that date, and this paragraph records the later ruling. (This
paragraph was added with the recording phase's delivery, after section 2.)

### 3.8 What the recording phase runs first

Before the probe, in the recording phase the orchestrator dispatches after
this phase is reviewed: the fake dress rehearsal of seeds 0-49 on the declared
config into scratch through every instrument (it runs the recorder, which this
phase ran only as the dry run); the scratch scripted game from the declared
config and the tactical lab rows against
`audits/tactical-gameplay/stage-b-r1-frozen-head.json`; a fresh recording
checkout at P with its own dry run; the key's programmatic copy and the
count-only key scan with each planted pattern; then the probe and its gates.

## 4. Before the probe: the rehearsals, the dry run, the pause and the key (2026-10-09)

The recording phase ran in three checkouts, as 1.4 sets them: a recording
worktree detached at P (`641b4254`) outside the repository's working tree,
with `uv sync --frozen`, no `.env` and an untracked copy of the declared file
at `replays/candidates/stage-b-r3/experiment-config.json`, which ran only the
recorder; a verification worktree detached at `F` (`e4fc6cbf`), with no copy
of the declared file, for the rehearsals and the planted suites; and this
branch's worktree for delivery, which received each checkpoint's bytes and
ran every gate in a bare shell (`env | grep -c '^AILIBI_'` printed 0 before
each). No provider was called before the probe. Every census and scan below
is count-only; no prompt, transcript text or seed-band prefix was printed.

### 4.1 The fake dress rehearsal, at `F`

Seeds 0-49 on the declared file, with `AILIBI_LLM_PROVIDER=fake`, into a
scratch directory outside the repository (four workers, `env -i` with only
the fake provider, the prompt set, the roster and the scratch targets exported): exit 0, 50 of 50 seeds in
19 s, `$0.0000`, 132 meetings, the report rebuilt, every MANIFEST row naming
`e4fc6cbf`. The same rehearsal on round 2's declared file: exit 0, 50 of 50,
19 s, `$0.0000`. Each instrument then exited 0 on the declared file's set:

| instrument | result |
|---|---|
| `validity_gate.py <dir> --require-zero-cost --expected-prompt-versions <the four pairs> --expected-experiment-config <declared file> --expected-seeds 0-49 --require-one-recording-sha` | exit 0; all ten checks PASS |
| `bash scripts/verify_samples.sh <dir>` | exit 0; "All 50 samples verified clean." |
| the golden's directory walk (`walk_directory`, a count-only runner) | exit 0; 50 seeds, 132 meetings, 1,652 prompts, 0 not reproduced, 0 miscounted meetings |
| `publish_gameplay_census.py --set-dir <dir> --json-stdout` | exit 0; the 20 Conf. cells `readings.py` names read 0; the cooldown cell 0/591 with writes at all three writers (round start 100, after a kill 227, at a regroup 264); the route cells in scope with `meetings_with_a_route_line` 0/132 and `ballots_carrying_route_lines` 0/826: a fake turn states no place, so no block is served |
| `publish_process_scorecard.py --set-dir <dir> --json-stdout` | exit 0 |
| `measure_baseline.py <dir> --honesty --json` | exit 0; no raise |
| `scan_recording_packets.py <dir>` | exit 0 |
| both route instruments with an `r3` column, on a throwaway commit of a scratch clone holding the fake set and the declared file at the round's paths (never pushed; the clone had no remote) | `route_check_replay` exit 0, r3 M 0; `route_lines_replay` exit 0, r3 in served mode with 0 ballots carrying a block and 0 lines served |

The fake tally reads `1652 6409973 94990 0.0` on the declared file and on
round 2's file alike, and the two sets' 2,433 replay rows are equal once the
config key and the `vote_ballot` stamp suffix are removed: the field is inert
where no place is stated, the inertness the field card proved. The route lines'
added input for planning stays the field card's projection on round-2 bytes
(1.5: 331,015 added input tokens, 9,518,895 in all), gating nothing.

`readings.py --after` was not run on the fake set (its presence check is for
the hosted round). One departure from the Validation's literal command:
`route_lines_replay` refuses an `r1` or `r2` column at any commit other than
the one the committed route-check JSON pins ("the route-check replay pins
other bytes for it"), so its `r1` and `r2` columns ran at that pinned commit,
`5877adb4`, whose set bytes are the same; the `route_check_replay` columns ran
at `F` as written.

**Proof:** the declared file's fake set gated against round 2's declared file
exits 1, failing `cost_and_provenance_exact` alone, with 50 lines naming the
recorded `route_lines_version` round 2's file lacks; round 2's fake set against
its own file exits 0.

### 4.2 The scripted rehearsal and the lab, at `F`

**The field is served.** The route-lines card's scripted game
(`tests/_helpers/scripted_routes.py`: its seed, placements and ejection),
recorded through `record_game` from the declared file as the declared file's
own loader reads it (`scripts/_declared_experiment.py`), into scratch:

| check | result |
|---|---|
| the recording | 2 meetings; the recorded config `a788b9eb…6d57d` |
| `verify_samples.sh <dir>` | "All 1 samples verified clean." |
| `validity_gate.py <dir> --require-zero-cost --expected-prompt-versions <the four pairs> --expected-experiment-config <declared file> --expected-seeds 0 --require-one-recording-sha` | exit 0; ten checks PASS |
| the golden's directory walk | 2 meetings, 26 prompts, 0 not reproduced, 0 miscounted meetings |
| census `--set-dir` | exit 0; every Conf. cell 0, `route_lines_false_to_the_map` 0/15 and `route_lines_off_the_table` 0/15; presence `meetings_with_a_route_line` 2/2, `ballots_carrying_route_lines` 12/13; lines per meeting 1 line 1, 2 lines 1; steps "walking fits" 2, "regroup between" 1; the cooldown cell written at all three writers (2, 4, 4) |
| scorecard, honesty and the packet scan | exit 0 each |

**Proof:** the golden's walk over the same game with the recorded evidence
profile dropped (the module's `profile_from_config` replaced by an empty
`MeetingEvidenceProfile`) leaves 13 of 26 prompts not reproduced and 2 meetings
miscounted: the ballots render without their route block, so the recorded
calls go unconsumed.

**The cases at `F`.** In the verification worktree (no declared copy there):

```
.venv/bin/pytest -q -n 6 tests/meetings/test_route_lines_arm.py tests/meetings/test_route_lines.py \
  tests/experiments/test_route_lines_replay.py tests/_helpers/test_scripted_meeting.py \
  tests/meetings/test_ballot_arms.py tests/eval/test_recorded_arm_readers.py
```

457 passed, exit 0: the field card's planted cases and rehearsals and round
2's scripted and ballot-arm cases. By name, among them:
`test_the_fake_rehearsal_is_inert`,
`test_the_scripted_rehearsal_serves_both_readings_and_no_step_for_the_left_out_change`,
`test_the_scripted_on_game_walked_without_the_field_fails_at_every_block` and
`test_the_manager_passing_no_lines_fails_the_scripted_on_golden`. The golden's
scripted cases, `-k "scripted or dropping or kill_row_gate or retired_guard_pins"`:
4 passed (`test_the_scripted_rebuttal_game_re_renders_byte_equal`, whose
perturbed half drops the recorded profile,
`test_dropping_the_recorded_reset_fails_the_meeting_post_hash`,
`test_the_kill_row_gate_forced_on_fails_the_golden_at_the_kill_holders` and
`test_the_retired_guard_pins_are_keyed_by_the_path_under_replays`).

**The lab.** The ten round-1 arms on `--split development`, written to
scratch:

```
.venv/bin/python -m experiments.tactical_gameplay --split development --arms baseline vent_risk \
  vent_physical vent_look_and_wait vent_own_fresh_kill stage_b_full stage_b_full_minus_look_and_wait \
  stage_b_full_minus_own_fresh_kill stage_b_full_minus_physical stage_b_full_minus_hub_with_grace \
  --output <scratch>/lab-F.json
```

Exit 0 (36 s). Against `audits/tactical-gameplay/stage-b-r1-frozen-head.json`,
rows matched by (arm, roster, seed) on the frozen file's own keys: 10 arms,
160 rows, 14 top-level keys per row, `counts` compared on the frozen row's
count keys, 13,622 fields compared, 0 differing. **Proof:** a scratch copy with
one counter edited (`stage_b_full`, 9p2i seed 1000, `applied:IMPOSTOR:kill` 5
to 6) prints that one field and exits 1. The field touches no tactical code.
The field card's lab rows reproduce by its own command:
`route_lines_replay --check` and `route_check_replay --check` at `F`, each
"reproduced".

### 4.3 The dry run, the pause and the key

**The dry run**, in the recording checkout at P (`641b4254`), under `env -i`
with only `HOME`, `PATH`, `TERM` and the recording shell's exports (1.7):
exit 0, echoing `Experiment config: replays/candidates/stage-b-r3/experiment-config.json
(sha256 a788b9eb…6d57d)`, the ten settings (`meeting_reset='hub_with_grace'`
to `route_lines_version=1`), `Experiment switch exports: none`, provider
featherless, model `Qwen/Qwen3.6-27B`, prompt set `qwen3_6_27b`, the bare
slate, 2 workers and 8 attempts; `git status --porcelain
--untracked-files=no` read 0 lines before and after. **Proof:** the same dry
run with a stray `AILIBI_BOUNDED_REBUTTAL=1` exits 1: "Refused: the
environment exports AILIBI_BOUNDED_REBUTTAL. ... Nothing was staged."

**The pause.** The leg runner checks the pause file
(`.../scratchpad/stage-b-record-r3/PAUSE`, outside the repository) before
every leg, refuses a seed already on disk, checks the recording checkout's
head is P with no tracked change and checks the declared copy's sha256.
**Proof:** with a planted pause file and the recorder replaced by `true`, the
runner exits 3, starts nothing and logs "PAUSE file present before leg
pause-proof-batch-2-6 (seeds 2,3,4,5,6): no leg started"; with the file
removed it runs `true` and exits 0. The pause file did not exist at any later
leg.

**The key.** `FEATHERLESS_API_KEY` lives only in the main checkout's untracked
`.env`. Its one line was copied by a `grep` whose output went straight to a
mode-0600 file in a mode-0700 directory outside every checkout, never printed:
a count-only `grep -c` found 1 matching line in the source, and the copy holds
1 line with a non-empty value. Every live leg ran `uv run --env-file <that
file> bash scripts/refresh_samples.sh ...`; the recorder's run logs, which
carry the key's first eight characters, stayed outside the repository. The
scan (`keyscan.py`, count-only, gzip decompressed) counts seven patterns over
every file changed since `F` (committed, staged or untracked): the exact value,
its first eight characters, and five generic shapes (a key assignment, a bearer
token, two secret-key prefixes and an API-key field). **Proof:** one plant per
pattern, written inside the key's mode-0700 directory and scanned alone, fires
its own pattern and exits 1 (the gzip-compressed exact-value plant also fires
the prefix and one generic shape); the plants were deleted (0 left).

## 5. The probe (2026-10-09)

### 5.1 Seeds 0-1

The sitting's 18 h window opened with the probe's first seed at
2026-10-09T07:59:44Z, after Q (committed 2026-10-09T02:43:47-04:00, that is
06:43:47Z); it closes at 2026-10-10T01:59:44Z. Seeds 0-1 recorded as one leg
on the leg's two workers in the recording checkout at P:

```
<the 1.7 exports> uv run --env-file <key file> bash scripts/refresh_samples.sh \
  --seeds 0,1 --expect-levers "" --experiment-config replays/candidates/stage-b-r3/experiment-config.json
```

It exited 0 at 08:10:17Z: "Refresh complete in 10m31s" (631 s), seed 0 in
630 s and seed 1 in 209 s, `$0.0000`, no retry, no `WARN` and no `ERROR` line.
Leg: 63 calls, 419,109 input, 18,430 output.

### 5.2 The probe's gates

In the delivery checkout on its copy of seeds 0-1, bare shell, the declared
copy re-checked (`a788b9eb…6d57d`):

| gate | result |
|---|---|
| `validity_gate.py <dir> --expected-model Qwen/Qwen3.6-27B --require-zero-cost --expected-prompt-versions <the four pairs> --expected-experiment-config <declared file> --expected-seeds 0-1 --require-one-recording-sha` | exit 0; all ten checks PASS |
| `bash scripts/verify_samples.sh <dir>` | exit 0; "All 2 samples verified clean." |
| the golden's directory walk | exit 0; 5 meetings, 63 prompts, 0 not reproduced, 0 miscounted meetings |
| census `--set-dir <dir> --json-stdout` | exit 0; the 20 Conf. cells 0; the cooldown cell written at all three writers (4, 9, 7); the route field served in 5 of 5 meetings and on 28 of 29 ballots |
| scorecard, `measure_baseline.py --honesty` (no raise) and `scan_recording_packets.py` | exit 0 each |
| `grep -l deadline_default` | 0 files |
| MANIFEST | one `git_sha`, `641b4254` (P) |
| the key scan | 0 over the 11 files changed since `F` |

Seeds 0-1 held meetings and served route lines, so the probe did not extend,
and the batches ran the first list of 1.7. The counts of two games are no
reading and none is drawn here.

### 5.3 The re-projection after the probe

By 1.5's rule over round 2's seeds 0-1 (85 calls, 546,811 input, 23,202
output): calls 63 / 85 x 1,502 = 1,113 (44.2% of the 2,520 stop), input
7,042,147 (44.7%), output 332,244 (49.2%), wall 631 s / 2 x 50 = 15,775 s =
4.38 h against the 10.8 h stop; every `cost_usd` 0.0. Every figure was inside
its stop. The probe's projected wall is 4.38 h, so 1.5 times it is 6.57 h
(23,663 s): unlike rounds 1 and 2, that line binds before the 10.8 h stop, and
the summed wall and every later projection stayed below it (6.3).

The probe was checkpointed as `a09065cc` after a count-only key scan.

## 6. The batches (2026-10-09, one sitting)

### 6.1 The legs

Each batch was `uv run --env-file <key file> bash scripts/refresh_samples.sh
--seeds <the batch> --expect-levers "" --experiment-config
replays/candidates/stage-b-r3/experiment-config.json` with the 1.7 exports,
in the recording checkout still detached at P; the leg runner checked the
pause file, the declared copy's sha256, the checkout's head and the seeds on
disk before every leg. Wall is the recorder's own "Refresh complete in"
figure; calls and tokens are the tally of the leg's seeds as committed. No
leg ran pytest or `check.sh` in the recording checkout, and no commit was made
there.

| leg | seeds | UTC | recording wall | calls | input | output | checkpoint |
|---|---|---|---|---|---|---|---|
| probe | 0-1 | 07:59:44-08:10:17 | 631 s | 63 | 419,109 | 18,430 | `a09065cc` |
| batch 1 | 2-6 | 08:11:40-08:27:16 | 935 s | 135 | 856,894 | 38,630 | `3800a6ce` |
| batch 2 | 7-11 | 08:28:15-08:49:55 | 1,298 s | 160 | 972,451 | 41,224 | `d4ce0c6b` |
| batch 3 | 12-16 | 08:51:14-09:06:51 | 934 s | 134 | 846,395 | 39,173 | `99950ebd` |
| batch 4 | 17-21 | 09:07:42-09:33:29 | 1,544 s | 195 | 1,231,754 | 53,588 | `0d450119` |
| batch 5 | 22-26 | 09:34:54-09:56:17 | 1,280 s | 154 | 1,002,275 | 45,886 | `d03a1a9d` |
| batch 6 | 27-31 | 09:57:15-10:16:40 | 1,160 s | 134 | 832,796 | 36,848 | `48bdccbf` |
| batch 7 | 32-36 | 10:18:25-10:36:47 | 1,098 s | 147 | 955,709 | 42,050 | `ddf45f4d` |
| batch 8 | 37-41 | 10:37:45-10:56:03 | 1,094 s | 148 | 932,599 | 42,217 | `152c9bd0` |
| batch 9 | 42-46 | 10:57:23-11:17:30 | 1,203 s | 143 | 893,354 | 37,920 | `502e70a8` |
| batch 10 | 47-49 | 11:18:36-11:32:31 | 831 s | 110 | 709,970 | 30,150 | `97b68014` |
| **the round** | 0-49 | | **12,008 s** | **1,523** | **9,653,306** | **426,116** | |

After every batch, in the delivery checkout and a bare shell: the copy from
the recording checkout (no committed seed file moved: `git diff --name-only
HEAD` over the set listed only the MANIFEST and the report), the tally, the
re-projection and the count-only key scan (0 at every push), then a pushed
`record:` checkpoint carrying the set and the re-derived candidates row of
`docs/artifacts.md` (offline `verify_ml_evidence.py` exit 0 at every
checkpoint: 52 OK, 0 FAIL, 7 ABSENT, 5 INFO). After the probe and after every
second batch (batches 2, 4, 6, 8 and 10), before that checkpoint, the full
gate set on seeds `0-N`, each run exiting 0:

| checkpoint | gate (ten checks) | verify | golden walk (prompts) | Conf. cells | cooldown writes (start, kill, regroup) | route presence (meetings; ballots) |
|---|---|---|---|---|---|---|
| probe, 0-1 | PASS | 2 clean | 63, 0 not reproduced | 20 at 0 | 4, 9, 7 | 5/5; 28/29 |
| batch 2, 0-11 | PASS | 12 clean | 358, 0 | 20 at 0 | 24, 46, 28 | 28/28; 160/165 |
| batch 4, 0-21 | PASS | 22 clean | 687, 0 | 20 at 0 | 44, 86, 57 | 55/55; 305/316 |
| batch 6, 0-31 | PASS | 32 clean | 975, 0 | 20 at 0 | 64, 124, 92 | 75/77; 427/449 |
| batch 8, 0-41 | PASS | 42 clean | 1,270, 0 | 20 at 0 | 84, 165, 126 | 98/100; 559/585 |
| batch 10, 0-49 | PASS | 50 clean | 1,523, 0 | 20 at 0 | 100, 192, 150 | 117/119; 671/702 |

At each of them the scorecard fold, `measure_baseline.py --honesty` (no raise)
and `scan_recording_packets.py` exited 0, `grep -l deadline_default` counted
0, and the MANIFEST named the one sha `641b4254`.

### 6.2 Events

1. **No failed seed.** No seed holds a `(deadline_default)` row or any
   `failed_call` row, so the failed-seed rule never fired and no seed was
   re-recorded; there is no husk.
2. **No retry, no stall.** No leg log carries a `WARN` or `ERROR` line: no
   seed needed a second attempt. No leg went 45 minutes without a completed
   seed (the longest seed, 9, took 787 s).
3. **No pause.** The pause file was absent before every leg; the sitting ran
   whole.
4. **No stop fired.** Every `cost_usd` is `0.0000`; no re-projection came near
   a stop (6.3); the summed wall stayed below 1.5 times the probe's projected
   wall.
5. **`main` moved, outside the freeze.** During the sitting `main` gained
   three document commits under `tasks/` (to `9775c9d6`: the finish-wave cards,
   the extractor card's closure, and the memo's closure and the orchestrator's
   default for the frozen before column). Nothing moved under the frozen
   pathspec or the nothing-moves paths, so `main` was merged in after the last
   seed (`7bdb490d`) and the gates re-ran at the merged head (7.1).
6. **A stop at delivery, after the last seed.** Once the declared config
   entered the tree, one test of the route-lines card turned red only because
   the round exists (7.5). The card names that a stop; it touches no recorded
   byte and no reading, and it is left open for the orchestrator.

### 6.3 The re-projection at every checkpoint

By 1.5's rule; each figure is the projected round total and its share of the
90% stop. The pre-registered 10-seed re-projection is the first checkpoint
holding at least 10 seeds, seeds 0-11.

| checkpoint | seeds | calls | input | output | summed wall | projected wall |
|---|---|---|---|---|---|---|
| the probe | 0-1 | 1,113 (44.2%) | 7,042,147 (44.7%) | 332,244 (49.2%) | 631 s | 4.38 h |
| batch 1 | 0-6 | 1,352 (53.6%) | 8,503,133 (54.0%) | 383,533 (56.8%) | 1,566 s | 3.11 h |
| **batch 2, the 10-seed re-projection** | 0-11 | 1,445 (57.4%) | 9,098,115 (57.8%) | 406,604 (60.2%) | 2,864 s | 3.31 h |
| batch 3 | 0-16 | 1,472 (58.4%) | 9,354,439 (59.4%) | 421,570 (62.5%) | 3,798 s | 3.10 h |
| batch 4 | 0-21 | 1,540 (61.1%) | 9,758,530 (62.0%) | 435,070 (64.5%) | 5,342 s | 3.37 h |
| batch 5 | 0-26 | 1,518 (60.2%) | 9,650,156 (61.3%) | 430,132 (63.7%) | 6,622 s | 3.41 h |
| batch 6 | 0-31 | 1,546 (61.4%) | 9,835,070 (62.4%) | 434,385 (64.4%) | 7,782 s | 3.38 h |
| batch 7 | 0-36 | 1,543 (61.2%) | 9,819,117 (62.3%) | 433,499 (64.2%) | 8,880 s | 3.33 h |
| batch 8 | 0-41 | 1,508 (59.8%) | 9,569,876 (60.8%) | 424,789 (62.9%) | 9,974 s | 3.30 h |
| batch 9 | 0-46 | 1,539 (61.1%) | 9,766,450 (62.0%) | 429,027 (63.6%) | 11,177 s | 3.30 h |
| batch 10 | 0-49 | 1,523 (60.4%) | 9,653,306 (61.3%) | 426,116 (63.1%) | 12,008 s | 3.34 h |

For context only: over all 50 seeds the round ran 1.014x round 2's calls,
1.051x its input and 1.019x its output, and 0.979x, 1.033x and 0.983x round
1's.

## 7. The round's gates, and its spend

### 7.1 The gates on the whole round

In the delivery checkout, bare shell, at `45d28b68` (the declared config
committed with P's sha256, the golden's pin row, `main` merged and the
candidate sentence; no recorded byte changed after the last checkpoint):

| gate | result |
|---|---|
| `validity_gate.py <round> --expected-model Qwen/Qwen3.6-27B --require-zero-cost --expected-prompt-versions <the four pairs> --expected-experiment-config <declared file> --expected-seeds 0-49 --require-one-recording-sha` | exit 0, ten checks PASS: `all_games_reach_game_over` (50/50), `meeting_rate_and_resolution` (1.0; 119 resolved, 0 unresolved), `no_duplicate_meeting_rows` (0 of 119), `no_tick_1_kills` (0), `no_friendly_fire_kills` (0), `no_betrayal_ballots_or_accusations` (0 of 702), `no_railroaded_crew_ejections` (0 of 2,397), `no_dangling_primary_reason_id` (0 of 702), `cost_and_provenance_exact` (one model, four prompt versions, the declared config, seeds 0-49, one sha), `byte_identical_reconstruction` (0 drifted) |
| proof: the same gate with `--expected-seeds 0-50` | exit 1: `cost_and_provenance_exact` alone, "missing [50]" for the replay files and the MANIFEST rows |
| proof: round 2 (`replays/samples/9p2i`) against this round's declared file | exit 1: `cost_and_provenance_exact`, 50 lines naming the `route_lines_version` round 2 did not record |
| `bash scripts/verify_samples.sh` (bare), then once per set directory | bare: exit 0, four sets clean (the two sample sets and rounds 1 and 3); `samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i` (150), `ml_corpus/4p1i`, round 1 and this round: each exit 0, all clean |
| `build_sample_report.py --sample-dir <dir> --check`, each of the six | exit 0 each; this round's report gz is the recorder's post-step rebuild through `eval/report_io.py` |
| the golden's directory walk | exit 0: 50 seeds, 119 meetings, 1,523 prompts, 0 not reproduced, 0 miscounted meetings; retired-guard census (119, 702, 0, 0), the pin row added (7.3) |
| census `--set-dir <round> --json-stdout` | exit 0: every Conf. cell reads 0, the route cells included (8.2, 8.3) |
| scorecard `--set-dir <round> --json-stdout` | exit 0 |
| `measure_baseline.py <round> --honesty --json` | exit 0; no raise |
| `scan_recording_packets.py <round>` | exit 0 (50 games, 13,021 packets) |
| `grep -l deadline_default` over the 50 replays; `failed_call` rows | 0 files; 0 rows |
| MANIFEST columns | 50 rows, seeds 0-49, one value in every column but the seed and the winner: model `Qwen/Qwen3.6-27B`, the four prompt versions, policy `fsm-default`, `refreshed_at` 2026-10-09, `git_sha` `641b4254`, cost `0.0000`; the flags column equals round 2's (one value on every row of each) |
| proof: the round pooled through the census (`fold_set` then `pool`) with round 2, and with round 1 | it folds alone; pooled, `GameplayCensusEraError`, "two eras differ in settings; the census never pools across eras", both times |
| `git merge-base --is-ancestor 641b4254 641b4254` (P against the MANIFEST's one sha); F before P; P before Q; Q before the first `record:` checkpoint (`a09065cc`) | exit 0 each. Proof: the head in place of P, exit 1 |
| Q's committer date (2026-10-09T06:43:47Z) against the probe's start in the operator log (07:59:44Z) and every MANIFEST `refreshed_at` (a UTC date, 2026-10-09 on all 50 rows) | the probe after Q, 0 rows before Q's date, exit 0. Proofs: a scratch MANIFEST with seed 7's `refreshed_at` set to 2026-10-08 exits 1 (1 row before); a probe start of 06:40:00Z exits 1 |
| the pre-registration section at P against the head | sections 1 and 2 unchanged since P and Q (7.4) |
| `route_check_replay --check`; `route_lines_replay --check` | exit 0 each, "reproduced": the committed outputs did not move |
| `publish_process_scorecard.py --check`; `publish_gameplay_census.py --check` | exit 0 each |

### 7.2 The spend against the ceilings

| limit | spent | ceiling | share | 90% stop |
|---|---|---|---|---|
| model calls | 1,523 | 2,800 | 54.4% | 2,520 |
| input tokens | 9,653,306 | 17,500,000 | 55.2% | 15,750,000 |
| output tokens | 426,116 | 750,000 | 56.8% | 675,000 |
| recording wall | 12,008 s (3.34 h), summed over the eleven legs | 12 h | 27.8% | 10.8 h |
| marginal cost | $0.0000 | $0.00 | | any non-zero |

There is no husk, so the set's tally, `1523 9653306 426116 0.0`, is the whole
spend. The round ran in one sitting: its 18 h window opened at 07:59:44Z and
the last seed finished at 11:32:31Z, 3 h 32 min 47 s into it. The round held
119 meetings against round 2's 117 and round 1's 124 on the same seeds, at
12.80 calls and 81,120 input tokens per meeting (round 2: 12.84 and 78,529).
Its input ran 465,426 tokens above round 2's 9,187,880; the field card's
planning projection was 331,015 added input on round 2's bytes, and the
route-lines instrument reads the served blocks' share of round 3's own ballot
input as 340,488 tokens (a share of prompt characters, not a tokenizer count).

### 7.3 The derived views and the registration

- The round's eval report is the recorder's post-step rebuild through
  `eval/report_io.py` at every leg, and `build_sample_report.py --sample-dir
  replays/candidates/stage-b-r3/9p2i --check` exits 0. No derived byte was
  typed.
- The round README (`replays/candidates/stage-b-r3/README.md`) holds the
  `candidate-declaration` block: the sha256 line
  `a788b9eb…6d57d  experiment-config.json` and `9p2i seeds 0-49`. The
  declared config entered the tree only after the last seed, in the delivery
  commit `f35ff99c`, byte-equal to the untracked copy every checkout checked;
  with both in place the candidate test's shape check reads 0 problems for each
  round and for the family.
- The two `docs/artifacts.md` rows are re-derived with `git ls-files`: the
  `replays/candidates/` row reads 72 MB / 111 files (the round's 55 files
  beside round 1's 55 and the family README), and the `audits/` row its tracked bytes at the commit that
  carries this section; offline `verify_ml_evidence.py` reads OK (never
  `--complete`).
- The golden's `_RETIRED_GUARD_PINS` row `candidates/stage-b-r3/9p2i` is
  (119, 702, 0, 0), the production walk's census on the round. **Proof:**
  without it, `test_every_reconstruction_divergence_is_a_retired_guard[candidates/stage-b-r3/9p2i]`
  raises `KeyError: 'no retired-guard pin for candidates/stage-b-r3/9p2i'` and
  `test_the_retired_guard_pins_are_keyed_by_the_path_under_replays` fails (2
  failed, 10 passed under `-k "retired_guard or stage-b-r3"`); with it, 12
  passed.

### 7.4 Nothing publishes, the freeze held, and the key

- `git log --oneline e4fc6cbf..HEAD` and `e4fc6cbf..origin/main` print 0
  commits over `engine agents meetings observation orchestrator eval api
  scripts llm experiments/lab/route_check_replay.py` (`main` is at
  `9775c9d6`, merged in). Proof: the same pathspec over `76270d6c..e4fc6cbf`
  prints 12 commits.
- `git diff --stat e4fc6cbf..HEAD` is empty over `replays/samples`,
  `replays/ml_corpus`, round 1's directory, `tests/fixtures`, `training`,
  `api`, `frontend`, `experiments`, `audits/tactical-gameplay` and the census
  and scorecard documents.
- The demo bundle built at `F` (the verification worktree) and at the head,
  each with the sample replays' mtimes pinned to one instant (the loader takes
  `created_at` from the file mtime), holds 110 files each, and `diff -r` exits
  0.
- Sections 1 and 2 are unchanged: section 1 at P (`git show
  641b4254:audits/audit-2026-10-09-stage-b-r3.md`) equals the head's, and
  section 2 at Q equals the head's, line for line. Sections 4 to 10 and the
  last paragraph of 3.7 are the only audit text added by the recording phase.
- The key scan read 0 at every push, over every file changed since `F`. The
  key file stayed mode 0600 outside every checkout until the last push, so that
  push's scan could count the exact value, and was deleted right after it; the
  card's Results record when.

### 7.5 The stop: one test the round turns red

At the delivery head the project's test tier is red in one case, and only
because the round exists. CI run 37924867474 (`CI`, pull_request, head
`45d28b68`): Project checks failed with 1 failed, 10,850 passed, 40 skipped
and 3 xfailed; Frontend checks and Frontend e2e passed. The case is the
route-lines card's
`tests/meetings/test_route_lines_arm.py::test_every_committed_payload_reads_the_field_off`,
which asserts that no committed payload, no `experiment-config.json` under
`replays/` and none of the sets it lists reads `route_lines_version` ON. Its
helper walks every `replays/**/experiment-config.json`, so it now finds
`replays/candidates/stage-b-r3/experiment-config.json`, the round's declared
config, which reads the field ON by design (1.3); it finds nothing else, since
the round's replays are outside the payload files and sets it lists. The same
case fails locally, and it is the only one: the targeted suites
(`tests/scripts/test_candidate_sets.py`, `tests/eval/test_gameplay_census.py`,
the route-lines arm, field and instrument suites, and the arms and config
suites) read 1 failed, 861 passed; `pytest -m campaign` 337 passed; the
golden's cases 12 passed.

The card names this a stop ("Stop and ask ... if a test besides the golden pin
turns red only because another round exists"), its scope allows one test edit
(the golden's pin row, 7.3), and the failing file is the route-lines card's
under the one-writer map. So this record does not edit it: the pull request
stays a draft, and there is no green CI run at the head to cite as the gate
record. Nothing recorded is touched by it: the bytes, the gates of 7.1 and the
readings of section 8 stand, and the step rule (8.7) reads no test. Who edits
the case, and how, is the question this record leaves open before it can merge
(the card's Results and the pull request carry it).

## 8. The assessment

The round-3 column is this round alone, computed only from 1.12's named
sources and never pooled with another column: the census and scorecard
`--set-dir replays/candidates/stage-b-r3/9p2i --json-stdout`,
`measure_baseline.py replays/candidates/stage-b-r3/9p2i --honesty --json`, the
validity gate's `no_betrayal_ballots_or_accusations`, and the route-check
replay run at the delivery head `45d28b68` with r1 and r2 at `F` and r3 at the
head, into scratch. Each reading is what 1.13's command, unchanged (sha256
`9e22e40c…57abc`), prints:

```
python3 readings.py census-stage-b-r1.json honesty-stage-b-r1.json route.json --column r1 --after     # exit 0
python3 readings.py census-samples-9p2i.json honesty-samples-9p2i.json route.json --column r2 --after  # exit 0
python3 readings.py census-stage-b-r3.json honesty-stage-b-r3.json route.json --column r3 \
  --bar A --after --step                                                                                # exit 0
```

Rates carry Wilson 95% intervals. Rounds 2 and 3 differ in one key, but each
is a single hosted recording of 50 games, so a difference between them is the
field's only within hosted-generation noise; the Conf. cells and the scripted,
fake and lab rows (4.1, 4.2) attribute a mechanism. Rounds 1 and 2 read exactly
as 1.8 states them.

### 8.1 The process cells

The scorecard's rows. They move with the game, and none is a gate.

| row | round 1 | round 2 | round 3 |
|---|---|---|---|
| games; meetings; ballots (EJECT, SKIP) | 50; 124; 717 (387, 330) | 50; 117; 691 (410, 281) | 50; 119; 702 (397, 305) |
| 1 grounded decisions, EJECT | 384/387 = 0.992 (0.98-1.00) | 407/410 = 0.993 (0.98-1.00) | 394/397 = 0.992 (0.98-1.00) |
| 1 grounded decisions, SKIP | 54/330 = 0.164 (0.13-0.21) | 44/281 = 0.157 (0.12-0.20) | 47/305 = 0.154 (0.12-0.20) |
| 1 grounded decisions, all ballots | 438/717 = 0.611 (0.57-0.65) | 451/691 = 0.653 (0.62-0.69) | 441/702 = 0.628 (0.59-0.66) |
| 2 EJECTs deviating from the voter's own suspicion argmax | 67/275 = 0.244 | 65/292 = 0.223 | 56/291 = 0.192 |
| 2 role-correct, followers vs deviators (chance) | 200/208 vs 5/67 (0.327) | 215/227 vs 4/65 (0.340) | 215/235 vs 2/56 (0.328) |
| 3 manufactured contradiction | 0/22, 22 not evaluable | 1/15, 14 not evaluable | 0/15, 15 not evaluable |
| 4 unexplained decisions | 7/717 = 0.010 (0.00-0.02) | 11/691 = 0.016 (0.01-0.03) | 6/702 = 0.009 (0.00-0.02) |
| 5 evidence-quality mix over ejections (contradiction flag, first hand, hearsay, vent flag) | 2, 27, 1, 24 (of 54) | 2, 39, 1, 24 (of 66) | 1, 35, 1, 24 (of 61) |
| 6 rationale faithfulness (tokens) | 588/588 (129 not evaluable) | 580/580 (111 not evaluable) | 583/583 (119 not evaluable) |
| 7 agent-authored share | 701/717 = 0.978 (teammate coerced 16) | 674/691 = 0.975 (invalid target 1, teammate coerced 16) | 692/702 = 0.986 (teammate coerced 10) |
| 8 wrong-but-believable, reported and never penalised | 178/387 = 0.460 | 189/410 = 0.461 | 177/397 = 0.446 |
| 9 role-correct ejection, reported and never a gate | 39/54 = 0.722 (0.59-0.82) | 44/66 = 0.667 (0.55-0.77) | 46/61 = 0.754 (0.63-0.84) |

### 8.2 Each Conf. cell, and each carried reading

**Every Conf. cell reads 0 as built**, the cooldown and route cells included.
The census exits non-zero on any breach; it exited 0 on the round, and the
readings command with `--after` exited 0 with no Conf. miss.

| arm | Conf. cell | round 1 | round 2 | round 3 |
|---|---|---|---|---|
| physical witness | `vent_exits_seen_only_from_room_left` | 0/72 | 0/72 | **0/70** |
| physical witness | `vent_band_resting_only_on_room_left` | 0/24 | 0/24 | **0/24** |
| look and wait | `surfacings_before_cap_in_view` | 0/72 | 0/72 | **0/70** |
| look and wait | `trips_longer_than_cap` | 0/63 | 0/66 | **0/70** |
| own fresh kill | `vent_entries_not_after_own_fresh_kill` | 0/142 | 0/140 | **0/140** |
| full reset | `stale_report_meetings` | 0/118 | 0/114 | **0/115** |
| full reset | `report_corpses_older_than_last_close` | 0/68 | 0/64 | **0/65** |
| full reset | `play_resumes_with_impostor_in_vent` | 0/110 | 0/102 | **0/104** |
| full reset | `play_resumes_with_corpse` | 0/110 | 0/102 | **0/104** |
| full reset | `kills_in_grace_window_after_regroup` (T+1 to T+6) | 0/139 | 0/109 | **0/106** |
| full reset | `prompts_missing_a_regroup_notice` | 0/782 | 0/722 | **0/745** |
| one reply | `rebuttals_differing_from_selector` | 0/121 | 0/117 | **0/119** |
| one reply | `meetings_with_second_repeat_speaker` | 0/124 | 0/117 | **0/119** |
| body handle | `report_openings_with_kill_tick_handle` | 0/118 | 0/114 | **0/115** |
| kill row | `own_kill_rows_breaching` | 0/4 | 0/23 | **0/22** |
| impostor ballot | `recorded_teammate_ballot_targets` | 0/203 | 0/200 | **0/198** |
| impostor ballot | the gate's `no_betrayal_ballots_or_accusations` | 0 of 717 | 0 of 691 | **0 of 702** |
| self-report off | `impostor_openers` | 0/124 | 0/117 | **0/119** |
| kill cooldown | `kill_cooldowns_differing_from_recorded` | 0/487 against 4 | 0/447 against 6 | **0/442 against 6** |
| route lines | `route_lines_false_to_the_map`; `route_lines_off_the_table` | n/a | n/a | **0/7,956 steps; 0/2,416 lines** |

**Look and wait.** Exits seen from the exit room: 8/72, 8/72 and **7/70 =
0.100 (0.05-0.19)**. By round 2's rule (0.30 or below) the reading is
**effective**. Beside it: exits into a room the impostor could see a crewmate
in, 0/72, 0/72 and 0/70.

**One reply.** Opener rebuttals answering the charged tick: 19/19 (82 not
evaluable), 17/18 (69) and **20/20 = 1.000 (0.84-1.00), 70 not evaluable**;
rebuttals that only redirect: 17/121, 27/117 and **25/119 = 0.210
(0.15-0.29)**. By round 2's rule (half or more answer; redirect-only below
half) the reading is **effective**, resting on the 20 evaluable of 90 opener
rebuttals.

**Kill row.** Conf. cell 0/22. Presence: **present**, 22 own-kill rows served
(round 1: 4; round 2: 23).

**Impostor ballot.** Impostor EJECTs whose only citation is a neutral row
(honesty cell 3): 0/107, 0/111 and **0/101 = 0.000 (0.00-0.04)**. By round 2's
rule (0.10 or below), **the wording holds**.

**The carried cells.** As the owner confirmed (1.10):
- false resume perceptions are carried by the one resume helper
  (`compose_resume_events`) and the golden's byte-equal re-render of every
  recorded prompt: 1,523 of 1,523 reproduced, 0 meetings miscounted;
- the regroup notice is the Conf. cell `prompts_missing_a_regroup_notice`,
  0/745 above;
- ballots citing a rebuttal: the turn citation is the cell,
  `ballots_citing_a_rebuttal` 70/707, 57/691 and **67/702 = 0.095
  (0.08-0.12)**, with the counter slot beside it,
  `ballots_countering_with_a_rebuttal` 150/707, 175/691 and **158/702**;
- holds-nothing SKIPs: `skips_holding_nothing` 256/330, 214/281 and
  **235/305 = 0.770 (0.72-0.81)**; of them, `holds_nothing_skips_naming_no_candidate`
  0/256, 0/214 and **0/235** (8.8).

### 8.3 The route cells

Round 3's own field, read on its own cells (out of scope on rounds 1 and 2,
which did not record it):

| cell | round 3 |
|---|---|
| `route_lines_false_to_the_map` (Conf.) | **0/7,956** steps served |
| `route_lines_off_the_table` (Conf.) | **0/2,416** lines served |
| presence `meetings_with_a_route_line` | **117/119 = 0.983 (0.94-1.00)**: present |
| `ballots_carrying_route_lines` | 671/702 = 0.956 (0.94-0.97) |
| table `route_lines_per_meeting` | no line 2, one line 21, two lines 19, three or more 77 |
| table `route_steps_by_reading` | "walking fits" 1,421, "regroup between" 29 |

Both Conf. cells read 0 as built and the presence is above 0, so the field
reads present and in scope; the readings command's r3 checks pass.

### 8.4 The kill cooldown cell

`kill_cooldowns_differing_from_recorded`: round 1 0/487 against 4 (round
start 100, after a kill 227, at a regroup 160), round 2 0/447 against 6 (100,
195, 152), and **round 3 0/442 against 6, with a count at each of the three
writers: round start 100, after a kill 192, at a regroup 150**. Conf. 0 as
built; no writer is empty. The grace-window cell, read at the recorded 6,
counted 0 kills at T+1 to T+6 after any of the round's regroups (0/106).

### 8.5 The envelope and the flag (non-gating)

| cell | round 1 | round 2 | round 3 | envelope |
|---|---|---|---|---|
| impostor win share (`impostor_wins`) | 34/50 = 0.68 (0.54-0.79), flagged above 0.60 | 24/50 = 0.48 (0.35-0.61) | **17/50 = 0.34 (0.22-0.48)** | inside 0.20-0.60, not flagged |
| the re-keyed reporter flag, bar A (above 21.28): `reporter_seats_ejected_without_vent_proof` against `other_crewmate_seats_ejected_without_vent_proof` | 11/98 against 2/303: 17.0, not flagged | 17/93 against 5/291: 10.6, not flagged | **10/95 against 5/302: 6.4, not flagged** | non-gating; never read by the step rule |

Round 2's reading under the old 0.104 line stands as recorded (its audit 6.4);
the readings command does not compute that line, and nothing re-scores
round 2.

### 8.6 The route-check count

A process count, never a bar on correctness: the route-check replay's
`rule_inputs` on each column.

| count | round 1 | round 2 | round 3 |
|---|---|---|---|
| misjudged cases M (ejections charged on a pair the map or the regroup reconciles) | 29 | 40 | **29** |
| at kill-witness meetings, W | 0 | 7 | **7** |
| reach over M: (a), (b), (b-snapshot), (c) | 8, 8, 15, 20 | 15, 16, 20, 29 | **8, 15, 18, 25** |
| reach of (c) over W | 0 | 7 | **7** |
| ejections; charges; charges on a reconcilable pair | 54; 406; 265 | 66; 402; 276 | **61; 376; 226** |

The census's own form agrees: `ejections_charged_on_a_reconcilable_pair`
reads 29/54, 40/66 and **29/61**, and its witness form 0/3, 7/12 and **7/13**.
Beside them, the route-lines instrument's served reach on round 3 (its r3
column, mode "served", read off the blocks the voters were shown): of the 29
misjudged cases, the ejected player's route line was served to its voters in
**26**, and in **7 of 7** at witness meetings; by class, 15 of 15 innocent
ejections, 11 of 14 misjudged impostor ejections, and 6 of 6 ejected kill witnesses carried a served line.
The route lines served 2,416 lines on 671 ballots. Reaching is showing a
line, not changing a vote, and the step reads M alone.

### 8.7 The step the rule names

The readings command's last line, verbatim:

```
step rule: names the era-keyed promotion of round 3 as the shown set, the owner's to take or override (Conf. misses 0; impostor wins 17/50; M 29 against round 2's 40)
```

Every Conf. cell is at 0; the point share of impostor wins, 17/50 = 0.34, is
neither above 0.60 nor below 0.20; and M, 29, is at or below round 2's 40. So
the pre-registered rule (1.11) names **the era-keyed promotion of round 3 as
the shown set**. The rule read no reporter flag and no role-correct figure:
the flag and `role_correct_ejections` were shown in 3.3 to leave the `step
rule:` line byte-identical when edited. The step itself is taken by the
orchestrator, on the owner's criteria and leaning (memo 8.8, section 2.3), and
written into this audit with the readings it rests on, after it reads the
round; this section takes no step.

### 8.8 The reported rows

Reported, gating nothing, each beside its definition in the census.

| cell | round 1 | round 2 | round 3 |
|---|---|---|---|
| `forced_surfacings` | 13/72 | 5/72 | 5/70 |
| table `ticks_inside_per_trip` (1, 2, 3, 4 ticks) | 51, 6, 2, 13 | 49, 3, 15, 5 | 47, 3, 15, 5 |
| `in_place_surfacings_near_crew` | 2/37 | 2/44 | 2/42 |
| `kills_soon_after_surfacing` | 0/227 | 0/195 | 0/192 |
| `skipped_report_meetings` | 70/118 | 51/114 | 58/115 |
| `trips_closed_by_regroup` | 46/142 | 47/140 | 47/140 |
| `kill_witness_button_calls_soon_after_regroup` | 0/6 | 0/3 | 0/4 |
| table `trigger_tick_events_dropped_by_regroup` (Moved, TaskProgressed, TaskCompleted) | 51, 26, 6 | 46, 22, 10 | 50, 19, 10 |
| `meetings_opening_with_impostor_in_vent` (beside it `post_meeting_kills_soon_after`) | 66/124 (0/139) | 66/117 (0/109) | 67/119 (0/106) |
| `accused_opener_answers` | 101/112 | 87/105 | 90/109 |
| `rebuttals_with_alibi`, `_with_whereabouts`, `_with_sighting` | 104/121, 104/121, 91/121 | 89/117, 89/117, 79/117 | 94/119, 94/119, 84/119 |
| `rebuttal_accusations_against_earlier_speakers` | 121/121 | 116/116 | 119/119 |
| table `rebuttal_beneficiaries` (the opener answering an impostor, the opener answering a crewmate, another impostor answering a crewmate, another crewmate answering an impostor, another crewmate answering a crewmate) | 71, 30, 17, 3, 0 | 59, 28, 28, 1, 1 | 60, 30, 25, 0, 4 |
| `own_kill_rows_cited_by_holder`; honesty cell 5 (holders, citing) | 3/4; 4, 3 of 4 | 21/23; 23, 21 of 23 | 20/22; 22, 20 of 22 |
| `impostor_eject_ballots`; `impostor_ejects_labelled_supported`; `authored_teammate_ballot_targets` | 107/203; 107/107; 16/203 | 111/200; 111/111; 16/200 | 101/198; 100/101; 10/198 |
| `reporter_seats_ejected`, `other_crewmate_seats_ejected`, `impostor_seats_ejected` | 11/118, 2/372, 35/194 | 17/114, 5/367, 41/195 | 10/115, 5/375, 42/191 |
| the same three without vent proof | 11/98, 2/303, 15/160 | 17/93, 5/291, 20/158 | 10/95, 5/302, 22/157 |
| the same three with vent proof | 0/20, 0/69, 20/34 | 0/21, 0/76, 21/37 | 0/20, 0/73, 20/34 |
| `reporters_among_ejected_crewmates`; `reporters_among_crewmate_seats` | 11/13; 118/490 | 17/22; 114/481 | 10/15; 115/490 |
| `held_kill_witnesses_ejected` | 0/3 | 5/14 | 6/14 |
| table `held_kill_next_meeting_outcomes` (non-zero rows) | one witness, the killer ejected 3 | one witness: a witness ejected 5, another player 1, no one 2, the killer 1; two or more: the killer 5 | one witness: a witness ejected 6, no one 1, the killer 2; two or more: the killer 5 |
| `held_kill_killers_ejected`; `..._at_any_later_meeting` | 3/3; 3/3 | 6/14; 8/14 | 7/14; 8/14 |
| `ejections_undone_with_impostor_ballots_as_skip`; `..._removed`; `ejections_carried_only_by_impostor_ballots` | 8/54; 2/54; 0/54 | 14/66; 5/66; 0/66 | 8/61; 3/61; 0/61 |
| `holds_nothing_skips_naming_no_candidate` | 0/256 | 0/214 | 0/235 |
| table `holds_nothing_skips_by_source` (a flag, a route line, a spoken turn line, an evidence row, an observation row perceived since the previous meeting) | 13, 0, 256, 256, 184 | 22, 0, 214, 214, 166 | 39, 230, 234, 235, 166 |
| `cited_lines_true_to_the_route`; `cited_lines_false_to_the_route` | 244/259; 15/259 | 278/281; 3/281 | 245/248; 3/248 |
| table `supported_ejects_not_checkable_by_reason` (cites no turn; places the target nowhere checkable; every placement unverifiable) | 17, 108, 0 | 29, 97, 0 | 26, 119, 1 |
| `ejections_on_a_reconcilable_pair`; `ejections_charged_on_a_reconcilable_pair` | 31/54; 29/54 | 41/66; 40/66 | 29/61; 29/61 |
| `witness_meeting_ejections_on_a_reconcilable_pair`; `..._charged_...` | 0/3; 0/3 | 7/12; 7/12 | 7/13; 7/13 |
| `charges_on_a_reconcilable_pair` | 265/406 | 276/402 | 226/376 |

One row is new in kind: a holds-nothing SKIP is counted by each source of a
line that names a living candidate in the voter's own inputs, and on round 3
a route line is one of those sources in 230 of 235 such SKIPs; the line names
a candidate's stated changes of room, never a charge.

### 8.9 Role-correct ejection, the balance and the win split, gating nothing

Role-correct ejections 39/54 = 0.722, 44/66 = 0.667 and **46/61 = 0.754
(0.63-0.84)**; innocent ejections 15 of 54, 22 of 66 and **15 of 61**. Kills
(the denominator of `kills_seen_by_crew`): 227, 195 and **192**. Meetings with
vent proof: 26/124, 24/117 and **24/119**. Impostors able to kill when a
meeting opened (`impostor_cooldown_zero_at_open`): 84/203, 54/200 and
**53/198 = 0.268 (0.21-0.33)**. The win split: 16 crew and 34 impostor wins in
round 1, 26 and 24 in round 2, **33 crew and 17 impostor in round 3**. All are
reported beside the readings and gate nothing; a wrong ejection on believable
data is the game working (scorecard row 8).

## 9. The decision menu

The audit gives no verdict.

- **The step the rule names: the era-keyed promotion of round 3 as the shown
  set** (8.7). Under memo 8.8 the orchestrator takes or declines it on the
  owner's criteria and leaning and writes the decision into this audit with
  the readings it rests on; under memo 8.9 a promotion card's merge is the
  orchestrator's once its reviews pass.
- **`route_lines_version = 1`**, the round's one added field: **adopt** it by
  the era-keyed promotion, **iterate** under a new value, or **keep round 2
  shown**. Its Conf. cells read 0 and its presence is 117 of 119 meetings
  (8.3).
- **The other nine fields**: Conf. cells only, and every one reads 0 (8.2,
  8.4).
- **With the promotion, its card's follow-ups**: a public-results label for
  the route field, which `frontend/src/components/PublicResults.tsx` cannot
  name today; the era registry entry; the pin sweep; round 2's bytes kept as
  `replays/candidates/stage-b-r2` (memo 8.9); the tour's re-curation in the
  same card (memo 8.7 item 3); and the scorecard's frozen before column in the
  grow form the promotion card contracts (the orchestrator's default of
  2026-10-09, memo section 8.9's addendum on `main`).
- **The step taken**: section 11, by the orchestrator under memo 8.8, on the readings above.
- **Before this record merges**: the stop of 7.5, the route-lines card's
  committed-payload case that reads the round's own declared config. Its
  edit is outside this card's scope and is the orchestrator's to assign.

## 10. Limitations

- Hosted generation is not byte-reproducible, so a seed is re-recorded only by
  the failed-seed rule, never to change its bytes (none was). Rounds 2 and 3
  differ in one key, but each is one hosted recording of 50 games: the win
  shares' intervals (0.35-0.61 and 0.22-0.48) overlap, and every difference
  between the rounds is the field's only within that noise.
- M counts ejections charged on a pair the map or the regroup reconciles; it
  does not say whether a served line changed any vote. The served reach (26 of
  29) says the line was shown, not read.
- The arms land together; only the Conf. cells and the scripted, fake and lab
  rows attribute a mechanism, and fake and lab rows establish mechanics, not
  reasoning quality.
- 50 games: the one-reply reading rests on 20 evaluable opener rebuttals of 90;
  the kill row served 22 rows; the witness counts rest on 13 witness-meeting
  ejections.
- The tally counts `llm_calls` rows only, as for rounds 1 and 2; this round has
  no husk and no `failed_call` row. Recording wall comes from the recorder's
  logs, kept outside the repository with the operator log; every other count
  reproduces from the committed bytes with the commands above.

## 11. The step taken (2026-10-09, the orchestrator under memo 8.8)

The orchestrator takes the step the rule names (8.7): candidate round 3 is promoted as the shown set by the
era-keyed path, in one card with the tour's re-curation (decision memo 8.7 item 3), keeping round 2's bytes as
`replays/candidates/stage-b-r2` (memo 8.9). The owner's criteria (memo 8.8), read on this audit:

1. **No issue with the recording.** 50 of 50 seeds in one sitting, 3 h 32 min 47 s from the window's open to the
   last seed, with 3.34 h of recording wall summed over its eleven legs (7.2); no stop rule fired (6.2); cost
   $0.0000; every gate and count-only key scan at every checkpoint passed (6.1, 7.1); every one of the 20 conformance
   cells reads 0, including the field's own two, 0 of 7,956 steps false to the map and 0 of 2,416 lines off the table
   (8.2, 8.3); the spend sits at 54.4, 55.2 and 56.8 percent of the call, input and output ceilings and at 27.8
   percent of the 12 h wall (7.2). The one red test (7.5) read the round's declared config by design and predates the
   round; it was re-scoped test-only (the card's Results, review round 1), not treated as a recording defect.
2. **No step down in gameplay against the direction.** The process rows hold: grounded EJECT ballots 394 of 397,
   unexplained decisions 6 of 702, agent-authored ballots 692 of 702, wrong-but-believable ejections 177 of 397, each
   as 8.1 reads them against round 2. The ejections charged on a route the map or the regroup reconciles fell from 40
   of 66 to 29 of 61, while the ejected player's served line was shown to the voters in 26 of those 29 and in all 7
   witness cases (8.6): the lines reached, and the tables still misjudged 29 times. The impostor win share moved from
   24 of 50 to 17 of 50, inside the band and above the watched floor (8.5); the re-keyed reporter flag reads 6.4
   against bar A's 21.28 (8.5); the cited lines true to the route read 245 of 248 (8.8). One reading this promotion
   carries as a stated limitation: held kill witnesses ejected read 6 of 14 against round 2's 5 of 14, with the
   witness's line served in all six (8.6, 8.8), so the route line reached the witness meetings and did not change
   their outcome. Nothing in this decision reads role-correctness.

The promotion card `promote-round-3` dispatches after this record merges and after `retire-era-locked-pins` merges;
its merge is the orchestrator's under memo 8.9.
