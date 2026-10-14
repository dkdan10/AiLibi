# Wave-E Plan + Contract Review

**Date:** 2026-06-22-2149
**Method:** Synthesis of 4 per-target reviews (plan + 13.13/13.14/13.15) + 1 adversarial skeptic pass, re-verified against code. Live re-extraction over the committed `replays/samples/9p2i` set confirmed the two highest-stakes findings. Findings weighted by code-grounded evidence; unsupported nitpicks discounted.
**Verdict:** **Wave E is NOT ready to dispatch.** Two independent blocking defects in 13.14 (self-contradictory contract = strict no-op, AND a missing joint-cap design that re-opens the single-witness railroad), a mis-scoped version-bump cascade in 13.13 that produces a red build, and a composed 13.13×13.14×13.7 wrong-ejection risk whose only instrument is the HELD 13.12 re-record under a mis-named gate.

---

## 1. Plan verdict

**Verdict: CONCERNS (sound spine, two unsafe load-bearing assumptions).**

What is right and empirically forced:
- **Detector-first sequencing is correct.** Probe 1 shows de-imperative-alone flips 13–38/39 ejections to SKIP (`report-forward-redesign-probes.md:29-30`); 13.13 genuinely cannot ship without 13.14 supplying real STRONG evidence. The dependency direction is right.
- **The KEY FINDINGS hold against artifacts:** the inferential detector spine is merged (`beliefs.py:603-624`), `MIN_VOICES`/`alibi_vs_physical` is an empty path on the room-only substrate (0 physical flags), corroboration craters precision 81%→67% (Probe 3), and R7=0 is a deliberate precision floor, not a config bug.
- **The bidirectional-imperative cascade pin (13.13) is real:** `vote_ballot.j2:143` renders both a MUST-eject and MUST-SKIP half and the tally reads the model's own confidence (`voting.py:208-211`).
- Holding 13.15 (rubric) until R7 is non-zero, and keeping the geomean a held-out referee never the gradient, are consistent with the grounding audit.

Where the plan is unsafe (the 81%-precision acceptance is NOT right as written):
- **The 81% acceptance conflates "not random" with "not single-signal."** The owner principle (`project_ejection_suspicion_principle`) requires corroborate-within-round AND *no single signal ejects*. A lone single-witness `alibi_vs_sighting` STRONG flag lifts the 0.5 prior to 0.80 and crosses the 0.60 gate ALONE — that IS a single signal ejecting. The plan satisfies "info-backed" (each flag is concrete) but violates "not single-signal," which the code currently enforces via the weak down-weight (`beliefs.py:54-68`, `beliefs.py:612-621`). Promoting the band straight to the full 0.3 delta is a deliberate reversal of a code-documented hard invariant, not a tuning knob.
- **The "§4.6 floor + plurality mediates the 19% crew FP" mitigation is asserted, never quantified, and contradicted by history.** The probes measured FLAG precision (50 TP / 11 FP), not ejection CONVERSION. The tally floor (`voting.py:199-213`) blocks only empty/tie/SKIP-plurality/low-confidence — it does NOT require multiple INDEPENDENT high-suspicion voters. Since every voter who sees the STRONG flag gets the same subject lifted to 0.80, voters converge on the same crew FP, producing exactly the strict plurality + ≥0.6 confidence the floor ejects on. The 13/13 historical wrong ejections happened WITH this same floor in place — the floor never stopped them; the weak down-weight did.

Net: sequencing sound; the 81% acceptance and the floor-mediation claim are unsafe assumptions that must be converted into a measured conversion probe + an anti-cascade MID-delta design before dispatch.

---

## 2. Contract 13.13 (de-imperative the §4.6 vote gate)

**Verdict: BLOCKING-FIXES** (surgically correct target, but a mis-scoped cascade that reds the build + two under-specified instructions).

