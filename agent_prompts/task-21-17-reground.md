# Agent Prompt — 21.17 THE ML RE-GROUND: the fits move onto the new corpus, the amnesty dies, the campaign tier is green

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.17 — THE ML RE-GROUND: the fits move onto the new corpus, the amnesty dies, the campaign tier is green, anchored to audits/audit-phase-20-baseline-7.md §10.2 ("The ML re-ground — A NAMED FOLLOW-UP, not a silent debt"), which routes this task verbatim — *"re-fit the surrogate and the conviction model on `replays/ml_corpus/`, re-stamp the fit-corpus fingerprint and the MAP-Elites pool's substrate stamp, move `BAKEOFF_BASELINE_ID`, and re-publish `docs/ml-program.md`'s arms"* — plus the three interim holdings it installed and this task retires (the `STALE` status, the `tests/training/` tripwires, `tests/training/_regrounding.py`); audits/audit-phase-20-close.md §1 F1 (`uv run pytest -m campaign` exits 1 with **9 failed, 308 passed**; the three classes; the routing at :108-113 — *"take the nine campaign-tier pins with it, either re-grounded or converted to tripwires in §10.2's own declared shape"*); audits/review-2026-08-26/B/collated-findings.md B-20 (verifier: the headline is REFUTED — `conversion_bar` IS gated green in the default tier by `tests/training/test_conviction_model.py:860`; the surviving residual is (a) the two verdict-identity rows bundle corpus-dependent and corpus-independent FIELDS so the row-scoped amnesty darkens the latter, (b) neither `verdict.json` has a `.sha256` sidecar, (c) `conversion_ceiling` on the committed conviction verdict has no pin anywhere) and B-46 (verifier: the deletion inventory, and the corrected test enumeration — THREE tests assert `STALE` as the expected answer, `:456` uses it only as a scoping filter and `:500` asserts the OPPOSITE; *"the one thing that must survive deletion is the assertion that a fingerprint MISMATCH fails — that is the whole gate"*); B-11 for the axis-3 disposition this task consumes rather than invents (21.16 pre-registers it), B-16/B-17 for the conviction fit-corpus record and the committed surrogate verdict this task fills (21.8 introduces them), B-47 for the `eval/watchability.py` bake-off-lag note this task's constant move obsoletes — routed HERE at assembly (it was drafted into 21.11) so the note and the constant it describes move in one commit. Anchors re-verified at HEAD `4002f19b`: `scripts/verify_ml_evidence.py:181` (`Status = Literal["OK", "FAIL", "ABSENT", "INFO", "STALE"]`), :197-201 `_DECLARED_GROUNDING_GAP`, :203-206 `_is_declared_grounding_gap`, :1459-1462 (the fingerprint row's STALE branch), :1554-1566 `_CORPUS_DEPENDENT_RECOMPUTE_ROWS` (nine names), :1569-1575 `_STALE_GROUNDING_NOTE`, :1577-1610 `_grounding_row`, :1927-1948 (the emitted-name assert + the downgrade loop), :1953 `_verdict_identity_row` (*"The strongest pin: the whole committed verdict object, field for field."*), :3018 and :3028-3035 (the summary counter's STALE arm and its epilogue) against :3049 `every check passed.`; `training/surrogate/runner.py:365-386` `SurrogateFitCorpus`, :388-414 `fit_corpus_fingerprint`, :432-513 the load-path fences; `training/anchor_study.py:143` `CORPUS_DIR`, :168 `HIGH_FLAG_FLOOR = 180 / 165`, :212-255 `compute_substrate_sha` (payload: `baseline_id`, corpus MANIFEST + splits + replay-byte digests, `flags_per_meeting_floor`); `training/bakeoff/map_elites.py:711-728` `bakeoff_substrate_sha`; `training/bakeoff/harness.py:181` `BAKEOFF_BASELINE_ID: Final[str] = "baseline-6"`; `tests/training/_regrounding.py` and its two call sites `tests/training/test_bakeoff_harness.py:130`, `:361-364`, `:557-561`; the nine F1 nodes all present — `tests/training/test_anchor_study.py:662`, `tests/training/test_coevo_driver.py:1525` and `:1668`, `tests/training/test_composed_runner.py:1217`/`:1243`/`:1275`/`:1586` under `pytestmark = pytest.mark.campaign` at `:127`, `tests/training/test_surrogate_fidelity.py:375`, `tests/training/test_scenarios.py:433` (21.13's). **One correction to F1, re-derived at HEAD:** F1 states the substrate-sha pair as *"recorded `f5865c53…`, live `9bc00af0…`"*; it is the other way round — `compute_substrate_sha()` returns `f5865c53…` live, while `training/artifacts/anchor_study/study.json` and all 60 `compute_substrate_sha`-kind campaign rows (36 impostor + 24 crew) record `9bc00af0…`; on the other definition `bakeoff_substrate_sha()` returns `ff7afd85…` live against `e4547789…` recorded in the pool stamp and in the 16 `bakeoff_substrate_sha`-kind impostor rows.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-reground`
**Depends on:** 21.8, 21.15, 21.16
**Section refs:** audits/audit-phase-20-baseline-7.md §10.2 ("The ML re-ground — A NAMED FOLLOW-UP, not a silent debt"), which routes this task verbatim — *"re-fit the surrogate and the conviction model on `replays/ml_corpus/`, re-stamp the fit-corpus fingerprint and the MAP-Elites pool's substrate stamp, move `BAKEOFF_BASELINE_ID`, and re-publish `docs/ml-program.md`'s arms"* — plus the three interim holdings it installed and this task retires (the `STALE` status, the `tests/training/` tripwires, `tests/training/_regrounding.py`); audits/audit-phase-20-close.md §1 F1 (`uv run pytest -m campaign` exits 1 with **9 failed, 308 passed**; the three classes; the routing at :108-113 — *"take the nine campaign-tier pins with it, either re-grounded or converted to tripwires in §10.2's own declared shape"*); audits/review-2026-08-26/B/collated-findings.md B-20 (verifier: the headline is REFUTED — `conversion_bar` IS gated green in the default tier by `tests/training/test_conviction_model.py:860`; the surviving residual is (a) the two verdict-identity rows bundle corpus-dependent and corpus-independent FIELDS so the row-scoped amnesty darkens the latter, (b) neither `verdict.json` has a `.sha256` sidecar, (c) `conversion_ceiling` on the committed conviction verdict has no pin anywhere) and B-46 (verifier: the deletion inventory, and the corrected test enumeration — THREE tests assert `STALE` as the expected answer, `:456` uses it only as a scoping filter and `:500` asserts the OPPOSITE; *"the one thing that must survive deletion is the assertion that a fingerprint MISMATCH fails — that is the whole gate"*); B-11 for the axis-3 disposition this task consumes rather than invents (21.16 pre-registers it), B-16/B-17 for the conviction fit-corpus record and the committed surrogate verdict this task fills (21.8 introduces them), B-47 for the `eval/watchability.py` bake-off-lag note this task's constant move obsoletes — routed HERE at assembly (it was drafted into 21.11) so the note and the constant it describes move in one commit. Anchors re-verified at HEAD `4002f19b`: `scripts/verify_ml_evidence.py:181` (`Status = Literal["OK", "FAIL", "ABSENT", "INFO", "STALE"]`), :197-201 `_DECLARED_GROUNDING_GAP`, :203-206 `_is_declared_grounding_gap`, :1459-1462 (the fingerprint row's STALE branch), :1554-1566 `_CORPUS_DEPENDENT_RECOMPUTE_ROWS` (nine names), :1569-1575 `_STALE_GROUNDING_NOTE`, :1577-1610 `_grounding_row`, :1927-1948 (the emitted-name assert + the downgrade loop), :1953 `_verdict_identity_row` (*"The strongest pin: the whole committed verdict object, field for field."*), :3018 and :3028-3035 (the summary counter's STALE arm and its epilogue) against :3049 `every check passed.`; `training/surrogate/runner.py:365-386` `SurrogateFitCorpus`, :388-414 `fit_corpus_fingerprint`, :432-513 the load-path fences; `training/anchor_study.py:143` `CORPUS_DIR`, :168 `HIGH_FLAG_FLOOR = 180 / 165`, :212-255 `compute_substrate_sha` (payload: `baseline_id`, corpus MANIFEST + splits + replay-byte digests, `flags_per_meeting_floor`); `training/bakeoff/map_elites.py:711-728` `bakeoff_substrate_sha`; `training/bakeoff/harness.py:181` `BAKEOFF_BASELINE_ID: Final[str] = "baseline-6"`; `tests/training/_regrounding.py` and its two call sites `tests/training/test_bakeoff_harness.py:130`, `:361-364`, `:557-561`; the nine F1 nodes all present — `tests/training/test_anchor_study.py:662`, `tests/training/test_coevo_driver.py:1525` and `:1668`, `tests/training/test_composed_runner.py:1217`/`:1243`/`:1275`/`:1586` under `pytestmark = pytest.mark.campaign` at `:127`, `tests/training/test_surrogate_fidelity.py:375`, `tests/training/test_scenarios.py:433` (21.13's). **One correction to F1, re-derived at HEAD:** F1 states the substrate-sha pair as *"recorded `f5865c53…`, live `9bc00af0…`"*; it is the other way round — `compute_substrate_sha()` returns `f5865c53…` live, while `training/artifacts/anchor_study/study.json` and all 60 `compute_substrate_sha`-kind campaign rows (36 impostor + 24 crew) record `9bc00af0…`; on the other definition `bakeoff_substrate_sha()` returns `ff7afd85…` live against `e4547789…` recorded in the pool stamp and in the 16 `bakeoff_substrate_sha`-kind impostor rows.
**Complexity:** Integration
**Record impact:** none — no rendered prompt byte, no recorded replay byte and no detector output moves. This task reads the 21.15 record and writes only ML artifacts, their pins and their prose; it is post-record by ordering and record-neutral by content.
**Measurement:** `uv run pytest -m campaign -q` green (against F1's **9 failed, 308 passed** at the Phase-20 close HEAD), with the PR naming each of the eight pins this task re-grounds and how; `uv run python scripts/verify_ml_evidence.py --complete` exits 0 with the `ML grounding` row reading `OK` and both fingerprints equal, and `grep -c STALE scripts/verify_ml_evidence.py` reads 0 — the token is GONE from the source, so the summary counter it fed no longer exists and cannot be asserted on (an `STALE 0` expectation would force the implementer to keep the dead arm alive); `uv run pytest tests/training tests/scripts/test_verify_ml_evidence.py -q` green; and the PR Summary quotes the fit-corpus fingerprint and both substrate shas before and after, recomputed by the one-liners in §Reproduce of each refreshed report.

Every committed ML fit in this repository is keyed to bytes that no longer exist. The
baseline-7 record re-recorded `replays/ml_corpus/` without re-fitting anything, and said so
in advance: §10.2 named the re-ground as a follow-up, held the interim state loud with a
`STALE` status and a set of tripwires, and froze `training/` precisely so one commit could
not move the ML baseline and the substrate baseline together. Phase 21's own record (21.15)
re-records the corpus a second time, on the corrected substrate. This task is where the
bookkeeping debt is paid — once, against the corpus 21.15 leaves behind, with the bars 21.16
re-derived and the row hygiene 21.8 landed already in the tree.

The debt is measurable and it is exactly one gap wide. The surrogate's committed
`fit-corpus.json` names corpus `164ef00c…`; `replays/ml_corpus/9p2i` fingerprints to
`45b11993…`, and `scripts/verify_ml_evidence.py:197-201` carries that pair as a literal so
that any OTHER mismatch still FAILS. Ten rows report `STALE` today and the command still
exits 0. `tests/training/test_conviction_model.py:792` asserts the refit DISAGREES with the
committed weights; `tests/training/test_surrogate_runner.py:496` asserts the committed fit
and the live corpus disagree; `tests/training/test_bakeoff_methods.py:1110` asserts the
MAP-Elites pool's stamp is stale; `tests/training/_regrounding.py` exists solely to keep the
harness paths runnable behind a refusal about the model. Each of those was written to FAIL
when this task lands. Making them fail correctly — by inverting the assertion, not by
deleting the guard — is half the work.

The other half is the campaign tier, red since before the Phase-20 close. F1 counted nine
failures and routed eight of them here (the ninth, the mover scenario pin, is 21.13's and
pre-dates the record). They are not one class. Five are corpus-derived fit pins — the four
composed-runner nodes and the FO-6 re-baseline node — and those simply re-derive once the
fits are re-ground. Three are substrate-sha self-consistency pins, and only ONE of them is
re-groundable: the anchor study's artifacts can be re-run at $0 on the new substrate, but the
two coevo pins compare RECORDED campaign rows against a live digest, and those rows are a
recording of a search that ran for hours. Re-stamping them would forge provenance. So this
contract rules them, rather than repairing them by force: the recorded shas stay recorded,
the pin becomes a provenance pin against the campaign's own committed provenance, and the
invariant the dynamic pin was standing in for — a seed whose substrate sha does not match the
live one is REFUSED at ingest — gets its own planted-case gate at the fence that actually
enforces it (`training/coevo/hall_of_fame.py:1457-1459`,
`load_archive_cell_genomes(..., expected_substrate_sha=...)`).

The interim state established two things worth carrying in rather than rediscovering, and
§10.2 says so itself. The conviction model, evaluated **fully out-of-sample** on a corpus it
had never seen, still returned GO on both bars with a HIGHER flag Spearman — 0.699 against
the recorded 0.578 — on a smaller held-out split, 87 meetings against the recorded 96. So a
conviction GO on the new corpus is not a surprise and is not evidence of anything new; what
would be informative is a NO-GO, and 21.8's precision guard beside recall is what makes that
outcome reachable at all. And the FO-6 comparator head has flipped three records running
(SKIP → all-EJECT → SKIP), which is why 21.16 reframes it as a meeting-mix tracker rather
than a physical baseline: whatever it reads here, it is not read as physics.

Two things this task deliberately does NOT do, both stated here so no reader infers
otherwise. It does not re-search: the λ grid in `training/artifacts/anchor_study/` and the
committed champion it is byte-identical to were found under the impostor objective as it
stood, and 21.16 repairs that objective (`training/rewards.py` feeds
`training/bakeoff/harness.py:154`, which the study imports at `training/anchor_study.py:98`).
Re-running the sweep under a changed objective produces a NEW study, not a re-ground, and it
would silently re-price a recorded result; only the corpus-derived filtered-BC anchor is
re-fit, exactly as the 18.14 turn of this same recipe did. And it does not re-price the arms
in `docs/ml-program.md` §Results: those win edges were measured against a comparator this
repository no longer ships, the document already says so in its own erratum, and re-measuring
them means a fresh campaign — an owner decision, routed, not a documentation edit. What
§10.2's "re-publish the arms" earns here is the grounding half: which corpus, which fits,
which verdicts, which bars, and which sentences stop being true.

The framing constraint on every sentence this task writes: **baseline 7 is canon by an
explicit owner override of a FINDING verdict** — bars 1 and 2 were missed
(audits/audit-phase-20-baseline-7.md §3, §6.1). Nothing in the refreshed reports, the
re-published `docs/ml-program.md` grounding section, or the PR may read as if that record
passed its bars; the re-ground inherits a ratified reference recording, not a cleared one.

**Files in scope:**
- training/artifacts/surrogate/; (the re-fit weights, the sha256 sidecar, the staleness cap re-keyed to the NEW fit-side meeting count, the rewritten `fit-corpus.json`, and the verdict artifact 21.8 introduced)
- training/artifacts/conviction/; (the re-fit weights + sidecar + cap + `verdict.json` from the FIRST held-out evaluation on the new corpus, plus the conviction-side `fit-corpus.json` 21.8 introduced, and a `verdict.json.sha256` sidecar)
- training/artifacts/composed/; (`manifest.json` + `verdict.json` re-derived from the two re-ground components, plus a `verdict.json.sha256` sidecar)
- training/artifacts/anchor_study/; (ONLY the corpus-derived `filtered-bc-anchor` weights re-fit, and every `config.json` + `study.json` substrate sha re-stamped; the λ-cell genomes and the λ=1.0/champion byte identity are untouched)
- training/artifacts/impostor/map-elites/cells/index.json; (the two-field pool re-stamp §10.2 routes — `baseline_id` and `substrate.substrate_sha256`)
- training/bakeoff/harness.py; (`BAKEOFF_BASELINE_ID` moves off `"baseline-6"` to `"baseline-8"` — the id 21.15's record stamps, read out of that record's audit rather than assumed — with its comment rewritten to state what it names rather than what it lags)
- training/anchor_study.py; (`HIGH_FLAG_FLOOR` re-pinned to the adopted `flags_per_meeting` floor, so `compute_substrate_sha`'s payload names the floor actually used; one provenance line, no history essay)
- scripts/verify_ml_evidence.py; (the amnesty deleted; the two verdict-identity rows report a per-field corpus-derived/corpus-independent partition in their detail; the closing summary loses its STALE arm)
- tests/scripts/test_verify_ml_evidence.py; (the three STALE-as-expected assertions re-pointed to OK; the scoping test and the undeclared-corpus FAIL guard kept, both with their perturbations; two new planted cases for the field partition)
- tests/training/test_surrogate_runner.py; (the hybrid tripwire inverts to an equivalence pin; the fence test keeps its refusal proof with a synthetic drifted corpus; the fidelity/FO-6/verdict pins re-derive)
- tests/training/test_conviction_model.py; (the refit-disagrees tripwire inverts to the ULP-equivalence pin; the committed-verdict pin re-pins to the new held-out evaluation; `conversion_ceiling` gains the value pin B-20 (c) found missing)
- tests/training/test_composed_runner.py; (the four F1 nodes re-derive)
- tests/training/test_surrogate_fidelity.py; (the FO-6 node re-derives against 21.16's reframed comparator)
- tests/training/test_anchor_study.py; (the substrate-sha pin goes green on the re-run; the λ=1.0 byte-identity pin is asserted UNCHANGED)
- tests/training/test_coevo_driver.py; (the two campaign-row pins become provenance pins, plus the live stale-seed fence gate with its planted case)
- tests/training/test_bakeoff_methods.py; (the pool tripwire inverts: the stamp is current and the genomes still reproduce)
- tests/training/test_bakeoff_harness.py; (both `_regrounding` call sites point back at `training/artifacts/surrogate` directly)
- tests/training/_regrounding.py; (DELETED — its own docstring says it has no reason to exist once this lands)
- training/reports/report-ballot-surrogate.md; (§3–§5 re-measured, §9 one-liners re-run and re-quoted, §8's recipe marked as executed again)
- training/reports/report-conviction-model.md; (§4–§5 re-measured, §7 cap re-derived, §9 re-run)
- training/reports/report-composed-runner.md; (§3–§4 re-measured, §6 Goodhart leg re-run, §9 re-run)
- training/reports/report-anchor-study.md; (the re-stamped substrate and the re-fit anchor; the λ grid explicitly recorded as unchanged)
- docs/ml-program.md; (the grounding half re-published — corpus, fits, verdicts, bars; the arms table and its erratum untouched)
- docs/artifacts.md; (the `training/artifacts/…` registry rows' file counts and sizes re-derived after the sidecars land)
- eval/watchability.py; (B-47's bake-off-lag comment block at `:908-914` ONLY — routed here at assembly so the note and the constant it describes move in one commit; no gauge, floor or baseline id in this module changes)

**Files NOT in scope:**
- tests/training/test_scenarios.py (F1's ninth failure is 21.13's; it pre-dates the record and belongs to 20.32's mover repair, not to the corpus)
- replays/ (the record is 21.15's; this task reads its bytes and writes none — `verify_samples.sh` and the corpus fingerprint are inputs here, never outputs)
- training/rewards.py, training/surrogate/fidelity.py, training/surrogate/ballots.py (21.16 owns the objectives, the GO bars and the FO-6 reframe; this task RUNS them and must not retune a bar it is being measured by — if a bar cannot be evaluated as landed, stop and report)
- training/conviction/dataset.py, training/conviction/model.py (21.7's grounding channels and 21.8's fit hygiene; this task consumes both)
- eval/watchability.py's gauges, floors and `_DEFAULT_BASELINE_ID` (the `baseline-8` block and the default id are 21.15's record; only B-47's comment block at `:908-914` is in scope here, and a diff of this file touching anything else is out of scope)
- training/reports/results-impostor-campaign.jsonl, results-crew-campaign.jsonl, results-impostor-bakeoff.jsonl, results-finalist-eval.jsonl (recorded results; a recorded provenance stamp is never re-stamped, and re-running any of them is an owner decision)
- training/artifacts/impostor/{utility-es,policy-es,bc-dagger}/, training/artifacts/crew/, training/artifacts/coevo/ (learned genomes and campaign provenance — substrate-independent recordings, untouched)
- meetings/, agents/, orchestrator/, api/, frontend/ (nothing about this task reaches the game or the served surfaces)

**Definition of done:**
- [ ] Nothing is fit against an unfrozen corpus. Before the first fit, the PR records that 21.15's `replays/ml_corpus/` legs are FROZEN per the corpus README's freeze doctrine and that `bash scripts/verify_samples.sh` and the corpus reconstruction leg are green on the bytes about to be read — a re-fit taken mid-recording is a fit against a moving target and cannot be reproduced.
- [ ] The surrogate is re-fit on `replays/ml_corpus/9p2i` by the committed recipe (`training/reports/report-ballot-surrogate.md` §8, steps 2–5): the walk re-validation runs FIRST and records `raw_mismatches == 0`, the coerced-SKIP census is read off the rebuilt table under 21.8's corrected marker-kind filter, then weights + sha256 sidecar + `max-uses.json` (`derive_max_uses(<new fit-side count>)`) + `fit-corpus.json` (`corpus_sha256=fit_corpus_fingerprint(<corpus dir>)`) are committed together. `load_surrogate_runner_factory(artifact_dir, corpus_dir=…)` loads clean with the fingerprint check enabled.
- [ ] The conviction model is re-fit by its own recipe (`training/reports/report-conviction-model.md` §8): `fit_corpus_conviction_model`, then weights + sidecar + cap (`derive_conviction_max_uses(<new fit-side count>)`) + `verdict.json` from `decide_conviction_go` on that FIRST held-out evaluation, whichever way it reads — under 21.8's precision guard beside recall — and the conviction-side `fit-corpus.json` 21.8 introduced is written in the same commit, so the `ML grounding` row measures both fits rather than asserting one transitively (B-16).
- [ ] The composed verdict is re-derived last, from the two re-ground components: `run_composed_fidelity` → `decide_composed_go` → `write_composed_manifest_artifact` + `write_composed_verdict_artifact`, plus a fresh Goodhart leg per `report-composed-runner.md` §6, and the report's §3/§4/§6 cells are rewritten from that run.
- [ ] Each verdict is taken and published as it reads. A GO publishes as GO and a NO-GO publishes as NO-GO with its pre-committed consequence mapping (`report-ballot-surrogate.md` §1/§5/§6, `report-conviction-model.md` §6); no bar is retuned in this task to change a verdict, and if 21.16's re-derived axis-3 disposition turns out not to be evaluable on these bytes, the PR STOPS and reports rather than improvising one.
- [ ] The MAP-Elites pool is re-stamped: `training/artifacts/impostor/map-elites/cells/index.json` carries the adopted `baseline_id` and `substrate.substrate_sha256 == bakeoff_substrate_sha()`, the 30 cell genomes and `filled_cells` are asserted UNCHANGED in the same test, and `tests/training/test_bakeoff_methods.py:1110` is inverted rather than deleted — its two halves stay asserted together so a current stamp can never be read without the untouched structure beside it.
- [ ] The anchor study is re-run at $0 on the new substrate: the corpus-derived `filtered-bc-anchor` is re-fit, every entrant `config.json` and `study.json` re-stamp to the live `compute_substrate_sha()` and the adopted `baseline_id`, and `tests/training/test_anchor_study.py::test_committed_lambda_1_artifact_reproduces_the_champion_byte_for_byte` is re-run and asserted UNCHANGED — the λ genomes are a recording of a search under the pre-21.16 objective and are not re-searched here.
- [ ] The objective-change limitation is recorded once, where a reader of the study will meet it: `compute_substrate_sha`'s payload covers the corpus, the baseline id and the flag floor and NOT the fitness objective, so 21.16's repair is invisible to the stale-seed fence. `training/reports/report-anchor-study.md` states in one paragraph that the λ grid is a recording under the prior objective, and the PR routes "re-search the λ grid and the campaign under the repaired objective" to the owner as a campaign-scale decision, alongside the arms.
- [ ] `BAKEOFF_BASELINE_ID` moves to the id 21.15's record stamps and `HIGH_FLAG_FLOOR` is re-pinned to that baseline's committed `flags_per_meeting` floor, so `compute_substrate_sha`'s `flags_per_meeting_floor` names the floor actually used. `tests/training/test_bakeoff_harness.py`'s selection-bar pin moves with it; the four committed bake-off rows keep their recorded `baseline_id` and their pins are asserted unchanged (they are provenance, not a current claim).
- [ ] The floor the selection bar now reads is stated with its composition, not just its value: the PR quotes the `flags_per_meeting` floor's two components (re-derived transcript flags vs persisted vent sightings) from 21.7's corrected floor-composition work, so a moved selection floor is never adopted with an unstated denominator (B-10's note, landed in 21.7 and consumed here).
- [ ] The STALE amnesty is DELETED, not disabled: `_DECLARED_GROUNDING_GAP` (`:197-201`), `_is_declared_grounding_gap` (`:203-206`), `_STALE_GROUNDING_NOTE` (`:1569-1575`), the fingerprint row's STALE branch (`:1459-1462`), `_grounding_row`'s `stale` return arm (`:1602-1610`), the recompute downgrade loop (`:1935-1948`), `"STALE"` in the `Status` literal (`:181`), and the STALE arms of the summary counter (`:3018`) and its epilogue (`:3028-3035`) are all gone. `grep -rn STALE scripts/verify_ml_evidence.py` returns nothing.
- [ ] The assertion B-46 names as the one that must survive deletion is pinned and can fail: `tests/scripts/test_verify_ml_evidence.py::test_an_undeclared_corpus_still_fails_the_grounding_row` (`:500`) keeps its planted drifted corpus and still asserts `status == "FAIL"` with `"undeclared substrate"` in the detail, now with no amnesty branch to fall through.
- [ ] The three tests that assert `STALE` as the expected answer are RE-POINTED, never dropped — `:372`/`:395` and `:399`, `:460`/`:495`, and the fit-corpus identity row at `:684` — each asserting `OK` and the two fingerprints agreeing. `:427` keeps its per-row scoping proof, rewritten so it no longer filters on a status that no longer exists, and B-46's own correction is recorded: of the five tests that mention STALE, only these three asserted it as correct, `:456` was a scoping filter and `:500` asserted the opposite.
- [ ] The two verdict-identity rows unbundle: `_verdict_identity_row` takes the declared set of corpus-derived field names and, on any drift, classifies each disagreeing field as corpus-derived or corpus-independent in the row detail. The row still FAILS on ANY drift — the classification is diagnostic, so no future re-record can reach for a row-scoped amnesty again — and two planted cases prove it bites: drift one corpus-derived field and one corpus-independent field, and assert each FAILS naming its own class.
- [ ] `_CORPUS_DEPENDENT_RECOMPUTE_ROWS` survives as that declared partition with a live consumer (the classification above and the existing emitted-name completeness assert at `:1927-1931`), and its docstring is rewritten to say what it is now rather than what the amnesty used it for. If it ends with no live consumer, delete it — rule 3 admits no ornamental constants.
- [ ] `training/artifacts/conviction/verdict.json` and `training/artifacts/composed/verdict.json` each gain a `<name>.sha256` sidecar (B-20 (b)), verified by the existing sidecar leg — `uv run python scripts/verify_ml_evidence.py --only sidecars` names both — and `conversion_ceiling` on the committed conviction verdict gains its first value pin anywhere (B-20 (c)), in the default-tier test at `tests/training/test_conviction_model.py:860` beside `conversion_bar`.
- [ ] The command's closing line means what it says again. With the STALE arm gone, `verify-ml-evidence: every check passed.` is reachable only when nothing is amnestied, and the PR quotes the full summary line — B-20's loudness note (the epilogue carried the real state while only the last line was read) stops applying because there is no epilogue left to miss.
- [ ] `tests/training/_regrounding.py` is deleted and both call sites in `tests/training/test_bakeoff_harness.py` (`:361-364`, `:557-561`) pass `training/artifacts/surrogate` directly, with the two interim comments removed rather than reworded. `grep -rn _regrounding tests/` returns nothing.
- [ ] The two coevo campaign-row pins are RULED, not forced. `tests/training/test_coevo_driver.py:1525` and `:1668` stop comparing recorded rows against a live digest and instead assert each block's recorded `substrate_sha256`/`substrate_sha_kind` against the sha the campaign's OWN committed provenance records (`training/artifacts/coevo/provenance/`, `EVIDENCE-MANIFEST.md`) — a cross-file pin, never a literal copied out of the rows it checks — with the dispatch-per-block coverage kept. The test docstrings state, in one line each, that these are recordings of a campaign run on a substrate this checkout no longer holds.
- [ ] The invariant those pins were standing in for gains a gate that can fail: a test drives `HallOfFame`'s MAP-Elites ingest (`training/coevo/hall_of_fame.py:1457-1459`) with a cell tree whose stamp does not match, and asserts the `ValueError` matching `adopted substrate`; the positive case ingests the re-stamped pool cleanly. Without both halves the stale-seed fence is prose.
- [ ] The two carry-forward facts §10.2 recorded are read back explicitly rather than left to be rediscovered: the PR states what the conviction verdict is now against its out-of-sample precedent (GO on both bars, flag Spearman 0.699 on 87 held-out meetings against the recorded 0.578 on 96), and what the FO-6 head does on a fourth record against its SKIP → all-EJECT → SKIP history — quoted as a meeting-mix observation, never as a physical baseline.
- [ ] `uv run pytest -m campaign -q` is green, and the PR maps all nine of F1's failures to an outcome: five corpus-derived fit pins re-derived, one substrate-sha pin re-ground, two converted to provenance pins with the fence gate beside them, and the ninth named as 21.13's.
- [ ] A TENTH campaign-tier pin is expected here and is discharged rather than discovered. Task 21.5 removes the audible copy of a witnessed vent, so `agents/tactical/features.py`'s `heard_vent_use` encoder slot goes structurally 0 for vents — the slot index and `ENCODER_VERSION "v2"` do not move, only the value a live packet produces — and learned-policy rollouts can therefore shift. 21.5 explicitly routes any campaign-tier pin that moves for that reason HERE rather than re-pinning it in place. The PR names each such pin, states that the cause is the narrowed encoder input and not the corpus, and re-derives it in the same commit as the fits; a pin that moves for any OTHER reason stops the task and is reported instead.
- [ ] `eval/watchability.py:908-914` no longer restates `BAKEOFF_BASELINE_ID`'s value: the block names the symbol and its module, or is deleted outright, in the SAME commit that moves the constant — which is the whole reason it is scoped here rather than upstream. No gauge, floor or `_DEFAULT_BASELINE_ID` in that module is touched, and `git diff eval/watchability.py` in the PR shows a comment-only change.
- [ ] The `ConvictionMeetingRow.rederived_flags` rename that 21.7 named as ROUTED rather than forgotten is executed here or is declined in writing. 21.7 left the field name alone deliberately — the row is the frozen 18.15 artifact contract and the keyword is constructed in three test modules owned by parallel Wave-1b tasks — and this task is the first point at which all of them have merged and the artifacts are being rewritten anyway. Rename it to what it now holds, with every construction site moved in the same commit and the artifact contract's version note updated; or, if the rename would move a committed artifact's field name and therefore its digest, state that in one line and leave the routing standing. Either outcome is recorded; silently dropping it is not.
- [ ] `uv run python scripts/verify_ml_evidence.py --complete` exits 0 and the `ML grounding` row reads `OK` with both fingerprints equal; the PR quotes the before/after pair (`164ef00c…` vs `45b11993…` before; equal after) recomputed live, never copied from this contract. The check is deliberately NOT "the summary line reads `STALE 0`": the item above deletes `"STALE"` from the `Status` literal and both summary arms, so a counter that could print `STALE 0` would be dead mechanism kept alive to satisfy a checklist (craft rule 3). The absence is asserted at the source instead — `grep -c STALE scripts/verify_ml_evidence.py` reads 0 — and the health of the grounding is asserted by the row, which is the thing that actually carries the answer.
- [ ] The four training reports are refreshed in the same commit as the artifacts they describe (each recipe's "commit together" step), every §Reproduce one-liner is re-run and its output re-quoted, and no cell is carried forward unmeasured. Where a number is a RECORD of the prior corpus rather than a current measurement, it is labelled as such and left, in the reports' established errata style — history is extended, never rewritten in place.
- [ ] `docs/ml-program.md`'s grounding half is re-published: which corpus the fits now stand on, which verdicts they now return, and which bars 21.16 re-derived them against — with the arms table, its `p` column and its erratum untouched, and one sentence stating plainly that those edges were measured against a comparator this repository no longer ships and are not re-priced here. Any sentence about the reference recording says what §6.1 says: baseline 7 is canon by an explicit owner override of a FINDING verdict, two bars missed.
- [ ] `docs/artifacts.md`'s `training/artifacts/…` registry rows are re-derived (file counts and sizes) after the new sidecars and 21.8's artifacts land, and `uv run python scripts/verify_ml_evidence.py --only availability` is green.
- [ ] Blast radius is stated from a fresh grep in the PR, not from this contract: `grep -rn 'BAKEOFF_BASELINE_ID\|HIGH_FLAG_FLOOR\|compute_substrate_sha\|bakeoff_substrate_sha' --include='*.py' --include='*.md' .` — every consumer is named with what happened to it, and any hit outside the files in scope stops the task rather than widening it (craft rule 6).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — read the ground truth before touching anything, and write the four numbers into the
PR draft first. `uv run python -c "from pathlib import Path; from training.surrogate.runner
import fit_corpus_fingerprint, load_fit_corpus_record; print(load_fit_corpus_record(Path('training/artifacts/surrogate')).corpus_sha256);
print(fit_corpus_fingerprint(Path('replays/ml_corpus/9p2i')))"` and
`uv run python -c "from training.anchor_study import compute_substrate_sha; from
training.bakeoff.map_elites import bakeoff_substrate_sha; print(compute_substrate_sha(),
bakeoff_substrate_sha())"`. At the Phase-20 close HEAD those read `164ef00c…` / `45b11993…`
and `f5865c53…` / `ff7afd85…`; on 21.15's corpus they will all be different, which is the
point. Everything downstream is a function of these, so capture them once.

