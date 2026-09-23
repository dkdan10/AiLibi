# Environment: which re-ground steps reproduce on this Mac, and which need Linux x86-64

Investigator memo for `tasks/work/ml-reground-baseline-9.md` (Q3).

**Ground rules followed.**
- Read-only: no commit, no push, no tracked edit. `git status --short` was empty after every run.
- Nothing under `training/artifacts/` was written.
- Every output went to
  `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/cd3daac2-c664-44ef-918c-024def8b33b9/scratchpad/envinv/`,
  called `$SCR` below.
- No provider call, no `.env`, no `--complete`, no recorder, no held-out generator.
- Citations are at `95fb894b` unless marked.

**Host.**
- Darwin 24.6.0 arm64: Apple T6000, 10 cores, 16 GB, macOS 15.7.3.
- uv 0.11.7, CPython 3.11.15, numpy 2.2.6. numpy's BLAS/LAPACK is Apple Accelerate (NEON).
- Other workflow agents were running pytest on the same host, with a load average of 18-22
  on 10 cores. Every wall time below is an upper bound.

**Linux reference.**
- GitHub Actions `ubuntu-latest`, which is ubuntu-24.04 x86-64 with CPython 3.11.16
  (`.github/workflows/ci.yml:18`, `:54`; `.github/workflows/campaign-tier.yml:28`, `:37`, `:64`).
- Read with `gh run view` (read-only) on three runs:
  - 35685443068: CI at `39a568c6`;
  - 35841706125: CI at `95fb894b`;
  - 35601542266: campaign tier at `0a1100ea`.

## Bottom line

**At `39a568c6`, every re-ground step reproduced on this macOS arm64 host:**
- the three GD fits, byte for byte;
- the composed Goodhart leg, cell for cell;
- the pool re-stamp, byte for byte;
- the campaign tier, at its 335 passed;
- the default tier, on every test that does not need a git index.

**At `95fb894b` this host matches Linux and the card:**
- this host and Linux CI fail on the identical 50 default-tier ids;
- this host reproduces the card's campaign count (308 passed, 25 failed, 2 errors);
- it also reproduces the card's verifier count (FAIL 12).

Nothing under `training/`, `uv.lock` or `pyproject.toml` changed between `39a568c6` and
`95fb894b` (`git diff --stat` is empty). So the head runs the same code that reproduced.

**Recommendation.**
- Run the whole card on this Mac, and name the platform beside every new digest.
- Take the Linux x86-64 confirmation from GitHub Actions, in two parts:
  - the PR's own `check.sh` run;
  - a `workflow_dispatch` of the campaign tier on the work branch.
- This needs no web session, and nothing has to be handed back.
- Use a Claude Code web session only for an optional, read-only Linux cross-check of the
  full-budget Goodhart leg and of GD byte identity. It hands its result back as a proof branch.

## 1. The three GD fits at `39a568c6` (baseline-8 corpus)

**Setup.**
- `git archive 39a568c6`, unpacked in `$SCR/b8`.
- `uv sync --frozen --offline` there took 0.14 s, from the wheel cache.
- `historical_fit_corpus_fingerprint` reads `cc54d3c0...` (1.5 s).

**Verifier subset.** `verify_ml_evidence.py --only sidecars --only corpus --only recompute`
took 22.0 s:
- exit 0; 28 checks: OK 22, FAIL 0, ABSENT 6.
- The six ABSENT rows are the evidence-branch rows and the git-index inventory row, which an
  archive cannot have.
- Every recompute row, both weight hashes and both adoption constraints read OK.

| fit | refit sha256 | committed | bytes | float params equal | wall |
|---|---|---|---|---|---|
| surrogate `ballot-predictor.json` | `06b20508...` | `06b20508...` | identical | 37/37 exact | 3.6 s |
| conviction `conviction-model.json` | `7e764b89...` | `7e764b89...` | identical | 51/51 exact | 11.5 s |
| filtered-BC anchor `weights.json` | `62595367...` | `62595367...` | identical | 19/19 exact | 4.5 s |

**The anchor's `config.json` differs, in the stamp only.** The fit-only run walks all 150
games.
- The run at `39a568c6` writes the version-two stamp: `substrate_sha_kind:
  compute_substrate_sha.v2`, value `7d912e4b...`.
