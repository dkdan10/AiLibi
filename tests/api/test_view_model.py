"""View-model contract v1 + cheap projections (Task 12.2).

Covers every additive Phase-12 loader projection (DESIGN.md §7), the versioned
contract stamp, the Playful identity palette swap (firewall-neutral), the
per-set rubric surface + staleness guard + its regen producer, and the
Pydantic→TS codegen drift gate. The two HARD gates from the task's Definition of
Done get dedicated tests:

* the §4.6 gate **consistency** test re-derives the verdict for every meeting in
  the committed 9p2i set and asserts it matches the recorded outcome /
  ``ejected_player_id`` (not just a formula unit test); and
* the codegen **fidelity** is pinned two ways — a drift test (regenerate and
  diff the committed ``api.ts`` / ``api.fidelity.ts``) here, plus the
  ``npm run tsc:check`` compile of the generated fidelity fixture in
  ``scripts/check.sh`` (which round-trips a real payload and narrows the
  discriminated unions).
"""

from __future__ import annotations

import importlib
import json
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from api.replay_loader import (
    _COLOR_PALETTE,
    _advantage_view,
    _color_for,
    _contradiction_view,
    _gate_view,
    _manifest_git_sha,
    _parse_rewrite_reasons,
    _rubric_is_stale,
    ReplayLoader,
    get_replay_loader,
)
from api.schemas import VIEW_MODEL_VERSION, BallotView, GateView
from engine.events import EngineEvent
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    DEFAULT_SKIP_CONFIDENCE_THRESHOLD,
    INVALID_REASON_ID_MARKER,
    TEAMMATE_VOTE_TARGET_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
)
from meetings.schemas import ContradictionRef, VoteBallot
from meetings.transcript import WEAK_CONTRADICTION_MARKER_PREFIX
from meetings.voting import INVALID_VOTE_TARGET_MARKER, SKIP_TARGET, tally_ballots
from observation.service import ObservationService
from orchestrator.seeder import seed_initial_state
from tests.api.fixtures.sample_replay import write_meeting_replay, write_sample_replay

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE_P_TWO_I = _REPO_ROOT / "replays" / "samples" / "9p2i"

# Import the (top-level) codegen module for the drift gate. ``scripts/`` is on
# mypy_path and resolved as bare module names (see tests/scripts/conftest.py).
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import gen_frontend_types  # noqa: E402

# The rubric regen producer is a top-level lab module (experiments/lab is not on
# mypy_path); import it dynamically so mypy does not try to resolve it by name.
_LAB_DIR = _REPO_ROOT / "experiments" / "lab"
if str(_LAB_DIR) not in sys.path:
    sys.path.insert(0, str(_LAB_DIR))
_rubric_score: Any = importlib.import_module("rubric_score")

# The committed Playful identity palette (tokens-seed.md identity[]); the SAME
# nine hues 12.1 transcribes into tokens.ts. Pinned here so the loader palette
# and the design token seed cannot drift.
_PLAYFUL_IDENTITY = (
    "#5DA83A",
    "#2BA45E",
    "#14A06E",
    "#0E9C93",
    "#128F9E",
    "#6C5CE0",
    "#8350D6",
    "#9A4FCB",
    "#A94FC6",
)
# Reserved firewall channels identity must never collide with (kill=red,
# suspicion=amber ramp, trust=blue) — claude-design-brief.md FIREWALL COLOR RULES.
_RESERVED_CHANNELS = {
    "#E23B2F",  # kill
    "#FBE6AE",
    "#F6C75A",
    "#EF9D33",
    "#DE6A24",
    "#C24A16",  # suspicion ramp
    "#2563D9",  # trust
}


@pytest.fixture
def meeting_loader(tmp_path: Path) -> ReplayLoader:
    write_meeting_replay(tmp_path / "replay-seed-1.jsonl", seed=1)
    write_sample_replay(tmp_path / "replay-seed-0.jsonl", seed=0, ticks=3)
    return ReplayLoader(replay_dir=tmp_path)


