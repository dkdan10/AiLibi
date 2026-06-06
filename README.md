# AiLibi

> An Among-Us-style social-deduction simulator being built almost entirely by AI coding agents under a strict review protocol — and a working example of how to keep architecture coherent across many agent-authored pull requests.

---

## What this is

AiLibi is two things at once.

**A deterministic multi-agent reasoning testbed.** Players (agents) roam a room graph, complete their own tasks, witness events, and meet to deliberate over a reactive accusation chain. Two impostors are hidden among them. The product is a research environment for studying agent reasoning under hidden information — not a game with AI players bolted on. See [DESIGN.md](DESIGN.md) for the full system architecture.

**An experiment in agentic software workflow.** Every coding PR was opened by an AI coding agent against a task contract authored by a human. Architecture is enforced by tooling — import-linter, `mypy --strict`, a recursive observation leak test, byte-identical replay determinism. The contracts in `tasks/phase-N.md` are the only spec each agent sees. So far: 82 merged PRs across phases 0–5 (MVP complete), 980 passing tests, 29 read-only audits in `audits/` (including a 50-game real-provider tournament eval), zero observation-firewall violations.

---

## How this is being built

The workflow is the experiment. Every coding task follows the same five-step loop:

1. **Author a task contract** in `tasks/phase-N.md` — branch, dependencies, files in/out of scope, definition of done, implementation hint.
2. **Generate a paste-ready prompt** with `uv run python scripts/generate_prompts.py`. The generator validates that every prompt mirrors its contract byte-for-byte and that parallel tasks don't share file scope.
3. **Dispatch an agent** (Claude Code, web or CLI, Codex) against the prompt. The agent works in a fresh checkout, runs `bash scripts/check.sh` until green, and opens a PR populated against [.github/pull_request_template.md](.github/pull_request_template.md).
4. **Review the PR.** CI gates catch the easy stuff (lint, types, firewall, determinism); the human catches the rest.
5. **Audit every N tasks.** A read-only audit (`audits/audit-YYYY-MM-DD-HHMM.md`) re-verifies every prior Pass finding hasn't regressed and surfaces drift CI can't catch. The repo currently audits before each high-blast-radius integration task.

Representative artifacts to skim:

- A task contract — [tasks/phase-3.md](tasks/phase-3.md) Task 3.19 (robust JSON extraction + failure recording) shows the ~250-line full-contract shape that emerged once tasks started spawning audit-driven repair work.
- An auto-generated prompt — [agent_prompts/task-3-19-robust-json-extraction-and-failure-recording.md](agent_prompts/task-3-19-robust-json-extraction-and-failure-recording.md).
- A reconciled multi-tool audit — [audits/audit-2026-05-26-2316-mid-phase-4-dto-reconciled.md](audits/audit-2026-05-26-2316-mid-phase-4-dto-reconciled.md) — Phase 4 mid-phase DTO leak audit, adjudicating two parallel auditors' reports.
- The iterative real-provider eval loop — six reports under `audits/audit-2026-05-25-*pre-phase-4-real-provider-eval.md` plus the closing [audit-2026-05-26-0325-pre-phase-4-real-provider-eval.md](audits/audit-2026-05-26-0325-pre-phase-4-real-provider-eval.md).

---

## Three load-bearing decisions

These are the architectural invariants every contributor (human or agent) must respect. They are documented as ADR-0001 and re-checked on every audit.

**1. Tick-based deterministic engine.** The engine is a pure function `(WorldState, list[Action]) -> (WorldState, list[Event])` at a fixed tick rate. Replays are bit-exact from a seed. No wall-clock, no unseeded randomness, no global state — verified by property tests and three scripted-game determinism tests.

**2. Strict observation firewall, agent-scoped.** `agents/` cannot import from `engine/`, directly or transitively. The boundary is import-linter enforced and tested with both direct-leak and transitive-leak fixtures. Agents see only `ObservationPacket` and `PublicMapView`; they emit only `ActionIntent`. The leak test walks every emitted packet recursively and rejects any hidden field (role, killer identity, kill attribution). The firewall is scoped to the *agent* surface; the spectator surfaces (replay viewer, eval dashboard) are privileged by design and intentionally expose role + kill attribution. The Phase 4 mid-phase DTO audit existed specifically to verify this scope decision held — every spectator-visible field is intentional, not accidental.

