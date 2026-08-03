# Phase-19 planning — the review-and-refresh plan (planning session, 2026-08-03)

Produced by the Phase-19 planning/coordination session against `main` @ `67166b3`. The
research is already done — `audits/audit-phase-19-triage.md` (the spine), the two input
audits, and `audits/audit-phase-18-close.md` §6–§7 — so this dossier is deliberately SHORT:
it records the phase shape, the owner's decision-menu answers, and every divergence from
the triage's §7 work-list, with reasons. The dispatchable contracts live in
`tasks/phase-19.md`; the owner's merge of that document ratifies this plan (the 15.18
convention).

---

## 1. Inputs and baseline

- **Reading list consumed in order:** triage (§7 work-list + §8 claim-verification table),
  `audit-phase-19-input-claude.md`, `audit-phase-19-input-codex.md`,
  `audit-phase-18-close.md` §6–§7, `tasks/phase-18.md` (contract conventions),
  `tasks/post-phase-14-plan.md` (the charter).
- **Anchor validity:** `git diff 8873e99..HEAD` touches only the two committed audit files —
  the code tree at HEAD is byte-identical to the commit every triage VERIFIED ruling was
  checked against, so triage-verified anchors are current. Anchors the triage did **not**
  independently re-run were re-verified at HEAD by this session's fan-out pass before being
  pinned into any contract (§6); contracts inheriting still-unexecuted source-specific
  claims carry verify-then-fix as their first DoD step, per the triage §8 row 20 rule.
