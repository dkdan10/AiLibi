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

---

# Part II — Phase 18 (Task 18.26): the slate + the pre-registration

> **Task:** 18.26 (`tasks/phase-18.md`, "Wave 4 — selection + close") — the
> real-LLM finalist eval (operator, $0). **Depends on:** 18.24 (the impostor
> campaign, which ratified the 4-arm impostor cut at merge `b19b952`) and 18.25
> (the crew campaign, merged `e9da533`, which named **no** crew finalist and
> handed off four F14-loadable diagnostics). **Consumers:** 18.27 reads both of
> its axes from here — axis 1 (the flip) from the win/referee cells, axis 2
> (emergence) from §13.
>
> **What Part II re-runs.** The Part I recorder (§1) and protocol (§2, §6) are
> unchanged and in-scope-frozen; what moves is the substrate (baseline 5 →
> **baseline 6**), the slate (2 arms → **9**), and the entry points (the 18.19
> `--crew-artifact` dual-stamp arm joins `--candidate-artifact`). The 17.14
> discipline carries over intact: stamp proofs read back from the bytes,
> validity gates, floor sensitivity with the rare-event z beside every verdict.
>
> **Substrate (baseline 6):** `Qwen/Qwen3.6-27B` on Featherless, prompt set
> `qwen3_6_27b`, the graduated levers **always-on in code** at baseline-6 (no
> lever env), `$0` flat-rate. Floors: the `"baseline-6"` pin block in
> `eval/watchability.py:787-821`; `_DEFAULT_BASELINE_ID = "baseline-6"`.
>
> **STATUS — this Part is a PRE-REGISTRATION, committed BEFORE ANY SEED RUNS.**
> The slate (§8), the protocol (§9), both pre-registered cells (§10, §11), the
> routed rider (§12), the instrument set (§13), the duration statement (§14) and
> the row plan (§15) are recorded in advance of the first recording.
> **Recordings are PENDING**; §16's tables are skeletons whose every result cell
> reads *pending*, and the results tables follow in a later commit on this
> branch. Part I above (the 17.14 baseline-5 record) is **untouched** — the
> phase-18 rows APPEND, history preserved per the 17.14 precedent.

---

## 8. The slate — 9 arms × 50 seeds (the ratified cut)

Every arm records the **same** canonical set: seeds **0–49** (the
`replays/samples/9p2i` seed set), roster **9p/2i**, `tasks_per_crewmate=2`,
`max_ticks` default, `--force`. 9 arms × 50 seeds = **450 games**.

### 8.1 The arms

