# Harden the public accounts channel against forged placement and leaked truth

**Status:** done

## Outcome

A speaker cannot forge a section of another listener's prompt, cannot mint a
contradiction flag against an innocent third party from their own claims alone,
and is placed by their own sighting claim. The teammate firewall covers every
observation kind the accounts menu elicits, and the attributed reply prompt asks
only for what the schema can express. The vent-certificate trade-off the
attributed mode makes by design is stated in both candidate checkpoints.

## Evidence

Review claims are leads, not measurements of this tree. Reproduce each claim
from the archived follow-up review
([report](../../audits/review-2026-09-06/REVIEW_REPORT_FOLLOWUP.md), findings
NC2-1, NC2-2/FU-ALIBI-4, NG2-2/NG3-5, NC2-3 and NG2-4) on this checkout before
implementing.

- **NC2-1.** `agents/strategic/prompts/qwen3_6_27b/_account_transcript.j2:3`
  renders `{{ turn.free_text }}` unquoted and undelimited, so a speaker can
  forge an `## Account comparisons` section in every listener's prompt.
- **NC2-2 / FU-ALIBI-4.** `meetings/public_accounts.py:146-153` pairs every two
  placements naming the same subject without requiring distinct speakers, so one
  speaker mints an `alibi_conflict` against an innocent third party from their
  own claims alone. The refuters found the machine-readable `subjects` tuple
  names only the innocent, and the flag reaches every listener's public block
  and, under evidence v2, their private block.
- **NG2-2 / NG3-5.** `meetings/public_accounts.py:71-110` derives placements from
  each turn but overwrites `subject` with the observation's subject (`:89`) for a
  sighting claim, so the speaker's own position is never placed and `co_present`
  is ignored. The cheapest lie is therefore a sighting claim that places nobody.
- **NC2-3.** The teammate firewall at `meetings/manager.py:3320` filters only
  `SawVentObservation`, while the accounts menu elicits `saw_kill`, so an
  impostor can be led to testify against its own teammate.
- **NG2-4.** `agents/strategic/prompts/qwen3_6_27b/accusation_round_accounts.j2:10`
  orders the replying agent to "Cite your relevant placement or observation"
  while the same template's return JSON offers `observations` and `claims` only —
  the attributed-only arm has no placement shape to cite.
- **Disclosure.** `audits/deduction-candidate/gameplay-review.md:68` records that
  shared role-proof flags fall to zero under attributed testimony, and
  `:153-157` explains why. That trade-off belongs in both checkpoints.

## Acceptance

- [x] Review correction: the comparison never pairs two rows read out of the same
  artifact, so no public-account flag is self-linked and none is typed
  `role_proof` by any of the three evidence classifiers. A planted case shows the
  self-named sighting that used to mint one, and a control shows a genuine
  cross-artifact disagreement still flags twice.
- [x] Review correction: the round-0 table's head-drift caveat names what actually
  moved — the NG3-5 (slack) row's endpoint, not its `contradiction_id`, which is
  unchanged — and both halves are reproduced by the quoted command on the two
  commits they are pinned to.
- [x] Review correction: the firewall's `saw_kill` arm is filtered only where the
  account channel elicits it, so a default-path meeting records exactly what it
  recorded before this card. A default-path case pins it; the accounts arm keeps
  its end-to-end drop.
- [x] Review correction: the account prompt-set revision advances to `v2`, so no
  capture taken after this card can share an identifier with the pre-hardening
  captures committed under `audits/`. A test reads both captures and fails on a
  collision.
- [x] Review correction: the fence flattens every character `str.splitlines`
  treats as a line boundary, in speaker free text and inside the serialized
  structured rows. The planted forgery is parametrised over that whole alphabet,
  and a third case proves the alphabet is complete.
- [x] Review correction: a speaker named among its own bystanders adds no
  placement, so a legal same-tick sighting two rooms from its stated position is
  not called impossible; a planted case shows the flag that used to mint and that
  a third party's denied co-presence still flags.
- [x] Review correction: a single-author re-target carries the private detector's
  proxy-intra-turn reason, so N same-speaker flags fold to ONE belief lift.
- [x] Review correction: a derived placement flags through the artifact id the
  readers' event-id vocabulary resolves; the derivation moves into the hashed
  identity, which is what keeps two derived pairs off one artifact pair distinct.
- [x] Review correction: every number in the reproduction table is the verbatim
  summary line of the quoted command on the tree that row is pinned to.
- [x] Reproduce each finding before repairing it: a forged section heading
  reaching a listener's prompt, a single-speaker minted `alibi_conflict` naming
  an innocent, a sighting claim that places nobody, an impostor's `saw_kill`
  reaching a teammate, and the reply prompt's unsatisfiable instruction.
- [x] `free_text` is quoted or delimited so no speaker-authored bytes can open a
  section the prompt's own structure owns. An adverse test plants a speaker whose
  free text is a full forged comparison section.
- [x] A conflict requires two distinct speakers, or is labelled as
  self-contradiction of the single speaker. The `subjects` tuple names the
  speaker whose claims produced it, not only the accused third party.
