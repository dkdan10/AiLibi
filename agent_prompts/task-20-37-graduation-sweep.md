# Agent Prompt — 20.37 Retire means delete: the post-record graduation sweep and the old accept-and-ignore residue

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.37 — Retire means delete: the post-record graduation sweep and the old accept-and-ignore residue, anchored to C-64 and C-104 in `audits/review-2026-08-19/B/collated-findings.md` §4 and §5; RC6 in `audits/review-2026-08-19/D/FINAL-synthesis.md` §1 ("the render-version stamp, plus one deletion pass"); the per-area sources `audits/review-2026-08-19/B/repo-health-architecture.md` §2 F6, `audits/review-2026-08-19/B/agents-memory.md` §2 F4, `audits/review-2026-08-19/B/meetings-transcript-voting.md` §2 F5, `audits/review-2026-08-19/B/meetings-manager.md` §2 P1-3, `audits/review-2026-08-19/B/orchestrator.md` §2 (the `suspicion_graph_for_meeting` dead-kwarg leg). Anchors RE-VERIFIED at HEAD: the nine accept-and-ignore resolvers `agents/memory/store.py:189`, `agents/memory/beliefs.py:190,224,292,407`, `meetings/constants.py:54`, `meetings/transcript.py:1362,1389`, `meetings/manager.py:859` (200 source lines in total, each ending `del env  # retired: the lever is unconditional, no environment is consulted`); their nine `ENV_*` constants `agents/memory/store.py:186`, `agents/memory/beliefs.py:187,221,289,404`, `meetings/constants.py:51`, `meetings/manager.py:856`, `meetings/transcript.py:1354,1359` and the nine matching `__all__` entries; the thirteen production read sites `agents/memory/store.py:280,286,1632,1652`, `agents/memory/beliefs.py:1463,1465,1502,1826,1835,1841`, `meetings/manager.py:1185,1759,2018,2448`, `meetings/transcript.py:1554,1555`, `orchestrator/game.py:2713`; the dead private-helper parameter `meetings/transcript.py:2380-2385` with its own "survives only for direct callers" comment at `:2407-2410`; the stamp registry `orchestrator/replay.py:531-545` (`_RETIRED_ALWAYS_ON_LEVERS`, thirteen keys) and `:570-572` (`_TOGGLEABLE_LEVER_RESOLVERS`, one live entry); the rule this task amends, `AGENTS.md:62-75` (Graduation sweeps) beside craft rule 3 at `AGENTS.md:91-94`; `.env.example:68-97` (the graduated always-ON note); the test residue `tests/agents/test_absence_prior.py:166-216`, `tests/agents/test_beliefs_hard_evidence_gate.py:86-115`, `tests/agents/test_beliefs.py:2634-2660`, `tests/agents/test_episodic_ids.py:383-458`, `tests/meetings/test_citation_gate.py:127-158`, `tests/meetings/test_manager.py:475-512` and `:772` (`TestRollCallOffPath`, whose docstring says the round is skipped while its test asserts the round fires), `tests/meetings/test_contradictions.py:1531-1617`. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-graduation-sweep`
**Depends on:** 20.36 — the adopting record is the ruling that says which levers graduated, and a lever may only be deleted after its verdict exists; the record's own graduation flips are the commit this sweep deletes on top of, so it cannot run in parallel with them
**Section refs:** C-64 and C-104 in `audits/review-2026-08-19/B/collated-findings.md` §4 and §5; RC6 in `audits/review-2026-08-19/D/FINAL-synthesis.md` §1 ("the render-version stamp, plus one deletion pass"); the per-area sources `audits/review-2026-08-19/B/repo-health-architecture.md` §2 F6, `audits/review-2026-08-19/B/agents-memory.md` §2 F4, `audits/review-2026-08-19/B/meetings-transcript-voting.md` §2 F5, `audits/review-2026-08-19/B/meetings-manager.md` §2 P1-3, `audits/review-2026-08-19/B/orchestrator.md` §2 (the `suspicion_graph_for_meeting` dead-kwarg leg). Anchors RE-VERIFIED at HEAD: the nine accept-and-ignore resolvers `agents/memory/store.py:189`, `agents/memory/beliefs.py:190,224,292,407`, `meetings/constants.py:54`, `meetings/transcript.py:1362,1389`, `meetings/manager.py:859` (200 source lines in total, each ending `del env  # retired: the lever is unconditional, no environment is consulted`); their nine `ENV_*` constants `agents/memory/store.py:186`, `agents/memory/beliefs.py:187,221,289,404`, `meetings/constants.py:51`, `meetings/manager.py:856`, `meetings/transcript.py:1354,1359` and the nine matching `__all__` entries; the thirteen production read sites `agents/memory/store.py:280,286,1632,1652`, `agents/memory/beliefs.py:1463,1465,1502,1826,1835,1841`, `meetings/manager.py:1185,1759,2018,2448`, `meetings/transcript.py:1554,1555`, `orchestrator/game.py:2713`; the dead private-helper parameter `meetings/transcript.py:2380-2385` with its own "survives only for direct callers" comment at `:2407-2410`; the stamp registry `orchestrator/replay.py:531-545` (`_RETIRED_ALWAYS_ON_LEVERS`, thirteen keys) and `:570-572` (`_TOGGLEABLE_LEVER_RESOLVERS`, one live entry); the rule this task amends, `AGENTS.md:62-75` (Graduation sweeps) beside craft rule 3 at `AGENTS.md:91-94`; `.env.example:68-97` (the graduated always-ON note); the test residue `tests/agents/test_absence_prior.py:166-216`, `tests/agents/test_beliefs_hard_evidence_gate.py:86-115`, `tests/agents/test_beliefs.py:2634-2660`, `tests/agents/test_episodic_ids.py:383-458`, `tests/meetings/test_citation_gate.py:127-158`, `tests/meetings/test_manager.py:475-512` and `:772` (`TestRollCallOffPath`, whose docstring says the round is skipped while its test asserts the round fires), `tests/meetings/test_contradictions.py:1531-1617`
**Complexity:** Medium
**Record impact:** post-record
**Measurement:** `grep -rnE 'def [a-z_]+_enabled\(' agents meetings orchestrator | wc -l` reads 11 at HEAD and must read 2 plus one per Phase-20 lever the record did NOT adopt; `grep -rnE 'ENV_(ROLL_CALL_ROUND|WHEREABOUTS_INTERIOR_FLAGS|VENT_PLACEMENT_CONTRADICTIONS|ABSENCE_PRIOR|CITATION_GATE|HARD_EVIDENCE_GATE|OBSERVATION_ID_RENDERING|EVIDENCE_QUALITY_LIFT|REPORTER_EXCULPATION)' tests/ | wc -l` reads 152 at HEAD and must read 0; `grep -rnE "accepted and ignored|no longer read|now always True" --include="*.py" agents meetings orchestrator | wc -l` reads 29 at HEAD and must read 0; `bash scripts/verify_samples.sh` stays 100/100 and `bash scripts/check.sh` is green.

