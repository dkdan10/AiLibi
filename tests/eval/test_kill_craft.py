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
    assert corpus_report.kills_total == 511
    assert corpus_report.crew_witnessed_kills == 13
    assert dict(corpus_report.co_present_histogram) == {0: 511}
    assert dict(corpus_report.one_hop_histogram) == {
        0: 274,
        1: 86,
        2: 97,
        3: 45,
        4: 7,
        5: 2,
    }


def test_corpus_means_and_correlations(corpus_report: KillCraftReport) -> None:
    assert corpus_report.mean_co_present_witnessed == pytest.approx(0.0)
    assert corpus_report.mean_co_present_unwitnessed == pytest.approx(0.0)
    assert corpus_report.mean_one_hop_witnessed == pytest.approx(2.6923076923076925)
    assert corpus_report.mean_one_hop_unwitnessed == pytest.approx(0.8393574297188755)
    # co_present is all-zero (zero variance) -> the point-biserial is undefined.
    # STILL all-zero at baseline 6: the kill-craft fold's structural finding — no
    # committed kill has ever had a co-present crewmate — survives the re-record.
    assert corpus_report.witnessed_point_biserial_co_present is None
    assert corpus_report.witnessed_point_biserial_within_one_hop == pytest.approx(
        0.26082404627833533
    )


