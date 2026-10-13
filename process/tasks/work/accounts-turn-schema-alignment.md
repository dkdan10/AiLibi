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

- [x] Review correction: the shape gate reads the default set's and the
  roll-call variant's OPENING prompts as well as their statements, so the
  coverage Results claims for those two families is the coverage the gate has.
- [x] Review correction: that default-set/roll-call guard has planted failures
  of its own — one per destination route its reader accepts — and the round-0
  planted rows are re-run against the widened reader to show it still bites.
- [x] Review correction: the whole-turn response example the account templates
  print is valid JSON again on every arm, and a gate parses every response
  example the account prompts and the default set print, so a model that copies
  the final example is not refused before its fields are read.
- [x] Review correction: all three Codex inline comments on `bc0a75f6` are
  dispositioned below — one repaired, two refuted in writing against the
  precedent and the reproduction each refutation rests on.
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
- **The return instruction names the destination; the example stays copyable
  JSON.** The two account templates that produce a turn (`_account_opening.j2`,
  `accusation_round_accounts.j2`) keep `"observations":[],"claims":[]` in the
  whole-turn example — that line is the object a model copies, so it has to
  parse — and say where a structured item goes in the sentence above it: "fill
  each structured item into the list its shape is listed under above, and put
  nothing else in either list". On the attributed-only impostor arm, which has
  no shape menu, that sentence reads "keep `"observations"` empty and put your
  one accusation claim, if you make one, in `"claims"`" instead. The first
  draft of this card put those destinations INSIDE the example, which cost the
  example its JSON; round 1 below records the defect and the repair.
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
a declaration line naming one field, a one-line whole-turn sketch where the
shape sits inside that field's list, or a sentence that names the shape and its
field together (`a structured "saw_vent" observation`, the form the default
opening uses inside its rules block). A shape with none of the three raises.
Each sketch is then filled with legal values from its own placeholder words and
validated as a `MeetingTurn` in that field, and the same item is asserted
REFUSED in the other field. `test_the_other_live_turn_prompts_file_their_shapes_the_same_way`
runs the same gate over the default set and over the impostor roll-call variant
the diagnosis names beside the accounts menu — neither moves a byte here. BOTH
live turn prompts of each are read, the opening (`crewmate_report.j2` /
`impostor_report.j2`, or the roll-call variant of the second) and the statement
under both turn kinds, so the drift that produced this card cannot recur
silently in either. The first draft of this gate read only the statements while
claiming both; round 2 below records that gap, the reader change that closed it,
and the planted failures that prove the extended guard bites.

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

Each row is a perturbation of the committed tree at the round-0 head
`bc0a75f6`: apply the
substitution, run the command, restore the file. `git status --porcelain` was
empty of unintended changes after each restore.

| Guard | Perturbation | Command | Observed |
| --- | --- | --- | --- |
| An advertised shape must name its list | `_account_rules.j2` back to its pre-card body (`git show HEAD:…/_account_rules.j2`), which lists the shapes under no field | `.venv/bin/python -m pytest "tests/agents/test_public_account_prompts.py::test_every_advertised_shape_is_accepted_in_the_list_the_prompt_names" -q` | `AssertionError: the prompt advertises 'whereabouts' without naming the turn field it belongs in: 'Use only the few relevant structured accounts. The same public shapes are available to every player:- {"type":"whereabouts","tick":<int>,"room":"<room id>"}: where you claim to have been.'` — `5 failed, 1 passed` (the sixth arm advertises nothing) |
| The named list must be the one the schema takes | `_account_rules.j2`: the `whereabouts` bullet moved under the `"claims"` heading — the live defect, written into the menu | the same command, and `::test_the_shape_the_live_run_filed_in_claims_is_refused_exactly_as_recorded` | `ValidationError: Input tag 'whereabouts' found using 'type' does not match any of the expected tags: 'alibi', 'accusation', 'corroboration' [type=union_tag_invalid…]` on the accept path, and `AssertionError: assert {'claims'} == {'observations'}` — `6 failed, 1 passed` |
| A prompt-conformant answer is never refused | `test_account_turn_refusals.py`: the zero-refusal test's `place_in="observations"` → `"claims"` | `.venv/bin/python -m pytest tests/meetings/test_account_turn_refusals.py -q` | `assert manager.defaulted_calls == ()` → `Left contains 3 more items, first extra item: DefaultedCall(phase='opening', agent_id='p-1', trigger='validation', turn_index=0, …)` — `1 failed, 1 passed` |

### Verification

