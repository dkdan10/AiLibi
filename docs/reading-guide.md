# Reading guide — the outsider's five minutes

Five minutes, no context: which numbers are real and where they are committed,
what to run, what the corpus does and does not demonstrate, and which three
audits to read first. Every number carries the path that owns it, and where this
page summarizes, the cited file wins. Private vocabulary is in the
[glossary](glossary.md); the phase narrative in [history](history.md).

---

## 1. The numbers worth knowing

The middle column is the current reference recording, made 2026-08-25; beside it
is the recording it replaced. Where the two agree, nothing moved.

| What | Figure | At baseline 6 | Recorded on, and where it lives |
|---|---|---|---|
| Committed sample replays that reconstruct byte-identically | 100 of 100 | 100 of 100 | every commit — `bash scripts/verify_samples.sh` |
| Observation-firewall violations, all phases | zero | zero | never breached in CI — the three mechanisms are named below |
| Impostor win rate, committed samples | 36% (4p1i), 24% (9p2i) | 34% (4p1i), 30% (9p2i) | the 2026-08-25 record — [4p1i](../replays/samples/4p1i/MANIFEST.md), [9p2i](../replays/samples/9p2i/MANIFEST.md) |
| Eject ballots carrying a valid citation, a turn or an observation id (9p2i) | 538 / 538, zero dangling | 520 / 520, zero dangling | reference recording 7, 2026-08-25 — [instrument](../tests/eval/test_vj_instruments.py) |
| Ejection accuracy with engine-certified proof of the ejectee's role, against without | 326 / 326 = 1.0000 vs 61 / 103 = 0.5922 | 310 / 310 = 1.0000 vs 46 / 125 = 0.3680 | the 2026-08-25 record, pooled over four recorded sets — [the record](../audits/audit-phase-20-baseline-7.md) §3, against [phase-19 close](../audits/audit-phase-19-close.md) §4.1 |
| Correct 9p ejections riding an ejectee-specific vent sighting | 69 / 85 = 81% | 68 / 78 = 87% | reference recording 7, 2026-08-25 — the cross-tab in §3, [pinned](../tests/eval/test_deduction_metrics.py) |
| Impostor ballots cast against a partner (9p2i) | 0 of 219 | 0 of 245 | enforced by the meeting layer, not shown by the model — §3 |
| Pre-registered emergence rulings demonstrated, phase 18 | 0 of 14 | 0 of 14 | [close audit](../audits/audit-phase-18-close.md), derived in [the emergence reading](../audits/audit-phase-18-flip-emergence.md) |
| Learned tactical policies that became the default | none, ruled twice | none, ruled twice | [phase 17](../audits/audit-phase-17-close.md), [18](../audits/audit-phase-18-close.md) |

The bars this recording was measured against were registered before the repairs
that would be measured on it, and two of them were missed: conviction accuracy
without engine-certified proof reached 61 of 103 = 0.5922 against a bar of 0.60,
short by 0.0078, and wrongful ejections reached 42 against a bar of fewer than
35. The rule's verdict is therefore a **finding**, not an adoption. This
recording is the reference in spite of it, by an explicit owner override of that
verdict recorded with its grounds on 2026-08-26 — see §6.1 of
[the record](../audits/audit-phase-20-baseline-7.md), and read it before citing
any row above as a pass.

**How the firewall claim is enforced.** Three mechanisms: the
[import-linter contracts](../.importlinter), the planted-leak test in
[tests/test_firewall.py](../tests/test_firewall.py), and the recursive packet
sweep in [eval/leak_scan.py](../eval/leak_scan.py). The contracts list every
top-level package that ships or gates shipping as a root, because the graph
builder builds nodes only for roots and a traversal stops at the first hop into
a package it does not know — a root left out is a hole in the transitive claim.
The planted-leak test writes its bad imports into a temporary copy of the tree,
never the checkout, and parses the committed configuration, so a contract added
there is exercised without editing the test.

## 2. What to run, and what to watch

```bash
git clone --filter=blob:none https://github.com/dkdan10/AiLibi.git && cd AiLibi
bash scripts/setup_env.sh      # one-time: Python deps + npm ci in frontend/
bash scripts/run_spectator.sh  # API + UI, opens http://localhost:5173
```

