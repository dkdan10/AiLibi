# Resolve carried audit claims and keep their dispositions checkable

**Status:** ready

## Outcome

Every carried close/hardening finding has a current, evidence-backed disposition.
Current summary claims, historical finding-to-contract attribution, and the
remaining source-prose corrections are checked at the surface they describe.

## Evidence

The phase-21 close F1/F3/F5 and section 4 identify unchecked summary claims,
incomplete routing, recurring stale prompt-archive prose, and fragile prose
heuristics. The hardening audit sections 4–5 distinguish unresolved, informational,
and refuted cases; those distinctions must survive cleanup.

## Acceptance

- [ ] Enumerate the close's carried items and hardening routes with a current
  reproduction, explicit disposition, and owning cleanup card where needed.
- [ ] Guard the close's verdict, bar readings, ladder claim, and real links
  against their historical source; quoted examples and historical comparisons
  remain valid. Adverse mutations demonstrate each new gate.
- [ ] Verify finding-to-contract attribution and complete coverage without
  silently crediting a partly fixed or unadopted finding as repaired.
- [ ] Fix the three carried claim-checker heuristics with semantic positive and
  adverse controls; correct stale current source prose without rewriting records.
- [ ] Add the unoverridden FINDING to the ownership lessons within its word
  budget, preserving the historical verdict and final owner decision boundary.
- [ ] All named repair cards are complete or the item has a supported explicit
  retained/retired/experimental disposition; targeted and full checks pass.

## Constraints

Follow docs/architecture.md and preserve historical records/contracts. Do not
reinterpret intentional rules as defects, adopt experiments, run live providers,
delete remote evidence, or claim all findings are fixed from a routing table.
Observation, frontend, and training fixes belong to their separately owned
cards. This card completes the accounting for roadmap38 alongside those repairs.

## Expected scope

scripts/check_doc_facts.py and focused script tests; a current disposition ledger
under docs/; docs/lessons.md; directly necessary source-docstring corrections
after ownership handover; task routing and this card. Corpus and observation
production code are not owned by this card.

## Record impact

None. Read and preserve historical evidence; check current claims without
changing simulation prompt bytes, detector output, or adoption decisions.

## Validation

Reproduce current findings with offline commands, run perturbed checker cases,
inspect the complete routing census and its linked card evidence, then run
bash scripts/check.sh. Historical attributions require full git history.
