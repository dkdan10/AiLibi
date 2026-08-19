# Agent Prompt — 20.11 Kill, report and sabotage are illegal from inside a vent

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.11 — Kill, report and sabotage are illegal from inside a vent, anchored to C-1 [CONFIRMED, P1] — audits/review-2026-08-19/B/engine.md §2 P1 F1 (the three-probe repro: kill, report and sabotage all resolve from inside a vent) and audits/review-2026-08-19/B/verdicts.md claim 1 (the full code-path read, three failed refutation attempts, the framing correction on the mask, the "committed replays unaffected" confirmation); the fix is roadmap row 1.5 of audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 1. Anchors re-verified at HEAD: engine/rules.py:56 `resolve_kill` (role, target-role, cooldown, same-room — no `in_vent`), :182 `resolve_report` (body-room only), :225 `resolve_sabotage` (role + not-already-active) against the four rules that DO guard — engine/tick.py:243 move, :280 do_task, engine/rules.py:209 `resolve_emergency_meeting` ("cannot call emergency meeting while in vent"), :254 `resolve_repair_sabotage` ("cannot repair sabotage while in vent"); engine/rules.py:64-70, the friendly-fire guard's own defense-in-depth argument, which this task extends to `in_vent` (the review cites :60-66; the true anchor at HEAD is :64-70); engine/rules.py:102-107 `resolve_vent` (impostor-only, so an in-vent actor is always an impostor) and engine/tick.py:530-536 `_apply_wait`; engine/tick.py:601 (`ActionRejectedError` → `ActionRejectedEvent`, the conversion the mask property test reads); engine/visibility.py:78 (`not player.in_vent` — the vented are hidden from others and never blinded themselves); training/env.py:213-223 (the mask's "a faithful mirror the property test pins against the real engine" docstring), :288-298 KILL, :322-329 REPORT, :341-350 SABOTAGE (whose comment asserts "no location or in-vent requirement"); tests/training/test_env.py:339-374 `test_mask_legality_against_engine` (8 seeds, BOTH directions asserted); tests/engine/test_tick.py:929 and :987 (the vent-exit allowances) and :1158 `test_emergency_rejects_actor_in_vent`; agents/tactical/impostor_policy.py:304 and agents/tactical/learned/forward.py:323-325 (the two shipped in-vent short-circuits); observation/service.py:348-356 (the `visible_players` allowance the review logs as its P2 secondary finding — the review's :365-372 anchor has moved); DESIGN.md:332-338 §3.4 and :359 §3.6 ("the engine is the single source of truth"); the in-vent census over committed bytes in audits/review-2026-08-19/B/verdicts.md claim 3 (`impostor_ticks=2461  in_vent=130` across all 50 committed 9p2i seeds).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-in-vent-guards`
**Depends on:** none (root)
**Section refs:** C-1 [CONFIRMED, P1] — audits/review-2026-08-19/B/engine.md §2 P1 F1 (the three-probe repro: kill, report and sabotage all resolve from inside a vent) and audits/review-2026-08-19/B/verdicts.md claim 1 (the full code-path read, three failed refutation attempts, the framing correction on the mask, the "committed replays unaffected" confirmation); the fix is roadmap row 1.5 of audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 1. Anchors re-verified at HEAD: engine/rules.py:56 `resolve_kill` (role, target-role, cooldown, same-room — no `in_vent`), :182 `resolve_report` (body-room only), :225 `resolve_sabotage` (role + not-already-active) against the four rules that DO guard — engine/tick.py:243 move, :280 do_task, engine/rules.py:209 `resolve_emergency_meeting` ("cannot call emergency meeting while in vent"), :254 `resolve_repair_sabotage` ("cannot repair sabotage while in vent"); engine/rules.py:64-70, the friendly-fire guard's own defense-in-depth argument, which this task extends to `in_vent` (the review cites :60-66; the true anchor at HEAD is :64-70); engine/rules.py:102-107 `resolve_vent` (impostor-only, so an in-vent actor is always an impostor) and engine/tick.py:530-536 `_apply_wait`; engine/tick.py:601 (`ActionRejectedError` → `ActionRejectedEvent`, the conversion the mask property test reads); engine/visibility.py:78 (`not player.in_vent` — the vented are hidden from others and never blinded themselves); training/env.py:213-223 (the mask's "a faithful mirror the property test pins against the real engine" docstring), :288-298 KILL, :322-329 REPORT, :341-350 SABOTAGE (whose comment asserts "no location or in-vent requirement"); tests/training/test_env.py:339-374 `test_mask_legality_against_engine` (8 seeds, BOTH directions asserted); tests/engine/test_tick.py:929 and :987 (the vent-exit allowances) and :1158 `test_emergency_rejects_actor_in_vent`; agents/tactical/impostor_policy.py:304 and agents/tactical/learned/forward.py:323-325 (the two shipped in-vent short-circuits); observation/service.py:348-356 (the `visible_players` allowance the review logs as its P2 secondary finding — the review's :365-372 anchor has moved); DESIGN.md:332-338 §3.4 and :359 §3.6 ("the engine is the single source of truth"); the in-vent census over committed bytes in audits/review-2026-08-19/B/verdicts.md claim 3 (`impostor_ticks=2461  in_vent=130` across all 50 committed 9p2i seeds).
**Complexity:** Small
**Record impact:** none
**Measurement:** `uv run pytest tests/engine/test_rules.py tests/training/test_env.py -q` green (the three new rejections, the exhaustive in-vent action table, and the mask-versus-engine property test over all 8 seeds); `bash scripts/verify_samples.sh` reports 100/100 committed samples clean; `uv run pytest -m campaign -q` green, with the PR recording that no pinned ML value moved.

The engine is the project's declared single source of truth for the rules (DESIGN.md:359),
and on three of them it is not. `resolve_kill`, `resolve_report` and `resolve_sabotage`
never look at `actor.in_vent`, while the four sibling rules that share the same physical
premise all do — move and do_task reject it in `engine/tick.py`, emergency and repair
reject it in `engine/rules.py` two and three functions away from the gap. The review
reproduced all three from a live state (B/engine.md §2 F1: `['Killed','TickAdvanced']`,
`['MeetingTriggered']`, `['SabotageStarted','TickAdvanced']`, each with
`killer in_vent: True`), and its refutation pass found no compensating guard anywhere:
no orchestrator or agent-boundary check (`grep -rn in_vent orchestrator/` returns only
`seeder.py:186`), no test covering the three cases, and no design ruling — DESIGN.md:334
lists the kill preconditions as role, crew target, same room and cooldown, and says
nothing about acting from inside a vent. This is an unruled gap, not an intentional
mechanic.

Combined with `engine/visibility.py:78` — which hides the vented from everyone else but
never restricts a vented *observer* — the gap composes into a strictly dominant impostor
line: see the whole room, never appear in anyone's `visible_players`, kill on cooldown,
stay inside, then open the meeting yourself. This is exactly the argument
`engine/rules.py:64-70` already makes for the friendly-fire guard — "a buggy or future
LLM-driven policy must not be able to" break the rule — simply never applied to
`in_vent`, which leaves rule enforcement load-bearing on agent code. Today it is latent
and the review confirmed it: both shipped policies take an in-vent branch before any kill,
body or sabotage logic (`agents/tactical/impostor_policy.py:304`,
`agents/tactical/learned/forward.py:323-325`), so no committed replay, eval number or ES
artifact is contaminated and this task is re-record-free. The forward risk is concentrated
in `training/`: `build_action_mask` mirrors the engine and therefore *advertises* kill,
report and sabotage as engine-legal from inside a vent (the review's repro3 printed
`ENGINE-LEGAL while vented: ['kill','sabotage','vent','wait']`), and the mask is not
hypothetical machinery — `training/bakeoff/policy_es.py:292` scores every
`mask.submission_legal` intent with no in-vent short-circuit of its own. The next policy
that samples the mask rather than the hand-written option menu can discover the untraceable
line and silently invalidate any impostor-side balance measurement taken with it.

The ruling this contract records is total rather than three patches: from inside a vent the
only legal actions are `vent` and `wait`. Sabotage is decided explicitly and ruled ILLEGAL.
Its remoteness is not the question — `resolve_sabotage` has no room check and that stays
true — the question is whether an actor with no physical presence may act at all, and the
engine's own answer everywhere else is no, including for `repair_sabotage`, sabotage's
mirror image. Leaving it legal would hand a mask-sampling policy a global action that costs
zero alibi exposure, from the one state in which the actor is absent from every other
agent's perception. `training/env.py` moves in the same commit and for a mechanical reason,
not a stylistic one: `test_mask_legality_against_engine` asserts both directions —
masked-legal implies engine-accepts *and* masked-illegal implies engine-rejects — so either
half alone turns the repo's own mirror gate red. That two-way pin is the finding's own
safeguard and must be kept working, not worked around.

Nothing else moves. This is not a lever: the rule ships unconditionally, with no
`AILIBI_*` gate and nothing to register in the substrate stamp. No prompt template is
touched. `observation/service.py` is read as evidence and left alone, but the PR should
note the consequence, because the leak-scanner entitlement work reads the same surface:
`_visible_players` (:348-356) admits an actor carrying an observed action even when
visibility excluded them, and after this task the only observed action that can still
surface a vented player is the `vent` sighting itself — which DESIGN.md:336 makes
observable by design. The "vented players are invisible" invariant goes from leaky to
exactly-one-documented-exception.

**Files in scope:**
- engine/rules.py; (three `if actor.in_vent: raise ActionRejectedError(...)` guards matching :209/:254)
- tests/engine/test_rules.py; (the three rejections + the existing in-vent allowances pinned)
- training/env.py; (the action mask excludes kill/report/sabotage while in_vent)
- tests/training/test_env.py; (mask==engine still green; the in-vent row asserted)
- DESIGN.md; (§3.4 kill preconditions gain 'not in a vent' — a one-line truth-up, historical content untouched)

**Files NOT in scope:**
- agents/tactical/ (the FSM and the compact learned forward pass already short-circuit on `in_vent`; the engine guard is the defense-in-depth layer beneath them, not a replacement)
- observation/service.py (the vented-actor-in-`visible_players` allowance at :348-356 is read as evidence and reported in the PR, never edited here)
- training/bakeoff/, training/crew/, experiments/lab/ (mask consumers — grep-verified and re-run, not edited)
- orchestrator/replay.py (this is an unconditional rule, not a lever: there is no resolver and nothing to register in the substrate stamp)
- agents/strategic/prompts/ (no task in this phase edits a game prompt template except the single prompt-set bump)
- replays/ and replays/samples/ (no re-record; byte-identical reconstruction is the gate, not an output)

**Definition of done:**
- [ ] `engine.rules.resolve_kill`, `resolve_report` and `resolve_sabotage` each reject an in-vent actor with `ActionRejectedError`, the guard placed immediately after the function's `_get_live_player` call so it reads before the role and room checks — the shape `resolve_emergency_meeting` (:209) and `resolve_repair_sabotage` (:254) already use — and each message names the rule it enforces rather than the symptom.
- [ ] Three new tests in `tests/engine/test_rules.py` pin the rejections from states where every OTHER precondition is satisfied — an impostor off cooldown with a living crewmate in the same room; a body in the actor's own room; no sabotage already active — so each rejection is attributable to the vent alone and not to an incidentally illegal fixture.
- [ ] The ruling is pinned as a TOTAL rule, not three ad-hoc guards: a table-driven test in `tests/engine/test_rules.py` asserts that from one in-vent state `engine.tick.advance_tick` accepts exactly `vent` and `wait` and rejects the other seven action types, and asserts the table's own coverage against the members of `engine.actions.Action` so a tenth action type fails this test until it is ruled.
- [ ] The existing in-vent allowances are unchanged and still green, unedited: the vent-exit tests at `tests/engine/test_tick.py:929` and `:987`, `test_emergency_rejects_actor_in_vent` at `:1158`, and all five pre-existing `resolve_kill` tests in `tests/engine/test_rules.py` (friendly-fire, crewmate target, actor-role, cooldown, same-room) with their current match strings.
- [ ] `training/env.py`'s mask marks kill, report and sabotage illegal while `in_vent` across its three regions (:288-298, :322-329, :341-350), and the SABOTAGE region's comment claim "no location or in-vent requirement" is corrected in the same edit rather than left contradicting the code beneath it.
- [ ] `tests/training/test_env.py::test_mask_legality_against_engine` stays green over all 8 seeds, and a new hand-built in-vent case — in the `_mask_with_impostor_in(..., in_vent=True)` style already in the file — asserts that the kill, report and sabotage intents land in `mask.illegal` AND that `_engine_rejects` agrees on the same state, so the pairing is pinned directly instead of depending on a sampled rollout happening to vent beside a victim.
- [ ] `DESIGN.md` §3.4 records the ruling additively, in the document's own Superseded style established by its demotion banner: a short dated note at the top of the section stating that kill, report and sabotage are rejected from inside a vent, that `vent` and `wait` are the only actions legal from there, and that `engine/rules.py` is the enforcing site — with the historical rule bullets at `:334-338` left as written.
- [ ] `bash scripts/verify_samples.sh` reports all 100 committed samples (50 × 4p1i + 50 × 9p2i) reconstructing byte-identically, and the PR states the conclusion this supports: no committed replay contains a now-illegal action, which is what makes this change re-record-free — the review measured 130 in-vent impostor ticks out of 2,461 across the 50 committed 9p2i seeds, so the state is common and the absence of the action is a real result, not an untested corner.
- [ ] The blast radius of the narrowed mask is stated in the PR from a fresh grep: `training/bakeoff/policy_es.py:292`, `training/bakeoff/harness.py:597`, `training/crew/scorer.py:778` and `experiments/lab/torch_probe/entrant.py:345` all enumerate the mask, and `policy_es` carries no in-vent short-circuit of its own, so a vented ES candidate's option set narrows; `uv run pytest -m campaign` is run and the PR records either that no pinned ML value moved or which one did and why.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-20-in-vent-guards` with a title like `task 20.11: kill, report and sabotage are illegal from inside a vent`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing C-1 [CONFIRMED, P1] — audits/review-2026-08-19/B/engine.md §2 P1 F1 (the three-probe repro: kill, report and sabotage all resolve from inside a vent) and audits/review-2026-08-19/B/verdicts.md claim 1 (the full code-path read, three failed refutation attempts, the framing correction on the mask, the "committed replays unaffected" confirmation); the fix is roadmap row 1.5 of audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 1. Anchors re-verified at HEAD: engine/rules.py:56 `resolve_kill` (role, target-role, cooldown, same-room — no `in_vent`), :182 `resolve_report` (body-room only), :225 `resolve_sabotage` (role + not-already-active) against the four rules that DO guard — engine/tick.py:243 move, :280 do_task, engine/rules.py:209 `resolve_emergency_meeting` ("cannot call emergency meeting while in vent"), :254 `resolve_repair_sabotage` ("cannot repair sabotage while in vent"); engine/rules.py:64-70, the friendly-fire guard's own defense-in-depth argument, which this task extends to `in_vent` (the review cites :60-66; the true anchor at HEAD is :64-70); engine/rules.py:102-107 `resolve_vent` (impostor-only, so an in-vent actor is always an impostor) and engine/tick.py:530-536 `_apply_wait`; engine/tick.py:601 (`ActionRejectedError` → `ActionRejectedEvent`, the conversion the mask property test reads); engine/visibility.py:78 (`not player.in_vent` — the vented are hidden from others and never blinded themselves); training/env.py:213-223 (the mask's "a faithful mirror the property test pins against the real engine" docstring), :288-298 KILL, :322-329 REPORT, :341-350 SABOTAGE (whose comment asserts "no location or in-vent requirement"); tests/training/test_env.py:339-374 `test_mask_legality_against_engine` (8 seeds, BOTH directions asserted); tests/engine/test_tick.py:929 and :987 (the vent-exit allowances) and :1158 `test_emergency_rejects_actor_in_vent`; agents/tactical/impostor_policy.py:304 and agents/tactical/learned/forward.py:323-325 (the two shipped in-vent short-circuits); observation/service.py:348-356 (the `visible_players` allowance the review logs as its P2 secondary finding — the review's :365-372 anchor has moved); DESIGN.md:332-338 §3.4 and :359 §3.6 ("the engine is the single source of truth"); the in-vent census over committed bytes in audits/review-2026-08-19/B/verdicts.md claim 3 (`impostor_ticks=2461  in_vent=130` across all 50 committed 9p2i seeds).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
