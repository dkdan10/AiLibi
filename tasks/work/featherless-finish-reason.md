# Record the provider's finish_reason so a truncation is observed, not inferred

**Status:** done

## Outcome

Every call the fresh-deduction instrument makes records the reason the
provider gave for stopping generation. The per-call cap check reads that
string beside the `output_tokens >= max_tokens` inference it uses today, stops
on either, and COUNTS a call on which the two disagree rather than silently
preferring one of them. A call whose provider supplied no such string records
null. The fourth run stopped on a truncation nobody observed; a fifth run that
stops the same way names the provider's own word for it, and a calibration
that sees one can report it.

## Evidence

[The diagnosis of 2026-09-15](../diagnosis-2026-09-15-truncation-stop.md) is
this card's source. It stopped the fourth run at unit 26 of 100 on a ballot
that reached its 1,024-token output cap, and its section-5 fix D is this work.
The owner approved that memo's section-6 decisions as a set on 2026-09-15;
decision 3 reads "Yes, independent of 1", at a cost of "one client change plus
tests".

**The string is absent from the tree.** `grep -rn finish_reason` over the
repository returns exactly one line, and it is a note rather than an
implementation: `audits/review-2026-08-19/B/llm-and-prompts.md:75` recorded in
August that a 2xx response whose `finish_reason` is `"length"` "is not
detected", and accepted it. Nothing under `llm/` has carried the field since.
`_raw_from_response_body` (`llm/featherless_client.py:804-861`) reads
`choices[0]`'s `message` (:833) and the body's `usage` (:841) and drops
everything else on the choice, including the field the server sends beside it.

**What infers it today** is `_InstrumentClient._unusable_response`
(`experiments/fresh_deduction_instrument.py:2394-2418`), whose second branch
(:2412) returns `PerCallCapExceeded` when `output_tokens >= max_tokens`. Two
call sites reach it and the fourth run's stop came through the FIRST, not the
obvious one: a body cut off mid-string fails `model_validate_json`, the
adapter attaches an `LLMCallFailure` to the propagating `ValidationError`
(`llm/featherless_client.py:388-400`), and the instrument judges that refused
attempt off the metadata's `output_tokens` (:2276-2280) rather than off a
response. The resolved path (:2299-2303) judges a response that came back. A
change that reaches only the response reaches everything except the call that
actually stopped the run.

**The shapes are small and every one of them defaults.** `LLMResponse`
(`llm/client.py:115-129`) and `LLMCallFailure` (`llm/provider.py:102-124`) are
both `frozen=True, extra="forbid"`, and `LLMCallRecord.agent_id`
(`orchestrator/replay.py:203`) is this repository's own precedent for adding
one optional field to such a model so that records written before it still
deserialize. The instrument's per-call row, `CapturedCall` (:1632-1650),
carries the same convention on `disposition` (:1648-1650).

**The digest consequence is two sentences, not one.**
`llm/featherless_client.py` is not in `ARM_SURFACE_SOURCES` (:4296-4304), so
the client change moves no arm-surface digest; the instrument IS in that
tuple, so its recording change moves the digest as every edit to it does.

## Acceptance

- [x] The client reads the field and never invents it.
  `_raw_from_response_body` (`llm/featherless_client.py:804-861`) takes
  `choices[0].get("finish_reason")` onto `FeatherlessRawResponse`
  (:185-205) as `str | None`, coerced to `None` when the key is absent or not
  a string, with no default of `"stop"` anywhere in the client. Planted: the
  fixture body of `TestResponseBodyMapping._body`
  (`tests/llm/test_featherless_client.py:490-497`) with the key absent reads
  `None`, with `"length"` reads `"length"`, and with a non-string reads `None`
  rather than the raw value.
