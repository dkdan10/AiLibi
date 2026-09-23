# The process scorecard

**Role-correctness is REPORTED and is NOT a gate. The owner accepted decision D1 of tasks/direction-2026-09-19-process-over-outcome.md section 10 on 2026-09-19: the process suite is the headline, role-correctness is a reported cell beside it, and the preregistered supported_correct_ejection outcome stops being the project's gate. Nothing in this scorecard, and nothing any card derived from it gates on, pushes an agent toward the correct answer: a wrong decision on believable data is the game working, and it is counted in row 8, never penalised.**

Nine measures of whether a decision rested on data the agent actually held, computed with **zero model calls** from recordings already in the tree. The suite is [the direction of 2026-09-19](../tasks/direction-2026-09-19-process-over-outcome.md) section 8; the card that publishes it is [the process scorecard card](../tasks/work/process-scorecard.md). Every row's definition — numerator, denominator, non-coverage — is published beside the number here and as typed keys in [`process-scorecard.json`](process-scorecard.json).

This page is GENERATED. Do not edit it by hand: run `uv run python scripts/publish_process_scorecard.py` and commit the result. `uv run python scripts/publish_process_scorecard.py --check` recomputes both files from the recordings and fails on drift.

## Why rows 2 and 3 are the point

Without **argmax-independence** the headline certifies an arithmetic aggregator as a reasoner: on the shipped corpus most crew EJECT ballots simply name the voter's own rendered suspicion argmax, and every departing ballot still carries a valid citation — so a "cited and on-target" measure scores the two alike. Without the **manufactured-contradiction rate** it certifies the seed-41 failure: the alibi schema compresses a truthfully-moving player into a single-room envelope, the detectors flag the envelope, and a right-looking process convicts an innocent on evidence the schema invented.

## Recording provenance

These four sets are one era — baseline 9, recorded after the substrate wave (the route claim, the grounded SKIP with its labelling guards, and the weighing channel) by [the process re-record](../audits/audit-2026-09-22-process-rerecord.md). They are labelled, never averaged across a boundary: the column on the recordings made before that wave is committed in that record's section 1, the SKIP row read 0 there by instruction, and row 3's claims became routes across the same line, so no row pools with that column.

* `replays/ml_corpus/9p2i`
* `replays/samples/9p2i`
* `replays/ml_corpus/4p1i`
* `replays/samples/4p1i`

Report format version 2; scorecard schema version 1; decision date 2026-09-19.

## Pooled

### pooled: all four committed sets

300 games, 676 meetings, 3630 ballots (2098 EJECT, 1532 SKIP). Sources: `replays/ml_corpus/9p2i`, `replays/samples/9p2i`, `replays/ml_corpus/4p1i`, `replays/samples/4p1i`.

| # | row | value |
| --- | --- | --- |
| 1 | grounded-decision rate, EJECT | 2083/2098 = 0.9929 |
| 1 | grounded-decision rate, SKIP | 351/1532 = 0.2291 |
| 1 | grounded-decision rate, all ballots | 2434/3630 = 0.6705 |
| 2 | argmax-independence: deviating EJECTs | 178/1775 = 10.0% |
| 2 | argmax-independence: role-correct, followers vs deviators | 1537/1597 = 96.2% vs 17/178 = 9.6% (chance 31.5%) |
| 3 | manufactured-contradiction rate | 0/74 = 0.0000 (not evaluable 74) |
| 4 | unexplained-decision rate | 17/3630 = 0.0047 |
| 5 | evidence-quality mix | contradiction_flag 5, first_hand 70, hearsay 10, vent_flag 326 over 411 ejections |
| 6 | rationale faithfulness (TOKENS) | 3015/3017 = 0.9993 (not evaluable 613) |
| 7 | agent-authored share | 3609/3630 = 0.9942 |
| 8 | wrong-but-believable rate | 462/2098 = 0.2202 — reported, never penalised |
| 9 | role-correct ejection rate | 369/411 = 0.8978 — reported beside, never a gate |

Row 2 detail: followers 1597, deviators 178, ties excluded 140, no rendered row inside the valid-target list 0. In meetings where the engine minted no contradiction at all, role-correct: followers 203/254, deviators 8/143.

Row 3 detail: manufactured flags contradicting an account the engine route makes true at EVERY tick, 0 of 0; the rest are the span-envelope artifact proper.

