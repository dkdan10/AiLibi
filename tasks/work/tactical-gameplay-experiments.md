# Compare purposeful tactics and structural gameplay rules

**Status:** active

## Outcome

Roadmap 21–25 and 43–46 have separately implemented, measured candidates or
supported retained decisions. Changes remain opt-in until their evidence and
adoption decision justify the default. Tactics use only entitled information.

## Evidence

The current crew policy allocates seat-preferred tasks and can wait after its
work finishes. Movement reversals, vent exits, lexicographic action order,
meetings, persistent corpses, self-report exclusion and sabotage/task outcomes
have effects that must be measured independently. The existing phase-21 and
earlier roll-call studies are inputs, not authority for new conclusions.

## Acceptance

- [x] Characterize current task load, finished-crew idle time, short movement
  cycles, vent-exit exposure, meeting follow-through, sabotage and task victory
  contributions with source-bound offline metrics before changing policies.
- [x] Compare deterministic workload-aware redistribution, bounded finished-crew
  patrol/accompaniment/investigation, locally informed vent-exit risk,
  a scoped anti-oscillation guard or supported retained disposition, and a small
  justified post-meeting tactical response separately. Include legitimate
  reversals/escape and uncertainty controls.
- [x] Use disjoint development and held-out seeds/scenarios, fixed budgets and
  paired measurements. Check deterministic repeatability, no role/position
  oracle, no new stagnant equilibrium and unintended task/escape regressions.
- [x] Measure seat/action-order effects using identity permutations with roles,
  intentions and map state remapped consistently. Do not equate fake meeting
  outcomes with model-quality evidence or adopt randomized action priorities.
- [x] Implement an explicit opt-in meeting-reset comparison covering positions,
  vent occupancy, cooldowns, grace and all remaining corpses together. Retain
  baseline semantics unless the separately measured decision supports adoption.
- [x] Investigate self-report and structural role tells using current and
  historical roll-call evidence; distinguish prompt eligibility, enforcement
  leaks and inherent certified proof. Coordinate any meeting-layer repair with
  the reasoning card and avoid implicit role-rule changes.
- [ ] Explain low sabotage/task contribution by configuration and compare one
  mechanism at a time. Publish candidate results including losses, costs and
  limits; provide an implemented/retained/experimental disposition for each
  roadmap item. Targeted/full gates and canonical samples pass.

## Constraints

Read docs/architecture.md. Deterministic engine, no tactical LLM calls, no
agents-to-engine imports, no globals or hidden-state access. No live calls,
training, new maps, providers, deployment or experimental adoption. New behavior
uses an explicit opt-in configuration/version and preserves default behavior.
Do not fix already-correct reported-corpse cleanup or duplicate report rejection.

## Expected scope

Agent tactical policies/pathing and explicit policy state/configuration;
necessary orchestrator/engine reset experiment seams after ownership handover;
orchestrator/experiment_config.py and versioned recording/reader follow-through;
offline harness/metrics, focused tests and compact result artifacts/current
disposition docs. Root coordinates memory, registry and training overlap.

## Record impact

Experimental candidates only; current default and historical replay hashes
remain unchanged. Any candidate that affects rendered memory/detector output
must use the recorded default-OFF substrate contract. Label each experiment.

## Validation

First capture baseline mechanism counts, then paired one-change comparisons and
only justified interaction checks. Use meaningful planted entitlement and
stagnation failures. Document run limits and source/input fingerprints. Root
runs bash scripts/check.sh and scripts/verify_samples.sh.

## Results

The pre-change diagnostic strictly reconstructed all 100 committed recordings.
It separates submitted, applied, rejected and meeting-discarded actions; raw
movement reversals are geometric counts, not a judgment about intent. In 9p2i,
268 of 355 task redistributions select a busier recipient than another eligible
crewmate, 457 accepted finished-crew waits occur at the meeting hub, and 62 of 97
vent exits have a crew witness. These are recorded-model mechanisms, not fresh
fake-provider evidence. The durable harness retains exact denominators,
input/source fingerprints and negative results in
[the comparison record](../../audits/tactical-gameplay/README.md).