All commands run at the round-0 head `bc0a75f6`, with this card's text on
disk.

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

### Review corrections, round 1 (2026-09-14)

One review lens returned one blocking finding over the head `bc0a75f6`: the
three Codex inline comments on that head were left undispositioned, and the P2
among them is a real defect. All three are dispositioned here — one repaired at
`2bddbde2`, two refuted. No other finding was returned, and no number in the
round-0 tables above failed to reproduce.

**Repaired: the response example was no longer valid JSON** (Codex 4002032957,
P2, `_account_opening.j2:14`). The first draft named each shape's destination
inside the whole-turn example, so the line printed after `Return only JSON` read
`…"observations":[<observation shapes, or empty>],"claims":[<claim shapes, or
empty>],…`. Reproduced on `bc0a75f6`:

```
git checkout bc0a75f6 -- agents/strategic/prompts/qwen3_6_27b
.venv/bin/python -c 'import json
from agents.strategic.prompts import build_prompt_renderers
r = build_prompt_renderers("qwen3_6_27b", env={}, public_account_version=1, attributed_testimony_version=1)
p = r.crewmate_report(agent_id="p-1", current_tick=8, meeting_trigger="Emergency meeting", rendered_memory="own memory", public_transcript="", living_ids=("p-2","p-3"))
line = [l for l in p.splitlines() if l.startswith("{\"turn_id\"")][0]
json.loads(line)'
```

→ `json.decoder.JSONDecodeError: Expecting value: line 1 column 101 (char 100)`.
The pre-card example parsed, and every default-ON template's example still
parses (`crewmate_report.j2`, `impostor_report.j2`, both branches of
`accusation_round.j2`), so this card was the one place that broke the property.
It matters because `llm/featherless_client.py` calls the provider with
`response_format={"type": "json_object"}` and no schema-guided decoding: a model
that imitates an unparseable final example is refused as a whole turn, billed
and replaced by a placeholder — the same outcome this card exists to remove,
reached by a different route.

Repaired by the route the finding's first option names. The example goes back to
`"observations":[],"claims":[]` on every account arm and the destination moves
into the return instruction beside the labelled menu, quoted in the corrected
bullet above. Nothing about the shape/field agreement depends on the example:
`_advertised_shapes` reads the accounts menu through its two DECLARATION lines
(`Each item of "observations" is one of these shapes:` and the `"claims"`
heading), and the whole-turn-sketch route it also supports is what the default
set and the roll-call variant use. `ACCOUNT_PROMPT_SET_REVISION` stays `v3`: no
committed capture carries a `v3` stamp — `.venv/bin/python -m pytest
"tests/agents/test_public_account_prompts.py::test_no_committed_capture_already_carries_todays_account_stamps"
-q` → `2 passed` — so this branch is still one unrecorded revision of those
bodies rather than a second generation of a published one.

The repair is pinned by two new gates in
`tests/agents/test_public_account_prompts.py`:
`test_every_account_response_example_is_copyable_json` parses every whole-object
example each account arm prints, asserts the turn examples carry the eight keys
with both lists empty, and asserts the prose destination is present on exactly
the arms that have a menu; `test_the_default_sets_response_examples_are_copyable_json_too`
reads the default set on the same terms, so the property is not asserted only
where it just broke.

**Refuted: `_PLACEMENT` is not module-level mutable state in the sense the rule
governs** (Codex 4002032953, P1, `tests/meetings/test_account_turn_refusals.py:43`).
AGENTS.md rule 5 is a load-bearing ARCHITECTURE rule about which object owns
runtime state — "Explicit objects own state" — and the repository applies it to
production modules, not to a test module's literal fixtures. Twenty-four other
test modules carry a module-level `dict`/`list` fixture on the same terms
(`grep -rlE '^[A-Za-z_][A-Za-z0-9_]*(: *(dict|list)\[[^]]*\])? *= *(\{|\[)'
tests --include='*.py' | wc -l` → `25`, this module included), among them
`tests/eval/test_funnel.py:150` (`_ROLES`) and `tests/engine/test_rules.py:264`
(`_IN_VENT_ACTION_TABLE`). The concrete risk the comment names does not exist
here either: `grep -n "_PLACEMENT" tests/meetings/test_account_turn_refusals.py`
returns exactly two lines — the definition and `payload[place_in] = [_PLACEMENT,
*payload[place_in]]` — the dict is never written to, and the enclosing `_answer`
returns `json.dumps(payload)`, so no alias of it escapes the call. Rewriting it
would change no behaviour and would cost the fixture the single place its value
is written down.

