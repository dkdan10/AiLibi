# AiLibi

> An Among-Us-style social-deduction simulator being built almost entirely by AI coding agents under a strict review protocol — and a working example of how to keep architecture coherent across many agent-authored pull requests.

---

## What this is

AiLibi is two things at once.

**A deterministic multi-agent reasoning testbed.** Players (agents) roam a room graph, complete tasks, witness events, and meet to deliberate. One impostor is hidden among them. The product is a research environment for studying agent reasoning under hidden information — not a game with AI players bolted on. See [DESIGN.md](DESIGN.md) for the full system architecture.

**An experiment in agentic software workflow.** Every coding PR was opened by an AI coding agent against a task contract authored by a human. Architecture is enforced by tooling — import-linter, `mypy --strict`, a recursive observation leak test, byte-identical replay determinism. The contracts in `tasks/phase-N.md` are the only spec each agent sees. So far: over 25 merged PRs, 257 passing tests, two read-only audits in `audits/`, zero observation-firewall violations.

---

## How this is being built

The workflow is the experiment. Every coding task follows the same five-step loop:

1. **Author a task contract** in `tasks/phase-N.md` — branch, dependencies, files in/out of scope, definition of done, implementation hint.
2. **Generate a paste-ready prompt** with `uv run python scripts/generate_prompts.py`. The generator validates that every prompt mirrors its contract byte-for-byte and that parallel tasks don't share file scope.
3. **Dispatch an agent** (Claude Code, web or CLI, Codex) against the prompt. The agent works in a fresh checkout, runs `bash scripts/check.sh` until green, and opens a PR populated against [.github/pull_request_template.md](.github/pull_request_template.md).
4. **Review the PR.** CI gates catch the easy stuff (lint, types, firewall, determinism); the human catches the rest.
5. **Audit every N tasks.** A read-only audit (`audits/audit-YYYY-MM-DD-HHMM.md`) re-verifies every prior Pass finding hasn't regressed and surfaces drift CI can't catch. The repo currently audits before each high-blast-radius integration task.

Representative artifacts to skim:

- A task contract — [tasks/phase-2.md](tasks/phase-2.md) Task 2.8 (the headless orchestrator)
- An auto-generated prompt — [agent_prompts/task-2-8-headless-game-orchestrator.md](agent_prompts/task-2-8-headless-game-orchestrator.md)
- An audit report — [audits/audit-2026-05-10-0721.md](audits/audit-2026-05-10-0721.md)

---

## Three load-bearing decisions

These are the architectural invariants every contributor (human or agent) must respect. They are documented as ADR-0001 and re-checked on every audit.

**1. Tick-based deterministic engine.** The engine is a pure function `(WorldState, list[Action]) -> (WorldState, list[Event])` at a fixed tick rate. Replays are bit-exact from a seed. No wall-clock, no unseeded randomness, no global state — verified by property tests and three scripted-game determinism tests.

**2. Strict observation firewall.** `agents/` cannot import from `engine/`, directly or transitively. The boundary is import-linter enforced and tested with both direct-leak and transitive-leak fixtures. Agents see only `ObservationPacket` and `PublicMapView`; they emit only `ActionIntent`. The leak test walks every emitted packet recursively and rejects any hidden field (role, killer identity, kill attribution).

**3. Structured memory first.** Agents reason from a typed event log and a derived belief state (suspicion, trust, alibi). When the LLM arrives in Phase 3, it will see a *rendered view* of that structure during meetings.

---

## Project status

| Phase | Description | Status |
| --- | --- | --- |
| 0 | Scaffolding, CI, firewall lint, ADR | merged |
| 1 | Engine: state, rules, RNG, visibility, replay, leak test | merged |
| 2 | Tactical agents: boundary, memory, perception, A*, FSMs, headless orchestrator | tasks 2.1–2.8 merged; tournament harness (2.9) next |
| 3 | LLM-driven meetings, voting, contradiction detection | not started |
| 4 | Spectator UI (FastAPI + React + PixiJS) | not started |
| 5 | Eval metrics + tournament dashboard | not started |
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

## Audits

The `audits/` folder is a public artifact. Each audit is a read-only checkpoint that:

- runs the full check gate from scratch,
- re-verifies every prior Pass finding hasn't regressed (`git diff` against the prior audit's HEAD),
- traces each new finding to a file path and line range,
- decides Ready / Ready-with-fixes / Not-ready for the next high-blast-radius task.

So far:

- [audits/audit-2026-05-09-1901.md](audits/audit-2026-05-09-1901.md) — pre-Phase-2 baseline, after Task 2.1.
- [audits/audit-2026-05-10-0721.md](audits/audit-2026-05-10-0721.md) — Phase 2 checkpoint, after Task 2.7. Six tasks landed in parallel; two Medium and four Low findings produced a one-PR "post-2.7 audit repair" cleanup task (Task 2.7.5).

Findings that didn't catch in CI but *did* catch in audit: scope drift (a task quietly modified a file outside its declared scope), a tactical policy that would crash on a disconnected map and an enum coupling between the engine and perception that no test was enforcing.

---

## Lessons from building this

A handful of things that didn't work, and what changed:

- **Scope drift is the most common defect.** Task 2.4 was declared in-scope for `agents/perception.py` only, but the agent also wired perception into `agents/runtime.py` (correct behaviour, missing from scope). CI was green; the audit caught it. The fix is to either update the contract or revert the wiring — both options have a clear paper trail. Lesson: file-scope discipline is more brittle than test discipline; audit for it explicitly.
- **CI proves correctness, not completeness.** All five low-severity findings from the post-2.7 audit passed CI cleanly. The crewmate FSM would have crashed on the first disconnected map; no test forced one to exist. The audit asked "what could break that no test would catch?" — and the answer was a non-trivial list.
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
```

Python 3.11 only. The [`uv`](https://docs.astral.sh/uv/) package manager is required.

---

## Architecture notes

- `engine/` — pure simulation. No LLM, no I/O, no globals. Owns hidden state.
- `observation/` — the firewall. Builds `ObservationPacket` and `PublicMapView` from engine state, strips every hidden field, audits every packet to disk.
- `agents/` — tactical and (future) strategic policies. No engine imports.
- `orchestrator/` — wires everything: seeds initial state, dispatches agents, translates `ActionIntent` → engine `Action`, records replay.
- `tasks/` — the project's spec, decomposed into task contracts.
- `agent_prompts/` — paste-ready prompts auto-generated from the task contracts.
- `audits/` — read-only checkpoint reports.

Full architecture: [DESIGN.md](DESIGN.md). Workflow protocol: [AGENTS.md](AGENTS.md). Build plan: [AGENT_IMPLEMENTATION.md](AGENT_IMPLEMENTATION.md).
