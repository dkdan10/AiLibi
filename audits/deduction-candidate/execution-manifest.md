# Fresh-model deduction evaluation — execution manifest

**Dated 2026-09-09. Status: bound. This document authorizes no live call.**

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
values differ from its parent's to be named in this section. A pre-run change to
the frozen analysis that nobody logged here fails that test.

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
| Held-out inputs | The 50 proof-free scripted physical prefixes frozen by the owner's merge of #438 as `23a23c2d` on 2026-09-08, recorded as hashes only in [held-out/manifest.json](held-out/manifest.json) |
| Seed band | 3000–3999 drawn ascending, first 50 passing prefixes; accepted seeds run 3000–3057 with 8 skips, all `witnessed_kill` |
| Seed list | Published in the freeze manifest's `accepted[]`. The prefixes themselves are NOT committed anywhere: the runner regenerates them with `experiments.held_out_prefixes.generate()` and refuses to proceed if any digest or skip differs |
| Development inputs | The seven hand-authored cases in `experiments/deduction_scenarios.py`, seed 1 by construction. Their digests are recorded in the freeze manifest and asserted absent from `accepted[]` |
| Legal schedules | Each prefix is replayed through the engine, which accepts or rejects every step; a prefix whose hashed steps the engine did not resolve step for step never gets a digest |
| Provider-response repetitions | One. Each unit is one prefix and one meeting; no response is sampled twice and no unit is repeated |
| Run order | Sequential, seed ascending, both arms per seed before the next seed |
| Maximum opportunities | 50 prefixes × 2 arms = 100 meeting units, ~600 model calls. An attempt that never resolves — a transport failure, a truncation, an exhausted limit — is a stop, and the partial state is reported rather than replaced. An attempt whose payload failed schema validation is NOT a stop: the meeting layer substitutes a placeholder turn or a marked SKIP ballot for it at an accepted ~1-in-50 rate, and the instrument counts every such substitution per unit and per arm (see "Meeting-internal defaults" below) so it stays visible instead of being silently replaced |

## Sampling configuration, caps and limits — the owner's authorized values

Copied verbatim from [the authorization card](../../tasks/work/fresh-deduction-authorization.md)'s
Constraints table, whose reasoning of record is item B of
[the 2026-09-07 decision memo](../../tasks/owner-decisions-2026-09-07.md) — with
one row that is NOT from that table and is marked as such. The authorization
card binds no temperature; the preregistration
(`preregistration.md:113-115`) requires this manifest to bind the sampling
configuration, so the sampling-temperature row states the values shipped in
`meetings/manager.py` and the instrument serves them explicitly rather than
inheriting them. It moves no owner-authorized number.

| Field | Value |
| --- | --- |
| Provider | `featherless` |
| Model | `Qwen/Qwen3.6-27B` (locked 2026-07-12, Task 16.2). Non-thinking with `enable_thinking=false` pinned on every call, `response_format_mode = json_object`, prompt set `qwen3_6_27b` — all carried from the model lock, not re-decided here |
| Per-call token cap | turn 2,048 output / vote 1,024, the shipped defaults unchanged. The committed lab rows for this model-and-prompt-set pair ran at `max_tokens=4096` and never exceeded 195 output tokens, so a truncation is a real signal rather than a cap artifact |
| Sampling temperature *(not from the authorization card — see the note above)* | turn temperature 0.4 / vote temperature 0.2 — the shipped values (`meetings/manager.py:211,213`), bound here rather than inherited. The instrument passes an explicit `MeetingConfig` carrying them, records both on every report, and a test asserts they are still the shipped values, so a later edit to those module defaults breaks a test instead of silently moving this frozen design's sampling distribution |
| Total token budget | 2,400,000 input / 200,000 output run-level, and 45,000 input / 4,000 output per unit. Hard stop. Projection for option A: 600 calls; input `repaired_clock` 3,636/call x 300 + `combined_accounts` 2,441/call x 300 = 1,823,100; output 600 x 220 = 132,000 |
| Wall-clock deadline | 4 h of model work within a 6 h elapsed deadline. The work window comes from the measured 12-23 s/call band; the 2 h margin covers one recorded 3h21m provider-side HTTP 529 stall (`audits/audit-phase-21-adopting-record.md:373-380`) |
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
  afterwards. The run also checks the client's real TYPE against the provider it
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
  one of the two shipped values, and refuses a response whose output reached its
  cap — a truncation is a stop, not a datum.
- **Sampling.** The two temperatures and the two caps are served through an
  explicit `MeetingConfig` built from `AUTHORIZED_SAMPLING`, and a live run whose
  sampling configuration is not that one is refused before any client is built.
- **Token budget.** One `llm.budget.GameBudget` per unit with a run-level parent,
  so every charge reaches both ceilings. After each unit the RECORDED per-call
  spend on the replay row is reconciled against the enforced budget snapshot, and
  a difference is a stop.
