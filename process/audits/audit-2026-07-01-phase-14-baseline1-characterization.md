# Phase-14 baseline-1 characterization — the model DRIVES the substrate; the problem INVERTED to over-conviction

**Date:** 2026-07-01 (measurement completed 2026-07-02)
**Task:** 14.8 — characterize baseline 1 (the R-gate as a MEASUREMENT, per the Phase-14 charter) + the
concrete 14.10/14.11 fix specs.
**Set:** `replays/samples/9p2i` (50 games / 152 meetings / 891 ballots / 631 turns) +
`replays/samples/4p1i` (50 games / 39 meetings), the Task-14.7 re-record (PR #213).
**Model:** `Qwen/Qwen3-32B` (Featherless, both call kinds, non-thinking, `fail_loud`, `json_object`, $0).
**Substrate:** all four Phase-13.5 levers ON (stamped into MANIFEST `flags` + replay `game_over`);
prompt set `qwen3_32b.v3`.
**Provenance tuple:** `replays/samples/{9p2i,4p1i}` @ recording sha `364f845`, `Qwen/Qwen3-32B`.
**Grounding:** every number below is a fold over the committed artifacts —
`tournament-eval-report.json` (both sets), `results-rubric-score.json` (9p2i + lab),
`experiments/lab/results-rubric-geomean.json`, `experiments/lab/results-substrate-ablation.jsonl`
(new, this task), and the replay JSONL bytes — not session memory. The rubric JSONs were re-derived
from the committed bytes during this audit and reproduce **byte-identically** (no number retrofit).
**Verdict in one line:** the new model **drives** the corrected substrate the 9B could not (R1 3→27,
impostor win 84%→32%, R7 7%→28%) — so the Phase-13 information-ceiling hypothesis is **REVISED, not
confirmed**: the ceiling bound impostor *concealment*, but the live binding constraint was crew
*conversion*, and conversion didn't just recover, it **overshot into over-conviction** (ejection
accuracy 0.566; 53 crew mis-ejects; a 5-row crew railroad) fueled by factually-false testimony on both
sides of every flag.

---

## 1. The R-gate scorecard — measurement, not gate (9p2i, vs the final-9B baseline)

| Gate term (13.12 definition) | final-9B (audit 2026-06-25) | baseline 1 | read |
|---|---|---|---|
| **R1 eject-decided win share** | 3/50 (6%) | **27/50 (54%)** | ✅ up 9× — the meeting DECIDES |
| R4 wrong-ejection games (floor: flat ≤ +2) | 4 | **39** (53 crew mis-eject meetings) | ❌ **+35 — the inversion headline** |
| Impostor win (floor ≥ 14%) | 84% (42/50) | **32% (16/50)** | ✅ floor holds; crater reversed |
| R7 strong-evidence meeting share | 13/195 (7%) | **43/152 (28%)**, >0 in 32/50 games | ✅ lit set-wide |
| geomean ranks eject-decided > stopwatch | top-3 = the 3 eject-decided | eject-decided median 61.3 vs stopwatch max 43.5; **25/27 above every stopwatch** | ✅ with one honest caveat (§1a) |