Step 2 — order matters and it is not the order of the file list. Surrogate first (its
`fit-corpus.json` is what `_grounding_row` reads), conviction second, composed third (it
loads both components and cross-checks their shas), the anchor study and the pool re-stamp
fourth, and the constants last — `BAKEOFF_BASELINE_ID` and `HIGH_FLAG_FLOOR` feed
`compute_substrate_sha`, so moving them before the study re-run means re-stamping twice. Run
each component's own §8 recipe verbatim rather than a hand-rolled fit: the recipes exist
because a re-fit that writes weights without re-writing the cap and the fit-corpus record
fails loud at load time (`training/surrogate/runner.py:479-495`), and that failure is the
design working.

Step 3 — the amnesty deletion is mechanical, and the test work is where the judgment is. Do
the code deletion first and watch `tests/scripts/test_verify_ml_evidence.py` go red in
exactly five places; that red list is your inventory, and it should match B-46's corrected
one (three assertions to re-point, one scoping filter to rewrite, one FAIL guard that must
survive untouched in meaning). Re-point rather than delete: a test that asserted the gap and
now asserts agreement is the proof the gap closed, and a deleted one proves nothing. The
`Status` literal drop is what makes a missed site a type error rather than dead code, so drop
it early and let `mypy` find the rest.

