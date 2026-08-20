# AiLibi — LLM social deduction behind an observation firewall, built by directing AI coding agents

by **Daniel Keinan** · code by Claude Code agents, reviewed by Codex · [MIT](LICENSE) · [![CI](https://github.com/dkdan10/AiLibi/actions/workflows/ci.yml/badge.svg)](https://github.com/dkdan10/AiLibi/actions/workflows/ci.yml) ![Python 3.11](https://img.shields.io/badge/python-3.11-blue) · May–August 2026, solo

**▶ Live demo** — the spectator as a static directory, no server behind it: `https://dkdan10.github.io/AiLibi/`
<!-- OWNER: enable Pages, then confirm this URL resolves; plain text until it does. -->

[![Nine agents mid-meeting: the accusation chain beside every ballot](docs/media/spectator-meeting.png)](docs/media/spectator-meeting.png)

*One meeting, seed 2: who accused whom, the observations behind each claim, and every ballot beside the sentence its voter acted on.*
<!-- ANCHOR: a later contract swaps this hero for a side-by-side still, omniscient beside one crewmate's fog-of-war. -->

![The spectator playing a featured replay](docs/media/spectator-journey.gif)

*Fifteen seconds against the built static bundle: pick a featured game, play it, watch the transport stop itself when a meeting starts.*

---

## Sixty seconds: what you are looking at

Nine LLM agents walk a room graph, work their task lists, witness what they can actually see, and meet to argue about it. Two are impostors, told each other's names at the start; the other seven reason in the dark. The spectator opens any agent's mind at any tick — prompt, response, memory, beliefs — and every game replays from an action log and a per-tick hash, byte for byte. (*AiLibi*: an alibi, with the AI in front.)

## At a glance

- **Stack** — Python 3.11 · FastAPI · Pydantic · React + Vite + PixiJS · uv · `mypy --strict` · Hypothesis.
- **Scale** — a snapshot of `main` as of 2026-08-19: 903 commits · 364 merged pull requests · 363 generated agent prompts · 100 committed replays · 4,940 tests in the default gate.
- **Status** — active; phases 0–19 closed, the last on 2026-08-18; phase 20 open.

## Verify it yourself in one minute

Three commands, three claims, all free and offline.

```bash
bash scripts/setup_env.sh   # one-time: uv sync + npm ci

# 1. Proves determinism — the same seed twice, byte-identical replay JSONL.
#    (A fresh dir each time: the recorder refuses to overwrite a replay path.)
d=$(mktemp -d)
uv run python scripts/run_game.py --seed 42 --replay-path "$d/r1.jsonl" &&
  uv run python scripts/run_game.py --seed 42 --replay-path "$d/r2.jsonl" &&
  diff -q "$d/r1.jsonl" "$d/r2.jsonl"

# 2. Proves replay integrity — every committed sample still reconstructs through
#    the engine's per-tick state hashes.
bash scripts/verify_samples.sh

# 3. Proves the demo is a static directory — a built bundle with no API process
#    in it, playable from any file server.
uv run python scripts/build_demo_bundle.py && python -m http.server -d frontend/dist/demo-bundle 8080
```

## How it was built — who did what

<!-- OWNER: confirm wording — first person, written from git evidence. -->
I'm Daniel Keinan. I built AiLibi solo between May and August 2026 by directing AI coding agents — Claude Code for the code, Codex for review and audit — against written task contracts. I wrote the contracts in `tasks/`, the standing rules in [AGENTS.md](AGENTS.md), the review gates, the audit rulings and the product direction; I did not write production code by hand. The agents wrote every coding pull request and most of the audits. Check that in git instead of taking my word: agent branches are named `claude/…`, agent commits are authored "Claude", and, as of 2026-08-19, 328 commits carry a `Co-Authored-By` trailer naming the model. Two disclosures ride with it: the "independent external audits" here are AI auditors I commissioned, not third parties, and every gameplay and ML number comes from one model on one prompt set, at 50 games per set.
<!-- OWNER: end. -->

Every coding task follows the same five steps:

1. **Author a contract** in `tasks/phase-N.md` — branch, dependencies, files in and out of scope, definition of done.
2. **Generate the prompt** with `uv run python scripts/generate_prompts.py`, which refuses to let a prompt drift from its contract.
3. **Dispatch an agent** against that prompt, in a fresh checkout.
4. **Review the pull request.** CI is required on `main` ([the workflow](.github/workflows/ci.yml)) and `bash scripts/check.sh` runs the same gate locally, so anyone can reproduce the verdict. I review what a gate cannot judge.
5. **Checkpoint** before high-blast-radius work with a read-only audit.

One contract and the prompt generated from it: [robust JSON extraction](tasks/phase-3.md), [its prompt](agent_prompts/task-3-19-robust-json-extraction-and-failure-recording.md).
<!-- ANCHOR: a later contract shows a contract, its prompt and the merged pull request inline. -->

## What it is

A deterministic testbed for studying multi-agent reasoning under hidden information, not a game with AI players bolted on. Three decisions carry the weight. They are recorded verbatim in [ADR-0001](docs/adr/0001-three-load-bearing-decisions.md).

1. **A deterministic engine behind a strict observation firewall.** The engine advances world state as a pure tick function — no wall clock, no unseeded randomness, no global state — so the same seed and the same inputs always produce the same bytes. Agents cannot import the engine, directly or transitively: an agent physically cannot read the state it must deduce. It sees an `ObservationPacket` and a `PublicMapView`, and emits an `ActionIntent`. The firewall covers the *agent* surface; the spectator is privileged by design.
2. **Two-tier reasoning.** Movement, tasks and venting are rule-based, every tick. Meeting speech, voting and suspicion updates call an LLM, only at meetings and triggers. Without that split, cost and latency make the system unviable.
3. **Memory is structured first.** Each agent reasons from a typed event log and a belief state derived from it; the LLM sees a rendered view of that structure, never raw engine state.

The system as built: [docs/architecture.md](docs/architecture.md).
<!-- ANCHOR: a later contract inlines the as-built layering diagram here. -->

## What the measurements said

| What | Figure | Recorded on, and where it lives |
|---|---|---|
| Committed sample replays that reconstruct byte-identically | 100 of 100 | every commit — `scripts/verify_samples.sh` |
| Observation-firewall violations, all phases | zero | never breached in CI: the [import-linter contracts](.importlinter), the planted-leak test in [tests/test_firewall.py](tests/test_firewall.py), the recursive sweep in [eval/leak_scan.py](eval/leak_scan.py) |
| Impostor win rate, committed samples | 34% (4p1i), 30% (9p2i) | reference recording 6, 2026-07-20 — [4p1i](replays/samples/4p1i/MANIFEST.md), [9p2i](replays/samples/9p2i/MANIFEST.md) |
| Eject ballots carrying a valid citation, a turn or an observation id (9p2i) | 520 / 520, zero dangling | reference recording 6, 2026-07-20 — [instrument](tests/eval/test_vj_instruments.py) |
| Correct 9p ejections riding an ejectee-specific vent sighting | 68 / 78 = 87% | reference recording 6, 2026-07-20 — [triage audit](audits/audit-phase-19-triage.md) |

**The headline finding is a negative one, and that is the point.** Almost nine in ten of the crew's correct 9-player ejections ride an engine-certified vent sighting; without one, ejection accuracy is roughly chance and innocents go down two to one. So the corpus demonstrates LLM evidence-processing of certified facts, plus real deception on top — and *not* general social deduction. The cross-tab is in the [reading guide](docs/reading-guide.md).

<!-- ANCHOR: a later contract adds the ML program's paragraph, titled by its result, plus the table's before/after column. -->
<!-- ANCHOR: a later contract adds "What I learned" and a lessons page. -->

## Project status

Active. Phases 0–5 built the MVP; phases 6–19 pushed how well the agents reason, moved the eval onto a hosted model, and ran a four-phase ML program. Phase 19 closed 2026-08-18; phase 20 is open.

Four learned tactical policies each beat the scripted one on wins. None became the default, because each failed an evidence-quality bar I had written down *before* the measurement that judged it — so both of those phases closed having adopted nothing and moved no reference recording. That is what those two closes mean: the bar was pre-registered, the honest answer was "not yet", and I record the miss rather than move it. The current reference recording is the sixth, which the audits call [baseline 6](docs/glossary.md#baseline-n-the-reference-recording).

Close audits start at the MVP close and resume at phase 13; earlier rows link the contract. One paragraph per phase: [docs/history.md](docs/history.md).

| Phase | What it did | Record |
|---|---|---|
| 0 | Scaffolding, CI, the firewall lint rule, the first ADR | [contract](tasks/phase-0.md) |
| 1 | Engine: state, rules, seeded RNG, visibility, replay, leak test | [contract](tasks/phase-1.md) |
| 2 | Tactical agents: memory, perception, pathfinding, headless runs | [contract](tasks/phase-2.md) |
| 3 | LLM-driven meetings, voting, contradiction detection | [contract](tasks/phase-3.md) |
| 4 | The spectator UI, replay-only | [contract](tasks/phase-4.md) |
| 5 | Eval metrics, dashboard, prompt-regression gate — the MVP | [audit](audits/audit-2026-05-30-0059-mvp-close.md) |
| 6 | Post-MVP repair and hardening | [contract](tasks/phase-6.md) |
| 7 | Impostor coordination; the eval moved to a local model | [contract](tasks/phase-7.md), [plan](tasks/phase-7-plan.md) |
| 8 | Deduction-substrate restructure | [contract](tasks/phase-8.md) |
| 9 | Producer hygiene and conversion quality | [contract](tasks/phase-9.md) |
| 10 | Conviction-engine repair; the crew's evidence economy | [contract](tasks/phase-10.md) |
| 11 | The impostor's information economy: vents, sabotage, balance | [contract](tasks/phase-11.md) |
| 12 | Front-end rework: the replay viewer as a product | [contract](tasks/phase-12.md) |
| 13 | Pre-ML grounding: rubric repair and deduction rework | [audit](audits/audit-2026-06-25-0859-phase-13-close.md) |
| 13.5 | Memory correctness, down to the substrate | [contract](tasks/phase-13-5.md) |
| 14 | A hosted provider, and the model/prompt migration onto it | [audit](audits/audit-phase-14-close.md) |
| 15 | Evidence cleanup, then the training environment | [audit](audits/audit-phase-15-close.md) |
| 16 | Voice and judgment: citation-gated ballots, pooling, personas | [audit](audits/audit-phase-16-close.md) |
| 17 | Co-adaptation: corpus and learned policies re-run together | [audit](audits/audit-phase-17-close.md) |
| 18 | The ML phase: co-evolution, the finalist eval, no adoption | [audit](audits/audit-phase-18-close.md) |
| 19 | Review and refresh: truth sweeps, spectator pass, ML close | [audit](audits/audit-phase-19-close.md) |
| 20 | In progress | [contract](tasks/phase-20.md) |

## Run it

```bash
bash scripts/setup_env.sh   # uv sync + npm ci; Python 3.11 and Node are both required
bash scripts/check.sh       # the full local gate: lint, types, imports, tests, frontend build
bash scripts/run_spectator.sh                       # API + UI on http://localhost:5173
uv run python scripts/run_tournament.py --num-games 50 --output-dir replays --roster-preset 4p1i
```

The spectator API is an unauthenticated game-master view, so it is loopback-only and stays that way; the static bundle is the only sanctioned public artifact ([docs/deployment.md](docs/deployment.md)).

**Providers.** `AILIBI_LLM_PROVIDER` selects one: `fake` (the default — deterministic, offline, $0, what CI runs), `anthropic`, `ollama` for a local open model, or `featherless` for the hosted model every recorded number came from. CI never selects a real provider and never reaches the network.

**The fake provider's report is empty on purpose.** Every fake ballot's vote target is a minted placeholder that the meeting layer normalizes to SKIP, so a fake tournament ejects nobody and its rates come out null. A real one is committed: [replays/samples/9p2i/tournament-eval-report.json](replays/samples/9p2i/tournament-eval-report.json) records 101 ejections, vote correctness 0.923, ejection accuracy 0.772.

**The samples.** A fresh clone ships 100 sample replays under `replays/samples/`: two 50-game tournaments, one per roster preset (`4p1i` and `9p2i`), regenerated 2026-07-20 against `Qwen/Qwen3.6-27B` on the `qwen3_6_27b` `v3` prompt set, impostor win rates 34% (4p1i) and 30% (9p2i). Each set's `MANIFEST.md` is the row-by-row provenance record. Replays you generate into `replays/` override the bundled ones.

**Cloning.** `git clone --filter=blob:none https://github.com/dkdan10/AiLibi.git` is the fast path — roughly the 256 MiB the working tree needs, not every blob version. A full clone still pays for the committed evidence; [docs/artifacts.md](docs/artifacts.md) holds the retention rules and the restore script.

---

**Where to go next.** [Architecture](docs/architecture.md) · [Reading guide](docs/reading-guide.md) · [Glossary](docs/glossary.md) · [History](docs/history.md) · [Audits index](audits/README.md) · [Workflow protocol](AGENTS.md) · [Contributing](CONTRIBUTING.md) · [Design history](DESIGN.md) · [Build plan](AGENT_IMPLEMENTATION.md).
