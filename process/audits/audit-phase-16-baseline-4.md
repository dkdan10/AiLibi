# Phase-16 baseline 4 — the model-only atomic re-record + the champion re-audit (Task 16.14)

**Date:** 2026-07-12 (pre-registration committed before the record; measurement sections filled
from the recorded bytes in this same operator session).
**Task:** 16.14 — baseline 4 (atomic re-record of both canonical sets with the MODEL as the only
layer change: `Qwen/Qwen3.6-27B` + the `qwen3_6_27b` v1 bespoke set, every Phase-16 lever
merged OFF/inert) + the opt-in champion's 50-seed re-audit against the new meeting substrate.
**Sets:** `replays/samples/9p2i` (50 seeds) + `replays/samples/4p1i` (50 seeds), this re-record.
**Model:** `Qwen/Qwen3.6-27B` (Featherless, both call kinds, non-thinking PINNED, `fail_loud`,
`json_object`, $0 flat-rate) — the Task-16.2 lock (`audits/audit-phase-16-model-lock.md`).
**Substrate:** mechanics byte-equivalent to baseline 3's — all SIX retired levers unconditionally
ON (`testimony_as_content`, `witnessed_kill_evidence`, `movement_perception`, `unfreeze_memory`,
`evidence_quality_lift`, `reporter_exculpation`), both live Phase-16 toggles
(`hard_evidence_gate`, `observation_id_rendering`) DEFAULT-OFF under a bare environment; prompt
set `qwen3_6_27b` v1 (all four templates `*.qwen3_6_27b.v1` — the registry in
`orchestrator/game.py::PROMPT_VERSION_SETS` is the version authority).
**Grounding:** every number below is a fold over committed artifacts via
`scripts/validity_gate.py` + `scripts/measure_baseline.py` (core / `--watchability` /
`--funnel`). The BEFORE column regenerates from the committed
`audits/baseline3-final-measure.json`, captured on the baseline-3 bytes at tip **beb2c07**
(`beb2c07e837074b35b394d8146bd77d2381694fb`) immediately before this re-record replaced them
(the baseline-3 bytes survive only in git history at beb2c07, and at the Q5 annotated tag
below). Zero hand-computed figures except the two pre-registered canary statistics, whose
formulas are pre-registered in §0.3 and whose inputs are quoted beside them (the 15.18
convention).

