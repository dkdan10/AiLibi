# The process scorecard

**Role-correctness is REPORTED and is NOT a gate. The owner accepted decision D1 of tasks/direction-2026-09-19-process-over-outcome.md section 10 on 2026-09-19: the process suite is the headline, role-correctness is a reported cell beside it, and the preregistered supported_correct_ejection outcome stops being the project's gate. Nothing in this scorecard, and nothing any card derived from it gates on, pushes an agent toward the correct answer: a wrong decision on believable data is the game working, and it is counted in row 8, never penalised.**

Nine measures of whether a decision rested on data the agent actually held, computed with **zero model calls** from recordings already in the tree. The suite is [the direction of 2026-09-19](../tasks/direction-2026-09-19-process-over-outcome.md) section 8; the card that publishes it is [the process scorecard card](../tasks/work/process-scorecard.md). Every row's definition — numerator, denominator, non-coverage — is published beside the number here and as typed keys in [`process-scorecard.json`](process-scorecard.json).

This page is GENERATED. Do not edit it by hand: run `uv run python scripts/publish_process_scorecard.py` and commit the result. `uv run python scripts/publish_process_scorecard.py --check` recomputes both files from the recordings and fails on drift.

## Why rows 2 and 3 are the point

Without **argmax-independence** the headline certifies an arithmetic aggregator as a reasoner: on the shipped corpus most crew EJECT ballots simply name the voter's own rendered suspicion argmax, and every departing ballot still carries a valid citation — so a "cited and on-target" measure scores the two alike. Without the **manufactured-contradiction rate** it certifies the seed-41 failure: the alibi schema compresses a truthfully-moving player into a single-room envelope, the detectors flag the envelope, and a right-looking process convicts an innocent on evidence the schema invented.

## Recording provenance

These four sets are one era — the committed bytes at publication, before the substrate wave. They are labelled, never averaged across a boundary: once the grounded-SKIP card and the weighing channel land and the re-record runs, the SKIP rows move off zero and rows 2 and 9 stop being comparable across that line.

* `replays/ml_corpus/9p2i`
* `replays/samples/9p2i`
* `replays/ml_corpus/4p1i`
* `replays/samples/4p1i`

Report format version 2; scorecard schema version 1; decision date 2026-09-19.

## Pooled

### pooled: all four committed sets

300 games, 672 meetings, 3631 ballots (2146 EJECT, 1485 SKIP). Sources: `replays/ml_corpus/9p2i`, `replays/samples/9p2i`, `replays/ml_corpus/4p1i`, `replays/samples/4p1i`.

| # | row | value |
| --- | --- | --- |
| 1 | grounded-decision rate, EJECT | 2078/2146 = 0.9683 |
| 1 | grounded-decision rate, SKIP | 0/1485 = 0.0000 |
| 1 | grounded-decision rate, all ballots | 2078/3631 = 0.5723 |
| 2 | argmax-independence: deviating EJECTs | 116/1811 = 6.4% |
| 2 | argmax-independence: role-correct, followers vs deviators | 1602/1695 = 94.5% vs 9/116 = 7.8% (chance 31.6%) |
| 3 | manufactured-contradiction rate | 159/192 = 0.8281 (not evaluable 32) |
| 4 | unexplained-decision rate | 20/3631 = 0.0055 |
| 5 | evidence-quality mix | contradiction_flag 10, first_hand 75, hearsay 8, unevidenced 3, vent_flag 333 over 429 ejections |
| 6 | rationale faithfulness (TOKENS) | 2874/2874 = 1.0000 (not evaluable 757) |
| 7 | agent-authored share | 3531/3631 = 0.9725 |
| 8 | wrong-but-believable rate | 383/2146 = 0.1785 — reported, never penalised |
| 9 | role-correct ejection rate | 383/429 = 0.8928 — reported beside, never a gate |

Row 2 detail: followers 1695, deviators 116, ties excluded 111, no rendered row inside the valid-target list 0. In meetings where the engine minted no contradiction at all, role-correct: followers 233/286, deviators 2/91.

Row 3 detail: manufactured flags contradicting an account the engine route makes true at EVERY tick, 9 of 159; the rest are the span-envelope artifact proper.

Row 3 claim census: 1003 self-alibi claims (814 spanning more than one tick), 106 false under the envelope test of which 105 are multi-tick, 2 false under the strict test (in that room at NO tick the claim covers), 0 unresolvable, and 13 further alibi claims name another player and are out of the census.

