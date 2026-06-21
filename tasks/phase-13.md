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
**Section refs:** experiments/lab/report-phase-b-plan.md (B3/B4); meetings/transcript.py (the 13.2 helper, `is_relevant_sighting`)
**Complexity:** Integration
**Files in scope:**
- meetings/transcript.py
- tests/meetings/test_contradictions.py
**Files NOT in scope:**
- perception-time deltas — the firewall exposes no per-player liveness channel, so ALL absence/last-seen inference lives
  in the meeting layer over public testimony only
- agents/memory/beliefs.py (13.5); engine/ and recordings — NO re-record

Add a new `alibi_vs_physical` contradiction kind in `meetings/transcript.py`, emitted from the 13.2 reconstruction over
PUBLIC testimony: a subject whose stated alibi is physically impossible given other speakers' stated sightings, or who is
the last speaker-placed party with the victim before the body. Emit STRONG ONLY under a TWO-SOURCE conjunction (the
subject's uncorroborated claim AND an independent physical placement); a lone atom emits at the weak/mid band. DROP all
perception-time forms (no liveness channel exists). Reuse `is_relevant_sighting` + endpoint-tick exclusion.
**Definition of done:** new `alibi_vs_physical` STRONG flags are emitted from transcript reconstruction (public testimony
only — no engine/perception); RE-EXTRACT + `rubric_score.py` shows R7 climbs further with every STRONG flag role-gated to
a true impostor (STRONG-on-crewmate ≈ 0, gp-3 watch-the-games BLOCKING); an assertion test confirms no flag references a
placement not traceable to a transcript `saw_player`; a lone atom cannot reach the §4.6 gate alone (only the two-source
conjunction does); $0, NO re-record; `scripts/check.sh` is green.
**Implementation hint:**
consume the 13.2 helper (stated paths); STRONG only on the two-source conjunction, single atoms weak/mid; reuse
`is_relevant_sighting` + endpoint-tick exclusion; no perception-time delta (the firewall has no liveness channel).
**Integration risk:**
firewall — every placement MUST trace to a public `saw_player`; since a leak test does not scan the belief layer, the
"traceable-to-transcript" assertion test is the guard; STRONG-on-crewmate is a false positive (Goodhart R7 / R4) →
role-gate + count; two-source-only keeps a lone reconstruction atom from ejecting alone (the wrong-ejection path the weak
delta closed).
**Ready-to-paste prompt:** `agent_prompts/task-13-4-strong-physical.md`

---

### Roadmap (13.5–13.10 — elaborated to full contracts immediately before each dispatch)

#### Task 13.5 — Belief-band wiring for the new STRONG classes (depends 13.3, 13.4)
Route the new STRONG contradiction classes through `agents/memory/beliefs.py::apply_contradiction_rule` so a LONE
inferential atom lands sub-gate (informs, cannot eject alone) and only the two-source conjunction reaches the full 0.3.
Preserve `contradiction_lift_key` dedup + `MEETING_CONTRADICTION_LIFT_CAP=0.3` + the `+0.05 < 0.10` gate-distance
invariant. No gate / tally / SKIP change. **Offline-validate:** unit test (one lone flag lifts a 0.50 listener to
< 0.60; the conjunction crosses); re-extract + `rubric_score.py` shows R4 inversions = 0 and wrong-ejection games do not
rise. $0.

#### Task 13.6 — Breadcrumb render + testimony-as-belief-mover framing + prompt trim (depends 13.5)
`agents/memory/store.py` emits a directional "saw X leave A→R" line for the agent's most-recent sighting per subject
(pure function of existing episodic deltas — no packet field, firewall untouched); add the "others' accounts are
belief-movers" framing to `vote_ballot.j2` + `accusation_round.j2`; trim accreted verbosity ONLY where it removes no
still-needed guard; bump the four prompt versions together. EXCLUDE the in-band reasoning field (→ 13.9).
**Offline-validate:** re-golden `tests/agents/test_strategic_prompts.py` at the new versions; the breadcrumb render is
byte-deterministic over a fixed episodic log; no packet field added (leak test unaffected). No re-record.

#### Task 13.7 — Graduated corroboration-aware testimony spread (depends 13.5, 13.6)
`beliefs.py`: replace the flat `+0.05` pre-vote inform with a spread keyed on the `independent_voices` count
(1 → +0.05, byte-identical to today; 2 → +0.12, first gate-cross; 3+ → cap +0.15); persist only the flat +0.05 (no
cross-round railroad); keep `TESTIMONY_INDEPENDENCE_BAR=2`; `independent_voices` derivation UNCHANGED. Gate on R1/R3
conversion, explicitly NOT the win-split and NOT R7. **Offline-validate:** the 1-voice rung is byte-identical to today
(crew / no-witness games unchanged); 2 INDEPENDENT voices cross 0.60 and a corroboration-aligned opt-in alone cannot;
dump per-meeting voice counts on the committed replays and hand-confirm independence. $0.

#### Task 13.8 — Asymmetric visibility: crew `same_room_only` / impostor `same_room_and_adjacent` (depends 13.5, 13.6)
Role-parameterize `engine/visibility.py` (`compute_visibility_for_player` keys on `observer.role`: crew → `same_room_only`
at base, impostor → base; an ACTIVE sabotage degrade still hits everyone). Firewall-clean (your sight depends on YOUR
role; leaks nothing about others). Probe-validated the impostor is NOT re-blinded (`visibility_resim_asymmetric.py`).
Ships AFTER the detector (crew room-only needs the inferential detector + the 13.6 render to deduce). **Owner balance
lever** (same class as the frozen clock). **Offline-validate:** state-hash determinism + leak test green; the
fake-provider sweep confirms the impostor is not cratered — but the deduction-side BALANCE swing is a REAL-PROVIDER
readout, gated at the 13.10 re-record, NOT pre-clearable on fake.

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
