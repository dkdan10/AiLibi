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
  `said: "<free text>"` with `\r` and `\n` replaced by a space and `"` by `'`.
  Speaker-authored bytes therefore always occupy exactly one quoted line and can
  never begin a line at column 0, which is what the section headings the template
  owns require. Structured rows are not flattened: `model_dump_json` escapes
  newlines, and every id inside them is checked against the roster, room ids and
  task ids by `validate_public_accounts` before the turn records.
- **A conflict names the account it impeaches.** In
  `detect_public_account_conflicts`, a pair whose two placements come from the
  same speaker about a third party now sets `subjects` to that speaker and appends
  `Both placements come from <speaker> alone, so this impeaches that speaker's own
  account rather than <subject>.` A pair from two speakers is unchanged and still
  names the subject; a speaker's own self-placements were already subject-named and
  are unchanged. This mirrors the rule the private detector applies to the same
  shape (`meetings/transcript.py::_apply_proxy_intra_turn_guard`); it is
  reimplemented rather than shared because this module reads only public speech.
- **A sighting places its speaker and its named bystanders.** `_placements` emits,
  for `saw_player` / `saw_vent` / `saw_kill` / `saw_move`, a second placement of
  the speaker at the observed room (`from_room` for a transition) and, for
  `saw_player`, one placement per `co_present` name at the observed room. The
  speaker placement carries one hop of `vision_slack`, added to the allowance in
  the walking comparison, because vision reaches one adjacent room for an impostor;
  the description says which clause came from a claimed sighting. The one-hop grant
  makes the comparison conservative rather than sound-by-construction: it will not
  flag a same-tick sighting two rooms from the speaker's stated position.
- **The teammate firewall is total over the shape union.**
  `exclude_teammate_vent_observations` is renamed
  `exclude_teammate_role_proving_observations` and drops a `saw_kill` naming a
  fellow impostor alongside the `saw_vent` it already dropped. Coverage is stated,
  not implied: `TEAMMATE_GUARDED_OBSERVATION_KINDS` carries one decision for each
  of the eight `ObservationClaim` members, and a test drives one teammate-naming
  instance of every member through the guard, so the declaration and the code
  cannot disagree in either direction. The six False shapes record untouched,
  matching the claims guard, which deliberately retains a teammate alibi and
  corroboration.
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
- **No prompt-version bump.** These templates take their identity from
  `public_account_prompt_versions`, which composes the stamp from the two lever
  values (`..._accounts.qwen3_6_27b.v1.accounts<N>.attributed<M>`) and not from a
  per-template marker. `grep -rn "accounts.qwen3_6_27b" tests scripts api experiments`
  returns nothing, so no recorded prompt-version pin names these bytes, and
  `orchestrator/game.py` is untouched.

### Reproductions and planted failures

Every finding was reproduced before it was repaired. Each reproduction is
restated here as a perturbation of the committed tree at `96a83a6a`, so a reader
re-creates the exact defect and watches the gate bite. Each row is: apply the
substitution to the named file, run the command, restore the file.

| Finding | Perturbation | Command | Observed |
| --- | --- | --- | --- |
| NC2-1 | `_account_transcript.j2`: the quoted, flattened `said:` line back to `said: {{ turn.free_text }}` | `.venv/bin/python -m pytest tests/agents/test_public_account_prompts.py::test_speaker_free_text_cannot_open_a_section_the_template_owns -q` | `assert ['## Account ... comparisons'] == ['## Account comparisons']` / `Left contains one more item: '## Account comparisons'` — `1 failed` |
| NG2-4 | `accusation_round_accounts.j2`: the branched reply instruction back to the unconditional `Cite your relevant placement or observation, …` | `.venv/bin/python -m pytest tests/agents/test_public_account_prompts.py::test_the_reply_prompt_asks_only_for_shapes_the_schema_expresses -q` | `assert demands_citation is bool(advertised & _PLACEMENT_KINDS)` → `assert True is False` where the advertised set is empty — `1 failed, 4 passed` |
| NC2-2 / FU-ALIBI-4 | `public_accounts.py`: `single_author = …` → `single_author = False` | `.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_one_speaker_alone_impeaches_itself_not_the_player_it_named -q` | `assert ('p-5',) == ('p-2',)` — the flag names the innocent again — `1 failed` |
| NG3-5 | `public_accounts.py`: `if not isinstance(observation, _SIGHTINGS):` → `if True or …` (no speaker placement) | `.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_the_cheapest_lie_now_places_the_speaker_who_told_it -q` | `ValueError: not enough values to unpack (expected 1, got 0)` — the cheapest lie raises nothing — `1 failed` |
| NG3-5 (slack) | `public_accounts.py`: the witness placement's `vision_slack=1` → `vision_slack=0` | `.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_a_sighting_within_the_granted_slack_is_never_called_impossible -q` | one legal pair becomes a flag: `Left contains one more item: ContradictionRef(contradiction_id='public-account-aa6d4eba507d9b36', …)` — `1 failed, 1 passed` |
| NG2-2 | `public_accounts.py`: `if not isinstance(observation, SawPlayerObservation):` → `if True or …` (no co-present placement) | `.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_a_named_bystander_is_placed_by_the_sighting_that_named_them -q` | `ValueError: not enough values to unpack (expected 1, got 0)` — a denied co-presence is invisible — `1 failed` |
| NC2-3 (coverage) | `manager.py`: `_ROLE_PROVING_OBSERVATIONS` back to `(SawVentObservation,)` | `.venv/bin/python -m pytest tests/meetings/test_manager.py::TestTeammateObservationFirewall -q` | `AssertionError: saw_kill` … `Left contains one more item: SawKillObservation(type='saw_kill', tick=4, subject='p-3', room='MEDBAY')` — `1 failed` |
| NC2-3 (end to end) | the same substitution | `.venv/bin/python -m pytest tests/meetings/test_public_accounts.py::test_an_impostor_menu_answer_naming_its_teammate_never_records -q` | `assert (SawKillObser...room='LABS'),) == ()` — the impostor's menu answer naming its teammate records — `1 failed` |