- **Gate baseline re-confirmed this session:** `bash scripts/check.sh` → pytest
  **4531 passed / 20 skipped / 3 xfailed** (identical to both audits' Linux baseline). The
  frontend `tsc` TS2688 `vite/client` failure in this cloud container is the known
  environment artifact (the Python line is the gate); the same frontend leg passes on the
  audited hosts and in CI.
- **Ratified rulings inherited, not relitigated:** the review-and-refresh charter, the
  triage §7 NOT-list, prerequisite 0 (small scoped contracts, hard cut line, no mega-PR),
  the evidence-label discipline, and the ML freeze (Wave 3 is closure, zero new
  recordings).

## 2. The decision menu (owner, 2026-08-03 — these are now locked decisions)

Six questions were put to the owner with costed recommendations; all six answers ratify the
recommended option. NUMBERING NOTE: `tasks/phase-19.md`'s locked-decision register is the
authoritative numbering and prepends the charter/NOT-list as decision 1, so menu question
N = register decision N+1 (menu Q5, the substrate deferral, is register decision 6; menu
Q6, the cut line, is register decision 7). Citations below and in the phase doc use the
REGISTER numbers.

1. **ML component tier map: EVIDENCE-FIRST HYBRID.** KEEP what committed evidence and
   always-on gates still execute (compact learned inference + parity, corpus
   verifier/splits, the conviction model, the surrogate **ranking** channel, the ES core +
   champion acceptance). FREEZE with labels: the composed runner (optional-diagnostic), the
   crew stack, co-evolution/campaign machinery (campaign-only test families behind opt-in
   markers). RETIRE after consumer verification: `training/realpath.py`, the standalone
   surrogate decision path (96/96 held-out SKIP), the unused `first_meeting` boundary, and
   new-search machinery. Retired code stays in git history.
2. **ML re-open fork: RECORD THE FORK, DECIDE LATER.** The reopening checklist documents
   both routes (floor re-pricing vs real-path conviction signal) plus the four mandatory
   pre-campaign checks (interval-aware floors, weak-flag Goodhart probe, run-variance
   treatment, screening replication), and states the owner picks a route only when a
   concrete re-open proposal exists. The phase stays frozen either way.
3. **License and public posture: MIT + minimal CONTRIBUTING/SECURITY.** MIT license; a
   short CONTRIBUTING stating the solo agent-built workflow; SECURITY.md documenting the
   local-only trust boundary of the unauthenticated replay API.
4. **Artifact retention: PRUNE COEVO ONLY.** `replays/samples/` and `replays/ml_corpus`
   stay in-tree (everything live gates recompute from remains self-contained). The ~109MB
   of closed-campaign co-evolution intermediates move to an evidence branch/release asset
   with manifests + hashes + the pinned stability summary staying in-tree. Partial clone
   (`--filter=blob:none`) is documented as the fast path. Stated honestly: full-history
   clones stay heavy until a future deliberate rewrite, which this phase does not do.
5. **Evidence-honesty substrate fixes: DECIDE AFTER THE METRICS.** Phase 19 ships the
   proof-vs-inference metrics, injustice fixtures, and per-mechanism labels; whether the
   substrate behavior fixes become the first post-19 phase is decided at the phase close,
   reading those metrics. Nothing behavioral changes in-phase (the NOT-list stands).
6. **Cut line: THE BALANCED PHASE.** All of Wave 1 (truth/gate); all of Wave 2 (spectator
   coherence + metrics + demo) with the ticker/cost chips as a dependency-gated tail;
   Wave 3 = ML close docs + tier map + retirements + artifact prune + one parameterized
   replay walker migrating the live eval consumers + vote-tally parity + test-suite
   structure + boundary hardening + freeze labels. OUT to the backlog (§5): monolith
   decompositions, API/training walker migration, typed ballot/suspicion telemetry.

## 3. The phase shape

**28 contracts, three waves, no recordings.** Every task is $0/offline; the only
operator-machine work is 19.21 (checking whether the finalist raw slate still exists on the
owner's machine) and the owner-ratified close. No baseline is recorded: the ladder tip
remains baseline 6, and every derived artifact this phase regenerates (eval reports, rubric
scores, generated goldens) is recomputed from committed bytes — replay bytes never move.

- **Wave 1 — truth and the gate (19.1–19.8):** the front-door truth sweep + generated-fact
  checks; the in-code truth sweep + graduation-sweep convention; ES portability; the reward
  claim; metric/data-display truth (conversion family + dashboard); the one-line defects;
  public/build hygiene + MIT; corpus truth disclosures.
- **Wave 2 — the spectator tells one coherent game (19.9–19.17):** curated 9p2i default +
  featured path; playback coherence (meeting pause, unspoiled mode, finale card, frame-time
  labels); the evidence taxonomy in DTO + UI; the frontend test baseline (Vitest + ESLint +
  one Playwright journey); README proof + the static demo artifact; the deduction metrics
  (proof-vs-inference); guard-rationale redaction (dormant); the outsider reading guide;
  the gated ticker/cost tail.
- **Wave 3 — ML close and consolidation (19.18–19.27):** tier map + freeze-label sweep +
  reopening checklist; retirements + dead-code sweep; ML report honesty (paired statistics,
  terminology errata); the raw-slate recovery/label (owner); artifact classes + the coevo
  prune; `verify-ml-evidence`; boundary hardening; the parameterized replay walker; vote-
  tally parity; test-suite structure. **19.28 closes the phase** with the close audit and
  the post-19 decision menu (substrate fixes vs presentation), read against the 19.14
  metrics per locked decision 6 (menu question 5).

**Model assignments** follow the phase-18 standing rule — Opus for loud-failure work
(mechanical fixes, re-pins, deletions with consumer greps, test scaffolding, generated
docs), Fable for silent-failure work (metric semantics, evidence taxonomy, docstring truth,
tier-map wording, statistical honesty, the spectator narrative). The per-task split is in
the phase-doc preamble.

**Collision discipline** (the phase doc's block is authoritative): the truth-sweep,
dashboard, walker, and frontend tasks share files and are serialized by dependency edges —
notably README.md (19.1 → 19.16 → 19.13 → 19.22), `api/replay_loader.py` (19.9 → 19.10 →
19.11), `api/schemas.py` (19.5 → 19.10 → 19.11 → 19.14) and `frontend/src/types/api.ts`
(19.5 → 19.10 → 19.11 → 19.14 → 19.24 — the report cells and the DTO-version constant
ride the same generated surface), `meetings/manager.py` (19.2 → 19.15 → 19.26),
`eval/leak_test.py` (19.24 → 19.25), `pyproject.toml` (19.6 → 19.7 → 19.27), and the
regenerated eval reports (19.5 → 19.14).

## 4. Divergences from the triage §7 (recorded, with reasons)

1. **Item 12's "prompts" surface is excluded from the in-phase evidence-taxonomy work
   (19.11).** Prompt-template edits are substrate behavior: they break the prompt
   byte-golden against committed bytes and change model behavior on any future recording —
   exactly what the NOT-list forbids beyond instrumentation/labels. The prompt-side flag
   naming ("VERIFIED evidence") routes to the post-19 decision (locked decision 6) with the
   other three mechanisms; Phase 19 fixes the UI/DTO/metric surfaces only and preserves the
   four mechanisms as separate fixtures/labels per triage item 20.
2. **Item 29 (typed telemetry) resolves as freeze-labels, not code** — ratified by the cut
   line: nothing records again this phase, so the rendered-prose metrics are labeled frozen
   and unreliable under prompt-shape change (folded into 19.18). The typed-telemetry
   migration is backlogged against any future recording decision.
3. **Item 30 (monolith extraction) routes to the backlog whole** — both audits deprioritize
   it below truth/demo work and it is only safe after the walker/tally/test seams exist.
4. **Item 25 (walker consolidation) is scoped to the live eval consumers** (nine loop
   bodies less the frozen `off_menu.py`); the API and training reconstruction walks are
   backlogged per the cut line. `off_menu.py` gets a freeze label instead of a migration.
5. **Merges relative to §7's item boundaries:** items 5+6 → 19.5 (one metric+display truth
   contract — same files, one review); items 19+21+the label halves of 29/31 → 19.18 (one
   tier-map/labels/checklist contract — `training/README.md` hosts both the tier table and
   the reopening checklist); item 26 lands as 19.24 (boundary hardening); item 8 absorbs
   the license ruling. Item 4's report erratum rides 19.20 (not 19.4) to avoid a
   `training/reports/` collision — 19.4 confines itself to code + tests.
6. **DESIGN.md needs a chartered exception:** dispatched agents are barred from DESIGN.md
   by the prompt generator (a hard constraint line in every prompt;
   `tasks/post-phase-14-plan.md` §5 records the bar). 19.1 therefore scope-gates that
   generator rule ("Do not modify DESIGN.md **unless this task explicitly lists it in
   scope**" — mirroring the existing tasks/phase-*.md rule) so the demotion/banner work is
   contractable; existing prompts stay byte-identical because no other task lists
   DESIGN.md. The owner's merge of the phase doc ratifies this control-surface change.
7. **A phase-close contract (19.28) is added** though §7 lists none — phase conventions
   (the close audit, the STATUS banner, the roadmap tick, the routed decision menu) require
   it.
8. **Contract count is 28 against the menu's "~24–26"** — the close contract and the
   owner-kept ticker tail account for the delta. Recorded, not silent.
9. **The rubric re-score (item 10) is confirmed $0** — this session verified the scorer is
   `experiments/lab/rubric_score.py`, offline over committed bytes with no LLM/provider
   imports — so 19.9 re-scores as an ordinary contract step to clear the staleness banner.
   The Highlights ordering is still hand-curated and the scalar labeled narrowly (triage
   singleton 29): a fresh score does not validate human-interest ordering.

## 5. The backlog (routed out, not dropped)

Tracked here so nothing lives only in a PR body; each re-enters only through a future
owner-chartered phase:

- Monolith decompositions: `orchestrator/game.py`, `api/replay_loader.py`,
  `meetings/manager.py`, `meetings/transcript.py` (characterization tests first; after the
  Phase-19 seams). This line also carries the loader's private
  `orchestrator.replay._state_hash` import (`api/replay_loader.py:162`) — the boundary
  cleanup belongs to the decomposition, explicitly deferred, not silently dropped.
- Dead frontend api-client methods (singleton-31 inventory): they collide with
  19.13/19.24's `client.ts` work this phase, so their deletion is deferred to this
  backlog rather than folded in.
- The five remaining cross-test library imports outside 19.27's narrowed scope
  (`tests/agents/test_absence_prior.py:958`, `tests/agents/test_episodic_ids.py:480`,
  and `tests/agents/test_beliefs_hard_evidence_gate.py:751` → test_prompt_byte_golden;
  `tests/llm/test_real_provider.py:56` → test_client;
  `tests/observation/test_leak_property.py:68` → test_tick_properties) — the same
  helper-extraction treatment, next structure pass.
- Replay-walk migration of the API (`api/replay_loader.py`) and training (`training/env.py`)
  reconstruction paths onto the 19.25 walker.
- Typed per-ballot suspicion/ballot telemetry (replaces the frozen rendered-prose scrapes if
  any recording ever happens again).
- The evidence-honesty substrate behavior fixes (sighting provenance, content-vs-memory
  validation, interval/weighting, prompt-side flag naming) — the pre-chartered candidate
  for the first post-19 phase, decided at the 19.28 close per locked decision 6.
- Equal-response-shape prototype behind a measured gate (Codex singleton; behavior change,
  same post-19 route).
- GuidedTour focus-trap dedup + the duplicated initial list fetch; SWC-plugin swap; npm
  advisory triage (ordinary dependency hygiene).
- Engine frozen-debt documentation beyond labels (unused RNG draw apparatus, dead schema
  fields — byte-frozen; labeled in 19.18, never churned).
- The Bash recorder port to Python (explicitly frozen; freeze-labeled in 19.18).
- A hosted (non-static) demo with a real trust boundary; heterogeneous-model lobbies; the
  human seat (charter-excluded).

## 6. Verification record (this session)

- `bash scripts/check.sh` re-run at HEAD: green on the Python gate (4531/20/3; §1).
- Anchor re-verification: a six-agent fan-out re-checked at HEAD every file:line anchor
  pinned in `tasks/phase-19.md` that the triage had not itself re-executed (the meetings/
  agents cluster, eval cluster, frontend cluster, api/scripts cluster, training cluster,
  tests/observation cluster — 60+ claims). Anchors that drifted from the source audits'
  citations were corrected before pinning; claims that could not be re-confirmed kept
  their source tag and a verify-then-fix first DoD step in the owning contract.
- **Source-audit claims corrected by this session's verification** (folded into the
  contracts; recorded here so the corrections are not lost):
  1. `eval/determinism_test.py` is NOT dead — bare pytest collects it (the `*_test.py`
     pattern) and README cites it as the engine-purity proof. The Claude audit's
     "exercised by nothing" is REFUTED; the module is excluded from 19.19's retirements,
     and the mandatory consumer-check discipline cites this as its motivating case.
  2. The surrogate "standalone decision path" has live consumers: the FACTORY itself is
     load-bearing — `training/composed_runner.py:266` calls
     `load_surrogate_runner_factory` as its sha/staleness verification fence, and
     `training/bakeoff/harness.py` imports it at :159 and calls it at :1763/:2072 with
     AST call-site pins in `tests/training/test_bakeoff_harness.py:1742-1772`. The
     retirement (19.19) therefore keeps the factory AND the class; only a surrogate-only
     runner exposure proven consumer-free may retire, and a no-consumer-free-exposure
     outcome is a recorded no-op. 19.18's tier map states the boundary.
  3. `tests/scripts/test_champion_flip_ruling.py` carries ~136 exact-literal pin lines,
     not "~580 of 831" — the audit counted the interleaved logic. 19.27's pin-to-golden
     conversion is scoped to the pin dicts accordingly.
  4. The rubric scorer (`experiments/lab/rubric_score.py`) is offline/$0 (no LLM
     imports), so 19.9's re-score is an ordinary contract step.
  5. Minor anchor drifts corrected in place (the replay store lives at
     `frontend/src/store/`, not `src/state/`; the harness provenance `/Users` path is at
     line 11, not 12).
  6. **The triage C6 mechanism is refuted** (surfaced by the first Codex review round,
     verified in-session): the conversion partition ALREADY imports
     `UNCITED_ZERO_FLAG_EJECT_MARKER` (`eval/meeting_quality.py:179`) and censuses the
     class separately — the committed 9p2i report carries
     `citation_coerced_skip_ballots = 1` beside `threshold_inversions = 87`, so the 87
     are not unrecognized citation-gated SKIPs. The three-surface doctrine disagreement
     (eval prose vs dashboard badge vs the 13.13 intent) stands and is still 19.5's
     work, but the contract is rewritten recount-first: measure the 87's cause mix from
     committed bytes, then re-doctrine to what the recount supports.
- **Codex round 11 (4 findings)** — all reproduced and absorbed: the recovered
  raw-slate bytes get a real handoff (the owner step pushes a manifest-verified
  `evidence/raw-slate-staging` ref; the artifact task folds and retires it — hashes
  alone cannot materialize files on a fresh checkout); the rubric scorer's two tracked
  lab outputs join 19.9 (its `main()` rewrites both alongside the served copy); the
  duplicate-id diagnostic prints `path:line` for BOTH headers (the parser now records
  header lines); and the dossier's frontier command is invocable as written
  (`uv run python …` — the script is mode 100644).
- **Codex round 10 (2 findings, over the owner-round absorption)** — both reproduced
  and absorbed: the walker's "shared core" still over-mandated (the leak-scan walk at
  `leak_test.py:593-600` performs NEITHER state-hash verification nor duplicate-row
  detection, so even those become profile OPTIONS — the core is reconstruction
  mechanics only), and the new dependency validator gains a duplicate-task-id check
  reporting both source locations (id-keyed state downstream would silently collapse
  duplicates), with a guard test.
- **The owner's own review round (8 findings + 6 improvements, after Codex converged
  clean at round 9)** was verified claim-by-claim — all eight reproduced, several in a
  class the automated rounds never reached (semantic defeat rather than scope ripple) —
  and absorbed: (F1) the rubric staleness KEY is broken for mixed-provenance sets
  (three recording SHAs → `manifest_sha=None` → unconditionally stale), so 19.9 now
  fixes the key (set fingerprint or an honest mixed-provenance notice) with
  `rubric_score.py` in scope; (F2) artifact preservation became one transaction —
  19.21's availability ruling precedes 19.22's single immutable, pushed, SHA-pinned
  evidence commit, `fetch_evidence.sh` fetches by pin, and 19.23 gains a `--complete`
  mode the 19.28 close must run after fetching; (F3) outcome reveal is now independent
  of perspective (the store defaults to and resets to OMNISCIENT — perspective-implied
  reveal would defeat unspoiled-by-default), gating cards' win-shape copy, the outcome
  filters, and URL state; (F4) 19.25's union-of-checks mandate was itself a charter
  violation (validity/funnel divergences are DELIBERATE per funnel's own comment) —
  replaced with shared mechanics + named per-consumer validation profiles with negative
  fixtures; (F5) the dispatch template's authority line is neutralized in THIS planning
  PR via AGENTS.md indirection (true before and after 19.1), removing the
  authority-contradiction window without a bootstrap task; (F6) the 19.28 close runs
  BOTH pytest tiers and the campaign CI job is scheduled, not merely path-filtered;
  (F7) the ticker renders through the perspective projection with four pinned fog cases
  and frame-bounded cost chips (the served event views carry privileged attribution);
  (F8) the realpath schema relocation carries its full dependency closure
  (`RealPathSeedTelemetry`, proof validators) and its round-trip/invalid-proof tests
  into a surviving test module. Improvements absorbed: the demo bundle is
  browser-tested with a zero-`/api` interception (19.13 deps 19.12); the Playwright
  browser is specified (channel or pinned+cached), never assumed; 19.19/19.24 may land
  as sanctioned stacked-PR sequences; the task parser dedupes Depends ids and the
  validator now rejects unknown dependencies and cycles (with guard tests, this PR);
  19.15's forward-recording redaction is ratified by name in locked decision 1; and the
  scope-gated constraint rules gained focused tests.
- **The eighth Codex review round (2 findings)** was verified claim-by-claim — both
  reproduced — and absorbed: the coevo prune would have stranded 268 of the 313
  training sidecars away from 19.23's flat verification promise, so 19.22 now keeps
  moved weight/sidecar pairs paired with hashes in the in-tree manifest and 19.23
  verifies per-class (in-tree offline; evidence-branch after fetch; absent reported as
  its own class, never a silent skip); and `ContradictionBadge.tsx` (the MindInspector
  evidence badge, styling by `kind` alone) joins 19.11 so weak flags are subordinated
  on every rendering surface.
- **The seventh Codex review round (4 findings)** was verified claim-by-claim — all
  four reproduced — and absorbed: `tests/eval/test_gate_metrics.py` (24 complete
  `GateMetricsReport` literals) and `tests/scripts/test_measure_baseline_cli.py` (the
  exact CLI contract) join 19.5; `frontend/src/components/TurnCard.tsx` joins 19.11
  (the INLINE `ContradictionMarker` branches on severity alone, so the summary fix
  left the same proof contradiction-styled inline); and the cross-test-import backlog
  count corrects from three to five (two more `test_prompt_byte_golden` importers in
  tests/agents).
- **The sixth Codex review round (7 findings)** was verified claim-by-claim — all seven
  reproduced — and absorbed: the generated-type ripple reaches the Storybook fixtures
  that construct complete `ReplayView`/`ContradictionView` literals
  (MeetingView/MapStage stories join 19.10; MeetingView/MindInspector stories join
  19.11); 19.3's implementation hint was UNREALIZABLE as written (inverse-CDF tails
  need `ln` — no polynomial removes it) and is rewritten to the realizable rule: libm
  is the hazard, not the mathematics, so any needed transcendental is a documented
  in-module pure-arithmetic routine; the post-flip stale-default copy sweep is
  assigned to the downstream owners of each file (HighlightCard comments → 19.10,
  dashboard copy + BeliefMatrix comment → 19.13, both ordered after 19.9);
  `tests/api/test_leak.py`'s exact field-set snapshot and the
  `_TournamentEvalReportView` mirror join both report-extension tasks (19.5/19.14);
  `tests/eval/test_wave2_metrics.py` (five independent report builds) joins 19.27's
  fixture adoption; and 19.9's test scope narrows to `tests/api/test_sets.py` so the
  two Wave-1 roots stay unordered.
