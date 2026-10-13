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

**Recording:** 2 parallel Featherless seed workers per set; wall ≈ **4h54m** (9p2i) + **43m**
(4p1i), per-seed crash-retry budget 8 (9p2i: 2 transient 429/transport retries; 4p1i: 0;
**0 hard failures**). One live-recording edge case, remedied per the corpus runbook exactly as
pre-registered in §0.5: 9p2i seed 5's first take recorded a wall-clock-miss
`(deadline_default)` phantom failed-call row ("opening turn (turn 0) defaulted (validation);
p-1 submitted no turn", 0 tokens, no real call — the same seed and the same class as the
16.14 record's one edge case); the validity gate rejects the phantom class by design and the
seed re-recorded clean in the same session at the same recording commit. All 100 MANIFEST rows
stamp `git_sha 2428044` (the slate/graduation commit — the code the record ran under) and
`refreshed_at 2026-07-14`.

**Verdict in one line:** baseline 5 is a VALID close record and the phase CLOSES — both sets
PASS the hard gate (`--expected-model Qwen/Qwen3.6-27B --require-zero-cost`, 10/10) and the
16.11 referee on the baseline-5 floors, and reconstruct byte-identically BARE (C6 discharged);
neither §0.4 canary arm fired (R1 lands AT the pre-registered band's inclusive edge, 25/50,
z = 1.830 — one fewer eject-decided win would have paused the phase; genuine-class conversion
is NO-DATA at 0/0 supplied, again); the named NO-GO pairing resolves NO — the zero-flag
conviction rate COLLAPSED 25/89 = 0.281 → 2/70 = 0.029 (z = 4.207, the falling direction, both
survivors CITED) while the voice tier moved toward diversity (echo rate 0.244 → 0.004,
distinct-2 0.159 → 0.288), so no rise exists to attribute to personas. The headline: the
citation chain is live end-to-end — citation compliance 0.505 → **1.000** (405/405 EJECTs
cited: 327 transcript turns + 146 observation ids, zero dangling), the J2 gate fired twice on
the recorded bytes (mark-and-coerce, visible), the J1 clamp fired visibly (seed 12's meeting-2
soft-only 0.60 row renders 0.59 in five voters' graphs), and crew mis-ejections halved 12 → 6
at ejection accuracy 0.865 → **0.914**. The costs are real and recorded: convictions are
harder (eject-decided wins 34 → 25, impostor win rate 0.24 → 0.36), testimony-backed
conversion eased 0.626 → 0.474, and roll-call uptake is partial (coverage 0.363) with the
genuine-class instrument still starved — all findings routed to Phase 17/18 (§6, §8), none a
pass-bar.

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

## 1. HARD validity gate — PASS (both sets)

`validity_gate.py --expected-model Qwen/Qwen3.6-27B --require-zero-cost` over both committed
sets (10/10 checks green each), cross-checked by `bash scripts/check.sh`:

| criterion | 9p2i | 4p1i |
|---|---|---|
| every game reaches game_over | 50/50 | 50/50 |
| meeting_rate / resolved meetings (bar ≥0.60 / ≥30) | 1.00 / 179 | 0.78 / 39 |
| tick-1 kills | 0 | 0 |
| friendly-fire (impostor-on-impostor) kills | 0 | 0 |
| betrayal ballots/accusations (§7.12 firewall) | 0 / 1057 | 0 (single-impostor, vacuous) |
| railroaded crew ejections | 0 / 1797 | 0 / 45 |
| dangling `primary_reason_id` | 0 / 1057 | 0 / 117 |
| cost rows ($0 Featherless flat-rate, `--require-zero-cost`) | exact | exact |
| provenance rows (`Qwen/Qwen3.6-27B`, 4 × `*.qwen3_6_27b.v3`, 9 levers stamped + `absence_prior` False) | exact | exact |
| byte-identical reconstruction (BARE env) | 0 drift | 0 drift |

`verify_samples.sh` reconstructs all 50+50 samples clean under a bare environment (no
`AILIBI_*` export): the three graduated levers and the six previously-retired levers stamp
`True` on every game_over record, `absence_prior` stamps `False` — the stamped flags equal the
§0.1.5 slate exactly, and the one remaining live toggle is default-OFF so bare recording and
bare reconstruction agree without any export (C6 discharged for the graduated set).

## 2. The close reading: 16.10's instruments before/after (voice ALONGSIDE zero-flag)

`measure_baseline.py --vj --json` on the committed bytes; BEFORE from the committed
`audits/baseline4-final-measure.json` `vj` block. The named pairing first — the judgment
channel and the voice tier in ONE table (9p2i):

| instrument | baseline 4 | **baseline 5** | read |
|---|---|---|---|
| **zero-flag conviction rate** | 25/89 = 0.2809 | **2/70 = 0.0286** | COLLAPSED (z = 4.207, falling; Wilson 95% CI [0.008, 0.098]) — the phase's target channel is shut |
| zero-flag typed split (soft / hard / unattr) | 15 / 10 / 0 | **2 / 0 / 0** | both survivors are soft-only AND CITED (a cited zero-flag EJECT is legitimate under J2 — the citation channel working, not leaking) |
| zero-flag crew / impostor | 9 / 16 | **1 / 1** | the mis-ejection arm of the channel is gone |
| **within-meeting echo rate** | 0.2438 | **0.0038** | 64× down — voices stopped parroting |
| response-skeleton share | 0.0705 | 0.0530 | down |
| distinct-skeleton ratio | 0.7728 | **0.8931** | up |
| distinct-1 / distinct-2 | 0.0448 / 0.1593 | **0.0840 / 0.2875** | lexical diversity roughly doubled |

**The persona-attribution question, answered:** the pre-registered §0.4.5 NO-GO arm (a
statistically resolved zero-flag RISE, persona-attributable by construction since J1/J2 only
push the channel down) cannot fire — the rate FELL by z = 4.207. Voice metrics moved
substantially AND the judgment channel closed simultaneously: the C10 ordering (persona text
strictly after the citation gate) delivered exactly the designed outcome. **The phase NO-GO
does not fire.**

The rest of the V&J table (9p2i):

| instrument | baseline 4 | **baseline 5** |
|---|---|---|
| citation compliance (EJECTs citing) | 265/525 = 0.5048 | **405/405 = 1.0000** |
| turn citations (valid / dangling) | 268 / 0 | 327 / 0 |
| observation-id citations (valid / dangling) | 0 / 0 (ids not rendered) | **146 / 0** |
| coerced zero-flag markers (J2 fired) | 0 (lever OFF) | **2** |
| nulled observation-id markers (16.5 validators) | 0 | 1 |
| ballot-confidence ECE / Brier / n | 0.1147 / 0.1689 / 525 | **0.0565 / 0.1074 / 405** |
| roll-call coverage mean (whereabouts claims) | 0.0 (0 claims) | **0.3629 (360 claims / 179 meetings)** |
| vouch rate mean / grounded-vouch share | 0.3923 / 0.6855 | 0.3279 / 0.6617 |
| absence-set size mean / median (vote-time fold) | 3.6375 / 4 | **3.0950 / 3** |
| whereabouts lies detected (rate) | 0 (—) | **6 (0.0167)** |
| integrity: provenance-sum breaches / rendered-row mismatches | 0 / 0 | **5 / 0** |

4p1i: zero-flag 9/19 = 0.474 → **0/10**; compliance 0.60 → **1.00** (24/24: 15 turn + 14
observation, 0 dangling); echo 0.034 → 0.000; roll-call coverage 0.573 (67 claims); whereabouts
lies 2; absence mean 1.897 → 0.692; integrity 0/0.

**The 5 provenance-sum breaches are the J1 clamp's signature, enumerated and explained:** all
five are one subject in one meeting (seed 12, `headless-seed-12:meeting-2`, subject p-2) whose
soft-only conviction-grade row (raw 0.60) renders clamped to 0.59 in five voters' ballot
graphs — the clamp deliberately keeps the raw typed provenance
(`test_clamps_the_scalar_but_keeps_raw_provenance`), so `0.5 + Σ(fields) = 0.60 ≠ 0.59` on
exactly the clamped rows. This is the gate WORKING, visible in bytes for the first time
(baseline 4 recorded the lever OFF, so the gauge could never see a clamped row). The gauge's
missing clamp-exemption is an instrument defect the close found — per the close doctrine it
becomes a Phase-17 eval-region contract (teach `_cross_check_graphs` the J1 exemption), never
a close edit. `rendered_row_mismatches` = 0: reconstruction matches the recorded prompt bytes
exactly, so the recorded substrate is coherent.

## 3. The information funnel re-measured (baseline 4 → baseline 5)

`eval.funnel` (the 15.3 instrument); BEFORE regenerates from the committed measure file,
AFTER from the committed bytes (9p2i):

| funnel row | baseline 4 | **baseline 5** | read |
|---|---|---|---|
| structured vent observations | 74 (of 100 vent meetings) | **83 (of 106)** | the vent channel strengthens again |
| vent mentioned (free text) | 75/100 | **82/106** | transmission 0.75 → 0.774 — the vent-tail ask moved it, modestly (§6) |
| innocent-reporter ejections | 1 | **0** | the reporter hole stays shut |
| votes outside a ≤3 candidate set | 12 (of 54) | **7 (of 41)** | vote discipline tighter again |
| report-meeting ejections | 79 | 61 | fewer, more accurate (§4) |
| killer accused | 88 | **101** | up |
| kill witnessed | 9 | 7 | small-sample wobble (witnessed-kill supply, §5 gauge: 7/203) |
| hard clue held | 125 | 133 | more held evidence (179 meetings vs 160) |
| killer-in-set (±1 window) | 136 | **156** | up |
| candidate-set median | 3 | 3 | diagnostic ceiling unchanged |

4p1i stays the determinism control: every pre-meeting held-evidence row is byte-identical
between baselines except `killer_placement_observed` 6 → 9 (a TESTIMONY-derived row — the
roll-call ask now places killers publicly); only the meeting-decided rows move
(report ejections 15 → 6, reporter-ejected 2 → 0, votes-outside 2 → 0), and the win split
moved 36/14 → 35/15 — the V&J layer is the only moving layer, byte-provable on this roster.

## 4. R-gate re-measured + the canaries under the §0.4 bands (9p2i, vs the baseline-4 anchors)

Per the pre-registration, directions are findings; the ONLY NO-GO is a §0.4 band violation —
and neither band fired. The R1 outcome demands the honesty note up front: **it landed exactly
ON the pre-registered band's inclusive edge.**

| term | baseline 4 | **baseline 5** | read |
|---|---|---|---|
| **R1 eject-decided win share** (canary) | 34/50 = 0.68 | **25/50 = 0.50** | pooled two-proportion z = 1.830 < 1.96 → NO REGRESSION under the pre-registered arm, at the band's exact lower edge (24/50 would have fired it, z = 2.026). Wilson 95% CI [0.366, 0.634] excludes BOTH ladder anchors (0.68, 0.68) → not UNDERPOWERED; the direction is real and the mechanism is visible in the reason histogram: EJECT 34 → 25, PARITY 12 → 18, TASKS 4 → 7 — convictions now demand citations, so fewer games END by ejection. Read WITH ejection accuracy (below): crew ejects less and is right more. |
| **genuine-class conversion** (canary) | 0/0 — NO-DATA | **0/0 — NO-DATA** | supply is ZERO again, exactly the §0.4.3 pre-registered outcome branch: the roll-call ask (360 placements landed) did NOT re-supply the alibi-contradiction instrument. Recorded confirmation that the genuine-class channel needs Phase-17/18 work beyond roll-call (§6, §8). |
| ejection accuracy | 0.865 (77 imp / 12 crew of 89) | **0.914 (64 imp / 6 crew of 70)** | crew mis-ejects halved 12 → 6 |
| impostor win (floor ≥0.14) | 0.24 | **0.36** | up 12pp — the flip side of harder convictions; floor holds wide. A finding, not a canary: the phase deliberately made zero-flag convictions expensive, and the impostor's price for that discipline is the Phase-17 training target |
| reason histogram | `{EJECT 34, PARITY 12, TASKS 4}` | `{EJECT 25, PARITY 18, TASKS 7}` | eject-decided share down; parity + task wins absorb it |
| accusation-claim ECE / n | 0.269 / 438 | 0.293 / 456 | ~flat, slightly more claims |
| vote-ballot ECE / n | 0.115 / 525 | **0.056 / 405** | ballots half as miscalibrated (and fewer — more skips) |
| missed-skip partition (impostor / invalid / inversions) | 89 (40 / 2 / 47) | **141 (42 / 0 / 99)** | crew now SKIPs under met thresholds roughly 2× more — the J3 "a call you cannot source is a call to SKIP" discipline overriding the suspicion-gate arithmetic in the citing direction. 2 of the 99 are the KNOWN 16.6-deferred over-count (the two J2-coerced SKIPs land in `threshold_inversions` because `compute_conversion_report` does not yet recognise the coercion marker — the partition learns the literal in Phase 17); the other 97 are voluntary. Correct skips rose 350 → 511. |

4p1i (continuity, findings only): R1 17/50 → 10/50 (two-proportion z = 1.577 — not a resolved
move at this n; Wilson CI [0.112, 0.330]); genuine-class 0/0 → 0/0 NO-DATA; ejection accuracy
0.895 → **1.000** (10/10, zero crew mis-ejects); impostor win 0.28 → 0.30.

Per the DEGRADED-Q3 rule the corpus is quoted as STALE CONTEXT only: `replays/ml_corpus/`
remains baseline-3/Qwen3-32B substrate (baseline-3-era 9p2i cells: genuine-class 34/52 =
0.654, R1 109/150 = 0.727) and is NOT same-substrate evidence for any baseline-5 cell — Phase
17 re-grounds it (§8).

## 5. Selection referee + baseline-5 floors — PASS (both sets; floors pinned, 16.11 definition)

This task pins the **baseline-5** floors in `eval/watchability.py`'s per-baseline block from
the committed bytes (each set passes at exact equality — the derivation self-consistency the
16.11 re-anchor guarantees) and moves `_DEFAULT_BASELINE_ID` to `baseline-5` (the 15.7/16.14
precedent).

| supply gauge (9p2i) | baseline 4 (floor) | **baseline 5 (floor)** |
|---|---|---|
| witnessed_event_rate | 0.05056 (9/178) | **0.03448 (7/203)** |
| flags_per_meeting | 0.5375 (86/160) | **0.50279 (90/179: 75 persisted vent + 15 re-derived)** |
| testimony_backed_conversion (subject-aware, population-relative) | 0.6260 (77/123) | **0.4741 (64/135)** |

**The population-relative conversion floor for the new population, with its derivation quoted**
(the 16.11 definition, `eval/watchability.py::population_relative_conversion_floor`):

```
floor = min(1.0, pinned_conversion × (pinned_flags_per_meeting / measured_flags_per_meeting))
      = min(1.0, 0.4740740740740741 × (0.5027932960893855 / measured flags_per_meeting))
```

The baseline itself measures flags 90/179, ratio exactly 1.0, so the derived floor equals the
pin (0.4740740740740741) and the measured 64/135 PASSES at exact equality. A future
evidence-starved candidate faces a sharpened demanded rate, never a free pass off the smaller
pin. The direction read is reported honestly: conversion eased 0.626 → 0.474 BECAUSE the
graduated judgment layer makes convictions demand cited evidence (J1 clamps conviction-grade
soft-only renders; J2 coerces uncited zero-flag EJECTs; crew voluntarily skips uncitable calls
— §4's inversion census) — the same games convict less often but far more accurately (0.865 →
0.914, mis-ejects halved).

4p1i: witnessed 1/61 = 0.01639 (numerator 1 → ADVISORY, the 15.19 rare-event rule),
flags_per_meeting 16/39 = 0.41026 (11 persisted vent + 5 re-derived), conversion 10/28 =
0.35714. Both sets PASS the referee (supply floors + integrity; 9p2i mean score 45.81 →
**42.25**, 4p1i 6.51 → **4.09**, median 1.3 → 0.2 — the 16.14 watch-flag on the sparse
roster's geomean eased further: only 10 ejections and 25 task-decided games; a Phase-17/18
watchability finding, not a floor).

## 6. Uptake findings per elicitation ask (findings, not pass bars — scoping Phase 17/18)

The 16.15 asks against measured compliance on the recorded bytes (record-only discipline —
none of these reopens 16.15 inside this task):

- **J3 citation-required confidence: COMPLETE uptake.** 405/405 EJECT ballots cite (327
  transcript turns + 146 observation ids, zero dangling on either channel; 4p1i 24/24). The
  observation-id channel is ALIVE — 146 private-evidence citations that could not exist
  before 16.5+16.15+this slate. The J2 gate fired only twice all set (both coerced to SKIP,
  markers in bytes) — the model almost never attempts an uncited zero-flag eject anymore.
- **Roll-call: PARTIAL uptake — the phase's named unhedged risk landed here.** 360 whereabouts
  claims over 179 meetings, coverage mean 0.363 (4p1i 0.573 on smaller rosters) — roughly a
  third of living players answer per meeting. It works (absence sets shrank: vote-time mean
  3.64 → 3.09, median 4 → 3; killer placements on 4p1i 6 → 9; SIX whereabouts lies caught by
  the 16.7 detectors — a channel that read zero forever), but it did NOT re-supply the
  genuine-class instrument (0/0 again): elicited placements are not yet convertible
  alibi-contradiction evidence at the fold. Phase-17/18 prompt work scoped: raise answer
  rate, and make placements land in the contradiction detectors' substrate.
- **The vent tail: MODEST movement.** Transmission 75/100 = 0.750 → 82/106 = 0.774; structured
  observations 74 → 83; the unspoken tail is 24/106 (was 25/100). The ask helps; the tail
  persists.
- **The self-accusation fix: HOLDS, zero recurrence.** 0 self-naming accusations in 456
  accusation claims (and 0 self-votes in 1057 ballots); the baseline-3 artifact (3/851) had
  already vanished at the model swap (0/438 on baseline-4 bytes) and stays gone under the
  rewritten impostor framing.
- **J2a provenance surface + voice:** ballot ECE halved (0.115 → 0.056) with the provenance
  split rendered; the persona layer moved every voice metric toward diversity (§2) with zero
  cost on the judgment channel — the C10 ordering thesis (louder voices only AFTER the
  evidence bound) is measured, not assumed.
- **Vouching eased** (rate 0.392 → 0.328, grounded share 0.686 → 0.662) — more talk budget
  spent on roll-call/citations, less on vouches; watch at the Phase-17 re-measure.

## 7. Provenance

- **MANIFEST provenance exact per seed** (both sets): `Qwen/Qwen3.6-27B`, the four
  `*.qwen3_6_27b.v3` stamps (the registry at HEAD is the version authority —
  `refresh_samples.sh` carries no version literal, and this check is the version proof the
  contract names), the nine-lever `flags` cell (`absence_prior` absent = False), policy
  `fsm-default`, `git_sha 2428044`, `cost_usd 0.0000`, `refreshed_at 2026-07-14` on all 100
  rows (single-day session; seed 5's remedy re-record landed the same day).
- **The recording commit is the slate/graduation commit** (`2428044`) — the 15.7 shape: the
  code the record ran under carries the slate, the graduated resolvers, and the §0
  pre-registration.
- **Q5 provenance point:** the annotated tag `phase-16-baseline-5` is created locally at
  `2428044`, but this environment's credential refuses tag pushes (HTTP 403 — the same
  limitation 16.14 §7 recorded) AND is scoped to the task branch only, so no holding branch
  was pushed either. The recording commit is durably reachable server-side via the task
  branch / the PR's `refs/pull/<N>/head` (GitHub retains it after merge), and the sha is
  stamped in every MANIFEST row (the Q5 alternative arm: the sha in the committed
  measurement rows). The owner completes the tag arm at leisure:
  `git fetch origin <this PR's merge commit or refs/pull/<N>/head> && git tag -a
  phase-16-baseline-5 2428044 -m "Q5: Task 16.17 baseline-5 recording commit" && git push
  origin phase-16-baseline-5`.
- **The 16.15 bump-in-flight prompt archive is RETIRED** (the PR #267 convention): the
  re-recorded stamps (`*.qwen3_6_27b.v3`) re-align with HEAD's registry, so the archived-v1
  walk covers no committed meeting — `tests/fixtures/prompt_archive/qwen3_6_27b_v1/` and the
  golden's `ARCHIVED_PROMPT_VERSION_SETS` entry are removed; the archive mechanism stays for
  any future bump-in-flight.

## 8. The permanent record: the Phase-17 staleness rule (re-stated) + the routed contracts

**Everything trained or selected before this close is PRIOR-SUBSTRATE-ANCHORED. Re-ground
before any training.** Specifically:

- **`replays/ml_corpus/`** is baseline-3/Qwen3-32B substrate — stale TWO rungs now. Its cells
  are context, never same-substrate evidence. `record_ml_corpus.sh`'s coupled pin block is
  re-pinned by this task to the baseline-5 substrate (model + set + v3 versions moved
  together, the stale-corpus notice rewritten) so the Phase-17 re-record runs at the close
  substrate by construction; until that re-record, the script's provenance checks legitimately
  refuse the committed corpus.
- **The surrogate** (`training/`, FO6-era) was fitted on baseline-3-substrate data; its
  fidelity numbers do not transfer.
- **The champion** (`agents/tactical/learned/`, `utility-es`) stays OPT-IN and
  baseline-4-audited: the 16.14 §5 re-audit figures are the recorded champion row — win edge
  +12pp over the same-substrate FSM baseline (0.36 vs 0.24), stamp-proven on all 50 games,
  validity gate PASS, 16.11 referee FAIL on its evidence-starved meeting economy (flags
  0.2988/meeting; derived conversion floor capped at 1.0). Those numbers are now ONE MORE
  rung stale: baseline 5 moved the meeting layer again. Phase 17 re-trains/re-selects under
  the baseline-5 substrate with the referee as the selection bar; the 15.20/15.21 deployment
  posture is unchanged by this close.
- **The absence prior** stays OFF (the §0.1.4 slate ruling): Phase 17 re-runs the set-size
  counterfactual on THESE bytes (roll-call live — the vote-time absent mean already fell
  3.64 → 3.09) and graduates at its own adopting record if warranted; the PR #264
  placement-substrate widening (vent sightings placing their subject) is decided WITH it.
- **Instrument contracts routed to Phase 17 (defects this close found — contracts, never
  close edits):** (a) the VJ provenance-sum gauge needs the J1 clamp-exemption
  (`eval/vj_instruments.py::_cross_check_graphs`; §2); (b) the conversion report's SKIP
  partition must learn `UNCITED_ZERO_FLAG_EJECT_MARKER` before any lever-ON gate-obedience
  read (`eval/meeting_quality.py`; the 16.6 deferral, now measured live: 2 of 99 inversions
  are coerced SKIPs); (c) the spectator chip for the coercion marker + the 16.5 observation
  marker (`api.replay_loader._BALLOT_PREFIX_MARKERS`, the deferred api-region task).
- **The genuine-class instrument** reads NO-DATA on the second consecutive substrate — Phase
  17/18 owns making elicited placements convertible (the §6 roll-call finding) or re-anchoring
  the instrument on channels this substrate actually supplies (vents, sightings,
  whereabouts-lies).

## 9. Decisions

- **The slate recorded three graduations + one stay-OFF** (§0.1) and the record matches it
  exactly (§1). The owner ratifies the slate, this close reading, and the two edge-of-band
  honesty calls below by merging this PR (the 15.18 convention).
- **R1 landed exactly on the pre-registered band edge (25/50) and the close PROCEEDS** — the
  §0.4.2 band is inclusive by pre-registration (REGRESSION iff ≤ 24/50), z = 1.830 < 1.96, and
  the accompanying mechanism read (§4: fewer-but-more-accurate convictions, parity/task wins
  absorbing the share) is the designed direction, not a deduction failure. Flagged
  prominently rather than absorbed: one fewer eject-decided win would have paused the phase.
- **The genuine-class canary verdict is NO-DATA, not REGRESSION** — the §0.4.3 pre-registered
  empty-anchor branch; the supply starvation stays a first-order routed finding (§6, §8).
- **provenance_sum_breaches re-pins to 5 with the J1-clamp explanation** (§2) — an instrument
  blind spot on the first lever-ON recording, routed to Phase 17; NOT a fold defect
  (`rendered_row_mismatches` 0; the clamp keeps raw provenance by design).
- **Re-recorded 9p2i seed 5 after a `(deadline_default)` phantom failed-call row** — the
  pre-registered §0.5 remedy, the same seed and class as 16.14's one edge case; the gate
  rejects the phantom class by design.
- **`audits/baseline4-final-measure.json` extends the measure-file convention with the `vj`
  block** — the 16.10 instruments exist at this capture (they did not at baseline-3's), and
  the §2 before/after must regenerate from a committed artifact like every other number.
- **The Q5 tag arm is deferred to the owner** (§7): tag pushes 403 under this credential AND
  the credential is branch-scoped, so the 16.14 holding-branch fallback was not available
  either; the sha rides every MANIFEST row and the PR ref.
- **`AILIBI_SEED_MAX_ATTEMPTS=8` for both legs** (the 16.14 §6 operator note); no commit
  landed between the two set refreshes; the lab rubric artifacts
  (`experiments/lab/results-rubric-*.json`) are committed alongside the 9p2i rubric (the
  15.7/16.14 convention).

## 10. Method + reproduction (all $0 against committed bytes, offline)

```
uv run python scripts/validity_gate.py replays/samples/9p2i \
    --expected-model Qwen/Qwen3.6-27B --require-zero-cost    # PASS (10/10)
uv run python scripts/validity_gate.py replays/samples/4p1i \
    --expected-model Qwen/Qwen3.6-27B --require-zero-cost    # PASS (10/10)
uv run python scripts/measure_baseline.py --json                 # §4 R-gate + canary cells
uv run python scripts/measure_baseline.py --funnel --json        # §3 funnel (15.3 instrument)
uv run python scripts/measure_baseline.py --watchability --json  # §5 referee (baseline-5 floors)
uv run python scripts/measure_baseline.py --vj --json            # §2 V&J instruments (16.10)
bash scripts/verify_samples.sh                                   # byte-identical, BARE env
```

The BEFORE column is `audits/baseline4-final-measure.json` (captured at tip **381832d** by the
same four CLIs on the baseline-4 bytes immediately before replacement; the baseline-4 bytes
survive only in git history there). The canary statistics are the §0.4 pre-registered formulas
(pooled two-proportion z; Wilson 95% CI) computed from the CLI cells quoted beside them in §4.
The two documented census folds quoted in §6 regenerate as follows, from committed bytes only:
the self-accusation census walks every `kind == "meeting"` row's transcript turns and counts
claims whose `against` equals the turn's `speaker` (0/456 on 9p2i, 0/92 on 4p1i; ballots with
`target == voter`: 0/1057, 0/117); the missed-skip partition cells are read directly from the
committed `tournament-eval-report.json` `conversion` block of each set. The record itself ran
`scripts/refresh_samples.sh --full` per set under
`AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b AILIBI_SEED_MAX_ATTEMPTS=8`
(plus the 9p2i roster env block) at the recording commit **2428044**, then
`--seeds 5` once for the phantom remedy at the same commit.
