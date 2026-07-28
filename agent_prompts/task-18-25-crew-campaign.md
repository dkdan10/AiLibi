# Agent Prompt — 18.25 THE CREW CAMPAIGN (operator, multi-session, ~30–40h real-path legs)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.25 — THE CREW CAMPAIGN (operator, multi-session, ~30–40h real-path legs), anchored to the 18.24 report (the frozen impostor champions this campaign trains against); training/crew/ (the crew bases); audits/audit-phase-18-planning.md §4 (#8, the impostor-first rationale) + the crew-fitness finding (correct_reports dead on non-convicting paths — the conviction term is the counterweight). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-crew-campaign`
**Depends on:** 18.24, 18.31, 18.32
**Section refs:** the 18.24 report (the frozen impostor champions this campaign trains against); training/crew/ (the crew bases); audits/audit-phase-18-planning.md §4 (#8, the impostor-first rationale) + the crew-fitness finding (correct_reports dead on non-convicting paths — the conviction term is the counterweight)
**Complexity:** Integration

The counter-adaptation half: evolve the crew side (both bases: general + owned-task)
against the frozen impostor campaign champions + hall of fame, with the conviction-supply
term giving crew fitness the conviction-economy gradient the fake path denies it, the
interrupt-preserving constraint kept (the 15.22 guard — starvation stays unreachable), and
real-path re-ranks per generation. Reachability honesty (the merged driver, 316d4e5): the
frozen-champion half of that shape is direct, the hall half is NOT — there is no seam for
adopting 18.24's committed hall as this campaign's opponent pool; the impostor side enters
via `impostor.initial_genome` seeded from a committed 18.24 CANDIDATE (re-frozen as a
fresh lineage in this campaign's own hall), so the counter-adaptation reading is against
that lineage plus this campaign's own accumulating hall, and if the report judges
full-pool continuity load-bearing that is a routed amendment, never a silent driver edit.
Name the seed artifact by exact path: the strongest 18.24 arms live under
`training/artifacts/coevo/intermediates/` and `…/runnerups/` (e.g. `ea4bc955…` at
intermediates/run-02-utility-lambda4/gen-2, `bfd145cb…` — never a champion — at
runnerups/run-02-utility-lambda4/gen-9), NOT only under `<run>/impostor/`; all load
through the four-file artifact (verified post-merge). Founder honesty (the campaign's F2,
sharpened by the slate): the committed MAP-Elites founder pool is v2 free-policy
(1049-gene) — a utility-family (19-gene) impostor side CANNOT ingest it (the driver's
genome-length reload check), so `founder_cells_dir` stays unset for a utility-family
side and its opponent pool starts EMPTY, accumulating swap-frozen members + exploiter
finds only; if pool diversity proves load-bearing mid-campaign, the routed conditional
is a utility-family founder-persistence run (18.6-shaped), recorded in 18.28's deferred
ledger — never an improvised ingest. Crew mechanics the driver pins:
`first_side="crew"`; the crew side config structurally REJECTS `anchor_policy` (crew
anchor-CE is FSM-fixed by construction); the crew builder must emit a `crew-`-prefixed
`encoder_version` (the 18.19 conflation guard, enforced both directions). Scenario
adoption (18.23, merged d63ffab) is available to this campaign but honestly thin on the
crew side: the library holds exactly ONE crew scenario (`body-discovery-latency`, max
1.0) — meaningful crew scenario pressure beyond discovery latency means AUTHORING new
crew specs, which is new work, not configuration. If adopted: pass
`ScenarioProvider(agent_factory_builders=..., fitness_seeds=..., meeting_runner_factory=...,
rng_hash_policy=...)` as the driver's `scenario_provider`, and use the AGENT-FACTORY seam
(genome → `build_coevo_factory`) — the selector seam drives EVERY seat including the
opponents under an unenforced delegation convention and is never a campaign
configuration. Terms add AFTER the slate mean, so row fitness scalars stop being
comparable to pre-scenario rows; the provider's `games_per_evaluation` budget is advisory
only (nothing meters it — quote it in the report); and under the default forced-fake
meeting layer the kill-witness survival clause is vacuous while force-parity gains an
unnamed crew-ejection channel only an ejection-capable runner (the composed runner, under
its GO gate) makes live — name whichever applies in the report. Report mirrors 18.24 (rows, cycling detector, floor
sensitivity, emergence sweeps — crew-side instruments emphasized: roll-call coverage,
conversion, counter-adaptation evidence against the specific impostor champions). Crew
champion adoption is NOT this task's call: candidates route to 18.26/18.27 evidence.
Duration honesty: the crew slate is smaller than 18.24's but the per-generation real-path
re-rank arithmetic is the same — plan **~30–40 h** of unattended real-path legs across
sessions, checkpoint-push per generation.

**Files in scope:**
- training/reports/report-crew-campaign.md (new) + training/reports/results-crew-campaign.jsonl (new)
- training/artifacts/coevo/ (crew-side frozen artifacts, via the driver; disjoint gen dirs from 18.24's — the store layout separates sides)
- tests/training/test_coevo_driver.py; (crew-campaign row pins ONLY — additive to 18.24's region)

**Files NOT in scope:**
- training/coevo/*.py + training/crew/*.py (runs, not redesigns)
- agents/tactical/learned/; (adoption is 18.27's evidence question)

**Definition of done:**
- [ ] The campaign report carries the full row/benchmark/meter discipline, the counter-adaptation reading (does trained crew close the frozen champion's win edge, and through which instrument channels), and the real-path re-rank tables with stamp proofs.
- [ ] Every candidate emergence behavior this campaign surfaces carries its 18.4-named ablation run and provenance in the report (the 18.24 discipline, crew side).
- [ ] The gate-validity discipline holds throughout (no starvation-family candidate survives selection; validity-gate columns quoted per entrant), and crew finalists (if any clear the bars) are named for 18.26.
- [ ] The 18.24 protocol preconditions hold: the §4.0-style stability table is computed after the FIRST retested candidate (and the campaign does not proceed at a seed budget whose measured noise exceeds 25% of any threshold it tests — F12); every frozen artifact this campaign names for 18.26 loads through the consuming entry point (`--crew-artifact` / `--candidate-artifact`) before hand-off (F14); every session's chain/leg log is committed under the provenance root (the blocker-4 ordering evidence — the 18.24 session-5 gap is the cautionary case).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The interesting cell is pace-to-wins conversion on the REAL path (the 17.13 open question:
does the citation-era conviction channel move an owned-task crew's pace advantage?) —
answer it with the campaign's real re-rank data and say so explicitly either way. The
18.31 operator surface (merged e2a040b, verified): stamp-grade config is now
config-preflight-enforced — `CoevoSideConfig.encoder_version` names the actual family,
`hidden` is REQUIRED for `v2`/`v3` masked-MLP families and FORBIDDEN for utility/scorer
families, `anchor_policy_label` must name the anchor artifact whenever `anchor_policy`
is set, and `CoevoCampaignConfig.run_label` must be set to the campaign run name (the
default stamps `coevo-campaign` into every freeze's provenance). Resume is OPT-IN:
re-invoke `run_realpath_rerank(..., resume=True)` with the same work_dir/tranche/mode/
config/prompt-set/backend (drift refuses; non-canonical maps refuse resume outright;
tick-budget-capped elements re-record on every resume by design, ~8 min each — budget
for it). The library now writes `leg-log.jsonl` and
`prescreen-quotes-<tranche>-<invocation>.json` natively per invocation — commit them
beside the rankings (they ARE the blocker-4 ordering evidence); new rankings carry
schema `realpath-rerank-v2`. Champion persistence is DEFAULT-ON — checkpoint-push now
includes `gen-champions/` (four files per generation); keep campaign trees on one real
filesystem (symlink/hard-link entries refuse). Report tables come from
`scripts/generate_campaign_tables.py` (`rows`/`legs`/`stability` subcommands), never
hand-assembled, and the F12 stability read runs via `stability` after the first
retested candidate. The
18.24 evidence is on this campaign's side here: the run-01 same-seed `conviction=None`
twin reproduced the impostor champion lineage sha-for-sha while CREW selection diverged —
the term's selection-relevant effect is crew-side, exactly where this campaign wants it
(quote the committed twin artifacts, not the report prose — report §12 Errata lists the
prose defects). Runbook (owner directive 2026-07-28, superseding 18.24's F7 one-leg
correction): run TWO legs concurrently — always on different tranches or different
work_dirs (the 18.31 tranche claim refuses same-tranche concurrency by design), staggered
starts with jittered backoff, keeping F7's `meeting_timeout_seconds=900` and 3-seed
tranches; each leg stays internally sequential (the library records one game at a time —
concurrency exists ONLY at the leg level). F7's one-leg numbers were measured under a
partially-impaired provider window; the two-leg default is the healthy-provider posture,
so if impairment symptoms reappear (rising timeout or retry-exhaustion rates in the
native leg logs), degrade to one leg and record the switch in the report — duration
honesty prices whichever posture actually ran. Sweep legs follow the recording-dir convention (`roster.json`
present, audit sidecars out — the campaign's F5). Founder-game pricing (F3) is moot while
founders cannot load (see the founder-honesty block above); run-05's 2×2 reduced shape is
the sizing precedent if any free-policy side runs. Stamp
obligation (routed by the 18.19 verification): the committed measurement-tier
`training/artifacts/crew/` dirs carry NO `stamp.json`, so the `--crew-artifact` arm fails
loud on them BY DESIGN — every crew artifact this campaign freezes carries the five-field
stamp, and the first dual-stamped crew recordings are this campaign's re-rank legs.

## Integration risk

Crew real-path evals are the phase's first learned-crew recordings — the 18.7/18.19 stamp
guards get their first live exercise; any conflation or leak finding stops the campaign leg
until routed.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.coevo.hall_of_fame"`
- `uv run python -c "import training.conviction.serving"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.conviction.model"`
- `uv run python -c "import training.conviction.dataset"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.tactical.learned.crew_forward"`
- `uv run python -c "import agents.tactical.learned.factory"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import eval.off_menu"`
- `uv run python -c "import eval.kill_craft"`
- `uv run python -c "import eval.deception_instruments"`
- `uv run python -c "import agents.tactical.features"`
- `uv run python -c "import training.coevo.factory"`
- `uv run python -c "import training.coevo.rollout"`
- `uv run python -c "import training.coevo.driver"`
- `uv run python -c "import training.bakeoff.map_elites"`
- `uv run python -c "import training.realpath"`
- `uv run python -c "import training.anchor_study"`

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
Open a PR from branch `phase-18-crew-campaign` with a title like `task 18.25: the crew campaign (operator, multi-session, ~30–40h real-path legs)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing the 18.24 report (the frozen impostor champions this campaign trains against); training/crew/ (the crew bases); audits/audit-phase-18-planning.md §4 (#8, the impostor-first rationale) + the crew-fitness finding (correct_reports dead on non-convicting paths — the conviction term is the counterweight)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
