# Keying the baseline-9 re-ground fits (owner Q1)

Investigation memo, 2026-09-23. Tree: `main` at `95fb894b` (all file:line citations are at
that commit unless a commit is named). Read-only: no tracked file was left modified, nothing
under `training/artifacts/` was written, no provider call, no recorder, no `--complete`.
Probes ran on scratch copies; two planted edits were applied to tracked files and restored
from byte copies (worktree `git status` clean after each).

**Label note.** The task labels the choices (a) version one, (b) version two. The card
(`tasks/work/ml-reground-baseline-9.md`, Constraints, Q1) uses the opposite letters: its
"(b) Historical, version one" is this memo's **(a)**, its "(a) Current, version two" is this
memo's **(b)**.

## Bottom line

Recommend **(a): key the re-ground's records to the version-one corpus identity**
(`historical_fit_corpus_fingerprint`, `6536c68c...` at this head). Certify the derivation
by **measurement** instead of a source-byte hash. The default tier already has that
measurement: the refit-equivalence pins compare a live refit with the committed weights.
Version two stays the identity a *current* consumer must mint. That happens at the commit
that installs the fit, as a separately authorized current fit. It is not a certificate held
continuously on `main`.

The measurements behind this:

1. Version two binds 109 files. That is the syntactic import closure of five roots. Only
   40 of them execute any function during the two fits. `eval/vote_correctness.py` is bound
   but never executes.
2. From the 21.17 fit commit (`1793eb23`) to the last baseline-8 `main` (`39a568c6`), the
   version-two derivation identity moved. Measured with the current definition, the
   closure grew from 86 to 108 files: 81 changed and 22 were added. Yet the refit at
   `39a568c6` on Darwin arm64 is **byte-identical** to all three committed GD weights
   (`06b20508...`, `7e764b89...`, `62595367...`).
3. Since version two landed, 15 of the 37 pull-request merges on `main` touched its bound
   set. Each would have reddened the fit fences in `check.sh` (and CI) under version-two
   records, although the fit itself never changed.
4. A planted +0.125 feature change leaves both version-one identity tests green, and the
   refit pin fails on it. The semantic fence catches the change that matters, and the
   byte fence catches every change.

## 1. What each version binds

**Version one**: `training/provenance.py:57-67`. It is a sha256 chain over every
`replay-seed-*.jsonl`, then `splits.json` and `MANIFEST.md`, each as `name\0sha256\n`.
It covers no roster, no code and no runtime.

**Version two**: `training/provenance.py:139-157`. The payload is `("format",
"fit-inputs-v2")`, then the sha256 of every replay plus `roster.json`, `splits.json` and
`MANIFEST.md`, then `("derivation", derivation_fingerprint())`. `derivation_fingerprint`
(`:108-136`) hashes three things:
- every file of `derivation_files()`;
- `engine/maps/canonical_1.yaml`, `pyproject.toml` and `uv.lock`;
- the Python major.minor version and the installed numpy and pydantic versions.

There is no platform or architecture row, so the digest is portable across hosts that
share the lock.

**How the bound set is chosen** (`training/provenance.py:70-105`). An AST walk starts from
five roots (`:20-26`):
- `training/surrogate/dataset.py`
- `training/surrogate/ballots.py`
- `training/conviction/dataset.py`
- `training/conviction/model.py`
- `agents/tactical/features.py`

The walk follows these rules:
- It follows **every** `Import` and `ImportFrom` node anywhere in a file, including those
  inside function bodies (`ast.walk`).
- It adds every package-prefix `__init__.py`.
- It tries each from-imported name as a submodule.
- It resolves only under the repo root. So `from _verify_samples import verify_samples`,
  which `eval/validity.py:142-146` imports through `sys.path`, is imported by the fit path
  but not bound. It is not executed either.

At `95fb894b` the set is **109 files**:

| directory | files |
|---|---|
| `agents/` | 20 |
| `api/` | 4 |
| `engine/` | 11 |
| `eval/` | 15 |
| `llm/` | 9 |
| `meetings/` | 12 |
| `observation/` | 9 |
| `orchestrator/` | 15 |
| `training/` | 14 |

The full list comes from `derivation_files()`.

