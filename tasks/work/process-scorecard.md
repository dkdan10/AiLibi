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

- [x] Review correction: row 3's alibi-kind filter IS the census that owns it.
  `ALIBI_FLAG_KINDS` said it was "read from the owning census in
  `eval.alibi_fabrication`" and then re-listed the three kinds by hand with
  nothing tying the two together, so that census could gain or retire a kind and
  the manufactured-contradiction row would drift in silence. The owning constant
  is now public (`eval.alibi_fabrication.ALIBI_CONTRADICTION_KINDS`, in its
  `__all__`) and `eval/process_scorecard.py` imports it: `ALIBI_FLAG_KINDS` is
  the SAME frozenset object, so there is one source of truth and the comment now
  states what the code does. Pinned by
  `tests/eval/test_process_scorecard.py::test_the_alibi_kind_filter_is_the_owning_census_itself`,
  which asserts identity (`is`, not `==`, since a hand-written copy compares
  equal today) and that the shared set is exactly the `alibi_*` members of
  `meetings.schemas.ContradictionRef`'s `kind` Literal. Both halves were planted
  live. No published figure moves.
- [x] Review correction: rows 4 and 7 cut the rationale by PROVENANCE, which is
  what they always claimed. `_authored_by_the_agent` and
  `_model_authored_rationale` scanned the WHOLE `rationale_text`, so a model
  body that OPENS with marker-shaped prose — at position 0, where a guard marker
  would sit — was read as a guard rewrite and left the authored share. The scan
  now runs over the marker region
  `eval.deduction_metrics._split_rationale` establishes from the voter's own
  pre-guard vote response, the region `_authored_target` documents its `chain`
  argument as, and `eval/deduction_metrics.py:2668-2669` reads the same way.
  Proved by the planted pair
  `tests/eval/test_process_scorecard.py::test_a_model_body_that_opens_with_marker_shaped_prose_stays_authored`
  / `::test_the_same_legacy_ballot_whose_marker_the_guard_wrote_leaves_the_share`,
  whose halves differ in exactly who wrote the marker. 0 such ballots on today's
  bytes, so no published cell moves; rows 4 and 7 publish the corrected
  mechanism in their own definition strings.
- [x] Review correction: the missing-prompt non-coverage count is partitioned by
  ballot KIND. One `no_prompt_ballots` fed the EJECT cell, the SKIP cell and
  wrong-but-believable alike, so one promptless EJECT reported a fully recorded
  SKIP cell as having measured nothing — against `RateCell`'s own rule that
  `not_evaluable` publishes separately so a reader can tell a cell that measured
  nothing from one that measured a zero. `no_prompt_eject_ballots` and
  `no_prompt_skip_ballots` now feed their own cells; `grounded_all` and the
  unexplained row keep the sum, because their denominator is every ballot.
  Proved by the pair
  `::test_the_missing_prompt_count_is_partitioned_by_ballot_kind` /
  `::test_the_partition_holds_with_the_kinds_swapped`, which assert the sibling
  cell stays 0. 0 promptless ballots on all four sets, so no published cell
  moves.
- [x] Review correction: a game with no reconstructed route RAISES rather than
  folding against an empty one. `fold_set` took `inputs.routes.get(game.seed,
  {})`, so an absent seed silently became "this game stood still" — every alibi
  tick unresolvable and row 3's census 0, which AGENTS.md rule 5 (invalid input
  raises, no silent fallbacks) is exactly the rule against, and which this
  card's own Results cites as why a non-reconstructing replay raises
  `ProcessScorecardReconstructionError`. It is unreachable through
  `load_set_inputs` (`walk_routes` keys every seed on disk), so it is pinned by
  a planted case rather than by a figure:
  `::test_a_game_with_no_reconstructed_route_is_refused_not_folded`, beside the
  new sibling `::test_a_replay_that_does_not_reconstruct_is_refused` for the
  walk-violation path.