Correct and load-bearing:
- The target is precise: `vote_ballot.j2:143` is the literal MUST-vote/MUST-skip imperative; `:131-137` is the `_susp`/`_max`/`_thr` derivation that MUST be preserved (it feeds the rendered evidence). Confirmed.
- "Leave `voting.py::tally_ballots` UNTOUCHED" is correct — it is the silent anti-cascade floor (`voting.py:120-213`), independent of prompt text.
- DESIGN.md §4.6/§5.5 are already reconciled to "evidence to weigh, not a directive"; 13.13 aligns code to committed design.

**Blocking — the version-bump cascade is mis-specified and will red the build.** The contract claims "two live-recorded orchestrator test pins" for `vote_ballot`. **They do not exist.** Verified:
- `tests/orchestrator/test_game.py` (the only orchestrator test in files-in-scope): **0** `vote_ballot` refs.
- `tests/orchestrator/test_replay_meetings.py:413-415` pins `accusation_round`/`crewmate_report`/`impostor_report` only; `vote_ballot` is presence-checked at `:394`, NOT versioned.
- `tests/orchestrator/test_meeting_integration.py:2320` pins `crewmate_report` only.
- The ONLY literal `assert "vote_ballot/v6" in prompt` is at **`tests/agents/test_strategic_prompts.py:1223`** — in `agents/`, NOT `orchestrator/`, and NOT in files-in-scope.
- `tests/scripts/test_manifest_writer.py:67` pins `vote_ballot/v5` (as-recorded) and will NOT break (no re-record).

An implementer who follows the contract bumps to v7, hunts two nonexistent orchestrator pins, and ships a red `check.sh` because `test_strategic_prompts.py:1223` (out of scope) fails. **Fix:** add `tests/agents/test_strategic_prompts.py:1223` to files-in-scope with an instruction to bump it to v7; drop the "two orchestrator pins" claim.

**Major — `guard_ballot_target_graph` needs an explicit UNCHANGED callout.** `meetings/manager.py::guard_ballot_target_graph` (`:2315`, called `:1662`) is a SECOND deterministic copy of the §4.6 verdict that recomputes `verdict_max >= skip_confidence_threshold` outside the prompt. It does NOT make 13.13 a no-op (it never forces SKIP→eject; returns unchanged when `verdict_max < threshold`), but a reviewer could read "de-imperative the gate" and try to soften this frozen safeguard. Add a files-NOT-in-scope bullet marking it deliberately UNCHANGED.

**Major — "pin the confidence rendering" has no code target.** The prompt renders `_max`/`_thr` only; `confidence` is a model-EMITTED output field (`vote_ballot.j2:185-186`), so there is no confidence *rendering* to pin. The real deterministic backstop is the tally's leader-confidence floor (`voting.py:211`). An implementer cannot tell whether to add a clamp, a schema field, a prompt sentence, or nothing — and a prompt-side clamp would be a NEW deterministic gate the plan does not intend. Restate as a behavioral constraint in prose ("emitted confidence must reflect the named target's rendered suspicion; may not report ≥0.60 on a sub-0.60 target") and explicitly forbid a code clamp.

**Minor:** anchor `131-149` spans load-bearing non-imperative setup — tighten to "rewrite only decision-rule prose at 140–149 (the `_max >= _thr` imperative on 143), preserving 131–137 and rule-3 reason-id machinery." Smoke success criteria need a pre-change baseline (null-reason-id share, count of under-gate/≥0.60 ballots) or "DOWN"/"NOT clustering" are unfalsifiable.

---

## 3. Contract 13.14 (promote `alibi_vs_sighting` to STRONG)

**Verdict: BLOCKING-FIXES** (two independent blockers; the contract is mutually inconsistent with its own headline metric AND missing a joint-cap design).

