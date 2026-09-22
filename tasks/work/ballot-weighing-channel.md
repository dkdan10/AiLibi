# Give the voter evidence to weigh instead of a verdict to follow

**Status:** done

## Outcome

At vote time the ballot prompt stops handing the voter a finished number and
stops telling it to follow that number. For each living ejection target it
renders the EVIDENCE ROWS behind the suspicion figure that the meeting layer can
NAME: the voter's own
first-hand sightings, vents, transits and body discoveries; the contradictions
naming the target; and the testimony about the target, each row naming its
speaker, saying whether that speaker DESCRIBED a sighting of their own at this
table or only named the player,
and carrying the id a ballot may cite for it. Nothing in the block says whether
a spoken account is true: the voter is given claims to price, some of which are
lies, and is never told which (review round 3). It is not a complete
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

- [x] Review correction (round 4, a CORRECTNESS defect): two of the union
  members `_stated_sighting_subjects` reads were unenforced. Dropping
  `SawKillObservation` alone, or `SawMoveObservation` alone, left the whole
  suite green, because round 3's row 6c neutered all three at once and its one
  failure was the vent case. The served set offers both shapes to speakers
  (`accusation_round.j2`, `crewmate_report.j2`, `_account_rules.j2`), so it is
  live behaviour. `test_a_described_sighting_marks_the_row_true_or_fabricated`
  is parametrised over ALL FOUR shapes, keeping the two-speaker
  borne-out/fabricated pair in each case, and row 6c is split into per-member
  rows 6c-a/b/c/d, each red on its own removal. No production behaviour
  changes.
- [x] Review correction (round 4, record integrity): the Results symbol table
  and three prose citations were stale at `d7b6be94` — round 3 moved
  `meetings/manager.py`, `meetings/render_contract.py` and `vote_ballot.j2`
  after the table said it was re-stamped at the final head. Every citation in
  the CURRENT sections is re-derived mechanically (`ast` for definitions,
  `grep -n` for lines) AFTER this round's last edit, each prior value kept in
  parentheses, with a dated note saying round 3 left the table behind.
- [x] Review correction (round 4): the two live Codex review comments carry a
  dated judgement in the card and the PR body — 4062448106 (null counter vs
  `none_held`): not a defect, but its second half is a real prompt gap, closed
  by one prose sentence saying what "pointing away" means for a SKIP, pinned by
  `test_the_counter_bullet_says_what_points_away_from_a_skip`; 4062448113
  (HISTORY blocks): premise false against the repo's own practice at base. No
  PR comment is posted.
- [x] Review correction (round 4), the smaller items: the trust field's
  survival is restated at DELIVERED strength; `_stated_sighting_subjects`'
  false reason for excluding `FoundBodyObservation` is replaced by the true
  one; `TestTheAssemblerCannotReachTheLedger`'s docstring says what the test is
  (a per-function name scan, not a call graph) and names the value family as
  the layered half; the closing greps are re-run and quoted UNCONDENSED; the
  deviations index gains the five files disclosed elsewhere; and the pre-existing
  flag-description leak the correctness verifier measured is recorded for the
  owner, outside this card.
- [x] Review correction (round 3, the PRINCIPLE defect): a testimony row's
  provenance is a pure function of the PUBLIC transcript — did that speaker
  describe seeing this subject at this table — and never of whether the
  speaker's own private record bears the account out. `testimony_ledger` leaves
  `build_evidence_rows` and its three builders entirely, the manager builds the
  ledger only while the corroboration lever is ON again, and the evidence block
  says nothing is confirmed. This SUPERSEDES the acceptance clause below that
  named `testimony_ledger` as one of the row sources; the reasoning is in the
  round-3 subsection of Results. `TestProvenanceReadsOnlyThePublicTranscript`
  (a 12-case family through the real `MeetingManager`, plus the fabricated-vent
  and described-nothing examples) and `TestTheAssemblerCannotReachTheLedger`
  (the `ast` call-graph guard). [CORRECTED, round 4, 2026-09-21: the second is
  not a call-graph guard. It is a per-function NAME SCAN over five named
  functions, so a neutrally-named helper that itself called
  `build_testimony_ledger` would pass it untouched; only the VALUE family
  catches that. The class docstring now says what the scan is and names the
  value family as the layered half.]
- [x] Review correction (round 3): the three production constructs that
  survived neutering with the suite green are enforced —
  `move_witness_records_for_meeting`'s episodic stamp
  (`tests/orchestrator/test_meeting_integration.py::TestMoveWitnessRecordsAccessor`)
  and the `subjects_of_interest` guard on each of the two public-row builders
  (`test_a_flag_about_a_player_nobody_may_vote_for_builds_no_row`,
  `test_a_voice_against_a_player_nobody_may_vote_for_builds_no_row`, one probe
  each). The mechanical pass was re-run whole over the production diff: 70 rows,
  in the round-3 subsection of Results, with the five that are red only because
  of a test THIS round adds named and each re-measured GREEN with its own pin
  deselected.