**Why so wide.** The edges were recovered by re-running the same walk with parent tracking:
- `training/surrogate/dataset.py:125-131` imports `eval.funnel._walk_game_vj` and four
  helpers of `eval.validity`. `eval/validity.py:97-112` pulls `api.replay_loader`,
  `eval.balance_eval`, `eval.meeting_quality` and more. `eval/meeting_quality.py:191-218`
  pulls `eval.vote_correctness`, `deduction_metrics`, `cost_dashboard`,
  `alibi_fabrication`, `accusation_calibration` and `_suspicion_parse`.
- `dataset.py:155` imports `orchestrator.game.apply_meeting_result`. That pulls the whole
  game runtime: the `llm/` clients (three of them through function-level imports in
  `llm/provider.py`), `agents/strategic/prompts/loader.py`, the scheduler, recording and
  run limits.
- `training/__init__.py` pulls `env`, `rewards` and `rollout`.
- `training/conviction/__init__.py` pulls `conviction/fidelity.py`.
- `conviction/model.py:78` pulls `surrogate/runner.py`.

Restricting the walk to top-level imports gives 106 files. **Question 1 answer:** the set
is the honest *import* closure of the fit code, but relative to what influences a fit it is
a broad sweep.

**Runtime trace** (a scratch script, `sys.setprofile`, measuring which repo files have any
function called). The run covered `measure_belief_render_parity`, `build_meeting_table`,
`fit_corpus_ballot_predictor` and `fit_corpus_conviction_model` on `ml_corpus/9p2i` and
took 44 s. **Only 40 of the 109 files execute.** The 69 that never execute include:
- `eval/vote_correctness.py` and every other `eval/` report module except `balance_eval`,
  `funnel`, `replay_walk`, `report_schema` and `validity`;
- all of `llm/`;
- `agents/strategic/prompts/loader.py`;
- `orchestrator/recording.py`;
- `agents/tactical/features.py`. This is a root, but it is the live serving encoder,
  unused by the corpus fit.

`assemble_tournament_report` (`eval/validity.py:357-379`) folds recorded outcomes only.
`eval/vote_correctness.py` is imported for its module definitions and never called.

**The stamps are mis-scoped under version two.**
- `compute_substrate_sha` (`training/anchor_study.py:242-259`) and `bakeoff_substrate_sha`
  (`training/bakeoff/map_elites.py:722-731`) fold `fit_corpus_fingerprint`. They therefore
  bind the *surrogate and conviction* closure.
- The anchor's own recipe and the ES code are **outside** those 109 files. Running the same
  walk from `training/anchor_study.py` adds 15 files. Among them are
  `training/anchor_study.py` itself and `training/bakeoff/{es,utility_es,map_elites,harness,policy_es,bc,goodhart}.py`.
- The MAP-Elites pool and the lambda grid are substrate-independent. They are
  fake-provider rollouts that never read the corpus (`tests/training/test_bakeoff_methods.py:1118-1124`).
- So a version-two stamp on them binds code their genomes never ran, and it misses the
  code they did run.

## 2. What happens today on an edit to a bound file

**Planted probe at `95fb894b`.** Two records were written into **scratch copies** of the
committed surrogate and conviction bundles:
- a version-one record with corpus identity `6536c68c...`;
- a version-two record with `fingerprint_version: 2` and `070e46b0...`.

Before any edit, all six loads succeed (v1 historical, v2 historical, v2 current). Then one
comment line was appended to `eval/vote_correctness.py` (restored afterwards):

| record | scope | after the one-line edit |
|---|---|---|
| version one | historical | still LOADS |
| version two | historical | REFUSED: "fit corpus or derivation drifted" |
| version two | current | REFUSED: "fit corpus or derivation drifted" |

Historical scope does not shield a version-two record: `verify_fit_identity` computes the
version-two digest whenever the record says version two (`training/provenance.py:195-199`).

**Which tests would go red under committed version-two records.** This is inferred from the
shared code path, not measured on committed v2 records: writing `training/artifacts/` is
outside this investigation.

- The same refusal at `training/provenance.py:200-203` is what reddens today's corpus-drift
  group: 28 default-tier and 24 campaign-tier fence tests (card, Evidence table).
- The verifier's identity row and ML grounding row would fail once they learn version two,
  and so would the 6 verifier controls that run them on the real tree.
- With v2-kind stamps, the anchor and pool stamp pins would fail too:
  `tests/training/test_anchor_study.py:743-790`,
  `tests/training/test_bakeoff_methods.py:1112-1144`, and the committed-pool ingest.
