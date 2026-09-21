# Ground every SKIP and make the ballot guards label instead of rewrite

**Status:** done

## Outcome

Every ballot carries a machine-checkable basis, and the recorded vote is the one
the voter authored. A SKIP stops being exempt: it cites a turn id or an
own-observation id that resolves, or it declares `none_held` in a new structured
field, and both are distinguishable from a voter that answered nothing. The
meeting layer stops re-aiming and stops coercing: `guard_ballot_target_graph`'s
suspicion-argmax redirect is retired and `guard_ballot_citation` becomes a
labeller that writes one closed-set `grounding_label` onto the recorded ballot
and changes no target. Citation relevance stops being a lever and becomes that
label's default input. The tally counts the agent's own target under every
label. The only rewrites left are the two a tally cannot do without, an illegal
target and the teammate firewall, both recorded as such.

## Evidence

[The direction of 2026-09-19](../direction-2026-09-19-process-over-outcome.md)
is the basis; the owner accepted D1 to D8 as a set on 2026-09-19 and section 12
records the rulings. D6 is this card, D8 sends the shelved accounts family's
SKIP register here, and the goal is the owner's: an agent's reasons must rest on
the data it holds, and a wrong call on believable data beats a right call on
none.

**The SKIP carries no basis, by instruction.** Counts only, partitioning each
committed ballot by `target == "SKIP"` and by whether either of
`primary_reason_id` / `primary_reason_observation_id` is non-null:

| set | EJECT | EJECT cited | SKIP | SKIP cited | SKIP w/ alternatives |
| --- | --- | --- | --- | --- | --- |
| `ml_corpus/9p2i` | 1,499 | 1,498 | 1,017 | **0** | 999 |
| `ml_corpus/4p1i` | 69 | 69 | 60 | **0** | 60 |
| `samples/9p2i` | 527 | 526 | 342 | **0** | 337 |
| `samples/4p1i` | 51 | 51 | 66 | **0** | 65 |

Not a missing gate.
`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:259` tells the voter "a
SKIP needs no citation" and `:268` repeats it as "a SKIP needs neither", while
`_normalize_ballot_reason_id` (`meetings/manager.py:3199`) and
`_normalize_ballot_observation_id` already run unconditionally at `:2337` and
`:2353`, before any target guard: a SKIP that cited something would already have
its id resolved or nulled. What is missing is the instruction, not the check.

**The guards rewrite.** `guard_ballot_target_graph` (`:3623`) returns early on a
SKIP (`:3683`), then re-aims an under-gate ballot at the eligible suspicion
argmax (`:3690-3736`) behind `BALLOT_TARGET_REDIRECT_MARKER` (`:322-324`), or
coerces to SKIP and nulls `primary_reason_id` when no eligible row clears the
gate (`:3721-3728`). `guard_ballot_citation` (`:3739`) then coerces an uncited
or off-target EJECT to SKIP at `:3867-3879`, exempting a flagged target
(`:3865`).

| marker class | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- |
| ballots | 2,516 | 869 | 129 | 117 |
| `under_gate_redirect` | 57 | 23 | 2 | 1 |
| `uncited_coerced` | 6 | 0 | 0 | 0 |
| `off_target_coerced` | 0 | 0 | 0 | 0 |

Restoring the authored target on every redirected and coerced ballot (read from
the marker's `{target!r}` payload) and re-tallying under `tally_ballots`
(`meetings/voting.py:187-281`) moves the outcome in 12 of 439 `ml_corpus/9p2i`
and 5 of 151 `samples/9p2i` meetings: 17 of 590, split 5 SKIPPED to EJECTED, 5
EJECTED to SKIPPED and 7 EJECTED onto a different player. That script also
reproduces the recorded outcome on 590 of 590 meetings before the substitution,
which establishes it implements the real tally; the split is two-sided, so
nothing here is an accuracy argument either way.

**The lever and the schema.** `citation_relevance_version` sits on
`MeetingEvidenceProfile` (`meetings/evidence_profile.py:82`) and
`RecordedExperimentConfig` (`orchestrator/experiment_config.py:50`), switched by
`AILIBI_CITATION_RELEVANCE` (`.env.example:256`), read at the guard call site
(`meetings/manager.py:2412-2419`) and never ON in a committed recording, which
is why `off_target_coerced` is 0. Its rule `citations_bear_on`
(`meetings/citation_relevance.py:141`) already sits inside the firewall and is
callable unconditionally. `_FrozenModel` is `extra="forbid"`
(`meetings/schemas.py:58-59`), so a value the schema rejects degrades the whole
vote through `_vote_parse_default` (`meetings/manager.py:3012-3038`), which is
why `_without_model_authored_provenance` (`:2982-3009`) strips first.

## Acceptance

- [x] Review correction: the `invalid_citation`-over-`none_held` ordering has
  the planted case it exists for, and the two orderings that are genuinely
  unreachable say so in the code. A voter that declares
  `decision_basis="none_held"` AND cites a turn id this meeting does not own
  reaches the labeller carrying both halves — the validator nulls the id while
  the in-set basis rides the pre-pass untouched — and the record says what the
  ballot DID: `invalid_citation`. Proved by
  `tests/meetings/test_grounding_label.py::TestEveryBallotDeclaresItsBasis::test_a_fabricated_citation_outranks_a_declared_none_held`,
  with the declared-basis twin beside it and the combination added to
  `TestEveryRecordedBallotIsLabelled._SPECS` (probe: swap the two branches —
  `1 failed, 44 passed`). `label_ballot_grounding`'s docstring now records the
  two lines that are unreachable-by-construction at the one call site and KEPT
  as defensive lines: `invalid_citation` can never race `supported` /
  `off_target` there, because `citation_nulled` requires both ids `None`; and
  the `ballot.target != SKIP` half of the `flag_only` guard can never be what
  decides it, because a live `ContradictionRef.subjects` holds a speaker or a
  claim subject and never the literal `"SKIP"`.
- [x] Review correction: `"grounding_label"` in `_LAYER_OWNED_BALLOT_FIELDS`
  (`meetings/manager.py:3030-3034`) is an enforced line. Removing the row left
  `tests/meetings` green while costing a voter its WHOLE vote on a
  non-validating client: an out-of-set `grounding_label` then fails the schema
  and the ballot degrades to `parse_default`.
  `tests/meetings/test_manager.py::test_a_model_authored_provenance_value_never_reaches_the_record`
  gains `{"grounding_label": "fabricated"}` and the in-set
  `{"grounding_label": "supported"}`, and asserts the vote survives on its
  authored target with the LAYER's label on it (probe: drop the row —
  `1 failed, 1,382 passed`).
- [x] Review correction: `bounded_marker_original(dropped)` on the invalid
  basis (`meetings/manager.py:3107`) is an enforced line. Removing it left
  `tests/meetings tests/api` green while a 5,000-character fabricated
  `decision_basis` grew the recorded rationale from 111 characters to 5,048.
  `test_an_over_length_fabricated_basis_is_quoted_bounded` drives that value
  through the manager and asserts the recorded rationale is the marker quoting
  a head bounded by `MARKER_QUOTED_ORIGINAL_MAX_CHARS` plus
  `MARKER_TRUNCATION_SUFFIX` (probe: drop the bound — `1 failed, 1,820 passed,
  2 skipped`).
- [x] Review correction: the call surface is walked a SECOND time, because
  round 3's claim that it was covered was wrong three times over. Every added
  or changed executable line and tuple row of the eight production modules was
  neutered again; two MORE came back green and now carry cases — the
  observation half of `cited_before_validation` at the labeller's call site (a
  voter that cites a fabricated own-observation id read `uncited` where it must
  read `invalid_citation`) and the JSON rendering of a non-string
  `decision_basis` in the pre-pass. Two lines are recorded as unobservable
  rather than planted, with the reason: both conjuncts of the `citation_nulled`
  expression are masked by the `supported` / `off_target` branch above them.
  The complete table with every count is in the round-4 Results subsection.
- [x] Review correction: the prose sweep is closed against every inflection of
  `coerc`, not the five phrases earlier rounds grepped.
  `tests/agents/test_public_account_prompts.py` said in the present tense that
  a nulled citation coerces the ejection to SKIP and that "a SKIP needs no
  citation"; `tests/api/test_view_model.py` called the under-gate redirect the
  "live" gate chip; `tests/training/test_surrogate_dataset.py` called the
  retired gate "the last guard" and its stack "the production stack"; and
  `experiments/fresh_deduction_instrument.py` said an under-gate redirect
  "breaks" the authored target. Each now states the retirement at the strength
  the code delivers. The widened greps and their output are quoted in the
  round-4 Results subsection.
- [x] Review correction: the smaller items. Three sites said the labels outside
  `TARGET_REWRITE_LABELS` are "the two citation-only" ones and this card made
  them three (`api/replay_loader.py:302-305`,
  `training/surrogate/dataset.py:212-221`,
  `training/surrogate/ballots.py:65-68`);
  `docs/glossary.md` and `frontend/src/lib/copy.ts` glossed `supported` with
  the SKIP's subject only, and now say both; `BallotCard.tsx`'s comment called
  `not_assessed` a firewall coercion and now names all four paths;
  `scripts/record_ml_corpus.sh`'s lineage comment said "all four at v5" above a
  literal reading v6/v6/v6/v7; `docs/artifacts.md:101` said the live set reads
  v6 with no mention of `vote_ballot`'s v7 (the row's class, where and size
  cells are untouched, so no inventory row is recomputed); and the schema's
  "`None` is reserved for a recording made before the field" is restated as a
  claim about MEETING recordings, because
  `training/surrogate/runner.py`, `training/composed_runner.py` and
  `eval/reasoning_evidence.py` build `VoteBallot` objects that are not
  recordings and correctly carry `None`.
- [x] Review correction: the labeller's `turns=` argument at the manager's call
  site has the enforcing case it lacked. An EJECT citing a REAL turn of this
  meeting that NAMES its target reads `supported`; replacing `turns=` with `()`
  at that call site turns the same ballot `off_target` and was invisible to the
  whole suite. Proved by
  `tests/meetings/test_grounding_label.py::TestEveryBallotDeclaresItsBasis::test_an_eject_citing_a_turn_that_names_its_target_is_supported`,
  driven through `MeetingManager`, with the off-target twin citing a turn that
  names somebody else (probe: `turns=()` — `1 failed, 42 passed`, and
  `1 failed, 1,816 passed, 2 skipped` over `tests/meetings tests/api`).
- [x] Review correction: the labeller's `candidate_targets=` argument has one
  too. A SKIP with EMPTY `considered_alternatives` — the generous-pool branch,
  23 of the 1,359 shipped 9p2i SKIPs — citing an own-observation line that names
  a living candidate reads `supported`; replacing the argument with `()` turns
  it `off_target`, because a citation with no subject bears on nobody. Proved by
  `tests/meetings/test_grounding_label.py::TestEveryBallotDeclaresItsBasis::test_a_skip_that_weighed_nobody_is_read_against_the_living_pool`,
  with the twin citing the line that names only the VOTER, who is never its own
  candidate (probe: `candidate_targets=()` — `1 failed, 42 passed`, and
  `1 failed, 1,816 passed, 2 skipped`).
- [x] Review correction: the whole call surface this card added is walked and
  probed, not just those two arguments — every argument of the labeller call,
  every argument of the `citations_bear_on_any` call inside it, all three
  branches of `_ballot_grounding_subjects`, the `_ballot_view` mirrors, the
  pre-pass call, `_default_vote`'s label, the four marker registrations and the
  two prompt skeletons. Two came back GREEN and now carry cases: the
  `invalid_basis` row of `api/replay_loader.py`'s `_BALLOT_PREFIX_MARKERS`
  (`tests/api/test_view_model.py::test_parse_rewrite_reasons_uses_imported_markers`)
  and the two `rewriteLabel` cases `BallotCard.tsx` gained
  (`frontend/src/components/PrivateReasoning.test.tsx`). The table with every
  probe's counts is in the round-3 Results subsection.
