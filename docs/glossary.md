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

An AI coding agent (Claude or Codex) implementing or reviewing a scoped work
card. The same word also describes players in the simulated game. Where both senses are
in play, the game's are **crewmate** and **impostor**.

---

## How the records are kept

### baseline N (the reference recording)

A numbered reference recording: one recording of the sample sets under a stated
set of behavioural settings, which everything afterwards is measured against.
Nine exist; the newest — the ladder tip — is baseline 9, recorded 2026-09-22
([`audits/audit-2026-09-22-process-rerecord.md`](../audits/audit-2026-09-22-process-rerecord.md)).
Since 2026-10-02 the shown 9-player set sits in a later era, recorded with the
adopted gameplay changes, while the 4-player set and the ML corpus stay at
baseline 9.

### era (recordings that share one recorded identity)

A group of committed recordings made under one identity: the same settings,
prompts and temporal delivery. Instruments read an era's sets together and
never pool two eras. [`eval/eras.py`](../eval/eras.py) names two: baseline 9's
owns the 4-player set and the ML corpus, and a later one owns the shown
9-player set, recorded 2026-10-01 with the adopted gameplay changes switched on
by one declared config
([`audits/audit-2026-10-01-stage-b-r2.md`](../audits/audit-2026-10-01-stage-b-r2.md)
§9).

### adopting record (the recording that adopts a change)

The point of a reference recording: it is the recording that *adopts* a
substrate change, not a label applied to one afterwards. So a setting
"graduates at its own adopting record" — the change and the recording that
makes it canonical are the same event
([`audits/audit-phase-17-absence-gate.md`](../audits/audit-phase-17-absence-gate.md)).

### the ladder tip (the newest reference recording)

Where the substrate currently stands. "The ladder tip stands at baseline 9"
([`audits/audit-2026-09-22-process-rerecord.md`](../audits/audit-2026-09-22-process-rerecord.md)); the
phrase is checked against that audit by
[`scripts/check_doc_facts.py`](../scripts/check_doc_facts.py), so no document
can quietly name a different one. The shown 9-player set moved to a later era
on 2026-10-02 without moving the tip: no substrate setting changed, and
baseline 10 is reserved for a full re-record.

### graduated lever (a setting deleted into the default)

A behavioural change ships behind an `AILIBI_*` environment gate, then
*graduates* at a reference recording: the gate is deleted, the behaviour becomes
unconditional, and the key survives only in the recording stamp for provenance.
Twenty-one have graduated; five live substrate toggles remain — `impostor_roll_call`,
`reporter_reasoning`, `corroboration_discipline`, `testimony_shapes`,
`temporal_observations`
([`orchestrator/replay.py`](../orchestrator/replay.py));
graduating requires deleting the mechanism and updating current prose
([retirement procedure](agent-procedures.md#retiring-substrate-levers)).
Separately versioned cleanup experiments use the closed recording configuration
described in [architecture](architecture.md); they do not inflate this registry.

A *repair* gate is not a lever and graduates differently: it records no arm and
nothing is decided on it, so at its record it is deleted outright and promoted
nowhere, which leaves the graduated-lever stamp keys — and the MANIFEST `flags`
cell derived from them — byte-identical across the flip.

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
200 games against the 100 sample games. Using a bigger denominator than the sets a
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
([`meetings/transcript.py`](../meetings/transcript.py)). A `vent_sighting` flag identifies an impostor subject when a speaker’s vent
claim matches their witnessed record. The speaker need not be an impostor.

### hard evidence (certified role evidence)

In this game's rules, an attributed witnessed vent or kill establishes an
impostor role, but the meeting layer certifies only the vent. It grounds a
spoken vent claim against the speaker's own witness record before publishing a
`vent_sighting` proof flag ([meeting detector](../meetings/transcript.py),
`detect_contradictions`). A witnessed kill stays with its witness: it enters the
witness's own memory and raises the witness's own suspicion of the killer
(`WITNESSED_KILL_SUSPICION_DELTA` in
[`agents/memory/beliefs.py`](../agents/memory/beliefs.py)). It publishes no flag,
because no contradiction kind names a kill (`ContradictionRef.kind` in
[`meetings/schemas.py`](../meetings/schemas.py)), and it adds no row to the
witness's ballot evidence (`_own_channel_evidence_rows` in
[`meetings/manager.py`](../meetings/manager.py)). Other spoken placements,
contradictions and agreement are different evidence classes; a citation alone
does not certify their inference
([observation contract](observation-contract.md)).

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

After the opening, reply chain and information-sharing rounds, the remaining
silent living players receive a whereabouts turn before voting. This gives
otherwise unheard players an opportunity to state an account
([`meetings/manager.py`](../meetings/manager.py)).

### kill cooldown

The ticks an impostor must wait before it can kill. It is set at round start,
after each of the impostor's own kills and after a regroup, and it counts down
one tick at a time during play. Its value is the map's (4 ticks on the canonical
map) unless a recording sets another with the recorded setting
`kill_cooldown_ticks`
([`engine/world.py`](../engine/world.py),
[experiment arms](experiment-arms.md)).

