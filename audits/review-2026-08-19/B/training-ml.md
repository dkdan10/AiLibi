# Code review — area `training-ml`

Scope: `training/` (29,441 LOC), `experiments/` (16,802 LOC), `agents/tactical/learned/`
(2,656 LOC), `tests/training/` (26,070 LOC). Read-only review at `main` @ `b809b19c`.
Host: macOS 15.7.3 / arm64, CPython 3.11.15, repo venv via `uv run`. Machine load
recorded per timing (10-core, other reviewers concurrent).

---

## 1. Executive read (10 lines)

1. **The numerics and reproducibility engineering here is genuinely good** — better than
   most research code I have reviewed. Bit-exact float-hex artifacts, sha256 sidecars
   that all verify, a hand-rolled libm-free normal sampler with honest accuracy claims
   that hold under measurement, and a one-command offline evidence verifier.
2. **The ML methodology is sound where it matters**: by-game splits (anti-leakage),
   a feature set deliberately restricted to what the live runner can reconstruct, a
   label-poisoning leakage fence, deterministic zeros-init full-batch GD, and
   pre-stated population-relative GO bars.
3. I independently reproduced the headline surrogate numbers (46/60 top-1, 36/96
   decision) and independently confirmed the repo's own NO-GO on the decision arm is
   **structural, not a hyperparameter artifact** — it survives a 100× epoch and 300×
   lr sweep. The project's negative results are trustworthy.
4. I also **closed an open reproducibility question the repo asks a reader to close**:
   the ES golden digest reproduces bit-identically on Darwin-arm64 (§2 G1).
5. Against that: **no production module imports `training/` at all** (verified by
   whole-repo import closure), and `training/` + `experiments/` are **39.8% of the
   repo's non-test Python** for a program the repo itself declares FROZEN.
6. Two modules totalling **5,163 lines of source + test** (`scenarios.py`,
   `anchor_study.py`) have *no importer anywhere except their own tests*.
7. One real defect: `reconstruct_episode` silently reports a corrupted replay as a
   legitimate tick-budget truncation (P1, verified with a repro).
8. Two God classes (`_CampaignEngine` 875 lines / `HallOfFame` 786 lines) and two
   God modules (`bakeoff/harness.py`, `bakeoff/goodhart.py`, ~2.3k lines each).
9. **30.1% of non-blank lines in the area are docstring/comment**, with 639 embedded
   `Task N.M` / audit / PR provenance references. Auditable, but it welds the code to
   a task-numbering scheme and is the single biggest source of bulk.
10. Test cost is well managed (two tiers, 701 training tests, ~230 s total) and the
    parity gates are real, but a handful of tests pin AST structure rather than
    behaviour.

---

## 2. What is genuinely GOOD

### G1 [VERIFIED] The Task-19.3 portable normal sampler works — and I closed the open question

`training/bakeoff/es.py:40-92` records two reproducibility scopes and explicitly leaves
one open. `tests/training/test_es.py:118-127` says:

> "Darwin-arm64 (the host that recorded the OLD stream's divergence …) has **NOT** been
> run against this constant yet; that owner-assisted run is what would upgrade the
> module's claim from 'designed-portable' to 'portable'. **Record the result here when
> it happens.**"

I ran it. Load 5.54.

```
$ uv run pytest "tests/training/test_es.py::test_evolve_is_deterministic_and_hash_pinned" -q
1 passed in 0.22s

$ uv run python -c "<independent recompute of the same config/fitness>"
macOS-15.7.3-arm64-arm-64bit arm64 3.11.15
digest: e72e24fe30d58f8ba573550b3d7aa4ec90a50d541669f22608ecdc6ff55024a8
MATCHES PINNED GOLDEN: True
```

The Linux/x86-64-recorded golden reproduces bit-identically on Darwin-arm64. The
`rng.gauss` → AS241/`_ln` rewrite demonstrably fixed the platform divergence recorded at
`tasks/phase-18.md:2656-2659`. **Recommendation R1: record this in `es.py` and
`test_es.py` and upgrade the module's claim to "portable, confirmed on Linux-x86-64 and
Darwin-arm64".**

I also verified the two accuracy claims in those docstrings, which are *not* hand-waves:

| Claim (docstring) | Measured |
|---|---|
| `_ln` max rel deviation vs `math.log` "~5e-16" (`es.py:312-315`) | **4.143e-16** over 4×10⁵ log-uniform samples |
| AS241 abs deviation "< 1e-14 everywhere" (`es.py:424-432`) | **2.665e-15** vs an independent `erfc`-bisection reference |
| AS241 rel deviation "< 1e-13 where \|Φ⁻¹\| ≥ 1e-3" | **6.132e-14** |
| Sampler is N(0,1) | mean −0.00113 (0.71 SE), sd 1.00051, n = 4×10⁵ |

