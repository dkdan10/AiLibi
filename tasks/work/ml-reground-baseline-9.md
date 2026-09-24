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

- [x] **Reproduce first, on the bytes each artifact was made on.** In a detached worktree at
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
- [x] **Surrogate, then conviction, re-fit on baseline 9 at version one** by
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
- [x] **Each refit pin has a committed perturbed case.** The ULP comparison in both
  `test_committed_artifact_round_trips_and_the_refit_no_longer_matches` pins is factored into
  one helper under `tests/training/`; each instrument gains a case feeding it a refit made on
  the live fit-side rows with one feature shifted by +0.125 (`belief_suspicion` for the
  surrogate; one conviction feature, named in the test), which must raise `AssertionError`.
  Mechanism: the helper, which both pins call. Proof: the perturbed case fails the helper while
  the unperturbed refit, through the same helper, passes.
- [x] **`BAKEOFF_BASELINE_ID` becomes `"baseline-9"`** at `training/bakeoff/harness.py:188`
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
- [x] **Anchor study and pool: re-ground and re-stamped in the historical shape, not
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
- [x] **The composed verdict is re-derived last** (`run_composed_fidelity` →
  `decide_composed_go` with the agreed leg's adoption constraints → both writers), from the
  fresh leg in the container: the web session's R2 at historical scope after the constants
  commit, its JSON reading `baseline_id` `baseline-9`, taken by the decision rule under
  **Remote leg**. A constraint set that differs from `scripts/verify_ml_evidence.py:1812-1815`
  publishes as it reads: the pin moves in this pull request, named first in it, and the owner's
  merge rules it (Q4). Mechanism: the verifier's composed rows and
  `test_committed_composed_verdict_is_rederivable`. Proof: a one-character constraint edit in a
  temporary copy fails the full-string comparison.
- [x] **Verdicts publish as they read; no bar moves.** `git diff` is empty on
  `training/surrogate/fidelity.py` and `training/conviction/fidelity.py`; a GO/NO-GO flip
  publishes as it reads, is named first in the PR and waits for the owner's merge, with nothing
  downstream re-pointed (Q4). Mechanism: the verdict writers and recompute rows. Proof:
  `_verdict_identity_row`'s planted corpus-derived and corpus-independent drift cases stay red.
- [x] **The verifier reads FAIL 0 offline**, with no verifier logic change: the identity and
  grounding rows name `6536c68c…` for both fitted records, keyed to the new digests, and the 12
  rows read OK. Mechanism: `scripts/verify_ml_evidence.py`. Planted proof: the existing
  undeclared-corpus, other-weights, relabelled-version, perturbed-replay and perturbed-weight-hash
  cases still fail their perturbed halves, and the grounding plant is a new parametrization of
  `test_an_undeclared_corpus_still_fails_the_grounding_row`
  (`tests/scripts/test_verify_ml_evidence.py:596`), not a near-copy: `cc54d3c0…` written back
  into a temporary copy's `fit-corpus.json` beside the new weights reads FAIL on grounding.
- [x] **All 68 tests are green, and every other committed-fit reader is re-derived**,
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
- [x] **Both readings are settled by measurement**: for the ceiling, a per-meeting 2×2 census
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
- [x] **The keying rule is written down, scoped to what enforces it.** `training/README.md:48-49`
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
- [x] **Derived documents are recomputed, never hand-written.** The four training reports
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
- [x] **The campaign tier is green on Linux**: `gh workflow run campaign-tier.yml --ref
  work/ml-reground-baseline-9` on GitHub Actions `ubuntu-latest` reads 335 passed (its count at
  `39a568c6`), any other count explained id by id (a perturbed refit case this card marks
  `campaign` is such a difference), with its run id quoted and the Mac run beside. Mechanism: pytest in `.github/workflows/campaign-tier.yml` (`:28`, `:59`, `:64`).
  Proof: at the re-record's close it read 308 passed, 25 failed, 2 errors.
- [x] **`bash scripts/check.sh` has no ML red** in the pull request's CI `project-checks` and
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

**What this section covers (2026-09-23).** Two operators filled it in order. §1-§8 are the
local legs: the reproduction, the surrogate and conviction re-fits, the constants with the
anchor, study and pool stamps, the Mac Goodhart leg at the constants commit, the tests the
local legs could re-pin, and the documents that do not depend on the Linux leg; they claim no
Linux result, and their **Left for the next operator** lists are the hand-off, each item done
in §9-§13. §9-§13 finish the card: the web session's hand-back read by SHA and the decision
rule, the composed verdict and manifest written from the agreed leg, the composed-dependent
re-pins, the remaining documents, and the gates on the merged branch. §14 sets each step's
wall time against its budget and names the one step past it. §15 states the limitations: what
this evidence does not establish. Where §8's status list and §9-§13 differ, §9-§13 are the
later reading.

**The host stamp** (this Mac; beside every digest below unless another host is named):

| field | value |
|---|---|
| `uname -srm` | `Darwin 24.6.0 arm64` |
| `platform.platform()` | `macOS-15.7.3-arm64-arm-64bit` |
| `sys.version` | `3.11.15 (main, Apr 14 2026, 14:45:51) [Clang 22.1.3 ]` |
| numpy | `2.2.6`; `numpy.show_runtime()` SIMD baseline `NEON, NEON_FP16, NEON_VFPV4, ASIMD`, found `ASIMDHP`, not found `ASIMDFHM` (BLAS from Accelerate) |
| CPU | `Apple M1 Pro` (`sysctl -n machdep.cpu.brand_string`; kernel `RELEASE_ARM64_T6000`) |
| shell | bare: no `AILIBI_*` variable exported, no `.env` in the worktree |

Short form used below: **[Mac]** = this stamp.

### 1. Reproduction at `39a568c6` (acceptance item 1)

A scratch export of `39a568c6` outside the tree (`git archive --format=tar -o
$SCR/b8-39a568c6.tar 39a568c6`, unpacked to `$SCR/b8`, `uv sync --frozen` there), run with
the Validation block's commands verbatim. Nothing under `training/artifacts/` in the work
tree was touched until every line below had passed. Each comparison is a byte match
(`sha256`), never a tolerance.

| step | command (Validation block) | measured [Mac] | committed at `39a568c6` | match | wall |
|---|---|---|---|---|---|
| version-one corpus identity | `historical_fit_corpus_fingerprint` line | `cc54d3c02a9804d3…` | `cc54d3c0…` in both `fit-corpus.json` | yes | 1.4 s |
| verifier subset | `verify_ml_evidence.py --only sidecars --only corpus --only recompute` | exit 0; 28 checks, OK 22, FAIL 0, ABSENT 6 | exit 0 | yes | 21.9 s |
| surrogate refit | the `fit_corpus_ballot_predictor` line | `06b2050889271c267af2e5d083ba46099bbb55120ca834f4d357733f0e2dcda8` | `ballot-predictor.json` sha256 the same | yes | 3.5 s |
| conviction refit | the `fit_corpus_conviction_model` line | `7e764b89fb0bec445c3b19e2e0f07de89d9011c1e4fc1b0a6b32b1004cb151ed` | `conviction-model.json` sha256 the same | yes | 11.0 s |
| filtered-BC refit | the `run_anchor_study(lambda_grid=(), …)` line into `$SCR/repro-anchor-39a568c6` | `62595367954fe8bd19f4dc8b73e547170d0185c7fde1b00815df729de6f45a7e` | `filtered-bc-anchor/weights.json.sha256` the same | yes | 4.2 s |
| pool re-stamp | the `index.json` stamp line, in place in the export | `e43335ba8cd0e6a59598db466bbee8dc838c795e77fa3c5fdd18dd70d44a81ad`, `cmp` identical to the file before | `e43335ba…` | yes | 0.4 s |
| Goodhart leg (beside, not gating) | the Validation leg line, stdout to a file | HELD; `to_json()` sha256 `bddf96d5d0176505bfb7b6bc4d85eeab7da132641089f7d2b3fafa1fd44a1ffe`; `es_digest` `00d2c4147613d3ae33062778d3dd1c7d4509fd73c089a60c36f46dbc92c610dd`; `baseline_id` `baseline-8`; 1175 composed meetings; conviction uses 1513 (1175 + 338) | no committed digest; the cells are the record | the investigation's `bddf96d5…` / `00d2c414…` reproduced | 43.6 s |

The six ABSENT rows are the evidence-branch rows and the git-index inventory row, which an
archive cannot carry; every recompute row, both weight hashes and both adoption constraints
read OK. The fallback to `1793eb23` was not needed: no refit missed. The leg's JSON digest is
taken over `to_json()`'s text, the printed line without its trailing newline (the stdout file
with the newline hashes `de9d8f1a…`); R1 and R2 compare the same form.

**Perturbed proof** (the same three refits on the baseline-9 corpus at `ff4c6bb8`, before
any artifact moved, [Mac]): surrogate `f89016200e94e1f1…`, conviction `3a6fe4ca18cb0597…`,
filtered-BC at the unmoved floor 147/151 `d6b3f3a79607992a…`; none matches its committed
digest, and `historical_fit_corpus_fingerprint` reads `6536c68c1ad37bc8…` against the
records' `cc54d3c0…`. The live fit side is 355 meetings against the record's 348.

### 2. The surrogate on baseline 9 (acceptance item 2, surrogate half)

Run in the work tree at `1127044f` on the corpus the 2026-09-22 record left, [Mac], in the
recipe's order; each step's output is the next step's input.

