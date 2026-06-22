# Ground-Up Audit — AiLibi (LLM-driven Among Us)

**Date:** 2026-06-22 04:46
**Method:** Six independent lenses (rubric / qwen-deduction / prompts / interesting / naturalness / fundamentals) read the raw `rubric_score.py`, the four `.j2` prompts, 1,095 real LLM calls, and all 50 committed 9p2i replays *before* the team docs. An adversarial verifier stress-tested every claim and issued per-claim verdicts. This audit weights findings by those verdicts: `yes`-supported claims are foregrounded; `no`/`partly` claims are discounted or corrected.

**Headline:** Five of six lenses independently converged on the same root cause from different angles — *the meeting layer cannot decide the game because evidence can neither fully enter the transcript nor move a listener's vote.* That convergence, repeatedly verifier-confirmed, is the strongest signal in this audit. The team's "stopwatch" diagnosis is **correct**; the "redistribute" fix is **necessary but not sufficient**; the from-scratch rubric is **structurally right but published without its own gating evidence**; and one widely-asserted critique (that the proposed geomean fails its own headline test) was **refuted by the verifier** and should not drive decisions.

---

## 1. The project's true GOAL, and how the RUBRIC should serve it

### The goal, ground-up
Strip the docs away and the soul of this game is **consequence under doubt**: words spoken in a meeting must be *able* to change who lives and dies, under genuine uncertainty, with the possibility of being wrong and of reversal. The engine's hard constraints (LLM-only-in-meetings, room-local crew vision, unwitnessed kills, testimony-based deduction) are a *good* setup for this — the crew is structurally blind, so the meeting is the only place truth can be assembled.

But the true goal is **one level deeper than "make deduction decide."** The `interesting` lens establishes (verifier `yes` on its decisive root-cause claim) that the crew *already tracks truth* — in seed-49 two crewmates each held a 1.00 firsthand vent-sighting on a *different* real impostor — and still lost. The binding axis is therefore **persuasion-and-swing**: a meeting is interesting when one player's testimony visibly moves the room, an accused impostor's counter-accusation can redirect the mob, and the deciding ballot could have flipped. "Deduction decides" is necessary; "the meeting is load-bearing AND contested" is the real target.

### How the rubric should be implemented

The `rubric` lens's **structural verdicts are sound and verifier-confirmed**:
- **Geomean over additive is right** (`yes`). The additive committed scorer literally ranks the two stopwatch games (62.5) above every CREWMATE_EJECT win (max 60.0) — one live term masks a dead one. Geomean's "one dead dimension sinks it" is the correct fix. *The flaw is in the term definitions, not the composition.*
- **Removing R7 (strong-flag legibility) is right** (`yes`). All 112 committed contradictions are WEAK; R7 reads 0.0 in all 50 games. Scoring a structurally-dead term is pointless.
- **D2 pivoting to the always-populated suspicion graph** (instead of dead detector flags) is the right instinct.

But three things must be fixed/added before this rubric is trusted as a selection gate or ML fitness:

1. **The verifier REFUTED the rubric lens's own headline alarm.** The lens claimed its proposed geomean *fails its own check #1* — ranking stopwatch seeds 0/16 at #1–#2. The verifier found this is **an artifact of the auditor's own misimplementation** (`no` on claims 1 and 2): the lens assigned `D1=0.5` to the stopwatch games, but that 0.5 is the *old committed R1*, not the proposed D1. The design doc's D1 keys on outcome `reason` and explicitly scores a CREWMATE_TASKS stopwatch **~0** with no carve-out for a mid-game ejection. With the doc-faithful D1≈0, both stopwatch games geomean to ~0 and rank at the *bottom* — check #1 **passes**. The lens also mislabeled the EJECT winner's D3 (used 0.2 when its committed R3 is 1.0), manufacturing the inversion. **Decision impact: do NOT treat "the proposed rubric is broken" as a finding. It is not.** The real, verifier-`yes` issue is narrower (next point).

2. **The §6 validation is unrun and there is no D1–D4 implementation** (verifier `partly` — factual half TRUE, "it fails check #1" FALSE). `rubric_score.py` contains no geomean/D1–D4 code; `results-rubric-score.json` is the old R1–R7 scorer. The rubric is published as a recommendation with zero gating evidence. **Implement D1–D4 concretely and run the §6 checks as a committed artifact (mirroring `results-rubric-score.json`) — $0, offline — before adopting it.**

