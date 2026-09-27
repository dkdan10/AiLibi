# B6: the witnessed-kill ballot row (R8) and the strategic impostor ballot (R10)

**Status:** done

## Outcome

Two default-OFF meeting-layer arms, declared by the spine as `RecordedExperimentConfig` fields of
type `Literal[1] | None`, set only by a declared config file (no env var), and recorded ON only by
the record card into `replays/candidates/stage-b-r1/9p2i/`:

- **`ballot_kill_row_version = 1` (R8).** A voter who watched a non-teammate kill gets one
  first-hand `own_kill` row in its ballot's weighing channel, `you watched them KILL in {room} at
  tick {tick}`, citable by the kill's observation id. Only the witness holds it; a killer's
  teammate never gets one; it is never a public certified flag, a testimony-ledger row or a belief
  input. The suspicion header stops telling the voter that a watched kill moves the number "with
  no line of its own".
- **`impostor_ballot_version = 1` (R10).** An impostor's ballot stops being framed as a belief
  ("name the one player you believe is an impostor"). An impostor believes exactly its teammates
  are impostors and may not vote them, so that framing leaves SKIP as its only consistent answer.
  The ballot becomes a move for its side, bounded by grounding: it may name a crewmate only when it
  cites a line it holds that points toward that crewmate (an accusation at this table, or a
  conflict naming them), never a teammate, and it SKIPs otherwise. **The bound is instructed, not
  enforced**: under ruling D6 the tally reads no grounding label, so an ungrounded impostor EJECT is
  recorded and tallied like any other, and a new evidence-honesty cell counts it.

Both arms are guarded blocks in the one served `vote_ballot.j2`, whose header marker stays
`vote_ballot.qwen3_6_27b.v8`. They are served through the spine's experiment-arm stamp registry as
`vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1` and `vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1`,
joined by `+` when both are ON. There is no registry bump and no prompt archive. As the last arm
card it removes its two names from `WAVE_ARMS_PENDING` and then deletes the emptied guard, its
checks and its refusal test (craft rule 3), so the declared round-1 config validates. With both
arms OFF nothing moves: every committed recording, derived view, fixture, gate and doc fact keeps
verifying byte-identically.

## Evidence

Every `path:line` below is a citation at `e886b663`; earlier cards edit several of these files, so
the implementer re-anchors each by the symbol named with it at dispatch. Every count is count-only,
keyed by (set, meeting), measured at `e886b663`, and **must be re-measured at dispatch**. The design
is the Stage-B decision memo (`stage-b-2026-09-24/decision-memo.md`) sections 0.2, 0.3, 2.5 and the
card-10 brief in 3.4; the investigation is `ballot_kill_row_and_impostor_strategy.md` sections 1-8
beside it. Where the investigation proposed a v9 stamp and an env var, the memo overrules it.

**The owner's rulings of 2026-09-24, verbatim.** "We should implement stage B". Items 6 to 10 and
13: "What do you think is best?" (delegated to the orchestrator). "Tour fix can be deferred to
after gameplay is finished". "Hold off on ML as D suggests until gameplay is finished." On the
record: "Let's not re-record all 300 seeds each time. When it's time to record, record the smaller
group of 50 seeds, assess if the implementations have been effective and resulted in desired
results. Also it is understood that updating the vent and body reset logic will probably have a
substantial effect on previous limits and statistics around the baseline voting results, that is
okay."

**The orchestrator's rulings, under the owner's delegation of 2026-09-24** (memo 0.2 and 3.4):
- R8: "a witnessed kill becomes an OWN-EVIDENCE row in the voter's weighing channel; no public
  certified flag".
- R10: "impostor ballots express STRATEGY bounded by grounding: an impostor may EJECT only a target
  against whom it can cite an evidence row it holds, never a teammate, and SKIPs otherwise; its
  decision_basis and citations stay honest as to the data cited; the wording never pushes toward
  the correct answer." Tightened (memo 2.5 item 3) to: "Name a crewmate only when you can cite a
  line you hold that points toward them: a turn in which someone accused them at this table, or a
  conflict that names them." No confidence clause.
- On enforcement: "Enforcement is by instruction, not by the tally. Under ruling D6 the tally reads
  no grounding label (`meetings/voting.py:238-250`), so "SKIPs otherwise" is instructed and
  counted, never enforced: an ungrounded impostor EJECT is recorded and tallied like any other, and
  the R10 compliance cell counts it."
- Decisions 0.3 items 2 (omit at default), 4 (two fields, derived suffixes, v9 unallocated), 5
  (config-only), 6 (a recorded value's meaning is frozen) and 9 (this card deletes the guard).

**The kill channel exists one layer short of the ballot.** `KillWitnessRecord` is a frozen
dataclass with no `observation_id` (`orchestrator/game.py:3512`); its accessor
`TacticalAgent.kill_witness_records_for_meeting` (`:4074-4134`) already drops a teammate (`:4126`)
and feeds only the conviction assembler (`training/conviction/serving.py:240`, `.subject` only).
`MeetingParticipant` (`meetings/manager.py:757`, own channels `:898-903`) carries no kill channel,
as `build_evidence_rows` (`:3774-3783`), `meetings/render_contract.py:467-474` and
`meetings/corroboration.py:344-352` say, and the served ballot says a watched kill moves the number
"with no line of its own" (`vote_ballot.j2:271`), pinned at
`tests/meetings/test_weighing_channel.py:2087`. Precedents: the vent accessor's
`observation_id=event.observation_id` (`orchestrator/game.py:3884`); `MoveWitnessAgent` (`:961`)
and its use in `_build_participants` (`:1664-1668`); `_own_channel_evidence_rows`
(`meetings/manager.py:3443`); class 0 of `_EVIDENCE_KIND_CLASS` (`:3415-3422`) under the budget of
8 rows per subject (`:3407`).

**The impostor ballot today.** One persona sentence serves both roles (`vote_ballot.j2:150`). The
team block renders only when `fellow_impostor_ids` is non-empty (`:287-291`), so a sole impostor
(4p1i) reads the crew text, and the renderer receives no role (`VotePromptRenderer`,
`meetings/render_contract.py:424`; `vote_ballot_prompt`, `agents/strategic/prompts/loader.py:1026`).
The firewall: `coerce_teammate_ballot_to_skip` (`meetings/manager.py:4349`), `check_no_betrayal`
(`eval/validity.py:759`, planted at `tests/eval/test_validity.py:355`) and
`TestTeammateGuardOnProductionPath` (`tests/meetings/test_manager.py:1629`).
`label_ballot_grounding` (`meetings/manager.py:4451`) is role-blind; its `supported` means the cited
line names the target (`turn_bears_on`, `meetings/citation_relevance.py:106`), not that it points
toward them. SKIP wins ties, and an ejection needs one ballot for the target at or above the
tally's confidence threshold (`tally_ballots`, `meetings/voting.py:190-236`), so strategic impostor
EJECTs can meet it alone.

**Baseline 9, count-only** (investigation memo section 2 and decision memo section 4; re-measure).

| cell | s9 | pooled, four sets |
|---|---|---|
| impostor ballots: EJECT / SKIP | 46 / 164 | 183 / 760 (943) |
| impostor EJECTs labelled `supported` / `off_target`; at confidence >= 0.6 | 44 / 2; 46 of 46 | 178 / 5; 182 of 183 |
| impostor SKIPs with `decision_basis` `none_held` | 95 of 164 | 440 of 760 |
| impostor SKIPs holding a citable row pointing toward a non-teammate | 163 of 164 | 759 of 760 |
| teammate-coerced impostor ballots | 1 | 13 |
| crew ballots holding a first-hand kill sighting of a non-teammate | 4 at 4 meetings | 31 at 30 meetings |
| impostor ballots holding a sighting of their teammate's kill (teammate living) | 18 (12) | 87 (56) |
| kill rows the per-subject budget would drop | 0 | 1 of 31 |
| kills with a crew witness; with an impostor-teammate witness | n/a | 20 and 50 of 849 |
| ejections whose confidence floor impostor ballots alone met | 0 of 90 | 0 of 411 (31 had an impostor among them) |

The grounding bound almost never binds (759 of 760 impostor SKIPs could have cited a
pointing-toward row), so the impostor EJECT rate under this arm is a property of the wording. The
kill row is tiny (4 holder ballots on s9) and is assessed for presence, not effect. The committed
kill-holder meetings, the golden's live coverage for "old recordings render identically", are s9
seed 17 m3, 19 m3, 26 m0 and 26 m1, and s4 seed 22 m0 (memo 2.5, Moot).

**The railroad tripwire can go vacuous.** `check_no_railroaded_crew_ejections`
(`eval/validity.py:855`) reads vote prompts only through `_SUSPICION_GRAPH_HEADER` and a row regex
(`:176-191`, block cut at the next `## ` in `_rendered_suspicions`, `:834`) and passes when nothing
parses; `_parse_suspicion_graph` (`eval/meeting_quality.py:402`) reads the same block. This card
edits the text under that header.

## Acceptance

- [x] Review correction: **an EJECT citing a turn and an own observation is classified by the
  turn** (round 2, correctness verifier, probe R07). Two new carriers in
  `tests/meetings/test_ballot_arms.py::test_each_carrier_moves_its_cell_by_exactly_one`: impostor
  p-2's EJECT keeps its own observation and also cites p-7's turn, which points nowhere (another
  turn +1, neutral only -1), or its own turn accusing the target (pointing toward +1, own turn +1,
  neutral only -1). Probe R07 (swap the turn branch and the observation branch in
  `eval/evidence_honesty.py::_fold_ballot_conduct`) now fails it.
- [x] Review correction: **the carried-ejection cell reads only ballots for the ejected player**
  (round 2, correctness verifier probe R05 and the docs verifier's cell-4 finding, the same
  probe). New carriers in the same test: crew p-1 voting p-9, or SKIP, at 0.9 leaves
  `ejections_carried_by_impostors_alone` unchanged, and crew p-1 voting the ejected p-7 at 0.9
  lowers it by one. Probe R05 (keep only the confidence filter in the carried list) now fails it.
- [x] Review correction: **the ejected-target comparison is pinned** (round 2, integrity verifier,
  probe P3). The same carriers; P3 (`ballot.target == entry.ejected_player_id` read as
  `ballot.target is not None`) now fails them.
- [x] Review correction: **only an accusation against the target points toward it** (round 2,
  integrity verifier, probe Q1). New carrier in the same test: the cited turn accuses p-9, not the
  EJECT's target, so the EJECT cites another turn (+1) and pointing toward is unchanged. Probe Q1
  (`claim.against == target` read as `claim.against is not None` in `_points_toward`) now fails it.
- [x] Review correction: **a contradiction points toward only from the turn it was minted from**
  (round 2, integrity verifier, probe Q4). New entry in the same test's conflict loop: a
  contradiction naming the target, minted from two other turns, while the cited turn accuses
  nobody: another turn +1, pointing toward unchanged. Probe Q4 (drop the per-turn conjunct on the
  contradiction branch of `_points_toward`) now fails it.
- [x] Review correction: **the ballot family's per-turn filter is pinned** (round 1, correctness
  verifier). A new carrier in `tests/meetings/test_ballot_arms.py::test_each_carrier_moves_its_cell_by_exactly_one`
  has another turn of the meeting accuse the target while the cited turn does not: it moves
  `ejects_other_turn` by one and leaves `ejects_pointing_toward` unchanged. Probe V16 (drop the
  per-turn filter in `eval/evidence_honesty.py::_points_toward`) now fails it.
- [x] Review correction: **an absent or unparseable body gets the body check's own refusal**
  (round 1, correctness verifier). `test_an_absent_or_unparseable_body_is_the_same_refusal_naming_the_file`
  (both arms) deletes the registered `vote_ballot.j2` from one set copy and appends a syntax error
  to it in another; each raises the check's `ValueError` naming the set and the file. Probes V01
  (drop `TemplateNotFound`) and V02 (drop `TemplateSyntaxError`) now fail it.
- [x] Review correction: **four message arguments are pinned** (round 1, correctness verifier). The
  set name in the body check's refusal (`test_a_dead_guard_is_no_block`,
  `test_the_runner_refuses_an_arm_for_a_set_whose_ballot_has_no_block`), the arm and
  account-profile lists in the profile refusal
  (`test_the_profile_refuses_a_ballot_arm_beside_an_account_profile` and the new
  `test_the_profile_refusal_names_every_arm_and_account_profile_it_met`), and the meeting id in the
  missing-memory raise (`test_a_ballot_by_a_player_with_no_rebuilt_memory_raises`). Probes V04,
  V20, V21 and V22 now fail.
