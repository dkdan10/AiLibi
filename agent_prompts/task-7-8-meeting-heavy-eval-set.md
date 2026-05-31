# Agent Prompt — 7.8 Generate, balance-validate, and commit the Phase 7 meeting-heavy eval set

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-7.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 7.8 — Generate, balance-validate, and commit the Phase 7 meeting-heavy eval set, anchored to tasks/phase-7-plan.md W0.4, W0.5, "Wave 0 exit criteria", Q2/Q3; audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §3, §6; DESIGN.md §9, §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-7.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-7-meeting-heavy-eval-set`
**Depends on:** 7.1 merged, 7.2 merged, 7.3 merged, 7.4 merged, 7.5 merged, 7.6 merged, 7.7 merged
**Section refs:** tasks/phase-7-plan.md W0.4, W0.5, "Wave 0 exit criteria", Q2/Q3; audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §3, §6; DESIGN.md §9, §11.4
**Complexity:** Integration

This is the Wave 0 enablement-gate OPERATIONAL task — the one that converts the
config + metric substrate (7.1, 7.3), the loader/layout plumbing (7.4), and the
Ollama provider substrate (7.5/7.6/7.7) into a committed, meeting-rich eval
denominator. It is run by the DESIGN THREAD, not a headless dispatched agent,
because it must run LOCALLY against a live Ollama server (it needs `ollama serve`
plus the model pulled — see 7.5) and needs human balance judgment. It writes NO
code — it consumes 7.4's roster-aware loader + per-set refresh/manifest routing,
7.1's CLI roster/task flags, 7.3's `meeting_rate` metric, and 7.5's Ollama provider
(wired into the provider-agnostic refresh by 7.7).

The canonical agent-intelligence provider for Phase 7 is **local Ollama
(`qwen2.5:7b-instruct`), $0** — there is no API key and no real spend, so the
cost dimension is trivially zero. This task generates a 7p/2i + 2-task sample set
via `scripts/refresh_samples.sh` with `AILIBI_LLM_PROVIDER=ollama` into
`replays/samples/7p2i/` (with its `roster.json` descriptor + `MANIFEST.md`),
commits it **alongside** the existing 4p/1i baseline (which stays untouched + frozen
for determinism/leak regression and as the A/B reference — replays are
model-agnostic, so the Anthropic-recorded 4p/1i set still replays byte-identically),
and confirms the Wave 0 exit gate: 7.3's `meeting_rate >= 0.60` with **>= 30
resolved meetings**, AND a near-even decisive crew/impostor split (not
all-`CREWMATE_TASKS`, not all-parity). If the split is degenerate, sweep
tasks-per-crewmate (2 vs 3) and/or roster and re-record (Q3: balance validation is
required) — but the sweep is BOUNDED, not open-ended: because the run is free, the
bound is **time, not dollars** — **STOP after 3 full 50-game re-record attempts OR
24 hours cumulative wall-clock, whichever comes first**, rather than a spend cap. If
both bars are still unmet at the bound, do
NOT commit a sub-gate set as a compromise — STOP, leave the committed sets
unchanged, and return to the design thread for a re-plan (the gate may need a
different roster axis, an engine-balance change, or a revised target). A
committed-but-sub-gate set would silently poison every later agent-intelligence A/B.

Operational note: the model runs locally, so a full ~5k-call 50-game run is **slow
on the owner's Mac** (tens of minutes to hours), not the wall-clock of a hosted API.
Run the gate small first (a few seeds) to confirm meetings resolve and the model
emits schema-valid reports, then kick the full 50-game run **overnight**. Quality
spot-check that `qwen2.5:7b-instruct` actually resolves meetings (no schema crashes,
coherent accusations) on the small run before committing the full set.

The committed per-set `roster.json` (`num_players`/`num_impostors`/`tasks_per_crewmate`)
this task lands is also the intended metadata source for the deferred frontend
browse track (locked decision 1 / the plan's Frontend track), so that later track
reads this descriptor rather than persisting a new roster field. The frontend
browse selector itself is out of scope here; do not touch `frontend/`.

**Files in scope:**
- replays/samples/7p2i/ (the new committed set: replay JSONLs + `roster.json` + `MANIFEST.md` + its own `tournament-eval-report.json`)
- tests/api/test_replay_loader.py (add the CI gate: a pytest test that loads + reconstructs the COMMITTED `replays/samples/7p2i/` set — shared with 7.4, which this task depends on)

**Files NOT in scope:**
- api/replay_loader.py, scripts/refresh_samples.sh, scripts/_manifest_writer.py (the plumbing is Task 7.4; consume it, do not edit)
- scripts/run_tournament.py, orchestrator/seeder.py (the roster/task flags + seeder are 7.1's; consume them)
- eval/meeting_quality.py (the `meeting_rate` metric is 7.3's; read its output, do not edit)
- replays/samples/ flat 4p/1i set (committed ALONGSIDE; never deleted or overwritten)
- replays/samples/tournament-eval-report.json (the 4p/1i report is regenerated by Task 7.3; this task generates only the 7p/2i set's own report under `replays/samples/7p2i/`)
- frontend/ (browse selector is a later track)
- DESIGN.md (design-thread-owned)

**Definition of done:**
- [ ] A meeting-heavy 7p/2i + 2-task sample set is generated via `scripts/refresh_samples.sh` against the **local Ollama** provider (`AILIBI_LLM_PROVIDER=ollama`, `qwen2.5:7b-instruct`, using 7.4's roster-aware routing + 7.7's provider-agnostic refresh + 7.1's flags) into `replays/samples/7p2i/` with its `roster.json` + `MANIFEST.md`, and committed **alongside** the existing 4p/1i baseline; the 4p/1i set is not deleted or overwritten (it is the frozen, model-agnostic determinism/leak/A-B reference).
- [ ] **Wave 0 exit gate met on the committed canonical set:** 7.3's `meeting_rate` is `>= 0.60` with `>= 30` resolved meetings, AND the decisive crew/impostor split is near-even (not all-`CREWMATE_TASKS`, not all-parity). The chosen canonical config and the gate numbers are recorded in the PR `## Decisions` block.
- [ ] **Bounded sweep + stopping rule (time-boxed, not spend-capped):** because the Ollama run is **$0**, the balance sweep is bounded by **time, not dollars** — **STOP after 3 full 50-game re-record attempts OR 24 hours cumulative wall-clock, whichever comes first** (not a spend cap). If both bars are still unmet at the bound, NO set is committed as a sub-gate compromise — the committed sets are left unchanged and the gate is escalated to the design thread for a re-plan. The PR `## Decisions` records the attempts made and the wall-clock spent.
- [ ] **Local-model quality + meeting-resolution spot-check:** before the full commit, a small run (a few seeds) confirms `qwen2.5:7b-instruct` resolves meetings without schema crashes (7.6's parse-tolerance must hold on real local output). This is NOT only a schema-validity check — it must also be a **BEHAVIORAL read**: sample a few real Ollama meetings and confirm transcripts read as plausible social deduction and votes are sensible / justified, not just well-formed. The diagnosis's fake-provider expectation is ~63% meeting rate, so if the Ollama `meeting_rate` diverges from that by more than **10pp** (either direction), investigate the cause before committing (it signals a model-behavior or config discrepancy, not just noise). Cross-phase note: the resulting `alibi_survival` / `vote_correctness` are an **Ollama baseline**, NOT comparable to Phase 6's Sonnet numbers (only byte-identical replay reconstruction is model-agnostic).
- [ ] The determinism / byte-identical replay suite AND the leak suite — including the W0.2 `self_state.fellow_impostor_ids == ()` crew-recipient invariant from 7.2 — pass on **both** committed sets. The **CI-enforced** gate for the new 7p/2i set is a pytest test in `tests/api/test_replay_loader.py` that loads + reconstructs the COMMITTED `replays/samples/7p2i/` set (run under `check.sh`'s pytest, since `check.sh` runs `uv run pytest` but does NOT invoke `verify_samples.sh`), paired with the existing pytest coverage of the flat 4p/1i set — both committed sets thus CI-gated. `scripts/verify_samples.sh <set-dir>` is the MANUAL operator tool (`scripts/verify_samples.sh` for 4p/1i, `scripts/verify_samples.sh replays/samples/7p2i` for the new set), run before committing.
- [ ] The PR `## Decisions` block records: the canonical Phase 7 eval config (roster + tasks-per-crewmate) and whether a re-balance sweep was needed; the measured `meeting_rate` / resolved-meeting count / decisive split; the provider/model (`ollama` / `qwen2.5:7b-instruct`); and the wall-clock of the run (cost is $0 — the refresh's cost line / MANIFEST sum should read zero on Ollama, which is itself a useful sanity check that the budget $-dimension is disabled per 7.5).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Confirm the full substrate is merged and green FIRST: 7.4's plumbing (the loader
reconstructs a hermetic 2-impostor replay, refresh/manifest route per-set), 7.5's
Ollama client, 7.6's parse-tolerance, and 7.7's provider-agnostic refresh + budget.
Start `ollama serve` and `ollama pull qwen2.5:7b-instruct`. Then run a SMALL
gate first (a few seeds) with `AILIBI_LLM_PROVIDER=ollama` and 7.1's roster/task
flags targeting `replays/samples/7p2i/` (via the `AILIBI_SAMPLE_DIR`/`AILIBI_MANIFEST`
hooks 7.4 wired + 7.7's provider-aware preflight), confirm meetings resolve and
reports validate (no schema crashes), then kick the full 50-game run **overnight**
(it is slow locally). Read 7.3's `meeting_rate` off the resulting
`replays/samples/7p2i/tournament-eval-report.json`, and check the exit gate +
balance. A balance re-sweep (2↔3 tasks / roster) means multiple full local runs,
each free but slow, so honor the **time-box / ~3-attempt** bound and the
stop-and-escalate rule (there is no dollar cap — the Ollama run is $0). After
committing, add the pytest test that loads + reconstructs the committed
`replays/samples/7p2i/` set so its determinism is CI-gated, and run
`scripts/verify_samples.sh replays/samples/7p2i` manually. Do NOT edit the 7.4–7.7
substrate or any engine/agent code; this is a data-generation + gate-confirmation
task.

## Integration risk

This task runs the model locally (no spend), commits the first multi-impostor
fixture set, and decides whether the Phase 7 roster re-balances — all design-thread
judgment.

- **Local run is free but slow and time-bounded.** The full 7.4–7.7 substrate must
  be merged and fake-validated first, and `ollama serve` + the model must be
  reachable; the **time-box / ~3-attempt** bound + stop-and-escalate rule prevents
  an open-ended re-balance loop. There is NO dollar cap — the Ollama run is $0; the
  bound is wall-clock, and a ~5k-call run is slow locally (run the gate small, the
  full set overnight).
- **The 4p/1i baseline must survive untouched.** Commit the 7p/2i set ALONGSIDE; a
  mis-routed refresh that overwrote `replays/samples/` would destroy the
  determinism/leak regression + A/B reference. The 4p/1i set was recorded on
  Anthropic but replays are model-agnostic, so it reconstructs byte-identically
  regardless of the new provider — verify the flat set still reconstructs after the
  commit.
- **Firewall on the first committed multi-impostor data.** The 7.2
  `fellow_impostor_ids == ()` crew invariant must hold across the new set's
  packets, not just the single-impostor 4p/1i set; run the leak suite over both.
- **Gate honesty + local-model schema risk.** `meeting_rate` and the decisive split
  are measured on the local model, not assumed from the fake-provider 63%; the
  divergence check + bounded sweep keep an unbalanced or low-meeting set from being
  committed as a false "gate cleared". The added local risk is that
  `qwen2.5:7b-instruct` may emit reports that violate the strict
  discriminated-union schemas — 7.6's parse-tolerance is the mitigation, and the
  small spot-check run is where a residual schema-crash surfaces before the full
  commit.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import llm.ollama_client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import observation.packet.SelfView"`
- `uv run python -c "import orchestrator.game"`
- `uv run python -c "import eval.meeting_quality"`

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
Open a PR from branch `phase-7-meeting-heavy-eval-set` with a title like `task 7.8: generate, balance-validate, and commit the phase 7 meeting-heavy eval set`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-7-plan.md W0.4, W0.5, "Wave 0 exit criteria", Q2/Q3; audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §3, §6; DESIGN.md §9, §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
