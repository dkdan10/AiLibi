# Independent review: `codex/cleanup` (9b333a76) against `main` (cfde4c89)

Reviewed on 2026-09-06. Read-only. No tracked file, PR, recording, weight, or experiment default was changed by this review.

## 1. Recommendation

**Changes required before merge, but small ones.** The branch is substantively what it claims: the 26 cards are implemented, the committed evidence recomputes to the digit, every gate reproduces in a pristine checkout, default gameplay is byte-identical to main, and every experiment is genuinely OFF. What blocks an immediate merge is a short list of introduced regressions, each with a reproduction and a one-line-to-one-function fix, several of which contradict an acceptance box the branch itself checked. After that fix batch the branch is ready, with the follow-ups in section 7.

Required before merge (details in section 5):

1. A committed derived report is now stale on the branch: `scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check` fails on HEAD and passes on main.
2. The As-agent lens still discloses another voter's private ballot confidence in the vote-gate line, contradicting the portfolio card's checked acceptance item.
3. The stale-rubric replay cards print a false explanation ("This set ships no interestingness rubric") under a banner that says the opposite, in the live viewer and the static demo.
4. A forced re-record that fails before its first row now deletes both the previous replay and its audit; main preserved the audit.
5. A tournament run publishes a zero-game report over an existing report before any seed runs, so a run that fails immediately destroys the prior report; main did not.
6. `docs/media/README.md` asserts the README shows five assets; the README shows two.
7. The public results page presents a fraction that is 100% by construction as one arm of an empirical contrast.
8. `pytest tests/orchestrator/` alone fails at collection because a new test imports a `scripts/` module at module scope.
9. The frontend type-fidelity fixture lost its `GameFinale` subtree, so three generated interfaces are no longer witnessed by a served payload.

Confidence: high on gates, default-path equivalence, and evidence reproduction (all recomputed independently, most twice). The class-(c) evidence that a fresh clone lacks turned out to be restorable offline from this machine's local `refs/evidence/*` objects; with it restored the ML verifier's `--complete` gate passes and the 300-game Wave-2 FINDING record reproduces every published figure. Material gaps that remain: no live-model evaluation exists or was run, so nothing here speaks to real-model reasoning quality; and crash-durability under a hard kill mid-row and concurrent writers on one path are disclaimed by the branch and behave badly when probed (section 7).

## 2. What was reviewed and how

References verified at start: `main` = `origin/main` = merge-base = `cfde4c8960a865eeaa39a004b2c33d302cbe4733`; `codex/cleanup` = `origin/codex/cleanup` = `9b333a76fb07f8db2a30ae00004bcdbddf9609ce`; working tree clean. The branch is a straight descendant of main (28 commits, no divergence), so the merge-base diff and the main-to-branch diff are identical: 288 files, 75,785 insertions, 3,244 deletions. About 46,000 of the insertions are two committed measurement JSON files. PR 431–434 commit identities are preserved byte-for-byte on the branch.

Method. Three independent tracks ran as separate agents with separate scratch directories and no shared notes until each had frozen its own findings: gameplay-first (six lenses over the recordings and fresh fake-provider games, told not to read the cards until their notes were frozen), code-first (eight lenses plus three commit-range reviews of all 28 commits), and portfolio/workflow (two lenses). Eight further agents built the completion matrix for the 49 priorities and two audited the 26 cards' acceptance boxes. Every finding then went to adversarial refuters (three per medium-or-higher finding: reproduce, pre-existing-on-main, scope/severity; one per low/info), and a completeness critic ran a follow-up round. All agents worked in detached, pristine worktrees of the reviewed commit and of main. All provider calls were the fake provider.

Independence note: the gameplay lenses' frozen notes were compared with the cards only afterwards. Nearly every gameplay observation turned out to be already on record in the branch's dispositions, which is itself a result: the branch's own account of the games is accurate. The one gameplay mechanism no register mentions is the movement breadcrumb (finding G1-02).

## 3. Verification results

All runs in a detached worktree of 9b333a76 with its own `uv` environment and `npm ci`.

| Check | Result | Matches branch claim |
| --- | --- | --- |
| `bash scripts/setup_env.sh` | exit 0. npm blocked four install scripts (esbuild, @swc/core, fsevents); the platform binaries ship as optional packages and the build succeeds. | yes |
| `bash scripts/check.sh` | exit 0. ruff/format clean; import-linter 4 contracts kept; task docs 390 phase tasks + 390 prompts + 26 cards; mypy clean on 438 files; pytest 6775 passed / 20 skipped / 3 xfailed in 230 s; vitest 489 passed; vite build ok. | yes, exactly |
| `bash scripts/verify_samples.sh` | 4p1i 50/50 and 9p2i 50/50 reconstruct clean. | yes |
| `uv run pytest -m campaign -q` | 335 passed, 6798 deselected, 209 s. | yes, exactly |
| `uv run python scripts/verify_ml_evidence.py` | Bare checkout: 60 checks, 48 OK, 0 FAIL, 7 ABSENT (evidence-branch bytes), 5 INFO. The bytes are present locally as `refs/evidence/phase-18-coevo` (476a1f85) and `refs/evidence/phase-21-wave2-finding` (29af85d5); in a fresh clone with those refs fetched, `bash scripts/fetch_evidence.sh` restores 3269/3269 files and `--complete` passes: 63 checks, 58 OK, 0 FAIL, 0 ABSENT, 5 INFO (the wave2 row expands into four per-set reconstruction rows: 50/150/50/50 games). All 316 Wave-2 files hash-match their manifest; the 11/20 = 0.55 FINDING cell and every per-set outcome reproduce. | yes, and stronger than claimed |
| `cd frontend && npm run e2e` | Run locally from the pristine worktree with the pinned Chromium build 1194 already present in `~/Library/Caches/ms-playwright` (installed 2026-08-19, no download made): 13 passed, 3 skipped (the opt-in README media captures), 0 retries, 1.2 min, exit 0. Playwright started its own uvicorn and Vite servers from that worktree on 8000/5173, which were free beforehand. GitHub CI job "Frontend e2e (Playwright)" is also green at exactly 9b333a76 (run 34010691215), alongside "Project checks" and "Frontend checks". | yes, exactly |
| Browser walk of the reviewed source | Done with the in-app browser against an API and Vite server launched from the review worktree on private ports (pids and cwd verified), plus the static bundle built to scratch and served separately. | n/a |
| The 3 xfails | Strict xfails in `tests/orchestrator/test_meeting_integration.py` (asymmetric-visibility emergency); present on main. | pre-existing |
| The 20 skips | Optional-provider tests (Ollama, Featherless), planted-decorator guards, git-history guards, case-sensitive-FS branch, `uv`+bash wrapper, dir-mode 0500. | expected |
| Default-path equivalence | Fake-provider games for 4p1i seeds 1/2/3/5/7/11/16/22/27/35/39 and 9p2i seeds 0–11 produced byte-identical tick and meeting rows on main and HEAD; the only difference is the additive `substrate_flags.temporal_observations: false` on the terminal row. The observation audit sidecar differs in `visible_bodies[].id` (public handle), which no committed recording carries. | yes |
| Committed evidence recomputation | `scripts/measure_reasoning_evidence.py` reproduces `audits/reasoning-evidence/scorecard.json` bit-for-bit except four wall-clock latency floats; `experiments/tactical_gameplay.py --split development` and `--split held_out` reproduce every arm/roster/seed row of both JSONs and the runtime fingerprint `d93f9d09…`; `scripts/measure_replay_loading.py` reproduces all four static byte figures; `scripts/scan_recording_packets.py` reproduces every cell of the semantic-validation table including both source fingerprints. | yes |
| Adverse baselines the cards claim | Re-created from `git archive` of the pre-change commits: budget-accounting 4 fail/23 pass, map-traversal 4 fail/41 pass, aborted-meeting 9 fail/2 pass, completed-attempts 6 fail/6 pass, temporal 9 fail, tournament-lifecycle 6 fail, completion-status 12 fail. All match or exceed the card wording. | yes |
| `scripts/build_sample_report.py --check` (not in any gate) | samples/4p1i, samples/9p2i, ml_corpus/4p1i consistent; **ml_corpus/9p2i STALE on HEAD**, consistent on main. | no (finding G5-1) |
| `pytest tests/orchestrator/` alone | 417 collected, 1 collection error. | no (finding C2-6) |