**Recording:** 2 parallel Featherless seed workers per set; wall ≈ **5h01m** (9p2i) + **37m**
(4p1i), with the plan's 4-concurrent-unit cap absorbed by per-seed crash-retry (9p2i: 11
transient 429/transport retries, deepest 4/4 on seed 31; 4p1i: 4 retries under an 8-attempt
budget; **0 hard failures**). One live-recording edge case: 9p2i seed 5's first take recorded a
wall-clock-miss `(deadline_default)` phantom failed-call row ("opening turn (turn 0) defaulted
(validation); p-1 submitted no turn", 0 tokens, no real call) — the validity gate rejects the
phantom class by design, and the seed was re-recorded clean per the corpus-runbook remedy (its
MANIFEST row honestly stamps `refreshed_at 2026-07-13`; the other 99 rows span 2026-07-12/13
across the UTC midnight the session crossed). The champion leg (51 recorded games incl. one
phantom-remedy re-record of seed 33) ran the same discipline over a longer wall (~11h with two
container restarts absorbed by resume-skip): 75 transient 429 retries, 2 seed-budget
exhaustions recovered by re-run (seed 39 recorded first-try once the tail went single-worker —
the plan's 4-unit cap makes 2 concurrent champion games collide in ballot phases; §6).

**Verdict in one line:** the model swap is a VALID baseline — both sets PASS the hard gate
(`--expected-model Qwen/Qwen3.6-27B --require-zero-cost`, 10/10 checks) and reconstruct
byte-identically BARE; **neither §0.3 canary band fired** (R1 lands EXACTLY on its 34/50 anchor,
z = 0.000; genuine-class conversion is NO-DATA at 0/0 supplied — the pre-registered test cannot
fire, §3) — and the headline finding is that the locked model's scratch-ladder impostor profile
TRANSFERRED to live games: structured alibi lies vanished (alibi_vs_* transcript flags 190 → 7,
all crew-subject), the vent/sighting channels strengthened, crew mis-ejections collapsed 33 → 12,
and ejection accuracy rose 0.697 → 0.865 while the impostor win rate eased 0.30 → 0.24. The
alibi-channel instruments (genuine-class conversion and its supply) are STARVED on this
substrate — routed to 16.15's elicitation scope and the 16.17 close, not absorbed (§6). The
champion re-audit (§5) is stamp-proven on all 50 games with a PASSING gate: the champion's win
edge over the same-substrate FSM baseline SURVIVES the swap (+12pp, 0.36 vs 0.24) while the
16.11 referee now rejects its evidence-starved meeting economy — a finding routed to the close
+ Phase 17, never a blocker. GO stands; no phase pause.

---

## 0. PRE-REGISTRATION (committed BEFORE the record — the 15.18 discipline)

Everything in this section was authored and committed before the first recorded seed. The
recording commit is this commit; the MANIFEST `git_sha` column and the Q5 annotated tag both
name it.

### 0.1 Preflight — the model is the ONLY layer (proven on the pre-record tree at beb2c07)

- **Prompt-byte golden GREEN:** `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` →
  `16 passed` — every recorded prompt of the committed baseline-3 sets re-renders
  byte-identically through HEAD's production render path.
- **`verify_samples.sh` BARE:** `bash scripts/verify_samples.sh` under a bare environment (zero
  `AILIBI_*` exports) → `=== verifying replays/samples/4p1i/ === All 50 samples verified clean.`
  and `=== verifying replays/samples/9p2i/ === All 50 samples verified clean.`
- **Every `_TOGGLEABLE_LEVER_RESOLVERS` entry OFF:** `orchestrator/replay.py` registers exactly
  two live toggles — `hard_evidence_gate` (16.4) and `observation_id_rendering` (16.5) — and
  `substrate_flag_snapshot()` under the bare recording environment resolves BOTH `False`
  (verified by direct invocation on the pre-record tree); the six retired levers snapshot
  unconditionally `True`.
- **`refresh_samples.sh` prompt-set literal:** `REQUIRED_PROMPT_SET="qwen3_6_27b"`
  (`scripts/refresh_samples.sh:432`) matches the locked set; the script carries NO version
  literal (the registry is the version authority).
- **HEAD's registry resolves the locked set to v1:**
  `PROMPT_VERSION_SETS["qwen3_6_27b"]` → `crewmate_report.qwen3_6_27b.v1`,
  `impostor_report.qwen3_6_27b.v1`, `accusation_round.qwen3_6_27b.v1`,
  `vote_ballot.qwen3_6_27b.v1` (`orchestrator/game.py:345`).
- **`record_ml_corpus.sh`'s coupled block stays baseline-3** (its model/prompt-set literals are
  16.17's business; `replays/ml_corpus/` is stale by design after this record — Phase 17
  re-grounds).
- **Model-set coupling + registry gates:** the refresh preflight requires the effective
  Featherless meeting model to equal `Qwen/Qwen3.6-27B` (the set's locked owner model) and that
  id to be registered in `llm/featherless_client._THINKING_KWARG_BY_MODEL` (16.12's fail-loud
  entry, non-thinking pinned at request time). Both confirmed by `--dry-run` on the pre-record
  tree; a one-call connectivity probe through `FeatherlessClient` returned clean
  (`{"ok": true}`, `cost_usd 0.0`, `model Qwen/Qwen3.6-27B`, no reasoning-channel leak).

### 0.2 The BEFORE column

`audits/baseline3-final-measure.json` — captured at tip **beb2c07** by the same three CLIs the
baseline-2 file used (`--json`, `--watchability --json`, `--funnel --json`) on the committed
baseline-3 bytes immediately before replacement. The before/after tables in §2–§4 regenerate
from this file plus the new bytes; no figure is copied by hand.

### 0.3 Pre-registered canary bands (the one NO-GO)

Per the DEGRADED-Q3 rule (`tasks/phase-16.md` "Canary honesty this phase"): the ML corpus is
baseline-3/Qwen3-32B substrate, so from the moment baseline 4 lands there is NO corpus-scale
same-substrate set. Canaries are judged on the **50-seed 9p2i set** with the 15.18
two-proportion discipline; the corpus figure is quoted as STALE CONTEXT only; 4p1i cells are
reported for ladder continuity and are findings, never NO-GO-bearing (the 15.7/15.18
precedent).

Anchors (from `audits/baseline3-final-measure.json`, 9p2i):

| canary | baseline-3 anchor | baseline-2 anchor (ladder context) |
|---|---|---|
| genuine-class conversion | 10/13 = 0.7692 | 0.625 |
| R1 eject-decided win share | 34/50 = 0.68 | 24/50 = 0.48 |

**The pre-registered test (per canary, 9p2i, two-sided α = 0.05):**

1. **REGRESSION (the phase-pausing NO-GO):** the baseline-4 cell is BELOW the baseline-3 anchor
   AND the pooled two-proportion z vs the anchor satisfies |z| ≥ 1.96. Directions above the
   anchor are findings, never regressions.
2. **R1 band (both n fixed at 50, so the band is numeric in advance):** REGRESSION iff
   baseline-4 R1 ≤ 24/50 = 0.48 (|z| = 2.026 at 24/50; 25/50 gives |z| = 1.830). The
   pre-registered band is therefore **R1 ∈ [25/50, 50/50]**.
3. **Genuine-class conversion (the supplied denominator n₂ is data-dependent):** the rule in
   (1) applies at whatever n₂ the recorded bytes supply. For transparency, the pre-computed
   regression boundaries: n₂=8 → converted ≤ 2; n₂=10 → ≤ 3; n₂=13 → ≤ 5; n₂=16 → ≤ 6;
   n₂=20 → ≤ 8.
4. **UNDERPOWERED (recorded honestly, not a judgment call):** alongside every verdict, the
   Wilson 95% CI of the baseline-4 cell is reported; if that CI contains BOTH the baseline-3
   anchor and the baseline-2 anchor (the two hypotheses the ladder distinguishes), the verdict
   is recorded as UNDERPOWERED — the 50-seed test cannot separate "unchanged" from
   "down-a-rung" at that n (the pause-audit corollary: n≈13 genuine-class opportunities per
   50-seed set).
5. Everything else — impostor win rate, ejection accuracy, ECE, the funnel rows, the referee
   gauges — is a MEASUREMENT with a direction read: findings that scope 16.15, never pass
   bars (record-only discipline; a disappointing uptake number is a finding, not a reason to
   iterate prompts mid-record).

### 0.4 Pre-registered champion re-audit reading

Second artifact, same operator session: the opt-in champion
(`agents/tactical/learned/`, `utility-es`, committed weights sha256
`6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0`) re-audited on the NEW
meeting substrate via `scripts/run_tournament.py --agent-factory learned-champion` over the
audit seeds (0..49, the canonical 9p2i roster: 9p, 2i, tasks_per_crewmate 2). Measurement
committed as `training/reports/results-champion-qwen36-audit.jsonl` in the
`results-champion-close.jsonl` stamp-proof row shape: the five-field
`tactical_policy_stamp` READ BACK from the recording bytes of every game via
`orchestrator.replay.read_tactical_policy_stamp` (never echoed from the launch config),
`stamp_verified_games` = 50, `stamp_equals_committed_sha256` asserted against the committed
sidecar. Raw recordings stay uncommitted (the Q5/close convention: outside
`replays/samples/` and `replays/ml_corpus/`, re-recordable from this recipe).

**The pre-registered reading:** the champion was SELECTED under Qwen3-32B meetings
(`results-champion-close.jsonl` anchors: impostor win 20/50 = 0.40, R1 29/50, genuine-class
20/24 = 0.833, gate PASS). This re-audit is the honest re-reading of that artifact against
Qwen3.6-27B meetings — NOT a retrain (Phase 17's business). **A degraded champion result — any
direction, any size — is a FINDING routed to the 16.17 close and Phase 17, never a blocker and
never a canary.** The §0.3 bands apply exclusively to the canonical FSM-default baseline
record; the champion row shares only the measurement CLIs.

### 0.5 The recording plan (the 15.7 runbook, verbatim mechanics)

- `scripts/refresh_samples.sh --full` twice — once with the 9p2i roster env
  (`AILIBI_NUM_PLAYERS=9 AILIBI_NUM_IMPOSTORS=2 AILIBI_TASKS_PER_CREWMATE=2
  AILIBI_SAMPLE_DIR=replays/samples/9p2i AILIBI_MANIFEST=replays/samples/9p2i/MANIFEST.md`),
  once bare for the flat 4p1i default — under
  `AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b` and NOTHING else (bare
  levers; the meeting model is the 16.12 client default — the locked id).
- 2 parallel Featherless seed workers (the plan's 4-unit cap at 2 units/request), per-seed
  crash-retry ≤ 4 with backoff, per-seed atomic staging (a failed seed never touches the live
  set), MANIFEST row per seed under the writer lock, full-mode canonicalize, eval-report
  rebuild, and the 9p2i rubric regeneration — all inside the committed script.
- No commit lands between the two set refreshes, so every MANIFEST row of both sets stamps the
  SAME recording commit (this one); the Q5 annotated tag is created at that commit after the
  atomic replacement commit lands.
- Both sets then gate through `scripts/validity_gate.py --expected-model Qwen/Qwen3.6-27B
  --require-zero-cost` and reconstruct byte-identically BARE before anything is committed.

---

## 1. HARD validity gate — PASS (both sets)

`validity_gate.py --expected-model Qwen/Qwen3.6-27B --require-zero-cost` over both committed
sets (10/10 checks green each), cross-checked by `bash scripts/check.sh`:

| criterion | 9p2i | 4p1i |
|---|---|---|
| every game reaches game_over | 50/50 | 50/50 |
| meeting_rate / resolved meetings (bar ≥0.60 / ≥30) | 1.00 / 160 | 0.78 / 39 |
| tick-1 kills | 0 | 0 |
| friendly-fire (impostor-on-impostor) kills | 0 | 0 |
| betrayal ballots/accusations (§7.12 firewall) | 0 / 964 | 0 / 0 (single-impostor, vacuous) |
| railroaded crew ejections | 0 / 1417 | 0 / 35 |
| dangling `primary_reason_id` | 0 / 964 | 0 / 117 |
| cost rows ($0 Featherless flat-rate, `--require-zero-cost`) | exact | exact |
| provenance rows (`Qwen/Qwen3.6-27B`, 4 × `*.qwen3_6_27b.v1`, 6 levers stamped) | exact | exact |
| byte-identical reconstruction (BARE env) | 0 drift | 0 drift |

`verify_samples.sh` reconstructs all 50+50 samples clean under a bare environment (no
`AILIBI_*` export): the two live Phase-16 toggles stamp `False` on every game_over record and
the six retired levers stamp `True` — byte-consistent with the preflight snapshot (§0.1).

## 2. The information funnel re-measured (baseline 3 → baseline 4)

`eval.funnel` (the 15.3 instrument), the same three-stage fold before and after; BEFORE
regenerates from `audits/baseline3-final-measure.json`, AFTER from the committed bytes (9p2i):

| funnel row | baseline 3 | **baseline 4** | read |
|---|---|---|---|
| structured vent observations | 55 (of 73 vent meetings) | **74 (of 100)** | the 15.4 mechanism carries over AND the model witnesses more vents |
| vent mentioned (free text) | 53/73 | **75/100** | transmission holds at ~0.75 |
| innocent-reporter ejections | 4 | **1** | the reporter hole stays shut |
| votes outside a ≤3 candidate set | 30 (of 64) | **12 (of 54)** | vote discipline sharply tighter |
| report-meeting ejections | 95 | 79 | fewer, more accurate (§3) |
| killer accused | 75 | **88** | up |
| kill witnessed | 5 | **9** | witnessed-kill supply nearly doubles |
| hard clue held | 98 | 125 | more held evidence (more meetings: 160 vs 139) |
| oracle candidate-set median | 3 | 3 | diagnostic ceiling unchanged |
| killer-in-set (±1 window) | 109 | 136 | up with the meeting count |

4p1i is the determinism control and the cleanest possible proof that the model was the ONLY
layer: every held-evidence row — vent witnessed/held 6, hard clue held 21, killer-in-set 35,
kill witnessed 1 — is **byte-identical** between baselines (the pre-meeting simulation is a
deterministic function of the seed and the unchanged tactical layer); only the meeting-decided
rows move (killer accused 31 → 25, report ejections 22 → 15, innocent reporters 3 → 2), and the
win split lands identical (36 crew / 14 impostor).

## 3. R-gate re-measured + the canaries under the §0.3 bands (9p2i, vs the baseline-3 anchors)

Per the pre-registration, directions are findings; the ONLY NO-GO is a §0.3 band violation —
and neither band fired.

| term | baseline 3 | **baseline 4** | read |
|---|---|---|---|
| **R1 eject-decided win share** (canary) | 34/50 = 0.68 | **34/50 = 0.68** | EXACTLY the anchor (two-proportion z = 0.000; Wilson 95% CI [0.542, 0.792] excludes the 0.48 rung — not UNDERPOWERED). Inside the pre-registered band [25/50, 50/50]. |
| **genuine-class conversion** (canary) | 10/13 = 0.769 | **0/0 — NO DATA** | supply is ZERO: the §0.3 two-proportion test is UNDEFINED at n₂ = 0 and no REGRESSION verdict can fire (the rule requires a below-anchor cell at \|z\| ≥ 1.96). Verdict recorded as NO-DATA; the supply collapse is §6's headline finding, and the failure mode this canary guards (crew failing to convict on supplied genuine catches) demonstrably did not occur — conviction rose across the board. |
| ejection accuracy | 0.697 (76 imp / 33 crew of 109) | **0.865 (77 imp / 12 crew of 89)** | crew mis-ejects collapsed 33 → 12 at equal impostor ejections |
| impostor win (floor ≥0.14) | 0.30 | **0.24** | eased; floor holds — from better crew deduction, not a balance bug |
| reason histogram | `{EJECT 34, PARITY 15, TASKS 1}` | `{EJECT 34, PARITY 12, TASKS 4}` | eject-decided share flat; parity wins down |
| accusation-claim ECE / n | 0.275 / 372 | 0.269 / 438 | calibration ~flat, more claims |
| vote-ballot ECE / n | 0.178 / 753 | **0.115 / 525** | ballots better calibrated (and fewer — earlier ejections shrink the alive-voter pool) |

4p1i (continuity, findings only): R1 21/50 → 17/50 (two-proportion z = 0.824 — not a resolved
move; Wilson CI [0.224, 0.479] contains BOTH anchors → **UNDERPOWERED, recorded honestly**);
genuine-class 3/3 → 0/0 NO-DATA (same supply collapse); ejection accuracy 0.808 → 0.895;
impostor win 0.28 → 0.28 (identical).

Per the DEGRADED-Q3 rule the corpus is quoted as STALE CONTEXT only: `replays/ml_corpus/`
remains baseline-3/Qwen3-32B substrate (its baseline-3-era 9p2i cells: genuine-class 34/52 =
0.654, R1 109/150 = 0.727) and is NOT same-substrate evidence for any baseline-4 cell — Phase
17 re-grounds it.

## 4. Selection referee + evidence-supply floors — PASS (both sets; baseline-4 floors pinned, 16.11 definition)

This task pins the **baseline-4** floors in `eval/watchability.py`'s per-baseline block from
the committed bytes (each set passes at exact equality — the derivation self-consistency the
16.11 re-anchor guarantees) and moves `_DEFAULT_BASELINE_ID` to `baseline-4` (the 15.7
precedent: the committed canonical set scores against its own supply).

| supply gauge (9p2i) | baseline 3 (floor) | **baseline 4 (floor)** |
|---|---|---|
| witnessed_event_rate | 0.03247 (5/154) | **0.05056 (9/178)** |
| flags_per_meeting | 1.863 (259/139) | **0.5375 (86/160)** |
| testimony_backed_conversion (subject-aware, population-relative) | 0.6636 (71/107) | **0.6260 (77/123)** |

4p1i: witnessed 1/58 = 0.01724 (numerator 1 → ADVISORY, the 15.19 rare-event rule),
flags_per_meeting 11/39 = 0.28205 (ALL persisted vent flags — the transcript census re-derives
zero on this set), conversion 17/29 = 0.5862. Both sets PASS the referee (supply floors + the
D1–D4 geomean; 9p2i mean score 35.19 → **45.81**, 4p1i 8.40 → 6.51).

The reading behind the flags_per_meeting drop (~3.5×): the flag pool is now VENT-DOMINATED (79
of 86 flags on 9p2i; vent flags themselves ROSE 69 → 79) because the alibi-contradiction
classes collapsed with the impostor's clean-alibi profile (§6). The gauge the referee actually
gates — SIGHTING-backed conversion under the 16.11 population-relative derivation — barely
moved (0.664 → 0.626) and stays density-aware: a future evidence-starved candidate faces a
sharpened demanded rate (floor = 0.6260 × (0.5375 / measured flags_per_meeting), capped at
1.0), never a free pass off the smaller pin.

## 5. The champion re-audit (finding, not blocker)

Second artifact, same operator session, per the §0.4 pre-registration: the opt-in champion
(`utility-es`, measured, never modified) re-run over the audit seeds (0..49, 9p/2i/tasks=2)
against the NEW meeting substrate via
`scripts/run_tournament.py --agent-factory learned-champion --force` (one seed per process,
per-seed staging + crash-retry; the 429-squeeze tail recorded single-worker). Measurement
committed as `training/reports/results-champion-qwen36-audit.jsonl` in the champion-close
stamp-proof row shape; raw recordings uncommitted (outside the repo tree, re-recordable from
this recipe). Recorded at checkout **1e28da2** (code byte-identical to the recording commit
a43b178 — 1e28da2 adds only the replaced sample bytes and audit artifacts).

**The stamp proof (read back from bytes, never echoed):** all 50 recordings carry an identical
five-field `TacticalPolicyStamp` read back via `orchestrator.replay.read_tactical_policy_stamp`
— `policy_id utility-es`, `method utility-scorer-es`, `encoder impostor-option-features-v1`,
`anchor fsm-default`, `weights_sha256 6d327dcb…f71d0` — and the sha equals the committed sidecar
digest (`stamp_equals_committed_sha256: true`, `stamp_verified_games: 50`). One recording edge
case: seed 33's first take carried the same `(deadline_default)` phantom failed-call class as
the canonical set's seed 5 and was re-recorded clean per the same remedy; the committed row's
gate then PASSES 10/10 with `--expected-model Qwen/Qwen3.6-27B --require-zero-cost`.

**The reading (all cells from the committed row's CLI blocks):**

| term | champion @ close (Qwen3-32B meetings) | **champion @ re-audit (Qwen3.6-27B meetings)** | FSM baseline-4 (same substrate) |
|---|---|---|---|
| impostor win rate | 20/50 = 0.40 | **18/50 = 0.36** | 12/50 = 0.24 |
| edge over the contemporary FSM baseline | +0.10 (0.40 vs 0.30) | **+0.12 (0.36 vs 0.24)** | — |
| R1 eject-decided win share | 29/50 | **27/50** | 34/50 |
| ejection accuracy | 0.6195 | **0.8171 (67 imp / 15 crew of 82)** | 0.8652 |
| genuine-class conversion | 20/24 = 0.833 | **0/0 — NO DATA** (the §6 substrate-wide alibi collapse) | 0/0 |
| meeting rate / resolved meetings | 1.0 / 139 | **1.0 / 164** | 1.0 / 160 |
| witnessed_event_rate | 0.2195 | **0.2071** | 0.0506 |
| flags_per_meeting | 3.0432 | **0.2988** | 0.5375 |
| testimony-backed conversion (16.11 derived floor) | 0.5743 (derived floor 0.4063 → PASS) | **0.4887 (derived floor CAPPED at 1.0 → FAIL)** | 0.6260 (= pin, PASS at equality) |
| referee | FAIL as recorded (absolute floor), PASS under the 16.11 derivation | **FAIL** (flags floor + starvation-sharpened conversion) | PASS |
| validity gate | PASS | **PASS** | PASS |

**Read as pre-registered — a finding routed to the 16.17 close and Phase 17, not a blocker:**

1. **The champion's competitive edge SURVIVES the model swap.** Against its own-substrate FSM
   baseline it wins +12pp (0.36 vs 0.24), slightly wider than its selection-era +10pp
   (0.40 vs 0.30). The honest re-reading does NOT find a degraded champion in win terms.
2. **The referee now rejects the champion's evidence economy, and that is the instrument
   working.** Under Qwen3-32B meetings the champion's games were flag-rich (3.04/meeting);
   under the new substrate its games carry LESS per-meeting testimony evidence (0.299) than
   even the FSM baseline (0.5375), so the 16.11 population-relative conversion floor sharpens
   past its cap (demanded 1.0, measured 0.489 → FAIL) and the flags floor fails outright. The
   champion's open-kill style (witnessed-kill rate 4× baseline) no longer converts to
   testimony under a meeting model that volunteers fewer claims. A Phase-17 retrain/re-select
   under the baseline-4 substrate — with this referee as the selection bar — is the routed
   action; the champion stays opt-in-only meanwhile (the 15.20/15.21 deployment posture is
   unchanged by this task).
3. **The genuine-class NO-DATA cell replicates on the champion substrate** (0/0 at 164
   meetings) — corroborating §6's reading that the collapse is a property of the new meeting
   model's alibi behavior, not of the tactical layer (the champion changes only impostor
   tactical decisions; the supply collapse appears identically under FSM and champion
   tactics).

## 6. Findings (directions, not pass bars — scoping 16.15 and the close)

- **The structured-alibi channel is starved — the headline.** The bespoke set's impostor
  profile (the scratch ladder's 0/32 self-flag design, `audit-phase-16-model-lock.md` §3)
  transferred to live full games: alibi claims fell 281 → 109 set-wide, `alibi_vs_sighting`
  transcript flags 147 → 7 (every one crew-subject), `alibi_vs_physical` 39 → 0. Consequence:
  **genuine-class conversion has ZERO supply on both 50-seed sets** (9p2i 13 → 0, 4p1i 3 → 0) —
  the Phase-10 primary-progress instrument reads NO-DATA on this substrate. The deduction game
  did not die: it moved to the vent channel (79 vent flags, up from 69; structured vent
  observations 74/100) and movement/sighting corroboration (corroboration claims 39 → 66,
  accusations 372 → 437), and convicts BETTER (ejection accuracy 0.697 → 0.865). Routed: 16.15's
  elicitation batch owns alibi elicitation (crew volunteering checkable alibis is exactly the
  vent-tail/citations territory), and the 16.17 close + Phase 17 own re-grounding the
  genuine-class instrument (and the stale corpus) on this substrate.
- **Crew skip discipline changed shape.** Missed-skip ballots 11 → 86 on 9p2i (crew voting for
  a target where the recorded skip-threshold reading says skip) while votes-outside-the-set fell
  30 → 12 and mis-ejects collapsed 33 → 12 — the new model votes MORE decisively inside the
  candidate set and is right more often, but its ballots more often override the suspicion-gate
  arithmetic. A dialogue/calibration finding for 16.15 (the ballot ECE actually improved,
  0.178 → 0.115).
- **4p1i geomean eased** (8.40 → 6.51, median 2.9 → 1.3) on the reference set — shorter
  eject-decided games and a smaller ejection census (26 → 19) on the sparse roster; the
  canonical 9p2i geomean ROSE 35.19 → 45.81. Watch at the 16.17 re-record.
- **The recording harness carries a real 4-unit concurrency squeeze** on this plan: a game's
  ballot phase can hold both plan slots, so the OTHER worker's game crashes on HTTP 429 when
  phases collide (11 retries over the 9p2i run; two synchronized-restart loops observed live on
  the champion leg before staggering/jitter were added to the operator driver). The per-seed
  crash-retry budget absorbed every instance; the committed recordings are unaffected
  (rejected requests consume nothing). Operator note for 16.17: stagger worker starts, jitter
  the backoff, budget ≥8 attempts.

## 7. Decisions

- **Pinned baseline-4 floors from the committed bytes and moved `_DEFAULT_BASELINE_ID` to
  `baseline-4`** (the 15.7 precedent — the committed canonical set scores against its own
  supply; baseline-3's block stays scoreable via `--baseline-id baseline-3`).
- **The genuine-class canary verdict is NO-DATA, not REGRESSION.** The §0.3 pre-registered test
  is arithmetically undefined at zero supplied opportunities; the phase-pausing arm requires a
  below-anchor cell at |z| ≥ 1.96, which cannot exist. Recorded with the supply collapse as a
  first-order finding (§6) rather than absorbed. The owner ratifies this reading by merging
  this PR — flagged explicitly in the PR description.
- **Re-recorded 9p2i seed 5 after its first take recorded a `(deadline_default)` phantom
  failed-call row** (the corpus-runbook remedy; the gate rejects the phantom class by design).
  Its MANIFEST row honestly stamps the re-record date.
- **`refreshed_at` provenance shape:** 9p2i stamps `2026-07-12` on 49 rows and `2026-07-13` on
  seed 5 alone (the phantom-remedy re-record, per the bullet above); 4p1i stamps `2026-07-13`
  on all 50 (the operator session crossed UTC midnight between the sets). The gate checks
  model/version/flag/cost coherence, not date uniformity — the mixed dates are the honest
  record of when each row's bytes were produced.
- **The Q5 annotated tag `phase-16-baseline-4` is created at the recording commit `a43b178`**
  (the sha every MANIFEST row stamps) but the execution environment's credential refuses TAG
  pushes (HTTP 403). Branch refs are permitted, so the recording commit is made durably
  reachable server-side by the holding branch **`phase-16-baseline-4-recording`** (pushed at
  `a43b178`) — squash-merge cannot orphan it. The owner completes the tag arm at leisure and
  drops the holder:
  `git fetch origin phase-16-baseline-4-recording && git tag -a phase-16-baseline-4 a43b178
  -m "Q5: Task 16.14 baseline-4 recording commit" && git push origin phase-16-baseline-4 &&
  git push origin :phase-16-baseline-4-recording`. (Belt-and-braces: GitHub also retains the
  commit via `refs/pull/266/head` after merge.)
- **The lab rubric artifacts** (`experiments/lab/results-rubric-*.json`) are committed alongside
  the 9p2i rubric — the refresh script writes them and the 15.7 baseline-3 PR (#236) committed
  them the same way.
- **`AILIBI_SEED_MAX_ATTEMPTS=8` for the 4p1i / seed-5 / champion legs** (the 9p2i run used the
  script's Featherless default of 4, which held at 4/4 on its deepest seed) — matching the
  baseline-3 operator record, whose own log shows a 7/8-attempt seed.

## 8. Method + reproduction (all $0 against committed bytes, offline)

```
uv run python scripts/validity_gate.py replays/samples/9p2i \
    --expected-model Qwen/Qwen3.6-27B --require-zero-cost    # PASS (10/10)
uv run python scripts/validity_gate.py replays/samples/4p1i \
    --expected-model Qwen/Qwen3.6-27B --require-zero-cost    # PASS (10/10)
uv run python scripts/measure_baseline.py --json                # §3 R-gate + canaries
uv run python scripts/measure_baseline.py --funnel --json       # §2 funnel (15.3 instrument)
uv run python scripts/measure_baseline.py --watchability --json # §4 referee (baseline-4 floors)
bash scripts/verify_samples.sh                                  # byte-identical, BARE env
```

The BEFORE column is `audits/baseline3-final-measure.json` (captured at tip **beb2c07** by the
same CLIs — `--json`, `--watchability`, `--funnel` — on the baseline-3 bytes immediately before
replacement; the baseline-3 bytes survive only in git history there). The canary statistics are
the two §0.3 pre-registered formulas (pooled two-proportion z; Wilson 95% CI), computed from the
CLI cells quoted beside them in §3. The record itself ran `scripts/refresh_samples.sh --full`
per set under `AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b` (plus the 9p2i
roster env block) at the recording commit **a43b178**.
