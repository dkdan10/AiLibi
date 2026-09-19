# Publish a deterministic process scorecard over the committed recordings

**Status:** done

## Outcome

The project gains one committed answer to "was this decision grounded in what
the agent held?", computed with zero model calls from bytes already in the
tree. A scorer folds the four committed sets plus the fifth run's archive into
the nine-row suite of the direction memo's section 8, defines every row in its
own output, and publishes `docs/process-scorecard.md` beside a
`docs/process-scorecard.json` a spectator surface can load later. The header
states, dated 2026-09-19, that role-correctness is REPORTED and is NOT a gate.
Two rows are the point: argmax-independence, which stops the headline
certifying an arithmetic aggregator as a reasoner, and the
manufactured-contradiction rate, which stops it certifying seed 41. No agent
behaviour, prompt, schema or recorded byte moves. These nine definitions are
the measures the substrate cards and [the re-record](process-rerecord.md)
quote; nothing else defines them.

## Evidence

[The direction of 2026-09-19](../direction-2026-09-19-process-over-outcome.md)
is the basis; the owner accepted D1 to D8 as a set that date and its section 12
records the rulings. D1 (the process suite is the headline, role-correctness a
reported cell, the demotion written down dated) and D3 (ship on today's bytes)
are this card; section 8 is the suite, sections 4, 5 and 7 what rows 2, 3 and 8
mean.

**Every input is on disk and every figure reproduces.** A ballot carries both
citation fields, the recorded target and the typed guard provenance; its
meeting carries the transcript, the claims, the flags and each voter's own
rendered prompt (`eval/report_schema.py:203-216`). Counts only:

```sh
python3 -c 'import json,sys,glob,collections as C;c=C.Counter()
for f in sorted(glob.glob(sys.argv[1]+"/replay-seed-*.jsonl")):
 for r in map(json.loads,open(f)):
  for b in (r["ballots"] if r.get("kind")=="meeting" else ()):
   k="SKIP" if b["target"]=="SKIP" else "EJECT";c[k]+=1
   c[k+"+cited"]+=bool(b["primary_reason_id"] or
                       b["primary_reason_observation_id"])
   c[k+"+alt"]+=bool(b["considered_alternatives"])
print(dict(c))' replays/ml_corpus/9p2i
```

| set | EJECT | cited | SKIP | cited | SKIP with alternatives |
| --- | --- | --- | --- | --- | --- |
| `ml_corpus/9p2i` | 1,499 | 1,498 | 1,017 | 0 | 999 |
| `samples/9p2i` | 527 | 526 | 342 | 0 | 337 |
| `samples/4p1i` | 51 | 51 | 66 | 0 | 65 |
| `ml_corpus/4p1i` | 69 | 69 | 60 | 0 | 60 |

The SKIP zero is by instruction:
`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:268` tells the voter "a
SKIP needs neither" reason id and `:259` repeats it in prose. The two uncited
EJECTs are flag-exempt, the one exemption `guard_ballot_citation` holds
(`meetings/manager.py:3739`, read at `:3860-3866`). All 3,631 ballots carry
their voter's vote prompt, so the not-evaluable cell is 0.

**Row 2 reproduces with one cell corrected**, over crew EJECT ballots on
`ml_corpus/9p2i`, taking each voter's rendered suspicion rows intersected with
its rendered `## Valid ejection targets` list:

| | ballots | role-correct | memo said |
| --- | --- | --- | --- |
| target equals the argmax | 1,189 (93.6%) | 1,143 (96.1%) | 1,137 (95.6%) |
| target differs | 81 (6.4%) | 7 (8.6%) | 7 (8.6%) |
| zero-flag followers / deviators | 206 / 64 | 176 / 1 | 170 / 1 |

Chance, the impostor share of each voter's valid list, is 0.303. Denominator,
split, deviator column and chance land to the digit; the follower column is 6
higher and the same 6 sit in the zero-flag row. It is not the guard rewrites
(dropping the 58 marker-bearing ballots gives 1,098 of 1,135 and 7 of 77), so
it is a definition the memo left unpinned and this card pins.

**Row 3 reproduces exactly**, against each speaker's own engine route, over the
955 self-alibi claims in the two 9p2i sets (13 further alibi claims name
another player and are out of the census): 104 false under the envelope test,
103 of those multi-tick, exactly 2 false under a strict "in that room at no
tick the claim covers", 769 of the 955 spanning more than one tick.

**The analyzers to reuse exist; their gaps are named.**
`compute_ballot_target_redirects` (`eval/meeting_quality.py:1510`) keys on the
redirect marker alone (`:1536`): that is the redirect census, not the authored
share, which `guard_rewrite_reason` (`meetings/schemas.py:735-748`) carries in
four classes on these bytes (`ml_corpus/9p2i`: 57 `under_gate_redirect`, 6
`uncited_coerced`, 5 `teammate_coerced`, 2 `invalid_target`; 70 of 2,516).
`decompose_ejection_channels` (`eval/meeting_quality.py:1880`) returns `None`
unless the ejected player is a true impostor, so the role-blind mix comes from
`recorded_contradiction_flags` (`:2354`) and the cited line's observation type.
`citations_bear_on` (`meetings/citation_relevance.py:141`) is the ONE aboutness
rule, needing only turns and prompt lines, so relevance is computable offline
with the lever still `None`. `_authored_target`
(`eval/deduction_metrics.py:958`) falls back to the marker chain for older
recordings, as `meetings/schemas.py:810-812` prescribes. Ground truth is the
engine:
`walk_replay` (`eval/replay_walk.py:455`) re-seeds under a state-hash-verifying
profile and yields `TickAdvanced.state` (`:374`), as
`scripts/build_sample_report.py:147` takes roles.

## Acceptance

- [x] Review correction: row 4 no longer reads the vote guard's own marker text
  as the agent naming a player. The player-token test runs over the
  MODEL-AUTHORED remainder — the anchored, repr-aware chain
  `eval.deduction_metrics._scan_marker_chain` consumes, the same cut
  `api/replay_loader.py` makes for `rationale_text_clean` — so a teammate-coerced
  SKIP whose only `p-N` token sits inside the guard's marker counts as
  unexplained. Proved by
  `tests/eval/test_process_scorecard.py::test_a_coerced_skip_whose_only_player_token_is_the_guard_marker`
  against its pair
  `::test_the_same_coerced_skip_with_a_model_body_naming_a_player_is_not`, and
  republished: pooled unexplained moves 15/3631 → **20/3631**.
- [x] Review correction: row 2's chance baseline is accumulated over the
  UNAMBIGUOUS ballots only, below the tie and no-row returns, so its population
  is the denominator the published definition names. Proved by
  `tests/eval/test_process_scorecard.py::test_chance_is_measured_over_the_unambiguous_ballots_and_no_others`,
  which plants three ballots with three different impostor shares, one per
  outcome. `scorecard_from_tally` now REFUSES a tally whose chance population is
  not the row's denominator, pinned by the perturbed half
  `::test_a_chance_population_wider_than_the_denominator_is_refused`.
  Republished: `ml_corpus/9p2i` chance 0.303178 → **0.303528**, the 0.3035
  this card's Results quotes. (Raised by two round-1 lenses.)
- [x] Review correction: the prose no longer pairs the two-set manufactured
  count with the four-set wholly-true sub-count. Results Decision 5 and the pull
  request now read **158 manufactured with 8 wholly-true on the two 9p2i sets**
  and 159 with 9 across all four, matching
  `docs/process-scorecard.json` `pooled_9p2i` / `pooled`; reproduced by
  `uv run python scripts/publish_process_scorecard.py --check`. (Raised by three
  round-1 lenses.)
- [x] Review correction: row 5's `first_hand` band requires a structured
  observation that NAMES the ejected player, which is what its published
  definition and Limitation 4 always said; a non-empty `observations` tuple and
  a turn merely spoken by the ejected player are no longer routes. Proved by the
  pair `tests/eval/test_process_scorecard.py::test_a_cited_turn_observing_the_ejected_player_is_first_hand`
  / `::test_a_cited_turn_observing_somebody_else_is_not_first_hand` plus
  `::test_the_ejected_players_own_turn_is_not_a_first_hand_route`. Republished:
  8 ejections move `first_hand` → `hearsay` (pooled 83 → **75**), with every
  no-flag total unchanged.
- [x] A pure `eval/process_scorecard.py` folds loaded reports plus the engine
  walk into one frozen result: nine rows, each carrying its definition string
  in the object. Grounded EJECT and grounded SKIP mean a citation that resolves
  in the voter's own inputs AND bears on the decision's subject by
  `citations_bear_on`, the subject being the target for an EJECT and the union
  of `considered_alternatives` for a SKIP; the other seven are the memo's
  section 8 rows, with `compute_alibi_fabrication_rate`
  (`eval/alibi_fabrication.py:196`) and `compute_reporter_justice`
  (`eval/reporter_justice.py:540`) supplying context cells. Every rate
  publishes numerator, denominator and not-evaluable count separately. Planted:
  a SKIP citing a turn about a named alternative scores grounded, the same SKIP
  with the citation nulled does not.
- [x] Row 2 is computed as the Evidence pins it and says so in its definition
  string: crew EJECT ballots, recorded target, roles from the seeder, argmax
  over that voter's rows from `_rendered_suspicion_by_target_per_voter`
  (`eval/meeting_quality.py:2481`) intersected with the voter's rendered
  valid-target list, ties excluded and counted. The valid-target parse lands
  beside `_parse_suspicion_graph` (`:387`) under the FROZEN tier note its
  neighbours carry (`:318-321`), which permits an evidence reader and forbids
  new search. Planted: one follower and one deviator whose role-correctness
  differs, and a tie landing in the excluded count.
- [x] Row 3 counts a flag as MANUFACTURED when its kind is an alibi class, its
  subjects name the speaker of a self-alibi claim in that meeting, and the
  claim is true at at least one tick of its own span against that speaker's
  `walk_replay` route. The claim census rides beside it: 955 claims, 104
  envelope-false, 103 multi-tick, 2 strict-false. Planted: an envelope alibi
  true at its first tick mints a flag and a flat single-tick lie does not.
- [x] Rows 7 and 8 read the authored layer, never the marker prefix alone. The
  authored share counts every `BallotTargetRewriteReason` member through
  `_authored_target`, reports citation-nulling rewrites separately as "citation
  nulled, target intact", and carries the redirect census as a sub-count.
  Wrong-but-believable is role-incorrect AND row-1 grounded AND not row-3
  manufactured, labelled "reported, never penalised". Planted: a ballot
  carrying `under_gate_redirect` leaves the authored share, one carrying only a
  nulled-citation marker does not.
- [x] Row 6 states its own limits in the output. It extracts whole-token player
  ids, room ids and tick references from `rationale_text` and checks each
  against this meeting's transcript and that voter's recorded prompt, reusing
  `names_player` (`meetings/citation_relevance.py:54`). The output says this
  tests TOKENS and not propositions, that an assertion and its negation score
  alike, and that the memo's section 3 result on invented facts is two-method
  agreement rather than this measurement. Planted: a rationale naming an absent
  room fails, and a test pins the negated-assertion pass as the stated limit.
- [x] `scripts/publish_process_scorecard.py` writes both files, and `--check`
  recomputes and returns 1 with the remediation shape `check_report`
  (`scripts/build_sample_report.py:524-556`) uses, through
  `preflight_report_output` / `atomic_write_report`
  (`scripts/_report_output.py:47,72`) as
  `scripts/measure_reasoning_evidence.py:13,26-31` does, with every
  `replays/**` path and the fifth run's archive protected so the writer cannot
  target a recording. The JSON carries a `schema_version`, the per-row
  definitions and the note that no component reads it yet. No new shell line is
  added: `check.sh:39,41` runs pytest and
  `tests/scripts/test_build_sample_report.py:57-61` calls `check_report`, so
  `tests/scripts/test_process_scorecard.py` does the same. Planted: one edited
  cell in the committed JSON turns `--check` red.
- [x] The header carries, dated 2026-09-19 and linked to the direction, that
  role-correctness is reported and is not a gate per D1; the JSON carries it as
  typed keys. The fifth run is a closing APPENDIX, labelled out of the
  headline, reporting both arms (candidate 75 EJECT / 73 cited / 75 SKIP / 0
  cited; reference 14 / 14 / 136 / 0) beside the fact that all 100 of its
  meetings recorded exactly 3 ballots. It reads
  `audits/deduction-candidate/run-2026-09-16/` and writes nothing there.
- [x] `docs/artifacts.md` gains ONE registry row for the pair, class `(b)`, `in
  git`, sized `2 files` with no byte figure so a re-record forces no edit
  (`scripts/verify_ml_evidence.py:2853-2854`). That command cross-checks row
  keys, so `_IN_TREE_PROBES` (`:2754`) and `_IN_TREE_INVENTORY` (`:2810`) gain
  matching entries and it passes offline; `tasks/README.md:43`'s inventory
  sentence is recomputed. Planted: the row without its probe entry fails it.

## Constraints

No live provider call on any path, and no model is called by the scorer, its
tests or `--check`: the suite is a fold over committed bytes, the property D3
rests on. No held-out band is generated, drawn, rendered or printed; band
2100-2999 stays unseen, and no prefix, prompt or transcript text appears in any
output. The untracked `.env` is not read and `verify_ml_evidence.py --complete`
is not run.

No agent behaviour, prompt byte, schema field, detector or recorded byte
changes here, so no prompt version bump and no `DEFAULT_PROMPT_VERSIONS` edit
is in scope. The owner's rulings DO now intend changes to shipped default
behaviour, a departure from the previous default-OFF-lever rule, but that
departure belongs to the three substrate cards. `citation_relevance_version`
stays `None`: relevance is computed offline and the lever never goes on. Roles
are read for rows 2, 8 and 9 only, feed nothing back into any agent surface,
and nothing is written inside a recording directory.

Nothing under `audits/deduction-candidate/run-2026-09-16/` is edited, and the
appendix binds that path:
[the close card](close-deduction-candidate-evaluation.md) retires the accuracy
gate and shelves the candidate but must not relocate that archive. One writer
per file: this card owns `eval/process_scorecard.py`, its script and its tests,
and shares `docs/artifacts.md` and `tasks/README.md` with its two wave-1
siblings, which the coordinator reconciles at merge. No frontend file moves.

## Expected scope

`eval/process_scorecard.py` (new), a valid-target parse beside
`_parse_suspicion_graph` in `eval/meeting_quality.py`,
`scripts/publish_process_scorecard.py` (new), the generated
`docs/process-scorecard.md` and `docs/process-scorecard.json`,
`docs/artifacts.md` (one row), `scripts/verify_ml_evidence.py` (two table
entries), `tasks/README.md`'s inventory sentence, new
`tests/eval/test_process_scorecard.py`,
`tests/scripts/test_process_scorecard.py` and this card. Not in scope:
`agents/`, `meetings/`, `orchestrator/`, `engine/`, `llm/`, `experiments/`,
`frontend/`, every prompt template and every committed recording. Delivered on
`work/process-scorecard`, one pull request into `main`, merge commit or
fast-forward and never a squash, trailer
`Card: tasks/work/process-scorecard.md`.

Order, identical on all seven cards. WAVE 1 is parallel and changes no agent
behaviour: this card, [the spectator tour](spectator-tour-and-alternatives.md)
and [the evaluation close](close-deduction-candidate-evaluation.md); the close
merges FIRST so the substrate wave's `GENERATOR_SOURCES` edits owe no restamp
to a retired band. The SUBSTRATE WAVE is serial, all three moving the
`qwen3_6_27b` prompt stamps and the ballot or claim schema:
[alibi as a route](alibi-as-route.md), then
[grounded SKIP and guard labels](grounded-skip-and-guard-labels.md), then
[the weighing channel](ballot-weighing-channel.md). Then
[the re-record](process-rerecord.md), once. Deferred and in no card: the body
freshness band, an impostor who reports a body, the `docs/` front door.

## Record impact

No recording, report, DTO, metric, weight, fixture or prompt byte moves; no
experiment becomes ON; no adopting record is created. `verify_samples.sh` and
the four `build_sample_report.py --sample-dir <set> --check` runs recompute
exactly what they do today, because this card adds a SECOND, independent check
over a NEW artifact and touches neither the report shape nor the loader; no
version gating and no as-recorded read is needed for them.

Two new committed files are the change. Being produced by running something,
`docs/artifacts.md`'s boundary (`:9-15`) puts them in the registry as the
flattened measurement rows a page's cells are read from, class `(b)`
(`:40-50`). Class `(d)` is refused for the reason `tournament-eval-report.json`
is committed: a regenerated view whose bytes a gate pins is a record.
`audits/` is refused because this file is rewritten at every re-record, which
would churn the `audits/` row (`docs/artifacts.md:109`) and need an index row
(`scripts/check_doc_facts.py:2393`); `docs/` costs neither.

Stated rather than discovered: once
[the grounded SKIP card](grounded-skip-and-guard-labels.md) and
[the weighing channel](ballot-weighing-channel.md) land and
[the re-record](process-rerecord.md) runs, the SKIP rows move off zero and rows
2 and 9 stop being comparable across that boundary. The published file carries
its recording provenance so the two eras are labelled, never averaged. Row 2
keeps reading OLD bytes after the weighing card drops the rendered trust
column, because that card widens `_SUSPICION_GRAPH_ROW_RE`
(`eval/meeting_quality.py:326-329`) rather than re-scoring history.

## Validation

`uv run pytest tests/eval tests/scripts -q` (fake and replay doubles only, at
$0), `uv run python scripts/publish_process_scorecard.py --check`,
`uv run python scripts/validate_task_docs.py`,
`uv run python scripts/check_doc_facts.py`, `uv run lint-imports`,
`uv run python scripts/verify_ml_evidence.py` (offline; never `--complete`)
with `uv run pytest tests/scripts/test_verify_ml_evidence.py -q`,
`bash scripts/verify_samples.sh`, the four
`uv run python scripts/build_sample_report.py --sample-dir <set> --check` runs
over the two `replays/samples/` and two `replays/ml_corpus/` sets, and
`bash scripts/check.sh` run whole in a clean worktree rather than to the first
gate. Results reports the nine rows and names the one corrected cell against
the memo's section 4. No provider call is a check here.

## Results

Implemented on `work/process-scorecard`. The scorer is `eval/process_scorecard.py`,
the writer is `scripts/publish_process_scorecard.py`, and the published pair is
`docs/process-scorecard.md` + `docs/process-scorecard.json`. No agent behaviour,
prompt byte, schema field, detector or recorded byte moved; `citation_relevance_version`
stays `None` and relevance is computed offline. No provider was called on any path,
and `scripts/verify_ml_evidence.py --complete` was not run.

### Architecture and contract references

`docs/architecture.md`'s `eval/` boundary — pure analyzers over recorded
artifacts, no engine mutation — is where the scorer sits; the observation
firewall is untouched, because `eval/` may read `engine/` and `agents/` learns
nothing from this. AGENTS.md load-bearing rule 5 (invalid input raises, no
silent fallbacks) is why a replay whose state hashes do not reconstruct raises
`ProcessScorecardReconstructionError` instead of yielding a partial route, and
why an unresolvable claim tick is published as not-evaluable rather than scored
as a lie. This card's own Evidence section is the contract for rows 2 and 3;
[the direction memo](../direction-2026-09-19-process-over-outcome.md) sections
4, 5, 7, 8 and 12 are the source of the suite and of decision D1.

### Decisions

1. **Row 1 requires a citation to be PRESENT and to RESOLVE before aboutness is
   asked.** `citations_bear_on` is vacuously true when neither channel is cited,
   so asking it alone would score all 1,485 uncited SKIPs as grounded. The
   definition string says so; the planted pair
   (`test_a_skip_citing_a_turn_about_a_named_alternative_is_grounded` /
   `test_the_same_skip_with_its_citation_nulled_is_not_grounded`) is the proof.
2. **Row 2's zero-flag band is "the meeting minted NO contradiction at all",
   vent flags included.** Reading it as the non-vent census
   (`recorded_contradiction_flags`) gives 1,011/70 rather than 206/64, so the
   memo's band is the all-flags one. The published definition names the surface.
3. **The corrected cell, against the memo's section 4.** The follower
   role-correct column on `ml_corpus/9p2i` is **1,143 (96.1%)**, not the memo's
   1,137 (95.6%); the zero-flag follower cell is **176/206**, not 170/206. The
   same six ballots account for both, exactly as this card's Evidence predicted.
   Denominator (1,270), split (1,189 / 81 = 93.6% / 6.4%), deviator column
   (7 = 8.6%) and zero-flag deviators (1/64) land to the digit. Chance publishes
   as **0.303528** over those same 1,270 unambiguous ballots — 0.3035 to four
   decimals, and the memo's 0.303 to within 0.0006, which is the one figure of
   the five that does NOT land on the memo's digit (see the round-1 corrections
   below). The definition the card pins is what this publishes:
   crew EJECT ballots, recorded target, roles from the seeder, argmax over the
   voter's rendered rows INTERSECTED with that voter's rendered valid-target
   list, ties excluded and counted (92 on that set).
