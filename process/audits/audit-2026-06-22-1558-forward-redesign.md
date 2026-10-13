# Forward-Redesign — AiLibi (LLM-driven Among Us)

**Date:** 2026-06-22
**Method:** Synthesis of four group designs (A let-the-vote-decide, B make-deception-a-craft, C unfreeze-the-soul, D judge-not-fitness), a determinism verdict (E), an integration pass, five adversarial skeptic verdicts (all returned "partly"), and a blindspot/overreach pass — reconciled against the committed lab artifacts (`report-phase-b-plan.md`, `report-rubric-design.md`, `report-ml-spike.md`, `report-tally-lab.md`, `report-model-ceiling-probe.md`, `results-rubric-score.json`) and `audit-2026-06-22-0446-ground-up.md`. Recommendations are weighted by the skeptics: every "no"/"partly" verdict was discounted and the surviving, code-grounded claims foregrounded.
**Headline:** The five issues collapse to ONE root wound — crew belief is a closed-form physical-flag tally with no deductive/persuadable representation, so testimony can't decide (A), lies can't land (B), and the only learnable signal is physical (C/D). The skeptic-validated path is NOT the GRAIL speech-as-prior fold the designs front-loaded into the "minimal fix" (it is the least de-risked component and is in direct tension with anti-cascade). It is the committed `report-phase-b-plan` spine: **de-imperative the gate (A-1, $0) + an inferential STRONG-contradiction detector proven on a $0 re-extraction (lights R7 off 0/114) + the repaired geomean referee (D-1) — then ONE combined held-13.12 re-record.** Speech-as-prior, information-symmetry, and the full ML/co-evolution program are reclassified as separately-gated research bets, not part of the soundness claim. REDISTRIBUTE (13.10) is kept; the re-record (13.12) stays HELD until the A/B social fixes land.

---

## 1. The target state (measurable)

"Fundamentally sound + interesting" is two distinct, measurable conditions. SOUND = reasoning has a causal path to the outcome and the metric that judges it is not Goodhartable. INTERESTING = deception is a skill (not luck) and meetings swing.

| Axis | Metric | Today (committed 9p2i, 50g/114m/759b) | Target |
|---|---|---|---|
| Reasoning decides | Eject-decided win share (R1) | 6/50 | **≥ 10/50 and never < 6/50 (HARD floor)** |
| Strong evidence exists | R7 strong-flag meeting share | **0/114** | **> 0 on ≥ 3 seeds, every STRONG flag role-gated to a TRUE impostor, ~0 naming a crewmate** |
| Testimony enters belief | Eject ballots citing a real `primary_reason_id` | 123/349 (226 null) | **null-reason share materially down; verbatim-number echo 56 → ~0** |
| Deception is skill not luck | Impostor alibi survival separated by craft, not vote placement | survival 59/109 = 54% (≈coin flip); same flagged alibi survives one meeting, spared next (seed-16 p-9) | **survival of a STRONG-flagged alibi < survival of an unflagged one by a measurable margin** |
| Meetings swing | Deciding-ballot-within-one-flip share (`plurality_margin==1`); assembled-truth-lost (≥2 true impostors drew eject votes yet SKIP won) | 16 vote-split SKIPs incl. seed-49 (two 0.95 firsthand vent-sightings → 2-2 → SKIP) | **assembled-truth-lost share down; swing surfaced as a scored D4 term** |
| Metric is safe | Geomean referee ranks eject-decided games above clock-wins | additive rubric ranks seed-0/16 clock-wins (62.5) ABOVE every eject-decided game (60.0); seed-34 chain at 40.0 | **all eject-decided games rank above all stopwatch games; no perverse sub-gradient (R2/R3/R7 verified)** |
| Anti-cascade holds | Threshold-inversions; wrong-ejection games; friendly-fire | inversions 0, ff 0 | **all stay 0 (REJECT-BY-PRINCIPLE)** |
| Balance | Impostor win-rate | 14% (Phase-11 floor) | **not cratered below 14% on the pre-re-record fake-provider sweep** |

The held 13.12 re-record is the instrument that moves the bottom-line balance/win metrics; everything above the re-record line is provable $0-offline on the committed replays first.

---

## 2. Group A — let the vote decide

**Goal:** restore a causal path from in-meeting reasoning to the ejection outcome, retire the §4.6 MUST-vote/MUST-skip prompt imperative, while keeping the anti-cascade floor (no random eject), the teammate firewall, and engine/replay determinism.