- [x] The speaker of a sighting claim is placed by their own claim, and
  `co_present` participates in the comparison. An adverse test shows the cheapest
  lie now places its speaker.
- [x] The teammate firewall covers every observation kind the accounts menu can
  elicit, `saw_kill` included; an adverse test plants an impostor whose menu
  answer names its teammate.
- [x] The attributed reply prompt asks only for what the schema expresses, or the
  schema gains the placement it demands. The two are checked against each other
  by a test, not by reading.
- [x] One sentence in each of `audits/deduction-candidate/checkpoint.md` and
  `audits/investigation-candidate/checkpoint.md` states the vent-certificate
  trade-off: attributed mode replaces the grounded vent detector by design, as
  disclosed at `audits/deduction-candidate/gameplay-review.md:68,153-157`.
- [x] Every new guard has a planted failure proving it detects the claimed defect.

## Constraints

Certified vent behaviour stays the baseline: attributed mode's removal of the
shared vent certificate is a deliberate, test-pinned design choice, not a defect
to repair here. Candidates (`public_accounts`, `attributed_testimony`) stay
default-OFF and this card adopts nothing; hardening a channel is not evidence
that it improves play. No re-record, no provider calls, no new levers, no
changes to the default meeting path. Any `audits/` byte change requires
refreshing the `audits/` row of `docs/artifacts.md` — `verify_ml_evidence.py`
compares that row's exact tracked-byte total and file count against disk. One
writer owns `meetings/` for the duration; this card must not run concurrently
with the renderer card over `agents/memory/store.py`. Prerequisite: the renderer
and provenance cards land first, so a repaired channel is measured by a renderer
that keeps its evidence.

## Expected scope

`meetings/public_accounts.py`, `meetings/manager.py`,
`agents/strategic/prompts/qwen3_6_27b/_account_transcript.j2`,
`agents/strategic/prompts/qwen3_6_27b/accusation_round_accounts.j2`, the account
schema module the reply prompt cites, `tests/meetings/`, `tests/agents/`, and one
sentence in each of the two candidate checkpoints under `audits/` plus the
`docs/artifacts.md` audits row that follows from it. The round-1 review
corrections add `agents/strategic/prompts/loader.py`: the account prompt-set
revision the templates take their identity from, and the line-flattening filter
the fence applies. Both were directed by the review; the schema was not widened.

## Record impact

ON-path meeting bytes only: no committed recording exercises any of these
fields, the default path is unchanged, and no report or DTO byte moves. Prompt
bytes on the accounts and attributed arms do change, so captures taken before
this card are not comparable to captures taken after; say so wherever the two
appear together. `audits/` tracked bytes move, so the `docs/artifacts.md`
registry row moves with them. Adoption of either profile remains a separate
decision with its own record.

## Validation

`uv run pytest tests/meetings tests/agents -q` for the planted forged section,
single-speaker conflict, unplaced speaker, teammate `saw_kill` and prompt/schema
agreement cases, then `bash scripts/check.sh`, then
`bash scripts/verify_samples.sh`, then the four derived report checks:

```sh
uv run python scripts/build_sample_report.py --sample-dir replays/samples/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check
```

Then `uv run python scripts/check_doc_facts.py` and
`uv run python scripts/verify_ml_evidence.py`, because the checkpoint sentences
move the `audits/` byte total the registry row promises.

## Results

Implemented on `work/accounts-channel-hardening`, based on the verified tip of
`work/recorded-provenance-gaps` (`5682ea2a`), so the channel is measured by the
repaired renderer. Both candidate profiles stay default-OFF and this card adopts
nothing.

### What the code now enforces

`docs/architecture.md` §Explicit cleanup experiments keeps its description of
`meetings/public_accounts.py` — public transcript structure and conditional
walking feasibility, no other speaker's private observations — and this card
changes nothing about that boundary. §Packages (`meetings/`) locates the turn
chokepoint the firewall runs at, and §Enforced boundaries is unaffected: no new
import crosses a contract, and `scripts/check.sh` reports the same four contracts
kept.

- **Fenced free text.** `agents/strategic/prompts/qwen3_6_27b/_account_transcript.j2`
  renders the transcript inside `<transcript>` delimiters and each spoken line as
  `said: "<free text>"` with `"` replaced by `'` and every line boundary flattened
  by the `flatten_lines` filter (`flatten_line_boundaries` in
  `agents/strategic/prompts/loader.py`, which is `" ".join(value.splitlines())`).
  Its alphabet is `str.splitlines`'s own, which is also how the tests decide what
  "begins a line" means, so the guard and its proof cannot cover different
  alphabets:
  speaker-authored bytes occupy exactly one quoted line and can never begin a line
  at column 0, which is what the section headings the template owns require. The
  serialized structured rows go through the same filter, because they carry
  speaker free text too — an `AccusationClaim.reason` or a
  `CorroborationClaim.reason` — and `model_dump_json` escapes only the boundaries
  below `\x1f`, leaving `\x85`, U+2028 and U+2029 intact. The ids inside those rows
  are separately checked against the roster, room ids and task ids by
  `validate_public_accounts` before the turn records.
