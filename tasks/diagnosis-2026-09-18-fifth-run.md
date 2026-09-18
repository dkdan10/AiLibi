# Why the fifth live run of the fresh-model deduction instrument was inconclusive

Diagnosis of 2026-09-18, written by the coordinator from four independent
read-only investigations, one synthesis and two adversarial refutations of
that synthesis, which rewrote its headline (section 10). A third refuter's
report was lost to a formatting failure; the one figure its partial text
disputed is marked unverified in section 3. Every other figure was recomputed
by at least two of those sessions from the fifth run's archive,
`audits/deduction-candidate/run-2026-09-16/` (merged as `42c7181f`, PR #465),
and from the tree at `5c892e24`, whose instrument digest is the one that ran.
The owner approved every decision in section 8 on 2026-09-18; section 11
records the rulings and the cards that carry them.

## 1. What the run measured (facts)

| Figure | reference `repaired_clock` | candidate `combined_accounts` |
|---|---|---|
| Units | 50 | 50 |
| Ejections | 1 | 12 |
| Role-correct ejections | 0 | 4 (2 crew-authored, 2 guard-made) |
| Wrongful (crewmate) ejections | 1 | 8 |
| `supported_correct_ejection` | 0 | 2 (8008, 8025) |
| Ballots naming the ejected player | 2 | 24 |
| Off-target citations among those | 0 | 7 |
| Supported ballots of 150 | 14 | 73 |
| Guard-rewritten ballots | 1 | 46 (44 `uncited_coerced`, 2 `under_gate_redirect`) |
| Nulled `primary_reason_id` / `…_observation_id` | 0 / 0 | 27 / 0 |
| Authored EJECT / SKIP ballots of 150 | 14 / 136 | 119 / 31 |
| Mean ballot confidence (threshold 0.6) | 0.543 | 0.711 |
| Contradiction flags / units carrying one | 14 / 7 | 1 / 1 |

Paired: b=2, c=0, exact McNemar p=0.5, net 2 against a bar of 10. Wrongful net
+7 against a permitted 2. `meets_decision_rule` False, verdict INCONCLUSIVE.

**The prefix's structural identities**, verified on 100 of 100 units rather than
assumed: 4 players, 3 living voters, the impostor alive and voting in all 100, 0
self-votes recorded *and* 0 authored, the crew pair's common legal target set
exactly `{impostor}` in all 100 — fixed by `_candidate_targets` = living-minus-voter
(`meetings/manager.py:4495-4509`), the SKIP rewrite of an out-of-set target
(`meetings/voting.py:147,175`) and `tally_ballots`' strict plurality with SKIP
competing (`:187`). Three consequences are therefore **arithmetic, not findings**:
every crewmate ejection carries the impostor's ballot, every impostor ejection is
two crew ballots, and two crewmates can only ever agree on the impostor.

## 2. Root cause of the wrongful ejections

**Mechanism, two multiplicative stages.** The candidate ejects 2 correct and 8
wrongful because the accusation round hands the tally twice as many wrongful
two-vote coalitions as correct ones, and the gate converts those at twice the rate.

*Stage 1 — the accusation round builds the coalitions.* The reporter is the
trigger and first speaker in 100 of 100 units and a crewmate in 100 of 100, and is
also the table's default suspect in **both arms**: the impostor publicly
mirror-accuses it in 41 of 50 candidate and 47 of 50 reference units (two-sided
binomial p=1.8e-7, p<1e-9), and the non-reporter crewmate — the swing — publicly
accuses it over the impostor 30:12 in the candidate and 32:10 in the reference
(p=0.0079, p=0.00094), then ballots its own stance (reporter→reporter 21 of 30,
impostor→impostor 11 of 12). The bias is arm-invariant; what the candidate changes
is that this speech becomes ballots.

| Authored coalitions and their source | reference | candidate |
|---|---|---|
| Both crewmates on the impostor (correct) | 0 | 11 |
| One crewmate + the impostor on a crewmate (wrongful) | 1 | 22 |
| Crew-on-crew authored EJECT ballots (units) | 6 (6) | 30 (27) |
| …targeting the reporter / authored by the swing | 6 / 6 | 22 / 22 |

*Stage 2 — the gate converts them asymmetrically.* A wrongful coalition needs one
crew ballot and one impostor ballot through the citation gate; a correct one needs
two crew ballots. With crew EJECTs surviving 51.9% and impostor EJECTs 86.8% (§3),
expected conversion is 0.450 against 0.269. Observed: **8 of 22 wrongful
coalitions convert (36.4%), 2 of 11 correct ones (18.2%)**; 11×0.182=2 and
22×0.364=8 are the recorded counts exactly. No residue — all 8 candidate wrongful
ejections and the reference's single one are this funnel's output, and every
coalition clearing the gate ejected (8 of 8, 1 of 1). The 13 ejections, ballots as
*authored* (REP = reporter, SWING = other crewmate):

| Seed | Arm | Ejected | Role | Authored ballots | Shape |
|---|---|---|---|---|---|
| 8002 | cand | SWING | CREW | REP→SWING, IMP→SWING, SWING→REP | crew-on-crew + imp |
| 8006 | cand | IMP | IMP | REP→IMP, SWING→REP, IMP→REP | **guard-made** |
| 8008 | cand | IMP | IMP | REP→IMP, SWING→IMP, IMP→SKIP | crew coalition, scored |
| 8013, 8019, 8021 | cand | REP | CREW | SWING→REP, IMP→REP, REP→IMP each | crew-on-crew + imp |
| 8014 | cand | REP | CREW | IMP→REP, SWING→REP, REP→SKIP | crew-on-crew + imp |
| 8025 | cand | IMP | IMP | SWING→IMP, REP→IMP, IMP→REP | crew coalition, scored |
| 8035, 8045 | cand | REP | CREW | IMP→REP, SWING→REP, REP→IMP each | crew-on-crew + imp |
| 8049 | cand | SWING | CREW | REP→SWING, IMP→SWING, SWING→IMP | crew-on-crew + imp |
| 8056 | cand | IMP | IMP | REP→IMP, SWING→REP, IMP→REP | **guard-made** |
| 8005 | ref | REP | CREW | IMP→REP, SWING→REP, REP→SKIP | crew-on-crew + imp |

**Correction: only 2 of the 12 role-correct ejections are crew-authored.** In
8006 and 8056 the swing authored against the *reporter*; `under_gate_redirect`
(`meetings/manager.py:3697-3706`, provenance `guard_redirected_from` naming the
reporter) re-aimed it onto the impostor. Both record role-correct and both fail
the primary outcome: a redirected ballot fails `voter_authored`
(`experiments/fresh_deduction_instrument.py:4290`, asserted at `:4482`); 8006 also
carries one off-target citation, failing `:4491`; and 8056 cleared the gate only
as the run's single contradiction-flagged unit (`meetings/manager.py:3785-3792`).
Crew-authored role-correct ejections are therefore **2 of 12 (16.7%)**, below the
1/3 chance rate for a 3-player table, not the recorded 4 of 12 (33.3%) — and those
2 are exactly the 2 that scored. (`RESULTS.md:209` attributes 8006's loss to
relevance alone, omitting the support conjunct; no graded figure moves.)

**The victim is usually the crewmate who was right**, and **exposure is ruled out
as the source of the bias.** The candidate's opener names the true impostor in 40
of 50 units, the reference's in 36 of 50; of 12 candidate ejections, 6 remove that
correct opener, 4 the impostor, 2 another crewmate. Yet the accounts opener is
twice the reference's (509.6 chars vs 248.2, 13.3 structured observations vs 3.8,
longest speaker 46 of 50 vs 21 of 50) and the bias is *no stronger* for it —
reference swing 32:10 against 30:12, reference impostor 47 of 50 against 41.

