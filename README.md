# AiLibi

> An Among-Us-style social-deduction simulator being built almost entirely by AI coding agents under a strict review protocol — and a working example of how to keep architecture coherent across many agent-authored pull requests.

---

## What this is

AiLibi is two things at once.

**A deterministic multi-agent reasoning testbed.** Players (agents) roam a room graph, complete their own tasks, witness events, and meet to deliberate over a reactive accusation chain. One or more impostors are hidden among them (the default game is 4 players / 1 impostor; a 9-player / 2-impostor preset also ships). The product is a research environment for studying agent reasoning under hidden information — not a game with AI players bolted on. See [DESIGN.md](DESIGN.md) for the full system architecture.

**An experiment in agentic software workflow.** Every coding PR was opened by an AI coding agent against a task contract authored by a human. Architecture is enforced by tooling — import-linter, `mypy --strict`, a recursive observation leak test, byte-identical replay determinism. The contracts in `tasks/phase-N.md` are the only spec each agent sees. So far: 219 merged PRs across phases 0–14, ~2,500 passing tests, zero observation-firewall violations. Phases 0–5 delivered the MVP; the phases after that pushed agent-reasoning quality and migrated the eval model.

---

## How this is being built

The workflow is the experiment. Every coding task follows the same loop:

1. **Author a task contract** in `tasks/phase-N.md` — branch, dependencies, files in/out of scope, definition of done, implementation hint.
2. **Generate a paste-ready prompt** with `uv run python scripts/generate_prompts.py`. The generator validates that every prompt mirrors its contract byte-for-byte and that parallel tasks don't share file scope.
3. **Dispatch an agent** (Claude Code, web or CLI) against the prompt. The agent works in a fresh checkout, runs `bash scripts/check.sh` until green, and opens a PR against [.github/pull_request_template.md](.github/pull_request_template.md).
4. **Review the PR.** CI gates catch the easy stuff (lint, types, firewall, determinism); the human catches the rest.
5. **Checkpoint periodically.** Before high-blast-radius work, a read-only checkpoint re-verifies prior findings and surfaces drift CI can't catch.

Two representative artifacts to skim:

- A task contract — [tasks/phase-3.md](tasks/phase-3.md) Task 3.19 (robust JSON extraction + failure recording) shows the ~300-line full-contract shape.
- Its auto-generated prompt — [agent_prompts/task-3-19-robust-json-extraction-and-failure-recording.md](agent_prompts/task-3-19-robust-json-extraction-and-failure-recording.md).

---

## Three load-bearing decisions

These are the architectural invariants every contributor (human or agent) must respect. They are recorded verbatim in [ADR-0001](docs/adr/0001-three-load-bearing-decisions.md).

**1. Tick-based deterministic engine with a strict observation firewall.** The engine advances world state as a pure, deterministic tick function — the same seed and inputs always produce bit-exact replays (no wall-clock, no unseeded randomness, no global state), verified by property tests and scripted-game determinism tests. Agents never touch engine state: `agents/` cannot import `engine/`, directly or transitively (import-linter enforced, tested with direct- and transitive-leak fixtures). Agents see only `ObservationPacket` and `PublicMapView` and emit only `ActionIntent`; the leak test walks every emitted packet recursively and rejects any hidden field (role, killer identity, kill attribution). The firewall is scoped to the *agent* surface — the spectator surfaces (replay viewer, eval dashboard) are privileged by design and intentionally expose role + kill attribution.

**2. Two-tier agent reasoning.** Tactical decisions (move, do task, follow, vent) are rule-based and run every tick. Strategic decisions (meeting reports, voting, suspicion updates) use an LLM (added in Phase 3) and run only at meetings or specific triggers (witnessing a kill, finding a body). Without this split, cost and latency make the system unviable.

**3. Memory is structured first.** Each agent reasons from a typed event log and a derived belief state (suspicion, trust, alibi). The LLM sees a *rendered view* of that structure during meetings — never raw engine state.

---

## Project status

