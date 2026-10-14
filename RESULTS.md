# Results in full

Every figure on this page is recomputed from the committed recordings and the generated reports by `scripts/check_doc_facts.py`, which runs inside `bash scripts/check.sh` and fails when a number drifts from its source. The [README](README.md) carries the plain-words summary; this page is the ledger it summarises.

## What the recordings show

In the 9-player set:

1. **Votes follow a rule-based suspicion score, and going against it is usually wrong.** The ballot prompt shows the voter's rule-kept suspicion of every player ([`agents/memory/`](agents/memory/)). Crew votes for the highest-rated player hit an impostor [215 of 235 times](eval/reports/process-scorecard.md) (91%); the 56 against it hit one twice (4%), where chance is about one in three.
2. **Meetings with a reported vent sighting never ejected a crewmate.** A vent claim counts only when the engine's witness record matches it. In the 24 meetings with one, every ejection removed an impostor; in the 95 without, [22 of 37](eval/reports/gameplay-census.md) did and 15 removed crewmates, near a coin flip: hard evidence, not general social deduction.
3. **Every vote to eject cites a real line.** [394 of 397](eval/reports/process-scorecard.md) votes to eject cite something the voter saw or heard; most of those lines are other players' claims, which can be lies, and the ballot demands a citation, so this is by design.

*Before* is each set's previously shown recording, copied from its record.

| What | Figure | Before | Recorded on, and where it lives |
|---|---|---|---|
| Sample games that replay byte for byte | 100 of 100 (100%) | 100 of 100 (100%) | `scripts/verify_samples.sh`; in CI, a [gate test](tests/api/test_replay_loader.py) for the 9-player set |
| Eject ballots citing what the voter saw or heard about the accused (9p2i) | 394 of 397 (99%) | 407 of 410 (99%) | [process scorecard](eval/reports/process-scorecard.md); a floor: the ballot asks every eject to cite |
| Crew eject ballots naming someone other than the voter's [top suspect](docs/glossary.md#top-suspect-the-player-a-voters-own-suspicion-rates-highest) (9p2i) | 56 of 291 (19%) | 65 of 292 (22%) | [process scorecard](eval/reports/process-scorecard.md) |
| Ballots with no stated reason (9p2i) | 6 of 702 (1%) | 11 of 691 (2%) | [process scorecard](eval/reports/process-scorecard.md) |
| Ballots whose target is the one their voter wrote (9p2i) | 692 of 702 (99%); 10 impostor votes against a partner turned into skips | 674 of 691 (98%) | [process scorecard](eval/reports/process-scorecard.md) |
| Eject ballots with a valid citation of a statement or sighting (9p2i) | 397 of 397 (100%), zero dangling | 410 of 410 (100%), zero dangling | the 2026-10-09 record (9p2i) — [instrument](tests/eval/test_vj_instruments.py) |
| Impostor win rate, sample games | 36% (4p1i), 34% (9p2i) | 36% (4p1i), 48% (9p2i) | the 2026-09-22 record (4p1i), the 2026-10-09 record (9p2i) — [4p1i](replays/samples/4p1i/MANIFEST.md), [9p2i](replays/samples/9p2i/MANIFEST.md) |
| Impostors among those ejected, with and without proof of their role (9p2i) | 24 of 24 (100%) vs 22 of 37 (59%) | 24 of 24 (100%) vs 20 of 42 (48%) | the 2026-10-09 record (9p2i) — [gameplay census](eval/reports/gameplay-census.md); 15 of 15 innocent ejections sit in the no-proof cell |
| Impostors ejected after a reported sighting of them venting (9p2i) | 24 of 46 (52%) | 24 of 44 (55%) | the 2026-10-09 record (9p2i) — [gameplay census](eval/reports/gameplay-census.md). Reading: general social deduction, **not** demonstrated |

*Valid* means resolvable, not supported.

## Limitations

- **One model, one recording per round.** One open model and prompt set, recorded once per round, so no figure ranks one version above another.
- **Learned policies stayed off.** Four learned impostor policies won more games than the scripted one and still failed gates written before measuring ([negative results](docs/ml-program.md)).
- **Reproducibility has limits.** Recordings always reconstruct; fake-provider runs repeat on one machine; real-model games are not deterministic.
- **Targets were missed twice.** I adopted the first recording anyway, in writing, and nothing from the second ([what each measured](process/README.md#evidence-honesty-phase-20)).
- **One known leak.** In the 2026-09-22 recordings the opening prompts name each body by a label that reveals when it died; the shown 9-player set no longer carries it. The full repair stays switched off ([observation contract](docs/observation-contract.md)).

## The recordings

A clone includes 100 sample replays under `replays/samples/`: two 50-game tournaments played by the `Qwen/Qwen3.6-27B` model. The 4-player set was regenerated 2026-09-22 (4p1i) with every experimental switch off ([its record](process/audits/audit-2026-09-22-process-rerecord.md)): impostor win rate 36% (4p1i). The 9-player set was regenerated 2026-10-09 (9p2i) under the adopted gameplay changes plus the [route lines](docs/glossary.md#route-line-what-the-doors-say-about-a-players-stated-places), a recorded setting ([its record](process/audits/audit-2026-10-09-stage-b-r3.md)): impostor win rate 34% (9p2i). Each set's manifest lists its prompt versions game by game ([4p1i](replays/samples/4p1i/MANIFEST.md), [9p2i](replays/samples/9p2i/MANIFEST.md)). The README's pictures show the 9-player game the guided tour opens on.

The README's pictures show 9p2i seed 19, the game the demo's guided tour opens on, from the 2026-10-09 record (9p2i); [media provenance](docs/media/README.md#provenance) records its source and asset identities.

**The fake provider's report is empty on purpose:** it returns one fixed reply, so every meeting skips and nothing is ejected. A real report, gzipped at [replays/samples/9p2i/tournament-eval-report.json.gz](replays/samples/9p2i/tournament-eval-report.json.gz), records 61 ejections; 46 removed an impostor, 36 of those 46 with evidence against that player on the meeting's record.

## Where the figures come from

The [demo](https://dkdan10.github.io/AiLibi/) carries all 100 games and replays them in the browser with no server and no model calls. One of five import contracts keeps [`agents/`](agents/) out of the engine; [a test](tests/test_firewall.py) plants a forbidden import that must fail. The recordings re-verify offline:

```bash
# Re-run the 200 sample and candidate recordings (about 20 s).
UV_OFFLINE=1 bash scripts/verify_samples.sh
```

[Process scorecard](eval/reports/process-scorecard.md) · [Gameplay census](eval/reports/gameplay-census.md) · [Reading guide](docs/reading-guide.md) · [Glossary](docs/glossary.md) · [Audits](process/audits/README.md)