## 3. Root cause of the citation failures (the 44 coerced ballots)

**Mechanism.** v4 repaired the observation channel completely and left the turn
channel broken, because the accounts transcript mints a second id vocabulary the
ballot validator has no entry for.
`agents/strategic/prompts/qwen3_6_27b/_account_transcript.j2:19,22` renders every
evidence row as `[turn:<turn_id>:obs|whereabouts:N]` and `[turn:<turn_id>:claim:N]`,
while `meetings/manager.py:3198` recovers only via `_REASON_ID_TURN_SUFFIX` at
`:628`, end-anchored on `:turn-(\d+)` — so a sub-row suffix blocks recovery and
`:3203` nulls the id. With both fields null, `guard_ballot_citation`
(`:3710`) coerces the EJECT to SKIP unless the target is flagged.

| Coerced class | n | Crew / impostor | Argues cross-testimony | Own-memory only |
|---|---|---|---|---|
| Copied a sub-row id, nulled | 21 | 17 / 4 | 11 | 10 |
| Emitted both ids null | 23 | 22 / 1 | 17 | 6 |

Shapes of the 27 nulled ids: 20 end `:claim:N`, 6 end `:obs:N`, 1 other; 3 keep the
leading `turn:` tag word. 26 of 27 strip to a real `turn_id` in that meeting, and
all 26 of those turns mention the ballot's authored target — present and on point,
only the shape rejected. All 44 also had usable private evidence: every voter's own
vote prompt carries at least one `[obs ...]` line naming the coerced target (min 2,
median 4, max 18). The class is "evidence present, not cited".

