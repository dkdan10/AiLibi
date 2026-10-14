# Reading guide — the outsider's five minutes

Numbers, reproduction commands, findings, and starting points. Cited sources
outrank summaries. See the [glossary](glossary.md) for terms and
[history](../process/README.md) for earlier phases.

---

## 1. The numbers worth knowing

The headline figures, each beside what the previously shown recording read,
are in the results table of the [README](../README.md); two more follow.

| What | Figure | Before | Where it lives |
|---|---|---|---|
| Impostor ballots cast against a partner (9p2i) | 0 of 198 (0%) | 0 of 200 (0%) | enforced by the meeting layer, not shown by the model — §3 |
| Learned behaviours the ML program set out to show | 0 of 14 (0%) | 0 of 14 (0%) | [close audit](../process/audits/audit-phase-18-close.md), derived in [the emergence reading](../process/audits/audit-phase-18-flip-emergence.md) |

## 2. What to run, and what to watch

Open the [recorded demo](https://dkdan10.github.io/AiLibi/) without installing.
For prerequisites and the offline checks, follow the
[README](../README.md#run-it).

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
[the fresh-clone audit](../process/audits/audit-phase-19-input-claude.md#53-what-is-genuinely-good)
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
on baseline 7 ([its record](../process/audits/audit-phase-20-baseline-7.md) §3) and
convicted four again on baseline 8
([its record](../process/audits/audit-phase-21-rerecord.md) §5.1.1); later records do
not re-read it.

## 4. Four audits, in this order

1. [The finished-state audit of 2026-10-10](../process/audits/audit-2026-10-10-finalized-state.md).
   **What it proves:** what the finished project shows and does not, each
   figure with its command.
2. [The fresh-clone audit](../process/audits/audit-phase-19-input-claude.md). **What it
   proves:** a stranger can reproduce every derived metric from the committed
   bytes.
3. [Its reconciliation with a second model's audit](../process/audits/audit-phase-19-triage.md).
   **What it proves:** disagreements are ruled on evidence; a source's headline
   term is refuted rather than absorbed.
4. [The ML program's close](../process/audits/audit-phase-18-close.md). **What it
   proves:** the machinery holds under a result nobody wanted: every learned arm
   beat the scripted comparator on wins and failed the selection gate.

The commissioned audits are AI auditors, not third parties, and every gameplay
and ML number here comes from one model and prompt set at 50 games per set.

The ML program's method, results and measurement flaws are in
[ml-program.md](ml-program.md).

## 5. Where to go next

[Architecture](architecture.md) · [glossary](glossary.md) ·
[history](../process/README.md) · [audits index](../process/audits/README.md) ·
[ownership decision](lessons.md#one-decision-traced) · [workflow protocol](../AGENTS.md) · [design history](../process/DESIGN.md) ·
[deployment](deployment.md) · [artifacts](artifacts.md).
