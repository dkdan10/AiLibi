# Tier-0 Rubric — what "the game working as desired" means, measurably

Anchored to the owner principles on record: deception IS the game (innocents are
ejectable, never at RANDOM); no single signal or single round ejects; corroborate within
a round, accumulate across rounds, decay when cleared; the win split is demoted — outcomes
should be decided by deduction and deception, not the task stopwatch. Each item below has
a computable metric (or a probe target), the last-known value, and the desired direction.
"Last known" = the Wave-1 attempt-1 evidence bytes (PR #147 @ 5fdba2c) unless noted —
provisional but the richest record of the current design.

Items R1–R4 are the game's correctness-of-spirit floor; R5–R7 are what "interesting"
adds on top. Every lab report cites the items it bears on.

## R1 — Deduction decides outcomes

Ejections (and the threat of them) causally drive wins; the task stopwatch is one path,
not the only path.
- Metrics: ejection-driven win share (CREWMATE_EJECT wins + parity wins materially shaped
  by a crew ejection); stopwatch-margin distribution (share of task wins within one mean
  kill-interval of a parity flip); zero-meeting game share.
- Last known: 0 ejection-driven wins ever; 33/47 task wins inside one kill-interval;
  4/50 zero-meeting games (was 7/50 on W0).
- Desired: ejection-driven wins > 0 and growing wave-over-wave; the photo-finish band
  narrows as a SHARE of outcomes without the stopwatch being re-tuned to fake it.

## R2 — Deception is attempted and sometimes works

Impostors take detectable risks that sometimes pay off — survival through ACTION, not
through crew incapacity.
- Metrics: active-deflection events and the active share of accused-impostor survival;
  fabricated-alibi supply (genuine-class flags on impostors); impostor-push-decisive wrong
  ejections; fake-task/report emissions once the toolkit exists.
- Last known: survival 53/57 (93%) but only 28 active vs 25 passive; genuine supply 8
  flags; push-decisive 2/7; fake-task emissions 0 (structurally unreachable).
- Desired: the ACTIVE subcount carries survival; deception sometimes beats a working
  conviction engine — and sometimes fails (a 100% deception success rate is as dead as 0%).

## R3 — Suspicion has arcs

Belief trajectories rise, corroborate, clear, and sometimes come back — across meetings,
not within one.
- Metrics: carry-transition census (grew / held / decayed / collapsed); multi-meeting
  convictions as a share of ejections; Rule-3 clears that later prove wrong (a clear that
  bites back is drama, not a bug); re-cross events (dip below the gate then return).
- Last known: 129 grew / 129 held / 229 decayed / 0 collapsed; the seed-10 m2→m3
  fold-then-carry conviction is the first multi-meeting arc on record.
- Desired: multi-meeting convictions a growing share; nonzero wrong-clears; arcs visible
  enough to narrate (feeds R7 and the Phase-11 brief).

## R4 — No railroads (HARD floor, not a dial)

Nobody is ejected at random or off-graph. This is the owner line every wave re-asserts.
- Metrics: graph-consistent share of wrong ejections (every deciding voter carries an
  over-gate rendered row for the target); unattributed ejections (gp-7 channel
  decomposition = []); bare-pile-on conversions; innocents rendered at 1.0; genuine
  threshold inversions.
- Last known: 7/7 wrong ejections graph-consistent; 1 unattributed (seed-12 class —
  repaired by 10.9.2, structurally 0 after); pile-on 0; at-1.0 0; inversions 0.
- Desired: all zeros, forever, under every experiment variant. Any experiment whose
  upside requires relaxing R4 reports itself as REJECTED-BY-PRINCIPLE.

## R5 — Varied win paths

Outcome diversity: multiple distinct ways games end, none above ~80% share.
- Metrics: win-reason distribution; per-game ejection-count distribution; kill-count
  variance; meeting-count histogram spread.
- Last known: 46/3/1 task-stopwatch monoculture (and the 1 is the abort); ejections/game
  0-2; meetings/game 0-4 median 2.
- Desired: at least three win shapes each occurring in ≥10% of games (aspirational
  end-state; Wave 2 + balance accounting are the levers).

## R6 — Agency at the margins (the upside hunt)

Unprompted strategic behavior — the model doing something the design didn't script.
- Metrics: emergence-census class count and per-class frequency, tracked per record.
- Last known: 1 confirmed class (impostor strategic skips protecting a steered target,
  seed 10 m2); opt-in usage 73/73 substantive is a second candidate.
- Desired: the census grows; confirmed classes feed toolkit/contract ambition instead of
  being rediscovered by accident.

## R7 — Legible stories

A game's bytes can be narrated: who suspected whom, why, and what turned the vote.
- Metrics: evidence-bearing meeting share; accusation→evidence linkage (voices with
  observation backing, ballot_follows_chain); free_text discipline (median/p95); the
  spot-walk test — can a seed's story be auto-assembled from transcript + graphs + markers
  alone (the Phase-11 spectator hook).
- Last known: 49% of meetings carry contradictions (up from 38%); voices 100%
  observation-backed by construction; free_text medians ~220 chars with a 1/264
  catastrophic tail.
- Desired: a random seed's spot-walk reads as a story without consulting source code.
  This item IS the Phase-11 front-end brief in miniature.

---

Scoring discipline: reports cite items as R1..R7; rubric is versioned per measurement era
(this is v1, pre-fresh-10.9); changes to the rubric are owner decisions, recorded here
with dates.
