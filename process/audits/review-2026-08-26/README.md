# The 2026-08-26 two-track Wave-0 audit — the grounding for Phase 21

Two independent audits of the tree at HEAD `d8ec0a1c` (the Phase-20 close merge), run **before**
any Phase-21 plan was drafted, so the plan is grounded in verified findings rather than in the
handoff's leads. Both tracks ran blind to each other, by the 2026-08-19 three-track review's
method: parallel finder fan-out → dedup/collation → **independent adversarial verification**,
where every finding was re-run against fresh code and bytes by a verifier instructed to refute
it (default REFUTED when evidence does not reproduce). Every claim in the two registers carries
the commands that produced it and the outputs they printed.

**Why now.** The next phase's mandatory step is the ML re-ground: re-fitting the surrogate and
conviction models to the committed baseline-7 bytes. Fitting to a substrate with unfixed
behavioral oddities bakes those oddities into the optimizer — so the audit runs first, and the
re-ground's contract is written against its verdicts.

**The substrate audited.** Baseline 7, canon by explicit owner override of a FINDING verdict
(bars 1 and 2 of the pre-registered rule missed — bar 1 by 0.0078; nothing re-priced;
`audits/audit-phase-20-baseline-7.md` §6.1). 300 committed games over four sets; prompt set
`qwen3_6_27b` v4; 22 substrate flags, 21 unconditional, `impostor_roll_call` OFF.

## 1. The two tracks and their tallies

| track | mandate | agents | canonical findings | CONFIRMED | ADJUSTED | REFUTED |
|---|---|---|---|---|---|---|
| **A — gameplay** ([register](A/collated-findings.md)) | is the game behaving as intended? — meetings, ballots, reporter justice, herding, dialect, flow edges, the evidence economy, legibility | 19 (8 find, 1 collate, 10 verify) | 48 | 13 | 35 | 0 |
| **B — code-up** ([register](B/collated-findings.md)) | correctness and quality from the code up, and: is the tree shaped so the re-ground can optimize better, not just re-fit? | 21 (8 find, 1 collate, 12 verify) | 56 | 18 | 37 | 1 |