**Refuted: the flagged lines state the defect, not provenance** (Codex 4002032955,
P1, `tests/agents/test_public_account_prompts.py:596`). Craft rule 1 bounds
PROVENANCE — who changed a thing, when, under which task — to one trailing line.
The flagged clause is not provenance: it is the semantic defect the gate detects
("two archived live candidate turns … billed and refused on `claims[].type` with
the tag `whereabouts`"), which craft rule 2 requires a new invariant gate to name
and prove with a planted case, and craft rule 5 requires a claim to state
together with the committed evidence it reproduces from. The one path in the
block, `tasks/diagnosis-2026-09-13-live-run-stops.md`, IS that evidence, cited
once. The repository writes exactly this way where a gate exists because of a
recorded failure — `tests/llm/test_real_provider.py:555-557`,
`tests/llm/test_budget.py:281`, `tests/experiments/test_probe_backends.py:87`,
`tests/training/test_goodhart_probe.py:698` — and the card carries the longer
history, as the comment asks, without the test losing the one sentence that says
why the gate is there.

**Planted failures, measured at `2bddbde2`.** Apply the substitution to the named
file, run the command, restore the file from a copy taken before it.
`git status --porcelain` named only this card's own files after each restore.

| Guard | Perturbation | Command | Observed |
| --- | --- | --- | --- |
| The account example must parse | `_account_opening.j2` back to its `bc0a75f6` body (`git show bc0a75f6:…/_account_opening.j2`), whose example carries the placeholder lists | `.venv/bin/python -m pytest "tests/agents/test_public_account_prompts.py::test_every_account_response_example_is_copyable_json" -q` | `AssertionError: opening: the response example is not JSON, so a model that copies it is refused before its fields are read (Expecting value: line 1 column 101 (char 100)): '{"turn_id":"t",…,"observations":[<observation shapes, or empty>],…}'` — `6 failed` |
| The default set's example must parse too | `crewmate_report.j2`: `"observations": []` → `"observations": [<observation shapes, or empty>]` in the output-format line | `.venv/bin/python -m pytest "tests/agents/test_public_account_prompts.py::test_the_default_sets_response_examples_are_copyable_json_too" -q` | the same assertion at `column 112`, on the default crewmate opening — `2 failed, 2 passed` |
| An empty example must be paired with the prose destination | `accusation_round_accounts.j2`: the clause `; fill each structured item into the list its shape is listed under above, and put nothing else in either list` deleted | `.venv/bin/python -m pytest "tests/agents/test_public_account_prompts.py::test_every_account_response_example_is_copyable_json" -q` | `assert ('fill each structured item into the list its shape is listed under above' in 'You are p-1. …') is not False` — `5 failed, 1 passed` (the sixth arm is the attributed-only impostor, which carries the other clause) |

**Verification, round 1.** All commands run at `2bddbde2` with this card's text
on disk.

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/meetings tests/agents -q` | 2,629 passed |
| `bash scripts/check.sh` | exit 0 — "All checks passed!"; 7,602 Python passed, 20 skipped, 3 xfailed; 515 frontend tests over 19 files; strict mypy clean on 476 sources; 4 import contracts kept, 0 broken; 390 phase tasks / 390 prompts in sync; 51 work cards; production build |
| `.venv/bin/python scripts/generate_prompts.py --check` | exit 0 — all 390 prompts in sync |
| `bash scripts/verify_samples.sh` | exit 0 — all 100 canonical recordings verified clean (50 + 50) |
| `.venv/bin/python scripts/build_sample_report.py --sample-dir <set> --check` for `replays/samples/4p1i`, `replays/samples/9p2i`, `replays/ml_corpus/4p1i`, `replays/ml_corpus/9p2i` | all four consistent with their replays, exit 0 |
| `.venv/bin/python -m pytest tests/experiments/test_held_out_prefixes.py -q` | 33 passed |

The Python count rises by ten from the round-0 table: the two new gates carry
six and four parametrisations. No `GENERATOR_SOURCES` file is in this branch's
diff (`git diff --name-only origin/main...HEAD` against the list that module
exports → empty intersection), so the frozen held-out manifest still needs no
restamp, and no `audits/` or `tests/fixtures/` byte moves, so the
`docs/artifacts.md` inventory is unchanged.

**Round-1 limitation.** The JSON gate reads the account arms and the default
set. It deliberately does NOT read the flag-selected impostor roll-call variant:
`accusation_round_roll_call.j2:197` spells a tick as a bare `<int>` inside its
example, so that example does not parse either. That byte predates this card, is
pinned by `accusation_round_roll_call.qwen3_6_27b.v1`, and moving it would open
that variant's own version cascade — out of this card's boundary, and recorded
here as an open item rather than silently covered.

### Review corrections, round 2 (2026-09-14)

One review lens returned two blocking findings over the round-1 head
`74ab19a5`, both about the guard `cd75afaf` added over the default set and the
impostor roll-call variant. Both are valid and both are repaired at
`d0685d02`. No other finding was returned, and no number in the round-0 or
round-1 tables failed to reproduce.

**Repaired: the guard read only the statements, while Results claimed the whole
families.** `test_the_other_live_turn_prompts_file_their_shapes_the_same_way`
rendered `renderers.statement` and nothing else, so `crewmate_report.j2`,
`impostor_report.j2` and `impostor_report_roll_call.j2` — the OPENING of every
arm — never reached `_advertised_shapes`, while the paragraph above said both
families were "now read". Reproduced at `74ab19a5` by pointing the gate's own
reader at the rendered default crewmate opening:

```
git checkout 74ab19a5 -- tests/agents/test_public_account_prompts.py
.venv/bin/python -c 'import sys; sys.path.insert(0, ".")
from tests.agents.test_public_account_prompts import _advertised_shapes, _opening_kwargs
from agents.strategic.prompts import build_prompt_renderers
r = build_prompt_renderers("qwen3_6_27b", env={})
_advertised_shapes(r.crewmate_report(**_opening_kwargs()))'
```

→ `AssertionError: the prompt advertises 'saw_vent' without naming the turn
field it belongs in: 'A witnessed vent is the single strongest fact this game
produces …'` (`crewmate_report.j2:129`; `:131` carries the same for
`saw_kill`). No live prompt defect followed — both inline items validate in
`observations`, which is where that prose names them — so the defect was the
coverage claim, not a byte.