MVP (phases 0–5) is complete. Everything since has pushed agent-reasoning quality on the same substrate. Phases 0–16 are merged and closed (Phase 16 — Voice & Judgment — closed 2026-07-14 on baseline 5); Phase 17 (co-adaptation, [tasks/phase-17.md](tasks/phase-17.md)) is open and dispatching.

| Phase | Description |
| --- | --- |
| 0 | Scaffolding, CI, firewall lint, ADR |
| 1 | Engine: state, rules, RNG, visibility, replay, leak test |
| 2 | Tactical agents: memory, perception, A*, FSMs, headless orchestrator + tournament harness |
| 3 | LLM-driven meetings, voting, contradiction detection |
| 4 | Spectator UI (FastAPI + React + PixiJS), replay-only |
| 5 | Eval metrics + tournament dashboard + prompt-regression close gate — **MVP complete** |
| 6 | Post-MVP repair & hardening |
| 7 | Agent intelligence: impostor coordination + local-Ollama eval pivot |
| 8 | Deduction-substrate restructure |
| 9 | Producer hygiene + conversion quality |
| 10 | Conviction-engine repair + crew evidence economy + impostor gameplay |
| 11 | Impostor information economy (vents, sabotage, then balance) |
| 12 | Front-end rework (spectator replay viewer, "Playful" cream/ink design) |
| 13 | Pre-ML grounding fixes: rubric repair + deduction rework |
| 13.5 | Memory-substrate correctness (truth-up → substrate) |
| 14 | Featherless AI integration: hosted-provider + model/prompt migration |

The post-Phase-14 roadmap is laid out in [tasks/post-phase-14-plan.md](tasks/post-phase-14-plan.md): Phase 15 ([tasks/phase-15.md](tasks/phase-15.md)) runs an evidence-substrate cleanup wave (charter: [tasks/post-phase-14-clean-up.md](tasks/post-phase-14-clean-up.md)) closing on baseline 3, then the machine-learned tactical-policy program — measurement harness, training environment, calibration corpus, rebuilt meeting surrogate, and a multi-method training bake-off — with a mid-phase pause that picks the winning method on measured numbers before a productization wave is authored. Phase 15 closed 2026-07-11 (branch A: the learned impostor champion ships opt-in; baseline 3 canonical). Phase 16 ([tasks/phase-16.md](tasks/phase-16.md)) closed 2026-07-14 on baseline 5: Voice & Judgment — citation-gated ballots (graduated ON with the hard-evidence gate and observation-id rendering; citation compliance 1.000 at close), information pooling (roll-call/vouching shipped; the absence prior stays OFF as a recorded slate ruling pending roll-call calibration), personas — all on the probe-locked `Qwen/Qwen3.6-27B` (baseline 4 was the model-only swap). Co-adaptation retraining (Phase 17) and presentation (Phase 18) follow.

---

## Reproduce a game

The single strongest demonstration of the determinism claim is that anyone can run the same seed twice and get byte-identical replays.

```bash
bash scripts/setup_env.sh

uv run python scripts/run_game.py --seed 42 --replay-path /tmp/r1.jsonl
uv run python scripts/run_game.py --seed 42 --replay-path /tmp/r2.jsonl

diff -q /tmp/r1.jsonl /tmp/r2.jsonl   # files are identical
```

The replay JSONL records per-tick actions and a SHA-256 hash of the full engine state. Identical seed + identical agent factory always produces identical bytes — that property is also how CI proves the engine is pure: `eval/determinism_test.py` runs every scripted fixture twice and compares the entire JSONL output.

---

## Watch a replay

The spectator UI reads saved replay JSONL files and renders the game tick by tick — map, agents moving room to room, meeting transcripts, contradiction flags, per-agent memory snapshots, and a suspicion heatmap.

```bash
bash scripts/run_spectator.sh
```

That starts the API + frontend, waits until both are healthy, and opens `http://localhost:5173` in your browser. Ctrl-C stops both. (One-time prerequisite: `bash scripts/setup_env.sh`. macOS + Linux only.)

