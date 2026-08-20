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
from typing import Any, get_args

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
from api.schemas import VIEW_MODEL_VERSION, BallotView, CurrentAction, GateView
from engine.events import EngineEvent
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    DEFAULT_SKIP_CONFIDENCE_THRESHOLD,
    INVALID_OBSERVATION_ID_MARKER,
    INVALID_REASON_ID_MARKER,
    TEAMMATE_VOTE_TARGET_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
)
from meetings.schemas import ContradictionRef, VoteBallot
from meetings.transcript import WEAK_CONTRADICTION_MARKER_PREFIX
from meetings.voting import INVALID_VOTE_TARGET_MARKER, SKIP_TARGET, tally_ballots
from observation.service import ObservationService
from orchestrator.seeder import seed_initial_state
from tests.api.fixtures.sample_replay import (
    write_meeting_replay,
    write_partial_replay,
    write_sample_replay,
)

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
def nine_p_two_i_loader(monkeypatch: pytest.MonkeyPatch) -> ReplayLoader:
    if not _NINE_P_TWO_I.is_dir():
        pytest.skip("committed 9p2i sample set not present")
    # Baseline 2 (Task 14.12) stamps the default-OFF Task-14.10
    # evidence_quality_lift lever ON, so flag-aware reconstruction of the
    # committed set requires it exported (else the loader's substrate guard
    # refuses the mismatch).
    monkeypatch.setenv("AILIBI_EVIDENCE_QUALITY_LIFT", "1")
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


