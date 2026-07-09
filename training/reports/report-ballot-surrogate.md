# The ballot-predictor surrogate — the GO/NO-GO verdict, the fallback ladder, the staleness doctrine

> Task 15.13 (`tasks/phase-15.md`). Anchored to
> `audits/post-phase-14-ML-training-signal.md` §5.3 (predict ballots, feed the real
> tally), §5.5 (the four-channel fidelity protocol + the honest ceiling), §5.6 (the
> re-grounding / model-exploitation doctrine). Code:
> `training/surrogate/ballots.py` (the predictor + training entry),
> `training/surrogate/runner.py` (the `MeetingRunner` implementation),
> `training/surrogate/fidelity.py` (the GO/NO-GO region — 15.11 owns the metrics
> core), `eval/balance_eval.py:228` (the additive `meeting_runner_factory` keyword).
> This report sits beside the 15.11 harness report (`report-meeting-table.md`) — the
> table and the FO-6 re-baseline it documents are the substrate every number below
> is measured on.
>
> **Date:** 2026-07-09.
> **Corpus:** `replays/ml_corpus/9p2i` — 150 games, frozen at **baseline-3**
> (`Qwen/Qwen3-32B` on Featherless, `qwen3_32b` prompt set, 15.9 `fsm-default`
> stamp, `$0`), committed `splits.json` **seed mod 5: {0,1,2}=train, {3}=val,
> {4}=test** → **fit side 120 games / held-out test 30 games**.
> **Committed artifact:** `training/artifacts/surrogate/ballot-predictor.json`,
> sha256 `1c99cbd1eee56fd961098d01ca484d4137fc921301feeca6d2f4b606fb2b52bf`,
> staleness cap **50000 meetings** (`max-uses.json`).
>
> Reproduce every figure with the one-liners in §9 — each is a pure function of the
> committed bytes and writes nothing.

The 15.11 harness re-baselined FO-6 honestly and measured the honest ceiling; this
task builds the surrogate that lives inside that ceiling, states the bar **before**
training, and reports the verdict. The verdict is **NO-GO** — and the deliverable is
the same either way: a $0 ballot-predicting surrogate that ships as a **diagnostic**,
with the fallback ladder, the staleness cap, and the re-grounding recipe all in
place so a NO-GO can never block the bake-off.

---

## 1. The pre-stated GO/NO-GO bar (OWNER-RATIFIED 2026-07-09, mid-wave review Q1)

The bar was stated **before** the surrogate was trained and committed in code as
`training.surrogate.fidelity.GO_TOP1_CEILING_RATIO` (= 0.75) + `decide_go_no_go`. It
is **population-relative on all three axes, with no absolute constants** — because
every absolute number in this project's history moved when the population changed
(FO-6 top-1 64% → 26%; the honest ceiling 65.1% → 70.6%), an absolute threshold is a
trap. Each axis is measured by the 15.11 harness **on the same scored held-out
population** as the surrogate's own numbers:

> **GO ⇔** held-out top-1 **≥ 0.75 × the honest ceiling measured on the same scored
> population** by the 15.11 harness (never the samples-set 70.6% figure) **AND**
> held-out top-1 **>** the corpus-re-baselined FO-6 logistic (never the spike's 64%
> or the samples-set 25.7%) **AND** SKIP-vs-eject accuracy **>** the scored
> population's own `always_eject_baseline` (on this corpus test split that trivial
> constant is **0.802** — the samples-set 78.4% does not transfer).

Pre-committed **in the same breath**: **NO-GO ⇒ fallback (a)** — the fake-provider
MeetingManager stays the bake-off's training-time runner and the surrogate ships as
a **DIAGNOSTIC only** (its fidelity report still lands; nothing trains against it).
`decide_go_no_go` encodes exactly that mapping in its `training_time_runner` /
`surrogate_role` fields so the bake-off consumes the verdict, not a prose reading of
it. The staleness cap (§7) ships regardless of the verdict.

---

## 2. The model + the live-parity feature decision

