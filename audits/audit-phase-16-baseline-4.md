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

**Verdict in one line:** _to be filled from the recorded bytes — GO/NO-GO per the §0.3 canary
bands._

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

## 1. HARD validity gate — _to be filled from the recorded bytes_

## 2. The information funnel re-measured (baseline 3 → baseline 4) — _to be filled_

## 3. R-gate re-measured + the canaries under the §0.3 bands — _to be filled_

## 4. Selection referee + evidence-supply floors (16.11 definition; baseline-4 floors pinned) — _to be filled_

## 5. The champion re-audit (finding, not blocker) — _to be filled_

## 6. Findings — _to be filled_

## 7. Decisions — _to be filled_

## 8. Method + reproduction — _to be filled_