- The committed file carries the historical `c845602d...`, with no kind field.
- This is the Q1 stamp-shape question, not an environment question. The weights are the same
  bytes.

**This host qualifies under the card's own rule.**
- The platform caveat says byte identity holds only on the producing platform
  (`training/conviction/model.py:18-22`, `training/anchor_study.py:51-58`).
- This host reproduces the bytes.
- The card's rule: "each step runs where its reproduction reproduced the committed output"
  (`tasks/work/ml-reground-baseline-9.md:223-225`).
- The fallback to `1793eb23` was not needed.

**Linux.**
- CI at `39a568c6` passed: 8249 passed, 35 skipped, 901.9 s.
- That run includes the default-tier round-trip pins
  (`tests/training/test_surrogate_runner.py:809-880`,
  `tests/training/test_conviction_model.py:803-855`). They re-fit on the live corpus and
  compare every parameter at `rel=1e-9, abs=1e-12`.
- So on Linux x86-64 the surrogate and conviction refits agree with the committed bytes to
  ULP.
- Unmeasured: whether Linux reproduces those two byte for byte, and anything at all about the
  anchor on Linux (no test re-fits it).

**Perturbed proof on this host** (at `95fb894b`, baseline-9 corpus, outputs in scratch):

| fit | refit sha256 | parameters equal to committed | wall |
|---|---|---|---|
| surrogate | `f8901620...` | 9/37 | 4.3 s |
| conviction | `3a6fe4ca...` | 1/51 | 12.8 s |
| anchor | `d6b3f3a7...` | 1/19 | 5.0 s |

None matches, and no walk refused. The anchor probe ran at the unchanged floor 147/151, so
`d6b3f3a7...` is not the card's final anchor.

## 2. The ES pins and the tests on ES-derived artifacts

| run | this host | Linux x86-64 |
|---|---|---|
| `tests/training/test_es.py` at `95fb894b` | 18 passed (1.9 s), including `test_evolve_is_deterministic_and_hash_pinned` (digest `e72e24fe...`) | green in CI |
| `pytest -m campaign` at `39a568c6` | **335 passed** (204.9 s) | 335 passed at `0a1100ea` (400.0 s) |
| default tier at `39a568c6` (archive) | 8236 passed, 15 failed, 33 skipped (224.4 s, 10 workers) | 8249 passed, 35 skipped |
| default tier at `95fb894b` | 41 failed + 9 errors, 8246 passed (296.8 s) | 41 failed + 9 errors, 8231 passed (759.1 s, 4 workers) |
| `pytest -m campaign` at `95fb894b` | 308 passed, 25 failed, 2 errors (100.2 s) | not run since the merge |

**The 15 failures at `39a568c6` are archive artifacts, not platform failures.** Each raises
"not a git repository", because the archive has no index. The failing tests:
- `test_firewall.py` (3 cases);
- `test_verify_ml_evidence.py` (9 git-inventory cases);
- `test_env_hermeticity.py::test_every_import_time_env_read_is_an_allow_listed_gate`;
- `tests/orchestrator/test_replay.py::TestSubstrateStampMismatches::test_every_committed_stamp_is_a_clean_subset_of_this_build`;
- `test_fresh_deduction_instrument.py::TestLiveGate::test_no_committed_file_outside_the_module_and_the_manifest_names_the_flag`.

A detached worktree would have run them, but adding one writes worktree metadata into the
repository, so no worktree was made.

**At `95fb894b` the red sets are identical.** `comm` of this host's 50 failing ids against
CI's 50 is empty in both directions. That includes the nine non-ML reds, so they are not
platform artifacts:
- `test_reported_testimony`;
- `test_view_model`;
- `test_evidence_honesty` (2 cases);
- `test_contradictions` (2 cases);
- `test_transcript`;
- `test_counterfactual_phase21` (2 cases).

**The ES hash pin now has its Darwin-arm64 confirmation.**
- The pin `e72e24fe...` was written by a web session on Linux: PR #329, branch
  `claude/es-portability-sampler-4uvnv4`. It passes here.
- `training/bakeoff/es.py:52-58`, `tests/training/test_es.py:117-127` and `README.md:98` are
  still waiting for this confirmation ("Record the result here when it happens").
- Recording it is a docs change outside this card.