**Why the candidate never uses the turn channel.** 0 of its 150 ballots carry a
surviving `primary_reason_id` (reference: 14 of 150, 0 nulls).
`vote_ballot_accounts.j2:21` works a bare-id example for
`primary_reason_observation_id` only and `:23` prefills `primary_reason_id` null
with no shape and no warning, where `vote_ballot.j2:263` prefills
`transcript.turns[-1].turn_id` and `:266` says copy it VERBATIM. Its 300 prompts
carry 563 `:claim:N`, 4,346 `:obs:N`, 2,135 `:whereabouts:N`; the reference's 18,
12 and 12. (A third refuter disputed the three reference figures and its
recount was lost to a formatting failure; treat them as unverified. No
conclusion rests on them.)

**The gate is role-asymmetric and is not a quality filter.**

| Candidate authored EJECTs | Crew | Impostor |
|---|---|---|
| Authored / survived the gate / coerced | 81 / 42 (51.9%) / 39 | 38 / 33 (86.8%) / 5 |
| Names the impostor, survived | 25 of 42 (59.5%) | 0 of 33 |
| Names the impostor, coerced | 26 of 39 (66.7%) | 0 of 5 |

Crew authored EJECTs name the impostor 51 of 81 (63.0%); the gate removes them at
a rate uncorrelated with correctness (59.5% vs 66.7%) and strongly correlated with
role. That asymmetry is §2 stage 2, and is why the recorded ejection set is worse
than the authored one.

## 4. Why the reference arm is inert

The reference does not fail to cite. It declines to vote. 136 of its 150 ballots
are authored SKIPs, there are 0 coercions and 0 nulled ids, all 14 of its authored
EJECTs carry a citation, mean ballot confidence is 0.543 against a 0.6 threshold,
and only 1 of 50 meetings reached two agreeing ejects. It is not blindness at the
deliberation layer: its opener names the impostor 36 of 50 against the candidate's
40 of 50, and §2 shows its speech layer carries the same reporter bias at the same
strength. The prose differs accordingly — `vote_ballot.j2:114,259` states the SKIP
discipline repeatedly, `vote_ballot_accounts.j2:1,21` gives it one clause. That is
a design confound worth naming: the arms differ in the accounts surface **and** in
the ballot register, so the run cannot attribute the candidate's 8.5x rise in
willingness to accuse to the accounts surface — and any diagnostic that counts
authored ballots inherits that confound (§5, §7 F1).

Secondary: the candidate's claim vocabulary collapsed to accusations only (139 / 0
/ 0 against the reference's 142 / 33 / 13) and its contradiction detector went
nearly silent with it (1 flag vs 14, 13 `alibi_vs_sighting`) — which is why the
gate's zero-flag branch is live in 49 of 50 candidate units.

## 5. What the primary outcome can and cannot distinguish

