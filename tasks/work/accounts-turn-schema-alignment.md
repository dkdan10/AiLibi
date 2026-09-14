# Make the accounts prompt and the turn schema agree on whereabouts

**Status:** done

## Outcome

On the candidate accounts path, the model is asked only for shapes the turn
schema accepts, so a well-formed answer to the prompt is never refused as an
invalid union tag. The candidate arm's refusal rate and output length are
measured offline against the replay double, and the change is a versioned,
default-OFF prompt-set revision.

## Evidence

[The diagnosis of 2026-09-13](../diagnosis-2026-09-13-live-run-stops.md):
two of the candidate arm's turns across two live runs were billed and refused
on `claims[].type` with the tag `whereabouts` (861 and 1,455 output tokens),
zero refusals in 23 reference-arm attempts, and the candidate arm emits about
617 output tokens per call against the reference arm's 252. The accounts
rules template instructs the model to emit
`{"type":"whereabouts","tick":<int>,"room":"<room id>"}`
(`agents/strategic/prompts/qwen3_6_27b/_account_rules.j2:9`) and the roll-call
template asks for "exactly ONE whereabouts self-placement"
(`accusation_round_roll_call.j2:10,55,116`), while `MeetingTurn.claims` admits
only `alibi`, `accusation` and `corroboration`
(`meetings/schemas.py:373-388,552-556`); `whereabouts` is an observation
shape, and the model places it under `claims`. The accounts-channel hardening
card (`accounts-channel-hardening.md`) aligned the reply prompt's citation
ask with the schema but not this shape. A billed-and-refused turn costs the
candidate arm a full turn's tokens and is replaced by a placeholder, which the
manifest says can only bias the primary outcome in one direction.

## Acceptance

- [x] Reproduce the refusal offline: a turn payload of the shape the accounts
  prompt instructs (a `whereabouts` item under `claims`) fails `MeetingTurn`
  validation with the archived `union_tag_invalid` reason; recorded with the
  command.
- [x] The prompt and the schema agree, by one of two routes chosen and
  justified in Results: the accounts templates place `whereabouts` where the
  schema accepts it and say so unambiguously, or the schema admits the shape
  where the prompt asks for it; a test extracts every shape the accounts
  templates advertise and asserts each is accepted by the schema at the place
  the template names it (extending the prompt/schema agreement test the
  hardening card added).
- [x] The prompt-set revision follows the version-bump cascade (the `.j2`
  marker, `DEFAULT_PROMPT_VERSIONS` in `orchestrator/game.py`, the recorded
  prompt-version pin); if that cascade touches `orchestrator/game.py`, the
  held-out restamp rule applies and is recorded. The default meeting path's
  prompt bytes are unchanged (`generate_prompts --check`, the default-path
  golden, `verify_samples.sh` and the four `--check` runs).
