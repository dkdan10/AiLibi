# Phase 19 input audit — Codex

**Audit date:** 2026-08-02

**Audited revision:** `48925e7eac706cb2dbfa154c4bd50752138b75af`

**Auditor:** Codex, working independently from the separately commissioned audit

## Executive summary

AiLibi is a real, substantial, locally runnable research system rather than a speculative design. Its durable core is unusually good: an immutable tick engine with explicit RNG ownership (`engine/world.py:52-84`, `engine/tick.py:565-651`, `engine/rng.py:63-165`), a narrow and executable observation firewall (`observation/action_intent.py:14-125`, `orchestrator/boundary.py:16-50`, `.importlinter:1-42`), byte-verifiable replays, typed Python-to-TypeScript view contracts, and a replay viewer that exposes both ground truth and agent belief (`api/schemas.py:39-52`, `scripts/gen_frontend_types.py:1-78`, `frontend/src/components/GuidedTour.tsx:147-227`). **[VERIFIED—run]** I reconstructed all 300 committed sample/corpus games without a hash mismatch, generated the same fake-provider game twice with identical bytes, exercised the API and browser viewer, and independently recomputed the principal committed ML metrics.

The repository is nevertheless not in a release-quality state today. **[VERIFIED—run]** The standing gate fails: 4,530 tests passed, 20 skipped, three xfailed, and one failed because the ES suite's fixed cross-machine digest differs on Python 3.11.15/Darwin arm64 (`tests/training/test_es.py:74-91`, `training/bakeoff/es.py:19-26,184-193`); because `scripts/check.sh` is fail-fast, its frontend leg did not run, although an independent `npm run tsc:check && npm run build` passed (`scripts/check.sh:1-24`). **[VERIFIED—read/run]** More broadly, the repository's asserted source of truth is stale, the public README reports obsolete milestones and metrics, the default spectator path spoils and then rushes past its best material, 85–87% of correct 9p ejections co-occur with ejectee-specific grounded vent proof while non-direct correctness is much lower, and the ML program has accumulated much more machinery than adopted product behavior (`AGENTS.md:14-24`, `DESIGN.md:1-17`, `README.md:13,48-104`, `frontend/src/hooks/usePlayback.ts:304-382`, `replays/samples/9p2i/tournament-eval-report.json:79744-79769`, `replays/ml_corpus/9p2i/tournament-eval-report.json:224645-224670`, `training/reports/report-finalist-eval.md:1074-1165`).

The strongest portfolio story is not “an AI version of Among Us”; it is **a deterministic, inspectable hidden-information laboratory built through hundreds of agent-authored changes while preserving an enforced information boundary**. **[JUDGMENT—portfolio progressive-disclosure standard]** That story can impress a senior engineer or research-minded employer, but a stranger currently has to excavate it from a stale, text-heavy README, then install two toolchains, then discover that the unscored four-player set is the API default (`README.md:73-104,158-175`, `api/replay_loader.py:2644-2659,2752-2768`, `frontend/src/components/ReplayPicker.tsx:18-24,207-218`). The polished cream/ink viewer, first-run tour, fog switch, belief matrix, mind inspector, citations, and key-moment navigation already provide most of the demonstration surface worth building around (`frontend/src/components/GuidedTour.tsx:147-227`, `frontend/src/lib/playback.ts:58-133,170-228,250-320`, `frontend/src/components/MeetingView.tsx:96-293`).

### Phase 19 recommendation in three sentences

Keep the review-and-refresh charter, but define “refresh” as a correctness-and-narrative release: first restore a green portable gate and truthful documentation, then make a curated nine-player replay readable from opening through an unspoiled finale, and lock that path with browser tests (`tasks/post-phase-14-plan.md:108-114,187-193`). Freeze the ML ladder and retain its compact inference, corpus, evaluators, validity gates, and train/serve parity work; spend Phase 19 on correcting reward/evidence claims, recovering final-eval lineage if possible, reporting paired uncertainty, and retiring or archiving scaffolding—not on another optimizer or recording slate (`scripts/run_tournament.py:160-175,279-295`, `training/reports/report-finalist-eval.md:998-1030,1074-1165`). Finally, promote genuine inference, weak-flag failures, turn-to-ballot consistency, and direct-proof share to first-class game metrics before changing gameplay, because the present watchability scalar and headline ejection accuracy obscure the most important behavioral distinction (`eval/watchability.py:9-20,53-57,1965-1973`, `meetings/schemas.py:442-460`).

---

## Audit method, standards, and confidence

Every substantive statement below is prefixed or scoped as one of:

- **[VERIFIED—run]** I generated the evidence by executing code or parsing committed artifacts.
- **[VERIFIED—read]** I checked the implementation or committed bytes at the cited lines.
- **[JUDGMENT]** an engineering or product conclusion, with the comparison standard named.
- **[SPECULATION]** a plausible explanation not established by the evidence.
- **[UNVERIFIED]** explicitly outside the runnable evidence available here.

Severity is ranked **P0** (blocks a credible Phase 19 close/public demonstration), **P1** (high impact), **P2** (important hardening), then **P3** (cleanup). Rough size is **XS** (<1 day), **S** (1–3 days), **M** (roughly a week), **L** (multi-week), or **XL** (new campaign/re-recording scale), for one engineer familiar with the system.

### Executed evidence

| Check | Result | What it establishes |
|---|---|---|
| `bash scripts/setup_env.sh` | **PASS**; locked Python environment and 202 frontend packages installed | The documented bootstrap is functional; it actually requires both `uv` and npm (`scripts/setup_env.sh:4-45`). The install reported two high-severity npm advisories, but this environment did not permit the dependency-graph upload needed to identify them, so I make no package-specific vulnerability claim. |
| `bash scripts/check.sh` | **FAIL** after 4,530 passed / 20 skipped / 3 xfailed / 1 failed | Ruff, formatting, import-linter, task/prompt validation, strict mypy, and all but one pytest case passed; fail-fast stopped before the frontend block (`scripts/check.sh:1-24`). The failure is analyzed in §3. |
| `uv run pytest tests/training -q` | **FAIL:** 796 passed / 1 failed | The only training failure is the same ES portability pin (`tests/training/test_es.py:74-91`). |
| `npm run tsc:check && npm run build` | **PASS:** Vite built 863 modules | The frontend type/build path works independently; it does not establish behavior or accessibility because there is no frontend test command (`frontend/package.json:6-34`). |
| Fake-provider seed 42, twice | **PASS:** byte-identical SHA-256, same impostor win at tick 18 | The core deterministic game path is functional without credentials; this directly checks the README's reproducibility claim (`README.md:73-86`). |
| Committed replay verification | **PASS:** 50/50 sample 4p, 50/50 sample 9p, 50/50 corpus 4p, 150/150 corpus 9p | All 300 games reconstructed through engine state hashes; the verifier's fail-loud walk is in `scripts/_verify_samples.py:164-304`, and the independent kill-craft walker also re-seeds and checks hashes (`eval/kill_craft.py:104-147,334-400`). |
| API + in-app browser | **PASS** for health, sets, lists, rubric, full replay, tour, key-moment jumps, meeting, ballots, roster, and controls | The local spectator is functional. It also exposed the mixed-time frame, misleading “Contradictions” label, winner spoiler, and narrative-flow problems described below (`api/replay_loader.py:1172-1205`, `frontend/src/App.tsx:252-301,358-480`). |
| Current watchability fold | **PASS:** sample-9p top seed 2 = 89.9, bottom seed 47 = 18.4, median-score seeds 11/45 = 52.3 | These are current internal scorer results used only to select games for manual reading; the computation and its caveats are in `eval/watchability.py:1965-1973,2118-2219`. |
| Offline ML evidence recomputation | **PASS** for corpus verifier, surrogate, conviction, and composed runner | Recomputed: surrogate top-1 0.7667 and decision accuracy 0.375 (96/96 test meetings predicted SKIP); conviction flag-count Spearman 0.5782 and conversion accuracy 0.9375; composed decision accuracy 0.8646 and exact outcome 0.7917. The committed reports provide the corresponding definitions and results (`training/reports/report-ballot-surrogate.md:226-246,285-347`, `training/reports/report-conviction-model.md:180-218`, `training/reports/report-composed-runner.md:118-167`). |

