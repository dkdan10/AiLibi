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
answer beside it. Every figure below is read from a committed
`scoring/<arm>/duration.json` or computed arithmetically from the
`~/ailibi-campaign-1826/leg-log-*.jsonl` rows. No projected hour count appears as
a measurement.

**Per-arm, as logged.** `games_ok` is the leg's **recorded**-game count
(retries included), not the finalized scored set — the two differ wherever a
purity retry re-recorded a seed.

| arm | games_ok | retry events | summed leg wall (s) | mean min/game | leg elapsed (h) |
|---|---|---|---|---|---|
| `p18-imp-ea4bc955` | 52 | 5 | 46460 | 14.891 | 14.295 |
| `p18-imp-bfd145cb` | 50 | 0 | 43056 | 14.352 | 12.223 |
| `p18-imp-6d327dcb` | 50 | 2 | 44529 | 14.843 | 13.045 |
| `p18-imp-7f73929d` | 49 | 5 | 49685 | 16.900 | 14.997 |
| `p18-fsm-comparator` | 50 | 10 | 46402 | 15.467 | 16.151 |
| `p18-crew-c1-gen9` | 50 | 0 | 54212 | 18.071 | 15.059 |
| `p18-crew-c1-gen0` | 57 | 3 | 54775 | 16.016 | 16.241 |
| `p18-crew-c2-gen9` | 56 | 1 | 9342 | 2.780 | 2.774 |
| `p18-crew-c2-gen0` | 50 | 0 | 27 | 0.009 | 0.008 |
| stubborn rounds (both seeds) | 11 attempts | — | 7821 | — | 2.173 |

**Summed wall.** The nine legs sum to **348488 s = 96.8022 h** over **464**
recorded games ⇒ **12.5175 min/game serial**, **2.5% above** the pre-registered
**12.2077 min/game** — the 18.25-derived rate transferred to this slate with a
margin narrower than any gauge on the board. Adding the 11 stubborn-round
attempts (7821 s) gives **356309 s = 98.9747 h** of leg wall for the campaign.

The pooled rate is pulled **down** by the two starved c2 legs. Over the **seven
meeting-bearing** legs (the four impostor arms, the comparator, `c1-gen9`,
`c1-gen0`) the serial rate is **339119 s = 94.1997 h over 358 games ⇒ 15.7877
min/game** — **29% slower** than the pre-registered 12.2077, because 18.25's rate
was measured on crew-vs-champion games and this slate's meeting-rich impostor
legs run longer meetings.

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
  `2026-07-31T08:33:09Z`), and a **final owner-directed retry run** of 4 more
  in-leg passes (all rc 99, 2981 s summed wall, `leg-abort` after the last at
  `2026-07-31T17:58:35Z`). The failure anatomy is **identical in every kept
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
- Stubborn wall: **3676 s** on comparator seed 5, **4145 s** on seed 35 in the
  stubborn rounds plus **2981 s** in the final retry run (**7126 s** for the
  seed in total), **10802 s** across both seeds; seed 20's 8 attempts cost a
  further **4829 s** inside its own leg.

**The c2 legs are fast because meetings are scarce, not because the provider was.**
`c2-gen9` runs at **2.780 min/game** (whole leg 2.5950 h) and `c2-gen0` at
**0.009 min/game** — its 50 games recorded in **27 seconds total**, which is the
duration signature of a leg that makes **zero LLM calls** (§16.b, §16.e).