`supported_correct_ejection` requires an ejection, role-correct, every naming
ballot supported and voter-authored, every citation relevant — all downstream of a
2-of-3 tally and of a gate removing 48.1% of crew EJECTs and 13.2% of impostor
ones. It cannot separate "the crew did not deduce" from "the crew deduced and the
channel ate the ballot": a coerced unit records as SKIPPED, like a unit where
nobody reasoned. With the reference pinned at 0, net-10 is an absolute bar.

**The read that survives refutation** is the crew's *per-ballot* authored
precision, conditioned on having authored at all, beside a harm counter on the
same denominator:

| Diagnostic (authored ballots, pre-guard) | reference | candidate |
|---|---|---|
| Crew EJECTs naming the impostor | 4 / 10 (40.0%, p=0.83) | 51 / 81 (63.0%, p=0.013) |
| Crew EJECTs naming the other crewmate | 6 / 10 | 30 / 81 |
| Units with a crew-on-crew authored EJECT | 6 / 50 | 27 / 50 |
| Ejection precision vs the 1/3 chance rate | n/a (1 ejection) | 4 / 12 as recorded, P(X≥4)=0.61; 2 / 12 crew-authored, P(X≤2)=0.18 |

The null is 0.5, each crewmate having exactly two legal targets. 63.0% is the one
deduction signal here that is neither an identity nor a volume artifact — but it
is a per-ballot rate, so it cannot feed a paired McNemar test and must never be
promoted to primary; its reference cell rests on 10 ballots; and it stays
confounded with the register until F7 ships.

**Not this: crew-bloc unanimity**, which an earlier draft proposed as the
replacement. Withdrawn. §1 shows the crew pair's legal targets intersect in exactly
`{impostor}`, so "11 of 11 correct" and "0 false unanimity" are
precision-by-construction. It is also monotone in accusation volume (both crewmates
authored an EJECT in 35 of 50 candidate units against 1 of 50, so the 11-vs-0
separation *is* the §4 register confound) and blind to harm (all 8 wrongful
ejections have namer set {crew, impostor} and score 0). Conditioned on opportunity,
unanimity is 11 of 35 (31.4%), *below* the 39.7% independence prediction from its
own 63.0% marginal (P(X≥11|35,0.397)=0.88) and not separable from uniform
targeting (P(X≥11|35,0.25)=0.24). It adds nothing beyond the per-ballot rate.

## 6. Alternatives considered and rejected

| Alternative | Verdict and evidence |
|---|---|
| The candidate deduces worse | Rejected. Crew authored EJECTs name the impostor 51/81 (63.0%, p=0.013) vs the reference's 4/10; opener correct 40/50 vs 36/50 |
| The gate is a quality filter removing weak crew votes | Rejected. Coerced crew EJECTs correct 26/39 (66.7%), survivors 25/42 (59.5%): anti-correlated with correctness, correlated with role |
| The wrongful ejections are a citation defect | Rejected. All 8 carry a valid observation citation on both naming ballots; the gate tests validity, never relevance (`meetings/manager.py:3710` ff) |
| The nulled ids are hallucinations | Rejected. 26 of 27 strip to a real turn in that meeting, and all 26 of those turns name the authored target |
| The v4 citation-id fix was a minor repair | Rejected. Re-tallying with every observation id nulled as v3 nulled them, the candidate ejects once (8056) and the reference once; both scoring seeds and all 8 wrongful ejections exist only because of v4 |
| Repairing the turn-id vocabulary makes the next run about deduction | Rejected as stated. Restoring only the 21 sub-row coercions gives 20 ejections, 6 role-correct, 14 wrongful: precision 33.3%→30.0%, wrongful net +7→+13, exactly as §2 stage 2 predicts |
| Port the reference's prefilled skeleton id into the candidate | Rejected. 7 of the reference's 14 kept turn citations are exactly the last-turn id `vote_ballot.j2:263` prefills — support without relevance, in both arms |
| "The impostor supplies the second vote" is the mechanism | Rejected as vacuous (§1, §10.1): true in every possible run of this prefix |
| A larger voter body would fix it | Not testable here; the prefixes are 4-player by construction. Flagged, not rejected |

## 7. Fix plan, smallest change first