**Every other pin on an ES-derived artifact is a file read, not a re-run:**
- `test_committed_lambda_1_artifact_reproduces_the_champion_byte_for_byte`
  (`tests/training/test_anchor_study.py:737-740`);
- `test_rerun_rows_match_the_committed_artifact_digests`
  (`tests/training/test_bakeoff_harness.py:746`);
- the pool index pins.

The ES re-runs inside the tiers (the CI-budget runs) are green here at `39a568c6`.

**One stored belief is stale.**
- The memory note `project_es_artifacts_platform_split` (2026-07-21) records `test_es` red on
  macOS, with the old digest `e3b67c69...`.
- That note predates Task 19.3's libm-free sampler (`training/bakeoff/es.py:84-92`), which
  moved the golden digest.
- Since then the pin passes on Darwin arm64: at `87c6abfe` (per the card), and here at
  `95fb894b`.

## 3. The composed Goodhart leg and the pool re-stamp at `39a568c6` (30-minute boxes)

### Goodhart leg

The leg ran as in `report-composed-runner.md` section 9, with `evidence_scope='historical'`.
It finished in **45.4 s**. Two runs wrote byte-identical JSON (sha256 `bddf96d5...`).

Every committed figure in sections 6.1, 6.2 and 6.4 reproduces
(`training/reports/report-composed-runner.md:208-313`):
- **Verdict:** HELD, no blockers, no findings.
- **Scores:** baseline mean 3.42, ES champion 0.65, relative gain -0.8102.
- **Lever score gains:** emergency +0.1423, report +0.0474, wait -0.9708, kill +0.1204,
  sabotage -0.1058.

The seven arms of section 6.2 reproduce in full:

| arm | meetings | predicted-supply gain | predicted flags/meeting | converting share |
|---|---|---|---|---|
| scripted-FSM baseline | 23 | 0 | 0.8523 | 0.4783 |
| forced-emergency | 39 | +0.0171 | 0.8399 | 0.3333 |
| forced-report | 32 | -0.5091 | 0.4212 | 0.0312 |
| forced-wait | 0 | -1.0 | 0 | 0 |
| forced-kill | 24 | -0.37 | 0.4812 | 0.375 |
| forced-sabotage | 23 | +0.0326 | 0.8386 | 0.4348 |
| ES champion | 28 | -0.0268 | 0.8057 | 0.0714 |

In addition:
- Recorded flags are 0.0 in every arm, and `validity_passed` is False in every arm. These are
  the facts behind both adoption constraints.
- The counters reproduce: 1175 composed meetings; conviction 1513 = 1175 + 338; surrogate
  1175.

The run's `es_digest` is `00d2c414...`. No committed file records the composed leg's digest
(`grep` finds none), so a digest comparison is not possible; the committed record is the
cells.

**Why the leg is portable at this budget.**
- The fitness trace is `-1.0` in all seven generations, and the leg records no improvements.
- On the composed path every arm fails the validity gate, so every genome scores
  `_INVALID_FITNESS = -1.0` (`training/bakeoff/goodhart.py:289-293`, `:308-326`).
- A champion is displaced only by a strict improvement. So the champion stays the seed-0
  initial genome, drawn by the portable sampler.
- The card gives "one ULP gives another champion" as its reason for the container
  (`tasks/work/ml-reground-baseline-9.md:231`). That mechanism cannot act while the gate
  fails structurally. The gate fails because a zero-LLM meeting path carries model=None
  (report section 6.3).
- The remaining platform exposure is numpy inference in the arm reads, which the report
  gives to four decimals.

### Pool re-stamp

The two-field re-stamp was done in the historical shape:
- `baseline_id` = `BAKEOFF_BASELINE_ID`;
- `substrate.substrate_sha256` = `historical_bakeoff_substrate_sha()`;
- serialized by `json.dumps(index, indent=2, sort_keys=True) + "\n"`, as the writer does
  (`training/bakeoff/map_elites.py:711-730`, `:887-889`).

Results:
- Written to scratch in 0.014 s (1.1 s including interpreter start).
- It reproduces the committed `index.json` byte for byte (sha256 `e43335ba...`), with 30
  cells, all 30 filled.
- `4a25ccdf...` is the sha256 of the corpus MANIFEST (baseline 8).
- It is idempotent and platform-free by construction.
- The version-two value, which was not written, would be `3c5dd239...`.

