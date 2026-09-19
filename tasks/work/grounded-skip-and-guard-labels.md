# Ground every SKIP and make the ballot guards label instead of rewrite

**Status:** ready

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

- [ ] Every ballot declares a basis. `ModelAuthoredVoteBallot` gains
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
- [ ] One prompt clause, one per-template version bump. `vote_ballot.j2:259`
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
- [ ] `guard_ballot_target_graph` is retired, not disabled: the function, its
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
- [ ] `guard_ballot_citation` becomes `label_ballot_grounding` and rewrites
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
- [ ] The tally is untouched and counts the agent's target under every label.
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
- [ ] Citation relevance is retired as a lever, per
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
- [ ] The new fields reach the spectator without breaking the old record.
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
- [ ] One planted case per label, each red before and green after: a SKIP citing
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