Row 4 detail: EJECT ballots whose citation does not resolve, 2; SKIP ballots naming no player at all, 18 (1461 SKIPs carry considered_alternatives and 748 name a player in prose).

Row 5 detail (role-correct beside each band, gating nothing): contradiction_flag 1/10, first_hand 42/75, hearsay 4/8, unevidenced 3/3, vent_flag 333/333.

Row 6 detail: 0 of 6796 extracted tokens are absent from what the voter held.

Row 7 detail: typed guard rewrites invalid_target 4, teammate_coerced 7, uncited_coerced 6, under_gate_redirect 83; 0 unwound from a marker with no typed reason; 13 citation nulled, target intact; redirect-marker census 83 (83 EJECT, 0 coerced SKIP).

Context: impostor alibis 122/139 survived contradiction detection; reporter slots 34/620 ejected against innocent non-reporter slots 12/1859.

### pooled: the two 9p2i sets

200 games, 590 meetings, 3385 ballots (2026 EJECT, 1359 SKIP). Sources: `replays/ml_corpus/9p2i`, `replays/samples/9p2i`.

| # | row | value |
| --- | --- | --- |
| 1 | grounded-decision rate, EJECT | 1962/2026 = 0.9684 |
| 1 | grounded-decision rate, SKIP | 0/1359 = 0.0000 |
| 1 | grounded-decision rate, all ballots | 1962/3385 = 0.5796 |
| 2 | argmax-independence: deviating EJECTs | 112/1704 = 6.6% |
| 2 | argmax-independence: role-correct, followers vs deviators | 1501/1592 = 94.3% vs 9/112 = 8.0% (chance 30.4%) |
| 3 | manufactured-contradiction rate | 158/191 = 0.8272 (not evaluable 32) |
| 4 | unexplained-decision rate | 19/3385 = 0.0056 |
| 5 | evidence-quality mix | contradiction_flag 10, first_hand 69, hearsay 7, unevidenced 2, vent_flag 288 over 376 ejections |
| 6 | rationale faithfulness (TOKENS) | 2719/2719 = 1.0000 (not evaluable 666) |
| 7 | agent-authored share | 3288/3385 = 0.9713 |
| 8 | wrong-but-believable rate | 364/2026 = 0.1797 — reported, never penalised |
| 9 | role-correct ejection rate | 334/376 = 0.8883 — reported beside, never a gate |

Row 2 detail: followers 1592, deviators 112, ties excluded 111, no rendered row inside the valid-target list 0. In meetings where the engine minted no contradiction at all, role-correct: followers 222/273, deviators 2/87.

Row 3 detail: manufactured flags contradicting an account the engine route makes true at EVERY tick, 8 of 158; the rest are the span-envelope artifact proper.

Row 3 claim census: 955 self-alibi claims (769 spanning more than one tick), 104 false under the envelope test of which 103 are multi-tick, 2 false under the strict test (in that room at NO tick the claim covers), 0 unresolvable, and 13 further alibi claims name another player and are out of the census.

Row 4 detail: EJECT ballots whose citation does not resolve, 2; SKIP ballots naming no player at all, 17 (1336 SKIPs carry considered_alternatives and 710 name a player in prose).

Row 5 detail (role-correct beside each band, gating nothing): contradiction_flag 1/10, first_hand 39/69, hearsay 4/7, unevidenced 2/2, vent_flag 288/288.

Row 6 detail: 0 of 6473 extracted tokens are absent from what the voter held.

Row 7 detail: typed guard rewrites invalid_target 4, teammate_coerced 7, uncited_coerced 6, under_gate_redirect 80; 0 unwound from a marker with no typed reason; 13 citation nulled, target intact; redirect-marker census 80 (80 EJECT, 0 coerced SKIP).

Context: impostor alibis 117/134 survived contradiction detection; reporter slots 30/548 ejected against innocent non-reporter slots 12/1787.

## Per set

### ml_corpus/9p2i

150 games, 439 meetings, 2516 ballots (1499 EJECT, 1017 SKIP). Sources: `replays/ml_corpus/9p2i`.