- [x] Both provider-neutral carriers take it. `LLMResponse`
  (`llm/client.py:115-129`) and `LLMCallFailure` (`llm/provider.py:102-124`)
  each gain `finish_reason: str | None = None`, and the Featherless adapter
  sets both: the response at `llm/featherless_client.py:402-410` and the
  parse-failure carrier at :390-399. The refused attempt that stopped the
  fourth run therefore carries the reading, as a resolved one does. The
  Anthropic adapter (`llm/provider.py:221-230,233-241`) and
  `llm/ollama_client.py:255` are NOT edited and therefore record null.
  Mapping Anthropic's `stop_reason` or Ollama's `done_reason` is out of
  scope, and a planted test asserts those two adapters still read null
  rather than a guess.
- [x] The offline doubles supply a value so every non-live path exercises the
  field. `llm/fake_provider.py:67-75` returns `"stop"`, and the replay double
  (`tests/experiments/usage_replay_double.py:331-338`) returns the archived
  row's reading when its profile carries one and `"stop"` otherwise;
  `charged_parse_failure` (`tests/experiments/burned_call_double.py:50-87`)
  carries the same onto the refusal it raises. A double's `"stop"` is
  synthetic and is not an archive's silence: the card says so here, the
  docstrings say so there, and the ARCHIVE path still records null.
- [x] The instrument records it per call. `CapturedCall` (:1632-1650) gains
  `finish_reason: str | None = None`, `_record` (:2308-2348) takes it, and
  both recording sites pass what they hold: the refused site (:2249-2259)
  from the parse-failure metadata, the resolved site (:2288-2297) from the
  response. The two sites that record no completion record null, by this
  table, and a test asserts each:

  | disposition | what the row reads it off | recorded |
  | --- | --- | --- |
  | `resolved` | the response | the string, or null |
  | `billed_and_refused` | the parse-failure metadata | the string, or null |
  | `unaccounted` | nothing came back | null |
  | `aborted` | the work window cut the attempt off | null |

- [x] The cap check reads both signals and prefers neither.
  `_unusable_response` (:2394-2418) takes the observed reading beside
  `output_tokens` and `max_tokens` and decides by this table, which is the
  whole of the new rule:

  | observed | inferred (`out >= cap`) | verdict | counted |
  | --- | --- | --- | --- |
  | `"length"` | yes | stop | agreement |
  | `"length"` | no | stop | disagreement |
  | any other string | yes | stop | disagreement |
  | any other string | no | pass | not counted |
  | null | yes | stop | not counted |
  | null | no | pass | not counted |

  A null observation is not a disagreement: an absent reading contradicts
  nothing. The stop message names which signal or signals fired.
- [x] Both planted proofs the diagnosis asks for exist and are red without the
  change: a body reporting `"length"` at 900 output tokens against the 1,024
  vote cap raises `PerCallCapExceeded` and counts a disagreement; a body
  reporting `"stop"` at exactly 1,024 raises it on the inference, unchanged,
  and counts one too. A third case pins the agreement row, so the counter
  cannot be wired to fire on every stop.
- [x] The count is reported, not just held. `ArmSummary` (:4035-4080) gains
  the per-arm disagreement count beside `retried_calls` and
  `unaccounted_attempts`, which are the existing precedent for a counted
  anomaly on that model; the calibration report's per-call row
  `CalibrationCall` (:5503-5519) gains `finish_reason: str | None = None`; and
  `usage_profile_from_calibration` (:6053-6118) carries it onto the rows the
  replay double draws. `UsageRow`
  (`tests/experiments/usage_replay_double.py:71-86`) reads it with
  `entry.get`, the way `refused` is read at :188. The spend reconciliation
  (`_reconcile_recorded_spend`, :3483-3521) gains no term: it is token
  arithmetic against the budget snapshot, and the reading rides the ledger row
  it reconciles rather than changing what has to balance.
- [x] Records written before this card still parse, and read null. A test
  loads the committed
  `audits/deduction-candidate/calibration-2026-09-14/calibration.json` and
  `tests/experiments/deduction_usage_profile.json` through the current models
  and asserts every call reads null rather than `"stop"`. `CALIBRATION_SCHEMA`
  (:5381) stays `fresh-deduction-calibration/1` and the usage profile stays
  `fresh-deduction-usage-profile/1`: an added optional field defaulting to
  null changes how no existing record reads, and that test proves it.