Row 3 claim census: 1021 self-alibi claims (1020 spanning more than one tick), 11 false under the envelope test of which 11 are multi-tick, 0 false under the strict test (in that room at NO tick the claim covers), 0 unresolvable, and 0 further alibi claims name another player and are out of the census.

Row 4 detail: EJECT ballots whose citation does not resolve, 0; SKIP ballots naming no player at all, 17 (1513 SKIPs carry considered_alternatives and 929 name a player in prose).

Row 5 detail (role-correct beside each band, gating nothing): contradiction_flag 2/5, first_hand 36/70, hearsay 5/10, vent_flag 326/326.

Row 6 detail: 2 of 7458 extracted tokens are absent from what the voter held.

Row 7 detail: typed guard rewrites invalid_target 8, teammate_coerced 13; 0 unwound from a marker with no typed reason; 5 citation nulled, target intact; redirect-marker census 0 (0 EJECT, 0 coerced SKIP).

Context: impostor alibis 145/155 survived contradiction detection; reporter slots 37/623 ejected against innocent non-reporter slots 4/1841.

### pooled: the two 9p2i sets

200 games, 594 meetings, 3384 ballots (1983 EJECT, 1401 SKIP). Sources: `replays/ml_corpus/9p2i`, `replays/samples/9p2i`.

| # | row | value |
| --- | --- | --- |
| 1 | grounded-decision rate, EJECT | 1970/1983 = 0.9934 |
| 1 | grounded-decision rate, SKIP | 309/1401 = 0.2206 |
| 1 | grounded-decision rate, all ballots | 2279/3384 = 0.6735 |
| 2 | argmax-independence: deviating EJECTs | 178/1677 = 10.6% |
| 2 | argmax-independence: role-correct, followers vs deviators | 1440/1499 = 96.1% vs 17/178 = 9.6% (chance 30.4%) |
| 3 | manufactured-contradiction rate | 0/74 = 0.0000 (not evaluable 74) |
| 4 | unexplained-decision rate | 17/3384 = 0.0050 |
| 5 | evidence-quality mix | contradiction_flag 5, first_hand 67, hearsay 10, vent_flag 281 over 363 ejections |
| 6 | rationale faithfulness (TOKENS) | 2843/2844 = 0.9996 (not evaluable 540) |
| 7 | agent-authored share | 3363/3384 = 0.9938 |
| 8 | wrong-but-believable rate | 446/1983 = 0.2249 — reported, never penalised |
| 9 | role-correct ejection rate | 322/363 = 0.8871 — reported beside, never a gate |

Row 2 detail: followers 1499, deviators 178, ties excluded 139, no rendered row inside the valid-target list 0. In meetings where the engine minted no contradiction at all, role-correct: followers 196/246, deviators 8/143.

Row 3 detail: manufactured flags contradicting an account the engine route makes true at EVERY tick, 0 of 0; the rest are the span-envelope artifact proper.

Row 3 claim census: 955 self-alibi claims (954 spanning more than one tick), 11 false under the envelope test of which 11 are multi-tick, 0 false under the strict test (in that room at NO tick the claim covers), 0 unresolvable, and 0 further alibi claims name another player and are out of the census.

Row 4 detail: EJECT ballots whose citation does not resolve, 0; SKIP ballots naming no player at all, 17 (1382 SKIPs carry considered_alternatives and 872 name a player in prose).

Row 5 detail (role-correct beside each band, gating nothing): contradiction_flag 2/5, first_hand 34/67, hearsay 5/10, vent_flag 281/281.

Row 6 detail: 1 of 7068 extracted tokens are absent from what the voter held.

Row 7 detail: typed guard rewrites invalid_target 8, teammate_coerced 13; 0 unwound from a marker with no typed reason; 5 citation nulled, target intact; redirect-marker census 0 (0 EJECT, 0 coerced SKIP).

Context: impostor alibis 143/153 survived contradiction detection; reporter slots 36/551 ejected against innocent non-reporter slots 4/1769.

## Per set

### ml_corpus/9p2i

150 games, 449 meetings, 2539 ballots (1487 EJECT, 1052 SKIP). Sources: `replays/ml_corpus/9p2i`.