- **Wall.** Two clocks, because the authorization names two limits: one
  `orchestrator.run_limits.RunDeadline` for the 6 h elapsed window, checked
  between units and inside the meeting, and a summed provider-call clock for the
  4 h of model work. The work clock bounds each provider await by what is LEFT
  of its window, the way `RunDeadline.run` bounds meeting work by what is left
  of the elapsed one, so the run stops DURING the call that exhausts the window.
  A clock charged only when a call returns would be a one-call-granular limit,
  and one call on this provider is not small: `llm/featherless_client.py` retries
  a send six times at a 600 s timeout with exponential backoff, so a run at
  3 h 59 m of model work could otherwise spend a fifth hour against an
  authorization of four. The cut-off attempt's elapsed wall is charged to the
  clock and its call recorded in the partial accounting with unknown (zero)
  usage before the stop is raised.
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
exhausted at either the per-unit or the run level; the elapsed wall deadline or
the model-work window, the latter cutting off the attempt in flight rather than
one call later; a per-call response that reached its output cap (a truncation
is a stop, not a datum); a held-out digest or skip that differs from the frozen
manifest; a rendered prompt or regenerated prefix matching the legacy body
handle; a unit whose recorded observation clock or experiment config is not the
arm's; or a recorded meeting default whose phase and trigger this instrument
cannot classify. A meeting-internal default is NOT itself a stop. The meeting
layer's shipped fail-soft substitutes a placeholder turn or a marked SKIP
ballot for a payload that failed schema validation, at an accepted rate of
about 1 in 50 calls, and a fixed 50-unit paired sample cannot be abandoned for
a substitution the engine is designed to make. Every such substitution is
instead counted per arm and per unit — turns and votes separately, by trigger,
with the units carrying any — and reported beside decision coverage, so it is
visible rather than silently replaced. No stop condition reads an outcome: the
50 paired units are a fixed sample with no interim analysis and no optional
stopping, so nothing here can be tripped by a result the run has produced.

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
| Preparer | A session dispatched on [the freeze card](../../tasks/work/held-out-prefix-freeze.md). It built the deterministic generator, drew from the preregistered band, committed the hashes and opened the pull request the owner merged as `23a23c2d`. It ran no arm |
| Runner | A separate session dispatched on [the instrument card](../../tasks/work/fresh-deduction-instrument.md), started after that merge. It regenerates the set from the frozen band, verifies the committed hashes, and opens no prefix: no prefix is printed, logged or written into any report, and `assert_report_holds_no_prefix_bytes` refuses a report that carries one |
| Coordinator | Dispatches both and runs neither |

Inspecting a held-out input converts it to development data. A held-out result
that informs a fix marks this set development — recorded by setting the freeze
manifest's `status` to `development` — and a new band is frozen under a new
card. The prefixes are archived with the results after the run, when they are no
longer held out.

## Verification of this manifest

The offline mechanics check, at commit `5682ea2a` plus this branch's changes:

```sh
.venv/bin/python -m experiments.fresh_deduction_instrument --dry-run
```

100 units (50 prefixes × 2 arms), 600 calls, `total_cost_usd` 0.0, in a few
seconds of wall. Both arms carried a non-SKIP decision to a graded outcome: 50 ejections
each, 19 role-correct, 31 wrongful, 18 supported-correct, 150 supported ballots and 6
guard-rewritten ones per arm, with 100 ballots naming the ejected player of which
6 cited evidence that does not bear on that player. The report carries the sampling configuration it
drew at (`turn_temperature` 0.4, `vote_temperature` 0.2, caps 2,048 / 1,024). Input tokens by the fake provider's `len // 4`
heuristic were 886,054 (`repaired_clock`) and 575,251 (`combined_accounts`);
applying the decision memo's calibrated 1.28x real-input ratio to their sum gives
about 1.87 M against the 2.4 M ceiling, and the larger arm's 17,721 per unit
gives about 22,700 against the 45,000 per-unit ceiling — headroom checks, not
predictions, because a real model writes a different transcript.

The relevance amendment cost this fixture no unit: 18 supported-correct before it
and 18 after, because its 6 off-target citations all fall in units the primary
outcome already scored 0. That the rule bites at all is established by its
planted cases, not by this run — the fixture cites the transcript's last turn
whatever it says, so what it exercises is the path, not the judgment.

**A green dry run says nothing about model judgment.** The dry-run provider reads
the prompt for a valid target and a real turn id and returns them; it establishes
that the pipeline carries a non-SKIP decision through to a graded outcome, not
that any model would produce one. Its choice does not depend on the arm, so the
dry run's paired result is `b=0, c=0, p=1.0` BY CONSTRUCTION and must not be read
as a comparison between the arms.