- **A conflict names the account it impeaches, once.** In
  `detect_public_account_conflicts`, a pair whose two placements come from the
  same speaker about a third party now sets `subjects` to that speaker, appends
  `Both placements come from <speaker> alone, so this impeaches that speaker's own
  account rather than <subject>.`, and closes the description with the weak marker
  `[weak signal: same-speaker proxy contradiction]`. The marker is the load-bearing
  half: `meetings.transcript.contradiction_lift_key` returns its constant
  proxy key for any flag carrying that reason, so belief Rule 2 folds every
  re-target against one speaker into ONE weak delta rather than one per claim pair.
  A pair from two speakers is unchanged and still names the subject; a speaker's own
  self-placements were already subject-named and are unchanged. Both halves — the
  re-target and the fold key — are the rule the private detector applies to the same
  shape (`meetings/transcript.py::_apply_proxy_intra_turn_guard`, Task 10.10); it is
  reimplemented rather than shared because this module reads only public speech.
- **A sighting places its speaker and its named bystanders.** `_placements` emits,
  for `saw_player` / `saw_vent` / `saw_kill` / `saw_move`, a second placement of
  the speaker at the observed room (`from_room` for a transition) and, for
  `saw_player`, one placement per `co_present` name at the observed room — except
  the speaker's own name, which its witness placement already covers, with the hop
  a bare co-present row would not carry. The speaker placement carries one hop of
  `vision_slack`, added to the allowance in the walking comparison, because vision
  reaches one adjacent room for an impostor; the description says which clause came
  from a claimed sighting. The one-hop grant makes the comparison conservative
  rather than sound-by-construction: it will not flag a same-tick sighting two rooms
  from the speaker's stated position, whether or not the speaker also named itself
  among the bystanders. A derived row keeps the event id of the artifact it was read
  out of, so every flag endpoint stays inside the `claim` / `obs` / `whereabouts`
  vocabulary `frontend/src/lib/contradictions.ts` declares and every reader
  resolves; the derivation lives in `_Placement.identity`, which the
  `contradiction_id` hashes, so two derived pairs off one artifact pair stay two
  distinct flags. Because those rows share an event id, the comparison also
  refuses to pair two rows read out of the SAME artifact: a flag reports a
  disagreement between two statements, and `api.schemas.classify_evidence` types a
  flag whose endpoints name one artifact as `role_proof` whatever its kind — so a
  speaker naming itself as a sighting's subject would otherwise turn one sentence
  into this channel's strongest band. Every endpoint pair the channel emits names
  two different artifacts.
- **The teammate firewall is total over the shape union, per path.**
  `exclude_teammate_vent_observations` is renamed
  `exclude_teammate_role_proving_observations` and drops a `saw_kill` naming a
  fellow impostor alongside the `saw_vent` it already dropped — the `saw_vent` arm
  on every path, as Task 15.4 left it, the `saw_kill` arm only where
  `accounts_enabled` says the public-account channel is on, which is the channel
  that put a kill sighting on an impostor's menu. Coverage is stated, not implied:
  `TEAMMATE_GUARDED_OBSERVATION_KINDS` carries one SCOPE for each of the eight
  `ObservationClaim` members (`always`, `accounts`, `never`), and a test drives one
  teammate-naming instance of every member through the guard with the channel on
  AND off, so the declaration and the code cannot disagree in either direction on
  either path. The six `never` shapes record untouched, matching the claims guard,
  which deliberately retains a teammate alibi and corroboration. `accounts_enabled`
  is a required keyword, so a caller cannot land on the wrong path by omission.
- **The reply prompt asks only what the arm offers.**
  `accusation_round_accounts.j2` branches its reply instruction on the same
  `public_account_version or not is_impostor` condition as the shape menu, so a
  speaker told to keep observations empty is asked for free text and an accusation
  claim instead of a placement citation.

### Decisions

- **The reply prompt was narrowed; the schema was not widened.** Acceptance
  offered either. The attributed-only impostor channel is a deliberate,
  test-pinned asymmetry (`tests/agents/test_public_account_prompts.py::test_attribution_alone_does_not_enable_the_common_role_menu`),
  so adding a placement shape to that arm would have changed what the arm compares.
- **No new `ContradictionRef.kind`.** A self-contradiction kind would move the
  served `api.schemas.ContradictionView` union, the frontend union and the
  generated types. The re-target reuses `alibi_conflict` and states the
  distinction in `subjects` and the description, so no DTO byte moves.
- **`saw_player` and `saw_move` naming a teammate still record.** They are
  ordinary placements, not role-proving assertions, and the 7.12 claims guard
  keeps the equivalent teammate alibi. The decision is written into
  `TEAMMATE_GUARDED_OBSERVATION_KINDS` rather than left to the reader.
