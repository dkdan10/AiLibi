# Agent Prompt — 14.7 Smoke → re-record BOTH sets on the locked model + new prompts + validity gate

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.7 — Smoke → re-record BOTH sets on the locked model + new prompts + validity gate, anchored to DESIGN.md §11.4, §3.5 (replay provenance, canonical set); agent_prompts/task-9-5-model-migration-rerecord.md (the migration shape); tasks/phase-14.md (the locked tuple from 14.6); scripts/refresh_samples.sh. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-featherless-rerecord`
**Depends on:** 14.1, 14.6
**Section refs:** DESIGN.md §11.4, §3.5 (replay provenance, canonical set); agent_prompts/task-9-5-model-migration-rerecord.md (the migration shape); tasks/phase-14.md (the locked tuple from 14.6); scripts/refresh_samples.sh
**Complexity:** Integration

Operator-run spend/time gate. With the tuple locked at 14.6, smoke first (3–5 seeds at 9p2i) to confirm the
thinking policy holds and structured-output parse-success ≈ 100% under the FROZEN token caps, project the
full-run wall time, and STOP for operator go. Then re-record BOTH committed sets (4p1i + 9p2i, all 50 seeds)
on the locked Featherless model + new prompt set with ALL 4 13.5 substrate flags ON, in ONE atomic PR,
STAMPING the flag config into the MANIFEST (a new `flags` column) + the replay metadata so a replay
self-describes which substrate generated it, regenerate reports + MANIFESTs + prompt-regression fixtures +
baseline, verify byte-identical reconstruction from the new recordings WITH the same 4 flags set and
roster.json present, and pass the HARD validity gate. This new baseline replaces the final-9B one as
canonical. Win split moves in any direction and is REPORTED, not gated (the R-gate is 14.8).

**STATUS (2026-07-01) — COMPLETE (PR #213).** The v3 re-smoke cleared the gate (parse 99.19%, ZERO
1024-truncations), both sets re-recorded on the locked tuple, HARD validity gate PASS, byte-identical
flag-aware reconstruction holds; the baseline is canonical. Headline: R1 eject-decided 27/50 (9B: 3/50),
impostor win 0.32 (9B: 0.84). Measured wall time: **~5h for both 50-seed sets with 2 parallel seed workers**
(each worker running the next available seed) — far under the 13–30h projection; use ~5h for future re-record
planning (14.12). Carried findings → 14.8: ejection accuracy 0.566, the 5-row crew railroad (10.1 cap defeated
at 4× flag density; tripwire downgraded to a regression pin), 23 missed-deadline markers. History below.

**STATUS (2026-06-30, historical) — infra landed; resumed at the re-smoke:**
- The 14.7 flag-stamping infrastructure is MERGED to main (PR #209): the MANIFEST `flags` column
  (`scripts/_manifest_writer.py`), the additive-optional substrate stamp on the replay `game_over` record
  (`orchestrator/replay.py`), the flag-aware loader guard (`api/replay_loader.py`,
  `ReplaySubstrateMismatchError`), and `scripts/refresh_samples.sh` Featherless support — which now FAILS LOUD
  before staging any seed unless the 14.6-locked substrate (`AILIBI_PROMPT_SET=qwen3_32b` + all 4 flags = `1`)
  is exported. So the re-record PR does NOT rebuild any of that; it produces the replay BYTES + regenerated
  reports/MANIFESTs/fixtures + re-pinned byte tests only.
- The FIRST smoke (2026-06-30, locked tuple) NO-GO'd: parse-success ~88.5% on a complete game (seed 0: 46/52),
  with 2 unterminated-JSON vote-cap truncations at the frozen 1024 cap + 4 schema-adherence failures. Root
  cause: the 14.4/14.5 sweep tested only reply+vote corpora (never the opening turns) and votes at a 4096-token
  budget, not the production 1024 cap — so it could not surface these. The `qwen3_32b` set was hardened to
  **v3** for full-game schema adherence + a compact-ballot fix (PR #209). The task now RESUMES at a re-smoke on
  v3; the bar to clear before the full re-record is parse-success ≈ 100% AND zero 1024-truncation.

**Files in scope:** (the atomic re-record PR only — the flag-stamping infra is already on main, PR #209)
- replays/samples/4p1i/ (50 replays + tournament-eval-report.json + MANIFEST.md re-recorded on the locked model, all 4 flags ON; model + prompt_versions + `flags` + git_sha rows updated)
- replays/samples/9p2i/ (50 replays + report + MANIFEST re-recorded, all 4 flags ON; roster sidecar {9,2,2} unchanged)
- tests/fixtures/prompt_regression/ (v_a + v_b fixtures + baseline.json regenerated — provider + substrate + prompt set changed)
- tests/api/test_replay_loader.py (committed-set BYTE pins re-verified on the new recordings)
- tests/eval/test_win_condition_selfcheck.py (committed-set pins re-verified on the new bytes)
- tests/scripts/test_manifest_writer.py (MANIFEST row pins for the locked model + `qwen3_32b.v3` prompt_versions + the new `flags` cell)

**Files NOT in scope:**
- the 14.7 flag-stamping infra — `scripts/_manifest_writer.py` (flags column), `orchestrator/replay.py` (stamp), `api/replay_loader.py` (guard) — plus `scripts/refresh_samples.sh` Featherless support + the locked-substrate preflight guard + their behavior tests: ALL LANDED on main (PR #209); the re-record CONSUMES them, it does not re-edit them
- engine/ + meetings/ + agents/ + llm/ + eval/ source (behavior landed in 14.1 / 14.5; this records + regenerates only)
- meetings/manager.py (token caps FROZEN — turn 2048 / vote 1024; do NOT raise; the 9.5 ctx-overrun lesson)
- agents/strategic/prompts/ (no template authoring here; this records the chosen prompt set, it does not edit it)
- the 13.5 flag-source logic (the `*_enabled()` resolvers + flag gates) — 14.7 sets the flags ON via env + STAMPS the config; it does NOT change the flag logic (default-ON + retiring the OFF path is 14.9)
- audits/workflows/extract_gameplay_facts.py (run read-only for the funnel; do not modify)

**Definition of done:**
- [ ] RE-smoke first (3–5 seeds at 9p2i) on the `qwen3_32b` **v3** set — the FIRST smoke NO-GO'd at ~88.5% parse: thinking policy holds under `fail_loud`, structured-output parse-success ≈ 100%, per-seed wall time + full-run projection reported BEFORE the full runs; STOP for operator go. ABANDON without recording if parse-success craters or the guard trips — iterate the `qwen3_32b` prompts (as v3 already did) or re-open 14.6; do NOT weaken the guard or raise the caps.
- [ ] Re-smoke confirms the floor on v3: every smoke seed reaches game_over with ZERO ballot truncation / unterminated-JSON parse failures under the FROZEN caps (the exact failure the first smoke hit — 2 vote-cap truncations at 1024, now targeted by v3's compact-ballot fix).
- [ ] Both sets re-recorded in ONE PR on the locked model + `qwen3_32b.v3` prompt set with all 4 13.5 substrate flags ON; both reports + MANIFESTs regenerated (the LANDED infra stamps model + prompt_versions + the `flags` column + new git_sha, and the flag config into the replay `game_over` metadata); prompt-regression fixtures + baseline regenerated; byte-identical reconstruction holds from the new recordings.
- [ ] Validity gate (HARD): friendly-fire 0; every game reaches game_over; betrayal ballots/accusations 0; leak suite green at 4p1i and 9p2i; meeting_rate ≥ 0.60 with ≥ 30 resolved meetings at 9p2i; byte-identical reconstruction (verified FLAG-AWARE — the same 4 flags set AND roster.json present, else the loader defaults to 4p1i and fails spuriously); zero tick-1 kills; zero missed-deadline markers; zero dangling primary_reason_id; cost rows 0; model + prompt_versions + flags rows correct.
- [ ] Funnel report ($0): `extract_gameplay_facts` over the new 9p2i set; the PR body reports win split, ejection count, accusation precision, accuser follow-through, persuasion rate, threshold-quoting-skip count.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

This is the Phase-9 9.5 shape transplanted to Featherless: `AILIBI_LLM_PROVIDER=featherless` +
`FEATHERLESS_API_KEY` + `AILIBI_PROMPT_SET=qwen3_32b` PLUS all 4 substrate flags
(`AILIBI_TESTIMONY_AS_CONTENT=1 AILIBI_WITNESSED_KILL_EVIDENCE=1 AILIBI_MOVEMENT_PERCEPTION=1
AILIBI_UNFREEZE_MEMORY=1`) on every `scripts/refresh_samples.sh` invocation; the locked model
`Qwen/Qwen3-32B` for both meeting and trigger call kinds (14.6), request-time thinking OFF, `fail_loud`.
`refresh_samples.sh` now ENFORCES exactly this tuple at preflight (PR #209): a real Featherless run aborts $0
before staging if `AILIBI_PROMPT_SET` ≠ `qwen3_32b` or any of the 4 flags ≠ `1`, so a mis-set env fails loud
instead of recording the wrong baseline.
ONE atomic PR — an intermediate commit is un-reconstructable. Time expectation (measured, 14.4/14.6): Qwen3-32B
non-thinking is ~27.1s/turn isolated — roughly 2× the local 9B's per-call latency, offset by the plan's 32B
concurrency cap of 2 (a 32B request = 2 of 4 units), so the full 50-seed × 2-format re-record lands in the
SAME ~13–30h ballpark as the 9B (the win is offloading the operator's machine, NOT wall-clock); do NOT assume
"far faster." The smoke (3–5 seeds) MUST project the real wall time before the full run. (MEASURED OUTCOME,
2026-07-01: the projection was over — the run took ~5h for both sets with 2 parallel seed workers each pulling
the next available seed; seed-level parallelism amortizes the per-turn latency. Plan future re-records at ~5h.) The report regeneration +
MANIFEST update + fixture refresh all happen through `scripts/build_sample_report.py` +
`scripts/_manifest_writer.py` (which already emits the `flags` column, PR #209) exactly as the 9.5 operator
workflow documents. Hosted non-determinism means FRESH generation won't byte-reproduce, but the recordings replay
byte-identically — verify that property explicitly with `scripts/verify_samples.sh` RUN WITH THE SAME 4 FLAGS
SET and a present `roster.json` (a flag-ON recording reconstructs byte-identically only when verify sets the
same flags AND finds roster.json; a temp dir without it defaults to 4p1i and fails spuriously — not a
determinism bug). Do NOT touch the 13.5 `*_enabled()` logic here (set via env + stamp only; default-ON is
14.9).

## Integration risk

The phase's spend/time gate. If structured-output parse-success is below the sim's tolerance, or the thinking
guard trips, STOP and fix upstream (14.1 adapter, 14.6 model choice) rather than papering the gate — in
particular do NOT raise the token caps (the 9.5 lesson: a raised ctx reintroduced overrun). The recorded
baseline must be auditable: no silent thinking, no silent cost, model/prompt rows exact. A VALIDITY failure
here (no candidate drives a valid sim) is the one real NO-GO that pauses the phase — surface it, do not force
a degraded baseline through. The FIRST smoke already exercised this gate as designed — it NO-GO'd at ~88.5%
parse (vote-cap truncations + opening-turn schema failures the narrow sweep never covered), which drove the
`qwen3_32b` → v3 hardening (PR #209). That is the gate working, not a phase failure; the re-smoke on v3 must
clear ≈ 100% parse + zero 1024-truncation before the full run, and a second NO-GO means iterate the prompts
again — never raise the caps.

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
Open a PR from branch `phase-14-featherless-rerecord` with a title like `task 14.7: smoke → re-record both sets on the locked model + new prompts + validity gate`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.4, §3.5 (replay provenance, canonical set); agent_prompts/task-9-5-model-migration-rerecord.md (the migration shape); tasks/phase-14.md (the locked tuple from 14.6); scripts/refresh_samples.sh), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
