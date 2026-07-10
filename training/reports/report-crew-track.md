# The crew track — a learned scorer over observable crew options (Task 15.16)

> The secondary track of the mid-phase measurement wave: a learned linear
> utility over a FIXED, observable-only crew option set, trained with the
> shared 15.14 ES core against the FROZEN scripted impostor, anchored
> (cross-entropy) to the scripted `CrewmatePolicy`, and evaluated under the
> 15.15 protocol shape (gate / referee / fitness / determinism / leak) on the
> same frozen eval seed set. The honest prior is FO-8's small gain (buddy/task
> gate: +1 game vs the FSM crew) — the deliverable is a clean measurement of
> what observable-option learning buys the crew, not a mandated win.
>
> **Headline:** the trained scorer lifts crew win rate from 3/30 to 18/30 on
> the fixed eval set — and does it by learning to SUPPRESS the report
> interrupt and grind tasks, starving the meeting layer to zero. The validity
> gate and the referee both catch it (§4). Fitness up, gates down: the
> selection-filter split did exactly its job, and that tension — not the win
> number — is the finding the pause should read.
>
> Section refs: audits/post-phase-14-ML-planning.md §4.1 (crew FSM gaps), §5.2
> (the crew option vocabulary + the observability blocker);
> audits/post-phase-14-ML-training-signal.md §3.2 (crew reward terms);
> agents/tactical/crewmate_policy.py (the ladder :343-423;
> `EmergencyPacingTracker`); experiments/lab/ml_spike/fo8_crew_buddy.py (the
> small-gain prior).