**3. Structured memory first.** Agents reason from a typed event log and a derived belief state (suspicion, trust, alibi). The LLM (added in Phase 3) sees a *rendered view* of that structure during meetings — never raw engine state.

---

## Project status

| Phase | Description | Status |
| --- | --- | --- |
| 0 | Scaffolding, CI, firewall lint, ADR | merged |
| 1 | Engine: state, rules, RNG, visibility, replay, leak test | merged |
| 2 | Tactical agents: boundary, memory, perception, A*, FSMs, headless orchestrator + tournament harness | merged |
| 3 | LLM-driven meetings, voting, contradiction detection | merged — closed with a 50-game real-provider eval (38% impostor win rate, $0.018 mean cost/game) |
| 4 | Spectator UI (FastAPI + React + PixiJS) | merged — replay-only MVP; 17 task contracts including two audit-derived substrate fixes (and two Phase-5 prelude tasks) |
| 5 | Eval metrics + tournament dashboard + prompt-regression close gate + perf pass | merged — **MVP complete** |
| 6 | Human player seat | post-MVP |

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

A fresh clone ships with 50 sample replays under `replays/samples/` — a full 50-game real-provider tournament regenerated 2026-05-27, tallying a 36% impostor win rate (18/50) and ~$0.91 total spend per `replays/samples/MANIFEST.md`, the canonical provenance record. Once the UI is up, pick any replay to scrub through ticks, click meeting markers to read transcripts with ballots and contradiction flags, and select an agent to see their memory snapshot and the suspicion heatmap at that moment. Any replays you generate locally into `replays/` (e.g. via `scripts/run_game.py`) override the bundled samples; the API logs which directory it picked at startup.

Those samples are managed by a refresh workflow. `scripts/refresh_samples.sh` regenerates them against the real provider — `--full` (all 50 seeds), `--meetings` (only the meeting-bearing seeds), or `--seeds N,N,N` (a subset) — recording each sample's prompt-template versions, model, spend, and outcome in `replays/samples/MANIFEST.md` so Phase 5 metrics can be attributed to a specific prompt version + model snapshot. Its free, API-free counterpart `scripts/verify_samples.sh` replays every sample through the engine and fails loud if any recorded state-hash no longer reconstructs, catching determinism drift before a metric reads a stale sample — e.g. `bash scripts/verify_samples.sh` checks all 50 in seconds.

The UI is intentionally minimal — function over polish. Alongside the per-game replay viewer, a **Tournament Dashboard** tab renders the aggregate eval report for a whole tournament run (see "Run a tournament" below). The spectator API exposes sanitized DTOs (`api/schemas.py`) covering everything visible: agent positions per tick, meeting transcripts with ballots and contradiction flags, per-agent memory snapshots at meeting boundaries, and the full LLM call log with prompts, responses, and cost.

---

## Run a tournament & read the metrics

Phase 5 turns the engine into an eval harness. One command runs N games, saves each game's replay, and writes the aggregate eval report — all into one directory:

```bash
uv run python scripts/run_tournament.py --num-games 50 --output-dir replays
```

This writes per-seed `replay-seed-*.jsonl` files plus a `tournament-eval-report.json` to `--output-dir`. With the default fake provider it costs $0 and runs offline (useful for the CI loop); set `AILIBI_LLM_PROVIDER=anthropic` (and a key) for metric values that reflect real model behavior.

### Run with a local LLM (Ollama)

Phase 7 adds a third provider: a **local Ollama** open model — `qwen2.5:7b-instruct`, free, served from your own machine — which is the canonical provider for the meeting-heavy Phase 7 eval set (a hosted frontier model is costly at that volume and brittle on the strict report schemas). Set it up once, then point AiLibi at it:

```bash
# 1. Install Ollama: https://ollama.com/download
# 2. Pull the canonical model and start the server:
ollama pull qwen2.5:7b-instruct
ollama serve                          # serves http://localhost:11434

# 3. In another shell, select the provider and run:
export AILIBI_LLM_PROVIDER=ollama
uv run python scripts/run_tournament.py --num-games 50 --output-dir replays
```

