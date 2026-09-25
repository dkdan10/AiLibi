# B6: the witnessed-kill ballot row (R8) and the strategic impostor ballot (R10)

**Status:** ready

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

- [ ] **The kill record moves and carries its id.** `KillWitnessRecord` moves to
  `meetings/schemas.py` beside `VentWitnessRecord` as a `_FrozenModel` with
  `observation_id: ObservationId | None = None`; `orchestrator.game` re-exports it, so
  `training/conviction/serving.py` and `tests/training/test_composed_runner.py` import it unchanged;
  the accessor passes `observation_id=event.observation_id` and keeps its teammate guard. Mechanism:
  the field, the accessor and the re-export. Proof: the equality assertions at
  `tests/training/test_conviction_serving.py:378-380` and `:409-411` (memo 2.5 item 6; also
  `:437-439` if it compares records) carry the id, and the conviction parity pin passes unchanged.
  Planted: an accessor that drops the id fails them.
- [ ] **A witness gets exactly one row.** Mechanism: an optional `@runtime_checkable`
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
- [ ] **A voter who was only told gets nothing.** A `TacticalAgent` whose store holds only a
  reported `saw_kill` statement (`absorb_reported_testimony`) returns `()` from the accessor and
  gets no `own_kill` row. Mechanism: the accessor's observed-provenance filter. Planted: the same
  event written with observed provenance produces the row.
- [ ] **The teammate firewall holds at assembly.** Mechanism: `if record.subject in teammates:
  continue` in the kill loop, as in the vent, sighting and transit loops. Proof, with records
  passed directly so the assembly guard is what is proven: an impostor with
  `fellow_impostor_ids=("p-3",)` and a record naming p-3 gets no row, while the identical records
  on a crewmate keep it (the `test_the_identical_records_on_a_crewmate_keep_every_row` pattern,
  `tests/meetings/test_weighing_channel.py:1710`). Planted: deleting the new `continue` fails the
  impostor case. Committed-data twin, count-only, arm forced ON through an existing
  `tests/_helpers/committed.py` entry point: the impostor holders of a teammate-kill sighting (87
  pooled, re-measured) get 0 `own_kill` rows; if no entry point fits, a scratch count in Results.
- [ ] **Old recordings render identically.** With the arm OFF and kill records present,
  `build_evidence_rows` returns today's tuple and the golden re-renders every committed s9 and s4
  ballot byte-identically. Mechanism: the profile gate. Planted, in the golden: with the gate
  forced ON the golden fails at the committed kill-holder meetings (re-measured, named in Results),
  so the OFF gate is not vacuous.
- [ ] **No flag, no ledger, no belief.** With the arm ON, `detect_contradictions`, the testimony
  ledger and the belief fold equal OFF on a meeting with kill records. Mechanism: the record reaches
  the assembler only, and `TestTheAssemblerCannotReachTheLedger`
  (`tests/meetings/test_weighing_channel.py:1549`) adds every new helper to `_ASSEMBLER`. Planted:
  a helper passing kill records to `build_testimony_ledger` fails the scan.
- [ ] **Crew bytes.** Under `ballot_kill_row_version=1`, a ballot with no kill record differs from
  OFF only in the suspicion-header sentence, which becomes (proposed): "And it is only a PARTIAL
  summary of the lines above: someone you saw near a body just before you found it moves these
  numbers with no line of its own up there — your memory block above still carries that."
  `_PARTIAL_SUMMARY_CLAIM` stays verbatim, and the test at `:2087` keeps pinning the OFF body.
  Under `impostor_ballot_version=1` every crew ballot is byte-identical to OFF. Mechanism: the
  guards, whitespace-controlled. Planted: an impostor block whose guard omits the role test changes
  a crew ballot and fails.
- [ ] **The role reaches every impostor.** `voter_role` is an additive defaulted keyword on
  `VotePromptRenderer` and `vote_ballot_prompt`, passed by the manager's vote render call from
  `participant.role`, beside the two arm values from the manager's evidence profile; every other
  prompt set ignores them. Mechanism: the keyword and the guard. Proof: under the arm an impostor
  with `fellow_impostor_ids=()` (the 4p1i shape) renders the strategy text. Planted: with
  `voter_role` withheld the same voter renders the crew text and the test fails.
- [ ] **The impostor wording, tightened and neutral.** Under `impostor_ballot_version=1`, for
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
- [ ] **The firewall under the impostor arm.** A scripted impostor ballot naming its teammate,
  rendered through the arm, is recorded as SKIP with `guard_rewrite_reason="teammate_coerced"`, its
  marker and label `not_assessed`, and `check_no_betrayal` passes. Mechanism: the unchanged
  coercion. Planted: with the coercion monkeypatched to identity, `check_no_betrayal` fails.
- [ ] **The meeting layer labels and never rewrites.** An impostor EJECT citing an accusation turn
  against its target labels `supported`; an impostor SKIP with no ids labels `none_held`; a scripted
  impostor EJECT citing only its own sighting of the target is recorded as cast, tallied for that
  target and counted in the compliance cell below. Mechanism: the role-blind labeller and the
  label-blind tally (D6). Planted: a tally patched to drop the ungrounded EJECT changes the scripted
  outcome and the test fails.