| # | row | value |
| --- | --- | --- |
| 1 | grounded-decision rate, EJECT | 1476/1487 = 0.9926 |
| 1 | grounded-decision rate, SKIP | 230/1052 = 0.2186 |
| 1 | grounded-decision rate, all ballots | 1706/2539 = 0.6719 |
| 2 | argmax-independence: deviating EJECTs | 147/1264 = 11.6% |
| 2 | argmax-independence: role-correct, followers vs deviators | 1081/1117 = 96.8% vs 14/147 = 9.5% (chance 30.6%) |
| 3 | manufactured-contradiction rate | 0/57 = 0.0000 (not evaluable 57) |
| 4 | unexplained-decision rate | 12/2539 = 0.0047 |
| 5 | evidence-quality mix | contradiction_flag 3, first_hand 51, hearsay 8, vent_flag 211 over 273 ejections |
| 6 | rationale faithfulness (TOKENS) | 2135/2136 = 0.9995 (not evaluable 403) |
| 7 | agent-authored share | 2522/2539 = 0.9933 |
| 8 | wrong-but-believable rate | 327/1487 = 0.2199 — reported, never penalised |
| 9 | role-correct ejection rate | 241/273 = 0.8828 — reported beside, never a gate |

Row 2 detail: followers 1117, deviators 147, ties excluded 102, no rendered row inside the valid-target list 0. In meetings where the engine minted no contradiction at all, role-correct: followers 144/175, deviators 5/118.

Row 3 detail: manufactured flags contradicting an account the engine route makes true at EVERY tick, 0 of 0; the rest are the span-envelope artifact proper.

Row 3 claim census: 715 self-alibi claims (715 spanning more than one tick), 9 false under the envelope test of which 9 are multi-tick, 0 false under the strict test (in that room at NO tick the claim covers), 0 unresolvable, and 0 further alibi claims name another player and are out of the census.

Row 4 detail: EJECT ballots whose citation does not resolve, 0; SKIP ballots naming no player at all, 12 (1038 SKIPs carry considered_alternatives and 657 name a player in prose).

Row 5 detail (role-correct beside each band, gating nothing): contradiction_flag 1/3, first_hand 24/51, hearsay 5/8, vent_flag 211/211.

Row 6 detail: 1 of 5346 extracted tokens are absent from what the voter held.

Row 7 detail: typed guard rewrites invalid_target 5, teammate_coerced 12; 0 unwound from a marker with no typed reason; 3 citation nulled, target intact; redirect-marker census 0 (0 EJECT, 0 coerced SKIP).

Context: impostor alibis 104/112 survived contradiction detection; reporter slots 29/416 ejected against innocent non-reporter slots 2/1318.

### samples/9p2i

50 games, 145 meetings, 845 ballots (496 EJECT, 349 SKIP). Sources: `replays/samples/9p2i`.

| # | row | value |
| --- | --- | --- |
| 1 | grounded-decision rate, EJECT | 494/496 = 0.9960 |
| 1 | grounded-decision rate, SKIP | 79/349 = 0.2264 |
| 1 | grounded-decision rate, all ballots | 573/845 = 0.6781 |
| 2 | argmax-independence: deviating EJECTs | 31/413 = 7.5% |
| 2 | argmax-independence: role-correct, followers vs deviators | 359/382 = 94.0% vs 3/31 = 9.7% (chance 29.8%) |
| 3 | manufactured-contradiction rate | 0/17 = 0.0000 (not evaluable 17) |
| 4 | unexplained-decision rate | 5/845 = 0.0059 |
| 5 | evidence-quality mix | contradiction_flag 2, first_hand 16, hearsay 2, vent_flag 70 over 90 ejections |
| 6 | rationale faithfulness (TOKENS) | 708/708 = 1.0000 (not evaluable 137) |
| 7 | agent-authored share | 841/845 = 0.9953 |
| 8 | wrong-but-believable rate | 119/496 = 0.2399 — reported, never penalised |
| 9 | role-correct ejection rate | 81/90 = 0.9000 — reported beside, never a gate |

Row 2 detail: followers 382, deviators 31, ties excluded 37, no rendered row inside the valid-target list 0. In meetings where the engine minted no contradiction at all, role-correct: followers 52/71, deviators 3/25.

Row 3 detail: manufactured flags contradicting an account the engine route makes true at EVERY tick, 0 of 0; the rest are the span-envelope artifact proper.