- [x] The execution manifest gains one dated paragraph under
  `### How each limit is enforced`
  (`audits/deduction-candidate/execution-manifest.md:857`), attached to the
  `Per-call cap` bullet at :888, recording that from this date the truncation
  reading is taken from the provider's own `finish_reason` as well as from the
  output counters, that either one stops the run, and that a disagreement is
  counted and reported per arm. The authorized table at :798, `STOP_RULE`
  (:619-650), `AUTHORIZED_SAMPLING` and every limit constant are
  byte-identical afterwards, and the test that pins the manifest to the
  constants passes unchanged.
- [x] `docs/artifacts.md`'s `audits/` inventory row is recomputed with the
  manifest change staged, `scripts/verify_ml_evidence.py` passes offline, and
  every new gate above has a planted failure recorded in Results with the
  message it produced.

## Constraints

No live provider call, on any path, for any reason. No band is drawn,
rendered, printed or tallied; the held-out band 7000-7999 is the live one and
this card has no business with it.

`STOP_RULE`'s text does not change, and neither do the limits, the sampling
configuration or the manifest's authorized table. The two per-call caps this
card's tests quote are the fourth authorization's: the turn cap of 4,096 and
the vote cap of 1,024 (`experiments/fresh_deduction_instrument.py:201-202`),
carried by the owner's merge of PR #457 (`10a19df8`) along with 106,000 /
16,000 per unit, 3,710,000 / 459,000 per run, 6 h of model work inside an 8 h
wall and four transport attempts at 180 s. This card quotes them and moves
none of them.

**The stop condition is unchanged in words and widened in evidence, and that
is a declared cost.** `STOP_RULE` already stops on "a per-call response that
reached its output cap", and a `finish_reason` of `"length"` is the provider
saying that happened. The union can only trip a stop EARLIER than the
inference alone, never later, and can never turn a stop into a datum. It
cannot be checked against the fourth run, because the field was never
recorded there. That is the reason for this card, not a claim that the risk
is zero.

`orchestrator/game.py` and `orchestrator/replay.py` are NOT edited, so the
per-unit replay JSONL rows (`LLMCallRecord`, `orchestrator/replay.py:174-203`,
written at `orchestrator/game.py:1083-1092`) do not carry the reading:
`orchestrator/game.py` is arm surface (:4296-4304) and decision 3 is costed as
digest-neutral outside the instrument. The cost is real: an archived unit's
JSONL still will not say why a call stopped, so a recount reads it from the
report and the calibration record. Extending that row is a separate card.

A missing reading is recorded as null and never inferred, guessed or
back-filled; the doubles' `"stop"` is a double's, stated as such. Any
`audits/` byte change recomputes the `docs/artifacts.md` audits row. The run's
primary outcome, decision rule, minimum actionable effect, tradeoff bound and
`STOP_RULE` do not change on this card.

Independent of [the accounts v4 card](accounts-prompt-set-v4.md): the two
share no file and neither waits on the other. It FEEDS
[the second calibration](fresh-deduction-calibration-2.md), whose brief is to
count truncations, so landing first is worth more than landing in parallel.

## Expected scope

`llm/featherless_client.py`, `llm/client.py`, `llm/provider.py`,
`llm/fake_provider.py`, `experiments/fresh_deduction_instrument.py`,
`tests/llm/test_featherless_client.py`,
`tests/experiments/test_fresh_deduction_instrument.py`,
`tests/experiments/usage_replay_double.py`,
`tests/experiments/burned_call_double.py`,
`audits/deduction-candidate/execution-manifest.md` (one dated paragraph),
`docs/artifacts.md` (the `audits/` row), `tasks/README.md`'s derived inventory
sentence, this card. No committed recording, report, calibration record or
usage profile is rewritten.

