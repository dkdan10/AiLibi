# The process scorecard

**Role-correctness is REPORTED and is NOT a gate. The owner accepted decision D1 of tasks/direction-2026-09-19-process-over-outcome.md section 10 on 2026-09-19: the process suite is the headline, role-correctness is a reported cell beside it, and the preregistered supported_correct_ejection outcome stops being the project's gate. Nothing in this scorecard, and nothing any card derived from it gates on, pushes an agent toward the correct answer: a wrong decision on believable data is the game working, and it is counted in row 8, never penalised.**

Nine measures of whether a decision rested on data the agent actually held, computed with **zero model calls** from recordings already in the tree. The suite is [the direction of 2026-09-19](../tasks/direction-2026-09-19-process-over-outcome.md) section 8; the card that publishes it is [the process scorecard card](../tasks/work/process-scorecard.md). Every row's definition — numerator, denominator, non-coverage — is published beside the number here and as typed keys in [`process-scorecard.json`](process-scorecard.json).

This page is GENERATED. Do not edit it by hand: run `uv run python scripts/publish_process_scorecard.py` and commit the result. `uv run python scripts/publish_process_scorecard.py --check` recomputes both files from the recordings and fails on drift.

History (2026-10-09): the fifth run's appendix, folded from `audits/deduction-candidate/run-2026-09-16`, left this page; `e75780b7` is the last commit that published it, and the archive keeps its bytes.

## Why rows 2 and 3 are the point

Without **argmax-independence** the headline certifies an arithmetic aggregator as a reasoner: on the shipped corpus most crew EJECT ballots simply name the voter's own rendered suspicion argmax, and every departing ballot still carries a valid citation — so a "cited and on-target" measure scores the two alike. Without the **manufactured-contradiction rate** it certifies the seed-41 failure: the alibi schema compresses a truthfully-moving player into a single-room envelope, the detectors flag the envelope, and a right-looking process convicts an innocent on evidence the schema invented.

## Recording provenance

The four sets span 2 recorded eras, grouped by the era registry (`eval/eras.py`). An era is pooled only with itself and is never averaged across a boundary:

* **baseline-9**, recorded 2026-09-22: `replays/ml_corpus/9p2i`, `replays/ml_corpus/4p1i`, `replays/samples/4p1i`. Owning record: [`audits/audit-2026-09-22-process-rerecord.md`](../audits/audit-2026-09-22-process-rerecord.md).
* **stage-b-r3**, recorded 2026-10-09: `replays/samples/9p2i`. Owning record: [`audits/audit-2026-10-09-stage-b-r3.md`](../audits/audit-2026-10-09-stage-b-r3.md).

The baseline-9 sets are the process re-record made after the substrate wave (the route claim, the grounded SKIP with its labelling guards, and the weighing channel); the column on the recordings made before that wave is committed in that record's section 1, the SKIP row read 0 there by instruction, and row 3's claims became routes across the same line, so no row pools with that column. A set whose bytes replaced an earlier recording carries that recording's published rows as a dated before column, read from [`process-scorecard-before.json`](process-scorecard-before.json) and never recomputed.

Report format version 2; scorecard schema version 3; decision date 2026-09-19.

## Pooled within an era

### pooled: the baseline-9 sets

250 games, 531 meetings, 2785 ballots (1602 EJECT, 1183 SKIP). Sources: `replays/ml_corpus/9p2i`, `replays/ml_corpus/4p1i`, `replays/samples/4p1i`.

| # | row | value |
| --- | --- | --- |
| 1 | grounded-decision rate, EJECT | 1589/1602 = 0.9919 |
| 1 | grounded-decision rate, SKIP | 272/1183 = 0.2299 |
| 1 | grounded-decision rate, all ballots | 1861/2785 = 0.6682 |
| 2 | argmax-independence: deviating EJECTs | 147/1362 = 10.8% |
| 2 | argmax-independence: role-correct, followers vs deviators | 1178/1215 = 97.0% vs 14/147 = 9.5% (chance 32.0%) |
| 3 | manufactured-contradiction rate | 0/57 = 0.0000 (not evaluable 57) |
| 4 | unexplained-decision rate | 12/2785 = 0.0043 |
| 5 | evidence-quality mix | contradiction_flag 3, first_hand 54, hearsay 8, vent_flag 256 over 321 ejections |
| 6 | rationale faithfulness (TOKENS) | 2307/2309 = 0.9991 (not evaluable 476) |
| 7 | agent-authored share | 2768/2785 = 0.9939 |
| 8 | wrong-but-believable rate | 343/1602 = 0.2141 — reported, never penalised |
| 9 | role-correct ejection rate | 288/321 = 0.8972 — reported beside, never a gate |

Row 2 detail: followers 1215, deviators 147, ties excluded 103, no rendered row inside the valid-target list 0. In meetings where the engine minted no contradiction at all, role-correct: followers 151/183, deviators 5/118.

Row 3 detail: manufactured flags contradicting an account the engine route makes true at EVERY tick, 0 of 0; the rest are the span-envelope artifact proper.