Row 3 claim census: 240 self-alibi claims (239 spanning more than one tick), 2 false under the envelope test of which 2 are multi-tick, 0 false under the strict test (in that room at NO tick the claim covers), 0 unresolvable, and 0 further alibi claims name another player and are out of the census.

Row 4 detail: EJECT ballots whose citation does not resolve, 0; SKIP ballots naming no player at all, 5 (344 SKIPs carry considered_alternatives and 215 name a player in prose).

Row 5 detail (role-correct beside each band, gating nothing): contradiction_flag 1/2, first_hand 10/16, hearsay 0/2, vent_flag 70/70.

Row 6 detail: 0 of 1722 extracted tokens are absent from what the voter held.

Row 7 detail: typed guard rewrites invalid_target 3, teammate_coerced 1; 0 unwound from a marker with no typed reason; 2 citation nulled, target intact; redirect-marker census 0 (0 EJECT, 0 coerced SKIP).

Context: impostor alibis 39/41 survived contradiction detection; reporter slots 7/135 ejected against innocent non-reporter slots 2/451.

### ml_corpus/4p1i

50 games, 43 meetings, 129 ballots (66 EJECT, 63 SKIP). Sources: `replays/ml_corpus/4p1i`.

| # | row | value |
| --- | --- | --- |
| 1 | grounded-decision rate, EJECT | 64/66 = 0.9697 |
| 1 | grounded-decision rate, SKIP | 19/63 = 0.3016 |
| 1 | grounded-decision rate, all ballots | 83/129 = 0.6434 |
| 2 | argmax-independence: deviating EJECTs | 0/55 = 0.0% |
| 2 | argmax-independence: role-correct, followers vs deviators | 55/55 = 100.0% vs 0/0 = n/a (chance 50.0%) |
| 3 | manufactured-contradiction rate | 0/0 = n/a |
| 4 | unexplained-decision rate | 0/129 = 0.0000 |
| 5 | evidence-quality mix | first_hand 2, vent_flag 26 over 28 ejections |
| 6 | rationale faithfulness (TOKENS) | 92/92 = 1.0000 (not evaluable 37) |
| 7 | agent-authored share | 129/129 = 1.0000 |
| 8 | wrong-but-believable rate | 9/66 = 0.1364 — reported, never penalised |
| 9 | role-correct ejection rate | 27/28 = 0.9643 — reported beside, never a gate |

Row 2 detail: followers 55, deviators 0, ties excluded 1, no rendered row inside the valid-target list 0. In meetings where the engine minted no contradiction at all, role-correct: followers 3/3, deviators 0/0.

Row 3 detail: manufactured flags contradicting an account the engine route makes true at EVERY tick, 0 of 0; the rest are the span-envelope artifact proper.

Row 3 claim census: 31 self-alibi claims (31 spanning more than one tick), 0 false under the envelope test of which 0 are multi-tick, 0 false under the strict test (in that room at NO tick the claim covers), 0 unresolvable, and 0 further alibi claims name another player and are out of the census.

Row 4 detail: EJECT ballots whose citation does not resolve, 0; SKIP ballots naming no player at all, 0 (63 SKIPs carry considered_alternatives and 25 name a player in prose).

Row 5 detail (role-correct beside each band, gating nothing): first_hand 1/2, vent_flag 26/26.

Row 6 detail: 0 of 201 extracted tokens are absent from what the voter held.

Row 7 detail: typed guard rewrites none; 0 unwound from a marker with no typed reason; 0 citation nulled, target intact; redirect-marker census 0 (0 EJECT, 0 coerced SKIP).

Context: impostor alibis 1/1 survived contradiction detection; reporter slots 1/36 ejected against innocent non-reporter slots 0/36.

### samples/4p1i

50 games, 39 meetings, 117 ballots (49 EJECT, 68 SKIP). Sources: `replays/samples/4p1i`.

| # | row | value |
| --- | --- | --- |
| 1 | grounded-decision rate, EJECT | 49/49 = 1.0000 |
| 1 | grounded-decision rate, SKIP | 23/68 = 0.3382 |
| 1 | grounded-decision rate, all ballots | 72/117 = 0.6154 |
| 2 | argmax-independence: deviating EJECTs | 0/43 = 0.0% |
| 2 | argmax-independence: role-correct, followers vs deviators | 42/43 = 97.7% vs 0/0 = n/a (chance 50.0%) |
| 3 | manufactured-contradiction rate | 0/0 = n/a |
| 4 | unexplained-decision rate | 0/117 = 0.0000 |
| 5 | evidence-quality mix | first_hand 1, vent_flag 19 over 20 ejections |
| 6 | rationale faithfulness (TOKENS) | 80/81 = 0.9877 (not evaluable 36) |
| 7 | agent-authored share | 117/117 = 1.0000 |
| 8 | wrong-but-believable rate | 7/49 = 0.1429 — reported, never penalised |
| 9 | role-correct ejection rate | 20/20 = 1.0000 — reported beside, never a gate |

