# The meeting training table + surrogate fidelity harness — re-baselining FO-6 honestly

> Task 15.11 (`tasks/phase-15.md`). Anchored to
> `audits/post-phase-14-ML-training-signal.md` §2 (what is broken), §5.4–5.5 (the
> belief-fold features + the fidelity protocol + the honest ceiling), §7.2 (the
> flat per-meeting table). Code: `training/surrogate/dataset.py` (the table
> builder) + `training/surrogate/fidelity.py` (the by-game CV harness + the honest
> ceiling + the FO-6 re-run). Reproduce every figure below with
> `uv run python -c "from pathlib import Path; from training.surrogate import
> build_meeting_table, fo6_rebaseline; print(fo6_rebaseline(build_meeting_table(Path('replays/samples/9p2i'))).model_dump_json(indent=2))"`.

This is the supervised substrate the ballot surrogate (Task 15.13) trains on and
every meeting model is judged against. It is reconstructed **offline** (no LLM call,
no network) and **replay-deterministically** from the committed **baseline-3** bytes
(`replays/samples/{9p2i,4p1i}`, re-recorded at Task 15.7). Everything here is a
**measurement** of those bytes, not a target.

---

## 1. The table (`training.surrogate.dataset`)

Row grain is one row per **(meeting, voter)** — the roster is read off
`result.ballots` (every living participant casts exactly one ballot,
`meetings/manager.py:2823`), which fixes the candidate universe. Each row carries
the voter's ACTUAL recorded ballot `{target, confidence, primary_reason_id}` and its
per-candidate feature view (one `CandidateFeatures` per living player). Reconstruction
mirrors `eval.funnel._walk_game` (re-seed → `advance_tick` → verify every state hash
→ `apply_meeting_result`); a drifted set fails loud.

| Set | Games | Meetings | Ejections | Skips | Ballots = **rows** |
|---|---:|---:|---:|---:|---:|
| **9p2i** (9 players, 2 impostors) | 50 | 139 | 109 | 30 | **851** |
| **4p1i** (4 players, 1 impostor) | 50 | 39 | 26 | 13 | **117** |

Counts are **derived** from each set's assembled tournament report
(`eval.validity.assemble_tournament_report`), never hard-coded, and the
reconstruction is asserted to reproduce them exactly — **every recorded ballot joins
exactly one feature row (100% join rate)**. The table rebuilds byte-identically
(`model_dump_json()` pinned by the determinism test).

### Feature columns (all offline)

The single biggest upgrade over FO-6's six raw physical counts is the **pre-meeting
belief-fold rendered suspicion**. The belief fold in `agents/memory/beliefs.py` is
deterministic over recorded events and needs no LLM;
`meetings.manager.extract_belief_evidence` (the `derive_belief_evidence` derivation,
roster off `result.ballots`) re-derives each meeting's public evidence
(accused / corroborated / contradicted / testimony). Folding that evidence over
**PRIOR** meetings through the real
`agents.memory.beliefs.apply_meeting_evidence_rules` (`phase=None` — the exact
persistent post-meeting absorb the orchestrator runs) reconstructs each voter's
cross-meeting suspicion accumulator **without this meeting's transcript** (a
training-time surrogate has no LLM, hence no current transcript). At the first
meeting no prior evidence has folded, so every candidate reads the neutral 0.5 prior;
by later meetings the accumulator has moved — this is the "0.60–0.69 rendered
suspicion" band §2.2 says the LLM votes on.

Alongside it, per candidate: the **contradiction-flag structure** (`strong_flags` /
`weak_flags` / `vent_flags` — the Task-15.4 `vent_sighting` role-proving flag in its
own band — plus `contradiction_lift`, the meeting's RENDERED vote-time lift computed
by the real `apply_contradiction_rule` with THIS meeting's recorded transcript
threaded exactly as the production vote path threads it: one delta per (subject,
claim) group, capped at one strong flag's worth, so duplicate flags of one claim
never stack, and a strong flag riding a self-refuted alibi renders the WEAK 0.08 —
the Task-14.10 downgrade, e.g. 9p2i seed 33 meeting 1),
**sighting / co-presence** (`witnessed` / `isolation`), **kill-proximity**
(`seen_at_kill` co-presence proxy), the **VOTER-LOCAL eyewitness pins** `witnessed_kill`
(+1.0) and `witnessed_vent` (+0.5) read straight off `KilledEvent` / vent-event
witnesses — exposed only to the row whose voter actually saw the act, never a
bystander and never leaked to a non-witness voter — **body-proximity**, **reporter
identity**, and **task-cadence / movement** (`task_submissions` / `move_count`,
counted from ACCEPTED `TaskProgressed`/`TaskCompleted` and `Moved` engine events —
a rejected replay intent emits neither and never counts). Roles
ground truth (`is_impostor` / `is_ejected`) comes from the tournament report — raw
replays are role-free by firewall design — and is a **label**, never a predictive
input.

