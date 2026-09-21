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

- [x] Review correction: `INVALID_BASIS_MARKER` is registered in the eval
  marker-chain table (`eval/deduction_metrics.py:724`), so the machinery's own
  sentence stays on the machinery side of the provenance split instead of being
  read as the voter's words from the re-record onward. Proved by
  `tests/eval/test_deduction_metrics.py::test_the_invalid_basis_marker_is_read_as_machinery_not_as_the_voter`
  (probe: drop the row — `1 failed, 117 passed`).
- [x] Review correction: the provenance-boundary line
  (`meetings/manager.py:2351`) has a probe. `test_a_fabricated_basis_survives_the_teammate_redaction`
  (`tests/meetings/test_grounding_label.py`) drives an impostor voter naming a
  teammate with an out-of-set `decision_basis` and asserts the redacted
  invalid-basis marker survives the firewall redaction; the card's universal
  probe claim is corrected above the probe table.
- [x] Review correction: `ModelAuthoredVoteBallot`'s docstring names THREE
  layer-owned fields (`meetings/schemas.py:987-990`), the set
  `_LAYER_OWNED_BALLOT_FIELDS` holds. Pinned by
  `tests/meetings/test_manager.py::TestBallotRewriteProvenanceSites::test_the_model_facing_schema_is_the_ballot_minus_the_guard_pair`,
  which DERIVES the three-name difference rather than restating it.
