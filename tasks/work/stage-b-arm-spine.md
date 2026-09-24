# Declare the Stage-B arms and thread them through one helper

**Status:** ready

## Outcome

Every Stage-B switch exists, default-OFF, before any arm card builds its behaviour. This card
declares the eight fields of the wave's version plan on `RecordedExperimentConfig`, classifies
every field by the layer that reads it, and builds the shared plumbing the arm cards, the readers
card, the record-plumbing card and the census consume:

- the omit-at-default serializer, so no committed payload gains a key;
- `FIELD_LAYER`, the one classification of every config field;
- one engine-arguments helper that every re-simulation site calls, which refuses an engine-layer
  value it cannot thread instead of silently re-simulating the default;
- `WAVE_ARMS_PENDING`, which refuses each new ON value until its arm card removes its name;
- a meeting runner built from the recorded config rather than the environment, with the two new
  ballot fields config-only;
- the tactical options mirror, the trigger-builder keyword, an empty experiment-arm stamp
  registry with a derived stamp suffix, the spectator view mirror and regenerated frontend types.

No arm behaviour is built here. After this card merges, nothing an agent sees or does changes, no
committed byte under `replays/` moves, and every derived view, fixture, gate and doc fact verifies
exactly as before. It pushes no agent toward any answer and labels nothing in a meeting.

**The partial-record principle binds this card.** Only `replays/samples/9p2i`'s seed set is ever
re-recorded, and only into a candidate directory (`replays/candidates/stage-b-r1/9p2i/`, written by
the record card). Every new switch is a `RecordedExperimentConfig` field, default-OFF and omitted
from the payload at its default. Every committed recording, derived view, fixture, gate and doc
fact keeps verifying byte-identically. There is no registry prompt bump: `vote_ballot` stays
`vote_ballot.qwen3_6_27b.v8` and the three `.v6` stamps are unchanged. Role-correctness is
reported and never a gate. Nothing pushes an agent toward the correct answer, and the meeting
layer labels and never rewrites.

## Evidence

Every `path:line` here is at `e886b663`; the implementer re-anchors each by the symbol named
beside it at dispatch (the documentation-truth card lands first and moves lines in
`orchestrator/game.py`). The design is the decision memo's section 1 (the settled mechanism) and
its card-3 dispatch brief in section 3.4, in `stage-b-2026-09-24/decision-memo.md`. The
investigation is `partial_record.md`, sections 1, 2 and 6, in the same directory.

**The owner's rulings of 2026-09-24, verbatim, that this card relies on.**
- Ruling 1: "We should implement stage B"
- The record paragraph: "Let's not re-record all 300 seeds each time. When it's time to record,
  record the smaller group of 50 seeds, assess if the implementations have been effective and
  resulted in desired results. Also it is understood that updating the vent and body reset logic
  will probably have a substantial effect on previous limits and statistics around the baseline
  voting results, that is okay."
- Items 6 to 10 and 13: "What do you think is best?" This delegated the rulings below.
- Ruling 12: "Hold off on ML as D suggests until gameplay is finished."

**The orchestrator's rulings, made under the owner's delegation of 2026-09-24.**
- Decision 0.3 item 2: each new field is omitted from the payload while it holds its default, a
  stated new pattern beside `_preserve_version_one_bytes`; `format_version` stays 1; no format 4.
  After adoption, recordings write adopted values explicitly, so a missing key keeps meaning the
  historical default.
- Decision 0.3 item 4: the ballot arms are two fields; "The suffix is derived from the field name,
  never chosen: drop `_version` and append `_v<value>`." The spine owns the one derivation
  function and a test that fails on a hand-written suffix. v9 stays unallocated.
- Decision 0.3 item 5: the new meeting-profile fields have no env var; they are set only by the
  declared config file.
- Decision 0.3 item 6: once round 1 is recorded, an arm value's meaning is frozen; a revision adds
  a new value and never redefines a recorded one.
- Decision 0.3 item 9: "The spine declares every wave field at once. Each ON value is refused
  (loudly, at config validation) while its name sits in `WAVE_ARMS_PENDING`."
- Section 2.3's optional guards, "taken": the validator refuses evidence version 1 with the reset
  and `post_meeting_retarget` with the reset; "The spine lands both, because the spine owns the
  validator."
- Section 2.4: "The view mirror (`api/schemas.py:1430-1447`, generated types, a
  `PublicResults.tsx` label) lands in the spine for every new field."