- **The fifth Codex review round (9 findings)** was verified claim-by-claim — all nine
  reproduced — and absorbed: 19.27's no-cross-test-imports DoD narrows to the four
  named `test_manager` importers (the other three repo cross-test imports are
  enumerated and backlogged below); `training/rewards.py`'s first-meeting docstring
  joins 19.19; 19.6 regenerates the token CSS output (`index.css` via
  `gen-tokens-css.ts` — tokens.ts alone resolves nothing) with the durable ramp vitest
  deferred to 19.12; 19.10's stale ReplayPicker exclusion line is removed (a
  contradiction introduced by the round-4 fix itself); BOTH generator artifacts
  (`api.ts` + `api.fidelity.ts`) regenerate in 19.10/19.11/19.24; the rubric-label DoD
  is split across the three owning tasks (19.9 picker, 19.10 HighlightCard, 19.5
  dashboard histogram); 19.24 depends on 19.12 and ships an executable vitest
  rejection test; the typed dashboard story fixture joins 19.5/19.14; and 19.3 gains
  pinned distribution-quality assertions so a portable-but-degenerate sampler cannot
  silently replace the Gaussian.
- **The fourth Codex review round (8 findings)** was verified claim-by-claim — all
  eight reproduced (one, the ballot-chip disclosure, verifies as data flow rather than
  at the cited literal: `teammate_coerced` reaches `BallotCard` inside
  `rewrite_reasons`) — and absorbed: 19.3's cross-platform claim now requires the
  owner-assisted Darwin-arm64 digest comparison before it is advertised (a Linux-only
  double-run cannot prove the motivating failure fixed); 19.14 pins the cross-tab under
  BOTH partitions with separate denominators (meeting-flag 10/31 = 32.3% vs
  ejectee-proof 10/33 = 30.3% — the round caught the two being mixed in one sentence,
  the C5 lesson applied to this plan itself); `tests/llm/test_client.py`'s
  fallback-pricing assertion joins 19.6; 19.7's smoke imports entry modules (all six
  package `__init__`s are 0 bytes — bare-package imports prove nothing); the featured
  entry cards' WinnerTag joins 19.10's unspoiled mode (HighlightCard + the picker's
  winner pass-through); the `teammate_coerced` chip gets perspective gating in 19.11
  (19.15 stays manager-side only); the finalist-pins module-reference docstrings join
  19.19 (artifact DATA paths under `realpath-crew/` stay); and 19.27 names its golden
  output directories explicitly.
