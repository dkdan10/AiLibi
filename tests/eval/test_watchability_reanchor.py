"""Tests for the Task-16.11 referee re-anchor (population-relative conversion).

The contract's three pillars (tasks/phase-16.md Task 16.11; the owner ruling of
2026-07-11, audits/audit-phase-15-close.md §10, with §11's conversion-seam
finding as the evidence):

* **The champion-close fixture reproduction** — the committed
  ``training/reports/results-champion-close.jsonl`` gauges, re-scored under the
  population-relative definition, read as the NON-BLOCKING outcome the §10
  ruling anticipated (derived rather than ruled), with the old-definition FAIL
  preserved alongside as the historical contrast.
* **The synthetic starved FAIL** — a set with a high meeting rate and ZERO
  backed accusations fails the conversion floor regardless of its population's
  supply: the floor's reason to exist survives the re-anchor.
* **The FSM-baseline consistency check** — the committed default sets (baseline-5
  since the Task 16.17 close re-record) still pass at EXACT floor == measured equality
  (at the baseline's own evidence density the derived floor IS the pin, bit-exact),
  and the frozen baseline-2 block stays absolute.

Plus the derivation's own properties (:func:`population_relative_conversion_floor`
is the public symbol downstream 16.14/16.17 quote): equality at the anchor
density, inverse scaling with per-meeting evidence supply, the 1.0 cap for
evidence-poor sets, maximal demand without per-meeting evidence, and fail-loud
degenerate pins.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any

import pytest

from eval.watchability import (
    _BASELINE_SUPPLY_FLOORS,
    SupplyGaugeValues,
    compute_watchability,
    evaluate_supply_floors,
    population_relative_conversion_floor,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"
_CORPUS_NINE = _REPO_ROOT / "replays" / "ml_corpus" / "9p2i"
_CORPUS_FOUR = _REPO_ROOT / "replays" / "ml_corpus" / "4p1i"
_CHAMPION_CLOSE_ROW = (
    _REPO_ROOT / "training" / "reports" / "results-champion-close.jsonl"
)

_B3_9P2I = _BASELINE_SUPPLY_FLOORS["baseline-3"]["9p2i"]
_B3_4P1I = _BASELINE_SUPPLY_FLOORS["baseline-3"]["4p1i"]


def _champion_watchability() -> dict[str, Any]:
    """The committed champion-close row's ``watchability`` blob (read-only)."""

    row: dict[str, Any] = json.loads(_CHAMPION_CLOSE_ROW.read_text())
    blob: dict[str, Any] = row["watchability"]
    return blob


def _recorded_gauges(blob: dict[str, Any]) -> SupplyGaugeValues:
    """The fixture's RECORDED measured gauges as Layer-1 inputs.

    The committed row records the measured RATES (the referee's stable JSON
    schema), not the raw counts behind them; the floor evaluation and the
    16.11 derivation consume only the rates, so the count fields carry the
    row-consistent context values where the row pins them (139 meetings, 423
    flags — cross-checked below) and 0 where unrecorded/unread.
    """

    by_name = {g["name"]: g for g in blob["supply_gauges"]}
    meetings_total = sum(g["n_meetings"] for g in blob["per_game"])
    assert meetings_total == 139  # the close audit §4's resolved-meeting count
    flags_measured: float = by_name["flags_per_meeting"]["measured"]
    assert flags_measured == 423 / 139  # the recorded rate is the exact census
    return SupplyGaugeValues(
        witnessed_event_rate=by_name["witnessed_event_rate"]["measured"],
        total_kills=0,
        crew_witnessed_kills=0,
        flags_per_meeting=flags_measured,
        total_flags=423,
        persisted_vent_flags=0,
        meetings_total=meetings_total,
        testimony_backed_conversion=by_name["testimony_backed_conversion"]["measured"],
        backed_conversion_attempted=0,
        backed_conversion_converted=0,
    )


# --------------------------------------------------------------------------- #
# The champion-close fixture — the §10 ruling, derived rather than ruled       #
# --------------------------------------------------------------------------- #