### regroup (the full meeting reset)

What a meeting's close does under the recorded setting
`meeting_reset = hub_with_grace`, when the meeting did not end the game. Every
living player is placed in the meeting room; every corpse is cleared, reported
or not; an impostor inside a vent is brought out; ongoing actions stop; and each
living impostor's kill cooldown restarts at its full value, the map's unless the
recording sets another, so no kill is possible for that many ticks after the
meeting. Task progress, button uses and
an active sabotage survive it. The relocation is announced, not walked: every
living player's memory records it, states it beside the meeting record and as
its own step in the player's route. The first observations after it carry only
the kills, vent entries and vent exits seen on the tick the meeting was called,
because those were seen where they happened; a walk or a task step from that
tick is not replayed from the meeting room. A sighting on the regroup's tick or
the tick after it counts as evidence neither for nor against anyone's alibi,
except under the recorded `attributed_testimony_version` setting, whose
comparison of spoken accounts reads no such window and can hold that sighting
against the account of a player the regroup moved.
The setting is off by default
([`engine/meeting_reset.py`](../engine/meeting_reset.py),
[observation contract](observation-contract.md#the-regroup-reset),
[experiment arms](experiment-arms.md)).

### endpoint-band whereabouts exemption

The rule that a whereabouts claim is not treated as contradicted when the two
statements differ only at the ends of the interval each covers — a player who
says "Engineering" for ticks 4–8 and one who saw them leave at tick 8 are not in
conflict ([`meetings/transcript.py`](../meetings/transcript.py)).

### absence prior

The starting assumption a table brings to a player nobody can place: absence is
weak evidence, weighted rather than ignored
([`audits/audit-phase-17-absence-gate.md`](../audits/audit-phase-17-absence-gate.md)).

### stated basis (what a voter says its vote rests on)

One field the voter fills on its own ballot. It reads `cited` when the voter put
a transcript turn or one of its own memory lines in the ballot's citation slots,
and `none_held` when it says outright that it holds nothing that resolves.
Empty means the voter answered the question with nothing at all, which is a
different record from saying it holds nothing
([`meetings/schemas.py`](../meetings/schemas.py)).

### grounding label (what the meeting found under a ballot)

The meeting's own one-word finding about that basis, written after the vote and
onto the record beside it. It **describes** and never corrects: the recorded
vote stays the one the voter cast, and the tally never reads the label. The
seven values are `supported` (a citation survived and is about the right player
— for an ejection that is the player it names, and for a skip it is one of the
alternatives the voter weighed, or any living candidate when it weighed none),
`off_target` (it survived but is about somebody else),
`invalid_citation` (the voter cited something that matched nothing on record),
`none_held` (the voter said so), `flag_only` (an ejection whose target carries a
contradiction raised at that meeting, and nothing else), `uncited` (nothing
cited and nothing said), and `not_assessed` (the meeting itself set this vote,
so there is no voter decision to assess)
([`meetings/manager.py`](../meetings/manager.py)).

### route line (what the doors say about a player's stated places)

One line of a ballot's `<routes>` block, served only under the recorded setting
`route_lines_version`. For one living candidate whose places stated at the table
change room, it lists each change the station's doors or the public regroup
allow: the rooms and ticks, the doors between the rooms, and either that walking
fits (the doors are at most the ticks between) or the regroup tick that falls
between, which walking cannot decide. A change of room that neither allows is
left out, so a line never says a move was impossible, and a candidate with no
allowed change has no line. The line reads statements only, so a lie stated at
the table yields a line as plain as an honest account; it is the same for every
voter and every role, and it names, ranks and recommends no one
([`meetings/route_lines.py`](../meetings/route_lines.py),
[experiment arms](experiment-arms.md)).

### game-shape profile (shelves, facets and the tripwire)

The game-shape profile is how the owner chose, on 2026-10-06, to have the replay
viewer describe each game of the shown 9-player set without a score or a rank
([decision memo](../tasks/decision-2026-09-24-stage-b-wave.md), section 8.6): a
**facet** is a plain fact every game has, such as its length, its meetings or
when its kills fell; a **shelf** is a named kind of moment to browse by, such as
a double kill or a close vote, listing its games by seed number and never by
rank and, when it reads a player's role or could give the ending away, hidden
until the viewer chooses to reveal the outcome; and the **tripwire** keeps a
game off every shelf, though never out of the list of all games, when a player
was voted out by ballots that rested on nothing the table held about them and
without which the meeting would have decided otherwise, or on a contradiction
raised against an account that was in fact true. The profile is version 2 of the
rubric: version 1, the interestingness score, is retired for the shown era and
kept as history. It is computed after the fact from committed bytes, a **chip**
marks one meeting, and no agent, pre-registration, step rule, gate or objective
reads any of it ([the generated page](game-profile.md),
[`eval/game_profile.py`](../eval/game_profile.py)).

### the shelves (the moments a game can sit on)

Before the reveal: *The reporter saw it happen* (the player who reported the body
was among the engine's witnesses of that kill), *Double kill*, *Slow burn* (a
long stretch with no kill), *Two kills after one regroup*, *A close call* (a
meeting decided by one ballot or a tie), *Suspicion moved* (read from ballots and
accusations, never from the engine's suspicion number) and *A third round*.
Behind the reveal: *Caught venting* and *One line, two readings* (two ballots
citing the same turn and reaching different decisions), which the leak rule moved
there on the shown set, *One-vote ejection*, *Nobody voted out*, *Down to the
wire*, *Runaway*, *Decided at a meeting*, and the pair *decided without proof*.
Each shelf lists its games by seed number; the generated page defines each one.

### eyewitness chip ("An eyewitness voted on it")

A mark on a meeting where some player's ballot cites the row of its own ballot
prompt saying it watched a kill. It names the meeting, places the game on no
shelf and is not leak-tested.

### tripwire (a vote that held nothing, or a manufactured contradiction)

The check that keeps a game off every shelf, though never out of the list of all
games, where it carries a plain label. It trips when removing the ejecting
ballots that cited nothing the voter held, or cited somebody else, would have
left the meeting ejecting no one or someone else, or when the ejected player was
named by a contradiction raised against an account that was in fact true. The
stricter and looser counts are published beside it. The second half can judge
few contradictions, and the page says so.

### decided without proof (right, and wrong on what it held)

An ejection whose ejecting ballots all rest on evidence the voters held, with no
vent sighting and no contradiction of the kind above naming the ejected player.
Behind the reveal it splits by the ejected player's role into two halves that are
always shown together: *the table was right*, and *wrong on what it held*.

### wrong on what it held

The half of *decided without proof* where the voters cited lines they held and
the lines pointed the wrong way. A wrong call on believable evidence is part of
the game, so it is shown as the game working, always beside its right twin, and
reported, never a gate. The profile reads the grounding labels, not whether the
cited line was true.

### leak rule

A candidate shelf goes behind the reveal for an era when a two-sided Fisher exact
test of its membership, against each recorded ending, against some meeting having
ejected someone or against a crewmate having been ejected, over every game of the
era, gives any p below 0.05. A game on a tripwire counts as off the shelf. The
rule is recomputed per era, recorded in the served file, and can only hide more.

### saturation rule

A candidate holding more than three quarters of an era's games is a facet, never a
shelf. It is applied before the leak rule.

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
