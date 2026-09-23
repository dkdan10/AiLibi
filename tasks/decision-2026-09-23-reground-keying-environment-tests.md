# Decision memo: the baseline-9 re-ground and the nine non-ML reds

Synthesizer, 2026-09-23. Tree: `main` at `95fb894b`, and every file:line citation is at that
commit. Inputs: the four memos in this directory (`keying.md`, `environment.md`, `signals.md`,
`bugs_other.md`) and the four refuter verdicts relayed with the task. The orchestrator acts on
this file.

**Ground rules I kept.**
- I stayed read-only: no tracked edit, no commit, no push, no PR comment.
- Nothing was written under `training/artifacts/`.
- No provider call, no `.env`, no `--complete`, no recorder, no held-out generator.
- My probes ran in a scratch venv (`UV_PROJECT_ENVIRONMENT` outside the tree). The worktree was
  clean afterwards.
- Every census is count-only, and role-correctness gates nothing.

## 0. The owner rulings this memo executes (2026-09-23, verbatim)

- **Q1 keying:** "Look into how it should best be fitted and implement your recommended strategy."
- **Q2 campaign tier:** "Go with your recommendation."
- **Q3 container:** "The previous Linux environment used was a Claude code session dispatched to the web."
- **Q4 verdict flips:** "Publish and wait for the merge."
- **Q5 the nine non-ML red tests:** "Look into why the tests would still fail, if they are necessary at all, or a separate potential path forward. Go with the recommended idea from that."

**How each ruling is read here.**
- **Q1** delegates both the keying choice and its implementation. Section 2 decides it.
- **Q2** takes the card's own recommendation: the campaign tier is in scope as tests, with no
  re-search and no campaign re-run.
- **Q3** answers the card's Q3, which reads "Without one the card stops before the Goodhart leg".
  The container for the Goodhart leg is therefore a Claude Code web session on Linux.
- **Q4:**
  - A GO/NO-GO flip publishes as it reads and is named first in the PR.
  - The orchestrator waits for the owner's merge, and nothing downstream is re-pointed.
  - I apply the same rule to the other published-cell class the card names: a changed adoption
    constraint set. The alternative would be a separate stop that no answer asked for.
- **Q5:** each of the nine was root-caused, and the recommended path is taken: cards B and C
  below. Two consequences:
  - The re-ground card is done when its failing ids are a subset of the ids B and C own.
  - Whichever of the three PRs merges last must show `bash scripts/check.sh` fully green on `main`.

## 1. Facts re-checked: the ones refuters disputed, and those decisions hang on

| # | fact | re-check at 95fb894b | result |
|---|---|---|---|
| 1 | No committed plant proves the refit pins bite (keying refuter) | The only +0.125 plant, `tests/training/test_model_evidence_provenance.py:54-79`, moves `fit_corpus_fingerprint` (v2) only. The refit pins (`tests/training/test_surrogate_runner.py:809-880`, `tests/training/test_conviction_model.py:803-855`) have no perturbed twin. | CONFIRMED |
| 2 | How README:42-48 should be read | `training/README.md:42-43` reads "Current use fails until a newly adopted corpus supports a separately authorized fit". `:48` says a future fit "must write" version two. `docs/ml-program.md:210-216` requires a new independent-evidence profile before a newly adopted corpus supports a refit, and forbids reinterpreting old weights through it. | Refuter's reading CONFIRMED. The version-one ruling rests on ml-program:210-216 and overrides README:48's plain reading under Q1. |
| 3 | The filtered-BC writer stamps a v2 kind | `training/anchor_study.py:1351` writes `substrate_sha_kind` v2. The config model accepts `None` (`:1256`). The docstrings at `:222-226` and `training/bakeoff/map_elites.py:712-716` say the historical definitions only restore old artifacts. | CONFIRMED |
| 4 | Churn: 15 of 37 vs 14 of 36 merges | Not re-measured. `git log --first-parent --merges --since=2026-09-06 95fb894b` lists 39 merges, so the two replicas differ at the window edge. | Not decision-relevant. The implementer quotes its own figure with the command. |
| 5 | Why STALE was deleted | `tasks/phase-21.md:4583` and `:4644-4650`: the gap was closed, B-20, B-46, and "Resist the pull to reintroduce a downgrade path". | Refuter CONFIRMED |
| 6 | Platform exposure inside the rollouts | `agents/tactical/features.py:873` calls `math.tanh` in `mlp_forward`, which `training/bakeoff/goodhart.py:92` imports. `training/surrogate/ballots.py:652` and `training/conviction/model.py:344` call `np.exp`. | CONFIRMED. The environment memo's portability paragraph is wrong. |
| 7 | "The head runs the same code" | `git diff --name-only 39a568c6 95fb894b`: nothing changed under `training/`, `uv.lock` or `pyproject.toml`. Seven code files did change: `api/public_results.py`, `api/replay_loader.py`, `api/routes/eval.py`, `eval/deduction_metrics.py`, `eval/report_io.py`, `eval/vote_correctness.py`, `eval/watchability.py`. The last one adds the baseline-9 floor block (`:1039`) and the default id (`:1129`). | CONFIRMED. New consequence below. |
| 7a | NEW: the leg's floors follow the baseline id | The leg scores through `compute_watchability(directory, baseline_id=...)` (`training/bakeoff/goodhart.py:454-456`), and its default is the literal `"baseline-8"` at `training/composed_runner.py:1247`. | The constants must move BEFORE the baseline-9 leg runs. The card's order puts them after the composed step, so it is amended. |
| 8 | How a web session hands work back | There are 282 `origin/claude/*` branches, and no `work/*-proof` branch has a precedent. | CONFIRMED: use the session's own `claude/` branch. |
| 9 | GitHub Actions meets the container definition | `campaign-tier.yml:28` (`workflow_dispatch`), `:59` (`setup_env.sh`) and `:64` (`pytest -m campaign`) run on `ubuntu-latest`. `ci.yml:54` runs `bash scripts/check.sh`, with the frontend in its own job. | CONFIRMED |
| 10 | Channel builders already exist | `tests/eval/test_evidence_honesty.py:2417` (move), `:2463` (vent), `:3008` (sighting), `:3126` (`_grounded_census`). | CONFIRMED |
| 11 | The existing move builder drifts from the live accessor | `orchestrator/game.py:4024` drops the holder's own rows (`player_id == self.agent_id`). `tests/eval/test_evidence_honesty.py:2417-2460` does not. | CONFIRMED on the code. The 675/676 count is the refuter's and was not re-measured. |
| 12 | "Kept can exceed offered" | `tests/agents/test_reported_testimony.py:956-958` | CONFIRMED |
| 13 | Walks are per worker | `scripts/check.sh:41` runs `-n auto --dist loadfile`. | CONFIRMED |
| 14 | Direction 1 of the adjacency census is vacuous | `tests/eval/test_evidence_honesty.py:3649-3658` makes identical `detect_contradictions` calls for off and on, so `demoted` is 0 by construction. | CONFIRMED |
| 15 | The FROZEN refusal fires only on graduation | `scripts/counterfactual_phase21.py:4130-4153` fires only when a lever is unregistered or graduated. The three Phase-21 levers are still live toggles. | CONFIRMED: the precedent `efcd43b8` does not transfer as it stands. |
| 16 | The fixtures precedent `70e49468`, and its cost | `tests/fixtures/baseline8_exhibits/` exists. Measured at `39a568c6`, the baseline-8 replay JSONL is 115,886,311 bytes in 300 files (233,746,908 with the tournament reports). | Path CONFIRMED. The cost was re-measured; the refuter's figure was about 158 MB. |
| 17 | Stale "one segment" docstrings | `meetings/schemas.py:406-408` and `eval/evidence_honesty.py:2295-2297` | CONFIRMED |
| 18 | NEW: the adjacency guard's 29 flags come from a pre-grounding re-derivation | My count-only probe; see the next paragraph. | This AMENDS the `bugs_other` refuter's severity claim. |