def test_samples_9p2i_fold1(samples_9p2i_report: KillCraftReport) -> None:
    assert samples_9p2i_report.games_total == 50
    assert samples_9p2i_report.kills_total == 177
    assert samples_9p2i_report.crew_witnessed_kills == 6
    assert dict(samples_9p2i_report.co_present_histogram) == {0: 177}
    assert dict(samples_9p2i_report.one_hop_histogram) == {
        0: 96,
        1: 30,
        2: 33,
        3: 13,
        4: 4,
        5: 1,
    }
    assert samples_9p2i_report.mean_co_present_witnessed == pytest.approx(0.0)
    assert samples_9p2i_report.mean_co_present_unwitnessed == pytest.approx(0.0)
    assert samples_9p2i_report.mean_one_hop_witnessed == pytest.approx(
        2.3333333333333335
    )
    assert samples_9p2i_report.mean_one_hop_unwitnessed == pytest.approx(
        0.8304093567251462
    )
    assert samples_9p2i_report.witnessed_point_biserial_co_present is None
    assert samples_9p2i_report.witnessed_point_biserial_within_one_hop == pytest.approx(
        0.238331042011978
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
    assert crew.decisions == 22013
    assert crew.mean_conditional_entropy == pytest.approx(0.8685342615319995)
    assert crew.mean_unconditional_entropy == pytest.approx(1.1888157677302782)
    assert sorted(crew.buckets) == ["none|crowd", "none|pair", "none|solo"]
    # One full bucket cell pinned (decisions + exact kinds + approx entropy).
    solo = crew.buckets["none|solo"]
    assert solo.decisions == 7723
    assert dict(solo.action_kinds) == {
        "do_task": 4516,
        "emergency": 11,
        "move": 2257,
        "repair_sabotage": 83,
        "report": 337,
        "wait": 519,
    }
    assert solo.entropy == pytest.approx(1.5140129767968076)


def test_corpus_entropy_impostor_cells(corpus_report: KillCraftReport) -> None:
    impostor = corpus_report.entropy_by_side["IMPOSTOR"]
    assert impostor.agents == 300
    assert impostor.decisions == 6629
    assert impostor.mean_conditional_entropy == pytest.approx(0.6527172198378607)
    assert impostor.mean_unconditional_entropy == pytest.approx(1.7656880007065832)
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
    assert ready_pair.decisions == 1182
    assert dict(ready_pair.action_kinds) == {
        "do_task": 3,
        "kill": 610,
        "move": 525,
        "sabotage": 6,
        "vent": 38,
    }
    assert ready_pair.entropy == pytest.approx(1.2325617242362652)


def test_samples_9p2i_entropy(samples_9p2i_report: KillCraftReport) -> None:
    crew = samples_9p2i_report.entropy_by_side["CREWMATE"]
    assert crew.agents == 350
    assert crew.decisions == 8136
    assert crew.mean_conditional_entropy == pytest.approx(0.8789489039463282)
    assert crew.mean_unconditional_entropy == pytest.approx(1.1994131474293237)
    assert sorted(crew.buckets) == ["none|crowd", "none|pair", "none|solo"]

    impostor = samples_9p2i_report.entropy_by_side["IMPOSTOR"]
    assert impostor.agents == 100
    assert impostor.decisions == 2461
    assert impostor.mean_conditional_entropy == pytest.approx(0.7069138997083648)
    assert impostor.mean_unconditional_entropy == pytest.approx(1.7642325293949697)
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
    assert crew.decisions == 1584
    assert crew.mean_conditional_entropy == pytest.approx(0.6529321621450677)
    assert crew.mean_unconditional_entropy == pytest.approx(1.0988807344951677)
    assert sorted(crew.buckets) == ["none|crowd", "none|pair", "none|solo"]

    impostor = samples_4p1i_report.entropy_by_side["IMPOSTOR"]
    assert impostor.agents == 50
    assert impostor.decisions == 632
    assert impostor.mean_conditional_entropy == pytest.approx(0.490861414163582)
    assert impostor.mean_unconditional_entropy == pytest.approx(1.5135518536786732)
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


def test_fail_loud_on_trailing_rows_after_game_over(tmp_path: Path) -> None:
    # A replay carrying a tick row AFTER the terminal GAME_OVER tick (a partially
    # appended / doubled candidate file with a unique tick id) holds recorded
    # actions the walk never validates or folds: it must raise, never return a
    # report that silently ignored them.
    seed = 0
    (tmp_path / "roster.json").write_text(
        (_SAMPLES_4P1I / "roster.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    source_lines = (
        (_SAMPLES_4P1I / f"replay-seed-{seed}.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    tick_rows = [row for row in map(json.loads, source_lines) if row["kind"] == "tick"]
    trailing = dict(tick_rows[-1])
    trailing["tick"] = max(row["tick"] for row in tick_rows) + 100
    (tmp_path / f"replay-seed-{seed}.jsonl").write_text(
        "\n".join([*source_lines, json.dumps(trailing)]) + "\n", encoding="utf-8"
    )

    with pytest.raises(KillCraftReconstructionError, match="after the terminal"):
        compute_kill_craft_report(tmp_path)


def test_fail_loud_on_missing_game_over_row(tmp_path: Path) -> None:
    # A recording truncated BETWEEN the terminal tick and the game_over stamp
    # still reconstructs to GAME_OVER, so completeness requires the row itself.
    seed = 0
    (tmp_path / "roster.json").write_text(
        (_SAMPLES_4P1I / "roster.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    source_lines = (
        (_SAMPLES_4P1I / f"replay-seed-{seed}.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    kept = [line for line in source_lines if json.loads(line)["kind"] != "game_over"]
    assert len(kept) < len(source_lines)  # the committed game carries the stamp
    (tmp_path / f"replay-seed-{seed}.jsonl").write_text(
        "\n".join(kept) + "\n", encoding="utf-8"
    )

    with pytest.raises(KillCraftReconstructionError, match="no game_over row"):
        compute_kill_craft_report(tmp_path)


def test_fail_loud_on_duplicate_meeting_rows(tmp_path: Path) -> None:
    # A doubled meeting row (same tick AND meeting id) is silently collapsed by
    # a tick-keyed lookup, leaving the dropped row's hashes unvalidated: the
    # walk must reject it before folding.
    source_lines: list[str] = []
    meeting_indexes: list[int] = []
    for seed in range(50):
        source_lines = (
            (_SAMPLES_4P1I / f"replay-seed-{seed}.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        )
        meeting_indexes = [
            i
            for i, line in enumerate(source_lines)
            if json.loads(line)["kind"] == "meeting"
        ]
        if meeting_indexes:
            break
    else:
        pytest.fail("no committed 4p1i sample game carries a meeting row")
    index = meeting_indexes[0]
    doubled = [
        *source_lines[: index + 1],
        source_lines[index],
        *source_lines[index + 1 :],
    ]
    (tmp_path / "roster.json").write_text(
        (_SAMPLES_4P1I / "roster.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (tmp_path / f"replay-seed-{seed}.jsonl").write_text(
        "\n".join(doubled) + "\n", encoding="utf-8"
    )

    with pytest.raises(KillCraftReconstructionError, match="duplicate meeting rows"):
        compute_kill_craft_report(tmp_path)


def test_fail_loud_on_doubled_actor_action(tmp_path: Path) -> None:
    # A second action for the same actor in one tick row can be a state no-op
    # (the hash chain still verifies) yet would inflate the entropy decisions:
    # the recorder's one-action-per-living-player invariant is enforced.
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
    # Insert the duplicate ADJACENT to the original so the row stays in
    # canonical actor-ascending order and the duplicate check (not the order
    # check) is what fires.
    first["actions"] = [
        first["actions"][0],
        dict(first["actions"][0]),
        *first["actions"][1:],
    ]
    source_lines[0] = json.dumps(first)
    (tmp_path / f"replay-seed-{seed}.jsonl").write_text(
        "\n".join(source_lines) + "\n", encoding="utf-8"
    )

    with pytest.raises(
        KillCraftReconstructionError, match="one action per living player"
    ):
        compute_kill_craft_report(tmp_path)


def test_fail_loud_on_permuted_action_order(tmp_path: Path) -> None:
    # advance_tick applies actions in list order without re-sorting, so a
    # permuted row changes intra-tick resolution (it can flip the witnessed
    # bit) while the post-advance hash can still verify: the recorder's
    # canonical actor-ascending order is enforced.
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
    assert len(first["actions"]) >= 2
    actions = list(first["actions"])
    actions[0], actions[1] = actions[1], actions[0]
    first["actions"] = actions
    source_lines[0] = json.dumps(first)
    (tmp_path / f"replay-seed-{seed}.jsonl").write_text(
        "\n".join(source_lines) + "\n", encoding="utf-8"
    )

    with pytest.raises(
        KillCraftReconstructionError, match="canonical actor-ascending order"
    ):
        compute_kill_craft_report(tmp_path)


def test_fail_loud_on_dropped_actor_action(tmp_path: Path) -> None:
    # The symmetric tamper: dropping one action (a no-op wait can vanish without
    # moving the hash chain) would silently UNDER-count the entropy decisions.
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
    first["actions"] = first["actions"][1:]
    source_lines[0] = json.dumps(first)
    (tmp_path / f"replay-seed-{seed}.jsonl").write_text(
        "\n".join(source_lines) + "\n", encoding="utf-8"
    )

    with pytest.raises(
        KillCraftReconstructionError, match="one action per living player"
    ):
        compute_kill_craft_report(tmp_path)


def test_fail_loud_on_empty_replay_set(tmp_path: Path) -> None:
    # A directory with no replay-seed-*.jsonl files (a path typo, or the parent
    # corpus dir) must raise, never pin a zero-game "measurement".
    with pytest.raises(KillCraftReconstructionError, match="no replay-seed"):
        compute_kill_craft_report(tmp_path)
