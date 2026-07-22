# The conviction-economy model — dataset, fit, fidelity, GO verdict (Task 18.15)

**Task:** 18.15 (tasks/phase-18.md) — the training-signal instrument Phase 18 was
chartered around (audits/audit-phase-18-planning.md §2.3; owner-ratified locked
decision 1).
**Code:** `training/conviction/{dataset,model,fidelity}.py`;
tests in `tests/training/test_conviction_model.py`.
**Date:** 2026-07-21.
**Corpus:** `replays/ml_corpus/9p2i` — the baseline-6 re-record (Task 18.13,
PR #301): 150 games (seeds 1000–1149), 463 meetings, 302 ejections, committed
`splits.json` (seed mod 5 → 90 train / 30 val / 30 test games; fit side
train ∪ val = 367 meetings, test = 96 meetings).
**Committed artifact:** `training/artifacts/conviction/conviction-model.json`
(float-hex weights), sha256
`4841f8e02eb7b587237c5b88bc2d350c12c7a5b5ac5c7ae1481069235c7b2a47`
(sidecar `conviction-model.json.sha256`), staleness cap `max-uses.json`
(**52 481** = 143 × 367), machine-readable verdict `verdict.json` keyed to the
same sha.

**Verdict summary:** **GO**, taken on the FIRST held-out evaluation against the
pre-stated bar. Held-out per-meeting flag-count Spearman **0.578** ≥ 0.5, and
conversion recall **45/47 = 0.957** ≥ **0.6375** = 0.75 × (1 − 0.15), with the
voice-driven share (0.15) measured on the same held-out population as the
structural denominator. Consequence (pre-committed, machine-readable in
`verdict.json`): the fitness term SHIPS on both sides and the referee
pre-screen GATES real-path spend (18.16 wires both). The conviction model is
INDEPENDENT of the ballot surrogate (`training/surrogate/` untouched — the
18.15 designer ruling): two artifacts, two fences, two verdicts.

---

## 1. The pre-stated GO bar

Committed in the task contract (and in code as
`training/conviction/fidelity.py::CONVICTION_SPEARMAN_BAR` /
`CONVICTION_CONVERSION_CEILING_RATIO` + `decide_conviction_go`) BEFORE the
first held-out evaluation ran:

1. **Held-out per-meeting flag-count rank correlation (Spearman) ≥ 0.5** —
   over every test meeting, average ranks on ties (flag counts are small
   integers; ties are the norm). A rank correlation carries no unit the
   population could move, so this axis needs no population-relative rescaling.
2. **Conversion-prediction fidelity ≥ 0.75 × (1 − voice_driven_share)** — both
   sides measured on the SAME held-out population. Fidelity is the held-out
   RECALL on the actual testimony-backed-conversion meetings, called at the
   pinned P ≥ 0.5 threshold (fixed before the evaluation, never tuned against
   it). The recall form is the structural match to the ceiling: a conversion
   that formed from the current meeting's spoken narrative carries no
   pre-meeting physical signal, so a fenced model structurally cannot flag it
   — exactly as the honest ceiling bounds the ballot surrogate's top-1
   (`training/surrogate/fidelity.py::compute_honest_ceiling`). Precision and
   accuracy are reported beside recall, never substituted for it.

Pre-committed in the same breath: **NO-GO ⇒ diagnostic-only** — the fitness
term does not ship (structurally absent, not zero-weighted) and 18.16
integrates the pre-screen only as advisory. The staleness cap ships regardless
of the verdict.

## 2. The model + the feature fence

`g(pre-meeting typed state) → (expected flags minted, P(testimony-backed
conversion))`: one per-meeting standardized feature vector, two deterministic
numpy heads — a closed-form ridge (`np.linalg.solve`, λ = 1e-8) for the flag
count and a full-batch logistic (zeros init, 300 epochs, lr 0.3, no RNG — the
`Fo6Logistic`/`BallotPredictor` recipe) for conversion. Platform caveat
(verbatim from the surrogate): a refit is byte-identical on the recording
platform and ULP-equivalent elsewhere (numpy SIMD reduction grouping varies by
CPU); the COMMITTED bytes are the frozen ground truth the sha256 sidecar pins.

The 12 features (`CONVICTION_FEATURE_NAMES`), each derivable at `run_meeting`
time from `(meeting_id, trigger, state, agents)` — the provenance map
(`CONVICTION_FEATURE_PROVENANCE`) is asserted feature-by-feature by the
committed provenance test:

| feature | offline column (15.11 table) | live derivation at `run_meeting` |
|---|---|---|
| `alive_count` | living-roster size | `state.players[*].alive` |
| `meeting_index` | `meeting_index` | parsed off the orchestrator `meeting_id` |
| `max_suspicion`, `mean_suspicion`, `suspicion_margin`, `cells_at_gate` | non-self `belief_suspicion` cells | each agent's `suspicion_graph_for_meeting()` |
| `vent_witness_pairs`, `vent_witnessed_candidates` | voter-local `witnessed_vent` pins | `vent_witness_records_for_meeting()` naming the candidate |
| `kill_pin_pairs`, `kill_pinned_candidates` | voter-local `witnessed_kill` pins | the agent's own episodic kill-stamped `saw_player` records (see the seam note) |
| `body_proximity_pairs`, `body_proximity_candidates` | voter-local `body_proximity` pins | the agent's own episodic body/sighting records via the §6.3 Rule-1 read (see the seam note) |

(`cells_at_gate` counts non-self cells at/above the production
`DEFAULT_SKIP_CONFIDENCE_THRESHOLD` (0.60) — the §4.6 gate signal;
`suspicion_margin` is the top-1 − top-2 lead of the per-candidate max.)

**The kill/body serving seam (precision note, adversarially re-verified).**
The four kill/body features carry the GAME-LONG semantics of exactly the
channels the task contract's section ref defines as live-reconstructable (the
honest ceiling's `proximity_legible` flag sets,
`training/surrogate/fidelity.py:213-243`), grounded in the agent's own
append-only episodic store (audit §2.3 [VERIFIED] — the rows persist all
game). Two facts about today's serving surface, so the fit distribution is
never silently mis-served: the `SuspicionEntry.kill_or_vent_pin` /
`body_proximity` provenance channels carry only pins minted since the
previous meeting (the boundary roll folds older pins into the
undifferentiated `carried_hard` bucket —
`agents/memory/beliefs.py::SuspicionProvenance.carried`), and the raw
kill/body episodic rows have no `*_for_meeting` projection yet
(`sighting_records_for_meeting` excludes incriminating-action rows). The
runner-side consumer therefore needs the `vent_witness_records_for_meeting()`
twin for kill/body records — a firewall-clean one-accessor seam owned by the
18.16 integration (out of 18.15's file scope), to land BEFORE the pre-screen
serves live feature vectors.

Excluded BY DESIGN (the fence's other half, proven by the committed poison
test): the contradiction-flag structure and `contradiction_lift` (THIS
meeting's transcript — the LABEL side), the omniscient window stats
(`witnessed` / `isolation` / `seen_at_kill` / `task_submissions` /
`move_count` — inter-meeting event history the runner never sees; the
contract's "seen-at-kill" CHANNEL is not the omniscient `seen_at_kill`
column — audit §2.3 scopes the channel "from episodic memory", whose episodic
form is the voter-local witnessed-kill pin served as `kill_pin_pairs` /
`kill_pinned_candidates`, while the table column is a global room-occupancy
fact that lives in no agent's store), all ballot
and role/outcome columns (labels), and raw sighting-record supply — though
live-servable via `sighting_records_for_meeting()`, it has no verified offline
mirror in the 15.11 table (the table's co-presence counts are omniscient, not
per-voter episodic), so it enters only through the belief scalar's
corroboration folds rather than being fitted against an unverified
reconstruction. This is the conservative side of the fence: features the
deployed consumer can serve worse than the fit saw them would inflate the
verdict — the exact failure the 6-feature fence forbids.

### 2.1 The 17.10 walk re-validation (run BEFORE the fit, mechanically gated)

`fit_corpus_conviction_model` refuses to fit until
`measure_belief_render_parity` (the production-fold cross-check: real
`TacticalAgent`s fed reconstructed packets, read through the exact
`suspicion_graph_for_meeting()` accessor) comes back clean
(`require_clean_walk` — the `ConvictionWalkGateError` gate). Measured on the
baseline-6 corpus, 2026-07-21:

* **Fold fidelity: 0 raw mismatches, 0 trust mismatches** over **14 326**
  non-self cells (150 games, 463 meetings, 2 726 rows); max raw |Δ| 0.0.
* **J1 live-parity divergence** (the graduated render clamp — the live runner
  is served the CLAMPED `SuspicionEntry.suspicion`; measured, never assumed
  away): **141 divergent cells** across **130 rows** (113 fit-side / 28
  test-side), max |Δ| **0.06**. The conviction features read the raw
  fold-side scalar, so the live consumer sees at most a 0.06 shift on ~1% of
  cells — quoted here as the known live-parity delta.

## 3. The labels, mirrored (never imported)

The labels are exactly the quantities the 15.2 referee gates — the
Goodhart-adjacent seam — so `training/conviction` mirrors the
`eval/watchability.py` assembly from recorded bytes and never imports `eval.*`
(the committed AST-firewall test, entrant-style; 18.16 extends the harness-side
scan to this package). The two structural guards from the task contract hold:
no `eval/watchability.py` read, and 18.18 re-runs the Goodhart probe with the
conviction term live before any campaign selection leans on it.

* **`flags_minted`** = `len(detect_contradictions(transcript,
  roster=frozenset(ballot voters)))` + the persisted `vent_sighting` flags
  from the recorded contradictions. The detector is the production
  `meetings.transcript.detect_contradictions`, imported; only the eval-layer
  census assembly (`compute_supply_gauges` + `_persisted_vent_flag_count`) is
  mirrored. The two sources are disjoint (the re-derivation cannot mint a
  vent flag — its grounding channel is private), so no double count. The
  committed parity test proves the mirror integer-exact against the
  production census on both baseline-6 sample sets.
* **`testimony_backed_conversion`** — the observation-BACKED conversion
  (subject-aware, Task 15.19): a true impostor named by a non-self
  `AccusationClaim` where some accusing turn also carries a first-hand
  `SawPlayerObservation`/`SawVentObservation` whose subject IS the accused;
  converted when the meeting ejects exactly that subject. Roles ground truth
  via the deterministic engine re-seed (`seed_initial_state` — the
  `roles_by_seed` recipe without the eval import). Semantics pinned by
  synthetic-transcript tests (other-subject sightings never back; crew
  accused never count; self-accusation-only subjects never enter; body
  reports never back; vent sightings back).

Corpus census (baseline 6): **576 flags minted** over 463 meetings
(fit side 452 / test 124), **239 converting meetings** of **394
attempted-subject meetings** (fit 192 / test 47). Conversion is DENSE on
baseline 6 — the 18.11 CREW-ONLY package moved the economy the §3.1 census
found scarce at baseline 5.

## 4. Held-out fidelity — the first evaluation

Development discipline: all choices (the 12 features, both heads, epochs/lr,
the 0.5 conversion threshold) were frozen against fit-side-only evidence — a
train→val probe inside the fit side (Spearman 0.513, recall 44/50 = 0.880,
fit-side voice-driven share 0.223) — and the committed test split was then
evaluated ONCE, with the frozen weights that were committed. The numbers below
ARE that first evaluation (`ConvictionFidelityReport`, reproducible from the
frozen artifact — §9).

| channel | held-out (30 test games, 96 meetings) |
|---|---|
| flag-count Spearman | **0.5782** (bar 0.5) |
| flag MAE | 0.752 (context; the bar is rank-based) |
| conversion recall | **45/47 = 0.9574** (bar 0.6375) |
| conversion precision | 45/49 = 0.9184 |
| conversion accuracy | 90/96 = 0.9375 |
| confusion (tp/fp/fn/tn) | 45 / 4 / 2 / 45 |
| test ejections / reachable | 60 / 51 |
| **voice_driven_share** | **0.15** (the structural denominator) |

## 5. THE VERDICT: GO

| axis | measured | bar | pass |
|---|---|---|---|
| 1. flag-count Spearman | 0.5782 | ≥ 0.5 | **yes** |
| 2. conversion recall | 0.9574 | ≥ 0.75 × (1 − 0.15) = 0.6375 | **yes** |

**GO.** Honest notes: (a) the conversion head's strength rides the baseline-6
economy — conversion correlates with the physical evidence supply the features
see (vent/kill/body pins + the belief lead), which is exactly the §2.3 design
claim, but the bar re-reads on any future substrate (population-relative
doctrine — nothing here transfers as an absolute number); (b) the flag channel
clears its bar with less headroom (0.578 vs 0.5) — the flag label's variance
is dominated by roll-call-era alibi flags whose supply the fenced features see
only through co-presence pins, so the Spearman channel is the one to watch at
the 18.14-style re-grounds; (c) the voice-driven share on the held-out split
(0.15) is lower than the fit side's (0.223) — both are measurements on their
own populations, quoted per the anti-absolute-number doctrine.

## 6. The consequence mapping for 18.16 (machine-readable)

`training/artifacts/conviction/verdict.json` — the committed
`ConvictionGoVerdict`, sha-keyed to the weights it judged. 18.16 branches on
its fields, never on this report's prose:

* `verdict: "GO"`
* `fitness_term: "ships"` — the additive conviction term enters BOTH sides'
  inner fitness (impostor via `inner_episode_fitness`, crew via
  `crew_inner_episode_fitness`); under `"absent"` the term is structurally
  omitted, never zero-weighted.
* `prescreen_role: "gating"` — the referee pre-screen may gate real-path
  spend; under `"advisory"` it only ever advises.
* `model_role: "training-signal"` (vs `"diagnostic-only"`).

The gate/reward boundary stays intact: the term is a REWARD-side prediction
from tactical facts (`training/bakeoff/harness.py:582-585` does not move), and
the model never reads, wraps, or re-derives `eval/watchability.py` scores.

## 7. The staleness cap (~143× rule)

`max-uses.json`: **52 481** predicted meetings = 143 ×
**367** fit-side meetings (`derive_conviction_max_uses` — the Task-17.10 rule
applied to THIS artifact; the constant is restated locally because the
conviction model and the ballot surrogate are independent artifacts whose caps
must never silently retune each other). Unit: one metered
`ConvictionEconomyModel.predict` call is one use; `ConvictionUseCounter` keys
on the weights sha256, is cumulative per run, and raises
`ConvictionStalenessExceededError` at the cap. 18.16 owns ONE counter per run,
threaded through both fitness sides and the pre-screen.

## 8. The re-grounding recipe (run at every substrate change)

1. Record the fresh corpus (`bash scripts/record_ml_corpus.sh --set 9p2i`) and
   land its adopting record per the standing cadence rules.
2. `fit_corpus_conviction_model(Path("replays/ml_corpus/9p2i"))` — the walk
   re-validation runs FIRST and refuses a drifted fold (0 raw mismatches or
   no fit); record the returned parity's numbers in §2.1's format.
3. `write_conviction_model_artifact(model, Path("training/artifacts/conviction"),
   max_uses=derive_conviction_max_uses(<fit-side meeting count>))`.
4. `run_conviction_fidelity(table, model=model)` then
   `decide_conviction_go(report, weights_sha256=<sha>)` then
   `write_conviction_verdict_artifact(verdict, <artifact dir>)` — the verdict
   is taken on that FIRST held-out evaluation, whichever way it reads.
5. Commit weights + sidecar + cap + verdict + the refreshed report together;
   re-pin the committed-artifact tests' numbers.

## 9. Reproduce

Every figure re-derives from committed bytes (each one-liner writes nothing):

```
uv run python -c "from pathlib import Path; from training.surrogate.dataset import measure_belief_render_parity; print(measure_belief_render_parity(Path('replays/ml_corpus/9p2i')).model_dump_json(indent=2))"
uv run python -c "from pathlib import Path; from training.conviction.dataset import build_conviction_table; t = build_conviction_table(Path('replays/ml_corpus/9p2i')); print(t.meetings_total, t.ejections_total, t.flags_minted_total, t.conversions_total, t.conversion_attempts_total)"
uv run python -c "from pathlib import Path; from training.conviction.model import load_conviction_model_artifact; from training.conviction.dataset import build_conviction_table; from training.conviction.fidelity import run_conviction_fidelity; m, sha = load_conviction_model_artifact(Path('training/artifacts/conviction')); r, _ = run_conviction_fidelity(build_conviction_table(Path('replays/ml_corpus/9p2i')), model=m); print(r.model_dump_json(indent=2))"
uv run python -c "from pathlib import Path; from training.conviction.fidelity import load_conviction_verdict; print(load_conviction_verdict(Path('training/artifacts/conviction')).model_dump_json(indent=2))"
uv run pytest tests/training/test_conviction_model.py -q
```

## 10. How downstream consumes this

* **18.16** loads the artifact (`load_conviction_model_artifact`), the cap
  (`load_conviction_staleness_cap` → `ConvictionUseCounter`), and the verdict
  (`load_conviction_verdict`), and wires the fitness term + pre-screen per §6.
  Public seam: `ConvictionEconomyModel` / `build_conviction_table` /
  `decide_conviction_go` (signatures stable per the task contract). Before
  the pre-screen serves LIVE feature vectors, 18.16 lands the kill/body
  episodic-record accessor (`vent_witness_records_for_meeting()`'s twin — the
  §2 seam note), so the four kill/body features are served with the same
  game-long semantics they were fitted on.
* **18.18** re-runs the Goodhart probe with the conviction term live before
  any campaign selection leans on it (the standing rule for a grown
  training-signal role).
* Any substrate change re-runs §8 — this verdict, like every number here, is
  a baseline-6 measurement, not a transferable constant.