The skeptic verdict (E and the A-verdict) confirms the load-bearing mechanical fact: the no-random-eject floor ALREADY lives in the deterministic `_tally`/`tally_ballots` (SKIP-on-tie, SKIP-on-SKIP-plurality, sub-threshold→SKIP; rule-5 docstring "independent of LLM compliance"; V0 matched 100% of recorded outcomes in `report-tally-lab.md`). So removing the prompt imperative cannot mechanically lower the floor — A's central claim is TRUE. But two cautions held against A: (a) the "+7% transcription degrades decision quality" premise (WereAlign) has zero committed grounding and the $0 desk test that would right-size A is pre-judged; (b) the imperative is BIDIRECTIONAL — the else-branch renders "you MUST set target to SKIP," and the tally's eject prong reads the model's OWN confidence, so stripping both halves lets a self-rated `confidence≥0.6` on a sub-threshold target eject where it cannot today — a latent cascade vector unless confidence rendering is pinned.

### Option A-1 — de-imperative the gate (RECOMMENDED, low-risk)
Rewrite `vote_ballot.j2` Decision-rule from a command into a non-directive evidence line: present the rendered max-suspicion + the 0.60 reference as one input among transcript + contradiction flags + memory, and ask the model to emit its OWN confidence. Keep the deterministic tally floor unchanged as the silent anti-cascade backstop. Retain the teammate half of the redirect guard and the teammate coercion; relax only the non-teammate target-binding.
- **Real case:** seed-16 m2 p-7 echoes "1.00 ≥ 0.60 … mandatory ejection threshold" with `primary_reason_id=null` and cites no testimony; under A-1 it must reason from p-8's firsthand body-catch of p-9.
- **Validation:** $0 desk test FIRST (count how many of 50 OUTCOMES change if the imperative is removed but the tally kept — likely few; this right-sizes A). Then a 6-10 seed real-9B smoke ($0 Ollama): null-reason share down, verbatim-echo → ~0, **and the confidence distribution checked** (the latent cascade vector — must not cluster a self-rated sub-threshold target across the gate).
- **Cost:** Low, ~1-2 days. Prompt rewrite + the version-bump cascade (`.j2` marker + `game.py DEFAULT_PROMPT_VERSIONS` + 2 orchestrator pins — enumerate it, it is real mechanical work).

### Option A-2 — deliberation round + floor demoted to tie-break (REJECTED)
A closing-statement round then a free ballot with the floor demoted from hard-veto to tie-break. **Rejected on anti-cascade grounds:** demoting the hard floor trades away exactly the protection the owner named; a confident liar + a quiet table could railroad on a 0.58 plurality, and 9B parroting (~6% verbatim) risks echo-cascades. The closing-statement idea is valuable but belongs inside the persuadable-belief track, not as a floor change.

### Option A-3 — GRAIL speech-as-prior (DEFERRED to a gated track)
Fold a per-voter qualitative {more/less/same} LLM judgment into the suspicion graph so an alibi moves belief before the gate computes. This is the same mechanism as B-2 and C-1. It is the real cure for the deeper disease but is substrate-sized, adds a journaled LLM call per voter-suspect, and — per the blindspot pass — is in direct tension with anti-cascade (see §10). DEFERRED behind a fidelity gate.

**Group A recommendation:** ship **A-1 now** as the held-13.12-gating fix, after the $0 desk test right-sizes it. Pin confidence rendering to close the bidirectional-imperative cascade vector. Reject A-2's floor demotion; defer A-3.

**Minimal baseline (do-nothing):** the floor is already deterministic and owner-endorsed; "64% eject-from-non-accuser" may be sound deference, not transcription. Worth the $0 desk test, but the held re-record must not bake in a decorative meeting layer — so A-1 lands, do-nothing does not.

---

## 3. Group B — make deception a craft

**Goal:** make deception a producible, ambiguous, persuadable skill without breaching the 4-layer firewall.

The B-skeptic verdict ("partly") is the most consequential reframe in the pack and it is **code-grounded**:
1. **B1's thesis is refuted by the very probe it cites.** The model-ceiling probe says the binding constraint is POISONED INFORMATION (the impostor found the body, doesn't know who witnessed it); the catchable tell is body CO-LOCATION (81% even frontier), which RISES with model strength and is NOT a movement-ambiguity problem. "Render own movement" does nothing to the body-co-location tell.
2. **"Deception is mechanically impossible" is STALE.** Phase 11 already landed eject-decides 6/50 and impostor 14%; belief is ALREADY partly persuadable (Task 13.7 routes verbal accusations into listener beliefs at +0.05/+0.12). B treats a partly-built seam as greenfield.
3. **GRAIL has zero repo grounding** — reject "8B+graph beats 671B" as load-bearing authority for a code change with no mapped path.
4. **The committed `report-phase-b-plan` inverts B's order.** That plan names the headline lever as an INFERENTIAL DETECTOR (new STRONG contradiction classes, $0 re-extraction lighting R7 off 0/114) and explicitly DEMOTES testimony-ingestion as "the wrong layer and inert on R7," sequenced SECOND and gated to R1/R3 not R7. B's B1→B2 inverts the committed plan's altitude.