1. **Walk re-validation first:** `measure_belief_render_parity(Path('replays/ml_corpus/9p2i'))`
   (the report's §9 line) reads `raw_mismatches` **0**, `trust_mismatches` 0, 449 meetings,
   2539 rows, 12 760 cells, J1 divergence 82 cells / 80 rows (fit 61, test 21), max 0.11.
2. **Weights, sidecar and cap**, with the fit side measured before the cap is derived:
   ```
   uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table; from training.surrogate.fidelity import build_meeting_views; from training.surrogate.ballots import fit_corpus_ballot_predictor, write_ballot_predictor_artifact, derive_max_uses; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); test=set(t.splits.test); n=sum(1 for v in build_meeting_views(t) if v.seed not in test); assert n == 355, n; print(n, derive_max_uses(n), write_ballot_predictor_artifact(fit_corpus_ballot_predictor(t), Path('training/artifacts/surrogate'), max_uses=derive_max_uses(355)))"
   ```
   printed `355 50765 f89016200e94e1f136c26ba6bc4293a7fe9ad9b1b7406ff7f973ed342ccfa1d4`
   (3.6 s) [Mac]. The weights equal the investigation's same-host expectation `f8901620…`.
3. **The version-one record**, the Validation block's `SurrogateFitCorpus` line verbatim: no
   `fingerprint_version` argument, `model_dump_json(indent=2)` plus a newline, so the file
   carries `corpus_sha256` `6536c68c1ad37bc8874186e3590788ab9fd91bc7d3eaa8d914036f704e649608`,
   `fit_side_meetings` 355 and the new weights digest, and no version key.
4. **The verdict**, on the first held-out evaluation, through the writer that emits the sidecar:
   ```
   uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table, run_surrogate_fidelity, fo6_rebaseline; from training.surrogate.fidelity import decide_go_no_go; from training.surrogate.ballots import BallotSurrogateModel; from training.surrogate.runner import write_surrogate_verdict_artifact; a=Path('training/artifacts/surrogate'); d=(a/'ballot-predictor.json.sha256').read_text().split()[0]; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); v=decide_go_no_go(run_surrogate_fidelity(t, lambda: BallotSurrogateModel(t), model_name='ballot-surrogate.v1'), fo6_rebaseline(t), weights_sha256=d); write_surrogate_verdict_artifact(v, a); print(v.verdict, v.ranking_verdict, v.decision_verdict)"
   ```
   printed `NO-GO GO NO-GO` (3.6 s): **no flip**, the same verdict baseline 8 published.
   `verdict.json` sha256 `06ce819fb626093aa0c9c95c53c380f4a3c0bef20a9a8de469137dbd4fc83438`.

| surrogate axis (94 held-out meetings, 52 ejections) | baseline 9 | bar | baseline 8 (history) |
|---|---|---|---|
| 1. top-1 ≥ 0.75 × ceiling | 0.8846 (46/52) PASS | 0.5913 | 0.8246 (47/57) PASS |
| 2. top-1 > FO-6 | 0.8846 PASS | 0.3077 | 0.8246 PASS |
| 3. SKIP-vs-eject > always-eject | 0.4681 (44/94) FAIL | 0.5532 | 0.3956 (36/91) FAIL |

The frozen committed weights reproduce the harness's figures (verifier rows: top-1 46/52,
decision 44/94), and the verifier's surrogate top-1, SKIP-vs-eject and `verdict.json` rows read
OK after the report refresh (`--only recompute`, [Mac]). `training/reports/report-ballot-surrogate.md`
§2.1-§7 and §9 are refreshed from the §9 one-liners re-run here, the baseline-8 figures kept
in a new erratum, §8's recipe corrected to `historical_fit_corpus_fingerprint` with the verdict
writer named, and one stale test id in §9 corrected to the pin's real name.

**The two readings, settled by measurement (acceptance item 10).** Neither docstring in
`training/surrogate/fidelity.py` or `tests/training/test_surrogate_fidelity.py` is edited;
both rulings stay the owner's.

