# Phase 19 — Review-and-refresh: truth, the spectator, and the ML close

STATUS: OPEN (chartered 2026-08-03; the owner's merge of this document ratifies the plan —
the 15.18 convention). Phase 19 is REVIEW-AND-REFRESH by owner charter
(`tasks/post-phase-14-plan.md`): a deep review of the code that exists plus an updated
presentation of the frontend and the data displays — NOT a feature phase. The planning
spine is `audits/audit-phase-19-triage.md` (§7 work-list, §8 claim-verification table);
the phase shape, the owner's decision-menu answers, and every divergence from the triage
are recorded in `audits/audit-phase-19-planning.md`. The gate baseline at chartering:
4531 passed / 20 skipped / 3 xfailed at `67166b3`, code byte-identical to the audited
`8873e99`. The ladder tip stands at baseline 6 and does not move this phase.

## Locked decisions (owner-ratified 2026-08-03)

1. **The charter and the NOT-list are binding.** No new mechanic, map, or physical
   channel; no behavior change to gameplay or evidence validation beyond
   instrumentation/labels; no training campaign, referee/floor change, or bar re-pricing;
   no human seat; no heterogeneous-model lobbies; no watchability-scalar tuning as a
   human-interest proxy; no recorder ports; no rewrite-for-its-own-sake; no further
   audit formalism beyond the 19.16 glossary; polish never ahead of narrative
   correctness. GAME prompt templates (`agents/strategic/prompts/`) are substrate
   behavior (the prompt byte-golden pins them): **no edits to any game prompt template
   anywhere in this phase** — the prompt-side evidence-flag naming routes to the post-19
   decision (decision 6 below). All five bespoke bake-off sets are LIVE (registered in
   `orchestrator/game.py:343-350`, parametrically validated by
   `tests/agents/test_bespoke_prompt_sets.py`) — the source audits' deletion candidacy
   is refuted and no prompt-set directory is deleted. The agent-dispatch template
   (`scripts/prompt_template.md.j2`) is not a game template; 19.1 updates its authority
   line with the DESIGN.md demotion.
2. **ML component tier map: the evidence-first hybrid.** KEEP what committed evidence and
   always-on gates still execute (compact learned inference + parity, the corpus
   verifier/splits, the conviction model, the surrogate RANKING channel, the ES core +
   champion acceptance). FREEZE with labels: the composed runner (optional-diagnostic),
   the crew stack, co-evolution/campaign machinery (campaign-only test families behind
   opt-in markers). RETIRE after consumer verification: `training/realpath.py`, the
   STANDALONE surrogate meeting-runner arm (the class itself stays as the composed
   runner's dependency — 19.19 records the boundary), the unused `first_meeting`
   boundary, and new-search machinery. Retired code stays in git history.
3. **ML re-open fork: record the fork, decide later.** The reopening checklist (19.18)
   documents BOTH routes — referee-floor re-pricing vs real-path conviction signal — plus
   the four mandatory pre-campaign checks (interval-aware floors, the weak-flag Goodhart
   probe, same-substrate run-variance treatment, screening replication), and states the
   owner picks a route only against a concrete re-open proposal. The program stays frozen.
4. **License and posture: MIT + minimal CONTRIBUTING/SECURITY** (19.7).
5. **Artifact retention: prune coevo only.** `replays/samples/` and `replays/ml_corpus`
   stay in-tree; the closed-campaign co-evolution intermediates move to an evidence
   branch with manifests, hashes, and every test-pinned byte staying in-tree; partial
   clone documented as the fast path (19.22). No history rewrite this phase.
6. **The evidence-honesty substrate fixes are decided AFTER the metrics.** Phase 19 ships
   the proof-vs-inference metrics (19.14), the injustice fixtures (19.11), and the
   per-mechanism labels; the close (19.28) routes the post-19 decision — the substrate
   gameplay phase vs the presentation phase — to the owner, argued from those metrics.
7. **The cut line: the balanced phase.** 28 contracts across three waves; the backlog
   (monolith decompositions, API/training walker migration, typed ballot telemetry, and
   the rest of `audit-phase-19-planning.md` §5) is out and recorded, not silent.
8. **DESIGN.md is contractable this phase.** Dispatched agents are barred from DESIGN.md
   by a prompt-generator constraint; THIS PLANNING PR scope-gates that rule (a task
   explicitly listing DESIGN.md in scope is exempt), so 19.1's generated prompt already
   carries the exception — resolving the bootstrap contradiction the first Codex review
   round flagged. Recorded, not silent: five HISTORICAL prompts (tasks 1.9, 2.10,
   2.10.5, 2.13, 2.14 — the era when DESIGN.md was the living spec and their contracts
   listed it in scope) also drop the constraint line under the same rule; every prompt
   whose task does not list DESIGN.md is byte-identical. The merge of this document
   ratifies the control-surface change.

## Designer rulings (recorded here so contracts inherit them)

- **Evidence labels are binding.** Every contract's Section refs carry the triage
  provenance tag — [C] both audits, [S-Claude]/[S-Codex] single-source, [L] internal
  ledger. Where the triage did not independently re-run a claim and the planning session
  could not verify it either, the contract's FIRST DoD step is verify-then-fix, never
  assume-then-fix. Anchors below were re-verified at HEAD by the planning session.
- **No recordings, anywhere.** Every task is $0 — no LLM calls, no recordings. Derived
  views (eval reports, the rubric score, generated goldens) regenerate from committed
  bytes only; replay bytes never move; `bash scripts/verify_samples.sh` must stay green
  through every merge. Ordinary tooling network (package registries for lockfile
  regeneration, action-SHA lookup, git push) is permitted — "offline" binds the
  evidence, not the toolchain.
- **Docs of record get additive, dated errata — never in-place rewrites.** README/design
  prose is living documentation and is rewritten; campaign reports and audits are records
  and get errata sections.
- **Generated facts beat copied facts.** Any number a contract writes into prose is
  recomputed from committed artifacts first, with the command recorded in the PR.
- **A regenerated derived view is not a baseline.** Nothing in this phase records a
  baseline; the ladder tip stays baseline 6.

## The DAG

```
Wave 1 (roots, dispatch in parallel):
  19.2 (in-code truth)        19.3 (ES portability)      19.4 (reward claim)
  19.5 (metric/display truth) 19.6 (one-line defects)
  19.8 (corpus disclosures)   19.9 (curated default)
  19.3 -> 19.1 (front-door truth — the README portability claim quotes 19.3's outcome)
  19.6 -> 19.7 (public hygiene + MIT)

Wave 2 (the spectator + the deduction instrument):
  (19.5, 19.9) -> 19.10 (playback coherence) -> 19.11 (evidence taxonomy)
  (the 19.5 edge is api/schemas.py + generated-types serialization — the report cells
   19.5 adds flow through the same DTO surface the 19.10 chain edits)
  (19.7, 19.10) -> 19.12 (frontend test baseline)
  19.1 -> 19.16 (reading guide)
  (19.1, 19.9, 19.10, 19.14, 19.16) -> 19.13 (README proof + static demo; the 19.14
   edge is TournamentDashboard serialization for the fetch-seam routing)
  (19.5, 19.11, 19.18) -> 19.14 (deduction metrics; the 19.18 edge is
   eval/meeting_quality.py serialization — the report wrapper lives there)
  19.2 -> 19.15 (guard-rationale redaction)
  (19.10, 19.12) -> 19.17 (ticker + cost chips — the gated tail)

Wave 3 (ML close + consolidation):
  19.5 -> 19.18 (tier map + freeze labels + reopening checklist)
  (19.1, 19.4, 19.18) -> 19.19 (retirements; 19.1/19.4 are llm-README and
   test_rewards serialization edges)
  19.4 -> 19.20 (report honesty)
  (19.13, 19.19) -> 19.22 (artifact classes + coevo prune)
  (19.20, 19.22) -> 19.21 (raw slate — OWNER)
  (19.19, 19.20, 19.21, 19.22) -> 19.23 (verify-ml-evidence — after the raw-slate ruling)
  (19.2, 19.11, 19.13, 19.14, 19.19) -> 19.24 (boundary hardening)
  19.24 -> 19.25 (the replay walker)
  19.15 -> 19.26 (vote-tally parity)
  (19.3, 19.4, 19.7, 19.12, 19.18, 19.19, 19.22, 19.25) -> 19.27 (test-suite structure)
  (19.3/19.4 edges are tests/training/ serialization, not semantic prerequisites)
  (19.8, 19.17, 19.23, 19.26, 19.27) -> 19.28 THE PHASE CLOSE [OWNER]
  (19.28's list is the true leaf set; every other task reaches the close transitively)
```

Critical path: 19.5 → 19.10 → 19.11 → 19.14 → 19.13 → 19.24 → 19.25 → 19.27 → 19.28
(nine tasks), with two eight-task feeders joining it — the README/demo branch
(19.3 → 19.1 → 19.16 → 19.13) and the ML chain (19.5 → 19.18 → 19.19 → 19.24). Dispatch
19.5 first (it heads the critical path and the ML chain), with 19.3 and 19.9 beside it
(19.3 heads the README branch; 19.9 feeds 19.10). The day-one frontier is seven roots
(19.2–19.6, 19.8, 19.9); nothing waits on the owner until 19.21 and the close.

**Baseline numbering.** None. This phase records no baselines and no recordings of any
kind; the ladder tip stands at baseline 6 (the 18.12 adopting record). Regenerated derived
views (19.5/19.9/19.14) are recomputations from committed bytes, not records.

**Collision discipline.** `README.md` 19.1 → 19.16 → 19.13 → 19.22 (dep-ordered);
`api/replay_loader.py` 19.9 → 19.10 → 19.11; `api/schemas.py` 19.5 → 19.10 → 19.11 →
19.14; `frontend/src/types/api.ts` 19.5 → 19.10 → 19.11 → 19.14 → 19.24 (the report
cells and DTO-version constant ride the same generated surface);
`frontend/src/App.tsx` 19.10 → 19.17;
`frontend/src/api/client.ts` 19.9 → 19.13 → 19.24; `frontend/e2e/` 19.12 → 19.17;
`frontend/src/components/ReplayPicker.tsx` 19.9 → 19.12 (transitive via 19.10);
`frontend/src/components/TournamentDashboard.tsx` 19.5 → 19.14 → 19.13 (truth tiles,
the metrics panel, then the fetch-seam routing);
`scripts/prompt_template.md.j2` + `agent_prompts/` 19.1 only (the authority-line
regeneration); `training/coevo/` 19.18 (labels) → 19.19 (the hall_of_fame reference
rewrite); `meetings/manager.py`
19.2 → 19.15 → 19.26; `orchestrator/game.py` 19.2 → 19.24; `eval/meeting_quality.py`
19.5 → 19.18 → 19.14 (labels, then the report-wrapper extension);
`eval/vote_correctness.py` 19.5 → 19.18; `llm/README.md` 19.1 → 19.19 (the cache
advertisement leaves with the module); `eval/leak_test.py` 19.24 → 19.25;
`eval/watchability.py` 19.18 → 19.25 (transitive); `pyproject.toml` + `uv.lock`
19.6 → 19.7 → 19.27; `scripts/check.sh` + `.github/workflows/ci.yml` 19.7 → 19.12;
`training/bakeoff/harness.py` 19.19 → 19.24;
`training/README.md` 19.18 → 19.23 (transitive); `training/reports/report-finalist-eval.md`
19.20 → 19.21; `docs/artifacts.md` 19.22 → 19.21; the four
`tournament-eval-report.json` derived views 19.5 → 19.14; `scripts/build_sample_report.py`
19.5 → 19.14; `tests/eval/test_report_schema.py` + `test_tournament_report.py`
19.5 → 19.14; `tests/api/` 19.9 → 19.10 → 19.11 → 19.24;
`training/surrogate/runner.py` 19.18 (label) → 19.19 (code);
`training/surrogate/fidelity.py` 19.18 → 19.19 (dir ripple);
`docs/reading-guide.md` 19.16 → 19.22 (transitive); `tests/training/`
19.3/19.4 → 19.19 → 19.27 (exact files, then the marker sweep — test_rewards.py is
19.4 → 19.19); `tasks/phase-19.md` 19.28 only.

**Model assignments** (the standing rule: Opus for loud-failure work — mechanical fixes,
re-pins, deletions with consumer greps, test scaffolding, generated docs; Fable for
silent-failure work — metric semantics, evidence taxonomy, docstring truth, tier-map
wording, statistical honesty, the spectator narrative):
Fable — 19.1, 19.2, 19.4, 19.5, 19.8, 19.10, 19.11, 19.14, 19.16, 19.18, 19.20, 19.25,
19.26, 19.28. Opus — 19.3, 19.6, 19.7, 19.9, 19.12, 19.13, 19.15, 19.17, 19.19, 19.21,
19.22, 19.23, 19.24, 19.27.

**Operator/owner gates.** No recording sessions exist in this phase. Owner touchpoints:
**19.21** (the raw-slate check runs on the owner's machine — minutes, not hours) and
**19.28** (the close ratification + the post-19 decision menu). Everything else is
dispatchable agent work at $0.

---

## Wave 1 — truth and the gate

### Task 19.1 — The front-door truth sweep + generated-fact checks
**Branch:** `phase-19-front-door-truth`
**Depends on:** 19.3 (the README's cross-platform reproducibility claim states 19.3's measured outcome — portable sampler vs narrowed guarantee — so the front door cannot publish before that outcome exists)
**Section refs:** audits/audit-phase-19-triage.md §7 item 1 [C; §8 rows 6, 16]; README.md:13 (219 PRs / ~2,500 tests), :48 vs :100 (the ladder-tip self-contradiction), :69 (the 0.938 mislabel), :104 ("intentionally minimal"), :158-175 (no Node/npm); AGENTS.md:16-19 (DESIGN.md declared authoritative), :64-79 (three-providers + stale baseline text); llm/README.md:32 (two providers) vs llm/provider.py:41-44 (four); .env.example:63-186 (six retired levers as LIVE default-OFF; zero `AILIBI_IMPOSTOR_ROLL_CALL`) vs orchestrator/replay.py:531-545 (`_RETIRED_ALWAYS_ON_LEVERS`), :570-572 (`_TOGGLEABLE_LEVER_RESOLVERS`), :590-625; scripts/generate_prompts.py:131-137 (the DESIGN.md constraint rule); the three reproducibility scopes (audit-phase-19-input-codex.md §6.1)
**Complexity:** Medium

The repo's front door is documented as false by both audits; this task makes it true and
adds the cheap checks that keep it true. README: replace the stale counts (volatile
absolutes become generated-or-checked facts; the PR count is not re-pinned by hand),
resolve the ladder-tip self-contradiction (baseline 6 is the tip), quote sample provenance
from the manifests (2026-07-20; 4p1i 34% / 9p2i 30%), relabel "decision accuracy 0.938" as
conversion-label accuracy with the 0.8646 composed decision figure beside it, replace the
"intentionally minimal" UI line, add the Node/npm prerequisite, and name the three
reproducibility scopes separately (replay integrity; same-runtime repeatability;
cross-platform optimizer portability — the third currently unsupported, per 19.3).
DESIGN.md: a demotion banner naming its vintage and pointing to a new 2-page
`docs/architecture.md` current-architecture note; AGENTS.md keeps its rules but stops
declaring stale prose authoritative, gains the graduation-sweep convention (rewrite
interior docstrings when a lever graduates — the structural fix for the drift class 19.2
sweeps) and a shallow-clone note. `llm/README.md` rewritten for the four providers with
Featherless canonical. `.env.example` rewritten from the live lever registry (the six
retired levers move to a "graduated — always ON" note; the one live toggle documented).
`scripts/check_doc_facts.py` (new): a cheap offline check that fails when README's checked
claims drift from committed sources (manifest dates/win rates, the lever registry, the
named ladder tip); wiring it into `scripts/check.sh` is NOT in scope (19.7 owns check.sh) —
it runs via pytest. The generator's DESIGN.md rule was already scope-gated in the
planning PR (locked decision 8), so this task's prompt permits the DESIGN.md edits; the
generator itself is not touched here. The demotion must also reach the DISPATCH surface:
`scripts/prompt_template.md.j2:19` currently tells every generated prompt "DESIGN.md is
the source of truth" — rewrite that authority line (AGENTS.md remains the rulebook;
docs/architecture.md is the current-architecture note; DESIGN.md is historical) and
regenerate ALL prompts in the same PR so no dispatched agent is ever told to obey the
document this task demotes. The README's third reproducibility scope quotes 19.3's
recorded outcome (the dependency edge exists for exactly this sentence).

**Files in scope:**
- README.md
- AGENTS.md
- DESIGN.md; (the demotion banner + per-section supersession notes only — the historical content is not rewritten)
- docs/architecture.md (new)
- llm/README.md
- .env.example
- scripts/prompt_template.md.j2; (the DESIGN.md authority line only)
- agent_prompts/; (regenerated — the authority line changes in every prompt, atomically with the demotion)
- scripts/check_doc_facts.py (new)
- tests/scripts/test_check_doc_facts.py (new)

**Files NOT in scope:**
- scripts/check.sh; (19.7 owns it — the fact check runs as a test)
- scripts/generate_prompts.py (the DESIGN.md scope-gate landed in the planning PR)
- orchestrator/replay.py (the lever registry is read, never edited)
- training/reports/ (report errata belong to 19.20)

**Definition of done:**
- [ ] Every named falsehood above is fixed and no README claim contradicts another README claim or a committed manifest; the three reproducibility scopes are stated; the ES portability caveat matches 19.3's honest wording (coordinate via the scopes text, not via shared files).
- [ ] `scripts/check_doc_facts.py` passes at HEAD, fails when a checked README fact is perturbed (test-pinned both ways), and runs offline in seconds.
- [ ] `.env.example` documents exactly the live toggleable levers from `orchestrator/replay.py:570-572` and labels the `_RETIRED_ALWAYS_ON_LEVERS` set as graduated/always-ON, cross-checked by a test importing the registry.
- [ ] DESIGN.md opens with the demotion banner; `docs/architecture.md` describes the CURRENT layering (engine → observation → agents/meetings ← orchestrator; llm behind the Protocol; eval/api privileged; frontend on generated types) in ≤2 pages; AGENTS.md routes readers to it and carries the graduation-sweep convention.
- [ ] The dispatch template's authority line no longer asserts DESIGN.md as the source of truth; all prompts are regenerated in this PR and `generate_prompts.py --check` is green — a repo grep proves zero generated prompts still carry the old sentence.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

For the fact check: prefer deleting volatile absolute counts from README over generating
them; where a number stays (win rates, dates, ladder tip), read it from the
manifest/registry and compare. Do not call the GitHub API — the PR count becomes prose
("300+; see GitHub") or is dropped.

**Ready-to-paste prompt:** `agent_prompts/task-19-1-front-door-truth.md`

### Task 19.2 — The in-code truth sweep: docstrings match the bytes
**Branch:** `phase-19-in-code-truth`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-19-triage.md §7 item 2 [S-Claude; §8 rows 5, 16 — every anchor re-verified at HEAD by the planning session]; agents/memory/beliefs.py:916-928 + :1102-1116 (the false "DEAD in production" pair) vs agents/memory/store.py:455-545 (the live write path, unconditional since 14.9); beliefs.py:1395-1399, :433, :1653, :1689-1692, :1791 (stale default-OFF claims) vs the four resolvers :183-197/:217/:285/:400 (hard-return True); meetings/transcript.py:2386-2387 + :2918-2920 vs resolvers :1360-1409 ("now always True"); meetings/manager.py:301-302, :1900, :1935-1946 (stale "default-OFF" citation-gate claims; the lever is always-ON at meetings/constants.py:54); orchestrator/game.py:12-13 (the false only-importer claim)
**Complexity:** Medium

In an agent-built repo, stale prose actively misleads the next agent: an implementer
trusting `beliefs.py`'s docstring would mislabel live production code as dead. Rewrite
every named false docstring to state the current truth, preserving history as history
("graduated at 18.12; was default-OFF") rather than as present tense. Replace
`orchestrator/game.py:12-13`'s false claim with the true, load-bearing invariant
(agents/meetings/llm are engine-free, enforced by import-linter; many privileged modules
import engine). This task executes the sweep; the convention that stops the class
regenerating (rewrite interior docstrings at lever graduation) lands in AGENTS.md via
19.1. Docstring/comment lines only — zero behavior bytes move.

**Files in scope:**
- agents/memory/beliefs.py; (docstring/comment lines only)
- meetings/transcript.py; (same)
- meetings/manager.py; (same)
- orchestrator/game.py; (the :12-13 module-docstring claim only)

**Files NOT in scope:**
- agents/memory/store.py (the live path is evidence, not an edit target)
- meetings/constants.py; (the resolver homes already state "now always True")
- any resolver body or lever mechanism (behavior untouched)

**Definition of done:**
- [ ] Each anchor listed in Section refs now states the truth; a repo grep for the exact stale phrases ("DEAD in production", "default-OFF" on the graduated levers named above) returns zero false claims in the swept files, and the PR quotes the grep.
- [ ] No behavior bytes moved: the diff contains only comment/docstring lines (assert via `git diff` review; the full suite and the prompt byte-golden stay green).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Keep the archaeology — these docstrings carry genuinely valuable history; the fix is tense
and truth, not deletion. Pattern: "LIVE since Task 13.5.2 (write path:
`store.py::record_alibi` from the orchestrator loop). Historical note: declared dead in
the 2026-06-25 diagnosis, revived at 13.5.2." Sweep only the named anchors plus any
same-file instance of the same class you can verify against a resolver in the same
sitting; do not free-hunt across the repo.

