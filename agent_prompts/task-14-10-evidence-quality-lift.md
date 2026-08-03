# Agent Prompt — 14.10 Evidence-quality lift fix: certain-guilt ceiling + self-refuted-alibi downgrade (default-OFF lever)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.10 — Evidence-quality lift fix: certain-guilt ceiling + self-refuted-alibi downgrade (default-OFF lever), anchored to audits/audit-2026-07-01-phase-14-baseline1-characterization.md §3/§3a (the MEASURED mechanism + the two-bound fix spec — read it first, it overturned the original framing); tests/meetings/test_manager.py (the pinned 5-row railroad set = the reproduction corpus); agents/memory/beliefs.py (the 13.14 joint cap this extends); tasks/phase-13-5.md (the default-OFF-lever + stamp pattern this task reuses). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-evidence-quality-lift`
**Depends on:** 14.8, 14.9
**Section refs:** audits/audit-2026-07-01-phase-14-baseline1-characterization.md §3/§3a (the MEASURED mechanism + the two-bound fix spec — read it first, it overturned the original framing); tests/meetings/test_manager.py (the pinned 5-row railroad set = the reproduction corpus); agents/memory/beliefs.py (the 13.14 joint cap this extends); tasks/phase-13-5.md (the default-OFF-lever + stamp pattern this task reuses)
**Complexity:** Integration

Fix the crew-railroad defect per the MEASURED 14.8 diagnosis (audit §3 — which OVERTURNED the original
flag-density framing: the 10.1/13.14 caps HOLD; even seed-44's 9 flags dedup to ONE `contradiction_lift_key`
group capped at +0.30, so flag COUNT is a signature, not the causal variable). The real mechanism compounds:
one saturated strong group lands +0.30 in EVERY voter's graph in lockstep (0.50 → 0.80 ≥ the 0.60 gate = a
roster-wide must-vote on the flagged subject), and the voters carrying the Phase-10 Rule-1 body-proximity
prior (0.70) clamp to certain-guilt 1.00 — in all 5 pinned rows the 1.00-renderers are the impostors.
Implement the audit's TWO measured bounds behind a NEW default-OFF env lever (the 13.5 pattern): (1)
CERTAIN-GUILT EXCLUSION — extend the 13.14 joint cap to `min(lifted, prior + 0.3, CONTRADICTION_RENDER_CEIL)`
(just below the clamp, e.g. 0.97) for flag/testimony-driven lift, EXEMPTING first-hand conclusive observation
(a witnessed kill legitimately reads ~1.0); zero conversion cost — every 0.97 stays a must-vote. (2)
SELF-REFUTED-ALIBI DOWNGRADE — a contradiction group whose refuted alibi is contradicted by the subject's OWN
same-turn `completed_task` observation contributes the WEAK delta (0.08), not STRONG (0.30); measured cost on
baseline 1: 0/57 flagged impostor ejections, while keeping seed-16/44's rosters sub-gate. The audit REJECTS
two tempting shapes BY MEASUREMENT — do NOT implement witness-count weighting (an anti-signal: honest greedy
alibis attract MORE independent refuting witnesses than impostor lies) or ≥2-group gating (over-damps: 54/57
flagged impostor ejections ride exactly ONE group). The change alters belief re-derivation, so gate it
default-OFF: OFF preserves baseline-1 byte-identity and every committed-bytes test; 14.12 records baseline 2
with the lever ON and stamps it. Register the lever in the `substrate_flag_snapshot()` stamp machinery (kept
generic by 14.9) so the recording self-describes.

**Files in scope:**
- agents/memory/beliefs.py (the render-ceiling extension of the 13.14 joint cap + the self-refuted-alibi WEAK downgrade, behind the new `*_enabled()` resolver; the existing caps are extended, not rewritten)
- orchestrator/replay.py (register the new lever as the first entry in `_TOGGLEABLE_LEVER_RESOLVERS` — the registration point 14.9 built for exactly this, whose docstring names 14.10 as "the next registrant"; `SUBSTRATE_FLAG_KEYS` and `substrate_flag_snapshot()` derive from the table automatically)
- .env.example (document the new default-OFF lever)
- tests/agents/test_beliefs.py (unit tests: a synthetic 9-flag same-meeting stack renders BELOW certain-guilt with the lever ON; byte-identity of the fold with it OFF; evidence-class weighting cases if implemented)
- tests/orchestrator/test_replay.py (the stamp round-trips the new lever)

**Files NOT in scope:**
- replays/samples/ (baseline 1 is untouched; the lever defaults OFF so it still byte-verifies — the re-record is 14.12)
- tests/meetings/test_manager.py (the railroad regression pin walks baseline-1 bytes and stays green as-is; RESTORING it to a tripwire happens at 14.12 when the bytes change)
- agents/strategic/prompts/ (the prompt-side fuel fix is 14.11)
- meetings/transcript.py detector logic (flags are still DETECTED the same; this task changes how the belief fold WEIGHS them)

