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
> **STATUS AS PRE-REGISTERED — the historical snapshot, quoted unchanged.** The
> paragraph that follows was committed at **`bf50f79`, before any seed ran**, and
> is preserved verbatim as the record of what was fixed in advance:
>
> > **STATUS — this Part is a PRE-REGISTRATION, committed BEFORE ANY SEED RUNS.**
> > The slate (§8), the protocol (§9), both pre-registered cells (§10, §11), the
> > routed rider (§12), the instrument set (§13), the duration statement (§14) and
> > the row plan (§15) are recorded in advance of the first recording.
> > **Recordings are PENDING**; §16's tables are skeletons whose every result cell
> > reads *pending*, and the results tables follow in a later commit on this
> > branch. Part I above (the 17.14 baseline-5 record) is **untouched** — the
> > phase-18 rows APPEND, history preserved per the 17.14 precedent.
>
> **STATUS NOW — RECORDED.** All **nine** arms are recorded and scored, and the
> results tables landed in the later commits that paragraph anticipated (through
> **`3b93cbf`**). §8–§15 remain exactly as pre-registered, with one appended
> subsection (§14.1, the measured duration re-price §14 committed to). **§16 now
> holds the selection evidence 18.27 reads** — the selection table (§16.a), the
> crew diagnostics (§16.b), both pre-registered cells (§16.c, §16.d) and the crew
> lineage reading with the routed rider's answer (§16.e); §17.1 records the
> decisions taken during the operator run. Part I remains untouched.

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

### 14.1 Duration — the measured reading (the re-price this section committed to)

The pre-statement above stands unedited; this subsection is the **measured**
answer beside it. No projected hour count appears as a measurement.

**Sources — the inputs are committed, not workspace-only.** Every arm's row in
`training/reports/results-finalist-eval.jsonl` carries a **`leg_duration`** block:
`games_recorded_ok`, `retry_events`, `sum_wall_seconds_ok`, `first_event_at` and
`last_event_at` (with `post_pr_retry_leg` on `p18-imp-7f73929d`). Those nine
blocks are the **committed digest of the leg logs**, and every per-arm cell and
every aggregate below is read from them or computed arithmetically from them.
They reconcile exactly: **Σ `sum_wall_seconds_ok` = 348488 s** and **Σ
`games_recorded_ok` = 464** across the nine, the campaign's first and last
`leg_duration` timestamps are `2026-07-29T07:17:48Z` and `2026-07-31T18:00:06Z`,
and each arm's `last − first` reproduces its **leg elapsed** column to the
third decimal.

**What stays workspace-only.** The raw `~/ailibi-campaign-1826/leg-log-*.jsonl`
rows themselves — per-seed timings, `purity-retry` / `pass-done` / `leg-abort`
event streams — and `leg-log-stubborn.jsonl`, whose 11 stubborn-round attempts
(7821 s) have **no row block** and are quoted from the log. Those are the
re-derivation path; the row blocks are the evidence of record for every figure
below except the stubborn-round line.

**Per-arm, as logged.** `games_ok` is the leg's **recorded**-game count
(retries included), not the finalized scored set — the two differ wherever a
purity retry re-recorded a seed.

| arm | games_ok | retry events | recorded-game wall (s) | **in-leg rc99 wall (s)** | mean min/game (recorded) | leg elapsed (h) |
|---|---|---|---|---|---|---|
| `p18-imp-ea4bc955` | 52 | 5 | 46460 | **3059** | 14.891 | 14.295 |
| `p18-imp-bfd145cb` | 50 | 0 | 43056 | **0** | 14.352 | 12.223 |
| `p18-imp-6d327dcb` | 50 | 2 | 44529 | **1882** | 14.843 | 13.045 |
| `p18-imp-7f73929d` ※ | 49 | 9 | 49685 | **6888** | 16.900 | 14.997 + 0.931 |
| `p18-fsm-comparator` | 50 | 10 | 46402 | **7230** | 15.467 | 16.151 |
| `p18-crew-c1-gen9` | 50 | 0 | 54212 | **0** | 18.071 | 15.059 |
| `p18-crew-c1-gen0` | 57 | 3 | 54775 | **3035** | 16.016 | 16.241 |
| `p18-crew-c2-gen9` | 56 | 1 | 9342 | **371** | 2.780 | 2.774 |
| `p18-crew-c2-gen0` | 50 | 0 | 27 | **0** | 0.009 | 0.008 |
| **nine-leg totals** | **464** | **30** | **348488** | **22465** | 12.5175 | — |
| stubborn rounds (both seeds), separately logged | 11 attempts | — | — | 7821 | — | 2.173 |

**Summed wall — three labelled components that sum to the campaign's full attempt
wall.** An earlier draft added the stubborn loop and the seed-35 retry passes to
the recorded-game wall and called the result the campaign total. That
under-counted: **every leg's in-leg rc99 attempts cost wall too**, and only one
leg's were being added. Each row now carries `leg_duration.retry_wall_seconds`,
so the components are stated separately and add up:

| component | wall | what it is |
|---|---|---|
| recorded-game wall | **348488 s = 96.8022 h** | the 464 rc-0 recordings — Σ `sum_wall_seconds_ok` |
| in-leg rc99 attempts | **22465 s = 6.2403 h** | the 30 purity-failed attempts inside the legs — Σ `retry_wall_seconds` |
| stubborn loop | **7821 s = 2.1725 h** | the 11 `retry-stubborn.sh` attempts, logged separately (workspace-only) |
| **full attempt wall** | **378774 s = 105.2150 h** | **505 attempts** (464 + 30 + 11) |

**The rates, each labelled by its denominator.** The **per-recorded-game** figure
is unchanged and is the one the projection is judged against: **348488 s / 464 =
12.5175 min/game serial**, **2.5% above** the pre-registered **12.2077** — the
18.25-derived rate transferred to this slate with a margin narrower than any gauge
on the board. Beside it, **attempt-inclusive**: **378774 s / 464 = 13.6054
min/recorded game**, i.e. every finished game cost **1.09 min** of failed-attempt
overhead on top of itself; **per attempt** the rate is **378774 s / 505 = 12.5008
min/attempt**, almost exactly the per-recorded-game figure — a failed attempt cost
about what a successful one did.

**One caution against double-counting.** `p18-imp-7f73929d`'s **6888 s** of
`retry_wall_seconds` **already contains** the retry leg's **2981 s**
(`post_pr_retry_leg.sum_wall_seconds`); the retry leg is a subset of that arm's
rc99 attempts, not a fourth component. The stubborn loop's 7821 s is the only
attempt wall that lives outside the per-arm blocks.

**※ — `p18-imp-7f73929d` ran a SECOND leg after the PR opened, and its row is the
only two-window entry.** Leg 1 (`leg-start 2026-07-30T08:23:42Z → leg-abort
23:23:31Z`, **14.997 h**) holds all 49 of its recorded games. The owner-directed
seed-35 retry is a second window (`leg-start 2026-07-31T17:04:16Z → leg-abort
18:00:06Z`, **0.931 h**) that produced **zero rc-0 recordings** — all 4 passes
rc 99 — so `games_recorded_ok` (49) and `sum_wall_seconds_ok` (49685) are
identical across the two windows, and the 348488 s / 464-game totals are
untouched. Two cells **do** span both windows and are quoted that way: the
**retry-events** count is **9** (5 in leg 1, 4 in the retry leg), matching the
row's `leg_duration.retry_events`, and the elapsed column shows both windows
rather than summing them across the gap between.

**Both window boundaries are now committed, so the decomposition is readable from
the row alone.** `leg_duration` carries `leg1_abort_at` and
`post_pr_retry_leg.leg_start_at` alongside the outer bounds, giving two **active**
windows and the idle stretch between them:

| segment | committed fields | duration |
|---|---|---|
| window 1 (leg 1) | `first_event_at 2026-07-30T08:23:42Z` → `leg1_abort_at 2026-07-30T23:23:31Z` | **14.997 h** |
| inter-leg gap (idle) | `leg1_abort_at` → `post_pr_retry_leg.leg_start_at 2026-07-31T17:04:16Z` | **17.679 h** |
| window 2 (retry leg) | `leg_start_at` → `last_event_at 2026-07-31T18:00:06Z` | **0.931 h** |
| **first-to-last span** | `first_event_at` → `last_event_at` | **33.607 h** |

14.997 + 17.679 + 0.931 = **33.607 h**, which closes on the outer span exactly.
The retry window also carries `attempts` 4, `sum_wall_seconds` 2981 and
`first_at 17:20:27Z` (its first recorded pass, 16 min after the leg started).
Those 2981 s are added to campaign leg wall (above) and the endpoint moves
accordingly (below); note the 17.679 h inter-leg gap is **this arm's own** idle
and is not the same quantity as the campaign-wide **1.4286 h** post-PR gap below,
which is measured from the last leg of the *slate* (`c1-gen0`, `15:38:33Z`)
rather than from this arm's leg 1.

The pooled rate is pulled **down** by the two starved c2 legs. Over the **seven
meeting-bearing** legs (the four impostor arms, the comparator, `c1-gen9`,
`c1-gen0`) the serial rate is **339119 s = 94.1997 h over 358 games ⇒ 15.7877
min/game per recorded game** — **29% slower** than the pre-registered 12.2077,
because 18.25's rate was measured on crew-vs-champion games and this slate's
meeting-rich impostor legs run longer meetings. Attempt-inclusive those same seven
legs read **339119 + 22094 = 361213 s over 358 games ⇒ 16.8162 min/game** (they
carry **22094** of the campaign's 22465 s of in-leg rc99 wall — the two starved c2
legs contribute only 371 s between them).

**The posture as it actually ran — two-leg rolling, not two-leg batched.** Legs
were launched as **staggered concurrent pairs** and a new leg started as soon as
a slot freed, never waiting for both to finish: `ea4bc955` + `fsm-comparator`
both start `2026-07-29T07:17:4xZ`; `bfd145cb` starts `20:10:03Z` while
`ea4bc955`'s purity pass still runs; `6d327dcb` at `23:27:42Z`; `c1-gen9` at
`2026-07-30T12:30:44Z` alongside `7f73929d`; `c1-gen0` at `23:24:07Z` alongside
`c1-gen9`'s tail. At most two legs are ever in flight.

**The app restart (one).** A single global pause of **~7 minutes** —
`2026-07-30T01:55:27Z → 02:02:30Z`, the only gap >5 min in the merged
all-leg busy interval — after which **both** in-flight legs (`bfd145cb`,
`6d327dcb`) relaunch under `leg-runner-v2.sh` at `02:02:30Z` / `02:02:33Z`. The
v2 runner is what added the purity re-check; the restart is why `ea4bc955`,
`bfd145cb` and `fsm-comparator` each carry a second `leg-start`.

**The three sleep interruptions.** None of them appear as idle time — the machine
slept **with a seed in flight**, so each stall is absorbed into that seed's
`wall_seconds` and shows up as an outlier against its leg's median:

| # | window | seeds in flight | logged `wall_seconds` | leg median | excess |
|---|---|---|---|---|---|
| 1 | `2026-07-30T17:36Z` | `c1-gen9` seed 18 / `7f73929d` seed 32 | 3783 / 4335 | 884 / 923 | 2899 / 3412 |
| 2 | `2026-07-30T21:50Z` | `c1-gen9` seed 34 | 2060 | 884 | 1176 |
| 3 | `2026-07-31T03:21–03:24Z` | `c1-gen0` seed 5 / `c1-gen9` seed 48 | 10208 / 10164 | 826 / 884 | 9382 / 9280 |

Interruptions 1 and 3 hit **both** concurrent legs at once, so the excess is
booked twice in leg wall: **26149 s = 7.264 h** of leg `wall_seconds` corresponds
to **13970 s = 3.881 h** of real wall-clock stall.

**The stubborn-seed history.** Three seeds refused to finish clean, in **three
different ways**. Two of them are purity failures (`rc 99`), and their
`retry-stubborn.sh` rounds are logged separately in `leg-log-stubborn.jsonl`; the
third never failed at all in the runner's eyes and is the reason the attempt
accounting below separates *exit code* from *outcome*:

- **`p18-fsm-comparator` seed 5 — pure on attempt 14.** One leg-1 recording
  (`2026-07-29T08:51:42Z`, rc 0, later found impure), then 4 in-leg attempts in
  leg 2 and 4 in leg 3 (passes 1–4 each, **all rc 99**, two `leg-abort`s), then 5
  stubborn rounds; the **14th** attempt (`2026-07-31T08:11:17Z`, 1022 s) returned
  **rc 0**. The arm scores at the full **n=50**.
- **`p18-imp-7f73929d` seed 35 — excluded, forensics kept.** **14 logged
  attempts, every one rc 99**: 4 in-leg (passes 1–4, ending in `leg-abort` at
  `2026-07-30T23:23:31Z`), 6 stubborn rounds (rounds 1–6, last at
  `2026-07-31T08:33:09Z`), and a **final owner-directed retry run** — **dispatched
  after this task's PR was already open**, as a last check on the exclusion — of 4
  more in-leg passes in a second leg (`leg-start 17:04:16Z`, passes recorded
  `17:20:27Z`, `17:31:47Z`, `17:43:26Z`, `17:58:35Z`, all rc 99, 970 + 587 + 607 +
  817 = **2981 s** summed wall, `leg-abort 2026-07-31T18:00:06Z`). The failure
  anatomy is **identical in every kept
  forensic copy**: the game's first meeting (`meeting-0`, tick 10), opening
  turn 0, agent `p-8`, defaults on **validation** ("p-8 submitted no turn").
  The pre-meeting prefix is engine-deterministic, so every attempt presents
  the model the identical opening prompt — a content-triggered pathology
  (invalid completion with observed probability 14/14), not a transient. The
  seed is **excluded** and the arm scores at **n=49** (§17). The 6 stubborn
  recordings are kept as forensics under `~/ailibi-campaign-1826/forensics/`
  — 10 forensic files in total, 4 for comparator seed 5 and 6 for seed 35
  (the in-leg passes delete impure replays rather than archiving them).
- **`p18-crew-c1-gen0` seed 20 — 8 attempts, every one `rc 0`, every one a
  stalemate.** This seed never triggered a purity retry and never reached the
  stubborn runner, because the recorder **succeeded** every time: 4 in-leg
  attempts (leg 1 passes 1–4 at `2026-07-31T06:57:04Z`, `13:38:33Z`, `14:08:50Z`,
  `14:35:15Z`) then a **bonus 4-pass v2 run** after the `leg-abort` (leg 2 passes
  1–4 at `15:04:24Z`, `15:15:06Z`, `15:26:06Z`, `15:37:31Z`), **8 attempts, all
  rc 0**, 4829 s of wall between them. Each run produced a complete 1002-row
  replay that reaches **tick 999** and simply never emits `game_over`. The arm
  scores at **49 finalized of 50 recorded** (§16.b, §17.1).
- Stuck-seed wall, reconciled against the per-arm `leg_duration` blocks. In the
  **separately-logged stubborn loop**: **3676 s** on comparator seed 5 and
  **4145 s** on seed 35 = the **7821 s** total above. **Inside the legs**, those
  two seeds' failures are rc 99 and sit in `retry_wall_seconds` — seed 35's
  in-leg attempts account for the whole of `7f73929d`'s **6888 s** (4 leg-1
  passes plus the retry leg's 2981 s), so the seed cost **4145 + 6888 = 11033 s**
  across both books. **Seed 20 is the exception and is counted elsewhere on
  purpose:** all 8 of its attempts returned **rc 0**, so its **4829 s** sits in
  `c1-gen0`'s **recorded-game** wall (54775 s) and inflates its `games_ok` to
  **57**, not in its `retry_wall_seconds` (**3035 s**, which is that leg's three
  genuine purity retries). A seed that records cleanly and never finishes costs
  recorded-game wall, not retry wall — which is exactly why the runner never saw
  it as a failure (§17.1).

**The c2 legs are fast because meetings are scarce, not because the provider was.**
`c2-gen9` runs at **2.780 min/game** (**summed seed wall** 9342 s = 2.5950 h;
**elapsed leg** `03:34:31Z → 06:20:58Z` = **2.774 h**, the figure in the table
above) and `c2-gen0` at
**0.009 min/game** — its 50 games recorded in **27 seconds total**, which is the
duration signature of a leg that makes **zero LLM calls** (§16.b, §16.e).

**The effective rate, recomputed on the complete slate — through the final
retry.** The campaign's last logged event across all nine leg logs is the seed-35
retry leg's `leg-abort`, so the measured span runs
`2026-07-29T07:17:48Z → 2026-07-31T18:00:06Z` = **58.705 h**. (To the last
*recording* at `17:58:35Z` it reads 58.680 h; the `leg-abort` is the honest
endpoint and is what every figure below uses.)

**Idle, extended alongside the span — two windows now, not one:**

| idle window | duration | what it is |
|---|---|---|
| `2026-07-30T01:55:27Z → 02:02:30Z` | **0.1175 h** | the single app restart (the only >5 min gap inside the slate itself) |
| `2026-07-31T15:38:33Z → 17:04:16Z` | **1.4286 h** | between the last slate leg's `leg-abort` (`c1-gen0`) and the retry leg's `leg-start` — nothing was recording while the PR sat open |
| **total idle** | **1.5461 h** | |