**The effective rate, recomputed on the complete slate.** Campaign span
`2026-07-29T07:17:48Z → 2026-07-31T15:38:33Z` = **56.346 h**, of which only
**0.117 h** is idle — a single 7-minute pause across two and a third days. Inside
it the slate recorded **449** seed-games (8 arms × 50 seeds + `7f73929d`'s 49)
⇒ **7.5295 min/game effective** at the two-leg posture, i.e. **≈ 6.27 h per
50-seed arm** and **≈ 56.5 h** for a 450-game slate. Read per completed arm
instead: **9 arms in 56.346 h = 6.261 h/arm** — the two readings agree to within
a minute per arm.

| unit | pre-registered (§14) | **measured** |
|---|---|---|
| serial rate | 12.2077 min/game | **12.5175** pooled / **15.7877** meeting-bearing legs only |
| one 50-seed arm, two-leg effective | ≈ 5 h | **≈ 6.27 h** (6.261 h/arm by completed-arm count) |
| the 9-arm slate (≈450 games) | ≈ 46 h | **≈ 56.5 h** |

**The projection was honest and optimistic by about a fifth.** The serial rate
it was built on came in at **12.5175** against a predicted 12.2077 — **2.5%
off**, an unusually good call. What the projection missed was the *posture*: the
gate priced "~5 h/finalist" and the two-leg rolling posture delivered
**≈ 6.27 h**, so the slate landed at **≈ 56.5 h** against ≈46 h, **23% over**.
The gap is not the provider — idle time across the whole campaign is 0.117 h. It
is the meeting-bearing legs' **15.7877 min/game**, the three sleep stalls
(3.881 h of real wall-clock), and the **32 recording attempts** spent on three
stuck seeds to salvage one of them.

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
`testimony_backed_conversion`. This is the Part I §3.a shape reproduced at
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

**`flags_per_meeting` reads UNRESOLVABLE on exactly two arms** —
`p18-imp-bfd145cb` (noise 0.29291 vs ceiling 0.27273, a 7% overshoot) and
`p18-crew-c2-gen9` (noise **1.30** vs 0.27273, a 4.8× overshoot). The c2-gen9
cell is **the §10.4 prediction landing**: the pre-registration named
`flags_per_meeting` "the UNRESOLVABLE-prone gauge on the meeting-scarce crew
lineage", quoting the committed n=3 `noise_to_threshold_ratio` **1.8333** for c2
against **0.3303** for c1. At n=50 the measured ratio is
**1.30 / 0.27273 = 4.767** on c2-gen9, against **0.17592 / 0.27273 = 0.645** on
c1-gen9 and **0.15068 / 0.27273 = 0.553** on c1-gen0 — c2 is worse than
predicted and **both** c1 arms clear. The prediction's **direction** is confirmed
on both sides of the lineage split; its **magnitude** understated the c2 problem.

`testimony_backed_conversion` **clears the precondition on every arm that has
meetings** (8 of 8), with noise between 0.00380 and 0.08357 — it is the most
stable gauge on the board and the one 18.27 can read most safely.

### 16.d Cell 2 — the F13 champions-vs-runner-ups cell (§11)

Champions `6d327dcb…` and `ea4bc955…` vs runner-ups `bfd145cb…` and
`7f73929d…`, pooled as plain two-arm means. The **margin** is
`runner-up mean − champion mean`. `7f73929d` contributes an **n=49** cell.

| gauge | `6d327dcb…` | `ea4bc955…` | `bfd145cb…` | `7f73929d…` (n=49) | champion mean | runner-up mean | margin | split-half noise (max across the four) | reads toward |
|---|---|---|---|---|---|---|---|---|---|
| `witnessed_event_rate` | 0.22280 | 0.15228 | 0.14778 | 0.22000 | 0.18754 | 0.18389 | **−0.00365** | 0.08671 | (18.27 rules) |
| `flags_per_meeting` | 0.96914 | 0.93548 | 0.90000 | 0.82840 | 0.95231 | 0.86420 | **−0.08811** | 0.29291 | (18.27 rules) |
| `testimony_backed_conversion` | 0.44444 | 0.36667 | 0.35099 | 0.38926 | 0.40556 | 0.37013 | **−0.03543** | 0.08357 | (18.27 rules) |

**Every margin is smaller than the largest split-half noise on its own row**, and
on **one** of three rows — `witnessed_event_rate` — smaller than *every*
contributing arm's noise. On the other two rows the margin exceeds the quietest
arm's noise (flags 0.08811 > `7f73929d`'s 0.01728; conversion 0.03543 >
`bfd145cb`'s 0.01146 and `7f73929d`'s 0.00380) while still sitting under the
loudest, as the bullets below itemise. Per §11.2 a margin smaller than either
side's split-half noise "is reported as such and cannot be read as support for
A".

