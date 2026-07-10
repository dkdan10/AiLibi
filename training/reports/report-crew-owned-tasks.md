# The crew owned-task surface — the `SelfView` widening + the gate-valid retrain (Task 15.22)

> Executes audits/audit-phase-15-pause.md decision 5 (YES, with the four-item
> review): widen the crewmate's observation surface by exactly ONE self-channel
> field — `SelfView.owned_task_ids` — and re-measure the crew track's
> gate-valid ceiling on it, under the FO-8-style interrupt-preserving
> constraint the pause scoped (the `report` interrupt is NOT suppressible by
> the learned scorer), so the 15.16 failure mode — win-by-meeting-starvation —
> is structurally unreachable and the ceiling finally gets a number. Crew
> champion adoption is NOT a goal of this task: the deliverable is the surface
> + the honest measurement; any crew deployment is a phase-close/Phase-17 call
> on these numbers.
>
> **Headline: the gate-valid ceiling of crew option learning on the widened
> surface is ZERO on this substrate — win rate 0/30 vs the FSM baseline's 3/30
> under a PASSING validity gate — while the task-pace cell decision 5
> predicted moved exactly as forecast (35.08 → 37.42 tasks/100 ticks, +6.7%).**
> The 15.16 win-rate headline (0.60) was bought entirely with the starvation
> exploit; with `report` removed from the selectable set the optimizer keeps
> the pace gain the owned-task basis exists to buy but converts none of it
> into wins. Fitness up in training, gates up, wins down: the honest number
> the pause asked for.
>
> Section refs: audits/audit-phase-15-pause.md decision 5;
> training/reports/report-crew-track.md §5 (the unmeasured gate-valid ceiling)
> + §7 (the surface ask this task lands); observation/packet.py (`SelfView`);
> observation/service.py (the packet assembly); eval/leak_test.py (the suite
> the new field extends); DESIGN.md §1.3 (the observation firewall).

Machine-readable rows: `training/reports/results-crew-owned-tasks.jsonl` (one
row per candidate — the RE-MEASURED `crew-fsm-baseline` and
`crew-owned-tasks-es` — the 15.15 tuple shape, emitted by the same
`CrewTrackResult` schema as the 15.16 track).

---

## 1. The surface — `SelfView.owned_task_ids`, the four-item review honored

`SelfView` gains `owned_task_ids: tuple[TaskId, ...] = ()` — the recipient's
OWN unfinished task instances as MAP task ids (`game_map.tasks` keys, never
the per-player `"{owner}:{map_task_id}"` instance id), sorted ascending for
replay stability. `pending_task_id` stays and, when non-None, is ALWAYS a
member: for a crewmate it is the set's lexicographic head (the same
owner-scoped filter, widened from head to frontier); for an IMPOSTOR the field
carries the camouflage pretend-task WINDOW
(`observation.service.impostor_pretend_task_set` — the full per-seat window
the rotating `pending_task_id` is drawn from, Task 10.14), so the field
mirrors `pending_task_id`'s role posture exactly and is never mirrored into
the crew-visible `PlayerView` channel.