The finding offered two routes: narrow the claim, or extend the guard. **The
guard was extended.** The unread half is the half worth reading — the default
crewmate opening carries the same roll-call instruction the accounts menu
carries, and it is the prompt the two archived turns' arm mirrors — and
narrowing would have left the `cd75afaf` commit body making the same claim,
which a pushed commit cannot be amended to correct. Extending makes both the
sentence and that commit body true.

Reaching the openings cost the reader two destination routes it did not have.
Each is forced by a named line, each is still a gate, and the planted table
below carries a row per route:

- **A sentence may name a shape and its field together.** `crewmate_report.j2`
  introduces two shapes inside its rules block rather than under the
  output-format menu — `… put it on the record as a structured "saw_vent"
  observation copied from that line exactly: {"type": "saw_vent", …}` (`:129`,
  and `:131` for `saw_kill`) — so the destination travels with the sketch
  instead of with a heading above it. `_NAMES_FIELD_INLINE` requires the field
  word to FOLLOW the quoted kind, so prose that merely uses "claim" as a verb
  names nothing: the pre-card `_account_rules.j2` bullet ends "where you claim
  to have been" and still raises with the same message (round-0 row 1, re-run
  below).
- **An indented shapeless line continues the menu it sits in.** Under `Each
  "claims" item is one of:` the accusation entry is prose with no sketch of its
  own (`crewmate_report.j2:157`), and the previous reader treated ANY shapeless
  line as the end of the menu, which would have orphaned the `corroboration`
  sketch beneath it. A flush-left shapeless line still ends the menu.

Both live turn prompts are now read on every arm, and the guard asserts more
than the absence of a misfiling: every crewmate prompt, and every prompt the
roll-call lever renders, must advertise `whereabouts` in `"observations"` — the
structured self-placement that is that lever's whole point and the shape the two
archived turns misfiled. The default impostor set advertises only its
accusation, so it has no observation shape to misfile and is asserted on the
first term only.

**Repaired: the guard now has planted failures of its own.** The round-0 and
round-1 rows perturb `_account_rules.j2`, `_account_opening.j2`,
`accusation_round_accounts.j2` and `crewmate_report.j2`'s example line, none of
which that guard asserts on; the finding reproduced the gap by restoring
`_account_rules.j2` to its pre-card body at `74ab19a5` and running the guard →
`8 passed`, which reproduces here too. Three rows are recorded instead, one per
destination route the reader accepts, each perturbing the default set's crewmate
opening, and each failing ONLY this guard — `4 failed, 77 passed` over the whole
module every time, the four being the crewmate arms of both families (the
impostor arms render a different opening). Apply the substitution, run the
command, restore with `git checkout -- agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2`.