Numbers the branch quotes that I could not recompute: the intermediate batch gate counts (6,115 / 6,292 / 6,409 / 6,599) and the 133.51 s timing, which cite `/tmp` logs; they exist on this machine and agree, but they are not committed evidence. The dependency advisory scans were re-run today against the network databases and still report zero findings on HEAD versus five npm and six Python findings on main.

## 4. How the findings were weighed

196 raw findings came out of 27 lenses, and a completeness critic's eight follow-up probes added 43 more (mostly confirmations or duplicates). 21 were refuted outright by the adversarial pass (the material ones are listed in section 9) and many more had their severity lowered because the mechanism reproduced but the branch already documents it as an accepted limitation. Everything below is either an introduced regression I could reproduce on HEAD and not on main, a pre-existing defect that bounds a claim the branch makes, an unsupported claim, or a documented limitation that an owner or reader needs to know. Classification uses the branch's own vocabulary: an OFF experiment can be merge-ready while its ON path is not adoption-ready.

## 5. Required before merge

Each item: severity, anchor at HEAD, introducing commit, trigger, expected versus actual, evidence, smallest fix, verification.

### 5.1 Committed `replays/ml_corpus/9p2i/tournament-eval-report.json` is stale on the branch (G5-1)
- Severity medium, introduced regression. Anchor `orchestrator/replay.py:632`; serializer projection `scripts/build_sample_report.py:198-205`. Introduced by 26386914.
- Trigger: `uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check`.
- Expected: exit 0, as on main and as for the other three sets. Actual: "is STALE" (exit 1) on HEAD. The only differences are two `call_id: null` fields on the failed-call rows of seeds 1012 and 1093; nothing numeric moves. The JSONL writer strips a `None` call_id and the API projection excludes it, but the report serializer embeds the entry whole and the historical projection excludes only `completion_status` and `outcome_verified`.
- Why it matters: the branch's thesis is that committed evidence is bound to its source; this is the one place a committed derived artifact no longer round-trips, and no gate catches it (`tests/scripts/test_build_sample_report.py` pins only samples/4p1i, which has no failed calls).
- Fix: add `call_id` to the historical projection's exclusion when it is `None` (mirroring the writer), or regenerate and commit the report (owner action). Add the two failed-call sets to the test's pinned list.
- Verify: the `--check` command exits 0 on all four sets.

### 5.2 Vote-gate readout leaks another voter's private confidence under As-agent fog (G6-2)
- Severity medium, introduced regression against a checked acceptance box. Anchor `frontend/src/components/MeetingView.tsx:193-202` (`gateReadout`), called unconditionally at `:242`. Introduced by 9b0735ba (the lens gating was added there without covering this line).
- Trigger: `/?set=9p2i&game_id=headless-seed-23&tick=10&perspective=p-1&selectedAgent=p-1&selectedMeeting=headless-seed-23%3Ameeting-0&view=workspace`.
- Expected: every non-own ballot hidden, as the ballot cards do. Actual: the resolution line reads "plurality leader p-6, top ballot 1.00 ≥ 0.60 threshold → EJECTED"; 1.00 is p-5's confidence, which the same page has just refused to show. Reproduced by three verifiers in their own servers, on two recordings.
- Affected: `tasks/work/portfolio-evidence-experience.md` acceptance "All private ballot reasoning … require the voter's … own lens, or omniscient mode."
- Fix: pass the observer/omniscient decision into `gateReadout` and omit the numeric confidence when the viewer is not entitled to the leader's ballot. Add a `VerdictPanel` case to `PrivateReasoning.test.tsx`.

### 5.3 Stale-rubric cards claim the set ships no rubric (G6-1)
- Severity medium, introduced regression (presentation). Anchor `frontend/src/components/ReplayPicker.tsx:438` (`hideUnscoredNote={!isHighlights && rubricMissing}`) and `:764` (`rubricMissing` only on a 404); fallback copy at `HighlightCard.tsx:283-306`. Introduced by 996864c0, which started serving `per_game=[]` for stale rubrics.
- Trigger: `/?set=9p2i&view=replays` (the landing surface) on the shipped corpus, live or in the static bundle.
- Expected: cards say nothing beyond tick counts, as the genuinely unscored 4p1i set does. Actual: 50 cards read "Not scored / This set ships no interestingness rubric." directly under a banner saying scores were hidden because their source cannot be verified. 9p2i does ship a rubric.
- Fix: treat withheld-because-stale like set-unscored for the per-card note (`rubricMissing || stale`), or add a stale-specific note. Pin with a Vitest case.

