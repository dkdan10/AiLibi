# AiLibi — an Among Us-style game played by LLM agents, built by directing AI coding agents

*Recorded AI social deduction*

by **Daniel Keinan** · implemented by Claude Code and Codex agents · AI-reviewed · [MIT](LICENSE) · [![CI](https://github.com/dkdan10/AiLibi/actions/workflows/ci.yml/badge.svg)](https://github.com/dkdan10/AiLibi/actions/workflows/ci.yml)

**[Watch a recorded game in your browser](https://dkdan10.github.io/AiLibi/)** · [See the results](https://dkdan10.github.io/AiLibi/?set=9p2i&view=tournament) · [Five-minute guide](docs/reading-guide.md)

AiLibi is a hidden-role game in the shape of Among Us. Nine players share a small space station: seven crewmates do tasks while two impostors kill, lie and sabotage. When a body is found, everyone meets, speaks and votes to eject someone or skip. Rules move each player; a language model speaks and votes for it at meetings, from a memory of what that player saw and heard. The question: does each vote rest on something the voter actually saw or heard? Two 50-game sets are recorded: 9p2i (nine players, two impostors) and 4p1i (four players, one impostor).

[![One scene in the omniscient view and through a crewmate's fog, with the agent's accusation below](docs/media/spectator-two-truths.png)](https://dkdan10.github.io/AiLibi/)

*At tick 9 two players lie dead, one impostor stands in MedBay and the other is inside a vent, while p-5 can see only p-4, whom p-5 accuses at the meeting that follows. This is 9p2i seed 19, the game the demo's guided tour opens on, from the 2026-10-09 record (9p2i); [media provenance](docs/media/README.md#provenance) records its source and asset identities.*

Here p-5 accuses p-4 on something it really saw, yet p-4 is a crewmate.

## Who did what

Daniel Keinan directed the project and decided what was accepted, without hand-writing the production code; AI agents wrote it, and the audits here are AI reviews, not independent human assurance.

Daniel's part:

- set the question and the design: a pure engine, agents walled off from game state, a model only at meetings;
- chose the checks and wrote targets down before measuring;
- decided which of the 514 pull requests merged (503, as of 2026-10-12);
- decided what the demo shows.

Coding agents wrote the code, tests and most documents and drafted the tasks, with AI review passes: 2,131 commits as of 2026-10-12.

[How a change gets in](docs/workflow.md) · [Lessons](docs/lessons.md) · [One decision, traced](docs/ownership-case-study.md) · [History](docs/history.md)

## The demo

[![The same game playing from its first tick to the meeting](docs/media/spectator-journey.gif)](https://dkdan10.github.io/AiLibi/)

The [demo](https://dkdan10.github.io/AiLibi/) carries all 100 games; its guided tour opens game 19 of the 9-player set, and Play stops at the first meeting.

- **Truth and fog.** *See as* any player dims the all-seeing map to that player's fog.
- **Behind each accusation.** Click a ballot's citation to open the sighting or statement it names.
- **A player's mind.** Click a player for its suspicions, memory and exact model prompts.

## How it works

- **A pure engine** ([`engine/`](engine/)). One pure function advances the world one tick at a time; the random state is in every recorded hash.
- **Hashed replays** ([`orchestrator/`](orchestrator/)). Each tick carries a SHA-256 of the whole state, and model replies are recorded, so replays never call a model.
- **A firewall** ([`observation/`](observation/)). Agents get filtered packets, never engine state. One of five import contracts keeps [`agents/`](agents/) out of the engine; [a test](tests/test_firewall.py) plants a forbidden import that must fail.
- **Two model calls** ([`meetings/`](meetings/), [`llm/`](llm/)). Movement, kills and tasks are rule-based; the model is called at exactly two sites, a speaking turn and a ballot, under token, cost and time budgets.
- **One gate** ([`scripts/check.sh`](scripts/check.sh)). Lint, strict typing, import contracts, 10,954 Python and 1,327 frontend tests as of 2026-10-12, and a checker that re-derives this page's table.

Python 3.11 · FastAPI/Pydantic · React/Vite/PixiJS · strict mypy · Hypothesis. [Current architecture and enforced boundaries](docs/architecture.md).

## What the recordings show

In the 9-player set:

1. **Votes follow a rule-based suspicion score, and going against it is usually wrong.** The ballot prompt shows the voter's rule-kept suspicion of every player ([`agents/memory/`](agents/memory/)). Crew votes for the highest-rated player hit an impostor [215 of 235 times](docs/process-scorecard.md) (91%); the 56 against it hit one twice (4%), where chance is about one in three.
2. **A reported vent sighting decides outcomes.** A vent claim counts only when the engine's witness record matches it. In the 24 meetings with one, all 24 ejections removed an impostor; in the 95 without, [22 of 37](docs/reading-guide.md) did and 15 removed crewmates, near a coin flip: hard evidence, not general social deduction.
3. **Votes cite what the voter saw.** [394 of 397](docs/process-scorecard.md) votes to eject cite something the voter saw or heard; the ballot demands a citation, so this is by design.

*Before* is each set's previously shown recording.

| What | Figure | Before | Recorded on, and where it lives |
|---|---|---|---|
| Sample games that replay byte for byte | 100 of 100 (100%) | 100 of 100 (100%) | `scripts/verify_samples.sh`; on every push, a [gate test](tests/api/test_replay_loader.py) for the 9-player set |
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

*Valid* means resolvable, not supported.

## Limitations

- **One model, one recording per round.** One open model and prompt set, recorded once per round, so no figure ranks one version above another.
- **Learned policies stayed off.** Four learned impostor policies won more games and still failed gates written before measuring ([negative results](docs/ml-program.md)).
- **Reproducibility has three scopes.** Recordings always reconstruct; fake-provider runs repeat on one machine; real-model games are not deterministic; bit-identical optimizer output across machines is seen on Linux/x86-64 only.

**Targets written down before measuring were missed twice:** the owner adopted the first recording anyway, in writing, and nothing from the second ([what each measured](docs/history.md#evidence-honesty-phase-20)).

**One known leak.** In the 2026-09-22 recordings the opening prompts name each body by a label that reveals when it died; the shown 9-player set's report openings no longer carry it (0 of 115). The full repair stays switched off, not adopted ([observation contract](docs/observation-contract.md)).

## Install, then verify offline

You need [uv](https://docs.astral.sh/uv/getting-started/installation/), Python 3.11 (`uv python install 3.11`) and Node.js 22 or newer:

```bash
git clone --filter=blob:none https://github.com/dkdan10/AiLibi.git
cd AiLibi
bash scripts/setup_env.sh
```

Nothing below needs an API key or the network.

```bash
# 1. The viewer on the committed recordings: http://localhost:5173.
bash scripts/run_spectator.sh

# 2. Two fake-provider runs of one seed match (under 1 s each).
d=$(mktemp -d)
AILIBI_LLM_PROVIDER=fake uv run --offline python scripts/run_game.py \
  --seed 42 --max-ticks 50 --replay-path "$d/r1.jsonl" &&
  AILIBI_LLM_PROVIDER=fake uv run --offline python scripts/run_game.py \
  --seed 42 --max-ticks 50 --replay-path "$d/r2.jsonl" &&
  diff -q "$d/r1.jsonl" "$d/r2.jsonl"

# 3. Re-run the 200 sample and candidate recordings (about 20 s).
UV_OFFLINE=1 bash scripts/verify_samples.sh

# 4. The full gate (its test tier: about 18 min on four cores).
bash scripts/check.sh
```

Fake-provider games are short and every meeting skips, because the fake provider returns one fixed reply. The local API shows hidden roles, so it stays on localhost. Real games need a provider and spending limits ([setup](llm/README.md), [.env.example](.env.example)).

## The recordings

A clone includes 100 sample replays under `replays/samples/`: two 50-game tournaments played by the `Qwen/Qwen3.6-27B` model. The 4-player set was regenerated 2026-09-22 (4p1i) with every experimental switch off ([its record](audits/audit-2026-09-22-process-rerecord.md)): impostor win rate 36% (4p1i). The 9-player set was regenerated 2026-10-09 (9p2i) under the adopted gameplay changes plus the [route lines](docs/glossary.md#route-line-what-the-doors-say-about-a-players-stated-places), a recorded setting ([its record](audits/audit-2026-10-09-stage-b-r3.md)): impostor win rate 34% (9p2i). Each set's manifest lists its prompt versions game by game ([4p1i](replays/samples/4p1i/MANIFEST.md), [9p2i](replays/samples/9p2i/MANIFEST.md)). The picture above is from the 9-player game the guided tour opens on.

**The fake provider's report is empty on purpose.** A real report, gzipped at [replays/samples/9p2i/tournament-eval-report.json.gz](replays/samples/9p2i/tournament-eval-report.json.gz), records 61 ejections; 46 removed an impostor, 36 of those 46 with evidence against that player on the meeting's record.

[Glossary](docs/glossary.md) · [Audits](audits/README.md) · [Contributing](CONTRIBUTING.md)