Row 2 detail: followers 43, deviators 0, ties excluded 0, no rendered row inside the valid-target list 0. In meetings where the engine minted no contradiction at all, role-correct: followers 4/5, deviators 0/0.

Row 3 detail: manufactured flags contradicting an account the engine route makes true at EVERY tick, 0 of 0; the rest are the span-envelope artifact proper.

Row 3 claim census: 35 self-alibi claims (35 spanning more than one tick), 0 false under the envelope test of which 0 are multi-tick, 0 false under the strict test (in that room at NO tick the claim covers), 0 unresolvable, and 0 further alibi claims name another player and are out of the census.

Row 4 detail: EJECT ballots whose citation does not resolve, 0; SKIP ballots naming no player at all, 0 (68 SKIPs carry considered_alternatives and 32 name a player in prose).

Row 5 detail (role-correct beside each band, gating nothing): first_hand 1/1, vent_flag 19/19.

Row 6 detail: 1 of 189 extracted tokens are absent from what the voter held.

Row 7 detail: typed guard rewrites none; 0 unwound from a marker with no typed reason; 0 citation nulled, target intact; redirect-marker census 0 (0 EJECT, 0 coerced SKIP).

Context: impostor alibis 1/1 survived contradiction detection; reporter slots 0/36 ejected against innocent non-reporter slots 0/36.

## Row definitions

**grounded_decision_rate.** Numerator: ballots whose citation RESOLVES in the voter's own inputs (primary_reason_id in this meeting's turns, or primary_reason_observation_id carried whole-token on a line of that voter's own recorded prompts) AND bears on the decision's subject by meetings.citation_relevance.citations_bear_on - the subject being the recorded target for an EJECT and any member of considered_alternatives for a SKIP. Denominator: all ballots of that decision kind. Not-evaluable: ballots OF THAT SAME KIND whose voter has no recorded prompt in the meeting - counted per kind, so a promptless EJECT never makes the SKIP cell read as one that measured nothing; the all-ballots cell carries the sum. An UNCITED ballot is not grounded: citations_bear_on is vacuously true with nothing cited, so presence and resolution are required before aboutness is asked. It does NOT measure whether the cited line was factually true.

**argmax_independence.** Over CREW EJECT ballots, comparing the RECORDED target with the argmax of that voter's own rendered suspicion rows INTERSECTED with that voter's rendered valid-ejection-target list. Numerator: the DEVIATING ballots, whose recorded target is not that argmax. Denominator: the unambiguous ballots. Ties are excluded and counted; a ballot whose voter's prompts carry no row inside the valid list is not-evaluable and counted. Roles come from the seeder, are used only to report the role-correctness of followers and deviators BESIDE the split, and gate nothing. Chance is the mean, over the SAME unambiguous ballots that form the denominator - never over the excluded ties or the not-evaluable ballots - of the living-impostor share of each voter's own rendered valid-target list. It does NOT measure whether the voter read the graph, only whether the recorded call equals the arithmetic the engine handed it.

**manufactured_contradiction_rate.** Numerator: recorded contradiction flags whose kind is an alibi class (alibi_conflict, alibi_vs_sighting, alibi_vs_physical) and whose subjects name the speaker of a SELF-alibi claim in that meeting that is TRUE at at least one tick of its own span against that speaker's engine route from a state-hash-verified walk_replay. Denominator: all alibi-class flags. Not-evaluable: an alibi-class flag naming no self-alibi speaker in its meeting, one whose claim covers a tick the walk does not reach, or one resting on a multi-leg route, which a recorded flag does not attribute to a leg - scoring it across the whole route would file a flag that caught a fabricated leg as manufactured. Ticks are agent-frame and resolve against engine tick T - 1. It does NOT measure intent, and it does NOT clear a flag whose subject lied at every tick - that flag is evidence, not an artifact.