The four-item review (report-crew-track.md §7; decision 5's condition), item
by item:

1. **`ObservationService` scoping.** `_owned_task_ids_for_agent` mirrors
   `_pending_task_id_for_agent`'s role split and derives strictly from the
   recipient's own engine-side task state (`task.owner == agent_id and not
   task.completed`) — never another player's, never a minted fake instance
   (the impostor window is never a `WorldState.tasks` entry; the 10.14
   integrity invariant holds unchanged).
2. **Leak-suite extension** (`eval/leak_test.py`, the owned-task assertions
   region). Two layers: `_assert_owned_task_discipline` runs on EVERY packet
   (scripted sweep AND factory mode) — the pinned SelfView key set (the
   byte-shape "versioning" guard a future widening must extend deliberately),
   no composite `":"` ids, sorted/deduped, and the role-blind consistency
   invariant `pending ∈ owned` that holds identically for both roles.
   `_assert_owned_tasks_match_engine_truth` runs in the scripted sweep with
   per-tick engine truth in hand: exact equality of the crew set against the
   recipient's own unfinished instances (kill-redistribution included), exact
   equality of the impostor set against its seat window, and — the
   implementation-hint ask — absence of every FOREIGN task id (other players'
   owned ids + other impostors' windows) from the WHOLE packet JSON, not just
   the new field. Three planted-leak tripwires prove the new assertions bite.
3. **Byte-shape discipline.** Additive Pydantic field with a `()` default, so
   any pre-widening bytes reconstruct unchanged. The field ALWAYS serializes —
   the `moved_players` omit-when-empty precedent is deliberately not copied,
   because that serializer exists for an empty-in-the-common-case field and no
   committed artifact pins packet bytes (verified: replays store engine
   `state_hash`es, never packets; the v4/v5 "transcripts" are prompt-version
   stamps on meeting entries). All committed replays byte-verify bare after
   the widening: `scripts/verify_samples.sh` (4p1i 50/50, 9p2i 50/50) and the
   corpus walks (`replays/ml_corpus/9p2i` 150/150, `4p1i` 50/50) reconstruct
   clean.
4. **The encoder note.** The widened basis is TRAINING-side only:
   `crew-option-features` bumps to **`crew-option-features-v2`**
   (`training.crew.scorer.OWNED_TASK_ENCODER_VERSION`), and the production
   encoder (`agents/tactical/features.py`) is untouched — no production
   surface consumes the field this phase.

One honest nuance the adversarial review surfaced (and refuted as a leak):
the camouflage window's CARDINALITY differs by role on the canonical map
(impostor window fixed at 3; a crewmate's frontier is ≤ tasks_per_crewmate and
shrinks). This is the same asymmetry class `pending_task_id` already carries
(impostor always non-None and rotating; crewmate None when done) and it lives
ONLY on the privileged self channel, where `role` is already plaintext —
every position that can observe the cardinality already holds the role
verbatim, and the field never crosses to another player's packet
(leak-suite-proven). No role bit crosses the §1.3 firewall.

## 2. The widened option basis — nearest-of-N + same-room batching

`training.crew.options.OwnedTaskOptionBasis` (the task's public type) WRAPS
the pinned 15.16 menu (`enumerate_crew_options` is byte-identical; every
15.16 pin — 7 kinds, 21 features, genome 22 — holds) and re-bases it onto the
widened alphabet: **8 kind one-hots** (the 15.16 kinds as a prefix +
`nearest_task`) **+ the 14 legacy scalars verbatim + 4 owned-task scalars**
(`owned_tasks_norm`, `nearest_owned_hops_norm`, `same_room_owned_norm`,
`goal_room_owned_norm`) = 26 features, genome **27**.

The `nearest_task` option is the nearest-of-N selection lever: the owned task
minimizing (A* hops, map id) — materialized only when it differs from the
engine-fed `pending_task_id` (else `continue_task` already carries it) —
realized as `do_task` in place, or one A* step toward its room, and skipped
entirely while a gating sabotage makes `do_task` engine-illegal. Same-room
batching rides the scalars: `same_room_owned_norm` (owned tasks co-located
with the agent) and `goal_room_owned_norm` (owned tasks in a task-directed
option's goal room).

The one legality seam: the action mask (`training/env.py`, read-only this
task) enumerates `do_task` only for `pending_task_id` — pre-15.22 the packet
carried no owned set — while the engine accepts a `do_task` for ANY owned
unfinished task in the actor's room (`engine/tick.py::_apply_do_task`). The
eval wrapper therefore carries
`_owned_task_do_task_is_submission_legal`, a mirror of the engine predicate
over the widened self channel (the emergency-uses-tracker precedent for
wrapper-carried legality inputs), so a `nearest_task` override validates
fail-loud like every other override.

## 3. The interrupt-preserving constraint — structural, not a penalty

Per the pause's scoping (and the Goodhart lesson the hint restates): `report`
is REMOVED from the scorer's selectable set rather than penalized. When a
body is visible in the agent's own room (the FSM's rung-1 interrupt), the
widened menu is a 1-tuple containing ONLY the report option — the learned
head has nothing to select away from, mirroring the FSM's interrupt
semantics exactly. `tests/training/test_crew_owned_tasks.py` proves it: a
scorer loaded +100 on every non-report kind still emits the
`ReportBodyIntent`. The consequence is measured in §4: the retrained
candidate's 30 eval games produce **103 meetings** (the 15.16 champion
produced 0) and the validity gate PASSES — the meeting-starvation channel is
structurally unreachable, exactly as decision 5 contracted.

## 4. Results — the metric tuple (both rows re-measured, 30 eval seeds, hardened referee)

Fixed protocol: the 15.16 shape verbatim — frozen corpus TEST split (30
seeds, `seed % 5 == 4`), 9p2i at 2 tasks/crewmate, deterministic
fake-provider meeting path ($0, offline), referee `baseline-3` under the
**hardened 15.19 definition** (conversion-coupled D2 + subject-aware backing
+ advisory rare-event floors — the module at HEAD), the 15.10 determinism
harness and the leak-test factory mode through the candidate's own factory.
Training: the 15.14 `(1+λ)` ES core consumed as-is, full budget (20×12,
K=6 train seeds, 300-tick training episodes), anchor weight 1.0. The
`crew-fsm-baseline` comparator is RE-MEASURED through this identical
protocol (never quoted from the 15.16 jsonl).

| metric | `crew-fsm-baseline` (re-measured) | `crew-owned-tasks-es` |
|---|---|---|
| tier | candidate | candidate |
| validity gate | **PASS** | **PASS** |
| validity failing checks | none | none |
| referee passed / mean / median (15.19-hardened) | FAIL / 3.33 / 3.70 | FAIL / 3.60 / 3.70 |
| supply floors | FAIL (all three) | FAIL (all three) |
| floor-trip rate | 0.0 | 0.0 |
| inner fitness (real path) | 11.469 | 10.335 |
| mean shaped crew reward | 11.469 | 10.777 |
| truncated episodes (of 30) | 0 | 0 |
| inner fitness (surrogate) | — (not metered) | — (not metered) |
| anchor cross-entropy (nats) | 0.000 | 0.441 |
| anchor-CE flagged (> 2.0) | no | no |
| off-menu anchor decisions | 0 | 0 |
| FSM intent agreement | 1.000 | 0.919 |
| **crew win rate** | **0.100** (3/30) | **0.000** (0/30) |
| crew survival rate | 0.295 | 0.362 |
| final task completion | 0.759 | 0.719 |
| **tasks / 100 ticks** | **35.08** | **37.42** |
| meetings (total / crew-triggered) | 116 / 116 | **103 / 103** |
| meeting-trigger quality | 0.000 | 0.000 |
| crew report meetings / correct | 104 / 0 | 91 / 0 |
| mis-eject rate (crew ejections / meetings) | 0.000 (0/116) | 0.000 (0/103) |
| impostor / crew ejections | 0 / 0 | 0 / 0 |
| determinism (15.10 double-run) | PASS | PASS |
| leak-test factory mode (packets) | PASS (534) | PASS (6258) |
| genome length | 0 | 27 |
| encoder version | crew-fsm-delegate-v1 | crew-option-features-v2 |
| train / eval wall-clock (s) | 0.0 / 11.1 | 2158.5 / 30.0 |

ES trajectory (champion fitness per generation, K=6 train seeds): 10.62 →
11.59 (241 evaluations, digest `eb2426c9a5abaafa…`), plateauing early — under
the interrupt constraint the optimizer finds no fitness cliff to climb. The
learned head is directly interpretable; the largest weights:
`kill_witnessed +2.25`, `path_hops_norm −1.86`, `kind_buddy −1.81`,
`kind_patrol −1.79`, `kind_emergency +1.50`, `own_over_gate +1.35`,
`kind_nearest_task −1.00`, `kind_continue_task +0.97`, … `kind_report −0.66`.
Two readings worth recording: the optimizer STILL pushes `kind_report`
negative — the same suppression pressure that produced the 15.16 exploit —
but the structural constraint makes the weight irrelevant (report is the
whole menu when a body is visible; agreement stays 0.919 and 103 meetings
happen anyway); and it prices routing distance steeply (`path_hops_norm
−1.86` with `goal_room_owned_norm +0.69`), which is where the pace gain
comes from.

Meeting-quality columns are degenerate on this substrate for BOTH candidates
(the 15.16 caveat verbatim): the deterministic fake-provider meeting path
ejects nobody, so trigger quality and correct-report rate are 0 for the
baseline and for the retrained candidate alike; both referee rows fail the
same meeting-driven supply floors (`flags_per_meeting` 0.0,
`testimony_backed_conversion` null, `witnessed_event_rate` under floor)
because fake meetings mint no evidence — the structural fake-path artifact
the 15.15/15.16 rows documented, not discrimination between these rows. Note
the comparator shift the hardening causes: the same FSM baseline that scored
referee-mean 7.96 in the 15.16 row scores **3.33** under the 15.19
conversion-coupled definition — which is exactly why this task re-measures
the comparator through the identical protocol instead of quoting the old row.

## 5. The gate-valid ceiling — the finding decision 5 contracted

All four numbers cited to `results-crew-owned-tasks.jsonl`:

- **Gate-valid win-rate delta: −0.100** (`crew_win_rate` 0.000 vs the
  re-measured baseline's 0.100; 0/30 vs 3/30). Both rows PASS the validity
  gate (`validity_passed: true`, empty `validity_failing_checks`), so this is
  the ceiling measurement 15.16 could not produce: with the report interrupt
  structurally preserved, learned option arbitration over the widened surface
  wins NO games the scripted ladder doesn't, and loses the three it does.
- **Gate-valid fitness delta: −1.134** (`inner_fitness_real` 10.335 vs
  11.469). The anchor penalty is not the story (anchor-CE 0.441, agreement
  0.919); the shaped-reward column itself is down (10.777 vs 11.469).
- **The task-pace cell decision 5 predicted: +2.34 tasks/100 ticks**
  (`tasks_per_100_ticks` 37.42 vs 35.08, +6.7%). Decision 5's expected-gain
  argument was that nearest-of-N selection and same-room batching attack
  exactly the routing lever the closed surface hid (the 15.16 champion's
  pace INVERTED to 29.80 while it won by starvation). Measured: the pace
  cell moves UP under a PASSING gate — the owned-task basis buys real
  routing efficiency — and survival rises with it (0.362 vs 0.295).
- **But pace does not convert into wins — and the loss channel is
  measured, not guessed.** Replaying both candidates over the same 30 eval
  seeds (the deterministic protocol makes this a pure reconstruction from
  the committed artifacts) and classifying each game's end state: the FSM
  baseline loses 27 games at kill parity and 0 to sabotage; the retrained
  candidate loses 20 at parity and **10 with MORE than two crew alive — an
  unrepaired gating sabotage is an impostor win**, and its games end
  earlier (mean final tick 27.7 vs 31.3; `descriptor_footprint` kills/game
  4.47 vs 4.93, median kill tick 13.65 vs 16.60). The constraint made
  `report` structural, but the rung-3 REPAIR diversion stayed arbitrable —
  and the learned head (repair ≈ −0.09 against `continue_task +0.97` with
  steep distance pricing) sometimes routes tasks through a live reactor
  timer. Final completion lands at 0.719 vs 0.759 for the same reason:
  faster per-tick routing, games cut short by the sabotage clock. The
  15.16 lesson generalizes exactly one rung up: every interrupt the menu
  leaves arbitrable is a channel the optimizer will trade against the win
  condition — with report closed, it spent repair. The honest gate-valid
  ceiling of option learning on this substrate is **zero (negative)
  win-rate delta**.

Read against the priors: FO-8 (interrupt-preserving routing, +1 game on 12
seeds) predicted small; the hint predicted "smaller than 15.16's 0.6"; the
measurement lands at the floor of both. The instructive split is
pace-vs-wins: the surface delivers the capability decision 5 predicted
(routing), and the substrate's win condition cannot reward it — a Phase-17
scoping fact (the real-meeting path, where reports convert to ejections, is
where a pace-positive, report-compliant crew could actually cash in), not a
verdict on the field.

## 6. The reward and diagnostic columns (continuity with 15.16)

The reward definition is unchanged (`training/rewards.py`, side CREWMATE —
task progress, survival, correctly-routed reports, the owner-ratified
engine-truth `patrol_coverage` proxy, terminal win; anchor penalty weight
1.0), so the fitness columns are directly comparable to the 15.16 rows. The
Q6 coverage-cue diagnostic reports for both rows (baseline: credited rate
0.300, cue separation +0.066; retrained: 0.302 / +0.060) — the retrained
crew's coverage profile is baseline-like, unlike the 15.16 champion's
spread-out grinding (0.137), consistent with its 0.919 FSM agreement.

## 7. Deployment posture

**No crew default change ships in this phase.** The scripted `CrewmatePolicy`
remains the default, the anchor, and the only crew policy any recording path
runs. The surface (`owned_task_ids`) is landed, leak-proven, and
byte-compatible; the widened basis, its champion artifact, and this
measurement are **Phase-17 scoping inputs** (decision 4's co-adaptation
revisit and decision 5's evidence trail): the gate-valid ceiling on the
fake-provider substrate is zero, the pace lever is real, the measured loss
channel is the still-arbitrable repair interrupt (§5 — the natural next
structural-constraint candidate if Phase 17 re-opens crew training), and any
future crew deployment case must be made on a meeting path where reports can
convert — re-measured under this same protocol at that time.

## 8. Reproduce

```bash
# The full owned-task retrain: trains the widened-basis scorer at the
# recorded budget (20x12 ES, K=6 train seeds, 300-tick training episodes),
# re-measures the FSM baseline, evaluates both through the fixed protocol
# (production 1000-tick budget, hardened 15.19 referee), rewrites the jsonl
# + artifacts. Fully deterministic (seeded ES, fake-provider rollouts):
# re-running reproduces the committed rows' weights_sha256 digests exactly.
uv run python -m training.crew.scorer run --basis owned-tasks --budget full

# The machine-readable rows this report quotes (§4, §5, §6):
#   training/reports/results-crew-owned-tasks.jsonl

# The committed tests that pin the contract (packet scoping + byte shape,
# leak discipline + tripwires, the widened basis + the structural interrupt,
# the wrapper legality mirror, the owned entrant + full eval row):
uv run pytest tests/observation/test_packet_owned_tasks.py \
              tests/training/test_crew_owned_tasks.py eval/leak_test.py

# The committed-replay byte-verification walk (the §1 item-3 evidence):
bash scripts/verify_samples.sh
uv run python scripts/_verify_samples.py replays/ml_corpus/9p2i
uv run python scripts/_verify_samples.py replays/ml_corpus/4p1i
```

Artifacts land under `training/artifacts/crew/{crew-fsm-baseline,
crew-owned-tasks-es}` (float-hex `weights.json` + `.sha256` sidecar +
`config.json`); the rows carry the digests (`bd6fdd0a…` for the retrained
champion). The retrain's artifacts are re-derivable bit-exactly from the
command above.

## 9. How downstream consumes this

- **Phase close (15.23) / Phase 17** read
  `results-crew-owned-tasks.jsonl` for the gate-valid ceiling (§5) and the
  deployment posture (§7); nothing in the shipped default changes.
- **Public types** (stable per the contract):
  `training.crew.options.OwnedTaskOptionBasis` (plus the widened constants
  `OWNED_TASK_OPTION_KINDS` / `OWNED_TASK_OPTION_FEATURE_NAMES` /
  `owned_task_genome_length`).
- **Reload seam:**
  `harness.load_candidate_weights(Path("training/artifacts/crew/crew-owned-tasks-es"))`
  → `training.crew.scorer.build_crew_scorer(weights,
  basis=OwnedTaskOptionBasis())`.
- **The observation surface** is production-wide: every packet now carries
  `owned_task_ids` on the privileged self channel behind the extended leak
  suite; the production encoder deliberately does not read it this phase
  (§1 item 4).