4. **Row 3 reproduces exactly and needed one convention written down.** Alibi
   ticks are AGENT-frame; `AGENT_CLOCK_OFFSET = 1` resolves a spoken tick `T`
   against engine tick `T - 1`, and agent tick 0 against the SEEDED pre-advance
   state of engine tick 0 (recorded in `walk_routes` as tick `-1`). Without that
   seeded frame, 15 tick lookups on the two 9p2i sets fall off the route and the
   envelope census reads 115 instead of 104. With it: **955 self-alibi claims,
   769 multi-tick, 104 envelope-false, 103 of those multi-tick, 2 strict-false,
   13 further alibi claims naming another player** — this card's Evidence to the
   digit. `test_the_agent_clock_offset_is_what_makes_the_census_hold` pins the
   convention on a planted route where the two frames disagree.
5. **Row 3 publishes one sub-count the card did not ask for.** A manufactured
   flag against a claim the route makes true at EVERY tick is a different defect
   from one against a truthfully-moving player compressed into a single-room
   envelope, and the pooled rate alone would read as one failure. Pooled over
   the two 9p2i sets, **158** flags are manufactured and only **8** rest on a
   wholly true claim; across all four sets it is **159** and **9**. The rest are
   the envelope artifact proper. Per set the wholly-true sub-count is
   `ml_corpus/9p2i` 6, `samples/9p2i` 2, `ml_corpus/4p1i` 1, `samples/4p1i` 0.
