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
from pathlib import Path

import pytest

from eval.watchability import (
    _BASELINE_SUPPLY_FLOORS,
    FloorPin,
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
    """HISTORICAL PIN: the frozen pre-15.19 spec still reproduces the lab scorer.

    Task 15.2's cross-implementation evidence — the committed
    ``experiments/lab/results-rubric-geomean.json`` vs this module on the same
    9p2i bytes — is kept reproducible under ``historical_15_2=True`` (the frozen
    subject-AGNOSTIC backing + UNCOUPLED D2 spec). This is the renamed pre-15.19
    parity test; it pins history and must never gate a champion. The LIVE
    hardened referee's committed-set behavior is pinned separately (the CLI
    aggregate test + the supply-floor tests below).

    Task 16.14 note: on the baseline-4 bytes this pin caught a real drift in the
    frozen bit — ``observation_backed_any`` had silently widened to the 15.4
    ``SawVentObservation`` type (absent from the 15.2-era extractor's isinstance
    tuple), diverging from the lab fixture on the first games where an
    accusation is backed ONLY by a vent sighting (seeds 5/22). The frozen bit
    was re-narrowed to mirror the extractor byte-for-byte
    (``eval/watchability.py::_testimony_vehicle``), so all 50 rows reproduce
    bit-exact again with no per-row exceptions.
    """

    fixture = json.loads(_GEOMEAN_FIXTURE.read_text())
    ref_by_seed = {row["seed"]: dict(row) for row in fixture["per_game"]}

    scores = _score_committed_set(_NINE, historical_15_2=True)
    assert len(scores) == 50
    assert {s.seed for s in scores} == set(ref_by_seed)

    for score in scores:
        ref = ref_by_seed[score.seed]
        assert score.reason == ref["reason"]
        assert score.n_meetings == ref["n_meetings"]
        for key in _PARITY_KEYS:
            assert getattr(score, key) == pytest.approx(ref[key], abs=1e-6), (
                f"seed {score.seed} {key}"
            )

    # The aggregate roll-ups, computed exactly as WatchabilityReport rounds them,
    # against the fixture's own roll-ups (bit-exact parity, no corrections).
    mean = round(math.fsum(s.score for s in scores) / len(scores), 2)
    median = round(statistics.median(s.score for s in scores), 2)
    assert mean == pytest.approx(fixture["mean_score"])
    assert median == pytest.approx(fixture["median_score"])
    # The fixture's floored games (0.0 score on a railroad breach) reproduce.
    floored = {s.seed for s in scores if s.floor_multiplier == 0.0}
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
    assert total == 11


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
    """The committed scripted-FSM baseline-6 sets clear their own re-pinned floors.

    The DoD anchor (15.19, re-recorded on the meeting-layer graduation slate at Task
    18.12): every gauge row passes, not just the composed verdict (the exact
    floor == measured equality is pinned separately by
    ``test_baseline_6_floor_pins_equal_the_measured_bytes``).
    """

    for sample_dir in (_NINE, _FOUR):
        report = compute_watchability(sample_dir)
        assert report.referee_passed is True
        assert report.supply_floors_passed is True
        assert all(gauge.passed for gauge in report.supply_gauges)


def test_baseline_6_floor_pins_equal_the_measured_bytes() -> None:
    """EXACT ANCHOR: each re-pinned floor equals the measured committed bytes.

    ``passed`` alone is one-sided (any floor at or below the true measured value
    clears it), so an under-pinned floor would silently weaken the gate with CI
    green. This pins BOTH sides at the Task 18.12 baseline-6 re-record: the
    measured gauge IS the recorded fraction, and the pinned floor IS the measured
    gauge — "the baseline passes at equality", made an assertion not a comment.
    """

    expected = {
        _NINE: {
            "witnessed_event_rate": 6 / 177,  # crew-witnessed kills (was 7/173)
            "flags_per_meeting": 180 / 165,  # 96 vent + 84 transcript (was 207/156)
            "testimony_backed_conversion": 78 / 136,  # SUBJECT-AWARE (was 78/133)
        },
        _FOUR: {
            "witnessed_event_rate": 1 / 61,  # numerator 1 -> ADVISORY (unchanged)
            "flags_per_meeting": 16 / 39,  # 11 vent + 5 transcript (unchanged)
            "testimony_backed_conversion": 9 / 30,  # SUBJECT-AWARE (was 10/30)
        },
    }
    for sample_dir, fractions in expected.items():
        report = compute_watchability(sample_dir)
        by_name = {g.name: g for g in report.supply_gauges}
        assert set(by_name) == set(fractions)
        for name, fraction in fractions.items():
            gauge = by_name[name]
            assert gauge.measured == fraction, f"{sample_dir.name} {name} measured"
            assert gauge.floor == fraction, f"{sample_dir.name} {name} floor pin"


def test_baseline_7_floor_pins_equal_the_measured_bytes() -> None:
    """EXACT ANCHOR: each baseline-7 floor equals the bytes it was pinned from.

    Same both-sides discipline as the baseline-6 anchor above — the measured
    gauge IS the recorded fraction and the pinned floor IS the measured gauge —
    so an under-pinned floor cannot silently weaken the block while the comments
    still claim self-consistency.

    Reconstruction is substrate-coupled, so this reads the Phase-20 slate the
    bytes were recorded at; the planted case below carries the "can it fail" half
    and needs no bytes at all.
    """

    expected = {
        _NINE: {
            "witnessed_event_rate": 3 / 177,  # crew-witnessed kills (was 6/177)
            "flags_per_meeting": 134 / 152,  # 92 vent + 42 transcript (was 180/165)
            "testimony_backed_conversion": 80 / 115,  # SUBJECT-AWARE (was 78/136)
        },
        _FOUR: {
            "witnessed_event_rate": 1 / 65,  # numerator 1 -> ADVISORY (was 1/61)
            "flags_per_meeting": 20 / 40,  # 20 vent + 0 transcript (was 16/39)
            "testimony_backed_conversion": 19 / 31,  # SUBJECT-AWARE (was 9/30)
        },
    }
    for sample_dir, fractions in expected.items():
        report = compute_watchability(sample_dir, baseline_id="baseline-7")
        assert report.referee_passed is True
        assert all(gauge.passed for gauge in report.supply_gauges)
        by_name = {gauge.name: gauge for gauge in report.supply_gauges}
        assert set(by_name) == set(fractions)
        for name, fraction in fractions.items():
            gauge = by_name[name]
            assert gauge.measured == fraction, f"{sample_dir.name} {name} measured"
            assert gauge.floor == fraction, f"{sample_dir.name} {name} floor pin"


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
        flags_per_meeting=134 / 152,  # at the pin -> ratio 1.0 -> floor == pin
        total_flags=134,
        persisted_vent_flags=92,
        meetings_total=152,
        testimony_backed_conversion=79 / 115,  # ONE conversion short of the pin
        backed_conversion_attempted=115,
        backed_conversion_converted=79,
    )
    passed, rows = evaluate_supply_floors(starved, floors)
    assert passed is False, "a below-floor conversion must fail the referee"
    conversion = next(r for r in rows if r.name == "testimony_backed_conversion")
    assert conversion.passed is False
    assert conversion.floor == 80 / 115
    assert conversion.advisory is False


