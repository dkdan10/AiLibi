# Independent audit — Phase 19 input (Claude)

**Date:** 2026-08-02. **Auditor:** Claude (Fable 5), running independently against `main` @ `48925e7e` (task 18.28 close, #319).
**Method:** everything below was produced this session from a fresh clone: the full gate was run end-to-end, the determinism and sample-verification claims re-executed, the spectator UI booted and screenshotted headlessly, the opt-in learned champion exercised, the referee CLI run against committed bytes, and the full module surface read by a fan-out of twelve specialist review passes whose every [VERIFIED] claim carries a file:line citation (a sample of which I re-checked by hand). `[VERIFIED]` = I or a review pass ran/read the artifact directly; `[JUDGMENT]` = inference or opinion, labeled as such. Docs, audits/, tasks/, and training/reports/ were treated as claims and checked against code and bytes throughout.

---

## 0. Executive summary

**What this is.** A three-month, 837-commit, ~315-merged-PR experiment in agent-built software that produced a genuinely working artifact: a deterministic social-deduction simulator with a real observation firewall, an LLM meeting layer with typed, citation-gated deliberation, a 100-game committed replay corpus, a polished spectator frontend, and a four-phase ML program that was honestly measured and honestly did not ship a default policy change.

**Overall state: mechanically excellent, self-description decaying.** [VERIFIED] The full gate is green from a cold clone (`check.sh`: ruff, import-linter, task-doc byte-sync, mypy --strict, **4,531 passed / 20 skipped / 3 xfailed**, frontend tsc + build). Determinism reproduces (same seed → byte-identical replay; all 100 committed samples reconstruct clean). The firewall holds under adversarial reading and is enforced by planted-leak tests that prove the gates can fail. The opt-in champion loads, sha-verifies, and plays. Against that: the project's *prose* — README headline numbers, DESIGN.md, AGENTS.md, in-code docstrings about which levers are live — has measurably drifted from the bytes, in places to the point of being flatly false, and the audit corpus that holds the project's institutional memory has crossed a legibility cliff that makes it nearly unreadable to outsiders.

**Top strengths (preserve at all costs):** (1) the determinism/firewall/provenance discipline — real, tested, and rare; (2) the test *instruments* — the leak property sweep, the prompt byte-golden, gates-that-prove-they-can-fail; (3) the spectator frontend + self-contained replay format — far better than the README admits, and the natural portfolio centerpiece; (4) the negative-result culture — two phases closed NO-FLIP with the losing evidence published in full.

**Top risks:** (1) prose drift is now systemic — the repo's primary defense is documentation, and the documentation is the least-maintained artifact in it; (2) the closed ML program's weight (~63k LOC training code+tests, ~330MB committed artifacts, growing pin-test families) taxes every clone, every gate run, and every future change; (3) the flagship UI has zero tests and no deploy path; (4) the front door (README/DESIGN) undersells the strongest work and misstates the current state.

**Phase-19 recommendation in three sentences.** The review-and-refresh charter is correct — this codebase needs consolidation and presentation, not features — but it should be executed as *truth reconciliation plus demo investment*, not as another round of instrument rigor. Priorities: (a) reconcile every stale claim (README, DESIGN.md, AGENTS.md, .env.example, in-code lever docstrings, the dashboard's "gate bug" badge) against bytes; (b) spend the frontend budget on the watchability quick wins (end-of-game card, event ticker, cost surfacing, the one-line contrast fix) plus a deployable static demo, a vitest baseline, and a linter; (c) formally freeze the ML program — tier its tests out of the default gate, prune ~200MB of closed-campaign artifacts to an evidence branch/LFS, and label the frozen subpackages — while keeping the live seam (env, ES core, champions, referee) intact. Phase 19 should explicitly *not* fund: new game mechanics, another training campaign, further referee/floor machinery, or more audit formalism.

---

## 1. What I ran (verification record)

All commands executed this session on a fresh clone; logs retained.

| Check | Result |
|---|---|
| `bash scripts/setup_env.sh` | exit 0 |
| `bash scripts/check.sh` (full gate) | exit 0 — ruff, ruff format, lint-imports, validate_task_docs (293 contracts ↔ 293 prompts), generate_prompts --check, mypy --strict, pytest **4531 passed / 20 skipped / 3 xfailed in 595s**, frontend `tsc` + `vite build` |
| `run_game.py --seed 42` twice + diff | **byte-identical** |
| `bash scripts/verify_samples.sh` | **100/100 samples reconstruct clean** (both sets) |
| `run_tournament.py --agent-factory learned-champion` (3 games, 9p2i, fake provider) | runs, $0; champion loads + sha-verifies |
| `measure_baseline.py --watchability` (both canonical sets) | referee PASS; floors pass **at exact equality** (floors are pinned from these bytes — see §6) |
| Spectator UI (uvicorn :8000 + vite :5173, headless Chromium) | boots; six screenshots captured; all views render |
| GitHub history | 837 commits 2026-05-01→2026-08-02; 315 merged PRs (GitHub API; 311 unique in main history), latest #319 |
| Weight artifacts | shipped champion sha `6d327dcb…` verifies; all 296 training sidecars verify; 231/231 campaign recordings match manifests |

The project's three headline claims — byte-exact determinism, a leak-free observation firewall, and a CI-enforced contract→prompt pipeline — all **survive adversarial verification**. That should be said plainly before any criticism: the hard invariants this project sells are real.

---

## 2. Project state

### 2.1 Architecture — the shape is right

[VERIFIED] The layering (engine → observation → agents/meetings ← orchestrator, llm behind a Protocol, eval/api privileged, frontend on generated types) is coherent and *enforced*, not aspirational: `.importlinter` forbids `agents → engine` (direct and transitive) plus `agents → training`; grep confirms `agents/`, `meetings/`, `llm/` contain zero engine imports; adversarial fixtures prove the linter trips (`tests/test_firewall.py:133-157, 205-225`). The engine tick is genuinely pure (frozen dataclasses, `MappingProxyType`, no wall-clock/unseeded randomness anywhere in engine/observation/orchestrator — checked by grep and read). The two-tier agent design (deterministic FSM movers, LLM only at meetings) is real at the mechanism level.

Notable architectural achievements worth naming:
- **The observation firewall is three-layer enforced** [VERIFIED]: scripted fixture sweep with recursive field/value scanners + key-set pins, a Hypothesis property sweep that *imports* the production scanners rather than reimplementing them (`tests/observation/test_leak_property.py:59-66`), and a factory-mode scan over reconstructed production games — with planted-leak self-tests proving each scanner bites (`eval/leak_test.py:380-445, 831-889`). The impostor pretend-task design (structural sentinel never minted into world state; camouflage window sorted to kill an ordering tell — `observation/service.py:174-192`) shows genuinely adversarial thinking.
- **Provenance engineering** [VERIFIED]: sha-sidecars on every weight artifact (296/296 verify), stamps read back from recorded bytes rather than echoed from config, MANIFEST rows carrying model/prompt-versions/flags/git-sha per sample, and replay corruption detection (doubled-tick/doubled-game-over fail-loud, `orchestrator/replay.py:1137-1187`).
- **The bit-exactness discipline on the learned path** [VERIFIED]: `math.fsum` with do-not-simplify warnings, float64-hex lossless weight serialization, sha-verified loads (`agents/tactical/learned/forward.py:21-24`, `weights.py:35-45`).

### 2.2 Module health (condensed; full grades in the fan-out reviews)

| Area | LOC | Verdict |
|---|---|---|
| engine/ | 2,293 | A−. Pure, disciplined. Debt: an RNG apparatus whose draws are never consumed yet was performance-optimized (E1 below); dead schema fields; one-map reality vs multi-map schema. |
| observation/ | 1,107 | A−. The firewall is real. One coverage gap: `moved_players` witness-gating has zero leak-suite coverage (§4 item 12). |
| orchestrator/ | 5,056 | B−. Quality parts aggregated into a 3,143-line god module (`orchestrator/game.py`) with a ~370-line inline prompt-version process ledger. |
| agents/ | 11,151 | B+. Mechanically excellent (suspicion provenance math, render budgeting); prose decayed — two docstrings flatly false (below). |
| meetings/ | 8,426 | B. Guard-chain design is textbook; 3,780-line manager; duplicated vote-tally logic vs the declared "canonical home" (`meetings/voting.py:38-48`). |
| llm/ | 3,444 | A−. Best package in the repo; Protocol boundary absorbed three provider migrations. Two real defects (undeclared httpx dep; silent fallback pricing). |
| eval/ | 17,046 | B−. Powerful instruments (circularity engineered out; metrics ship their own caveats as pinned JSON fields; the referee has a real adversarial-integrity model) + heavy structural debt: the replay-reconstruction walk duplicated **~8×** inside eval/ alone (each copy enforcing a *different* subset of integrity checks — `eval/watchability.py:1186`, `validity.py:344`, `funnel.py:287` and `:1138`, `kill_craft.py:474`, `off_menu.py:431`, `win_condition_selfcheck.py:191`, `balance_eval.py:760`, `leak_test.py:593` — the project's own Phase-19 hand-off admits three); 30 hardcoded floor constants across five baseline blocks in a 2,276-line `watchability.py`; two load-bearing metrics regex-scraping their inputs out of rendered LLM prompt text with *silent* skip-on-mismatch (`eval/_suspicion_parse.py:42-44`, `meeting_quality.py:276-283` — contradicting the no-silent-fallback doctrine); roughly half the package (~8.8k LOC) frozen ML-referee apparatus with no live consumer. |
| api/ | 4,446 | B+. Thin routes, DTO firewall with redaction-by-revalidation; one 2,838-line loader flagged (accurately) by the roadmap for decomposition. |
| scripts/ | ~10k | B. Load-bearing core is tested and solid; ~2.2k lines of bash implementing a concurrent work-queue is the most fragile artifact in the repo; several dead one-shots. |
| training/ + experiments/ | 49,825 | Functional but concluded — see §6. |
| frontend/ | ~15.5k | B+ code, A− product. Zero tests, no linter, no deploy path; excellent type-codegen, URL-state, a11y, fog enforcement. |
| tests/ | 127,034 | Instruments world-class; weight problems structural (§4 items 10–11). |

### 2.3 Genuinely good — the things a Phase-19 sweep must not break

1. [VERIFIED] The leak property sweep (`tests/observation/test_leak_property.py`) — Hypothesis drives real ticks + real packet builds and asserts invariants the generic scanners can't (crew-empty `fellow_impostor_ids`, own-task-only derivation, `own_kill` confined to one JSON path).
2. [VERIFIED] The prompt byte-golden (`tests/meetings/test_prompt_byte_golden.py`) — re-runs every committed meeting of ~100 replays through the *real* MeetingManager keyed on exact prompt strings, with coverage floors asserting every recorded call was consumed. The strongest prompt-regression instrument I have seen at this scale.
3. [VERIFIED] The prompt-regression close gate (`tests/eval/test_prompt_regression.py`) proves the loop (change moves exactly one metric, attributably) rather than just pinning numbers.
4. [VERIFIED] The type-codegen pipeline to the frontend, including `api.fidelity.ts` generated by running a real game through the production writer/loader and type-checking the payload under tsc (`scripts/gen_frontend_types.py:339-443`) — above industry standard.
5. [VERIFIED] Hermeticity: an autouse fixture pins the fake provider for every test (`tests/conftest.py:33-37`); CI spends $0 and touches no network.
6. [VERIFIED] The single-seam training interposition (`training/env.py:399-553`): training drives the *real* `HeadlessGame` with the real firewall; `intent_selector=None` is byte-identical to production. This is why the ML findings transfer at all.
7. [VERIFIED] The contract→prompt→CI pipeline (293 contracts byte-mirrored, parallel-scope overlap detection) — the load-bearing machinery of the whole experiment, in good shape.

### 2.4 The bad — cross-cutting

**The single systemic defect of this codebase is prose drift.** The project's method makes in-code prose a first-class control surface ("docs are claims, code is truth" is its own doctrine) — and that surface has measurably decayed:

- [VERIFIED — flatly false docstrings] `agents/memory/beliefs.py:916-928` and `:1102-1116` declare `PlayerBelief.alibis`/`record_alibi` "DEAD in production today … zero non-test callers"; production writes it at `agents/memory/store.py:539` (from `orchestrator/game.py:2275`) and renders it at `store.py:1664-1709` — live since Task 13.5.2. I re-checked this by hand.
- [VERIFIED] Nine graduated levers' interior docstrings still claim "default-OFF" while their resolvers hard-return `True` (e.g. `agents/memory/beliefs.py:1396-1398` vs `:183-197`; `meetings/transcript.py:2386, 2918-2920` vs `:1360-1409`; `meetings/manager.py:294-303` et al.).
- [VERIFIED] `orchestrator/game.py:12-13` claims "the orchestrator is the only non-engine module that imports engine" — false (training/ imports engine in 24 files; eval/, api/, scripts/ too). The *true* invariant (agents/meetings/llm engine-free) holds and is the one that matters.
- [VERIFIED] `.env.example` documents six retired levers as "LIVE default-OFF" and omits the only live one (`AILIBI_IMPOSTOR_ROLL_CALL` — zero hits in the file).
- [VERIFIED] `llm/README.md` lists two providers; the code has four, and the canonical one (Featherless) isn't mentioned.
- README/DESIGN/AGENTS staleness is covered in §3 (it is the portfolio's front door).

This is not cosmetic. In an agent-built repo, stale prose is *actively misleading to the next agent* — an auditor or implementer trusting `beliefs.py`'s docstring would mislabel live code as dead. The failure mechanism is structural: doc refresh happens only when a close contract names the paragraph, so any prose not named rots silently [VERIFIED mechanism: the README sample-provenance paragraph survived two record PRs and a close PR that each updated adjacent text].

Second cross-cutting item: **comment mass as maintenance liability** [JUDGMENT]. `meetings/manager.py` and `orchestrator/game.py` are more than half prose; `training/` carries a 0.51 doc:code ratio with hundreds of cross-file line-number citations that already rot (`training/coevo/factory.py:10-13` cites `harness.py:531-609`; actual location 548). The archaeology is genuinely valuable — but the project needs a convention that *rewrites interior docstrings on lever graduation* and keeps campaign history in reports, not code.

---

## 3. Portfolio assessment

### 3.1 The strongest story

[JUDGMENT] This project has three candidate stories, in descending order of distinctiveness:

1. **The workflow experiment** — 300+ agent-authored PRs under CI-enforced contracts, with byte-mirrored prompts, checkpoint audits, and architecture that survived three months of agent pressure. This is the rarest artifact and the one no one else has. But it is currently told worst: the README's headline numbers are stale, and the evidence corpus (audits/) is unreadable to outsiders (below).
2. **The simulator + spectator** — "watch AI agents accuse each other, with the receipts": deterministic replays, typed transcripts where every claim cites an observation id, a belief-vs-truth matrix, an interestingness-ranked highlight reel. Immediately demoable, visually distinctive, and *already built*.
3. **The ML program as honest science** — four phases, pre-registered bars, a no-ship conclusion published in full. Impressive to a narrow audience; needs a 2-page summary, not 27k lines of audits.

The right portfolio posture leads with 2 (the demo is the hook), uses 1 as the differentiator, and links 3 as depth.

### 3.2 The five-minute test — what a stranger sees today

[VERIFIED, by doing it] Cloning and running `bash scripts/setup_env.sh && bash scripts/run_spectator.sh` works as documented and lands in a genuinely impressive UI: a guided tour ("two truths at once"), auto-loaded high-interest replay, map with bodies/vents/kill flashes, event timeline with an advantage curve, "Next key moment" navigation, an Omniscient/As-agent perspective toggle enforcing fog honestly, per-meeting Belief × Truth matrix, a Highlights reel, and a Tournament dashboard. **The README's "intentionally minimal — function over polish" (README.md:104) is false modesty that costs real credit** — it describes the pre-Phase-12 UI.

What undermines the first five minutes, in order:
1. **No hosted demo.** The flagship surface requires a local two-process dev setup ([VERIFIED] `vite build` output is never served; FastAPI mounts no StaticFiles; `scripts/run_spectator.sh` runs the *dev* server). For a portfolio repo in 2026, a static deploy of the built frontend + a small hosted API (or pre-baked JSON) is table stakes.
2. **A stale, self-contradicting README.** [VERIFIED] README.md:13 says "219 merged PRs … ~2,500 passing tests" (actuals: 311–315 merged PRs, 4,531 tests). README.md:48 names baseline 6 the ladder tip while README.md:100 says "these baseline-5 sets remain the ladder tip," with the wrong refresh date (2026-07-14 vs actual 2026-07-20) and wrong win rates (claims 30%/36%; committed bytes: 4p1i 17/50 = **34%**, 9p2i 15/50 = **30%** — I parsed the `game_over` records myself). Two paragraphs after declaring "each set's MANIFEST.md is the canonical provenance record," the README loses to its own manifest.
3. **A 350MB clone.** [VERIFIED] 222MB replays + 111MB training artifacts (109MB of which is closed-campaign co-evolution intermediates across 1,473 files). The first impression of `git clone` is a several-minute wait.
4. **DESIGN.md as the advertised architecture doc.** [VERIFIED] AGENTS.md:16 calls it authoritative; it ends its roadmap at Phase 6, lists RL "out of scope" against a 33k-line training package, names the wrong canonical provider and the wrong sabotage inventory. Its header honestly declares the vintage (2026-05-30), but a stranger sent there by the README reads a description of a project twelve phases ago.
5. **The audit corpus's legibility cliff.** [JUDGMENT, accuracy of underlying docs VERIFIED by ~40 spot-checks] Early audits are readable and even gripping; the phase-18 close is case law — self-referential citation idiom ("the 15.18 convention", "F10–F13", "§1.3 bar") with no glossary anywhere in the repo. Every spot-checked number reproduced exactly; the problem is purely density. The strongest single asset (the honesty machinery: errata that disown their own headline figures, "recorded, not repaired" discipline, 0/14 pre-registered emergence reported without goalpost movement) is invisible behind the idiom.

### 3.3 Recommendations (priority order)

1. **Truth-pass on the front door** (≤1 day): fix README §status/§samples numbers and the internal contradiction; refresh the "minimal UI" sentence; add current test/PR counts; either annotate DESIGN.md section-by-section with "superseded by X" banners or demote it explicitly to historical status with a 2-page current-architecture note; fix AGENTS.md:74-75.
2. **Give the demo a URL** (1–3 days): serve `dist/` from FastAPI or ship a static build with pre-baked JSON for 3–5 curated replays + the dashboard; even a GIF/video in the README beats the current nothing.
3. **A 200-line outsider-facing reading guide**: the meta-story (workflow, honesty culture, key numbers, where the bodies are buried) with a glossary for the audit idiom. This multiplies the corpus's value more than any additional rigor [JUDGMENT].
4. **Shrink the clone**: move `training/artifacts/coevo/realpath*` (~104MB) and arguably `replays/ml_corpus` (161MB) to an evidence branch or LFS, keeping manifests/verdicts in-tree. The determinism story survives — `verify_samples.sh` covers `replays/samples/`.
5. **Watchability quick wins in the UI** (§8 Wave 2 — end-of-game card, event ticker, cost chips): hours each, and they directly serve "would a human find a game interesting to follow."

---

## 4. Fix / refactor / harden (prioritized)

Severity-ranked; sizes are rough (S ≤ ½ day, M ≤ 3 days, L > 3 days). Items marked ● were verified directly by me; ○ verified by a fan-out review pass at the cited location.

**P0 — defects and falsehoods (all S)**
1. ● False "DEAD in production" docstrings — `agents/memory/beliefs.py:916-928, 1102-1116`. Rewrite; add the graduation-sweep convention.
2. ○ Undeclared direct dependency `httpx` — `llm/featherless_client.py:764` vs `pyproject.toml:7-20`. One line; the canonical provider currently rides transitive luck.
3. ○ Silent fallback pricing (unknown model → $3/$15) — `llm/provider.py:52, 660-663`. Contradicts the repo's own no-silent-fallback doctrine exactly where money is at stake; fail loud instead.
4. ● Missing token `text-ink-600` breaks meeting-modal legibility — `frontend/src/components/MeetingView.tsx:517`, `HighlightCard.tsx:60` vs `tokens.ts:39-47`. One-line fix + a class-exists check.
5. ● `threshold_inversions` doctrine drift: committed 9p2i report carries **87** (`replays/samples/9p2i/tournament-eval-report.json /conversion/threshold_inversions`); `eval/meeting_quality.py:618-624` says "expected ~0 … a gate-render/obedience bug to chase"; the dashboard renders a "gate bug — expect 0" badge against canonical data; the 13.13 design change made nonzero *intended* (`audits/audit-2026-06-24-1840-gameplay-data.md:37`), and `meetings/manager.py:307-320` documents that citation-gated SKIPs land in this bucket because the eval partition never learned `UNCITED_ZERO_FLAG_EJECT_MARKER`. Re-doctrine the sentinel, teach the partition the marker, fix the badge copy. Three surfaces currently disagree about whether the flagship dashboard is displaying a bug.
6. ○ `.env.example`: six dead levers documented as live; the only live lever absent. Rewrite from `orchestrator/replay.py:595-619`.
7. ● README/AGENTS/DESIGN staleness (§3.2 items 2/4) — the truth-pass.

**P0.5 — eval-layer honesty (S/M)**
7a. ○ **The declared canary metric is unwired**: `supplied_channel_conversion` ("the ONLY canary-eligible genuine-class cell from baseline 5 onward", `eval/vote_correctness.py:676-688`) is imported *only by its own tests*, while the starved predecessor (`genuine_class_conversion`, 0/0 = NO-DATA since baseline 4) rides the dashboard labeled "PRIMARY gate" (`frontend/src/components/TournamentDashboard.tsx:325-337`) and `measure_baseline.py`. Wire the successor into the report/CLI and retire the starved cell from the dashboard. S–M.
7b. ○ `alibi_fabrication.survival_rate` returns `0.0` when undefined, breaking the package's own None-iff-undefined convention (`eval/alibi_fabrication.py:90-94`); the frontend converts it back to n/a by special case. On the current substrate (checkable alibis ~0) the metric is near-permanently in its misleading branch. S.
7c. ○ `eval/leak_test.py` is simultaneously a pytest module and a shipping library — `scan_factory_packets` is imported by `training/bakeoff/harness.py:107`, so the champion-gate path imports `pytest` at runtime. Promote the scanner to a library module with a thin test wrapper. S.

**P1 — structural (M/L)**
8. ○ Decompose `orchestrator/game.py` (3,143 LOC: prompt registry / meeting wiring / loop / TacticalAgent are four modules) and `api/replay_loader.py` (2,838 LOC; also stop importing `orchestrator.replay._state_hash` privately, :162). M–L each; mechanical, low-risk.
9. ○ Consolidate vote resolution onto `meetings/voting.py` (production uses `MeetingManager._tally`, `manager.py:1956-2004`; eval/training use `voting.tally_ballots`; semantically identical today by review, protected only by prose). The ejection rule the game applies and the one eval re-checks should share one implementation. M.
10. ○ Test-suite structure: extract shared helpers out of `tests/meetings/test_manager.py` (7,531 LOC; imported as a library by 3 modules) and `test_prompt_byte_golden.py`; add a session-scoped committed-replay walk fixture (the 9p2i set is currently re-walked ~5× per suite run); register pytest markers (`slow`, training tiers) — the cheapest big win for gate runtime. M.
11. ○ Convert exact-scalar ruling pins to generated goldens (`tests/scripts/test_champion_flip_ruling.py` ~580 of 831 LOC; `tests/training/test_finalist_eval_pins.py` bulk): keep the derived-invariant pins (conjunction logic, digest chains, default-selector checks), retire the transcription tables that turn every re-record into multi-file literal editing. M.
12. ○ Leak-suite gap: add `moved_players` witness-gating coverage (`observation/service.py:470-505` — the one packet channel with zero leak-test coverage, and the one whose docstring narrates a prior gating bug). S–M, high value.
13. ○ Frontend hygiene baseline: vitest + first tests for `lib/playback.ts` and the store race guards; flat-config ESLint (two `eslint-disable` comments currently suppress a linter that doesn't exist); split the three-semantics error field (`replayStore.ts:445, 488`). M.
14. ○ Add `intent.actor == player_id` validation at the orchestrator trust boundary (`orchestrator/game.py:2030-2033`) — one line; the architecture explicitly anticipates learned movers on this seam. S.

**P2 — debt worth scheduling (not urgent)**
15. ○ Engine: remove-or-document the unused RNG draw apparatus (`engine/tick.py:643`; state-hash compat pins it — document as frozen rather than break bytes); dead `PlayerState.position` field; `_advance_tasks` continuation path production-dead (`engine/tick.py:141-198`); CAFETERIA hardcode in the map validator (`engine/world.py:337-338`). Mostly S each; some are byte-frozen — label, don't churn.
16. ○ Dead code deletions: `llm/cache.py` (192 LOC, interface-drifted, test-only), `scripts/record_meeting_gate_probe.py` (749 LOC, zero references), `eval/determinism_test.py` (exercised by nothing), `ui/SectionLabel.tsx`, dead API client methods, five unmarked bake-off prompt sets (~700 template lines). S each.
17. ○ CI: stop building the frontend twice (`check.sh:17-24` + dedicated job); consider pytest-xdist after markers land. S.
18. ○ Bash work-queue (`refresh_samples.sh` 913 + `record_ml_corpus.sh` 1,261 lines): freeze as-is (they work and are tested); if ever touched again, port to Python. Explicitly *not* Phase-19 work beyond the freeze label [JUDGMENT].
19. ○ Consolidate the eval replay walk — ~8 independent implementations (§2.2 row), each with a different integrity-check subset, so "reconstructs cleanly" already denotes eight subtly different predicates. One parameterized walker with fact-collector callbacks collapses ~800 lines and unifies the contract. The project's hand-off frames this as 3 copies and "a design question"; it is 8 and a drift hazard. M.
20. ○ Move `_BASELINE_SUPPLY_FLOORS` (30 pinned constants + ~300 comment lines, `eval/watchability.py:548-851`) to per-baseline JSON artifacts beside the sample sets; archive baselines 2–5 blocks (~200 lines of history reachable only by explicit flag; baseline-2 is additionally pinned under a *different* metric definition, `:549-554`). Also stops `training/realpath.py:158-166` privately importing the constant block. M.
21. ○ Record structured per-ballot suspicion telemetry so the §4.6 gate verdict and suspicion graph stop being regex-scraped from rendered prompt prose with silent skip-on-mismatch (`eval/_suspicion_parse.py:12-13` names the root cause itself). M — only worth it if any recording ever happens again; otherwise document the hazard.

---

## 5. The games themselves

Two review passes read **18 committed games end-to-end** (10 of 50 in 4p1i, 8 of 50 in 9p2i — every transcript turn, ballot, flag, and, where needed, the embedded LLM prompts) and reconstructed ground-truth positions from the tick logs to check every quoted claim; a third independently parsed **all 300 committed replays** (samples + ml_corpus) with stdlib scripts. Cross-validation is airtight: winner/final-tick match the eval reports 300/300; the ejection census, meeting-rate block, and cost-dashboard token totals reproduce the committed `tournament-eval-report.json` figures **to the byte** on all four sets — the committed derived metrics are reproducible from the committed raw bytes with no pipeline access, which is exemplary eval hygiene and should be said first. All game-level claims below were verified against reconstructed ground truth unless marked [JUDGMENT].

Corpus shape [VERIFIED]: samples 4p1i — 34% impostor wins, median 11 ticks, 0–1 meetings ever (max 1 in all 100 4p1i games, structural), 22% zero-meeting games, win reasons 23 TASKS / 10 EJECT / 17 PARITY. samples 9p2i — 30% impostor wins, median 33 ticks, 3.3 meetings/game, reasons 4 / 31 / 15 — the meeting-decided economy the project wants, confirmed. ml_corpus drifts crew-ward of samples on five metrics at the "same" substrate (25.3% vs 30.0% impostor win on 9p2i; ejection accuracy 0.821 vs 0.772) — no single gap significant, but it puts between-run variance at ±5–10pp impostor win, the exact granularity of the project's bright-line rules (see §7).

### 5.1 The headline finding: deduction is real exactly where the engine certifies it, and ~chance elsewhere

[VERIFIED] The single most important cross-tab in this audit, computed over all 165 9p2i meetings:

| meeting contains a `vent_sighting` flag | impostor ejected | innocent ejected |
|---|---|---|
| yes (70 meetings) | 68 | 2 |
| no (95 meetings) | 10 | 21 |

**87% of impostor catches (68/78) ride a witnessed vent** — hard, impostor-only evidence that the *scripted FSM donates* by venting in witnessed conditions after nearly every kill (most flagrantly, seed 44's two impostors venting the same tick, from the same room, in front of the same witness). In meetings without that smoking gun, ejection accuracy is ~32% — roughly chance for the typical living-roster state, with innocents ejected 2:1. The same law holds in 4p1i: all 12 ejections occurred in flagged meetings; 26 of 27 flagless meetings skipped; 9 of 10 correct ejections were vent sightings; soft deduction (proximity, timing, absence) produced **zero** ejections in 50 games — including seed 16, where a player was *seen entering the kill room at the kill tick* and nothing happened because that is not a flaggable contradiction class.

The honest summary: **the system demonstrates LLM evidence-processing of engine-certified facts, plus real deception, on top of a conviction engine that is substantially deterministic.** Ejection outcomes are a near-deterministic function of the contradiction detector; the LLM layer supplies voice, occasionally a tie-break (and in 4p1i seed 41, the one tie-break it decided, it decided wrong). Any claim that the corpus demonstrates LLM *social deduction* needs this qualification — and the crew's ejection win rate is being subsidized by opponent scripting (a minimally smarter mover that doesn't vent near witnesses would collapse it — which is, notably, exactly what the ML program's learned movers did, and exactly what the referee then failed them for; see §6).

### 5.2 The second finding: the "VERIFIED evidence" doctrine convicts innocents

[VERIFIED, traced case-by-case] The vote prompt labels every contradiction flag "VERIFIED evidence … never side with one over a verified flag." But an `alibi_vs_sighting` flag merely juxtaposes two *unverified model-authored statements* and always assigns guilt to the alibi-speaker. Traced consequences:
- 9p2i seed 17 M0: an impostor pair **fabricates a sighting** against the truthful vent witness; the engine flags the *witness*; the table ejects them 7–1 ("This verified contradiction proves p-1 is lying").
- 9p2i seed 12 M0: two honest players' one-tick-off statements produce a flag against a *truthful* innocent; 6–1 ejection; no impostor lied at all.
- 9p2i seed 23 M1: the impostor files a **provenance-impossible but factually true** sighting (it could not have been in view); the flag fires; innocent ejected 5–0. The contradiction engine never checks whether the observer could have made the observation.
- 4p1i seeds 41/49 (both impostor social wins in that corpus): flags fired on honest testimony over **1-tick interval-extraction artifacts** — in 49 both flags were explicitly stamped "[weak signal…]" and obeyed anyway; in 41 a *correct* impostor-only vent flag lost to a bogus alibi flag because the suspicion engine scores both +0.30, against the project's own hard-evidence doctrine.

40% of directional flag subjects in 9p2i are innocents (75/186). In three of four traced innocent ejections the fatal falsehood was authored by an *innocent* (misremembered tick, over-broad alibi) — the pipeline validates citation *ids* rigorously but never validates restated *content* against the speaker's own memory, which sits in the same record. This cluster — flag naming ("verified"), weak-signal weighting, interval extraction, no provenance check on sightings, no content-vs-memory check — is the highest-value *gameplay* fix available to any future phase, and none of it is in the project's Phase-19 hand-off list.

### 5.3 What is genuinely good

- **Deception is real and is the strongest capability on display** [VERIFIED]: coordinated fabricated alibis built by reading the transcript (17 M0), strategic truth-telling at parity (8 M4 — the impostor wins by accurately exposing a confused innocent's error), reporter-framing as a repeatable play, verbal bussing of a caught partner while the ballot SKIPs ("I'm just so scared to vote p-4 because they're my partner"). Impostor ballots: 245 in 9p2i, **0 votes against a partner** — the teammate firewall held perfectly, and within it the models produce genuine variety.
- **Citation discipline is real** [VERIFIED]: 520/520 eject ballots in 9p2i carry a citation; spot-checked observation ids resolve to real lines in the voter's own rendered memory; hallucinated ids are nulled with audit markers (2 of 971 ballots). Votes are attributable in a way most LLM-game projects never achieve.
- **Persona voice works** [VERIFIED]: ~13 voices per set, consistent across a game's five meetings, zero duplicate turns in 116 4p1i turns; lines land ("I must have been venting through your credibility"; "don't go painting the barn while the horse is still hitched"). The meeting prose is the attraction.
- **Cross-meeting memory exists and matters** [VERIFIED]: carried suspicion priors plus narrative recall ("he's already dead, so we can't vote him").
- **The replay is a first-class audit artifact** [VERIFIED]: full prompts, token counts, typed ballots, rejected actions, per-tick hashes; every engine intervention on a ballot preserved as a greppable marker. This audit was only possible because of it.
- **Emergent-feeling beats exist**: an emergency-button conviction with the corpse never found (4p1i seed 2), a six-tick stalk endgame (seed 0), a victim alibiing their own killer one tick before dying to them (seed 29 — the most "Among Us" moment in the corpus).

### 5.4 What is bad

- **The median game is not watchable** [JUDGMENT, grounded]: 4p1i median = 11 ticks, one unwitnessed dead-end kill, scripted double-vent, one 3-turn meeting of near-identical "too thin, skip" ballots, then task-timer win or inevitable parity. My own referee run agrees: 4p1i watchability geomean **median 0.75/100**. 9p2i's median (52.3) is genuinely better — gift-vent → clean ejection → repeat — pleasant but formulaic. The good tail (9p2i seeds 8/17/23; 4p1i 41/29/2) is legitimately gripping courtroom drama; roughly 1 game in 8 contains something a human would rewind.
- **4p1i undermines the thesis** [VERIFIED]: 23/33 crew wins are task-timer wins (46% of all games end CREWMATE_TASKS; 4 games have zero kills; seed 31 ends at t4 before the first kill cooldown expires), directly contradicting the map's own claim that redistribute makes "the only crew win path … ejection — i.e. deduction" (`engine/maps/canonical_1.yaml:39-41`). 22% of 4p1i games contain zero social content. No 4p1i game ever reaches a second meeting, so the suspicion arc the genre depends on structurally cannot occur there.
- **Scaffold leaks into the fiction** [VERIFIED]: 17% of 9p2i ballot rationales quote machinery ("suspicion of 0.55 falls below the 0.60 threshold, so I must SKIP" — recited by an *impostor*); 40 impostor rationales flatly state their role ("I am the impostor. Voting is suicide."); one player asks in open discussion "How do you know the system didn't flag it as verified evidence against p-6?". Fine as private-thought dramatic irony; cracked fourth wall as written text.
- **Discussion and ballots can decouple** [VERIFIED]: 9p2i seed 44 M0 — seven turns build a case against p-8; seven ballots eject p-4, whom nobody accused, because a flag landed during ballot rendering. A spectator following the argument cannot predict the vote.
- **Ballots partly measure the guard, not the model** [VERIFIED]: 13 under-gate ejects were engine-redirected in 9p2i; seed 8 M3's replay shows two "votes for the impostor" that were redirects of votes cast against an innocent. Fine engineering for balance; must be kept in view for any capability claim.
- **Prompt-mandated vent re-statement produces zombie testimony** [VERIFIED]: dead impostors' vents re-litigated meeting after meeting (five `[invalid accusation target]` drops in one seed-23 meeting), burning scarce turns and getting true witnesses accused of "fabricating a dead man's sin."
- **Skip-template despite anti-template instructions** [VERIFIED]: "the evidence is too thin" ×24 in 4p1i; one sentence verbatim ×5 across different seeds and voters.
- **The interestingness rubric inverts the tails** [JUDGMENT vs. full reads]: it top-scores formulaic double-vent stomps (seed 44: r2_deception = 1.0 for self-defeating chaos) and bottom-scores seed 8 (33.6, r2_deception = 0.2) — the most genuinely dramatic game read, where the impostor engineered an innocent's ejection at parity by telling the truth. The Highlights tab ranks by this rubric; its ordering should not be trusted as watchability, in either direction.
- **Metric naming spin** [VERIFIED]: `vote_correctness_rate = 1.0` sits beside `ejection_accuracy = 0.833` and two wrongful convictions in the same committed 4p1i report block — the 1.0 is "evidence-backed share of impostor ejections," structurally pinned by the §4.6 gate (the module itself documents this and demoted it to a sentinel, `eval/vote_correctness.py:11-25`; the dashboard still shows it as "correctness").
- **FSM artifacts as theater** [VERIFIED]: 19 consecutive `wait {}` ticks (4p1i seed 16; corpus-wide, ≥10-tick wait streaks in 53 player-games of samples-9p2i, all crew, worst 36), ping-pong pathing, kill *attempts* logged tick after tick against out-of-room targets, and identical post-kill double-vent choreography in every game. Corpus-wide, **20–21% of all 9p impostor kill submissions are engine-rejected** (48/225 samples, 131/640 ml_corpus) — one in five mover decisions is illegal, a mover-quality signal no eval report surfaces.
- **The reporter-innocence prior is absolute — and it's baked into the training corpus** [VERIFIED]: across all 300 committed games there are **zero** impostor-filed body reports and **zero** impostor-called emergencies (the scripted FSM simply has no such action), so "the reporter is innocent" is a 100%-reliable feature of every training example in `replays/ml_corpus` — the corpus whose stated purpose is fitting ballot surrogates. Any learned impostor that acquires self-reporting instantly invalidates the crew's learned prior. The corpus README does not acknowledge the property. [JUDGMENT on the implication; counts verified.]
- **~5% of 9p2i turns ship a diagnostic husk in player-visible text** [VERIFIED]: `[invalid accusation target 'p-X' dropped]` is welded into `free_text` (139+2 turns in ml/9p2i, 53 in samples) — the same non-model-text class the corpus README refuses for deadline husks ("a frozen training/eval corpus must not contain", `replays/ml_corpus/README.md:232-235`), tolerated here at 5% of turns. It is also a real capability datum: the 27B model names an illegal accusation target roughly 1 turn in 20 at 9p.

### 5.5 Verdict

As a simulation artifact, the corpus is honest, deep, and fully auditable — better than nearly anything in its genre. As a *game experience*, it is carried by the meeting prose and the good tail; the median is formulaic, the 4p1i preset actively undermines the deduction story, and the conviction engine's flag doctrine is both the source of its rigor and the cause of every traced injustice. The spectator UI (§3) is good enough to showcase the tail games today; what it needs is curation (lead with 9p2i's best seeds), and what the *substrate* needs — if any future phase touches gameplay — is the §5.2 evidence-honesty cluster, not new mechanics.

---

## 6. The ML implementation — a frank retrospective

**Has it worked?** [JUDGMENT, on verified evidence] As *science*: yes, narrowly. As *product*: no, and on the current bar it cannot.

**It is functional.** [VERIFIED by execution] The training env, ES core, surrogate and composed meeting runners, and a miniature end-to-end alternating-freeze campaign all run offline today, in seconds, at $0 (a fan-out pass ran each; I ran the champion factory path and the referee CLI). The shipped artifact chain verifies: train-side `utility-es` weights are byte-identical to the shipped `agents/tactical/learned/weights.json` (sha `6d327dcb…`), all 296 sidecars and 231/231 campaign recording manifests check out.

**What it demonstrably produced.**
- [VERIFIED] A real, replicated impostor win edge that never shipped: +0.10 (Phase 15) → +0.16 (Phase 17) → **+0.26** (Phase 18: 26/50 vs same-seed FSM comparator 13/50; all four finalists +0.12…+0.30) — with same-batch same-seed comparator hygiene that exceeds ML A/B norms.
- [VERIFIED] The same referee FAIL three phases running, same mechanism each time: learned movers suppress evidence supply, the population-relative conversion floor rises, conversion misses by 0.20–0.37.
- [VERIFIED] A conviction-economy model with genuinely clean eval hygiene (pre-registered bars, frozen thresholds, single held-out read at game-level splits; held-out decision accuracy 90/96 = 0.9375 vs ~51% majority class), plus two honest NO-GOs and one degenerate GO on the ballot-surrogate ladder.
- [VERIFIED] Two real behavioral findings (N1/N2 — learned kill-placement: witnessed-kill rate 0.152 vs FSM 0.046, z=+3.370; co-present kills 0.102 vs structural 0.0, z=+4.321; both recomputed from committed cells by this audit) — recorded as NOT-DEMONSTRATED under a pre-registration whose ablation clause was unsatisfiable by construction.
- [VERIFIED] Clean negatives published in full: torch PPO probe NO; policy-es real-path annihilation; crew track null (McNemar p=1.0).

**Is the evaluation honest?** Two answers. As *measurement*: exceptionally so — pre-registration, an UNRESOLVABLE outcome class that ate the program's own headline gauge at n=50, split-half noise preconditions, Wilson/z inputs quoted, reproduction snippets embedded (I reproduced the z-scores exactly). Most published ML evals do not meet this bar. As *decision structure*: **the flip bar is close to unpassable by construction, and the program half-knows it** [JUDGMENT, mechanism VERIFIED]. The floors are the scripted FSM's own measured economy, re-pinned each baseline (and confirmed by my own run: the canonical sets pass the referee at exact floor equality — the yardstick is the incumbent's self-play); the conversion floor is population-relative (`floor = baseline_conversion × baseline_flags / measured_flags`), so an impostor that suppresses evidence — which is what winning as impostor *is* — raises its own bar twice; and the training loop was blind to the priced quantity for most of the program (campaigns ran on fake-provider meetings where every meeting resolves SKIPPED; the 17-close says it itself: "training pressure toward the conviction economy the referee prices is therefore invisible on the surrogate path"). The Phase-15 owner ruling even conceded the floor is "not a principled necessity" before phases 17/18 hardened the opposite doctrine. Meanwhile the selection funnel screened candidates at n=3–6 — power the program's own instruments later proved insufficient (the campaign's only screening referee PASS failed to replicate).
- Counterweights, honestly stated: the supply floors *are* clearable by learned play (the Phase-15 champion cleared two of three by wide margins); `policy-es` proves a learned mover can pass the referee (by losing); and "don't ship a mover that starves the deduction game" is a defensible *product* stance. But it is a product gate wearing experiment clothes, and after the Phase-15 close the remaining two phases re-measured a foregone conclusion at increasing precision.
- Two further eval-layer defects sharpen this [both from the eval review pass]: (i) the floors are **bare point-estimate comparisons with zero uncertainty treatment** (`eval/watchability.py:911-985`) — the repo has a correct Wilson implementation (`deception_instruments.py:191-211`) and a split-half protocol, and the champion gate uses neither; two of the doctrine amendments the program needed (the 15.19 advisory rule, the 16.11 re-anchor after a floor miss comfortably inside binomial noise) would likely have been unnecessary with interval-aware gating. (ii) The 16.11 population-relative floor opens a **weak-flag Goodhart channel** — demanded conversion falls as measured flags/meeting rises, and the density term counts weak flags (`meeting_quality.py:2013-2021`) — that the referee's own "the Goodhart probe is the referee's acceptance test" doctrine (`watchability.py:19-21`) says must be probed, and never was after 16.11. Dormant while the program is frozen; first seam to red-team if selection ever reopens.

**Cost/benefit.** [VERIFIED counts; JUDGMENT on the ratio] 91 merged task sessions across phases 15–18, five 500–1,250-line close audits, ~200–250 operator wall-hours of recording, ~50k LOC of training code+experiments plus ~30k of training tests, 111MB of artifacts — for: one opt-in 19-weight linear champion, one unadopted 27-weight crew artifact, N1/N2, and the eval machinery. Roughly 20% of the apparatus (validity gate, stamp proofs, one Goodhart probe, the same-seed comparator) delivered ~90% of the decision value; the surrogate ladder, MAP-Elites persistence, composed runner, emergence framework, and coevo stabilizers either returned NO-GO/NOT-ADOPTED/0-EMERGENT or fed decisions a 50-seed win-rate + 3-gauge panel would have made identically. What the extra machinery *did* uniquely catch: the crew starvation-win exploit, the vent tell, the forced-kill Goodhart exploit — the gate/fitness split earned its keep; most of the rest was ceremony.

**Keep / freeze / simplify / retire** (details per-module in the fan-out review):
- **KEEP** (the live seam, ~12–14k LOC): `training/env.py`+`rollout`+`rewards`+`determinism`, `bakeoff/es.py`+`utility_es.py`, `harness.py` CLI, `surrogate/ballots+runner`, `conviction/model+serving`, `composed_runner.py`, `crew/`, and all of `agents/tactical/learned/`.
- **FREEZE with a labeled tier map**: `coevo/`, `scenarios.py`, `anchor_study.py`, losing bake-off entrants + `goodhart.py`, both `fidelity.py` harnesses, all of `experiments/`. A `training/README.md` declaring live-seam vs frozen-program is the single highest-leverage cheap action — today the ~6 live files are indistinguishable from the ~20 closed ones.
- **RETIRE-candidate**: `training/realpath.py` (4,470 LOC + 4,601 test LOC of one-shot campaign ops for a two-operator workflow that has ended); keep the ranking-row schema doc and committed rankings.
- **PRUNE**: `training/artifacts/coevo/realpath*` (~104MB) to LFS/evidence branch.
- **Test tiering**: move campaign-machinery test families (~13k LOC) behind an opt-in marker; keep champion-acceptance, ES, determinism, and artifact-digest surfaces always-on.
- **Eval-side freeze** (from the eval review's simplification map): archive `off_menu.py` (0-by-construction on every committed recording, by its own docstring) and `deception_instruments.py` (no non-test consumer) to a labeled frozen tier; keep `report_schema`, the validity gate, the wrapper analyzers, and `prompt_regression` as the durable live core (~5–6k of eval's 17k LOC). The watchability referee stays, frozen with the champion opt-in path it serves.

Two corpus-level caveats belong in this ledger [both VERIFIED, from the statistical pass]: (i) the "canary denominator" corpus is a noisier instrument than the prose treats it as — five metrics drift crew-ward between the samples and corpus recordings of the same substrate, and a pre-record 150-game probe landed at 0.327 impostor win where the committed corpus landed at 0.253 (~7pp swing, z≈1.4), while the program's bright lines (e.g. the 0.20 impostor-win floor) sit at exactly this granularity and single-run deltas are quoted to four decimals; (ii) the corpus's absolute reporter-innocence prior (§5.4) is a built-in distribution-shift trap for every surrogate fitted on it.

**Viability forward.** [JUDGMENT] Do not run a fourth campaign under the current bar — it will reproduce the NO-FLIP shape at further cost. Re-opening requires exactly one of two owner-level decisions the audits route but never take: (a) re-price the conversion floor for non-FSM populations (the abandoned Phase-15 logic), or (b) give training real-path/citation-aware conviction signal at meaningful scale. Absent either, the honest continuation is the one the program is demonstrably good at: instrumented behavioral findings (N1/N2-class) on an opt-in mover, at a fraction of the ceremony. Phase 19 should do none of this — only the freeze.

---

## 7. Anything else

- ● **The samples' own watchability scores condemn the 4p1i preset as a demo**: my referee run gives 4p1i a geomean **median 0.75/100** (mean 4.7; best game 19.7) vs 9p2i's median 52.3. The default demo path should always lead with 9p2i. [Also relevant to §5.]
- ○ **CI builds the frontend twice per run** (§4 item 17) and runs the undivided 4,531-test suite serially — ~15 min/PR that markers + xdist could halve.
- ○ **No committed launcher for the headline campaigns**: the 18.24/18.25 invocations live in report prose and `.py.txt` provenance files with hard-coded `/Users/danielkeinan/...` paths (`training/artifacts/coevo/provenance/harnesses/harness_run_c1.py.txt:12`). The library is deterministic; the invocation is folklore.
- ○ **The headline ML evidence bytes are not in the repo** (finalist-eval recordings live on the operator's machine; committed rows carry `/Users/danielkeinan/...` `replay_set_dir`). Consistent with declared policy, and the derived statistics reproduce from committed cells — but the program's central claims rest on measurements *of* evidence, not committed evidence.
- ○ **`DEFAULT_PROMPT_SET = "qwen3_5_9b"`** (`agents/strategic/prompts/loader.py:119`) while the operational baseline is `qwen3_6_27b` via env: a bare-environment run silently renders two-generation-old prompts. S fix, real footgun.
- ○ **Wall-clock assertions in tests** (`tests/training/test_realpath.py:288,320,3307`) are CI-under-load flake vectors; tag `slow`/`perf`.
- ● **Shallow-clone default in hosted CI/agents environments breaks history claims**: this session's clone had 50 commits until unshallowed — anyone verifying "PR counts" or `git log --follow` provenance needs the full fetch (worth a note in AGENTS.md).
- ● **A near-collision of two similar gauges invites misquoting**: the baseline-6 audit's "watchability mean 54.58" (eval/watchability geomean — my `measure_baseline.py --watchability` run reproduces it exactly from committed bytes) and `replays/samples/9p2i/results-rubric-score.json`'s `interestingness.mean_score = 54.1` (the lab rubric, scored at recording sha `f011848`) are **different instruments with nearly identical values and the same median (52.3)**. A statistical pass in this audit initially misread the pair as audit drift; a human will too. Meanwhile the Highlights tab's staleness banner fires because HEAD moved past the scoring sha — a rubric re-score at HEAD clears the banner and is worth doing in any demo-refresh wave.
- ○ **Calibration curves pool deceptive and honest accusers** (`eval/accusation_calibration.py:245-282`; ballot Brier/ECE likewise): an impostor confidently accusing a crewmate is successful deception, not miscalibration, yet no calibration surface splits by author role. The arithmetic is correct; the construct is muddied. [JUDGMENT on the construct.]
- ○ **Class membership decided by English substrings**: weak-reason band membership for the primary gate metric is tested via phrases like `"endpoint-tick sighting"` in `ContradictionRef.description` (`eval/vote_correctness.py:566-571, 667-671`) — metric-definitional state that should be a typed field.

---

## 8. Phase 19 — what it should actually contain

The charter (deep code review + frontend/data-display refresh; explicitly not a feature phase; human seat out; hetero-model lobbies out) is **correct**, and this audit's disagreement with the project is only about emphasis: the phase-18 close's §7 hand-off list is 14 inward-facing plumbing items, several of which are the *least* valuable things Phase 19 could do. The phase should be chartered as three waves:

**Wave 1 — Truth reconciliation (the review half, ~week 1).** P0 + P0.5 items above: fix what is false before touching what is merely imperfect. Include the graduation-sweep docstring convention and a CI-able claims check where cheap (e.g. README numbers vs manifest/pytest counts — the project already has the pinning-test idiom for exactly this).

**Wave 2 — The refresh half (the visible payoff).** Frontend P0 quick wins (end-of-game outcome card, event ticker, cost surfacing, contrast fix — all data already client-side); a deployable demo (static build + pre-baked JSON or StaticFiles mount) so the project has a URL; vitest + ESLint baseline; the outsider-facing reading guide; lead every demo path with 9p2i.

**Wave 3 — Consolidation (the freeze).** ML freeze per §6 (tier map, test tiering, artifact prune to LFS/evidence branch, realpath retirement decision); test-suite structural work (§4 items 10–11); the two god-module decompositions if budget remains (they are mechanical and low-risk, but they are also the items most safely deferred).

**Explicitly NOT in Phase 19:** any new game mechanic or map; any training campaign or referee/floor change (that is an owner decision to make *before* work is chartered, not review work); further audit formalism (the corpus needs a glossary, not more case law); porting the bash recorders to Python (freeze them); chasing the 14-item hand-off list's long tail (items like the recorder lock-race and `deadline_default` blindness belong to frozen machinery — label them frozen and move on). [JUDGMENT throughout this section.]

**On the charter itself:** the one place I'd push back is sequencing implied by the hand-off — the project's own §7 list would spend the review budget deep in eval/training plumbing. The evidence in this audit says the highest-value review targets are the *truth layer* (docs/docstrings/badges) and the *presentation layer*, and the highest-value hardening is test tiering + the leak-suite `moved_players` gap — not further polishing of machinery the program itself just froze.