Step 4 — the field partition. `_verdict_identity_row` already walks the committed object
field by field; give it a frozenset of corpus-derived field names (the ones the recompute leg
measures: the test-split counts, the accuracies, the Spearman, the bars derived from them)
and have the detail line say `corpus-derived` or `corpus-independent` beside each drifted
field. The row's verdict does not change — any drift FAILS — so the two planted cases are
cheap: copy the artifact to `tmp_path`, perturb one field of each class, assert FAIL and
assert the class name appears in the detail. Resist the pull to reintroduce a downgrade path
"for next time"; the next re-record's amnesty, if it needs one, is that record's contract to
write with its own declared digest pair.

Step 5 — the two coevo pins. Read the campaign's committed provenance under
`training/artifacts/coevo/provenance/` and `EVIDENCE-MANIFEST.md` and find where the run's
substrate is recorded independently of the result rows; pin row-against-provenance, and keep
the existing per-block dispatch coverage (`_COMPUTE_SUBSTRATE_BLOCKS` /
`_BAKEOFF_SUBSTRATE_BLOCKS`) so a row that names the wrong sha KIND still fails. If the
provenance does not record the substrate independently, say so in the PR and pin the recorded
value as a dated literal with the provenance gap named — do not invent a cross-check that is
really the rows checking themselves. The fence test is the compensating control either way,
and it is the one that must be able to fail.

