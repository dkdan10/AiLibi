# Prospective deduction evaluation

**Draft dated 2026-09-06. Status: planning, no live execution authorized.**

This document specifies the evaluation structure before future held-out work.
It does not declare the candidate, source inventory, held-out inputs or spending
limits frozen. Those execution fields must be bound after the remaining runtime
work and independently reviewed before any live call. The current development
matrix is already known to the implementers; it cannot confirm generalization.

## Question and competing explanations

Can agents use their entitled observations and attributed public accounts to
make better supported decisions when neither a kill nor a vent was directly
witnessed? Does an answer to a new allegation correct an unsupported accusation,
and does a deterministic investigation obtain information worth its tactical
cost? A desirable result includes justified uncertainty when evidence is missing.

Separate these explanations for apparent improvement:

- Better inference from legal sightings, conditional route constraints, public
  death bounds and testimony.
- More opportunities to hear or act, independent of reasoning quality.
- More direct proof, private truth certificates or hidden-state leakage.
- Mechanical vote rewriting, forced accusation, task completion or tactical
  changes that happen to improve the final win rate.
- A selected small scenario, lucky model response or inspected test input.

The comparisons and reports below must distinguish them. No observed vent is a
narrower condition than no direct proof: witnessed kills also belong in a direct
evidence stratum. A meeting containing a witness does not give every listener
first-hand knowledge. Labels must be attached to the agent's information at the
decision, as well as reported at meeting and game level.

## Existing development matrix

The authoritative definitions are `scenario_cases()` and `comparison_arms()` in
`experiments/deduction_evaluation.py`, with legal actions and scripted speech in
`experiments/deduction_scenarios.py`. They currently define seven cases:

| Case | Mechanism or control |
| --- | --- |
| `honest` | An unwitnessed kill followed by body discovery and a legal account; walking feasibility can contest an impossibility claim without proving innocence. |
| `impossible_account` | The engine takes legal actions while a speaker gives an account incompatible with cited placements under the stated timing assumptions. |
| `insufficient_evidence` | Missing placements prevent a confident travel verdict; uncertainty is an intended result. |
| `already_known_dead` | A public death announcement precedes later proximity; later presence cannot create an opportunity for that earlier death. |
| `witnessed_kill` | Direct kill-evidence control. |
| `witnessed_vent` | Direct vent-evidence control. |
| `late_accusation` | A consequential new allegation tests the independently bounded reply opportunity. |

Every case is crossed with these six arms, giving 42 development captures:

| Arm | Temporal / evidence context | Public accounts | Attributed testimony | Additional reply |
| --- | --- | --- | --- | --- |
| `legacy_reference` | OFF / OFF | OFF | OFF | OFF |
| `repaired_clock` | v2 / v2 | OFF | OFF | OFF |
| `common_accounts` | v2 / v2 | v1 | OFF | OFF |
| `attributed_testimony` | v2 / v2 | OFF | v1 | OFF |
| `combined_accounts` | v2 / v2 | v1 | v1 | OFF |
| `combined_with_reply` | v2 / v2 | v1 | v1 | v1 |

The repaired-clock arm is the component reference. Compare common accounts and
attributed testimony independently to it; compare the combination to each
component; compare the extra reply to the combination without that reply.
Legacy versus repaired clock measures a package of repaired timing/context
semantics. It does not isolate each internal repair. Existing OFF/v1 compatibility
tests remain necessary even though v1 is not a seventh matrix arm.

These captures use canonical seed 1, the four-player/one-impostor roster,
predetermined actions and the deterministic scenario provider. Custom factories
must retain that identity. Scripted speech and abstention are mechanism fixtures,
not decisions learned from a model. Identical trajectories are an expected
possible result. The final capture must preserve the actual source inventory,
input hashes, arm settings, provider identity, complete recordings and strict
reader output; an execution timestamp alone is insufficient provenance.

The matrix does not measure spontaneous movement or missing-player searches.
Investigation profiles require separate normal-policy comparisons; adding their
names to a fixed-action fixture would not make the fixture test those policies.

## Staged evaluation and freeze gates

### 1. Complete offline mechanics and independent review

Finish the current integrity, temporal, public-account and investigation work.
Run the full project gate and required historical replay checks. Reproduce all
relevant adverse controls: unentitled/private channels, timing corruption,
duplicate or omitted evidence, forged ballot rosters/targets, wrong report
identity, reset discontinuities and source/input drift. Any such defect blocks
capture or comparison; it is not averaged into an acceptable quality score.