Machine-readable rows: `training/reports/results-crew-track.jsonl` (one row
per candidate — the FSM baseline and the trained scorer — same tuple shape as
15.15's `results-impostor-bakeoff.jsonl`). Frozen artifacts:
`training/artifacts/crew/<entrant>/` (float-hex `weights.json` + `.sha256`
sidecar + `config.json`).

---

## 1. The fixed protocol (stated before training ran)

- **The crew twin of the 15.15 harness.** The 15.15 harness's rollout runner
  and eval loop interpose IMPOSTOR decisions only (`_CandidateAgent` returns
  the FSM intent for every crew decision) and its trace/fitness are
  impostor-specific, so this track carries the crew-side twin in
  `training/crew/scorer.py`: `rollout_crew_candidate` (the real production
  loop — `HeadlessGame` through the candidate's own agent factory, impostors
  frozen to the scripted `ImpostorPolicy`) and `evaluate_crew_candidate` (the
  only module that computes reported crew metrics).
  `training/bakeoff/harness.py` and `training/bakeoff/es.py` are consumed
  strictly READ-ONLY: the eval seed loader, the canonical `intent_key`
  alphabet, `TrainedCandidate`, the artifact writer/loader, the row
  sub-models (`DeterminismRow`/`MetricSpread`/`SupplyGaugeRow`), the anchor
  constants, and the whole `(1 + λ)` ES core. The generalization ask this
  implies is stated in §8.
- **Fixed eval seed set.** The frozen corpus TEST split —
  `replays/ml_corpus/9p2i/splits.json`, the 30 seeds with `seed % 5 == 4`
  (`harness.load_eval_seeds`, the same loader and the same seeds as 15.15).
  Training draws only TRAIN-split seeds (`load_train_seeds()[:6]`).
- **Roster + referee baseline.** 9p2i, 2 tasks/crewmate, referee
  `baseline-3` — identical to 15.15. Deterministic fake-provider meeting
  path throughout ($0, offline).
- **The crew inner fitness** (the ES optimizes, identical shape to 15.15 with
  the side flipped): the tactically-reachable crew terms + potential shaping
  (`training.rewards.compute_shaped_reward(..., "CREWMATE").total()` — task
  progress, survival, correctly-routed reports, the engine-truth
  `patrol_coverage` proxy (§6), the terminal win, Φ = completed task
  instances) MINUS an anchor penalty toward the frozen crew FSM, weight 1.0 —
  the anchor cross-entropy: the mean per-decision log-loss of the candidate's
  choice distribution at the FSM's deterministic choice, exactly as 15.15
  defines it. A truncated episode scores the documented −10.0. The validity
  gate and the 15.2 referee are SELECTION columns applied after training —
  never fitness terms.
- **Pre-stated bars.** Anchor-CE ceiling **2.0 nats** (the committed
  `harness.ANCHOR_CE_CEILING`); rows above are FLAGGED, never dropped.
- **Per-candidate gates, through the candidate's OWN crew factory:** the
  15.10 determinism harness (double-run, seeds 1004/1009 at 9p2i; a FAIL
  demotes to experiment-tier with the N-repeat spread) and the leak-test
  factory mode (`eval.leak_test.scan_factory_packets` through
  `build_crew_candidate_factory` — the candidate's real featurizer + head run
  on every crew decision).
- **No surrogate metering.** The 15.13 surrogate's committed staleness cap
  budgets the impostor bake-off + the Goodhart re-run; this track does not
  meter it. The rows carry `inner_fitness_surrogate = null` (shape parity,
  never a silently-zero measurement) and `surrogate_uses_* = 0`.
- **Budgets.** `full` = 20 generations × 12 offspring, K-seed-averaged over 6
  TRAIN-split seeds (the 15.15 utility-es budget mirrored), with TRAINING
  episodes capped at `TRAIN_MAX_TICKS = 300` (recorded in the frozen
  `config.json`; the FO-8 spike precedent — the prior itself trained under
  `max_ticks=80`). The cap exists because an uncapped pilot run drifted into
  marathon survive-and-grind genomes whose games ran to the production
  1000-tick budget, 20-30× the scripted crew's 16-49-tick games; under the
  cap such an episode truncates to the documented −10 sentinel. The EVAL
  protocol keeps the production 1000-tick budget, so every reported number
  below is measured uncapped. Training wall-clock: **1452 s** local CPU
  (1446 rollouts), $0.

## 2. The option set — and the observable-only proof

The FIXED seven-option menu (`training/crew/options.py`), the §5.2 vocabulary
verbatim. Five kinds are the crew FSM's own ladder rungs, generated through
the FSM's OWN pure helpers (zero reimplementation drift — the 15.15 utility-es
idiom); **buddy** and **patrol** are the two observable-only additions the
planning audit names (§4.1: "no witness/buddy/safety awareness at all …
Movement never reads other players' positions").

| option | availability | realized intent |
|---|---|---|
| `continue_task` | a routable engine-fed `pending_task_id` (or the FSM's hub-routing walk when none) | `do_task` in place (skipped while a gating sabotage makes it engine-illegal), else one A* step |
| `buddy` | ≥1 presumed-living, last-seen player whose quantized own-suspicion is BELOW the eject gate | one A* step toward the largest trusted group's room (size DESC, hops ASC, room ASC); `wait` when already with it |
| `patrol` | ≥1 presumed-living, last-seen player whose quantized own-suspicion is STRICTLY ABOVE the neutral 0.5 prior | one A* step toward the top suspect's last-seen room (suspicion DESC, id ASC); `wait` shadows in place |
| `report` | the FSM's rung-1 interrupt (alphabetically-first body in own room) | the FSM's own `ReportBodyIntent` |
| `emergency` | ONLY when the tracker-gated FSM took the button course this tick (§3) | the FSM's button walk, or the press carrying the FSM's `reason` payload |
| `repair` | the FSM's rung-3 gating-sabotage diversion | the FSM's own repair walk / `RepairSabotageIntent` |
| `hold` | always | `wait` |

Per-option features (`CREW_OPTION_FEATURE_NAMES`, 21 dims + bias = genome 22):
the seven kind one-hots, then path-hops / in-place / buddy-group size + min
suspicion / suspect suspicion / sighting age / press flag, then the
decision-level ladder context (body, witnessed kill, gating sabotage, task
completion, crowd density, own max suspicion + over-gate). Every suspicion
value is INTEGER-QUANTIZED through the encoder grid
(`agents.tactical.features.quantize_unit_interval`, 1000 levels) before any
comparison — the §6.3 residue-flips-argmax mitigation — and every roster
iteration is sorted.

**Observable-only, proven three ways.** "Belief-trusted" keys on the crew
agent's OWN suspicion floats — the same self-held information class that
already reaches crew tactics through the emergency gate
(`EmergencyPacingTracker._over_gate` reads the identical suspicion against the
identical eject gate). Nothing role-derived crosses in; the enumeration's
ENTIRE input surface is `(packet, public_map, memory, fsm_intent)`.

1. `tests/training/test_crew_options.py::test_corpus_sweep_menu_is_total_legal_and_observable_only`
   sweeps committed-corpus replays, rebuilds the packets every crew agent
   actually saw, reconstructs each agent's own memory by ingesting exactly
   those packets, and asserts the menu is total, submission-legal, and
   feature-shape-pinned on every decision.
2. The leak-test factory mode runs through the candidate's own crew factory
   in every eval row (`leak_test_passed = true` on both rows below: 534 /
   673 packets scanned) and is pinned by
   `tests/training/test_crew_scorer.py::test_evaluate_crew_candidate_full_row`.
3. `training/crew/options.py` carries the 15.15 import firewall (no `eval.*`
   import; AST-scanned by a committed test).

**Task-ordering is structurally OUT.** The packet exposes a single engine-fed
`pending_task_id` and no owned-task set (`observation/packet.py::SelfView`),
so ordering is un-observable from today's surface — §4.1's "no task selection
or ordering" is "not merely un-learned, it is un-observable" (§5.2). This
track widens nothing; the surface ask goes to the pause in §7.

## 3. Emergency semantics — the tracker gate honored, the 15.8 mask gap closed

**The gate is honored by construction, never re-derived.** The emergency
option exists only when the crew FSM's OWN tracker-gated decision took the
button course this tick: the rung-2 kill-witness interrupt is memory-derived
through the FSM's own `_kill_witnessed` helper; the rung-4 suspicion press IS
`fsm_intent` (kept verbatim, `reason` payload and all); the rung-4 button
WALK is detected by ladder reconstruction (no body, no witnessed kill, no
gating sabotage, and `fsm_intent` equals the button-walk step while differing
from the task continuation — when the two coincide the move is already on the
menu as `continue_task`). The `EmergencyPacingTracker` itself lives untouched
inside the inner `TacticalAgent`, which the wrapper always drives first:
`test_wrapper_emits_reason_stamped_press_through_mask_validation` proves the
tracker samples exactly once per decision (no interposition bookkeeping), and
`test_wrapper_note_meeting_concluded_keeps_tracker_and_uses_in_lockstep`
proves the meeting-end announce/pacing fold runs verbatim.

**The env.py canonicalization region (this task's one edit outside
`training/crew/`).** The mask's emergency entry carries the default payload
(`reason=None`) while the crew FSM stamps `reason='suspicion_accumulation'` /
`'kill_witnessed'`, and mask membership was exact frozen-model equality — so
any selector delegating the FSM's own emergency raised out of the
interposition wrapper (the documented 15.8 gap, `eval/leak_test.py`
`_IdleExploreAgent` docstring; mid-wave review X1). `training/env.py` now
canonicalizes EMERGENCY intents for mask membership by dropping the free-form
`reason` payload (`_canonical_mask_intent`): engine legality is reason-blind
(the tag is agent-side provenance for replay/eval tooling, never an engine
input), so the canonicalization is a faithful mirror; every other intent type
still compares exact — their payloads ARE engine inputs. The button-room
fixture the contract names —
`test_crew_options.py::test_fsm_reason_emergency_is_submission_legal_in_button_room`
— proves a mask-legal crew emergency carrying either FSM `reason` payload
validates as `submission_legal` (and stays illegal outside the button room or
with the one emergency use spent). Today's `tests/training/test_env.py`
emergency fixture only round-trips the mask's own default-payload object and
cannot fail on this; it is left untouched (not in scope) and still passes.

**The uses caveat, mirrored not widened.** The actor's spent-use count is not
on the observation surface, so the eval wrapper carries the
`_InterposedAgent`-precedent tracker and feeds it to the menu: a PRESS is
dropped at zero remaining uses (the mask's emergency legality mirror). The
15.10 determinism harness drives the policy through its fixed `FramePolicy`
surface (no uses argument), where the press keys on the FSM's own
tracker-gated proposal alone — the one documented divergence, reachable only
in the rare state where the FSM re-presses after its call is spent.

## 4. Results — the metric tuple (one row per candidate, 30 eval seeds)

| metric | `crew-fsm-baseline` | `crew-utility-es` |
|---|---|---|
| tier | candidate | candidate |
| validity gate | **PASS** | **FAIL** |
| validity failing checks | none | `all_games_reach_game_over`, `meeting_rate_and_resolution`, `cost_and_provenance_exact` |
| referee passed / mean / median | FAIL / 7.96 / 3.70 | FAIL / 0.00 / 0.00 |
| supply floors | FAIL | FAIL |
| inner fitness (real path) | 11.469 | 13.240 |
| mean shaped crew reward | 11.469 | 14.984 |
| truncated episodes (of 30) | 0 | 1 |
| inner fitness (surrogate) | — (not metered) | — (not metered) |
| anchor cross-entropy (nats) | 0.000 | 0.676 |
| anchor-CE flagged (> 2.0) | no | no |
| off-menu anchor decisions | 0 | 0 |
| FSM intent agreement | 1.000 | 0.707 |
| **crew win rate** | **0.100** (3/30) | **0.600** (18/30) |
| crew survival rate | 0.295 | 0.448 |
| final task completion | 0.759 | 0.919 |
| tasks / 100 ticks | 35.08 | 29.80 |
| meetings (total / crew-triggered) | 116 / 116 | 0 / 0 |
| meeting-trigger quality | 0.000 | — (no meetings) |
| crew report meetings / correct | 104 / 0 | 0 / 0 |
| correct-report rate | 0.000 | — (no reports) |
| mis-eject rate (crew ejections / meetings) | 0.000 (0 / 116) | — (no meetings) |
| impostor / crew ejections | 0 / 0 | 0 / 0 |
| determinism (15.10 double-run) | PASS | PASS |
| leak-test factory mode (packets) | PASS (534) | PASS (673) |
| genome length | 0 | 22 |
| train / eval wall-clock (s) | 0.0 / 8.5 | 1452.3 / 35.0 |

ES trajectory (champion fitness per generation, K=6 train seeds): 11.47 →
13.29 → … → 16.05 (241 evaluations, digest `e138688372ced468…`). The learned
head is directly interpretable — kind weights: `repair +1.57`,
`continue_task +0.83`, `patrol +0.01`, `emergency −0.27`, `buddy −0.41`,
`report −0.49`, `hold −0.65`.

**Mis-eject-relevant deltas (trained vs FSM), and their honest limits:**

- **Win rate +0.500** (3/30 → 18/30), **survival +0.152**, **final task
  completion +0.160**; task pace per tick −5.28 tasks/100 ticks (the trained
  crew's games run longer — it wins by surviving and finishing, not by
  routing faster; the routing lever is closed, §7).
- **Meeting-trigger quality and correct-report rate are DEGENERATE on this
  substrate for both candidates.** The deterministic fake-provider meeting
  path ejected NOBODY in any of the baseline's 116 meetings (0 impostor and 0
  crew ejections; mis-eject rate 0), so the baseline's trigger quality and
  correct-report rate are 0.0, and the trained scorer's are undefined —
  because it triggers **zero meetings**. A mis-eject-relevant improvement is
  unmeasurable on an eval path where meetings never eject; measuring it needs
  the real-provider (or a surrogate-with-ejections) meeting path — an input
  for the pause, not something this track can conjure from the fake provider.

**How the scorer wins — and why the gate flags it.** The optimizer learned
that on this substrate meetings only cost the crew (they eject nobody and
burn time), so it suppresses the report interrupt (`report −0.49` vs
`continue_task +0.83`) and grinds tasks while surviving: 0 meetings across 30
eval games, completion 0.92, 18 task wins. The 15.1 validity gate fails the
candidate on exactly that shape — `meeting_rate_and_resolution` (0 < 0.60),
`cost_and_provenance_exact` (zero meetings ⇒ no model call ⇒ no cost row —
a downstream symptom of the same starvation, not a separate defect), and
`all_games_reach_game_over` (1 of 30 games ground past the 1000-tick
production budget) — and the referee scores the meeting-starved games 0.0.
**This is the selection-filter split doing its job** (training-signal audit
§3.2: the gate/referee are never fitness terms): the fitness says the crew
got better; the gates say the product got worse. Per the 15.15 discipline the
row is reported, never promoted — a gate-FAIL candidate is data for the
pause, and the tension between the win column and the validity column is the
crew track's core finding. (The FSM baseline itself fails the referee's
supply floors on this substrate — mean 7.96 but `flags_per_meeting` /
`testimony_backed_conversion` under their baseline-3 floors — matching the
15.15 rows' posture on the fake-provider path.)

## 5. Anchor-KL to `CrewmatePolicy` — and the FO-8 prior

Anchor cross-entropy (log-loss at the FSM's deterministic choice, as 15.15
defines it) is reported for every candidate: the FSM baseline is exactly
**0.000** by construction (a delta distribution at its own choice, agreement
1.0); the trained scorer measures **0.676 nats** with **0 off-menu
decisions** — every FSM choice was on the menu at every scored decision —
and 0.707 top-1 agreement. That is well under the 2.0-nat ceiling
(unflagged): the piKL-style anchor held the policy near the legible FSM on
~71% of decisions, and the divergence concentrates precisely where the
learned head disagrees with the ladder's priorities (the suppressed report
interrupt and the idle hold).

**The FO-8 prior, quoted.** The spike's buddy/task gate
(`experiments/lab/ml_spike/fo8_crew_buddy.py`; planning audit §8.2): "FO-8
showed a learned crew buddy/task gate is real but small (**11/12 vs FSM
10/12**)" — **+1 game on 12 seeds** (fitness = crew wins vs a fixed FSM
impostor, 9p2i, `max_ticks=80`).

