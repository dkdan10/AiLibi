# Phase-15 Wave-0 close — baseline 3: the two measured evidence holes are closed, the deduction game got stronger, no canary regressed

**Date:** 2026-07-08
**Task:** 15.7 — baseline 3 (atomic re-record on the Wave-0 substrate: `qwen3_32b.v5` + `vote_ballot.v6`,
the `reporter_exculpation` lever graduated to unconditional) + the WAVE-0 CLOSE.
**Sets:** `replays/samples/9p2i` (50 games / 139 meetings / 851 ballots) + `replays/samples/4p1i`
(50 games / 39 meetings), this re-record.
**Model:** `Qwen/Qwen3-32B` (Featherless, both call kinds, non-thinking, `fail_loud`, `json_object`, $0).
**Substrate:** all SIX levers unconditionally ON — the four Phase-13.5 levers (since 14.9), Task-14.10
`evidence_quality_lift` (since the 14.12 close), and Task-15.5 `reporter_exculpation` (graduated in this
task) — stamped into MANIFEST `flags` + each replay's `game_over.substrate_flags`; prompt set
`qwen3_32b.v5` for the three 15.4-owned templates and `vote_ballot.qwen3_32b.v6` (15.5's per-template
bump). Recorded at `git_sha` **cdf0a4b** (the graduation commit — the code the record ran under); the
committed sets reconstruct BARE (no `AILIBI_*` export).
**Recording:** 2 parallel Featherless seed workers; wall ≈ **4.8h** for both sets, with intermittent
Featherless degradation windows absorbed by per-seed crash-retry (11 transient retries, **0 hard
failures**; max retries on any seed 7/8).
**Grounding:** every number below is a fold over the committed baseline-3 artifacts via
`scripts/validity_gate.py` + `scripts/measure_baseline.py` (core / `--watchability` / `--funnel`). The
BEFORE column regenerates from the committed `audits/baseline2-final-measure.json`, captured on the
baseline-2 bytes at tip **adca07f** immediately before this re-record replaced them (the baseline-2
bytes survive only in git history at adca07f). Zero hand-computed figures.
**Verdict in one line:** the two measured Wave-0 holes are CLOSED — witnessed vents are now structurally
speakable (structured vent observations **0 → 55** on 9p2i) and the reporter hole is shut
(innocent-reporter ejections **22 → 4**) — and the deduction game got STRONGER for it (9p2i ejection
accuracy **0.525 → 0.697**, genuine-class conversion **0.625 → 0.769**, both canaries UP), with the
impostor win rate easing (0.40 → 0.30) from genuinely better crew deduction, not a balance bug. Both
sets PASS the hard validity gate and the selection referee. No canary regressed. This is a VALID close.

---

## 1. HARD validity gate — PASS (both sets)

`validity_gate.py` over both committed sets (10/10 checks green each), cross-checked by `bash scripts/check.sh`:

| criterion | 9p2i | 4p1i |
|---|---|---|
| every game reaches game_over | 50/50 | 50/50 |
| meeting_rate / resolved meetings (bar ≥0.60 / ≥30) | 1.00 / 139 | 0.78 / 39 |
| tick-1 kills | 0 | 0 |
| friendly-fire (impostor-on-impostor) kills | 0 | 0 |
| betrayal ballots/accusations (§7.12 firewall) | 0 / 851 | 0 (single-impostor, vacuous) |
| railroaded crew ejections | 0 / 1495 | 0 / 97 |
| dangling `primary_reason_id` | 0 / 851 | 0 / 117 |
| cost rows ($0 Featherless flat-rate) | exact | exact |
| provenance rows (`Qwen/Qwen3-32B`, v5 set + `vote_ballot.v6`, 6 levers stamped) | exact | exact |
| byte-identical reconstruction (BARE env) | 0 drift | 0 drift |

`verify_samples.sh` reconstructs all 50+50 samples clean under a bare environment (roster.json present,
no `AILIBI_*` lever export): the `reporter_exculpation` lever was GRADUATED to unconditional in this task
(the 14.9/14.12 move), so the resolver's constant `True` keeps the belief fold byte-identical to the
recorded stamp and the committed set serves without any env flag.