@pytest.fixture
def nine_p_two_i_loader() -> ReplayLoader:
    if not _NINE_P_TWO_I.is_dir():
        pytest.skip("committed 9p2i sample set not present")
    return ReplayLoader(replay_dir=_NINE_P_TWO_I)


# ---------------------------------------------------------------------------
# Versioned contract + identity palette (firewall-neutral)
# ---------------------------------------------------------------------------


def test_served_payload_carries_view_model_version(
    meeting_loader: ReplayLoader,
) -> None:
    replay = meeting_loader.load_replay("headless-seed-1")
    assert replay.view_model_version == VIEW_MODEL_VERSION
    # The served JSON (FastAPI dumps by_alias) carries the CONTRACT name
    # ``viewModelVersion`` exactly, so downstream compatibility guards match —
    # not the snake_case attribute name.
    served = json.loads(replay.model_dump_json(by_alias=True))
    assert served["viewModelVersion"] == VIEW_MODEL_VERSION
    assert "view_model_version" not in served


def test_player_color_serves_playful_identity_palette(
    meeting_loader: ReplayLoader,
) -> None:
    # The loader palette IS the committed Playful identity set (no rainbow).
    assert _COLOR_PALETTE == _PLAYFUL_IDENTITY
    # Identity is disjoint from every reserved firewall channel (no collisions).
    assert not (set(_COLOR_PALETTE) & _RESERVED_CHANNELS)
    # p-N maps deterministically into it, and every served color is from it.
    assert _color_for("p-1") == "#5DA83A"
    replay = meeting_loader.load_replay("headless-seed-1")
    for player in replay.players:
        assert player.color in _COLOR_PALETTE


# ---------------------------------------------------------------------------
# §4.6 gate — formula unit test + the CONSISTENCY test across the 9p2i set
# ---------------------------------------------------------------------------


def _ballot(voter: str, target: str, confidence: float) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=confidence,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text="",
    )


def _to_vote_ballot(ballot: BallotView) -> VoteBallot:
    """Reconstruct the engine ballot from the served DTO (for the gate cross-check)."""

    return VoteBallot(
        voter=ballot.voter,
        target=ballot.target,
        confidence=ballot.confidence,
        primary_reason_id=ballot.primary_reason_id,
        considered_alternatives=ballot.considered_alternatives,
        rationale_text=ballot.rationale_text,
    )


def test_gate_view_matches_the_voting_rule() -> None:
    threshold = DEFAULT_SKIP_CONFIDENCE_THRESHOLD
    # EJECTED: sole plurality leader with a >= 0.6 ballot.
    ejected = _gate_view(
        [_ballot("a", "p-2", 0.8), _ballot("b", "p-2", 0.4), _ballot("c", "SKIP", 0.9)]
    )
    assert ejected == GateView(
        leader="p-2", leader_max_confidence=0.8, threshold=threshold, passed=True
    )
    # Sole plurality leader but no confident ballot -> SKIPPED (sub-gate): the
    # leader is still reported, but the gate does not pass.
    sub_gate = _gate_view(
        [_ballot("a", "p-2", 0.5), _ballot("b", "p-2", 0.4), _ballot("c", "SKIP", 0.1)]
    )
    assert sub_gate.leader == "p-2" and sub_gate.passed is False
    # Tie between non-SKIP targets -> no leader, not passed.
    tie = _gate_view([_ballot("a", "p-2", 0.9), _ballot("b", "p-3", 0.9)])
    assert tie.leader is None and tie.passed is False
    # SKIP plurality -> no leader.
    skip = _gate_view([_ballot("a", "SKIP", 0.9), _ballot("b", "p-2", 0.9)])
    assert skip.leader is None and skip.passed is False
    # Empty ballots -> not passed.
    assert _gate_view([]).passed is False
    # Inclusive at exactly the threshold.
    assert _gate_view([_ballot("a", "p-2", threshold)]).passed is True