| arm (entrant) | side / role | sha (short) | committed artifact dir (dir name == full `weights_sha256`) |
|---|---|---|---|
| `p18-imp-ea4bc955` | impostor finalist — **slate 1** | `ea4bc955…` | `training/artifacts/coevo/intermediates/run-02-utility-lambda4/gen-2/<sha>` |
| `p18-imp-bfd145cb` | impostor finalist — **slate 2** | `bfd145cb…` | `training/artifacts/coevo/runnerups/run-02-utility-lambda4/gen-9/<sha>` |
| `p18-imp-6d327dcb` | impostor finalist — **slate 3**, the incumbent control (same artifact as Part I's `utility-es` row, **re-recorded** at the phase-18 substrate) | `6d327dcb…` | `training/artifacts/coevo/run-01-utility-champion/impostor/gen-3/<sha>` |
| `p18-imp-7f73929d` | impostor finalist — **slate 4**, the F13 test arm; the **only** arm with `anchor_policy = filtered-bc-anchor` | `7f73929d…` | `training/artifacts/coevo/runnerups/run-03-utility-bcanchor/gen-8/<sha>` |
| `p18-fsm-comparator` | all-scripted comparator — the same-seed FSM row, recorded **FRESH at n=50** | `fsm-default` | (no artifact) |
| `p18-crew-c1-gen9` | crew **diagnostic** — vs the frozen champion `ea4bc955…` | `0bf179b7…` | `training/artifacts/coevo/run-c1-crew-owned-tasks/crew/gen-9/<sha>` |
| `p18-crew-c1-gen0` | crew diagnostic **control** — vs the frozen champion `ea4bc955…` | `bd6fdd0a…` | `training/artifacts/coevo/realpath-crew/controls/crew-owned-tasks-es-gen0` |
| `p18-crew-c2-gen9` | crew **diagnostic** — vs the frozen champion `ea4bc955…` | `515fc066…` | `training/artifacts/coevo/run-c2-crew-general/crew/gen-9/<sha>` |
| `p18-crew-c2-gen0` | crew diagnostic **control** — vs the frozen champion `ea4bc955…` | `888046d0…` | `training/artifacts/coevo/realpath-crew/controls/crew-utility-es-gen0` |

Full digests (the machine-checkable identities; each equals its directory name
where the dir is sha-named, and equals the committed `weights.json.sha256`
sidecar in every case):

- `ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f`
- `bfd145cb4883fa7fd0f009811cdc6e660b4f4a62105534f384afbb45b2c12ee8`
- `6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0`
- `7f73929d5b91f4afe67adc1b2ac7ca42bdd3ab1f49ed0393342ab21c7db0985e`
- `0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df`
- `bd6fdd0a030a01cc57f2ef8c95abf66f46d8cbc5ac270e04ae74a6cab587f19c`
- `515fc066f7aafc5d3603ab531adb9fe78cd496192c7565e9d8b4d3ff7b09a635`
- `888046d082daf62853c9d10d25dde04e20691c042dcd6a6609492d554ed569bf`

**The comparator row is recorded fresh.** The 18.24 backfill n=3
`ea4bc955`-vs-FSM rows remain a **screen** — never this task's comparator — and
the 18.24 §5.9 3-game comparator does **not** discharge it either. Part I's
baseline-5 FSM `0.36` is stale at this substrate and is never quoted forward
(the §1.3 comparator discipline; the task's own integration risk).

### 8.2 Loadability (the five-second F14 check)

F14 loadability is **re-verified at run time through the real entry points** —
`scripts/run_tournament.py::_load_candidate_policy` for the impostor arms and
`::_load_crew_artifact_policy` for the crew arms, not a bespoke loader — before
the first seed of each arm. **All arms green**, and in every case the artifact's
own `stamp.json` `weights_sha256` **== the directory name == the committed
sidecar digest**. The family-matched control pairing is **encoder-correct**:

| candidate | `encoder_version` | its gen-0 control | `encoder_version` |
|---|---|---|---|
| `0bf179b7…` (c1 gen-9) | `crew-option-features-v2` | `crew-owned-tasks-es-gen0` (`bd6fdd0a…`) | `crew-option-features-v2` |
| `515fc066…` (c2 gen-9) | `crew-option-features-v1` | `crew-utility-es-gen0` (`888046d0…`) | `crew-option-features-v1` |

A cross-family pairing would compare two different encoders and read as "crew
learning"; the pins above are what makes the gen-9-vs-gen-0 delta a **learning**
delta and not an encoder delta.

### 8.3 The crew block is DIAGNOSTIC, not champion selection

The 18.25 hand-off names **NO crew finalist** — no crew candidate cleared the
bars, and the four arrive UNRANKED by 18.25's own anti-laundering ruling. The
crew block here is the **owner-directed diagnostic (2026-07-29)**:

- **Four crew arms**, each **SINGLE-OPPONENT** against the frozen champion
  `ea4bc955…`: the two gen-9 candidates (`0bf179b7…`, `515fc066…`) plus their
  same-seed gen-0 controls.
- The **dual-opponent** shape in the 18.26 contract's opening (crew finalist vs
  both the scripted impostor and the frozen impostor champion) applies **only to
  a crew CHAMPION candidate**, which 18.25 named none of. It therefore does not
  bind here.
- **The gen-0 pairing at the same opponent is what isolates crew learning** —
  same seeds, same frozen opponent, same encoder family; the only moving part is
  the crew genome's generation.
- **Win conversion is read ONLY at n=50.** No n<6 crew win read is quoted as a
  result anywhere in this Part (the §4.0 lesson).

---

## 9. The recording protocol (baseline 6)

### 9.1 Environment and entry points

Provider `featherless`, model `Qwen/Qwen3.6-27B` (meeting + trigger), prompt set
`qwen3_6_27b`, **$0** flat-rate. The environment is **exactly**:

```bash
AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b AILIBI_SEED_MAX_ATTEMPTS=8
```

with `FEATHERLESS_API_KEY` **exported manually** — nothing auto-loads `.env`.
`AILIBI_IMPOSTOR_ROLL_CALL` stays **UNSET** (the baseline-6 crew-only ruling),
and the graduated levers are always-on in code at baseline-6, so there is **no
lever env** to set. Any other `AILIBI_*` in the recording shell is off-protocol.

Recording is **sharded one seed per invocation** through
`scripts/run_tournament.py`, with the per-arm flags:

```bash
# common to every arm
--start-seed $seed --num-games 1 \
--num-players 9 --num-impostors 2 --tasks-per-crewmate 2 \
--output-dir "$WORKROOT/$arm" --force

# impostor arms (4)
--candidate-artifact <artifact dir>

# crew arms (4) — the 18.19 dual-stamp entry point
--crew-artifact <crew dir> --candidate-artifact <ea4bc955 dir>

# the comparator (1) — neither artifact flag
--tactical-policy-stamp fsm-default
```

The crew leg's entry point is the one **18.32 deliberately never touched**, so
its dual-stamp semantics stand: the impostor `TacticalPolicyStamp` and the
`CrewTacticalPolicyStamp` land in **DISTINCT schema slots**, which is the
cross-stamp conflation guard — the crew read-back can never be mistaken for the
impostor read-back, in the bytes or in the row.

### 9.2 Working root, resume, provenance

- **Working root `~/ailibi-campaign-1826/`** — outside the repo tree, per the
  18.25 operator-root convention. Recordings are **working artifacts**: they do
  not join `replays/samples/` or `replays/ml_corpus/`, and they are re-recordable
  from this recipe. What is committed is their **measurement** (§15).
- As-recorded `replay_set_dir` paths stay **verbatim** in the measurement JSON,
  with a **prefix map** recorded beside them (the standing convention) — the
  bytes are never rewritten to look repo-relative.
- **Resume** = skip any seed whose replay already exists **and** reaches
  `GAME_OVER`. `run_tournament.py` has **no built-in resume**; this is an
  operator-side precondition check, and a partial replay is deleted and
  re-recorded rather than resumed mid-game.

### 9.3 Scoring and the stamp proof

Scoring is the Part I §6 recipe, re-based on baseline-6: drop the
`*.audit.jsonl` sidecars first (they collide with the scorer's `replay-seed-*`
glob), verify `roster.json` holds `{"num_players": 9, "num_impostors": 2,
"tasks_per_crewmate": 2}`, then

```bash
uv run python scripts/validity_gate.py "$WORKROOT/$arm" \
  --json --expected-model Qwen/Qwen3.6-27B --require-zero-cost
uv run python scripts/measure_baseline.py "$WORKROOT/$arm" --json
uv run python scripts/measure_baseline.py "$WORKROOT/$arm" --funnel --json
uv run python scripts/measure_baseline.py "$WORKROOT/$arm" --watchability \
  --baseline-id baseline-6 --json
```

**Stamp proof, per arm, read back from the bytes** (never echoed from the launch
config), via `orchestrator.replay`:

| arm class | read-back call | what must hold across all 50 games |
|---|---|---|
| impostor (4) | `read_tactical_policy_stamp` | stamp present, **uniform**, `weights_sha256 == committed sidecar` |
| crew (4) | `read_policy_stamps` → `.crew` / `.tactical` | **both** slots present and uniform: `.crew.weights_sha256 == the crew sidecar`, `.tactical.weights_sha256 == ea4bc955…` |
| comparator (1) | `read_tactical_policy_stamp` + `read_policy_stamps` | **PROVES opponent absence**: `fsm-default` stamp, **ZERO** games carrying a learned stamp, **no crew stamp** |

The comparator's proof is stated as a positive obligation because a silently
learned mover in the comparator row would invert every Δ in §16.

---

## 10. PRE-REGISTERED CELL 1 — the noise precondition

**Stated before any seed runs.** Per **arm × per referee gauge**, a **split-half
stability read** at this task's n=50.

### 10.1 The split and the statistic

- **H1 = even seeds** `{0, 2, …, 48}` — 25 games.
- **H2 = odd seeds** `{1, 3, …, 49}` — 25 games.
- `measured_noise(arm, gauge) = |gauge(H1) − gauge(H2)|`.

The split is fixed here, in advance, so it cannot be chosen after the fact to
flatter a gauge.

### 10.2 Threshold base per gauge (the standing baseline-6 9p2i pins)

| gauge | baseline-6 threshold base | 25% noise ceiling |
|---|---|---|
| `witnessed_event_rate` | **0.03389830508474576** (6/177, **non-advisory**) | 0.00847457627118644 |
| `flags_per_meeting` | **1.0909090909090908** (180/165) | 0.2727272727272727 |
| `testimony_backed_conversion` | pinned conversion **0.5735294117647058** (78/136); the gate uses the population-relative derived floor `min(1.0, 0.5735294117647058 × (1.0909090909090908 / measured flags_per_meeting))` | 25% of **the arm's own full-n derived floor** |

For the conversion gauge the threshold base of the noise test is **the arm's own
full-n derived floor**, not the pin — an arm that starves flags faces a higher
floor, and its noise must be judged against the bar it is actually gated on.

### 10.3 The verdict rule

> A gauge whose **measured noise exceeds 25% of its threshold** reads
> **UNRESOLVABLE** — a third verdict outcome beside PASS/FAIL,
> findings-not-failures (the §4.0 lesson priced at 40 h); **only gauges clearing
> the precondition feed 18.27's axis-1 ruling.**

UNRESOLVABLE is not a soft FAIL and not a soft PASS: it means the instrument
cannot resolve the question at this n, and the honest output is the finding that
it cannot. A gauge that reads UNRESOLVABLE is excluded from 18.27's axis-1
ruling by this pre-registration, not by a later judgement call.

### 10.4 Expectations, stated in advance

- **`flags_per_meeting` is the UNRESOLVABLE-prone gauge** on the meeting-scarce
  crew lineage. Committed evidence at n=3:
  `training/artifacts/coevo/realpath-crew/run-c2-crew-general/measurement-stability-c2.json`
  records `noise_to_threshold_ratio` **1.8333** (**183%**) against
  `flags_floor` 1.0909090909090908, versus **0.3303** (**33%**) on the
  meeting-rich c1 lineage
  (`…/run-c1-crew-owned-tasks/measurement-stability-c1.json`). If the c2 arms
  read UNRESOLVABLE on flags at n=50, that is this prediction landing, not a
  surprise.
- **`meeting_rate ≥ 0.60`** (`eval/validity.py::MEETING_RATE_FLOOR`) is watched
  **live** as the starvation floor on the general-base crew arms — a legs-level
  abort signal, checked while recording rather than discovered at scoring.

### 10.5 Floor sensitivity beside every verdict (the 17.12 discipline)

Beside **every** gauge verdict this Part records the **signed distance**
`measured − floor` and, for the rare-event `witnessed_event_rate`, the
two-proportion z:

```
z = (p₁ − p₀) / √( p̂(1−p̂)(1/n₁ + 1/n₀) ),   p̂ = (x₁ + x₀) / (n₁ + n₀)
```

with the **floor side `x₀ = 6`, `n₀ = 177`** at baseline-6 (the pin's own
numerator/denominator), `x₁` = crew-witnessed kills and `n₁` = total kills over
the arm's 50-seed set. **A sub-1σ miss is labelled within-noise and the floor
still gates** — the verdict and the noise read sit side by side for the 18.27
owner reading, exactly as §3.1 did for 17.16.

---

## 11. PRE-REGISTERED CELL 2 — the F13 cell (champions vs runner-ups)

### 11.1 The hypotheses, verbatim (before the first seed)

Champions (`6d327dcb…`, `ea4bc955…`) vs runner-ups (`bfd145cb…`, `7f73929d…`)
on the referee gauges, quoted from the contract (`tasks/phase-18.md:1925-1930`):

> **hypothesis A** (the ES trades evidence-supply for wins; runner-ups sit one
> step less far along the trade — predicts the runner-ups' gauge margins
> **PERSIST** at n=50)
>
> **hypothesis B** (n≤6 referee reads are noise — predicts the champion/runner-up
> gauge gap **VANISHES** at n=50)

### 11.2 Reporting form

Per referee gauge: each of the four arms' **n=50 measured value**, the **pooled
champion mean** vs the **pooled runner-up mean**, the **margin**, with the §10
split-half noise read **beside** it. A margin smaller than either side's
split-half noise is reported as such and cannot be read as support for A.

The **within-lineage pair** — `ea4bc955…` (intermediate gen-2) vs `bfd145cb…`
(runner-up gen-9), **both `run-02-utility-lambda4`** — is quoted as its **own
cell**: it is the one comparison where lineage is held constant and only the
champion/runner-up position moves, so it is the cleanest read on A vs B.

**The cell REPORTS; the ruling stays 18.27's.** Nothing in this Part declares A
or B confirmed.

### 11.3 Evidence honesty

- **Screening coverage was UNEQUAL**: slots 1–3 rest on **6-seed** screens, slot
  4 (`7f73929d…`) on a **3-seed** screen. Per 18.24 §4.0, **all screening gaps
  are within noise** — which is precisely why the n=50 read exists and why no
  screening rank is carried forward as evidence here.
- **The 18.24 §5.9 3-game comparator does NOT discharge this task's comparator
  row** (§8.1); `p18-fsm-comparator` is recorded fresh at n=50.
- Slot 4 is the **F13 gauge-hypothesis** arm. Promoting the win-rate-led
  alternative `11aa6863…` in its place would **change what slot 4 tests** (a
  win-rate arm for a gauge arm) and would be recorded as such. It was not done.

---

## 12. The routed rider — the crew-witnessed kill rate (from 18.25)

One instrument question rides in from 18.25: the **crew-witnessed kill rate ran
6.5×–15× corpus across all twelve 18.25 arms**, and at n=3 it is **confounded** —
too few kills per arm to separate a learned-crew observation effect from an
artifact of the small denominator and the opponent pairing.

**The read this task takes.** Kill-craft `crew_witnessed_kills / kills_total` per
crew arm **vs its own gen-0 control at the same frozen opponent** (`ea4bc955…`),
at n=50 — the pairing of §8.3. The corpus cell is
**12/505 = 0.0238** (`training/artifacts/coevo/realpath/baseline-cells-corpus.json`,
`kill_craft` 9p2i, baseline-6).

The **n=50 gen-9-vs-gen-0 comparator pair is what decides** whether the elevation
is a learned-crew observation effect (gen-9 above gen-0 at the same opponent) or
an artifact (gen-9 ≈ gen-0, both above corpus). Both outcomes are reportable;
neither is a failure.

---

## 13. The emergence instruments (18.27's second axis)

Computed **per arm over that arm's 50 recordings**, through the committed
in-tree instruments — never re-implemented at scoring time:

| instrument | entry point | note |
|---|---|---|
| deception | `eval.deception_instruments.compute_deception_instruments` | |
| kill craft | `eval.kill_craft.compute_kill_craft_report` | the **byte-completeness fence runs FIRST** on every recording dir |
| off-menu | `eval.off_menu.compute_off_menu_report` | denominators come **from the recordings directly** — per 18.24 §12 item 15 the committed sweep JSONs carry **no `off_menu_decisions` key** |
| roll-call coverage | `eval.funnel.compute_pooling_funnel` | the ratified **0.60** floor |

**Baseline cells are quoted from
`training/artifacts/coevo/realpath/baseline-cells-corpus.json`** — the
machine-readable, baseline-6 corpus regenerated **2026-07-27**. The 18.4 memo
**prose is baseline-5 and stale** per its own `_note` and is not quoted here;
where a baseline cell is needed it comes from the JSON.

---

## 14. Duration honesty — stated before recording

**The only derivable rate** is 18.25's committed leg logs: **36 games**,
**26368.604 s** summed seed `wall_seconds` = **7.3246 h** ⇒ **12.2077 min/game
serial** at a healthy provider. That rate was measured on **meeting-rich
crew-vs-champion games**.

| unit | at 12.2077 min/game serial | at the two-leg posture (effective) |
|---|---|---|
| one 50-seed arm | ≈ **10.2 h** | ≈ **5 h** |
| the 9-arm slate (≈ 450 games) | ≈ 91.6 h | ≈ **46 h** wall-clock |

sessioned with checkpoint-push. **Commitment: RE-PRICE from the first leg pair's
measured pace before trusting this projection.** The report will quote
**whichever posture actually ran** and **only log-derivable figures** — no
projected hour counts presented as measurements (the 18.25 §12 lesson). The
gate's "~5 h/finalist" is the two-concurrent-leg **effective** rate, not a serial
one, and is labelled as such wherever it appears.

---

## 15. The jsonl / row plan

The phase-18 rows **APPEND** to `training/reports/results-finalist-eval.jsonl`
under the §8.1 entrant names. **The two 17.14 rows (`utility-es`, `policy-es`,
baseline-5) stay in place** as the prior record — history preserved per the
17.14 precedent, never overwritten and never re-scored at baseline-6.

- **Impostor rows (+ the comparator) reuse the 17.14 row schema** —
  `artifact_path`, `committed_sidecar`, `committed_weights_sha256`,
  `tactical_policy_stamp`, `stamp_equals_committed_sha256`,
  `stamp_verified_games`, `stamp_source`, `recording`, `core`, `funnel`,
  `watchability`, `validity_gate` — with **baseline-6 watchability**.
- **Crew rows carry the dual identities in DISTINCT slots:** the row's **subject**
  fields describe the **crew artifact**, and the **frozen opponent's read-back**
  lives in its **own opponent fields**. This is **explicitly NOT** the
  realpath-v3 convention, where `stamp`/`stamp_*` hold the **impostor**
  read-back even on crew legs and `opponent_stamp` holds the **declaration** —
  copying that shape here would put the opponent in the subject slot and label
  four diagnostics with the champion's identity.
- **Exact crew-row field names are fixed at scoring time and pinned in
  `tests/training/test_finalist_eval_pins.py`** — the pins are what stop the
  convention above from drifting between the row writer and 18.27's reader.

---

## 16. The evidence tables — PENDING

Skeletons only; committed here so the shape is pre-registered with the cells.
Every result cell reads *pending* until the recordings exist.

### 16.a The selection table (columns follow §3.a, re-based on baseline 6)

| arm | stamp==sidecar (50/50) | validity gate | referee mean/med (verdict) | imp. win | Δ vs FSM | ej. accuracy | witnessed rate | flags/meeting | backed conv. |
|---|---|---|---|---|---|---|---|---|---|
| `p18-imp-ea4bc955` | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| `p18-imp-bfd145cb` | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| `p18-imp-6d327dcb` | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| `p18-imp-7f73929d` | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| `p18-fsm-comparator` | `fsm-default` (opponent absence proven) | pending | pending | pending | — | pending | pending | pending | pending |

### 16.b The crew diagnostic pairs (single-opponent, frozen `ea4bc955…`)

| crew arm | dual stamp (crew / tactical) | validity gate | meeting_rate (≥0.60) | crew win conv. (n=50) | witnessed kills / kills | flags/meeting (noise verdict) |
|---|---|---|---|---|---|---|
| `p18-crew-c1-gen9` | pending | pending | pending | pending | pending | pending |
| `p18-crew-c1-gen0` | pending | pending | pending | pending | pending | pending |
| `p18-crew-c2-gen9` | pending | pending | pending | pending | pending | pending |
| `p18-crew-c2-gen0` | pending | pending | pending | pending | pending | pending |

### 16.c Cell 1 — the split-half noise read (§10)

| arm | gauge | H1 (even 25) | H2 (odd 25) | measured noise | 25% of threshold | precondition | floor distance | z / clearance |
|---|---|---|---|---|---|---|---|---|
| *(one row per arm × gauge)* | | pending | pending | pending | pending | pending | pending | pending |

### 16.d Cell 2 — the F13 champions-vs-runner-ups cell (§11)

| gauge | `6d327dcb…` | `ea4bc955…` | `bfd145cb…` | `7f73929d…` | champion mean | runner-up mean | margin | split-half noise | reads toward |
|---|---|---|---|---|---|---|---|---|---|
| `witnessed_event_rate` | pending | pending | pending | pending | pending | pending | pending | pending | (18.27 rules) |
| `flags_per_meeting` | pending | pending | pending | pending | pending | pending | pending | pending | (18.27 rules) |
| `testimony_backed_conversion` | pending | pending | pending | pending | pending | pending | pending | pending | (18.27 rules) |

**Within-lineage pair** (`run-02-utility-lambda4`: `ea4bc955…` gen-2 vs
`bfd145cb…` gen-9) — pending, quoted as its own cell.

---

## 17. Decisions (Part II)

- **The crew block is single-opponent by owner directive, not by omission.** The
  contract's dual-opponent shape binds a crew CHAMPION candidate; 18.25 named
  none, so the diagnostic runs each crew arm against the frozen champion
  `ea4bc955…` and isolates learning through the same-seed gen-0 control (§8.3).
- **The comparator is re-recorded, never quoted.** Part I's baseline-5 FSM row
  and the 18.24 n=3 backfill rows are both non-comparators here; the substrate
  moved, so the FSM row is recorded fresh at n=50 (§8.1).
- **UNRESOLVABLE is pre-registered as a first-class verdict**, with its split and
  its 25% rule fixed before any seed, so a noisy gauge is a finding rather than a
  retro-fitted excuse (§10).
- **Crew rows do not inherit the realpath-v3 slot convention.** Subject fields
  hold the crew artifact; the opponent read-back gets its own fields; the pins
  in `tests/training/test_finalist_eval_pins.py` hold the line (§15).
- **Duration is quoted only where a log derives it.** One measured rate exists
  (18.25's 36 legs); everything past it is labelled a projection and is re-priced
  from the first leg pair (§14).