The predictor (`training.surrogate.ballots.BallotPredictor`) is a **standardized
conditional logit**: one shared weight vector over per-(voter, candidate) features
plus a **learned SKIP alternative** over per-voter aggregates, softmax over
`candidates + [SKIP]`, fit by full-batch gradient descent (zeros init, no RNG, 300
epochs, lr 0.3 — the `Fo6Logistic` deterministic recipe). The ballot **confidence**
is a ridge-solved linear head on the chosen target's standardized features, clipped
to [0, 1]. Weights serialize as **float-hex JSON** (lossless float64, the
`agents/tactical/features.py::weights_to_hex_json` convention) with a **sha256
sidecar**. Serialization is byte-stable (load → re-serialize is the identity),
and a refit is byte-identical **on the recording platform**; across CPUs a refit
agrees only to float ULP (numpy's SIMD summation grouping varies by machine), so
the **committed bytes are the frozen ground truth** the sha pins and the bake-off
reloads — the round-trip test asserts refit parameter-equivalence plus
frozen-weights reproduction of every reported number.

| Head | Features |
|---|---|
| Per-candidate choice utility | `belief_suspicion`, `belief_trust`, `is_reporter`, `witnessed_vent`, `meeting_index`, `alive_count` |
| Learned SKIP alternative | `max_belief_suspicion`, `meeting_index`, `alive_count` |
| Confidence head (ridge) | the chosen target's six standardized candidate features + bias |

**The live-parity feature decision (the load-bearing design call).** The six
per-candidate columns are *exactly* the subset a `SurrogateMeetingRunner` can derive
**identically at `run_meeting` time** from the `MeetingRunner` protocol's trigger-time
inputs (`trigger`, `state`, `agents`): `belief_suspicion` / `belief_trust` off the
agent's own `suspicion_graph_for_meeting()`, `witnessed_vent` off its typed
`vent_witness_records_for_meeting()` channel, `is_reporter` from
`trigger.triggered_by`, `meeting_index` / `alive_count` from the orchestrator id and
the living roster. The columns a live runner **cannot** reconstruct are excluded **by
design, not oversight**: the contradiction-flag structure and `contradiction_lift`
need **this meeting's transcript** (a training-time surrogate has no LLM, hence no
transcript — the same structural blindness the honest ceiling measures), and the
physical window stats (`witnessed` / `isolation` / `seen_at_kill` / `body_proximity`
/ `task_submissions` / `move_count`) need the inter-meeting **event history** the
runner never sees. Training on features that would be identically zero (or
unobtainable) live would **inflate the offline fidelity number the GO/NO-GO verdict
reads while the deployed runner behaves worse** — exactly the "weaken a mitigation to
make the verdict look better" failure the task contract forbids.

The predicted ballots feed the **REAL** deterministic
`meetings.voting.tally_ballots` (`meetings/voting.py:120-213`) at the **explicit**
`meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD` (0.60) — plurality +
SKIP-first-class + tie→SKIP + a confidence gate on the leader's ballot. The tally is
consumed **pure, never reimplemented** anywhere in `training/`; SKIP-vs-eject emerges
from the real tally, never from a tuned binary head (this is what eliminates FO-6's
always-SKIP collapse by construction, §5.2/§5.3). One ballot per living voter is
exactly the roster the cross-meeting belief fold reads off `result.ballots`
(`meetings/manager.py:2841`).

---

## 3. Held-out fidelity vs the ceiling (the four channels together)

Scored population: the **9p2i corpus test split** — 30 games / **91 meetings** / **73
ejections** / **18 skips**. Every channel below (ranking, decision, calibration, the
ceiling) is measured on **this one distribution**, so they describe the same games.

**Surrogate `ballot-surrogate.v1`:**

| Channel | Value |
|---|---|
| top-1 (ejected target ranked first) | **64.4%** (47/73) |
| top-2 | **82.2%** (60/73) |
| SKIP-vs-eject decision accuracy | **76.9%** (70/91) |
| — correct ejects / correct skips | 70 correct ejects · **0** correct skips |
| always-eject baseline (population constant) | **80.2%** (73/91) |
| decision census (predicted) | 88 ejections · 3 skips |
| — where the 3 predicted skips fell | all 3 on **true-ejection** meetings |
| `degenerates_to_skip` | **False** (the FO-6 collapse did not recur) |
| ejection-confidence Brier / ECE | 0.0984 / 0.0798 |

**The honest ceiling on the SAME population** (a measurement, not a target):

| Ceiling channel | Value |
|---|---|
| max achievable top-1 | **68.5%** (reachable 50/73) |
| flag on target | 54/73 |
| proximity/eyewitness on target | 44/73 |
| strict belief-lead on target | 40/73 |
| voice-driven share (the complement) | **31.5%** |

