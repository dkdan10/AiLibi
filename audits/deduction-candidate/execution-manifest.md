# Fresh-model deduction evaluation — execution manifest

**Dated 2026-09-09, amended 2026-09-10, 2026-09-13, 2026-09-14 and
2026-09-15. Status: bound. This document authorizes no live call.**

[The preregistration](preregistration.md) §"Select a candidate and prepare a
separate execution manifest" lists what an execution manifest must bind before
any fresh provider run. This is that manifest. Every field below is bound; the
owner-authorization fields carry the values the owner authorized by merging
[the authorization card](../../tasks/work/fresh-deduction-authorization.md) as
#437 on 2026-09-07 (merge commit `0f49d8e6`, ruling B.12 in
[the decision memo](../../tasks/owner-decisions-2026-09-07.md)).

**Supersession.** [The instrument card](../../tasks/work/fresh-deduction-instrument.md)
was written before #437 and asks for these fields "present and EMPTY". The
owner's later ruling filled them, so they are present and FILLED here, copied
verbatim from the authorization card. The card's original wording is superseded
by that ruling, not by this document.

**What is still not authorized.** #437 authorized LIMITS, not a run. Nothing in
this manifest is a licence to spend: no live call, pilot, smoke run or retry is
authorized by it, including on flat-rate service. A call requires an explicit
runner invocation naming this file, carrying the runner flag on the command
line. No committed file outside this one and the instrument that defines that
flag carries it — no test, workflow, script or card — and a test scans every
tracked file for it. Tests do build invocation objects, which is how each
refusal below is proved; none of them reaches a provider (see "The live gate").

## Amendments before first run

This manifest may still be amended: no held-out outcome has been inspected, no
unit has been run, and preregistration binds a design before results exist
rather than after. Every amendment is dated here, in the order it was made, and
that completeness is a mechanism rather than a promise:
`tests/experiments/test_fresh_deduction_instrument.py::TestExecutionManifest::test_the_amendment_log_names_every_commit_that_moved_the_frozen_analysis`
walks this branch's history from the commit that first bound this document,
reads the frozen-analysis constants out of every later revision of
`experiments/fresh_deduction_instrument.py`, and requires each commit whose
values differ from its parent's to be named in one of this document's dated
amendment logs — this section, or one of the post-run sections below, which is
where an amendment made after a unit ran belongs. A change to the frozen
analysis that nobody logged fails that test wherever it was made.

