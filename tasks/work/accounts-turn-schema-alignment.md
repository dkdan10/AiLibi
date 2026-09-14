# Make the accounts prompt and the turn schema agree on whereabouts

**Status:** ready

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

- [ ] Reproduce the refusal offline: a turn payload of the shape the accounts
  prompt instructs (a `whereabouts` item under `claims`) fails `MeetingTurn`
  validation with the archived `union_tag_invalid` reason; recorded with the
  command.
- [ ] The prompt and the schema agree, by one of two routes chosen and
  justified in Results: the accounts templates place `whereabouts` where the
  schema accepts it and say so unambiguously, or the schema admits the shape
  where the prompt asks for it; a test extracts every shape the accounts
  templates advertise and asserts each is accepted by the schema at the place
  the template names it (extending the prompt/schema agreement test the
  hardening card added).
- [ ] The prompt-set revision follows the version-bump cascade (the `.j2`
  marker, `DEFAULT_PROMPT_VERSIONS` in `orchestrator/game.py`, the recorded
  prompt-version pin); if that cascade touches `orchestrator/game.py`, the
  held-out restamp rule applies and is recorded. The default meeting path's
  prompt bytes are unchanged (`generate_prompts --check`, the default-path
  golden, `verify_samples.sh` and the four `--check` runs).
- [ ] Measured offline on the replay double from
  [the realism card](fresh-deduction-instrument-realism.md) (or, if that card
  has not landed, on the fake provider with a planted payload of the archived
  refusal's shape): the candidate arm's refusal rate on the previously refused
  shape is zero, and Results states that the live output-length effect can only
  be measured by the owner's calibration decision.
- [ ] Every new guard has a planted failure proving it detects the claimed
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