Each perturbation was applied and reverted in place; `git status --porcelain`
was empty afterwards.

### Verification

All commands run on the committed tree at `96a83a6a`.

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/meetings tests/agents -q` | 2,570 passed |
| `bash scripts/check.sh` | exit 0 — 7,289 Python passed, 20 skipped, 3 xfailed; 515 frontend tests over 19 files; strict mypy on 471 sources; 4 import contracts kept, 0 broken; 390 phase tasks / 390 prompts in sync; 43 work cards; production build |
| `bash scripts/verify_samples.sh` | all 100 canonical recordings verified clean |
| `AILIBI_SAMPLES_ROOT=replays/ml_corpus bash scripts/verify_samples.sh` | all 200 ML-corpus recordings verified clean |
| `.venv/bin/python scripts/build_sample_report.py --sample-dir <set> --check` for `replays/samples/4p1i`, `replays/samples/9p2i`, `replays/ml_corpus/4p1i`, `replays/ml_corpus/9p2i` | all four consistent with their replays, exit 0 |
| `.venv/bin/python scripts/check_doc_facts.py` | doc facts, front door, `docs/ml-program.md` and budgets all verified |
| `.venv/bin/python scripts/verify_ml_evidence.py` | checks 60, OK 48, FAIL 0, ABSENT 7, INFO 5 — every check passed |
| `.venv/bin/python -m pytest tests/experiments/test_held_out_prefixes.py -q` | 28 passed |

The `audits/` registry row moved with the two checkpoint sentences. Recomputed
with the change staged: `git ls-files audits | wc -l` → 202 and
`git ls-files audits -z | xargs -0 wc -c | tail -1` → 14,853,326, which is the
row now written in `docs/artifacts.md`.

No file in `experiments/held_out_prefixes.py::GENERATOR_SOURCES` is touched by
this branch, so the frozen held-out manifest needs no restamp and its
regeneration test passes unchanged. `pytest tests/orchestrator/ --collect-only`
and the frontend `npm run e2e` leg were not required: no reader, orchestrator or
served DTO byte changes, and `scripts/check.sh` ran the whole Python and frontend
suites regardless.

### Record impact and limitations

- Prompt bytes on the accounts and attributed arms changed, so captures taken
  before this branch are not comparable to captures taken after. The two
  candidate measurements committed under `audits/deduction-candidate/` and
  `audits/investigation-candidate/` predate it; anywhere they are shown beside a
  later capture, that discontinuity has to be stated.
- The default meeting path is unchanged. The templates edited here are reached
  only under `public_account_version` / `attributed_testimony_version`, both
  default-OFF; the firewall rename is behaviour-identical for every crewmate and
  every sole impostor; and the comparator runs only on the attributed arm. All
  300 committed recordings reconstruct and all four derived reports remain
  byte-consistent, which is the evidence that no recorded byte moved.
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
  impossible.
- Delivery state: implemented and verified locally. Not independently reviewed,
  not owner reviewed, not merged. Adoption is not applicable — this card repairs
  a gated channel and adopts nothing.