| # | row | value |
| --- | --- | --- |
| 1 | grounded-decision rate, EJECT | 1455/1499 = 0.9706 |
| 1 | grounded-decision rate, SKIP | 0/1017 = 0.0000 |
| 1 | grounded-decision rate, all ballots | 1455/2516 = 0.5783 |
| 2 | argmax-independence: deviating EJECTs | 81/1270 = 6.4% |
| 2 | argmax-independence: role-correct, followers vs deviators | 1143/1189 = 96.1% vs 7/81 = 8.6% (chance 30.4%) |
| 3 | manufactured-contradiction rate | 105/134 = 0.7836 (not evaluable 28) |
| 4 | unexplained-decision rate | 15/2516 = 0.0060 |
| 5 | evidence-quality mix | contradiction_flag 3, first_hand 52, hearsay 4, unevidenced 2, vent_flag 220 over 281 ejections |
| 6 | rationale faithfulness (TOKENS) | 2014/2014 = 1.0000 (not evaluable 502) |
| 7 | agent-authored share | 2446/2516 = 0.9722 |
| 8 | wrong-but-believable rate | 251/1499 = 0.1674 — reported, never penalised |
| 9 | role-correct ejection rate | 252/281 = 0.8968 — reported beside, never a gate |

Row 2 detail: followers 1189, deviators 81, ties excluded 92, no rendered row inside the valid-target list 0. In meetings where the engine minted no contradiction at all, role-correct: followers 176/206, deviators 1/64.

Row 3 detail: manufactured flags contradicting an account the engine route makes true at EVERY tick, 6 of 105; the rest are the span-envelope artifact proper.

Row 3 claim census: 696 self-alibi claims (559 spanning more than one tick), 68 false under the envelope test of which 68 are multi-tick, 1 false under the strict test (in that room at NO tick the claim covers), 0 unresolvable, and 9 further alibi claims name another player and are out of the census.

Row 4 detail: EJECT ballots whose citation does not resolve, 1; SKIP ballots naming no player at all, 14 (999 SKIPs carry considered_alternatives and 524 name a player in prose).

Row 5 detail (role-correct beside each band, gating nothing): contradiction_flag 0/3, first_hand 28/52, hearsay 2/4, unevidenced 2/2, vent_flag 220/220.

Row 6 detail: 0 of 4796 extracted tokens are absent from what the voter held.

Row 7 detail: typed guard rewrites invalid_target 2, teammate_coerced 5, uncited_coerced 6, under_gate_redirect 57; 0 unwound from a marker with no typed reason; 10 citation nulled, target intact; redirect-marker census 57 (57 EJECT, 0 coerced SKIP).

Context: impostor alibis 86/97 survived contradiction detection; reporter slots 23/407 ejected against innocent non-reporter slots 6/1323.

### samples/9p2i

50 games, 151 meetings, 869 ballots (527 EJECT, 342 SKIP). Sources: `replays/samples/9p2i`.

| # | row | value |
| --- | --- | --- |
| 1 | grounded-decision rate, EJECT | 507/527 = 0.9620 |
| 1 | grounded-decision rate, SKIP | 0/342 = 0.0000 |
| 1 | grounded-decision rate, all ballots | 507/869 = 0.5834 |
| 2 | argmax-independence: deviating EJECTs | 31/434 = 7.1% |
| 2 | argmax-independence: role-correct, followers vs deviators | 358/403 = 88.8% vs 2/31 = 6.5% (chance 30.5%) |
| 3 | manufactured-contradiction rate | 53/57 = 0.9298 (not evaluable 4) |
| 4 | unexplained-decision rate | 4/869 = 0.0046 |
| 5 | evidence-quality mix | contradiction_flag 7, first_hand 17, hearsay 3, vent_flag 68 over 95 ejections |
| 6 | rationale faithfulness (TOKENS) | 705/705 = 1.0000 (not evaluable 164) |
| 7 | agent-authored share | 842/869 = 0.9689 |
| 8 | wrong-but-believable rate | 113/527 = 0.2144 — reported, never penalised |
| 9 | role-correct ejection rate | 82/95 = 0.8632 — reported beside, never a gate |

Row 2 detail: followers 403, deviators 31, ties excluded 19, no rendered row inside the valid-target list 0. In meetings where the engine minted no contradiction at all, role-correct: followers 46/67, deviators 1/23.

Row 3 detail: manufactured flags contradicting an account the engine route makes true at EVERY tick, 2 of 53; the rest are the span-envelope artifact proper.

Row 3 claim census: 259 self-alibi claims (210 spanning more than one tick), 36 false under the envelope test of which 35 are multi-tick, 1 false under the strict test (in that room at NO tick the claim covers), 0 unresolvable, and 4 further alibi claims name another player and are out of the census.

Row 4 detail: EJECT ballots whose citation does not resolve, 1; SKIP ballots naming no player at all, 3 (337 SKIPs carry considered_alternatives and 186 name a player in prose).