**The measured delta against it: +15 games on 30 seeds** (0.100 → 0.600,
+50 pp vs the prior's +8.3 pp) — an order of magnitude beyond the prior, but
NOT comparable at face value. FO-8's wrapper structurally could not suppress
a report/repair/emergency interrupt (it only re-routed Move/Wait), so its +1
game measured pure buddy-vs-task routing; this track's menu makes interrupt
arbitration itself learnable — that is the point of the option set — and the
optimizer spent the new freedom almost entirely on suppressing reports (§4),
which is where the win-rate explosion comes from and why the gate fails the
champion. Read jointly: FO-8-style interrupt-preserving routing buys little
(+1 game); interrupt ARBITRATION buys a lot of win rate at the price of gate
validity on this substrate. The gate-valid ceiling of crew option learning is
therefore still unmeasured — quantifying it needs either a validity-aware
selection step or FO-8-style interrupt-preserving constraints, a scoping
decision that belongs to the pause.

## 6. The reward disclosure (Q6) — and the coverage-cue diagnostic

**Disclosure.** `training/rewards.py`'s `patrol_coverage` term measures
co-location with an impostor's ACTUAL room — engine truth
(`EpisodeFrame.crew_shadowing_impostor`), not the agent's beliefs. This
engine-truth proxy is the RATIFIED doctrine (owner, 2026-07-09, mid-wave
review Q6): a belief-keyed coverage term would be self-referential — the
policy influences its own beliefs, so it would reward belief manipulation,
the exact Goodhart class this phase avoids — while the engine-truth term is
privileged but structurally ungameable, since the policy cannot see roles and
gradient pressure can only select observable behaviors that correlate with
shadowing impostors. **No re-definition ask goes to the pause.** The
observable-only DoD of §2 governs the POLICY's inputs; the reward channel is
engine-side by design, like every reward term.

**The one required diagnostic** (Q6: "measure the correlation between
coverage credit and the agent's own contemporaneous suspicion toward the
shadowed player"). At every crew decision the eval twin records whether a
living impostor is co-located in the deciding agent's own room (the
per-decision attribution of the frame-level coverage credit; engine-truth
roles feed ONLY this diagnostic) and samples the agent's OWN quantized
suspicion toward the shadowed impostor(s). A credited decision is CUED when
that suspicion exceeds the neutral 0.5 prior, STRONGLY cued at/above the 0.60
eject gate; the co-located-innocent column is the contrast.

| coverage-cue column | `crew-fsm-baseline` | `crew-utility-es` |
|---|---|---|
| crew decisions | 4717 | 11138 |
| credited decisions (co-located w/ impostor) | 1416 | 1526 |
| credited rate | 0.300 | 0.137 |
| mean suspicion toward shadowed | 0.566 | 0.600 |
| cued rate (> 0.5) | 0.159 | 0.200 |
| strongly cued rate (≥ 0.60 gate) | 0.159 | 0.200 |
| mean suspicion toward co-located innocents | 0.500 | 0.500 |
| cue separation | +0.066 | +0.100 |

**Reading: the trained crew's coverage is mostly UN-CUED — ~80% of credited
decisions shadow players the agent holds no elevated suspicion about**
(cued rate 0.200; the baseline FSM's own incidental co-location is 84%
un-cued too). The cue separation is real but small (+0.100: suspicion toward
shadowed impostors sits above the innocent contrast, so the credit is not
pure noise), and the trained scorer's coverage is LESS frequent than the
baseline's (credited rate 0.137 vs 0.300 — it spreads out to grind tasks
rather than crowding). Per the Q6 ruling's own criterion, this term as
earned by THIS champion is predominantly **crowding/incidental co-location
rather than cued patrol** — the pause should revisit the term with exactly
this data. (Note the term did not drive the champion's behavior: its head
weights buddy/patrol negative-to-zero; the coverage credit it earned was a
by-product of task routing through populated rooms.)