def test_gate_consistency_across_committed_9p2i_set(
    nine_p_two_i_loader: ReplayLoader,
) -> None:
    """The recomputed §4.6 gate matches every recorded meeting outcome.

    This is the DoD's consistency gate: not just the formula, but that
    recomputing from the persisted ballots reproduces each meeting's actual
    EJECTED/SKIPPED + ``ejected_player_id`` across the committed 9p2i set — and
    agrees with ``meetings.voting.tally_ballots`` (the engine gate) ballot-for-
    ballot.
    """

    meetings_checked = 0
    for meta in nine_p_two_i_loader.list_replays():
        replay = nine_p_two_i_loader.load_replay(meta.game_id)
        for meeting in replay.meetings:
            meetings_checked += 1
            gate = meeting.gate
            # passed mirrors the recorded outcome; leader mirrors the ejected id.
            assert gate.passed == (meeting.outcome == "EJECTED"), meeting.meeting_id
            if gate.passed:
                assert gate.leader == meeting.ejected_player_id, meeting.meeting_id
            # And it agrees with the engine gate (tally_ballots) run on the same
            # persisted ballots, reconstructed back into VoteBallot.
            outcome, ejected = tally_ballots(
                [_to_vote_ballot(b) for b in meeting.ballots],
                skip_confidence_threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD,
            )
            assert outcome == meeting.outcome, meeting.meeting_id
            assert ejected == meeting.ejected_player_id, meeting.meeting_id
    assert meetings_checked > 0, "expected meetings in the committed 9p2i set"


# ---------------------------------------------------------------------------
# Parsed ballot rewrite markers + clean rationale
# ---------------------------------------------------------------------------


def test_parse_rewrite_reasons_uses_imported_markers() -> None:
    # No marker -> no reasons, clean == original.
    assert _parse_rewrite_reasons("I think p-2 vented.") == ((), "I think p-2 vented.")

    # A single prefix marker is stripped; the model text remains.
    teammate = TEAMMATE_VOTE_TARGET_MARKER.format(target="p-4") + "cover for ally"
    assert _parse_rewrite_reasons(teammate) == (("teammate_coerced",), "cover for ally")

    # Stacked prefixes are all collected, front-to-back.
    stacked = (
        INVALID_VOTE_TARGET_MARKER.format(target="ghost")
        + INVALID_REASON_ID_MARKER.format(reason_id="m:turn-9")
        + "real text"
    )
    reasons, clean = _parse_rewrite_reasons(stacked)
    assert reasons == ("invalid_target", "invalid_reason_id")
    assert clean == "real text"

    # The redirect marker.
    redirect = BALLOT_TARGET_REDIRECT_MARKER.format(target="p-7") + "argmax pick"
    assert _parse_rewrite_reasons(redirect) == (("under_gate_redirect",), "argmax pick")

    # VOTE_PARSE_DEFAULT is the WHOLE rationale -> clean is empty.
    parse_default = VOTE_PARSE_DEFAULT_MARKER.format(head="<<garbage>>")
    assert _parse_rewrite_reasons(parse_default) == (("parse_default",), "")

    # The invalid VALUE itself contains the marker's tail text: the repr-quoted
    # payload is consumed whole, so the strip stops at the REAL marker end, not
    # inside the quoted value (P3 edge case).
    nasty = (
        INVALID_VOTE_TARGET_MARKER.format(target="x normalized to SKIP] y")
        + "real rationale"
    )
    assert _parse_rewrite_reasons(nasty) == (("invalid_target",), "real rationale")


