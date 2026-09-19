# Process over outcome: where AiLibi stands and where it goes next

Direction memo of 2026-09-19. The owner restated the project's goal on that
day: an agent's vote or skip must rest on data the agent actually holds, true
or false, and a wrong decision on believable data is better than a right one
on none. The coordinator answered with a read-only deep dive: five
independent investigations over the committed recordings, the fifth run's
archive and the code, one synthesis, three adversarial critics, and a
revision that moved the verdict. The coordinator then re-checked the six
code claims the conclusions lean on hardest in the tree at `989c7c17`. The
owner accepted all eight decisions of section 10 on 2026-09-19; section 12
records the rulings and the cards that carry them.

Revision note from the memo as it left the critics:

Read-only synthesis at `989c7c17`. Five investigators, then three critics who attacked rev. 1. Where they
disagreed I re-measured from committed bytes. Every number marked MEASURED is mine, recomputed this pass.
No provider calls, no held-out generation.

**What changed in this revision.** Three things in rev. 1 were wrong: the showcase example was not a lie
caught but a schema artifact (§5); the deception table was inflated by a bad ground-truth model (§5); two
code claims were false (§3, §5). One finding was missing and is now the centre of the document: the agent
mostly does not weigh evidence — an arithmetic aggregator does, and the agent is handed its answer (§4).
§11 records what I rejected.

## 1. The owner's goal, restated as testable properties

| # | Property | Testable as |
|---|---|---|
| P1 | No invented facts | Every factual claim in a rationale traces to the voter's own inputs or the public transcript |
| P2 | Every decision names its basis | Every ballot, EJECT and SKIP, carries a citation that resolves |
| P3 | The basis is about the target | The cited line concerns the player voted for |
| P4 | The agent's call is the recorded call | No layer re-aims or deletes a ballot the agent authored |
| P5 | The data is worth following | Truth and lies are distinguishable in principle |
| P6 | **The agent does the weighing** | The choice is a function of the evidence the agent read, not of a number the engine computed for it |

P6 is new in this revision. It is the property your question is actually about, and the one the project
scores worst on.

## 2. Is this the path we are on?

Partly. The plumbing is on it. The measurement program has been off it for weeks, and the decision interface was never on it.

**What served the goal.** Phases 13-21 built what P1-P4 need: typed observations with stable ids, a ballot
citation channel (`meetings/schemas.py:751-774`), four contradiction detectors, testimony landing in
listeners' beliefs as content (`agents/memory/store.py:751`). That last one closes the 2026-06-25 "social
info is a scalar" diagnosis; a critic tried to reopen it and could not. This part is real.

**What served a different goal.** The last weeks went into a held-out evaluation whose primary outcome is
`supported_correct_ejection` (`experiments/fresh_deduction_instrument.py:764-771`): 1 only when the
ejection is role-correct AND supported AND relevant. Your preferred case — a wrong call on good evidence —
scores 0, the same as a meeting where nobody reasoned. The decision rule and tradeoff bound (`:780-790`,
`:796-811`) are both counts of who got ejected.

**The arena is stacked three ways.** The generator keeps a prefix only when no living crewmate holds a
witnessed kill or vent (`experiments/held_out_prefixes.py:21-25`) — and the vent flag is the *only* channel
that reliably works (§3). MEASURED: all 100 fifth-run meetings recorded exactly **3 ballots**, against a
3-to-8 spread in the shipped corpus, so the impostor held a third of every table the evaluation measured.
And the candidate prompts are a poorer substrate than the default:

| | reference (`repaired_clock`) | candidate (`combined_accounts`) | shipped default 9p2i |
|---|---|---|---|
| meetings | 50 | 50 | 439 |
| alibi claims spoken | 33 | **0** | 705 |
| corroboration claims | 13 | **0** | 1,039 |
| contradiction flags | 14 | **1** | 449 |

Zero alibi claims means zero alibi contradictions, so no lie in that arm can be caught. The experiment
removed the mechanism it was trying to measure.