6. **Row 5 is role-blind by construction.** `decompose_ejection_channels`
   returns `None` unless the ejected player is a true impostor, so it cannot
   produce a role-blind mix; the bands come from the recorded flags plus the
   cited line's observation type, and role-correctness is reported beside each
   band. The decomposition nests exactly inside the memo's section 3 table:
   `ml_corpus/9p2i` vent 220/220, other contradiction flag 0/3, no flag 32/58
   (28/52 first-hand, 2/4 hearsay, 2/2 unevidenced); `samples/9p2i` vent 68/68,
   no flag 13/20 (11/17 first-hand plus 2/3 hearsay). The no-flag totals are the
   memo's; the round-1 correction to the `first_hand` rule below moved 8
   ejections into `hearsay` and changed no no-flag total.
7. **Rows 7 and 8 read the typed layer, and the marker census rides beside.**
   `guard_rewrite_reason` carries four classes on `ml_corpus/9p2i`
   (`under_gate_redirect` 57, `uncited_coerced` 6, `teammate_coerced` 5,
   `invalid_target` 2 = 70 of 2,516), while the redirect MARKER census sees 57.
   A ballot is non-authored when either channel says so — the typed field, or
   `_authored_target` unwinding a marker on a recording older than the fields.
   Citation-nulling markers are counted separately (10 on that set) and a ballot
   carrying both is counted among the rewrites, because the target moved.
