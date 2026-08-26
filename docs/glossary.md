# Glossary

This project keeps its records as case law, and case law grows a private
vocabulary. Every term below is one an audit, a contract or a report uses as if
it were common English. Where a convention was originally named after the task
that introduced it, the descriptive name is the heading and the old name is
given inside the entry — the descriptive one is what the prose should say from
here on.

Each entry names one committed usage you can go and read.

The route: [README](../README.md) → [reading guide](reading-guide.md) → this
page when a word stops you.

---

## Who is who

### owner

Me — Daniel Keinan, the one human on the project. The contracts and audits say
"the owner" because they are written for agents, who need a single word for
"the party whose merge decides". An owner ruling is a decision no gate can make:
which route a phase takes, whether a measured miss is acceptable, whether a
learned policy ships. Usage: the phase-19 close routes its open decision to the
owner ([`audits/audit-phase-19-close.md`](../audits/audit-phase-19-close.md)).

### agent

An AI coding agent (Claude Code, or Codex for review) working one task contract
in a fresh checkout — not a player in the simulated game. Where both senses are
in play, the game's are **crewmate** and **impostor**.

---

## How the records are kept

### baseline N (the reference recording)

A numbered reference recording: one recording of the sample sets under a stated
set of behavioural settings, which everything afterwards is measured against.
Seven exist; the newest — the ladder tip — is baseline 7, recorded 2026-08-25
([`audits/audit-phase-20-baseline-7.md`](../audits/audit-phase-20-baseline-7.md)).

### adopting record (the recording that adopts a change)

The point of a reference recording: it is the recording that *adopts* a
substrate change, not a label applied to one afterwards. So a setting
"graduates at its own adopting record" — the change and the recording that
makes it canonical are the same event
([`audits/audit-phase-17-absence-gate.md`](../audits/audit-phase-17-absence-gate.md)).

### the ladder tip (the newest reference recording)

Where the substrate currently stands. "The ladder tip stands at baseline 7"
([`audits/audit-phase-20-baseline-7.md`](../audits/audit-phase-20-baseline-7.md)); the
phrase is checked against that audit by
[`scripts/check_doc_facts.py`](../scripts/check_doc_facts.py), so no document
can quietly name a different one.

### graduated lever (a setting deleted into the default)

A behavioural change ships behind an `AILIBI_*` environment gate, then
*graduates* at a reference recording: the gate is deleted, the behaviour becomes
unconditional, and the key survives only in the recording stamp for provenance.
Thirteen have graduated and one live toggle remains
([`orchestrator/replay.py`](../orchestrator/replay.py)); graduating obliges a
prose sweep ([AGENTS.md](../AGENTS.md), "Graduation sweeps").

### the flip bar (formerly "the §1.3 bar")

The written bar a learned policy must clear to become the default: close both
evidence-supply gaps *without* surrendering its win edge. Stated in
[`audits/audit-phase-17-close.md`](../audits/audit-phase-17-close.md) §1.3, and
every later ruling reads against it.

### NO-FLIP (the scripted policy stays the default)

The ruling that the flip bar was not cleared, so the scripted policy stays the
default and the learned one stays opt-in. Ruled twice, in the titles of
[`audits/audit-phase-17-close.md`](../audits/audit-phase-17-close.md) and
[`audits/audit-phase-18-close.md`](../audits/audit-phase-18-close.md).

### canary denominator (the held-out monitoring corpus)

The largest same-substrate, validity-gated recording set that monitoring metrics
are judged on — today [`replays/ml_corpus/`](../replays/ml_corpus/README.md),
about three times the sample sets. Using a bigger denominator than the sets a
change was tuned on is the point.

### findings, not failures

The closing doctrine: a pre-registered measurement that misses its bar is a
finding to record, not a failure to hide or re-price. Chartered in
[`tasks/phase-18.md`](../tasks/phase-18.md) and applied in
[`audits/audit-phase-18-close.md`](../audits/audit-phase-18-close.md) §6.

### merge-as-ratification (formerly "the 15.18 convention")

Decision documents — plans, close readings, tier maps — are proposed as pull
requests, and the owner's *merge* is the ratification. Measurements commit their
pre-registration before the measurement and their reproduction snippets beside
the numbers ([`tasks/phase-19.md`](../tasks/phase-19.md)).

### the two-owner gate

A phase's ruling and its close are two separate owner merges, and the close
carries no new evidence — so the second merge ratifies a reading rather than a
surprise ([`tasks/phase-18.md`](../tasks/phase-18.md)).

### errata discipline

Living documentation is rewritten; *records* — campaign reports and audits — are
not. They take additive, dated errata, and later prose quotes only
errata-approved figures
([`training/reports/report-finalist-eval.md`](../training/reports/report-finalist-eval.md)
§18).