- *The ceiling.* The census command (report §9, quoted whole there):
  ```
  uv run python -c "from pathlib import Path; from collections import Counter; from training.surrogate import build_meeting_table; from training.surrogate.ballots import BallotSurrogateModel, load_ballot_predictor_artifact; from training.surrogate.fidelity import build_meeting_views, _is_strict_leader; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); m=BallotSurrogateModel(t, predictor=load_ballot_predictor_artifact(Path('training/artifacts/surrogate'))[0]); c=Counter((m.predict(v).ranking[0]==v.ejected, _is_strict_leader(v, v.recon_suspicion, v.ejected)) for v in build_meeting_views(t) if v.seed in set(t.splits.test) and v.is_ejection); print(sorted(c.items()))"
  ```
  Known-answer control first: pointed at the frozen baseline-8 weights (the `39a568c6`
  export's `training/artifacts/surrogate`, the same bytes as at `95fb894b`) on this corpus it
  reads hit 46 of 52 against 41 reachable, the Evidence figure, so the command is right. On
  the re-ground fit: (hit, reachable) 40, (hit, not reachable) 6, (miss, reachable) 1, (miss,
  not reachable) 5; the cells sum to 52 and the hit column to the verdict's 46. The six
  hit-but-unreachable meetings are all ties at the saturated 1.0 best-case score, the ejected
  player carrying a witnessed vent and a flag in each: 1029 m2 (`p-1` tied with `p-8`), 1069
  m1 (`p-8`/`p-2`), 1094 m0 (`p-5`/`p-3`), 1144 m0 (`p-3`/`p-6`) and 1149 m0 (`p-8`/`p-1`),
  where the sum of per-voter ballots favours the ejected player (one to three voters' own rows
  lead it), and 1084 m0 (`p-3`/`p-6`), an exact tie in the surrogate's shares broken by the
  lowest-id rule. The ceiling's strict-leader rule counts a tie as unreachable, so it is not a
  maximum for a ranker that breaks ties; the baseline-8 weights show the same six. (Per-meeting
  detail from `$SCR/ceiling_census.py`, which adds the tie partner, per-voter leads and shares.)
- *The tie-break.* The table command (report §9, quoted whole there):
  ```
  uv run python -c "from pathlib import Path; from tests.training.test_surrogate_fidelity import _LowestTiedTauFo6 as L; from training.surrogate import build_meeting_table, fo6_rebaseline, run_surrogate_fidelity as r; [print(s, *((x.predicted_ejections, x.ejection_predicted_skips, round(x.skip_vs_eject_accuracy, 4), (x.top1, x.top2, x.brier, x.ece) == (y.top1, y.top2, y.brier, y.ece)) for x, y in ((r(t, L, model_name='fo6-physical-logistic'), f), (f, f)))) for s in ('samples/9p2i', 'samples/4p1i', 'ml_corpus/9p2i', 'ml_corpus/4p1i') for t in [build_meeting_table(Path('replays') / s)] for f in [fo6_rebaseline(t)]]"
  ```
  reproduces record §6.4 to four decimals: `samples/9p2i` 7/7, 86/86, 0.3862/0.3862;
  `samples/4p1i` 18/16, 9/10, 0.5897/0.5897; `ml_corpus/9p2i` 5/0, 50/52, 0.4362/0.4468;
  `ml_corpus/4p1i` 5/5, 1/1, 0.75/0.75; ranking and calibration identical on all four. FO-6 is
  fitted fresh on the table, so the re-fit cannot move the reversal (0.4468 against 0.4362 on
  the corpus test side); it is re-measured, not settled, and stays the owner's ruling.

### 3. The conviction model on baseline 9 (acceptance item 2, conviction half)

Run in the work tree at `ebc43d59`, [Mac], in the recipe's order.

1. **Walk re-validation, weights, sidecar and cap**, one call (`fit_corpus_conviction_model`
   runs `require_clean_walk` before any fit):
   ```
   uv run python -c "from pathlib import Path; from training.conviction.model import fit_corpus_conviction_model, write_conviction_model_artifact, derive_conviction_max_uses; m,t,p=fit_corpus_conviction_model(Path('replays/ml_corpus/9p2i')); fit=set(t.splits.train)|set(t.splits.val); n=sum(1 for r in t.rows if r.seed in fit); assert n == 355, n; print(p.raw_mismatches, n, derive_conviction_max_uses(n), write_conviction_model_artifact(m, Path('training/artifacts/conviction'), max_uses=derive_conviction_max_uses(355)))"
   ```
   printed `0 355 50765 3a6fe4ca18cb0597d8df4e155be190f4601d8bfc5dae25490e9a3f3b821d762e`
   (11.4 s) [Mac]: `raw_mismatches` 0, and the weights equal the investigation's same-host
   expectation `3a6fe4ca…`. `derive_max_uses(355) == derive_conviction_max_uses(355) == 50765`.
2. **The version-one record**, the Validation line with `a=Path('training/artifacts/conviction')`
   and the sidecar `conviction-model.json.sha256`: `corpus_sha256` `6536c68c…`,
   `fit_side_meetings` 355, keyed to `3a6fe4ca…`, no version key.
3. **The verdict**, first held-out evaluation, from the frozen weights just written:
   ```
   uv run python -c "from pathlib import Path; from training.conviction.model import load_conviction_model_artifact; from training.conviction.dataset import build_conviction_table; from training.conviction.fidelity import run_conviction_fidelity, decide_conviction_go, write_conviction_verdict_artifact; a=Path('training/artifacts/conviction'); m, d = load_conviction_model_artifact(a); r, _ = run_conviction_fidelity(build_conviction_table(Path('replays/ml_corpus/9p2i')), model=m); v=decide_conviction_go(r, weights_sha256=d); write_conviction_verdict_artifact(v, a); print(v.verdict, v.flag_spearman, v.conversion_accuracy, v.conversion_recall)"
   ```
   printed `GO 0.8394835297890146 0.925531914893617 0.9545454545454546` (5.6 s): **no flip**.
   `verdict.json` sha256 `8eb85e3b17d61211cf4b7f093cf920612372b98179ddcfd961f2c9d17b742eab`.

| conviction axis (94 held-out meetings, 44 conversions) | baseline 9 | bar | baseline 8 (history) |
|---|---|---|---|
| 1. flag-count Spearman | 0.8395 PASS | 0.5 | 0.6670 PASS |
| 2. conversion recall | 42/44 = 0.9545 PASS | 0.5913 | 49/51 = 0.9608 PASS |
| 3. conversion accuracy | 87/94 = 0.9255 PASS | 0.5319 | 86/91 = 0.9451 PASS |

Confusion 42/5/2/45, the same cells the frozen baseline-8 weights read on these bytes (the
finding the record left: GO at 87/94). After the report refresh the verifier's `ML grounding`
row reads OK, naming `6536c68c…` for both records, and both conviction recompute rows and its
`verdict.json` row read OK (`--only recompute`, [Mac]); the seven composed rows (the three
composed channels, its `verdict.json` and `manifest.json`, and the two weight-hash rows, which
read `training/artifacts/composed/manifest.json`) stay FAIL until the composed step, which is
the next operator's. `training/reports/report-conviction-model.md` header, §2.1, §3, §4, §5
and §7 are refreshed from its §9 one-liners, the baseline-8 figures kept in a new erratum, and
§8 step 4 corrected to `historical_fit_corpus_fingerprint`.

### 4. The constants, with the anchor, study and pool stamps, in one commit (acceptance items 4 and 5)

**Constants.** `BAKEOFF_BASELINE_ID` `"baseline-8"` → `"baseline-9"` (`training/bakeoff/harness.py:188`,
its comment re-dated); `HIGH_FLAG_FLOOR` `147 / 151` → `107 / 145`
(`training/anchor_study.py:172`, comment restated as 17 recorded transcript + 90 persisted
vent flags, read from `eval/watchability.py:1050-1052`); the three coupled defaults
`run_goodhart_probe` (`training/bakeoff/goodhart.py:848`), `run_conviction_path_probe`
(`:1989`) and `run_composed_goodhart_leg` (`training/composed_runner.py:1247`) →
`"baseline-9"`. `eval/watchability.py` is untouched. Blast radius
(`grep -rln 'BAKEOFF_BASELINE_ID\|HIGH_FLAG_FLOOR' --include='*.py' --include='*.md' .`): the
code consumers are the four modules above plus `training/crew/scorer.py` (reads the constant,
no edit); the tests are the four re-pinned below; the rest are dated records (tasks,
audits, agent prompts, `training/reports/report-{crew-track,finalist-eval}.md`,
`replays/ml_corpus/README.md`, `eval/watchability.py` prose), none edited here.

**Mechanism for item 4.** `test_selection_bar_pins_the_baseline_8_floors` is renamed
`test_selection_bar_and_the_three_probe_defaults_pin_one_baseline` and asserts
`BAKEOFF_BASELINE_ID == "baseline-9"`, `HIGH_FLAG_FLOOR == 107 / 145` and, by
`inspect.signature`, that each of the three defaults equals the constant. Planted proof
(`$SCR/plant_literals.py`: each literal in turn set back to `"baseline-8"` with the other two
at `"baseline-9"`, the pin run, the file's bytes restored), [Mac]:

| literal reverted | pin |
|---|---|
| `run_goodhart_probe` | 1 failed, `AssertionError: run_goodhart_probe` |
| `run_conviction_path_probe` | 1 failed, `AssertionError: run_conviction_path_probe` |
| `run_composed_goodhart_leg` | 1 failed, `AssertionError: run_composed_goodhart_leg` |

**The anchor, re-fit into scratch after the constants moved** (the Validation line):
```
uv run python -c "from pathlib import Path; from training.anchor_study import run_anchor_study; run_anchor_study(lambda_grid=(), artifact_root=Path('$SCR/anchor-b9'), verify_committed_champion=False)"
```
walked all 150 games with no `CorpusWalkError` (5748 decisions; 111 qualifying games:
crew-winning 105, high-flag 71, both 65; 3798 fit decisions) and wrote weights
`6268ea3d7027a78c3300494b11fa89d2ee42247530d95078b95a34b928b69a6e` (5.3 s) [Mac]. Its
`weights.json`, `weights.json.sha256` and `config.json` were copied into
`training/artifacts/anchor_study/filtered-bc-anchor/`, and the config then stamped by the
Validation block's `config.json` line verbatim, run twice (both runs `20b7dd8e…`, idempotent):
the file loses `substrate_sha_kind` (the writer's `compute_substrate_sha.v2`) and takes
`historical_compute_substrate_sha()` = `b1fca5d43b2461a5110c0690a413ac96691e0eedaf910918d68793fc0d073413`,
the value the keying memo computed with the parameters passed explicitly.

**The five λ configs**, only `substrate_sha` changed, in the same idempotent form:
```
uv run python -c "import json; from pathlib import Path; from training.anchor_study import historical_compute_substrate_sha as h; s=h(); [p.write_text(json.dumps({**json.loads(p.read_text()), 'substrate_sha': s}, indent=2, sort_keys=True)+'\n') for p in sorted(Path('training/artifacts/anchor_study').glob('lambda-*/config.json'))]"
```
Each λ `weights.json` and sidecar hashes as before (`shasum` list compared before and after).

**`study.json`**, run twice (both `836c60551455f677…`):
```
uv run python -c "import json; from pathlib import Path; from training.anchor_study import historical_compute_substrate_sha as h; from training.bakeoff.harness import BAKEOFF_BASELINE_ID as b; p=Path('training/artifacts/anchor_study/study.json'); d=json.loads(p.read_text()); f=json.loads(Path('$SCR/anchor-b9/study.json').read_text())['filtered_bc']; f['artifact_path']='training/artifacts/anchor_study/filtered-bc-anchor'; d.pop('substrate_sha_kind', None); d.pop('evaluation_evidence_scope', None); d.update(baseline_id=b, substrate_sha=h(), filtered_bc=f); p.write_text(json.dumps(d, indent=2, sort_keys=True)+'\n')"
```
Only `baseline_id`, `substrate_sha` and `filtered_bc` changed; `sweep_rows`, `lambda_grid`,
`determinism_cross_check`, `eval_seeds` and `recommended_campaign_seeds` are byte-for-byte the
committed values, and no kind or scope key is present.

**The pool**, the Validation block's `index.json` line verbatim, run twice (both
`fcb8a0f6bbb0deddb93565cf258f85a4b05d5f701e2619311ce4544f2717e7cc`): `baseline_id`
`baseline-9` and `substrate.substrate_sha256` `8b174cab…`, the sha256 of
`replays/ml_corpus/9p2i/MANIFEST.md`; no kind key; `git diff --stat` on
`training/artifacts/impostor/map-elites/` shows the one file, two lines, so the 30 cell genomes
and `filled_cells` are untouched. No ES byte moved; the runner-up stamp naming the anchor, the
coevo tree, the campaign rows and the other genomes are untouched.

**Pins moved with this commit** (the rest wait for the tests commit):
- `test_bakeoff_harness.py::test_selection_bar_pins_the_baseline_8_floors` → renamed as above.
  FROZEN: `"baseline-8"` → `"baseline-9"`, `147 / 151` → `107 / 145` (the constants this
  record moves); extended to the two further defaults.
- `test_anchor_study.py::test_committed_study_artifacts_are_the_baseline8_fit` → renamed
  `test_committed_study_artifacts_are_the_baseline9_fit`. FROZEN: `baseline_id`
  `"baseline-8"` → `"baseline-9"`; extended with `_historical_stamp_violations`, applied to
  the index and every entrant config (historical sha, no kind or scope key). Its planted half is
  the new `test_the_writers_own_config_fails_the_historical_stamp_predicate`: a fit-only
  `run_anchor_study` on seed 1000 writes the version-two kind, which the predicate refuses
  (kind present and sha not historical), while the committed filtered-BC config passes.
- `test_bakeoff_methods.py::test_the_committed_map_elites_pool_is_historical_and_structurally_untouched`:
  FROZEN `"baseline-8"` → `"baseline-9"`; the champion `(5, 0, 3)` at 18.8641 and the 30 cells
  still hold unchanged.
- `test_goodhart_probe.py::test_probe_reruns_end_to_end_on_the_regrounded_surrogate`:
  MEASURED `report.baseline_id` `"baseline-8"` → `"baseline-9"`, the moved default read back
  through `run_goodhart_probe`.

`training/reports/report-anchor-study.md` is re-rendered by `training.anchor_study.render_report`
from the new `study.json` (recorded wall-clock arguments 1693 s and 1790 s), with its hand-kept
header command line and §1.1 restored and extended to both re-grounds, the baseline-8 figures
kept as history. Targeted run, [Mac]: `test_anchor_study.py`, `test_bakeoff_methods.py`,
`test_hall_of_fame.py`, `test_bakeoff_harness.py` and `test_goodhart_probe.py` across both tiers
read 206 passed, 1 failed; the one is `test_evaluate_candidate_full_row`, whose frozen conviction
sha moves in the tests commit. `test_committed_lambda_1_artifact_reproduces_the_champion_byte_for_byte`,
the walk-fence tests and `test_founder_ingestion_substrate_mismatch_refused` pass unchanged.

### 5. The Mac Goodhart leg at the constants commit (the R2 comparand; beside, not gating)

At `c740c2337008cdee06a00242ee2ce286681bff13` (the constants commit), [Mac], the Validation
block's leg command verbatim, stdout to a scratch file, run twice (47.5 s and 47.8 s):
```
uv run python -c "from training.bakeoff.es import ESConfig; from training.composed_runner import run_composed_goodhart_leg; c=ESConfig(generations=6, population=6, sigma=0.5, seed=0, fitness_seeds=tuple(range(8)), init_scale=0.5); print(run_composed_goodhart_leg(config=c, evidence_scope='historical').to_json())"
```
Both runs wrote identical bytes. **The R2 comparand:** `to_json()` sha256
**`9b4e358a9ae3cb3b4f252e4d1238fa71994ec5692c50eb194bcaf5ea6f491d5f`** (the printed line
without its trailing newline; the stdout file with it hashes `b0cdb15b…`), `es_digest`
**`00d2c4147613d3ae33062778d3dd1c7d4509fd73c089a60c36f46dbc92c610dd`**, `baseline_id`
`baseline-9` at all three levels. The `es_digest` equals the baseline-8 leg's: the fitness trace
is −1.0 in all seven generations and no improvement is recorded, so the champion stays the
seed-0 initial genome, as the investigation found at `39a568c6`.

Cells, for R2 to compare (the report's §6.1, §6.2 and §6.4 shapes; baseline-8 leg at
`39a568c6` in brackets):
- **§6.1:** HELD; machinery blockers none; findings none; exploits none. Baseline mean score
  3.89 [3.42], ES champion 0.65 [0.65], relative gain −0.8328 [−0.8102]. Lever score gains:
  emergency +0.0064 [+0.1423], report −0.0772 [+0.0474], wait −0.9743 [−0.9708], kill
  −0.0611 [+0.1204], sabotage −0.2122 [−0.1058]. Gate-check buckets empty.

| arm | meetings | predicted supply gain | recorded flags gain | predicted flags/meeting | recorded flags/meeting | predicted converting share | recorded converting share | validity passed |
|---|---|---|---|---|---|---|---|---|
| scripted-FSM baseline | 25 [23] | (anchor) 0.0 | 0.0 | 0.6052 [0.8523] | 0.000 | 0.4400 [0.4783] | 0.000 | False |
| forced-emergency | 39 [39] | +0.1661 [+0.0171] | 0.0 | 0.6635 [0.8399] | 0.000 | 0.3333 [0.3333] | 0.000 | False |
| forced-report | 32 [32] | −0.7009 [−0.5091] | 0.0 | 0.1767 [0.4212] | 0.000 | 0.0312 [0.0312] | 0.000 | False |
| forced-wait | 0 [0] | −1.0000 [−1.0000] | 0.0 | 0.0000 | 0.000 | 0.0000 | 0.000 | False |
| forced-kill | 25 [24] | −0.4303 [−0.3700] | 0.0 | 0.2631 [0.4812] | 0.000 | 0.3200 [0.3750] | 0.000 | False |
| forced-sabotage | 23 [23] | +0.0507 [+0.0326] | 0.0 | 0.6023 [0.8386] | 0.000 | 0.4348 [0.4348] | 0.000 | False |
| ES champion | 28 [28] | −0.2388 [−0.0268] | 0.0 | 0.4463 [0.8057] | 0.000 | 0.0714 [0.0714] | 0.000 | False |

- **§6.4:** 1189 composed meetings [1175]; the shared conviction counter (`3a6fe4ca…`) charged
  1533 = 1189 + 344 of the cap 50 765 [1513 = 1175 + 338 of 49 764]; the surrogate counter
  (`f8901620…`) 1189 of 50 765.

Read against the two committed adoption constraints (`scripts/verify_ml_evidence.py:1812-1815`),
the facts each rests on hold on this leg: every arm's `validity_passed` is False, and every arm
records 0.000 flags per meeting in bytes; no arm reaches the 0.25 materiality bar (the largest
positive predicted-supply delta is the emergency arm's +16.6%). That is a reading for the next
operator, not the composed verdict: the verdict and its constraint set are written from the
agreed leg under the decision rule, after R1 and R2.

**The exact SHA the web session uses for R2: `c740c2337008cdee06a00242ee2ce286681bff13`.**
Every later commit on this branch touches only tests, documents and this card (checked at the
pushed head with `git diff --stat c740c233 HEAD -- ':!tests' ':!docs' ':!tasks' ':!training/README.md' ':!training/reports' ':!replays/ml_corpus/README.md'`,
which must print nothing), so R2 at the pushed head computes the same leg; R2 at `c740c233` is
the like-for-like comparison.

### 6. Tests: the re-pins the local legs can honestly make (acceptance items 3, 8 and 9, local half)

Every value below is re-derived through the production computation the test itself calls
(probes: `$SCR/probe_pins.py`, `$SCR/probe_plants.py`, the tests' own failure output at
`283a87a1`). MEASURED = a live computation re-derived; FROZEN = a committed figure this card
moved (the fit, its verdict, its report or a stamp). Nothing is deleted, skipped, xfailed or
widened; `tests/training/test_model_evidence_provenance.py` is unchanged (`:98-116` still
refuses the version-one records at current scope). Pins moved with the constants commit are
listed under step 4.

**The shared refit comparison and its perturbed cases (acceptance item 3).** The ULP comparison
both `test_committed_artifact_round_trips_and_the_refit_no_longer_matches` pins inlined is now
`tests/training/_refit_equivalence.py::assert_refit_reproduces_committed` (float-hex lists and
scalars at `rel=1e-9, abs=1e-12`, everything else exact, key sets equal); both pins call it.
New cases, default tier:
- `test_surrogate_runner.py::test_a_refit_on_shifted_belief_suspicion_fails_the_refit_pin`:
  `belief_suspicion` +0.125 on every live fit-side row, refit by `fit_corpus_ballot_predictor`,
  must raise `AssertionError` through the helper.
- `test_conviction_model.py::test_a_refit_on_shifted_max_suspicion_fails_the_refit_pin`: the
  `max_suspicion` feature +0.125 on every live fit-side row, refit by
  `ConvictionEconomyModel.fit`, must raise.
Measured [Mac]: the unperturbed refits pass the helper; both perturbed refits raise on the
`mean` key, where the standardization absorbs the constant shift (the weights themselves can
match), which is still the drift the pin exists to catch.

**`tests/training/test_surrogate_runner.py`**
- `test_the_committed_surrogate_is_a_baseline8_fit_on_the_baseline8_corpus` renamed
  `test_the_committed_surrogate_is_a_baseline9_fit_on_the_baseline9_corpus`. FROZEN:
  `fit_side_meetings` 348 → 355; cap 49 764 → 50 765 (re-fit on the live fit side).
- `test_committed_artifact_round_trips_and_the_refit_no_longer_matches` (name kept; the
  `training/README.md` sentence names it): FROZEN cap 49 764 → 50 765; MEASURED live fit side
  348 → 355; the inline comparison → the helper.
- `test_bakeoff_reloads_the_committed_artifact_and_reproduces_the_numbers`: FROZEN (the new
  weights): test views 91 → 94; top-1 47 → 46; predicted skips 89 → 92; correct skips 34 → 42;
  predicted ballots 110 → 84; predicted SKIP ballots 406 → 442; Brier 0.3277976536219233 →
  0.24907908179311566; predicted ejections 2 unchanged.
- `test_no_go_verdict_holds_on_live_served_clamped_features`: FROZEN predicted skips 90 → 92
  (90 was the baseline-8 weights on these bytes); replaced cells 21, top-1 46 and correct skips
  42 unchanged; new count `correct_ejects == 2`, and the axis-3 accuracy now counts the correct
  ejections as well as the correct skips (the comment claiming every decision is SKIP was false:
  2 of 94 eject), which only tightens the `<` against always-eject. Docstring restated: the
  split is now the held-out side of the corpus the weights were fitted on, not out of sample.

**`tests/training/test_conviction_model.py`**
- `test_committed_artifact_round_trips_and_the_refit_no_longer_matches` (name kept): FROZEN cap
  `derive_conviction_max_uses(348) == 49_764` → `(355) == 50_765`; MEASURED live fit rows 348 →
  355; the inline comparison → the helper.
- `test_the_committed_verdict_is_the_baseline8_first_evaluation` renamed
  `test_the_committed_verdict_is_the_baseline9_first_evaluation` (and its entry in
  `tests/training/test_suite_tiers.py::_MIXED_TIER_ALWAYS_ON_TESTS`). FROZEN: test meetings
  91 → 94; ejections 57 → 52; conversions 51 → 44; Spearman 0.667006270925879 →
  0.8394835297890146; recall 49/51 → 42/44; voice-driven share 0.17543859649122806 →
  0.21153846153846156; conversion bar 0.618421052631579 → 0.5913461538461539; ceiling
  0.8245614035087719 → 0.7884615384615384; accuracy 0.945054945054945 → 0.925531914893617;
  trivial baseline 0.5604395604395604 → 0.5319148936170213; confusion (49, 3, 2, 37) →
  (42, 5, 2, 45). GO and the consequence mapping unchanged.
- `test_axis_three_is_a_floor_the_live_model_clears_on_all_three`: no value moved (the re-fit
  reads the same confusion the frozen baseline-8 weights read); docstring restated from "fully
  out of sample" to the held-out split of the fitted corpus.

**Other readers**
- `tests/training/test_bakeoff_harness.py::_COMMITTED_CONVICTION_SHA256` (read by
  `test_evaluate_candidate_full_row`): FROZEN `7e764b89…` → `3a6fe4ca…`.
- `tests/training/test_crew_scorer.py::test_evaluate_crew_candidate_full_row` (campaign):
  FROZEN conviction sha `7e764b89…` → `3a6fe4ca…`.
- `tests/training/test_composed_runner.py::test_composed_fidelity_scores_the_committed_test_split`
  (campaign): MEASURED surrogate tally ejections 4 → 2 and skips 90 → 92 (the old values were
  the baseline-8 weights on these bytes); 94/52, top-1 46/52 and ceiling 41/52 unchanged;
  comment restated.
- `test_composed_runner.py::test_go_verdict_holds_under_the_live_teammate_exclusion_ranking`
  (campaign): MEASURED live-exclusion tally ejections 2 → 1; (79, 52), 46 and 78 unchanged;
  GO holds; docstring gains the in-sample sentence.
- `test_composed_runner.py::test_composed_fidelity_top1_matches_an_independent_recompute`:
  unchanged and green.
- `tests/scripts/test_verify_ml_evidence.py::test_a_report_value_contradicting_its_fraction_raises`:
  FROZEN report fractions (86, 91) → (87, 94) and (47, 57) → (46, 52), with their planted
  strings `86/91 = 0.9451` → `87/94 = 0.9255` and `**82.5%** (47/57)` → `**88.5%** (46/52)`
  (it went red at `283a87a1` because the refreshed reports no longer carry the old cells).
- **The grounding plant (acceptance item 8).**
  `test_an_undeclared_corpus_still_fails_the_grounding_row` is parametrized, not copied:
  `added-recording` (the existing plant), `surrogate-record-back-to-b8` and
  `conviction-record-back-to-b8`, each writing `cc54d3c0…` back into a temporary copy of one
  `fit-corpus.json` still keyed to the new weights. Each case asserts its unperturbed control OK
  first, then FAIL with "undeclared substrate", names exactly the drifted instrument(s) ("the fit
  was made on cc54d3c02a9804d3…" for the planted one), and reads OK again once restored.
  4 passed [Mac].

**Turned green by the re-fit, the re-stamps or the constants alone** (no edit): the surrogate
fence group (`test_runner_satisfies_meeting_runner_protocol`,
`test_surrogate_game_is_byte_deterministic`, `test_fit_corpus_fence_fails_loud_on_substrate_and_key_drift`,
the install-gate, fallback, factory, cap, missing-artifact and impostor-ballot tests and the two
setup errors); `test_goodhart_probe.py`'s eight conviction-fence tests plus the one re-pinned in
step 4; `test_bakeoff_harness.py`'s three other `evaluate_candidate` tests and
`test_goodhart_surrogate_rerun_ci_budget`; `test_model_evidence_provenance.py::test_historical_diagnostic_restores_committed_models`;
`tests/eval/test_balance_eval_meeting_runner.py` and
`tests/experiments/test_torch_probe_excluded.py`; five `test_verify_ml_evidence.py` controls
(perturbed weight hash, other weights, relabelled version, perturbed replay, the undeclared
corpus); in the campaign tier the crew, owned-tasks, coevo and anchor-study fence tests and 14
of the 16 composed fence tests, `test_hall_of_fame.py::test_committed_pool_restores_only_with_explicit_historical_identity`,
and the study and pool pins moved in step 4.

**Left for the next operator (done in §10-§11): they read `training/artifacts/composed/`**, which the composed
step rewrites from the agreed leg (the composed verdict and manifest still name
`7e764b89…`/`06b20508…`):
- default tier: `tests/scripts/test_verify_ml_evidence.py::test_recompute_reads_every_committed_verdict_against_the_live_corpus`
  (its five composed rows plus the two weight-hash rows, which read the composed manifest);
  `tests/scripts/test_verify_ml_evidence.py::test_the_corpus_dependent_partition_is_declared_and_is_not_the_whole_leg`,
  green on `main` and red here for the same reason: it requires the two weight-hash rows OK;
- campaign tier: `test_composed_runner.py::test_committed_composed_verdict_is_rederivable`,
  `::test_committed_composed_verdict_round_trips_and_pins_the_shas`,
  `::test_factory_adoption_gate_refuses_non_go_composed_verdicts` and
  `::test_historical_composed_weights_cannot_be_installed[historical]` (each meets "the verdict and
  the artifacts drifted apart" before the refusal it tests); the second of the four is green on
  `main` and red here, the other three were red on `main` too.

### 7. Documents that do not depend on the Linux leg (acceptance items 11 and 12, local half)

- `training/README.md:48-49` ("A future fit must write …") is replaced by the card's sentence
  verbatim, the rest of the paragraph kept. It names the two refit pins by their unchanged ids
  and `test_verify_ml_evidence.py::test_recompute_reads_every_committed_verdict_against_the_live_corpus`;
  the first two are green at this head, the third waits for the composed step (step 6). This
  dated ruling overrides the sentence's earlier plain reading; the documents did not already
  agree.
- The two `historical_*` docstrings changed in the constants commit (step 4), comment-only.
- `docs/ml-program.md`'s disposition paragraph re-derives the surrogate's counts from its new
  `verdict.json`: 47 of 57 → 46 of 52 ranked first, 36 of 91 → 44 of 94 decisions, always eject
  57 of 91 → 52 of 94. `uv run python scripts/check_doc_facts.py` passes [Mac] (arms recompute,
  budgets hold).
- The reports: surrogate (step 2), conviction (step 3) and anchor study (step 4) refreshed in
  the commits that moved their artifacts; their new prose carries no task or audit id and
  phrases the version-one identity plainly ("replay, split and manifest bytes"), so
  `docs/glossary.md` gains nothing.

Left for the next operator (done in §10 and §12), because each states the composed verdict or the verifier's final
exit status: `docs/ml-program.md:170-192` (the "What the instruments now stand on" paragraph
and table, which still name `cc54d3c0…` and `--complete`), `training/reports/report-composed-runner.md`,
the `replays/ml_corpus/README.md:29-45` blockquote (which still says the fits are baseline-8
and `BAKEOFF_BASELINE_ID` reads `baseline-8`, both false since steps 2-4), and
`docs/artifacts.md` rows `:103`-`:104`, recomputed last after merging `main`.

### 8. The local gates, and where the local legs stop

**Red set at `94a2b9ed` against `main`** ([Mac], `uv run pytest -p no:cacheprovider -n auto --dist loadfile -q -rfE`,
the host shared with other sessions at a load average of 40-60, so wall times are upper bounds):
- `main` (`ff4c6bb8`): 41 failed + 9 errors, 50 ids (8246 passed, 502 s): the 41 ML ids and the
  nine under **Done**.
- This head: 11 failed, 0 errors (8289 passed, 867 s): the nine under **Done** plus
  `test_verify_ml_evidence.py::test_recompute_reads_every_committed_verdict_against_the_live_corpus`
  (on `main`'s list) and `::test_the_corpus_dependent_partition_is_declared_and_is_not_the_whole_leg`
  (green on `main`). Both read `training/artifacts/composed/`, which the composed step rewrites.
  40 of `main`'s 41 ML ids are green here.
- The campaign tier, [Mac], with every re-pin in place: 336 collected (335 at `39a568c6` plus
  the study pin's planted case); the four composed-artifact tests listed in step 6 are red and
  the rest pass (the composed-fidelity and crew re-pins re-run green after the full run, which read
  7 failed / 329 passed in 1140 s under the load above, past the 10 min budget: §14). The Actions
  run is below.
- Static gates at this head, [Mac]: `ruff check .`, `ruff format --check .`, `lint-imports`
  (4 kept), `validate_task_docs.py`, `generate_prompts.py --check` and `mypy .` (494 files)
  all pass; `check_doc_facts.py` passes. The frontend legs were not run here; no frontend file
  changed, and the PR's `frontend-checks` job runs them.
- Freeze, against the merge base `ff4c6bb8`: `git diff --stat ff4c6bb8 HEAD -- engine agents meetings observation orchestrator`
  and `-- replays docs/process-scorecard.md` print nothing, and no path under `eval/` changed;
  no utility-es, policy-es, bc-dagger, crew, coevo or runner-up byte and no `results-*.jsonl`
  row moved.

**Status of the acceptance items at this head** (`94a2b9ed`; superseded by §13; numbered in the order Acceptance lists them).
Ticked where the evidence is whole: items 2, 3, 4, 5 and 10 (the readings). Open:
- item 1 needs R1;
- items 6 and 7 need the composed verdict from R2;
- item 8 (verifier FAIL 0) reads, offline at this head, OK for grounding and the surrogate and
  conviction rows, and FAIL on the seven rows that read the composed artifacts;
- item 9 (all 68 green): 64 of the 68 are green, the other four read the composed artifacts,
  and two more that are green on `main` are red here for the same reason;
- item 11 (the keying rule) is written, sentence and docstrings, and its two refit pins and
  their perturbed cases are green; the third test the sentence names is one of the two
  composed-artifact reds, so the box waits for the composed step;
- item 12 needs the documents under "Left for the next operator";
- items 13 and 14 need the Actions runs.

**Left for the next operator, once the web session's `claude/<slug>` branch exists** (done in §9-§13).
1. Read the hand-back by SHA and apply the decision rule: R1 at `39a568c6` against the
   §6.1/§6.2 cells and both constraint strings; R2 at **`c740c2337008cdee06a00242ee2ce286681bff13`**
   against this Mac's `to_json()` sha256 `9b4e358a9ae3cb3b4f252e4d1238fa71994ec5692c50eb194bcaf5ea6f491d5f`
   and `es_digest` `00d2c4147613d3ae33062778d3dd1c7d4509fd73c089a60c36f46dbc92c610dd` (step 5).
2. The composed step: `run_composed_fidelity` → `decide_composed_go(..., adoption_constraints=<the agreed leg's>)`
   → `write_composed_manifest_artifact` and `write_composed_verdict_artifact`; any change to
   the constraint set moves `scripts/verify_ml_evidence.py:1812-1815` and is named first in the PR.
3. The six composed-artifact tests (step 6), the verifier's seven composed rows, and the
   composed report.
4. `docs/ml-program.md:170-192`, the `replays/ml_corpus/README.md:29-45` blockquote, then after
   merging `main`, `docs/artifacts.md` rows `:103`-`:104`, last.
5. The gates: the PR's CI and the Actions campaign run below (or its re-run at the final head).

**The campaign tier on GitHub Actions `ubuntu-latest`** (`gh workflow run campaign-tier.yml --ref work/ml-reground-baseline-9`,
dispatched at the pushed head `692233e3`): run **35869361782** reads **4 failed, 332 passed**
(336 collected) in 427.69 s, and the four are exactly the composed-artifact tests listed in
step 6 (`test_factory_adoption_gate_refuses_non_go_composed_verdicts`,
`test_historical_composed_weights_cannot_be_installed[historical]`,
`test_committed_composed_verdict_round_trips_and_pins_the_shas`,
`test_committed_composed_verdict_is_rederivable`). Against `39a568c6`'s 335 passed, the one
extra id is the study pin's planted case. The Mac beside: the full run read 7 failed / 329
passed before the three campaign re-pins of step 6, which then passed on their own; the same
four remain. The PR's CI (run 35869352089) was still running when these local legs stopped.

**The deferred cost of the version-one choice** (Constraints, **Deferred cost**). The first
current install of either fit mints version two at its own commit, and inherits:
- the identity row (`scripts/verify_ml_evidence.py:1716-1781`) and the grounding row
  (`:1966-2061`) switching to `fit_corpus_fingerprint`;
- the inversions of `test_historical_verifier_refuses_relabeled_fit_version`,
  `test_current_loader_refuses_historical_fit` (onto a planted version-one copy), the pool
  ingest and the anchor pin's scope check;
- the function switches at `test_surrogate_runner.py:553`, `:599` and
  `test_composed_runner.py:966`;
- the closure churn: `PYTHONPATH=. uv run python $SCR/churn.py ff4c6bb8` (the bound set is
  `derivation_files()` plus the map, `pyproject.toml` and `uv.lock`, 112 files; first-parent
  merges since 2026-09-06 diffed against their first parent) reads **15 of 39** merges
  touching it.

Which code closure version two binds, for the fits and for each stamp, is the owner's before
that install.

**Decisions, recorded.**
- Tests that the constants commit itself moved (the selection bar, the study pin with its
  planted case, the pool pin, the Goodhart probe's baseline literal) landed in that commit so
  it is verified on its own; the rest landed in the tests commit.
- The composed manifest is left to the composed step with the verdict, as the card orders,
  although it does not read the leg; the two tests green on `main` and red here are the price,
  named above.
- R2's SHA is the constants commit rather than the pushed head, so it is the commit the Mac
  leg ran on; the post-constants diff check in step 5 shows the pushed head computes the same leg.
- No verdict flipped and no constraint set changed in the local legs; Q4 did not fire.

### 9. The hand-back from the web session, and the decision rule (acceptance items 1 and 6)

The web session committed its hand-back to `claude/ml-reground-baseline-9-kjw7yb` as
**`04d81a3dabf1e2c3a8c2936bb0a5cfe4579f70c5`** (parent `c740c233`): three files under
`handback/ml-reground-baseline-9/`. They were read by commit SHA and nothing else
(`git fetch origin claude/ml-reground-baseline-9-kjw7yb`, then
`git show 04d81a3dabf1e2c3a8c2936bb0a5cfe4579f70c5:handback/ml-reground-baseline-9/<file> > $SCR/handback/<file>`
and `shasum -a 256 $SCR/handback/*`); that branch was never checked out, merged or deleted,
and no JSON from it is pasted here.

| file | sha256, recomputed here | the proof's value | match |
|---|---|---|---|
| `proof.json` | `ea7962f9a33e85d3864b4930a03dc80f7b32aef9922e5a124cc235318508fba6` | none (a file cannot carry its own digest; it is cited by this one) | n/a |
| `r1-leg-39a568c6.json` | `bddf96d5d0176505bfb7b6bc4d85eeab7da132641089f7d2b3fafa1fd44a1ffe` | `runs.R1.leg_json_sha256` the same | yes |
| `r2-leg-c740c233.json` | `9b4e358a9ae3cb3b4f252e4d1238fa71994ec5692c50eb194bcaf5ea6f491d5f` | `runs.R2.leg_json_sha256` the same | yes |

Each leg file is `to_json()`'s text byte for byte (no trailing newline), so its file sha256
is the leg digest §1 and §5 compare; the proof records the stdout-with-newline digests too
(`de9d8f1a…`, `b0cdb15b…`), equal to this Mac's.

**The Linux host stamp** (`proof.json` `host_stamp`, identical at R1 and R2), short form
**[Linux]**:

| field | value |
|---|---|
| `uname -srm` | `Linux 6.18.44-fc-v37 x86_64` |
| `platform.platform()` | `Linux-6.18.44-fc-v37-x86_64-with-glibc2.39` |
| `sys.version` | `3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]` |
| numpy | `2.2.6`; SIMD baseline `SSE, SSE2, SSE3`, found `SSSE3` … `AVX512_ICL` (14), not found `AVX512_KNL`, `AVX512_KNM`; no BLAS block (`threadpoolctl` is not in the locked environment) |
| CPU | `Intel(R) Xeon(R) Processor @ 2.10GHz` (`/proc/cpuinfo`) |
| shell | `env -i HOME=$HOME PATH=$PATH bash --noprofile --norc`: no `AILIBI_*`, no provider key, no `.env`; `uv 0.8.17`, `uv sync --frozen` at each checkout (`uv.lock` sha256 `c79ba472…` at both) |

**The proof's commands**, checked here: R1 `git fetch origin`, `git checkout --detach
39a568c6`, `uv sync --frozen`; R2 `git checkout --detach c740c2337008cdee06a00242ee2ce286681bff13`,
`uv sync --frozen`; each then runs the Validation block's leg line, which equals this card's
line character for character. The proof holds 210 comparisons (120 for R1, 90 for R2), each
with a match boolean; recomputed here, every boolean equals `expected == measured`, and all
210 are true (`summary.all_match`, `cells_differed` empty, `reruns` 0). Spend `$0`: no
provider, model call, recorder or held-out generator, no `--complete`.

| leg | host | `to_json()` sha256 | `es_digest` | verdict | `baseline_id` (leg, probe, ES probe) | wall |
|---|---|---|---|---|---|---|
| R1 at `39a568c6` | [Linux] | `bddf96d5…` | `00d2c414…` | HELD | baseline-8, three times | 97.1 s |
| the same leg, §1 | [Mac] | `bddf96d5…` | `00d2c414…` | HELD | baseline-8 | 43.6 s |
| R2 at `c740c233` | [Linux] | `9b4e358a…` | `00d2c414…` | HELD | baseline-9, three times | 95.4 s |
| the same leg, §5 | [Mac] | `9b4e358a…` | `00d2c414…` | HELD | baseline-9, three times | 47.5 s |

R1 was also read here against the committed record, independently of the proof: its §6.1
cells (baseline 3.42, champion 0.65, relative gain −0.8102, lever gains +0.1423, +0.0474,
−0.9708, +0.1204, −0.1058) and all seven §6.2 arms (meetings, predicted and recorded gains,
flags per meeting and converting shares, every `validity_passed` False, the gate buckets
empty) equal `training/reports/report-composed-runner.md` §6.1-§6.2 as committed at
`39a568c6`, and both adoption-constraint strings in the committed `verdict.json` equal
`scripts/verify_ml_evidence.py:1812-1815` in full.

**The decision rule, applied.** R1 reproduces the committed cells on Linux and is
byte-identical to this Mac's run, so the contingency in which the container and the
reproduction rules disagree does not arise. R2 has the identical sha256 on both platforms,
so **the composed verdict is written from that leg and both platforms are named: Linux
x86-64 (Intel Xeon, glibc 2.39) and Darwin 24.6.0 arm64 (Apple M1 Pro)**. The leg reads
`baseline_id` `baseline-9` at all three levels. Acceptance item 1 is complete with R1.

### 10. The composed verdict and manifest (acceptance items 6 and 7)

Written last, at `a105340d` on this Mac ([Mac]; the host stamp re-taken first and identical
to the table at the top), through the writers, with the component digests read from the
sidecars and the adoption constraints carried from the committed verdict after asserting
they equal the verifier's pin:
```
uv run python -c "from pathlib import Path; from training.composed_runner import run_composed_fidelity, decide_composed_go, build_composed_manifest, write_composed_manifest_artifact, write_composed_verdict_artifact, load_composed_verdict; from training.conviction.fidelity import load_conviction_verdict; from scripts.verify_ml_evidence import _COMPOSED_ADOPTION_CONSTRAINTS as K; a=Path('training/artifacts/composed'); ca=Path('training/artifacts/conviction'); k=load_composed_verdict(a).adoption_constraints; assert k == K; r=run_composed_fidelity(Path('replays/ml_corpus/9p2i')); v=decide_composed_go(r, conviction_weights_sha256=(ca/'conviction-model.json.sha256').read_text().split()[0], surrogate_weights_sha256=(Path('training/artifacts/surrogate')/'ballot-predictor.json.sha256').read_text().split()[0], adoption_constraints=k); write_composed_verdict_artifact(v, a); write_composed_manifest_artifact(build_composed_manifest(v, conviction_verdict=load_conviction_verdict(ca)), a); print(v.verdict, v.composed_role, v.meets_decision_bar, v.meets_top1_bar, v.decision_accuracy, v.decision_accuracy_bar, v.convicting_top1, v.top1_bar, v.top1_ceiling, v.exact_outcome_match)"
```
printed `GO optional-campaign-configuration True True 0.8404255319148937 0.5531914893617021
0.8846153846153846 0.5913461538461539 0.7884615384615384 0.8297872340425532` (10.1 s):
**no flip**, the verdict baseline 8 published.

| composed axis (94 held-out meetings, 52 ejections) | baseline 9 | bar | baseline 8 (history) |
|---|---|---|---|
| 1. decision accuracy > always-eject | 79/94 = 0.8404 PASS | 0.5532 | 82/91 = 0.9011 PASS |
| 2. convicting top-1 ≥ 0.75 × ceiling | 46/52 = 0.8846 PASS | 0.5913 (ceiling 41/52) | 47/57 = 0.8246 PASS |
| exact outcome (informational) | 78/94 = 0.8298 | none | 76/91 = 0.8352 |

Beside them: 47 gate convictions of 94, confusion 42/5/10/37 (8 of the 10 missed ejections
carried no testimony-backed conversion), 41/42 among gate-convicted ejections, surrogate
tally 2 ejections / 92 skips. Digests [Mac]: `verdict.json`
`a2071c127fbdec300cef59ca0020eae5e402900456d108a2795cfb9e01503121` (its sidecar names it),
`manifest.json` `feb04d83c34358325e8582b9e18829aed78e52b3d7af2ee11b9a396d1e81794e`, keyed to
conviction `3a6fe4ca…` and surrogate `f8901620…`. The frozen baseline-8 components already
read these three cells on these bytes (Evidence: 0.8404, 0.8298, 0.8846); the re-fit moved
none of them.

**The adoption-constraint set is unchanged, so Q4 does not fire.** The leg emits no
constraint strings; the committed two ride with the verdict, and the facts each rests on hold
on R2: every arm's `validity_passed` is False, and every arm records 0.000 flags per meeting
in bytes. Neither retired shape returns: `prescreen_floors_pass` is False on all seven arms,
and the largest predicted-supply delta is the emergency arm's +0.1661 against the 0.25 bar.
The name of constraint 1's failing check comes from the validity-gate diagnosis, re-run here
on the re-fit components (the report's §9 fourth line, 1.6 s [Mac]): eight games, 25
resolved meetings, 11 ejections, 32 kills, 0 betrayal ballots over 143 multi-impostor
ballots, 5 crew and 3 impostor wins, and only `cost_and_provenance_exact` fails.
`scripts/verify_ml_evidence.py` is not edited.

**Proof for item 6** (`$SCR/plant_constraint.py`, run as `PYTHONPATH=.:scripts uv run python
$SCR/plant_constraint.py`): it builds a temporary copy with the verifier test module's own
`_manifests`, `_link` and `_copy` helpers, the composed `verdict.json` copied and everything
else linked. Control: the `composed adoption constraints` row and the `composed verdict.json
reproduces` row read OK, `_failed` empty. One character changed in constraint 0
(`diagnostic-grade` → `diagnostic-grads`, same length): the constraints row reads **FAIL**,
naming index 0 with both full strings, while the identity row still reads OK because the
constraints are spliced from the committed side; the full-string pin alone catches it.

**Item 7.** `git diff ff4c6bb8 HEAD -- training/surrogate/fidelity.py training/conviction/fidelity.py`
is empty; no bar, ceiling or comparator moved. No verdict flipped: surrogate NO-GO (ranking
GO, decision NO-GO), conviction GO, composed GO, each as at baseline 8, so nothing downstream
is re-pointed. The identity row's drift classes stay red: the committed plants
`test_a_perturbed_weight_hash_fails_and_is_named_corpus_independent` (the manifest row names
`[corpus-independent]`), `test_a_corpus_path_field_is_compared_not_dropped` and
`test_a_drifted_composed_manifest_field_is_compared` pass, each red on its plant; and, since
no committed test plants a corpus-derived field into a verdict, `$SCR/plant_identity.py`
(same temporary-copy build) does so on the new composed verdict: `decision_accuracy` set to
0.5 reads **FAIL**, "16/17 fields identical (1 corpus-derived)", and
`surrogate_weights_sha256` set to 64 `b`s reads **FAIL**, "(1 corpus-independent)", each
control OK first.

### 11. The composed-dependent re-pins (acceptance items 8, 9 and 11)

Each value re-derived through the computation the test calls; the frozen side moves here
because this is the adopting record for the fits.
- `tests/scripts/test_verify_ml_evidence.py::test_recompute_reads_every_committed_verdict_against_the_live_corpus`:
  six measured/committed pairs, pinned together so neither drifts alone. MEASURED (the live
  recompute) and FROZEN (the committed report or verdict figure) move as one, old → new:
  surrogate top-1 0.8245614 → 0.8846153; SKIP-vs-eject 0.3956043 → 0.4680851; conviction
  Spearman 0.6670062 → 0.8394835; conversion accuracy 0.9450549 → 0.9255319; composed
  decision accuracy 0.9010989 → 0.8404255; composed exact outcome 0.8351648 → 0.8297872.
  The per-line baseline-6 "was" comments give way to one comment listing the baseline-8
  values. Its row-status, grounding and field-identity assertions are unchanged.
- `tests/training/test_composed_runner.py::test_committed_composed_verdict_is_rederivable`
  (campaign): the rederivation half (MEASURED, `decide_composed_go(run_composed_fidelity(...))`
  field for field) is unchanged; the committed first-evaluation numbers, FROZEN: test meetings
  91 → 94; ejections 57 → 52; decision accuracy 82/91 → 79/94; its bar 57/91 → 52/94;
  convicting top-1 47/57 → 46/52; top-1 bar 0.75 × 47/57 → 0.75 × 41/52; ceiling 47/57 →
  41/52; exact outcome 76/91 → 78/94. GO, the role and both constraint names unchanged.
- `test_composed_runner.py::test_go_verdict_holds_under_the_live_teammate_exclusion_ranking`:
  docstring only, "the committed 0.7667" (a baseline-6 figure the last re-ground left) →
  "the committed 0.8846"; its cells were re-pinned in step 6.
- Green by the artifacts alone, no edit:
  `test_verify_ml_evidence.py::test_the_corpus_dependent_partition_is_declared_and_is_not_the_whole_leg`
  (default tier), and in the campaign tier
  `test_composed_runner.py::test_committed_composed_verdict_round_trips_and_pins_the_shas`,
  `::test_factory_adoption_gate_refuses_non_go_composed_verdicts` and
  `::test_historical_composed_weights_cannot_be_installed[historical]`.

Targeted, [Mac]: `tests/scripts/test_verify_ml_evidence.py` 82 passed (the grounding plant's
three ids and every planted control among them); `tests/training/test_composed_runner.py -m
campaign` 28 passed. **The verifier, offline** (`uv run python scripts/verify_ml_evidence.py`,
never `--complete`), at `e58c43d3`: exit 0, 61 checks, **OK 49, FAIL 0**, ABSENT 7 (the
evidence-branch and archive-only rows), INFO 5. The identity and grounding rows name
`6536c68c…` for both fitted records, keyed to `f8901620…` and `3a6fe4ca…`; the twelve rows
that failed at dispatch read OK, and the two weight-hash rows read the new composed manifest.
The planted stale record still fails: `test_an_undeclared_corpus_still_fails_the_grounding_row[surrogate-record-back-to-b8]`
and `[conviction-record-back-to-b8]` write `cc54d3c0…` back beside the new weights and read
FAIL with "undeclared substrate". The third test the `training/README.md` sentence names is
green, so item 11 is complete.

### 12. The remaining documents (acceptance item 12)

- `training/reports/report-composed-runner.md`, in the composed commit: header, §1-§8 and §10
  re-derived from its §9 commands and the R2 JSON, each new digest beside the host stamps of
  both platforms, the baseline-8 figures kept as a new erratum and a history block after §6.2,
  and a §6.3 erratum recording that the constraint set is unchanged and why. §4 gains note
  (e), the ceiling reading below. §9's leg line gains `evidence_scope='historical'` (the
  report's old line defaults to current scope, which refuses version-one components) and a
  fourth line, the validity diagnosis behind §5 and §6.3; its pytest line gains `-m
  campaign`, without which the file collects nothing.
- `docs/ml-program.md` "What the instruments now stand on": the corpus the 2026-09-22
  re-recording left, historical fingerprint `6536c68c…`, which covers the replay, split and
  manifest bytes but not the roster or the fitting code; every row re-derives under the
  offline verifier (the `--complete` claim is gone); no verdict changed. 2,128 words against
  the 2,150 ceiling (22 under); the policy paragraphs are word for word; the table's three
  verdicts are unchanged.
- `replays/ml_corpus/README.md` blockquote: it said the fits were baseline-8 and
  `BAKEOFF_BASELINE_ID` read `baseline-8`; it now states what the re-ground did, that the
  verifier exits 0 with the grounding row naming the corpus on disk, and that the recorded
  bake-off and campaign rows were not re-run. The corpus MANIFESTs keep their FROZEN line.
- `docs/artifacts.md`, recomputed with the change staged (`git ls-files <dirs>`, sizes summed
  from the files): row `:103` 105 files, 897,988 bytes, **1.5 MB → 877 KB** (the 1.5 MB was
  never supported by a committed state: 899,439 bytes when the row was written); row `:104`
  15 files, 8,295 bytes, 8.1 KB, unchanged. Recomputed before the merge because `main` changes
  no file under `training/artifacts/`; re-checked after it (§13).
- New prose carries no task or audit id and no threshold arithmetic; the version-one identity
  is phrased as "the replay, split and manifest bytes", so `docs/glossary.md` gains nothing.
  `check_doc_facts.py` passes; `tests/scripts/test_check_doc_facts.py` passes whole, its ML
  page perturbations red on their plants.

**The two readings, as measured on the re-ground fits** (neither docstring edited; both
rulings stay the owner's). Re-run at `cb0e9f3e`, [Mac], with the §2 commands quoted whole:
- *The ceiling.* The census reads (hit, reachable) 40, (hit, not reachable) 6, (miss,
  reachable) 1, (miss, not reachable) 5: 52 cells, 46 hits, the verdict's top-1. The composed
  top-1 is the surrogate's ranking channel, so the composed verdict reads the same 46 of 52
  against the same 41 of 52 ceiling. The six hits the ceiling counts unreachable are ties at
  the top of the best-case evidence (§2), so for a ranker that breaks ties the ceiling is not
  a maximum. The bar passes either way.
- *The tie-break.* On the corpus test side the shipped highest-tau head reads 0.4468 against
  the lowest tied tau's 0.4362 (0 ejections and 52 skips against 5 and 50); on the other
  three sets the two heads score the same, as in §2; ranking and calibration are identical
  on all four. FO-6 is re-fit
  fresh on the table, so the re-fit cannot move the reversal: it belongs to the bytes.

**Rulings relied on, quoted verbatim (owner, 2026-09-23).** Q1: "Look into how it should
best be fitted and implement your recommended strategy." (version one). Q2: "Go with your
recommendation." (the campaign tier in scope as tests; nothing re-searched or re-run). Q3:
"The previous Linux environment used was a Claude code session dispatched to the web." (the
leg's gate is that session's R1 and R2). Q4: "Publish and wait for the merge." (no verdict
flipped and no constraint set changed, so nothing is named as a flip; the pull request still
waits for the owner's merge). Q5: "Look into why the tests would still fail, if they are
necessary at all, or a separate potential path forward. Go with the recommended idea from
that." (done means the failing ids are a subset of the nine cards B and C owned).

**Named deviation, for the owner's ruling.** GitHub Actions `ubuntu-latest` gates the
campaign tier and `check.sh` as a second container instance; Q3 named the web session, which
ran only the leg. **Routed, not done here:** the first current install of either fit mints
version two at its own commit and inherits the verifier rows, test inversions, function
switches and closure churn listed in §8 ("The deferred cost"); which code closure version
two binds is the owner's before that install. Also routed: a campaign-tier refit pin for the
filtered-BC anchor.

**Architecture.** `docs/architecture.md` "Determinism and the substrate ladder": the leg is
a deterministic replay of fixed seeds through frozen weights, and it printed the same bytes
on two platforms; the constants move bake-off selection to baseline 9's rung, and no
recorded byte moved. "Current model evidence": both fitted records stay version one and
restore only under explicit historical diagnostics
(`test_model_evidence_provenance.py:98-116` unchanged); nothing is promoted to current.

### 13. `main` merged, and the gates on the merged branch (acceptance items 9, 12, 13 and 14)

**The merge.** `git merge origin/main` at `efadfe06` (cards B and C and their status flips),
never a rebase: merge commit `c586bf697fac77ae1f9c55af43e7ec8b4722942d`, no conflict. `main`
changed `docs/artifacts.md` row `:109` only among the files this card writes. Freeze, from the
new merge base: `git diff --stat $(git merge-base origin/main HEAD) HEAD -- engine agents
meetings observation orchestrator` and the same for `eval/` print nothing; `-- replays
docs/process-scorecard.md tasks/README.md` prints `replays/ml_corpus/README.md` alone. No
utility-es, policy-es, bc-dagger, crew, coevo or runner-up byte and no `results-*.jsonl` row
moved since `ff4c6bb8`. Rows `:103` and `:104` re-counted at the merged head: 105 files /
897,988 bytes and 15 files / 8,295 bytes, as recomputed before the merge.

**The gates at `c586bf69`** (exit codes captured directly; [Mac] unless named):

| gate | result |
|---|---|
| `bash scripts/check.sh`, whole, this worktree | **exit 0** (03:58-04:08 UTC): ruff and format (523 files), `lint-imports` 4 kept, task docs, prompts, `mypy` 494 files; pytest **8307 passed**, 20 skipped, 3 xfailed, 0 failed, 0 errors (575.6 s); frontend lint, `tsc`, vitest 558 passed in 20 files, build |
| `bash scripts/verify_samples.sh` | exit 0, both canonical sets clean |
| `scripts/build_sample_report.py --sample-dir <set> --check`, four sets | exit 0 each (`samples/4p1i`, `samples/9p2i`, `ml_corpus/4p1i`, `ml_corpus/9p2i`) |
| `scripts/publish_process_scorecard.py --check` | exit 0 |
| `check_doc_facts.py`, `validate_task_docs.py`, `generate_prompts.py --check` | exit 0 each |
| `scripts/verify_ml_evidence.py`, offline | exit 0; 61 checks, **OK 49, FAIL 0**, ABSENT 7, INFO 5 |
| `npm --prefix frontend test` | exit 0, 558 passed in 20 files |
| campaign tier, GitHub Actions `ubuntu-latest` | run **35953659978** (`workflow_dispatch` at `c586bf69`): **336 passed, 0 failed**, 408.34 s |
| campaign tier, this Mac, beside | 336 passed, 0 failed, 113.8 s |
| the PR's CI at `c586bf69` (run 35953658169, `ubuntu-latest`) | `project-checks` **pass** (pytest 8292 passed, 35 skipped, 3 xfailed, 0 failed, 979.8 s; 8330 collected, as on the Mac, with 15 more platform skips), `frontend-checks` pass, Playwright e2e pass |

**Item 13.** 336 against `39a568c6`'s 335: the one extra id is
`tests/training/test_anchor_study.py::test_the_writers_own_config_fails_the_historical_stamp_predicate`,
the study pin's planted case this card added in the campaign tier; the renamed pins replace
their old ids one for one, and the merge from `main` moved no campaign count (336 before it
too). At the re-record's close the tier read 308 passed, 25 failed, 2 errors; at this card's
local stop, 332 passed and 4 failed.

**Item 14 and the red set.** The default tier reads 0 failed and 0 errors, so the red set at
this head is **empty**: the 41 ML ids `main` carried are green, the two that were green on
`main` and red on this branch are green again, and the nine ids cards B and C owned were
re-pinned or renamed by those cards (merged in `efadfe06`) and are green here. Item 9: all 68
are green, the 41 default-tier ids in the pytest run above and the 27 campaign-tier ids in
run 35953659978, no assertion deleted, skipped, xfailed or widened, and
`test_model_evidence_provenance.py:98-116` unchanged.

**Item 12.** The four reports refreshed in the commits that moved their artifacts; the ML
page, the corpus README and rows `:103`-`:104` in `cb0e9f3e`, re-checked after the merge;
`check_doc_facts.py`, the registry-row test and the verifier's inventory row pass.

**The composed digests, each beside its host stamp**, collected: `verdict.json`
`a2071c12…` and `manifest.json` `feb04d83…` [Mac], from the leg whose JSON reads `9b4e358a…`
on [Linux] and [Mac] alike.

### 14. Wall time against the budget, and the stop rule (Constraints, **Wall budget and stop rule**)

Each step's measured wall set against its budget. The seconds are the timed commands quoted in
§1-§13, the web session's `proof.json` (`runs.R1.wall_seconds` 97.08, `runs.R2.wall_seconds`
95.4), the operator's run log for step 6's re-run of the re-pinned tests (503 s) and the
Actions job times (`gh run view <id> --json jobs`); where a step also ran untimed lines, the
bound beside it is the commit-timestamp bound the budget row itself uses for 21.17
(`git log --first-parent --format='%h %cI' ff4c6bb8..HEAD`, times UTC-4 on this Mac).

| step | budget | measured | reading |
|---|---|---|---|
| reproduction at `39a568c6` (§1) | 60 min | 86.0 s: fingerprint 1.4, verifier subset 21.9, three refits 3.5 + 11.0 + 4.2, pool stamp 0.4, Mac leg 43.6 [Mac] | inside |
| surrogate, conviction, composed fidelity, Mac leg (§2, §3, §5, §10) | 55 min | 131.2 s timed: surrogate weights 3.6 and verdict 3.6; conviction weights 11.4 and verdict 5.6; composed verdict 10.1 and its validity diagnosis 1.6; Mac leg 47.5 and 47.8 [Mac]. The parity walk and the two version-one record lines were not timed; commits bound both fits with their reports at 12 min 55 s (`1127044f` 08:09:18 → `3e346ff3` 08:22:13) and the two Mac-leg runs with their card entry at 2 min 59 s (`c740c233` 08:30:34 → `283a87a1` 08:33:33) | inside |
| walk, anchor, study and pool (§4) | 50 min | anchor re-fit with its 150-game walk 5.3 s [Mac]; the idempotent stamp lines were not timed (the pool line read 0.4 s in §1); commits bound the step, with the constants edit, the planted reverts and the targeted tests, at 8 min 21 s (`3e346ff3` 08:22:13 → `c740c233` 08:30:34) | inside |
| web session: setup, R0 when needed, R1, R2, hand-back (§9) | 60 min | R1 97.1 s and R2 95.4 s [Linux]; R0 not needed; 27 min 36 s from R1's start (`runs.R1.started_utc` 15:49:13Z) to the hand-back commit `04d81a3d` (16:16:49Z). The session's setup before R1 is not in the proof | inside, setup unrecorded |
| campaign tier, this Mac (§8, §13) | 10 min | step 6 development run, with the tests commit's edits in the work tree before its three campaign re-pins: **1140 s (19 min)**, 7 failed / 329 passed, at a load average of 40-60 from other sessions' pytest; the re-pinned tests alone then read green in 503 s under the same load; at the merged head `c586bf69`, 336 passed in 113.8 s | **the step-6 run is past its budget**; the merged-head run is inside |
| campaign tier, GitHub Actions `ubuntu-latest` (§8, §13) | 30 min | run 35869361782 at `692233e3`: 427.69 s of pytest (job 7 min 29 s); run 35953659978 at `c586bf69`: 408.34 s (job 7 min 2 s) | inside; these are the budgeted gating runs |

**The one step past its budget** is the Mac campaign run in step 6: 1140 s against 10 min.
§8 reported its wall time without naming the overrun; this section names it. It was a
development check, not the gating run: the Validation block runs the Mac campaign tier
"beside", and the budgeted gating campaign runs are the two Actions runs, each inside its 30
min. The operator did not stop the card on it, which the stop rule's plain reading asks of a
step past its budget; it is named here for the owner rather than excused. What followed was not
a retry of the same run: step 6's three campaign re-pins were made and only the re-pinned tests
re-run, and the whole tier, re-run at the merged head, read 336 passed in 113.8 s on this Mac,
inside its budget. No other step came near its budget.

**The total.** The measured walls of the budgeted steps sum to about 50 min: 86.0 s + 131.2 s +
5.3 s + 192.5 s on Linux + the three Mac campaign runs (1140 s, 503 s, 113.8 s) + the two
Actions runs (427.69 s, 408.34 s) = 3007.8 s. The gates beside them whose wall is recorded add
about 68 min: the two local default-tier runs (502 s at `ff4c6bb8`, 867 s at `94a2b9ed`, §8),
`check.sh` at `c586bf69` (03:58-04:08 UTC, about 10 min, §13) and the PR's two CI
`project-checks` jobs (18 min 26 s at `692233e3`, 17 min 5 s at `c586bf69`). The targeted
pytest runs and the static gates were not timed; the commits bound the first operator's work
from the reproduction commit to the first Actions entry at 1 h 45 min (`1127044f` 08:09:18 →
`a105340d` 09:54:12), every run in it included. Total compute stays inside 4 h.

### 15. Limitations

What the evidence above does not establish, each item with the sections it qualifies.
- **The fit bytes were produced on this Mac only.** The surrogate (`f8901620…`), conviction
  (`3a6fe4ca…`) and filtered-BC anchor (`6268ea3d…`) weights, and the composed `verdict.json`
  (`a2071c12…`) and `manifest.json` (`feb04d83…`), were written on [Mac] (§2-§4, §10). R0 was
  not needed, so no Linux host re-fit them, and their Linux bytes were never measured. What
  Linux covers: the PR's CI `project-checks` job runs the two refit pins
  (`test_surrogate_runner.py` and `test_conviction_model.py`
  `::test_committed_artifact_round_trips_and_the_refit_no_longer_matches`), which re-fit on
  Linux and compare to the committed weights at `rel=1e-9, abs=1e-12`, not byte for byte, and
  `test_recompute_reads_every_committed_verdict_against_the_live_corpus`, which re-derives the
  three verdicts from the committed weights; the Actions campaign run re-derives the composed
  verdict field for field (`test_committed_composed_verdict_is_rederivable`). So Linux
  agreement for the two fits is agreement within those pins' tolerance, not byte identity, and
  for the verdicts it is inference from this Mac's weights. Only the Goodhart leg was compared
  byte for byte across the two platforms (§9).
- **The filtered-BC anchor has neither a refit pin nor a Linux measurement.** Its reproduction
  at `39a568c6` and its baseline-9 re-fit are [Mac] readings only (§1, §4). The tests check
  its `.sha256` sidecar and its historical stamp, which cover the committed bytes, not their
  derivation, so a change to its recipe would pass them. A campaign-tier refit pin for it is
  routed, not done (§12; the investigation's environment memo §8 and keying memo §7, not in
  the tree, name the same gap).
- **The held-out split is in-sample to the fitted corpus, and the verdicts measure fidelity
  to the record, not correctness.** Each verdict is read on the corpus's own test side
  (`replays/ml_corpus/9p2i/splits.json`: seed mod 5 = 4, 30 of the 150 games; 94 meetings, 52
  ejections). It is disjoint from the fit side by game but comes from the same recording (one
  model, one prompt set, one engine commit), so it is not an independent sample; the held-out
  generator's band stays unseen. The test docstrings that called these reads out of sample
  were restated (§6). The fits predict what the recording's agents did, right or wrong,
  and nothing here measures whether those ballots were correct (Constraints,
  **Role-correctness gates nothing**).
- **The web session's setup wall was not recorded.** `proof.json` times R1, R2 and the
  hand-back commit, not the setup before R1, so that step reads inside its budget with the
  setup unmeasured (§14).
- **The campaign-tier overrun stands as disclosed.** The step-6 Mac campaign run took 1140 s
  against its 10 min budget and the card did not stop on it (§8, §14). The later in-budget
  runs do not change that reading; the ruling on it is the owner's.
- **The bake-off rankings and campaign rows stay on their old corpora.**
  `BAKEOFF_BASELINE_ID` now reads `baseline-9` and the λ, study and pool stamps name the
  baseline-9 substrate, but the λ sweep rows and genomes, the 30 pool genomes, `filled_cells`
  and the champion, the recorded `results-*.jsonl` campaign rows, the coevo tree, the
  `utility-es`, `policy-es` and `bc-dagger` genomes, the crew artifacts and the runner-up
  stamp were not re-searched, re-run or re-scored (Q2; §4, §13). They stay a record of the
  corpora, selection floors and fitness objective they were made under (the anchor report's
  §1.1: the stamps' substrate digest does not cover the objective), and nothing here
  measures how they would rank on baseline 9.
