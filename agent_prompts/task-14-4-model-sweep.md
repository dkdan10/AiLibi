# Agent Prompt — 14.4 Featherless model × thinking-mode sweep over reconstructed 9p2i contexts

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.4 — Featherless model × thinking-mode sweep over reconstructed 9p2i contexts, anchored to audits/audit-2026-06-25-0859-phase-13-close.md (the information-ceiling hypothesis); experiments/lab/report-model-ceiling-probe.md (the model-ceiling-vs-information method); experiments/lab/deflection_probe.py (the cover-directive injection); replays/samples/9p2i. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-model-sweep`
**Depends on:** 14.1, 14.3
**Section refs:** audits/audit-2026-06-25-0859-phase-13-close.md (the information-ceiling hypothesis); experiments/lab/report-model-ceiling-probe.md (the model-ceiling-vs-information method); experiments/lab/deflection_probe.py (the cover-directive injection); replays/samples/9p2i
**Complexity:** Integration

Operator-run sweep ($0 marginal): run each candidate Featherless model over the SAME reconstructed
opening/reply/vote contexts from committed `replays/samples/9p2i`, on the PINNED 9B prompts, in both
non-thinking and thinking mode where available, and grade with the identical mechanical `_grade`
(`self_co_locates_body`, `new_self_flag`, `deflects_legal`) + per-model structured-output parse-success rate.
Also run the cover-directive 2×2 (model × {cover OFF, cover ON-reply}, via `deflection_probe._cover_directive`)
to settle whether the impostor self-incrimination tell is a capability ceiling, a prompt artifact, both, or
the information ceiling. Emit a comparison report proposing a recommended (meeting_model, trigger_model, mode)
tuple WITH its evidence — including an honest statement of whether the information-ceiling hypothesis holds.

**Files in scope:**
- experiments/lab/featherless_sweep.py (new: the matrix driver over vote/opening/reply corpora × models × {pinned-9B prompts, cover ON/OFF} × {non-thinking, thinking} × {flag-OFF, flag-ON substrate}, reusing `model_ceiling_probe.do_dump` to freeze contexts once per substrate and `grade-frontier` to grade)
- experiments/lab/results-featherless-sweep.jsonl (new: per-cell mechanical grades + parse-success + tokens + latency + the `substrate_flags` config)
- experiments/lab/report-featherless-sweep.md (new: the comparison table, the model-ceiling-vs-information read, the cover-directive quadrant verdict, the per-model flag-OFF vs flag-ON substrate delta, and the recommended tuple with evidence)

**Files NOT in scope:**
- llm/ (the adapter is 14.1) + experiments/model_probe/probe.py + experiments/lab/deception_battery.py + experiments/lab/deflection_probe.py + experiments/lab/model_ceiling_probe.py + experiments/lab/probe_backends.py (14.2/14.3 own those; this consumes them)
- agents/strategic/prompts/ (prompt VARIANTS are tested by injection/registry, NOT by editing templates here; authoring a new set is 14.5)
- replays/samples/ (read-only; no re-record)
- orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS` unchanged until a baseline locks)