- AGENTS.md craft rule 7: prompt-byte and detector changes stay default-OFF behind an explicit
  experimental gate until an adopting record. The dated 2026-09-24 addendum to section 12 of
  `tasks/direction-2026-09-19-process-over-outcome.md` (a `docs:` commit that lands before wave 1)
  amends the stop on adding levers for this wave only and names every new field.

**Why each piece is needed (memo section 1, "Where it fails").**
- The recorder cannot set an engine or tactical arm, and the only runner constructor reads its
  meeting profile from the environment (`orchestrator/game.py:1378`,
  `MeetingEvidenceProfile.from_environment`). The record-plumbing card needs a runner built from a
  declared config.
- "Witness sets live only in events, not in state (`engine/rules.py:146-156`). A reader that
  forgets R7 passes every hash check." The investigator's prototype measured 221 of 221 hashes
  equal with 4 of 28 exits different (memo section 1; the physical-witness card re-measures on its
  own planted tests). So an engine-layer field threaded by hand at each site is a silent-failure
  risk, and the helper must refuse what it does not thread.
- A config format 4 would need a ladder rewrite of `orchestrator/experiment_config.py:65-94`
  (checks on `== 3` and `!= 3`) and `api/replay_loader.py:1455`; omit-at-default replaces it
  (partial_record section 2, "Config format", superseded by decision 0.3 item 2).
- A registry bump for the ballot arms would open an archive and move pins on the three sets left
  behind (partial_record section 6); a recording-bound overlay served from the recorded config
  keeps the live default at v8.

**The code today.**
- `RecordedExperimentConfig` (`orchestrator/experiment_config.py:29-47`) has 14 fields including
  `format_version`, `extra="forbid"` and `frozen=True`. `_preserve_version_one_bytes` (`:96-107`)
  drops four keys by format; `is_default` (`:116-122`) and `normalize_experiment_config`
  (`:137-142`) represent all-OFF as an absent field; `has_tactical_changes` (`:124-134`) decides
  whether experimental policies are built.
- `redistribution_policy` is threaded by hand at each re-simulation advance:
  `orchestrator/game.py:2566-2575`, `api/replay_loader.py:1633-1640`,
  `eval/replay_walk.py:636-643`, and `experiments/tactical_gameplay.py:413-418` (the per-action
  apply). The permutation re-advance at `experiments/tactical_gameplay.py:223` passes none; it runs
  only on baseline recordings (`require_baseline_experiments` in `measure_identity_effects`).
- `ReplayWalkConfig` (`eval/replay_walk.py:298-356`) has one coarse `supports_experiments` flag,
  checked at `:505-508`. Three profiles set it: `current-report` (`eval/balance_eval.py:931-940`),
  `leak-scan-factory` (`eval/leak_scan.py:950-955`) and `process-scorecard`
  (`eval/process_scorecard.py:783-787`).
- `MeetingEvidenceProfile` (`meetings/evidence_profile.py:67-104`) has four fields, each reached
  through one of the four `EXPERIMENT_ENV_NAMES` switches (`:25-32`). `HeadlessGame` compares the
  runner's profile with the config for those four keys (`orchestrator/game.py:2252-2264`).
- `TacticalExperimentOptions` (`agents/tactical/experimental.py:29-63`) mirrors the tactical
  fields plus the derived `meeting_positions_preserved`; `_tactical_experiment_options`
  (`orchestrator/game.py:4422-4433`) builds it.
- `prompt_versions_for_set` (`orchestrator/game.py:661-736`) folds the ambient lever overlays; an
  arm that re-bodies a set's own template is stamped by `_lever_arm_versions` (`:482-497`), and a
  composite joins contributing values with `+` (`:735`). No overlay is keyed on the recorded config.
- `_build_meeting_trigger` (`orchestrator/game.py:3399-3483`) builds the trigger text; its callers
  are `orchestrator/game.py:2681`, `tests/_helpers/committed.py:389` and
  `experiments/held_out_prefixes.py:1134`.
- The spectator mirror is `ExperimentConfigView` (`api/schemas.py:1432-1448`); its optional keys
  are listed in `scripts/gen_frontend_types.py:311-313`; the leak allow-list is
  `tests/api/test_leak.py:497-507`; the labels are `BehaviorIdentity` in
  `frontend/src/components/PublicResults.tsx:6-26`.