The served default is the 9-player, 2-impostor set, the one with meetings and
suspicion arcs; the 4-player set is a fast fixture of short games. The curated
list the guided tour opens is hand-picked, not scored, and spoiler-free.

Three of those curated games are the ones to open first, each re-read on the
2026-08-25 bytes: **9p2i seed 23**, twenty-six spoken turns over four meetings,
whose one traced injustice — a crewmate convicted on a sighting its speaker
could not have made — is gone, that meeting now carrying no flags at all and
ejecting nobody; **9p2i seed 46**, four meetings and exactly one flag in the
whole game, and that one a pair of conflicting accounts rather than anything the
engine certified; and **4p1i seed 11**, one meeting and three turns with nothing
flagged at all, where the crew's own reading is the only thing on the table.

One qualification, the seam the project turns on: a flag is a contradiction the
meeting layer *detected*, not a fact the engine *certified*. The ballot now says
which is which — engine-certified role proof above two accounts that cannot both
be true, with the detector's own weak stamp below them — where earlier
recordings dressed every flag alike as verified proof, and the crew convicted on
the difference.

## 3. What the corpus demonstrates — and what it does not

**Evidence-processing: demonstrated.** Deliberation is typed, and all 538 eject
ballots in the 9p2i samples cite a line the voter could really see.

**Deception: demonstrated, and the strongest capability on display.**
Coordinated fabricated alibis built by reading the transcript, strategic
truth-telling at parity, verbal betrayal of a caught partner while the ballot
skips. One guard belongs with the zero-betrayal-votes row above: a ballot
targeting a fellow impostor is rewritten to SKIP, so that zero is the teammate
firewall holding, not restraint the model showed.

**General social deduction: NOT demonstrated.** A *flag* is a contradiction the
meeting layer detects and shows the voters; a vent flag is the one class only an
impostor can produce, resting on an engine-certified observation. Over all 152
committed 9p2i meetings:

| Meeting contains a vent flag | impostor ejected | innocent ejected |
|---|---|---|
| yes (69 meetings) | 69 | 0 |
| no (83 meetings) | 16 | 14 |

With the certified evidence in front of it the table never convicted a crewmate.
Without it, ejection accuracy is close to a coin flip — 16 of 30 — which is why
the pre-registered bar for exactly this cell, 0.60 pooled across the four
recorded sets, is one of the two the recording missed. What the recording did
close is the worst of the evidence itself: the class of flag that convicted 70
innocents on a single alibi-versus-sighting is empty on these bytes, and so is
the adjacent-room class that supplied it, both by extinction rather than by
waiver ([the record](../audits/audit-phase-20-baseline-7.md) §3, bars 4 and 7).

## 4. Three audits, in this order

1. [audit-phase-19-input-claude.md](../audits/audit-phase-19-input-claude.md) —
   an independent audit from a fresh clone. **What it proves:** a stranger can
   reproduce every derived metric from the committed raw bytes.
2. [audit-phase-19-triage.md](../audits/audit-phase-19-triage.md) — its
   reconciliation against a second, independent audit by a different model.
   **What it proves:** disagreements are ruled on evidence, and one of its own
   sources' headline terms is refuted rather than absorbed.
3. [audit-phase-18-close.md](../audits/audit-phase-18-close.md) — the close of
   the ML program. **What it proves:** the machinery holds under a result nobody
   wanted. Every learned arm beat the scripted comparator on wins and failed the
   pre-registered selection gate, so none became the default.

The commissioned audits are AI auditors, not third parties, and every gameplay
and ML number here comes from one model on one prompt set at 50 games per set.

The ML program in research shape — problem, environment, method, one results
table, the two behavioural findings, and what is wrong with the measurement — is
[ml-program.md](ml-program.md).

## 5. Where to go next

[Architecture](architecture.md) · [glossary](glossary.md) ·
[history](history.md) · [audits index](../audits/README.md) ·
[workflow protocol](../AGENTS.md) · [design history](../DESIGN.md) ·
[deployment](deployment.md) · [artifacts](artifacts.md).