Supporting rows (same bytes): ejection accuracy **0.566** (69 impostor / 53 crew of 122 ejections —
~43% of ejections take out crew); meeting rate 1.00 with 152 resolved meetings (9B: 195 meetings,
177 SKIP / 18 eject); skipped 30 / ejected 122 (eject rate 80% vs the 9B's 9%); genuine-class
conversion 32/48 = 0.667; win split CREW 34 / IMP 16; reason histogram
`{CREWMATE_EJECT: 27, IMPOSTOR_PARITY: 16, CREWMATE_TASKS: 7}`. 4p1i: R1 26/50, ejection accuracy
0.788 (26 imp / 7 crew), impostor win 24%, zero defaulted turns.

The phase charter (owner decision 2026-06-25) makes this a measurement on a VALID baseline, never a
pass/fail gate — and the measurement is unambiguous: **the mechanism converts under the new model.**
The 9B-era failure mode (a voter at suspicion 1.00 over the 0.60 gate with the meeting still SKIPPED)
is gone. What replaced it is §2's defect.

### 1a. The geomean caveat (the referee catching the defect)

Two of the 27 eject-decided games (seeds 12, 21) score **0.0** — floored by the 13.15 rubric's own
railroad-ejection floor (a crewmate ejected on flag-stacked/below-gate evidence), so the strict
"every eject-decided above every stopwatch" reading is false (`all_eject_decided_above_all_stopwatch:
false`). Every UN-floored eject-decided game outranks every stopwatch game. Six games floor in total
(seeds 2, 12, 21, 24, 26, 31), all on crew-ejection quality, none on firewall/determinism/friendly-fire.
The held-out referee is flagging exactly the over-conviction defect this audit characterizes — that is
the term working, and it is why the phase does not close on baseline 1.

---

## 2. Railroad-discounted R1 — how much of 27 is genuine deduction

The 5 pinned railroad rows (`tests/meetings/test_manager.py::known_railroad`) live in 4 games:

| pinned meeting | crew subject (flags) | meeting outcome | game outcome |
|---|---|---|---|
| seed-13 m0 | p-7 (2) | EJECTED (innocent) | CREWMATES / **CREWMATE_EJECT** |
| seed-16 m0 | p-6 (4) | EJECTED (innocent) | CREWMATES / **CREWMATE_EJECT** |
| seed-28 m0 | p-3 (5), p-6 (2) | SKIPPED (railroaded to 1.0, no eject) | IMPOSTORS / IMPOSTOR_PARITY |
| seed-44 m1 | p-1 (9) | EJECTED (innocent) | CREWMATES / CREWMATE_TASKS |

Discounting every eject-decided game whose win path contains a pinned railroad meeting removes seeds
13 and 16 (seed-28 lost, seed-44 won by tasks, so neither contributes to R1):
**railroad-discounted R1 = 25/50** — the pinned rows account for only 2 of the 24-game R1 lift, so the
headline is overwhelmingly genuine conversion, not the pinned pile-ons.

The wider pile-on question (for 14.12 to re-measure): of the 122 ejections, the ejectee carried ≥2
same-meeting flags in 32/69 impostor (46%) and 26/53 crew (49%) cases — the railroad *signature* is
role-blind, so "fewer stacked-flag convictions" alone cannot be the 14.10 success metric (it would cost
impostor convictions one-for-one). 12 impostor and 22 crew ejections carried ZERO flags on the ejectee
(prior-carry / witness-chain / voice-driven convictions). The honest 14.12 comparison pair is:
**railroad-discounted R1 (25) + ejection accuracy (0.566)**, not raw R1.

---

## 3. The 10.1 cap-bypass diagnosis — the exact mechanism (14.10's fix spec input)

Reproduced from the committed bytes by re-running the EXACT production vote-time fold
(`apply_contradiction_rule` → pre-vote `apply_meeting_evidence_rules` → the 13.14 joint cap
`min(lifted, prior + 0.3)`), seeded from each voter's reconstructed meeting-open beliefs (the loader's
memory walk under the stamped all-ON substrate). The reproduction is **exact for every voter row in
every pinned meeting AND set-wide: 2482/2482 recorded vote-prompt suspicion rows match** (4p1i:
167/167) — the fold model below is the recorded behavior, not an approximation.

**Mechanism (three compounding parts, none of which is an arithmetic cap failure):**

1. **The caps HOLD.** In all 5 pinned rows the same-meeting Rule-2 lift is capped at +0.30 — even
   seed-44's 9 flags dedup to ONE `contradiction_lift_key` group (one greedy alibi vs 9 sightings), and
   seed-16's two groups (0.30 + 0.08 = 0.38 uncapped) cap at 0.30. The flag COUNT (2–9) is a
   diagnostic signature, **not** the causal variable: one STRONG `alibi_vs_sighting` group already
   saturates the whole per-meeting budget.
2. **One strong group gate-crosses the ENTIRE roster at once.** The saturated +0.30 lands identically
   in every voter's graph: neutral prior 0.50 → rendered **0.80 ≥ the 0.60 §4.6 gate** → a roster-wide
   MUST-vote verdict on the flagged subject. Every pinned row shows every voter at exactly 0.80 —
   there is no per-voter independence requirement anywhere in the fold, so a single public flag group
   moves all graphs in lockstep. This is what converts a garbled alibi into a 5–6-vote pile-on.
3. **The Rule-1 body-proximity prior compounds to certain-guilt.** The voters rendering **1.00** are
   exactly those whose meeting-open prior on the subject was **0.70** = 0.50 + `BODY_PROXIMITY_
   SUSPICION_DELTA` (+0.20, first sighting of the body with the subject co-present — Phase-10-era
   Rule 1, NOT a 13.5 lever): 0.70 + 0.30 clamps at 1.00. In ALL 5 pinned rows the 1.00-renderers are
   IMPOSTORS (they are at the scenes they created, so their graphs carry the bystander lift) — the
   render then hands them a "certain guilt" row on an innocent to vote on.