**Busy span = 58.705 − 1.5461 = 57.1589 h.** The slate recorded **449**
seed-games (8 arms × 50 seeds + `7f73929d`'s 49) and the retry added **none**, so
on the busy span the effective rate is **7.6382 min/game** at the two-leg
posture, i.e. **≈ 6.37 h per 50-seed arm** and **≈ 57.3 h** for a 450-game slate.
Read per completed arm instead: **9 arms in 57.1589 h = 6.351 h/arm** — the two
readings still agree to within a minute per arm.

**The full-span figures, so the post-PR idle neither inflates the rate nor
vanishes from it.** On the raw **58.705 h** span with idle included, the same 449
games read **7.8448 min/game**, **≈ 6.54 h per 50-seed arm**, **≈ 58.8 h** for a
450-game slate, **6.523 h/arm**. The busy figures are the throughput number, the
full-span figures are the calendar number, and the **1.4286 h** between them is
the post-PR dispatch gap and nothing else. The endpoint reported before the retry
(`15:38:33Z`, 56.346 h, 7.5295 min/game, ≈ 6.27 h/arm) was correct for the slate
as it then stood and is **superseded** here rather than deleted.

| unit | pre-registered (§14) | **measured** |
|---|---|---|
| serial rate | 12.2077 min/game | **12.5175** pooled / **15.7877** meeting-bearing legs only |
| one 50-seed arm, two-leg effective | ≈ 5 h | **≈ 6.37 h** busy-span (6.351 h/arm by completed-arm count); **≈ 6.54 h** on the full 58.705 h span |
| the 9-arm slate (≈450 games) | ≈ 46 h | **≈ 57.3 h** busy-span / **≈ 58.8 h** full span |

**The projection was honest and optimistic by about a fifth.** The serial rate
it was built on came in at **12.5175** against a predicted 12.2077 — **2.5%
off**, an unusually good call. What the projection missed was the *posture*: the
gate priced "~5 h/finalist" and the two-leg rolling posture delivered
**≈ 6.37 h**, so the slate landed at **≈ 57.3 h** against ≈46 h, **25% over** —
**≈ 58.8 h** and **28% over** if the post-PR idle is counted as calendar time.
The gap is not the provider: recording-idle **inside** the slate is **0.1175 h**,
and the campaign's other **1.4286 h** of idle is the gap before the owner-directed
seed-35 retry, not provider downtime. It is the meeting-bearing legs' **15.7877
min/game**, the three sleep stalls (3.881 h of real wall-clock), and the **36
recording attempts** spent on three stuck seeds to salvage one of them.

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

## 16. The evidence tables — RECORDED

The skeletons above are now filled from the operator run. **All nine arms are
recorded and scored** — `p18-crew-c1-gen0`, the last leg to land, closes the
crew block and with it §16.e's deciding cell. No cell in this section reads
*pending*.

Every cell below is read from a committed `~/ailibi-campaign-1826/scoring/<arm>/`
JSON (`summary.json`, `validity.json`, `core.json`, `watchability*.json`,
`split-half.json`, `instruments.json`, `stamp-proof.json`, `duration.json`,
`row.json`) or computed arithmetically from those files. The as-recorded
`replay_set_dir` paths stay verbatim in the measurement JSON per §9.2.

### 16.a The selection table (columns follow §3.a, re-based on baseline 6)

| arm | stamp==sidecar (games/games) | validity gate | referee mean/med (verdict) | imp. win | Δ vs FSM | ej. accuracy | witnessed rate | flags/meeting | backed conv. |
|---|---|---|---|---|---|---|---|---|---|
| `p18-imp-ea4bc955` | yes 50/50 (`ea4bc955…`) | **PASS** | 48.90 / 50.15 (**FAIL** — 2 gauges) | **0.52** | **+0.26** | 0.7108 (59/24 of 83) | 0.15228 (30/197) | 0.93548 | 0.36667 (floor 0.66882) |
| `p18-imp-bfd145cb` | yes 50/50 (`bfd145cb…`) | **PASS** | 47.24 / 48.00 (**FAIL** — 2 gauges) | **0.56** | **+0.30** | 0.6707 (55/27 of 82) | 0.14778 (30/203) | 0.90000 | 0.35099 (floor 0.69519) |
| `p18-imp-6d327dcb` | yes 50/50 (`6d327dcb…`) | **PASS** | 51.15 / 63.95 (**FAIL** — 2 gauges) | **0.38** | **+0.12** | 0.7333 (66/24 of 90) | 0.22280 (43/193) | 0.96914 | 0.44444 (floor 0.64559) |
| `p18-imp-7f73929d` **(n=49)** | yes 49/49 (`7f73929d…`) | **PASS** | 52.49 / 53.70 (**FAIL** — 2 gauges) | **0.42857** (21/49) | **+0.18367** (49-seed intersection) | 0.75000 (63/21 of 84) | 0.22000 (44/200) | 0.82840 | 0.38926 (floor 0.75527) |
| `p18-fsm-comparator` | `fsm-default` — 0 learned-stamp games, 0 crew-stamp games (**opponent absence proven**) | **PASS** | 54.96 / 53.55 (**PASS**) | **0.26** | — | 0.8351 (81/16 of 97) | 0.04598 (8/174) | 1.19745 | 0.55147 (floor 0.52250) |

**Every impostor arm beats the fresh comparator; every impostor arm fails the
referee on the same two supply gauges.** The comparator is the only referee-PASS
row on the board (54.96 mean, all three floors cleared), and it is also the
lowest impostor win rate (0.26). The four learned arms sit **+0.12 to +0.30**
above it on wins while each missing `flags_per_meeting` and
`testimony_backed_conversion`.

**One correction to that sentence, for 18.27's axis-1 ruling.** All four arms
miss both *referee floors* — that much is a plain floor comparison and is what
the column above reports. But `p18-imp-bfd145cb`'s **`flags_per_meeting` cell is
UNRESOLVABLE**, not FAIL, for ruling purposes: its split-half noise **0.29291
exceeds the 0.27273 ceiling** (§16.c), so **§10.3 excludes that cell from the
axis-1 ruling** entirely. `bfd145cb` therefore fails axis-1 **on
`testimony_backed_conversion` alone**, with its flags cell removed by the noise
precondition rather than counted against it. The other three arms fail on both
gauges with both cells clearing the precondition.

This is the Part I §3.a shape reproduced at
baseline 6 and at four arms instead of one: the co-adapted impostor starves the
flag supply, the starved supply lifts the population-relative conversion floor,
and the conversion misses the lifted floor. Ranking by win rate gives
`bfd145cb` (0.56) > `ea4bc955` (0.52) > `7f73929d` (0.42857) > `6d327dcb`
(0.38); ranking by referee mean **inverts** it — `6d327dcb`/`7f73929d` score
higher (51.15 / 52.49) than `ea4bc955`/`bfd145cb` (48.90 / 47.24). No arm
satisfies both, so no arm on this table clears a referee-PASS **AND**
retained-edge bar. The ruling is 18.27's.

**The Δ column, and the 49-seed intersection.** Three arms take the Δ against the
comparator's full-50 impostor win rate **0.26** (13 of 50). `p18-imp-7f73929d`
recorded **49** seeds — seed 35 is excluded (§14.1, §17) — so quoting the full-50
comparator against a 49-seed arm would compare different seed sets. **Method,
inline:** the comparator's own `watchability.json` `per_game` array carries a
per-seed `reason`, and the win side is derivable from it directly
(`IMPOSTOR_PARITY` / `IMPOSTOR_SABOTAGE` = impostor win; `CREWMATE_EJECT` /
`CREWMATE_TASKS` = crew win) — no replay-file read was needed. Seed 35's
comparator game is an `IMPOSTOR_PARITY`, so dropping it takes the comparator from
**13/50 = 0.26** to **12/49 = 0.24490** on the intersection, and
`p18-imp-7f73929d`'s Δ is **0.42857 − 0.24490 = +0.18367**. (Against the
full-50 comparator it would read +0.16857; that number is **not** used, because
it is a cross-seed-set comparison.)

**Stamp proof held on every scored arm.** Four impostor arms carry a uniform
five-field `tactical_policy` stamp on every game with `weights_sha256` equal to
the committed sidecar and **no crew stamp**; the comparator's positive obligation
(§9.3) discharges — `fsm-default` is the only tactical id in the set, with
**zero** learned-stamp games and **zero** crew-stamp games, so no silently
learned mover inverted a Δ.

### 16.b The crew diagnostic pairs (single-opponent, frozen `ea4bc955…`)

Read this table under the **gate-validity discipline**: a row whose validity gate
FAILS is a diagnostic reading, not selection evidence. **Three of the four rows
FAIL** — both `c2` rows and `c1-gen0` — and all three are marked accordingly.
`c1-gen9` is the only crew arm with a clean gate. The 18.25 hand-off named no
crew finalist and nothing here promotes one (§8.3).

| crew arm | dual stamp (crew / tactical) | validity gate | meeting_rate (≥0.60) | crew win conv. | witnessed kills / kills | flags/meeting (noise verdict) |
|---|---|---|---|---|---|---|
| `p18-crew-c1-gen9` | 50/50 `0bf179b7…` / 50/50 `ea4bc955…`, both uniform | **PASS** (0 failed checks) | **1.0** | **26/50 = 0.52** | 30/196 = 0.15306 | 0.96644 (noise 0.17592 < 0.27273 → **clears**) |
| `p18-crew-c1-gen0` | 49/49 `bd6fdd0a…` / 49/49 `ea4bc955…`, uniform **over the stamped games** — seed 20 carries no `game_over` | **FAIL** (`all_games_reach_game_over`, `cost_and_provenance_exact`) | **1.0** | 25/49 finalized (25 of 50 recorded) — **not readable as selection evidence** | 33/200 = 0.16500 (49-game view) | 0.92667 (noise 0.15068 < 0.27273 → **clears**) |
| `p18-crew-c2-gen9` | 48/48 `515fc066…` / 48/48 `ea4bc955…`, uniform **over the stamped games** — seeds 19 and 20 carry no `game_over` | **FAIL** (`all_games_reach_game_over`, `cost_and_provenance_exact`) | **0.6 — EXACTLY at the floor** | 7/48 — **not readable as selection evidence** | 45/231 = 0.19481 (48-game view) | 1.75758 (noise 1.3 > 0.27273 → **UNRESOLVABLE**) |
| `p18-crew-c2-gen0` | 50/50 `888046d0…` / 50/50 `ea4bc955…`, both uniform | **FAIL** (`meeting_rate_and_resolution`, `cost_and_provenance_exact`) | **0.0** | 1/50 — **not readable as selection evidence** | 36/251 = 0.14343 | undefined — 0 meetings (**UNRESOLVABLE**) |

**The three FAIL rows, quoted verbatim from `validity.json`.** They are recorded
here rather than dropped, per the gate-validity discipline — a starved arm is a
finding, and hiding the FAIL would be the laundering the discipline exists to
prevent.

`p18-crew-c2-gen0`:

> `meeting_rate 0.000 < floor 0.60`
>
> `no model recorded on any game cost row`
>
> `model provenance [] != expected ['Qwen/Qwen3.6-27B']`

`p18-crew-c2-gen9`:

> `seed 19: no game_over row (game never reached game_over)`
>
> `seed 20: no game_over row (game never reached game_over)`
>
> `seed 19: no substrate_flags stamp on game_over`
>
> `seed 20: no substrate_flags stamp on game_over`

`p18-crew-c1-gen0` — **both violations trace to seed 20 and nothing else**:

> `seed 20: no game_over row (game never reached game_over)`
>
> `seed 20: no substrate_flags stamp on game_over`

Its other eight checks all PASS, including `meeting_rate_and_resolution` at
**1.0** (150 resolved meetings, 0 unresolved),
`no_betrayal_ballots_or_accusations` over 862 multi-impostor ballots and
`no_railroaded_crew_ejections` over 2875 rendered crew suspicions. This is a
**one-seed** gate FAIL on an otherwise healthy leg, and §17.1 records why the
seed was kept in-row rather than retried away.

**`c2-gen9` sits EXACTLY on the meeting floor — and passes, inclusively.** Its
`meeting_rate` is **0.6** against `eval/validity.py::MEETING_RATE_FLOOR = 0.60`,
and the gate's own check is `rate >= MEETING_RATE_FLOOR`
(`eval/validity.py:593`), so the equality **passes**: 30 of 50 games hold a
meeting, 33 resolved meetings, 0 unresolved. `meeting_rate_and_resolution` is
therefore a **PASS** check on that arm — its gate FAIL comes from the two
stalemate seeds, not from meeting starvation. The row is a boundary case and is
labelled as one rather than rounded into a comfortable margin.

**The referee reads 0.0 on `c1-gen0` and `c2-gen9`, and that is the integrity
layer, not a play result.** Both arms report `mean_score` **0.0** / `median_score`
**0.0** with `integrity_ok` **false**: the scorer **zeroes** the watchability
score whenever a non-finalized game sits in the set, because a score computed
across a partial game is not a score. `c1-gen0`'s own `per_game` row for seed 20
shows the mechanism — `floor_multiplier` **0.0**, `score` **0.0** — while its 49
finalized games carry ordinary per-game scores. **These zeroes are never read as
a referee verdict**, and they are never read without the gate that explains
them; the arms' *supply gauges* (which the same JSON reports independently) are
what §16.c and §16.e use.

**What the FAIL rows still support.** `witnessed kills / kills` is read from
`instruments.json` and does not depend on the meeting economy, so the kill-craft
rider (§12, §16.e) reads those cells; `crew win conv.` is a **gate-invalid**
reading on all three FAIL rows and is excluded from every selection claim in this
Part — including the `c1-gen0` cell that §16.e's conversion comparison quotes,
which is offered as a diagnostic contrast and explicitly not as evidence for a
crew champion.

### 16.c Cell 1 — the split-half noise read (§10)

Split fixed in advance: **H1 = even seeds** (25 games), **H2 = odd seeds** (25
games). One exception, noted in-row: `p18-imp-7f73929d`'s H2 holds **24** games
because the excluded seed 35 is odd. `floor distance` and `z` are the **full-n**
reads (§10.5), carried beside the precondition so the verdict and the noise sit
side by side.

**The halves are NOT fenced.** The split-half read is computed over each arm's
**full recorded view**, including the non-finalized games — the byte-completeness
fence of §13 applies only to the **instruments** (§16.e's kill-craft cells and
the §13 emergence set), never to the watchability halves. Concretely: both arms
carrying stalemates keep **25/25** in their halves —
`p18-crew-c1-gen0` reads `games_total` **25** in `watchability-h1.json` and **25**
in `watchability-h2.json`, and `p18-crew-c2-gen9` likewise **25 / 25** — even
though their instrument views are fenced to 49 and 48 games respectively. Only
`7f73929d`'s 24-game H2 differs, and that is a *missing recording*, not a fence.

| arm | gauge | H1 (even) | H2 (odd) | measured noise | 25% of threshold | precondition | floor distance | z / clearance |
|---|---|---|---|---|---|---|---|---|
| `p18-imp-ea4bc955` | `witnessed_event_rate` | 0.12264 | 0.18681 | 0.06417 | 0.00847 | **UNRESOLVABLE** | +0.11839 | z = **+3.8757** |
| | `flags_per_meeting` | 0.84810 | 1.02632 | 0.17821 | 0.27273 | clears | −0.15543 | FAIL, starved supply |
| | `testimony_backed_conversion` | 0.32432 | 0.40789 | 0.08357 | 0.16720 | clears | −0.30215 | FAIL, floor lifted to 0.66882 |
| `p18-imp-bfd145cb` | `witnessed_event_rate` | 0.13462 | 0.16162 | 0.02700 | 0.00847 | **UNRESOLVABLE** | +0.11388 | z = **+3.7815** |
| | `flags_per_meeting` | 0.75904 | 1.05195 | 0.29291 | 0.27273 | **UNRESOLVABLE** | −0.19091 | FAIL, but noise exceeds the ceiling |
| | `testimony_backed_conversion` | 0.35714 | 0.34568 | 0.01146 | 0.17380 | clears | −0.34419 | FAIL, floor lifted to 0.69519 |
| `p18-imp-6d327dcb` | `witnessed_event_rate` | 0.19588 | 0.25000 | 0.05412 | 0.00847 | **UNRESOLVABLE** | +0.18890 | z = **+5.3548** |
| | `flags_per_meeting` | 0.88750 | 1.04878 | 0.16128 | 0.27273 | clears | −0.12177 | FAIL, starved supply |
| | `testimony_backed_conversion` | 0.41892 | 0.47143 | 0.05251 | 0.16140 | clears | −0.20115 | FAIL, floor lifted to 0.64559 |
| `p18-imp-7f73929d` (H2 = 24) | `witnessed_event_rate` | 0.17925 | 0.26596 | 0.08671 | 0.00847 | **UNRESOLVABLE** | +0.18610 | z = **+5.3170** |
| | `flags_per_meeting` | 0.82022 | 0.83750 | 0.01728 | 0.27273 | clears | −0.26251 | FAIL, starved supply |
| | `testimony_backed_conversion` | 0.39130 | 0.38750 | 0.00380 | 0.18882 | clears | −0.36601 | FAIL, floor lifted to 0.75527 |
| `p18-fsm-comparator` | `witnessed_event_rate` | 0.03448 | 0.05747 | 0.02299 | 0.00847 | **UNRESOLVABLE** | +0.01208 | z = **+0.5782** (**within noise**; the floor still gates and the arm PASSES it) |
| | `flags_per_meeting` | 1.20779 | 1.18750 | 0.02029 | 0.27273 | clears | +0.10654 | PASS |
| | `testimony_backed_conversion` | 0.53030 | 0.57143 | 0.04113 | 0.13062 | clears | +0.02897 | PASS |
| `p18-crew-c1-gen9` | `witnessed_event_rate` | 0.13000 | 0.17708 | 0.04708 | 0.00847 | **UNRESOLVABLE** | +0.11916 | z = **+3.8917** |
| | `flags_per_meeting` | 0.87671 | 1.05263 | 0.17592 | 0.27273 | clears | −0.12447 | FAIL, starved supply |
| | `testimony_backed_conversion` | 0.41667 | 0.40741 | 0.00926 | 0.16185 | clears | −0.23605 | FAIL, floor lifted to 0.64739 |
| `p18-crew-c1-gen0` | `witnessed_event_rate` | 0.15686 | 0.17347 | 0.01661 | 0.00847 | **UNRESOLVABLE** | +0.13110 | z = **+4.1715** |
| | `flags_per_meeting` | 0.84932 | 1.00000 | 0.15068 | 0.27273 | clears | −0.16424 | FAIL, starved supply |
| | `testimony_backed_conversion` | 0.41791 | 0.41026 | 0.00765 | 0.16880 | clears | −0.26139 | FAIL, floor lifted to 0.67518 |
| `p18-crew-c2-gen9` | `witnessed_event_rate` | 0.22807 | 0.16239 | 0.06568 | 0.00847 | **UNRESOLVABLE** | +0.16091 | z = **+4.8706** |
| | `flags_per_meeting` | 1.16667 | 2.46667 | 1.30000 | 0.27273 | **UNRESOLVABLE** | +0.66667 | the §10.4 prediction landing (see below) |
| | `testimony_backed_conversion` | 0.36842 | 0.35000 | 0.01842 | 0.08900 | clears | +0.00299 | inside a gate-FAIL arm |
| `p18-crew-c2-gen0` | `witnessed_event_rate` | 0.15079 | 0.13600 | 0.01479 | 0.00847 | **UNRESOLVABLE** | +0.10953 | z = **+3.7510** |
| | `flags_per_meeting` | — | — | — | 0.27273 | **UNRESOLVABLE** (no meetings) | — | undefined |
| | `testimony_backed_conversion` | — | — | — | 0.25000 | **UNRESOLVABLE** (no meetings) | — | undefined |