Delivered on `work/featherless-finish-reason` and one pull request into
`main`, merged as a merge commit or a fast-forward and never squashed, with
the trailer `Card: tasks/work/featherless-finish-reason.md` on every commit.
It is stacked on nothing and needs no retarget, every acceptance item that
adds a gate carries a planted failure, and no candidate prompt byte is
touched, so no experiment lever, recording or re-record is in scope.

## Record impact

Amends one `audits/` document (the execution manifest) with a dated paragraph;
no recording, report, DTO, metric or weight byte moves, no experiment becomes
ON, no adopting record is created, and no committed measurement record is
regenerated.

The client change is digest-neutral: `llm/featherless_client.py`,
`llm/client.py` and `llm/provider.py` are outside `ARM_SURFACE_SOURCES`
(:4296-4304) and outside the prompt directory it hashes. The instrument change
is not, so the arm-surface digest moves, `assert_checkpoint_matches` (:4755,
the comparison at :4791-4802) refuses a resume across the change, and units
recorded before it cannot be pooled with units after. The move is symmetric,
since the instrument is not an arm, and the fourth run's 24 complete units are
already unpoolable, so this costs the queue nothing it has not spent.

`InstrumentReport` and `CalibrationCall` are `extra="forbid"`, so the new
fields are additive and visible; the report still carries counts only and
`assert_report_holds_no_prefix_bytes` is unchanged.

## Validation

`uv run pytest tests/llm -q` and `uv run pytest tests/experiments -q` (fake and
replay doubles only), then `uv run python scripts/validate_task_docs.py`,
`uv run python scripts/check_doc_facts.py`, `uv run python
scripts/verify_ml_evidence.py` (offline; never `--complete`), `uv run pytest
tests/scripts/test_verify_ml_evidence.py -q`, and `bash scripts/check.sh`.
Neither the live evaluation nor a live calibration is a check or is run here.

## Results

Every acceptance item is met and the card is `done`. The stop condition's WORDS
are unchanged — `STOP_RULE` (`experiments/fresh_deduction_instrument.py:619-650`)
already stops on "a per-call response that reached its output cap" — and its
EVIDENCE is widened: the provider's own `finish_reason` is now recorded beside
the `output_tokens >= max_tokens` inference, either signal stops the run, and a
call on which the two contradict is counted per arm. No limit, no sampling
value, no authorized-table row and no byte of `STOP_RULE` or
`AUTHORIZED_SAMPLING` moved; no run, calibration or re-record is authorized by
this work, and no live provider call was made on any path.

Architecture: `docs/architecture.md`'s LLM-adapter layer — the provider-neutral
`llm/client.py` surface every adapter implements — and AGENTS.md load-bearing
rule 5, invalid input raises and no silent fallbacks, are what shape the
design: a reading the adapter did not receive is recorded as `None` rather than
defaulted, on every path.