def test_champion_close_fixture_recorded_the_old_definition_fail() -> None:
    """HISTORICAL CONTRAST: the committed row's FAIL vs the absolute floor.

    The 15.23 close recorded ``referee_passed: false`` on exactly one gauge —
    conversion 0.5743 vs the FSM baseline's absolute 0.6636 (close audit §3).
    The row is untouched by 16.11 (the fixture is read, never rewritten); this
    pins the old-definition verdict the re-anchor is measured against, and that
    the recorded floor IS the module's still-pinned anchor (no drift).
    """

    blob = _champion_watchability()
    assert blob["baseline_id"] == "baseline-3"
    assert blob["roster_key"] == "9p2i"
    assert blob["integrity_ok"] is True
    assert blob["referee_passed"] is False
    assert blob["supply_floors_passed"] is False
    by_name = {g["name"]: g for g in blob["supply_gauges"]}
    conversion = by_name["testimony_backed_conversion"]
    assert conversion["measured"] == 58 / 101
    pin = _B3_9P2I.testimony_backed_conversion
    assert pin is not None
    assert conversion["floor"] == pin.value == 71 / 107  # the then-absolute constant
    assert conversion["passed"] is False
    # The one-gauge shape of the miss: both supply gauges passed with margin.
    assert by_name["witnessed_event_rate"]["passed"] is True
    assert by_name["flags_per_meeting"]["passed"] is True


def test_champion_close_fixture_rescored_is_nonblocking_under_the_reanchor() -> None:
    """THE CALIBRATION REPRODUCTION: recorded gauges re-score to non-blocking.

    Under the population-relative definition the champion's own evidence
    density (flags 423/139 = 3.0432, 1.63× the baseline's) derives a floor of
    0.40628797419411855 < the recorded 0.5743, so the conversion gauge PASSES
    and — with the recorded ``integrity_ok: true`` — the outcome is the
    non-blocking one the owner ruling anticipated (close audit §10), now
    derived rather than ruled.
    """

    blob = _champion_watchability()
    gauges = _recorded_gauges(blob)
    passed, rows = evaluate_supply_floors(gauges, _B3_9P2I)
    by_name = {row.name: row for row in rows}
    conversion = by_name["testimony_backed_conversion"]
    assert _B3_9P2I.testimony_backed_conversion is not None
    expected_floor = population_relative_conversion_floor(
        pinned_conversion=_B3_9P2I.testimony_backed_conversion.value,
        pinned_flags_per_meeting=_B3_9P2I.flags_per_meeting.value,
        measured_flags_per_meeting=gauges.flags_per_meeting,
    )
    assert conversion.floor == expected_floor == 0.40628797419411855
    assert conversion.measured == 58 / 101
    assert conversion.passed is True
    assert conversion.advisory is False  # the pin numerator (71) keeps its teeth
    # Every gauge clears — the miss was confined to the re-anchored one.
    assert all(row.passed for row in rows)
    assert passed is True
    # The composed non-blocking outcome: supply floors PASS + recorded integrity.
    assert blob["integrity_ok"] is True


def test_champion_close_fixture_still_fails_under_the_absolute_variant() -> None:
    """The contrast is the MODE, not the pins: absolute floors still FAIL it.

    Re-scoring the same recorded gauges with ``population_relative_conversion``
    off (the pre-16.11 behavior, pins unchanged) reproduces the recorded FAIL —
    the re-anchor, not any pin edit, is what flips the fixture's outcome.
    """

    gauges = _recorded_gauges(_champion_watchability())
    absolute = dataclasses.replace(_B3_9P2I, population_relative_conversion=False)
    passed, rows = evaluate_supply_floors(gauges, absolute)
    conversion = next(r for r in rows if r.name == "testimony_backed_conversion")
    assert conversion.floor == 71 / 107
    assert conversion.passed is False
    assert passed is False


# --------------------------------------------------------------------------- #
# The starvation catch — sharp regardless of population                        #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "flags_per_meeting",
    [
        pytest.param(0.9, id="supply-below-baseline"),
        pytest.param(1.8633093525179856, id="supply-at-baseline"),
        pytest.param(6.0, id="supply-far-above-baseline"),
    ],
)
def test_synthetic_starved_set_fails_regardless_of_population(
    flags_per_meeting: float,
) -> None:
    """Zero backed accusations FAIL the derived floor at ANY supply level.

    The contract's synthetic starved set: a high meeting rate (bodies still
    trigger meetings after testimony has died) with ZERO backed accusations —
    conversion measures ``None`` (undefined, not 0.0) and the derived floor is
    numeric at every population supply level, so the gauge fails and the set
    fails Layer 1. The floor's reason to exist survives the re-anchor.
    """

    starved = SupplyGaugeValues(
        witnessed_event_rate=0.25,
        total_kills=120,
        crew_witnessed_kills=30,
        flags_per_meeting=flags_per_meeting,
        total_flags=int(flags_per_meeting * 60),
        persisted_vent_flags=0,
        meetings_total=60,
        testimony_backed_conversion=None,
        backed_conversion_attempted=0,
        backed_conversion_converted=0,
    )
    passed, rows = evaluate_supply_floors(starved, _B3_9P2I)
    conversion = next(r for r in rows if r.name == "testimony_backed_conversion")
    assert conversion.measured is None
    assert conversion.floor is not None  # numeric — None measured cannot clear it
    assert conversion.passed is False
    assert passed is False


