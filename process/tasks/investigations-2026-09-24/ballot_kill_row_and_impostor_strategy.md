# B6 — the ballot's witnessed-kill row and the impostor's strategic ballot

Investigator memo, 2026-09-24. Read-only on `main` at `e886b663` (baseline 9). No
model call, no recorder, no held-out band, nothing committed, no tracked file
edited. Every census below is count-only, keyed by (set, meeting). File:line
citations are at `e886b663`.

Card B6 carries two rulings in ONE `vote_ballot` revision (v8 to v9):
R8 (a witnessed kill becomes an own-evidence row in the voter's weighing channel;
no public flag) and R10 (impostor ballots express strategy, bounded by the same
grounding rule as crew).

---

## 0. The answer in ten lines

1. **The kill channel already exists, one layer short of the ballot.**
   `KillWitnessRecord` (`orchestrator/game.py:3510-3531`) and
   `TacticalAgent.kill_witness_records_for_meeting()` (`orchestrator/game.py:4074-4134`)
   project first-hand witnessed kills, with the teammate guard already applied
   (`:4126-4130`). They feed only the training conviction assembler
   (`training/conviction/serving.py:83-84,136,240`). They carry no observation id,
   and the meeting layer has no kill channel at all (`meetings/manager.py:3776-3786`,
   `meetings/render_contract.py:467-474`). B6 threads that record onto
   `MeetingParticipant`, adds an `observation_id`, and builds one `own_kill` row per
   record in `_own_channel_evidence_rows` (`meetings/manager.py:3443-3559`).
2. **The kill row is tiny in volume.** On baseline 9, 31 living-voter ballots at 30
   meetings held a first-hand kill sighting (9p2i: 30 at 29). All 31 were crew.
   24 of them (at 23 meetings) held one on a killer still alive at the meeting. On
   samples/9p2i alone: 4 ballots at 4 meetings. It cannot be assessed for effect on
   50 seeds, only for presence.
3. **The teammate case is real, not hypothetical.** 87 impostor ballots
   (56 with the teammate still living) held a sighting of their own teammate's kill.
   The accessor drops them today, and the assembly must drop them again.
4. **R10's grounding bound is almost never binding.** Of the 760 impostor SKIPs,
   760 held a citable row about some non-teammate candidate. 759 held a citable row
   pointing toward one: someone spoke against them, or a flag names them.
   So the v9 wording, not the grounding rule, decides how often impostors EJECT.
5. **Recommended wording.**
   - Crew bytes change only where a kill row exists and in one sentence under the
     suspicion header.
   - Impostor bytes lose the belief framing that makes SKIP the only consistent
     answer (`vote_ballot.j2:150`). The team block (`:289-291`) gains one
     honest-citation paragraph.
   - The confidence sentence is left alone: 182 of 183 impostor EJECTs already
     carry confidence 0.6 or more.
6. **Recommended gate.**
   - Ship the change as a default-OFF experiment-profile arm, following the
     `bounded_rebuttal_version` precedent (`meetings/evidence_profile.py:67-110`,
     `orchestrator/experiment_config.py:29-45`). Its ON stamp is literally
     `vote_ballot.qwen3_6_27b.v9`. The default registry stays at v8 until the owner
     adopts.
   - Do not use an env lever: the replay loader refuses a lever-ON replay in a bare
     environment (`api/replay_loader.py:745-777`), and `verify_samples.sh` loads
     through it (`scripts/_verify_samples.py:132`).
7. **The partial-record hypothesis holds for B6 on that route, except at five named
   gates** that assume the four sets share one substrate or one stamp (section 5).
   The main one is `scripts/check_doc_facts.py:2257-2266`, enforced by
   `tests/scripts/test_check_doc_facts.py:373-374`.

---

## 1. What exists today

### 1.1 A seen kill, from engine to memory

- **Engine.** Kill witnesses are the living players outside vents in the room,
  minus the killer and the victim (`engine/rules.py:29-44`, `:97-104`). A fellow
  impostor is therefore a witness. Of 849 kills pooled, 20 had a crew witness and
  50 had an impostor-teammate witness.
- **Observation.** Each witness gets a `PlayerView(action="kill")`
  (`observation/service.py:282-290`, `:542-547`).
- **Beliefs.** The witnessed-kill pin adds +1.0 to suspicion, and skips a teammate
  (`agents/memory/beliefs.py:1118-1147`).
- **Memory render.** The line reads "You witnessed {p} kill in {room}." and carries
  the observation id, so a seen kill is already citable (`agents/memory/store.py:2243-2249`).
  An impostor's view of a teammate at a kill is suppressed
  (`agents/memory/store.py:1331-1395`).
- **Typed accessor.** `kill_witness_records_for_meeting` exists (Task 18.30) and
  applies the §4.7 teammate guard itself. It is deliberately off the
  `MeetingAwareAgent` protocol, and `KillWitnessRecord` has no `observation_id`
  (`orchestrator/game.py:3510-3531`, `:4074-4134`).