**Definition of done:**
- [ ] Bound 1 (certain-guilt exclusion): with the lever ON, NO flag/testimony-driven lift can render at the 1.0 clamp — unit tests cover BOTH 1.0 paths from the audit: the neutral-prior case (0.50 + saturated 0.30 → 0.80, unchanged) and the compounding case (body-proximity prior 0.70 + 0.30 → CEILS at ~0.97, not 1.00); a first-hand witnessed-kill pin still renders ~1.0 (the exemption).
- [ ] Bound 2 (self-refuted-alibi downgrade): a contradiction group whose refuted alibi is contradicted by the subject's OWN same-turn `completed_task` observation contributes WEAK (0.08) not STRONG (0.30), with tests for the self-refuted and not-self-refuted cases.
- [ ] The offline proof over baseline-1 bytes (via the 14.8 `allow_substrate_mismatch` override): all 5 pinned railroad rows render below 1.0 with the lever ON, AND the seed-44 m0 true-impostor catch still gate-crosses (the over-damping canary).
- [ ] With the lever OFF (the default), the belief fold is byte-identical to pre-task behavior: committed baseline-1 reconstructs byte-identically and every committed-bytes test stays green unmodified.
- [ ] The REJECTED shapes are absent: no witness-count weighting, no ≥2-group gating (audit §3a rejected both by measurement — a reviewer finding either is a contract violation, not an improvement).
- [ ] The new lever is registered in `substrate_flag_snapshot()` / `SUBSTRATE_FLAG_KEYS` and round-trips through the replay stamp + MANIFEST `flags` cell (so the 14.12 recording self-describes).
- [ ] `.env.example` documents the lever as default-OFF pending the 14.12 baseline-2 re-record.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Read audit §3/§3a FIRST — it reproduced the production fold exactly (2482/2482 recorded vote-prompt rows) and
its spec is measured, not hypothesized. Both bounds are small extensions at the 13.14 joint-cap site in
`agents/memory/beliefs.py`: bound 1 adds a third term to the min (`CONTRADICTION_RENDER_CEIL`, ~0.97, applied
only to flag/testimony-driven lift — the first-hand witnessed-kill pin path stays exempt); bound 2 needs the
self-refutation signal at fold time, which is mechanically derivable from the transcript (the subject's own
same-turn `completed_task` room/tick inside the refuted alibi span — the same check the audit ran). The gate:
a module constant `ENV_EVIDENCE_QUALITY_LIFT` + an `evidence_quality_lift_enabled(env=None)` resolver — NOTE
the signature: 14.9's `_TOGGLEABLE_LEVER_RESOLVERS` table expects
`Callable[[Mapping[str, str] | None], bool]` (env threaded, defaulting to the process environment, like
`resolve_prompt_set`), not a no-arg reader. OFF branch byte-identical. The relevant constants already exist in
`agents/memory/beliefs.py` (`CONTRADICTION_SUSPICION_DELTA` 0.3 / `WEAK_CONTRADICTION_SUSPICION_DELTA` 0.08 /
`MEETING_CONTRADICTION_LIFT_CAP`) — extend that machinery, do not duplicate it. Prove the
fix offline before 14.12 spends: re-derive the 5 pinned railroad meetings from baseline-1 bytes with the lever
ON and confirm every pinned row renders below 1.0 AND the seed-44 m0 true-impostor catch still converts. Note
the stamp: baseline 1's stamp lacks the new lever key, so re-deriving with it ON is a substrate mismatch — use
the 14.8 analysis-only override (`allow_substrate_mismatch=True`) for exactly this comparison; that is what it
exists for.

## Public types this task introduces
- `agents.memory.beliefs.evidence_quality_lift_enabled`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This is a belief-fold change on the exact code path 13.5/14.9 just reshaped — the OFF-branch byte-identity
bullet is the guard against regressing the committed baseline; run `scripts/verify_samples.sh` (bare env)
before and after. Do NOT weaken the §4.6 vote gate or the detectors to make the numbers move — the fix is in
the FOLD's weighting, so genuine multi-witness evidence must still convict (the seed-44 m0 TRUE-impostor
catch, driven by real cross-referencing, must still convert with the lever ON; add it as a fixture if cheap).
Over-damping is the failure mode to watch: if the lever ON drops genuine-class conversion materially in the
14.12 smoke, the bound is too tight — iterate the weighting, do not ship a crew that can't convict.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import llm.featherless_client"`
- `uv run python -c "import llm.provider"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-14-evidence-quality-lift` with a title like `task 14.10: evidence-quality lift fix: certain-guilt ceiling + self-refuted-alibi downgrade (default-off lever)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-2026-07-01-phase-14-baseline1-characterization.md §3/§3a (the MEASURED mechanism + the two-bound fix spec — read it first, it overturned the original framing); tests/meetings/test_manager.py (the pinned 5-row railroad set = the reproduction corpus); agents/memory/beliefs.py (the 13.14 joint cap this extends); tasks/phase-13-5.md (the default-OFF-lever + stamp pattern this task reuses)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