**The fuel is factually-false testimony, verified against engine truth:** in ALL 5 pinned rows the crew
subject's OWN alibi is false (wrong room for part or all of the span — the greedy-span defect;
seed-44 m1 p-1's `CAFETERIA t5-14` vs their actual EAST_HALL t5 / ENGINEERING t6 / STORAGE t7–13 /
ENGINEERING t14 walk is the worked example). Set-wide, of flagged EJECTED subjects: **59/59 (100%) of impostor and 32/33 (97%) of crew
alibis are factually false**, and **47% (crew) / 67% (impostor) of the refuting sightings are
THEMSELVES false**. The detector and caps are working on garbage-in: conviction currently rides on who
garbled their testimony into a flag, and impostors always garble (they must lie) while innocent crew
garble ~10% of the time (§4 defect 1) — which is the entire 0.566-vs-1.0 gap.

### 3a. The 14.10 fix spec (measured, with the over-damping guard priced)

Recommended shape — two complementary bounds behind the new default-OFF lever
(`ENV_EVIDENCE_QUALITY_LIFT` / `evidence_quality_lift_enabled()`, the 13.5 pattern), registered in
`substrate_flag_snapshot()` / `SUBSTRATE_FLAG_KEYS` so 14.12's recording stamps it:

1. **Certain-guilt exclusion (the tripwire-restoring bound).** The transient same-meeting lift
   (contradiction + testimony spread) must never RENDER at the 1.0 clamp: extend the 13.14 joint cap to
   `min(lifted, prior + 0.3, CONTRADICTION_RENDER_CEIL)` with `CONTRADICTION_RENDER_CEIL` just below
   the clamp (e.g. 0.97) for subjects whose lift is flag/testimony-driven, EXEMPTING first-hand
   conclusive observation (a witnessed kill/vent pin, which legitimately reads ~1.0). Zero conversion
   cost (every 0.97 stays a MUST-vote); it removes the false "certain guilt 1.00" rows the model reads
   (which also feed the flat-0.95 ballot confidences) and restores the 14.12 tripwire semantics: no
   crew row at 1.0 from same-meeting stacks, per construction.
2. **Evidence-class weighting — the sloppy-testimony downgrade.** A contradiction group whose refuted
   alibi is SELF-refuted by the subject's own same-turn `completed_task` observation (mechanically
   detectable from the transcript at fold time) contributes the WEAK delta (0.08), not STRONG (0.30).
   Measured incidence: **0/57 flagged impostor ejections** vs **6/31 flagged crew ejections** (and 2/5
   pinned rows, including both worst-by-flag-count: seed-16, seed-44) — i.e. on this set the class
   costs ZERO impostor convictions and would have kept seed-16/seed-44's rosters sub-gate
   (0.50 + 0.08 = 0.58 < 0.60; only the 0.70-prior voters reach 0.78, short of a plurality).
3. **Explicitly rejected by measurement** (do NOT implement):
   - *Witness-count weighting* — an ANTI-signal on these bytes: crew mis-ejects have MORE independent
     refuting witnesses than impostor convictions (≥2 witnesses: 61% crew vs 40% impostor), because an
     honest greedy alibi is contradicted by everyone who really saw the subject.
   - *Requiring ≥2 strong lift-key groups to gate-cross* — over-damping: **54/57** flagged impostor
     ejections ride exactly ONE lift-key group (30 with one strong group), so a ≥2-group requirement
     would forfeit most of R1's fuel. (The remaining 25 impostor flagged-ejections crossed on weak-only
     flags + carry, untouched by group gating either way.)

The seed-44 m0 canary from the 14.10 contract stands: genuine multi-witness catches must still convict
with the lever ON — bound (1) costs none, bound (2) costs zero on this set by construction. The
residual mis-eject channel (pinned rows 13/28, honest-looking-but-false alibis with no self-refutation)
is fuel-limited, not fold-limited — it is 14.11's target, and the ablation confirms no substrate lever
feeds it (§5).

---

## 4. The 14.11 v4 targets — the measured per-defect counts baseline 2 must beat

All on the committed 9p2i bytes (891 ballots / 631 turns / 505 accusation claims / 295 self-alibis):

