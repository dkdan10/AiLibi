# Phase 13 — Pre-ML grounding fixes (rubric repair → deduction rework)

Goal: make the substrate SOUND before Phase-C ML. The 2026-06-20 grounding audit
(`experiments/lab/report-grounding-audit.md` — 26-agent, adversarially verified; lands on main via
PR #181) found the **rubric is unsafe as raw ML fitness**: three of four scored terms (R2/R3/R7) have
verified perverse gradients and the one valid term (R1) is untrainable by the tactical layer Phase C
trains, so a raw `_game_interestingness` inner-loop would optimize noise and degeneracy.

**13.1 (rubric repair) is DONE** (merged PR #182; the three perverse gradients verified gone). The rest is
**Wave B — the deduction/information rework** that makes the rubric MEASURABLE (R7 is 0/50 today because the detector
only emits WEAK firsthand flags). Planned by the `phase-b-plan` workflow (`experiments/lab/report-phase-b-plan.md`):
the SPINE is a meeting-time **inferential contradiction detector** (a new STRONG, transcript-reconstructed flag class)
that lights R7 on a **$0 re-extraction of the committed replays — before any re-record** (the extractor re-runs
`detect_contradictions` over the recorded transcript). Sequence: detector (13.2–13.5) → breadcrumb-render + prompt
rework (13.6) → graduated testimony-spread (13.7) → **asymmetric visibility** (13.8) → optional two-phase reasoning
(13.9) → ONE combined re-record (13.10). Every pre-re-record task validates by **re-extracting committed replays**
(R7 climbs, every STRONG flag role-gated to a true impostor, R4 floors hold); one combined re-record at the end
(cadence doctrine). **13.2–13.4 are elaborated as full contracts below; 13.5–13.10 are the roadmap, elaborated to full
contracts immediately before each dispatch (they depend on interfaces the spine builds).**

**Owner decisions (taken with the workflow's recommended defaults — override if desired):** (1) **Visibility = ASYMMETRIC**
crew `same_room_only` / impostor `same_room_and_adjacent` — probe-validated the impostor is NOT re-blinded
(`visibility_resim_asymmetric.py`: kills 168 / wins 11 ≈ baseline 165 / 11, vs the symmetric flip's crater to 141 / 5);
ships AFTER the detector, balance gated at the real re-record (the fake sweep cannot read the deduction-side swing).
(2) New STRONG flags use **full-0.3 only on a two-source conjunction**; a lone inferential atom stays sub-gate (informs,
cannot eject alone). (3) Testimony graduated-spread lands AFTER the detector (13.7). (4) Two-phase reason→emit is
OPTIONAL, gated on an offline qwen husk/length test (13.9). (5) $0 gate to greenlight the re-record = **R7 > 0 on ≥2–3
seeds with ZERO STRONG-on-crewmate** (gp-3 watch-the-games is a BLOCKING manual check).

The **Phase-C fitness-architecture** decisions (use the FO-6 LLM-free physical-suspicion RANK as the inner-loop objective;
use the repaired rubric ONLY as a held-out real-LLM SELECTION gate; mandate watch-the-games) are recorded in the ML plan
memory and belong to **Phase-C entry, not this phase**.

All Phase-13 rubric work is **offline** (reads committed replays; **NO re-record**); the firewall and
byte-determinism are untouched.

---

### Task 13.1 — Repair the rubric scorer (R2/R3/R7 perverse gradients)
**Branch:** `phase-13-rubric-repair`
**Depends on:** none
**Section refs:** experiments/lab/report-grounding-audit.md (the audit findings + punch-list; on main via PR #181); experiments/lab/rubric_score.py; eval/meeting_quality.py; audits/workflows/extract_gameplay_facts.py; agents/strategic/../transcript.py (`is_weak_contradiction`)
**Complexity:** Integration
**Files in scope:**
- experiments/lab/rubric_score.py
- experiments/lab/results-rubric-score.json
- experiments/lab/report-rubric-interestingness.md
**Files NOT in scope:**
- agents/memory/beliefs.py and the detector — the inferential-suspicion path is workstream B (a later Phase-13 task), NOT this one
- the ML fitness architecture (FO-6-rank inner-loop, rubric-as-held-out-gate, watch-the-games) — Phase-C entry, recorded in the ML plan
- engine/ and the recorded replays — the rubric is computed offline from committed replays; NO re-record
- frontend/ and api/ — they consume `results-rubric-score.json` as DATA; regenerating it re-ranks Highlights with no code change

Repair `experiments/lab/rubric_score.py` so its per-game score stops rewarding degenerate play (the audit's
three verified perverse gradients), reusing signals the codebase already computes — then regenerate the
artifact and PROVE the gradients are gone. **R2 (passive-survival → anti-correlated).** Today
`survived_accused` is alive-and-not-ejected with no active gate (`rubric_score.py:270-297`), so a passive
LOSS (R2 0.6) outscores a passive WIN (R2 0.4) and R2 is anti-correlated with the total (Pearson −0.281).
Gate R2 credit on an ACTIVE-deflection event — reuse `eval/meeting_quality.py::compute_effective_deflection`'s
ACTIVE-DEFLECTED class — scoring passive/clock survival ~0.0–0.2; and report **R1 and R2 as SEPARATE outputs**
(do not let R1 swamp R2 in one scalar). **R3 (flagless-carry → rewards the railroad R4 forbids).** Today
`r3` gives 0.5 for ≥2 meetings + 0.5 for any `carry_eject`, including a flagless meeting-0 conviction of an
innocent (seed-15 scores R3 1.0; `rubric_score.py:300-305`). Require the ejected subject's rendered suspicion
to RISE across ≥2 meetings AND land on a true impostor — source from the extractor's `accumulator_trajectories`
(`extract_gameplay_facts.py`) + the firewalled role. **R7 (weak-flag presence).** Today `r7` counts raw
`n_contradictions>0` (`rubric_score.py:308`); all 112 baseline flags are WEAK `alibi_vs_sighting` (+0.08,
below the 0.60 gate, eject nobody). Count a meeting as evidence-bearing only if it carries a STRONG
(non-weak) contradiction naming a true impostor — reuse `is_weak_contradiction` (`transcript.py`) + the role;
cap per-meeting credit at 1. Also **drop `ballot_follows_chain` from any fitness aggregate** and relabel it a
diagnostic (remove the "UP-is-good" note at `rubric_score.py:227-233`) — 65% of non-skip ballots are
null-reason BY DESIGN, so it measures a coherence the meeting architecture deliberately suppresses. **Hygiene
(P2):** give `IMPOSTOR_SABOTAGE` its own `_win_shape` branch before the `startswith('IMPOSTOR')` catch-all
(`rubric_score.py:242`), and stamp the SET manifest sha (not scoring HEAD) on the lab-local
`results-rubric-score.json` write. R1's `CREWMATE_EJECT` definition is SOUND — keep it byte-identical.
**Definition of done:** R2 is gated on active deflection (passive/clock survival ≤ 0.2) and R1/R2 are reported
as separate terms; R3 credits only a cross-meeting suspicion RISE onto a true impostor (seed-15's innocent
conviction no longer scores R3 > 0); R7 counts only STRONG contradictions naming a true impostor (the
all-weak baseline scores R7 = 0); `ballot_follows_chain` is out of the fitness aggregate and labeled a
diagnostic; `IMPOSTOR_SABOTAGE` has its own win-shape; `results-rubric-score.json` is regenerated stamped with
the SET manifest sha; a VALIDATION re-run over the committed 9p2i set shows the three perverse gradients are
gone (R2 no longer anti-correlated with the total; the seed-15 R3 and all-weak R7 cases fall to 0) while
calibration at the extremes is preserved (the audit's top-3 seeds 5/47/34 still rank above the dull bottom);
R1 unchanged; NO re-record; `scripts/check.sh` is green.
**Implementation hint:**
reuse the existing signals by import — `compute_effective_deflection` (`eval/meeting_quality.py`),
`accumulator_trajectories` (the extractor), `is_weak_contradiction` (`transcript.py`) — never re-derive; keep
R1's `CREWMATE_EJECT` branch byte-identical. Emit the score as a STRUCTURED object (R1, R2, R3, R7 reported
separately) rather than only the collapsed scalar, so Phase-C can take multi-objective axes. Re-run the scorer
over the committed 9p2i set and diff the per-seed scores to confirm the intended ranking shift (perverse cases
down, genuine cases up) before regenerating the committed artifact.
**Integration risk:**
the score change RIPPLES to consumers — the front-end `/eval/rubric` + Highlights/Dashboard read
`results-rubric-score.json` (regenerate it and let the staleness guard re-stamp; no front-end code change, but
the reel re-ranks) and Phase-C will read these terms as fitness, so keep R1 byte-identical and the term names
stable. Offline-only (committed replays in, JSON out): NO engine change, NO re-record, firewall/determinism
untouched. Validate against the audit's SPECIFIC cases (the Pearson sign on R2, seed-15 R3, the all-weak R7) —
a repair that does not flip those has not fixed the gradient.
**Ready-to-paste prompt:** `agent_prompts/task-13-1-rubric-repair.md`

---

## Wave B — deduction/information rework (makes the repaired rubric measurable)

The spine: a meeting-time inferential contradiction detector whose new STRONG flags light R7 on a **$0 re-extraction of
the committed replays** (the extractor re-runs `detect_contradictions` + `is_weak_contradiction` over the recorded
transcript — `audits/workflows/extract_gameplay_facts.py:286-293,358`). 13.2–13.4 are full contracts; 13.5–13.10 follow
as the roadmap. All firewall- and byte-determinism-preserving; one combined re-record only at 13.10.

### Task 13.2 — Meeting-time position-reconstruction helper (transcript-only)
**Branch:** `phase-13-recon-helper`
**Depends on:** none
**Section refs:** experiments/lab/report-phase-b-plan.md (the spine); experiments/lab/inference_feasibility_probe.py (the `reconstruct` logic to promote); meetings/transcript.py (`is_relevant_sighting`)
**Complexity:** Medium
**Files in scope:**
- meetings/transcript.py
- tests/meetings/test_transcript_reconstruct.py
**Files NOT in scope:**
- engine/ and observation/ — the helper reads the PUBLIC transcript only, never engine WorldState or perception
- meetings/transcript.py's contradiction-detection rules — those are 13.3 / 13.4
- agents/memory/beliefs.py — belief wiring is 13.5; no re-record

Promote `experiments/lab/inference_feasibility_probe.py::reconstruct` into a pure, replay-deterministic helper in
`meetings/transcript.py` that rebuilds each subject's STATED room-by-tick path from the meeting transcript's
`saw_player` observations ONLY (never engine state, never perception). This is the substrate every new STRONG
inferential rule (13.3 / 13.4) consumes. No behaviour change — pure helper + unit tests only.
**Definition of done:** a pure function in `meetings/transcript.py` reconstructs per-subject stated paths from transcript
Observations alone (no engine/perception/observation import); a unit test over a hand-built transcript yields the
expected paths and asserts no engine import; the function is deterministic (run twice → byte-identical); no recording or
replay touched; `scripts/check.sh` is green.
**Implementation hint:**
port the probe's `reconstruct` semantics (engine actor-id order) but over STATED sightings, not engine truth; keep it a
pure function (transcript in → paths out, no side effects); reuse `is_relevant_sighting` for which sightings count.
**Ready-to-paste prompt:** `agent_prompts/task-13-2-recon-helper.md`

### Task 13.3 — Cross-speaker alibi_conflict promoted STRONG (B2)
**Branch:** `phase-13-strong-cross-speaker`
**Depends on:** 13.2
**Section refs:** experiments/lab/report-phase-b-plan.md (B2); experiments/lab/report-grounding-audit.md (the "add an inferential path" P1); meetings/transcript.py (`is_weak_contradiction`, the weak guards); audits/workflows/extract_gameplay_facts.py (re-extraction)
**Complexity:** Integration
**Files in scope:**
- meetings/transcript.py
- tests/meetings/test_contradictions.py
**Files NOT in scope:**
- the reconstruction helper (13.2 — consumed, not modified)
- agents/memory/beliefs.py — the belief delta for the new STRONG class is 13.5
- engine/ and the recorded replays — re-extraction only; NO re-record

In `meetings/transcript.py`, stop appending the WEAK marker to a genuinely-independent cross-speaker `alibi_conflict`
(two distinct non-subject speakers placing the same subject in two rooms over overlapping ticks). KEEP the adversarial /
self-pair / narrow / boundary weak guards VERBATIM (the adversarial guard exists because an impostor weaponised a
counter-alibi). Promote ONLY genuinely-independent cross-speaker conflicts → `is_weak_contradiction` returns False → the
extractor stamps `strong=True` → R7 lights on a pure re-extraction of the committed replays.
**Definition of done:** an independent cross-speaker `alibi_conflict` no longer carries the weak marker (the existing
weak guards unchanged + tested); RE-EXTRACTING the committed 9p2i replays and re-running `experiments/lab/rubric_score.py`
shows R7 > 0 on ≥ 2 seeds with EVERY new STRONG flag role-gated to a TRUE impostor (≈ 0 naming a crewmate, the gp-3
watch-the-games eyeball is a BLOCKING check); the wrong-ejection count does NOT rise vs the baseline (R4 floor); $0, NO
re-record; `scripts/check.sh` is green.
**Implementation hint:**
the flag simply carries no weak marker → `is_weak_contradiction` returns False → the extractor stamps `strong=True`; do
NOT touch `is_weak_contradiction` itself and keep the adversarial/self-pair/narrow/boundary guards byte-identical;
validate by re-extracting the committed replays (no recording changes).
**Integration risk:**
a STRONG flag that names a CREWMATE is a false positive that both Goodharts R7 and risks a wrong ejection (R4) — role-gate
every new STRONG flag and count STRONG-on-crewmate (must be ≈ 0); the adversarial weak-guard MUST stay verbatim or the
impostor games it; this changes the EXTRACTOR's output on re-extraction, NOT any recording — byte-determinism and the
firewall are untouched and there is NO re-record.
**Ready-to-paste prompt:** `agent_prompts/task-13-3-strong-cross-speaker.md`

### Task 13.4 — alibi_vs_physical STRONG from reconstructed testimony (B3/B4)
**Branch:** `phase-13-strong-physical`
**Depends on:** 13.2, 13.3
**Section refs:** experiments/lab/report-phase-b-plan.md (B3/B4); experiments/lab/inference_testimony_probe.py (the 13.4-ceiling probe) + inference_feasibility_probe.py; meetings/transcript.py (the 13.2 `reconstruct_stated_paths` helper, `is_relevant_sighting`)
**Complexity:** Integration
**Files in scope:**
- meetings/transcript.py
- tests/meetings/test_contradictions.py
**Files NOT in scope:**
- perception-time deltas — the firewall exposes no per-player liveness channel, so ALL absence/last-seen inference lives
  in the meeting layer over public testimony only
- agents/memory/beliefs.py (13.5); engine/ and recordings — NO re-record

**This task is THE R7 lever.** The 13.3 $0 gate confirmed R7 stays 0/50 from promotion alone — the committed transcripts
hold 111 `alibi_vs_sighting` + only 1 (guarded, crewmate-naming) `alibi_conflict`, so 13.3 had nothing to promote. 13.4
GENERATES the STRONG flags. Add a new `alibi_vs_physical` contradiction kind in `meetings/transcript.py`, emitted from
the 13.2 `reconstruct_stated_paths` over PUBLIC testimony: a subject whose stated alibi is **physically contradicted** by
independent placements over its tick range, or who is the last speaker-placed party with the victim before the body. Do
NOT rely on same-tick clashes — the ceiling probe found those are rare (~2); the lever is the reconstructed-path
impossibility + last-seen-with-victim. **THE CRUX (role-gating): flag only a genuinely CONTRADICTED alibi, NEVER mere
two-source co-placement.** The ceiling probe found the material exists (4.0 placements/meeting; 26 impostor-subjects
placed by ≥2 independent speakers) — but ALSO **28 CREWMATE-subjects with the same two-source coverage**, so a detector
that fires on co-placement (rather than on a genuine physical contradiction of the subject's OWN alibi) will
false-positive on crew. Emit STRONG ONLY under the TWO-SOURCE conjunction (the subject's uncorroborated alibi AND an
independent contradicting placement); a lone atom emits at the weak/mid band. DROP all perception-time forms (no liveness
channel exists). Reuse `is_relevant_sighting` + endpoint-tick exclusion.
**Definition of done:** new `alibi_vs_physical` STRONG flags are emitted from `reconstruct_stated_paths` (public testimony
only — no engine/perception); RE-EXTRACT + `rubric_score.py` shows **R7 > 0 on ≥2–3 seeds with EVERY STRONG flag
role-gated to a true impostor and ZERO STRONG-on-crewmate** (role-gating is the make-or-break given the 28 crew two-source
cases; gp-3 watch-the-games is a BLOCKING manual check); an assertion test confirms no flag references a placement not
traceable to a transcript `saw_player`; a lone atom cannot reach the §4.6 gate alone (only the two-source conjunction
does); $0, NO re-record; `scripts/check.sh` is green.
**Implementation hint:**
consume `reconstruct_stated_paths` (returns `{subject -> (StatedPlacement{tick, rooms, speaker, event_id}, ...)}`); a
STRONG flag = the subject's OWN alibi is physically impossible given ≥1 INDEPENDENT (different-speaker, non-accuser)
placement over the alibi's tick range, OR last-speaker-placed with the victim pre-body — never co-placement agreement;
single atoms weak/mid; reuse `is_relevant_sighting` + endpoint-tick exclusion; no perception-time delta.
**Integration risk:**
the 28 crew two-source cases are the Goodhart/R4 trap — a STRONG flag on a crewmate is a false positive (it games R7 AND
risks a wrong ejection), so the contradiction MUST be against the subject's own alibi, role-gated + counted (the gate's
zero-STRONG-on-crewmate is the guard). 13.4 carries the WHOLE R7 outcome (13.3 was a no-op), so if the gate yields thin
R7 or ANY crew false positive, STOP — that is the refine/re-sequence signal, not a reason to weaken the role-gate.
Firewall: every placement MUST trace to a public `saw_player` (a leak test does not scan the belief layer, so the
traceable-to-transcript assertion test is the guard). NO re-record; byte-determinism intact.
**Ready-to-paste prompt:** `agent_prompts/task-13-4-strong-physical.md`

---

### GATE FINDING 2026-06-21 — the detector spine is BUILT but the committed data is BARREN

With 13.2–13.4 merged, the 13.4 $0 re-extract gate is the pivot: re-extracting the committed 9p2i replays yields **0
`alibi_vs_physical` flags and R7 = 0/50** — NOT because the detector is wrong (13.4's own test fires the kind on a
constructed case; it is firewall-clean + role-gated, 0 false positives) but because the committed transcripts hold **no
inferential-deduction signal to mine** (111 weak firsthand `alibi_vs_sighting`, ~0 multi-witness contradictions). You
cannot mine a signal the game never generated. **So the $0-re-extract path is exhausted; the lever is the GAME producing
richer testimony** — asymmetric visibility (13.8, crew must infer not witness) + the prompt rework (13.6, crew STATE more
sightings) + testimony-spread (13.7). The detector (13.2–13.4) is done and dormant; it lights R7 only once the game feeds
it richer testimony, which is **real-Ollama-generated → tested by a SMOKE re-record, NOT $0 re-extraction.** Do NOT refine
13.4 (it is correct — loosening it to fire on the thin data just reintroduces the crew false-positives it rightly avoids).

### Re-sequenced Wave B (game-first; the detector is built, awaiting material)

**Offline (dispatch now):** 13.5 belief-band wiring (routes the detector's strong flags into votes; unit-tested, ready
for when flags fire). **Game-changers (the R7 lever — need a real run to test):** 13.6 prompt-rework → 13.8 asymmetric
visibility → 13.7 testimony-spread. **New gate (replaces the $0 gate):** a SMOKE re-record (a few meeting-bearing seeds,
real Ollama) → re-extract → does the built detector now light R7 (>0 on ≥2–3 seeds, zero STRONG-on-crewmate)? If yes →
13.10 full re-record; if no → the deeper model / two-phase-reasoning question (13.9). **13.5 + 13.6 are full contracts
below; 13.7–13.10 stay roadmap (elaborate before each dispatch).**

### Roadmap / full contracts

### Task 13.5 — Belief-band wiring for the new STRONG inferential classes
**Branch:** `phase-13-belief-band`
**Depends on:** 13.3, 13.4
**Section refs:** experiments/lab/report-phase-b-plan.md (belief-band); agents/memory/beliefs.py (`apply_contradiction_rule`, `contradiction_lift_key`, `MEETING_CONTRADICTION_LIFT_CAP`, the `+0.05 < 0.10` gate-distance invariant)
**Complexity:** Integration
**Files in scope:**
- agents/memory/beliefs.py
- tests/agents/test_beliefs.py
**Files NOT in scope:**
- meetings/transcript.py — the detector + flag classes (13.2–13.4) are consumed, not changed
- the §4.6 gate / tally / SKIP logic — untouched
- engine/ and recordings — NO re-record

Route the new STRONG contradiction classes (cross-speaker `alibi_conflict` from 13.3, `alibi_vs_physical` from 13.4)
through `agents/memory/beliefs.py::apply_contradiction_rule` so a LONE inferential atom lands sub-gate (it INFORMS but
cannot eject alone) and only the TWO-SOURCE conjunction reaches the full `CONTRADICTION_SUSPICION_DELTA=0.3`. Preserve the
`contradiction_lift_key` dedup, `MEETING_CONTRADICTION_LIFT_CAP=0.3`, and the `+0.05 < 0.10` gate-distance invariant. No
gate / tally / SKIP change. NOTE: the new strong flags do not fire on the committed data yet (the 13.4 gate found 0) —
this is the PLUMBING that converts them to votes once the Wave-B game-changers (13.6–13.8) feed the detector richer
testimony, so it is validated by UNIT tests now (constructed flags), not by a re-extraction.
**Definition of done:** the new STRONG classes route through `apply_contradiction_rule` with a lone atom sub-gate and the
two-source conjunction at the full 0.3; a unit test confirms one lone new-class flag lifts a baseline 0.50 listener to
< 0.60 (cannot eject alone) while the conjunction crosses 0.60; `contradiction_lift_key` dedup + the 0.3 cap + the
gate-distance invariant are preserved (tested); no §4.6 gate / tally / SKIP change; the existing belief + leak +
determinism tests stay green; NO re-record; `scripts/check.sh` is green.
**Implementation hint:**
extend `apply_contradiction_rule`'s existing weak/strong handling to the new kinds rather than adding a parallel path; a
lone new-class atom takes the same sub-gate inform delta as a weak flag, the two-source conjunction takes the full 0.3;
reuse `contradiction_lift_key` so atoms of one contradiction cannot stack past the cap.
**Integration risk:**
the gate-distance invariant (`+0.05 < 0.10`) is load-bearing — a lone new-class atom that reaches 0.60 alone reopens the
single-signal wrong-ejection path the weak delta closed, so keep the full 0.3 strictly behind the two-source conjunction.
Belief-layer only: no §4.6 / tally / SKIP edit, no re-record, byte-determinism + firewall intact.
**Ready-to-paste prompt:** `agent_prompts/task-13-5-belief-band.md`

### Task 13.6 — Prompt rework: elicit richer testimony + breadcrumb render + trim
**Branch:** `phase-13-prompt-rework`
**Depends on:** none
**Section refs:** experiments/lab/report-phase-b-plan.md (prompts); the 13.4 GATE FINDING above (committed testimony is too thin to mine — this is the lever that fattens it); experiments/lab/deception_battery_2.py (the local real-Qwen harness pattern) + experiments/lab/inference_testimony_probe.py (the richness metric); agents/memory/store.py; agents/strategic/prompts/{crewmate_report,accusation_round,vote_ballot,impostor_report}.j2 — **RUN LOCALLY (needs local Ollama/Qwen); file-disjoint from 13.5/13.8 so it runs in parallel.**
**Complexity:** Integration
**Files in scope:**
- agents/memory/store.py
- agents/strategic/prompts/crewmate_report.j2
- agents/strategic/prompts/accusation_round.j2
- agents/strategic/prompts/vote_ballot.j2
- agents/strategic/prompts/impostor_report.j2
- tests/agents/test_strategic_prompts.py
- experiments/lab/meeting_prompt_battery.py
**Files NOT in scope:**
- the in-band reasoning field / two-phase reason→emit — that is the gated 13.9 (keep `think=False`)
- engine/ visibility (13.8); api/ — none; NO re-record here (the testimony-richness payoff is measured at the smoke re-record)

**RUN LOCALLY (needs local Ollama/Qwen).** Unlike 13.5/13.8, 13.6's goal — does the new prompt make Qwen *state richer
sightings* — is INVISIBLE to offline checks; only running the prompts through real Qwen verifies it, and a cloud session
cannot reach local Ollama. The 13.4 gate proved the detector is STARVED (crew state only thin firsthand sightings →
reconstruction finds no contradictions, R7 0/50); 13.6 fattens the testimony the detector mines. Three changes:
(1) **elicit richer crew sightings** — rework `crewmate_report.j2` + `accusation_round.j2` so crew state WHO they saw,
WHERE, and WHEN as concrete `saw_player` observations (not vague free-text), and frame OTHERS' accounts as belief-movers —
more + more-specific `saw_player` claims are the two-source-conjunction material 13.4 needs. (2) **breadcrumb render** —
`agents/memory/store.py` emits a directional "saw X leave A→R" line for the agent's most-recent sighting per subject (pure
function of existing episodic deltas — NO packet field, firewall untouched). (3) **trim** accreted verbosity ONLY where it
removes no still-needed guard; bump the four prompt versions together. EXCLUDE the in-band reasoning field (→ 13.9; keep
`think=False`).

**Build approach — rebuild the two sighting prompts, don't patch the crowded ones.** `crewmate_report.j2` (241 lines)
and `accusation_round.j2` (315 lines) are accreted walls that bury the model's attention in noise; layering MORE
sighting-elicitation onto them makes it worse. REBUILD those two from a clean, concise base tuned for the canonical model
— **`qwen3.5:9b` with `think=False` structured output** (the deployed local model — confirmed by
`llm/ollama_client.py::DEFAULT_OLLAMA_MODEL`, the committed replays' `llm_calls[].model`, and the MANIFEST; migrated from
qwen2.5:7b in Phase 9, so ignore any older 7B reference). Ground the rebuild in **`qwen3.5:9b` structured-output
prompting best-practices — WEB-SEARCH them** (it is a recent model; do not assume its quirks), else apply the principles:
short, schema-clear, a few worked examples, no redundant imperative stacking. CRITICAL: before rebuilding, **catalog the
load-bearing guards** the existing prompts encode (each defensive patch exists because the model failed a specific way —
anti-over-skip, anti-narration, cover-consistency, the firewall lines) and carry EACH forward; the fixture loop must
regression-test the rebuild against BOTH the new goal (richer sightings) AND those failure modes (husk / over-skip / leak
/ cover-drift), so the rebuild trades crowding for clarity, NOT for regressions. `vote_ballot.j2` / `impostor_report.j2`
get the lighter trim + the belief-mover framing, not a full rebuild.

**Iterate fixture-first, not by full games (efficiency).** Build a local meeting-prompt fixture harness
(`experiments/lab/meeting_prompt_battery.py`, extending the `deception_battery_2.py` pattern): **ISOLATE the fixed
pre-meeting context** each agent has entering a meeting — reconstructed from the committed 9p2i replays (the observation
re-walk, or the context already embedded in the recorded `llm_calls` prompts) — then render the NEW template against those
fixtures and run real Qwen **one call at a time**, inspecting whether the output carries richer/more-specific `saw_player`
observations. Iterate the template on the fixtures (fast, prompt-isolated) until it does; **only then** run a few full
real-Ollama seeds to confirm it holds in-game. This isolates the prompt as the only variable and avoids waiting on whole
games per edit.
**Definition of done:** `store.py` emits the directional breadcrumb (byte-deterministic, no new packet field — leak test
unaffected); the report/accusation prompts elicit concrete WHO/WHERE/WHEN `saw_player` observations + frame others'
accounts as belief-movers; verbosity trimmed without dropping a guard; the existing prompts' load-bearing guards (anti-over-skip / anti-narration /
cover-consistency / firewall lines) cataloged and carried into any rebuilt prompt, regression-tested by the fixture loop
against the known failure modes (husk / over-skip / leak / cover-drift); the four prompt versions bumped together;
`tests/agents/test_strategic_prompts.py` re-goldened; `think=False` preserved. **LOCAL real-Qwen validation (the real
bar):** the fixture harness shows the new template yields MORE + MORE-SPECIFIC `saw_player` observations than the old on
the SAME pre-meeting contexts, and a few full real-Ollama seeds + `inference_testimony_probe.py` show testimony richness
rises (placements/meeting up from the committed ~4.0). NO re-record (the full R7 lift is the Wave-B smoke re-record);
`scripts/check.sh` is green.
**Implementation hint:**
iterate on FIXTURES first (the `deception_battery_2.py` pattern) — reconstruct one realistic pre-meeting context per test,
render the new template, run Qwen once, inspect; only after the template is dialed run full seeds. The breadcrumb render
is a pure read of the existing episodic deltas (no packet field). Keep `think=False` (the in-band reasoning field
relocates JSON into the thinking channel — deferred to 13.9).
**Integration risk:**
RUN LOCALLY — a cloud session cannot reach Qwen, so it would ship prompts BLIND to their actual effect (the exact
look-done-but-inert failure the 13.4 gate caught). The R7 lift itself is observable only at the smoke re-record; 13.6's
own bar is the fixture-harness richness gain + the placements/meeting rise on a few seeds. `think=False` is load-bearing.
Firewall: the breadcrumb render adds no packet field; bump prompt versions together so the regression pins stay coherent.
**Ready-to-paste prompt:** `agent_prompts/task-13-6-prompt-rework.md`

### Task 13.7 — Graduated corroboration-aware testimony spread (R1/R3 lever)
**Branch:** `phase-13-testimony-spread`
**Depends on:** 13.5
**Section refs:** experiments/lab/report-phase-b-plan.md (testimony-spread); agents/memory/beliefs.py (the pre-vote inform fold, `apply_meeting_evidence_rules`, `MeetingBeliefEvidence`, `TESTIMONY_INDEPENDENCE_BAR`); meetings/transcript.py (`independent_voices` — REUSED unchanged)
**Complexity:** Integration
**Files in scope:**
- agents/memory/beliefs.py
- tests/agents/test_beliefs.py
**Files NOT in scope:**
- meetings/transcript.py — the `independent_voices` derivation is REUSED unchanged
- the detector / flag classes (13.2–13.5, consumed), prompts (13.6), visibility (13.8) — file-disjoint → parallel
- the §4.6 gate / tally / SKIP — untouched; engine/ + recordings — NO re-record

File-disjoint from the in-flight 13.6 (prompts) and 13.8 (visibility); it builds on 13.5's now-merged `beliefs.py` (hence
`depends on 13.5`, the shared-file edge). Replace the flat `+0.05` pre-vote inform with a graduated spread keyed on the
`independent_voices` COUNT: 1 voice → +0.05 (BYTE-IDENTICAL to today, so crew / no-witness games are unchanged); 2
INDEPENDENT voices → +0.12 (the first gate-cross — two corroborating observation-backed accounts can now move a 0.50
listener over 0.60); 3+ → cap +0.15. Persist only the flat +0.05 across rounds (no cross-round railroad). Keep
`TESTIMONY_INDEPENDENCE_BAR=2`; the `independent_voices` derivation in transcript.py is REUSED UNCHANGED. This is the
R1/R3 lever — it converts the richer shared testimony 13.6 elicits into ejections — so gate it explicitly on R1/R3
CONVERSION, NOT the win-split (decoupled) and NOT R7 (a separate channel).
**Definition of done:** the pre-vote inform is graduated by independent-voice count (1→+0.05, 2→+0.12, 3+→cap +0.15),
persisting only +0.05; `TESTIMONY_INDEPENDENCE_BAR=2` and the `independent_voices` derivation are unchanged; a unit test
confirms the 1-voice rung is BYTE-IDENTICAL to today (crew / no-witness games unmoved), 2 INDEPENDENT voices cross 0.60,
and a single corroboration-aligned opt-in alone cannot; no §4.6 gate / tally / SKIP change; the existing belief + leak +
determinism tests stay green; NO re-record (the R1/R3 conversion lift is measured at the Wave-B smoke re-record);
`scripts/check.sh` is green.
**Implementation hint:**
thread the `independent_voices` COUNT through `MeetingBeliefEvidence` + `apply_meeting_evidence_rules` (pre_vote) and map
it to the graduated delta; keep the 1-voice path byte-identical (the regression pin); reuse `independent_voices` from
transcript.py unchanged.
**Integration risk:**
this raises the stakes of any independence-filter bypass from a harmless +0.05 to a gate-crossing +0.12, so the
`independent_voices` bar is now load-bearing — do NOT loosen it, and persist only the flat +0.05 (a persisted +0.12 would
railroad across rounds). The 1-voice byte-identical pin guards the no-regression invariant. Belief-layer only: no §4.6 /
tally / SKIP edit, no re-record, firewall + determinism intact.
**Ready-to-paste prompt:** `agent_prompts/task-13-7-testimony-spread.md`

### Task 13.8 — Asymmetric visibility: crew `same_room_only` / impostor `same_room_and_adjacent`
**Branch:** `phase-13-asym-visibility`
**Depends on:** none
**Section refs:** experiments/lab/report-phase-b-plan.md (visibility); experiments/lab/visibility_resim_asymmetric.py (the probe — impostor NOT re-blinded); engine/visibility.py (`compute_visibility_for_player`, `resolve_visibility_mode`, `visible_rooms_for_player`); engine/maps/canonical_1.yaml (`visibility_defaults`)
**Complexity:** Integration
**Files in scope:**
- engine/visibility.py
- tests/engine/test_visibility.py
**Files NOT in scope:**
- agents/ and meetings/ — the detector (13.2–13.4), belief-wiring (13.5), and prompts (13.6) are the other levers; this is the engine sight rule only
- engine/maps/canonical_1.yaml — the BASE stays `same_room_and_adjacent`; the asymmetry is role-parameterized IN CODE, not a yaml base flip (so the lights sabotage + the default stay intact)
- recordings — the balance effect is measured at the smoke re-record; NO re-record here

File-disjoint from 13.5 (beliefs.py) and 13.6 (store.py + prompts), so it runs in PARALLEL with them. Role-parameterize
`engine/visibility.py` so an observer's visibility depends on its ROLE: at BASE visibility a CREWMATE sees
`same_room_only` while an IMPOSTOR keeps the base `same_room_and_adjacent`; an ACTIVE sabotage degrade (mode != base, e.g.
lights → `same_room_only`) still degrades EVERYONE. `compute_visibility_for_player` already holds the observer (with
`.role`), so choose the mode on it. This is the genre-correct impostor information economy (the predator keeps the sight
edge; the crew must INFER) and the FORCING FUNCTION that makes the inferential detector load-bearing (crew room-only →
private kills → testimony-based deduction). Probe-validated the impostor is NOT re-blinded
(`visibility_resim_asymmetric.py`: kills 168 / wins 11 ≈ baseline vs the symmetric flip's crater 141 / 5). Firewall-clean:
an observer's sight depending on ITS OWN role leaks nothing about others' hidden info.
**Definition of done:** crew observers get `same_room_only` and impostor observers `same_room_and_adjacent` at base, with
an active sabotage degrade still applying to everyone (unit-tested for crew, impostor, and the sabotage case); state-hash
determinism + the observation leak-property + firewall import tests stay green; a fake-provider sweep confirms the impostor
is NOT cratered (kills / parity-wins hold near baseline, per `visibility_resim_asymmetric.py`); NO re-record (the
deduction-side BALANCE swing is a REAL-PROVIDER readout gated at the Wave-B smoke re-record + owner sign-off);
`scripts/check.sh` is green.
**Implementation hint:**
the seam is inside `compute_visibility_for_player` (it has the observer): when `resolve_visibility_mode` returns the base,
use `same_room_only` for a crewmate and the base for an impostor; otherwise keep the resolved mode (so an active lights
degrade still hits the impostor too) — exactly the predicate in `visibility_resim_asymmetric.py`. No yaml base change.
**Integration risk:**
OWNER BALANCE LEVER (same class as the frozen clock) — it favors the impostor (it hunts AND evades better while crew
detect less); the fake sweep only certifies "impostor not cratered", and the real swing (does it overshoot the Phase-11
~14% floor?) is a real-provider readout gated at the smoke re-record + your sign-off. Firewall: role-parameterized sight
must not leak others' hidden state — the leak-property test is the guard. Determinism: role is fixed per game, so
byte-determinism holds. Ships (re-records) AFTER the detector + 13.6 render — crew room-only needs the inferential
detector to deduce — but is BUILT in parallel.
**Ready-to-paste prompt:** `agent_prompts/task-13-8-asym-visibility.md`

#### Task 13.9 — OPTIONAL gated: parse-only reasoning sub-schema (two-phase reason→emit) (depends 13.6, 13.7)
Define a parse-only `ReasonedMeetingTurn` (reasoning + `MeetingTurn` fields); validate the LLM text against it, then
construct the RECORDED `MeetingTurn` from the non-reasoning fields ONLY so reasoning structurally never reaches the
replay. Gate adoption on an offline qwen husk/length measurement; do NOT delete the anti-narration patches until
validated. **Offline-validate:** the `deception_battery` harness on qwen (reasoning stays 2–4 lines, free_text ~1
sentence, total under the turn cap, husk rate does not rise); recorded turns carry no reasoning field. **Owner go/no-go.**

#### Task 13.10 — ONE combined re-record (9p2i + 7p2i) + close-audit gate + era-pin re-anchor (depends 13.7, 13.8, 13.9)
After all offline-validated changes land, the single combined re-record (cadence doctrine): fake-provider sweep FIRST
(balance check, incl. the 13.8 asymmetric swing), then real-Ollama re-record of both sets, regenerate the rubric
artifact, re-anchor the 15 era-pins (precedent `dbe1827`), run the close audit. **Gate:** `rubric_score.py` shows R7 > 0
on multiple seeds, R3/R1 up, R4 (inversions / wrong-eject / friendly-fire) HARD-floor clean, impostor win ≥ the
Phase-11 14% floor; abandon the branch if R1 regresses below 6/50.
