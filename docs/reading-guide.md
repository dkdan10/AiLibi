# Reading guide — the outsider's five minutes

Five minutes, no context: which numbers are real and where they are committed,
what to run, what the corpus does and does not demonstrate, and which three
audits to read first. Every number carries the path that owns it, and where this
page summarizes, the cited file wins. Private vocabulary is in the
[glossary](glossary.md); the phase narrative in [history](history.md).

---

## 1. The numbers worth knowing

| What | Figure | Recorded on, and where it lives |
|---|---|---|
| Committed sample replays that reconstruct byte-identically | 100 of 100 | every commit — `bash scripts/verify_samples.sh` |
| Observation-firewall violations, all phases | zero | never breached in CI — the three mechanisms are named below |
| Impostor win rate, committed samples | 36% (4p1i), 24% (9p2i) | the 2026-08-25 record — [4p1i](../replays/samples/4p1i/MANIFEST.md), [9p2i](../replays/samples/9p2i/MANIFEST.md) |
| Eject ballots carrying a valid citation, a turn or an observation id (9p2i) | 520 / 520, zero dangling | reference recording 6, 2026-07-20 — [instrument](../tests/eval/test_vj_instruments.py) |
| Ejection accuracy with engine-certified proof of the ejectee's role, against without | 310 / 310 = 1.000 vs 46 / 125 = 0.368 | measured 2026-08-18 across all four committed recordings — [phase-19 close](../audits/audit-phase-19-close.md) §4.1 |
| Correct 9p ejections riding an ejectee-specific vent sighting | 68 / 78 = 87% | reference recording 6, 2026-07-20 — [triage audit](../audits/audit-phase-19-triage.md) §8 |
| Impostor ballots cast against a partner (9p2i) | 0 of 245 | enforced by the meeting layer, not shown by the model — §3 |
| Pre-registered emergence rulings demonstrated, phase 18 | 0 of 14 | [close audit](../audits/audit-phase-18-close.md), derived in [the emergence reading](../audits/audit-phase-18-flip-emergence.md) |
| Learned tactical policies that became the default | none, ruled twice | [phase 17](../audits/audit-phase-17-close.md), [18](../audits/audit-phase-18-close.md) |

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

Three seeds are the exhibits the audits traced case by case: **9p2i seed 17**,
an impostor pair fabricating a sighting against a truthful vent witness; **9p2i
seed 23**, a claim that is factually true but provenance-impossible passing
unchallenged; and **4p1i seed 41**, the one meeting an LLM tie-break decided.

One qualification, the seam the project turns on: the "VERIFIED" stamp a voter
sees is applied by the ballot prompt over a flag minted in the meeting layer.
The engine certifies the vent *observation* under a vent flag; it never
certifies the fabricated testimony seed 17 turns on.

## 3. What the corpus demonstrates — and what it does not

**Evidence-processing: demonstrated.** Deliberation is typed, and all 520 eject
ballots in the 9p2i samples cite a line the voter could really see.

**Deception: demonstrated, and the strongest capability on display.**
Coordinated fabricated alibis built by reading the transcript, strategic
truth-telling at parity, verbal betrayal of a caught partner while the ballot
skips. One guard belongs with the zero-betrayal-votes row above: a ballot
targeting a fellow impostor is rewritten to SKIP, so that zero is the teammate
firewall holding, not restraint the model showed.

**General social deduction: NOT demonstrated.** A *flag* is a contradiction the
meeting layer detects and shows the voters; a vent flag is the one class only an
impostor can produce, resting on an engine-certified observation. Over all 165
committed 9p2i meetings:

| Meeting contains a vent flag | impostor ejected | innocent ejected |
|---|---|---|
| yes (70 meetings) | 68 | 2 |
| no (95 meetings) | 10 | 21 |

Without hard evidence, ejection accuracy is roughly chance and innocents go down
two to one. Two limits ride with that: an alibi-versus-sighting flag juxtaposes
two *unverified* model-authored statements and is still labelled verified to the
voters, and about 40% of directional flag subjects in 9p2i are innocents. Both
are traced case by case in the first audit below.

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
