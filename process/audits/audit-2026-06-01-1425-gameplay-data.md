# Gameplay Data Audit — 2026-06-01 14:25 (replays/samples/7p2i)

## 1. Verdict

**SIGNIFICANT_ISSUES.**

The 50-game committed eval set at `replays/samples/7p2i` is mechanically faithful (every per-tick reconstructed `state_hash` matched the recorded hash, so playback is byte-identical and every event below is exactly what the recorded games produced), and several previously-feared defects are confirmed *absent*: the §6.3 win-condition impostor-elimination gap does not recur, no game continued past its zero-impostor tick, no win attribution disagreed with the reconstructed final state, no phantom bodies or untriggered meetings, and the dead-player-action hard violation has zero standalone instances. That correctness floor is solid.

However, the set is **not usable as a Wave-1 balance/intelligence baseline in its current state**, for two independent reasons. First, in **39 of 50 games an impostor kills its own teammate** (35% of all 111 kills are impostor-on-impostor), and that single binary event explains the entire win split: of the 39 self-destruct games, impostors won **0**; of the 11 clean games, impostors won **9 of 11 (82%)**. The headline 38-9 (76% crew) outcome is therefore an artifact of a teammate-blind kill policy interacting with a permissive engine rule, not a measurement of crew deduction or agent reasoning. Second, **3 of 50 games (seeds 25, 36, 40) hard-abort with no `game_over`** when qwen2.5 emits a non-chronological `AlibiClaim` (`from_tick > to_tick`) that the Pydantic validator rejects, killing the whole run instead of failing soft — silently dropping 6% of the set.

On top of those two blocking issues, the meeting/voting channel is nearly inert: 88% of meetings SKIP, crew suspicion and accuse confidences are near-constant enums (0.55 / 0.85) rather than calibrated probabilities (vote_ballot ECE 0.52, right <30% of the time at 0.85), and 22 of 45 SKIPPED meetings had a structured contradiction naming a *living* impostor that the table ignored. These are exactly the Wave-1 agent-intelligence targets, but they cannot be A/B-measured cleanly until the two blocking issues above are fixed and the set is re-recorded. The recommendation is to treat the current 38-9 split and all derived balance/calibration/vote_correctness numbers as provisional, fix gp-1 and gp-2, re-record, then re-baseline.

## 2. Environment

- **Audit timestamp:** 2026-06-01 14:25
- **Audited HEAD:** `de2e794 update tournament eval report`
- **Sample dir:** `replays/samples/7p2i` (roster 7p/2i, tasks_per_crewmate=2)
- **Games analyzed:** 50 (== 50 replay `.jsonl` files; verified)
- **Extractor self-checks:** all PASS — every seed re-seeds to exactly 2 impostors; facts meetings (51) == `"kind":"meeting"` records (51); every per-tick reconstructed `state_hash` matched the recorded hash; every kill victim is in its game's deaths set.
- **Mechanical (code-certain) findings:** 3 (MECH-B-1/2/3) — not subject to refutation.
- **Judgment findings:** 31 raw → 5 refuted (2-of-3 skeptics) → **26 surviving** load-bearing.
- **Refute rate:** 5/31 = 16.1%.
- **One verifier severity adjustment:** F-F-5 downgraded medium → low.

## 3. Confirmed bugs & rule violations

### Mechanical findings (code-certain, state-hash-verified)

**MECH-B-1 (blocking) — Impostors kill their own teammate in 39/50 games (35% of all kills).**
39 of 111 resolved kills have `victim_role == IMPOSTOR`. Many are MUTUAL same-tick kills in the spawn room on tick 1-2 (both impostors target each other; the engine resolves the first and rejects the second as "player is dead"). `engine.rules.resolve_kill` only checks the actor is IMPOSTOR and never checks the target is a CREWMATE, so the kill is legal. *Evidence:* seed 4 tick 1 p-5(IMPOSTOR) kills p-6(IMPOSTOR) in CAFETERIA (mutual); seed 13 tick 1 p-1→p-4 CAFETERIA; seed 0 tick 7 p-3→p-5 MEDBAY; seed 32 tick 1 p-5→p-7 CAFETERIA. *Repair:* exclude `fellow_impostor_ids` from kill-target selection (agent layer); optionally add an engine friendly-fire reject. See **gp-1**.