8. **Row 6 publishes its limits inside the row.** It tests TOKENS, not
   propositions; an assertion and its negation score alike
   (`test_a_negated_assertion_passes_which_is_the_stated_limit`); and the memo's
   section 3 result on invented facts is two-method agreement between two
   graders, not this measurement. On today's bytes 0 of 6,796 extracted tokens
   are absent, which is a real reading of a weak test, not a strong result.
9. **Pooling adds counts and never averages rates.** Every cell is a count over
   disjoint recordings; the chance baseline is carried as an exact `Fraction`
   sum of per-ballot shares plus a ballot count, so pooling is order-free
   (`test_pooling_the_chance_baseline_is_exact_and_order_free`). Two pooled
   groups are published — all four sets, and the two 9p2i sets where the memo's
   pins live — beside the four per-set rows, with the recording provenance named
   so the pre-substrate-wave era is labelled and never averaged across the
   coming boundary.
10. **The appendix is labelled out of the headline and pools with nothing.** It
    reads `audits/deduction-candidate/run-2026-09-16/` and writes nothing there.
    Counts only: no prefix, prompt or transcript text enters either published
    file.

### The nine rows (pooled over all four committed sets)

| # | row | value |
| --- | --- | --- |
| 1 | grounded-decision rate, EJECT / SKIP / all | 2078/2146 = 0.9683 / 0/1485 = 0.0000 / 2078/3631 = 0.5723 |
| 2 | argmax-independence: deviating EJECTs | 116/1811 = 6.4%; role-correct followers 1602/1695 = 94.5% vs deviators 9/116 = 7.8%, chance 0.315503 |
| 3 | manufactured-contradiction rate | 159/192 = 0.8281 (32 not evaluable) |
| 4 | unexplained-decision rate | 20/3631 = 0.0055 |
| 5 | evidence-quality mix | vent_flag 333, first_hand 75, contradiction_flag 10, hearsay 8, unevidenced 3, over 429 ejections |
| 6 | rationale faithfulness (TOKENS) | 2874/2874 = 1.0000 (757 not evaluable) |
| 7 | agent-authored share | 3531/3631 = 0.9725 |
| 8 | wrong-but-believable rate | 383/2146 = 0.1785 — reported, never penalised |
| 9 | role-correct ejection rate | 383/429 = 0.8928 — reported beside, never a gate |