## 3. How grounded are decisions today?

Citation coverage, ballot by ballot over committed JSONL. Reproduced independently three times this pass,
agreeing to the digit:

| corpus | EJECT | EJECT cited | SKIP | SKIP cited |
|---|---|---|---|---|
| `replays/ml_corpus/9p2i` | 1,499 | 1,498 (99.9%) | 1,017 | **0 (0%)** |
| `replays/samples/9p2i` | 527 | 526 (99.8%) | 342 | **0 (0%)** |
| `replays/samples/4p1i` | 51 | 51 (100%) | 66 | **0 (0%)** |
| fifth run, candidate | 75 recorded | 73 | 75 | **0** |
| fifth run, reference | 14 | 14 | 136 | **0** |

P2 holds on EJECT and is absolutely absent on SKIP. Rev. 1 blamed a missing early return; that was half the
story. The SKIP is **uncited by instruction** — `agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:268`
tells the voter "a SKIP needs neither" reason id, and `:259` says the same in prose. It is a prompt fix first.

Rev. 1 also called SKIP "no data link". Too strong. MEASURED: `considered_alternatives` is non-empty on
**1,336 of 1,359** shipped SKIPs (98.3%), and 721 (53%) name a player in prose. The true statement is that a
SKIP carries no *machine-checkable* basis — and the one structured field it does carry has no consumer
anywhere in the product (§4).

**What the citation points at** (ml_corpus, 1,307 EJECT ballots citing a turn): a first-hand observation
naming the target 1,126 (86%); the target's own turn 94 (7%); only an accusation against the target 47 (4%);
nothing about the target 40 (3%). A further 442 cite the voter's own observation id. P3 holds at about 93%.

**Ejection accuracy by evidence band** (MEASURED, ml_corpus, 281 ejections; roles from the engine's own
secret-team block, not reconstructed):

| band | ejections | role-correct |
|---|---|---|
| vent sighting flag on the ejected player | 220 | 220 (100%) |
| other contradiction flag | 3 | 0 |
| no flag | 58 | 32 (55.2%) |

On `samples/9p2i`: vent flag 68/68, no flag 13/20. Combined, **288 vent-flagged ejections, 288 role-correct.**
The no-flag band at ~56% sits above a ~0.25-0.30 chance baseline, so something real survives without a vent —
but one channel does essentially all the reliable work, and it is the channel the held-out band filters out.

**P1 holds.** Two investigators independently graded all 300 fifth-run rationales for invented facts and found
0 and 3 out of ~190-300 checkable assertions. I did not re-test this and neither did the critics: treat it as
two-method agreement, not my measurement.

**P4 is violated at a low rate, and rev. 1 overstated the harm.** `guard_ballot_target_graph`
(`meetings/manager.py:3690-3736`) replaces an under-gate target with the suspicion argmax and prepends a
marker. MEASURED: 57 of 2,516 ml_corpus ballots, 23 of 869 sample ballots — 2.4%; reverting all of them changes
the plurality in 17 of 590 meetings. Rev. 1 claimed "the marker renders inside the agent's voice in the UI."
**False.** `api/replay_loader.py:3665-3694` strips every marker into `rewrite_reasons`; `BallotCard.tsx:16`
renders only `rationale_text_clean`; `:134-146` shows a "Vote redirected by the meeting rule" chip and
`:155-157` prints a plain-language disclosure. Rev. 1's card 5 is largely shipped.

## 4. What the agent actually weighs — the finding rev. 1 missed

MEASURED on `replays/ml_corpus/9p2i`: I parsed the rendered suspicion graph and the valid-target list out of
every ballot prompt and compared each crew EJECT to that voter's own suspicion argmax. 1,270 ballots had an
unambiguous argmax.

| | ballots | role-correct |
|---|---|---|
| target **equals** the voter's suspicion argmax | 1,189 (93.6%) | 1,137 (**95.6%**) |
| target **differs** from it | 81 (6.4%) | 7 (**8.6%**) |