def test_contract_version_and_action_set_move_in_lockstep() -> None:
    # The stamp is only a contract if both halves move together: the server
    # stamps this string and `frontend/src/api/client.ts` rejects any payload
    # carrying a different one, reading the value from the generated module. The
    # assertions above compare each side to itself and so cannot see a Python
    # bump that never reached the generated file; these pin the literal.
    assert VIEW_MODEL_VERSION == "2"
    generated = gen_frontend_types._OUT_TYPES.read_text(encoding="utf-8")
    assert f'export const VIEW_MODEL_VERSION = "{VIEW_MODEL_VERSION}";' in generated

    # Version "2" IS the widened action set, so it is pinned in the same breath:
    # eleven values under ONE name on both sides, in one order.
    assert get_args(CurrentAction) == (
        "IDLE",
        "MOVING",
        "TASK",
        "KILL",
        "VENT",
        "REPORT",
        "SABOTAGE",
        "PRETEND_TASK",
        "EMERGENCY",
        "REPAIR",
        "BLOCKED",
    )
    alias = " | ".join(f'"{value}"' for value in get_args(CurrentAction))
    assert f"export type CurrentAction = {alias};" in generated
    assert "current_action: CurrentAction;" in generated


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
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The recomputed §4.6 gate matches every recorded meeting outcome.

    This is the DoD's consistency gate: not just the formula, but that
    recomputing from the persisted ballots reproduces each meeting's actual
    EJECTED/SKIPPED + ``ejected_player_id`` across the committed 9p2i set — and
    agrees with ``meetings.voting.tally_ballots`` (the engine gate) ballot-for-
    ballot.
    """

    # The committed 9p2i set was re-recorded on the Phase-13.5 substrate (all four
    # flags ON); reconstruct it under the stamped substrate so the loader does not
    # raise ReplaySubstrateMismatchError under the bare CI env.

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


def test_fabricated_emergency_opening_marker_stripped_and_flagged(
    nine_p_two_i_loader: ReplayLoader,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The dev-jargon EMERGENCY_BODY_STRIP_MARKER (meetings.manager) must never
    # reach the wire (DESIGN.md §3.4 — parsed server-side, not rendered raw); its
    # presence is surfaced as the role-neutral ``fabricated_opening`` flag instead.
    # This is the load-bearing LEAK contract, asserted over every committed turn
    # below and enforced regardless of what the recording contains.
    #
    # Non-vacuity (Task 14.7 Featherless/Qwen3-32B qwen3_32b.v3 re-record): the
    # marker is baked into a turn's recorded free_text only when a live emergency
    # opening fabricated a found_body that the manager backstop then stripped — it
    # is NOT re-derived at reconstruction. The new committed 9p2i set contains ZERO
    # fabricated emergency openings (all 152 reconstructed openings have
    # fabricated_opening=False; the raw literal appears zero times), so the committed
    # set no longer exercises the strip path — a legitimate behavior difference of
    # the new model, not a leak. Rather than assert a property the bytes no longer
    # carry (or weaken the leak check), the non-vacuity guard SKIPS when the set has
    # none, mirroring the committed-set skip idiom in
    # tests/eval/test_win_condition_selfcheck.py. The strip → ``fabricated_opening``
    # mapping itself stays covered hermetically in tests/meetings/test_manager.py.
    from meetings.manager import EMERGENCY_BODY_STRIP_MARKER

    flagged = 0
    for meta in nine_p_two_i_loader.list_replays():
        replay = nine_p_two_i_loader.load_replay(meta.game_id)
        for meeting in replay.meetings:
            for turn in meeting.turns:
                assert EMERGENCY_BODY_STRIP_MARKER not in turn.free_text, turn.turn_id
                if turn.fabricated_opening:
                    flagged += 1
                    # A flagged turn is always the (emergency) opening.
                    assert turn.turn_kind == "opening", turn.turn_id
    if flagged == 0:
        pytest.skip(
            "the committed 9p2i set carries no fabricated emergency opening to strip "
            "(the Qwen3-32B re-record produced none); the leak contract above still "
            "ran over every turn, and the strip mapping is covered hermetically in "
            "tests/meetings/test_manager.py"
        )


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

    # Task 17.3: the 16.5 nulled-observation marker (mirrors invalid_reason_id).
    obs = INVALID_OBSERVATION_ID_MARKER.format(observation_id="p-7:9:4") + "saw a vent"
    assert _parse_rewrite_reasons(obs) == (("invalid_observation_id",), "saw a vent")

    # Task 17.3: the 16.6 coercion marker (mirrors teammate_coerced).
    coerced = UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-6") + "over threshold"
    assert _parse_rewrite_reasons(coerced) == (("uncited_coerced",), "over threshold")

    # Task 17.3: the live stacking order on the committed 9p2i set (seed 48) --
    # 16.5 nulls the citation first, 16.6 then coerces the now-uncited ballot, so
    # the coercion marker is prepended OUTSIDE the observation marker and both
    # chips surface front-to-back. The observation payload carries spaces/colons
    # (``'obs p-7:9:4'``) -- the repr-quoted match consumes it whole.
    stacked_gate = (
        UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-6")
        + INVALID_OBSERVATION_ID_MARKER.format(observation_id="obs p-7:9:4")
        + "I found p-3."
    )
    reasons_gate, clean_gate = _parse_rewrite_reasons(stacked_gate)
    assert reasons_gate == ("uncited_coerced", "invalid_observation_id")
    assert clean_gate == "I found p-3."

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
    monkeypatch: pytest.MonkeyPatch,
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


def test_gate_marker_chips_on_committed_9p2i_bytes(
    nine_p_two_i_loader: ReplayLoader,
) -> None:
    """Task 18.12: the gate-rewrite markers surface as spectator chips on the live
    cases the committed BASELINE-6 9p2i set carries, re-anchored after the vent
    widening re-record cascaded the trajectories.

    Census over the 971 committed ballots after the vent-widening re-record:
    invalid_reason_id x2, invalid_target x3, uncited_coerced (16.6) x1, and the
    live gate chip under_gate_redirect x13. The 16.5 nulled-observation citation
    (invalid_observation_id) stays honest-zero -- NO nulled observation citation
    survives anywhere on the committed set, asserted below. The 16.6 coercion
    (uncited_coerced) is NOT zero on baseline 6: exactly ONE ballot carries it
    (seed 36 m0, p-7's SKIP, STACKED with invalid_reason_id), re-pinned below (it
    was an honest-zero on the pre-widening record). The live gate-marker chip is
    the under-gate eject REDIRECT (the owner-principle guard: an under-gate eject
    target is redirected, never left to a random innocent), which fires on 13
    ballots (was 17); it is re-anchored here as the real-bytes chip pin so a future
    substrate cannot silently drop the chips. The DTO/chip rendering mechanism
    itself stays covered synthetically by tests/api/test_schemas.
    """

    ballots = [
        b
        for seed in range(50)
        for meeting in nine_p_two_i_loader.load_replay(f"headless-seed-{seed}").meetings
        for b in meeting.ballots
    ]

    # The 16.5 observation-null scenario class stays collapsed: no
    # invalid-observation-id (16.5) ballot survives on the baseline-6 committed set.
    assert not [b for b in ballots if "invalid_observation_id" in b.rewrite_reasons]
    # The 16.6 coercion re-appears with the vent-widening trajectories: exactly one
    # uncited-coerced ballot (seed 36 m0, stacked with invalid_reason_id).
    coerced = [b for b in ballots if "uncited_coerced" in b.rewrite_reasons]
    assert len(coerced) == 1

    # The live gate-marker chip: the under-gate eject redirect. 13 ballots carry it.
    redirected = [b for b in ballots if "under_gate_redirect" in b.rewrite_reasons]
    assert len(redirected) == 13

    # Anchor seed 22 m2: an under-gate eject redirected off the sub-gate target,
    # the marker stripped from the served render (the chip is NOT a fabricated
    # addition -- the clean prose is a suffix of the raw text).
    replay_22 = nine_p_two_i_loader.load_replay("headless-seed-22")
    anchored = [
        b
        for b in replay_22.meetings[2].ballots
        if "under_gate_redirect" in b.rewrite_reasons
    ]
    assert len(anchored) == 1
    (ballot_22,) = anchored
    assert ballot_22.rewrite_reasons == ("under_gate_redirect",)
    assert ballot_22.rationale_text_clean
    assert BALLOT_TARGET_REDIRECT_MARKER.partition("{")[0] not in (
        ballot_22.rationale_text_clean
    )
    assert ballot_22.rationale_text.endswith(ballot_22.rationale_text_clean)


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


def test_vent_events_projected_on_9p2i(
    nine_p_two_i_loader: ReplayLoader, monkeypatch: pytest.MonkeyPatch
) -> None:
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
    view = _advantage_view(
        state,
        tasks_completed=0,
        tasks_required=required,
        tasks_required_total=required,
    )
    assert view.crew_alive == 3 and view.impostors_alive == 1
    # task_progress(0) - pressure(1/3) = -1/3, clamped into [-1, 1].
    assert view.advantage == pytest.approx(-1 / 3)
    # The fixed display total threads through verbatim (here it equals the live
    # denominator since no crewmate has died yet).
    assert view.tasks_required_total == required
    # Full task completion + no impostors flips it positive.
    won = _advantage_view(
        seed_initial_state(seed=0, game_map=game_map, num_players=4, num_impostors=1),
        tasks_completed=required,
        tasks_required=required,
        tasks_required_total=required,
    )
    assert -1.0 <= won.advantage <= 1.0


def test_advantage_required_total_is_fixed_across_ticks(
    nine_p_two_i_loader: ReplayLoader,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The roster-meter denominator must be STABLE (Phase-12 close-audit): the
    # fixed game-start total is identical on every tick, even as the live
    # ``tasks_required`` shrinks when crewmates die. tasks_completed never
    # exceeds the fixed total, so the displayed meter is monotonic + bounded.
    replay = nine_p_two_i_loader.load_replay("headless-seed-12")
    totals = {tick.advantage.tasks_required_total for tick in replay.ticks}
    assert len(totals) == 1, "fixed display total drifted across ticks"
    (fixed_total,) = totals
    assert fixed_total > 0
    for tick in replay.ticks:
        adv = tick.advantage
        assert adv.tasks_completed <= fixed_total
        # The live win-condition denominator never exceeds the game-start total
        # (instances only leave the pool), so the fixed meter never under-reads.
        assert adv.tasks_required <= fixed_total


def test_advantage_in_bounds_on_real_set(
    nine_p_two_i_loader: ReplayLoader, monkeypatch: pytest.MonkeyPatch
) -> None:
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
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The advantage graph must show the ejection inflection: at an EJECTED
    # meeting tick the advantage frame is recomputed from the POST-resolution
    # state, so the ejected player is not counted even though the tick's
    # agent_states (the meeting roster) still show them alive.
    # Task 13.12 re-pointed this pin from seed-12 to seed-16. (The re-point's
    # original premise — "seed-12 no longer ejects, all SKIP" — is stale on the
    # bytes committed since: seed-12 ejects the crewmate p-3 at tick 7 and skips
    # at tick 15. seed-16 stays the anchor because Task 19.10 uses seed-12 as the
    # NON-meeting-final-frame control below, and reusing it here would couple the
    # two.)
    replay = nine_p_two_i_loader.load_replay("headless-seed-16")
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

    # Task 19.10: that mix is no longer implicit. The same frame now LABELS both
    # vintages — ``meeting_resolution`` names the meeting and its ejected player
    # and carries the frame's pre-resolution advantage, while ``advantage`` stays
    # the post-resolution one asserted above. The label is additive: every
    # assertion above still describes the same, unchanged fields.
    resolution = tick.meeting_resolution
    assert resolution is not None, "a resolved meeting frame must be labeled"
    assert resolution.meeting_id == ejection.meeting_id
    assert resolution.ejected_player_id == ejection.ejected_player_id
    alive_in_states = sum(1 for a in tick.agent_states if a.is_alive)
    pre = resolution.pre_advantage
    assert pre.crew_alive + pre.impostors_alive == alive_in_states
    assert (
        tick.advantage.crew_alive + tick.advantage.impostors_alive
        == alive_in_states - 1
    )


def test_non_meeting_frames_carry_no_resolution_label(
    nine_p_two_i_loader: ReplayLoader,
) -> None:
    """``meeting_resolution`` is ``None`` off a resolved meeting frame (19.10).

    The label means "this frame mixes two vintages"; a frame that resolved
    nothing must not claim one. seed-12 is the control because it ends on a KILL
    at tick 19, not on a meeting (its meetings sit at ticks 7 and 15), so the
    last frame — the one the finale card renders over — is unlabeled.
    """

    replay = nine_p_two_i_loader.load_replay("headless-seed-12")
    meeting_ticks = {meeting.tick for meeting in replay.meetings}
    assert replay.ticks[-1].tick not in meeting_ticks, (
        "seed-12 must not end on a meeting"
    )
    assert replay.ticks[-1].meeting_resolution is None
    labeled = {t.tick for t in replay.ticks if t.meeting_resolution is not None}
    assert labeled == meeting_ticks, "exactly the resolved meeting frames are labeled"


# ---------------------------------------------------------------------------
# Game finale: the recorded outcome composed server-side (Task 19.10)
# ---------------------------------------------------------------------------


def test_finale_pins_committed_eject_decided_game(
    nine_p_two_i_loader: ReplayLoader,
) -> None:
    """The finale is built from the recorded bytes of an eject-decided game.

    seed-1 is the cheapest CREWMATE_EJECT game in the committed 9p2i set (13
    recorded ticks, two meetings, both ejecting a real impostor) and it ends ON
    its decisive meeting — so one load pins the winner, the recorded end tick,
    the decisive-beat ordering, and the alive-at-end correction across the
    labeled pre/post mix at the same time (Task 19.10;
    audits/audit-phase-19-triage.md §7 item 11).

    ``final_tick`` is the recorded ``game_over`` tick (12), NOT
    ``metadata.total_ticks`` (13, a count of recorded ROWS) — the two differ by
    one here, which is exactly why 19.10 had to start retaining it.
    """

    replay = nine_p_two_i_loader.load_replay("headless-seed-1")
    finale = replay.finale
    assert finale is not None
    assert finale.winner == "CREWMATES"
    assert finale.winner_reason == "CREWMATE_EJECT"
    assert finale.final_tick == 12
    assert replay.metadata.total_ticks == 13, "the row count is a different number"

    # Ascending tick; within tick 12 the ejection precedes the terminal beat.
    assert [
        (e.tick, e.kind, e.actor_id, e.subject_id) for e in finale.decisive_events
    ] == [
        (5, "kill", "p-6", "p-3"),
        (7, "kill", "p-7", "p-4"),
        (8, "ejection", "p-8", "p-6"),
        (12, "ejection", "p-1", "p-7"),
        (12, "game_end", None, None),
    ]

    recaps = {recap.agent_id: recap for recap in finale.agent_recaps}
    assert [r.agent_id for r in finale.agent_recaps] == sorted(recaps)
    assert set(recaps) == {p.agent_id for p in replay.players}
    # Ground truth: both impostors were ejected, which is how the crew won. p-7's
    # row is the one that proves the alive-at-end correction — it is ejected ON
    # the final frame, whose agent_states (pre-resolution) still show it alive.
    for impostor in ("p-6", "p-7"):
        assert recaps[impostor].role == "IMPOSTOR"
        assert recaps[impostor].alive_at_end is False
    assert any(
        a.is_alive and a.agent_id == "p-7" for a in replay.ticks[-1].agent_states
    )

    # Belief side: the last meeting's ballots. Everyone who voted named p-7, a
    # real impostor; p-7 skipped, which names nobody (None, not False).
    assert recaps["p-1"].final_vote_target == "p-7"
    assert recaps["p-1"].final_vote_named_impostor is True
    assert recaps["p-7"].final_vote_target == "SKIP"
    assert recaps["p-7"].final_vote_named_impostor is None
    # p-3 died at tick 5, long before the last meeting — no ballot to recap.
    assert recaps["p-3"].final_vote_target is None
    assert recaps["p-3"].final_vote_named_impostor is None


def test_finale_pins_committed_wrong_ejection_game(
    nine_p_two_i_loader: ReplayLoader,
) -> None:
    """The contrast case: an impostor win decided by a WRONG ejection.

    seed-47 ejects the crewmate p-8 at tick 33 and hands the impostors parity —
    zero impostors are ejected all game. It is the exhibit that makes the recap's
    "what they knew vs the truth" split legible (every living voter named p-8, a
    crewmate → ``final_vote_named_impostor`` is ``False``, not ``None``), and the
    reason the finale must be reveal-gated on the frontend at all.
    """

    replay = nine_p_two_i_loader.load_replay("headless-seed-47")
    finale = replay.finale
    assert finale is not None
    assert finale.winner == "IMPOSTORS"
    assert finale.winner_reason == "IMPOSTOR_PARITY"
    assert finale.final_tick == 33

    ejections = [e for e in finale.decisive_events if e.kind == "ejection"]
    assert [(e.tick, e.subject_id) for e in ejections] == [(33, "p-8")]
    # Both earlier meetings resolved without an ejection and are recorded as
    # such — a skipped meeting is a decisive beat too (it is why nobody left).
    assert [e.tick for e in finale.decisive_events if e.kind == "meeting_skipped"] == [
        7,
        14,
    ]

    recaps = {recap.agent_id: recap for recap in finale.agent_recaps}
    assert recaps["p-8"].role == "CREWMATE"
    assert recaps["p-8"].alive_at_end is False
    assert recaps["p-1"].final_vote_target == "p-8"
    assert recaps["p-1"].final_vote_named_impostor is False
    # An authored ballot: the meeting layer rewrote nothing on this one.
    assert recaps["p-1"].final_vote_rewritten is False
    # Neither impostor was ever ejected; both survive to the end.
    assert all(recaps[pid].alive_at_end is True for pid in ("p-1", "p-9"))


def test_finale_recap_flags_a_rewritten_ballot_and_withholds_judgment(
    nine_p_two_i_loader: ReplayLoader,
) -> None:
    """A REWRITTEN ballot is flagged and never judged as belief (Task 19.10
    review).

    seed-22's last meeting records p-5's ballot with the ``under_gate_redirect``
    audit marker: the authored target was redirected to the tallied ``p-7``, and
    the recorded rationale explicitly OPPOSES p-7's ejection ("the herd is wrong
    to eject p-7"). Presenting that target under "what they knew" — worse,
    stamping it "named an impostor" — would invert the agent's recorded
    reasoning, so the recap carries ``final_vote_rewritten=True`` and a ``None``
    judgment for it, while an unmarked co-voter on the same meeting keeps the
    ordinary ``True`` judgment. Only TARGET-rewriting markers set the flag
    (``_TARGET_REWRITE_LABELS``); a citation-only rewrite leaves the authored
    target intact and stays unflagged.
    """

    replay = nine_p_two_i_loader.load_replay("headless-seed-22")
    last = replay.meetings[-1]
    redirected = next(b for b in last.ballots if b.voter == "p-5")
    assert "under_gate_redirect" in redirected.rewrite_reasons
    assert redirected.target == "p-7"

    finale = replay.finale
    assert finale is not None
    recaps = {recap.agent_id: recap for recap in finale.agent_recaps}
    # The rewritten ballot: tallied target shown, flagged, judgment withheld.
    assert recaps["p-5"].final_vote_target == "p-7"
    assert recaps["p-5"].final_vote_rewritten is True
    assert recaps["p-5"].final_vote_named_impostor is None
    # An unmarked co-voter on the SAME ballot sheet keeps the judgment: p-4 also
    # voted p-7 (an impostor — the ejection was right), authored and unflagged.
    assert recaps["p-4"].final_vote_target == "p-7"
    assert recaps["p-4"].final_vote_rewritten is False
    assert recaps["p-4"].final_vote_named_impostor is True


def test_skipped_meeting_frame_is_labeled_resolved(
    meeting_loader: ReplayLoader,
) -> None:
    """A SKIPPED meeting is RESOLVED — its frame is labeled, with no ejected id.

    Hermetic (``write_meeting_replay``), because no committed 9p2i game ends on a
    skipped meeting. The distinction the label draws is resolution, not ejection:
    ``meeting_resolution is None`` means "nothing resolved on this frame", while
    ``ejected_player_id is None`` inside a present label means "resolved, and the
    vote ejected nobody". Conflating the two would make a SKIPPED frame
    indistinguishable from an ordinary play tick.
    """

    replay = meeting_loader.load_replay("headless-seed-1")
    meeting = replay.meetings[0]
    assert meeting.outcome == "SKIPPED"
    tick = next(t for t in replay.ticks if t.tick == meeting.tick)
    resolution = tick.meeting_resolution
    assert resolution is not None, "a SKIPPED meeting still resolved the frame"
    assert resolution.meeting_id == meeting.meeting_id
    assert resolution.ejected_player_id is None
    # Nothing was ejected, so pre- and post-resolution advantage agree exactly.
    assert resolution.pre_advantage == tick.advantage

    # The fixture's shape derived, not spelled: the kill is the tick before the
    # report opens the meeting, and the game-end record is stamped on the quiet
    # tick after it resumes play (``write_meeting_replay``).
    finale = replay.finale
    assert finale is not None
    assert finale.final_tick == meeting.tick + 1
    assert [(e.tick, e.kind) for e in finale.decisive_events] == [
        (meeting.tick - 1, "kill"),
        (meeting.tick, "meeting_skipped"),
        (meeting.tick + 1, "game_end"),
    ]


def test_finale_is_none_for_a_partial_replay(tmp_path: Path) -> None:
    """No recorded ``game_over`` row → no finale (Task 19.10).

    A crashed / tick-budget-exhausted run has no recorded outcome, so the finale
    must be absent rather than synthesized from re-walked state — the same
    fail-quiet-but-honest contract ``metadata.winner`` already has for partials.
    """

    write_partial_replay(tmp_path / "replay-seed-0.jsonl", seed=0, ticks=3)
    replay = ReplayLoader(replay_dir=tmp_path).load_replay("headless-seed-0")
    assert replay.metadata.winner is None
    assert replay.finale is None


def test_finale_final_tick_prefers_the_recorded_game_end_tick(
    tmp_path: Path,
) -> None:
    """``finale.final_tick`` follows the RECORDED game-end row, not the walk.

    On every orchestrator-shaped recording the two coincide (``GameOverEvent.tick``
    is the emitting tick), so a fixture must force them apart or the
    recorded-tick path in ``_finale_view`` is unobserved — deleting the
    ``_ReplaySummary.final_tick`` threading would leave every other finale pin
    green (Task 19.10 review). The writer permits the disagreement: ``tick`` is a
    free argument on ``ReplayLog.record_game_end``.
    """

    write_sample_replay(
        tmp_path / "replay-seed-0.jsonl", seed=0, ticks=3, game_end_tick=41
    )
    replay = ReplayLoader(replay_dir=tmp_path).load_replay("headless-seed-0")
    finale = replay.finale
    assert finale is not None
    assert replay.ticks[-1].tick == 2, "the walk position the fallback would pick"
    assert finale.final_tick == 41, "the recorded row wins over the walk position"
    assert [(e.tick, e.kind) for e in finale.decisive_events] == [(41, "game_end")]


def test_finale_final_tick_falls_back_to_the_walk_without_a_recorded_tick(
    tmp_path: Path,
) -> None:
    """A game-end row with no ``tick`` (a direct-``ReplayLog`` writer) falls back
    to where the walk stopped — the documented ``_finale_view`` fallback."""

    write_sample_replay(
        tmp_path / "replay-seed-0.jsonl", seed=0, ticks=3, game_end_tick=None
    )
    replay = ReplayLoader(replay_dir=tmp_path).load_replay("headless-seed-0")
    finale = replay.finale
    assert finale is not None
    assert finale.final_tick == replay.ticks[-1].tick == 2


def test_finale_degrades_to_the_terminal_beat_without_meetings(
    meeting_loader: ReplayLoader,
) -> None:
    """A meeting-less game still gets a finale — one ``game_end`` beat, no votes.

    This is the shape the codegen fidelity fixture records
    (``scripts/gen_frontend_types.py``), so it must never raise: no meetings
    means no ballots, hence ``final_vote_target is None`` on every recap, and the
    decisive-events list degrades to the terminal beat alone rather than being
    empty (the card still has a tick to name).
    """

    replay = meeting_loader.load_replay("headless-seed-0")
    assert replay.meetings == ()
    finale = replay.finale
    assert finale is not None
    assert finale.winner == "CREWMATES"
    assert finale.final_tick == 2
    assert [(e.tick, e.kind) for e in finale.decisive_events] == [(2, "game_end")]
    assert {r.agent_id for r in finale.agent_recaps} == {
        p.agent_id for p in replay.players
    }
    for recap in finale.agent_recaps:
        assert recap.final_vote_target is None
        assert recap.final_vote_named_impostor is None
    assert all(t.meeting_resolution is None for t in replay.ticks)


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
    monkeypatch: pytest.MonkeyPatch,
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


def test_report_tick_fog_keeps_the_reported_body(
    nine_p_two_i_loader: ReplayLoader,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """On a body-report frame the reporter still sees the body they just found.

    ``engine.tick._apply_report`` marks the trigger body discovered before the
    post-advance fog solve, and ``compute_visibility_for_player`` excludes
    discovered bodies — so the loader re-opens the trigger body for that frame
    (``_agent_visibility_map(reopened_body_id=...)``). This pins that the
    reporter's field of view includes the reported body (which also shows in
    ``tick.bodies`` + the report event), i.e. the As-agent view matches what the
    agent could see at the meeting frame rather than dropping it.
    """

    saw_report = False
    for meta in nine_p_two_i_loader.list_replays():
        replay = nine_p_two_i_loader.load_replay(meta.game_id)
        for tick in replay.ticks:
            for event in tick.events:
                if event.type != "report_body":
                    continue
                saw_report = True
                reporter = next(
                    a for a in tick.agent_states if a.agent_id == event.reporter_id
                )
                assert reporter.visibility is not None
                seen_victims = {
                    body.victim_id for body in reporter.visibility.visible_bodies
                }
                assert event.body_of in seen_victims, (
                    f"{event.reporter_id} does not see the body it reported "
                    f"({event.body_of}) at tick {tick.tick} of {meta.game_id}"
                )
    assert saw_report, "expected at least one body-report meeting in the 9p2i set"


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


def _write_manifest_flags(
    replay_dir: Path, git_sha: str, *, refreshed_at: str = "2026-06-30"
) -> None:
    # The Task-14.7 8-column layout: a `flags` cell inserted after
    # prompt_versions, which shifts git_sha one head-index to the right. The
    # readers must key off the tail (cells[-4]) so they return git_sha, not the
    # refreshed_at DATE that now sits at the old head-index 5.
    (replay_dir / "MANIFEST.md").write_text(
        "# Sample Replay Manifest\n\n"
        "| seed | model | prompt_versions | flags | refreshed_at | git_sha "
        "| cost_usd | winner |\n"
        "|------|-------|-----------------|-------|--------------|---------"
        "|----------|--------|\n"
        "| 0 | Qwen/Qwen3-32B | accusation_round.qwen3_32b.v3 | "
        "testimony_as_content, unfreeze_memory | "
        f"{refreshed_at} | {git_sha} | 0.0 | CREWMATES |\n",
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


def test_manifest_git_sha_reads_git_sha_from_8col_flags_manifest(
    tmp_path: Path,
) -> None:
    # Regression (Task 14.7 flags column, PR #209 review): with the 8-column
    # layout the reader must return git_sha, NOT the refreshed_at date that sits
    # at the old head-index 5 — else same-day re-records read as fresh against
    # stale rubric bytes.
    _write_manifest_flags(tmp_path, "1e48c40", refreshed_at="2026-06-30")
    assert _manifest_git_sha(tmp_path) == "1e48c40"
    assert _manifest_git_sha(tmp_path) != "2026-06-30"


def test_rubric_stamps_git_sha_from_8col_flags_manifest(tmp_path: Path) -> None:
    # The rubric producer's _set_manifest_sha must likewise read git_sha (not the
    # date) from the 8-column manifest, so the freshness guard stays meaningful.
    _write_manifest_flags(tmp_path, "1e48c40", refreshed_at="2026-06-30")
    _rubric_score.regen_for_set(_facts(), tmp_path)  # no git_head -> stamps set sha
    view = ReplayLoader(replay_dir=tmp_path).rubric()
    assert view.git_head == "1e48c40"
    assert view.manifest_sha == "1e48c40"
    assert view.stale is False


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
