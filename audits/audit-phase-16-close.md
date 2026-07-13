# Phase-16 close — baseline 5: the graduation slate, the atomic re-record, the phase close (Task 16.17)

**Date:** 2026-07-13 (the slate and every §0 pre-registration section committed BEFORE the record —
the 15.18 discipline; measurement sections filled from the recorded bytes in this same operator
session).
**Task:** 16.17 — baseline 5 (atomic re-record of both canonical sets with the Wave-1 V&J layer as
the moving substrate: the graduation slate below + the 16.15/16.16 prompt bumps `v1 → v3`, model
HELD at the Task-16.2 lock) + the phase close.
**Sets:** `replays/samples/9p2i` (50 seeds) + `replays/samples/4p1i` (50 seeds), this re-record.
**Model:** `Qwen/Qwen3.6-27B` (Featherless, both call kinds, non-thinking PINNED, `fail_loud`,
`json_object`, $0 flat-rate) — UNCHANGED from baseline 4 (the one-layer-per-baseline discipline:
baseline 4 moved the model alone; baseline 5 moves the V&J layer alone, so the attribution chain
baseline 3 → 4 → 5 is unbroken).
**Substrate:** NINE levers unconditionally ON — the six retired at baselines ≤ 4
(`testimony_as_content`, `witnessed_kill_evidence`, `movement_perception`, `unfreeze_memory`,
`evidence_quality_lift`, `reporter_exculpation`) plus the THREE graduated by this task's slate
(`hard_evidence_gate`, `observation_id_rendering`, `citation_gate`) — and ONE live default-OFF
toggle (`absence_prior`, the slate's recorded stay-OFF, §0.1.4). Prompt set `qwen3_6_27b` v3 (all
four templates `*.qwen3_6_27b.v3` — 16.15's elicitation batch + 16.16's persona voice layer; the
registry in `orchestrator/game.py::PROMPT_VERSION_SETS` is the version authority).
**Grounding:** every number below is a fold over committed artifacts via
`scripts/validity_gate.py` + `scripts/measure_baseline.py` (core / `--watchability` / `--funnel` /
`--vj`). The BEFORE column regenerates from the committed `audits/baseline4-final-measure.json`,
captured on the baseline-4 bytes at tip **381832d**
(`381832d3cfea34ed11b9e81f9e5d5738f8fc8b1c`) immediately before this re-record replaced them (the
baseline-4 bytes survive only in git history there, and at the Q5 provenance point named in §7).
Zero hand-computed figures except the pre-registered canary statistics (§0.4) and the two
documented census folds (§10 quotes their exact reproduce snippets), whose inputs are quoted
beside them (the 15.18 convention).

**Verdict in one line:** _filled from the recorded bytes in this operator session — see §1–§8._

---

## 0. PRE-REGISTRATION (committed BEFORE the record — the 15.18 discipline)

Everything in this section was authored and committed before the first recorded seed. The
recording commit is the slate/graduation commit this file lands beside; the MANIFEST `git_sha`
column and the Q5 provenance point (§7) both name it.

### 0.1 The GRADUATION SLATE (the owner gate)

For each Wave-1 lever the ruling below cites the lever's COMMITTED counterfactual against its
named canary (`tasks/phase-16.md` 16.17 preflight). Per the 15.18 convention the owner's
sign-off rides the merge of this PR: the slate text is in the tree before the recording session
starts, the operator records what the slate says and nothing else, and a merge ratifies the
rulings. The pause trigger is restated up front: stay-OFF is coherent in-scope ONLY for the
template-free levers (J1, the absence prior); a stay-OFF ruling on either half of the COUPLED
pair (the citation gate, observation-id rendering) after 16.15's asks landed would PAUSE the
close for owner re-planning — that outcome did not occur (both halves rule graduate-ON below).

#### 0.1.1 J1 — the hard-evidence render gate (16.4): **GRADUATE-ON**

- **Named canary:** zero hard-flag-backed conviction outcomes change (the over-damping canary).
- **Committed counterfactual:** re-measured on the ADOPTING-ERA bytes (baseline 4) and pinned in
  `tests/agents/test_beliefs_hard_evidence_gate.py::TestHardEvidenceGateOnCommittedBytes`
  (re-pinned at the 16.14 merge `1c70d35`): over 79 recorded ejections (64 hard-backed / 15
  soft-only) the canary is CLEAN — `outcome_changes == 0`, `subject_level_flips == ()`, and the
  clamp never raises (`ejectee_clamp_raises == ()`). Polarity on baseline 4 is favourable: the
  clamp neutralises 1 soft-decided crew mis-eject and risks ZERO impostor catches (the 14
  still-over ejections all carry fresh same-meeting hard lift) — inverting the baseline-3 era's
  0-crew/2-impostor split (PR #258, measured over 72 hard-backed ejections, canary equally
  clean there).