**Committed payloads the serializer must keep byte-identical (count-only; re-measure at
dispatch).** 956 non-null `experiment_config` payloads in 101 recordings: 947 rows across the 100
recordings of `audits/deduction-candidate/run-2026-09-16` (479 and 468 across two payload shapes)
and 9 rows in `tests/fixtures/v3_policy_reconstruction/replay-seed-1.jsonl`. Another 237 payloads
sit in five audit JSON files (41, 41, 42, 13 and 100). All 1,193 parse and re-serialize equal to
their committed form at `e886b663`. The four committed sets carry no `experiment_config` key. The
commands are under Validation.

## Acceptance

- [ ] **The eight fields and `FIELD_LAYER`.** `RecordedExperimentConfig` declares, after the
  existing fields and in this order: `vent_witness_rule: Literal["both_rooms", "physical"] =
  "both_rooms"`; `vent_entry_policy: Literal["any_body", "own_fresh_kill"] = "any_body"`;
  `report_body_handle_version: Literal[1] | None = None`; `ballot_kill_row_version: Literal[1] |
  None = None`; `impostor_ballot_version: Literal[1] | None = None`. `vent_exit_policy` gains the
  value `look_and_wait` (default `target_distance`; `observed_risk` kept). `meeting_reset` and
  `bounded_rebuttal_version` are declared already and are unchanged. `FIELD_LAYER` is an
  immutable mapping of every model field to one of `format`, `engine`, `orchestrator`, `tactical`
  or `meeting`; the wave's fields follow the memo's version plan (engine: `vent_witness_rule`;
  tactical: both vent policies; orchestrator: `meeting_reset`, `report_body_handle_version`;
  meeting: `bounded_rebuttal_version` and both ballot fields). Each existing field is classified by
  the consumer that reads it, recorded in Results. Mechanism: a test comparing `FIELD_LAYER`'s keys
  with `model_fields`. Planted: a config model with one extra, unclassified field fails it.
- [ ] **Omit at default.** A new serializer rule beside `_preserve_version_one_bytes` drops each
  of the five new fields from the payload while it holds its default, under every
  `format_version`; the declared wave config serializes with `format_version` 1. Mechanism: a
  committed-bytes test that parses each of the 956 recorded payloads and 237 audit-JSON payloads
  and re-serializes it (compact sorted-key JSON, as `_stable_json` in `orchestrator/replay.py`
  writes rows) byte-equal to the committed text; a default config dumps none of the five keys;
  a config built with `model_construct` carrying an ON value dumps its key; the JSON schema still
  lists every typed field. Perturbed: with the new rule removed, the committed-bytes test fails on
  the first archive row. `is_default` and `normalize_experiment_config` keep reading a config
  whose new fields sit at default as all-OFF.
- [ ] **The pending guard.** `WAVE_ARMS_PENDING` is an immutable mapping from field name to its
  refused values: `vent_witness_rule` `physical`; `vent_exit_policy` `look_and_wait`;
  `vent_entry_policy` `own_fresh_kill`; `report_body_handle_version` 1; `ballot_kill_row_version`
  1; `impostor_ballot_version` 1. Mechanism: config validation raises naming the field and value;
  `HeadlessGame` construction re-checks, so a config built with `model_construct` past validation
  is still refused; `build_default_meeting_runner` refuses a profile carrying a pending ballot
  field. Planted: the refusal test is parametrized from `WAVE_ARMS_PENDING`'s live contents, each
  value once through validation and once through `model_construct` into `HeadlessGame`, with a
  guard that fails on an empty mapping; at this card's head it covers all six values, and an arm
  card that deletes its own names needs no edit to `tests/orchestrator/test_experiment_arms.py`
  (the ballot card, last, deletes the test with the guard). Adverse: every ON value that exists at `e886b663` still
  validates and constructs (`least_remaining_work`, `hub_with_grace`, `patrol`, `accompany`,
  `observed_risk`, `post_meeting_retarget`, `self_report`, `two_thirds`,
  `bounded_rebuttal_version` 1, and the payload shapes of the committed archive and v3 fixture).
- [ ] **The two reset guards.** Validation refuses `evidence_reasoning_version` 1 with
  `meeting_reset="hub_with_grace"`, and `post_meeting_retarget` with `hub_with_grace`, each message
  naming both fields in plain words. Mechanism: the model validator. Planted: both pairs raise.
  Adverse: evidence version 2 with the reset still validates (the shape
  `tests/orchestrator/test_public_regroup_evidence.py:60` uses), and a count-only scan shows no
  committed payload and none of the lab's nine candidate configs
  (`experiments/tactical_gameplay.py:95-110`, `candidate_configs`: a baseline and eight one-change
  arms) combines either pair.