**Decision (documented):** the belief scalar folds only the cross-meeting MEETING
evidence; the perception-time hard pins the real store also folds at ingest (a
witnessed vent → +0.5, a witnessed kill → +1.0) are surfaced as their OWN first-class
columns (`vent_flags`, `witnessed_kill`, `witnessed_vent`, `seen_at_kill`) rather than
folded into the single suspicion scalar. These eyewitness pins are **voter-local** —
production stamps `action="kill"` / `"vent"` only for the witnessing agent's belief, so
a pin is exposed only to a row whose voter is in the event's crew-witness set (a global
flag would leak private evidence to every voter and inflate the ceiling; the honest
ceiling ORs the pin across a meeting's voters — the strongest signal any voter holds).
Reconstructing the full per-agent belief store exactly would require re-driving the
`ObservationService` + memory-store pipeline; as columns the surrogate weights each
channel independently — and the honest ceiling folds the eyewitness pins back in at
their real weights (kill +1.0, vent +0.5) with the contradiction lift capped at one
strong flag's worth (`MEETING_CONTRADICTION_LIFT_CAP`) and clamped to [0, 1], exactly
as `apply_contradiction_rule` renders — while the belief scalar stays a clean
deterministic function of the recorded meeting evidence. The scalar is therefore
the **cross-meeting accusation/testimony accumulator** — precisely the "voice
momentum" signal, and precisely what a physical-only surrogate (FO-6) lacks.

---

## 2. The fidelity harness (`training.surrogate.fidelity`)

Every meeting model is judged the SAME way (§5.5), and never on a single headline
number. Four channels, reported **together**, under **by-GAME cross-validation**
(never by-meeting — a game's cross-meeting belief state would leak between train and
test; the leakage test proves two meetings of one game never split across folds).
When a set ships a committed `splits.json` the harness honours it (validated first —
the fit and test seed sets must be disjoint, together partition EVERY recorded game
(including no-meeting games), and each side must carry at least one scoreable
meeting, else it fails loud so a corpus mistake cannot silently leak a game across
the fold, drop a game from both sides, or score nothing / an untrained model while
looking like a valid held-out run); otherwise it derives K=5 deterministic by-game
folds.

- **top-1 / top-2** ejected-target ranking (the continuous suspicion-rank signal).
- **SKIP-vs-eject** decision accuracy (the decision FO-6 failed at).
- **Brier / ECE** on TWO channels: the model's per-candidate ejection confidence, AND
  the recorded **ballot confidences** — each non-SKIP voter's stated confidence vs
  whether its named target was ejected (the WOLF vote-prediction channel, ~0.26–0.29,
  arXiv:2512.09187). Brier is numeric-probability fidelity, ranking is ordering —
  report both (arXiv:2504.18278). On baseline-3 9p2i the recorded ballot confidences
  score **Brier 0.211 / ECE 0.120** over 753 non-SKIP ballots (4p1i: 0.232 / 0.232).

The harness is model-agnostic (a `MeetingModel` = `fit` + `predict`); every
prediction is validated (ranking a permutation of the living candidates, ejected a
candidate or SKIP, probabilities in [0, 1]) before scoring, so a broken model fails
loud instead of producing meaningless metrics. The 15.13 ballot surrogate implements
the same interface and its per-candidate ejection probability derives from predicted
ballots fed to the **real** deterministic tally (`meetings.voting.tally_ballots`, skip
threshold 0.60). The GO/NO-GO wiring on top of this report is Task 15.13's region.

---

## 3. FO-6 re-baseline — the true prior, honestly (§2.1, §5.2)

The FO-6 logistic (`experiments/lab/ml_spike/fo6_learned_vote_surrogate.py`) is
**re-run** here (re-implemented as `Fo6Logistic`; the spike is mypy-excluded and
never imported): the same six LLM-free physical features
`{witnessed, isolation, seen_at_kill, is_reporter, meeting_index, alive_count}` per
candidate, a deterministic standardized logistic, its SKIP threshold tuned on train,
probability ties broken toward the smallest player id (the spike's own
first-strict-max convention, shared by the ranking and the decision head) — now
under **by-game 5-fold CV** across all 50 games (the spike used one 35/15 split).

| Set | top-1 | top-2 | decision acc (binary) | always-eject baseline | ejection Brier/ECE | ballot Brier/ECE | binary head |
|---|---:|---:|---:|---:|---:|---:|---|
| **9p2i** | **23.9%** (26/109) | **42.2%** (46/109) | **35.3%** | 78.4% | 0.107 / 0.008 | 0.211 / 0.120 | **collapses to always-SKIP** |
| **4p1i** | 69.2% (18/26) | 88.5% (23/26) | 64.1% | 66.7% | 0.154 / 0.102 | 0.232 / 0.232 | SKIP-biased (not collapsed) |