Chance, measured as the living-impostor share of each voter's valid targets: **0.303**. So when the agent
departs from the arithmetic it is not merely worse — it is far *below* chance. In meetings where the engine
minted no contradiction at all, followers score 170/206 (82.5%) and deviators **1/64 (1.6%)**.

**All 81 deviating ballots carry a valid citation.** That is the whole problem with the metric rev. 1 proposed.
"Grounded = cited and on-target" scores the 1.6%-accurate ballots exactly like the 95.6%-accurate ones. It
cannot tell weighing from prose written beside a citation.

Three reasons the agent is not doing the weighing:

1. **It is told not to.** `vote_ballot.j2:259`: the suspicion levels are "your own accumulated evidence ...
   trust them over meeting rhetoric."
2. **The weighing already happened, in Python.** `agents/memory/beliefs.py:454` `graduated_spread_delta`
   weights testimony by independent-voice count and `:1374` `apply_meeting_evidence_rules` folds it
   **pre-vote**, so the number the voter reads already contains this meeting's speech. The rendered row says
   so: "built from: this meeting +0.23, carried prior +0.00".
3. **There is no channel to weigh with.** One citation slot (`meetings/schemas.py:770-774`) — no field for the
   strongest thing pointing the other way. `considered_alternatives` is populated on 98.3% of SKIPs, sits in
   the API type (`frontend/src/types/api.ts:383`), and is read by **no component**. Source credibility does not
   exist: `beliefs.py:953 adjust_trust` has only test callers, and MEASURED, the rendered trust column was
   `0.50` in **5,918 of 5,918** rows — a dead constant displayed as data.

I do **not** read the 93.6% agreement by itself as proof the agent is a rubber stamp; a faithful summary of the
same evidence *should* correlate with a good decision. What is damning is the deviation column: where the
agent's judgement is visibly its own, it is anti-predictive.

## 5. Truth, lies, and the alibi envelope

I rebuilt ground truth from the **engine's own rendered per-agent route** ("Your route (t = tick): CAFETERIA t0
-> EAST_HALL t1 -> ..."), which needs no phase model at all. Corrected (`ml_corpus/9p2i`):

| channel | crew false | impostor false | rev. 1 said |
|---|---|---|---|
| own whereabouts | 19 / 1,920 (1.0%) | **4 / 294 (1.4%)** | 19.8% impostor |
| sighting of another player | 170 / 2,273 (7.5%) | **12 / 408 (2.9%)** | 9.4% / 6.6% |
| self-alibi claim | 43 / 599 (7.2%) | 25 / 97 (**25.8%**) | 7.1% / 36.1% |

The crew numerators match rev. 1 almost exactly, which tells you the old impostor figures came from counting a
*true* room stated at a vent or kill tick as a lie. The sighting channel's sign flips: the impostor is **more**
accurate about other players than the crew is. Rev. 1's movement-destination cell does not reproduce under any
tick convention I tried; I dropped it rather than publish a number I cannot pin.

One real tell survives, at about **3.5x**: across both 9p2i corpora, 38 of 134 impostor self-alibis (28.4%) are
false versus 66 of 821 crew (8.0%). Evidence, not proof. That is the right shape.

**But almost none of them are lies.** MEASURED over all 955 self-alibi claims in the shipped corpora: 103 of the
104 false ones are **multi-tick span claims**; 75 of those are true at the span's first tick; and under a strict
test — was the speaker in that room at *no* tick the claim covers — exactly **2 of 955** are false. The alibi
schema carries one room and a tick range, so a player who walks through four rooms and truthfully says so is
compressed into a single-room envelope, and the envelope then contradicts the truth.

