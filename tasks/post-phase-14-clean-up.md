# Post-Phase-14 clean-up charter — the measured holes, and the Wave-0 tasks that close them

> **STATUS: ADOPTED (owner, 2026-07-05).** This is a CHARTER document, not a task doc — it is named
> outside the `tasks/phase-*.md` glob on purpose, so the validator/prompt tooling never parses it. The
> dispatchable contracts for every item below live in `tasks/phase-15.md` **Wave 0** (Tasks 15.1–15.7);
> this file is the evidence base those contracts cite and the target sheet the wave is measured against.
> Roadmap context: `tasks/post-phase-14-plan.md`.

## 1. Why a cleanup wave exists at all

The owner's direction is ML tactical play (Phase 15) → Voice & Judgment (Phase 16). Before recording
training data or training a policy, a first-principles measurement of the committed baseline-2 bytes
(2026-07-05; all 50 9p2i games re-seeded and replayed through the real engine, every recorded state hash
verified) established where the game actually loses its deduction signal. The verdict: **the simulation
is NOT information-poor — the meeting layer is information-LOSSY.** Fixing the two measured holes is
cheap, and doing it first protects both later programs:

- A learned impostor optimizes whatever the fitness landscape rewards. Today that landscape contains two
  known exploits — evidence that evaporates (vents) and a free-win vote channel (frame the reporter). A
  bake-off run before the fixes selects champions optimized against bugs already scheduled to die.
- The ML calibration corpus (~7h operator recording) and the ballot surrogate trained on it are
  snapshots of the meeting layer. Changing that layer afterwards invalidates both — the documented FO-6
  regression (surrogate top-1 64% → 26% after one re-record) is exactly this failure, already paid once.

## 2. The measurement (baseline-2 committed bytes, 9p2i, 50 games, 129 body-report meetings)

Reproduction: re-seed via `orchestrator.seeder.seed_initial_state`, replay recorded actions through
`engine.tick.advance_tick` + `orchestrator.game.apply_meeting_result`, verify every tick against the
recorded `state_hash` (the `api/replay_loader.py::_walk` recipe). Task 15.3 commits these folds to
`eval/` with the exact figures below as its reproduction gate; until it lands, the numbers are
charter-tier.

**Stage 1 — the information EXISTS.** A pooled-testimony oracle (perfect sharing of every living crew
member's legitimate same-room sightings, alibi-elimination at the kill tick):

| measure | value |
|---|---|
| killer-candidate set, median (of ~7–8 living) | **3** (mean 2.86) |
| with a ±1-tick kill window | mean **2.0**; unique killer in **45/129**; ≤2 in 85/129 |
| killer inside the set | 122/129 (7 misses are a same-tick move+kill frame artifact of the method) |
| crew alone-time / sighting volume | alone only 34% of living ticks; ~23 sighting-frames per crew per game |
| body-discovery delay | 66% of reported kills found within 3 ticks (the kill window is knowable) |

**Stage 2 — individuals HOLD hard clues.** In **94/129** report meetings (73%) at least one living crew
member holds hard evidence: an impostor vent witnessed (**74/129** — vents are impostor-only, i.e.
role-proving), victim-last-seen-with-the-killer (37), killer placed at the scene (32), the kill itself
witnessed (6).

**Stage 3 — the funnel LOSES it before the vote:**

| leak | value |
|---|---|
| meetings where a crew-witnessed impostor vent is even MENTIONED in any turn | **36/74** |
| structured observation types in `meetings/schemas.py` | `SawPlayer`, `CompletedTask`, `FoundBody` — **no vent type exists**; vent evidence is free-text-only, invisible to the contradiction detector and the ballot reason-id linkage |
| clue-holding meetings where the killer even gets accused | 56/94 |
| ejections landing OUTSIDE the pooled-knowledge candidate set, when that set was ≤3 | **42/73 (58%)** |
| ejections that removed the meeting's own REPORTER | **22/106 — all 22 innocent** (~40% of all crew mis-ejects; impostors essentially never self-report in this corpus) |

Conclusion: at current play quality the binding constraint is **aggregation, not generation**. New
physical information channels (cameras, logs) are deferred until the funnel keeps what it is given
(`post-phase-14-plan.md` §5).

## 3. The holes → the Wave-0 tasks (contracts in `tasks/phase-15.md`)

| # | hole (measured) | fix | task | measured target at baseline 3 |
|---|---|---|---|---|
| H1 | No committed measurement harness: `scripts/validity_gate.py` / `measure_baseline.py` are audit-prose citations, no CLI exists in `eval/` | Wire the existing folds into the two audit-cited CLIs | **15.1** | Reproduces every baseline-2 close number from committed bytes, exactly |
| H2 | Watchability referee is lab-tier, baseline-1-anchored; no evidence-supply floors | Promote the D1–D4 geomean + add supply floors to committed `eval/` | **15.2** | Parity with the lab scorer on baseline-2 facts; floors pinned per-baseline |
| H3 | The funnel numbers above have no committed reproduction | Promote the oracle/possession/transmission folds into `eval/` | **15.3** | Reproduces §2's figures from committed bytes before baseline 3 is recorded |
| H4 | Witnessed vents unspeakable (36/74 transmission; no schema type) | `SawVentObservation` + turn validation + hard contradiction flag + ballot citability + v5 prompt elicitation | **15.4** | Share of witnessed-vent meetings carrying a STRUCTURED vent observation: 0% → measured (directional target: a strong majority); vent-flagged ejection accuracy reported |
| H5 | Reporter ejected 22/106, all innocent (proximity-at-discovery read as guilt) | Reporter-exculpation belief/render lever, default-OFF, offline-proved | **15.5** | Innocent-reporter ejections per 106: 22 → measured (directional target: near zero) without suppressing genuine catches (conversion canary held) |
| H6 | Known latent hazards + dead weight: raw-vs-rendered 0.60-gate band disagreement; belief-delta boundary sums pass by IEEE luck; dead `StrategicReasoner` island (~2.7 KLoC); 0.60 constant homed inside `meetings/manager.py` (imported by `agents/`); only one import-linter contract; stale AGENTS.md provider/tooling doctrine | Substrate hygiene: fix the band, pin boundary sums, delete the island, re-home the constant, add two firewall contracts, de-stale AGENTS.md | **15.6** | All hazards closed with pinning tests; `agents ↛ meetings.manager` + `observation ↛ agents/meetings/llm` contracts KEPT |
| H7 | Every fix above is unmeasured until recorded | Baseline 3: one atomic re-record of both canonical sets, funnel metrics before/after, levers graduated | **15.7** | Validity gate PASS; §2's funnel table re-measured and reported as the wave's close finding |

Targets follow the repo doctrine: directional, measured, closed as findings — model behavior is not
guaranteed, but every lever must demonstrably move its own channel without firing the over-damping
canaries (genuine-class conversion, R1 collapse) that Phase 14 established.

## 4. Explicitly deferred (do not scope-creep this wave)

- **Ballot-whereabouts / roll-call elicitation** (the pooling mechanism the Stage-1 oracle motivates) —
  Phase 16, where the citation gate gives it teeth. Wave 0 makes evidence *speakable*; Phase 16 makes
  sharing *systematic*.
- **New physical channels** (cameras/door logs, task-visual soft alibis, sabotage retune) — after the
  funnel demonstrably keeps what it is given.
- **DESIGN.md prose refresh** — owner-side (the prompt generator bars dispatched agents from DESIGN.md).
- **`api/replay_loader.py` decomposition, second map** — standalone hygiene, not blocking.