- `witnessed_event_rate`: margin **0.00365** against noises of 0.02700–0.08671 —
  the margin is **7 to 24 times smaller** than the noise. This row is also
  UNRESOLVABLE on all four arms (§16.c), so it carries **no** discriminating
  weight in either direction.
- `flags_per_meeting`: margin **0.08811** against noises of 0.01728–0.29291. It
  exceeds `7f73929d`'s noise (0.01728) but sits well under `bfd145cb`'s
  (0.29291), and `bfd145cb`'s cell is itself UNRESOLVABLE.
- `testimony_backed_conversion`: margin **0.03543** against noises of
  0.00380–0.08357. This is the **only** row where the precondition clears on all
  four arms, and the margin still sits below the largest contributing noise
  (0.08357) while exceeding the two smallest (0.00380, 0.01146).

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
opposite direction to A's "one step less far along the trade") and all three are
**smaller than the split-half noise** they must clear. **The ruling is 18.27's.**
Nothing in this Part declares A or B confirmed.

**The within-lineage pair** (`run-02-utility-lambda4`: `ea4bc955…` gen-2 vs
`bfd145cb…` gen-9) — the one comparison where lineage is held constant and only
the champion/runner-up position moves, quoted as its own cell:

| gauge | `ea4bc955…` (gen-2, champion) | `bfd145cb…` (gen-9, runner-up) | difference (runner-up − champion) | noise `ea4bc955` | noise `bfd145cb` |
|---|---|---|---|---|---|
| `witnessed_event_rate` | 0.15228 | 0.14778 | **−0.00450** | 0.06417 | 0.02700 |
| `flags_per_meeting` | 0.93548 | 0.90000 | **−0.03548** | 0.17821 | **0.29291** (UNRESOLVABLE) |
| `testimony_backed_conversion` | 0.36667 | 0.35099 | **−0.01567** | 0.08357 | 0.01146 |
| impostor win rate | 0.52 | **0.56** | **+0.04** | — | — |

**On the cleanest read available, all three gauge differences are inside the
noise on at least one side, and two of three are inside the noise on both.** The
lineage-mate runner-up scores marginally *lower* on every gauge and marginally
*higher* on wins — the same negative-margin direction as the pooled cell, at a
magnitude no smaller than the instrument's own wobble.

**What `bfd145cb`'s UNRESOLVABLE flags precondition excludes.** `bfd145cb…` is
the **only** arm in the F13 quartet whose `flags_per_meeting` fails the noise
precondition (0.29291 > 0.27273). By §10.3 that cell is excluded from 18.27's
axis-1 ruling, which means **the `flags_per_meeting` row of this cell cannot be
read as a within-lineage result at all** — the within-lineage pair is exactly
`ea4bc955` vs `bfd145cb`, so an UNRESOLVABLE on one side removes the row. What
survives the within-lineage read is `testimony_backed_conversion` (both sides
clear) and, formally, `witnessed_event_rate` — except that gauge is
UNRESOLVABLE on **every** arm (§16.c). **So the within-lineage cell rests on one
gauge: `testimony_backed_conversion`, difference −0.01567.** That is the honest
width of the cleanest F13 read this campaign produced, and 18.27 should read it
knowing it is one gauge wide.

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

**The pre-registered branch that fires is the ARTIFACT one: gen-9 ≈ gen-0, both
above corpus.** The margin is **−0.00793** — the *untrained* gen-0 control sits
marginally **higher** than the gen-9 candidate, which is the opposite of a
learning effect and is in any case a gap of well under one witnessed kill in a
hundred. Both arms sit at **6.61×** and **6.94×** the 12/505 corpus cell. §12's
own words for this outcome: "gen-9 ≈ gen-0, both above corpus" ⇒ **artifact**,
not a learned-crew observation effect.