Row 5 detail (role-correct beside each band, gating nothing): contradiction_flag 1/7, first_hand 11/17, hearsay 2/3, vent_flag 68/68.

Row 6 detail: 0 of 1677 extracted tokens are absent from what the voter held.

Row 7 detail: typed guard rewrites invalid_target 2, teammate_coerced 2, under_gate_redirect 23; 0 unwound from a marker with no typed reason; 3 citation nulled, target intact; redirect-marker census 23 (23 EJECT, 0 coerced SKIP).

Context: impostor alibis 31/37 survived contradiction detection; reporter slots 7/141 ejected against innocent non-reporter slots 6/464.

### ml_corpus/4p1i

50 games, 43 meetings, 129 ballots (69 EJECT, 60 SKIP). Sources: `replays/ml_corpus/4p1i`.

| # | row | value |
| --- | --- | --- |
| 1 | grounded-decision rate, EJECT | 66/69 = 0.9565 |
| 1 | grounded-decision rate, SKIP | 0/60 = 0.0000 |
| 1 | grounded-decision rate, all ballots | 66/129 = 0.5116 |
| 2 | argmax-independence: deviating EJECTs | 1/60 = 1.7% |
| 2 | argmax-independence: role-correct, followers vs deviators | 59/59 = 100.0% vs 0/1 = 0.0% (chance 50.0%) |
| 3 | manufactured-contradiction rate | 1/1 = 1.0000 |
| 4 | unexplained-decision rate | 0/129 = 0.0000 |
| 5 | evidence-quality mix | first_hand 2, unevidenced 1, vent_flag 26 over 29 ejections |
| 6 | rationale faithfulness (TOKENS) | 83/83 = 1.0000 (not evaluable 46) |
| 7 | agent-authored share | 127/129 = 0.9845 |
| 8 | wrong-but-believable rate | 10/69 = 0.1449 — reported, never penalised |
| 9 | role-correct ejection rate | 29/29 = 1.0000 — reported beside, never a gate |

Row 2 detail: followers 59, deviators 1, ties excluded 0, no rendered row inside the valid-target list 0. In meetings where the engine minted no contradiction at all, role-correct: followers 7/7, deviators 0/1.

Row 3 detail: manufactured flags contradicting an account the engine route makes true at EVERY tick, 1 of 1; the rest are the span-envelope artifact proper.

Row 3 claim census: 19 self-alibi claims (19 spanning more than one tick), 0 false under the envelope test of which 0 are multi-tick, 0 false under the strict test (in that room at NO tick the claim covers), 0 unresolvable, and 0 further alibi claims name another player and are out of the census.

Row 4 detail: EJECT ballots whose citation does not resolve, 0; SKIP ballots naming no player at all, 0 (60 SKIPs carry considered_alternatives and 17 name a player in prose).

Row 5 detail (role-correct beside each band, gating nothing): first_hand 2/2, unevidenced 1/1, vent_flag 26/26.

Row 6 detail: 0 of 176 extracted tokens are absent from what the voter held.

Row 7 detail: typed guard rewrites under_gate_redirect 2; 0 unwound from a marker with no typed reason; 0 citation nulled, target intact; redirect-marker census 2 (2 EJECT, 0 coerced SKIP).

Context: impostor alibis 1/1 survived contradiction detection; reporter slots 0/36 ejected against innocent non-reporter slots 0/36.

### samples/4p1i

50 games, 39 meetings, 117 ballots (51 EJECT, 66 SKIP). Sources: `replays/samples/4p1i`.

| # | row | value |
| --- | --- | --- |
| 1 | grounded-decision rate, EJECT | 50/51 = 0.9804 |
| 1 | grounded-decision rate, SKIP | 0/66 = 0.0000 |
| 1 | grounded-decision rate, all ballots | 50/117 = 0.4274 |
| 2 | argmax-independence: deviating EJECTs | 3/47 = 6.4% |
| 2 | argmax-independence: role-correct, followers vs deviators | 42/44 = 95.5% vs 0/3 = 0.0% (chance 50.0%) |
| 3 | manufactured-contradiction rate | 0/0 = n/a |
| 4 | unexplained-decision rate | 1/117 = 0.0085 |
| 5 | evidence-quality mix | first_hand 4, hearsay 1, vent_flag 19 over 24 ejections |
| 6 | rationale faithfulness (TOKENS) | 72/72 = 1.0000 (not evaluable 45) |
| 7 | agent-authored share | 116/117 = 0.9915 |
| 8 | wrong-but-believable rate | 9/51 = 0.1765 — reported, never penalised |
| 9 | role-correct ejection rate | 20/24 = 0.8333 — reported beside, never a gate |

