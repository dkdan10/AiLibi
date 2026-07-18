"""Unit tests + reproduction pins for eval/kill_craft.py (Task 18.2).

The kill-craft fold is a pure, offline, state-hash-verified reconstruction over
committed replay bytes, so its cells are pinnable. Three sets are pinned:

* ``replays/ml_corpus/9p2i`` — THE corpus, the primary pin (150 games);
* ``replays/samples/9p2i`` and ``replays/samples/4p1i`` — the sample sets.

The pins were derived from the committed bytes by running the fold once (a
throwaway script, never committed). Fold 1's ``co_present_crew`` is zero on every
committed kill — kills land when the impostor is alone with the victim — so the
crew-witness signal lives entirely in the one-hop channel, and
``witnessed_point_biserial_co_present`` is ``None`` (the count has zero variance)
while ``witnessed_point_biserial_within_one_hop`` is a defined positive
correlation. Crew never carry a cooldown, so every crew bucket is ``none|*``;
impostors always carry one, so every impostor bucket is ``cooling|*`` / ``ready|*``.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from eval.kill_craft import (
    KillCraftReconstructionError,
    KillCraftReport,
    compute_kill_craft_report,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CORPUS_9P2I = _REPO_ROOT / "replays" / "ml_corpus" / "9p2i"
_SAMPLES_9P2I = _REPO_ROOT / "replays" / "samples" / "9p2i"
_SAMPLES_4P1I = _REPO_ROOT / "replays" / "samples" / "4p1i"

_LOG2_9 = math.log2(9)


# --------------------------------------------------------------------------- #
# Module-scoped fixtures — each report computed ONCE.                           #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def corpus_report() -> KillCraftReport:
    return compute_kill_craft_report(_CORPUS_9P2I)


@pytest.fixture(scope="module")
def samples_9p2i_report() -> KillCraftReport:
    return compute_kill_craft_report(_SAMPLES_9P2I)


@pytest.fixture(scope="module")
def samples_4p1i_report() -> KillCraftReport:
    return compute_kill_craft_report(_SAMPLES_4P1I)


# --------------------------------------------------------------------------- #
# Fold 1 — kill-timing vs witness density (pins 1 + 2).                         #
# --------------------------------------------------------------------------- #


def test_corpus_kill_counts_and_histograms(corpus_report: KillCraftReport) -> None:
    assert corpus_report.games_total == 150
    assert corpus_report.kills_total == 599
    assert corpus_report.crew_witnessed_kills == 20
    assert dict(corpus_report.co_present_histogram) == {0: 599}
    assert dict(corpus_report.one_hop_histogram) == {
        0: 331,
        1: 101,
        2: 103,
        3: 53,
        4: 7,
        5: 4,
    }


def test_corpus_means_and_correlations(corpus_report: KillCraftReport) -> None:
    assert corpus_report.mean_co_present_witnessed == pytest.approx(0.0)
    assert corpus_report.mean_co_present_unwitnessed == pytest.approx(0.0)
    assert corpus_report.mean_one_hop_witnessed == pytest.approx(2.55)
    assert corpus_report.mean_one_hop_unwitnessed == pytest.approx(0.7996545768566494)
    # co_present is all-zero (zero variance) -> the point-biserial is undefined.
    assert corpus_report.witnessed_point_biserial_co_present is None
    assert corpus_report.witnessed_point_biserial_within_one_hop == pytest.approx(
        0.27899083053626106
    )


def test_samples_9p2i_fold1(samples_9p2i_report: KillCraftReport) -> None:
    assert samples_9p2i_report.games_total == 50
    assert samples_9p2i_report.kills_total == 203
    assert samples_9p2i_report.crew_witnessed_kills == 7
    assert dict(samples_9p2i_report.co_present_histogram) == {0: 203}
    assert dict(samples_9p2i_report.one_hop_histogram) == {
        0: 115,
        1: 35,
        2: 35,
        3: 12,
        4: 5,
        5: 1,
    }
    assert samples_9p2i_report.mean_co_present_witnessed == pytest.approx(0.0)
    assert samples_9p2i_report.mean_co_present_unwitnessed == pytest.approx(0.0)
    assert samples_9p2i_report.mean_one_hop_witnessed == pytest.approx(
        2.7142857142857144
    )
    assert samples_9p2i_report.mean_one_hop_unwitnessed == pytest.approx(0.75)
    assert samples_9p2i_report.witnessed_point_biserial_co_present is None
    assert samples_9p2i_report.witnessed_point_biserial_within_one_hop == pytest.approx(
        0.32152356362861145
    )


def test_samples_4p1i_fold1(samples_4p1i_report: KillCraftReport) -> None:
    assert samples_4p1i_report.games_total == 50
    assert samples_4p1i_report.kills_total == 61
    assert samples_4p1i_report.crew_witnessed_kills == 1
    assert dict(samples_4p1i_report.co_present_histogram) == {0: 61}
    assert dict(samples_4p1i_report.one_hop_histogram) == {0: 49, 1: 11, 2: 1}
    assert samples_4p1i_report.mean_co_present_witnessed == pytest.approx(0.0)
    assert samples_4p1i_report.mean_co_present_unwitnessed == pytest.approx(0.0)
    assert samples_4p1i_report.mean_one_hop_witnessed == pytest.approx(1.0)
    assert samples_4p1i_report.mean_one_hop_unwitnessed == pytest.approx(0.2)
    assert samples_4p1i_report.witnessed_point_biserial_co_present is None
    assert samples_4p1i_report.witnessed_point_biserial_within_one_hop == pytest.approx(
        0.22687999213482657
    )


# --------------------------------------------------------------------------- #
# Fold 2 — action-stream behavioral entropy (pin 3).                           #
# --------------------------------------------------------------------------- #


def test_corpus_entropy_crew_cells(corpus_report: KillCraftReport) -> None:
    crew = corpus_report.entropy_by_side["CREWMATE"]
    assert crew.agents == 1050
    assert crew.decisions == 24758
    assert crew.mean_conditional_entropy == pytest.approx(0.9176435717876024)
    assert crew.mean_unconditional_entropy == pytest.approx(1.2334107384075725)
    assert sorted(crew.buckets) == ["none|crowd", "none|pair", "none|solo"]
    # One full bucket cell pinned (decisions + exact kinds + approx entropy).
    solo = crew.buckets["none|solo"]
    assert solo.decisions == 8609
    assert dict(solo.action_kinds) == {
        "do_task": 4923,
        "emergency": 11,
        "move": 2568,
        "repair_sabotage": 102,
        "report": 395,
        "wait": 610,
    }
    assert solo.entropy == pytest.approx(1.5443476559830103)


def test_corpus_entropy_impostor_cells(corpus_report: KillCraftReport) -> None:
    impostor = corpus_report.entropy_by_side["IMPOSTOR"]
    assert impostor.agents == 300
    assert impostor.decisions == 7693
    assert impostor.mean_conditional_entropy == pytest.approx(0.712621088564195)
    assert impostor.mean_unconditional_entropy == pytest.approx(1.7847675437767605)
    assert sorted(impostor.buckets) == [
        "cooling|crowd",
        "cooling|pair",
        "cooling|solo",
        "ready|crowd",
        "ready|pair",
        "ready|solo",
    ]
    # The kill bucket (impostor ready + a co-present victim): the fold's sharpest
    # cell — kills concentrate here.
    ready_pair = impostor.buckets["ready|pair"]
    assert ready_pair.decisions == 1408
    assert dict(ready_pair.action_kinds) == {
        "do_task": 18,
        "kill": 700,
        "move": 626,
        "sabotage": 13,
        "vent": 50,
        "wait": 1,
    }
    assert ready_pair.entropy == pytest.approx(1.3424168797786455)


def test_samples_9p2i_entropy(samples_9p2i_report: KillCraftReport) -> None:
    crew = samples_9p2i_report.entropy_by_side["CREWMATE"]
    assert crew.agents == 350
    assert crew.decisions == 8320
    assert crew.mean_conditional_entropy == pytest.approx(0.9038068319803731)
    assert crew.mean_unconditional_entropy == pytest.approx(1.219106522647087)
    assert sorted(crew.buckets) == ["none|crowd", "none|pair", "none|solo"]

    impostor = samples_9p2i_report.entropy_by_side["IMPOSTOR"]
    assert impostor.agents == 100
    assert impostor.decisions == 2592
    assert impostor.mean_conditional_entropy == pytest.approx(0.7170339225884729)
    assert impostor.mean_unconditional_entropy == pytest.approx(1.77659044713753)
    assert sorted(impostor.buckets) == [
        "cooling|crowd",
        "cooling|pair",
        "cooling|solo",
        "ready|crowd",
        "ready|pair",
        "ready|solo",
    ]


def test_samples_4p1i_entropy(samples_4p1i_report: KillCraftReport) -> None:
    crew = samples_4p1i_report.entropy_by_side["CREWMATE"]
    assert crew.agents == 150
    assert crew.decisions == 1612
    assert crew.mean_conditional_entropy == pytest.approx(0.650965013359306)
    assert crew.mean_unconditional_entropy == pytest.approx(1.0969217125759623)
    assert sorted(crew.buckets) == ["none|crowd", "none|pair", "none|solo"]

    impostor = samples_4p1i_report.entropy_by_side["IMPOSTOR"]
    assert impostor.agents == 50
    assert impostor.decisions == 646
    assert impostor.mean_conditional_entropy == pytest.approx(0.48159347248591944)
    assert impostor.mean_unconditional_entropy == pytest.approx(1.4981725214543429)
    assert sorted(impostor.buckets) == [
        "cooling|crowd",
        "cooling|pair",
        "cooling|solo",
        "ready|crowd",
        "ready|pair",
        "ready|solo",
    ]


# --------------------------------------------------------------------------- #
# Structural invariants (pin 4 — corpus set).                                  #
# --------------------------------------------------------------------------- #


def test_corpus_structural_invariants(corpus_report: KillCraftReport) -> None:
    assert len(corpus_report.per_kill) == corpus_report.kills_total
    assert sum(corpus_report.co_present_histogram.values()) == corpus_report.kills_total
    assert sum(corpus_report.one_hop_histogram.values()) == corpus_report.kills_total
    assert corpus_report.crew_witnessed_kills == sum(
        row.crew_witnessed for row in corpus_report.per_kill
    )
    for cells in corpus_report.entropy_by_side.values():
        # Side decisions == the sum of its bucket decisions.
        assert cells.decisions == sum(b.decisions for b in cells.buckets.values())
        for bucket_key, bucket in cells.buckets.items():
            assert bucket.decisions == sum(bucket.action_kinds.values())
            # Entropy is in bits over <= 9 kinds: 0 <= H <= log2(9).
            assert 0.0 <= bucket.entropy <= _LOG2_9 + 1e-9, (bucket_key, bucket.entropy)


def test_side_buckets_partition_by_cooldown(corpus_report: KillCraftReport) -> None:
    # Crew never carry a cooldown entry -> every crew bucket is "none|*"; impostors
    # always carry one -> no impostor bucket is "none|*".
    for bucket_key in corpus_report.entropy_by_side["CREWMATE"].buckets:
        assert bucket_key.startswith("none|")
    for bucket_key in corpus_report.entropy_by_side["IMPOSTOR"].buckets:
        assert not bucket_key.startswith("none|")


# --------------------------------------------------------------------------- #
# Determinism (pin 5) + fail-loud (pin 6).                                      #
# --------------------------------------------------------------------------- #


def test_report_is_deterministic(samples_4p1i_report: KillCraftReport) -> None:
    # A second, independent computation must dump byte-identically to the first.
    recomputed = compute_kill_craft_report(_SAMPLES_4P1I)
    assert recomputed.model_dump() == samples_4p1i_report.model_dump()


def test_fail_loud_on_corrupted_state_hash(tmp_path: Path) -> None:
    seed = 0
    (tmp_path / "roster.json").write_text(
        (_SAMPLES_4P1I / "roster.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    source_lines = (
        (_SAMPLES_4P1I / f"replay-seed-{seed}.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    first = json.loads(source_lines[0])
    assert first["kind"] == "tick"
    original_hash = first["state_hash"]
    # Flip one hex character so the recorded hash no longer reconstructs.
    first["state_hash"] = ("0" if original_hash[0] != "0" else "f") + original_hash[1:]
    source_lines[0] = json.dumps(first)
    (tmp_path / f"replay-seed-{seed}.jsonl").write_text(
        "\n".join(source_lines) + "\n", encoding="utf-8"
    )

    with pytest.raises(KillCraftReconstructionError, match="tick 0 reconstructed"):
        compute_kill_craft_report(tmp_path)


def test_fail_loud_on_truncated_replay(tmp_path: Path) -> None:
    # A replay whose bytes end while the game is still in play (no GAME_OVER
    # reached) is an EOF-truncated recording: it must raise, never return a
    # partial (silently under-counted) report.
    seed = 0
    (tmp_path / "roster.json").write_text(
        (_SAMPLES_4P1I / "roster.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    source_lines = (
        (_SAMPLES_4P1I / f"replay-seed-{seed}.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    first = json.loads(source_lines[0])
    assert first["kind"] == "tick"  # a game cannot be over at tick 0
    (tmp_path / f"replay-seed-{seed}.jsonl").write_text(
        source_lines[0] + "\n", encoding="utf-8"
    )

    with pytest.raises(KillCraftReconstructionError, match="never reached GAME_OVER"):
        compute_kill_craft_report(tmp_path)


def test_fail_loud_on_empty_replay_set(tmp_path: Path) -> None:
    # A directory with no replay-seed-*.jsonl files (a path typo, or the parent
    # corpus dir) must raise, never pin a zero-game "measurement".
    with pytest.raises(KillCraftReconstructionError, match="no replay-seed"):
        compute_kill_craft_report(tmp_path)
