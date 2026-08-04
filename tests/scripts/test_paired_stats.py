"""Tests for scripts/paired_stats.py (Task 19.20).

Drives ``main`` directly (no subprocess). Pins the paired recomputation over the
COMMITTED finalist-eval measurement exactly — per-arm n / wins / discordant
counts, the exact-binomial McNemar p to 4dp (and as an exact fraction where it is
clean), and the Wilson 95% bounds to 4dp — so a later report edit cannot drift
the quoted numbers without turning this file red. Unit tests cover the two
primitives at their edges, and the error paths (unrecognised reason, duplicate
seed, missing entrant) run against tiny synthetic JSONL files in ``tmp_path``.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

import paired_stats

_REPO_ROOT = Path(__file__).resolve().parents[2]
_RESULTS = _REPO_ROOT / "training" / "reports" / "results-finalist-eval.jsonl"

_BASELINE = "p18-fsm-comparator"
_ARMS = (
    "p18-imp-ea4bc955",
    "p18-imp-bfd145cb",
    "p18-imp-6d327dcb",
    "p18-imp-7f73929d",
)


# --------------------------------------------------------------------------- #
# synthetic-JSONL helpers                                                      #
# --------------------------------------------------------------------------- #


def _row(entrant: str, games: Sequence[tuple[int, str]]) -> dict[str, Any]:
    return {
        "entrant": entrant,
        "watchability": {
            "per_game": [{"seed": seed, "reason": reason} for seed, reason in games]
        },
    }


def _write(tmp_path: Path, rows: Sequence[Mapping[str, Any]]) -> Path:
    path = tmp_path / "results.jsonl"
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    return path


# --------------------------------------------------------------------------- #
# the committed measurement — pinned exactly                                   #
# --------------------------------------------------------------------------- #


def test_committed_arms_and_order() -> None:
    rows = paired_stats.compute_paired_stats(_RESULTS)
    assert [row.entrant for row in rows] == list(_ARMS)


@pytest.mark.parametrize(
    ("entrant", "n", "arm_wins", "baseline_wins", "b", "c", "p_4dp", "delta"),
    [
        ("p18-imp-ea4bc955", 50, 26, 13, 17, 4, 0.0072, 0.26),
        ("p18-imp-bfd145cb", 50, 28, 13, 20, 5, 0.0041, 0.30),
        ("p18-imp-6d327dcb", 50, 19, 13, 15, 9, 0.3075, 0.12),
        ("p18-imp-7f73929d", 49, 21, 12, 12, 3, 0.0352, 9.0 / 49.0),
    ],
)
def test_committed_paired_counts(
    entrant: str,
    n: int,
    arm_wins: int,
    baseline_wins: int,
    b: int,
    c: int,
    p_4dp: float,
    delta: float,
) -> None:
    rows = {row.entrant: row for row in paired_stats.compute_paired_stats(_RESULTS)}
    row = rows[entrant]
    assert row.n == n
    assert row.arm_wins == arm_wins
    assert row.baseline_wins == baseline_wins
    assert row.b == b
    assert row.c == c
    assert round(row.p_exact, 4) == p_4dp
    assert row.delta == pytest.approx(delta)
    assert row.arm_rate == pytest.approx(arm_wins / n)
    assert row.baseline_rate == pytest.approx(baseline_wins / n)
    # delta is the paired marginal difference, i.e. (b - c) / n.
    assert row.delta == pytest.approx((b - c) / n)


def test_committed_exact_p_fractions() -> None:
    """The two clean fractions, asserted as exact rationals (not 4dp)."""

    rows = {row.entrant: row for row in paired_stats.compute_paired_stats(_RESULTS)}
    # b=17, c=4: n=21 discordant, 2 * sum(C(21,i), i<=4) / 2**21.
    assert rows["p18-imp-ea4bc955"].p_exact == 15094 / 2097152
    # b=12, c=3: n=15 discordant, 2 * sum(C(15,i), i<=3) / 2**15.
    assert rows["p18-imp-7f73929d"].p_exact == 1152 / 32768
    assert rows["p18-imp-7f73929d"].p_exact == 0.03515625


@pytest.mark.parametrize(
    ("entrant", "arm_ci", "baseline_ci"),
    [
        ("p18-imp-ea4bc955", (0.3851, 0.6520), (0.1587, 0.3955)),
        ("p18-imp-bfd145cb", (0.4231, 0.6884), (0.1587, 0.3955)),
        ("p18-imp-6d327dcb", (0.2586, 0.5185), (0.1587, 0.3955)),
        ("p18-imp-7f73929d", (0.3002, 0.5673), (0.1460, 0.3809)),
    ],
)
def test_committed_wilson_bounds(
    entrant: str, arm_ci: tuple[float, float], baseline_ci: tuple[float, float]
) -> None:
    rows = {row.entrant: row for row in paired_stats.compute_paired_stats(_RESULTS)}
    row = rows[entrant]
    assert (round(row.arm_wilson_low, 4), round(row.arm_wilson_high, 4)) == arm_ci
    assert (
        round(row.baseline_wilson_low, 4),
        round(row.baseline_wilson_high, 4),
    ) == baseline_ci


def test_committed_significance_verdicts() -> None:
    """Two arms clear Bonferroni 0.0125; 7f73929d fails it; 6d327dcb fails 0.05."""

    rows = {row.entrant: row for row in paired_stats.compute_paired_stats(_RESULTS)}
    threshold = 0.05 / 4
    assert rows["p18-imp-ea4bc955"].p_exact < threshold
    assert rows["p18-imp-bfd145cb"].p_exact < threshold
    assert 0.05 > rows["p18-imp-7f73929d"].p_exact > threshold
    assert rows["p18-imp-6d327dcb"].p_exact > 0.05


def test_explicit_arm_selection_matches_autodetect() -> None:
    auto = paired_stats.compute_paired_stats(_RESULTS)
    explicit = paired_stats.compute_paired_stats(_RESULTS, arm_entrants=_ARMS)
    assert [row.model_dump() for row in auto] == [row.model_dump() for row in explicit]


def test_result_rows_are_frozen() -> None:
    row = paired_stats.compute_paired_stats(_RESULTS)[0]
    with pytest.raises(ValidationError):
        row.n = 1


# --------------------------------------------------------------------------- #
# exact_mcnemar_p                                                              #
# --------------------------------------------------------------------------- #


def test_mcnemar_no_discordant_pairs_is_one() -> None:
    assert paired_stats.exact_mcnemar_p(0, 0) == 1.0


@pytest.mark.parametrize(("b", "c"), [(17, 4), (12, 3), (6, 5), (9, 15), (1, 0)])
def test_mcnemar_is_symmetric(b: int, c: int) -> None:
    assert paired_stats.exact_mcnemar_p(b, c) == paired_stats.exact_mcnemar_p(c, b)


def test_mcnemar_caps_at_one() -> None:
    # The crew-report precedent (b=6, c=5): sum(C(11,i), i<=5) is exactly 2**10,
    # so the doubled tail lands on 1.0 rather than overshooting it.
    assert paired_stats.exact_mcnemar_p(6, 5) == 1.0
    # b=c=1 doubles a 3/4 tail to 1.5 and must be capped.
    assert paired_stats.exact_mcnemar_p(1, 1) == 1.0


def test_mcnemar_hand_computable_cases() -> None:
    # All five discordant pairs one way: 2 * C(5,0) / 2**5 = 2/32.
    assert paired_stats.exact_mcnemar_p(5, 0) == 0.0625
    # 2 * C(10,0) / 2**10 = 2/1024.
    assert paired_stats.exact_mcnemar_p(10, 0) == 0.001953125
    # 2 * (C(4,0) + C(4,1)) / 2**4 = 2 * 5 / 16.
    assert paired_stats.exact_mcnemar_p(3, 1) == 0.625


@pytest.mark.parametrize(("b", "c"), [(-1, 0), (0, -1), (-3, -2)])
def test_mcnemar_rejects_negative_counts(b: int, c: int) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        paired_stats.exact_mcnemar_p(b, c)


# --------------------------------------------------------------------------- #
# wilson_interval                                                              #
# --------------------------------------------------------------------------- #


def test_wilson_textbook_value() -> None:
    low, high = paired_stats.wilson_interval(50, 100, z=1.96)
    assert (round(low, 4), round(high, 4)) == (0.4038, 0.5962)


def test_wilson_zero_successes_edge() -> None:
    low, high = paired_stats.wilson_interval(0, 20)
    assert low == pytest.approx(0.0, abs=1e-12)
    assert 0.0 < high < 1.0


def test_wilson_all_successes_edge() -> None:
    low, high = paired_stats.wilson_interval(20, 20)
    assert high == pytest.approx(1.0, abs=1e-12)
    assert 0.0 < low < 1.0
    # Mirror image of the zero-successes interval.
    zero_low, zero_high = paired_stats.wilson_interval(0, 20)
    assert low == pytest.approx(1.0 - zero_high)
    assert high == pytest.approx(1.0 - zero_low)


def test_wilson_brackets_the_point_estimate() -> None:
    low, high = paired_stats.wilson_interval(26, 50)
    assert low < 0.52 < high


@pytest.mark.parametrize(
    ("successes", "total"),
    [(0, 0), (1, -5), (-1, 10), (11, 10)],
)
def test_wilson_rejects_invalid_input(successes: int, total: int) -> None:
    with pytest.raises(ValueError):
        paired_stats.wilson_interval(successes, total)


# --------------------------------------------------------------------------- #
# error paths (no silent fallbacks)                                            #
# --------------------------------------------------------------------------- #


def test_unrecognised_reason_raises(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        [
            _row("p18-imp-x", [(0, "IMPOSTOR_PARITY"), (1, "no game_over record")]),
            _row(_BASELINE, [(0, "CREWMATE_EJECT"), (1, "CREWMATE_TASKS")]),
        ],
    )
    with pytest.raises(ValueError, match="unrecognised game-over reason"):
        paired_stats.compute_paired_stats(path, arm_entrants=["p18-imp-x"])


def test_unrecognised_reason_in_uncompared_entrant_is_ignored(tmp_path: Path) -> None:
    """The committed file's crew arms carry unknown reasons; they are not compared."""

    path = _write(
        tmp_path,
        [
            _row("p18-imp-x", [(0, "IMPOSTOR_PARITY"), (1, "IMPOSTOR_SABOTAGE")]),
            _row(_BASELINE, [(0, "CREWMATE_EJECT"), (1, "CREWMATE_TASKS")]),
            _row("p18-crew-z", [(0, "no game_over record in replay")]),
        ],
    )
    rows = paired_stats.compute_paired_stats(path)
    assert [row.entrant for row in rows] == ["p18-imp-x"]
    assert rows[0].b == 2
    assert rows[0].c == 0