**MECH-B-2 (high) — 16 kills queued against an out-of-room target.**
16 `ActionRejected "kill requires same room"` events — an impostor emitted a kill action without checking co-location, wasting the turn. *Evidence:* seed 1 tick 2 p-7; seed 9 ticks 2/6/9 (p-7,p-7,p-2); seed 34 ticks 2/7 p-6. *Repair:* gate the kill intent on the target being in the actor's current room before emitting. See **gp-3**.

**MECH-B-3 (informational) — 80 same-tick "player is dead" rejections are downstream symptoms of B-1, not a standalone bug.**
All 80 `ActionRejected "player is dead"` are SAME-TICK (the actor died earlier in that tick's resolution order): 37 are the losing half of mutual impostor kills, 39 are crewmate `do_task` continuations whose owner was killed that tick, 4 are move/wait. ZERO are a player dead *coming into* the tick still being handed an action — so the strict dead-player-action hard violation has **no instances**; the dead-player gate works correctly. *Evidence:* seed 3 tick 4 p-2/p-6 do_task rejected (both killed that tick); seed 4 tick 1 p-6 kill rejected after p-5 killed it first. *Repair:* none for the gate; this count shrinks automatically once gp-1 lands. Treat as a derived metric of B-1.

### Surviving engine/correctness judgment findings

**E-E-1 / A-A-2 (blocking) — Non-chronological-alibi schema reject aborts the whole game (3 instances = all 3 no-game-over games).**
qwen2.5:7b-instruct emits `AlibiClaim` with `from_tick > to_tick`; the Statement validator rejects it, the meeting aborts, and the game terminates with NO `game_over` record. `winner`/`reason`/`game_over_tick` are null for exactly {25, 36, 40} and no other seed. 6% of the set corrupted; ~127,121 input tokens (4.6%) spent on games that never resolve. *Evidence:* seed 25 failed_call @tick 11 (meeting-1, from_tick=8>to_tick=1); seed 36 @tick 11 (meeting-0, 8>1); seed 40 @tick 14 (meeting-1, 9>1) — in each replay the LAST jsonl record is the `failed_call`, no `game_over` follows. *Repair:* (1) parse-tolerance — swap the bounds or coerce to a 1-tick window and retry once; (2) fail-soft at the meeting level — degrade one rejected statement to a missed-deadline placeholder and continue. Do both. See **gp-2**.

**A-A-3 (informational) — §6.3 win-condition impostor-elimination gap confirmed CLOSED in this data.**
Every both-impostors-dead game resolves on the exact elimination tick with reason CREWMATE_EJECT, and `first_zero_impostor_tick == game_over_tick`. No tick records exist beyond any `game_over_tick`. *Evidence:* seed 28 (both dead@17, go=17, p-3 ejected@17), seed 43 (both dead@7, go=7, p-7 killed@6 friendly fire, p-6 ejected@7), seed 45 (both dead@15, go=15). *Repair:* none — confirmation only; keep `first_zero_impostor_tick == game_over_tick` as an automated self-check.

**A-A-4 (informational) — All win attributions agree with reconstructed final state; no phantom meetings/bodies.**
All 9 IMPOSTOR_PARITY wins are 2v2 at game-over; all 3 CREWMATE_EJECT wins have `alive_impostors == 0`; all 35 CREWMATE_TASKS wins still have an impostor alive (EJECT branch correctly did not fire). Every ejected player's stated role matches its true role. All 51 meetings are report-triggered (0 emergency), every reported `body_id` matches a real kill. *Repair:* none.

## 4. Gameplay trends

Evidence-backed, numbers included:

- **Friendly fire decides the game.** 39/50 games (78%) contain an impostor-on-impostor kill; conditioned on it, crew win 36/39 (the other 3 are the no-game-over aborts) and impostors win 0. In the 11 clean games impostors win 9 (82%). The single binary "did an impostor kill its teammate" fully explains the 38-9 split. (B-B-1, A-A-1, D-D-1, F-F-1)
- **Tick-1 mutual spawn-room kills.** In 10 games the very first action (tick 1, CAFETERIA) is a mutual kill where both impostors target each other; all 10 are impostor-on-impostor. 18/50 games have their first kill at tick ≤2. 167 kill actions were issued but only 111 resolved — 56 wasted kill actions. (B-B-2)
- **CREWMATE_TASKS dominates (35/50 decided games).** Parity wins are fast (avg tick 11.6, each with exactly 3 kills); task wins are slow (avg tick 20.3). Crews win mostly by the task clock, not by deduction. (B-B-6)
- **Half of bodies are never reported.** 111 kills vs 51 meetings (all body-report-triggered) ⇒ ≥60 bodies (54%) unreported; 11 games have kills but zero meetings (20 bodies unreported in those alone). (B-B-5)
- **Kill spread is healthy.** Kills span 9 rooms (CAFETERIA 25 → STORAGE 5), kills/game 0-4 (mean 2.22), meetings/game 0-3 (mean 1.02) — coverage is non-degenerate on these axes. (F-F-6)
- **Impostor action repertoire is move/wait/kill only.** Zero vent, zero sabotage, zero `do_task` (no task-faking), zero `report`. Impostor-only tally: wait 555, move 664, kill 167. This bounds how "intelligent" pre-Wave-2 impostor play can look. (D-D-4)
- **Fabricated-alibi survival 57.4%.** 101 impostor alibis, 58 survive contradiction detection; the §5.4 detector catches ~43%. (D-D-5)

## 5. Decision-quality findings

### Crew (Lens C)

- **All 3 wrong (crewmate) ejections share one failure mode (C-C-1, high):** an impostor kills its own partner, the body triggers the meeting, and a crewmate who was merely *sighted near the body* is flagged by a technically-true-but-causally-irrelevant `alibi_vs_sighting` contradiction and ejected at 0.85-0.95. *Evidence:* seed 7 (p-3 ejected, 13 contradictions), seed 49 (p-2 ejected @0.85, 16 contradictions), seed 46 (p-2 ejected on alibi_conflict). Crew has no "present at scene ≠ killer" prior.
- **vote_ballot ECE 0.52 (C-C-2, high):** accusing ballots are cast at a near-constant 0.85 but hit an actual impostor only 29.7% of the time (bin [0.8-0.9) = 64/94 votes). 0.85 is a fixed output token, not a calibrated probability.
- **§4.6 skip threshold leaves impostors safe (C-C-3, high):** all 45 SKIPPED meetings had ≥1 living impostor; **22 of 45** had a contradiction explicitly naming a living impostor, yet the table skipped (in 9 of those 22 the flagged impostor got ZERO eject votes). 65% of all 272 ballots are SKIP; 84% of SKIP ballots carry exactly 0.55, just under the 0.60 gate. *Evidence:* seed 32 meeting-0 tick 8 flagged impostor p-5 but all 6 ballots SKIP@0.55.
- **vote_correctness_rate=1.0 is misleading (C-C-4, medium):** computed as evidence_backed_impostor_ejections / impostor_ejections = 3/3, by design excluding the 3 crewmate ejections. Actual ejection accuracy is **50%** (3 impostor / 6 total). Pair the headline with `ejection_accuracy`.
- **Confidences are a two-value enum (C-C-5, low):** SKIP=0.55 in 149/178, accuse=0.85 in 63/94 — the suspicion graph carries almost no discriminating information into the vote, which is the upstream cause of C-2 and C-3.

### Impostor (Lens D)

- **Kill path never reads `fellow_impostor_ids` (D-D-1, high):** the field is plumbed into perception (`observation/service.py:101`) but `agents/tactical/impostor_policy.py::_scored_targets` (lines 264-329) ranks every sighted player with no teammate filter — the deferred Wave-2/J-5 wiring. This is the code-level root cause of the friendly-fire trend.
- **Zero teammate corroboration (D-D-2, medium):** impostors authored 28 corroboration claims, 0 supporting a fellow impostor (20 crew, 8 self); in all 6 dual-impostor meetings, not once did an impostor build cover for the teammate. Wave-2 baseline = 0/6.
- **Impostors verbally accuse their own teammate (D-D-3, medium):** the vote-firewall holds (0/57 ballots target a teammate) but free-text accusation claims do not — 4 teammate-accusations (seed 1 p-7→p-4, seed 10 p-2→p-6, seed 20 p-1→p-5, seed 7 p-6→p-7). A transcript-level tell the firewall masks.

## 6. Time-waste findings

**No wall-clock data exists in the replays — all time-waste is reasoned purely from token sinks and call/round counts, not latency.**

- **3 dead games cost ~127,121 input tokens (4.6% of the set)** on runs that never reach `game_over` (E-E-1): seed 25 in=59,840; seed 36 in=3,207; seed 40 in=64,074. Recovered for free once gp-2 lands.
- **56 wasted kill actions** (167 issued vs 111 resolved), of which 16 are cross-room rejects (MECH-B-2) and 37 are the losing half of mutual teammate kills (MECH-B-1 / B-B-2).
- **LLM spend is concentrated and bimodal (B-B-3, high):** all 1,075 calls occur inside the 51 meetings (~21.1 calls/meeting); tick play is deterministic. 13/50 games have zero meetings and **12/50 (24%) consume zero input tokens** — a quarter of the set exercises the LLM not at all yet still produces winners (incl. 3 of 9 impostor wins). Games with a meeting avg 75,352 input tokens vs 247 without. Aggregate: input 2,791,243 / output 162,654 over 1,075 calls.

## 7. Metric soundness, coverage & balance

- **Balance is degenerate (F-F-1, blocking):** the 76% crew baseline is an artifact of impostor self-destruct, not crew skill (see §4). Any Wave-1 A/B on win-rate measures self-destruct frequency, not detection quality, until gp-1 lands. At minimum, stratify the win split by self-destruct so an A/B compares like-for-like.
- **vote_correctness rests on n=3, all confounded (F-F-2, high):** the 3 "correct" impostor ejections (seeds 28, 43, 45) are all the lone-surviving impostor caught *after self-destructing its partner* (10-11 contradictions each). A rate of 1.0 measures crews finishing off a self-destructed lone impostor, not multi-impostor deduction. Do not gate Wave-1 on this rate at n=3; report a secondary signal ("contradictions flagged but ignored" — 36/45 SKIPPED meetings had ≥1 contradiction yet no ejection).
- **Accusation calibration has no tail signal (F-F-3, high):** ~94.5% of 182 accusation samples sit in deciles [0.5,0.8); ballots cluster ~70% at 0.85. ECE is computed from 3-4 populated bins with no low/high anchors — ECE deltas are unreliable for this provider. Report per-bin counts alongside ECE; consider coarser bins.
- **meeting_rate sound but its split is a catch-all (F-F-5, low — verifier-adjusted from medium):** `meeting_rate` = 37/50 = 0.74 is computed correctly and clears the 0.60 Stage-A gate. But the committed report shows `body_report_meetings: 22, emergency_meetings: 29` while all 51 meetings are in fact report-triggered — `emergency_meetings` is a documented catch-all (true emergency-button UNION body-report meetings whose triggering report lacked a `FoundBodyObservation`) and must NOT be read as a positive emergency count. Also: 88% of meetings SKIP, so "reached a meeting" overstates "meeting did something." Pair meeting_rate with the SKIPPED/EJECTED breakdown.
- **cost_dashboard zeroed on Ollama (F-F-6, informational):** $0.00 across the board; mean_cost_per_game and per-model dollar breakdowns carry no signal and cannot anchor the DESIGN.md ~$0.20/game target — use token counts as the cost proxy. Seed coverage (kills/rooms/meetings) is otherwise healthy.

## 8. Improvement proposals

### gp-1 — Make the impostor kill policy teammate-aware (and decide engine friendly-fire guard)
- **Finding ids:** MECH-B-1, A-A-1, B-B-1, B-B-2, D-D-1, F-F-1, F-F-2
- **Scope sketch:** Filter `self_state.fellow_impostor_ids` out of `_scored_targets` in `agents/tactical/impostor_policy.py` (lines 264-329) before ranking — the field is already on the observation packet (`observation/service.py:101`), this is the deferred Wave-2/J-5 wiring. Add an impostor coordination heuristic so two impostors don't both rush a kill in the same room/tick (the tick-1 mutual case). Separately decide against DESIGN.md §3 whether `engine.rules.resolve_kill` should reject an IMPOSTOR target (defense-in-depth so a buggy/LLM policy can never self-sabotage). **Reproduce:** seed 4 tick 1 — p-5(IMPOSTOR) and p-6(IMPOSTOR) both spawn alone in CAFETERIA and each emit `{type:kill, target:<the other>}`; p-5 resolves, p-6's is rejected "player is dead"; game ends CREWMATES/CREWMATE_TASKS @tick 18. Also seed 0 tick 7 (mid-game, MEDBAY, non-mutual). **After fix, re-record the 7p2i set** — the 38-9 split and all derived balance/vote_correctness/calibration metrics are untrustworthy until then.
- **Priority:** urgent (blocking — address before Wave 1)

### gp-2 — Fail-soft on malformed meeting statements (non-chronological alibi)
- **Finding ids:** E-E-1, A-A-2, F-F-6
- **Scope sketch:** Two independent fixes: (1) parse-tolerance — when an `AlibiClaim` has `from_tick > to_tick`, swap the bounds (or coerce to a 1-tick window at `to_tick`) and retry once; (2) fail-soft at the meeting level — a single rejected `Statement` degrades to a missed-deadline placeholder (the mechanism already used elsewhere) and the meeting/game continues to `game_over`, never aborting the run. **Reproduce:** seed 36 meeting-0 @tick 11 — qwen2.5 emits `AlibiClaim from_tick=8, to_tick=1`; the Statement validator raises `ValidationError "AlibiClaim tick range must be chronological"`; the LAST jsonl record in `replay-seed-36.jsonl` is `kind=failed_call` with no `game_over`. Identical on seed 25 (@tick 11, meeting-1) and seed 40 (@tick 14, meeting-1). Recovers 3 games + ~127K tokens.
- **Priority:** urgent (blocking — address before Wave 1)

### gp-3 — Gate impostor kill intent on co-location
- **Finding ids:** MECH-B-2
- **Scope sketch:** Before emitting a kill action, check the target is in the actor's current room (the orchestrator already knows co-location). Reduces wasted impostor turns and the rejection noise in the action stream. Cheaper than gp-1 and independent of it. **Reproduce:** seed 9 ticks 2/6/9 — p-7/p-7/p-2(IMPOSTOR) kill rejected "kill requires same room"; also seed 1 tick 2 p-7, seed 34 ticks 2/7 p-6.
- **Priority:** pre-wave-1

### gp-4 — Wave-1 crew-intelligence: down-weight lone body-proximity sightings, calibrate vote confidence, beat the §4.6 SKIP default
- **Finding ids:** C-C-1, C-C-2, C-C-3, C-C-5, B-B-4
- **Scope sketch:** On the meeting/voting prompt + aggregation (not the engine): give voters a body-proximity prior that distinguishes "present at scene" from "is the killer" (a kill leaves the killer free to move, so a lone `alibi_vs_sighting` near a found body is weak evidence — feed the agent body-discovery-tick vs suspect-sighting-tick). Tie `VoteBallot` confidence to evidence quality (distinct corroborating signals / kill-witness chain) instead of the habitual 0.55/0.85 enum — even passing the numeric suspicion-graph value through to the confidence field would inject real variance. Bias away from reflexive SKIP when a contradiction clearly names a subject AND a second independent signal corroborates, so genuine cases cross 0.60 while lone proximity sightings (C-1) stay below it. **Track** vote_ballot_ece (target <0.2 from 0.52), the SKIP-with-flagged-impostor count (target <22/45), and `ejection_accuracy` as Wave-1 regression gates. **Reproduce (wrong eject):** seed 49 meeting-0 tick 15 — p-5(IMP) killed partner p-6, p-2(CREWMATE) sighted in EAST_HALL flagged by 16 `alibi_vs_sighting` contradictions, ejected @0.85. **Reproduce (missed impostor):** seed 32 meeting-0 tick 8 — contradiction names living impostor p-5, all 6 ballots SKIP@0.55.
- **Priority:** pre-wave-1 (this IS the Wave-1 target; scope it against this baseline, run after the set is re-recorded post gp-1/gp-2)

### gp-5 — Raise body-report rate so bodies reliably trigger meetings (eval coverage)
- **Finding ids:** B-B-5, B-B-3
- **Scope sketch:** Examine the deterministic report policy: crewmates co-located with a body should report at a higher rate (or make reporting LLM-mediated). Currently ≥54% of bodies go unreported and 24% of games invoke the LLM zero times, so a quarter of every run is dead weight for the intelligence signal. Track meeting-rate and zero-meeting-game share as coverage metrics; consider seeding/parameters that raise the share of games that reach a meeting. **Reproduce:** seed 3 — 3 kills, 0 meetings, 0 input tokens; seed 41 — 3 kills, 0 meetings (and an impostor win on a zero-LLM game).
- **Priority:** opportunistic

### gp-6 — Wave-2 impostor coordination baseline (corroboration + narrative firewall)
- **Finding ids:** D-D-2, D-D-3, D-D-4, D-D-5
- **Scope sketch:** Wave-2/J-5 work, recorded here against a concrete baseline. (1) Use `fellow_impostor_ids` in the impostor meeting prompt to emit a corroboration claim supporting the live teammate when it has filed an alibi/report (baseline: 0 teammate-corroborations / 6 dual-impostor meetings). (2) Filter teammate ids out of accusation-claim `against` candidates at the narrative layer (mirror the vote-firewall; baseline: 4 teammate-accusations). (3) Scope net-new vent/sabotage/fake-task behavior (baseline: impostors emit only move/wait/kill). Track `supports-IMPOSTOR / dual-impostor-meetings` and alibi `survival_rate` (currently 57.4%) as effect metrics. **Reproduce:** seed 1 meeting-0 — both impostors p-4 & p-7 alive and speaking, 0 corroboration of teammate, and p-7 free-text-accuses teammate p-4 @0.7.
- **Priority:** opportunistic

### gp-7 — Eval reporting hardening (no code-behavior change)
- **Finding ids:** C-C-4, F-F-2, F-F-3, F-F-5, F-F-6, A-A-3
- **Scope sketch:** Reporting/interpretation fixes so Wave-1 readers aren't misled: (a) add a derived `ejection_accuracy` field (impostor_ejections / total_ejections = 3/6 = 0.5) next to `vote_correctness_rate=1.0`; (b) report `vote_correctness` with an explicit small-n caveat (n=3) and a secondary "contradictions ignored" signal; (c) report accusation-calibration per-bin counts alongside ECE and flag it low-power under qwen2.5; (d) pair `meeting_rate` with the SKIPPED/EJECTED split and stop reading `emergency_meetings` (29) as a positive emergency count — do not add an emergency-revival feature without first persisting a real `trigger_kind` on the replay record; (e) document `cost_dashboard` as informational-only under Ollama (use token counts); (f) keep `first_zero_impostor_tick == game_over_tick` as an automated extract self-check to catch any §6.3 regression. **Reproduce:** committed `replays/samples/7p2i/tournament-eval-report.json` — `vote_correctness_rate=1.0` with `crewmate_ejections=3`; `meeting_rate` block shows `emergency_meetings:29` despite all 51 meetings being report-triggered.
- **Priority:** opportunistic

## 9. Lens coverage notes

- **Lens A — Engine rule-correctness:** Examined every game's win attribution vs an independently reconstructed final alive-set (roles only from FACTS JSON), the win-condition order in `engine/win_conditions.py`, the kill validator in `engine/rules.py`, ejection-role accuracy, the §6.3 gap (`first_zero_impostor_tick` vs `game_over_tick`), zombie continuation, meeting-trigger validity, report-body validity, phantom bodies, and the 3 no-game-over games. Traced friendly-fire into the impostor tactical policy and perception layer. Did NOT independently re-verify the HARD mechanical rejections beyond confirming replay tick.actions contain more kill actions than resolved kills (the surplus are engine-rejected) — those go straight to synthesis. Did not assess transcript quality, vote correctness, or token waste.
- **Lens B — Gameplay trends:** Examined FACTS aggregates + all 50 per-game records with replay cross-checks for kill mechanics and meeting trigger semantics: win split, win-reason distribution, kill patterns (rooms/ticks/roles/IoI), meeting patterns, task-vs-parity timing, role-slot correlations, body-report rate, token/call distribution as a time-waste proxy. Did NOT re-flag the §6.3 gap or hollow-meeting timeouts as new defects (neither recurs), audit hard-rule violations, assess transcript-level statement quality, or measure wall-clock latency.
- **Lens C — Crew decision quality:** Examined all 51 meeting transcripts + ballots cross-referenced with FACTS ground-truth roles; all 6 EJECTED meetings in full; all 45 SKIPPED meetings to test §4.6 net effect; both calibration curves (accusation_claim ECE 0.31, vote_ballot ECE 0.52) read from the committed report and re-derived from raw confidences; §4.6 rule text in `vote_ballot.j2` and definitions in `eval/vote_correctness.py` / `eval/accusation_calibration.py`. Did NOT assess impostor kill-target selection, meeting-trigger/quorum mechanics, report quality, token/cost, or the contradiction-detector's internal correctness (treated its flags as given).
- **Lens D — Impostor behavior & coordination:** Categorized all 111 kills by killer/victim role (39 IoI) and traced the root cause to `impostor_policy.py::_scored_targets` ignoring `observation/service.py` `fellow_impostor_ids`; meeting coordination (vote-firewall 0/57, free-text accusations 4, corroboration 0/6); the vent/sabotage/fake-task gap; the 57.4% alibi-survival figure from the committed report. Roles always from FACTS JSON, never inferred. No latency claims. Did NOT assess crew intelligence, kill-scoring tuning, meeting-trigger rates, or the 3 failed_calls beyond confirming they don't distort the kill findings.
- **Lens E — Performance & time-waste:** Examined the failed_call chronology bug (instances + game-abort impact + wasted tokens), the R=2 statement-phase token sink, full-deliberate-then-SKIP meetings, degraded missed-deadline entries, empty/timeout markers. All token figures from FACTS aggregates and per-call input/output_tokens — NO wall-clock; time-waste reasoned purely from token sinks + call/round counts. Did NOT examine tick-phase LLM call costs in detail, LLM output correctness, or the §6.3 gap / hollow timeouts (do not recur). Roles from FACTS JSON.
- **Lens F — Metric soundness, coverage & balance:** Read all 5 tournament-report metric modules + `eval/balance_eval.py` and cross-checked each against FACTS JSON and raw transcripts (sample sizes, confidence distributions, denominators, documented caveats); computed per-game kill/meeting/room distributions and failed_call recurrence; traced the 38/9 split to the impostor self-destruct mechanic. Did NOT re-audit hard-rule violations, transcript reasoning quality, leak-firewall correctness, per-agent behavior, or root-cause the kill-target-selection code.