**Ready-to-paste prompt:** `agent_prompts/task-19-2-in-code-truth.md`

### Task 19.3 — ES portability: a portable sampler or a narrowed claim
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
`log`/`exp`/libm transcendentals are not) and regenerate the golden digest. Fallback path
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
- [ ] Primary path: the sampler's algorithm is documented (name + why each operation is portable), a double-run on this host is digest-identical, and the new golden is pinned. Fallback path: the claim text states exactly what is guaranteed (same-runtime repeatability) and the test carries an explicit platform pin/guard with the Darwin divergence cited.
- [ ] The in-code claim and README's reproducibility-scopes text (19.1) agree — coordinate wording, not files.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Inverse-CDF via a rational approximation (Acklam, or Wichura's AS241) needs only +, −, ×,
÷, and sqrt if you choose the polynomial form carefully — evaluate with explicit float64
arithmetic and document coefficient provenance. Keep the `rng.gauss` path available
nowhere (one sampler, one stream); regenerating the golden is a deliberate, documented ES
drift — say so in the pin's comment, quoting this task id.

**Ready-to-paste prompt:** `agent_prompts/task-19-3-es-portability.md`

### Task 19.4 — The reward-invariance claim correction
**Branch:** `phase-19-reward-claim`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-19-triage.md §7 item 4 + singleton 1 [S-Codex; VERIFIED §8 row 2]; training/rewards.py:18-24 (the false "cannot change the optimal policy" claim), :82-102 (`_side_potential` = cumulative kills/tasks — trajectory-dependent terminal potential), :157-198 + :259-305 (the kill-term economy vs ±1 terminal); tests/training/test_rewards.py:153-168 (proves telescoping only)
**Complexity:** Small

The shaping claim is mathematically false: at γ=1 the sum telescopes to
Φ(terminal)−Φ(initial), and because Φ(terminal) is cumulative kills it is
trajectory-dependent — the shaping is a real +1-per-kill incentive, not policy-invariant.
Correct the claim in code and pin the truth: a test with two trajectories of equal
environment reward and different terminal kill counts whose shaped returns differ. No
retraining, and no computed value moves — this changes prose and adds a test, nothing
else; the ML program is frozen and the finding is documented, not repaired. The
report-side erratum (recording the possible contribution to evidence-starved policies,
uncausal as measured) rides 19.20.

**Files in scope:**
- training/rewards.py; (docstring/comment lines only — computed values byte-identical)
- tests/training/test_rewards.py

**Files NOT in scope:**
- training/bakeoff/harness.py (the fitness consumer is untouched)
- training/reports/ (the erratum belongs to 19.20)

**Definition of done:**
- [ ] The docstring states the true property (telescoping ≠ invariance; the terminal-potential qualification) and names the +1/kill equivalence.
- [ ] The new test demonstrates non-invariance (two trajectories, equal env reward, different shaped return) and an existing-value pin proves no computed number moved.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Ready-to-paste prompt:** `agent_prompts/task-19-4-reward-claim.md`

### Task 19.5 — Metric and data-display truth: the conversion family and the dashboard
**Branch:** `phase-19-metric-display-truth`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-19-triage.md §7 items 5+6 [S-Claude; §8 rows 7, 8; the alibi 0.0-vs-None row was UNVERIFIED in the triage and is now re-verified at HEAD: eval/alibi_fabrication.py:88-94]; eval/meeting_quality.py:618-624 ("Expected ~0 … bug to chase") — CORRECTED PREMISE: the partition ALREADY imports `UNCITED_ZERO_FLAG_EJECT_MARKER` (eval/meeting_quality.py:179, censused as `citation_coerced_skip_ballots`), and the committed 9p2i report carries `citation_coerced_skip_ballots = 1` BESIDE `threshold_inversions = 87` — so the 87 are NOT unrecognized citation-gated SKIPs (the triage C6 mechanism is refuted; the three-surface doctrine disagreement stands); frontend/src/components/TournamentDashboard.tsx:296-312 (the "gate bug — expect 0" badge), :327-344 (the starved `genuine_class_conversion` labeled "PRIMARY gate"), :423-426 (the survival_rate n/a special case); eval/vote_correctness.py:11-25 (the sentinel demotion the dashboard ignores), :676-688 (`supplied_channel_conversion` — "the ONLY canary-eligible genuine-class cell"); scripts/measure_baseline.py (zero canary references — grep-verified)
**Complexity:** Medium

