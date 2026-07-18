# The multi-finalist recorder + the real-LLM finalist eval (Task 17.14)

> **Task:** 17.14 (`tasks/phase-17.md`) — the multi-finalist recorder + the
> real-LLM finalist eval (operator, $0). **Depends on:** 17.12 (the impostor
> bake-off re-run, which named the finalists and froze their artifacts).
> **Consumers:** 17.16 (the evidence-gated default flip) reads the win edge +
> referee verdict below against locked decision 2.
>
> **What this task productizes.** The Phase-15 pause recorded its two finalists on
> the real meeting path with a **~90-line uncommitted Python driver** because
> `scripts/run_tournament.py` carried a `--tactical-policy-stamp` flag but **no
> agent-factory flag**, so the stamp CLI alone could not drive a learned policy
> (`audits/audit-phase-15-pause.md:141-145`). Task 15.21 added `--agent-factory
> learned-champion`, but that loads only the **one committed champion**
> (`scripts/run_tournament.py` `_build_learned_champion_factory` →
> `load_champion_weights()`). Evaluating **multiple** new finalists needs a
> recorder that loads an **arbitrary** candidate artifact by path. This task adds
> `--candidate-artifact` — the productized recorder — and this report is its
> runbook + the evidence-table skeleton the operator leg fills.
>
> **Substrate (baseline 5):** `Qwen/Qwen3.6-27B` on Featherless, prompt set
> `qwen3_6_27b` v3, the nine always-on levers, `absence_prior` OFF
> (`audits/audit-phase-16-close.md`; the 17.7 STAY-OFF ruling). $0 flat-rate.
> **Selection floors:** `training/bakeoff/harness.py::BAKEOFF_BASELINE_ID =
> "baseline-5"`, `eval/watchability.py::_DEFAULT_BASELINE_ID = "baseline-5"`.
>
> **Finalists (from 17.12 §8):** `utility-es` and `policy-es`. Their committed
> artifacts + five-field `stamp.json` live under
> `training/artifacts/impostor/<entrant>/`.
>
> **Status of this PR.** The recorder (§1) and its fixture-pinned tests are
> **committed and green**, and the 50-seed real-LLM eval (§2) is **DONE**: both
> finalists recorded 50/50 on the real Featherless baseline-5 path (2026-07-18,
> $0), stamp‑proof (50/50 stamp==sidecar each) and validity-gate PASS, committed
> to `training/reports/results-finalist-eval.jsonl` (§3.a). **Headline:**
> utility-es holds a real impostor edge (win 0.52, Δ **+0.16** vs the same-seed
> FSM 0.36) but FAILS the referee on the starved conversion economy;
> policy-es collapses on the vent tell (win 0.02, Δ **−0.34**), referee PASS but
> competitively annihilated. Neither clears locked-decision-2's referee-PASS
> AND retained-edge bar, so 17.16's finding is: champion stays opt-in, default
> stays scripted (§4).

---

## 1. The recorder — `scripts/run_tournament.py --candidate-artifact` (committed)