def test_ballot_markers_parse_on_the_real_9p2i_set(
    nine_p_two_i_loader: ReplayLoader,
) -> None:
    saw_rewrite = False
    for meta in nine_p_two_i_loader.list_replays():
        replay = nine_p_two_i_loader.load_replay(meta.game_id)
        for meeting in replay.meetings:
            for ballot in meeting.ballots:
                if ballot.rewrite_reasons:
                    saw_rewrite = True
                    # clean is the original with the markers stripped.
                    assert ballot.rationale_text_clean != ballot.rationale_text
                    assert ballot.rationale_text.endswith(ballot.rationale_text_clean)
    assert saw_rewrite, "expected at least one rewritten ballot in the 9p2i set"


# ---------------------------------------------------------------------------
# Contradiction weak/severity (via the imported predicate)
# ---------------------------------------------------------------------------


def _contradiction(description: str) -> ContradictionRef:
    return ContradictionRef(
        contradiction_id="c1",
        kind="alibi_vs_sighting",
        event_a_id="a",
        event_b_id="b",
        subjects=("p-2",),
        description=description,
    )


def test_contradiction_weak_strong_class() -> None:
    weak = _contradiction_view(
        _contradiction(f"conflict {WEAK_CONTRADICTION_MARKER_PREFIX}narrow window]")
    )
    assert weak.weak is True and weak.severity == "weak"

    strong = _contradiction_view(_contradiction("hard alibi conflict"))
    assert strong.weak is False and strong.severity == "strong"


# ---------------------------------------------------------------------------
# Per-tick projections: vent events, killed_by bodies, sabotage, advantage
# ---------------------------------------------------------------------------


def test_vent_events_projected_on_9p2i(nine_p_two_i_loader: ReplayLoader) -> None:
    found = False
    replay = nine_p_two_i_loader.load_replay("headless-seed-12")
    for tick in replay.ticks:
        for event in tick.events:
            if event.type == "vent":
                found = True
                assert event.phase in ("enter", "exit")
                assert event.from_room_id and event.to_room_id
                assert event.traversal_ticks >= 0
    assert found, "expected vent events in a 9p2i game with impostor vent use"


def test_killed_by_body_projection(meeting_loader: ReplayLoader) -> None:
    replay = meeting_loader.load_replay("headless-seed-1")
    impostor = next(p.agent_id for p in replay.players if p.role == "IMPOSTOR")
    bodies = [body for tick in replay.ticks for body in tick.bodies]
    assert bodies, "the meeting fixture kills a crewmate -> a body must persist"
    # killed_by is the privileged spectator attribution (the impostor).
    assert all(body.killed_by == impostor for body in bodies)


def test_advantage_view_formula() -> None:
    game_map = load_canonical_map()
    state = seed_initial_state(
        seed=0, game_map=game_map, num_players=4, num_impostors=1
    )
    required = len(state.tasks)
    view = _advantage_view(state, tasks_completed=0, tasks_required=required)
    assert view.crew_alive == 3 and view.impostors_alive == 1
    # task_progress(0) - pressure(1/3) = -1/3, clamped into [-1, 1].
    assert view.advantage == pytest.approx(-1 / 3)
    # Full task completion + no impostors flips it positive.
    won = _advantage_view(
        seed_initial_state(seed=0, game_map=game_map, num_players=4, num_impostors=1),
        tasks_completed=required,
        tasks_required=required,
    )
    assert -1.0 <= won.advantage <= 1.0


def test_advantage_in_bounds_on_real_set(nine_p_two_i_loader: ReplayLoader) -> None:
    replay = nine_p_two_i_loader.load_replay("headless-seed-12")
    # Ejection meeting ticks carry POST-resolution advantage (the ejected player
    # is gone) while their agent_states are PRE-resolution, so the strict
    # advantage==alive equality holds only off those ticks.
    ejection_ticks = {m.tick for m in replay.meetings if m.outcome == "EJECTED"}
    for tick in replay.ticks:
        adv = tick.advantage
        assert -1.0 <= adv.advantage <= 1.0
        alive = sum(1 for a in tick.agent_states if a.is_alive)
        if tick.tick in ejection_ticks:
            assert adv.crew_alive + adv.impostors_alive == alive - 1
        else:
            assert adv.crew_alive + adv.impostors_alive == alive