**Blocking #1 — the contract as written is a strict NO-OP, and its headline 54/114 is unreachable under its own instructions. Confirmed by live extraction.** I re-extracted the committed `replays/samples/9p2i` set: **111 `alibi_vs_sighting` flags, ZERO honest (non-weak).** Marker breakdown: `self-stated alibi` 52, `self-stated; endpoint-tick` 45, `self-stated; narrow` 13, `same-speaker proxy` 1. The contract says KEEP self-stated/narrow/endpoint weak → it promotes **0** flags → R7 stays 0/114 → 13.15's geomean collapses every game to 0 (its own DoD). The ONLY path to the headline 54/114 is the sweep's `promote_all_avs` config (`forward_redesign_detector_sweep.py:88-92`), which takes ALL avs subjects with **no `is_weak_contradiction` filter** (verified: the `minv` path filters, the `promote_all_avs` path does not). The headline metric and the instructions are mutually exclusive. The honest other-stated band the contract claims to "promote" is ALREADY STRONG today (`test_transcript.py:906-931` asserts `is_weak_contradiction is False` on it). **Fix:** state the real lever plainly — the change is to REMOVE `WEAK_REASON_SELF_STATED` emission for the sighting path (`_weak_signal_reasons` `transcript.py:1933` + endpoint append `:1767`), i.e. reverse the audit-9.7 self-stated down-weight for this band. If the owner wants self-stated to stay weak, 13.14 cannot light R7 and the whole Wave-E chain collapses — escalate as an explicit owner decision.

**Blocking #2 — the implementation hint points at the wrong function, and the change re-opens a code-documented anti-railroad invariant.** `is_weak_contradiction` (`transcript.py:610`) is a pure MARKER-PREFIX predicate (`:629`), not a per-kind classifier — it cannot be edited to "stop returning weak for alibi_vs_sighting." The real change site is the marker WRITER. More fundamentally, the codebase deliberately keeps single-witness physical contradictions WEAK because a lone flag at the full 0.3 reaches 0.5+0.3=0.80 and crosses the 0.60 gate ALONE — the exact pattern behind 13/13 wrong ejections (`beliefs.py:54-68`, `:612-621`; `transcript.py:513-515`). The plan frames this as "reversing the 9.7 down-weight" as if it were a tuning knob; the design treats it as a hard invariant. **Fix:** do NOT promote the lone band straight to the full 0.3. Introduce a MID delta (~0.10–0.12) lifting a lone flag to suspicious-but-sub-gate while a SECOND independent witness crosses (mirroring the `alibi_vs_physical` two-source design at `beliefs.py:608-624`). Probe 3 shows ≥2-sighting corroboration craters signal 54→14 and precision 81→67%, so the MID-delta path is the honest one. If the owner truly accepts a lone STRONG flag crossing the gate, escalate as an explicit owner decision — do not bury it under "the floor mediates it."

**Blocking #3 (skeptic, code-confirmed) — 13.14 STRONG STACKS with 13.7 testimony-spread on the same subject, no joint cap.** `meetings/manager.py:1911-1928` applies BOTH belief rules sequentially on the SAME `BeliefState`: `apply_contradiction_rule` (Rule 2; 13.14 lone avs +0.3, capped at `MEETING_CONTRADICTION_LIFT_CAP` = 0.3) THEN `apply_meeting_evidence_rules` (13.7 pre-vote spread; +0.05/+0.12/+0.15). Verified the two caps are INDEPENDENT (the lift cap is Rule-2-only) and `adjust_suspicion` (`beliefs.py:415-422`) clamps only to [0,1]. A subject both lone-STRONG-flagged AND named by 2+ accusers reaches 0.5+0.3+0.12 = **0.92** rendered into the ballot — and 13.7's spread is itself a convergence mechanism (every listener gets +0.12), amplifying exactly the multi-voter crew-FP convergence the plan's floor-mediation claim hand-waves. 13.14 `Depends-on` 13.7 but neither contract models the stacking. **Fix:** add a joint per-subject cap across Rule-2 + testimony-spread (or design the MID-delta from #2 so the stacked total cannot clear the gate on a single-witness contradiction), and quantify the stacked worst case before dispatch.

