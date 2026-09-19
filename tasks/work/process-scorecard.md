# Publish a deterministic process scorecard over the committed recordings

**Status:** ready

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

- [ ] A pure `eval/process_scorecard.py` folds loaded reports plus the engine
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
- [ ] Row 2 is computed as the Evidence pins it and says so in its definition
  string: crew EJECT ballots, recorded target, roles from the seeder, argmax
  over that voter's rows from `_rendered_suspicion_by_target_per_voter`
  (`eval/meeting_quality.py:2481`) intersected with the voter's rendered
  valid-target list, ties excluded and counted. The valid-target parse lands
  beside `_parse_suspicion_graph` (`:387`) under the FROZEN tier note its
  neighbours carry (`:318-321`), which permits an evidence reader and forbids
  new search. Planted: one follower and one deviator whose role-correctness
  differs, and a tie landing in the excluded count.
- [ ] Row 3 counts a flag as MANUFACTURED when its kind is an alibi class, its
  subjects name the speaker of a self-alibi claim in that meeting, and the
  claim is true at at least one tick of its own span against that speaker's
  `walk_replay` route. The claim census rides beside it: 955 claims, 104
  envelope-false, 103 multi-tick, 2 strict-false. Planted: an envelope alibi
  true at its first tick mints a flag and a flat single-tick lie does not.
- [ ] Rows 7 and 8 read the authored layer, never the marker prefix alone. The
  authored share counts every `BallotTargetRewriteReason` member through
  `_authored_target`, reports citation-nulling rewrites separately as "citation
  nulled, target intact", and carries the redirect census as a sub-count.
  Wrong-but-believable is role-incorrect AND row-1 grounded AND not row-3
  manufactured, labelled "reported, never penalised". Planted: a ballot
  carrying `under_gate_redirect` leaves the authored share, one carrying only a
  nulled-citation marker does not.
- [ ] Row 6 states its own limits in the output. It extracts whole-token player
  ids, room ids and tick references from `rationale_text` and checks each
  against this meeting's transcript and that voter's recorded prompt, reusing
  `names_player` (`meetings/citation_relevance.py:54`). The output says this
  tests TOKENS and not propositions, that an assertion and its negation score
  alike, and that the memo's section 3 result on invented facts is two-method
  agreement rather than this measurement. Planted: a rationale naming an absent
  room fails, and a test pins the negated-assertion pass as the stated limit.
- [ ] `scripts/publish_process_scorecard.py` writes both files, and `--check`
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
- [ ] The header carries, dated 2026-09-19 and linked to the direction, that
  role-correctness is reported and is not a gate per D1; the JSON carries it as
  typed keys. The fifth run is a closing APPENDIX, labelled out of the
  headline, reporting both arms (candidate 75 EJECT / 73 cited / 75 SKIP / 0
  cited; reference 14 / 14 / 136 / 0) beside the fact that all 100 of its
  meetings recorded exactly 3 ballots. It reads
  `audits/deduction-candidate/run-2026-09-16/` and writes nothing there.
- [ ] `docs/artifacts.md` gains ONE registry row for the pair, class `(b)`, `in
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