**The systematic finding: `witnessed_event_rate` is UNRESOLVABLE on ALL NINE
scored arms — 9 of 9, the complete slate.** Not one arm's split-half noise fits
inside the gauge's 25% ceiling of **0.00847** — the smallest witnessed-gauge
noise on the board is `c2-gen0`'s **0.01479**, still **1.75×** the ceiling, and
the largest is `7f73929d`'s **0.08671**, **10.2×** it. `c1-gen0`, the last leg
in, lands at **0.01661** (1.96×) and changes nothing. The cause is structural,
not per-arm: the
baseline-6 threshold base for this gauge is **6/177 = 0.03390**, a rare-event
point estimate, so its 25% ceiling is **0.00847** while every arm's per-half
witnessed rate moves by **0.015–0.087** between 25-game halves. **At n=50 this
gauge cannot resolve a 25%-of-a-rare-event-floor question**, and by the §10.3
pre-registration that is a **finding, not a failure**: `witnessed_event_rate`
is **excluded from 18.27's axis-1 ruling on every arm**, including the arms
where it PASSES the floor by 3–5σ. The floor still gates (a PASS is still a
PASS); what it cannot do is discriminate **between** arms at this n.

This is the §4.0 lesson generalizing: the gauge whose floor is a rare event is
the gauge whose noise ceiling is unreachable. It was pre-registered as a
possibility for the **crew** lineage's flags gauge and it landed everywhere for
the **witnessed** gauge instead.

**`flags_per_meeting` reads UNRESOLVABLE on three arms — two by measured noise
over the ceiling, one for want of meetings.** By measured noise:
`p18-imp-bfd145cb` (0.29291 vs ceiling 0.27273, a 7% overshoot) and
`p18-crew-c2-gen9` (**1.30** vs 0.27273, a 4.8× overshoot). By undefinedness:
`p18-crew-c2-gen0`, whose zero meetings leave the gauge with no halves to split
at all — marked UNRESOLVABLE in the table above, and a different kind of
unresolvable from the other two (no measurement, rather than a measurement too
noisy to use). Its `testimony_backed_conversion` cell is undefined for the same
reason. The c2-gen9
cell is **the §10.4 prediction landing**: the pre-registration named
`flags_per_meeting` "the UNRESOLVABLE-prone gauge on the meeting-scarce crew
lineage", quoting the committed n=3 `noise_to_threshold_ratio` **1.8333** for c2
against **0.3303** for c1.

**Compared like-for-like, all three arms IMPROVED.** The committed n=3 figures are
`noise / flags_floor` (floor **1.0909090909090908**), so the n=50 comparison has
to use the same denominator — the **25% ceiling (0.27273)** is a different
denominator and reading one against the other inflates the n=50 side by 4×. On
`noise / floor`:

| arm | n=3 committed | n=50 measured | direction |
|---|---|---|---|
| c2 lineage (`c2-gen9`) | **1.8333** | **1.30 / 1.09091 = 1.192** | improved 1.54× |
| c1 lineage (`c1-gen9`) | **0.3303** | **0.17592 / 1.09091 = 0.161** | improved 2.05× |
| c1 lineage (`c1-gen0`) | **0.3303** | **0.15068 / 1.09091 = 0.138** | improved 2.39× |

So the earlier "worse than predicted" reading was an artifact of mixed
denominators and **does not stand**: every arm's noise fell relative to the floor
at n=50. What **does** survive is the prediction's **direction** — the c2 lineage
remains far noisier than c1 (**7.4×** the c1-gen9 ratio at n=50, against **5.6×**
at n=3, so the split widened rather than closed) — and the **verdict**: on the
precondition's own 25% ceiling, `c2-gen9` still reads **1.30 / 0.27273 = 4.767×**
and is **UNRESOLVABLE**, while c1-gen9 (**0.645**) and c1-gen0 (**0.553**) both
clear. The prediction landed on which lineage, not on the magnitude.

`testimony_backed_conversion` **clears the precondition on every arm that has
meetings** (8 of 8), with noise between 0.00380 and 0.08357 — it is the most
stable gauge on the board and the one 18.27 can read most safely.

### 16.d Cell 2 — the F13 champions-vs-runner-ups cell (§11)

Champions `6d327dcb…` and `ea4bc955…` vs runner-ups `bfd145cb…` and
`7f73929d…`, pooled as plain two-arm means. The **margin** is
`runner-up mean − champion mean`.

**THE CELL, on a composition-clean 49-seed intersection.** `7f73929d` recorded 49
seeds (seed 35 excluded, §14.1/§17.1) while the other three recorded 50, so
pooling their as-recorded values would have averaged three 50-seed arms against
one 49-seed arm on gauges whose denominator *is* the sample. Seed 35 is therefore
removed from **all four** arms. The three full arms' intersection cells are
**persisted in their committed rows** at `f13_intersection_gauges` (with
`excluded_seed` 35 and each gauge's floor); `7f73929d`'s own row **is** the n=49
view already, so it is quoted unchanged. This is the cell:

| gauge | `6d327dcb…` | `ea4bc955…` | `bfd145cb…` | `7f73929d…` | champion mean | runner-up mean | margin | **§11.2 test — champion-side / runner-up-side noise** | per-arm noise, min–max (context only) | reads toward |
|---|---|---|---|---|---|---|---|---|---|---|
| `witnessed_event_rate` | 0.22751 | 0.15625 | 0.15075 | 0.22000 | 0.19188 | 0.18538 | **−0.00650** | **0.07001 / 0.06026** — below both | 0.03381 – 0.08671 | (18.27 rules) |
| `flags_per_meeting` | 0.95597 | 0.95364 | 0.89744 | 0.82840 | 0.95481 | 0.86292 | **−0.09189** | **0.17958 / 0.15652** — below both | 0.01728 – 0.29576 | (18.27 rules) |
| `testimony_backed_conversion` | 0.43662 | 0.37162 | 0.34932 | 0.38926 | 0.40412 | 0.36929 | **−0.03483** | **0.06578 / 0.00942** — below champion side, **3.70× above runner-up side** | 0.00380 – 0.09459 | (18.27 rules) |

All four columns are the **same 49 seeds** — **and so is the noise column**. The
three full arms' halves were re-split on the intersection (even/odd **minus seed
35**) and their `h1`/`h2`/`split_half_noise` are persisted beside the measured
values in `f13_intersection_gauges`; `7f73929d`'s own `split_half` block **is**
its 49-seed noise and is quoted from its row. Per arm:

| arm | `witnessed_event_rate` | `flags_per_meeting` | `testimony_backed_conversion` |
|---|---|---|---|
| `ea4bc955…` | 0.07503 | 0.22134 | 0.09459 |
| `bfd145cb…` | 0.03381 | **0.29576** (UNRESOLVABLE) | 0.01504 |
| `6d327dcb…` | 0.06499 | 0.13782 | 0.03696 |
| `7f73929d…` | **0.08671** | 0.01728 | 0.00380 |

**No precondition verdict moves on the intersection**: `bfd145cb`'s flags noise
reads 0.29576 against the 0.27273 ceiling (0.29291 on its full view), so it stays
**UNRESOLVABLE**; every other flags and conversion cell still clears, and
`witnessed_event_rate` stays UNRESOLVABLE on all four as in §16.c. §16.c's own
table is unchanged — those halves are the arm's **full recorded view** by
construction (§16.c), and this column is the F13 cell's matched-composition
counterpart, not a correction to it.

**The POOLED-side noises — the quantity §11.2 actually registers — and why the
per-arm column could not stand in for them.** §11.2's rule is stated on the
**pooled sides**: "A margin smaller than **either side's** split-half noise is
reported as such and cannot be read as support for A." The min–max of four
individual arms' wobbles is the noise of *those arms*, not of the two pooled
means the margin is taken between. Both pooled-side noises are derived here
**purely from committed cells** — the three full arms' `h1`/`h2` in
`f13_intersection_gauges` plus `7f73929d`'s own `split_half` `h1`/`h2`, pooled
per half exactly as the margin is pooled:

| gauge | champ H1 | champ H2 | **champion-side noise** | runner H1 | runner H2 | **runner-up-side noise** | margin H1 | margin H2 | *margin stability* | pooled margin (49 seeds) |
|---|---|---|---|---|---|---|---|---|---|---|
| `witnessed_event_rate` | 0.15926 | 0.22927 | **0.07001** | 0.15693 | 0.21719 | **0.06026** | −0.00233 | −0.01208 | *0.00975* | **−0.00650** |
| `flags_per_meeting` | 0.86780 | 1.04738 | **0.17958** | 0.78963 | 0.94615 | **0.15652** | −0.07817 | −0.10123 | *0.02306* | **−0.09189** |
| `testimony_backed_conversion` | 0.37162 | 0.43740 | **0.06578** | 0.37422 | 0.36480 | **0.00942** | +0.00260 | −0.07260 | *0.07520* | **−0.03483** |

(Champion mean = (`ea4bc955` + `6d327dcb`)/2, runner-up mean = (`bfd145cb` +
`7f73929d`)/2, per half; each side's noise is |H2 − H1| of that side's pooled
mean. The pooled margin is computed on the full 49-seed set and is **not** the
average of the two half-margins — the halves carry different denominators. The
italic ***margin stability*** column is `|margin_h1 − margin_h2|`: it measures how
steady the **margin itself** is between halves and is **an observation about
reproducibility, NOT the §11.2 test** — the §11.2 test is the two bolded
side-noise columns.)

**Applying §11.2 as registered.** The rule is **either-side sufficiency** — "A
margin smaller than **either** side's split-half noise is reported as such and
cannot be read as support for A" — so a margin that one pooled side cannot
distinguish from its own half-to-half wobble is barred, whatever the other side
does. That is the conservative reading and it is the one applied here. **All
three gauges are barred, each by the same route:**

| gauge | margin, absolute | champion-side noise | runner-up-side noise | barred by |
|---|---|---|---|---|
| `witnessed_event_rate` | 0.00650 | 0.07001 | 0.06026 | **both** sides |
| `flags_per_meeting` | 0.09189 | 0.17958 | 0.15652 | **both** sides |
| `testimony_backed_conversion` | 0.03483 | **0.06578** | 0.00942 | the **champion** side |