**2026-09-09 (`2dde0c91`) — the decision rule gains its third condition, and
the sampling configuration is bound.** Round-1 review of the instrument's pull
request (#443) found that this document bound two preregistration fields as
prose the instrument did not enforce. `DECISION_RULE` advanced the candidate on
two conditions — p below 0.05 AND a net paired difference of at least 10 — so an
arm could buy its supported-correct ejections by ejecting more innocents and
still advance, and the preregistration's "acceptable tradeoffs" field
(`preregistration.md:116-118`) had no bound to point at. The rule was rewritten
from BOTH to ALL THREE by adding the wrongful-ejection bound now quoted below as
`WRONGFUL_EJECTION_TRADEOFF`, and the sampling configuration was bound as
`AUTHORIZED_SAMPLING` in code with the marked sampling row added to the owner's
table above. The amendment RAISES the bar the candidate must clear and adds a
field rather than removing one, and it was written before any unit ran.

**2026-09-09 (`bfd5696b`) — a meeting-internal default is counted, not
stopped.** Round-2 review found that the stop rule promised a stop the code
never made. The Inputs row "Maximum opportunities" read "A missing or truncated
attempt is a stop, and the partial state is reported rather than replaced",
while the meeting layer's shipped fail-soft substitutes a placeholder turn or a
marked SKIP ballot for a payload that failed schema validation and the run
carries on. Both that row and `STOP_RULE` were reversed: an attempt that never
resolves is still a stop, a schema-validation default is NOT, and every such
substitution is counted per unit and per arm instead (see "Meeting-internal
defaults: counted, not stopped"). This is the one amendment that RELAXES a rule,
and it is on the record as such: a fixed 50-unit paired sample cannot be
abandoned for a substitution the engine is designed to make at an accepted rate
of about 1 in 50 calls, and the alternative was a stop rule the run would have
tripped on its first default. Its cost to a reader — a defaulted ballot removes
a constraint from the primary outcome rather than failing it, biasing it upward
— is stated where the counts are. It was written before any unit ran.

**2026-09-09 (`3a02ede8`) — citation relevance joins the primary outcome.**
Round-4 review of
the instrument's pull request (#443) found that the privileged grader checked
only that a ballot's citation was PRESENT in that voter's prompt, so a ballot
that guessed the impostor while citing a turn about somebody else scored the
primary outcome — collapsing the distinction between a supported inference and a
lucky guess, which is the distinction the primary outcome exists to draw. The
frozen rubric below ("Evidence privileges and grading", pass 3) now requires the
cited turn or observation to bear on the ejected player, and the primary outcome
is the conjunction of role-correctness, presence and relevance. The amendment
was written before any unit ran; the fake-provider mechanics check it was
verified on carries no held-out outcome. It lands in the same commit as the
grader that enforces it, which
[the instrument card](../../tasks/work/fresh-deduction-instrument.md)'s Results
names in its round-4 subsection.

## Amendments after the stopped run of 2026-09-10

The first live run stopped after one unit of one hundred and was left unmerged
by the owner (PR #445, branch `work/fresh-deduction-run`). What stopped it was
an accounting defect in the instrument rather than a limit, and the repair is
recorded apart from the pre-run amendments above because it is made after a unit
ran rather than before any existed. It reaches the enforcement text only. The
frozen analysis does not move — `PRIMARY_OUTCOME`, `DECISION_RULE`,
`MINIMUM_ACTIONABLE_EFFECT_UNITS`, `WRONGFUL_EJECTION_TRADEOFF` and `STOP_RULE`
are the same bytes the sections below quote — and no held-out outcome informed
it: the stop the repair reads carries counts and identifiers only.

**2026-09-10 (`d8eb7d36`) — the reconciliation counts every charged call, and
the enforcement text stops naming a stop the stop rule never carried.**
`_reconcile_recorded_spend` summed `MeetingReplayEntry.llm_calls` alone. A real
provider validates the completion itself and raises before the recording client
can log the call, so a paid call whose payload it refused is charged to the
budget while its spend rides the parse-failure metadata on the surfaced default
instead of a meeting row (`meetings/manager.py:1712-1720`). On the stopped run
that was one call of 2,228 input and 861 output tokens against a unit whose
meeting row carried 13,263 / 1,448 of an enforced 15,491 / 2,309. The
reconciliation now sums the meeting's resolved calls plus every failed attempt
the replay records with usage, and the same call reaches the partial accounting
a stop reports. Alongside it, this document's "How each limit is enforced"
section said of that comparison "a difference is a stop" — a stop condition
`STOP_RULE` does not carry, which is how a run could be stopped by a rule the
frozen analysis never stated. The reconciliation is the token budget's
accounting check; a unit whose accounting does not add up stops the run through
the same clause every other unit failure does. That bullet now quotes
`SPEND_RECONCILIATION` verbatim, so the code's statement and this document's
cannot drift apart again. The amendment of 2026-09-09 (`bfd5696b`) reached
`STOP_RULE` and the default counter but not this comparison; this is the rest of
it.

**2026-09-10 (`6215fda1`) — the stops a charged failure has to meet.** Round-1
review of this repair's pull request (#447) found that the amendment above had
made a refused call countable without making it judgeable. Two stops `STOP_RULE`
carries, plus one limit this manifest binds of its own, were reachable only on
the success path, so counting the burned call — which is what stopped the run of
2026-09-10 — let it through all three. The two frozen clauses: a response that
reached its output cap ("a truncation is a stop, not a datum") was fail-softed to
a SKIP when the truncated body also failed schema validation, which is the usual
reason it fails; and "a token budget exhausted at either the per-unit or the run
level" was left unenforced for a charge applied after the fact, whose overrun
`llm/budgeted_client.py` downgrades to a note on the exception the meeting layer
fail-softs — on a unit's last call, with the budget then discarded, no later
pre-flight existed to find it. The third is this manifest's own: a checkpoint
this run does not authorize reached `InstrumentReport.model_ids` instead of
stopping the run. Provider identity is not a clause of the frozen rule and this
entry does not claim it is; it is the "Provider and model" row of the authorized
values above, whose enforcement bullet has bound `_InstrumentClient` to refuse a
response whose `model` is not the authorized one since before the first run, and
the amendment only extends that refusal from a response the provider returned to
one it billed for and then refused. The client now judges a billed-and-refused
completion by the `model` and `output_tokens` its parse-failure metadata
carries, and both budgets are read back against their caps after each unit
(`BUDGET_CAP_READBACK`, quoted verbatim in "How each limit is enforced"). This
amendment adds no stop condition and relaxes none: `STOP_RULE` is byte-identical,
the two clauses quoted above are ones it already carried, and the checkpoint
refusal is the manifest limit just named. Every planted case is red without the
check it proves, and each is listed in
[the reconciliation card](../../tasks/work/fresh-deduction-instrument-reconciliation.md)'s
round-1 subsection. Round-2 review of the same pull request corrected this
entry's attribution, which as first written counted the checkpoint refusal as a
third clause `STOP_RULE` carries; a gate now checks that every clause this
section credits to the frozen rule is one the rule states, and that the count it
claims is the number it quotes.

**2026-09-10 (`08aee9cc`) — the Inputs table is re-bound to the second held-out
band, and a gate holds a live run to it.** The stopped run rendered the first
seed of the 3000-3999 band to the model, which the preregistration and the Roles
section below make development data. A second band was frozen under
[the second freeze card](../../tasks/work/held-out-prefix-freeze-2.md), and the
first band's record was marked `development` and kept beside it rather than
deleted, which is what that section requires. The Inputs table now binds
5000-5999 — accepted seeds 5000-5052, three `witnessed_kill` skips, every number
read off [the freeze record](held-out/manifest.json) — and says where the first
band's record now lives; the Roles table names the second preparer session
beside the first. Nothing the owner authorized moves with it: the limits, the
sampling configuration, the provider and model, the measures and the frozen
analysis are the same bytes as before this entry.

Re-binding a document does not bind a run, so the amendment carries a gate with
it. `verify_frozen_set` regenerates whatever record sits at the generator's
`MANIFEST_PATH` and never reads this file, and the live gate checked this file's
path and digest but not the inputs it names — which is how a band could move
under an unchanged authorization with every check green.
`assert_manifest_binds_the_live_band` reads the band out of the Inputs row and
refuses a live run whose freeze record holds another one. It runs inside
`assert_live_run_is_authorized`, the first thing `assert_ready_for_a_live_run`
calls, so a stale binding stops the run before a provider, a credential or a
connection exists. It adds no stop condition and relaxes none: a run it refuses
never starts, and `STOP_RULE` is byte-identical. Every planted case is red
without the check it proves, and each is listed in
[the reconciliation card](../../tasks/work/fresh-deduction-instrument-reconciliation.md)'s
stacking subsection.

## Amendments after the stopped run of 2026-09-13

The second live run stopped inside its first unit as well (PR #448, closed
unmerged; branch `work/fresh-deduction-run-2` is its archive). On its fifth
call the endpoint answered a 2xx with no `choices`, which
`llm/featherless_client.py::_raw_from_response_body` refuses with a bare
`RuntimeError` that none of that client's own retry classes carries, so the
attempt reached the instrument as a failure and the run stopped with four
resolved calls of a projected six hundred. This section is dated apart from the
one above for the same reason that one is: it is written after a unit ran. It
reaches the transport clause of the frozen rule, the enforcement text and the
wall row; no held-out outcome informed it, because the stop it reads carries
counts and identifiers only, and the four calls it resolved were seed 5000 of a
band this document no longer binds.

**2026-09-13 (`0fa2a3e5`) — an attempt that produced nothing is retried
within a stated bound, and the wall window carries the third authorization's
numbers.** Three things move together.

`STOP_RULE` gains a transport clause and is quoted below in its new bytes. It is
the one amendment in this document that reaches the frozen analysis after a unit
ran, and it is written down as such: a call that came back with no completion at
all is retried up to three times and then a stop, with every attempt counted per
arm and per unit. It widens no limit and adds no stop — the run stops on the
same conditions it stopped on before, one of them later — and it draws no second
sample, because the attempts it re-sends produced nothing to sample. The clause
says the other half in the same breath: a body that reached its output cap and a
returned payload that failed schema validation ARE samples and are never
retried, and neither is an exhausted budget or deadline. The other four frozen
constants — `PRIMARY_OUTCOME`, `DECISION_RULE`,
`MINIMUM_ACTIONABLE_EFFECT_UNITS` and `WRONGFUL_EJECTION_TRADEOFF` — are the
same bytes the sections below quote.

The retry itself lives in the instrument's own client wrapper and not in
`llm/featherless_client.py`, which is what keeps every recorded campaign's
behaviour where it was; `TRANSPORT_RETRY` states it and "How each limit is
enforced" quotes that constant verbatim. Its bound is four attempts at a 180 s
per-attempt wall, sized off the measured per-call band rather than chosen: this
evaluation's calls have run at 11.7 s and 26.6 s, so a healthy call cannot reach
the wall, and four attempts at it cost at most 12 minutes of the work window
against the better part of an hour one stalled call could otherwise hold. Every
attempt is still bounded by what is left of that window, so no retry outlives
the authorization. Each case is planted and red without the code it proves, and
each is listed in
[the transport-resilience card](../../tasks/work/fresh-deduction-instrument-transport-resilience.md)'s
Results.

The wall row of the authorized table now reads 6 h of model work within an 8 h
elapsed deadline, copied verbatim from
[the third authorization card](../../tasks/work/fresh-deduction-authorization-3.md)'s
Constraints table, and `AUTHORIZED_MODEL_WORK_SECONDS` /
`AUTHORIZED_ELAPSED_SECONDS` carry the same numbers. That row is the owner's,
widened by the instruction of 2026-09-13 that card records; every other row of
that table is #437's, unchanged. The cost statement is the same paragraph in
both cards and is not re-cut here: its "2.0 M tokens over a 6-hour elapsed
window" is the first authorization's projection sentence, and the elapsed limit
this manifest binds is the 8 h row above it.

Two obligations were left open by this entry and are not claimed by it: the
Inputs table below still bound the 5000-5999 band, which the stopped run of
2026-09-13 rendered the first seed of and which
[the third freeze card](../../tasks/work/held-out-prefix-freeze-3.md) replaces,
and the re-binding to the third band was the same card's later round. The
stacking entry below is that round and closes both.

**2026-09-13, review round 1 (`4591cc17`) — the enforcement text says only what
this side can see.** Review of the entry above found `TRANSPORT_RETRY` claiming
more than the mechanism can do: it said every failed attempt is recorded "with
whatever usage the provider reported for it". None of the four retried classes
can carry usage. `llm/featherless_client.py::_raw_from_response_body` refuses a
body with no completion in it BEFORE it reads that body's `usage` block, and a
failure that does carry parse-failure metadata is a completion the provider
billed for and is never retried at all — so an attempt of these classes reaches
the wrapper with nothing on it to charge. The constant, the quotation of it
under "How each limit is enforced" and the measures row now say what is true: an
unaccounted attempt is recorded as zero tokens, which is what is KNOWN about it
rather than what it was billed, and it may have been billed for tokens this side
cannot see — the phrasing the model-work cut-off already used for the same
reason. Reading the usage first would be a change to
`llm/featherless_client.py`, which
[the transport-resilience card](../../tasks/work/fresh-deduction-instrument-transport-resilience.md)'s
Constraints exclude precisely so that no recorded campaign's behaviour moves;
the gap is carried as a limitation on that card instead. The frozen analysis
does not move here: the stop rule and the four constants named above are the
same bytes this document quotes below. The same commit makes two smaller
corrections to the wrapper — the status the adapter reported is read before any
response body it quotes, so a permanent 4xx is never re-sent, and a retried call
is counted once its next send begins rather than before the backoff, so a run
cancelled mid-wait cannot report a send it never made — and repairs the
`_ModelWorkClock` docstring, which still described the 4 h / 6 h authorization
the entry above widened.

**2026-09-13, the stacking round (`56581a98`) — the Inputs table is re-bound to
the third held-out band, and the gate that refuses a stale binding says which
bands have moved.** The stopped run of 2026-09-13 rendered the first seed of the
5000-5999 band to the model, which the preregistration and the Roles section
below make development data, exactly as the run of 2026-09-10 did to 3000-3999.
[The third freeze card](../../tasks/work/held-out-prefix-freeze-3.md) drew
6000-6999 with the same generator, marked the second record `development` and
kept it beside the first rather than deleting it, and merged as PR #449; this
branch merged that record in and the Inputs table now binds 6000-6999 —
accepted seeds 6000-6058, nine `witnessed_kill` skips, every number read off
[the freeze record](held-out/manifest.json) — and names both converted bands
with the dates and the files their records now live in. The Roles table names
the third preparer session beside the first two. This closes the two
obligations the entry of `0fa2a3e5` left open and claims nothing else: the
limits, the sampling configuration, the provider and model, the measures and
the frozen analysis are the same bytes they were before it, and the stop rule
is byte-identical.

A re-binding is a document change, so the gate is what makes it bite, and this
round found the gate itself out of date. `assert_manifest_binds_the_live_band`
motivates its own check by naming the conversions, and its docstring still read
that 5000-5999 was frozen in place of 3000-3999 after 5000-5999 had itself
become development data. `56581a98` corrects it and holds it there:
`test_the_gate_says_which_bands_actually_moved` reads each span out of
`CONVERTED_BANDS` and each date out of that record's own `converted` block, so
the next conversion turns the docstring red rather than leaving the enforcing
function explaining a history that moved on. The band the row names and the band
the live record holds are compared as before; nothing about the refusal changed.
The verification section below is re-measured on the new band, and its dry run
is the one the transport-resilience card owed: the same 600 calls with one of
them answered emptily, counted and recovered. This entry cannot name the commit
that carries the document changes, for the reason the entries above record — a
commit cannot carry its own hash — so it names the code commit it is written
against, and the record commit that writes it moves no instrument byte.

## Amendments after the diagnosis of 2026-09-13

Three live attempts stopped, and
[the diagnosis of 2026-09-13](../../tasks/diagnosis-2026-09-13-live-run-stops.md)
— written from four independent read-only investigations, one synthesis and
three adversarial refutations of it — found one root under all three: this
evaluation was SIZED in charged tokens and ENFORCED in reserved ones, and the
only place it ever met the real provider was the held-out run itself. This
section is dated apart from the two above because it is written after a
diagnosis rather than after a stop. It reaches the enforcement text, the live
gate and the verification section; no held-out outcome informed it, because
the stops it reads carry counts and identifiers only.

**2026-09-13 (`78b136bd`) — the units of account are stated, the ceilings are
checked against them before a run starts, and the rehearsal sees what the
provider did.** Four things move together, all offline and all at $0.

The enforcement section's token-budget bullet now states the units of account
and quotes `RESERVATION_POLICY` verbatim: the ceilings are enforced on RESERVED
spend, one unit reserves 9,216 output tokens across its six pre-flights, and a
ceiling below that schedule authorizes calls it cannot pay for.
`assert_limits_are_feasible` refuses such a ceiling — and either run-level
ceiling below a hundred units at the largest unit the live archives charged
(24,282 input, 3,116 output) — from arithmetic over module constants alone,
before a path is resolved or a credential read. **Under the limits merged on
2026-09-07 it refuses.** That is not a defect of the gate: those numbers
authorize six legal calls a unit cannot pay for, the third attempt was stopped
by exactly that, and the live gate now fails closed until a fourth
authorization card re-sizes them. This manifest does not re-size anything: the
row above is still #437's and the widened wall row is still the third
authorization card's.

The rehearsal now exercises the dimension that bound. `DryRunProvider` derives
its usage from the payload it serialises — 66 output tokens a call, identical
on both arms, 9.9% of the per-unit ceiling — so no committed check could see a
reservation schedule at all. A usage-replaying double
(`tests/experiments/usage_replay_double.py`) answers each call with the tokens
the real endpoint reported for a call of that arm and that kind, out of a
committed profile of the 36 resolved calls and the two billed-and-refused ones
the three run branches archived. The profile carries token counts only: no
prompt, no prefix, no response text and no seed. The verification section below
records what it measures.

The retry classifier covers every fail-loud empty-response shape the authorized
client raises. Two of them —
a body carrying no usage block, and a usage block without its two counts
(`llm/featherless_client.py:844,850`) — were not covered and would have re-raised
bare, uncharged and unretried. `TRANSPORT_RETRY` is amended to say what the
class actually is (any body the client refuses to record a completion from) and
to stop claiming the adapter refuses before it reads the usage block, which is
true of two of the four shapes and not of the other two; the quotation under
"How each limit is enforced" carries the new bytes. The bound, the four trigger
classes and the counts are unchanged.

A run may now write a per-unit checkpoint and be continued from one, and the
live gate refuses that continuation until this document carries the owner's
resumption clause — which it does not, so no live run may be resumed today. The
mechanism is built and rehearsed on the fake provider because the diagnosis
names it as owed (`tasks/owner-decisions-2026-09-07.md`, B.4); authorizing a
second sitting on the held-out set is decision 2 of the diagnosis and the
owner's to take. The resume is outcome-blind by construction: it reads the
checkpoint's completed seeds and its identity digests, and nothing in the run
path reads a grade.

*(Superseded 2026-09-14 as to its current-state sentence only: the owner took
decision 2 on that date and this document now carries the clause, under
"Resumption clause (2026-09-14)" below. What this entry records about the
mechanism stands unchanged.)*

The frozen analysis does not move here. `PRIMARY_OUTCOME`, `DECISION_RULE`,
`MINIMUM_ACTIONABLE_EFFECT_UNITS`, `WRONGFUL_EJECTION_TRADEOFF` and `STOP_RULE`
are the same bytes the sections below quote, and a test holds them to the
revision the last logged amendment names. The feasibility gate adds no stop to
the frozen rule: it is a refusal before a run, like the band binding and the
sampling check, not a condition that can stop one in flight. As with the
entries above, this one cannot name the commit that carries the document
change, so it names the commit that carries the behaviour it records,
`78b136bd`; the record commit that wrote this entry, `808b5070`, changed this
document, the derived counts, one docstring this amendment corrects, and one
guard: `arm_surface_digests` refuses a missing prompt-set directory instead of
hashing nothing (corrected 2026-09-14; the entry first said "no behaviour").
This entry records that commit and stops there: what a review then
found wrong with the mechanism above, and what was changed to repair it, is the
entry below.

**2026-09-14 (`0185182d`) — a stopped sitting carries its whole spend into the
next one, and the identity a resume is held to is named rather than claimed.**
An independent review of the commit above found the resume forgiving what a
stop had already bought and holding a resumed sitting to a set of files that
omitted the code rendering its prompts. Nothing the entry above records is
retracted; this entry records what changed in the mechanism it describes.

A resumed sitting carries the whole of what the earlier ones spent, not the
graded part of it. The checkpoint is written at PAIR boundaries, so a stop
part-way through a pair charges calls that no unit row accounts for; one final
checkpoint is written on the stop path and records them as abandoned spend
(`AbandonedSpend`), per arm, with the model-work seconds they burned, and the
next sitting charges them — `charged_usage_by_arm` and
`charged_model_work_seconds`, the graded rows plus the abandoned ones — against
the same ceilings before it makes a call. It accumulates across stops. Two
other rules follow from the same file: a resumed sitting writes into an output
directory of its own, and `assert_the_tail_can_be_recorded` refuses by name a
replay already on disk for a seed still to run rather than overwriting it,
because a stop leaves the unit it was inside half-recorded; and a resume may
not be narrower than the checkpoint it continues, so a unit count that would
drop a finished seed is refused instead of reported. The identity a resume is
held to is a NAMED set of files (`ARM_SURFACE_SOURCES` plus every file of the
prompt directory), which this amendment widens to
`agents/strategic/prompts/loader.py`, which builds the Jinja environment and
selects the renderers, and to `orchestrator/game.py`; the constant states where
the rest of the run path is covered instead, rather than claiming the digests
cover every byte an arm renders through. The live gate's own paragraph on what
a second sitting must do is written by this commit as well, and states the same
rules where a runner reads them.

The frozen analysis does not move here either. The five constants the entry
above lists are the same bytes at `0185182d` as at `78b136bd`, and the test
that holds them compares the tree against the revision the log names rather
than trusting this sentence. As with the entries above, this entry cannot name
the commit that writes it; the record commit that does changes this document,
the card and the tests that hold this section to the history, and no instrument
byte.

## Resumption clause (2026-09-14)

The owner's decision 2 of
[the diagnosis of 2026-09-13](../../tasks/diagnosis-2026-09-13-live-run-stops.md),
approved on 2026-09-14 in the coordinator's session and recorded in
[the calibration card](../../tasks/work/fresh-deduction-calibration.md). It is
quoted here verbatim, which is what authorizes a live resume:
`assert_resume_is_authorized` looks for these bytes in this file and refuses a
live `--resume` without them, and a test holds the sentence below and the
module's `RESUMPTION_CLAUSE` byte for byte identical.

> A run stopped by transport exhaustion, a credential failure or a process crash may be resumed once per stop, from its last checkpoint and under this manifest, with the interrupted unit's spend and model-work time carried into the next sitting; a stop by a limit, a truncation, a digest or provenance mismatch, or the legacy body handle is final.

What of it the code enforces, and what it does not:

- **The carried spend is arithmetic — for a stop that unwinds.** A stop writes
  one final checkpoint on the stop path recording the interrupted pair's spend
  and its model-work seconds as `AbandonedSpend`, and the next sitting charges
  those — with every graded unit's — against the same ceilings before it makes
  a call. This is the mechanism the entry of `0185182d` above describes and the
  tests in `TestCheckpointAndResume` hold. It is reached by every stop that
  unwinds the process, an interrupt included: `run_instrument` catches
  `BaseException` for that write and re-raises an interrupt unchanged, so a
  Ctrl-C or a SIGTERM carries its pair's spend like a transport failure does.
- **A stop that runs no code carries nothing, and the runner closes it.** A
  SIGKILL, an OOM kill or a power loss writes no final checkpoint, because no
  handler runs. The last checkpoint is then the previous PAIR boundary, and the
  interrupted pair's spend — up to one pair — is not in it, so a resume would
  rebuild its run budget without it. The clause above still authorizes that
  resume; carrying the spend across it is the runner's step, not the
  instrument's: before resuming from a stop of that class the runner reads the
  abandoned sitting's output directory and its stdout for what the pair had
  already charged, and records it in the run's own record beside the stop. This
  is stated rather than claimed because the alternative — a document asserting
  a carry the code cannot make for this class — is the more dangerous error.
- **The same run, or none.** A resume is refused on any provider unless the
  checkpoint's execution manifest, held-out freeze, arm-surface digests, limits
  and sampling configuration are still this tree's, it continues at the next
  unrendered seed, and it writes into an output directory of its own.
- **"Once per stop" and the final-stop list are the runner's.** A checkpoint
  records no stop class, so no code refuses a second resume or a resume after a
  limit stop: the runner applies those two rules and the run's record states
  which stop each sitting followed. Recorded here as discipline rather than as
  a gate, because a document that claimed a refusal the code does not make
  would be the more dangerous of the two errors.

## Development calibration (2026-09-14)

The owner's decision 1 of the same diagnosis, approved in the same session and
recorded in the same card: a bounded live measurement on DEVELOPMENT inputs,
which the first authorization forbade
(`tasks/work/fresh-deduction-authorization.md:159-160`). Its purpose is the
root the diagnosis names — this evaluation was sized in charged tokens,
enforced in reserved ones, and only ever met the real provider on the held-out
run itself — so the ceilings a fourth authorization is written from come off
this endpoint instead of off a projection. The clause, quoted verbatim and
checked for by `assert_calibration_is_authorized`, which refuses a live
calibration without these bytes in this file:

> A development calibration may spend on the first five accepted seeds of a converted band, both arms, once and under the calibration limits; it grades nothing, reads no held-out prefix, and writes aggregates only.

**The mode.** `experiments/fresh_deduction_instrument.py --calibrate`. It runs
both arms of each drawn seed sequentially through the same path the evaluation
runs — `run_unit`, the same client wrapper, the same budgets, the same arms in
the same order — because what it measures is what THAT path costs. It grades
nothing: no grader is called, no paired statistic is computed and no meeting
outcome is reported, so no unit of it can reach the frozen analysis. The
analysis below is untouched by it, and a test holds those strings byte for byte.

**The inputs.** The first `CALIBRATION_PAIRED_SEEDS = 5` accepted seeds,
ascending, of a CONVERTED band's freeze record — by default
[held-out/manifest-band-3000-3999.json](held-out/manifest-band-3000-3999.json),
whose first seed a stopped run rendered on 2026-09-10 and whose set has been
development data since. Each prefix is rebuilt with the unchanged generator
(`experiments.held_out_prefixes.build_prefix`, driven with the record's own
roster and map) and held to the digest that record froze; a mismatch is a stop.
`verify_calibration_set` refuses [the held-out record](held-out/manifest.json)
by name, refuses any path that is not one of `CONVERTED_BANDS`' records, and
refuses a record whose `status` is not `development`. The held-out set is not
read on this path at all: `verify_frozen_set` is never called by it.

| Field | Value |
| --- | --- |
| Calibration per-unit token ceiling | 60,000 input / 12,000 output |
| Calibration run-level token ceiling | 600,000 input / 120,000 output |
| Calibration wall-clock deadline | 1 h of model work within a 1.5 h elapsed deadline |
| Calibration per-call token cap | turn 2,048 output / vote 1,024 — the run's own on 2026-09-14, unchanged for it. The fourth authorization below raised the RUN's turn cap to 4,096 on the strength of what this calibration measured; the calibration's own ceilings were approved against the 9,216-token schedule these caps reserve, so they are frozen together as `CALIBRATION_SAMPLING` and this spent mode reproduces the draw it made. A calibration sizing a run that draws at 4,096 would have to draw at 4,096 and would need its own ceilings on its own card |
| Calibration sampling temperature | turn 0.4 / vote 0.2 — the run's own, unchanged |
| Calibration transport bound | 4 attempts per call at a 180 s per-attempt wall — the run's own, unchanged |
| Calibration units | 5 paired seeds x 2 arms = 10 units, about 60 model calls |
| Calibration dollar limit | $0.00 marginal, on the same flat-rate subscription and for the same reason as the run's cost statement above |

The three caps that are NOT re-sized are the point: a calibration that drew
differently would measure a distribution the run it sizes never draws from.
The four ceilings that are re-sized are the calibration's own — they are
`CALIBRATION_LIMITS` in the instrument, `assert_calibration_is_authorized`
refuses a live calibration under any other limits, `assert_live_run_is_authorized`
refuses the held-out run under these, and `assert_limits_are_feasible` accepts
these for ten units at the caps this calibration drew at while still refusing
the 2026-09-07 ceilings for a hundred at either cap. That last qualification is
the fourth authorization's doing and is stated rather than absorbed: since the
run's turn cap moved to 4,096 these ceilings pay for ten units of the 2,048
draw they were approved against and not for ten units of the run's, and
`assert_calibration_is_authorized` now holds a live calibration to
`CALIBRATION_SAMPLING` for exactly that reason.

**What it writes.** One aggregate JSON committed under
`audits/deduction-candidate/calibration-<date>/`: per arm and per call type the
completion count, mean, p95 and max of input and output tokens; the defaults,
the provider-billed refusals and the retried and unaccounted attempts per arm;
per-unit usage rows; the pace in model-work seconds per attempt; and a re-sized
ceiling proposal. It carries no prompt, no prefix, no step and no outcome, and
the evaluation's own `assert_report_holds_no_prefix_bytes` runs over it. The
rendered prompts of a calibration are development data and are still not
committed: its replays go to the `--output-dir` the runner names, which is not
under version control.

**The proposal rule**, computed by `ceiling_proposal` and quoted in every
output: the per-unit output ceiling is max(the 9,216-token reservation
schedule, 3 x the largest unit measured); the per-unit input ceiling is 3 x the
largest unit measured; each run-level ceiling is the whole design's unit count
x the measured mean unit x 1.5, raised to that unit count x the largest unit
measured where the mean rule falls below it, because that product is the floor
`assert_limits_are_feasible` enforces; every figure is rounded up to the next
1,000 tokens. The proposal authorizes nothing — a ceiling is the owner's, on a
card — and the output states in the gate's own words whether the instrument
would accept it. The reservation schedule it clears is the schedule of the caps
it DREW at, which is why its 14,000 per-unit output figure is not the 16,000
the fourth authorization wrote down: the card raised the run's turn cap on the
strength of the same measurement, and a ceiling for a run that draws at 4,096
has to clear 15,360. That step is the owner's judgment, made on the card, and
it is the one figure in the table above that is not the proposal's.

**The commands.** The live calibration, which is the runner's and nobody
else's:

```sh
.venv/bin/python -m experiments.fresh_deduction_instrument \
  --calibrate \
  --provider featherless \
  --execution-manifest audits/deduction-candidate/execution-manifest.md \
  --i-am-the-runner \
  --output-dir <a directory outside version control> \
  --json audits/deduction-candidate/calibration-<date>/calibration.json
```

The dated directory in that `--json` path does not exist beforehand and the
invocation makes it: the destination is created — or the path refused, at exit
2, before a single call — by `_preflight_json_destination`, and the payload is
printed to stdout before it is written. A once-only measurement may not be lost
to its own output path, in either direction.

Then the refresh of the rehearsal double's committed usage profile from that
output, which makes no call:

```sh
.venv/bin/python -m experiments.fresh_deduction_instrument \
  --refresh-usage-profile audits/deduction-candidate/calibration-<date>/calibration.json \
  --profile-out tests/experiments/deduction_usage_profile.json
```

Refreshing that profile moves what the feasibility gate is calibrated against:
`CALIBRATED_UNIT_INPUT_TOKENS` and `CALIBRATED_UNIT_OUTPUT_TOKENS` are held
equal to the profile's largest charged unit by
`test_the_calibration_is_the_largest_unit_the_archives_charged`, so the two
constants move with it in the same commit or that test is red.

## Fourth authorization (2026-09-14)

The owner's decision 3 of
[the diagnosis of 2026-09-13](../../tasks/diagnosis-2026-09-13-live-run-stops.md),
approved in the same session as the two clauses above and written up as
[the fourth authorization card](../../tasks/work/fresh-deduction-authorization-4.md):
ceilings re-sized from a live measurement rather than from a projection. This
section is dated apart from the three above because it follows a measurement
rather than a stop or a diagnosis. It reaches the per-call cap row, the token
budget row, the enforcement text and the verification section; no held-out
outcome informed it, because the calibration it rests on drew five paired seeds
of a CONVERTED band and graded nothing.

**2026-09-14 (`b80cb92e`) — the turn cap is raised and the four token ceilings
are re-sized from the calibration.** The per-call token cap row now reads turn
4,096 output / vote 1,024, and the total token budget row 3,710,000 input /
459,000 output run-level with 106,000 / 16,000 per unit; both are copied
verbatim from that card's Constraints table and
`AUTHORIZED_TURN_MAX_TOKENS`, `AUTHORIZED_RUN_MAX_*` and `AUTHORIZED_UNIT_MAX_*`
carry the same numbers. Every other row of the table is #437's or the third
authorization card's, unchanged.

The basis is
[the development calibration of 2026-09-14](calibration-2026-09-14/calibration.json),
the section above this one. Sixty calls on five paired seeds measured, per
unit, a reference mean of 21,026 input / 1,108 output and a candidate mean of
28,430 / 3,137, with a largest unit of 35,232 / 4,590; the ceilings are three
times that largest unit per dimension and, run-level, the larger of a hundred
units at the measured mean x 1.5 and a hundred units at that largest unit. The
turn cap is the one value the three approved decisions did not name, and one
observation forced it: the largest candidate-arm turn charged 2,036 output
tokens against the 2,048 cap — 1 of 15 candidate turns — a truncation is a stop
with no retry, and the committed lab rows for this model ran at
`max_tokens=4096`. The vote cap is unchanged; the largest ballot measured was
237.

Raising the turn cap moves what a unit RESERVES, which is the unit of account
the three stopped runs were enforced in: `unit_output_reservation` is now
3 x 4,096 + 3 x 1,024 = 15,360, and the reservation-policy quotation under "How
each limit is enforced" carries those bytes. That is why the per-unit output
ceiling is 16,000 and not the 14,000 the calibration's own `ceiling_proposal`
printed: a proposal reserves against the caps it MEASURED, and lifting it to
the schedule of a raised cap is a judgment, made on the card. With that lift,
`assert_limits_are_feasible` accepts `AUTHORIZED_LIMITS` — the first time the
gate the diagnosis of 2026-09-13 installed has passed on the committed numbers.
The refusal it was built for is kept as a plant rather than retired with the
defect: the 4,000 ceiling merged on 2026-09-07 is still refused, now against
the wider schedule, and the two gate tests that used to rely on the committed
limits being infeasible plant those ceilings as the authorized set instead.

The calibration mode keeps the caps it drew at, and the section above says so
in its own table. Its ceilings were approved against the 9,216-token schedule
those caps reserve; following the run to 4,096 would authorize six calls they
cannot pay for, which is the defect this gate exists to refuse. So
`CALIBRATION_SAMPLING` freezes the calibration's draw,
`assert_calibration_is_authorized` holds a live calibration to it, and the
committed calibration output stays re-derivable from this tree. Sizing a run
that draws at 4,096 would need a calibration that draws at 4,096 under ceilings
that can pay for it; neither is authorized here, and no second calibration is
authorized at all.

**Round-1 review correction, same date.** The entry above moved the per-unit
output ceiling to clear the reservation schedule but left the run-level check
comparing against charged spend alone. `GameBudget.preflight`
recurses into its parent, so the RUN budget sees a call's full output cap on
top of everything the run has charged, exactly as the unit budget does: a
run-level output ceiling of 311,600 — a hundred units at the largest archived
unit, which is how the card sized 459,000 — could not have paid for its own
last call. `assert_limits_are_feasible` now adds one turn cap to the run-level
OUTPUT comparison and the reservation-policy quotation above says so; the input
dimension takes no such term, its pre-flight being the prompt's own estimated
length rather than a cap. No authorized figure moves: the corrected bound is
315,696 and this table already binds 459,000. The correction is recorded on
[the limits card](../../tasks/work/fresh-deduction-limits-4.md) with its
planted case and the commit its commands are pinned to.

**Round-2 review correction, same date — a residual this entry does NOT
close.** The corrected run-level bound is 315,696 only because the instrument's
calibrated per-unit output figure is the three stopped runs' archived 3,116.
The run ceiling this table binds was sized from a DIFFERENT figure: the
calibration's largest measured unit, 4,590 output tokens, times a hundred
units — 459,000 to the token. That is exactly the shape the corrected gate
refuses. Were
`tests/experiments/deduction_usage_profile.json` refreshed to the calibration's
own figures, `assert_limits_are_feasible` would refuse `AUTHORIZED_LIMITS`:
100 x 4,590 plus the 4,096 the last call reserves is 463,096 against a 459,000
ceiling. The input dimension clears either figure (100 x 35,232 = 3,523,200
against 3,710,000), so the residual is one comparison wide. It is recorded
rather than repaired here for one reason: 459,000 is an owner-authorized number
on
[the fourth authorization card](../../tasks/work/fresh-deduction-authorization-4.md),
and a card that may not move it may not close a gap that only a move can close.
Handed back to that card and to the owner, with the profile refresh
[the calibration card](../../tasks/work/fresh-deduction-calibration.md) already
left open: whichever is done first, the other has to follow, because the
ceiling and the profile are the two sides of one comparison. Nothing in the run
this document authorizes changes meanwhile — the gate passes on the profile
this tree carries, and
`test_the_run_output_ceiling_does_not_clear_the_calibrations_largest_unit`
holds the residual so it cannot be lost.

Nothing else moves. The primary outcome, the decision rule, the minimum
actionable effect, the tradeoff bound and the stop rule are the same bytes the
sections below quote, and a test holds them so. The provider, the model, the
prompt set, the temperatures, the roster, the wall windows, the transport bound
and the dollar limit are unchanged. No recording, report, DTO or weight byte
moves and no experiment becomes ON.

Two obligations were left open by this entry when it was written and are
discharged by the round-3 entry below: the Inputs table bound the 6000-6999
band, which
[the fourth freeze card](../../tasks/work/held-out-prefix-freeze-4.md) replaces
with 7000-7999 and marks development, and the rehearsal of the whole pipeline
under these limits on that band. This entry names the code commit it is written
against rather than the commit that carries it, for the reason the entries
above record — a commit cannot carry its own hash — and the record commit that
writes it moves no instrument byte.

**Round-3 re-binding, same date — the Inputs table moves to the fourth band and
the rehearsal is re-made under these ceilings.** The fourth freeze is merged
into the branch that carries this entry, so the record at
[held-out/manifest.json](held-out/manifest.json) is band 7000-7999 and the
6000-6999 record sits beside it as
[held-out/manifest-band-6000-6999.json](held-out/manifest-band-6000-6999.json),
marked `development` because the stopped run of 2026-09-13 rendered seeds 6000
and 6001 to the model. The Inputs table below now binds 7000-7999 — accepted
seeds 7001-7057, eight `witnessed_kill` skips, every number read off that
record rather than retyped, which
`test_the_manifest_binds_a_committed_held_out_record` holds — and names all
three converted bands with their dates and their record paths, which
`test_the_inputs_row_names_every_converted_band` holds against the records
themselves. With the row moved,
`assert_manifest_binds_the_live_band` passes instead of refusing: while the row
named one band and the freeze record another, that gate shut every live path,
which is what a stacked delivery is for. The verification section below is
re-made on the new band under `AUTHORIZED_LIMITS` and `AUTHORIZED_SAMPLING` —
the ceilings and the caps this table binds — and the rehearsal clears
`assert_limits_are_feasible` and completes at $0.00 over all 100 units;
`test_the_rehearsal_is_green_under_the_fourth_authorizations_limits` is that
run as a committed case. No authorized figure moves in this entry: it re-binds
inputs and re-measures headroom, and the ceilings, the caps, the frozen
analysis and the residual recorded above are the bytes the paragraphs above
left.

## Accounts prompt set v4 (2026-09-15)

Decisions 1 and 2 of
[the diagnosis of 2026-09-15](../../tasks/diagnosis-2026-09-15-truncation-stop.md),
approved by the owner on that date and written up as
[the v4 accounts revision card](../../tasks/work/accounts-prompt-set-v4.md).
This section is dated apart from the authorizations above because it is not
one: it moves what the CANDIDATE ARM IS ASKED FOR and nothing it is judged by.
The primary outcome and its rubrics, the decision rule, the minimum actionable
effect, the tradeoff bound and the stop rule are the bytes the sections below
quote; every cap, ceiling, wall, transport bound and dollar limit in the table
above is unchanged; the schema is untouched; and no unit has been run under
these bodies, nor is one authorized by this entry.

**2026-09-15 — the three bounds the reference family already carried are
ported into the candidate's account templates, and
`ACCOUNT_PROMPT_SET_REVISION` advances `v3` to `v4`
(`agents/strategic/prompts/loader.py:1248`).** The candidate ballot
commissioned deliberation and gave it one unbounded place to land, which is
what stopped the fourth run at unit 26 of 100 on a ballot at the 1,024-token
vote cap. Three edits, all on the `*_accounts.j2` family that only the
`combined_accounts` arm renders; the reference family keeps its bytes and is
what each edit is copied from rather than a re-invention of it:

- **The ballot's rationale budget.** `vote_ballot_accounts.j2` now asks for ONE
  short sentence (~20 words) and carries `vote_ballot.j2`'s own warning that a
  long rationale can overrun the output limit and truncate the JSON, which
  discards the vote. An honest limit, recorded with the fix: a budget bounds
  the symptom, not the channel — decoding is non-thinking by the model lock, so
  deliberation still has nowhere to go but the answer, and the reference arm
  shows a bound holding it to ~100 characters rather than removing it.
- **The citation form.** The same line shows the bare `{agent}:{tick}:{seq}`
  observation id — WITHOUT the `obs ` tag word `agents/memory/store.py` renders
  around it, which is render dressing rather than part of the id — with a
  literal example built from the voter's own id. The response skeleton keeps
  `primary_reason_observation_id` NULL, exactly as `vote_ballot.j2`'s own
  skeleton does: the form is shown in prose and never pre-filled into the
  object a model copies verbatim. Corrected in round 3 of review — an earlier
  draft of this bullet, and of the fix as delivered, pre-filled the skeleton
  with the literal example, which is copyable into an EJECT, and a copied
  literal that is not in the voter's own valid set is nulled and the ejection
  coerced to SKIP: the very defect this bullet repairs, re-entering through
  its own example.
- **The turn bound.** `_account_rules.j2` asks for one short phrase in an
  accusation's and a corroboration's `"reason"`, and
  `accusation_round_accounts.j2`'s reply instruction asks for 1-2 short
  sentences and then a stop in place of an explanation of what a citation does
  and does not establish. It is also the only proposed lever against the
  public-transcript role leak the diagnosis measured (2 of 13 candidate games,
  0 of 13 reference): `_account_rules.j2` already forbids that leak in words,
  and a prohibition alone did not hold in this register. The owner's reading of
  decision 9 is that the leak does not block the next run on its own, so the
  per-arm leak count is pre-declared as a reported diagnostic on the next
  calibration rather than as a gate here.

**ONE-SIDED EFFECT — declared here before anything is measured.** The citation
repair is neither a style note nor measurement-neutral. On the fourth run 13 of
14 candidate EJECT citations were nulled and 12 ballots were coerced to SKIP —
`meetings/manager.py` nulls an id that is not in the voter's own valid set,
with no suffix recovery by design, and then coerces the now-uncited EJECT to
SKIP whenever the target carries no contradiction flag — against none of either
on the reference arm. Supplying the format therefore converts coerced SKIPs
into live ejections ON THE TREATMENT ARM ONLY: the fix raises the candidate's
ejection RATE, which is precisely the failure `WRONGFUL_EJECTION_TRADEOFF`
polices, and the next run reads the wrongful-ejection bound against this entry
rather than reading a higher ejection count as a finding.

**ONE-SIDED EFFECT, second channel — the turn bound reaches a grader too.**
An earlier draft of this section called the other two edits measurement-neutral
on the ground that neither a ballot's rationale nor a turn's prose is an input
to any grader. Half of that is WITHDRAWN: turn prose IS one.
`grade_citation_relevance` grades a ballot that cites a TURN through
`_turn_bears_on`, which walks the cited turn's dumped structure rather than a
named field list — `CITATION_RELEVANCE_RUBRIC` says so in as many words, "its
claims and its free text included" — so a cited turn is RELEVANT to the ejected
player when it is that player's own or names them anywhere in its content, the
turn's `free_text` and each claim's `"reason"` included. Those are exactly the
two fields the turn bound shortens, and `every_citation_relevant` is a conjunct
of the primary outcome `supported_correct_ejection`. The declared direction is
DOWNWARD and on the candidate arm alone: shorter prose names fewer players, so
a ballot citing a bounded turn is likelier to be graded OFF_TARGET for the
ejected player and its unit likelier to score 0. The next calibration therefore
may not attribute a shift in the candidate's citation relevance to the citation
repair alone — two of the three edits move graded inputs, and they push in
opposite directions. Only the rationale half of the withdrawn claim survives:
no grader reads a ballot's `rationale_text`, so the rationale budget moves
prompt bytes and no graded input. Both halves are behavioural facts about the
instrument rather than a reading of it, and
`tests/experiments/test_accounts_v4_measurement_surface.py` pins them.

**Run 4's 24 complete units are not poolable with what follows.** The three
edits move the candidate's measured surface, so a unit recorded before them and
a unit recorded after them are not two draws from one instrument; the fourth
run's 24 complete units stay what they are, a record of the bodies that
produced them, and nothing after this entry may be pooled with them.

**The arm-surface digest moves, and no committed constant pins it.** Every file
of `agents/strategic/prompts/qwen3_6_27b` is hashed into `arm_surface_digests`
alongside `ARM_SURFACE_SOURCES`, so these three templates and
`agents/strategic/prompts/loader.py` all move it. The digest is recomputed from
the tree rather than pinned by a literal, so no recorded byte needs editing —
but `assert_checkpoint_matches` compares a resuming run against the checkpoint's
recorded digests, so the fourth run's sitting (PR #458, branch
`work/fresh-deduction-run-4` at `5f2383ea`, unmerged) is no longer resumable.
That is the intended consequence of a moved surface, not a defect in the
checkpoint.

**No recording, no re-record, no calibration.** The account bodies are
reachable only behind two default-OFF levers: `public_account_version` and
`attributed_testimony_version` default to `None` in both
`orchestrator/experiment_config.py` and `meetings/evidence_profile.py`,
`.env.example` carries both switches commented out, and
`public_account_prompt_versions` returns `None` when neither is set. No
committed recording renders these bodies, so no sample is rebuilt and no report
is re-scored, and every committed account stamp under `audits/` stays at the
revision it recorded — a stamp records which bodies ran, not which bodies are
current, which is why the 2026-09-14 calibration record keeps `v3`. The second
calibration and the fifth run are authorized by their own cards, not by this
entry.

## Development calibration 2 (2026-09-15)

The owner's decision 7 of
[the diagnosis of 2026-09-15](../../tasks/diagnosis-2026-09-15-truncation-stop.md),
approved with the rest of that section as a set on the same day and written up as
[the second calibration card](../../tasks/work/fresh-deduction-calibration-2.md).
A SECOND calibration beside the one above and not a replacement of it: the
2026-09-14 section, its clause and its numbers are the record of a spend that
has been made, and nothing here edits them.

Why a second one. The fourth run stopped at unit 26 of 100 on a ballot whose
author was that seed's impostor — one truncation in thirteen
impostor-authored candidate ballot draws, Wilson 95% [1.4%, 33.3%], P(a clean
50-pair run) = 1.8%. The first calibration could not have seen it: fifteen
candidate ballots, about five impostor-authored, 0.4 expected events, and at
n=15 its p95 IS its maximum under `PERCENTILE_RULE`. It measured tokens, not
role. This one measures what the fifth run would actually draw — sixty paired
seeds at the RUN's own caps, both arms — and reports it split by the author's
hidden role. The clause, quoted verbatim and checked for by
`assert_calibration_is_authorized`, which refuses a live second calibration
without these bytes in this file:

> A second development calibration may spend on the first sixty accepted seeds of the converted bands, taken in the order those bands were converted, both arms, once and under the calibration-2 limits; it grades nothing, reads no held-out prefix, counts a per-call truncation as a measurement rather than a stop, and writes aggregates only.

**The mode.** `experiments/fresh_deduction_instrument.py --calibrate
--calibration-mode 2026-09-15`. The same path the evaluation runs — `run_unit`,
the same client wrapper, the same budgets, the same arms in the same order —
because what it measures is what THAT path costs. It grades nothing: no grader
is called, no paired statistic is computed and no meeting outcome is reported,
so no unit of it can reach the frozen analysis. The analysis below is untouched
by it, and a test holds those strings byte for byte.

**Two authorized modes, each whole.** `CALIBRATION_MODES` carries both, and
`calibration_mode_for` accepts a calibration only when its limits, its sampling
configuration and its seed count are ONE of them together. Every crossing is
refused with the fields named: sixty seeds under the first mode's ceilings is a
draw its 12,000-token per-unit output cannot pay for, five seeds under the
second's is a spend nobody approved, and either mode drawing at the other's caps
measures a distribution the run it sizes does not draw from. Each mode's clause
authorizes that mode's spend and no other.

**The inputs.** The first `CALIBRATION_2_PAIRED_SEEDS = 60` accepted seeds,
ascending, taken across `CONVERTED_BANDS` in the order those bands were
converted: all fifty of
[held-out/manifest-band-3000-3999.json](held-out/manifest-band-3000-3999.json)
and then 5000 to 5009 of
[held-out/manifest-band-5000-5999.json](held-out/manifest-band-5000-5999.json).
No single record holds sixty, so the draw spans records; the ordering rule is
the list and the count, with nothing left to the runner, and the CLI refuses a
`--calibration-record` in this mode for that reason. Each prefix is rebuilt with
the unchanged generator (`experiments.held_out_prefixes.build_prefix`, driven
with the record's own roster and map) and held to the digest that record froze;
a mismatch is a stop, in every record of the draw and not only in the first.
`verify_calibration_draw` refuses [the held-out record](held-out/manifest.json)
by name, refuses any path that is not one of `CONVERTED_BANDS`' records, refuses
a record whose `status` is not `development`, and refuses a draw that runs out
of accepted seeds before sixty — fifty of them measures a different thing. The
held-out set is not read on this path at all: `verify_frozen_set` is never
called by it. Seeds 3000 to 3004 were rendered by the calibration of 2026-09-14,
which changes nothing: a converted band is development data from its conversion,
not from its rendering. The report's inputs block names every record it drew
with that record's sha256 and the seeds taken from it.

| Field | Value |
| --- | --- |
| Calibration-2 paired seeds | 60, ascending across `CONVERTED_BANDS` in order: all fifty of `held-out/manifest-band-3000-3999.json`, then 5000-5009 of `-5000-5999.json` |
| Calibration-2 per-unit token ceiling | 60,000 input / 16,000 output |
| Calibration-2 run-level token ceiling | 4,500,000 input / 450,000 output |
| Calibration-2 wall-clock deadline | 5 h of model work within a 6 h elapsed deadline |
| Calibration-2 per-call token cap | turn 4,096 output / vote 1,024 — `AUTHORIZED_SAMPLING` itself, because the point is to measure the draw the fifth run makes |
| Calibration-2 sampling temperature | turn 0.4 / vote 0.2 — the run's own, unchanged |
| Calibration-2 transport bound | 4 attempts per call at a 180 s per-attempt wall — the run's own, unchanged |
| Calibration-2 units | 60 paired seeds x 2 arms = 120 units, about 720 model calls |
| Calibration-2 dollar limit | $0.00 marginal, on the same flat-rate subscription and for the same reason as the run's cost statement above |

The ceilings are the mode's own and `assert_limits_are_feasible` accepts them
for 120 units at these caps: per-unit output 16,000 against the 15,360-token
schedule `unit_output_reservation` computes for the raised turn cap; per-unit
input 60,000 against the 24,282 of the largest archived unit, and about 1.6x the
36,743 the fourth run's largest unit charged; run-level output 450,000 against
120 units of the largest archived unit plus one further turn cap of in-flight
headroom; run-level input 4,500,000 against 2,913,840. `assert_live_run_is_authorized`
refuses the held-out run under these ceilings and `assert_calibration_is_authorized`
refuses this calibration under the run's, exactly as the two authorizations
above refuse each other's.

The wall is the binding limit and is stated rather than absorbed: 720 calls in
5 h allows 25.0 s per call, against 17.23 s per attempt pooled and 21.85 s on
the candidate arm on 2026-09-14, so the margin is 1.45x pooled and 1.14x at the
slowest arm pace this evaluation has measured. A calibration has no checkpoint
and no resume: a stop is reported with its partial accounting, and a second
sitting needs the owner's say, as every live sitting does.

**A per-call truncation is a MEASUREMENT in this mode, and only in it.** The
owner's decision 6 of the same diagnosis is No for the live run: a cap
truncation there is a stop, `STOP_RULE` below is unedited and quoted byte for
byte, and `assert_live_run_is_authorized` builds a client that raises
`PerCallCapExceeded` on that response. In a calibration the same ordering is
self-defeating — a calibration sent to measure the rate at which a ballot runs
past its cap cannot stop at the first one, or it reports one event and no
denominator. So in this mode the cap branch of `_unusable_response` returns no
stop, the truncated ballot or turn takes the meeting layer's shipped fail-soft
(a marked SKIP, or a placeholder turn) exactly as any other payload that fails
schema validation does, and the call is counted per arm, per call type and per
voter role with the `finish_reason` the provider reported. The identity branch
still stops in this mode: a response from a model this run is not authorized for
is never a datum. The relaxation is a calibration rule and the live run's stop
rule is unchanged.

**What it reports.** Everything the 2026-09-14 output carries, plus the unit of
account the fourth run's stop needed: per arm, per call type and split by the
voter's or speaker's hidden role, the draws and the mean, p95 and max of output
tokens and of the character lengths of `rationale_text`, `claims[].reason` and
`free_text`; the truncation count with its `finish_reason`, whose denominator is
impostor DRAWS, since a fail-softed ballot is a draw that produced no rationale;
and the count of impostor-authored ballots whose rationale OPENS by stating that
role or a kill. Counts and lengths only — no prose, no prompt, no prefix, no
step and no outcome — and the evaluation's own
`assert_report_holds_no_prefix_bytes` runs over the payload.

**The public-transcript role leak, pre-declared as a reported column of the
fifth run.** The owner's decision 9 of the same diagnosis, ruled on 2026-09-15:
the leak does not block the next run on its own, and the next cards pre-declare
a per-arm leak count as a reported diagnostic so the primary outcome can be read
against it. This is that pre-declaration. A leaking turn is a committed public
turn whose speaker is an IMPOSTOR and whose text states, in the first person and
without attributing the statement to someone else, either that role or a kill
that speaker committed; the rule is `ROLE_LEAK_RULE`, quoted in every
calibration-2 output, and the fourth run's own three shapes are what it is held
to — two positives and the rebuttal the diagnosis counted out, with a
supposition or a question ("if I am the impostor, why would I report the body?")
counted out the same way. The count is an ESTIMATE carrying error in BOTH
directions and is not a floor: the rule reads no intent, so a confession its
shapes do not match is missed, and its guards see one sentence at a time, so an
attribution spread across two is counted. It is a reported
diagnostic and not a gate: no stop condition reads it, the decision rule below
does not mention it, and it changes no primary outcome. The fifth run reports
the same column, so the leak is visible beside the result rather than argued
about after it.

**What it writes.** One aggregate JSON committed under
`audits/deduction-candidate/calibration-2-<date>/`, in the shape the first
calibration committed with the role split, the leak count and the per-record
inputs block added. Its rendered prompts are development data and are still not
committed: its replays go to the `--output-dir` the runner names, which is not
under version control.

**The proposal rule**, computed by `ceiling_proposal` and quoted in every
output, gains the term the gate has always enforced: a proposed run-level OUTPUT
ceiling is at least the unit count times the largest unit measured PLUS one
per-call turn cap, because the run's last call is reserved against the run
budget after everything before it has been charged. Without it a proposal
reproduces the open item of 2026-09-14 — 459,000 is exactly a hundred times that
calibration's largest unit and 4,096 short of what a hundred such units reserve,
and it clears the gate today only because the committed usage profile still
carries the older 3,116. The proposal's own feasibility check now runs against
the CALIBRATION's measured maxima, because the question a proposal answers is
whether these ceilings pay for the run THIS sitting measured; the same check
against the committed profile is reported beside it. The proposal authorizes
nothing: a ceiling is the owner's, on a card.

**The commands.** The live second calibration, which is the runner's and nobody
else's:

```sh
.venv/bin/python -m experiments.fresh_deduction_instrument \
  --calibrate \
  --calibration-mode 2026-09-15 \
  --provider featherless \
  --execution-manifest audits/deduction-candidate/execution-manifest.md \
  --i-am-the-runner \
  --output-dir <a directory outside version control> \
  --json audits/deduction-candidate/calibration-2-<date>/calibration.json
```

Then the refresh of the rehearsal double's committed usage profile from that
output, which makes no call:

```sh
.venv/bin/python -m experiments.fresh_deduction_instrument \
  --refresh-usage-profile audits/deduction-candidate/calibration-2-<date>/calibration.json \
  --profile-out tests/experiments/deduction_usage_profile.json
```

Refreshing that profile moves what the feasibility gate is calibrated against:
`CALIBRATED_UNIT_INPUT_TOKENS` and `CALIBRATED_UNIT_OUTPUT_TOKENS` are held
equal to the profile's largest charged unit by
`test_the_calibration_is_the_largest_unit_the_archives_charged`, so the two
constants move with it in the same commit or that test is red. That refresh
belongs to the sitting that produces the measurement, not to the card that built
the mode: a profile rebuilt from a fixture-driven rehearsal would lower both
constants to a serialisation length and quietly widen the gate.

**This section authorizes no run.** It authorizes a spend, once, on development
inputs, under the limits in its table; the call itself still needs the runner's
explicit invocation naming this file, and the fifth held-out run is a separate
authorization on a separate card.

## Fifth authorization (2026-09-15)

The owner's fifth authorization
([the card](../../tasks/work/fresh-deduction-authorization-5.md)), opened once
the second calibration reported, as section 9 of
[the diagnosis of 2026-09-15](../../tasks/diagnosis-2026-09-15-truncation-stop.md)
said it would be. Like the fourth, this section is dated apart because it
follows a measurement rather than a stop or a diagnosis, and no held-out
outcome informed it: the sitting it rests on drew sixty paired seeds of
CONVERTED bands and graded nothing. It reaches the total token budget row, the
enforcement text and the verification section. The per-call caps, the
temperatures, the wall, the dollar limit, the roster and the execution mode are
untouched, and so are the "Fourth authorization (2026-09-14)" and "Accounts
prompt set v4 (2026-09-15)" sections above, whose two declared one-sided
effects stand.

**2026-09-15 — the three run and per-unit ceilings are re-sized from the second
calibration, and the committed usage profile becomes that sitting's.** The
total token budget row now reads 3,844,000 input / 422,000 output run-level
with 116,000 / 16,000 per unit, copied verbatim from that card's Constraints
table, and `AUTHORIZED_RUN_MAX_INPUT_TOKENS`, `AUTHORIZED_RUN_MAX_OUTPUT_TOKENS`
and `AUTHORIZED_UNIT_MAX_INPUT_TOKENS` carry the same numbers.
`AUTHORIZED_UNIT_MAX_OUTPUT_TOKENS` stays 16,000, because 3 x 4,176 is 12,528
and the figure is held to the 15,360-token reservation schedule either way.
Every other row of the table is #437's, the third authorization card's or the
fourth's, unchanged.

The basis is
[the second development calibration of 2026-09-15](calibration-2-2026-09-15/calibration.json),
the section above this one — one sitting, 120 units, 720 calls, $0.00 marginal
— read through `CEILING_PROPOSAL_RULE` by `ceiling_proposal`, whose output the
card's table quotes verbatim. That sitting measured, per unit, a reference mean
of 20,862 input / 1,142 output and a candidate mean of 22,734 / 1,609, with a
largest unit of 38,440 input / 4,176 output. Per unit the ceilings are three
times that largest unit with the output figure held to the reservation
schedule; run-level they are the larger of a hundred units at the measured mean
x 1.5 and a hundred units at that largest unit, with ONE further turn cap on
the output side for the run's last in-flight reservation — 100 x 4,176 + 4,096
= 421,696, rounded up to 422,000.

**The run-level OUTPUT ceiling FALLS, from 459,000 to 422,000, and no budget
was tightened.** The rule is followed and v4 made units smaller on output: the
candidate arm's per-unit output mean fell from 3,481.5 at v3 to 1,608.9, and
its largest unit from 4,816 to 4,176. The INPUT ceiling rises for the same
reason read the other way — the largest unit's input rose to 38,440, so a
hundred of them need 3,844,000 against the 3,710,000 the fourth authorization
bound, and the gate refuses that ceiling on the refreshed profile. A ceiling
here is an anomaly detector rather than a budget, both provider pre-flight
rates being zero, so it moves with the measurement in whichever direction the
measurement went.

**The refreshed profile now sizes the gate.**
`tests/experiments/deduction_usage_profile.json` is rebuilt from that sitting's
`calibration.json` by the `--refresh-usage-profile` command the section above
quotes, and `CALIBRATED_UNIT_INPUT_TOKENS` / `CALIBRATED_UNIT_OUTPUT_TOKENS`
move with it to 38,440 / 4,176 in the same commit, which is what
`test_the_calibration_is_the_largest_unit_the_archives_charged` requires. The
profile that stood there before — the three stopped live runs' 38 rows, the
only archived FAULTS this evaluation has — is committed beside it as
`tests/experiments/deduction_stopped_runs_usage_profile.json`, and the eight
rehearsals whose subject is a fault read that one. `RESERVATION_POLICY` embeds
both constants, so the quotation under "How each limit is enforced" moved with
them; its numbers are this sitting's.

**This section authorizes limits, not a run.** The fifth held-out run is
[its own card](../../tasks/work/fresh-deduction-authorization-5.md)'s, dispatched
after this manifest carries these values and after
[the fifth freeze](../../tasks/work/held-out-prefix-freeze-5.md) binds band
8000-8999 in the Inputs table above. No pilot, no smoke run and no re-run is
authorized, on flat-rate service or otherwise.

**Stacking round, same date — the Inputs table moves to the fifth band and the
verification section is re-made on it.** The obligation the paragraph above left
open is discharged here.
[The fifth freeze](../../tasks/work/held-out-prefix-freeze-5.md) is merged into
the branch that carries this entry, so the record at
[held-out/manifest.json](held-out/manifest.json) is band 8000-8999 and the
7000-7999 record sits beside it as
[held-out/manifest-band-7000-7999.json](held-out/manifest-band-7000-7999.json),
marked `development` because the stopped run of 2026-09-15 rendered thirteen of
its prefixes — seeds 7001 to 7016 in accepted order, that span less its three
skips — before the vote cap truncated a candidate-arm ballot on seed 7016. The
Inputs table above now binds 8000-8999 — accepted seeds 8000-8057, eight
`witnessed_kill` skips, every number read off that record rather than retyped,
which `test_the_manifest_binds_a_committed_held_out_record` holds — and names
all four converted bands with their dates and their record paths, which
`test_the_inputs_row_names_every_converted_band` holds against the records
themselves. With the row moved, `assert_manifest_binds_the_live_band` passes
instead of refusing: while the row named one band and the freeze record another,
that gate shut every live path, which is what a stacked delivery is for. The
Roles table's preparer row gains the fifth preparer session and PR #463. The
verification section below is re-made on the new band under `AUTHORIZED_LIMITS`
and `AUTHORIZED_SAMPLING` — the ceilings and the caps the table above binds: the
dry run's input heuristic and its graded counts are the fifth band's (the shape
moves, 49 terminal units and one `partial` an arm becoming 50 and none), and the
replay rehearsals clear `assert_limits_are_feasible` and complete at $0.00 over
all 100 units, their token totals unmoved because the double is keyed by arm and
call type rather than by prefix. No authorized figure moves in this entry: it
re-binds inputs and re-measures headroom, and the ceilings, the caps, the frozen
analysis and the refreshed profile recorded above are the bytes the paragraphs
above left.

## The instrument

`experiments/fresh_deduction_instrument.py`, new for this evaluation and
separate from the two committed MECHANICS_ONLY harnesses
(`experiments/deduction_evaluation.py`, `experiments/investigation_evaluation.py`),
which keep refusing real providers and are neither imported, subclassed nor
relaxed. The run is driven through the shipped public entry points only:
`orchestrator.game.HeadlessGame`,
`orchestrator.game.build_default_meeting_runner` and the public
`orchestrator.game.TacticalAgent`. Its own bytes are hashed into every report
it writes (`instrument_sha256`), so a result names the instrument that produced
it.

`build_default_agent_factory` is NOT used, and the reason is a limitation rather
than a preference: its agents choose their own actions, so they cannot execute a
frozen scripted prefix, and the `AgentMemory` it constructs carries none of an
arm's channel versions. The instrument therefore builds the same public
`TacticalAgent` with the same public `CrewmatePolicy` / `ImpostorPolicy` the
default factory builds, and hands it the prefix schedule and the arm's memory —
the construction `experiments/deduction_scenarios.py::run_case` already uses.

## Candidate, reference and source inventory

| Field | Value |
| --- | --- |
| Reference arm | `repaired_clock` — `format_version=2`, `evidence_reasoning_version=2`, nothing else |
| Candidate arm | `combined_accounts` — the reference plus `public_account_version=1` and `attributed_testimony_version=1` |
| Observation clock | Temporal version 2 on BOTH arms. Recorded per unit and checked against the arm (`GameProvenance.temporal_observation_version`); a unit that does not carry its arm's clock and config is a provenance failure and a stop |
| Out of scope | Investigation. It changes the world the prefix froze, so it cannot be paired on an identical prefix |
| Prompt set | `qwen3_6_27b` |
| Prompt/template versions | Recorded per arm from the replay rows the runner writes (`MeetingReplayEntry.prompt_versions`) and carried in the report's per-arm `prompt_versions`. The two arms render different template families by design, so their markers differ; two different marker sets WITHIN one arm is a source change mid-run and a stop |
| Map and roster | `canonical_1`, 4 players / 1 impostor / 1 task per crewmate, 3 living voters at meeting open |
| Generator source identity | The 22 `GENERATOR_SOURCES` digests in [the freeze manifest](held-out/manifest.json), asserted by `tests/experiments/test_held_out_prefixes.py::test_the_committed_manifest_regenerates_from_its_own_band` |
| Dependency/runtime identity | Python 3.11 and the committed `uv.lock`; the run is made from a single commit, recorded with its results |
| Recorded configuration | Each unit writes a replay carrying its experiment config and substrate flags; the instrument reads them back and refuses a unit whose recorded identity is not its arm's |

## Inputs

| Field | Value |
| --- | --- |
| Held-out inputs | The 50 proof-free scripted physical prefixes drawn on [the fifth freeze card](../../tasks/work/held-out-prefix-freeze-5.md) by a preparer session that ran no arm, recorded as hashes only in [held-out/manifest.json](held-out/manifest.json). PR #463 is that freeze, and this re-binding is stacked on it |
| Seed band | 8000–8999 drawn ascending, first 50 passing prefixes; accepted seeds run 8000–8057 with 8 skips, all `witnessed_kill`. Four earlier bands are development data since a stopped run of their date rendered a prefix of theirs, and each freeze record is kept beside this one, marked `development`, rather than deleted: 3000-3999 since 2026-09-10, as [held-out/manifest-band-3000-3999.json](held-out/manifest-band-3000-3999.json); 5000-5999 since 2026-09-13, as [held-out/manifest-band-5000-5999.json](held-out/manifest-band-5000-5999.json); 6000-6999 since 2026-09-13, as [held-out/manifest-band-6000-6999.json](held-out/manifest-band-6000-6999.json), whose stopped run of that date rendered seeds 6000 and 6001; and 7000-7999 since 2026-09-15, as [held-out/manifest-band-7000-7999.json](held-out/manifest-band-7000-7999.json), whose stopped run of that date rendered thirteen prefixes — seeds 7001 to 7016 in accepted order, which is that span less its three skips — the band this row bound until the fifth freeze marked it `development` on 2026-09-15 |
| Seed list | Published in the freeze manifest's `accepted[]`. The prefixes themselves are NOT committed anywhere: the runner regenerates them with `experiments.held_out_prefixes.generate()` and refuses to proceed if any digest or skip differs |
| Development inputs | The seven hand-authored cases in `experiments/deduction_scenarios.py`, seed 1 by construction. Their digests are recorded in the freeze manifest and asserted absent from `accepted[]` |
| Legal schedules | Each prefix is replayed through the engine, which accepts or rejects every step; a prefix whose hashed steps the engine did not resolve step for step never gets a digest |
| Provider-response repetitions | One. Each unit is one prefix and one meeting; no response is sampled twice and no unit is repeated |
| Run order | Sequential, seed ascending, both arms per seed before the next seed |
| Maximum opportunities | 50 prefixes × 2 arms = 100 meeting units, ~600 model calls. An attempt that came back with no completion at all — an empty body, a transport failure, a retryable status, a send that outran the per-attempt wall — is retried up to three times and then a stop; a truncation and an exhausted limit are stops with no retry. The partial state is reported rather than replaced, and every retried attempt is counted per arm and per unit. An attempt whose payload failed schema validation is NOT a stop: the meeting layer substitutes a placeholder turn or a marked SKIP ballot for it at an accepted ~1-in-50 rate, and the instrument counts every such substitution per unit and per arm (see "Meeting-internal defaults" below) so it stays visible instead of being silently replaced |

## Sampling configuration, caps and limits — the owner's authorized values

Copied verbatim from [the authorization card](../../tasks/work/fresh-deduction-authorization.md)'s
Constraints table, whose reasoning of record is item B of
[the 2026-09-07 decision memo](../../tasks/owner-decisions-2026-09-07.md) — with
one row that is NOT from that table and is marked as such, and three the owner
later moved. The wall row is copied verbatim from
[the third authorization card](../../tasks/work/fresh-deduction-authorization-3.md)'s
Constraints table instead, which restates #437's other values unchanged and
carries the owner's instruction of 2026-09-13; see "Amendments after the stopped
run of 2026-09-13". The per-call token cap and the total token budget are
copied verbatim from
[the fourth authorization card](../../tasks/work/fresh-deduction-authorization-4.md)'s
Constraints table, which re-sizes them from the live development calibration of
2026-09-14 and restates #437's other values unchanged; see "Fourth
authorization (2026-09-14)". The total token budget row is copied verbatim from
[the fifth authorization card](../../tasks/work/fresh-deduction-authorization-5.md)'s
Constraints table instead, which re-sizes it from the SECOND live development
calibration of 2026-09-15 and leaves the per-call caps where the fourth
authorization put them; see "Fifth authorization (2026-09-15)". The authorization
card binds no temperature; the preregistration
(`preregistration.md:113-115`) requires this manifest to bind the sampling
configuration, so the sampling-temperature row states the values shipped in
`meetings/manager.py` and the instrument serves them explicitly rather than
inheriting them. It moves no owner-authorized number.

| Field | Value |
| --- | --- |
| Provider | `featherless` |
| Model | `Qwen/Qwen3.6-27B` (locked 2026-07-12, Task 16.2). Non-thinking with `enable_thinking=false` pinned on every call, `response_format_mode = json_object`, prompt set `qwen3_6_27b` — all carried from the model lock, not re-decided here |
| Per-call token cap *(raised 2026-09-14 — from the fourth authorization card)* | turn 4,096 output / vote 1,024. The turn cap is raised from the shipped 2,048 on 2026-09-14: the calibration's largest candidate-arm turn charged 2,036 output tokens against 2,048 (1 of 15 candidate turns), a truncation is a stop with no retry, and the committed lab rows for this model ran at `max_tokens=4096`; the vote cap is unchanged (largest measured ballot 237) |
| Sampling temperature *(not from the authorization card — see the note above)* | turn temperature 0.4 / vote temperature 0.2 — the shipped values (`meetings/manager.py:211,213`), bound here rather than inherited. The instrument passes an explicit `MeetingConfig` carrying them, records both on every report, and a test asserts they are still the shipped values, so a later edit to those module defaults breaks a test instead of silently moving this frozen design's sampling distribution |
| Total token budget *(re-sized 2026-09-15 — from the fifth authorization card)* | 3,844,000 input / 422,000 output run-level, and 116,000 input / 16,000 output per unit. Hard stop. Basis, from `audits/deduction-candidate/calibration-2-2026-09-15/calibration.json`'s `proposal`: per unit, 3 x the largest measured unit (38,440 input; 4,176 output gives 12,528) with the output figure held to the reservation schedule under the raised turn cap (3 x 4,096 + 3 x 1,024 = 15,360) and rounded up to 16,000; run-level, the larger of 100 units x the measured mean x 1.5 and 100 units x the largest measured unit on each dimension, plus ONE further turn cap on the output side for the run's last in-flight reservation (input 3,844,000; output 100 x 4,176 + 4,096 = 421,696, rounded up to 422,000). The run OUTPUT ceiling FALLS from the fourth authorization's 459,000: no budget was tightened, the rule is followed and v4 made units smaller on output. Both provider pre-flight rates are zero, so these ceilings are a stop rule sized as an anomaly detector, not a budget |
| Wall-clock deadline *(widened 2026-09-13 — from the third authorization card)* | 6 h of model work within an 8 h elapsed deadline. Widened from 4 h / 6 h on 2026-09-13: the second attempt measured 26.6 s/call over its four resolved calls against 11.7 s/call on 2026-09-10, and six hundred calls at the slower pace need about 4 h 26 m; the 2 h elapsed margin still covers one recorded 3h21m provider-side stall (`audits/audit-phase-21-adopting-record.md:373-380`) |
| Dollar limit | $0.00 marginal, recorded as bookkeeping and not as an enforcement mechanism. The provider's zero pre-flight rate disables the USD dimension, so only the token budget and the deadline can stop a run |
| Roster | 4p1i with 3 living voters at meeting open. A change of roster invalidates the token budget above and requires a new authorization |
| Execution mode | sequential |
| Death-tick body handle | Left as temporal v2 renders it in both arms, stated in the manifest, and asserted by the regex over the rendered prompts and the frozen prefixes |

### Cost statement

Required even on flat-rate service, and quoted verbatim from the authorization
card:

> This evaluation runs on the Featherless AI Premium plan, a flat-rate hosted
> subscription at $25/month authorized by the owner on 2026-06-25
> (`llm/provider.py:74`). Its marginal cost is $0.00: no per-token charge is
> incurred, and the provider-keyed zero rate makes every recorded `cost_usd` on
> this run exactly 0.0 by construction rather than by measurement. The resources
> this run actually consumes are subscription capacity and elapsed wall time:
> 600 projected model calls and about 2.0 M tokens over a 6-hour elapsed window,
> against a plan whose concurrency ceiling is four units and whose 32B-class
> request costs two — i.e. two workers saturate it, and this run uses one worker,
> two of those four units. The dollar cap recorded in this manifest is $0.00 and
> is not an enforcement mechanism on this provider: `BudgetedLLMClient`'s USD
> pre-flight dimension self-disables at a zero rate
> (`llm/featherless_client.py:243-244`, `llm/budgeted_client.py:118-126`), so the
> token budget and the wall deadline are the only limits that can stop this run.
> The same run on a metered provider would cost about $2.17 on
> `claude-haiku-4-5` or $6.52 on `claude-sonnet-4-6` at the rates in
> `llm/provider.py:58-61` and would require its own separate authorization;
> nothing in this statement carries over to one.

### How each limit is enforced

Every number above is a module constant in
`experiments/fresh_deduction_instrument.py`
(`AUTHORIZED_*`, gathered into the frozen `AUTHORIZED_LIMITS` and
`AUTHORIZED_SAMPLING`), so the instrument enforces the manifest rather than
describing it, and `tests/experiments/test_fresh_deduction_instrument.py`
asserts this document quotes each of them.

- **Provider and model.** The live client is built from the authorized values,
  not from the shell: `build_authorized_client` pins `AILIBI_LLM_PROVIDER` and
  both model variables to `featherless` and `Qwen/Qwen3.6-27B` and carries
  exactly one value over from the ambient environment, the API key.
  `_InstrumentClient` then refuses a RESPONSE whose `model` is not the
  authorized one, on the call that returns it, so a hosted endpoint serving a
  different checkpoint is a stop rather than something noticed in the report
  afterwards. A completion the provider billed for and then refused on its own
  schema validation is judged the same way, off the `model` its parse-failure
  metadata carries: a checkpoint swap does not become acceptable because the
  body it served failed to parse. The run also checks the client's real TYPE
  against the provider it
  claims to be (`assert_client_matches_provider`): a run labelled `fake` may only
  hold the offline fake provider, and a live-labelled run may hold neither it nor
  no client at all, so neither a metered client smuggled in under the offline
  label nor a fixture's output recorded as a live result is possible.
- **Cost rates.** `_InstrumentClient` exposes the WRAPPED client's USD
  pre-flight rates rather than rates of its own, so the budget layer prices
  whatever this instrument composes. On this provider the pass-through is zero
  (`llm/featherless_client.py:244-245`), which is exactly what the cost
  statement above says: the USD dimension is disabled and only the token budget
  and the wall deadline can stop the run.
- **Per-call cap.** `_InstrumentClient` refuses a call whose `max_tokens` is not
  one of the two values the table above binds — the authorized turn cap of
  4,096 and the shipped vote cap of 1,024 — and refuses a response whose output
  reached its cap — a truncation is a stop, not a datum. That reading is taken off the
  completion, not off the parse: a body cut off at the cap is the usual reason a
  payload then fails schema validation, so the same check is applied to the
  `output_tokens` a refused call's parse-failure metadata reports.

  **2026-09-15 — the truncation reading is observed as well as inferred.** From
  this date the cap check reads the provider's own `finish_reason` beside the
  `output_tokens >= max_tokens` inference above, and EITHER of them stops the
  run. A `finish_reason` of `"length"` is the provider saying the completion
  reached its cap, which is what this bullet already refuses, so the union can
  only stop a run earlier than the inference alone and can never turn a stop
  into a datum. A call on which the two signals disagree — `"length"` below the
  cap, or any other word at it — stops the run and is COUNTED, reported per arm
  as `cap_signal_disagreements` beside `retried_calls` and
  `unaccounted_attempts`. A call whose provider reported no reading records
  null, and null is not a disagreement, because an absent reading contradicts
  nothing. The reading rides a refused call's parse-failure metadata as well as
  a response, since the run of 2026-09-15 stopped through the refused path and
  a check that reached only responses would have missed it. This changes no
  limit, no sampling value and no word of `STOP_RULE`; the fourth run cannot be
  re-read against it, because the field was never recorded there
  (`tasks/work/featherless-finish-reason.md`;
  `tasks/diagnosis-2026-09-15-truncation-stop.md` §5 fix D, §6 decision 3).
- **Sampling.** The two temperatures and the two caps are served through an
  explicit `MeetingConfig` built from `AUTHORIZED_SAMPLING`, and a live run whose
  sampling configuration is not that one is refused before any client is built.
- **Token budget.** One `llm.budget.GameBudget` per unit with a run-level parent,
  so every charge reaches both ceilings. What the run then checks about that
  accounting is quoted verbatim from `SPEND_RECONCILIATION`:

  After each unit the recorded spend is reconciled against the enforced budget
  snapshot over every call the provider charged: the meeting row's resolved
  calls plus every failed attempt the replay records with usage — a payload a
  real provider validated and refused before the recording client could log
  it, whose tokens the budget charged off the parse-failure metadata. A
  zero-spend default marker is not a charged call, so a manager-side
  validation of a returned payload, whose spend the meeting row already
  carries, is counted once and not twice. This is the token budget's
  accounting check rather than a limit of its own: what it can find is a unit
  whose recorded calls do not add up to what the budget charged, and that unit
  stops the run the way every other unit failure does.

  The ceiling itself is enforced by the budget's pre-flight, on the call that
  would cross it, and — for the one charge that never meets a pre-flight — by a
  post-unit read-back quoted verbatim from `BUDGET_CAP_READBACK`:

  After each unit both budgets are also read back against the caps they were
  built with, because one kind of charge never meets a pre-flight: a call the
  provider billed and then refused on its own schema validation is charged
  after the fact, off the parse-failure metadata, and the resulting overrun is
  downgraded to a note on the exception the meeting layer then fail-softs. On
  a unit's last call the per-unit ceiling would otherwise be crossed with the
  budget then discarded, and on a run's last call the run ceiling with nothing
  further to pre-flight. A budget found past its cap stops the run on the unit
  that crossed it: the tokens are already spent, and the stop is what keeps
  the next unit from spending more.

  Both ceilings are stated in one unit of account and enforced in another, and
  that difference is what stopped the run of 2026-09-13. The rule is quoted
  verbatim from `RESERVATION_POLICY`:

  The token ceilings are enforced on RESERVED spend and were sized on
  CHARGED spend. Every call is pre-flighted against its full per-call
  output cap before it is sent, so one unit reserves 3 x 4,096 for its
  turns and 3 x 1,024 for its ballots — 15,360 output tokens — whatever
  it is then billed. A per-unit output ceiling below that schedule
  authorizes six legal calls it cannot pay for, and refuses one of them
  by arithmetic rather than by spend; the instrument therefore refuses
  such a ceiling before a live run starts, rather than discovering it
  partway through one. The run-level ceilings are the same question one
  level up, because the pre-flight recurses into the parent budget, and
  are checked against the largest per-unit spend the committed usage
  profile carries — 38,440 input and 4,176 output, the largest of the
  120 units the second live development calibration of 2026-09-15
  measured at accounts revision v4 — rather than against a mean
  projection: a hundred units at the largest unit this evaluation has
  measured is what a run ceiling has to be able to pay for, because a
  ceiling that cannot is a stop rule that fires on arithmetic near the
  end of a run it has already paid for. The run-level OUTPUT ceiling
  carries one further 4,096-token turn cap on top of that product,
  because the last call of the run is reserved against the run budget
  after the run has charged everything before it; the input dimension
  carries no such term, its pre-flight being the prompt's own estimated
  length rather than a cap.

  `assert_limits_are_feasible` is where it bites, before a credential, a client
  or a held-out prefix exists: it refuses a per-unit output ceiling below the
  reservation schedule above, a per-unit input ceiling below the largest unit
  the committed usage profile carries, either run-level ceiling below a hundred
  units at that figure, and a run-level OUTPUT ceiling that does not also clear
  the one turn cap its last call reserves against the run budget — 421,696
  tokens against the 422,000 authorized since 2026-09-15. Under the limits
  merged on 2026-09-07 it REFUSES — 4,000 per-unit output against a schedule of
  9,216 then and 15,360 now — which is deliberate and is the live gate failing
  closed: those numbers authorize six calls a unit cannot pay for. It also
  refuses the fourth authorization's own 3,710,000 run-level input ceiling on
  the refreshed profile — a hundred units of 38,440 need 3,844,000 — which is
  the refusal the fifth authorization answers and which
  `test_the_fourth_authorizations_run_input_ceiling_is_refused_on_this_profile`
  plants. It ACCEPTS the ceilings in the table above, which is what the fifth
  authorization card re-sized them to do and what
  `test_the_gate_accepts_the_fifth_authorizations_limits` holds; the refusal
  of the 2026-09-07 ceilings is still planted beside it. Nothing about noticing
  any of them needed a provider — it is arithmetic over the module constants
  this table binds.
- **Wall.** Two clocks, because the authorization names two limits: one
  `orchestrator.run_limits.RunDeadline` for the 8 h elapsed window, checked
  between units and inside the meeting, and a summed provider-call clock for the
  6 h of model work. The work clock bounds each provider await by what is LEFT
  of its window, the way `RunDeadline.run` bounds meeting work by what is left
  of the elapsed one, so the run stops DURING the call that exhausts the window.
  A clock charged only when a call returns would be a one-call-granular limit,
  and one call on this provider is not small: `llm/featherless_client.py` retries
  a send six times at a 600 s timeout with exponential backoff, so a run at
  5 h 59 m of model work could otherwise spend a seventh hour against an
  authorization of six. Each attempt is bounded by the tighter of that remaining
  window and the 180 s per-attempt wall below, and which of the two expired is
  what the cut-off means: the window is a limit reached and a stop, the
  per-attempt wall is an attempt that stopped answering and a retry. The cut-off
  attempt's elapsed wall is charged to the clock and its call recorded in the
  partial accounting with unknown (zero) usage before the stop is raised.
- **Transport.** A call that produced no completion is sent again by the
  instrument's own client wrapper, within a bound this document states, quoted
  verbatim from `TRANSPORT_RETRY`:

  A call whose attempt came back with no completion at all is sent again by
  this instrument's own client wrapper rather than by the provider client,
  so no recorded campaign changes behaviour: at most 4 attempts, one send
  and 3 retries, on any body the authorized client refuses to record a
  completion from — no choices, empty assistant content, or a usage block it
  cannot read token counts out of — as well as a transport failure, a
  retryable HTTP status, or an attempt that outran the 180 s per-attempt
  wall this wrapper bounds each send by — each retry after a short
  exponential backoff, and each attempt still bounded by what is left of the
  model-work window, which no retry may outlive. The last failure stops the
  run with the same partial accounting every other unit failure reports.
  Nothing that produced a completion is retried: a response that reached its
  output cap, a returned payload that failed schema validation, an exhausted
  budget or deadline and a refused live run are all left exactly as they
  were. Every retried attempt is recorded as an unaccounted attempt carrying
  zero tokens, which may have been billed for tokens this side cannot see:
  the provider client raises instead of returning a completion, and its
  refusal carries no usage onto the exception, so no usage rides any of
  these four classes and this wrapper has none to charge. A body it refused
  for the state of its usage block is no different here: what the adapter
  read, it did not pass on. The attempts are counted per arm and per unit —
  retried calls, unaccounted attempts and the trigger class of each — beside
  the meeting-internal defaults.
- **Dollar.** `max_cost_usd=0.0` on both budgets, which the provider's zero
  pre-flight rate makes bookkeeping rather than a brake — exactly as the cost
  statement says.
- **On any of these, the run stops** and raises with a partial-state record: the
  units completed out of those planned, per-arm calls and tokens including the
  stopped unit's spent-but-unusable calls, elapsed wall and model work. No retry
  and no widening is authorized by a stop. Every stop records the response that
  caused it BEFORE raising — a truncated or foreign-model response was still
  spent — and every way a unit can fail is one of these stops, including a
  provider transport failure and a mid-run legacy body handle, so an attempt
  that never resolved reports its partial state rather than escaping as a bare
  exception. A meeting-internal default is the one case that is NOT a stop; it
  is counted instead, immediately below.

### Meeting-internal defaults: counted, not stopped

The meeting layer does not abort a meeting on a payload that fails schema
validation. A turn falls back to a placeholder (`meetings/manager.py::_default_turn`)
and a ballot to a marked SKIP (`_vote_parse_default`, the cap-truncation runaway
class accepted at about 1 in 50 calls); each fires a `deadline_default`
`FailedCallReplayEntry` row. On the ~600 calls this manifest authorizes, that
rate puts roughly a dozen such substitutions inside a completed run, so a fixed
50-unit paired sample cannot be abandoned for one — but the preregistration
requires that "Missing or truncated attempts remain visible" (`preregistration.md:112`)
and that failed attempts are retained (`:136`), and a substitution nobody counts
is neither.

The instrument therefore reads those rows for every unit and reports them per
arm: `defaulted_turns`, `defaulted_votes`, `defaults_by_validation`,
`defaults_by_deadline`, `degraded_openings` (the Task 10.6 validation-degrade,
recognised by its typed `opening_degraded_unsure` turn annotation) and
`units_with_defaults`. A recorded default whose phase and trigger the instrument
cannot classify IS a stop: the producer's wording would have moved and the
counts would no longer be evidence.

Two consequences a reader of the results has to carry. A defaulted ballot is a
SKIP the voter did not choose, so it inflates the abstention side of the ballot
verdicts; and because the privileged grader's "every naming ballot supported"
is an `all()` over the ballots naming the ejected player, a defaulted ballot
removes a constraint rather than failing it, which biases the primary outcome
UPWARD. `units_with_defaults` per arm is the bound on how many of that arm's
decisions that can touch.

## The live gate: what actually authorizes a call

The manifest authorizes limits. A call additionally requires an explicit
invocation that names this file:

```sh
.venv/bin/python -m experiments.fresh_deduction_instrument \
  --provider featherless \
  --execution-manifest audits/deduction-candidate/execution-manifest.md \
  --i-am-the-runner \
  --output-dir <results directory>
```

`assert_live_run_is_authorized` refuses every provider except `fake` without a
`LiveRunInvocation`. Given one, it takes nothing on that object's word: it
re-resolves this file's own path under the repository root and requires the
invocation to name exactly it, re-hashes the file on disk and requires the
invocation's `manifest_sha256` to equal that digest, and requires the
invocation's model to be `Qwen/Qwen3.6-27B` — so a same-named file elsewhere on
disk, and a hand-built invocation carrying a path, digest or model of its own,
authorize nothing. It also refuses limits that are not `AUTHORIZED_LIMITS`, a
sampling configuration that is not `AUTHORIZED_SAMPLING`, and any `--units`
override: a live run is the whole frozen set, and a subset is the pilot this
manifest does not authorize. `LiveRunInvocation.naming` applies the same path
check when the invocation is built, and additionally refuses a manifest that does
not name the authorized provider, model and prompt set. `run_dry` refuses a
`LiveRunInvocation` outright, so the mechanics check cannot become the run.

No committed file outside this manifest's command above and
`experiments/fresh_deduction_instrument.py`, which defines the flag as
`LIVE_RUN_FLAG`, carries that flag: not a test, a workflow, a script or a card.
A test scans every tracked file whose suffix a command could be written in for
the constant itself, so the file doing the scanning carries no copy of the needle
and needs no exemption. Committed tests DO construct `LiveRunInvocation` objects
— proving each refusal above is what they are for — and none of them reaches a
provider.

A run may also write a per-unit checkpoint (`--checkpoint`) and be continued
from one (`--resume`), and the second of those is gated on this document rather
than on the code. `assert_resume_is_authorized` refuses a live resume unless
this manifest carries the owner's resumption clause — the sentence
`RESUMPTION_CLAUSE` holds. It carries that sentence since 2026-09-14, under
"Resumption clause (2026-09-14)" above, which is where the owner's decision and
its limits are stated; a describing paraphrase authorizes nothing, because the
gate looks for those bytes. A resume is also refused, on any provider, unless
the checkpoint's execution manifest, held-out freeze, arm-surface digests,
limits and sampling configuration are still this tree's: a resumed run is the
same run or it is none.

The calibration mode (`--calibrate`) is gated the same way and separately:
`assert_calibration_is_authorized` refuses a live calibration unless this
manifest carries `CALIBRATION_CLAUSE`, which it does since 2026-09-14 under
"Development calibration (2026-09-14)" above, and refuses it under any limits
but `CALIBRATION_LIMITS`, any sampling configuration but the authorized one,
any provider but `featherless`, and any seed count but five. Neither
authorization is the other's: the run's gate refuses the calibration's limits
and the calibration's gate refuses the run's.

What a runner has to do differently on a second sitting, and what the code does
for them: pass a NEW `--output-dir`, because the first sitting's directory holds
the half-recorded replay of the unit its stop was inside and a resume that would
land on it is refused by name; pass the same `--units` or more, because a resume
narrower than its checkpoint is refused rather than silently reporting units it
did not run; and pass `--resume` alone if the checkpoint is to keep advancing in
place, since `--checkpoint` defaults to the `--resume` path and a sitting that
wrote no checkpoint would lose its own progress to the next stop. The budgets
the second sitting starts from are the first one's whole spend: the units it
graded and the pair its stop abandoned, the latter recorded by a final
checkpoint written on the stop path — on every stop that unwinds the process,
interrupts included, and on none that does not. After a SIGKILL, an OOM kill or
a power loss there is no such write, so the runner carries the abandoned pair
themselves, as "Resumption clause (2026-09-14)" above states.

The gate and the frozen-set check both run BEFORE a client is constructed, and
that order is a property of the signatures rather than of the order two lines
happen to sit in: `assert_ready_for_a_live_run` runs the authorization gate and
then `verify_frozen_set`, and RETURNS the verified set, which
`build_authorized_client` requires as its first argument. A run whose held-out
set has moved therefore stops before a credential is read or a connection made.
The client that is then constructed is `build_authorized_client`'s, not
`build_default_client`'s: an invocation labelled `featherless` cannot reach
whatever provider and model the shell's `AILIBI_LLM_PROVIDER` /
`AILIBI_LLM_MEETING_MODEL` happen to name.

## Evidence privileges and grading

Three passes, in this order, and the order is a property of the signatures
rather than a convention.

1. **Supported (entitled inputs only).** `grade_supported` reads a ballot's
   `primary_reason_id` and `primary_reason_observation_id` and requires each
   citation to appear verbatim in a prompt THAT VOTER was handed. A citation
   found in another voter's prompt is not support. Verdicts are `supported`,
   `unsupported` (a citation is present and the voter's own prompts do not carry
   it) and `uncited` (a ballot carrying neither — a SKIP needs no citation).
   Ballots the meeting layer rewrote (`guard_rewrite_reason`) are counted
   separately and never count as the voter's own supported call.
2. **Relevance (recorded meeting, same entitled inputs).**
   `grade_citation_relevance` asks what the presence check cannot: whether the
   thing a ballot cited is ABOUT the player it named. Presence is not aboutness,
   and without this a ballot that guessed the impostor while citing an unrelated
   alibi, or a turn about somebody else, scored the primary outcome. The rule is
   frozen in `CITATION_RELEVANCE_RUBRIC` and quoted verbatim below. It reads the
   recorded turns and the voter's own prompts; no role and no support label is an
   input to it.
3. **Privileged (hidden roles).** `grade_privileged` takes the support grades as
   an ARGUMENT rather than recomputing them, so no support label can be revised
   after the role is known. It scores role-correctness (was the ejected player
   the impostor) and, separately, the three-way conjunction the primary outcome
   uses: role-correct, every naming ballot supported, every naming ballot's
   citation relevant. Relevance is computed here because the player it is judged
   against — the one the meeting ejected — is only fixed once the unit is
   finished.

Judge information never returns to a listener or a tactic: grading is a pure
function over a finished `UnitRecord`, the run path calls no grader at all
(pinned by a test that replaces every `grade_*` function the instrument defines
with a landmine and runs a unit anyway — the list read off the module rather
than typed into the test, so a grader added later is landmined the round it
lands), and the hidden roles are read off the final state only after the game
has returned.

The two arms are compared on prompts the instrument captured live, and every
recorded meeting call is checked to be one of those live inputs — a recording
that does not mirror what the model saw would let the grader score inputs that
never existed.

## Measures and denominators

Per unit, with counts beside every rate:

| Measure | Unit and denominator |
| --- | --- |
| Decision coverage | Units run / units planned (100). A stopped unit is reported, never dropped |
| Ejections | Per resolved meeting, per arm |
| Role-correct ejections | Per resolved meeting and conditional on an ejection, per arm |
| Wrongful ejections | Per resolved meeting, per arm: an ejection that landed on a crewmate. A skipped meeting is not wrongful. This is the count the acceptable-tradeoff bound below is computed on |
| Supported / unsupported / uncited ballots | Per ballot, per arm, with guard-rewritten ballots counted separately |
| Naming ballots and off-target citations | Per ballot, per arm: `naming_ballots` counts the ballots naming the ejected player and `off_target_citations` how many of those cited evidence that does not bear on that player. The pair says how often relevance rather than presence is what a unit turned on |
| Meeting-internal defaults | Per attempt, per arm: `defaulted_turns` and `defaulted_votes`, split by trigger into `defaults_by_validation` and `defaults_by_deadline`, plus `degraded_openings`. `units_with_defaults` counts the units carrying at least one, and is the bound on how many of that arm's decisions rest on a partly unauthored meeting |
| Retried provider attempts | Per attempt, per arm: `retried_calls` counts the calls this run had to send more than once and `unaccounted_attempts` the attempts that bought no completion and carried no usage this side can see, split by trigger into `attempts_by_trigger`. `units_with_retries` counts the units carrying at least one. Every unaccounted attempt is also a row in the per-arm `calls` total, carrying the `no-completion-returned` marker and zero tokens — what is known about it, not what it was billed — so the completions are `calls` minus `unaccounted_attempts` |
| Terminal vs partial units | A unit whose meeting ended the game is terminal; one that stopped at the tick after the report is deliberately partial. Neither is a game-win trial |
| Provider cost | Calls, input and output tokens, `cost_usd` and model-work seconds, per arm and per run, against the limits above |

The unit of analysis is the paired seed, not the ballot: three voters in one
meeting are correlated, so the paired difference is taken per seed.

## Decision rule, minimum actionable effect, acceptable tradeoffs and stop rule

Frozen here and in code (`PRIMARY_OUTCOME`, `DECISION_RULE`,
`MINIMUM_ACTIONABLE_EFFECT_UNITS`, `WRONGFUL_EJECTION_TRADEOFF`, `STOP_RULE` in
`experiments/fresh_deduction_instrument.py`) before any held-out outcome exists.

**Primary outcome — `supported_correct_ejection`.** Quoted verbatim from
`PRIMARY_OUTCOME_RUBRIC`:

A unit scores 1 when its meeting ejected the player whose hidden role is
IMPOSTOR and every ballot naming that player carried a citation that is both
PRESENT in that voter's own prompts (the supported grader) and RELEVANT to the
ejected player (the citation-relevance rule); otherwise 0. Role-correctness
alone, support alone and relevance alone are reported beside it and none of
them is the primary outcome.

**Citation relevance.** Quoted verbatim from `CITATION_RELEVANCE_RUBRIC`, frozen
with the rest of the analysis and amended into this manifest on 2026-09-09,
before any unit ran (see "Amendments before first run"):

A citation is RELEVANT to a named player when the evidence it identifies bears
on that player. For a transcript turn (primary_reason_id): the recorded turn is
the named player's own — they are its speaker, the case the ballot template
itself asks a voter to cite when a contradiction broke their account — or it
names that player anywhere in its recorded content, its structured
observations, its claims and its free text included. For an episodic
observation (primary_reason_observation_id): at least one line of that voter's
OWN prompts carrying the cited id also names that player, which is the rendered
'[obs ...]' memory line the id was copied from. A player id is matched as a
whole token, so p-1 does not match p-10. A citation naming a turn this meeting
did not record is not relevant to anyone. A ballot is RELEVANT when every
citation it carries is relevant, OFF_TARGET when it carries one that is not,
and UNCITED when it carries none. Relevance reads the recorded meeting and the
voter's own prompts only: no role, no trajectory and no support label is an
input to it.

**Estimator and test.** The two-sided exact binomial McNemar over the discordant
pairs, `scripts/paired_stats.py::exact_mcnemar_p`, on 50 paired units.

**Decision rule.** Quoted verbatim from `DECISION_RULE`:

combined_accounts advances to an explicitly scoped adopting review only if ALL
THREE hold on the 50 paired units: the two-sided exact McNemar p over the
discordant pairs (scripts/paired_stats.py::exact_mcnemar_p) is below 0.05; the
net paired difference b - c is at least 10 units; and the candidate's net
increase in wrongful crew ejections over the reference arm is no larger than
that net paired difference. Any other result is inconclusive, and inconclusive
is not success. A result in either direction is a measurement, never an
adoption: adoption stays a separate owner decision on a separate card.

`PairedResult.meets_decision_rule` is the conjunction of the three, computed
beside the test rather than left to a reader.

**Minimum actionable effect — 10 of 50.** Chosen for the resolution of this
design, not for a headline. The smallest net difference the exact test can call
at all on 50 paired units is 6 with no discordant pairs the other way
(`b=6, c=0` gives `p=0.03125`; `b=5, c=0` gives `p=0.0625`), so a bar of 6 would
be the significance boundary restated. A net of 10 stays below 0.05 for every
discordant total up to 20 (`b=15, c=5` gives `p=0.0414`) and fails at 22
(`b=16, c=6` gives `p=0.0525`), so it is a difference that survives the noise
this design can actually carry. Reproduce every figure with:

```sh
.venv/bin/python -c "import sys; sys.path.insert(0, 'scripts'); \
from paired_stats import exact_mcnemar_p as p; \
print([(b, c, round(p(b, c), 6)) for b, c in \
[(5, 0), (6, 0), (15, 5), (16, 6)]])"
```

**Acceptable tradeoffs — the wrongful-decision bound.** The preregistration
(`:116-118`, `:236-239`) requires the manifest to bind the acceptable tradeoffs
and names the wrongful decision among them. Quoted verbatim from
`WRONGFUL_EJECTION_TRADEOFF`:

A wrongful ejection is a unit whose meeting ejected a player whose hidden role
is CREWMATE. The candidate may not buy its supported-correct ejections by
ejecting more innocents: its net increase in wrongful ejections over the
reference arm, on the same 50 paired units, must be no larger than its net
paired gain b - c on the primary outcome. One extra wrongful ejection has to be
paid for by at least one extra supported-correct ejection. The bound is
one-for-one because the failure it guards against is a candidate that merely
raises the ejection RATE: converting reference-arm skips into ejections lifts
both counts together, and a candidate whose wrongful count rises at least as
fast as its supported-correct count has moved the meeting's willingness to eject
rather than its deduction. No ratio below one is asserted, because this design
resolves 50 paired units and a finer bound would be a number the sample cannot
carry.

The other tradeoffs the preregistration names are structural here rather than
numeric, and are bound by the design above: direct-evidence use is excluded by
construction (the held-out prefixes are proof-free, and the `- [x]` freeze
asserts no living crewmate holds a firsthand kill or vent observation), the
tactical layer is identical on both arms (the same public policies drive the same
frozen schedule), and the cost tradeoff is the $0.00 marginal statement with the
token and wall limits above.

**Stop rule.** Quoted verbatim from `STOP_RULE`:

The run stops, retains its partial evidence and unresolved accounting, and
authorizes no retry and no widening of any limit, on any of: a token budget
exhausted at either the per-unit or the run level; the elapsed wall deadline
or the model-work window, the latter cutting off the attempt in flight
rather than one call later; a per-call response that reached its output cap
(a truncation is a stop, not a datum); a held-out digest or skip that
differs from the frozen manifest; a rendered prompt or regenerated prefix
matching the legacy body handle; a unit whose recorded observation clock or
experiment config is not the arm's; or a recorded meeting default whose
phase and trigger this instrument cannot classify. A call that came back
with no completion at all — an empty body, a transport failure, a retryable
status, or an attempt that outran the per-attempt wall each send is bounded
by — is retried up to three times, then a stop carrying the same partial
accounting, with every attempt counted per arm and per unit. Retrying one of
those buys no new draw: an attempt that produced nothing is not a sample. A
body that reached its output cap and a returned payload that failed schema
validation ARE samples and are never retried, and neither is an exhausted
budget or deadline. A meeting-internal default is NOT itself a stop. The
meeting layer's shipped fail-soft substitutes a placeholder turn or a marked
SKIP ballot for a payload that failed schema validation, at an accepted rate
of about 1 in 50 calls, and a fixed 50-unit paired sample cannot be
abandoned for a substitution the engine is designed to make. Every such
substitution is instead counted per arm and per unit — turns and votes
separately, by trigger, with the units carrying any — and reported beside
decision coverage, so it is visible rather than silently replaced. No stop
condition reads an outcome: the 50 paired units are a fixed sample with no
interim analysis and no optional stopping, so nothing here can be tripped by
a result the run has produced.

**Possible decisions**, per the preregistration: advance for an explicitly scoped
adopting review, revise and evaluate a new version, reject, or gather more
evidence under a new authorized manifest. More evidence is not an automatic
spending authorization.

## Death-tick body handle

Left as temporal version 2 renders it, in both arms, and not masked. Under v2
`observation/body_ids.py` returns a handle carrying no death tick, so both arms
already render `body-p-N` by construction rather than by masking. The claim is
mechanical, not asserted: `assert_no_legacy_body_handles` runs the regex
`body-p-\d+-\d+` over every regenerated prefix before the run and over every
rendered prompt after each unit, and over the emitted report; a match is a stop.

## Roles

| Role | Session |
| --- | --- |
| Preparer | A session dispatched on [the freeze card](../../tasks/work/held-out-prefix-freeze.md). It built the deterministic generator, drew from the preregistered band, committed the hashes and opened the pull request the owner merged as `23a23c2d`. It ran no arm. A second session, dispatched on [the second freeze card](../../tasks/work/held-out-prefix-freeze-2.md) after the stopped run of 2026-09-10 rendered a prefix of the first band, drew 5000-5999 with the same generator, marked the first record `development` rather than deleting it, and opened PR #446. A third, dispatched on [the third freeze card](../../tasks/work/held-out-prefix-freeze-3.md) after the stopped run of 2026-09-13 rendered a prefix of the second, drew 6000-6999 the same way, marked the second record `development`, and opened PR #449. A fourth, dispatched on [the fourth freeze card](../../tasks/work/held-out-prefix-freeze-4.md) after the stopped run of 2026-09-13 rendered two prefixes of the third, drew 7000-7999 the same way, marked the third record `development`, and opened PR #456. A fifth, dispatched on [the fifth freeze card](../../tasks/work/held-out-prefix-freeze-5.md) after the stopped run of 2026-09-15 rendered thirteen prefixes of the fourth, drew 8000-8999 the same way, marked the fourth record `development`, and opened PR #463. None of the five ran an arm |
| Runner | A separate session dispatched on [the instrument card](../../tasks/work/fresh-deduction-instrument.md), started after that merge. It regenerates the set from the frozen band, verifies the committed hashes, and opens no prefix: no prefix is printed, logged or written into any report, and `assert_report_holds_no_prefix_bytes` refuses a report that carries one |
| Coordinator | Dispatches both and runs neither |

Inspecting a held-out input converts it to development data. A held-out result
that informs a fix marks this set development — recorded by setting the freeze
manifest's `status` to `development` — and a new band is frozen under a new
card. The prefixes are archived with the results after the run, when they are no
longer held out.

## Verification of this manifest

The offline mechanics check, re-made on the FIFTH held-out band under the
ceilings and the caps this document now binds. Run on this branch at the commit
that re-binds the Inputs table; that hash is named in
[the limits card](../../tasks/work/fresh-deduction-limits-5.md)'s Results
rather than here, because a commit cannot carry its own hash — the reason the
amendment entries above record — and only that card's `## Acceptance` and
`## Results` move after it, neither of which the dry run reads:

```sh
uv run python -m experiments.fresh_deduction_instrument --dry-run
```

100 units (50 prefixes × 2 arms), 600 calls, `total_cost_usd` 0.0, in about two
seconds of wall, written to the temporary directory the run makes for itself.
Every one of the 150 ballots an arm cast was a non-SKIP decision — 150 supported
ballots an arm, 1 guard-rewritten one among them rather than beside them,
because the guard column overlays the verdict columns rather than adding to
them (300 ballots over the two arms, one for each of the 600 calls that is not
a turn) — and 50 of each arm's 50 units reached a graded terminal outcome: 50
ejections each, 16 role-correct, 34 wrongful, 16 supported-correct, and 100
ballots naming the ejected player, two per ejection. No unit of either arm is
graded `partial` on this band, where the fourth band left one of each arm's
fifty: that was a fixture outcome rather than a stop — its three ballots named
three different players, so no majority formed — and which of the two shapes a
band produces is the prefixes' arithmetic, not a property of the pipeline. The
run completed all 100 units. The report carries the sampling
configuration it drew at (`turn_temperature` 0.4, `vote_temperature` 0.2, caps
4,096 / 1,024 — the caps the fourth authorization above raised the turn half of)
and the limits it ran under (3,844,000 / 422,000 run-level, 116,000 / 16,000 per
unit — the fifth authorization's, since 2026-09-15; the paragraph read
3,710,000 / 459,000 and 106,000 with the fourth's). Input tokens by the fake provider's
`len // 4` heuristic were 892,718 (`repaired_clock`) and 641,246
(`combined_accounts`); applying the decision memo's calibrated 1.28x real-input
ratio to their sum (1,533,964) gives about 1.96 M against the 3,844,000 this
manifest binds (51%), and the larger arm's 17,854 per unit gives about 22,900
against the 116,000 per-unit ceiling (20%) — headroom checks, not predictions,
because a real model writes a different transcript. The figures this paragraph
carried before this re-binding were the fourth band's, measured under these same
ceilings on 2026-09-15: 895,883 and 643,779 over 1,539,662, 49 ejections an arm
with 13 role-correct, 36 wrongful and 13 supported-correct, and 98 ballots
naming the ejected player. They are superseded with that band by the paragraph
you are reading, and the two sets differing only in the second significant digit
on input is what a re-binding between two draws of the same generator should
produce. The v4 account bodies and the round-3 ballot-skeleton revision of
2026-09-15 moved the candidate arm's figure alone (608,664 to 643,779, +5.8%, on
the fourth band), because only its templates gained bytes; on this band the same
one-arm gap reads 641,246 against the reference arm's 892,718.

**The output dimension, measured rather than assumed (2026-09-13).** The
paragraph above is an INPUT headroom check, and until this amendment it was the
only one: the fake provider's output figure is 66 tokens a call by
construction, so no committed run could say anything about the ceiling the
third live attempt actually hit. The replay rehearsal is the output half.
Re-run it with:

```sh
uv run pytest tests/experiments/test_fresh_deduction_instrument.py \
  -k "TestUsageReplay or TestFeasibility" -q
```

Under the re-sizing [the diagnosis](../../tasks/diagnosis-2026-09-13-live-run-stops.md)
puts to the owner (per unit 60,000 in / 12,000 out, run 3,600,000 / 350,000 —
the per-unit output figure is 16,000 here since the fourth authorization, which
is what clears the raised turn cap's schedule, and the two run figures are
3,900,000 / 430,000 since the fifth, which is what clears a hundred units of the
refreshed profile; neither changes a figure below, because what the double
charges does not depend on a ceiling it never reaches),
the rehearsal runs all 100 units and 600 calls at $0.00 in about seven seconds:
`repaired_clock` charges 1,072,642 input and 66,105 output (21,453 and 1,322 a
unit), `combined_accounts` 1,015,417 and 145,889 (20,308 and 2,918 a unit). The
candidate arm's mean unit is therefore 18.2% of the per-unit output ceiling
this manifest now binds and 19.0% of the schedule its six calls reserve, and the
run total of 211,994 output tokens is 50.2% of the 422,000 run-level ceiling
the fifth authorization binds (46.2% of the fourth's 459,000).
Measured against the ceilings this manifest bound before the fourth
authorization, the same totals read the other way: that mean unit was 72.9% of
a 4,000 per-unit ceiling and 31.7% of a 9,216-token schedule, and the run total
was **106.0% of the 200,000 run-level ceiling** — a complete run would have
stopped near its end on that ceiling even with the per-unit one fixed, which is
what the diagnosis projected from four units, what this measured over a hundred,
and what the re-sizing of 2026-09-14 answers. Input is 2,088,059: 54.3% of the
3,844,000 ceiling now, 87.0% of the 2.4 M one then. The candidate arm also
replays the refusal rate its archives carry — two of its nine archived turns —
as 33 defaulted turns across its 150, against none on the reference arm.

**The same rehearsal under THIS table's own ceilings, on the fifth band
(2026-09-14, re-made 2026-09-15).** The paragraph above runs under the
diagnosis's proposal, which
is not what the owner authorized. Since the fourth authorization the gate
accepts `AUTHORIZED_LIMITS`, so the rehearsal can be made under the authorized
ceilings themselves, and it is —
`tests/experiments/test_fresh_deduction_instrument.py::TestUsageReplay::test_the_rehearsal_is_green_under_the_fourth_authorizations_limits`,
600 calls over 100 units at $0.00, `assert_limits_are_feasible` cleared first
and 50 terminal units with no `partial` on either arm, the fifth band's own
shape (the fourth band's was 49 and one). The token totals are the paragraph
above's to the token, and that is the
point rather than a coincidence: the double replays an archived distribution
keyed by arm and call type, so what it charges depends on which arm and which
call type asked, never on which prefix the unit ran. Both paragraphs replay the
three stopped runs' archive, which since 2026-09-15 is committed as
`tests/experiments/deduction_stopped_runs_usage_profile.json` rather than as
the current profile: the refresh of that day moved the current profile to the
second calibration's 720 clean calls, and the figures here — the refusals and
the defaulted turns among them — are that archive's. The headroom figures above
therefore survive the re-binding from the third band to the fourth and again
from the fourth to the fifth without
being re-measured, and the figures that do depend on the prefixes — the fake
provider's input heuristic and the terminal-unit shape — are re-measured in the
dry-run paragraph and in the count just quoted instead.

**And the fifth authorization's own pair, on the fifth band (2026-09-15).** The
rehearsal above replays the three stopped runs' archive, because the paragraphs
it checks are that archive's. The pairing this section owes the fifth
authorization is its ceilings against the measurement they were sized on, and
that is
`tests/experiments/test_fresh_deduction_instrument.py::TestUsageReplay::test_the_rehearsal_is_green_on_the_refreshed_profile_under_the_new_limits`:
`assert_limits_are_feasible` cleared first, then 600 calls over 100 units at
$0.00 replaying the refreshed profile — the second calibration's 720 clean calls
— under `AUTHORIZED_LIMITS` and `AUTHORIZED_SAMPLING`. `repaired_clock` charges
1,038,160 input and 56,765 output over 300 calls, `combined_accounts` 1,134,054
and 80,441 over 300, for a run total of 2,172,214 input and 137,206 output:
56.5% of the 3,844,000 run-level input ceiling and 32.5% of the 422,000 output
one. Those totals are the ones this case carried before the re-binding, to the
token, for the reason the paragraph above gives — the double is keyed by arm and
call type, never by prefix — so the re-run on band 8000-8999 is a confirmation
rather than a re-measurement, and the run writes to a temporary directory and
opens no prefix.

Under the limits and the turn cap this manifest bound until the fourth
authorization, the same rehearsal stops where the live
run of 2026-09-13 stopped and says the same thing: `LLM budget exceeded on
output_tokens: current=3116.0 + delta=1024.0 > cap=4000.0`, on the candidate
arm, 5 of 100 units completed. The figure is the archived unit's own, because
the rehearsal replays that unit's calls including the turn the provider billed
and refused. Both halves of that day are planted to reproduce it — the four
ceilings and the 2,048 turn cap — because at 4,096 the first call of the first
unit is refused instead, which is a different stop.

Nothing graded in either rehearsal is reported here, and none of it is
evidence about the arms. The double's decision does not depend on the arm, and
the refusals it replays are the candidate arm's by construction, so any paired
difference it produces is the fixture's arithmetic rather than a measurement —
the same caveat the dry run below carries, and it is stronger here because the
replayed refusals are asymmetric by design.

The bounded retry is exercised here rather than only in its unit cases, because
the card that added it owes a run of the whole pipeline through one empty
completion. The plain run above does not reach it — the dry-run provider
answers every call, so both arms report `retried_calls` 0,
`unaccounted_attempts` 0 and no trigger at all. The same 600 calls with the
empty-body double answering one of them are a committed case,
`tests/experiments/test_fresh_deduction_instrument.py::TestDryRun::test_the_full_dry_run_survives_one_empty_completion`:
the double receives 601 sends, `repaired_clock` reports 301 calls,
`retried_calls` 1, `unaccounted_attempts` 1, `attempts_by_trigger`
`{"empty_completion": 1}` and one unit with a retry, `combined_accounts` reports
none, and every graded field, ballot verdict and token total on both arms is the
plain run's — an attempt that produced nothing produced nothing to grade or to
charge. The run's `model_ids` carries `no-completion-returned` beside the
fixture's own model, so a retried run cannot read as a clean one. What the
bound does once the retries are exhausted is established by its planted cases,
not by this run.

The figures this section carried before the re-bindings of 2026-09-10,
2026-09-13 and 2026-09-14 were measured on the 3000-3999, 5000-5999 and
6000-6999 bands. They are superseded with those bands and are not re-run: all
three are development data, and a dry run over any of them would measure a set
this manifest no longer authorizes.

The relevance amendment costs this fixture no unit on this band either, and the
figures say so more directly than on any band before it: the dry-run provider
produced no off-target citation at all on either arm across its 98 naming
ballots, and supported-correct is the same 13 as role-correct, so the rule
removed no role-correct ejection here. That the rule bites at all is established
by its planted cases, not by this run — the fixture cites the transcript's last
turn whatever it says, so what it exercises is the path, not the judgment.

**A green dry run says nothing about model judgment.** The dry-run provider reads
the prompt for a valid target and a real turn id and returns them; it establishes
that the pipeline carries a non-SKIP decision through to a graded outcome, not
that any model would produce one. Its choice does not depend on the arm, so the
dry run's paired result is `b=0, c=0, p=1.0` BY CONSTRUCTION and must not be read
as a comparison between the arms.