**And the artifact reading is over-determined.** Three independent cells now say
the same thing, each removing a different candidate cause:

- the four **impostor** arms run 6.2×–9.4× corpus against **scripted** crew —
  removes *learned crew* as a requirement;
- **`c2-gen0`** runs 6.04× corpus with **zero meetings and zero LLM calls** —
  removes the *meeting economy* and the *language model* as requirements;
- the **c1 gen-9-vs-gen-0** pair shows **no generation effect at the same frozen
  opponent** — removes *crew training* as the driver on the one lineage that
  could have carried it.

What is left is the **impostor** side and the physical layer, with the
`fsm-comparator` row as the control that isolates it: same seeds, same substrate,
same instrument, **1.93×** (z +0.5782, within noise of the floor) for the
scripted mover against **6.2×–9.4×** for every learned one. **The routed rider
from 18.25 is answered: the elevation is an artifact of learned-impostor kill
placement, not a learned-crew observation effect.**

**The conversion read on the same pair — same-seed, 49-seed intersection.**
`c1-gen0`'s seed 20 is the stalemate, so the honest comparison excludes it from
**both** arms; `c1-gen9`'s seed-20 game was an `IMPOSTOR_PARITY`, so dropping it
costs gen-9 no crew win:

| c1 lineage arm | crew wins / 49-seed intersection | conversion |
|---|---|---|
| `p18-crew-c1-gen9` | 26/49 | 0.53061 |
| `p18-crew-c1-gen0` | 25/49 | 0.51020 |
| **margin** | **+1 game** | **+0.02041** |

**One game.** After ten generations of crew evolution, the gen-9 candidate
converts one more game than its own untrained gen-0 control on the same 49 seeds
against the same frozen opponent. **There is no learning signal on the c1
lineage** — which is consistent with 18.25 naming no crew finalist, and is
recorded here as the n=50 confirmation of that hand-off rather than as a new
result.

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
identical numbers and not a re-derivation. Every baseline cell is read from
`training/artifacts/coevo/realpath/baseline-cells-corpus.json`,
`baseline_cells_corpus_9p2i` — the machine-readable, baseline-6 registered
claim-cell block (§13); the baseline-5 memo prose is not quoted anywhere here.
Numerator/denominator is given wherever the row carries both terms.

Column labels are the arm suffixes of §16.a/§16.b (`c1-g9` = `p18-crew-c1-gen9`,
and so on). A bold **(49)** / **(48)** marks the crew-block **fenced view** the
arm's instruments were computed over.