- **What the ballot says today.**
  - The assembler says a witnessed kill has no row (`meetings/manager.py:3776-3786`).
  - The render contract says so too (`meetings/render_contract.py:467-474`).
  - The served body tells the voter that "a kill you watched happen" moves the
    number "with no line of its own" (`vote_ballot.j2:271`).
  - A test pins that sentence (`tests/meetings/test_weighing_channel.py:2087-2111`).
- **Other surfaces.** `meetings/corroboration.py:340-352` says `KillWitnessRecord`
  never reaches the meeting layer or the testimony ledger. After B6 it reaches the
  weighing channel only, still not the ledger.

### 1.2 The weighing channel (ruling D5)

- **Assembler.** `build_evidence_rows` (`meetings/manager.py:3749-3892`) builds rows
  from typed inputs only: the voter's own channels, the meeting's flags and the typed
  accusations.
- **Own-channel builder.** `_own_channel_evidence_rows` (`:3443-3559`) drops every row
  naming a fellow impostor (`:3483`, `:3501`, `:3524`).
- **Order and budget.** Row kinds sort into classes, and the order encodes
  "provenance, never strength" (`:3409-3422`). The budget is 8 rows per
  (subject, class), and it drops the earliest arrivals (`:3407`, `:3862-3889`).
- **Kind vocabulary.** `meetings/render_contract.py:131-150`.
- **Template.** The template only loops. An `own_*` row renders "first-hand: you saw
  this yourself; cite `<id>`" (`vote_ballot.j2:260-268`).

### 1.3 The impostor's ballot today

- **One template for both roles.** The belief framing is the persona sentence
  (`vote_ballot.j2:150`): "name the one player you believe is one of the impostors,
  or SKIP ... vote the conclusion you actually reach". An impostor believes exactly
  its teammates are impostors, and it may not vote them. So SKIP is the only answer
  consistent with that sentence.
- **Team block.** "Never vote a teammate — if your suspicion lands on one, set target
  to SKIP" (`:289-291`). It renders only when `fellow_impostor_ids` is non-empty, so a
  SOLE impostor (4p1i) gets the crew text word for word. The vote renderer receives
  no role (`meetings/render_contract.py:482-500`,
  `agents/strategic/prompts/loader.py:1026-1048`).