**Row 18 in detail.** `_corridor_census` passes no sighting mapping
(`tests/eval/test_evidence_honesty.py:3649-3658`). With no mapping, `meetings/transcript.py:1836`
keeps the pre-grounding rules, so the census's STRONG population is a counterfactual that
production never runs.

Of the 42 STRONG `alibi_vs_sighting` flags it re-derives, 29 are adjacent and kept STRONG.
Matching those 29 to the recording by kind and both event ids gives:

| in the recording | flags |
|---|---|
| recorded STRONG: `ml_corpus/9p2i` seed 1041 meeting 1, with a stay-relative gap of 0 | 1 |
| recorded weak | 5 |
| never minted | 23 |

Across all four sets, the recording holds 1 STRONG and 45 weak `alibi_vs_sighting` flags.

So the refuter was right that the guard exposes a real rule question: one-tick fuzz at an
interior, declared stay boundary. But in the committed bytes, the production instance of that
class is exactly one flag, and it is the same meeting T2 names.

## 2. Keying (Q1): decision

**Decision.** Key the baseline-9 surrogate and conviction records to version one:
`SurrogateFitCorpus(corpus_set="9p2i", corpus_sha256=historical_fit_corpus_fingerprint(C), fit_side_meetings=355, weights_sha256=<new digest>)`,
with no `fingerprint_version` argument. It defaults to 1 and is excluded from the JSON
(`training/surrogate/runner.py:414-416`).

- **Stamps.** Every stamp uses the historical definitions, in the committed shape with no kind
  field. That covers the filtered-BC `config.json`, each lambda `config.json`, `study.json` and
  the pool index.
- **Version two** stays the identity that a current install mints, at the commit that installs
  it.
- **The derivation certificate is measurement.** It is made of the two refit-equivalence pins
  and the verifier's recompute rows, now backed by a committed perturbed case.

This is the investigator's recommendation, which the refuter did not overturn (refuted=false).

**Why.**
- Version two binds a 109-file import closure, of which only 40 files execute during the fits.
- The committed fits reproduced byte-for-byte across the closure churn from `1793eb23` to
  `39a568c6`. That churn is the reason the default-OFF gates of craft rule 7 exist.
- A version-two key would redden `check.sh` on roughly 40% of merges without the fit moving.
- `docs/ml-program.md:210-216` makes this a re-fit of the *historical* raw flag-count
  instrument. A fit a current consumer could install needs the new independent-evidence profile
  first.

**Objections.**

Accepted:
- **Craft rule 2.** Add one committed perturbed case per instrument beside the refit pins.
- **Deferred cost.** Results states that the first current install must mint version two at its
  own commit, and that it inherits:
  - the verifier and test inversions in `keying.md` section 4 row (b);
  - the closure churn.

  The fit-closure scope, and not only the stamp scope, goes to the owner (OPEN 2).
- **Precedent.** Cite `docs/ml-program.md:210-216` as the reason. Record README:48's plain reading
  as overridden by the dated Q1 ruling; do not claim the documents already agree.
