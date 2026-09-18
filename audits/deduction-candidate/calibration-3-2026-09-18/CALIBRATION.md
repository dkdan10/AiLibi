# Third development calibration of the fresh-model deduction instrument, 2026-09-18

A bounded live measurement of the revised wave of 2026-09-18, on development
inputs, run once by a runner session on
[the third calibration card](../../../tasks/work/fresh-deduction-calibration-3.md)
(its last acceptance item) under the owner's decision 1 of
[the diagnosis of 2026-09-18](../../../tasks/diagnosis-2026-09-18-fifth-run.md),
recorded in [the execution manifest](../execution-manifest.md)'s "Development
calibration 3 (2026-09-18)" section.

**This measured nothing about the candidate's merit.** No grader ran, **no
paired statistic was computed, no decision rule was evaluated and no primary
outcome is reported**; no meeting outcome is recorded anywhere in this directory
per seed. The primary outcome, the decision rule, the minimum actionable effect,
`WRONGFUL_EJECTION_TRADEOFF` and `STOP_RULE` are untouched and no unit of this
calibration counts towards them. What it measures is what one call and one unit
CHARGE on each arm, split by the author's hidden role; how often a call runs past
its output cap; and the aggregate authored-ballot diagnostics the wave was sent
to move — read against six predictions the manifest fixed BEFORE the sitting,
none of which is a gate.

## The design

| Field | Value |
| --- | --- |
| Mode | `experiments/fresh_deduction_instrument.py --calibrate --calibration-mode 2026-09-18` |
| Inputs | the first sixty accepted seeds, ascending, across `CONVERTED_BANDS` in the order those bands were converted: all fifty of the 3000–3999 record, then 5000–5009 of the 5000–5999 record — the second calibration's draw to the seed |
| Arms | both, `repaired_clock` then `combined_accounts`, sequential, seed ascending, both arms per seed before the next seed |
| Units | 60 paired seeds x 2 arms = 120 units, 721 attempts |
| Provider / model | `featherless` / `Qwen/Qwen3.6-27B`, non-thinking, `json_object` |
| Prompt set | `qwen3_6_27b`, at `ACCOUNT_PROMPT_SET_REVISION` **v5** (`agents/strategic/prompts/loader.py`) |
| The revised wave, BOTH arms | `AILIBI_CITATION_RELEVANCE=1` on both, the v5 accounts templates on the candidate; each arm's resolved lever profile is published in the payload as `resolved_levers` |
| Sampling | turn 4,096 output at temperature 0.4; ballot 1,024 at 0.2 — `AUTHORIZED_SAMPLING` itself, so what is measured is the draw a run makes |
| Limits | `CALIBRATION_3_LIMITS`: per unit 116,000 in / 16,000 out, run 4,700,000 / 520,000, 5 h model work inside a 6 h elapsed window |
| Transport bound | 4 attempts per call, 180 s per attempt — the run's own, unchanged |
| Truncation | a MEASUREMENT in this mode, not a stop (`CALIBRATION_3_CLAUSE`); the live run's `STOP_RULE` is unedited |
| Instrument | `instrument_sha256` `1927ff6187c036444ba83e4240483d059a071001c6d4f44a1b3c9481582cc98a` |
| Held-out record | not read, not rendered, not touched: `verify_frozen_set` is never called on this path, and `verify_calibration_draw` refuses `held-out/manifest.json` by name |

**One sitting.** The calibration ran once, start to finish, and was not re-run,
resumed or restarted. It began at `2026-09-18T17:17:08Z`, ended at
`2026-09-18T20:16:13Z` and exited 0 with all 120 units complete and all 721
attempts resolved. The card's Constraints authorize one calibration and no retry
beyond the instrument's own transport bound; no retry was needed, because no
attempt failed in transport. A calibration has no checkpoint and no resume, and a
second sitting would need the owner's say.

## The input binding

Both records the draw spans were bound before any spend:

```sh
shasum -a 256 audits/deduction-candidate/held-out/manifest-band-3000-3999.json \
              audits/deduction-candidate/held-out/manifest-band-5000-5999.json
git diff --exit-code origin/main -- audits/deduction-candidate/held-out/manifest-band-3000-3999.json
git diff --exit-code origin/main -- audits/deduction-candidate/held-out/manifest-band-5000-5999.json
```

| Record | sha256 | Status | Accepted | Drawn |
| --- | --- | --- | --- | --- |
| [held-out/manifest-band-3000-3999.json](../held-out/manifest-band-3000-3999.json) | `ca4cd057acb2119646190fb6fff923a897ec207d5f54c491c3e1dfae0944cf3c` | `development` since 2026-09-10 | 50 (8 skipped) | all 50, seeds 3000–3057 |
| [held-out/manifest-band-5000-5999.json](../held-out/manifest-band-5000-5999.json) | `4fc831dafeda0a6ee7fc311e6557c149506be1fabcf05c69b2117ddb436f7711` | `development` since 2026-09-13 | 50 (3 skipped) | the first 10, seeds 5000–5009 |

Both `git diff --exit-code` invocations exit 0, so both files are byte-identical
to `origin/main`'s at `ef8081c3`. The same two digests are recorded inside the
output as `input_records[].record_sha256`, so the report names the bytes it drew
from. Band 8000–8999 was not read, rendered or named by anything this sitting
ran: its record is still the live held-out one at `MANIFEST_PATH` and
`_converted_band_for` refuses it by name.

## The measured profile

Per arm and per call type, over the 721 completions. `n` is the completion
count; `p95` is the nearest-rank percentile the report's `percentile_rule`
states (index `ceil(0.95 x n) - 1` of the ascending sample, no interpolation).

### `repaired_clock` (reference arm)

| Call type | n | in mean | in p95 | in max | out mean | out p95 | out max | out cap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| turn | 181 | 3,278.1 | 4,091 | 4,344 | 286.4 | 426 | 540 | 4,096 |
| ballot | 180 | 3,668.7 | 4,337 | 4,721 | 100.8 | 123 | 143 | 1,024 |

Per unit: input mean 20,895.1, max 25,247; output mean 1,166.3, max 1,602.
Arm totals: 1,253,706 input, 69,981 output over 361 attempts.

### `combined_accounts` (candidate arm)

| Call type | n | in mean | in p95 | in max | out mean | out p95 | out max | out cap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| turn | 180 | 3,397.5 | 4,736 | 5,477 | 476.2 | 835 | 1,187 | 4,096 |
| ballot | 180 | 4,753.1 | 6,227 | 7,354 | 99.8 | 123 | 130 | 1,024 |

Per unit: input mean 24,451.9, max 34,412; output mean 1,728.3, max 2,764.
Arm totals: 1,467,113 input, 103,696 output over 360 attempts.

The candidate arm charges **1.48x** the reference arm's output (103,696 against
69,981) and **1.17x** its input. On the same sixty seeds at revision v4 the two
ratios were 1.41x and 1.09x, and the candidate's ballot call is where the
cross-sitting input difference sits: 4,753.1 mean input against 4,272.6 on
2026-09-15, **+11.2%**, on a call type whose output did not move (99.8 against
93.3).

