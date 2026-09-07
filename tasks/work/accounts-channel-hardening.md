# Harden the public accounts channel against forged placement and leaked truth

**Status:** ready

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

- [ ] Reproduce each finding before repairing it: a forged section heading
  reaching a listener's prompt, a single-speaker minted `alibi_conflict` naming
  an innocent, a sighting claim that places nobody, an impostor's `saw_kill`
  reaching a teammate, and the reply prompt's unsatisfiable instruction.
- [ ] `free_text` is quoted or delimited so no speaker-authored bytes can open a
  section the prompt's own structure owns. An adverse test plants a speaker whose
  free text is a full forged comparison section.
- [ ] A conflict requires two distinct speakers, or is labelled as
  self-contradiction of the single speaker. The `subjects` tuple names the
  speaker whose claims produced it, not only the accused third party.
- [ ] The speaker of a sighting claim is placed by their own claim, and
  `co_present` participates in the comparison. An adverse test shows the cheapest
  lie now places its speaker.
- [ ] The teammate firewall covers every observation kind the accounts menu can
  elicit, `saw_kill` included; an adverse test plants an impostor whose menu
  answer names its teammate.
- [ ] The attributed reply prompt asks only for what the schema expresses, or the
  schema gains the placement it demands. The two are checked against each other
  by a test, not by reading.
- [ ] One sentence in each of `audits/deduction-candidate/checkpoint.md` and
  `audits/investigation-candidate/checkpoint.md` states the vent-certificate
  trade-off: attributed mode replaces the grounded vent detector by design, as
  disclosed at `audits/deduction-candidate/gameplay-review.md:68,153-157`.
- [ ] Every new guard has a planted failure proving it detects the claimed defect.

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
`docs/artifacts.md` audits row that follows from it.

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