The recorder generalizes the champion factory's entry point rather than writing a
second loader: it **reuses** `training.bakeoff.harness.load_candidate_weights`
(the sha-verifying reload the bake-off already froze artifacts with) and
`build_candidate_factory` (the candidate's own agent factory), and rebuilds the
inference policy through the committed builder the artifact's `encoder_version`
selects.

```bash
uv run python scripts/run_tournament.py \
  --candidate-artifact training/artifacts/impostor/utility-es \
  --start-seed <seed> --num-games 1 \
  --num-players 9 --num-impostors 2 --tasks-per-crewmate 2 \
  --output-dir <stage> --force
```

Semantics (all fixture-pinned in
`tests/scripts/test_run_tournament_candidate_artifact.py`):

- **Load + sha-verify, fail loud before any spend.** The genome is read via
  `load_candidate_weights(artifact_dir)`, which raises on any `weights.json` vs
  `weights.json.sha256` drift; the recorder converts that to a non-zero
  `SystemExit` **before** a single game runs (no LLM call is made on a bad
  artifact).
- **Rebuild by encoder_version.** `impostor-option-features-v1` →
  `utility_es.build_utility_scorer_policy`; the `v2` masked-MLP family
  (policy-es / bc-dagger / map-elites) → `policy_es.build_masked_mlp_policy`
  with `hidden` read from the artifact's `config.json`. A rebuilt policy whose
  `encoder_version` disagrees with the stamp fails loud.
- **Auto-stamp from the artifact's OWN `stamp.json`** — never the committed
  champion's constants. The five-field `TacticalPolicyStamp` is stamped onto
  every game's `game_over` record, so `orchestrator.replay.read_tactical_policy_stamp`
  reads it back from the bytes (never echoed from the launch config).
- **The conflation guard.** The stamp's `weights_sha256` **must** equal the
  sidecar digest; a `stamp.json` naming a different artifact fails loud. The
  loader binds **one** candidate per invocation and the stamp names it — two
  learned movers can never share a recording (the 17.14 integration risk). No
  module-level state leaks between runs.
- **Mutually exclusive** with `--agent-factory learned-champion` (the artifact,
  not the flag, selects the policy); an explicit `--tactical-policy-stamp` must
  match the artifact stamp field-for-field (the two-direction 15.21 guard,
  shared with the champion path).

The committed champion surface (`agents/tactical/learned/`) is **untouched** —
its swap is 17.16's, after this eval.

---

## 2. The fixed protocol (the operator leg)

Cloned from the Phase-15 finalist recipe (`audits/audit-phase-15-pause.md`
§3.1), re-based on the baseline-5 substrate and the 16.14/16.17 concurrency
notes (`audits/audit-phase-16-close.md` §0.5).

- **Per finalist:** seeds **0–49** (the canonical `replays/samples/9p2i` seed
  set), roster **9p/2i** at `tasks_per_crewmate=2`, `max_ticks` default,
  `--force`. One finalist at a time into its own `--output-dir`.
- **Environment (and nothing else):**
  `AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b
  AILIBI_SEED_MAX_ATTEMPTS=8` with `FEATHERLESS_API_KEY` set; model
  `Qwen/Qwen3.6-27B` (meeting + trigger), $0 flat-rate. `AILIBI_ABSENCE_PRIOR`
  unset (bare levers).
- **Concurrency (the 16.14 §6 finding):** **2 parallel Featherless seed
  workers** (the plan's 4-unit cap at 2 units/request), **staggered starts,
  jittered backoff, per-seed atomic staging, crash-retry budget ≥ 8**. A game's
  ballot phase can hold both plan slots, so the other worker's game 429s when
  phases collide — the retry budget absorbs it; the tail goes single-worker.
  The recorded-parse-failure `(deadline_default)` phantom is a FAILED recording
  and the seed re-records clean.
- **Provenance separation:** the raw recordings are working artifacts — they
  live **outside** the repo tree, do NOT join `replays/samples/` or
  `replays/ml_corpus/`, and are re-recordable from this recipe. What is
  committed is their **measurement** (§3, the jsonl).

Wall-clock ≈ 5–8 h per finalist at 2 workers (baseline-5 meetings ≈ 2×
baseline-3's ~2.5–3 h); ≈ 10–15 h total.

---

## 3. The evidence table

Columns follow the Phase-15 finalist table
(`audits/audit-phase-15-pause.md` §3.2). The **stamp proof** column is the
machine-checkable evidence that the loaded candidate — not the FSM wearing a
label — produced the bytes: all 50 games carry the five-field `tactical_policy`
stamp read back from the recording, uniform, with `weights_sha256` equal to the
committed sidecar digest.

### 3.a Baseline 5 (RECORDED — the committed `results-finalist-eval.jsonl`)

Recorded 2026-07-18, `AILIBI_LLM_PROVIDER=featherless`, model `Qwen/Qwen3.6-27B`,
prompt set `qwen3_6_27b` v3, `absence_prior` OFF, **$0**. 50 seeds (0–49) 9p/2i
each.

**Provenance durability (Q5 convention).** Each row's `recording.recording_git_sha`
names the **recorder-code commit** `2a9b369` — the commit that introduced the
`scripts/run_tournament.py --candidate-artifact` recorder that produced these
bytes (unchanged for the rest of the branch). That recorder is a **committed,
in-scope file** in this PR, so it lands on `main` via the merge and the exact
recorder is retrievable from `main`'s history regardless of the branch's
`wip: promote` commits squashing away. Per the Q5/16.14 durability convention the
SHA is **back-filled to the squash-merge landing SHA on merge** (the annotated-tag
arm is unavailable — this remote rejects tag pushes). The recordings are
re-recordable from that recorder + §6.

The
stamp proof held on every recording: all 50 games per finalist carry the
five-field `tactical_policy` stamp read back from the bytes, uniform, with
`weights_sha256` equal to the committed sidecar — the machine-checkable evidence
the loaded candidate (not the FSM wearing a champion label) produced the bytes.

| finalist | stamp==sidecar (50/50) | validity gate | referee mean/med (passed) | imp. win | Δ vs FSM | ej. accuracy | genuine conv. | witnessed rate | flags/meeting | backed conv. |
|---|---|---|---|---|---|---|---|---|---|---|
| utility-es | yes (`6d327dcb…`) | **PASS** | 41.47 / 42.7 (**FAIL** — 2 gauges) | **0.52** | **+0.16** | 0.866 (58/9 of 67) | 1/1 (1.0) | 0.2078 (48/231) | 0.4255 | **0.3585** (floor 0.5601) |
| policy-es | yes (`561e5ff3…`) | **PASS** | 48.20 / 49.6 (**PASS**) | **0.02** | **−0.34** | 1.000 (97/0 of 97) | 0/0 (NO-DATA) | 0.1194 (8/67) | 1.7748 | 0.9417 (floor 0.1343) |
| **baseline 5 (FSM, same seeds 0–49)** | fsm-default | **PASS** | **42.25** / 0.2 (**PASS**) | **0.36** | — | 0.914 (64/6 of 70) | 0/0 (NO-DATA) | 0.03448 (7/203) | 0.50279 (90/179) | 0.4741 (64/135) |

The FSM row is the committed baseline-5 scripted comparator: it **is** seeds 0–49
at this exact substrate (`replays/samples/9p2i`, 16.17 close re-record,
git_sha `2428044`, MANIFEST 32 CREWMATES / 18 IMPOSTORS). The **win edge** each
finalist reports is its impostor win rate minus this FSM `0.36` on the same
seeds and substrate (the house convention;
`audits/audit-phase-16-baseline-4.md` "edge over the same-substrate FSM
baseline").

**utility-es on the real baseline-5 path — a real edge, referee-starved.** Win
**0.52** vs the FSM baseline's 0.30… **0.36** — Δ **+0.16**, 26 impostor wins all
by parity — inside games markedly evidence-RICHER than the FSM (witnessed rate
0.208 vs 0.034, z **+5.42σ**). But it FAILS the referee on two supply gauges:
flags/meeting 0.4255 < 0.5028, and testimony-backed conversion 0.3585 < its
population-relative floor 0.5601 (the floor RISES to 0.560 precisely because the
starved flag supply lifts it, §3.1). This is the selection-bar honesty ruling
working: a co-adapted impostor makes convictions harder — exactly what the
conversion floor prices — so the FAIL is the instrument reading a starved
economy, legible beside the win edge, not a silent rejection.

**policy-es on the real baseline-5 path — the vent-tell collapse, again.** Win
**0.02** (1 of 50, Δ **−0.34**); crew win 49/50, 47 by ejection, ejection
accuracy **1.000** — every one of its 97 ejections is a true impostor. It clears
the referee (48.20 PASS) only because the crew reads its play trivially: heavy
flag supply (1.775/meeting) and near-perfect backed conversion (0.942) are the
crew converting the vent tell into ejections. Same competitive annihilation the
Phase-15 pause recorded (0/50 there), re-confirmed on the co-adapted layer.

### 3.b Baseline 3 (the prior-substrate reference — from the Phase-15 pause)

Source: `audits/audit-phase-15-pause.md` §3.2 (recorded 2026-07-10 on
`Qwen/Qwen3-32B`, `qwen3_32b`, the pre-16 substrate). Carried here as the
before/after — the committed `results-finalist-eval.jsonl` now holds the
baseline-5 rows (§3.a); these baseline-3 numbers survive in that audit and git
history.

| finalist | stamp==sidecar (50/50) | validity gate | referee mean/med (passed) | imp. win | ej. accuracy | genuine conv. | witnessed rate | flags/meeting | backed conv. |
|---|---|---|---|---|---|---|---|---|---|
| utility-es | yes (`6d327dcb…`) | PASS | 46.62 / 48.3 (FAIL — one gauge, pre-15.19) | 0.38 | 0.613 (68/43 of 111) | 0.75 (9/12) | 0.2012 | 2.681 | 0.592 (floor 0.6068) |
| policy-es | yes (`561e5ff3…`) | PASS | 48.08 / 47.7 (PASS) | 0.00 | 0.99 (99/1 of 100) | 0.60 (6/10) | 0.0847 | 3.581 | 0.875 |
| (baseline 3, FSM, same seeds) | fsm-default | PASS | 39.83 / 47.5 (PASS) | 0.30 | 0.697 | 0.769 | 0.0325 | 1.863 | 0.607 |

**Baseline-3 → baseline-5 read.** Both movers' qualitative shapes **held** across
the substrate change: utility-es keeps a real impostor edge (0.38 → **0.52**;
edge over the same-seed FSM +0.08 → **+0.16**) but still misses the referee on the
conversion economy; policy-es stays competitively annihilated (0.00 → **0.02**,
the vent tell). The baseline-5 economy prices zero-flag convictions harder, which
widened utility-es's raw win rate while keeping its conviction gauges below floor
— the co-adaptation the phase set out to measure, not a ranking flip.

### 3.1 Floor sensitivity — the method (per finalist, per gauge)

Selection-bar honesty (`tasks/phase-17.md` "Designer rulings"): a starved-economy
rejection must be legible as the instrument working, so each finalist's cell
carries the **signed distance to each supply floor** (`measured − floor`) beside
the PASS/FAIL, and for the rare-event `witnessed_event_rate` floor a **statistical**
read, not just a distance. The baseline-5 9p2i floors
(`eval/watchability.py:755-762`):

| gauge | baseline-5 floor (pin) |
|---|---|
| `witnessed_event_rate` | 0.03448 (7/203) — rare-event, SE ≈ 0.0128 |
| `flags_per_meeting` | 0.50279 (90/179) |
| `testimony_backed_conversion` | 0.4741 (64/135), population-relative |

- **Population-relative conversion floor** (16.11): `floor = min(1.0,
  0.4740740740740741 × (0.5027932960893855 / measured_flags_per_meeting))`. A
  finalist that starves flags faces a HIGHER derived conversion floor — the
  economy prices co-adaptation directly.
- **Rare-event z (the 17.12 discipline).** `witnessed_event_rate`'s floor is a
  7/203 point estimate, so each finalist's cell carries the two-proportion z
  against the pin's numerator/denominator:
  `z = (p₁ − p₀) / √(p̂(1−p̂)(1/n₁ + 1/n₀))`, `p̂ = (x₁+x₀)/(n₁+n₀)`, floor side
  `x₀ = 7`, `n₀ = 203`; `x₁` = crew-witnessed kills, `n₁` = total kills over the
  50-seed set. A sub-1σ miss is labelled **within-noise** and the floor still
  gates — the verdict and noise columns sit side by side for the 17.16 owner
  reading.

### 3.1a Floor sensitivity — the recorded reading

| finalist | gauge | measured (raw) | floor (pin/derived) | distance | verdict | noise / clearance |
|---|---|---|---|---|---|---|
| **utility-es** | witnessed_event_rate | 0.2078 (48/231) | 0.03448 (7/203) | +0.1733 | **PASS** | z = **+5.42σ** |
| | flags_per_meeting | 0.4255 | 0.50279 (90/179) | −0.0773 | **FAIL** | starved supply |
| | testimony_backed_conversion | 0.3585 | 0.5601 (derived) | −0.2016 | **FAIL** | floor lifted by starved flags |
| **policy-es** | witnessed_event_rate | 0.1194 (8/67) | 0.03448 (7/203) | +0.0849 | **PASS** | z = **+2.63σ** |
| | flags_per_meeting | 1.7748 | 0.50279 (90/179) | +1.2720 | **PASS** | vent tell floods flags |
| | testimony_backed_conversion | 0.9417 | 0.1343 (derived) | +0.8074 | **PASS** | crew converts the tell |

Both witnessed-rate clearances are well beyond 1σ (no within-noise call needed).
utility-es's two FAILs are the conversion economy: its low flag supply (0.4255)
lifts the population-relative conversion floor to 0.5601, which its 0.3585
conversion misses — the co-adapted impostor making convictions harder, priced
exactly. policy-es passes every floor because the crew reads its vent play
trivially (flags flood, conversion near-perfect) — a PASS that coexists with a
0.02 win rate, which is why the referee is read WITH the win edge, never alone.

---

## 4. What 17.16 consumes — the verdict

Locked decision 2 flips the default mover iff the re-selected champion **PASSES
the baseline-5 referee** (supply floors + population-relative conversion +
geomean) **AND retains its win edge** at this real-LLM eval. Read against the
§3.a evidence:

- **utility-es**: win edge **YES** (0.52 vs FSM 0.36, Δ +0.16) but referee
  **FAIL** (flags/meeting and conversion below floor). Fails the AND.
- **policy-es**: referee **PASS** but win edge **NO** (0.02, Δ −0.34, collapsed).
  Fails the AND.

**Neither finalist satisfies referee-PASS AND retained-win-edge.** Under locked
decision 2 the champion therefore **stays opt-in** and the scripted FSM **stays
the default mover** — the 15.20/15.21 posture holds, and 17.16 records the finding
rather than flipping the default. The starved-economy referee FAIL on utility-es
is the selection bar working as designed (a co-adapted impostor prices harder
convictions), not a tooling defect. No baseline record here — 17.17 records
whatever substrate the mover layer closes on.

---

## 5. Definition-of-done status

- [x] **The recorder loads an arbitrary candidate artifact with sha verification
  (mismatch fails loud before any spend) and stamps every game row with the full
  15.9 provenance; fixture-pinned.** — `scripts/run_tournament.py`
  `--candidate-artifact`; `tests/scripts/test_run_tournament_candidate_artifact.py`
  (19 tests: exact stamp read-back for both finalists, weights-vs-sidecar and
  stamp-vs-sidecar mismatch fail loud before any recording, mutual exclusion,
  the two-direction explicit-stamp guard, default-path byte-identity). The
  recorder was additionally validated on the **real Featherless baseline-5 path**
  (not just the fake provider): a single-seed `--candidate-artifact
  training/artifacts/impostor/utility-es` run recorded a full 9p2i game — 5
  resolved meetings, model `Qwen/Qwen3.6-27B` + `qwen3_6_27b` v3 in the bytes,
  **$0** — whose `game_over` stamp read back (via
  `read_tactical_policy_stamp`) equals the artifact's own `stamp.json`
  (`utility-es`, `weights_sha256 6d327dcb…` == sidecar). That one game took
  ~20 min wall-clock — the empirical basis for the ~10–15 h estimate below.
- [x] **Every finalist's 50-seed eval is committed with stamp-proof rows,
  validity gate PASS, and the evidence table (win edge, referee scoring, floor
  sensitivity) in the report.** — Both finalists recorded 50/50 on the real
  Featherless baseline-5 path (2026-07-18, $0), stamp‑proof (50/50 stamp==sidecar
  each), validity gate **PASS** both, committed to
  `training/reports/results-finalist-eval.jsonl`; the evidence table (§3.a) +
  floor sensitivity (§3.1a) + the 17.16 verdict (§4) are recorded. Raw recordings
  are re-recordable working artifacts and are NOT committed (§2, §6).

---

## 6. Reproduce (the operator recipe)

**Record** (per finalist, into a scratch dir outside the repo tree; 2 staggered
workers, `AILIBI_SEED_MAX_ATTEMPTS=8`, per-seed crash-retry):

```bash
export AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b
export AILIBI_SEED_MAX_ATTEMPTS=8            # FEATHERLESS_API_KEY already set
for ent in utility-es policy-es; do
  for seed in $(seq 0 49); do                # shard across 2 staggered workers
    uv run python scripts/run_tournament.py \
      --candidate-artifact training/artifacts/impostor/$ent \
      --start-seed $seed --num-games 1 \
      --num-players 9 --num-impostors 2 --tasks-per-crewmate 2 \
      --output-dir "$WORK/$ent" --force
  done
done
```

**Score** (per finalist set — the committed CLIs, unchanged):

```bash
uv run python scripts/validity_gate.py "$WORK/$ent" \
  --json --expected-model Qwen/Qwen3.6-27B --require-zero-cost   # PASS
uv run python scripts/measure_baseline.py "$WORK/$ent" --json                       # core
uv run python scripts/measure_baseline.py "$WORK/$ent" --funnel --json              # funnel
uv run python scripts/measure_baseline.py "$WORK/$ent" --watchability \
  --baseline-id baseline-5 --json                                                   # referee
```

Drop the `*.audit.jsonl` sidecars before scoring (they collide with the scorer's
`replay-seed-*` glob), and ensure `roster.json` holds
`{"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2}` in the set dir.

**The stamp proof** (read back from EVERY recording, never echoed):

```bash
uv run python -c "
from pathlib import Path
from orchestrator.replay import read_tactical_policy_stamp
import json, sys
d = Path(sys.argv[1]); ent = sys.argv[2]
sidecar = (Path('training/artifacts/impostor')/ent/'weights.json.sha256').read_text().split()[0]
stamps = [read_tactical_policy_stamp(p) for p in sorted(d.glob('replay-seed-*.jsonl'))]
assert stamps and all(s is not None for s in stamps)
assert len({s.model_dump_json() for s in stamps}) == 1, 'stamps not uniform'
assert all(s.weights_sha256 == sidecar for s in stamps), 'stamp != sidecar'
print(ent, len(stamps), 'games, stamp==sidecar', sidecar[:12])
" "$WORK/$ent" "$ent"
```

**Assemble** each finalist's row (`artifact_path`, `committed_sidecar`,
`committed_weights_sha256`, `tactical_policy_stamp`, `stamp_equals_committed_sha256`,
`stamp_verified_games`, `recording`, `core`, `funnel`, `watchability`,
`validity_gate`) into `training/reports/results-finalist-eval.jsonl`, then fill
§3.a from the `core` / `watchability` cells and the FSM `0.36` comparator. The
floor-sensitivity columns (§3.1) derive from each finalist's `watchability`
`supply_gauges` rows (`measured − floor`) plus the rare-event z.

**The recorder's own regression proof** (offline, fake provider, $0):

```bash
uv run pytest tests/scripts/test_run_tournament_candidate_artifact.py -q
```

---

## 7. Decisions

- **Dispatch on `encoder_version`, not entrant name.** The reload seam keys on the
  artifact's own `stamp.json` `encoder_version` (`impostor-option-features-v1` →
  utility scorer; `v2` → masked-MLP), so an arbitrary finalist rebuilds through
  the committed builder the bake-off froze it with — no hard-coded entrant list.
- **`hidden` is read from `config.json`** for the masked-MLP family (a committed
  artifact parameter), fail-loud if absent — never a hard-coded `8`.
- **The conflation guard checks `stamp.weights_sha256 == sidecar digest`** on top
  of the genome sha verification, so a `stamp.json` copied from another artifact
  can never mislabel a recording.
- **`results-finalist-eval.jsonl` carries the baseline-5 measurement** — the
  operator run (§6) recorded both finalists 50/50 on the real Featherless
  baseline-5 path and this patch replaced the prior Phase-15 baseline-3 rows with
  the recorded baseline-5 rows (§3.a). The baseline-3 numbers survive as the
  before/after reference in `audits/audit-phase-15-pause.md` §3.2 and git history
  (§3.b), never fabricated.