`AILIBI_OLLAMA_HOST` overrides the server address (default `localhost:11434`); the model knobs (`AILIBI_LLM_MEETING_MODEL` / `AILIBI_LLM_TRIGGER_MODEL`) both default to `qwen2.5:7b-instruct`. Every Ollama completion reports `cost_usd == 0.0`, so the per-game USD budget cap is moot and the token ceiling is the operative backstop. CI never selects Ollama and never reaches the server — the live integration tests are opt-in behind `AILIBI_RUN_OLLAMA_TESTS=1`.

The report is consumed by four pure analyzers in `eval/` — each reads the typed `TournamentReport`, never raw JSONL:

- **vote correctness** — were ejections evidence-backed, or coin-flips? (guards against circular "they were the impostor so the vote was right" scoring).
- **accusation calibration** — does stated confidence match how often an accusation is correct? (reliability curve + ECE).
- **alibi fabrication** — how often does an impostor's alibi claim survive scrutiny.
- **cost dashboard** — total/mean spend, a per-model roll-up, and a per-prompt-version cost breakdown so a prompt change's cost impact is legible alongside its quality impact.

The **Tournament Dashboard** tab in the spectator UI renders this report (served via `GET /eval/tournament-report`).

### The close gate: prompt change → measurable metric delta

The acceptance gate for Phase 5 is a deterministic regression loop, not a live eval: change a prompt template and a metric must move, attributably. `tests/eval/test_prompt_regression.py` demonstrates it from frozen recorded fixtures (no model, no network) — bumping the impostor-report template v1→v2 moves the alibi-fabrication survival rate 1.0 → 0.8, attributed to that specific `(template_name, version)` via per-version provenance. Because it runs on committed fixtures, the whole prompt-iteration loop is reproducible in CI.

---

## Audits

The `audits/` folder is a public artifact. Each audit is a read-only checkpoint that:

- runs the full check gate from scratch,
- re-verifies every prior Pass finding hasn't regressed (`git diff` against the prior audit's HEAD),
- traces each new finding to a file path and line range,
- decides Ready / Ready-with-fixes / Not-ready for the next high-blast-radius task.

The audit pipeline grew across phases:

- **Phase 2** (single-tool, post-checkpoint): [audits/audit-2026-05-09-1901.md](audits/audit-2026-05-09-1901.md) baseline and [audits/audit-2026-05-10-0721.md](audits/audit-2026-05-10-0721.md) post-Task-2.7. The latter produced the one-PR "audit repair" pattern that's been used ever since (Task 2.7.5, 2.8.5, etc.).
- **Phase 3** (two-tool with reconciliation): a pre-phase audit + reconciliation produced the [audit-2026-05-25-0414-reconciled.md](audits/audit-2026-05-25-0414-reconciled.md) verdict. Closing the phase took seven iterative real-provider evals against the live Anthropic provider, each surfacing exactly one defect class — culminating in [audit-2026-05-26-0325-pre-phase-4-real-provider-eval.md](audits/audit-2026-05-26-0325-pre-phase-4-real-provider-eval.md) (50/50 games clean).
- **Phase 4** (two-tool with reconciliation, mid-phase): [audit-2026-05-26-2316-mid-phase-4-dto-reconciled.md](audits/audit-2026-05-26-2316-mid-phase-4-dto-reconciled.md) ran after the foundation tasks landed but before the five UI components fanned out. Both source audits passed; informational findings produced two substrate-fix tasks (4.7, 4.9) that landed before the components, preventing five PRs from baking in the same gaps.
- **Phase 5** (two-tool with reconciliation, mid-phase): [audit-2026-05-29-1338-mid-phase-5-metric-reconciled.md](audits/audit-2026-05-29-1338-mid-phase-5-metric-reconciled.md) introduced a defect class CI cannot reach — *metric correctness*: does each analyzer compute what its docstring claims? Both auditors built independent known-answer fixtures for all four metrics; the verdict passed (0 blocking, 1 informational docstring qualification) and cleared the dashboard + close-gate fan-out.

Findings that didn't catch in CI but *did* catch in audit: scope drift (a task quietly modified a file outside its declared scope), a tactical policy that would crash on a disconnected map, an enum coupling between the engine and perception that no test was enforcing, a `BeliefEntryView.last_updated_tick` field that was honest-by-accident but would have misled the suspicion-heatmap component if not renamed, an `LLMCallRecord` that didn't carry the agent id needed by the per-agent memory viewer.

---

## Lessons from building this

A handful of things that didn't work, and what changed:

- **Scope drift is the most common defect.** Task 2.4 was declared in-scope for `agents/perception.py` only, but the agent also wired perception into `agents/runtime.py` (correct behaviour, missing from scope). CI was green; the audit caught it. The fix is to either update the contract or revert the wiring — both options have a clear paper trail. Lesson: file-scope discipline is more brittle than test discipline; audit for it explicitly.
- **CI proves correctness, not completeness.** All five low-severity findings from the post-2.7 audit passed CI cleanly. The crewmate FSM would have crashed on the first disconnected map; no test forced one to exist. The audit asked "what could break that no test would catch?" — and the answer was a non-trivial list.
- **Real-provider evals surface one defect class at a time.** Phase 3 closed only on the seventh iteration of the 50-game tournament; the first six each crashed on a different live-provider quirk that the fake-provider tests couldn't reproduce (missing transport wiring, leading backtick fences, truncation under tight `max_tokens`, prose preambles before fenced JSON, subject-field placeholder leakage). Each defect spawned exactly one focused repair task. Trying to fix-them-all-at-once before any eval would have been guessing; iterating against the live provider made each fix evidence-driven. The fake provider stayed essential for the CI loop — but it couldn't substitute for the live one as the acceptance gate.
- **Mid-phase audits catch substrate gaps before fan-out.** Phase 4 had a vertical-slice + mid-phase-audit + fan-out structure: build one component end-to-end (MapView vertical slice), audit the DTO + store + leak surface, *then* fan out the remaining four components. The audit produced two substrate-fix tasks (`BeliefEntryView.snapshot_tick` rename, `LLMCallRecord.agent_id` propagation) that landed before the five-component fan-out. Without the audit, those gaps would have been re-implemented in five PRs.
- **Two-tool audits with separate reconciliation are more robust than single-tool.** Phase 3 and 4 ran each audit twice — once with Codex, once with Claude — then handed both reports to a separate reconciler. Disagreements between the two auditors surfaced as the most interesting findings; agreement made the verdict load-bearing. Single-tool audits are still fine for low-blast-radius checkpoints; the reconciliation step is worth the cost at phase boundaries.
- **iOS Claude Code's sandbox is more restrictive than macOS or web.** A native iOS session couldn't create PRs at all because `gh` wasn't installed and no MCP server was loaded. The fix turned out to be running Claude Code in iOS Safari (the web variant) instead of the native app — same Claude, more tools.
- **Half-step task IDs are useful.** Initially banned in Phase 2+ for cleanliness, but audit-repair tasks really do belong between two sequential tasks (Task 2.7.5 sits between 2.7 and 2.8). The policy now allows a single `.N.5`-style suffix exclusively for hygiene work.

---

## Setup

```bash
# install
bash scripts/setup_env.sh

# full local gate: ruff, ruff format, lint-imports, validate_task_docs,
# generate_prompts --check, mypy, pytest
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
- `llm/` — provider-neutral `LLMClient` Protocol, Anthropic adapter, budget enforcement, fake deterministic provider for CI.
- `orchestrator/` — wires everything: seeds initial state, dispatches agents, translates `ActionIntent` → engine `Action`, runs meetings, records replay JSONL.
- `eval/` — the eval harness: the typed tournament report schema, four pure metric analyzers (vote correctness, accusation calibration, alibi fabrication, cost dashboard), the JSONL→`TournamentReport` loader (roles taken from authoritative final engine state, never the replay), the tournament runner, the determinism + leak tests, and the prompt-regression close gate.
- `api/` — FastAPI app + sanitized DTO inventory + replay loader + the tournament eval report endpoint. The spectator surface; intentionally privileged.
- `frontend/` — React + Vite + Tailwind + PixiJS spectator UI (MapView, MeetingView, ThoughtStream, BeliefMatrix, ReplayControls, TournamentDashboard). Consumes the API DTOs; never imports Python.
- `tasks/` — the project's spec, decomposed into task contracts.
- `agent_prompts/` — paste-ready prompts auto-generated from the task contracts.
- `audits/` — read-only checkpoint reports + reusable audit prompts (single-tool, two-tool, real-provider eval, mid-phase DTO, mid-phase metric correctness).

Full architecture: [DESIGN.md](DESIGN.md). Workflow protocol: [AGENTS.md](AGENTS.md). Build plan: [AGENT_IMPLEMENTATION.md](AGENT_IMPLEMENTATION.md).