This card's Evidence ballot table reproduces exactly: `ml_corpus/9p2i` 1,499
EJECT / 1,498 cited / 1,017 SKIP / 0 cited / 999 with alternatives;
`samples/9p2i` 527 / 526 / 342 / 0 / 337; `samples/4p1i` 51 / 51 / 66 / 0 / 65;
`ml_corpus/4p1i` 69 / 69 / 60 / 0 / 60. All 3,631 ballots carry their voter's
prompt, so row 1's not-evaluable cell is **0**. The appendix reproduces as the
Acceptance states it: candidate (`combined_accounts`) 75 EJECT / 73 cited /
75 SKIP / 0 cited; reference (`repaired_clock`) 14 / 14 / 136 / 0; all 100
meetings recorded exactly 3 ballots.

### Verification

Every command below was run in this worktree at the implementation head, with
each exit code captured directly rather than through a pipe.

```
$ uv run python scripts/publish_process_scorecard.py
Wrote docs/process-scorecard.md and docs/process-scorecard.json: 3631 ballots over 672 meetings; grounded 2078/3631; deviating EJECTs 116/1811; manufactured flags 159/192; role-correctness is reported and gates nothing.

$ uv run python scripts/publish_process_scorecard.py --check
--check: docs/process-scorecard.md and docs/process-scorecard.json are consistent with the committed recordings.

$ uv run python scripts/validate_task_docs.py
Task docs validation passed: 390 historical phase tasks and 390 prompts; 73 work cards.

$ uv run python scripts/verify_ml_evidence.py
checks: 61 | OK 49 | FAIL 0 | ABSENT 7 | INFO 5
```

`uv run python scripts/check_doc_facts.py`, `uv run lint-imports`,
`uv run pytest tests/scripts/test_verify_ml_evidence.py -q`,
`bash scripts/verify_samples.sh`, the four
`uv run python scripts/build_sample_report.py --sample-dir <set> --check` runs
over `replays/samples/4p1i`, `replays/samples/9p2i`, `replays/ml_corpus/4p1i`
and `replays/ml_corpus/9p2i`, and `bash scripts/check.sh` run whole in this
clean worktree all pass. Their per-command counts are in the pull request's
`## Definition of done`. `verify_samples.sh` and the four `--check` runs
recompute exactly what they did before this card: it adds a SECOND, independent
check over a NEW artifact and touches neither the report shape nor the loader.
No provider call is a check here, and none was made.

