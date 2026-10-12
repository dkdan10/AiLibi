# AiLibi — can agents reason from what they actually saw?

*Recorded AI social deduction*

by **Daniel Keinan** · implemented by Claude Code and Codex agents · AI-reviewed · [MIT](LICENSE) · [![CI](https://github.com/dkdan10/AiLibi/actions/workflows/ci.yml/badge.svg)](https://github.com/dkdan10/AiLibi/actions/workflows/ci.yml)

**[Watch the recorded demo](https://dkdan10.github.io/AiLibi/)** · [See the results](https://dkdan10.github.io/AiLibi/?set=9p2i&view=tournament) · [Read the five-minute guide](docs/reading-guide.md)

## What this is

AiLibi is a game of hidden roles, in the shape of Among Us, played by language-model agents and recorded so that anyone can replay it. Nine players move around a small space station: seven crewmates doing tasks, two impostors who kill, lie and sabotage. When a body is found, play stops for a meeting: each player speaks from what it saw, then votes to eject someone or to skip. Crew win by finishing tasks or ejecting both impostors; impostors win by killing enough of the crew.

It is two things at once. It is a deterministic game engine and a viewer: every game is a recording that re-runs byte for byte, and the viewer shows any moment through the all-seeing camera or one player's fog. And it is an experiment in building software with AI coding agents, which wrote the code, the tests and most of the documents to written tasks, with one human setting the goal and deciding what was accepted.

The question is exact: not whether the agents catch the impostors, but whether each vote rests on something the voter actually saw or heard. A crewmate who votes out an innocent player on a believable lie is the game working. A vote with nothing behind it is not.

[![One scene in the omniscient view and through a crewmate's fog, with the agent's accusation below](docs/media/spectator-two-truths.png)](https://dkdan10.github.io/AiLibi/)

*At tick 9 two players lie dead, one impostor stands in MedBay and the other is inside a vent, while p-5 can see only p-4, whom p-5 accuses at the meeting that follows. This is 9p2i seed 19, the game the demo's guided tour opens on, from the 2026-10-09 record (9p2i); [media provenance](docs/media/README.md#provenance) records its source and asset identities.*

[![The same game playing from its first tick to the meeting](docs/media/spectator-journey.gif)](https://dkdan10.github.io/AiLibi/)

The [recorded demo](https://dkdan10.github.io/AiLibi/) opens on a first meeting with a short tour: click any accusation to see the exact line behind it, and switch to one player's fog to see how little it knows when it votes.

## How it works

- **A deterministic engine.** One pure function advances the world a tick at a time, with the random state written into every recorded hash, so a committed game re-runs byte for byte.
- **An observation boundary.** Agents never touch engine state. They receive sanitized packets and a public map; import rules and planted-leak tests enforce the line; only the viewer sees everything.
- **Two tiers of reasoning.** Movement and tasks are rule-based every tick. A language model speaks and votes only at meetings, from a rendered memory of what that player saw and heard.
- **A gate on every push.** Lint, strict typing, import contracts, the tests, and a checker that re-derives this page's numbers from the recordings. The default test tier holds 10,954 tests as of 2026-10-12.

Python 3.11 · FastAPI/Pydantic · React/Vite/PixiJS · strict mypy · Hypothesis. [Current architecture and enforced boundaries](docs/architecture.md).

## Who did what

Daniel Keinan directed the project and decided what was accepted, without hand-writing the production code; AI agents wrote it, and the audits here are AI reviews, not independent human assurance. Each change arrived on its own branch with a written task, a pull request and the full gate.

[How a change gets in](docs/workflow.md) · [Lessons](docs/lessons.md) · [One decision, traced](docs/ownership-case-study.md) · [History](docs/history.md)

## What the recordings show, and what they do not

The shown 9-player set was recorded 2026-10-09 under the adopted gameplay changes; the 4-player set and the ML training games were recorded 2026-09-22. Three things hold there, each with its command in the [reading guide](docs/reading-guide.md):

- **Votes are grounded.** Almost every vote to eject names a line the voter held about the accused, and almost no ballot lacks a stated reason.
- **The engine, not the model, catches venting.** Every ejection after a certified vent sighting removed an impostor. Without one the table is near a coin flip and some ejections removed crewmates.
- **No change is claimed to have improved anything.** Each round of changes was recorded once, as fifty games; one recording cannot show that one version plays better than another.

| What | Figure | Before | Recorded on, and where it lives |
|---|---|---|---|
| Sample games that replay byte for byte | 100 of 100 (100%) | 100 of 100 (100%) | every commit — `scripts/verify_samples.sh` |
| Observation boundary checks | import rules and planted/recursive leak checks | import rules and planted/recursive leak checks | [contracts](.importlinter), [planted imports](tests/test_firewall.py), [packet scans](eval/leak_scan.py); bounded checks, not complete privacy assurance |
| Eject ballots citing what the voter saw or heard about the accused (9p2i) | 394 of 397 (99%) | 407 of 410 (99%) | [process scorecard](docs/process-scorecard.md); a floor: the ballot asks every eject to cite |
| Crew eject ballots naming someone other than the voter's [top suspect](docs/glossary.md#top-suspect-the-player-a-voters-own-suspicion-rates-highest) (9p2i) | 56 of 291 (19%) | 65 of 292 (22%) | [process scorecard](docs/process-scorecard.md) |
| Ballots with no stated reason (9p2i) | 6 of 702 (1%) | 11 of 691 (2%) | [process scorecard](docs/process-scorecard.md) |
| Ballots whose target is the one their voter wrote (9p2i) | 692 of 702 (99%); 10 impostor votes against a partner turned into skips | 674 of 691 (98%) | [process scorecard](docs/process-scorecard.md) |
| Eject ballots with a valid citation of a statement or sighting (9p2i) | 397 of 397 (100%), zero dangling | 410 of 410 (100%), zero dangling | the 2026-10-09 record (9p2i) — [instrument](tests/eval/test_vj_instruments.py) |
| Impostor win rate, sample games | 36% (4p1i), 34% (9p2i) | 36% (4p1i), 48% (9p2i) | the 2026-09-22 record (4p1i), the 2026-10-09 record (9p2i) — [4p1i](replays/samples/4p1i/MANIFEST.md), [9p2i](replays/samples/9p2i/MANIFEST.md) |
| Impostors among those ejected, with and without proof of their role (9p2i) | 24 of 24 (100%) vs 22 of 37 (59%) | 24 of 24 (100%) vs 20 of 42 (48%) | the 2026-10-09 record (9p2i) — [the record](audits/audit-2026-10-09-stage-b-r3.md) §12.5, against [round 2's](audits/audit-2026-10-01-stage-b-r2.md) §9.6; 15 of 15 innocent ejections sit in the no-proof cell |
| Impostors ejected after a reported sighting of them venting (9p2i) | 24 of 46 (52%) | 24 of 44 (55%) | the 2026-10-09 record (9p2i) — the cross-tab in the [reading guide](docs/reading-guide.md). Reading: general social deduction, **not** demonstrated |
| Learned tactical policies that became the default | none, ruled twice | none, ruled twice | 2026-07-18 and 2026-08-01 — [phase 17](audits/audit-phase-17-close.md), [phase 18](audits/audit-phase-18-close.md) |

*Valid* means resolvable, not supported. Four learned impostor policies won more games than the scripted one and none became the default; each failed a gate written before measuring: [methods, negative results and limits](docs/ml-program.md).

**Targets written down before measuring were missed twice:** the owner adopted the first recording anyway, in writing, and nothing from the second ([what each measured](docs/history.md#evidence-honesty-phase-20)).

**One known leak.** In the 2026-09-22 recordings the opening prompts name each body by a label that reveals when it died; the shown 9-player set's report openings no longer carry it (0 of 115). The full repair stays switched off, not adopted. [Observation contract and limitations](docs/observation-contract.md).

## Try it offline

You need [uv](https://docs.astral.sh/uv/getting-started/installation/), Python 3.11 (`uv python install 3.11`) and Node.js 22 or newer; the locked install takes a few minutes:

```bash
git clone --filter=blob:none https://github.com/dkdan10/AiLibi.git
cd AiLibi
bash scripts/setup_env.sh
```

Nothing below needs a provider account or network access.

```bash
# 1. Watch the committed recordings: starts the API and the viewer on
#    http://localhost:5173, opening on the 50-game 9-player set.
bash scripts/run_spectator.sh

# 2. Two fake-provider runs of one seed produce identical replays.
d=$(mktemp -d)
AILIBI_LLM_PROVIDER=fake uv run --offline python scripts/run_game.py \
  --seed 42 --max-ticks 50 --replay-path "$d/r1.jsonl" &&
  AILIBI_LLM_PROVIDER=fake uv run --offline python scripts/run_game.py \
  --seed 42 --max-ticks 50 --replay-path "$d/r2.jsonl" &&
  diff -q "$d/r1.jsonl" "$d/r2.jsonl"

# 3. Every committed recording re-runs through the engine byte for byte.
UV_OFFLINE=1 bash scripts/verify_samples.sh

# 4. Build the static demo the public site serves; open http://127.0.0.1:8080.
uv run --offline python scripts/build_demo_bundle.py
uv run --offline python -m http.server --bind 127.0.0.1 \
  -d frontend/dist/demo-bundle 8080
```

Two of three reproducibility claims are proven: a committed recording always reconstructs, and a fake-provider run repeats on one machine. Fresh games against a real model are not deterministic. Bit-identical learned-optimizer output across machines is seen on Linux/x86-64 only.

The spectator's API is an unauthenticated game-master view and stays loopback-only. Real generation needs a selected provider plus token, cost and wall-time limits: [provider setup](llm/README.md), [.env.example](.env.example), [recording procedure](docs/deployment.md).

## The recordings

A clone includes 100 sample replays under `replays/samples/`: two 50-game tournaments played by the `Qwen/Qwen3.6-27B` model. The 4-player set was regenerated 2026-09-22 (4p1i) with every experimental switch off ([its record](audits/audit-2026-09-22-process-rerecord.md)): impostor win rate 36% (4p1i). The 9-player set was regenerated 2026-10-09 (9p2i) under the adopted gameplay changes plus the [route lines](docs/glossary.md#route-line-what-the-doors-say-about-a-players-stated-places), a recorded setting ([its record](audits/audit-2026-10-09-stage-b-r3.md)): impostor win rate 34% (9p2i). Each set's manifest lists its prompt versions game by game ([4p1i](replays/samples/4p1i/MANIFEST.md), [9p2i](replays/samples/9p2i/MANIFEST.md)). The picture above is from the 9-player game the guided tour opens on.

**The fake provider's report is empty on purpose.** A real report, gzipped at [replays/samples/9p2i/tournament-eval-report.json.gz](replays/samples/9p2i/tournament-eval-report.json.gz), records 61 ejections; 46 removed an impostor, 36 of those 46 with evidence against that player on the meeting's record.

[Reading guide](docs/reading-guide.md) · [Glossary](docs/glossary.md) · [Audits](audits/README.md) · [Contributing](CONTRIBUTING.md)