**So no F13 gauge can be read as supporting hypothesis A**, by §11.2's noise rule
alone. Two observations sit beside that and neither is the load-bearing route:
`testimony_backed_conversion`'s margin runs **3.70× above** the runner-up side's
**0.00942** (that pair is unusually steady between halves, 0.37422 → 0.36480), so
it is barred by one side and not the other; and its half-margins **flip sign**
(+0.00260 → −0.07260). **Corroborating note, not the argument:** all three margins
are **negative** while A predicts runner-ups sitting *higher* ("one step less far
along the trade"), so the direction points away from A independently of any noise
test.

**The margin-stability and sign reads, kept as separate observations:**

- **`witnessed_event_rate`** — margin stability **0.00975**, sign **consistent**
  across halves (−0.00233, −0.01208).
- **`flags_per_meeting`** — margin stability **0.02306**, sign **consistent**
  (−0.07817, −0.10123); the pooled margin is **4.0× larger** than that stability
  figure, i.e. the margin is steady between halves even though it sits inside
  both sides' noise. **Separately**, `bfd145cb`'s per-arm flags cell remains
  **UNRESOLVABLE** on the noise precondition (0.29576 > 0.27273), so §10.3
  excludes that arm's cell from the axis-1 ruling — all of these hold at once and
  none cancels the others.
- **`testimony_backed_conversion`** — margin stability **0.07520**, and the
  **sign does not reproduce across the halves**: **+0.00260** in H1, **−0.07260**
  in H2. In the flavour of §6.b's sign rule, a margin that flips direction
  between halves is not reproducing.

**None of this is a ruling**; it is the registered test applied to committed
cells, with the stability and sign observations recorded beside it. **The ruling
is 18.27's.**

Every margin stays **negative** — the hypothesis-B shape is unchanged by the
composition fix. The magnitudes move only in the third decimal, and **not all in
the same direction**: `witnessed_event_rate` grew a hair (0.00365 → 0.00650) and
`flags_per_meeting` grew a hair (0.08811 → 0.09189), while
`testimony_backed_conversion` **shrank** a hair (0.03543 → 0.03483).

**The per-arm values, for reference — NOT the cell.** These are each arm's own
full-n instrument values, quoted elsewhere in this Part (§16.a, §16.c). They mix a
49-seed arm with three 50-seed arms and are recorded here only so the two sets
cannot be confused:

| gauge | `6d327dcb…` | `ea4bc955…` | `bfd145cb…` | `7f73929d…` (n=49) | champion mean | runner-up mean | margin (per-arm, mixed composition) |
|---|---|---|---|---|---|---|---|
| `witnessed_event_rate` | 0.22280 | 0.15228 | 0.14778 | 0.22000 | 0.18754 | 0.18389 | *−0.00365* |
| `flags_per_meeting` | 0.96914 | 0.93548 | 0.90000 | 0.82840 | 0.95231 | 0.86420 | *−0.08811* |
| `testimony_backed_conversion` | 0.44444 | 0.36667 | 0.35099 | 0.38926 | 0.40556 | 0.37013 | *−0.03543* |

**Every margin is smaller than the largest intersection noise on its own row**,
and on **one** of three rows — `witnessed_event_rate` — smaller than *every*
contributing arm's noise. On the other two rows the margin clears some arms'
noise and not others, and the split is different on each row; the bullets state
it per side, without smoothing. Per §11.2 a margin smaller than either side's
split-half noise "is reported as such and cannot be read as support for A". Every
figure below is the **intersection** margin against the **intersection** noise —
matched composition on both terms. **These bullets read the margin against the
individual arms' wobbles, which is context — §11.2's registered test is the
pooled-side one applied above**, and the two can differ: on
`testimony_backed_conversion` the margin clears two of four per-arm noises here
*and* the runner-up side's pooled noise there, while on `flags_per_meeting` it
clears one per-arm noise but sits inside both pooled sides'. All of it is
recorded; none of it is a ruling.

- `witnessed_event_rate`: margin **0.00650** against noises of **0.03381
  (`bfd145cb`) – 0.08671 (`7f73929d`)** — smaller than **all four**, by **5.2× to
  13.3×**. This row is also UNRESOLVABLE on all four arms, so it carries **no**
  discriminating weight in either direction.
- `flags_per_meeting`: margin **0.09189**. It **exceeds one** arm's noise —
  `7f73929d`'s **0.01728** — and sits **inside the other three**: `6d327dcb`
  0.13782, `ea4bc955` 0.22134, `bfd145cb` **0.29576**, and `bfd145cb`'s cell is
  itself UNRESOLVABLE.
- `testimony_backed_conversion`: margin **0.03483**, and this row **changed
  materially with the composition fix**. It **exceeds two** arms' noise —
  `7f73929d`'s **0.00380** and **`bfd145cb`'s 0.01504** — and sits **inside the
  other two**: `6d327dcb` **0.03696** (by 0.00213, a hair) and `ea4bc955`
  **0.09459**. This is the **only** row where the precondition clears on all four
  arms, so it is also the only one where every side of that comparison is
  readable. The margin is *not* uniformly inside the noise here, and the report
  does not claim it is.

**The measured answer, stated beside the verbatim hypotheses (§11.1).** Quoting
them unchanged:

> **hypothesis A** (the ES trades evidence-supply for wins; runner-ups sit one
> step less far along the trade — predicts the runner-ups' gauge margins
> **PERSIST** at n=50)
>
> **hypothesis B** (n≤6 referee reads are noise — predicts the champion/runner-up
> gauge gap **VANISHES** at n=50)

The measured cells sit with **hypothesis-B-shaped** outcomes: all three margins
are **negative** (runner-ups score *lower*, not higher, on every gauge — the
opposite direction to A's "one step less far along the trade") and all three sit
**inside the loudest contributing arm's split-half noise**, with
`witnessed_event_rate` inside **every** arm's. On the other two rows the margin
does clear the quietest arms — one of four on flags, two of four on conversion —
so "smaller than the noise" is true of the row as a whole and **not** of every
pairwise comparison inside it; the bullets above give the exact split.

**Under §11.2's registered test the statement is cleaner than any of that.** The
rule bars a margin smaller than **either** pooled side's split-half noise, and
**all three gauges are barred** — witnessed and flags below **both** sides,
conversion below the **champion** side (0.03483 < 0.06578). **So no F13 gauge
supports hypothesis A, by the noise rule alone**; that the margins are also all
**negative**, A's opposite, is corroboration rather than the route. That is the
whole of what the cell establishes; the B-shaped reading it leaves standing is
*not* thereby confirmed, since "A unsupported" is not "B demonstrated". **The
ruling is 18.27's.** Nothing in this Part declares A or B confirmed.

**The within-lineage pair** (`run-02-utility-lambda4`: `ea4bc955…` gen-2 vs
`bfd145cb…` gen-9) — the one comparison where lineage is held constant and only
the champion/runner-up position moves, quoted as its own cell:

on the **same 49-seed intersection** as the cell above, so its noises are the
intersection noises too:

| gauge | `ea4bc955…` (gen-2, champion) | `bfd145cb…` (gen-9, runner-up) | difference (runner-up − champion) | noise `ea4bc955` | noise `bfd145cb` |
|---|---|---|---|---|---|
| `witnessed_event_rate` | 0.15625 | 0.15075 | **−0.00550** | 0.07503 | 0.03381 |
| `flags_per_meeting` | 0.95364 | 0.89744 | **−0.05620** | 0.22134 | **0.29576** (UNRESOLVABLE) |
| `testimony_backed_conversion` | 0.37162 | 0.34932 | **−0.02231** | 0.09459 | 0.01504 |
| impostor win rate *(full 50 — no intersection cell is persisted for it)* | *0.52* | ***0.56*** | ***+0.04*** | — | — |

**On the cleanest read available, all three gauge differences are inside the
noise on at least one side, and two of three are inside the noise on both.** The
lineage-mate runner-up scores marginally *lower* on every gauge and marginally
*higher* on wins — the same negative-margin direction as the pooled cell, at a
magnitude **smaller than** the instrument's own wobble: on **both** sides for
`witnessed_event_rate` (|−0.00550| inside 0.07503 and 0.03381) and
`flags_per_meeting` (|−0.05620| inside 0.22134 and 0.29576), and on **one** side
for `testimony_backed_conversion` — |−0.02231| sits inside `ea4bc955`'s **0.09459**
and **outside** `bfd145cb`'s **0.01504**, so on the quieter arm the difference
does clear the wobble. The composition fix widened that one gap (it was
|−0.01567| against 0.01146 on the full views) without changing which side of
which noise it falls on. A difference that cannot clear its own instrument's
noise on both sides is not a within-lineage result.

**What `bfd145cb`'s UNRESOLVABLE flags precondition excludes.** `bfd145cb…` is
the **only** arm in the F13 quartet whose `flags_per_meeting` fails the noise
precondition (0.29291 > 0.27273). By §10.3 that cell is excluded from 18.27's
axis-1 ruling, which means **the `flags_per_meeting` row of this cell cannot be
read as a within-lineage result at all** — the within-lineage pair is exactly
`ea4bc955` vs `bfd145cb`, so an UNRESOLVABLE on one side removes the row. What
survives the within-lineage read is `testimony_backed_conversion` (both sides
clear) and, formally, `witnessed_event_rate` — except that gauge is
UNRESOLVABLE on **every** arm (§16.c). **So the within-lineage cell rests on one
gauge: `testimony_backed_conversion`, difference −0.02231** on the
composition-clean 49-seed intersection (the full-view figure, −0.01567, is the
labelled reference table's and is not the cell). That is the honest width of the
cleanest F13 read this campaign produced, and 18.27 should read it knowing it is
one gauge wide — and that the difference **exceeds `bfd145cb`'s own intersection
noise (0.01504)** while sitting inside `ea4bc955`'s (0.09459).

### 16.e The crew lineage reading (c1 vs c2) and the routed rider

This subsection is new — the pre-registration reserved §16.a–d and the crew
lineage needs its own cell, because the two lineages did not fail in the same
way. Both are **diagnostics** (§8.3); neither promotes a crew champion.

**The c1 lineage plays the game.** `p18-crew-c1-gen9` is the only crew arm with a
**PASS** validity gate (zero failed checks), a **1.0** meeting_rate, 149 resolved
meetings, and a **50/50** dual stamp with both slots uniform. Its crew win
conversion is **26/50 = 0.52** against the frozen champion — 24 of those wins by
`CREWMATE_EJECT`, 2 by `CREWMATE_TASKS`, with 24 `IMPOSTOR_PARITY` losses. Its
referee misses the same two supply gauges as every impostor arm (mean 47.99,
flags 0.96644 below 1.09091, conversion 0.41135 below the derived 0.64739), and
its `flags_per_meeting` **clears** the noise precondition.

`p18-crew-c1-gen0`, the same-encoder (`crew-option-features-v2`) same-opponent
control, lands the same shape: **1.0** meeting_rate, 150 resolved meetings, dual
stamp uniform over its 49 stamped games, `flags_per_meeting` **clears** the
precondition, and the same two supply gauges below floor (flags 0.92667 below
1.09091, conversion 0.41379 below the derived 0.67518). Its gate FAILS on **one
seed** — seed 20 (§16.b, §17.1) — which is a different failure from anything on
the c2 side: **the c1 lineage plays the game at both generations.**

**The c2 lineage does not.** `p18-crew-c2-gen0` is **total starvation**:
`meeting_rate` **0.00**, **0** meetings of any kind, **0** ejections, **0**
ballots, `ejection_accuracy` and `genuine_class_conversion` both undefined. The
duration signature confirms the mechanism — **50 games in 27 seconds total**
(0.009 min/game), which is not a game making LLM calls; and the gate agrees in
its own words: **"no model recorded on any game cost row"** and **"model
provenance [] != expected ['Qwen/Qwen3.6-27B']"**. Empty model provenance plus a
27-second leg is **zero LLM calls**. Crew won **1** of 50 (that one by
`CREWMATE_TASKS`; the other 49 are `IMPOSTOR_PARITY`) — a gate-invalid reading,
quoted only to characterise the starvation.

`p18-crew-c2-gen9` is the **partial** version of the same pathology: meetings
exist but sit **exactly** on the 0.60 floor, and **two seeds (19, 20) never reach
`game_over` at all** — `tick_budget_reached` 2, no `game_over` row, no
`substrate_flags` stamp. These are **learned deterministic stalemates**: the two
games ran out the tick budget with neither side able to force a resolution.
Crew won **7 of the 48** finalized games. Both figures are gate-invalid and
neither is selection evidence.

**The rider — crew-witnessed kill rate vs the corpus (§12).** Corpus cell
**12/505 = 0.02376** (`baseline-cells-corpus.json`, `kill_craft` 9p2i,
baseline-6). Every scored arm's cell, read from `instruments.json`:

| arm | crew-witnessed kills / kills | rate | × corpus | rare-event z (x₀=6, n₀=177) |
|---|---|---|---|---|
| `p18-imp-ea4bc955` | 30/197 | 0.15228 | 6.41× | +3.8757 |
| `p18-imp-bfd145cb` | 30/203 | 0.14778 | 6.22× | +3.7815 |
| `p18-imp-6d327dcb` | 43/193 | 0.22280 | 9.38× | +5.3548 |
| `p18-imp-7f73929d` (n=49) | 44/200 | 0.22000 | 9.26× | +5.3170 |
| `p18-fsm-comparator` | 8/174 | 0.04598 | 1.93× | +0.5782 |
| `p18-crew-c1-gen9` | 30/196 | 0.15306 | 6.44× | +3.8917 |
| `p18-crew-c1-gen0` | 33/200 | 0.16500 | 6.94× | +4.1715 |
| `p18-crew-c2-gen9` | 45/231 | 0.19481 | 8.20× | +4.8706 |
| `p18-crew-c2-gen0` | 36/251 | 0.14343 | 6.04× | +3.7510 |

The comparator's row is its **full-50** cell. Its **49-seed** counterpart — the
same-seed pairing view for `7f73929d`, persisted at
`instruments.intersection_49_seed_for_7f73929d` — reads **8/170 = 0.04706**
(1.98× corpus), so the comparator's near-floor position is unchanged on either
seed set and the contrast with `7f73929d`'s 0.22000 is not a composition
artifact. The full-50 cell is the comparator's own row in this corpus-anchored
table and is quoted as such; it is **not** a clause-(b) pairing for every arm —
§16.g scopes which arm pairs which comparator view.

Each cell is **that arm's own** instrument value over **its own** scored view —
50 seeds where the arm has no stalemate, the fenced view where it does
(`7f73929d` 49, `c1-gen0` 49, `c2-gen9` 48). These are the right numbers for
reading one arm against the corpus, and the **wrong** numbers for reading two
arms against each other when their views differ; the deciding cell below
therefore re-computes the gen-9 side on the matched seed set rather than lifting
its row from here.

**The 18.25 elevation reproduces at n=50 — and two facts narrow what can cause it
before the deciding cell is even read.** First, it is present **against SCRIPTED
crew**: the four impostor arms play the stock FSM crew and still run
**6.2×–9.4×** corpus, while the all-scripted comparator on the same seeds runs
**1.93×** (z **+0.5782**, within noise of the floor). So the elevation cannot be
a *learned-crew* observation effect in those rows — there is no learned crew in
them. Second, it is present **in a leg with no meetings at all**: `c2-gen0` runs
**6.04×** corpus with `meeting_rate` 0.00 and zero LLM calls, so the elevation
cannot require the meeting economy or the language model either.

**THE DECIDING CELL — the c1 gen-9-vs-gen-0 pair, on a same-seed intersection.**
§12 fixed the read as gen-9 vs its **own** gen-0 control at the **same frozen
opponent** — that pairing holds the impostor constant, so any gap between them is
attributable to the crew genome's generation and nothing else.

**The sample sets must match, and they did not by default.** `c1-gen0`'s
instrument cell is its **49-game fenced view** (seed 20 is its stalemate, §17.1),
while `c1-gen9` has no stalemate and its instrument cell spans **all 50** seeds.
Comparing 30/196 against 33/200 would have compared a 50-seed arm to a 49-seed
one on a gauge whose denominator *is* the sample. So the gen-9 side is
re-computed on the **same 49-seed intersection** — seed 20 excluded from **both**
arms — through the committed instrument
(`eval.kill_craft.compute_kill_craft_report` over the staged view
`scoring/p18-crew-c1-gen9/rider-intersection-view/`, 49 replays, seed 20 absent).
Seed 20 contributed **5 kills, 0 of them witnessed** on the gen-9 side, so the
intersection cell is **30/191**:

| c1 lineage arm | view | crew-witnessed kills / kills | rate | × corpus | z |
|---|---|---|---|---|---|
| `p18-crew-c1-gen9` (gen-9 candidate) | **49-seed intersection** | 30/191 | **0.15707** | 6.61× | **+3.9738** |
| `p18-crew-c1-gen0` (gen-0 control) | **49-seed intersection** (its own fenced view) | 33/200 | **0.16500** | 6.94× | **+4.1715** |
| **margin (gen-9 − gen-0)** | | | **−0.00793** | | |
| *`p18-crew-c1-gen9`, for reference* | *full 50-seed, the arm's own instrument value quoted elsewhere in this Part* | *30/196* | *0.15306* | *6.44×* | *+3.8917* |

**Where this cell lives — the row, not the workspace.** The intersection is
**persisted in the committed evidence row**:
`training/reports/results-finalist-eval.jsonl`, entrant `p18-crew-c1-gen9`,
`instruments.kill_craft_rider_intersection`. It carries the whole cell as
recorded — `gen9_crew_witnessed_kills` **30** / `gen9_kills_total` **191**
(`gen9_rate` **0.15706806282722513**), `gen0_crew_witnessed_kills` **33** /
`gen0_kills_total` **200** (`gen0_rate` **0.165**), `margin_gen9_minus_gen0`
**−0.007931937172774878**, `excluded_seed` **20**, and `corpus_rate`
**0.023762376237623763** (the 12/505 cell) — so every figure in the table above
is readable straight out of the committed evidence file with no workspace access
and no recomputation. **That row is the evidence of record**, and it is pinned:
`tests/training/test_finalist_eval_pins.py::test_the_c1_rider_intersection_is_the_persisted_same_seed_deciding_cell`
ties the counts, both rates, the margin (derived, sign included), the excluded
seed, and the corpus cell to the row — including the gen-9/gen-0 asymmetry
(gen-9's denominator cut 196→191 by the exclusion; gen-0's 33/200 already its
own fenced parent verbatim), so a future recompute cannot cut the wrong side
without failing the suite. The operator workspace directory named above
(`~/ailibi-campaign-1826/scoring/p18-crew-c1-gen9/rider-intersection-view/`) is a
**re-derivation path** — how the cell was produced, and how a reader reproduces
it from the recordings — **not** the evidence; it is an operator working artifact
outside `replays/` (§9.2), and nothing in this section depends on its continued
existence.

The last row is the arm's own §16.b / §16.e-table instrument value and is **not**
the comparison cell — it is quoted beside so the two numbers cannot be confused.
Excluding seed 20 moves gen-9 by **+0.00401**, which is smaller than the margin
it is being compared on; the correction changes no conclusion, but the
comparison is now genuinely same-seed.

**The point estimates sit with the ARTIFACT branch — and "gen-9 ≈ gen-0" was
never given a margin, so the pair read cannot close by itself.** The measured
margin is **−0.00793**: the *untrained* gen-0 control sits marginally **higher**
than the gen-9 candidate, which is the opposite direction from a learning effect,
and both arms sit at **6.61×** and **6.94×** the 12/505 corpus cell. That is the
shape §12's artifact branch describes. **But §12 wrote the branch condition as
"gen-9 ≈ gen-0" and never operationalized "≈" as an equivalence margin**, and a
null difference is not by itself equivalence evidence. Quoting the uncertainty
instead of the point alone, the independent-binomial 95% interval on the
difference (p₁ = 30/191 = 0.15707, p₂ = 33/200 = 0.16500, SE **0.03718**) is

> **−0.00793, 95% CI [−0.0808, +0.0649]**

— an interval **±0.073 wide** that comfortably contains zero **and** contains
generation effects up to roughly ±8 percentage points in either direction, on a
gauge whose corpus anchor is 0.024. At n=49 per side this pair **cannot
distinguish "no learning effect" from "an effect this study is too small to
see"**. So: the **point estimates** sit with the artifact branch, and the
scripted-crew and LLM-free cells below are **independent supporting context** for
the same reading — but the **c1 pair read is formally INCONCLUSIVE** absent a
pre-registered equivalence margin. **Whether to adopt an equivalence criterion
post hoc, and what to rule on this cell, is 18.27's** — this section records the
measurement, the interval, and the gap in the pre-registration, and rules
nothing.

**The artifact reading is nonetheless supported from three independent
directions**, each removing a different candidate cause — context for 18.27's
ruling, not a substitute for the missing equivalence margin:

- the four **impostor** arms run 6.2×–9.4× corpus against **scripted** crew —
  removes *learned crew* as a requirement;
- **`c2-gen0`** runs 6.04× corpus with **zero meetings and zero LLM calls** —
  removes the *meeting economy* and the *language model* as requirements;
- the **c1 gen-9-vs-gen-0** pair shows **no *detectable* generation effect at the
  same frozen opponent** — the one lineage that could have carried crew training
  as the driver shows none, subject to the [−0.0808, +0.0649] interval above.

What is left is the **impostor** side and the physical layer, with the
`fsm-comparator` row as the control that isolates it: same seeds, same substrate,
same instrument, **1.93×** (z +0.5782, within noise of the floor) for the
scripted mover against **6.2×–9.4×** for every learned one. **What the routed
rider from 18.25 gets back is this: every measured cell points at learned-impostor
kill placement rather than a learned-crew observation effect — the scripted-crew
and zero-meeting cells carrying most of that weight, the c1 pair adding a
null it is underpowered to certify. The rider is answered as far as n=49 per side
allows; the ruling is 18.27's.**

**The conversion read on the same pair — same-seed, 49-seed intersection.**
`c1-gen0`'s seed 20 is the stalemate, so the honest comparison excludes it from
**both** arms; `c1-gen9`'s seed-20 game was an `IMPOSTOR_PARITY`, so dropping it
costs gen-9 no crew win:

| c1 lineage arm | crew wins / 49-seed intersection | conversion |
|---|---|---|
| `p18-crew-c1-gen9` | 26/49 | 0.53061 |
| `p18-crew-c1-gen0` | 25/49 | 0.51020 |
| **margin** | **+1 game** | **+0.02041** |

**One game — and the paired table shows why that aggregate cannot carry a
conclusion.** The seeds are shared, so the honest read is **paired**, not two
independent proportions. That table is persisted on the `p18-crew-c1-gen9` row at
`instruments.conversion_paired_49_seed`:

| | gen-0 WINS | gen-0 loses | row total |
|---|---|---|---|
| **gen-9 WINS** | 20 | **6** | 26 |
| **gen-9 loses** | **5** | 18 | 23 |
| **column total** | 25 | 24 | **49** |

**38 of the 49 seeds are concordant** — both arms win 20, both lose 18 — and the
whole aggregate margin lives in **11 discordant pairs split 6–5**. McNemar's
exact two-sided test on those discordants gives **p = 1.0** (two-sided binomial,
6 of 11 at p = ½ — the most inconclusive value the test can return). A 6–5 split
is what a coin does.

So the honest statement is a **null, not an equivalence**: no learning signal is
**detectable** on the c1 lineage at n=49, and — exactly as with the rider cell
above — **no equivalence margin was pre-registered**, so this cell cannot support
"the generations are the same" any more than it supports "the generations
differ". The aggregate +1 game / +0.02041 is not evidence in either direction.
This is **consistent with** 18.25 naming no crew finalist, and is recorded as the
n=49 paired measurement of that hand-off. **The ruling — including whether to
adopt an equivalence criterion post hoc — is 18.27's**, on the same terms as the
rider.

**The stalemate census across the crew block.** Four arms, three distinct
stuck-game mechanisms — worth tabulating because they are not the same failure:

| crew arm | stalemates | character |
|---|---|---|
| `p18-crew-c1-gen9` | 0 | clean leg, gate PASS |
| `p18-crew-c1-gen0` | 1 (seed 20) | **meeting-bearing** (2 meetings) — LLM-nondeterministic, yet **robust**: identical stalemate on all 8 attempts |
| `p18-crew-c2-gen9` | 2 (seeds 19, 20) | **LLM-free** — engine-deterministic, unretryable by construction (§17.1) |
| `p18-crew-c2-gen0` | 0 | no stalemates because impostors win fast — 49 of 50 by `IMPOSTOR_PARITY` |

The c2 pair could never have substituted for the deciding cell: `c2-gen0` at
**6.04×** with zero meetings and `c2-gen9` at **8.20×** with a gate FAIL are not
a clean generation contrast, and the c2 gen-0 arm never played a game in the
sense the rider means. It is the c1 pair — two healthy, meeting-rich legs at the
same encoder and the same opponent — that carries the ruling above.

### 16.f The emergence instruments (§13's second axis) — the full pre-registered table

§13 pre-registered a **second axis** beside the selection cells: the four
committed instrument families, computed per arm over that arm's recordings, read
beside the corpus. §16.a–§16.e quoted the handful of cells that carry the
verdicts; **this subsection records the whole registered set, per arm, with
nothing dropped and nothing invented.**

**Sources, exactly.** Every per-arm cell is read from the `instruments` block of
that arm's phase-18 row in `training/reports/results-finalist-eval.jsonl` — the
same committed row §16.a/§16.b/§16.e quote, so the overlapping cells are
identical numbers and not a re-derivation; the six cells whose sources the
flattening dropped come from that row's `instruments.registered_nested_cells`
(‡). Every baseline cell is read from
`training/artifacts/coevo/realpath/baseline-cells-corpus.json`, specifically the
**top-level `deception` / `kill_craft` / `off_menu` blocks of the
`sample_dir: replays/ml_corpus/9p2i` entry** — the baseline-6 cells, on the
registered numerator/denominator **fields** of the pre-registration's §2.2 table.
The `baseline_cells_corpus_9p2i` subkey inside those entries is **not** the source
for anything here: it is the embedded **baseline-5** snapshot, and reading it as
the baseline is the error † records. The baseline-5 memo prose is likewise not
quoted. Numerator/denominator is given wherever the row carries both terms.

Column labels are the arm suffixes of §16.a/§16.b (`c1-g9` = `p18-crew-c1-gen9`,
and so on). A bold **(49)** / **(48)** marks the crew-block **fenced view** the
arm's instruments were computed over. Rows the ratified pre-registration
(`audits/audit-phase-18-emergence-preregistration.md` §7) puts on the **advisory**
list are labelled **ADVISORY** and carry a Wilson 95% score interval `[low, high]`
beside every rate; per that memo an advisory cell **never alone rules a claim**,
and the reading at †† holds to it.

| instrument (registered cell) | corpus baseline (9p2i, baseline-6) | ea4bc955 | bfd145cb | 6d327dcb | 7f73929d **(49)** | fsm-comp | c1-g9 ✥ | c1-g0 ✥ **(49)** | c2-g9 ✥ **(48)** | c2-g0 ✥ |
|---|---|---|---|---|---|---|---|---|---|---|
| false-vouch `saw_player` rate — `false_vouch_saw_player_observations / vouch_observations_impostor` | 0.12292 (74/602) | 0.12621 (26/206) | 0.13825 (30/217) | 0.18779 (40/213) | 0.14078 (29/206) | 0.10204 (20/196) | 0.06250 (12/192) | 0.11413 (21/184) | 0.10448 (7/67) | **undef** (0/0) |
| false-vouch corroboration rate — `false_vouch_corroborations / corroboration_claims_impostor` | 0.17614 (31/176) | 0.22222 (12/54) | 0.18310 (13/71) | 0.42254 (30/71) | 0.33333 (20/60) | 0.11111 (6/54) | 0.14286 (7/49) | 0.28846 (15/52) | 0.33333 (7/21) | **undef** (0/0) |
| fabricated-vouch share — `false_vouch_fabricated / false_vouch_subject_events` — **ADVISORY** †† | 0.25397 (16/63) [0.1628, 0.3734] | 0.23810 (5/21) [0.1063, 0.4509] | 0.26087 (6/23) [0.1255, 0.4647] | 0.45455 (15/33) [0.2984, 0.6201] | 0.34783 (8/23) [0.1881, 0.5511] | 0.47368 (9/19) [0.2733, 0.6829] | 0.16667 (2/12) [0.0470, 0.4480] | 0.41176 (7/17) [0.2161, 0.6399] | 0.00000 (0/6) [0.0000, 0.3903] | **undef** (0/0) |
| frame attempt rate — `frame_attempt_meetings / meetings_total` | 0.94384 (437/463) | 0.97419 (151/155) | 0.95625 (153/160) | 0.98148 (159/162) | 0.97041 (164/169) | 0.94268 (148/157) | 0.97315 (145/149) | 0.97973 (145/148) | 1.00000 (33/33) | **undef** (0/0) |
| frame conversion rate — **ADVISORY** | 0.05263 (23/437) [0.0353, 0.0777] | 0.06623 (10/151) [0.0364, 0.1176] | 0.08497 (13/153) [0.0503, 0.1399] | 0.08805 (14/159) [0.0532, 0.1424] | 0.07317 (12/164) [0.0423, 0.1235] | 0.04054 (6/148) [0.0187, 0.0856] | 0.11034 (16/145) [0.0691, 0.1717] | 0.05517 (8/145) [0.0282, 0.1051] | 0.12121 (4/33) [0.0482, 0.2733] | **undef** (0/0) |
| teammate accusation rate — **ADVISORY** | 0.00000 (0/549) [0.0000, 0.0069] | 0.00000 (0/214) [0.0000, 0.0176] | 0.00000 (0/217) [0.0000, 0.0174] | 0.00000 (0/225) [0.0000, 0.0168] | 0.00000 (0/223) [0.0000, 0.0169] | 0.00000 (0/190) [0.0000, 0.0198] | 0.00000 (0/197) [0.0000, 0.0191] | 0.00000 (0/196) [0.0000, 0.0192] | 0.00000 (0/55) [0.0000, 0.0653] | **undef** (0/0) |
| alibi survival rate — **ADVISORY** | 0.76623 (59/77) [0.6605, 0.8467] | 0.78788 (26/33) [0.6225, 0.8932] | 0.87879 (29/33) [0.7267, 0.9518] | 0.75862 (22/29) [0.5789, 0.8778] | 0.86667 (26/30) [0.7032, 0.9469] | 0.76667 (23/30) [0.5907, 0.8821] | 0.84375 (27/32) [0.6825, 0.9314] | 0.83333 (25/30) [0.6644, 0.9266] | 1.00000 (3/3) [0.4385, 1.0000] | **undef** (0/0) |
| deflection efficacy — `effective_deflections / active_survivals` | 0.45395 (69/152) ‖ | 0.44211 (42/95) | 0.39583 (38/96) | 0.36842 (28/76) | 0.42222 (38/90) | 0.38983 (23/59) | 0.44706 (38/85) | 0.39744 (31/78) | 0.54167 (13/24) | **undef** (0/0) |
| crew-witnessed kill rate — `crew_witnessed_kills / kills_total` | 0.02376 (12/505) † | 0.15228 (30/197) | 0.14778 (30/203) | 0.22280 (43/193) | 0.22000 (44/200) | 0.04598 (8/174) | 0.15306 (30/196) | 0.16500 (33/200) | 0.19481 (45/231) | 0.14343 (36/251) |
| witnessed point-biserial, within one hop | 0.25852 | 0.21108 | 0.20847 | 0.52142 | 0.35293 | 0.27505 | 0.23395 | 0.20536 | 0.28347 | 0.26509 |
| **co-present departure (the REGISTERED cell)** — `co_present_ge1_kills / kills_total` | 0.00000 (0/505) ◆ | 0.10152 (20/197) | 0.10345 (21/203) | 0.18653 (36/193) | 0.17500 (35/200) | **0.00000 (0/174)** | 0.10714 (21/196) | 0.12500 (25/200) | 0.10823 (25/231) | 0.07570 (19/251) |
| witnessed point-biserial, co-present — **explicitly NOT registered** (§8 rejected it: `null` on all 863 committed kills, zero variance) | — (corpus sample: `null`) | 0.73122 | 0.77013 | 0.76781 | 0.77291 | **n/a** | 0.71486 | 0.83352 | 0.67307 | 0.65639 |
| co-present conditional means, witnessed / unwitnessed — **presentation statistic, NOT the registered cell** | — (corpus sample: 0.0 / 0.0) | 0.66667 / 0.00599 | 0.66667 / 0.00578 | 0.88372 / 0.02000 | 0.84091 / 0.01282 | 0.00000 / 0.00000 | 0.73333 / 0.00602 | 0.78788 / 0.00000 | 0.53333 / 0.00538 | 0.50000 / 0.00465 |
| action entropy — crew mean conditional — **NOT-DEMONSTRATED as recorded** ✧ | 0.86932 | 0.74780 | 0.74920 | 0.77148 | 0.78597 | 0.88099 | 0.74776 | 0.75497 | 0.67974 | 0.66697 |
| action entropy — impostor mean conditional — **NOT-DEMONSTRATED as recorded** ✧ | 0.65258 | 0.60780 | 0.61543 | 0.53579 | 0.50194 | 0.66839 | 0.58359 | 0.60059 | 0.62184 | 0.64172 |
| off-menu rate — `off_menu_total / impostor_decisions` | 0.00000 (0/6663) | 0.00000 (0/2015) | 0.00000 (0/2083) | 0.00000 (0/2100) | 0.00000 (0/2176) | 0.00000 (0/2299) | 0.00000 (0/2027) | 0.00000 (0/1962) | 0.00000 (0/2520) | 0.00000 (0/2596) |
| roll-call coverage mean (all) ✦ | **no corpus cell** — standing-gauge floor **0.60** | 0.84320 | 0.84192 | 0.83549 | 0.84498 | 0.85872 | 0.83846 | 0.84485 | 0.86353 | **n/a** |
| roll-call coverage mean — crew ✦ | **no corpus cell** | 1.00000 | 0.98885 | 0.99383 | 0.99556 | 0.99735 | 0.99060 | 1.00000 | 1.00000 | **n/a** |
| roll-call coverage mean — impostor ✦ | **no corpus cell** | 0.40968 | 0.45625 | 0.41049 | 0.42899 | 0.43949 | 0.42953 | 0.43919 | 0.57576 | **n/a** |
| roll-call answer rate — `roll_call_answered_total / roll_call_asked_total` ✦ | **no corpus cell** | 0.85222 (767/900) | 0.85307 (778/912) | 0.84842 (806/950) | 0.85331 (826/968) | 0.86746 (805/928) | 0.85129 (727/854) | 0.85748 (728/849) | 0.86170 (162/188) | **undef** (0/0) |

**‡ — nothing registered is missing any more. Here is the accounting.** The
`instruments` block committed on each row is a **flattened** view of the four
instrument reports: it keeps every scalar and counter key and **drops every
nested/dict-valued sub-object**. Differencing one impostor row
(`p18-imp-ea4bc955`) against the corpus JSON's blocks gives **seven** dropped
nested keys — `deception.{frame_conversions, teammate_accusations,
alibi_fabrication, effective_deflection}` and `kill_craft.{entropy_by_side,
co_present_histogram, one_hop_histogram}`; `off_menu` loses nothing. **Six
registered rulings lived in those keys, and all six are now persisted** on every
phase-18 row at `instruments.registered_nested_cells` — `frame_conversions`
(n/d), `teammate_accusations` (n/d), `alibi_survival`
(`survived`/`total_impostor_alibis`), `effective_deflection`
(`effective_deflections`/`active_survivals`) and `action_entropy` per side
(`mean_conditional_entropy` with its `agents`/`decisions`). The co-present
departure numerator is persisted separately at
`instruments.kill_craft_co_present_departure`. **Every one of those rows above is
read from the committed cells, not recomputed here.**

**What remains recompute-only is two DISTRIBUTIONS, and no registered ruling.**
`kill_craft.co_present_histogram` and `kill_craft.one_hop_histogram` are still
absent from the rows as full histograms. Neither is a claim cell: the
pre-registration registers the co-present **rate** derived from the first
(persisted) and the within-one-hop **point-biserial** (a scalar, already on every
row). The histograms would only be needed to re-plot the distributions, and are
recoverable by re-running `eval.kill_craft.compute_kill_craft_report` over each
arm's recordings.

**So the table above now carries the complete registered set.** The
pre-registration enumerates **13 claim cells, 14 rulings** (`action-entropy`
ruled once per side); all 13 appear above, per arm, on the registered
numerator/denominator fields of its own §2.2 table — including the
grounded/fabricated vouch split, whose counters were always plain scalars. The
only rows here that are **not** part of that set are the three explicitly
labelled as such: the co-present point-biserial (§8 rejected it), the co-present
conditional means (presentation statistic), and the roll-call block (✦).

**✧ — the two action-entropy rulings read NOT-DEMONSTRATED as recorded, by the
pre-registration's own instruction.** The registered entropy cell is a **mean**
tested with Welch, and Welch needs the per-agent variance. The memo's §6.a names
the gap and disposes of it in advance, verbatim:

> the unit is the per-agent conditional entropy, which the module computes
> deterministically but does NOT emit — `ActionEntropyCells` carries `agents` /
> `decisions` / the two means / pooled `buckets` only, **so s² is not recoverable
> from committed outputs today**. This is a **named instrument gap routed back as
> a contract** … a follow-up adds the per-agent entropy vector (or its N−1
> variance) to `ActionEntropyCells` with re-pins, **landing BEFORE the campaigns
> record** (the §1 substrate discipline). … **Until that field is committed and
> pinned, an entropy claim is unjudgeable from committed outputs and reads
> NOT-DEMONSTRATED as recorded** — an improvised out-of-report recomputation
> never substitutes.

**That follow-up did not land before this campaign recorded**, so the condition
the memo set is unmet and both entropy rulings (crew and impostor — 2 of the 14)
read **NOT-DEMONSTRATED as recorded**. This report therefore **does not** compute
a variance, a Welch t, or any entropy delta: the memo forbids exactly that
substitution, and doing it here would manufacture judgeability the committed
outputs do not have. The means, `agents` and `decisions` persisted at
`instruments.registered_nested_cells.action_entropy` stay in the table as
**context** — they are what a future re-pin would be read against — and nothing
in §16 or §17 rests on them.

**‖ — the deflection baseline is quoted on the REGISTERED denominator.** The
pre-registration's §2.2 cell is `effective_deflection.effective_deflections /
effective_deflection.active_survivals` — *active* survivals, never the raw
accused-impostor events, because "skip-saved survival is never deflection" (§3.5).
On the baseline-6 top-level 9p2i block that is **69/152 = 0.45395**, and every
arm column uses the same two fields from its own row. (Quoting
`effective_deflections / accused_impostor_events` would give 69/416 and compare
an arm against a corpus figure computed on a different denominator; the
pre-registered denominator is a **field**, and it re-anchors with the cells.)

**◆ — the co-present baseline is the 9p2i sample block's histogram, and only
that one.** `baseline_cells_corpus_9p2i` registers no co-present cell, and §8 of
the pre-registration says why it registers none for the *correlation* form:
"**Rejected — registering the co-present point-biserial as a baseline:** the cell
is None on all 863 committed kills (zero variance — §4.1) … **The departure is
registered as a rate cell instead.**" The rate's corpus anchor is therefore the
9p2i sample block's `kill_craft.co_present_histogram` = `{"0": 505}` ⇒
**0 of 505 kills = 0.00000**. The **4p1i** block in the same file carries its own
`{"0": 55}` (0/55) and is **not** the 9p2i anchor; neither is the sample block's
`mean_co_present_*` pair, which is a conditional-mean *presentation* statistic and
is labelled as such in its own row.

**†† — the fabricated-vouch share, and why its baseline did not move.** This cell
was already read from the **top-level** 9p2i `deception` block, so the † correction
leaves it unchanged at **16/63 = 0.25397** — fabricated **16** + grounded **47** =
**63** subject events, the split partitioning **subject events** rather than the
observation-level numerator, per the 18.1–18.3 batch finding. The **7/28 =
0.25000** figure in the phase-18 contract prose and in the pre-registration's
§3.1 table is the **baseline-5** corpus — the same snapshot the embedded
`baseline_cells_corpus_9p2i` key preserves — and per §1's mechanical re-anchor
rule it is superseded by 16/63, not quoted beside it. (Its complement, the
grounded share, likewise re-anchors from 21/28 to **47/63 = 0.74603**.)

**Read as the ratified pre-registration requires — advisory, with the interval,
ruling nothing.** `audits/audit-phase-18-emergence-preregistration.md` registers
this cell **advisory** (§3.1 by the 18.1 numerator rule, numerator 7 ≤ 7, and by
the one cross-set disagreement in its §5; §7 carries it on the advisory list):
an advisory cell is "quoted with its Wilson interval, never alone ruling a
claim", and what the flag bars is **baseline-anchored** reading and short-circuit
readings of the fragile point rate. **That advisory flag — not any arithmetic
below — is why this cell cannot rule.** The intervals are quoted beside every
rate because the memo requires it, and the arm intervals run 0.32–0.42 wide on
denominators of 6 to 33, which is the honest measure of how little a single
point rate here is worth.

**A correction to how an earlier draft read those intervals.** It inferred from
"every arm's interval overlaps the baseline's [0.1628, 0.3734]" that **no arm
separates from the corpus**. That inference is **invalid**: overlapping marginal
confidence intervals are not a difference test, and two overlapping intervals can
still sit on a significant difference. Run the actual test the pre-registration
names for rates — the pooled two-proportion z — and `6d327dcb`'s cell is right
at the bar: **15/33 vs 16/63, pooled p̂ = 0.32292, SE = 0.10048, z = +1.9962**
(two-sided p = **0.0459**), i.e. **just past |z| ≥ 1.96**. The overlap-based
"no separation" claim is therefore withdrawn.

**What that z does and does not license.** It is a **baseline-anchored** read on
an **advisory** cell, which is precisely the reading §7's advisory rule bars from
ruling — and it is one cell of a conjunctive four-part §6 discipline
(pooled z **against the same-seed scripted comparator**, sign reproduction on the
`seed mod 5` splits, a named ablation, and selected-for presence), not a claim on
its own. So it is recorded **as an observation beside the interval**, together
with the neighbouring observation that the two highest point rates (`6d327dcb`
0.45455, `c1-g0` 0.41176) are topped by the **scripted** comparator at 0.47368.
**The ruling is 18.27's**, and by the pre-registration's own rule it must come
from the arm-vs-arm §6 discipline, never from this baseline anchor.

**The same treatment applies to every other advisory-registered cell in this
table, and is now applied.** `frame conversion` (baseline 23/437),
`teammate accusation` (0/549) and `alibi survival` (59/77) are all on the
pre-registration's §7 advisory list; each is marked **ADVISORY** in the table
above and now carries a Wilson interval on **every arm cell as well as the
baseline**, since all three are filled from `registered_nested_cells`. An
advisory baseline anchors no ruling on any of them, on the same terms as ††.
The **grounded-vouch share** is registered
advisory as well; it is the exact complement of the fabricated share on the same
denominator (corpus 47/63 = **0.74603**, [0.6266, 0.8372]) and per §7 is "not a
separate registration", so it gets no separate row. Every interval in this
section is computed by the production helper the pre-registration names,
`eval.deception_instruments._wilson_interval`, which reproduces the memo's own
pinned intervals exactly (7/28 → [0.1268, 0.4336]; 0/455 → [0.0, 0.00837]).

**† — WHICH block in that file is the baseline, corrected.** The file holds two
kinds of block and an earlier draft of this section read them the wrong way
round. The key **named** `baseline_cells_corpus_9p2i` is **byte-identical in both
list entries — including the 4p1i entry**, which is the tell: a per-sample cell
set cannot be identical across a 4-player and a 9-player corpus. It is an
**embedded legacy snapshot, the baseline-5 pins** (its 34/149, 13/46 and 21+7=28
are exactly the 18.1 corpus figures the pre-registration quotes in its §3.1).
**The baseline-6 cells are the TOP-LEVEL `deception` / `kill_craft` / `off_menu`
blocks of the `sample_dir: replays/ml_corpus/9p2i` entry**, and the whole baseline
column above is now read from those and nothing else — saw_player **74/602**,
corroboration **31/176**, frame attempts **437/463**, matching
`training/reports/report-impostor-campaign.md` §5's corpus column verbatim
(`437/463 = 0.9438`, `74/602 = 0.1229`, `31/176 = 0.1761`, `23/437`).

This is the pre-registration's own mechanism, not a deviation from it: its §1
standing rule says "the quoted baseline CELLS re-anchor mechanically at any
adopting record" and that "every quoted cell VALUE" re-anchors **without
re-ratification**. Quoting the baseline-6 re-anchor is therefore the compliant
read; quoting the embedded baseline-5 snapshot was the error.

**Nothing in §12 or §16.e moves.** The witnessed-kill cell those sections use —
**12/505 = 0.02376** — was always the top-level, baseline-6 cell, so the rider's
**6.2×–9.4×** multiples, the comparator's **1.93×**, and the c1 gen-9-minus-gen-0
margin all stand exactly as recorded. The correction lands on the *other* rows of
this table, and §16.f's readings below are rewritten against the corrected column.

**The same-seed comparator view for the `7f73929d` column.** `7f73929d`'s cells
are its 49-seed view while the comparator column is the full 50, so reading the
two against each other directly compares different seed sets — the same hazard
§16.a's Δ column and §16.e's deciding cell each had to correct for. **The
comparator's own instrument cells recomputed on that 49-seed view are persisted**
on its committed row at `instruments.intersection_49_seed_for_7f73929d`
(`excluded_seed` 35), and are the right comparator reference for any axis-2 read
against `7f73929d`:

| cell | comparator, full 50 | **comparator, 49-seed (vs `7f73929d`)** | `7f73929d` (49) |
|---|---|---|---|
| crew-witnessed kill rate | 0.04598 (8/174) | **0.04706 (8/170)** | 0.22000 (44/200) |
| co-present departure | 0.00000 (0/174) | **0.00000 (0/170)** | 0.17500 (35/200) |
| frame attempt rate | 0.94268 (148/157) | **0.94805 (146/154)** | 0.97041 (164/169) |
| `saw_player` rate | 0.10204 (20/196) | **0.09794 (19/194)** | 0.14078 (29/206) |
| corroboration rate | 0.11111 (6/54) | **0.11321 (6/53)** | 0.33333 (20/60) |
| fabricated-vouch share | 0.47368 (9/19) | **0.44444 (8/18)** | 0.34783 (8/23) |
| frame conversion rate | 0.04054 (6/148) | **0.03425 (5/146)** | 0.07317 (12/164) |
| teammate accusation rate | 0.00000 (0/190) | **0.00000 (0/187)** | 0.00000 (0/223) |
| alibi survival rate | 0.76667 (23/30) | **0.76667 (23/30)** | 0.86667 (26/30) |
| deflection efficacy | 0.38983 (23/59) | **0.38596 (22/57)** | 0.42222 (38/90) |
| off-menu rate | 0.00000 (0/2299) | **0.00000 (0/2219)** | 0.00000 (0/2176) |
| one-hop point-biserial | 0.27505 | **0.28164** | 0.35293 |
| action entropy, crew / impostor | 0.88099 / 0.66839 | **0.87723 / 0.66472** | 0.78597 / 0.50194 |

Every cell moves in the third decimal or not at all, so **no reading in this
section changes** — which is itself the useful result: the `7f73929d` column can
be read against the comparator column above without a composition correction.
**The full-50 comparator cells stay the reference for the other three impostor
arms** — `ea4bc955`, `bfd145cb`, `6d327dcb` — which are the arms that actually
share its 50-seed set. The crew columns do not: `c1-g0` (49) and `c2-g9` (48) are
fenced differently again, and in any case no comparator here is a valid
opponent-matched reference for a crew arm (§2.1, ✥).

**The fenced views, and the one column that is not a fence.** `7f73929d` is a
49-game arm because seed 35 was never recorded (§14.1, §17); `c1-g0` (49, seed 20)
and `c2-g9` (48, seeds 19–20) were computed through the staged
`scoring/<arm>/instruments-view/` fences of §16.b. **`c2-g0` is a full 50-game
view** — its **undef**/**n/a** cells are not a fence but the zero-meeting
starvation of §16.e: 0 meetings ⇒ 0 vouch observations, 0 frame attempts, 0
roll calls, so every meeting-derived denominator is genuinely zero. Its
kill-craft and off-menu cells **are** real (they need no meeting), which is
precisely what lets §16.e quote its 6.04× witnessed rate as evidence that the
elevation needs neither the meeting economy nor the language model.

**The two Part I rows carry no instruments at all.** `utility-es` and
`policy-es` (§3.a) are **prior-record** baseline-5 entries recorded before this
axis existed; their rows have **no `instruments` block**, so no cell in this
table is quoted for them and none is back-filled.

**What the table says, in one pass.** (i) **Off-menu is 0/N on every arm** —
vacuous by construction for menu-bounded movers, exactly as the instrument's own
`scope_note` warns; it discriminates nothing here and is recorded to show the
denominator was real (1962–2596 impostor decisions per arm). (ii) **Frame-attempt
rate is AT corpus, not above it** — the baseline-6 anchor is **0.94384
(437/463)** and the arms span **0.94268–1.00000**, with the all-scripted
comparator (0.94268) sitting marginally *below* the corpus and every other arm
within six points above. Near-universal framing is a property of this substrate
and roster. (The earlier "far above corpus" reading was an artifact of the
baseline-5 snapshot's 0.76710 — see †.) **One arm does cross the corpus-anchored
threshold and should not be rounded away:** `6d327dcb` at **159/162** against the
corpus **437/463** gives pooled p̂ = 0.95360, SE = 0.019201, **z = +1.9601**
(two-sided p = **0.0500**) — **just past |z| ≥ 1.96**. Recorded on the same terms
as the fabricated cell at ††: this is a **corpus-anchored** observation at a
threshold, and the **claim** comparator for clause (a) is the **same-seed FSM
arm**, not the corpus (§2.1) — against `fsm-comp`'s 148/157 the same arm's margin
is far smaller. **It is not an emergence ruling; 18.27 rules.** (iii)
**Both false-vouch channels straddle their corrected baselines, and the split is
by side, not by cell.** On `saw_player` (baseline **0.12292**) the **four impostor
arms all sit above** — `ea4bc955` 0.12621, `bfd145cb` 0.13825, `6d327dcb`
0.18779, `7f73929d` 0.14078 — and the **comparator and all three meeting-bearing
crew arms sit below**: `fsm-comp` 0.10204, `c1-g9` 0.06250, `c1-g0` 0.11413,
`c2-g9` 0.10448. On corroboration (baseline **0.17614**) **six of the eight** run
above — `6d327dcb` **0.42254**, `7f73929d` **0.33333** (a validity-PASS
finalist), `c2-g9` **0.33333**, `c1-g0` **0.28846**, `ea4bc955` **0.22222**,
`bfd145cb` **0.18310** — with only `c1-g9` (0.14286) and `fsm-comp` (0.11111)
below. Two earlier readings of this row were wrong (first "at or below corpus on
every arm but one", then a four-arm count against the stale 0.28261); the
corrected picture is a **majority of arms above corpus on corroboration** and, on
`saw_player`, a clean partition that is **descriptive, not causal**: the arms
above the baseline are the four recorded as **impostor candidate vs scripted
crew**, and the arms below it are the comparator plus the three meeting-bearing
arms recorded as **learned crew vs the frozen champion**. It is tempting to read
that as learned-impostor-vs-everything-else, and **an earlier draft did — wrongly**.
The crew arms face `ea4bc955…`, a **learned** impostor, and still sit below the
baseline, so "learned impostor present" cannot be what separates the two groups.
What the partition actually tracks is the **game context** — which side is the
candidate, and therefore which opponent, roster and meeting economy each leg ran
— so an **opponent/context confound** is in play and no causal reading is
available from this cell. Which way either
reads is **18.27's ruling**, not this section's. The fabricated share is **advisory** and is read separately at ††,
where its per-arm intervals and a pooled-z observation are recorded and the
**advisory flag** — not any arithmetic — is the reason nothing here rules on it. (iv) **Roll-call coverage clears its
0.60 floor on every arm that held meetings** (0.8355–0.8635), with the same
crew/impostor split everywhere (~0.99 crew vs 0.41–0.58 impostor): impostors
under-place themselves uniformly, learned or scripted — read as context, per ✦.
(v) **The one large, uniform departure is the kill-craft pair** — the witnessed
rate (§16.e's rider) and, beside it, the **registered co-present departure rate**:
every **learned** arm kills with at least one crewmate co-present on
**0.07570–0.18653** of its kills, while the **scripted comparator is 0 of 174**
and the 9p2i corpus **0 of 505**. The pre-registration anticipated exactly this,
having noted that the committed FSM kills only when alone (co-present 0 on all
863 pinned kills) and that **any nonzero co-present count in a learned mover's
recordings is itself a behavioural departure** — which is why §8 registered the
**rate** and rejected the point-biserial. That is the same
learned-mover-versus-scripted-mover split the rider reading turns on, showing up
on a second, independent kill-craft cell — consistent with §16.e's reading that
what is left is the impostor side and the physical layer. It is **an observation
on a pre-registered instrument**, offered without a §6 four-part claim behind it,
and nothing in §17 rests on it.

**✥ — every CREW column's axis-2 cell reads NOT-DEMONSTRABLE as recorded, for
want of a comparator.** The four crew columns (`c1-g9`, `c1-g0`, `c2-g9`,
`c2-g0`) carry real, correctly computed instrument values — and **none of them
can be ruled on under axis 2**, because the pre-registration's §2.1 requires an
opponent-matched comparator that this slate does not contain:

> **Crew claims are judged opponent-matched:** a crew claim cell's candidate arm
> is (crew finalist vs opponent O) and its comparator is (**scripted-FSM crew vs
> the same O**, same seeds, same substrate) — 18.26 records a scripted-crew
> comparator row for EACH opponent a crew finalist is recorded against … **or the
> crew claim on that opponent pairing reads NOT-DEMONSTRATED for want of a
> comparator.**

Every crew arm here was recorded against the frozen impostor champion
`ea4bc955…` (§8.3), so the required comparator is **scripted-FSM crew vs
`ea4bc955…` on the same 50 seeds**. The ratified slate has no such arm:
`p18-fsm-comparator` is scripted crew **and** scripted impostor, which is a
different pairing. The condition §2.1 names is therefore unmet on all four crew
columns, and the shortfall is a **missing recording**, not a defect in the cells.

**Owner decision (2026-07-31, ratified in-session): label, do not record.** The
crew block was ratified as **diagnostic** from the outset — 18.25 named no crew
finalist and §8.3 states nothing here promotes one — so the missing comparator
costs this task no claim it was going to make. Recording a scripted-crew-vs-
`ea4bc955…` arm is a **routed follow-up**, to be taken up only if 18.27 wants
crew-side axis-2 claims; it is not a gap this report closes retroactively. The
crew cells **stay in the table as context**, which is the purpose §8.3 gave them:
they characterise how each crew lineage played, they carry §16.b's and §16.e's
diagnostics, and they are read as measurements rather than as claims. See §17.1.

**✦ — the roll-call rows are CONTEXT, not axis-2 cells.** The ratified
pre-registration fixes the emergence set at **eight instruments** (§8: Tier A
`false-vouch`, `frame`, `teammate-immunity`, `alibi-survival`, `deflection`;
Tier B `kill-craft`, `off-menu`, `action-entropy`) and states in §2.5 that
"**roll-call coverage and conversion are standing eval gauges, not
pre-registered emergence instruments**"; its §9 amendment log is **empty**, so
nothing has been added. The roll-call cells are therefore carried here as
**contextual diagnostics outside the ratified axis-2 set** — quoted because they
characterise the meeting economy each arm produced, and **excluded from anything
18.27 rules on under axis 2**. §13 of this report listed the funnel entry point
among the instrument entry points; that listing is left standing as written and
is corrected by this label and the §17.1 bullet, **not** by editing the
pre-registration (which would be an amendment, and amendments were due before the
campaigns recorded).

### 16.g The `seed mod 5` split views (§6.b evidence, committed per row)

Clause (b) of the §6 claim discipline needs each cell **recomputed on the three
`seed mod 5` partitions**, so that a pooled delta can be checked for
**sign reproduction in ≥ 2 of 3** splits. That evidence is **committed on every
phase-18 row** at `instruments.seed_mod5_splits`, partitioned `{0,1,2}` /
`{3}` / `{4}` over each arm's **own recorded seed list with its fenced exclusions
already applied**, and carrying **the complete registered claim surface per
split**: the **11 rate cells as n/d**, the one-hop point-biserial as `r` with its
`kills_total`, **and the per-side action-entropy means with their `agents` and
`decisions`** — the pre-registration's **13 claim cells / 14 rulings** in full,
on every one of the nine arms and on the comparator's nested 49-seed block too.
Nothing in this subsection is recomputed here.

**What the entropy splits do and do not change.** Their arrival means the **mean
cells' clause-(b) inputs are now committed** — a per-side entropy delta can be
read on each of the three partitions from the rows alone, with no recomputation.
It does **not** make the entropy rulings judgeable. Clause (a) needs a Welch test
and Welch needs the per-agent variance, which §6.a says is "not recoverable from
committed outputs today"; the field that would fix it never landed. §6 is
**conjunctive**, so a missing clause (a) kills the ruling regardless of how clean
clause (b) is. **Both entropy rulings therefore stay NOT-DEMONSTRATED as
recorded** (✧ in §16.f), and the per-split entropy means are **context** — what a
future re-pin would be read against — not evidence toward a claim.

**Partition sizes, as committed** — 30/10/10 where the arm recorded a clean 50,
carved where an exclusion lands: `7f73929d` **29**/10/10 (seed 35), `c1-g0`
**29**/10/10 (seed 20), `c2-g9` **29**/10/**9** (seeds 19 and 20). Every other
arm is 30/10/10.

**`7f73929d`'s clause-(b) pairing views are committed too, on the comparator's
row.** Clause (b) is a **per-split delta against the same-seed comparator**, so a
49-seed arm needs 49-seed comparator splits or the deltas compare different seed
sets in each partition. The comparator's own `seed mod 5` views on the shared 49
seeds are persisted at
`instruments.intersection_49_seed_for_7f73929d.seed_mod5_splits` — **29/10/10**,
seed 35 removed from the `{0,1,2}` partition, which is the only one it lands in.
**Which arm pairs which comparator splits, exactly.** The comparator's **full-50**
splits pair the **three full impostor arms** — `ea4bc955`, `bfd145cb`,
`6d327dcb` — and those three only, since they alone share its 50-seed set.
**`7f73929d` pairs the committed 49-seed splits** above. The **four crew arms
pair neither**: `c1-g0` and `c2-g9` read their own fenced views (49 and 48), so
their splits are carved differently again — but the decisive point is upstream of
composition. Per §2.1 a crew claim's comparator must be **scripted-FSM crew
against the same opponent**, and no such row exists in this slate (✥ in §16.f);
`p18-fsm-comparator` is scripted on both sides, a different pairing. **All four
crew arms therefore have no valid clause-(b) comparator at all**, and their
axis-2 cells already read NOT-DEMONSTRABLE for that reason. Their per-split cells
are committed and quoted as diagnostics, never as pairings. Both comparator rows
appear below.

**Illustration — the two kill-craft rate cells, five arms.** The full 12-cell ×
3-split set is in the rows; this table exists so a reader can see the shape of
the committed evidence without opening the JSON:

| arm | crew-witnessed kill rate: {0,1,2} / {3} / {4} | co-present departure: {0,1,2} / {3} / {4} |
|---|---|---|
| `p18-imp-ea4bc955` | 16/121 = 0.13223 · 9/39 = 0.23077 · 5/37 = 0.13514 | 12/121 = 0.09917 · 4/39 = 0.10256 · 4/37 = 0.10811 |
| `p18-imp-bfd145cb` | 16/122 = 0.13115 · 8/43 = 0.18605 · 6/38 = 0.15789 | 12/122 = 0.09836 · 4/43 = 0.09302 · 5/38 = 0.13158 |
| `p18-imp-6d327dcb` | 25/108 = 0.23148 · 10/41 = 0.24390 · 8/44 = 0.18182 | 20/108 = 0.18519 · 9/41 = 0.21951 · 7/44 = 0.15909 |
| `p18-imp-7f73929d` | 26/117 = 0.22222 · 10/42 = 0.23810 · 8/41 = 0.19512 | 18/117 = 0.15385 · 9/42 = 0.21429 · 8/41 = 0.19512 |
| `p18-fsm-comparator` — full 50, **pairs `ea4bc955` / `bfd145cb` / `6d327dcb` only** | 6/102 = 0.05882 · 1/36 = 0.02778 · 1/36 = 0.02778 | 0/102 = 0.00000 · 0/36 = 0.00000 · 0/36 = 0.00000 |
| `p18-fsm-comparator` — **49-seed, pairs `7f73929d` only** | 6/98 = 0.06122 · 1/36 = 0.02778 · 1/36 = 0.02778 | 0/98 = 0.00000 · 0/36 = 0.00000 · 0/36 = 0.00000 |
| *(no comparator row pairs the four crew arms — §2.1, ✥)* | *their split cells are committed and read as diagnostics only* | *—* |

**What this report does and does not say about it.** As recorded, each of the
four impostor arms sits **above** the same-seed comparator on **all three**
splits for both cells — the comparator's co-present column is 0 in every split,
so the departure's sign is positive wherever an arm has any co-present kill at
all. That is an **observation about the committed cells**, stated so the evidence
is legible. **This report does not apply the 2-of-3 sign rule and does not rule
on clause (b).** Clause (b) is one of four conjunctive conditions (§6: pooled
|z| ≥ 1.96 vs the same-seed FSM comparator, sign reproduction, a named ablation
showing the behaviour recede, and selected-for presence in the champion's own
recordings). **This task recorded no ablations** — clause (c) is not sourced from
the finalist eval. **The clause-(c) raw material lives in the campaign reports'
own §6 ablation runs**, and it is worth stating what those five runs actually
are, because an earlier draft of this paragraph listed them as though each were
clause-(c) evidence. Two things disqualify a run on the face of the source
reports: the registered naming is
**`ablation:<instrument-key>/<lever-id>`** — `ablation:*/…` names no instrument —
and the registered criterion needs **the ablated champion recorded on the claim
cell** showing the behaviour recede. Each run's status, in its own report's words:

| run | key | source report's own status |
|---|---|---|
| `ablation:*/conviction-term` — run-01 twin (impostor §6.1) | wildcard | recede **structurally impossible**: the twin selects the same genome, so "any sweep delta on run-01's impostor champion cannot be attributed to the conviction term … the behavior cannot recede because it is identical by construction" |
| `ablation:*/anchor-lambda=4.0` — run-02 twin (impostor §6.2) | wildcard | lever is selection-decisive, but the claim-cell recordings are **absent**: "completing that read for a meeting-layer cell **requires the ablated champion's REAL-path recordings** (priced ~2 h, scheduled only if tranche 2 sustains the delta)" |
| **`ablation:off-menu/encoder-v3`** (impostor §6.3) | **registered** (`off-menu`) | the only registered-key run, real path recorded, per-pair recede computed vs the same-seed comparator — **neither pair recedes** — but tranche 2 validity-FAILED and the verdict "is a **tranche-1 screen at n=3**"; "**This report therefore does NOT rule on `off-menu`** … the clause-(c) classification and any causal attribution are **deferred to 18.27**, which should resolve them against the 50-seed protocol rather than these bytes" |
| `ablation:*/conviction-term` — run-c2 twin (crew §6.1) | wildcard | "limb (c) is therefore **PARTIAL, not complete**" — the recede recording's "real-path arms are **deliberately NOT recorded**"; claim "**NOT-DEMONSTRATED at this budget**", handed to 18.27 as **UNABLATED-on-the-claim-cell** |
| `ablation:*/conviction-term` — run-c1 twin (crew §6.2) | wildcard | "same as §6.1 — selection-relevance recorded, **limb (c) PARTIAL** (no recede recording…), claim NOT-DEMONSTRATED at this budget and handed to 18.27 as **UNABLATED-on-the-claim-cell**" |

**So, plainly: none of the five is stated by its own source report as
clause-(c)-complete.** Four are wildcard-keyed and carry no claim-cell recede
recording at all — two of them say so in the words "PARTIAL, not complete" and
"UNABLATED-on-the-claim-cell". The fifth is the only one with a registered
instrument key **and** a computed real-path recede read, and its own report
declines to classify it, deferring clause (c) to 18.27 against the 50-seed
protocol. What these runs do establish — lever selection-relevance, byte-level
lineage divergence, committed twins — is real and is the material 18.27 works
from. **Whether any of it covers a given cell here remains 18.27's inspection**;
this report neither supplies clause (c) nor forecloses it, and now states the
inventory accurately enough that the inspection starts from what was recorded
rather than from a count of five.
**18.27 applies the rule**
against the committed per-split cells; §16.f's labels carry forward unchanged —
the crew columns are ✥ NOT-DEMONSTRABLE for want of an opponent-matched
comparator, and the two entropy rulings are ✧ NOT-DEMONSTRATED, on both axes.

### 16.h Clause (a) — the pooled z against the same-seed FSM comparator

§6.a's convention is that "the campaign/finalist report quotes the computed z with
its inputs beside it", so the clause-(a) statistic is computed here for **every
registered rate cell on every impostor arm**, against that arm's **same-seed**
comparator pairing: the comparator's **full-50** cells for `ea4bc955`,
`bfd145cb` and `6d327dcb`, and its **persisted 49-seed** cells
(`instruments.intersection_49_seed_for_7f73929d`) for `7f73929d` (§16.g). Both
numerators and denominators come from the committed rows and are printed per arm
in **§16.f**; each entry below is **pooled p̂ · z**, with **✱** marking
**|z| ≥ 1.96**. The correlation cell uses **Fisher's r-to-z** on the committed `r`
and `kills_total` per side, as §6.a registers for the non-rate cells.

| registered cell | `ea4bc955` | `bfd145cb` | `6d327dcb` | `7f73929d` (49) | arms at/over the bar |
|---|---|---|---|---|---|
| false-vouch `saw_player` | 0.11443 · +0.7610 | 0.12107 · +1.1264 | 0.14670 · **+2.4487 ✱** | 0.12000 · +1.3177 | **1** |
| false-vouch corroboration | 0.16667 · +1.5492 | 0.15200 · +1.1105 | 0.28800 · **+3.8088 ✱** | 0.23009 · **+2.7745 ✱** | **2** |
| fabricated-vouch share *(advisory)* | 0.35000 · −1.5600 | 0.35714 · −1.4326 | 0.46154 · −0.1333 | 0.39024 · −0.6294 | 0 |
| frame-attempt rate | 0.95833 · +1.3930 | 0.94953 · +0.5520 | 0.96238 · +1.8211 | 0.95975 · +1.0213 | 0 |
| frame-conversion rate *(advisory)* | 0.05351 · +0.9867 | 0.06312 · +1.5845 | 0.06515 · +1.6855 | 0.05484 · +1.5026 | 0 |
| teammate-accusation rate *(advisory)* | **degenerate** | **degenerate** | **degenerate** | **degenerate** | — |
| alibi survival *(advisory)* | 0.77778 · +0.2023 | 0.82540 · +1.1708 | 0.76271 · −0.0726 | 0.81667 · +1.0009 | 0 |
| deflection efficacy | 0.42208 · +0.6385 | 0.39355 · +0.0743 | 0.37778 · −0.2545 | 0.40816 · +0.4358 | 0 |
| crew-witnessed kill rate | 0.10243 · **+3.3701 ✱** | 0.10080 · **+3.2732 ✱** | 0.13896 · **+4.8898 ✱** | 0.14054 · **+4.7701 ✱** | **4** |
| co-present departure | 0.05391 · **+4.3211 ✱** | 0.05570 · **+4.3660 ✱** | 0.09809 · **+5.9988 ✱** | 0.09459 · **+5.7322 ✱** | **4** |
| off-menu rate | **degenerate** | **degenerate** | **degenerate** | **degenerate** | — |
| one-hop point-biserial *(Fisher)* | −0.6484 | −0.6792 | **+2.8078 ✱** | +0.7541 | **1** |
| **cells at/over the bar, per arm** | **2** | **2** | **5** | **3** | |

**The two degenerate rows are honest no-claim reads, per §6.a's own rule.**
`off-menu` is **0/N on both sides** (0/2015–0/2176 arm, 0/2299 and 0/2219
comparator) and `teammate-accusation` is likewise **0 on both sides** (0/214–0/225
arm, 0/190 and 0/187 comparator). A pooled rate of exactly 0 has no standard
error, so **no z exists** — not a z of 0, and not a pass. Both cells report
**no difference measurable**, which for `off-menu` is the vacuity its own
`scope_note` predicts for menu-bounded movers and for `teammate-accusation` is the
scripted structural invariant the pre-registration names. **The co-present cell is
NOT degenerate** even though the comparator is 0/174: the *pooled* rate is
nonzero, so the z is defined and is computed above.

**Crew arms are absent from this table because clause (a) is not computable for
them.** §2.1 requires the comparator to be **scripted-FSM crew against the same
opponent**, and no such row exists in this slate (✥, §16.f, §17.1). There is no
denominator to pool against, so no z is quoted — **NOT-DEMONSTRABLE stands**, and
substituting `p18-fsm-comparator` (scripted on both sides) would be the improvised
comparator §2.1 forbids.

**What this table is, and what it is not.** It is the **quoted clause-(a)
statistic**, nothing more. §6 is **conjunctive**: clause (b)'s split evidence is in
§16.g, clause (c)'s ablation inventory is in §16.g and **none of the five runs is
clause-(c)-complete as recorded**, and clause (d) (selected-for presence in the
champion's own recordings) is not evaluated here at all. A ✱ above therefore
marks **one limb of four**, on one cell, for one arm — it is **not** an emergence
finding, and two cells clearing the bar on all four arms is not four findings.
**18.27 rules**; this report computes and quotes.

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

- **The 18.26 contract was amended on `main` (`6f24ec3`, owner, 2026-07-31) to
  scope the forced flip-test relaxation** — this PR carries that work as
  **in-scope**, superseding the earlier handling that recorded it in Decisions
  only.
- **The crew block's axis-2 cells are labelled NOT-DEMONSTRABLE rather than
  rescued by a new recording — OWNER DECISION, 2026-07-31, ratified in-session.**
  Pre-registration §2.1 judges crew claims **opponent-matched**: the comparator
  for (crew finalist vs opponent O) is (scripted-FSM crew vs the **same** O, same
  seeds, same substrate), "or the crew claim on that opponent pairing reads
  NOT-DEMONSTRATED for want of a comparator". Every crew arm here ran against the
  frozen champion `ea4bc955…`, and the ratified slate contains **no**
  scripted-crew-vs-`ea4bc955…` row — `p18-fsm-comparator` is scripted on **both**
  sides, a different pairing. Two options were open: record the missing arm now,
  or label the cells. **The owner chose labelling**, because the crew block was
  ratified as a **diagnostic** (§8.3) and 18.25 named no crew finalist, so no
  claim this task was going to make depends on it — and recording an arm after
  the slate closed to rescue a cell is the shape of fitting evidence to a wanted
  conclusion. Recording scripted-crew-vs-`ea4bc955…` is therefore a **routed
  follow-up**, taken up only if 18.27 wants crew-side axis-2 claims. The crew
  cells stay in §16.f marked **✥** and are read as context; §16.b and §16.e's
  crew diagnostics are unaffected, since neither was ever an axis-2 claim.
- **Roll-call coverage is relabelled CONTEXT, not an axis-2 instrument — a
  labelling correction, not an amendment.** §13 of this report listed
  `eval.funnel.compute_pooling_funnel` among the instrument entry points. The
  ratified pre-registration does not: `audits/audit-phase-18-emergence-preregistration.md`
  §8 fixes the emergence set at **eight** instruments (Tier A `false-vouch`,
  `frame`, `teammate-immunity`, `alibi-survival`, `deflection`; Tier B
  `kill-craft`, `off-menu`, `action-entropy`) and §2.5 states that "roll-call
  coverage and conversion are standing eval gauges, not pre-registered emergence
  instruments". Its **§9 amendment log is empty**, and §9's own rule is that
  amendments land before the campaigns record "or not at all for this phase's
  claims" — so roll-call **cannot** be added now. The correction taken here is the
  minimal one: **§13's committed pre-registration text is left exactly as
  written** (rewriting it after recording is the amendment this rule forbids), the
  roll-call rows in §16.f are **labelled contextual diagnostics outside the
  ratified axis-2 set** (✦), and 18.27 reads them as context only. The cells stay
  in the report because they characterise each arm's meeting economy; they carry
  no axis-2 weight.

### 17.1 Decisions taken during the operator run (recorded after the fact)

- **Seed 35 is EXCLUDED from `p18-imp-7f73929d`, and the Δ is taken on the
  49-seed intersection.** The seed returned rc 99 on **14 logged attempts** — 4
  in-leg passes ending in a `leg-abort`, 6 `retry-stubborn.sh` rounds, and a
  final owner-directed 4-pass retry leg dispatched after this task's PR opened
  (§14.1) — while the other stubborn seed on the board, `p18-fsm-comparator`
  seed 5, came clean on attempt 14 and kept that arm at n=50. This **extends the
  owner's comparator ruling** (a stubborn seed is retried, and only excluded once
  retrying has plainly stopped converging) to an impostor arm, with two
  conditions attached: the **forensics are kept** — all 6 stubborn recordings
  live under `~/ailibi-campaign-1826/forensics/` rather than being deleted — and
  the **Δ is recomputed on the 49-seed intersection** rather than quoted against
  a 50-seed comparator. The comparator's seed-35 game is an `IMPOSTOR_PARITY`, so
  the intersection comparator is **12/49 = 0.24490**, not 0.26, and the arm's Δ
  is **+0.18367**. Quoting the full-50 comparator against a 49-seed arm would
  have moved the arm's Δ by 0.01510 (to +0.16857) on the strength of a seed the
  arm never recorded — understating it here, but the objection is the mismatched
  seed sets, not the sign; the
  cross-seed-set number appears in §16.a only to be named and rejected. Every
  `p18-imp-7f73929d` cell in this Part is annotated **n=49**.
- **The two starvation validity-FAIL rows are COMMITTED, not dropped.**
  `p18-crew-c2-gen0` (`meeting_rate_and_resolution`,
  `cost_and_provenance_exact`) and `p18-crew-c2-gen9`
  (`all_games_reach_game_over`, `cost_and_provenance_exact`) both FAIL the gate,
  and both rows appear in §16.b with their violations quoted **verbatim** from
  `validity.json`. This is the gate-validity discipline applied in the direction
  that costs something: the alternative — quietly scoring 8 arms and reporting 6
  — would have removed the only two rows that show what the c2 lineage actually
  does, and would have laundered a starvation result into an absence. The
  discipline's other half is enforced in the same table: **no gate-invalid cell
  is read as selection evidence**, so `c2-gen9`'s 7/48 and `c2-gen0`'s 1/50 crew
  conversions are marked unreadable at the point of use, not merely footnoted.
- **The deterministic-stalemate finding: LLM-free games are engine-deterministic
  and therefore UNRETRYABLE by construction.** `p18-crew-c2-gen9` seeds 19 and
  20 exhausted the tick budget without a `game_over` row. The runner treated them
  as missing and re-recorded them, and the leg log shows why that could never
  work: passes 2, 3 and 4 completed at `06:17:18Z`, `06:18:38Z` and `06:19:58Z`
  — **80 seconds apart** — each reporting **`missing: 2`**, before `leg-abort` at
  `06:20:58Z`. A game that reaches no meeting makes no LLM call, and with no LLM
  call the engine is a pure function of the seed: re-recording reproduces the
  identical stalemate, byte for byte, in seconds. **Retry budget is the wrong
  instrument for this failure mode** — the seed-retry machinery assumes provider
  nondeterminism as the thing being retried against, and there is none here. The
  correct handling is what was done: stop retrying, record the two seeds as
  stalemates, fail the gate honestly, and score the finalized view.
- **`score-arm.py` computes `p18-crew-c2-gen9`'s instruments over the 48-game
  FINALIZED view (the byte-completeness fence).** Per §13 the byte-completeness
  fence runs **first** on every recording dir, and the two stalemate replays
  carry no `game_over` row, so they are not byte-complete games. The arm's
  instruments are therefore computed over a staged 48-game view
  (`scoring/p18-crew-c2-gen9/instruments-view/`), and `instruments.json` records
  the exclusion in its own `instruments_view` block:
  `{"games": 48, "excluded_stalemates": ["replay-seed-19.jsonl",
  "replay-seed-20.jsonl"]}`. The consequence is that this arm's kill-craft
  denominator is **231 kills over 48 games**, while `validity.json` — which reads
  the full 50-game directory precisely so it can *see* the stalemates — reports
  **238** total kills. The two numbers disagree **by design**; the fence keeps
  partial games out of the instruments while the gate keeps them visible. Every
  `c2-gen9` **instrument** cell — §16.b's kill-craft column, §16.e's rider row
  and the §13 emergence set in §16.f — is the 48-game view, and is labelled as
  such where it is quoted. **§16.c is deliberately NOT in that list:** the
  split-half halves are computed over the arm's **full recorded view** and stay
  at **25/25**, because the byte-completeness fence applies to the instruments
  only, never to the watchability halves (§16.c states this in its own words).
- **`p18-crew-c1-gen0` seed 20 is KEPT IN-ROW as a recorded stalemate, and the
  row ships validity-FAIL-recorded.** The seed was attempted **8 times** — 4
  in-leg passes plus a bonus 4-pass v2 run after the `leg-abort` — and **every
  attempt returned rc 0** while producing the identical outcome: a complete
  1002-row replay reaching **tick 999** with no `game_over` row (§14.1). It is
  handled exactly like the c2 stalemates: kept in the directory, failing the gate
  in the open (`"seed 20: no game_over row (game never reached game_over)"`,
  `"seed 20: no substrate_flags stamp on game_over"` — both violations trace to
  this one seed), with instruments computed over the **49-game finalized view**
  behind the byte-completeness fence
  (`instruments.json` `instruments_view` = `{"games": 49, "excluded_stalemates":
  ["replay-seed-20.jsonl"]}`). It was **not** excluded the way `7f73929d` seed 35
  was, because the two failures are not the same thing: seed 35 was an **impure
  validation** (rc 99, nothing usable recorded), whereas seed 20 recorded
  cleanly 8 times and the game itself is what did not finish.
- **The stalemate finding EXTENDS to a meeting-bearing, non-deterministic
  class — a third stuck-seed class.** The c2 stalemates were explicable: no
  meetings, no LLM calls, engine-deterministic, so retrying was mathematically
  hopeless. Seed 20 is **not** that. It holds **2 meetings**, so it *does* make
  LLM calls and *is* nondeterministic between attempts — and it still stalled at
  tick 999 on all 8 tries. **Nondeterminism is therefore not sufficient for a
  retry to help.** The campaign's three stuck seeds are three distinct classes,
  and the runner's single `rc != 0` retry trigger sees only one of them:
  1. **impure validation** (`fsm-comparator` seed 5, `7f73929d` seed 35) — rc 99,
     retryable, and the two seeds took the same 14 attempts to opposite ends —
     `fsm-comparator` seed 5 converged on attempt 14, `7f73929d` seed 35 never
     converged in 14;
  2. **LLM-free deterministic stalemate** (`c2-gen9` seeds 19, 20) — rc 0,
     **unretryable by construction**, reproduced byte-identically in ~80 s;
  3. **meeting-bearing robust stalemate** (`c1-gen0` seed 20) — rc 0,
     nondeterministic, **retryable in principle and hopeless in practice** at 8
     attempts.
  Classes 2 and 3 both exit `rc 0`, so the retry machinery never sees them as
  failures at all; both were caught by the scorer's `game_over` check, not by the
  runner. That is the operational lesson this campaign hands forward.

## 18. Errata (coordination, 2026-08-04 — the Task 19.20 report-honesty pass; additive, no in-place rewrites)

Anchor: `audits/audit-phase-19-triage.md` §7 item 20 [S-Codex/S-Claude], whose §8
row 4 recomputation is marked **VERIFIED exactly**, together with the triage's
contradiction rulings **C2** (the paired win edge) and **C9** (the
conversion-vs-decision terminology). Every item below is **additive**: no recorded
byte, no table cell, and no verdict above this section is rewritten, and the
committed `training/reports/results-finalist-eval.jsonl` is read, never edited.
**One reading does change, and it is named plainly** — item 1 removes the
inferential license from §16.a's win-edge sentence for the shipped champion. Item 2
records a possible mechanism and is explicitly uncausal as measured. Item 3 records
what these items do **not** touch.

1. **§16.a's impostor win edge was recorded as a bare point estimate, with no
   paired uncertainty treatment — item 1 supplies it, and the shipped arm's edge
   does not survive.** The report states (:1082-1087): "Every impostor arm beats
   the fresh comparator; every impostor arm fails the referee on the same two
   supply gauges." and "The four learned arms sit **+0.12 to +0.30** above it on
   wins". Both sentences are arithmetically correct — every Δ cell in §16.a
   reproduces from the committed rows — but the win-edge cells carry **no interval
   and no test**, so "beats" was doing inferential work the recording never
   supported. The report applies exactly this discipline elsewhere (two-proportion
   z on the emergence gauges, :232; an exact McNemar on the crew pair,
   :1746-1770); it never applied it to the impostor win edge. This erratum does.

   **The recomputation.** An exact (binomial) McNemar test on each arm's per-game
   rows against the **same-seed** `p18-fsm-comparator` rows, plus Wilson score
   intervals on each side's win rate. Every row is read from the committed
   `training/reports/results-finalist-eval.jsonl`, which is consistent with this
   report's own provenance separation — §2 (:115-118) records that the raw
   recordings "live **outside** the repo tree… What is committed is their
   **measurement**", and §16 (:1066-1070) records that the committed measurement
   is what every cell is read from. The paired test therefore runs entirely on
   committed bytes and needs no access to the external slate.

   | arm | n | wins (arm/comparator) | Δ | discordant b/c | exact McNemar p | Wilson 95% (arm) | Wilson 95% (comparator) |
   |---|---|---|---|---|---|---|---|
   | `p18-imp-ea4bc955` | 50 | 26 / 13 | +0.26 | 17/4 | **0.0072** | [0.3851, 0.6520] | [0.1587, 0.3955] |
   | `p18-imp-bfd145cb` | 50 | 28 / 13 | +0.30 | 20/5 | **0.0041** | [0.4231, 0.6884] | [0.1587, 0.3955] |
   | `p18-imp-6d327dcb` | 50 | 19 / 13 | +0.12 | 15/9 | **0.3075 — n.s.** | [0.2586, 0.5185] | [0.1587, 0.3955] |
   | `p18-imp-7f73929d` | 49 | 21 / 12 | +0.18367 | 12/3 | **0.0352** | [0.3002, 0.5673] | [0.1460, 0.3809] |

   **In plain language, first: the SHIPPED champion's edge is not statistically
   significant.** `p18-imp-6d327dcb` runs the artifact this repo actually ships —
   the committed weights at `agents/tactical/learned/weights.json`, sidecar
   `6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0`. Its paired
   edge is **+0.12 on 15/9 discordant seeds, p = 0.3075**: **not statistically
   significant at n=50**, at any conventional level. A 15-vs-9 discordant split is
   what a coin does. **The Phase-18 edge of the artifact the repo actually ships is
   statistically unresolved.** §16.a's "every impostor arm beats the fresh
   comparator" stays true as a statement about point estimates, and must not be
   quoted as a demonstrated advantage for this arm.

   **Second: across the four-arm family, one more arm falls to the multiplicity
   correction.** Four learned arms were tested against the same comparator, so the
   family-wise bar is Bonferroni **α = 0.05 / 4 = 0.0125**. Against it,
   `p18-imp-7f73929d` (p = 0.0352) **fails the multiplicity correction**; only
   `p18-imp-ea4bc955` (p = 0.0072) and `p18-imp-bfd145cb` (p = 0.0041) survive it.
   Two of the four arms hold a family-wise defensible win edge, and the shipped one
   is not among them.

   **Recompute:**

   ```
   uv run python scripts/paired_stats.py training/reports/results-finalist-eval.jsonl
   ```

   (exact binomial McNemar on the discordant pair + Wilson score intervals,
   `scripts/paired_stats.py`, pinned by `tests/scripts/test_paired_stats.py`.) The
   method is not new to this report: §16 already applies it to the crew pair — the
   c1 gen-9/gen-0 exact McNemar at :1746-1770, where "**38 of the 49 seeds are
   concordant**… McNemar's exact two-sided test on those discordants gives **p =
   1.0**". This erratum applies that same standard to the impostor win edge, which
   the report itself never did.

2. **The four learned arms were trained under a reward-shaping term whose
   docstring claim was mathematically false.** Every arm in §16.a was trained
   through `training/rewards.py`, whose module docstring headed its shaping term
   "**Potential-based shaping (Ng et al. 1999, policy-invariant).**" and asserted:
   "At ``γ = 1`` the shaping TELESCOPES: ``Σ_t F = Φ(terminal) − Φ(initial)`` for
   ANY episode, so it cannot change the optimal policy." — quoted from
   `training/rewards.py` as committed at `09cd2416`, the last state of that file
   before the Task 19.4 correction. **The claim is false as deployed.** Telescoping
   is not invariance: Ng-1999 policy invariance needs one further hypothesis this
   module does not satisfy — a trajectory-INdependent terminal potential — and
   `_side_potential` here is a CUMULATIVE count (impostor: kills; crew: completed
   task instances). Φ(terminal) is therefore trajectory-DEPENDENT, the shaping sum
   at γ=1 equals the episode's terminal kill count, and the term is a real
   **+1-per-kill incentive** added to the return rather than a policy-neutral
   transform. Corrected in code by Task 19.4; the non-invariance is now pinned by a
   committed test in `tests/training/test_rewards.py`.

   **Why it is recorded in this report.** It bears on this report's central
   negative: all four learned arms fail the referee on the same two
   evidence-supply gauges (`flags_per_meeting` and `testimony_backed_conversion`,
   §16.a), and a +1-per-kill incentive is a possible contributor to evidence-starved
   play. **Uncausal as measured**: no committed measurement isolates the shaping
   term's contribution to those gauges — no ablation of the shaping term was ever
   recorded — so it is entered here as a **possible mechanism, not an established
   cause**. **No computed value in this report moves.**

3. **What items 1-2 do NOT touch: the retained findings, still quotable exactly as
   recorded.** Neither item reaches this report's positively-established findings,
   which are rate contrasts rather than the paired win edge:
   - **N1 — the learned mover kills into witnesses at ~3.3× the scripted rate.**
     Crew-witnessed-kill rate **0.15228 = 30/197** against the comparator's
     **0.04598 = 8/174**, **z = +3.370**, sign-reproduced **3/3**.
   - **N2 — the learned mover emits a kill class the FSM structurally never does.**
     Co-present-kill departure rate **0.10152 = 20/197** against **0.0 = 0/174**,
     **z = +4.321**, sign-reproduced **3/3**.

   Both are from `audits/audit-phase-18-flip-emergence.md` §8.3, with the
   underlying cells carried in this report's §16.a witnessed-rate column. They are
   rate contrasts measured at **z = +3.4 / +4.3** — a different instrument, a
   different quantity, and a different order of evidence from a +0.12 win-rate
   point estimate — and they **survive item 1 untouched**.

   The program's clean negatives likewise remain standing and quotable (the set
   catalogued at `audits/audit-phase-19-triage.md` §4 item 23): the **torch PPO
   probe NO**; the **policy-es real-path annihilation** (win 0.02, Δ −0.34 in §3.a;
   "stays competitively annihilated (0.00 → **0.02**…)" at :207); and the
   **crew-track null** — this report's own §16 crew-pair exact McNemar at **p =
   1.0**, recorded there as "a **null, not an equivalence**". Item 1 weakens the
   shipped champion's win-edge claim. It does not weaken any of these.

## 19. Availability erratum (coordination, 2026-08-15 — the Task 19.21 raw-slate ruling; additive, no in-place rewrites)

Anchor: `audits/audit-phase-19-triage.md` §7 item 22 [C; VERIFIED §8 row 11] —
"**Recover/content-address the finalist raw slate if it still exists; otherwise
mark event-level lineage non-reproducible. Do not re-record.**" This section is
**additive** and records exactly one thing: **where the bytes this report was
measured from now live**. No cell, table, statistic, or verdict above it moves,
and **nothing was re-recorded** (item 4).

1. **The ruling, checked 2026-08-15: RECOVERED.** §2 (:115-118) records the
   provenance separation — "the raw recordings are working artifacts — they live
   **outside** the repo tree… What is committed is their **measurement**" — and
   §16 (:1066-1070) names that external source for every recorded cell:
   "`~/ailibi-campaign-1826/scoring/<arm>/` JSON". The triage read the two
   together and found the gap: the flattened rows in
   `training/reports/results-finalist-eval.jsonl` are committed, but the
   **event-level lineage under them was repo-external and uncommitted** —
   `git ls-files training/reports/_finalist_eval_raw` returned nothing, and the
   external path had never been checked for survival.

   The owner-machine check found `~/ailibi-campaign-1826/` **intact**:
   **1,569 files, 298.2 MiB**, carrying all **449** raw per-seed recordings,
   all 450 audit sidecars, every `scoring/<arm>/` measurement JSON this report's
   §16 cells are read from, the 10 forensics recordings, the operator leg and
   per-seed logs, and the `score-arm.py` / `assemble-row.py` scorers that turned
   the events into the committed rows. The census reproduces the slate as this
   report records it: §8's ratified cut is 9 arms × 50 = **450 games**, §14
   (:998) records what the slate actually recorded — "**449** seed-games (8 arms
   × 50 seeds + `7f73929d`'s 49)" — and the disk carries **449** raw recordings,
   with seed 35 absent by construction as :935 records it ("**excluded,
   forensics kept**", 14 logged attempts, every one rc 99; §16.a carries that
   arm at n=49). Its audit sidecar and six forensics recordings are retained, so
   even the excluded game keeps a lineage.

2. **Content-addressed, staged, and destined for the evidence store.** Every one
   of the 1,569 files carries a sha-256 in the new
   **`training/reports/_finalist_eval_raw/MANIFEST.md`**, which also tabulates
   the 1,433 split-view symlinks by membership (the seeds each view held) rather
   than duplicating 612.3 MiB of already-hashed recordings. The bytes are staged
   on the temporary ref **`evidence/raw-slate-staging`** @
   `c27ab7b5f5e7e10bfab5c6dc752362b137862cac`; **Task 19.22** folds them into the
   ONE immutable evidence commit (`evidence/phase-18-coevo`) as **class-(c) large
   immutable evidence** and retires the staging ref. They do **not** join
   `replays/samples/` or `replays/ml_corpus/` and they do not enter the working
   tree, so §2's separation stands unchanged. The hashes were checked at
   **1,569/1,569 OK** against the staged copy, the staging commit's extracted
   tree, and a fresh anonymous fetch of the pushed ref; the manifest's §5 carries
   the command.

3. **The boundary — what recovery does and does not buy.** It buys the exact
   bytes behind every §16 cell, hash-pinned: the flattened rows are re-derivable
   from the events, the stamp==sidecar claim is auditable game by game, and the
   recovered bytes are provably the recorded ones. It does **not** make the
   recording reproducible. These are real-provider recordings
   (`Qwen/Qwen3.6-27B` on Featherless); a seed alone does not regenerate them,
   and the recording itself is the determinism boundary. §2's "**re-recordable
   from this recipe**" is therefore a statement about the *recipe* producing a
   *new* slate — not about these bytes being regenerable, which they are not.
   Separately, and unchanged by this ruling: **every flattened row and every
   derived statistic in this report was already reproducible from committed
   cells** — item 1 of §18 recomputed the paired statistics entirely from
   `results-finalist-eval.jsonl` "and needs no access to the external slate".

4. **Not re-recorded, and none is scheduled.** §14 prices the slate at a
   **58.705 h** span / **57.1589 busy hours**. That price is named and declined
   by charter: these are the original `2026-07-29T07:17:48Z →
   2026-07-31T18:00:06Z` bytes, preserved, not reproduced.

## 20. Availability erratum II (coordination, 2026-08-26 — the fold completed and verified; additive, no in-place rewrites)

Anchor: `audits/review-2026-08-19/C/p2-ml-research-lead.md` §3 item 3, the
research read of this report — "the 449-game finalist raw slate behind the
adoption ruling is not in the repo — the derived cells reproduce, the raw evidence
does not." §19 above answered half of that on 2026-08-15 and left the other half a
promise: it put the bytes on a **temporary** `evidence/raw-slate-staging` ref and
said Task 19.22 would fold them into the durable evidence commit. That promise
carried no destination sha, no restore command, and no result from the fold itself
— §19 item 2's 1,569/1,569 OK is the check on the **staged** copy, taken before it
— so a reader had no way to watch it be kept. This section supplies exactly those
three. Additive in the sense §18 and §19 are: no cell, table, statistic or verdict
above it moves, and nothing was re-recorded.

1. **Where the bytes are, by sha.** The fold is done. All 1,569 files /
   298.157 MiB sit on the ONE orphan evidence commit **`evidence/phase-18-coevo`
   @ `476a1f85492439277350af9708f1d120eb1c0a71`**, under `finalist-eval-raw/`.
   That sha is pinned in `training/artifacts/coevo/EVIDENCE-MANIFEST.md` §1 and
   the fetch is by sha, never by branch name — a branch is a moving pointer and
   the sha is the whole immutability guarantee (`docs/artifacts.md`, class (c)).
   §19 item 2's staging ref `evidence/raw-slate-staging` @
   `c27ab7b5f5e7e10bfab5c6dc752362b137862cac` is **superseded**: nothing reads it,
   and deleting it is the one owner step still open (`EVIDENCE-MANIFEST.md` §4,
   with the current status in `docs/artifacts.md`'s class-(c) detail).

2. **The one command that restores them, and what it printed.**

   ```bash
   bash scripts/fetch_evidence.sh   # fetch by the pinned sha, restore, verify
   ```

   Its verification leg is the result §19 owed and did not have. At the Phase-19
   close it read **"OK: 2953/2953 files match
   476a1f85492439277350af9708f1d120eb1c0a71."** — every file of both class-(c)
   payloads (this slate's 1,569, the co-evolution prune's 1,383, and the branch
   README) hashed against its manifest, quoted in `audits/audit-phase-19-close.md`
   §1. `uv run python scripts/verify_ml_evidence.py --complete` re-asks the same
   question on demand and carries the slate as an availability row of its own.

3. **What that makes checkable in this report.** Three places above describe the
   slate as repo-external. Each is correct as recorded and none is rewritten:
   §2's provenance separation (:115-118) — "the raw recordings … live **outside**
   the repo tree"; §16's source line (:1066-1070), which reads every recorded cell
   from a `~/ailibi-campaign-1826/scoring/<arm>/` JSON; and the nine
   `/Users/danielkeinan/ailibi-campaign-1826/…` `replay_set_dir` values kept
   **verbatim** in `training/reports/results-finalist-eval.jsonl` under §9.2's
   as-recorded rule. All three name the operator working root this campaign ran
   in, and the bytes that root held are the bytes on the pinned commit in item 1 —
   so a reader who wants the event-level lineage under any §16 cell runs item 2's
   command and reads it at `training/reports/_finalist_eval_raw/`. The recorded
   paths stay exactly as recorded; this section is the map from them to the
   archive, not an edit to them.

4. **What recovery still does not buy.** §19 item 3's boundary stands unchanged:
   these are real-provider recordings (`Qwen/Qwen3.6-27B` on Featherless), so a
   seed does not regenerate them and the recording itself is the determinism
   boundary. Auditability is what the pin buys. Separately and as before, every
   derived statistic here was already reproducible without the slate — §18 item 1
   recomputed the paired tests from `results-finalist-eval.jsonl` alone.