- [x] Review correction: the skeleton no longer pre-answers the basis.
  `vote_ballot.j2:263` and `vote_ballot_accounts.j2:23` ship
  `"decision_basis": null`, on this repo's own discipline — a slot is shown in
  PROSE and never pre-filled into the object a model copies verbatim
  (`agents/strategic/prompts/loader.py`'s `v5` bullet) — which binds hardest
  here, because ruling D6 exists to make the VOTER state its basis and a voter
  that edits `target` and leaves the skeleton alone would record one it never
  chose. Both prose registers keep the two legal tokens and now say the skeleton
  shows null. Still `vote_ballot` `v7` and still `ACCOUNT_PROMPT_SET_REVISION`
  `v6`, both unreleased. Pinned by
  `tests/meetings/test_elicitation_fixtures.py::TestCitationRequiredConfidence::test_the_skeleton_leaves_the_basis_for_the_voter_to_write`
  (probe: restore `"cited"` — `1 failed, 27 passed`) and
  `tests/agents/test_public_account_prompts.py::test_the_skeleton_leaves_the_basis_for_the_voter_to_write`
  (probe: restore `"none_held"` — `2 failed, 92 passed`). That file's total is
  94 here and 93 in the accounts-revision item below: both are as measured, at
  the round-3 head and the round-1 head respectively, and the difference is the
  case round 3 added (dated note, review round 4, 2026-09-21).
- [x] Review correction: `TestTheOnlyTargetRewrites` reads `node.keywords`
  beside `node.args`, so a `ballot_target_rewrite_provenance(ballot,
  reason=...)` call can no longer be visited and contribute nothing. Proved by
  `tests/meetings/test_grounding_label.py::TestTheOnlyTargetRewrites::test_the_scan_sees_a_reason_passed_as_a_keyword`,
  which runs the REAL scanner over a planted source carrying the keyword,
  dotted-keyword and positional forms (probe: read `node.args` only —
  `1 failed, 42 passed`).
- [x] Review correction: decision 4's `state_hash_after` claim is stated at the
  strength the code delivers. The check is unweakened on the ENGINE leg and
  that is now the whole of it: `_run_recorded_meeting` applies the RECORDED
  decision, so the hash cannot transitively say today's ballot chain still
  reaches it, and `test_every_reconstruction_divergence_is_a_retired_guard` is
  what carries that half. Corrected in decision 4 and in the comment above the
  check (`tests/meetings/test_prompt_byte_golden.py`).
- [x] Review correction: the undated Verification table is re-measured at THIS
  head and labelled with the round it was measured at; the dated round-1 and
  round-2 tables stay as history. Three of its cells were stale at `7e6747c7`
  — 8,153 where `check.sh` printed 8,158, 1,810 where `tests/meetings tests/api`
  printed 1,813, and 38 where `test_grounding_label.py` printed 40.
- [x] Review correction: the card's own record is complete. The
  planted-failures running total counts rounds 2 and 3; the three files the
  diff touches that `## Expected scope` does not name are recorded by a dated
  note rather than by a silent rewrite (decision 10); the test pin that moved
  off `audits/deduction-candidate/execution-manifest.md` is declared (decision
  11); and every citation in the CURRENT sections was re-derived mechanically
  at this head AFTER the last code edit.
- [x] Review correction: the `none_held`-over-`flag_only` ordering has the
  planted case it exists for. An EJECT onto a target carrying a contradiction
  detected THIS meeting, whose voter declared `decision_basis="none_held"`,
  labels `none_held`; the same meeting and the same flag without the voter's
  word labels `flag_only`. Both run the manager chain, and the flag is detected
  from the transcript rather than injected. Proved by
  `tests/meetings/test_grounding_label.py::TestEveryBallotDeclaresItsBasis::test_a_declared_none_held_outranks_a_flag_on_the_target`
  (probe: lift the `flag_only` branch above the `none_held` one —
  `1 failed, 39 passed`).
- [x] Review correction: the spectator mirror in `_ballot_view` is an enforced
  production line. `tests/api/test_view_model.py::test_ballot_view_mirrors_the_stated_basis_and_the_layers_finding`
  drives a `VoteBallot` carrying both fields through the loader seam and asserts
  both survive into the served payload, with the `None` half beside it (probe:
  replace both mirrors with `None` — `1 failed, 437 passed, 2 skipped` over
  `tests/api`).
- [x] Review correction: the prose sweep is finished against the RETIRED SYMBOL
  names and case-insensitively, not only against the round-1 phrases.
  `tests/meetings/test_manager.py:829-833` no longer says the gate coerces in
  the present tense, and `eval/meeting_quality.py:277-282` / `:983-987` no
  longer say the citation gate IS the last guard in the live chain. The closing
  greps and their exact results are quoted in the round-2 Results subsection;
  no test pins prose, so the enforcing check is the grep.
- [x] Review correction: the four live-tense references to the deleted
  `guard_ballot_citation` are swept the way `eval/meeting_quality.py:114` was —
  `tests/eval/test_meeting_quality.py:5-11` and `:291-297`,
  `tests/meetings/test_corroboration.py:1397-1400` and `:1955-1959`, and
  `tests/experiments/test_fresh_deduction_instrument.py:10153-10158` — each now
  naming the retirement rather than a live function.
- [x] Review correction: the retired `citation_gate` key carries the history
  line the lever-retirement procedure requires, at `_RETIRED_ALWAYS_ON_LEVERS`
  (`orchestrator/replay.py:982-990`) and in the `.env.example` graduated-levers
  note (`.env.example:120-126`), and the false "unconditionally ON" claim is
  corrected at `orchestrator/replay.py:973` and `:1259`. The key STAYS, because
  dropping it would shift `SUBSTRATE_FLAG_KEYS` and move every committed
  MANIFEST `flags` cell; Record impact declares that from the re-record that
  cell keeps reading `citation_gate` true for a retired mechanism. Pinned by
  `tests/orchestrator/test_replay.py` (111 passed) and
  `scripts/check_doc_facts.py` (the note still labels the class always-ON).
- [x] Review correction: the ten stale file:line citations in Results resolve
  at this head. Re-measured by SYMBOL after every code edit of this round, so
  `meetings/schemas.py:1016` / `:1079` / `:886`, `meetings/manager.py:2352` /
  `:2376` / `:3001` / `:3030-3034` / `:3057` / `:3706` / `:3733`,
  `meetings/voting.py:192` and `api/replay_loader.py:3613` are the true lines
  (re-derived by symbol again after round 4's last edit, which moved eight of
  them; the round-2 and round-3 subsections keep the figures of THEIR heads);
  the round-1 subsection's `_LAYER_OWNED_BALLOT_FIELDS` and provenance-boundary
  citations move with them.
- [x] Review correction: `INVALID_BASIS_MARKER` is registered in the eval
  marker-chain table (`eval/deduction_metrics.py:724`), so the machinery's own
  sentence stays on the machinery side of the provenance split instead of being
  read as the voter's words from the re-record onward. Proved by
  `tests/eval/test_deduction_metrics.py::test_the_invalid_basis_marker_is_read_as_machinery_not_as_the_voter`
  (probe: drop the row — `1 failed, 117 passed`).
- [x] Review correction: the provenance-boundary line
  (`meetings/manager.py:2352`) has a probe. `test_a_fabricated_basis_survives_the_teammate_redaction`
  (`tests/meetings/test_grounding_label.py`) drives an impostor voter naming a
  teammate with an out-of-set `decision_basis` and asserts the redacted
  invalid-basis marker survives the firewall redaction; the card's universal
  probe claim is corrected above the probe table.
- [x] Review correction: `ModelAuthoredVoteBallot`'s docstring names THREE
  layer-owned fields (`meetings/schemas.py:993-996`), the set
  `_LAYER_OWNED_BALLOT_FIELDS` holds. Pinned by
  `tests/meetings/test_manager.py::TestBallotRewriteProvenanceSites::test_the_model_facing_schema_is_the_ballot_minus_the_guard_pair`,
  which DERIVES the three-name difference rather than restating it.
- [x] Review correction: `ACCOUNT_PROMPT_SET_REVISION` advances `v5` → `v6`
  (`agents/strategic/prompts/loader.py:1283`) with its history bullet, because
  ruling D6 moved `vote_ballot_accounts.j2`'s bytes. Proved by
  `tests/agents/test_public_account_prompts.py::test_a_body_carrying_the_v6_bounds_cannot_be_stamped_an_older_revision`
  (probe: set the constant back to `v5` — `1 failed, 92 passed`).
- [x] Review correction: the prose sweep is finished. `loader.py`'s v4 and v5
  bullets, `meetings/voting.py`'s provenance docstring, `meetings/manager.py`'s
  `observation_ids` and absence paragraphs, `agents/memory/beliefs.py`'s
  absence constant, `scripts/counterfactual_phase21.py`'s C-7 row note,
  `api/replay_loader.py`'s marker-table note,
  `tests/agents/test_absence_prior.py`'s two docstrings and five further sites
  no longer say an uncited EJECT coerces. The enforcing check is a grep, quoted
  with its result in the round-1 Results subsection, not a gate: no test pins
  prose, which is why the sweep is done by reading the tree rather than by
  running it.
- [x] Review correction: the byte-golden docstring states the census its own
  file pins — 24 of 986 sample ballots across 15 of 190 meetings
  (`tests/meetings/test_prompt_byte_golden.py:288-295`), the figures
  `test_every_reconstruction_divergence_is_a_retired_guard` asserts per set.
- [x] Review correction: a citation-class marker stacked BEHIND a target
  rewrite is counted again (`training/surrogate/dataset.py:314`), so a
  fabricated basis on a betrayal ballot is not lost to the surrogate reader.
  Proved by
  `tests/training/test_surrogate_dataset.py::test_a_citation_class_marker_behind_a_target_rewrite_is_still_counted`
  plus the committed-bytes census (probe: restore the unbounded return —
  `2 failed, 38 passed`).
- [x] Review correction: the two unresolvable file:line citations in Results
  now read `frontend/src/types/api.ts:391-392` and
  `frontend/src/components/BallotCard.tsx:292-294`, checked by
  `grep -n "decision_basis\|grounding_label" frontend/src/types/api.ts` and
  `grep -n "under_gate_redirect" frontend/src/components/BallotCard.tsx`.
- [x] Every ballot declares a basis. `ModelAuthoredVoteBallot` gains
  `decision_basis: Literal["cited", "none_held"] | None = None`
  (`meetings/schemas.py:767-773`): `None` means the voter answered nothing and
  is what every committed recording parses to, `"none_held"` is its explicit
  statement that it holds nothing that resolves, `"cited"` puts the basis in the
  two id slots. Any other token is dropped from the raw payload before
  validation by the pre-pass that strips the guard keys
  (`meetings/manager.py:2982-3009`), behind a new `INVALID_BASIS_MARKER` shaped
  like `INVALID_REASON_ID_MARKER` (`meetings/manager.py:357-359`), so a
  fabrication is countable and never defaults the vote. This is one field of
  ONE decision record the wave composes: target, the two citation ids,
  `decision_basis`, `considered_alternatives`, `rationale_text` and the
  `counter_reason_id` [the weighing card](ballot-weighing-channel.md) adds,
  with `grounding_label` written beside them by the layer. That card reuses
  this `none_held` vocabulary and mints no second one.
- [x] One prompt clause, one per-template version bump. `vote_ballot.j2:259`
  loses "a call you cannot source either way is a call to SKIP, and a SKIP needs
  no citation" and `:268` loses "a SKIP needs neither", replaced by the SKIP
  register harvested from the shelved accounts body
  (`vote_ballot_accounts.j2:21`): which slot a SKIP may cite, the exact
  `"none_held"` token, and that body's id-shape discipline (copy it verbatim
  from between the brackets, never abbreviate, never append a row suffix). The
  clause states that the vote stands either way, because after this card nothing
  changes it; `vote_ballot.j2:263`'s skeleton gains `"decision_basis"` and
  `:262`'s key count moves from 7 to 8, which
  [the weighing card](ballot-weighing-channel.md) then moves from 8 to 9.
  `vote_ballot.j2:3`'s marker and the `qwen3_6_27b` entry in
  `PROMPT_VERSION_SETS` (`orchestrator/game.py:424`) advance `vote_ballot`
  ALONE from the `v6` [the alibi card](alibi-as-route.md) leaves at this branch
  point to `v7`, in the Task 15.5 `qwen3_32b` form at `:401-407`; the set's
  "four stamps bump as a unit" note is about the map card and does not bind when
  one body moves. Live-registry and marker-equality pins move
  (`tests/agents/test_bespoke_prompt_sets.py:525-541`, `:1000-1004`);
  recorded-manifest pins do NOT (`tests/scripts/test_manifest_writer.py:78-80`),
  because a manifest reads as-recorded and every replay records `.v5`, which the
  alibi card's v5 archive already covers, so no archive entry is added here.
- [x] `guard_ballot_target_graph` is retired, not disabled: the function, its
  call site (`meetings/manager.py:2387-2394`) and the tests pinning its redirect
  go. `BALLOT_TARGET_REDIRECT_MARKER` and `BallotTargetRewriteReason`'s
  `under_gate_redirect` member (`meetings/schemas.py:725-732`) survive as
  read-only history, because 83 committed ballots carry that marker and four
  consumers parse it (`api/replay_loader.py:3605-3614`,
  `training/surrogate/dataset.py:195-203`, `eval/meeting_quality.py:1454-1455`,
  `experiments/fresh_deduction_instrument.py:5015`); a test asserts no live path
  mints it. It goes rather than becoming a label because re-aiming at the argmax
  IS the engine pushing the agent toward its own arithmetic, the deference
  [the weighing card](ballot-weighing-channel.md) also drops.
- [x] `guard_ballot_citation` becomes `label_ballot_grounding` and rewrites
  nothing. It writes one value to a new `grounding_label` on `VoteBallot` only
  (never on `ModelAuthoredVoteBallot`, the rule `guard_rewrite_reason` follows),
  in this precedence: `not_assessed` when the recorded target is the layer's and
  not the voter's; else `supported` / `off_target` when a citation survived, by
  `citations_bear_on`; else `invalid_citation` when an id was nulled; else
  `none_held` when the voter said so; else `flag_only` when an EJECT's target
  carries a contradiction flag detected this meeting (the `:3865` exemption kept
  as a label, not a pass); else `uncited`. `None` is reserved for recordings
  predating the field, and `none_held` outranks `flag_only` on purpose: a voter
  that says it holds nothing must not be upgraded by the layer. The subject is
  the EJECT's target, and for a SKIP it is `considered_alternatives` when
  non-empty (1,336 of 1,359 shipped 9p2i SKIPs) and `candidate_targets`
  otherwise. `citation_relevance` gains `citations_bear_on_any(subjects=...)`
  and `citations_bear_on` becomes its one-subject case, so the rule stays ONE
  definition. Every label value is a row
  [the process scorecard](process-scorecard.md) counts, under its definitions.
- [x] The tally is untouched and counts the agent's target under every label.
  `tally_ballots` (`meetings/voting.py:187-281`) takes no new argument and reads
  no label: an `uncited`, `off_target` or `invalid_citation` EJECT is tallied
  for the player the voter named. Recorded as a decision in the card and the
  function docstring, with its reason: the shown decision must be the agent's,
  and dropping an unsupported EJECT is the engine deciding, one-sidedly, toward
  SKIP. "Innocents are ejectable but not at random" is served by the label being
  visible and counted, not by suppressing the vote; plurality and the confidence
  cutoff are unchanged, and the coercion removed here reached 6 of 2,516 and 0
  of 869 committed ballots. The two rewrites that remain say so: an illegal
  target cannot be tallied, so `normalize_ballot_target`
  (`meetings/voting.py:152`) still records `target="SKIP"`,
  `guard_rewrite_reason="invalid_target"`, the bounded authored string, its
  marker and `grounding_label="not_assessed"`; and the teammate firewall
  (`coerce_teammate_ballot_to_skip`, `meetings/manager.py:3628`) enforces a role
  rule the voter was told in its own prompt (`vote_ballot.j2:243`), not an
  evidence judgement. A test asserts these two plus `parse_default` are the only
  target-rewriting paths.