- [x] Review correction: **the listed-class survivors V01 and V02 are killed and V03 is named
  equivalent** (round 1, integrity verifier; the same except tuple as the second item). The
  planted cases are the ones above; V03 (drop `AttributeError`) is equivalent because
  `_environment_for_set` always gives the environment a `FileSystemLoader`, so `loader` is never
  `None`. All three are in the round-1 mutation table.
- [x] Review correction: **`kill_holders_citing_the_kill` reads both slots that take an own
  observation id** (round 1, docs verifier; Codex P2 on PR #491). The fold counts a kill
  observation cited in `primary_reason_observation_id` or in `counter_reason_id`, as the family's
  sentence and cell 5 say. Planted: a holder citing the kill only in the counter slot moves the
  cell by one, and a counter naming a turn does not. Re-measured with
  `uv run python scripts/measure_baseline.py replays/<set> --honesty --json` on the four sets: every
  report equals the previous head's byte for byte, so cell 5 stays 3 of 4 on s9 and 21 of 31
  pooled.
- [x] **The kill record moves and carries its id.** `KillWitnessRecord` moves to
  `meetings/schemas.py` beside `VentWitnessRecord` as a `_FrozenModel` with
  `observation_id: ObservationId | None = None`; `orchestrator.game` re-exports it, so
  `training/conviction/serving.py` and `tests/training/test_composed_runner.py` import it unchanged;
  the accessor passes `observation_id=event.observation_id` and keeps its teammate guard. Mechanism:
  the field, the accessor and the re-export. Proof: the equality assertions at
  `tests/training/test_conviction_serving.py:378-380` and `:409-411` (memo 2.5 item 6; also
  `:437-439` if it compares records) carry the id, and the conviction parity pin passes unchanged.
  Planted: an accessor that drops the id fails them.
- [x] **A witness gets exactly one row.** Mechanism: an optional `@runtime_checkable`
  `KillWitnessAgent` protocol, used by `_build_participants` as it uses `MoveWitnessAgent`;
  `MeetingParticipant.kill_witness_records` (default `()`); `"own_kill"` in `EvidenceRowKind` and
  in `_EVIDENCE_KIND_CLASS` as class 0; one row per record in `_own_channel_evidence_rows`, built
  only when the manager's evidence profile has `ballot_kill_row_version == 1`. Proof: a crew
  participant with one record gets one `own_kill` row with the exact description, `first_hand`,
  the voter as speaker and the record's id as `citation_id`; it names no victim, sorts by tick
  among the killer's class-0 rows and obeys the budget; the description equals the census card's
  own-kill pattern constant: the test imports it from `eval/gameplay_census.py`, which this card
  never edits, while `meetings/` imports nothing from `eval/`. Planted: the same participant with
  the arm OFF gets no row, and a row whose wording differs from the constant fails the equality.
- [x] **A voter who was only told gets nothing.** A `TacticalAgent` whose store holds only a
  reported `saw_kill` statement (`absorb_reported_testimony`) returns `()` from the accessor and
  gets no `own_kill` row. Mechanism: the accessor's observed-provenance filter. Planted: the same
  event written with observed provenance produces the row.
- [x] **The teammate firewall holds at assembly.** Mechanism: `if record.subject in teammates:
  continue` in the kill loop, as in the vent, sighting and transit loops. Proof, with records
  passed directly so the assembly guard is what is proven: an impostor with
  `fellow_impostor_ids=("p-3",)` and a record naming p-3 gets no row, while the identical records
  on a crewmate keep it (the `test_the_identical_records_on_a_crewmate_keep_every_row` pattern,
  `tests/meetings/test_weighing_channel.py:1710`). Planted: deleting the new `continue` fails the
  impostor case. Committed-data twin, count-only, arm forced ON through an existing
  `tests/_helpers/committed.py` entry point: the impostor holders of a teammate-kill sighting (87
  pooled, re-measured) get 0 `own_kill` rows; if no entry point fits, a scratch count in Results.
- [x] **Old recordings render identically.** With the arm OFF and kill records present,
  `build_evidence_rows` returns today's tuple and the golden re-renders every committed s9 and s4
  ballot byte-identically. Mechanism: the profile gate. Planted, in the golden: with the gate
  forced ON the golden fails at the committed kill-holder meetings (re-measured, named in Results),
  so the OFF gate is not vacuous.
- [x] **No flag, no ledger, no belief.** With the arm ON, `detect_contradictions`, the testimony
  ledger and the belief fold equal OFF on a meeting with kill records. Mechanism: the record reaches
  the assembler only, and `TestTheAssemblerCannotReachTheLedger`
  (`tests/meetings/test_weighing_channel.py:1549`) adds every new helper to `_ASSEMBLER`. Planted:
  a helper passing kill records to `build_testimony_ledger` fails the scan.
- [x] **Crew bytes.** Under `ballot_kill_row_version=1`, a ballot with no kill record differs from
  OFF only in the suspicion-header sentence, which becomes (proposed): "And it is only a PARTIAL
  summary of the lines above: someone you saw near a body just before you found it moves these
  numbers with no line of its own up there — your memory block above still carries that."
  `_PARTIAL_SUMMARY_CLAIM` stays verbatim, and the test at `:2087` keeps pinning the OFF body.
  Under `impostor_ballot_version=1` every crew ballot is byte-identical to OFF. Mechanism: the
  guards, whitespace-controlled. Planted: an impostor block whose guard omits the role test changes
  a crew ballot and fails.
- [x] **The role reaches every impostor.** `voter_role` is an additive defaulted keyword on
  `VotePromptRenderer` and `vote_ballot_prompt`, passed by the manager's vote render call from
  `participant.role`, beside the two arm values from the manager's evidence profile; every other
  prompt set ignores them. Mechanism: the keyword and the guard. Proof: under the arm an impostor
  with `fellow_impostor_ids=()` (the 4p1i shape) renders the strategy text. Planted: with
  `voter_role` withheld the same voter renders the crew text and the test fails.
- [x] **The impostor wording, tightened and neutral.** Under `impostor_ballot_version=1`, for
  impostor voters only:
  - the persona keeps its win-condition clause and replaces the belief clause. Proposed: "You are
    {{ impostors.one_of_them }}. The discussion is over — cast one ejection ballot. It is a move for
    your side, not a statement of who {{ impostors.subject }} {{ impostors.verb_be }}: name one
    crewmate to eject, or SKIP, whichever you judge better for your side. The outcome is a
    deterministic tally over every ballot.";
  - the team block renders for every impostor voter: its Secret line, present only with a teammate,
    loses its belief clause ("Never vote a teammate, and never your own name: your ballot names a
    crewmate or SKIP, nothing else."), and a sole impostor's block keeps the own-name rule;
  - one honest-citation paragraph carries R10's tightened sentence verbatim, then: copy that line's
    id exactly; you may choose which of the lines you hold to cite; cite only lines really on this
    page; in "rationale_text" say only what the cited line shows; when nothing you hold points
    toward any crewmate, write SKIP;
  - left alone: both confidence sentences (`:247`, `:306`), the nine-key contract, `decision_basis`.
  Mechanism: tests after `test_the_decision_section_recommends_no_player` (`:2063`): the new persona
  and citation text name no player, rank nothing, recommend no target, carry no digit, no confidence
  clause and no task, audit or ruling ID, and contain the tightened sentence; the team block names
  only the teammate list. Planted: a body saying a sighting may be invented, one with a confidence
  clause, one with a digit: each fails.
- [x] **The firewall under the impostor arm.** A scripted impostor ballot naming its teammate,
  rendered through the arm, is recorded as SKIP with `guard_rewrite_reason="teammate_coerced"`, its
  marker and label `not_assessed`, and `check_no_betrayal` passes. Mechanism: the unchanged
  coercion. Planted: with the coercion monkeypatched to identity, `check_no_betrayal` fails.
- [x] **The meeting layer labels and never rewrites.** An impostor EJECT citing an accusation turn
  against its target labels `supported`; an impostor SKIP with no ids labels `none_held`; a scripted
  impostor EJECT citing only its own sighting of the target is recorded as cast, tallied for that
  target and counted in the compliance cell below. Mechanism: the role-blind labeller and the
  label-blind tally (D6). Planted: a tally patched to drop the ungrounded EJECT changes the scripted
  outcome and the test fails.
- [x] **Stamps, derived and never a default.** The spine's experiment-arm registry gains exactly
  two entries, `ballot_kill_row_version` and `impostor_ballot_version`, each re-bodying
  `vote_ballot` only. Mechanism: the spine's derivation function and fold. Proofs in
  `tests/agents/test_bespoke_prompt_sets.py`: either arm serves its derived stamp; both serve
  `vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1+vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1`
  (memo 3.3); the `.v6` stamps are unchanged; no arm stamp equals a default or overlay stamp; the
  first header marker stays v8 (`TestVersionMarkersMatchTheRegistry`, `:1012`), the header prose
  names both arms by field name, and `PROMPT_VERSION_SETS`, `DEFAULT_PROMPT_VERSIONS` and the four
  overlay registries are unchanged. Planted: a hand-written suffix fails the derivation test; a
  runner whose served stamps omit an arm its manager renders fails the one-source check.
- [x] **Refusals.** `MeetingEvidenceProfile` validation refuses either ballot arm with
  `public_account_version` or `attributed_testimony_version`; `build_default_meeting_runner`
  refuses either arm while `impostor_roll_call`, `reporter_reasoning`, `corroboration_discipline`
  or `testimony_shapes` is ON, beside the account-mode refusal (`orchestrator/game.py:1388-1403`),
  in plain words. Mechanism: the validator and the runner check. Planted: each combination raises.
  Adverse: each arm alone, and both with the rebuttal and the reset, construct.
  `EXPERIMENT_ENV_NAMES` and `.env.example` are unchanged; if a registry check wants an env name
  for every profile field, a config-only allow-list lands with a planted case (memo 2.5 item 6).
- [x] **The railroad tripwire cannot go vacuous.** A ballot rendered with each arm ON, and with
  both, parses through `_rendered_suspicions` and `_parse_suspicion_graph` to exactly the rows of
  the suspicion graph it was given (one per living player in the scripted case), and on the
  scripted arm-ON recording `check_no_railroaded_crew_ejections` reports `rendered_crew_rows > 0`.
  Mechanism: the header and the row shape stay intact under both guards. Planted: a template copy
  whose ON block edits the header, or puts a `## ` line between the header and the rows, parses
  to zero rows and fails; an arm-ON prompt with a crew row at 1.00 and two same-meeting flags
  naming that crewmate fails the check.
- [x] **The golden covers the ON body.** Called on a scripted both-arms-ON recording in
  `tmp_path` (the readers card's directory walk and `tests/_helpers/scripted_meeting.py`, to which
  this card adds its ballot cases), the golden re-renders every ballot byte-identically through the
  arm stamps. Mechanism: the readers card's arm-stamp resolution over this card's registry entries.
  Planted: dropping a bound arm value fails it; a one-byte edit inside an ON block leaves the
  golden on s9 and s4 green and fails it on the scripted recording.
- [x] **Evidence-honesty cells.** `eval/evidence_honesty.py` gains one ballot family with its own
  `CELL_DEFINITIONS` sentence (numerator, denominator, and what it does not measure: whether an
  accusation is true, or intent), repeated verbatim in the module and family docstrings under the
  existing drift test. A citation **points toward** target T when the cited turn carries a typed
  accusation against T or minted a contradiction flag of this meeting naming T (the
  `_turn_id_for_event` mapping); a cited own observation is **neutral**. Cells: (1) impostor EJECT
  and SKIP counts; (2) impostor EJECTs by cited kind: pointing toward (split by whether the cited
  accusation is the voter's own turn), neutral only, other turn, no valid citation; (3) **R10
  compliance**: impostor EJECTs whose valid citations are only neutral rows, over impostor EJECTs;
  (4) ejections whose confidence floor, read from the tally's own parameter, is met only by
  impostor ballots, over ejections; (5) kill-row presence: first-hand kill holders at meeting open
  (the accessor's own predicate over the walk's rebuilt memories) and their ballots citing the kill
  observation; (6) recorded teammate targets, which `check_no_betrayal` requires to be 0.
  Mechanism: a fold beside `_fold_grounding`. Planted: one carrier per cell moves it by exactly
  one. Proof: on the scripted arm-ON game cell 4 equals the census's "ejections carried only by
  impostor ballots"; on baseline 9 it reads 0 of 411 pooled. No cell is a gate; Results reports
  cells 1-4 and 6 on s9 and pooled as the record card's "before".
- [x] **The census reads 0 by construction on a scripted arm-ON game.** One end-to-end test in this
  card's own test file folds the scripted game through the census's `--set-dir` path: "own-kill
  rows naming a teammate or held by a non-witness" reads 0 over a non-empty denominator, and
  "recorded teammate ballot targets" reads 0. Mechanism: the census conformance fold over the
  served rows. Planted: a copy whose impostor ballot prompt carries an `own_kill` row naming its
  teammate raises the census conformance error.
- [x] **The pending guard is gone.** With B0, B1 and B4 merged, this card's two names are the last
  in `WAVE_ARMS_PENDING`. It deletes them, then the mapping, its checks at config validation, at
  `HeadlessGame` construction and in `build_default_meeting_runner`, and the refusal test;
  `git grep -n WAVE_ARMS_PENDING -- '*.py'` prints nothing and every test that patched the mapping
  drops the patch (files named in Results). Mechanism: deletion (craft rule 3). Proof: a test
  validates the round-1 config literal (memo section 1) as a `RecordedExperimentConfig`, constructs
  a fake-provider `HeadlessGame` from it in a bare environment, plays one seed to its end and loads
  it through `ReplayLoader` with `outcome_verified` true. Perturbed: the same test at the merge
  base, where the guard still refuses the two ballot values, fails; Results quotes the failure.
- [x] **The OFF path is byte-identical.** Mechanism: default `None`, the omitted key and the
  whitespace-controlled guards. Evidence at the branch head: the four-set loop under Validation
  (`verify_samples`, `build_sample_report --check`, and `--honesty --json` whose pre-existing
  families equal the merge base's exactly); the golden on s9 and s4, whose one-byte perturbation leg
  and the planted leg above are the failing sides; the scorecard and census `--check`;
  `uv run pytest -m campaign`; and an empty demo-bundle diff (Record impact).

## Constraints

**The partial-record principle binds this card.** Only `replays/samples/9p2i`'s seeds 0-49 are
ever re-recorded, only into `replays/candidates/stage-b-r1/9p2i/`, and only by the record card.
Every switch is a `RecordedExperimentConfig` field, default-OFF and omitted from the payload at its
default. Every committed recording, derived view, fixture, gate and doc fact keeps verifying
byte-identically. No registry prompt bump and no archive: `vote_ballot` stays at v8, and v9 stays
unallocated until an adopting decision. Role-correctness is reported, never a gate: the compliance
and floor cells are readings the record card pre-registers. Nothing pushes an agent toward the
correct answer: the kill row restates a first-hand fact the witness holds, and the impostor text
names, ranks and recommends no player. The meeting layer labels and never rewrites: no new guard,
marker or rewrite reason, and the three marker mirrors (`_BALLOT_MARKER_CHAIN`,
`_BALLOT_PREFIX_MARKERS`, `BALLOT_AUDIT_MARKERS`) are untouched.

**Prompt copy.** The new ballot text carries no task, audit or ruling ID, no unexplained jargon and
no threshold arithmetic or other number (craft rule 4); a term needing definition gets a glossary
entry, named in Results.

**Wave and order.** Wave 4, card 10 of the memo's section 3.1. It starts after the meeting-reset
card (`tasks/work/meeting-reset-coherence.md`) has merged; by then A3, the census, the spine, the
readers and physical-witness cards, and the look-and-wait and body-handle cards have merged. Record
plumbing may still be open; the two cards share no file. It merges before the record card (`tasks/work/stage-b-record-r1.md`), whose
preflight asserts the guard is gone. Every merge is the owner's. The PR cites the dated 2026-09-24
addendum to `tasks/direction-2026-09-19-process-over-outcome.md` (memo section 6).

**Shared files, one writer at a time (memo 3.2).** No other card is active in wave 4.
- `orchestrator/game.py`, region-owned: `KillWitnessAgent` beside `MoveWitnessAgent`;
  `_build_participants`; the accessor, the record's docstring and the re-export; the two entries in
  the spine's arm-stamp registry; and the legacy-overlay refusal in `build_default_meeting_runner`.
  That last region is the spine's and lies beyond 3.2's list for this card; it is the only place
  the substrate flags are visible, the edit is serial, and Results records it.
- `orchestrator/experiment_config.py`, the declared exception: removals merge in the order B0, B1,
  B4, B6; this card deletes its two names, then the emptied guard and its checks. In the spine's
  `tests/orchestrator/test_experiment_arms.py` it deletes only the refusal test.
- Serial after the earlier writers: `meetings/manager.py` (A3, then B2), `meetings/schemas.py` (A3),
  `meetings/corroboration.py`, docstring only (B2), `meetings/evidence_profile.py` (the spine),
  `eval/evidence_honesty.py` (readers, then B2; the ballot family),
  `tests/meetings/test_prompt_byte_golden.py` (A3's construction at `:1641`, then readers, then
  B2; the planted OFF leg),
  `tests/_helpers/scripted_meeting.py` (readers; ballot cases), `tests/meetings/test_manager.py` (A3).
- Serial after A3, which edits its constructions at `:705` and `:744` first:
  `tests/training/test_conviction_serving.py` (this card's region is the equality assertions at
  `:378-380` and `:409-411`, and `:437-439` if it compares records).
- Single writer: `meetings/render_contract.py`, `agents/strategic/prompts/loader.py`,
  `vote_ballot.j2`, `tests/meetings/test_weighing_channel.py`,
  `tests/agents/test_bespoke_prompt_sets.py`, and a new `tests/meetings/test_ballot_arms.py`.
- Not written: `eval/gameplay_census.py` (the census card's alone: this card's test imports its
  own-kill pattern constant and pins the row text to it), `eval/validity.py`,
  `eval/meeting_quality.py`, `eval/process_scorecard.py`, `tests/_helpers/committed.py`, `api/`,
  `frontend/`, `training/` code, `docs/` other than a glossary entry, and every recorded byte.

**Decisions this card makes, recorded in Results.** (1) The kill row is class 0 under the same
budget (D5 orders by provenance, never strength; 1 of 31 baseline rows dropped). (2) It names no
victim; the record carries none. (3) The manager passes `voter_role` and the arm values at the
render call from its profile, and the runner's stamps come from the same profile (the spine's
one-source rule). (4) Account-mode refusals sit in the profile validator, overlay refusals in the
runner. (5) The ballot family is a new fold beside `_fold_grounding`, which memo 3.2 names but
which folds one strong flag's sighting side. (6) `KillWitnessRecord` becomes a frozen pydantic
model; its one training reader uses `.subject`.

**What stays out.** No confidence clause, no number in the prompt, no ranking, no recommended
target. No kill row for an impostor's teammate; no public flag or ledger entry for any kill. No
`AILIBI_*` lever and no env var. No viewer, featured-list or public-results change (owner ruling
11). No ML training, refit or corpus change (owner ruling 12). No scorecard cell (R13). No
held-out band. Fake provider and scripted clients only: no live call and no `.env`.

**Delivery.** Branch `work/ballot-kill-row-and-impostor-strategy`, one PR into `main`, merged or
fast-forwarded, never squashed; never amend a pushed commit; merge `main` in, never rebase. Each
commit body carries `Card: tasks/work/ballot-kill-row-and-impostor-strategy.md` immediately
followed by the exact line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` (the house trailer, verbatim, whichever model the worker session runs). The PR body fills the
template's Summary, Definition of done, Decisions and Questions and ends with the Claude Code
attribution line. Agents post no PR comments. `bash scripts/check.sh` is reported with its real
exit code. The Status line and `tasks/README.md` are the orchestrator's (the validator derives the
inventory sentence from every Status); the worker fills Results.

**Stop and ask** if: `WAVE_ARMS_PENDING` holds a name other than this card's two at dispatch; a
committed byte, derived view, census cell or pre-existing honesty or counterfactual pin moves
under OFF; the golden needs more than the planted OFF leg to stay green; or the wording seems to
need a confidence clause, a number, a registry bump or an archive.

## Expected scope

The files and regions named under Constraints: in `meetings/`, `schemas.py`, `manager.py`,
`render_contract.py`, `evidence_profile.py` and `corroboration.py` (docstring); the regions of
`orchestrator/game.py` and `orchestrator/experiment_config.py`; `vote_ballot_prompt` in
`agents/strategic/prompts/loader.py`; guarded blocks at the persona, the suspicion header and the
team block of `agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2`, plus header prose;
`eval/evidence_honesty.py`; the new `tests/meetings/test_ballot_arms.py` (scripted arm-ON cases,
tripwire, golden ON leg, census end-to-end test, round-1 config) and the test files named under
Constraints. Directly necessary follow-through inside these files, and renderer test doubles
elsewhere that need the defaulted keywords, is permitted and named in Results.

## Record impact

**What moves: nothing.** No committed recording, report, fixture, prompt stamp, doc fact,
scorecard or census cell changes. The evidence-honesty report gains one additive family; no
committed file stores that report, and its pre-existing families stay byte-equal. The two fields
are recorded ON only by the record card, into `replays/candidates/stage-b-r1/9p2i/`, under the
composite `vote_ballot` stamp of the version plan (memo 3.3).

**Reading notes for the record card.** Every grounded impostor EJECT lands in scorecard row 8 by
construction (teammate ballots are coerced, so its target is a crewmate): row 8 rises with the
impostor EJECT share partly as bookkeeping (today 178 of the 462 pooled numerator, s9 44 of 119),
and its voter-role split is read from the census, never a new scorecard cell (R13). B1 to B4 share
the record, so R10 is read by its process cells (the pre-registered R10 reading uses cell 3) and R8
for presence only. Projected cost: about 34k input tokens against 9.85M on s9, under 0.4%
(investigation memo section 8, an estimate).

**Publication.** A push to `main` republishes the demo bundle (`.github/workflows/pages.yml`).
This card edits nothing under `api/` or `frontend/`, touches no shown replay, and neither
`EvidenceRow` nor `KillWitnessRecord` reaches the generated types, but the bundle's loader imports
meetings and orchestrator code this card changes. So the PR proves the shown bundle unchanged:
`scripts/build_demo_bundle.py --out <scratch>` at the merge base and at the head, then a diff of
the two `data/` trees, which must be empty.

**Adoption, later and not here**, per memo section 1 (adoption items 2, 3 and 6): the four-set
re-record (`vote_ballot` flips to v9) or the promotion path (the v8 archive); graduation deletes
each switch and keeps its recorded key, a missing key meaning OFF (craft rule 3).

**Limitations that stay.** The grounding bound is instructed, not enforced; so is "say only what
the cited line shows", since the rationale-faithfulness row checks tokens, not propositions.
`supported` means aboutness; the compliance cell uses the stricter typed test. The kill row has no
statistical power at 50 seeds.

## Validation

```
uv sync --frozen
uv run pytest tests/meetings/test_ballot_arms.py tests/meetings/test_weighing_channel.py \
  tests/meetings/test_manager.py tests/agents/test_bespoke_prompt_sets.py \
  tests/eval/test_evidence_honesty.py tests/orchestrator/test_experiment_arms.py \
  tests/training/test_conviction_serving.py tests/training/test_composed_runner.py \
  tests/meetings/test_prompt_byte_golden.py tests/eval/test_validity.py -q
uv run lint-imports
git grep -n WAVE_ARMS_PENDING -- '*.py'            # must print nothing
# the OFF path at the branch head, in a bare shell, once per set directory
for s in samples/9p2i samples/4p1i ml_corpus/9p2i ml_corpus/4p1i; do
  bash scripts/verify_samples.sh "replays/$s"
  uv run python scripts/build_sample_report.py --sample-dir "replays/$s" --check
  uv run python scripts/measure_baseline.py "replays/$s" --honesty --json > "<scratch>/honesty-${s/\//-}.json"
done
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/verify_ml_evidence.py        # offline; never --complete
uv run pytest -m campaign                          # the c9 refit pins' campaign-tier half
# the bundle, at the merge base and at the head, into scratch directories outside the tree
uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-base
uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-head
diff -r <scratch>/bundle-base/data <scratch>/bundle-head/data
# the full gate, whole, in a clean worktree, with its real exit code quoted in Results
bash scripts/check.sh; echo "check.sh exit $?"
```

Every gate runs in a bare shell with no `AILIBI_*` export; the honesty JSON is compared with the
merge base's family by family, excluding only the new family. `npm --prefix frontend test` and the
Playwright journey are not required (no `api/` or `frontend/` edit); `check.sh` still runs the
frontend legs, and the bundle diff is the publication proof.

## Results

Implemented on `work/ballot-kill-row-and-impostor-strategy` from `4b1e9a01` (main after B2, #490;
every earlier Stage-B card merged). Commits: `958aeb3e` (both arms, the refusals, the registry
entries, the deletion of `WAVE_ARMS_PENDING` and of the emptied `UNBUILT_OPTION_VALUES`, the arm
page and the test follow-through), `f01cff63` (the evidence-honesty ballot family), `7ca0485a`
(the scripted ballot game and `tests/meetings/test_ballot_arms.py`), `92e8803a` (the planted cases
the mutation pass asked for) and the Results commit, which changes only this card and
`tasks/README.md`. Every command below ran at `92e8803a` in a shell with no `AILIBI_*` export
unless a line names another commit; no production byte changed after `f01cff63`.

**Sections relied on.** `docs/architecture.md` "Enforced boundaries" (the meeting layer imports
nothing from `eval/`; `agents/` imports no engine module; `lint-imports` 4 kept) and "Explicit
cleanup experiments", which links the arm page `docs/experiment-arms.md` (the meeting layer, the
omit-at-default rule, config-only ballot fields, the registry and its derived suffix). The Stage-B
decision memo `tasks/decision-2026-09-24-stage-b-wave.md`: 0.2 (R8, R10 and its enforcement
note), 0.3 items 2, 4, 5, 6 and 9, 2.5, 3.2 (the one-writer map), 3.3 (the composite stamp) and
the card-10 brief in 3.4. The investigation `tasks/investigations-2026-09-24/ballot_kill_row_and_impostor_strategy.md`
sections 1-8, with the memo overruling its v9 stamp and environment switch. The dated 2026-09-24
addendum to `tasks/direction-2026-09-19-process-over-outcome.md`, which records R10 ("an impostor
may name a crewmate only when it can cite a line it holds that points toward that crewmate ... The
tally does not enforce the SKIP").

**What was built.**
- `meetings/schemas.py`: `KillWitnessRecord` as a frozen model beside `VentWitnessRecord`, with
  `observation_id: ObservationId | None = None`. `orchestrator.game` re-exports it (`__all__`), so
  `training/conviction/serving.py` and `tests/training/test_composed_runner.py` import it unchanged.
- `orchestrator/game.py`: the accessor's predicate became `kill_witness_records_in(events)`
  (first-hand `saw_player` rows stamped `kill`, the teammate guard, the row's `observation_id`);
  `TacticalAgent.kill_witness_records_for_meeting` calls it. An optional `@runtime_checkable`
  `KillWitnessAgent`, read by `_build_participants` as it reads `MoveWitnessAgent`. The two
  registry entries (`EXPERIMENT_ARM_TEMPLATES`, both re-bodying `vote_ballot`). In
  `build_default_meeting_runner`: the refusal of either arm beside any of the four legacy overlays
  (the spine's region, edited serially, see Decisions), the body check, and the one-source check
  on the served stamp. The pending checks at the runner and at `HeadlessGame` construction are
  gone.
- `meetings/manager.py`: `MeetingParticipant.kill_witness_records` (default `()`); `"own_kill"` in
  `_EVIDENCE_KIND_CLASS` as class 0; one row per record in `_own_channel_evidence_rows`, built only
  when `ballot_kill_row_version == 1` and dropping a fellow impostor again; `build_evidence_rows`
  takes the arm value, and the manager passes its profile's value there and passes `voter_role`
  and both arm values at the ballot render.
- `meetings/render_contract.py`: `"own_kill"` in `EvidenceRowKind`, `VoterRole`, and the three
  defaulted keywords on `VotePromptRenderer`; `agents/strategic/prompts/loader.py`: the same three
  on `vote_ballot_prompt`, and `require_guarded_bodies` (the testimony-shapes body test with the
  guard name as a parameter).
- `vote_ballot.j2`: guarded blocks at the persona, the suspicion header's sentence and the team
  block, plus header prose naming both arms; the marker stays `vote_ballot.qwen3_6_27b.v8`.
- `meetings/evidence_profile.py`: the profile refuses either ballot arm beside either account
  profile. `meetings/corroboration.py`: docstring only.
- `orchestrator/experiment_config.py`: `WAVE_ARMS_PENDING`, `refuse_pending_values` and the config
  validator that called it are deleted. `agents/tactical/experimental.py`: the emptied
  `UNBUILT_OPTION_VALUES`, `UnbuiltTacticalOptionError` and `_refuse_unbuilt_options` are deleted.
- `eval/evidence_honesty.py`: `BallotConductCells` (report field `ballot_conduct`,
  `CELL_DEFINITIONS["ballot-conduct"]`), folded by `_fold_ballot_conduct` beside `_fold_grounding`.
- `docs/experiment-arms.md` (the pending-guard section and the registry paragraph) and one
  sentence of `docs/architecture.md`.

**The served text.** Under `impostor_ballot_version = 1`, for an impostor voter only, the persona
keeps its win-condition clause and continues: "You are {{ impostors.one_of_them }}. The
discussion is over — cast one ejection ballot. It is a move for your side, not a statement of who
{{ impostors.subject }} {{ impostors.verb_be }}: name one crewmate to eject, or SKIP, whichever you
judge better for your side. The outcome is a deterministic tally over every ballot." The team
block renders for every impostor: with a teammate, "Secret: ... is your fellow saboteur. Never vote
a teammate, and never your own name: your ballot names a crewmate or SKIP, nothing else."; alone,
"Your own name never goes in "target": your ballot names a crewmate or SKIP, nothing else."; then
the paragraph "Name a crewmate only when you can cite a line you hold that points toward them: a
turn in which someone accused them at this table, or a conflict that names them. Copy that line's
id exactly. You may choose which of the lines you hold to cite. Cite only lines that are really on
this page, and in "rationale_text" say only what the cited line shows. When nothing you hold points
toward any crewmate, write SKIP." Under `ballot_kill_row_version = 1` the header sentence reads
"And it is only a PARTIAL summary of the lines above: someone you saw near a body just before you
found it moves these numbers with no line of its own up there — your memory block above still
carries that." (the card's proposal, verbatim), and the witness reads `you watched them KILL in
{room} at tick {tick}` rendered as "first-hand: you saw this yourself; cite `<id>`". No new term
needed a glossary entry: the new copy uses plain words and no ID, number or threshold.

### Decisions

1. **The kill row is class 0 under the same budget** (D5 orders by provenance, never strength).
   Re-measured: 32 kill records at 31 holder ballots pooled, 1 dropped by the per-subject budget
   (ml_corpus/9p2i), 0 on samples/9p2i.
2. **It names no victim**; the record carries none.
3. **One source.** The manager passes `voter_role` (from `participant.role`) and both arm values
   at the ballot render from its own evidence profile; the runner folds its stamps from the same
   profile (`_profile_arm_config`). An explicit `prompt_versions` pin bypasses the fold, so the
   runner now checks that the served `vote_ballot` stamp credits exactly the arm values the
   profile renders with (`_served_experiment_arm_values`), both ways, and raises otherwise.
4. **Where each refusal sits.** Account profiles: the `MeetingEvidenceProfile` validator. Legacy
   overlays: `build_default_meeting_runner`, beside the account-mode refusal, which now shares the
   one overlay list. That runner region is the spine's and lies beyond the memo's 3.2 list for this
   card; it is the only place the substrate flags are visible, and the edit was serial (no other
   card was active). The runner also refuses either arm for a prompt set whose served vote body
   has no live guard for it (`require_guarded_bodies`, the testimony-shapes body test with the guard
   as a parameter): the spine's Results named this refusal as the ballot card's.
5. **The ballot family is a new fold beside `_fold_grounding`** (`_fold_ballot_conduct`), not a
   widening of it: `_fold_grounding` folds one STRONG flag's sighting side. It reads the kill
   holders by the accessor's own predicate, which is why that predicate became the module
   function `kill_witness_records_in`.
6. **`KillWitnessRecord` is a frozen pydantic model.** Its one training reader uses `.subject`;
   the conviction parity pin (`tests/training/test_conviction_serving.py`) passes unchanged.
7. **The emptied `UNBUILT_OPTION_VALUES` guard is deleted with the pending guard**, following
   Decision 3 of the look-and-wait card ("the card that deletes `WAVE_ARMS_PENDING` deletes it
   with that test"). This file (`agents/tactical/experimental.py`) is not in this card's named
   scope, so it is reported as a deviation. The two readers' tests that used the guard as a probe
   (the recorded value reaches the policy builder) now stop the builder with a monkeypatched
   constructor that raises naming the value it received: the same claim, proven without the
   retired mechanism.
8. **The scripted game.** Seed 26 on the round-1 config, the first seed of a count-only search over
   fake round-1 games (seeds 0-79) whose recording serves an own-kill row: impostors p-2 and p-3,
   and crewmate p-1 watches p-3 kill before the first meeting. Its ballot script is in
   `tests/_helpers/scripted_meeting.py` (`BALLOT_ARMS_*`); a scripted citation is read off the
   prompt the voter was served and raises when the prompt holds no such row.
9. **Arm-page and architecture follow-through.** `docs/experiment-arms.md` and one sentence of
   `docs/architecture.md` described the pending guard in the present tense; the card lists `docs/`
   as not written except a glossary entry, so these two edits are reported as deviations (the
   earlier arm cards edited the same page for their removals).
10. **Where the new tests live.** The wording, crew-byte and role tests the card places "after
   `test_the_decision_section_recommends_no_player`" live in `tests/meetings/test_ballot_arms.py`
   beside the other arm-ON cases, reusing that test's recommendation pattern;
   `tests/meetings/test_weighing_channel.py` keeps pinning the OFF body and gains the planted
   ledger-scan case.
11. **Status and index.** The Constraints reserve the Status line and `tasks/README.md` for the
   orchestrator; the dispatch delegated the flip, so the Results commit flips Status to done and
   re-derives the inventory sentence with `scripts/validate_task_docs.py` (88 cards: 2 ready, 86
   done).

### Acceptance evidence

Tests: `tests/meetings/test_ballot_arms.py` (A) unless named.
- Record: A `test_the_kill_record_lives_beside_the_vent_record_and_is_re_exported`; the three
  accessor equality tests in `tests/training/test_conviction_serving.py` now carry
  `observation_id` (`OBS:5:1`, `OBS:6:1`, `OBS:3:1`/`OBS:7:1`); planted M27 below.
- One row: A `test_a_witness_gets_exactly_one_kill_row`, `test_the_kill_kind_is_named_and_sorts_with_the_first_hand_rows`,
  `test_a_kill_row_sorts_by_tick_among_the_killers_first_hand_rows`,
  `test_a_kill_row_obeys_the_per_subject_budget` (kill at tick 2 dropped, at 20 kept),
  the property `test_every_non_teammate_record_makes_exactly_its_own_row` (both arms, both roles,
  two voters), `test_a_row_worded_otherwise_is_not_the_census_row` (the census finds the built row
  and not a reworded one), `test_the_meeting_layer_imports_nothing_from_eval` (with its planted
  import), `test_the_participants_carry_the_kill_channel_of_an_agent_that_has_it`.
- Told, not watched: A `test_a_voter_told_of_a_kill_holds_no_kill_row` (absorbed reported
  `saw_kill`: accessor `()`, no row; planted: the same kill perceived first-hand makes the row) and
  `test_the_accessor_reads_first_hand_rows_only`.
- Teammate firewall at assembly: A `test_an_impostors_record_naming_its_teammate_makes_no_row`
  (records passed directly; the crewmate twin keeps both rows);
  `test_the_teammate_guard_reads_first_hand_self_state_only`. Committed-data twin: no
  `tests/_helpers/committed.py` entry point exposes the rebuilt memories, so it is a scratch count
  (below): 87 impostor holders of a teammate-kill sighting (56 with the teammate living), 0
  `own_kill` rows naming a fellow when their RAW records, teammate kills included, reach
  `build_evidence_rows` with the arm forced ON.
- Old recordings: A `test_the_arm_off_builds_no_kill_row_and_the_tuple_of_today`; the golden
  (`tests/meetings/test_prompt_byte_golden.py`) green on samples/9p2i and samples/4p1i; its new OFF
  leg `test_the_kill_row_gate_forced_on_fails_the_golden_at_the_kill_holders` forces the
  assembler's gate ON and fails at exactly five committed meetings: samples/9p2i seed 17
  `meeting-3`, seed 19 `meeting-3`, seed 26 `meeting-0` and `meeting-1`, and samples/4p1i seed 22
  `meeting-0` (memo 2.5's list, re-measured).
- No flag, ledger or belief: A `test_the_kill_arm_mints_no_flag_no_ledger_row_and_no_belief_input`
  (with kill records and the corroboration lever ON: equal flags, transcript, ledgers, suspicion
  graphs and `extract_belief_evidence`). `TestTheAssemblerCannotReachTheLedger` needed no new
  `_ASSEMBLER` member (the kill loop lives in `_own_channel_evidence_rows`); its planted
  `test_a_helper_handing_kill_records_to_the_ledger_fails_the_scan` is new.
- Crew bytes: the property `test_a_crew_ballot_moves_only_in_the_header_sentence` (60 generated
  renders: the impostor arm leaves a crew ballot byte-identical; the kill-row arm moves only the
  sentence; `_PARTIAL_SUMMARY_CLAIM` stays); planted
  `test_an_impostor_guard_without_the_role_test_moves_a_crew_ballot`. The OFF body stays pinned by
  `tests/meetings/test_weighing_channel.py::TestTheServedBody::test_the_number_is_called_a_partial_summary_of_the_rows`.
- Role: A `test_the_role_reaches_a_sole_impostor` (4p1i shape through the real manager; planted:
  `voter_role` withheld renders the crew text) and
  `test_the_manager_threads_the_role_and_both_arm_values_to_every_ballot`.
- Wording: A `test_the_impostor_wording_is_neutral_and_carries_the_tightened_sentence` (with a
  teammate and alone), `test_the_wording_scan_bites_a_planted_line` (an invented sighting, a
  confidence clause, a digit, a recommended target), and
  `test_the_impostor_arm_leaves_the_confidence_sentences_and_contract_alone`.
- Firewall under the arm: A `test_a_teammate_ballot_under_the_arm_is_coerced_and_betrayal_stays_zero`
  (meeting 0, p-3 names p-2: SKIP, `teammate_coerced`, redirected from p-2, the marker,
  `not_assessed`; `check_no_betrayal` passes over the recorded game) and planted
  `test_without_the_coercion_the_betrayal_check_fails`.
- Labels, never rewrites: A `test_the_layer_labels_what_the_impostor_cites_and_records_it_as_cast`
  (EJECT citing p-4's accusation: `supported`; EJECT citing only an own sighting: recorded as
  cast), `test_an_impostor_skip_that_holds_nothing_labels_none_held`,
  `test_an_ungrounded_impostor_eject_is_tallied_like_any_other` (it decides the outcome) and
  planted `test_a_tally_that_dropped_the_ungrounded_eject_would_change_the_outcome`.
- Stamps: `tests/agents/test_bespoke_prompt_sets.py`
  `test_each_ballot_arm_serves_its_derived_stamp_on_vote_ballot_only` (either arm and the composite
  `vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1+vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1`;
  the `.v6` stamps unchanged), `test_no_ballot_arm_stamp_equals_a_default_or_overlay_stamp`,
  `test_the_ballot_arms_move_no_default_or_overlay_registry`,
  `test_the_ballot_header_keeps_the_v8_marker_and_names_both_arms`, and
  `test_a_pin_that_omits_an_arm_the_manager_renders_fails_the_one_source_check`; the spine's
  `test_every_registered_arm_serves_its_derived_stamp` now runs over the two real entries and its
  `test_a_hand_written_stamp_fails_the_derivation_test` stays the planted side.
- Refusals: A `test_the_profile_refuses_a_ballot_arm_beside_an_account_profile` (4 combinations),
  `test_the_runner_refuses_a_ballot_arm_beside_a_legacy_overlay` (8), adverse
  `test_each_arm_alone_and_both_with_the_rebuttal_and_reset_construct`,
  `test_the_runner_refuses_an_arm_for_a_set_whose_ballot_has_no_block`,
  `test_a_dead_guard_is_no_block`, `test_the_body_check_reads_the_template_the_arm_registers`,
  `test_a_pin_claiming_an_arm_on_another_set_fails_the_one_source_check`. No registry check wanted
  an environment name for every profile field, so no config-only allow-list was needed;
  `EXPERIMENT_ENV_NAMES` (four names) and `.env.example` are unchanged.
- Tripwire: A `test_an_arm_on_ballot_parses_to_exactly_its_suspicion_rows` (each arm and both,
  through `_parse_suspicion_graph` and `eval.validity._rendered_suspicions`),
  `test_a_template_copy_that_moves_the_header_parses_to_nothing` (a `## ` line inserted, the
  header edited), `test_the_tripwire_reads_crew_rows_on_the_scripted_arm_on_game`
  (`rendered_crew_rows > 0`), planted `test_a_railroaded_crew_row_on_an_arm_on_prompt_fails_the_tripwire`.
- Golden ON: A `test_the_golden_re_renders_every_ballot_of_the_arm_on_game` (every prompt of the
  scripted game re-renders through the composite stamp), planted
  `test_the_golden_fails_when_a_bound_arm_value_is_dropped` (each arm) and
  `test_a_byte_inside_an_on_block_fails_only_the_arm_on_recording` (green on both sample sets, red
  on the scripted game).
- Honesty: `tests/eval/test_evidence_honesty.py` registers the family in the drift test (the
  sentence is verbatim in the module and family docstrings, and the drifted sentence is rejected
  on both); A `test_each_carrier_moves_its_cell_by_exactly_one`,
  `test_the_confidence_floor_is_read_from_the_recording`, `test_the_roles_are_read_from_the_seed`,
  `test_a_ballot_by_a_player_with_no_rebuilt_memory_raises`, and on the scripted game
  `test_the_honesty_cells_count_the_scripted_ballots` (cell 4 equals the census's
  `ejections_carried_only_by_impostor_ballots`, 1 of 1).
- Census: A `test_the_census_reads_zero_breaching_rows_and_zero_teammate_targets` (through
  `scripts/publish_gameplay_census.py`'s `--set-dir` path) and planted
  `test_a_teammate_kill_row_in_an_impostor_prompt_raises_the_census`.
- Pending guard gone: `git grep -n WAVE_ARMS_PENDING -- '*.py'` prints nothing (exit 1). A
  `test_the_round_one_config_validates_plays_and_verifies_in_a_bare_shell`. Perturbed: the same
  test body run at the merge base (the base tree exported to scratch, run with its own code)
  fails: `Value error, experiment configuration sets ballot_kill_row_version=1, a Stage-B arm
  whose behaviour is not built yet; it stays refused until its arm card removes it from
  WAVE_ARMS_PENDING` (1 failed).
- OFF path byte-identical: Verification below.

### Verification at `92e8803a`

Re-measured Evidence (count-only, production path). The ballot-family rows come from
`uv run python scripts/measure_baseline.py replays/<set> --honesty --json`, once per set; the
rest from the scratch walk described under the committed-data twin (the evidence-honesty walk,
the accessor's predicate and the live `build_evidence_rows`), which prints counts keyed by set.

| cell | s9 | pooled, four sets |
|---|---|---|
| impostor ballots: EJECT / SKIP | 46 / 164 | 183 / 760 (943) |
| impostor EJECTs labelled `supported` / `off_target`; at confidence >= 0.6 | 44 / 2; 46 of 46 | 178 / 5; 182 of 183 |
| impostor SKIPs with `decision_basis` `none_held` | 95 of 164 | 440 of 760 |
| impostor SKIPs holding a citable row pointing toward a non-teammate | 163 of 164 | 759 of 760 |
| teammate-coerced impostor ballots | 1 | 13 |
| first-hand kill holders (ballots) | 4 | 31 |
| impostor holders of a teammate-kill sighting (teammate living) | 18 (12) | 87 (56) |
| kill records the per-subject budget drops | 0 of 4 | 1 of 32 |
| ejections whose confidence floor impostor ballots alone met | 0 of 90 | 0 of 411 |

The new family on the committed sets, the record card's "before" (cells 1-4 and 6, plus 5):

| cell | s9 | pooled |
|---|---|---|
| 1. impostor EJECT / SKIP | 46 / 164 | 183 / 760 |
| 2. EJECTs pointing toward (own turn) / another turn / neutral only / no valid citation | 26 (13) / 19 / 1 / 0 | 98 (47) / 83 / 2 / 0 |
| 3. EJECTs citing only neutral rows, over impostor EJECTs | 1 of 46 | 2 of 183 |
| 4. ejections carried by impostor ballots alone | 0 of 90 | 0 of 411 |
| 5. kill holders; their ballots citing the kill | 4; 3 of 4 | 31; 21 of 31 |
| 6. recorded teammate targets, over impostor ballots | 0 of 210 | 0 of 943 |

The pre-existing honesty families are equal to the merge base's on all four sets: the base JSON
came from `4b1e9a01` exported to scratch (`git archive`) and run with its own code; the comparison
reads every family and prints `families base=18 head=19 added=['ballot_conduct'] missing=[]
differing=[]` for each set.

Validation, each exit code captured directly:

| command | result |
|---|---|
| `uv sync --frozen` | exit 0 |
| the card's targeted pytest list | exit 0, 894 passed |
| `uv run lint-imports` | exit 0, 4 kept, 0 broken |
| `git grep -n WAVE_ARMS_PENDING -- '*.py'` | no output (exit 1) |
| `bash scripts/verify_samples.sh replays/<set>`, four sets | exit 0 each: 50, 50, 150, 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir replays/<set> --check`, four sets | exit 0 each |
| `uv run python scripts/measure_baseline.py replays/<set> --honesty --json`, four sets | exit 0 each; families above |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0 |
| `uv run python scripts/publish_gameplay_census.py --check` | exit 0 |
| `uv run python scripts/check_doc_facts.py` | exit 0 |
| `uv run python scripts/validate_task_docs.py` | exit 0 |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0, every check passed |
| `uv run pytest -m campaign` | exit 0, 336 passed |
| `scripts/build_demo_bundle.py --out <scratch>` at the base and at the head, `diff -r` of `data/` | empty diff (see below) |
| `bash scripts/check.sh` | exit 0: ruff, format, `lint-imports`, task docs, prompt sync, mypy; 9,753 passed, 20 skipped, 3 xfailed (297 s); frontend lint, typecheck, 559 tests in 20 files, build |

**The bundle.** The first diff was not empty: 9 files differed, every difference in
`created_at`, which the loader reads from each replay file's modification time
(`api/replay_loader.py` `_iso_mtime`); the exported base tree carries the export's times. With the
100 replay files byte-compared and their mtimes copied from the head checkout onto the export, the
base rebuild's `data/` equals the head's: `diff -r` exit 0, 0 lines. The shown bundle is unchanged.
No file under `api/` or `frontend/` changed, so `npm --prefix frontend test` and the Playwright
journey were not required; `check.sh` ran the frontend legs.

### Planted failures

Each probe was applied to a copy, run, and the file restored from the copy (sha256 checked).
Named demonstrations, `planted.py <probe> <selection>`:

- M27, the predicate drops the observation id, `tests/training/test_conviction_serving.py`:
  perturbed exit 1, 3 failed, 10 passed (the three accessor equality tests); restored exit 0, 13
  passed.
- M03, the kill loop's teammate `continue` deleted, `test_ballot_arms.py -k teammate`: perturbed
  exit 1, 2 failed (`test_every_non_teammate_record_makes_exactly_its_own_row`,
  `test_an_impostors_record_naming_its_teammate_makes_no_row`); restored exit 0, 7 passed.
- N02, the kill-row gate disabled, `-k 'witness or kill_row'`: perturbed exit 1, 6 failed and 2
  errors (the scripted game cannot cite a row it was not served); restored exit 0, 17 passed.
- M47, the persona guard without its role test, `-k 'crew_ballot or role'`: perturbed exit 1, 3
  failed (the sole-impostor test, the crew property and the planted-guard test); restored exit 0,
  5 passed.
- H13, the floor read as the literal 0.6, `-k floor`: perturbed exit 1, 2 failed (thresholds 0.2
  and 0.95); restored exit 0, 4 passed.
- The in-test planted legs listed under Acceptance evidence (the golden's forced gate, the
  census's planted row, the dead guard, the dropped arm value, the one-byte ON edit, the planted
  scan, the uncoerced ballot, the dropping tally, the railroaded row, the reworded row) each assert
  their failing side inside the test.

### Neutering and the bounded mutation pass

One pass over every production line, row and argument this card added or changed (N probes) and
the eight operator classes over the touched production modules (F filter, S swap, N comparison, C
constant for a role/kind/room/tick read, M message, T tuple member, B branch swap, L loaded source
to literal), run by `run_mutants.py` with the suites `tests/meetings/test_ballot_arms.py`,
`tests/meetings/test_weighing_channel.py`, `tests/agents/test_bespoke_prompt_sets.py`,
`tests/training/test_conviction_serving.py` and `tests/orchestrator/test_experiment_arms.py`
(`pytest -x -n 6`, so the counts stop at the first failure). 91 probes; 85 killed on the first
run; 6 survived: M01 and M42 are equivalent (reasons in the table); M31, M38, M43 and M44 were
killed by the cases in `92e8803a` and re-run. Restored: the same suites, 362 passed.

| id | class | module | probe | first run | after the kill round |
|---|---|---|---|---|---|
| N01 | neuter | manager | delete the `own_kill` class row | killed: 2 failed, 42 passed, 3 errors |  |
| N02 | neuter | manager | kill-row gate `if False` | killed: 2 failed, 42 passed, 3 errors |  |
| N03 | neuter | manager | drop the arm argument to `_own_channel_evidence_rows` | killed: 2 failed, 42 passed, 3 errors |  |
| N04 | neuter | manager | drop the profile arm at the manager's `build_evidence_rows` call | killed: 1 failed, 68 passed, 3 errors |  |
| N05 | neuter | manager | drop `voter_role` at the render call | killed: 3 failed, 74 passed |  |
| N06 | neuter | manager | drop `ballot_kill_row_version` at the render call | killed: 2 failed, 86 passed |  |
| N07 | neuter | manager | drop `impostor_ballot_version` at the render call | killed: 3 failed, 74 passed |  |
| M01 | N | manager | gate `== 1` to `is not None` | SURVIVED: 360 passed | SURVIVED (equivalent: the field is `Literal[1] | None`, so `== 1` and `is not None` agree on every legal value) |
| M02 | N | manager | gate `== 1` to `!= 1` | killed: 2 failed, 42 passed, 3 errors |  |
| M03 | F | manager | drop the kill loop's teammate `continue` | killed: 1 failed, 327 passed |  |
| M04 | S | manager | kill loop reads `vent_witness_records` | killed: 2 failed, 42 passed, 3 errors |  |
| M05 | C | manager | row order key tick to 0 | killed: 1 failed, 92 passed |  |
| M06 | C | manager | row room to `ADMIN` | killed: 2 failed, 73 passed |  |
| M07 | C | manager | row tick to 0 | killed: 2 failed, 73 passed |  |
| M08 | C | manager | row kind to `own_sighting` | killed: 1 failed, 88 passed |  |
| M09 | C | manager | row speaker to `p-1` | killed: 1 failed, 286 passed |  |
| M10 | C | manager | row citation to None | killed: 1 failed, 42 passed, 4 errors |  |
| M11 | M | manager | row description to a constant | killed: 2 failed, 42 passed, 3 errors |  |
| M12 | L | manager | `own_kill` class 0 to 1 | killed: 1 failed, 89 passed |  |
| M13 | C | manager | manager passes arm 1 to the assembler | killed: 2 failed, 88 passed |  |
| M14 | C | manager | render `voter_role` to CREWMATE | killed: 3 failed, 74 passed |  |
| M15 | S | manager | render kill-row value from the impostor field | killed: 1 failed, 99 passed |  |
| M16 | S | manager | render impostor value from the kill-row field | killed: 2 failed, 87 passed |  |
| M17 | T | render_contract | drop `own_kill` from `EvidenceRowKind` | killed: 1 failed, 89 passed |  |
| N08 | neuter | evidence_profile | profile validator `if False` | killed: 1 failed, 90 passed |  |
| M18 | T | evidence_profile | drop the kill-row field from the arm tuple | killed: 1 failed, 90 passed |  |
| M19 | T | evidence_profile | drop the impostor field from the arm tuple | killed: 1 failed, 91 passed |  |
| M20 | T | evidence_profile | drop `public_account_version` from the account tuple | killed: 1 failed, 90 passed |  |
| M21 | T | evidence_profile | drop `attributed_testimony_version` from the account tuple | killed: 1 failed, 92 passed |  |
| M22 | N | evidence_profile | arm filter `is not None` to `is None` | killed: 1 failed, 90 passed |  |
| M23 | M | evidence_profile | profile refusal message to a constant | killed: 1 failed, 90 passed |  |
| N09 | neuter | game | drop the kill-row registry entry | killed: 3 failed, 70 passed |  |
| N10 | neuter | game | drop the impostor registry entry | killed: 3 failed, 70 passed |  |
| M24 | S | game | kill-row entry re-bodies `accusation_round` | killed: 1 failed, 66 passed, 3 errors |  |
| N11 | neuter | game | drop the participants' kill channel | killed: 1 failed, 74 passed, 4 errors |  |
| M25 | S | game | participants test `MoveWitnessAgent` | killed: 1 failed, 175 passed |  |
| M26 | B | game | participants swap the conditional's branches | killed: 1 failed, 94 passed, 4 errors |  |
| N12 | neuter | game | accessor returns () | killed: 1 failed, 112 passed, 4 errors |  |
| M27 | C | game | predicate drops the observation id | killed: 1 failed, 75 passed, 4 errors |  |
| M28 | F | game | predicate drops the teammate guard | killed: 3 failed, 288 passed |  |
| M29 | F | game | predicate drops the provenance filter | killed: 1 failed, 177 passed |  |
| M30 | F | game | predicate drops the kill-action filter | killed: 2 failed, 166 passed |  |
| M31 | F | game | fellow set drops the provenance filter | SURVIVED: 360 passed | killed: 1 failed, 170 passed |
| M32 | F | game | overlay refusal drops the overlay condition | killed: 1 failed, 66 passed, 3 errors |  |
| M33 | T | game | overlay tuple drops `testimony_shapes` | killed: 1 failed, 122 passed |  |
| M34 | T | game | overlay tuple drops `impostor_roll_call` | killed: 1 failed, 96 passed |  |
| M35 | T | game | overlay tuple drops `reporter_reasoning` | killed: 1 failed, 109 passed |  |
| M36 | T | game | overlay tuple drops `corroboration_discipline` | killed: 1 failed, 94 passed |  |
| M37 | N | game | arms-on filter `is not None` to `is None` | killed: 2 failed, 83 passed |  |
| N13 | neuter | game | skip the body check | killed: 1 failed, 104 passed |  |
| M38 | L | game | body check reads `vote_ballot.j2` for every arm | SURVIVED: 360 passed | killed: 1 failed, 147 passed |
| M39 | C | game | body check reads `qwen3_6_27b` for every set | killed: 1 failed, 126 passed |  |
| N14 | neuter | game | one-source check `if False` | killed: 1 failed, 114 passed |  |
| M40 | N | game | one-source expected value inverted | killed: 2 failed, 46 passed, 3 errors |  |
| M41 | C | game | one-source check reads `qwen3_6_27b` for every set | killed: 1 failed, 125 passed |  |
| M42 | L | game | arm values literal `(1,)` for the annotation read | SURVIVED: 360 passed | SURVIVED (equivalent: both registered fields are `Literal[1] | None`, so the annotation read yields exactly `(1,)`) |
| M43 | M | game | one-source message to a constant | SURVIVED: 360 passed | killed: 1 failed, 165 passed |
| M44 | M | game | overlay refusal message to a constant | SURVIVED: 360 passed | killed: 2 failed, 80 passed |
| M45 | C | loader | body check drops the guard argument | killed: 1 failed, 127 passed |  |
| N15 | neuter | loader | loader drops `voter_role` | killed: 4 failed, 23 passed, 2 errors |  |
| N16 | neuter | loader | loader drops `ballot_kill_row_version` | killed: 1 failed, 99 passed |  |
| N17 | neuter | loader | loader drops `impostor_ballot_version` | killed: 2 failed, 87 passed |  |
| M46 | B | loader | body check raise branch inverted | killed: 1 failed, 66 passed, 3 errors |  |
| M47 | F | vote_ballot.j2 | persona guard drops the role test | killed: 1 failed, 100 passed |  |
| M48 | N | vote_ballot.j2 | header guard inverted | killed: 3 failed, 80 passed |  |
| M49 | B | vote_ballot.j2 | team block's teammate branch inverted | killed: 1 failed, 174 passed |  |
| N18 | neuter | evidence_honesty | drop the ballot fold call | killed: 1 failed, 352 passed |  |
| N19 | neuter | evidence_honesty | missing memory `continue` before the raise | killed: 1 failed, 355 passed |  |
| H01 | N | evidence_honesty | accusation `==` to `!=` | killed: 1 failed, 352 passed |  |
| H02 | F | evidence_honesty | drop the accusation type filter | killed: 1 failed, 354 passed |  |
| H03 | F | evidence_honesty | drop `target in flag.subjects` | killed: 1 failed, 354 passed |  |
| H04 | T | evidence_honesty | drop event a from the resolved pair | killed: 1 failed, 354 passed |  |
| H05 | T | evidence_honesty | drop event b from the resolved pair | killed: 1 failed, 354 passed |  |
| H06 | F | evidence_honesty | drop the impostor-voter filter | killed: 2 failed, 133 passed |  |
| H07 | N | evidence_honesty | SKIP test inverted | killed: 2 failed, 133 passed |  |
| H08 | F | evidence_honesty | drop the self-vote exclusion | killed: 1 failed, 354 passed |  |
| H09 | F | evidence_honesty | drop the turn-id membership test | killed: 1 failed, 354 passed |  |
| H10 | N | evidence_honesty | own-turn test inverted | killed: 1 failed, 354 passed |  |
| H11 | N | evidence_honesty | observation-id test inverted | killed: 2 failed, 133 passed |  |
| H12 | N | evidence_honesty | floor `>=` to `>` | killed: 1 failed, 357 passed |  |
| H13 | L | evidence_honesty | floor literal 0.6 | killed: 1 failed, 357 passed |  |
| H14 | N | evidence_honesty | EJECTED test inverted | killed: 1 failed, 352 passed |  |
| H15 | F | evidence_honesty | kill holders read the whole log | killed: 1 failed, 354 passed |  |
| H16 | F | evidence_honesty | drop the cited-id None test | killed: 1 failed, 354 passed |  |
| H17 | C | evidence_honesty | impostors literal `{p-2, p-3}` | killed: 1 failed, 141 passed |  |
| H18 | S | evidence_honesty | neutral-only denominator from impostor ballots | killed: 1 failed, 352 passed |  |
| H19 | S | evidence_honesty | teammate denominator from impostor EJECTs | killed: 1 failed, 352 passed |  |
| H20 | S | evidence_honesty | kill-citing denominator from impostor ballots | killed: 1 failed, 352 passed |  |
| H21 | S | evidence_honesty | carried denominator from impostor EJECTs | killed: 1 failed, 352 passed |  |
| H22 | S | evidence_honesty | other-turn cell reads the no-citation tally | killed: 1 failed, 352 passed |  |
| H23 | S | evidence_honesty | SKIP cell reads the EJECT tally | killed: 1 failed, 352 passed |  |

### Changed test expectations

- `tests/training/test_conviction_serving.py`: the three accessor equality assertions carry
  `observation_id`.
- `tests/orchestrator/test_experiment_arms.py`: deleted with the guard: `_open_the_guard`,
  `_PENDING`, `_PENDING_PROFILE`, `_unbuilt_values` and the tests
  `test_a_value_is_pending_exactly_while_its_behaviour_is_unbuilt`,
  `test_the_pending_guard_still_lists_an_arm`, `test_validation_refuses_a_pending_value`,
  `test_construction_refuses_a_pending_value_built_past_validation`,
  `test_the_runner_refuses_a_profile_carrying_a_pending_value`,
  `test_a_pinned_runner_still_refuses_a_pending_profile_value` and
  `test_the_lab_candidates_are_all_arms_that_exist_today` (vacuous once every value is built); the
  contract-page check no longer requires the page to name `WAVE_ARMS_PENDING`;
  `test_a_config_only_field_must_equal_the_runners_both_ways` builds its runner on `qwen3_6_27b`
  (the only set whose ballot carries the blocks); `test_the_runner_stamps_the_profile_it_renders`
  stubs the body check for its planted rebuttal entry.
- `tests/orchestrator/test_experiment_config.py`: `test_a_coerced_wave_version_is_refused_with_the_guard_open`
  renamed `test_a_coerced_wave_version_is_refused` without the patch; deleted with the unbuilt
  guard: `test_an_unbuilt_option_value_refuses_to_build_a_policy` and
  `test_the_factory_refuses_an_unbuilt_value_rather_than_running_the_default`.
- `tests/orchestrator/test_report_body_handle.py`: deleted `test_the_arm_is_no_longer_pending`.
- `tests/eval/test_vent_witness_readers.py`, `tests/experiments/test_vent_look_and_wait_game.py`,
  `tests/agents/test_vent_look_and_wait.py`: dropped the assertions that a name is not pending or
  that the unbuilt guard is empty.
- `tests/eval/test_recorded_arm_readers.py`: the builder probe is `_stop_at_the_builder` (same
  claim); `_PENDING_*` constants and two tests renamed `wave`; the golden half of
  `test_the_reconstructors_walk_every_meeting_of_a_copy_carrying_the_wave_values` now expects the
  copy's ballots NOT to reproduce while every turn prompt does: the golden renders the arms the
  rewritten settings name.
- `tests/meetings/test_prompt_byte_golden.py`: `test_a_recording_made_with_a_registered_arm_resolves_through_its_settings`
  stubs the body check for its planted rebuttal entry; one docstring; the new OFF leg.
- Vote-renderer doubles widened by the three keywords: `tests/meetings/_manager_helpers.py`,
  `tests/meetings/test_corroboration.py`, `tests/agents/test_beliefs.py`,
  `tests/orchestrator/test_meeting_integration.py`, `tests/orchestrator/test_replay_meetings.py`.
- `tests/eval/test_evidence_honesty.py`: `_CELL_OWNERS` gains `ballot-conduct`.

Files that dropped a pending-guard patch: `tests/eval/test_gameplay_census.py`,
`tests/eval/test_recorded_arm_readers.py`, `tests/eval/test_regroup_instruments.py`,
`tests/eval/test_replay_walk.py`, `tests/eval/test_validity.py`,
`tests/experiments/test_vent_look_and_wait_game.py`, `tests/orchestrator/test_experiment_arms.py`,
`tests/orchestrator/test_experiment_config.py`, `tests/scripts/test_scan_recording_packets.py`
(and a now-unused `monkeypatch` parameter where the patch was its only use).

### Closing greps

- `git grep -n WAVE_ARMS_PENDING -- '*.py'`: nothing. `git grep -n -i 'UNBUILT_OPTION\|UnbuiltTactical\|refuse_pending' -- '*.py'`: nothing.
- `git grep -n -i -E 'pending guard|wave_arms_pending|unbuilt_option|no kill channel|kill channel at all|two of the eight|two provenance channels|never reaches the meeting|registry is empty' -- ':!tasks' ':!audits' ':!agent_prompts'`:
  seven hits, none live-tense about the old behaviour: two in this card's test file (a past-tense
  banner and docstring), two in `tests/meetings/test_weighing_channel.py` qualified "with the
  kill-row arm OFF", two unrelated `test_manager.py` docstrings and one unrelated
  `training/README.md` line.

### Limitations

- The grounding bound is instructed, not enforced: the tally reads no grounding label (ruling D6),
  so an ungrounded impostor EJECT is recorded and tallied, and cell 3 counts it. "Say only what
  the cited line shows" is instructed too: the rationale row checks tokens, not propositions.
- `supported` means aboutness; the family's "points toward" is the stricter typed test (s9: 44
  impostor EJECTs labelled `supported`, 26 pointing toward).
- The kill row has no statistical power at 50 seeds (4 holder ballots on s9).
- The one-source check enumerates each registered field's `Literal` ON values; both are
  `Literal[1] | None` today.
- The body check requires a live guard in the served body; it does not decide whether the guarded
  lines are the right ones (the byte tests do).
- The committed-data twin is a scratch count, not a test: no committed-walk entry point exposes
  the rebuilt memories, and `tests/_helpers/committed.py` is outside this card.
- `scripts/measure_baseline.py`'s human-readable `--honesty` rendering does not print the new
  family (the JSON carries it); `scripts/` is outside this card.

### Review corrections, round 1 (2026-09-27)

Five blocking findings from the round-1 verifiers at `9b198d55` (two of them the same except
tuple, seen by two verifiers). Fix commit `318c99ed`: `eval/evidence_honesty.py` (the kill-citing
fold and the family docstring) and `tests/meetings/test_ballot_arms.py`; the commit after it
changes only this card. Every command below ran at `318c99ed` in a shell with no `AILIBI_*`
export.

**What changed.**
- **Kill citations in either own-id slot (docs verifier; Codex P2 on PR #491).** Reply to Codex:
  valid, and fixed the way it proposes rather than by narrowing the text. The ballot contract lets
  `counter_reason_id` carry one of the voter's own observation ids (the `counter_reason_id` bullet
  of `vote_ballot.j2`'s output format), and `meetings.manager._normalize_ballot_counter_reason_id`
  keeps it only when it is this meeting's turn or this voter's own observation, so a match is a
  real citation of the kill. `_fold_ballot_conduct` now counts a holder whose ballot names one of
  its kill records' observation ids in `primary_reason_observation_id` or `counter_reason_id`; the
  family docstring says so. Planted: the counter-slot carrier and the counter-names-a-turn carrier
  in `test_each_carrier_moves_its_cell_by_exactly_one`. No committed number moves: no committed
  holder ballot cites the kill only in the counter slot (the four honesty reports are
  byte-identical, below).
- **The per-turn filter (correctness verifier, V16).** New carrier: p-2's turn accuses p-7 and
  impostor p-3's EJECT of p-7 cites p-7's own turn, which accuses nobody. Expected: other turn +1,
  pointing toward unchanged. With the filter dropped the published s9 split moved to 35 / 10 (the
  verifier's measurement); the carrier now fails that mutant.
- **Absent or unparseable bodies (correctness and integrity verifiers, V01, V02, V03).** New
  `test_an_absent_or_unparseable_body_is_the_same_refusal_naming_the_file`, both arms: a set copy
  without `vote_ballot.j2`, and a set copy whose `vote_ballot.j2` ends in `{% if %}`; each must raise
  the check's `ValueError` naming the set and the file. V03 (drop `AttributeError`) is equivalent:
  `_environment_for_set` always builds the environment on a `FileSystemLoader`, so
  `environment.loader` is never `None` and `get_source` is always there.
- **Message arguments (correctness verifier, V04, V20, V21, V22).** The match patterns now carry
  the set name (`Prompt set 'qwen3_6_27b' template 'vote_ballot.j2' ...` and `Prompt set
  'qwen3_32b' ...`), the arm list and the account-profile list (per arm and account, plus a new
  case with both arms and both profiles that pins the order), and the meeting id
  (`headless-seed-26:meeting-2: ballot by 'p-9', ...`).

**Mutation pass, bounded to the spans the findings name and the span this round changed.** The
named operator classes only (F filter, T tuple member, M message argument, N comparison, S swap).
Suites: the five core suites (`tests/meetings/test_ballot_arms.py`,
`tests/meetings/test_weighing_channel.py`, `tests/agents/test_bespoke_prompt_sets.py`,
`tests/training/test_conviction_serving.py`, `tests/orchestrator/test_experiment_arms.py`) for the
loader and profile probes, and `tests/meetings/test_ballot_arms.py` with
`tests/eval/test_evidence_honesty.py` for the honesty probes; `pytest -q -n 6`, no `-x`. Each probe
was applied in place, run, and the file restored from a copy with its sha256 checked. First run:
the fixed production code with the test file of `9b198d55`; second run: the fixed test file.
Restored: the core suites 365 passed, the honesty pair 195 passed.

| id | class | module | probe | first run (tests of `9b198d55`) | with the round-1 tests |
|---|---|---|---|---|---|
| V16 | F | evidence_honesty | `_points_toward` drops the per-turn filter | SURVIVED: 192 passed | killed: 1 failed, 194 passed |
| V01 | T | loader | body-check except tuple drops `TemplateNotFound` | SURVIVED: 362 passed | killed: 2 failed, 363 passed |
| V02 | T | loader | body-check except tuple drops `TemplateSyntaxError` | SURVIVED: 362 passed | killed: 2 failed, 363 passed |
| V03 | T | loader | body-check except tuple drops `AttributeError` | SURVIVED: 362 passed | SURVIVED: 365 passed (equivalent, reason above) |
| V04a | M | loader | refusal's set name to `'X'` | SURVIVED: 362 passed | killed: 6 failed, 359 passed |
| V04b | M | loader | refusal's set name to `'qwen3_6_27b'` | SURVIVED: 362 passed | killed: 2 failed, 363 passed |
| V20 | M | evidence_profile | refusal's arm list to `['X']` | SURVIVED: 362 passed | killed: 5 failed, 360 passed |
| V20b | M | evidence_profile | refusal's arm list to `['ballot_kill_row_version']` | SURVIVED: 362 passed | killed: 3 failed, 362 passed |
| V21 | M | evidence_profile | refusal's account list to `['X']` | SURVIVED: 362 passed | killed: 5 failed, 360 passed |
| V21b | M | evidence_profile | refusal's account list to `['public_account_version']` | SURVIVED: 362 passed | killed: 3 failed, 362 passed |
| V22 | M | evidence_honesty | missing-memory raise's meeting id to `'m-x'` | SURVIVED: 192 passed | killed: 1 failed, 194 passed |
| K1 | T | evidence_honesty | kill-citing slots drop `counter_reason_id` | SURVIVED: 192 passed | killed: 1 failed, 194 passed |
| K2 | T | evidence_honesty | kill-citing slots drop `primary_reason_observation_id` | killed: 2 failed, 190 passed | killed: 2 failed, 193 passed |
| K3 | F | evidence_honesty | kill-citing slots drop the `None` filter | killed: 1 failed, 191 passed | killed: 1 failed, 194 passed |
| K4 | N | evidence_honesty | kill-citing filter `is not None` to `is None` | killed: 2 failed, 190 passed | killed: 2 failed, 193 passed |
| K5 | S | evidence_honesty | counter slot swapped for `primary_reason_id` | SURVIVED: 192 passed | killed: 1 failed, 194 passed |
| K6 | N | evidence_honesty | kill match `in` to `not in` | killed: 2 failed, 190 passed | killed: 2 failed, 193 passed |

17 probes. With the round-1 tests: 16 killed, 1 equivalent (V03). The probes that first came back
green were V16, V01-V04, V20, V21, V22 (the findings) and K1 and K5 (the new counter slot, before
its carrier existed). No other operator class was run.

**Verification at `318c99ed`.** Ballot rows re-measured count-only from the recorded ballots
through `eval.validity.roles_by_seed` (a scratch script keyed by set, printing counts only), the
family from `uv run python scripts/measure_baseline.py replays/<set> --honesty --json`:

| cell | s9 | pooled, four sets |
|---|---|---|
| impostor ballots: EJECT / SKIP | 46 / 164 | 183 / 760 (943) |
| impostor EJECTs labelled `supported` / `off_target`; at confidence >= 0.6 | 44 / 2; 46 of 46 | 178 / 5; 182 of 183 |
| impostor SKIPs with `decision_basis` `none_held` | 95 of 164 | 440 of 760 |
| teammate-coerced impostor ballots | 1 | 13 |
| ejections | 90 | 411 |
| family cell 2: pointing toward / another turn | 26 / 19 | 98 / 83 |
| family cell 4: ejections carried by impostor ballots alone | 0 of 90 | 0 of 411 |
| family cell 5: kill holders; their ballots citing the kill (either slot) | 4; 3 of 4 | 31; 21 of 31 |
| family cell 6: recorded teammate targets | 0 of 210 | 0 of 943 |

The four honesty reports at `318c99ed` are byte-identical (`cmp` exit 0) to the same command run
at `9b198d55` (that tree exported to scratch and run with its own code), so every family, the new
one included, is unchanged, and the earlier comparison with the merge base's 18 families carries
over. The rows of the `92e8803a` table that came from the earlier scratch walk over rebuilt
memories (SKIPs holding a pointing row, teammate-kill sighting holders, budget-dropped kill
records) were not re-measured: they read no code this round changed.

| command | result |
|---|---|
| the card's targeted pytest list | exit 0, 897 passed |
| `uv run lint-imports` | exit 0, 4 kept, 0 broken |
| `git grep -n WAVE_ARMS_PENDING -- '*.py'` | no output (exit 1) |
| `bash scripts/verify_samples.sh replays/<set>`, four sets | exit 0 each: 50, 50, 150, 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir replays/<set> --check`, four sets | exit 0 each |
| `uv run python scripts/measure_baseline.py replays/<set> --honesty --json`, four sets | exit 0 each; byte-identical to `9b198d55` |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0 |
| `uv run python scripts/publish_gameplay_census.py --check` | exit 0 |
| `uv run python scripts/check_doc_facts.py` | exit 0 |
| `uv run python scripts/validate_task_docs.py` | exit 0 (and again at the card commit) |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0 |
| `uv run pytest -m campaign` | exit 0, 336 passed |
| `uv run mypy eval/evidence_honesty.py tests/meetings/test_ballot_arms.py` | no issues |
| `scripts/build_demo_bundle.py --out <scratch>` before and after the fix, same checkout, `diff -r` of `data/` | exit 0, no output; the builder does not import `eval.evidence_honesty` |
| `bash scripts/check.sh` (clean tree at `318c99ed`) | exit 0: ruff, format, `lint-imports` (4 kept), task docs, prompt sync, mypy (518 files); 9,756 passed, 20 skipped, 3 xfailed (292 s); frontend lint, typecheck, 559 tests in 20 files, build |

**Changed test expectations.** None weakened, skipped or deleted. Tightened: the match patterns of
`test_the_profile_refuses_a_ballot_arm_beside_an_account_profile`,
`test_the_runner_refuses_an_arm_for_a_set_whose_ballot_has_no_block`,
`test_a_dead_guard_is_no_block` and `test_a_ballot_by_a_player_with_no_rebuilt_memory_raises`.
Added: three carriers in `test_each_carrier_moves_its_cell_by_exactly_one`,
`test_the_profile_refusal_names_every_arm_and_account_profile_it_met` and
`test_an_absent_or_unparseable_body_is_the_same_refusal_naming_the_file` (two cases).

**Closing greps.** `git grep -n -i -E "kill.{0,60}(primary[_ ]reason[_ ]observation|primary observation slot|primary slot)|(primary[_ ]reason[_ ]observation|primary observation slot).{0,60}kill" -- '*.py' '*.md' ':!replays' ':!audits' ':!agent_prompts'`:
two hits, both unrelated test lines (`tests/meetings/test_ballot_observation_citation.py`,
`tests/meetings/test_vote_guard_rationale.py`); no sentence says the family reads only the primary
slot. `git grep -n -i -E "absent or unparseable|unparseable or absent" -- '*.py' '*.md' ':!replays'`:
the two loader docstrings, now both pinned.

**Limitation added.** The census's own-kill cell `own_kill_rows_cited_by_holder`
(`eval/gameplay_census.py`, the census card's file, not written here) reads only
`primary_reason_observation_id`, while its definition says "cites the row's observation". The
honesty cell now reads both slots, so the two can differ once an arm-ON record holds a counter-slot
kill citation; on committed data both read nothing from the counter slot. Noted for the census
owner and the record card.

### Review corrections, round 2 (2026-09-27)

Six blocking findings from the round-2 verifiers at `07282a4e`, five distinct probes: the
correctness verifier's R05 and the docs verifier's cell-4 finding are the same mutant. All five are
listed-class survivors in `eval/evidence_honesty.py` that no carrier pinned; the code already did
what the family sentence says, so no production byte changes. Fix commit `173139cb` edits only
`tests/meetings/test_ballot_arms.py`; the commit after it changes only this card. Every command
below ran at `173139cb` in a shell with no `AILIBI_*` export.

**What changed.** New carriers in `test_each_carrier_moves_its_cell_by_exactly_one`, all on the
scripted game's third meeting (impostors p-2 and p-3 eject p-7 at 0.9; recorded floor 0.6):
- **Classification order (R07, correctness verifier).** Impostor p-2's EJECT keeps its own
  observation `p-2:1:12` and also cites a turn of this meeting. Citing p-7's turn, which points
  nowhere, moves another turn +1 and neutral only -1; citing its own turn accusing p-7 moves
  pointing toward +1, own turn +1 and neutral only -1. The family docstring's order (a turn first,
  then an own observation) is now enforced; with the branches swapped the published s9 cell 3 would
  read 17 of 46 instead of 1 of 46 (the verifier's measurement), consistent with the count-only
  population below.
- **The ejected-target filter in cell 4 (R05, correctness verifier; the docs verifier's cell-4
  finding; P3, integrity verifier).** Crew p-1 voting p-9 at 0.9, or SKIP at 0.9, leaves
  `ejections_carried_by_impostors_alone` unchanged; crew p-1 voting p-7 at 0.9 lowers it by one.
  Both mutants could only lower a count that reads 0 of 411 on committed data, so no published
  value was at risk; the family sentence ("ballots for the ejected player") is now enforced.
- **An accusation against somebody else (Q1, integrity verifier).** p-7's turn carries a typed
  accusation against p-9 and impostor p-3's EJECT of p-7 cites it: another turn +1, pointing toward
  unchanged. With the mutant the published s9 split would read 45 / 0 instead of 26 / 19 (the
  verifier's measurement).
- **A contradiction minted from other turns (Q4, integrity verifier).** A new conflict-loop entry:
  a contradiction naming p-7 whose two event ids resolve to p-9's and p-1's turns, while the cited
  turn (p-7's) accuses nobody: another turn +1, pointing toward unchanged. The loop's assertion
  message now names both event ids, since two entries share the subjects `("p-7",)`.

**Count-only population for the R07 carrier.** Impostor EJECTs whose recorded
`primary_reason_id` names a turn of the meeting and whose `primary_reason_observation_id` is set:
16 of 46 on s9 and 61 of 183 pooled (samples/4p1i 1 of 6, ml_corpus/9p2i 43 of 121, ml_corpus/4p1i
1 of 10). A scratch script over the recorded ballots, roles through `eval.validity.roles_by_seed`
with `resolve_roster_knobs`, printing counts keyed by set only.

**Mutation pass, bounded to the spans the findings name.** The card's operator letters (F drop a
filter, S swap one collection for a related one, N comparison to a None test or its inverse, B swap
adjacent branches). Suites: `tests/meetings/test_ballot_arms.py` and
`tests/eval/test_evidence_honesty.py`, `pytest -q -n 6`, no `-x`. Each probe was applied in place,
run, and `eval/evidence_honesty.py` restored from a copy with its sha256 checked; restored, the pair
reads 195 passed after each run. First run: the test file of `07282a4e`; second run: the test file
of `173139cb`. The last column names the assertion that fails first under the probe (a single-test
run with `--tb=line`).

| id | class | probe | first run (tests of `07282a4e`) | with the round-2 tests | first failing assertion |
|---|---|---|---|---|---|
| R07 | B | classification swaps the turn branch and the own-observation branch | SURVIVED: 195 passed | killed: 1 failed, 194 passed | p-2 cites p-7's turn and keeps its observation |
| R07b | B | pointing-toward and other-turn bodies swapped | killed: 2 failed, 193 passed | killed: 2 failed, 193 passed | |
| R07c | F | drop the turn-id membership test | killed: 1 failed, 194 passed | killed: 1 failed, 194 passed | |
| R07d | N | own-observation test `is not None` to `is None` | killed: 3 failed, 192 passed | killed: 3 failed, 192 passed | |
| R05 | F | carried list keeps only the confidence filter | SURVIVED: 195 passed | killed: 1 failed, 194 passed | crew p-1 votes p-9 at 0.9 |
| R05b | F | carried list drops the confidence filter | killed: 5 failed, 190 passed | killed: 5 failed, 190 passed | |
| R05c | F | drop the non-empty test before `all` | killed: 1 failed, 194 passed | killed: 1 failed, 194 passed | |
| R05d | S | impostor set swapped for the roles mapping | killed: 1 failed, 194 passed | killed: 2 failed, 193 passed | |
| P3 | N | ejected-target test to `ballot.target is not None` | SURVIVED: 195 passed | killed: 1 failed, 194 passed | crew p-1 votes p-9 at 0.9 |
| P3b | N | ejected-target `==` to `!=` | killed: 4 failed, 191 passed | killed: 4 failed, 191 passed | |
| Q1 | N | accusation `claim.against == target` to `is not None` | SURVIVED: 195 passed | killed: 1 failed, 194 passed | the cited turn accuses p-9 |
| Q1b | N | accusation `==` to `!=` | killed: 2 failed, 193 passed | killed: 2 failed, 193 passed | |
| Q4 | F | drop the per-turn conjunct on the contradiction branch | SURVIVED: 195 passed | killed: 1 failed, 194 passed | the contradiction minted from p-9's and p-1's turns |
| Q4b | N | subjects `in` to `not in` | killed: 1 failed, 194 passed | killed: 1 failed, 194 passed | |
| Q4c | F | drop the subjects filter | killed: 1 failed, 194 passed | killed: 1 failed, 194 passed | |

15 probes, all killed with the round-2 tests. The probes that first came back green were exactly
the five the findings name (R07, R05, P3, Q1, Q4); the other ten are neighbours in the same spans,
killed on both runs. The crew-SKIP carrier sits after the p-9 carrier in the same loop, so no probe
reached it first; it is not claimed as a killer. No other operator class was run.

**Verification at `173139cb`.** No production path changed since `318c99ed` (`git diff --stat
318c99ed 173139cb` names only `tests/meetings/test_ballot_arms.py`), so no committed number can
move; the family was re-measured anyway with
`uv run python scripts/measure_baseline.py replays/<set> --honesty --json` on the four sets and
equals the round-1 table cell for cell:

| cell | s9 | pooled, four sets |
|---|---|---|
| impostor ballots: EJECT / SKIP | 46 / 164 | 183 / 760 (943) |
| ejections | 90 | 411 |
| family cell 2: pointing toward (own turn) / another turn | 26 (13) / 19 | 98 (47) / 83 |
| family cell 3: EJECTs citing only a neutral row | 1 of 46 | 2 of 183 |
| family cell 4: ejections carried by impostor ballots alone | 0 of 90 | 0 of 411 |
| family cell 5: kill holders; their ballots citing the kill (either slot) | 4; 3 of 4 | 31; 21 of 31 |
| family cell 6: recorded teammate targets | 0 of 210 | 0 of 943 |

| command | result |
|---|---|
| the card's targeted pytest list (`-n 6`) | exit 0, 897 passed (the carriers sit inside one existing test) |
| `uv run lint-imports` | exit 0, 4 kept, 0 broken |
| `git grep -n WAVE_ARMS_PENDING -- '*.py'` | no output (exit 1) |
| `uv run mypy tests/meetings/test_ballot_arms.py eval/evidence_honesty.py` | no issues |
| `bash scripts/verify_samples.sh replays/<set>`, four sets | exit 0 each: 50, 50, 150, 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir replays/<set> --check`, four sets | exit 0 each |
| `uv run python scripts/measure_baseline.py replays/<set> --honesty --json`, four sets | exit 0 each; the family as tabled above |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0 |
| `uv run python scripts/publish_gameplay_census.py --check` | exit 0 |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0 |
| `uv run pytest -m campaign` | exit 0, 336 passed |
| `scripts/build_demo_bundle.py --out <scratch>` with only the test file changed from `07282a4e` and again at `173139cb`, `diff -r` of `data/` | exit 0, no output; the builder reads no `tests/` path |
| `bash scripts/check.sh` (clean tree at `173139cb`) | exit 0: ruff, format (547 files), `lint-imports` (4 kept), task docs, prompt sync, mypy (518 files); 9,756 passed, 20 skipped, 3 xfailed (292 s); frontend lint, typecheck, 559 tests in 20 files, build |
| `uv run python scripts/check_doc_facts.py`, `uv run python scripts/validate_task_docs.py` | exit 0 each, at the card commit |

**Changed test expectations.** None weakened, skipped or deleted. Added, all inside
`test_each_carrier_moves_its_cell_by_exactly_one`: seven carrier assertions (Q1 one, R07 two, Q4
one conflict-loop entry, cell 4 three, two of them in one loop) and two precondition assertions
(p-2's recorded observation id is set; the third meeting ejects p-7 under the recorded floor 0.6). Changed: the
conflict loop's assertion message, from the subjects alone to the subjects and both event ids.

**Closing greps.** No behaviour or vocabulary changed this round, so no old-behaviour sentence can
be stale. The sentences the carriers now enforce, `git grep -n -i -E "ballots for the ejected
player|minted a contradiction of this|classified by its primary citations" -- '*.py' '*.md'
':!replays' ':!audits' ':!agent_prompts'`: `eval/evidence_honesty.py` lines 91, 94, 539, 542, 940,
943 and 950 (the module text, the `CELL_DEFINITIONS` sentence and the family docstring) and the new
test comment at `tests/meetings/test_ballot_arms.py:2138`; each states what the code does, at that
strength.