- CI runs `bash scripts/check.sh` on every pull request and push
  (`.github/workflows/ci.yml:3-5`, `:54`).

**Measured churn.** Since v2 landed (first-parent, `--since=2026-09-06`, diff against the
first parent):
- **15 of 37** PR merges touched the version-two bound set, including prompt-loader,
  featherless-client and process-scorecard merges.
- **10 of 37** touched even the 40 files that execute during the fits. Those are the
  gameplay core: `meetings/manager.py`, `orchestrator/game.py`, `agents/memory/beliefs.py`
  and others.

The 40 files are the gameplay core because a reconstruction-based dataset is walked
through the live engine and memory fold.

**Measured non-effect.** The current `derivation_fingerprint` was computed over exported
trees:

| commit | closure | derivation digest |
|---|---|---|
| `1793eb23` | 86 files | `c35e0a8b...` |
| `a0285760` | 102 files | `f6ef91ac...` |
| `39a568c6` | 108 files | `39e96d9c...` |
| `95fb894b` | 109 files | `6c606191...` (matches the in-tree value) |

At `39a568c6` on macOS-15.7.3 arm64, `uv run pytest` of the two refit pins plus the fence
and provenance files reads **20 passed**. The in-memory refits hash to exactly `06b20508...`
(surrogate) and `7e764b89...` (conviction). `run_anchor_study(lambda_grid=(), ...)` into
scratch gives filtered-BC `62595367...` in 5.4 s. A version-two key would have declared
these fits stale on about 15 merges, and on none of them did the fit change.

**Is there a re-stamp path that recomputes identity without a re-fit?**
- None in the tree. No production function writes `fit-corpus.json`: the section 8 recipes
  construct `SurrogateFitCorpus` by hand (`training/reports/report-ballot-surrogate.md:497-501`,
  `report-conviction-model.md:284-291`).
- `training/README.md:53-54` forbids relabelling old provenance.
- 21.17's pool and study re-stamps were manual procedures quoted in its PR.

A re-certification is conceivable: refit, assert equality with the committed weights, then
rewrite the digest. It would be honest as a measurement, but not acceptable as a routine
path:
- It is new mechanism.
- It makes unrelated pull requests write `training/artifacts/`, against the one-writer
  rule.
- It duplicates what the refit pins already measure on every gate run.
- It recreates the pressure to declare a gap per pull request. 21.17 deleted STALE to end
  that pressure (section 3).

## 3. STALE: what it was, why 21.17 deleted it

- **Origin.** STALE was installed by the baseline-7 record as an interim holding
  (`audits/audit-phase-20-baseline-7.md:750-754`).
- **Mechanism.** It was a fifth verifier status. The ML grounding row compared one literal
  declared pair, `_DECLARED_GROUNDING_GAP` = (fit sha, corpus sha). When the mismatch was
  exactly that pair, the grounding row and the corpus-dependent recompute rows were
  downgraded from FAIL to STALE, and the command still exited 0.
- **Re-stamp at 21.15.** `3eebc7d5` re-stamped only the corpus half of that pair ("THE
  DECLARED GROUNDING GAP re-stamped, and only the half that may move", commit body line
  482). That moved the verifier from 13 FAIL to 1 FAIL with 12 STALE.

Task 21.17 deleted the whole mechanism (`tasks/phase-21.md:4583`) for these reasons:
- The gap was closed by the re-fit.
- B-20: the row-scoped amnesty also hid corpus-independent drift in the same verdict
  object.
- B-46: "the one thing that must survive deletion is the assertion that a fingerprint
  MISMATCH fails" (`:4448`).
- The contract warned: "Resist the pull to reintroduce a downgrade path" (`:4648-4650`).

What survives is the per-field classification, `CORPUS_DERIVED_VERDICT_FIELDS`
(`scripts/verify_ml_evidence.py:1904`), and a mismatch still fails.

A version-two key would put `main` into exactly the declared-gap state after most product
merges.

## 4. Options, with their costs