def test_advantage_reflects_post_meeting_ejection(
    nine_p_two_i_loader: ReplayLoader,
) -> None:
    # The advantage graph must show the ejection inflection: at an EJECTED
    # meeting tick the advantage frame is recomputed from the POST-resolution
    # state, so the ejected player is not counted even though the tick's
    # agent_states (the meeting roster) still show them alive.
    replay = nine_p_two_i_loader.load_replay("headless-seed-12")
    ejection = next(m for m in replay.meetings if m.outcome == "EJECTED")
    tick = next(t for t in replay.ticks if t.tick == ejection.tick)
    ejected_still_in_states = any(
        a.is_alive and a.agent_id == ejection.ejected_player_id
        for a in tick.agent_states
    )
    assert ejected_still_in_states, "agent_states are the pre-resolution roster"
    expected_alive = sum(
        1
        for a in tick.agent_states
        if a.is_alive and a.agent_id != ejection.ejected_player_id
    )
    assert tick.advantage.crew_alive + tick.advantage.impostors_alive == expected_alive


# ---------------------------------------------------------------------------
# Belief frames: per-meeting snapshot + Error vs ground truth
# ---------------------------------------------------------------------------


def test_belief_frames_served_with_error_projection(
    meeting_loader: ReplayLoader,
) -> None:
    replay = meeting_loader.load_replay("headless-seed-1")
    n_players = len(replay.players)
    frames = meeting_loader.belief_frames("headless-seed-1")
    assert frames, "the meeting fixture has one meeting -> one belief frame"
    for frame in frames:
        # The FULL N×N observer×subject grid (diagonal included) — a stable
        # square the 9×9 matrix renders without synthesizing the diagonal.
        assert len(frame.entries) == n_players * n_players
        pairs = {(c.observer, c.subject) for c in frame.entries}
        assert len(pairs) == len(frame.entries)  # no dupes; full grid
        diagonal = [c for c in frame.entries if c.observer == c.subject]
        assert len(diagonal) == n_players  # one self/N-A cell per player
        for cell in frame.entries:
            # error is the signed Belief - Truth projection vs PlayerView.role.
            truth = 1.0 if cell.subject_is_impostor else 0.0
            assert cell.error == pytest.approx(cell.suspicion - truth)
            # A self cell is never a held belief (N/A diagonal).
            if cell.observer == cell.subject:
                assert cell.has_belief is False
            # "NO BELIEF YET"/self ≠ 0: a no-belief cell is the neutral prior.
            if not cell.has_belief:
                assert cell.suspicion == pytest.approx(0.5)
                assert cell.confidence == pytest.approx(0.0)
    # Early frames have agents who have formed no belief about some peers.
    assert any(
        not c.has_belief and c.observer != c.subject for f in frames for c in f.entries
    )
    # A zero-meeting game yields no frames (first-class empty state).
    assert meeting_loader.belief_frames("headless-seed-0") == ()


def test_belief_frames_are_cached(meeting_loader: ReplayLoader) -> None:
    meeting_loader.clear_cache()
    first = meeting_loader.belief_frames("headless-seed-1")
    second = meeting_loader.belief_frames("headless-seed-1")
    # Same cached object (the expensive memory re-walk runs once).
    assert first is second


# ---------------------------------------------------------------------------
# Per-tick As-agent visibility (fog) projection (Task 12.3, DESIGN.md §3.2, §7)
# ---------------------------------------------------------------------------