def test_duplicate_seed_raises(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        [
            _row("p18-imp-x", [(0, "IMPOSTOR_PARITY"), (0, "CREWMATE_EJECT")]),
            _row(_BASELINE, [(0, "CREWMATE_EJECT")]),
        ],
    )
    with pytest.raises(ValueError, match="duplicate seed 0"):
        paired_stats.compute_paired_stats(path)


def test_missing_baseline_entrant_raises(tmp_path: Path) -> None:
    path = _write(tmp_path, [_row("p18-imp-x", [(0, "IMPOSTOR_PARITY")])])
    with pytest.raises(ValueError, match="baseline entrant"):
        paired_stats.compute_paired_stats(path)


def test_missing_arm_entrant_raises(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        [
            _row("p18-imp-x", [(0, "IMPOSTOR_PARITY")]),
            _row(_BASELINE, [(0, "CREWMATE_EJECT")]),
        ],
    )
    with pytest.raises(ValueError, match="not found"):
        paired_stats.compute_paired_stats(path, arm_entrants=["p18-imp-nope"])


def test_no_arm_entrants_raises(tmp_path: Path) -> None:
    path = _write(tmp_path, [_row(_BASELINE, [(0, "CREWMATE_EJECT")])])
    with pytest.raises(ValueError, match="no arm entrants"):
        paired_stats.compute_paired_stats(path)


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not found"):
        paired_stats.compute_paired_stats(tmp_path / "nope.jsonl")


