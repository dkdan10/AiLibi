"""Tests for eval/watchability.py (Task 15.2 — the selection referee).

Three pillars, per the Definition of Done:

* **Geomean parity** — on the committed 9p2i bytes the referee reproduces the lab
  scorer's per-game D1-D4 + composed scores EXACTLY (the committed
  ``experiments/lab/results-rubric-geomean.json`` is the fixture; any mismatch is
  a task failure). The referee also runs on 4p1i, which has no committed rubric
  artifact (the asymmetry is handled, not assumed away).
* **Floor trips** — a railroaded crew ejection, a friendly-fire kill, and a
  determinism breach each force a game's score to 0 (synthetic ``_GameFacts``).
* **Evidence-supply floors** — baseline 2 passes its own pinned floors; a synthetic
  evidence-starved set (high meeting rate, zero flags, zero witnesses) FAILS.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from eval.watchability import (
    SupplyFloors,
    SupplyGaugeValues,
    WatchabilityReport,
    _Accusation,
    _GameFacts,
    _MeetingFacts,
    _TestimonyRecord,
    _TestimonyTurn,
    compute_game_score,
    compute_watchability,
    evaluate_supply_floors,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"
_GEOMEAN_FIXTURE = _REPO_ROOT / "experiments" / "lab" / "results-rubric-geomean.json"

# The per-game keys the geomean parity test pins against the lab scorer's
# committed artifact (the shared D1-D4 breakdown + composition).
_PARITY_KEYS = (
    "floor_multiplier",
    "d1_resolution",
    "d2_deduction",
    "d3_craft",
    "d4_arc",
    "d2_separation_norm",
    "d2_conversion",
    "d4_arc_term",
    "d4_swing_term",
    "d4_contest_term",
    "score",
)


# --------------------------------------------------------------------------- #
# Geomean parity                                                              #
# --------------------------------------------------------------------------- #


def test_geomean_parity_reproduces_lab_scorer_on_9p2i() -> None:
    """Per-game D1-D4 + composed scores match the committed lab geomean artifact."""

    fixture = json.loads(_GEOMEAN_FIXTURE.read_text())
    ref_by_seed = {row["seed"]: row for row in fixture["per_game"]}

    report = compute_watchability(_NINE)
    assert report.games_total == 50
    assert {s.seed for s in report.per_game} == set(ref_by_seed)

    for score in report.per_game:
        ref = ref_by_seed[score.seed]
        assert score.reason == ref["reason"]
        assert score.n_meetings == ref["n_meetings"]
        for key in _PARITY_KEYS:
            assert getattr(score, key) == pytest.approx(ref[key], abs=1e-6), (
                f"seed {score.seed} {key}"
            )

    assert report.mean_score == pytest.approx(fixture["mean_score"])
    assert report.median_score == pytest.approx(fixture["median_score"])
    # The fixture's floored games (0.0 score on a railroad breach) reproduce.
    floored = {s.seed for s in report.per_game if s.floor_multiplier == 0.0}
    assert floored == set(
        fixture["validation"]["no_perverse_gradient"]["floored_games"]
    )


def test_referee_runs_on_both_sets_from_bytes_including_4p1i() -> None:
    """The referee runs on BOTH committed sets — 4p1i has no committed rubric."""

    for sample_dir in (_NINE, _FOUR):
        report = compute_watchability(sample_dir)
        assert report.games_total > 0
        assert report.per_game
        assert report.integrity_ok is True
        assert report.referee_passed is True


def test_watchability_report_json_round_trips() -> None:
    report = compute_watchability(_FOUR)
    text = report.model_dump_json()
    back = WatchabilityReport.model_validate_json(text)
    assert back == report


# --------------------------------------------------------------------------- #
# Floor trips (synthetic games)                                              #
# --------------------------------------------------------------------------- #


def _clean_meeting(
    *,
    ejected: str | None = "p-0",
    ejected_role: str | None = "IMPOSTOR",
    among: float | None = 0.8,
) -> _MeetingFacts:
    """A single meeting that ejects the true impostor on backed testimony."""

    return _MeetingFacts(
        meeting_index=0,
        ejected_player_id=ejected,
        ejected_role=ejected_role,  # type: ignore[arg-type]
        suspicion_graph_by_voter={
            "p-1": {"p-0": 0.8, "p-2": 0.2},
            "p-2": {"p-0": 0.7, "p-1": 0.2},
        },
        rendered_suspicion_by_target={"p-0": 0.8, "p-1": 0.2, "p-2": 0.2},
        testimony_records=(
            _TestimonyRecord(
                subject="p-0",
                subject_role="IMPOSTOR",
                testimony_turns=(
                    _TestimonyTurn(vehicle="accusation", observation_backed=True),
                ),
            ),
        ),
        accusations=(_Accusation(speaker="p-1", accused="p-0"),),
        plurality_target="p-0",
        plurality_margin=2,
        ejected_rendered_suspicion_among_ejectors=among,
        contradictions_by_subject={},
    )


def _clean_game(**overrides: object) -> _GameFacts:
    roles = {"p-0": "IMPOSTOR", "p-1": "CREWMATE", "p-2": "CREWMATE", "p-3": "CREWMATE"}
    defaults: dict[str, object] = {
        "seed": 0,
        "reason": "CREWMATE_EJECT",
        "roles": roles,
        "meetings": (_clean_meeting(),),
        "kill_victim_roles": ("CREWMATE",),
        "trajectories": {},
        "integrity_ok": True,
    }
    defaults.update(overrides)
    return _GameFacts(**defaults)  # type: ignore[arg-type]


def test_clean_game_scores_above_zero() -> None:
    """The baseline synthetic game scores > 0 — so a floor trip is the cause of 0."""

    score = compute_game_score(_clean_game())
    assert score.floor_multiplier == 1.0
    assert score.score > 0.0


def test_friendly_fire_kill_forces_score_zero() -> None:
    """An impostor victim (engine-forbidden) floors the whole game to 0."""

    score = compute_game_score(_clean_game(kill_victim_roles=("IMPOSTOR",)))
    assert score.floor_multiplier == 0.0
    assert score.score == 0.0


def test_railroaded_ejection_forces_score_zero() -> None:
    """A crewmate ejected with no over-gate suspicion (a railroad) floors to 0."""

    railroad_meeting = _MeetingFacts(
        meeting_index=0,
        ejected_player_id="p-3",
        ejected_role="CREWMATE",
        suspicion_graph_by_voter={"p-1": {"p-3": 0.1}},
        rendered_suspicion_by_target={"p-3": 0.1},
        testimony_records=(),
        accusations=(),
        plurality_target="p-3",
        plurality_margin=1,
        # Below the §4.6 gate among the ejectors -> gate-bypass railroad.
        ejected_rendered_suspicion_among_ejectors=None,
        contradictions_by_subject={},
    )
    score = compute_game_score(
        _clean_game(reason="CREWMATE_TASKS", meetings=(railroad_meeting,))
    )
    assert score.floor_multiplier == 0.0
    assert score.score == 0.0


def test_determinism_breach_forces_score_zero() -> None:
    """A firewall/determinism breach (integrity_ok False) floors to 0."""

    score = compute_game_score(_clean_game(integrity_ok=False))
    assert score.floor_multiplier == 0.0
    assert score.score == 0.0


def test_honest_mistaken_crew_ejection_is_not_railroaded() -> None:
    """A crewmate ejected ABOVE the gate WITH a flag is a mistake, not a railroad."""

    honest_meeting = _MeetingFacts(
        meeting_index=0,
        ejected_player_id="p-3",
        ejected_role="CREWMATE",
        suspicion_graph_by_voter={"p-1": {"p-3": 0.8}},
        rendered_suspicion_by_target={"p-3": 0.8},
        testimony_records=(),
        accusations=(),
        plurality_target="p-3",
        plurality_margin=1,
        ejected_rendered_suspicion_among_ejectors=0.8,
        contradictions_by_subject={"p-3": (True,)},
    )
    score = compute_game_score(
        _clean_game(reason="CREWMATE_TASKS", meetings=(honest_meeting,))
    )
    assert score.floor_multiplier == 1.0


# --------------------------------------------------------------------------- #
# Evidence-supply floors                                                     #
# --------------------------------------------------------------------------- #

_BASELINE_2_9P2I_FLOORS = SupplyFloors(
    witnessed_event_rate=0.0375,
    flags_per_meeting=2.007042253521127,
    testimony_backed_conversion=0.5042016806722689,
)


def test_baseline_2_supply_floors_pass() -> None:
    """The referee accepts baseline 2 — it clears its own pinned supply floors."""

    for sample_dir in (_NINE, _FOUR):
        report = compute_watchability(sample_dir)
        assert report.supply_floors_passed is True
        assert all(gauge.passed for gauge in report.supply_gauges)


def test_baseline_2_witnessed_event_rate_is_the_measured_anchor() -> None:
    """The 9p2i witnessed-event rate is the §6 6/160 = 3.75% crew-witnessed anchor."""

    report = compute_watchability(_NINE)
    witnessed = next(
        g for g in report.supply_gauges if g.name == "witnessed_event_rate"
    )
    assert witnessed.measured == pytest.approx(6 / 160)


def test_evidence_starved_set_fails_the_referee() -> None:
    """High meeting rate but zero flags + zero witnesses FAILS every supply floor."""

    starved = SupplyGaugeValues(
        witnessed_event_rate=0.0,  # zero witnesses
        total_kills=200,
        crew_witnessed_kills=0,
        flags_per_meeting=0.0,  # zero flags
        total_flags=0,
        persisted_vent_flags=0,
        meetings_total=150,  # high meeting rate — bodies still trigger meetings
        testimony_backed_conversion=0.0,
        impostor_accused_meetings=50,
        impostor_accused_conversions=0,
    )
    passed, gauges = evaluate_supply_floors(starved, _BASELINE_2_9P2I_FLOORS)
    assert passed is False
    assert all(gauge.passed is False for gauge in gauges)


def test_none_measured_gauge_fails_a_numeric_floor() -> None:
    """A None measured gauge (e.g. zero kills) does NOT pass a numeric floor."""

    no_kills = SupplyGaugeValues(
        witnessed_event_rate=None,
        total_kills=0,
        crew_witnessed_kills=0,
        flags_per_meeting=2.5,
        total_flags=300,
        persisted_vent_flags=0,
        meetings_total=120,
        testimony_backed_conversion=0.6,
        impostor_accused_meetings=40,
        impostor_accused_conversions=24,
    )
    passed, gauges = evaluate_supply_floors(no_kills, _BASELINE_2_9P2I_FLOORS)
    assert passed is False
    witnessed = next(g for g in gauges if g.name == "witnessed_event_rate")
    assert witnessed.passed is False


def test_flags_per_meeting_is_vent_aware() -> None:
    """A persisted role-proving vent_sighting flag is MERGED into the flag census.

    ``compute_supply_gauges`` re-derives flags from the transcript and cannot
    reproduce a grounded ``vent_sighting`` flag (its grounding channel has no
    transcript id, Task 15.4), so the referee merges the persisted vent flags —
    else a vent-rich baseline-3 candidate's strongest evidence reads as starved.
    The committed v4 sets carry none, so the pinned baseline-2 floors are unchanged.
    """

    from eval.validity import assemble_tournament_report
    from eval.watchability import _persisted_vent_flag_count, _supply_gauge_values
    from meetings.schemas import ContradictionRef

    report = assemble_tournament_report(_FOUR)
    # The committed set is v4 — zero vent flags, so nothing is double-counted and
    # the pinned floor stays put.
    assert _persisted_vent_flag_count(report) == 0

    game = next(g for g in report.games if g.meetings)
    subject = next(iter(game.roles))
    vent = ContradictionRef(
        contradiction_id="c-vent-test",
        kind="vent_sighting",
        event_a_id=game.meetings[0].transcript.turns[0].turn_id
        if game.meetings[0].transcript.turns
        else "m:turn-0",
        event_b_id="m:turn-0",
        subjects=(subject,),
        description="witnessed impostor vent",
    )
    meeting_with_vent = game.meetings[0].model_copy(
        update={"contradictions": game.meetings[0].contradictions + (vent,)}
    )
    game_with_vent = game.model_copy(
        update={"meetings": (meeting_with_vent, *game.meetings[1:])}
    )
    report_with_vent = report.model_copy(
        update={
            "games": tuple(game_with_vent if g is game else g for g in report.games)
        }
    )

    assert _persisted_vent_flag_count(report_with_vent) == 1
    before = _supply_gauge_values(report, [])
    after = _supply_gauge_values(report_with_vent, [])
    assert after.persisted_vent_flags == 1
    assert after.total_flags == before.total_flags + 1
    assert after.flags_per_meeting is not None and before.flags_per_meeting is not None
    assert after.flags_per_meeting > before.flags_per_meeting


def test_saw_vent_observation_counts_as_backed_evidence() -> None:
    """A witnessed impostor vent is first-hand role-proving evidence (Task 15.4).

    ``_testimony_vehicle`` must treat a :class:`SawVentObservation` like a
    :class:`SawPlayerObservation` — observation-backing, and a sighting of its
    subject — so a vent-backed accusation converts in D2 without a redundant
    player-sighting. (The pre-15.4 audit extractor omits the type; the referee
    recognizes it. Committed v4 sets carry none, so parity is unchanged.)
    """

    from eval.watchability import _testimony_vehicle
    from meetings.schemas import AccusationClaim, MeetingTurn, SawVentObservation

    vent = SawVentObservation(
        type="saw_vent", tick=100, subject="p-0", room="Cafeteria"
    )

    # An accusation of the vent subject, backed ONLY by the vent sighting.
    accuse_turn = MeetingTurn(
        turn_id="m:turn-1",
        turn_index=1,
        speaker="p-1",
        turn_kind="reply",
        reply_to=None,
        observations=(vent,),
        claims=(
            AccusationClaim(
                type="accusation", against="p-0", confidence=0.9, reason="vent"
            ),
        ),
        free_text="I watched p-0 drop into the vent.",
    )
    vehicle, backed = _testimony_vehicle(accuse_turn, "p-0")
    assert vehicle == "accusation"
    assert backed is True

    # A bare vent sighting (no accusation) still names its subject as a sighting.
    sight_turn = MeetingTurn(
        turn_id="m:turn-2",
        turn_index=2,
        speaker="p-2",
        turn_kind="opt_in",
        reply_to=None,
        observations=(vent,),
        claims=(),
        free_text="",
    )
    vehicle2, backed2 = _testimony_vehicle(sight_turn, "p-0")
    assert vehicle2 == "sighting"
    assert backed2 is True


def test_none_conversion_floor_is_vacuously_cleared() -> None:
    """A None conversion floor (baseline supplied no accused-impostor meeting) passes."""

    floors = SupplyFloors(
        witnessed_event_rate=0.0,
        flags_per_meeting=0.0,
        testimony_backed_conversion=None,
    )
    gauges = SupplyGaugeValues(
        witnessed_event_rate=0.1,
        total_kills=10,
        crew_witnessed_kills=1,
        flags_per_meeting=1.0,
        total_flags=10,
        persisted_vent_flags=0,
        meetings_total=10,
        testimony_backed_conversion=None,
        impostor_accused_meetings=0,
        impostor_accused_conversions=0,
    )
    passed, gauge_reports = evaluate_supply_floors(gauges, floors)
    assert passed is True
    conversion = next(
        g for g in gauge_reports if g.name == "testimony_backed_conversion"
    )
    assert conversion.passed is True


# --------------------------------------------------------------------------- #
# Baseline resolution guards (no silent fallback)                            #
# --------------------------------------------------------------------------- #


def test_unknown_baseline_id_raises() -> None:
    with pytest.raises(KeyError, match="baseline-99"):
        compute_watchability(_NINE, baseline_id="baseline-99")


def test_missing_dir_raises() -> None:
    with pytest.raises(NotADirectoryError):
        compute_watchability(_REPO_ROOT / "replays" / "samples" / "nope")


# --------------------------------------------------------------------------- #
# The scripts/measure_baseline.py --watchability fold                        #
# --------------------------------------------------------------------------- #
# eval.watchability -> eval.validity puts scripts/ on sys.path at import time,
# so the top-level ``measure_baseline`` module resolves here.
import measure_baseline  # noqa: E402


def test_cli_watchability_json_emits_per_game_and_aggregate() -> None:
    """--watchability --json emits per-game + aggregate referee results per set."""

    import io
    from contextlib import redirect_stdout

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        assert measure_baseline.main([str(_NINE), "--watchability", "--json"]) == 0
    payload = json.loads(buffer.getvalue())
    assert isinstance(payload, list)
    assert len(payload) == 1
    report = payload[0]
    assert report["referee_passed"] is True
    assert report["roster_key"] == "9p2i"
    assert report["baseline_id"] == "baseline-2"
    assert len(report["per_game"]) == 50
    assert len(report["supply_gauges"]) == 3
    assert report["mean_score"] == pytest.approx(46.44)


def test_cli_watchability_human_output() -> None:
    import io
    from contextlib import redirect_stdout

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        assert measure_baseline.main([str(_FOUR), "--watchability"]) == 0
    out = buffer.getvalue()
    assert "Watchability referee" in out
    assert "evidence-supply floors" in out
    assert "4p1i" in out