- [ ] **One engine-arguments helper.** One function in `orchestrator/experiment_config.py` takes
  the recorded config (or `None`) and returns the `advance_tick` keyword arguments for every
  engine-layer field it threads (today `redistribution_policy`), raising and naming any
  engine-layer field set to a non-default value it does not thread. Every re-simulation advance
  calls it: the live tick (`orchestrator/game.py:2566`), the loader (`api/replay_loader.py:1633`),
  the walk (`eval/replay_walk.py:636`) and both lab sites (`experiments/tactical_gameplay.py:223`
  and `:413-418`, where the per-action apply takes the same arguments). The `apply_meeting_result`
  sites keep passing their two named fields. Mechanism: the helper plus an `ast` scan of those four
  modules that fails on an `advance_tick` or `_apply_action` call not taking the helper's
  arguments. Planted: `FIELD_LAYER` extended with a fake engine field set non-default makes the
  helper raise, where a hand-threaded call would re-simulate the default; a fixture module passing
  `redistribution_policy=` by hand fails the scan. With no config the arguments equal today's.
- [ ] **Walk configs thread or refuse by layer.** `ReplayWalkConfig` gains `threaded_layers`,
  the layers besides the engine whose fields the profile's consumer reads, and `_walk_replay`
  refuses before its first advance a recording that sets one of the five new fields, or the
  `look_and_wait` value, outside those layers, naming field and profile. Engine-layer fields go
  through the helper, which refuses what it cannot thread. Fields that exist at `e886b663` keep
  today's `supports_experiments` meaning. Every profile keeps an empty `threaded_layers` here, so
  the existing experiment-supporting profiles refuse the new fields until their owner declares
  their layers, and their files are not edited here. One owner per profile, each with its own
  acceptance item: `current-report` (`eval/balance_eval.py:933`), validity and kill-gift go to
  record plumbing; `leak-scan-factory` (`eval/leak_scan.py:951`) to the physical-witness card;
  `process-scorecard` (`eval/process_scorecard.py:787`) to the meeting-reset card; the two lab
  profiles derived from `current-report` with `replace` (`experiments/tactical_gameplay.py:199`,
  `:363`) to the look-and-wait card. The readers card owns the five instruments it widens, and
  the census declares its own. Each owner's item proves two things: the profile reads a fake
  full-config recording with every hash verified, and it refuses a planted unknown field by name
  before its first advance. A fake full-config recording is a copy of a fake-provider recording
  made on arms that exist today, its tick rows and footer rewritten to carry every other wave
  field at its ON value while the pending set is patched empty; `vent_witness_rule` is set there
  only once the physical-witness card has made the helper thread it. A planted unknown field is a
  stand-in added to the config model and `FIELD_LAYER` in a layer the profile does not declare,
  as in this item's own tactical-layer case. Planted: a walk whose engine threading is patched to omit
  `redistribution_policy` refuses a fake `least_remaining_work` recording naming the field; a
  profile without the tactical layer refuses a copy of a fake recording whose rows carry
  `vent_entry_policy="own_fresh_kill"` (pending set patched empty for the test), and accepts it
  once the layer is declared.
- [ ] **A runner built from the recorded config.** `build_default_meeting_runner(profile=...)`
  serves the given profile instead of reading the environment, and raises if any
  `EXPERIMENT_ENV_NAMES` switch is exported ON beside it: the declared config is the one source.
  `profile_from_config` in `meetings/evidence_profile.py` builds the profile from the meeting-layer
  values the orchestrator selects by `FIELD_LAYER`; `meetings/` does not import the wiring module
  (`orchestrator/experiment_config.py:3-4`). `MeetingEvidenceProfile` gains
  `ballot_kill_row_version` and `impostor_ballot_version`, config-only: `from_environment` never
  sets them, and `EXPERIMENT_ENV_NAMES` (four names) and `.env.example` do not change. The
  agreement loop covers the two new fields with exact equality in both directions; the four
  existing keys keep their rule. The stamps a runner serves and the profile it renders come from
  one source. Mechanism: the constructor and the loop, with a test that `FIELD_LAYER`'s meeting
  fields equal the profile's fields (planted drift fails). Proofs: a fake-provider 9p2i game built
  from a declared config with `meeting_reset="hub_with_grace"` and `bounded_rebuttal_version=1`,
  in a bare environment, records both keys on every tick row and the footer; the same config with
  a bare env-built runner raises; with the pending set patched empty, a runner serving
  `ballot_kill_row_version=1` under a config without it raises, and so does the reverse; a
  profile plus an ambient `AILIBI_BOUNDED_REBUTTAL=1` raises.