Three surfaces disagree about whether the flagship dashboard displays a bug, the declared
canary metric is wired to nothing, and two tiles mislead by name. Fix the family in one
pass: (a) the threshold-inversions re-doctrine, RECOUNT FIRST: the partition already
consumes the citation-gate marker (see Section refs — the corrected premise), so the
committed 87 inversions have an unmeasured cause mix; recount them by cause from
committed bytes (the partition's own inputs), record the by-cause table as a pinned
fixture, and THEN rewrite `eval/meeting_quality.py`'s "Expected ~0 … bug" prose and the
dashboard badge to the post-13.13 doctrine (nonzero intended) with whatever named split
the recount actually supports — never a cell invented ahead of the count; (b) wire
`supplied_channel_conversion` into the report assembly and `measure_baseline` output, and
demote the starved `genuine_class_conversion` tile to an explicitly historical label;
(c) rename/re-explain the `vote_correctness_rate` tile as what it is (evidence-backed
share of impostor ejections — a sentinel, not overall correctness); (d) make undefined
`alibi_fabrication.survival_rate` follow the package's None-iff-undefined convention and
delete the frontend special case that papers over it. Regenerate the four committed
`tournament-eval-report.json` derived views from committed replay bytes ($0) and update
the affected pins, quoting each delta in the PR. Replay bytes never move.

**Files in scope:**
- eval/meeting_quality.py
- eval/vote_correctness.py
- eval/alibi_fabrication.py
- scripts/measure_baseline.py
- scripts/build_sample_report.py; (the report-assembly wiring for the canary cell)
- api/schemas.py; (the report-DTO surface the new/None-able cells flow through — additive)
- frontend/src/types/api.ts; (regenerated)
- frontend/src/components/TournamentDashboard.tsx
- replays/samples/4p1i/tournament-eval-report.json; (regenerated derived view)
- replays/samples/9p2i/tournament-eval-report.json; (regenerated derived view)
- replays/ml_corpus/4p1i/tournament-eval-report.json; (regenerated derived view)
- replays/ml_corpus/9p2i/tournament-eval-report.json; (regenerated derived view)
- tests/eval/test_meeting_quality.py
- tests/eval/test_vote_correctness.py
- tests/eval/test_alibi_fabrication.py
- tests/eval/test_report_schema.py
- tests/eval/test_tournament_report.py

**Files NOT in scope:**
- meetings/manager.py (the marker constant is imported, never edited)
- eval/watchability.py (floors and referee untouched — no gate moves)
- replays/**/replay-seed-*.jsonl (recorded bytes are frozen)

**Definition of done:**
- [ ] Verify-then-fix for the one previously-unverified element: confirm the 0.0-vs-None behavior at `eval/alibi_fabrication.py:88-94` before changing it (it is re-verified at HEAD; re-run the check in-session and quote it).
- [ ] The recount of the committed 87 inversions is recorded (a by-cause table in the PR + a pinned fixture over committed bytes); the partition's docstring and the dashboard badge state the post-13.13 doctrine consistent with the recount; any bucket split ships only if the recount supports it; the existing marker consumption (`meeting_quality.py:179` ← `meetings.manager`) is pinned as already-wired, not re-derived.
- [ ] `supplied_channel_conversion` appears in the regenerated reports and in `measure_baseline` output; the dashboard's gate tile shows it; the starved cell is labeled historical; the correctness tile is renamed/explained; the alibi tile renders n/a from a true `None`.
- [ ] Every regenerated view is byte-reproducible from committed replays with the exact command recorded in the PR; `bash scripts/verify_samples.sh` stays green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Land the eval-side reclassification first and regenerate reports once, at the end, so the
pin churn happens in one commit. The dashboard consumes generated types — if a report cell
is added, extend `api`/report schema surfaces the reports actually flow through (follow
`scripts/build_sample_report.py`'s existing assembly; `tests/eval/test_report_schema.py`
shows the shape contract). The frontend n/a special case to delete sits at
`TournamentDashboard.tsx:423-426`.

**Ready-to-paste prompt:** `agent_prompts/task-19-5-metric-display-truth.md`

### Task 19.6 — The one-line defects
**Branch:** `phase-19-one-line-defects`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-19-triage.md §7 item 7 [S-Claude; VERIFIED §8 row 9]; pyproject.toml (zero `httpx`) vs llm/featherless_client.py:764 (the lazy `import httpx`); llm/provider.py:52 (`_FALLBACK_PRICING_USD_PER_MTOK = (3.00, 15.00)`) + :659-662 (the silent `.get` fallback); frontend/src/tokens.ts:39-47 (the ink ramp: 900/700/500/400/300/200/100 — no 600) vs frontend/src/components/MeetingView.tsx:517 + HighlightCard.tsx:60 (`text-ink-600` used); agents/strategic/prompts/loader.py:119 (`DEFAULT_PROMPT_SET = "qwen3_5_9b"` — two generations behind the operational baseline)
**Complexity:** Small

Four verified one-line-class defects, fixed loud: declare `httpx` as a direct dependency
(the canonical provider currently rides transitive luck); make unknown-model pricing fail
loud (raise with the model name) instead of silently billing at $3/$15 — cost accounting
is exactly where the no-silent-fallback doctrine matters; add `ink-600` to the token ramp
(or remap the two call sites to an existing step if the design ramp intends seven stops)
plus a token-exists check; and make the bare-environment prompt-set fallback LOUD — the
default stays `qwen3_5_9b` for byte-identity (a documented owner decision), but falling
back without the env override now emits a one-line stderr notice naming the operational
baseline variable. No prompt bytes move (the byte-golden proves it).

**Files in scope:**
- pyproject.toml; (the httpx declaration)
- uv.lock; (regenerated for the new declaration)
- llm/provider.py
- frontend/src/tokens.ts
- agents/strategic/prompts/loader.py
- tests/llm/test_provider.py
- tests/agents/test_prompt_loader.py; (or the loader's actual test home — locate by grep, name it in the PR)

**Files NOT in scope:**
- llm/featherless_client.py (the import stays lazy; only the declaration moves)
- frontend/src/components/MeetingView.tsx + HighlightCard.tsx (call sites stand; the token appears under them)
- .env.example (19.1's file — the env-var documentation rides there)

**Definition of done:**
- [ ] Unknown-model pricing raises with the model name (test-pinned); known models unchanged.
- [ ] `httpx` is a declared dependency and the lock regenerates cleanly.
- [ ] `text-ink-600` resolves to a real token (or the two call sites use a real step) with a ramp-integrity test.
- [ ] The loader emits the fallback notice exactly when the env override is absent (test-pinned) and prompt bytes are unchanged (byte-golden green).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Ready-to-paste prompt:** `agent_prompts/task-19-6-one-line-defects.md`

### Task 19.7 — Public and build hygiene + the MIT posture
**Branch:** `phase-19-public-hygiene`
**Depends on:** 19.6
**Section refs:** audits/audit-phase-19-triage.md §7 item 8 [S-Codex/S-Claude; §8 rows 12, 16] + locked decision 4 (MIT + minimal); .github/workflows/ci.yml (no `permissions:` block; checkout@v6/setup-python@v6/setup-uv@v7/setup-node@v4 by tag; the frontend-checks job :32-57 repeating scripts/check.sh:17-24); pyproject.toml:7-21 (pytest/ruff/mypy/hypothesis/import-linter in RUNTIME deps) vs :48-51 (dev group = one stub); package-lock.json (a 10-line dead root lockfile); the absent LICENSE/CONTRIBUTING/SECURITY (verified absent at HEAD)
**Complexity:** Medium

Public-repo basics plus CI hygiene in one pass. CI: add `permissions: contents: read`,
pin every action to a full SHA (tag in a comment), and deduplicate the frontend build —
`scripts/check.sh` keeps its leg (one-command local truth) and CI keeps ONE frontend
build, not two paths building the same thing per run. Packaging: partition dev tools
(pytest, ruff, mypy, hypothesis, import-linter) into the dev group, keep runtime deps
minimal, regenerate the lock, and make CI/setup install the dev group; delete the dead
root `package-lock.json`. Known, accepted boundary: `eval/leak_test.py` imports pytest at
module level and `training.bakeoff.harness` imports from it, so training/eval remain
dev-environment surfaces until 19.24 promotes the scanners to a pytest-free library — the
runtime-only claim below covers the production packages ONLY, and the contract says so
rather than hiding it. Posture (locked decision 4): LICENSE (MIT), a short
CONTRIBUTING.md (agent-built experiment; the contract workflow; issues welcome, PRs are
not the workflow), and SECURITY.md (the replay API is an intentionally unauthenticated GM
view — loopback only; how to report).

**Files in scope:**
- .github/workflows/ci.yml
- scripts/check.sh
- scripts/setup_env.sh; (the dev-group install, if the partition requires it)
- pyproject.toml
- uv.lock
- package-lock.json; (deleted)
- LICENSE (new)
- CONTRIBUTING.md (new)
- SECURITY.md (new)

**Files NOT in scope:**
- frontend/package.json (19.12's file)
- README.md (19.1's file — link additions ride the README chain)

**Definition of done:**
- [ ] CI runs green with the permissions block, SHA-pinned actions, and exactly one frontend build per run.
- [ ] `uv run pytest` and `bash scripts/check.sh` still pass locally after the dependency partition (dev group installed by setup), and the runtime-only smoke actually proves the partition: `uv run --no-dev --exact python -c "import engine, orchestrator, api, agents, meetings, llm"` (the `--no-dev --exact` flags are load-bearing — a bare `uv run` re-syncs the dev group and vacuously passes) plus an assertion that pytest/mypy are absent from that environment — training/eval are explicitly excluded from the claim until 19.24 (the known `eval.leak_test` pytest import, stated in the partition's notes).
- [ ] LICENSE is MIT with the owner's copyright line; CONTRIBUTING and SECURITY match locked decision 4's posture and the deployment doc's trust boundary.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `.github/workflows/ci.yml` first to see which job runs what: the duplication is the
frontend-checks job re-running the `npm ci && tsc:check && build` that check.sh's leg also
runs inside the Python job. Keep the split that maximizes CI parallelism and delete the
other copy. For the partition, `uv`'s dependency groups + `uv sync --group dev` is the
shape; CI must install the group explicitly.

**Ready-to-paste prompt:** `agent_prompts/task-19-7-public-hygiene.md`

### Task 19.8 — Corpus truth disclosures
**Branch:** `phase-19-corpus-disclosures`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-19-triage.md §7 item 9 [S-Claude/S-Codex; §8 rows 12, 13 VERIFIED; the roll-call coverage split is S-Codex and NOT independently re-run — verify-then-fix]; agents/tactical/impostor_policy.py:39-40 ("after the kill … the impostor must not file a report" — the structural reporter-innocence prior); replays/ml_corpus/README.md:228-236 (the no-husk doctrine the committed husks violate), :91-102 (the by-game split); the verified counts: 21.3% engine-rejected 9p kill submissions (48/225 samples), ~5% husk turns (53/971 samples; 137/2,726 corpus), 19/798 crew-witnessed kills with zero non-victim co-present at the decision frame
**Complexity:** Medium

The corpus is honest about what it contains and silent about what that implies. Add a
"capability disclosures" section to the corpus README and a short mirror note in each
samples MANIFEST, recording as measured facts: the absolute reporter-innocence prior
(structural — the scripted impostor cannot report or call meetings, so 100% of training
examples carry it; any learned impostor that self-reports invalidates the crew's learned
prior); the engine-rejected kill-submission rate; the player-visible
`[invalid accusation target …]` husk rate against the README's own no-husk doctrine;
zombie-vent re-litigation; skip-template repetition; wait-streak/ping-pong mover theater;
model-originated fourth-wall statements and machinery quotation; the role-correlated
public response shape (crew ~99.6–99.7% roll-call coverage vs impostor ~45.5–46.5% —
verify-then-fix: recompute the split from committed bytes before quoting it); and the
too-clean evidence economy. Disclosures record capability limitations — zero gameplay
tuning, zero byte changes outside the two documentation surfaces.

**Files in scope:**
- replays/ml_corpus/README.md
- replays/samples/4p1i/MANIFEST.md
- replays/samples/9p2i/MANIFEST.md

**Files NOT in scope:**
- agents/tactical/impostor_policy.py (the prior is disclosed, not changed)
- replays/**/replay-seed-*.jsonl + tournament-eval-report.json (no bytes move)

**Definition of done:**
- [ ] Verify-then-fix first: every number written is recomputed from committed bytes this session with the stdlib command recorded in the PR (numerator/denominator quoted); the roll-call split in particular is re-derived, not copied from the audit.
- [ ] The disclosures section covers every phenomenon listed above with its committed-bytes citation, and explicitly reconciles the husk rate with the README's no-husk doctrine (a recorded deviation, not a silent contradiction).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The audits' parses are the recipe (turn counts, ballot counts, husk substrings, roll-call
response fields); reimplement each as a ~20-line stdlib script over the JSONL and paste
the outputs into the PR. Where your recount differs from an audit's figure, the recount
wins and the delta is noted — generated facts beat copied facts.

**Ready-to-paste prompt:** `agent_prompts/task-19-8-corpus-disclosures.md`

---

## Wave 2 — the spectator tells one coherent game

### Task 19.9 — The curated spectator default + the featured path + the rubric re-score
**Branch:** `phase-19-curated-default`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-19-triage.md §7 item 10 [C; §8 rows 10, 16] + singleton 29; api/replay_loader.py:2653 (`DEFAULT_SET = "4p1i"`); frontend/src/components/ReplayPicker.tsx:19-20 + :211-213 (the false "mostly zero-meeting" copy — actual: 39/50 4p1i games have exactly one meeting, 11/50 zero), :284-290 (the staleness banner keyed on git_head); frontend/src/components/GuidedTour.tsx:30 (the tour already targets 9p2i best-rubric); experiments/lab/rubric_score.py (offline, $0 — verified: no LLM/provider imports); engine/maps/canonical_1.yaml:39-44 (the map's own "only crew win path becomes ejection" intent that 4p1i's task-timer economy contradicts); the audits' named good tail (9p2i seeds 2/8/17/23; 4p1i 41/29/2)
**Complexity:** Medium

The weakest set is the product default and its copy is false. Flip `DEFAULT_SET` to
`"9p2i"`; relabel 4p1i honestly ("fast technical fixture — median ~12 ticks, at most one
meeting, most games decided by the task timer"); replace the false picker copy with
recomputed facts; re-run the rubric scorer at HEAD to clear the staleness banner (a $0
offline regeneration of the committed derived view); and add a hand-curated FEATURED list
— the named good-tail seeds with a one-line why-watch label each. Curation is editorial
and by hand: a fresh rubric score clears staleness but does NOT validate human-interest
ordering, so wherever the rubric scalar renders it is labeled narrowly ("internal
pacing/structure heuristic — not a human rating").

**Files in scope:**
- api/replay_loader.py; (the DEFAULT_SET constant + the featured-list serving, if served)
- frontend/src/api/client.ts; (ONLY the omitted-set contract comment at :62-65 — it documents the 4p1i server default this task retires — plus a pin that an omitted `set` resolves 9p2i)
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/GuidedTour.tsx; (retarget onto the curated featured entry if its selection rule changes)
- replays/samples/9p2i/results-rubric-score.json; (regenerated at HEAD — derived view)
- tests/api/

**Files NOT in scope:**
- frontend/src/hooks/usePlayback.ts + frontend/src/App.tsx (19.10's files)
- experiments/lab/rubric_score.py (run, not edited)
- replays/**/replay-seed-*.jsonl (frozen)

**Definition of done:**
- [ ] The API default set is 9p2i (pinned in tests/api/), the client's omitted-set contract comment states it, and the picker's 4p1i copy quotes recomputed meeting-count facts with the fixture relabel.
- [ ] The rubric re-score is committed, the staleness banner is clear at HEAD, and the regeneration command is recorded in the PR.
- [ ] The featured list exists (the named seeds + editorial labels), the tour lands on a featured game, and every rendered rubric scalar carries the narrow label.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The featured list is data, not machinery: a small committed structure (seed, set, one-line
label) served beside the replay list — resist building a curation system. GuidedTour
already picks the rubric's best 9p2i game; after re-scoring, verify its target is on the
featured list and pin that agreement.

**Ready-to-paste prompt:** `agent_prompts/task-19-9-curated-default.md`

### Task 19.10 — Playback coherence: the meeting pause, the unspoiled mode, the finale card
**Branch:** `phase-19-playback-coherence`
**Depends on:** 19.5, 19.9 (the first edge is api/schemas.py + generated-types serialization)
**Section refs:** audits/audit-phase-19-triage.md §7 item 11 [S-Codex; VERIFIED §8 row 10]; frontend/src/hooks/usePlayback.ts:40 (500 ms base cadence), :304-331 (auto-advance), :333-382 (auto-follow selects a meeting on its single frame and clears it on the next — :366/:376); frontend/src/App.tsx:290 (the header renders `meta.winner` unconditionally), :366-489 (RosterRail mixes pre-ejection `agent_states` with post-ejection `advantage` counts); api/replay_loader.py:1188-1195 (the loader's own deliberate-mix comment)
**Complexity:** Integration

The app's core content cannot be consumed on the default Play path: a meeting gets one
500 ms frame, the header spoils the winner from frame zero, the game simply stops with no
resolution, and a meeting frame carries two different times. Fix the narrative spine:
(a) autoplay pauses on meeting entry with Resume and next-beat affordances; (b) unspoiled
mode is the default — the winner render and any outcome-revealing chrome are deferred
until the finale or an explicit reveal toggle; (c) a real finale card — winner, win
reason, the decisive events, a compact per-agent "what they knew vs the truth" recap, and
the reveal toggle — built from data already recorded in the replay (exposed as additive
DTO fields where the view model lacks them); (d) one frame, one time: model the meeting's
pre-resolution and post-resolution states separately or label the transition explicitly,
resolving the deliberate mix the loader documents.

**Files in scope:**
- frontend/src/hooks/usePlayback.ts
- frontend/src/App.tsx
- frontend/src/lib/playback.ts; (pure helpers for pause/beat/finale state — keep them pure, 19.12 tests them)
- api/replay_loader.py
- api/schemas.py; (additive DTO fields only)
- frontend/src/types/api.ts; (regenerated)
- tests/api/

**Files NOT in scope:**
- frontend/src/components/MeetingView.tsx (19.11's file)
- frontend/src/components/ReplayPicker.tsx + GuidedTour.tsx (19.9's files)
- replays/ (frozen)

**Definition of done:**
- [ ] Default Play on a featured replay pauses at each meeting, resumes on demand, and ends on the finale card; the winner is not rendered before the finale without the reveal toggle.
- [ ] Meeting-tick frames expose explicit pre/post-resolution semantics (fixture-pinned through the loader: the roster a meeting deliberates over and the advantage after its result are never conflated in one unlabeled frame).
- [ ] The DTO additions are additive (existing committed fixtures still parse; the fidelity fixture regenerates green).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The pause belongs in the playback reducer, not the component: emit a "meeting-entered"
beat from the frame index (the key-moment machinery in `lib/playback.ts` already knows
meeting frames) and let the hook consume it. The finale's raw material (`winner`,
`winner_reason`, final tick, decisive events) is in the recorded `game_over`/meeting
records — thread it through `api/schemas.py` as one additive `GameFinale` view rather
than scattering fields.

**Integration risk:**

This changes default user-visible behavior on purpose; the risk is regressing the pinned
interactions that already work (keyboard transport, fog enforcement, URL state). Until
19.12's automated pins exist, the PR carries a manual checklist over those behaviors, and
the DTO change is additive-only so older committed fixtures keep parsing.

**Public types introduced:**
- `api.schemas.GameFinale`

**Ready-to-paste prompt:** `agent_prompts/task-19-10-playback-coherence.md`

### Task 19.11 — The evidence taxonomy: proof is not a contradiction
**Branch:** `phase-19-evidence-taxonomy`
**Depends on:** 19.10
**Section refs:** audits/audit-phase-19-triage.md §7 item 12 [S-Codex/S-Claude; §8 rows 10, 14] + item 20 (the four mechanisms preserved as separate fixtures); meetings/schemas.py:442-456 (vent_sighting: "both event ids reference the SAME spoken observation"); meetings/transcript.py:2878-2906 (the self-linked emission); frontend/src/components/MeetingView.tsx:303-385 with :348 (every flag rendered `A ↔ B`, so grounded vent proof shows as `p-X ↔ p-X` under "Contradictions"); the traced injustice exhibits (§8 row 14: seed 17 M0, seed 47; plus seed 12 M0, seed 23 M1, 4p1i seeds 41/49)
**Complexity:** Integration

A grounded vent sighting is role proof, not a contradiction — but the schema carries it
through `ContradictionRef` and the UI renders `p-1 ↔ p-1` under "Contradictions", while
weak interval flags render with the same visual weight as hard proof. Derive an evidence
taxonomy at the DTO layer (recorded bytes and `meetings/` schemas are frozen — this is
classification, not schema migration): every flag classifies as ROLE-PROOF (vent_sighting
/ self-linked), CROSS-STATEMENT CONTRADICTION, or WEAK-SIGNAL (the `[weak signal…]`
description stamp), fail-loud on anything unclassifiable. The UI renders proof as proof
(no self-linked `↔`), subordinates weak flags visually, and never labels an unverified
statement-pair "VERIFIED". Preserve the four evidence-honesty mechanisms as SEPARATE
committed fixtures so the post-19 decision has executable exhibits: the
provenance-impossible sighting (9p2i seed 23 M1), the content-vs-own-memory miss (seed 12
M0), the one-tick interval artifact (4p1i seeds 41/49), and the equal-weight conflict
(seed 41). Prompt templates are NOT touched (locked decision 1) — the prompt-side flag
naming routes to the post-19 decision.

**Files in scope:**
- api/schemas.py
- api/replay_loader.py
- frontend/src/types/api.ts; (regenerated)
- frontend/src/components/MeetingView.tsx
- tests/api/

**Files NOT in scope:**
- meetings/schemas.py + meetings/transcript.py (recorded-byte schemas and emission are frozen; the taxonomy derives)
- agents/strategic/prompts/ (substrate behavior — the NOT-list)
- eval/ (the eval-side twin of this classification is 19.14's)

**Definition of done:**
- [ ] The classification is total over all committed bytes: a pin counts each category corpus-wide (samples + ml_corpus) and an unknown kind fails loud, never defaults.
- [ ] The committed self-linked vent records render as role proof (no `p-X ↔ p-X` anywhere); weak-stamped flags are visually subordinated; the four mechanism fixtures exist with their seed/meeting anchors and one-line descriptions of what each demonstrates.
- [ ] The DTO change is additive; older fixtures parse; the fidelity fixture regenerates green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The classifier is one pure function over the flag record (kind, event ids, description
stamps) living API-side; keep it in one place with the category rules readable as a
table. `event_a_id == event_b_id` or `kind == "vent_sighting"` ⇒ role proof; the
`[weak signal` stamp is already machine-detectable in `description`. 19.14 implements the
eval-side twin — the two classifications are cross-pinned (same counts on the same
bytes), which is why the category rules must be trivially portable.

**Integration risk:**

The taxonomy touches the most-watched UI surface and a served DTO in one PR. Two guards:
the corpus-wide category-count pin (any classification drift is a loud diff), and
additive-only DTO fields so no existing consumer breaks. If any committed flag defies the
three categories, stop and record it as a finding — never add a silent OTHER bucket.

**Public types introduced:**
- `api.schemas.EvidenceCategory`

**Ready-to-paste prompt:** `agent_prompts/task-19-11-evidence-taxonomy.md`

### Task 19.12 — The frontend test baseline: Vitest, ESLint, one Playwright journey
**Branch:** `phase-19-frontend-test-baseline`
**Depends on:** 19.7, 19.10
**Section refs:** audits/audit-phase-19-triage.md §7 item 13 [C]; frontend/package.json:6-14 (no test script); the two `eslint-disable` comments with no linter (frontend/src/components/MapView.tsx:329, AgentToken.tsx:142 — verified: no eslint config or dependency exists); frontend/src/store/replayStore.ts:445 + :488 (one error field, three meanings) [S-Claude — re-verified at HEAD]; frontend/src/lib/playback.ts (407 LOC of pure functions, the natural unit-test target)
**Complexity:** Integration

The flagship surface has zero tests and suppresses a linter that does not exist. Land the
baseline: Vitest with unit tests for `lib/playback.ts`'s pure functions (tick/frame
mapping, key moments, the new pause/beat/finale helpers) and the store's race guards;
split the three-meaning error field into distinct states; flat-config ESLint whose rule
set actually includes the rules the two existing disables reference; and ONE Playwright
journey — featured replay → play → meeting pause → inspect ballots → finale (unspoiled →
reveal) — plus assertions pinning the keyboard transport, fog enforcement, and
reduced-motion behaviors that already work. Wire vitest + eslint into `scripts/check.sh`
and CI; the Playwright journey runs in CI and on demand locally (the environment's
pre-installed Chromium; never `playwright install` in CI without caching).

**Files in scope:**
- frontend/package.json
- frontend/package-lock.json
- frontend/vitest.config.ts (new)
- frontend/eslint.config.js (new)
- frontend/src/lib/playback.test.ts (new)
- frontend/src/store/replayStore.ts
- frontend/src/store/replayStore.test.ts (new)
- frontend/e2e/ (new)
- frontend/playwright.config.ts (new)
- frontend/src/components/ReplayPicker.tsx; (ONLY the `currentReplayError` selector update the error-field split forces — verified consumer at :358)
- frontend/src/components/MindInspector.tsx; (same — verified consumer at :758)
- .github/workflows/ci.yml
- scripts/check.sh

**Files NOT in scope:**
- frontend/src/App.tsx + usePlayback.ts (19.10's files — tested here, not edited; if a race guard fix requires an edit there, coordinate as a follow-up, don't fold it in)
- frontend/src/components/ (beyond the two named selector updates — behavior pinned, not changed)

**Definition of done:**
- [ ] `npm run test` (vitest) and `npm run lint` exist and pass; the two pre-existing disables reference rules the config enables; new lint debt is zero or explicitly inline-justified.
- [ ] The error-field split is landed with a store test proving stale-response races cannot clobber newer state.
- [ ] The Playwright journey passes headless against the local dev servers, covering pause → finale with the keyboard/fog/reduced-motion pins.
- [ ] check.sh runs vitest + eslint; CI runs all three legs green with the journey's runtime and flake posture noted in the PR.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Keep the journey to ONE spec file with generous, condition-based waits (no sleeps) and a
single retry in CI; flake here poisons the whole gate's credibility. The store race
guards are testable without the DOM — drive the store directly with out-of-order promise
resolutions.

**Integration risk:**

check.sh and CI are shared, load-bearing surfaces (19.7 just touched both — this task
depends on it precisely to serialize). The risk is gate-runtime creep and browser flake:
vitest/eslint are cheap and belong in check.sh; the browser journey is CI + on-demand,
and its CI job must reuse the preinstalled browser rather than downloading one per run.

**Ready-to-paste prompt:** `agent_prompts/task-19-12-frontend-test-baseline.md`

### Task 19.13 — Proof above the fold + the static demo artifact
**Branch:** `phase-19-demo-artifact`
**Depends on:** 19.1, 19.9, 19.10, 19.14, 19.16 (the 19.14 edge is TournamentDashboard.tsx serialization — the metrics panel lands before the fetch-seam routing)
**Section refs:** audits/audit-phase-19-triage.md §7 item 14 [C]; docs/deployment.md:10-33 (the unauthenticated-GM-view trust boundary — preserved verbatim in spirit); docker-compose.yml:31-37 (loopback binding); the verified gap: `vite build` output is never served, no StaticFiles mount, no screenshot/GIF anywhere in README
**Complexity:** Medium

The strongest surface has no visual proof and no shippable artifact. Two deliverables:
(a) proof above the fold — a screenshot and a short capture (≤60 s GIF/video) of the
featured 9p2i journey placed at the top of README with three reproducible-claim commands
under them; (b) `scripts/build_demo_bundle.py` — a self-contained static demo: the built
frontend plus pre-baked JSON for the featured replays only, no API process, no GM
surface, playable from any static file server. The client gains a static-data mode (a
data-source seam reading pre-baked `./data/*.json` when built for the bundle).
`docs/deployment.md` documents the bundle as the ONLY sanctioned public artifact and
keeps the live API loopback-only; binding `0.0.0.0` remains forbidden.

**Files in scope:**
- README.md
- docs/deployment.md
- docs/media/ (new — the committed captures)
- scripts/build_demo_bundle.py (new)
- frontend/src/api/client.ts; (the static-data seam only)
- frontend/src/components/BeliefMatrix.tsx; (its direct `fetch` at :30-46 routes through the seam — verified bypass)
- frontend/src/components/TournamentDashboard.tsx; (the direct rubric `fetch` at :753 routes through the seam — same)
- frontend/vite.config.ts; (the bundle build mode, if needed)
- tests/scripts/test_build_demo_bundle.py (new)

**Files NOT in scope:**
- api/ (no StaticFiles mount — the bundle replaces the need; the live API's posture is unchanged)
- docker-compose.yml (loopback stance stands)

**Definition of done:**
- [ ] `scripts/build_demo_bundle.py` builds offline from committed bytes into one directory; opening it via a static server plays the featured journey end-to-end (pause → finale) with zero API calls (test asserts no non-static fetch paths in bundle mode).
- [ ] README opens with the capture + screenshot and three commands that reproduce top claims (determinism double-run, verify_samples, the spectator boot); media files are committed at reasonable size (< a few MB total).
- [ ] deployment.md documents the bundle path and restates the loopback boundary; the words that forbid exposing the GM API survive.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The seam in `client.ts` should be one base-resolution function (static mode ⇒ relative
`./data/…`), not a parallel client. Bake only the featured seeds + the picker/rubric
metadata they need — the bundle's weight budget is a demo, not the corpus. Capture the
GIF with the headless Chromium already in the environment; keep it under ~15 s of
footage at modest resolution to respect the media budget.

**Ready-to-paste prompt:** `agent_prompts/task-19-13-demo-artifact.md`

### Task 19.14 — The deduction metrics: what "deduction" means, instrumented
**Branch:** `phase-19-deduction-metrics`
**Depends on:** 19.5, 19.11, 19.18 (the last is the eval/meeting_quality.py serialization edge — labels land before the wrapper extension)
**Section refs:** audits/audit-phase-19-triage.md §7 item 15 [S-Codex/S-Claude convergent objective; §8 rows 3, 10, 14; the roll-call split and the 13-redirected-ejects cells are source-specific and NOT independently re-run — verify-then-fix] + item 24 disclosure twin (19.8); the headline cross-tab (9p2i samples: 70 flagged meetings → 68 imp/2 inn ejected, 95 unflagged → 10/21; corpus: 213/248; non-direct accuracy 30.3%/39.3%); tests/eval/test_kill_craft.py:66-135 (the witnessed-supply pins to adopt); the C5 lesson (define the metric before counting)
**Complexity:** Medium

The precondition for any future gameplay phase (locked decision 6): make "deduction"
measurable without touching gameplay. One pure eval module computing, per set:
direct-proof vs non-direct ejection accuracy (the audits' cross-tab as a permanent,
pinned metric); weak-flag-only conviction rate; same-agent turn→ballot consistency;
public response coverage split by role; engine-redirected ballot share; witnessed and
co-present evidence supply (adopting the kill-craft cells); and scaffold-leakage rates
split between model-originated role/machinery statements and guard-originated stale
rationales — with each metric DEFINED in the module docstring before it is counted (the
C5 lesson: the audits' fourth-wall counts differed only by definition). The flag
classification must agree with 19.11's DTO taxonomy (cross-pinned counts on the same
bytes). Wire the headline cells into the report assembly and a proof-vs-inference
dashboard panel; regenerate the four derived reports. This module's committed cells are
the evidence the 19.28 close puts in front of the owner.

**Files in scope:**
- eval/deduction_metrics.py (new)
- tests/eval/test_deduction_metrics.py (new)
- scripts/build_sample_report.py; (report wiring)
- eval/meeting_quality.py; (ONLY the persisted `TournamentEvalReport` wrapper/assembler extension — the report model is `extra="forbid"`, so the new cells must be real fields on the canonical owner; no metric logic moves here)
- api/schemas.py; (the new report cells' DTO surface — additive)
- frontend/src/types/api.ts; (regenerated)
- frontend/src/components/TournamentDashboard.tsx; (the proof-vs-inference panel)
- replays/samples/4p1i/tournament-eval-report.json; (regenerated)
- replays/samples/9p2i/tournament-eval-report.json; (regenerated)
- replays/ml_corpus/4p1i/tournament-eval-report.json; (regenerated)
- replays/ml_corpus/9p2i/tournament-eval-report.json; (regenerated)
- tests/eval/test_report_schema.py; (the added cells)
- tests/eval/test_tournament_report.py

**Files NOT in scope:**
- meetings/ + agents/ (measurement only — zero substrate movement)
- eval/vote_correctness.py (consumed, not edited; 19.5 already landed its truth pass)
- eval/kill_craft.py (its cells are imported/adopted, not reimplemented)

**Definition of done:**
- [ ] Verify-then-fix for the source-specific cells: the roll-call coverage split and the engine-redirected eject count are recomputed from committed bytes before pinning (and the recount is the pin).
- [ ] The 9p2i cross-tab pin reproduces the triage's independent recount exactly (165 meetings; 70 flagged → 68/2; 95 unflagged → 10/21); the corpus twin is pinned beside it.
- [ ] Every metric has a docstring definition stating numerator, denominator, and what it does NOT measure; the weak/proof classification counts match 19.11's DTO taxonomy on the same bytes (cross-pin).
- [ ] The regenerated reports carry the cells; the dashboard panel renders direct-proof vs non-direct accuracy side by side with honest labels; regeneration commands recorded.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Follow the `eval/deception_instruments.py` shape (pure function over the assembled report
+ replay records, one frozen report model, committed-bytes pins primary, Wilson intervals
on rare cells). The redirect markers and guard markers are greppable in recorded ballots;
the roll-call fields are in the recorded meeting records. Turn→ballot consistency needs a
definition that tolerates SKIP (an accusation followed by a SKIP ballot is inconsistency
only when the accused was votable) — write the definition first, then count.

**Public types introduced:**
- `eval.deduction_metrics.DeductionMetricsReport`
- `eval.deduction_metrics.compute_deduction_metrics`

**Ready-to-paste prompt:** `agent_prompts/task-19-14-deduction-metrics.md`

### Task 19.15 — Guard-rationale redaction (the dormant path)
**Branch:** `phase-19-guard-rationale`
**Depends on:** 19.2
**Section refs:** audits/audit-phase-19-triage.md §7 item 16 [S-Codex; mechanism confirmed by the triage's partner-phrase counts and re-verified at HEAD]; meetings/manager.py:1906-1913 (the call site) + :2893-2925 (`coerce_teammate_ballot_to_skip` — rewrites the target, prepends a marker, and KEEPS `ballot.rationale_text` at :2923, preserving omniscient teammate/self-kill text)
**Complexity:** Small

When the vote guard coerces a teammate ballot to SKIP, the preserved rationale can say
"p-3 is my partner" — spectator-visible omniscience. Replace the preserved rationale with
a neutral strategic reason while KEEPING the audit marker that the guard changed the
target (auditability is never laundered — the redaction is itself marked). Dormant for
committed bytes (they are frozen and unaffected); this matters on any future recording.
Explicitly distinct from model-originated fourth-wall statements, which 19.14 measures
and 19.8 discloses — this fixes only the guard-originated class.

**Files in scope:**
- meetings/manager.py; (the guard's rationale construction only)
- tests/meetings/test_vote_guard_rationale.py (new)

**Files NOT in scope:**
- replays/ (committed bytes frozen — the fix is forward-looking)
- meetings/voting.py (19.26's file)

**Definition of done:**
- [ ] A coerced ballot carries the guard marker plus a neutral rationale with zero teammate/self-kill phrasing (fixture-pinned, including the marker's survival for auditability); the docstring labels the path dormant-for-committed-bytes.
- [ ] Committed-byte surfaces are unaffected (full suite + byte-golden green).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Ready-to-paste prompt:** `agent_prompts/task-19-15-guard-rationale.md`

### Task 19.16 — The outsider reading guide + the audit-idiom glossary
**Branch:** `phase-19-reading-guide`
**Depends on:** 19.1
**Section refs:** audits/audit-phase-19-triage.md §7 item 17 [S-Claude] + rows 23 (N1/N2 and the clean negatives), the legibility-cliff finding (audit-phase-19-input-claude.md §3.2 item 5: the corpus is case law with no glossary); the named good-tail seeds (19.9's featured list)
**Complexity:** Medium

The project's institutional memory is unreadable to outsiders — the strongest single
asset (the honesty machinery) is invisible behind the idiom. Write `docs/reading-guide.md`
(~200 lines): the meta-story (the workflow experiment, the honesty culture, the key
verified numbers each with its committed source path); a glossary of the audit idiom
(baseline N, the ladder tip, the §1.3 bar, canary denominator, NO-FLIP,
findings-not-failures, the 15.18 convention, graduated levers, adopting records, the
two-owner gate, errata discipline); a "where the bodies are buried" tour (the three
audits worth reading first and what each proves); the demo path (the featured seeds and
why each is worth watching); the capability distinctions an outsider needs
(evidence-processing vs deception vs general social deduction — with the vent-proof
qualification stated plainly); and the honest ML story (N1/N2, the clean negatives, the
frozen program, where the reopening checklist lives). README links it.

**Files in scope:**
- docs/reading-guide.md (new)
- README.md; (the link line only)

**Files NOT in scope:**
- audits/ (the corpus is described, never rewritten)
- docs/architecture.md (19.1's file)

**Definition of done:**
- [ ] Every number quoted carries its committed source path; every glossary entry is verifiable against a cited audit usage; the guide's demo path matches 19.9's featured list.
- [ ] An outsider path exists: README → guide → demo → the three named audits, with no undefined idiom on the path.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Write for a senior engineer with zero context and five minutes: short declarative
sentences, the numbers doing the arguing. The vent-proof qualification (87% of correct 9p
ejections ride an ejectee-specific vent sighting; ~30–39% otherwise) belongs in the
capability section stated exactly — the guide's credibility rests on volunteering it.

**Ready-to-paste prompt:** `agent_prompts/task-19-16-reading-guide.md`

### Task 19.17 — The event ticker + cost chips (the gated tail)
**Branch:** `phase-19-ticker-cost`
**Depends on:** 19.10, 19.12
**Section refs:** audits/audit-phase-19-triage.md §7 item 18 + singleton 29 [S-Claude — "subordinate to pause/finale/temporal-coherence work, not silently discarded"]; the per-call token counts already recorded in replay bytes and served client-side
**Complexity:** Small

The two cheap visible wins, landed deliberately LAST in the frontend chain (the
dependency edges are the point: narrative correctness shipped first). An event ticker
(kills, reports, meetings, ejections as they play) and cost/token chips (per-meeting and
cumulative LLM token counts — the data is already client-side). Both are additive chrome;
neither may regress the pause/finale flow, and both extend the existing test baseline.

**Files in scope:**
- frontend/src/components/EventTicker.tsx (new)
- frontend/src/components/CostChips.tsx (new)
- frontend/src/App.tsx; (mounting only)
- frontend/e2e/; (extend the journey's assertions)

**Files NOT in scope:**
- api/ (no new server data — client-side data only)
- frontend/src/hooks/usePlayback.ts (consumed, not edited)

**Definition of done:**
- [ ] Ticker and chips render from already-served data, respect unspoiled mode (no outcome leakage before the finale), and the extended journey still passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Ready-to-paste prompt:** `agent_prompts/task-19-17-ticker-cost.md`

---

## Wave 3 — the ML close and consolidation

### Task 19.18 — The tier map, the freeze-label sweep, and the reopening checklist
**Branch:** `phase-19-tier-map`
**Depends on:** 19.5
**Section refs:** audits/audit-phase-19-triage.md §7 items 19+21 [C] and the label halves of 29 [S-Claude] + 31 [L / source-specific] + locked decisions 2 and 3; §8 rows 21–22 (the reopen caveats; the component channels); audits/audit-phase-18-close.md §7 (the ledger long tail to freeze-label: items 5–8, 10–14) and §6.1 L10 (the Red-Queen context); eval/off_menu.py:12-34 (its own vacuity docstring); eval/deception_instruments.py (no non-test consumer — verified); eval/_suspicion_parse.py:9-13 + eval/meeting_quality.py:276-283 + eval/vote_correctness.py:566-571 (the rendered-prose scrapes to label frozen) [S-Claude — sites re-verified at HEAD]; training/surrogate/runner.py:105/:164/:383 with its live importers (training/composed_runner.py:122-124, training/bakeoff/harness.py) — the standalone-vs-dependency boundary 19.19 implements
**Complexity:** Medium

The ruling is made (locked decision 2); this task writes it down where the next agent
will trip over it. `training/README.md` (new): the component-by-component
keep/freeze/retire table with the measured basis per row — surrogate RANKING kept (46/60
top-1) vs the standalone decision arm retired (96/96 held-out SKIP; the FACTORY and the
class stay wherever the composed runner's verification fence and the harness consume
them — `training/composed_runner.py:266`, `training/bakeoff/harness.py:159` — and what
retires is the surrogate-ONLY runner exposure 19.19's consumer grep proves free; state
the boundary explicitly); the composed
runner frozen optional-diagnostic (0.8646 decision / 0.7917 exact, zero-LLM Goodhart
substrate caveat); the conviction model kept (0.9375 CONVERSION-LABEL accuracy — the
terminology ruling); ES core + champion acceptance kept; crew stack frozen
(clean negative); coevo/campaign machinery frozen; realpath retired (19.19). Record what
the program POSITIVELY learned (N1/N2 with their z-scores; the clean negatives) so the
tier map is findings, not just plumbing. The REOPENING CHECKLIST section implements
locked decision 3: both routes, the four mandatory pre-campaign checks, decide-at-
proposal. The freeze-label sweep: a standard FROZEN header (naming this map) on every
frozen module — coevo/, scenarios.py, anchor_study.py, the fidelity harnesses,
experiments/, off_menu, deception_instruments, the rendered-prose metric sites (labeled
"frozen — unreliable under prompt-shape change"), the watchability referee (frozen with
the champion opt-in path it serves), the bash recorders, and an engine note for the
byte-frozen RNG-draw apparatus — plus the phase-18 ledger long tail labeled in place
(recorder lock-race, `deadline_default` gaps, `composed_artifact_dir` escape,
campaign-plan overwrite, selector delegation convention, resume map refusal,
`WORK_DIR_OWNED_NAMES`), each label naming its close-audit anchor. Labels and docs only —
zero behavior bytes.

**Files in scope:**
- training/README.md (new)
- training/coevo/; (FROZEN headers only)
- training/scenarios.py; (same)
- training/anchor_study.py; (same)
- training/conviction/fidelity.py; (FROZEN header only)
- training/surrogate/fidelity.py; (FROZEN header only)
- training/composed_runner.py; (the frozen optional-diagnostic label)
- training/surrogate/runner.py; (the standalone-vs-dependency boundary label — 19.19 does the code)
- experiments/; (FROZEN headers)
- eval/off_menu.py; (label)
- eval/deception_instruments.py; (label)
- eval/_suspicion_parse.py; (the frozen-metric label)
- eval/meeting_quality.py; (the scrape-site label lines only)
- eval/vote_correctness.py; (same)
- eval/watchability.py; (the referee freeze label only — floors untouched)
- scripts/record_ml_corpus.sh; (freeze header + the ledger labels)
- scripts/refresh_samples.sh; (freeze header)
- engine/tick.py; (the byte-frozen RNG-apparatus note only)

**Files NOT in scope:**
- training/realpath.py (19.19 deletes it — do not label a file being retired)
- tests/ (marker/tiering implementation is 19.27's, driven by this map)
- training/reports/ (19.20's errata)

**Definition of done:**
- [ ] Verify-then-label for the S-Claude scrape sites: confirm each rendered-prose scrape at HEAD before labeling it (sites re-verified by the planning session; re-run the grep in-session).
- [ ] `training/README.md` names every disputed component with its ruling, measured basis, and consumer boundary; the reopening checklist carries both routes + all four checks + the decide-at-proposal rule; N1/N2 and the clean negatives are recorded as retained findings.
- [ ] Every frozen module opens with the standard header naming the map; every ledger long-tail item is labeled at its anchor; a repo grep for the header proves coverage matches the map's FREEZE column exactly.
- [ ] Zero behavior bytes: the diff is docs, comments, and docstrings only.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

One header format, stated in training/README.md and repeated verbatim:
`FROZEN (Phase 19 tier map, training/README.md): <one-line reason>. Bug fixes and
evidence readers only; no new search.` The tier table's rows should quote the exact
numbers from the committed reports (recompute nothing — cite `report-ballot-surrogate.md`
etc. by line). The reopening checklist's four checks come from triage §8 row 21 — quote
the mechanism, not just the name.

**Ready-to-paste prompt:** `agent_prompts/task-19-18-tier-map.md`

### Task 19.19 — The retirements + the dead-code sweep (consumer-verified)
**Branch:** `phase-19-retirements`
**Depends on:** 19.1, 19.4, 19.18 (19.1 is the llm/README.md serialization edge; 19.4 the tests/training/test_rewards.py edge)
**Section refs:** audits/audit-phase-19-triage.md §7 item 19 (retire set) + singleton 31 + claude §4 item 16 [S-Claude/S-Codex; consumer checks mandatory] + locked decision 2; training/realpath.py (4,470 LOC; the one-shot campaign ops surface) + tests/training/test_realpath.py (4,601 LOC; wall-clock asserts :288/:320-322/:3307-3309); training/surrogate/runner.py:383 (`load_surrogate_runner_factory`) — VERIFIED LIVE CONSUMERS: training/composed_runner.py:266 (the sha/staleness verification fence) and training/bakeoff/harness.py:159/:1763/:2072, with AST call-site pins at tests/training/test_bakeoff_harness.py:1742-1772 — so the factory and class STAY and only a surrogate-ONLY runner exposure proven consumer-free may retire; training/env.py:1037-1056 (`first_meeting` — production callers all pass `full_game`: crew/scorer.py:946, bakeoff/harness.py:722, coevo/rollout.py:214); scripts/run_tournament.py:102-105 (the stale crew-dir CLI advertisement); llm/cache.py (192 LOC; sole importer tests/llm/test_client.py:12); scripts/record_meeting_gate_probe.py (zero references); frontend/src/ui/SectionLabel.tsx (dead); the realpath docstring references in surviving files (training/coevo/hall_of_fame.py:279 `RealPathCandidate`, training/conviction/serving.py:301 `_TimeoutMeetingRunner` — rewritten with the deletion). NOTE 1: the five bespoke prompt-set dirs are NOT retired — all five are live (orchestrator/game.py:343-350; tests/agents/test_bespoke_prompt_sets.py loads every one); the source audits' deletion candidacy is REFUTED. NOTE 2: eval/determinism_test.py is NOT retired — the planning session verified pytest collects it (`*_test.py`) and README cites it as the engine-purity proof; the source audit's "exercised by nothing" is REFUTED.
**Complexity:** Integration

Implement the tier map's RETIRE column plus the verified dead-code list, one deletion at
a time, each with a grep-proven consumer check recorded in the PR. Retire:
`training/realpath.py` + its test file (the ranking-row schema doc and committed rankings
survive — the map records where); the surrogate-ONLY meeting-runner exposure — with the
verified boundary respected: `load_surrogate_runner_factory` and
`SurrogateMeetingRunner` STAY (the composed runner's verification fence at
`composed_runner.py:266` and the harness at `:159/:1763/:2072` consume them, AST-pinned)
— the retire candidate is any config/CLI arm that runs the surrogate ALONE as a meeting
runner, and if the consumer grep proves no such consumer-free exposure exists, the
outcome is a recorded no-op for this item, not a forced deletion. The realpath deletion
carries a verified consumer migration: `scripts/generate_campaign_tables.py:76` imports
`RealPathRerankRow` from the module (its test imports the script), so the ranking-row
schema RELOCATES to a small surviving module (`training/realpath_schema.py`, new) and
the script + test migrate onto it — the committed rankings' row contract survives the
campaign machinery. The `first_meeting` removal updates ALL its test constructors
(test_env.py:227-239, test_env_fast_path.py:141-154, test_rewards.py:115 — verified
list), and the cache deletion removes `llm/README.md`'s advertisement of the module
(:20-21) so 19.1's rewritten README does not point at a deleted API; the `first_meeting` episode
boundary (env + rollout plumbing; tests-only consumer); the stale crew-dir CLI
advertisement in run_tournament (the honest fail-loud behavior stays; the advertisement
of a stampless directory goes); `llm/cache.py` (+ its import in test_client);
`scripts/record_meeting_gate_probe.py`; `frontend/src/ui/SectionLabel.tsx`; and the
realpath docstring references left in surviving modules (hall_of_fame, conviction
serving — rewritten as historical notes, not left pointing at deleted APIs). The
bespoke prompt sets are NOT touched (live — see Section refs). Every deletion is
recoverable from git history; the PR lists each with its consumer-check output.

**Files in scope:**
- training/realpath.py; (deleted)
- tests/training/test_realpath.py; (deleted)
- training/realpath_schema.py (new — the relocated RealPathRerankRow row contract)
- scripts/generate_campaign_tables.py; (the import migration onto the relocated schema)
- tests/scripts/test_generate_campaign_tables.py; (same)
- tests/training/test_env.py; (the first_meeting constructors)
- tests/training/test_env_fast_path.py; (same)
- tests/training/test_rewards.py; (the :115 boundary constructor)
- llm/README.md; (the cache.py advertisement removed with the module)
- training/surrogate/runner.py; (the surrogate-only exposure, if the grep frees one)
- training/surrogate/; (ripple from the arm removal)
- training/bakeoff/harness.py; (only if a retired exposure ripples — record if touched)
- tests/training/test_bakeoff_harness.py; (the AST pins, only on ripple)
- tests/training/test_goodhart_probe.py; (only on ripple)
- tests/training/test_composed_runner.py; (only on ripple)
- tests/eval/test_balance_eval_meeting_runner.py; (only on ripple)
- training/env.py
- training/rollout.py
- tests/training/test_rollout.py
- tests/training/test_surrogate_runner.py
- tests/training/test_coevo_driver.py; (only if the realpath removal ripples — record if touched)
- scripts/run_tournament.py
- tests/scripts/test_run_tournament.py
- scripts/record_meeting_gate_probe.py; (deleted)
- llm/cache.py; (deleted)
- tests/llm/test_client.py; (the cache import removed)
- frontend/src/ui/SectionLabel.tsx; (deleted)
- training/coevo/hall_of_fame.py; (the :279 realpath docstring reference only)
- training/conviction/serving.py; (the :301 realpath docstring reference only)

**Files NOT in scope:**
- eval/determinism_test.py (NOT dead — see Section refs; it stays)
- agents/strategic/prompts/ (all sets live; nothing here moves)
- training/composed_runner.py + the conviction/compact-inference surfaces (KEEP column)
- frontend/src/api/ (dead client methods are backlog — they collide with 19.13/19.24)

**Definition of done:**
- [ ] Every deletion carries its consumer-check grep output in the PR; every skipped candidate (failed grep) is named with the blocking consumer.
- [ ] The surrogate boundary is proven: `load_surrogate_runner_factory`/`SurrogateMeetingRunner` and every verified consumer (composed runner fence, harness, the AST pins) are untouched and green; the surrogate-only exposure is either retired with its consumer grep quoted or recorded as no-consumer-free-exposure (a documented no-op), never force-deleted.
- [ ] `first_meeting` is gone from env/rollout with the three production call sites unchanged (`full_game` explicit) and every former boundary-constructing test (the verified list in the prose) updated and green.
- [ ] `RealPathRerankRow` lives in the surviving schema module; `generate_campaign_tables` and its test consume it there; the committed rankings and `measurement-stability.json` pins are untouched.
- [ ] The full gate is green after all deletions; the gate-runtime delta is quoted in the PR.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Order the deletions leaf-first (cache → gate probe → SectionLabel → first_meeting →
standalone arm → realpath) so each gate run isolates one removal. The realpath docstring
rewrites in hall_of_fame/serving land in the same commit as the module deletion so no
intermediate state points at a missing API; keep the historical facts, change the tense
and drop the dotted-path references.

**Integration risk:**

Deletions across five packages in one branch. The guards: leaf-first commit ordering with
the suite green at each step, the consumer-check discipline (nothing deleted on an
audit's say-so alone — the audits themselves got `eval/determinism_test.py` wrong, and
the first Codex review caught two more unlisted consumers, which is why the check is
mandatory), and the composed-runner dependency boundary pinned by its existing tests
before the standalone arm is removed.

**Public types introduced:**
- `training.realpath_schema.RealPathRerankRow`

**Ready-to-paste prompt:** `agent_prompts/task-19-19-retirements.md`

### Task 19.20 — ML report honesty: paired statistics + terminology errata
**Branch:** `phase-19-report-honesty`
**Depends on:** 19.4
**Section refs:** audits/audit-phase-19-triage.md §7 item 20 [S-Codex/S-Claude; §8 row 4 VERIFIED exactly] + C2 + C9; training/reports/report-finalist-eval.md (the paired-stats erratum target; :115-118 + :1066-1070 the external-slate citations); training/reports/results-finalist-eval.jsonl (the recomputation base — the triage's exact McNemar: ea4bc955 17/4 p=0.0072; bfd145cb 20/5 p=0.0041; 6d327dcb 15/9 p=0.3075 n.s.; 7f73929d 12/3@n=49 p=0.0352, fails Bonferroni α=0.0125); report-conviction-model.md:196 (0.9375 = conversion-label) + report-composed-runner.md:120-159 (0.8646/0.7917); report-impostor-campaign.md:415-465 (the screening instability + late-measured instrument noise); the 19.4 reward-claim erratum
**Complexity:** Medium

The reports are records — they get additive, dated errata, never rewrites. Land: (a) a
paired-statistics erratum in the finalist report — the exact McNemar table recomputed
from the committed per-game rows, stating plainly that the SHIPPED champion's paired edge
is statistically unresolved at n=50 and one arm fails the multiplicity correction; (b)
terminology errata wherever 0.9375 is called decision accuracy (the composed 0.8646 is
the decision figure); (c) the reward-shaping erratum (19.4's finding, with the
uncausal-as-measured statement about evidence starvation); (d) a screening-instability
note quoting the report's own late-discovery admission, framed as a stopping-rule
lesson; (e) a retained-findings note keeping N1/N2 and the clean negatives quotable. The
recomputation lives in `scripts/paired_stats.py` (exact binomial McNemar + Wilson) with
tests — 19.23 consumes it.

**Files in scope:**
- training/reports/report-finalist-eval.md; (additive dated erratum)
- training/reports/report-conviction-model.md; (same)
- training/reports/report-composed-runner.md; (same)
- training/reports/report-impostor-campaign.md; (same)
- training/reports/report-ballot-surrogate.md; (same, where the decision channel is described)
- scripts/paired_stats.py (new)
- tests/scripts/test_paired_stats.py (new)

**Files NOT in scope:**
- training/reports/results-finalist-eval.jsonl (the evidence rows are read, never edited)
- README.md (19.1 already carries the front-door terminology fix)

**Definition of done:**
- [ ] `scripts/paired_stats.py` recomputes the four McNemar cells from the committed JSONL exactly matching the triage's §8 row 4 values (pinned), plus Wilson intervals; the erratum quotes the recomputation command.
- [ ] Every erratum is additive and dated, never an in-place rewrite; each names what it corrects and quotes the original.
- [ ] The n.s. shipped-champion statement and the Bonferroni failure are stated in the finalist erratum in plain language.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Exact McNemar: two-sided binomial test on the discordant pair (min(b,c), b+c, p=0.5) —
pure stdlib via `math.comb`. Follow the repo's existing errata idiom (the crew report's
§12 errata are the exemplar: numbered, dated, each quoting the sentence it corrects).

**Ready-to-paste prompt:** `agent_prompts/task-19-20-report-honesty.md`

### Task 19.21 — The finalist raw slate: recover or label (owner)
**Branch:** `phase-19-raw-slate`
**Depends on:** 19.20, 19.22
**Section refs:** audits/audit-phase-19-triage.md §7 item 22 [C; VERIFIED §8 row 11]; training/reports/report-finalist-eval.md:115-118 ("the raw recordings … live outside the repo tree") + :1066-1070 (`~/ailibi-campaign-1826/scoring/…`); `git ls-files training/reports/_finalist_eval_raw` → empty; the 19.22 artifact classes (the store that would receive a recovered slate)
**Complexity:** Small

The 449-game slate behind the phase-18 adoption decision exists only on the owner's
machine, if at all. OWNER STEP (minutes): check whether `~/ailibi-campaign-1826/scoring/`
still exists. If YES: content-address it — per-file sha-256 manifest committed under
`training/reports/_finalist_eval_raw/` (manifest only; the bytes go to the 19.22
evidence store as class (c)) — and a dated erratum records the recovery and where the
bytes live. If NO: a dated erratum labels event-level finalist lineage NON-REPRODUCIBLE
(the flattened rows and every derived statistic remain reproducible from committed
cells — state exactly that boundary). Either way: do NOT re-record — the ~57-busy-hour
price is named and declined by charter.

**Files in scope:**
- training/reports/report-finalist-eval.md; (the availability erratum)
- training/reports/_finalist_eval_raw/MANIFEST.md (new, only on the recovery path)
- docs/artifacts.md; (the class-(c) registry row)

**Files NOT in scope:**
- replays/ (nothing is recorded)
- training/artifacts/ (19.22's surface)

**Definition of done:**
- [ ] One of the two outcomes is recorded with a dated erratum; on recovery, the manifest's shas cover every file and the evidence-store location is named; on loss, the reproducibility boundary is stated exactly.
- [ ] No re-recording occurred or is scheduled.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Ready-to-paste prompt:** `agent_prompts/task-19-21-raw-slate.md`

### Task 19.22 — Artifact classes + the coevo prune + the fast-clone path
**Branch:** `phase-19-artifact-classes`
**Depends on:** 19.13, 19.19
**Section refs:** audits/audit-phase-19-triage.md §7 item 23 [C; VERIFIED §8 row 11] + locked decision 5; the verified consumer set (planning session): exactly two test files read coevo bytes — tests/scripts/test_generate_campaign_tables.py (pins `measurement-stability.json` key-for-key) and tests/training/test_finalist_eval_pins.py (pins weights under `intermediates/`, `runnerups/`, run-01/run-c1/run-c2 generation dirs, and `realpath-crew/controls/…`); the tree: training/artifacts/coevo = ~109MB / 1,473 files, the realpath* subtrees ~104MB / 403 files; audits/audit-phase-18-close.md §6.3 C4 (the coevo namespace rules — the prune must not disturb `DEFAULT_RANKING_ROOTS` semantics)
**Complexity:** Medium

Implement locked decision 5. `docs/artifacts.md` defines the four artifact classes:
(a) small canonical fixtures in git; (b) manifests/hashes/summaries in git; (c) large
immutable evidence in the evidence branch; (d) disposable regenerated views. Then the
prune: FIRST enumerate every byte the two consumer test files pin (they are the
authority — the enumeration is the contract's first step and its output is committed
into the manifest); everything else under `training/artifacts/coevo/` moves to the
orphan evidence branch `evidence/phase-18-coevo` with a per-file sha-256 manifest
committed in-tree. Pinned bytes, `measurement-stability.json`, and the provenance
records stay in-tree. `replays/` does not move (locked decision 5). README and the
reading guide document `git clone --filter=blob:none` as the fast path, with the honest
caveat that full-history clones stay heavy absent a future deliberate rewrite.

**Files in scope:**
- training/artifacts/coevo/; (the prune — unpinned bytes removed from the working tree)
- docs/artifacts.md (new)
- README.md; (the fast-clone note)
- docs/reading-guide.md; (the same note where the guide describes cloning)
- scripts/fetch_evidence.sh (new — a small helper that checks out the evidence branch's bytes back into place)

**Files NOT in scope:**
- replays/ (stays whole — locked decision 5)
- tests/scripts/test_generate_campaign_tables.py + tests/training/test_finalist_eval_pins.py (their pinned bytes must remain in-tree so the tests are untouched)
- .git history (no rewrite)

**Definition of done:**
- [ ] The consumer enumeration is committed (the manifest marks each retained path with its pinning test); the full suite passes with NO test edits — the prune provably removed only unpinned bytes.
- [ ] The evidence branch exists, its bytes match the manifest sha-for-sha, and `scripts/fetch_evidence.sh` restores them; the working-tree size reduction is quoted in the PR.
- [ ] The fast-clone path is documented with the honest history caveat.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Build the retained-path allowlist by parsing the two test files' path literals plus
`training/artifacts/coevo/PATHS.md`/provenance conventions, then verify by running the
suite against a scratch tree with everything else removed BEFORE committing the prune.
The evidence branch is orphan (`git checkout --orphan evidence/phase-18-coevo`) carrying
only the moved bytes + a README naming the manifest commit.

**Ready-to-paste prompt:** `agent_prompts/task-19-22-artifact-classes.md`

### Task 19.23 — `verify-ml-evidence`: one command
**Branch:** `phase-19-verify-ml-evidence`
**Depends on:** 19.19, 19.20, 19.21, 19.22 (the availability report consumes the recorded raw-slate ruling)
**Section refs:** audits/audit-phase-19-triage.md §7 item 24 [S-Codex/S-Claude]; the Codex audit's executed-evidence table (each recomputation exists piecemeal today: sidecar/sha verification, corpus reconstruction, surrogate 0.7667/0.375, conviction 0.9375, composed 0.8646/0.7917); training/artifacts/coevo/provenance/harnesses/harness_run_c1.py.txt:11 (`_REPO = "/Users/danielkeinan/projects/AiLibi"` — the invocation folklore); scripts/paired_stats.py (19.20)
**Complexity:** Medium

One read-only command for the whole ML evidence story: `scripts/verify_ml_evidence.py`
runs sidecar/sha verification (296 sidecars), corpus reconstruction (delegating to the
existing verifiers), surrogate/conviction/composed recomputation against the committed
verdicts, the paired finalist statistics (via `scripts/paired_stats`), and an
artifact-availability report per `docs/artifacts.md` class (in-tree / evidence-branch /
repo-external / lost) — offline, $0, one exit code. Beside it, preserve the exact
campaign invocations: a committed appendix in `training/README.md` recording the
harness invocations currently living as hard-coded-path provenance folklore, rewritten
repo-relative.

**Files in scope:**
- scripts/verify_ml_evidence.py (new)
- tests/scripts/test_verify_ml_evidence.py (new)
- training/README.md; (the invocation appendix — dep-ordered behind 19.18/19.19)

**Files NOT in scope:**
- training/ (recomputation delegates to existing modules; nothing retrains)
- scripts/paired_stats.py (consumed, not edited)

**Definition of done:**
- [ ] The command runs green at HEAD in one invocation, listing every check with its measured value vs the committed verdict, and the availability class of every named evidence artifact (including the 19.21 outcome).
- [ ] It is read-only (no artifact writes outside a temp dir) and offline; a perturbed-input test proves it fails loud.
- [ ] The invocation appendix reproduces the recorded harness invocations repo-relative, citing the provenance files it replaces.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Wrap, don't reimplement: each leg calls the existing verifier/recomputation entry point
and compares against the committed verdict file. The runtime budget matters — the full
run should finish in minutes; put the corpus reconstruction behind a `--fast` flag that
samples if the full walk exceeds that budget, with the sampling disclosed in output.

**Ready-to-paste prompt:** `agent_prompts/task-19-23-verify-ml-evidence.md`

### Task 19.24 — Boundary hardening: the leak-scan library, `moved_players`, `intent.actor`, the API factory, DTO versions
**Branch:** `phase-19-boundary-hardening`
**Depends on:** 19.2, 19.11, 19.13, 19.14, 19.19
**Section refs:** audits/audit-phase-19-triage.md §7 item 26 [S-Claude/S-Codex; §8 row 16; the DTO cast and the CWD import re-verified at HEAD: frontend/src/api/client.ts:51 (`data as T`), api/main.py:24-27 (CWD-relative fallbacks) + :188 (module-scope `create_app()`)]; eval/leak_test.py:9 (module-level pytest import) + :719 (`scan_factory_packets`) + training/bakeoff/harness.py:107 (the champion-gate path importing a pytest module); observation/service.py:458-506 (`_moved_players_for_agent` — the one packet channel with ZERO leak-suite coverage, whose docstring narrates a prior gating bug); orchestrator/game.py:2024-2033 (no `intent.actor` validation); frontend/src/types/api.ts:25 (`viewModelVersion: string`)
**Complexity:** Integration

Five hardening moves on the project's trust boundaries. (a) Promote the packet scanners
to `eval/leak_scan.py` (a library with no pytest import); `eval/leak_test.py` becomes the
thin pytest wrapper; the harness imports the library — pytest leaves the champion-gate
import path. Every existing planted-leak self-test must still bite (the gates prove they
can fail — that property is the crown jewel; this move is import-path only). (b) Add
`moved_players` witness-gating coverage to the leak suite: the Hypothesis property sweep
and a planted-leak self-test proving the new scanner detects a violation. (c) One line at
the orchestrator boundary: `intent.actor == player_id` validation, fail-loud, with a
test — the seam the architecture explicitly anticipates learned movers on. (d) A
CWD-independent API factory: the data root resolves from an injected/config value or the
repo anchor, never the working directory; import-from-elsewhere is tested. (e) Runtime
DTO version rejection: the generator emits a literal version constant; the client rejects
a mismatched `viewModelVersion` loudly (and the static demo bundle bakes the matching
constant, so 19.13's artifact keeps working).

**Files in scope:**
- eval/leak_scan.py (new)
- eval/leak_test.py
- training/bakeoff/harness.py; (the import swap at :107 only)
- tests/observation/test_leak_property.py
- tests/observation/
- orchestrator/game.py; (the one-line validation + test hook)
- tests/orchestrator/
- api/main.py
- tests/api/
- scripts/gen_frontend_types.py; (the version-constant emission)
- frontend/src/types/api.ts; (regenerated)
- frontend/src/api/client.ts

**Files NOT in scope:**
- observation/service.py (covered, not changed)
- eval/leak_test.py's scanner SEMANTICS (the move is mechanical; scanner behavior changes are out)
- api/replay_loader.py (19.11 was the last writer; the loader does not move here)

**Definition of done:**
- [ ] Verify-then-fix for the DTO-cast claim: re-confirm the unvalidated cast at HEAD before adding rejection (re-verified by the planning session; re-run in-session).
- [ ] `import eval.leak_scan` succeeds without pytest installed in the environment probe (test-pinned); the harness path imports no pytest; every pre-existing planted-leak self-test still fails when its leak is planted.
- [ ] The `moved_players` property sweep runs in the leak suite with its planted-leak proof; the leak-suite gap named by the audits is closed.
- [ ] A forged `intent.actor` fails loud at the boundary (test); the API imports and serves from a foreign CWD (test); a version-mismatched payload is rejected loudly client-side and the demo bundle still passes its 19.13 test.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The scanner move: `leak_scan.py` takes the scanner functions and constants verbatim
(`_walk_json`, the forbidden-field/value scanners, `scan_factory_packets`);
`leak_test.py` re-exports for its tests and keeps every test body. The property sweep
already imports production scanners (tests/observation/test_leak_property.py:59-66) —
point those imports at the library. For `moved_players`: the docstring at
`observation/service.py:464-489` narrates the exact bug class to scan for (post-advance
visibility gating); the planted leak plants that bug.

**Integration risk:**

Touching the leak suite and the champion-gate import path in one PR. The invariant that
cannot regress: every scanner that could bite before still bites (run the planted-leak
matrix before and after the move and diff the outcomes — identical or the PR stops).
The DTO version rejection risks breaking the demo bundle and dev flows on skew — the
generated constant keeps client and server in lockstep through the same codegen.

**Public types introduced:**
- `eval.leak_scan.scan_factory_packets`

**Ready-to-paste prompt:** `agent_prompts/task-19-24-boundary-hardening.md`

### Task 19.25 — The parameterized replay walker + the eval consumer migration
**Branch:** `phase-19-replay-walker`
**Depends on:** 19.24
**Section refs:** audits/audit-phase-19-triage.md §7 item 25 [C; count VERIFIED §8 row 15 — eight modules, nine loop bodies] + C3 + close §7 items 1–2 (the disclosed duplication); the loop bodies re-verified at HEAD: eval/watchability.py:1229-1231/1290, eval/validity.py:402-404/453, eval/funnel.py:365/471 + :1217/1324, eval/kill_craft.py:474-519, eval/win_condition_selfcheck.py:191-225, eval/balance_eval.py:760-796, eval/leak_test.py:593-600; eval/deception_instruments.py:166 (the one module that already imports a shared walk — the consumption exemplar); eval/off_menu.py EXCLUDED (frozen, 19.18)
**Complexity:** Integration

"Reconstructs cleanly" currently denotes eight subtly different predicates — each copy of
the walk enforces a different subset of the integrity checks, which is a semantic-drift
hazard, not just duplication. Build `eval/replay_walk.py`: one typed, fail-loud walker
(re-seed → `advance_tick` over recorded actions → `apply_meeting_result`) enforcing the
UNION of the integrity checks the copies enforce (state-hash verification per tick,
doubled-tick/doubled-game-over detection, meeting-result application rules), with
pluggable per-tick and per-meeting fact collectors. Migrate the eight live call sites
one consumer at a time with BYTE-PARITY: no committed pin, report cell, or metric value
may change — parity is the deliverable. `off_menu.py` stays frozen and unmigrated
(labeled by 19.18); the API and training walks are backlog by the cut line.

**Files in scope:**
- eval/replay_walk.py (new)
- eval/watchability.py
- eval/validity.py
- eval/funnel.py
- eval/kill_craft.py
- eval/win_condition_selfcheck.py
- eval/balance_eval.py
- eval/leak_test.py
- tests/eval/test_replay_walk.py (new)
- tests/eval/test_watchability.py
- tests/eval/test_validity.py
- tests/eval/test_funnel.py
- tests/eval/test_kill_craft.py
- tests/eval/test_win_condition_selfcheck.py
- tests/eval/test_balance_eval.py

**Files NOT in scope:**
- eval/off_menu.py (frozen — not migrated)
- api/replay_loader.py + training/env.py (backlog per the cut line)
- eval/deception_instruments.py (already consumes a shared walk; not churned)

**Definition of done:**
- [ ] The walker's docstring tables the union of integrity checks with, per retired copy, which checks it had and which it lacked (the drift record).
- [ ] All eight call sites consume the walker; a repo grep proves no independent `advance_tick` reconstruction loop remains in the migrated modules.
- [ ] BYTE-PARITY: every committed pin and regenerated-report byte is unchanged across the migration (the four derived reports regenerate identical; the diff proves it); if any committed byte fails the union of checks, the migration STOPS and records the finding — the union is never weakened silently.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

One consumer per commit, suite green between commits, `funnel.py`'s two walks last (they
are the memory-augmented ones — the walker's collector seam must serve the
reconstructed-`TacticalAgent` pattern before they migrate). The walker API shape that
works: a config of enabled collectors + a generator of typed per-tick events, so callers
fold rather than subclass.

**Integration risk:**

Eight load-bearing eval modules on one branch. The parity discipline is the guard
(committed pins are the oracle at every step), plus the stop-rule: any committed byte
that fails the union of integrity checks is a recorded finding and a halt, never a
silently-relaxed check. If the branch runs long, land the walker + the first three
consumers and split the rest into a follow-up on the same contract (coordination notes
the split) rather than letting the branch drift.

**Public types introduced:**
- `eval.replay_walk.walk_replay`
- `eval.replay_walk.ReplayWalkConfig`

**Ready-to-paste prompt:** `agent_prompts/task-19-25-replay-walker.md`

### Task 19.26 — Vote-tally parity (consolidation optional)
**Branch:** `phase-19-vote-tally-parity`
**Depends on:** 19.15
**Section refs:** audits/audit-phase-19-triage.md §7 item 27 [S-Claude; verified in the original triage]; meetings/voting.py:38-48 ("the manager retains its own private copies … future work may consolidate the manager onto this canonical home"); meetings/manager.py:1956-2004 (`_tally` — the implementation the live game applies); the equivalence protected today by prose only
**Complexity:** Medium

The ejection rule the game applies and the one eval re-checks live in two
implementations whose equivalence is protected by a comment. Parity first: a test family
running BOTH implementations over every committed meeting's recorded ballots (all four
sets) plus synthetic edge fixtures (ties, coerced ballots, dead voters, SKIP thresholds,
the guard markers) asserting identical outcomes. THEN, only if parity is total and the
migration is mechanical, consolidate the manager onto `voting.tally_ballots`; otherwise
land the parity suite plus a dated note naming the blocking difference, and the
consolidation goes to the backlog — the fallback is pre-authorized by the triage.

**Files in scope:**
- meetings/manager.py
- meetings/voting.py
- tests/meetings/test_vote_tally_parity.py (new)

**Files NOT in scope:**
- replays/ (evidence, frozen)
- eval/ (consumers of voting.py are untouched)

**Definition of done:**
- [ ] The parity suite covers every committed meeting (count pinned) + the synthetic edges, green on both implementations at the pre-consolidation commit.
- [ ] Consolidation is either DONE (manager delegates; replay verification + byte-golden green; the private copy gone — and the suite pivots to pinning the delegation plus the recorded outcomes, since only one implementation remains) or DEFERRED with the blocking difference named in a dated note in voting.py (the two-implementation suite then stays as the permanent guard) — no third state.
- [ ] `bash scripts/verify_samples.sh` green (reconstruction semantics unchanged).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Drive the committed-meeting sweep from the recorded ballot sets (the meeting records
carry them) rather than re-running meetings; the interesting edges are the ones
production has actually exercised — coerced ballots and redirects are greppable via
their markers. Consolidation, if taken, should leave `_tally` as a thin delegation, not
delete the call site.

**Ready-to-paste prompt:** `agent_prompts/task-19-26-vote-tally-parity.md`

### Task 19.27 — Test-suite structure: markers, the shared fixture, pins to goldens
**Branch:** `phase-19-test-structure`
**Depends on:** 19.3, 19.4, 19.7, 19.12, 19.18, 19.19, 19.22, 19.25
**Section refs:** audits/audit-phase-19-triage.md §7 items 19 (the tiering half) + 28 [S-Claude, Codex-compatible; the ~5× re-walk figure is source-specific — verify-then-fix]; the verified structure facts: NO pytest markers registered today (pyproject.toml:45-46 has only `pythonpath`), tests/meetings/test_manager.py = 7,531 LOC imported as a library by four sibling modules (test_citation_gate.py:61, test_vouch_grounding.py:80, test_elicitation_fixtures.py:57, test_ballot_observation_citation.py:54); tests/scripts/test_champion_flip_ruling.py (830 LOC, ~136 exact-literal pin lines — the audit's "~580" overstated; convert the pin DICTS, keep the logic) + tests/training/test_finalist_eval_pins.py (2,089 LOC, ~173 literal pin lines)
**Complexity:** Medium

The gate's structure work, driven by the tier map. Register markers (`slow`, `campaign`,
`perf`) and put the campaign-only test families behind opt-in per 19.18's map — the
always-on set is named and stays: champion acceptance, ES, determinism, artifact-digest,
train/serve parity, the leak property sweep, the prompt byte-golden, the
prompt-regression close gate. Add a session-scoped committed-replay walk fixture
(verify-then-fix: measure how often the 9p2i set is re-walked per suite run FIRST, quote
before/after). Extract the shared helpers out of `test_manager.py` into a non-test
helper module so four modules stop importing a 7.5k-line test file as a library. Convert
the exact-scalar transcription pin blocks in the two named files to generated goldens
(committed JSON regenerated by a script), keeping derived-invariant assertions as code.
Quote the default-gate runtime before/after in the PR.

**Files in scope:**
- pyproject.toml; (the markers registration)
- tests/conftest.py
- tests/meetings/test_manager.py
- tests/meetings/_manager_helpers.py (new)
- tests/meetings/test_citation_gate.py
- tests/meetings/test_vouch_grounding.py
- tests/meetings/test_elicitation_fixtures.py
- tests/meetings/test_ballot_observation_citation.py
- tests/scripts/test_champion_flip_ruling.py
- tests/training/test_finalist_eval_pins.py
- tests/training/; (marker application on the campaign families named by the tier map)
- scripts/regen_test_goldens.py (new)

**Files NOT in scope:**
- scripts/check.sh + .github/workflows/ci.yml (the default gate's INVOCATION is unchanged — markers make the campaign tier opt-in via registration defaults, not CI edits; if an invocation change becomes necessary, coordinate, don't fold)
- tests/meetings/test_prompt_byte_golden.py (always-on; consumes the fixture only if the migration is zero-risk — otherwise untouched)

**Definition of done:**
- [ ] Verify-then-fix: the re-walk count is measured before the fixture lands and the delta quoted after.
- [ ] Markers are registered; `uv run pytest` (default) runs the always-on set green with the campaign families opt-in (`-m campaign` runs them green too — nothing is orphaned); the always-on list in the contract is asserted by a meta-test.
- [ ] No test module imports another test module as a library (grep-pinned); the goldens regenerate byte-identically via the script; every conversion preserves the assertion's meaning (the derived-invariant checks remain code).
- [ ] The default-gate runtime delta is quoted.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Marker defaults via `addopts = -m "not campaign"` keeps CI invocations untouched — but
then `-m campaign` must be exercised in CI weekly or on the training paths' PRs; note
the chosen posture in conftest. The helper extraction is mechanical: move, re-export
from the old location for one release of grace, then drop the re-export in the same PR
if all four importers migrate cleanly.

**Ready-to-paste prompt:** `agent_prompts/task-19-27-test-structure.md`

### Task 19.28 — The phase close (owner)
**Branch:** `phase-19-close`
**Depends on:** 19.8, 19.17, 19.23, 19.26, 19.27
**Section refs:** [L] the phase-18 close conventions (audits/audit-phase-18-close.md — the exemplar); locked decision 6 (the post-19 menu reads the 19.14 metrics); tasks/post-phase-14-plan.md (the roadmap tick this close owns)
**Complexity:** Medium

The close re-verifies and routes. `audits/audit-phase-19-close.md`: re-run the full gate,
`verify_samples`, and `verify_ml_evidence` at close HEAD; re-verify each contract's
headline DoD with fresh commands (merge equals done, but the close re-runs — the
phase-18 precedent found real defects in otherwise-green merges); the phase ledger
(every deviation recorded as a finding, never silently); the before/after story told in
generated numbers (gate runtime, clone weight, the truth-check counts). Then the routed
decision: the post-19 menu — the evidence-honesty substrate phase vs the presentation
phase — put to the owner with the 19.14 proof-vs-inference cells as the evidence (locked
decision 6), a costed recommendation, and no unilateral ruling. STATUS banner flips in
this file; the roadmap gets its tick.

**Files in scope:**
- audits/audit-phase-19-close.md (new)
- tasks/phase-19.md; (the STATUS banner + any close-recorded surgery notes)
- tasks/post-phase-14-plan.md; (the roadmap tick)

**Files NOT in scope:**
- everything else (the close verifies; it does not fix — late findings route to the next phase's inputs)

**Definition of done:**
- [ ] The gate, verify_samples, and verify-ml-evidence are green at close HEAD with outputs quoted; every contract is verified-or-deviation-recorded in the ledger.
- [ ] The post-19 decision menu is framed from the committed 19.14 cells with a recommendation; the owner's ruling is recorded in the close audit.
- [ ] The STATUS banner and roadmap reflect the close.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Follow the phase-18 close's section shape at a fraction of its length — this phase
recorded nothing, so the close is verification + routing, not evidence assembly. The
decision menu's framing rule: outcomes, risks, and costs per option, recommendation
first, the 19.14 numbers doing the arguing.

**Ready-to-paste prompt:** `agent_prompts/task-19-28-phase-close.md`