## 4. How earlier ML steps ran: the recorded environment

**No platform is named anywhere in the 21.17 record or the artifacts.** That covers the
reports, the artifacts, the 21.17 commit messages and the PR #413 body.
- The version-two identity binds the Python minor version and the numpy and pydantic
  versions (`training/provenance.py:108-136`).
- It does not bind the OS, the architecture or the BLAS, so a Linux fit and a macOS fit
  carry the same v2 fingerprint.

**Web sessions leave a signature.** 862 commits are authored and committed as `Claude
<noreply@anthropic.com>`, on `claude/*` branches. The last is dated 2026-08-18 (Task 19.28).

| PR | work | environment |
|---|---|---|
| #292 | anchor lambda sweep and genomes | web session |
| #294 | MAP-Elites pool cells | web session |
| #310 | composed runner's first leg | web session |
| #329 | ES sampler golden | web session |
| #302 | conviction model | local |
| #303 | (mixed commits) | mixed |

**Task 21.17 (PR #413, squash `1793eb23`) produced the committed baseline-8 fits, and it very
likely ran on this Mac.**
- It was authored under the local identity `danielkeinan@icloud.com`, the identity this
  host's git config uses.
- It ran on branch `phase-21-reground`, with author times 15:47-17:11 EDT.
- Its PR body says the pre-fit campaign run was taken on a `git stash`ed clean tree.
- Together with the byte-for-byte reproduction here, this makes 21.17 a local macOS run to a
  high likelihood. It is an inference: the tree does not record the platform.
- If it holds, the committed GD bytes and the section 6 Goodhart cells are Darwin-arm64
  ground truth. Requiring a Linux container for them would invert the card's rule.

**What ran on Linux:** the lambda sweep genomes and the MAP-Elites pool genomes (July, old
gauss sampler). This card re-searches neither, and their pins are file reads.

## 5. Exact commands and wall times (this host)

The wrapper `$SCR/timed.sh <tree> <label> <cmd...>` does four things:
- `cd`s to the tree;
- exports `PYTHONPATH=<tree>`;
- unsets `AILIBI_*`;
- logs to `$SCR/out/<label>.log` and `$SCR/out/timings.txt`.

The card's own `python -c` forms need none of it.

| step | tree | command | wall |
|---|---|---|---|
| env | b8 | `uv sync --frozen --offline` | 0.14 s |
| fingerprint | b8 | `uv run python $SCR/fp.py` (= card line 346) | 1.5 s |
| verifier subset | b8 | `uv run python scripts/verify_ml_evidence.py --only sidecars --only corpus --only recompute` | 22.0 s |
| surrogate refit | b8 | `uv run python $SCR/refit.py surrogate $SCR/out/refit_b8_surrogate` (= card line 348) | 3.6 s |
| conviction refit | b8 | `uv run python $SCR/refit.py conviction $SCR/out/refit_b8_conviction` (= card line 349) | 11.5 s |
| anchor refit | b8 | `uv run python $SCR/refit.py anchor $SCR/out/refit_b8_anchor` (= card line 350: `lambda_grid=()`, `verify_committed_champion=False`) | 4.5 s |
| Goodhart leg | b8 | `uv run python $SCR/goodhart.py $SCR/out/goodhart_b8.json historical` (= card line 352) | 45.4 s; repeat 46.3 s |
| pool re-stamp | b8 | `uv run python $SCR/pool_restamp.py $SCR/out/pool_b8/index.json` | 1.1 s |
| ES pin | head | `uv run pytest -p no:cacheprovider tests/training/test_es.py -q -rA` | 1.9 s |
| campaign | b8 | `uv run pytest -p no:cacheprovider -m campaign -q -rfE` | 206.4 s |
| default tier | b8 | `uv run pytest -p no:cacheprovider -n auto --dist loadfile -q -rfE` | 225.1 s |
| default tier | head | same | 297.4 s |
| campaign | head | same as campaign | 108.3 s |
| verifier full | head | `uv run python scripts/verify_ml_evidence.py` (61 checks: OK 37, FAIL 12, ABSENT 7, INFO 5, as the card) | 41.9 s |
| perturbed refits | head | `refit.py surrogate`, `conviction`, `anchor` | 4.3 / 12.8 / 5.0 s |

The whole reproduction block at `39a568c6` (fingerprint, verifier, three fits, leg, pool)
costs about 90 s here. The card budgets 60 minutes for it.

**Not attempted: the card's `docker run --platform linux/amd64` path** (`:234-239`).
- The Docker CLI is installed, but the daemon is not running.
- Starting Docker Desktop and pulling `ghcr.io/astral-sh/uv:python3.11-bookworm-slim` is a
  download, which needs the owner's permission.
- x86-64 emulation on arm64 is itself unproven.

## 6. Recommendation per step

| step | run where | proof |
|---|---|---|
| reproduction at `39a568c6` | this Mac | done above; re-run and quote in Results |
| surrogate, conviction, anchor refits on baseline 9 | this Mac, named `Darwin arm64 / macOS 15.7.3 / CPython 3.11.15 / numpy 2.2.6 (Accelerate)` | byte reproduction at `39a568c6`; the PR's CI round-trip pins re-check Linux ULP-equivalence automatically |
| composed fidelity, verdicts, walk, stamps, constants | this Mac | platform-free: frozen-weight inference, sha256, deterministic engine |
| composed Goodhart leg | this Mac | cells reproduce at `39a568c6`; optional Linux cross-check (section 7) |
| `pytest -m campaign` | this Mac (the gate), plus a Linux confirmation: `gh workflow run campaign-tier.yml --ref work/ml-reground-baseline-9` | 335 here at `39a568c6` = Linux's 335 |
| `bash scripts/check.sh` | this Mac in a clean worktree (the gate), plus the PR's CI `project-checks` job on ubuntu-24.04 x86-64 | identical 50-id red set on both platforms at `95fb894b` |

**Card edit for the implementer.** Several places say "in the container":
- the Environment table (`:227-239`);
- the acceptance lines `:131`, `:146`, `:212` and `:216-217`.

With the evidence above, they would instead read "where reproduction reproduced (this host),
confirmed on Linux by CI".

## 7. If a remote Linux session is used

Use a remote session for the optional cross-check, or if the owner still wants a leg produced
in a container.

### Step 1: prove the environment before any re-fit

1. **Stamp the host.** Run `git fetch origin && git checkout --detach 39a568c6 && uv sync --frozen`,
   then `uname -srm` and
   `uv run python -c "import platform,sys,numpy; print(platform.platform(), sys.version); numpy.show_config()"`.
2. **Run the card's reproduction lines** (`:345-352`). They must print `cc54d3c0...` and
   a verifier exit of 0.
3. **Check the three refit digests.** They must print `06b20508...`, `7e764b89...` and
   `62595367...`. Otherwise they must pass the two round-trip pins, and the report must say
   the bytes differ.
4. **Check the Goodhart leg.** It must print HELD with the section 6.2 cells. Compare its
   `es_digest` with this host's `00d2c414...`, and its JSON with `bddf96d5...`.
5. **Stop on a mismatch in the leg's cells.** Report it; do not re-run.

### Step 2: hand back by branch, never by paste

1. Write one JSON file containing the host stamp, the commit SHA, each command, each digest,
   and a match boolean per comparison.
2. Commit that file alone to `work/ml-reground-baseline-9-linux-proof`, with the card path in
   the commit body, and push.
3. The local session fetches the branch and checks the file's own sha256 against the commit.
   It then quotes the file in Results by commit SHA.
4. If the session also produced a card artifact:
   - it goes on the same branch, with its `.sha256` sidecar;
   - the local session re-verifies each sidecar first;
   - only then is the branch merged or fast-forwarded into the work branch, never squashed.

## 8. What stays unestablished

- **Linux byte identity of the three GD refits.** CI measures only ULP-level agreement, and
  only for two of them. The anchor has not been measured on Linux at all.
- **The Linux result of the full-budget composed Goodhart leg.** No test runs it; the campaign
  tier runs only the tiny-budget leg.
- **The platform 21.17 actually ran on.** This is a strong inference only.
- **Whether arm64 `docker run --platform linux/amd64` emulation reproduces anything.** The
  Docker daemon is down, and this was not attempted.
- **The 15 git-index tests at `39a568c6` on this host.** The archive has no index. At
  `95fb894b` they pass here and are not in the red set.