**That 11.2% is an OBSERVED difference between two sittings and not an estimate
of the wave's template bytes.** A seed holds the scripted prefix constant, not
the meeting the sitting then generates, and a ballot prompt renders that
generated transcript: this sitting's candidate turns are longer — turn output
mean 476.2 against the 2026-09-15 sitting's 443.0, on the same sixty seeds — so
the ballot prompt they feed is longer before a single template byte is counted.
The figure therefore mixes the v5 templates' static bytes with the growth of the
transcript they produce, in a proportion this sitting cannot separate; splitting
them needs a controlled-transcript measurement, which no sitting has made. What
does not depend on the split is the sizing: the largest charged unit is 34,412
input however the rise is apportioned, and every ceiling figure below is read off
that maximum rather than off this delta.

**Neither arm approaches a per-call cap.** The candidate's largest turn is 1,187
of 4,096 (29.0%) and its largest ballot 130 of 1,024 (12.7%); the reference's are
540 (13.2%) and 143 (14.0%).

**The reference arm made one extra call.** 361 attempts for 360 meeting slots:
one unit resolved seven calls where the meeting layer asked an opening twice on
its shipped single-retry path, exactly as the fifth run's seed 8026 did. It is
neither a transport retry nor a default — `retried_calls` and `degraded_openings`
are both 0 on that arm — and both calls are charged in the accounting below.

## The role split

Per arm, per call type, split by the AUTHOR's hidden role: the draws, the output
tokens, and the character lengths of the fields that carry prose. The two
denominators differ on purpose — `draws` counts calls made, `samples` counts
authored payloads — so a fail-softed call is a draw that produced no text.
Nothing in this section is prose: it is counts and lengths.

### `repaired_clock`

| Call | Role | draws | out mean | out p95 | out max | truncations |
| --- | --- | --- | --- | --- | --- | --- |
| turn | CREWMATE | 121 | 332.5 | 438 | 540 | 0 |
| turn | IMPOSTOR | 60 | 193.6 | 338 | 445 | 0 |
| ballot | CREWMATE | 120 | 101.3 | 122 | 143 | 0 |
| ballot | IMPOSTOR | 60 | 99.7 | 124 | 140 | 0 |

| Call | Role | Field | samples | chars mean | chars p95 | chars max |
| --- | --- | --- | --- | --- | --- | --- |
| turn | CREWMATE | `free_text` | 120 | 228.9 | 354 | 473 |
| turn | CREWMATE | `claims[].reason` | 126 | 74.1 | 129 | 214 |
| turn | IMPOSTOR | `free_text` | 60 | 200.4 | 314 | 414 |
| turn | IMPOSTOR | `claims[].reason` | 60 | 65.6 | 108 | 148 |
| ballot | CREWMATE | `rationale_text` | 120 | 104.5 | 151 | 253 |
| ballot | IMPOSTOR | `rationale_text` | 60 | 103.9 | 187 | 232 |

### `combined_accounts`

| Call | Role | draws | out mean | out p95 | out max | truncations |
| --- | --- | --- | --- | --- | --- | --- |
| turn | CREWMATE | 120 | 494.6 | 816 | 1,017 | 0 |
| turn | IMPOSTOR | 60 | 439.6 | 842 | 1,187 | 0 |
| ballot | CREWMATE | 120 | 100.9 | 123 | 128 | 0 |
| ballot | IMPOSTOR | 60 | 97.7 | 119 | 130 | 0 |

| Call | Role | Field | samples | chars mean | chars p95 | chars max |
| --- | --- | --- | --- | --- | --- | --- |
| turn | CREWMATE | `free_text` | 119 | 384.2 | 597 | 842 |
| turn | CREWMATE | `claims[].reason` | 115 | 117.8 | 230 | 338 |
| turn | IMPOSTOR | `free_text` | 60 | 256.7 | 344 | 470 |
| turn | IMPOSTOR | `claims[].reason` | 60 | 106.5 | 184 | 269 |
| ballot | CREWMATE | `rationale_text` | 120 | 108.7 | 135 | 167 |
| ballot | IMPOSTOR | `rationale_text` | 60 | 104.2 | 129 | 231 |

Three readings worth stating rather than leaving to a reader.

**The candidate's crewmate `free_text` has a shorter tail than the surface it
replaces.** Its maximum is 842 characters against the 2026-09-15 sitting's 4,258
on the same seeds, and its p95 falls from 670 to 597 while its mean rises from
401.6 to 384.2 — which is to say it did not rise. The turn output maximum falls
with it, 1,884 to 1,187.

**The candidate's crewmate `free_text` has one fewer sample than its draws.**
119 samples over 120 draws is the arm's one defaulted turn: a fail-softed call is
a draw that produced no authored text, so it is in the draw denominator and not
in the length one.

**`claims[].reason` has its own denominator on both arms.** 126 samples over 121
reference crewmate turn draws and 115 over 120 candidate ones: a turn may carry
more than one claim or none, so the claim row counts claims and the `free_text`
row counts turns.

## Truncation

**Zero, on both arms, on every call type and for both roles.** No completion of
the 721 reached its output cap by either signal.

| Arm | Denominator | draws | truncations | rate | Wilson 95% |
| --- | --- | --- | --- | --- | --- |
| `combined_accounts` | impostor-authored ballot draws | 60 | 0 | 0.00% | [0.00%, 6.02%] |
| `combined_accounts` | all ballot draws | 180 | 0 | 0.00% | [0.00%, 2.09%] |
| `combined_accounts` | all draws | 360 | 0 | 0.00% | [0.00%, 1.06%] |
| `repaired_clock` | impostor-authored ballot draws | 60 | 0 | 0.00% | [0.00%, 6.02%] |
| `repaired_clock` | all ballot draws | 180 | 0 | 0.00% | [0.00%, 2.09%] |
| `repaired_clock` | all draws | 361 | 0 | 0.00% | [0.00%, 1.05%] |

The interval is computed by `scripts/paired_stats.py`'s `wilson_interval`. The
second calibration and the fifth run each measured the same zero on their own
denominators, so this is the third consecutive live measurement in which the
per-call tail the fourth run stopped on does not recur — at a prompt surface
whose candidate ballot input is 11.2% larger than the one the second calibration
measured.

### `finish_reason`, and the two signals

| Arm | rows | `finish_reason` | observed truncations | inferred truncations | disagreements |
| --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 361 | `{"stop": 361}` | 0 | 0 | 0 |
| `combined_accounts` | 360 | `{"stop": 360}` | 0 | 0 | 0 |

`observed` is the provider's own `finish_reason == "length"`; `inferred` is
`output_tokens >= max_tokens`, the comparison this instrument has always made.
Every one of the 721 rows carries `"stop"`, on both call types, the two readings
agree on every row, and no row is silent. **The cap-signal disagreement count is
0 on each arm.**

## The impostor self-tell

Impostor-authored ballots whose `rationale_text` OPENS by stating that role or a
kill that voter committed (`opens_with_a_self_tell`):

| Arm | self-telling ballots | impostor ballot draws | share |
| --- | --- | --- | --- |
| `combined_accounts` | 28 | 60 | 46.7% |
| `repaired_clock` | 3 | 60 | 5.0% |

On the same sixty seeds at v4 the two figures were 39 of 60 (65.0%) and 9 of 60
(15.0%); the fifth run's, on held-out prefixes, were 29 of 50 (58.0%) and 3 of 50
(6.0%). So the self-tell falls on both arms at v5 and has not gone away on the
candidate: the model still writes the concealment plan from the private truth
forward in a little under half of its impostor ballots.

## The public-transcript role leak

The pre-declared diagnostic of the owner's decision 9, counted by
`ROLE_LEAK_RULE`, which the payload quotes in full:

| Arm | leaking turns | units with a leaking turn | units |
| --- | --- | --- | --- |
| `combined_accounts` | 0 | 0 | 60 |
| `repaired_clock` | 0 | 0 | 60 |

