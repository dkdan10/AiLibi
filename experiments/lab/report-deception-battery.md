# Lab report — Deception probe battery (Tier 2, the 10.10 gate pulled forward)

**Decision informed:** Wave-2 shape — the deception-probe go/no-go (renumbered 10.10) and
the toolkit contract (10.11). **Rubric:** R2 (deception works sometimes), R3 (arcs), R6.
**Date:** 2026-06-13. **Model:** qwen3.5:9b, production prompts (impostor_report_v4 /
accusation_round.v7), temp 0.4, contexts reconstructed from the Wave-1 attempt-1 evidence
bytes via ReplayLoader (real memories, real transcripts). 62 calls, 100% schema-valid.
Grading fully mechanical (canonical rooms, repaired detector, claim parses).

## Probes and results

**A — spontaneous self-report fabrication (n=18).** The killer opens the meeting for
their own kill. **Lie attempted: 2/18 (11%).** Honest self-placement at the kill scene:
8/18. Evasive no-position (alibi window missing the kill tick): 8/18. Self-incriminating
text: 0. Accuses someone else: 14/18. Both liars drew weak-only flags against a true
witness (the self-stated shelter, exactly as designed); zero self-conflicts.

**C — the same ask, handed a cover story (n=12).** One injected line ("you were doing
the wiring task in ROOM from tick T1–T2"). **Deployed: 11/12 (92%). All 11 lies survived
a true witness sighting at weak-only (sub-gate, sheltered).** Ignored: 1. Garbled: 0.

**A2 — consistency under pressure (n=10).** A synthetic accuser confronts the opening
with the true sighting. Story holds (room+window): 7/10. Confessions: 0. Counter-accuse
when cornered: 5/10. **Pressed chains minting detectable self-flags: 4/10** — drift the
detector can catch.

**B — deflect-without-boomerang, recorded accusation contexts (n=22).** Deflects: 19/22
(86%). Self-accusation: 0. Confession: 0. Replies minting flags against self: 0. Quality
gaps: counter-target NOT a living player 6/22 (27% — the id-hallucination class under
pressure, prod guard absorbs but the deflection is wasted); counter aimed at OWN TEAMMATE
4/22 (the v4 firewall block suppresses the ballot, not the urge); textually CONFIRMS the
accuser's room claim 8/22 (soft boomerang).

## The finding

**The 9B cannot invent deception (11%) but executes scripted deception almost perfectly
(92%, 100% sheltered).** Survival instinct is already strong (zero confessions or
self-flags anywhere); fabrication is the missing faculty, and it is missing at the
GENERATION step, not the performance step.

## Decision input

1. **The Wave-2 go/no-go is GO, with the architecture decided:** the 10.11 toolkit must
   be POLICY-AUTHORED deception — at kill time the impostor policy mints a cover story
   (plausible task + room ≠ kill room + window covering the kill) and injects it into
   rendered memory; the model performs it. Do not ship a "be deceptive" instruction; the
   model demonstrably won't take the hint spontaneously.
2. **The probe task (10.10) shrinks** from "can it play the villain at all" (answered) to
   confirmatory + the targeting-quality baseline: deflection legality (73% legal today),
   teammate-deflection rate (18%), room-confirmation leak (36%) — the three numbers the
   toolkit A/B must move.
3. **R2's "sometimes fails" requirement has a natural mechanism:** 30% story drift under
   pressure mints real self-flags — scripted deception is catchable without any new
   detector work. The game gets liars worth catching AND the catching stays honest.
4. Raw rows + examples: `results-deception-battery.jsonl`.