Re-implementing `ln` and the probit in-module to escape libm is an unusual call, and the
docstring justifies it with the exact mechanism (`log`/`cos`/`sin` are not
correctly-rounded; MT19937 + `random()`'s 53-bit compose are exact). It is correct, and
it is documented at the level a numerics reviewer needs. Confidence: high.

### G2 [VERIFIED] Artifact hygiene is airtight

All **55** `*.sha256` sidecars under `training/artifacts/` + `agents/tactical/learned/`
verify against their targets; zero mismatches, zero orphans. Weights serialize as
float-hex (`agents/tactical/learned/weights.json` → `"0x1.e5fdd6583ee78p+0"`, …), which
is lossless float64 — the right choice, and rare. Committed artifact bulk is modest
(2.2 MB artifacts + 2.5 MB reports); large raw slates are pushed to an evidence branch
with a manifest pin rather than committed.

### G3 [VERIFIED] `scripts/verify_ml_evidence.py` is an exemplary reproducibility gate

One offline, read-only command, 20 s in `--fast`, 54 checks, 0 failures. It does not just
check hashes — it *re-derives* every headline number from the frozen weights and compares
to the report that owns it:

```
[  OK  ] surrogate top-1 (ranking channel)      measured 0.7666666667 (46/60)  committed 0.7666666667
[  OK  ] conviction flag-count Spearman         measured 0.5781584983          committed 0.5781584983
[  OK  ] composed decision accuracy             measured 0.8645833333          committed 0.8645833333
[  OK  ] conviction verdict.json reproduces     18/18 fields identical
checks: 54 | OK 44 | FAIL 0 | ABSENT 5 | INFO 5
```

The `ABSENT` rows are the evidence-branch bytes, reported as their own class with counts
rather than silently skipped. I independently rebuilt the surrogate from the corpus and
got **46/60 and 55/60**, matching exactly. This is the strongest single artifact in the
area.

### G4 [VERIFIED] The train/serve parity gates are real bit-exact gates

The observation firewall forces the learned inference path to be re-implemented under
`agents/` (which may not import `training/`). The mitigation is not a smoke test — it is a
lockstep comparison of **float-hex feature streams, float-hex score streams, and chosen
intents at every decision of a real rollout**
(`tests/agents/test_learned_policy.py:462`, `tests/training/test_learned_factory_acceptance.py:616`),
with an explicit assertion that multi-option menus were actually exercised
(`multi_option_decisions > 0`). That is the correct shape for this hazard.

### G5 [VERIFIED] The mask-vs-engine property test checks both directions

`tests/training/test_env.py:340` replays 8 real games and asserts, per packet, that every
masked-legal intent is engine-accepted *and* every masked-illegal intent is
engine-rejected. My instrumented re-run measured **9,771 legal + 19,750 illegal + 151
submission-only assertions over 1,644 packets**. Two-sided mirror checks like this are
what makes an agent-side legality mirror safe to duplicate.

### G6 [VERIFIED] Anti-leakage discipline in the surrogate/conviction datasets

Splits are **by GAME, not by meeting** (`replays/ml_corpus/*/splits.json`, rule
`seed mod 5`), because a game's meetings share cross-meeting belief state.
`SurrogateSplits` (`training/surrogate/dataset.py:317`) is `extra="forbid"` + a validator
that refuses a self-inconsistent count. `_game_folds`
(`training/surrogate/fidelity.py:567-643`) refuses overlapping, omitted, empty, or
no-scoreable-meeting splits. The feature set is restricted *by design* to columns a live
runner can reconstruct (`training/surrogate/ballots.py:16-44`), with the excluded columns
and the reason named — this is the discipline that prevents an inflated offline number.
`fit`/`predict` label columns are fenced with a poison test.

### G7 [VERIFIED] Type and test discipline

`uv run mypy training agents/tactical/learned` → **Success, 40 source files**, with only
**8** `type: ignore` / `noqa` / `cast` occurrences in all of `training/`. All 701 training
tests pass (384 default + 317 campaign). The two-tier marker scheme
(`pyproject.toml:74`, `--strict-markers -m 'not campaign'`) is well designed: **every one
of the repo's 317 campaign-tier tests is a training test**, so the frozen campaign
machinery is fully off the default gate without being unmaintained (weekly CI job).

### G8 [VERIFIED] The freeze-header registry is exact

`training/README.md` §5 claims exactly 70 files carry the FROZEN header. The grep it
specifies returns exactly 70, and the per-directory breakdown (training 13, experiments
48, eval 6, scripts 2, engine 1) matches. Docs that assert a checkable invariant *and*
supply the check are unusual and worth naming.

### G9 [VERIFIED] The project's negative results survive independent probing

I stress-tested the NO-GO on the standalone decision arm across a 100× epoch range and a
300× lr range (n=96 held-out meetings, always-eject baseline 0.6250):

```
 epochs     lr  decision_acc  predicted_ejects    top1    top2  bar(>0.6250)
     50   0.30        0.3750                 0   0.833   0.917  fail
    300   0.30        0.3750                 0   0.767   0.917  fail      <- committed
   5000   0.30        0.3750                 0   0.783   0.933  fail
    300   0.03        0.3750                 0   0.833   0.917  fail
    300  10.00        0.4479                55   0.850   0.900  fail
   5000   3.00        0.4062                31   0.733   0.917  fail
```

The all-SKIP collapse is **structural**. The `surrogate_role="diagnostic-only"` ruling in
`training/README.md` §2a is correct and robust. Equally, the ranking channel's top-2 is
stable at 0.900–0.933 across the whole sweep, so the KEEP ruling on ranking is sound.

---

## 3. Findings, ranked

### F1 — P1 [VERIFIED, high confidence] `reconstruct_episode` reads a corrupted replay as a legitimate truncation

**File:** `training/rollout.py:653-663`

```python
    # Cross-check the winner against the recorded game_over row when present (the
    # reconstruction is authoritative; a mismatch is a corrupted replay).
    if (
        game_end is not None
        and not truncated          # <-- disables the check in exactly the case that needs it
        and game_end.winner is not None
        and game_end.winner != winner
    ):
        raise RolloutReconstructionError(...)
```

When the recorded `game_over` row declares a winner but the tick rows stop short of the
terminal tick, the reconstruction sets `winner = None → outcome = "TICK_BUDGET",
truncated = True`, and the `not truncated` guard then **suppresses** the cross-check that
would have caught the contradiction.

**Repro** (script:
`…/scratchpad/work/training-ml/trunc_repro.py`), on the committed corpus replay
`replays/ml_corpus/9p2i/replay-seed-1000.jsonl`:

```
BASELINE seed=1000: outcome=CREWMATES truncated=False complete=True winner=CREWMATES ticks=25
CORRUPT (last tick row dropped, game_over row kept): NO ERROR RAISED
   outcome=TICK_BUDGET truncated=True complete=False winner=None ticks=23
CORRUPT-10 (last 10 tick rows dropped): NO ERROR RAISED
   outcome=TICK_BUDGET truncated=True complete=False winner=None ticks=14
```

Every state hash still verifies (dropping *trailing* rows shortens the walk without
breaking the chain), so nothing else catches it.

**Why it matters.** The module's own docstring (`training/rollout.py:24-33`) promises
"silent truncation is structurally unreachable" and the comment at :656 says "a mismatch
is a corrupted replay". Neither holds. The reward channel does refuse to *score* it
(`complete=False` → `TruncatedEpisodeError`), so a fitness number is not directly
poisoned — but `_build_descriptors` is still called with `outcome="TICK_BUDGET"`, and any
consumer that counts truncations (bake-off budget accounting, QD descriptors, campaign
telemetry) treats file corruption as a legitimate game outcome. This is not purely
theoretical: `training/README.md` §6 item 5 records a known **recorder lock-race** at
`scripts/record_ml_corpus.sh:966-999` — concurrent writers to one replay file are exactly
the mechanism that produces this byte shape.

**Fix (one line):** drop `and not truncated`, and raise when
`game_end.winner is not None and (truncated or game_end.winner != winner)`.

### F2 — P1 [VERIFIED, high confidence] Zero production reachability, yet 39.8% of the repo's non-test Python

Whole-repo import-closure analysis (`…/scratchpad/work/training-ml/reach.py`, AST-based,
resolving to longest-matching module):

```
PROD closure (api / orchestrator / eval / agents / engine):   0 modules,     0 LOC
SCRIPTS only:                                                28 modules, 26,051 LOC
TESTS only:                                                   3 modules,  3,140 LOC
UNREACHABLE (package __init__ only):                          4 modules,    250 LOC
```

The one apparent counter-example — `eval/leak_test.py:687 import training.bakeoff.harness`
— is inside a **string literal** holding a subprocess script, not a real import. So the
claim is exact: **no production module imports `training/`.**

Repo Python LOC (`git ls-files`): engine 2,299 · observation 1,107 · agents 11,250 ·
meetings 8,673 · orchestrator 5,106 · llm 3,281 · eval 20,938 · api 5,122 · scripts
12,252 · **training 29,441 · experiments 16,802** — i.e. training + experiments =
46,243 of 116,271 non-test lines = **39.8%**, plus 26,070 lines of `tests/training`.

This is *architecturally correct* (training is a research tree; only its *product* — the
weights + the pure-Python forward pass — ships), and I would not want it coupled to
production. But the size/liveness ratio is the single biggest maintainability fact about
the area: two-fifths of the codebase, formally frozen, serving three module CLIs, one
verifier script, and its own tests. An outside engineer joining this repo pays the read
cost of 46k lines that cannot affect the running game.

### F3 — P1 [VERIFIED, high confidence] 5,163 lines whose only importer is their own test

```
$ grep -rn "training.scenarios" --include='*.py' .   # excluding self-references
tests/training/test_scenarios.py:53
$ grep -rn "training.anchor_study" --include='*.py' .
tests/training/test_anchor_study.py
tests/training/test_coevo_driver.py
```

| Module | Source LOC | Test LOC | Peak complexity |
|---|---|---|---|
| `training/scenarios.py` | 1,203 | 1,334 | `_validate_scenario_state` **F(59)** |
| `training/anchor_study.py` | 1,906 | 720 | `walk_corpus_game` **F(53)** |

`training/README.md` §6 item 12 already records that the scenario seam was **never
exercised by any campaign** (`scenario_labels: []` on both) — and I confirmed the string
`scenario_labels` does not appear anywhere in `training/artifacts/`. The tier map is
internally inconsistent here: `training/realpath.py` was **RETIRED** for exactly this
reason ("one-shot campaign ops surface … campaigns concluded"), while `scenarios.py` and
`anchor_study.py` were **FROZEN** on the same basis. An F(59) validator maintained
under mypy --strict, ruff, and a 1,334-line test file, for a seam no run ever used, is
the clearest deletion candidate in the area.

### F4 — P1 [VERIFIED, medium-high confidence] The corpus's `val` split is not a validation set for the three headline instruments

```
training/surrogate/ballots.py:938   fit_seeds = frozenset(table.splits.train) | frozenset(table.splits.val)
training/surrogate/ballots.py:777   fit_seeds = frozenset(table.splits.train) | frozenset(table.splits.val)
training/surrogate/fidelity.py:597  train      = frozenset(table.splits.train) | frozenset(table.splits.val)
training/conviction/dataset.py:376  fit_seeds  = frozenset(table.splits.train) | frozenset(table.splits.val)
```

The 3-way split (90/30/30 games on 9p2i) collapses to 2-way for the surrogate, the
conviction model, and the composed runner: `val` is folded into the fit side and there is
**no model-selection holdout**. (`val` *is* a genuine holdout for exactly one consumer,
`training/bakeoff/bc.py:126` via `load_val_seeds`, and for the mypy-excluded torch probe.)

Consequently `DEFAULT_EPOCHS = 300` / `DEFAULT_LEARNING_RATE = 0.3`
(`training/surrogate/ballots.py:135-136`, repeated verbatim at
`training/conviction/model.py:81-82`) have **no recorded selection basis**. I measured the
resulting band on the headline ranking number (fit = train ∪ val, score = the committed
test split, n = 60 ejection meetings):

```
 epochs     lr         top1         top2
     50   0.30   50/60 =  0.833   55/60 =  0.917
    100   0.30   50/60 =  0.833   55/60 =  0.917
    300   0.30   46/60 =  0.767   55/60 =  0.917    <- the committed setting, reproduces exactly
    600   0.30   46/60 =  0.767   55/60 =  0.917
   3000   0.30   46/60 =  0.767   55/60 =  0.917
    300   0.10   51/60 =  0.850   56/60 =  0.933
    300   3.00   46/60 =  0.767   55/60 =  0.917
```

To the project's credit the committed setting is the **worst** in the sweep — there is no
sign of tuning on test. But the reported `0.7667` carries an unreported **±8 pp**
hyperparameter band, on top of a Wilson-95% sampling interval of **[0.6456, 0.8556]**
(width 21 pp) at n = 60. The GO verdict does not flip (the bar is population-relative,
0.75 × the 0.850 honest ceiling = 0.6375, and every setting clears it), and F-G9 shows
the *negative* verdict is robust — so this is a reporting/methodology finding, not a
wrong conclusion. The repo's own `training/README.md` §7 pre-campaign check 1 says
precisely this: *"a point-estimate pass/fail at campaign n is not a decision."* The
already-published numbers should carry their intervals, and any re-open must use `val`
as a real selection holdout.

### F5 — P2 [VERIFIED, high confidence] ~240 lines of exact-duplicate logic across the firewall

Measured by AST-normalising every function body (docstrings stripped) and comparing
(`…/scratchpad/work/training-ml/dup.py`):

```
agents/tactical/learned/crew_forward.py vs training/crew/{options,scorer}.py + env.py
  byte-identical body in reference: 16 funcs / 144 normalized lines
  EXACT  enumerate_crew_options   111 lines   (crew_forward.py:275 == crew/options.py:282)

agents/tactical/learned/forward.py vs training/bakeoff/utility_es.py + env.py
  EXACT  6 funcs / 21 lines
  enumerate_options (74 lines) differs by exactly ONE statement: `del sabotage_kinds`
```

So both learned surfaces are effectively verbatim ports, and `enumerate_crew_options`
carries **F(54)** cyclomatic complexity in *both* copies. The firewall makes this
unavoidable and G4's bit-exact gate makes it *safe*, but it is still two 111-line
F(54) functions that must be edited in lockstep forever. The gate catches divergence only
on branches the 8-seed stream actually reaches (see F7).

### F6 — P2 [VERIFIED, high confidence] God classes and God modules

```
training/coevo/driver.py::_CampaignEngine   875 lines, 15 methods   (file: 2,274)
training/coevo/hall_of_fame.py::HallOfFame  786 lines, 17 methods   (file: 1,978)
training/bakeoff/harness.py                 2,302 lines: seed loading + agent factory +
      conviction fitness bundling + prescreen + artifact IO + candidate evaluation +
      Goodhart rerun + a CLI main
training/bakeoff/goodhart.py                2,243 lines
training/crew/scorer.py                     1,945 lines
```

Radon C-and-worse hotspots in the area include `scenarios.py::_validate_scenario_state`
**F(59)**, `anchor_study.py::walk_corpus_game` **F(53)**, `crew/options.py::enumerate_crew_options`
**F(54)**, `bakeoff/utility_es.py::enumerate_options` **E(37)**,
`env.py::build_action_mask` **E(31)**, `rollout.py::reconstruct_episode` **E(31)**.
Three of the six worst live in modules that are frozen or test-only.

### F7 — P2 [VERIFIED, high confidence] The mask property test never reaches the non-gating-sabotage branch

`build_action_mask` gates crew `do_task` on `not (sabotage_active and sabotage_is_gating)`
(`training/env.py:281-285`). The canonical map has two sabotages —
`lights (gates_tasks=False)` and `reactor (gates_tasks=True)`. Instrumenting the property
test's 8 seeds:

```
packets 1644 | in_vent 24 | sabotage_active 44 | gating_sabotage 44 | emerg_spent 23
```

`gating_sabotage == sabotage_active`, i.e. **only `reactor` was ever sabotaged**; the
`lights` branch is never exercised. The dedicated sabotage test
(`tests/training/test_env.py:505`) also uses only `reactor`. In-vent coverage is likewise
thin (24 of 1,644 packets, 1.5%).

I probed the uncovered branch directly (`…/scratchpad/work/training-ml/lights_mask.py`):

```
sabotage=lights   gates_tasks=False  legal=  55 illegal= 111  mismatches=0
sabotage=reactor  gates_tasks=True   legal=  54 illegal= 112  mismatches=0
```

**No bug** — the mask is correct on both branches (the extra legal action under `lights`
is exactly the crew `do_task` that stays legal). This is a coverage gap in a mirror that
must track engine legality, not a defect. A cheap fix: parametrise the existing sabotage
test over `game_map.sabotages` instead of hard-coding `"reactor"`.

### F8 — P2 [JUDGMENT, high confidence] Doc/behaviour drift

- `agents/tactical/features.py:23`: *"`numpy` is confined to `training/` by an
  **import-linter contract**"*. **No such contract exists.** `.importlinter` has five
  contracts (agents↛engine, agents↛training, agents↛meetings.manager, observation↛{agents,
  meetings,llm}); none mentions numpy. The real enforcement is an AST **source scan**
  (`tests/test_firewall.py:118`) — which the test's own comment at :85-89 correctly
  describes as *"not an import-linter contract"*, contradicting the module docstring it
  is paraphrasing. The mechanism is fine; the claim in `features.py` is wrong.
- `training/surrogate/ballots.py:339` and `:495`: *"ridge-solved linear head"* /
  `"""Ridge-solve the confidence head"""`. The implementation is
  `gram = design.T @ design + 1e-8 * np.eye(...)` — a conditioning epsilon eight orders of
  magnitude below any regularising scale, i.e. plain OLS. `training/conviction/model.py:84`
  is honest about the identical construct ("the same numerically-stabilizing epsilon").
  Make `ballots.py` say the same thing.
- `training/rewards.py:19-45`: the module docstring documents at length that a prior
  policy-invariance claim was **mathematically FALSE** and that the finding is
  *"DOCUMENTED, NOT REPAIRED"*. This is admirable honesty, but it means the live shaping
  term carries a real +1-per-kill / +1-per-completed-task incentive that a reader could
  easily mistake for a wash. Worth a one-line warning at `_side_potential` itself
  (currently only in the module header and a long paragraph at :100-114).

### F9 — P2 [VERIFIED, medium confidence] Dead single-valued-enum scaffolding

After Task 19.19 retired `first_meeting`, `EpisodeBoundary` is a one-element `Literal`
that still carries a derived `frozenset`, a bespoke validator, a custom error message, an
`__all__` export, a dataclass field, and a keyword parameter threaded through two modules:

```
training/rollout.py:73  EpisodeBoundary: TypeAlias = Literal["full_game"]
training/rollout.py:76  _VALID_EPISODE_BOUNDARIES = frozenset(get_args(EpisodeBoundary))
training/rollout.py:79  def _validate_episode_boundary(...)          # 11 lines + docstring
training/rollout.py:252, :474, :502, :681, :698
training/env.py:114, :122, :578, :588
```

`training/env.py:122` additionally imports the **private** `_validate_episode_boundary`
across a module boundary. Roughly 30 lines of live scaffolding that can only ever take
one value, plus a dedicated test (`test_env_rejects_unknown_episode_boundary`).

### F10 — P2 [VERIFIED, medium confidence] Cross-package private imports

```
training/env.py:111            from orchestrator.replay import WinnerSide, _state_hash
training/rollout.py:65         from orchestrator.replay import ... _state_hash
training/anchor_study.py:94    ... _state_hash
training/anchor_study.py:126   from training.rollout import _meeting_result_from_entry
training/surrogate/dataset.py:126  from eval.funnel import _walk_game_vj
training/crew/options.py:83,87 from agents.tactical... import _seen_victim_ids, _episodic_last_seen
training/env.py:120-122        from training.rollout import _build_descriptors, _frame, _validate_episode_boundary
```

Eleven `_`-prefixed names cross package boundaries. Each is a de-facto public API without
the stability contract, and `orchestrator.replay._state_hash` is load-bearing for the
replay-verification promise. Promote the four or five that are genuinely shared
(`_state_hash` above all) to public names.

### F11 — P2 [JUDGMENT, medium confidence] Tests that pin structure rather than behaviour

`tests/training/test_bakeoff_harness.py:1742-1772` parses `harness.py`'s AST and asserts
every `load_surrogate_runner_factory` call site passes a `corpus_dir=` keyword. Similar
AST pins at `test_bakeoff_harness.py:182/215`, `test_conviction_model.py:158`,
`test_crew_scorer.py:299`. The intent is sound (the fence is opt-in by keyword), but the
test passes/fails on *syntax*: `f(**kwargs)` or a thin wrapper defeats it while preserving
the behaviour, and a pure rename breaks it while preserving the behaviour. A behavioural
test — hand the harness a stale corpus and assert it raises — would be both stronger and
refactor-stable. Also 28 test reaches into `._inner` and ~90 other private-attribute
accesses across `tests/training/`.

### F12 — P2 [VERIFIED, high confidence] Documentation bulk

```
TOTALS (training/ + experiments/ + agents/tactical/learned/):
  total 48,899 | blank 5,425 | comment 3,331 | docstring 9,737 | code 30,406
  doc+comment share of non-blank lines: 30.1%
```

`training/bakeoff/es.py` is **45.0%** docs (253 code lines, 296 doc/comment lines); nine
more files exceed 30%. Embedded provenance references (`Task N.M`, `audits/*.md`,
`PR #N`, `tasks/phase-N.md`): **441 in source, 198 in tests = 639**, led by
`coevo/driver.py` (49) and `coevo/hall_of_fame.py` (40).

This cuts both ways and I want to be fair: the density is *why* I could verify so many
claims quickly, and the ES docstring is a model of how to justify an unusual numerics
decision. But a lot of it is history narration ("Until Task 19.3 this module claimed…",
"the previous value was e3b67c69…", "PR #240's review finding") that belongs in
`audits/` and git history, not in a module header — and it welds every file to a phase/task
numbering scheme that will be opaque in a year.

---

## 4. Architecture & design assessment

**Well designed.**

- *The determinism spine.* One shared, audited ES core (`bakeoff/es.py`) that every
  entrant rides — `mutate_genome`, `random_genome`, `derive_stream_seed` are exported so
  MAP-Elites and BC do not re-implement the operator. `derive_stream_seed` deliberately
  uses a **different payload scheme** (`"stream:"` prefix) from the internal `_derive_seed`
  so the committed digests can never be pressured by a new caller (`es.py:517-532`). That
  is exactly the right instinct.
- *The layered evidence architecture.* raw replays → hash-verified reconstruction
  (`rollout.py`) → typed table (`surrogate/dataset.py`) → model (`ballots.py`) → fidelity
  harness (`fidelity.py`) → committed verdict JSON → `verify_ml_evidence.py`. Each layer
  is independently re-runnable over committed bytes. This is better than most industrial
  ML pipelines.
- *The firewall + parity-gate pattern.* Duplication forced by an architectural constraint,
  neutralised by a bit-exact cross-implementation gate rather than by trust.
- *Fail-loud everywhere.* `_finite_fitness` refuses NaN/inf before it can corrupt a
  champion trace (`es.py:500-514`); `ESConfig` refuses duplicate `fitness_seeds` with a
  reason ("the stated K-seed budget would be a lie"); `_validate_prediction` refuses a
  non-permutation ranking before computing meaningless top-k. Consistent and principled.

**Accidental complexity.**

- The frozen-but-retained tier (F3): `scenarios.py` and `anchor_study.py` are 5,163 lines
  of source+test kept alive by mypy, ruff and a full test file for zero consumers.
- `bakeoff/harness.py` and `coevo/driver.py` as single-file kitchens (F6). `harness.py`
  mixes split loading, agent construction, conviction bundling, prescreening, artifact IO,
  evaluation, a Goodhart rerun, and a CLI. The natural seams are obvious and unused.
- Defensive validators for impossible states (F9): a one-element enum with a runtime
  validator; `ActionMask` distinguishing `engine_legal` / `submission_only` / `illegal`
  where `submission_only` has exactly one member (the impostor pretend-task) hard-coded in
  a branch.
- Provenance narration in code (F12).

**Optimizer methodology, from an outside ML engineer's chair.** The optimizer is a
`(1 + λ)` hill-climber with fixed σ, no antithetic sampling, no rank-normalisation, no
step-size adaptation, and no gradient estimate — i.e. *not* OpenAI-ES despite the "ES"
name. At the genome dimensionalities actually in play (utility 19, crew 22, owned-task 27,
Goodhart probe 66) this is a defensible choice and the elitist lexical tie-break buys real
reproducibility. But the docstrings should say "(1+λ) elitist hill-climber" rather than
lean on "evolution strategy", and mirrored sampling would halve the gradient variance for
one line of code if the program ever re-opens. The K-seed averaging via `math.fsum`
(`es.py:184`) is the right call for order-stability.

**What I would refactor, in order.**

1. Delete `training/scenarios.py` + `training/anchor_study.py` + their tests (−5,163
   lines), recording the finding text in `training/README.md` §3 as the tier map already
   does for other results. Consistent with the `realpath.py` precedent.
2. Split `bakeoff/harness.py` into `harness/{seeds,factory,conviction,evaluate,cli}.py`
   and lift `_CampaignEngine`'s 15 methods into 3–4 collaborators (plan/execute/persist).
3. Fix F1; promote the five cross-package privates (F10); collapse `EpisodeBoundary` (F9).
4. Move history narration out of module headers into `audits/`, keeping only the
   *mechanism* paragraphs (the `_ln`/AS241 justification is exactly what should stay).

---

## 5. Test assessment

**Cost — well managed.** Load recorded at each run.

| Tier | Tests | Wall | Load |
|---|---|---|---|
| `tests/training` default | 384 passed, 317 deselected | 104 s | 7.01 |
| `tests/training -m campaign` | 317 passed | 127 s | 5.72 |
| `mypy training agents/tactical/learned` | 40 files clean | <1 s | 5.29 |
| `verify_ml_evidence.py --fast` | 54 checks, 0 fail | 20 s | 4.59 |

Repo-wide: 4,961 tests, 4,644 default / 317 campaign. **All 317 campaign-tier tests are
training tests**, so the frozen machinery is fully off the fast gate. Slowest single test
is 29 s (`test_evaluate_crew_candidate_full_row`, campaign tier). No test in the area is
unreasonably expensive.

**Quality — mostly high.**

- *Excellent:* the bit-exact parity gates (G4), the two-sided mask property test (G5),
  the by-game-CV leakage test (`test_by_game_cv_never_splits_a_games_meetings_across_folds`),
  the label-poisoning fence, the determinism double-runs (identical decision stream **and**
  identical state-hash chain), the ES golden with a comment that tells a future reader
  *"if this pin ever trips WITHOUT such a documented change, the ES core drifted:
  investigate, do not re-pin."*
- *Golden constants are used sparingly and correctly:* 11 sha-256 literals across
  `tests/training/`, **zero** bare `== 0.xxxxxx` float pins — the reported numbers are
  compared through the verifier against committed verdict JSON instead.
- *Weaknesses:* the AST structure pins (F11); ~90 private-attribute reaches; the
  non-gating-sabotage and in-vent coverage gaps (F7); 26,070 test lines to 29,441 source
  lines is a ~0.9 ratio that is fine in absolute terms but is being paid for frozen code.

---

## 6. Recommendations (prioritised)

1. **Fix F1** (`training/rollout.py:653-663`): raise when a `game_over` row names a winner
   but the reconstruction found none. One line; closes a silent-corruption path that the
   known recorder lock-race can actually produce. Add a regression test using the
   drop-trailing-rows repro.
2. **Record the Darwin-arm64 ES result** (G1) in `training/bakeoff/es.py:52-58` and
   `tests/training/test_es.py:118-127`, and upgrade the module's second reproducibility
   scope from "designed-for, not yet confirmed" to confirmed on two platforms. The repo
   explicitly asks for this; it is now free.
3. **Retire `training/scenarios.py` and `training/anchor_study.py` with their tests**
   (−5,163 lines, incl. the two worst complexity functions in the area). Apply the same
   rule the tier map applied to `realpath.py`; preserve the findings in
   `training/README.md` §3.
4. **Publish intervals with the frozen numbers** (F4). Add Wilson bounds to
   `report-ballot-surrogate.md` / `report-conviction-model.md` (top-1 46/60 = 0.767,
   95% CI [0.646, 0.856]) and note the ±8 pp hyperparameter band. Cheap, and it
   pre-satisfies `training/README.md` §7 pre-campaign check 1. If the program re-opens,
   use `val` as a real selection holdout rather than folding it into the fit.
5. **Fix the three doc/behaviour drifts** (F8): the non-existent numpy import-linter
   contract in `agents/tactical/features.py:23`; "ridge-solved" → "OLS with a conditioning
   epsilon" in `training/surrogate/ballots.py:339,495`; a one-line warning at
   `training/rewards.py::_side_potential`.
6. **Parametrise the sabotage tests over `game_map.sabotages`** and add in-vent /
   emergency-spent states to the mask property seeds (F7). ~10 lines, closes a real
   coverage hole in a legality mirror.
7. **Split `bakeoff/harness.py` and `coevo/driver.py::_CampaignEngine`** (F6) *if* the
   program ever re-opens; otherwise leave them — refactoring frozen code buys nothing.
8. **Replace the AST call-site pins with behavioural equivalents** (F11), starting with
   the `corpus_dir` fingerprint fence: construct a stale corpus and assert it raises.

---

## Appendix — scratch artifacts

All under
`/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/training-ml/`:

- `density.py` — docstring/comment density measurement (F12)
- `dup.py`, `diffbody.py` — AST-normalised cross-firewall duplication measurement (F5)
- `reach.py` — whole-repo import-closure reachability (F2)
- `mask_cov.py` — mask property-test state coverage (F7, G5)
- `lights_mask.py` — direct probe of the uncovered non-gating-sabotage branch (F7)
- `trunc_repro.py` — truncated-replay repro (F1)
- `epoch_sens.py`, `decision_sens.py` — surrogate hyperparameter sensitivity (F4, G9)

Nothing in the repository was created, edited, staged or committed; no network call was
made; no real-provider LLM call was made.