- [x] Review correction: `RateCell` refuses a published rate that contradicts
  its own counts. `_counts_are_coherent` checked only non-negativity, numerator
  ≤ denominator and the None-iff-zero-denominator rule, so
  `RateCell(numerator=1, denominator=2, rate=0.9)` was accepted and the same
  shape round-tripped through `RateCell.model_validate` from JSON — the typed
  boundary every published rate crosses, and the model a later spectator surface
  will parse `docs/process-scorecard.json` with. A rate must now equal
  `round(numerator / denominator, 6)`. Pinned by the perturbed
  `::test_a_rate_that_contradicts_its_own_counts_is_refused`, which builds the
  inconsistent cell both in process and from JSON, the way the chance-population
  invariant is pinned.
- [x] Review correction: the writer's destination guard refuses by CONTAINMENT
  and not by file identity. `protected_inputs` now carries the recording
  DIRECTORIES — `replays/`, each committed set and the fifth run's archive —
  beside the 741 files, so `_check_destination`'s parent test refuses a
  destination that does not exist YET. Before this the files-only list accepted
  `replays/new-process-scorecard.md`,
  `replays/samples/9p2i/new-scorecard.md` and
  `audits/deduction-candidate/run-2026-09-16/new-scorecard.md`, and the
  preflight would have created each one inside a recording location. Proved by
  the three NEW parameters of
  `tests/scripts/test_process_scorecard.py::test_the_writer_refuses_a_recording_destination_before_computing`
  (which also assert the refusal leaves nothing behind) and by the perturbed
  `::test_the_recording_roots_are_protected_by_containment`, which shows the
  pre-correction files-only list accepting the same destination.
- [x] Review correction: every figure names the head it belongs to. The round-1
  repairs landed at `5303ce5b`, one commit past the `cb2b861b` a round-1 lens
  was handed, so that lens's four "does not reproduce" reports were readings of
  a superseded head — all four reproduce at `5303ce5b` and at this one. The pull
  request body is rewritten against the pushed head with `gh pr edit
  --body-file`, this `## Results` dates each round, and the test count it
  publishes is **61** across the two modules (49 + 12) rather than round 1's 57.
  Reproduced by `uv run python scripts/publish_process_scorecard.py --check` and
  `uv run pytest tests/eval/test_process_scorecard.py tests/scripts/test_process_scorecard.py -q`.
- [x] Review correction: row 4 no longer reads the vote guard's own marker text
  as the agent naming a player. The player-token test runs over the
  MODEL-AUTHORED remainder — the marker region
  `eval.deduction_metrics._split_rationale` establishes and
  `_scan_marker_chain` consumes (round 1 cut the anchored chain out of the WHOLE
  record, which is a pattern and not a provenance; corrected in round 3 below),
  the same cut
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

**3. The writer cannot target a recording.** Seven parametrized destinations are
each refused by `preflight_report_output` with `ValueError: ... overlaps ...`
BEFORE `compute_process_scorecard` runs
(`test_the_writer_refuses_a_recording_destination_before_computing`). Four
EXIST — a `samples/4p1i` replay, a `samples/9p2i` roster, the `ml_corpus/9p2i`
committed report and the fifth run's `RESULTS.md` — and the test asserts their
bytes are unchanged after the refusal. Three do NOT exist yet and are refused by
containment alone (round-2 correction below); the test asserts each is still
absent afterwards, because the preflight CREATES its destination as an
exclusivity probe once the containment test has passed. Two companions pin the
list itself: every file under the fifth run's archive is on it, and the
recording roots are on it with the perturbed half showing the files-only list
accepting the same destination.

**4. Per-row planted pairs** (`tests/eval/test_process_scorecard.py`; 68 tests
across it and its `tests/scripts/` sibling — 56 and 12 — none of which walks a
committed set except the one committed-bytes `--check`):

* Row 1 — a SKIP citing a turn about a named alternative scores grounded; the
  same SKIP with the citation nulled does not. An EJECT citing a turn that
  resolves but names somebody else is NOT grounded (aboutness, not resolution).
  The missing-prompt count is partitioned by KIND: one promptless EJECT beside a
  fully recorded SKIP leaves the SKIP cell's not-evaluable at 0, and the pair
  swaps the kinds to prove it is the kind and not the position
  (`test_the_missing_prompt_count_is_partitioned_by_ballot_kind` /
  `test_the_partition_holds_with_the_kinds_swapped`).
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
  typed reason still leaves the share (the pre-typed-field fallback);
  `uncited_coerced`, which prepends no target repr, is counted by the typed
  layer although the marker census cannot see it; and a legacy ballot whose
  MODEL body opens with the redirect literal STAYS in the share while the same
  bytes with the guard as the marker's author leave it
  (`test_a_model_body_that_opens_with_marker_shaped_prose_stays_authored` /
  `test_the_same_legacy_ballot_whose_marker_the_guard_wrote_leaves_the_share`) —
  the halves differ in exactly who wrote the marker.
