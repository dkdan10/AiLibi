"""Tests for the off-menu action instrument (:mod:`eval.off_menu`, Task 18.3).

Two layers, mirroring ``tests/eval/test_funnel_pooling.py``:

* **Committed-bytes all-on-menu pins.** The committed replay sets were recorded
  by the scripted FSM, whose emitted action space is a strict subset of the
  oracle menu (the menu is a structural superset of the ``decide()`` ladder), so
  the instrument MUST read rate 0 on every one — the "all-on-menu fixture" that
  proves the gauge is calibrated and does not false-positive. The exact
  ``impostor_decisions`` N pinned here is the denominator Task 18.4 quotes; each
  N was MEASURED by running :func:`compute_off_menu_report` on the committed
  bytes on this host (see the per-fixture comments). If a committed set ever
  reads a non-zero off-menu count, that is a walk-fidelity bug OR a genuine
  FSM/menu divergence — investigate; never widen the membership test to force 0.

* **Synthetic can-it-move fixtures.** An instrument that cannot MOVE is not an
  instrument. Two hand-scripted 4p1i recordings (written fresh under ``tmp_path``
  through the production :class:`~orchestrator.replay.ReplayLog`, so state hashes
  are self-consistent regardless of engine drift) each plant EXACTLY ONE off-menu
  impostor decision — one off-menu-by-target (a ``move`` to a neighbour no option
  offered while a move-emitting option exists) and one off-menu-by-kind (a
  no-body vent-enter — an impostor-only ``vent`` the menu carries no ``vent``
  option for). Every other scripted impostor decision is on-menu; the assertion
  is that the instrument detects the planted decision at exactly ``1/N`` and
  identifies its ``(seed, tick, actor)``. A tampered-hash fixture and a
  dropped-action fixture prove the reconstruction fails loud rather than
  silently mis-measuring.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError

from engine.actions import Action
from engine.tick import advance_tick
from engine.world import load_canonical_map
from eval.off_menu import (
    OffMenuActionReport,
    OffMenuReconstructionError,
    compute_off_menu_report,
)
from orchestrator.replay import ReplayLog
from orchestrator.seeder import seed_initial_state

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SAMPLES_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"
_SAMPLES_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_CORPUS_FOUR = _REPO_ROOT / "replays" / "ml_corpus" / "4p1i"
_CORPUS_NINE = _REPO_ROOT / "replays" / "ml_corpus" / "9p2i"

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)


# --------------------------------------------------------------------------- #
# Module-scoped fixtures — each committed set is walked ONCE.                   #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def samples_four() -> OffMenuActionReport:
    return compute_off_menu_report(_SAMPLES_FOUR)


@pytest.fixture(scope="module")
def samples_nine() -> OffMenuActionReport:
    return compute_off_menu_report(_SAMPLES_NINE)


@pytest.fixture(scope="module")
def corpus_four() -> OffMenuActionReport:
    return compute_off_menu_report(_CORPUS_FOUR)


@pytest.fixture(scope="module")
def corpus_nine() -> OffMenuActionReport:
    return compute_off_menu_report(_CORPUS_NINE)


def _assert_all_on_menu(
    report: OffMenuActionReport, *, games: int, decisions: int
) -> None:
    """Assert a committed FSM set reads all-on-menu with the pinned denominator."""

    assert report.games_total == games
    # The impostor_decisions denominator (18.4 quotes this) — MEASURED by running
    # the instrument on the committed bytes on this host.
    assert report.impostor_decisions == decisions
    assert report.on_menu_total == decisions
    assert report.off_menu_total == 0
    assert report.off_menu_by_kind == 0
    assert report.off_menu_by_target == 0
    assert report.off_menu_rate == 0.0
    assert report.off_menu_decisions == ()
    assert report.scope_note  # the honest-scoping statement is always carried


# --------------------------------------------------------------------------- #
# Layer B — committed-bytes all-on-menu pins.                                   #
# --------------------------------------------------------------------------- #


def test_samples_four_all_on_menu(samples_four: OffMenuActionReport) -> None:
    """samples/4p1i (50 games): all-on-menu, N == 632 impostor decisions."""

    _assert_all_on_menu(samples_four, games=50, decisions=632)
    assert (samples_four.num_players, samples_four.num_impostors) == (4, 1)


def test_samples_nine_all_on_menu(samples_nine: OffMenuActionReport) -> None:
    """samples/9p2i (50 games): all-on-menu, N == 2461 impostor decisions."""

    _assert_all_on_menu(samples_nine, games=50, decisions=2461)
    assert (samples_nine.num_players, samples_nine.num_impostors) == (9, 2)


def test_corpus_four_all_on_menu(corpus_four: OffMenuActionReport) -> None:
    """ml_corpus/4p1i (50 games): all-on-menu, N == 579 impostor decisions."""

    _assert_all_on_menu(corpus_four, games=50, decisions=579)


def test_corpus_nine_all_on_menu(corpus_nine: OffMenuActionReport) -> None:
    """ml_corpus/9p2i (150 games): the canary denominator — all-on-menu, N == 6629.

    The largest committed corpus (6629 impostor decisions) and hence the most
    sensitive rate-0 pin: this is the set the definition-of-done's "committed
    FSM-generated corpus bytes read all-on-menu (rate 0)" most directly targets.
    The denominator moved 7693 -> 6629 at the Task-18.13 baseline-6 re-record: the
    graduated meeting layer resolves games in fewer ticks, so the impostors get
    fewer tactical decisions. The menu discipline is unchanged — still exactly 0
    off-menu at the larger-N read.
    """

    _assert_all_on_menu(corpus_nine, games=150, decisions=6629)
    assert (corpus_nine.num_players, corpus_nine.num_impostors) == (9, 2)


# --------------------------------------------------------------------------- #
# Synthetic recording machinery.                                               #
# --------------------------------------------------------------------------- #


def _act(actor: str, action_type: str, payload: dict[str, object]) -> Action:
    return _ACTION_ADAPTER.validate_python(
        {"actor": actor, "type": action_type, "payload": payload}
    )


def _write_scripted_replay(
    sample_dir: Path,
    *,
    seed: int,
    impostor_script: list[tuple[str, dict[str, object]]],
) -> str:
    """Write a hand-scripted 4p1i recording; return the impostor's player id.

    Seeds a real 4p1i game (``roster.json`` + ``replay-seed-{seed}.jsonl`` through
    the production :class:`~orchestrator.replay.ReplayLog`, so recorded state
    hashes are genuine and self-consistent) and drives one impostor action per
    tick from ``impostor_script`` while every crewmate waits. The recording ends
    mid-play (no ``game_over`` row — a valid partial recording the walk accepts).
    """

    sample_dir.mkdir(parents=True, exist_ok=True)
    (sample_dir / "roster.json").write_text(
        json.dumps({"num_players": 4, "num_impostors": 1, "tasks_per_crewmate": 1}),
        encoding="utf-8",
    )
    game_map = load_canonical_map()
    path = sample_dir / f"replay-seed-{seed}.jsonl"
    log = ReplayLog(path=path, game_id=f"headless-seed-{seed}")
    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
    )
    impostor = next(p for p, pl in state.players.items() if pl.role == "IMPOSTOR")
    for action_type, payload in impostor_script:
        actions: list[Action] = []
        for pid in sorted(state.players):
            if not state.players[pid].alive:
                continue
            if pid == impostor:
                actions.append(_act(pid, action_type, payload))
            else:
                actions.append(_act(pid, "wait", {}))
        input_tick = state.tick
        state, _events = advance_tick(state, actions, game_map=game_map)
        log.record_tick(input_tick, actions, state)
    log.close()
    return impostor


# --------------------------------------------------------------------------- #
# Layer A — synthetic can-it-move fixtures.                                     #
# --------------------------------------------------------------------------- #


def test_off_menu_by_target_detected(tmp_path: Path) -> None:
    """A ``move`` to a neighbour no option offers reads as one off-menu-by-target.

    Seed 0's impostor spawns in CAFETERIA with pretend task in ENGINEERING, so
    the tick-1 menu offers ``move:EAST_HALL`` (repositioning toward the pretend
    task) + ``wait`` — but NOT ``move:WEST_HALL`` (also a CAFETERIA neighbour, so
    engine-legal). Scripting the impostor to wait, then move WEST_HALL, then wait
    plants exactly one off-menu-by-target decision at tick 1 among N == 3.
    """

    impostor = _write_scripted_replay(
        tmp_path,
        seed=0,
        impostor_script=[
            ("wait", {}),
            ("move", {"to_room": "WEST_HALL"}),
            ("wait", {}),
        ],
    )
    report = compute_off_menu_report(tmp_path)

    assert report.impostor_decisions == 3
    assert report.off_menu_total == 1
    assert report.off_menu_by_target == 1
    assert report.off_menu_by_kind == 0
    assert report.on_menu_total == 2
    assert report.off_menu_rate == pytest.approx(1 / 3)

    (row,) = report.off_menu_decisions
    assert (row.seed, row.tick, row.actor) == (0, 1, impostor)
    assert row.classification == "off_menu_by_target"
    assert row.recorded_action_type == "move"
    assert row.recorded_action_payload == {"to_room": "WEST_HALL"}
    # By-target means the KIND was offered but this target was not.
    assert "move" in row.menu_intent_kinds


def test_off_menu_by_kind_detected(tmp_path: Path) -> None:
    """A no-body vent-enter reads as one off-menu-by-kind (menu has no ``vent``).

    The impostor repositions to ENGINEERING via EAST_HALL (both moves ARE menu
    reposition options toward the pretend task, hence on-menu), then enters
    ENGINEERING_VENT — a lone impostor may vent its own room, but the menu offers
    ``vent`` only as ``vent_exit`` (while already in a vent) or ``cover_vent``
    (with a co-located body), neither of which holds here. So the vent-enter is
    off-menu-by-kind: the recorded ``vent`` kind is absent from the menu entirely.
    The recording ends on the vent tick (in PLAY phase) so this is the ONLY
    off-menu decision among N == 3.
    """

    impostor = _write_scripted_replay(
        tmp_path,
        seed=0,
        impostor_script=[
            ("move", {"to_room": "EAST_HALL"}),
            ("move", {"to_room": "ENGINEERING"}),
            ("vent", {"vent_id": "ENGINEERING_VENT"}),
        ],
    )
    report = compute_off_menu_report(tmp_path)

    assert report.impostor_decisions == 3
    assert report.off_menu_total == 1
    assert report.off_menu_by_kind == 1
    assert report.off_menu_by_target == 0
    assert report.on_menu_total == 2
    assert report.off_menu_rate == pytest.approx(1 / 3)

    (row,) = report.off_menu_decisions
    assert (row.seed, row.tick, row.actor) == (0, 2, impostor)
    assert row.classification == "off_menu_by_kind"
    assert row.recorded_action_type == "vent"
    assert row.recorded_action_payload == {"vent_id": "ENGINEERING_VENT"}
    # By-kind means the recorded KIND was offered by no option at all.
    assert "vent" not in row.menu_intent_kinds


def test_tampered_state_hash_fails_loud(tmp_path: Path) -> None:
    """A corrupted per-tick ``state_hash`` raises :class:`OffMenuReconstructionError`.

    The walk verifies every recorded hash; a drifted/forged set must fail loud
    rather than silently mis-measure the off-menu rate (AGENTS.md "no silent
    fallbacks").
    """

    _write_scripted_replay(
        tmp_path,
        seed=0,
        impostor_script=[("wait", {}), ("wait", {})],
    )
    path = tmp_path / "replay-seed-0.jsonl"
    rewritten: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw:
            continue
        record = json.loads(raw)
        if record.get("kind", "tick") == "tick" and record.get("tick") == 0:
            record["state_hash"] = "0" * 64
        rewritten.append(json.dumps(record, sort_keys=True))
    path.write_text("\n".join(rewritten) + "\n", encoding="utf-8")

    with pytest.raises(OffMenuReconstructionError):
        compute_off_menu_report(tmp_path)


def test_missing_impostor_action_fails_loud(tmp_path: Path) -> None:
    """A tick with no action for a living impostor raises, never under-measures.

    Production records exactly one action per living player per tick, so a
    missing impostor action means a partial/drifted recording; silently skipping
    it would shrink the ``impostor_decisions`` denominator (AGENTS.md "no silent
    fallbacks"). The walk scores decisions BEFORE advancing, so this fires ahead
    of the (also-doomed) state-hash check.
    """

    impostor = _write_scripted_replay(
        tmp_path,
        seed=0,
        impostor_script=[("wait", {}), ("wait", {})],
    )
    path = tmp_path / "replay-seed-0.jsonl"
    rewritten: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw:
            continue
        record = json.loads(raw)
        if record.get("kind", "tick") == "tick" and record.get("tick") == 0:
            record["actions"] = [
                action for action in record["actions"] if action["actor"] != impostor
            ]
        rewritten.append(json.dumps(record, sort_keys=True))
    path.write_text("\n".join(rewritten) + "\n", encoding="utf-8")

    with pytest.raises(OffMenuReconstructionError, match="no recorded action"):
        compute_off_menu_report(tmp_path)


# --------------------------------------------------------------------------- #
# Report hygiene — schema stability + the empty-denominator convention.        #
# --------------------------------------------------------------------------- #


def test_report_is_frozen_and_json_round_trips(
    samples_four: OffMenuActionReport,
) -> None:
    """The report is a frozen value object with a stable JSON schema."""

    assert (
        OffMenuActionReport.model_validate_json(samples_four.model_dump_json())
        == samples_four
    )
    with pytest.raises(ValidationError):
        samples_four.off_menu_total = 99


def test_empty_denominator_rate_is_none() -> None:
    """``off_menu_rate`` is ``None`` (not 0.0) when there are no decisions to score.

    The ``eval`` empty-denominator convention: a set with no impostor decisions
    has an undefined rate, surfaced as ``None`` — distinct from a genuine 0.0
    (all decisions on-menu).
    """

    empty = OffMenuActionReport(
        replay_set_dir="/dev/null",
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
        games_total=0,
        impostor_decisions=0,
        on_menu_total=0,
        off_menu_total=0,
        off_menu_rate=None,
        off_menu_by_kind=0,
        off_menu_by_target=0,
        scope_note="n/a",
        off_menu_decisions=(),
    )
    assert empty.off_menu_rate is None