**unexplained_decision_rate.** Numerator: an EJECT whose citations do not resolve in the voter's own inputs, or a SKIP that names no player at all - empty considered_alternatives AND a MODEL-AUTHORED rationale carrying no whole-token player id. Model-authored means the remainder once the meeting layer's own audit markers are cut off BY PROVENANCE: the marker region eval.deduction_metrics._split_rationale establishes from that voter's OWN pre-guard vote response, scanned by _scan_marker_chain - the same cut api.replay_loader makes for rationale_text_clean. Shape is not provenance, so the whole record is never scanned: a model body that OPENS with marker-shaped prose sits at position 0 too, and scanning the record would credit the guard with the voter's own words. A guard marker preserves the coerced target's id and the teammate firewall then redacts the body, so reading the raw text would let the machinery's prose answer for a voter who named nothing. Denominator: all ballots. Not-evaluable: ballots whose voter has no recorded prompt. The two halves are reported separately because they are different defects: an EJECT with no basis, and an abstention that names nothing it weighed.

**evidence_quality_mix.** A mix, not a rate: one numerator per band, summing to the denominator. One row per EJECTION (a meeting whose outcome is EJECTED), classified ROLE-BLIND into the highest band the ejected player carried: vent_flag (a recorded vent_sighting flag names them), contradiction_flag (a recorded non-vent flag names them), first_hand (no flag, but an EJECT ballot against them cites a resolving observation of the voter's own memory, or a transcript turn carrying a structured observation that NAMES them - whole-token, by meetings.citation_relevance.names_player over the observation's dumped structure, so a turn whose only observation places somebody else, and a turn merely SPOKEN by the ejected player, are not first-hand accounts of them), hearsay (no flag, and the cited turn carries only an accusation), unevidenced (no flag and no resolving, on-target citation). Denominator: all ejections. Role-correctness is reported beside each band and gates nothing. eval.meeting_quality.decompose_ejection_channels is NOT used here: it returns None unless the ejected player is a true impostor, which would make the mix role-conditioned.

**rationale_faithfulness.** Numerator: ballots every extracted TOKEN of whose rationale_text is present in what the voter held - whole-token player ids (matched by meetings.citation_relevance.names_player), canonical room ids (matched case-insensitively, underscore or space), and tick references - checked against this meeting's transcript and that voter's own recorded prompts. Denominator: ballots carrying at least one such token. Not-evaluable: ballots with no extractable token, and ballots whose voter has no recorded prompt. It reads rationale_text WHOLE, guard audit markers included, and deliberately differs from row 4 there: this row asks whether every token in the RECORDED text is one the voter held, and a marker's preserved id always is, while row 4 asks the authorship question and must cut the machinery's prose off first. LIMITS, stated: this tests TOKENS, not propositions - an assertion and its negation score alike, and a true sentence assembled from present tokens scores the same as a false one. The direction memo's section 3 result on invented facts is two-method agreement between two graders, NOT this measurement.

**agent_authored_share.** Numerator: ballots the meeting layer did not re-aim - neither a typed guard_rewrite_reason (any BallotTargetRewriteReason member) nor a target-rewriting marker unwound by eval.deduction_metrics._authored_target, the fallback meetings/schemas.py prescribes for recordings made before the typed fields. The marker channel reads the PROVENANCE-established marker region (eval.deduction_metrics._split_rationale) and never the whole recorded rationale, so a model body opening with marker-shaped prose is not read as a guard rewrite. Denominator: all ballots. Citation-only rewrites are NOT counted against the share and are reported separately as 'citation nulled, target intact'; a ballot carrying both is counted among the rewrites, because the target moved. The marker-only redirect census rides beside as a sub-count: it keys on the graph-redirect marker alone and is therefore smaller than the typed layer.

**wrong_but_believable_rate.** Numerator: EJECT ballots that are role-INCORRECT (the recorded target is a crewmate) AND grounded by row 1 AND not resting on a manufactured contradiction by row 3 (no manufactured flag in that meeting names the ballot's target). Denominator: all EJECT ballots. Not-evaluable: EJECT ballots whose voter has no recorded prompt, the same per-kind count row 1's EJECT cell carries. REPORTED, NEVER PENALISED: this is the owner's preferred case - a wrong decision on believable data - and the direction of this row is deliberately unstated.

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
