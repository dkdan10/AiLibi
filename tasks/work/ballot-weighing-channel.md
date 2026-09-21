# Give the voter evidence to weigh instead of a verdict to follow

**Status:** done

## Outcome

At vote time the ballot prompt stops handing the voter a finished number and
stops telling it to follow that number. For each living ejection target it
renders the EVIDENCE ROWS behind the suspicion figure that the meeting layer can
NAME: the voter's own
first-hand sightings, vents, transits and body discoveries; the contradictions
naming the target; and the testimony about the target, each row naming its
speaker, saying whether that speaker saw it first-hand or is repeating another
voice, and carrying the id a ballot may cite for it. It is not a complete
decomposition of the figure — a witnessed kill and the body-proximity lift reach
no row, and review round 1 weakened the template's own wording to match. The
scalar stays, moved
below its rows and relabelled their PARTIAL summary; the sentence instructing
deference is deleted and nothing that points at a target replaces it. The
ballot gains `counter_reason_id`, the strongest thing the voter holds pointing
the other way, validated exactly like the primary citation, and the spectator's
ballot card shows both, so "I weighed A against B" becomes a recorded fact. The
dead trust column leaves the serving render and its unused writer is deleted.
This is the only card of the wave that changes what the meeting decides: the
ejection rate WILL move, and D5 intends that.

## Evidence

[The direction of 2026-09-19](../direction-2026-09-19-process-over-outcome.md)
is the basis; the owner accepted D1 to D8 as a set on 2026-09-19 and its
section 12 records the rulings. D5 is this card; its section 4 is the finding,
property P6, "the agent does the weighing".

**The agent is handed its answer.** Re-tallied this pass over the committed
JSONL, counts only. Each meeting's vote prompts are found by their
`## Valid ejection targets` and `## How to decide` headers, the graph rows
parsed with the pattern at `eval/meeting_quality.py:326`, the argmax taken over
the rendered rows naming a player on that same prompt's valid-target list, and
roles read off the rendered team line
(`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:243`).

| crew EJECT ballots, one unambiguous argmax | ml_corpus 9p2i | samples 9p2i |
| --- | --- | --- |
| ballots | 1,270 | 434 |
| target EQUALS that argmax | 1,189 (93.6%) | 403 (92.9%) |
| of those, role-correct | 1,143 (96.1%) | 358 (88.8%) |
| target DIFFERS from it | 81 | 31 |
| of those, role-correct | 7 (8.6%) | 2 (6.5%) |

The follow rate and both deviation cells reproduce the direction's section 4
table to the digit; its follower role-correct cell reads 1,137 against 1,143
here, six ballots, and nothing turns on that. It is the same six
[the process scorecard](process-scorecard.md) pins, under that card's
definition of the row.

**Three reasons the weighing is not the agent's.** The prompt says so:
`vote_ballot.j2:259` calls the levels "your own accumulated evidence from the
whole game", then "trust them over meeting rhetoric". The weighing already ran
in Python: `graduated_spread_delta` (`agents/memory/beliefs.py:454`) prices
testimony by independent-voice count and `apply_meeting_evidence_rules`
(`:1374`) folds this meeting PRE-VOTE, which the row announces as "built from:
this meeting +0.23, carried prior +0.00" (`vote_ballot.j2:227`). And there is
nothing to weigh with: one citation slot and no counter
(`meetings/schemas.py:770-771`); `considered_alternatives` non-empty on 1,336 of
the 1,359 SKIPs in the two 9p2i sets (98.3%), typed at
`frontend/src/types/api.ts:383` and read by no component, which
[the spectator card](spectator-tour-and-alternatives.md) fixes; and a constant
trust column.

**Trust is a dead constant.** `BeliefState.adjust_trust`
(`agents/memory/beliefs.py:953`) has no caller outside `tests/`, as
`docs/adr/0001-three-load-bearing-decisions.md:30` records. Across the four
committed sets 14,880 of 14,880 rendered graph rows read `trust 0.50`: the field
sits at `_DEFAULT_TRUST` (`beliefs.py:65`) and nothing moves it, so
`_format_belief_score`'s trust branch (`agents/memory/store.py:2593-2604`) is
unreachable in production.

**The rows exist, scattered, and half are not citable.** `MeetingParticipant`
carries the voter's own typed channels, `sighting_records`,
`vent_witness_records`, `move_witness_records`, `observation_ids` and
`body_discovery_records` (`meetings/manager.py:826-835`), and the manager holds
this meeting's `contradictions` and `testimony_ledger` at the render site
(`:2151-2205`). Only `BodyDiscoveryRecord` carries an episodic id
(`meetings/render_contract.py:128`); the other three carry none
(`meetings/schemas.py:306-308`, `:340-343`, `:366-369`), so a row built from
them has nothing a ballot could cite. The rendered memory does tag its lines
(`agents/memory/store.py:587-590`, an `[obs {id}]` prefix folded in), but that
is prose, and `meetings/schemas.py:300` states the standing rule that the
grounding chokepoint never parses rendered prose. The citable vocabulary is
exactly two shapes: this meeting's turn ids (`_normalize_ballot_reason_id`,
`meetings/manager.py:3199`) and the voter's own observation ids
(`_normalize_ballot_observation_id`, `:3241`); anything else is nulled with a
marker, and [the accounts v5 card](accounts-prompt-set-v5.md) measured a third
vocabulary's cost, 27 of 150 ballots nulled on a row suffix.

**What a shipped prompt change costs the committed record.**
`tests/meetings/test_prompt_byte_golden.py` re-renders every recorded prompt of
all 300 committed games and asserts byte-equality; its bump-in-flight seam,
`ARCHIVED_PROMPT_VERSION_SETS` plus `tests/fixtures/prompt_archive/`
(`:192-199`), is EMPTY at HEAD and asserted empty at `:1296-1304`, because all
300 games stamp `*.qwen3_6_27b.v5` (`orchestrator/game.py:424`);
[the alibi card](alibi-as-route.md) opens it. Separately
`eval/meeting_quality._SUSPICION_GRAPH_ROW_RE` (`:326-329`) requires
`, trust <N>` on each row and feeds `_parse_suspicion_graph` (`:387`) and
`_rendered_suspicion_by_target_per_voter` (`:2481`), and through them the
metrics `scripts/build_sample_report.py --check` recomputes over old bytes.

## Acceptance

- [x] Review correction (round 2): the served row reads `first_hand` BEFORE the
  speaker, so a testimony or contradiction row the voter itself spoke renders as
  a statement made at this table and never as something the voter perceived.
  `tests/meetings/test_weighing_channel.py::TestTheServedBody` —
  `test_what_the_voter_merely_said_here_is_not_rendered_as_perception` over both
  kinds, its planted twin `test_planted_the_old_branch_order_is_detected`, and
  one test per branch:
  `test_a_row_the_voter_perceived_says_it_saw_it_itself`,
  `test_a_grounded_voice_names_the_speaker_who_saw_it`,
  `test_another_voice_at_this_table_names_that_speaker`.
- [x] Review correction (round 2): the two production constructs the round-0
  pass left unenforced are enforced — the self-accusation drop by
  `test_a_speaker_who_names_themselves_is_no_voice_against_themselves` (whose
  first leg drives a real meeting and shows the claim arriving intact), and the
  provenance class ranks by
  `test_the_three_provenance_classes_rank_in_the_stated_order`, which states them
  as LITERALS instead of re-deriving them from `_EVIDENCE_KIND_CLASS`. Six
  perturbation rows, all red, in the round-2 subsection of Results.
- [x] Review correction (round 2): `VotePromptRenderer`'s `evidence_rows`
  paragraph (`meetings/render_contract.py:461-473`) states the limit the code
  delivers, naming the witnessed-kill and body-proximity channels that reach no
  row, and the round-1 paragraph that claimed this site had already been
  corrected is restated true.
- [x] Review correction (round 2): the three comments this diff falsified are
  updated to the counts the code delivers — nine prefix kinds
  (`training/surrogate/dataset.py:189`) and the vote body TWO versions ahead at
  v8 (`tests/scripts/test_record_ml_corpus.py:980`,
  `tests/agents/test_bespoke_prompt_sets.py:548`), with two more hits the
  closing grep found (`tests/meetings/test_prompt_byte_golden.py:1341`,
  `tests/agents/test_impostor_answer_arm.py:683`). Greps and output quoted in
  Results.
- [x] Review correction: the §4.7 TEAMMATE firewall is re-applied at assembly,
  so no own-channel row and no `co_present` companion names a fellow impostor.
  `tests/meetings/test_weighing_channel.py::TestTheTeammateFirewall` —
  `test_no_own_row_names_a_fellow_impostor`,
  `test_the_identical_records_on_a_crewmate_keep_every_row` (the non-vacuity
  control), `test_the_public_rows_about_a_teammate_are_not_dropped` and
  `test_the_firewall_holds_through_the_real_meeting`.
- [x] Review correction: the same finding's documentation half —
  `orchestrator/game.py`'s sighting and vent accessor docstrings state the
  guarantee at the strength the code now delivers (these rows DO reach a prompt;
  the consumer re-applies the firewall).