The surrogate's top-1 (64.4%) sits at **94% of the ceiling** (68.5%): the ranking
channel is near the structural cap. ~31.5% of ejections formed from the current
meeting's spoken narrative — no flag, no proximity, no pre-meeting suspicion lead —
and are invisible to any training-time surrogate by construction.

**FO-6 re-baseline on the SAME population** (`fo6_rebaseline`, the floor to beat):

| FO-6 channel | Value |
|---|---|
| top-1 | **17.8%** (13/73) |
| top-2 | 41.1% |
| SKIP-vs-eject decision accuracy | 34.1% |
| `degenerates_to_skip` | **True** — 53/73 true ejections called SKIP |
| decision census (predicted) | 27 ejections · 64 skips |

**Recorded-ballot reference calibration (the WOLF channel, model-INDEPENDENT).** Over
the scored split's **501** non-SKIP recorded ballots, each real voter's stated
confidence vs whether its named target was ejected: **ballot Brier 0.2070 / ballot
ECE 0.1010**. This is a property of the committed ballots — it is *not* the
surrogate's calibration (§4), and the harness reports it for every model as the
ground-truth reference (arXiv:2512.09187 WOLF ~0.26–0.29).

---

## 4. The surrogate's PREDICTED-ballot calibration (its OWN channel)

Distinct by construction from the recorded reference in §3. Fitting
`BallotSurrogateModel` on the non-test views and scoring the predicted **non-SKIP**
ballot confidences on the test views against whether the predicted target was
actually ejected:

| Predicted-ballot calibration | Value |
|---|---|
| Brier | **0.3574** |
| ECE | **0.4076** |
| predicted ballots (non-SKIP) | 529 |
| predicted SKIP ballots | 0 |

**State it plainly:** the harness's committed `ballot_brier` (0.2070) / `ballot_ece`
(0.1010) are the **model-independent RECORDED-ballot reference**; the numbers in this
section are the **surrogate's own predicted-confidence calibration** and are
**markedly worse**. The surrogate predicts SKIP on **zero** ballots and is
**over-confident on targets that were not ejected** — the per-voter argmax names a
target with high confidence even when the real meeting split its vote or gated to
SKIP. This is the same failure the decision channel shows in §5, seen from the
calibration side.

---

## 5. THE VERDICT: NO-GO

`decide_go_no_go(surrogate, fo6)` on the shared 91-meeting / 73-ejection population:

| # | Axis | Surrogate | Bar | Result |
|---|---|---:|---:|:---:|
| 1 | top-1 ≥ 0.75 × ceiling | 0.6438 | 0.5137 (= 0.75 × 0.6849) | **PASS** |
| 2 | top-1 > FO-6 re-baseline | 0.6438 | 0.1781 | **PASS** |
| 3 | SKIP-vs-eject > always-eject | 0.7692 | 0.8022 | **FAIL** |