| # | defect (v4 fix) | measured baseline-1 count | measurement definition |
|---|---|---|---|
| 1 | **greedy/false self-alibis** (alibi discipline) | **30/295 self-alibis (10.2%)** self-contradicted by the speaker's OWN same-turn task observation; 97–100% of flagged ejectee alibis factually false vs engine truth | alibi span contains own `completed_task` tick in a different room; engine-truth check via reconstruction |
| 2 | **invalid-target ballots** (dead-roster salience) | **27** ballots (`INVALID_VOTE_TARGET_MARKER`) | marker census over `rationale_text` |
| 3 | **invalid `primary_reason_id`** (real `turn_id` worked example) | **20** ballots (`INVALID_REASON_ID_MARKER`) | marker census; #2 + #3 = the 47/891 guard-normalized headline (full guard census incl. redirects/teammate/parse: 66) |
| 4 | **confidence 1.0 accusations** (calibration rubric) | **64/505 (12.7%)** accusation claims at exactly 1.0; claim ECE 0.347, ballot ECE 0.272 (0.7–0.8 ballot bin: actual impostor rate 0.42 vs mean confidence 0.75) | claim/ballot confidence census + committed calibration report |
| 5 | **observation dumping** (curation: 3–5 probative rows) | **47% (crew) / 67% (impostor) of flag-cited sightings factually false**; 24 defaulted turns + 3 defaulted votes — ALL validation-triggered (schema failures/rambles at the frozen caps), none literal timeouts | engine-truth check of flag-cited observations; `deadline_default` failed-call census |
| 6 | **template rationales** (voiced rationale) | **320/891 (35.9%)** of ballots open with the one literal "p-N's alibi …" template family (largest exact-string class 12; alibi-contradiction phrasing family overall: 49.5%) | marker-stripped rationale clustering (player ids/rooms/digits collapsed) |
| — | missed-deadline turns (the #213 carry) | **23** transcript markers (`(missed deadline; no turn submitted)`); the report's `cap_defaulted_turns` = 24 (the 24th is seed-45 m1's defaulted OPENING, which landed as an `[opening degraded to unsure …]` row instead of the marker) | transcript + failed-call census, reconciled |

Note on defect 5/the caps: all 27 `deadline_default` rows are `(validation)`-triggered — the model
fails schema or rambles to the cap; the caps stay FROZEN (the 9.5 lesson) and the fix is output
discipline, not latency or budget.

Fixes 1 and 5 are the railroad's fuel line (§3): v4 alibi discipline should collapse the crew side of
flag supply (innocent false alibis are a prompt defect) while leaving the impostor side (structural
lying) intact — the measurable expectation for 14.12 is defect-1 → ~0 with impostor flagged-alibi
falseness staying ~100%, ejection accuracy up from 0.566 with R1 holding near 25–27.

---

## 5. The per-lever substrate ablation ($0, offline — `experiments/lab/results-substrate-ablation.jsonl`)

Method: the committed baseline is STAMPED all-ON, so each toggled cell re-derives the memory/belief
reconstruction under a DELIBERATE substrate mismatch via the Task-14.8 analysis-only loader override
(`ReplayLoader(..., allow_substrate_mismatch=True)`; default OFF — serving/verify still fail loud; every
JSONL row records the deliberate mismatch). Recorded outcomes cannot move offline; each cell measures
the lever's contribution to the EVIDENCE SUBSTRATE (meeting-open standing beliefs) and to the
would-have vote-time fold (the §3 production fold seeded from the cell's priors with the recorded
flags). Validation anchor: the all-ON cell reproduces the recorded vote-prompt rows **2482/2482**
(9p2i) / **167/167** (4p1i) and re-derives exactly the 5 pinned railroad rows.

| cell (9p2i) | held belief cells | impostor cells ≥1.0 | MUST-vote verdicts | railroad rows | lever-firing |
|---|---|---|---|---|---|
| all-ON (control) | 2728 | 167 | 656/891 | 5 (the pinned set) | 17,115 reported rows; 10,784 movement rows |
| testimony OFF | 2347 (−381) | 167 | 656 | 5 | reported rows → 0 |
| witnessed-kill OFF | 2723 | **160 (−7)** | **653 (−3)** | 5 | 7 impostor kill-pins gone |
| movement OFF | 2728 | 167 | 656 | 5 | movement rows → 0; reported rows RISE to 20,447 (render-budget competition) |
| unfreeze OFF | 2728 | 167 | 656 | 5 | no reconstruction delta (live-only lever) |
| all-OFF | 2342 | 160 | 653 | 5 | both supplies → 0 |

Per-lever reads (all consistent with adopting the full default-ON set — **14.9 is confirmed**):

- **`testimony_as_content`** — pure SUPPLY: 17,115 `[meeting]`-tagged reported rows in the rendered
  memories (+381 held belief rows via the alibi map) with ZERO deterministic gate/fold movement (the
  13.5.2 hard invariant — never touches the scalar graph — holds under measurement). Its conversion
  effect is what the MODEL does with richer prompts, i.e. live-only; baseline 1 is the live evidence.
- **`witnessed_kill_evidence`** — the only lever that moves the deterministic fold, and only
  truthfully: 7 impostor-only standing cells at the 1.0 pin (zero crew — only impostors kill + the §4.7
  teammate firewall), +3 MUST-vote verdicts. Its DETECTOR half (kill-scene `alibi_vs_physical`
  intensification) fired **1× in 152 meetings** (re-run ON vs OFF: 702 vs 701 flags; 0× at 4p1i; 0× in
  the 9B smoke) — **effectively UNMEASURED at n=1, not a negative result**; it needs a richer scenario
  (more co-located kills) than the committed seeds produce.
- **`movement_perception`** — pure SUPPLY: 10,784 first-hand movement rows + live `last_seen` belief
  suffixes; no fold movement. Toggling it OFF frees render budget that testimony rows then fill
  (17,115 → 20,447) — the levers compete inside the fixed 1,500-token render, a sizing datum for any
  future render-budget work.
- **`unfreeze_memory`** — invisible to reconstruction BY DESIGN (a live ballot-render effect whose
  output is frozen into the recorded prompt bytes); measured on the recorded bytes instead:
  **554/554** ballot prompts (13/13 at 4p1i) have belief-line suspicion == the pre-vote-folded graph —
  the PR #198 inconsistency is closed set-wide.
- **The railroad is lever-independent:** all six cells re-derive the same 5 railroad rows — the defect
  lives in the pre-13.5 fold weighting (§3) + the model's testimony (§4), NOT in any adopted lever. No
  lever is harmful; none is the 14.10 target.

This was the LAST run of this ablation: 14.9 deletes the toggles it flips. The harness recipe is
documented in §6 for the record; the committed JSONL is the artifact.

---

## 6. Method + reproduction (all $0, offline, committed bytes only)

- **R-gate folds:** reason/winner histograms + per-meeting ejection roles from
  `tournament-eval-report.json`; R7 from `results-rubric-score.json` per-game
  `r7_legible × n_meetings`; geomean ranking from `results-rubric-geomean.json`.
- **Fold reproduction / diagnosis:** reconstruct meeting-open beliefs via the loader memory walk
  (all-ON env, no override needed for the control), then
  `meetings.manager.derive_belief_evidence` + `agents.memory.beliefs.apply_contradiction_rule` +
  `apply_meeting_evidence_rules(phase="pre_vote")` + the 13.14 joint cap, compared against the
  recorded vote-prompt `## Your suspicion of each player` rows.
- **Ablation cells:** per cell, export the cell's `AILIBI_*` env config and construct
  `ReplayLoader(replay_dir=<set>, allow_substrate_mismatch=True)` (the Task-14.8 override; the loader
  logs every permitted mismatch at WARNING); walk all 50 seeds; fold as above. The witnessed-kill
  DETECTOR half re-runs `detect_contradictions(transcript, roster=<ballot voters>, env=...)` ON vs OFF
  (env-parameterized — no ambient state). One row per (set, cell) in
  `experiments/lab/results-substrate-ablation.jsonl`, each recording `substrate_flags`,
  `deliberate_substrate_mismatch`, and the override used.
- **Truth checks:** engine-truth rooms per (player, tick) from the loader's reconstructed tick states,
  compared against flag-cited alibi spans and sightings.
- **Rubric regen check:** `extract_gameplay_facts.py` → `rubric_score.py --set-dir replays/samples/9p2i`
  reproduces all three committed rubric JSONs byte-identically at sha `364f845`.

## 7. Not resolved by this characterization (open, carried forward)

- The **22 zero-flag crew mis-ejects** (prior-carry / voice-driven convictions outside the flag
  channel) are measured but not yet mechanistically decomposed; 14.10's lever will not touch them, and
  14.12 should report whether v4's calibration/curation fixes move them.
- The **kill-scene detector** remains effectively unmeasured (n=1 firing); needs a richer scenario —
  a Phase-15 candidate, not a 14.x blocker.
- **Impostor concealment** is unchanged by this phase's fixes by design (the 14.4 tell persists;
  cover-directive work is scoped to Phase 15) — the ceiling on concealment stands as the REVISED
  hypothesis's surviving half.
- The **4p1i set** shows the same direction with less data (accuracy 0.788, 7 mis-ejects) and no
  railroad rows; it stays the secondary set for this defect class.
