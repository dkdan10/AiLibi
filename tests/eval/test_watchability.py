"""Tests for eval/watchability.py (Task 15.2 referee; Task 15.19 hardening).

Four pillars:

* **Historical geomean parity (frozen pin)** — on the committed 9p2i bytes the
  referee's ``historical_15_2`` mode reproduces the lab scorer's per-game D1-D4
  + composed scores EXACTLY (the committed
  ``experiments/lab/results-rubric-geomean.json`` is the fixture) — 15.2's
  cross-implementation evidence stays reproducible under the FROZEN pre-15.19
  spec. The live referee also runs on 4p1i, which has no committed rubric
  artifact (the asymmetry is handled, not assumed away).
* **Task-15.19 hardening** — the 15.14 exploit-trajectory shape (high D2
  separation, zero conversion, zero flags) scores 0 on the D2 term; backing is
  SUBJECT-AWARE (a vent sighting of X cannot back an accusation of Y); rare-event
  floors with a baseline numerator ≤ 1 are advisory (reported, never
  referee-failing) so ``replays/ml_corpus/4p1i`` passes the referee.
* **Floor trips** — a railroaded crew ejection, a friendly-fire kill, and a
  determinism breach each force a game's score to 0 (synthetic ``_GameFacts``).
* **Evidence-supply floors** — the committed baseline (baseline-6) passes its own
  pinned floors (subject-aware since 15.19, re-recorded on the meeting-layer
  graduation slate at Task 18.12, with the ML corpus re-ground onto the same
  substrate at Task 18.13); a synthetic evidence-starved set (high meeting rate,
  zero flags, zero witnesses) FAILS.
"""

from __future__ import annotations