So the skeptic-and-committed-plan path replaces B1/B2-first with: **inferential detector spine first.**

### Option B-spine (RECOMMENDED) — inferential STRONG-contradiction detector, $0 re-extraction
`extract_gameplay_facts.py:358` re-runs `detect_contradictions` over the recorded transcript and stamps `strong = not is_weak_contradiction`. A new contradiction class emitted WITHOUT the weak marker lights R7 on a pure RE-EXTRACTION of already-committed replays — $0, zero re-record. Two classes (from `report-phase-b-plan`): cross-speaker `alibi_conflict` promoted STRONG (keep the adversarial/self-pair/narrow/boundary weak guards verbatim), and `alibi_vs_physical` STRONG only under a two-source conjunction, emitted meeting-time over public transcript (NO perception-time absence inference — no liveness channel; firewall-clean).
- **Validation:** RE-EXTRACT committed replays + rerun `rubric_score.py`: R7 > 0 on ≥ 3 seeds, every STRONG flag role-gated to a true impostor, ~0 naming a crewmate (gp-3 watch-the-games BLOCKING), R4 inversions/wrong-ejections do not rise. **$0, no re-record.**
- **Cost:** Low-medium, ~3-5 days; pure offline.

### Option B-1 — information symmetry (legit impostor tasks + own-movement render) — DEFER, contested
The blindspot pass flags a second-order hazard the design missed: the crew's ENTIRE current deduction signal is the impostor being physically where it shouldn't be (112/112 contradictions are alibi-vs-sighting; the FO-6 surrogate's top features are sightings/proximity-to-kill). Making impostor movement legitimately task-driven LAUNDERS that tell into task traffic — crew win-rate could crater not because crew got dumber but because the only working detector signal degraded. It is also entangled with the only validated balance knob (the task-completion clock). B-1 is NOT orthogonal/$0-safe as described. **Defer behind an explicit fake-sweep that checks detector signal-to-noise AND the clock, with owner balance sign-off.**

### Option B-2 — persuadable belief (speech-as-prior) — DEFERRED (= A-3 = C-1, gated)
Same mechanism as A-3. Reuses the real seam (`complete()` → `apply_meeting_evidence_rules` fold → `manager.py` teammate-drop; the +0.05/+0.12 ladder). Belief-fold changes ARE firewall-safe (leak_test does not scan the belief layer). But it touches the `extra='forbid'` frozen `MeetingTurn` (the seed-35/30 husk failure class) so any in-band reasoning field is HIGH-risk and must be walled behind offline qwen husk validation (committed-plan task 13.8) — "smoke-validated" understates it. Sequenced SECOND per the committed plan and gated to R1/R3, NOT R7.

### Option B-3 — intent-conditioned cover-memory + selection — DEFERRED LAST
Highest firewall scrutiny (shared-cover/teammate-corroboration is the most sensitive edge). B's own judgment to defer it holds. The cross-domain pack (CICERO) argues this is actually the load-bearing piece for INTERESTING deception, not a follow-on — but it must ride a proven persuadable substrate + passing leak_test.

**Group B recommendation:** adopt the **committed plan order** — inferential detector spine FIRST (R7 off 0 via $0 re-extraction), then testimony-spread (R1/R3), then defer B-1 (contested, balance-entangled), B-2 (gated husk-validated), B-3 (firewall-last). Do NOT lead with B1→B2.

---

## 4. Group C — unfreeze the soul

**Goal:** make social/deduction agency improvable. The C-skeptic verdict ("partly") is decisive and **I re-ran FO-6 to confirm it.**

The C reframe (better PROSE is not the lever; the binding constraint is that prose has no causal path to the decision) is correct and grounded: the model-ceiling probe shows a STRONGER frozen model is WORSE at the impostor tell (81% vs 69% self-co-location), so C0 (swap to sonnet-4-6) is disproven by the project's own probe. But C1's headline efficacy claim is contradicted by its own linchpin file.

### C1 — learned belief/vote prior (GRAIL-lite, frozen LM) — GO on substrate, REFRAME the claim
- **Data source:** committed `replays/samples/9p2i` (50g/114m/759b) for supervised bootstrap (ejected/not = label, what FO-6 trains on); synthetic fake-provider self-play (~20 games/s, $0) for the impostor suspicion-rank objective. No human labels, no weight fine-tune.
- **Cost:** ~3-5 dev-days; training $0 CPU-minutes; validation smoke ~5 games on local 9B. No GPU.
- **The flaw (verified):** the 64%/82% C1 quotes is the RANK metric that IGNORES SKIP (`report-ml-spike.md:209-210`). The column that maps to a vote OUTCOME — "with-SKIP" — is **0/11 (LLM-free) and 2/11 (18%, LLM-dependent)**; the model collapses to SKIP. FO-6 is a continuous-fitness tool for the IMPOSTOR side; it is NOT a validated crew vote-decider. And the eject decision is plurality+threshold over FROZEN-LLM ballots — a learned prior changes only what the LLM READS. "Trainable belief decides" overstates; belief INFORMS a frozen decider. **Reframe C1 as "learned belief INPUT to a frozen plurality decider," accept it cannot be validated without the re-record it claims to defer (committed ballots were emitted under the OLD prior — you cannot observe re-votes without re-running the LLM), and pin the belief head integer/quantized (FO-4) or it re-opens the Check-1 determinism BLOCKER.**

### C3 — learned ballot selection (Werewolf-RL: LLM proposes N, policy disposes) — follow-on
Most faithful to the existing LLM-proposes/ML-disposes seam. Selection head trainable on committed replays, frozen LM, $0. Must run BEFORE `coerce_teammate_ballot_to_skip` (verify in leak_test). Higher novelty than C1; layered on a proven belief surface.
- **Data source:** committed replays (recorded ballot = positive when its side won) + fake self-play for win-value. **Cost:** ~5-8 dev-days, $0 CPU, no GPU.

### C2 — fine-tune the open model (LoRA/DPO/SPIN) — DEFERRED LAST, gated
The ONLY path that improves prose / could lower the self-incrimination tell. But it RE-OPENS live-record determinism (new weights → byte-divergent re-records; FO-4 frozen-quantized artifact + re-anchored era-pins) and — fatally — mines DPO pairs from the rubric Group D proved broken, so it MUST wait for D-1's repair. It is GPU/infra for a model-tuning novice.
- **Data source:** committed replays → DPO (chosen=winning-side speech, rejected=losing) labeled by the **D-1-repaired** rubric; SPIN needs no labels. **Cost:** ~2-4 weeks wall-clock for a novice; LoRA/QLoRA ~1 consumer 24GB GPU; ~$50-200/iteration cloud if no local GPU.

**Group C recommendation:** GO on the substrate/seam and the impostor-side suspicion ranker (that half of FO-6 is green). REJECT the claim that C1 is a proven crew vote-decider. Build C1 as a belief INPUT, validate on the NEW post-re-record replays (not the old ones), then C3. Defer C2 last, post-D-1. FO-2 co-evolution collapse is the open Phase-C engineering problem — handle with BC-bootstrap + a league/PFSP, never two scratch populations.

---

## 5. Group D — judge, not fitness

**Goal:** replace the additive R1/R2/R3/R7 scalar with a metric that captures swing, separates a lie from a confabulation, and is safe as an ML SELECTION GATE but never the inner-loop gradient.

The D-skeptic verdict ("partly") confirms the spine is REAL and verified, and flags a mechanical landmine.

**Verified:** the Goodhart is exactly as described — `results-rubric-score.json` ranks seeds 0/16 (stopwatch, R1=0.5) at the TOP (62.5), above ALL eject-decided games (60.0) and the contested seed-34 at 40.0. Additive masking (R2=1.0 masks a dead R1=0.5) is real; geomean structurally fixes it. The firewall/determinism claim is SOUND (the scorer is pure-stdlib, reads roles offline from recorded replays, never touches the live packet leak_test guards). The lens-vs-gradient split (symmetric geomean = held-out referee; FO-6 physical-suspicion rank = side-specific inner-loop fitness; the rubric is NEVER the gradient) genuinely contains the Goodhart by construction.

### D-1 — multiplicative D1-D4 geomean as the held-out SELECTION GATE (RECOMMENDED spine)
Replace the additive sum with `floor_multiplier × geomean_weighted(D1,D2,D3,D4)`, D4 enriched with a swing term (`plurality_margin==1` + cross-meeting suspicion movement).
- **The landmine (verified):** a naive geomean on the CURRENT substrate **collapses all 50/50 games to 0** — R7 is 0.0 across the ENTIRE set, R3 is 0 in 44/50; any zero term zeros the product. So D-1 is **strictly downstream of the B-spine detector + the 13.11 enrichment** (which lights R7) AND needs an epsilon/weighted-geomean floor. It is NOT parallel to the A/B fixes; it lands JUST BEFORE the re-record once R7 is non-zero.
- **Overstated readiness:** `suspicion_separation` (the new D2 spine) exists NOWHERE in code; `suspicion_graph_by_voter` is VOTE-call-only (cross-meeting arc is sparser than implied). "~90% designed" is the spec, not the code.
- **Cost:** Low, ~1-2 days once R7 is lit. $0, replay-exact, zero firewall risk.

### D-2 — swing_lab + truth-shadow MEASUREMENT oracle — GREENFIELD, prerequisite for full D-1
Counterfactual ballot-fragility + an offline truth-shadow oracle (re-seeded roles + FO-6 reconstruction) that labels real-lie vs confabulation for CURATION and detector precision/recall — never the gradient (oracle-sees-roles → Goodhart-unsafe by construction, that separation is the point). **Verified caveat:** `swing_lab`/`truth_shadow` are ZERO code today; D-1's D4 swing term depends on D-2, so D-2 is a PREREQUISITE for full D-1, not a parallel sibling.
- **Cost:** Low-medium, ~1.5 days. Add a leak_test-style assertion that the oracle module is never imported by the play path (no automated guard exists today).

### D-3 — LLM-judge of persuasion — DEFERRED, quarantined
Reads the LANGUAGE substance the deterministic chain can't. But re-opens the Phase-7.5 fake-vs-real fidelity trap (fake 76% vs real 0%), and the frozen 9B is too weak to judge its own prose. Quarantine to a separate versioned curation artifact; NEVER summed into D1-D4 or fed to fitness.

**Group D recommendation:** **D-1 geomean as the spine** (epsilon-floored, downstream of the detector + 13.11, landing just before the re-record), with **D-2 built first as its prerequisite** (swing producer + truth-shadow oracle). Defer D-3. Use the <1hr r1-reweight only as an interim patch if a ranking fix is needed before the geomean can land.

---

## 6. Determinism verdict (E)

The CORE reframe holds against the code (`orchestrator/replay.py` docstring: engine determinism = state_hash + recorded actions; LLM-layer determinism = replaying recorded outputs; the on-disk format splits `ReplayEntry` (engine) from the recorded meeting payload). So **keep ENGINE byte-determinism frozen forever** — it is what the ML $0 loop, the spectator `replay_loader.py` (re-walks every tick, HARD-FAILS on state_hash mismatch), `leak_test.py`, and the 15 era-pins all consume — and **retire only the §4.6 imperative**, a separable anti-cascade DESIGN CHOICE, not a determinism requirement. Every option A-D operates on the recorded-social or offline-measurement layer; `advance_tick`/RNG/state-hash are untouched at replay.

**E's muddle (held):** "moving the no-random-eject floor into `_tally` where it belongs" is largely a no-op — the floor is ALREADY in the deterministic tally. Retiring the imperative removes EJECT-PRESSURE, it does not relocate a misplaced floor. And "$0, breaks NO determinism" omits the version-bump cascade (`.j2` marker + `DEFAULT_PROMPT_VERSIONS` + orchestrator pins + ~15 era-pin re-anchors). Engine-determinism-free ≠ cost-free.

**Per-option engine-determinism impact:** A-1, B-spine, A-3/B-2/C-1, B-1, B-3, C-3, D-1, D-2, D-3 all = **no** engine-determinism break (recorded-social or offline). **C-2 = partly** — engine untouched, but new weights → byte-divergent LIVE re-records (the only option that materially widens the live-record surface; FO-4 mitigation + re-anchored baselines).

**Room for both:** YES, because the on-disk format already separates them. The FSM engine stays byte-deterministic; the meeting stays recorded-not-deterministic; ML trains on recorded actions + the FO-6 surrogate with the frozen LLM as the periodic gate.

**The unflagged determinism risk (blindspot):** the LLM is "frozen" by NAME not BEHAVIOR. Provider-side model updates, sampling, `num_ctx`, quantization, and Ollama version changes silently move the recorded social layer (history: the `num_ctx=8192` fix, the 7b→9b migration). When belief is persuadable-by-LLM AND the LLM meeting is the ML selection gate, a silent provider drift becomes a silent FITNESS drift with no era-pin to catch it (era-pins guard engine bytes, not meeting semantics). **Action: specify a pinned-quantization / recorded-logits gate for the SOCIAL layer the way FO-4 did for the physical layer.**

**Spectator impact:** no DTO/state-hash/fog-reconstruction change is forced. But (1) the belief×truth panel (12.6) should now render belief MOVING from arguments rather than fixed +0.05/+0.12 steps — expose the per-voter speech-prior delta; (2) ROLE-LEAK in the mind-inspector (12.8) — B-3's cover-memory must stay self-channel-only (never reference a teammate position) and the leak smoke should add a mind-inspector-render assertion.

---

## 7. Integrated architecture + A×E interaction matrix

**Target architecture:** a two-layer system with a TRAINABLE persuadable-belief seam bridging them. (1) The FSM engine stays byte-deterministic forever — the substrate the ML $0 loop, spectator, leak_test, era-pins consume; never changes. (2) The MEETING layer stays recorded-not-deterministic but is rebuilt so reasoning decides: A-1 retires the imperative; the inferential detector mints STRONG evidence that can cross the gate; the testimony-spread fold lets arguments move belief. (3) ML trains the PHYSICAL layer only (clean `agent_factory` seam, zero engine edits), selected against the FO-6 LLM-free physical-suspicion RANK as continuous $0 inner-loop fitness, with the frozen LLM meeting as a periodic selection gate and the repaired D-1 geomean as the held-out REFEREE (never the gradient).

| Pair | Interaction | Kind |
|---|---|---|
| A×B | A-1 frees the ballot; the inferential detector gives it STRONG evidence to weigh — both serve "the vote decides." | synergy |
| A×C | A-1's recorded seam is where C's trainable belief/selection later sits; C-3 selection must run BEFORE teammate-coerce, an ordering A-1's tally change must preserve. | synergy |
| A×D | A-1 + the detector make meetings that decide and R7 non-zero, which is exactly what D-1's geomean must score — D-1 verifies the fix without becoming its gradient. | synergy |
| **A×E** | E confirms A-1 breaks NO engine determinism (gate runs in `_tally` over recorded ballots); the version-bump cascade is the real (non-determinism) cost; the bidirectional imperative is the cascade vector E must pin. | synergy + caution |
| B×D | the detector's STRONG flags are what light R7, which is what makes D-1's geomean runnable (else all 50 collapse to 0). | hard dependency |
| C×D | D-1 is the held-out SELECTION GATE for C's policies; FO-6 is C's inner-loop fitness; the rubric is NEVER the gradient; C-2 must wait for D's repair. | synergy + conflict (C-2) |
| C×E | C-1/C-3 are recorded-layer, FO-4-contained; C-2 alone re-opens live-record determinism → sequenced LAST. | conflict (C-2) |
| D×E | D-1/D-2 offline, zero engine impact; D-3 is non-deterministic → quarantined from the gate and the gradient. | conflict (D-3) |

---

## 8. Minimal-viable fix vs full redesign

**Minimal fix (the soundness claim):** **A-1 (de-imperative, $0) + the inferential STRONG-contradiction detector (B-spine, $0 re-extraction lighting R7 off 0/114) + the epsilon-floored D-1 geomean (referee).** This is the smallest change that closes the testimony→evidence→outcome loop the prior audit named DOMINANT (b1=27: spoken testimony never enters listeners' beliefs and witnesses lose plurality). It is entirely $0-offline-provable on the committed replays BEFORE the re-record, breaks zero engine determinism, and keeps the firewall intact. **Critically, this is NOT the designs' minimal fix** (A-1 + GRAIL speech-as-prior fold). The blindspot pass is decisive: the speech-as-prior fold is the least de-risked component, is in direct tension with anti-cascade, and front-loading it into the minimal tier bets the soundness claim on an unproven, possibly-contradictory mechanism.

**Full redesign:** minimal fix + testimony-spread (R1/R3) + the held 13.12 re-record, THEN the ML layer (C-1 belief INPUT → C-3 selection on the NEW replays, D-2 truth-shadow oracle as the held-out gate), with B-1 (information symmetry, contested/balance-entangled), B-3 (firewall-last), C-2 (fine-tune, re-opens determinism, post-D-1) deferred LAST.

**Recommendation:** ship the minimal fix to PROVE the loop closes on $0 offline evidence (R7 off 0 + geomean re-ranks + A-1 outcome desk test), then batch testimony-spread into the SAME held-13.12 re-record. Defer the speech-as-prior fold, all of C, and B-1/B-3/C-2 as separately-gated research bets — NOT part of the soundness claim.

---

## 9. Roadmap reconciliation

The deferred memory items integrate cleanly into this sequence — none is orphaned:

- **b1=27 testimony-ingestion (the DOMINANT lever):** this is the SPINE, not a deferred item. The inferential detector (B-spine) mints the STRONG evidence that lets witness testimony cross the gate; the testimony-spread fold (committed task 13.7, partly built) routes 2-voice corroboration to the gate-cross. Both are sequenced inside the minimal/near-minimal fix and gated on R1/R3 conversion. The 27-meeting lever is the headline target metric.
- **BotC-style crew misinformation (cross-domain idea):** reclassify as a FUTURE balance/richness lever that sidesteps the LLM ceiling entirely — inject structured noise into the crew's PHYSICAL channel (false sightings, room-local fog, ambiguous labels) so the deterministic substrate is the source of richness. The room-local visibility probe already in the bundle is the hint. This is an owner-gated balance change (same class as the frozen clock), NOT part of the soundness fix — but it is the strongest answer to "interesting without unfreezing the soul" and should be on the roadmap as an alternative to the costly persuadable-social bet.
- **Two-phase reasoning:** already on the committed plan as the gated optional task 13.8 (parse-only reason→emit sub-schema, offline qwen husk-validation FIRST because `MeetingTurn` is `extra='forbid'` frozen). Keep it gated and offline-validated; do not let it touch the re-record without the husk smoke.
- **ML / Phase-C plan:** reconciles as the LATER track. Phase A (spike) is CLOSED on main. The substrate is GO; the impostor-side suspicion ranker is green (FO-6 RANK). C-1 (belief INPUT, not decider) and C-3 (selection) train against the NEW post-re-record replays. C-2 (fine-tune) is last, post-D-1 rubric repair. The open Phase-C engineering problem is co-evolution stability (FO-2 collapse) — handled with BC-bootstrap + AlphaStar-style league/PFSP + a belief-EXPLOITER pre-test (see §10). The Pre-ML grounding audit's verdict stands: the rubric is unsafe as raw fitness; use the FO-6 suspicion rank + the D-1-repaired geomean as a held-out gate, never the gradient.

---

## 10. Blindspots

The blindspot pass raises three HIGH-severity structural issues no group named, all weighting the recommendation toward the smaller, offline-provable spine:

1. **Persuadability vs anti-cascade may be a CONTRADICTION, not a tuning task (HIGH).** The whole point of the WEAK_DELTA=0.08 ladder + the 0.60 gate + the lift cap is to make a single confident speaker UNABLE to move belief across the gate. A speech-as-prior fold that lets arguments move belief is BY CONSTRUCTION a channel for a confident liar to railroad. A bound tight enough to preserve anti-cascade likely reproduces "testimony never decides"; a bound loose enough to close that loop re-opens cascade. **No group ran the desk experiment that finds whether a single bound satisfies both.** This is why the minimal fix uses the INFERENTIAL DETECTOR (STRONG evidence the gate already trusts, constrained to two-source conjunction for the full delta) rather than the speech-as-prior fold — the detector path is anti-cascade-safe by construction; the fold may not be.
2. **The speech-prior closes an adversarial loop on a DESCRIPTIVELY-validated surrogate (HIGH).** FO-6 was validated as a physical suspicion RANK, not as a target an adversary optimizes to minimize. The moment B/C ship, the impostor learns to produce whatever the belief-fold rewards as "innocent" — the FO-2 degenerate-disengagement collapse relocated into the social layer where it's harder to detect (it looks like "good deception"). **Cross-domain fix: before trusting the fold, train a dedicated belief-EXPLOITER impostor whose only fitness is to fool the fold — a $0-offline test, run BEFORE the re-record. If it trivially wins, the fold is Goodhartable and not ready.**
3. **Multi-impostor COORDINATED deception is architecturally forbidden, yet 9p2i is canonical (HIGH).** The firewall is a 4-layer NO-coordination wall; MEMORY lists "no signaling" as open. The redesign makes deception a SOLO craft while the structurally richest content — "are these two covering for each other?" — stays impossible. This is the deeper version of issue B. Flag for a future phase; it is where Among Us's real depth lives and the current scope cannot reach it.

Medium-severity: B-1 likely degrades the very physical detector/surrogate signal the deduction game runs on and is coupled to the only validated balance clock; the "frozen" LLM drifts silently (no social-layer era-pin); "interesting" is being defined/measured/trained entirely inside a closed loop of a mediocre model judging its own prose (the human/strong-judge anchor is deferred LAST — add a periodic strong-judge sanity anchor as a 3-way agreement gate); the full ML program is a research stack for a solo novice justified by $0 probes that each needed 2 Codex rounds of bug-fixes.

**Overreach verdict (partial):** diagnosis right, prescription over-builds. The targeted fix (A-1 + the inferential detector + D-1, measured on existing replays before any persuadable-LLM-fold or ML) is sound and small. The persuadable-social + co-evolution ML program is a research bet the evidence does not yet justify folding into the "fix" — and may be optimizing a social ceiling it cannot raise (emergence is physical; the social soul is capped at the frozen LLM). Honest framing: make the PHYSICAL game interesting and let the frozen LLM be a fixed, slightly-better-wired referee.

---

## 11. Recommended sequenced path

REDISTRIBUTE (13.10) is KEPT and in-flight (the physical lever that breaks the stopwatch). The RE-RECORD (13.12) stays HELD until the A/B social fixes land, so the new baseline captures meetings that actually decide.

| # | Step | What | Depends on | Effort |
|---|---|---|---|---|
| 0 | $0 desk test (A) | Count how many of 50 OUTCOMES change if the imperative is removed but the tally kept — right-sizes A-1; confirm imperative changes rationale broadly but few outcomes. | — | $0, ~½ day |
| 1 | A-1 de-imperative the gate | Prompt rewrite + version-bump cascade; keep the deterministic tally floor + teammate firewall; **pin confidence rendering** to close the bidirectional-imperative cascade vector. 6-10 seed real-9B smoke ($0): null-reason down, echo→0, confidence distribution checked. | 0 | ~1-2 days, $0 |
| 2 | B-spine inferential detector | Cross-speaker `alibi_conflict` STRONG + `alibi_vs_physical` STRONG (two-source conjunction, meeting-time over public transcript). **RE-EXTRACT committed replays** → R7 > 0 on ≥3 seeds, every STRONG flag role-gated to a true impostor, ~0 on crewmates (gp-3 watch-the-games BLOCKING), R4 not rising. | — | ~3-5 days, $0 |
| 3 | Belief-band wiring | Route new STRONG classes through the corroborate-within-round band; lone atom informs (sub-gate), two-source conjunction crosses. Keep dedup + lift cap + the +0.05<0.10 invariant. | 2 | ~2 days, $0 |
| 4 | Testimony-spread (R1/R3) | Graduated 2-voice +0.12 gate-cross (persist only flat +0.05). Gated on R1/R3 conversion, NOT R7. | 3 | ~2-3 days, $0 |
| 5 | D-2 swing_lab + truth-shadow oracle | Build FIRST as D-1's prerequisite (swing producer + real-lie-vs-confab oracle, curation-only, never gradient; add the never-imported-by-play-path assertion). | — (parallel to 2-4) | ~1.5 days, $0 |
| 6 | D-1 geomean referee | Epsilon-floored multiplicative geomean; lands once R7 is non-zero. Verify it re-ranks eject-decided above stopwatch and has no perverse sub-gradient. | 2,5 | ~1-2 days, $0 |
| 7 | belief-EXPLOITER pre-test | $0-offline: train an impostor whose only fitness is to fool any persuadable fold; if it trivially wins, the fold is Goodhartable — gate before any fold ships. | 3 | ~2-3 days, $0 |
| 8 | **HELD 13.12 RE-RECORD** | Fake-sweep FIRST (impostor win not < 14%); batch A-1 + detector + belief-wiring + testimony-spread + the kept REDISTRIBUTE (13.10); real-Ollama re-record both sets; regenerate rubric; **re-anchor the 15 era-pins**; close-audit; leak smoke + mind-inspector-render assertion. Abandon branch if R1 < 6/50. | 1,3,4,6,7 | ~1 wk wall-clock, $0 |
| 9 | C-1 belief INPUT (reframed) | Build as a learned belief INPUT to the frozen plurality decider (NOT a decider); validate on the NEW post-re-record replays; pin head integer/quantized (FO-4). | 8 | ~3-5 days, $0 CPU |
| 10 | C-3 learned selection | LLM-proposes-N + selection head; ordered BEFORE teammate-coerce (verify leak_test). | 9 | ~5-8 days, $0 CPU |
| 11 | Deferred research bets | B-1 (info symmetry, owner balance sign-off + detector-SNR fake-sweep); B-3 (cover-memory, firewall-last); two-phase reasoning (gated, husk-validated); C-2 fine-tune (post-D-1, re-opens determinism); BotC physical-misinfo (owner balance lever). | as gated | weeks each |

---

## 12. Open owner decisions

1. **A-1 scope:** does the $0 desk test (step 0) showing few OUTCOME changes shrink A-1 to a rationale-text fix, or do you want the confidence-rendering pin shipped regardless to close the cascade vector?
2. **Persuadable-belief fork:** adopt the committed-plan INFERENTIAL DETECTOR as the deduction spine (anti-cascade-safe by construction, $0 re-extraction) vs the designs' GRAIL speech-as-prior fold (richer but in direct anti-cascade tension, unproven, husk-risky)? Recommendation: detector first; fold only behind the belief-exploiter pre-test (step 7).
3. **Information symmetry (B-1):** ship impostor tasks despite the verified risk of laundering the only working detector signal + coupling to the balance clock? Recommendation: defer behind a fake-sweep that measures detector SNR + clock, with explicit balance sign-off.
4. **BotC-style physical misinformation:** pursue structured crew-channel noise (false sightings, room-local fog) as the "interesting without unfreezing the LLM" lever — an owner-gated balance change, same class as the frozen clock?
5. **Frozen-social-layer pin:** specify a pinned-quantization / recorded-logits gate for the SOCIAL layer (the FO-4 analogue), to stop silent provider drift from moving the D-1 referee and the ML selection gate undetected?
6. **ML scope honesty:** accept that the social soul is capped at the frozen LLM (emergence is physical) and frame Phase C as "trainable physical play + a slightly-better-wired referee," not "unfreeze the soul" — and treat C-2 fine-tune + co-evolution as a separately-gated research bet, not part of the soundness deliverable?
7. **Re-record batching (cadence doctrine):** confirm the single held-13.12 re-record absorbs A-1 + detector + belief-wiring + testimony-spread + REDISTRIBUTE (13.10) together (one combined re-record, 15 era-pins re-anchored), so no lever is re-recorded twice.
8. **Multi-impostor coordination:** acknowledge as a flagged future phase (architecturally forbidden today by the firewall; where the deepest deduction content lives) — in-scope-later or permanently out?