- [x] Citation relevance is retired as a lever, per
  [the procedure](../../docs/agent-procedures.md#retiring-substrate-levers)
  and AGENTS craft rule 7. Deleted: the field on `MeetingEvidenceProfile`
  (`meetings/evidence_profile.py:82`) and `RecordedExperimentConfig`
  (`orchestrator/experiment_config.py:50`), both validator entries
  (`meetings/evidence_profile.py:89`, `orchestrator/experiment_config.py:61`),
  the `None`-omission branch (`orchestrator/experiment_config.py:121-122`),
  `CITATION_RELEVANCE_ENV` and its `EXPERIMENT_ENV_NAMES` row
  (`meetings/evidence_profile.py:18`, `:32`), `.env.example:256`, the
  `orchestrator/game.py:2212-2218` runner-agreement key, the
  `tests/api/test_leak.py:508` allowlist entry, and
  `experiments/citation_relevance_counterfactual.py`, whose question has no
  answer once nothing coerces; `scripts/check_doc_facts.py:1899-1969` then gates
  a 4-switch registry (`:964`). Because `RecordedExperimentConfig` is
  `extra="forbid"` (`orchestrator/experiment_config.py:32`), the shelved
  `combined_accounts` arm loses its `citation_relevance_version=1` keyword at
  `experiments/fresh_deduction_instrument.py:1167` and keeps importing, the one
  edit [the close card](close-deduction-candidate-evaluation.md) names for it.
  The prose sweep is required: every docstring or doc line calling the gate
  default-OFF or saying an uncited EJECT coerces is corrected,
  `eval/vote_correctness.py:18` and `vote_ballot_accounts.j2:21` included.
- [x] The new fields reach the spectator without breaking the old record.
  `BallotView` (`api/schemas.py:962-970`) and `_ballot_view`
  (`api/replay_loader.py:3286-3301`) mirror both with `None` defaults;
  `frontend/src/types/api.ts:381-386` and `tests/api/test_leak.py` (the
  `BallotView` row at `:112`, the field allowlist beside `:552`) follow.
  `BallotCard.tsx` renders the label as one plain-language chip beside the
  alternatives block [the spectator card](spectator-tour-and-alternatives.md)
  added, the second of three edits that component takes; the weighing card adds
  the third. `rewriteLabel` (`BallotCard.tsx:20-31`) KEEPS its
  `under_gate_redirect` and `uncited_coerced` cases and the `:154-156` redirect
  disclosure, because the shown recordings carry those markers until
  [the re-record](process-rerecord.md). Every label value gets a
  `docs/glossary.md` entry, per craft rule 4.
- [x] One planted case per label, each red before and green after: a SKIP citing
  a resolving own-observation id that names a weighed alternative is
  `supported`, the same citation naming nobody weighed is `off_target`, a
  fabricated turn id is `invalid_citation`, `decision_basis="none_held"` is
  `none_held`, a bare SKIP is `uncited`, and a ballot naming a dead player is
  `not_assessed` and tallies as SKIP. Two more prove the tally ruling: an
  uncited EJECT onto a flagged target is `flag_only`, one onto an unflagged
  target is `uncited`, and BOTH tally as an EJECT where `main` coerces them to
  SKIP. A ninth plants an out-of-set `decision_basis` and asserts it is
  stripped, marked and `uncited` rather than defaulting the vote. One fixture
  replays the whole chain and asserts no `target` differs from the authored one
  outside the three rewrite reasons above.

## Constraints

No live provider call of any kind: fake and replay providers only, no
calibration, no recording and NO re-record. The single combined re-record is
[its own card](process-rerecord.md) after the wave, per the standing cadence
doctrine, so this card's behaviour change first reaches recorded bytes there.
Band 2100-2999 stays unseen, no held-out prefix is generated or opened, and
`scripts/verify_ml_evidence.py --complete` is not run.

This card changes SHIPPED DEFAULT behaviour, departing from the default-OFF
lever rule in AGENTS craft rule 7; the departure is ruling D6 of 2026-09-19 and
the PR carries it. Nothing here may push the agent toward the correct answer:
the label describes the basis and is never an input to the tally, and no
threshold, ordering or exemption is tuned against role-correctness, a reported
cell under D1 that appears in no acceptance item. The labeller is a pure
function of its inputs, with no RNG, clock or env read, so determinism holds;
`meetings/` must not import `experiments/`; invalid input raises, with the one
exception the chain already makes for a model payload, where a bad value is
marked and nulled rather than allowed to destroy a vote.

Order, identical on all seven cards. WAVE 1 is parallel and changes no agent
behaviour: [the scorecard](process-scorecard.md),
[the spectator tour](spectator-tour-and-alternatives.md) and
[the evaluation close](close-deduction-candidate-evaluation.md), the close
merging FIRST so the substrate wave's `GENERATOR_SOURCES` edits owe no restamp
to a retired band. The SUBSTRATE WAVE is serial, all three moving the
`qwen3_6_27b` stamps and the ballot or claim schema:
[alibi as a route](alibi-as-route.md), then THIS card, then
[the weighing channel](ballot-weighing-channel.md); then
[the re-record](process-rerecord.md), once. Deferred and in no card: the body
freshness band, an impostor who reports a body, the `docs/` front door.

One writer per file. This card branches from the alibi card, because both move
`meetings/schemas.py`, `vote_ballot.j2` and the prompt-version table; the
weighing card stacks third and takes the next `vote_ballot` version. The alibi
card owns `tests/fixtures/prompt_archive/` and `docs/artifacts.md`'s
`tests/fixtures/` row; `BallotCard.tsx` and `frontend/src/types/api.ts` are the
spectator card's until it merges, and this card then stacks on what it left.

## Expected scope

`meetings/schemas.py` (the two fields, the closed-set alias, the history note on
`BallotTargetRewriteReason`), `meetings/manager.py` (the retired redirect, the
labeller, the basis pre-pass, the new marker, the two call sites),
`meetings/citation_relevance.py`, `meetings/evidence_profile.py`,
`orchestrator/experiment_config.py`, `orchestrator/game.py`, `.env.example`,
`experiments/fresh_deduction_instrument.py` (the shelved arm's one keyword),
`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2` (plus
`agents/strategic/prompts/loader.py` and `vote_ballot_accounts.j2` for the prose
sweep), `api/schemas.py`, `api/replay_loader.py`, `frontend/src/types/api.ts`,
`frontend/src/components/BallotCard.tsx`, `docs/glossary.md`,
`scripts/check_doc_facts.py`, the prose sweep from
`eval/vote_correctness.py:18`, the deletion of
`experiments/citation_relevance_counterfactual.py`, `tasks/README.md`'s
inventory sentence, the tests for each, and this card.
`eval/meeting_quality.py`, `eval/vj_instruments.py` and
`training/surrogate/dataset.py` keep their marker tables: they read history.
Delivered on `work/grounded-skip-and-guard-labels` and one pull request into
`main`, a merge commit or fast-forward and never a squash, with the trailer
`Card: tasks/work/grounded-skip-and-guard-labels.md`.

## Record impact

A deliberate change to shipped default behaviour, authorized by ruling D6. From
the merge a recorded ballot's `target` is the voter's under every grounding
label, and the meeting mints `BALLOT_TARGET_REDIRECT_MARKER`,
`UNCITED_ZERO_FLAG_EJECT_MARKER` and `OFF_TARGET_CITATION_EJECT_MARKER` never
again. Expect the ejection rate to move: on committed bytes the equivalent
substitution moved 17 of 590 meeting outcomes, two-sided.

No committed byte moves and no report is re-scored, by the SAME mechanism the
other two substrate cards use: every recorded shape is read as recorded.
`decision_basis` and `grounding_label` are additive with `None` defaults; the
three retired markers stay as constants, so `api/replay_loader.py:3569-3577`,
`training/surrogate/dataset.py:195-203` and the `eval/` census patterns keep
resolving over old bytes; and `citation_relevance_version` was `None` in every
recording and is omitted from the serialized config, so deleting it removes no
recorded key. The four `--check` runs stay green by construction rather than by
version gating: no cell is added to `tournament-eval-report.json`.

Prompt bytes move, so `vote_ballot`'s stamp advances to `v7` while every
committed recording keeps `.v5` under the archive the alibi card opened, and
`arm_surface_digests` refuses a resume begun before this card. The served API
payload gains two fields, a contract change published by the Pages rebuild on
merge; the label mix becomes a reported row on
[the process scorecard](process-scorecard.md), reading `None` until the
re-record. No `audits/` or `tests/fixtures/` byte changes here, so no
`docs/artifacts.md` row is recomputed. Adoption is not applicable: there is no
switch and no arm to adopt.

A SECOND prompt stamp moves, declared in review round 1: the shelved accounts
family's `vote_ballot_accounts.j2` carries the same ruling, so
`ACCOUNT_PROMPT_SET_REVISION` advances `v5` → `v6` and every account stamp
`public_account_prompt_versions` composes reads `.v6.accounts<n>.attributed<n>`.
The correction that made this mandatory is prose — the body told a voter a
nulled id "coerces it to SKIP", which ruling D6 makes false — and the revision
advances for a byte change of any size. No recorded stamp collides: committed
account stamps exist at `v1` and `v4` only
(`test_no_committed_capture_already_carries_todays_account_stamps`), the family
is shelved and appears in no live registry, so no committed byte moves and no
recording can be misread. The accounts bodies are not `vote_ballot`'s: the
`v7` bump above is still `vote_ballot` ALONE, and the weighing card's `v8`
is unaffected.

That `v6` ABSORBS a second edit, declared in review round 3: the skeleton's
`"decision_basis"` is now `null` in both bodies rather than pre-filled. Neither
stamp moves again, and both gates agree that they must not. `v6` is unreleased
— `test_no_committed_capture_already_carries_todays_account_stamps` is the
assertion that no capture carries it, and `vote_ballot`'s `v7` reaches no
recording until the re-record — so there is no generation of either body under
its own stamp for this edit to collide with, which is the whole property the
revision exists to hold. `_PRE_V6_REVISIONS` is unchanged and
`test_a_body_carrying_the_v6_bounds_cannot_be_stamped_an_older_revision` still
passes: the edit touches none of the v6 spans that gate names, and the gate now
asserts the null skeleton beside them so the two facts move together or not at
all.

A SUBSTRATE-STAMP cell changes meaning without moving, declared in review round
2: the `citation_gate` key stays in `_RETIRED_ALWAYS_ON_LEVERS`, so every
recording and every MANIFEST `flags` cell keeps asserting `citation_gate` true
— from the re-record for a mechanism this build no longer runs, because ruling
D6 retired the coercion that key named. The key is kept deliberately: dropping
it would shift `SUBSTRATE_FLAG_KEYS` and move the `flags` cell of all four
committed MANIFESTs, which this card forbids. It now carries the one history
line [the lever-retirement procedure](../../docs/agent-procedures.md#retiring-substrate-levers)
requires, in the registry comment and in the `.env.example` note, so a reader
of a post-merge stamp is told what the cell does and does not mean. No
committed byte moves here: the stamp's SHAPE, key order and values are
unchanged.

## Validation

`uv run pytest tests/meetings tests/api tests/agents tests/orchestrator
tests/eval tests/experiments tests/training tests/scripts
tests/test_firewall.py -q` (fake and replay providers only),
`uv run lint-imports`, `npm --prefix frontend test`,
`uv run python scripts/validate_task_docs.py`,
`uv run python scripts/check_doc_facts.py`,
`uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`),
`bash scripts/verify_samples.sh`, the four
`build_sample_report.py --sample-dir <set> --check` runs over the two
`replays/samples/` and two `replays/ml_corpus/` sets, the counts-only commands
behind this card's two tables, and `bash scripts/check.sh` to the end rather
than to the first gate. No live evaluation, calibration, recording or provider
call is a check.

## Results

Delivered on `work/grounded-skip-and-guard-labels`, branched from `038a22a5`
(the alibi card's merge, PR #474). The architecture this rests on:
[AGENTS.md](../../AGENTS.md) load-bearing rules 1 and 5 (a deterministic engine;
invalid input raises, no silent fallbacks) and craft rules 2, 3, 4, 5, 6 and 7;
[docs/architecture.md](../../docs/architecture.md) on the meeting layer and the
observation firewall; and
[the lever-retirement procedure](../../docs/agent-procedures.md#retiring-substrate-levers).
The behaviour change is ruling D6 of
[the direction of 2026-09-19](../direction-2026-09-19-process-over-outcome.md)
§12, which supersedes AGENTS craft rule 7's default-OFF requirement for this
wave; §7 of the same memo is the shape it asks for — "the layer labels; it
never rewrites".

Every file:line in Acceptance above was taken at `cdefb7a6`, before the alibi
card landed. Each was re-anchored by SYMBOL at this branch point and the true
lines are cited below. No cited construct had been removed or re-aimed by the
alibi card, so nothing here needed a stop-and-report.

### What changed

**Every ballot declares a basis.** `ModelAuthoredVoteBallot` gains
`decision_basis: BallotDecisionBasis | None = None` (`meetings/schemas.py:1016`),
with the closed set as a named alias at `:975` so the schema and the pre-pass
cannot disagree about it. `None` is what every committed recording parses to
and means the voter answered nothing; `"none_held"` is its explicit statement
that it holds nothing that resolves. An out-of-set token is dropped from the
raw payload before validation by `_prepared_ballot_payload`
(`meetings/manager.py:3057`, the renamed pre-pass that strips the layer-owned
keys), which reports the dropped value so the call site prepends
`INVALID_BASIS_MARKER` (`:438`) at `meetings/manager.py:2352` — after taking a
copy of the model's own body, so the marker survives the teammate firewall's
rationale redaction instead of being redacted as model prose. The marker is
registered as the `invalid_basis` spectator chip (`api/replay_loader.py:3613`),
so it never reaches `rationale_text_clean`.

**The suspicion-argmax redirect is retired outright.**
`guard_ballot_target_graph`, its private `_render_gate_value` helper, its call
site and the four test classes pinning it are deleted, and
`tests/meetings/test_manager_gate_band.py` goes with them.
`BALLOT_TARGET_REDIRECT_MARKER` (`meetings/manager.py:333`) and the
`under_gate_redirect` member of `BallotTargetRewriteReason`
(`meetings/schemas.py:886`) survive as read-only history, both re-documented as
such, because 83 committed ballots carry the marker and four consumers parse
it. `TestTheRetiredGuardsMintNothing` walks `agents/`, `api/`, `eval/`,
`meetings/`, `orchestrator/` and `training/` with `ast` and fails on any
`<MARKER>.format(...)` call site for the three retired markers; a companion
case runs the same scan over `INVALID_REASON_ID_MARKER` and asserts it finds
one, so an empty result is a fact about the tree and not about the scanner.

**`guard_ballot_citation` became `label_ballot_grounding`**
(`meetings/manager.py:3733`) and rewrites nothing. It writes one
`grounding_label` (`meetings/schemas.py:1079`, alias at `:923`) on `VoteBallot`
only, in the card's precedence, and returns a ballot identical in every other
field. The subject is the EJECT's target and, for a SKIP,
`considered_alternatives` when non-empty and `candidate_targets` otherwise
(`_ballot_grounding_subjects`, `:3706`). `invalid_citation` is separated from
`uncited` by `citation_nulled`, computed at the call site
(`meetings/manager.py:2376` and `:2448`) from the ballot before and after the
two citation validators.

**The tally is untouched.** `tally_ballots` (`meetings/voting.py:192`) takes no
new argument and its body names no label; the decision and its reason are
recorded in its docstring.
`TestTheTallyNeverReadsTheLabel::test_the_tally_takes_no_label_argument_and_names_no_label`
parses `meetings/voting.py` with `ast` and asserts the function body mentions
neither `grounding_label` nor any of its seven values, and a parametrized case
runs the tally under all eight label values and gets one outcome.
`TestTheOnlyTargetRewrites` scans every `ballot_target_rewrite_provenance` call
site in the five live packages and asserts the reachable reasons are exactly
`{invalid_target, teammate_coerced}`, with `parse_default` the third and last,
written directly by `_vote_parse_default`.

**Citation relevance is retired as a lever.** Deleted: the field on
`MeetingEvidenceProfile` and `RecordedExperimentConfig`, both validator entries,
the `None`-omission branch, `CITATION_RELEVANCE_ENV` and its
`EXPERIMENT_ENV_NAMES` row, the `.env.example` block, the
`orchestrator/game.py` runner-agreement key, the `tests/api/test_leak.py`
allowlist entry, the four `AILIBI_CITATION_RELEVANCE` exports under
`experiments/`, both instrument arms' keywords, and
`experiments/citation_relevance_counterfactual.py` with
`tests/experiments/test_citation_relevance_consumers.py`.
`scripts/check_doc_facts.py` derives the registry size from
`len(EXPERIMENT_ENV_NAMES)` and now reports four switches. The rule survives as
the labeller's ONE definition: `meetings/citation_relevance.py` gains
`citations_bear_on_any` (`:143`) and `citations_bear_on` (`:216`) is literally
that call with a one-element pool, which
`test_the_one_subject_case_is_the_pooled_rule` asserts over every shape the
module can build rather than on one example.

**One prompt clause, one per-template bump.** `vote_ballot.j2:259` loses "a call
you cannot source either way is a call to SKIP, and a SKIP needs no citation"
and `:268` loses "a SKIP needs neither", replaced by the SKIP register harvested
from `vote_ballot_accounts.j2`; `:262`'s key count moves 7 → 8 and `:263`'s
skeleton gains `"decision_basis"`, carried NULL — the voter states its basis
and never copies one (review round 3; the same holds of
`vote_ballot_accounts.j2:23`). The marker at `:3` and the `qwen3_6_27b`
entry in `PROMPT_VERSION_SETS` (`orchestrator/game.py:435`) advance
`vote_ballot` ALONE, v6 → v7, in the Task 15.5 `qwen3_32b` form. The cascade
also moves `REQUIRED_PROMPT_VERSIONS_BASE` (`scripts/record_ml_corpus.sh:169`),
the live-registry and marker-equality pins, and the four lever-arm overlays
(see decision 7). Recorded-manifest pins do NOT move: every committed replay
stamps `.v5` and reads as recorded.

**The spectator reads both.** `BallotView` (`api/schemas.py:1082-1083`),
`_ballot_view`, `frontend/src/types/api.ts:391-392` and the two
`tests/api/test_leak.py` allowlists mirror them with `None` defaults;
`BallotCard.tsx` renders the label as one plain-language chip beside the
alternatives heading, behind the same perspective gate as the citations.
`rewriteLabel` keeps its `under_gate_redirect` and `uncited_coerced` cases and
the `BallotCard.tsx:292-294` redirect disclosure, and gains `off_target_coerced`
and `invalid_basis`. Every label value has a `docs/glossary.md` entry, as does the
stated basis. A label this build has not been taught renders nothing rather
than a guess.

### Decisions

1. **The tally reads no label, and an unsupported EJECT is tallied for the
   player the voter named.** Ruling D6's reason, restated in `tally_ballots`'s
   docstring: the shown decision must be the agent's, and dropping an
   unsupported EJECT is the engine deciding one-sidedly toward SKIP. The
   coercion removed reached 6 of 2,516 committed `ml_corpus/9p2i` ballots and 0
   of 869 in `samples/9p2i` (re-measured at this head, below).
2. **A second writer of `grounding_label`, stated rather than hidden.** A
   deadline miss and a twice-failed completion both return before the guard
   chain starts, so `_default_vote` (`meetings/manager.py:3001`) states
   `not_assessed` itself. That is the same value the labeller derives for any
   ballot whose target is the layer's, and it is what leaves every
   live-recorded ballot labelled — which is what reserves `None` for a
   recording made before the field. The schema docstring says "two writers, and
   no third" rather than the card's "written by the labeller and by nothing
   else", because that is what the code delivers.
3. **`decision_basis` and `grounding_label` are elided when `None`.** Required,
   not cosmetic: the committed `tournament-eval-report.json` of all four sets
   embeds recorded ballots, so writing `"decision_basis": null` moved bytes in
   four reports and turned all four `--check` runs red. `None` and an absent key
   say the same thing — no basis was stated — so they get one spelling. The
   elision also keeps `VoteBallot.model_dump_json()` re-validatable against
   `ModelAuthoredVoteBallot`, which is `extra="forbid"` and is what every test
   helper and fake provider feeds back.
4. **The reconstruction walk reads the recorded DECISION as recorded.** This is
   the card's own mechanism — "every recorded shape is read as recorded" —
   applied to `walk_replay_meetings`, the shared instrument behind the byte
   golden, `tests/agents/test_episodic_ids.py`,
   `tests/agents/test_beliefs_hard_evidence_gate.py`,
   `tests/meetings/test_corroboration.py` and
   `scripts/counterfactual_phase21.py`. That walk drives the LIVE meeting
   layer, so retiring two target-rewriting guards changes what it decides on
   old bytes; re-deriving the world advance from today's guards made every
   committed recording unwalkable, which is exactly what this card forbids
   before the re-record. `_run_recorded_meeting` now swaps the recorded
   outcome, ejected player and ballots into the `result` every consumer reads,
   keeps the re-derived ballots under `ReconstructedMeeting.rebuilt_ballots`,
   and `test_every_reconstruction_divergence_is_a_retired_guard` measures and
   explains the difference rather than dropping it. The `state_hash_after`
   check is unweakened on the ENGINE leg, and — restated at exactly that
   strength in review round 3 — the engine leg is now the whole of what it
   pins: it still applies a result to the reconstructed state and demands the
   recorded bytes, so drift in `apply_meeting_result`, in the tick walk or in
   the recording fails it loud. It no longer pins the BALLOT leg even
   transitively, because the decision it applies is read as recorded rather
   than re-derived. What says today's chain still REACHES that decision is the
   divergence census, ballot by ballot against `rebuilt_ballots`, and nothing
   else.
5. **The pre-pass's reach is stated, not overclaimed.** Acceptance says an
   out-of-set basis "never defaults the vote". That holds for every payload
   that reaches the manager, which is what `_prepared_ballot_payload` governs.
   It does NOT hold on a client that validates the authored schema first: all
   three shipped adapters do, and `_FrozenModel` is `extra="forbid"`, so there
   an out-of-set basis is a schema violation like any other and takes the
   existing provider-level retry and then the parse default — the identical
   limit the guard-provenance strip beside it has had since it shipped.
   `test_a_validating_adapter_refuses_the_fabrication_first` pins that half,
   and `_UnvalidatingClient` exists so the pre-pass is exercised at all.
6. **No `eval/process_scorecard.py` reader was added.** That module is not in
   this card's Expected scope and the scorecard's published columns belong to
   another card; adding a row here would move
   `docs/process-scorecard.{md,json}`, which this card's Record impact forbids.
   Which rows change meaning at the re-record is under Limitations.
7. **The lever-arm overlays now spread the default registry.** All four
   (`impostor_roll_call`, `reporter_reasoning`, `corroboration_discipline`,
   `testimony_shapes`) restated `_bespoke_versions(..., version="v6")` and then
   overrode some keys. With a PER-TEMPLATE bump that is a live bug: an arm that
   does not override `vote_ballot` would serve the v7 body under the v6 stamp.
   Each now spreads `PROMPT_VERSION_SETS["qwen3_6_27b"]`, which is what their
   own comments already claimed they did, and a new pin asserts the roll-call
   arm's vote stamp equals the default one.
8. **The SKIP's id-shape discipline is harvested minus the row-suffix clause.**
   `vote_ballot_accounts.j2` warns against appending `":claim:N"` / `":obs:N"` /
   `":whereabouts:N"` because `_account_transcript.j2` renders those tags. The
   served `vote_ballot.j2` renders no such tag, so naming them would be
   unexplained jargon in model speech (AGENTS craft rule 4). The discipline is
   carried as "copy it VERBATIM from between the brackets, WITHOUT the square
   brackets themselves and with nothing appended to it".
9. **`experiments/held_out_prefixes.py`'s restamp note is untouched.** Its line
   1453 names `citation_relevance_version` inside a dated `DEPENDENCY_RESTAMPS`
   record of what a past card did. That is history, not a description of live
   behaviour, and the deduction evaluation is closed. No `GENERATOR_SOURCES`
   file's scripted prefixes move, so no restamp is owed and the two archive
   readers stay green.
10. **Three files the diff touches are not in `## Expected scope`, recorded
    here rather than written into it (review round 3, 2026-09-21).** Expected
    scope is what the card asked for before the work; a file discovered during
    it is declared, not retrofitted. The three:
    `agents/strategic/prompts/qwen3_5_9b/vote_ballot.j2` and
    `eval/process_scorecard.py`, both comment-only sweeps of sentences that
    said an uncited EJECT coerces (the card's own prose-sweep requirement
    reaches whatever file carries the sentence, which is why neither needed a
    scope amendment to be correct); and
    `experiments/fresh_deduction_instrument.py` beyond the one keyword Expected
    scope names — `assert_the_revised_wave_is_enabled`, `REVISED_WAVE_LEVERS`
    and `CalibrationMode.requires_the_revised_wave` are deleted with the lever
    they gate, because `RecordedExperimentConfig` is `extra="forbid"` and a
    wave assertion over a field that no longer exists cannot be written at all.
11. **A test pin moved off a closed evaluation's archive, declared here
    (review round 3, 2026-09-21).** `TestUsageReplay` read the terminal/partial
    SHAPE off a paragraph of `audits/deduction-candidate/execution-manifest.md`
    that quotes "49 terminal units with one `partial`" against "16 terminal
    units and 34 `partial`" — a split that paragraph itself attributes to the
    relevance rule of 2026-09-18 meeting an ARCHIVED distribution, and says
    read 50 and none with the rule OFF. Ruling D6 retired the coercion that
    rule drove, so the archive's meetings decide again and the shape is back to
    50 and none. The manifest is the record of a spent sitting and no card may
    rewrite it, so the assertion moved into the test
    (`assert [arm.terminal_units for arm in report.arms] == [50, 50]` and
    `[0, 0]`), where it carries its own explanation. The token counts are still
    read off the manifest; no `audits/` byte moves, so no `docs/artifacts.md`
    row is recomputed.
12. **Two unreachable-by-construction lines in the labeller are KEPT, and say
    so (review round 4, 2026-09-21).** The round-4 walk found two guards no
    perturbation can turn red, and keeping or removing them is a decision
    rather than a finding. Both stay, and `label_ballot_grounding`'s docstring
    names them with the construction that makes them unreachable, so no later
    reader re-derives them as an unenforced-line report. `invalid_citation` can
    never race `supported` / `off_target`, because the one call site computes
    `citation_nulled` as "cited before the validators AND both ids `None` after
    them"; it stays BELOW them because that is the correct order for a caller
    that holds both, which is a grader's shape over recorded bytes. The
    `ballot.target != _SKIP_TARGET` half of the `flag_only` guard can never
    decide the label, because every live `ContradictionRef.subjects` entry is a
    speaker or a claim subject and never the literal `"SKIP"`; it stays because
    `PlayerId` is `str` and nothing in the type forbids that value, and because
    `flag_only` is defined as an EJECT's word. What this card forbids is an
    unexplained unenforced line; an explained one is a defensive line.

### Verification

Every command run from this worktree, exit codes captured directly (never
through a pipe). **Measured at the round-4 head** — the table carries the round
it was taken at because three of its cells were once stale under a heading that
claimed the head of the day (review round 3): it read 8,153 for 8,158 passed,
1,810 for 1,813, and 38 for 40 at `7e6747c7`. Every cell below is re-measured
at THIS head; round 4's cases move four of them, and `tests/training` joins the
table because this round edits `training/surrogate/`. The dated round-1,
round-2 and round-3 tables below are the record of THOSE heads and are not
re-measured.

| command | result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 — 8,167 passed, 20 skipped, 3 xfailed; 4 import contracts kept, 0 broken; 73 work cards validated; 390 prompts in sync; 552 frontend tests; frontend build OK |
| `uv run mypy .` | Success: no issues found in 488 source files |
| `uv run ruff check .` / `ruff format --check .` | All checks passed / 517 files already formatted |
| `uv run pytest tests/meetings tests/api -q` | exit 0 — 1,821 passed, 2 skipped |
| `uv run pytest tests/meetings/test_grounding_label.py -q` | exit 0 — 45 passed |
| `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` | exit 0 — 25 passed |
| `uv run pytest tests/agents tests/experiments -q` | exit 0 — 1,977 passed |
| `uv run pytest tests/training -q` | exit 0 — 472 passed, 335 deselected |
| `bash scripts/verify_samples.sh` | exit 0 — 50/50 + 50/50 = 100/100 clean |
| `uv run python scripts/build_sample_report.py --sample-dir replays/<set> --check` ×4 | exit 0 — consistent on all four sets |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0 — consistent |
| `uv run python scripts/validate_task_docs.py` | exit 0 — 73 work cards |
| `uv run python scripts/check_doc_facts.py` | exit 0 — 26-lever substrate registry, 4-switch experiment registry |
| `uv run python scripts/generate_prompts.py --check` | exit 0 — all 390 prompts in sync |
| `uv run python scripts/verify_ml_evidence.py` | exit 0 — 61 checks, 0 FAIL, 7 evidence-branch-absent |
| `npm --prefix frontend test` / `run build` | 552 passed / built |

No live provider call, no calibration, no recording, no re-record. Band
2100-2999 was not generated or opened and
`scripts/verify_ml_evidence.py --complete` was not run.

**The retired markers on committed bytes, re-measured at this head.** Counts
only, keyed by set; no rationale, prompt or seed-band prefix is printed.

| set | ballots | `under_gate_redirect` | `uncited_coerced` | `off_target_coerced` |
| --- | --- | --- | --- | --- |
| `ml_corpus/9p2i` | 2,516 | 57 | 6 | 0 |
| `ml_corpus/4p1i` | 129 | 2 | 0 | 0 |
| `samples/9p2i` | 869 | 23 | 0 | 0 |
| `samples/4p1i` | 117 | 1 | 0 | 0 |
| all | 3,631 | 83 | 6 | 0 |

That is the card's Evidence table reproduced at this branch point, and it is
the arithmetic behind the read-as-recorded decision: 89 recorded ballots carry
a marker no live path mints any more, and the spectator must keep rendering
them exactly as before.

**What today's chain would decide differently.**
`test_every_reconstruction_divergence_is_a_retired_guard` drives every
committed sample meeting through the live manager on its recorded completions
and compares ballot by ballot:

| set | meetings | ballots | targets that move | meetings holding one |
| --- | --- | --- | --- | --- |
| `samples/9p2i` | 151 | 869 | 23 | 14 |
| `samples/4p1i` | 39 | 117 | 1 | 1 |

The third column equals that set's `under_gate_redirect` count exactly, which
is the arithmetic statement that the reconstruction restores every redirect and
moves nothing else. The test asserts it per ballot as well: a ballot whose
target moves must carry a retired reason, and its new target must equal the
`guard_redirected_from` that guard preserved.

### The planted failures

Sixteen probes at the first head, five more in
[round 1](#review-corrections-round-1-2026-09-21), two in
[round 2](#review-corrections-round-2-2026-09-21), twenty new ones in
[round 3](#review-corrections-round-3-2026-09-21) and thirteen in
[round 4](#review-corrections-round-4-2026-09-21) — fifty-six. Round 3 also
RE-MEASURED six lines an earlier round had already probed, because its new
cases move their counts; those six carry both figures in the round-3
call-surface table and are not counted again. Each probe neutered ONE
production line, ran the selection, and was reverted; both counts are recorded.
The claim at the first head, that every line this card changed in a production
module had one, was WRONG, and was wrong twice more after that: round 1 found
the provenance-boundary line (`meetings/manager.py:2352`) unprobed, round 2
found the `_ballot_view` mirrors unprobed, and round 3 found four more — the
labeller's `turns=` and `candidate_targets=` arguments, the `invalid_basis`
row of `api/replay_loader.py`'s marker table, and the two `rewriteLabel` cases
`BallotCard.tsx` gained. All four are planted now. Round 3's claim that its
table was a walk of the WHOLE call surface was itself wrong, and round 4 says
so: five more lines were unenforced at `53335618`, three of them named by the
round-4 verifiers and two found by walking the diff again. That walk, and the
two lines it records as unobservable rather than planted, are in the round-4
subsection.

| probe (line neutered) | perturbed | restored |
| --- | --- | --- |
| `supported`/`off_target` collapsed to `supported` | 3 failed, 58 passed | 61 passed |
| the `invalid_citation` branch removed | 1 failed, 37 passed | 38 passed |
| the `none_held` branch removed | 1 failed, 37 passed | 38 passed |
| the `flag_only` branch removed | 1 failed, 37 passed | 38 passed |
| the `not_assessed` branch removed | 1 failed, 37 passed | 38 passed |
| the SKIP subject pool reduced to `candidate_targets` | 1 failed, 37 passed | 38 passed |
| the pre-pass's `isinstance` guard removed | 2 failed, 36 passed | 38 passed |
| `INVALID_BASIS_MARKER` never prepended | 6 failed, 32 passed | 38 passed |
| `_default_vote`'s `not_assessed` removed | 2 failed, 36 passed | 38 passed |
| `decision_basis` elision removed | 10 failed, 14 passed | 24 passed |
| `grounding_label` elision removed | 40 failed, 227 passed | 267 passed |
| `citations_bear_on_any` reads only the first subject | 1 failed, 60 passed | 61 passed |
| the SKIP register removed from `vote_ballot.j2` | 1 failed, 26 passed | 27 passed |
| a live `BALLOT_TARGET_REDIRECT_MARKER.format(...)` re-added | 1 failed, 37 passed | 38 passed |
| `tally_ballots` made to name `grounding_label` | 1 failed, 37 passed | 38 passed |
| the reconstruction made to carry the re-derived decision | 2 failed, 23 passed | 25 passed |

**One probe first came back green, and is recorded as such.** The last row
initially read `25 passed` perturbed: nothing pinned that
`ReconstructedMeeting.result` carries the RECORDED decision, only that the
world advance did. `scripts/counterfactual_phase21.py` reads
`meeting.result.ejected_player_id`, so that gap was real — its OFF ledger would
have drifted silently. Three assertions were added inside the divergence census
(`result.outcome`, `result.ejected_player_id` and `result.ballots` equal the
entry's, on every meeting), and the same probe then read `2 failed, 23 passed`.

A defect the plants caught rather than confirmed: `basis not in
_VALID_DECISION_BASES` raised `TypeError` on an unhashable value, so a model
sending `"decision_basis": {...}` would have killed the meeting instead of
losing its declared basis. The `isinstance` test now runs first, and the
parametrized case covers a number, a list, an object, `"CITED"` and
`" none_held"`.

### Limitations

* **`uncited_coerced` is untested by the reconstruction census.** Both sample
  sets read 0 for it; the 6 that exist are in `ml_corpus/9p2i`, which the byte
  golden does not walk. The per-ballot assertion covers the reason, but only
  `under_gate_redirect` exercises it on committed bytes.
* **`off_target_coerced` has no recorded instance at all**, because the lever
  was never ON in a committed recording. Its marker, its
  `BallotTargetRewriteReason` member and its spectator chip are kept for
  readers written against the old vocabulary, and nothing exercises them over
  real bytes.
* **Two process-scorecard rows change meaning at the re-record, and neither
  moves now.** `agent_authored_share` counts a ballot as agent-authored when it
  carries neither a typed `guard_rewrite_reason` nor a target-rewriting marker;
  from the re-record no ballot carries `under_gate_redirect` or
  `uncited_coerced`, so the share rises for a reason that is the ruling and not
  a measured improvement. `uncited_ejects` counts EJECTs whose citation does not
  resolve; before this card such a ballot was coerced to SKIP and left the EJECT
  denominator, so that row will rise too. Both read unchanged on committed
  bytes, where `grounding_label` is `None` throughout.
* **The label mix is not yet a published row.** It reads `None` on every
  committed recording and first carries values at the re-record; the scorecard
  card owns the row's definitions.
* **The behaviour change is unmeasured on new bytes.** No recording was made
  here, by the card's own constraint. The equivalent substitution over committed
  bytes moved 17 of 590 meeting outcomes, two-sided, and the reconstruction
  census above is the same class of estimate — neither is a recording at this
  head, and neither is an accuracy argument.
* **The spectator chip is invisible in the shipped tour** until the re-record,
  because every committed ballot reads `None`. The frontend test asserts that
  absence deliberately, so the shipped pages are byte-unchanged.
* **Role-correctness gates nothing here**, as ruling D1 requires. No threshold,
  ordering or exemption in the labeller was chosen against it, and it appears in
  no acceptance item.

### Review corrections, round 1 (2026-09-21)

Eleven blocking findings from three independent lenses, eight distinct defects
(two pairs were the same defect found twice: the accounts revision and the
byte-golden census). Every command quoted below was run from this worktree at
this head.

**1. The new marker was invisible to the eval marker chain.**
`INVALID_BASIS_MARKER` was registered in `api/replay_loader.py` and
`training/surrogate/dataset.py` but not in `eval/deduction_metrics.py`'s
`_BALLOT_MARKER_CHAIN` (`:717-725`), the ONE table that answers every
guard-origin question. That scan is anchored and stops at the first prefix it
cannot name, so the machinery's own sentence would have fallen on the MODEL side
of the provenance split and been read as the voter's words — from the re-record,
not today: 0 committed bytes carry the marker, which is why every gate was
green. The row is added beside the two citation-id markers it is shaped after,
with the consequence written into the table's comment.

**2. The provenance-boundary line had no probe.** Moving
`authored_rationale_text = parsed.rationale_text` (`meetings/manager.py:2352`)
to after the marker prepend left `tests/meetings tests/api` at
`1810 passed, 2 skipped` — fully green — while silently dropping the
invalid-basis marker from every betrayal ballot, because
`_preserved_ballot_markers` splits on that string. The card claimed every
production line it changed had a probe; that claim was wrong and is corrected
above the probe table. `test_a_fabricated_basis_survives_the_teammate_redaction`
now drives an impostor voter naming a teammate with an out-of-set
`decision_basis` through the real manager and asserts the recorded rationale is
exactly the teammate marker, the invalid-basis marker with its payload redacted,
and the substitution note — with the same betrayal minus the fabrication beside
it, so the assertion is about THIS marker.

**3. The authored schema's docstring undercounted the layer's fields.** It said
two (`guard_redirected_from` / `guard_rewrite_reason`) where the code has three;
`grounding_label` is the third, and `_LAYER_OWNED_BALLOT_FIELDS`
(`meetings/manager.py:3027-3031`) already listed all three. Rewritten to name
three and to say why the third belongs there.

**4 and 5. The accounts body moved without its revision.**
`vote_ballot_accounts.j2` gained the SKIP-basis register and a `decision_basis`
skeleton key while `ACCOUNT_PROMPT_SET_REVISION` stayed `v5`, against that
constant's own rule that two generations of one template never share a stamp.
The revision advances to `v6` with a history bullet, the `v5` bullet is
corrected where it described the pre-edit body, and the gate moves with it:
`_PRE_V6_REVISIONS` now holds `v1`-`v5` and
`test_a_body_carrying_the_v6_bounds_cannot_be_stamped_an_older_revision` asserts
the v6 spans (the basis register, the `none_held` token, the vote-stands
sentence and the corrected consequence) beside the constant. Cutting the edit
back was the alternative and was rejected: the prose correction alone moves the
body's bytes, so the revision was owed either way, and leaving the shelved
family's SKIP without the basis vocabulary would put two ballot bodies in one
set asking for two different decision records. Declared in Record impact.

**6. Two published-looking figures no test could refute.** The
`ReconstructedMeeting` docstring said the retirement moves "41 of the 1,215
committed sample ballots and 9 of the 252 meetings"; the executable census in
the same file pins `(151, 869, 23, 14)` and `(39, 117, 1, 1)` — 24 moved of 986
ballots across 15 of 190 meetings, which is what the card's own table, the PR
body and commit `23ca3260` state. The docstring now states those figures and
names the census that pins them.

**7. A stacked fabrication was uncountable in the surrogate reader.**
`training.surrogate.dataset.ballot_rewrite_labels` stopped as soon as it
consumed the marker naming `guard_rewrite_reason`, but every target guard runs
AFTER the citation validators and the basis pre-pass, so on a betrayal ballot
the basis marker sits BEHIND the teammate marker and was dropped —
`api.replay_loader` reported `(teammate_coerced, invalid_basis)` where this
reader reported `(teammate_coerced,)`. The stop is now bounded to TARGET
markers, which is the only class that cannot legitimately sit behind the bound,
and the docstring states that at exactly that strength: a fabricated target
class still cannot be minted past the bound, a fabricated citation class can, as
on a legacy recording. It closes the 7-annotation gap the committed-bytes census
carried: `invalid_reason_id` 1 → 5 and `invalid_observation_id` 12 → 15, so
127 annotations now meet 127 claimed labels. No recorded byte moves, no fit-side
exclusion moves (neither label is in `TARGET_REWRITE_LABELS`, and
`per_set_rewritten` still reads `[27, 70, 1, 2]`), and `ballot_coerced_skip` is
untouched at 6.

**8. Two Results citations did not resolve.** `frontend/src/types/api.ts:393`
/`:397` and `BallotCard.tsx:154-156` were stale; the true lines are
`api.ts:391-392` and `BallotCard.tsx:291-292`, and the Results text above now
carries them.

**The prose sweep, finished.** `agents/strategic/prompts/loader.py` was named in
Expected scope for it and had been missed entirely; its v4 and v5 bullets said
an uncited ejection is coerced. Swept with it, in the same commit:
`meetings/voting.py:122-137` (the two-rewrite stack is now stated as recorded
history, with the reason no live chain stacks), `meetings/manager.py:818-824`
and `:2828-2840`, `agents/memory/beliefs.py:333-339`,
`scripts/counterfactual_phase21.py`'s C-7 row note (a live description, not the
published memo row, which stays untouched as the record of a past measurement),
`tests/agents/test_absence_prior.py:25-30` and `:685-690` (which also pointed at
`tests/meetings/test_citation_gate.py`, a module this card deleted), and
`experiments/fresh_deduction_instrument.py:5138-5140` and `:5309-5313`. Two
stale counts introduced by the card's own edit went with them:
`training/surrogate/dataset.py:188-189` and `:243` called the eight-entry
marker table "seven kinds". A duplicated `Defensive normalization` comment block
the card had left stranded in `_collect_vote` was deleted.

The sweep is enforced by reading the tree, not by a gate — no test pins prose.
The grep that closed it, and its result at this head:

```
grep -rn "coerces it to SKIP\|coerces an uncited\|coerces the uncited\|still coerces\|then coerces" . \
  --include="*.py" --include="*.j2" --include="*.ts" --include="*.tsx" \
  --exclude-dir=.venv --exclude-dir=.git --exclude-dir=node_modules
```

It returned four more sites after the eight above — `api/replay_loader.py:3587`,
`tests/api/test_view_model.py:407`, `tests/meetings/test_vote_tally_parity.py:154`
and `tests/training/test_surrogate_dataset.py:995`, each describing the
16.5-then-16.6 stack in the present tense — and returns nothing now. Every one
of them still describes the RECORDED pair; what changed is the tense and the
sentence naming the retirement, because those bytes are read for as long as the
recordings exist.

**The round-1 probes.** Five more, each neutering ONE production line, run, and
reverted.

| probe (line neutered) | perturbed | restored |
| --- | --- | --- |
| the `INVALID_BASIS_MARKER` row dropped from `_BALLOT_MARKER_CHAIN` | 1 failed, 117 passed | 118 passed |
| the provenance boundary read AFTER the marker prepend | 1 failed, 38 passed | 39 passed |
| the surrogate strip's unbounded early return restored | 2 failed, 38 passed | 40 passed |
| the surrogate strip's TARGET-class bound removed | 2 failed, 38 passed | 40 passed |
| `ACCOUNT_PROMPT_SET_REVISION` set back to `v5` | 1 failed, 92 passed | 93 passed |

The second row is the one that matters most: before this round the same
perturbation read `1810 passed, 2 skipped` over `tests/meetings tests/api`.

**Verification at this head.** Commands run from this worktree, exit codes
captured directly.

| command | result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 — 8,156 passed, 20 skipped, 3 xfailed; mypy clean over 488 files; 73 work cards validated; 390 prompts in sync; 550 frontend tests; frontend build OK |
| `.venv/bin/python -m pytest tests/meetings/test_grounding_label.py -q` | 39 passed |
| `.venv/bin/python -m pytest tests/eval/test_deduction_metrics.py -q` | 118 passed |
| `.venv/bin/python -m pytest tests/training/test_surrogate_dataset.py -q` | 40 passed |
| `.venv/bin/python -m pytest tests/agents/test_public_account_prompts.py -q` | 93 passed |
| `bash scripts/verify_samples.sh` | 50/50 + 50/50 = 100/100 clean |
| `.venv/bin/python scripts/build_sample_report.py --sample-dir replays/<set> --check` ×4 | consistent on all four sets |
| `.venv/bin/python scripts/publish_process_scorecard.py --check` | consistent |
| `.venv/bin/python scripts/verify_ml_evidence.py` | offline, no FAIL rows |
| `.venv/bin/python scripts/validate_task_docs.py` | passed |
| `.venv/bin/python scripts/check_doc_facts.py` | verified |

No live provider call, no calibration, no recording and no re-record in this
round either; band 2100-2999 was not generated or opened and
`scripts/verify_ml_evidence.py --complete` was not run. No `audits/` or
`tests/fixtures/` byte moved, so no `docs/artifacts.md` row is recomputed.

### Review corrections, round 2 (2026-09-21)

Six blocking findings from three independent lenses, five distinct defects
(findings 3 and 6 are the same unfinished prose sweep, reached from two
lenses). Every command quoted below was run from this worktree at this head.

**1. The stated `none_held`-over-`flag_only` precedence had no planted case.**
The ordering is a RULING, not an arithmetic necessity — a voter that says it
holds nothing must not be upgraded by the layer reading a flag on its behalf —
and it was the one branch pair whose order nothing pinned: lifting the
`flag_only` branch above `none_held` left the whole suite byte-identical,
because `none_held` appeared in tests only on SKIP targets, where `flag_only`
cannot fire. `test_a_declared_none_held_outranks_a_flag_on_the_target` plants
it through the manager chain: two turns place p-3 in two rooms across one
window, the detector mints one `alibi_conflict` naming p-3, and the voter
EJECTs p-3 with `decision_basis="none_held"` and no citation. The case asserts
the flag exists before asserting the label, and the SAME meeting minus the
voter's word is asserted `flag_only` beside it, so the pin is about the ORDER
rather than about either branch being reachable.

**2. The spectator mirror in `_ballot_view` was an unprobed production line.**
Replacing both mirrors with `None` left `tests/api` and the full suite green:
the frontend cases build `BallotView` fixtures by hand, the leak test pins the
field NAMES against a frozenset, and every committed recording reads `None` for
both — so after the re-record the chip would have silently never rendered.
`test_ballot_view_mirrors_the_stated_basis_and_the_layers_finding`
(`tests/api/test_view_model.py`) drives a `VoteBallot` carrying both fields
through the seam, asserts both survive into `model_dump()`, and asserts the
`None` half beside it, which is the identity every committed recording takes.

**3 and 6. The prose sweep was not finished.** Round 1 closed it against five
phrases, case-SENSITIVELY. Re-run case-insensitively and widened to the two
deleted symbol names, it still hit six sites, five of them in files this card
edits. Swept in this round's commit, each stating the retirement at the
strength the code now delivers:

* `tests/meetings/test_manager.py:829-833` — said the graduated citation gate
  "coerces an UNCITED zero-flag eject" in the present tense. Now: the ballots
  were written that way FOR that gate, ruling D6 retired the coercion, and the
  citations today only decide `supported` versus `uncited`.
* `tests/eval/test_meeting_quality.py:5-11` — a `:func:` link to
  `guard_ballot_citation`, a function this PR deletes, in the present tense.
  Now names the retirement and the labeller that replaced it, and says the
  bucket counts 6 committed `ml_corpus/9p2i` ballots.
* `tests/eval/test_meeting_quality.py:291-297` — "the citation gate is the LAST
  guard in the manager's ballot chain". Now past tense, with the anchor stated
  as a fact about recorded bytes.
* `tests/meetings/test_corroboration.py:1397-1400` and `:1955-1959` — the
  zero-flag predicate, attributed to a live `guard_ballot_citation`. Now
  attributed to the retired gate AND to `label_ballot_grounding`'s `flag_only`
  branch, which is the live reader of that predicate.
* `tests/experiments/test_fresh_deduction_instrument.py:10153-10160` — "Both
  authored ballots pass `guard_ballot_citation`". Now: they carry no rewrite of
  the class that gate wrote, and both guards are history the instrument reads
  off recorded bytes.

Three further sites were live-tense claims about the retired gate that the
widened grep surfaced and no finding had named:
`eval/meeting_quality.py:277-282` and `:981-986` (the anchored-match comments,
"the citation gate IS the LAST guard"), and `meetings/manager.py:828-830` (the
persona render ordered "after the citation gate"). `scripts/check_doc_facts.py`
gained the D6 half of its sub-1.0 sentence. Sentences describing a RECORDING's
stamped substrate — `eval/watchability.py:758` is the example — were
deliberately left as recorded: they say what produced those bytes, which is
still true.

The two closing greps and their results at this head:

```
grep -rni "coerces it to SKIP\|coerces an uncited\|coerces the uncited\|still coerces\|then coerces" . \
  --include="*.py" --include="*.j2" --include="*.ts" --include="*.tsx" \
  --exclude-dir=.venv --exclude-dir=.git --exclude-dir=node_modules
```

returns nothing (exit 1).

```
grep -rn "guard_ballot_citation\|guard_ballot_target_graph" . \
  --include="*.py" --include="*.j2" --include="*.ts" --include="*.tsx" \
  --exclude-dir=.venv --exclude-dir=.git --exclude-dir=node_modules
```

returns six lines, and cannot return none: two are
`tests/meetings/test_grounding_label.py:799-800`, the gate that asserts BOTH
symbols are gone from the manager by name, and the other four are the swept
sites above, which name the retired symbols on purpose because the markers they
minted are still on 89 committed ballots. The result is quoted as what the tree
delivers rather than claimed empty.

**4. The retired citation gate still shipped as an unconditionally-ON lever.**
`guard_ballot_citation` became a labeller that rewrites nothing, but its lever
key `citation_gate` sits in `_RETIRED_ALWAYS_ON_LEVERS`, every snapshot stamps
it `True`, and both the registry comment and the `.env.example` note called
that class "unconditionally ON" / "always ON" — so each post-merge recording
and MANIFEST `flags` cell asserts a mechanism that no longer exists. The key
STAYS: dropping it shifts `SUBSTRATE_FLAG_KEYS` and moves the `flags` cell of
all four committed MANIFESTs. What changed is the truth around it — the one
history line
[the procedure](../../docs/agent-procedures.md#retiring-substrate-levers)
requires, at `orchestrator/replay.py:982-990` and `.env.example:120-126`,
naming `citation_gate` provenance-only since ruling D6; the registry comment at
`:973`, which now says twenty of the twenty-one name behaviour that is
unconditional in this build and this one does not; and the refusal message at
`:1259`, which says "stamped ON" rather than "unconditionally ON", with its
three pins in `tests/orchestrator/test_replay.py` moved with it. The
`.env.example` note keeps the "always ON" label its own gate requires
(`scripts/check_doc_facts.py` fails the file without it), because that label is
the class's, and carries the exception underneath it. Declared in Record
impact.

**5. Ten Results citations did not resolve at this head.** Commit `968ed6ab`
shifted them itself — the same defect class its own round-1 entry 8 fixed — so
this round re-anchored every one by SYMBOL and re-measured them AFTER the last
code edit of the round, which moved eight of them again by one line.
`meetings/schemas.py`: `decision_basis` 1010, `grounding_label` 1073,
`under_gate_redirect` 886. `meetings/manager.py`: the provenance boundary 2352,
`cited_before_validation` 2376, `citation_nulled` 2448, `_default_vote` 3001,
`_LAYER_OWNED_BALLOT_FIELDS` 3027-3031, `_prepared_ballot_payload` 3054,
`_ballot_grounding_subjects` 3703, `label_ballot_grounding` 3730.
`meetings/voting.py`: `tally_ballots` 192. `api/replay_loader.py`: the
`invalid_basis` row 3612. The round-1 subsection's two citations of the same
symbols moved with them, as did the Acceptance round-1 item citing the
provenance boundary. Each was re-derived by grepping the symbol and re-read at
the line now cited.

**The round-2 probes.** Two more, each neutering ONE production line, run, and
reverted. Both are red only because of this round's tests: the first is the
perturbation the finding reported as byte-identical over the full suite, the
second was green over `tests/api` AND the full suite.

| probe (line neutered) | perturbed | restored |
| --- | --- | --- |
| `flag_only` lifted above `none_held` in the precedence | 1 failed, 39 passed | 40 passed |
| both `_ballot_view` mirrors replaced with `None` | 1 failed, 437 passed, 2 skipped | 438 passed, 2 skipped |

**Verification at this head.** Commands run from this worktree, exit codes
captured directly (never through a pipe).

| command | result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 — 8,158 passed, 20 skipped, 3 xfailed; 4 import contracts kept, 0 broken; 73 work cards validated; 390 prompts in sync; mypy clean over 488 files; ruff clean and 517 files formatted; 550 frontend tests; frontend build OK |
| `.venv/bin/python -m pytest tests/meetings/test_grounding_label.py -q` | 40 passed |
| `.venv/bin/python -m pytest tests/api/test_view_model.py -q` | 50 passed, 1 skipped |
| `.venv/bin/python -m pytest tests/api -q` | 438 passed, 2 skipped |
| `.venv/bin/python -m pytest tests/orchestrator/test_replay.py -q` | 111 passed |
| `.venv/bin/python -m pytest tests/eval/test_meeting_quality.py -q` | 21 passed |
| `.venv/bin/python -m pytest tests/experiments/test_fresh_deduction_instrument.py -q` | 526 passed |
| `bash scripts/verify_samples.sh` | exit 0 — 50/50 + 50/50 = 100/100 clean |
| `.venv/bin/python scripts/build_sample_report.py --sample-dir replays/<set> --check` ×4 | exit 0 — consistent on all four sets |
| `.venv/bin/python scripts/publish_process_scorecard.py --check` | exit 0 — consistent |
| `.venv/bin/python scripts/verify_ml_evidence.py` | exit 0 — 61 checks, 0 FAIL, 7 evidence-branch-absent |
| `.venv/bin/python scripts/check_doc_facts.py` | exit 0 — 26-lever substrate registry, 4-switch experiment registry |
| `.venv/bin/python scripts/validate_task_docs.py` | exit 0 — 73 work cards |

No live provider call, no calibration, no recording and no re-record in this
round either; band 2100-2999 was not generated or opened and
`scripts/verify_ml_evidence.py --complete` was not run. No `audits/` or
`tests/fixtures/` byte moved, so no `docs/artifacts.md` row is recomputed, and
the `tasks/README.md` inventory sentence is unchanged because Status was
already `done` before this round.

### Review corrections, round 3 (2026-09-21)

Three blocking findings from the round-3 verifiers, and the smaller items
beside them. The first two are one defect reached twice: an argument of the
labeller's call site that no test enforced. Answering them properly meant
walking the WHOLE call surface this card added rather than the two lines the
findings named, and that walk found two more — both green, both now planted.
Every command quoted below was run from this worktree at this head.

**1. `turns=transcript.turns` at the labeller's call site had no enforcing
test.** Replacing it with `turns=()` in `_collect_vote` left the whole suite
green (8,158 passed at `7e6747c7`), yet it is not a no-op:
`citations_bear_on_any` resolves a cited turn id through `turns_by_id`, and an
id that resolves to no turn bears on NOBODY, so an EJECT citing a real turn
that names its target reads `supported` at head and `off_target` perturbed. The
reason nothing caught it: every `supported` assertion in the tree was on the
OBSERVATION channel (`prompt_lines`) or called the labeller directly with its
own `turns`. `test_an_eject_citing_a_turn_that_names_its_target_is_supported`
plants the turn channel through `MeetingManager`: p-1's opening accuses p-3, so
`m-1:turn-0` names p-3, and p-1's ballot EJECTs p-3 citing that turn. The case
asserts the cited turn is a real one of this meeting and that it is the turn
naming the target BEFORE asserting the label, and the off-target twin — the
same EJECT citing `m-1:turn-2`, where p-2 accuses p-4 and nothing names p-3 —
sits beside it, so the pin is about ABOUTNESS and not about an id resolving.

**2. `candidate_targets=candidate_targets` had none either.** Same
perturbation class, different branch: `_ballot_grounding_subjects` returns the
caller's `candidate_targets` for a SKIP that wrote down no alternatives — 23 of
the 1,359 shipped 9p2i SKIPs — and with a citation present and an EMPTY subject
pool `citations_bear_on_any` answers `False` by construction. So a SKIP citing
an own-observation line that names a living candidate reads `supported` at head
and `off_target` perturbed, and the suite stayed green.
`test_a_skip_that_weighed_nobody_is_read_against_the_living_pool` plants it
through the manager, with a twin citing a second own-observation line that
names only the VOTER: `_candidate_targets` is the living roster MINUS the
voter, so that citation bears on nobody in the pool. The twin is what makes the
case a statement about the POOL rather than about a citation surviving.

**The call surface, walked and probed.** Every argument of the labeller call,
every argument of the `citations_bear_on_any` call inside it, all three
branches of `_ballot_grounding_subjects`, and every other site this card added.
Each row neutered ONE line, ran the selection, and was reverted.

| site | line neutered | selection | perturbed | restored |
| --- | --- | --- | --- | --- |
| labeller call | `ballot=normalized` to `parsed` | `test_grounding_label.py` | 4 failed, 39 passed | 43 passed |
| labeller call | `contradictions=` to `()` | `test_grounding_label.py` | 1 failed, 42 passed | 43 passed |
| labeller call | `candidate_targets=` to `()` — NEW | `test_grounding_label.py` | 1 failed, 42 passed | 43 passed |
| labeller call | `candidate_targets=` to `()` — NEW | `tests/meetings tests/api` | 1 failed, 1,816 passed, 2 skipped | 1,817 passed, 2 skipped |
| labeller call | `citation_nulled=` to `False` | `test_grounding_label.py` | 1 failed, 42 passed | 43 passed |
| labeller call | `turns=` to `()` — NEW | `test_grounding_label.py` | 1 failed, 42 passed | 43 passed |
| labeller call | `turns=` to `()` — NEW | `tests/meetings tests/api` | 1 failed, 1,816 passed, 2 skipped | 1,817 passed, 2 skipped |
| labeller call | `prompt_lines=` to `()` | `test_grounding_label.py` | 2 failed, 41 passed | 43 passed |
| `citations_bear_on_any` | `cited_turn_id=` to `None` | `test_grounding_label.py` | 1 failed, 42 passed | 43 passed |
| `citations_bear_on_any` | `cited_observation_id=` to `None` | `test_grounding_label.py` | 2 failed, 41 passed | 43 passed |
| `citations_bear_on_any` | `subjects=` to `(ballot.target,)` | `test_grounding_label.py` | 2 failed, 41 passed | 43 passed |
| `citations_bear_on_any` | `turns_by_id=` to `{}` | `test_grounding_label.py` | 1 failed, 42 passed | 43 passed |
| `citations_bear_on_any` | `lines=` to `()` | `test_grounding_label.py` | 2 failed, 41 passed | 43 passed |
| `_ballot_grounding_subjects` | the EJECT branch removed | `test_grounding_label.py` | 1 failed, 42 passed | 43 passed |
| `_ballot_grounding_subjects` | the `considered_alternatives` branch removed | `test_grounding_label.py` | 1 failed, 42 passed | 43 passed |
| `_ballot_grounding_subjects` | the `candidate_targets` fallback to `()` | `test_grounding_label.py` | 1 failed, 42 passed | 43 passed |
| the basis pre-pass | `_prepared_ballot_payload(...)` bypassed | `test_grounding_label.py` | 8 failed, 35 passed | 43 passed |
| the basis pre-pass | `INVALID_BASIS_MARKER` never prepended | `test_grounding_label.py` | 7 failed, 36 passed | 43 passed |
| the basis pre-pass | the provenance boundary read AFTER the prepend | `test_grounding_label.py` | 1 failed, 42 passed | 43 passed |
| `_default_vote` | `grounding_label="not_assessed"` dropped | `test_grounding_label.py` | 2 failed, 41 passed | 43 passed |
| `_ballot_view` | both mirrors to `None` | `tests/api` | 1 failed, 437 passed, 2 skipped | 438 passed, 2 skipped |
| `api/replay_loader` marker table | the `invalid_basis` row dropped | `tests/api` | 438 passed, 2 skipped — GREEN | 438 passed, 2 skipped |
| `api/replay_loader` marker table | the same, after the planted case | `tests/api` | 1 failed, 437 passed, 2 skipped | 438 passed, 2 skipped |
| `training/surrogate` marker table | the `invalid_basis` row dropped | `tests/training` | 2 failed, 470 passed, 335 deselected | 472 passed, 335 deselected |
| `eval/deduction_metrics` marker chain | the `invalid_basis` row dropped | `test_deduction_metrics.py` | 1 failed, 117 passed | 118 passed |
| `BallotCard.tsx` `rewriteLabel` | the `off_target_coerced` + `invalid_basis` cases dropped | `PrivateReasoning.test.tsx` | 39 passed — GREEN | 39 passed |
| `BallotCard.tsx` `rewriteLabel` | the same, after the planted cases | `PrivateReasoning.test.tsx` | 2 failed, 37 passed | 39 passed |
| `vote_ballot.j2` | the skeleton pre-fills `"cited"` | `test_elicitation_fixtures.py` | 1 failed, 27 passed | 28 passed |
| `vote_ballot_accounts.j2` | the skeleton pre-fills `"none_held"` | `test_public_account_prompts.py` | 2 failed, 92 passed | 94 passed |
| `TestTheOnlyTargetRewrites` | the scan reads `node.args` only | `test_grounding_label.py` | 1 failed, 42 passed | 43 passed |

Twenty-six perturbations. Six of them RE-MEASURE a line an earlier round had
already probed — the pre-pass marker prepend, the provenance boundary, the
`_default_vote` label, the `eval/deduction_metrics` row, the `_ballot_view`
mirrors and the `considered_alternatives` branch — because this round's new
cases move their counts; those six are not counted again in the card's running
total, which reads forty-three.

**The two the walk caught, and why each was invisible.** The `invalid_basis`
row of `api/replay_loader._BALLOT_PREFIX_MARKERS` is the one row of that table
a LIVE meeting can still add, and no committed recording carries it, so the
real-bytes case could not reach it and the hand-built `BallotView` fixtures
never parse a rationale at all. Unregistered, the front-to-back strip stops in
front of the marker and the machinery's own sentence is served to the spectator
as the voter's words. `test_parse_rewrite_reasons_uses_imported_markers` now
asserts the row plain AND stacked in the order production writes it — the basis
marker goes on at the top of the ballot chain, the teammate firewall prepends
OUTSIDE it. The two `rewriteLabel` cases are the display twin of the same gap:
`off_target_coerced` never fired on any recording and `invalid_basis` first
mints at the re-record, so deleting either case degraded the chip to the
generic "Recorded vote adjustment" with the suite green.

**3. The undated Verification table was stale under a heading claiming this
head.** At `7e6747c7` it read 8,153 where `check.sh` printed 8,158; 1,810 where
`tests/meetings tests/api` printed 1,813; and 38 where
`test_grounding_label.py` printed 40. Every cell is re-measured at THIS head
below and the table now says which round it was measured at; the dated round-1
and round-2 tables stay exactly as they were, as the record of those heads.

**The skeleton stops pre-answering the basis.** `vote_ballot.j2:263` shipped
`"decision_basis": "cited"` and `vote_ballot_accounts.j2:23` shipped
`"decision_basis": "none_held"`, inside the JSON object each prompt tells the
model to copy. This repo's own discipline forbids that — the `v5` accounts
bullet in `agents/strategic/prompts/loader.py` states it for
`primary_reason_id` ("the shape is shown in prose and never pre-filled into the
object a model copies verbatim"), on the measured ground that 7 of the
reference arm's 14 surviving citations were the id its skeleton pre-filled. It
binds harder here than anywhere: the pre-filled token is the very thing this
card exists to make the VOTER state, and a voter that edits `target` and leaves
the rest alone would record a basis it never chose. Both skeletons now carry
the KEY with a NULL value — the ballot still declares one — and both prose
registers keep the two legal tokens unchanged and say the skeleton shows null.
No further version bump: `vote_ballot` `v7` is unreleased (nothing is recorded
on it) and `ACCOUNT_PROMPT_SET_REVISION` `v6` is the unreleased revision round
1 opened for this card, so the same `v6` absorbs the edit —
`test_no_committed_capture_already_carries_todays_account_stamps` is what says
no capture carries it, `_PRE_V6_REVISIONS` is unchanged, and the v6 gate still
passes because the edit touches none of the spans that gate names. The gate now
asserts the null skeleton BESIDE them, so the revision and the body cannot
drift apart. A null basis still labels honestly: `test_a_bare_skip_is_uncited`
(SKIP) and `test_an_uncited_eject_survives_the_whole_production_chain` (EJECT)
both run a `decision_basis` of `None` through the manager and read `uncited`.

**The smaller items.** `TestTheOnlyTargetRewrites` scanned `node.args` only, so
`ballot_target_rewrite_provenance(ballot, reason=...)` — an ordinary
positional-or-keyword parameter — would have been visited and contributed
nothing; the scan is now a shared helper reading `node.keywords` too, and
`test_the_scan_sees_a_reason_passed_as_a_keyword` runs that REAL helper over a
planted source carrying the keyword, dotted-keyword and positional forms.
Decision 4's `state_hash_after` sentence is restated at the strength the code
delivers, above and in the comment at the check itself: unweakened on the
ENGINE leg, and no longer pinning the BALLOT leg at all, because the decision
it applies is read as recorded. The running probe total counts rounds 2 and 3.
Decisions 10 and 11 record the three files outside `## Expected scope` and the
test pin that moved off `audits/deduction-candidate/execution-manifest.md`.

**Citations, re-derived at this head after the last code edit.** Three were
wrong and are corrected in Acceptance: `normalize_ballot_target`
`meetings/voting.py:147` to `:152`, `coerce_teammate_ballot_to_skip`
`meetings/manager.py:3531` to `:3628`, and the second anchored-match comment
`eval/meeting_quality.py:981-985` to `:983-987` (the first, `:277-282`, was
right). Re-derived by symbol and unchanged since round 2:
`meetings/schemas.py` `decision_basis` 1010, `grounding_label` 1073,
`under_gate_redirect` 886; `meetings/manager.py` the provenance boundary 2352,
`cited_before_validation` 2376, the labeller call 2444, `citation_nulled` 2448,
`_default_vote` 3001, `_LAYER_OWNED_BALLOT_FIELDS` 3027-3031,
`_prepared_ballot_payload` 3054, `_ballot_grounding_subjects` 3703,
`label_ballot_grounding` 3730; `meetings/voting.py` `tally_ballots` 192;
`meetings/citation_relevance.py` `citations_bear_on_any` 143,
`citations_bear_on` 216; `api/replay_loader.py` `_ballot_view` 3306 and the
`invalid_basis` row 3612; `api/schemas.py` 1082-1083;
`eval/deduction_metrics.py` 724; `training/surrogate/dataset.py` 208;
`orchestrator/game.py` 435; `frontend/src/types/api.ts` 391-392;
`agents/strategic/prompts/loader.py` `ACCOUNT_PROMPT_SET_REVISION` 1283 (moved
by this round's history-bullet edit); `vote_ballot.j2` 3, 259, 262, 263;
`vote_ballot_accounts.j2` 23. The `## Evidence` section's citations are NOT
re-anchored and are not stale: they were taken on `main` before this card and
several name constructs it then DELETED (`MeetingEvidenceProfile`'s
`citation_relevance_version`, the guard call site at `:2412-2419`), so they are
the record of what was found, which is what that section is for.

**Verification at this head (round 3).** Commands run from this worktree, exit
codes captured directly (never through a pipe).

| command | result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 — 8,163 passed, 20 skipped, 3 xfailed; 4 import contracts kept, 0 broken; 73 work cards validated; 390 prompts in sync; mypy clean over 488 files; ruff clean and 517 files formatted; 552 frontend tests; frontend build OK |
| `uv run pytest tests/meetings tests/api -q` | exit 0 — 1,817 passed, 2 skipped |
| `uv run pytest tests/meetings/test_grounding_label.py -q` | exit 0 — 43 passed |
| `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` | exit 0 — 25 passed |
| `uv run pytest tests/agents tests/experiments -q` | exit 0 — 1,977 passed |
| `bash scripts/verify_samples.sh` | exit 0 — 50/50 + 50/50 = 100/100 clean |
| `uv run python scripts/build_sample_report.py --sample-dir replays/<set> --check` x4 | exit 0 — consistent on all four sets |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0 — consistent |
| `uv run python scripts/check_doc_facts.py` | exit 0 — 26-lever substrate registry, 4-switch experiment registry |
| `uv run python scripts/generate_prompts.py --check` | exit 0 — all 390 prompts in sync |
| `uv run python scripts/validate_task_docs.py` | exit 0 — 73 work cards |
| `uv run python scripts/verify_ml_evidence.py` | exit 0 — 61 checks, 0 FAIL, 7 evidence-branch-absent |

No live provider call, no calibration, no recording and no re-record in this
round either; band 2100-2999 was not generated or opened and
`scripts/verify_ml_evidence.py --complete` was not run. No recorded flag,
sample report, scorecard figure, prompt archive or golden moved. No `audits/`
or `tests/fixtures/` byte moved, so no `docs/artifacts.md` row is recomputed,
and the `tasks/README.md` inventory sentence is unchanged because Status was
already `done` before this round.

### Review corrections, round 4 (2026-09-21)

Four blocking findings from the round-4 verifiers. The first three are one
class of defect found three times: a production line nothing enforced, left
standing by a round-3 walk that claimed to cover the whole call surface. The
fourth is a prose site three closing greps had missed, because all three
grepped phrases rather than inflections. The verifiers reproduced every figure
in this card, all 26 round-3 probes and the card's universal guarantee on their
own 1,848-meeting family with 0 failures, so nothing above is withdrawn; what
follows is added to it. Every command quoted below was run from this worktree
at this head.

**1. `invalid_citation` over `none_held` was unenforced, and the reachable case
untested.** Swapping the two branches of `label_ballot_grounding` left the
WHOLE Python suite green. The pair is reachable through the manager and only
the branch order decides it: a voter that declares `decision_basis="none_held"`
AND cites a turn id this meeting does not own arrives at the labeller carrying
both halves, because the validator nulls the id (`citation_nulled=True`) while
the in-set basis rides the pre-pass untouched.
`test_a_fabricated_citation_outranks_a_declared_none_held` plants exactly that
ballot through `MeetingManager` — `p-1` SKIP,
`primary_reason_id="m-1:turn-99"`, `decision_basis="none_held"` — and asserts
both halves are really on the recorded ballot (the id nulled with its marker,
the voter's word surviving beside it) before asserting `invalid_citation`, with
the declared-basis twin beside it reading `none_held`. The combination is also
in `TestEveryRecordedBallotIsLabelled._SPECS`, so the generated family carries
the one shape where two branches of the precedence both hold. The ordering is
the ruling it looks like: the record says what the ballot DID, not what it said
it held.

*The two orderings that are genuinely unreachable, decided and written down.*
Both lines STAY as defensive lines and `label_ballot_grounding`'s docstring now
says so, with why, so no later reader re-finds them as findings. First,
`invalid_citation` can never race `supported` / `off_target`: at the one
production call site `citation_nulled` is computed as "cited before the
validators AND both ids `None` after them", which forces `cited` false, so no
ordering between branches 2 and 3 is observable there. Branch 3 stays BELOW
branch 2 for a caller that passes `citation_nulled=True` beside a surviving id
— a grader's shape over recorded bytes, never the manager's. Second, the
`ballot.target != _SKIP_TARGET` half of the `flag_only` guard can never be what
decides it: every live `ContradictionRef.subjects` entry is a speaker or a
claim subject (`meetings.transcript.detect_contradictions`,
`meetings.public_accounts`), so the literal `"SKIP"` is never in `flagged` and
the membership test alone would answer the same. It stays because `PlayerId` is
`str` and nothing in the type forbids that value, and because `flag_only` is
defined as an EJECT's word.

**2. `"grounding_label"` in `_LAYER_OWNED_BALLOT_FIELDS` was unenforced, and
removing it costs a voter its whole vote.** Dropping the row left
`tests/meetings` green. With a non-validating client a model that sends
`grounding_label="fabricated"` goes from `target='p-3', reason=None,
label='uncited'` at head to `target='SKIP', reason='parse_default',
label='not_assessed'` perturbed: the `Literal` refuses the value, so an
unstripped key fails the schema and the ballot degrades — the identical failure
mode the half-pair provenance rows exist for.
`test_a_model_authored_provenance_value_never_reaches_the_record` asserted that
property for `guard_redirected_from` / `guard_rewrite_reason` and was never
given the third name. It now carries `{"grounding_label": "fabricated"}` and
the in-set `{"grounding_label": "supported"}`, and asserts the vote survives on
its authored target AND that the recorded label is the layer's `uncited`. The
in-set row states what the strip does and does not buy: the labeller overwrites
the field at the end of the chain either way, so what the strip keeps out is
the model's word from the payload the layer validates.

**3. `bounded_marker_original(dropped)` on the invalid basis was unenforced,
and removing it unbounds the record.** Dropping the call left
`tests/meetings tests/api` green while a 5,000-character `decision_basis`
through the manager grew the recorded rationale from 111 characters to 5,048.
`test_an_over_length_fabricated_basis_is_quoted_bounded` drives that value and
asserts the recorded rationale is exactly the marker quoting a head bounded by
`MARKER_QUOTED_ORIGINAL_MAX_CHARS` plus `MARKER_TRUNCATION_SUFFIX`, that the
runaway string is absent, and that the whole rationale stays inside the
constant's bound — the Task 10.6 rule, whose measured reason is seed 35 m1's
3,499-char blob.

**The call surface, walked again.** Every added or changed executable line and
tuple/dict row of `git diff 038a22a5 HEAD` over `meetings/manager.py`,
`meetings/schemas.py`, `meetings/citation_relevance.py`, `meetings/voting.py`,
`api/replay_loader.py`, `api/schemas.py`, `training/surrogate/dataset.py` and
`eval/deduction_metrics.py` that is NOT in the round-3 table and not one of the
three findings above. `meetings/voting.py` contributes no row: its whole diff
is docstring. Each row neutered ONE line, ran the selection, and was reverted
from a COPY taken first.

| site | line neutered | selection | perturbed | restored |
| --- | --- | --- | --- | --- |
| labeller precedence | branches 3 and 4 swapped | `test_grounding_label.py` | 1 failed, 44 passed | 45 passed |
| `_LAYER_OWNED_BALLOT_FIELDS` | the `"grounding_label"` row dropped | `tests/meetings` | 1 failed, 1,382 passed | 1,383 passed |
| the basis pre-pass | `bounded_marker_original(dropped)` dropped | `tests/meetings tests/api` | 1 failed, 1,820 passed, 2 skipped | 1,821 passed, 2 skipped |
| labeller call | `cited_before_validation` loses its observation half | `test_grounding_label.py` | 45 passed — GREEN | 45 passed |
| labeller call | the same, after the planted case | `test_grounding_label.py` | 1 failed, 44 passed | 45 passed |
| labeller call | `citation_nulled`'s turn conjunct dropped | `test_grounding_label.py` | 45 passed — UNOBSERVABLE | 45 passed |
| labeller call | `citation_nulled`'s observation conjunct dropped | `test_grounding_label.py` | 45 passed — UNOBSERVABLE | 45 passed |
| the basis pre-pass | `drop_basis` loses its `basis is not None` guard | `test_grounding_label.py` | 1 failed, 44 passed | 45 passed |
| the basis pre-pass | the byte-conservative early return dropped | `tests/meetings tests/api` | 1 failed, 1,820 passed, 2 skipped | 1,821 passed, 2 skipped |
| the basis pre-pass | a non-string basis rendered `str()` not `json.dumps()` | `test_grounding_label.py` + `tests/api` | 483 passed, 2 skipped — GREEN | 483 passed, 2 skipped |
| the basis pre-pass | the same, after the planted case | `test_grounding_label.py` + `tests/api` | 2 failed, 481 passed, 2 skipped | 483 passed, 2 skipped |
| `citations_bear_on_any` | the vacuous-true early return dropped | `tests/meetings` | 1 failed, 1,382 passed | 1,383 passed |
| `meetings/schemas.py` | the `decision_basis` field row dropped | `test_grounding_label.py` | 25 failed, 20 passed | 45 passed |
| `meetings/schemas.py` | the `grounding_label` field row dropped | `test_grounding_label.py` | 10 failed, 35 passed | 45 passed |
| `api/schemas.py` | both `BallotView` field rows dropped | `test_view_model.py` | 21 failed, 30 passed | 50 passed, 1 skipped |

Thirteen distinct lines, TWO of which first came back GREEN and are now
planted, and TWO of which are recorded as unobservable rather than planted.

*The two that first came back green.* `cited_before_validation` reads BOTH
citation channels at the call site, and its observation disjunct was reachable
by no assertion: every `invalid_citation` case in the tree cited a TURN id, so
a voter that reached for a private memory line and missed was recorded
`uncited` — the same record as a voter that reached for nothing, which is the
one distinction the label exists to make.
`test_a_fabricated_turn_id_is_invalid_citation` now carries the observation
channel beside the turn channel, driven through the manager against a voter
holding no typed observation ids. The second is the pre-pass's rendering of a
NON-STRING basis: `json.dumps(basis)` reports the value as the bytes the model
sent, `str(basis)` reports Python's repr of the parsed object, and
`test_every_out_of_set_shape_is_dropped_rather_than_refused` asserted only that
SOME marker was prepended. Its parametrize now carries the expected quoted
rendering per shape, spelled out literally rather than recomputed.

*The two that are unobservable, and why they are not planted.* Both conjuncts
of the `citation_nulled` expression at the call site are masked by the
`supported` / `off_target` branch above `invalid_citation`: dropping either one
can only make `citation_nulled` true on a ballot whose citation SURVIVED, and
such a ballot never reaches branch 3. That is the same construction the
reachability note in the labeller's docstring states, reached from the other
end — so the honest record is that the conjuncts are belt-and-braces at this
call site, not that a case is missing. No test can distinguish them without a
second call site, and this card adds none.

**4. The prose sweep left false current-intent sentences in a file this PR
touches.** Rounds 1 to 3 closed the sweep against five phrases, then against
the two deleted symbol names, case-insensitively. All three rounds grepped
PHRASES (`coerces|still coerces|then coerces`), so a sentence using another
inflection survived. `tests/agents/test_public_account_prompts.py` carried
three: the fourth-live-run paragraph said the layer "nulls before coercing the
now-uncited ejection to SKIP" (now history — the id is still nulled, and since
D6 the ejection stands carrying `grounding_label="invalid_citation"`); the
citation test said a copied literal "is nulled and the ejection then coerced to
SKIP" (same correction); and the same test closed on "The skeleton is a SKIP,
and a SKIP needs no citation" — false since D6, and now: the skeleton is a
SKIP, which states its basis in `decision_basis` rather than being exempt from
one, and the citation slot stays null because a pre-filled literal is COPYABLE,
not because a SKIP may cite nothing.

The widened sweep found four more sites no finding had named, each a live-tense
claim about a mechanism this card removed:

* `tests/api/test_view_model.py:522-529` and `:550-552` — called the under-gate
  redirect "the live gate chip" and described the guard in the present tense.
  Now: the chip with real bytes behind it, 23 of them, retired by D6, and no
  later recording adds one.
* `tests/training/test_surrogate_dataset.py:850-856` — "the gate is the last
  guard, so the coercion marker is the outermost prefix", present tense about a
  retired gate. Now a statement about the RECORDED marker order and why it is
  what it is.
* `tests/training/test_surrogate_dataset.py:1002` — "the production stack is
  citation-gate-outermost"; now "the RECORDED stack".
* `experiments/fresh_deduction_instrument.py:5193-5194`, `:5204-5206` and
  `:5449-5450` — "One ballot can carry two", "the vote prompt renders coerced
  ballots back to later voters" and "which an under-gate redirect breaks". All
  three are about bytes the instrument grades, and all three now say so.

The closing greps at this head, widened to every inflection and
case-insensitive, over the whole tree minus `.venv`, `.git`, `node_modules`,
`audits/`, `replays/` and the dated card history under `tasks/` and
`agent_prompts/`:

```
grep -rniE "SKIP needs|needs no citation|needs neither" . \
  --include="*.py" --include="*.j2" --include="*.ts" --include="*.tsx" \
  --exclude-dir=.venv --exclude-dir=.git --exclude-dir=node_modules \
  --exclude-dir=audits --exclude-dir=replays --exclude-dir=tasks \
  --exclude-dir=agent_prompts
```

returns five lines and cannot return none: two are
`tests/fixtures/prompt_archive/qwen3_6_27b_v5/vote_ballot.j2:259` and `:268`,
the ARCHIVED v5 body whose bytes are the record of what every committed replay
was generated from; two are `tests/meetings/test_elicitation_fixtures.py:344`
and `:345`, the gate asserting both phrases are GONE from the live body; and
the fifth is `tests/orchestrator/test_replay.py:95`, an unrelated sentence
saying a by-identity lever binding "needs neither a mirror nor an equivalence
pin".

```
grep -rniE "guard_ballot_citation|guard_ballot_target_graph" . \
  --include="*.py" --include="*.j2" --include="*.ts" --include="*.tsx" \
  --exclude-dir=.venv --exclude-dir=.git --exclude-dir=node_modules \
  --exclude-dir=audits --exclude-dir=replays --exclude-dir=tasks \
  --exclude-dir=agent_prompts
```

returns the same six lines round 2 recorded, at their current numbers, and
cannot return none for the same reason: two are the gate asserting both symbols
are gone from the manager, and four name the retired symbols on purpose,
because the markers they minted are still on 89 committed ballots.

```
grep -rniE "two layer-owned|two citation-only" . \
  --include="*.py" --include="*.j2" --include="*.ts" --include="*.tsx" \
  --exclude-dir=.venv --exclude-dir=.git --exclude-dir=node_modules \
  --exclude-dir=audits --exclude-dir=replays --exclude-dir=tasks \
  --exclude-dir=agent_prompts
```

returns nothing (exit 1).

```
grep -rniE "default.off" . --include="*.py" --include="*.j2" --include="*.ts" \
  --include="*.tsx" --exclude-dir=.venv --exclude-dir=.git \
  --exclude-dir=node_modules --exclude-dir=audits --exclude-dir=replays \
  | grep -iE "citation|relevance"
```

returns nothing (exit 1).

The two broad sweeps are read rather than claimed empty, because both must
return lines:

```
grep -rniE "coerc" . --include="*.py" --include="*.j2" --include="*.ts" \
  --include="*.tsx" --exclude-dir=.venv --exclude-dir=.git \
  --exclude-dir=node_modules --exclude-dir=audits --exclude-dir=replays \
  --exclude-dir=tasks --exclude-dir=agent_prompts
```

```
grep -rniE "redirect" . --include="*.py" --include="*.j2" --include="*.ts" \
  --include="*.tsx" --exclude-dir=.venv --exclude-dir=.git \
  --exclude-dir=node_modules --exclude-dir=audits --exclude-dir=replays \
  --exclude-dir=tasks --exclude-dir=agent_prompts | grep -iE "ballot|gate|argmax"
```

737 and 355 lines respectively. Every one is in one of four classes, and none is
a live-tense claim about a retired mechanism: the LIVE teammate firewall and
invalid-target normalization; Pydantic / SDK type coercion in `llm/`,
`training/realpath_schema.py` and their tests; the retired markers' own
identifiers, chip copy and report cells, which stay because 89 committed
ballots carry them; and sentences about RECORDED bytes, which say what produced
those bytes and are still true.

**The smaller items.** Three sites called the labels outside
`TARGET_REWRITE_LABELS` "the two citation-only" ones where this card makes them
three: `api/replay_loader.py:302-305`, `training/surrogate/dataset.py:212-221`
and `training/surrogate/ballots.py:65-68`, the third found by the same grep and
named by no finding. `docs/glossary.md` and `frontend/src/lib/copy.ts` glossed
`supported` with the SKIP's subject alone and now say both — an ejection's
subject is the player it names, a skip's is the alternatives it weighed, or any
living candidate when it weighed none; the frontend cases read
`BALLOT_COPY.groundingLabels` by KEY rather than by text, so no test
expectation moved. `BallotCard.tsx`'s comment called `not_assessed` a firewall
coercion and now names all four paths (an illegal target, the teammate
firewall, a ballot that never parsed, a missed deadline).
`scripts/record_ml_corpus.sh:159-165` said "all four at v5" above a literal
reading v6/v6/v6/v7, and now carries the real lineage through v6 (the alibi
card, four as a unit) and v7 (`vote_ballot` alone, this card).
`docs/artifacts.md:101` said the live set reads v6 and now adds
`vote_ballot`'s v7; its class, `where` and size cells are untouched, and
`scripts/verify_ml_evidence.py` keys that row on its first backticked token, so
the row's pin is unmoved.

**The schema's `None` reservation, restated at the strength the code
delivers.** `BallotGroundingLabel`'s docstring said `None` "is reserved for a
recording made before the field existed". That holds for MEETING recordings,
which is what the two writers cover; `training/surrogate/runner.py:367`,
`training/composed_runner.py:726` and `eval/reasoning_evidence.py:167` build
`VoteBallot` objects for a surrogate tally or a fixture and leave the field
`None` — correctly, because no meeting assessed them and none of those objects
is a recording. That docstring and `_default_vote`'s now say exactly that. The
three call sites are unchanged.

**Citations, re-derived at this head after the last code edit.** Eight moved
again with this round's docstring additions and are corrected in Acceptance and
in the CURRENT Results text: `meetings/schemas.py` `decision_basis` 1016,
`grounding_label` 1079, `BallotDecisionBasis` 975 (`BallotGroundingLabel` 923
and `under_gate_redirect` 886 are unmoved); `meetings/manager.py`
`_LAYER_OWNED_BALLOT_FIELDS` 3030-3034, `_prepared_ballot_payload` 3057,
`_ballot_grounding_subjects` 3706, `label_ballot_grounding` 3733 (the
provenance boundary 2352, `cited_before_validation` 2376, the labeller call
2444, `citation_nulled` 2448, `_default_vote` 3001 and `INVALID_BASIS_MARKER`
438 are unmoved); `api/replay_loader.py` `_ballot_view` 3307 and the
`invalid_basis` row 3613; `scripts/record_ml_corpus.sh`
`REQUIRED_PROMPT_VERSIONS_BASE` 169; `BallotCard.tsx`'s redirect disclosure
292-294. Two Acceptance citations were wrong before this round's edits and are
corrected too: `agents/strategic/prompts/loader.py:1278` to `:1283`, and
`api/replay_loader.py:3569-3577` to the marker table's real span `:3605-3614`.
The round-1, round-2 and round-3 subsections keep the figures of THEIR heads
and are not re-anchored.

**One Acceptance pair quoted two different totals for one file, and both were
right.** `tests/agents/test_public_account_prompts.py` reads 94 in the skeleton
item and 93 in the accounts-revision item: the first was measured at the
round-3 head, the second at the round-1 head, and the difference is the case
round 3 added. A dated note now says so, rather than making the two agree by
rewriting a measurement.

**Verification at this head (round 4).** Commands run from this worktree, exit
codes captured directly (never through a pipe).

| command | result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 — 8,167 passed, 20 skipped, 3 xfailed; 4 import contracts kept, 0 broken; 73 work cards validated; 390 prompts in sync; mypy clean over 488 files; ruff clean and 517 files formatted; 552 frontend tests; frontend build OK |
| `uv run pytest tests/meetings tests/api -q` | exit 0 — 1,821 passed, 2 skipped |
| `uv run pytest tests/meetings/test_grounding_label.py -q` | exit 0 — 45 passed |
| `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` | exit 0 — 25 passed |
| `uv run pytest tests/agents tests/experiments -q` | exit 0 — 1,977 passed |
| `uv run pytest tests/training -q` | exit 0 — 472 passed, 335 deselected |
| `npm --prefix frontend test` | exit 0 — 552 passed over 20 files |
| `bash scripts/verify_samples.sh` | exit 0 — 50/50 + 50/50 = 100/100 clean |
| `uv run python scripts/build_sample_report.py --sample-dir replays/<set> --check` x4 | exit 0 — consistent on all four sets |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0 — consistent |
| `uv run python scripts/check_doc_facts.py` | exit 0 — 26-lever substrate registry, 4-switch experiment registry |
| `uv run python scripts/validate_task_docs.py` | exit 0 — 73 work cards |
| `uv run python scripts/generate_prompts.py --check` | exit 0 — all 390 prompts in sync |
| `uv run python scripts/verify_ml_evidence.py` | exit 0 — 61 checks, 0 FAIL, 7 evidence-branch-absent |

No live provider call, no calibration, no recording and no re-record in this
round either; band 2100-2999 was not generated or opened and
`scripts/verify_ml_evidence.py --complete` was not run. No recorded flag,
sample report, scorecard figure, prompt archive or golden moved. No `audits/`
or `tests/fixtures/` byte moved, so no `docs/artifacts.md` row is recomputed
(the `docs/artifacts.md` edit is PROSE inside one row's description cell, which
no inventory figure reads), and the `tasks/README.md` inventory sentence is
unchanged because Status was already `done` before this round.