def test_hardened_patches_fire_on_the_committed_9p2i_bytes() -> None:
    """LIVE-PATH SNAPSHOT: the 15.19 D2 patches measured on the committed bytes.

    The historical parity pin guards only the FROZEN path, and the CLI aggregate
    (mean 54.97) is a single scalar — neither shows the patches acting on any
    real committed game. This pins the live-vs-historical per-game delta on the
    baseline-6 9p2i bytes: the subject-aware railroad floor (patch 2) floors
    NO committed game (the graduated slate's citation gate leaves ZERO
    evidence-free crew railroads on the committed bytes — the mechanism stays
    covered by the synthetic ``test_subject_aware_backing_gates_conversion_and_railroad``;
    baseline 4 floored one, 29; baseline 3 four, 19/27/29/31), and on baseline-6
    the conversion-coupled D2 gate (patch 1) zeroes the separation term on NO
    committed game either — every game with live separation now carries a
    converted backed accusation or a flag, so live separation equals the frozen
    spec's on all 50 seeds (honest-zero census; baseline 5 zeroed 2/4/10/12/37/47,
    the mechanism itself pinned on synthetic bytes elsewhere in this file).
    """

    live = {s.seed: s for s in _score_committed_set(_NINE)}
    hist = {s.seed: s for s in _score_committed_set(_NINE, historical_15_2=True)}

    live_floored = {seed for seed, s in live.items() if s.floor_multiplier == 0.0}
    hist_floored = {seed for seed, s in hist.items() if s.floor_multiplier == 0.0}
    # Patch 2 (subject-aware backing -> the railroad floor's backed leg): the
    # hardened floor only ever ADDS railroads on the same bytes...
    assert hist_floored <= live_floored
    # ...and on baseline-5 9p2i it adds NONE — the graduated slate (J1/J2 citation
    # gate) leaves zero evidence-free crew railroads on the committed bytes (the
    # honest-zero census of a scenario class that collapsed with the substrate;
    # the mechanism itself is pinned on synthetic bytes elsewhere in this file).
    assert live_floored - hist_floored == set()

    # Patch 1 (conversion-coupled D2): on baseline-6 NO committed game is
    # suspicion theater — every game with rendered-suspicion separation now
    # carries a converted backed accusation or a contradiction flag, so the gate
    # zeroes nothing and live separation equals the frozen spec's on every seed
    # (honest-zero census; baseline 5 gated 2/4/10/12/37/47 to 0 live). The
    # patch-1-zeroed set is therefore EMPTY: no seed has live separation collapsed
    # to zero while the historical path kept it positive.
    patch1_zeroed = {
        seed
        for seed in live
        if live[seed].d2_separation_norm == 0.0 and hist[seed].d2_separation_norm > 0.0
    }
    assert patch1_zeroed == set()


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

    source = _FOUR / "replay-seed-0.jsonl"
    lines = source.read_text().splitlines()
    kept = [line for line in lines if "meeting_id" not in json.loads(line)]
    assert len(kept) < len(lines)  # a meeting row was dropped (this game has one)

    (tmp_path / "replay-seed-0.jsonl").write_text("\n".join(kept) + "\n")
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

    lines = (_FOUR / "replay-seed-0.jsonl").read_text().splitlines()
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

    lines = (_FOUR / "replay-seed-0.jsonl").read_text().splitlines()
    forged: list[str] = []
    changed = False
    for line in lines:
        row = json.loads(line)
        if row.get("kind") == "game_over":
            assert row["reason"] != "CREWMATE_EJECT"  # seed 0 is an impostor win
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

    lines = (_FOUR / "replay-seed-0.jsonl").read_text().splitlines()
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

    lines = (_FOUR / "replay-seed-0.jsonl").read_text().splitlines()
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

    lines = (_FOUR / "replay-seed-0.jsonl").read_text().splitlines()
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