import json
import math
import statistics
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from eval import watchability as watchability_module
from eval.watchability import (
    _BASELINE_SUPPLY_FLOORS,
    REFEREE_READS,
    FloorPin,
    SupplyFloorGauge,
    SupplyFloors,
    SupplyGaugeValues,
    WatchabilityGameScore,
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
_CORPUS_FOUR = _REPO_ROOT / "replays" / "ml_corpus" / "4p1i"
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
# Geomean parity — FROZEN HISTORICAL PIN (Task 15.19)                         #
# --------------------------------------------------------------------------- #


def _score_committed_set(
    sample_dir: Path, *, historical_15_2: bool = False
) -> list[WatchabilityGameScore]:
    """Fold a committed set to per-game scores under the chosen doctrine.

    Replicates :func:`compute_watchability`'s facts assembly (report + re-seeded
    roles + reconstruction) so the FROZEN ``historical_15_2`` spec can be scored
    without exposing the parity-only mode on the composed public referee.
    """

    from engine.world import load_canonical_map
    from eval.validity import (
        assemble_tournament_report,
        resolve_roster_knobs,
        roles_by_seed,
    )
    from eval.watchability import _game_facts, _KillWitnessFact, _reconstruct_kills

    report = assemble_tournament_report(sample_dir)
    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    game_map = load_canonical_map()
    per_seed_roles = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    reconstruction = _reconstruct_kills(sample_dir)
    kills_by_seed: dict[int, list[_KillWitnessFact]] = {}
    for kill in reconstruction.kills:
        kills_by_seed.setdefault(kill.seed, []).append(kill)
    return [
        compute_game_score(
            _game_facts(
                game,
                per_seed_roles[game.seed],
                [kill.victim_role for kill in kills_by_seed.get(game.seed, [])],
                integrity_ok=reconstruction.integrity_ok,
            ),
            historical_15_2=historical_15_2,
        )
        for game in report.games
    ]


def test_historical_15_2_geomean_parity_frozen_pin_on_9p2i() -> None:
    """HISTORICAL PIN: the frozen pre-15.19 spec's parity fixture, kept as history.

    Task 15.2's cross-implementation evidence — the committed
    ``experiments/lab/results-rubric-geomean.json`` against this module on the
    same 9p2i bytes — reproduced all fifty rows to 1e-6 under
    ``historical_15_2=True`` on every record up to baseline 9. Those bytes left
    ``replays/samples/9p2i`` when candidate round 2 was promoted (2026-10-02),
    and the gameplay-facts extractor that wrote the fixture does not read the
    promoted era, so the fixture cannot be regenerated. Its byte recomputation
    is RETIRED, as the baseline-2 block's was when its bytes left the tree: the
    fixture is held to itself and to the baseline-9 MANIFEST it names
    (``27646d67``, the samples-9p2i recording at ``d41c9006``), and never re-derived.
    """

    fixture = json.loads(_GEOMEAN_FIXTURE.read_text())
    rows = fixture["per_game"]
    assert len(rows) == 50
    assert {row["seed"] for row in rows} == set(range(50))
    # The baseline-9 samples-9p2i MANIFEST the fixture was scored on; the
    # promoted set's MANIFEST is a different recording.
    from experiments.lab.rubric_score import _set_manifest_sha

    assert fixture["git_head"] == "27646d67"
    assert _set_manifest_sha(_NINE) != fixture["git_head"]
    # The aggregate roll-ups, recomputed from the fixture's own rows exactly as
    # WatchabilityReport rounds them, as recorded on the baseline-9 bytes.
    scores = [row["score"] for row in rows]
    mean = round(math.fsum(scores) / len(scores), 2)
    median = round(statistics.median(scores), 2)
    assert mean == pytest.approx(50.54)
    assert median == pytest.approx(50.7)
    assert fixture["mean_score"] == pytest.approx(mean)
    assert fixture["median_score"] == pytest.approx(median)
    floored = {row["seed"] for row in rows if row["floor_multiplier"] == 0.0}
    assert floored == {6, 12, 13, 38, 39}
    assert fixture["validation"]["no_perverse_gradient"]["floored_games"] == sorted(
        floored
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
                    _TestimonyTurn(
                        vehicle="accusation",
                        observation_backed=True,
                        observation_backed_any=True,
                    ),
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
# Task 15.19 patch 1 — the conversion-coupled D2 separation term              #
# --------------------------------------------------------------------------- #


def _suspicion_theater_meeting(
    *, contradictions: dict[str, tuple[bool, ...]] | None = None
) -> _MeetingFacts:
    """A 15.14-shaped meeting: high separation, no ejection, no backed testimony."""

    return _MeetingFacts(
        meeting_index=0,
        ejected_player_id=None,
        ejected_role=None,
        # Rendered suspicion tracks the impostor's kill count (separation
        # 0.85 - 0.10 = 0.75 >= the 0.30 scale -> separation_norm 1.0) ...
        suspicion_graph_by_voter={
            "p-1": {"p-0": 0.9, "p-2": 0.1},
            "p-2": {"p-0": 0.8, "p-1": 0.1},
        },
        rendered_suspicion_by_target={"p-0": 0.9, "p-1": 0.1, "p-2": 0.1},
        # ... but nothing converts: no observation-backed accusation, no
        # ejection, no contradiction flag.
        testimony_records=(),
        accusations=(),
        plurality_target=None,
        plurality_margin=0,
        ejected_rendered_suspicion_among_ejectors=None,
        contradictions_by_subject=contradictions or {},
    )


def test_exploit_trajectory_d2_scores_zero_under_hardened_referee() -> None:
    """REGRESSION PIN (the 15.14 kill-lever exploit, pause audit §4 EXPLOITED).

    A synthetic trajectory reproducing the forced-kill shape — high D2
    separation, conversion pinned at 0.00, zero contradiction flags (the fake
    provider's suspicion tracks kill count; report-goodhart-probe.md: separation
    0.20 → 0.84 lifted ``mean_score`` 6.51 → 16.62) — scores 0 on the D2 term
    under the hardened referee: separation without an ejection or a
    contradiction flag is suspicion theater, not deduction. The FROZEN
    ``historical_15_2`` spec still rewards it (that IS the exploit), pinning the
    delta the hardening closes.
    """

    game = _clean_game(
        reason="IMPOSTOR_PARITY",
        meetings=(_suspicion_theater_meeting(),),
        kill_victim_roles=("CREWMATE", "CREWMATE"),
    )

    hardened = compute_game_score(game)
    assert hardened.d2_separation_norm == 0.0  # gated: no conversion, no flag
    assert hardened.d2_conversion == 0.0
    assert hardened.d2_deduction == 0.0  # the D2 term scores ~0 (exactly 0)

    exploited = compute_game_score(game, historical_15_2=True)
    assert exploited.d2_separation_norm == 1.0  # the raw suspicion-theater lift
    assert exploited.d2_deduction == 0.5
    assert hardened.score < exploited.score


def test_contradiction_flag_keeps_separation_live_without_conversion() -> None:
    """The OR-leg of the D2 gate: a contradiction flag is deduction evidence.

    Separation with a flag but no converted ejection still counts (the gate is
    "an ejection or a contradiction flag", pause audit §4) — the coupling kills
    suspicion theater, not honest tables whose evidence did not convert yet.
    """

    game = _clean_game(
        reason="IMPOSTOR_PARITY",
        meetings=(_suspicion_theater_meeting(contradictions={"p-0": (True,)}),),
        kill_victim_roles=("CREWMATE",),
    )
    score = compute_game_score(game)
    assert score.d2_separation_norm == 1.0
    assert score.d2_conversion == 0.0
    assert score.d2_deduction == 0.5


def test_persisted_vent_flag_keeps_separation_live_without_conversion() -> None:
    """The D2 gate's flag leg is VENT-AWARE (Codex review on PR #247).

    The re-derived ``contradictions_by_subject`` census can never contain the
    grounded role-proving ``vent_sighting`` flag (its grounding channel is not
    in the transcript, Task 15.4), so a game whose ONLY deduction evidence is a
    persisted vent flag must open the gate through ``persisted_vent_flags`` —
    mirroring the ``flags_per_meeting`` merge. A witnessed impostor vent is the
    game's hardest evidence, not suspicion theater.
    """

    import dataclasses

    vent_meeting = dataclasses.replace(
        _suspicion_theater_meeting(), persisted_vent_flags=1
    )
    game = _clean_game(
        reason="IMPOSTOR_PARITY",
        meetings=(vent_meeting,),
        kill_victim_roles=("CREWMATE",),
    )
    score = compute_game_score(game)
    assert score.d2_separation_norm == 1.0  # the vent flag opens the gate
    assert score.d2_conversion == 0.0
    assert score.d2_deduction == 0.5


def test_meeting_facts_carry_the_persisted_vent_flag_census() -> None:
    """``_meeting_facts`` surfaces the persisted vent flags off the recorded bytes.

    The committed baseline-5 4p1i set carries 11 persisted ``vent_sighting``
    flags (the same census ``test_flags_per_meeting_is_vent_aware`` pins for the
    supply gauge); the per-meeting facts must total the same so the D2 gate
    actually sees them on real bytes.
    """

    from eval.validity import assemble_tournament_report
    from eval.watchability import _meeting_facts

    report = assemble_tournament_report(_FOUR)
    total = sum(
        _meeting_facts(meeting, index, {}).persisted_vent_flags
        for game in report.games
        for index, meeting in enumerate(game.meetings)
    )
    assert total == 20  # was 11


def test_backed_conversion_keeps_separation_live() -> None:
    """The conversion leg of the D2 gate: a converted backed accusation counts."""

    score = compute_game_score(_clean_game())
    # _clean_meeting ejects the observation-backed-accused impostor.
    assert score.d2_conversion == 1.0
    assert score.d2_separation_norm > 0.0
    assert score.d2_deduction > 0.5


# --------------------------------------------------------------------------- #
# Task 15.19 patch 2 — subject-aware observation backing                      #
# --------------------------------------------------------------------------- #


def test_vent_sighting_of_x_does_not_back_accusation_of_y() -> None:
    """SUBJECT-AWARE BACKING (owner-ratified Q2, review-phase-15-midwave.md).

    A speaker grounds a genuine vent sighting of X in the SAME turn that accuses
    innocent Y: the Y-accusation is UNBACKED under the hardened referee (the
    grounded observation's subject must be the accused), while the X-mention
    stays a backed sighting. The frozen subject-agnostic bit still counts the
    Y-accusation backed — the exploit the re-anchoring closes.
    """

    from eval.watchability import _testimony_vehicle
    from meetings.schemas import AccusationClaim, MeetingTurn, SawVentObservation

    turn = MeetingTurn(
        turn_id="m:turn-1",
        turn_index=1,
        speaker="p-1",
        turn_kind="reply",
        reply_to=None,
        observations=(
            SawVentObservation(
                type="saw_vent", tick=100, subject="p-0", room="Cafeteria"
            ),
        ),
        claims=(
            AccusationClaim(
                type="accusation", against="p-2", confidence=0.9, reason="vibes"
            ),
        ),
        free_text="I saw p-0 vent, but honestly I think p-2 is the other one.",
    )

    vehicle_y, backed_y, backed_any_y = _testimony_vehicle(turn, "p-2")
    assert vehicle_y == "accusation"
    assert backed_y is False  # the vent names p-0, not the accused p-2
    # The frozen pre-15.19 bit mirrors the 15.2-era extractor byte-for-byte
    # (SawPlayer/FoundBody only — Task 16.14 re-narrowed it), so a vent-only
    # turn does not count as backed under the HISTORICAL spec either.
    assert backed_any_y is False

    vehicle_x, backed_x, backed_any_x = _testimony_vehicle(turn, "p-0")
    assert vehicle_x == "sighting"
    assert backed_x is True  # the sighting DOES name p-0


def test_subject_aware_backing_gates_conversion_and_railroad() -> None:
    """The ONE backing predicate flows into D2 conversion AND the railroad floor.

    A record whose only "backing" is a grounded observation about someone else
    (``observation_backed=False`` / ``observation_backed_any=True``) neither
    counts as a backed conversion attempt nor saves a crew ejection from the
    evidence-free-conviction railroad — while the frozen ``historical_15_2``
    mode preserves the old subject-agnostic behavior for the parity pin.
    """

    from eval.watchability import (
        _observation_backed_conversion,
        _subject_has_observation_backed_accusation,
    )

    record = _TestimonyRecord(
        subject="p-0",
        subject_role="IMPOSTOR",
        testimony_turns=(
            _TestimonyTurn(
                vehicle="accusation",
                observation_backed=False,  # the grounded sighting named X, not p-0
                observation_backed_any=True,
            ),
        ),
    )
    assert _subject_has_observation_backed_accusation(record) is False
    assert (
        _subject_has_observation_backed_accusation(record, historical_15_2=True) is True
    )

    # Conversion: the impostor ejection does NOT count as a backed conversion.
    meeting = _MeetingFacts(
        meeting_index=0,
        ejected_player_id="p-0",
        ejected_role="IMPOSTOR",
        suspicion_graph_by_voter={},
        rendered_suspicion_by_target={},
        testimony_records=(record,),
        accusations=(_Accusation(speaker="p-1", accused="p-0"),),
        plurality_target="p-0",
        plurality_margin=1,
        ejected_rendered_suspicion_among_ejectors=0.9,
        contradictions_by_subject={},
    )
    game = _clean_game(meetings=(meeting,))
    rate, attempted, converted = _observation_backed_conversion([game])
    assert (rate, attempted, converted) == (None, 0, 0)

    # Railroad: a CREW ejection with the same someone-else "backing" and no flag
    # is an evidence-free conviction under the hardened referee (floor 0)...
    crew_record = _TestimonyRecord(
        subject="p-3",
        subject_role="CREWMATE",
        testimony_turns=(
            _TestimonyTurn(
                vehicle="accusation",
                observation_backed=False,
                observation_backed_any=True,
            ),
        ),
    )
    railroad_meeting = _MeetingFacts(
        meeting_index=0,
        ejected_player_id="p-3",
        ejected_role="CREWMATE",
        suspicion_graph_by_voter={"p-1": {"p-3": 0.8}},
        rendered_suspicion_by_target={"p-3": 0.8},
        testimony_records=(crew_record,),
        accusations=(_Accusation(speaker="p-1", accused="p-3"),),
        plurality_target="p-3",
        plurality_margin=1,
        ejected_rendered_suspicion_among_ejectors=0.8,
        contradictions_by_subject={},
    )
    railroaded = _clean_game(reason="CREWMATE_TASKS", meetings=(railroad_meeting,))
    assert compute_game_score(railroaded).floor_multiplier == 0.0
    # ... while the frozen historical spec (subject-agnostic) does not floor it.
    assert compute_game_score(railroaded, historical_15_2=True).floor_multiplier == 1.0


# --------------------------------------------------------------------------- #
# Task 15.19 — advisory rare-event floors (baseline numerator <= 1)           #
# --------------------------------------------------------------------------- #


def test_rare_event_floor_with_numerator_at_most_one_is_advisory() -> None:
    """A floor pinned on a baseline numerator <= 1 is reported, never failing.

    The pause audit §1/§5.1 one-event floor degeneracy: the 4p1i
    ``witnessed_event_rate`` floor is pinned to 1/61 (baseline-5; was 1/58), so a
    same-substrate set can miss it by pure variance. The gauge row keeps the honest
    measured-vs-floor verdict (``passed=False``) and is marked ``advisory``,
    but ``supply_floors_passed`` excludes it.
    """

    floors = SupplyFloors(
        witnessed_event_rate=FloorPin(value=0.018, numerator=1),  # 1 event -> advisory
        flags_per_meeting=FloorPin(value=1.0, numerator=42),
        testimony_backed_conversion=FloorPin(value=0.5, numerator=20),
    )
    gauges = SupplyGaugeValues(
        witnessed_event_rate=0.0,  # below the advisory floor
        total_kills=46,
        crew_witnessed_kills=0,
        flags_per_meeting=1.5,
        total_flags=60,
        persisted_vent_flags=11,
        meetings_total=40,
        testimony_backed_conversion=0.72,
        backed_conversion_attempted=36,
        backed_conversion_converted=26,
    )
    passed, rows = evaluate_supply_floors(gauges, floors)
    assert passed is True  # the advisory miss cannot fail the referee
    witnessed = next(r for r in rows if r.name == "witnessed_event_rate")
    assert witnessed.advisory is True
    assert witnessed.passed is False  # the row still reports the honest verdict
    assert all(r.advisory is False for r in rows if r.name != "witnessed_event_rate")


def test_non_advisory_floor_still_fails_the_set() -> None:
    """A numerator >= 2 floor keeps its teeth: missing it fails the referee."""

    floors = SupplyFloors(
        witnessed_event_rate=FloorPin(value=0.018, numerator=2),
        flags_per_meeting=FloorPin(value=1.0, numerator=42),
        testimony_backed_conversion=FloorPin(value=0.5, numerator=20),
    )
    gauges = SupplyGaugeValues(
        witnessed_event_rate=0.0,
        total_kills=46,
        crew_witnessed_kills=0,
        flags_per_meeting=1.5,
        total_flags=60,
        persisted_vent_flags=11,
        meetings_total=40,
        testimony_backed_conversion=0.72,
        backed_conversion_attempted=36,
        backed_conversion_converted=26,
    )
    passed, rows = evaluate_supply_floors(gauges, floors)
    assert passed is False
    witnessed = next(r for r in rows if r.name == "witnessed_event_rate")
    assert witnessed.advisory is False
    assert witnessed.passed is False


def test_corpus_4p1i_passes_the_referee_via_the_advisory_rule() -> None:
    """``replays/ml_corpus/4p1i`` PASSES: the one-event floor is advisory.

    The pause audit §1 finding: corpus-4p1i measures 0.0 on
    ``witnessed_event_rate`` (baseline-6 floor 1/61 ≈ 0.0164, a one-event
    numerator) while passing the hard validity gate and both other supply floors.
    Under the advisory rule the set passes the referee; the miss is still reported.

    Task 18.13 note: the corpus is now re-recorded at BASELINE 6 (the meeting-layer
    re-ground), so it is measured against its OWN baseline-6 block — the Q3
    restoration held forward: same-substrate evidence again, never the stale-context
    read that would score baseline-6 bytes against the prior block's floors. (The
    4p1i ``witnessed_event_rate`` and ``flags_per_meeting`` pins are numerically
    identical across the two blocks — the small 4p1i games elicit no new roll-call
    or vent flags — so this flip moves only the population-relative conversion
    floor, and the verdicts below are unchanged.)
    """

    report = compute_watchability(_CORPUS_FOUR, baseline_id="baseline-6")
    assert report.integrity_ok is True
    assert report.referee_passed is True
    assert report.supply_floors_passed is True
    witnessed = next(
        g for g in report.supply_gauges if g.name == "witnessed_event_rate"
    )
    assert witnessed.advisory is True
    assert witnessed.measured == 0.0
    assert witnessed.passed is False  # reported honestly, excluded from the AND
    others = [g for g in report.supply_gauges if g.name != "witnessed_event_rate"]
    assert all(g.passed and not g.advisory for g in others)


# --------------------------------------------------------------------------- #
# Evidence-supply floors                                                     #
# --------------------------------------------------------------------------- #

_BASELINE_2_9P2I_FLOORS = SupplyFloors(
    witnessed_event_rate=FloorPin(value=0.0375, numerator=6),
    flags_per_meeting=FloorPin(value=2.007042253521127, numerator=285),
    testimony_backed_conversion=FloorPin(value=0.4375, numerator=56),
)


def test_baseline_6_sets_pass_the_hardened_referee_end_to_end() -> None:
    """The committed scripted-FSM sets clear the baseline-6 floors too.

    The DoD anchor (15.19): every gauge row passes, not just the composed
    verdict. The baseline-6 EXACT anchor (measured == floor on the bytes those
    floors were pinned from) retired with the baseline-7 record, which replaced
    those bytes; what it proved is now proved by
    ``test_baseline_7_floor_pins_equal_the_measured_bytes``. Clearing the older,
    lower floors stays a real check: a record that fell below them would fail
    here.
    """

    for sample_dir in (_NINE, _FOUR):
        report = compute_watchability(sample_dir)
        assert report.referee_passed is True
        assert report.supply_floors_passed is True
        assert all(gauge.passed for gauge in report.supply_gauges)


def test_baseline_9_floor_pins_equal_the_measured_bytes() -> None:
    """EXACT ANCHOR: each baseline-9 floor equals the bytes it was pinned from.

    Same both-sides discipline as the retired baseline-6 to baseline-8 anchors —
    the measured gauge IS the recorded fraction and the pinned floor IS the
    measured gauge — so an under-pinned floor cannot silently weaken the block
    while the comments still claim self-consistency.

    The 4p1i entry is still measured: ``replays/samples/4p1i`` holds the bytes it
    was pinned from. The 9p2i entry's bytes left ``replays/samples/9p2i`` at the
    promotion of candidate round 2 (2026-10-02), so it is HISTORY, and the ML
    selection floor (``BAKEOFF_BASELINE_ID``): it is held to its literal pins and
    never re-derived, as the baseline-2 block was. The shown set's own floors
    are the ``stage-b-r3`` block, anchored below.
    """

    historical = _BASELINE_SUPPLY_FLOORS["baseline-9"]["9p2i"]
    assert historical.witnessed_event_rate == FloorPin(
        value=0.017142857142857144, numerator=3
    )  # 3/175
    assert historical.flags_per_meeting == FloorPin(
        value=0.7379310344827587, numerator=107
    )  # 107/145
    assert historical.testimony_backed_conversion == FloorPin(
        value=0.7053571428571429, numerator=79
    )  # 79/112
    assert historical.transcript_flags_per_meeting == FloorPin(
        value=0.11724137931034483, numerator=17
    )  # 17/145
    assert historical.persisted_vent_flags_per_meeting == FloorPin(
        value=0.6206896551724138, numerator=90
    )  # 90/145

    fractions = {
        "witnessed_event_rate": 1 / 66,  # numerator 1 -> ADVISORY (was 1/62)
        "flags_per_meeting": 20 / 39,  # 20 vent + 0 transcript (unchanged)
        "testimony_backed_conversion": 20 / 37,  # SUBJECT-AWARE (was 20/33)
        "transcript_flags_per_meeting": 0 / 39,  # numerator 0 -> ADVISORY
        "persisted_vent_flags_per_meeting": 20 / 39,  # unchanged
    }
    report = compute_watchability(_FOUR, baseline_id="baseline-9")
    assert report.referee_passed is True
    assert all(gauge.passed for gauge in report.supply_gauges)
    by_name = {gauge.name: gauge for gauge in report.supply_gauges}
    assert set(by_name) == set(fractions)
    for name, fraction in fractions.items():
        gauge = by_name[name]
        assert gauge.measured == fraction, f"4p1i {name} measured"
        assert gauge.floor == fraction, f"4p1i {name} floor pin"


#: The shown set's measured supply: the stage-b-r3 block is pinned from it. The
#: stage-b-r2 block (14/195, 53/117 with 38 vent and 15 transcript, 44/94) left
#: with round 2's bytes at round 3's promotion, with its equality tests.
_STAGE_B_R3_FRACTIONS: dict[str, float] = {
    "witnessed_event_rate": 14 / 192,
    "flags_per_meeting": 54 / 119,  # 39 vent + 15 transcript
    "testimony_backed_conversion": 46 / 94,  # SUBJECT-AWARE
    "transcript_flags_per_meeting": 15 / 119,
    "persisted_vent_flags_per_meeting": 39 / 119,
}


def test_stage_b_r3_floor_pins_equal_the_measured_bytes() -> None:
    """EXACT ANCHOR: the stage block's 9p2i floors equal the promoted bytes.

    The same both-sides discipline: on ``replays/samples/9p2i`` every gauge
    measures exactly its pinned floor, and the set's default block is its own
    era's (``eval/eras.py``), so a bare call scores it against these floors.
    The block of the era its bytes replaced is gone.
    """

    report = compute_watchability(_NINE)
    assert report.baseline_id == "stage-b-r3"
    assert report.referee_passed is True
    assert "stage-b-r2" not in _BASELINE_SUPPLY_FLOORS
    by_name = {gauge.name: gauge for gauge in report.supply_gauges}
    assert set(by_name) == set(_STAGE_B_R3_FRACTIONS)
    for name, fraction in _STAGE_B_R3_FRACTIONS.items():
        assert by_name[name].measured == fraction, f"{name} measured"
        assert by_name[name].floor == fraction, f"{name} floor pin"
    # The other committed sample set reads its own era's block by default.
    assert compute_watchability(_FOUR).baseline_id == "baseline-9"


def _stage_pin_numerator_problems(
    floors: SupplyFloors, measured: SupplyGaugeValues
) -> list[str]:
    """Each stage pin whose numerator is not the event count it was measured from.

    The numerator is what the advisory rare-event rule reads, so it is held to
    the raw count behind the pinned value, not to the value alone.
    """

    counts = {
        "witnessed_event_rate": measured.crew_witnessed_kills,
        "flags_per_meeting": measured.total_flags,
        "testimony_backed_conversion": measured.backed_conversion_converted,
        "transcript_flags_per_meeting": (
            measured.total_flags - measured.persisted_vent_flags
        ),
        "persisted_vent_flags_per_meeting": measured.persisted_vent_flags,
    }
    problems = []
    for name, count in counts.items():
        pin = getattr(floors, name)
        if pin is None or pin.numerator != count:
            problems.append(f"{name}: pinned numerator {pin}, measured count {count}")
    return problems


def test_stage_b_r3_floor_numerators_equal_the_measured_counts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """EXACT ANCHOR: each stage-b-r3 pin's numerator is its measured event count.

    The counts are the ones the referee's own walk measures on the promoted
    bytes, read off the call that gates them. Planted: one pin's numerator moved
    by one, the value unchanged, fails by name.
    """

    measured: list[SupplyGaugeValues] = []
    gate = watchability_module.evaluate_supply_floors

    def spy(
        gauges: SupplyGaugeValues, floors: SupplyFloors
    ) -> tuple[bool, tuple[SupplyFloorGauge, ...]]:
        measured.append(gauges)
        return gate(gauges, floors)

    monkeypatch.setattr(watchability_module, "evaluate_supply_floors", spy)
    assert compute_watchability(_NINE).baseline_id == "stage-b-r3"
    assert len(measured) == 1
    floors = _BASELINE_SUPPLY_FLOORS["stage-b-r3"]["9p2i"]
    assert _stage_pin_numerator_problems(floors, measured[0]) == []
    for name in sorted(_STAGE_B_R3_FRACTIONS):
        pin = getattr(floors, name)
        moved = replace(floors, **{name: replace(pin, numerator=pin.numerator + 1)})
        assert _stage_pin_numerator_problems(moved, measured[0]) == [
            f"{name}: pinned numerator {replace(pin, numerator=pin.numerator + 1)}, "
            f"measured count {pin.numerator}"
        ]


@pytest.mark.parametrize("gauge", sorted(_STAGE_B_R3_FRACTIONS))
def test_a_stage_pin_raised_by_one_numerator_fails_its_set(gauge: str) -> None:
    """PLANTED: each stage-b-r3 pin, raised by one numerator, rejects the bytes.

    The measured supply is the promoted set's; only the one pin moves. The
    conversion pin is a population-relative anchor, so raising it raises the
    derived floor in proportion and still fails the set.
    """

    floors = _BASELINE_SUPPLY_FLOORS["stage-b-r3"]["9p2i"]
    denominators = {
        "witnessed_event_rate": 192,  # was 195
        "flags_per_meeting": 119,  # was 117
        "testimony_backed_conversion": 94,
        "transcript_flags_per_meeting": 119,  # was 117
        "persisted_vent_flags_per_meeting": 119,  # was 117
    }
    pin = getattr(floors, gauge)
    raised = FloorPin(
        value=(pin.numerator + 1) / denominators[gauge], numerator=pin.numerator + 1
    )
    measured = SupplyGaugeValues(
        witnessed_event_rate=14 / 192,  # was 14 / 195
        total_kills=192,  # was 195
        crew_witnessed_kills=14,
        flags_per_meeting=54 / 119,  # was 53 / 117
        total_flags=54,  # was 53
        persisted_vent_flags=39,  # was 38
        meetings_total=119,  # was 117
        testimony_backed_conversion=46 / 94,  # was 44 / 94
        backed_conversion_attempted=94,
        backed_conversion_converted=46,  # was 44
    )
    assert evaluate_supply_floors(measured, floors)[0] is True
    changes: dict[str, Any] = {gauge: raised}
    passed, rows = evaluate_supply_floors(measured, replace(floors, **changes))
    assert passed is False
    assert next(row for row in rows if row.name == gauge).passed is False


def test_a_recording_with_one_layer_undeclared_is_refused_naming_the_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PLANTED: the referee refuses a recorded setting it was not reviewed for.

    The walk's declared layers come from :data:`REFEREE_READS`; dropping the
    meeting layer's fields from it makes the promoted set's ballot arms unread,
    and the referee refuses before any reconstruction, naming the field, rather
    than flooring the set as an integrity breach.
    """

    meeting_fields = {
        "bounded_rebuttal_version",
        "ballot_kill_row_version",
        "impostor_ballot_version",
    }
    monkeypatch.setattr(
        watchability_module, "REFEREE_READS", REFEREE_READS - meeting_fields
    )
    with pytest.raises(ValueError, match="does not read the recorded bounded_rebuttal"):
        compute_watchability(_NINE)
    # The baseline-9 sets record no setting, so they stay readable.
    assert compute_watchability(_FOUR).integrity_ok is True


def test_a_gauge_below_a_baseline_7_floor_is_rejected() -> None:
    """PLANTED: the baseline-7 block bites — a starved supply fails its referee.

    Drives the committed block's own floors, so a mistyped pin or a broken
    population-relative derivation shows up here rather than passing quietly. The
    flag census is held at the pin so the conversion floor derives to the pin
    itself, and only the conversion is dropped below it.
    """

    floors = _BASELINE_SUPPLY_FLOORS["baseline-7"]["9p2i"]
    starved = SupplyGaugeValues(
        witnessed_event_rate=3 / 177,  # at the pin
        total_kills=177,
        crew_witnessed_kills=3,
        flags_per_meeting=144 / 152,  # at the pin -> ratio 1.0 -> floor == pin
        total_flags=144,
        persisted_vent_flags=92,
        meetings_total=152,
        testimony_backed_conversion=83 / 132,  # ONE conversion short of the pin
        backed_conversion_attempted=132,
        backed_conversion_converted=83,
    )
    passed, rows = evaluate_supply_floors(starved, floors)
    assert passed is False, "a below-floor conversion must fail the referee"
    conversion = next(r for r in rows if r.name == "testimony_backed_conversion")
    assert conversion.passed is False
    assert conversion.floor == 84 / 132
    assert conversion.advisory is False


def _vent_fed_candidate(
    *, total_flags: int, persisted_vent_flags: int
) -> SupplyGaugeValues:
    """A candidate clearing every non-flag baseline-7 gauge, flags parameterized.

    Kills, conversion and meeting count are held at the baseline-7 9p2i pins so
    the only thing under test is where the flag supply comes from.
    """

    return SupplyGaugeValues(
        witnessed_event_rate=3 / 177,
        total_kills=177,
        crew_witnessed_kills=3,
        flags_per_meeting=total_flags / 152,
        total_flags=total_flags,
        persisted_vent_flags=persisted_vent_flags,
        meetings_total=152,
        testimony_backed_conversion=1.0,
        backed_conversion_attempted=115,
        backed_conversion_converted=115,
    )


def test_a_vent_fed_candidate_fails_the_transcript_component_floor() -> None:
    """PLANTED: the merged flag floor cannot be cleared on vent sightings alone.

    ``flags_per_meeting`` is one number over two sources, so a candidate whose
    deduction-flag supply has collapsed can still clear it by minting vent
    sightings — a selection floor that stops selecting for the evidence it
    names. This candidate carries MORE merged supply than the baseline (200/152
    against 144/152) with 190 of it vents, so the merged row passes and only the
    transcript component (10/152, under the pinned 52/152) bites.
    """

    floors = _BASELINE_SUPPLY_FLOORS["baseline-7"]["9p2i"]
    passed, rows = evaluate_supply_floors(
        _vent_fed_candidate(total_flags=200, persisted_vent_flags=190), floors
    )

    assert passed is False, "a starved transcript component must fail the referee"
    by_name = {row.name: row for row in rows}
    assert by_name["flags_per_meeting"].passed is True, "the merged row must pass"
    component = by_name["transcript_flags_per_meeting"]
    assert component.passed is False
    assert component.measured == 10 / 152
    assert component.floor == 52 / 152
    assert component.advisory is False
    assert by_name["persisted_vent_flags_per_meeting"].passed is True
    # The component row is what fails: every other row cleared.
    assert {row.name for row in rows if not row.passed} == {
        "transcript_flags_per_meeting"
    }


def test_the_same_merged_supply_with_a_healthy_component_passes() -> None:
    """PERTURBED: the component gauge, not the merged floor, did the work above.

    Same merged census (200/152), the split moved back inside the pins — so the
    referee passes. Without this the failure above could be an artifact of any
    row, not the component the test names.
    """

    floors = _BASELINE_SUPPLY_FLOORS["baseline-7"]["9p2i"]
    passed, rows = evaluate_supply_floors(
        _vent_fed_candidate(total_flags=200, persisted_vent_flags=100), floors
    )

    assert passed is True
    assert all(row.passed for row in rows)
    by_name = {row.name: row for row in rows}
    assert by_name["transcript_flags_per_meeting"].measured == 100 / 152


def test_a_vent_count_above_the_merged_census_fails_loud() -> None:
    """PLANTED: the split's own arithmetic cannot go negative in silence.

    The vent census is a subset of the merged one by construction, so a larger
    vent count means the two terms came from different walks. Reporting the
    resulting negative component rate would look like a starved candidate
    rather than a broken instrument.
    """

    floors = _BASELINE_SUPPLY_FLOORS["baseline-7"]["9p2i"]
    impossible = _vent_fed_candidate(total_flags=50, persisted_vent_flags=90)

    with pytest.raises(ValueError, match="subset of the merged"):
        evaluate_supply_floors(impossible, floors)


def test_a_block_without_component_pins_emits_no_component_rows() -> None:
    """The earlier blocks stay evaluable: an unpinned component emits no row.

    Their sample sets left the tree, so no component can be measured for them;
    ``evaluate_supply_floors`` must skip rather than invent a floor.
    """

    floors = _BASELINE_SUPPLY_FLOORS["baseline-6"]["9p2i"]
    assert floors.transcript_flags_per_meeting is None
    assert floors.persisted_vent_flags_per_meeting is None

    _, rows = evaluate_supply_floors(
        _vent_fed_candidate(total_flags=200, persisted_vent_flags=190), floors
    )
    assert {row.name for row in rows} == {
        "witnessed_event_rate",
        "flags_per_meeting",
        "testimony_backed_conversion",
    }


def test_hardened_patches_fire_on_the_committed_9p2i_bytes() -> None:
    """LIVE-PATH SNAPSHOT: the 15.19 D2 patches measured on the committed bytes.

    The historical parity pin guards only the FROZEN path, and the CLI aggregate
    is a single scalar — neither shows the patches acting on any real committed
    game. This pins the live-vs-historical per-game delta on the promoted
    stage-b-r3 9p2i bytes: the subject-aware railroad floor (patch 2) adds no
    floored game (the stage-b-r2 bytes added none either; the baseline-9 bytes
    added two, 5 and 19; baseline 8 added 19 alone; baseline 4 floored one, 29;
    baseline 3 four, 19/27/29/31 — the mechanism stays covered by the synthetic
    ``test_subject_aware_backing_gates_conversion_and_railroad``), and the
    conversion-coupled D2 gate (patch 1) zeroes the separation term on twelve
    games, where the stage-b-r2 bytes read thirteen, the baseline-9 bytes four,
    4/10/39/46, and baselines 6 to 8 none (baseline 5 zeroed 2/4/10/12/37/47;
    the mechanism itself is pinned on synthetic bytes elsewhere in this file).
    """

    live = {s.seed: s for s in _score_committed_set(_NINE)}
    hist = {s.seed: s for s in _score_committed_set(_NINE, historical_15_2=True)}

    live_floored = {seed for seed, s in live.items() if s.floor_multiplier == 0.0}
    hist_floored = {seed for seed, s in hist.items() if s.floor_multiplier == 0.0}
    # Patch 2 (subject-aware backing -> the railroad floor's backed leg): the
    # hardened floor only ever ADDS railroads on the same bytes...
    assert hist_floored <= live_floored
    # ...and on the promoted 9p2i bytes it adds none (the baseline-9 bytes added
    # seeds 5 and 19, a crew railroad the subject-aware backing refused to count
    # as backed; the mechanism itself is pinned on synthetic bytes elsewhere in
    # this file).
    assert live_floored - hist_floored == set()  # was {5, 19}

    # Patch 1 (conversion-coupled D2): on the promoted bytes twelve committed
    # games are suspicion theater — rendered-suspicion separation with no
    # converted backed accusation and no contradiction flag — so the gate zeroes
    # their live separation while the frozen spec keeps it positive (the
    # baseline-9 bytes gated 4/10/39/46; baselines 6 to 8 read the empty set;
    # baseline 5 gated 2/4/10/12/37/47).
    patch1_zeroed = {
        seed
        for seed in live
        if live[seed].d2_separation_norm == 0.0 and hist[seed].d2_separation_norm > 0.0
    }
    # was {4, 12, 15, 21, 23, 25, 28, 29, 31, 33, 43, 45, 48} on round 2's bytes
    assert patch1_zeroed == {2, 4, 23, 24, 29, 30, 34, 35, 36, 38, 43, 48}


def test_testimony_backed_conversion_requires_observation_backing() -> None:
    """The conversion floor counts only OBSERVATION-BACKED accusations, not vibes.

    An unbacked accusation that happens to eject an impostor must NOT count toward
    ``testimony_backed_conversion`` (else the "backed" floor could be cleared by
    ungrounded vibe-convictions), matching the geomean's D2 conversion predicate.
    """

    from eval.watchability import _observation_backed_conversion

    def _game(*, backed: bool) -> _GameFacts:
        return _GameFacts(
            seed=0,
            reason="CREWMATE_EJECT",
            roles={"p-0": "IMPOSTOR", "p-1": "CREWMATE"},
            meetings=(
                _MeetingFacts(
                    meeting_index=0,
                    ejected_player_id="p-0",  # the impostor was ejected
                    ejected_role="IMPOSTOR",
                    suspicion_graph_by_voter={},
                    rendered_suspicion_by_target={},
                    testimony_records=(
                        _TestimonyRecord(
                            subject="p-0",
                            subject_role="IMPOSTOR",
                            testimony_turns=(
                                _TestimonyTurn(
                                    vehicle="accusation",
                                    observation_backed=backed,
                                    observation_backed_any=backed,
                                ),
                            ),
                        ),
                    ),
                    accusations=(_Accusation(speaker="p-1", accused="p-0"),),
                    plurality_target="p-0",
                    plurality_margin=1,
                    ejected_rendered_suspicion_among_ejectors=0.9,
                    contradictions_by_subject={},
                ),
            ),
            kill_victim_roles=(),
            trajectories={},
        )

    # UNBACKED accusation → not a backed conversion attempt at all.
    rate, attempted, converted = _observation_backed_conversion([_game(backed=False)])
    assert (attempted, converted) == (0, 0)
    assert rate is None

    # BACKED accusation that ejected the impostor → a converted attempt.
    rate2, attempted2, converted2 = _observation_backed_conversion([_game(backed=True)])
    assert (attempted2, converted2) == (1, 1)
    assert rate2 == 1.0


def test_missing_meeting_row_is_an_integrity_breach(tmp_path: Path) -> None:
    """A truncated replay (a MEETING reached but no recorded meeting row) is floored.

    Codex repro: deleting one meeting row left ``integrity_ok=True`` /
    ``referee_passed=True`` — the walk silently stopped without checking the rest.
    Reconstruction now flags the missing row as an integrity breach so the set is
    REJECTED, never silently certified.
    """

    import json
    import shutil

    source = _FOUR / "replay-seed-1.jsonl"
    lines = source.read_text().splitlines()
    kept = [line for line in lines if "meeting_id" not in json.loads(line)]
    assert len(kept) < len(lines)  # a meeting row was dropped (this game has one)

    (tmp_path / "replay-seed-1.jsonl").write_text("\n".join(kept) + "\n")
    shutil.copy(_FOUR / "roster.json", tmp_path / "roster.json")

    from eval.watchability import _reconstruct_kills

    assert _reconstruct_kills(tmp_path).integrity_ok is False

    report = compute_watchability(tmp_path)
    assert report.integrity_ok is False
    assert report.referee_passed is False
    assert all(game.score == 0.0 for game in report.per_game)


def _write_one_game_set(tmp_path: Path, lines: list[str]) -> None:
    """Write a single-game 4p1i-rostered replay set (the given lines) into tmp."""

    import shutil

    (tmp_path / "replay-seed-0.jsonl").write_text("\n".join(lines) + "\n")
    shutil.copy(_FOUR / "roster.json", tmp_path / "roster.json")


def test_corrupted_meeting_pre_hash_is_an_integrity_breach(tmp_path: Path) -> None:
    """A tampered ``state_hash_before`` (that verify-samples rejects) floors the set.

    The trigger-tick hash and ``state_hash_after`` still reconstruct, so only the
    pre-hash cross-check catches the corrupted meeting metadata.
    """

    import json

    from eval.watchability import _reconstruct_kills

    lines = (_FOUR / "replay-seed-1.jsonl").read_text().splitlines()
    corrupted: list[str] = []
    changed = False
    for line in lines:
        row = json.loads(line)
        if "state_hash_before" in row:
            row["state_hash_before"] = "0" * 64  # a valid-shaped but wrong hash
            changed = True
            corrupted.append(json.dumps(row))
        else:
            corrupted.append(line)
    assert changed  # this game has a meeting row carrying a pre-hash
    _write_one_game_set(tmp_path, corrupted)

    assert _reconstruct_kills(tmp_path).integrity_ok is False
    report = compute_watchability(tmp_path)
    assert report.integrity_ok is False
    assert report.referee_passed is False


def test_forged_game_over_reason_is_an_integrity_breach(tmp_path: Path) -> None:
    """A forged ``game_over`` reason (not hash-covered) is caught before it inflates D1.

    Every tick + meeting hash still reconstructs, but the recorded reason no longer
    matches the reconstructed terminal GameOverEvent, so the set is floored rather
    than scored on the tampered (D1-inflating) label.
    """

    import json

    from eval.watchability import _reconstruct_kills

    lines = (_FOUR / "replay-seed-3.jsonl").read_text().splitlines()
    forged: list[str] = []
    changed = False
    for line in lines:
        row = json.loads(line)
        if row.get("kind") == "game_over":
            assert row["reason"] != "CREWMATE_EJECT"  # seed 3 is a task win
            row["reason"] = (
                "CREWMATE_EJECT"  # forge a play-decided label (D1 0.6 -> 1.0)
            )
            changed = True
            forged.append(json.dumps(row))
        else:
            forged.append(line)
    assert changed
    _write_one_game_set(tmp_path, forged)

    assert _reconstruct_kills(tmp_path).integrity_ok is False
    report = compute_watchability(tmp_path)
    assert report.integrity_ok is False
    assert report.referee_passed is False
    assert all(game.score == 0.0 for game in report.per_game)


def test_missing_game_over_row_is_an_integrity_breach(tmp_path: Path) -> None:
    """A set whose terminal ``game_over`` row is deleted is floored, not certified.

    Every tick + meeting hash still reconstructs and the supply floors still pass,
    but the recorded terminal outcome is gone — an incomplete recording.
    """

    import json

    from eval.watchability import _reconstruct_kills

    lines = (_FOUR / "replay-seed-1.jsonl").read_text().splitlines()
    kept = [line for line in lines if json.loads(line).get("kind") != "game_over"]
    assert len(kept) == len(lines) - 1  # exactly the game_over row was dropped
    _write_one_game_set(tmp_path, kept)

    assert _reconstruct_kills(tmp_path).integrity_ok is False
    report = compute_watchability(tmp_path)
    assert report.integrity_ok is False
    assert report.referee_passed is False


def test_duplicate_meeting_row_is_an_integrity_breach(tmp_path: Path) -> None:
    """A doubled meeting row (which the report loader double-counts) floors the set."""

    import json

    from eval.watchability import _reconstruct_kills

    lines = (_FOUR / "replay-seed-1.jsonl").read_text().splitlines()
    meeting_line = next(line for line in lines if "meeting_id" in json.loads(line))
    # Insert a second copy of the meeting row (same tick + meeting id).
    doubled = [*lines, meeting_line]
    _write_one_game_set(tmp_path, doubled)

    assert _reconstruct_kills(tmp_path).integrity_ok is False
    report = compute_watchability(tmp_path)
    assert report.integrity_ok is False
    assert report.referee_passed is False


def test_ballots_not_tallying_to_outcome_is_an_integrity_breach(
    tmp_path: Path,
) -> None:
    """Tampered ballots that don't tally to the recorded ejection floor the set.

    ``apply_meeting_result`` consumes only ``outcome`` / ``ejected_player_id``, so
    emptying a recorded EJECTED meeting's ballots leaves every hash valid — only the
    tally cross-check catches that the ballots no longer imply the ejection.
    """

    import json

    from eval.validity import assemble_tournament_report
    from eval.watchability import _reconstruct_kills

    # Find a 4p1i seed whose game has an EJECTED meeting (a recorded ejection).
    report = assemble_tournament_report(_FOUR)
    eject_seed = next(
        game.seed
        for game in report.games
        for meeting in game.meetings
        if meeting.outcome == "EJECTED" and meeting.ejected_player_id is not None
    )
    lines = (_FOUR / f"replay-seed-{eject_seed}.jsonl").read_text().splitlines()
    tampered: list[str] = []
    changed = False
    for line in lines:
        row = json.loads(line)
        if row.get("outcome") == "EJECTED" and "ballots" in row:
            row["ballots"] = []  # empty ballots tally to SKIPPED, not the ejection
            changed = True
            tampered.append(json.dumps(row))
        else:
            tampered.append(line)
    assert changed
    _write_one_game_set(tmp_path, tampered)

    assert _reconstruct_kills(tmp_path).integrity_ok is False


def test_trailing_row_after_game_over_is_an_integrity_breach(tmp_path: Path) -> None:
    """A fabricated replay row after the terminal event floors the set."""

    import json

    from eval.watchability import _reconstruct_kills

    lines = (_FOUR / "replay-seed-1.jsonl").read_text().splitlines()
    rows = [json.loads(line) for line in lines]
    terminal_tick = next(r["tick"] for r in rows if r.get("kind") == "game_over")
    tick_row = next(dict(r) for r in rows if "actions" in r)  # a per-tick ReplayEntry
    tick_row["tick"] = terminal_tick + 1  # a fabricated post-game tick
    _write_one_game_set(tmp_path, [*lines, json.dumps(tick_row)])

    assert _reconstruct_kills(tmp_path).integrity_ok is False


def test_malformed_bytes_fail_closed_not_crash(tmp_path: Path) -> None:
    """A corrupt candidate the loader rejects yields a FAILING report, not a crash."""

    import shutil

    (tmp_path / "replay-seed-0.jsonl").write_text("this is not valid replay json\n")
    shutil.copy(_FOUR / "roster.json", tmp_path / "roster.json")

    report = compute_watchability(tmp_path)  # must NOT raise
    assert report.integrity_ok is False
    assert report.referee_passed is False
    assert report.supply_floors_passed is False
    assert report.per_game == ()


def test_witnessed_event_rate_is_the_measured_anchor() -> None:
    """The 9p2i witnessed-event rate is the 14/192 = 7.29% crew-witnessed anchor.

    Computed from the committed bytes (not the pinned constant), so it tracks the
    set's own era: the promoted stage-b-r3 bytes record 14 crew-witnessed of 192
    kills in 9p2i (stage-b-r2 was 14/195 = 7.18%; baseline 9 was 3/175 = 1.71%;
    baseline 8 was 3/182 = 1.65%;
    baseline 7 was 3/177 = 1.69%; the vent-widening baseline 6 was 6/177 =
    3.39%; the pre-widening baseline 6 was 7/173 = 4.05%; baseline 5 was 7/203 =
    3.45%).
    """

    report = compute_watchability(_NINE)
    witnessed = next(
        g for g in report.supply_gauges if g.name == "witnessed_event_rate"
    )
    assert witnessed.measured == pytest.approx(14 / 192)  # was 14 / 195


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
        backed_conversion_attempted=50,
        backed_conversion_converted=0,
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
        backed_conversion_attempted=40,
        backed_conversion_converted=24,
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
    else a vent-rich baseline-5 candidate's strongest evidence reads as starved.
    The committed baseline-5 4p1i set carries 11 such vent flags (the retained
    Wave-0 vent substrate) — 11 of the 16 total behind the pinned flags/meeting
    floor (16/39 = 0.4103; the other 5 are re-derived transcript flags on the
    graduated substrate); injecting one more vent must add exactly 1.
    """

    from eval.validity import assemble_tournament_report
    from eval.watchability import _persisted_vent_flag_count, _supply_gauge_values
    from meetings.schemas import ContradictionRef

    report = assemble_tournament_report(_FOUR)
    # The committed baseline-5 4p1i set carries 11 grounded vent flags that the
    # transcript re-derivation cannot reproduce, so they are merged in (baseline 2's
    # v4 set carried none).
    assert _persisted_vent_flag_count(report) == 20  # was 11

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

    assert _persisted_vent_flag_count(report_with_vent) == 21  # was 12
    before = _supply_gauge_values(report, [], [])
    after = _supply_gauge_values(report_with_vent, [], [])
    assert after.persisted_vent_flags == 21  # was 12
    assert after.total_flags == before.total_flags + 1
    assert after.flags_per_meeting is not None and before.flags_per_meeting is not None
    assert after.flags_per_meeting > before.flags_per_meeting


def test_saw_vent_observation_counts_as_backed_evidence() -> None:
    """A witnessed impostor vent is first-hand role-proving evidence (Task 15.4).

    ``_testimony_vehicle`` must treat a :class:`SawVentObservation` like a
    :class:`SawPlayerObservation` on the LIVE subject-aware bit — observation-
    backing, and a sighting of its subject — so a vent-backed accusation
    converts in D2 without a redundant player-sighting. The FROZEN
    ``backed_any`` bit deliberately does NOT count it: it mirrors the 15.2-era
    extractor (SawPlayer/FoundBody only), whose vocabulary predates the type —
    Task 16.14 re-narrowed the drifted bit after the baseline-4 bytes exposed
    the divergence on vent-only-backed accusations (seeds 5/22).
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
    vehicle, backed, backed_any = _testimony_vehicle(accuse_turn, "p-0")
    assert vehicle == "accusation"
    assert backed is True  # subject-aware: the vent names the accused p-0
    assert backed_any is False  # the frozen extractor-mirror bit: no Saw/FoundBody

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
    vehicle2, backed2, backed_any2 = _testimony_vehicle(sight_turn, "p-0")
    assert vehicle2 == "sighting"
    assert backed2 is True
    assert backed_any2 is False  # frozen bit: vent-only turn, no Saw/FoundBody


def test_saw_move_backs_the_live_bit_and_leaves_the_frozen_bit_alone() -> None:
    """A spoken transition places its subject; the frozen parity bit ignores it.

    The LIVE subject-aware bit reads a :class:`SawMoveObservation` through
    :func:`meetings.transcript.sighting_placement` — the destination placement
    the detector itself mints flags from — so an accusation backed only by a
    spoken transition converts in D2. The FROZEN ``backed_any`` bit mirrors the
    15.2-era extractor's ``(SawPlayerObservation, FoundBodyObservation)`` tuple
    and must stay blind to the type, which is what
    ``test_historical_15_2_geomean_parity_frozen_pin_on_9p2i`` enforces on the
    committed bytes.
    """

    from eval.watchability import _testimony_vehicle
    from meetings.schemas import AccusationClaim, MeetingTurn, SawMoveObservation

    move = SawMoveObservation(
        type="saw_move",
        tick=100,
        subject="p-0",
        from_room="CAFETERIA",
        to_room="STORAGE",
    )
    accuse_turn = MeetingTurn(
        turn_id="m:turn-1",
        turn_index=1,
        speaker="p-1",
        turn_kind="reply",
        reply_to=None,
        observations=(move,),
        claims=(
            AccusationClaim(
                type="accusation", against="p-0", confidence=0.9, reason="transit"
            ),
        ),
        free_text="p-0 slipped from the Cafeteria into Storage.",
    )
    vehicle, backed, backed_any = _testimony_vehicle(accuse_turn, "p-0")
    assert vehicle == "accusation"
    assert backed is True  # LIVE: the transition places the accused p-0
    assert backed_any is False  # FROZEN: no SawPlayer/FoundBody in the turn

    # A transition about someone ELSE still cannot back an accusation of p-0 —
    # the 15.19 subject-awareness the widening must not undo.
    other_move = SawMoveObservation(
        type="saw_move",
        tick=100,
        subject="p-3",
        from_room="CAFETERIA",
        to_room="STORAGE",
    )
    misaimed = accuse_turn.model_copy(update={"observations": (other_move,)})
    _, backed_other, backed_any_other = _testimony_vehicle(misaimed, "p-0")
    assert backed_other is False
    assert backed_any_other is False


def test_none_conversion_floor_is_vacuously_cleared() -> None:
    """A None conversion floor (baseline supplied no accused-impostor meeting) passes."""

    floors = SupplyFloors(
        witnessed_event_rate=FloorPin(value=0.0, numerator=5),
        flags_per_meeting=FloorPin(value=0.0, numerator=10),
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
        backed_conversion_attempted=0,
        backed_conversion_converted=0,
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
    # The set's own era's block (eval/eras.py), no longer one global default.
    assert report["baseline_id"] == "stage-b-r3"  # was stage-b-r2
    assert len(report["per_game"]) == 50
    # Three Layer-1 gauges plus the two flags-per-meeting components the stage
    # block pins; the components trail the merged row, in that order.
    assert [g["name"] for g in report["supply_gauges"]] == [
        "witnessed_event_rate",
        "flags_per_meeting",
        "testimony_backed_conversion",
        "transcript_flags_per_meeting",
        "persisted_vent_flags_per_meeting",
    ]
    # Every gauge row carries the 15.19 advisory bit (False on 9p2i — no
    # one-event floor on this roster).
    assert [g["advisory"] for g in report["supply_gauges"]] == [False] * 5
    # The HARDENED mean over the committed baseline-6 bytes (was 54.97 pre-widening,
    # 42.25 on baseline 5 — the meeting-layer graduation's richer flag supply and
    # higher conversion lift the geomean; the conversion-coupled D2 gate still sinks
    # the suspicion-theater games). Re-derived on the same bytes when the backing
    # vocabulary gained the spoken saw_move placement: more attempts enter D2 than
    # convert, so the mean eases. Re-derived on the baseline-9 bytes, and again on
    # the promoted stage-b-r2 bytes, where the D2 gate sank thirteen games, and
    # on the promoted stage-b-r3 bytes, where it sinks twelve.
    assert report["mean_score"] == pytest.approx(28.73)  # was 24.73


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
