# Agent Prompt — 19.3 ES portability: a portable sampler or a narrowed claim

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.3 — ES portability: a portable sampler or a narrowed claim, anchored to audits/audit-phase-19-triage.md C1 + §7 item 3 [S-Codex, platform-scoped; §8 row 1]; training/bakeoff/es.py:24-26 (the "bit-stable across machines" promise), :184-193 (`rng.gauss` in `_mutate` and `_random_genome`); tests/training/test_es.py:74-91 (the fixed digest pin, no platform guard); tasks/phase-18.md:2656-2659 (the recorded Darwin-arm64 divergence); the three reproducibility scopes (19.1). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-es-portability`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-19-triage.md C1 + §7 item 3 [S-Codex, platform-scoped; §8 row 1]; training/bakeoff/es.py:24-26 (the "bit-stable across machines" promise), :184-193 (`rng.gauss` in `_mutate` and `_random_genome`); tests/training/test_es.py:74-91 (the fixed digest pin, no platform guard); tasks/phase-18.md:2656-2659 (the recorded Darwin-arm64 divergence); the three reproducibility scopes (19.1)
**Complexity:** Medium

The standing gate is green on Linux and recorded red on Darwin-arm64 twice (the Codex
audit run and the phase-18 close note): `es.py` promises a cross-machine bit-stable
stream while `random.Random.gauss()` rides libm, the leading — but unisolated — cause.
FIRST DoD step (verify-then-fix): reproduce the promise/pin relationship at HEAD and
identify which operations in the sample path are platform-sensitive by construction.
Then, primary path: implement a specified portable normal sampler (pure arithmetic over
`random()` draws — IEEE-754 basic ops and `math.sqrt` are correctly rounded and portable;
LIBM-backed `math.log`/`math.exp` are not, so any transcendental the algorithm needs is
implemented in-module as a documented pure-arithmetic routine; see the hint) and
regenerate the golden digest. Fallback path
(only if bit-portability cannot be established): narrow the in-code claim to the
supported pin and platform-guard the test. Never just re-pin the hash — that conceals the
unsupported promise. The ES program is frozen: no artifact retrains, the shipped champion
weights and acceptance gates are untouched (the golden pins the OPTIMIZER stream, not any
shipped artifact).

**Files in scope:**
- training/bakeoff/es.py
- tests/training/test_es.py

**Files NOT in scope:**
- agents/tactical/learned/ (shipped weights and parity gates untouched)
- training/bakeoff/harness.py + training/bakeoff/utility_es.py (consumers of the ES core, not edited)

**Definition of done:**
- [ ] Verify-then-fix recorded: the platform-sensitive call(s) identified with the reasoning in the module docstring, and the old promise text quoted in the PR.
- [ ] The replacement sampler is provably GAUSSIAN, not merely deterministic: pinned distribution-quality assertions over the fixed stream (symmetry, mean, variance, and a sigma-scaled tail check at minimum) guard against a portable-but-degenerate sampler silently replacing the documented isotropic mutation distribution.
- [ ] Primary path: the sampler's algorithm is documented (name + why each operation is portable), a double-run on this host is digest-identical, and the new golden is pinned — but the CROSS-PLATFORM claim is not advertised until the digest is confirmed on the divergent platform: an owner-assisted Darwin-arm64 run (minutes — the recorded failure host) matches the Linux digest, recorded in the test's comment. Until that comparison exists the in-code claim uses the narrowed wording even on the primary path (designed-portable, cross-platform digest pending). Fallback path: the claim text states exactly what is guaranteed (same-runtime repeatability) and the test carries an explicit platform pin/guard with the Darwin divergence cited.
- [ ] The in-code claim and README's reproducibility-scopes text (19.1) agree — coordinate wording, not files.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The platform hazard is LIBM, not the mathematics: inverse-CDF approximations (Acklam,
AS241) are rational in the central region but their tail transform needs
`sqrt(-2·ln p)` — no polynomial choice removes the logarithm, so "avoid transcendentals"
is unrealizable as an instruction. The realizable rule: any transcendental the sample
path needs (ln, for the tails) is implemented IN-MODULE as a documented pure-arithmetic
routine over IEEE-754 basic ops — `math.frexp` (exact) for range reduction plus a
series/polynomial evaluated in explicit float64 — never `math.log`/libm; `math.sqrt` is
correctly rounded per IEEE-754 and portable. Document coefficient provenance and the
approximation's bounded deviation, and pin the distribution-quality assertions from the
DoD. Keep the `rng.gauss` path available nowhere (one sampler, one stream); regenerating
the golden is a deliberate, documented ES drift — say so in the pin's comment, quoting
this task id. If the pure-arithmetic route proves unreasonable in practice, the narrowed
fallback is the honest exit, not a libm call.

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

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-19-es-portability` with a title like `task 19.3: es portability: a portable sampler or a narrowed claim`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md C1 + §7 item 3 [S-Codex, platform-scoped; §8 row 1]; training/bakeoff/es.py:24-26 (the "bit-stable across machines" promise), :184-193 (`rng.gauss` in `_mutate` and `_random_genome`); tests/training/test_es.py:74-91 (the fixed digest pin, no platform guard); tasks/phase-18.md:2656-2659 (the recorded Darwin-arm64 divergence); the three reproducibility scopes (19.1)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