(Decision accuracy is the BINARY eject-vs-skip decision — right when the model's
eject/skip *choice* matches, regardless of which player it named; the exact-target
accuracy is the separate top-1 channel. The **ejection** Brier/ECE calibrate FO-6's
per-candidate ejection probability; the **ballot** Brier/ECE calibrate the RECORDED
voters' confidences — the WOLF channel — and are model-independent, reported for every
model as the ground-truth reference.)

The spike's headline **"FO-6 top-1 64% / top-2 82%"** was measured on 9p2i in the
spike era. On the committed baseline-3 9p2i it is **23.9% / 42.2%** under by-game CV —
matching the audit's re-record regression to "26% / 43% on baseline 2" (§2.1). The
small **4p1i** set still shows a high headline (69.2%) — that is the *misleading*
single number the audit warns about, not a recovery: on a 4-player set the ranking
problem is trivially small (≤3 candidates), and its decision head is still below the
always-eject baseline.

**The always-SKIP collapse, made explicit (9p2i):** the tuned binary head predicts
SKIP on **78 of 109 true ejection meetings** and reaches only **35.3%** binary
eject-vs-skip accuracy — *worse than the trivial always-eject constant (78.4%)*. The
single top-1 number hid this. The SKIP/eject decision is testimony/plurality driven and **absent
from physical features**, exactly as §5.2 predicts; this is why §5.3's rebuild
predicts BALLOTS and feeds the real tally instead of a binary ejection head.
(`degenerates_to_skip = True` trips only on 9p2i; the flag requires both a
majority-SKIP head AND sub-baseline accuracy, so the small 4p1i set is not falsely
flagged.)

---

## 4. The honest ceiling — a measurement, not a target (§2.2)

The crew's entire deduction signal under same-room-only vision is physical
(sightings, kill-proximity) plus the cross-meeting belief accumulator. A conviction
that formed from THIS meeting's spoken narrative — no flag, no proximity, no
pre-meeting suspicion lead — is invisible to a training-time surrogate. The ceiling
measures that: over the SCORED ejection meetings (the same held-out population every
other channel reports on — all meetings under K-fold, the test games under a
committed split), the share whose ejected target is the **strict (unique) argmax** of
the best-case reconstructed physical+belief suspicion (the sharpest ranking a
physical+belief surrogate could form from the pre-meeting bytes, using the real
belief-fold deltas — the voter-local eyewitness pins at +1.0 kill / +0.5 vent, the
table's `contradiction_lift` column RENDERED by the real `apply_contradiction_rule`
(one delta per (subject, claim) lift group, capped at one strong flag's worth),
clamped to [0, 1], and the accusation accumulator). A flat tie (an early meeting, no
prior evidence, no flag) is not uniquely rankable and correctly counts as unreachable.

| Set | **max achievable top-1** | **voice-driven share** | reachable | flag on target | proximity/eyewitness on target | strict belief-lead |
|---|---:|---:|---:|---:|---:|---:|
| **9p2i** | **65.1%** | **34.9%** | 71/109 | 78/109 | 82/109 | 15/109 |
| **4p1i** | 84.6% | 15.4% | 22/26 | 21/26 | 24/26 | 0/26 |

Read the 9p2i row as: **no physical+belief surrogate can exceed ~65% top-1 on this
corpus**, and **~35% of ejections are structurally voice-driven** — they formed from
the current meeting's narrative and cannot be seen without the LLM. FO-6's achieved
**23.9%** sits far below the **65.1%** ceiling: the gap is the belief accumulator and
the flag channels FO-6's six raw counts never use (the surrogate's headroom, Task
15.13), while the ceiling itself is the honest cap the plan does not chase. §5.5's two
responses follow directly: use the surrogate for the physically-legible component and
a periodic real-LLM selection gate for the rest, and lean the training reward on the
tactically-reachable signals that do not depend on the meeting outcome (§3.2).

---

## 5. How downstream consumes this

- **Task 15.12** records the frozen ML-calibration corpus and commits a `splits.json`
  the table builder reads unchanged (the builder takes any replay-set directory).
- **Task 15.13** trains the ballot-prediction surrogate against this table and gates
  it on THIS harness (top-1/top-2 + SKIP-vs-eject + Brier/ECE, by-game CV), with the
  honest ceiling as the north star and the FO-6 row as the floor to beat.

The stale spike conclusion is banner-marked at its source
(`experiments/lab/report-ml-spike.md`).
