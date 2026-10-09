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