### Planted and perturbed failures

Each new gate has a case proving it fails on the defect it claims to catch.
Three were demonstrated live (edit, run, restore); the rest are committed tests
whose halves differ in exactly the thing the row's definition names.

**1. One edited cell turns `--check` red** (live; restored afterwards). Setting
`pooled_9p2i.manufactured_contradiction.self_alibi_claims_strict_false` from 2
to 3 in the committed JSON:

```
$ uv run python scripts/publish_process_scorecard.py --check
--check: docs/process-scorecard.json is STALE — it does not match a recomputation from the committed recordings. Re-run `uv run python scripts/publish_process_scorecard.py` and commit the result.
EXIT=1
```

Restoring the byte returns it to `EXIT=0`. The same shape is committed as
`tests/scripts/test_process_scorecard.py::test_one_edited_cell_turns_check_red`,
which publishes a planted scorecard into a temp tree, verifies green, moves one
integer and asserts red — so the gate is exercised end to end with no second
walk over the recordings.

**2. The registry row without its probe entry fails `verify_ml_evidence.py`**
(live; restored afterwards). Deleting the `docs/process-scorecard.md` entry from
`_IN_TREE_PROBES` while the row stays in `docs/artifacts.md`:

```
$ uv run python scripts/verify_ml_evidence.py      # EXIT=1
[ FAIL ] registry coverage
          measured : 20 probed row(s)
          committed: 21 registry row(s)
          source   : docs/artifacts.md
          note     : in docs/artifacts.md but not probed here: docs/process-scorecard.md
          note     : probed here but not in docs/artifacts.md: (none)
```

Restoring the entry returns `checks: 61 | OK 49 | FAIL 0` and `EXIT=0`.

**3. The writer cannot target a recording.** Four parametrized destinations — a
`samples/4p1i` replay, a `samples/9p2i` roster, the `ml_corpus/9p2i` committed
report and the fifth run's `RESULTS.md` — are each refused by
`preflight_report_output` with `ValueError: ... overlaps ...` BEFORE
`compute_process_scorecard` runs, and the test asserts the source bytes are
unchanged after the refusal
(`test_the_writer_refuses_a_recording_destination_before_computing`). A
companion pins that every file under the fifth run's archive is on the protected
list.

**4. Per-row planted pairs** (`tests/eval/test_process_scorecard.py`; 57 tests
across it and its `tests/scripts/` sibling, none of which walks a committed set
except the one committed-bytes `--check`):

* Row 1 — a SKIP citing a turn about a named alternative scores grounded; the
  same SKIP with the citation nulled does not. An EJECT citing a turn that
  resolves but names somebody else is NOT grounded (aboutness, not resolution).
* Row 2 — one follower and one deviator whose role-correctness differs (the
  follower onto the impostor, the deviator onto a crewmate); a tie lands in the
  excluded count and in neither column; a higher rendered row OUTSIDE the valid
  list cannot win the argmax; an impostor voter is outside the denominator; and
  chance is measured over the unambiguous ballots alone, on three ballots with
  three different impostor shares
  (`test_chance_is_measured_over_the_unambiguous_ballots_and_no_others`), with
  the perturbed half proving `scorecard_from_tally` REFUSES a wider chance
  population outright
  (`test_a_chance_population_wider_than_the_denominator_is_refused`).
* Row 3 — an envelope alibi true at its first tick mints a manufactured flag; a
  flat single-tick lie does not; a wholly-true claim is manufactured and
  reported separately; a flag naming no self-alibi speaker and a claim reaching
  past the walk are not-evaluable rather than false; a vent flag is outside the
  alibi denominator; the clock offset is pinned on a route where the two frames
  disagree.
* Row 4 — a SKIP naming no player anywhere is unexplained; the same SKIP naming
  a player only in prose is not; an EJECT whose citation does not resolve is;
  and a teammate-coerced SKIP whose ONLY player token is the guard's own marker
  is unexplained while the same coerced SKIP with a model body naming a player
  is not (`test_a_coerced_skip_whose_only_player_token_is_the_guard_marker` /
  `test_the_same_coerced_skip_with_a_model_body_naming_a_player_is_not`), with a
  parse-defaulted SKIP pinned beside them.
* Row 5 — a vent flag outranks every other band; an unflagged ejection on a
  cited observation is first-hand, on an accusation turn is hearsay, and with no
  resolving citation is unevidenced; a cited turn whose observation NAMES the
  ejected player is first-hand and the same turn with that one field moved to
  another player is not
  (`test_a_cited_turn_observing_the_ejected_player_is_first_hand` /
  `test_a_cited_turn_observing_somebody_else_is_not_first_hand`); the ejected
  player's own turn is not a first-hand route; an innocent ejected on a vent
  flag still lands in the vent band with role-correct 0 beside it.
* Row 6 — a rationale naming an absent room fails; the same rationale with the
  held room passes; a negated assertion PASSES, which is the stated limit; a
  rationale with no extractable token is not-evaluable with a `None` rate.
* Row 7 — a ballot carrying `under_gate_redirect` leaves the authored share; one
  carrying only a nulled-citation marker does not; a marker rewrite with no
  typed reason still leaves the share (the pre-typed-field fallback); and
  `uncited_coerced`, which prepends no target repr, is counted by the typed
  layer although the marker census cannot see it.
* Row 8 — a grounded wrong call is wrong-but-believable; the same wrong call
  resting on a manufactured flag is not; a role-correct EJECT never is.
* Row 9 and pooling — the row is labelled as no gate; pooling two groups adds
  counts and recomputes the rate (1 of 4, not the 0.667 a mean of rates would
  publish); the chance baseline pools identically in either order.