| option | next code or substrate change (no re-record) | next re-record | verifier and tests needed now |
|---|---|---|---|
| **(a) v1 keyed to `6536c68c...`** | No bookkeeping. The refit pins (`tests/training/test_surrogate_runner.py:809`, `tests/training/test_conviction_model.py:803`) and the verifier's recompute and verdict-identity rows go red **only if** the change moves the fit or its verdicts, which is the honest trigger for a re-ground. | The v1 digest moves, and the whole fence group plus the 12 rows go red until the next re-ground. This is the measured/frozen pair rule, unchanged. | No verifier logic change. The rows keep "historical v1; does not certify current derivation" (`scripts/verify_ml_evidence.py:1770`). One parametrized planted case. `training/README.md:48` scoped by one sentence. The section 8 recipes corrected to name `historical_fit_corpus_fingerprint`. |
| **(b) v2 as designed** | Every edit to the 109 + 3 files, a lock bump, or a numpy, pydantic or Python bump reddens the fence group, the verifier rows and (if v2-stamped) 3 stamp pins in `check.sh` and CI. That was about 15 of 37 merges in 17 days. The re-ground PR itself races any closure-touching merge. | Same as (a). | The identity row (`:1716-1781`) and grounding row (`:1966-2061`) must switch to `fit_corpus_fingerprint` and choose a source root. Temp-root tests would have to link the 109 + 3 sources, or a foreign `repo_root` would silently verify the local source. `test_historical_verifier_refuses_relabeled_fit_version` (`tests/scripts/test_verify_ml_evidence.py:636`) inverts. `test_current_loader_refuses_historical_fit` (`tests/training/test_model_evidence_provenance.py:98-104`) inverts onto a planted v1 copy. Pins at `tests/training/test_surrogate_runner.py:553`, `:599` and `tests/training/test_composed_runner.py:966` switch functions. The pool ingest test (`tests/training/test_hall_of_fame.py:519-548`) inverts. The anchor pin's `evaluation_evidence_scope is None` (`tests/training/test_anchor_study.py:764`) changes. |
| **(c) v2 narrowed to what influences the fit** | Narrowing by import graph gives nothing: the graph *is* the 109 (106 counting top-level imports only). The only mechanical narrowing is a runtime trace (40 files). It is data-dependent, misses constant-only modules, and would drop the serving-encoder root. It still hit 10 of 37 merges, all of which left the fit byte-identical. | Same as (a). | A new identity definition (a version three) in `training/provenance.py`. All of (b)'s verifier and test work, plus the trace harness and its planted case. |
| **(d1) dual digest** (v1 plus v2 in one record) | Tests read the v1 half and stay green. The v2 half goes stale after about one merge, so it is decorative (ornamental-constant rule). | Same as (a). | A schema field on `SurrogateFitCorpus` (`training/surrogate/runner.py:397-427`), a scope split in `verify_fit_identity`, and the verifier. It is outside the card's recipe freeze. |
| **(d2) v2 plus a re-certify script** | Every closure-touching PR runs a refit and commits new digests under `training/artifacts/`. | Same as (a). | New mechanism and file-ownership conflicts. It duplicates the refit pins. |

## 5. Recommendation: (a), exactly

**Why.** Version two was built for **current installation**. The model-evidence card's
probe was a current loader accepting a planted +0.125 feature change
(`tasks/work/model-evidence-provenance.md`, Results). Current loaders keep refusing
version-one records (`training/provenance.py:191-194`), so that door stays shut.

For the committed-evidence tier, the derivation is better certified by the refit itself:
- Planted probe at `39a568c6`: the +0.125 change in `training/surrogate/dataset.py`. Result:
  `test_committed_artifact_round_trips_and_the_refit_no_longer_matches` FAILED at
  `tests/training/test_surrogate_runner.py:867`, while both version-one fence tests passed.
- Roster: v1 does not bind `roster.json`. A roster-only perturbation of a scratch corpus
  copy (tasks per crewmate 2 to 3) leaves v1 unchanged and moves v2. `build_meeting_table`
  then refuses with `MeetingTableReconstructionError` at tick 0, because the state hash
  diverges. So the walk covers the roster by measurement.
- The documents already treat a *current* fit as a separate, later act.
  `training/README.md:42-43` says "Current use fails until a newly adopted corpus supports
  a separately authorized fit". `docs/ml-program.md:210-216` says a new independent-evidence
  feature profile precedes such a refit. This card re-fits the historical instrument by the
  unchanged recipe.

**Writer calls.** Use corpus `C = Path("replays/ml_corpus/9p2i")`, fit side 355 meetings
for both instruments (`tests/training/test_conviction_model.py:799`), and `max_uses`
`derive_max_uses(355) == derive_conviction_max_uses(355) == 50765`.