def test_zero_conversion_with_backed_supply_also_fails() -> None:
    """A set whose backed accusations NEVER convert fails even with rich supply.

    Starvation's twin: backed testimony exists (measured 0.0, not ``None``) but
    the crew never convict on it. The derived floor is strictly positive by
    construction (a positive pin times a positive ratio), so 0.0 fails at any
    supply density.
    """

    never_converts = SupplyGaugeValues(
        witnessed_event_rate=0.25,
        total_kills=120,
        crew_witnessed_kills=30,
        flags_per_meeting=6.0,
        total_flags=360,
        persisted_vent_flags=0,
        meetings_total=60,
        testimony_backed_conversion=0.0,
        backed_conversion_attempted=40,
        backed_conversion_converted=0,
    )
    passed, rows = evaluate_supply_floors(never_converts, _B3_9P2I)
    conversion = next(r for r in rows if r.name == "testimony_backed_conversion")
    assert conversion.floor is not None and conversion.floor > 0.0
    assert conversion.passed is False
    assert passed is False


# --------------------------------------------------------------------------- #
# FSM-baseline self-consistency — PASS at exact equality                       #
# --------------------------------------------------------------------------- #


def test_fsm_baseline_sets_pass_at_exact_equality_under_the_reanchor() -> None:
    """The committed default (baseline-6) sets clear their own DERIVED floor.

    At the baseline's own evidence density the supply ratio is exactly 1.0 and
    the derived floor IS the pin — an exact float identity, not an approximate
    one (the derivation multiplies the pin by the ratio, in that order, so
    "the baseline passes at equality" survives the re-anchor bit-exact). Re-pinned
    to the vent-widening baseline-6 conversion pins (9p2i 78/136, 4p1i 9/30; the
    pre-widening baseline-6 record was 78/133 and 10/30).
    """

    expected = {_NINE: 78 / 136, _FOUR: 9 / 30}
    for sample_dir, fraction in expected.items():
        report = compute_watchability(sample_dir)
        assert report.referee_passed is True, sample_dir.name
        assert report.supply_floors_passed is True, sample_dir.name
        conversion = next(
            g for g in report.supply_gauges if g.name == "testimony_backed_conversion"
        )
        assert conversion.measured == fraction, sample_dir.name
        assert conversion.floor == fraction, sample_dir.name
        assert conversion.passed is True, sample_dir.name


def test_remeasured_corpus_sets_at_baseline5_referee_verdicts() -> None:
    """The Task-17.9 re-record re-grounds both corpus sets to baseline 5.

    The corpus is now measured against its OWN baseline-5 block — the Q3
    restoration: same-substrate evidence again, no longer the DEGRADED-Q3
    stale-context read that pinned the prior baseline-3 recording to the
    baseline-3 floors. The honest baseline-5 verdicts DIVERGE from the
    baseline-3 close-audit PASS:

    * 4p1i still PASSES — its conversion clears the derived population-relative
      floor and the one-event ``witnessed_event_rate`` floor is advisory.
    * 9p2i now FAILS the referee on ``witnessed_event_rate`` (0.0334 < the 0.0345
      floor, a narrow rate miss that is NOT the one-event advisory case) even
      though its conversion and flag-density floors clear. This is the expected
      direction under the co-adapted baseline-5 economy (17.5/17.12: a
      starved-supply rejection is the instrument working, never silent); the
      surrogate/bake-off consume the corpus as a TRAINING substrate regardless
      of this watchability verdict.
    """

    corpus_nine = compute_watchability(_CORPUS_NINE, baseline_id="baseline-5")
    assert corpus_nine.integrity_ok is True
    assert corpus_nine.supply_floors_passed is False  # witnessed_event_rate miss
    assert corpus_nine.referee_passed is False
    witnessed_nine = next(
        g for g in corpus_nine.supply_gauges if g.name == "witnessed_event_rate"
    )
    assert witnessed_nine.measured == 0.0333889816360601
    assert witnessed_nine.floor == 0.034482758620689655
    assert witnessed_nine.passed is False  # a real rate miss, blocks the floor AND
    conversion_nine = next(
        g for g in corpus_nine.supply_gauges if g.name == "testimony_backed_conversion"
    )
    assert conversion_nine.measured == 0.5333333333333333
    assert conversion_nine.floor == 0.37816259549905257  # derived population-relative
    assert (
        conversion_nine.passed is True
    )  # conversion clears; the miss is witnessed-supply

    corpus_four = compute_watchability(_CORPUS_FOUR, baseline_id="baseline-5")
    assert corpus_four.integrity_ok is True
    assert (
        corpus_four.supply_floors_passed is True
    )  # witnessed miss is advisory (one-event)
    assert corpus_four.referee_passed is True
    conversion_four = next(
        g for g in corpus_four.supply_gauges if g.name == "testimony_backed_conversion"
    )
    assert conversion_four.measured == 0.5405405405405406
    assert conversion_four.floor == 0.29304029304029305  # derived population-relative
    assert conversion_four.passed is True