**[UNVERIFIED]** I did not record a new Featherless/Anthropic/Ollama game. The first two require credentials, and the final finalist report prices a comparable real-provider slate at about 57 busy hours (`training/reports/report-finalist-eval.md:998-1030`). I exercised committed artifact loading, compact inference, fidelity evaluation, and offline model recomputation, but did not run a fresh ES/co-evolution campaign or a real-provider learned-policy tournament end to end.

### External standards used

- **Deterministic Python:** Python guarantees a compatible seeded `random()` sequence, not that every distribution algorithm remains invariant; its own [reproducibility notes](https://docs.python.org/3.11/library/random.html#notes-on-reproducibility) are the standard applied to the ES hash.
- **Episodic reward shaping:** the terminal-potential qualification in [Reward Shaping in Episodic Reinforcement Learning](https://www.ifaamas.org/Proceedings/aamas2017/pdfs/p565.pdf) is the standard applied to the policy-invariance claim.
- **ML evidence lineage:** runs should retain or addressably link code version, parameters, metrics, inputs, and output artifacts; [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/) is used as a concrete mainstream reference, not as a recommendation to adopt MLflow itself.
- **Statistical comparison:** matched binary outcomes use an exact binomial McNemar test ([statsmodels reference](https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html)); repeated candidate comparisons require a named multiplicity policy, for which scikit-learn's [statistical comparison example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_grid_search_stats.html) is a practical broader reference.
- **Frontend testing:** test user-visible behavior and a small critical browser journey; [Playwright's best practices](https://playwright.dev/docs/best-practices) are the reference.
- **CI supply chain:** least-privilege token permissions and immutable action revisions; GitHub's [secure-use reference](https://docs.github.com/en/actions/reference/security/secure-use) and [full-SHA setting](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository?apiVersion=2022-11-28) are the reference.
- **Large artifacts:** preserve content identity while keeping bulk data out of ordinary Git objects; [Git LFS](https://git-lfs.com/) and [MLflow artifact stores](https://mlflow.org/docs/latest/self-hosting/architecture/artifact-store/) illustrate the practice. The project need not adopt either product.

---

## 1. Project state

### 1.1 Overall verdict

**[VERIFIED—run/read]** AiLibi works as a local deterministic simulator, replay corpus, evaluation laboratory, and privileged replay viewer. It is not currently a live multiplayer game or hosted public app; the design explicitly says persistence is local JSONL/JSON, there is no live WebSocket path or `POST /games`, and the viewer is replay-only (`DESIGN.md:7-17`). The local-only posture is responsible because the API intentionally exposes roles, kills, vents, prompts, and other game-master data without authentication (`docs/deployment.md:10-32`); loopback binding is preserved in Docker (`docker-compose.yml:31-37`).

**[JUDGMENT—research-software standard]** The repository is closer to a mature research prototype than a product. It has excellent executable invariants and unusually deep evaluation plumbing, but its public claims, default experience, experiment lineage, and one standing test do not meet release discipline.

### 1.2 Code-rooted architecture inventory

| Layer | Current implementation and assessment |
|---|---|
| Engine | **[VERIFIED—read, strong]** Frozen `WorldState`, read-only mappings, explicit serialized RNG state, and a single tick transition make ownership legible (`engine/world.py:52-84`, `engine/rng.py:63-165`, `engine/tick.py:565-651`). Preserve this shape. |
| Observation boundary | **[VERIFIED—read/run, strong]** Agents emit a discriminated, frozen `ActionIntent` union and the orchestrator alone translates it to engine actions (`observation/action_intent.py:14-125`, `orchestrator/boundary.py:16-50`). Recursive packet walking and import-linter protect both data and module boundaries (`eval/leak_test.py:166-230`, `.importlinter:1-42`); targeted determinism/leak/API tests passed 240/240, with two skips. |
| Agents and memory | **[VERIFIED—read, mixed]** Tactical decisions remain engine-free and structured memory feeds meetings, satisfying the three load-bearing rules (`README.md:34-42`). However, `agents/runtime.py` is a retained test scaffold whose action is always `WaitIntent`; the live composition is `orchestrator.game.TacticalAgent` (`agents/runtime.py:1-14,27-44,118-137`, `orchestrator/game.py:2500-2525`). The code is honest about this, while the authoritative design is not. |
| Meetings | **[VERIFIED—read/run, strong but concentrated]** Structured turns, observations, citations, flags, ballots, and result objects produce auditable deliberation. Ownership is concentrated in 3,780-line `meetings/manager.py` and 3,524-line `meetings/transcript.py`, and the overloaded “contradiction” schema now also carries role-proof evidence (`meetings/manager.py:3780`, `meetings/transcript.py:3524`, `meetings/schemas.py:423-460`). |
| Orchestration/replays | **[VERIFIED—run, strong]** The fake-provider full game and all committed replay sets reconstruct exactly. `orchestrator/game.py` is also a 3,143-line composition root, while several evaluators and the API repeat replay walks (`orchestrator/game.py:3143`, `training/env.py:928-955`, `eval/kill_craft.py:104-117`). |
| Evaluation/ML | **[VERIFIED—run, mixed]** Hashes, corpus splits, artifact fingerprints, validity gates, paired seeds, compact learned inference, and parity tests are real. The optimizer/campaign layer has outgrown its demonstrated adoption and contains two serious evidence defects (§4). |
| API/view contracts | **[VERIFIED—read/run, strong]** Pydantic DTOs generate TypeScript and a drift fixture compiles exhaustive discriminated unions (`api/schemas.py:39-52`, `scripts/gen_frontend_types.py:1-78`, `tests/api/test_view_model.py:970-1001`). Runtime clients still cast unvalidated JSON and accept any view-model version (`frontend/src/api/client.ts:36-55`, `frontend/src/types/api.ts:24-31`). |
| Frontend | **[VERIFIED—run/read, strong surface, weak behavior gate]** React/Pixi/Vite builds and the rendered workspace is distinctive and information-rich. It has lazy routes, keyboard transport, fog, mind and belief views, focus handling, and reduced-motion CSS (`frontend/src/App.tsx:57-72,99-198`, `frontend/src/hooks/useFocusTrap.ts:1-67`, `frontend/src/index.css:183-198`), but no component or E2E test command (`frontend/package.json:6-34`). |

### 1.3 What is genuinely good and worth preserving

1. **The observation firewall is an architectural asset.** **[VERIFIED—read/run]** It is a narrow data contract, an import rule, and a recursive behavioral test—not a comment (`observation/action_intent.py:14-125`, `.importlinter:1-42`, `eval/leak_test.py:166-230`). **[JUDGMENT—capability-security standard]** This is the repository's clearest demonstration of preventing privileged-state leakage by construction.
2. **Replays are executable evidence.** **[VERIFIED—run]** Every committed game I checked reconstructed through the current engine, and the fake-provider replay remained byte-identical. The project records state hashes per tick and ships fail-loud verification (`README.md:73-86,100-102`, `scripts/_verify_samples.py:164-304`).
3. **Cross-language DTO drift is handled well.** **[VERIFIED—read]** Python remains the source, generation is mechanical, and TypeScript exhaustiveness is checked in Python tests (`api/schemas.py:39-52`, `scripts/gen_frontend_types.py:1-78`, `tests/api/test_view_model.py:970-1001`).
4. **The spectator's analytical concept is excellent.** **[VERIFIED—run/read]** The first-run tour teaches ground truth versus belief, perspective fog, Belief × Truth, mind inspection, and transport shortcuts (`frontend/src/components/GuidedTour.tsx:147-227`). **[JUDGMENT—explainable-agent UX standard]** Few portfolio projects make private knowledge, public claims, model prompts, citations, and post-hoc truth this inspectable.
5. **Failure is usually explicit.** **[VERIFIED—read]** Frozen/forbid-extra models, invalid-action errors, replay hash mismatches, artifact hashes, and stamp validation embody the repository's “no silent fallback” rule (`engine/world.py:87-92`, `api/replay_loader.py:1180-1187`, `scripts/run_tournament.py:740-770`).

### 1.4 What is fragile, confusing, or overbuilt

1. **P0 — the asserted architecture source of truth is not current.** **[VERIFIED—read]** Contributors must obey `DESIGN.md` (`AGENTS.md:14-24`), yet that document says it was reconciled only through Phase 6 (`DESIGN.md:1-17`). It describes `AgentRuntime` as the production composition while code labels it test-only, and it calls `api/` thin although `api/replay_loader.py` is a 2,838-line privileged reconstruction subsystem (`DESIGN.md:152-179,238-240,430-432`, `agents/runtime.py:1-14`, `api/replay_loader.py:1-24,2838`). **[JUDGMENT—documentation-as-code standard]** Stale optional prose is annoying; stale mandatory prose is an implementation risk.
2. **P1 — source modules have become phase-history monoliths.** **[VERIFIED—read]** `meetings/manager.py:3780`, `meetings/transcript.py:3524`, `orchestrator/game.py:3143`, and `api/replay_loader.py:2838` each combine several stable responsibilities. **[JUDGMENT—high-cohesion/change-isolation standard]** Split replay walking/projection and meeting phases at tested seams; do not rewrite the engine.
3. **P1 — training scale is disproportionate to adoption.** **[VERIFIED—run/read]** Measured footprint is 33,220 training-source lines, 29,835 training-test lines, and 1,588 tracked training-artifact files totaling 107.4 MB (102.4 MiB), while the scripted FSM remains the default (`scripts/run_tournament.py:160-175,279-295`). The conclusion is in §4.
4. **P2 — tooling is comprehensive but not cleanly partitioned.** **[VERIFIED—read]** Test/lint tools sit in runtime dependencies while the development group contains only type stubs (`pyproject.toml:7-21,48-51`); CI repeats frontend installation/build already performed by setup/check (`scripts/setup_env.sh:18-45`, `scripts/check.sh:12-24`, `.github/workflows/ci.yml:32-57`).
5. **P2 — Git is carrying artifact-store duties.** **[VERIFIED—run]** The checkout contains 2,985 tracked files; `replays/` is about 221 MiB, the ML corpus 161 MiB, and `.git` 151 MiB. The largest value is the 300 verified source replays, but giant regenerated reports and intermediate campaign artifacts make normal clone/review work heavier without improving source traceability (§4.3).

---

## 2. Portfolio assessment

### 2.1 Strongest story

**[JUDGMENT—portfolio differentiation standard]** Lead with the engineering experiment: “Hundreds of AI-authored changes built a deterministic social-reasoning simulator without violating an executable hidden-information boundary.” The code supports each noun: contracts/prompts are generated and checked (`README.md:17-30`), the engine and RNG are explicit (`engine/tick.py:565-651`, `engine/rng.py:63-165`), the firewall is enforced (`.importlinter:1-42`, `eval/leak_test.py:166-230`), and the UI can juxtapose truth with each agent's rendered knowledge (`frontend/src/components/GuidedTour.tsx:147-227`).

“Emergent AI gameplay” should not be the lead. **[VERIFIED—read/run]** The project's own Phase 18 close records zero of fourteen preregistered emergence rulings demonstrated and no default mover flip (`tasks/phase-18.md:3-25`), while corpus analysis shows that most correct convictions co-occur with ejectee-specific role-proof vent flags (`api/schemas.py:583-610,696-724`; §5). **[JUDGMENT]** The honest story—disciplined systems work plus measured negative ML/game-design results—is stronger than overstating emergence.

### 2.2 First five minutes today

1. **P0 — facts are stale.** **[VERIFIED—read/run]** `README.md:13` says 219 PRs through Phase 14 and about 2,500 tests; audited HEAD is merge #319 and pytest collected 4,554. The phase table stops at Phase 14 and compresses Phases 15–18 into one very long paragraph (`README.md:46-69`).
2. **P0 — the sample claim disagrees with committed artifacts.** **[VERIFIED—read/run]** README says refreshed 2026-07-14 with impostor win rates 30%/36% (`README.md:90-102`); manifests say 2026-07-20, and current outcomes are 34%/30% (`replays/samples/4p1i/MANIFEST.md:10-61`, `replays/samples/9p2i/MANIFEST.md:10-61`). The README also calls a conversion-label metric “decision accuracy 0.938,” while actual composed meeting-decision accuracy is 0.8646 (`README.md:69`, `training/reports/report-conviction-model.md:190-199`, `training/reports/report-composed-runner.md:118-167`).
3. **P0 — there is no immediate visual proof.** **[VERIFIED—read]** The README offers only commands and prose for the viewer, with no screenshot/GIF or hosted demo (`README.md:73-104`). Setup mentions Python and `uv` but not the hard Node/npm prerequisite exercised by setup (`README.md:158-175`, `scripts/setup_env.sh:18-45`).
4. **P0 — the unguided default is the weakest spectator set, and its UI copy is wrong.** **[JUDGMENT, supported by run/read]** The API default is `4p1i`; that set has no interestingness rubric, and the frontend incorrectly calls it “mostly zero-meeting” (`api/replay_loader.py:2644-2659,2752-2768`, `frontend/src/components/ReplayPicker.tsx:18-24,207-218`). In fact, 39/50 sample games and 40/50 corpus games have exactly one meeting, but they are much shorter and less deliberative than 9p (§5). The tour correctly works around this by loading a high-interest 9p game (`frontend/src/components/GuidedTour.tsx:26-80,242-270`), so product default, product copy, and teaching default disagree.
5. **P1 — the UI is better than its documentation.** **[VERIFIED—run/read]** The README calls it “intentionally minimal” (`README.md:104`); the actual viewer has lazy map/mind routes, guided onboarding, fog, keyboard navigation, a suspicion matrix, a detailed meeting chain, ballots, and prompts (`frontend/src/App.tsx:57-72,99-198`, `frontend/src/components/GuidedTour.tsx:147-227`, `frontend/src/components/MeetingView.tsx:96-293`). This is currently hidden value.

### 2.3 Concrete demonstration priorities

1. **P0 / S — make one canonical five-minute path.** **[JUDGMENT]** Open on a curated, freshly scored 9p replay; offer “Watch unspoiled” and “Inspect omnisciently”; pause at meetings; end with winner/reason plus a compact “what each agent knew” recap. The present API default and autoplay behavior work against that path (`api/replay_loader.py:2644-2659`, `frontend/src/hooks/usePlayback.ts:304-382`).
2. **P0 / S — put proof above the fold.** **[JUDGMENT]** Add a 30–60 second capture, one screenshot of Belief × Truth/meeting evidence, and three current claims with reproducible commands. Link directly to a featured seed and explain local-only/no-auth status (`docs/deployment.md:10-32`).
3. **P0 / XS — make README facts generated or checked.** **[JUDGMENT—documentation-as-code standard]** Derive test count, sample provenance/outcomes, baseline, and phase list from committed sources where practical; otherwise add a small consistency check. Current drift is enumerated above (`README.md:13,46-104`).
4. **P1 / M — publish a safe static/read-only demo or a recorded fallback.** **[JUDGMENT]** Do not expose the unauthenticated GM API directly; deployment documentation correctly forbids that (`docs/deployment.md:10-32`). A prebuilt curated replay bundle can demonstrate the UI without live games, credentials, or a privileged origin.
5. **P1 / XS — add public-project basics.** **[VERIFIED—read]** No tracked `LICENSE`, `CONTRIBUTING`, or `SECURITY` file exists. **[JUDGMENT—public repository norm]** The owner must choose the license; absent a license, outsiders cannot safely reuse the work.

---

## 3. Fix / refactor / harden

Ranked within this section:

| Priority | Finding | Why it matters / standard | Size and proposed action |
|---|---|---|---|
| **P0** | **[VERIFIED—run/read] Standing gate is red on a non-portable digest promise.** `random.Random.gauss()` drives ES mutations while comments/tests promise cross-machine bit stability (`training/bakeoff/es.py:19-26,184-193`, `tests/training/test_es.py:74-91`). Same-host double runs matched, but expected `e3b67c…` became `3a6ec34…` on Darwin arm64. | Python promises seeded `random()`, not every distribution implementation; `gauss`/libm variation is the likely source, but this audit did not isolate it on a reference host. A deterministic-engine project must distinguish same-runtime repeatability from portability. | **S–M.** Implement and golden-test a specified portable normal sampler, or explicitly pin platform/interpreter and narrow the claim. Updating only the golden hash would conceal the unsupported promise; restore `bash scripts/check.sh` green. |
| **P0** | **[VERIFIED—read] Mandatory docs and public facts contradict code/artifacts.** Design status is Phase 6, runtime ownership is wrong, provider/baseline text is stale, `.env.example` describes graduated evidence features as disabled, and README metrics are obsolete (`DESIGN.md:1-17,152-179,238-240`, `agents/runtime.py:1-14`, `AGENTS.md:64-79`, `.env.example:63-186`, `README.md:13,46-104`). | Documentation-as-code: the repository explicitly makes design prose authoritative (`AGENTS.md:14-24`). | **S–M.** Reconcile design/module inventory/config/README; add checks for generated facts and live environment keys. |
| **P0** | **[VERIFIED—read/run] Default 1× autoplay with auto-follow makes meetings unreadable.** Base cadence is 500 ms; the timer advances continuously; auto-follow selects the meeting on its single frame and clears it on the next (`frontend/src/hooks/usePlayback.ts:38-40,304-382`). Manually selected meetings persist and other speeds change the interval, but the default Play path gives several ~42-word turns about half a second. | Critical-path browser behavior, not type correctness. The app's core content cannot be consumed with default Play. | **S.** Pause on meeting entry, provide Resume/next beat, and add a behavior/E2E test. |
| **P0** | **[VERIFIED—read] The viewer spoils the result and lacks a finale.** Header always renders `meta.winner`; transport merely stops at the last frame, and production has no `winner_reason`/`game_over` renderer (`frontend/src/App.tsx:252-301`, `frontend/src/hooks/usePlayback.ts:304-331`). | Replay/sports-storytelling norm: preserve suspense, then deliver resolution. | **S.** Default unspoiled mode plus explicit end card with winner, reason, decisive events, and reveal toggle. |
| **P1** | **[VERIFIED—run/read] Meeting frames mix two times.** At a meeting tick, roster liveness comes from pre-ejection `agent_states`, while the alive counts come from post-ejection `advantage`; loader comments confirm the deliberate mix (`api/replay_loader.py:1172-1205`, `frontend/src/App.tsx:358-388,416-480`). In the browser, the tally said crew 5 / impostor 1 while both impostors still showed alive. | Snapshot-coherence standard: one frame should have one temporal meaning, or timing must be explicit. | **S–M.** Model pre-resolution and post-resolution states separately, or keep one phase consistent and label the transition. Add a fixture test. |
| **P1** | **[VERIFIED—run/read] “Contradictions” includes self-linked proof.** `vent_sighting` is put into `ContradictionRef` with identical event IDs (`meetings/schemas.py:423-460`, `meetings/transcript.py:2880-2906`), and the UI always renders `A ↔ B` under “Contradictions” (`frontend/src/components/MeetingView.tsx:303-383`). The browser showed `p-1 ↔ p-1` and `p-8 ↔ p-8`. | Semantic typing and data-display truthfulness. A grounded evidence flag is not a contradiction. | **S.** Introduce an evidence-flag union/category and render role proof separately; migrate API/types/tests. |
| **P1** | **[VERIFIED—run/read] Private ballot rationales sometimes break character by naming secret teammates or self-authored kills.** A parse found 13/1,088 ballots (1.19%; 13/204 meetings) with such text, e.g. seed 11 says “p-3 is my partner” (`replays/samples/9p2i/replay-seed-11.jsonl:11`; further examples at `replays/samples/9p2i/replay-seed-18.jsonl:13` and `replays/samples/9p2i/replay-seed-21.jsonl:12`). The vote guard coerces teammate targets but preserves the original rationale (`meetings/manager.py:1906-1913,2893-2925`). | Narrative consistency, not an observation-firewall breach: ballots are spectator-private. Still, a character should reason strategically without addressing the spectator as an omniscient optimizer. | **S.** Add a rationale constraint/redaction or regenerate a neutral strategic reason after guard coercion; regression-test secret-name phrases. |
| **P1** | **[VERIFIED—run/read] Weak interval flags can railroad votes.** The low-tail seed 47 ejects an innocent after weak inclusive-window flags despite contradictory conversation (`replays/samples/9p2i/replay-seed-47.jsonl:37-38`). | Social-deduction coherence: weak evidence should not mechanically dominate testimony without an articulated bridge. | **M.** Add same-agent turn→ballot consistency and weak-flag-only conviction metrics/tests before tuning gates. Review interval endpoint semantics. |
| **P1** | **[VERIFIED—read] API import depends on current working directory.** Replay-root resolution is CWD-relative and `create_app()` runs at module import (`api/main.py:24-27,85-112,152-188`); importing with the repo only on `PYTHONPATH` from `/private/tmp` raised `RuntimeError`. | Application-factory/config-injection norm. Packaging, tests, and service managers need location-independent imports. | **S.** Inject/configure the data root or resolve a project resource; test import from another CWD. |
| **P1** | **[VERIFIED—read] Network DTOs have compile-time but not runtime version safety.** `getJson<T>` casts arbitrary JSON and `viewModelVersion` is just `string` (`frontend/src/api/client.ts:36-55`, `frontend/src/types/api.ts:24-31`). | Validate trust boundaries; generated types disappear at runtime. | **S.** Generate a literal version constant plus rejection path, or a small runtime schema for endpoint envelopes. |
| **P1** | **[VERIFIED—read] Frontend has no behavior or accessibility gate.** Scripts cover build/typecheck/Storybook only; CI repeats build but runs no Vitest/Testing Library/Playwright (`frontend/package.json:6-34`, `.github/workflows/ci.yml:32-57`). | Testing-pyramid standard: type checking cannot detect meetings that auto-close or winners shown too early. | **M.** Unit-test playback/store transformations and add one Playwright path: featured replay → play → meeting pauses → inspect → resume → finale; include keyboard and fog assertions. |
| **P2** | **[VERIFIED—read] Replay reconstruction is duplicated across API, evaluation, and training.** API projection walks state, kill-craft independently walks hashes, and no-replay training explicitly mirrors reconstruction assembly (`api/replay_loader.py:943-1250`, `eval/kill_craft.py:104-147`, `training/env.py:928-955`). | Single-source-of-truth/change-isolation standard. Multiple walkers require permanent parity tests and invite semantic drift. | **M.** Extract a typed replay-walk iterator with pluggable projections; migrate one consumer at a time. |
| **P2** | **[VERIFIED—read] Large modules obscure stable seams.** Meeting manager/transcript, game orchestrator, and replay loader are 2.8–3.8k lines (`meetings/manager.py:3780`, `meetings/transcript.py:3524`, `orchestrator/game.py:3143`, `api/replay_loader.py:2838`). | High cohesion and reviewability. | **M–L.** Split only after characterization tests: meeting rounds/ballots/result, replay walk/projections, API indexing. No broad rewrite. |
| **P2** | **[VERIFIED—read] CI lacks explicit least privilege and immutable action pins.** Workflow uses tag references and no `permissions` block (`.github/workflows/ci.yml:1-25`). | GitHub secure-use guidance. | **XS.** Set `permissions: contents: read`; pin action SHAs; deliberately deduplicate or partition frontend work. |
| **P2** | **[VERIFIED—read/run] Dependency/build hygiene needs a pass.** Test tools are runtime dependencies, a dead root lockfile describes no packages, Vite says SWC is unnecessary without SWC plugins, and npm install reported two unidentified high advisories (`pyproject.toml:7-21,48-51`, `package-lock.json:1-10`, `frontend/package.json:24-34`). | Least runtime surface and reproducible build hygiene. | **S.** Move dev tools to a dev group, remove the root lock, switch the React plugin if no SWC feature is needed, and have a human-authorized environment triage `npm audit` without automatically applying breaking upgrades. |
| **P3** | **[VERIFIED—read] Small duplication/dead-path cleanup remains.** GuidedTour reimplements the existing focus trap; application and picker can both issue initial list requests; `first_meeting` remains implemented/tested but active trainers request full games (`frontend/src/components/GuidedTour.tsx:300-358`, `frontend/src/hooks/useFocusTrap.ts:1-67`, `frontend/src/App.tsx:588-599`, `frontend/src/components/ReplayPicker.tsx:389-434`, `training/env.py:958-1056`). | Reduce incidental complexity after P0/P1 work. | **S.** Remove or consolidate only after confirming no external consumers. |

---

## 4. The ML implementation — frank retrospective

### 4.1 Verdict

**[JUDGMENT]** The ML direction worked as a bounded research and infrastructure exercise but did **not** work as a product-adoption program. It produced a functional corpus, reproducible compact models, strong serialization/fingerprint/parity discipline, and learned impostor arms with higher observed win rates; nevertheless all four Phase-18 learned impostor finalists failed the baseline-6 referee, no finalist across the retained comparisons cleared both the win-edge and referee bars, no crew policy was adopted, and the scripted FSM remains the default (`training/reports/results-finalist-eval.jsonl:3-11`, `training/reports/report-finalist-eval.md:1074-1165`, `scripts/run_tournament.py:160-175,279-295`).

**[JUDGMENT—Google's “keep the first model simple” standard]** With 33,220 source lines, 29,835 training-test lines, 1,588 tracked artifact files totaling 107.4 MB (102.4 MiB), and a final 449-game slate consuming 57.16 busy hours, another training wave has poor demonstrated marginal value (`training/reports/report-finalist-eval.md:998-1030`). [Google's Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml/) favors simple baselines and end-to-end product objectives over complexity without product gain. The retained value now lies more in evaluation, parity, and negative findings than in campaign machinery.

### 4.2 Functional core paths

1. **[VERIFIED—run] Corpus and artifact reading work.** All 200 ML-corpus games reconstructed; all checked sidecars/manifests matched. The split is by game, not meeting, preventing direct same-game meeting leakage (`replays/ml_corpus/README.md:91-102`).
2. **[VERIFIED—run] The ballot surrogate reproduces, but its decision channel is nonfunctional as a useful eject/skip classifier.** Ranking reaches 46/60 top-1, while the decision head predicts SKIP on all 96 test meetings and trails an always-eject baseline (`training/reports/report-ballot-surrogate.md:226-246,285-347`).
3. **[VERIFIED—run] The conviction model reproduces well on its actual label.** Flag-count Spearman is 0.5782 and conversion accuracy 0.9375 (`training/reports/report-conviction-model.md:180-218`). This is testimony-backed conversion classification, not final meeting-decision accuracy.
4. **[VERIFIED—run] The composed runner is the strongest meeting-level ML result.** Decision accuracy recomputes to 0.8646 and exact outcome to 0.7917 (`training/reports/report-composed-runner.md:118-167`). It remains an optional training configuration, and the report's Goodhart substrate has zero actual transcript flags/model provenance in its zero-LLM path (`training/reports/report-composed-runner.md:223-265`, `training/artifacts/composed/verdict.json:2-7`).
5. **[VERIFIED—read] Shipped learned inference is compact and firewall-safe.** The impostor path is a 19-weight pure-Python linear scorer with no engine/training import; bit-exact parity is an acceptance gate (`agents/tactical/learned/forward.py:1-35`, `tests/agents/test_learned_policy.py:250-270,377-406,458-518`). Preserve that engineering even if weights remain opt-in.

### 4.3 Ranked ML findings

#### P0 — the “policy-invariant” reward claim is mathematically false

**[VERIFIED—read/mathematics]** The code says that at gamma 1 the shaping sum `Phi(terminal) - Phi(initial)` “cannot change the optimal policy,” while defining Phi as cumulative kills or completed tasks (`training/rewards.py:18-24,82-100,136-143`). Its test proves only telescoping (`tests/training/test_rewards.py:153-168`). Because terminal kills/tasks vary by trajectory, the endpoint term varies and can change return ordering; episodic policy invariance needs terminal potential fixed/zero under the cited standard.

The objective also already rewards kills and unwitnessed kills, then adds cumulative-kill shaping with default weight 1, while terminal win/loss is only ±1 (`training/rewards.py:157-198,259-305`). The actual ES fitness consumes that total and treats watchability/validity as later filters (`training/bakeoff/harness.py:909-946`). **[SPECULATION]** This may contribute to evidence-starved policies—the objective rewards hidden kills while the referee requires evidence supply and conversion—but the committed experiments do not isolate causation (`training/reports/report-finalist-eval.md:1074-1107`).

**Disposition:** **XS–S** to correct code, tests, and claims; **XL** to retrain every dependent artifact. Because I recommend freezing ML, document the limitation and do not use Phase 19 to rerun the ladder.

#### P0 — the decisive finalist evidence is not reproducible from committed source bytes

**[VERIFIED—read/run]** The finalist report says raw recordings live outside the repository (`training/reports/report-finalist-eval.md:115-118`) and later names repo-external, uncommitted `~/ailibi-campaign-1826/scoring/...` sources (`training/reports/report-finalist-eval.md:1066-1070`); `git ls-files training/reports/_finalist_eval_raw` returned nothing. I did not verify whether those external paths still exist. The eleven flattened result rows preserve per-seed outcomes and arithmetic (`training/reports/results-finalist-eval.jsonl:1-11`) but cannot independently regenerate event extraction, tactical stamps, validity, or referee metrics.

This is backwards retention: **[VERIFIED—run]** the repository spends 107.4 MB (102.4 MiB) on 1,588 training-artifact files—dominated by 1,473 co-evolution files totaling 106.5 MB (101.6 MiB)—yet omits the 449-game source slate behind the adoption decision. **[JUDGMENT—experiment-lineage standard]** Preserve a content-addressed external artifact location plus manifest if raw games still exist; do not necessarily commit them. If lost, label event-level finalist conclusions non-reproducible rather than paying ~57 hours to repeat them during Phase 19 (`training/reports/report-finalist-eval.md:998-1030`).

#### P0 — ES cross-machine portability is unsupported and currently breaks the gate

This is the engineering finding in §3: same-host repeatability passes; the committed cross-machine golden is non-portable to this supported host (`training/bakeoff/es.py:19-26,184-193`, `tests/training/test_es.py:74-91`). **[JUDGMENT]** Treat reproducibility scope as a public contract: engine/replay determinism on the supported runtime is strong, while ES portability is not established beyond a pinned runtime. `gauss`/libm variation is the likely cause, not a root cause independently isolated here.

#### P1 — finalist point estimates omit paired uncertainty

**[VERIFIED—derived from committed same-seed rows]** Two-sided exact McNemar comparisons against FSM produced:

| Learned arm | Paired win-rate delta | Discordant learned wins / FSM wins | Exact p |
|---|---:|---:|---:|
| `ea4bc955` | +0.26 | 17 / 4 | 0.0072 |
| `bfd145cb` | +0.30 | 20 / 5 | 0.0041 |
| `6d327dcb` | +0.12 | 15 / 9 | 0.3075 |
| `7f73929d` | +0.1837 | 12 / 3 (49 seeds) | 0.0352 |

Thus “every arm beats the comparator” is true as an observed point estimate (`training/reports/report-finalist-eval.md:1082-1087`), but one arm shows no convincing paired advantage and the fourth does not survive Bonferroni over four comparisons (alpha 0.0125). **[JUDGMENT—paired-experiment standard]** Add paired intervals/exact tests to the existing result evaluator; **XS**, no new recordings.

#### P1 — screen instability was discovered late

**[VERIFIED—read]** Ten of 22 arms changed at least one win under retest; three referee passes were observed, but only one was retested and it failed to replicate (`training/artifacts/coevo/measurement-stability.json:2-13`, `training/reports/report-impostor-campaign.md:415-465`). The report itself says the first non-replication was misread as candidate noise and recording continued roughly another day before measuring instrument noise (`training/reports/report-impostor-campaign.md:460-465`). **[JUDGMENT]** This is a valuable negative result; preserve it as a stopping-rule lesson, not as a reason to build more screening infrastructure.

### 4.4 Keep, freeze, simplify, retire

| Decision | Components | Reason |
|---|---|---|
| **Keep** | Corpus verifier/splits; artifact hashes and fingerprints; replay reconstruction; referee/validity gates; compact learned readers; train/serve parity tests | **[VERIFIED—run/read]** These paths reproduced and protect real boundary/correctness properties (`replays/ml_corpus/README.md:91-102`, `agents/tactical/learned/forward.py:1-35`, `tests/agents/test_learned_policy.py:250-270,377-406,458-518`, `tests/training/test_learned_factory_acceptance.py:479-507,616-644`). |
| **Freeze** | Current corpus identity, weights, finalists, default FSM, opt-in learned surface | **[VERIFIED—read]** No learned arm clears both the retained win edge and referee bar, and no crew adoption occurred (`training/reports/report-finalist-eval.md:1074-1165`). Freeze means bug fixes/evidence readers remain allowed; no new search. |
| **Simplify** | One `verify-ml-evidence` command; report terminology; paired statistics; artifact index; ranking-only use of surrogate | **[VERIFIED—run/read]** Evidence currently requires several commands, README mislabels conviction accuracy, and standalone surrogate decision is all-SKIP (`README.md:69`, `training/reports/report-ballot-surrogate.md:285-347`). |
| **Retire/archive** | New ES/co-evolution arms, unused `first_meeting` boundary if no consumer exists, standalone decision runner, stale CLI example, bulky intermediate screens/derived reports | **[VERIFIED—read]** Active trainers use full games while the fallback remains (`training/env.py:958-1056`, `training/bakeoff/harness.py:665-723`, `training/crew/scorer.py:930-947`, `training/coevo/rollout.py:168-215`); the CLI advertises a crew directory it admits lacks the required stamp (`scripts/run_tournament.py:102-105,740-751,809-814`). Confirm external consumers before deletion. |

---

## 5. The games themselves

### 5.1 Corpus-level assessment

**[VERIFIED—run]** I parsed all 300 committed games through reconstructed truth, meetings, flags, ballots, and outcomes. The following are computed observations, not document claims; pacing counts recorded tick frames (`game_over.tick + 1`), and the source rows are the 50-game sample manifests and 50/150-game corpus sets (`replays/samples/4p1i/MANIFEST.md:12-61`, `replays/samples/9p2i/MANIFEST.md:12-61`, `replays/ml_corpus/README.md:1-19,91-102`).

| Set | Pacing/outcomes | Kill craft | Deduction shape |
|---|---|---|---|
| Sample 4p1i (50) | Median 12 ticks; 39 games have exactly one meeting; crew 33 (23 task, 10 eject), impostor 17 parity | 61 kills, one crew-witnessed | 10 correct ejections; nine direct-vent. Non-direct: 1/3 correct. |
| Sample 9p2i (50) | Median 34 ticks; median three meetings (max five); crew 35 (31 eject, four task), impostor 15 parity | 177 kills, six crew-witnessed | 101 ejections / 78 correct (77.2%); 68 correct ejectees were grounded vent-flag subjects. Non-direct: 10/33 correct (30.3%). Aggregate report corroborates ejection totals (`replays/samples/9p2i/tournament-eval-report.json:79744-79769`). |
| Corpus 4p1i (50) | Median 11 recorded tick frames; 40 games have exactly one meeting; crew 39 (20 eject, 19 task), impostor 11 parity | 55 kills, none crew-witnessed | 20/20 correct ejectees were grounded vent-flag subjects; no non-direct conviction. |
| Corpus 9p2i (150) | Median 27 recorded tick frames; every game has meetings; crew 112 (106 eject, six task), impostor 38 parity | 505 kills, 12 crew-witnessed | 302 ejections / 248 correct (82.1%); 213 correct ejectees were grounded vent-flag subjects. Non-direct: 35/89 correct (39.3%). Aggregate report corroborates totals (`replays/ml_corpus/9p2i/tournament-eval-report.json:224645-224670`). |

Across all four sets there are 798 kills and 19 crew-witnessed (2.38%); at the evaluator's pre-advance decision frame, every kill had zero non-victim crew co-present. The committed kill-craft pins show 505/12 for corpus 9p, 177/6 for sample 9p, and 61/1 for sample 4p (`tests/eval/test_kill_craft.py:66-135`); the fourth-set parse adds 55/0. Rare same-tick one-hop arrivals explain the 19 witness cases (`eval/kill_craft.py:23-46`).

### 5.2 Ranked gameplay findings

#### P0 — headline deduction is dominated by cases containing direct role proof

**[VERIFIED—run/read]** In sample 9p, the ejectee is the subject of a grounded `vent_sighting` flag in 68/78 correct ejections (87.2%); in corpus 9p it is 213/248 (85.9%). I matched reconstructed role truth and the ejected player to `meeting.contradictions[kind="vent_sighting"].subjects`; the served DTO carries the required kind/subjects and ejected-player fields (`api/schemas.py:583-610,696-724`). The prompt explicitly teaches that witnessed venting proves impostor identity and must be repeated (`agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:173-190`), while observation delivery is correctly witness-gated (`observation/service.py:395-414`).

**[JUDGMENT—social-deduction standard]** The inspected meetings show coherent use of vent proof, but aggregate matching establishes co-occurrence rather than ballot-level causation. The 77–82% correctness headline therefore overstates what is demonstrated about inference: among ejections without ejectee-specific vent proof, accuracy is only 30–39%. Preserve venting, but report proof-present and non-direct performance separately before changing mechanics.

#### P0 — the deterministic impostor is clean but too clean

**[VERIFIED—read/run]** The default policy kills only a colocated isolated target and, after a clean unwitnessed kill, prefers a vent when one is available in the body room and otherwise moves away (`agents/tactical/impostor_policy.py:38-50,76-83,93-116`). That produces essentially zero messy co-present kills across 300 games. **[JUDGMENT]** This is competent tactical craft and makes replay causality legible, but it starves the testimony economy and makes the policy visibly scripted. Do not merely increase randomness; introduce bounded risk/ambiguity and measure evidence supply.

#### P1 — meetings are structurally excellent but semantic consistency is not guaranteed

**[VERIFIED—run]** Sample 9p contains 971 transcript turns and 971 ballots, with zero exact repeated free texts, median free text 42 words, zero within-meeting echo, 0.957 distinct skeleton ratio, and 520/520 eject ballots with valid citations. Corpus 9p contains 2,726 turns, zero echo, 0.916 skeleton ratio, and 1,574/1,578 cited eject ballots; the instrument reconstructs structured citations and voice/judgment measures (`eval/vj_instruments.py:10-83,270-340`).

**[JUDGMENT—structured-output hygiene]** The voice variety, observation grounding, and citation compliance are unusually strong and should be preserved. Citations prove traceability, not that a turn, flag, ballot target, and rationale agree: seed 42 and seed 47 demonstrate that gap below.

#### P1 — public response shape remains role-correlated

**[VERIFIED—run/read]** Roll-call response coverage is about 99.6% crew versus 45.5% impostor in sample 9p and 99.7% versus 46.5% in corpus 9p. Default impostor templates intentionally hard-code empty observations, while the answer-capable lever remains optional (`agents/strategic/prompts/qwen3_6_27b/impostor_report.j2:28-36,100-111`, `agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:21-46`, `agents/strategic/prompts/loader.py:183-239`).

**[JUDGMENT—hidden-information game standard]** This template-induced, role-correlated behavioral tell matters even if an absence prior intentionally prices it; it is not an observation-firewall leak. Equalize the public response shape and constrain lies rather than suppressing impostor answers; validate win/watchability before adoption.

### 5.3 End-to-end game reads

#### High tail — sample 9p seed 2

**[VERIFIED—run/read]** This is a 36-tick, four-meeting crew ejection win and the fresh HEAD watchability fold's top game within sample 9p (89.9; see the method table). The committed stale rubric instead ranks it third at 80.4 and names an older Git head (`replays/samples/9p2i/results-rubric-score.json:3,44-55`). A kill lands at tick 4 and the first meeting is recorded at line 9; crew identify actual impostor p-7 from isolation but mostly skip. Meeting two ejects p-4 after p-8 directly sees a vent; meeting three puts two votes on p-7 but ties SKIP; the last meeting ejects p-7 after another direct vent, then ends the game (`replays/samples/9p2i/replay-seed-2.jsonl:5,9,17,23,40-41`).

**[JUDGMENT]** This is watchable: it has a cold open, early suspicion, one resolved villain, a near miss, and a final reveal. It is weak evidence for genuine deduction because both decisive convictions are role-proof vents.

#### Median — sample 9p seed 11

**[VERIFIED—run/read]** This inspected median-score game contains frames 0 through 15 (16 recorded frames) and three meetings. P-3 kills p-2 at tick 7, vents, is seen and ejected at the first meeting (`replays/samples/9p2i/replay-seed-11.jsonl:8-11`); the second meeting wrongly ejects crew p-9 on a location lie (`replays/samples/9p2i/replay-seed-11.jsonl:16`); the third ejects partner p-7 after p-8 sees another vent, producing a crew win (`replays/samples/9p2i/replay-seed-11.jsonl:19-20`). The first private ballot also contains the out-of-character “p-3 is my partner” rationale (`replays/samples/9p2i/replay-seed-11.jsonl:11`).

**[JUDGMENT]** This median-score selection is watchable: it has a coherent arc and agents who use hard evidence, alongside one plausible but wrong inference and a private-reasoning seam. It is much shorter than the sample-9p median duration, so I do not treat it as representative of median pacing; its interesting ambiguity is in the middle, not in the decisive votes.

#### Low tail — sample 9p seed 47

**[VERIFIED—run/read]** Four isolated kills lead to a 34-tick, three-meeting impostor parity win. The first two meetings skip (`replays/samples/9p2i/replay-seed-47.jsonl:6-17`); the final meeting ejects innocent p-8 and immediately reaches parity (`replays/samples/9p2i/replay-seed-47.jsonl:37-38`). The opener accuses p-8, three other turns accuse p-7, and p-4 explicitly corroborates p-8, yet p-4 and others flip to p-8 after weak inclusive-window flags.

**[JUDGMENT]** This tail is not coherently watchable: weak structured flags overpower the conversation, and a corroborating voter reverses without a narrative bridge. It is exactly the failure a turn→ballot consistency metric should catch.

#### Compact failure — sample 4p seed 42

**[VERIFIED—run/read]** P-3 kills p-2 at tick 5, vents, and the body is reported at tick 12; the only meeting skips; p-3 kills p-1 at tick 14 and wins parity (`replays/samples/4p1i/replay-seed-42.jsonl:6-8,13-17`). At the meeting p-4 accurately cites seeing p-3 in Storage at the kill tick and accuses at 0.75, then ballots SKIP claiming p-3 was with them in Engineering; p-1 says p-3's alibi holds although p-3 supplied none (`replays/samples/4p1i/replay-seed-42.jsonl:14`).

**[JUDGMENT]** This is compact proof that schema-valid structured turns/observations and grounded fields can coexist with incoherent semantics; its three SKIP ballots have no citation IDs. Four-player games remain valuable fast fixtures, but with median 12 ticks and usually one meeting they are a poor portfolio default.

### 5.4 Is it watchable, and does the frontend help?

**[JUDGMENT]** The inspected median-score 9p game is watchable with manual stepping; the 4p median is not a satisfying spectator product. The tails range from a strong four-act seed 2 to a flag-driven seed 47 failure. The internal watchability score is useful for selection, but its own code calls the construct fuzzy and Goodhart-prone, so it must not be presented as a human rating (`eval/watchability.py:9-20,53-57,1965-1973`).

**[VERIFIED—run/read]** The frontend makes causal inspection much easier through key-moment jumps, transcript/ballot panels, fog, mind snapshots, and Belief × Truth (`frontend/src/lib/playback.ts:170-320`, `frontend/src/components/GuidedTour.tsx:147-227`, `frontend/src/components/MeetingView.tsx:96-293`). It makes passive watching harder because default 1× autoplay with auto-follow gives a meeting one 500 ms frame, while immediate winner display, no ending, mixed pre/post frame semantics, misleading evidence labels, and a stale highlight rubric add further friction (`frontend/src/hooks/usePlayback.ts:304-382`, `frontend/src/App.tsx:252-301`, `api/replay_loader.py:1172-1205`, `frontend/src/components/MeetingView.tsx:303-383`, `frontend/src/components/ReplayPicker.tsx:284-290`, `replays/samples/9p2i/results-rubric-score.json:3,44-55`).

---

## 6. Anything else

### 6.1 P0 — reproducibility has three scopes, and the repo conflates them

**[JUDGMENT]** Phase 19 should name three contracts separately:

1. **Replay integrity:** committed bytes reconstruct through current engine hashes—**verified strong** (`scripts/_verify_samples.py:164-304`).
2. **Same-runtime repeatability:** same seed/config/provider response produces identical bytes—**verified for fake provider** (`README.md:73-86`).
3. **Cross-platform numerical portability:** independent supported hosts produce the same learned optimizer bytes—**the committed ES golden is non-portable to this supported host** (`training/bakeoff/es.py:19-26,184-193`, `tests/training/test_es.py:74-91`); `gauss`/libm variation is likely but was not independently isolated.

This distinction preserves the valid core claim without laundering a narrower failure into a general “determinism is broken” statement.

### 6.2 P1 — the roadmap is directionally right but lacks an executable Phase 19 contract

**[VERIFIED—read]** The roadmap says Phase 19 is review-and-refresh, not features, and explicitly excludes a human seat and heterogeneous-model lobby (`tasks/post-phase-14-plan.md:108-114,187-193`); Phase 18 routes review inputs to it (`tasks/phase-18.md:25-35`). At audited HEAD there is no `tasks/phase-19.md`, even though repository workflow says every coding task begins from a phase contract (`README.md:17-30`).

**[JUDGMENT]** That absence is appropriate while collecting independent audits, but implementation should not start as an unbounded cleanup branch. Convert the accepted findings into scoped contracts with explicit files, tests, migration rules, and evidence-preservation constraints.

### 6.3 P1 — the local-only security stance is good; a portfolio deploy must not bypass it

**[VERIFIED—read]** The spectator is an unauthenticated privileged view and documentation clearly limits it to loopback or an authenticated isolated proxy (`docs/deployment.md:10-32`). Docker publishes only host loopback (`docker-compose.yml:31-37`). **[JUDGMENT]** A hosted portfolio demo should serve precomputed sanitized/static replay data or add an actual trust boundary; changing `0.0.0.0` alone would be a security regression.

### 6.4 P2 — repository weight and evidence retention should be solved together

**[VERIFIED—run/read]** Current Git holds large derived tournament reports and many intermediate screens, yet the final decision slate's raw source is not committed; the report points to repo-external working paths whose current existence I did not verify (`training/reports/report-finalist-eval.md:115-118,1066-1070`). **[JUDGMENT]** Do not simply delete big files. Define artifact classes: (a) tiny canonical fixtures in Git, (b) manifests/hashes/summary rows in Git, (c) large immutable replays/reports in addressable release/object storage, and (d) disposable regenerated views; then migrate forward without a casual history rewrite.

---

## 7. Phase 19 recommendation

The charter is correct that this must not be a feature phase (`tasks/post-phase-14-plan.md:108-114,187-193`), but “frontend/data-display refresh” is too easy to interpret as cosmetics. **[JUDGMENT]** Phase 19 should be a **truth, evidence, and spectator-coherence release** with the following ordered work.

### P0 — restore trustworthy foundations

1. **Portable green gate.** Replace/specify ES Gaussian sampling or narrow and pin its support contract; make `bash scripts/check.sh` green on the supported matrix (`training/bakeoff/es.py:184-193`, `tests/training/test_es.py:74-91`).
2. **Repository truth sweep.** Reconcile `DESIGN.md`, `AGENTS.md`, `.env.example`, README phases/stats/provider/baseline, runtime ownership, and live flags; add small consistency checks (`DESIGN.md:1-17`, `AGENTS.md:14-24,64-79`, `README.md:13,46-104`). Correct “conviction decision accuracy” and explicitly distinguish point estimates from evidence of advantage (`README.md:69`, `training/reports/report-conviction-model.md:190-199`).
3. **Author Phase 19 contracts.** Turn accepted audit findings into small branches with explicit scope; do not allow a single review/refactor mega-PR (`README.md:17-30`).

**Exit:** green full gate, no known authoritative-doc/code contradiction, generated/checkable public metrics.

### P1 — make the spectator tell one coherent game

1. Default/landing path is a freshly rescored curated 9p game; 4p is labeled a fast technical fixture (`api/replay_loader.py:2644-2659`, `frontend/src/components/ReplayPicker.tsx:18-24`).
2. Add unspoiled mode, pause on meetings, Resume/next beat, and a real game-over reveal/summary (`frontend/src/App.tsx:252-301`, `frontend/src/hooks/usePlayback.ts:304-382`).
3. Separate pre/post meeting snapshots and evidence flags from contradictions (`api/replay_loader.py:1172-1205`, `meetings/schemas.py:423-460`).
4. Add one critical Playwright journey plus playback/store component tests; keep existing keyboard/fog/a11y behavior (`frontend/package.json:6-34`, `frontend/src/hooks/useFocusTrap.ts:1-67`, `frontend/src/index.css:183-198`).
5. Put a screenshot/capture and current reproducible claims above the README fold (`README.md:1-13,73-104`).

**Exit:** a new visitor can watch seed 2 or another curated game from start through readable meetings to an unspoiled resolution; the same journey is automated.

### P1 — repair what “deduction” means before tuning gameplay

1. Add first-class direct-vent versus non-direct ejection accuracy, weak-flag-only conviction, and same-agent turn→ballot consistency metrics (`meetings/schemas.py:442-460`, `eval/vj_instruments.py:270-340`).
2. Reclassify grounded vents as proof/evidence, not contradiction links; prevent weak interval flags alone from driving unexplained ballot flips (`meetings/transcript.py:2880-2906`, `frontend/src/components/MeetingView.tsx:317-383`).
3. Remove secret teammate/self-kill phrasing from private ballot rationales without hiding the fact that a guard changed a vote (`meetings/manager.py:1906-1913,2893-2925`).
4. Prototype equal response shape for crew/impostors behind a measured gate; do not blindly enable it (`agents/strategic/prompts/loader.py:183-239`).

**Exit:** dashboards distinguish role proof from inference, and seed-42/47-style semantic failures are detectable by tests/metrics.

### P1 — close the ML evidence program, do not extend it

1. Correct the false reward-invariance claim and record its implication without retraining (`training/rewards.py:18-24,82-100,136-143`).
2. Recover/content-address the finalist raw slate if it still exists; otherwise mark its event-level lineage unavailable (`training/reports/report-finalist-eval.md:115-118,1066-1070`).
3. Add one read-only evidence command for hashes, corpus verification, surrogate/conviction/composed recomputation, and paired finalist statistics.
4. Freeze default FSM/corpus/weights; retain compact inference, parity, evaluator, and validity code; archive unused runners and bulky intermediate artifacts only with manifests (`scripts/run_tournament.py:160-175,279-295`, `agents/tactical/learned/forward.py:1-35`).

**Exit:** every published ML number states label, split, uncertainty, and source-artifact availability; one command verifies all evidence possible from committed/addressed bytes.

### P2 — surgical maintainability and public hygiene

1. Extract a common replay walker/projection seam, then split meeting/replay monoliths under characterization tests (`api/replay_loader.py:943-1250`, `eval/kill_craft.py:104-147`, `training/env.py:928-955`).
2. Fix CWD-dependent API roots and runtime DTO-version rejection (`api/main.py:24-27,85-112,152-188`, `frontend/src/api/client.ts:36-55`).
3. Partition dev/runtime dependencies, deduplicate CI, pin actions/permissions, remove dead lock/duplicated focus/fetch paths (`pyproject.toml:7-21,48-51`, `.github/workflows/ci.yml:1-57`, `package-lock.json:1-10`).
4. Choose a license and add minimal contribution/security posture before public promotion.
5. Move large replaceable artifacts out of ordinary Git while keeping canonical replay fixtures and content manifests.

### Explicitly out of Phase 19

- **No human seat, heterogeneous-model lobby, live WebSockets, database, or other feature expansion.** This matches the owner charter (`tasks/post-phase-14-plan.md:108-114,187-193`).
- **No new ES/co-evolution method, feature family, surrogate re-grounding, 450-game slate, or more corpus volume.** Existing finalists did not clear the joint bar (`training/reports/report-finalist-eval.md:1074-1165`).
- **No broad engine rewrite, frontend framework migration, or monolith split for its own sake.** The engine's executed invariants are strong and the current frontend is manually usable; this audit did not profile render performance. Extract only tested seams (`engine/tick.py:565-651`).
- **No tuning the current watchability scalar as a proxy for human interest.** First fix the viewing path and instrument proof versus inference; the scorer is explicitly fuzzy/Goodhart-prone (`eval/watchability.py:9-20,53-57,1965-1973`).
- **No appearance-only refresh before narrative correctness.** Color and component polish are already a strength; unreadable meetings, spoilers, mixed-time frames, stale scores, and misleading labels are the higher-impact display defects (`frontend/src/hooks/usePlayback.ts:304-382`, `api/replay_loader.py:1172-1205`, `frontend/src/components/ReplayPicker.tsx:284-290`).

## Final recommendation

**[JUDGMENT]** Proceed with Phase 19, but treat it as a release-quality correction pass, not a victory lap and not another research phase. AiLibi's best assets—the deterministic engine, observation firewall, replay evidence, structured memory, and inspectable viewer—are strong enough to preserve and present; its biggest risks are now credibility gaps between those assets and the claims, metrics, defaults, and UI semantics around them. A successful Phase 19 ends with one green command, one truthful README, one excellent watch-through, one reproducible evidence command, and a smaller clearly frozen ML surface.