def test_agent_visibility_served_living_only_and_cached(
    nine_p_two_i_loader: ReplayLoader,
) -> None:
    """Every living agent carries a field of view; dead agents carry None; and the
    projection is LRU-cached (the expensive solve runs once per game)."""

    first = nine_p_two_i_loader.load_replay("headless-seed-12")
    second = nine_p_two_i_loader.load_replay("headless-seed-12")
    # Cost-bounded: the served payload is memoized, never recomputed per request.
    assert first is second

    living = dead = 0
    for tick in first.ticks:
        for agent in tick.agent_states:
            if agent.is_alive:
                assert agent.visibility is not None
                living += 1
            else:
                # A dead agent has no field of view to simulate.
                assert agent.visibility is None
                dead += 1
    # A real 9p2i game has deaths, so both branches are exercised (fog stops at
    # death).
    assert living > 0 and dead > 0


def test_agent_visibility_matches_observation_pipeline(
    meeting_loader: ReplayLoader, tmp_path: Path
) -> None:
    """The served fog is byte-identical to the firewall pipeline's own output.

    Reconstructs the committed no-op game (seed 0, 4p1i) independently through
    ``ObservationService.build_packet`` and asserts each living agent's served
    ``visibility`` equals the packet's ``visible_players`` / ``visible_bodies`` /
    ``audible_events`` — proving the projection REUSES the pipeline output (no
    re-implemented, drift-prone visibility) and that the As-agent view simulates
    the same firewall ``eval/leak_test.py`` validates.
    """

    game_map = load_canonical_map()
    state = seed_initial_state(
        seed=0, game_map=game_map, num_players=4, num_impostors=1
    )
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )

    def field_of_view(
        world: WorldState, events: Sequence[EngineEvent]
    ) -> dict[str, object]:
        out: dict[str, object] = {}
        for pid in sorted(world.players):
            if not world.players[pid].alive:
                continue
            packet = service.build_packet(
                world_state=world, agent_id=pid, engine_events=events
            )
            out[pid] = (
                tuple((p.id, p.room, p.action) for p in packet.visible_players),
                tuple((b.id, b.room, b.victim_id) for b in packet.visible_bodies),
                tuple((e.kind, e.room) for e in packet.audible_events),
            )
        return out

    # The loader synthesizes a Start frame (tick -1) from the seeded state, then a
    # TickView per recorded entry built from the POST-advance state (Finding 1), so
    # served tick ``k`` maps to the state after the (k+1)-th advance.
    expected: dict[int, dict[str, object]] = {-1: field_of_view(state, [])}
    for served_tick in range(3):  # write_sample_replay records 3 no-op ticks
        state, events = advance_tick(state, [], game_map=game_map)
        expected[served_tick] = field_of_view(state, events)
    service.close()

    replay = meeting_loader.load_replay("headless-seed-0")
    served: dict[int, dict[str, object]] = {}
    for tick in replay.ticks:
        frame: dict[str, object] = {}
        for agent in tick.agent_states:
            if agent.visibility is None:
                continue
            frame[agent.agent_id] = (
                tuple(
                    (p.id, p.room, p.action) for p in agent.visibility.visible_players
                ),
                tuple(
                    (b.id, b.room, b.victim_id) for b in agent.visibility.visible_bodies
                ),
                tuple((e.kind, e.room) for e in agent.visibility.audible_events),
            )
        served[tick.tick] = frame

    assert served == expected


# ---------------------------------------------------------------------------
# Endpoints: /replays/{id}/beliefs and /eval/rubric
# ---------------------------------------------------------------------------


@pytest.fixture
def client(meeting_loader: ReplayLoader) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_replay_loader] = lambda: meeting_loader
    with TestClient(app) as test_client:
        yield test_client