- **Hand-edit.** Quote the filtered-BC `config.json` transformation as an idempotent command.
  Update the two `historical_*` docstrings in scope (comment-only).
- **STALE motive.** Cite the 21.17 contract's reasons, not "pressure".
- **Labels.** Name the ruling by function everywhere: `historical_fit_corpus_fingerprint`,
  version one. The card's letter-keyed "Q1 (a)" clauses are marked not applicable:
  - verifier edits;
  - the genuine-class ordering, which merged anyway as #478;
  - the record-impact sentence about the 109-file closure.

Partly accepted:
- **The churn figure.** Its direction holds. The implementer quotes whatever it measures, with the
  command.
- **The README sentence as a standing rule.**
  - The sentence is limited to the historical raw flag-count instrument (surrogate and
    conviction), dated to the 2026-09-23 ruling, and names its enforcing tests.
  - It says the filtered-BC anchor has no refit pin.
  - It does not bind a new-profile fit, which writes version two.

  The rest is not accepted: a re-ground of the same historical instrument is exactly what the
  sentence should govern, and leaving it per-card would re-open Q1 at every record.

**The README sentence.** It replaces `training/README.md:48-49`, and the rest of that paragraph
stays:

> Re-grounds of the historical raw flag-count instrument (the ballot surrogate and the
> conviction model; ruled 2026-09-23) keep version-one records: their derivation is checked by
> measurement, not a source digest, by
> `test_surrogate_runner.py::test_committed_artifact_round_trips_and_the_refit_no_longer_matches`,
> `test_conviction_model.py::test_committed_artifact_round_trips_and_the_refit_no_longer_matches`
> and `test_verify_ml_evidence.py::test_recompute_reads_every_committed_verdict_against_the_live_corpus`;
> the filtered-BC anchor has no refit pin. A fit a current consumer installs writes
> `SurrogateFitCorpus(fingerprint_version=2, ...)` with `fit_corpus_fingerprint(corpus_dir)` at
> the commit that installs it.

## 3. Environment (Q3): decision

**Decision.** Split by what each step is exposed to, and keep the card's gate direction.

| step | runs on | gate or proof |
|---|---|---|
| reproduction at `39a568c6`: fingerprint, verifier subset, three GD refits, pool re-stamp | this Mac (Darwin arm64) | byte match to the committed digests, quoted with the host stamp. The Mac Goodhart leg is reported beside, not gating. |
| surrogate, conviction and filtered-BC refits on baseline 9 | this Mac | reproduction byte-matched here, as card rows :229-230 allow. Linux ULP-equivalence is re-checked by the PR's CI round-trip pins. |
| composed fidelity, verdict writers, `walk_corpus`, stamps, constants | this Mac | frozen-weight inference, a deterministic engine, and sha256 |
| **the composed Goodhart leg** | **a Claude Code web session on Linux x86-64 (Q3). Required and gating.** | R1 at `39a568c6` must reproduce the report's section 6.1 and 6.2 cells and both constraints. R2 at the branch head, after the constants move, is the leg that gets committed. |
| `pytest -m campaign` | GitHub Actions `ubuntu-latest`, via `gh workflow run campaign-tier.yml --ref work/ml-reground-baseline-9`. Gating. | 335 passed, or each difference explained id by id. The Mac run is reported beside. |
| `bash scripts/check.sh` | the PR's CI `project-checks` and `frontend-checks` jobs. Gating. | failing ids are none, or a subset of the ids cards B and C own. The Mac clean-worktree run is reported beside. |

**The decision rule for the leg.**
1. **R1:** if Linux does not reproduce the committed cells while the Mac does, stop and report.
   That would put the container rule and the reproduction rule in conflict (OPEN 3).
2. **R2:** compare the Linux and Mac leg JSON.
   - Identical sha256: write the verdict from it and name both platforms.
   - Equal cells but different bytes: write the verdict from the Linux JSON (the container rule)
     and report the byte difference.
   - Any cell differs: stop and report.

   In every case, the leg JSON's `baseline_id` must read `baseline-9`.

**The hand-back.**
- The web session commits one proof JSON, plus the two leg JSONs, to its own `claude/<slug>`
  branch and pushes. The proof JSON holds the host stamp, the SHAs, each command, each digest, and
  a match boolean per comparison.
- The local session fetches that branch and reads the files by commit SHA (`git show <sha>:<path>`).
- It verifies each file's sha256 and quotes the proof in Results by SHA.
- The branch is never merged and never deleted.

**The host stamp**, on every platform and beside every digest:
- `uname -srm`;
- `platform.platform()` and `sys.version`;
- the numpy version and `numpy.show_runtime()` (the SIMD dispatch);
- the CPU model: `/proc/cpuinfo` on Linux, `sysctl -n machdep.cpu.brand_string` on the Mac.

**Objections.** All nine environment objections are accepted:
- the leg is exposed to `math.tanh` and `np.exp` inside the rollouts;
- the Mac's reproduction is same-host repeatability, so Results makes no claim about where 21.17
  ran;
- Q3 was about the leg;
- Actions counts as a container instance, named in card :234 and flagged in the PR;
- the hand-back goes on a `claude/` branch;
- the host stamp names the CPU and runtime SIMD;
- the "same code" sentence is replaced by the measured list in row 7;
- the `test_es` pin is kept out of this card's ES evidence;
- the provenance inference is not written down.

Kept from the memo:
- Mac execution of the GD, fidelity, stamp and constant steps;
- its measured reproduction at `39a568c6`: bytes `06b20508...`, `7e764b89...`, `62595367...`;
  pool `e43335ba...`; leg cells; about 90 s for the whole block.