The shared experiment contract is closed, frozen and versioned. Tactical arms,
redistribution, meeting reset and the two reasoning profiles remain independently
selectable; OFF is omitted from recordings. The provenance owner integrates
game/replay/API bindings first, followed by explicit handover. Engine functions
receive narrow typed options, never the privileged orchestrator config.

Development seeds are 1000–1007 and held-out seeds are 2000–2015, separately for
4p1i and 9p2i. Each paired arm uses the same setup, deterministic fake client,
96-tick cap and per-game model-call/token budget. Mechanical controls and
development results select bounded candidates before held-out evaluation; no
result authorizes adoption or claims improved model reasoning.

The carried RNG reseeding optimization already exists. Five immutable mapping
copies remain per WorldState replacement, but protect against external mutable
mapping proxies. Any separate optimization needs measured benefit plus aliasing
controls; retaining the current implementation is valid.

The eight implemented candidate arms are workload allocation, finished-crew
patrol, brief accompaniment followed by patrol, observed vent-exit risk,
preserved-location meeting follow-through, coupled meeting reset, self-report,
and an earlier sabotage threshold. Each is independently selectable in the
closed recorded config. Default policy objects and absent config bytes remain
the baseline. All arms must preserve deterministic repeatability, legal task and
escape interrupts, and entitlement controls; the held-out screen reports every
arm and its losses rather than choosing an adoption from fake wins.

The scoped anti-oscillation guard is removed, including its accepted config
field. Sixteen paired development games had identical action/engine trajectory
hashes and counts. The unchanged-goal shortest-path control strictly decreases
remaining distance; changing a repair goal or leaving a newly discovered body
can justify an immediate reversal. Raw reversals remain measured, while a
blanket reversal ban is rejected. This is roadmap 24's supported retained
result, not an adopted new mover. The dated exploratory comparison is preserved
separately because the discarded implementation is no longer a callable arm.

Self-report directly changes tactical eligibility, without changing engine
report rules or the meeting protocol. Keep the historical impostor-roll-call
verdict and its unresolved sibling-template composition limits intact; neither
fake skip ballots nor reporter counts establish improved model inference.
The earlier sabotage arm changes only the public completion threshold, retaining
kill priority, repair behavior and the existing rearm rule. For three total
tasks, the baseline threshold cannot activate before completion; the candidate
can activate at two completed tasks.

The harness measures submitted/applied/rejected/discarded actions separately,
source-event witnesses, carried task progress and eligible workload, report ages
from actual kill events, and post-meeting spatial state. Identity interventions
relabel each entire pre-tick state and its submitted intentions, then rerun that
single transition. They quantify action/task-state effects without resampling
speech, changing RNG state or claiming whole-game counterfactual win rates.
Experimental inputs are refused by this baseline-only identity instrument.
Historical and fresh usage totals include failed attempts and aborted prefixes;
the fresh totals must reconcile with the enforced game budget. Source hashes
include Python, templates, map/config inputs and dependency locks. Runtime/input
changes during a screen refuse publication.

The carried mapping-copy measurement retains the safe implementation: five new
mapping wrappers preserve values and RNG bytes, while external mutation of an
input mapping proxy cannot mutate a WorldState. The harness reports warmed
single-process replacement/copy operation times without a CI latency threshold
or claiming the separate copy loop isolates a causal fraction of runtime.
The final development and held-out captures share source fingerprint
`d93f9d096e4b23572915e0ab128ee4ad266420bbbc266231eb7d49322d09bbd8`.
All 144 development and 288 held-out games completed without an error or limit.
The development record also contains 100 strict canonical folds and 3,550
coherent identity interventions. The coordinator's combined full gate remains
pending; no default was adopted and no live provider was called.