- **The account prompt revision advances `v1` → `v2`.** These templates take their
  identity from `public_account_prompt_versions`, which composes the stamp from
  `ACCOUNT_PROMPT_SET_REVISION` and the two lever values
  (`..._accounts.qwen3_6_27b.v2.accounts<N>.attributed<M>`) rather than from a
  per-template marker, so the revision is where a byte change is declared. It
  bumps because two committed candidate captures already record the `v1` stamps
  against the pre-hardening bodies (census below), and
  `MeetingReplayEntry.prompt_versions` is the mechanism that tells two generations
  of one template apart. The four account templates share one suffix and advance as
  a unit — the `qwen3_32b` vote-ballot precedent in
  `orchestrator.game.PROMPT_VERSION_SETS` — because a unit bump is what makes a
  changed body unable to keep an old stamp. `orchestrator/game.py` composes the
  stamp through the loader and is untouched, so no `GENERATOR_SOURCES` file moves
  and the frozen held-out manifest needs no restamp.
- **A self co-presence is skipped, not rejected.** Naming yourself among the
  bystanders of your own sighting is a legal thing to say: the schema allows it, the
  rules template advertises `co_present` with no exclusion, and it asserts nothing
  the witness placement has not already asserted. Raising would fail-soft the whole
  turn to a placeholder over a redundant sentence, so `_placements` derives nothing
  from it and the speaker stays placed by the witness row, which carries the vision
  hop. Nothing is dropped from the record; the speaker's position is unchanged.
- **A self-pair is skipped at the pair, not by dropping one of its rows.** A
  speaker naming itself as a sighting's SUBJECT is also legal, but unlike the
  bystander case the two rows it produces are different placements — the
  destination it states and the origin its own sighting was made from — and both
  are worth comparing against what other speakers said. Suppressing either would
  leave a claimed position uncompared, so `_placements` still emits both and only
  the comparison declines to pair them with each other. The skip keys on
  `event_id`, so it covers any derivation a later change adds rather than the one
  shape that exposed it.
- **The flattening filter is registered for every prompt set.** It is a pure text
  primitive with no game state, and only the account transcript uses it, so no other
  set's bytes move (`test_explicit_off_preserves_every_default_renderer` compares the
  default renderings byte for byte). A per-profile environment would have meant a
  second cached environment for one filter.

### Reproductions and planted failures

Every finding was reproduced before it was repaired. Each reproduction is
restated here as a perturbation of the committed tree at `96a83a6a`, so a reader
re-creates the exact defect and watches the gate bite. Each row is: apply the
substitution to the named file, run the command, restore the file.

This table is the round-0 record and stays pinned to `96a83a6a`. The round-1
corrections below moved three of these guards, so at the head the NC2-3 rows name
an anchor that no longer exists (`_ROLE_PROVING_OBSERVATIONS` is now two
scope-specific tuples), the NC2-1 command runs eleven parametrisations rather than
one, and the NG3-5 (slack) row's flag now carries the artifact endpoint
`event_b_id='turn:p-2:obs:1'` where it used to carry `turn:p-2:obs:1:witness` — its
`contradiction_id` is unchanged, because `_Placement.identity` hashes the same
string the endpoint pair used to. Each of those guards is re-planted against the
current tree in **Review corrections, round 1** below.

| Finding | Perturbation | Command | Observed |
| --- | --- | --- | --- |
| NC2-1 | `_account_transcript.j2`: the quoted, flattened `said:` line back to `said: {{ turn.free_text }}` | `.venv/bin/python -m pytest tests/agents/test_public_account_prompts.py::test_speaker_free_text_cannot_open_a_section_the_template_owns -q` | `assert ['## Account ... comparisons'] == ['## Account comparisons']` / `Left contains one more item: '## Account comparisons'` — `1 failed` |
| NG2-4 | `accusation_round_accounts.j2`: the branched reply instruction back to the unconditional `Cite your relevant placement or observation, …` | `.venv/bin/python -m pytest tests/agents/test_public_account_prompts.py::test_the_reply_prompt_asks_only_for_shapes_the_schema_expresses -q` | `assert demands_citation is bool(advertised & _PLACEMENT_KINDS)` → `assert True is False` where the advertised set is empty — `1 failed, 5 passed` |
| NC2-2 / FU-ALIBI-4 | `public_accounts.py`: `single_author = …` → `single_author = False` | `.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_one_speaker_alone_impeaches_itself_not_the_player_it_named -q` | `assert ('p-5',) == ('p-2',)` — the flag names the innocent again — `1 failed` |
| NG3-5 | `public_accounts.py`: `if not isinstance(observation, _SIGHTINGS):` → `if True or …` (no speaker placement) | `.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_the_cheapest_lie_now_places_the_speaker_who_told_it -q` | `ValueError: not enough values to unpack (expected 1, got 0)` — the cheapest lie raises nothing — `1 failed` |
| NG3-5 (slack) | `public_accounts.py`: the witness placement's `vision_slack=1` → `vision_slack=0` | `.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_a_sighting_within_the_granted_slack_is_never_called_impossible -q` | one legal pair becomes a flag: `Left contains one more item: ContradictionRef(contradiction_id='public-account-aa6d4eba507d9b36', …)` — `1 failed, 1 passed` |
| NG2-2 | `public_accounts.py`: `if not isinstance(observation, SawPlayerObservation):` → `if True or …` (no co-present placement) | `.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_a_named_bystander_is_placed_by_the_sighting_that_named_them -q` | `ValueError: not enough values to unpack (expected 1, got 0)` — a denied co-presence is invisible — `1 failed` |
| NC2-3 (coverage) | `manager.py`: `_ROLE_PROVING_OBSERVATIONS` back to `(SawVentObservation,)` | `.venv/bin/python -m pytest tests/meetings/test_manager.py::TestTeammateObservationFirewall -q` | two of the class's four cases fail — the union-coverage one with `AssertionError: saw_kill` … `Left contains one more item: SawKillObservation(type='saw_kill', tick=4, subject='p-3', room='MEDBAY')`, and `test_impostor_teammate_kill_observation_never_reaches_the_transcript` with `assert (SawKillObser...om='MEDBAY'),) == ()` — `2 failed, 2 passed` |
| NC2-3 (end to end) | the same substitution | `.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_an_impostor_menu_answer_naming_its_teammate_never_records -q` | `assert (SawKillObser...room='LABS'),) == ()` — the impostor's menu answer naming its teammate records — `1 failed` |