Post-verification severity (the verifier's correction wins): **A** — 14 P1, 14 P2, 17 P3, 3 P4;
every one of the four findings filed at P0 was adjusted to P1 on realized-exposure grounds, and
the registers record each adjustment beside the original. **B** — 6 P1, 30 P2, 19 P3, 1 refuted
(B-34, a specified-and-ratified behavior filed as a defect). ADJUSTED means the core observation
stands and the verifier corrected the claim, the severity, or the classification — a large share
of the adjustments are findings whose numbers reproduce exactly but which turned out to be
re-measurements of already-routed items, or readings of specified behavior as defect; each
verdict names its grounds.

## 2. What will bear weight (the short list)

Each line is one sentence; the register entry carries the full evidence and the verifier's
independent re-run.

1. **The 42 innocent ejections now have a per-case ledger** (A-10): 30 of 42 eject the meeting's
   own body reporter (A-4), who on these bytes is innocent with probability 1 (A-25: recorded
   impostor reports are 0/626); the reporter is structurally mute after turn 0 while
   `reporter_exculpation` bites only at ballot time (A-5); "accuse the reporter" is 70.7% of the
   impostor's accusation output (A-24). This falsifies the prior review's disposition that the
   ballot-time guard "holds" — it holds only where the evidence gate already decided.
2. **The machinery dialect is taught, not emergent** (A-6, CONFIRMED): two v4 template lines
   literally read *"The engine certified these"*; leak is 78 utterances across 44 of 300 games —
   13.8% of meetings where the block renders, 0.0% where it does not. A prompt fix, hence a
   recorded-byte change.
3. **Four live consumers re-derive contradictions without the private grounding channels**
   (B-6, CONFIRMED): the conviction model's own referee label, the `flags_per_meeting` supply
   gauge, watchability, and vote-correctness disagree with the recorded flag set on 61/476
   corpus meetings and invert the STRONG/WEAK band on the whole `alibi_vs_sighting` class —
   the exact corpus the re-ground fits is labeled by a detector counterfactual.
4. **Guard-redirected ballots enter the fit as if the voter had authored them** (A-3 + A-26):
   ~120 recorded ballots carry a guard-rewritten target under the original rationale, 25 meeting
   outcomes flipped, and the surrogate's coerced-row filter recognizes 1 of the 6 audit-marker
   kinds, so ~142 such rows ride into the fit.
5. **The replay records actions that were never applied** (A-14 + B-1, CONFIRMED): a meeting
   trigger aborts the tick and ~2,160 recorded actions — 36 kills, 99 reports, 17 emergency
   calls — are neither applied nor rejected, yet are recorded as submitted.
6. **The meeting has two regimes** (A-20, intended-mechanic): the `vent_sighting` role proof is
   a 100%-precision, 100%-conversion oracle deciding 76% of ejections; without it the table is
   a coin flip — the ML protocol must not learn the oracle as "deduction".
7. **A plain re-fit reproduces NO-GO** (B-11): the surrogate GO bar is saturated on two axes and
   structurally blocked on the third — the re-ground must re-derive its bars, not re-run them.
8. **The memory and referee vocabularies drop the largest testimony shapes** (B-7, B-8, B-9):
   `WhereaboutsClaim` (2,269) and `SawMoveObservation` (1,160) never reach a listener's memory;
   the belief line's "last seen" contradicts the agent's own sightings in 19% of rendered rows;
   the referee's first-hand vocabulary excludes `saw_move`, so 29% of spoken placements can
   never back an accusation.
9. **Two instruments are mis-aimed** (A-8, A-9, CONFIRMED): pooled accusation ECE 0.30/0.28 is
   ~40% teammate-firewall artifact, and the shipped machinery-dialect gauge shares zero
   utterances with the actual leak (0/39 overlap).
10. **Record-truth cells that don't reproduce** (A-15): `replays/ml_corpus/README.md`'s item-8
    numbers do not reproduce on the committed bytes — a provenance-surface defect in exactly the
    class Phase 20 was chartered against.

## 3. Proposed routing (NOT ratified — the Phase-21 planning PR ratifies)

| route | destination | finding ids |
|---|---|---|
| recorded-behavior fixes → **one combined re-record** (cadence doctrine: never two) | Wave 1, before the re-fit | A-6, A-17, A-34, A-31, B-8, the record-fidelity halves of A-14/A-3/B-1; A-1 flagged for an owner ruling (the current ordering is test-pinned as specified) |
| instrument/fit-side fixes, no recorded-byte change | Wave 1, before the re-fit | B-6, A-26, B-40, A-8, A-9, B-9, B-15, B-16, B-17, B-23, B-52, B-48, B-18, B-21, B-19, B-10, A-15, A-16, B-39, B-50, B-51, B-55, B-56 |
| the re-ground contract itself | Wave 1 core | the §10.2 moves + F1's nine campaign pins, B-11 (fresh bars), B-12 (FO-6 reframe), B-13/B-14 (objective shape — the declared carries come due), B-43, B-26, B-20/B-46 (the STALE-amnesty deletion shape), B-44/B-45 (fingerprint scope) |
| the last-injustice levers, pre-registered, own record | Wave 2 | A-4, A-5, A-24, A-37, A-38 (reporter reasoning); A-10's hearsay pile-on + A-19 (herding/calibration); A-11, A-12 (boomerang and the transit charge); B-7 as a candidate testimony lever |
| balance-wave backlog additions / re-quantifications | recorded, not acted on here | A-2 (G-22), A-13, A-20, A-22 (G-8), A-23 (G-15), A-25, A-27, A-28, A-29, B-24, B-25, B-38 |
| record-only (intended / acceptable-emergent / observations) | the registers | everything else, including the clean negatives A-42 (zero template fragments in 11,727 utterances) and A-45 (impostor deflection is varied and grounded) |

## 4. What this review is not

No code changed. The campaign tier stays RED exactly as the close declared (F1's nine, verified
at this HEAD before the audit ran). Nothing here re-prices the baseline-7 record or its verdict.
The known-open re-quantifications (G-8, G-15, G-22, G-31's speech half, G-29, G-37) are recorded
as deepenings, not new findings, and each register entry says which. Evidence commands that name
one-session scratch scripts are that session's reproductions; any number that becomes
load-bearing in a Phase-21 contract must be re-derived by that contract's own Measurement
command before anything is built on it.