def test_baseline_6_witnessed_event_rate_is_the_measured_anchor() -> None:
    """The 9p2i witnessed-event rate is the 6/177 = 3.39% crew-witnessed anchor.

    Computed from the committed bytes (not the pinned constant), so it tracks the
    default baseline: the vent-widening baseline 6 records 6 crew-witnessed of 177
    kills in 9p2i (the pre-widening baseline 6 was 7/173 = 4.05%; baseline 5 was
    7/203 = 3.45%).
    """

    report = compute_watchability(_NINE)
    witnessed = next(
        g for g in report.supply_gauges if g.name == "witnessed_event_rate"
    )
    assert witnessed.measured == pytest.approx(6 / 177)


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
    assert _persisted_vent_flag_count(report) == 11

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

    assert _persisted_vent_flag_count(report_with_vent) == 12
    before = _supply_gauge_values(report, [], [])
    after = _supply_gauge_values(report_with_vent, [], [])
    assert after.persisted_vent_flags == 12
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
    assert report["baseline_id"] == "baseline-6"
    assert len(report["per_game"]) == 50
    assert len(report["supply_gauges"]) == 3
    # Every gauge row carries the 15.19 advisory bit (False on 9p2i — no
    # one-event floor on this roster).
    assert [g["advisory"] for g in report["supply_gauges"]] == [False, False, False]
    # The HARDENED mean over the committed baseline-6 bytes (was 54.97 pre-widening,
    # 42.25 on baseline 5 — the meeting-layer graduation's richer flag supply and
    # higher conversion lift the geomean; the conversion-coupled D2 gate still sinks
    # the suspicion-theater games).
    assert report["mean_score"] == pytest.approx(54.58)


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