Row 2 detail: followers 44, deviators 3, ties excluded 0, no rendered row inside the valid-target list 0. In meetings where the engine minted no contradiction at all, role-correct: followers 4/6, deviators 0/3.

Row 3 detail: manufactured flags contradicting an account the engine route makes true at EVERY tick, 0 of 0; the rest are the span-envelope artifact proper.

Row 3 claim census: 29 self-alibi claims (26 spanning more than one tick), 2 false under the envelope test of which 2 are multi-tick, 0 false under the strict test (in that room at NO tick the claim covers), 0 unresolvable, and 0 further alibi claims name another player and are out of the census.

Row 4 detail: EJECT ballots whose citation does not resolve, 0; SKIP ballots naming no player at all, 1 (65 SKIPs carry considered_alternatives and 21 name a player in prose).

Row 5 detail (role-correct beside each band, gating nothing): first_hand 1/4, hearsay 0/1, vent_flag 19/19.

Row 6 detail: 0 of 147 extracted tokens are absent from what the voter held.

Row 7 detail: typed guard rewrites under_gate_redirect 1; 0 unwound from a marker with no typed reason; 0 citation nulled, target intact; redirect-marker census 1 (1 EJECT, 0 coerced SKIP).

Context: impostor alibis 4/4 survived contradiction detection; reporter slots 4/36 ejected against innocent non-reporter slots 0/36.

## Row definitions

**grounded_decision_rate.** Numerator: ballots whose citation RESOLVES in the voter's own inputs (primary_reason_id in this meeting's turns, or primary_reason_observation_id carried whole-token on a line of that voter's own recorded prompts) AND bears on the decision's subject by meetings.citation_relevance.citations_bear_on - the subject being the recorded target for an EJECT and any member of considered_alternatives for a SKIP. Denominator: all ballots of that decision kind. Not-evaluable: ballots whose voter has no recorded prompt in the meeting. An UNCITED ballot is not grounded: citations_bear_on is vacuously true with nothing cited, so presence and resolution are required before aboutness is asked. It does NOT measure whether the cited line was factually true.

**argmax_independence.** Over CREW EJECT ballots, comparing the RECORDED target with the argmax of that voter's own rendered suspicion rows INTERSECTED with that voter's rendered valid-ejection-target list. Numerator: the DEVIATING ballots, whose recorded target is not that argmax. Denominator: the unambiguous ballots. Ties are excluded and counted; a ballot whose voter's prompts carry no row inside the valid list is not-evaluable and counted. Roles come from the seeder, are used only to report the role-correctness of followers and deviators BESIDE the split, and gate nothing. Chance is the mean, over the SAME unambiguous ballots that form the denominator - never over the excluded ties or the not-evaluable ballots - of the living-impostor share of each voter's own rendered valid-target list. It does NOT measure whether the voter read the graph, only whether the recorded call equals the arithmetic the engine handed it.

**manufactured_contradiction_rate.** Numerator: recorded contradiction flags whose kind is an alibi class (alibi_conflict, alibi_vs_sighting, alibi_vs_physical) and whose subjects name the speaker of a SELF-alibi claim in that meeting that is TRUE at at least one tick of its own span against that speaker's engine route from a state-hash-verified walk_replay. Denominator: all alibi-class flags. Not-evaluable: an alibi-class flag naming no self-alibi speaker in its meeting, or one whose claim covers a tick the walk does not reach. Ticks are agent-frame and resolve against engine tick T - 1. It does NOT measure intent, and it does NOT clear a flag whose subject lied at every tick - that flag is evidence, not an artifact.

**unexplained_decision_rate.** Numerator: an EJECT whose citations do not resolve in the voter's own inputs, or a SKIP that names no player at all - empty considered_alternatives AND a MODEL-AUTHORED rationale carrying no whole-token player id. Model-authored means the remainder once the meeting layer's own audit markers are cut off by provenance, the same anchored chain eval.deduction_metrics._scan_marker_chain walks and api.replay_loader cuts for rationale_text_clean: a guard marker preserves the coerced target's id and the teammate firewall then redacts the body, so reading the raw text would let the machinery's prose answer for a voter who named nothing. Denominator: all ballots. Not-evaluable: ballots whose voter has no recorded prompt. The two halves are reported separately because they are different defects: an EJECT with no basis, and an abstention that names nothing it weighed.