- [ ] **The tactical options mirror.** `TacticalExperimentOptions` gains `vent_entry_policy` and
  the `look_and_wait` value; `_tactical_experiment_options` passes `vent_entry_policy`;
  `has_tactical_changes` counts it. A value whose behaviour is not built (`look_and_wait`,
  `own_fresh_kill`) raises a named error when a policy is built with it, rather than running the
  default in its place. Mechanism: a test that the tactical fields of `FIELD_LAYER` equal the
  options' fields minus the derived `meeting_positions_preserved`. Planted: drift fails;
  `ExperimentalImpostorPolicy` built with `look_and_wait` raises, where the exit branch
  (`agents/tactical/experimental.py:193`) would otherwise fall through to `target_distance`.
- [ ] **The trigger keyword.** `_build_meeting_trigger` takes `report_body_handle_version`,
  passed from the recorded config at the live call site. `None` keeps today's text byte for byte;
  a non-`None` value raises until the body-handle card replaces the refusal with its substitution.
  The two other callers keep the default. Mechanism: the keyword. Planted: value 1 raises; the
  golden on s9 and s4 is unchanged.
- [ ] **Arm stamps, derived.** `orchestrator/game.py` gains an empty experiment-arm stamp
  registry (config field name to the templates its arm re-bodies) and one function deriving a
  stamp suffix from a field name and value: drop `_version`, append `_v<value>`.
  `prompt_versions_for_set(..., experiment_config=...)` folds ON arms after the lever overlays, in
  field-declaration order, on the existing per-template `+` rule, each stamp being
  `_lever_arm_versions`'s form with the derived suffix. Mechanism: the fold, the function and a
  derivation test. Proofs: with no config or a default config, every registered set returns
  today's mapping by identity; a planted entry keyed on `bounded_rebuttal_version` for
  `accusation_round` is served, as `accusation_round.qwen3_6_27b.v6.bounded_rebuttal_v1`, only for
  a config that carries the arm, and composes with an ON lever overlay by the `+` rule;
  `ballot_kill_row_version` 1 derives `ballot_kill_row_v1` and `impostor_ballot_version` 1 derives
  `impostor_ballot_v1`; a field not ending in `_version` raises; a planted entry that supplies a
  literal stamp string fails the derivation test.