- **Firewall layers:**
  - `coerce_teammate_ballot_to_skip` (`meetings/manager.py:4349-4421`, with typed
    reason `teammate_coerced` and a marker);
  - the hard validity row `check_no_betrayal` (`eval/validity.py:759-820`), pinned
    with planted failures (`tests/eval/test_validity.py:348-385`);
  - `tests/meetings/test_manager.py:1594-1705` (`TestTeammateGuardHelpers`,
    `TestTeammateGuardOnProductionPath.test_no_impostor_ejected_by_teammate_betrayal_vote`);
  - `tests/orchestrator/test_meeting_integration.py:1800-1940`.
  - Task 7.12 commits: `60257403` and `e69e601f` (merged in #105); `04214220` later kept the teammate out of the ballot evidence.
- **Grounding labeller.** `label_ballot_grounding` (`meetings/manager.py:4451-4568`)
  is role-blind. Its vocabulary is `not_assessed`, `supported`, `off_target`,
  `invalid_citation`, `none_held`, `flag_only` and `uncited`
  (`meetings/schemas.py:943-951`). It never rewrites a target, and the tally never
  reads it (`meetings/voting.py:192-240`).
- **What `supported` means.** It means aboutness: the cited line names the target
  (`meetings/citation_relevance.py:143-189`). It does not mean incrimination.
- **Tally.** SKIP is a real tally target, and SKIP wins ties at the top
  (`meetings/voting.py:214-217`). So impostor SKIPs today pull meetings toward SKIP.
- **Marker chain.** B6 adds no guard and no marker. So the three marker mirrors stay
  byte-identical:
  - `eval/deduction_metrics.py:718-728`;
  - `api/replay_loader.py:3620-3630`;
  - `training/surrogate/dataset.py:201-213`.

---

## 2. Census on baseline 9 (count-only)

Method: the verified replay walk (`eval.replay_walk.walk_replay` with the
evidence-honesty profile). Each agent's episodic memory is rebuilt through the real
perception path, a mirror of the golden's `_ingest_tick`. At each recorded meeting,
the LIVE `build_evidence_rows` runs for every voter over the recorded transcript and
flags. Scripts are in section 10.

| | s9 | c9 | s4 | c4 | 9p2i | pooled |
|---|---|---|---|---|---|---|
| ballots (crew / impostor) | 635 / 210 | 1888 / 651 | 78 / 39 | 86 / 43 | 2523 / 861 | 2687 / 943 |
| voter-ballots holding a first-hand kill sighting of a non-teammate (all crew) | 4 | 26 | 1 | 0 | 30 | 31 |
| ... at meetings | 4 | 25 | 1 | 0 | 29 | 30 |
| ... with the killer alive at the meeting (ballots / meetings) | 3 / 3 | 20 / 19 | 1 / 1 | 0 | 23 / 22 | 24 / 23 |
| kill-sighting holders who voted the killer / SKIP / someone else | 3 / 0 / 1 | 19 / 3 / 4 | 1 / 0 / 0 | – | 22 / 3 / 5 | 23 / 3 / 5 |
| kill rows the per-subject budget of 8 would drop | 0 | 1 | 0 | 0 | 1 | 1 of 31 |
| impostor ballots holding a sighting of their TEAMMATE's kill | 18 | 69 | 0 | 0 | 87 | 87 |
| ... teammate still living | 12 | 44 | – | – | 56 | 56 |
| impostor EJECT / SKIP | 46 / 164 | 121 / 530 | 6 / 33 | 10 / 33 | 167 / 694 | 183 / 760 |
| impostor SKIPs holding ≥1 citable row about a non-teammate candidate | 164 | 530 | 33 | 33 | 694 | **760 / 760** |
| ... holding a citable row pointing toward one (testimony or flag) | 163 | 530 | 33 | 33 | 693 | **759 / 760** |
| ... of which: a testimony row / a contradiction row | 163 / 8 | 529 / 26 | 33 / 0 | 33 / 0 | 692 / 34 | 758 / 34 |
| impostor SKIP decision basis: none_held / cited | 95 / 69 | 324 / 206 | 8 / 25 | 13 / 20 | 419 / 275 | 440 / 320 |
| impostor SKIP label: none_held / supported / off_target / not_assessed | 94 / 43 / 25 / 2 | 323 / 126 / 68 / 13 | 8 / 12 / 13 / 0 | 13 / 11 / 9 / 0 | 417 / 169 / 93 / 15 | 438 / 192 / 115 / 15 |
| impostor EJECT label: supported / off_target | 44 / 2 | 120 / 1 | 6 / 0 | 8 / 2 | 164 / 3 | 178 / 5 |
| impostor EJECT with confidence ≥ 0.6 | 46 / 46 | 121 / 121 | – | – | – | 182 / 183 |
| teammate-coerced impostor ballots | 1 | 12 | 0 | 0 | 13 | 13 |
| scorecard row 8 numerator: crew voter / impostor voter | 75 / 44 | 207 / 120 | 1 / 6 | 1 / 8 | 282 / 164 | 284 / 178 (= 462) |

**Other counts:**

- **Choices open to an impostor SKIP.** Per SKIP, the number of non-teammate
  candidates with a pointing-toward row was: 0 in 1 case, 1 in 532, 2 in 200, 3 in 24
  and 4 or more in 3. The mean is 1.34 of 4.2 non-teammate candidates.
- **Impostor votes and the confidence floor.** 31 of 411 ejections had an impostor
  among the ballots at 0.6 or more. None was carried by impostor ballots alone.
- **Committed sample meetings where a voter holds a kill sighting.** These are the
  golden's live coverage for "old recordings render identically":
  - samples/9p2i seed 17 m3, seed 19 m3, seed 26 m0, seed 26 m1;
  - samples/4p1i seed 22 m0.
- **Cross-checks.** 943 = 183 + 760, and 3630 ballots in total. 849 kills, 20 with
  a crew witness (the synthesis memo's 20 of 849). 462 = 284 + 178 reproduces the
  published row 8 (`docs/process-scorecard.md`, pooled).

---

## 3. Design — the witnessed-kill row (R8)

**Channel.**

- **Record.** Move `KillWitnessRecord` to `meetings/schemas.py`, beside
  `VentWitnessRecord` (`:285-318`), as a `_FrozenModel` with
  `observation_id: ObservationId | None = None`. Keep a re-export from
  `orchestrator.game` so `training/conviction/serving.py:83-84` and
  `tests/training/test_composed_runner.py:68` keep importing it unchanged. Its one
  training reader uses `.subject` only (`serving.py:240`), so the parity pin cannot
  move.
- **Accessor.** `kill_witness_records_for_meeting` gains
  `observation_id=event.observation_id`, the vent accessor's precedent
  (`orchestrator/game.py:3880-3886`). Its teammate guard stays.
- **Protocol.** Add an optional `@runtime_checkable KillWitnessAgent`, the
  `MoveWitnessAgent` / `BodyDiscoveryAgent` pattern (`orchestrator/game.py:966-997`).
  `_build_participants` populates `MeetingParticipant.kill_witness_records`
  (a new additive field defaulting to `()`, `meetings/manager.py:891-904`) exactly
  like `move_witness_records` (`orchestrator/game.py:1664-1668`).
- **Not threaded elsewhere.** The record goes to nothing but the assembler: not
  `detect_contradictions`, not `derive_belief_evidence`, not the testimony ledger.
  R8: no public flag.

**Row.**

- One `EvidenceRow` per record:
  - `kind="own_kill"`, added to `EvidenceRowKind` (`render_contract.py:131-138`) and
    to `_EVIDENCE_KIND_CLASS` as class 0 (`manager.py:3415-3422`);
  - `first_hand=True`, `speaker=voter`, `citation_id=record.observation_id`.
- **Wording:** `you watched them KILL in {room} at tick {tick}`.
  - It mirrors the vent row (`manager.py:3491-3493`) and the memory line.
  - It names only the killer (as the row subject), the room and the tick, like the
    other own rows.
  - It names no victim. The typed record carries none: the `PlayerView` has no
    victim field (`observation/service.py:286-289`), and inferring one from a nearby
    body would be layering.
  - The loop renders it as "first-hand: you saw this yourself; cite `<id>`" with no
    template change (`vote_ballot.j2:265`).
- **Source is first-hand only.** The accessor reads observed `saw_player` rows with
  `action=="kill"`. A kill that was reported is a different event type with reported
  provenance (`agents/memory/store.py:2383-2386`, `:957`), so it never becomes a row.
- **Ordering.**
  - Class 0, beside sightings, vents and transits. It is sorted by tick within the
    killer's group, the killer's group sits in roster order, and first-hand rows come
    first.
  - Putting kill rows in a class of their own, above sightings, was considered and
    rejected. D5 orders by provenance, never strength (`manager.py:3409-3414`).
  - For the same reason the kill row obeys the same budget. It would be dropped once
    on baseline 9 (1 of 31), and the template already says the oldest lines stay in
    memory.
- **Teammate firewall at assembly.** `if record.subject in teammates: continue`,
  exactly as the vent, sighting and transit loops do. It is belt and braces over the
  accessor's own guard, the move-channel precedent.
- **Gated.** Rows are built only when the manager's evidence profile says the v9
  ballot is served (section 5). With it OFF, `build_evidence_rows` returns today's
  tuple even when kill records are present.
- **Docstrings to correct under the arm:**
  - `manager.py:3776-3786`: "two of the eight channels have no row" becomes "one"
    while the arm is on;
  - `render_contract.py:467-474`;
  - `orchestrator/game.py:3515-3522`, `:4082-4085`;
  - `meetings/corroboration.py:346-349`.
- **One template edit for crew.** Under the arm, the suspicion-header sentence
  (`vote_ballot.j2:271`) drops "a kill you watched happen," and keeps "someone you
  saw near a body just before you found it". The phrase "only a PARTIAL summary of
  the lines above" stays word for word (`tests/meetings/test_weighing_channel.py:82-83`).

---

## 4. Design — the impostor's strategic ballot (R10)

**Principle.** Remove the belief framing that makes SKIP the only consistent answer
for an impostor. Add nothing that ranks a player, recommends a target, or pushes at
EJECT or at SKIP (the D5 rule, `vote_ballot.j2:126-128`). Keep the grounding rule
identical to crew's.

**Role.** Thread `voter_role` as an additive, defaulted kwarg:

- on `VotePromptRenderer` (`meetings/render_contract.py:482-500`);
- on `vote_ballot_prompt` (`loader.py:1026-1048`);
- at the manager's render call (`manager.py:2271-2310`, from `participant.role`).

Without it, a sole impostor (4p1i: `fellow_impostor_ids == ()`, `_build_participants`
at `orchestrator/game.py:1632-1636`) cannot be told apart from crew. That set is not
re-recorded this wave, but the arm must be right for every set. Every other prompt
set ignores the kwarg.

**v9 edits, all under the arm guard:**

1. **Persona** (`:150`). The crew sentence stays byte-identical. An impostor voter
   gets:
   > "You are one of the impostors. The discussion is over — cast one ejection
   > ballot. It is a move for your side, not a statement of who the impostors are:
   > name one crewmate to eject, or SKIP, whichever you judge better for your side.
   > The outcome is a deterministic tally over every ballot."

   The win-condition clause before it is unchanged.
2. **Team block** (`:289-291`). It renders for every impostor voter, so a sole
   impostor gets it too. The teammate sentence loses its belief clause:
   > "Secret: p-3 is your fellow saboteur. Never vote a teammate, and never your own
   > name: your ballot names a crewmate or SKIP, nothing else."

   It is followed by one paragraph:
   > "Whichever you choose stands on what is on this page, like every ballot at this
   > table. Name a crewmate only when you can cite a line you hold that bears on them
   > — a transcript turn, or a line in <evidence> above — and copy that line's id
   > exactly. You may choose which of the lines you hold to cite. Cite only lines
   > that are really on this page, and in "rationale_text" say only what the cited
   > line shows. When nothing you hold bears on any crewmate, write SKIP."
3. **Left alone:**
   - the "How to decide" paragraph and the confidence sentence (`:304-306`). 182 of
     183 impostor EJECTs are already at 0.6 or more, and redefining confidence for
     impostors would add a push toward the tally floor;
   - the nine-key contract and the `decision_basis` words (`:317`);
   - the rationale bullet (`:320`).

**What this satisfies:**

- **The grounding rule is the crew's.** An impostor EJECT citing a line about its
  target labels `supported`, through the same role-blind labeller. A SKIP labels
  `none_held` or `cited`.
- **The firewall is unchanged and re-proven** (section 7).
- **Nothing points toward the correct answer.** The only role-true fact the text
  states is the one it already stated: the teammate list.
- **Nothing asks the impostor to lie about held data.** It may choose which held
  line to cite, and the id validators null anything it does not hold.

**Limit (stated, not hidden).**

- Row 6 (rationale faithfulness) checks TOKENS, not propositions. So "say only what
  the cited line shows" is an instruction, not something the pipeline enforces.
- The grounding bound is near-vacuous (section 2): 759 of 760 impostor SKIPs could
  have cited a pointing-toward row. The EJECT rate after v9 is therefore a property
  of the wording, and the assessment should read it as such.

**Where I part with R10, mildly.**

- I accept R10.
- But the 50-seed record must not be read as evidence that R10 "worked" through
  outcome cells. With B3 ON in the same record, reporter ejections move under two
  opposing arms at once: the opener gets a reply, while impostors now pile on.
- Read B6 by its own process cells instead:
  - the impostor EJECT share (baseline s9 46 of 210);
  - the impostor SKIP `none_held` share (s9 95 of 164);
  - the label mix of impostor EJECTs;
  - the kind of row they cite;
  - `teammate_coerced` (s9 1);
  - `check_no_betrayal` = 0.

---

## 5. The gate, and the partial-record hypothesis checked

**Three possible gates.**

1. **Default registry bump now** (v8 to v9 in `PROMPT_VERSION_SETS`).
   - This ships prompt bytes default-ON before any adopting record, contrary to
     AGENTS.md craft rule 7, unless the owner overrides it as D4 did
     (`tasks/work/alibi-as-route.md:575-583`).
   - It also opens a bump-in-flight window over the three sets that are not
     re-recorded (section 6b).
   - Not recommended for this wave.
2. **An env lever with a prompt-version overlay** (the `corroboration_discipline`
   precedent: `orchestrator/game.py:527-550`, `orchestrator/replay.py:1057-1065`).
   It FAILS the partial-record principle for s9 itself:
   - `ReplayLoader` refuses any replay whose stamped toggle differs from the ambient
     environment (`api/replay_loader.py:745-777`, `ReplaySubstrateMismatchError`).
   - `verify_samples.sh` loads through `ReplayLoader` with no override
     (`scripts/_verify_samples.py:132`), so s9 would stop verifying in CI and stop
     serving in the demo.
   - The new flag also splits the MANIFEST flags column away from the other three
     sets (`scripts/check_doc_facts.py:2248-2266`).
3. **Recommended: an experiment-profile arm.**
   - **Fields.** Add `vote_ballot_version: Literal[9] | None = None` to
     `MeetingEvidenceProfile` (`meetings/evidence_profile.py:67-110`, read from an env
     var in `from_environment`, the `bounded_rebuttal_version` precedent) and the same
     field to `RecordedExperimentConfig` (`orchestrator/experiment_config.py:29-45`).
   - **Recorder and loader.**
     - The runner reads the profile from the environment
       (`orchestrator/game.py:1379`).
     - `HeadlessGame` merges it into the experiment config written on every tick
       row (`orchestrator/game.py:2253-2272`). So the standard
       `refresh_samples.sh` records it with no new plumbing.
     - The loader reconstructs from the recording's own config
       (`api/replay_loader.py:1454-1560`), so it raises no substrate mismatch.
     - The flags stamp is unchanged.
   - **Stamp.** The runner stamps `vote_ballot.qwen3_6_27b.v9` when the field is 9.
     The account-arm path is the precedent for a profile that re-stamps
     (`orchestrator/game.py:1410-1427`). The arm is refused in combination with the
     four legacy overlays and with account mode, following the precedent at
     `:1389-1403`.
   - **Body.** Guarded blocks in the same `vote_ballot.j2`, on a render kwarg bound
     by `build_prompt_renderers` (the `public_account_version` kwarg precedent). The
     header marker keeps `vote_ballot.qwen3_6_27b.v8` first
     (`tests/agents/test_bespoke_prompt_sets.py:1016-1021` reads the first marker)
     and names the v9 arm in prose.
   - **Manager.** It already holds the profile (`meetings/manager.py:1105`), which
     decides both the kill rows and the impostor kwarg. One captured choice, beside
     the stamp.
   - **Serializer.** The new field must not change old bytes. Delete it from the
     payload when it is None, the pattern at `experiment_config.py:95-104`, so every
     recorded experiment config keeps its bytes.
   - **Frontend types.** Regenerate them: `RecordedExperimentConfig` is exported to
     the frontend (`scripts/gen_frontend_types.py:296`,
     `frontend/src/types/api.ts:73`).
   - **Adoption later.** Flip the registry default to v9, delete the switch, keep
     the recorded key (craft rule 3). The s9 assessment recordings already wear the
     adopted stamp.

**Verdict on the hypothesis for B6.** It holds on gate 3. It fails at these places:

- **One substrate across four sets.** `scripts/check_doc_facts.py:2146-2270` requires
  all four sets to share ONE prompt stamp, and the lead-in must name every token.
  README's sample-provenance paragraph must name every version token
  (`scripts/check_doc_facts.py:1360-1367`, `:1468-1480`). Both are enforced by
  `tests/scripts/test_check_doc_facts.py:373-374`. Any prompt change on a partial
  record trips this, whatever the gate. It needs a per-set or per-era provenance
  amendment, with the `eval/vote_correctness.py:30-39` lead-in rewritten to match.
  This belongs on the record card, but B6 is what forces it.
- **The golden walk cannot walk the re-recorded s9:**
  - `resolve_prompt_set` finds no set for an arm stamp
    (`tests/meetings/test_prompt_byte_golden.py:468-500`);
  - `_tagging_manager` builds a default-profile manager (`:433-458`);
  - the walk applies meetings without the recorded `meeting_reset` (`:723-726`,
    `orchestrator/game.py:1773-1781`), so a B2-ON recording fails its post-meeting
    hash check;
  - it refuses any temporal-observation recording outright (`:656`,
    `orchestrator/replay.py:938-944`). If B4 stamps temporal observations on s9, the
    golden loses s9 entirely, and with it the proof that the v9 ballot renders
    through its stamp.
  - The walk must thread the recording's experiment config.
- **The window test.** `test_the_bump_in_flight_window_is_closed_and_the_archive_is_empty`
  (`test_prompt_byte_golden.py:1445-1467`) asserts every committed stamp equals the
  default mapping. It must accept a registered arm stamp whose recording carries the
  arm.
- **The live-recorded prompt-version pin.** `tests/scripts/test_validity_gate_cli.py:536-557`
  (`_locked_pin`, read against samples/9p2i at `:30`) must follow s9's own recorded
  map.
- **Publication.** A re-recorded `replays/samples/9p2i` merged to `main` republishes
  the demo (AGENTS.md, `pages.yml`; `scripts/build_demo_bundle.py:90`). The
  assessment recording should stay off `main`, or its publication should be ruled
  explicitly.
- **Wave-wide, not B6.** The standard recorder cannot record TACTICAL or ENGINE
  experiment arms: `scripts/run_game.py:95-114` builds `HeadlessGame` with no
  `experiment_config`, and `build_default_agent_factory()` with none. Only the
  meeting-profile arms travel by environment. B1, B2 and R7 need that plumbing.

---

## 6. The v8 to v9 cascade

### 6a. This wave (gate 3: the arm; default stays v8)

- **Template.** `agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2`: guarded blocks
  at `:150`, `:271` and `:289-291`; the header lineage paragraph (after `:104-137`)
  names the v9 arm. The marker at `:3` stays v8.
- **Profile, config and runner:**
  - `meetings/evidence_profile.py`: the field and its env read;
  - `orchestrator/experiment_config.py`: the field, the serializer and `is_default`;
  - `orchestrator/game.py:1379-1427`: the v9 stamp map and the combination refusals;
    `:2253-2263`, where the key joins the runner-agreement loop.
- **Loader.** `agents/strategic/prompts/loader.py`: the kwarg on
  `vote_ballot_prompt` (`:1026-1130`) and in `build_prompt_renderers`.
- **Meeting layer:**
  - `meetings/render_contract.py`: `voter_role`, `own_kill` and the docstring;
  - `meetings/manager.py`: `MeetingParticipant`, the kind class, the own-channel
    builder, the assembler gate and the render call;
  - `meetings/schemas.py`: `KillWitnessRecord`.
- **Orchestrator.** `orchestrator/game.py`: the record re-export, `KillWitnessAgent`,
  `_build_participants` and the accessor id.
- **Frontend.** Regenerate `frontend/src/types/api.ts` and `api.fidelity.ts`.
- **Tests:**
  - `tests/meetings/test_weighing_channel.py` (new arm class; the v8 partial-summary
    test at `:2087-2125` stays for the OFF body);
  - `tests/meetings/test_prompt_byte_golden.py` (arm resolution, recorded-config
    threading, the window test);
  - `tests/agents/test_bespoke_prompt_sets.py` (arm stamp never equals a default
    stamp);
  - `tests/meetings/test_manager.py` (firewall twin);
  - `tests/scripts/test_validity_gate_cli.py:536-557`.
- **Not touched this wave:**
  - `DEFAULT_PROMPT_VERSIONS` (`orchestrator/game.py:354-359`, the frozen `qwen3_5_9b`
    reference);
  - `PROMPT_VERSION_SETS["qwen3_6_27b"]` (`:439-442`);
  - the four overlay registries (`:467-583`);
  - `scripts/record_ml_corpus.sh:171`;
  - `scripts/refresh_samples.sh`, which has no version pin, only the prompt-set check
    (`:564-575`) and the lever-slate preflight (`:303-326`). The arm travels by env
    and is not a lever.
  - `tests/scripts/test_manifest_writer.py:80`, which reads samples/4p1i.

### 6b. At adoption (or now, if the owner overrides rule 7): the default bump

- **Marker.** `vote_ballot.j2:3`, v8 to v9. The guards are deleted and the v9 text
  becomes the body.
- **Registry.** `orchestrator/game.py:439-442`, `vote_ballot.qwen3_6_27b.v9`, plus the
  lineage comment at `:423-436`.
  - `DEFAULT_PROMPT_VERSIONS` (`:354-359`) does NOT move.
  - The four overlays inherit through their `**PROMPT_VERSION_SETS[...]` spreads
    (`:475`, `:519`, `:545`, `:577`). Only their comments move.
- **Pins:**
  - `tests/agents/test_bespoke_prompt_sets.py:530-541` (pin), `:543-551` (floor
    becomes `.v9`, stale list gains `.v8`), `:1035-1053` (rewind v9 to v8);
  - `tests/meetings/test_corroboration.py:2150`, `:2170`, `:2181`;
  - `tests/meetings/test_prompt_byte_golden.py:1336-1337`.
- **Recorder.** `scripts/record_ml_corpus.sh:171` `REQUIRED_PROMPT_VERSIONS_BASE`
  becomes `vote_ballot.qwen3_6_27b.v9`. The frozen recorder's pin moves with the
  registry, the alibi-card precedent. The comment at `:158-170` moves too, and
  `tests/scripts/test_record_ml_corpus.py:228`, `:985-994`.
- **`scripts/refresh_samples.sh`:** no edit.
- **Bump-in-flight archive**, while s4, c9 and c4 still stamp v8 (the mechanism of
  `tasks/work/alibi-as-route.md:544-553`, `:592-596`, `:644-646`):
  - byte-copy the pre-bump bodies to `tests/fixtures/prompt_archive/qwen3_6_27b_v8/`:
    `crewmate_report.j2`, `impostor_report.j2`, `accusation_round.j2`,
    `vote_ballot.j2`, and the two `*_roll_call.j2` variants, as the v5 archive held
    six;
  - `ARCHIVED_PROMPT_VERSION_SETS` gains `{"qwen3_6_27b_v8": {the three .v6,
    vote_ballot.qwen3_6_27b.v8}}` (`test_prompt_byte_golden.py:194-195`);
  - `ARCHIVED_MAP_CARDS` gains the unchanged live card (`:201`);
  - the window test (`:1445-1467`) is rewritten to assert the window is OPEN;
  - the perturbation leg (`:1690`) is re-aimed at the archived v8 body;
  - the `docs/artifacts.md` `tests/fixtures/` row and the `tasks/README.md` inventory
    sentence are updated.
  - The golden walks only the two samples sets (`:174-177`), so the archive serves
    s4 there. c9 and c4 are not re-rendered by it.
  - `_locked_pin` (`tests/scripts/test_validity_gate_cli.py:536-557`) prefers the
    archive, so it would pin samples/9p2i to v8. It must read s9's own map.
- **Docs and doc-fact checks.** README provenance tokens, the
  `eval/vote_correctness.py` lead-in and `check_doc_facts` one-substrate agreement
  (section 5).
- **Comments that stay true** as history: `eval/meeting_quality.py:331`,
  `eval/validity.py:179`.

---

## 7. Planted tests

**Kill row:**

1. **A witness gets the row.** A crew participant with one `KillWitnessRecord`, arm
   ON, gets exactly one `own_kill` row. It carries the exact description,
   `first_hand`, the voter as speaker, and the observation id.
2. **A voter told about it gets nothing.**
   - Set-up: a `TacticalAgent` whose store holds only a REPORTED `saw_kill`
     statement (`absorb_reported_testimony`), in a transcript with another speaker's
     `SawKillObservation`.
   - Expected: `kill_witness_records_for_meeting()` returns `()`, and no `own_kill`
     row appears.
   - Planted side: the same event written with observed provenance produces the row.
3. **A teammate witness never gets a row naming its teammate.**
   - An impostor participant with `fellow_impostor_ids=("p-3",)` and a record naming
     p-3 gets no row. The same records on a crewmate keep it (the
     `test_the_identical_records_on_a_crewmate_keep_every_row` pattern,
     `test_weighing_channel.py:1710`).
   - The records are passed directly, bypassing the accessor, so the ASSEMBLY guard
     is what is proven.
   - A committed-data twin: over the 87 impostor ballots holding a teammate-kill
     sighting, no arm-ON row names a fellow.
4. **Old recordings render identically.**
   - Arm OFF with kill records present: `build_evidence_rows` returns the v8 tuple,
     and the v8 body bytes are unchanged.
   - Planted side: an ungated assembler changes the re-rendered ballots at the five
     committed sample meetings listed in section 2, and the byte golden fails there.
     So the gate is not vacuous.
5. **No flag.** Arm ON leaves `detect_contradictions` output, the testimony ledger and
   the belief fold identical. `TestTheAssemblerCannotReachTheLedger`
   (`test_weighing_channel.py:1549-1620`) gains any new helper in `_ASSEMBLER`.

**Impostor ballot:**

6. **Firewall under v9.**
   - A scripted impostor ballot naming its teammate, rendered through the v9 arm, is
     recorded as SKIP with `guard_rewrite_reason="teammate_coerced"`, the marker and
     label `not_assessed`, and `check_no_betrayal` passes.
   - Planted side: with `coerce_teammate_ballot_to_skip` monkeypatched to identity,
     `check_no_betrayal` fails.
7. **Role reaches the sole impostor.** Under the arm, an impostor with
   `fellow_impostor_ids=()` renders the strategy text. Planted side: with
   `voter_role` withheld, it renders the crew text.
8. **Crew bytes.** Under the arm, a crew ballot with no kill record differs from v8
   only in the one suspicion-header sentence.
9. **No push and no lie.**
   - The impostor paragraphs name no player id, rank nothing and recommend no target.
     This follows `test_the_decision_section_recommends_no_player` and its planted
     twin (`test_weighing_channel.py:2063-2085`).
   - They contain the honest-citation clause. Planted side: a body saying a sighting
     may be invented is detected.
10. **Labels unchanged in kind.**
    - An impostor EJECT citing a testimony turn about its target labels `supported`.
    - An impostor SKIP with no ids and `none_held` labels `none_held`.
    - The tally is independent of the label (the existing `test_grounding_label.py`
      pattern).

---

## 8. What the record will do, and what must not move

**Will move on samples/9p2i, all acceptable.**

- Impostor EJECTs enter scorecard rows 1, 4, 6, 7 and 8, and through ejections rows 5
  and 9. Row 2 is crew-only (`eval/process_scorecard.py:1443-1451`).
- **Row 8 (wrong-but-believable).** Every grounded impostor EJECT is counted in row 8
  by construction (`:1436-1442`: the target is a crewmate, because teammate ballots
  are coerced).
  - Today 178 of the 462 pooled numerator come from impostor voters (s9: 44 of 119).
  - Row 8 will rise with the impostor EJECT share, partly as bookkeeping rather than
    as crew being fooled.
  - Report its voter-role split in the separate census (R13), not in the scorecard.
- **Row 9 and the reporter cells** may fall or rise, confounded with B1 to B4.
- **Row 7** `teammate_coerced` may rise from 1 on s9.
- **Row 5** `first_hand` shifts only at the few kill-holder meetings.

**Must not move.**

- Every byte under `replays/samples/4p1i`, `replays/ml_corpus/9p2i` and
  `replays/ml_corpus/4p1i`.
- `verify_samples.sh` on those sets.
- Their per-set scorecard, vote-correctness and other `--check` cells. These are
  as-recorded; the labeller and the tally are never re-run on old bytes.
- The byte golden on samples/4p1i.
- `build_evidence_rows` on any v8 recording.
- `check_no_betrayal` = 0 on all four sets.
- The three marker mirrors.
- The pooled scorecard sections must not silently pool across the new boundary. The
  publisher labels or splits them; `docs/process-scorecard.md` "Recording
  provenance".

**Cost.** No new call.

- Input tokens: about 160 per impostor ballot, plus one line per kill holder. On s9
  that is about 34k tokens against 9.85M (under 0.4%).

---

## 9. Risks and open decisions

- **The gate.** An arm, not a default bump, contrary to the card title's "bump v8 to
  v9". The stamp still reads v9. The orchestrator should confirm; the owner rules
  only if the default is to move now.
- **One-substrate doc-fact gate.** It must be amended for any partial record. That
  belongs on the record card, forced by B6 and B3.
- **Golden walk.** It must thread the recorded experiment config. If B4 uses the
  temporal-observation path, the golden cannot cover s9 at all.
- **Publication** of a re-recorded samples/9p2i on `main`.
- **n is tiny for the kill row** (4 holders in 50 games). Assess presence and
  mechanism, not effect.
- **Attribution.** All arms ON in one 50-seed record cannot attribute outcome deltas
  to one arm. Read B6 by its own process cells.
- **Honest rationales are instructed, not enforced** (row 6 tests tokens only).

---

## 10. Reproduction

Scripts are uncommitted and count-only, in
`<session scratchpad>/b6census/`.
Run them from the repo root at `e886b663`:

- `PYTHONPATH=. uv run --frozen python <dir>/census.py <dir>/out.json`: kill holders,
  the teammate case, impostor rows, bases and labels.
- `PYTHONPATH=. uv run --frozen python <dir>/census2.py <dir>/out2.json`: the budget
  simulation, the number of choices open to an impostor SKIP, and confidence against
  the floor.
- `PYTHONPATH=. uv run --frozen python <dir>/census3.py <dir>/out3.json`: the same as
  census2, plus the (set, meeting) keys of the kill holders.
- `PYTHONPATH=. uv run --frozen python <dir>/row8.py <dir>/row8.json`: scorecard row 8
  split by voter role, using the scorecard's own predicates.
- The kill-witness cross-check (849 / 20 / 50) reads the synthesis `walk.json`.