### 5.4 Forced re-record that fails before the first row destroys both previous artifacts (C2-1)
- Severity medium, introduced regression on an error path. Anchor `orchestrator/game.py:2171` (`begin_recording()` called before `_run_loop`); discard branch `orchestrator/recording.py:151-155`. Introduced by 62ba0162.
- Trigger: `force=True` over an existing replay/audit pair, then any exception before the first replay row (a verifier reached it without monkeypatching via `RunDeadline(0.0)` at the top of the loop).
- Expected (the card's own contract): a failure before recording begins restores the previous pair; a failure after preserves new partial data. Actual: the backups are discarded, no new file was ever created, both artifacts are gone. On main the same failure destroys the replay but preserves the audit.
- Fix: make `begin_recording()` lazy, invoked on the first byte written. Verify with the two-step probe (fail before first row → old pair intact; fail after first tick → new partial retained).

### 5.5 A pre-existing tournament report is destroyed before any game runs (C7b-2)
- Severity medium, introduced regression. Anchor `scripts/run_tournament.py:1405` (`progress.publish()` before `for seed in seeds:`). Introduced by 3d0a0a12.
- Trigger: `--report-output` pointing at an existing report; a run that fails on its first seed (e.g. an invalid roster).
- Expected: the prior report is untouched (main's behaviour: publication only after games). Actual: a zero-game report replaces it atomically before the first seed and stays there. Reproduced with sha before/after on both checkouts.
- Fix: seed the progress record's report hash from the existing file, or publish only once the first attempt has produced a game. Add a test that a first-seed failure leaves `--report-output` byte-identical.

### 5.6 `docs/media/README.md` describes the pre-rewrite README (P1-1)
- Severity medium, introduced documentation regression. Anchor `docs/media/README.md:3` and `:120-128`. Introduced by 3a1e64ac (README cut 251 → 111 lines; the media doc was not revisited).
- Actual: it asserts five assets are shown in or linked from the README and that "the README shows the GIF"; the README shows one PNG and links one clip; `spectator-meeting.png` and `spectator-journey.gif` are referenced from no Markdown file. This is exactly the claim class CONTRIBUTING.md says the project treats as its highest-value issue.
- Fix: rewrite the two paragraphs to the current README. Optionally extend `check_doc_facts.py` to assert each asset the media doc claims the README shows appears in it.

### 5.7 A definitional 100% presented as a measured contrast (C5-1)
- Severity low-medium, unsupported public claim. Anchor `frontend/src/components/PublicResults.tsx:47-54`; `ROLE_PROOF_KINDS == {"vent_sighting"}` at `eval/deduction_metrics.py:447` and `api/schemas.py:764`; grounding chokepoint `meetings/transcript.py:148-149`. Introduced by 3a1e64ac.
- Actual: "With role proof: 68/68 (100%)" beside "Without role proof: 14/27 (52%)" under a heading framing them as a contrast. A grounded vent flag can only name a genuine venter, so the left figure cannot be anything but 100%. The hedges on the page are causal, not structural.
- Fix: one caption clause saying the proof-backed figure is 100% by construction and that the informative number is the 27-ejection proof-free split.

### 5.8 `tests/orchestrator/` no longer collects on its own (C2-6 / CARD-01)
- Severity low, introduced. Anchor `tests/orchestrator/test_aborted_meeting_records.py:12` imports `_manifest_writer` from `scripts/` at module scope; only `tests/scripts/conftest.py` puts that directory on `sys.path`. Introduced by 26386914.
- Actual: `pytest tests/orchestrator/` → 417 collected, 1 error. The full suite passes only because an earlier-collected package bootstraps the path. The aborted-meeting card's own Validation instruction cannot be followed as written.
- Fix: import through the same bootstrap the scripts tests use, or move the helper import inside the test.

### 5.9 Type-fidelity fixture lost its `GameFinale` subtree (C7a-2)
- Severity low-medium, introduced test-coverage regression. Anchor `scripts/gen_frontend_types.py:438`; fixture `frontend/src/types/api.fidelity.ts:36` now `"finale": null`. Introduced by 55ed6d9a, which removed `record_game_end` from the fixture game because the new gate correctly refused a forged terminal.
- Actual: `GameFinale`, `AgentRecap`, `DecisiveEvent` are exercised by no served payload in the gate documented at `gen_frontend_types.py:400-418` (main's fixture had them).
- Fix: drive the fixture game to a genuine terminal with the `finish_replay_with_kills` helper the same commit added, regenerate, and confirm `agent_recaps` reappears.

## 6. Also fix or explicitly document before merge (cheap, but not blocking)

- **Limit-stopped tournaments cannot be resumed by `--resume`** (C7b-1, M1-F2, C3-02, C7b-3). Anchor `scripts/run_tournament.py:1302-1305` (limits inside the fingerprinted configuration), `:1359` (deadline rebuilt from the exhausted allowance), `scripts/_tournament_progress.py:173-176`. Introduced by 3d0a0a12. Same limit re-fails immediately; a raised limit is refused as a configuration change; the flag omitted is refused too. The card says the limits "apply across seeds and resumed attempts". Verifiers disagreed on severity: the mechanism is certain, the acceptance text literally requires "the same configuration", and a workaround exists (run the remaining seeds as a second tournament into the same output directory with its own report), so this is a card overclaim plus an operator dead end rather than data loss. Fix: exclude the four limits from the fingerprint and allow monotonic raises, or state the dead end on the card and in `--help`.
- **Report-destination protection covers only the selected seeds** (C2-4, M1-F1). Anchor `scripts/run_tournament.py:1199-1210`. A `--report-output` naming a genuine recording for an unselected seed in the same output directory is overwritten (no `--force` needed; the audit sidecar is orphaned). The card's wording is scoped to "selected" paths, so the card is accurate; the Milestone-1 exit line ("reports cannot destroy their evidence") is not. Fix: glob the output directory's existing recordings into the protected set.
- **`/eval/summary` reconstructs all 50 recordings on every request** (C6-1). Anchor `api/public_results.py:232-233`; `_DEFAULT_CACHE_SIZE = 16` at `api/replay_loader.py:209`. Introduced by 3a1e64ac. Measured in-process: 2.2 s cold, 1.4 s warm, 50 walks per request, four concurrent cold requests 8.2 s and 211 MB peak RSS; raising the cache to 64 drops request two to 174 ms. The frontend fires it on every dashboard mount and set change. Static bundles are unaffected. Fix: memoize `build_public_results` on the recording fingerprint it already computes.
- **The `after.json` performance capture is bound to e805ddd6's reader, not HEAD** (C6-3, CARD-01, M6-02). The recorded `reader_implementation` digest equals the tree at e805ddd6; 24 hashed files changed afterwards, including `api/replay_loader.py`. The byte figures reproduce at HEAD; the timing, RSS and walk-count rows do not characterise the branch head. The card's "once runtime sources froze" is not accurate. `before.json` is reproducible from no commit (the harness post-dates the state it measures). Fix: amend the card, or re-run the after capture at HEAD (owner action).
- **Cold `GET /replays` is about five times slower than main** (C6-2): 135 ms → 681 ms for 50 games, the deliberate price of validating each timeline at listing time; cached afterwards; undisclosed and unmeasured in the committed evidence.
- **`Attempt.accounting_complete` is set unconditionally** (GC-2). `scripts/_tournament_progress.py:338` sits outside the `if replay.exists() and replay.stat().st_size:` guard at `:318`, so an attempt whose recording is missing or empty is persisted with cost 0 and accounting marked complete; reproduced after a real SIGKILL followed by the only documented recovery (deleting the damaged pair): 54,291 input tokens silently leave the cumulative cap. Introduced by 3d0a0a12. One-line fix: move the assignment inside the guard.
- **README points operators at instructions that do not exist** (GC-6). `README.md:105` sends readers to `docs/deployment.md` for bounded tournament and resume instructions; no such section exists anywhere under `docs/`, and `--help` is the only documentation of `--resume`, `--retry-incomplete` and the four `--max-*` flags. Introduced by 3a1e64ac. Fix: write the section or re-point the link.

## 7. Important follow-ups (not blocking)

Grouped by the invariant they bound.

**Recording integrity bounds "strict".** Ballots are never reduced against the recorded outcome (C1-01, C2-2, G5-2; pre-existing; `orchestrator/replay_integrity.py:200-210`, `eval/balance_eval.py:928`): retargeting every ballot while leaving the outcome, ejectee and hashes intact passes `verify_samples`, loads, serves and folds as `outcome_verified=True`, and the served gate view contradicts the row. The tally check already exists (`eval/replay_walk.py:601`) and is selected only by `eval/watchability.py`. All 672 committed meetings re-tally cleanly, so no committed number is wrong. Deleting a `game_over` row is accepted and reclassified "unfinished" although the engine reconstructs a terminal event (C2-3, C7a-3; `replay_integrity.py:256`). Swapping two meetings' ids is accepted (C7a-4). The `outcome_verified` docstrings should say the stamp certifies chronology and the terminal engine event, not the meeting's social payload, or the tally check should be added to the current-report walk and the validator.

**Experiment provenance.** The tournament report carries no experiment or substrate label and the current-report walk deliberately accepts experimental and temporal recordings, so an experimental-arm game folds into a report indistinguishably from baseline (C4-2, TGE-2; `eval/balance_eval.py:929-931`). An experimental agent factory paired with a `None` experiment config produces an unstamped recording that passes `require_baseline_experiments` (TGE-1; `orchestrator/game.py:2565-2577` checks only when the recorded config claims tactical changes). No committed artifact is affected; the CLI and harness build both sides from one config. Fix: add `experiment_config` to `GameReport`, and make the factory/config comparison unconditional.

**Temporal experiment ON path** (see section 12).

**Tactical evidence presentation.** Arm-versus-baseline deltas omit effective sample size (G3-1, TGE-3): in held-out 4p1i the vent-risk arm is trajectory-identical to baseline in 15/16 games, meeting follow-through in 13/16, workload in 12/16; the values are derivable from the committed `trajectory_sha256` fields, so one added column needs no rerun. Roadmap 46's "task victories" half is not explained (TGE-4). `post_meeting_retarget` is silently inert when combined with `meeting_reset` (G3-3).

**Budget accounting edge.** A non-`BudgetExceededError` raised while charging failure metadata replaces the original provider exception (C3-04, C7a-5; `llm/budgeted_client.py:336-343`); reachable only with a provider reporting negative usage. Cumulative caps are estimate-based admission caps, not ceilings, and `--help` does not say so (C3-05). `Attempt.accounting_complete` is written but never read (C3-03). Published reports and sidecars now land at mode 0600 where main wrote 0644 (C2-5, C3-01).

**Smaller code items.** `ReportedStatement`'s wrap serializer lacks the `__get_pydantic_json_schema__` companion its siblings carry, collapsing its serialization schema to zero properties (C7c-1; `meetings/schemas.py:682`). `temporal_observation_version` accepts a JSON boolean and coerces it to 1 while sibling version fields reject non-int (C4-5). `ReplayLog` silently overwrites a caller-supplied `substrate_flags['temporal_observations']` (C4-4). `load_archive_cell_genomes` defaults the expected kind to v2 while recorded kind defaults to the historical name (C7c-6). `MovedEvent.witnesses` is computed on every move on the default path but consumed only under the OFF lever, about 1.9× slower on a move-heavy synthetic tick (C1-02). The intermediate commits ee46d114 and a0285760 are red on `tests/api/test_leak.py::test_eval_report_field_set_snapshot` (fixed two commits later), so the branch is not bisectable at those points (C7c-2). `scripts/build_sample_report.py:395` bypasses the atomic writer (C7a-7). The "Pinned recording source" links hard-code branch-only commit 5006a32f (C5-4 and duplicates); `replays/` is byte-identical between that commit and main, so pin to a main commit after merge.

**Crash durability and concurrent writers** (disclaimed by the recording, report and checkpoint modules; probed anyway). A recording truncated mid-row by a hard kill makes both `--resume` and `--resume --retry-incomplete` fail at `scripts/_tournament_progress.py:319` with a raw `ValueError` before the retry path can archive it; the only recoveries are deleting the pair by hand or `--force` re-running every seed, and neither is documented (GC-1). Two `run_game --force` processes on one replay path both exit 0 reporting success while only the later game's bytes survive (GC-3, reproduced at nine stagger intervals; `orchestrator/recording.py:136`); keeping the exclusive probe descriptor open for the recording's lifetime would refuse the second writer and also close the residual non-force interleave window (GC-4). Concurrent tournaments on one `--output-dir` lose the loser's sidecar and strand its recordings (GC-7). `_atomic_write` does not fsync before `os.replace` (GC-5). Verified good on the same probes: two-phase report publication, post-game kill recovery, and refusal of damaged bytes by both the loader and the verifier.

**Substrate-lever edge cases** (the four pre-existing levers were exercised ON by the follow-up probes; all default-OFF, all low). `recorded_testimony_shapes` ignores the `AbortedMeetingReplayEntry` prompt versions, so an all-aborted lever-ON recording reads OFF (GL-1; `orchestrator/replay.py:683-689`). `served_testimony` folds `all()` over a filtered generator that is vacuously true for a registry entry with no arm-suffixed values (GL-2; `orchestrator/game.py:1315`). Unrecognised values for the four `AILIBI_*` levers resolve silently OFF while the branch's new evidence-profile parser raises on the same input (GL-4; `meetings/constants.py:74` versus `meetings/evidence_profile.py`). `reporter_reasoning` and `impostor_roll_call` have no served-versions guard, unlike corroboration and the new testimony guard (GL-6). Under `AILIBI_TEMPORAL_OBSERVATIONS=1` the packet census reports kill, vent and moved-player views as 0 because those channels move into event batches the census does not count; the underlying entitlement assertions do run, but a zero row is indistinguishable from an unscanned channel (GL-3; `scripts/scan_recording_packets.py:79-87`). One reachable caller was not migrated to the new `derive_reported_testimony` signature, `scripts/counterfactual_phase20.py:527`, though that script exits before folding on both main and HEAD (GH-1).

**Evidence and workflow hygiene** (all process, none blocking; section 11 has the recommendations): completion is asserted in five documents and checked by none of the doc-fact gates (P2-2); `docs/workflow.md` is frozen at batch two (P2-1); acceptance boxes are prose-only, 19/26 cards name no card-specific command, and a vacuous "done" card passes the validator (P2-3); 49 evidence citations point at `/tmp` paths (P2-7, M7-2, CARD-03, M5-03, M2-F3); the branch's own independent reviews left no committed notes, so the rule it wrote in `docs/workflow.md:126` is unexercised on its own work (M7-1); the roadmap-24 acceptance text was rewritten in the commit that checked it (TGE-5); two cards' clean-source numbers no longer reproduce (M2-F2, CARD-02-temporal); the audit-fact-gates card states a stale byte total (M6-01).

## 8. Documented limitations and pre-existing defects a reader must know

These are not regressions. They bound what the branch's default behaviour and its public numbers mean.

- **Default opening prompt carries the death tick.** `orchestrator/game.py:3120-3123` uses the raw engine handle `body-{victim}-{killTick}` unless temporal observations are on. Across all 177 body-report meetings in the two sample sets the handle appears in exactly the reporter's prompts (179 of 1,832 prompts), never in another participant's, and the same holds for all 450 handle-bearing prompts in the 200-game ML corpus; the reporter is a non-witness, and in this corpus always a crewmate. The encoded tick is 1–12 ticks before the report and one tick off from every other agent-facing timestamp. I found essentially no evidence the recorded model exploited it. The branch states this limitation in the card, `docs/observation-contract.md`, `docs/architecture.md:131` and the dispositions ledger, and repairs the typed packet unconditionally. Accurate as documented (G1-01, G4-1, C4-1, M3-03).
- **The 9p2i meeting is a vent detector.** 68/68 meetings with a grounded vent sighting eject an impostor; the other 83 split 56 skips / 14 correct / 13 wrongful. In 4p1i, 19 of 20 correct ejections carry a spoken vent; none of the 15 skips or 4 wrongful ejections do. A first-hand witnessed kill has no speakable structured shape by default (`crewmate_report.j2:130,151`, gated on testimony shapes): 5 meetings across 190 where someone privately witnessed a kill, 0 spoken `saw_kill` rows, one clean trace (4p1i seed 22) where the eyewitness's accusation moved the listener by +0.08 and the impostor survived. Retained as unadopted candidate 15 (G1-03, G2-8).
- **The alibi-contradiction channel is anti-informative on 9p2i** (G2-2, pre-existing): 50 of 57 non-vent contradictions name a crewmate; 6 of the 7 ejections it drove removed an innocent. The detector is precise (1 false positive in 199 true crew alibis); the asymmetry is volume and exposure, because crew templates require an alibi and a whereabouts and impostor templates require neither. Worth publishing as a headline number beside the "new detector kinds need measured false positives" rule.
- **Structural role tells in the public record** (G2-3, G3-4; disclosed as A-2/A-30 and the self-report arm): 112/112 impostor reply turns carry zero observations and 76/76 crewmate replies carry a whereabouts; 151/151 9p2i meetings and 39/39 4p1i meetings were called by a crewmate. The recorded model does not exploit either; 7 of 13 wrongful ejections removed the necessarily innocent reporter.
- **One turn per player** (G1-04; accepted): 61 of 103 accusations in 4p1i are never answered; three of the four wrongful ejections eject a player who never replied. `select_bounded_rebuttal` names exactly the wrongly ejected player in all four, but `bounded_rebuttal_version` is OFF.
- **Nothing refutes a false impossibility charge** (G1-05; accepted): 2 of 4 wrongful 4p1i ejections turn on an "impossible" ENGINEERING↔STORAGE transit between rooms that share a door in the map card printed in the same prompt. The evidence candidate (OFF) renders a travel check.
- **Lexicographic same-tick resolution** (G2-1, G5-4; retained deliberately): all 39 rejected 9p2i kills have one shape (the target's id sorts before the killer's and it moved first); escape counts by seat run p-1 9 … p-8 0, p-9 0; the lowest id won all 101 contested report ticks across the four sets; the spectator labels the losers "BLOCKED" like refused actions.
- **Movement breadcrumb asserts unwatched transitions** (G1-02, pre-existing, and the only gameplay mechanism I could not find in any register): `agents/memory/store.py:1039-1046,1080-1083` renders "(moved from X, last seen there at tick t)" from the observer's two most recent sightings with no tick or adjacency bound; 24% of 4p1i suffixes span more than one tick; 14 spoken `saw_move` rows across the corpora restate such a suffix as a watched transition, 2 between non-adjacent rooms (9p2i seed 13 meeting-2 is the ground-truth case). Verifiers lowered severity because the harm chain in the corpus is small, but it is a render-fidelity defect worth a card.
- **Body-proximity suspicion is anchored on discovery, not death, and ignores public knowledge of death** (G4-5, M3-01; pre-existing; `agents/memory/beliefs.py:1177-1193`): the code is DESIGN §6.3 Rule 1 as specified, so this is priority 16's second clause unimplemented rather than a bug; 167 reports in the 9p2i corpora concern a victim already announced dead.
- **Privacy lenses are a client render gate.** The API and the static bundle carry roles, kill attribution, every ballot's rationale and confidence, and every agent's memory and model bodies (G5-5, C5-5, C7c-9). This matches the documented privileged-reader design and is unchanged from main; the card says so. The commit title "enforce private spectator lenses" and the e2e test name "must not expose private memory" should not be read as a server-side guarantee.
- **Highlights are dark for the only scored set** (G6-3, C5-3, C7b-7): the committed 9p2i rubric has no `source_fingerprint`; main served 50 stale rows behind a banner, the branch serves none. Justified by a real corruption (16/50 meeting counts and 9 endings disagree with the recordings, recomputed) and disclosed; but a whole feature is empty in the shipped demo until someone re-extracts facts.
- **Clocks.** Agent-facing observation ticks are one greater than the engine tick of the event they describe (G5-3, G6-6); disclosed in the transport caption and the evidence panel, mitigated by the scene-frame jump; the meeting transcript and the curated case prose still quote the agent clock without a scene link.
- **Clean-checkout limits, now bounded.** The seven evidence-branch artefacts are absent on a fresh clone until `scripts/fetch_evidence.sh` runs, which `docs/ml-program.md:176`'s `--complete` claim does not say (P1-4). With them restored everything passes, and the restored Wave-2 record also demonstrates a main-branch defect the branch fixes: under a bare environment main's cost summary published decisive-outcome splits (for example 0.72/0.28) computed over games its own loader had refused, whereas HEAD reports `decisive_split={}` with `verified_outcomes=0` (WAVE2-03; `api/replay_loader.py:997`). `docs/artifacts.md:176` still quotes the Phase-19 figure "OK: 2953/2953" where the command now prints 3269/3269 over two pins (GAP-MLEV-3). No failed or partial recorded game exists in the tree, so that part of the gameplay brief could only be exercised with constructed fixtures and fresh fake-provider runs.

## 9. Findings refuted or withdrawn

For transparency, the adversarial pass removed these as defects:

- C7a-1 (aborted-meeting spend missing from served meetings): the metadata/meeting divergence is real but is the documented, tested contract; the claimed CostChips copy does not appear for that payload.
- P1-2 (missing Co-Authored-By trailers contradict the README): the counts are right (28/28 commits carry the owner as sole author with no trailer; the last 60 main commits all carry one) but no document states a trailer convention and the README makes no git-metadata claim. Recorded as a process observation in section 11.
- G3-2 (meeting-reset effect dominated by corpse deletion): the bundle is exactly what the acceptance line requires ("together"), and the lens's decomposition numbers did not reproduce against the committed evidence. The decomposition idea survives as an optional suggestion for any future adoption decision.
- C5-4 / C7c-3 (branch-only pinned commit will 404): reachable-commit retention is not something that could be shown; downgraded to the post-merge re-pin note above.
- C7b-9 (`sys.path` mutation in the rubric lab script): pre-existing pattern, out of scope.
- P1-5 and G4-9: refuted on inspection (the ledger's `/tmp` citations are a process issue, kept under P2-7; the movement observation's destination naming is by contract).

## 10. Gameplay-first synthesis

What the recorded games actually show, independent of the cards, and then how the branch's account compares.

Default play is unchanged by the branch in every byte that matters: 22 fresh fake-provider seeds across both rosters and the 100 canonical reconstructions agree with main. So the gameplay findings describe the state the branch inherits and documents, plus the experiments it adds OFF.

The decision channel is essentially singular (vents), the accused rarely gets to answer, the reporter is always innocent, the crew's strongest evidence (a witnessed kill) is mute, and the alibi detector spends its output on honest-but-sloppy crewmates. The two-impostor pair coordinate only by not naming each other; the firewall is absolute (0 teammate ballots or accusations in 869 ballots and 738 accusations) and it also prevents an impostor from cutting a caught teammate loose. Bodies behave correctly (only the triggering corpse is consumed; 96 undiscovered corpses per 50 9p2i games persist as reportable evidence; 0 duplicate reports; 25 same-tick multi-reports resolved by id order). Positions and cooldowns persist across meetings, so 28 kills in 151 meetings land within two ticks of a meeting and 13 of them kill the caller. Sabotage is dormant (0 reactor starts in 50 4p1i games; 10 starts/8 repairs in 50 9p2i games; no sabotage win anywhere). Oscillation is an impostor artifact (14/14 purposeless round trips in 4p1i, 48/62 in 9p2i are impostors); crew reversals enclose real actions. Vent entries are rarely seen (18/115) but exits often are (62/97), because the default exit ignores destination occupancy. Fake tasks are perceptually perfect but an impostor can never name the task the table watched it perform.

On resetting locations at meetings: it exchanges one problem for another. The committed arm moves survivors, clears every corpse and restores full cooldown in one call, which is exactly what the acceptance line requested; measured, it eliminates post-meeting execution of the reporter and the alone-with-the-impostor state at the cost of far fewer body reports and a clean slate for the impostor. Any adoption decision should separate the three levers first (an optional suggestion, not a defect).

The experiments, when enabled, work end to end: all nine tactical arms and the evidence/reply/temporal levers run as real recorded games, stamp their configuration on every tick row and the footer, reconstruct through the readers, and refuse the wrong consumers. None is adoption-ready and none claims to be (section 12).

Comparison with the branch's account: every gameplay mechanism above except the movement breadcrumb is already named in the dispositions, the reasoning card, or the tactical README, and every recorded-model baseline number I recomputed matched (wins, meetings, witnessed exits 62/97 and 18/39, witnessed kills 3/182 and 1/62, corpses after meetings 3/96, longest finished wait 9/17, 39 meetings vs 40 triggers). The branch under-emphasises two things it knows: the role-conditioned precision of the existing alibi channel, and that every reasoning metric on this corpus is measured in a world where the reporter can never be the killer.

## 11. Portfolio and workflow synthesis

For a fresh engineering reader the front door works: README (1,439 words, machine-budgeted to 1,600) → reading guide → architecture → workflow → card. Nineteen concrete README/docs claims were traced to code or committed evidence and all held, including the impostor win rates, the 95/0.915/0.863 report figures, the 333/333 vs 50/96 and 11/20 FINDING cells, the four import contracts, twenty-one graduated keys and five OFF toggles, and the final gate counts. `scripts/check_doc_facts.py` re-derives the README's numbers, resolves every relative link in nine published documents and budgets the front-door pages; it is the strongest workflow artefact in the tree. The three curated cases are machine-checked against the recording bytes at build time and one of them is the system convicting an innocent; the tour and header state author, AI authorship and separate AI review; limitations (default body-ID exposure, the unoverridden FINDING, tactical losses, absent archived ML bytes, "not the --complete claim") are discoverable from the README and reading guide without opening an audit.

What a hiring reviewer would still catch: the media doc (5.6); the definitional 100% (5.7); the demo deep link that lands on a case-free tab until the branch is deployed (P1-3); the `--complete` command failing on a clean clone (P1-4); `/tmp` paths cited as the final-gate record; and `agent_prompts/` (390 files, 56k lines, 6.6 MB of fully regenerable output) dominating a first `ls` while `compute_next_task.py` still prints a "dispatchable now" list of long-finished foundational tasks.

The card workflow versus the phase–task prompt workflow: it is a real simplification. One canonical file per change, seven required sections plus Results, six delivery states that refuse to collapse green tests into adoption, dispatch by path with no generated copies, and validators for structure. Its weaknesses are one kind: the project built excellent enforcement machinery and did not point it at its own process documents. Concrete simplifications, in order of value per hour:

1. Add three `check_doc_facts.py` rules: card count/state in `tasks/README.md` and the ledger equal `tasks/work/*.md`; roadmap rows are exactly 1..N; disposition IDs equal the union of the two registers. (Today a card flipped to `active` breaks four aggregate sentences and no gate notices.)
2. Require each card's Validation to contain at least one backticked command other than the two global gates, and each done card's Results to contain at least one; eight lines in `validate_work_cards`.
3. Commit a one-page review note per batch under `audits/` instead of citing `/tmp`; the ledger's reviewer attributions are currently unfalsifiable from committed bytes.
4. Refresh `docs/workflow.md`'s pilot section to the final batch and change `AGENTS.md:5`, which still says `tasks/README.md` names the active queue.
5. Delete `agent_prompts/` (the validator proves it is derivable) and either retire `compute_next_task.py` or make it announce itself as historical; retain `tasks/phase-*.md`.
6. Decide the post-merge branch policy: `codex/cleanup` is hard-coded in AGENTS.md, 15 Markdown files and `ci.yml`, and no card commits to removing it.
7. Document the commit-trailer convention one way or the other; the branch's 28 commits carry the owner as sole author with no agent trailer while the prose attribution is scrupulous.

Commit hygiene: bodies are excellent (card paths, gate counts, limitations). Two commits are hard to review (3a1e64ac mixes four concerns across 47 files; ee46d114 mixes three cards with 44k lines of artefacts) and two intermediate commits are red on one snapshot test. Behaviour was reviewed per commit regardless; nothing hidden was found in the integration commit 1843b1b2.

## 12. Experiment adoption assessment (separate from merge readiness)

| Experiment | Merge-ready (OFF, stamped, refused by wrong readers) | Enabled path works | Adoption-ready | Notes |
| --- | --- | --- | --- | --- |
| `temporal_observations` (AILIBI env) | yes | runs, stamps, reconstructs, leak scan passes | **no** | ON introduces prompt-internal contradictions: event rows on the engine clock beside a route on the snapshot clock (40/310 same-room event lines contradicted the route ON vs 2/296 OFF across 9 seeds; e.g. an agent told it witnessed a vent in a room while its route says it was inside a vent elsewhere). Same-tick crossings are witnessed only when the arriver's id sorts first (G4-2, G4-3). Temporal batches reach dead agents (G4-7). `MovedEvent.witnesses` uses a looser definition than kill/vent and has no independent checker (C1-03, G4-4). The packet census reports the kill, vent and movement channels as zero under this lever (GL-3). The card correctly does not claim adoption. |
| `evidence_reasoning_version=1` | yes | renders death bounds and a travel check; hearsay excluded by provenance | no (correctly unclaimed) | Travel counterevidence covers only the most recent differing-room pair per subject, dropping earlier intervals including a witnessed impossibility (M3-02, undisclosed); public-death knowledge never reaches the proximity rule (M3-01). |
| `bounded_rebuttal_version=1` | yes | inert with the fake provider; the scripted harness adds exactly one call | no | Correction and wrongful-ejection rates are structurally undefined (0 eligible model ballots), stated plainly. |
| Tactical arms (9) | yes | all run, all stamped, all reconstruct; three unlisted combinations also complete | no | Losses published; effective sample sizes not (section 7). `post_meeting_retarget` inert under `meeting_reset`. |
| Legacy levers (`reporter_reasoning`, `corroboration_discipline`, `testimony_shapes`, `impostor_roll_call`) | unchanged, OFF | only under `AILIBI_PROMPT_SET=qwen3_6_27b`; default set refuses loudly | no; FINDING preserved | The prompt-set constraint is not restated in the disposition. |

Nothing on the branch supports adopting any arm, and the artefacts say so consistently. Fake-provider games establish mechanics only.

## 13. Completion matrix (49 priorities)

Classifications: D = implemented and verified in default behaviour; X = implemented and verified behind an OFF experiment; R = explicitly retained with a defensible rationale; P = partially implemented. No priority was unverified or incorrectly marked complete.

| # | Card | Class | Note |
| --- | --- | --- | --- |
| 1 | report-destinations | D | reproduced main overwrite vs HEAD refusal; scope limited to selected seeds (section 6) |
| 2 | completed-meeting-attempts | D | write-chokepoint proof 1 row/$0.01 on main vs 2/$0.02 on HEAD; cross-consumer reconciliation is a real test |
| 3 | evaluation-replay-integrity | D | forged winner and reorder accepted on main, rejected on HEAD, including with `derive_kill_gift=False` |
| 4 | report-completion-status | D | spend visible with `verified_outcomes=0`; four states distinct |
| 5 | report-completion-status | D | durable `game_stopped` row; deleted stop degrades to unfinished, never to tick-limited |
| 6 | tournament-lifecycle | P | progress, binding, kill -9 resume all work; limit-stopped runs cannot be resumed (section 6) |
| 7 | tournament-lifecycle | D | caps carry across seeds and resumes; not preemptive of synchronous Python (disclosed) |
| 8 | public-recording-provenance | D | suppression verified on the real stale 9p2i rubric; 16/50 and 9 mismatches recomputed |
| 9 | public-recording-provenance | D | pinned capture revision hashes verified against git history |
| 10 | public-recording-provenance | D | journey re-executed; the card's bundle numbers are stale (154 files → 156) |
| 11 | dependency-advisories | D | npm and pip audits re-run today on both checkouts: 5+6 findings on main, 0 on HEAD |
| 12 | temporal-observation-contract | P | packet handle repaired unconditionally; opening prompt repaired only ON |
| 13 | temporal-observation-contract | D | channel matrix, audible gate with 8 planted cases, live-vs-reader parity test |
| 14 | reasoning-evidence-experiments | D | scorecard reproduces bit-for-bit; 152 sources and 300 inputs re-hashed; held-out population narrower than the plan (C4-3) |
| 15 | reasoning-evidence-experiments | R | FINDING preserved; levers still work under the qwen3_6_27b set only |
| 16 | reasoning-evidence-experiments | P | death bounds render; the movement-after-public-death clause has no mechanism ON or OFF |
| 17 | reasoning-evidence-experiments | P | travel check renders with legal/impossible controls; last-pair-only coverage undisclosed |
| 18 | reasoning-evidence-experiments | X | one extra call, no recursion; correction/wrongful rates undefined by construction |
| 19 | reasoning-evidence-experiments | D | hearsay excluded by provenance; 645 vs 638 independent flags reproduces |
| 20 | reasoning-evidence-experiments | X | coalescing loss quantified (3 kept, 1 rendered at every budget); candidate-only repairs |
| 21 | tactical-gameplay-experiments | X | reproduced; 4p half rests on 4 of 16 games |
| 22 | tactical-gameplay-experiments | X | patrol and accompany; "investigation" neither built nor recorded as dropped |
| 23 | tactical-gameplay-experiments | X | provenance-gated risk; 4p row rests on one game |
| 24 | tactical-gameplay-experiments | R | guard deleted; retained-controls hashes match current baseline 16/16; acceptance text rewritten in the checking commit |
| 25 | tactical-gameplay-experiments | X | thin effect; trigger is any concluded meeting |
| 26 | portfolio-evidence-experience | D | 176/176 cited observations resolve to text and a scene; forged ids disclosed; one malformed-URL hang (M5-01) |
| 27 | portfolio-evidence-experience | D | every denominator recomputed; tampered outcome refuses publication |
| 28 | portfolio-evidence-experience | D | verified in the bundle with no API |
| 29 | portfolio-evidence-experience | D | both source sha pins verified; cases reconstructed independently |
| 30 | portfolio-evidence-experience | D | README 1,439 words under a machine-enforced 1,600 |
| 31 | portfolio-evidence-experience | D | journeys reproduced; clean-clone evidence is `/tmp`-only |
| 32 | replay-loading-performance | D | 86.2% byte reduction reproduced at HEAD |
| 33 | replay-loading-performance | D | every table number recomputed; after-capture bound to an earlier tree |
| 34 | map-traversal-contract | D | `traversal_ticks=2` accepted on main, rejected on HEAD |
| 35 | cleanup-synthesis | R | 16 new modules with production callers; the two named large modules grew; no new contract |
| 36 | model-evidence-provenance | D | roster mutation moves v2 and not v1; enabled experiments refuse campaign |
| 37 | protocol-retirement | D | no producer, reference or recording carries the retired cue; slot pinned to 0.0 |
| 38 | audit-fact-gates / carried / semantic | D | byte gate, CommonMark link gate, corpus scan all reproduce; section-5 IDs dispositioned in prose only |
| 39 | cleanup-iteration | D | pilot evaluated without time-saving claims; intermediate numbers `/tmp`-only |
| 40 | cleanup-iteration | D | 235 → 90 lines; every rule located in AGENTS.md or agent-procedures.md; nothing pins that |
| 41 | cleanup-iteration | D | 26 ledger SHAs resolve, none an ancestor of main; 6775+20+3 = 6798 collected |
| 42 | cleanup-iteration | D | A/B registers untouched; retirement executed; the branch's own reviews left no notes |
| 43 | tactical-gameplay-experiments | R | 3,550 interventions reproduce; deterministic order retained |
| 44 | tactical-gameplay-experiments | X | reset covers all five things together, by design |
| 45 | tactical-gameplay-experiments | X | self-report measured; role-tell half is a retained disposition |
| 46 | tactical-gameplay-experiments | P | sabotage half explained by configuration; task-victory half not |
| 47 | cleanup-synthesis | R | tally byte-identical to main; 98 parity tests; trigger unmet |
| 48 | model-evidence-provenance | D | all three counts recompute; refusal and historical restoration both exercised |
| 49 | cleanup-synthesis | R | no new map, provider or deployment on the diff; agent-authored disposition awaiting the owner |

Card audit: 21 of 26 cards verified with independent evidence for every acceptance box that can have it; 5 partially verified (cleanup-iteration, cleanup-synthesis, dependency-advisories, model-evidence-provenance, replay-loading-performance), all because a box is prose-shaped or its evidence is `/tmp`-only or bound to an earlier tree; 0 unverified; 0 incorrectly marked complete.

## 14. Prioritised correction plan

**Required before merge** (one short fix batch; each has a reproduction in section 5): 5.1 stale report projection or regeneration; 5.2 verdict-panel confidence; 5.3 stale-rubric card copy; 5.4 lazy `begin_recording`; 5.5 no pre-loop publish; 5.6 media doc; 5.7 caption clause; 5.8 test import bootstrap; 5.9 fixture terminal. Then re-run `bash scripts/check.sh`, `bash scripts/verify_samples.sh`, `scripts/build_sample_report.py --check` on all four sets, and `pytest tests/orchestrator/` alone.

**Important follow-up** (next cards): resumable limit-stopped tournaments or documented dead end; output-directory-wide report-destination protection; `/eval/summary` memoization; ballot-tally check in the current walk and validator, or narrowed `outcome_verified` docstrings; experiment label in `GameReport` and an unconditional factory/config check; the temporal ON clock reconciliation and order-independent move witnesses before any temporal adoption; effective-sample-size column in the tactical README; re-capture or re-label `after.json`; workflow rules 1–4 in section 11.

**Optional portfolio improvements**: delete `agent_prompts/`; retire or relabel `compute_next_task.py`; add the movement-breadcrumb defect to the disposition ledger; publish the alibi channel's role-conditioned precision and the "reporter is always innocent" caveat beside the deduction metrics; restore the README hero caption; land the tour on a game with beliefs; fix the meeting-overlay header overlap (pre-existing); re-pin source links to a main commit after merge.

## 15. Complexity and overhead worth removing

- `agent_prompts/` and the prompt-sync leg of the gate: 40% of the repository's Markdown, zero information beyond the contracts plus the template.
- `compute_next_task.py`: still runs, still prints a to-do list of finished work; two documents exist only to tell readers to ignore it.
- Five hand-maintained completion statements where one derived count would do.
- Ephemeral-log citations in cards and the ledger; a committed one-page note per batch replaces 49 of them.
- The branch-name policy in AGENTS.md and `ci.yml`, which becomes stale the moment this merges.

## 16. What remains unverified

A machine-readable list of every finding that survived adversarial verification, with anchors and refuter verdicts, is in the companion file `REVIEW_APPENDIX_findings.md`.

- Evidence-branch bytes on a fresh clone without the local refs; on this machine they restore and verify (section 3).
- Real-model behaviour of any arm; every fresh game used the deterministic fake provider and no reasoning-quality inference was drawn from it.
- The tactical held-out split was recomputed by two lenses and the development split by three; the 432-game harness was not run from a cold cache more than once.
- Power-loss durability (no fsync) beyond process kills; the process-kill and concurrent-writer cases were probed (section 7).
- Whether the named independent reviews in the ledger happened as described; no committed artefact exists, only corroborating adverse tests.
- Real-provider cancellation and usage reporting under the run-limit machinery.