* Row 8 — a grounded wrong call is wrong-but-believable; the same wrong call
  resting on a manufactured flag is not; a role-correct EJECT never is.
* Row 9 and pooling — the row is labelled as no gate; pooling two groups adds
  counts and recomputes the rate (1 of 4, not the 0.667 a mean of rates would
  publish); the chance baseline pools identically in either order.
* The typed boundary and the fold's own contract — a `RateCell` whose published
  rate is not its own counts is REFUSED, built in process and validated from
  JSON alike (`test_a_rate_that_contradicts_its_own_counts_is_refused`); a game
  whose seed the route table does not carry raises rather than folding against
  an empty route, with the same game keyed as the adverse half
  (`test_a_game_with_no_reconstructed_route_is_refused_not_folded`); and a
  profile violation raises through the same error
  (`test_a_replay_that_does_not_reconstruct_is_refused`).

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
`p-N` no agent wrote. `_model_authored_rationale` now cuts the marker chain off
first. **The mechanism sentence this paragraph carried is SUPERSEDED by round 3
below**: round 1 cut the anchored chain out of the WHOLE recorded rationale,
which is a cut by PATTERN, while the claim written here — and in the row's
published definition — was a cut by PROVENANCE. Round 3 makes the code match
the claim, over the marker region
`eval.deduction_metrics._split_rationale` establishes from the voter's own
pre-guard body, which is what every other guard-origin cell in the package
reads and what `api/replay_loader.py` cuts for `rationale_text_clean`. The
published movement below is round 1's and is unaffected: no committed ballot's
recorded body opens with marker-shaped prose, so the two cuts agree to the byte
on these recordings. Published
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

### Review corrections, round 2 (2026-09-20)

The round-1 lens sweep was re-read against the PUSHED head `5303ce5b` — the
head the corrections above landed at — and raised **two further findings**.
Both are VALID; neither needed a refutation. One is a real gap the round-1 pass
did not close, and one is a head-accounting repair:

| defect | raised by | repair |
| --- | --- | --- |
| the destination guard protected FILES, so a destination that does not exist yet inside a recording location was ACCEPTED | correctness lens; documentation/Codex lens | put the recording ROOTS on the protected list |
| four figures were reported as not reproducing at `cb2b861b` although the round-1 repairs had already moved them at `5303ce5b` | documentation/Codex lens | re-point the pull request body at the pushed head and date each round here |

**1. The writer is CONTAINED, not merely alias-checked.** `protected_inputs`
enumerated files — `replays/**` plus every byte the fold reads — and
`_check_destination` (`scripts/_report_output.py:12-32`) refuses a destination
that equals a protected path or sits under one. A path that did not exist
matched no file, so the guard left a hole exactly where the Acceptance claimed
there was none: aimed at `replays/samples/9p2i/new-scorecard.md` the writer
accepted the destination, and `preflight_report_output` would have CREATED it
inside a recording set (it creates the file as an exclusivity probe and unlinks
it again, so the damage is a new byte in a recording directory rather than an
overwritten one — still a writer reaching into the bytes it reads). The list
now carries the recording DIRECTORIES as well: `replays/`, each of the four
committed sets and the fifth run's archive, named once as `RECORDINGS_ROOT` /
`COMMITTED_SETS` / `FIFTH_RUN_ARCHIVE` in `eval/process_scorecard.py`, so
CONTAINMENT — a protected path among the destination's parents — is what
refuses, created or not. 741 protected entries become 747; nothing else about
the writer moves, and republishing produces byte-identical files. Both halves
stay, because they catch different things: containment cannot see a HARD LINK
to a recording placed outside the recording tree — that path resolves to itself
and is caught only by `_check_destination`'s `samefile` probe against the
recording file.

The perturbation is the gate turning red on exactly this defect (live: edit,
run, restore). With the roots taken back off the list:

```
$ uv run pytest tests/scripts/test_process_scorecard.py -q
FAILED ...::test_the_writer_refuses_a_recording_destination_before_computing[replays/new-process-scorecard.md]
FAILED ...::test_the_writer_refuses_a_recording_destination_before_computing[replays/samples/9p2i/new-scorecard.md]
FAILED ...::test_the_writer_refuses_a_recording_destination_before_computing[audits/deduction-candidate/run-2026-09-16/new-scorecard.md]
FAILED ...::test_the_recording_roots_are_protected_by_containment
4 failed, 8 passed in 10.17s
EXIT=1
```

and restored:

```
$ uv run pytest tests/scripts/test_process_scorecard.py -q
12 passed in 8.26s
EXIT=0
```

`test_the_recording_roots_are_protected_by_containment` carries that planted
defect as a committed case: it feeds `_check_destination` the pre-correction,
files-only half of the list and asserts the same destination is ACCEPTED, then
feeds it the whole list and asserts the refusal. The three new parameters of
the refusal test also assert the destination is still ABSENT afterwards, which
is what a files-only list could not promise. The sibling writer
`scripts/measure_reasoning_evidence.py` builds its protected list the same
files-only way through `eval.reasoning_evidence.scorecard_source_paths`; that is
another card's file under the one-writer rule and is NOT touched here, but the
same containment repair applies to it and is stated so it is not lost.

**2. Each figure now names its head.** A round-1 lens was handed `cb2b861b`
while `5303ce5b` was already the pull request's head, and reported four body
figures — unexplained 20/3631, `first_hand` 75 with a `hearsay` 8 band, pooled
chance 0.315503, and the test count — as not reproducing. They do not reproduce
at `cb2b861b` because they ARE the round-1 corrections above; all four reproduce
at `5303ce5b` and at this head, from `docs/process-scorecard.json` through
`uv run python scripts/publish_process_scorecard.py --check`. The one figure
that genuinely moved is the test count: round 1 published **57** across the two
modules and round 2 makes it **61** (`tests/eval/test_process_scorecard.py` 49,
unchanged; `tests/scripts/test_process_scorecard.py` 8 to 12). The pull request
body is rewritten against the pushed head, and the "Planted and perturbed
failures" list above now reads seven refused destinations rather than four.

**What did NOT move.** No agent behaviour, prompt byte, schema field, detector
or recorded byte; no `audits/` and no `tests/fixtures/` byte; and no published
scorecard byte at all — `docs/process-scorecard.md` and
`docs/process-scorecard.json` are identical before and after this round, because
the repair is to the writer's destination guard and not to the fold. All nine
rows are byte-identical to round 1, and no `docs/artifacts.md` inventory row is
recomputed because no registry-covered byte moved.

**Verification at this head.** Every command was re-run in this worktree with
its exit code captured directly, never through a pipe:

```
$ uv run python scripts/publish_process_scorecard.py --check
--check: docs/process-scorecard.md and docs/process-scorecard.json are consistent with the committed recordings.
EXIT=0

$ uv run pytest tests/eval/test_process_scorecard.py tests/scripts/test_process_scorecard.py -q
61 passed in 8.22s
EXIT=0

$ uv run python scripts/validate_task_docs.py
Task docs validation passed: 390 historical phase tasks and 390 prompts; 73 work cards.
EXIT=0

$ uv run python scripts/verify_ml_evidence.py
checks: 61 | OK 49 | FAIL 0 | ABSENT 7 | INFO 5
EXIT=0
```

`uv run pytest tests/eval tests/scripts -q` (**2537 passed, 1 skipped**),
`uv run python scripts/check_doc_facts.py`, `uv run lint-imports` (4 kept, 0
broken), `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` (80
passed), `bash scripts/verify_samples.sh` (50 + 50 verified clean) and the four
`uv run python scripts/build_sample_report.py --sample-dir <set> --check` runs
all pass. `bash scripts/check.sh` run whole in this worktree returns
**EXIT=0**: ruff clean, `lint-imports` 4 kept / 0 broken, 390 phase tasks + 390
prompts + 73 work cards, mypy over 489 source files, **8048 passed, 20 skipped,
3 xfailed**, frontend 19 test files / 515 tests passed and the build green.