Two of three axes pass; axis 3 fails, so the conjunction is **NO-GO**. Per the
pre-committed consequence: **fallback (a)** — the fake-provider MeetingManager (the
training env's default runner, `training/env.py::_build_meeting_runner`) **is** the
bake-off's training-time runner; the surrogate ships as a **diagnostic only**
(reachable via `run_tournament_eval`'s `meeting_runner_factory` and the env's
`meeting_runner_factory` seam, inside the staleness cap); **nothing trains against
it**, and final champion numbers are **never surrogate-scored**.
`decide_go_no_go` returns `training_time_runner="fake-provider-meeting-manager"`,
`surrogate_role="diagnostic-only"` — the machine-readable form of exactly that.

**Honest diagnosis.** The ranking channel is near-ceiling (94%); the decision channel
is the whole failure. Recorded voters individually cast SKIP on only ~5% of ballots
— real SKIPPED **meeting outcomes** arise mostly from vote **SPLITS** and the 0.60
confidence gate, not from voters agreeing to skip. A deterministic per-voter argmax
**over-converges**: every voter votes its argmax with a confident head, so the real
tally ejects on **all 18 true-skip meetings** (0 correct skips; the surrogate's only
3 predicted skips all fall on true-ejection meetings). From ballot-level supervision
alone the decision channel
cannot beat the **80.2%** always-eject constant — the plurality/split structure that
produces a real SKIP is not recoverable from argmax ballots without modelling the
LLM's vote-dispersion, which a $0 deterministic surrogate does not have.

**The verdict was taken on the FIRST held-out evaluation.** The model was **not**
iterated against the test split — doing so would corrupt the held-out claim. The
**val** split exists for any future model iteration, and any re-fit re-states its
verdict against **this same population-relative bar** (§9 reproduces it end-to-end).

**Secondary diagnostic — 4p1i corpus test split** (tiny, noise-dominated: 10
meetings / 8 ejections):

| Channel | Surrogate | Reference |
|---|---:|---:|
| top-1 | 75.0% (6/8) | ceiling 87.5%; FO-6 50.0% |
| SKIP-vs-eject | 80.0% | always-eject 80.0% → axis 3 fails (strict `>`) |
| predicted-ballot calib Brier / ECE | 0.3031 / 0.3319 (n=30) | — |

**NO-GO on both populations.** One committed artifact — the **9p2i corpus fit**, the
primary scored population; the 4p1i figures are a corroborating diagnostic only.

---

## 6. The fallback ladder as shipped (all three in-contract)

All three are contracted; **(a) is live today**, which is what proves a NO-GO cannot
block the bake-off:

- **(a) fake-provider MeetingManager as the training-time runner** — the training
  env's **DEFAULT** (a runner is always installed; `MEETING_PHASE_REACHED` truncation
  is structurally unreachable on this path). Exercised by committed test **regardless
  of the verdict**, so a NO-GO can never block the bake-off.
- **(b) the 15.8 env's explicit `episode_boundary="first_meeting"` opt-in** with
  meeting-free fitness terms — episodes are marked **truncated** and
  `compute_shaped_reward` refuses to score them as full games (the deliberate
  boundary mode 15.8 contracts, **not** silent truncation).
- **(c) periodic real-LLM re-grounding recordings** — operator-run, `$0` on
  flat-rate Featherless (the 15.12 recorder). This is also the staleness-cap escape
  hatch (§7–§8).

---

## 7. The staleness doctrine (ships regardless of verdict)

Committed cap file `training/artifacts/surrogate/max-uses.json`:

```json
{ "max_uses": 50000, "unit": "meetings",
  "weights_sha256": "1c99cbd1eee56fd961098d01ca484d4137fc921301feeca6d2f4b606fb2b52bf" }
```

- **Unit:** surrogate-simulated **MEETINGS** — one `SurrogateMeetingRunner.run_meeting`
  call is one use.
- **Keyed on the weights sha256:** `SurrogateUseCounter.record_use` refuses to meter a
  different artifact against the same counter.
- **CUMULATIVE across a bake-off run:** the bake-off owns **ONE**
  `SurrogateUseCounter` and threads it through every runner factory; constructing a
  fresh runner **never** resets it; exceeding the cap raises
  `SurrogateStalenessExceededError` (deliberately not silently recoverable — a trainer
  at the cap must re-ground, §8).

**Rationale for 50000.** The fit is grounded on **349 fit-side meetings** (the
2599-row table, 120 fit games). 50k simulated meetings ≈ **143× the grounding data** —
enough headroom for a mid-size ES bake-off (e.g. ~24 pop × ~30 gens × ~5 seeds ×
~2–3 meetings/game ≈ **7–11k** simulated meetings per sweep, a few sweeps per run)
while **forcing re-grounding before unbounded optimization against a frozen model**
(the MBPO/Dreamer model-exploitation failure, audit §5.6). The cap is
**operator-tunable** by editing the committed file — which re-keys review to the
artifact hash (the sidecar + cap must agree with the weights, checked on load).

---

## 8. The re-grounding recipe (operator, `$0`, step-by-step)

Mandatory after **any mover (tactical policy) change**, **any meeting-layer/prompt
change**, or when a bake-off run **hits the cap**. The corpus README's freeze
doctrine applies throughout (never re-record without re-freezing).