**A side note.** The auto-memory note `project_es_artifacts_platform_split` is stale: `test_es`
passes on Darwin arm64 since Task 19.3's libm-free sampler. Recording that in
`training/bakeoff/es.py:52-58` is a separate docs item (R-3), and its first line is OPEN 5.

## 4. Signals, T1 to T5 (Q5): decision

**Decision.** Change tests only, now. Make no substrate change and no re-record. The route of 1041
meeting 1 is under S-1.

This is the investigator's strategy, amended on mechanism:
- **One home.** Promote the existing evidence-honesty channel builders into
  `tests/_helpers/committed.py` as the single home.
- **Match the live accessor.** Fix the move builder to drop the holder's own rows
  (`orchestrator/game.py:4024`), carry `observation_id`, and thread `trigger_kind`
  (`meetings/manager.py:1557-1567`).
- **Gate it.** Recorded flags equal the both-leg re-derivation on 676 of 676 committed meetings.
- **Label the re-scopes.** T1 and T2 are re-scopes under Q5, not repairs.
- **Retire the stand-ins.** Remove the records-free machinery whose only job was to stand in for
  the recording.

Per test:

| test | what fails and why | change class |
|---|---|---|
| T1 `tests/meetings/test_contradictions.py::TestGroundedProsecutionCommittedCensus::test_the_fully_grounded_leg_drops_the_whole_class` (`:4133`) | A records-free leg with no movement channel. Even with the true channels, the generous leg keeps 2 STRONG (1041 m1): rule (b) allows two carriers. | Re-scope (test re-anchor): the census moves onto the helper's movement and vent channels; re-pin MEASURED; rename |
| T2 `...::TestGroundedProsecutionInjusticeShapes::test_no_committed_ejection_rides_a_strong_sighting_flag` (`:4174`) | "Empty" was a records-free reading. The recorded class is {`ml_corpus/9p2i` seed 1041 meeting 1}. | Re-scope: read `entry.contradictions`; named-set tripwire; no role asserted |
| T3 `tests/agents/test_reported_testimony.py::test_reported_rows_survive_in_every_candidate_bucket` (`:930`) | The route claim offers more testimony than a saturated 6,000-character render holds; 0.786 is below 0.80. The band order holds. | Re-anchor: retire the met Phase-20 ratio floor; assert band order per render on the selector's kept list |
| T4 `tests/eval/test_evidence_honesty.py::test_the_band_change_not_the_fold_is_what_costs_first_hand_coverage` (`:4185`) | The rows-ordering comparand was deleted at graduation, and row counts are budget-capped. | Retire the rows ordering; rename to what it still measures |
| T5 `tests/meetings/test_transcript.py::TestCommittedBytesArtifactCollapse::test_rederivation_diverges_only_at_the_repaired_sites` (`:1930`) | The records-free harness has no movement channel. With the rebuilt channels, 145 of 145 re-derive exactly. | Re-anchor: pure exactness on the helper |

**Objections.**

Accepted:
- **One home.** Confirmed at row 10.
- **Self-row drift.** Confirmed on the code at row 11. It becomes a planted control.
- **Re-scope labels,** citing Q5.
- **Full docstring blast radius.**
- **1041 meeting 1:** default-OFF, with the labelling variant preferred (S-1).
- **T3 predicate** on the selector's kept list.
- **Cost and ownership.** Card B is the single writer of `tests/eval/test_evidence_honesty.py`,
  and the new walk is registered in `tests/_helpers/test_committed_single_home.py`.
- **T4 rename.**
- **T2 justified in its docstring:** an ejectee holding a STRONG sighting flag plus another kind's
  STRONG flag is inside T2 but outside I-3's sole-flag cell (`test_evidence_honesty.py:1638`).

Partly accepted: **retire the whole records-free harness.** `_rederive` has 21 call sites across
the two files. The rule applied:
- Every assertion that claims to describe the recording moves to the helper.
- Every mechanism that only stood in for the recording is deleted.
- `_rederive` stays only for consumers asserting transcript-level properties (determinism, and
  kinds with no private channel), each carrying a one-line "records-free by design" docstring.
- The implementer lists every consumer and its disposition in Results.

The rest is not accepted: those consumers are live, not dead mechanism.

## 5. The other four (Q5): decision

- **Item 1, the report-tick fog: a code fix in the loader.** The investigator's diagnosis stands.
  The fix re-opens a reported body on a game-deciding `GAME_OVER` tick that carries a
  `MeetingTriggeredEvent` (`api/replay_loader.py`, after `:1692`), and updates the comments at
  `:1698-1701` and `:2027`. Refuter amendments accepted:
  - a measured before/after diff of the demo bundle;
  - the test parametrized over `samples/4p1i`;
  - a vacuity guard.
- **Item 2, the adjacency guard: a test re-anchor plus a test-bug fix, not "test-only by
  construction".**
  - `_endpoint_gap` reads the route's outer ends. That is the detector's designed rule (`301993f7`),
    so the restatement becomes faithful.
  - The 0-as-unset sentinel becomes `None`.
  - A pinned census reports the class instead of blessing it: kept-STRONG adjacent flags within
    `MAP_ARBITRATION_MAX_TICK_GAP` of an interior stay boundary. The record audit reads 26 of 29
    (section 6.4); the implementer measures and pins the count.
  - The docstring states the production reading from row 18: 1 of 29 recorded STRONG (1041
    meeting 1, pinned by T2), 5 recorded weak, 23 never minted.
  - The vacuous direction-1 check and the duplicated off/on legs are deleted under craft rule 3.
  - The rule question goes to S-1.

  The refuter's alternative, landing the sentinel fix alone and leaving the test red for a
  ruling, is not taken. The stay reading holds 26 zeros, so the test would stay red. The ruling
  it waits on (S-1) is a future default-OFF lever, not a reason to keep `check.sh` red. And Q5
  delegated the path.