Zero on both arms, on the guard the diagnostics card repaired — the interrogative
family is now the three question words crossed with four auxiliaries, so the
shape that produced the fifth run's reference false positive cannot be counted
here. On the same sixty seeds at v4 the count was 1 candidate unit and 0
reference; the fifth run's was 1 of 50 candidate and, under the rule as written,
0 of 50 reference.

**The count is an ESTIMATE carrying error in BOTH directions and is not a
floor.** `ROLE_LEAK_RULE` says so in those words. The rule reads no intent, so an
impostor that confesses in words its two shapes do not match is missed; and its
guards see one sentence at a time, so an attribution, denial or supposition
spread across two sentences is counted. It is a reported diagnostic and not a
gate: no stop condition reads it, the decision rule does not mention it, and it
changes no primary outcome. A numerator of zero on a two-sided rule bounds the
leak loosely rather than measuring it, and zero leaking turns does not mean zero
leaks.

**The `role_leak_rule` string this payload quotes is the LIVE evaluation's, and
two of its sentences do not fit a calibration.** It says the count is "a reported
column beside the primary outcome" and "a further reason to read it beside the
outcome rather than to gate on it", while this mode reports no primary outcome
at all — `CALIBRATION_3_CAVEAT` says so and
`assert_calibration_reports_no_outcome` enforces it over these same bytes. It is
the same split the third calibration card already made for
`AUTHORED_DIAGNOSTICS_NOTE`, not yet made for this string; `ROLE_LEAK_RULE` is an
instrument byte, and a run pull request may not move one, so the repair is routed
to the sixth authorization's instrument work with the four missing counters
above. Nothing in this directory is misread in the meantime: the two clauses
argue that the column is not a gate, which is what this mode also says, the
column is 0 on BOTH arms, and there is no outcome here to read it beside. The
full disposition is under "Review corrections".

## Refusals, defaults and charged failed attempts

| Per arm | `repaired_clock` | `combined_accounts` |
| --- | --- | --- |
| charged failed attempts (billed and refused) | 0 | **1** (2,885 in / 459 out) |
| defaulted turns | 0 | **1** |
| defaulted votes | 0 | 0 |
| defaults by schema validation | 0 | **1** |
| defaults by deadline | 0 | 0 |
| units with any default | 0 | **1** |
| degraded openings | 0 | 0 |
| completions | 361 of 361 attempts | 360 of 360 attempts |

**The one default and the one charged failed attempt are the same call**, on the
candidate arm: the provider billed a completion and refused it on its own schema
validation, and the meeting layer's shipped fail-soft substituted a placeholder
turn. The instrument classified its phase and trigger without complaint, so the
"a default this instrument cannot classify is a stop" condition did not fire. It
is the same class and the same rate the fifth run recorded — 1 substitution in
601 attempts there, 1 in 721 here — and it is the CANDIDATE arm that recorded it
in both. The `union_tag_invalid` refusals the diagnosis of 2026-09-13 found did
not recur at revision v5, as they did not at v3 or v4.

A defaulted turn is not a defaulted ballot: the arm's 180 ballots are all the
voter's own, `defaulted_votes` is 0, and the one unit carrying a substitution is
the bound on how many of this arm's diagnostics rest on a partly unauthored
meeting.

## Transport

| Per arm | `repaired_clock` | `combined_accounts` |
| --- | --- | --- |
| attempts | 361 | 360 |
| retried calls | 0 | 0 |
| unaccounted attempts | 0 | 0 |
| aborted attempts | 0 | 0 |
| attempts by trigger | none | none |

721 sends produced 720 completions and one billed-and-refused completion; no row
carries the `no-completion-returned` marker and the transport bound (4 attempts,
180 s each) was in force and never engaged.

## The authored-ballot DIAGNOSTICS block

Per arm, as the payload carries it, with the note it is published under quoted in
the artifact. Every count here is conditioned on a ballot having been AUTHORED as
an ejection, so it flatters whichever arm authors more and says nothing about how
often an arm decides correctly. The crew per-ballot precision is reported ONLY
beside its harm counter. None of these is a decision input: no stop condition
reads one, the decision rule does not mention one, none is a field of any paired
result, and none was preregistered.

### Authored register, over the 180 recorded ballots of each arm

The AUTHORED columns recompute from the committed payload —
`authored_diagnostics.by_voter_role[].authored` sums to 23 on the reference and
39 on the candidate. The RECORDED columns are read off the replays and do not;
see "Review corrections".

| Arm | authored EJECT | authored SKIP | recorded EJECT | recorded SKIP |
| --- | --- | --- | --- | --- |
| `repaired_clock` | 23 | 157 | 22 | 158 |
| `combined_accounts` | **39** | 141 | 36 | 144 |

### Crew per-ballot precision, and its harm counter

| Arm | crew authored EJECTs | naming the impostor | share | one-sided p vs 0.5 | crew-on-crew authored EJECTs | units carrying one |
| --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 15 | 6 | 40.0% | 0.849 | 9 | 9 of 60 |
| `combined_accounts` | 27 | 13 | 48.1% | 0.649 | 14 | 14 of 60 |

The null is 0.5, each crewmate having exactly two legal targets on this roster.
Neither arm separates from it.

### The gate's survival rate, by voter role

| Arm | Role | authored | cleared | survival | coerced | illegal targets |
| --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | CREWMATE | 15 | 15 | **100.0%** | 0 | 0 |
| `repaired_clock` | IMPOSTOR | 8 | 7 | 87.5% | 1 | 0 |
| `combined_accounts` | CREWMATE | 27 | 26 | **96.3%** | 1 | 0 |
| `combined_accounts` | IMPOSTOR | 12 | 10 | 83.3% | 2 | 0 |

### The authored coalition funnel

An authored coalition is two or more ballots authored at the same legal target in
one unit. `cleared` counts coalitions every ballot of which reached the tally;
`converted` counts those that reached it ON THE AUTHORED TARGET.

| Arm | Coalition | authored | cleared | converted | conversion |
| --- | --- | --- | --- | --- | --- |
| `repaired_clock` | correct | 0 | 0 | 0 | — |
| `repaired_clock` | wrongful | 3 | 3 | 3 | 100.0% |
| `combined_accounts` | correct | 1 | 1 | 1 | 100.0% |
| `combined_accounts` | wrongful | 8 | 8 | 8 | 100.0% |

### Guard rewrites, by reason

Over `BallotTargetRewriteReason`, counted off the marker stack each rewrite
prepends rather than off a substring search.

| Arm | `off_target_coerced` | `uncited_coerced` | `under_gate_redirect` | `teammate_coerced` | `invalid_target` | `parse_default` |
| --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 1 | 0 | 0 | 0 | 0 | 0 |
| `combined_accounts` | 3 | 0 | 1 | 0 | 0 | 0 |

### The citation channel, and the contradiction detector

**Read off the sitting's own replays, which are NOT committed, so no figure in
the two tables below recomputes on a clean checkout.** The derivation is quoted
in "What was archived" and the disposition is under "Review corrections": the
counters that would close this are instrument bytes, which a run pull request may
not move, and they are routed to the sixth authorization's instrument work.

| Arm | ballots | surviving `primary_reason_id` | nulled (model emitted one, the record holds none) | surviving `…_observation_id` | model emitted BOTH ids null |
| --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 180 | 19 | **0** | 10 | 157 |
| `combined_accounts` | 180 | **32** | **0** | 10 | 141 |

