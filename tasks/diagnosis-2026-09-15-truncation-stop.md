# Why the fourth live run of the fresh-model deduction instrument stopped

Diagnosis of 2026-09-15, written by the coordinator from four independent
read-only investigations, one synthesis and two adversarial refutations of
that synthesis (a third refuter's report was lost to a formatting failure; the
one figure its partial text disputed, the line layout of the candidate
ballots, is corrected in section 8). Every figure below was recomputed by at
least two of those sessions from the fourth run's archive on its pull
request's branch (`work/fresh-deduction-run-4` at `5f2383ea`, PR #458,
unmerged) and from the tree at `10a19df8`; the coordinator re-counted the
citation, template and public-transcript figures independently. The owner
approved every decision in section 6 on 2026-09-15; section 9 records the
rulings and the cards that carry them.

## 1. What stopped the run (facts)

The run stopped at unit 26 of 100 on a BALLOT on `combined_accounts` seed 7016. `STOP_RULE`
gives it no retry and the resumption clause makes it final (`execution-manifest.md:1298-1312`).

| Fact | Value | Source |
| --- | --- | --- |
| Arm, seed, call | `combined_accounts`, 7016, ballot (voter 2 of 3) | `run-2026-09-15/combined_accounts-seed-7016.jsonl` |
| Refused call | 4,734 in, 1,024 out — input BELOW the arm's 5,484 ballot mean | abandoned minus on-row: 18,953-14,219 in, 2,881-1,857 out |
| Cap, and the stop it raised | 1,024; `PerCallCapExceeded` | `fresh_deduction_instrument.py:202,2412`, `meetings/manager.py:212` |
| Parse error | `EOF while parsing a string at line 11 column 3620` | `stop.log`, via `RESULTS.md:184` |
| **Who was voting** | **the fragment opens `{"voter": "p-2"` — p-2 is seed 7016's impostor, who killed p-4 at tick 5** | `RESULTS.md:186`; that replay's tick-5 row `{"actor":"p-2","type":"kill","payload":{"target":"p-4"}}` |

| Arm | Call | n | mean out | max out | cap | max % cap |
| --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | turn | 39 | 271.5 | 423 | 4,096 | 10.3% |
| `repaired_clock` | ballot | 39 | 100.4 | 144 | 1,024 | 14.1% |
| `combined_accounts` | turn | 40 | 917.9 | 1,900 | 4,096 | 46.4% |
| `combined_accounts` | ballot | 37 (+1 refused at 1,024) | 182.3 | 624 | 1,024 | 60.9% |

`rationale_text` is the LAST of the 7 keys in 37 of 37 candidate ballots, 65% of a ballot's
characters on average and 91% at worst. Split by the voter's hidden role, the candidate arm is
two populations, not one:

| Arm | Voter | n | `rationale_text` mean | max | opens with a first-person role confession |
| --- | --- | --- | --- | --- | --- |
| `combined_accounts` | impostor | 12 | 477 | 1,795 | **11 of 12** |
| `combined_accounts` | crew | 24 | 381 | 606 | 0 of 24 |
| `repaired_clock` | impostor | 13 | 95 | 154 | 2 of 13 (one clause each, 44 and 104 chars) |
| `repaired_clock` | crew | 26 | 110 | 203 | 0 of 26 |

## 2. Root cause

**The candidate ballot template commissions deliberation, gives it one unbounded place to land,
and the voter with the most to deliberate about is the impostor.** Two defects share that root.

**(a) The runaway.** `vote_ballot_accounts.j2:10` asks the voter to "Judge who said what,
whether accounts agree and what alternatives remain"; `:21` asks only for "a concise reason";
`:23`'s skeleton ends at `"rationale_text":"<one short reason>"`. The reference template bounds
the same field and warns about the consequence — `vote_ballot.j2:270`: "ONE short sentence (~20
words)" and "a long rationale can overrun the output limit and truncate the JSON, which discards
your vote". Nothing else bounds it: `meetings/schemas.py:766` is a bare `rationale_text: str`
with no `max_length`, and `json_object` constrains syntax only. Decoding is non-thinking
(`enable_thinking=false`, pinned by the model lock, `execution-manifest.md:823`), so there is no
reasoning channel: the deliberation lands in the answer's last key, where an unterminated string
destroys every field before it.