**Major — "affects ONLY belief Rule 2's delta" is false; ≥4 live readers re-run the detector.** `eval/meeting_quality.py:1891-1896` re-runs `detect_contradictions` + `is_weak_contradiction` LIVE (offline eval/quality counts shift ~54 flags weak→strong immediately); `api/replay_loader.py:1743` sets spectator solid-vs-dashed severity; `api/schemas.py:550` re-derives class at load; `audits/workflows/extract_gameplay_facts.py:286` re-runs it live — and that last one is the SAME path 13.15 re-extracts against, so 13.14↔13.15 share a hidden `is_weak_contradiction` coupling neither contract names. **Fix:** enumerate the downstream readers; mark the eval-metric shift as expected (not a regression).

**Major — DoD over-claims test impact.** Promoting self-stated breaks committed-bytes re-derivation pins the contract doesn't flag: `test_self_stated_alibi_vs_third_party_sighting_is_weak` (`test_transcript.py:368`), `test_surviving_endpoint_flags_are_weak_banded` (`:1664-1680`, asserts `endpoint_weak==58`), plus the `TestCommittedBytesSeedPins` cluster (`:1655,1678,1753,1898`). "State-hash verify stays green" is TRUE (reads recorded actions) but is conflated with the classification pins that WILL invert. **Fix:** enumerate the pins that must re-anchor; separate "state-hash green" from "classification pins flip."

**Major — endpoint-tick interaction unaddressed.** 58 of 111 avs flags carry endpoint-tick atop self-stated. If endpoint stays weak, the promoted set is ~53, not 54, and the 81% precision (48 imp/11 crew) was measured over ALL 111 (`promote_all_avs`), not the promoted subset — the precision figure may not hold. **Fix:** decide whether endpoint/narrow also promote; re-run the sweep restricted to the actually-promoted subset before pinning "54/114 @ 81%."

**Minor:** "defense-echo" listed as a weak-guard to keep does not exist as a classification reason (it is a dedup step, `transcript.py:976,1508`) — drop it. The `contradiction_lift_key` + cap (`beliefs.py:662-674`) does already prevent N sightings stacking past one strong delta against the SAME alibi — a real safety property the contract benefits from but doesn't mention.

---

## 4. Contract 13.15 (geomean rubric)

**Verdict: MINOR-FIXES** (motivation verified-true, data exists, but the design report is not an implementation spec and DTO coupling is unflagged — none blocking *given* 13.14 is fixed first).

Correct and verified:
- Motivation is real: `results-rubric-score.json` per_game[0] (seed-0 CREWMATE_TASKS stopwatch) scores 62.5 with R2=1.0/R3=1.0 masking a non-decisive R1=0.5 — the additive-masking pathology; a geomean sinks it.
- The 13.14 dependency is mechanically sound: the extractor re-runs `is_weak_contradiction` LIVE (`extract_gameplay_facts.py:286`), so re-running it after 13.14 lights R7 from committed replays with no re-record.
- All D1–D4 raw signals genuinely exist and are per-game reachable (`rendered_suspicion_by_target`, `suspicion_graph_by_voter`, `prevote_folds`, `plurality_margin`, `first_zero_impostor_tick`); `plurality_margin` is a guarded fail-loud field (`extract_gameplay_facts.py:1452` → `rubric_score.py:330-339`).