- [ ] **Stamps, derived and never a default.** The spine's experiment-arm registry gains exactly
  two entries, `ballot_kill_row_version` and `impostor_ballot_version`, each re-bodying
  `vote_ballot` only. Mechanism: the spine's derivation function and fold. Proofs in
  `tests/agents/test_bespoke_prompt_sets.py`: either arm serves its derived stamp; both serve
  `vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1+vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1`
  (memo 3.3); the `.v6` stamps are unchanged; no arm stamp equals a default or overlay stamp; the
  first header marker stays v8 (`TestVersionMarkersMatchTheRegistry`, `:1012`), the header prose
  names both arms by field name, and `PROMPT_VERSION_SETS`, `DEFAULT_PROMPT_VERSIONS` and the four
  overlay registries are unchanged. Planted: a hand-written suffix fails the derivation test; a
  runner whose served stamps omit an arm its manager renders fails the one-source check.
- [ ] **Refusals.** `MeetingEvidenceProfile` validation refuses either ballot arm with
  `public_account_version` or `attributed_testimony_version`; `build_default_meeting_runner`
  refuses either arm while `impostor_roll_call`, `reporter_reasoning`, `corroboration_discipline`
  or `testimony_shapes` is ON, beside the account-mode refusal (`orchestrator/game.py:1388-1403`),
  in plain words. Mechanism: the validator and the runner check. Planted: each combination raises.
  Adverse: each arm alone, and both with the rebuttal and the reset, construct.
  `EXPERIMENT_ENV_NAMES` and `.env.example` are unchanged; if a registry check wants an env name
  for every profile field, a config-only allow-list lands with a planted case (memo 2.5 item 6).
- [ ] **The railroad tripwire cannot go vacuous.** A ballot rendered with each arm ON, and with
  both, parses through `_rendered_suspicions` and `_parse_suspicion_graph` to exactly the rows of
  the suspicion graph it was given (one per living player in the scripted case), and on the
  scripted arm-ON recording `check_no_railroaded_crew_ejections` reports `rendered_crew_rows > 0`.
  Mechanism: the header and the row shape stay intact under both guards. Planted: a template copy
  whose ON block edits the header, or puts a `## ` line between the header and the rows, parses
  to zero rows and fails; an arm-ON prompt with a crew row at 1.00 and two same-meeting flags
  naming that crewmate fails the check.
- [ ] **The golden covers the ON body.** Called on a scripted both-arms-ON recording in
  `tmp_path` (the readers card's directory walk and `tests/_helpers/scripted_meeting.py`, to which
  this card adds its ballot cases), the golden re-renders every ballot byte-identically through the
  arm stamps. Mechanism: the readers card's arm-stamp resolution over this card's registry entries.
  Planted: dropping a bound arm value fails it; a one-byte edit inside an ON block leaves the
  golden on s9 and s4 green and fails it on the scripted recording.
- [ ] **Evidence-honesty cells.** `eval/evidence_honesty.py` gains one ballot family with its own
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
- [ ] **The census reads 0 by construction on a scripted arm-ON game.** One end-to-end test in this
  card's own test file folds the scripted game through the census's `--set-dir` path: "own-kill
  rows naming a teammate or held by a non-witness" reads 0 over a non-empty denominator, and
  "recorded teammate ballot targets" reads 0. Mechanism: the census conformance fold over the
  served rows. Planted: a copy whose impostor ballot prompt carries an `own_kill` row naming its
  teammate raises the census conformance error.
- [ ] **The pending guard is gone.** With B0, B1 and B4 merged, this card's two names are the last
  in `WAVE_ARMS_PENDING`. It deletes them, then the mapping, its checks at config validation, at
  `HeadlessGame` construction and in `build_default_meeting_runner`, and the refusal test;
  `git grep -n WAVE_ARMS_PENDING -- '*.py'` prints nothing and every test that patched the mapping
  drops the patch (files named in Results). Mechanism: deletion (craft rule 3). Proof: a test
  validates the round-1 config literal (memo section 1) as a `RecordedExperimentConfig`, constructs
  a fake-provider `HeadlessGame` from it in a bare environment, plays one seed to its end and loads
  it through `ReplayLoader` with `outcome_verified` true. Perturbed: the same test at the merge
  base, where the guard still refuses the two ballot values, fails; Results quotes the failure.
- [ ] **The OFF path is byte-identical.** Mechanism: default `None`, the omitted key and the
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

Not started. The implementer records here and in the PR: the sections relied on
(`docs/architecture.md` "Enforced boundaries" and "Explicit cleanup experiments", with the spine's
arm page `docs/experiment-arms.md` it links; memo 0.2, 0.3, 2.5, 3.4); the six decisions and the runner-region follow-through; the
meetings the planted OFF leg failed at; the new honesty cells and re-measured Evidence counts with
their commands; every planted failure's red output; every Validation command's exit code; the
bundle diff; the files that dropped a pending patch; and the limitations.
