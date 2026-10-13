# Reading guide — the outsider's five minutes

Numbers, reproduction commands, findings, and starting points. Cited sources
outrank summaries. See the [glossary](glossary.md) for terms and
[history](history.md) for earlier phases.

---

## 1. The numbers worth knowing

The shown 9-player set was recorded 2026-10-09 under the adopted gameplay
changes; the 4-player set and the ML training games were recorded 2026-09-22.
Before is each set's previously shown recording.

| What | Figure | Before | Recorded on, and where it lives |
|---|---|---|---|
| Sample games that replay byte for byte | 100 of 100 (100%) | 100 of 100 (100%) | `scripts/verify_samples.sh`; in CI, a [gate test](../tests/api/test_replay_loader.py) for the 9-player set |
| Observation boundary checks | import rules and planted/recursive leak checks | import rules and planted/recursive leak checks | bounded mechanisms, described below |
| Eject ballots citing what the voter saw or heard about the accused (9p2i) | 394 of 397 (99%) | 407 of 410 (99%) | [process scorecard](process-scorecard.md); a floor: the ballot asks every eject to cite |
| Crew eject ballots naming someone other than the voter's [top suspect](glossary.md#top-suspect-the-player-a-voters-own-suspicion-rates-highest) (9p2i) | 56 of 291 (19%) | 65 of 292 (22%) | [process scorecard](process-scorecard.md) |
| Ballots with no stated reason (9p2i) | 6 of 702 (1%) | 11 of 691 (2%) | [process scorecard](process-scorecard.md) |
| Ballots whose target is the one their voter wrote (9p2i) | 692 of 702 (99%); 10 impostor votes against a partner turned into skips | 674 of 691 (98%) | [process scorecard](process-scorecard.md) |
| Eject ballots with a valid citation of a statement or sighting (9p2i) | 397 of 397 (100%), zero dangling | 410 of 410 (100%), zero dangling | the 2026-10-09 record (9p2i) — [instrument](../tests/eval/test_vj_instruments.py) |
| Impostor win rate, sample games | 36% (4p1i), 34% (9p2i) | 36% (4p1i), 48% (9p2i) | the 2026-09-22 record (4p1i), the 2026-10-09 record (9p2i) — [4p1i](../replays/samples/4p1i/MANIFEST.md), [9p2i](../replays/samples/9p2i/MANIFEST.md) |
| Impostors among those ejected, with and without proof of their role (9p2i) | 24 of 24 (100%) vs 22 of 37 (59%) | 24 of 24 (100%) vs 20 of 42 (48%) | the 2026-10-09 record (9p2i) — [the record](../audits/audit-2026-10-09-stage-b-r3.md) §12.5, against [round 2's](../audits/audit-2026-10-01-stage-b-r2.md) §9.6 |
| Impostors ejected after a reported sighting of them venting (9p2i) | 24 of 46 (52%) | 24 of 44 (55%) | the 2026-10-09 record (9p2i) — the cross-tab in §3, [pinned](../tests/eval/test_deduction_metrics.py) |
| Impostor ballots cast against a partner (9p2i) | 0 of 198 (0%) | 0 of 200 (0%) | enforced by the meeting layer, not shown by the model — §3 |
| Learned behaviours the ML program set out to show | 0 of 14 (0%) | 0 of 14 (0%) | [close audit](../audits/audit-phase-18-close.md), derived in [the emergence reading](../audits/audit-phase-18-flip-emergence.md) |
| Learned tactical policies that became the default | none, ruled twice | none, ruled twice | [phase 17](../audits/audit-phase-17-close.md), [18](../audits/audit-phase-18-close.md) |

Two of baseline 7's pre-registered bars missed: conviction accuracy without
engine-certified proof reached 61 of 103 = 0.5922 against a bar of 0.60, and
wrongful ejections reached 42 against a bar of fewer than 35. That read was a
**finding**; the recording became the reference by an explicit owner override
dated 2026-08-26 ([the phase-20 record](../audits/audit-phase-20-baseline-7.md)
§6.1). Baseline 8 registered no bars and read 50 of 96 = 0.5208 and 46 innocent
ejections. An experiment on it met three of four fresh bars:
innocent ejections fell from 46 to 20, and 11 of those 20 were the meeting's own
reporter, against 34 of 46 — a share of 0.5500 against a registered 0.40, so a
**finding** again, and nothing was adopted
([the record](../audits/audit-phase-21-adopting-record.md)). Baseline 9
registered none and read 43 of 85 = 0.5059 and 42 innocent ejections over its
four recorded sets.

**What the boundary checks cover.** The
[import-linter contracts](../.importlinter), the
[planted-leak test](../tests/test_firewall.py) and the recursive
[packet sweep](../eval/leak_scan.py) test imports and entitled
packets. They do not establish complete privacy: in the 2026-09-22 recordings,
the opening prompts name each body by a label that reveals when it died; the
shown 9-player set's report openings no longer carry it (0 of 115). The full
repair stays switched off. The
[observation contract](observation-contract.md) states the exact boundary.

## 2. What to run, and what to watch

Open the [recorded demo](https://dkdan10.github.io/AiLibi/) without installing.
For prerequisites and the offline checks, follow the
[README](../README.md#install-then-verify-offline).

```bash
git clone --filter=blob:none https://github.com/dkdan10/AiLibi.git && cd AiLibi
bash scripts/setup_env.sh      # one-time: Python deps + npm ci
bash scripts/run_spectator.sh  # API + UI, opens http://localhost:5173
```

The served default is the 9-player, 2-impostor set; the 4-player set is a
fast fixture of short games. The games the guided tour can open are
spoiler-free; the tour opens game 19 at its start, and Play stops at its
first meeting, which ejects a player a reported vent sighting names.

**Results** shows each set's figures, and source-bound cases from the
first 9-player featured game. Start from the featured games: **9p2i seed 19**
has three meetings, nineteen spoken turns and a reported vent sighting;
**9p2i seed 14** has one meeting, eight turns and no flags; **4p1i seed 11** is
a short comparison: one meeting, three turns, no flags.

Click an exact statement, observation, or flag source to inspect it.
Observation and scene-frame times are labelled separately; private memory needs
the observer's perspective or the omniscient view, and a link never silently
widens fog.

One qualification: a flag is a contradiction the meeting layer *detected*, not
a fact the engine *certified*, and the ballot says which is which.

## 3. What the corpus demonstrates — and what it does not

**Evidence-processing: demonstrated.** Deliberation is typed, and of
all 397 eject ballots in the 9p2i samples, every one cites a line the voter
could really see.

**Deception: demonstrated in earlier recordings**, as
[the fresh-clone audit](../audits/audit-phase-19-input-claude.md#53-what-is-genuinely-good)
verified.
Coordinated fabricated alibis built by reading the transcript, strategic
truth-telling at parity, verbal betrayal of a caught partner while the ballot
skips. One guard belongs with the partner row above: a ballot naming a fellow
impostor is rewritten to SKIP, so that zero is the teammate firewall holding,
not the model's restraint.

**General social deduction: NOT demonstrated.** A *flag* is a contradiction the
meeting layer detects and shows the voters; a vent flag is the one class only an
impostor can produce, resting on an engine-certified observation. Over all 119
committed 9p2i meetings:

| Meeting contains a vent flag | impostor ejected | innocent ejected |
|---|---|---|
| yes (24 meetings) | 24 | 0 |
| no (95 meetings) | 22 | 15 |

With the certified evidence in front of it the table never convicted a crewmate.
Without it, ejection accuracy stays near a coin flip — 22 of 37 — still short
of the pre-registered bar for exactly this cell, 0.60 pooled across the four
recorded sets, one of the two baseline 7 missed. The worst class of evidence,
a single alibi-versus-sighting flag that once convicted 70 innocents, was empty
on baseline 7 ([its record](../audits/audit-phase-20-baseline-7.md) §3) and
convicted four again on baseline 8
([its record](../audits/audit-phase-21-rerecord.md) §5.1.1); later records do
not re-read it.

## 4. Four audits, in this order

1. [The finished-state audit of 2026-10-10](../audits/audit-2026-10-10-finalized-state.md).
   **What it proves:** what the finished project shows and does not, each
   figure with its command.
2. [The fresh-clone audit](../audits/audit-phase-19-input-claude.md). **What it
   proves:** a stranger can reproduce every derived metric from the committed
   bytes.
3. [Its reconciliation with a second model's audit](../audits/audit-phase-19-triage.md).
   **What it proves:** disagreements are ruled on evidence; a source's headline
   term is refuted rather than absorbed.
4. [The ML program's close](../audits/audit-phase-18-close.md). **What it
   proves:** the machinery holds under a result nobody wanted: every learned arm
   beat the scripted comparator on wins and failed the selection gate.

The commissioned audits are AI auditors, not third parties, and every gameplay
and ML number here comes from one model and prompt set at 50 games per set.

The ML program's method, results and measurement flaws are in
[ml-program.md](ml-program.md).

## 5. Where to go next

[Architecture](architecture.md) · [glossary](glossary.md) ·
[history](history.md) · [audits index](../audits/README.md) ·
[ownership decision](ownership-case-study.md) · [workflow protocol](../AGENTS.md) · [design history](../DESIGN.md) ·
[deployment](deployment.md) · [artifacts](artifacts.md).