- **Items 3 and 4, the Phase-21 memo gate: retire the memo-vs-live comparison.** The argument is
  rebased as follows:
  - It rests on the measured/frozen pair rule (`3eebc7d5`): the memo is the frozen side, a
    baseline-8 measurement, and no step re-issues it, since Phase 21 closed FINDING.
  - `efcd43b8`'s graduation trigger does not hold here (row 15).
  - `70e49468`'s frozen-fixture path is named and dismissed on cost (row 16).
  - E.4 cites the last commit where the gate passed, verified by running both tests at `39a568c6`
    before it is cited, together with the exact reproduction command.
  - `docs/artifacts.md:109` is recomputed last in its PR.

  Every refuter amendment for items 1, 3 and 4 is accepted.

## 6. Implementation plan: cards

**Step 0 (orchestrator, one planning commit on `main`).** A `docs:` commit carrying the
following:
- the amendments to card A below;
- new cards B and C, written to `docs/workflow.md`;
- the `tasks/README.md` active list.

Then run `scripts/validate_task_docs.py` and `scripts/check_doc_facts.py`. Workers are
dispatched by card path (AGENTS.md), on opus.

### Card A: `tasks/work/ml-reground-baseline-9.md` (amended)

- **Base:** `main` after step 0.
- **Branch:** `work/ml-reground-baseline-9`.
- **Delivery:** one PR, merged or fast-forwarded, never squashed. Every commit body carries
  `Card: tasks/work/ml-reground-baseline-9.md`.

**Rulings relied on:** Q1, Q2, Q3, Q4 and Q5, quoted in section 0.

**Amendments to the card text.**
1. **Constraints, Q1.** Write "Ruled 2026-09-23: version one (`historical_fit_corpus_fingerprint`)",
   with section 2's reasons. Mark the letter-keyed "Q1 (a)" clauses at :280-281, :311-312 and
   :339-340 not applicable.
2. **Environment table (:227-239).**
   - Replace it with section 3's table.
   - Name GitHub Actions `ubuntu-latest` (Linux x86-64, Python 3.11, `scripts/setup_env.sh`
     locked sync) as the container instance for the campaign tier and `check.sh`.
   - Keep the web session (Q3) as the container for the leg.
   - Acceptance lines :131 and :146 stay ("in the container" = the web session). Lines :212 and
     :216-217 now name the Actions runs.
   - The PR lists the Actions naming as a named deviation (OPEN 4).
3. **Order (:326-327).** The new order is:
   1. reproduction;
   2. surrogate;
   3. conviction;
   4. the constants, with the anchor, study and pool stamps, in one commit;
   5. push; the Mac leg; the web session R1 and R2; the composed verdict;
   6. tests;
   7. reports and documents;
   8. the gates.
4. **Validation (:359-360).** The freeze checks use
   `git diff --stat $(git merge-base origin/main HEAD) HEAD -- engine agents meetings observation orchestrator`
   (and the same form for `replays`, `eval` and `docs/process-scorecard.md`). Card B's
   comment-only edits then cannot trip them after a merge from `main`.
5. **Expected scope additions.**
   - Comment-only docstrings: `training/anchor_study.py:222-226` and
     `training/bakeoff/map_elites.py:712-716`.
   - Two perturbed refit cases: in `tests/training/test_surrogate_runner.py` and
     `tests/training/test_conviction_model.py`.
6. **Q5.** "Done" means the failing ids are a subset of the six card B owns and the three card C
   owns.

**Scope.** Unchanged from the card except as above:
- the artifacts under `training/artifacts/{surrogate,conviction,composed}/`, the anchor study and
  two pool fields;
- `training/bakeoff/harness.py:188`, `training/anchor_study.py:162-172`, and the coupled literals
  `training/bakeoff/goodhart.py:848`, `:1989` and `training/composed_runner.py:1247`;
- tests;
- the four reports, `docs/ml-program.md`, `docs/artifacts.md` rows :103-104, the
  `replays/ml_corpus/README.md` blockquote, one `training/README.md` sentence, and the
  `tasks/README.md` line.

**Steps and writer calls** (section 2; `keying.md` section 5 has the exact calls):
1. **Reproduce at `39a568c6` on the Mac,** in a detached worktree.
   - `historical_fit_corpus_fingerprint` reads `cc54d3c0...`.
   - `verify_ml_evidence.py --only sidecars --only corpus --only recompute` exits 0.
   - The refits give `06b20508...`, `7e764b89...` and `62595367...`.
   - Report the Mac leg and the pool re-stamp beside.
   - Perturbed proof: the refits on baseline 9 do not match.
2. **Surrogate.**
   - Require `raw_mismatches == 0` from `measure_belief_render_parity`.
   - Fit, then `write_ballot_predictor_artifact(..., max_uses=derive_max_uses(355))`.
   - Write `fit-corpus.json` as `model_dump_json(indent=2) + "\n"`.
   - Write the verdict with `write_surrogate_verdict_artifact`.
   - Refresh the report, correcting its section 8 recipe to `historical_fit_corpus_fingerprint`.