1. **Surrogate.**
   1. `measure_belief_render_parity(C)`. `raw_mismatches` must be 0.
   2. `t = build_meeting_table(C)`, then `p = fit_corpus_ballot_predictor(t)`.
   3. `d = write_ballot_predictor_artifact(p, Path("training/artifacts/surrogate"), max_uses=derive_max_uses(355))`.
   4. `rec = SurrogateFitCorpus(corpus_set="9p2i", corpus_sha256=historical_fit_corpus_fingerprint(C), fit_side_meetings=355, weights_sha256=d)`.
      Write `(dir / FIT_CORPUS_FILENAME).write_text(rec.model_dump_json(indent=2) + "\n")`.
      Pass no `fingerprint_version`. It defaults to 1 and is excluded from the JSON
      (`training/surrogate/runner.py:414-416`). This serialization byte-matches both
      committed records today.
   5. `write_surrogate_verdict_artifact(decide_go_no_go(run_surrogate_fidelity(...), fo6_rebaseline(t), weights_sha256=d), dir)`.
2. **Conviction.**
   1. `m, table, parity = fit_corpus_conviction_model(C)`.
   2. `d = write_conviction_model_artifact(m, dir, max_uses=derive_conviction_max_uses(355))`.
   3. Write the same record shape keyed to `d`.
   4. `write_conviction_verdict_artifact(decide_conviction_go(run_conviction_fidelity(table, model=m), weights_sha256=d), dir)`.
3. **Composed.**
   1. `run_composed_fidelity(C)` loads by sha only.
   2. `decide_composed_go(...)`.
   3. `write_composed_manifest_artifact` and `write_composed_verdict_artifact`.
   4. Goodhart leg in the container: `run_composed_goodhart_leg(config=..., evidence_scope="historical")`.
      The default is `"current"` (`training/composed_runner.py:1251`), which refuses v1
      components.
4. **Constants first, then stamps.** Move `BAKEOFF_BASELINE_ID = "baseline-9"` and
   `HIGH_FLAG_FLOOR = 107/145`. Then:
   1. `run_anchor_study(lambda_grid=(), artifact_root=<scratch>, verify_committed_champion=False)`.
   2. Copy `filtered-bc-anchor/weights.json` and its `.sha256` into the tree.
   3. Its `config.json` is the scratch config **without** `substrate_sha_kind`, with
      `substrate_sha = historical_compute_substrate_sha()`. Explicit parameters at this
      head give `b1fca5d43b2461a5110c0690a413ac96691e0eedaf910918d68793fc0d073413`;
      recompute it after the constants move.
   4. Each `lambda-*/config.json` changes only its `substrate_sha`.
   5. `study.json` takes `baseline_id "baseline-9"`, the same `substrate_sha`, and the new
      `filtered_bc`. Its `artifact_path` must be reset to
      `training/artifacts/anchor_study/filtered-bc-anchor`, because the scratch run writes
      its own path. `study.json` gets no `substrate_sha_kind` or
      `evaluation_evidence_scope` key.
   6. Pool `cells/index.json`: two fields, `baseline_id "baseline-9"` and
      `substrate.substrate_sha256 = historical_bakeoff_substrate_sha()` (`8b174cab...`, the
      MANIFEST sha), with no kind key.
5. **Documents.** Correct both section 8 recipes, which currently say
   `fit_corpus_fingerprint`. Followed verbatim they write a v1-labelled record carrying a v2
   digest, which fails loudly at every loader and in the identity row. Then:
   - Replace `training/README.md:48` with one sentence: a fit a current consumer installs
     writes version two at the commit that installs it, while an evidence re-ground writes
     version one and is derivation-checked by the refit pins.
   - Re-derive `docs/ml-program.md:171-176`, naming `6536c68c...`.

**Verifier expectations** (no logic change):
- The identity row reads OK with measured and committed both at `6536c68c...`, keyed to the
  new surrogate digest.
- The ML grounding row reads OK, naming conviction and surrogate both at `6536c68c...`.
- The 12 recompute rows read OK.
- New planted parametrization, not a near-copy: write `cc54d3c0...` back into a temp copy's
  `fit-corpus.json` beside the new weights. Grounding must read FAIL with "the fit was made
  on cc54d3c0".