**Seed 41 is that failure, and rev. 1 made it the showcase.** In `replays/samples/9p2i/replay-seed-41.jsonl`
meeting 2, p-9 (crew) makes an alibi claim of `{room: ENGINEERING, ticks 12-15}` whose own evidence strings read
`moved to EAST_HALL @ tick 13`, `ADMIN @ tick 14`, `WEST_HALL @ tick 15` — every one **true** against the
engine's route for p-9. The listeners' render drops the evidence and shows the envelope alone:

> `- alibi: p-9 in ENGINEERING, ticks 12-15.`

The detectors mint five flags, four against p-9, three tagged `[weak signal: ...]`, one comparing p-9's claim to
p-9's *own* whereabouts line in the same turn. Four voters convict:

> "I personally observed p-9 in Admin at tick 14, which directly refutes their claim of remaining in Engineering."

p-9 is ejected. p-9 is innocent, told the truth, and itemised it. The impostor voted along with the crowd. By
this memo's own §7 rule that is **UNGROUNDED** — the "contradiction" is not something the target said, it is
something the schema said for them. It is exactly the case you named: the right-looking process on invalid data.
It belongs in the plan as a defect, not in the demo as an exhibit.

**The reporter pathology is an instrument artifact**, and rev. 1's explanation of it was also wrong. MEASURED: of
281 shipped ejections, 23 (8%) removed the reporter. Rev. 1 said reporter-exculpation lives "only inside the
numeric graph, never in the reasoning surface." **False.** `vote_ballot.j2:245-248` renders a plain-language "Who
reported the body" block, the resolver is unconditional (`meetings/manager.py:2867`), and the block appeared in
548 of 590 shipped meetings. The reporter problem belongs to the 4-player slice, where three voters share one
legal target.

**One real world-model gap stands.** The impostor is never the reporter: MEASURED 0 of 407 report meetings in
ml_corpus, 0 of 141 in samples. And `BodyState` carries no kill tick (`engine/entities.py:43-50`), so "at the
body" and "at the kill" are one observable.

## 6. Does the architecture need reconstruction?

| property | status | where |
|---|---|---|
| P1 no invented facts | **holds empirically** | nothing checks rationale against citation |
| P2 EJECT names its basis | **enforced** | `meetings/manager.py:3839-3878` |
| P2 SKIP names its basis | **absent by instruction** | `vote_ballot.j2:268` |
| P3 basis is about the target | **only when a lever is on** | `citation_relevance_version`, default None |
| P4 agent's call is recorded | **violated at 2.4%**, honestly disclosed in the UI | `:3690-3736`; `BallotCard.tsx:134-157` |
| P5 data worth following | **present but thin**; absent on the held-out band | §5 |
| **P6 the agent does the weighing** | **largely absent** | §4: argmax 93.6%, deviations 8.6% correct |
| weighing has a channel | **absent** | one citation slot; `considered_alternatives` unread |
| source credibility | **dead code** | `beliefs.py:953`; trust 0.50 in 5,918/5,918 rows |
| claim shape fits a moving player | **broken** | 103/104 false alibis are span artifacts |

**Verdict: no rebuild — but rev. 1's "a missing early return and a metric" was too small.** The world model,
typed-observation substrate, citation channel, detectors and testimony-as-content are built and measurably
working; three critics failed to break that. What needs real work is the **decision interface**: the agent is
handed a pre-computed verdict and one slot in which to justify it, over a claim schema that misrepresents a
moving player. Fixing that is a claim-shape change, a prompt change, a second citation field and a live
credibility signal — several hundred lines and one re-record. One substrate wave, not a reconstruction.

## 7. How it should work

**A decision record.** Every ballot, EJECT and SKIP alike, carries: `target`; a citation resolving in the voter's
own inputs; a `counter_reason_id` naming the strongest thing pointing the other way, or an explicit "none held";
a rationale whose assertions trace to those citations; and a `grounding_label` written by the meeting layer,
never the model.

**A claim shape that can be honest.** An alibi is a *route*: an ordered list of (room, tick-span) segments, or one
segment when the player truly did not move. Detectors compare routes to sightings; the render shows the route the
speaker actually gave. A truthful moving player stops generating fake contradictions.