Each perturbation was applied and reverted in place; `git status --porcelain`
was empty afterwards.

### Verification

All commands run on the code tree at `25351035` — the last commit that changes
anything executable — with this card's own round-2 text on disk as the only
uncommitted difference, which is exactly the tree this card's commit produces.
The figures they replace were measured at `f8140c32` after round 1 and at
`96a83a6a` before it; both are superseded, and the only movement is the one test
round 2 adds.

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/meetings tests/agents -q` | 2,599 passed |
| `bash scripts/check.sh` | exit 0 — 7,318 Python passed, 20 skipped, 3 xfailed; 515 frontend tests over 19 files; strict mypy on 471 sources; 4 import contracts kept, 0 broken; 390 phase tasks / 390 prompts in sync; 43 work cards; production build |
| `bash scripts/verify_samples.sh` | all 100 canonical recordings verified clean |
| `AILIBI_SAMPLES_ROOT=replays/ml_corpus bash scripts/verify_samples.sh` | all 200 ML-corpus recordings verified clean |
| `.venv/bin/python scripts/build_sample_report.py --sample-dir <set> --check` for `replays/samples/4p1i`, `replays/samples/9p2i`, `replays/ml_corpus/4p1i`, `replays/ml_corpus/9p2i` | all four consistent with their replays, exit 0 |
| `.venv/bin/python scripts/check_doc_facts.py` | doc facts, front door, `docs/ml-program.md` and budgets all verified |
| `.venv/bin/python scripts/verify_ml_evidence.py` | checks 60, OK 48, FAIL 0, ABSENT 7, INFO 5 — every check passed |
| `.venv/bin/python -m pytest tests/experiments/test_held_out_prefixes.py -q` | 28 passed |
| `.venv/bin/python -m pytest tests/orchestrator/ --collect-only -q` | 583 tests collected |

The `audits/` registry row moved with the two checkpoint sentences, in round 0.
Recomputed with that change staged: `git ls-files audits | wc -l` → 202 and
`git ls-files audits -z | xargs -0 wc -c | tail -1` → 14,853,326, which is the
row written in `docs/artifacts.md`. The round-1 corrections move no `audits/`
byte — they only READ two committed captures from a test — so that row is
unchanged and `verify_ml_evidence.py` still reconciles it against disk. The
round-2 correction moves no `audits/` byte either.

No file in `experiments/held_out_prefixes.py::GENERATOR_SOURCES` is touched by
this branch. The prompt-revision bump lives in
`agents/strategic/prompts/loader.py`, which `orchestrator/game.py` calls but does
not copy, so no hashed file moves, the frozen held-out manifest needs no restamp,
and its regeneration test passes unchanged. The frontend `npm run e2e` leg was not
required: no reader, orchestrator or served DTO byte changes — the round-1
endpoint repair exists precisely so the served `ContradictionView` keeps the
event-id vocabulary the frontend already parses — and `scripts/check.sh` ran the
whole Python and frontend suites regardless.

### Record impact and limitations

- Prompt bytes on the accounts and attributed arms changed, so captures taken
  before this branch are not comparable to captures taken after. The two
  candidate measurements committed under `audits/deduction-candidate/` and
  `audits/investigation-candidate/` predate it. That discontinuity is now
  machine-readable rather than prose-only: they record the `v1` stamps and every
  later capture records `v2`, and a test fails if a stamp composed today already
  appears in either file.
- The default meeting path is unchanged, and the gate is in the code rather than
  in the reader's head. The templates edited here are reached only under
  `public_account_version` / `attributed_testimony_version`, both default-OFF; the
  comparator runs only on the attributed arm; and the firewall's new `saw_kill` arm
  is filtered only when `accounts_enabled` is true, so with both levers OFF the
  guard is exactly the Task 15.4 vent filter it was — a no-op for every crewmate
  and every sole impostor, and for a multi-impostor turn it drops a teammate vent
  and records a teammate kill, as before. A default-path case pins that. All 300
  committed recordings reconstruct and all four derived reports remain
  byte-consistent, which is the evidence that no recorded byte moved.
- What the default path does with a teammate-naming `saw_kill` is now an explicit
  open question rather than a silent inheritance. The default `accusation_round.j2`
  does elicit `saw_kill`, so a multi-impostor default-path turn can still publicly
  name a teammate as a killer; the 7.12 doctrine arguably wants that filtered
  everywhere. Doing so changes what a default meeting records, which is a decision
  with its own record and its own re-record question — it is not this card's to
  take, and this card does not take it.
- Hardening a channel is not evidence that it improves play. Adoption of either
  profile remains a separate decision with its own record.
- `agents/memory/evidence_context.py` is outside this card's writer boundary. The
  private travel-check row FU-ALIBI-4 describes is built from the claim itself
  rather than from a flag, so the speaker-distinctness rule added here does not
  reach it; that mirror remains open and belongs to whoever next owns that file.
- The vision hop makes the speaker comparison deliberately conservative: a
  same-tick sighting two rooms from the speaker's stated position is legal
  arithmetic here even though the engine's vision would not allow it. The
  comparison keeps its existing posture of never calling a legal account
  impossible — including when the speaker names itself, among the bystanders of
  that sighting or as its subject. Both are ways this card briefly broke that
  posture: the first repaired in round 1, the second in round 2.
- `eval/alibi_fabrication.py` scores a caught alibi by subject membership, so an
  author-retargeted flag leaves the alibi's third-party subject outside the caught
  set and the alibi counts as survived. That is a real property and it is NOT new
  here: the private detector's own Task 10.10 re-target has the identical shape on
  the DEFAULT path. Reproduced at `f8140c32` with two contradictory alibis about
  p-5 from one impostor speaker through `detect_contradictions` (levers OFF):
  `kind=alibi_conflict subjects=('p-2',)`, `subject-membership caught set: ['p-2']`,
  `scored as SURVIVED: ['p-5']`. Teaching the scorer to read a re-target changes a
  published metric's definition for every arm including the baseline, and
  `eval/` is outside this card's writer boundary, so it stays an open item for
  whoever next owns that metric rather than a silent redefinition here.
- Delivery state: implemented and verified locally; two independent review rounds
  received and their blocking findings repaired (below). Not owner reviewed, not
  merged. Adoption is not applicable — this card repairs a gated channel and
  adopts nothing.

### Review corrections, round 1 (2026-09-09)

Three review lenses returned fourteen blocking findings over the head `28742c2b`
— seven distinct items, most of them reported by more than one lens — alongside
seven Codex inline comments. Six are code defects, repaired at `4142f661`,
`93eeb7d5` and `f8140c32`; the seventh is two mis-recorded numbers, corrected in
the round-0 table above; one Codex comment is refuted below. Every sentence in
this card's earlier sections now describes the repaired head; the paragraphs
below say what each of them used to claim and why that was false.

**Six false or unenforced claims.**

1. *"The default meeting path is unchanged"* (Record impact) and *"no changes to
   the default meeting path"* (Constraints). The guard is called unconditionally
   at the per-turn chokepoint, so adding `SawKillObservation` to its filtered
   tuple changed every path, not the account arms. The card's own new test proved
   it: it runs through `_make_manager`, which builds a `MeetingConfig()` with both
   levers `None`. Reverting the tuple to the base `(SawVentObservation,)` and
   running that class gave `2 failed, 2 passed` — the default-path meeting
   recorded `SawKillObservation(subject='p-3')` before this branch and silently
   dropped it after. Repaired by scope: the vent arm stays global, the kill arm is
   filtered only under `accounts_enabled`, and a default-path case pins the
   untouched behaviour. (Codex 3966002125.)
2. *"No prompt-version bump … so no recorded prompt-version pin names these
   bytes"* (Decisions). The quoted grep reproduces (`grep -rn
   "accounts.qwen3_6_27b" tests scripts api experiments` → exit 1), but its scope
   excludes `audits/`, where the pins live. `grep -c "accounts\.qwen3_6_27b\.v1\."
   audits/investigation-candidate/2026-09-06-meetings.json
   audits/deduction-candidate/2026-09-06-mechanisms.json` returns 112 for each
   file — 28 account-arm captures × four template keys — and `grep -o
   "accusation_round_accounts\.qwen3_6_27b\.v1\.accounts[01]\.attributed[01]"
   <either file> | sort | uniq -c` splits those 28 into 7 / 7 / 14 across the
   three arms. Repaired by advancing
   `ACCOUNT_PROMPT_SET_REVISION` to `v2` and pinning the non-collision with a test
   that reads both captures. (Codex 3966002107.)
3. *"Speaker-authored bytes … can never begin a line at column 0"* and *"Structured
   rows are not flattened: `model_dump_json` escapes newlines"*. Both were false
   for eight of the ten line boundaries `str.splitlines` recognises, and the
   structured rows carry speaker free text (`AccusationClaim.reason`). Repaired by
   the `flatten_lines` filter on both, with the planted forgery parametrised over
   the whole alphabet and a case proving the alphabet is complete. (Codex
   3966002112.)
4. *"it will not flag a same-tick sighting two rooms from the speaker's stated
   position"* and *"never calling a legal account impossible"*. A speaker naming
   itself in `co_present` minted exactly that flag, because the derived co-present
   row carried no vision slack while the witness row carried one. Repaired by
   skipping the speaker; a planted case shows the flag that used to mint and that a
   third party's denied co-presence still flags. (Codex 3966002117.)
5. *"This mirrors the rule the private detector applies to the same shape"*. Only
   the subject retarget was copied; `WEAK_REASON_PROXY_INTRA_TURN` was not, so
   `contradiction_lift_key` gave each same-speaker pair its own key and N flags
   from one mouth became N weak lifts against that mouth. Repaired by writing the
   same weak marker the private detector writes. (Codex 3966002132.)
6. The derived endpoints `…:witness` and `…:co_present:<i>` sat outside the
   `claim` / `obs` / `whereabouts` vocabulary `frontend/src/lib/contradictions.ts`
   declares as the one place it is written down, so such a flag attached to no turn
   artifact. Latent — the comparator runs only on the attributed arm and no
   committed recording carries a `public-account-` flag — and repaired by keeping
   the artifact id as the endpoint and moving the derivation into the hashed
   identity. (Codex 3966002139.)

**Two numbers that did not reproduce.** Re-measured on the reviewed tree
`28742c2b` (whose code is identical to `96a83a6a`) and corrected in the round-0
table: the NG2-4 row is `1 failed, 5 passed` (the test carries six
parametrisations, not five), and the NC2-3 coverage row is `2 failed, 2 passed`
(the quoted command runs the whole class, and two of its four cases fail under
that substitution — the row had quoted the tally of a single-node run).

**Planted failures, measured at `f8140c32`.** Apply the substitution to the named
file, run the command, restore the file from a copy taken before it. Each row
re-creates the defect the review reported and watches the new gate bite; after the
last one `git status --porcelain` named this card alone.

| Guard | Perturbation | Command | Observed |
| --- | --- | --- | --- |
| Fence alphabet | `_account_transcript.j2`: `turn.free_text \| flatten_lines` → `turn.free_text \| replace('\r', ' ') \| replace('\n', ' ')` | `.venv/bin/python -m pytest tests/agents/test_public_account_prompts.py::test_speaker_free_text_cannot_open_a_section_the_template_owns -q` | the `CRLF`, `VT`, `FF`, `FS`, `GS`, `RS`, `NEL`, `LINE SEPARATOR` and `PARAGRAPH SEPARATOR` ids fail — `9 failed, 2 passed` |
| Fenced structured row | `_account_transcript.j2`: `{{ claim.model_dump_json() \| flatten_lines }}` → `{{ claim.model_dump_json() }}` | `.venv/bin/python -m pytest tests/agents/test_public_account_prompts.py::test_a_structured_rows_free_text_cannot_open_a_section_either -q` | `assert ['## Account ... comparisons'] == ['## Account comparisons']` for `NEL`, `LINE SEPARATOR`, `PARAGRAPH SEPARATOR` — `3 failed, 8 passed` |
| Default-path gate | `manager.py`: the `if accounts_enabled` choice of tuples → the unconditional union of both | `.venv/bin/python -m pytest tests/meetings/test_manager.py::TestTeammateObservationFirewall -q` | `AssertionError: ('saw_kill', 'accounts', False)` — the declared scope and the code disagree with the channel OFF — `2 failed, 3 passed` |
| Accounts-arm kill firewall | `manager.py`: `_ACCOUNT_ROLE_PROVING_OBSERVATIONS` → `()` | `.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_an_impostor_menu_answer_naming_its_teammate_never_records -q` | `assert (SawKillObser...room='LABS'),) == ()` — `1 failed` |
| Prompt-set revision | `loader.py`: `ACCOUNT_PROMPT_SET_REVISION = "v2"` → `"v1"` | `.venv/bin/python -m pytest tests/agents/test_public_account_prompts.py::test_no_committed_capture_already_carries_todays_account_stamps -q` | `AssertionError: vote_ballot_accounts.qwen3_6_27b.v1.accounts1.attributed0 is already recorded in audits/investigation-candidate/2026-09-06-meetings.json` — `2 failed` |
| Self co-presence skip | `public_accounts.py`: `if bystander == turn.speaker:` → `if False and bystander == turn.speaker:` | `.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_a_speaker_named_among_its_own_bystanders_impeaches_nobody -q` | `assert (Contradictio...band='weak'),) == ()` — the legal two-room sighting flags again — `1 failed` |
| Proxy fold marker | `public_accounts.py`: `marker = (…)` → `marker = ""` | `.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_every_re_target_against_one_speaker_folds_to_one_belief_lift -q` | `assert 3 == 1` — three distinct lift keys for one speaker — `1 failed` |
| Resolvable endpoints | `public_accounts.py`: the co-present row's `event_id` → `f"{event_id}:co_present:{bystander_index}"` | `.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_a_derived_row_flags_through_an_artifact_id_a_reader_resolves -q` | `assert {'turn:p-2:ob...co_present:0'} == {'turn:p-2:ob...rn:p-2:obs:1'}` — `1 failed` |

**One Codex comment refuted.** 3966002147 asks this card to teach
`eval.alibi_fabrication.compute_alibi_fabrication_rate` about author-retargeted
flags, on the ground that the new subject rewrite inflates the survival rate. The
underlying property is real, but it is not introduced here: the private detector's
Task 10.10 re-target produces the identical shape on the DEFAULT path, with both
levers OFF, and the scorer has always read it the same way — the reproduction is in
the limitation above. Repairing it would redefine a published metric for every arm
including the baseline, in `eval/`, which is outside this card's writer boundary.
It is recorded there as an open item instead.

### Review corrections, round 2 (2026-09-09)

A second review round over the head `113c046c` returned two blocking findings:
one code defect the round-1 endpoint repair traded for the defect it fixed, and
one mis-recorded evidence statement introduced by the round-1 documentation
commit itself. Both were reproduced before being repaired. Neither reaches the
default meeting path, any `audits/` byte or any file in
`experiments/held_out_prefixes.py::GENERATOR_SOURCES`, so no recorded byte moves,
the registry row is unchanged and the frozen held-out manifest still needs no
restamp.

**One code defect: one sentence could contradict itself into a role proof.**
Before round 1 a flag's two endpoints were two artifacts by construction —
`_placements` emitted exactly one row per artifact. The round-1 repair made a
derived row keep its artifact's `event_id` (the derivation moved into
`_Placement.identity`), which made a self-pair reachable: `validate_public_accounts`
checks a sighting's `subject` against the roster and nothing else, so a speaker
may name ITSELF, and one `saw_move` then places that speaker at the `to_room` it
states and at the `from_room` its own witness row infers. Reproduced at
`113c046c` over `engine/maps/canonical_1.yaml` with p-2 speaking
`saw_move(subject='p-2', from_room='ADMIN', to_room='LABS', tick=5)` —
d(ADMIN, LABS) = 3 against two allowed steps — which minted
`kind=alibi_conflict evidence_band=weak` with
`event_a_id == event_b_id == 'turn:p-2:obs:0'`, and
`api.schemas.classify_evidence`, `eval.deduction_metrics.classify_flag` and
`agents.strategic.prompts.loader.classify_flag_for_prompt` each typed it
`role_proof`. All three implement the same documented self-linkage rule, whose
docstring says it exists so a known kind that starts emitting self-linked flags
cannot silently render as a contradiction — and this branch made `alibi_conflict`
start emitting them. So one sentence produced a `weak`-band flag that the
spectator, the eval and the prompt each called a role proof, inside a channel
whose docstring promises to declare no role proven, on the arm whose defining
count of shared role-proof flags is zero. Repaired at `25351035` by skipping a
pair whose two rows come from the same artifact, which is the assumption
`api/schemas.py` already documents. Dropping one of the two rows instead would
have lost a real placement — the speaker's claimed origin would go uncompared —
so the skip is at the pair, and the speaker stays placed against every OTHER
artifact.

**One mis-recorded evidence statement.** The round-0 table's head-drift caveat
said the NG3-5 (slack) row's `contradiction_id` differs at the head "because the
hash source moved from the endpoint pair to the derived identity". It does not:
`_Placement.identity` returns `f"{event_id}:witness"` for a witness row, which is
the exact string the pre-repair endpoint pair hashed, so that id is invariant
under the round-1 repair. What moved is the endpoint the flag carries. Re-measured
with the same substitution (`vision_slack=1` → `vision_slack=0`) and the same
command on each commit, run inside a `git archive` of that commit:

```sh
.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_a_sighting_within_the_granted_slack_is_never_called_impossible -q -vv
```

| Tree | `contradiction_id` | `event_b_id` | Summary |
| --- | --- | --- | --- |
| `96a83a6a` | `public-account-aa6d4eba507d9b36` | `turn:p-2:obs:1:witness` | `1 failed, 1 passed` |
| `113c046c` | `public-account-aa6d4eba507d9b36` | `turn:p-2:obs:1` | `1 failed, 1 passed` |

The caveat above now names the endpoint. It is the third mis-recorded evidence
statement in this card's Results, so every figure in this round was measured on
the tree it is pinned to rather than predicted from a diff.

**Planted failure, measured at `25351035`.** Apply the substitution, run the
command, restore the file from a copy taken before it; afterwards `git status
--porcelain` named this card alone.

| Guard | Perturbation | Command | Observed |
| --- | --- | --- | --- |
| Same-artifact skip | `public_accounts.py`: `if first.event_id == second.event_id:` → `if False and first.event_id == second.event_id:` | `.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_one_sentence_cannot_contradict_itself_into_a_role_proof -q` | the self-named sighting mints a flag again, `ContradictionRef(contradiction_id='public-account-bdfa24d95bbad5ef', kind='alibi_conflict', event_a_id='turn:p-2:obs:0', event_b_id='turn:p-2:obs:0', subjects=('p-2',), …)` — `1 failed` |