- [x] Review correction: `ACCOUNT_PROMPT_SET_REVISION` advances `v5` → `v6`
  (`agents/strategic/prompts/loader.py:1278`) with its history bullet, because
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
  `frontend/src/components/BallotCard.tsx:291-292`, checked by
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
  consumers parse it (`api/replay_loader.py:3569-3577`,
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
  (`meetings/voting.py:147`) still records `target="SKIP"`,
  `guard_rewrite_reason="invalid_target"`, the bounded authored string, its
  marker and `grounding_label="not_assessed"`; and the teammate firewall
  (`coerce_teammate_ballot_to_skip`, `meetings/manager.py:3531`) enforces a role
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
`decision_basis: BallotDecisionBasis | None = None` (`meetings/schemas.py:1006`),
with the closed set as a named alias at `:969` so the schema and the pre-pass
cannot disagree about it. `None` is what every committed recording parses to
and means the voter answered nothing; `"none_held"` is its explicit statement
that it holds nothing that resolves. An out-of-set token is dropped from the
raw payload before validation by `_prepared_ballot_payload`
(`meetings/manager.py:3049`, the renamed pre-pass that strips the layer-owned
keys), which reports the dropped value so the call site prepends
`INVALID_BASIS_MARKER` (`:438`) at `meetings/manager.py:2351` — after taking a
copy of the model's own body, so the marker survives the teammate firewall's
rationale redaction instead of being redacted as model prose. The marker is
registered as the `invalid_basis` spectator chip (`api/replay_loader.py:3610`),
so it never reaches `rationale_text_clean`.

**The suspicion-argmax redirect is retired outright.**
`guard_ballot_target_graph`, its private `_render_gate_value` helper, its call
site and the four test classes pinning it are deleted, and
`tests/meetings/test_manager_gate_band.py` goes with them.
`BALLOT_TARGET_REDIRECT_MARKER` (`meetings/manager.py:333`) and the
`under_gate_redirect` member of `BallotTargetRewriteReason`
(`meetings/schemas.py:885`) survive as read-only history, both re-documented as
such, because 83 committed ballots carry the marker and four consumers parse
it. `TestTheRetiredGuardsMintNothing` walks `agents/`, `api/`, `eval/`,
`meetings/`, `orchestrator/` and `training/` with `ast` and fails on any
`<MARKER>.format(...)` call site for the three retired markers; a companion
case runs the same scan over `INVALID_REASON_ID_MARKER` and asserts it finds
one, so an empty result is a fact about the tree and not about the scanner.

**`guard_ballot_citation` became `label_ballot_grounding`**
(`meetings/manager.py:3725`) and rewrites nothing. It writes one
`grounding_label` (`meetings/schemas.py:1069`, alias at `:923`) on `VoteBallot`
only, in the card's precedence, and returns a ballot identical in every other
field. The subject is the EJECT's target and, for a SKIP,
`considered_alternatives` when non-empty and `candidate_targets` otherwise
(`_ballot_grounding_subjects`, `:3698`). `invalid_citation` is separated from
`uncited` by `citation_nulled`, computed at the call site
(`meetings/manager.py:2374` and `:2447`) from the ballot before and after the
two citation validators.

**The tally is untouched.** `tally_ballots` (`meetings/voting.py:187`) takes no
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
skeleton gains `"decision_basis"`. The marker at `:3` and the `qwen3_6_27b`
entry in `PROMPT_VERSION_SETS` (`orchestrator/game.py:435`) advance
`vote_ballot` ALONE, v6 → v7, in the Task 15.5 `qwen3_32b` form. The cascade
also moves `REQUIRED_PROMPT_VERSIONS_BASE` (`scripts/record_ml_corpus.sh:166`),
the live-registry and marker-equality pins, and the four lever-arm overlays
(see decision 7). Recorded-manifest pins do NOT move: every committed replay
stamps `.v5` and reads as recorded.

**The spectator reads both.** `BallotView` (`api/schemas.py:1082-1083`),
`_ballot_view`, `frontend/src/types/api.ts:391-392` and the two
`tests/api/test_leak.py` allowlists mirror them with `None` defaults;
`BallotCard.tsx` renders the label as one plain-language chip beside the
alternatives heading, behind the same perspective gate as the citations.
`rewriteLabel` keeps its `under_gate_redirect` and `uncited_coerced` cases and
the `BallotCard.tsx:291-292` redirect disclosure, and gains `off_target_coerced`
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
   chain starts, so `_default_vote` (`meetings/manager.py:2996`) states
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
   check is unweakened: it still applies a result to the reconstructed state
   and demands the recorded bytes.
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

### Verification

Every command run from this worktree at this head, exit codes captured
directly (never through a pipe).

| command | result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 — 8,153 passed, 20 skipped, 3 xfailed; 4 import contracts kept, 0 broken; 73 work cards validated; 390 prompts in sync; 550 frontend tests; frontend build OK |
| `.venv/bin/python -m mypy .` | Success: no issues found in 488 source files |
| `.venv/bin/python -m ruff check .` / `ruff format --check .` | All checks passed / 517 files already formatted |
| `.venv/bin/python -m pytest tests/meetings tests/api -q` | 1,810 passed, 2 skipped |
| `.venv/bin/python -m pytest tests/meetings/test_grounding_label.py -q` | 38 passed |
| `.venv/bin/python -m pytest tests/meetings/test_prompt_byte_golden.py -q` | 25 passed |
| `bash scripts/verify_samples.sh` | 50/50 + 50/50 = 100/100 clean |
| `.venv/bin/python scripts/build_sample_report.py --sample-dir replays/<set> --check` ×4 | consistent on all four sets |
| `.venv/bin/python scripts/publish_process_scorecard.py --check` | consistent |
| `.venv/bin/python scripts/validate_task_docs.py` | passed |
| `.venv/bin/python scripts/check_doc_facts.py` | verified (4-switch experiment registry) |
| `.venv/bin/python scripts/verify_ml_evidence.py` | offline, no FAIL rows |
| `npm --prefix frontend test` / `run build` | 550 passed / built |

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

Sixteen probes at the first head, and five more in
[round 1](#review-corrections-round-1-2026-09-21) — twenty-one. Each neutered
ONE production line, ran the selection, and was reverted; both counts are
recorded. The claim at the first head, that every line this card changed in a
production module had one, was WRONG: review round 1 found the
provenance-boundary line (`meetings/manager.py:2351`) unprobed, and a
perturbation of it left `tests/meetings tests/api` fully green. It has one now,
and so does every line round 1 added.

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
`authored_rationale_text = parsed.rationale_text` (`meetings/manager.py:2351`)
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
(`meetings/manager.py:3022-3026`) already listed all three. Rewritten to name
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
and `:2826-2839`, `agents/memory/beliefs.py:333-339`,
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