Row 3 claim census: 781 self-alibi claims (781 spanning more than one tick), 9 false under the envelope test of which 9 are multi-tick, 0 false under the strict test (in that room at NO tick the claim covers), 0 unresolvable, and 0 further alibi claims name another player and are out of the census.

Row 4 detail: EJECT ballots whose citation does not resolve, 0; SKIP ballots naming no player at all, 12 (1169 SKIPs carry considered_alternatives and 714 name a player in prose).

Row 5 detail (role-correct beside each band, gating nothing): contradiction_flag 1/3, first_hand 26/54, hearsay 5/8, vent_flag 256/256.

Row 6 detail: 2 of 5736 extracted tokens are absent from what the voter held.

Row 7 detail: typed guard rewrites invalid_target 5, teammate_coerced 12; 0 unwound from a marker with no typed reason; 3 citation nulled, target intact; redirect-marker census 0 (0 EJECT, 0 coerced SKIP).

Context: impostor alibis 106/114 survived contradiction detection; reporter slots 30/488 ejected against innocent non-reporter slots 2/1390.

The stage-b-r3 era holds one set, `replays/samples/9p2i`; its rows are under Per set.

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

50 games, 119 meetings, 702 ballots (397 EJECT, 305 SKIP). Sources: `replays/samples/9p2i`.

Before (stage-b-r2, as published at `2eed2e92`): 50 games, 117 meetings, 691 ballots (410 EJECT, 281 SKIP).

| # | row | before: stage-b-r2, as published at `2eed2e92` | value |
| --- | --- | --- | --- |
| 1 | grounded-decision rate, EJECT | 407/410 = 0.9927 | 394/397 = 0.9924 |
| 1 | grounded-decision rate, SKIP | 44/281 = 0.1566 | 47/305 = 0.1541 |
| 1 | grounded-decision rate, all ballots | 451/691 = 0.6527 | 441/702 = 0.6282 |
| 2 | argmax-independence: deviating EJECTs | 65/292 = 22.3% | 56/291 = 19.2% |
| 2 | argmax-independence: role-correct, followers vs deviators | 215/227 = 94.7% vs 4/65 = 6.2% (chance 34.0%) | 215/235 = 91.5% vs 2/56 = 3.6% (chance 32.8%) |
| 3 | manufactured-contradiction rate | 1/15 = 0.0667 (not evaluable 14) | 0/15 = 0.0000 (not evaluable 15) |
| 4 | unexplained-decision rate | 11/691 = 0.0159 | 6/702 = 0.0085 |
| 5 | evidence-quality mix | contradiction_flag 2, first_hand 39, hearsay 1, vent_flag 24 over 66 ejections | contradiction_flag 1, first_hand 35, hearsay 1, vent_flag 24 over 61 ejections |
| 6 | rationale faithfulness (TOKENS) | 580/580 = 1.0000 (not evaluable 111) | 583/583 = 1.0000 (not evaluable 119) |
| 7 | agent-authored share | 674/691 = 0.9754 | 692/702 = 0.9858 |
| 8 | wrong-but-believable rate | 189/410 = 0.4610 — reported, never penalised | 177/397 = 0.4458 — reported, never penalised |
| 9 | role-correct ejection rate | 44/66 = 0.6667 — reported beside, never a gate | 46/61 = 0.7541 — reported beside, never a gate |

Row 2 detail: followers 235, deviators 56, ties excluded 5, no rendered row inside the valid-target list 0. In meetings where the engine minted no contradiction at all, role-correct: followers 105/116, deviators 1/52.

Row 3 detail: manufactured flags contradicting an account the engine route makes true at EVERY tick, 0 of 0; the rest are the span-envelope artifact proper.

Row 3 claim census: 331 self-alibi claims (330 spanning more than one tick), 3 false under the envelope test of which 3 are multi-tick, 0 false under the strict test (in that room at NO tick the claim covers), 0 unresolvable, and 0 further alibi claims name another player and are out of the census.

Row 4 detail: EJECT ballots whose citation does not resolve, 0; SKIP ballots naming no player at all, 6 (299 SKIPs carry considered_alternatives and 185 name a player in prose).

Row 5 detail (role-correct beside each band, gating nothing): contradiction_flag 0/1, first_hand 22/35, hearsay 0/1, vent_flag 24/24.

Row 6 detail: 0 of 1517 extracted tokens are absent from what the voter held.

Row 7 detail: typed guard rewrites teammate_coerced 10; 0 unwound from a marker with no typed reason; 0 citation nulled, target intact; redirect-marker census 0 (0 EJECT, 0 coerced SKIP).

Context: impostor alibis 34/34 survived contradiction detection; reporter slots 10/115 ejected against innocent non-reporter slots 5/375.

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

No component reads this file yet. It is published beside the markdown so a spectator surface can load it later; today its only consumer is scripts/publish_process_scorecard.py --check, which recomputes both files from the committed recordings and fails on drift.