1. **Record** a fresh real-LLM corpus slice at the current mover/meeting config —
   `bash scripts/record_ml_corpus.sh --set 9p2i` (Featherless, frozen prompt
   registry, `fsm-default` stamp — or the future champion's stamp) into a **NEW seed
   range**.
2. **Rebuild the table** — `build_meeting_table(Path(<new corpus dir>))` (it reads the
   recorder-written committed `splits.json`).
3. **Re-fit + commit weights** —
   `fit_corpus_ballot_predictor(table)` then
   `write_ballot_predictor_artifact(predictor, Path("training/artifacts/surrogate"))`.
   A new sha256 is written; the use-counter **re-keys automatically**.
4. **Re-measure** — `run_surrogate_fidelity` + `fo6_rebaseline` + `decide_go_no_go`
   on the new table; the verdict **re-states itself** against the same
   population-relative bar.
5. **Commit together** — weights + sha256 sidecar + cap + the updated report in one
   change.

---

## 9. Reproduce

Every number above is a pure function of the committed bytes. Each one-liner writes
nothing.

- **Table** (440 meetings / 2599 rows; fit 349 meetings / 120 games, test 91
  meetings / 30 games):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); print(t.meetings_total, len(t.rows), t.games_total)"
  ```
- **Surrogate fidelity report** (§3, §4-recorded-ref):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table, run_surrogate_fidelity; from training.surrogate.ballots import BallotSurrogateModel; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); print(run_surrogate_fidelity(t, lambda: BallotSurrogateModel(t), model_name='ballot-surrogate.v1').model_dump_json(indent=2))"
  ```
- **FO-6 re-baseline** (§3 floor):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table, fo6_rebaseline; print(fo6_rebaseline(build_meeting_table(Path('replays/ml_corpus/9p2i'))).model_dump_json(indent=2))"
  ```
- **The verdict** (§5):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table, run_surrogate_fidelity, fo6_rebaseline; from training.surrogate.fidelity import decide_go_no_go; from training.surrogate.ballots import BallotSurrogateModel; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); s=run_surrogate_fidelity(t, lambda: BallotSurrogateModel(t), model_name='ballot-surrogate.v1'); f=fo6_rebaseline(t); print(decide_go_no_go(s, f).model_dump_json(indent=2))"
  ```
- **Artifact provenance + frozen-weights reproduction** (refit is ULP-equivalent
  to the committed weights — byte-identical only on the recording platform — and
  the LOADED artifact reproduces the reported numbers):
  ```
  uv run pytest tests/training/test_surrogate_runner.py::test_committed_artifact_round_trips_and_provenance_holds tests/training/test_surrogate_runner.py::test_bakeoff_reloads_the_committed_artifact_and_reproduces_the_numbers -q
  ```
- **Predicted-ballot calibration** (§4, the surrogate's OWN channel):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table; from training.surrogate.fidelity import build_meeting_views; from training.surrogate.ballots import BallotSurrogateModel; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); test=frozenset(t.splits.test); v=build_meeting_views(t); m=BallotSurrogateModel(t); m.fit([x for x in v if x.seed not in test]); print(m.predicted_ballot_calibration([x for x in v if x.seed in test]).model_dump_json(indent=2))"
  ```

---

## 10. How downstream consumes this

- **Task 15.15** (the impostor bake-off): under this **NO-GO**, its training-time
  runner is **fallback (a)** — nothing trains against the surrogate (§5). The
  surrogate stays available to 15.15 as an **offline diagnostic only**, within the
  staleness cap; and regardless of any future GO, **every reported number is
  re-scored on a real meeting path** — surrogate-scored vs real-rescored columns are
  reported side-by-side where they diverge, and divergence is data, never collapsed.
- **Task 15.14** re-runs the Goodhart probe **under the surrogate meeting path** at
  15.15 time — a mis-calibrated SKIP/eject rate can hold the meeting-driven floors
  for the wrong reason (this surrogate **over-ejects**: 0 of 18 held-out skip
  meetings recognized), so the probe reports the surrogate's ejection/SKIP rate
  alongside its verdict.
- The additive `meeting_runner_factory` keyword on `run_tournament_eval`
  (`eval/balance_eval.py:228`) is the diagnostic seam: surrogate-driven tournaments
  produce standard reports at `$0`, with the default path byte-identical (existing
  balance-eval tests stay green untouched).

The mitigations are **all structural and all shipped here**: the staleness cap, the
pre-stated GO/NO-GO with the honest ceiling as denominator, re-grounding as a
documented operator recipe, and the bake-off's rule that final numbers are never
surrogate-scored — none weakened to make the verdict look better.
