# Recorded training-campaign invocations

The eight harness scripts that launched the crew co-evolution campaign,
rewritten to run from the repository root, with the three preconditions they
now need. This text moved here unchanged from section 8 of
[`training/README.md`](../../training/README.md), and its section numbers (§2,
§7) refer to that file. The program it records is written up in
[docs/ml-program.md](../../docs/ml-program.md).

## 8. APPENDIX — the recorded campaign invocations, repo-relative (Task 19.23)

The 18.25 crew campaign was launched from eight operator-authored harness
scripts, preserved as provenance (home directory shortened to `~`) under
`training/artifacts/coevo/provenance/harnesses/`. They are the record of what
actually ran, and they are **not runnable as written**: every one of them opens
with the same three lines —

```python
_REPO = "~/projects/AiLibi"
os.chdir(_REPO)
sys.path.insert(0, _REPO)
```

— so the invocation only ever existed as folklore about one machine's home
directory (`provenance/harnesses/harness_run_c1.py.txt:11`). That `_REPO` literal
opens all eight; every one of them then derives a `REPO = Path(…)` from it (the
two `run-c1` files repeat the literal a second time, the other six spell it
`Path(_REPO)`), and the four campaign harnesses add an operator `CAMPAIGN_ROOT`
beside it. This appendix rewrites them **repo-relative**, so the exact
configuration survives the machine it was typed on. What it replaces is the
FOLKLORE, not the files: every provenance file stays where it is and stays the
record, and each is cited by name below beside the invocation that reproduces
it.

**Read this as a record, not an invitation.** The co-evolution machinery is
FROZEN (§2 FREEZE) and the program stays frozen: §7 is the only door back in,
and it needs an owner decision against a concrete proposal. Nothing here is a
campaign anyone should start.

**Three preconditions, stated because two of them changed after these runs.**