| instrument (registered cell) | corpus baseline (9p2i, baseline-6) | ea4bc955 | bfd145cb | 6d327dcb | 7f73929d **(49)** | fsm-comp | c1-g9 | c1-g0 **(49)** | c2-g9 **(48)** | c2-g0 |
|---|---|---|---|---|---|---|---|---|---|---|
| false-vouch `saw_player` rate — `false_vouch_saw_player_observations / vouch_observations_impostor` | 0.22819 (34/149) | 0.12621 (26/206) | 0.13825 (30/217) | 0.18779 (40/213) | 0.14078 (29/206) | 0.10204 (20/196) | 0.06250 (12/192) | 0.11413 (21/184) | 0.10448 (7/67) | **undef** (0/0) |
| false-vouch corroboration rate — `false_vouch_corroborations / corroboration_claims_impostor` | 0.28261 (13/46) | 0.22222 (12/54) | 0.18310 (13/71) | 0.42254 (30/71) | 0.33333 (20/60) | 0.11111 (6/54) | 0.14286 (7/49) | 0.28846 (15/52) | 0.33333 (7/21) | **undef** (0/0) |
| frame attempt rate — `frame_attempt_meetings / meetings_total` | 0.76710 (415/541) | 0.97419 (151/155) | 0.95625 (153/160) | 0.98148 (159/162) | 0.97041 (164/169) | 0.94268 (148/157) | 0.97315 (145/149) | 0.97973 (145/148) | 1.00000 (33/33) | **undef** (0/0) |
| frame conversion rate ‡ | 0.01205 (5/415) | — | — | — | — | — | — | — | — | — |
| teammate accusation rate ‡ | 0.00000 (0/455) | — | — | — | — | — | — | — | — | — |
| alibi survival rate ‡ | 0.78571 (11/14) | — | — | — | — | — | — | — | — | — |
| effective deflection rate ‡ | 0.23980 (47/196) | — | — | — | — | — | — | — | — | — |
| crew-witnessed kill rate — `crew_witnessed_kills / kills_total` | 0.03339 (20/599) † | 0.15228 (30/197) | 0.14778 (30/203) | 0.22280 (43/193) | 0.22000 (44/200) | 0.04598 (8/174) | 0.15306 (30/196) | 0.16500 (33/200) | 0.19481 (45/231) | 0.14343 (36/251) |
| witnessed point-biserial, within one hop | 0.27899 | 0.21108 | 0.20847 | 0.52142 | 0.35293 | 0.27505 | 0.23395 | 0.20536 | 0.28347 | 0.26509 |
| witnessed point-biserial, co-present | **no registered cell** (corpus sample: `null`) | 0.73122 | 0.77013 | 0.76781 | 0.77291 | **n/a** | 0.71486 | 0.83352 | 0.67307 | 0.65639 |
| co-present departure — mean co-present, witnessed / unwitnessed | **no registered cell** (corpus sample: 0.0 / 0.0) | 0.66667 / 0.00599 | 0.66667 / 0.00578 | 0.88372 / 0.02000 | 0.84091 / 0.01282 | 0.00000 / 0.00000 | 0.73333 / 0.00602 | 0.78788 / 0.00000 | 0.53333 / 0.00538 | 0.50000 / 0.00465 |
| action entropy — crew mean conditional ‡ | 0.91764 | — | — | — | — | — | — | — | — | — |
| action entropy — impostor mean conditional ‡ | 0.71262 | — | — | — | — | — | — | — | — | — |
| off-menu rate — `off_menu_total / impostor_decisions` | 0.00000 (0/7693) | 0.00000 (0/2015) | 0.00000 (0/2083) | 0.00000 (0/2100) | 0.00000 (0/2176) | 0.00000 (0/2299) | 0.00000 (0/2027) | 0.00000 (0/1962) | 0.00000 (0/2520) | 0.00000 (0/2596) |
| roll-call coverage mean (all) | **no corpus cell** — ratified floor **0.60** | 0.84320 | 0.84192 | 0.83549 | 0.84498 | 0.85872 | 0.83846 | 0.84485 | 0.86353 | **n/a** |
| roll-call coverage mean — crew | **no corpus cell** | 1.00000 | 0.98885 | 0.99383 | 0.99556 | 0.99735 | 0.99060 | 1.00000 | 1.00000 | **n/a** |
| roll-call coverage mean — impostor | **no corpus cell** | 0.40968 | 0.45625 | 0.41049 | 0.42899 | 0.43949 | 0.42953 | 0.43919 | 0.57576 | **n/a** |
| roll-call answer rate — `roll_call_answered_total / roll_call_asked_total` | **no corpus cell** | 0.85222 (767/900) | 0.85307 (778/912) | 0.84842 (806/950) | 0.85331 (826/968) | 0.86746 (805/928) | 0.85129 (727/854) | 0.85748 (728/849) | 0.86170 (162/188) | **undef** (0/0) |