**One check refinement (documented, owner-approved).** The betrayal check
(`eval.validity.check_no_betrayal`) initially flagged **3 impostor SELF-accusations** (`p-1→p-1` on
seed 35; `p-7→p-7` on seed 48 ×2) — a v5 dialogue artifact where an accused impostor echoes an
accusation naming ITSELF. The §7.12 firewall the check verifies drops only FELLOW impostors
(`meetings.manager.fellow_impostor_ids` = "the OTHER impostors", manager.py:496); self is deliberately
excluded because accusing yourself betrays no teammate. There are **zero cross-teammate betrayals**. The
check was strictly stricter than the firewall it validates, so it was refined to exclude self-targeting
(`against != speaker` / `target != voter`), with a regression test (self excluded; cross-teammate still
caught). The self-accusation itself is a Phase-16 dialogue-quality finding (§5), not a firewall breach.

## 2. The information funnel re-measured — the wave's own instrument (baseline 2 → baseline 3)

`eval.funnel` (Task 15.3), the same three-stage instrument before and after. The Wave-0 target sheet's
four rows plus context (9p2i):

| funnel row | baseline 2 | **baseline 3** | read |
|---|---|---|---|
| **structured vent observations** (15.4 mechanism) | 0 | **55** | the hole is CLOSED — held vents are now speakable |
| vent mentioned (free text) | 36 | **53** | v5 elicitation lifted transmission (of 73 held) |
| **innocent-reporter ejections** (15.5 lever) | 22 | **4** | the reporter hole is shut (all 4 still innocent) |
| votes outside a ≤3 candidate set | 37 | **30** | fewer off-set votes (of 64 small-set ejections) |
| report-meeting ejections | 106 | 95 | — |
| killer accused | 76 | 75 | ~flat |
| oracle candidate-set median | 3 | 3 | diagnostic ceiling unchanged |
| killer-in-set (±1 window) | 122 | 109 | ~flat (re-record variance) |
| hard clue held | 98 | 98 | identical held-evidence supply |

The headline: **vent transmission 36/74 → 53/73, and 55 of those are now STRUCTURED** (citeable,
contradiction-detectable turns) where baseline 2 had zero. The reporter damp cut innocent-reporter
convictions **22 → 4**. Both are exactly the transmission gains Wave 0 set out to make speakable.

4p1i (the flat determinism/leak reference, sole impostor, sparse supply) mirrors the vent gain
(structured vents **0 → 6**) but shows the reporter cell moving the OTHER way (innocent-reporter
ejections **1 → 3**, report-meeting ejections **10 → 22**): the small set became more eject-happy
this re-record. On a 39-meeting single-impostor set that is run-to-run variance, and it is a **finding**,
not a pass bar (§5).

## 3. R-gate re-measured + the Phase-14 canaries (9p2i, vs the baseline-2 anchors)

Per the charter the R-gate is a MEASUREMENT on a valid baseline. Directions are findings; the ONLY
NO-GO is a canary regression — and neither canary regressed.

| term | baseline 2 | **baseline 3** | read |
|---|---|---|---|
| **genuine-class conversion** (canary) | 0.625 | **0.769** (10/13) | UP — the over-damping canary did NOT fire |
| **R1 eject-decided win share** (canary) | 24/50 | **34/50** | UP — the game is MORE deduction-driven, not collapsed |
| ejection accuracy | 0.525 | **0.697** (76 imp / 33 crew of 109) | UP — crew mis-ejects fell 56 → 33 |
| impostor win (floor ≥0.14) | 0.40 | **0.30** | eased; floor holds — from better crew deduction |
| reason histogram | `{EJECT 24, PARITY 20, TASKS 6}` | `{EJECT 34, PARITY 15, TASKS 1}` | eject-decided crew wins up, impostor parity wins down |

**Neither defined failure mode triggered.** Genuine-class conversion held/ROSE (0.769 → the seed-level
genuine catches still convict); R1 did NOT collapse (it rose — the deduction game is more, not less,
alive); no railroad, no friendly-fire, no betrayal. The impostor win rate fell because the vent/reporter
substrate gave the crew genuinely more to deduce with — the watchability contract accepts any win-rate
movement from smarter play provided the gate + referee pass (they do, §4).