| Guard route | Perturbation of `crewmate_report.j2` | Command | Observed |
| --- | --- | --- | --- |
| A declared list must be the one the schema takes | the `whereabouts` menu line moved from under `Fill "observations" …:` to under `Each "claims" item is one of:` — the live defect, written into the DEFAULT set's menu | `.venv/bin/python -m pytest tests/agents/test_public_account_prompts.py -q` | `ValidationError: Input tag 'whereabouts' found using 'type' does not match any of the expected tags: 'alibi', 'accusation', 'corroboration' [type=union_tag_invalid…]` — `4 failed, 77 passed` |
| A shape must have a destination at all | the declaration line `Fill "observations" with your curated first-hand records, each item one of these shapes:` deleted | the same command | `AssertionError: the prompt advertises 'saw_player' without naming the turn field it belongs in: '  {"type": "saw_player", "tick": <int>, …}'` — `4 failed, 77 passed` |
| An inline sentence's named field is read, not assumed | `structured "saw_vent" observation copied from that line exactly` → `structured "saw_vent" claim copied from that line exactly` | the same command | `ValidationError: Input tag 'saw_vent' found using 'type' does not match any of the expected tags: 'alibi', 'accusation', 'corroboration' [type=union_tag_invalid…]` — `4 failed, 77 passed` |

**The round-0 rows still bite under the widened reader.** A relaxation is only
safe if the defect it was written for still fails, so both round-0 perturbations
were re-applied at `d0685d02` and produced their recorded counts and messages
unchanged:

| Round-0 row | Command | Observed at `d0685d02` |
| --- | --- | --- |
| `_account_rules.j2` back to its pre-card body (`git show c15c587f:…/_account_rules.j2`) | `.venv/bin/python -m pytest "tests/agents/test_public_account_prompts.py::test_every_advertised_shape_is_accepted_in_the_list_the_prompt_names" -q` | `AssertionError: the prompt advertises 'whereabouts' without naming the turn field it belongs in: 'Use only the few relevant structured accounts. The same public shapes are available to every player:- {"type":"whereabouts",…}'` — `5 failed, 1 passed` |
| the `whereabouts` bullet moved under the `"claims"` heading | the same selection plus `::test_the_shape_the_live_run_filed_in_claims_is_refused_exactly_as_recorded` | `union_tag_invalid` on the accept path and `AssertionError: assert {'claims'} == {'observations'}` — `6 failed, 1 passed` |

**Verification, round 2.** All commands run at `d0685d02` with this card's text
on disk. No template byte moved this round, so `ACCOUNT_PROMPT_SET_REVISION`
stays `v3`, the generated prompt exports are untouched, no `GENERATOR_SOURCES`
file is in this branch's diff, the frozen held-out manifest needs no restamp,
and no `audits/` or `tests/fixtures/` byte moves, so the `docs/artifacts.md`
inventory is unchanged.

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/meetings tests/agents -q` | 2,629 passed |
| `bash scripts/check.sh` | exit 0 — "All checks passed!"; 7,602 Python passed, 20 skipped, 3 xfailed; 515 frontend tests over 19 files; strict mypy clean on 476 sources; 4 import contracts kept, 0 broken; 390 phase tasks / 390 prompts in sync; 51 work cards; production build |
| `.venv/bin/python scripts/generate_prompts.py --check` | exit 0 — all 390 prompts in sync |
| `bash scripts/verify_samples.sh` | exit 0 — all 100 canonical recordings verified clean (50 + 50) |
| `.venv/bin/python scripts/build_sample_report.py --sample-dir <set> --check` for `replays/samples/4p1i`, `replays/samples/9p2i`, `replays/ml_corpus/4p1i`, `replays/ml_corpus/9p2i` | all four consistent with their replays, exit 0 |
| `.venv/bin/python -m pytest tests/experiments/test_held_out_prefixes.py -q` | 33 passed |

The Python count does not move from the round-1 table: the guard's
parametrisation is unchanged, it now reads two prompts per case instead of one.

**Round-2 limitation.** The inline route reads a SENTENCE, not a paragraph: a
template that named a shape's field in a different sentence from the sketch
would still raise, and so would one that named it only in a heading above a
flush-left prose line. No current template does either, and the conservative
direction is the safe one — the reader raises rather than guessing a
destination. The gate's coverage is still the set of shapes written as a
`{"type":…}` sketch, as the round-0 limitations say.
