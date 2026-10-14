# The process record

This folder keeps how AiLibi was built: what the agents were asked to do, how
each result was checked and what the owner decided. It is a record, not a set of
instructions; current work follows [AGENTS.md](../AGENTS.md) and
[the workflow](../docs/workflow.md).

- [`tasks/`](tasks/README.md) holds the task cards and phase contracts the agents
  were dispatched against, the owner's decision memos and the review ledger.
- [`audits/`](audits/README.md) holds the close audits, the recording records
  and the independent reviews.
- [`design/`](design/phase-12/) holds the viewer's phase-12 design record: its
  brief and stages, the map reference and the one-off generator that draws it.
- [`DESIGN.md`](DESIGN.md) is the original system design, kept as rationale.
- [`AGENT_IMPLEMENTATION.md`](AGENT_IMPLEMENTATION.md) is the original plan for
  building with coding agents, kept as onboarding history.
- [`docs/cleanup-dispositions.md`](docs/cleanup-dispositions.md) routes the
  findings of the September cleanup.

The paths written inside these records predate their move into this folder, and
a record's text is never rewritten to follow a move; only the relative links it
carries were re-pointed on 2026-10-13 so they still resolve. A record that cites `tasks/…`,
`audits/…`, `design/…`, `DESIGN.md` or `AGENT_IMPLEMENTATION.md` means that path
here; `docs/history.md` means this page and `docs/cleanup-dispositions.md` means
`process/docs/cleanup-dispositions.md`. The generated pages it cites under
`docs/` (the gameplay census, the game profile and the process scorecard) are
under [`eval/reports/`](../eval/reports/README.md); `docs/ownership-case-study.md`
is the second part of [How this was built](../docs/lessons.md#one-decision-traced),
and `docs/game-shape.md` and `engine/README.md` open
[the game rules](../docs/observation-contract.md). The one audit tool code
imports, `audits/workflows/extract_gameplay_facts.py`, is now
[`experiments/extract_gameplay_facts.py`](../experiments/extract_gameplay_facts.py).

## Phase history

One paragraph per phase, in order. Each names its contract — the document the
agents were dispatched against — and its close audit where one exists. Close
audits begin at the MVP close and resume at phase 13; the phases in between
closed inside their contract files, which carry the per-task status lines.

Vocabulary that turns up below is defined in the [glossary](../docs/glossary.md),
or [on this page](#vocabulary-of-the-records) when only the records use it; the
numbers and what they do and do not show are in the
[reading guide](../docs/reading-guide.md).

### The MVP: phases 0–5

**Phase 0 — scaffolding.** Repository, CI, the project skeleton, the lint rule
that enforces the observation firewall, and a deliberately failing leak test, so
the firewall had a gate before it had an implementation.
[Contract](tasks/phase-0.md).

**Phase 1 — the engine.** World state, rules, seeded RNG, visibility, the replay
recorder and the leak test made to pass. The determinism property — one seed and
one set of inputs, one set of bytes — dates from here and has never been
relaxed.
[Contract](tasks/phase-1.md).

**Phase 2 — tactical agents.** Memory, perception, pathfinding, the
finite-state-machine policies that still ship as the default mover, and the
headless orchestrator plus tournament harness that every later measurement runs
on. [Contract](tasks/phase-2.md).

**Phase 3 — the meeting.** LLM-driven meetings, voting, and contradiction
detection across the transcript. The provider-neutral client, the deterministic
fake provider, and robust JSON extraction with failure recording all land here.
[Contract](tasks/phase-3.md).

**Phase 4 — the spectator.** A FastAPI plus React replay viewer, replay-only by
construction: it reads saved replay files and never drives the engine. The
sanitized DTO inventory dates from this phase.
[Contract](tasks/phase-4.md).

**Phase 5 — eval.** Metric analyzers over a typed tournament report, the
tournament dashboard, and the prompt-regression close gate that turns "change a
prompt, watch a metric move, attributably" into a test. This is the MVP.
[Contract](tasks/phase-5.md) ·
[close audit](audits/audit-2026-05-30-0059-mvp-close.md).
Retired on 2026-10-09: the close gate and its module, with the three-seed
fixtures whose last version is at `4e5b6d6a`.

### Making the agents reason: phases 6–13.5

**Phase 6 — repair and hardening.** The post-MVP cleanup pass: the defects the
close audit surfaced, closed before anything was built on top of them.
[Contract](tasks/phase-6.md).

**Phase 7 — impostor coordination, and a change of eval model.** Impostors
learned to coordinate, and the teammate firewall — a ballot targeting a fellow
impostor is deterministically rewritten to SKIP — landed here. The eval moved
off a hosted commercial model onto a local open one, which made large sample
runs free. [Contract](tasks/phase-7.md) · [plan](tasks/phase-7-plan.md).

**Phase 8 — deduction substrate.** A restructure of how evidence reaches the
table, after the phase-7 measurements showed the meeting ejecting people without
deciding anything. [Contract](tasks/phase-8.md).

**Phase 9 — producer hygiene and conversion.** The quality of what agents
*produce* into a meeting, and how much of it converts into a correct ejection.
[Contract](tasks/phase-9.md).

**Phase 10 — the conviction engine.** Repair of the flag-to-ballot-to-tally
pipeline, plus the crew's evidence economy — what the table is actually handed
to reason with. [Contract](tasks/phase-10.md).
Retired on 2026-10-09: the three corrected-baseline fixtures with their anchor
tests, the Wave-2 gate spec and the report builder's baseline derivation; the
fixtures' last version is at `83148aa6`.

**Phase 11 — the impostor's information economy.** Vents and sabotage became
real impostor moves rather than decoration, then were balanced against the
crew's side of the economy. [Contract](tasks/phase-11.md).

**Phase 12 — the front end.** The spectator rebuilt as a product: map playback
with a fog-of-war perspective toggle, meeting transcripts with ballots and
flags, per-agent memory snapshots, a belief matrix, a guided tour, keyboard
transport. [Contract](tasks/phase-12.md).

**Phase 13 — pre-ML grounding.** Rubric repair and a deduction rework, intended
to make the meeting decide rather than merely eject. The mechanism was built and
verified present; the model of the day could not drive it, which is what sent
the project to a memory-correctness pass and then a model migration.
[Contract](tasks/phase-13.md) ·
[close audit](audits/audit-2026-06-25-0859-phase-13-close.md).

**Phase 13.5 — memory correctness.** Spoken testimony had been collapsing into a
suspicion scalar before it reached anyone's beliefs. This phase took the fix
down to the substrate rather than papering over it at the prompt.
[Contract](tasks/phase-13-5.md).

### Measurement and the ML program: phases 14–18

**Phase 14 — the hosted provider.** A hosted OpenAI-compatible provider, and the
model and prompt migration onto it. The first numbered reference recording
follows from this migration. [Contract](tasks/phase-14.md) ·
[close audit](audits/audit-phase-14-close.md).

**Phase 15 — cleanup, then the training environment.** An evidence-substrate
cleanup wave closing on reference recording 3, then the machine-learned tactical
policy program proper: measurement harness, training environment, calibration
corpus, a rebuilt meeting surrogate, and a multi-method bake-off with a mid-phase
pause that picked the winning method on measured numbers before any
productization was authored. The learned impostor policy shipped opt-in.
[Contract](tasks/phase-15.md) ·
[close audit](audits/audit-phase-15-close.md).

**Phase 16 — voice and judgment.** Citation-gated ballots (every eject ballot
must cite a transcript turn or an observation id, and compliance reached 1.000
at the close), information pooling via a roll-call round and vouching, and
personas — all on one model, chosen by a probe and then frozen so that nothing
else in the phase could be confused with a model change. Three settings graduated together at
that close and became unconditional: the citation gate (`citation_gate`), the
hard-evidence gate (`hard_evidence_gate`) and observation-id rendering
(`observation_id_rendering`). Closed on reference recording 5; the absence prior
(`absence_prior`) stayed off there as a recorded ruling pending roll-call
calibration, and graduated at the next recording. Reference recording 4, one
phase earlier, was the model-only swap, isolated from every behavioural change.
[Contract](tasks/phase-16.md) ·
[close audit](audits/audit-phase-16-close.md).

**Phase 17 — co-adaptation.** The monitoring corpus was re-recorded on the
current substrate, the ballot surrogate re-fit to the first GO verdict at the
training-time-runner tier, and the full impostor and crew slate re-run and
re-selected under the new referee. The evidence-gated default flip was ruled
FAIL: the leading learned mover kept a +0.16 win edge over the scripted one and
still failed the conversion floors, while the arm that passed the referee did so
at a 0.02 win rate — a pass bought by losing. No adoption.
[Contract](tasks/phase-17.md) ·
[close audit](audits/audit-phase-17-close.md).

**Phase 18 — the ML phase.** The meeting-layer package graduated crew-only at
the baseline-6 adopting record, with the monitoring corpus re-recorded on it. A
conviction model landed GO, and composed with the surrogate's retained ranking
channel into the meeting-outcome runner used for training rollouts.
Alternating-freeze co-evolution ran the impostor campaign, then the crew
campaign, and a real-model finalist eval fed a two-axis owner ruling: NO-FLIP —
every learned arm beat the same-seed scripted comparator on wins, by +0.12 to
+0.30, and every arm failed the supply and conversion floors, reproducing the
starved-economy shape on a co-adapted slate — and zero of the fourteen
pre-registered emergence rulings demonstrated, with two selected-for
kill-placement effects recorded as named findings rather than upgraded to fit
the claim. No crew adoption. [Contract](tasks/phase-18.md) ·
[close audit](audits/audit-phase-18-close.md).

### Review and refresh: phase 19

**Phase 19.** Chartered as review-and-refresh after the owner deferred
presentation work. It ran the front-door and in-code truth sweeps with
generated-fact checks, the spectator coherence pass and the static demo bundle,
the frontend test baseline, the deduction metrics and injustice fixtures, the ML
tier map with its retirements and report-honesty close, and a two-tier test
structure. All 28 contracts merged, and the phase closed with nothing recorded:
the substrate did not move, and the choice between an evidence-honesty substrate
phase and a presentation phase was routed to the owner.
[Contract](tasks/phase-19.md) ·
[close audit](audits/audit-phase-19-close.md).

### Evidence honesty: phase 20

**Phase 20** takes the presentation-and-honesty route out of that decision: the
front door made true, the inference channel repaired, and one pre-registered
record. That record was spent on 2026-08-25, and the phase read it against bars
it had written down before the repairs existed. Two of them missed — conviction
accuracy without engine-certified proof at 61/103 = 0.5922 against 0.60, short
by 0.0078, and wrongful ejections at 42 against fewer than 35, down from 79 at
the recording before it but not far enough — so the rule's verdict is a finding,
not an adoption. Reference recording 7 became canon because
the owner overrode that verdict in writing on 2026-08-26, on stated grounds, and
the phase closed behind it that same day at `d8ec0a1c`
([close audit](audits/audit-phase-20-close.md)).
[Contract](tasks/phase-20.md) ·
[record](audits/audit-phase-20-baseline-7.md).
Retired on 2026-10-09: the offline lever counterfactual script, which refused to
run once its levers graduated; its last version is at `a8a3db9b`.

### Phase 21 — the substrate told the truth, and the record caught up

Phase 20's repairs had landed in the code but not in the bytes: every instrument,
the training corpus, the front door and the spectator were still reading
recordings made by code that no longer existed. A review of the whole record
found the shape of the problem — a re-recording had once moved the bytes and
relabelled one word while every number stayed behind, leaving a green check
certifying a document it contradicted. Phase 21 repaired what the engine records
and what a model is shown (discarded actions stop being written down as though
they happened, the belief line stops contradicting the agent's own sightings,
each witnessed vent is remembered once instead of twice, the oracle voice leaves
the templates, and structured testimony survives to the ballot), then spent a
twelve-hour recording on 2026-08-31 to put those repairs into the record.

That recording is **reference recording 8**, and it decided nothing. It has no
bars and no verdict by design: it re-records, publishes every cell before and
after, and leaves every judgment to the record that comes after it. Some of what
it published is unwelcome — conviction accuracy without engine-certified proof
fell, wrongful ejections rose from 42 to 46, and a class of wrongful conviction
that the previous record had described as extinct reappeared at four cases.
Pooled over its four recorded sets, accuracy without that proof read
50 of 96 = 0.5208 with 46 innocent ejections. Those
are published unchanged, which is the whole point of separating a maintenance
record from an adopting one.
[Record](audits/audit-phase-21-rerecord.md).

Then came what the re-record was for. Three meeting-layer repairs were built and
kept switched off until a record could judge them — the reporter's own reasoning
on its turn, a discipline on how corroborating accounts are counted, and
structured testimony that survives into the ballot — and four bars were written
down before any of it was measured. A 300-game recording taken over 2026-09-03
and 2026-09-04 met three. Conviction accuracy without engine-certified proof
rose to 46 of 66 = 0.6970 against a bar of 0.60.
Innocent ejections fell from 46 to 20 against a ceiling of fewer than 35; 11 of
those 20 were the meeting's own reporter, against 34 of 46, inside the
reporter's own ceiling of 12. The fourth asked
that the reporter be under 0.40 of what was left, and 11 of 20 = 0.5500 is not
— the reporter channel closed faster than every other route and still dominated
the much smaller total behind it. Every bar has to pass, so the rule returns a
**finding**, not an adoption: nothing was adopted, the three repairs stay
switched off, the reference recording did not move, and those 300 games are kept
as named evidence beside the record instead of replacing the committed sets. No
override was made.
[Record](audits/audit-phase-21-adopting-record.md).
The phase closed on 2026-09-05 behind that finding.
[Contract](tasks/phase-21.md) ·
[close audit](audits/audit-phase-21-close.md).

### Where the sample sets came from

The 100 committed replays under `replays/samples/` sit in two eras, named in
`eval/eras.py`. On 2026-10-02 the owner promoted candidate round 2 as the shown
9-player set: `replays/samples/9p2i` held its fifty games, recorded 2026-10-01
under one declared config that switches on the seven adopted gameplay settings,
the kept vent exit and a six-tick kill cooldown, with that config beside the
replays. The ladder tip stays at baseline 9, because no substrate setting moved.
Baseline 10 is reserved for the full re-record. The set's previous games remain
at `d41c9006`
([`audits/audit-2026-10-01-stage-b-r2.md`](audits/audit-2026-10-01-stage-b-r2.md)
§9).

On 2026-10-09 the orchestrator, under the owner's delegation, promoted candidate
round 3: `replays/samples/9p2i` now holds its fifty games, recorded 2026-10-09
on round 2's config plus the route lines, a line on each ballot about which
stated changes of room the doors or the regroup allow. Round 2's games stay in
the tree as `replays/candidates/stage-b-r2`, the comparison record for that one
change, and the ladder tip stays at baseline 9
([`audits/audit-2026-10-09-stage-b-r3.md`](audits/audit-2026-10-09-stage-b-r3.md)
§12).

The 4-player set and both corpus sets are reference recording 9,
made 2026-09-22. It re-recorded the same four sets at the same seeds after three
repairs the owner accepted as a set on 2026-09-19: an alibi is stated as a route
rather than one room, an abstention names what it weighed, and a ballot sees the
evidence rows behind each suspicion rather than the number alone. Those ship as
the default, not as settings under test, so the recorded settings list is the
same twenty-one graduated settings as before, with the impostor-answer arm still
recorded off; what moved is the prompt set (three templates at `v6`, the ballot
at `v8`). It published the process measures before and after and **decided
nothing** — no bars, no verdict
([`audits/audit-2026-09-22-process-rerecord.md`](audits/audit-2026-09-22-process-rerecord.md)).
Pooled over the four sets, accuracy without engine-certified proof read
43 of 85 = 0.5059 with 42 innocent ejections, a movement these samples cannot
call real.

Reference recording 8 (2026-08-31) keeps its history and loses only its claim to
be the current one
([`audits/audit-phase-21-rerecord.md`](audits/audit-phase-21-rerecord.md)). It
was a **maintenance** record: the same four sets on repaired code at a bumped
prompt set, nothing adopted, inheriting reference recording 7's settings exactly.

**Read reference recording 7's own §6.1 before citing either.** Recording 8
succeeded recording 7 as the newest, but it adopted nothing of its own and
inherited that substrate exactly as it was adopted: the pre-registered decision
rule returned **FINDING**, not adoption — two of its bars missed — and the owner
adopted it by an explicit override of that verdict, on stated grounds, **not
because the bars passed**
([`audits/audit-phase-20-baseline-7.md`](audits/audit-phase-20-baseline-7.md)).
Recording 7 keeps that whole history and loses only its claim to be the current
one ([`audits/audit-phase-21-rerecord.md`](audits/audit-phase-21-rerecord.md)).
Reference recording 6 remains the meeting-layer adopting record that preceded
them ([`audits/audit-phase-18-baseline-6.md`](audits/audit-phase-18-baseline-6.md)).

Each set's `MANIFEST.md` is the canonical provenance record, row by row: model,
prompt-template versions, the twenty-one graduated settings stamped on every row,
refresh date, cost and outcome. `scripts/refresh_samples.sh` regenerates the
sets against the active provider and rewrites those rows;
`scripts/verify_samples.sh` replays every sample through the engine, free and
offline, and fails loudly the moment a recorded state hash stops reconstructing.

## Vocabulary of the records

The records use these words as if they were common English, and no live page
does; [the glossary](../docs/glossary.md) defines the rest. Where a convention
was originally named after the task that introduced it, the descriptive name is
the heading and the old name is given inside the entry.

### the ladder tip (the newest reference recording)

Where the substrate currently stands. "The ladder tip stands at baseline 9"
([`audits/audit-2026-09-22-process-rerecord.md`](audits/audit-2026-09-22-process-rerecord.md)).
The shown 9-player set moved to later eras
on 2026-10-02 and 2026-10-09 without moving the tip: no substrate setting
changed, and baseline 10 is reserved for a full re-record.

### the flip bar (formerly "the §1.3 bar")

The written bar a learned policy must clear to become the default: close both
evidence-supply gaps *without* surrendering its win edge. Stated in
[`audits/audit-phase-17-close.md`](audits/audit-phase-17-close.md) §1.3, and
every later ruling reads against it.

### canary denominator (the held-out monitoring corpus)

The largest same-substrate, validity-gated recording set that monitoring metrics
are judged on — today [`replays/ml_corpus/`](../replays/ml_corpus/README.md),
200 games against the 100 sample games. Using a bigger denominator than the sets a
change was tuned on is the point.

### findings, not failures

The closing doctrine: a pre-registered measurement that misses its bar is a
finding to record, not a failure to hide or re-price. Chartered in
[`tasks/phase-18.md`](tasks/phase-18.md) and applied in
[`audits/audit-phase-18-close.md`](audits/audit-phase-18-close.md) §6.

### merge-as-ratification (formerly "the 15.18 convention")

Decision documents — plans, close readings, tier maps — are proposed as pull
requests, and the owner's *merge* is the ratification. Measurements commit their
pre-registration before the measurement and their reproduction snippets beside
the numbers ([`tasks/phase-19.md`](tasks/phase-19.md)).

### the two-owner gate

A phase's ruling and its close are two separate owner merges, and the close
carries no new evidence — so the second merge ratifies a reading rather than a
surprise ([`tasks/phase-18.md`](tasks/phase-18.md)).

### errata discipline

Living documentation is rewritten; *records* — campaign reports and audits — are
not, apart from the 2026-10-13 personal-data scrub, which spelled the operator's home directory `~` or elided its account name, elided scratch paths and redacted one mail address in place, keeping every line number, with a dated erratum in each campaign report it touched. Otherwise they take additive, dated errata, and later prose quotes only
errata-approved figures
([`training/reports/report-finalist-eval.md`](../training/reports/report-finalist-eval.md)
§18).

### citation shorthand

`§N.M` is a section of the cited document. `F<n>` is a numbered campaign finding
carried between contracts, `L<n>` an item in a ruling's own ledger, and
`P0`–`P2` the input audits' severity ranks. In
[`audits/audit-phase-19-triage.md`](audits/audit-phase-19-triage.md), `[C]`
marks a finding both external audits reached, `[S-Claude]` / `[S-Codex]` a
single-source one, and `[L]` an internal-ledger-only one — provenance tags, not
verification status.

### conviction economy (what a meeting does with evidence)

The pipeline from flag to ballot to tally, and how much of the evidence a
meeting is handed it converts into a correct ejection. "Conviction engine" means
this pipeline in [`meetings/`](../meetings), never the [`engine/`](../engine)
package.

### supply and conversion floors

The two halves of that economy, as numbers a recording must clear: how much
usable evidence the meeting is *supplied*, and how much of it the table
*converts*. They are the gauges the
[referee](../docs/glossary.md#referee-the-selection-gate) prices
([`eval/watchability.py`](../eval/watchability.py)).

### starved-economy shape

The failure pattern where a learned mover wins more games by supplying the
meeting with less evidence — the win edge is real and the deduction gets worse.
First named in
[`audits/audit-phase-17-close.md`](audits/audit-phase-17-close.md) and
reproduced on a co-adapted slate in
[`audits/audit-phase-18-close.md`](audits/audit-phase-18-close.md).

### endpoint-band whereabouts exemption

The rule that a whereabouts claim is not treated as contradicted when the two
statements differ only at the ends of the interval each covers — a player who
says "Engineering" for ticks 4–8 and one who saw them leave at tick 8 are not in
conflict ([`meetings/transcript.py`](../meetings/transcript.py)).

### absence prior

The starting assumption a table brings to a player nobody can place: absence is
weak evidence, weighted rather than ignored
([`audits/audit-phase-17-absence-gate.md`](audits/audit-phase-17-absence-gate.md)).

### screening-tier shortlist

A campaign result that is explicitly too small to rule on: the arms are ranked
well enough to shortlist for a bigger run, and no further
([`audits/audit-phase-18-close.md`](audits/audit-phase-18-close.md)).

### training-time-runner tier

A verdict on a learned component saying it is good enough to drive training
rollouts but not to decide anything in a real game — the two jobs have different
accuracy requirements ([`training/README.md`](../training/README.md)).

### two-axis owner ruling

A close that rules on two independent questions at once — here, "does a learned
mover become the default?" and "was any pre-registered emergence claim
demonstrated?" — so a yes on one cannot be read as a yes on the other
([`audits/audit-phase-18-close.md`](audits/audit-phase-18-close.md)).

### evidence-gated default flip

The proposal that the learned mover become the default *conditional* on the
evidence gauges, rather than on wins alone. Ruled FAIL in
[`audits/audit-phase-17-close.md`](audits/audit-phase-17-close.md).

## Candidate rounds

Each candidate round recorded the 9-player set under one declared config.
[The experiment arms page](../docs/experiment-arms.md) states the recorded
settings and which of them are adopted.

### Candidate round 1

The ladder tip stands at baseline 9.
[`replays/candidates/stage-b-r1/9p2i`](../replays/candidates/stage-b-r1/README.md)
is candidate round 1, recorded with the experimental switches its README
names; it adopts nothing and is not a canonical sample set.

### Candidate round 2

Candidate round 2 was recorded with the adopted switches, the kept vent exit
and a six-tick kill cooldown, under one declared config. On 2026-10-02 the owner
promoted it as the shown 9-player set, in its own era
([the record](audits/audit-2026-10-01-stage-b-r2.md), section 9), with one
flag its record states: reporters ejected per report meeting read 17/114, above
the pre-registered 0.104, so the round's own rule named no promotion step; the
owner's ruling promoted it regardless. Since round 3's promotion its bytes are
[`replays/candidates/stage-b-r2/9p2i`](../replays/candidates/stage-b-r2/README.md),
moved there without a byte changed with its config at the round's root: the
comparison record for the route lines, which round 3 adds and nothing else. It
adopts nothing and is not a canonical sample set.

### Candidate round 3, the shown set

Candidate round 3 was recorded with round 2's rules and one more switch that
gives each voter a plain line about the places stated at the table. On
2026-10-09 the orchestrator, under the owner's delegation, promoted it: it is now
[`replays/samples/9p2i`](../replays/samples/9p2i/MANIFEST.md), the shown
9-player set, in its own era (`eval/eras.py`), with its declared config beside
its replays as `experiment-config.json`, and its candidate copy is deleted
([the record](audits/audit-2026-10-09-stage-b-r3.md), sections 11 and 12).
Promotion moves no default and deletes no switch. The ladder tip stands at
baseline 9.

## The workflow pilot

Copied from [the workflow page](../docs/workflow.md), whose
[branch and delivery route](../docs/workflow.md#branch-and-delivery) is the one
the last paragraph names.

The pilot has now run through the first parallel recording batch. Its recorded
results justify keeping canonical cards and manual ownership; they do not
establish a measured time-saving claim. The owner's delivery policy for that
cleanup was a shared branch and Claude review after all cleanup. During
implementation, the coordinating agent handled necessary manifest attribution
and explicit historical-loader follow-through without another owner permission
round. The pilot's independent reviewer found parser defects, now covered by
adverse tests; the three recording repairs' independent reviews left no blockers.
Their cards preserve the underlying checks and limitations.

The combined recording gate passed 6,292 Python and 440 frontend tests plus
100 canonical reconstructions. The Python leg took 133.51 seconds on that local
run; this is a verification measurement, not total development time. Continue
recording scope follow-through and independently found defects in Results, and
compare future batches before changing the process again.

**Merged into main (2026-09-07).** The cleanup branch merged into `main` as
`8161689a` through PR #435 — a merge commit rather than a squash, so the branch
SHAs the ledger cites stay reachable. Its last recorded full gate ran at
`93bf7d54`: 7,173 Python tests, 514 frontend tests and 300 canonical
reconstructions, with 20 optional skips and three expected failures; CI and the
Pages build then passed on the merge commit itself. The shared-branch policy
above ended with that cleanup; delivery for new work is the `work/<card-slug>`
branch and pull request described at the top of this document.

---

Back to the [README](../README.md), the [reading guide](../docs/reading-guide.md), the
[glossary](../docs/glossary.md), or the [audits index](audits/README.md).