**Major — `report-rubric-design.md` is a design narrative, NOT an implementation spec.** It specifies D1–D4 SIGNALS + the `floor_multiplier × geomean_weighted(D1..D4)` SHAPE but contains ZERO numeric weights, NO `floor_multiplier` value (ambiguous "→0 / heavy dock"), NO per-dimension [0,1] mapping, NO epsilon. An implementer told to build "per report-rubric-design.md" must invent all the math. **Fix:** add a "Decisions to make (not in the report)" block enumerating: 4 geomean weights, `floor_multiplier` value (recommend hard 0 to match R4-style floors), epsilon (promote the hint's 1e-3 to spec), each Dₙ's [0,1] mapping — or freeze them in the report before dispatch. (The skeptic refines the D2 nuance: the raw suspicion data EXISTS at `extract_gameplay_facts.py:1134-1155`/`:1527`; what's missing is the separation SCALAR + mapping, so don't re-extract — just specify the formula.)

**Major — cross-scope DTO breakage unflagged.** If per_game emits D1–D4 keys or drops r1/r2/r3/r7, `RubricGameView` (REQUIRED `r1_decisive`/`r7_legible`, `api/schemas.py:933-936`) breaks at `model_validate` (`replay_loader.py:517`); `api/schemas.py` + `tests/api/test_view_model.py` are NOT in files-in-scope. **Fix:** state the intended low-risk path explicitly — per_game KEEPS emitting r1/r2/r3/r7 and the geomean only replaces the `score` value, leaving `api/schemas.py` untouched. If renaming to d1–d4, add the schema + tests to scope.

**Minor:** the R7-lit facts artifact isn't committed — add one line: "re-run `extract_gameplay_facts.py` against the committed replays AFTER 13.14 patches `is_weak_contradiction`; score that fresh facts JSON." The §6 mirror is under-specified (filename, which of the 4 checks are machine-asserted vs PR-narrative spot-reads). The `_facts()` test fixture (`test_view_model.py:684`) lacks the D-fields and may hit the fail-loud at `rubric_score.py:330` — extend it or keep D-dims tolerant of a minimal fixture.

**Internal contradiction to reconcile (raised by plan review):** 13.15's DoD says it "lands AFTER 13.14 lights R7 (else the geomean collapses to 0)" and `Depends-on 13.14`, but `report-rubric-design.md` D1–D4 was explicitly designed to ROUTE AROUND R7 (`:11`/`:68`/`:115`; D2 "supersedes R7's dead strong-flag requirement"). The R7-dependence belongs to the audit's older additive-R7 D-1, which conflicts with the Wave-C decision (`tasks/phase-13.md:441-442`) that R7/R3 are DEAD. The additive form at `rubric_score.py:528` still has an r7 term (verified) — that is the source of the confusion. **Fix:** pick one. If D1–D4 (eject_decided/separation/deflection/arc) is the target, D2's reachability does NOT depend on 13.14 lighting R7 — drop the "Depends on 13.14 / else collapses to 0" framing and 13.15 can land independently. Make the contract self-consistent before dispatch.

---

## 5. Cross-contract + skeptic findings

- **13.13 × 13.14 compose ONLY at the HELD 13.12 re-record, in opposite directions, and the only instrument is mis-named.** De-imperative (13.13) frees the model to weigh evidence; promoting the band STRONG (13.14) renders a lone "alibi says X, seen in Y" as legible concrete evidence — a persuadable de-imperative model converges, re-enabling the single-witness railroad the old imperative at least NAMED. Neither task's $0-offline validation (both on byte-identical OLD replays) can see this. The named gate is wrong: "friendly-fire-flat" means impostor-kills-impostor, which the ENGINE FORBIDS (`report-rubric-design.md:93`) — a structurally-immovable integrity check, NOT the wrong-ejection-of-crew metric 13.14 actually threatens.
- **13.14 STRONG + 13.7 spread stacking (no joint cap)** — see Blocking #3 above; the dominant un-modeled wrong-ejection amplifier, worse than the single-rule 0.80 path every per-task review analyzed.
- **13.14 no-op silently breaks the 13.15 chain.** If 13.14 lands as written (0 honest flags), the re-extracted facts keep R7=0 and the geomean collapses every game to 0. "Lands AFTER 13.14 lights R7" is only satisfiable if 13.14 actually promotes the self-stated band — which its own contract forbids.
- **13.13 cascade scope/instruction mismatch** — the in-scope orchestrator files have no `vote_ballot` version pin; the only breaking literal is out of scope → red `check.sh`.

---

## 6. Required fixes before dispatch (blocking)

1. **13.14 — resolve the self-contradiction.** Rewrite to REMOVE `WEAK_REASON_SELF_STATED` (+ co-occurring narrow/endpoint) emission for the `alibi_vs_sighting` path (`_weak_signal_reasons` `transcript.py:1933` + endpoint append `:1767`) — point the implementation hint at the marker WRITER, not `is_weak_contradiction` (a pure marker-predicate). Drop the false "keep self-stated weak" framing. The headline 54/114 is ONLY reachable this way.
2. **13.14 — replace the lone-STRONG promotion with a MID delta (~0.10–0.12)** so a single witness stays sub-gate and a SECOND independent witness crosses (mirror `alibi_vs_physical` two-source, `beliefs.py:608-624`). If the owner truly accepts a lone single-witness ejection, escalate it as an explicit Wave-E owner-decision line (it reverses the no-single-signal-eject principle).
3. **13.14 / 13.7 — add a joint per-subject suspicion cap** across Rule-2 contradiction lift + testimony-spread (`manager.py:1911-1928`), or design the MID delta so the stacked worst case (0.5+Δ_contra+0.12) cannot clear 0.60 on a single witness. Quantify the stacked worst case.
4. **Conversion probe before dispatch ($0 offline).** Re-tally the committed ballots/suspicion-graphs with the promoted classification and count how many of the 11 crew FPs reach strict plurality + a ≥0.6 ballot (would actually EJECT), not just get flagged. Pre-commit an abandon threshold: wrong-ejection (R4) count must not rise vs baseline. This is the Probe-1 desk-test rigor 13.14 deserves.
5. **13.13 — fix the version-bump cascade.** Add `tests/agents/test_strategic_prompts.py:1223` to files-in-scope (bump to v7); delete the nonexistent "two orchestrator pins" claim.
6. **Re-specify the held-13.12 gate.** Replace "R1-up / friendly-fire-flat" with "R1-up AND wrong-ejection/railroad-floor count flat (R4 holds) AND impostor win not < 14%." Run a real-qwen smoke that counts crew ejections traceable to a lone promoted flag; pre-commit the abandon-branch threshold.

## 7. Advisory

- **13.13:** mark `guard_ballot_target_graph` (`manager.py:2315`) deliberately UNCHANGED; restate "pin confidence rendering" as a prose behavioral constraint (no code clamp — the tally floor at `voting.py:211` is the backstop); tighten the `131-149` anchor to "rewrite 140–149 (imperative on 143), preserve 131–137"; pin a pre-change smoke baseline so "DOWN"/"NOT clustering" are falsifiable.
- **13.14:** enumerate the 4 live `is_weak_contradiction` readers (eval/quality, spectator severity, schemas, the extractor) and mark the eval-metric weak→strong shift expected; list the classification pins that must re-anchor (`test_self_stated_..._is_weak`, `test_surviving_endpoint_flags_are_weak_banded`, `TestCommittedBytesSeedPins`) and separate them from "state-hash stays green"; decide whether endpoint/narrow also promote and re-run the sweep on the actually-promoted subset before pinning precision; drop "defense-echo" from the weak-guard list.
- **13.15:** add a "Decisions to make (not in the report)" block (4 weights, floor_multiplier value, epsilon, each Dₙ mapping) or freeze them in the report; state the per_game dict KEEPS r1–r7 keys (geomean replaces only `score`) to avoid the `RubricGameView` DTO break; add the re-extraction step + input facts path; reconcile the R7-dependence (D1–D4 routes around R7 → drop the "Depends on 13.14 / collapses to 0" framing) so the contract is self-consistent; correct the D2 nuance (raw suspicion data exists, the scalar/mapping does not — don't re-extract); acknowledge the "ranks ALL eject-decided above ALL CREWMATE_TASKS" target may not be achievable with one weight vector — report in `## Decisions` rather than tuning weights to force it.
- **Owner-decision line:** is a lone concrete single-witness contradiction allowed to eject (info-backed but single-signal), or must it still require a second within-round signal? Current code = the latter (`beliefs.py:614-621`); 13.14 changes it to the former. Make this an explicit Wave-E owner decision, not an implementation default.
