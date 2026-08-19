# Agent Prompt — 3.20 Subject-field correctness (accusation-round `agent_id` threading + claim-subject normalization)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.20 — Subject-field correctness (accusation-round `agent_id` threading + claim-subject normalization), anchored to DESIGN.md §5.3, DESIGN.md §5.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-subject-field-correctness`
**Depends on:** 3.19 merged
**Section refs:** DESIGN.md §5.3, DESIGN.md §5.4
**Complexity:** Small

Close the two non-blocking data-artifact observations surfaced by §9 of
the seventh Pre-Phase-4 real-provider eval at
`audits/audit-2026-05-26-0325-pre-phase-4-real-provider-eval.md`. The
eval **passed all five Phase 3 merge criteria** (50/50 games, 38%
impostor win rate, $0.018 mean cost, 100% sampled readability, replay
completeness). Phase 3 closure is no longer eval-gated; this task is a
Phase-4-prelude that fixes a quiet correctness hole the auditor flagged
because Task 3.11's contradiction detector keys on `subject` matching
across speakers, and the corrupted subjects observed below silently
disable that mechanism.

**Finding 1 (Subject hallucination on accusation-round self-alibi):
seed 24 statements emit `subject: "p-0"` for non-reporter speakers.**
All four statements emitted by non-reporting speakers (`p-2`, `p-4`) in
seed 24 carry `subject: "p-0"` in their structured alibi claims, even
though `p-0` is not a player in that game. The reporter (`p-3`) emits
the correct `subject: "p-3"`. Root cause is structural: unlike
`impostor_report_prompt` (which receives `agent_id` and threads it into
the self-alibi example via `{{ agent_id }}` per Task 3.18),
`accusation_round_prompt` at [agents/strategic/prompts/loader.py:117](agents/strategic/prompts/loader.py#L117)
takes `rendered_memory`, `transcript`, and `contradictions` only — no
`agent_id`. The template at [agents/strategic/prompts/accusation_round.j2](agents/strategic/prompts/accusation_round.j2)
documents the alibi-claim shape generically (line 158: "Places a player
(usually yourself) in a room over a tick range") without a concrete
self-id anchor. The model falls back to a default — empirically `p-0`
— when emitting a self-alibi.

**Finding 2 (Subject hallucination on impostor self-alibi):
seed 49 impostor report emits `subject: "p-self"`.** Task 3.18 injected
`{{ agent_id }}` into the impostor template's self-alibi example
(`agents/strategic/prompts/impostor_report.j2:106`), so the literal
example renders as `"subject": "p-4"` for player 4. Sonnet 4.6 still
nondeterministically emits `"p-self"` (the `p-` prefix from sibling
examples concatenated with the conceptual `self` token). The schema
accepts it because `PlayerId` is just `str` (no runtime validation;
see [engine/entities.py:11](engine/entities.py#L11)). The post-3.18
fix is a prompt-only fix; it does not catch this variant.

Both findings are structured-field corruption: prose `rationale_text`
and accusation reasoning remain coherent (the auditor's transcript
rubric confirms this — both games scored Pass-with-Partial-on-Grounded,
and votes correctly ejected the impostor). What breaks is the
mechanical layer: contradiction detection (DESIGN.md §5.4) indexes
alibis by `(subject, tick_range, location)`. A claim with
`subject: "p-0"` (non-existent player) or `subject: "p-self"`
(non-canonical token) cannot participate in cross-speaker
contradiction analysis with any other speaker's claims. The detector
silently fails to match instead of flagging the conflict it should
flag.

This task closes both findings in one bundled PR. Same defect family
(structured `subject` field corruption); same two-layer fix (prompt
anchor + defensive code normalizer).

**Out of scope** (explicit decisions deferred):

- **Promoting `PlayerId` to a Pydantic-validated constrained type.**
  Would catch unknown subjects at schema-validation time across every
  meeting artifact. Larger refactor; touches every consumer of
  `PlayerId`. Defer until the simpler prompt + targeted normalizer fix
  is proven insufficient by a future eval.
- **Refactoring `AlibiClaim` to split `self_alibi` from `other_alibi`
  variants.** Would force the discriminator to carry the speaker-vs-
  other distinction, structurally eliminating the "is this `subject` me
  or someone else?" question. Larger schema change; affects Task 3.11
  contradiction-detection code. Defer.
- **Auditing the other claim subject fields** (`AccusationClaim.against`,
  `CorroborationClaim.supports`, `SawPlayerObservation.subject`,
  `FoundBodyObservation.body_of`) for the same hallucination pattern.
  The eval did not surface those variants in the sampled games, but
  the same root cause (unconstrained `PlayerId`-shaped string + no
  prompt-side anchor for `other`-player ids) plausibly applies. Defer
  to a future hygiene task; the current normalizer should be designed
  so it can be extended to those fields without re-architecting.
- **Crewmate report template review.** The crewmate template
  (`agents/strategic/prompts/crewmate_report.j2`) already injects
  `agent_id` into its prompt context (per Task 3.18's debug report
  §5). The eval's seed 22 / 26 transcripts showed correctly-populated
  `subject` fields in the crewmate reporter slot. No change needed.

**Files in scope:**
- agents/strategic/prompts/loader.py
- agents/strategic/prompts/accusation_round.j2
- meetings/manager.py
- tests/meetings/test_manager.py
- tests/agents/test_strategic_prompts.py

**Files NOT in scope:**
- llm/
- meetings/schemas.py
- meetings/transcript.py
- meetings/voting.py
- meetings/__init__.py
- agents/strategic/prompts/crewmate_report.j2
- agents/strategic/prompts/impostor_report.j2
- agents/strategic/prompts/vote_ballot.j2
- agents/strategic/prompts/__init__.py
- agents/strategic/reasoner.py
- agents/strategic/output_schemas.py
- agents/memory/
- agents/tactical/
- agents/
- engine/
- observation/
- orchestrator/
- api/
- frontend/
- eval/
- scripts/
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- DESIGN.md
- pyproject.toml
- uv.lock
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- tests/engine/
- tests/observation/
- tests/orchestrator/
- tests/eval/
- tests/llm/
- tests/test_firewall.py

**Definition of done:**
- [ ] **Thread `agent_id` through `accusation_round_prompt`.** Add `agent_id: PlayerId` to the keyword-only signature of `accusation_round_prompt` at [agents/strategic/prompts/loader.py:117](agents/strategic/prompts/loader.py#L117), and pass it into the Jinja render context. The parameter is positional-keyword, required (no default) — matches the impostor_report pattern at [agents/strategic/prompts/loader.py:90](agents/strategic/prompts/loader.py#L90).
- [ ] **Update `accusation_round.j2` to render a concrete self-alibi example.** Inject the speaker's own `agent_id` into the alibi-claim documentation in the template's `## Your task` section so the model sees `"subject": "p-X"` (the actual speaker id) as the canonical self-alibi shape, not the generic word `"yourself"`. Place the example alongside the existing alibi-claim description at [agents/strategic/prompts/accusation_round.j2:158](agents/strategic/prompts/accusation_round.j2#L158); follow the impostor template's pattern at [agents/strategic/prompts/impostor_report.j2:106](agents/strategic/prompts/impostor_report.j2#L106) for symmetry. Preserve every other section of the template (game-rule framing, transcript rendering, contradiction-flag section, output constraints) verbatim.
- [ ] **Bump `accusation_round` template version.** The prompt-version map at meeting-entry level (per R-3 placement, verified in §7 of the eval audit) records `"accusation_round": "accusation_round.v1"`. After this template change, the version string must increment (e.g. `accusation_round.v2`). The version is sourced from the template's leading-comment `version:` field at [agents/strategic/prompts/accusation_round.j2:4](agents/strategic/prompts/accusation_round.j2#L4) — change `version: 1` to `version: 2`. Wherever this string flows into `prompt_versions` (likely `_meeting_prompt_versions` in `meetings/manager.py` or an adjacent helper), it should pick up the new value automatically; verify in the post-merge smoke that a fresh replay entry shows `accusation_round.v2`.
- [ ] **Wire `agent_id` through `_collect_statement`.** In `meetings/manager.py::_collect_statement` (around [meetings/manager.py:557](meetings/manager.py#L557)), pass `agent_id=participant.agent_id` into the `self._statement_prompt(...)` call at line 567. The `StatementPromptRenderer` Protocol may need its signature widened in the same module — pick the cleanest spot (likely the Protocol definition near the top of `meetings/manager.py`). Identity-field override at lines 601–608 stays unchanged; the new wiring is prompt-context only.
- [ ] **Defensive subject normalization in report + statement parse paths.** Add a helper `_normalize_self_alibi_subjects(claims, *, speaker_id) -> tuple[Claim, ...]` (or similar; name picked by implementing agent) in `meetings/manager.py`. The helper walks the parsed `claims` tuple, finds every `AlibiClaim`, and rewrites `subject` to `speaker_id` IF the raw `subject` matches any of:
  - exact `"self"` (Task 3.18 reference token — already covered by prompt fix but defense-in-depth)
  - exact `"p-self"` (Finding 2 from this task — the prompt-only fix did not catch this)
  - exact `"{{ agent_id }}"` (unrendered Jinja placeholder — paranoid case; would only happen on a rendering bug)
  - any other claim subject left as-is (non-self alibis MUST pass through unchanged; this normalizer's contract is "fix the speaker's self-alibi only").
  Invoke the helper inside `_collect_one_report` after `model_validate_json` and before `model_copy` (around [meetings/manager.py:543-553](meetings/manager.py#L543-L553)), and inside `_collect_statement` after `model_validate_json` and before `model_copy` (around [meetings/manager.py:597-608](meetings/manager.py#L597-L608)). The rewrite is via `model_copy(update={"claims": normalized})` — preserves Pydantic immutability.
- [ ] **Out-of-roster subject pass-through is documented.** The helper docstring must explicitly state: claims with `subject` that's NOT in the self-alibi placeholder set are passed through unchanged. This task does NOT attempt to validate `subject` against the meeting's player roster — that's the larger refactor explicitly deferred above. Document the rationale (Task 3.11 contradiction detection will silently fail to match unknown subjects, which is no worse than today; the goal of THIS task is to fix the deterministic placeholder-leak cases, not to mechanically validate all subjects).
- [ ] **Unit test: `accusation_round_prompt` renders speaker's own id.** Add to `tests/agents/test_strategic_prompts.py`. Build a minimal `MeetingTranscript` + empty contradictions tuple, call `accusation_round_prompt(agent_id="p-3", ...)`, assert the rendered string contains `"p-3"` in a context that would anchor a self-alibi (e.g. the rendered example contains `"subject": "p-3"`).
- [ ] **Unit test: claim-subject normalizer rewrites placeholder variants.** Add to `tests/meetings/test_manager.py`. Construct a `ReportDocument` (or `Statement`) with three `AlibiClaim`s carrying `subject` values `"self"`, `"p-self"`, and `"p-4"` (the real id). Speaker is `"p-4"`. Call the normalizer; assert all three results have `subject == "p-4"`.
- [ ] **Unit test: normalizer passes non-self subjects through.** Same setup as above but with `subject` values `"p-2"` (another real player) and `"p-99"` (a hallucination that's neither in the self-placeholder set nor in the roster). Assert both pass through unchanged. Rationale: this task does not validate against roster.
- [ ] **Unit test: prompt-version bump shows in replay record.** Add to `tests/meetings/test_manager.py` (or extend an existing meeting integration test). Run a fake-provider meeting; inspect the resulting `MeetingReplayEntry`'s `prompt_versions` map; assert it contains `"accusation_round": "accusation_round.v2"` (the new version), not `v1`.
- [ ] **Post-merge local verification.** With `AILIBI_LLM_PROVIDER=fake`:
  - Run `uv run pytest tests/meetings/ tests/agents/test_strategic_prompts.py -v` — all tests pass, new tests pass.
  - Run a 5-game smoke (seeds 20–24 via `scripts/run_game.py`); confirm at least one meeting fires; grep the replay JSONL for `"accusation_round": "accusation_round.v2"`; confirm no `"subject": "p-self"` or `"subject": "self"` strings appear anywhere in the meeting transcript JSON.
  - Paste verbatim outputs (test results, smoke replay grep results) into `## Decisions`.
- [ ] **`@real_provider` regression test (opt-in).** Add to `tests/llm/test_real_provider.py` a test that runs a single meeting (or just the statement turn for a seeded scenario) against the live provider and asserts no statement's `claims[*].subject` is in `{"self", "p-self"}`. Skipped in CI by default. Cost: ~$0.10 per invocation; defer running locally to the next eval pass (the next 50-game real-provider eval is the canonical acceptance gate).
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import orchestrator.game"`
- `uv run python -c "import agents.strategic.reasoner"`
- `uv run python -c "import llm.budgeted_client"`
- `uv run python -c "import meetings.manager"`

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
Open a PR from branch `phase-3-subject-field-correctness` with a title like `task 3.20: subject-field correctness (accusation-round `agent_id` threading + claim-subject normalization)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.3, DESIGN.md §5.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