- **Ruling:** graduate-ON. The canary holds on both measured substrates; the lever closes the
  zero-flag render channel at its root (a conviction-grade soft-only suspicion renders 0.59,
  under the §4.6 gate) and composes with J2 below — J1 bounds what the model SEES, J2 bounds
  what an uncited ballot can DO. J1 is kwarg/lever-gated with no template presence, so stay-OFF
  was available in-scope; the evidence does not support it (zero measured cost on the adopting
  baseline, and the phase's named residual — voice beating evidence — is exactly what it
  bounds under the 16.16 persona layer).

#### 0.1.2 Observation-id rendering (16.5): **GRADUATE-ON**

- **Named canary:** golden-proven inertness + 16.15's citation surface needs it ON.
- **Committed counterfactual:** the 16.3 prompt-byte golden
  (`tests/meetings/test_prompt_byte_golden.py`) is the OFF-path proof instrument — every
  committed baseline-4 prompt re-renders byte-identically through HEAD's production path with
  the lever OFF (16 passed on the pre-record tree, §0.2), and the one-byte-perturbation leg
  proves the gate can fail. The ON path is enforcement-free by construction (16.5 renders
  stable `[obs …]` ids; no gate consults them — enforcement is J2's).
- **The coupling that decides it:** 16.15's v2+ templates ask every EJECT to cite a transcript
  turn id or an `[obs …]` observation id (`vote_ballot.qwen3_6_27b.v3`: "copy that tag's id
  EXACTLY"). Those tags exist in the rendered memory ONLY when this lever is ON: with it OFF
  the elicitation surface asks for ids the substrate never renders — the incoherent half-state
  this contract's pause path exists to prevent.
- **Ruling:** graduate-ON. Inertness is golden-proven, the surface that consumes it is already
  merged, and stay-OFF would pause the close for a template retreat this task cannot absorb.

#### 0.1.3 J2 — the citation gate (16.6): **GRADUATE-ON** (with a recorded evidence caveat)

- **Named canary:** near-zero honest catches blocked (the soundness counterfactual).
- **Committed counterfactual** (PR #262, static per-meeting re-tally via
  `meetings.voting.tally_ballots` on the committed baseline-3 bytes): canonical 9p2i — **1**
  correct impostor ejection coerced (hand-examined: a single uncited gut-read deciding ballot)
  vs 2 soft-only crew mis-ejects prevented; 4p1i never gates (0/117 ballots); ml_corpus/9p2i
  cross-check 4 → 2 coerced once the honest-witness allowance credits voters holding
  witnessed-vent observations of their target (the C3 case 16.5's citation path exists to
  protect, fixture-pinned in `tests/meetings/test_citation_gate.py`) vs 2 prevented.
- **Recorded caveat:** unlike J1 and the absence prior, J2's soundness figure was NOT
  regenerated on the baseline-4 bytes (its committed evidence is baseline-3-anchored + the
  fixture suite). The graduation basis is therefore the baseline-3 counterfactual plus the
  structural protections that have only strengthened since: 16.5's ids + 16.15's citation asks
  give every honest catch a citation channel the baseline-3 counterfactual did not have
  (near-zero should fall further, not rise), and the gate coerces to SKIP — it can cost one
  ballot, never mint a conviction. The §2 close reading measures the realized coercion census
  (`coerced_zero_flag_markers`) on the recorded bytes as the post-hoc check.
- **Ruling:** graduate-ON. The canary reads near-zero on the committed evidence, the coupled
  surface (0.1.2) is live, and stay-OFF would pause the close. The enforcement tooth is the
  phase's headline contract: a zero-flag conviction must cite or coerce to SKIP.

#### 0.1.4 The absence prior (16.8): **STAY-OFF** (a recorded owner decision, not a silent omission)

- **Named canary:** the boundary pins + the set-size evidence (plus the PR #264-flagged owner
  question, ruled below).
- **Committed counterfactual:** the boundary pins hold (65 tests in
  `tests/agents/test_absence_prior.py`: lone absence renders 0.58 UNDER the gate, the delta
  composes through every cap, mints no `ContradictionRef`, never crosses alone). But the
  SET-SIZE evidence on the adopting-era bytes rules against graduating on this record:
  re-measured on baseline 4 and pinned in
  `tests/agents/test_absence_prior.py::TestAbsencePriorOnCommittedBytes` (re-pinned at
  `1c70d35`), **154/160 meetings carry a non-empty absent set** (median 4, max 8; histogram
  `{0:6,1:15,2:24,3:27,4:37,5:31,6:12,7:1,8:7}`), lever-ON creates a NEW at-or-over-the-gate
  candidate in **39/160** meetings and churns a voter's top rendered candidate in **106/160**.
  The pinned suite's own comment names the cause: the absent set is large because the 16.15
  roll-call elicitation did not exist in the recorded substrate — the lever is calibrated to
  work WITH roll-call (answering roll-call removes a player from the absent set), and roll-call
  uptake at scale is exactly this record's one unhedged unknown (`tasks/phase-16.md` 16.17
  integration risk). Graduating ON against a median-4 uncalibrated absent set would lift
  suspicion on quiet players game-wide on the same record that first measures whether roll-call
  shrinks that set.
- **Ruling:** stay-OFF, recorded. The lever is kwarg/lever-gated with no template presence, so
  stay-OFF is coherent in-scope (the roll-call ASK ships in v3 regardless — 16.7's
  `WhereaboutsClaim` machinery and 16.10's absence-set instrument measure it either way). The
  routed action: Phase 17 re-runs the set-size counterfactual on THIS record's bytes (roll-call
  live) and graduates at its own adopting record if the post-roll-call absent set supports it —
  §8's hand-off names it.
- **The PR #264-flagged owner question — ruled:** should vent sightings widen the placement
  substrate (today: stated paths + whereabouts only)? **Declined for now, recorded here.** The
  widening is a mechanism change (`reconstruct_stated_paths`' contract), and a defect/design
  question the close finds becomes a contract, never a close edit — it is routed WITH the
  absence lever to Phase 17, where the substrate question and the post-roll-call calibration
  can be decided together on measured baseline-5 evidence (widening shrinks the absent set and
  prevents double-counting a vent-sighted player as also "absent"; it interacts with the same
  calibration this ruling declines to guess at).

#### 0.1.5 The slate, in one row

| lever | task | canary | ruling | recorded flag at baseline 5 |
|---|---|---|---|---|
| `hard_evidence_gate` (J1) | 16.4 | zero hard-backed outcome changes — **CLEAN on baseline 4** (0/64) | **GRADUATE-ON** | `True` (retired) |
| `observation_id_rendering` | 16.5 | golden-proven inertness + 16.15 needs it ON — **both hold** | **GRADUATE-ON** | `True` (retired) |
| `citation_gate` (J2) | 16.6 | near-zero honest catches blocked — **1 on baseline-3 9p2i** (caveat: not re-measured on baseline 4) | **GRADUATE-ON** | `True` (retired) |
| `absence_prior` | 16.8 | boundary pins hold; set-size evidence **rules against** (154/160 non-empty, median 4, pre-roll-call) | **STAY-OFF** (recorded; Phase-17 re-measure post-roll-call; PR #264 substrate widening declined for now, routed with it) | `False` (live toggle, default-OFF) |

The recorded substrate must match this slate exactly: every `game_over.substrate_flags` stamp
carries the six previously-retired levers `True`, the three graduated levers `True`, and
`absence_prior` `False` under the bare recording environment (no `AILIBI_*` export — C6
discharged by graduation for the graduated set; the one remaining live toggle is default-OFF, so
bare recording and bare reconstruction agree without any export).

### 0.2 Preflight — the V&J layer is the ONLY moving layer (proven on the pre-record tree)

- **Prompt-byte golden GREEN:** `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` →
  `16 passed` at tip **381832d** — every recorded prompt of the committed baseline-4 sets
  re-renders byte-identically through HEAD's production render path (the v1 stamps resolve
  through the archived `qwen3_6_27b_v1` fixture per the PR #267 convention; this task retires
  that archive once the re-recorded stamps re-align with HEAD's registry, §7).
- **`verify_samples.sh` BARE:** `bash scripts/verify_samples.sh` under a bare environment (zero
  `AILIBI_*` exports) → `All 50 samples verified clean.` for both sets at 381832d.
- **The lever registry at the pre-record tree:** `orchestrator/replay.py` registers exactly four
  live toggles (`hard_evidence_gate`, `observation_id_rendering`, `citation_gate`,
  `absence_prior`), all resolving `False` under the bare environment; the graduation commit
  this file lands beside retires the first three per §0.1 and leaves `absence_prior` the sole
  live default-OFF toggle.
- **`refresh_samples.sh` gates (via `--dry-run`, both roster shapes):** prompt-set literal
  `REQUIRED_PROMPT_SET="qwen3_6_27b"` matches the locked set; the model-set coupling gate
  requires the effective Featherless meeting model to equal `Qwen/Qwen3.6-27B` (the set's
  locked owner model) with that id registered in
  `llm/featherless_client._THINKING_KWARG_BY_MODEL`; the script carries NO version literal —
  HEAD's registry is the version authority, which is why the MANIFEST provenance check in §7 is
  the version proof.
- **HEAD's registry resolves the locked set to v3:** `PROMPT_VERSION_SETS["qwen3_6_27b"]` →
  `accusation_round.qwen3_6_27b.v3`, `crewmate_report.qwen3_6_27b.v3`,
  `impostor_report.qwen3_6_27b.v3`, `vote_ballot.qwen3_6_27b.v3` (16.15's elicitation batch
  v1→v2 + 16.16's persona layer v2→v3 — the two prompt layers this record adopts).
- **Connectivity probe:** one `FeatherlessClient` call through the production client returned
  clean (`{"ok": true}`, `cost_usd 0.0`, `model Qwen/Qwen3.6-27B`, no reasoning-channel leak).
- **`record_ml_corpus.sh`'s coupled pin block** is re-pinned to the baseline-5 substrate IN THIS
  PR (model + set + `REQUIRED_PROMPT_VERSIONS` move together — its preflight couples the three)
  with the stale-corpus comment updated to name the substrate any future corpus records at;
  `replays/ml_corpus/` itself stays byte-untouched and STALE (baseline-3/Qwen3-32B substrate) —
  Phase 17 re-grounds it (§8).

### 0.3 The BEFORE column

`audits/baseline4-final-measure.json` — captured at tip **381832d** on the committed baseline-4
bytes immediately before replacement, by the same three CLIs the baseline-3 file used (`--json`,
`--watchability --json`, `--funnel --json`) PLUS the `--vj --json` block: the Task-16.10 V&J
instruments exist at this capture (they did not at the baseline-3 capture), and this close's
before/after on those instruments must regenerate from a committed artifact like every other
number. The before/after tables in §2–§5 regenerate from this file plus the new bytes; no figure
is copied by hand.

### 0.4 Pre-registered canary bands + the named NO-GO pairing (the close's pause arms)

Per the DEGRADED-Q3 rule (`tasks/phase-16.md` "Canary honesty this phase"): the ML corpus is
baseline-3/Qwen3-32B substrate — there is NO corpus-scale same-substrate set. Canaries are
judged on the **50-seed 9p2i set** with the 15.18 two-proportion discipline; the corpus figure
is quoted as STALE CONTEXT only; 4p1i cells are reported for ladder continuity and are findings,
never NO-GO-bearing.

Anchors (from `audits/baseline4-final-measure.json`, 9p2i):

| canary | baseline-4 anchor | baseline-3 anchor (ladder context) |
|---|---|---|
| R1 eject-decided win share | 34/50 = 0.68 | 34/50 = 0.68 |
| genuine-class conversion | 0/0 — NO-DATA (supply collapsed at the model swap) | 10/13 = 0.7692 |

**The pre-registered tests (9p2i, two-sided α = 0.05):**

1. **REGRESSION (the phase-pausing NO-GO):** the baseline-5 cell is BELOW the baseline-4 anchor
   AND the pooled two-proportion z vs the anchor satisfies |z| ≥ 1.96. Directions above the
   anchor are findings, never regressions.
2. **R1 band (both n fixed at 50, numeric in advance):** REGRESSION iff baseline-5
   R1 ≤ 24/50 = 0.48 (|z| = 2.026 at 24/50; 25/50 gives |z| = 1.830). The pre-registered band
   is therefore **R1 ∈ [25/50, 50/50]** — identical to baseline 4's band because the anchor is
   identical (34/50).
3. **Genuine-class conversion — the anchor is EMPTY (0/0), so no regression arm can fire:** the
   rule in (1) is arithmetically undefined against a zero-supply anchor. Pre-registered
   handling: whatever the recorded bytes supply is a FINDING — a supply recovery (n₂ > 0, the
   16.15 roll-call ask's purpose) is reported with its conversion cell and Wilson 95% CI
   against the baseline-3 anchor (0.7692) as LADDER CONTEXT only (different model — never
   NO-GO-bearing); zero supply again is the recorded confirmation that the alibi channel needs
   Phase-17/18 prompt work beyond the roll-call ask.
4. **UNDERPOWERED (recorded honestly, not a judgment call):** alongside every verdict, the
   Wilson 95% CI of the baseline-5 cell is reported; if that CI contains BOTH the baseline-4
   anchor and the baseline-3 anchor, the verdict is recorded as UNDERPOWERED.
5. **The named NO-GO pairing (voice metrics ALONGSIDE zero-flag — pre-registered reading):**
   the §2 table reports the 16.10 voice tier and the zero-flag conviction rate side by side.
   At THIS record the judgment levers move ONLY downward on the zero-flag channel: J1 clamps
   conviction-grade soft-only renders sub-gate and J2 coerces uncited zero-flag EJECTs to SKIP
   — neither can ADD a zero-flag conviction. The persona layer (16.16) is the only graduated
   component that could raise it. Pre-registered arm: a zero-flag conviction rate RISE above
   the baseline-4 anchor (25/89 = 0.2809 on 9p2i) that is statistically resolved (pooled
   two-proportion |z| ≥ 1.96) is therefore persona-attributable BY CONSTRUCTION and is **the
   phase NO-GO** — the close pauses for the owner. A rise below resolution is reported with
   its CI (and UNDERPOWERED honesty); a fall is the expected direction (finding).
6. **The close's one pass-bar (the 15.23 pattern):** both recorded sets PASS
   `scripts/validity_gate.py --expected-model Qwen/Qwen3.6-27B --require-zero-cost` and the
   16.11 referee with the baseline-5 floors pinned from the committed bytes; a failure here
   pauses for an owner call rather than shipping. Everything else — funnel rows, uptake,
   ejection accuracy, win rates, referee gauges on OTHER populations — is a MEASUREMENT with a
   direction read: findings that scope Phase 17/18 (record-only discipline).

### 0.5 The recording plan (the 15.7 runbook, verbatim mechanics; the 16.14 operator notes applied)

- `scripts/refresh_samples.sh --full` twice — once with the 9p2i roster env
  (`AILIBI_NUM_PLAYERS=9 AILIBI_NUM_IMPOSTORS=2 AILIBI_TASKS_PER_CREWMATE=2
  AILIBI_SAMPLE_DIR=replays/samples/9p2i AILIBI_MANIFEST=replays/samples/9p2i/MANIFEST.md`),
  once bare for the flat 4p1i default — under
  `AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b AILIBI_SEED_MAX_ATTEMPTS=8`
  and NOTHING else (bare levers: the three graduated levers are unconditional in code, the
  absence prior stays OFF by default — stamped flags = the slate, no export to forget; the
  meeting model is the client default — the locked id).
- 2 parallel Featherless seed workers (the plan's 4-unit cap at 2 units/request) with the 16.14
  §6 operator notes applied: staggered worker starts, jittered backoff, per-seed crash-retry
  budget 8, per-seed atomic staging (a failed seed never touches the live set), MANIFEST row per
  seed under the writer lock, full-mode canonicalize, eval-report rebuild, and the 9p2i rubric
  regeneration — all inside the committed script.
- No commit lands between the two set refreshes, so every MANIFEST row of both sets stamps the
  SAME recording commit (the slate/graduation commit this file lands beside); the Q5 provenance
  point is created at that commit after the atomic replacement commit lands (§7 records the
  arm actually used — annotated tag, or the 16.14 fallback if tag pushes are refused).
- A `(deadline_default)` phantom failed-call row on any seed is remedied per the corpus
  runbook: the seed re-records clean, its MANIFEST row honestly stamps the re-record date (the
  16.14 seed-5 precedent; the validity gate rejects the phantom class by design).
- Both sets then gate through `scripts/validity_gate.py --expected-model Qwen/Qwen3.6-27B
  --require-zero-cost` and reconstruct byte-identically BARE before anything is committed.

---

## 1. HARD validity gate — _to be filled from the recorded bytes_

## 2. The close reading: 16.10's instruments before/after (voice ALONGSIDE zero-flag) — _to be filled_

## 3. The information funnel re-measured (baseline 4 → baseline 5) — _to be filled_

## 4. R-gate re-measured + the canaries under the §0.4 bands — _to be filled_

## 5. Selection referee + baseline-5 floors — _to be filled_

## 6. Uptake findings per elicitation ask (findings, not pass bars) — _to be filled_

## 7. Provenance — _to be filled_

## 8. The permanent record: the Phase-17 staleness rule — _to be filled_

## 9. Decisions — _to be filled_

## 10. Method + reproduction — _to be filled_