- `test_historical_verifier_refuses_relabeled_fit_version` stays as is.

**Test pins:**
- `test_surrogate_runner.py:516-553` (rename baseline8 to baseline9): 355, 50_765,
  `record.corpus_sha256 == historical_fit_corpus_fingerprint(_CORPUS)`.
- Both refit pins stay at `rel=1e-9`, re-pinned to 355.
- `test_model_evidence_provenance.py:98-116` stays **unchanged**. It is the proof that
  nothing was promoted to current.
- The anchor pin, renamed: `substrate_sha == historical_compute_substrate_sha()`,
  `baseline_id == BAKEOFF_BASELINE_ID == "baseline-9"`, and
  `evaluation_evidence_scope is None`.
- The pool pin: `baseline_id "baseline-9"`, substrate equal to
  `historical_bakeoff_substrate_sha()`, 30 cells, champion `(5,0,3)` at 18.8641 unchanged.
- The hall-of-fame historical ingest keeps its logic.

## 6. ES-derived artifacts

- **Key and certificate.** The lambda genomes, the pool's 30 cells and the utility-es,
  policy-es and bc-dagger genomes are keyed by their own weights sidecars. They are
  certified by deterministic reproduction:
  - the ES hash pin in `tests/training/test_es.py`;
  - the lambda=1.0 byte-identity test (`tests/training/test_anchor_study.py:737`);
  - the pool champion pin.

  No substrate stamp certifies them.
- **Stamps.** A stamp only declares the baseline an artifact is filed under. In (a) it is
  written by the historical definitions, in the committed shape with no kind field.
  - Never give a committed ES artifact a v2 kind. v2 is a *campaign-run* identity: a
    current campaign recomputes it at start (`training/coevo/driver.py:1184-1211`), and it
    binds code these genomes never ran.
- **What must stay byte-identical.** The lambda genomes, their sidecars and sweep rows, the
  30 cell genomes, `filled_cells`, the coevo rows and every recorded campaign row. Only the
  declared stamp fields move. Any ES byte that moves stops the card; it is never re-stamped.
- **The composed Goodhart leg** is an ES champion search.
  - It runs in the container at `evidence_scope="historical"`.
  - Its adoption constraints are compared in full against
    `scripts/verify_ml_evidence.py:1812-1815`.
  - A different champion on another platform is a reproduction failure, not a keying
    question.
- **Platform data point.** All three GD fits reproduce byte-for-byte on Darwin arm64 at
  `39a568c6`. ES portability remains unconfirmed.

## 7. Limitations and routed items

- **Filtered-BC gap.** The filtered-BC anchor has no refit-equivalence pin. Its derivation
  is covered only by its stamp and sidecar, the same as after 21.17. A campaign-tier pin
  would take about 5 s; route it as a follow-up, since it is outside the card's test scope.
- **v2 stamp definitions are mis-scoped.** They bind the wrong closure for the anchor and
  pool. Before any current campaign relies on them, the owner should rule per-artifact
  closures.
- **What was not measured.**
  - v2-committed test counts (inferred).
  - The producing platform of the committed weights.
  - Linux reproduction.
  - The stamp after the constants actually move. `b1fca5d4...` was computed with
    parameters passed explicitly.
  - The trace is file-level on this corpus only.

## Commands (scratch scripts under the session scratchpad `keying-inv/`)

- The closure list: `derivation_files()`. Edges: a replica walk with parent tracking.
  Runtime: a `sys.setprofile` trace around the four fit calls.
- Churn: `git log --first-parent --since=2026-09-06` plus `git diff --name-only <c>^1 <c>`,
  intersected with the set.
- Cross-commit derivation: `git archive` exports of the four commits, then
  `derivation_fingerprint(root)`.
- At `39a568c6`:
  - `uv run pytest -q tests/training/test_surrogate_runner.py::test_committed_artifact_round_trips_and_the_refit_no_longer_matches tests/training/test_conviction_model.py::test_committed_artifact_round_trips_and_the_refit_no_longer_matches tests/training/test_surrogate_runner.py::test_fit_corpus_fence_fails_loud_on_substrate_and_key_drift tests/training/test_model_evidence_provenance.py`
    reads 20 passed.
  - The in-memory refits hash to the committed digests.
  - The planted +0.125 case: 1 failed, 2 passed.
