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

Amended 2026-09-23 after the owner answered the card's five questions (quoted under
Constraints): the fits stay keyed to the version-one corpus identity
(`historical_fit_corpus_fingerprint`) with historical stamps, their derivation certified by
the refit-equivalence pins (each now backed by a committed perturbed case) and the verifier's
recompute rows; the GD refits, fidelity, stamps and constants run on this Mac (the refits
move to the web session only if this Mac misses the committed bytes), the composed Goodhart
leg is gated in a Claude Code web session on Linux, and GitHub Actions gates the
campaign tier and `check.sh`; a verdict flip publishes and waits for the owner's merge; and
the card is done when its failing ids are a subset of the nine that two sibling cards own.

## Evidence

Line numbers are at `95fb894b`, the `main` this amendment was written on; re-verify at
dispatch. Nothing under `training/` or `tests/training/`, and nothing in
`scripts/verify_ml_evidence.py`, changed from `87c6abfe`, where the card was first written.
The record merged to `main` as `acf6c604` on 2026-09-23, carrying the genuine-class
self-check card (#478, merged into the branch as `5eb547d8`). The orchestrator's 2026-09-23
investigation (keying, environment and decision memos, not in the tree) measured the same 50
failing default-tier ids at `95fb894b` on this Mac and on Linux CI (run 35841706125): the 41
ML ids this card lists and the nine under Constraints, **Done**. Re-measure at dispatch.

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

**The 12 FAIL rows**, reproduced offline at `87c6abfe` while writing this card and again at
`95fb894b` by the investigation (61 checks: OK 37, FAIL 12, ABSENT 7 evidence-branch rows,
INFO 5): fit-corpus identity and ML grounding (`6536c68c…` on disk, `cc54d3c0…` in both
records); surrogate top-1 0.8846 (46/52) vs committed 0.8246, SKIP-vs-eject 0.4894 vs 0.3956,
`verdict.json` 15/31 fields; conviction Spearman 0.8191 vs 0.6670, conversion accuracy 0.9255
vs 0.9451, `verdict.json` 11/21; composed decision accuracy 0.8404 vs 0.9011, exact outcome
0.8298 vs 0.8352, convicting top-1 0.8846 vs 0.8246, `verdict.json` 9/17. Every drifted field
is corpus-derived; weight hashes, the composed manifest and the two adoption constraints read OK.

**Digests at `95fb894b`.** Weights: surrogate `06b20508…`, conviction `7e764b89…`,
filtered-BC anchor `62595367…`. Verdict sidecars: surrogate `02197128…`, conviction
`03976eee…`, composed `a0640164…`. Corpus fingerprint: version one `6536c68c…`
(`training/provenance.py:57`), version two `070e46b0…` (`:139`). Anchor substrate: historical
`894f4daf…`, version two `f48fdd17…`, both still at `baseline-8` and `HIGH_FLAG_FLOOR =
147/151`, so both move with the constants. Pool substrate: historical `8b174cab…` (the corpus
MANIFEST's sha256), version two `e5016c1b…`; the committed `index.json` hashes `e43335ba…`.
Nothing under `training/artifacts/` changed after `1793eb23`, and nothing under `training/`,
in `uv.lock` or in `pyproject.toml` between `39a568c6` and `95fb894b`. Outside `tests/` the
Python that did change there (`git diff --name-only 39a568c6 95fb894b -- '*.py'`) is
`api/public_results.py`, `api/replay_loader.py`, `api/routes/eval.py`,
`eval/deduction_metrics.py`, `eval/report_io.py`, `eval/vote_correctness.py`,
`eval/watchability.py`, five `scripts/` files and one `audits/workflows/` file. The leg reads
`eval/watchability.py`, which adds the `baseline-9` floor block (`:1039`) and makes it the
default (`:1129`).

**The leg's floors follow the baseline id.** The probe scores through
`compute_watchability(directory, baseline_id=...)` (`training/bakeoff/goodhart.py:454-456`);
`run_composed_goodhart_leg` defaults `baseline_id` to the literal `"baseline-8"`
(`training/composed_runner.py:1247`) and `evidence_scope` to `"current"` (`:1251`), which
refuses version-one components. So the constants move before the baseline-9 leg runs. Three
defaults carry the literal: `run_goodhart_probe` (`training/bakeoff/goodhart.py:848`),
`run_conviction_path_probe` (`:1989`), through which the leg scores, and
`run_composed_goodhart_leg`. The baseline-id pin (`tests/training/test_bakeoff_harness.py:185-187`)
reads only the first, so a stale leg default passes it today.

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

**What Task 21.17 did** ([contract](../phase-21.md) `:4445-4736`; PR #413, merge
`1793eb23`). It re-fit the surrogate (NO-GO: ranking GO, decision NO-GO), conviction (GO) and
composed (GO) by the §8 recipes; ran a fresh Goodhart leg (HELD; the adoption constraints went
three to two, a published-cell move the orchestrator ruled); re-fit the filtered-BC anchor and
re-stamped the study and two pool fields, λ grid and genomes untouched; moved the constants;
deleted the STALE amnesty (`tasks/phase-21.md:4448`, `:4583`, `:4644-4650`: the re-fit closed
the gap, a row-scoped amnesty hid corpus-independent drift, a fingerprint mismatch must fail);
and ruled the coevo campaign-row pins against their own provenance. Cost `$0`, CPU-only;
commit timestamps bound its fits and leg at ≤ 26 min and its walk, anchor and re-stamps at
≤ 24 min; its campaign tier ran 157.34 s (331 passed). No record names its environment, and
this card makes no claim about it.

**The measured/frozen pair rule** (`3eebc7d5`: "re-stamped, and only the half that may
move"). A re-record re-derives the measured side of a pinned pair, the corpus on disk; the
frozen side, the corpus a fit was made on and every figure its artifacts commit, moves only at
the re-ground that re-fits it. 21.17 moved the frozen side and deleted the declared-gap
mechanism, so the 2026-09-22 record left these rows FAIL, not STALE (§7.3).

**Two identity versions since 21.17.** `a0285760` ([model-evidence card](model-evidence-provenance.md))
added a version two binding the corpus, `roster.json`, the import closure of the derivation
code, the map, `pyproject.toml`, `uv.lock` and the Python, numpy and pydantic versions
(`training/provenance.py:108-157`); `derivation_files()` measures that closure at 109 files.
Current consumers require version two; the committed records are version one, read as
historical (`scripts/verify_ml_evidence.py:1726`, `:1744-1746`, `:2010-2014`;
`tests/training/test_model_evidence_provenance.py:98-116`). [`training/README.md`](../../training/README.md)`:48-49`
says a future fit "must write" version two, while `:42-43` has current use wait for "a
separately authorized fit" and `docs/ml-program.md:210-216` requires a new independent-evidence
profile before a newly adopted corpus supports a refit. The anchor and pool writers stamp
version-two kinds (`training/anchor_study.py:1351`, `training/bakeoff/map_elites.py:881-885`),
and both §8 recipes name `fit_corpus_fingerprint`
(`training/reports/report-ballot-surrogate.md:499-500`, `report-conviction-model.md:285-286`):
followed verbatim they write a record labelled version one (`training/surrogate/runner.py:414-416`)
carrying a version-two digest, which every loader refuses. Q1 ruled this (Constraints).

**Keying measurements** (the investigation, on this Mac; re-measure at dispatch). A
`sys.setprofile` trace of the two fits executed 40 of the 109 bound files
(`eval/vote_correctness.py` is bound and never runs). By today's definition the closure grew
from 86 files at `1793eb23` to 108 at `39a568c6`, yet the refits at `39a568c6` are
byte-identical to all three committed GD weights. It counted 15 of 37 pull-request merges
since 2026-09-06 touching the bound set; `git log --first-parent --merges --since=2026-09-06
95fb894b` lists 39, so the implementer quotes its own count with its command. A planted +0.125
shift of `belief_suspicion` in `training/surrogate/dataset.py` failed the surrogate refit pin
while both version-one fence tests passed. The only committed +0.125 plant
(`test_model_evidence_provenance.py:54-79`) moves `fit_corpus_fingerprint` alone, so no
committed case proves the refit pins (`tests/training/test_surrogate_runner.py:809-880`,
`tests/training/test_conviction_model.py:803-855`) bite.

**Platform.** The GD fits are byte-identical on their producing platform and ULP-equivalent
elsewhere (`training/conviction/model.py:18-22`, `training/anchor_study.py:51-58`); the
round-trip pins compare at `rel=1e-9, abs=1e-12`. At `39a568c6` on this Mac (Darwin 24.6.0
arm64, Apple T6000, CPython 3.11.15, numpy 2.2.6 on Accelerate) the investigation reproduced
the three weights byte for byte (3.6 s, 11.5 s, 4.5 s), the verifier subset (exit 0), the pool
re-stamp (`e43335ba…`), the campaign tier (335 passed) and the Goodhart leg cell for cell
(45.4 s; two runs wrote byte-identical JSON `bddf96d5…`, `es_digest` `00d2c414…`); on the
baseline-9 corpus the same refits hash `f8901620…`, `3a6fe4ca…` and `d6b3f3a7…` (the last at
the unmoved floor). No committed file records the leg's digest: its committed record is the
cells. The leg stays platform-exposed, calling `math.tanh` (`agents/tactical/features.py:873`,
imported at `training/bakeoff/goodhart.py:90`) and `np.exp` (`training/surrogate/ballots.py:652`,
`training/conviction/model.py:344`) inside its rollouts. ES portability is "designed for, not
yet confirmed" (`training/bakeoff/es.py:52-58`); `test_es` passing here is not ES evidence.

**Linux references.** GitHub Actions `ubuntu-latest`: CI 35685443068 at `39a568c6` (8249
passed), CI 35841706125 at `95fb894b`, campaign tier 35601542266 at `0a1100ea` (335 passed,
400.0 s) (`.github/workflows/ci.yml:18`, `:54`; `.github/workflows/campaign-tier.yml:28`,
`:37`, `:59`, `:64`). Web sessions hand work back on `claude/*` branches (282 on `origin`); no
`work/*-proof` branch has a precedent.

**Stamp shapes.** Every committed stamp file byte-matches `json.dumps(<parsed>, indent=2,
sort_keys=True) + "\n"`, the writers' form (`training/bakeoff/harness.py:1645`,
`training/bakeoff/map_elites.py:887-889`), and both `fit-corpus.json` byte-match
`model_dump_json(indent=2) + "\n"`, so the Validation re-stamps re-serialize as the writers do.

## Acceptance

- [ ] **Reproduce first, on the bytes each artifact was made on.** In a detached worktree at
  `39a568c6` (the last `main` before the re-record: baseline-8 corpus, this card's fit code),
  on this Mac with the host stamp: `historical_fit_corpus_fingerprint` reads `cc54d3c0…`;
  `verify_ml_evidence.py --only sidecars --only corpus --only recompute` exits 0; the
  surrogate, conviction and filtered-BC refits hash byte for byte to `06b20508…`, `7e764b89…`
  and `62595367…`; the pool re-stamp reproduces `e43335ba…`; the Mac leg is reported beside,
  not gating; and the composed Goodhart leg, in the container (the web session's R1, **Remote
  leg**), reproduces the report's §6.1 and §6.2 cells and both adoption constraints. The refit
  gate is a byte match: agreement within the round-trip pins' ULP tolerance does not pass it.
  A refit that misses its bytes is repeated at `1793eb23`, the commit that wrote the
  artifacts: a match there but not at `39a568c6` means the recipe changed after the fit, and
  stops the card. A refit that misses its bytes on this Mac at both commits moves, with the
  other two, to the web session (R0, **Remote leg**), which must byte-match all three at
  `39a568c6`; the baseline-9 refits then run there as well, and a miss there stops the card
  for the owner. Mechanism: each comparison, quoted with its command. Perturbed proof: the
  same refits on the baseline-9 corpus (355 fit-side meetings, not 348) must not match.
- [ ] **Surrogate, then conviction, re-fit on baseline 9 at version one** by
  `report-ballot-surrogate.md` §8 steps 2-5 and `report-conviction-model.md` §8 steps 2-6:
  walk re-validation first (`raw_mismatches` ≠ 0 stops the card); weights, sidecar,
  `max-uses.json` (`derive_max_uses(355) == derive_conviction_max_uses(355) == 50765`), the
  verdict with its writer-emitted sidecar, and `fit-corpus.json` as
  `SurrogateFitCorpus(corpus_set="9p2i", corpus_sha256=historical_fit_corpus_fingerprint(C),
  fit_side_meetings=355, weights_sha256=<new digest>)` with no `fingerprint_version` argument
  (it defaults to 1 and is excluded from the JSON, `training/surrogate/runner.py:414-416`),
  committed together; each verdict taken on the first held-out evaluation, whichever way it
  reads; both §8 recipes corrected to name `historical_fit_corpus_fingerprint`. The
  investigation's baseline-9 digests (`f8901620…`, `3a6fe4ca…`) are a same-host expectation,
  not a pin: a dispatch-time mismatch is reported in Results beside the host stamp. Mechanism: the
  loaders' fence (`training/provenance.py:176-203`) loads both bundles clean at historical
  scope, and `test_current_loader_refuses_historical_fit` still refuses them at current scope.
  Planted proof: `test_fit_corpus_fence_fails_loud_on_substrate_and_key_drift` and
  `test_conviction_corpus_fence_cannot_be_omitted` still refuse their planted records.
- [ ] **Each refit pin has a committed perturbed case.** The ULP comparison in both
  `test_committed_artifact_round_trips_and_the_refit_no_longer_matches` pins is factored into
  one helper under `tests/training/`; each instrument gains a case feeding it a refit made on
  the live fit-side rows with one feature shifted by +0.125 (`belief_suspicion` for the
  surrogate; one conviction feature, named in the test), which must raise `AssertionError`.
  Mechanism: the helper, which both pins call. Proof: the perturbed case fails the helper while
  the unperturbed refit, through the same helper, passes.
- [ ] **`BAKEOFF_BASELINE_ID` becomes `"baseline-9"`** at `training/bakeoff/harness.py:188`
  and nowhere else, in one commit with the anchor, study and pool stamps, before the baseline-9
  leg runs; the three coupled `baseline_id` defaults move with it (`run_goodhart_probe`,
  `training/bakeoff/goodhart.py:848`; `run_conviction_path_probe`, `:1989`;
  `run_composed_goodhart_leg`, `training/composed_runner.py:1247`); `HIGH_FLAG_FLOOR`
  (`training/anchor_study.py:172`, its comment `:162-171`) becomes 107/145, stated as 17
  transcript + 90 persisted vent flags (`eval/watchability.py:1050-1052`), with
  `eval/watchability.py` untouched. Mechanism: `test_selection_bar_pins_the_baseline_8_floors`
  (`tests/training/test_bakeoff_harness.py:172-187`), renamed to what it then asserts (for
  example `test_selection_bar_and_the_three_probe_defaults_pin_one_baseline`) and extended:
  it asserts `BAKEOFF_BASELINE_ID == "baseline-9"`, `HIGH_FLAG_FLOOR == 107 / 145`, and, by
  `inspect.signature`, that the `baseline_id` default of each of `run_goodhart_probe`,
  `run_conviction_path_probe` and `run_composed_goodhart_leg` equals `BAKEOFF_BASELINE_ID`.
  Planted proof: a scratch edit of each of the three literals in turn, back to `"baseline-8"`
  with the other two at `"baseline-9"`, turns the test red each time; Results quotes the three
  runs.
- [ ] **Anchor study and pool: re-ground and re-stamped in the historical shape, not
  re-searched.** `walk_corpus` walks all 150 games (a `CorpusWalkError` stops the card, as it
  stopped 21.17); the filtered-BC anchor is re-fit under the moved floor into a scratch root
  and its weights and `.sha256` copied in; its `config.json` loses `substrate_sha_kind` and any
  `evaluation_evidence_scope` and takes `historical_compute_substrate_sha()` by the quoted
  idempotent command (Validation); each λ `config.json` changes only `substrate_sha`;
  `study.json` takes `baseline_id "baseline-9"`, the same sha and the new `filtered_bc` (its
  `artifact_path` reset to `training/artifacts/anchor_study/filtered-bc-anchor`), with no kind
  or scope key; the pool index takes `baseline_id` and `substrate.substrate_sha256 =
  historical_bakeoff_substrate_sha()`, no kind key. The λ genomes, their sidecars, the sweep
  rows, the 30 pool genomes and `filled_cells` stay byte-identical. Mechanism:
  `test_committed_study_artifacts_are_the_baseline8_fit` (renamed; asserting the historical sha,
  `baseline_id == BAKEOFF_BASELINE_ID == "baseline-9"` and no kind or scope key),
  `test_the_committed_map_elites_pool_is_historical_and_structurally_untouched` (champion
  `(5, 0, 3)` at 18.8641) and `test_committed_pool_restores_only_with_explicit_historical_identity`.
  Proof: the writer's own scratch `config.json`, which carries the version-two kind
  (`training/anchor_study.py:1351`), fails the renamed pin's predicate;
  `test_committed_lambda_1_artifact_reproduces_the_champion_byte_for_byte`, the walk-fence
  tests (`tests/training/test_anchor_study.py:236-380`) and
  `test_founder_ingestion_substrate_mismatch_refused` stay green and unchanged.
- [ ] **The composed verdict is re-derived last** (`run_composed_fidelity` →
  `decide_composed_go` with the agreed leg's adoption constraints → both writers), from the
  fresh leg in the container: the web session's R2 at historical scope after the constants
  commit, its JSON reading `baseline_id` `baseline-9`, taken by the decision rule under
  **Remote leg**. A constraint set that differs from `scripts/verify_ml_evidence.py:1812-1815`
  publishes as it reads: the pin moves in this pull request, named first in it, and the owner's
  merge rules it (Q4). Mechanism: the verifier's composed rows and
  `test_committed_composed_verdict_is_rederivable`. Proof: a one-character constraint edit in a
  temporary copy fails the full-string comparison.
- [ ] **Verdicts publish as they read; no bar moves.** `git diff` is empty on
  `training/surrogate/fidelity.py` and `training/conviction/fidelity.py`; a GO/NO-GO flip
  publishes as it reads, is named first in the PR and waits for the owner's merge, with nothing
  downstream re-pointed (Q4). Mechanism: the verdict writers and recompute rows. Proof:
  `_verdict_identity_row`'s planted corpus-derived and corpus-independent drift cases stay red.
- [ ] **The verifier reads FAIL 0 offline**, with no verifier logic change: the identity and
  grounding rows name `6536c68c…` for both fitted records, keyed to the new digests, and the 12
  rows read OK. Mechanism: `scripts/verify_ml_evidence.py`. Planted proof: the existing
  undeclared-corpus, other-weights, relabelled-version, perturbed-replay and perturbed-weight-hash
  cases still fail their perturbed halves, and the grounding plant is a new parametrization of
  `test_an_undeclared_corpus_still_fails_the_grounding_row`
  (`tests/scripts/test_verify_ml_evidence.py:596`), not a near-copy: `cc54d3c0…` written back
  into a temporary copy's `fit-corpus.json` beside the new weights reads FAIL on grounding.
- [ ] **All 68 tests are green, and every other committed-fit reader is re-derived**,
  including the five the re-record re-derived against the frozen baseline-8 fits (the three
  composed-fidelity reads, `test_axis_three_is_a_floor_the_live_model_clears_on_all_three`,
  `test_no_go_verdict_holds_on_live_served_clamped_features`), whose "out-of-sample"
  docstrings become false and are restated. Results lists every changed expectation old → new
  in the re-record card's format, each marked MEASURED (a live computation, re-derived) or
  FROZEN (a committed figure this card moved) with its reason, lists renamed ids, and keeps
  the baseline-8 fits' baseline-9 readings as a finding (conviction GO at 87/94; surrogate
  46/52 against a 41/52 ceiling). No assertion is deleted or weakened, and
  `tests/training/test_model_evidence_provenance.py:98-116` is unchanged: nothing is promoted
  to current. Mechanism: pytest, both tiers. Proof: the planted cases above.
- [ ] **Both readings are settled by measurement**: for the ceiling, a per-meeting 2×2 census
  over the re-ground fit's held-out ejections (surrogate top-1 hit × ceiling-reachable), each
  hit-but-unreachable meeting named with its mechanism; for the tie-break, record §6.4's
  four-set low/high-tau table re-run at this head. Both go into Results and the surrogate
  report with their commands; no docstring in `training/surrogate/fidelity.py` or
  `tests/training/test_surrogate_fidelity.py` is edited, and the rulings stay the owner's.
  Mechanism: the two commands, quoted whole. Proof: the census cells sum to 52 and its hit
  column to the verdict's top-1; the tie-break table reproduces §6.4 to four decimals; and a
  known-answer control runs first: the same census at `95fb894b` on the frozen baseline-8
  surrogate reads 46 of 52 hits against a ceiling of 41 (Evidence), or the census command is
  wrong.
- [ ] **The keying rule is written down, scoped to what enforces it.** `training/README.md:48-49`
  ("A future fit must write …") is replaced by this sentence, the rest of the paragraph kept:
  "Re-grounds of the historical raw flag-count instrument (the ballot surrogate and the
  conviction model; ruled 2026-09-23) keep version-one records: their derivation is checked by
  measurement, not a source digest, by
  `test_surrogate_runner.py::test_committed_artifact_round_trips_and_the_refit_no_longer_matches`,
  `test_conviction_model.py::test_committed_artifact_round_trips_and_the_refit_no_longer_matches`
  and `test_verify_ml_evidence.py::test_recompute_reads_every_committed_verdict_against_the_live_corpus`;
  the filtered-BC anchor has no refit pin. A fit a current consumer installs writes
  `SurrogateFitCorpus(fingerprint_version=2, ...)` with `fit_corpus_fingerprint(corpus_dir)` at
  the commit that installs it." The two `historical_*` docstrings (`training/anchor_study.py:222-226`,
  `training/bakeoff/map_elites.py:712-716`), which today say those definitions only restore old
  artifacts, say instead, comment-only, that they also stamp re-grounds of the historical
  instrument and still cannot authorize a current campaign. Both refit pins are named
  `test_committed_artifact_round_trips_and_the_refit_no_longer_matches`, though they assert a
  ULP match (`tests/training/test_surrogate_runner.py:809-826`); a commit that renames either
  pin names the new id in this `training/README.md` sentence in the same commit.
  Mechanism: the three tests the sentence names. Proof: the perturbed refit cases and the
  grounding plant above fail on exactly the drift the sentence says those tests catch.
- [ ] **Derived documents are recomputed, never hand-written.** The four training reports
  refresh in the commits that move their artifacts, each §9 one-liner re-run, baseline-8
  figures kept as labelled history, each new digest beside its host stamp. `docs/ml-program.md`
  `:170-204` is re-derived from the verdicts, naming `6536c68c…`, at least 15 words under its
  2,150 ceiling (`scripts/check_doc_facts.py:896-901`; 21.17's D6); its claim at `:175-176`
  that every row re-derived under `--complete`, a mode this card never runs, is restated to
  name the offline verifier; the policy paragraphs at `:205-218` (the loader rule, and at
  `:210-216` the independent-evidence profile the keying ruling cites) stay word for word.
  `replays/ml_corpus/README.md:29-45` is re-derived from disk. New prose in these documents and
  the reports carries no task or audit id, no threshold arithmetic and no unexplained jargon:
  a term it needs (the corpus identity's version, the historical scope, the derivation
  closure) is phrased plainly or defined in `docs/glossary.md`, whose added lines are in
  Expected scope. After merging `main` (card C writes row `:109`), `docs/artifacts.md` rows
  `:103` and `:104` are recomputed last; `docs/process-scorecard.md` is untouched. Mechanism:
  `scripts/check_doc_facts.py`, the verifier's availability and inventory rows and
  `test_every_counted_registry_row_matches_the_index`; for jargon, the reviewer's read plus the
  front-door budget check, because no committed gate scans `docs/ml-program.md` or the reports
  for dialect terms (`check_dialect_terms` reads `README.md` only). Proof:
  `tests/scripts/test_check_doc_facts.py`'s ML-page perturbations stay red.
- [ ] **The campaign tier is green on Linux**: `gh workflow run campaign-tier.yml --ref
  work/ml-reground-baseline-9` on GitHub Actions `ubuntu-latest` reads 335 passed (its count at
  `39a568c6`), any other count explained id by id (a perturbed refit case this card marks
  `campaign` is such a difference), with its run id quoted and the Mac run beside. Mechanism: pytest in `.github/workflows/campaign-tier.yml` (`:28`, `:59`, `:64`).
  Proof: at the re-record's close it read 308 passed, 25 failed, 2 errors.
- [ ] **`bash scripts/check.sh` has no ML red** in the pull request's CI `project-checks` and
  `frontend-checks` jobs: its failing ids are none, or a subset of the nine under Constraints,
  **Done**. A whole run in a clean worktree on this Mac is reported beside, its frontend leg run
  on its own while pytest is red (`set -e` stops the script there). Mechanism:
  `.github/workflows/ci.yml:54` and the frontend job. Proof: at the re-record's close it failed
  on 50 ids, 41 of them ML.

## Constraints

**Keying (Q1), ruled 2026-09-23: version one (`historical_fit_corpus_fingerprint`).** Both
fitted records carry the version-one corpus identity; every stamp uses the historical
definitions in its committed shape, with no kind field; version two stays the identity a
current install mints at the commit that installs it. Why: version two binds 109 files of which
40 run in the fits; the fits reproduced byte for byte across the closure's growth from
`1793eb23` to `39a568c6`; a version-two key would redden `check.sh` on roughly 40% of merges
without the fit moving, the churn craft rule 7's default-OFF gates exist to avoid; and
`docs/ml-program.md:210-216` makes this a re-fit of the historical raw flag-count instrument,
while a fit a current consumer could install needs the new independent-evidence profile first.
`training/README.md:48`'s plain reading is overridden by this dated ruling; Results does not
claim the documents already agreed. Never write a version-two kind into a committed stamp.

**Environment, per step.** Each step runs where its reproduction reproduced the committed
output, and Results names the host stamp beside every new digest.

| step | runs on | gate or proof |
|---|---|---|
| reproduction at `39a568c6`: fingerprint, verifier subset, three GD refits, pool re-stamp | this Mac | byte match to the committed digests, with the host stamp; a refit that misses at both `39a568c6` and `1793eb23` moves the three refits to R0; the Mac leg reported beside, not gating |
| surrogate, conviction and filtered-BC refits on baseline 9 | this Mac if its reproduction byte-matched; otherwise the web session (R0) | the host's reproduction byte-matched; the PR's CI round-trip pins re-check Linux ULP-equivalence |
| composed fidelity, verdict writers, `walk_corpus`, stamps, constants | this Mac | frozen-weight inference, the deterministic engine, sha256 over committed bytes |
| tests, reports and documents, while developing | this Mac | targeted pytest, `check_doc_facts.py`, `validate_task_docs.py`; the gating runs are the Linux rows |
| **the composed Goodhart leg** | **a Claude Code web session on Linux x86-64 (Q3); required and gating** | R1 at `39a568c6` reproduces §6.1, §6.2 and both constraints; R2 at the branch head after the constants commit is the leg whose cells and constraints this card commits |
| `pytest -m campaign` | GitHub Actions `ubuntu-latest`, by `workflow_dispatch`; gating | 335 passed, or each difference explained id by id; the Mac run beside |
| `bash scripts/check.sh` | the PR's CI `project-checks` and `frontend-checks` jobs; gating | failing ids none, or a subset of the nine under **Done**; the Mac clean-worktree run beside |

**The host stamp**, on every platform and beside every digest: `uname -srm`;
`platform.platform()` and `sys.version`; the numpy version and `numpy.show_runtime()` (the
SIMD dispatch); the CPU model (`/proc/cpuinfo` on Linux, `sysctl -n machdep.cpu.brand_string`
on the Mac). The web session is the container for the leg. GitHub Actions `ubuntu-latest`
(Linux x86-64, Python 3.11, the locked sync of `scripts/setup_env.sh`) is named a second
container instance, for the campaign tier and `check.sh`: a deviation from Q3's answer, which
named the web session, so the PR lists it as a named deviation for the owner's ruling at
review. The `docker run --platform linux/amd64` path this card first offered is not used: Q3
named the web session, and x86-64 emulation on arm64 is unproven.

### Remote leg

The web session is dispatched by this card's path and reads this section. It runs on Linux
x86-64, Python 3.11, `uv sync --frozen`, at `$0` (no provider, no `.env`, no `--complete`),
never pushes to `main` or `work/ml-reground-baseline-9`, and opens no pull request.

1. **Host stamp** first, as defined above, and beside every digest.
2. **R0, only when this Mac missed a refit's bytes at both `39a568c6` and `1793eb23`**
   (acceptance item 1). At `39a568c6`, the three refit commands in Validation must hash byte
   for byte to `06b20508…`, `7e764b89…` and `62595367…`; a miss stops the card for the owner.
   On a match, the three baseline-9 refits run at the branch head the implementer names, and
   their weight files and `.sha256` sidecars join the hand-back.
3. **R1 at `39a568c6`** (`git fetch origin && git checkout --detach 39a568c6 && uv sync
   --frozen`): the Validation leg command. It must reproduce the §6.1 machine verdict and the
   seven §6.2 arms (`training/reports/report-composed-runner.md:208-237`) and both adoption
   constraints as full strings (`scripts/verify_ml_evidence.py:1812-1815`), and it records its
   JSON's sha256 and `es_digest` beside the Mac's (the investigation read `bddf96d5…` and
   `00d2c414…`; the implementer's dispatch-time run supersedes them). A cell that differs: stop
   and report, no re-run.
4. **R2 at the branch head the implementer names**, once the constants commit is pushed: the
   same command, its JSON's `baseline_id` reading `baseline-9`.
5. **Hand-back by branch, never by paste.** One proof JSON (the host stamp, each SHA, each
   command, each digest, a match boolean per comparison) and the R1 and R2 leg JSONs (after
   R0, also the baseline-9 refit weights and sidecars) are committed together to the session's own `claude/<slug>` branch, with
   `Card: tasks/work/ml-reground-baseline-9.md` in the body, and pushed. The local session
   fetches it, reads each file by commit SHA (`git show <sha>:<path>`), checks each file's
   sha256 against the proof, and quotes the proof in Results by SHA. The branch is never merged
   and never deleted.

**The decision rule.** R1: if Linux misses the committed cells while the Mac reproduces them,
the card stops for the owner's ruling between the container rule and the reproduction rule.
R2 against the Mac leg at the same head: identical sha256, the verdict is written from it and
both platforms are named; equal cells but different bytes, it is written from the Linux JSON
and the byte difference is reported; any cell differs, stop and report. Every leg JSON the
verdict uses reads `baseline_id` `baseline-9`.

**Spend and inputs.** `$0`: no provider, model call, recorder or held-out generator (band
2100-2999 stays unseen); no `--complete`, which needs the evidence fetch and adds only
evidence-branch rows unrelated to the fits. A bare shell with no `AILIBI_*` export and no
`.env`; rollouts use the fake provider (`training/provenance.py:29-36`).

**No recorded byte moves.** Under `replays/` only `replays/ml_corpus/README.md` changes; the
corpus MANIFESTs keep their stale FROZEN line (record §7.2), since an edit re-fingerprints the
corpus (`3eebc7d5`). Nothing is re-scored. Recorded campaign rows
(`training/reports/results-*.jsonl`), the coevo tree, the `utility-es`, `policy-es` and
`bc-dagger` genomes, `training/artifacts/crew/` and the runner-up stamp naming the anchor are
never re-stamped (21.17's rulings); the λ grid and the campaign are not re-searched or re-run
(Q2). No ES byte moves; one that does stops the card and is never re-stamped.

**The freeze.** Nothing changes under `engine/`, `agents/` (the prompt set included),
`meetings/`, `observation/`, `orchestrator/` or `eval/`, checked from the merge base so that
card B's docstring-only edit, merged from `main`, cannot trip it (Validation).

**Role-correctness gates nothing.** The fits are fidelity to the record, not correctness: a
fit that predicts the recording's wrong ejection is right. No bar, ceiling or comparator is
retuned; a bar that cannot be evaluated on these bytes stops the card.

**Wall budget and stop rule.** Each budget is about twice the larger of 21.17's
commit-timestamp bound and the investigation's measurement on this Mac (re-measure):

| step | bound | budget |
|---|---|---|
| reproduction at `39a568c6` (fingerprint, verifier, three refits, pool) | ≤ 50 min (21.17); about 90 s here, leg included | 60 min |
| surrogate, conviction, composed fidelity, Mac leg | ≤ 26 min (21.17) | 55 min |
| walk, anchor, study and pool | ≤ 24 min (21.17) | 50 min |
| web session: setup, R0 when needed, R1, R2, hand-back | 45.4 s per leg here; about 20 s per set of three refits here | 60 min |
| campaign tier | 157 s (21.17); 204.9 s here; 400.0 s on Actions | 10 min here; 30 min on Actions |

Total compute stays inside 4 h. Stop and report with the partial output on: a step past its
budget (never a silent retry); a refit that misses its committed bytes on every host tried
(this Mac at `39a568c6` and `1793eb23`, then R0), or a refit that matches at `1793eb23` but not
at `39a568c6`; an R1 or R2 outcome the decision rule stops on; `raw_mismatches` ≠ 0 or a `CorpusWalkError`; a
pin that moves for any reason but the re-fit (a λ genome, a coevo row, a corpus byte, an ES
byte). A verdict flip or a changed constraint set does not stop the card (Q4).

**Prerequisites and ownership.** [The re-record](process-rerecord.md) has merged. Base:
`main` after the orchestrator's planning commit carrying this amendment and cards B
(`tasks/work/committed-channel-rederivation.md`) and C
(`tasks/work/report-fog-and-counterfactual-freeze.md`). One writer per file: this card writes
the files under Expected scope, which include `docs/artifacts.md` rows `:103` and `:104` only.
Card B writes `tests/_helpers/committed.py`, `tests/_helpers/test_committed_single_home.py`,
`tests/meetings/test_contradictions.py`, `tests/meetings/test_transcript.py`,
`tests/eval/test_evidence_honesty.py`, `tests/agents/test_reported_testimony.py` and one
docstring span (`eval/evidence_honesty.py:2295-2297`); card C writes `api/replay_loader.py`,
`tests/api/test_view_model.py`, `tests/scripts/test_counterfactual_phase21.py`,
`audits/audit-phase-21-counterfactual.md` and `docs/artifacts.md` row `:109`.
~~Under Q1 (a) the genuine-class card (record §7.1, second item) merges first, because
`eval/vote_correctness.py` is in the derivation closure.~~ *Not applicable (2026-09-23): Q1
ruled version one, and that card merged anyway as #478.*

**Status and the task index.** `tasks/README.md` is the orchestrator's.
`scripts/validate_task_docs.py` derives its inventory sentence from every card's
`**Status:**`, so any Status flip here would redden `check.sh`. The worker therefore fills
Results and leaves the Status line to the orchestrator, who flips it together with the
sentence in one commit.

**Merge order and done (identical in the three baseline-9 cards).** Card A is
`tasks/work/ml-reground-baseline-9.md`, card B is `tasks/work/committed-channel-rederivation.md`
and card C is `tasks/work/report-fog-and-counterfactual-freeze.md`. Merge order: B, then C,
then A last, after merging `main` into its branch. If A is ready first, it may merge first.
Whichever pull request merges last merges `main` into its branch first and shows
`bash scripts/check.sh` fully green on `main`. A card is done when every acceptance item has
evidence and every id still failing at its gate belongs to one of the other two cards.

**Done (Q5).** For this card, the other two cards' ids are these nine, as they read at
`95fb894b` (or their renamed successors, as those cards' Results name them):
- `tests/meetings/test_contradictions.py::TestGroundedProsecutionCommittedCensus::test_the_fully_grounded_leg_drops_the_whole_class` (B)
- `tests/meetings/test_contradictions.py::TestGroundedProsecutionInjusticeShapes::test_no_committed_ejection_rides_a_strong_sighting_flag` (B)
- `tests/agents/test_reported_testimony.py::test_reported_rows_survive_in_every_candidate_bucket` (B)
- `tests/eval/test_evidence_honesty.py::test_the_band_change_not_the_fold_is_what_costs_first_hand_coverage` (B)
- `tests/meetings/test_transcript.py::TestCommittedBytesArtifactCollapse::test_rederivation_diverges_only_at_the_repaired_sites` (B)
- `tests/eval/test_evidence_honesty.py::test_the_instrument_and_the_detector_read_one_adjacency_rule` (B)
- `tests/api/test_view_model.py::test_report_tick_fog_keeps_the_reported_body` (C)
- `tests/scripts/test_counterfactual_phase21.py::test_the_memo_table_equals_a_live_four_set_run` (C)
- `tests/scripts/test_counterfactual_phase21.py::test_the_memo_marks_every_advisory_cell` (C)

**The deferred cost, stated in Results.** The first current install of either fit must mint
version two at its own commit, and it inherits: the identity row
(`scripts/verify_ml_evidence.py:1716-1781`) and grounding row (`:1966-2061`) switching to
`fit_corpus_fingerprint`; the inversions of `test_historical_verifier_refuses_relabeled_fit_version`
(`tests/scripts/test_verify_ml_evidence.py:636`), of `test_current_loader_refuses_historical_fit`
(onto a planted version-one copy), of the pool ingest (`tests/training/test_hall_of_fame.py:519-548`)
and of the anchor pin's scope check (`tests/training/test_anchor_study.py:764`); the function
switches at `tests/training/test_surrogate_runner.py:553`, `:599` and
`tests/training/test_composed_runner.py:966`; and the closure churn. Which code closure
version two binds, for the fits and for each stamp, goes to the owner before that install.

**Questions for the owner, answered 2026-09-23.**
- **Q1 (blocked the first write): which identity version? ANSWERED.** Asked: *historical,
  version one* (records keyed to `6536c68c…`, historical stamps, no kind field; listed here as
  (b)) or *current, version two* (`fit_corpus_fingerprint` at the fit commit, version-two
  stamps; listed as (a)). Owner: "Look into how it should best be fitted and implement your
  recommended strategy." Ruling: version one, `historical_fit_corpus_fingerprint` (**Keying**,
  above), named by function because the investigation lettered the options the other way
  round. Each "Q1 (a)" clause in this card (Prerequisites, Expected scope, Record impact) is
  struck through and marked not applicable, dated, where it stands.
- **Q2: the campaign tier. ANSWERED.** Owner: "Go with your recommendation." Ruling: in scope
  as tests; all 27 campaign reds turn green as consequences, with no re-search and no campaign
  re-run.
- **Q3: which container is available? ANSWERED.** Owner: "The previous Linux environment used
  was a Claude code session dispatched to the web." Ruling: the Goodhart leg runs in a Claude
  Code web session on Linux, a required gate (**Remote leg**); Actions gating the campaign tier
  and `check.sh` is the named deviation above.
- **Q4: a verdict flip. ANSWERED.** Owner: "Publish and wait for the merge." Ruling: a GO/NO-GO
  flip, and a changed adoption-constraint set alike, publishes as it reads, is named first in
  the PR, and waits for the owner's merge; nothing downstream is re-pointed.
- **Q5: "done" with the nine non-ML reds standing? ANSWERED.** Owner: "Look into why the tests
  would still fail, if they are necessary at all, or a separate potential path forward. Go with
  the recommended idea from that." Ruling: the nine were root-caused and routed to cards B and
  C, and this card's done rule is **Done**, above.

**Still open for the owner, not blocking.** The version-two closure scope (the deferred cost);
the contingency in which R1 fails on Linux while the Mac reproduces; Actions as the gating
Linux run. Routed, not done here: a campaign-tier refit pin for the filtered-BC anchor (about
5 s in the investigation).

## Expected scope

Artifacts: `training/artifacts/{surrogate,conviction,composed}/` (every file);
`training/artifacts/anchor_study/` (`filtered-bc-anchor/`, the stamp in each
`lambda-*/config.json`, `study.json`); two fields of
`training/artifacts/impostor/map-elites/cells/index.json`. Code:
`training/bakeoff/harness.py:188`, `training/anchor_study.py:162-172`, the three coupled
literals; comment-only, the docstrings at `training/anchor_study.py:222-226` and
`training/bakeoff/map_elites.py:712-716`; `scripts/verify_ml_evidence.py` only for a
constraint pin the leg moves (Q4) ~~or under Q1 (a)~~ *(not applicable, 2026-09-23: Q1 ruled
version one)*. Tests, re-pins, renames and planted cases only, file by file:
- written: `tests/training/{test_surrogate_runner,test_conviction_model,test_composed_runner,test_anchor_study,test_bakeoff_methods,test_bakeoff_harness}.py`;
  the shared refit-pin helper and its two perturbed cases under `tests/training/`; the
  grounding parametrization in `tests/scripts/test_verify_ml_evidence.py`;
- expected green by the re-fit alone, edited only for a measured re-pin or a docstring whose
  outcome claim changes, each edit named in Results:
  `tests/training/{test_goodhart_probe,test_crew_scorer,test_crew_owned_tasks,test_coevo_driver}.py`,
  `tests/eval/test_balance_eval_meeting_runner.py` and
  `tests/experiments/test_torch_probe_excluded.py` (card B writes neither of the last two),
  and any other `tests/training/` file whose pin reads a committed fit;
- read only: `tests/training/test_hall_of_fame.py` and
  `tests/training/test_model_evidence_provenance.py` (`:98-116` stays unchanged), whose red
  tests turn green by the re-fit and the re-stamps alone.

Documents: the four
`training/reports/report-{ballot-surrogate,conviction-model,composed-runner,anchor-study}.md`
(the two §8 recipes corrected), `docs/ml-program.md`, `docs/artifacts.md` rows `:103` and
`:104`, the `replays/ml_corpus/README.md` blockquote, the `training/README.md` sentence, the
`docs/glossary.md` lines for any term the new prose defines, and this card. Not in scope: recorded bytes, the frozen directories, `eval/`, the recipes
(`training/surrogate/`, `training/conviction/`, `training/rewards.py`),
`scripts/record_ml_corpus.sh`, `frontend/`, `api/`, `audits/`, `tests/_helpers/`,
`tests/meetings/`, `tests/agents/`, `tests/api/`, the rest of `tests/eval/`,
`tests/scripts/test_counterfactual_phase21.py`, `docs/artifacts.md` row `:109`,
`docs/process-scorecard.md` and `tasks/README.md`.

Delivered on `work/ml-reground-baseline-9` by one pull request into `main` (merge or
fast-forward, never squash), each commit carrying `Card: tasks/work/ml-reground-baseline-9.md`.
Order:
1. reproduction at `39a568c6`;
2. surrogate, with its report;
3. conviction, with its report;
4. the constants, with the anchor, study and pool stamps and the two docstrings, in one commit;
5. push; the Mac leg; the web session's R1 and R2; the composed verdict, with its report;
6. tests;
7. the remaining documents; merge `main` if card C has landed, then recompute
   `docs/artifacts.md` rows `:103` and `:104` last;
8. the gates: the Mac runs beside, the PR's CI, the campaign-tier dispatch; any flip or changed
   constraint set named first in the PR; then wait for the owner's merge.

## Record impact

The adopting record for the ML fits; no recorded replay byte, rendered prompt byte or detector
output moves, and gameplay is unchanged. The fit bundles, the anchor weights and the study,
λ-config and pool stamps move, all in the version-one, historical shape, and so do
`BAKEOFF_BASELINE_ID` and `HIGH_FLAG_FLOOR`, so bake-off selection reads baseline 9's five
supply gauges; the documents in scope recompute. Moving the frozen side is legitimate here and
only here: it is the half of the pair a re-record may not move (`3eebc7d5`), and these fits
were made on these bytes. Earlier verdicts stay as labelled history in the reports' errata;
baseline 8's fits stay reachable at `39a568c6`. The demo rebuild on merge
(`.github/workflows/pages.yml`) reads none of these files. Nothing is promoted to current: the
records restore only through explicit historical diagnostics (`docs/architecture.md`, "Current
model evidence"). The next corpus recording re-stales the fits as this one did; ~~under Q1
(a), so does any edit to the 109-file closure~~ *(not applicable, 2026-09-23: Q1 ruled version
one, so a closure edit re-stales them only if it moves a refit or a verdict, which the refit
pins and recompute rows then report)*.

## Validation

```
# host stamp, on every platform, beside every digest
uname -srm
uv run python -c "import platform,sys,numpy; print(platform.platform()); print(sys.version); print(numpy.__version__); numpy.show_runtime()"
sysctl -n machdep.cpu.brand_string          # the Mac; on Linux: grep -m1 'model name' /proc/cpuinfo
# reproduction: detached worktree at 39a568c6 (1793eb23 for a refit that misses its bytes), uv sync --frozen there; the three refit lines are also R0's
uv run python -c "from pathlib import Path; from training.provenance import historical_fit_corpus_fingerprint as f; print(f(Path('replays/ml_corpus/9p2i')))"
uv run python scripts/verify_ml_evidence.py --only sidecars --only corpus --only recompute
uv run python -c "import hashlib; from pathlib import Path; from training.surrogate import build_meeting_table; from training.surrogate.ballots import fit_corpus_ballot_predictor; p=fit_corpus_ballot_predictor(build_meeting_table(Path('replays/ml_corpus/9p2i'))); print(hashlib.sha256(p.to_artifact_json().encode()).hexdigest())"
uv run python -c "import hashlib; from pathlib import Path; from training.conviction.model import fit_corpus_conviction_model; m,_,_=fit_corpus_conviction_model(Path('replays/ml_corpus/9p2i')); print(hashlib.sha256(m.to_artifact_json().encode()).hexdigest())"
uv run python -c "from pathlib import Path; from training.anchor_study import run_anchor_study; run_anchor_study(lambda_grid=(), artifact_root=Path('$SCRATCH/anchor'), verify_committed_champion=False)" && cat "$SCRATCH/anchor/filtered-bc-anchor/weights.json.sha256"
# the Goodhart leg (report-composed-runner.md §9 at historical scope): the Mac beside; R1 and R2 in the web session
uv run python -c "from training.bakeoff.es import ESConfig; from training.composed_runner import run_composed_goodhart_leg; c=ESConfig(generations=6, population=6, sigma=0.5, seed=0, fitness_seeds=tuple(range(8)), init_scale=0.5); print(run_composed_goodhart_leg(config=c, evidence_scope='historical').to_json())"
# the version-one record, once write_ballot_predictor_artifact(..., max_uses=derive_max_uses(355)) has written the weights (conviction: same shape)
uv run python -c "from pathlib import Path; from training.provenance import historical_fit_corpus_fingerprint as f; from training.surrogate.runner import FIT_CORPUS_FILENAME, SurrogateFitCorpus; C=Path('replays/ml_corpus/9p2i'); a=Path('training/artifacts/surrogate'); d=(a/'ballot-predictor.json.sha256').read_text().split()[0]; (a/FIT_CORPUS_FILENAME).write_text(SurrogateFitCorpus(corpus_set='9p2i', corpus_sha256=f(C), fit_side_meetings=355, weights_sha256=d).model_dump_json(indent=2)+'\n')"
# stamps, after the constants move and the scratch anchor re-fit is copied in; each is idempotent
uv run python -c "import json; from pathlib import Path; from training.anchor_study import historical_compute_substrate_sha as h; p=Path('training/artifacts/anchor_study/filtered-bc-anchor/config.json'); c=json.loads(p.read_text()); c.pop('substrate_sha_kind', None); c.pop('evaluation_evidence_scope', None); c['substrate_sha']=h(); p.write_text(json.dumps(c, indent=2, sort_keys=True)+'\n')"
uv run python -c "import json; from pathlib import Path; from training.bakeoff.harness import BAKEOFF_BASELINE_ID as b; from training.bakeoff.map_elites import historical_bakeoff_substrate_sha as h; p=Path('training/artifacts/impostor/map-elites/cells/index.json'); d=json.loads(p.read_text()); d['baseline_id']=b; d['substrate']['substrate_sha256']=h(); d['substrate'].pop('substrate_sha_kind', None); p.write_text(json.dumps(d, indent=2, sort_keys=True)+'\n')"
# the hand-back, read by SHA
git fetch origin claude/<slug> && git show <sha>:<path> | shasum -a 256
# at the head
uv run python scripts/verify_ml_evidence.py                  # offline; FAIL 0
uv run pytest tests/training tests/scripts/test_verify_ml_evidence.py tests/eval/test_balance_eval_meeting_runner.py tests/experiments/test_torch_probe_excluded.py -q
uv run pytest -m campaign -q                                 # this Mac, beside
gh workflow run campaign-tier.yml --ref work/ml-reground-baseline-9 && gh run list --workflow campaign-tier.yml --branch work/ml-reground-baseline-9 --limit 1
uv run python scripts/check_doc_facts.py && uv run python scripts/validate_task_docs.py
bash scripts/check.sh                                        # whole, clean worktree, this Mac, beside the PR's CI
git diff --stat $(git merge-base origin/main HEAD) HEAD -- engine agents meetings observation orchestrator  # empty
git diff --stat $(git merge-base origin/main HEAD) HEAD -- replays eval docs/process-scorecard.md  # replays/ml_corpus/README.md only
```

The anchor re-fit at the head reuses the fit-only `run_anchor_study` call into a scratch root
(it re-searches nothing). Results quotes it, the two stamp commands above, the `study.json` and
λ `config.json` re-stamps (commands of the same idempotent form), and the census and tie-break
commands whole; it cites `docs/architecture.md` "Determinism and the substrate ladder" and
"Current model evidence", and the PR fills every section of its template.

## Results

Not started.