| # | Change | Touches | Alters outcome / rule / bound / stop rule | One-sided |
|---|---|---|---|---|
| F1 | Report crew per-ballot authored precision vs 0.5, the crew-on-crew authored rate beside it, and ejection precision vs 1/3 — as labelled **diagnostics**, never a preregistered secondary | instrument report assembly, its tests, manifest diagnostics section | no | **yes in effect**: authoring-conditioned, so it inherits the §4 register confound and reads high for whichever arm authors more; publish only paired with its harm counter, never as a decision input |
| F2 | Add `how do` to `_NOT_AN_ASSERTION` (`experiments/fresh_deduction_instrument.py:6269`) | instrument, its tests, manifest leak section | no | no, symmetric |
| F3 | Record per-call `finish_reason` in run mode | instrument call recorder, its tests, manifest | no | no |
| F4 | Give `vote_ballot_accounts.j2:21,23` the turn-id shape and a never-abbreviate warning, without prefilling a real id | one candidate prompt, prompt-version bump, tests | bound only, and it worsens it (+7 → +13 wrongful net here) | yes, candidate only |
| F5 | Let `_normalize_ballot_reason_id` strip a leading `turn:` and a trailing `:claim\|obs\|whereabouts:N` before lookup (`meetings/manager.py:628,3198`) | shared frozen substrate, manager tests, fixture, manifest | same as F4, and re-baselines both arms | yes in effect |
| F6 | Make `guard_ballot_citation` test aboutness by reusing `_cited_line_names` (`experiments/fresh_deduction_instrument.py:4366`) | shared substrate, manager tests, manifest, both arms re-baselined | yes, changes which ejections happen in both arms | candidate-weighted in practice |
| F7 | Port `vote_ballot.j2:114,259`'s SKIP register into `vote_ballot_accounts.j2` so the arms differ in the accounts surface only | one candidate prompt, version bump, tests, manifest design section | bound only, and it improves it | yes, candidate only |
| F8 | Second citation slot for a conflict between two accounts (the 23 bare nulls, 17 cross-testimony) | `meetings/schemas.py`, manager validators and guard, both prompt families, graders, manifest, preregistration | yes | no, both arms |

F1–F3 are instrumentation: no recorded byte moves, no provider call, F1 derivable
from this archive today. F4–F8 change measured behaviour and need re-baselining;
F5/F6 edit shared substrate. **F6 alone attacks §2 stage 2 and F7 alone attacks
stage 1's volume**, so a wave shipping F4 or F5 without both worsens the tradeoff.

## 8. Owner decisions

| # | Decision | Recommendation | Cost / hidden cost |
|---|---|---|---|
| 1 | The preregistered choice (`execution-manifest.md:1780`) | **Revise and evaluate a new version** | A new manifest, a new held-out band, one sitting of ~2 hours at $0 marginal. Rejecting discards a candidate whose crew names the impostor on 63.0% of its authored EJECTs against chance; advancing is unavailable, the rule failed all three clauses |
| 2 | Adopt F1 before further spending? | **Yes, as a labelled diagnostic only** | One instrument patch, a manifest amendment, no provider call. Hidden: authoring-conditioned, so it flatters whichever arm authors more — ship it with the crew-on-crew rate beside it and never preregister it |
| 3 | Which outcome is primary next time? | **Keep `supported_correct_ejection`; add no secondary** | No candidate secondary survived refutation: bloc unanimity is precision-by-construction (§5, §10.2), the per-ballot rate cannot be paired. The bar of 10 stays out of reach if the gate is untouched, so this coheres only with 4 and 5 |
| 4 | Ship a citation-channel fix (F4 or F5)? | **Yes, F4 only**, prompt-side, in a re-baselining manifest, **and only in the same wave as F6 and F7** | One-sided; on this archive it raises the wrongful net from +7 to +13, so shipped alone it fails the tradeoff clause by construction |
| 5 | Ship F6, the relevance-aware gate? | **Yes**, same wave | The only change that costs the impostor its free pass — 4 of its 8 naming ballots are off-target and §2 stage 2 is entirely its 86.8% survival. It edits shared substrate and invalidates the reference baseline |
| 6 | Equalise the ballot register (F7)? | **Yes** | Candidate ejections fall and the run stops confounding register with accounts surface. Without it, F1's diagnostics are not interpretable across arms |
| 7 | Restate `WRONGFUL_EJECTION_TRADEOFF` on the reference ejecting at all? | **No — withdrawn** | See below |
| 8 | Value: the next band | **Freeze a sixth band before any live run** — 8000-8999 is now development data | One freeze PR |
| 9 | `_NOT_AN_ASSERTION` word-list gap (F2) | **Yes, fix it** | `:6269` carries `why would`, `how would`, `what would` but not `how do`, which is why seed 8014's interrogative turn counts as a reference leak. One regex line and a test; instrument defect, not a record one, and both readings stay published |
| 10 | Per-call `finish_reason` in run mode (F3) | **Yes** | No per-call distribution exists, so the truncation column is a single aggregate. One recorder field and a test |