The coordinator then captures the final development matrix into a new protected
output directory and binds it to the actual source inventory. Freeze gameplay-
first and code-first findings separately before their synthesis. Preserve the
record even if it is unhelpful or reveals no changed decisions.

### 2. Select a candidate and prepare a separate execution manifest

Use development evidence to choose a bounded candidate and named component
comparisons. Keep unadopted components independent until their interaction is
tested. The normal-policy investigation comparison must name the exact search,
expiry, urgent-action override, accompaniment and self-report configurations
actually selected; the current six arms do not silently cover those settings.

Before any fresh provider run, the execution manifest must bind:

- Candidate and reference source inventories, prompt/template versions,
  dependency/runtime identities, recorded configuration, factory and policy
  identities, map and roster, and the evaluation instrument itself.
- Development versus held-out game inputs, legal scenario schedules, seed
  lists, provider-response repetitions, run order, and the maximum opportunities
  and games that will be attempted. Missing or truncated attempts remain visible.
- Exact provider/model, sampling configuration, requested token caps, elapsed
  time limit, cost limit and the owner's explicit authorization for those limits.
  Flat-rate access still needs bounded token/time use and a cost statement.
- Primary comparisons, outcome/entitlement rubrics, decision rules, uncertainty
  method, acceptable tradeoffs and any numeric margins justified before outcomes
  are inspected. This draft supplies no invented success threshold or budget.

The owner can approve this concrete manifest after it exists. No live call,
including a pilot or retry on flat-rate service, is authorized by this draft.
Keep existing baseline-only training campaigns unchanged; any new experiment
uses a separate source-bound evaluation surface.

### 3. Measure fresh meeting decisions under controlled evidence

Each controlled unit consists of one actual seeded, frozen legal prefix followed
by one fresh meeting through the real pipeline. Apply that meeting's outcome and
stop: a terminal outcome remains terminal; otherwise record an explicit stop and
label the unit deliberately partial. Fresh ejections can change the living roster,
tasks and subsequent legal actions, so do not continue claiming a fixed trajectory
after that decision. Later meeting opportunities require their own independently
frozen prefixes, including any scripted earlier discussion. Complete downstream
divergence belongs to the normal-policy stage below.

Retain full prompts, responses, normalization, guard changes and failed attempts
so account and reply effects are attributable. Independently vary reliable
observation, attributed testimony, missing evidence and contradicted testimony
without injecting hidden facts into agent memory. Define the eligible meeting
boundary before inspecting fresh decisions; terminal/partial controlled units
are not game-win trials and do not enter normal-policy win-rate denominators.

Use the known seven cases only for development/operational checks. A separate
reviewer should prepare and freeze new held-out legal schedules and information
patterns before the candidate is evaluated on them. They must exercise the same
map and rules without requiring impossible engine actions. Merely relabeling
players or rerunning the same inspected schedule is not independent confirmation.
If held-out content or results inform a fix, mark those inputs development and
freeze new confirmation inputs before making a generalization claim.

### 4. Measure complete games with normal policies

Run paired candidate/reference game inputs with actual deterministic tactical
policies and newly generated meeting decisions. Freeze those seed lists separately
from the scripted suite and any pilot. A seed controls initial conditions, not
identical future provider output or identical trajectories after decisions diverge.
Pair analysis by initial input and report divergence explicitly.

Compare missing-player search against its reference independently before adding
accompaniment, and compare context-dependent self-report independently before
the combined candidate. Count whether the selected intent changed an executed
action, the path or the available evidence. Measure gained sightings/body
discoveries, search expiry and interruption, urgent repair/report/escape behavior,
task delay, travel/repetition and deaths as well as wins. A later sighting can
guide a new action; it cannot certify an earlier claimed alibi.

Component evaluation precedes the combined candidate and held-out confirmation.
Do not repeatedly select the best subset on the held-out results. Source edits
after a freeze create a new candidate version; retain the earlier result.

## Evidence privileges and grading

Agents receive only the rendered typed memory, their own reliable observations,
public topology and the accounts their protocol permits. Common task activity
has the same public vocabulary for both roles; the listener does not receive
another actor's private completion/rejection receipt. Attributed testimony must
not expose a speaker's private certification through flags, confidence changes,
reply selection, rendered labels or citation resolution.

Grade evidence support first from exactly the deciding agent's entitled inputs,
without revealing hidden roles or complete trajectories to that grader. Freeze
the support rubric, grader process and disagreement handling before confirmation.
Then use a separate privileged pass to grade truth and role accuracy from hidden
roles and complete legal trajectories. Keep the two judgments separate rather
than revising a support label after learning whether the guess was correct.
Judge truth never selects a tactical action, fabricates an observation, chooses
an agent's reply or supplies an accusation target. A true guess without support
is different from a supported inference. A false account that was unknowable to
the listener is different from a missed contradiction present in its memory.

