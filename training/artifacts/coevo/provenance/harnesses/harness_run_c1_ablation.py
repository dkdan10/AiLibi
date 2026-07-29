"""Task 18.25 session harness — run-c1 (crew owned-task base vs the ea4bc955 seed).

Operator-authored; the machinery is consumed frozen (the 18.24 §9 idiom).
Fake-path campaign run: $0, deterministic under master_seed on this platform.
"""

import os
import sys
from pathlib import Path

_REPO = "/Users/danielkeinan/projects/AiLibi"
os.chdir(_REPO)
sys.path.insert(0, _REPO)

from training.anchor_study import compute_substrate_sha
from training.bakeoff.harness import load_candidate_weights, load_conviction_fitness_term
from training.bakeoff.utility_es import build_utility_scorer_policy
from training.coevo.driver import CoevoCampaignConfig, CoevoSideConfig, run_alternating_freeze
from training.crew.options import OwnedTaskOptionBasis
from training.crew.scorer import build_crew_scorer

REPO = Path("/Users/danielkeinan/projects/AiLibi")
CAMPAIGN_ROOT = Path("/Users/danielkeinan/ailibi-campaign-1825")
RUN_NAME = "ablation-run-c1-conviction-term"

# The 18.24 hand-off seed: intermediates/run-02-utility-lambda4/gen-2 (finalist 1a,
# pooled 6/6). Re-frozen as a fresh lineage in THIS campaign's own hall by the
# driver's swap-boundary freeze (no hall-adoption seam exists — reachability honesty).
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
    genome_length=27,
    build_policy=lambda g: build_crew_scorer(g, basis=OwnedTaskOptionBasis()),
    encoder_version="crew-option-features-v2",
    initial_genome=load_candidate_weights(REPO / "training/artifacts/crew/crew-owned-tasks-es"),
)

config = CoevoCampaignConfig(
    work_dir=CAMPAIGN_ROOT / RUN_NAME / "work",
    substrate_sha256=composite,
    substrate_sha_kind="compute_substrate_sha",
    impostor=impostor,
    crew=crew,
    master_seed=182501,
    num_swaps=4,
    generations_per_swap=3,
    fitness_seeds=(1000, 1001, 1002, 1005, 1006, 1007),
    benchmark_seeds=(2000, 2001, 2002, 2003),
    payoff_seeds=(3000, 3001, 3002, 3003),
    # A FRESH ConvictionFitnessTerm per run (mutable use counter — the 18.24 §9 note).
    conviction=None,
    first_side="crew",
    hall_root=REPO / "training/artifacts/coevo" / RUN_NAME,
    run_label=RUN_NAME,
)

result = run_alternating_freeze(config)
print(f"RUN DONE {RUN_NAME}")
print(f"rows: {config.work_dir / 'campaign-rows.jsonl'}")
print(f"digest: {result.digest()}")
print(f"gen_champions_dir: {result.gen_champions_dir}")