**‡ — the six registered cells this table CANNOT fill from the rows, and why.**
The `instruments` block committed on each row is a **flattened** view: it keeps
the scalar and counter keys of each instrument report and **drops every
nested/dict-valued sub-object**. The dropped sub-objects are exactly where these
six cells live — `deception.frame_conversions` (frame conversion rate),
`deception.teammate_accusations` (teammate accusation rate),
`deception.alibi_fabrication` (alibi survival rate),
`deception.effective_deflection` (effective deflection rate), and
`kill_craft.entropy_by_side` (both action-entropy cells, per side). The same
flattening also dropped `kill_craft.co_present_histogram` and
`kill_craft.one_hop_histogram`. **No per-arm value is stated for any of them,
because none is available without recomputation** — they are recoverable only by
re-running the committed instruments
(`eval.deception_instruments.compute_deception_instruments`,
`eval.kill_craft.compute_kill_craft_report`) over each arm's recordings, which
this task did not do. The baseline column is filled because the corpus JSON
carries the nested blocks in full; the arm columns are honestly blank.

**† — the two corpus blocks in that file disagree on the witnessed kill rate, and
this table names it rather than picking one silently.** The registered
`baseline_cells_corpus_9p2i` cell is **20/599 = 0.03339**; the same file's
`sample_dir: replays/ml_corpus/9p2i` `kill_craft` block reads **12/505 =
0.02376**, and **12/505 is the cell §12 pre-registered and §16.e's rider ruling
uses**. The registered block's denominators are uniformly the larger ones (599
kills vs 505, 541 meetings vs 463, 176 impostor corroboration claims vs 46), so
the two are different corpus snapshots, not a transcription error. **The rider
ruling is unaffected by which one is used**: against 20/599 the learned arms run
**4.3×–6.7×** corpus instead of 6.2×–9.4×, the scripted comparator runs
**1.38×** instead of 1.93×, the ordering is identical, and the c1 gen-9-minus-gen-0
margin (a difference of two rates) does not move at all. Every other baseline
cell in the table above is the registered block's, per §13.

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
rate is far above corpus on every arm** (0.94–1.00 vs 0.76710) including the
all-scripted comparator, so it is a substrate property of this roster, not a
learned trait. (iii) **The false-vouch cells sit at or below corpus** on every
arm but `6d327dcb` (corroboration 0.42254 vs 0.28261) — the deception channel did
not run hot. (iv) **Roll-call coverage clears the ratified 0.60 floor on every
arm that held meetings** (0.8355–0.8635), with the same crew/impostor split
everywhere (~0.99 crew vs 0.41–0.58 impostor): impostors under-place themselves
uniformly, learned or scripted. (v) **The one large, uniform departure is the
kill-craft pair** — the witnessed rate (§16.e's rider) and, beside it, the
co-present cell: every **learned** arm places witnessed kills strongly co-present
(0.50–0.88) against a near-zero unwitnessed figure, while the **scripted**
comparator is 0.00000/0.00000 and the corpus sample 0.0/0.0. That is the same
learned-mover-versus-scripted-mover split the rider ruling turns on, showing up
on a second, independent kill-craft cell — consistent with §16.e's conclusion
that what is left is the impostor side and the physical layer. It is **an
observation on a pre-registered instrument, not a new pre-registered cell**, and
nothing in §17 rests on it.

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

### 17.1 Decisions taken during the operator run (recorded after the fact)

- **Seed 35 is EXCLUDED from `p18-imp-7f73929d`, and the Δ is taken on the
  49-seed intersection.** The seed returned rc 99 on **10 logged attempts** — 4
  in-leg passes ending in a `leg-abort`, then 6 `retry-stubborn.sh` rounds
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
  `c2-gen9` instrument cell in §16.b, §16.c and §16.e is the 48-game view, and is
  labelled as such where it is quoted.
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
     retryable, converged once in 14 attempts and never in 10;
  2. **LLM-free deterministic stalemate** (`c2-gen9` seeds 19, 20) — rc 0,
     **unretryable by construction**, reproduced byte-identically in ~80 s;
  3. **meeting-bearing robust stalemate** (`c1-gen0` seed 20) — rc 0,
     nondeterministic, **retryable in principle and hopeless in practice** at 8
     attempts.
  Classes 2 and 3 both exit `rc 0`, so the retry machinery never sees them as
  failures at all; both were caught by the scorer's `game_over` check, not by the
  runner. That is the operational lesson this campaign hands forward.