| Arm | contradiction flags | units carrying one | by kind | claim vocabulary (accusation / alibi / corroboration) |
| --- | --- | --- | --- | --- |
| `repaired_clock` | 7 | 6 of 60 | 3 `alibi_conflict`, 4 `alibi_vs_sighting` | 174 / 42 / 12 |
| `combined_accounts` | **0** | **0 of 60** | — | 175 / 0 / 0 |

### Ejections, by role-correctness

| Arm | ejections | role-correct | p vs the 1/3 chance rate | crew-authored role-correct | p |
| --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 3 | 0 | 1.0 | 0 | 1.0 |
| `combined_accounts` | 9 | 1 | 0.974 | 1 | 0.974 |

## The six predictions

The manifest fixed these six BEFORE the sitting, copied verbatim from the card's
Evidence table, and `CALIBRATION_3_PREDICTIONS` holds the same six rows. Each
"fifth run" cell is that run's own figure, measured on the **8000–8999 prefixes**
— different inputs, and 50 paired seeds against this sitting's 60 — so each is a
DIRECTION rather than a threshold. The manifest says so beside its own copy:

> These six are PREDICTIONS and none of them is a gate. They are read against the fifth run's figures, which were measured on different prefixes, so each is a direction rather than a threshold: a miss is neither a stop nor a verdict, and no decision rule reads any of them.

| # | Prediction, as the manifest states it | Fifth run | This sitting (candidate arm) | Verdict |
| --- | --- | --- | --- | --- |
| P1 | F6 costs the impostor its free pass: **the gap narrows** | impostor EJECTs survive 86.8%, crew 51.9% (impostor ahead by 34.9 pp) | impostor 10 of 12 = 83.3%, crew 26 of 27 = 96.3% (crew ahead by 13.0 pp) | **held** — the gap did not narrow, it inverted |
| P2 | F6 attacks stage 2: **wrongful falls to or below correct** | wrongful coalitions convert 36.4% (8 of 22), correct 18.2% (2 of 11) | wrongful 8 of 8 = 100.0%, correct 1 of 1 = 100.0% | **did not hold** — the wrongful rate did not fall, it ROSE from 36.4% to 100.0%; the relative-order clause is satisfied only by a tie at the ceiling, against a correct denominator of one. Re-labelled on review; see "Review corrections" |
| P3 | F7 equalises the register: **authored EJECTs fall toward 14** | candidate authors 119 EJECT / 31 SKIP of 150 (79.3%) | 39 EJECT / 141 SKIP of 180 (21.7%), against this sitting's reference at 23 of 180 (12.8%) | **held** — the candidate's authoring rate fell by a factor of 3.7 and now sits within 9 points of its own reference |
| P4 | F4 revives the turn channel: **surviving ids rise, coercions fall** | 0 of 150 keep a `primary_reason_id`; 27 nulled; 44 coerced (`uncited_coerced`) | 32 of 180 keep one; **0** nulled; **0** `uncited_coerced` | **held on both halves** — the coercion half recomputes from the committed payload; the surviving/nulled-id half is replay-derived and does NOT, see "Review corrections" |
| P5 | The deduction signal is real: **holds near 63% once volume falls** | crew authored EJECTs name the impostor 51 of 81 (63.0%, p 0.013) | 13 of 27 (48.1%, p 0.649) | **did not hold** — the rate fell to chance on a denominator a third the size |
| P6 | The vocabulary un-collapses: **flags rise above 1** | 1 contradiction flag against the reference's 14 | **0** flags against the reference's 7; claims 175 accusation / 0 alibi / 0 corroboration against 174 / 42 / 12 | **did not hold** — the candidate's claim vocabulary is still accusations only, and its detector is now silent rather than nearly silent. Every figure in this row is replay-derived and does NOT recompute from the committed payload, see "Review corrections" |

**Three of the six held and three did not**: P1 and P3 held, P4 held on both of
its halves, and P2, P5 and P6 did not. P2's verdict was re-labelled on review —
it was first published as "held by the letter, on n = 1" — because the
prediction is that the wrongful conversion rate FALLS to or below the correct
one and it rose instead; the paragraph under "Review corrections" is that
disposition. Nothing in the tally is a gate or a bar, and no decision reads it.

**What this table is not.** The baseline column is the fifth run, measured on
DIFFERENT prefixes at a different sample size; a difference between the two
columns is not an effect estimate and no interval is computed for one. None of
the six is a gate, a stop or a bar. **No paired statistic was computed, no
primary outcome is reported and no decision rule was evaluated** — the payload
carries no `paired` block and no `supported_correct_ejection` field, and
`assert_calibration_reports_no_outcome` refuses one that does.

Two of the six read on the reference arm as well, and are stated here because a
one-arm reading of them would mislead: the reference arm's own citation channel
carries 19 surviving turn ids of 180 where the fifth run's carried 14 of 150, and
the reference's contradiction detector fell from 14 flags to 7 — so the
candidate's 0 is a collapse relative to a reference that also moved down.

## Pace

**14.89 s per attempt** pooled over 721 attempts: 13.49 s on the reference arm
and 16.30 s on the candidate. Model work totalled 10,737.2 s inside 10,744.1 s
elapsed — the calibration is sequential, so the two are the same clock less
setup.

The card sized the wall against about 12.9 s per call on the fifth run's
candidate arm and 11.65 s on calibration 2's, and called it a 1.9x margin at
25.0 s per call. The realised pace is slower than both of those figures and the
realised margin is **1.68x**: 720 calls at this pace need 10,737 s of the
authorized 18,000 s. At this pace the held-out design's ~600 sequential calls
need about 2.5 h of model work.

## Actual usage against the calibration-3 limits

| Dimension | Charged | Ceiling | Used |
| --- | --- | --- | --- |
| run input tokens | 2,720,819 | 4,700,000 | 57.9% |
| run output tokens | 173,677 | 520,000 | 33.4% |
| largest unit input | 34,412 | 116,000 | 29.7% |
| largest unit output | 2,764 | 16,000 | 17.3% |
| model work | 10,737.2 s | 18,000 s | 59.7% |
| elapsed | 10,744.1 s | 21,600 s | 49.7% |
| per-call output cap, turn | largest 1,187 (candidate) | 4,096 | 29.0% |
| per-call output cap, vote | largest 143 (reference) | 1,024 | 14.0% |
| transport attempts | 1 attempt per call, 721 of 721 | 4 per call, 180 s each | 25% of the bound |

No ceiling fired and none came close. **$0.00 marginal**, the report's
`total_cost_usd` and both arms' `cost_usd`, on the same flat-rate subscription
and for the same reason as the manifest's cost statement: the Featherless
provider's zero pre-flight rate disables `BudgetedLLMClient`'s USD dimension, so
the token budget and the wall deadline are the only limits that could have
stopped this sitting.

## The ceiling proposal

Computed by `ceiling_proposal` and carried in the output as `proposal`, with
`CEILING_PROPOSAL_RULE` quoted beside it. For the held-out design's **100**
units:

| Ceiling | Proposed |
| --- | --- |
| per unit input | **104,000** |
| per unit output | **16,000** |
| run input | **3,442,000** |
| run output | **281,000** |

The two rules, reported separately because they disagree:

| Run ceiling | mean rule (100 x mean x 1.5) | max floor (100 x max, + one turn cap on output) | adopted |
| --- | --- | --- | --- |
| input | 3,402,000 | 3,442,000 | 3,442,000 (the floor) |
| output | 218,000 | 281,000 | 281,000 (the floor) |