A fresh clone ships with 100 sample replays under `replays/samples/` — two full 50-game tournaments, one per roster preset (`4p1i/` and `9p2i/`), regenerated 2026-07-14 against the Featherless provider (`Qwen/Qwen3.6-27B` — the Task-16.2 locked model, non-thinking — on the `qwen3_6_27b` `v3` prompt set: the Phase-16 "baseline 5" close substrate, the Voice & Judgment layer — citation-gated ballots, observation-id rendering, the hard-evidence render gate, the elicitation batch, and the persona voice layer — as the only layer change from baseline 4, model held constant). Each set's `MANIFEST.md` is the canonical provenance record; the recorded impostor win rates are 30% (4p1i) and 36% (9p2i). Once the UI is up, pick a roster set and any replay to scrub through ticks, click meeting markers to read transcripts with ballots and contradiction flags, and select an agent to see their memory snapshot and the suspicion heatmap at that moment. Any replays you generate locally into `replays/` (e.g. via `scripts/run_game.py`) override the bundled samples; the API logs which directory it picked at startup.

Those samples are managed by a refresh workflow. `scripts/refresh_samples.sh` regenerates them against the active provider — `--full` (all 50 seeds), `--meetings` (only the meeting-bearing seeds), or `--seeds N,N,N` (a subset) — recording each sample's prompt-template versions, model, spend, and outcome in the set's `MANIFEST.md` so metrics can be attributed to a specific prompt version + model snapshot. Its free, API-free counterpart `scripts/verify_samples.sh` replays every sample through the engine and fails loud if any recorded state-hash no longer reconstructs, catching determinism drift before a metric reads a stale sample.

The UI is intentionally minimal — function over polish. Alongside the per-game replay viewer, a **Tournament Dashboard** tab renders the aggregate eval report for a whole tournament run (see "Run a tournament" below). The spectator API exposes sanitized DTOs (`api/schemas.py`) covering everything visible: agent positions per tick, meeting transcripts with ballots and contradiction flags, per-agent memory snapshots at meeting boundaries, and the full LLM call log with prompts, responses, and cost.

---

## Run a tournament & read the metrics

Phase 5 turns the engine into an eval harness. One command runs N games, saves each game's replay, and writes the aggregate eval report — all into one directory:

```bash
uv run python scripts/run_tournament.py --num-games 50 --output-dir replays --roster-preset 4p1i
```

This writes per-seed `replay-seed-*.jsonl` files plus a `tournament-eval-report.json` to `--output-dir`. `--roster-preset {4p1i,9p2i}` selects a named roster (or pass `--num-players` / `--num-impostors` explicitly). With the default fake provider it costs $0 and runs offline (useful for the CI loop); set a real provider (below) for metric values that reflect real model behavior.

### Providers

The provider is selected by `AILIBI_LLM_PROVIDER`:

- **`fake`** (default) — deterministic, offline, $0. Powers the CI loop.
- **`anthropic`** — the real Anthropic provider (requires `ANTHROPIC_API_KEY`).
- **`ollama`** — a local open model (`qwen3.5:9b`), free, served from your own machine.
- **`featherless`** — hosted Featherless AI (`Qwen/Qwen3.6-27B`), OpenAI-compatible, on a flat-rate subscription (recorded as $0; requires `FEATHERLESS_API_KEY`). This is the **canonical eval provider** as of Phase 14 (model locked 2026-07-12, Task 16.2 — audits/audit-phase-16-model-lock.md).

Both open-model providers disable "thinking" per request and fail loud if a response still carries thinking content. CI never selects a real provider and never reaches the network; the live integration tests are opt-in.

```bash
# Example: local Ollama
ollama pull qwen3.5:9b
ollama serve                          # serves http://localhost:11434
export AILIBI_LLM_PROVIDER=ollama
uv run python scripts/run_tournament.py --num-games 50 --output-dir replays

# Example: hosted Featherless
export AILIBI_LLM_PROVIDER=featherless FEATHERLESS_API_KEY=...
uv run python scripts/run_tournament.py --num-games 50 --output-dir replays
```

