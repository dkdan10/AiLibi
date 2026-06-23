# Agent Prompt — 13.14 Promote `alibi_vs_sighting` to STRONG (light R7 off 0/114)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.14 — Promote `alibi_vs_sighting` to STRONG (light R7 off 0/114), anchored to DESIGN.md §5.4 + §6.4 (reconciled — WEAK/STRONG classification; STRONG drives Rule 2's gate-crossing delta); experiments/lab/report-forward-redesign-probes.md Probe 3 (the live sweep: promoting `alibi_vs_sighting` STRONG = 54/114 at 81% precision; `MIN_VOICES`/co-presence is an empty path; corroboration makes it worse); experiments/lab/forward_redesign_detector_sweep.py (the validating re-extraction); meetings/transcript.py:610 (`is_weak_contradiction`), :517 (`PHYSICAL_CONTRADICTION_MIN_VOICES`), :922 (`detect_contradictions`); agents/memory/beliefs.py:659 (Rule 2 reads `is_weak_contradiction`). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-avs-strong`
**Depends on:** 13.3, 13.4, 13.5, 13.7
**Section refs:** DESIGN.md §5.4 + §6.4 (reconciled — WEAK/STRONG classification; STRONG drives Rule 2's gate-crossing delta); experiments/lab/report-forward-redesign-probes.md Probe 3 (the live sweep: promoting `alibi_vs_sighting` STRONG = 54/114 at 81% precision; `MIN_VOICES`/co-presence is an empty path; corroboration makes it worse); experiments/lab/forward_redesign_detector_sweep.py (the validating re-extraction); meetings/transcript.py:610 (`is_weak_contradiction`), :517 (`PHYSICAL_CONTRADICTION_MIN_VOICES`), :922 (`detect_contradictions`); agents/memory/beliefs.py:659 (Rule 2 reads `is_weak_contradiction`)
**Complexity:** Integration
**Files in scope:**
- meetings/transcript.py
- tests/meetings/test_transcript.py
- tests/agents/test_beliefs.py
**Files NOT in scope:**
- the committed replays — NO re-record; the recorded `contradictions` field stays, validation is a $0 RE-EXTRACTION that recomputes; the held 13.12 re-record is what bakes STRONG flags into recordings
- meetings/voting.py + the §4.6 floor — unchanged
- the belief delta wiring (`apply_contradiction_rule`) — already routes a non-weak flag to the gate-crossing delta from Wave B; only the CLASSIFICATION changes

Change the contradiction CLASSIFICATION so the **honest** `alibi_vs_sighting` set — the flags that pass the
existing weak-guards (NOT self-pair / defense-echo / adversarial / narrow / boundary / endpoint-mismatch,
which STAY weak) — is classified **STRONG**, so it drives Rule 2's gate-crossing delta (§6.3). Today
`is_weak_contradiction` marks every `alibi_vs_sighting` WEAK (the audit-9.7 precision down-weight), so
R7=0/114; the live sweep (Probe 3) shows promoting it gives R7 54/114 at 81% precision (48 impostor /
11 crew). This is a deliberate precision/recall trade — the 19% crew flags are info-backed (concrete
"alibi says X, seen in Y"), some are impostors FRAMING a crewmate, and the flag is not a verdict (the §4.6
floor + plurality mediate it). Keep `PHYSICAL_CONTRADICTION_MIN_VOICES` / the `alibi_vs_physical`
co-presence path AS-IS (the sweep proved it is an empty path — do not tune it).

**Firewall:** the detector reads only the public transcript (no privileged state); no agent-visible field is
added. **Determinism:** the classification is a pure function of the recorded transcript — a re-extraction
is deterministic, and the committed replays re-walk byte-identically (reconstruction replays recorded
outputs, it does not re-run the detector).
**Definition of done:** the honest `alibi_vs_sighting` set classifies STRONG while the weak-guards stay
weak; a $0 re-extraction of the committed 9p2i set (`forward_redesign_detector_sweep.py` style) shows R7 off
0 to ~54/114, every STRONG flag's subject role-checked (≈81% impostor; the crew FPs are logged not hidden —
spot-read 5 flagged meetings, gp-3 watch-the-games is BLOCKING); `alibi_vs_physical` / `MIN_VOICES`
UNCHANGED; detector-classification unit tests re-anchored; the committed state-hash verify stays green;
`scripts/check.sh` green.

## Implementation hint
in `is_weak_contradiction` (`transcript.py:610`) stop returning weak for an `alibi_vs_sighting` that has
passed the existing weak-guards (keep the self-pair / defense-echo / adversarial / narrow / boundary /
endpoint-mismatch carve-outs returning weak); the Rule 2 wiring (`beliefs.py:659`) already applies the
STRONG delta to a non-weak flag, so no belief-layer edit; validate with the committed-set re-extraction,
NOT a re-record.

## Integration risk
this REVERSES the audit-9.7 precision down-weight for the honest band — the 19% crew FP is the accepted cost
of lighting R7 (info-backed + gate-mediated; the deterministic floor keeps it from being RANDOM), and the
held 13.12 re-record measures the real R1-up vs friendly-fire. Keep the weak-guards (do NOT promote the
self-pair / defense-echo / adversarial shapes — those are the actual false positives). Do NOT touch
`alibi_vs_physical` / `MIN_VOICES` (empty path). The unit tests that recompute the classification re-anchor;
the committed replays' recorded data is unaffected (reconstruction replays recorded outputs).

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-13-avs-strong` with a title like `task 13.14: promote `alibi_vs_sighting` to strong (light r7 off 0/114)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.4 + §6.4 (reconciled — WEAK/STRONG classification; STRONG drives Rule 2's gate-crossing delta); experiments/lab/report-forward-redesign-probes.md Probe 3 (the live sweep: promoting `alibi_vs_sighting` STRONG = 54/114 at 81% precision; `MIN_VOICES`/co-presence is an empty path; corroboration makes it worse); experiments/lab/forward_redesign_detector_sweep.py (the validating re-extraction); meetings/transcript.py:610 (`is_weak_contradiction`), :517 (`PHYSICAL_CONTRADICTION_MIN_VOICES`), :922 (`detect_contradictions`); agents/memory/beliefs.py:659 (Rule 2 reads `is_weak_contradiction`)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