One earlier run of that script at this head returned EXIT=1 on
`tests/orchestrator/test_run_limits.py::test_wall_deadline_cancels_meeting_and_retains_success`
(`assert provider.attempts == 2` saw 0). It is unrelated to this card and
load-dependent, not a regression: the diff touches no `orchestrator/` byte and
that test imports nothing this card changes; the test asserts that a 0.25-second
`RunDeadline` still reaches the provider twice, and it failed while the machine
carried a load average near 100 on 10 cores (that gate run took 44 minutes
against this one's 6). It reproduces at the PRISTINE head under the same load
and disappears at both heads when the load drops: three consecutive
`uv run pytest tests/orchestrator -q -n auto --dist loadfile` runs pass with the
change applied and three pass with it reverted, as does the file alone. It is a
sibling of the `test_recording_replacement.py` flake round 1 recorded and is
filed the same way; nothing here depends on it. The record-impact statement is
unchanged and re-demonstrated. No provider call is a check here, and none was
made.

### Review corrections, round 3 (2026-09-20)

A live Codex pass over the pushed head `b8a2c622` raised **four findings**. All
four are VALID and all four are repaired; none needed a refutation. Three are
rule-5 or typed-boundary holes that no committed byte reaches today, and one is
a mechanism that did not match the claim its own row publishes:

| defect | raised by | repair |
| --- | --- | --- |
| rows 4 and 7 scanned the WHOLE rationale, so marker-shaped MODEL prose at position 0 read as a guard rewrite | documentation/Codex lens | scan the provenance-established marker region |
| the missing-prompt non-coverage count was not partitioned by ballot kind | documentation/Codex lens | tally and publish it per kind |
| a game absent from the route table folded against an EMPTY route | documentation/Codex lens | raise, naming the seed |
| `RateCell` accepted a published rate that contradicts its own counts | documentation/Codex lens | require the rate to be the quotient |

**1. The cut is by provenance now, not only in prose.** `_authored_by_the_agent`
and `_model_authored_rationale` called `_scan_marker_chain(ballot.rationale_text)`
— the ANCHORED chain over the whole record. Anchoring is a shape, not an author:
a model body that OPENS by quoting the redirect literal sits at position 0
exactly where the guard's marker would, so such a ballot was unwound as a guard
rewrite and left the authored share, and row 4 then read the voter's own opening
words as machinery. `eval/deduction_metrics.py`'s `_MarkerChain` says every
guard-origin cell reads the PROVENANCE-established marker region only, and
`_authored_target` documents its `chain` argument as the scan of that region;
`eval/deduction_metrics.py:2668-2669` does exactly that. This card's own round-1
correction claimed the same mechanism and shipped the other one — that paragraph
is marked SUPERSEDED above, and the row 4 and row 7 definition strings now name
`_split_rationale` as the boundary. `_guard_marker_chain` is the one place the
cut is made, from each voter's PRE-GUARD vote body recovered by
`_model_authored_bodies`, and `_fold_meeting` passes one chain to every
guard-origin cell (authored share, marker-unwound fallback, citation-nulled
sub-count, row 4's player-token test). A record whose boundary cannot be
established yields an EMPTY marker region, which is the published under-count
direction `guard_provenance_unverifiable_ballots` already carries rather than a
new silent one.

The committed sets carry 0 such ballots (`deduction_metrics` reports 0
unverifiable and 0 model-source-unavailable on all four, where every guard cell
equals its whole-record reading), so **no published cell moves**. The planted
pair is the proof instead, and the two halves differ in exactly who wrote the
marker:
`test_a_model_body_that_opens_with_marker_shaped_prose_stays_authored` (the
model's pre-guard body IS the whole record, so the ballot stays authored) and
`test_the_same_legacy_ballot_whose_marker_the_guard_wrote_leaves_the_share`
(same bytes, body alone as the pre-guard text, so the rewrite is real). Live
perturbation — restoring the whole-record scan, running, restoring:

```
$ uv run pytest tests/eval/test_process_scorecard.py -q
FAILED ...::test_a_model_body_that_opens_with_marker_shaped_prose_stays_authored
1 failed, 55 passed in 0.34s
```

and with the provenance cut back: `56 passed`. The planted meetings now record
each voter's pre-guard body in its own `LLMCallRecord` (`_call(model_body=...)`),
which is what a recorded vote call carries; a planted ballot that means to
exercise a guard marker has to supply the body the guard prepended to.

**2. The missing-prompt count is partitioned by ballot kind.** One
`no_prompt_ballots` fed `grounded_eject`, `grounded_skip`, `grounded_all` and
`wrong_but_believable` alike, so a single promptless EJECT reported a fully
recorded SKIP cell as one that measured NOTHING — the exact distinction
`RateCell`'s own docstring says `not_evaluable` is published separately to
preserve. `no_prompt_eject_ballots` and `no_prompt_skip_ballots` now feed their
own cells (`wrong_but_believable`'s denominator is EJECT ballots, so it takes
the EJECT count); `grounded_all` and the unexplained row keep the sum, because
their denominator is every ballot. Row 1's and row 8's published definitions say
so. `no_prompt_ballots` is **0 on all four committed sets**, so no published
cell moves. Pinned by `test_the_missing_prompt_count_is_partitioned_by_ballot_kind`,
which asserts the sibling cell stays 0, and its adverse half
`test_the_partition_holds_with_the_kinds_swapped`.

**3. A game with no reconstructed route raises.** `fold_set` took
`inputs.routes.get(game.seed, {})`, so a seed absent from the route table folded
against an empty route: every alibi tick unresolvable, row 3's census silently
0, and a published number that reads as a measurement of nothing. That is the
silent fallback AGENTS.md rule 5 forbids and the rule this card's Results
already cites as why a non-reconstructing replay raises
`ProcessScorecardReconstructionError`. It now raises, naming the seed and the
game. It is unreachable through `load_set_inputs` — `walk_routes` keys every
seed on disk — so it is pinned by a planted case rather than by a figure:
`test_a_game_with_no_reconstructed_route_is_refused_not_folded`, whose adverse
half folds the same game with its own seed keyed, beside the new
`test_a_replay_that_does_not_reconstruct_is_refused` for the walk-violation
path.

**4. `RateCell` refuses an incoherent published rate.** `_counts_are_coherent`
checked non-negativity, `numerator <= denominator` and the
None-iff-zero-denominator rule, so `RateCell(numerator=1, denominator=2,
rate=0.9)` was accepted and the identical shape round-tripped through
`RateCell.model_validate` from JSON. This is the typed boundary every published
scorecard rate crosses in both directions, and the model a later spectator
surface will parse `docs/process-scorecard.json` with, so an inconsistent
serialized cell must be refused rather than preserved and read. A rate must now
equal `round(numerator / denominator, 6)` — which is what `_cell` has always
produced, so every committed cell validates unchanged. Pinned by the perturbed
`test_a_rate_that_contradicts_its_own_counts_is_refused`, in process and from
JSON, the way the chance-population invariant is pinned.

The three code gates were also perturbed live, together: reverting the SKIP
cell's count to the shared one, the seed guard to `.get(seed, {})` and the rate
comparison to a no-op turns exactly their own three tests red
(`3 failed, 53 passed`), and restoring the file returns `56 passed`.

**What DID move, and what did not.** No agent behaviour, prompt byte, schema
field, detector or recorded byte; no `audits/` and no `tests/fixtures/` byte, so
no `docs/artifacts.md` inventory row is recomputed (the scorecard's own row is
deliberately sized `2 files` with no byte figure) and `tasks/README.md`'s
inventory sentence is unchanged, since the card's Status stays `done`. Every
NUMBER in `docs/process-scorecard.md` and `docs/process-scorecard.json` is
byte-identical: all nine rows, every per-set and pooled cell, the appendix. Four
DEFINITION strings moved, because a claim has to name the mechanism that
enforces it — rows 1 and 8 now define their per-kind not-evaluable count, and
rows 4 and 7 name `_split_rationale` as the provenance boundary in place of the
anchored-chain sentence the defect made false. The pair was republished with
`uv run python scripts/publish_process_scorecard.py` and the diff is those four
strings and nothing else.

**Verification at this head.** Every command was run in this clean worktree with
its exit code captured directly, never through a pipe:

```
$ uv run python scripts/publish_process_scorecard.py --check
--check: docs/process-scorecard.md and docs/process-scorecard.json are consistent with the committed recordings.
EXIT=0

$ uv run pytest tests/eval/test_process_scorecard.py tests/scripts/test_process_scorecard.py -q
68 passed in 12.11s
EXIT=0

$ uv run python scripts/validate_task_docs.py
Task docs validation passed: 390 historical phase tasks and 390 prompts; 73 work cards.
EXIT=0

$ uv run python scripts/verify_ml_evidence.py
checks: 61 | OK 49 | FAIL 0 | ABSENT 7 | INFO 5
EXIT=0
```

`uv run pytest tests/eval -q` (**1158 passed, 1 skipped**) and `uv run pytest
tests/scripts -q` (**1386 passed**) — 2,544 together, seven more than round 2's
2,537, which are the seven planted cases above. `uv run python
scripts/check_doc_facts.py`, `uv run lint-imports` (4 kept, 0 broken), `uv run
pytest tests/scripts/test_verify_ml_evidence.py -q` (80 passed), `bash
scripts/verify_samples.sh` (50 + 50 verified clean) and the four `uv run python
scripts/build_sample_report.py --sample-dir <set> --check` runs over
`replays/samples/4p1i`, `replays/samples/9p2i`, `replays/ml_corpus/4p1i` and
`replays/ml_corpus/9p2i` all pass. `bash scripts/check.sh` run whole in this
worktree returns **EXIT=0**: ruff clean, `lint-imports` 4 kept / 0 broken, 390
phase tasks + 390 prompts + 73 work cards, mypy over 489 source files, **8055
passed, 20 skipped, 3 xfailed**, frontend 19 test files / 515 tests passed and
the build green. Neither flake the earlier rounds recorded
(`test_recording_replacement.py`, `test_run_limits.py`) reappeared here. The
record-impact statement is unchanged and
re-demonstrated: `verify_samples.sh` and the four `--check` runs recompute
exactly what they did before this card. No provider call is a check here, and
none was made.

### Review corrections, round 4 (2026-09-20)

Three verifier lenses re-read the pushed head `1f4ac6a4`. Integrity and
documentation passed; correctness left **one** finding, which is VALID and is
repaired here:

> `ALIBI_FLAG_KINDS` claims it is read from the owning census but re-lists it,
> with no gate.

**The claim and the code disagreed.** `eval/process_scorecard.py`'s constant
carried the comment *"Read from the owning census in
:mod:`eval.alibi_fabrication` rather than re-listed, so a new alibi kind cannot
start being scored by one module and not the other"*, and the next three lines
wrote the three kinds out by hand. The census that owns them —
`eval/alibi_fabrication.py`'s `_ALIBI_CONTRADICTION_KINDS`, the set the
subject-membership join credits a catch from — was a PRIVATE constant nothing
outside that module could read, and no test compared the two. The sentence was
therefore an intention, not a mechanism: a fourth alibi kind added to the census
(as `alibi_vs_physical` was, by Task 13.4) would credit catches there and be
skipped by row 3's `if flag.kind not in ALIBI_FLAG_KINDS: continue`, moving the
manufactured-contradiction denominator away from the census in silence. The two
sets happen to be equal today, so nothing published is wrong; the defect is that
nothing held them together.

**Repair 1 of the two the review offered — one source of truth.** Nothing
forbids the import: both modules are in `eval/`, `.importlinter` states no
contract over `eval` beyond its membership in `root_packages` (its four
contracts govern `agents`, `observation` and `meetings.manager`), AGENTS.md's
only import rule is the observation firewall (rule 4, `agents/` must not import
`engine/`), and `eval/process_scorecard.py` already imports
`compute_alibi_fabrication_rate` from this very module. So the owning constant is
promoted to public — `eval.alibi_fabrication.ALIBI_CONTRADICTION_KINDS`, listed
in that module's `__all__`, its comment naming itself as the one home — and the
scorer binds the same object:

```python
ALIBI_FLAG_KINDS: Final[frozenset[str]] = ALIBI_CONTRADICTION_KINDS
```

There is now one list. The comment says what the code does, and the module
docstring's "Reuse, not re-implementation" paragraph names the constant beside
the analyzers it already reads by name. `ALIBI_FLAG_KINDS` keeps its name and
its place in the module's `__all__`, because row 3's published definition is
stated in terms of it.

**The gate.** Identity is the assertion, not equality: a hand-written copy of
the same three strings compares `==` and is exactly the drift the finding names,
so `tests/eval/test_process_scorecard.py::test_the_alibi_kind_filter_is_the_owning_census_itself`
asserts `ALIBI_FLAG_KINDS is ALIBI_CONTRADICTION_KINDS`, and its second half
pins the shared set inside the schema both modules branch on — the `alibi_*`
members of `meetings.schemas.ContradictionRef`'s `kind` Literal, exactly, so a
fifth alibi kind minted in the schema and left out of the census is red too.

**Planted, both directions.** First the defect itself restored — the scorer
re-listing the three kinds, the census untouched:

```
$ .venv/bin/python -m pytest tests/eval/test_process_scorecard.py -q
E       AssertionError: assert frozenset({'alibi_conflict', 'alibi_vs_physical', 'alibi_vs_sighting'}) is frozenset({'alibi_conflict', 'alibi_vs_physical', 'alibi_vs_sighting'})
FAILED tests/eval/test_process_scorecard.py::test_the_alibi_kind_filter_is_the_owning_census_itself
1 failed, 56 passed in 0.30s
```

— equal and not the same object, which is the whole finding in one line. Then
the drift the finding predicts, planted on the OTHER side: `"vent_sighting"`
added to the owning census alone, with the scorer untouched.

```
$ .venv/bin/python -m pytest tests/eval/test_process_scorecard.py -q
FAILED tests/eval/test_process_scorecard.py::test_a_vent_flag_is_outside_the_alibi_denominator
FAILED tests/eval/test_process_scorecard.py::test_the_alibi_kind_filter_is_the_owning_census_itself
2 failed, 55 passed in 0.33s
```

Row 3's own denominator test goes red, which is the proof the import did its
job: the scorecard now FOLLOWS the census rather than shadowing it, so the two
can no longer disagree — under the old hand-list that same plant left row 3
green and the modules silently split. Both files were restored; `57 passed`.

**Nothing published moved.** `.venv/bin/python
scripts/publish_process_scorecard.py` rewrote the pair and `git status
--porcelain docs/` is empty — every number and every definition string in
`docs/process-scorecard.md` and `docs/process-scorecard.json` is byte-identical,
as it must be, since the two sets were already equal. No agent behaviour, prompt
byte, schema field, detector, recorded byte, `audits/` byte or `tests/fixtures/`
byte moves, so no `docs/artifacts.md` row is recomputed and `tasks/README.md`'s
inventory sentence is unchanged (Status stays `done`).

**Verification at this head.** Each command run in this clean worktree with its
exit code captured directly, never through a pipe:

```
$ .venv/bin/python scripts/publish_process_scorecard.py --check
--check: docs/process-scorecard.md and docs/process-scorecard.json are consistent with the committed recordings.
EXIT=0

$ .venv/bin/python -m pytest tests/eval/test_process_scorecard.py tests/scripts/test_process_scorecard.py -q
69 passed in 8.11s
EXIT=0

$ .venv/bin/python scripts/validate_task_docs.py
Task docs validation passed: 390 historical phase tasks and 390 prompts; 73 work cards.
EXIT=0
```

`scripts/check_doc_facts.py` passes (EXIT=0), the eval suite reads **1159
passed, 1 skipped** — one more than round 3's 1158, which is the single new
case above — the promoted constant's own module
(`tests/eval/test_alibi_fabrication.py`) reads 21 passed, and `bash
scripts/check.sh` run whole in this worktree returns **EXIT=0**: ruff clean over
518 formatted files, `lint-imports` 4 kept / 0 broken over 188 analyzed files,
390 phase tasks + 390 prompts + 73 work cards, mypy over 489 source files,
**8056 passed, 20 skipped, 3 xfailed** — one more than round 3's 8055, the same
single case — and frontend 19 test files / 515 tests passed with the build
green. Neither flake the earlier rounds recorded reappeared. The
record-impact statement is unchanged and re-demonstrated. No provider call is a
check here, and none was made.