- [x] Review correction (round 3, the second author's own finding): the served
  block described its row order as "what you perceived yourself before anything
  you are repeating", which names the wrong subject — `_sort_key`'s second term
  is the ROW'S `first_hand`, so a voice that described a sighting sorts above a
  contradiction about the same player. The sentence now states the key the code
  applies and says a described sighting sorts there whether or not it happened;
  pinned inside `test_the_block_tells_the_voter_nothing_was_checked` and probed
  as row R3-8.
- [x] Review correction (round 3): the four places claiming an OFF meeting's
  prompt bytes were unchanged by the unconditional ledger build now state what
  the code delivers — the ledger is BUILT only when the lever is ON, so the
  claim is true again by construction rather than by argument
  (`meetings/manager.py`, `meetings/corroboration.py`, this card's Decisions
  and the PR body), and no claim about v8 bytes rests on the prompt-byte
  golden, which replays v5 archives over all 300 committed games.
- [x] Review correction (round 3): this card's Record impact and the version
  cascade item below carried dated corrections — one `tests/fixtures/` byte DID
  move and `docs/artifacts.md:101` WAS recomputed (deviation 1 recorded it; the
  two earlier sentences denied it). The row is re-verified against disk at this
  head: 2,196,250 tracked bytes / 35 files.
- [x] Review correction (round 2): the served row reads `first_hand` BEFORE the
  speaker, so a testimony or contradiction row the voter itself spoke renders as
  a statement made at this table and never as something the voter perceived.
  `tests/meetings/test_weighing_channel.py::TestTheServedBody` —
  `test_what_the_voter_merely_said_here_is_not_rendered_as_perception` over both
  kinds, its planted twin `test_planted_the_old_branch_order_is_detected`, and
  one test per branch:
  `test_a_row_the_voter_perceived_says_it_saw_it_itself`,
  `test_a_grounded_voice_names_the_speaker_who_saw_it`,
  `test_another_voice_at_this_table_names_that_speaker`. [Round 3, 2026-09-21:
  the property is KEPT and strengthened — an own-channel kind is now read
  before anything else, so a row the voter merely spoke is a statement
  whatever its `first_hand` bit says. The clause has five leaves and the last
  two tests above are renamed
  `test_a_describing_voice_is_quoted_as_saying_so` and
  `test_another_voice_that_described_nothing_is_marked_that_way`, with
  `test_a_flag_somebody_else_spoke_into_is_a_statement_here` for the fifth.]
- [x] Review correction (round 2): the two production constructs the round-0
  pass left unenforced are enforced — the self-accusation drop by
  `test_a_speaker_who_names_themselves_is_no_voice_against_themselves` (whose
  first leg drives a real meeting and shows the claim arriving intact), and the
  provenance class ranks by
  `test_the_three_provenance_classes_rank_in_the_stated_order`, which states them
  as LITERALS instead of re-deriving them from `_EVIDENCE_KIND_CLASS`. Six
  perturbation rows, all red, in the round-2 subsection of Results.
- [x] Review correction (round 2): `VotePromptRenderer`'s `evidence_rows`
  paragraph (`meetings/render_contract.py:461-473`; `:467-481` at the round-4
  head, re-derived 2026-09-21) states the limit the code
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
  [SUPERSEDED, round 3, 2026-09-21: `testimony_ledger` is NOT a source. It
  reads engine truth about whether each accuser's own record bore their spoken
  account out, and putting that on every voter's ballot is a lie detector, not
  evidence to weigh. The third source is the transcript's own typed observation
  claims, read as STATED. See the round-3 subsection of Results.]
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
  `DESIGN.md:718` are corrected. [RESTATED AT DELIVERED STRENGTH, round 4,
  2026-09-21: "one history line" understates what shipped, and the card must
  state what the code delivers. Measured at this head: a 15-line comment block
  (`agents/memory/beliefs.py:969-983`), a 12-line paragraph inside
  `_format_belief_score` (`agents/memory/store.py:2808-2819`) and a 14-line ADR
  bullet (`docs/adr/0001-three-load-bearing-decisions.md:30-43`). The blocks
  are NOT shrunk — see the round-4 judgement on Codex 4062448113 — only the
  sentence describing them.]
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
  `docs/artifacts.md`. [CORRECTED, round 3, 2026-09-21: the ARCHIVE half is
  true — no archive entry was added. The `docs/artifacts.md` half is FALSE and
  was already falsified by deviation 1 below: deleting the belief render's
  trust branch moved one line of
  `tests/fixtures/memory_rendering/crewmate_basic.expected.md`, so
  `docs/artifacts.md:101` WAS recomputed, to 2,196,250 tracked bytes / 35
  files. Re-verified against disk at the round-3 head.] In the same move
  `_SUSPICION_GRAPH_ROW_RE`
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
[CORRECTED, round 3, 2026-09-21: false as written, and deviation 1 in Results
had already recorded the truth. ONE `tests/fixtures/` byte moved — the
`crewmate_basic` golden lost its `- p-1: trust 0.70` line when the belief
render's trust branch went — and `docs/artifacts.md:101` WAS recomputed to
2,196,250 tracked bytes / 35 files, re-verified against disk at the round-3
head with `git ls-files tests/fixtures | xargs wc -c`. The `audits/` half is
true: no `audits/` byte moved in any round.]
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

Every line below is RE-STAMPED at THIS ROUND's final head (review round 4) and
re-derived mechanically after this round's last edit — `ast` for every
definition, `grep -n` for every line — not carried forward. It had drifted
before: the table said round 1 and then round 3 moved `meetings/manager.py`
(-6/+32/+38), `meetings/render_contract.py` (+8) and `vote_ballot.j2` (+5)
underneath it without re-stamping, so at `d7b6be94` fourteen cells were wrong.
Round 4 moves three files again (this round's `_stated_sighting_subjects`
docstring is +7 in `meetings/manager.py`, and the SKIP counter sentence is +4
in `vote_ballot.j2`), which is exactly why the derivation is run LAST. Each
cell keeps its prior value in parentheses.

| Contract item | Symbol | Line at the round-4 head (prior values) |
| --- | --- | --- |
| the row DTO | `EvidenceRow` / `EvidenceRowKind` | `meetings/render_contract.py:155` / `:131` (unmoved since round 1) |
| the renderer widening | `VotePromptRenderer.evidence_rows` | `meetings/render_contract.py:500` (round 3 table said `:492`, round 1 `:487`, round 0 `:481`; card said `:340-400`); its Protocol paragraph, weakened in round 2, at `:467-481` (the table said `:461-473`) |
| the three witness stamps | `VentWitnessRecord` / `SightingRecord` / `MoveWitnessRecord` `.observation_id` | `meetings/schemas.py:318` / `:358` / `:389` (unmoved; card said `:306-308`, `:340-343`, `:366-369`) |
| the ninth ballot key | `ModelAuthoredVoteBallot.counter_reason_id` | `meetings/schemas.py:1035` (unmoved; card said `:767-773`) |
| row assembly | `build_evidence_rows` + its three builders | `meetings/manager.py:3749`, `:3443`, `:3562`, `:3689` (the table said `:3710`, `:3449`, `:3568`, `:3646`; round 0 said `:3618`, `:3424`, `:3510`, `:3557`) |
| the stated-sighting set | `_stated_sighting_subjects` | `meetings/manager.py:3640` (new in round 3; never in the table) |
| the render call site | `MeetingManager._collect_one_ballot` | `meetings/manager.py:2183`; `:2265` builds the rows, `:2303` passes them (the table said `:2184` / `:2270` / `:2309`; card said `:2151`) |
| the counter validator | `_normalize_ballot_counter_reason_id` | `meetings/manager.py:4034`, called at `:2493` (the table said `:3989` / `:2499`) |
| the two shared decisions | `_resolved_reason_id` / `_resolved_observation_id` | `meetings/manager.py:3894` / `:3919` (the table said `:3849` / `:3874`), extracted from `_normalize_ballot_reason_id` at `:3939` (the table said `:3894`; card said `:3199`) and `_normalize_ballot_observation_id` at `:3985` (the table said `:3940`; card said `:3241`) |
| the counter marker | `INVALID_COUNTER_REASON_MARKER` | `meetings/manager.py:412` (unmoved) |
| the per-group bound | `MAX_EVIDENCE_ROWS_PER_SUBJECT` | `meetings/manager.py:3407` (Decisions said `:3413`) |
| the served body | `vote_ballot.j2` | `:262-267` the `<evidence>` block with the provenance branch at `:265`, `:270-271` the relabelled PARTIAL summary, `:274` the row without `trust`, `:306` where the deference sentence was deleted, `:309-310` nine keys, `:316` the counter bullet (the table said `:253-258` / `:256` / `:261-262` / `:265` / `:297` / `:300-301` / `:307`; each +9 on that — round 3's last commit added five lines above them and round 4's SKIP-counter comment adds four) |
| the row pattern | `_SUSPICION_GRAPH_ROW_RE` | `eval/meeting_quality.py:341` (unmoved; card said `:326`) and, added in round 1, `eval/validity.py:189` (the table said `:190` — the regex is DEFINED at `:189`) |
| the served DTO | `BallotView.counter_reason_id` | `api/schemas.py:1093` (unmoved; card said `:962-970`), mirrored at `api/replay_loader.py:3324` (card said `:3286`) |
| the spectator card | `BallotCard.tsx` | `:261` the third `EvidenceLink`, `:68` `counterKind` (round 0 said `:57`), `frontend/src/lib/copy.ts:450` the chip label (round 0 said `BallotCard.tsx:32`) — all unmoved |
| the marker tables | three | `api/replay_loader.py:3612` (the tuple; the counter row at `:3618`), `training/surrogate/dataset.py:207` (round 0 said `:205`; card said `:213`), `eval/deduction_metrics.py:718` (the chain; the counter row at `:725`) — all unmoved |
| the trust deletion | `BeliefState.adjust_trust` / `_format_belief_score` | `agents/memory/beliefs.py:969-983` (the 15-line history block where it stood; round 0 said `:966`; card said `:953`), `agents/memory/store.py:2792` with its 12-line paragraph at `:2808-2819` (round 0 said `:2808`) |

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

[REVERSED, round 3, 2026-09-21. The reasoning above is the defect, not the fix:
the ledger's `first_hand` is ENGINE TRUTH about another player's honesty, and
putting it on the default ballot per accuser told every voter which accusations
the engine bears out. The ledger is built only while the lever is ON again,
exactly as at this card's base, and `build_evidence_rows` takes no ledger
parameter and reaches no `meetings.corroboration` name. A testimony row's
provenance comes from the transcript alone. The OFF-bytes claim is now true by
construction — nothing is built, so nothing can be threaded — and it no longer
rests on the prompt-byte golden, which replays the committed v5 archives and
renders no v8 body at all. The round-3 subsection of Results states all of it.]

**What `first_hand` means, stated at the strength the code delivers.** True only
where the row's speaker perceived the thing themselves: every own-channel row,
and a testimony row whose speaker is in the ledger's first-hand set for that
subject. A contradiction row is the meeting layer's cross-check of two
statements rather than one speaker's perception, so it is False — said in the
DTO docstring, in `build_evidence_rows`, and in the template's own wording
("not first-hand: {speaker} stated it at this table", which is accurate for a
contradiction row as well as for an ungrounded voice).

[RESTATED, round 3, 2026-09-21. `first_hand` is provenance AS STATED: True for
every own-channel row (the voter's own perception, which the engine
witness-gated into its packet) and for a testimony row whose speaker DESCRIBED
seeing that subject somewhere in this meeting's public transcript
(`meetings/manager._stated_sighting_subjects`). Whether their own record bears
it out is never read, so a fabricated sighting and a true one carry the same
bit. The contradiction half above is unchanged and still False for the same
reason; the served wording for it is unchanged too.]

**Row order encodes no guilt, and the bound is a page rule.** Order is: subject
(the `candidate_targets` roster order, then any other subject by id), first-hand
before not, then the provenance CLASS (own perception → the detector's flags →
what was said here), then earliest-first, then kind/speaker/citation. A
witnessed vent and an ordinary sighting share class 0 on purpose, so the block
cannot rank one player's evidence above another's. `MAX_EVIDENCE_ROWS_PER_SUBJECT
= 8` (`meetings/manager.py:3407`, re-derived round 4; this paragraph said
`:3413`) bounds each (subject, class) group, not each
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
outside the `cited_before_validation` read (`meetings/manager.py:2450`,
re-derived round 4; this paragraph said `:2456`), so it
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

[RESTATED AT DELIVERED STRENGTH, round 4, 2026-09-21. "One history line" is not
what shipped in any of the three. Measured at this head: `beliefs.py:969-983`
is a 15-line comment block, `store.py:2808-2819` a 12-line paragraph inside
`_format_belief_score`, and `docs/adr/0001-three-load-bearing-decisions.md:30-43`
a 14-line bullet. Each records the same three things — that nothing ever wrote
trust, why it was DELETED rather than wired, and why the FIELD stays — and none
is shrunk this round; only this sentence and the Acceptance item are corrected
to the delivered size.]

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
6. **[Added round 4, 2026-09-21.] Five more files outside Expected scope, each
   disclosed somewhere else in this card but never listed HERE** — which is
   what this subsection presents itself as, the single index of everything that
   left the declared scope. Nothing about them is new; they are indexed:
   `eval/validity.py` (the widened row pattern, a ticked acceptance item of its
   own), `meetings/corroboration.py` (docstrings only — round 3's finding 1,
   fourth restated sentence), `eval/deduction_metrics.py` (the counter marker's
   row in `_BALLOT_MARKER_CHAIN`, which the acceptance item calls "both marker
   tables" and which is in fact three), `frontend/src/lib/copy.ts` (the counter
   chip's label constant, in the symbol table) and
   [the scorecard card](process-scorecard.md) (the dated argmax-independence
   prediction this card's acceptance requires be written in BOTH places).

### Verification

Every command below was run in this clean worktree with its real exit code
captured directly, at the FIRST PASS's final head (`6b79ff08`). Each review
round below re-ran the same list at its own head and states its own numbers
there — ROUND 4's is the CURRENT table (it was round 3's until 2026-09-21);
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

[Dated note, round 3, 2026-09-21. Neither bullet is withdrawn and neither
number moves: both are counts over COMMITTED bytes, and both are about whether
a voter's EJECT follows the opener, which nothing in round 3 touches. What the
round does change is the substrate the prediction will be measured on — at the
head it was written against, the ballot told each voter which accusers the
engine bore out, and the follower share might have fallen partly because the
block was ranking the accusers for the voter. It no longer does. So the
prediction now means what it was meant to mean: if the share falls, it falls
because the voter read evidence and priced it, not because the page sorted the
honest voices to the top for it. The prediction stays not-a-gate.]

### Limitations

* **Nothing is measured on new bytes.** No provider call, no recording, no
  re-scored report; every number above is either a committed-bytes
  recomputation or a test count. What the v8 body actually does to a voter is
  unknown until the re-record, by design.
* **The testimony rows' `first_hand` bit is only as good as the ledger's
  grounding predicates**, which are the detector's own. A speaker who saw
  something their record does not bear out reads as "not first-hand", which is
  what is known, not a claim that they lied. [RESTATED, round 3, 2026-09-21:
  the ledger is gone from the rows. The bit now says only whether the speaker
  DESCRIBED a sighting here, so it is exactly as good as the transcript — an
  invented account carries the same bit as a true one, by construction. The
  limitation that replaces this one is the opposite in sign: the block gives
  the voter no help at all in telling an invented sighting from a real one, and
  that is the intended cost.]
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

### Review corrections, round 3 (2026-09-21)

One PRINCIPLE defect decided by the orchestrator, four blocking findings, and a
second author's pass over all of it. Every command quoted below was run in this
worktree at this head, and every `file:line` is re-derived here by `grep -n` on
the symbol, not carried forward. The round's numbers are the SECOND author's own
measurements: the perturbation table was re-run from scratch and is published at
the size it actually has.

**1. The default ballot was handing every voter an engine-truth lie detector.**
At the reviewed head `0ba95723` each TESTIMONY row of the DEFAULT `<evidence>`
block read either `first-hand: p-2 saw it themselves` or `not first-hand: p-2
stated it at this table`, and `_testimony_evidence_rows` decided that word from
`MeetingTestimonyLedger.first_hand` — which `meetings/corroboration.py` defines
as the speaker's OWN PRIVATE, engine-witnessed record bearing their spoken
account out ("an invented sighting matches no record and earns no account").
Round 1 had also made `MeetingManager.run` build that ledger UNCONDITIONALLY so
the bit would be live on the shipped path. Net effect: per accuser, per voter,
on the default path, the page said whether the ENGINE confirms this person
really saw what they claim. An impostor's fabricated "I saw `p-3` vent"
rendered "not first-hand"; an honest witness's rendered "first-hand … saw it
themselves".

That is the one thing the owner's rule forbids. Verbatim: an agent "could have
a lot of accurate data, a lot of inaccurate data from lies from other players,
or a mix of both. It has to pick what data would make sense to follow." Picking
is the job. A page that marks the lies is not evidence to weigh, it is the
answer — and the wave's standing rule is that NOTHING may push an agent toward
the correct answer. The card's own Outcome sentence ("saying whether that
speaker saw it first-hand or is repeating another voice") always meant
PROVENANCE AS STATED: did this speaker CLAIM to have seen it, or only back a
charge. The implementation read it as provenance as CHECKED.

The orchestrator's decision, implemented here and not re-litigated: a testimony
row's provenance is a pure function of the PUBLIC TRANSCRIPT, and the
Acceptance clause naming `testimony_ledger` as an input is SUPERSEDED. The
round-1 statement that "the ledger is built UNCONDITIONALLY
(`MeetingManager.run`) since ruling D5" — in that round's finding 4, in the
builder's docstring and in the Decisions above — is superseded with it: the
build is gated on the lever again, exactly as at this card's base `0a1100ea`.

**The provenance definition, as built.** `_stated_sighting_subjects`
(`meetings/manager.py:3640`) walks THIS meeting's transcript up to the vote and
records, per speaker, every player named by a typed observation claim they
spoke. `first_hand` on a testimony row is `True` iff that speaker is recorded
against that subject. `meetings/schemas.py:267-277` lists EIGHT
`ObservationClaim` shapes; the four read are the ones whose fields NAME ANOTHER
PLAYER AS PERCEIVED:

| shape | field(s) read | why |
| --- | --- | --- |
| `SawPlayerObservation` | `subject` AND `co_present` | "I saw `p-4`, with `p-3`" is a claim to have seen `p-3` too |
| `SawVentObservation` | `subject` | the strongest thing sayable here, and the one most worth inventing |
| `SawKillObservation` | `subject` | a claimed perception of that player acting |
| `SawMoveObservation` | `subject` | a claimed perception of that player's transition |

The other four are excluded, each for a stated reason:
`CompletedTaskObservation` and `TaskActivityAccount` describe the SPEAKER's own
task activity and name no other player; `WhereaboutsClaim` is self-placement
(its subject IS the speaker, and a self-accusation builds no row at all);
`FoundBodyObservation`'s `body_of` names a DEAD player, who is never among the
living ejection targets a testimony row may be about, so a branch for it would
be a line no probe could reach. Whether the speaker's own record bears any of
it out is NEVER read: `build_evidence_rows` (`:3742`) and its three builders
(`:3443`, `:3562`, `:3682`) lost the `testimony_ledger` parameter entirely and
reference no `meetings.corroboration` name, which an `ast` test now enforces.

Before and after, on the same fabricated claim. `p-2` speaks
`SawVentObservation(subject="p-3", room="ENGINEERING", tick=7)` and accuses
`p-3`, holding NO `VentWitnessRecord`; a second meeting is identical except
that `p-2` holds the matching record:

| leg | at `0ba95723` | at this head |
| --- | --- | --- |
| `p-2`'s own record bears the vent out | `first-hand: p-2 saw it themselves` | `p-2 says they saw it themselves` |
| `p-2` invented the vent | `not first-hand: p-2 stated it at this table` | `p-2 says they saw it themselves` |
| `p-2` accused without describing anything | `not first-hand: p-2 stated it at this table` | `p-2 named them without describing a sighting of their own` |

The served clause (`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:261`)
now has FIVE leaves, ordered so the voter's own words can never be returned to
it as perception — an own-channel KIND first, then the speaker, then the bit:

1. the voter's own record channel → `first-hand: you saw this yourself`;
2. anything else the voter itself spoke → `not first-hand: you stated it at
   this table` (round 2's fix, strengthened: it no longer depends on the bit,
   so an impostor's own fabricated sighting cannot come back as something it
   perceived);
3. another speaker who described a sighting → `{speaker} says they saw it
   themselves`;
4. another speaker's testimony with no described sighting → `{speaker} named
   them without describing a sighting of their own`;
5. a contradiction row citing another speaker's turn → `not first-hand:
   {speaker} stated it at this table`, unchanged, because a flag is the
   detector's cross-check of two statements and not one speaker's account.

The block's header sentence (`:259`) and the template comment (`:104-118`) are
rewritten to match: they now say a spoken account is what THEY said here, that
no one has checked it, and that an invented sighting reads exactly like a real
one. Nothing in the block says confirmed, grounded, borne out, verified or
true, which `test_a_describing_voice_is_quoted_as_saying_so` asserts over the
rendered bytes.

**The ledger's gating, restored.** `MeetingManager.run`
(`meetings/manager.py:1612-1636`) builds the testimony ledger only when
`corroboration_discipline` is on. The expression is byte-identical to
`git show 0a1100ea:meetings/manager.py`'s — only the comment above it differs —
so the default path is the base's path and nothing about it is new.
`_collect_ballots` and `_collect_one_ballot` lose the second `evidence_ledger`
kwarg round 1 added, and `build_evidence_rows` is called with four arguments.
Nothing about the lever-arm stamps moved:
`CORROBORATION_DISCIPLINE_PROMPT_VERSION_SETS` spreads the default registry and
still reads `vote_ballot.qwen3_6_27b.v8`; the lever gates a BLOCK, not a
version, and no recorded stamp, prompt archive or committed body changed.
`vote_ballot` stays at v8 on the same reasoning rounds 1 and 2 recorded —
nothing has ever been recorded under v8, so the one-stamp-one-body rule
separates no two generations here.

**2. THE GATE: no ballot byte moves with another player's records.** A property
over a GENERATED family driven through the real `MeetingManager`
(`TestProvenanceReadsOnlyThePublicTranscript`, 16 collected tests). Twelve
parametrised cases — two spoken shapes (`saw_player`, `saw_move`, the two that
carry a private grounding channel the ledger reads) × three (accuser, subject)
pairs × two ticks — each run TWICE over participant sets that are identical in
everything public and differ only in the OTHER speakers' private record
channels: in leg A the accuser's own record matches their spoken sighting, in
leg B they hold nothing. 24 real meetings, 4 voters each, 96 ballots compared.
Each case asserts, in order:

* the two legs really are identical in public — `result_a.transcript ==
  result_b.transcript` and `contradictions == ()` on both, so no flag can
  differ either;
* the two legs really do differ in private — `build_testimony_ledger` over leg
  A's records puts the accuser in the subject's first-hand set and over leg B's
  does not. This is the non-vacuity check that matters: the surface that DOES
  read engine truth separates the legs, so the ballot's indifference to them is
  a fact about the ballot and not about the fixture;
* for every voter, the testimony evidence rows are equal field for field, and
  the bytes the real served v8 body renders from them are equal.

Plus the named examples:
`test_a_fabricated_vent_claim_reads_exactly_like_a_true_one` (which records
honestly that the detector's own `vent_sighting` FLAG does fire on the
borne-out leg only — that is a PUBLIC fact the `<contradictions>` block already
shows everyone, not a per-voter verdict);
`test_an_accuser_who_describes_no_sighting_reads_differently`; and
`test_a_companion_named_in_a_sighting_is_a_player_the_speaker_saw`.

The static half is `TestTheAssemblerCannotReachTheLedger` (11 collected tests),
in the idiom `tests/meetings/test_grounding_label.py:958` already uses for the
tally: parse `meetings/manager.py`, take the five functions that build the rows
(`build_evidence_rows`, `_own_channel_evidence_rows`,
`_contradiction_evidence_rows`, `_testimony_evidence_rows`,
`_stated_sighting_subjects`), and show that none takes a parameter whose name
contains "ledger" and none NAMES `ledger`, `corroboration`, `TestimonySupport`
or `first_hand_places` anywhere in its body (matched case-insensitively, after
the docstring is stripped). Non-vacuity:
`test_the_scan_finds_a_function_that_does_reach_the_ledger` shows the same scan
finds `build_testimony_ledger` inside `MeetingManager.run`. Both halves are
probed in the table below (rows 6, 6b, 6c, 6d, 12, 12b).

**3. The other row kinds, checked against the same rule and REPORTED.** Nothing
is changed here; this is the finding.

* **Contradiction rows reveal nothing beyond the `<contradictions>` block.** A
  row carries the detector's OWN sentence — `flag.description`, the identical
  string `vote_ballot.j2:208` / `:214` print above for every participant — plus
  the subject (printed there too, as `subjects:`), a turn id resolved from the
  flag's two event ids, and that turn's speaker. Every one of those is public:
  the flag list, the transcript and its bracketed turn ids (`:163`) are
  rendered to all participants already, and `_turn_id_for_event` matches an id
  the meeting layer itself minted rather than parsing prose. `first_hand` is
  hard-coded `False` on the kind, so the new provenance is not consulted for it
  at all. The only thing a contradiction row adds to what the page already
  showed is a per-target GROUPING of flags the page shows ungrouped — a layout
  of public bytes. What a flag's BANDING rests on (a speaker's own record
  grounding a spoken sighting) is decided in `meetings/transcript` and reaches
  the page as the flag's own sentence, exactly as it did before this card; that
  channel is pre-existing, out of this card's scope, and the same bytes for
  everyone rather than a private per-voter verdict.
* **Own-channel rows reveal no other player's private record.**
  `_own_channel_evidence_rows` reads `voter.*` and nothing else — the four
  channels the engine witness-gated into THIS agent's packet — and the §4.7
  teammate drop runs on top. No other participant is reachable from the
  function at all (`build_evidence_rows` takes one `voter`), which
  `test_only_this_voters_own_channels_reach_its_rows` and
  `test_a_row_built_from_another_participants_channel_is_caught` already pin. A
  body-discovery row names the dead victim, which is public the moment the body
  is reported.

**4. Three production constructs survived neutering with the suite green.** All
three of the finding's probes reproduced here, and each is now enforced by one
test that fails on exactly that perturbation and on no other. Each is
re-measured below as a row that goes GREEN when its new pin alone is
deselected:

* `orchestrator/game.py::move_witness_records_for_meeting`'s
  `observation_id=event.observation_id` (`:4044`) — set to `None`, the whole
  suite stayed green, so every `own_transit` evidence row could have shipped
  reading "nothing here you could cite". Pinned by
  `tests/orchestrator/test_meeting_integration.py::TestMoveWitnessRecordsAccessor`
  (2 tests), in the shape the sighting and vent channels already use: the stamp
  equals the episodic id read back off the log, and a row appended without
  perception carries `None`;
* the `subjects_of_interest` guard in `_contradiction_evidence_rows` —
  `test_a_flag_about_a_player_nobody_may_vote_for_builds_no_row`, over a
  transcript carrying no accusation at all, so the testimony guard beside it
  cannot make this test red;
* the same guard in `_testimony_evidence_rows` —
  `test_a_voice_against_a_player_nobody_may_vote_for_builds_no_row`, over a
  transcript carrying no flag, for the mirror reason. Each test carries a
  control row about a player who IS a target, so an empty result cannot be a
  fact about the fixture.

**5. The served block described its own row order wrongly, and the second
author fixed it.** The header read "grouped by the player they concern, what
you perceived yourself before anything you are repeating". That names the wrong
subject: `_sort_key`'s second term is `row.first_hand`, which a TESTIMONY row
carries whenever its speaker described a sighting, so a describing voice sorts
above a contradiction about the same player and the voter's own lines do not
always come first. The sentence now reads "lines whose speaker describes a
perception of their own before lines whose speaker does not … and a described
sighting sorts there whether or not it happened", which is what the key does
and which also says the sort ranks no claim's truth. Pinned inside
`test_the_block_tells_the_voter_nothing_was_checked` (both the new clause and
the absence of the old one) and probed as row R3-8.

**The round-3 perturbation pass, over the WHOLE production diff.** Re-run from
scratch by the second author over `git diff 0a1100ea HEAD -- ':!tests'
':!tasks' ':!docs'` plus this round's uncommitted changes — every added or
changed executable line, tuple row, dict row, call-site argument, schema field
and template branch. **70 rows**, which is the size the table actually has (the
first draft of this subsection said 72 and listed 69; the count is measured
here, not asserted). Each edits ONE thing, runs the named probe, and restores
every file it touched from an in-memory COPY (never `git checkout`), with
`PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`; `git status` is clean
after the pass. `W` = `tests/meetings/test_weighing_channel.py` (88 tests at
this head).

| # | perturbation | probe | result |
| --- | --- | --- | --- |
| 1 | own sighting row's `citation_id` → `None` | W | red (2 failed, 86 passed) |
| 2 | own vent row's `first_hand` → `False` | W | red (1 failed, 87 passed) |
| 3 | body-discovery rows dropped | W | red (3 failed, 85 passed) |
| 4 | own transit rows dropped | W | red (3 failed, 85 passed) |
| 5 | contradiction → turn resolution neutered | W | red (3 failed, 85 passed) |
| 6 | testimony `first_hand` ignores what the speaker described | W | red (6 failed, 82 passed) |
| 6b | the `saw_player` `co_present` companions drop out of the stated set | W | red (1 failed, 87 passed) |
| 6c | the vent / kill / move shapes drop out of the stated set | W | red (1 failed, 87 passed) |
| 6d | `_stated_sighting_subjects` walks no turn | W | red (6 failed, 82 passed) |
| 7 | the (speaker, subject) dedupe removed | W | red (1 failed, 87 passed) |
| 8 | the described-perception rank removed from the sort key | W | red (3 failed, 85 passed) |
| 9 | subject grouping removed from the sort key | W | red (1 failed, 87 passed) |
| 10 | the per-(subject, class) budget disabled | W | red (2 failed, 86 passed) |
| 10b | the budget drops by RENDER position, not arrival time | W | red (1 failed, 87 passed) |
| 11 | `evidence_rows` not threaded into the render | W | red (10 failed, 78 passed) |
| 11b | the loader drops the `evidence_rows` pass-through | W | red (11 failed, 77 passed) |
| 12 | the ledger built UNCONDITIONALLY again (the reviewed head's gating) | W, `test_corroboration.py`, `test_prompt_byte_golden.py` | red (7 failed, 217 passed) |
| 12b | the assembler imports the corroboration ledger again | W | red (1 failed, 87 passed) |
| 13 | the counter validator removed from the chain | W | red (3 failed, 85 passed) |
| 14 | the counter's observation-id branch removed | W | red (1 failed, 87 passed) |
| 15 | the counter marker payload left unbounded | W | red (1 failed, 87 passed) |
| 16 | the shared turn-suffix recovery neutered | `test_manager.py` | red (1 failed, 268 passed) |
| 17 | `counter_reason_id` not elided from the recorded bytes | W | red (1 failed, 87 passed) |
| 18 | sighting accessor drops the episodic stamp | `test_sighting_accessor.py` | red (5 failed, 3 passed) |
| 19 | vent accessor drops the episodic stamp | `test_meeting_integration.py` | red (2 failed, 45 passed) |
| 19b | move accessor drops the episodic stamp | `test_meeting_integration.py` | red (1 failed, 46 passed) |
| 20 | `vote_ballot` rolled back to v7 | `test_bespoke_prompt_sets.py` | red (4 failed, 99 passed) |
| 20b | the recording preflight pin rolled back to v7 | `test_record_ml_corpus.py` | red (19 failed, 90 passed) |
| 21 | the meeting-quality row pattern re-requires `, trust <N>` | `test_elicitation_fixtures.py`, `test_meeting_quality.py` | red (1 failed, 49 passed) |
| 21b | the validity row pattern re-narrowed (the railroad gate goes vacuous) | `test_validity.py` | red (1 failed, 57 passed) |
| 22 | `BallotView` stops mirroring the counter | `test_view_model.py` | red (21 failed, 30 passed) |
| 22b | the replay loader stops passing the counter through | `test_view_model.py` | red (1 failed, 49 passed) |
| 23 | the counter marker leaves the replay-loader table | `test_view_model.py`, W | red (2 failed, 136 passed) |
| 24 | the counter marker leaves the surrogate table | `test_surrogate_dataset.py`, W | red (2 failed, 126 passed) |
| 25 | the counter marker leaves the deduction chain | W | red (2 failed, 86 passed) |
| 26 | the deference sentence restored in the served body | W | red (2 failed, 86 passed) |
| 27 | the trust column restored on the served row | W | red (1 failed, 87 passed) |
| 28 | the evidence block never renders | W | red (11 failed, 77 passed) |
| 29 | the ninth contract key dropped from the skeleton | W | red (1 failed, 87 passed) |
| 30 | the row's citation clause dropped | W | red (8 failed, 80 passed) |
| 31 | the belief render's trust branch restored | `test_memory_rendering.py`, `test_beliefs_hard_evidence_gate.py` | red (3 failed, 165 passed) |
| 31b | `BeliefState.adjust_trust` put back | `test_memory.py` | red (1 failed, 28 passed) |
| R2 | the own-VENT teammate drop removed | W | red (3 failed, 85 passed) |
| R3 | the own-SIGHTING teammate drop removed | W | red (3 failed, 85 passed) |
| R4 | the `co_present` teammate strip removed | W | red (2 failed, 86 passed) |
| R5 | the own-TRANSIT teammate drop removed | W | red (3 failed, 85 passed) |
| R6 | `teammates` read as an empty set | W | red (3 failed, 85 passed) |
| R7 | the contradiction's per-subject preference removed | W | red (1 failed, 87 passed) |
| R8 | only `event_a_id` resolved | W | red (1 failed, 87 passed) |
| R9 | the contradiction fallback returns `None` | W | red (2 failed, 86 passed) |
| R10 | the PARTIAL-summary sentence restored to a running summary | W | red (1 failed, 87 passed) |
| R2-5 | `or subject == turn.speaker` deleted | W, `test_corroboration.py` | red (1 failed, 198 passed) |
| R2-6 | `_EVIDENCE_KIND_CLASS` `contradiction`/`testimony` values exchanged | W | red (1 failed, 87 passed) |
| R3-1 | the clause tests `first_hand` before the own-channel kind (the round-2 body) | W | red (1 failed, 87 passed) |
| R3-2 | the own-channel test replaced by an unconditional own-perception leaf | W | red (2 failed, 86 passed) |
| R3-3 | another speaker's described sighting rendered as a finding | W | red (2 failed, 86 passed) |
| R3-4 | the "described nothing" testimony leaf collapsed into the flag wording | W | red (2 failed, 86 passed) |
| R3-5 | the block header drops the unchecked sentence | W | red (1 failed, 87 passed) |
| R3-6 | the `subjects_of_interest` guard in `_contradiction_evidence_rows` deleted | W | red (1 failed, 87 passed) |
| R3-7 | the `subjects_of_interest` guard in `_testimony_evidence_rows` deleted | W | red (1 failed, 87 passed) |
| R3-8 | the header's order sentence restored to "what you perceived yourself" | W | red (1 failed, 87 passed) |
| S1 | `VentWitnessRecord` loses `observation_id` | W, `test_meeting_integration.py` | red (28 failed, 107 passed) |
| S2 | `SightingRecord` loses `observation_id` | W, `test_sighting_accessor.py` | red (41 failed, 55 passed) |
| S3 | `MoveWitnessRecord` loses `observation_id` | W, `test_meeting_integration.py` | red (35 failed, 100 passed) |
| S4 | `ModelAuthoredVoteBallot` loses `counter_reason_id` | W | red (23 failed, 65 passed) |
| S5 | `EvidenceRowKind` loses the `own_transit` member | `mypy .` | red (2 errors in 1 file) |
| F1 | `counterKind` always answers `statement` | `npm test` | red (1 failed, 557 passed) |
| F2 | the third `EvidenceLink` removed from the ballot card | `npm test` | red (1 failed, 557 passed) |
| F3 | the counter chip label re-worded as a correction | `npm test` | red (1 failed, 557 passed) |
| F4 | the served TS type drops the counter field | `npm run tsc:check` | red (`counter_reason_id` does not exist in type `BallotView`) |

**Every one of the 70 rows was red on the first attempt at this head — no probe
in this pass first returned green.** That is a statement about the head, not
about the code's history, so the five rows that are red ONLY because of a test
THIS round adds are named plainly and each is measured: the pin is deselected
(for `F3`, whose pin is a frontend test, the reviewed head's own test file is
used instead) and the same perturbation is re-run.

| row | the unenforced line | with its pin deselected |
| --- | --- | --- |
| 6b | the `co_present` companions in `_stated_sighting_subjects` | GREEN (87 passed, 1 deselected) |
| 19b | `move_witness_records_for_meeting`'s episodic stamp | GREEN (45 passed, 2 deselected, 3 xfailed) |
| R3-6 | the `subjects_of_interest` guard on the contradiction builder | GREEN (87 passed, 1 deselected) |
| R3-7 | the same guard on the testimony builder | GREEN (87 passed, 1 deselected) |
| F3 | the counter chip's WORDING | GREEN at `0ba95723` (557 passed) |

6b would have let a voice that placed its target only as a COMPANION read as a
bare name. 19b would have let every `own_transit` row ship reading "nothing
here you could cite". R3-6 and R3-7 are the two guards that keep a flag or a
voice about a player nobody may vote for from building a row at all. F3's
label was asserted everywhere through the `BALLOT_COPY.counterLabel` constant,
so the copy could be re-worded "Citation removed" — a guard's verdict on the
ballot, which is the one thing that slot is not — with nothing failing; it is
pinned as a PROPERTY rather than a literal, so the copy stays editable.

Two production files in the diff carry no executable change at this head and so
carry no row: `meetings/corroboration.py` (docstrings only — finding 1's fourth
restated sentence) and the comment-only hunks of `orchestrator/game.py`'s four
lever-arm spreads, `api/replay_loader.py`'s `_TARGET_REWRITE_LABELS` note and
`training/surrogate/dataset.py:189`. `DESIGN.md` and `docs/adr/0001-…` are
prose. The two frontend story fixtures carry only the new required field and
are covered by row F4, whose typecheck fails on them the moment the field
leaves the type.

**The four sentences that claimed an OFF meeting's prompt bytes were unchanged,
restated at exactly the strength the code delivers.** Finding 1's gating makes
the claim true by construction — the ledger is not BUILT on the default path,
so nothing can be threaded — and none of the four now rests on the prompt-byte
golden, which replays the committed v5 archives over all 300 committed games
and renders no v8 body at all:

1. `meetings/manager.py:1612-1623` — was "Built UNCONDITIONALLY since ruling D5
   … the LEVER still decides whether the `<testimony_sources>` BLOCK renders …
   so an OFF meeting's prompt bytes are unchanged by this line." Now: built
   ONLY while the lever is ON, which is the gate
   `corroboration_discipline_enabled` documents; engine truth about whose
   account was borne out reaches the ballot through the lever's block or not at
   all; the DEFAULT path threads no ledger, so an OFF meeting renders exactly
   the bytes it rendered before the lever existed.
2. this card's **Decisions** — the paragraph is kept as filed and carries a
   dated `[REVERSED, round 3, 2026-09-21]` note saying the reasoning was the
   defect, plus a dated `[RESTATED …]` note giving `first_hand`'s real meaning.
3. the **PR body** — its Summary and Decisions are rewritten for the as-stated
   provenance and its Verification paragraph is re-measured at this head.
4. `meetings/corroboration.py:103-109` — was "so the manager threads no ledger
   and every rendered byte matches the committed registry", which round 1 had
   made false. Now: "the manager BUILDS no ledger, threads none, and every
   rendered byte matches the committed registry. Nothing else reaches this
   module from the ballot path." The module docstring's "'first-hand' means
   here exactly what it means everywhere else in the meeting layer" (`:17`) is
   corrected in the same move: it means that HERE, inside this lever's block,
   and the default ballot means something weaker by the same words.

**The `docs/artifacts.md` row, and the two card sentences that denied it.**
Record impact and the ticked version-cascade acceptance item both said this card
moved no `tests/fixtures/` byte and touched no `docs/artifacts.md` row. Both
were false at the first pass, and deviation 1 above already recorded why:
`tests/fixtures/memory_rendering/crewmate_basic.expected.md` lost its
`- p-1: trust 0.70` line when the belief render's trust branch went. Each now
carries a dated `[CORRECTED …]` note in place. The row is re-verified against
disk at THIS head:

```
$ git ls-files tests/fixtures | wc -l                          35
$ git ls-files tests/fixtures | xargs wc -c | tail -1     2196250 total
$ sed -n 101p docs/artifacts.md   …| 2,196,250 tracked bytes / 35 files |
```

`audits/` is unchanged, in this round and in every earlier one, so no second
inventory row is owed.

**Every changed test expectation.** No test was weakened, skipped or deleted.

* `test_the_invariant_holds_over_committed_meeting_transcripts`,
  `test_the_three_provenance_classes_rank_in_the_stated_order` and
  `test_the_budget_drops_by_arrival_time_not_by_render_position` drop their
  `testimony_ledger=build_testimony_ledger(...)` argument. The first two needed
  nothing else: the speaker in each already spoke the sighting, so the same row
  is first-hand under the new definition. The third's docstring is reworded
  from "grounded" to "described a sighting";
* `test_a_grounded_voice_is_marked_first_hand_on_the_default_path` is REPLACED
  by `test_a_described_sighting_marks_the_row_true_or_fabricated`, which drives
  a real meeting in which `p-2` (holding the matching record) and `p-4`
  (holding nothing) speak the SAME sighting and accuse the same player, and
  asserts both rows read `first_hand=True`. The old test asserted the defect;
  the new one asserts its opposite;
* `test_a_grounded_voice_sorts_above_an_ungrounded_one` →
  `test_a_describing_voice_sorts_above_a_silent_one`: same two rows, same
  expected order, the ledger argument gone;
* `test_a_grounded_voice_names_the_speaker_who_saw_it` →
  `test_a_describing_voice_is_quoted_as_saying_so`, expecting `p-3 says they
  saw it themselves` and additionally asserting the rendered body contains none
  of "confirm", "bears out", "borne out", "verified", "grounded";
* `test_another_voice_at_this_table_names_that_speaker` →
  `test_another_voice_that_described_nothing_is_marked_that_way`, expecting
  `p-3 named them without describing a sighting of their own`; the old
  expectation moves to the new
  `test_a_flag_somebody_else_spoke_into_is_a_statement_here`, which is where it
  is still true;
* `test_what_the_voter_merely_said_here_is_not_rendered_as_perception` now
  loops over BOTH `first_hand` values as well as both kinds — a strengthening,
  since the reviewed head passed it only for `first_hand=False`;
* `test_a_testimony_row_cites_the_accusing_turn`'s trailing comment is reworded
  ("nobody here spoke a sighting their own record bears out" → "nobody here
  described seeing anyone"); its assertions are unchanged;
* `test_the_block_tells_the_voter_nothing_was_checked` gains finding 5's two
  assertions (the new order sentence present, the old one absent). No other
  assertion in it moved.

Added: `TestProvenanceReadsOnlyThePublicTranscript` (16 collected tests),
`TestTheAssemblerCannotReachTheLedger` (11), the two `subjects_of_interest`
probes, `test_the_block_tells_the_voter_nothing_was_checked`,
`TestMoveWitnessRecordsAccessor` (2) and one frontend copy property. The suite
moves 8227 → **8260** passed, and the frontend 557 → **558**.

**The closing greps, run at this head** over the live packages (`agents api
engine eval experiments llm meetings observation orchestrator scripts training
tests docs frontend/src DESIGN.md AGENTS.md README.md tasks/work
tasks/README.md`, source extensions only), excluding `audits/`, `replays/`,
`agent_prompts/` and the dated `tasks/phase-*` history.

```
$ grep -rniE "saw (it|them|that) (them)?sel(f|ves)"
  vote_ballot.j2:230   the default-OFF <testimony_sources> LEVER block, untouched
  vote_ballot.j2:259   the new header sentence ("Where a line says someone saw
                       it themselves, that is what THEY said here")
  vote_ballot.j2:261   the third leaf of the provenance clause
  test_weighing_channel.py:1429,1842   the two leaf assertions
  tests/fixtures/prompt_archive/qwen3_6_27b_v5/vote_ballot.j2:198  the archived
                       v5 body the golden replays (history)
$ grep -rniE "first.hand" | grep -iE "testimony|ledger|bears? out|borne out|grounded"
  meetings/corroboration.py:350        the LEVER's own definition, now scoped
                                       by the module docstring at :17
  meetings/manager.py:1329,4774        the grounded-prosecution / vouch seams,
                                       unrelated to the ballot's rows
  scripts/counterfactual_phase21.py:803,2117   the lever's own probe
  agents/**, tests/agents/**           reported-testimony salience, unrelated
  docs/architecture.md:163             "attributed testimony … does not become
                                       first-hand proof" -- still true
  (no live-tense sentence ties an evidence ROW's first_hand to a record)
$ grep -rniE "unconditional" | grep -iE "ledger|testimony|evidence.row|first.hand"
  beliefs.py:792,1002 and five test comments -- all the Task-14.9
  reported-testimony reduction; none is the ledger
$ grep -rniE "trust them over"
  vote_ballot.j2:127                   the header quoting the DELETED sentence
  experiments/lab/qwen36_prompt_scratch/v3,v4,v5   frozen scratch rungs
  tests/fixtures/prompt_archive/…/vote_ballot.j2   the archived v5 body
  test_weighing_channel.py:76,1960,1983            the forbidden constant and
                                                   its two assertions
$ grep -rniE "adjust_trust"
  beliefs.py:10,969 / store.py:2811,2816 / DESIGN.md:718 /
  docs/adr/0001-…:31                   the deletion's own history notes
  five test comments, all past tense, plus the hasattr assertion
$ grep -rniE "credib"
  beliefs.py:973,975 / docs/adr/0001-…:36,38   the "not wired" reasoning
  eval/deduction_metrics.py:75                 unrelated (flag symmetry)
  six impostor-prompt "credible opening" lines -- unrelated
$ grep -rniE "deferen"
  orchestrator/game.py:435, test_bespoke_prompt_sets.py:534,
  test_weighing_channel.py:11,74,1955,1969,1980   all naming the DELETION
$ grep -rniE "running summar"
  test_weighing_channel.py:81,2020     the FORBIDDEN string constant and the
                                       test that asserts its absence
```

**Gates re-measured at THIS round's head** — the CURRENT table — each exit code
captured directly, never through a pipe or a compound command. The card's own
Validation list is covered in full; no live provider call of any kind was made
and none is a check.

```
$ bash scripts/check.sh                                   EXIT=0
  ruff check . / ruff format --check .  518 files, all clean
  lint-imports                          4 contracts kept, 0 broken, 189 files,
                                        1034 dependencies
  validate_task_docs.py                 390 phase tasks + 390 prompts; 73 work
                                        cards (this card's Status does not move)
  generate_prompts.py --check           all 390 prompts in sync
  mypy .                                no issues in 489 source files
  pytest -n auto --dist loadfile        8260 passed, 20 skipped, 3 xfailed
                                        (8227 in round 2: +33 new tests)
  frontend lint / tsc:check / vitest    558 tests in 20 files passed; build green
$ uv run pytest tests/meetings tests/agents tests/orchestrator tests/eval tests/api -q
                                                          EXIT=0
  5029 passed, 3 skipped, 3 xfailed
$ uv run pytest tests/meetings/test_prompt_byte_golden.py -q               EXIT=0
  25 passed
$ npm --prefix frontend test                              EXIT=0
  20 test files, 558 tests passed
$ bash scripts/verify_samples.sh                          EXIT=0
  replays/samples/4p1i  All 50 samples verified clean.
  replays/samples/9p2i  All 50 samples verified clean.
$ uv run python scripts/build_sample_report.py --sample-dir <set> --check
  replays/samples/4p1i     consistent with its replays.      EXIT=0
  replays/samples/9p2i     consistent with its replays.      EXIT=0
  replays/ml_corpus/4p1i   consistent with its replays.      EXIT=0
  replays/ml_corpus/9p2i   consistent with its replays.      EXIT=0
$ uv run python scripts/publish_process_scorecard.py --check              EXIT=0
  docs/process-scorecard.md and .json consistent with the committed recordings
$ uv run python scripts/check_doc_facts.py                                EXIT=0
$ uv run python scripts/validate_task_docs.py                             EXIT=0
  390 phase tasks + 390 prompts; 73 work cards
$ uv run python scripts/generate_prompts.py --check                       EXIT=0
  All 390 prompts are in sync.
$ uv run python scripts/verify_ml_evidence.py                             EXIT=0
  checks: 61 | OK 49 | FAIL 0 | ABSENT 7 | INFO 5   (never --complete)
```

Nothing moved that may not move: no recording, no sample report, no scorecard
figure, no prompt archive entry, and no fixture byte beyond the one deviation 1
already declared. The four `--check` recomputations and the scorecard are
byte-identical again, which is the point — this round touched no recorded byte,
and every number above is either a committed-bytes recomputation or a test
count. What the corrected v8 body does to a real voter stays unknown until
[the re-record](process-rerecord.md), by design.

### Review corrections, round 4 (2026-09-21)

Two blocking findings — one correctness, one record integrity — plus seven
smaller items and the two live Codex comments, which had no judgement anywhere.
Round 4's two verifiers first re-established the round-3 gate on their own
generated families: 0 byte differences in the full rendered v8 prompt across
twins differing only in other players' private records or roles, every gate
figure reproduced, and 15 neuter rows re-run to the digit. Every `file:line`
below is re-derived mechanically at THIS round's head, after this round's last
edit. Rounds 1 to 3 above are unchanged, byte for byte: the text from
`### Review corrections, round 1` up to this heading hashes to SHA-256
`5cc2dd053834005e9c8808d30b93e83bd3bedac0fcda08d168663fa229030ae8`, its value at
`d7b6be94`. Round 3's gate block calls itself "the CURRENT table"; round 4's
below is, and round 3's stands as recorded.

**1. Two union members in `_stated_sighting_subjects` were unenforced.** At
`d7b6be94` the shape test read

```python
elif isinstance(observation, SawVentObservation | SawKillObservation | SawMoveObservation):
```

and dropping `SawKillObservation` ALONE, or `SawMoveObservation` ALONE, left the
whole suite green — 5029 passed over the five test directories in either case.
Round 3's row 6c neutered all three members at once and its single failure was
the vent case, which masked the other two: a table row that perturbs a UNION is
ONE probe for N branches, and it reports the strongest member's pin as if it
covered the rest.

The two shapes are live behaviour, not dead union members. The turn schema
accepts both unconditionally (`meetings/schemas.py`'s `SawKillObservation` and
`SawMoveObservation` docstrings: "parsing never depends on which templates offer
it"), so a speaker can emit one whatever a template says. And the served
`qwen3_6_27b` set does offer them: `saw_move` on the DEFAULT path and ungated
(`crewmate_report.j2:147`, `accusation_round.j2:281`, `_account_rules.j2:28`),
`saw_kill` inside a lever arm (`crewmate_report.j2:152` under
`testimony_shapes`, `accusation_round.j2:286` under the same and not-impostor,
`_account_rules.j2:33` under `public_account_version`; `meetings/manager.py:5057`
is the disjunction that turns the shape on). A speaker whose testimony row said
"named them without describing a sighting of their own" after describing a
witnessed KILL would be understated by the page, which is the one thing the row
is for.

No production behaviour changes.
`test_a_described_sighting_marks_the_row_true_or_fabricated` was one example
over `saw_player`; it is now parametrised over ALL FOUR shapes
(`_DESCRIBED_SHAPES`, `tests/meetings/test_weighing_channel.py:384`), keeping
the two-speaker pair in each case — `p-2` holds the private channel that bears
that shape out, `p-4` holds nothing and speaks the identical words — and
asserting `first_hand is True` for BOTH speakers. `saw_kill` carries no typed
grounding channel of its own (none exists for kills), so its borne-out leg holds
the nearest private perception the engine does record, a sighting of that player
in that room at that tick; the A/B pair stays a real private difference rather
than two empty channels. `W` below is
`tests/meetings/test_weighing_channel.py`, **92 tests** at this head (88 at
`d7b6be94`: +3 parametrised cases, +1 for the prompt gap in finding 3).

Row 6c is split into one row per union member. Each edits ONE thing, runs the
probe, and restores `meetings/manager.py` from an in-memory COPY (never `git
checkout`), with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`; `git
status` is clean after the pass. The last column re-runs the same perturbation
with THIS round's three new cases deselected, which is round 3's own idiom for
separating "red because the pin is new" from "red because it was already
pinned":

| # | perturbation | probe | result | with round 4's cases deselected |
| --- | --- | --- | --- | --- |
| 6c-a | `SawPlayerObservation` drops out of the stated set | W | red (5 failed, 86 passed) | red (5 failed, 83 passed, 3 deselected) |
| 6c-b | `SawVentObservation` drops out of the stated set | W | red (2 failed, 89 passed) | red (1 failed, 87 passed, 3 deselected) |
| 6c-c | `SawKillObservation` drops out of the stated set | W | red (1 failed, 90 passed) | **GREEN (88 passed, 3 deselected)** |
| 6c-d | `SawMoveObservation` drops out of the stated set | W | red (1 failed, 90 passed) | **GREEN (88 passed, 3 deselected)** |
| 6b | the `saw_player` `co_present` companions drop out | W | red (1 failed, 90 passed) | red (1 failed, 87 passed, 3 deselected) |

The finding's three controls reproduce to the digit in the deselected column:
`SawPlayerObservation` removed **5 failed / 83**, `SawVentObservation` removed
**1 failed / 87**, `co_present` dropped **1 failed / 87**. 6c-c and 6c-d are the
two that were unenforced, and they are the only two whose deselected column is
GREEN — which is the statement the split exists to make. Round 3's row 6c is
superseded by these five; it is left as filed there, as every earlier round's
table is.

**2. The Results symbol table and three prose citations were stale at
`d7b6be94`.** The table said every line was "RE-STAMPED at this card's final
head (review round 1)", and that stopped being true when round 3 moved
`meetings/manager.py` (-6/+32/+38), `meetings/render_contract.py` (+8) and
`vote_ballot.j2` (+5) underneath it. Fourteen cells and three prose citations
pointed at the wrong lines. A card that says "re-derived by symbol, not carried
forward" and then carries a value forward is worse than one that gives no line
at all, because the next reader trusts it.

Every citation in the CURRENT sections is re-derived MECHANICALLY at this head
and AFTER this round's last edit — `ast` for every definition and constant,
`grep -n` for every line — with each prior value kept in parentheses. The table
above is the re-stamped one, and its preamble now names the round that stamped
it and the files each round moved. The prose citations outside it:

| where | said | at this head |
| --- | --- | --- |
| Decisions, the per-group bound | `MAX_EVIDENCE_ROWS_PER_SUBJECT = 8` (`manager.py:3413`) | `manager.py:3407` |
| Decisions, the counter's exclusion | the `cited_before_validation` read (`manager.py:2456`) | `manager.py:2450` |
| Acceptance, the round-2 item | `render_contract.py:461-473` | `render_contract.py:467-481` |
| the symbol table, the validity pattern | `eval/validity.py:190` | `eval/validity.py:189` — the regex is DEFINED at `:189`, and that cell was off by one from the start |

Round 4 moves two of the same files — this round's `_stated_sighting_subjects`
docstring is +7 in `meetings/manager.py` and the SKIP-counter sentence is +4 in
`vote_ballot.j2` — which is exactly why the derivation is the LAST thing run
before the card is committed.

**3. The two live Codex comments, judged.** Both were open with no judgement in
the card or the PR. No PR comment is posted; the judgement lives here and in the
PR body.

* **4062448106, "Separate a null counter from a none-held decision basis"**
  (`vote_ballot.j2:313` as reviewed, `:316` here). Dated 2026-09-21: **the
  first half is NOT a defect; the second half is a genuine prompt gap, and it
  is fixed.** The bullet does not conflate the two facts. The next bullet
  defines `decision_basis` independently and on its own terms ("replace that
  null with `cited` when either reason id is filled, and with exactly
  `none_held` when both are null"); the two fields are validated independently —
  a fabricated counter costs exactly `counter_reason_id` plus its own marker and
  is deliberately outside the `cited_before_validation` read, so it cannot turn
  an `uncited` ballot into an `invalid_citation` one (Decisions, above) — and
  they are recorded independently. Re-using `none_held`'s wording rather than
  minting a third vocabulary is a decision this card already records, with the
  measured cost of a third vocabulary beside it: 27 of 150 ballots nulled on a
  row suffix, from [the accounts v5 card](accounts-prompt-set-v5.md). What the
  comment is right about is its last clause. The bullet said "pointing AWAY from
  the name you just wrote", and a SKIP writes no name — and SKIP is the MAJORITY
  ballot, so the gap is not a corner case. One prose sentence in the same bullet
  closes it:

  > When you wrote SKIP, that is the strongest thing you hold pointing TOWARD
  > ejecting someone — the line that most nearly made you name a name.

  It adds no vocabulary and asks for no new literal: the skeleton still prefills
  `"counter_reason_id": null`, the same two id shapes are still what it takes,
  and the only quoted words in the bullet remain `counter_reason_id`,
  `decision_basis` and `none_held`. It is a v8 body edit and `vote_ballot` STAYS
  v8 — nothing has ever been recorded under v8, so no stamp covers two bodies.
  Pinned by `test_the_counter_bullet_says_what_points_away_from_a_skip` in the
  served-body idiom: render the real body, assert the sentence is in the
  counter bullet, assert the skeleton's null, and assert the bullet's
  quoted-literal SET is exactly those three words, so adding a fourth fails.
* **4062448113, "Replace historical comment blocks with current intent"**
  (`agents/memory/beliefs.py:973`). Dated 2026-09-21: **not accepted; the
  premise is false.** It reads AGENTS.md craft rule 1 ("Comments explain current
  intent. Provenance is at most one trailing line.") as a size limit on a
  deliberate history block. The repository's own practice at this card's BASE
  `0a1100ea` says otherwise — READ-ONLY HISTORY blocks recording a retired
  mechanism, at `meetings/manager.py:304-332` (29 lines), `:389-407` (19) and
  `:412-421` (10), `api/replay_loader.py:3596-3604` (9),
  `training/surrogate/dataset.py:196-199` (4), and an 11-line HISTORY paragraph
  in `eval/meeting_quality.py`'s module docstring at `:115`. Every one exists
  for the reason this one does: committed bytes still carry the retired thing,
  and a reader of those bytes needs to know what it meant. Craft rule 1's
  "provenance" is the attribution line — which task, which PR — not the record
  of a deletion; craft rule 3's "one history line" is scoped to GRADUATED
  LEVERS, and trust was never a lever, which this card's Record impact says in
  those words. The blocks stay at the size they are. What WAS wrong is the
  card's own description of them, which finding 4 corrects.

**4. The trust field's survival, restated at DELIVERED strength.** Acceptance
and Decisions both said the reason is recorded by "one history line" in each of
three documents. Measured at this head, what shipped is a 15-line comment block
(`agents/memory/beliefs.py:969-983`), a 12-line paragraph inside
`_format_belief_score` (`agents/memory/store.py:2808-2819`) and a 14-line ADR
bullet (`docs/adr/0001-three-load-bearing-decisions.md:30-43`). Both sentences
now carry a dated `[RESTATED AT DELIVERED STRENGTH …]` note. The blocks are NOT
shrunk (finding 3's second judgement); only the card's description of them
moves, which is the direction this project's rule runs in — a guarantee is
stated at exactly the strength the code delivers, and that cuts both ways.

**5. `_stated_sighting_subjects`' docstring gave a FALSE reason for excluding
`FoundBodyObservation`.** It said the shape "names a DEAD victim, who is never
among the living ejection targets a testimony row may be about" — which would
make a branch for it unreachable, a line no probe could hit. It is not
unreachable. `body_of` is only ROSTER-validated
(`meetings.public_accounts.validate_public_accounts`, the
`("subject", "body_of", "against", "supports")` loop at
`meetings/public_accounts.py:52-55`), which is deliberate — that validator
checks references and time bounds, never truth — so a speaker CAN file
`found_body(body_of=<a living candidate>)` and it survives into the transcript,
leaving that row `first_hand=False`. The docstring now gives the TRUE reason: a
body report is not a sighting of a living player, and the shape is deliberately
not read here, so a misfiled one UNDERSTATES the speaker's claim rather than
confirming it — the safe direction for a page that must never price a claim for
the voter. Behaviour is unchanged; no executable line moved.

**6. `TestTheAssemblerCannotReachTheLedger`'s docstring said "call graph".** It
is not one. It is a per-function NAME SCAN over five named functions
(`build_evidence_rows`, `_own_channel_evidence_rows`,
`_contradiction_evidence_rows`, `_testimony_evidence_rows`,
`_stated_sighting_subjects`): it parses `meetings/manager.py`, strips each
docstring, and asserts that no parameter and no name in the body matches
`ledger`, `corroboration`, `testimonysupport` or `first_hand_places`. It
follows no calls, so a neutrally-named helper that itself called
`build_testimony_ledger` would pass it untouched. The docstring now says exactly
that, and names `TestProvenanceReadsOnlyThePublicTranscript` as the half that
DOES catch that case — change only another speaker's private records, and no row
field and no rendered byte may move, however the assembler reached them. The two
are layered on purpose: the scan is cheap and catches the obvious reintroduction
by name, the values catch the rest. The Acceptance item that called it "the
`ast` call-graph guard" carries a dated `[CORRECTED …]` note.

**7. "Deviations from the card, declared" was not the single index it presents
itself as.** Five files outside Expected scope were disclosed elsewhere in this
card but never listed there: `eval/validity.py`, `meetings/corroboration.py`,
`eval/deduction_metrics.py`, `frontend/src/lib/copy.ts` and
[the scorecard card](process-scorecard.md). They are added as deviation 6, each
with where it was already disclosed. Nothing about any of them is new; the index
is now an index.

**The closing greps, re-run VERBATIM at this head and quoted UNCONDENSED.**
Round 3's quotation of these was condensed, and the condensation dropped real
hits and mis-stated one: grep 3 also matches
`experiments/lab/report-ml-spike.md:27`; grep 7 also matches
`tasks/work/grounded-skip-and-guard-labels.md:377` and three more lines of
`tests/meetings/test_weighing_channel.py` than it listed; and grep 6's "six
impostor-prompt lines" is in fact FIFTEEN prompt lines across nine files in six
sets, four of them accusation-round prose rather than an impostor report. Below
is EVERY hit, classified, with the count per grep; nothing is elided.

Run over the live packages (`agents api engine eval experiments llm meetings
observation orchestrator scripts training tests docs frontend/src DESIGN.md
AGENTS.md README.md tasks/work tasks/README.md`) with `--include` `*.py` `*.j2`
`*.md` `*.ts` `*.tsx` `*.sh`, which excludes `audits/`, `replays/`,
`agent_prompts/` and the dated `tasks/phase-*` history. THIS CARD is excluded
from the paths as well, and that exclusion is stated rather than silent (round 3
made it without saying so): the card quotes every one of these strings by
construction, so any count of its own hits is falsified by the sentence that
states it. Every hit in every OTHER file is below.

```
$ grep -rniE "saw (it|them|that) (them)?sel(f|ves)"                     6 hits
  vote_ballot.j2:234          the default-OFF <testimony_sources> LEVER block,
                              untouched by this card
  vote_ballot.j2:263          the evidence block's header sentence
  vote_ballot.j2:265          the third leaf of the provenance clause
  prompt_archive/qwen3_6_27b_v5/vote_ballot.j2:198   the archived v5 body the
                              golden replays (history)
  test_weighing_channel.py:1502,1920    the two leaf assertions

$ grep -rniE "first.hand" | grep -iE "testimony|ledger|bears? out|borne out|grounded"
                                                                       47 hits
  vote_ballot.j2:238          the LEVER's <testimony_sources> row, untouched
  vote_ballot.j2:265          the evidence row's provenance clause -- the ONE
                              live site, and it says "says they saw it
                              themselves", with no bears-out word anywhere
  _account_rules.j2:14        "Nobody at the table receives a certificate from
                              another player's private memory" -- the rule
  meetings/corroboration.py:350    the LEVER's own definition, scoped by that
                              module's docstring at :17
  meetings/manager.py:1329,4781    the grounded-prosecution and grounded-vouch
                              seams, neither on the ballot's row path
  meetings/transcript.py:2173      the pre-vote testimony spread, unrelated
  agents/memory/store.py:2428, agents/memory/episodic.py:66,
  agents/perception.py:23     "not a first-hand citable observation" -- the
                              episodic-id vocabulary, unrelated
  agents/memory/beliefs.py:410     the Task-14.9 spread, unrelated
  scripts/counterfactual_phase21.py:803,2117        the lever's own probe
  prompt_archive/qwen3_6_27b_v5/vote_ballot.j2:202  archived v5 (history)
  test_weighing_channel.py:948,1292,1315,1425,1430,1529,1918,1960,1978
                              this card's own tests; the three `_ledger_*` lines
                              are the NON-VACUITY check, by design
  test_corroboration.py:356,374,608,788,820,925     the lever's own tests
  test_perception.py:400, test_reported_testimony.py:10,361,362,364,365,392,
  400,1719,1792,1862,1868,1876,1881,1882            reported-testimony
                              salience, unrelated
  docs/architecture.md:163    "Attributed testimony … does not become first-hand
                              proof" -- still true
  evidence-renderer-salience.md:1491, alibi-as-route.md:2296
                              other cards' salience prose, unrelated
  (no live-tense sentence ties an evidence ROW's first_hand to a record)

$ grep -rniE "unconditional" | grep -iE "ledger|testimony|evidence.row|first.hand"
                                                                        8 hits
  agents/memory/beliefs.py:792,1002    the Task-14.9 reported-testimony
                              reduction; neither is the ledger
  experiments/lab/report-ml-spike.md:27    a Phase-A lab figure ("detector tally
                              predicts the ejection 56% unconditional") --
                              unrelated, and OMITTED by round 3
  test_episodic_ids.py:12     the `[obs {id}]` prefix, unconditional since 14.9
  test_reported_testimony.py:385,409,683,954   the same 14.9 / baseline-7
                              reduction

$ grep -rniE "trust them over"                                          8 hits
  vote_ballot.j2:127          the header comment quoting the DELETED sentence
  experiments/lab/qwen36_prompt_scratch/v5/vote_ballot.j2:33,
  …/v4/vote_ballot.j2:33, …/v3/vote_ballot.j2:31      frozen scratch rungs
  prompt_archive/qwen3_6_27b_v5/vote_ballot.j2:259    the archived v5 body
  test_weighing_channel.py:77,2038,2061   the forbidden constant and its two
                              assertions

$ grep -rniE "adjust_trust"                                            12 hits
  agents/memory/store.py:2811,2816, agents/memory/beliefs.py:10,969
                              the deletion's own history notes
  docs/adr/0001-…:31, DESIGN.md:718       the two corrected documents
  test_memory.py:203,228,290, test_memory_rendering.py:219,498,
  test_beliefs_hard_evidence_gate.py:369  five past-tense comments plus the
                              `hasattr` assertion that the writer is gone

$ grep -rniE "credib"                                                  24 hits
  agents/memory/beliefs.py:973,975, docs/adr/0001-…:36,38
                              the "not wired" reasoning, in two of the three
                              history blocks
  eval/deduction_metrics.py:75      unrelated (flag symmetry)
  glm_4_32b/impostor_report.j2:36,81, qwen3_5_9b/impostor_report.j2:9,178,190,
  qwen3_6_27b/impostor_report.j2:124, qwen3_6_27b/accusation_round.j2:275,
  qwen3_6_27b/impostor_report_roll_call.j2:115,
  qwen3_6_27b/accusation_round_roll_call.j2:198,
  qwen3_32b/impostor_report.j2:100,108,147,
  qwen3_32b_thinking/impostor_report.j2:69,
  qwen3_30b_a3b/impostor_report.j2:68,71
                              FIFTEEN "credible opening" / "more credible"
                              prompt lines, nine files, six sets -- all
                              unrelated to the deleted scalar, and four are
                              accusation-round prose rather than an impostor
                              report. Round 3 called this "six impostor-prompt
                              lines": the condensation was wrong, not just short
  prompt_archive/qwen3_6_27b_v5/impostor_report.j2:124,
  …/accusation_round.j2:275, …/impostor_report_roll_call.j2:115,
  …/accusation_round_roll_call.j2:198     the archived v5 copies (history)

$ grep -rniE "deferen"                                                 10 hits
  orchestrator/game.py:435, test_bespoke_prompt_sets.py:534
                              the two version-entry comments, both naming the
                              DELETION
  test_weighing_channel.py:11,75,2033,2037,2047,2058,2060
                              the module docstring, the forbidden constant, and
                              the gone / planted pair. Round 3 listed four of
                              these seven
  grounded-skip-and-guard-labels.md:377   the PREVIOUS card's prose about the
                              same deletion, OMITTED by round 3

$ grep -rniE "running summar"                                           2 hits
  test_weighing_channel.py:82,2098   the FORBIDDEN string constant and the test
                              that asserts its absence
```

The `test_weighing_channel.py` line numbers above differ from round 3's because
this round adds four tests and one constant to that file. No assertion moved.

**N5, a residual this round does NOT change.** A contradiction row renders as
`not first-hand: p-3 stated it at this table`, and the sentence beside it is the
DETECTOR's (`flag.description`), not `p-3`'s — the row cites the turn `p-3`
spoke, but the words are the meeting layer's cross-check of two statements. The
clause is accurate about provenance and misleading about authorship. It is left
alone deliberately: the wording is pinned
(`test_a_flag_somebody_else_spoke_into_is_a_statement_here`), changing it would
be a SECOND template edit in a round whose other template edit is already a v8
body change, and the fix belongs with a reader who can see what it does to a
real voter. [The re-record](process-rerecord.md)'s runner brief carries it.

**For the owner, outside this card.** Round 4's correctness verifier measured a
PRE-EXISTING leak while checking this card's no-oracle rule. It is recorded here
so it does not have to be re-found. It is NOT a wave item, and nothing in this
card caused it, widened it or fixes it.

A contradiction flag's `description` carries the weak-reason vocabulary
`WEAK_REASON_UNGROUNDED_SIGHTING` / `WEAK_REASON_LONE_GROUNDED_SOURCE`
(`meetings/transcript.py:726-727`, appended at `:4520` / `:4522`), and which of
those two a flag earns is decided by the SPEAKER's own private record. The flag
list is rendered to every participant by `vote_ballot.j2:212` / `:218` / `:224`.
So the page already tells every voter something about whose account the engine
bears out, through the `<contradictions>` block, which predates this card.
Measured: over **60** generated meetings with the PUBLIC transcript held fixed
and only other participants' private records changed, the flag set or one of its
descriptions moved in **23 of 60**. Identical at this card's base `0a1100ea`.
This card's contradiction evidence row repeats that same description VERBATIM,
and over the committed sets **3032 of 3032** such rows were already rendered in
the same prompt's `<contradictions>` block: **0 new exposure**. Whether a public
detector may price a private record at all is a question about the detector, one
layer below the ballot, and it is the owner's to route.

**Gates re-measured at ROUND 4's head** — the CURRENT table — each exit code
captured directly, never through a pipe or a compound command. The card's own
Validation list is covered in full; no live provider call of any kind was made
and none is a check.

```
$ bash scripts/check.sh                                   EXIT=0
  ruff check . / ruff format --check .  518 files, all clean
  lint-imports                          4 contracts kept, 0 broken, 189 files,
                                        1034 dependencies
  validate_task_docs.py                 390 phase tasks + 390 prompts; 73 work
                                        cards (this card's Status does not move)
  generate_prompts.py --check           all 390 prompts in sync
  mypy .                                no issues in 489 source files
  pytest -n auto --dist loadfile        8264 passed, 20 skipped, 3 xfailed
                                        (8260 in round 3: +4 new tests)
  frontend lint / tsc:check / vitest    558 tests in 20 files passed; build green
$ uv run pytest tests/meetings tests/agents tests/orchestrator tests/eval tests/api -q
                                                          EXIT=0
  5033 passed, 3 skipped, 3 xfailed    (5029 in round 3: the same +4)
$ uv run pytest tests/meetings/test_weighing_channel.py -q                 EXIT=0
  92 passed                            (88 in round 3)
$ uv run pytest tests/meetings/test_prompt_byte_golden.py -q               EXIT=0
  25 passed
$ npm --prefix frontend test                              EXIT=0
  20 test files, 558 tests passed
$ bash scripts/verify_samples.sh                          EXIT=0
  replays/samples/4p1i  All 50 samples verified clean.
  replays/samples/9p2i  All 50 samples verified clean.
$ uv run python scripts/build_sample_report.py --sample-dir <set> --check
  replays/samples/4p1i     consistent with its replays.      EXIT=0
  replays/samples/9p2i     consistent with its replays.      EXIT=0
  replays/ml_corpus/4p1i   consistent with its replays.      EXIT=0
  replays/ml_corpus/9p2i   consistent with its replays.      EXIT=0
$ uv run python scripts/publish_process_scorecard.py --check              EXIT=0
  docs/process-scorecard.md and .json consistent with the committed recordings
$ uv run python scripts/check_doc_facts.py                                EXIT=0
$ uv run python scripts/validate_task_docs.py                             EXIT=0
  390 phase tasks + 390 prompts; 73 work cards
$ uv run python scripts/generate_prompts.py --check                       EXIT=0
  All 390 prompts are in sync.
$ uv run python scripts/verify_ml_evidence.py                             EXIT=0
  checks: 61 | OK 49 | FAIL 0 | ABSENT 7 | INFO 5   (never --complete)
```

Nothing moved that may not move. `git status` names exactly four files at this
round's head — `agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2`,
`meetings/manager.py` (a docstring only), `tests/meetings/test_weighing_channel.py`
and this card. No recording, no sample report, no scorecard figure, no prompt
archive entry, and no fixture byte beyond the one deviation 1 already declared.
The four `--check` recomputations and the scorecard are byte-identical again.
`vote_ballot` stays at **v8**. Every number above is a committed-bytes
recomputation or a test count; what the v8 body does to a real voter stays
unknown until [the re-record](process-rerecord.md), by design.