4p1i: ejection accuracy 0.923 → **0.808** (21 imp / 5 crew of 26 — the more eject-happy small set),
impostor win 0.38 → **0.28**, genuine-class conversion 1.0 → **1.0** (3/3). Findings on the reference
set; the canonical 9p2i result is the close.

## 4. Selection referee + evidence-supply floors — PASS (both sets, baseline-3 floors pinned)

`measure_baseline.py --watchability` reads the per-baseline floor block; this task pins the **baseline-3**
floors from the committed bytes (each set passes at equality), and moves `_DEFAULT_BASELINE_ID` to
`baseline-3` so the canonical set scores against its own supply.

| supply gauge (9p2i) | baseline 2 (floor) | **baseline 3 (floor)** |
|---|---|---|
| witnessed_event_rate | 0.0375 (6/160) | **0.03247** (5/154) |
| flags_per_meeting | 2.007 (285/142) | **1.863** (259/139) |
| testimony_backed_conversion | 0.4375 (56/128) | **0.6068** (71/117) |

Both sets PASS the referee (supply floors + the D1–D4 geomean; 9p2i mean score 39.83, 4p1i 9.07). The
finding within: the witnessed-kill rate and flags/meeting eased slightly while **testimony-backed
conversion rose sharply (0.44 → 0.61)** — the held evidence that IS present converts to a correct
ejection better under the Wave-0 vent/reporter substrate. The floors are baseline 3's OWN supply, so a
later trained candidate that produces structurally less evidence than baseline 3 fails the referee.

## 5. Findings (directions, not pass bars — scoping Phase 16)

- **v5 impostor self-accusation (3/851 9p2i ballots).** An accused impostor sometimes emits an
  accusation naming ITSELF. Firewall-clean (§1) but a dialogue-quality artifact of the v5 elicitation
  prompts. Phase-16 Voice & Judgment work; not iterated here (record-only discipline).
- **v5 vent uptake is real but partial.** 55 structured vent observations landed (0 before), and free-text
  vent mentions rose 36 → 53 of 73 held — but 18 held vents still go unspoken. The mechanism works; the
  model's uptake is a FINDING that scopes further prompt work, not a reason to iterate inside this task.
- **4p1i reporter/eject uptick.** The sole-impostor reference set became more eject-happy (report-meeting
  ejections 10 → 22, innocent-reporter 1 → 3, ejection accuracy 0.923 → 0.808) while impostor win still
  fell (0.38 → 0.28). Run-to-run variance on a 39-meeting set; watch it at the next re-record.

## 6. Decisions

- **Graduated `reporter_exculpation` at the record (both halves of the 14.9/14.12 move):** the resolver
  returns constant `True` and the registry entry moved `_TOGGLEABLE_LEVER_RESOLVERS` →
  `_RETIRED_ALWAYS_ON_LEVERS`. Discharges the C6 recording-preflight hazard (no lever env to forget) and
  keeps the recorded 6-flag stamp byte-consistent with the bare code.
- **Refined `check_no_betrayal` to exclude self-targeting** (owner-approved, §1): the firewall invariant
  (no FELLOW-impostor betrayal) holds; the check was over-broad. A correctness fix, not a suppression.
- **Moved `_DEFAULT_BASELINE_ID` to `baseline-3`** (and the `measure_baseline.py --baseline-id` default
  tracks it): baseline 3 is the committed canonical set, so a bare referee run scores against its own floors.

## 7. Method + reproduction (all $0, offline, committed bytes)

```
uv run python scripts/validity_gate.py replays/samples/9p2i     # PASS (10/10)
uv run python scripts/validity_gate.py replays/samples/4p1i     # PASS (10/10)
uv run python scripts/measure_baseline.py --json                # §3 R-gate + canaries
uv run python scripts/measure_baseline.py --funnel --json       # §2 funnel (15.3 instrument)
uv run python scripts/measure_baseline.py --watchability --json # §4 referee (baseline-3 floors)
bash scripts/verify_samples.sh                                  # byte-identical, BARE env
```

The BEFORE column is `audits/baseline2-final-measure.json` (captured at tip **adca07f** by the same
CLIs — `--json`, `--watchability`, `--funnel` — on the baseline-2 bytes immediately before replacement).
