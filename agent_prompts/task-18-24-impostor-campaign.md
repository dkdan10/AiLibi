# Agent Prompt — 18.24 THE IMPOSTOR CAMPAIGN (operator, multi-session)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.24 — THE IMPOSTOR CAMPAIGN (operator, multi-session), anchored to audits/audit-phase-18-planning.md §7 (the campaign shape); the 18.21 driver + 18.20 hall of fame + 18.16 fitness stack + 18.17 real-path re-rank + 18.5 anchor-study candidates; audits/audit-phase-17-close.md §1.3 (the flip bar the campaign aims at). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-impostor-campaign`
**Depends on:** 18.4, 18.5, 18.17, 18.18, 18.21, 18.22, 18.30
**Section refs:** audits/audit-phase-18-planning.md §7 (the campaign shape); the 18.21 driver + 18.20 hall of fame + 18.16 fitness stack + 18.17 real-path re-rank + 18.5 anchor-study candidates; audits/audit-phase-17-close.md §1.3 (the flip bar the campaign aims at)
**Complexity:** Integration

The phase's first live campaign: evolve the impostor side against the frozen scripted crew
plus hall-of-fame opponents (as the crew side gains members, later swaps use them),
entrants seeded from the committed champion, the 18.5 anchor-study candidates, and (for the
free-policy family) 18.22's v3 features — inner fitness on the fake/surrogate path with the
conviction term, per-generation real-path top-K re-ranks (18.17, ~2 h/gen), pre-screen
before every real spend, all meters quoted. The dep edges are load-bearing: no campaign
records before the emergence bars are ratified (18.4) or before the conviction signal it
selects on has been re-probed (18.18). THE PROBE'S FOUR NAMED BLOCKERS BIND THIS CAMPAIGN
(report-goodhart-probe.md "Blockers", folded verbatim): (1) `d4-contest-farming[4p1i]` —
no 4p1i-scored selection until the routed D4 contest floor lands; (2)+(3)
`conviction-supply-laundering[emergency|kill,4p1i]` — no conviction-weighted fitness on
the 4p1i roster, and on ANY roster the term's credit for meeting-count-multiplying play is
conditioned/capped on recorded-bytes confirmation; (4)
`prescreen-substrate-divergence[9p2i]` — a pre-screen PASS is real-path spend advice ONLY;
every gating use pairs with a recorded-bytes floor read on flag-mintless substrates. One
asymmetry this campaign owns (the 18.30 hand-off): the harness/crew eval passes serve the
term live, but the impostor TRAINING loops are deliberately still anchor-composed — 
threading the term into impostor training is THIS campaign's protocol decision, made under
blocker (2)'s guard and recorded in the report. The merged driver (316d4e5) makes the
mechanism concrete: passing `conviction=` to `run_alternating_freeze` serves the term LIVE
into BOTH sides' training fitness (a Codex-round fix — there is no metering-only mode),
while under a composed configuration the term object is inert in training fitness
(contributes exactly zero; conviction pressure flows through real ejection outcomes
instead) — so the protocol decision is exactly: non-composed + `conviction=` under
blocker (2)'s guard, composed, or neither. Scenario legs (18.23) and the composed
meeting-outcome runner (18.29) are deliberately NOT prerequisites: the campaign starts
without them, and if either merges mid-campaign a later swap MAY adopt it (the composed
runner ONLY under its committed GO verdict, through 18.21's runner-factory seam, with both
component use-counters quoted in the campaign meters), recorded per-generation in the
rows — the close (18.28) still waits on both either way. The composed verdict LANDED GO
(6339116: decision accuracy 0.8646 > 0.625, convicting top-1 0.7667 ≥ 0.6375) with three
adoption constraints machine-readable in `training/artifacts/composed/verdict.json`
(`adoption_constraints`) — carried verbatim into the campaign meters on adoption:
composed-provenance-validity (composed-substrate probe reads are diagnostic-grade — every
LLM-free meeting path fails `cost_and_provenance_exact` until the validity gate answers
the stamped-substrate question, an eval/-side open item routed to the close),
prescreen-substrate-divergence-shape (pre-screen PASS = spend advice only; pair every
gating use with a recorded-bytes floor read — blocker (4)'s shape), and
emergency-predicted-supply-above-bar (forced-emergency predicted-supply delta +29.5%
exceeds the 25% materiality bar with recorded 0.0 — the laundering shape; blockers
(2)+(3)'s recorded-bytes conditioning applies unchanged). Driver-consumption facts the
campaign plans around (316d4e5, verified): `CoevoCampaignConfig` requires `work_dir`,
`substrate_sha256` + `substrate_sha_kind` (named per the two-definition rule below and
quoted in every row), both side configs, `master_seed`, `num_swaps`,
`generations_per_swap`, `fitness_seeds`, `benchmark_seeds`, and non-empty unique
`payoff_seeds`; defaults slate_size 3, staleness_cap 8, exploiter 5×6 (the probe cannot be
disabled and dominates the projected game bound at defaults), game_ceiling 25 000 with
`allow_over_ceiling` defaulting False. The driver REFUSES to resume: an existing hall
root or rows file is a no-clobber error, so the multi-session shape is SEQUENTIAL FRESH
RUNS — each session a fresh work_dir + hall_root seeded via `initial_genome=` from the
prior session's frozen champion, the opponent pool restarting from substrate-fenced
MAP-Elites founders (there is NO path to load a prior run's hall as the pool); if
mid-campaign evidence shows cross-session pool continuity is load-bearing, that is a
routed amendment under the integration-risk discipline, never a silent machinery patch.
Composed-adoption hygiene: the merged suite never runs a composed campaign end-to-end
(rows with `meeting_runner="composed"` are unexercised), so the first composed swap is
preceded by a miniature composed smoke campaign whose rows are read before any real
spend; under a composed configuration `opponent_payoffs` are composed-runner-scored
hardness meters, never absolute champion numbers (benchmark/exploiter columns stay
fake-path by construction); and the first retire-and-replace event
(`retired_opponent_shas` non-empty) gets a sanity read in the rows — the suite pins
exhaustion, not continuation. Seed hygiene: every study-artifact entrant (the 18.5
candidates, the 18.6 cells) carries a substrate sha; a seed whose sha mismatches the
campaign substrate is re-fit/re-run at the current substrate before entry (cheap and
deterministic), never consumed stale. Two sha DEFINITIONS exist (merged, verified):
`training.anchor_study.compute_substrate_sha` (composite: baseline + MANIFEST digest +
splits digest + set + floor) and `training.bakeoff.map_elites.bakeoff_substrate_sha`
(raw MANIFEST digest) — the refusal logic dispatches per artifact family, never assumes
one key. The 18.5 report names the seed candidates: `lambda-4.0` (Pareto-dominant —
anchor-CE 0.61 at fitness 19.22; legibility is free at the fake-path budget) and
`filtered-bc-anchor` (via 18.16's anchor-policy seam). Instrument sweeps over campaign
recordings require BYTE-COMPLETE recordings: 18.3's walk accepts partial recordings by
design (an EOF-truncated file silently shrinks the decision denominator — the 18.2
byte-completeness fence is the model); the sweep leg verifies completeness first. Report: campaign rows, the cycling-detector
reading, per-entrant floor-sensitivity on the real re-ranks, the emergence-instrument
sweeps (18.1/18.2/18.3) over the campaign's real-path recordings against the 18.4 memo's
cells, and the named finalists for 18.26. Operator shape: fake-path legs are hours;
real-path legs total ~40–50 h spread across sessions — checkpoint-push per generation.

**Files in scope:**
- training/reports/report-impostor-campaign.md (new) + training/reports/results-impostor-campaign.jsonl (new)
- training/artifacts/coevo/ (the campaign's frozen artifacts, via the driver)
- tests/training/test_coevo_driver.py; (campaign-row pins from the committed rows ONLY)

**Files NOT in scope:**
- training/coevo/*.py + training/bakeoff/ (the machinery froze at Wave 3 — a campaign is a run, not a redesign)
- agents/tactical/learned/; (no champion swap here — 18.27's evidence decides)

**Definition of done:**
- [ ] The campaign report carries every generation's row (fitness, anchor benchmarks both directions, opponent slates, exploiter outcomes, meter consumption), the cycling-detector verdict stated against the pre-registered signature, and the real-path re-rank tables with stamp proofs and floor sensitivity per the 17.14 discipline.
- [ ] The emergence instruments are swept over the campaign's real-path recordings with deltas quoted against the 18.4 baseline cells (claims deferred to 18.27 — this task reports, never rules), and the finalists for 18.26 are named with their artifacts frozen.
- [ ] For every candidate emergence behavior the report surfaces (a delta the 18.27 reading could rule on), the 18.4-named counterfactual ablation is RUN (disable the enabling lever/term/feature; fake-path re-runs suffice where the behavior is tactical) and its provenance recorded in the report — the 18.27 four-part discipline consumes ablation evidence from here, and an unablated candidate reads NOT-DEMONSTRATED by construction.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Run the standing runbook per real-path leg (2 staggered workers, jittered backoff,
`AILIBI_SEED_MAX_ATTEMPTS=8`, per-seed atomic staging, checkpoint-push). If a meter (cap)
exhausts mid-campaign, the swap-boundary stop is the design working — re-ground and
resume, and say so in the report; per the driver's no-clobber discipline "resume" means a
FRESH run in a new work_dir seeded from the frozen champion (the driver-consumption block
above), and checkpoint-push covers the streamed `campaign-rows.jsonl` + frozen hall dirs.

## Integration risk

The first run composes every new subsystem (conviction term, pre-screen, HoF sampling,
driver, real re-ranks) — expect integration findings. The discipline: a defect found
mid-campaign becomes a routed contract or an in-report finding; the campaign never patches
machinery silently (merge-equals-done applies to the tools it runs on).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
- `uv run python -c "import training.coevo.hall_of_fame"`
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
Open a PR from branch `phase-18-impostor-campaign` with a title like `task 18.24: the impostor campaign (operator, multi-session)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §7 (the campaign shape); the 18.21 driver + 18.20 hall of fame + 18.16 fitness stack + 18.17 real-path re-rank + 18.5 anchor-study candidates; audits/audit-phase-17-close.md §1.3 (the flip bar the campaign aims at)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