**Definition of done:**
- [ ] Each candidate model (`Qwen/Qwen3-32B`, `Qwen/Qwen3-30B-A3B`, `zai-org/GLM-4-32B`, `TheDrummer/Cydonia-24B-v2` [RP/creative]) — AND the 9B reference — runs over the SAME reconstructed contexts on the PINNED 9B prompts, in non-thinking and thinking mode where available (driven by the request-time thinking toggle from 14.1, threaded via 14.3 — not the response-side policy), on BOTH the flag-OFF (legacy) and flag-ON (corrected 13.5) substrate (two columns; flag-ON contexts re-derived offline by setting the 4 `AILIBI_*` env vars); each result row carries its `substrate_flags`; mechanical metrics + per-model parse-success rate are tabulated per substrate against the 9B.
- [ ] The cover-directive 2×2 (model × {cover OFF, cover ON-reply}) is run and the report states the quadrant verdict: capability ceiling / prompt artifact / both / information ceiling.
- [ ] The report states the per-model SUBSTRATE delta (flag-ON vs flag-OFF): does the corrected 13.5 substrate help THIS model decide where the 9B degraded (a voter at suspicion 1.00 over the 0.60 gate, meeting STILL SKIPPED)? — separating "corrected memory helps the model" from "the model is just stronger."
- [ ] Per-model structured-output fidelity (parse-success under `response_format`) is reported; any model that cannot reliably emit schema-valid JSON is flagged unfit for the sim.
- [ ] A recommended (meeting_model, trigger_model, mode) tuple is proposed WITH evidence; the report states honestly whether the information-ceiling hypothesis is supported (tell persists across all models) — a valid finding either way.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Reuse `model_ceiling_probe.do_dump` to freeze the hard body-meeting contexts once (`contexts.pkl`), then run
each Featherless model/mode as a new `--tag` graded by the IDENTICAL `_grade` / `grade-frontier` so the only
moving variable is the model (and, in the 2×2, the cover injection from `deflection_probe._cover_directive`).
For votes, drive `experiments/model_probe/probe.py --backend featherless` with its existing variant registry.
This generalizes `model_ceiling_probe.py:11-14` ("if self-flagging does NOT fall as model strength rises, the
binding constraint is INFORMATION not the model") across Featherless models. Operator session: set
`FEATHERLESS_API_KEY`; bounded concurrency for behavior passes, a sequential pass for latency. $0 marginal,
but watch token usage against the 32K context and the frozen 2048/1024 caps. Build the flag-ON (corrected
13.5) contexts by setting the 4 env vars (`AILIBI_TESTIMONY_AS_CONTENT` / `AILIBI_WITNESSED_KILL_EVIDENCE` /
`AILIBI_MOVEMENT_PERCEPTION` / `AILIBI_UNFREEZE_MEMORY`) before the context reconstruction (`ReplayLoader` /
`build_*_contexts` re-derive memory through the `*_enabled()` reads), and the flag-OFF column with them unset;
the levers are replay-deterministic over the committed (flags-OFF) replays, so no re-record is needed. Tag
every row's `substrate_flags`. Slate ids (HuggingFace repo form, owner-confirmed 2026-06-28):
`Qwen/Qwen3-32B` (quality baseline; the adapter default), `Qwen/Qwen3-30B-A3B` (MoE / speed), and
`zai-org/GLM-4-32B` (agentic) — these three are live-verified on Featherless (PR #202) — plus the RP/creative
wildcard `TheDrummer/Cydonia-24B-v2` (confirm it is served via `GET {base_url}/v1/models` before the run; an
unrecognized id is a hard HTTP 400). The thinking axis (`request_thinking` True/False) applies ONLY to the
two Qwen3 models (native `enable_thinking`); `zai-org/GLM-4-32B` and the RP tune run non-thinking only.

## Integration risk

This is where the strategic risk lives. The mechanical isolated-turn metrics here are PROXIES, not the live
R-gate — a model can deflect better in isolation yet still CORRECTLY SKIP in a noisy full game (the Phase-13
information-ceiling hypothesis). The report must distinguish "emits better turns in isolation" from "raises R1
in a full game," and the lock (14.6) must read this report as evidence, not verdict. Do not let one strong
model's good single-corpus numbers stand in for "the model fixes R1." Operator spend is $0 marginal but the
sweep must not be silently truncated — log the model/mode/context matrix actually run.

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

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-14-model-sweep` with a title like `task 14.4: featherless model × thinking-mode sweep over reconstructed 9p2i contexts`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-2026-06-25-0859-phase-13-close.md (the information-ceiling hypothesis); experiments/lab/report-model-ceiling-probe.md (the model-ceiling-vs-information method); experiments/lab/deflection_probe.py (the cover-directive injection); replays/samples/9p2i), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