### citation shorthand

`§N.M` is a section of the cited document. `F<n>` is a numbered campaign finding
carried between contracts, `L<n>` an item in a ruling's own ledger, and
`P0`–`P2` the input audits' severity ranks. In
[`audits/audit-phase-19-triage.md`](../audits/audit-phase-19-triage.md), `[C]`
marks a finding both external audits reached, `[S-Claude]` / `[S-Codex]` a
single-source one, and `[L]` an internal-ledger-only one — provenance tags, not
verification status.

---

## How a meeting works

### mover (the tactical policy)

The per-tick decision policy that moves a player, does tasks, kills and vents —
as opposed to the LLM that speaks and votes at meetings. The default mover is a
scripted finite-state machine ([`agents/tactical/`](../agents/tactical));
learned movers exist and are opt-in.

### flag-minting (stamping a contradiction into the transcript)

The meeting layer, not the engine, detects contradictions across the transcript
and *mints* a flag the voters can see
([`meetings/transcript.py`](../meetings/transcript.py)). A `vent_sighting` flag
is the one class only an impostor can produce, because it rests on an
engine-certified observation.

### conviction economy (what a meeting does with evidence)

The pipeline from flag to ballot to tally, and how much of the evidence a
meeting is handed it converts into a correct ejection. "Conviction engine" means
this pipeline in [`meetings/`](../meetings), never the [`engine/`](../engine)
package.

### supply and conversion floors

The two halves of that economy, as numbers a recording must clear: how much
usable evidence the meeting is *supplied*, and how much of it the table
*converts*. They are the gauges the referee below prices
([`eval/watchability.py`](../eval/watchability.py)).

### starved-economy shape

The failure pattern where a learned mover wins more games by supplying the
meeting with less evidence — the win edge is real and the deduction gets worse.
First named in
[`audits/audit-phase-17-close.md`](../audits/audit-phase-17-close.md) and
reproduced on a co-adapted slate in
[`audits/audit-phase-18-close.md`](../audits/audit-phase-18-close.md).

### roll-call round (the whereabouts round)

A meeting round in which every living player states where they were, before
anyone is accused, so alibis exist to be checked against
([`meetings/manager.py`](../meetings/manager.py)).

### endpoint-band whereabouts exemption

The rule that a whereabouts claim is not treated as contradicted when the two
statements differ only at the ends of the interval each covers — a player who
says "Engineering" for ticks 4–8 and one who saw them leave at tick 8 are not in
conflict ([`meetings/transcript.py`](../meetings/transcript.py)).

### absence prior

The starting assumption a table brings to a player nobody can place: absence is
weak evidence, weighted rather than ignored
([`audits/audit-phase-17-absence-gate.md`](../audits/audit-phase-17-absence-gate.md)).

---

## The machine-learning program

### arm (one measured configuration)

One configuration under measurement — a policy plus its settings — run over a
fixed seed set so it can be compared against the others and against the scripted
comparator.

### slate (the set of arms in a campaign)

The full set of arms a campaign measures, chosen before the measurement runs
([`audits/audit-phase-18-close.md`](../audits/audit-phase-18-close.md)).

### champion (the best arm, kept opt-in)

The arm a campaign selects. Selection is not adoption: the champion ships behind
a flag and the scripted mover stays the default until the flip bar is cleared
([`training/README.md`](../training/README.md)).

### referee (the selection gate)

The pre-registered gate that decides whether an arm may be adopted. It prices
what a mover does to the deduction economy it plays in, not just whether it
wins, and it is a *selection* gate only — never a training reward
([`eval/watchability.py`](../eval/watchability.py)).

### screening-tier shortlist

A campaign result that is explicitly too small to rule on: the arms are ranked
well enough to shortlist for a bigger run, and no further
([`audits/audit-phase-18-close.md`](../audits/audit-phase-18-close.md)).

### training-time-runner tier

A verdict on a learned component saying it is good enough to drive training
rollouts but not to decide anything in a real game — the two jobs have different
accuracy requirements ([`training/README.md`](../training/README.md)).

### two-axis owner ruling

A close that rules on two independent questions at once — here, "does a learned
mover become the default?" and "was any pre-registered emergence claim
demonstrated?" — so a yes on one cannot be read as a yes on the other
([`audits/audit-phase-18-close.md`](../audits/audit-phase-18-close.md)).

### evidence-gated default flip

The proposal that the learned mover become the default *conditional* on the
evidence gauges, rather than on wins alone. Ruled FAIL in
[`audits/audit-phase-17-close.md`](../audits/audit-phase-17-close.md).

---

Back to the [README](../README.md), the [reading guide](reading-guide.md), or
the [phase history](history.md).