Per-call model ids default to the active provider's model and can be overridden with `AILIBI_LLM_MEETING_MODEL` / `AILIBI_LLM_TRIGGER_MODEL`.

The report is consumed by pure analyzers in `eval/` — each reads the typed `TournamentReport`, never raw JSONL:

- **vote correctness** — were ejections evidence-backed, or coin-flips? (guards against circular "they were the impostor so the vote was right" scoring).
- **accusation calibration** — does stated confidence match how often an accusation is correct? (reliability curve + ECE).
- **alibi fabrication** — how often does an impostor's alibi claim survive scrutiny.
- **cost dashboard** — total/mean spend, a per-model roll-up, and a per-prompt-version cost breakdown so a prompt change's cost impact is legible alongside its quality impact.

The **Tournament Dashboard** tab in the spectator UI renders this report (served via `GET /eval/tournament-report`).

### The close gate: prompt change → measurable metric delta

The acceptance gate is a deterministic regression loop, not a live eval: change a prompt template and a metric must move, attributably. `tests/eval/test_prompt_regression.py` demonstrates it from frozen recorded fixtures (no model, no network) — bumping the impostor-report template moves the alibi-fabrication survival rate, attributed to that specific `(template_name, version)` via per-version provenance. Because it runs on committed fixtures, the whole prompt-iteration loop is reproducible in CI.

---

## Setup

```bash
# install
bash scripts/setup_env.sh

# full local gate: ruff check, ruff format --check, lint-imports, validate_task_docs,
# generate_prompts --check, mypy (strict, via config), pytest, + frontend tsc + build
bash scripts/check.sh

# run a single deterministic game
uv run python scripts/run_game.py --seed 0 --replay-path /tmp/replay.jsonl

# run a tournament: replays + aggregate eval report into one dir
uv run python scripts/run_tournament.py --num-games 50 --output-dir replays
```

Python 3.11 only. The [`uv`](https://docs.astral.sh/uv/) package manager is required.

---

## Architecture notes

- `engine/` — pure simulation. No LLM, no I/O, no globals. Owns hidden state.
- `observation/` — the firewall. Builds `ObservationPacket` and `PublicMapView` from engine state, strips every hidden field, audits every packet to disk.
- `agents/` — tactical (deterministic FSMs) and strategic (LLM-driven meeting reasoning) policies. No engine imports.
- `meetings/` — the meeting protocol: an opening turn → a reactive accusation chain → opt-in info-share → voting, with contradiction detection. No engine imports.
- `llm/` — provider-neutral `LLMClient` Protocol; Anthropic, local-Ollama, and Featherless adapters; budget enforcement; a fake deterministic provider for CI.
- `orchestrator/` — wires everything: seeds initial state, dispatches agents, translates `ActionIntent` → engine `Action`, runs meetings, records replay JSONL.
- `eval/` — the eval harness: the typed tournament report schema, the metric analyzers (vote correctness, accusation calibration, alibi fabrication, cost dashboard, and more), the JSONL→`TournamentReport` loader (roles taken from authoritative final engine state, never the replay), the tournament runner, the determinism + leak tests, and the prompt-regression close gate.
- `api/` — FastAPI app + sanitized DTO inventory + replay loader + the tournament eval report endpoint. The spectator surface; intentionally privileged.
- `frontend/` — React + Vite + Tailwind + PixiJS spectator UI (the Phase 12 "Playful" cream/ink rework): MapView, MeetingView, MindInspector, BeliefMatrix, ThoughtStream, ReplayControls, TournamentDashboard, and more. Consumes the API DTOs; never imports Python.
- `tasks/` — the project's spec, decomposed into task contracts.
- `agent_prompts/` — paste-ready prompts auto-generated from the task contracts.

Full architecture: [DESIGN.md](DESIGN.md). Workflow protocol: [AGENTS.md](AGENTS.md). Build plan: [AGENT_IMPLEMENTATION.md](AGENT_IMPLEMENTATION.md).