### Limitations

1. **Row 6 is weak, and says so.** A token test cannot see an invented RELATION
   between present tokens, so its 1.0000 is the absence of a specific, narrow
   defect and not evidence that rationales are faithful. The memo's section 3
   result stands on two-method agreement between two graders; this row neither
   confirms nor replaces it.
2. **Row 1's SKIP cell is structurally zero and will move.** The voter is told a
   SKIP needs no citation (`vote_ballot.j2:268`), so 0/1,485 is a property of the
   prompt, not of the agent. Once
   [the grounded-SKIP card](grounded-skip-and-guard-labels.md) lands and
   [the re-record](process-rerecord.md) runs, rows 1, 2 and 9 stop being
   comparable across that boundary; the published provenance labels the era so
   the two are never averaged.
3. **Row 3 is not a measure of intent.** It says a flag's basis is an account
   the engine route supports at some tick, which is a defect in the claim
   SCHEMA, not a verdict on the detector or the speaker. It also cannot clear a
   flag whose subject lied at every tick — that flag is evidence.
4. **Row 5's `first_hand` band trusts the cited turn's SHAPE.** A turn carrying
   a structured observation that NAMES the ejected player reads as first-hand;
   whether that observation was true is row 3's and the substrate wave's
   business, not this band's. Naming is the whole-token
   `meetings.citation_relevance.names_player` test over the observation's dumped
   structure, so an observation about somebody else — and a turn merely SPOKEN
   by the ejected player — is not a first-hand account of them and falls through
   to `hearsay` or `unevidenced`.
5. **Roles are read for rows 2, 5, 8 and 9 only**, come from the seeder, feed
   nothing back into any agent surface, and gate nothing. Row 8's direction is
   deliberately unstated.
6. **The argmax row cannot prove the voter read the graph.** It measures whether
   the recorded call equals the arithmetic the engine handed it. The deviation
   column is what carries the finding, and the 111 ties across the four sets are
   excluded and published rather than assigned to either side.
7. **`tests/eval/__init__.py` was added.** `tests/eval/` and `tests/scripts/`
   both gained a `test_process_scorecard.py`, and without a package marker
   pytest cannot collect two modules with the same basename. This follows the
   existing `tests/api/__init__.py` precedent, which resolves the same collision
   for `test_schemas.py`.

### Review corrections, round 1 (2026-09-19)

Three independent lenses raised **seven findings** over the implementation head
`cb2b861b`. All seven are VALID and all seven are repaired; none needed a
refutation. They are seven statements of **four defects** — two of them were
raised twice and three times over — and each defect is one `- [x] Review
correction:` item at the head of `## Acceptance`:

| defect | raised by | repair |
| --- | --- | --- |
| row 4 read the vote guard's own marker text as the agent naming a player | correctness lens | strip by provenance before the player-token test |
| row 2's chance baseline was accumulated over ties and no-row ballots too | correctness lens; documentation/Codex lens (Codex comment 1) | accumulate below both returns |
| the prose paired the two-set manufactured count with the four-set wholly-true sub-count (9 where the artifact says 8) | correctness lens; scope/record-integrity lens; documentation/Codex lens | correct the sentence in Decision 5 and in the PR body |
| row 5's `first_hand` band ignored whether the observation names the ejected player | documentation/Codex lens (Codex comment 2) | require an observation naming them |

**1. Row 4 now reads the model-authored remainder.** The player-token test ran
over the raw `rationale_text`, guard markers included, so a teammate-coerced
SKIP — whose marker preserves the coerced target's id and whose body the guard
then replaces with `TEAMMATE_COERCED_VOTE_RATIONALE` — escaped the counter on a
`p-N` no agent wrote. `_model_authored_rationale` now cuts the anchored,
repr-aware marker chain off first, by PROVENANCE rather than by pattern: the
same `eval.deduction_metrics._scan_marker_chain` every other guard-origin cell
in the package reads, and the same cut `api/replay_loader.py` makes for
`rationale_text_clean`. The row's published definition says so. Published
movement, per set and pooled:

| set | unexplained, was → now | SKIPs naming no player | SKIPs naming one in prose |
| --- | --- | --- | --- |
| `ml_corpus/9p2i` | 12 → **15** | 11 → 14 | 531 → 524 |
| `samples/9p2i` | 2 → **4** | 1 → 3 | 190 → 186 |
| `ml_corpus/4p1i` | 0 → 0 | 0 → 0 | 17 → 17 |
| `samples/4p1i` | 1 → 1 | 1 → 1 | 21 → 21 |
| pooled, two 9p2i sets | 14 → **19** | 12 → 17 | 721 → 710 |
| pooled, all four sets | 15 → **20** | 13 → 18 | 759 → 748 |

**2. Row 2's chance baseline is measured over the row's own denominator.** The
accumulator ran before the no-row and tie returns, so `ml_corpus/9p2i` summed
1,362 shares (1,270 unambiguous plus 92 ties) and divided by 1,362 while the
split's denominator was 1,270 — a population the published definition does not
name and no cell on the row accounts for. Moving it below both returns makes the
two agree, and `scorecard_from_tally` now RAISES rather than publish a chance
population wider than the row's denominator — a new invariant gate with its own
perturbed case, `test_a_chance_population_wider_than_the_denominator_is_refused`,
which adds the one ballot a tie would have contributed and asserts the build
turns red. `ml_corpus/9p2i` chance is now **0.303528**, the 0.3035 Decision 3
quotes; `samples/9p2i` 0.305845 → 0.305058; pooled over the two 9p2i sets
0.303844 → 0.303918; pooled over all four 0.314764 → **0.315503**. Both 4p1i
sets stay 0.5 (no ties there). The memo's section 4 figure is 0.303 at three
decimals; the published 0.303528 differs from it by under 0.0006, and Decision 3
now says that rather than claiming chance lands on the memo's digit — the other
four cells of that decision still do. This Evidence section's sentence
"Denominator, split, deviator column and chance land to the digit" is the
pre-implementation contract and is SUPERSEDED for chance alone by this
paragraph; the other three cells it names are unaffected, and nothing in the
memo's argument turns on the difference (the zero-flag deviation rate stays far
below chance either way).