## 7. The crew-surface ask (for the pause)

**The field.** Add to the privileged self channel
(`observation/packet.py::SelfView`) an owned-task set:
`owned_task_ids: tuple[TaskId, ...]` — the recipient's OWN unfinished task
instances as MAP task ids (`game_map.tasks` keys, the same id vocabulary as
today's `pending_task_id`), sorted for replay stability, `()` for a player
with no remaining tasks. `pending_task_id` stays (it is the engine's
next-instance feed; the set does not replace it, it widens it to the full
owned frontier).

**Why it is firewall-clean in principle.** Task ownership of one's OWN tasks
is already self-channel information — `pending_task_id` rides the same
privileged channel as `role` / `fellow_impostor_ids`, scoped by owner in
`ObservationService`, and §5.2 already classifies the addition as "a
firewall-clean addition — task ownership for one's own tasks is already
self-channel information."

**The review it needs before landing (the pause owns this decision).**
1. `ObservationService` scoping: the set must be derived from the recipient's
   own instances only and NEVER mirrored into `PlayerView` (the leak
   scanner's role-information rules).
2. The leak suite: `eval/leak_test.py` pins packet key sets — the SelfView
   key-set pin and the recursive hidden-field scan need a deliberate
   extension, and the factory mode must re-run on the widened packet.
3. Byte-shape discipline: the committed corpora and audit logs serialize
   packets verbatim; the field needs the `moved_players` precedent
   (omit-when-empty or an explicit re-record decision) so committed replay
   bytes stay honest.
4. The encoder/leak review note in `agents/tactical/features.py` (the module
   docstring requires any observation widening to be documented there).

**The expected-gain argument, with this track's measured ceiling as the
evidence.** §4.1 [VERIFIED]: "No task selection or ordering … it cannot pick
the nearest of several tasks, batch same-room tasks, or re-prioritize —
selection isn't even in the policy." §5.2 [VERIFIED, blocker]: from today's
surface this is "not merely un-learned, it is un-observable." This track now
supplies the ceiling measurement: with arbitration over the FULL fixed option
set — the entire observable action surface — the trained crew raised final
completion to 0.919 but its task PACE went DOWN (35.08 → 29.80 tasks/100
ticks): every win it found came from survival and interrupt suppression,
none from routing efficiency, because the only routable task is the one the
engine feeds. Nearest-of-N selection and same-room batching attack exactly
that closed lever — task pace is the crew's win condition — and they need
precisely one field: the owned-task set. That is the expected gain; the
measured 29.80 vs 35.08 pace inversion is the evidence that no amount of
option-learning on today's surface can buy it.

## 8. The harness-generalization ask (read-only obligation)

`training/bakeoff/harness.py` was consumed read-only per the contract. What a
crew-capable shared harness would need (documented here instead of edited
there, for the pause / a Wave-2 task behind 15.15's edge):

- `_CandidateAgent.decide` hard-codes the interposed side
  (`role != "IMPOSTOR" → return fsm_intent`) — it needs a side parameter (and
  the crew side needs the emergency-uses tracker + the delegation-aware mask
  validation `training/crew/scorer.py::_CrewCandidateAgent` carries).
- `DecisionTrace` is impostor-specific (kill take-rate accumulators);
  `inner_episode_fitness` hard-codes `compute_shaped_reward(..., "IMPOSTOR")`;
  `BakeoffResult` carries the impostor metric block. Each needs a side-keyed
  twin or a parametrization.
- Until then, `training/crew/scorer.py` carries the crew twins
  (`rollout_crew_candidate`, `CrewDecisionTrace`,
  `crew_inner_episode_fitness`, `CrewTrackResult`) — one file, disjoint from
  the bake-off by construction.

## 9. Reproduce

```bash
# The full crew track: trains the scorer at the recorded budget (20×12 ES,
# K=6 train seeds, 300-tick training episodes), evaluates it + the FSM
# baseline through the fixed protocol (production 1000-tick budget),
# rewrites the jsonl + artifacts.
uv run python -m training.crew.scorer run --budget full

# The machine-readable rows this report quotes (§4, §5, §6):
#   training/reports/results-crew-track.jsonl

# The committed tests that pin the contract (option set, mask
# canonicalization, emergency routing, eval row, corpus sweep, leak mode):
uv run pytest tests/training/test_crew_options.py tests/training/test_crew_scorer.py
```

## 10. How downstream consumes this

- **The pause (15.18)** reads `results-crew-track.jsonl` (the same tuple
  shape as 15.15's rows) for the crew-side decision — the fitness-vs-gate
  tension of §4 and the unmeasured gate-valid ceiling of §5 are the decision
  inputs — plus §6's diagnostic for the Q6 revisit and §7 for the
  owner-gated owned-task-set decision.
- **Artifacts** reload through the 15.15 seam:
  `harness.load_candidate_weights(Path("training/artifacts/crew/crew-utility-es"))`
  → `training.crew.scorer.build_crew_scorer(weights)`.
- **Public types** (stable per the contract):
  `training.crew.options.CrewOption`, `training.crew.scorer.CrewOptionScorer`.