1. **Run from the repository root.** The `os.chdir` / `sys.path.insert` pair is
   replaced by the working directory itself. The forms below are written for
   `uv run python -` reading the script on **stdin**, because that puts the
   working directory (not a script's own directory) on `sys.path`.
2. **`training/realpath.py` is RETIRED** (Task 19.19, commit `4e8d533`), so the
   four **real-path leg** scripts below **do not import at HEAD**. Their
   configuration is recorded exactly as it ran; the module they call is in git
   history (`git show 4e8d533^:training/realpath.py`). This is stated rather
   than quietly omitted — the leg invocation is evidence about a concluded
   campaign, not a working entry point.
3. **The leg slates read hall artifacts the prune moved.** Each leg names a
   `gen-3` swap champion under `training/artifacts/coevo/<run>/crew/gen-3/…`,
   which Task 19.22 moved to the pinned evidence commit (the `gen-9` champions
   stayed in-tree — `EVIDENCE-MANIFEST.md` §3). `bash scripts/fetch_evidence.sh`
   restores them. Verify the whole picture — hashes, corpus, recomputation,
   availability — with `uv run python scripts/verify_ml_evidence.py`.

**The substrate fence still holds — on the four harnesses that carry it.** The
**campaign** harnesses (§8.1) each assert
`compute_substrate_sha().startswith("9bc00af0")` — the 18.24 composite the seed
was trained at, so that a moved substrate makes the seed re-run-before-use
rather than a config edit. The **four real-path leg scripts (§8.2) contain no
such assertion**: none of them imports `compute_substrate_sha`, so the legs ran
with no substrate fence of their own and inherited only whatever the campaign
that produced their candidates had checked. That is recorded rather than
smoothed over — it is a property of the evidence, not of this appendix.
Recomputed at this HEAD:

```
uv run python -c "from training.anchor_study import compute_substrate_sha; print(compute_substrate_sha())"
9bc00af0f9e76719cb78d66c5593ec178312716528715f4a580677fb519f04f4
```

### 8.1 The four campaign harnesses (fake-path, `$0`, deterministic)

The repo-relative form of `provenance/harnesses/harness_run_c1.py.txt`,
`harness_run_c1_ablation.py.txt`, `harness_run_c2.py.txt` and
`harness_run_c2_ablation.py.txt`. One body, four parameter sets — the recorded
files differ only in the rows of the table below. (`harness_run_c1_ablation`
carries `run_c1`'s docstring unedited; the run name and `conviction=None` are
what actually distinguish it. Recorded here rather than corrected there —
provenance files are records.)

```python
# uv run python - <<'PY'   (from the repository root)
from pathlib import Path

from training.anchor_study import compute_substrate_sha
from training.bakeoff.harness import load_candidate_weights, load_conviction_fitness_term
from training.bakeoff.utility_es import build_utility_scorer_policy
from training.coevo.driver import CoevoCampaignConfig, CoevoSideConfig, run_alternating_freeze
from training.crew.options import OwnedTaskOptionBasis
from training.crew.scorer import build_crew_scorer

REPO = Path.cwd()                       # was "~/projects/AiLibi"
CAMPAIGN_ROOT = Path("/tmp/ailibi-campaign-1825")   # operator scratch root, outside
                                        # the tree by convention (docs/artifacts.md,
                                        # class REPO-EXTERNAL) — was
                                        # "~/ailibi-campaign-1825"

# --- the row from the table below -----------------------------------------
RUN_NAME = "run-c1-crew-owned-tasks"
MASTER_SEED = 182501
CREW_SEED_ARTIFACT = REPO / "training/artifacts/crew/crew-owned-tasks-es"
CREW_GENOME_LENGTH = 27
CREW_ENCODER = "crew-option-features-v2"
CREW_BASIS = OwnedTaskOptionBasis()     # None on the run-c2 rows
USE_CONVICTION_TERM = True              # False on the two ablation rows
# ---------------------------------------------------------------------------

# The 18.24 hand-off seed (finalist 1a, pooled 6/6), re-frozen as a fresh lineage
# in this campaign's own hall by the driver's swap-boundary freeze. Retained
# in-tree by the 19.22 prune (EVIDENCE-MANIFEST.md §3).
SEED_ARTIFACT = (
    REPO
    / "training/artifacts/coevo/intermediates/run-02-utility-lambda4/gen-2"
    / "ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f"
)

composite = compute_substrate_sha()
# Stale-substrate honesty: the seed was trained at 18.24's recorded composite
# 9bc00af0… — a moved substrate makes the seed re-run-before-use, not a config edit.
assert composite.startswith("9bc00af0"), f"substrate moved since 18.24: {composite}"

impostor = CoevoSideConfig(
    side="impostor",
    genome_length=19,
    build_policy=build_utility_scorer_policy,
    encoder_version="impostor-option-features-v1",
    initial_genome=load_candidate_weights(SEED_ARTIFACT),
    # The seed's own provenance regime (config.json: anchor_weight 4.0, the λ=4 lineage).
    anchor_weight=4.0,
)
crew = CoevoSideConfig(
    side="crew",
    genome_length=CREW_GENOME_LENGTH,
    build_policy=lambda g: build_crew_scorer(g, basis=CREW_BASIS),
    encoder_version=CREW_ENCODER,
    initial_genome=load_candidate_weights(CREW_SEED_ARTIFACT),
)

config = CoevoCampaignConfig(
    work_dir=CAMPAIGN_ROOT / RUN_NAME / "work",
    substrate_sha256=composite,
    substrate_sha_kind="compute_substrate_sha",
    impostor=impostor,
    crew=crew,
    master_seed=MASTER_SEED,
    num_swaps=4,
    generations_per_swap=3,
    fitness_seeds=(1000, 1001, 1002, 1005, 1006, 1007),
    benchmark_seeds=(2000, 2001, 2002, 2003),
    payoff_seeds=(3000, 3001, 3002, 3003),
    # A FRESH ConvictionFitnessTerm per run (mutable use counter — the 18.24 §9 note).
    conviction=(
        load_conviction_fitness_term(REPO / "training/artifacts/conviction")
        if USE_CONVICTION_TERM
        else None
    ),
    first_side="crew",
    hall_root=REPO / "training/artifacts/coevo" / RUN_NAME,
    run_label=RUN_NAME,
)

result = run_alternating_freeze(config)
print(f"RUN DONE {RUN_NAME}")
print(f"rows: {config.work_dir / 'campaign-rows.jsonl'}")
print(f"digest: {result.digest()}")
print(f"gen_champions_dir: {result.gen_champions_dir}")
# PY
```

| provenance file (`provenance/harnesses/`) | `RUN_NAME` | `MASTER_SEED` | crew seed artifact | genome / encoder | `CREW_BASIS` | conviction term |
|---|---|---:|---|---|---|---|
| `harness_run_c1.py.txt` | `run-c1-crew-owned-tasks` | 182501 | `training/artifacts/crew/crew-owned-tasks-es` | 27 / `crew-option-features-v2` | `OwnedTaskOptionBasis()` | loaded |
| `harness_run_c1_ablation.py.txt` | `ablation-run-c1-conviction-term` | 182501 | `training/artifacts/crew/crew-owned-tasks-es` | 27 / `crew-option-features-v2` | `OwnedTaskOptionBasis()` | **`None`** |
| `harness_run_c2.py.txt` | `run-c2-crew-general` | 182502 | `training/artifacts/crew/crew-utility-es` | 22 / `crew-option-features-v1` | `None` | loaded |
| `harness_run_c2_ablation.py.txt` | `ablation-run-c2-conviction-term` | 182502 | `training/artifacts/crew/crew-utility-es` | 22 / `crew-option-features-v1` | `None` | **`None`** |

Where each run's output landed is the `PATHS.md` consolidation map, not a 1:1
mirror: `work/campaign-rows.jsonl` for the two main runs was concatenated into
`training/reports/results-crew-campaign.jsonl` (run-c1 rows 1–12, run-c2 rows
13–24); the ablation twins' rows and plan went to
`training/artifacts/coevo/ablation-<run-suffix>/`; `work/gen-champions/` to
`training/artifacts/coevo/gen-champions/<run>/`; and `hall_root` was written
in-tree by the driver (`training/artifacts/coevo/PATHS.md` §"The 18.25 crew
campaign").

### 8.2 The four real-path legs (`training/realpath.py` — RETIRED, see precondition 2)

The repo-relative form of `provenance/harnesses/leg_c1_t1.py.txt`,
`leg_c1_t2.py.txt`, `leg_c2_t1.py.txt` and `leg_c2_t2.py.txt`. The slate is
protocol-fixed (gen-0 control + the two crew swap champions), not
conviction-ordered, so no pre-screen quote set rides these legs;
`meeting_timeout_seconds=900.0` (F7 kept).

```python
# uv run python - <<'PY'   (from the repository root; needs the retired module —
# `git show 4e8d533^:training/realpath.py` — and `bash scripts/fetch_evidence.sh`
# for the gen-3 hall artifact the prune moved)
from pathlib import Path

from training.bakeoff.harness import load_candidate_weights
from training.coevo.hall_of_fame import read_loadable_artifact
from training.realpath import RealPathCandidate, RealPathRerankConfig, run_realpath_rerank

REPO = Path.cwd()                       # was "~/projects/AiLibi"

# --- the row from the table below -----------------------------------------
LEG = "leg-c1-t1"
RUN = "run-c1-crew-owned-tasks"
SEEDS = (4000, 4001, 4002)
TRANCHE = "4000-4002"
GEN0_LABEL = "c1-gen0-owned-tasks-es"
GEN0_ARTIFACT = REPO / "training/artifacts/crew/crew-owned-tasks-es"
GEN0_POLICY_ID = "crew-owned-tasks-es"
ENCODER = "crew-option-features-v2"
SWAP0 = ("c1-swap0-champ-gen3", 3, "72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5")
SWAP2 = ("c1-swap2-champ-gen9", 9, "0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df")
# ---------------------------------------------------------------------------

# WHERE THE ARCHIVED BYTES LIVE (read-only). As-recorded, this leg wrote to
# "~/ailibi-campaign-1825/realpath/<run>/"; PATHS.md maps that
# prefix here, which is where the recordings and their manifest were archived
# (on the evidence commit since 19.22, restored by scripts/fetch_evidence.sh).
ARCHIVE = REPO / "training/artifacts/coevo/realpath-crew" / RUN

# WHERE A RERUN WRITES. Deliberately NOT the archive: `run_realpath_rerank`
# creates `recordings-<tranche>/` and `ranking-<tranche>.jsonl` under whatever it
# is handed, so pointing it at ARCHIVE would mix fresh output into immutable
# class-(c) evidence — or overwrite it. The original ran under an operator root
# outside the tree and this keeps that property (docs/artifacts.md: the archive
# is where the bytes ENDED UP, never a workspace).
ROOT = Path("/tmp/ailibi-campaign-1825/realpath") / RUN
HALL = REPO / "training/artifacts/coevo" / RUN / "crew"
OPPONENT = (
    REPO
    / "training/artifacts/coevo/intermediates/run-02-utility-lambda4/gen-2"
    / "ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f"
)


def hall_candidate(gen: int, sha: str, label: str) -> RealPathCandidate:
    art = read_loadable_artifact(HALL / f"gen-{gen}" / sha)
    return RealPathCandidate(
        label=label,
        genome=art.genome,
        encoder_version=art.encoder_version,
        hidden=None,
        policy_id=art.policy_id,
        method=art.method,
        anchor_policy=art.anchor_policy,
        generation_indices=(gen,),
    )


candidates = [
    RealPathCandidate(
        label=GEN0_LABEL,
        genome=load_candidate_weights(GEN0_ARTIFACT),
        encoder_version=ENCODER,
        hidden=None,
        policy_id=GEN0_POLICY_ID,
        method="crew-utility-scorer-es",
        anchor_policy="fsm-default",
        generation_indices=(),
    ),
    hall_candidate(SWAP0[1], SWAP0[2], SWAP0[0]),
    hall_candidate(SWAP2[1], SWAP2[2], SWAP2[0]),
]

print(f"[{LEG}] candidates: {[(c.label, c.encoder_version) for c in candidates]}", flush=True)
print(f"[{LEG}] opponent: ea4bc955 (the 18.24 frozen champion)  seeds={SEEDS}", flush=True)
print(f"[{LEG}] meeting_timeout_seconds=900.0 (F7 kept)  prescreen=None (protocol-fixed slate)", flush=True)
print(f"[{LEG}] writing to {ROOT}; the ARCHIVED run is at {ARCHIVE} (read-only)", flush=True)

result = run_realpath_rerank(
    candidates,
    seeds=SEEDS,
    work_dir=ROOT / f"recordings-{TRANCHE}",
    ranking_path=ROOT / f"ranking-{TRANCHE}.jsonl",
    config=RealPathRerankConfig(meeting_timeout_seconds=900.0),
    opponent_artifact=OPPONENT,
)

for row in result.rows:
    print(
        f"[{LEG}] rank {row.rank}: {row.label} selection={row.selection_score:.4f} "
        f"validity={row.validity_passed} referee={row.referee_passed} "
        f"win={row.core_impostor_win_rate:.3f} crew_stamped={row.crew_stamp_verified_games}",
        flush=True,
    )
print(f"[{LEG}] LEG DONE ranking={result.ranking_path}", flush=True)
# PY
```

| provenance file (`provenance/harnesses/`) | `LEG` | `RUN` | `SEEDS` / `TRANCHE` | gen-0 control | encoder | `SWAP0` (gen-3) | `SWAP2` (gen-9) |
|---|---|---|---|---|---|---|---|
| `leg_c1_t1.py.txt` | `leg-c1-t1` | `run-c1-crew-owned-tasks` | 4000–4002 | `crew-owned-tasks-es` | `crew-option-features-v2` | `72adb41c…` | `0bf179b7…` |
| `leg_c1_t2.py.txt` | `leg-c1-t2` | `run-c1-crew-owned-tasks` | 4003–4005 | `crew-owned-tasks-es` | `crew-option-features-v2` | `72adb41c…` | `0bf179b7…` |
| `leg_c2_t1.py.txt` | `leg-c2-t1` | `run-c2-crew-general` | 4000–4002 | `crew-utility-es` | `crew-option-features-v1` | `7fa59718…` | `515fc066…` |
| `leg_c2_t2.py.txt` | `leg-c2-t2` | `run-c2-crew-general` | 4003–4005 | `crew-utility-es` | `crew-option-features-v1` | `7fa59718…` | `515fc066…` |

Within a run the two tranche files are byte-identical apart from `LEG`, `SEEDS`
and `TRANCHE` (the c2 pair additionally sets `GEN0_LABEL = "c2-gen0-utility-es"`
and `GEN0_POLICY_ID = "crew-utility-es"`); the slate itself does not move between
tranches. The full sha of each swap champion is in the provenance file and in
`EVIDENCE-MANIFEST.md`.

The `gen-9` artifacts (`0bf179b7…`, `515fc066…`) are two of the eight genome
directories the 19.22 prune retained in-tree; the `gen-3` ones (`72adb41c…`,
`7fa59718…`) moved to the evidence commit with the rest of the unpinned halls.