3. **Conviction.** The same shape, through `fit_corpus_conviction_model` and
   `derive_conviction_max_uses(355)`, plus the report.
4. **Constants and stamps, in one commit.**
   - `BAKEOFF_BASELINE_ID = "baseline-9"`, plus the three coupled literals.
   - `HIGH_FLAG_FLOOR = 107/145`, which is 17 transcript + 90 persisted vent flags.
   - `run_anchor_study(lambda_grid=(), artifact_root=<scratch>, verify_committed_champion=False)`.
     Copy the weights and their `.sha256` into the tree.
   - `config.json`: drop `substrate_sha_kind` and any `evaluation_evidence_scope`, and set
     `substrate_sha = historical_compute_substrate_sha()`. Do it with one quoted, idempotent
     Python command that re-serializes exactly as the writer does.
   - Each lambda `config.json` changes only `substrate_sha`.
   - `study.json` takes `baseline_id "baseline-9"`, the same sha, and the new `filtered_bc`, whose
     `artifact_path` is reset to `training/artifacts/anchor_study/filtered-bc-anchor`. It gets no
     kind or scope key.
   - Pool `index.json`: `baseline_id` and
     `substrate.substrate_sha256 = historical_bakeoff_substrate_sha()`, with no kind. The 30
     genomes and `filled_cells` are unchanged.
   - Update the two docstrings.
5. **The leg.**
   - Push. Run the Mac leg at the head:
     `run_composed_goodhart_leg(config=ESConfig(generations=6, population=6, sigma=0.5, seed=0, fitness_seeds=tuple(range(8)), init_scale=0.5), evidence_scope="historical")`.
   - Dispatch the web session by card path, pointing it at the card's new "Remote leg" section,
     which lists R1 and R2, the host stamp and the hand-back.
   - Apply section 3's decision rule.
   - Then run `run_composed_fidelity` -> `decide_composed_go` (the constants taken from the
     agreed leg) -> `write_composed_manifest_artifact` and `write_composed_verdict_artifact`.
   - A constraint set that differs from `scripts/verify_ml_evidence.py:1812-1815` is published as
     it reads and named first in the PR (Q4).
6. **Tests.**
   - Every re-pin and rename in the card.
   - The `cc54d3c0` grounding plant, as a parametrization.
   - The two perturbed refit cases.
   - `test_model_evidence_provenance.py:98-116` stays unchanged: nothing is promoted to current.
7. **Documents.**
   - Re-derive `docs/ml-program.md:171-176`, naming `6536c68c...`.
   - Replace README:48-49 with section 2's sentence.
   - Record the two readings (the ceiling 2x2 census and the tie-break table) in Results and the
     surrogate report.
   - Merge `main` into the branch if card C has landed. Then recompute `docs/artifacts.md` rows
     :103-104, last.
8. **Gates.**
   - On the Mac, in a clean worktree: `pytest -m campaign` and `bash scripts/check.sh`, reported
     beside.
   - Open the PR. The CI project-checks and frontend-checks jobs gate.
   - Run `gh workflow run campaign-tier.yml --ref work/ml-reground-baseline-9`; quote the run id
     and the passed count.
   - Name any flip first, then wait for the owner's merge.

**Acceptance and planted proofs.** Keep every one in the card: the fence plants, the
verdict-identity drift classes, the one-literal constants plant, the one-character constraint edit,
the walk-fence tests, and the lambda=1.0 byte identity. Add:
- **The grounding plant.** Write `cc54d3c0...` back into a temp copy's `fit-corpus.json`, beside
  the new weights. Grounding must read FAIL.
- **The perturbed refit case, per instrument.** Factor the ULP comparison into one helper. Feed it
  a refit made on the live fit-side rows with one feature shifted by +0.125, and require an
  `AssertionError`.
- **Offline verifier.** FAIL 0. The identity and grounding rows name `6536c68c...` for both
  records, and the 12 recompute rows read OK.

**Constraints.**
- The spend is $0: no provider, no `.env`, no `--complete`, no recorder.
- The freeze holds for `engine/`, `agents/`, `meetings/`, `observation/`, `orchestrator/` and `eval/`.
- Never write a v2 kind into a committed stamp.
- No ES byte moves; one that does stops the card.
- Role-correctness gates nothing.
- Results names the host stamp beside every new digest. It makes no claim about which platform
  21.17 ran on, and it prices the deferred version-two cost.

**Verification.**
- The card's Validation block, with amendment 4 applied.
- The proof JSON, quoted by SHA.
- The Actions run ids.

### Card B: `tasks/work/committed-channel-rederivation.md` (new; six tests)

- **Base:** `main` after step 0.
- **Branch:** `work/committed-channel-rederivation`.
- **Delivery:** one PR, never squashed.

**Rulings relied on:** Q5: "Look into why the tests would still fail, if they are necessary at all, or a separate potential path forward. Go with the recommended idea from that."

**Scope.**
- Tests: `tests/_helpers/committed.py`, `tests/_helpers/test_committed_single_home.py`,
  `tests/meetings/test_contradictions.py`, `tests/meetings/test_transcript.py`,
  `tests/eval/test_evidence_honesty.py`, `tests/agents/test_reported_testimony.py`.
- Comment-only: `eval/evidence_honesty.py:2295-2297` and `meetings/schemas.py:406-408`. The diff
  must be docstring lines only.
- Nothing else.