def test_malformed_json_line_raises(tmp_path: Path) -> None:
    path = tmp_path / "results.jsonl"
    path.write_text('{"entrant": "p18-imp-x"\n')
    with pytest.raises(ValueError, match="malformed JSON"):
        paired_stats.compute_paired_stats(path)


def test_disjoint_seed_sets_raise(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        [
            _row("p18-imp-x", [(0, "IMPOSTOR_PARITY")]),
            _row(_BASELINE, [(1, "CREWMATE_EJECT")]),
        ],
    )
    with pytest.raises(ValueError, match="no seeds shared"):
        paired_stats.compute_paired_stats(path)


def test_seed_intersection_is_used(tmp_path: Path) -> None:
    """An arm missing a seed is compared only over the shared seeds."""

    path = _write(
        tmp_path,
        [
            _row("p18-imp-x", [(0, "IMPOSTOR_PARITY"), (1, "CREWMATE_EJECT")]),
            _row(
                _BASELINE,
                [
                    (0, "CREWMATE_EJECT"),
                    (1, "CREWMATE_EJECT"),
                    (2, "IMPOSTOR_PARITY"),
                ],
            ),
        ],
    )
    row = paired_stats.compute_paired_stats(path)[0]
    assert row.n == 2
    assert row.arm_wins == 1
    assert row.baseline_wins == 0
    assert (row.b, row.c) == (1, 0)


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #


def test_cli_human_output(capsys: pytest.CaptureFixture[str]) -> None:
    assert paired_stats.main([str(_RESULTS)]) == 0
    out = capsys.readouterr().out
    for arm in _ARMS:
        assert arm in out
    assert _BASELINE in out
    assert "0.0125" in out
    assert "Bonferroni" in out
    assert "p18-imp-6d327dcb" in out.split("UNCORRECTED")[-1]


def test_cli_json_matches_library(capsys: pytest.CaptureFixture[str]) -> None:
    assert paired_stats.main([str(_RESULTS), "--json"]) == 0
    payload: list[dict[str, Any]] = json.loads(capsys.readouterr().out)
    assert payload == [
        row.model_dump() for row in paired_stats.compute_paired_stats(_RESULTS)
    ]
    assert [row["entrant"] for row in payload] == list(_ARMS)


def test_cli_baseline_flag(capsys: pytest.CaptureFixture[str]) -> None:
    assert paired_stats.main([str(_RESULTS), "--baseline", _BASELINE, "--json"]) == 0
    payload: list[dict[str, Any]] = json.loads(capsys.readouterr().out)
    assert payload[0]["p_exact"] == 15094 / 2097152


def test_cli_missing_file_is_usage_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert paired_stats.main([str(tmp_path / "nope.jsonl")]) == 2
    assert "not found" in capsys.readouterr().err


def test_cli_unknown_baseline_is_usage_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert paired_stats.main([str(_RESULTS), "--baseline", "no-such-entrant"]) == 2
    assert "baseline entrant" in capsys.readouterr().err