The tail is not arm-wide. A crewmate's deliberation is a case about someone else; the IMPOSTOR's
is a concealment plan, and this model writes it from the private truth forward: 11 of 12
impostor candidate ballots open by naming their own role and kill ("I am the Impostor and killed
p-3. Voting to eject a crewmate would..."), against 0 of 24 crew ballots. The four longest draws
on the arm — the refused one, then 1,795, 633 and 629 characters — are ALL impostor-authored: a
1-in-103 accident under an arm-wide tail (hypergeometric, 13 impostor draws of 38, p=0.0097).

**(b) The citation channel, one-sided.** The same template thinness breaks the arm's
citations. Candidate voters DO cite: 14 of 17 EJECT ballots carry one, 13 in
`primary_reason_observation_id`. But memory lines render as `[obs p-1:5:2] ...`
(`agents/memory/store.py:590`) and 13 of those 14 ids are copied WITH that tag word.
`meetings/manager.py:3242-3244` nulls an id not in the voter's own valid set, with no
suffix recovery by design (`:365-381`), and `manager.py:3780-3798` then coerces the now-uncited
EJECT to SKIP whenever the target carries no contradiction flag: 12 `uncited_coerced` plus 1
`under_gate_redirect` on the candidate, 0 on the reference (`RESULTS.md:359-366`).
`vote_ballot.j2:267` inoculates the reference with a literal example; the candidate's `:21` says
only "a reference copied from YOUR OWN private memory". Reference EJECTs: 5 of 5 validly cited.

| Link | Evidence | Citation |
| --- | --- | --- |
| Same gap upstream | `"reason":"<reason>"` and "explain what it does and does not establish" vs `"<one short phrase>"` and "1-2 short sentences, then stop" | `_account_rules.j2:38-39`, `accusation_round_accounts.j2:16` vs `accusation_round.j2:291,245` |
| Nothing else bounds it | no `max_length` in the schema file; the payload is model/messages/max_tokens/temperature only — no `stop`, `top_p` or penalty, and `finish_reason` is never read | `meetings/schemas.py:766`; `llm/featherless_client.py:654-667` |
| The long text is deliberation | longest: 341 words, 44 sentences, unique-5-gram 0.988, opens "As the Impostor, I know I killed p-1." | seed 7010 p-4 output (p-4 is that game's impostor) |
| It is the impostor's deliberation | impostor mean 477 / max 1,795 vs crew 381 / 606; 11 of 12 confess; top 4 draws all impostor (p=0.0097); the refused draw is the killer | recount; `RESULTS.md:186` |
| Citations are malformed, not absent | 14 of 17 candidate EJECTs cite; 13 of 14 ids carry the `obs ` tag word; nulled, then 12 coerced to SKIP | replays; `manager.py:3242-3244,3780-3798`; `RESULTS.md:359-366` |
| Truncation ends the run, pre-empting the shipped net | at-cap raises `PerCallCapExceeded`, which "replaces the ValidationError the meeting layer fail-softs with a stop it does not, which is the point"; that net degrades a ballot to a marked SKIP as "the cap-truncation runaway class, accepted at ~1/50" | `fresh_deduction_instrument.py:2412,2272-2282`; `meetings/manager.py:2265-2298` |

The repo hit the truncation class before and fixed it on the prompt side:
`tasks/phase-14.md:640-643` records "2 unterminated-JSON vote-cap truncations at the frozen 1024
cap", repaired by a `qwen3_32b` v3 "compact-ballot fix", and `:654` rules "do NOT ... raise the
caps". The accounts family never inherited it — its only commit is its creation, `e12b6180`; the
v3 commits `2bddbde2`, `cd75afaf`, `520d5a9b` never opened the ballot file.
`vote_ballot_accounts.j2` is 23 lines against `vote_ballot.j2`'s 273.

**The rate, on the right denominator.** One truncation in 13 impostor-authored candidate
ballot draws — 7.7%, Wilson 95% CI [1.4%, 33.3%]. Exposure is ~one impostor draw per candidate
unit (13 draws over 13 units), so the expected first stop is candidate unit 13 and the observed
one is candidate unit 13. A 50-pair run draws ~50 impostor ballots: P(clean) = (12/13)^50 =
**1.8%**, not the 7.0% a homogeneous 1-in-57 model gives.

## 3. Why the calibration did not see it

It drew 15 candidate ballots, not 30: the brief's "30 candidate ballots" is 30 candidate CALLS,
15 turns plus 15 ballots.

| Quantity | Calibration | Run 4 | Error |
| --- | --- | --- | --- |
| Candidate ballot mean out | 163.8 | 182.3 | +11.3% |
| Candidate ballot max out | 237 (23% of cap) | 624 resolved, 1,024 refused | +163% / +332% |
| Candidate per-unit output | 3,137.0 | 3,481.5 | +11.0% |
| Reference per-unit output | 1,107.8 | 1,115.7 | +0.7% |
| Per-unit input, both arms | 28,430 / 21,026 | 27,537 / 20,278 | -3.1% / -3.6% |

1. n=15 cannot see it, and the effective n was ~5: only impostor draws are exposed (13 of 38
   ballots, 34%), so it held ~5 exposed draws and 0.4 expected events. Under its own
   nearest-rank rule p95 at n=15 IS the maximum, so 237 was never a bound.
2. Its candidate TURN measurement was censored at 2,036 of the then-current 2,048 cap. The
   fourth authorization read that near-miss correctly and raised the turn cap to 4,096
   (`fresh_deduction_instrument.py:194-199`) but read the ballot near-miss as distance, not
   as an unsampled tail (`execution-manifest.md:824`): same shape, opposite treatment.
3. It was accurate about means, and means were never the risk (`STOP_RULE` is a per-call
   maximum condition); and it measured tokens, not content, so nothing in it would have
   shown that the arm's ballots confess a hidden role or that its citations were malformed.

## 4. Alternatives considered and rejected

| Alternative | Why rejected |
| --- | --- |
| Prompt size, not the instruction set | The refused call's input was 4,734 against a 5,484 mean; ballot input to output correlates at r=0.28 and prompt tokens to rationale characters at r=0.23; the candidate's base first-turn prompt is the SMALLER of the two (8,030 vs 10,308 characters) |
| Degenerate decoding, a repetition loop | Unique-5-gram ratio 0.988 on the longest rationale and 1.000 on the next two, largest repeated 5-gram 3; the text is coherent planning that ends on a stated vote |
| A formatting mode departure | Corrects an earlier lens that read all 75 responses as single-line compact JSON. Candidate ballots average 10.1 newlines and `rationale_text` is the last key in all 37; "line 11 column 3620" is the NORMAL `rationale_text` line of a 12-line object (19 of 36; with one alternative line 10, with none line 8 — section 8). The departure is LENGTH: ~3,598 chars against a resolved mean of 411, max 1,795 |
| The ordinary tail, so raise the cap | Rejected, and the refutation strengthened it. Three lognormal fits put 3,620 chars 5.3-5.9 sigma out and a Hill/Pareto refit (alpha 3.45) expects 0.01 such events in 38 draws. A tail no tail model can produce is a SECOND MODE — section 2's. A larger cap relocates that mode's boundary rather than closing it and pays for it by widening a preregistered limit; at 2,048 the same runaway gives a 2,048-token ballot and the same dead parse |
| A model-quality problem | The same model on the same wire config produced 39 reference ballots with a 203-character, 144-token maximum — 13 of them impostor-authored |
| A Featherless-side decoding constraint | Unavailable today: `llm/featherless_client.py:18-46` records the owner-ratified finding that strict `json_schema` is deterministically rejected on this slate |
| Route the truncation into the meeting layer's fail-soft | Rejected as a default: it reverses the owner's own round-1 repair (`execution-manifest.md:125-135`, review #447 on 2026-09-10, `6215fda1`, closed "a response that reached its output cap ... was fail-softed to a SKIP"). Also `DefaultedCall.trigger` is only `deadline` or `validation`, so a truncation lands indistinguishable from a schema failure, and `execution-manifest.md:1048-1056` warns a defaulted SKIP "biases the primary outcome UPWARD", asymmetrically on the truncating arm. Owner decision, not a fix |

## 5. Fix plan, smallest change first

No grader reads rationale prose (`fresh_deduction_instrument.py:556-565`), so A and C are
measurement-neutral in intent. B is NOT: it repairs a one-sided defect that is suppressing the
candidate's ejections today, and the revision card must say so.

**A. Port the reference bound into the candidate ballot template.** Smallest. Add
`vote_ballot.j2:270`'s two sentences — the "~20 words" budget and the truncation warning — to
`vote_ballot_accounts.j2:21`. One `.j2` file, but it requires a new accounts revision (v4) in
`agents/strategic/prompts/loader.py`, a new arm-surface digest, a manifest prompt-set section,
its prompt-version test pin and a fresh calibration. Alters no primary outcome, decision rule,
tradeoff bound or stop rule; it does change the candidate's measured surface, so run 4's 24
units cannot be pooled with what follows. **Honest limit:** a budget bounds the symptom, not the
channel — non-thinking decoding is pinned by the model lock, so deliberation still has nowhere
to go but the answer; the reference arm shows a bound holds it to ~100 characters rather than
removing it.

**B. Give the candidate the citation-ID example** (replacing the earlier "name the destination
field"). Copy `vote_ballot.j2:267`'s form — `"primary_reason_observation_id":
"{{voter_id}}:12:0"`, the id WITHOUT the `obs ` tag word —
into `vote_ballot_accounts.j2:21,23` and pre-fill the skeleton. Same files and gates as A; do
both in one revision. **Cost, and it is not a nudge:** 13 of 17 candidate EJECT citations are
nulled today and 12 ballots coerced to SKIP, so supplying the format flips those coerced SKIPs
into live ejections ON THE TREATMENT ARM ONLY — a change in the arm's ejection RATE, precisely
the failure `WRONGFUL_EJECTION_TRADEOFF` polices (`fresh_deduction_instrument.py:591-605`). Name
it in the revision card and read the wrongful-ejection bound against it next run. Do NOT aim
deliberation at `considered_alternatives`: it is `tuple[PlayerId, ...]`
(`meetings/schemas.py:765`) and the arm already puts 7 non-id prose items (to 108 chars) there
against the reference's 0.

**C. Bound the upstream turn — a validity repair, not just headroom.**
`_account_rules.j2:38-39` to `"reason":"<one short phrase>"`; soften
`accusation_round_accounts.j2:16`. It removes the 876-character register the ballot prompt
echoes AND addresses a leak this memo previously missed: in 2 of 13 candidate games the impostor
commits its own role and kill into the COMMITTED PUBLIC TRANSCRIPT ("since I am the impostor, I
know I killed p-3 at tick 5", `headless-seed-7003:meeting-0:turn-1`; same shape at seed 7009
turn-1), against 0 of 39 reference turns. `_account_rules.j2:43` ALREADY forbids it ("Never put
a private role, teammate identity or a bookkeeping score in public speech"), so a prohibition
alone does not hold in this register — the length bound is the lever with evidence behind it. A
leak hands the crew a free correct ejection on the treatment arm.

**D. Record `finish_reason`.** `llm/featherless_client.py:827-858` reads only
`choices[0].message` and `usage`, so truncation is INFERRED from `output_tokens >= max_tokens`;
no `finish_reason` string exists anywhere in `llm/`. Touches the client, its response model and
`tests/llm/`; no preregistered constant, and the client is NOT in `ARM_SURFACE_SOURCES`
(`:4296-4304`), so it is digest-neutral. Do it anyway.

**E. Bound `rationale_text` in the schema.** A `max_length` at `meetings/schemas.py:766` makes a
runaway a BELOW-cap `ValidationError` that `meetings/manager.py:2265` already records as a
defaulted vote: counted, not fatal. Costs: it changes shipped behaviour for every campaign,
inherits the upward bias at `execution-manifest.md:1048-1056`, and — unlike D — schemas.py IS in
`ARM_SURFACE_SOURCES`, so it moves the digest on BOTH arms.

**F. Re-size the vote cap.** `AUTHORIZED_VOTE_MAX_TOKENS` is an alias of
`DEFAULT_VOTE_MAX_TOKENS` (`:202`) and must first become a literal; then
`unit_output_reservation`, `3 x (turn + vote)` (`:502-518`), moves.
`AUTHORIZED_UNIT_MAX_OUTPUT_TOKENS` is preregistered, and raising it is a widening only a new
authorization card can make (`STOP_RULE` forbids the run from doing it).

| vote cap | reservation | vs ceiling 16,000 | verdict |
| --- | --- | --- | --- |
| 1,024 (today) | 15,360 | fits | feasible |
| 2,048 | 18,432 | over | `LimitsInfeasible`; needs >= 18,432 |
| 4,096 | 24,576 | over | needs >= 24,576 |
| 2,048 with turn 3,072 | 15,360 | fits | feasible, cuts turn headroom |

## 6. Owner decisions

1. **Revise the accounts ballot template to v4 (A + B)?** Yes. Cost: a new revision, digest and
   calibration; run 4's 24 units are not poolable; and B moves the candidate's ejection rate
   one-sidedly — the card must declare it, read against `WRONGFUL_EJECTION_TRADEOFF`.
2. **Include the turn bound (C)?** Yes, on validity grounds and not headroom alone: it is the
   only proposed lever against the public-transcript role leak. Cost: nothing extra given 1.
3. **Record `finish_reason` (D)?** Yes, independent of 1. Cost: one client change plus
   tests, digest-neutral. It makes the stop's central fact observed, not inferred.
4. **Bound `rationale_text` in the schema (E)?** No for now. Cost of yes: shipped behaviour
   changes everywhere, defaulted SKIPs bias the outcome upward, and the digest moves on both
   arms. Revisit if a v4 calibration still shows the impostor mode.
5. **Raise the vote cap (F)?** No. Cost of yes: a literal, a widened per-unit ceiling of at
   least 18,432, a new authorization card — and it still does not close the behaviour.
6. **Make a cap-truncation a counted default, not a stop?** No. Cost of yes: it reverses the
   2026-09-10 review repair, needs a new `trigger` word plus classifier and counter changes,
   and biases the outcome upward on one arm.
7. **Minimum candidate ballots in the next calibration?** The bar is IMPOSTOR draws: at least
   60 impostor-authored candidate ballots (P(seeing a 1-in-13 event) = 99.2%), ~60 development
   units, with `finish_reason` recorded and role-split reporting. Cost: ~4x the 2026-09-14
   candidate volume, at $0 marginal.
8. **Freeze a new held-out band?** Yes. Thirteen of band 7000-7999's seeds are now public and
   `RESULTS.md:600-609` says a re-run is not a clean sample. Cost: a band frozen by a
   preparer who has not read this run.
9. **NEW — does the public-transcript role leak block the next run on its own?** Owner call.
   It is a measured, one-sided validity threat (2 of 13 candidate games, 0 of 13 reference)
   that C only mitigates. If no, the next card should pre-declare a leak count as a reported
   diagnostic so the primary outcome can be read against it.

## 7. What this run DID establish

**The margins.** Every ceiling except the vote cap had large headroom.

| Limit | Authorized | Actual | Used |
| --- | --- | --- | --- |
| Run input / output | 3,710,000 / 459,000 | 612,588 / 58,986 | 16.51% / 12.85% |
| Per-unit input / output | 106,000 / 16,000 | 36,743 / 4,816 | 34.7% / 30.1% |
| Elapsed wall / model work | 28,800 s / 21,600 s | 1,886.3 s / 1,884.6 s | 6.55% / 8.73% |
| Turn cap | 4,096 | 1,900 | 46.4% |
| **Vote cap** | **1,024** | **1,024** | **100%, the stop** |

**The calibration's accuracy.** Means accurate, maxima unbounded: a mean-accurate
calibration is not a maximum-accurate one, and a token-only one is neither content- nor
role-aware.

**The rate.** 1 truncation in 13 impostor-authored candidate ballot draws (7.7%, Wilson CI [1.4%,
33.3%]); arm-wide 1 in 38 drawn ballots, but that figure predicts the wrong unit. P(a clean
50-pair run) = 1.8%. **A complete 100-unit run is not reachable at this rate. That is the finding.**

**The primary outcome — corrected.** Both arms scored 0 of 12 on
`supported_correct_ejection`, b=0 and c=0, but that is NOT "nothing either way": the candidate
arm could not score. Its one ejection, seed 7015, ejected `p-4`, whose hidden role IS impostor,
and failed only because both ballots naming p-4 cited `"obs p-1:5:2"` and `"obs p-2:1:2"`, which
the meeting layer nulled for the tag word — leaving them uncited and pinning
`every_citation_relevant` false (`fresh_deduction_instrument.py:3868-3878`;
`RESULTS.md:340-350`). b=0/c=0 is an artifact of a one-sided instrument defect on the treatment
arm, not a null result about deduction. Two side facts: the candidate arm produced the only 2
defaulted turns and all 13 guard-rewritten ballots, the reference zero of each.

## 8. Refutations considered

Accepted, and where the memo changed.

| Objection | Verdict | Evidence |
| --- | --- | --- |
| The mechanism is role-conditioned, not an arm-wide tail | **Accepted**; section 2 rewritten | 11 of 12 impostor candidate ballots confess (0 of 24 crew); impostor mean 477 / max 1,795 vs crew 381 / 606; top 4 draws all impostor, p=0.0097; the refused draw is seed 7016's killer (`RESULTS.md:186`, tick-5 kill row) |
| "1 draw in 57" is the wrong denominator | **Accepted**; now 1 in 13 impostor draws | exposure ~1 per unit; expected first stop unit 13, observed 13; P(50 pairs clean) 1.8%, not 7.0% |
| "36 of 37 are 12-line with `rationale_text` on line 11" | **Accepted as an error** | 19 of 36 recorded ballots are (line 11 of 12); 14 are (10 of 11), 2 are (8 of 9), 1 is single-line. The durable fact is that it is the LAST key in 37 of 37 |
| "It displaces the citation" | **Accepted as an error**; the link is replaced | 14 of 17 candidate EJECTs carry a citation and the 3 uncited ones are LONGER (439 vs 405 chars), not shorter. The defect is the `obs ` prefix, not prose crowding |
| The citation channel is broken one-sidedly and fix B must own that cost | **Accepted**; B rewritten, decision 1 and section 7 corrected | 13 of 14 candidate ids malformed, 0 of 3 reference; `manager.py:3242-3244,3780-3798`; 12 `uncited_coerced` vs 0 (`RESULTS.md:359-366`); seed 7015 lost the arm's only scoreable ejection to it |
| `considered_alternatives` content DOES grow, so B must not aim prose there | **Accepted**, with a corrected count: 7 items, not 4 | 7 non-id items up to 108 chars on the candidate, 0 on the reference; the field is `tuple[PlayerId, ...]` (`schemas.py:765`) |
| The role leak reaches the committed public transcript and the memo never named it | **Accepted**; C reframed, decision 9 added | 2 of 13 candidate games (seeds 7003 and 7009, turn-1), 0 of 39 reference turns |
| E's cost list omits the arm-surface digest | **Accepted** | `meetings/schemas.py` is in `ARM_SURFACE_SOURCES` (`fresh_deduction_instrument.py:4296-4304`); `llm/featherless_client.py` is not, so D stays digest-neutral |

Rejected, with the evidence that rejects them.

| Objection | Why rejected |
| --- | --- |
| "12 of 12 impostor ballots open with a confession" | 11 of 12. Seed 7015's impostor p-4 accuses p-1 with no self-tell — the one impostor draw that deflects instead of confessing. Direction unchanged, figure corrected |
| "Reference 1 of 13" | 2 of 13 (`repaired_clock` seeds 7003 and 7014: "I killed p-3 myself", "I did it."). The contrast is 11/12 vs 2/13, and the reference's are one clause long — which is the point: the bound holds the same impulse to ~100 characters rather than removing it |
| ">= 2 of 13 games leak to the transcript", as an open lower bound | Exactly 2. Seed 7015's turn-1 match is the impostor REBUTTING an accusation ("p-1's claim that I am the impostor ... is weak"), not a self-tell; counted out |
| "Fix A is neither sufficient nor first" | Half accepted, half rejected. A is not sufficient — section 5 now says so in its own words. But A stays first: it is the only change that acts on the stop itself, and B and C ride in the same revision, so the ordering costs nothing |
| "The arm-wide 1-in-38 rate should be dropped" | Kept as a reported figure in section 7: it is the true rate per drawn ballot. What was wrong was using it to predict a UNIT, which the role-split model now does |

## 9. Rulings (2026-09-15)

The owner approved the decisions of section 6 as a set on 2026-09-15, in the
coordinator's session. Decision 9 was put without a recommendation; approving
the set is read as the reading under which the next run proceeds: the leak
does not block it on its own, and the next cards pre-declare a per-arm leak
count as a reported diagnostic.

| Decision | Ruling | Carried by |
| --- | --- | --- |
| 1. Revise the accounts ballot template to v4 (A + B) | approved | [the v4 accounts card](work/accounts-prompt-set-v4.md) |
| 2. Include the turn bound (C) | approved | the same card |
| 3. Record `finish_reason` (D) | approved | [the finish-reason card](work/featherless-finish-reason.md) |
| 4. Bound `rationale_text` in the schema (E) | no for now | none; revisit if the second calibration still shows the impostor mode |
| 5. Raise the vote cap (F) | no | none |
| 6. A cap-truncation as a counted default in the live run | no | none; the live stop rule is unchanged. The second calibration counts a truncation as a measurement, because a calibration that stops at the first runaway cannot measure its rate, and that is a calibration rule, not the run's |
| 7. At least 60 impostor-authored candidate ballots, role-split, with `finish_reason` recorded | approved | [the second calibration card](work/fresh-deduction-calibration-2.md) |
| 8. Freeze a new held-out band | approved | [the fifth freeze card](work/held-out-prefix-freeze-5.md) |
| 9. The public-transcript role leak | not blocking on its own; pre-declared as a reported per-arm diagnostic | the second calibration card adds the detector and the manifest pre-declaration; the fifth run reads it |

The fifth authorization is opened after the second calibration reports, as
the fourth was after the first. It carries the ceilings re-sized on the new
profile with the in-flight headroom term the feasibility gate now applies
(the open item of 2026-09-14: 459,000 equals 100 times the calibration's
largest unit and clears the gate only on the older committed profile), the
refreshed usage profile, and the leak diagnostic as a reported column. The
fourth run's record stays on PR #458 for the owner; its card on `main` stays
`active` until the owner merges or closes that pull request.
