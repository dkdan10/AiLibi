# Re-ground the ML fits on the baseline-9 corpus

**Status:** ready

## Outcome

The 2026-09-22 re-record replaced `replays/ml_corpus/9p2i` under fits it was forbidden to
touch, so every committed ML instrument describes games no longer in the tree: 68 ML tests
are red (41 in `bash scripts/check.sh`'s default tier, 27 in the campaign tier) and 12 rows
of `scripts/verify_ml_evidence.py` FAIL. This card re-grounds every fit the record
invalidated, on the same baseline-9 bytes, by the same committed recipes, at `$0` and with no
model call. It first reproduces each committed artifact from its recipe on the baseline-8
bytes it was fitted on, so "same recipe" is measured, not assumed; then the red tests and
FAIL rows turn green by measurement. It is the adopting record for the fits: the frozen side
of every measured/frozen pair (the digest a fit was made on, the committed verdict and report
figures, the artifact stamps) moves here and only here, and `BAKEOFF_BASELINE_ID` advances to
`baseline-9` here and nowhere else. The two readings the record left open, the surrogate
ranking above its documented "honest ceiling" and the FO-6 tie-break scoring better at the
higher tau, are settled by measurement on the re-ground fits, never by editing a docstring.
It is a re-fit, not a re-record, and it re-searches nothing.

## Evidence

Line numbers are at `87c6abfe` (head of `work/process-rerecord`); re-verify at dispatch.
The record merged to `main` as `acf6c604` on 2026-09-23, carrying the genuine-class
self-check card (#478, merged into the branch as `5eb547d8`); `bash scripts/check.sh` on
that `main` is red on exactly the tests this card lists, and on nothing else.

**Routing.** [The record](../../audits/audit-2026-09-22-process-rerecord.md) §7.1 names this
its first follow-up, the successor of Task 21.17; §7.3 quantifies it and §6.4 routes the
tie-break reversal with it. The owner opened it on 2026-09-23 ("Then open up the next
re-ground card after."). [The direction of 2026-09-19](../direction-2026-09-19-process-over-outcome.md)
sections 7, 9 and 12 place no ML work in or after the wave, and [the task index](../README.md)
keeps "Q1 search, Phase C co-evolution resumption and a corpus refit" distinct: this is the
refit.

**The 68 red tests** ([the re-record card](process-rerecord.md) "Left red", `:1387-1459`):

| group | default tier | campaign tier | why red |
|---|---|---|---|
| fit-corpus fence | 28 (15 surrogate, 13 conviction) | 16 surrogate (`test_composed_runner.py`) + 8 conviction (`test_crew_scorer.py` 3, `test_crew_owned_tasks.py` 2, `test_coevo_driver.py` 2, `test_anchor_study.py` 1) | loading a committed fit under `evidence_scope="historical"`, `training/provenance.py:176-203` reads the version-one corpus fingerprint `6536c68c…` against the recorded `cc54d3c0…` and raises "fit corpus or derivation drifted"; six campaign tests assert another refusal and meet this one first |
| frozen fit | 7 (`test_surrogate_runner.py` 4, `test_conviction_model.py` 2, `test_bakeoff_methods.py` 1) | 3 (composed `verdict.json`, anchor-study stamp, hall-of-fame pool stamp) | a committed artifact, verdict or stamp no longer equals its live computation: fit side 348 vs 355 meetings; confusion (49,3,2,37) vs (42,5,2,45); composed accuracy 0.9011 vs 0.8404; study `c845602d…` vs `894f4daf…`; pool `4a25ccdf…` vs `8b174cab…` |
| verifier controls | 6 (`tests/scripts/test_verify_ml_evidence.py`) | — | their OK controls run on the real corpus and read FAIL on the grounding, identity or recompute rows |

**The 12 FAIL rows**, reproduced offline at `87c6abfe` while writing this card (61 checks: OK
37, FAIL 12, ABSENT 7 evidence-branch rows, INFO 5): fit-corpus identity and ML grounding
(`6536c68c…` on disk, `cc54d3c0…` in both records); surrogate top-1 0.8846 (46/52) vs
committed 0.8246, SKIP-vs-eject 0.4894 vs 0.3956, `verdict.json` 15/31 fields; conviction
Spearman 0.8191 vs 0.6670, conversion accuracy 0.9255 vs 0.9451, `verdict.json` 11/21;
composed decision accuracy 0.8404 vs 0.9011, exact outcome 0.8298 vs 0.8352, convicting top-1
0.8846 vs 0.8246, `verdict.json` 9/17. Every drifted field is corpus-derived; weight hashes,
the composed manifest and the two adoption constraints read OK.

**Digests at `87c6abfe`.** Weights: surrogate `06b20508…`, conviction `7e764b89…`,
filtered-BC anchor `62595367…`. Verdict sidecars: surrogate `02197128…`, conviction
`03976eee…`, composed `a0640164…`. Corpus fingerprint: version one `6536c68c…`
(`training/provenance.py:57`), version two `070e46b0…` (`:139`). Anchor substrate: historical
`894f4daf…`, version two `f48fdd17…`, both still at `baseline-8` and `HIGH_FLAG_FLOOR =
147/151`, so both move with the constants. Pool substrate: historical `8b174cab…` (the corpus
MANIFEST's sha256), version two `e5016c1b…`. Nothing under `training/artifacts/` changed
after `1793eb23`, and nothing under `training/` or in `uv.lock` changed between `39a568c6`
and `87c6abfe`: the re-record's base runs this card's fit code.

**The two readings.** (1) `compute_honest_ceiling` (`training/surrogate/fidelity.py:545-583`)
calls its headline "the maximum top-1 any physical+belief surrogate could reach", yet the
frozen surrogate and a fresh re-fit both rank 46 of 52 held-out ejections first against a
ceiling of 41 (`top1_ceiling_gap` −0.0962). Axis 1 (`:1214-1217`) passes either way; the
claim, not the verdict, hangs on it. (2) On the `ml_corpus/9p2i` test side the shipped FO-6
head (highest tied tau) scores 0.4468 against the lowest tied tau's 0.4362 (record §6.4),
falsifying a "never better" docstring. `fo6_rebaseline` re-fits FO-6 fresh on the committed
table and the surrogate verdict reads only FO-6's ranking (`:1217`), which the tie-break
leaves identical: the reversal belongs to the bytes, and this card re-measures it but cannot
move it.

**What Task 21.17 did, cost and changed** ([contract](../phase-21.md) `:4445-4736`; PR #413,
merge `1793eb23`). It re-fit the surrogate (NO-GO: ranking GO, decision NO-GO), conviction
(GO) and composed (GO) by the §8 recipes; ran a fresh composed Goodhart leg (HELD; the
adoption constraints went three to two, a published-cell move the orchestrator ruled);
re-fit the filtered-BC anchor and re-stamped the study, the λ grid, genomes and λ=1.0 byte
identity untouched; gave the MAP-Elites pool its two-field re-stamp; moved
`BAKEOFF_BASELINE_ID` and `HIGH_FLAG_FLOOR` together with three coupled literals; deleted the
STALE amnesty; and ruled the coevo campaign-row pins against their own provenance instead of
re-stamping recorded rows. Cost `$0`, CPU-only. No step was timed alone; commit timestamps
(2026-08-31, EDT) bound them: pre-dispatch re-anchor 15:21:08; the surrogate, conviction and
composed re-fits and the Goodhart leg committed 15:47:09 (≤ 26 min); walk repair, anchor,
re-stamps and pool 16:10:46 (≤ 24 min, including a premise-falsity stop and ruling); campaign
tier 156.29 s (15 failed, 313 passed) before and 157.34 s (331 passed) after; merge 18:35:53
after three review rounds. No record names its environment, so the platform that produced the
committed GD weights cannot be established from the tree.

**The measured/frozen pair rule** (`3eebc7d5`: "re-stamped, and only the half that may
move"). A re-record re-derives the measured side of a pinned pair, the corpus on disk; the
frozen side, the corpus a fit was made on and every figure its artifacts commit, moves only at
the re-ground that re-fits it. 21.17 moved the frozen side and deleted the declared-gap
mechanism, so the 2026-09-22 record left these rows FAIL, not STALE (§7.3).

**Two identity versions since 21.17.** `a0285760` ([model-evidence card](model-evidence-provenance.md))
added a version-two identity binding the corpus, `roster.json`, the local import closure of
the derivation code, the map, `pyproject.toml`, `uv.lock` and the Python, numpy and pydantic
versions (`training/provenance.py:108-157`). `derivation_files()` measures that closure at 109
files across `agents/`, `api/`, `engine/`, `eval/`, `llm/`, `meetings/`, `observation/`,
`orchestrator/` and `training/`. Current consumers require version two; the committed records
are version one, and tests and verifier read them as historical
(`scripts/verify_ml_evidence.py:1726`, `:1744-1746`, `:2010-2014`;
`tests/training/test_model_evidence_provenance.py:98-116`).
[`training/README.md`](../../training/README.md)`:48-50` says a future fit "must write"
version two, the anchor and pool writers already stamp version-two kinds
(`training/anchor_study.py:1351`, `training/bakeoff/map_elites.py:881-885`), and the Goodhart
leg defaults to current scope (`training/composed_runner.py:1251`). Followed verbatim, the §8
recipes write a record labelled version one (`training/surrogate/runner.py:414`) carrying a
version-two digest, which every loader refuses. Q1 resolves this.

**Platform.** The GD fits (ballot predictor, conviction model, filtered-BC anchor) are
byte-identical only on their producing platform and ULP-equivalent elsewhere
(`training/conviction/model.py:18-21`, `training/anchor_study.py:51-58`); the round-trip pins
compare at `rel=1e-9`. ES portability is "designed for, not yet confirmed"
(`training/bakeoff/es.py:52-58`), and the standing project fact is that ES artifacts reproduce
only in the Linux container. One new data point: on a Darwin-arm64 host at `87c6abfe`,
`tests/training/test_es.py::test_evolve_is_deterministic_and_hash_pinned` passes; that is one
CI-budget pin, not a champion search, so the rule stands.

## Acceptance

- [ ] **Reproduce first, on the bytes each artifact was made on.** In a detached worktree at
  `39a568c6` (the last `main` before the re-record: baseline-8 corpus, this card's fit code):
  `historical_fit_corpus_fingerprint` reads `cc54d3c0…`;
  `verify_ml_evidence.py --only sidecars --only corpus --only recompute` exits 0; the
  surrogate, conviction and filtered-BC refits hash to `06b20508…`, `7e764b89…` and
  `62595367…` on a named platform, or else agree parameter by parameter within `rel=1e-9`
  with Results saying no platform tried reproduced the bytes; and the composed Goodhart leg,
  in the container, reproduces the report's §6.1 cells and both adoption constraints. A refit
  that fails is repeated at `1793eb23`, the commit that wrote the artifacts: a match there but
  not at `39a568c6` means the recipe changed after the fit, and stops the card. Mechanism: each
  comparison, quoted with its command. Perturbed proof: the same refit on the baseline-9 corpus
  (355 fit-side meetings, not 348) must not match.
- [ ] **Surrogate, then conviction, re-fit on baseline 9** by `report-ballot-surrogate.md` §8
  steps 2-5 and `report-conviction-model.md` §8 steps 2-6: walk re-validation first
  (`raw_mismatches` ≠ 0 stops the card); weights, sidecar, `max-uses.json`
  (`derive_max_uses(<fit-side count>)`), `fit-corpus.json` at the version Q1 rules and the
  verdict with its writer-emitted sidecar committed together; each verdict taken on the first
  held-out evaluation, whichever way it reads. Mechanism: the loaders' fence
  (`training/provenance.py:176-203`) loads both bundles clean with the corpus check on. Planted
  proof: `test_fit_corpus_fence_fails_loud_on_substrate_and_key_drift` and
  `test_conviction_corpus_fence_cannot_be_omitted` still refuse their planted records.
- [ ] **The composed verdict is re-derived last** (`run_composed_fidelity` →
  `decide_composed_go` → both writers), with a fresh Goodhart leg in the container at the scope
  Q1 rules. A constraint set that differs from `scripts/verify_ml_evidence.py:1812-1815` is a
  published-cell move, reported for a ruling as 21.17's D2 was; the pin moves only after it.
  Mechanism: the verifier's composed rows and `test_committed_composed_verdict_is_rederivable`.
  Proof: a one-character constraint edit in a temporary copy fails the full-string comparison.
- [ ] **Verdicts publish as they read; no bar moves.** `git diff` is empty on
  `training/surrogate/fidelity.py` and `training/conviction/fidelity.py`; a GO/NO-GO flip
  follows Q4 and is named first in the PR. Mechanism: the verdict writers and recompute rows.
  Proof: `_verdict_identity_row`'s planted corpus-derived and corpus-independent drift cases
  stay red.
- [ ] **Anchor study and pool: re-ground and re-stamped, not re-searched.** `walk_corpus` walks
  all 150 games (a `CorpusWalkError` stops the card, as it stopped 21.17); the filtered-BC
  anchor is re-fit under the moved floor; in the stamp shape Q1 rules, its weights, sidecar and
  `config.json`, each λ `config.json` stamp and `study.json`'s `filtered_bc`, `substrate_sha`
  and `baseline_id` are rewritten; the pool index takes `baseline_id` and
  `substrate.substrate_sha256`, its 30 genomes and `filled_cells` asserted unchanged in the
  same test. The λ genomes, their sidecars and the sweep rows stay byte-identical; the re-stamp
  procedure is quoted in Results and is idempotent. Mechanism:
  `test_committed_study_artifacts_are_the_baseline8_fit` (renamed), the inverted pool tripwire
  in `test_bakeoff_methods.py` and `test_committed_pool_restores_only_with_explicit_historical_identity`.
  Proof: `test_committed_lambda_1_artifact_reproduces_the_champion_byte_for_byte`, the
  walk-fence tests (`tests/training/test_anchor_study.py:236-380`) and
  `test_founder_ingestion_substrate_mismatch_refused` stay green and unchanged.
- [ ] **`BAKEOFF_BASELINE_ID` becomes `"baseline-9"`** at `training/bakeoff/harness.py:188`
  and nowhere else; the coupled literals (`training/bakeoff/goodhart.py:848`, `:1989`;
  `training/composed_runner.py:1247`) move with it; `HIGH_FLAG_FLOOR`
  (`training/anchor_study.py:172`) becomes 107/145, stated as 17 transcript + 90 persisted vent
  flags (`eval/watchability.py:1050-1054`), with `eval/watchability.py` untouched. Mechanism:
  `test_selection_bar_pins_the_baseline_8_floors` (`tests/training/test_bakeoff_harness.py:172-187`,
  renamed), asserting the probe default equals the constant. Proof: one literal left at
  `baseline-8` in a scratch edit turns it red.
- [ ] **The verifier reads FAIL 0 offline**, the grounding and identity rows naming the new
  record digests for both fitted instruments and the 12 rows OK. Mechanism:
  `scripts/verify_ml_evidence.py`. Planted proof: the existing undeclared-corpus,
  other-weights, relabelled-version, perturbed-replay and perturbed-weight-hash cases still
  fail their perturbed halves, and one stale-artifact case is added as a parametrization, not
  a near-copy: `cc54d3c0…` written back beside the new weights in a temporary copy FAILs
  grounding.
- [ ] **All 68 tests are green, and every other committed-fit reader is re-derived**,
  including the five the re-record re-derived against the frozen baseline-8 fits (the three
  composed-fidelity reads, `test_axis_three_is_a_floor_the_live_model_clears_on_all_three`,
  `test_no_go_verdict_holds_on_live_served_clamped_features`), whose "out-of-sample"
  docstrings become false and are restated. Results lists every changed expectation old → new
  in the re-record card's format, each marked MEASURED (a live computation, re-derived) or
  FROZEN (a committed figure this card moved) with its reason, lists renamed ids, and keeps
  the baseline-8 fits' baseline-9 readings as a finding (conviction GO at 87/94; surrogate
  46/52 against a 41/52 ceiling). No assertion is deleted or weakened. Mechanism: pytest, both
  tiers. Proof: the planted cases above.
- [ ] **Both readings are settled by measurement**: for the ceiling, a per-meeting 2×2 census
  over the re-ground fit's held-out ejections (surrogate top-1 hit × ceiling-reachable), each
  hit-but-unreachable meeting named with its mechanism; for the tie-break, record §6.4's
  four-set low/high-tau table re-run at this head. Both go into Results and the surrogate
  report with their commands; no docstring in `training/surrogate/fidelity.py` or
  `tests/training/test_surrogate_fidelity.py` is edited, and the rulings stay the owner's.
  Proof: the census cells sum to 52 and its hit column to the verdict's top-1; the tie-break
  table reproduces §6.4 to four decimals.
- [ ] **Derived documents are recomputed, never hand-written.** The four training reports
  refresh in the commits that move their artifacts, each §9 one-liner re-run, baseline-8
  figures kept as labelled history. `docs/ml-program.md` `:170-218` is re-derived from the
  verdicts, with no task or audit id and no threshold arithmetic, at least 15 words under its
  2,150 ceiling (`scripts/check_doc_facts.py:896-901`; 21.17's D6). `replays/ml_corpus/README.md:29-45`
  and `docs/artifacts.md` rows `:103` and `:104` are re-derived from disk;
  `training/README.md:40-53` states the ruled version in one sentence;
  `docs/process-scorecard.md` is untouched. Mechanism: `scripts/check_doc_facts.py` and the
  verifier's availability and inventory rows. Proof: `tests/scripts/test_check_doc_facts.py`'s
  ML-page perturbations stay red.
- [ ] **The campaign tier is green in the container**: `uv run pytest -m campaign` reads 335
  passed (its count at `39a568c6`), any other count explained id by id. Mechanism: pytest,
  also run weekly by `.github/workflows/campaign-tier.yml`. Proof: at the re-record's close it
  read 308 passed, 25 failed, 2 errors.
- [ ] **`bash scripts/check.sh` has no ML red**, run whole in a clean worktree in the
  container: its failing ids are none, or a subset of the re-record's nine non-ML Left-red
  ids, each owned elsewhere. Proof: at the re-record's close it failed on 50 ids, 41 of them
  ML.

## Constraints

**Environment, per fit.** Reproduction proves the environment: each step runs where its
reproduction reproduced the committed output, and Results names the platform beside every new
digest.

| step | container? | why |
|---|---|---|
| surrogate, conviction and filtered-BC refits | no | numpy full-batch GD: byte-identical on the producing platform, ULP-equivalent elsewhere; run where reproduction byte-matched, else in the container, and name the platform in each report header |
| composed fidelity, verdicts, `walk_corpus`, stamps, constants | no | inference on frozen weights, the deterministic engine, sha256 over committed bytes |
| the composed Goodhart leg | **yes** | an ES champion search, where one ULP gives another champion; the constraints and §6 cells come from it |
| `pytest -m campaign`, the final `check.sh` | **yes** | they carry the ES pins and CI-budget ES runs; macOS results are reported beside, not gating |

The container is Linux x86-64, Python 3.11, `uv sync --frozen`: a Claude Code web session
like the earlier ML tasks', or the image `docker-compose.yml` pins, `docker run --rm
--platform linux/amd64 -v "$PWD":/app -w /app -e UV_PROJECT_ENVIRONMENT=/tmp/ailibi-venv
ghcr.io/astral-sh/uv:python3.11-bookworm-slim uv run --locked <command>`, whose fidelity
under emulation on arm64 is exactly what reproduction tests. Its only network use installs
the locked wheels.

**Spend and inputs.** `$0`: no provider, model call, recorder or held-out generator (band
2100-2999 stays unseen); no `--complete`, which needs the evidence fetch and adds only
evidence-branch rows unrelated to the fits. A bare shell with no `AILIBI_*` export and no
`.env`; rollouts use the fake provider (`training/provenance.py:29-36`).

**No recorded byte moves.** Under `replays/` only `replays/ml_corpus/README.md` changes; the
corpus MANIFESTs keep their stale FROZEN line (record §7.2), since an edit re-fingerprints the
corpus (`3eebc7d5`). Nothing is re-scored. Recorded campaign rows
(`training/reports/results-*.jsonl`), the coevo tree, the `utility-es`, `policy-es` and
`bc-dagger` genomes, `training/artifacts/crew/` and the runner-up stamp naming the anchor are
never re-stamped (21.17's rulings); the λ grid and the campaign are not re-searched.

**The freeze.** Nothing changes under `engine/`, `agents/` (the prompt set included),
`meetings/`, `observation/` or `orchestrator/`: the fits read them, and nothing here changes
them. `eval/` is read-only too.

**Role-correctness gates nothing.** The fits are fidelity to the record, not correctness: a
fit that predicts the recording's wrong ejection is right. No bar, ceiling or comparator is
retuned; a bar that cannot be evaluated on these bytes stops the card.

**Wall budget and stop rule.** 21.17 timed no fit alone, so each budget is twice its
commit-timestamp bound:

| step | bound | budget |
|---|---|---|
| reproduction at `39a568c6` (the two rows below, smaller corpus) | ≤ 50 min | 60 min |
| surrogate, conviction, composed fidelity, Goodhart leg | ≤ 26 min | 55 min |
| walk, anchor, study and pool | ≤ 24 min | 50 min |
| campaign tier | 157 s | 10 min |

Total compute stays inside 4 h. Stop and report with the partial output on: a step past its
budget (never a silent retry); a reproduction that matches on no platform, by bytes or by ULP,
or an ES-bearing output no environment reproduces; `raw_mismatches` ≠ 0 or a
`CorpusWalkError`; a pin that moves for any reason but the re-fit (a λ genome, a coevo row, a
corpus byte); and a verdict flip (Q4).

**Prerequisites and ownership.** [The re-record](process-rerecord.md) has merged. One writer
per file: the coordinator serializes `docs/artifacts.md` and `tasks/README.md` with the
concurrent follow-ups, and this card writes only `docs/artifacts.md` rows `:103` and `:104`.
Under Q1 (a) the genuine-class card (record §7.1, second item) merges first, because
`eval/vote_correctness.py` is in the derivation closure.

**Questions for the owner.**
- **Q1 (blocks the first write): which identity version?** (b) *Historical, version one*,
  recommended: records keyed to `6536c68c…` as today's are; study and pool stamped by the
  historical definitions in their committed shape (no kind field); one sentence scoping
  `training/README.md:48` to fits a current consumer will install. It survives code edits,
  the verifier and tests work unchanged, and no current consumer may install it, which no
  authorized work needs. (a) *Current, version two*, as `:48` literally reads: records carry
  `fit_corpus_fingerprint` at the fit commit, stamps the version-two definitions; the
  verifier's two version-one rows learn version two, and `test_current_loader_refuses_historical_fit`
  inverts onto a planted version-one copy. Its cost: any later edit to one of the 109 closure
  files re-stales every fit and reddens the ML tests until the next re-ground.
- **Q2: the campaign tier.** Recommended in scope as tests, since all 27 turn green as
  consequences, nothing re-searched, re-run or re-stamped; deferring it leaves the weekly run
  on `main` red.
- **Q3: which container is available?** Without one the card stops before the Goodhart leg.
- **Q4: a verdict flip.** Recommended: publish as it reads, name it first in the PR, wait for
  the owner's merge, re-point nothing downstream; the alternative is to stop before committing
  it.
- **Q5: "done" with the nine non-ML reds standing?** `AGENTS.md` forbids "done" while
  `check.sh` is red; the re-record was marked done on the coordinator's instruction with every
  red named. May this card be too?

## Expected scope

Artifacts: `training/artifacts/{surrogate,conviction,composed}/` (every file);
`training/artifacts/anchor_study/` (`filtered-bc-anchor/`, the stamp in each
`lambda-*/config.json`, `study.json`); two fields of
`training/artifacts/impostor/map-elites/cells/index.json`. Code:
`training/bakeoff/harness.py:188`, `training/anchor_study.py:162-172`, the three coupled
literals; `scripts/verify_ml_evidence.py` only for a ruled constraint pin or under Q1 (a).
Tests, re-pins, renames and the one planted case only: the files in the Evidence table,
`tests/eval/test_balance_eval_meeting_runner.py`,
`tests/experiments/test_torch_probe_excluded.py` and
`tests/training/{test_goodhart_probe,test_bakeoff_harness,test_model_evidence_provenance}.py`.
Documents: the four `training/reports/report-{ballot-surrogate,conviction-model,composed-runner,anchor-study}.md`,
`docs/ml-program.md`, two `docs/artifacts.md` rows, the `replays/ml_corpus/README.md`
blockquote, one `training/README.md` sentence, `tasks/README.md`'s inventory sentence and this
card. Not in scope: recorded bytes, the frozen directories, `eval/`, the recipes
(`training/surrogate/`, `training/conviction/`, `training/rewards.py`),
`scripts/record_ml_corpus.sh`, `frontend/`, `api/`, `audits/`, `docs/process-scorecard.md`.

Delivered on `work/ml-reground-baseline-9` by one pull request into `main` (merge or
fast-forward, never squash), each commit carrying `Card: tasks/work/ml-reground-baseline-9.md`.
Order: reproduction; surrogate, conviction, composed; the constants with the anchor, study and
pool stamps in one commit; tests, reports, documents; the campaign tier and `check.sh` last.

## Record impact

The adopting record for the ML fits; no recorded replay byte, rendered prompt byte or detector
output moves, and gameplay is unchanged. The fit bundles, the anchor weights and the study,
λ-config and pool stamps move, and so do `BAKEOFF_BASELINE_ID` and `HIGH_FLAG_FLOOR`, so
bake-off selection reads baseline 9's five supply gauges; the documents in scope recompute.
Moving the frozen side is legitimate here and only here: it is the half of the pair a
re-record may not move (`3eebc7d5`), and these fits were made on these bytes. Earlier verdicts
stay as labelled history in the reports' errata; baseline 8's fits stay reachable at
`39a568c6`. The demo rebuild on merge (`.github/workflows/pages.yml`) reads none of these
files. The next corpus recording re-stales the fits as this one did; under Q1 (a), so does any
edit to the 109-file closure.

## Validation

```
# reproduction: detached worktree at 39a568c6, uv sync --frozen there
uv run python -c "from pathlib import Path; from training.provenance import historical_fit_corpus_fingerprint as f; print(f(Path('replays/ml_corpus/9p2i')))"
uv run python scripts/verify_ml_evidence.py --only sidecars --only corpus --only recompute
uv run python -c "import hashlib; from pathlib import Path; from training.surrogate import build_meeting_table; from training.surrogate.ballots import fit_corpus_ballot_predictor; p=fit_corpus_ballot_predictor(build_meeting_table(Path('replays/ml_corpus/9p2i'))); print(hashlib.sha256(p.to_artifact_json().encode()).hexdigest())"
uv run python -c "import hashlib; from pathlib import Path; from training.conviction.model import fit_corpus_conviction_model; m,_,_=fit_corpus_conviction_model(Path('replays/ml_corpus/9p2i')); print(hashlib.sha256(m.to_artifact_json().encode()).hexdigest())"
uv run python -c "from pathlib import Path; from training.anchor_study import run_anchor_study; run_anchor_study(lambda_grid=(), artifact_root=Path('$SCRATCH/anchor'), verify_committed_champion=False)" && cat "$SCRATCH/anchor/filtered-bc-anchor/weights.json.sha256"
# container: the Goodhart leg (report-composed-runner.md §9, at the scope Q1 rules)
uv run python -c "from training.bakeoff.es import ESConfig; from training.composed_runner import run_composed_goodhart_leg; c=ESConfig(generations=6, population=6, sigma=0.5, seed=0, fitness_seeds=tuple(range(8)), init_scale=0.5); print(run_composed_goodhart_leg(config=c, evidence_scope='historical').to_json())"
# at the head
uv run python scripts/verify_ml_evidence.py                  # offline; FAIL 0
uv run pytest tests/training tests/scripts/test_verify_ml_evidence.py tests/eval/test_balance_eval_meeting_runner.py tests/experiments/test_torch_probe_excluded.py -q
uv run pytest -m campaign -q                                 # container
uv run python scripts/check_doc_facts.py && uv run python scripts/validate_task_docs.py
bash scripts/check.sh                                        # whole, clean worktree, container
git log --oneline 87c6abfe..HEAD -- engine agents meetings observation orchestrator  # empty
git diff --stat 87c6abfe..HEAD -- replays eval docs/process-scorecard.md  # corpus README only
```

The anchor re-fit at the head reuses the fit-only `run_anchor_study` call into a scratch root
(it re-searches nothing); Results quotes it, the re-stamp after it, and the census and
tie-break commands whole.

## Results

Not started.
