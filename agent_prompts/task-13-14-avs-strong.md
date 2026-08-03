# Agent Prompt — 13.14 Promote `alibi_vs_sighting` to STRONG (light R7 off 0/114)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.14 — Promote `alibi_vs_sighting` to STRONG (light R7 off 0/114), anchored to DESIGN.md §5.4 + §6.4 (reconciled — WEAK/STRONG classification; STRONG drives Rule 2's gate-crossing delta); experiments/lab/report-forward-redesign-probes.md Probe 3 (the sweep) + Probe 4 (the conversion probe: +3 worst-case wrong / +20 correct); audits/audit-2026-06-22-2149-wave-e-review.md (the review + the owner LONE-STRONG decision); meetings/transcript.py:1933 (`_weak_signal_reasons` — the marker WRITER to edit), :1767 (the endpoint marker, KEPT weak), :610 (`is_weak_contradiction`, a pure predicate — do NOT edit); meetings/manager.py:1911-1928 (the Rule-2 + 13.7-spread apply site — add the joint cap); agents/memory/beliefs.py:659 (Rule 2 reads the marker). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-avs-strong`
**Depends on:** 13.3, 13.4, 13.5, 13.7
**Section refs:** DESIGN.md §5.4 + §6.4 (reconciled — WEAK/STRONG classification; STRONG drives Rule 2's gate-crossing delta); experiments/lab/report-forward-redesign-probes.md Probe 3 (the sweep) + Probe 4 (the conversion probe: +3 worst-case wrong / +20 correct); audits/audit-2026-06-22-2149-wave-e-review.md (the review + the owner LONE-STRONG decision); meetings/transcript.py:1933 (`_weak_signal_reasons` — the marker WRITER to edit), :1767 (the endpoint marker, KEPT weak), :610 (`is_weak_contradiction`, a pure predicate — do NOT edit); meetings/manager.py:1911-1928 (the Rule-2 + 13.7-spread apply site — add the joint cap); agents/memory/beliefs.py:659 (Rule 2 reads the marker)
**Complexity:** Integration
**Files in scope:**
- meetings/transcript.py
- meetings/manager.py
- tests/meetings/test_transcript.py
- tests/agents/test_beliefs.py
**Files NOT in scope:**
- the committed replays — NO re-record; the recorded `contradictions` field stays, validation is a $0 RE-EXTRACTION that recomputes; the held 13.12 re-record is what bakes STRONG flags into recordings
- meetings/voting.py + the §4.6 floor — unchanged
- the belief delta wiring (`apply_contradiction_rule`) — already routes a non-weak flag to the gate-crossing delta from Wave B; only the CLASSIFICATION changes
- the `is_weak_contradiction` READERS (eval/meeting_quality.py:1891, api/replay_loader.py:1743, api/schemas.py:550, audits/workflows/extract_gameplay_facts.py:286) — UNCHANGED; their eval-metric / spectator-severity weak→strong shift is EXPECTED, not a regression

**Owner decision (2026-06-22): LONE-STRONG.** A single-witness `alibi_vs_sighting` contradiction MAY cross the
gate — relaxing the "no single signal ejects" principle for concrete, evidence-backed contradictions. The $0
conversion probe (Probe 4) bounds the cost at **+3 worst-case wrong crew vs +20 correct impostor ejections**
(deterministic-gate upper bound; 13.13 de-imperative reduces it further; the held re-record measures the real
rate under an R4-abandon gate).

The real lever (the original "promote the honest set" framing was a NO-OP — all 111 committed
`alibi_vs_sighting` flags carry a weak marker): **REMOVE `WEAK_REASON_SELF_STATED` emission for the
`alibi_vs_sighting` kind at the marker WRITER** (`meetings/transcript.py:1933` `_weak_signal_reasons`),
reversing the audit-9.7 self-stated down-weight for this band, so a self-stated-only alibi-vs-sighting
contradiction classifies **STRONG** and drives Rule 2's full gate-crossing delta (§6.3). **KEEP the genuine
shaky-flag guards weak** — endpoint-tick mismatch (`:1767`), narrow, self-pair, adversarial — they are real
precision guards, NOT the self-stated down-weight; do NOT promote them. Do NOT edit `is_weak_contradiction`
(`:610`, a pure marker-PREDICATE). **Add a joint per-subject suspicion cap** across the Rule-2 contradiction
lift + the 13.7 testimony-spread (`meetings/manager.py:1911-1928`) so a lone-flagged + multi-accused subject
cannot stack to 0.92 (today the two caps are independent). Keep `PHYSICAL_CONTRADICTION_MIN_VOICES` /
`alibi_vs_physical` AS-IS (the sweep proved it an empty path).

**Firewall:** the detector reads only the public transcript (no privileged state); no agent-visible field is
added. **Determinism:** the classification is a pure function of the recorded transcript — a re-extraction
is deterministic, and the committed replays re-walk byte-identically (reconstruction replays recorded
outputs, it does not re-run the detector).
**Definition of done:** `WEAK_REASON_SELF_STATED` is no longer emitted for the `alibi_vs_sighting` kind (the
genuine shaky guards — endpoint / narrow / self-pair / adversarial — STAY weak); the joint per-subject 13.7
cap is added (`manager.py:1911-1928`) so a lone-flagged + multi-accused subject cannot exceed the bound; a $0
re-extraction shows R7 off 0 on ≥3 seeds with the precision MEASURED on the ACTUALLY-promoted subset (NOT the
assumed 81% — that was `promote_all_avs` over all 111; spot-read 5 flagged meetings, gp-3 watch-the-games
BLOCKING); a re-run of `forward_redesign_conversion_probe.py` shows the wrong-ejection (R4) delta ≤ the +3
worst case; `alibi_vs_physical` / `MIN_VOICES` UNCHANGED; the classification pins re-anchored
(`test_self_stated_alibi_vs_third_party_sighting_is_weak`, `test_surviving_endpoint_flags_are_weak_banded`, the
`TestCommittedBytesSeedPins` cluster); the committed state-hash verify stays green; `scripts/check.sh` green.

## Implementation hint
edit the marker WRITER `_weak_signal_reasons` (`transcript.py:1933`) to stop emitting `WEAK_REASON_SELF_STATED`
for the `alibi_vs_sighting` kind (KEEP the endpoint-tick `:1767`, narrow, self-pair, adversarial reasons); do
NOT edit `is_weak_contradiction` (`:610`, a pure marker-predicate). Add the joint cap in `manager.py:1911-1928`
(a per-subject cap across `apply_contradiction_rule` + `apply_meeting_evidence_rules`). The Rule 2 wiring
(`beliefs.py:659`) already applies the STRONG delta to a non-weak flag. Validate with the re-extraction + the
conversion probe, NOT a re-record.

## Integration risk
OWNER-ACCEPTED LONE-STRONG: a single-witness contradiction may eject (relaxing the no-single-signal principle
for evidence-backed contradictions); the conversion probe bounds the cost at +3 worst-case wrong crew vs +20
correct (deterministic-gate upper bound; 13.13 reduces it). The joint 13.7 cap is LOAD-BEARING (without it a
lone-flagged + 2-accuser subject renders 0.92). The 4 live `is_weak_contradiction` readers shift weak→strong —
EXPECTED, not a regression. Re-spec the held-13.12 gate to **R1-up AND R4 wrong-ejection-floor flat AND
impostor win ≥ 14%** (NOT friendly-fire = impostor-kills-impostor, which is engine-forbidden); abandon the
re-record if R4 rises beyond the conversion probe's +3. Do NOT touch `alibi_vs_physical` / `MIN_VOICES` (empty
path); the committed replays' recorded data is unaffected (reconstruction replays recorded outputs).

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
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
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.4 + §6.4 (reconciled — WEAK/STRONG classification; STRONG drives Rule 2's gate-crossing delta); experiments/lab/report-forward-redesign-probes.md Probe 3 (the sweep) + Probe 4 (the conversion probe: +3 worst-case wrong / +20 correct); audits/audit-2026-06-22-2149-wave-e-review.md (the review + the owner LONE-STRONG decision); meetings/transcript.py:1933 (`_weak_signal_reasons` — the marker WRITER to edit), :1767 (the endpoint marker, KEPT weak), :610 (`is_weak_contradiction`, a pure predicate — do NOT edit); meetings/manager.py:1911-1928 (the Rule-2 + 13.7-spread apply site — add the joint cap); agents/memory/beliefs.py:659 (Rule 2 reads the marker)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