**evidence_quality_mix.** A mix, not a rate: one numerator per band, summing to the denominator. One row per EJECTION (a meeting whose outcome is EJECTED), classified ROLE-BLIND into the highest band the ejected player carried: vent_flag (a recorded vent_sighting flag names them), contradiction_flag (a recorded non-vent flag names them), first_hand (no flag, but an EJECT ballot against them cites a resolving observation of the voter's own memory, or a transcript turn carrying a structured observation that NAMES them - whole-token, by meetings.citation_relevance.names_player over the observation's dumped structure, so a turn whose only observation places somebody else, and a turn merely SPOKEN by the ejected player, are not first-hand accounts of them), hearsay (no flag, and the cited turn carries only an accusation), unevidenced (no flag and no resolving, on-target citation). Denominator: all ejections. Role-correctness is reported beside each band and gates nothing. eval.meeting_quality.decompose_ejection_channels is NOT used here: it returns None unless the ejected player is a true impostor, which would make the mix role-conditioned.

**rationale_faithfulness.** Numerator: ballots every extracted TOKEN of whose rationale_text is present in what the voter held - whole-token player ids (matched by meetings.citation_relevance.names_player), canonical room ids (matched case-insensitively, underscore or space), and tick references - checked against this meeting's transcript and that voter's own recorded prompts. Denominator: ballots carrying at least one such token. Not-evaluable: ballots with no extractable token, and ballots whose voter has no recorded prompt. It reads rationale_text WHOLE, guard audit markers included, and deliberately differs from row 4 there: this row asks whether every token in the RECORDED text is one the voter held, and a marker's preserved id always is, while row 4 asks the authorship question and must cut the machinery's prose off first. LIMITS, stated: this tests TOKENS, not propositions - an assertion and its negation score alike, and a true sentence assembled from present tokens scores the same as a false one. The direction memo's section 3 result on invented facts is two-method agreement between two graders, NOT this measurement.

**agent_authored_share.** Numerator: ballots the meeting layer did not re-aim - neither a typed guard_rewrite_reason (any BallotTargetRewriteReason member) nor a target-rewriting marker unwound by eval.deduction_metrics._authored_target, the fallback meetings/schemas.py prescribes for recordings made before the typed fields. Denominator: all ballots. Citation-only rewrites are NOT counted against the share and are reported separately as 'citation nulled, target intact'; a ballot carrying both is counted among the rewrites, because the target moved. The marker-only redirect census rides beside as a sub-count: it keys on the graph-redirect marker alone and is therefore smaller than the typed layer.

**wrong_but_believable_rate.** Numerator: EJECT ballots that are role-INCORRECT (the recorded target is a crewmate) AND grounded by row 1 AND not resting on a manufactured contradiction by row 3 (no manufactured flag in that meeting names the ballot's target). Denominator: all EJECT ballots. REPORTED, NEVER PENALISED: this is the owner's preferred case - a wrong decision on believable data - and the direction of this row is deliberately unstated.

**role_correct_ejection_rate.** Numerator: ejections whose ejected player was an IMPOSTOR. Denominator: all ejections. REPORTED BESIDE the suite, NEVER A GATE (decision D1, 2026-09-19). It is published last on purpose.

## Appendix: the fifth run (2026-09-16), out of the headline

OUT OF THE HEADLINE. The fifth run is a 3-ballot arena on a proof-free held-out band whose generator filters out the one evidence channel that reliably works, so neither arm is adoptable and neither arm's cells pool with the committed sets. It is reported because the two arms differ on the process measures the frozen outcome scored 0 and 2. Counts only: no prefix, prompt or transcript text is read into this artifact, and nothing under the archive is written.

Archive: `audits/deduction-candidate/run-2026-09-16` (read, never written).

| arm | recordings | meetings | EJECT | EJECT cited | SKIP | SKIP cited |
| --- | --- | --- | --- | --- | --- | --- |
| combined_accounts | 50 | 50 | 75 | 73 | 75 | 0 |
| repaired_clock | 50 | 50 | 14 | 14 | 136 | 0 |

Ballots per meeting: 3 ballots in 100 meetings.

No component reads this file yet. It is published beside the markdown so a spectator surface can load it later; today its only consumer is scripts/publish_process_scorecard.py --check, which recomputes both files from the committed recordings and fails on drift.
