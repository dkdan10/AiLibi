"""Task 18.25 real-path leg — run-c2 slate, tranche 4003-4005, vs the ea4bc955 opponent.

Operator-authored leg harness (18.24 §9 idiom + the 18.32 crew arm). The slate is
protocol-fixed (gen-0 control + the two crew swap champions), not conviction-ordered,
so no pre-screen quote set rides this leg (blocker-4 pairing does not bind; the native
leg-log is the ordering evidence). meeting_timeout_seconds=900 (F7 kept).
"""

import os
import sys

_REPO = "/Users/danielkeinan/projects/AiLibi"
os.chdir(_REPO)
sys.path.insert(0, _REPO)

from pathlib import Path

from training.bakeoff.harness import load_candidate_weights
from training.coevo.hall_of_fame import read_loadable_artifact
from training.realpath import RealPathCandidate, RealPathRerankConfig, run_realpath_rerank

REPO = Path(_REPO)
LEG = "leg-c2-t2"
ROOT = Path("/Users/danielkeinan/ailibi-campaign-1825/realpath/run-c2-crew-general")
SEEDS = (4003, 4004, 4005)
TRANCHE = "4003-4005"
OPPONENT = (
    REPO
    / "training/artifacts/coevo/intermediates/run-02-utility-lambda4/gen-2"
    / "ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f"
)
HALL = REPO / "training/artifacts/coevo/run-c2-crew-general/crew"


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
        label="c2-gen0-utility-es",
        genome=load_candidate_weights(REPO / "training/artifacts/crew/crew-utility-es"),
        encoder_version="crew-option-features-v1",
        hidden=None,
        policy_id="crew-utility-es",
        method="crew-utility-scorer-es",
        anchor_policy="fsm-default",
        generation_indices=(),
    ),
    hall_candidate(3, "7fa59718d8810a3c26214309eaf6b637a1afc66dc3ea923ab887152f4e985acd", "c2-swap0-champ-gen3"),
    hall_candidate(9, "515fc066f7aafc5d3603ab531adb9fe78cd496192c7565e9d8b4d3ff7b09a635", "c2-swap2-champ-gen9"),
]

print(f"[{LEG}] candidates: {[(c.label, c.encoder_version) for c in candidates]}", flush=True)
print(f"[{LEG}] opponent: ea4bc955 (the 18.24 frozen champion)  seeds={SEEDS}", flush=True)
print(f"[{LEG}] meeting_timeout_seconds=900.0 (F7 kept)  prescreen=None (protocol-fixed slate)", flush=True)

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