| # | test | change class | record impact |
|---|---|---|---|
| 1 | T1 (above) | re-scope, re-anchored on the helper; rename; re-pin MEASURED. The investigator's figures: off 19/27, ungrounded 0/46, generous 2/44. Keep the scope-firewall assertion. | none |
| 2 | T2 | re-scope: the recorded named set {`ml_corpus/9p2i` seed 1041 meeting 1}; keep the plant at `test_contradictions.py:4191`; the docstring names the baseline-8 member (`samples` seed 41 meeting 2) and the I-3 distinction | none |
| 3 | T3 | re-anchor: delete the 0.80 floor, with a history line; per-render band order on the selector's kept list; planted re-band to 25 | none |
| 4 | T4 | retire the rows ordering, with a history line; rename; keep the pins 32,123 / 28,359 and the coverage inequality | none |
| 5 | T5 | re-anchor: pure exactness on the helper (145/145; recorded total = re-derived total, 107 including vent kinds); delete `_REPAIRED_SITES`, `_NAMED_UNCLASSIFIED_DIVERGENCES` and the addition allowlist | none |
| 6 | `tests/eval/test_evidence_honesty.py::test_the_instrument_and_the_detector_read_one_adjacency_rule` (`:3816`) | re-anchor plus test-bug fix: route outer ends via `maximal_stays`; `None` sentinel; the interior-boundary class census pinned MEASURED with the production reading; delete direction 1 and the duplicate off/on legs | none |

**The helper.**
- Promote the move, vent and sighting builders from `test_evidence_honesty.py`, plus the
  `_grounded_census` inputs, with a cache per set.
- The move builder drops the holder's own rows and carries `observation_id`.
- The roster is the living participants, and the trigger kind is passed as production passes it.
- Replace the `_REDERIVED_MEETINGS` off-leg comparison (`:2862`, `:3425`) with a
  both-leg-equals-recorded gate over 676 of 676 meetings.
- Re-derive, MEASURED, every census pin that the self-row fix moves.

**Retire** (craft rule 3; delete each after confirming it has no consumer left):
- `_MOVEMENT_CHANNEL_DIVERGING_MEETINGS` and its test (`test_contradictions.py:3446`, `:3550`);
- the 451 sensitivity test (`:3584`);
- `_planted_move_channel` (`:3354`);
- `sighting_records_from_recorded_flags` (`tests/_helpers/committed.py:147`);
- each `_rederive` consumer, dispositioned as in section 4.

**Correct every "not recoverable" comment:**
- `tests/_helpers/committed.py:161-165`;
- `test_contradictions.py:3243-3261`, `:3551-3557`, `:4703-4706`;
- `test_transcript.py:1698-1703`, `:1970-1976`;
- `test_evidence_honesty.py:2856-2868`.

**Planted proofs.**
- **The helper gate:**
  - dropping the movement channel makes 68 meetings diverge;
  - dropping the sighting channel makes 31 diverge;
  - keeping the holder's own move rows diverges at `ml_corpus/9p2i` seed 1035 meeting 3. The
    refuter reads 675/676; pin what is measured.
- **T5:** dropping movement diverges at the `samples/9p2i` members.
- **T3:** the re-band to 25.
- **The adjacency guard:**
  - pointing it back at the stay window turns it red;
  - a sequence with a 0 gap after a nonzero gap proves the sentinel.
- **T2:** the existing planted conviction.

**Constraints.**
- No recorded byte, prompt byte, detector output or served payload moves.
- No role assertion.
- Every moved pin is marked MEASURED, with its command.
- Each re-scope is labelled with Q5, with one history line per retired property.
- The walk adds roughly 9 s per worker file; mark it `slow` if the file convention requires.

**Verification.**
- The six files' tests, then mypy and ruff.
- `bash scripts/check.sh` whole, in a clean worktree. These six ids leave the red list and no new
  id appears.

### Card C: `tasks/work/report-fog-and-counterfactual-freeze.md` (new; three tests)

- **Base:** `main` after step 0.
- **Branch:** `work/report-fog-and-counterfactual-freeze`.
- **Delivery:** one PR with one commit per item, never squashed. The PR names the viewer change
  first: it is a publication decision on merge.

**Rulings relied on:** Q5 (above).

| # | test | change class | record impact |
|---|---|---|---|
| 7 | `tests/api/test_view_model.py::test_report_tick_fog_keeps_the_reported_body` (`:1237`) | code fix in `api/replay_loader.py`, plus test parametrization over `samples/4p1i` and a vacuity guard (at least one game-deciding report tick is exercised) | Served `visible_bodies` changes on the final frame of 3 non-featured games. The demo bundle is byte-identical, measured by a before/after diff. No recorded byte moves. |
| 8, 9 | `tests/scripts/test_counterfactual_phase21.py::test_the_memo_table_equals_a_live_four_set_run` (`:705`) and `::test_the_memo_marks_every_advisory_cell` (`:673`) | retire the memo-vs-live comparison, plus a doc change (dated E.4 provenance erratum) | One `audits/` byte change. The registry row at `docs/artifacts.md:109` is recomputed last. The file count stays 329. |

**Acceptance for item 1.**
- Planted: the unfixed loader fails on seed 13.
- A count-only reporter-fog census reads 1 -> 0 on `samples/9p2i`, `samples/4p1i` and
  `ml_corpus/4p1i`.
- Run `tests/api` and `tests/scripts/test_build_demo_bundle.py`.

**Acceptance for items 3 and 4.**
- Split the corroboration-pin loop into its own slow test. If none exists, add a plant: perturb
  one committed cell and require the test to fail.