Step 6 — the reports and `docs/ml-program.md` are not a victory lap. Every number is re-run
from a §Reproduce one-liner and pasted; nothing is edited by analogy to the previous
recording. The one sentence to get exactly right appears in three places (the surrogate
report's verdict section, `docs/ml-program.md`'s grounding section, and the PR Summary): the
reference recording is canon by an explicit owner override of a FINDING verdict, with two
bars missed. Write it that way each time. `uv run python scripts/check_doc_facts.py` and
`uv run pytest -m campaign` are the last two commands, in that order, before the PR.

Step 7 — expect two classes of platform noise and do not paper over either. The filtered-BC
fit and the ballot predictor are numpy full-batch gradient descent: byte-identical on the
recording platform, ULP-equivalent elsewhere (`training/anchor_study.py:51-58` states the
caveat). Commit the artifact bytes you actually produced and let the equivalence pins compare
with a tolerance, exactly as the pre-existing round-trip tests do — never hand-edit a weight
to make a byte-identity assertion pass. Separately, the ES artifacts and the pool cells are
bit-deterministic and must reproduce EXACTLY; if one of those moves, something outside this
task's ruling changed and the task stops and reports rather than re-pinning it.

## Public types this task introduces
- `scripts.verify_ml_evidence.CORPUS_DERIVED_VERDICT_FIELDS`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This task moves the ML program's grounding, its selection floor and its evidence gate in one
PR, and its own exit criterion is a tier that has been red since before the Phase-20 close.
Two seams are unforgiving: a re-fit that writes weights without re-keying the cap and the
fit-corpus record fails at load rather than at test time, and 21.16's objective repair means
the λ grid must be re-stamped but never re-searched — re-running it would silently re-price a
recorded result behind a substrate digest that does not cover objectives.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.rewards"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.replay_walk.ReplayWalkConfig"`
- `uv run python -c "import engine.tick"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import eval.watchability.SupplyFloors"`
- `uv run python -c "import eval.vj_instruments"`
- `uv run python -c "import eval.vj_instruments.VJInstrumentReport"`
- `uv run python -c "import eval.vj_instruments.VJMeetingRow"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import frontend/src/lib/contradictions"`
- `uv run python -c "import check_doc_facts"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-21-reground` with a title like `task 21.17: the ml re-ground: the fits move onto the new corpus, the amnesty dies, the campaign tier is green`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-20-baseline-7.md §10.2 ("The ML re-ground — A NAMED FOLLOW-UP, not a silent debt"), which routes this task verbatim — *"re-fit the surrogate and the conviction model on `replays/ml_corpus/`, re-stamp the fit-corpus fingerprint and the MAP-Elites pool's substrate stamp, move `BAKEOFF_BASELINE_ID`, and re-publish `docs/ml-program.md`'s arms"* — plus the three interim holdings it installed and this task retires (the `STALE` status, the `tests/training/` tripwires, `tests/training/_regrounding.py`); audits/audit-phase-20-close.md §1 F1 (`uv run pytest -m campaign` exits 1 with **9 failed, 308 passed**; the three classes; the routing at :108-113 — *"take the nine campaign-tier pins with it, either re-grounded or converted to tripwires in §10.2's own declared shape"*); audits/review-2026-08-26/B/collated-findings.md B-20 (verifier: the headline is REFUTED — `conversion_bar` IS gated green in the default tier by `tests/training/test_conviction_model.py:860`; the surviving residual is (a) the two verdict-identity rows bundle corpus-dependent and corpus-independent FIELDS so the row-scoped amnesty darkens the latter, (b) neither `verdict.json` has a `.sha256` sidecar, (c) `conversion_ceiling` on the committed conviction verdict has no pin anywhere) and B-46 (verifier: the deletion inventory, and the corrected test enumeration — THREE tests assert `STALE` as the expected answer, `:456` uses it only as a scoping filter and `:500` asserts the OPPOSITE; *"the one thing that must survive deletion is the assertion that a fingerprint MISMATCH fails — that is the whole gate"*); B-11 for the axis-3 disposition this task consumes rather than invents (21.16 pre-registers it), B-16/B-17 for the conviction fit-corpus record and the committed surrogate verdict this task fills (21.8 introduces them), B-47 for the `eval/watchability.py` bake-off-lag note this task's constant move obsoletes — routed HERE at assembly (it was drafted into 21.11) so the note and the constant it describes move in one commit. Anchors re-verified at HEAD `4002f19b`: `scripts/verify_ml_evidence.py:181` (`Status = Literal["OK", "FAIL", "ABSENT", "INFO", "STALE"]`), :197-201 `_DECLARED_GROUNDING_GAP`, :203-206 `_is_declared_grounding_gap`, :1459-1462 (the fingerprint row's STALE branch), :1554-1566 `_CORPUS_DEPENDENT_RECOMPUTE_ROWS` (nine names), :1569-1575 `_STALE_GROUNDING_NOTE`, :1577-1610 `_grounding_row`, :1927-1948 (the emitted-name assert + the downgrade loop), :1953 `_verdict_identity_row` (*"The strongest pin: the whole committed verdict object, field for field."*), :3018 and :3028-3035 (the summary counter's STALE arm and its epilogue) against :3049 `every check passed.`; `training/surrogate/runner.py:365-386` `SurrogateFitCorpus`, :388-414 `fit_corpus_fingerprint`, :432-513 the load-path fences; `training/anchor_study.py:143` `CORPUS_DIR`, :168 `HIGH_FLAG_FLOOR = 180 / 165`, :212-255 `compute_substrate_sha` (payload: `baseline_id`, corpus MANIFEST + splits + replay-byte digests, `flags_per_meeting_floor`); `training/bakeoff/map_elites.py:711-728` `bakeoff_substrate_sha`; `training/bakeoff/harness.py:181` `BAKEOFF_BASELINE_ID: Final[str] = "baseline-6"`; `tests/training/_regrounding.py` and its two call sites `tests/training/test_bakeoff_harness.py:130`, `:361-364`, `:557-561`; the nine F1 nodes all present — `tests/training/test_anchor_study.py:662`, `tests/training/test_coevo_driver.py:1525` and `:1668`, `tests/training/test_composed_runner.py:1217`/`:1243`/`:1275`/`:1586` under `pytestmark = pytest.mark.campaign` at `:127`, `tests/training/test_surrogate_fidelity.py:375`, `tests/training/test_scenarios.py:433` (21.13's). **One correction to F1, re-derived at HEAD:** F1 states the substrate-sha pair as *"recorded `f5865c53…`, live `9bc00af0…`"*; it is the other way round — `compute_substrate_sha()` returns `f5865c53…` live, while `training/artifacts/anchor_study/study.json` and all 60 `compute_substrate_sha`-kind campaign rows (36 impostor + 24 crew) record `9bc00af0…`; on the other definition `bakeoff_substrate_sha()` returns `ff7afd85…` live against `e4547789…` recorded in the pool stamp and in the 16 `bakeoff_substrate_sha`-kind impostor rows.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