- [x] Review correction: `eval/validity.py`'s `_SUSPICION_GRAPH_ROW_RE` is
  widened exactly as `eval/meeting_quality.py`'s was, so the Task-14.12 railroad
  gate cannot go vacuous on v8 bytes.
  `tests/eval/test_validity.py::test_railroad_reads_both_rendered_row_shapes`
  (parametrised over both rendered shapes).
- [x] Review correction: a contradiction row resolves to the turn the SUBJECT
  spoke rather than to the lexically first event id, and the fallback is stated
  at the strength it delivers.
  `test_a_cross_turn_flag_cites_the_subjects_own_account` and
  `test_a_flag_that_names_no_turn_of_the_subjects_falls_back`.
- [x] Review correction: the four live-tense guarantees inside the diff that
  were false at `6b79ff08` are rewritten (the testimony builder's ledger
  sentence, `vent_witness_records`' "never reaches a prompt surface",
  `observation_ids`' "exactly ONE place", and the stale `None`-while-OFF comment
  above the unconditional ledger build), with the three sibling paragraphs in
  the same docstring that had drifted the same way. Verified by the closing
  greps quoted in Results.
- [x] Review correction: the suspicion block no longer calls itself "A running
  summary of the lines above". It is a PARTIAL summary and names the two
  provenance channels that reach no row.
  `test_the_number_is_called_a_partial_summary_of_the_rows` with its planted
  twin `test_planted_the_complete_summary_claim_is_detected`, and the matching
  Limitations bullet.
- [x] Review correction: the Results symbol table is re-stamped at this round's
  final head, re-derived by symbol with `grep -n`, and the two non-Python rows
  (`BallotCard.tsx` `counterKind`, `meetings/schemas.py`
  `VoteBallot._serialize`) with it.
- [x] Typed evidence rows, assembled from typed inputs only. A frozen
  `EvidenceRow` in `meetings/render_contract.py` (the leaf that breaks the
  `agents` cycle, so it imports no `agents.*`) carries the subject, a one-line
  description, `kind` (own sighting, own vent, own transit, own body discovery,
  contradiction, testimony), `first_hand: bool`, `speaker` and `citation_id`.
  The manager builds the rows at the render site (`meetings/manager.py:2151`)
  from the participant's typed channels, `contradictions` and
  `testimony_ledger`, never from `rendered_memory` (`meetings/schemas.py:300`).
  `VentWitnessRecord`, `SightingRecord` and `MoveWitnessRecord` gain
  `observation_id: str | None = None` mirroring `BodyDiscoveryRecord`
  (`meetings/render_contract.py:128`), stamped by the `orchestrator/game.py`
  `*_for_meeting()` accessors off the episodic rows they already read; a row
  whose id stays `None` renders without a citation and says so. A test asserts
  over a committed fixture meeting that every rendered `citation_id` is a
  `turn_id` of this meeting's final transcript or a member of THAT voter's own
  `observation_ids`. Planted: a row built from another participant's channel is
  red.
- [x] Evidence renders first, the number last, and no wording pushes at a
  target. `VotePromptRenderer` (`meetings/render_contract.py:340-400`) gains
  `evidence_rows: tuple[EvidenceRow, ...] = ()`, the inert widening
  `reporter_id`, `persona` and `testimony_ledger` already use, so the six
  non-serving sets render byte-identically. In `vote_ballot.j2` the rows render
  ABOVE `## Your suspicion of each player` (`:224-233`) and the number is
  relabelled their summary; `:259` loses "Your suspicion levels above are your
  own accumulated evidence from the whole game, trust them over meeting
  rhetoric" with no replacement that ranks, recommends or names a player, while
  its other clauses keep their bytes, including the grounded-SKIP register
  [the previous card](grounded-skip-and-guard-labels.md) put there. Planted:
  the deference sentence restored is red; a rendered ballot naming a
  recommended target is red.