The floor binds on both dimensions, as it did on 2026-09-15: the largest unit is
1.52x the pooled mean unit on input (34,412 against 22,673.5) and 1.91x on output
(2,764 against 1,447.3), both above the 1.5 margin. The output floor carries the
in-flight headroom term the gate enforces — 100 x 2,764 + 4,096 = 280,496,
rounded up to 281,000. The per-unit figures take no such disagreement: input is
3 x 34,412 = 103,236 -> 104,000, and output is max(15,360 reservation schedule,
3 x 2,764) = 15,360 -> 16,000.

`clears_the_feasibility_gate: true`, `feasibility_refusal: null`. That check runs
against the maxima THIS sitting measured, which is the proposal's own claim —
these ceilings pay for a run of the units it saw — and it is **true by
construction**, because the rule computes the four figures from those same
maxima. `clears_the_committed_profiles_gate: false`, and its
`committed_profile_refusal` is the check that is not by construction: the same
four figures against the constants this tree carries (38,440 / 4,176, the second
calibration's maxima), which the proposed run-level OUTPUT ceiling does NOT
clear, because a hundred units of 4,176 plus the in-flight term need 421,696 and
this proposal is sized at 281,000. That is this sitting's units being SMALLER
than the committed profile's on output — 2,764 against 4,176 — and a proposal
sized on the smaller does not clear the larger. It is a fact about which
measurement each gate reads, not a defect and not a refusal of anything this
sitting did.

**The proposal authorizes nothing.** A ceiling is the owner's, on a card, and
`assert_live_run_is_authorized` keeps refusing any limits but the ones it is
handed.

## The committed usage profile was NOT refreshed, by the card's own rule

The card's Constraints settle this in advance: the refresh of
`tests/experiments/deduction_usage_profile.json`, the two calibrated constants at
`CALIBRATED_UNIT_INPUT_TOKENS` / `CALIBRATED_UNIT_OUTPUT_TOKENS` and their
dependent test `test_the_calibration_is_the_largest_unit_the_archives_charged`
belong to [the sixth authorization's limits card](../../../tasks/work/fresh-deduction-limits-6.md),
"not to this card and not to the runner". No committed profile byte and neither
constant moved here.

The refresh was run into a path outside version control so its numbers could be
reported, and they are, as numbers only:

```sh
.venv/bin/python -m experiments.fresh_deduction_instrument \
  --refresh-usage-profile audits/deduction-candidate/calibration-3-2026-09-18/calibration.json \
  --profile-out <a path outside version control>
```

721 call rows, 120 unit rows, `built_from.mode` `2026-09-18`, `built_from.records`
`[("3000-3999", 50), ("5000-5999", 10)]`, totals `resolved_calls` 720,
`refused_calls_with_usage` 1, **`largest_charged_unit_input_tokens` 34,412**,
**`largest_charged_unit_output_tokens` 2,764**. The ceiling proposal those maxima
produce is the one above: 104,000 / 16,000 per unit, 3,442,000 / 281,000 per run.

One arithmetic consequence, stated and not acted on: a hundred units of this
sitting's largest unit need 3,441,200 input and 280,496 output, and the standing
`AUTHORIZED_LIMITS` run ceilings — 3,844,000 and 422,000, re-sized by the fifth
authorization on the second calibration — clear both. Where the 2026-09-15
sitting handed its authorization a ceiling that no longer cleared, this one hands
its successor a profile that the standing ceilings already pay for. Which
constants move, and whether, is the limits card's.

## Comparison with the two earlier calibrations and the fifth run

| Quantity | 2026-09-14 (v3) | 2026-09-15 (v4, same 60 seeds) | Run 5 (v4, held-out) | This sitting (v5 + the guard, same 60 seeds) |
| --- | --- | --- | --- | --- |
| Units / attempts | 10 / 60 | 120 / 720 | 100 / 601 | **120 / 721** |
| Candidate per-unit input | 28,430.2 | 22,733.8 | 23,684 | **24,451.9** |
| Candidate per-unit output | 3,137.0 | 1,608.9 | 1,705 | **1,728.3** |
| Reference per-unit input | 21,025.8 | 20,862.4 | 21,194 | **20,895.1** |
| Reference per-unit output | 1,107.8 | 1,141.5 | 1,189 | **1,166.3** |
| Largest unit | 35,232 / 4,590 | 38,440 / 4,176 | 34,683 / 2,898 | **34,412 / 2,764** |
| Candidate turn out max | 2,036 (99.4% of a 2,048 cap) | 1,884 (46.0%) | 1,075 (26.2%) | **1,187 (29.0%)** |
| Candidate ballot out max | 237 | 135 (13.2%) | 132 (12.9%) | **130 (12.7%)** |
| Impostor candidate ballot truncations | not measured | 0 of 60 | 0 of 50 | **0 of 60** |
| Candidate impostor self-tells | not measured | 39 of 60 (65.0%) | 29 of 50 (58.0%) | **28 of 60 (46.7%)** |
| Candidate units with a leaking turn | not measured | 1 of 60 | 1 of 50 | **0 of 60** |
| Pooled pace | 17.23 s | 10.28 s | 11.46 s | **14.89 s** |
| Refusals / defaults / retries | 0 / 0 / 0 | 0 / 0 / 0 | 1 / 1 / 0 | **1 / 1 / 0** |

**Cross-sitting comparison is on INPUTS, not on arms.** The 2026-09-15 column is
the same sixty seeds, so the token profile compares directly and the wave's
prompt bytes are the only CONFIGURED thing that moved between those two — but a
seed fixes the scripted prefix and not the meeting each sitting generates, so a
difference between the two columns mixes the wave's bytes with the difference
between two hosted generations at nonzero temperature, and is an observed
difference rather than an effect estimate. The reference arm
was RE-BASELINED by the citation guard, which both arms of this sitting enable,
so no reference cell of the fifth run or of either earlier calibration is a
like-for-like control for this one; and the fifth run's column is a different
band.

## What was archived, and how to reproduce every number

Everything in this directory:

| File | What it is |
| --- | --- |
| `calibration.json` | the mode's whole output, 206,332 bytes; every figure above is read from it EXCEPT the four replay-derived ones named below |
| `unit-usage.jsonl` | the 120 per-unit usage rows, extracted verbatim from `calibration.json`'s `unit_usage` block |
| `calibration-run.log` | the sitting's log: the start and end stamps, the documented command with its credential and output paths elided, the exit code, and the payload the mode printed to stdout |
| `CALIBRATION.md` | this file |

The rendered prompts and prefixes are development data and are NOT committed: the
sitting's replays went to an `--output-dir` outside version control, as the
manifest requires, and a per-seed reading of the six predictions is available
there and nowhere else. The output itself carries no prompt, no prefix, no step
and no outcome — `assert_report_holds_no_prefix_bytes` was re-run over the
archived payload against all sixty rebuilt prefixes and passed, and
`assert_calibration_reports_no_outcome` passed over the same bytes — and the 721
`calls` rows carry exactly six fields each: `arm`, `call_type`, `input_tokens`,
`output_tokens`, `disposition`, `finish_reason`. The log's stdout body is
byte-identical to `calibration.json` (both sha256
`ce5e95610ba390a9bd0c871252baf42188316c036620c76164dc4a8570556984`); the
credential scan over every file in this directory, comparing counts only against
the key's first six characters and against the whole key, returns zero on both.

Read the output:

```sh
.venv/bin/python -m json.tool audits/deduction-candidate/calibration-3-2026-09-18/calibration.json
```

Recompute every derived figure this file reads off the payload — the per-arm and
per-call-type profile, the role split and its prose lengths, the truncation rates
with their Wilson intervals, the `finish_reason` and cap-signal-disagreement
counts, the self-tell and leak counts, the refusal, default and transport counts,
the whole diagnostics block, the pace, the usage against the limits and both
ceiling rules:

```sh
.venv/bin/python - <<'PY'
import json, math
from collections import Counter
from pathlib import Path
from scripts.paired_stats import wilson_interval
d = json.loads(Path(
    "audits/deduction-candidate/calibration-3-2026-09-18/calibration.json").read_text())
L, S, P = d["limits"], d["sampling"], d["proposal"]
caps = {"turn": S["turn_max_tokens"], "vote": S["vote_max_tokens"]}
up = lambda v: int(math.ceil(v / 1000.0) * 1000)
for r in d["input_records"]:
    print(r["record"], r["record_sha256"], r["status"],
          "| drawn", len(r["seeds"]), r["seeds"][0], "..", r["seeds"][-1])
for a in d["arms"]:
    print(a["arm"], "units", a["units"], "attempts", a["attempts"],
          "completions", a["completions"],
          "| refused", a["charged_failed_attempts"],
          a["charged_failed_input_tokens"], a["charged_failed_output_tokens"],
          "| defaults", a["defaulted_turns"], a["defaulted_votes"],
          a["defaults_by_validation"], a["defaults_by_deadline"],
          a["degraded_openings"], a["units_with_defaults"],
          "| retried", a["retried_calls"], "unaccounted", a["unaccounted_attempts"],
          "aborted", a["aborted_attempts"], dict(a["attempts_by_trigger"]),
          "| s/attempt %.2f" % a["seconds_per_attempt"])
    print("   levers", dict(sorted(a["resolved_levers"].items())))
    for c in a["by_call_type"]:
        print("  ", c["call_type"], "n", c["completions"],
              "| in mean %.1f p95 %d max %d" % (c["input_mean"], c["input_p95"], c["input_max"]),
              "| out mean %.1f p95 %d max %d cap %d" % (
                  c["output_mean"], c["output_p95"], c["output_max"], c["max_tokens"]))
    for r in a["by_role"]:
        print("   ", r["call_type"], r["role"], "draws", r["draws"],
              "| out mean %.1f p95 %d max %d" % (
                  r["output_mean"], r["output_p95"], r["output_max"]),
              "| truncations", r["truncations"], r["truncations_by_finish_reason"])
        for ln in r["lengths"]:
            print("        ", ln["field"], "samples", ln["samples"],
                  "| chars mean %.1f p95 %d max %d" % (ln["mean"], ln["p95"], ln["max"]))
    for label, rows in (
        ("impostor ballot", [r for r in a["by_role"]
                             if r["call_type"] == "ballot" and r["role"] == "IMPOSTOR"]),
        ("all ballot", [r for r in a["by_role"] if r["call_type"] == "ballot"]),
        ("all", list(a["by_role"])),
    ):
        draws = sum(r["draws"] for r in rows)
        trunc = sum(r["truncations"] for r in rows)
        lo, hi = wilson_interval(trunc, draws)
        print("   %s truncations %d/%d = %.2f%% Wilson [%.2f%%, %.2f%%]" % (
            label, trunc, draws, 100 * trunc / draws, 100 * lo, 100 * hi))
    rows = [c for c in d["calls"] if c["arm"] == a["arm"]]
    reasons, observed, inferred, disagree = Counter(), 0, 0, 0
    for c in rows:
        reasons["null" if c["finish_reason"] is None else c["finish_reason"]] += 1
        cap = caps["vote" if c["call_type"] == "ballot" else "turn"]
        obs, inf = c["finish_reason"] == "length", c["output_tokens"] >= cap
        observed += obs; inferred += inf
        disagree += c["finish_reason"] is not None and obs != inf
    print("   finish_reason", dict(sorted(reasons.items())),
          "| observed", observed, "inferred", inferred, "disagreements", disagree,
          "| dispositions", dict(sorted(Counter(c["disposition"] for c in rows).items())))
    print("   self-telling impostor ballots", a["self_telling_impostor_ballots"],
          "| leaking turns", a["leaking_turns"],
          "| units with one", a["units_with_a_leaking_turn"])
    print("   unit in mean %.1f max %d | unit out mean %.1f max %d | totals %d/%d"
          % (a["mean_unit_input_tokens"], a["max_unit_input_tokens"],
             a["mean_unit_output_tokens"], a["max_unit_output_tokens"],
             a["input_tokens"], a["output_tokens"]))
    b = a["authored_diagnostics"]
    print("   DIAGNOSTICS crew authored", b["crew_authored_ejects"],
          "naming impostor", b["crew_authored_naming_impostor"],
          "p %.4g" % b["crew_authored_precision_p"],
          "| HARM crew-on-crew", b["crew_on_crew_authored_ejects"],
          "units", b["units_with_crew_on_crew"])
    for row in b["by_voter_role"]:
        print("      ", row["role"], "authored", row["authored"], "cleared", row["cleared"],
              "coerced", row["coerced"], "illegal", row["illegal_targets"])
    print("       coalitions correct %d/%d/%d wrongful %d/%d/%d (authored/cleared/converted)"
          % (b["correct_coalitions"], b["correct_coalitions_cleared"],
             b["correct_coalitions_converted"], b["wrongful_coalitions"],
             b["wrongful_coalitions_cleared"], b["wrongful_coalitions_converted"]))
    print("       ejections", b["ejections"], "role-correct", b["role_correct_ejections"],
          "p %.4g" % b["role_correct_p"], "| crew-authored role-correct",
          b["crew_authored_role_correct_ejections"], "p %.4g" % b["crew_authored_role_correct_p"])
    print("       rewrites", dict(sorted(b["guard_rewrites_by_reason"].items())))
ti = sum(a["input_tokens"] for a in d["arms"])
to = sum(a["output_tokens"] for a in d["arms"])
print("run  %d/%d in (%.1f%%)  %d/%d out (%.1f%%)" % (
    ti, L["run_max_input_tokens"], 100 * ti / L["run_max_input_tokens"],
    to, L["run_max_output_tokens"], 100 * to / L["run_max_output_tokens"]))
print("work %.1f/%.0f s (%.1f%%) | elapsed %.1f/%.0f s (%.1f%%) | %.2f s/attempt" % (
    d["model_work_seconds"], L["model_work_seconds"],
    100 * d["model_work_seconds"] / L["model_work_seconds"],
    d["elapsed_seconds"], L["elapsed_seconds"],
    100 * d["elapsed_seconds"] / L["elapsed_seconds"], d["seconds_per_attempt"]))
print("cost", d["total_cost_usd"], "| units", d["units"], "| mode", d["mode"])
print("proposal per unit %d/%d run %d/%d clears %s committed %s" % (
    P["unit_max_input_tokens"], P["unit_max_output_tokens"],
    P["run_max_input_tokens"], P["run_max_output_tokens"],
    P["clears_the_feasibility_gate"], P["clears_the_committed_profiles_gate"]))
print("mean rule  run in %d out %d" % (
    up(P["units"] * P["measured_mean_unit_input_tokens"] * 1.5),
    up(P["units"] * P["measured_mean_unit_output_tokens"] * 1.5)))
print("max floor  run in %d out %d" % (
    up(P["units"] * P["measured_max_unit_input_tokens"]),
    up(P["units"] * P["measured_max_unit_output_tokens"] + S["turn_max_tokens"])))
PY
```

And the per-unit rows, which are the same bytes as `unit-usage.jsonl`:

```sh
.venv/bin/python -c "import json;d=json.load(open('audits/deduction-candidate/calibration-3-2026-09-18/calibration.json'));[print(json.dumps(u,sort_keys=True)) for u in d['unit_usage']]"
```

The authored register, the citation channel and the contradiction detector are
the four figures this file reads off the REPLAYS rather than the payload — the
authored EJECT/SKIP split, the surviving and nulled `primary_reason_id` counts,
the contradiction flags and the claim vocabulary. **They do NOT recompute on a
clean checkout**, because the replays they are read off are development data that
the manifest keeps outside version control and this directory holds none of them;
the command below needs the sitting's own `--output-dir`, which no longer exists.
"Review corrections" below states that disposition in full, names the manifest
clause it rests on, and separates the sub-claims that DO recompute from the
payload from the ones that do not. The derivation is recorded here because it is
the definition of each count and because the next sitting's instrument work is to
fold these four counters into the payload; it prints counts and never a
rationale, a prompt or a model output:

```sh
.venv/bin/python - <<'PY'
import json
from collections import Counter
from pathlib import Path
from experiments.fresh_deduction_instrument import (
    _authored_an_ejection, ballot_rewrites_that_fired)
from meetings.schemas import VoteBallot
REPLAYS = Path("<the sitting's --output-dir>")
tally = Counter()
for path in sorted(REPLAYS.glob("*.jsonl")):
    arm = path.stem.rsplit("-seed-", 1)[0]
    rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    meeting = next(r for r in rows if r["kind"].startswith("meeting"))
    tally[(arm, "units")] += 1
    flags = meeting.get("contradictions") or []
    tally[(arm, "contradiction_flags")] += len(flags)
    tally[(arm, "units_with_a_flag")] += int(bool(flags))
    for flag in flags:
        tally[(arm, "flag:" + flag["kind"])] += 1
    for turn in meeting["transcript"]["turns"]:
        for claim in turn.get("claims") or []:
            tally[(arm, "claim:" + claim["type"])] += 1
    said = {}
    for call in meeting["llm_calls"]:
        try:
            parsed = json.loads(call.get("response_text") or "")
        except Exception:
            continue
        if isinstance(parsed, dict) and "target" in parsed:
            said[call["agent_id"]] = parsed
    for raw in meeting["ballots"]:
        ballot = VoteBallot.model_validate(raw)
        tally[(arm, "ballots")] += 1
        tally[(arm, "authored_eject" if _authored_an_ejection(ballot) else "authored_skip")] += 1
        tally[(arm, "recorded_skip" if ballot.target == "SKIP" else "recorded_eject")] += 1
        tally[(arm, "surviving_turn_id")] += ballot.primary_reason_id is not None
        tally[(arm, "surviving_obs_id")] += ballot.primary_reason_observation_id is not None
        for reason in ballot_rewrites_that_fired(ballot):
            tally[(arm, "rewrite:" + reason)] += 1
        payload = said.get(ballot.voter)
        if payload is None:
            continue
        emitted = payload.get("primary_reason_id")
        if emitted not in (None, ""):
            tally[(arm, "model_emitted_turn_id")] += 1
            tally[(arm, "nulled_turn_id")] += ballot.primary_reason_id is None
for key in sorted(tally):
    print(key[0], key[1], tally[key])
PY
```

## Limitations

* **This measured cost, shape and the authored layer — not merit.** No grader
  ran, no paired statistic was computed, no decision rule was evaluated and no
  primary outcome is reported, so nothing here says whether the candidate arm
  deduces better, and no unit of it counts towards the frozen analysis.
* **The six predictions are directions, not thresholds.** They are read against
  the fifth run's figures, measured on the 8000–8999 prefixes at 50 paired seeds
  rather than on this draw's 60. A miss is neither a stop nor a verdict, and no
  decision rule reads any of them.
* **Cross-sitting comparison is on inputs, not on arms.** The draw is
  calibration 2's to the seed, so the token profile compares; the reference arm
  was re-baselined by the citation guard, which both arms of this sitting enable,
  so no reference cell of an earlier sitting is a control for this one.
* **The diagnostics are authoring-conditioned.** Every count in that block is
  conditioned on a ballot having been authored as an ejection, so it flatters
  whichever arm authors more. The candidate authored 39 ejections and the
  reference 23, and the precision figures rest on 27 and 15 crew ballots
  respectively — denominators at which neither arm separates from the 0.5 null.
* **The coalition funnel rests on single figures.** One correct coalition on the
  candidate arm and none on the reference. P2's "wrongful falls to or below
  correct" reads as MISSED on this funnel: the wrongful rate rose to 100.0% (8 of
  8) rather than falling, and its order against the correct rate is a tie at the
  ceiling on a correct denominator of one. The reading that survives is the
  narrower one — the gate now converts everything that clears it, on both classes
  and on both arms — and it is a statement about the funnel rather than about F6.
* **Nine ejections and three are small numerators.** The ejection precision rows
  cannot separate 1-of-9 from the 1/3 chance rate (p 0.974), and the reference's
  0-of-3 says nothing at all.
* **Zero truncations in sixty impostor-authored candidate ballot draws bounds the
  rate; it does not prove it is zero.** The Wilson 95% upper bound is 6.02% on
  that denominator.
* **Four of the figures above do not recompute on a clean checkout.** The
  recorded EJECT/SKIP column, the surviving and nulled `primary_reason_id`
  counts, the contradiction flags and the claim vocabulary are read off replays
  the manifest keeps outside version control, so they carry this record's word
  and no in-tree check. They are P4's surviving-id half and the whole of P6.
  "Review corrections" names the clause, separates what does recompute, and
  routes the closing repair — those counters inside `authored_diagnostics` — to
  the sixth authorization's instrument work.
* **The leak detector is a lexical rule** over committed turn text gated on the
  speaker's ground-truth role; `ROLE_LEAK_RULE` states in its own words that the
  count is an estimate carrying error in both directions and is not a floor. Zero
  on both arms bounds the leak loosely rather than measuring it.
* **The role split's prose lengths are over AUTHORED payloads and its truncation
  denominator is DRAWS**, so two numbers in the same row have different
  denominators. The field names say which is which (`draws` against
  `lengths[].samples`).
* **The wave gate cannot read the accounts revision.** It checks that both arms
  resolve `AILIBI_CITATION_RELEVANCE=1` and `AILIBI_PROMPT_SET=qwen3_6_27b`; that
  the candidate's templates are at v5 is pinned by the accounts card's own
  version test and by the prompt-version markers a run records.
* **`CALIBRATED_UNIT_INPUT_TOKENS` and `CALIBRATED_UNIT_OUTPUT_TOKENS` are still
  the second calibration's 38,440 / 4,176**, and every feasibility claim this tree
  makes is against those. The section above says what this sitting's own maxima
  would be and whose card moves them.

## Deviations from the manifest and the dispatch

Three, all recorded rather than silent.

1. **The invocation carried its credential through `uv run --env-file`.** The
   manifest documents `.venv/bin/python -m experiments.fresh_deduction_instrument
   --calibrate --calibration-mode 2026-09-18 ...`; this sitting ran
   `uv run --env-file <a 0600 credential-only file outside the repository> python
   -m experiments.fresh_deduction_instrument --calibrate --calibration-mode
   2026-09-18 ...` with the module, the mode, the provider, the manifest path,
   the runner flag, the output directory and the `--json` path identical. The
   substitution injects `FEATHERLESS_API_KEY` from a file outside version control
   instead of the ambient shell, so the key never reaches a command line, a log
   or a commit; the file was deleted when the sitting finished. It is the same
   substitution the calibrations of 2026-09-14 and 2026-09-15 and the fifth run
   recorded, and nothing about what was drawn, gated or charged differs.
2. **The committed usage profile was not refreshed and neither calibrated
   constant moved.** This is the card's own instruction rather than a runner's
   choice — the card's Constraints assign the refresh and its dependent test to
   the sixth authorization's limits card — and the refreshed profile's numbers are
   reported above so that card has them.
3. **`audits/deduction-candidate/checkpoint.md` gained a dated line** naming this
   sitting, and `audits/deduction-candidate/README.md` a paragraph indexing this
   directory, as the dispatch asked. Both state only what this directory holds.

Nothing else departs from the manifest's documented third calibration. The
`--json` destination — this dated directory — did not exist beforehand and the
invocation made it, as the manifest's command section says it does.

## Review corrections (2026-09-19)

Four findings were raised against this record on the pull request that publishes
it, all four by the repository's automated reviewer and all four valid as
observations. They are dispositioned here, in the record itself, before the
record merges. **No instrument, prompt, manifest, profile or constant byte moves
for any of them, no provider call was made, and the sitting was not re-run** —
this card authorizes exactly one spend and that spend is spent. What moved is
this file, `../README.md`, `../checkpoint.md`, the card, and the
`docs/artifacts.md` `audits/` row that any `audits/` byte change recomputes.

**1. P2 is re-labelled MISSED, and the headline that propagated from it is
corrected.** The prediction the manifest fixed before the sitting is that the
wrongful coalition conversion rate **falls** to or below the correct one. It did
not fall: it rose, 36.4% (8 of 22) to 100.0% (8 of 8), and its order against the
correct rate is a tie at the ceiling on a correct denominator of one. The first
publication called that "held by the letter, on n = 1", which reads the
relative-order clause as the whole prediction and drops the fall the mechanism
claim rests on — F6 was to ATTACK stage 2, and stage 2 converted everything that
reached it, on both classes and on both arms. Calling it held overstated the
sitting and carried a "four held, two did not" summary into `../README.md`,
`../checkpoint.md` and the card. The verdict cell, the tally, the Limitations
bullet and all three of those documents now read **three held (P1, P3, P4) and
three did not (P2, P5, P6)**. The prediction's own text did NOT move: it is
frozen before the sitting in the manifest's "Development calibration 3
(2026-09-18)" section and in the card's Evidence table, a test holds those two
copies to the same six rows, and re-reading a verdict is the only correction a
record may make to a preregistered direction after the fact. Nothing downstream
changes: no decision rule reads P2, none of the six is a gate, and the owner's
reading of the sixth band is made from the six verdicts as they now stand.

**2. P4's surviving-id half and the whole of P6 do NOT recompute from committed
bytes, and that is now stated rather than implied.** AGENTS.md craft rule 5
(`AGENTS.md:68-69`) requires a number to be reproducible from committed evidence
with its command in the record. Four figures here are not: the authored
EJECT/SKIP split's recorded column, the surviving and nulled `primary_reason_id`
counts, the contradiction flags and the claim vocabulary. They are read off the
sitting's replays, and the replays are development data that
[the manifest](../execution-manifest.md)'s "Development calibration 3
(2026-09-18)" section puts outside version control by name — *"Its rendered
prompts are development data and are still not committed: its replays go to the
`--output-dir` the runner names, which is not under version control, and a
per-seed reading of the six predictions is available there and nowhere else"* —
which the card's own aggregates acceptance item restates. That clause is the
authority this record rests on, and it is a deliberate held-out-discipline trade
rather than an oversight: a replay row carries rendered prompts and model-output
prose, which this directory's aggregates-only rule forbids and which
`assert_report_holds_no_prefix_bytes` is run over the payload to prove absent.

What DOES recompute from `calibration.json` is stated so the line is exact.
P4's coercion half recomputes: `authored_diagnostics.guard_rewrites_by_reason`
carries `uncited_coerced` 0 on both arms. P3's authored-EJECT numerator
recomputes: `authored_diagnostics.by_voter_role[].authored` sums to 23 on the
reference and 39 on the candidate, over 180 ballots per arm. So do the coalition
funnel, gate survival by role, crew precision with its harm counter, the ejection
rows, the leak and self-tell columns, and every token, pace and ceiling figure in
this file. P4's "32 of 180 keep a `primary_reason_id`, 0 nulled" and every figure
of P6 do not: the payload carries no citation, contradiction or claim field,
which is why they were derived off the replays in the first place. The verdict
cells and the section header now say so in place.

The repair that closes this is an INSTRUMENT byte — those four counters belong in
`authored_diagnostics` beside the ones it already carries — and a run pull
request may not move an instrument byte. It is routed, with item 3 below, to the
sixth authorization's instrument work, so the next sitting archives them as
aggregates instead of deriving them off a directory that does not survive it. It
cannot be closed retroactively here: the sitting's `--output-dir` no longer
exists, re-deriving the counts needs a second live spend this card does not
authorize, and committing the replays themselves is refused by the
aggregates-only rule above. Until then, P4's surviving-id half and P6 are
readings this record makes that a clean checkout cannot check, and they are
marked as such wherever they appear.

**3. The archived `role_leak_rule` is the live evaluation's string, and two of
its sentences do not fit a no-outcome payload.** It tells the reader that the
leak count is "a reported column beside the primary outcome" and gives "a further
reason to read it beside the outcome rather than to gate on it", while this mode
reports no primary outcome — the same defect the card already repaired for
`AUTHORED_DIAGNOSTICS_NOTE` by giving mode 3 its own note, and not repaired for
this string. It is `ROLE_LEAK_RULE`, an instrument constant, so the fix is a
calibration-specific or outcome-neutral description routed to the sixth
authorization's instrument work beside item 2, and the live evaluation's own text
stays byte-identical because it is what the live run publishes under. Nothing in
this directory is misread meanwhile: both clauses argue the column is NOT a gate,
which is also this mode's position; the count is **0 on both arms**; and there is
no outcome in this payload for a reader to read it beside. It is recorded in the
leak section above as well, so a reader meets the caveat where the number is.

**4. The 11.2% ballot-input rise is re-stated as an observed cross-sitting
difference.** It was published as the wave's bytes landing on the candidate's
input side. A seed holds the scripted prefix constant and not the meeting the
sitting generates, and a ballot prompt renders that generated transcript, so two
sittings at nonzero temperature do not hold the ballot's input text fixed: this
sitting's candidate turn output mean is 476.2 against the 2026-09-15 sitting's
443.0 on the same sixty seeds, and a longer transcript enlarges the ballot prompt
before a template byte is counted. The measured-profile section now says the
figure mixes the v5 templates' static bytes with the growth of the transcript
they produce, that separating the two needs a controlled-transcript measurement
no sitting has made, and that the sizing conclusion does not rest on the split —
the largest charged unit is 34,412 input however the rise is apportioned, and
every ceiling figure is read off that maximum. The comparison section's
"Cross-sitting comparison is on INPUTS" paragraph is corrected the same way: the
wave's bytes are the only CONFIGURED difference between the two sittings, and a
difference between their columns is an observed difference rather than an effect
estimate.
