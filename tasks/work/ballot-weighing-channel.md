# Give the voter evidence to weigh instead of a verdict to follow

**Status:** ready

## Outcome

At vote time the ballot prompt stops handing the voter a finished number and
stops telling it to follow that number. For each living ejection target it
renders the EVIDENCE ROWS the suspicion figure was built from: the voter's own
first-hand sightings, vents, transits and body discoveries; the contradictions
naming the target; and the testimony about the target, each row naming its
speaker, saying whether that speaker saw it first-hand or is repeating another
voice, and carrying the id a ballot may cite for it. The scalar stays, moved
below its rows and relabelled as their summary; the sentence instructing
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

- [ ] Typed evidence rows, assembled from typed inputs only. A frozen
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
- [ ] Evidence renders first, the number last, and no wording pushes at a
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
- [ ] `counter_reason_id` end to end, composing into ONE decision record.
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
- [ ] Trust is DELETED, not wired, and the card says why: a credibility scalar
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
- [ ] The version cascade, the archive window, and old recordings that keep
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
- [ ] The prediction is written down BEFORE anything is re-recorded, and is not
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