**A weighing the agent can do.** Render the evidence rows the suspicion number was built from, not the number's
conclusion. Drop the "trust them over meeting rhetoric" instruction. Give trust a live signal — a speaker caught
in a real contradiction should be discounted by later listeners — or delete the column rather than display a
constant.

**What the meeting layer enforces.** Citation presence and target-relevance, on SKIP as well as EJECT; relevance
becomes the default, not a lever. The layer labels; it never rewrites.

**What stays free.** Which evidence to believe, how much a contradiction weighs, whether to abstain, whom to
trust. Nothing pushes the agent toward the correct answer.

**Wrong-but-believable versus ungrounded** becomes mechanical. Wrong-but-believable = role-incorrect,
`grounding_label == supported`, and the cited line is factually true of the target or is a genuine contradiction
in what the target *said*. Ungrounded = label not `supported`, a SKIP naming no player, a rationale asserting what
no input contains, **or a contradiction the claim schema manufactured** (seed 41). The first is the game working;
the rest are bugs.

## 8. The yardstick

| metric | direction |
|---|---|
| grounded-decision rate (EJECT and SKIP, cited + on-target) | up |
| **argmax-independence: share of EJECTs departing from the suspicion argmax, and their accuracy** | reported; deviations should be **at least as accurate** as follows |
| **manufactured-contradiction rate: flags whose basis is a span envelope the speaker's own evidence refutes** | down, toward 0 |
| unexplained-decision rate (no citation, or names no player) | down |
| evidence quality mix (vent flag / contradiction / sighting / hearsay) | reported |
| rationale faithfulness (assertions traceable to inputs) | up, near 1.0 |
| agent-authored share (no guard rewrite) | up |
| wrong-but-believable rate | reported, not penalised |
| role-correct ejection rate | reported beside, never a gate |

All nine are derivable today from committed bytes with zero model calls. Rows 2 and 3 are new and are the point of
this revision: without row 2 the headline metric certifies a scalar-driven pipeline as process-grounded; without
row 3 it certifies seed 41 as good reasoning.

**The fifth run re-scored:** reference 14/150 grounded decisions (9%), candidate 73/150 (49%), against
`supported_correct_ejection` 0 and 2. The frozen rule calls the reference arm safer; the process rule says it
declined to decide 136 times with no recorded reason. Neither arm is adoptable — the candidate reasons more, in a
3-ballot arena where reasoning cannot pay.

## 9. The plan to a solid, showable state

**v1 changes no behaviour, makes no model call, and invalidates no bytes** — the demo can go out on the corpus that
exists today. About a day.

| # | v1 card | Size |
|---|---|---|
| 1 | Publish the process scorecard over committed replays, including the two new §8 rows. Most of it exists in `eval/`: `meeting_quality.compute_ballot_target_redirects` / `decompose_ejection_channels`, `alibi_fabrication`, `reporter_justice`, `deduction_metrics._authored_target`. | S |
| 2 | Reorder `FEATURED_GAMES` (`frontend/src/components/ReplayPicker.tsx:94`). MEASURED: 49 of 50 committed `samples/9p2i` games carry ≥1 flag and ≥1 ejection; the tour opens on seed 2, the one that carries neither. One line. | S |
| 3 | Render `considered_alternatives` on the ballot card — in the API type, in no component, populated on 98.3% of SKIPs. The nearest thing to a weighing record already on disk. | S |

**v2 — one coupled substrate wave, then ONE re-record.** About a week plus 4h wall, $0.

