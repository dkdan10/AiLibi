# Compare purposeful tactics and structural gameplay rules

**Status:** ready

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

- [ ] Characterize current task load, finished-crew idle time, short movement
  cycles, vent-exit exposure, meeting follow-through, sabotage and task victory
  contributions with source-bound offline metrics before changing policies.
- [ ] Compare deterministic workload-aware redistribution, bounded finished-crew
  patrol/accompaniment/investigation, locally informed vent-exit risk,
  anti-oscillation memory and a small justified post-meeting tactical response
  separately. Include legitimate reversals/escape and uncertainty controls.
- [ ] Use disjoint development and held-out seeds/scenarios, fixed budgets and
  paired measurements. Check deterministic repeatability, no role/position
  oracle, no new stagnant equilibrium and unintended task/escape regressions.
- [ ] Measure seat/action-order effects using identity permutations with roles,
  intentions and map state remapped consistently. Do not equate fake meeting
  outcomes with model-quality evidence or adopt randomized action priorities.
- [ ] Implement an explicit opt-in meeting-reset comparison covering positions,
  vent occupancy, cooldowns, grace and all remaining corpses together. Retain
  baseline semantics unless the separately measured decision supports adoption.
- [ ] Investigate self-report and structural role tells using current and
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