Independent review found and repaired a roster-capture ordering race: the
fingerprint now precedes setup reads, the exact captured roster bytes are parsed
and stamped, and both whole-source and exact-roster comparisons run before any
game and after the screen. The planted transient A→B→A replacement fails before
candidate work even when the surrounding aggregate fingerprints match. The
reviewer reran all 15 harness tests and found no remaining scoped blocker in the
policies, reset, allocation or identity intervention. The broader affected
selection passed 258 tests with 3 existing xfails; strict mypy passed 13 selected
files. Combined project verification remains the coordinator's pending gate.

Necessary shared follow-through includes the provenance owner's frozen runner
settings and explicit HeadlessGame substrate override. A direct runner resolves
optional booleans once, rejects contradictory stamps, and a custom campaign
runner can receive a complete validated baseline snapshot. The provenance card
owns the campaign semantics and their independent regression checks. The env
example gives reasoning experiments a separate section from the five existing
substrate toggles; they do not register extra substrate keys.

Final commands, each refusing an existing output path:

```sh
uv run python -m experiments.tactical_gameplay --split development --include-samples --output audits/tactical-gameplay/development.json
uv run python -m experiments.tactical_gameplay --split held_out --output audits/tactical-gameplay/held-out.json
```

The development and held-out fake clients recorded 3,192 and 6,886 calls,
8,484,617 and 18,319,405 synthetic input tokens, 164,388 and 354,629 output tokens,
and $0; all totals reconcile with their enforced budgets. Held-out least-work
allocation eliminates above-minimum eligible recipients and reduces finished
waits from 71 to 45 in 4p and 233 to 68 in 9p. Patrol and brief accompaniment
remove measured finished waits. These are not uniformly better trajectories:
the 9p least-work arm raises crew-witnessed exits from 32/53 to 47/55, the vent-risk
arm has 33/61 witnessed exits and more waiting, and meeting reset raises waits
to 110/341. Earlier sabotage produces 13/9 reactor starts but no sabotage wins;
the fake task wins fall from 7/1 to 3/0. The README publishes every arm's losses
and its experimental or retained disposition, rather than promoting a winner.

The retained-controls record binds all 16 abandoned-guard baseline trajectories
to the final baseline. Its older Python/map/harness-only source identity is
explicitly dated and narrower; the removed guard is not claimed to remain
rerunnable. Current executable controls cover fixed-goal progress, legitimate
reversal, aliasing, unexpected configuration, reported/stale observation risk,
task/escape interrupts, complete reset state and repeated genuine replay/API
reconstruction. The carried RNG reconstruction issue already has its fast path;
safe mapping copies remain, measured at 3.586 microseconds per replacement and
1.542 microseconds per separate five-copy operation on this machine, with no
causal attribution or timing threshold.

Scope follows docs/architecture.md's layering, explicit experiments and recorded
determinism contracts. The identity screen is a transition-level intervention,
not a whole-game action-order counterfactual. No fake skip ballot establishes
reasoning quality, and no structural-proof or historical roll-call conclusion
is reversed. Independent review approved the bounded implementation after the
roster-binding repair. Runtime is frozen; the coordinating agent owns combined
verification, commit delivery and artifact inventory follow-through.

Final focused verification passed 49 tests in 2.09 seconds:

```sh
uv run pytest tests/agents/test_tactical_experiments.py tests/engine/test_redistribution_experiments.py tests/engine/test_meeting_reset_experiment.py tests/orchestrator/test_experiment_config.py tests/experiments/test_tactical_gameplay.py -q --tb=short
```

Ruff and format checks passed, and strict mypy reported no issues in the 13
owned production/test files. The final source fingerprint still matches both
captures after verification. The contemporaneous historical counterfactual
script compatibility repair lies outside this fingerprint and is not called
by the tactical harness; it does not alter these measured inputs.

The isolated runtime/measurement commit snapshot passed strict mypy across 436
files and 235 selected mechanism/profile/reader tests, including the tactical
controls and harness. Final combined verification remains pending.