| # | v2 card | Size | Why |
|---|---|---|---|
| 4 | **Alibi as a route, not a single-room envelope** | M | Highest-value process fix here. 103 of 104 false alibis are envelope artifacts; 2 of 955 claims are flat lies. Today the detectors manufacture evidence against honest movers. |
| 5 | Ground the SKIP: one prompt clause (`vote_ballot.j2:268`) plus extending `guard_ballot_citation` past `manager.py:3839` | S/M | 40% of shipped decisions carry no machine-checkable basis. |
| 6 | Something to weigh with: second citation slot + `counter_reason_id`; drop the deference line; render the evidence rows behind the suspicion number | M | Delivers P6. Without it the scorecard measures prose. |
| 7 | Trust: wire a live credibility signal, or delete the dead column | S/M | Unused since `beliefs.py:953`; 0.50 in 5,918/5,918 rows. |
| 8 | Guard labels instead of re-aiming (`:3690-3736`) | M | Delivers P4. Small — 2.4% of ballots, 17 of 590 pluralities. |
| 9 | One re-record of `replays/samples/9p2i` at HEAD with citation relevance on | M (4h, $0) | Standing cadence doctrine: one combined re-record after the substrate settles. |

**Defer:** body freshness band; letting the impostor report a body; the `docs/` front door. None blocks a demo.

**The shown opener.** Not seed 41 — it is now the lead defect. Pick by a measured criterion in card 2: a game whose
ejection rests on a vent flag or on a contradiction the target's own words actually support. Seed 41 keeps a place
in the scorecard's manufactured-contradiction row, where it belongs.

## 10. What to stop, and what to decide

**Stop:** gating on `supported_correct_ejection` (it scores your preferred outcome zero); evaluating on the
proof-free held-out band (it filters out the 288/288 channel); developing `combined_accounts` as-is (0 alibi claims,
0 corroborations, 1 flag in 50 meetings); 3-ballot arenas; coercing ballots to SKIP instead of labelling them;
reading 4-player results as facts about the game; adding levers — five exist, all default None.

| # | Decision | Cost if yes |
|---|---|---|
| D1 | Adopt the process suite as the headline, **with the argmax-independence and manufactured-contradiction rows**; demote role-correctness to a reported cell | The frozen preregistered outcome stops being the gate. Write the demotion down, dated. |
| D2 | Retire the proof-free held-out band as the arena; keep 2100-2999 unseen | Four runs become context, not evidence. |
| D3 | Ship **v1 now**, on today's bytes | Nothing. No re-record, no behaviour change. |
| D4 | **Alibi becomes a route (card 4)** | The one change that makes the evidence honest. Invalidates alibi comparisons against older recordings. |
| D5 | Give the agent a weighing channel and stop instructing deference (cards 6, 7) | The only cards that change what the meeting decides. Expect the ejection rate to move. |
| D6 | Ground the SKIP (card 5) + guard labels (card 8) | Invalidates SKIP comparisons against older recordings. |
| D7 | **One** re-record, after cards 4-8 land | 4 hours wall, $0. |
| D8 | Shelve `combined_accounts`; harvest its SKIP register into card 5 | Shelved, not deleted. |

The honest answer to your question: **this is the path, but it was being measured by the wrong instrument and the
agent was never given the job.** Nothing needs rebuilding. One substrate wave and a new scorecard get you to a state
you can show — and v1 gets you something showable this week.

## 11. Objections considered

What I **accepted** is above: the argmax finding and P6 (§4); the corrected deception table and the seed-41 artifact
(§5); the two false code claims (§3, §5); the SKIP overstatement; the no-flag band at 32/58 rather than 30/58; the
v1/v2 split; and the new card 4. What I **rejected**, with the evidence:

1. **"The verdict falls; the memo certifies a scalar-driven pipeline."** Partly rejected. The deviation column is
   damning, but the 93.6% follow rate alone is not — a faithful summary of the same evidence *should* correlate with
   a good decision, and rev. 1's plumbing findings survived that critic's own attack (they confirmed
   testimony-as-content at `store.py:751` and the 288/288 vent band). More to the point, the deference is **one
   prompt sentence** (`vote_ballot.j2:259`) over a substrate that is already built; a rebuild does not follow from a
   prompt line and a missing struct field. The verdict moved from "a missing early return" to "one substrate wave" —
   not to "reconstruct".