def test_baseline_modes_are_pinned_per_block() -> None:
    """baseline-3 carries the re-anchor; the frozen baseline-2 stays absolute."""

    for roster, floors in _BASELINE_SUPPLY_FLOORS["baseline-3"].items():
        assert floors.population_relative_conversion is True, roster
    for roster, floors in _BASELINE_SUPPLY_FLOORS["baseline-2"].items():
        assert floors.population_relative_conversion is False, roster


# --------------------------------------------------------------------------- #
# The derivation itself — pure, quotable, fail-loud                            #
# --------------------------------------------------------------------------- #


def test_derived_floor_equals_the_pin_at_the_baseline_density() -> None:
    """Equality self-consistency, bit-exact — for both baseline-3 rosters."""

    for floors in (_B3_9P2I, _B3_4P1I):
        assert floors.testimony_backed_conversion is not None
        derived = population_relative_conversion_floor(
            pinned_conversion=floors.testimony_backed_conversion.value,
            pinned_flags_per_meeting=floors.flags_per_meeting.value,
            measured_flags_per_meeting=floors.flags_per_meeting.value,
        )
        assert derived == floors.testimony_backed_conversion.value


def test_derived_floor_scales_inversely_with_evidence_density() -> None:
    """Twice the per-meeting evidence supply demands half the conversion rate."""

    base = population_relative_conversion_floor(
        pinned_conversion=0.6,
        pinned_flags_per_meeting=2.0,
        measured_flags_per_meeting=2.0,
    )
    doubled = population_relative_conversion_floor(
        pinned_conversion=0.6,
        pinned_flags_per_meeting=2.0,
        measured_flags_per_meeting=4.0,
    )
    assert base == 0.6
    assert doubled == 0.3


def test_derived_floor_caps_at_one_for_evidence_poor_sets() -> None:
    """Below-baseline supply RAISES the demand, capped at the reachable 1.0.

    (Such a set already fails the ``flags_per_meeting`` floor itself — the
    re-anchor only ever RELAXES the bar for sets that clear the supply floors.)
    """

    raised = population_relative_conversion_floor(
        pinned_conversion=0.6,
        pinned_flags_per_meeting=2.0,
        measured_flags_per_meeting=1.5,
    )
    assert raised == 0.7999999999999999  # 0.6 * (2.0 / 1.5), below the cap
    capped = population_relative_conversion_floor(
        pinned_conversion=0.6,
        pinned_flags_per_meeting=2.0,
        measured_flags_per_meeting=0.5,
    )
    assert capped == 1.0


def test_derived_floor_is_maximal_without_per_meeting_evidence() -> None:
    """No meetings (``None``) or zero flags -> the maximal demand 1.0."""

    assert (
        population_relative_conversion_floor(
            pinned_conversion=0.6,
            pinned_flags_per_meeting=2.0,
            measured_flags_per_meeting=None,
        )
        == 1.0
    )
    assert (
        population_relative_conversion_floor(
            pinned_conversion=0.6,
            pinned_flags_per_meeting=2.0,
            measured_flags_per_meeting=0.0,
        )
        == 1.0
    )


def test_derived_floor_rejects_degenerate_pins() -> None:
    """A non-measurable anchor fails loud (no silent fallbacks)."""

    with pytest.raises(ValueError, match="pinned_conversion"):
        population_relative_conversion_floor(
            pinned_conversion=0.0,
            pinned_flags_per_meeting=2.0,
            measured_flags_per_meeting=1.0,
        )
    with pytest.raises(ValueError, match="pinned_conversion"):
        population_relative_conversion_floor(
            pinned_conversion=1.2,
            pinned_flags_per_meeting=2.0,
            measured_flags_per_meeting=1.0,
        )
    with pytest.raises(ValueError, match="pinned_flags_per_meeting"):
        population_relative_conversion_floor(
            pinned_conversion=0.6,
            pinned_flags_per_meeting=0.0,
            measured_flags_per_meeting=1.0,
        )