def test_beliefs_endpoint_serves_frames(client: TestClient) -> None:
    response = client.get("/replays/headless-seed-1/beliefs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    missing = client.get("/replays/headless-seed-404/beliefs")
    assert missing.status_code == 404


def test_rubric_endpoint_404_without_rubric_file(client: TestClient) -> None:
    # The meeting fixture dir ships no results-rubric-score.json -> empty state.
    assert client.get("/eval/rubric").status_code == 404


# ---------------------------------------------------------------------------
# Per-set rubric surface: staleness guard + regen producer
# ---------------------------------------------------------------------------


def _write_manifest(replay_dir: Path, git_sha: str) -> None:
    (replay_dir / "MANIFEST.md").write_text(
        "# Sample Replay Manifest\n\n"
        "| seed | model | prompt_versions | refreshed_at | git_sha | cost_usd | winner |\n"
        "|------|-------|-----------------|--------------|---------|----------|--------|\n"
        f"| 0 | qwen3.5:9b | accusation_round.v8 | 2026-06-16 | {git_sha} | 0.0 | CREWMATES |\n",
        encoding="utf-8",
    )


def _facts() -> dict[str, object]:
    return {
        "seedset": "9p2i",
        "git_head": "ignored-rest-stamped",
        "games": [
            {
                "seed": 5,
                "reason": "CREWMATE_EJECT",
                "roles": {"p-1": "IMPOSTOR", "p-2": "CREWMATE"},
                "deaths": [],
                "meetings": [
                    {
                        "ejected_player_id": "p-1",
                        "ejected_role": "IMPOSTOR",
                        "n_contradictions": 1,
                        "accusations": [{"speaker": "p-2", "accused": "p-1"}],
                        "contradictions_by_subject": {},
                    },
                    {
                        "ejected_player_id": None,
                        "n_contradictions": 0,
                        "accusations": [],
                    },
                ],
            }
        ],
    }


def test_manifest_git_sha_parses_uniform_set(tmp_path: Path) -> None:
    _write_manifest(tmp_path, "1e48c40")
    assert _manifest_git_sha(tmp_path) == "1e48c40"
    assert _manifest_git_sha(tmp_path / "missing") is None


def test_rubric_is_stale_prefix_logic() -> None:
    # Manifest stores a short sha; the rubric a full one -> prefix match = fresh.
    assert _rubric_is_stale("1e48c40deadbeef", "1e48c40") is False
    assert _rubric_is_stale("deadbeefcafe", "1e48c40") is True
    assert _rubric_is_stale(None, "1e48c40") is True
    assert _rubric_is_stale("1e48c40", None) is True


def test_rubric_regen_producer_and_staleness(tmp_path: Path) -> None:
    # The PRODUCER co-locates the rubric, stamped with a chosen git_head.
    fresh_head = "1e48c40aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    dest = _rubric_score.regen_for_set(_facts(), tmp_path, git_head=fresh_head)
    assert dest == tmp_path / "results-rubric-score.json"

    # The loader SERVES it and reports FRESH when the rubric commit prefixes the
    # set's MANIFEST sha.
    _write_manifest(tmp_path, "1e48c40")
    loader = ReplayLoader(replay_dir=tmp_path)
    view = loader.rubric()
    assert view.seedset == "9p2i"
    assert view.git_head == fresh_head
    assert view.manifest_sha == "1e48c40"
    assert view.stale is False
    assert view.per_game and view.per_game[0].seed == 5
    assert view.per_game[0].win_shape == "eject-decided"

    # A rubric scored at a different commit reads STALE.
    _rubric_score.regen_for_set(_facts(), tmp_path, git_head="deadbeefdeadbeef")
    assert ReplayLoader(replay_dir=tmp_path).rubric().stale is True


def test_rubric_regen_defaults_to_set_manifest_sha(tmp_path: Path) -> None:
    # With no explicit git_head, the producer stamps the SET's MANIFEST sha (the
    # replay version it scored), so a co-located rubric is fresh-by-construction
    # and the stamp is independent of cwd / git HEAD (review fixes for the
    # refresh-path + committed-artifact staleness).
    _write_manifest(tmp_path, "1e48c40")
    _rubric_score.regen_for_set(_facts(), tmp_path)
    view = ReplayLoader(replay_dir=tmp_path).rubric()
    assert view.git_head == "1e48c40"
    assert view.stale is False


def test_rubric_rejects_present_but_malformed_file(tmp_path: Path) -> None:
    # A PRESENT-but-malformed rubric must fail loud, not masquerade as an empty
    # "no highlights" state (the 404 path is reserved for an ABSENT rubric).
    rubric_path = tmp_path / "results-rubric-score.json"
    loader = ReplayLoader(replay_dir=tmp_path)

    rubric_path.write_text(json.dumps({"seedset": "9p2i"}), encoding="utf-8")
    with pytest.raises(ValueError, match="interestingness"):
        loader.rubric()

    rubric_path.write_text(
        json.dumps({"seedset": "9p2i", "interestingness": {"per_game": "nope"}}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="per_game"):
        loader.rubric()


def test_rubric_set_mismatch_is_stale(tmp_path: Path) -> None:
    # A rubric from a DIFFERENT set co-located here (seedset 4p1i) with a
    # matching git_head must still read STALE — the set identity (from the set's
    # roster.json) is part of the guard (DESIGN.md §7 "set or sha mismatch"), so
    # wrong-set highlights are never served as fresh.
    (tmp_path / "roster.json").write_text(
        json.dumps({"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2}),
        encoding="utf-8",
    )
    _write_manifest(tmp_path, "1e48c40")
    facts = {**_facts(), "seedset": "4p1i"}
    _rubric_score.regen_for_set(facts, tmp_path, git_head="1e48c40")
    view = ReplayLoader(replay_dir=tmp_path).rubric()
    assert view.seedset == "4p1i"
    assert view.stale is True  # set mismatch, despite the matching sha

    # The right-set rubric (seedset 9p2i) over the same roster reads FRESH.
    _rubric_score.regen_for_set(_facts(), tmp_path, git_head="1e48c40")
    assert ReplayLoader(replay_dir=tmp_path).rubric().stale is False


# ---------------------------------------------------------------------------
# Codegen drift gate (the compile/narrow fidelity runs in scripts/check.sh via
# npm run tsc:check over the generated api.fidelity.ts).
# ---------------------------------------------------------------------------


def test_generated_frontend_types_are_committed() -> None:
    expected_types = gen_frontend_types.render_types()
    committed_types = gen_frontend_types._OUT_TYPES.read_text(encoding="utf-8")
    assert committed_types == expected_types, (
        "frontend/src/types/api.ts is stale. Regenerate with: "
        "uv run python scripts/gen_frontend_types.py"
    )

    expected_fidelity = gen_frontend_types.render_fidelity()
    committed_fidelity = gen_frontend_types._OUT_FIDELITY.read_text(encoding="utf-8")
    assert committed_fidelity == expected_fidelity, (
        "frontend/src/types/api.fidelity.ts is stale. Regenerate with: "
        "uv run python scripts/gen_frontend_types.py"
    )


def test_fidelity_fixture_round_trips_payload_and_narrows_unions() -> None:
    fidelity = gen_frontend_types._OUT_FIDELITY.read_text(encoding="utf-8")
    # A real served payload assigned to the generated ReplayView type, carrying
    # the contract version under its served (aliased) key.
    assert "const _fidelityReplay: ReplayView = {" in fidelity
    assert '"viewModelVersion"' in fidelity
    # Exhaustive narrowing of each discriminated union (compiled by tsc:check).
    for union in ("TickEventView", "ObservationClaimView", "StatementClaimView"):
        assert f"_narrow_{union}(e: {union}): {union}" in fidelity
    assert "const _exhaustive: never = e;" in fidelity
    assert 'case "vent":' in fidelity


def test_skip_target_constant_round_trips_through_gate() -> None:
    # A defensive guard that the imported SKIP sentinel still excludes a leader.
    gate = _gate_view([_ballot("a", SKIP_TARGET, 0.9)])
    assert gate.leader is None