- [x] Measured offline on the replay double from
  [the realism card](fresh-deduction-instrument-realism.md) (or, if that card
  has not landed, on the fake provider with a planted payload of the archived
  refusal's shape): the candidate arm's refusal rate on the previously refused
  shape is zero, and Results states that the live output-length effect can only
  be measured by the owner's calibration decision.
- [x] Every new guard has a planted failure proving it detects the claimed
  defect.

## Constraints

Candidates `public_accounts` and `attributed_testimony` stay default-OFF;
this card adopts nothing and changes no default-path byte. No live provider
call. No change to the frozen analysis of the instrument. One writer:
`meetings/schemas.py`, `meetings/manager.py` and the accounts templates are
yours; do not edit `experiments/fresh_deduction_instrument.py` (the realism
card owns it) or `agents/memory/`. The vent-certificate trade-off statements
in the candidate checkpoints stay as written.

## Expected scope

`agents/strategic/prompts/qwen3_6_27b/_account_rules.j2`,
`accusation_round_roll_call.j2` and the other accounts templates as needed,
`meetings/schemas.py`, `meetings/manager.py` if the placement moves,
`tests/meetings/`, `tests/agents/`, `orchestrator/game.py` only for the
version pin if the cascade requires it (with the restamp), the generated
prompt exports `generate_prompts` maintains, `tasks/README.md`'s derived
inventory sentence, this card. Delivered on
`work/accounts-turn-schema-alignment` and one pull request into `main`.

## Record impact

A versioned prompt-set revision on the default-OFF accounts path; no
recording, report, DTO or weight byte moves; no experiment becomes ON; no
adopting record is created.

## Validation

`uv run pytest tests/meetings tests/agents -q`, `uv run python
scripts/generate_prompts.py --check` (or the gate's form), `bash
scripts/check.sh`, `bash scripts/verify_samples.sh`, the four `uv run python
scripts/build_sample_report.py --sample-dir <set> --check` runs, and
`uv run pytest tests/experiments/test_held_out_prefixes.py -q` if
`orchestrator/game.py` moved.

## Results

Implemented on `work/accounts-turn-schema-alignment`, based on `c15c587f`.
Both account levers stay default-OFF and this card adopts nothing.

### The route, and why this one

`docs/architecture.md` §Explicit cleanup experiments keeps its description of
the accounts channel unchanged: this card moves prompt bytes on that gated
channel and no boundary. §Packages (`meetings/`) locates the turn chokepoint
that refused the two archived turns, and §Enforced boundaries is unaffected —
no new import crosses a contract.

Acceptance offered two routes. **The templates were made to name the field;
the schema was not widened**, because `MeetingTurn` discriminates by FIELD as
well as by tag and the two unions are disjoint by design:
`observations` takes `ObservationClaim` (with `WhereaboutsClaim` in it) and
`claims` takes `alibi` / `accusation` / `corroboration`
(`meetings/schemas.py:267-277,429-432,589-590`). Admitting `whereabouts` under
`claims` would give one sentence two legal homes, and the second home is not
free:

- `api/schemas.py` shadows the two unions separately as `ObservationClaimView`
  and `StatementClaimView` (`api/schemas.py:652-697`), `TurnView` serves both
  (`:738-739`), and `frontend/src/types/api.ts` mirrors them — so a widened
  claims union moves a served DTO and the generated frontend types, which this
  card's Record impact forbids.
- `meetings.transcript.detect_contradictions` indexes a `whereabouts` item as a
  degenerate single-tick self-alibi read off `observations`. A second home
  would make the SAME spoken sentence reach the detector by two paths, which
  changes what the candidate arm measures rather than repairing it.

The template route moves only default-OFF prompt bytes, which is the smaller
measurement impact: the arm keeps exactly the shapes it had, filed where the
schema already takes them.

### What the prompt now says

- **The menu names its list.** `_account_rules.j2` prints two labelled lists —
  `Each item of "observations" is one of these shapes:` and `Each item of
  "claims" is one of these three shapes and nothing else:` — instead of an
  unlabelled shape list followed by a sentence beginning "Claims may be". The
  `whereabouts` bullet says so in its own words: it places the speaker alone,
  names no subject, "so it goes in `"observations"` — it is not one of the
  `"claims"` shapes".
- **The whole turn object is sketched with its lists filled.** The two account
  templates that produce a turn (`_account_opening.j2`,
  `accusation_round_accounts.j2`) print
  `"observations":[<observation shapes, or empty>],"claims":[<claim shapes, or
  empty>]` instead of two empty lists, so the sketch and the menu agree about
  where an item goes. On the attributed-only impostor arm, which is told to
  keep observations empty, the sketch keeps `"observations":[]` literally and
  offers `"claims":[<one accusation claim, or empty>]` — the one shape that arm
  has.
- **Two rendering seams were closed in passing.** `trim_blocks` eats the
  newline after a block tag, so the pre-existing renders ran the last rules
  sentence into the next instruction (`…in public speech.Open the meeting…`)
  and the menu heading into its first bullet (`…every player:- {"type":…`).
  Both sit inside the block this card had to make legible, and the revision
  already moves these bytes, so the include tags now use `{% include … +%}`
  and the heading is its own line. Nothing else about those templates moved.

The default meeting templates were NOT edited. They already file every shape
they advertise in the list the schema takes it in, which is now asserted rather
than assumed (below).

### The reproduction, and what the tests assert

The archived refusal reproduces on the committed tree from the payload shape
alone:

```
.venv/bin/python -c 'from pydantic import ValidationError; from meetings.schemas import MeetingTurn; t={"turn_id":"m:turn-1","turn_index":1,"speaker":"p-1","turn_kind":"reply","reply_to":"m:turn-0","observations":[],"claims":[{"type":"whereabouts","tick":4,"room":"LABS"}],"free_text":"I was in LABS."}
try:
    MeetingTurn.model_validate(t)
except ValidationError as exc:
    print([(e["type"], e["loc"], e["msg"]) for e in exc.errors()])'
```

which prints exactly the archived reason:

```
[('union_tag_invalid', ('claims', 0), "Input tag 'whereabouts' found using 'type' does not match any of the expected tags: 'alibi', 'accusation', 'corroboration'")]
```

The committed form of that reproduction reads the payload out of the prompt
instead of typing it:
`tests/agents/test_public_account_prompts.py::test_the_shape_the_live_run_filed_in_claims_is_refused_exactly_as_recorded`
takes the `whereabouts` sketch the candidate-arm prompt prints, asserts the
prompt files it under `observations`, then asserts the same item under `claims`
raises `union_tag_invalid` at `('claims', 0)` with the archived message.

The agreement gate itself is `_advertised_shapes` plus
`test_every_advertised_shape_is_accepted_in_the_list_the_prompt_names`. It
reads the RENDERED prompt, outside the `<transcript>` fence (that region is
speaker-authored, so no speaker can add a shape to what the gate reads), and
maps every advertised `{"type":…}` sketch to the turn field the prompt names —
either a declaration line naming one field, or a one-line whole-turn sketch
where the shape sits inside that field's list. A shape with neither raises.
Each sketch is then filled with legal values from its own placeholder words and
validated as a `MeetingTurn` in that field, and the same item is asserted
REFUSED in the other field. `test_the_other_live_turn_prompts_file_their_shapes_the_same_way`
runs the same gate over the default set and over the impostor roll-call variant
the diagnosis names beside the accounts menu — neither moves a byte here; both
are now read, so the drift that produced this card cannot recur silently in
either.

### The offline measurement

`tests/meetings/test_account_turn_refusals.py` runs the real account renderers
through a real `MeetingManager` on the candidate arm (both levers on) with a
fake provider that answers every turn with one planted payload, and counts
`MeetingManager.defaulted_calls` — the manager's own record of a turn replaced
by a placeholder, which is what the two archived live refusals produced.
Reproduced with `.venv/bin/python -m pytest tests/meetings/test_account_turn_refusals.py -q`
(2 passed) and, as counts, from the same helper:

| Self-placement filed in | Turn calls | Recorded turns | Defaulted turns | Refusal rate |
| --- | --- | --- | --- | --- |
| `observations` (what the prompt now asks for) | 3 | 3 | 0 | 0.00 |
| `claims` (the archived live shape) | 4 | 3 | 3 | 1.00 |

The refusal rate on the previously refused shape is zero: an answer that obeys
the menu is never refused, and every turn reaches the record carrying the
placement it was asked for. The four turn calls in the second row are three
turns plus the opening's one retry; all three turns still defaulted with
trigger `validation`.

**The output-length half of the diagnosis is not measured here and cannot be.**
A scripted payload has no length of its own, so nothing in this card moves or
measures the candidate arm's ~617 output tokens per call. Whether the menu's
new structure shortens or lengthens a real answer is a live property, and the
diagnosis routes it to the owner's bounded-calibration decision (decision 1 of
that document); no live call was made here.

### Version cascade and the frozen set

The account templates take their identity from
`public_account_prompt_versions`, which composes the stamp from
`ACCOUNT_PROMPT_SET_REVISION` and the two lever values, so the revision is
where a byte change is declared (the hardening card's decision, unchanged).
`ACCOUNT_PROMPT_SET_REVISION` advances `v2` → `v3` with a docstring bullet
saying what moved; the four account templates share the suffix and advance as
a unit, so stamps composed today are
`..._accounts.qwen3_6_27b.v3.accounts<N>.attributed<M>` and
`test_no_committed_capture_already_carries_todays_account_stamps` keeps
failing if any of them already appears in the two committed candidate captures.

`orchestrator/game.py` is untouched: it composes the stamp through the loader
rather than copying it, so no `DEFAULT_PROMPT_VERSIONS` entry and no recorded
prompt-version pin moves, no file in
`experiments/held_out_prefixes.py::GENERATOR_SOURCES` is in this branch's diff
(checked against the list that module exports), the frozen held-out manifest
needs no restamp, and its regeneration test passes unchanged (33 passed). No
`audits/` or `tests/fixtures/` byte moves, so the `docs/artifacts.md` audits
row is unchanged and still reconciles against disk.

### Planted failures

Each row is a perturbation of the committed tree at this card's head: apply the
substitution, run the command, restore the file. `git status --porcelain` was
empty of unintended changes after each restore.

| Guard | Perturbation | Command | Observed |
| --- | --- | --- | --- |
| An advertised shape must name its list | `_account_rules.j2` back to its pre-card body (`git show HEAD:…/_account_rules.j2`), which lists the shapes under no field | `.venv/bin/python -m pytest "tests/agents/test_public_account_prompts.py::test_every_advertised_shape_is_accepted_in_the_list_the_prompt_names" -q` | `AssertionError: the prompt advertises 'whereabouts' without naming the turn field it belongs in: 'Use only the few relevant structured accounts. The same public shapes are available to every player:- {"type":"whereabouts","tick":<int>,"room":"<room id>"}: where you claim to have been.'` — `5 failed, 1 passed` (the sixth arm advertises nothing) |
| The named list must be the one the schema takes | `_account_rules.j2`: the `whereabouts` bullet moved under the `"claims"` heading — the live defect, written into the menu | the same command, and `::test_the_shape_the_live_run_filed_in_claims_is_refused_exactly_as_recorded` | `ValidationError: Input tag 'whereabouts' found using 'type' does not match any of the expected tags: 'alibi', 'accusation', 'corroboration' [type=union_tag_invalid…]` on the accept path, and `AssertionError: assert {'claims'} == {'observations'}` — `6 failed, 1 passed` |
| A prompt-conformant answer is never refused | `test_account_turn_refusals.py`: the zero-refusal test's `place_in="observations"` → `"claims"` | `.venv/bin/python -m pytest tests/meetings/test_account_turn_refusals.py -q` | `assert manager.defaulted_calls == ()` → `Left contains 3 more items, first extra item: DefaultedCall(phase='opening', agent_id='p-1', trigger='validation', turn_index=0, …)` — `1 failed, 1 passed` |

### Verification

All commands run on this branch's tree with this card's text on disk.

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/meetings tests/agents -q` | 2,619 passed |
| `bash scripts/check.sh` | exit 0 — 7,592 Python passed, 20 skipped, 3 xfailed; 515 frontend tests over 19 files; strict mypy on 476 sources; 4 import contracts kept, 0 broken; 390 phase tasks / 390 prompts in sync; 51 work cards; production build |
| `.venv/bin/python scripts/generate_prompts.py --check` | all 390 prompts in sync, exit 0 |
| `bash scripts/verify_samples.sh` | exit 0 — all 100 canonical recordings verified clean (50 + 50) |
| `.venv/bin/python scripts/build_sample_report.py --sample-dir <set> --check` for `replays/samples/4p1i`, `replays/samples/9p2i`, `replays/ml_corpus/4p1i`, `replays/ml_corpus/9p2i` | all four consistent with their replays, exit 0 |
| `.venv/bin/python -m pytest tests/experiments/test_held_out_prefixes.py -q` | 33 passed |

### Limitations

- Prompt bytes on both account arms changed, so captures taken before this
  branch are not comparable to captures taken after. That discontinuity stays
  machine-readable: the pre-hardening captures record `v1`, anything recorded
  between the hardening card and this one records `v2`, and every capture from
  here on records `v3`.
- The gate reads what a prompt ADVERTISES, not what a model does with it. It
  proves that an answer following the menu validates; it cannot prove a model
  will follow the menu. Only a live run can show that, and the diagnosis routes
  that measurement to the owner's calibration decision.
- The gate's coverage is the set of shapes written as a `{"type":…}` sketch.
  A template that described a shape in prose alone would advertise something
  this reader cannot see; no current template does.
- Hardening or clarifying a channel is not evidence that it improves play.
  Adoption of either account profile remains a separate owner decision with its
  own record.
- Delivery state: implemented and verified locally; not owner reviewed, not
  merged.
