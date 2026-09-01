# Agent Prompt — 21.21 THE OFFLINE COUNTERFACTUAL: the Wave-2 levers over the re-recorded bytes, published before any bar is written

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.21 — THE OFFLINE COUNTERFACTUAL: the Wave-2 levers over the re-recorded bytes, published before any bar is written, anchored to A-10 [ADJUSTED, P1] — audits/review-2026-08-26/A/collated-findings.md:1138-1344 (the 42-row innocent-ejection ledger and its class totals RC 30 / BOOM 29 / PIT 17 / IMP-RIDES 33 / WEAKFLAG 5 / REDIRECT 4 / ENDGAME 5, reproduced row for row by the verifier at :1291-1298 including every vote tally; the citation mix of the 145 ejecting ballots hearsay 79 / own_obs 40 / own_turn 26 / other_obs 0 / none 0 at :1300-1303; 37 of 42 ejectees carried no contradiction flag at all; the verifier's TWO binding corrections at :1143 and :1332-1335 — "only 4 of the 42" is wrong on the finding's own ledger (six rows carry nothing beyond IMP-RIDES and/or PIT, of which three are PIT, so the pure-herd set is the THREE rows C9 1008:m2, C9 1066:m0, C9 1106:m3) and two supporting cells drift by one under a different tie-break (pile-driver CREW 27 filed vs 28 measured, IMP-RIDES pivotal 14 filed vs 13 measured), and its ruling at :1298 that "PIT is a judgement net in both readings and should be quoted as such"; the verifier note at :1338 that this ledger "is an acceptance-test artifact ... and should be scheduled with the levers it scores"); A-4 [ADJUSTED, P1] :431-612 (30 of 42 innocent ejections eject the meeting's own reporter; 618 body-report meetings of 668, 50 emergency; reporter_is_impostor 0/618; reporter ejected 30/618 = 4.85% against innocent non-reporter 12/1844 = 0.65%, RR 7.46x, z=6.98; 28 of the 30 convictions carry NO contradiction naming the reporter; pooled ejection accuracy 387/429 = 90.2%; the verifier's correction that the reporter's ejectability is a RECORDED design decision, not an oversight, and that the channel is down ~2.6x from baseline 2); A-5 [ADJUSTED, P1] :614-691 (3312/3312 ballot prompts carry the exculpation block, 0/2694 non-reporter speech prompts carry any structured statement that a body was reported; turns-per-speaker histogram {1: 3312}; reporter turn kinds {opening: 618}; accusations against the reporter by turn index summing to 1061, all at index >= 1; 508/618 meetings accuse the reporter after their only turn; the verifier's framing correction that the load-bearing anchor is `grep -c reporter` = 0 in all five non-ballot templates against 5 in vote_ballot.j2, NOT the memory census); A-24 [ADJUSTED, P2] :2901-2954 (impostor accusations at the reporter 521/737 = 70.7% against crew 540/1513 = 35.7%; the verifier's correction that the ~2x ratio is a STANDING pattern — 64.2% baseline-6 vs 65.9% baseline-7 like-for-like — and that what is new and adverse is the BALLOT-side regression, reporter-directed ballots 2.2% -> 9.6% crew and 4.1% -> 17.1% impostor on the same seeds); A-37 [ADJUSTED, P3] :3950-4004 (the exculpation is almost never argued: ~28 rationales co-mention with an exculpatory hinge and ~19-20 genuinely argue it, against the filed "16 co-mentions, ~5 genuine"; at least one reporter DOES invoke it at ballot time; the "generic under-gate redirect is what bites" attribution is a mis-attribution that omits the soft-lift cap); A-38 [ADJUSTED, P3, fix_sketch REJECTED] :4006-4052 (121/618 meetings carry a non-reporter with the identical discovery line; innocent co-discoverers ejected 3/89 = 3.37% vs 9/1755 = 0.51%, Fisher p=0.017; and the reason the widening was rejected — 51 of the 140 non-reporter co-discoverer slots, 36.4%, are IMPOSTORS); A-11 [ADJUSTED, P2] :1346-1447 (the boomerang convicts the opener in 29 of 42, but the verifier DROPS the "0 of 387 impostor ejections" contrast as a tautology — the opener is the trigger actor in 668/668 and the trigger actor is a crewmate in 668/668 — and re-prices the shape at 29/492 = 5.9% overall, 29/271 = 10.7% inside the no-vent-flag half against 1/71 = 1.4% without it); A-12 [ADJUSTED, P1] :1449-1566 (>= 1 impossibility-asserting convicting ballot in 17 of 42, >= half in 15 of 42 = 35.7%; the map card renders in every meeting call; the verifier REPLACES "provably false every time" — the test performed is true by construction for every crewmate — and re-prices the enrichment inside the no-vent-flag stratum at 15/19 = 78.9% against a 42/103 = 40.8% base = 1.9x); A-19 [ADJUSTED, P2] :2252-2343 (the verifier REFUTES the "turn >= 2 is pure noise" headline by a decomposition the filing never ran: turn >= 2 crew accusations naming the SAME target as turn 0 hit 79.2% (n=48) and 88.5% (n=122), different-target 4.7% (n=106) and 3.1% (n=287); the pooled lift is a mixture artifact; the turn-1 row conditions on the opener having been wrong; and the ML advice "down-weight turn >= 2 soft accusations" is WITHDRAWN); B-7 [CONFIRMED, P1] — audits/review-2026-08-26/B/collated-findings.md:565-624 (WhereaboutsClaim 2,269 and SawMoveObservation 1,160 never reach a listener's memory; the verifier's own census over 476 corpus meetings reproduces the table exactly and adds that CompletedTaskObservation 310 and FoundBodyObservation 586 also fall through, so the gap is four shapes; alibi_map fed by 706 of 2,975 location accounts = 23.7%; the precision note that whereabouts DO still move suspicion through the scalar channel); A-22 [ADJUSTED, P3] audits/review-2026-08-26/A/collated-findings.md:2610-2793 (5 of 517 spoken saw_vent rows name a subject who never vented, all 5 joining that speaker's own witnessed kill on killer+room+tick; 448/448 vent_sighting contradictions engine-backed; the verifier's bound that all 5 named a real IMPOSTOR and all 5 meetings ejected that impostor, so the damage is legibility only, and that "65 ungrounded saw_vent rows" is an inflated denominator); A-16 [ADJUSTED, P2] :2006-2084 (the instrument half stands: the self-kill and role nets never run over the player-visible surface; the gameplay inference is corrected — both confessors were ejected in the meeting they confessed in; and the fix is conditioned: the raw net fires 10 times player-visible, 4 IMPOSTOR / 6 CREWMATE, only 2 genuine = 20% precision overall, 50% within impostor speakers, so it ships only with a disambiguation step against the ground-truth kill record); A-3 :242-429 (the ~120 guard-redirected ballots, 25 flipped meeting outcomes, 3 ejections nobody voted for — the REDIRECT class of the ledger, and the reason this script reads a structured provenance field rather than parsing a marker string); audits/audit-phase-20-counterfactual.md §0-§3 (the headline-then-baseline discipline), §4.1 (per-row reading rules), §7 (the cells no offline instrument can reach), §8 (per-lever predictions with leave-one-out attribution), §9 (abandon criteria), §11 (reproduction; 28 s over 300 games, $0, no network) — the protocol this task mirrors; audits/audit-phase-20-baseline-7.md §6.1 (THE OWNER'S ADOPTION RULING, 2026-08-26: the decision rule "STANDS AS FINDING — bars 1 and 2 missed as measured, nothing is re-priced", and separately, by explicit owner prerogative, baseline 7 is adopted as canon) and §3 bars 1 and 2 (non-direct accuracy 61/103 = 0.5922 against >= 0.60, innocent ejections 42 against < 35 — the two missed bars whose successors the pre-registration will write from this memo's cells). Anchors re-verified at HEAD `4002f19b` by direct read: orchestrator/replay.py:524-546 (`_RETIRED_ALWAYS_ON_LEVERS`, twenty-one keys), :568-570 (`_TOGGLEABLE_LEVER_RESOLVERS` — ONE live toggle at HEAD, `impostor_roll_call`), :578-580 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS`), :585-588 (`SUBSTRATE_FLAG_KEYS`), :591 (`substrate_flag_snapshot`, the threaded-`env` seam), :617 (`env_var_for_lever`), :651 (`substrate_slate_mismatches`), :713 (`fold_meeting_outcome_into_memories`); meetings/manager.py:1776-1779 and :1831 (`reporter_id` derived at meeting scope and passed to the vote prompt and to nothing else), :3768 (`derive_reported_testimony` — the register's :3822-3875 loop anchors sit inside this function); meetings/schemas.py:539-541 (`ReportedStatementKind`, five members); agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:171-175 (the only home of the exculpation block); meetings/transcript.py:1490-1500 (`detect_contradictions` — NOTE: it no longer carries the `env` keyword the Phase-20 counterfactual toggled; that seam was deleted at the graduation sweep, so the Wave-2 levers supply their own); eval/evidence_honesty.py:861 (`compute_evidence_honesty`, a DIRECTORY argument and no lever-slate parameter — the 20.34 anchor :850 has drifted), :719-737 (`RenderBudgetCells`), :293 (`CELL_DEFINITIONS`); eval/solvability.py:395 (`compute_solvability_report`); eval/deduction_metrics.py:1120 (`EjecteeProofCrossTab`), :852 (`_wilson_interval`), :2350-2351 region (`player_visible_leak_turns`, the partner net only); eval/replay_walk.py:366 (`walk_replay`); api/replay_loader.py:697 (`ReplayLoader`); agents/memory/store.py:575-588 (`record_alibi`, fed by `alibi` statements only); tests/eval/test_deduction_metrics.py:158, :179, :265, :271, :307, :313 (the committed non-direct and innocent-ejection pins the re-record re-derives); scripts/counterfactual_phase20.py:1-56 and tests/scripts/test_counterfactual_phase20.py:1-92 (the precedent AND its epilogue: the script now REFUSES to run because its eight levers graduated, with `_assert_ambient_slate_is_off` as the guard and a planted case proving the guard bites); tests/scripts/conftest.py:1-18 (bare-module import of `scripts/`).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-counterfactual`
**Depends on:** 21.18, 21.19, 21.20
**Section refs:** A-10 [ADJUSTED, P1] — audits/review-2026-08-26/A/collated-findings.md:1138-1344 (the 42-row innocent-ejection ledger and its class totals RC 30 / BOOM 29 / PIT 17 / IMP-RIDES 33 / WEAKFLAG 5 / REDIRECT 4 / ENDGAME 5, reproduced row for row by the verifier at :1291-1298 including every vote tally; the citation mix of the 145 ejecting ballots hearsay 79 / own_obs 40 / own_turn 26 / other_obs 0 / none 0 at :1300-1303; 37 of 42 ejectees carried no contradiction flag at all; the verifier's TWO binding corrections at :1143 and :1332-1335 — "only 4 of the 42" is wrong on the finding's own ledger (six rows carry nothing beyond IMP-RIDES and/or PIT, of which three are PIT, so the pure-herd set is the THREE rows C9 1008:m2, C9 1066:m0, C9 1106:m3) and two supporting cells drift by one under a different tie-break (pile-driver CREW 27 filed vs 28 measured, IMP-RIDES pivotal 14 filed vs 13 measured), and its ruling at :1298 that "PIT is a judgement net in both readings and should be quoted as such"; the verifier note at :1338 that this ledger "is an acceptance-test artifact ... and should be scheduled with the levers it scores"); A-4 [ADJUSTED, P1] :431-612 (30 of 42 innocent ejections eject the meeting's own reporter; 618 body-report meetings of 668, 50 emergency; reporter_is_impostor 0/618; reporter ejected 30/618 = 4.85% against innocent non-reporter 12/1844 = 0.65%, RR 7.46x, z=6.98; 28 of the 30 convictions carry NO contradiction naming the reporter; pooled ejection accuracy 387/429 = 90.2%; the verifier's correction that the reporter's ejectability is a RECORDED design decision, not an oversight, and that the channel is down ~2.6x from baseline 2); A-5 [ADJUSTED, P1] :614-691 (3312/3312 ballot prompts carry the exculpation block, 0/2694 non-reporter speech prompts carry any structured statement that a body was reported; turns-per-speaker histogram {1: 3312}; reporter turn kinds {opening: 618}; accusations against the reporter by turn index summing to 1061, all at index >= 1; 508/618 meetings accuse the reporter after their only turn; the verifier's framing correction that the load-bearing anchor is `grep -c reporter` = 0 in all five non-ballot templates against 5 in vote_ballot.j2, NOT the memory census); A-24 [ADJUSTED, P2] :2901-2954 (impostor accusations at the reporter 521/737 = 70.7% against crew 540/1513 = 35.7%; the verifier's correction that the ~2x ratio is a STANDING pattern — 64.2% baseline-6 vs 65.9% baseline-7 like-for-like — and that what is new and adverse is the BALLOT-side regression, reporter-directed ballots 2.2% -> 9.6% crew and 4.1% -> 17.1% impostor on the same seeds); A-37 [ADJUSTED, P3] :3950-4004 (the exculpation is almost never argued: ~28 rationales co-mention with an exculpatory hinge and ~19-20 genuinely argue it, against the filed "16 co-mentions, ~5 genuine"; at least one reporter DOES invoke it at ballot time; the "generic under-gate redirect is what bites" attribution is a mis-attribution that omits the soft-lift cap); A-38 [ADJUSTED, P3, fix_sketch REJECTED] :4006-4052 (121/618 meetings carry a non-reporter with the identical discovery line; innocent co-discoverers ejected 3/89 = 3.37% vs 9/1755 = 0.51%, Fisher p=0.017; and the reason the widening was rejected — 51 of the 140 non-reporter co-discoverer slots, 36.4%, are IMPOSTORS); A-11 [ADJUSTED, P2] :1346-1447 (the boomerang convicts the opener in 29 of 42, but the verifier DROPS the "0 of 387 impostor ejections" contrast as a tautology — the opener is the trigger actor in 668/668 and the trigger actor is a crewmate in 668/668 — and re-prices the shape at 29/492 = 5.9% overall, 29/271 = 10.7% inside the no-vent-flag half against 1/71 = 1.4% without it); A-12 [ADJUSTED, P1] :1449-1566 (>= 1 impossibility-asserting convicting ballot in 17 of 42, >= half in 15 of 42 = 35.7%; the map card renders in every meeting call; the verifier REPLACES "provably false every time" — the test performed is true by construction for every crewmate — and re-prices the enrichment inside the no-vent-flag stratum at 15/19 = 78.9% against a 42/103 = 40.8% base = 1.9x); A-19 [ADJUSTED, P2] :2252-2343 (the verifier REFUTES the "turn >= 2 is pure noise" headline by a decomposition the filing never ran: turn >= 2 crew accusations naming the SAME target as turn 0 hit 79.2% (n=48) and 88.5% (n=122), different-target 4.7% (n=106) and 3.1% (n=287); the pooled lift is a mixture artifact; the turn-1 row conditions on the opener having been wrong; and the ML advice "down-weight turn >= 2 soft accusations" is WITHDRAWN); B-7 [CONFIRMED, P1] — audits/review-2026-08-26/B/collated-findings.md:565-624 (WhereaboutsClaim 2,269 and SawMoveObservation 1,160 never reach a listener's memory; the verifier's own census over 476 corpus meetings reproduces the table exactly and adds that CompletedTaskObservation 310 and FoundBodyObservation 586 also fall through, so the gap is four shapes; alibi_map fed by 706 of 2,975 location accounts = 23.7%; the precision note that whereabouts DO still move suspicion through the scalar channel); A-22 [ADJUSTED, P3] audits/review-2026-08-26/A/collated-findings.md:2610-2793 (5 of 517 spoken saw_vent rows name a subject who never vented, all 5 joining that speaker's own witnessed kill on killer+room+tick; 448/448 vent_sighting contradictions engine-backed; the verifier's bound that all 5 named a real IMPOSTOR and all 5 meetings ejected that impostor, so the damage is legibility only, and that "65 ungrounded saw_vent rows" is an inflated denominator); A-16 [ADJUSTED, P2] :2006-2084 (the instrument half stands: the self-kill and role nets never run over the player-visible surface; the gameplay inference is corrected — both confessors were ejected in the meeting they confessed in; and the fix is conditioned: the raw net fires 10 times player-visible, 4 IMPOSTOR / 6 CREWMATE, only 2 genuine = 20% precision overall, 50% within impostor speakers, so it ships only with a disambiguation step against the ground-truth kill record); A-3 :242-429 (the ~120 guard-redirected ballots, 25 flipped meeting outcomes, 3 ejections nobody voted for — the REDIRECT class of the ledger, and the reason this script reads a structured provenance field rather than parsing a marker string); audits/audit-phase-20-counterfactual.md §0-§3 (the headline-then-baseline discipline), §4.1 (per-row reading rules), §7 (the cells no offline instrument can reach), §8 (per-lever predictions with leave-one-out attribution), §9 (abandon criteria), §11 (reproduction; 28 s over 300 games, $0, no network) — the protocol this task mirrors; audits/audit-phase-20-baseline-7.md §6.1 (THE OWNER'S ADOPTION RULING, 2026-08-26: the decision rule "STANDS AS FINDING — bars 1 and 2 missed as measured, nothing is re-priced", and separately, by explicit owner prerogative, baseline 7 is adopted as canon) and §3 bars 1 and 2 (non-direct accuracy 61/103 = 0.5922 against >= 0.60, innocent ejections 42 against < 35 — the two missed bars whose successors the pre-registration will write from this memo's cells). Anchors re-verified at HEAD `4002f19b` by direct read: orchestrator/replay.py:524-546 (`_RETIRED_ALWAYS_ON_LEVERS`, twenty-one keys), :568-570 (`_TOGGLEABLE_LEVER_RESOLVERS` — ONE live toggle at HEAD, `impostor_roll_call`), :578-580 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS`), :585-588 (`SUBSTRATE_FLAG_KEYS`), :591 (`substrate_flag_snapshot`, the threaded-`env` seam), :617 (`env_var_for_lever`), :651 (`substrate_slate_mismatches`), :713 (`fold_meeting_outcome_into_memories`); meetings/manager.py:1776-1779 and :1831 (`reporter_id` derived at meeting scope and passed to the vote prompt and to nothing else), :3768 (`derive_reported_testimony` — the register's :3822-3875 loop anchors sit inside this function); meetings/schemas.py:539-541 (`ReportedStatementKind`, five members); agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:171-175 (the only home of the exculpation block); meetings/transcript.py:1490-1500 (`detect_contradictions` — NOTE: it no longer carries the `env` keyword the Phase-20 counterfactual toggled; that seam was deleted at the graduation sweep, so the Wave-2 levers supply their own); eval/evidence_honesty.py:861 (`compute_evidence_honesty`, a DIRECTORY argument and no lever-slate parameter — the 20.34 anchor :850 has drifted), :719-737 (`RenderBudgetCells`), :293 (`CELL_DEFINITIONS`); eval/solvability.py:395 (`compute_solvability_report`); eval/deduction_metrics.py:1120 (`EjecteeProofCrossTab`), :852 (`_wilson_interval`), :2350-2351 region (`player_visible_leak_turns`, the partner net only); eval/replay_walk.py:366 (`walk_replay`); api/replay_loader.py:697 (`ReplayLoader`); agents/memory/store.py:575-588 (`record_alibi`, fed by `alibi` statements only); tests/eval/test_deduction_metrics.py:158, :179, :265, :271, :307, :313 (the committed non-direct and innocent-ejection pins the re-record re-derives); scripts/counterfactual_phase20.py:1-56 and tests/scripts/test_counterfactual_phase20.py:1-92 (the precedent AND its epilogue: the script now REFUSES to run because its eight levers graduated, with `_assert_ambient_slate_is_off` as the guard and a planted case proving the guard bites); tests/scripts/conftest.py:1-18 (bare-module import of `scripts/`).
**Complexity:** Medium
**Record impact:** none
**Measurement:** `uv run python scripts/counterfactual_phase21.py --sets all` completes offline at $0 in under 10 minutes over the four sets the re-record committed and prints an OFF/ON table whose every cell equals the corresponding row of `audits/audit-phase-21-counterfactual.md`; the OFF column equals the record audit's committed cells and the committed instrument pins cell for cell; `uv run pytest tests/scripts/test_counterfactual_phase21.py -q` green; `uv run python scripts/check_doc_facts.py` green with the memo indexed.

The Wave-2 levers are three prompt-and-memory changes aimed at the largest recorded injustice
class in the project's history, and they will be measured by a ~23-hour operator event that can
be run once. The pre-registration comes next and will write bars from committed cells; this memo
is what those cells are drawn from, and it is published FIRST on purpose. Phase 20 ran the two in
the other order — its counterfactual predicted against bars the owner had already ratified
(audits/audit-phase-20-counterfactual.md §0). Here the order is inverted, and the inversion
carries one hazard that this contract rules on explicitly: a memo that publishes predicted values
and then proposes bars would be setting a bar to a number it has already seen. **This memo
therefore states measurements and predictions and writes no bar, no target and no decision rule.**
Those are the pre-registration's, and the owner's.

What the instrument can see is narrower here than in Phase 20, and saying so precisely is most of
the work. The Phase-20 slate was five render levers and three DETECTOR levers, so a large part of
its table was flags that stop being minted — a pure function of recorded testimony and each
speaker's own records, computable to the digit. The Wave-2 slate mints no flag. Threading the
reporter's identity into the accusation round changes what the model READS; whether an accuser
then withholds an accusation is a fact about the model, not about the bytes. So the honest
offline column for these levers is the RENDERED SURFACE and the EXPOSED POPULATION: how many
prompts gain the block, in how many meetings, at what cost against the render budget, over how
many recorded ballots of the shape the lever re-renders. 20.34 wrote "a flag that stops being
minted is not a vote that changes"; the Phase-21 form is stronger and the memo leads with it — a
sentence added to a prompt is not a vote that changes. Everything downstream of new model
behaviour is named in the not-predictable-offline section with its reason, and the reporter-
conviction count is the first name on that list.

Concretely, and this is the table's skeleton. The reporter lever's offline column is a prompt
census: the accusation-round prompt classes that gain the reporter context, against the record's
own denominators — on the prior-record bytes 3,312 ballot prompts carried the exculpation block
and 0 of 2,694 non-reporter speech prompts carried any structured statement that a body had been
reported, with the reporter accused after their only turn in 508 of 618 body-report meetings
(A-5). Its exposure rows are the reporter class of the ledger and the co-discoverer population,
the latter always printed beside the cell that got A-38's widening rejected: 51 of 140
co-discoverer slots are impostors. The corroboration lever's offline column is a ballot census over
the ejecting ballots — citation channel, sole-source chain and follower count, stated confidence
split by flag status, and the impossibility-charge population — against the prior-record shape of
79 hearsay / 40 own-observation / 26 own-turn / 0 uncited out of 145, with 37 of 42 ejectees
carrying no contradiction flag at all (A-10). The testimony lever is the one with a genuine
non-render offline column: the ingest widening is a countable number of episodic rows and a
countable change in the alibi-map fill rate (2,269 whereabouts and 1,160 saw-move statements
dropped today, the alibi map fed by 706 of 2,975 location accounts — B-7, whose verifier adds
that completed-task and found-body observations fall through the same reduction), plus the
confession net's OFF value with the disambiguation step A-16's verifier required, since the raw
net is 20% precise on the player-visible surface.

That is not a weak instrument, because the render-side prediction is falsifiable EARLY. Every
ON-column render cell this memo publishes is checkable on the Wave-2 smoke's first seed without
spending the record: if the memo predicts the reporter block renders in N accusation-round prompts
per body-report meeting and the smoke's ON seed renders it in zero, the lever did not thread and
the record must not start. The memo publishes those cells in exactly that form — per-meeting,
per-prompt-class, with denominators — so the smoke report can be read straight against it and the
pre-registration can convert any of them into a STOP condition it chooses to ratify.

The population all three levers are scored against is the injustice ledger. A-10 is a per-case
classification of every innocent ejection in the record, and its verifier note says what it is
for: "an acceptance-test artifact ... it should be scheduled with the levers it scores"
(collated-findings.md:1338). This memo recomputes that ledger on the re-recorded bytes and joins
each lever's exposure onto it. Two disciplines bind the join. First, exposure is an upper bound on
effect and is printed as such: a meeting the lever touches is not a meeting the lever fixes, and no
row of this memo may read as a predicted flip. Second, the ledger's tags split into two kinds and
the memo labels every one of them. The structural tags — ejectee equals the meeting's trigger
actor; the turn-1 reply accuses the turn-0 speaker; a living impostor voted for the ejectee; three
or fewer ballots; a contradiction naming the ejectee; a guard-redirected convicting ballot — are
exact joins over recorded fields and reproduce digit for digit. The impossible-transit tag is a
regex over ballot prose, and the verifier ruled on it: "PIT is a judgement net in both readings and
should be quoted as such" (:1298) — two independently written classifiers agreed on the total of 17
while disagreeing on two rows that cancelled. So the regex is committed in the script, the tagged
rows are listed by set/seed/meeting/victim in the memo, and the cell is labelled a judgment net
wherever it appears. Third, the two 4p1i sets are advisory throughout: they carried one innocent
ejection each on the prior record, so a per-set exposure cell there moves a whole step per case and
cannot carry a reading in either direction. The memo labels those rows advisory at the recorded
denominator rather than dropping them, the convention the Phase-20 memo's own rare-event rule set
(audits/audit-phase-20-counterfactual.md §4.1).

Four verifier corrections BIND this memo's prose and are the difference between a table and a
misleading table. A-12's "provably false every time" does not survive: the test performed — the
ejectee's reconstructed route is map-legal and they never vented — is true by construction for
every crewmate in every game, so 17/17 carries no information and the memo states the charge as
"asserts a physical impossibility about a player who could not have performed one", with the
enrichment quoted inside the no-vent-flag stratum (15/19 = 78.9% against a 42/103 = 40.8% base) and
never pooled. A-11's "0 of 387 impostor ejections" is a tautology — the opener is the trigger actor
in 668/668 meetings and the trigger actor is a crewmate in 668/668 — so the memo quotes the
boomerang at 29/492 = 5.9% overall and 29/271 = 10.7% within the no-vent-flag half, never as
destiny. A-19's "turn >= 2 is pure noise" is refuted by its own decomposition: same-target turn->=2
crew accusations hit 79.2% and 88.5% while different-target ones hit 4.7% and 3.1%, so agreement
with the opener is the strongest soft signal in the corpus and the memo must not repeat the
withdrawn advice to down-weight it. And A-38's widening was rejected on measurement, not taste: 51
of the 140 non-reporter co-discoverer slots (36.4%) are impostors, so any lever that extends
exculpatory framing beyond the report action hands it to an impostor in over a third of cases —
the memo prints that cell as the over-damping exposure beside every co-discoverer row.

The last thing the memo owes its reader is a durability note, and the tree supplies the evidence.
`scripts/counterfactual_phase20.py` cannot run any more: its eight levers graduated at the record
that adopted them, a graduated resolver ignores the `env` argument, and its OFF column would
silently BE its ON column — so the script refuses to start and
`tests/scripts/test_counterfactual_phase20.py` pins the refusal with a planted case
(`_assert_ambient_slate_is_off`). This task inherits that guard on day one rather than after the
fact: the Phase-21 script asserts every lever it prices is still live in
`orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS` and reads OFF under an empty environment, and
refuses with a message naming the graduation and where its ruling lives otherwise. The memo it
produces outlives the instrument, which is the point of publishing before the record.

Context for every number below: the register figures were measured on the baseline-7 committed
bytes, and baseline 7 is canon by explicit owner override of a FINDING verdict — bars 1 and 2
missed as measured and nothing was re-priced (audits/audit-phase-20-baseline-7.md §6.1). Those
bytes are replaced by the re-record before this task runs, so every figure quoted here is prior-
record CONTEXT and every cell the script prints is recomputed on the new bytes. The script asserts
its OFF column against the record audit's committed cells and fails loud on a disagreement rather
than publishing a number nobody can trace.

Nothing here changes production behaviour: the script reads committed bytes, toggles resolvers
through their `env` parameters, writes no replay, calls no model, and mutates no process
environment.

**Files in scope:**
- scripts/counterfactual_phase21.py; (new — runs the committed instruments and the render/ingest folds over all four re-recorded sets under a chosen lever slate, OFF as the record's own substrate and ON as the whole Wave-2 slate, and emits the before/after table plus `--json`)
- tests/scripts/test_counterfactual_phase21.py; (new — the CLI contract, the OFF-equals-committed-cells property, the live-slate guard with its planted case, the environment-purity assertion, and the memo-matches-the-script doc-fact check)
- audits/audit-phase-21-counterfactual.md; (new — the memo: the per-lever OFF/ON tables, the injustice-ledger join with exposure printed as an upper bound, the cells that CANNOT be predicted offline with their reasons, and the tripwire candidates offered to the pre-registration)

**Files NOT in scope:**
- meetings/manager.py, meetings/transcript.py, meetings/schemas.py, agents/memory/store.py, agents/strategic/prompts/ and every other Wave-2 lever home (read-only here — the mechanisms froze when their tasks merged; this task toggles them, never edits them, and a defect found here routes to a named fix task rather than being patched inside the counterfactual)
- orchestrator/replay.py (the registry is imported and read; registration belongs to each lever's own task)
- eval/evidence_honesty.py, eval/solvability.py, eval/deduction_metrics.py, eval/watchability.py, eval/vote_correctness.py, training/ (the instruments are IMPORTED, never re-implemented — no instrument cell may be born in this script; a cell this script needs and the instruments lack is a finding to route. Verified at HEAD: `compute_evidence_honesty(sample_dir, *, impostor_policy, assert_recorded_action_fidelity)` at eval/evidence_honesty.py:861 and `compute_solvability_report(sample_dir)` at eval/solvability.py:395 take a DIRECTORY and expose no lever-slate parameter, which is exactly why the RECORDED-OFF / RECONSTRUCTED-OFF split below exists and is not a defect to route. The injustice ledger is not an instrument cell: it is a join over recorded fields plus one declared judgment regex, and it lives in this script until a task that owns a gauge asks for it)
- scripts/counterfactual_phase20.py, tests/scripts/test_counterfactual_phase20.py, audits/audit-phase-20-counterfactual.md (the Phase-20 instrument and its memo are frozen history; its refusal path is READ as the precedent for this script's guard and never edited, and its memo is never amended)
- replays/ (nothing records and no byte moves; the frozen record is the substrate the whole method depends on holding still)
- audits/audit-phase-21-rerecord.md (the record audit is the OFF column's source of truth; this memo reads against it and may only add a dated erratum, never a re-derivation)
- audits/README.md and docs/artifacts.md (the memo needs exactly ONE index row or `check_doc_facts.check_audits_index` fails and `tests/scripts/test_check_doc_facts.py::test_committed_front_door_passes` turns red, and landing a file moves the `docs/artifacts.md` `audits/` row's count — but every audit-landing task in this phase touches the same two files, so both ride this PR as the standing index amendment in the 20.34 precedent's shape rather than being claimed as scope entries; both counts are re-read at implementation time, never hard-pinned)
- audits/audit-phase-21-preregistration.md and the Wave-2 smoke report (they do not exist yet and are downstream of this memo by the DAG; this task may not pre-empt either by writing a bar or a STOP condition into its own document)
- scripts/refresh_samples.sh, scripts/record_ml_corpus.sh, scripts/validity_gate.py (the recorders and the record's gates are the operator tasks' surface; this task spends no provider call and starts no recording)
- scripts/check.sh (the full `--sets all` run is a manual pre-record command, not a gate leg; the fast pins run under pytest)

**Definition of done:**
- [ ] `uv run python scripts/counterfactual_phase21.py --sets all` prints, per set and pooled and each with numerator and denominator, the OFF and ON readings of every cell the instruments and the recorded bytes can supply offline: for the reporter lever, the accusation-round prompt classes that gain the reporter context (reporter openings, non-reporter speech turns, per body-report meeting) and the meetings where the reporter is accused after their only turn; for the corroboration lever, the citation mix of the ejecting ballots (hearsay / own-observation / own-turn / uncited), the sole-source chains with their follower counts, the stated-confidence distribution of ejecting ballots split by flag status, and the impossibility-charge population; for the testimony lever, the reported-statement census by kind, the episodic rows the widened ingest would add, the alibi-map fill rate, the laundered saw_vent join, and the confession net with its disambiguation step; and for all three, the render-budget cells (`rendered_lines_mean`, testimony rows by living bucket) imported from `eval.evidence_honesty`.
- [ ] The OFF column is proven to BE the committed record before any ON number is believed: every OFF cell equals the corresponding cell of `audits/audit-phase-21-rerecord.md` and of the committed instrument pins (the non-direct and innocent-ejection cells at tests/eval/test_deduction_metrics.py:158, :179, :265, :271, :307, :313), asserted in `tests/scripts/test_counterfactual_phase21.py` rather than eyeballed in the memo. A disagreement is a defect in this script, not a finding about the bytes, and the failure message says so and names both readings.
- [ ] Reconstruction fidelity is asserted, not assumed: the script separates RECORDED-OFF (an instrument reading the committed bytes) from RECONSTRUCTED-OFF (the same cell folded from re-derived inputs with the whole slate OFF) and refuses to print an ON value for any cell whose two OFF readings disagree, printing the RECORDED value with the disagreement named instead.
- [ ] The live-slate guard bites before any number is printed: the script asserts every lever it prices is present in `orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS` and reads False under an empty environment, and otherwise refuses with a message naming each graduated lever, its `AILIBI_*` variable and the ruling that graduated it — the shape `scripts/counterfactual_phase20.py::_assert_ambient_slate_is_off` now uses. A planted case in the tests points the guard at an already-graduated key and proves the refusal fires, and a second points it at the live toggle and proves it passes.
- [ ] The slate is toggled ONLY through each resolver's `env` parameter: the script never assigns to `os.environ`, never writes a replay and never calls a model. A test asserts the process environment is byte-identical before and after a full run and that `substrate_flag_snapshot()` read from the ambient process still reports every Wave-2 key False after the run completes.
- [ ] The injustice ledger is recomputed on the re-recorded bytes and published as the shared population, with each row carrying its structural tags and, separately labelled, the judgment tag: the impossibility regex is committed in the script, the rows it tags are listed by set/seed/meeting/victim in the memo, and the cell is named a judgment net wherever it is quoted — the verifier's ruling at collated-findings.md:1298, executed rather than paraphrased. The guard-redirect tag reads the structured provenance field the record now carries, never a marker string.
- [ ] Exposure is printed as an upper bound and never as a predicted flip: for each lever and each ledger class, the memo states how many cases the lever's rendered surface reaches, and states in one sentence per lever that a case the lever touches is not a case the lever fixes. No row of the memo subtracts an exposure count from an injustice count.
- [ ] Lever interaction is reported rather than summed: the ON column is one shipping slate, and for each cell the memo states either the leave-one-out attribution the script computed (a `--withhold LEVER` leg, the flag the Phase-20 script already carries) or an explicit declination with its reason. The three levers overlap on the same meetings by construction — the reporter class, the hearsay class and the testimony class all sit inside the same ledger — so the memo shows the overlap as a join, not as three additive censuses.
- [ ] The render budget is priced as a first-class risk, not a footnote: the memo states the OFF and ON `rendered_lines_mean` and the testimony-row retention by living bucket, and names what the ON slate displaces if the budget binds — three levers each adding prose to the same snapshot is the one interaction that can make an ON arm strictly worse.
- [ ] `audits/audit-phase-21-counterfactual.md` names every cell it CANNOT predict offline with its reason — at minimum the reporter-conviction count, the non-direct conviction accuracy, the innocent-ejection count, the stated-confidence response to any anchoring rule, whether crew stop laundering witnessed kills into saw_vent rows, and the win split — and states in one sentence that a sentence added to a prompt is not a vote that changes.
- [ ] Small denominators are labelled, not laundered: every per-set cell whose recorded denominator is small enough that one case moves it by more than the difference the memo is discussing is printed with an advisory label and takes no part in any directional statement — the two 4p1i sets in particular, which carried one innocent ejection each on the prior record.
- [ ] The memo writes NO bar, NO target and NO decision rule, and says so in its opening status line: it publishes measurements and predictions for the pre-registration to read, and offers tripwire CANDIDATES (cells whose predicted value is exactly zero or exactly the full population, so a smoke seed can falsify them at n=1) explicitly labelled as candidates the owner may ratify, decline or replace.
- [ ] Every ON-side render prediction is stated in a form the Wave-2 smoke can check on one seed — per meeting and per prompt class, with its denominator — and the memo says which cells the smoke can falsify and which need the full record.
- [ ] The run is bounded and reproducible: `--sets all` completes in under 10 minutes over the four committed sets from a fresh clone (the wall time recorded in the PR Summary, against the 28 s the Phase-20 instrument took over 300 games), needs no network and no `AILIBI_*` export from the operator, and `--json` emits the same table machine-readably for the pre-registration and the record audit to consume.
- [ ] `tests/scripts/test_counterfactual_phase21.py` pins the CLI contract on a small committed slice fast enough for the default tier, asserts the memo's table equals the script's output so the document cannot drift from the instrument, and pins the no-bar discipline this task's inverted position in the DAG requires: the memo carries its explicit no-bar status line, and no line of it attaches a threshold to a Wave-2 cell. Both pins ship with a perturbed copy of the memo proving they bite, in the `doc_tree` fixture style `tests/scripts/test_check_doc_facts.py` already uses.
- [ ] The memo is committed before the pre-registration is authored — the DAG enforces the order — and the PR Summary carries the headline exposure sentence and the "what this cannot predict" sentence side by side, so neither is read without the other.
- [ ] `uv run python scripts/check_doc_facts.py` passes with the memo indexed: `audits/README.md` gains exactly one row for it, recorded in the PR as a scope amendment in the 20.34 precedent's shape (the file is contended by every record-audit task in this phase, so it is deliberately not claimed as a scope entry).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — read the three lever contracts and the record audit before writing a line of the script.
The cell list is not yours to invent: it is what the three levers actually render plus what the
record audit committed. Anything this script prints that no lever renders and no instrument owns is
scope creep; anything a lever renders that this script cannot price is a line in the
"cannot predict offline" section, never a silent omission. Read
`audits/audit-phase-20-counterfactual.md` §7 and §8 for the shape of both of those sections — they
are the parts of that memo worth copying.

Step 2 — one walk, two slates. Reconstruct each game ONCE (`eval.replay_walk.walk_replay` at
eval/replay_walk.py:366 for the typed per-tick events, `api.replay_loader.ReplayLoader` at
api/replay_loader.py:697 for the served meeting views), then evaluate both slates from the same
reconstruction. Reconstructing twice doubles the runtime for no signal and invites the two passes to
diverge. Fold each meeting's outcome into the rebuilt memories through
`orchestrator.replay.fold_meeting_outcome_into_memories` (orchestrator/replay.py:713), the shared
helper the replay-loader walk, the byte-golden walk and the evidence-honesty walk already route
through, so the fold is identical in all four places.

Step 3 — toggle by argument, never by environment. Build one frozen mapping per slate —
`{env_var_for_lever(key): "1" for key in WAVE_2_LEVERS}` for ON and `{}` for OFF — and thread it
into each resolver's `env` parameter the way `orchestrator.replay.substrate_flag_snapshot`
(orchestrator/replay.py:591) already threads it. Note the seam has moved since Phase 20:
`meetings.transcript.detect_contradictions` (meetings/transcript.py:1490) no longer takes an `env`
keyword — that parameter was deleted when the Phase-20 levers graduated — so read each Wave-2
lever's own resolver signature from its home module rather than assuming the old call shape. Assert
the ambient snapshot is all-False at process start and again at exit; a monkeypatched `os.environ`
would make the memo unreproducible for anyone with a stale export.

Step 4 — the render cells are a diff of rendered bytes, not a metric of behaviour. For a prompt
lever the ON reading is a second render of the same rebuilt memory and the same meeting inputs with
the lever ON, compared line for line against the OFF render. Count what appears, what disappears and
what is displaced by the token budget (`agents.memory.store.DEFAULT_TOKEN_BUDGET`), and print the
render-budget cells from `eval.evidence_honesty.RenderBudgetCells` (eval/evidence_honesty.py:719)
rather than defining a second notion of "a rendered row". Name each prompt class the way the record
does — reporter opening, non-reporter speech turn, ballot — so the smoke can join on it.

Step 5 — the ledger is a join, not a new metric. Take every innocent ejection from the committed
`EjecteeProofCrossTab` partition (eval/deduction_metrics.py:1120), key each by (set, seed, meeting),
and attach the structural tags from recorded fields only: trigger actor, turn-0 and turn-1 speakers
and their accusation claims, the ballot list and its size, roles re-derived by re-seeding, the
recorded contradictions naming the ejectee, and the guard-redirect provenance field. Cross-check the
enumeration's total against the record audit's own innocent-ejection cells before printing anything
and fail loud on a mismatch. Keep the impossibility regex in one named constant with the verifier's
"judgement net" ruling in its docstring, and emit the tagged rows so a reader can re-judge them.

Step 6 — write the memo as a falsifiable publication, not a summary. Measured value, denominator,
and the prompt class or ledger class it belongs to, one row each; then the not-predictable-offline
section with one clause of reason apiece; then the per-lever table; then the tripwire candidates.
State at the top, in the status line, that this memo precedes the pre-registration and therefore
writes no bar — and state in the same place that its numbers are recomputed on the re-recorded
bytes, with the register's prior-record figures quoted only as context. Where a register number was
corrected by its verifier, quote the corrected form and nothing else.

Step 7 — the guard first, the table second. Write `_assert_live_slate` and its two planted cases
before the folds, and watch the refusal fire: the Phase-20 script is the standing proof that a
counterfactual whose levers have graduated prints an OFF column that is silently the ON column, and
the only reason that failure is legible today is that someone turned it into a refusal with a test.
Yours costs fifteen lines now and is the difference between a memo and a memo nobody can trust.

## Public types this task introduces
- `counterfactual_phase21.WAVE_2_LEVERS`
- `counterfactual_phase21.LeverExposureCensus`
- `counterfactual_phase21.InjusticeLedgerRow`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import orchestrator.game"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import meetings.corroboration"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import orchestrator.game.TacticalAgent"`
- `uv run python -c "import eval.reporter_justice"`
- `uv run python -c "import training.rewards"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import engine.tick"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.vj_instruments"`
- `uv run python -c "import eval.vj_instruments.VJInstrumentReport"`
- `uv run python -c "import eval.vj_instruments.VJMeetingRow"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import frontend/src/lib/contradictions"`
- `uv run python -c "import check_doc_facts"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-21-counterfactual` with a title like `task 21.21: the offline counterfactual: the wave-2 levers over the re-recorded bytes, published before any bar is written`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing A-10 [ADJUSTED, P1] — audits/review-2026-08-26/A/collated-findings.md:1138-1344 (the 42-row innocent-ejection ledger and its class totals RC 30 / BOOM 29 / PIT 17 / IMP-RIDES 33 / WEAKFLAG 5 / REDIRECT 4 / ENDGAME 5, reproduced row for row by the verifier at :1291-1298 including every vote tally; the citation mix of the 145 ejecting ballots hearsay 79 / own_obs 40 / own_turn 26 / other_obs 0 / none 0 at :1300-1303; 37 of 42 ejectees carried no contradiction flag at all; the verifier's TWO binding corrections at :1143 and :1332-1335 — "only 4 of the 42" is wrong on the finding's own ledger (six rows carry nothing beyond IMP-RIDES and/or PIT, of which three are PIT, so the pure-herd set is the THREE rows C9 1008:m2, C9 1066:m0, C9 1106:m3) and two supporting cells drift by one under a different tie-break (pile-driver CREW 27 filed vs 28 measured, IMP-RIDES pivotal 14 filed vs 13 measured), and its ruling at :1298 that "PIT is a judgement net in both readings and should be quoted as such"; the verifier note at :1338 that this ledger "is an acceptance-test artifact ... and should be scheduled with the levers it scores"); A-4 [ADJUSTED, P1] :431-612 (30 of 42 innocent ejections eject the meeting's own reporter; 618 body-report meetings of 668, 50 emergency; reporter_is_impostor 0/618; reporter ejected 30/618 = 4.85% against innocent non-reporter 12/1844 = 0.65%, RR 7.46x, z=6.98; 28 of the 30 convictions carry NO contradiction naming the reporter; pooled ejection accuracy 387/429 = 90.2%; the verifier's correction that the reporter's ejectability is a RECORDED design decision, not an oversight, and that the channel is down ~2.6x from baseline 2); A-5 [ADJUSTED, P1] :614-691 (3312/3312 ballot prompts carry the exculpation block, 0/2694 non-reporter speech prompts carry any structured statement that a body was reported; turns-per-speaker histogram {1: 3312}; reporter turn kinds {opening: 618}; accusations against the reporter by turn index summing to 1061, all at index >= 1; 508/618 meetings accuse the reporter after their only turn; the verifier's framing correction that the load-bearing anchor is `grep -c reporter` = 0 in all five non-ballot templates against 5 in vote_ballot.j2, NOT the memory census); A-24 [ADJUSTED, P2] :2901-2954 (impostor accusations at the reporter 521/737 = 70.7% against crew 540/1513 = 35.7%; the verifier's correction that the ~2x ratio is a STANDING pattern — 64.2% baseline-6 vs 65.9% baseline-7 like-for-like — and that what is new and adverse is the BALLOT-side regression, reporter-directed ballots 2.2% -> 9.6% crew and 4.1% -> 17.1% impostor on the same seeds); A-37 [ADJUSTED, P3] :3950-4004 (the exculpation is almost never argued: ~28 rationales co-mention with an exculpatory hinge and ~19-20 genuinely argue it, against the filed "16 co-mentions, ~5 genuine"; at least one reporter DOES invoke it at ballot time; the "generic under-gate redirect is what bites" attribution is a mis-attribution that omits the soft-lift cap); A-38 [ADJUSTED, P3, fix_sketch REJECTED] :4006-4052 (121/618 meetings carry a non-reporter with the identical discovery line; innocent co-discoverers ejected 3/89 = 3.37% vs 9/1755 = 0.51%, Fisher p=0.017; and the reason the widening was rejected — 51 of the 140 non-reporter co-discoverer slots, 36.4%, are IMPOSTORS); A-11 [ADJUSTED, P2] :1346-1447 (the boomerang convicts the opener in 29 of 42, but the verifier DROPS the "0 of 387 impostor ejections" contrast as a tautology — the opener is the trigger actor in 668/668 and the trigger actor is a crewmate in 668/668 — and re-prices the shape at 29/492 = 5.9% overall, 29/271 = 10.7% inside the no-vent-flag half against 1/71 = 1.4% without it); A-12 [ADJUSTED, P1] :1449-1566 (>= 1 impossibility-asserting convicting ballot in 17 of 42, >= half in 15 of 42 = 35.7%; the map card renders in every meeting call; the verifier REPLACES "provably false every time" — the test performed is true by construction for every crewmate — and re-prices the enrichment inside the no-vent-flag stratum at 15/19 = 78.9% against a 42/103 = 40.8% base = 1.9x); A-19 [ADJUSTED, P2] :2252-2343 (the verifier REFUTES the "turn >= 2 is pure noise" headline by a decomposition the filing never ran: turn >= 2 crew accusations naming the SAME target as turn 0 hit 79.2% (n=48) and 88.5% (n=122), different-target 4.7% (n=106) and 3.1% (n=287); the pooled lift is a mixture artifact; the turn-1 row conditions on the opener having been wrong; and the ML advice "down-weight turn >= 2 soft accusations" is WITHDRAWN); B-7 [CONFIRMED, P1] — audits/review-2026-08-26/B/collated-findings.md:565-624 (WhereaboutsClaim 2,269 and SawMoveObservation 1,160 never reach a listener's memory; the verifier's own census over 476 corpus meetings reproduces the table exactly and adds that CompletedTaskObservation 310 and FoundBodyObservation 586 also fall through, so the gap is four shapes; alibi_map fed by 706 of 2,975 location accounts = 23.7%; the precision note that whereabouts DO still move suspicion through the scalar channel); A-22 [ADJUSTED, P3] audits/review-2026-08-26/A/collated-findings.md:2610-2793 (5 of 517 spoken saw_vent rows name a subject who never vented, all 5 joining that speaker's own witnessed kill on killer+room+tick; 448/448 vent_sighting contradictions engine-backed; the verifier's bound that all 5 named a real IMPOSTOR and all 5 meetings ejected that impostor, so the damage is legibility only, and that "65 ungrounded saw_vent rows" is an inflated denominator); A-16 [ADJUSTED, P2] :2006-2084 (the instrument half stands: the self-kill and role nets never run over the player-visible surface; the gameplay inference is corrected — both confessors were ejected in the meeting they confessed in; and the fix is conditioned: the raw net fires 10 times player-visible, 4 IMPOSTOR / 6 CREWMATE, only 2 genuine = 20% precision overall, 50% within impostor speakers, so it ships only with a disambiguation step against the ground-truth kill record); A-3 :242-429 (the ~120 guard-redirected ballots, 25 flipped meeting outcomes, 3 ejections nobody voted for — the REDIRECT class of the ledger, and the reason this script reads a structured provenance field rather than parsing a marker string); audits/audit-phase-20-counterfactual.md §0-§3 (the headline-then-baseline discipline), §4.1 (per-row reading rules), §7 (the cells no offline instrument can reach), §8 (per-lever predictions with leave-one-out attribution), §9 (abandon criteria), §11 (reproduction; 28 s over 300 games, $0, no network) — the protocol this task mirrors; audits/audit-phase-20-baseline-7.md §6.1 (THE OWNER'S ADOPTION RULING, 2026-08-26: the decision rule "STANDS AS FINDING — bars 1 and 2 missed as measured, nothing is re-priced", and separately, by explicit owner prerogative, baseline 7 is adopted as canon) and §3 bars 1 and 2 (non-direct accuracy 61/103 = 0.5922 against >= 0.60, innocent ejections 42 against < 35 — the two missed bars whose successors the pre-registration will write from this memo's cells). Anchors re-verified at HEAD `4002f19b` by direct read: orchestrator/replay.py:524-546 (`_RETIRED_ALWAYS_ON_LEVERS`, twenty-one keys), :568-570 (`_TOGGLEABLE_LEVER_RESOLVERS` — ONE live toggle at HEAD, `impostor_roll_call`), :578-580 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS`), :585-588 (`SUBSTRATE_FLAG_KEYS`), :591 (`substrate_flag_snapshot`, the threaded-`env` seam), :617 (`env_var_for_lever`), :651 (`substrate_slate_mismatches`), :713 (`fold_meeting_outcome_into_memories`); meetings/manager.py:1776-1779 and :1831 (`reporter_id` derived at meeting scope and passed to the vote prompt and to nothing else), :3768 (`derive_reported_testimony` — the register's :3822-3875 loop anchors sit inside this function); meetings/schemas.py:539-541 (`ReportedStatementKind`, five members); agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:171-175 (the only home of the exculpation block); meetings/transcript.py:1490-1500 (`detect_contradictions` — NOTE: it no longer carries the `env` keyword the Phase-20 counterfactual toggled; that seam was deleted at the graduation sweep, so the Wave-2 levers supply their own); eval/evidence_honesty.py:861 (`compute_evidence_honesty`, a DIRECTORY argument and no lever-slate parameter — the 20.34 anchor :850 has drifted), :719-737 (`RenderBudgetCells`), :293 (`CELL_DEFINITIONS`); eval/solvability.py:395 (`compute_solvability_report`); eval/deduction_metrics.py:1120 (`EjecteeProofCrossTab`), :852 (`_wilson_interval`), :2350-2351 region (`player_visible_leak_turns`, the partner net only); eval/replay_walk.py:366 (`walk_replay`); api/replay_loader.py:697 (`ReplayLoader`); agents/memory/store.py:575-588 (`record_alibi`, fed by `alibi` statements only); tests/eval/test_deduction_metrics.py:158, :179, :265, :271, :307, :313 (the committed non-direct and innocent-ejection pins the re-record re-derives); scripts/counterfactual_phase20.py:1-56 and tests/scripts/test_counterfactual_phase20.py:1-92 (the precedent AND its epilogue: the script now REFUSES to run because its eight levers graduated, with `_assert_ambient_slate_is_off` as the guard and a planted case proving the guard bites); tests/scripts/conftest.py:1-18 (bare-module import of `scripts/`).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