Graduating a lever in this repo has so far meant deleting the env *read* and keeping the
*shape*. Nine resolvers of the form `def x_enabled(env: Mapping[str, str] | None = None) ->
bool: del env; return True` survive at HEAD — 200 source lines, each carrying a 12-to-31-line
docstring explaining a switch that no longer exists — with nine `ENV_*` constants "retained
for naming provenance", nine `__all__` exports, and thirteen production read sites that still
spell an unconditional behaviour as `if always_true():`. The review reproduced the tax three
ways and all three numbers reproduce byte-for-byte at HEAD today: 29 comment lines in
`agents/`, `meetings/` and `orchestrator/` say "accepted and ignored" / "no longer read" /
"now always True", and 152 lines of the test suite set environment variables that no
production code reads (`audits/review-2026-08-19/B/repo-health-architecture.md` §2 F6 — the
review's own grep, re-run by this contract with the same result). Of those 152, 94 live in a
single 538-line test class (`tests/orchestrator/test_replay.py:212-749`) whose job is to
assert that constants are constant.

One correction to the register, made at HEAD and to be carried into the phase file: C-64
counts **ten** accept-and-ignore resolvers, listing `agents/strategic/prompts/loader.py:264`
and `orchestrator/replay.py:110` among them. Both are LIVE — they read
`AILIBI_IMPOSTOR_ROLL_CALL` and return its parsed value; the 18.10 impostor-answer arm is
still default-OFF because the CREW-ONLY ruling did not ship it. The true count of
accept-and-ignore resolvers is **nine**, and the eleven-hit `def *_enabled(` grep is nine
dead plus two live. Likewise C-64's "13 `ENV_*` constants" is the size of
`_RETIRED_ALWAYS_ON_LEVERS`, not the constant count: the four Phase-13.5 levers were swept
properly at Task 14.9 and left nothing behind, which is the existence proof that this sweep
is achievable.

The class doubles the moment the adopting record lands. If the pre-registered decision rule
adopts baseline 7, the eight Phase-20 levers built default-OFF in wave 2 have their bodies
hard-return `True` and their keys move into `_RETIRED_ALWAYS_ON_LEVERS` — by construction
they become exactly the same residue, in exactly the same three modules. This task is the
first execution of craft rule 3 (`AGENTS.md:91-94`, "Retire means delete"), applied to both
generations at once, and it closes the loop by amending the older Graduation-sweeps rule at
`AGENTS.md:62-75`, which today demands only a *prose* sweep and explicitly blesses keeping
the function: *"the lever stays in the substrate stamp for provenance"*. That sentence is
true of the stamp KEY and false of everything else, and it is why nine dead functions
accumulated across five graduations.

Nothing observable moves. Every deleted branch is the branch production already takes, so the
committed bytes are the invariant and the gate is `verify_samples.sh` at 100/100 plus the
prompt byte-golden: if either moves, a deletion was not equivalent. The substrate stamp is
untouched — the keys stay in `_RETIRED_ALWAYS_ON_LEVERS`, `substrate_flag_snapshot()` keeps
stamping every one of them `True`, and a legacy replay stamped OFF keeps failing loud. What
goes is the resolver, its `env` parameter where nothing else reads one, the dead `if`, the
`ENV_*` constant, and the tests that pin a parameter — including the test class whose
docstring at `tests/meetings/test_manager.py:772` states the opposite of what its body
asserts (C-104's flagship example).

**Files in scope:**
- agents/memory/beliefs.py; (delete `evidence_quality_lift_enabled`, `reporter_exculpation_enabled`, `hard_evidence_gate_enabled`, `absence_prior_enabled`, their `ENV_*` constants and `__all__` entries, and collapse the read sites at :1463-1465, :1502, :1826, :1835, :1841; one history line per deleted lever)
- agents/memory/store.py; (same for `observation_id_rendering_enabled` and the `hard_evidence_gate_enabled` import; collapse `ids_on` at :280-286 and `gate_on` at :1632-1652; plus every Phase-20 store lever the record adopted)
- meetings/transcript.py; (same for `whereabouts_interior_flags_enabled` and `vent_placement_contradictions_enabled`; collapse :1554-1555 and delete the `whereabouts_interior_flags` parameter and its dead `False` branch at :2380-2410; plus every Phase-20 transcript lever the record adopted)
- meetings/manager.py; (same for `roll_call_round_enabled`; collapse :1185, :1759, :2018, :2448 and drop the `env` plumbing that only fed them; plus every Phase-20 manager lever the record adopted)
- meetings/constants.py; (delete `citation_gate_enabled`, `ENV_CITATION_GATE` and their `__all__` entries; `UNCITED_ZERO_FLAG_EJECT_MARKER` and the threshold constants stay)
- agents/strategic/prompts/loader.py; (the live 18.10 resolver STAYS — only its dangling `:func:` cross-references to deleted siblings at :253, :269, :271 are rewritten)
- orchestrator/replay.py; (the keys stay in `_RETIRED_ALWAYS_ON_LEVERS`; the resolver imports and any identity bindings for graduated levers go)
- tests/agents/; (the resolver-only classes and the tautology halves deleted; behaviour tests kept)
- tests/meetings/; (same, plus the new deletion-guard pin and its planted counter-case)
- AGENTS.md; (the Graduation-sweeps rule amended to "delete the mechanism, keep the stamp key and one history line", naming this task as its precedent)
- .env.example; (the newly graduated keys join the always-ON note; no lever gains a variable)
- orchestrator/game.py; (the hard_evidence_gate_enabled import and read-site; the stale narration beside it)
- tests/orchestrator/test_replay.py; (the graduated resolver/constant imports and parameter pins)
- meetings/render_contract.py; (one dangling resolver reference)
- eval/meeting_quality.py; (one dangling resolver reference)
- tests/eval/test_meeting_quality.py; (same)

**Files NOT in scope:**
- any lever the record did NOT adopt (it stays a live env-gated toggle with its resolver, parameter, tests and `.env.example` entry intact — the 18.10 impostor arm is the standing example)
- replays/ (the committed bytes are the pin, not an edit target; `verify_samples.sh` green is the invariant this task must not move)
- orchestrator/replay.py's `_TOGGLEABLE_LEVER_RESOLVERS` semantics and `substrate_flag_snapshot` behaviour (registration is not re-litigated here; only imports of deleted symbols change)
- the prompt templates under agents/strategic/prompts/qwen3_6_27b/ (no task except the single prompt-set bump may edit template bytes)
- tasks/ and agent_prompts/ (historical contracts record what was true when they were written and are never retro-edited)

**Definition of done:**
- [ ] Zero accept-and-ignore resolvers remain for graduated levers: a new AST-walking pin in `tests/meetings/test_lever_registry.py` parses every module under `agents/`, `meetings/` and `orchestrator/` and fails on any function whose name ends `_enabled` and whose body neither reads its `env` argument nor returns anything but a bare `True`; the pin ships with a planted counter-case (a fixture module written into `tmp_path` carrying exactly that shape) proving it bites.
- [ ] No `if <graduated>_enabled():` branch survives: each of the thirteen verified read sites is replaced by its always-taken side, with `ids_on`, `gate_on`, `lift_enabled`, `render_reporter` and the `absence_prior` disjunct in `meetings/manager.py:2448` folded into unconditional code, and `meetings/transcript.py::_detect_alibi_vs_sightings` loses its `whereabouts_interior_flags` parameter along with the `False` branch its own comment describes as reachable only by direct callers.
- [ ] The nine graduated `ENV_*` constants and their `__all__` entries are deleted; the nine snake_case keys remain in `orchestrator/replay.py::_RETIRED_ALWAYS_ON_LEVERS`, `SUBSTRATE_FLAG_KEYS` is unchanged in content and order, and `substrate_flag_snapshot()` in a bare environment still stamps every retired key `True` — pinned by one consolidated test that replaces the nine per-lever repeats.
- [ ] An `env` parameter survives on a public function only where a LIVE resolver still reads it: `render_for_prompt`, `detect_contradictions`, `apply_contradiction_rule`, `apply_meeting_evidence_rules`, `_build_belief_lines`, `_suspicion_graph_with_contradictions` and `TacticalAgent.suspicion_graph_for_meeting` each either keep `env` with a named live reader or lose it, and the PR states which and why for each.
- [ ] The test residue is gone and the keepers survive: the seven resolver-only classes named in Section refs are deleted, `TestRollCallOffPath` at `tests/meetings/test_manager.py:772` is deleted or renamed so no test name or docstring describes an OFF path that cannot exist, `test_marker_literal_pinned_exactly` and the behaviour halves of `TestObservationIdRenderLever` are preserved verbatim, and the three ON-path assertions in `tests/agents/test_impostor_answer_arm.py` are untouched because that lever is live.
- [ ] The three Measurement greps read their target values and the PR Summary pastes all three with before/after; the default pytest tier is smaller by the deleted line count, which the PR quotes from `git diff --stat`.
- [ ] `bash scripts/verify_samples.sh` reports 100/100 and `tests/meetings/test_prompt_byte_golden.py` is green over every committed meeting; the golden still fails on a one-byte perturbation of a template body, demonstrated in the PR, so the no-behaviour-moved claim rests on a gate that can fail.
- [ ] `AGENTS.md`'s Graduation-sweeps section states the amended rule — delete the resolver, its parameter, the dead branch and the parameter-pinning tests; keep the stamp key and one history line; the prose sweep remains the smaller half — and names this task as the precedent, with craft rule 3 cross-referencing it instead of restating it.
- [ ] `.env.example` lists every graduated lever in the always-ON note with its adopting record, documents no variable for any of them, and still documents exactly the live toggles read from `orchestrator/replay.py::_TOGGLEABLE_LEVER_RESOLVERS`; the existing registry-cross-check test stays green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Do this one lever at a time, never as a bulk regex pass, and commit per lever so a bisect
lands on a single symbol. The 19.19 deletion pattern applies verbatim.

Step 1 — read the record's verdict first. Open the record audit written by the adopting task
and list, explicitly, which Phase-20 levers graduated. `_RETIRED_ALWAYS_ON_LEVERS` after that
commit is the authoritative list; anything still in `_TOGGLEABLE_LEVER_RESOLVERS` is LIVE and
this task must not touch its resolver, its parameter, its tests or its `.env.example` entry.
Write that list at the top of the PR description before editing anything.

Step 2 — per symbol, grep the consumers before deleting. For each resolver name and its
`ENV_*` constant run the blast-radius grep over the whole tree, not just the files in scope,
and read every hit. Expect hits in three shapes: real read sites (collapse them), `__all__`
entries (delete), and prose `:func:` cross-references in modules that are not in scope
(rewrite where the module is in scope, and report the rest rather than widening scope
silently). Two known consumers sit outside this contract's files and are called out in the
notes below; if a third appears, stop and ask.

Step 3 — collapse, do not comment out. `ids_on = observation_id_rendering_enabled(env)`
followed by `if ids_on:` becomes the body of the `if`, dedented, with the guard gone. A
disjunct like `or (evidence.absent and absence_prior_enabled(env))` becomes `or
evidence.absent`. A ternary like `reporter_id if reporter_exculpation_enabled() else None`
becomes `reporter_id`. After each collapse run the module's own test file plus
`tests/meetings/test_prompt_byte_golden.py` before moving on — a wrong collapse shows up as a
prompt-byte diff immediately, and finding it one lever at a time costs minutes instead of a
bisect.

Step 4 — the parameter is the subtle part. `env` is threaded through several public
signatures purely to reach these resolvers. Delete it only where the grep proves no live
resolver is reached from that call chain; where a Phase-20 lever survived the record, `env`
survives with it. Leaving a parameter that nothing reads is the exact defect this task
exists to remove, and deleting one a live lever needs breaks the toggle silently, so record
the decision per signature in the PR.

Step 5 — the tests. Delete whole classes where the class exists only to assert a constant;
inside mixed classes delete only the tautology methods and keep the behaviour ones. Replace
the nine per-lever stamp repeats with one test that asserts the full retired tuple stamps
`True` under a bare mapping, an explicit "0", a junk value and the ambient process
environment — one test, four cases, the whole registry. The new AST guard belongs beside it;
give it a planted bad module in `tmp_path` so it is a gate rather than prose.

Step 6 — the docstrings that survive. Each lever's mechanism keeps one trailing provenance
line naming its adopting record, and nothing more; the 12-to-31-line narrations go with the
functions. Do not migrate the narration into the surviving mechanism docstring — that
converts a deletion into a move and the reader is no better off.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import check_doc_facts"`
- `uv run python -c "import eval.leak_scan"`
- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`
- `uv run python -c "import tests._helpers.committed"`
- `uv run python -c "import eval.validity"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import api.schemas"`

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
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-20-graduation-sweep` with a title like `task 20.37: retire means delete: the post-record graduation sweep and the old accept-and-ignore residue`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing C-64 and C-104 in `audits/review-2026-08-19/B/collated-findings.md` §4 and §5; RC6 in `audits/review-2026-08-19/D/FINAL-synthesis.md` §1 ("the render-version stamp, plus one deletion pass"); the per-area sources `audits/review-2026-08-19/B/repo-health-architecture.md` §2 F6, `audits/review-2026-08-19/B/agents-memory.md` §2 F4, `audits/review-2026-08-19/B/meetings-transcript-voting.md` §2 F5, `audits/review-2026-08-19/B/meetings-manager.md` §2 P1-3, `audits/review-2026-08-19/B/orchestrator.md` §2 (the `suspicion_graph_for_meeting` dead-kwarg leg). Anchors RE-VERIFIED at HEAD: the nine accept-and-ignore resolvers `agents/memory/store.py:189`, `agents/memory/beliefs.py:190,224,292,407`, `meetings/constants.py:54`, `meetings/transcript.py:1362,1389`, `meetings/manager.py:859` (200 source lines in total, each ending `del env  # retired: the lever is unconditional, no environment is consulted`); their nine `ENV_*` constants `agents/memory/store.py:186`, `agents/memory/beliefs.py:187,221,289,404`, `meetings/constants.py:51`, `meetings/manager.py:856`, `meetings/transcript.py:1354,1359` and the nine matching `__all__` entries; the thirteen production read sites `agents/memory/store.py:280,286,1632,1652`, `agents/memory/beliefs.py:1463,1465,1502,1826,1835,1841`, `meetings/manager.py:1185,1759,2018,2448`, `meetings/transcript.py:1554,1555`, `orchestrator/game.py:2713`; the dead private-helper parameter `meetings/transcript.py:2380-2385` with its own "survives only for direct callers" comment at `:2407-2410`; the stamp registry `orchestrator/replay.py:531-545` (`_RETIRED_ALWAYS_ON_LEVERS`, thirteen keys) and `:570-572` (`_TOGGLEABLE_LEVER_RESOLVERS`, one live entry); the rule this task amends, `AGENTS.md:62-75` (Graduation sweeps) beside craft rule 3 at `AGENTS.md:91-94`; `.env.example:68-97` (the graduated always-ON note); the test residue `tests/agents/test_absence_prior.py:166-216`, `tests/agents/test_beliefs_hard_evidence_gate.py:86-115`, `tests/agents/test_beliefs.py:2634-2660`, `tests/agents/test_episodic_ids.py:383-458`, `tests/meetings/test_citation_gate.py:127-158`, `tests/meetings/test_manager.py:475-512` and `:772` (`TestRollCallOffPath`, whose docstring says the round is skipped while its test asserts the round fires), `tests/meetings/test_contradictions.py:1531-1617`), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