- **The third Codex review round (8 findings)** was verified claim-by-claim — all eight
  reproduced — and absorbed: AGENT_IMPLEMENTATION.md joins 19.1's authority demotion
  (with the generator's second constraint scope-gated in the planning PR; zero parsed
  tasks list the file, so only 19.1's prompt changes); the campaign test tier gets a
  standing automated CI home in 19.27 (a scheduled/path-filtered `-m campaign` job —
  never orphaned by promise alone); `training/crew/scorer.py:113` is a second verified
  production consumer of the leak scanners and joins 19.24's import swap (and
  `training/crew/` joins 19.18's freeze-label scope — a gap the finding exposed); the
  whole `llm/README.md` cache worked example (:126-147) leaves with the module; the
  `survival_rate` None convention propagates through `eval/prompt_regression.py:257`
  (+ its metrics model and test) in 19.5; 19.25 targets the leak walk at its post-19.24
  home (`eval/leak_scan.py`); 19.16 depends on 19.9 (the guide quotes the curation);
  and three more realpath reference sites (driver:207/:281-283/:949,
  test_coevo_driver:1764) join 19.19 with a closing repo-wide-grep DoD.
- **The second Codex review round (6 findings)** was likewise verified claim-by-claim —
  all six reproduced — and absorbed. Two more source-audit refutations came out of it:
  7. **The five bespoke prompt sets are LIVE**, not dead-code candidates: all five are
     registered in `orchestrator/game.py:343-350` and parametrically loaded/validated by
     `tests/agents/test_bespoke_prompt_sets.py`. The deletion item is removed from
     19.19 entirely (nothing in `agents/strategic/prompts/` moves this phase).
  8. **The dispatch surface asserted the demoted authority**: every generated prompt's
     template line ("DESIGN.md is the source of truth",
     `scripts/prompt_template.md.j2:19`) now changes atomically with the demotion —
     19.1 rewrites the authority line and regenerates all prompts in the same PR.
  The remaining four: realpath docstring references in surviving modules
  (hall_of_fame:279, conviction/serving:301) join 19.19's scope; the runtime-partition
  smoke becomes `uv run --no-dev --exact` (a bare `uv run` re-syncs the dev group and
  proves nothing); 19.1 now depends on 19.3 (the README's portability claim quotes
  19.3's recorded outcome — the frontier drops to seven roots and the critical path is
  the nine-task 19.5 → 19.10 → 19.11 → 19.14 → 19.13 → 19.24 → 19.25 → 19.27 → 19.28);
  and the static demo routes the two verified direct-fetch bypasses
  (BeliefMatrix.tsx:30-46, TournamentDashboard.tsx:753) through the data seam, with
  19.13 ordered behind 19.14 on the shared dashboard file.
- **The first Codex review round (10 findings, PR #322)** was verified claim-by-claim
  against the bytes — all ten reproduced — and absorbed: the planning PR itself now
  carries the generator's DESIGN.md scope-gate (resolving the 19.1 bootstrap
  contradiction; locked decision 8 — five historical prompts whose contracts listed
  DESIGN.md in the pre-demotion era drop the constraint line under the same rule,
  recorded in the register), 19.19 gained the verified consumer migrations
  (`RealPathRerankRow` relocation for `generate_campaign_tables`, the full
  `first_meeting` test list, the `llm/README.md` cache line), 19.14 gained the
  `TournamentEvalReport` wrapper ownership (`extra="forbid"` — the cells must live on
  the canonical owner), 19.9/19.12 gained the client-contract comment and the
  error-field consumers, 19.7 states the pytest/leak_test boundary, and 19.23 now
  depends on the raw-slate ruling.
- Validator/generator/frontier all green at authoring and after both review rounds:
  321 tasks ↔ 321 prompts (293 + 28), `generate_prompts.py --check` in sync, and
  `uv run python scripts/compute_next_task.py --phase 19` reports exactly the designed
  frontier
  (seven roots — 19.2–19.6, 19.8, 19.9 — dispatchable, twenty-one blocked; 19.1 waits
  on 19.3's recorded portability outcome).