**Decision 7 in full.** The earlier draft proposed a candidate-only 50% precision
bar with the paired net dropped when the reference ejects fewer than 3 in 50.
Three costs kill it. Its trigger is already satisfied by data in hand (the
reference ejected 1), so it is post-hoc, not prospective. The frozen rationale at
`experiments/fresh_deduction_instrument.py:700-706` names this exact failure — "a
candidate that merely raises the ejection RATE: converting reference-arm skips
into ejections lifts both counts together" — on a run that is an 8.5x rise in
accusation volume. And a 50% bar alone permits 6 wrongful in 12 where the current
bound permits a net of 2, while this run (33.3%, or 16.7% crew-authored) and the
F4 counterfactual (30.0%) fail it anyway. A precision floor belongs as a fourth
clause the candidate must *also* clear, never as a replacement for the net.

## 9. What this run DID establish

1. The instrument runs to completion (100 of 100 units, one sitting, 0
   truncations, 0 defaulted votes, 1 defaulted turn, $0) and the archive is exactly
   reproducible — a re-tally reproduces every ejection, seed and per-ballot verdict.
2. The candidate's crew deduces above chance **per ballot**: 51 of 81 authored crew
   EJECTs name the impostor (63.0%, one-sided p=0.013 against the 0.5 null of two
   legal targets) against 4 of 10 in the reference — conditioned on authoring, so a
   diagnostic, not a paired outcome (§5).
3. Its 12 ejections are not that signal: 2 crew-authored role-correct (16.7%,
   below the 1/3 chance rate) plus 2 the guard re-aimed. The mechanism is §2's
   funnel — 22 wrongful authored coalitions against 11, converted 36.4% vs 18.2%.
4. The reporter-suspicion behind those coalitions is arm-invariant and therefore
   *not* an accounts-surface effect (swing 30:12 vs 32:10, impostor 41/50 vs 47/50,
   on an opener twice as long).
5. The v4 citation-id fix is the entire ejection delta: under v3's nulling the
   candidate ejects once, so that pre-declared one-sided effect accounts for 11 of
   12 ejections and both scoring seeds.
6. The turn-citation channel is dead in the candidate and located:
   `_account_transcript.j2:19,22` renders ids `meetings/manager.py:628` cannot
   validate; 26 of 27 nulled ids point at a real turn naming the target. The
   reference's inertness, by contrast, is a ballot-register effect, so the
   comparison confounds the accounts surface with the register.

## 10. Refutations considered

1. **ACCEPTED — "the impostor supplies the second vote" is a theorem.** With 3
   living voters, no self-votes and `_candidate_targets` living-minus-voter, only
   the other crewmate and the impostor can name crewmate X, and only the two
   crewmates can name the impostor (verified 100/100). §2 is rebuilt on the
   coalition funnel; the old claims are quarantined in §1 as arithmetic.
2. **ACCEPTED — crew-bloc unanimity cannot register a false positive**, by the
   same identity, **and the 11-vs-0 gap is an authoring-rate gap**: both crewmates
   authored an EJECT in 35 of 50 candidate units against 1 of 50, and conditioned
   on that, unanimity is 11 of 35 (31.4%) — below the 39.7% independence prediction
   from the 63.0% marginal. Withdrawn from §5 and §9; F1 uses the per-ballot rate.