Grade accusations and decisions for cited support, attribution, timing,
conditional language and acknowledgement of missing evidence. Distinguish
independent observations from repetitions and hearsay. A feasible route does
not establish innocence, and an impossible claimed route is conditional on its
placements. Missing-evidence controls must permit abstention; a mandatory vote
or accusation is not a measure of inference.

## Measures and denominators

Retain per-game, per-meeting and per-agent records before aggregation. Report
counts alongside rates, with the unit and denominator for every measure.

| Measure | Required interpretation |
| --- | --- |
| Decision coverage | All scheduled opportunities, those reached, valid responses, failures/defaults, completed and interrupted games; no silent exclusion of hard cases. |
| Correct and wrongful ejections | Both per resolved meeting and conditional on an ejection. Also separate role-correct guesses from evidence-supported choices. |
| Abstention | Voluntary skips, guard rewrites and failure defaults separately; distinguish appropriately insufficient evidence from missed usable evidence. |
| Accusation quality | Supported and unsupported allegations per opportunity and per allegation, with direct observation, attributed speech and missing-evidence strata. |
| Correction | Eligible new allegations, answers offered/received, and observable revisions in the subsequent account or ballot. Extra words or a reply turn alone are not correction. |
| Evidence use | Evidence present, retained, rendered, cited and semantically relevant at that decision; source identity and independent-origin counts remain visible. |
| Information gained | Newly entitled useful observations and discoveries after an investigation, relative to its cost and initial information; future evidence never rewrites past knowledge. |
| Effective behavioral change | Different selected intents, executed actions, paths, meetings and outcomes; rejected/discarded actions and unchanged trajectories separately. |
| Tactical cost | Task delay, travel loops, searches expiring/interrupted, urgent-action handling, deaths and role exposure; report relevant opportunities. |
| Provider cost | Calls, returned and unresolved token/cost accounting, latency, cancellation/retry/defaults and budget exhaustion. Unknown usage remains unknown. |

Stratify decisions by first-hand direct proof, direct evidence reported by
another speaker, indirect observed evidence, attributed accounts and insufficient
evidence. Overlaps require an explicit precedence or multi-label definition in
the execution manifest; do not combine strata post hoc to improve a headline.

Treat games as the main independent sampling units. Meetings and multiple agents
in one game are correlated. Report paired differences by seed/input and their
uncertainty rather than treating every ballot or repeated response as a new
independent game. The execution manifest fixes the estimator, resampling or
interval method, response repetition and comparison families before evaluation.
Small or inconclusive results remain inconclusive.

## Decision rules and stopping

Any provenance failure, unentitled evidence, inconsistent cutoff/ballot outcome,
live/reader disagreement or source change stops the affected comparison until
it is corrected and recaptured as a new version. Reaching an authorized time,
token or cost limit stops new calls, retains partial evidence and unresolved
accounting, and does not trigger unbudgeted retries or silent expansion.

The candidate should advance only if it shows supported indirect-evidence use
and appropriate uncertainty while satisfying the predeclared wrongful-decision,
direct-evidence, tactical and cost tradeoffs. It must not obtain its improvement
from exposed private truth, forced accusation, a larger direct-proof population
or guard rewriting. Numeric acceptance margins and sample sizes are intentionally
unset here: they require a justified execution design and must be frozen before
held-out results are read.

Possible decisions are advance for an explicitly scoped adopting review, revise
and evaluate a new version, reject, or gather more evidence under a new authorized
manifest. Inconclusive results do not become success, and more evidence is not
an automatic spending authorization. Preserve original negative outcomes and
every earlier experimental verdict. Implementation, verification, owner review,
merge and adoption remain separate states.

## Deliverables and current prerequisites

The next concrete deliverables are the final offline matrix and manifests,
independent gameplay and code findings with synthesis, an exact selected
candidate/reference set, a separately frozen held-out inventory and a reviewable
execution manifest with authorized provider limits. Publish future results with
their denominators, uncertainty, failures, costs and adverse cases, together with
the source and prompt identities needed to inspect them.

At this draft date, the source-bound final capture and remaining investigation
work are not represented as completed here. No held-out inputs, numerical success
margins or live limits are fabricated to fill those gaps. This is the complete
planning boundary; future execution remains a separately authorized step.