**What moved, in one line each.** `FeatherlessRawResponse`, `LLMResponse` and
`LLMCallFailure` each gain `finish_reason: str | None = None`; the Featherless
adapter reads `choices[0]["finish_reason"]` in `_raw_from_response_body` and
sets both carriers; `FakeProvider` reports `FAKE_FINISH_REASON` (`"stop"`, a
double's word, named so no reader mistakes it for a measurement) and
`DryRunProvider` carries the same; `CapturedCall`, `CalibrationCall`, the usage
profile's call rows and `ArmSummary.cap_signal_disagreements` record it or the
count derived from it. `llm/ollama_client.py` and the Anthropic adapter in
`llm/provider.py` are NOT edited and therefore read null, which a test pins.

**Decision — where the count lives, and why it is derived.** The per-arm count
rides `ArmUsage` (and `CarriedUsage`, so a resumed sitting carries it) and is
DERIVED from the ledger rows by `_cap_signals_disagree`, not accumulated as a
second counter inside `_unusable_response`. One definition then serves the stop
and the report, and the count is a property of what was recorded: a row whose
two signals disagreed counts even if some other stop — an identity mismatch —
fired first, which is the honest reading, because the disagreement happened.
`ArmUsage` is a spend tally and this is not spend; it rides there because that
is the one tally that walks the captured rows, and its docstring says so.

**Decision — the stop message names which signal fired, and the inference's own
wording is byte-identical.** A call stopped by the counters alone with no
reading still raises exactly `a response reached its 1024-token output cap
(1024 tokens); a truncation is a stop, not a datum`, pinned by
`test_a_silent_provider_is_stopped_by_the_inference_alone`. An observed-only
stop names `finish_reason 'length'` and the tokens it was seen at; a
disagreement appends the contradiction in the same message.

**Decision — the doubles say `"stop"`, and say that they are saying it.** The
fake provider, the dry-run provider, `charged_parse_failure` and the replay
double all report `"stop"` where they have no archived reading, so every
offline path exercises the field. `usage_replay_double.REPLAYED_FINISH_REASON`
and `llm.fake_provider.FAKE_FINISH_REASON` name it, their docstrings say it is
a double's word and not an archive's, and `UsageRow.finish_reason` keeps the
ARCHIVE's own silence visible as `None`.

**Record impact, as declared.** One `audits/` document is amended — the
execution manifest, one dated paragraph attached to the `Per-call cap` bullet —
and `docs/artifacts.md`'s `audits/` row moves from `15,096,108 tracked bytes /
211 files` to `15,097,461 tracked bytes / 211 files`: 211 files unchanged,
+1,353 bytes, the paragraph. No recording, report, calibration record or usage
profile is regenerated. The arm-surface digest moves, because the instrument is
in `ARM_SURFACE_SOURCES`: `assert_checkpoint_matches` refuses a resume across
the change and the fourth run's units are not poolable with later ones, which
the card costs as already spent. `llm/featherless_client.py`, `llm/client.py`
and `llm/provider.py` are outside that tuple and outside the prompt directory,
so the client half is digest-neutral. `CALIBRATION_SCHEMA` stays
`fresh-deduction-calibration/1` and the usage profile stays
`fresh-deduction-usage-profile/1`.

**Two deviations from Expected scope, both directly necessary and both
declared.** First, `DryRunProvider.complete` — inside the instrument, already
in scope — sets `finish_reason=FAKE_FINISH_REASON`, so the dry run exercises
the recorded field instead of leaving it null on every offline path. Second,
the profile row's permitted-key enumeration in
`TestCalibrationProfileRefresh::test_the_refresh_writes_a_profile_the_double_reads`
gains `"finish_reason"`: it is a leak guard over a row that carries counts
only, and the provider's one-word stop reason carries no prompt, prefix or
payload bytes. Nothing else outside the card's file list is touched.

### Verification

Run on `work/featherless-finish-reason`, in a worktree of this branch, with the
repository's own `.venv`.

| command | result |
| --- | --- |
| `.venv/bin/python -m pytest tests/llm -q` | `328 passed, 17 skipped` |
| `.venv/bin/python -m pytest tests/experiments -q` | `412 passed` |
| `.venv/bin/python scripts/validate_task_docs.py` | passed |
| `.venv/bin/python scripts/check_doc_facts.py` | passed |
| `.venv/bin/python scripts/verify_ml_evidence.py` | `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5`, `verify-ml-evidence: every check passed.` |
| `.venv/bin/python -m pytest tests/scripts/test_verify_ml_evidence.py -q` | passed |
| `bash scripts/check.sh` | passed, exit 0 |

The seven `ABSENT` rows are the evidence-branch bytes a fresh clone does not
carry. `--complete` was not run, and neither a live evaluation nor a live
calibration is a check here or was run.

### The planted failures, each edited, run and restored

Every one was applied to this tree, run, and reverted; the tests named are the
new ones in `tests/llm/test_featherless_client.py` and
`tests/experiments/test_fresh_deduction_instrument.py`.

1. **The client invents a reading.** `_raw_from_response_body`'s coercion
   changed to `else "stop"`. Red: `test_absent_finish_reason_maps_to_none`, the
   four `test_a_non_string_finish_reason_maps_to_none` cases and
   `test_the_client_never_defaults_the_reading_to_stop` — `6 failed, 1 passed`,
   the last with `assert 'stop' not in [...]` naming the literal.
2. **The observed signal is dropped**, i.e. the rule as it stood before this
   card: `observed = False` forced in `_unusable_response`. Red:
   `test_the_decision_table_is_the_whole_rule[length-900-True-1]`,
   `test_the_two_planted_disagreements_are_red_without_the_reading`,
   `test_the_agreement_row_stops_without_counting_a_disagreement` and
   `test_a_refused_completion_carries_the_reading_the_fourth_run_lost` —
   `4 failed, 12 passed`. This is the `"length"`-at-900-tokens case the counters
   cannot see.
3. **The counter fires on every truncation stop.** `_cap_signals_disagree`
   returning `observed or inferred`. Red:
   `test_the_decision_table_is_the_whole_rule[length-1024-True-0]` and
   `test_the_agreement_row_stops_without_counting_a_disagreement` —
   `2 failed, 14 passed`. This is the agreement row, which is what keeps the
   count from being a second name for the stop.
4. **A null observation counted as a disagreement.** The
   `if call.finish_reason is None: return False` guard removed. Red:
   `test_the_decision_table_is_the_whole_rule[None-1024-True-0]` —
   `1 failed, 15 passed`, `assert 1 == 0`.
5. **The refused path loses the reading.** `finish_reason` dropped from the
   instrument's `billed_and_refused` record and from its `_unusable_response`
   call. Red: `test_a_refused_completion_carries_the_reading_the_fourth_run_lost`
   — `1 failed, 15 passed`. This is the path the fourth run actually stopped
   through.
6. **The boundary defaults instead of recording null.**
   `CalibrationCall.finish_reason` defaulted to `"stop"`. Red:
   `test_the_committed_calibration_and_profile_parse_and_read_null` —
   `1 failed, 15 passed`, `Extra items in the right set: None`.
7. **The adapter's refusal carrier loses it, and an unedited adapter guesses.**
   `finish_reason=raw.finish_reason` removed from the Featherless
   `LLMCallFailure`, and `finish_reason="stop"` added to `llm/ollama_client.py`.
   Red: `test_the_parse_failure_carrier_takes_the_reading` and
   `test_the_anthropic_and_ollama_adapters_still_read_null` —
   `2 failed, 3 passed`. Both edits reverted; `llm/ollama_client.py` carries no
   change in this branch's diff.

### Limitations

- **The widening cannot be checked against the fourth run.** The field was
  never recorded there, so there is no way to know how often its two signals
  would have disagreed. That is the reason for the card, not a claim that the
  risk is zero. The union can only trip a stop EARLIER than the inference
  alone, never later, and can never turn a stop into a datum.
- **A per-unit replay row still will not say why a call stopped.**
  `orchestrator/game.py` and `orchestrator/replay.py` are arm surface and are
  not edited, so `LLMCallRecord` does not carry the reading; a recount reads it
  from the report and the calibration record. Extending that row is a separate
  card.
- **Only the Featherless adapter maps a reading.** Anthropic's `stop_reason`
  and Ollama's `done_reason` are out of scope by the card, and those two
  adapters record null — pinned, so a later guess is red rather than silent.
- **The two readings are checked against each other, not against ground
  truth.** A provider that reports `"length"` wrongly, or omits it on a
  truncation, is invisible to both; what the count says is that the two
  readings differed, which is the most an offline instrument can say.
- **The disagreement count is at most one per stopped run in practice**, since
  a disagreement is also a stop. It is reported per arm because a calibration —
  which the second calibration card is briefed to run — can see several.