**3. The wholly-true sub-count is attributed to its own group.** Decision 5 and
the PR body read "158 flags are manufactured and only 9 rest on a wholly true
claim", pairing the two-set numerator with the four-set sub-count.
`docs/process-scorecard.json` is authoritative and unchanged on this point:
`pooled_9p2i.manufactured_contradiction` is 158 with **8** wholly-true, and the
all-four `pooled` group is 159 with **9**. Decision 5 now states both pools and
the per-set split (`ml_corpus/9p2i` 6, `samples/9p2i` 2, `ml_corpus/4p1i` 1,
`samples/4p1i` 0); the PR body's Decisions item 3 is corrected to match. No code
and no artifact byte moved for this one — it was prose against a correct
artifact.

**4. Row 5's `first_hand` band asks whether the observation names them.** The
band tested only that `turn.observations` was non-empty, so a cited turn whose
one observation placed somebody else — and a turn merely SPOKEN by the ejected
player — read as first-hand evidence about a player no observation mentions.
That is not what the published definition, Limitation 4 or the memo's section 3
nesting says. `_observes_player` now requires an observation whose dumped
structure names the ejected player by the whole-token
`meetings.citation_relevance.names_player` rule, walked as a structure for the
reason `turn_bears_on` gives. Eight ejections move from `first_hand` to
`hearsay`, a band that was empty on every set before:

| set | first_hand, was → now | hearsay | role-correct first_hand |
| --- | --- | --- | --- |
| `ml_corpus/9p2i` | 56 → **52** | 0 → 4 (2 role-correct) | 30 → 28 |
| `samples/9p2i` | 20 → **17** | 0 → 3 (2 role-correct) | 13 → 11 |
| `ml_corpus/4p1i` | 2 → 2 | 0 | 2 → 2 |
| `samples/4p1i` | 5 → **4** | 0 → 1 (0 role-correct) | 1 → 1 |
| pooled, all four sets | 83 → **75** | 0 → 8 (4 role-correct) | 46 → 42 |

Every no-flag TOTAL is unchanged, so Decision 6's claim that the mix nests
inside the memo's section 3 table still holds to the digit
(`ml_corpus/9p2i` no flag 32/58; `samples/9p2i` 13/20) — only the split inside
that band moved.

**What did NOT move.** No agent behaviour, prompt byte, schema field, detector
or recorded byte, and no `audits/` or `tests/fixtures/` byte; the two changed
files are the two published `docs/process-scorecard.*` the card already
registers, whose `docs/artifacts.md` row is deliberately sized `2 files` with no
byte figure so a republication forces no inventory edit. Rows 1, 3, 6, 7, 8 and
9 are byte-identical. Row 6 deliberately still reads `rationale_text` WHOLE:
it asks whether every token in the RECORDED text is one the voter held, and a
marker's preserved id always is — the contrast with row 4's authorship question
is now stated in both definition strings.

**Verification at this head.** Every command was re-run in this worktree with
its exit code captured directly, never through a pipe:

```
$ uv run python scripts/publish_process_scorecard.py
Wrote docs/process-scorecard.md and docs/process-scorecard.json: 3631 ballots over 672 meetings; grounded 2078/3631; deviating EJECTs 116/1811; manufactured flags 159/192; role-correctness is reported and gates nothing.

$ uv run python scripts/publish_process_scorecard.py --check
--check: docs/process-scorecard.md and docs/process-scorecard.json are consistent with the committed recordings.

$ uv run python scripts/validate_task_docs.py
Task docs validation passed: 390 historical phase tasks and 390 prompts; 73 work cards.

$ uv run python scripts/verify_ml_evidence.py
checks: 61 | OK 49 | FAIL 0 | ABSENT 7 | INFO 5
```

`uv run pytest tests/eval tests/scripts -q` (49 planted cases in
`tests/eval/test_process_scorecard.py`, eight of them new), `uv run
python scripts/check_doc_facts.py`, `uv run lint-imports`, `uv run pytest
tests/scripts/test_verify_ml_evidence.py -q` (80 passed),
`bash scripts/verify_samples.sh` (50 + 50 + 50 + 150 reconstructed clean) and
the four `uv run python scripts/build_sample_report.py --sample-dir <set>
--check` runs all pass. `bash scripts/check.sh` run whole in this worktree
returns **EXIT=0**: ruff clean, `lint-imports` 4 kept / 0 broken, 390 phase
tasks + 390 prompts + 73 work cards, mypy over 489 source files, **8044 passed,
20 skipped, 3 xfailed**, frontend 19 test files / 515 tests passed and the
build green. One earlier parallel run of that script tripped
`tests/orchestrator/test_recording_replacement.py::test_writer_construction_failure_restores_the_previous_pair`
(`assert len(closed_replays) == 1` saw 2). It is unrelated to this card — the
diff touches no `orchestrator/` byte — and it is scheduling-dependent exactly as
`check.sh:16-18` describes: the file, `tests/orchestrator` and three
consecutive `-n auto --dist loadfile` runs over that directory all pass, and the
test patches `ReplayLog.close` on the CLASS, so it counts every close in its
worker rather than its own. It is filed separately and nothing here depends on
it. The record-impact
statement is unchanged and re-demonstrated: `verify_samples.sh` and the four
`--check` runs recompute exactly what they did before this card. No provider
call is a check here, and none was made.