3. **Two term-definition fixes are verifier-supported:**
   - **D2 is ~14% a visibility tell, not deduction** (`yes`, matches CAL-1). Per-target separation is +0.122 overall but collapses to +0.070 once the suspicion≥0.9 vent-seen rows are removed; 45% of impostor-views sit below the 0.60 gate. *Decontaminate D2* — subtract a was-seen-venting baseline, or weight D2 toward the conversion half (observation-backed accusation → correct ejection), which actually discriminates outcomes. (Note: the lens's claim that separation is *near-flat across outcomes* was rated `partly` — the verifier could not reproduce the specific +0.286/+0.231/+0.227 magnitudes and found EJECT 62% above PARITY, not the claimed 26%. So "separation barely distinguishes" is directionally right but overstated; lean on the conversion half regardless.)
   - **D3 (impostor craft) rewards futile theatrical deflection** (`yes`). 7 of 9 effective-deflection credits land in games the impostor *lost*. Gate top-tier D3 on the deflection being *load-bearing* (survived the meeting it was accused in AND materially extended the game).

4. **Add a within-meeting deduction-richness term.** D4 (arc) is cross-meeting only, so a rich 7-turn correct-naming meeting scores identical to a 2-turn nothing — blind to exactly the testimony-ingestion improvement the roadmap is pursuing.

5. **Calibrate AFTER the re-record, not before** (`yes`, rated minor — the doc already pre-empts this). 37/50 committed games are the stopwatch the rubric is tuned against; redistribute removes it. Make "lock thresholds after Wave-C" a hard dependency, not a footnote.

---

## 2. How qwen3.5:9b actually does DEDUCTION, and whether the PROMPTS are valid

### What the model genuinely does
- **It does real, well-calibrated deduction from HARD signals** (`yes`). First-accusation precision is 0.86 (95/111) vs a ~29% base rate (all games are exactly 2-impostor). When memory hands it a witnessed vent or kill, it cites the correct tick/room, names the right player at ~0.95 confidence, and **the cited vents are real, not hallucinated** (verified against the action stream).
- **The impostor firewall is total** (`yes`, *better* than claimed). Impostors throw a teammate in **0/56** accusations and **0/209** ballots — the Task-7.12 firewall holds completely (the lens's "4/56" was a slight *over*statement of betrayal).
- **Robustness is excellent** (`yes`): 0/1,095 non-JSON responses, 0 refusals despite the "deception is a game rule" framing, 0 firewall leaks into crew memory, 0 alibi room-drift across multi-turn impostor cover.

### Where the model is DECORATIVE — the central finding
The vote — the step that actually decides ejections — is **engine arithmetic wearing the model's words as decoration** (verifier `yes`, *strongly*):
- `vote_ballot.j2` pre-computes the §4.6 gate verdict in Jinja and hands the model an imperative ("0.70 ≥ 0.60 — you MUST vote to eject"). The model **complies 97.1%** of the time; ~58% of rationales restate the injected number (the lens's 33% was conservative).
- **64% (225/349) of eject votes come from voters who made no accusation** in the meeting.
- Confidence is pinned at 0.95 on 339/759 ballots.

So "deduction quality" the team wants to improve has **almost no causal path to the eject outcome** under current machinery. Catches ride on **one good opener's physical sighting + testimony pile-on arithmetic** (`partly`/`yes`: opener named the eventual ejectee in 25/33 catches; mean 0.9 distinct accusers per catch; 7/33 catches had *zero* transcript accusers). And the decision layer can **override genuine deduction** (`yes`): seed-16 ejects the impostor crew had a *stale prior* on, discarding a fresh eyewitness catch of the *other* impostor.

### Are the prompts valid? (specifics)
**Yes for the failure modes that would halt the pipeline; under-defended for the ones that make the game uninteresting.**

Verifier-confirmed prompt defects, in priority order:

1. **`impostor_report.j2` is dead code** (`yes`). 242 lines (2nd-largest prompt, ~110-line changelog header) that render **only** when an impostor opens a meeting — which happens **0/114 times** by design (impostors never file reports). Its cover directive is byte-identical to `accusation_round.j2:76-86`, which *does* render. **Decision: delete it (route impostor openings through `crewmate_report.j2`) or document it as a deliberate safety net — after confirming the 7p2i set also never triggers it.**

2. **Impostors leak their role into `rationale_text` on ~20–30 ballots** (`yes`): "I am an impostor and p-3 is my teammate; I must vote SKIP to protect our team." Invited by decision-rule 6 ("the tally does not care about your role") + the SKIP-on-teammate block, with no stay-in-character guard. Logged-only (not a gameplay leak) but **will surface verbatim in the Phase-12 mind-inspector UI.** One-line fix: add an in-character rationale guard.

3. **The model launders a bare suspicion scalar as evidence** (`yes` on the core; the kill-rider was `partly`/false). Rendered memory feeds `- p-6: suspicion 0.70` with no provenance; 27% of outputs cite "suspicion score" as a *reason* to vote — circular, since suspicion is the detector's *output*. **Fix: render provenance ("a running summary of your own observations — NOT itself evidence; cite the sighting"), or move the scalar out of the LLM-facing memory entirely.** *Note: the lens's rider that "crew cannot witness a kill, so 'I witnessed a kill' is always a fabrication" is FALSE (verifier) — `DESIGN.md` gives co-present crew a real `witnessed a kill` signal; most such claims are TRUE. Discount that rider.*

4. **A self-contradictory length instruction** (`yes`, minor): rule 5 says rationale is "ONE sentence," the schema example 17 lines later says "<one short paragraph>." 1-line fix.

5. **The prompts are over-worded for a 9B** (`yes`, minor): accusation_round ~2,949 input tokens / 244 lines, rules restated 3–4×; the team's own GATE finding blames the "v7 wall" for thin testimony. State each rule once; consider a de-duplicated/salience-capped memory view.

6. **The emergency no-body guard is mis-scoped** — but the verifier rated this `partly` and found the lens's *mechanism backwards*. The guard does *not* get "ignored/overridden 90% of the time"; the engine **deterministically strips** the fabricated body 100% of the time (`manager.py:384`). The valid part: the strip is over-broad and discards *truthful* bodies in memory. The fix (rescope to "do not invent a body not in your memory") is still correct, but the "model overrides the guard" framing is wrong and the counts were ~2× off (20 emergency openings, not 39).

7. **The prompts are AHEAD of the machinery** (`yes`). The current on-disk v8/v9 rebuild (Task 13.6, never re-recorded) elicits two-source `co_present` testimony for an *inferential detector that hasn't shipped*. The committed detector is firsthand-only (111/112 weak `alibi_vs_sighting`). The n=20 A/B battery shows the rebuild moves the targeted metric (co_present +1.05/turn, parse 100%, 0 leaks — `yes`, verified exactly), but **sequence the re-record AFTER the detector lands**, or you measure prompts against machinery that can't consume their main new output.

**Net on prompts:** structurally valid and robust; the highest-value edits are (a) delete/justify the dead impostor_report, (b) the in-character rationale guard, (c) de-circularize the suspicion scalar — and crucially, **no prompt rewrite fixes deduction until the meeting machinery gives the model's words something to mechanically DO.**

---

## 3. How to DECIDE an interesting simulation (definition + measurable signal)

**Definition (synthesized, lens-convergent):** A game is interesting iff **(a) play decides it — a kill or an ejection, not the clock — AND (b) the meeting was contested — the outcome could have gone the other way.**

**Measurable signals** (track these as the north-star, not the rubric scalar alone):
- **Eject-as-primary-win-path**: fraction of games decided by CREWMATE_EJECT or contested IMPOSTOR_PARITY (today: **6/50 = 12%**, `yes`-verified across both the report JSON and raw `game_over` events).
- **Second-impostor-survival-after-first-catch**: only **6/50 games ever eject BOTH impostors** (`yes`). This is the cleanest "did the table out-think the room" metric.
- **SWING**: did the eject-plurality leader change across turns? did an accused redirect it? was the deciding ballot within one vote of flipping? The memorable games (34, 5, 47) all have a reversal/near-miss; the forgettable ones (20, 3) SKIP on ties while the clock runs.
- **Kill-gifted share** as a *negative* signal: **18/50 crew wins are kill-gifted** (`yes`) — the impostor's own kill drops the victim's last task and tips the pool. A third of crew wins are noise no deduction work can improve; these should score low-interest.

The rubric's D1+D2 capture (a); **add an explicit SWING axis for (b)** — it is currently invisible, and it is the part players actually remember.

---

## 4. What should be IMPLEMENTED — or is it already solid?

**Solid and load-bearing (keep):**
- **Determinism + firewall** (`yes`): 8/8 byte-identical replays under a learned genome; recursive leak_test forbids role/kill fields. *This is the project's strongest asset* and is what makes the ML substrate viable. Roles are so well-firewalled that the auditors had to *derive* impostor identity from actions.
- **Physical substrate** (`yes`): 70% of kills unwitnessed (intended), seed-varied movement (50/50 distinct openings), impostor toolkit no longer passive (kill 207 / vent 204 / sabotage 38 / fake-task 380; wait down to ~8%).
- **Anti-cascade guards** work against pile-ons.

**NOT solid — the implementation gaps, ranked by leverage:**

1. **Add an eyewitness testimony vocabulary** (the `naturalness` lens's flagship — verifier `partly`, with an important correction). The lens claimed crew "cannot say" they witnessed a kill; the verifier found this **overstated**: the engine *does* render `[tick N] You witnessed p-X kill in ROOM` to co-present crew, and witnesses *do* verbalize it (seed-16 p-8, seed-23 p-1). **The real, narrower defect that IS true and decision-useful:** the eyewitness account is *unstructured free-text that mints no contradiction flag*, so it cannot anchor against the killer's fabricated alibi (seed-16: the killer's ADMIN alibi survived an eyewitness). **Implement a structured `witnessed_kill`/`saw_vent` observation type that produces a STRONG flag** — this directly attacks the 7/31 witnessed-kill conversion and the 0/50 strong-flag rate. (Firewall-safe: the witness legitimately saw it.)

2. **Wire spoken/observation-backed testimony into listeners' pre-vote beliefs** (the most-cross-confirmed finding in the whole audit — `interesting` C3 `yes`, `qwen-deduction` C-implied, `naturalness` Claim 3 `yes`, `fundamentals` Claim 2/3 `yes`). A **bare** verbal accusation never enters a listener's pre-vote belief; two crewmates each holding half the truth cannot pool it into a plurality. *Nuance the verifier added:* observation-*backed* testimony **does** now propagate via the Task-10.7/10.15 fold/inform, but only as a sub-gate +0.05 — informs, never ejects alone. **This is the 27-meeting lever from the Phase-9 audit and the single highest-leverage deduction fix.**

3. **Make detected contradictions actually matter** (`yes`, critical, triple-confirmed). 112/112 flags are WEAK (+0.08 → 0.58, below the 0.60 gate *by design*); the inferential `alibi_vs_physical` STRONG path fires **0/114 meetings**. A detected lie can *never* eject. **Light the STRONG detector (workstream B 13.3/13.4)** so a lie crosses the gate; currently only the testimony pile-on can.

4. **Fix the vote-aggregation mechanism.** With 2 impostors + distributed sightings, plurality + tie→SKIP fragments correct votes across both impostors — **16 SKIPPED meetings split correct votes across ≥2 real impostors** (`yes`). Today "crew agrees there ARE impostors but disagrees which" is indistinguishable from "crew is clueless." *Verifier nuance:* in 9 of those 16, pooling still wouldn't beat SKIP (most crew abstain), so vote-split is co-equal with abstention as a failure mode — but a shared-suspicion summary or a split-aware tally is a balance-neutral interestingness fix.

5. **Fix the stale-prior override** (seed-16 class): a fresh in-meeting eyewitness catch should dominate a stale cross-meeting prior on a different player.

6. **Neutralize kill-gifting** (18/50): count the victim's tasks as still-owed, or score those games low-interest.

**The redistribute lever itself:** the team's smoke (2 ejection-wins + 3 win-shapes + 12/12 info-backed ejections vs 8/8 task-wins) is **promising and addresses (a) of the interesting-definition** — it removes the clock that pre-empts the meeting. But it does **not** touch (b) or the aggregation/testimony channel. **Redistribute makes meetings HAPPEN; items 1–5 make them DECIDE and SWING.** Do both.

---

## 5. Does the simulation feel NATURAL?

**The physical game mostly does; the meetings feel half-real.** (`naturalness` lens, mostly `yes`/`partly`.)

**Natural (confirmed):** seed-varied movement, impostors fake-task/vent/sabotage, 70% unwitnessed kills (the intended Among Us feel), a genuinely well-designed hub-and-spoke map. At their best the meetings are real social deduction — seed-47 m1: three crew independently cite an impossible alibi and eject the impostor (`yes`).

**Gamey (verifier-tempered):**
- **Repetitive timing** (`partly`): first kill at tick 4–5 in 43/50 (a consequence of the fixed kill cooldown), first meeting at tick 8 in 28/50. The verifier *refuted* the spatial half — all 50 openings have distinct movement signatures and first kills land in 6 different rooms, so "every game opens identically" is overstated. The *timing* monotony is real; the *geometry* is varied.
- **Static-huddle endgames** (`partly`): 51% of late ticks have 4+ survivors clustered in one room. But the verifier found only 28% of clustered-player actions are `wait` — most are still racing tasks, and clustering is largely a map artifact (Cafeteria is the spawn+meeting+task hub). The "passive huddle, win by waiting" framing is partly unsupported.
- **Visible engine seams** (`yes`): 12% of meeting turns carry a correction marker — fabricated found_body stripped (16×), invalid corroboration dropped (16×), accusing a non-existent "p-10" (11×), impostors self-accusing (11×, 4 impostor). Vote-harmless but reads as broken; **polish before the spectator UI surfaces these transcripts.**
- **Templated language** (`yes`): "I was in the cafeteria" ×30, forced by the alibi format.

**Deepest naturalness defect** (lens fundamental_concern, well-grounded): the social loop is half-open at both ends — the strongest evidence can't fully enter the transcript as *structured* signal, and bare accusations can't be heard. The meeting *looks* like deduction but is largely a deterministic physics-prior the LLM transcribes. Crew win 37/43 by the stopwatch, not by thinking.

---

## 6. DEEPER IDEAS the owner likely hasn't considered

1. **Attack the impostor's INFORMATION position, not its reasoning** (`fundamentals`, strongly grounded by the model-ceiling probe, `yes`). The probe proves a *frontier* model self-incriminates **more** than the 9B (81% vs 69% self-co-location) because better reasoning grounds more faithfully in "you found the body here" poisoned memory. **No model deflects out of the impostor's information disadvantage — so a better model will not help, and may hurt.** The lever the team *owns* is the impostor's information: give impostors overlapping legit tasks near bodies, partial knowledge of who witnessed them, or a self-report tool — so a grounded alibi is *sometimes innocent* and truth/lie become indistinguishable to the listener. **Deception is only possible when the listener can't tell.** This reframes the entire deception problem from "make the model lie better" (capped) to "make honest and dishonest behavior information-symmetric" (tractable, engine-owned).

2. **A truth-shadow oracle for MEASUREMENT (not play).** There is currently *no way to know* whether a detected "contradiction" corresponds to a real lie or a confabulation — and the model demonstrably confabulates (seed-2: structured `against: p-4` while the free_text reasons toward p-7; "shifted between ticks 6 and 5" — time running backwards). A ground-truth shadow (kept out of the play path to preserve the firewall) lets you score detector precision/recall honestly and prove whether deduction is *signal or theater*. Right now the only number is 65% precision on weak flags that eject no one.

3. **Question the LLM-only-in-meetings split for ML.** ALL deception+deduction is frozen, so the trainable tactical layer can only move physical play — the rhetorical *soul* of Among Us is permanently capped at the frozen LLM (the same ceiling Phase 11 hit). Consider a **narrow trainable social channel** — a learned WHO-to-accuse / vote prior conditioned on physical features (the FO-6 suspicion-rank), co-trained with the frozen LLM's prose — so deduction *quality*, not just kill-timing, enters the optimization loop.

4. **Treat the transcript as a CONTAMINATED evidence source.** ~10% of reply turns are verbatim copies of a prior speaker (`qwen-deduction` C7 `yes`: seed-36 p-8 is a 1.0 copy of the impostor's alibi *then accuses that impostor*; seed-15 p-7 parrots its own accuser while self-defending). Any testimony-ingestion or vote-correctness metric must **semantically de-duplicate near-identical turns**, or "N independent corroborators" is often 1 player echoed N times — which would silently inflate the very testimony-spread channel you're about to build.

5. **De-monotonize the opening.** Stagger spawn dispersion or impostor kill-readiness so games don't all open with a tick-4 kill / tick-8 meeting — a repl-value win orthogonal to balance.

---

## 7. FUNDAMENTAL ISSUES (ranked by severity)

1. **[CRITICAL] The social loop is half-open at both ends** — strongest evidence can't enter as structured signal; bare testimony can't move a vote. *Confirmed by 5 of 6 lenses, verifier `yes` on every load-bearing instance.* This caps both "interesting" and "measurable." Everything else is downstream.

2. **[CRITICAL] The outcome is a stopwatch, not a contest** — 6/50 deduction-decided, 6/50 eject-both-impostors, 18/50 kill-gifted (`yes`). Redistribute attacks this directly; it is the right first move but does not fix #1.

3. **[CRITICAL] Detected contradictions cannot eject** — 112/112 WEAK, STRONG path fires 0× (`yes`). Deduction-via-contradiction is structurally dead.

4. **[MAJOR] The frozen-LLM social layer is a hard interestingness ceiling, and a better model makes the impostor's tell WORSE** (`yes`). The binding constraint is the impostor's information position, not model strength — so the ML plan to learn a *tactical* layer feeding a *frozen* social layer can only move physical play.

5. **[MAJOR] The vote step is engine arithmetic the model transcribes** (`yes`): 97% gate-compliance, 64% of ejects from non-accusers, 45% confidence-pinned. "The model is the binding constraint" is a FALSE framing — fix the machinery before attributing anything to the model.

6. **[MAJOR] The rubric about to become ML fitness is unsafe as a RAW scalar** (`yes`): the grounding audit's perverse gradients live in raw `_game_interestingness`; the cleanest suspicion separator is mechanical vent-visibility (CAL-1, 74/74 impostor), so a naive optimizer learns *visibility-avoidance*, not interesting play. *Tempered:* the team is heeding this — the plan uses the FO-6 suspicion-RANK as inner-loop fitness and the *repaired* rubric only as a held-out gate. Keep that discipline; do not regress to the raw scalar.

7. **[MAJOR] Impostor wins are crew aggregation-failure, not impostor craft** (`partly`). Several impostor-win games are genuine vote-splits (seed-49); but the verifier found others are abstention or even a wrong-conviction (seed-12 ejects an innocent), so "the crew saw both and merely split" doesn't generalize to all 7. Still: don't credit impostor *deception* for wins the crew handed over.

8. **[MINOR] Calibrating on data about to be replaced** (`yes`) — 37/50 stopwatch games disappear under redistribute. Lock thresholds after the re-record.

9. **[MINOR] Dead code + leaks + seams** — dead impostor_report (`yes`), role-leak rationales (`yes`), 12% correction-marker turns (`yes`). Legibility debt before the spectator UI.

---

## DIRECTION VERDICT

**The current path is PARTIALLY RIGHT — correct diagnosis, correct first lever, but it stops one layer too shallow and ships a key artifact ungated.**

**Confirmed by the fresh reads:**
- The "stopwatch" diagnosis is **dead-on** (6/50 deduction-decided, 18/50 kill-gifted — every lens, verifier `yes`).
- Redistribute is the **right first move** — it removes the clock that pre-empts the meeting, and the qwen smoke (info-backed ejections, ejection-wins) is real.
- The from-scratch rubric's **structure is sound** (geomean ✓, R7-removal ✓, suspicion-graph pivot ✓).
- "The detector is dead / flags never fire" is **true** (112/112 WEAK, STRONG 0×).

**Contradicted / corrected by the fresh reads:**
- **"The proposed rubric fails its own headline test" is FALSE** (verifier `no` ×2) — an artifact of the auditor's own D1 misimplementation. Don't act on it.
- **"Leaving the qwen prompts as-is" is acceptable for robustness but wrong for interestingness** — and the prompts are currently AHEAD of the machinery (eliciting co_present for an unshipped detector). Re-recording prompts *before* the inferential detector measures them against a consumer that doesn't exist.
- **The team's framing that better deduction = better game is incomplete.** Crew *already* track truth and lose to the aggregation/persuasion channel being firewalled. Redistribute alone yields *more accurate* games, not more *interesting* ones, because nothing a player SAYS can yet change a fate.

**The single most important thing to get right:**

> **Before the re-record locks in a new baseline, close the testimony→belief loop: (1) a STRUCTURED eyewitness `witnessed_kill`/`saw_vent` observation that mints a STRONG flag, and (2) observation-backed spoken testimony that raises *listeners'* pre-vote suspicion enough to actually convert (above the sub-gate +0.05). Redistribute makes meetings HAPPEN; this is what makes them DECIDE and SWING.**

If you re-record on redistribute *without* closing this loop, you will produce a cleaner stopwatch-free game whose meetings are still half-theater — and then calibrate the rubric and train ML against it, baking the half-open loop into the fitness function. **Sequence: close the loop (testimony-ingestion + structured eyewitness + STRONG flag) → re-record → implement & run §6 rubric validation as a committed artifact → calibrate thresholds → then Phase-C ML.** The determinism/firewall substrate is excellent and ready; the meeting machinery is the gate.