- [ ] **The view, the types and the labels.** `ExperimentConfigView` mirrors every new field and
  value; the five new keys join the optional list in `scripts/gen_frontend_types.py`, and
  `frontend/src/types/api.ts` and `api.fidelity.ts` are regenerated; the five names join the leak
  allow-list. `BehaviorIdentity` names each new ON field in plain words (proposed: "vent use seen
  only in the room where it happens"; "body reports without the time of death"; "witnessed kills
  listed on the voter's ballot"; "impostor ballots cast by strategy"), and `vent_entry_policy`
  joins the movement-policy condition. No label carries a task or audit ID, unexplained jargon or
  threshold arithmetic; a term a label introduces gets a `docs/glossary.md` entry. Mechanism:
  `gen_frontend_types.py --check`, the leak test, a vitest render. Planted: a group with each new
  field ON renders its phrase; a default group reads "No enabled experiments recorded. This alone
  does not certify the default behavior." unchanged; a payload missing the five keys validates
  with defaults; removing one name from the allow-list fails the leak test.
- [ ] **Publication: the shown data does not move.** The demo bundle built by
  `scripts/build_demo_bundle.py` at the base and at the head has a byte-identical baked data tree
  (every file under `data/`, compared by a sha256 listing), and the `PublicResults` text of every
  shown group is unchanged. The compiled frontend differs only by the label strings this card
  adds, named file by file in the PR. Mechanism: the listing diff and `npm --prefix frontend run
  e2e`. Perturbed: a one-byte edit to a baked file in a scratch copy makes the listing diff
  non-empty.
- [ ] **The OFF path is byte-identical.** The golden on s9 and s4; `verify_samples` run once per
  set directory on all four sets; the four `build_sample_report --check` runs;
  `publish_process_scorecard --check`; the c9 refit pins including `uv run pytest -m campaign`;
  `check_doc_facts`; offline `verify_ml_evidence`; and the lab's committed rows
  (`tests/experiments/test_tactical_gameplay.py`) all pass unchanged. The census `--check` does
  not exist yet (the census card merges after this one). Perturbed: a scratch copy of one s4 game
  with one tick row's state hash edited fails `verify_samples` on that copy.
- [ ] **Documentation as contract.** A new page, `docs/experiment-arms.md`, states the wave's
  arms: the eight fields and their layers, omit-at-default and what a missing key means, the
  pending guard and who empties it, the one helper, the config-only ballot fields, and the
  frozen-value rule. The "Explicit cleanup experiments" section of `docs/architecture.md`
  (`:143-165`) links it in one sentence. The architecture page is held to 1,300 words by
  `_ARCHITECTURE_WORD_BUDGET` in `tests/scripts/test_check_doc_facts.py` (`_word_budget_problems`,
  whitespace split); it had 1,295 at `e886b663`, and the documentation-truth card may use the
  spare words first. The constant stays unedited: if the linking sentence does not fit, condense
  prose on the same page that restates another document, and Results records the final count. The policy-stamp docstring
  (`orchestrator/replay.py:520-546`, `FSM_DEFAULT_POLICY_ID` and
  `fsm_default_tactical_policy_stamp`) states that `fsm-default` plus a recorded tactical arm means
  `ExperimentalImpostorPolicy`, which the replay's `agent_factory_kind` records. Mechanism:
  `check_doc_facts`, the word-budget test, and a test that reads `docs/experiment-arms.md` and
  requires each wave field named in `FIELD_LAYER`, and that the architecture section links the
  page. Planted: a copy of the page missing one field name fails it, and so does a copy of the
  section without the link.

## Constraints

**Wave and order.** Wave 1, card 3 of the memo's section 3.1. It starts after the
documentation-truth card (`tasks/work/docs-truth-typed-trigger.md`) has merged and the 2026-09-24
direction addendum has landed as a `docs:` commit. It merges second, after that card and before
the census (`gameplay-census`, which merges after this card and before any arm card) and before
every wave-2 card: the readers card, the record-plumbing card and the physical-witness card all
start once this card has merged. The critical path is documentation truth, then this card, then
readers, then the meeting reset, then the ballot card, then the record. Every merge is the
owner's.

**Shared files, one writer at a time (memo section 3.2).**
- `orchestrator/game.py`: after the documentation-truth card's trigger construction. This card's
  regions: the live tick (`:2566`), `build_default_meeting_runner` (from `:1322`; profile read
  `:1378`), the agreement loop (`:2252-2264`), the construction refusal in `HeadlessGame.__init__`,
  the tactical options (`:4422-4433`), the `_build_meeting_trigger` keyword and its live call, the
  new experiment-arm registry and `prompt_versions_for_set` (`:661`). Later, serially: the
  body-handle card (`_build_meeting_trigger` body), the meeting-reset card, the ballot card (its
  two registry entries).
- `orchestrator/experiment_config.py`: this card owns it. Declared exception: the physical-witness,
  look-and-wait, body-handle and ballot cards each delete only their own pending names, the
  physical-witness card also adds its helper line, and the ballot card, last, empties the mapping
  and deletes the guard, its call sites and its refusal test (craft rule 3).
- This card first, then later cards serially: `meetings/evidence_profile.py` (then the ballot
  card), `agents/tactical/experimental.py` and `experiments/tactical_gameplay.py` (then
  look-and-wait), `eval/replay_walk.py` and `api/replay_loader.py` (then the meeting reset),
  `orchestrator/replay.py` (the docstring; then the meeting reset).
- `docs/architecture.md` (one linking sentence) and `docs/glossary.md`: after the
  documentation-truth card, before the record card and the meeting-reset card respectively. The
  new `docs/experiment-arms.md` is this card's; the record card may later add its one candidate
  sentence there.
- Single writer: `api/schemas.py`, `frontend/src/types/api.ts`,
  `frontend/src/types/api.fidelity.ts`, `frontend/src/components/PublicResults.tsx`,
  `tests/api/test_leak.py`, and with them `scripts/gen_frontend_types.py` and
  `frontend/src/components/PublicResults.test.tsx`.
- Not touched: `eval/balance_eval.py`, `eval/leak_scan.py`, `eval/process_scorecard.py`,
  `tests/_helpers/committed.py`, `tests/meetings/test_prompt_byte_golden.py`, `engine/`, the
  prompt set and every recorded byte. Other cards own them.

**No behaviour.** No arm is built: the pending guard, the policy refusal and the trigger refusal
keep every new ON value unreachable. No `AILIBI_*` lever and no environment switch is added;
`AILIBI_BOUNDED_REBUTTAL` stays in the registry. No template body, no registry prompt bump, no
scorecard cell, no tour or featured-list change (ruling 11), no ML training or refit (ruling 12).
Missing config keeps meaning the historical defaults; invalid input raises, never a silent
fallback. No module-level mutable state: `FIELD_LAYER`, `WAVE_ARMS_PENDING` and the arm registry
are immutable mappings. `agents/` imports no `engine/`, and the import-linter contracts hold.

**Spend and providers.** `$0`. The fake provider and scripted clients only: no live call, no
`.env` read, no held-out band opened, no recorder run into `replays/`.

**Delivery.** Branch `work/stage-b-arm-spine`, one pull request into `main`, merged as a merge
commit or a fast-forward and never squashed; a pushed commit is never amended; `main` is merged
into the branch, never rebased onto. Every commit body ends with the trailer
`Card: tasks/work/stage-b-arm-spine.md` immediately followed by
the `Co-Authored-By:` attribution line the worker's own session supplies (never a model name copied from this card). The PR body has the sections Summary,
Definition of done (this Acceptance list, ticked with evidence), Decisions and Questions, and ends
with the Claude Code attribution line. Agents post no PR comments. `bash scripts/check.sh` is
reported with its real exit code. Status and `tasks/README.md` are the orchestrator's: the worker
fills Results and leaves the Status line, whose flip re-derives the index's inventory sentence.

**Stop and ask** before: moving any committed byte; adding a field or value beyond the version
plan; editing a file another card owns; or finding a committed payload that no longer
round-trips. Each is raised in the PR's Questions for the orchestrator and, where protected, the
owner.

## Expected scope

- `orchestrator/experiment_config.py`: the five fields and the `look_and_wait` value, the
  omit-at-default rule, `FIELD_LAYER`, the engine-arguments helper, `WAVE_ARMS_PENDING` and its
  check, the two reset guards, `has_tactical_changes`.
- `orchestrator/game.py`: the regions listed under Constraints.
- `meetings/evidence_profile.py`: the two ballot fields and `profile_from_config`.
- `agents/tactical/experimental.py`: the option field, the value, the not-yet-built refusal.
- `api/replay_loader.py` (`:1633` only), `eval/replay_walk.py` (the helper at `:636`,
  `threaded_layers` and the refusal), `experiments/tactical_gameplay.py` (`:223`, `:413-418`).
- `orchestrator/replay.py`: the policy-stamp docstring only.
- `api/schemas.py`, `scripts/gen_frontend_types.py`, the two regenerated type files,
  `frontend/src/components/PublicResults.tsx` and its test, `tests/api/test_leak.py`.
- Tests: `tests/orchestrator/test_experiment_config.py` (extended), a new
  `tests/orchestrator/test_experiment_arms.py` (committed bytes, pending guard, helper scan,
  runner, stamps), `tests/eval/test_replay_walk.py` (the walk refusals),
  `tests/orchestrator/test_substrate_binding.py` or `tests/agents/test_bespoke_prompt_sets.py`
  for the identity pin, as the implementer finds them.
- `docs/experiment-arms.md` (new: the arm contract), `docs/architecture.md` (one linking
  sentence), `docs/glossary.md` (label terms only), this card's Results.

Directly necessary follow-through inside these files is permitted and named in Results. A test
elsewhere that pins a served view payload carrying a config is re-pinned only if it is the view
mirror's own consequence, and each such file is named in the PR.

## Record impact

Default-OFF. No committed byte moves: nothing under `replays/`, no fixture, no audit, no report,
no MANIFEST, no doc fact. No rendered prompt byte and no detector output changes: every new ON
value stays refused until its arm card lands, and every default serves today's bytes. The committed
payloads that carry a config (956 recorded rows and 237 audit-JSON payloads) re-serialize
byte-identically under the new rule, which the committed-bytes test enforces. The ladder tip stays
at baseline 9; the ML fits are untouched (the c9 pins prove it).

**Publication.** This card touches `api/` and `frontend/`, and a push to `main` republishes the
demo bundle (`.github/workflows/pages.yml`, AGENTS.md "Delivery"). What the merge publishes: a
bundle whose baked data is byte-identical and whose `PublicResults` text is unchanged for every
shown group, because no shown recording carries a config. The compiled frontend changes only by
the new label strings, which render for no shown game. The owner's merge is that publication
decision, and the PR says so.

**Compatibility.** A recording without the new keys reads as the historical defaults, now and
after adoption. The view accepts older payloads that omit the five keys. Adoption, graduation and
a config-field retirement procedure are later cards' work (memo section 1, "What adoption means
later").

## Validation

```
# count-only census of committed config payloads (re-measure; expect 947 over 100 files, 9, and 41 41 42 13 100)
git grep -c '"experiment_config":{' -- 'audits/deduction-candidate/run-2026-09-16/*.jsonl'
git grep -c '"experiment_config":{' -- 'tests/fixtures/v3_policy_reconstruction/*.jsonl'
grep -c '"experiment_config": {' audits/deduction-candidate/2026-09-06-mechanisms.json \
  audits/investigation-candidate/2026-09-06-meetings.json \
  audits/investigation-candidate/2026-09-06-normal-policies.json \
  audits/investigation-candidate/candidate-handoff.json \
  audits/deduction-candidate/run-2026-09-16/usage-reconciliation.json
# the card's tests
uv run pytest tests/orchestrator/test_experiment_config.py tests/orchestrator/test_experiment_arms.py \
  tests/orchestrator/test_substrate_binding.py tests/eval/test_replay_walk.py tests/api/test_leak.py \
  tests/agents/test_bespoke_prompt_sets.py tests/experiments/test_tactical_gameplay.py -q
uv run lint-imports && uv run mypy .
# the OFF path
uv run pytest tests/meetings/test_prompt_byte_golden.py -q
bash scripts/verify_samples.sh replays/samples/9p2i
bash scripts/verify_samples.sh replays/samples/4p1i
bash scripts/verify_samples.sh replays/ml_corpus/9p2i
bash scripts/verify_samples.sh replays/ml_corpus/4p1i
uv run python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/samples/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/4p1i --check
uv run python scripts/publish_process_scorecard.py --check
uv run pytest -m campaign -q
# the view, the types and the frontend
uv run python scripts/gen_frontend_types.py --check
npm --prefix frontend test
npm --prefix frontend run e2e
# publication: build at the base, then at the head, into fresh scratch directories
uv run python scripts/build_demo_bundle.py --out "$SCRATCH/bundle-base"   # at the base
uv run python scripts/build_demo_bundle.py --out "$SCRATCH/bundle-head"   # at the head
(cd "$SCRATCH/bundle-base" && find data -type f -exec shasum -a 256 {} + | sort -k2) > "$SCRATCH/base.sha"
(cd "$SCRATCH/bundle-head" && find data -type f -exec shasum -a 256 {} + | sort -k2) > "$SCRATCH/head.sha"
diff "$SCRATCH/base.sha" "$SCRATCH/head.sha"                   # empty
diff -rq "$SCRATCH/bundle-base" "$SCRATCH/bundle-head"          # only the label-carrying assets
# documents and evidence
uv run python scripts/check_doc_facts.py && uv run python scripts/validate_task_docs.py
uv run python -c "print(len(open('docs/architecture.md').read().split()))"   # at most 1300
uv run python scripts/verify_ml_evidence.py                     # offline; never --complete
git diff --stat $(git merge-base origin/main HEAD) HEAD -- replays audits tests/fixtures   # empty
bash scripts/check.sh; echo "check.sh exit $?"                 # whole, in a clean worktree
```

`shasum -a 256` is `sha256sum` on Linux. `check.sh` runs with `set -e`, so a red pytest leg
masks the frontend leg: report the real exit code, and run a masked leg on its own beside it.
Results cites `docs/architecture.md` "Determinism and the substrate ladder" and "Explicit cleanup
experiments" with the new `docs/experiment-arms.md`, the memo's sections 1 and 3.4, and the rulings
above.

## Results

Not started. The worker fills this section: the architecture and memo sections the change
implements; the `FIELD_LAYER` classification of each existing field and the consumer that decided
it; the label wording as merged, with any glossary entry; the file-by-file compiled-asset delta of
the bundle; every command above with its exit code and count; the planted and perturbed failures,
each shown red before and green after; material decisions; and limitations (at least: no arm
behaviour exists, so the pending values are proved refused, never proved to work).