2. **"Delete `considered_alternatives`."** Rejected. MEASURED: non-empty on 1,336 of 1,359 shipped SKIPs (98.3%). It
   is the only weighing artefact already on disk. The defect is that no component reads it
   (`frontend/src/types/api.ts:383` and nothing else), so v1 card 3 renders it.
3. **"Defer the SKIP and P4 cards indefinitely — they buy ~2% of ballots."** Partly rejected. The sizing is right and
   I moved them behind v1, but the SKIP is 40% of the shipped record with no machine-checkable basis and P6 is your
   actual question; both stay in v2 rather than off the plan.
4. **"Every false alibi is a span claim."** Rejected as stated. MEASURED: 103 of 104 — `samples/9p2i` contains one
   false single-tick impostor alibi. The structural point stands and card 4 is unchanged.
5. **Chance baseline 0.231.** Not adopted. For a *crew voter's ballot* the correct denominator is that voter's
   valid-target list, which excludes self; that gives **0.303** (MEASURED). Either figure leaves the 1.6% zero-flag
   deviation rate far below chance, so nothing turns on it.
6. **"Rev. 1's P1 result is unverified."** Accepted as a limit, not a correction: §3 now labels rationale
   faithfulness two-method agreement rather than my measurement.

## Confidence

**High** — recomputed by me this pass from engine-authoritative ground truth (the rendered per-agent route and the
secret-team block, not a reconstruction): the argmax table, the corrected deception table, the alibi-envelope census,
the ejection bands, the seed-41 reading, ballots-per-meeting, the trust constant, the dead-code greps.

**High** — three independent passes agreeing to the digit: citation coverage, the SKIP zero, redirect counts, the
fifth-run arm tallies. **Two-method, not mine:** P1 rationale faithfulness.

**Refutation:** a fresh 9p2i recording at HEAD where crew deviations from the suspicion argmax score at or above
chance, or where impostor self-alibis fail the strict test at a rate meaningfully above crew. Either would mean the
decision interface is healthier than §4 and §5 say.

## 12. Rulings (2026-09-19)

The owner accepted decisions D1 to D8 of section 10 as a set on 2026-09-19, in
the coordinator's session.

| Decision | Ruling | Carried by |
| --- | --- | --- |
| D1. The process suite is the headline; role-correctness is a reported cell; the preregistered `supported_correct_ejection` stops being the project's gate | accepted, dated here | [the process scorecard card](work/process-scorecard.md) and [the evaluation-closing card](work/close-deduction-candidate-evaluation.md) |
| D2. Retire the proof-free held-out band as the arena; band 2100-2999 stays unseen | accepted | the evaluation-closing card, which also retires the sixth freeze card unexecuted |
| D3. Ship v1 now, on today's bytes | accepted | the process scorecard card and [the spectator card](work/spectator-tour-and-alternatives.md) |
| D4. An alibi becomes a route | accepted | [the alibi-as-route card](work/alibi-as-route.md) |
| D5. A weighing channel, no instructed deference, trust wired or deleted | accepted | [the ballot weighing card](work/ballot-weighing-channel.md) |
| D6. Ground the SKIP; guards label and never rewrite; citation relevance by default | accepted | [the grounded-SKIP card](work/grounded-skip-and-guard-labels.md) |
| D7. One re-record after the substrate wave lands | accepted | [the re-record card](work/process-rerecord.md) |
| D8. Shelve `combined_accounts`; harvest its SKIP register | accepted | the evaluation-closing card; the grounded-SKIP card takes the register wording |

Order. Version 1 (the scorecard and the spectator card) and the
evaluation-closing card start at once and in parallel; none changes agent
behaviour. The substrate wave then runs serially, alibi-as-route, then the
grounded SKIP, then the weighing channel, because all three move the shipped
prompt versions and the ballot and claim schemas. The re-record follows the
wave, once. The body-freshness band, an impostor who reports a body, and the
documentation front door stay deferred, as section 9 lists them.