3. **ACCEPTED — "role-correct means both crewmates converged on the impostor" is
   false for 8006 and 8056**, where the swing authored against the reporter and
   `under_gate_redirect` re-aimed the ballot. Crew-authored role-correct is 2 of
   12, not 4 (§1, §2, §9.3).
4. **ACCEPTED — the old reason for demoting exposure was invalid.** "The reference
   shows the same cascade without converting it" cannot discriminate, the reference
   being inert at the ballot layer by register. Replaced with a *speech*-layer
   discriminator: twice the opener length, the same or weaker bias (§2).
5. **ACCEPTED — decision 7 as drafted drops the volume guard on a volume-driven
   run.** Withdrawn; §8 decision 7 gives the three costs.
6. **REJECTED IN PART — "6 of the 8 wrongful ejections are REP accuses IMP → IMP
   mirrors onto REP → SWING joins on REP".** Six counts the *reporter* ejections,
   not the 8 wrongful: 8002 and 8049 invert the roles (the reporter authors on the
   swing, the impostor joins). And only 5 of the 6 carry the full public chain — in
   8045 the swing published no accusation yet still balloted the reporter. §2's
   funnel covers all 9 wrongful ejections in both arms, no residue.
7. **REJECTED — "the swing speaks last of 3 turns".** Every meeting has 3 turns
   (100/100) but the swing speaks last in 76 of 100, not by construction. The
   mechanism rests on its public stance predicting its ballot (21/30 and 11/12
   above), not on turn order.
8. **REJECTED IN PART — "the rate-limiting step is the accusation round, not the
   tally or the impostor's vote".** That round is the *source* (22 wrongful
   coalitions against 11 correct) but is not alone rate-limiting: the gate converts
   36.4% of wrongful coalitions against 18.2% of correct ones, and that 2x
   asymmetry turns an authored 11:22 into a recorded 2:8. Both stages are
   load-bearing — hence §8 pairs F6 with F7 and refuses F4 alone.

## 11. Rulings (2026-09-18)

The owner approved the ten decisions of section 8 as a set on 2026-09-18, in
the coordinator's session.

| Decision | Ruling | Carried by |
| --- | --- | --- |
| 1. The preregistered choice | revise and evaluate a new version | the wave below, then [a third development calibration](work/fresh-deduction-calibration-3.md), then a sixth authorization with its limits card, opened after that calibration reports |
| 2. Crew per-ballot authored precision with its harm counter (F1) | approved, as a labelled diagnostic only, never preregistered | [the instrument diagnostics card](work/fresh-deduction-instrument-diagnostics.md) |
| 3. The primary outcome | kept as `supported_correct_ejection`; no secondary | none |
| 4. The turn-id shape in the candidate's ballot prompt (F4) | approved, only in the same wave as 5 and 6 | [the v5 accounts card](work/accounts-prompt-set-v5.md) |
| 5. The relevance-aware citation guard (F6) | approved, same wave, as a default-OFF lever both arms of the next evaluation enable | [the citation guard card](work/relevance-aware-citation-guard.md) |
| 6. Port the SKIP register into the candidate's ballot prompt (F7) | approved | the v5 accounts card |
| 7. Restating `WRONGFUL_EJECTION_TRADEOFF` | no; the bound stands as frozen | none |
| 8. A sixth held-out band | approved | [the sixth freeze card](work/held-out-prefix-freeze-6.md) |
| 9. The leak rule's `how do` gap (F2) | approved | the instrument diagnostics card |
| 10. Per-call `finish_reason` in run mode (F3) | approved | the instrument diagnostics card |

The wave rule of section 7 binds the order: the v5 prompts and the guard ship
in one re-baselining manifest, because the turn-id repair alone raises the
wrongful net from 7 to 13 on this archive. F5 (the validator-side strip) was
not chosen, decision 4 taking the prompt-side repair instead, and F8 (a second
citation slot) was not put for decision; both stay recorded in section 7. The
third calibration measures the whole wave on development inputs before any
ceiling is sized or any held-out seed is drawn.