- [x] `counter_reason_id` end to end, composing into ONE decision record.
  `ModelAuthoredVoteBallot` (`meetings/schemas.py:767-773`) gains
  `counter_reason_id: str | None = None`, so `VoteBallot` inherits it and the
  adapters that constrain decoding on the authored model carry it. The manager
  validates it through the SAME two normalizers as the primary citation and
  nulls an unknown id with its own marker, registered in both marker tables
  (`training/surrogate/dataset.py:213` and `api/replay_loader.py`'s label set)
  so their equality pin stays green on the widened pair. `vote_ballot.j2:262`
  moves from the 8 keys the grounded-SKIP card left to 9, `:263` prefills
  `null`, and one bullet asks for the strongest thing the voter holds pointing
  AWAY from its target, in the same two id shapes, or `null`. A null counter
  means the voter holds none; the prompt uses the SAME `none_held` wording that
  card introduced for `decision_basis` and mints no third vocabulary. The
  record the wave ends with is target, the two citation ids, `decision_basis`,
  `counter_reason_id`, `considered_alternatives` and `rationale_text`, with
  `grounding_label` written beside them by the layer. It is NOT a gate: a null
  counter never coerces, redirects or lowers a ballot. `BallotView`
  (`api/schemas.py:962-970`) and `frontend/src/types/api.ts:377-386` take the
  field with the same `None` default `primary_reason_observation_id` uses, so
  older recordings surface `None`; `_ballot_view`
  (`api/replay_loader.py:3286`) passes it through and `BallotCard.tsx:149-152`
  renders a third `EvidenceLink` labelled as counter-evidence beside the
  existing two, the THIRD and last edit that component takes in this plan.
  `tests/api/test_leak.py` gains the field on the same rows the grounded-SKIP
  card widened, and a frontend test covers present, null and unresolvable.
- [x] Trust is DELETED, not wired, and the card says why: a credibility scalar
  would be a second engine-computed verdict handed to the agent, the defect this
  card exists to remove, while the credibility information itself already
  arrives as evidence, a speaker whose own account a route-aware detector broke
  appearing in the rows with that contradiction's id for the listener to price.
  So `BeliefState.adjust_trust` (`agents/memory/beliefs.py:953`) and its seven
  test callers go, the `trust` column leaves `vote_ballot.j2:227`, and
  `_format_belief_score`'s unreachable branch
  (`agents/memory/store.py:2593-2604`) goes with a test asserting the §6.6
  render is byte-identical across that deletion. `PlayerBelief.trust` and
  `SuspicionEntry.trust` STAY: six frozen sets render `entry.trust` (for example
  `agents/strategic/prompts/qwen3_32b/vote_ballot.j2:79`) and their byte pins
  must not move, so one history line says the field is now a frozen-set render
  input only. `docs/adr/0001-three-load-bearing-decisions.md:30` and
  `DESIGN.md:718` are corrected.
- [x] The version cascade, the archive window, and old recordings that keep
  loading. The wave takes THREE `qwen3_6_27b` bumps, one per card whose
  template bytes move, so no stamp ever covers two bodies: the alibi card's
  set-wide `v6`, then `vote_ballot` ALONE to `v7` on the grounded-SKIP card,
  then to `v8` here, in the Task 15.5 `qwen3_32b` per-template form at
  `orchestrator/game.py:401-407`. This card moves the `.j2` marker
  (`vote_ballot.j2:3`) and `orchestrator/game.py:424` together, leaves the four
  variant-arm entries (`:451`, `:489`, `:509`, `:535`) reading the wave's
  `_bespoke_versions` base, and asserts every live-recorded prompt-version pin
  agrees. The v5 archive the alibi card opened already covers all 300 committed
  games, so this card adds no archive entry and does not touch
  `docs/artifacts.md`. In the same move `_SUSPICION_GRAPH_ROW_RE`
  (`eval/meeting_quality.py:326-329`) makes `, trust <N>` OPTIONAL so a
  pre-card and a post-card row both parse, every metric reading it stays an
  as-recorded read, no history is re-scored, and `verify_samples.sh` plus the
  four `--check` runs stay green on unchanged bytes. Planted, each red
  before and green after: an archived body edited by one byte, the old row shape
  under a narrowed pattern, and a `--check` run over a committed set drifting.
- [x] The prediction is written down BEFORE anything is re-recorded, and is not
  a gate. This card's Results and [the scorecard](process-scorecard.md)'s
  argmax-independence row state, dated, that after
  [the re-record](process-rerecord.md) the follower share should FALL from 93.6%
  and deviating EJECTs should be AT LEAST as role-correct as following ones,
  against today's 8.6% versus 96.1%. Under D1 role-correctness is reported
  beside, never gated: a wrong call on rows the voter can cite is the outcome
  the owner asked for.

## Constraints

No live provider call of any kind: fake and replay providers only, no
calibration, no recording, no re-record, no re-scored report. No per-card
re-record; [the single re-record](process-rerecord.md) follows the whole wave.
Band 2100-2999 stays unseen and no held-out prefix is generated or opened.

This card changes SHIPPED DEFAULT behaviour, which AGENTS.md craft rule 7 would
otherwise route behind a default-OFF experimental gate. Ruling D5 is the
authorization, the departure is declared in Record impact, and no new lever is
added: the direction's section 10 stop list names lever proliferation
explicitly, five existing and all default `None`.

Nothing may push the agent toward the correct answer. Row order is stated in the
template and encodes no role, guilt or engine ranking: group by target, then
first-hand before hearsay, then by tick. No row is dropped for being
exculpatory, and the meeting layer labels rather than re-aims, which is
[the grounded-SKIP card](grounded-skip-and-guard-labels.md)'s half.

Order, identical on all seven cards. WAVE 1 is parallel and changes no agent
behaviour: [the scorecard](process-scorecard.md),
[the spectator tour](spectator-tour-and-alternatives.md) and
[the evaluation close](close-deduction-candidate-evaluation.md), the close
merging FIRST so no retired held-out band is owed a restamp by the
`GENERATOR_SOURCES` files this wave edits:
`experiments/held_out_prefixes.py:155` lists `agents/memory/beliefs.py`,
`agents/memory/store.py` and `orchestrator/game.py` among them. The SUBSTRATE
WAVE is serial, all three moving the shipped prompt versions and the ballot or
claim schema: [alibi as a route](alibi-as-route.md), then
[the grounded SKIP and guard labels](grounded-skip-and-guard-labels.md), then
THIS card; then [the re-record](process-rerecord.md), once. Deferred and in no
card: the body freshness band, an impostor who reports a body, the `docs/`
front door.

One writer per file: this card takes `vote_ballot.j2`, `meetings/schemas.py`
and `meetings/manager.py` only after the grounded-SKIP card merges, rebasing
rather than branching beside it; the alibi card owns
`tests/fixtures/prompt_archive/` and `docs/artifacts.md`'s `tests/fixtures/`
row. The engine stays a deterministic tick function, `agents/` imports no
`engine/`, and invalid input raises.

## Expected scope

`meetings/render_contract.py` (the `EvidenceRow` DTO and the renderer kwarg),
`meetings/schemas.py` (`counter_reason_id`; `observation_id` on the three
witness records), `meetings/manager.py` (row assembly, the counter normalizer
and marker, the render call site), `agents/strategic/prompts/qwen3_6_27b/
vote_ballot.j2` (the whole change to rendered bytes), `agents/memory/beliefs.py`
and `agents/memory/store.py` (the trust deletion), `orchestrator/game.py` (the
accessors' observation-id stamp and the `vote_ballot` version entry),
`eval/meeting_quality.py` (the row pattern), `api/schemas.py`,
`api/replay_loader.py`, `frontend/src/types/api.ts`,
`frontend/src/components/BallotCard.tsx`, `training/surrogate/dataset.py`, the
tests for each plus `tests/meetings/test_prompt_byte_golden.py` and
`tests/api/test_leak.py`, `docs/adr/0001-three-load-bearing-decisions.md`,
`DESIGN.md`'s dead-trust paragraph, `tasks/README.md`'s inventory sentence
(`:43`), this card. NOT in scope: the six frozen prompt sets, the engine, the
tactical layer, the SKIP register and guard dispositions, the alibi claim shape,
`tests/fixtures/prompt_archive/`, `docs/artifacts.md`, and any recording.

Delivered on `work/ballot-weighing-channel` and one pull request into `main`,
merged as a merge commit or a fast-forward and never squashed, with the trailer
`Card: tasks/work/ballot-weighing-channel.md`. Every acceptance item that adds a
gate carries a planted failure.

## Record impact

An INTENDED change to shipped default behaviour: the prompt the default set
serves, the ballot schema the model authors, and the spectator DTO all move on
the default path with no experimental gate. That departs from AGENTS.md craft
rule 7 and is authorized by ruling D5 of
[the direction](../direction-2026-09-19-process-over-outcome.md), recorded here
rather than discovered at review. What the meeting decides changes: the voter
reads its evidence before its summary, is no longer told to defer to the
summary, and carries a counter citation, so ballots will differ from what the
same inputs produced before and the EJECTION RATE WILL MOVE, in either
direction. Role-correctness may fall; under D1 it is a reported cell, not a
gate.

No committed byte is re-scored, by the SAME mechanism the other two substrate
cards use: every recording keeps its recorded `prompt_versions` and is read as
recorded. The bump-in-flight archive the alibi card opened keeps the
prompt-byte golden a real gate over the 300 committed games, and the widened
suspicion-row pattern keeps every `--check` recomputation identical over old
bytes. The new schema field is additive with a default, so older recordings
validate and surface `None` exactly as `primary_reason_observation_id` does. No
sample set is rebuilt here; [the re-record](process-rerecord.md) is the one
place new bytes are made, once, after the wave. No `tests/fixtures/` or
`audits/` byte changes here, so no `docs/artifacts.md` row is recomputed.
Deleting `adjust_trust` retires a dead mechanism with its coupled consumers as
AGENTS.md craft rule 3 requires; no replay stamp key is involved, trust having
never been a lever.

## Validation

`uv run pytest tests/meetings tests/agents tests/api tests/eval tests/training
tests/scripts tests/test_firewall.py -q` (fake and replay providers only),
`uv run lint-imports`, `uv run mypy .`,
`uv run python scripts/validate_task_docs.py`,
`uv run python scripts/check_doc_facts.py`,
`uv run python scripts/verify_ml_evidence.py` (offline; never `--complete`) with
`uv run pytest tests/scripts/test_verify_ml_evidence.py -q`,
`bash scripts/verify_samples.sh`, the four
`uv run python scripts/build_sample_report.py --sample-dir <set> --check` runs
over the two `replays/samples/` and two `replays/ml_corpus/` sets,
`cd frontend && npm run lint && npm run tsc:check && npm run test`, the
counts-only re-tally that reproduces this card's argmax table, and
`bash scripts/check.sh` run whole in a clean worktree so no gate after the first
failure is masked. No live evaluation, calibration or provider call is a check.
## Results

Delivered on `work/ballot-weighing-channel`, the THIRD and last card of the
substrate wave. Every `file:line` this card was written against was taken at
`cdefb7a6`, before [the alibi card](alibi-as-route.md) and
[the grounded-SKIP card](grounded-skip-and-guard-labels.md) landed; every
citation below is re-anchored by SYMBOL at this card's base, `0a1100ea`, and
the true lines are given. No cited construct had disappeared and neither
earlier card had changed one's meaning, so nothing was blocked.

### Architecture and contract references

`docs/architecture.md` layering is unchanged: the engine stays a deterministic
tick function, `agents/` imports no `engine/`, and
`meetings/render_contract.py` stays the leaf that breaks the `agents ↛
meetings.manager` cycle — `EvidenceRow` carries ids and rendered strings only
and imports no `agents.*`, which `uv run lint-imports` re-checks (4 contracts
kept, 0 broken). DESIGN.md §5.5 is the ballot contract the ninth key joins;
§6.6 is the render whose trust branch is deleted. The basis is ruling D5 of
[the direction of 2026-09-19](../direction-2026-09-19-process-over-outcome.md),
§4 (the finding and property P6), §7 ("render the evidence rows the suspicion
number was built from … drop the 'trust them over meeting rhetoric'
instruction … or delete the column rather than display a constant") and §12
(the ruling table).

### What was built, and where it actually lives

Every line below is RE-STAMPED at this card's final head (review round 1) and
re-derived by symbol with `grep -n`, not carried forward: the round-1 fixes moved
`meetings/manager.py` again, and the round-0 table had already drifted by the two
commits that landed after it.

| Contract item | Symbol | Line at the final head (round-0 table's value) |
| --- | --- | --- |
| the row DTO | `EvidenceRow` / `EvidenceRowKind` | `meetings/render_contract.py:155` / `:131` (new) |
| the renderer widening | `VotePromptRenderer.evidence_rows` | `meetings/render_contract.py:492` (round 1 said `:487`, round 0 `:481`; card said `:340-400`); its Protocol paragraph, weakened in round 2, at `:461-473` |
| the three witness stamps | `VentWitnessRecord` / `SightingRecord` / `MoveWitnessRecord` `.observation_id` | `meetings/schemas.py:318` / `:358` / `:389` (card said `:306-308`, `:340-343`, `:366-369`) |
| the ninth ballot key | `ModelAuthoredVoteBallot.counter_reason_id` | `meetings/schemas.py:1035` (card said `:767-773`) |
| row assembly | `build_evidence_rows` + its three builders | `meetings/manager.py:3710`, `:3449`, `:3568`, `:3646` (round 0 said `:3618`, `:3424`, `:3510`, `:3557`) |
| the render call site | `MeetingManager._collect_one_ballot` | `meetings/manager.py:2184`; `:2270` builds the rows, `:2309` passes them (round 0 said `:2248` / `:2300`; card said `:2151`) |
| the counter validator | `_normalize_ballot_counter_reason_id` | `meetings/manager.py:3989`, called at `:2499` (round 0 said `:3863` / `:2477`) |
| the two shared decisions | `_resolved_reason_id` / `_resolved_observation_id` | `meetings/manager.py:3849` / `:3874` (round 0 said `:3730` / `:3753`), extracted from `_normalize_ballot_reason_id` at `:3894` (card said `:3199`) and `_normalize_ballot_observation_id` at `:3940` (card said `:3241`) |
| the counter marker | `INVALID_COUNTER_REASON_MARKER` | `meetings/manager.py:412` |
| the served body | `vote_ballot.j2` | `:253-258` the `<evidence>` block with the provenance branch at `:256`, `:261-262` the relabelled PARTIAL summary, `:265` the row without `trust`, `:297` the sentence deleted, `:300-301` nine keys, `:307` the counter bullet (each +4 on round 1's `:249-254` / `:257-258` / `:261` / `:293` / `:296-297` / `:303`: round 2 added four header lines) |
| the row pattern | `_SUSPICION_GRAPH_ROW_RE` | `eval/meeting_quality.py:341` (card said `:326`) and, added in round 1, `eval/validity.py:190` |
| the served DTO | `BallotView.counter_reason_id` | `api/schemas.py:1093` (card said `:962-970`), mirrored at `api/replay_loader.py:3324` (card said `:3286`) |
| the spectator card | `BallotCard.tsx` | `:261` the third `EvidenceLink`, `:68` `counterKind` (round 0 said `:57`), `frontend/src/lib/copy.ts:450` the chip label (round 0 said `BallotCard.tsx:32`) |
| the marker tables | three | `api/replay_loader.py:3612` (the tuple; the counter row at `:3618`), `training/surrogate/dataset.py:207` (round 0 said `:205`; card said `:213`), `eval/deduction_metrics.py:718` (the chain; the counter row at `:725`) |
| the trust deletion | `BeliefState.adjust_trust` / `_format_belief_score` | `agents/memory/beliefs.py:969` (history note where it stood; round 0 said `:966`; card said `:953`), `agents/memory/store.py:2792` (round 0 said `:2808`) |

### Decisions

**The evidence block's sources, and the one the card named that is lever-gated.**
The card names "the participant's typed channels, `contradictions` and
`testimony_ledger`". The first two are unconditional; the ledger was built ONLY
while the `corroboration_discipline` lever was ON (`meetings/manager.py:1568` at
this card's base, before this card), so on the shipped default path every
testimony row would have
read "not first-hand" whatever the speaker's own record said — the block would
have shipped with its third source dark. The ledger is a pure derivation of
bytes the meeting already holds, so it is now built unconditionally
(`meetings/manager.py:1625` at the final head) and used for the `first_hand` bit
alone; the LEVER
still decides whether the `<testimony_sources>` BLOCK renders, so an OFF
meeting's prompt bytes are unchanged, which the prompt-byte golden re-asserts
over all 300 committed games. The testimony ROWS themselves are built from the
transcript's typed `AccusationClaim`s — the ledger carries no per-speaker turn
id, and a row must carry an id a ballot may cite.

**What `first_hand` means, stated at the strength the code delivers.** True only
where the row's speaker perceived the thing themselves: every own-channel row,
and a testimony row whose speaker is in the ledger's first-hand set for that
subject. A contradiction row is the meeting layer's cross-check of two
statements rather than one speaker's perception, so it is False — said in the
DTO docstring, in `build_evidence_rows`, and in the template's own wording
("not first-hand: {speaker} stated it at this table", which is accurate for a
contradiction row as well as for an ungrounded voice).

**Row order encodes no guilt, and the bound is a page rule.** Order is: subject
(the `candidate_targets` roster order, then any other subject by id), first-hand
before not, then the provenance CLASS (own perception → the detector's flags →
what was said here), then earliest-first, then kind/speaker/citation. A
witnessed vent and an ordinary sighting share class 0 on purpose, so the block
cannot rank one player's evidence above another's. `MAX_EVIDENCE_ROWS_PER_SUBJECT
= 8` (`meetings/manager.py:3413`) bounds each (subject, class) group, not each
subject: a single budget would have let many own sightings of one player crowd
out the contradictions and the voices against that same player. It is decided
on ARRIVAL TIME, not on the render order: the render puts first-hand rows first
inside a class, so a budget taken off the front of the rendered block would
drop the GROUNDED voices of an over-budget testimony group first — a bound
deciding by what a row says, which is the one thing it must not do. Ranked on
arrival, the EARLIEST rows of the group go and nothing is dropped for its
content; the template says so in one standing sentence. (Found by writing the
guarantee down and then reading the loop against it; the two rules are made to
disagree in
`test_the_budget_drops_by_arrival_time_not_by_render_position`.)

**A body discovery's subject is the victim.** It is the one own-channel kind
whose subject is dead and therefore never an ejection target; it is kept (the
card lists the kind) and sorts after the living targets. Nothing is dropped for
being exculpatory.

**`counter_reason_id` is a gate over nothing, and the code says how.** It is
validated through the SAME two decisions as the primary slots — which is why
those decisions were extracted into `_resolved_reason_id` /
`_resolved_observation_id` and the three validators now share them, rather than
a third copy that could drift. A null counter returns the ballot untouched. A
fabricated counter costs exactly this field plus a marker; it is deliberately
outside the `cited_before_validation` read (`meetings/manager.py:2456`), so it
cannot turn an `uncited` ballot into an `invalid_citation` one, and no guard, no
`tally_ballots` and no `label_ballot_grounding` branch reads it.

**The counter's null is ELIDED from the recorded bytes**, like `decision_basis`
and for the same reason: the four committed `tournament-eval-report.json` files
embed re-serialized ballots, so a `null` key written there would have moved
bytes in four reports this card may not move. `VoteBallot._serialize`
(`meetings/schemas.py:1148`).

**Trust is DELETED, not wired**, with the card's reason recorded in three
places: the comment where `adjust_trust` stood
(`agents/memory/beliefs.py:969`), the ADR's 2026-08-19 note
(`docs/adr/0001-three-load-bearing-decisions.md:30`) and DESIGN.md's §6.6
banner (`:718`). A credibility scalar would be a second engine-computed verdict
handed to the agent — the defect this card exists to remove — while the
credibility information itself already arrives as evidence. `PlayerBelief.trust`
and `SuspicionEntry.trust` STAY: six frozen sets render `entry.trust` and their
byte pins must not move, so one history line in each of the three documents says
the field is now a frozen-set render input only.

**`VIEW_MODEL_VERSION` is NOT bumped.** It stays `"5"`. The constant's own rule
(`api/schemas.py:56`) is that a BREAKING shape change bumps it and an additive
projection does not; `counter_reason_id` is additive with a `None` default, the
same shape `decision_basis` and `grounding_label` took without a bump.
`frontend/src/types/api.ts` was regenerated by
`uv run python scripts/gen_frontend_types.py`, which reproduced the hand edit
exactly, so the DTO and the TS type cannot have drifted.

### Deviations from the card, declared

1. **One `tests/fixtures/` byte moved, and the `docs/artifacts.md` row was
   recomputed** — which Record impact said would not happen and Expected scope
   put out of bounds. Deleting `_format_belief_score`'s trust branch is not
   invisible to the committed goldens after all: `crewmate_basic.json:44` seeds
   `p-1` at `suspicion 0.5, trust 0.7`, a row production cannot produce, and its
   golden carried `- p-1: trust 0.70`. The alternatives were to keep the branch
   (failing the acceptance item) or to move one line of one golden. The golden
   line is removed, the fixture INPUT is left exactly as its author wrote it (it
   is the historical record of what that fixture asked for), and
   `docs/artifacts.md:101` is recomputed with the change staged: **2,196,268 →
   2,196,250 tracked bytes, 35 files unchanged** (`git ls-files tests/fixtures |
   xargs wc -c`). `scripts/verify_ml_evidence.py` (offline) and
   `tests/scripts/test_verify_ml_evidence.py` are green on the new row. The
   alibi card, which owned that row, is merged, so no concurrent writer was
   displaced.
2. **`scripts/record_ml_corpus.sh` was edited** — not in Expected scope, but the
   card's own cascade clause says the bump must reach "the lever-arm overlays
   that now spread `PROMPT_VERSION_SETS` and `scripts/record_ml_corpus.sh`". Its
   `REQUIRED_PROMPT_VERSIONS_BASE` preflight pin (`:169`) would otherwise refuse
   every future recording under the v8 body.
3. **Two frontend story fixtures** (`MeetingView.stories.tsx`,
   `MindInspector.stories.tsx`) gained the new required field. `npm run
   tsc:check` fails without them; this is the "directly necessary
   call-site follow-through" AGENTS.md permits.
4. **`agents/strategic/prompts/loader.py`** takes the new kwarg. The card's
   Expected scope names `meetings/render_contract.py` for "the renderer kwarg";
   the Protocol and the callable that conforms to it are two files, and a
   Protocol nothing implements renders nothing.
5. **`audits/workflows/extract_gameplay_facts.py:272` keeps the NARROWED row
   pattern.** It is a second reader of the same rendered row shape, and after
   the re-record it will silently skip a post-card row. It is not edited because
   it lives under `audits/`, whose bytes this card may not move and whose
   `docs/artifacts.md` row it may not recompute. It reads committed bytes only,
   which all carry the trust suffix, so it is correct today; the re-record card
   should take it. Recorded here rather than left to be re-found.

### Verification

Every command below was run in this clean worktree with its real exit code
captured directly, at the FIRST PASS's final head (`6b79ff08`). The review round
below re-ran the same list at its own head and states its own numbers there;
these are kept as recorded rather than overwritten.

```
$ bash scripts/check.sh                                   EXIT=0
  ruff check . / ruff format --check .  518 files, all clean
  lint-imports                          4 contracts kept, 0 broken, 188 modules
  validate_task_docs.py                 390 phase tasks + 390 prompts; 73 work cards
  generate_prompts.py --check           clean
  mypy .                                no issues in 489 source files
  pytest -n auto --dist loadfile        8210 passed, 20 skipped, 3 xfailed
  frontend lint / tsc:check / vitest    557 tests in 20 files passed; build green

$ bash scripts/verify_samples.sh                          EXIT=0
  replays/samples/4p1i  All 50 samples verified clean.
  replays/samples/9p2i  All 50 samples verified clean.

$ uv run python scripts/build_sample_report.py --sample-dir <set> --check
  replays/samples/4p1i     consistent with its replays.      EXIT=0
  replays/samples/9p2i     consistent with its replays.      EXIT=0
  replays/ml_corpus/4p1i   consistent with its replays.      EXIT=0
  replays/ml_corpus/9p2i   consistent with its replays.      EXIT=0

$ uv run python scripts/publish_process_scorecard.py --check              EXIT=0
$ uv run python scripts/verify_ml_evidence.py                             EXIT=0
  checks: 61 | OK 49 | FAIL 0 | ABSENT 7 | INFO 5   (never --complete)
$ uv run python scripts/check_doc_facts.py                                EXIT=0
$ uv run pytest tests/scripts/test_verify_ml_evidence.py -q               EXIT=0
$ cd frontend && npm run e2e                              13 passed, 3 skipped
```

The card's own Validation list is covered: `tests/meetings tests/agents
tests/api tests/eval tests/training tests/scripts tests/test_firewall.py` all
run inside the `pytest` line above (fake and replay providers only — no live
provider call of any kind was made, and none is a check here), `lint-imports`,
`mypy`, `validate_task_docs.py`, `check_doc_facts.py`, `verify_ml_evidence.py`
offline with its own test, `verify_samples.sh`, the four `--check` runs, the
three frontend commands, the re-tally below, and the whole gate.

**The argmax re-tally, count-only, through the production path.** The card's
Evidence table is reproduced by
`uv run python scripts/publish_process_scorecard.py --check` (EXIT=0), which
recomputes `docs/process-scorecard.md` from the committed recordings and
compares it byte for byte. Its rows read, unchanged by this card:
`ml_corpus/9p2i` deviating **81/1270 = 6.4%** (so 1,189 following = 93.6%),
role-correct **1143/1189 = 96.1% vs 7/81 = 8.6%** (`:107-108`);
`samples/9p2i` deviating **31/434 = 7.1%** (403 following = 92.9%),
role-correct **358/403 = 88.8% vs 2/31 = 6.5%** (`:142-143`). Every cell of the
card's table to the digit. The census is keyed by (set, meeting), prints no
rendered prompt and no seed-band prefix, and re-scores nothing: the widened row
pattern reads the committed `, trust 0.50` rows exactly as the narrow one did,
which is why all four `--check` recomputations are byte-identical.

### Planted and perturbed failures

A mechanical pass over the WHOLE production diff, 32 rows — INCOMPLETE, as
round 2 found: three production constructs it did not reach survive neutering
with the suite green, and the round-2 subsection below carries the six rows that
repair that. The table and the "0 unenforced" line beneath it are the round-0
reading, kept as filed and read against that correction.
Each row edits ONE thing,
runs the named probe, and restores the file from an in-memory COPY (never `git
checkout`). Run with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`
after a first pass produced three FALSE reds from stale `__pycache__` bytecode:
the `v8 → v7` edit preserves file SIZE, so a restore inside the same second let
CPython reuse the perturbed `.pyc`. That is recorded because it is exactly the
kind of thing that makes a perturbation table lie.

| # | perturbation | probe | result |
| --- | --- | --- | --- |
| 1 | own sighting row's `citation_id` → `None` | `test_weighing_channel.py` | red |
| 2 | own vent row's `first_hand` → `False` | same | red |
| 3 | body-discovery rows dropped | same | red |
| 4 | transit rows dropped | same | red |
| 5 | contradiction → turn resolution neutered | same | red |
| 6 | testimony rows ignore the ledger's first-hand set | same | red |
| 7 | the (speaker, subject) dedupe removed | same | red |
| 8 | first-hand rank removed from the sort key | same | red |
| 9 | subject grouping removed from the sort key | same | red |
| 10 | the per-(subject, class) budget disabled | same | red |
| 10b | the budget drops by render position, not arrival time | same | red |
| 11 | `evidence_rows` not threaded into the render | same | red |
| 12 | the ledger built only while the lever is ON | same | red |
| 13 | the counter validator removed from the chain | same | red |
| 14 | the counter's observation-id branch removed | same | red |
| 15 | the counter marker payload left unbounded | same | red |
| 16 | the shared turn-suffix recovery neutered | `test_manager.py` | red |
| 17 | `counter_reason_id` not elided from recorded bytes | `test_weighing_channel.py` | red |
| 18 | sighting accessor drops the episodic stamp | `test_sighting_accessor.py` | red |
| 19 | vent accessor drops the episodic stamp | `test_meeting_integration.py` | red |
| 20 | `vote_ballot` rolled back to v7 | `test_bespoke_prompt_sets.py` | red |
| 21 | the row pattern re-requires `, trust <N>` | `test_elicitation_fixtures.py`, `test_meeting_quality.py` | red |
| 22 | `BallotView` stops mirroring the counter | `test_view_model.py` | red |
| 23 | the counter marker leaves the replay-loader table | `test_view_model.py`, `test_weighing_channel.py` | red |
| 24 | the counter marker leaves the surrogate table | `test_surrogate_dataset.py`, `test_weighing_channel.py` | red |
| 25 | the counter marker leaves the deduction chain | `test_weighing_channel.py` | red |
| 26 | the deference sentence restored in the served body | same | red |
| 27 | the trust column restored on the served row | same | red |
| 28 | the evidence block rendered below the number | same | red |
| 29 | the ninth contract key dropped from the skeleton | same | red |
| 30 | the row's citation clause dropped | same | red |
| 31 | the belief render's trust branch restored | `test_memory_rendering.py`, `test_beliefs_hard_evidence_gate.py` | red |

**Five of these first came back GREEN and are named plainly**: #2 (the
`first_hand` bit on own rows), #5 (the contradiction→turn resolution), #7 (the
dedupe), #8 (the first-hand rank) and #21 (the widened row pattern). Each was an
unenforced production line; five tests were added for them —
`test_every_own_channel_row_is_marked_first_hand`,
`test_a_contradiction_row_resolves_to_the_turn_it_was_spoken_in`,
`test_one_speaker_naming_one_subject_twice_makes_one_row`,
`test_a_grounded_voice_sorts_above_an_ungrounded_one` (the rank is only
observable between two rows alike in every earlier key) and
`test_the_suspicion_row_pattern_reads_both_rendered_shapes` — and the pass was
re-run from scratch: 32 rows, 0 unenforced AMONG THE ROWS THIS PASS COVERED.
That is the true statement; the claim as filed at `cf20c03f` said "0
unenforced" flat, and round 2 falsified it — the pass never perturbed the
template's provenance branch, the self-accusation drop or the values of
`_EVIDENCE_KIND_CLASS`, and all three survived. Six further rows are in the
round-2 subsection, and the coverage rule they were found under is now stated
plainly: a mechanical pass must perturb every BRANCH and every CONSTANT the diff
adds, not only the statements.

Beside the table, the acceptance items' own planted cases:

* **a row built from another participant's channel** —
  `test_a_row_built_from_another_participants_channel_is_caught` runs the real
  assembler on p-1's records and checks the rows against p-2's id set: 4
  violations, and 0 against their real owner, so the invariant is not vacuously
  red;
* **the deference sentence restored** —
  `test_planted_the_restored_deference_sentence_is_detected` puts it back into a
  COPY of the rendered bytes and shows the predicate fires;
* **a rendered ballot recommending a target** —
  `test_planted_a_recommended_target_is_detected` runs the same
  recommendation-verb scan over a body that names one;
* **an archived body edited by one byte, the old row shape under a narrowed
  pattern, and a drifting `--check`** — the first is
  `tests/meetings/test_prompt_byte_golden.py::test_one_byte_template_perturbation_breaks_the_golden`
  and its archive sibling, both already gates and both green here; the second is
  row 21; the third is the four `--check` runs, whose failure mode
  `tests/scripts/` already plants.

**Properties, not examples.** `counter_reason_id` is exercised over a generated
family driven through the real `MeetingManager`: for each of seven counter
values — absent, fabricated, a valid turn id, a valid observation id, another
player's observation id, an injection-shaped string and a marker-shaped string —
the recorded target, the confidence, the outcome, the ejected player, both
primary citations and every `grounding_label` equal what the identical meeting
produced with no counter at all. A separate case shows a marker-shaped counter
lands INSIDE the counter marker's quoted payload (the chain consumes exactly one
marker and the model's body survives intact), and an over-length value is bounded
by `bounded_marker_original`.

### The prediction, written down BEFORE anything is re-recorded

Dated **2026-09-21**, and it is NOT a gate. After
[the re-record](process-rerecord.md) runs on this substrate:

* the FOLLOWER share of crew EJECT ballots should FALL from today's **93.6%**
  (`ml_corpus/9p2i`, 1,189 of 1,270) and **92.9%** (`samples/9p2i`, 403 of 434);
* deviating EJECTs should be AT LEAST as role-correct as following ones, against
  today's **8.6% versus 96.1%** (`ml_corpus/9p2i`) and **6.5% versus 88.8%**
  (`samples/9p2i`).

The same prediction is recorded, dated, in
[the scorecard card](process-scorecard.md)'s Results. Under ruling D1
role-correctness is reported beside and gates nothing: a wrong call on rows the
voter can cite is the outcome the owner asked for, and this card's Record
impact already says the ejection rate will move in either direction. Neither
figure is a merge condition for anything.

### Limitations

* **Nothing is measured on new bytes.** No provider call, no recording, no
  re-scored report; every number above is either a committed-bytes
  recomputation or a test count. What the v8 body actually does to a voter is
  unknown until the re-record, by design.
* **The testimony rows' `first_hand` bit is only as good as the ledger's
  grounding predicates**, which are the detector's own. A speaker who saw
  something their record does not bear out reads as "not first-hand", which is
  what is known, not a claim that they lied.
* **The suspicion number is only PARTLY decomposed by the rows.** Two of the
  eight provenance channels reach no row: a witnessed KILL (the participant
  carries no kill channel, and `sighting_records_for_meeting` filters the kill
  action out) and the BODY-PROXIMITY lift (whose row would name the nearby
  suspect, while the body-discovery row names the dead victim). A number can
  therefore sit above lines that do not add up to it; the rendered memory block
  still carries both, and the template calls itself a PARTIAL summary rather
  than a running summary of the lines above (review round 1).
* **A contradiction row's speaker is a resolution, not a certainty.** It cites
  the turn the SUBJECT spoke where the flag resolves to one; where it resolves
  only to the other side of the conflict the row cites THAT turn and names its
  speaker, and where the event ids name no turn of this meeting the row renders
  with no citation and the SUBJECT as its speaker — honest, but thinner than the
  resolved case.
* **The per-(subject, class) budget can hide evidence.** Eight rows per group is
  a page bound, not a claim that a ninth did not exist; the rendered memory block
  above still carries it, and the template says so.
* **`audits/workflows/extract_gameplay_facts.py` keeps the narrowed row
  pattern** (deviation 5): it will skip post-re-record rows until someone who may
  move `audits/` bytes widens it.
* **The four committed `tournament-eval-report.json` files stay byte-identical**
  only because the new ballot key is elided when null. A future field that is not
  elided moves them.

### Review corrections, round 1 (2026-09-21)

Eight blocking findings from two independent lenses, SIX distinct defects: two
pairs were the same defect found twice (the teammate firewall, and the
contradiction row's turn). Every command quoted below was run in this worktree
at this head, and every `file:line` is re-derived here, not carried forward.

**1 and 5. An impostor's ballot named its own teammate (§4.7).**
`_own_channel_evidence_rows` read `voter.sighting_records`,
`vent_witness_records` and `move_witness_records` with no teammate filter, so an
IMPOSTOR voter's block could render "you watched `p-2` VENT" or "you saw them in
REACTOR at tick 3, with `p-2`" about its own partner — the 7.12 own-goal, on the
shipped default path, in the one surface that reaches the model. The two
accessors hand those rows over ON PURPOSE:
`sighting_records_for_meeting` keeps a teammate-at-a-kill-window row because
that is safe for its GROUNDING consumer and its docstring said every other
consumer must re-apply the suppression, and the §6.6 render never suppressed a
witnessed teammate vent at all
(`meetings/transcript.exclude_teammate_role_proving_observations` records that).
The weighing channel is such a consumer and did not.

The drop is applied at assembly (`meetings/manager.py:3462`), exactly where the
manager already re-applies it for the prosecution mapping (`:1345`): every row
whose subject is a fellow impostor is dropped, and every fellow is stripped from
a sighting's `co_present` companions so the "with …" suffix cannot re-introduce
one sideways. It is BROADER than `_sighting_is_suppressed`'s kill-window rule —
any room, any tick, the shape `move_witness_records_for_meeting` already uses —
and empty for every crewmate and sole impostor, so the crew path is unchanged.
Body-discovery rows take no filter and need none: `engine/rules.py:80` refuses a
kill whose target is an impostor, so a body is never a teammate's, and the
docstring says so rather than carrying a line no test could reach. The
FLAG and TESTIMONY rows naming a teammate are deliberately NOT dropped: those
are public facts of this meeting that the `<contradictions>` block and the
transcript already put in front of everyone, and hiding them would tell the
impostor something false about the table.

Proofs: `TestTheTeammateFirewall` —
`test_no_own_row_names_a_fellow_impostor` (an impostor holding all three shapes,
including the co-present route),
`test_the_identical_records_on_a_crewmate_keep_every_row` (the same four records
with `fellow_impostor_ids=()` keep every row AND the `with p-2, p-4` companion,
so the drop is the firewall's and nothing else's),
`test_the_public_rows_about_a_teammate_are_not_dropped`, and
`test_the_firewall_holds_through_the_real_meeting` driven through the real
`MeetingManager`. The documentation half is the same finding's other leg:
`orchestrator/game.py:3906-3932` (sighting) and `:3845-3858` (vent) now state
what is true — these rows DO reach a prompt, and the consumer re-applies the
firewall — and `meetings/manager.py:1345` and
`tests/meetings/test_manager.py:7073` name both re-applying consumers instead of
"its only consumer corroborates". Before this round,
`grep -ci teammate tests/meetings/test_weighing_channel.py` returned 0; it now
returns 16 (`impostor`: 0 → 17).

**2. The Task-14.12 railroad gate would have gone VACUOUS on v8 bytes.**
`eval/validity._SUSPICION_GRAPH_ROW_RE` kept the narrowed `, trust <N>` shape
while `eval/meeting_quality`'s was widened. It is not a loud failure: a v8 prompt
matches nothing, `_rendered_suspicions` returns `[]`, no row clears
`CERTAIN_GUILT_SUSPICION`, and `check_no_railroaded_crew_ejections` —
`run_validity_gate`'s fifth check, the one `scripts/validity_gate.py` runs over
any report — reports `passed=True` over a railroaded crew row. Widened at
`eval/validity.py:190` with the comment (`:176-189`) stating the vacuity, and
pinned by `test_railroad_reads_both_rendered_row_shapes`, parametrised over
`", trust 0.0"` and `""` with `rendered_crew_rows > 0` asserted on both legs.
The two test-local copies of the pattern that read COMMITTED prompts
(`tests/meetings/test_manager.py:3997`, `tests/agents/test_beliefs.py:3479`) are
widened in the same move with the reason in a comment; they change no number
today, because every prompt they read carries the suffix. The one reader left
narrowed is `audits/workflows/extract_gameplay_facts.py:272`, which deviation 5
already declares and this card may not touch.

**3 and 6. A contradiction row cited the witness's turn, not the account.**
`meetings/transcript` canonicalises a flag's event pair with `sorted()`, so
`event_a_id` is the lexically smaller id — the WITNESS's turn whenever the
witness spoke first — and the builder resolved `event_a_id` first and stopped.
A flag about `p-2`'s account spoken in `m-1:turn-1`, raised against a sighting
spoken by `p-4` in `m-1:turn-0`, rendered `speaker=p-4`, `citation_id=m-1:turn-0`
under `p-2`'s name, while the ballot tells the voter to "cite the turn that
account was spoken in". Both event ids are now resolved and the row prefers, PER
SUBJECT, the turn that subject spoke (`meetings/manager.py:3595-3602`); the
fallback is stated at the strength it delivers, in the builder's docstring, in
`EvidenceRow`'s and in the Limitations above. Proofs:
`test_a_cross_turn_flag_cites_the_subjects_own_account` (the adverse ORDER, which
the one pre-existing test could not show because it planted both ids inside a
single turn) and `test_a_flag_that_names_no_turn_of_the_subjects_falls_back`.

**4. Four live-tense guarantees inside the diff were false.** All four are
rewritten to what the code delivers, and three sibling paragraphs that had
drifted the same way went with them:
`_testimony_evidence_rows` (the ledger is built UNCONDITIONALLY since D5, so a
grounded voice IS marked first-hand on the default path — the reverse of what
the docstring said and of what
`test_a_grounded_voice_is_marked_first_hand_on_the_default_path` asserts);
`vent_witness_records`' "it never reaches a prompt surface" (it does, as this
voter's own `own_vent` rows); `observation_ids`' "consulted in exactly ONE
place" (two, both the same shared decision `_resolved_observation_id`); the
stale "`None` while the lever is OFF" comment sitting directly above the
unconditional build; plus `sighting_records`' "two consuming seams" and "OFF,
the channel reaches no prompt surface", `move_witness_records`' "Nothing else
reads it", and `body_discovery_records`' "reads it in exactly one place".

**7. The suspicion number was called a running summary of rows that cannot
contain two of its inputs.** `SuspicionEntry` carries `body_proximity` and
`kill_or_vent_pin`; `MeetingParticipant` has no kill channel,
`sighting_records_for_meeting` filters the kill action out, and an
`own_body_discovery` row names the dead victim rather than the nearby suspect
the proximity lift raised. Of the two repairs the finding offered, the rows were
NOT added — a kill channel is new plumbing on the participant, the orchestrator
and the firewall, which this card may not take — so the claim is weakened to
what is true. The served line now reads "only a PARTIAL summary of the lines
above" and NAMES both inputs (`vote_ballot.j2:262` at this head, `:258` at
`6b79ff08`), the same correction is made
in `build_evidence_rows`, `EvidenceRow`, the template header, this card's
Outcome and the PR body, and a Limitations bullet is added. The renderer
Protocol paragraph was named in this list at `6b79ff08` and was NOT in fact
corrected — round 2's finding 3 caught the overclaim and made the sixth edit;
this sentence is the round-1 list restated true. Pinned by
`test_the_number_is_called_a_partial_summary_of_the_rows` with its planted twin
`test_planted_the_complete_summary_claim_is_detected`. The weakened sentence
names no player, ranks nothing and still points at the evidence rather than the
count, which the same test asserts.

**8. The symbol table cited lines that were wrong at the reviewed head.** The
whole table is re-stamped above, at THIS head and by `grep -n` on each symbol,
with the round-0 value kept beside it; the same pass corrected the Decisions
prose (`MAX_EVIDENCE_ROWS_PER_SUBJECT` `:3390`→`:3413`, the
`cited_before_validation` read `:2444`→`:2456`, `VoteBallot._serialize`
`:1163`→`:1148`, the `adjust_trust` history note `:966`→`:969`, the ledger build
`:1568`→`:1625`) and the two non-Python rows (`BallotCard.tsx` `counterKind`
`:57`→`:68`; the chip label is `frontend/src/lib/copy.ts:450`, not
`BallotCard.tsx:32`).

**No version bump for the v8 body edit.** `vote_ballot` stays at
`qwen3_6_27b.v8`: nothing has been recorded under v8, so the two generations
this repo's one-stamp-one-body rule separates do not exist here — the v8 body is
still unshipped and unrecorded, and the only stamp any committed game carries is
`v5`, which the alibi card's archive covers. Nothing is re-recorded or
re-scored in this round either.

**The round-1 perturbation pass.** Ten rows over every production line this
round adds or changes; each edits ONE thing, runs the named probe, and restores
from an in-memory COPY (never `git checkout`), with
`PYTHONDONTWRITEBYTECODE=1 -p no:cacheprovider`. **Every one came back RED on
the first attempt — no probe in this round first returned green.**

| # | perturbation | probe | result |
| --- | --- | --- | --- |
| R1 | `eval/validity.py`'s row pattern re-narrowed to require `, trust <N>` | `tests/eval/test_validity.py` | red |
| R2 | the own-VENT teammate drop removed | `test_weighing_channel.py` | red |
| R3 | the own-SIGHTING teammate drop removed | same | red |
| R4 | the `co_present` teammate strip removed | same | red |
| R5 | the own-TRANSIT teammate drop removed | same | red |
| R6 | `teammates` read as an empty set instead of `voter.fellow_impostor_ids` | same | red |
| R7 | the contradiction's per-subject preference removed (cite the first sorted event) | same | red |
| R8 | only `event_a_id` resolved (the second slot never tried) | same | red |
| R9 | the contradiction fallback returns `None` instead of the first resolvable turn | same | red |
| R10 | the template's PARTIAL-summary sentence restored to "A running summary of the lines above" | same | red |

R1 is the finding's own repro: under the narrowed pattern the OTHER railroad
tests stay green and only the new one fails, which is what "vacuous" means here.
The two test-local pattern widenings (`test_manager.py`, `test_beliefs.py`) are
deliberately NOT in the table: they read committed prompts only, every one of
which carries the trust suffix, so the change is unobservable today and the
comment beside each says so.

**The closing greps, run at this head.**

```
$ grep -rni "running summary" --include=*.py --include=*.j2 --include=*.md .
  audits/audit-2026-06-22-0446-ground-up.md:64   (history, 2026-06-22)
  tests/meetings/test_weighing_channel.py:77     (the FORBIDDEN string constant)
  tests/meetings/test_weighing_channel.py:1244   (the docstring naming it)
$ grep -rni "never reaches a prompt|reaches no prompt|reach a prompt" (per-word)
  meetings/manager.py:862        observation_ids -- still true
  orchestrator/game.py:3925      the corrected sighting paragraph
  orchestrator/game.py:3929      "a teammate reaches no prompt through this channel"
  eval/evidence_honesty.py:66,359,583   ballot-rationale markers -- unrelated, true
$ grep -rni "in exactly one place" --include=*.py .        (no hits)
$ grep -rni "ledger is built only|built only while the corroboration" .
  tasks/work/ballot-weighing-channel.md:601      the round-0 perturbation row (a
                                                 perturbation's name, not a claim)
$ grep -rni "its only consumer" --include=*.py . | grep -i firewall-adjacent
  meetings/manager.py:1345 and tests/meetings/test_manager.py:7073 -- both rewritten
```

**Gates re-measured at this round's head**, each exit code captured directly,
never through a pipe. The card's own Validation list is covered in full; no
live provider call of any kind was made and none is a check.

```
$ bash scripts/check.sh                                   EXIT=0
  ruff check . / ruff format --check .  518 files, all clean
  lint-imports                          4 contracts kept, 0 broken, 189 modules
  validate_task_docs.py                 390 phase tasks + 390 prompts; 73 work cards
  generate_prompts.py --check           all 390 prompts in sync
  mypy .                                no issues in 489 source files
  pytest -n auto --dist loadfile        8220 passed, 20 skipped, 3 xfailed
                                        (8210 at the first pass: +10 new tests)
  frontend lint / tsc:check / vitest    557 tests in 20 files passed; build green
$ bash scripts/verify_samples.sh                          EXIT=0
  replays/samples/4p1i  All 50 samples verified clean.
  replays/samples/9p2i  All 50 samples verified clean.
$ uv run python scripts/build_sample_report.py --sample-dir <set> --check
  the two replays/samples/ and two replays/ml_corpus/ sets       EXIT=0 each
  ("consistent with its replays" on all four)
$ uv run python scripts/publish_process_scorecard.py --check              EXIT=0
$ uv run python scripts/verify_ml_evidence.py                             EXIT=0
  checks: 61 | OK 49 | FAIL 0 | ABSENT 7 | INFO 5   (never --complete)
$ uv run python scripts/check_doc_facts.py                                EXIT=0
$ uv run pytest tests/scripts/test_verify_ml_evidence.py -q               EXIT=0
  80 passed
```

The four `--check` recomputations and the scorecard are byte-identical to the
first pass, which is the point: this round touched no recorded byte, and the
widened `eval/validity` pattern reads the committed `, trust 0.50` rows exactly
as the narrow one did.

No `audits/` or `tests/fixtures/` byte moved in this round, so no
`docs/artifacts.md` row is recomputed here; deviation 1's recomputation from the
first pass stands unchanged.

### Review corrections, round 2 (2026-09-21)

Four blocking findings from two independent lenses, four distinct defects. Every
command quoted below was run in this worktree at this head, and every `file:line`
is re-derived here by `grep -n` on the symbol, not carried forward.

**1. The served v8 row told the voter it had PERCEIVED its own rhetoric.** The
provenance clause tested `row.speaker == voter_id` BEFORE `row.first_hand`, so
the two row kinds that can carry the voter's own id with `first_hand=False` —
a `testimony` row for a name the voter itself spoke (`speaker=turn.speaker`,
`meetings/manager.py:3702`) and a `contradiction` row that resolved to a turn the
voter spoke (`speaker=speaker_by_turn_id.get(...)`, `:3638`) — rendered as
"first-hand: you saw this yourself". That is the one thing a provenance clause
may never invent: it hands the voter its own accusation back as evidence it
perceived, on the shipped default path, in the block this card exists to make
honest. The clause now branches on `first_hand` FIRST and only then on the
speaker (`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:256`), giving four
leaves — "first-hand: you saw this yourself", "first-hand: `<speaker>` saw it
themselves", "not first-hand: you stated it at this table", "not first-hand:
`<speaker>` stated it at this table" — and the template header states the
precedence at `:110-113`. One test per leaf plus the two-kind case and its
planted twin, in `TestTheServedBody`.

Count-only census over the two committed sample sets at THIS head, through the
real `build_evidence_rows` and the real `renderers.vote("qwen3_6_27b")`, keyed by
(set, meeting), printing no rendered prompt and no seed-band prefix (the same
reconstruction `test_the_invariant_holds_over_committed_meeting_transcripts`
uses: recorded transcripts and recorded flags, a voter whose own channels are
empty):

| samples set | meetings | ballots | rows the voter itself spoke, NOT first-hand | of which contradiction / testimony | ballots carrying one |
| --- | --- | --- | --- | --- | --- |
| 9p2i | 151 | 869 | 739 | 90 / 649 | 738 |
| 4p1i | 39 | 117 | 103 | 20 / 83 | 103 |

That reproduces the finding's own census to the digit, pooled testimony 732 and
contradiction 110. At the reviewed head all 842 rendered "first-hand: you saw
this yourself"; at this head all 842 render "not first-hand: you stated it at
this table" and that string appears 739 + 103 times. The 89 + 20 lines that
still read "you saw this yourself" are exactly the 109 `testimony` rows the
ledger marked first-hand for a voter who watched the vent it is naming
(`meetings/corroboration._speaker_grounding_places`' vent channel grounds a
speaker with no `SightingRecord` in hand), where the clause is TRUE. Nothing is
re-scored: the recordings are read as recorded and the rows are minted at render
time exactly as production mints them.

**2. Three production constructs survived neutering with the suite green.** The
round-0 pass perturbed statements and call-site arguments but never a BRANCH
ORDER or the VALUE of a constant, and all three of the finding's probes
reproduced here. Each is now enforced, and the coverage rule is written into the
round-0 paragraph above so the next pass cannot repeat the omission:

* the template's provenance branch — the four leaf tests of finding 1, of which
  `test_what_the_voter_merely_said_here_is_not_rendered_as_perception` runs over
  both kinds that can reach the adverse pair;
* the self-accusation drop, `or subject == turn.speaker`
  (`meetings/manager.py:3685`) —
  `test_a_speaker_who_names_themselves_is_no_voice_against_themselves`. Its
  first leg drives a REAL meeting in which p-2 accuses p-2, asserts the
  `("p-2", "p-2")` claim in the final transcript (nothing upstream removes it:
  `_drop_non_roster_claims` drops only names off the roster and a living speaker
  is on it), and then asserts no ballot's rows carry a row whose speaker is its
  own subject; the second leg puts the same claim through the assembler
  directly, where the one row the transcript may yield is the other speaker's;
* the ranks in `_EVIDENCE_KIND_CLASS` (`meetings/manager.py:3421`) —
  `test_the_three_provenance_classes_rank_in_the_stated_order`, which states the
  order as LITERAL kinds. The pre-existing
  `test_the_stated_order_holds_under_every_adjacent_swap` re-derives its key from
  that same constant, so exchanging two of its values moved the rendered order
  AND the expectation together; the new test drives four rows about ONE subject
  built so arrival time disagrees with class rank inside each first-hand group,
  and fails on both the value exchange and on dropping the class term from the
  sort key.

**The round-2 perturbation pass.** Six rows over every branch and constant this
round's findings name, each editing ONE thing, running the named probe and
restoring the file from an in-memory COPY (never `git checkout`), with
`PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`; `git status` clean after
every row.

| # | perturbation | probe | result |
| --- | --- | --- | --- |
| R2-1 | the clause tests the speaker before `first_hand` (the reviewed head's own bytes) | `tests/meetings/test_weighing_channel.py` | red (2 failed, 55 passed) |
| R2-2 | the two FIRST-HAND leaves exchanged | same | red (2 failed) |
| R2-3 | the two NOT-first-hand leaves exchanged | same | red (3 failed) |
| R2-4 | the first-hand and not-first-hand blocks exchanged | same | red (5 failed) |
| R2-5 | `or subject == turn.speaker` deleted | `test_weighing_channel.py`, `test_corroboration.py` | red (1 failed, 167 passed) |
| R2-6 | `_EVIDENCE_KIND_CLASS` `contradiction`/`testimony` values exchanged | `test_weighing_channel.py` | red (1 failed, 56 passed) |

**Named plainly: R2-1, R2-5 and R2-6 first came back GREEN**, at the reviewed
head `04214220`, which is the finding. R2-2, R2-3 and R2-4 are new branches this
round adds and were red from the first attempt. The prose corrections of
findings 3 and 4 are docstrings and comments with no observable behaviour; they
carry no perturbation row and are verified by the closing greps below.

**3. The renderer Protocol kept the completeness claim.** `VotePromptRenderer`'s
`evidence_rows` paragraph still read "the typed `EvidenceRow` pieces THIS
voter's suspicion numbers were built FROM", the exact claim round 1 weakened in
five other places and then listed this one among them. It now states the limit
the code delivers (`meetings/render_contract.py:461-473`), naming both channels
that reach no row — a witnessed KILL, because the participant carries no kill
channel, and the BODY-PROXIMITY lift, because the body-discovery row names the
dead victim rather than the nearby suspect — and says a template must render the
figure as a PARTIAL summary and never as the rows' total, mirroring `:164-166`
and `build_evidence_rows` at `meetings/manager.py:3730-3739`. The round-1
paragraph that claimed this site had already been corrected is restated true
above rather than left standing.

**4. Comments this diff made false.** Three named by the finding and two more the
closing grep turned up, all corrected to the counts the code delivers:
`training/surrogate/dataset.py:189` ("the same eight kinds" → nine; both tables
print nine labels, and the very next line's "tenth kind" was already updated in
this diff), and the vote body's version distance at
`tests/scripts/test_record_ml_corpus.py:980`,
`tests/agents/test_bespoke_prompt_sets.py:548`,
`tests/meetings/test_prompt_byte_golden.py:1341` and
`tests/agents/test_impostor_answer_arm.py:683` — "a version ahead" → TWO versions
ahead, D6 having moved `vote_ballot` alone v6 → v7 and D5 alone again v7 → v8,
beside three templates at v6.

**The closing greps, run at this head.**

```
$ len(BALLOT_AUDIT_MARKERS), len(api.replay_loader._BALLOT_PREFIX_MARKERS)
  9 9                       (identical label sets)
$ grep -rniE "eight kinds|nine kinds|same eight|ninth kind|tenth kind" \
      --include=*.py --include=*.j2 --include=*.md --include=*.ts --include=*.tsx .
  training/surrogate/dataset.py:189   "the same nine kinds"      -- corrected
  training/surrogate/dataset.py:190   "the tenth kind"           -- true
  training/surrogate/dataset.py:247   "The tenth kind"           -- true
  tests/scripts/test_counterfactual_phase21.py:3213  eight REPORTED-STATEMENT
                                       kinds -- unrelated, true
  tests/meetings/test_elicitation_fixtures.py:267    eight SuspicionProvenance
                                       channels -- unrelated, true
  (everything else is tasks/phase-*, audits/ and agent_prompts/ history)
$ grep -rniE "versions? ahead" --include=*.py --include=*.j2 --include=*.md \
      --include=*.ts --include=*.tsx --include=*.sh . | grep -v tasks/phase-
  four test comments, all reading "TWO versions ahead"; plus this card
$ grep -rni "saw this yourself" --include=*.py --include=*.j2 --include=*.md \
      --include=*.ts --include=*.tsx .
  vote_ballot.j2:256                   the first-hand leaf of the new branch
  test_weighing_channel.py:1394,1423,1437,1440   the leaf test, the
                                       not-perception assertion and its twin
$ grep -rniE "trust them over|adjust_trust|deference|credibility scalar" \
      --include=*.py --include=*.j2 --include=*.ts --include=*.tsx .
  experiments/lab/qwen36_prompt_scratch/v3,v4,v5  frozen scratch rungs (history)
  tests/fixtures/prompt_archive/qwen3_6_27b_v5/vote_ballot.j2:259  the archived
                                       v5 body the golden replays (history)
  the rest are past-tense test comments naming the deletion -- round 1's sweep
```

**No version bump for this round's v8 body edit**, on the same reasoning round 1
recorded: nothing has been recorded under v8, so the one-stamp-one-body rule
separates no two generations here — the v8 body is still unshipped and
unrecorded, and the only stamp any committed game carries is `v5`, which the
alibi card's archive covers. Nothing is re-recorded or re-scored in this round;
the four `--check` recomputations and the scorecard are byte-identical again.

**Gates re-measured at this round's head**, each exit code captured directly,
never through a pipe or a compound command. The card's own Validation list is
covered in full; no live provider call of any kind was made and none is a check.

```
$ bash scripts/check.sh                                   EXIT=0
  ruff check . / ruff format --check .  518 files, all clean
  lint-imports                          4 contracts kept, 0 broken, 189 modules
  validate_task_docs.py                 390 phase tasks + 390 prompts; 73 work
                                        cards (2 ready, 71 done — re-derived,
                                        and this card's Status does not move)
  generate_prompts.py --check           all 390 prompts in sync
  mypy .                                no issues in 489 source files
  pytest -n auto --dist loadfile        8227 passed, 20 skipped, 3 xfailed
                                        (8220 in round 1: +7 new tests)
  frontend lint / tsc:check / vitest    557 tests in 20 files passed; build green
$ bash scripts/verify_samples.sh                          EXIT=0
  replays/samples/4p1i  All 50 samples verified clean.
  replays/samples/9p2i  All 50 samples verified clean.
$ uv run python scripts/build_sample_report.py --sample-dir <set> --check
  the two replays/samples/ and two replays/ml_corpus/ sets       EXIT=0 each
  ("consistent with its replays" on all four)
$ uv run python scripts/publish_process_scorecard.py --check              EXIT=0
$ uv run python scripts/verify_ml_evidence.py                             EXIT=0
  checks: 61 | OK 49 | FAIL 0 | ABSENT 7 | INFO 5   (never --complete)
$ uv run python scripts/check_doc_facts.py                                EXIT=0
$ uv run pytest tests/scripts/test_verify_ml_evidence.py -q               EXIT=0
  80 passed
```

`tests/meetings/test_prompt_byte_golden.py` is inside that suite and stayed
green through its recorded-decision walk and divergence census: the v8 body is
unrecorded, the 300 committed games replay from the v5 archive, and no
bump-in-flight entry is owed. No test was weakened, skipped or deleted in this
round and no expectation changed; the only test-file edits are seven added tests
and five corrected comments. No `audits/` or `tests/fixtures/` byte moved, so no
`docs/artifacts.md` row is recomputed.