- Delete the memo comparisons, the errata-fold tests, the five perturbation cases and the helpers
  that no longer have callers.
- Keep `test_the_memo_table_parses_into_rows` and the no-bar pins.
- Rewrite the module docstring. It argues from `3eebc7d5` and "no step re-issues the memo", says
  why `efcd43b8` does not apply, and says why `70e49468` was not taken.
- E.4 names the last commit where the gate passed (confirmed first by running both tests at
  `39a568c6`) and the command.

**Verification.** `bash scripts/check.sh` whole, in a clean worktree. These three ids leave the red
list and no new id appears.

### Order, dependencies and shared files

- **Order.** Step 0 comes first. Then A, B and C start in parallel, since their files are disjoint.
- **Merges.** B and C are small and should merge first.
- **The long card.** A's web-session leg starts once A's steps 1-4 are pushed. A merges last, after
  merging `main` into its branch. Its CI then reads zero failing ids.
- **If A is ready first.** It merges, and whichever PR merges last carries the whole-green proof
  for Q5.
- **`docs/artifacts.md`** has two writers: C writes row :109 and A writes rows :103-104. Whichever
  merges second merges `main` first and re-runs
  `test_every_counted_registry_row_matches_the_index`.
- **`tasks/README.md`:** only the orchestrator writes it.
- **`tests/eval/test_evidence_honesty.py`:** card B is its only writer.

### Substrate changes that would need a future re-record (listed, not scheduled)

- **S-1: one-tick fuzz at an interior, declared stay boundary.** The detector measures adjacency
  from the route's outer ends (`meetings/transcript.py:3357-3387`).
  - **The production instance** is 1 recorded STRONG flag, `ml_corpus/9p2i` seed 1041 meeting 1.
    The sighting is false at its own tick and true one tick later. That flag convicted.
  - **The records-free class** is about 25-26 of 29 flags.
  - **Candidate:** the labelling variant. When the sighted room is the speaker's own contiguous
    neighbouring stay within the tick gap, the flag takes the weak band.
  - **How it would ship:** default-OFF behind an experimental gate until an adopting record (craft
    rule 7), paired with the per-stay row-3 instrument (record audit section 7.1, third item).
  - **The conflict:** it collides with the direction memo's stop on adding levers (section 10), so
    it is OPEN 1.
- **S-2: the empty sighting-mapping fall-back** (`meetings/transcript.py:1836`,
  `meetings/manager.py:1345-1354`).
  - With an empty mapping, the detector silently keeps the pre-grounding rules.
  - It is latent: 0 of 676 meetings are affected, but the records-free re-derivers rely on it.
  - A fail-loud change moves no committed byte, but it is a detector-path change (OPEN 6).
- **S-3: a render budget for reported testimony.** This is not recommended: the band order holds.
  It is listed because record audit section 6.4 routed T3 as a render-budget question. It would be
  a prompt-byte change.

### Routed follow-ups that need no re-record

- **R-1:** a campaign-tier refit-equivalence pin for the filtered-BC anchor (about 5 s).
- **R-2:** a version-two fit-closure and per-artifact stamp-closure design before any current
  install or campaign (OPEN 2).
- **R-3:** record the Darwin-arm64 `test_es` pass in `training/bakeoff/es.py:52-58`,
  `tests/training/test_es.py:117-127` and `README.md:98` (OPEN 5).

## 7. OPEN for the owner (not settled by the 2026-09-23 answers)

1. **S-1.** Build the interior-boundary adjacency rule as a default-OFF lever for the next
   combined re-record, despite the direction's "Stop: adding levers"? Until then, may the tour or
   scorecard show 1041 meeting 1 as a caught lie?
2. **The version-two scope.** Before the first current install or campaign: which code closure
   version two binds, for the fits and for each stamp. That install inherits the verifier and test
   inversions and the closure churn. Not blocking.
3. **Contingency only.** If the web session does not reproduce the committed section 6 leg cells
   at `39a568c6` while the Mac does, the card stops for a ruling between the container rule and the
   reproduction rule.
4. **GitHub Actions `ubuntu-latest` as the gating Linux run** for the campaign tier and
   `check.sh`. It is flagged as a named deviation in A's PR, for ruling at review.
5. **The ES docs change.** Does the investigator's Darwin-arm64 pass of `test_es` count as the
   "owner-assisted" run `training/bakeoff/es.py:52-58` asks for, before R-3 records it?
6. **S-2.** Should the empty-mapping fall-back fail loud, or stay as the re-derivers' designed
   entry?

## 8. The re-check commands (this host, scratch only)

- **Fact rows 1-17:** `sed -n`, `git grep` and `git diff --name-only 39a568c6 95fb894b` at the
  cited lines.
- **Row 16:** `git ls-tree -r -l 39a568c6 -- replays/samples replays/ml_corpus`, summed over
  `replay-seed-*.jsonl`.
- **Row 18:** the scratch probe `synth/probe_kept.py`, run with
  `UV_PROJECT_ENVIRONMENT=<scratch venv> uv run --project <worktree> --frozen --no-sync python probe_kept.py <worktree>`.
  - It re-runs `_corridor_census`'s loop through the test module's own helpers.
  - It matches each adjacent kept-STRONG flag to `entry.contradictions` by
    (kind, `event_a_id`, `event_b_id`) and counts its recorded band.
  - Output: 29 adjacent kept flags, of which 1 recorded STRONG (seed 1041 meeting 1, stay gap 0),
    5 recorded weak and 23 not recorded. Recorded `alibi_vs_sighting`: 1 strong and 45 weak.
