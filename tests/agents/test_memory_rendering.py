"""Tests for ``agents/memory/store.py::render_for_prompt`` (DESIGN.md §6.6).

Covers the R-6 acceptance gate (composite memory surface reads from
episodic, working, and belief stores) and the R-10 acceptance gate
(packet leak scanners are reused against rendered output). See
``audits/audit-2026-05-15-0225-reconciled.md`` §§R-6/R-10.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final, cast

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import BaseModel

from agents.memory.beliefs import ContradictionRef
from agents.memory.episodic import EpisodicEvent
from agents.memory.store import (
    DEFAULT_TOKEN_BUDGET,
    ENV_COALESCED_MEMORY_RENDER,
    ENV_SELF_LOCATION_TRAIL,
    ENV_TASK_COMPLETION_FROM_EVENTS,
    SELF_LOCATION_TRAIL_MAX_SPANS,
    AgentMemory,
    coalesced_memory_render_enabled,
    render_for_prompt,
    self_location_trail_enabled,
    task_completion_from_events_enabled,
)
from engine.world import WorldState, load_canonical_map
from eval.leak_test import (
    JsonValue,
    _assert_no_recursive_hidden_fields,
    _assert_no_role_bearing_values,
)
from llm.budget import GameBudget
from llm.client import CallKind, LLMResponse
from llm.fake_provider import FakeProvider
from meetings.manager import INVALID_OBSERVATION_ID_MARKER, MeetingTrigger
from meetings.schemas import VoteBallot
from agents.base import AgentInterface
from orchestrator.game import (
    DEFAULT_TASKS_PER_CREWMATE,
    DefaultMeetingRunner,
    HeadlessGame,
    MeetingArtifacts,
    MeetingAwareAgent,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries
from orchestrator.scheduler import TickScheduler

_FIXTURE_DIR = Path("tests/fixtures/memory_rendering")
# The completed-task lever, toggled through ``render_for_prompt(env=...)`` so no
# test mutates ``os.environ`` (the suite runs parallel).
_ROLE_LINE_PATTERN = re.compile(r"^## Your role: .+$\n?", re.MULTILINE)
_ROLE_VALUE_PATTERN = re.compile(r"^## Your role: (.+)$", re.MULTILINE)


def _scan_rendered_view(view: str) -> None:
    """Apply the canonical packet leak scanners to a rendered prompt view.

    The agent's own role legitimately appears at ``## Your role: X``.
    We map that line onto the ``self_state.role`` path that
    ``eval/leak_test.py`` already allow-lists, then scan the remaining
    body in full. This mirrors the R-10 contract: the rendered surface
    is held to the same anti-leak invariants as ObservationPackets
    (`audits/audit-2026-05-15-0225-reconciled.md` §R-10).
    """

    role_match = _ROLE_VALUE_PATTERN.search(view)
    role = role_match.group(1) if role_match else ""
    body = _ROLE_LINE_PATTERN.sub("", view)
    payload: JsonValue = {
        "self_state": {"role": role},
        "rendered_body": body,
    }
    _assert_no_recursive_hidden_fields(payload)
    _assert_no_role_bearing_values(payload)


def _self_state_event(
    *,
    tick: int,
    role: str = "CREWMATE",
    room: str = "CAFETERIA",
    pending_task_id: str | None = None,
    agent_id: str | None = None,
    fellow_impostor_ids: tuple[str, ...] | None = None,
    owned_task_ids: tuple[str, ...] | None = None,
    observation_id: str | None = None,
    in_vent: bool | None = None,
) -> EpisodicEvent:
    payload: dict[str, Any] = {
        "room": room,
        "role": role,
        "pending_task_id": pending_task_id,
    }
    # ``in_vent`` rides the same privileged self channel; only added when supplied
    # so every existing fixture renders byte-identically.
    if in_vent is not None:
        payload["in_vent"] = in_vent
    # ``owned_task_ids`` is added only when supplied, so a fixture can still
    # express a pre-widening row that carries no set at all.
    if owned_task_ids is not None:
        payload["owned_task_ids"] = owned_task_ids
    # ``agent_id`` / ``fellow_impostor_ids`` drive the Task 9.3 render guards
    # (DESIGN.md §4.7). They are only added to the payload when supplied, so
    # existing fixtures/tests that omit them render byte-identically.
    if agent_id is not None:
        payload["agent_id"] = agent_id
    if fellow_impostor_ids is not None:
        payload["fellow_impostor_ids"] = fellow_impostor_ids
    return EpisodicEvent(
        tick=tick,
        type="self_state",
        payload=payload,
        provenance="observed",
        observation_id=observation_id,
    )


def _global_status_event(*, tick: int, completed: int, total: int) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="global_status",
        payload={"tasks_completed": completed, "tasks_total": total},
        provenance="inferred",
    )


def _saw_player_event(
    *,
    tick: int,
    player_id: str,
    room: str,
    action: str | None = None,
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="saw_player",
        payload={"player_id": player_id, "room": room, "action": action},
        provenance="observed",
    )


def _saw_player_move_event(
    *,
    tick: int,
    player_id: str,
    from_room: str,
    to_room: str,
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="saw_player_move",
        payload={
            "player_id": player_id,
            "from_room": from_room,
            "to_room": to_room,
        },
        provenance="observed",
    )


def _saw_body_event(
    *, tick: int, body_id: str, victim_id: str, room: str
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="saw_body",
        payload={"body_id": body_id, "victim_id": victim_id, "room": room},
        provenance="observed",
    )


def _build_memory_from_fixture(fixture: Mapping[str, Any]) -> AgentMemory:
    memory = AgentMemory()

    for raw_event in fixture["events"]:
        memory.episodic.append(
            EpisodicEvent(
                tick=int(raw_event["tick"]),
                type=str(raw_event["type"]),
                payload=dict(raw_event["payload"]),
                provenance=str(raw_event["provenance"]),
            )
        )

    for belief in fixture["beliefs"]:
        player_id = str(belief["player_id"])
        suspicion_delta = float(belief["suspicion"]) - 0.5
        trust_delta = float(belief["trust"]) - 0.5
        if suspicion_delta != 0.0:
            memory.beliefs.adjust_suspicion(player_id, delta=suspicion_delta)
        if trust_delta != 0.0:
            memory.beliefs.adjust_trust(player_id, delta=trust_delta)
        # A belief at neutral both ways still touches the store so
        # known_players() can list everyone the fixture mentions.
        if suspicion_delta == 0.0 and trust_delta == 0.0:
            memory.beliefs.adjust_suspicion(player_id, delta=0.0)

    for contradiction in fixture["contradictions"]:
        memory.beliefs.record_contradiction(
            str(contradiction["player_id"]),
            ContradictionRef(
                summary=str(contradiction["summary"]),
                left_ref=str(contradiction["left_ref"]),
                right_ref=str(contradiction["right_ref"]),
            ),
        )

    for last_seen in fixture["last_seen"]:
        memory.working.record_sighting(
            player_id=str(last_seen["player_id"]),
            room=str(last_seen["room"]),
            tick=int(last_seen["tick"]),
        )

    return memory


def _load_fixture(name: str) -> tuple[Mapping[str, Any], str]:
    fixture_path = _FIXTURE_DIR / f"{name}.json"
    expected_path = _FIXTURE_DIR / f"{name}.expected.md"
    fixture = cast(Mapping[str, Any], json.loads(fixture_path.read_text("utf-8")))
    expected = expected_path.read_text("utf-8")
    return fixture, expected


class TestGoldenFixtures:
    @pytest.mark.parametrize(
        "fixture_name",
        ["crewmate_basic", "tight_budget_drops_low_salience", "impostor_minimal"],
    )
    def test_render_matches_golden(self, fixture_name: str) -> None:
        fixture, expected = _load_fixture(fixture_name)
        memory = _build_memory_from_fixture(fixture)

        rendered = render_for_prompt(memory, token_budget=int(fixture["token_budget"]))

        assert rendered == expected, (
            f"\nFixture: {fixture_name}\n"
            f"---- expected ----\n{expected}"
            f"---- rendered ----\n{rendered}"
        )


class TestRequiredSections:
    def test_renders_role_line(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0, role="CREWMATE"))

        view = render_for_prompt(memory)

        assert view.startswith("## Your role: CREWMATE\n")

    def test_renders_tasks_summary_when_global_status_present(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.episodic.append(_global_status_event(tick=0, completed=3, total=10))

        view = render_for_prompt(memory)

        assert "## Tasks completed (global): 3 / 10" in view

    def test_omits_tasks_summary_when_no_global_status(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))

        view = render_for_prompt(memory)

        assert "Tasks completed" not in view


class TestSalienceOrdering:
    def test_higher_salience_events_render_before_lower(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.episodic.append(_global_status_event(tick=0, completed=0, total=12))
        memory.episodic.append(
            _saw_player_event(tick=100, player_id="p-3", room="ELECTRICAL", action=None)
        )
        memory.episodic.append(
            _saw_body_event(
                tick=101, body_id="body-p-2-101", victim_id="p-2", room="MEDBAY"
            )
        )

        view = render_for_prompt(memory)

        body_pos = view.index("You discovered p-2's body")
        sighting_pos = view.index("You saw p-3 in ELECTRICAL")
        assert body_pos < sighting_pos

    def test_within_same_salience_more_recent_tick_renders_first(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.episodic.append(
            _saw_player_event(tick=100, player_id="p-3", room="ADMIN", action=None)
        )
        memory.episodic.append(
            _saw_player_event(tick=200, player_id="p-4", room="STORAGE", action=None)
        )

        view = render_for_prompt(memory)

        newer_pos = view.index("[tick 200] You saw p-4 in STORAGE")
        older_pos = view.index("[tick 100] You saw p-3 in ADMIN")
        assert newer_pos < older_pos

    def test_within_same_salience_and_tick_lines_sort_alphabetically(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.episodic.append(
            _saw_player_event(tick=100, player_id="p-5", room="STORAGE", action=None)
        )
        memory.episodic.append(
            _saw_player_event(tick=100, player_id="p-3", room="ADMIN", action=None)
        )

        view = render_for_prompt(memory)

        p3_pos = view.index("p-3 in ADMIN")
        p5_pos = view.index("p-5 in STORAGE")
        assert p3_pos < p5_pos

    def test_render_is_deterministic_across_repeated_calls(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.episodic.append(_global_status_event(tick=0, completed=1, total=5))
        memory.episodic.append(
            _saw_player_event(tick=10, player_id="p-3", room="ADMIN", action="vent")
        )
        memory.episodic.append(
            _saw_body_event(
                tick=20, body_id="body-p-2-20", victim_id="p-2", room="MEDBAY"
            )
        )
        memory.beliefs.adjust_suspicion("p-3", delta=0.4)

        first = render_for_prompt(memory)
        second = render_for_prompt(memory)
        assert first == second


class TestTokenBudget:
    def test_drops_lowest_salience_when_budget_is_tight(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.episodic.append(_global_status_event(tick=0, completed=0, total=12))
        memory.episodic.append(
            _saw_player_event(tick=10, player_id="p-3", room="ADMIN", action=None)
        )
        memory.episodic.append(
            _saw_body_event(
                tick=20, body_id="body-p-2-20", victim_id="p-2", room="MEDBAY"
            )
        )

        # 60, not 40: the route block the self-location trail renders costs about
        # twenty tokens before any observation is spent.
        view = render_for_prompt(memory, token_budget=60)

        assert "You discovered p-2's body in MEDBAY" in view
        assert "You saw p-3 in ADMIN" not in view

    def test_generous_budget_includes_all_observations(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.episodic.append(_global_status_event(tick=0, completed=0, total=12))
        memory.episodic.append(
            _saw_player_event(tick=10, player_id="p-3", room="ADMIN", action=None)
        )
        memory.episodic.append(
            _saw_body_event(
                tick=20, body_id="body-p-2-20", victim_id="p-2", room="MEDBAY"
            )
        )

        view = render_for_prompt(memory, token_budget=DEFAULT_TOKEN_BUDGET)

        assert "You discovered p-2's body in MEDBAY" in view
        assert "You saw p-3 in ADMIN" in view

    def test_non_positive_budget_raises(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))

        with pytest.raises(ValueError, match="token_budget must be positive"):
            render_for_prompt(memory, token_budget=0)

        with pytest.raises(ValueError, match="token_budget must be positive"):
            render_for_prompt(memory, token_budget=-5)

    def test_observations_section_omitted_when_no_event_fits_budget(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.episodic.append(_global_status_event(tick=0, completed=0, total=12))
        memory.episodic.append(
            _saw_body_event(
                tick=20, body_id="body-p-2-20", victim_id="p-2", room="MEDBAY"
            )
        )

        view = render_for_prompt(memory, token_budget=15)

        assert "## Recent observations" not in view
        assert "## Your role: CREWMATE" in view


class TestBeliefsAndContradictions:
    def test_beliefs_section_shows_suspicion_for_high_suspicion_player(
        self,
    ) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.beliefs.adjust_suspicion("p-3", delta=0.25)

        view = render_for_prompt(memory)

        assert "- p-3: suspicion 0.75" in view

    def test_beliefs_section_shows_trust_when_trust_deviates_more(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.beliefs.adjust_trust("p-4", delta=0.3)

        view = render_for_prompt(memory)

        assert "- p-4: trust 0.80" in view

    def test_beliefs_section_omits_neutral_players(self) -> None:
        # A player known to the belief store but at neutral suspicion AND trust
        # (and with no recorded alibi) carries no signal and is omitted. Before
        # Task 13.5.2 this test seeded the known-but-neutral player with a dead
        # ``record_alibi`` call; that path now WIRES an alibi render (the
        # testimony-as-content lever), so the neutral player is seeded here by an
        # adjust-and-revert that leaves suspicion back at 0.5 without an alibi.
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.beliefs.adjust_suspicion("p-9", delta=0.2)
        memory.beliefs.adjust_suspicion("p-9", delta=-0.2)

        view = render_for_prompt(memory)

        assert "p-9" not in view

    def test_beliefs_section_is_sorted_by_player_id(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.beliefs.adjust_suspicion("p-5", delta=0.2)
        memory.beliefs.adjust_suspicion("p-3", delta=0.3)
        memory.beliefs.adjust_suspicion("p-7", delta=0.1)

        view = render_for_prompt(memory)

        p3 = view.index("p-3:")
        p5 = view.index("p-5:")
        p7 = view.index("p-7:")
        assert p3 < p5 < p7

    def test_contradictions_section_includes_summary(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.beliefs.record_contradiction(
            "p-4",
            ContradictionRef(
                summary="alibi conflict for p-4 around tick 405",
                left_ref="alibi:p-4@400-410",
                right_ref="sighting:p-6:p-4@405",
            ),
        )

        view = render_for_prompt(memory)

        assert "## Open contradictions:" in view
        assert "- alibi conflict for p-4 around tick 405" in view

    def test_contradictions_section_omitted_when_no_contradictions(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))

        view = render_for_prompt(memory)

        assert "Open contradictions" not in view

    def test_contradictions_are_deduplicated_across_players(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        contradiction = ContradictionRef(
            summary="conflict between p-3 and p-4",
            left_ref="alibi:p-3@100",
            right_ref="sighting:p-4@100",
        )
        memory.beliefs.record_contradiction("p-3", contradiction)
        memory.beliefs.record_contradiction("p-4", contradiction)

        view = render_for_prompt(memory)

        assert view.count("conflict between p-3 and p-4") == 1


class TestTeammatePerceptionFirewallRender:
    """Task 9.3 team-internal firewall, render side (DESIGN.md §4.7).

    Two render-time suppressions keyed off the latest ``self_state`` event:

    * a self-subject ``saw_player`` row (the recipient's own id) never renders
      into ANY player's prompt -- it would be third-person garble;
    * for an IMPOSTOR, a ``saw_player`` row that places a fellow impostor at a
      kill room/tick is dropped from the rendered meeting input (audit gp-7
      seed 47) -- benign teammate sightings are kept (kill-window only).

    Crewmate renders are byte-identical: ``fellow_impostor_ids`` is empty and
    the teammate guard is role-gated, while fixtures without ``agent_id`` never
    trip the self-subject guard.
    """

    def test_self_subject_saw_player_row_is_suppressed(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=0, role="CREWMATE", agent_id="p-1")
        )
        memory.episodic.append(
            _saw_player_event(tick=10, player_id="p-1", room="ADMIN", action=None)
        )
        memory.episodic.append(
            _saw_player_event(tick=10, player_id="p-2", room="ADMIN", action=None)
        )

        view = render_for_prompt(memory)

        assert "You saw p-1 in ADMIN" not in view
        assert "You saw p-2 in ADMIN" in view

    def test_self_subject_guard_is_role_independent(self) -> None:
        # The self-subject guard fires for an impostor too (it is not the
        # teammate guard): an impostor never sees itself in third person.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=0, role="IMPOSTOR", agent_id="p-9", fellow_impostor_ids=()
            )
        )
        memory.episodic.append(
            _saw_player_event(tick=10, player_id="p-9", room="STORAGE", action="kill")
        )

        view = render_for_prompt(memory)

        assert "You witnessed p-9 kill in STORAGE" not in view

    def test_impostor_teammate_kill_witness_row_is_suppressed(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=0, role="IMPOSTOR", agent_id="p-9", fellow_impostor_ids=("p-1",)
            )
        )
        # Directly witnessed teammate p-1 killing (action == "kill").
        memory.episodic.append(
            _saw_player_event(tick=7, player_id="p-1", room="ADMIN", action="kill")
        )
        # A non-teammate p-3 witnessed killing elsewhere -- retained.
        memory.episodic.append(
            _saw_player_event(tick=7, player_id="p-3", room="STORAGE", action="kill")
        )

        view = render_for_prompt(memory)

        assert "You witnessed p-1 kill in ADMIN" not in view
        assert "You witnessed p-3 kill in STORAGE" in view

    def test_impostor_teammate_at_body_scene_row_is_suppressed(self) -> None:
        # Body-proximity kill-window: teammate p-1 seen in a room where the
        # impostor then discovers a body within the proximity window.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=0, role="IMPOSTOR", agent_id="p-9", fellow_impostor_ids=("p-1",)
            )
        )
        memory.episodic.append(
            _saw_player_event(tick=7, player_id="p-1", room="ADMIN", action=None)
        )
        memory.episodic.append(
            _saw_body_event(tick=8, body_id="b", victim_id="p-3", room="ADMIN")
        )

        view = render_for_prompt(memory)

        assert "You saw p-1 in ADMIN" not in view
        # The body discovery itself still renders.
        assert "You discovered p-3's body in ADMIN" in view

    def test_impostor_benign_teammate_sighting_is_retained(self) -> None:
        # Kill-window only: a teammate sighting with no kill action and no nearby
        # body is benign coordination context and is NOT dropped.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=0, role="IMPOSTOR", agent_id="p-9", fellow_impostor_ids=("p-1",)
            )
        )
        memory.episodic.append(
            _saw_player_event(tick=2, player_id="p-1", room="CAFETERIA", action=None)
        )

        view = render_for_prompt(memory)

        assert "You saw p-1 in CAFETERIA" in view

    def test_role_flip_render_identical_except_teammate_suppressions(self) -> None:
        # DoD bullet 3: one 9p/2i-shaped fixture rendered as CREWMATE and as
        # IMPOSTOR-with-fellow-ids; the two renders are identical except the
        # role header and the teammate kill-window suppression.
        def _memory(*, role: str, fellow: tuple[str, ...] | None) -> AgentMemory:
            memory = AgentMemory()
            memory.episodic.append(
                _self_state_event(
                    tick=0, role=role, agent_id="p-9", fellow_impostor_ids=fellow
                )
            )
            memory.episodic.append(_global_status_event(tick=0, completed=2, total=14))
            # A benign sighting of a non-teammate, identical under both roles.
            memory.episodic.append(
                _saw_player_event(tick=5, player_id="p-2", room="STORAGE", action=None)
            )
            # p-1 is the (would-be) teammate, witnessed killing in ADMIN.
            memory.episodic.append(
                _saw_player_event(tick=7, player_id="p-1", room="ADMIN", action="kill")
            )
            memory.episodic.append(
                _saw_body_event(tick=8, body_id="b", victim_id="p-3", room="ADMIN")
            )
            return memory

        crew_view = render_for_prompt(_memory(role="CREWMATE", fellow=None))
        impostor_view = render_for_prompt(_memory(role="IMPOSTOR", fellow=("p-1",)))

        suppressed = "- [tick 7] You witnessed p-1 kill in ADMIN."
        assert suppressed in crew_view
        assert suppressed not in impostor_view

        crew_lines = crew_view.splitlines()
        impostor_lines = impostor_view.splitlines()
        assert crew_lines[0] == "## Your role: CREWMATE"
        assert impostor_lines[0] == "## Your role: IMPOSTOR"
        # Apart from the role header (index 0) and the single suppressed teammate
        # row, the two renders are byte-identical.
        crew_rest = [
            line
            for index, line in enumerate(crew_lines)
            if index != 0 and line != suppressed
        ]
        impostor_rest = [
            line for index, line in enumerate(impostor_lines) if index != 0
        ]
        assert crew_rest == impostor_rest


class TestR6CompositeMemoryReadsAllThreeStores:
    """R-6 acceptance gate: render_for_prompt reads from episodic +
    working + beliefs, not from any one in isolation."""

    def test_render_uses_episodic_for_role_and_tasks(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=5, role="CREWMATE"))
        memory.episodic.append(_global_status_event(tick=5, completed=4, total=10))

        view = render_for_prompt(memory)

        assert "## Your role: CREWMATE" in view
        assert "## Tasks completed (global): 4 / 10" in view

    def test_render_uses_beliefs_for_suspicion_and_contradictions(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.beliefs.adjust_suspicion("p-3", delta=0.4)
        memory.beliefs.record_contradiction(
            "p-3",
            ContradictionRef(
                summary="p-3 alibi gap",
                left_ref="alibi:p-3",
                right_ref="sighting:p-5:p-3",
            ),
        )

        view = render_for_prompt(memory)

        assert "## Your current beliefs:" in view
        assert "- p-3: suspicion 0.90" in view
        assert "## Open contradictions:" in view
        assert "- p-3 alibi gap" in view

    def test_render_uses_working_memory_for_last_seen_enrichment(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.beliefs.adjust_suspicion("p-3", delta=0.2)
        memory.working.record_sighting(player_id="p-3", room="REACTOR", tick=42)

        view = render_for_prompt(memory)

        assert "- p-3: suspicion 0.70 (last seen in REACTOR at tick 42)" in view

    def test_render_combines_all_three_components_in_one_view(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=10, role="CREWMATE"))
        memory.episodic.append(_global_status_event(tick=10, completed=2, total=12))
        memory.episodic.append(
            _saw_body_event(
                tick=20, body_id="body-p-2-20", victim_id="p-2", room="MEDBAY"
            )
        )
        memory.beliefs.adjust_suspicion("p-3", delta=0.3)
        memory.working.record_sighting(player_id="p-3", room="ELECTRICAL", tick=15)

        view = render_for_prompt(memory)

        # Episodic-derived
        assert "## Your role: CREWMATE" in view
        assert "## Tasks completed (global): 2 / 12" in view
        assert "[tick 20] You discovered p-2's body" in view
        # Belief-derived
        assert "- p-3: suspicion 0.80" in view
        # Working-memory enrichment threaded into the belief line
        assert "(last seen in ELECTRICAL at tick 15)" in view


class TestR10LeakScannerReuse:
    """R-10 acceptance gate: the canonical packet scanners are reused
    against render_for_prompt output."""

    def test_render_passes_canonical_leak_scanners(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0, role="CREWMATE"))
        memory.episodic.append(_global_status_event(tick=0, completed=2, total=12))
        memory.episodic.append(
            _saw_player_event(
                tick=10, player_id="p-3", room="ELECTRICAL", action="vent"
            )
        )
        memory.episodic.append(
            _saw_body_event(
                tick=20, body_id="body-p-2-20", victim_id="p-2", room="MEDBAY"
            )
        )
        memory.beliefs.adjust_suspicion("p-3", delta=0.4)
        memory.beliefs.record_contradiction(
            "p-3",
            ContradictionRef(
                summary="alibi conflict around tick 18",
                left_ref="alibi:p-3@10-20",
                right_ref="sighting:p-4:p-3@18",
            ),
        )

        view = render_for_prompt(memory)

        _scan_rendered_view(view)

    def test_role_bearing_value_scanner_trips_on_planted_player_id(self) -> None:
        """Planted negative test mirroring ``eval/leak_test.py:222``.

        Inject a forbidden role-bearing substring ("crewmate") into a
        ``saw_player`` payload's player_id. When the renderer surfaces
        it inside the observations section, the canonical value scanner
        must trip — proving the rendered surface is covered by the
        same anti-leak invariants as ObservationPackets (R-10).
        """

        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0, role="CREWMATE"))
        memory.episodic.append(
            _saw_player_event(
                tick=10,
                player_id="crew_role_leak_fixture",
                room="STORAGE",
                action=None,
            )
        )

        view = render_for_prompt(memory)

        # Sanity check: the planted string actually surfaced in the
        # observations section so the scanner has something to catch.
        assert "crew_role_leak_fixture" in view

        with pytest.raises(AssertionError, match="rendered_body"):
            _scan_rendered_view(view)

    def test_role_bearing_value_scanner_trips_on_planted_contradiction(
        self,
    ) -> None:
        """Second planted negative test for the contradictions section."""

        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0, role="CREWMATE"))
        memory.beliefs.record_contradiction(
            "p-4",
            ContradictionRef(
                summary="impostor sighting near MEDBAY",
                left_ref="alibi:p-4",
                right_ref="sighting:p-5:p-4",
            ),
        )

        view = render_for_prompt(memory)

        assert "impostor sighting near MEDBAY" in view

        with pytest.raises(AssertionError, match="rendered_body"):
            _scan_rendered_view(view)

    def test_role_bearing_value_scanner_allows_self_state_role(self) -> None:
        """The legitimate ``## Your role: CREWMATE`` line does not trip
        the scanner because it maps to the canonical allowed path."""

        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0, role="CREWMATE"))

        view = render_for_prompt(memory)

        # Should not raise.
        _scan_rendered_view(view)


class TestErrorHandling:
    def test_missing_self_state_raises(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_global_status_event(tick=0, completed=0, total=12))

        with pytest.raises(ValueError, match="no self_state event"):
            render_for_prompt(memory)

    def test_completely_empty_memory_raises(self) -> None:
        memory = AgentMemory()

        with pytest.raises(ValueError, match="no self_state event"):
            render_for_prompt(memory)


class TestCompletedTaskFromEvents:
    """The completed-task line, read off ``owned_task_ids``.

    A living agent's owned set loses a map id only when that instance completes;
    redistribution only ADDS one. Unconditional since the baseline-7 record.
    """

    def test_the_rule_is_unconditional(self) -> None:
        for env in ({}, {ENV_TASK_COMPLETION_FROM_EVENTS: "0"}, None):
            assert task_completion_from_events_enabled(env) is True

    def test_redistributed_task_displacing_pending_mints_no_completion(self) -> None:
        # The confirmed defect's shape: a crewmate holding ``upload_logs`` inherits
        # a victim's ``align_engine_output``, which sorts first and takes over
        # ``pending_task_id`` -- while ``upload_logs`` is still owned and unfinished.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=12,
                room="MEDBAY",
                pending_task_id="upload_logs",
                owned_task_ids=("upload_logs",),
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=13,
                room="MEDBAY",
                pending_task_id="align_engine_output",
                owned_task_ids=("align_engine_output", "upload_logs"),
            )
        )

        view = render_for_prompt(memory)

        assert "You completed" not in view
        # The gate bites: drop the owned set from the second row and the render
        # has no evidence either way, so the line the retired pending-id rule
        # fabricated cannot come back through a fixture that merely omits it.
        assert "You completed" not in render_for_prompt(memory)

    def test_a_genuine_rollover_dates_and_rooms_the_completion(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=100,
                room="ADMIN",
                pending_task_id="swipe_card",
                owned_task_ids=("submit_scan", "swipe_card"),
                observation_id="p-1:100:0",
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=130,
                room="MEDBAY",
                pending_task_id="submit_scan",
                owned_task_ids=("submit_scan",),
                observation_id="p-1:130:0",
            )
        )

        view = render_for_prompt(memory)

        # The room is the one on the row that DATES the completion (tick 130,
        # MEDBAY) -- the self-location trail's rule, which the retired
        # roll-forward rendered as ADMIN.
        assert (
            "[obs p-1:130:0] [tick 130] You completed swipe_card (you were in MEDBAY)."
            in view
        )
        assert "You completed submit_scan" not in view

    def test_final_clear_renders_the_completion(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=100,
                room="ADMIN",
                pending_task_id="swipe_card",
                owned_task_ids=("swipe_card",),
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=160,
                room="MEDBAY",
                pending_task_id=None,
                owned_task_ids=(),
            )
        )

        view = render_for_prompt(memory)

        assert "[tick 160] You completed swipe_card (you were in MEDBAY)." in view

    def test_completion_behind_an_inherited_task_renders(self) -> None:
        # The agent finishes ``upload_logs`` on a tick when ``pending_task_id`` is
        # already held by the inherited earlier-sorting ``align_engine_output``, so
        # nothing about the pending id changes -- and the owned set still says so.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=12,
                room="MEDBAY",
                pending_task_id="upload_logs",
                owned_task_ids=("upload_logs",),
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=13,
                room="MEDBAY",
                pending_task_id="align_engine_output",
                owned_task_ids=("align_engine_output", "upload_logs"),
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=14,
                room="STORAGE",
                pending_task_id="align_engine_output",
                owned_task_ids=("align_engine_output",),
            )
        )

        view = render_for_prompt(memory)

        assert "[tick 14] You completed upload_logs (you were in STORAGE)." in view
        # Reported once, on the tick the id actually LEFT the owned set -- never
        # on tick 13, where it was merely displaced from ``pending_task_id``.
        assert "[tick 13] You completed" not in view

    def test_impostor_pretend_rotation_mints_no_completion(self) -> None:
        # The impostor's ``owned_task_ids`` is a CONSTANT per-seat camouflage
        # window while ``pending_task_id`` rotates through it, so the rule mints
        # nothing for an impostor without any role gate.
        window = ("fuel_reserves", "submit_scan", "swipe_card")
        memory = AgentMemory()
        for tick, pretend in (
            (10, "swipe_card"),
            (20, "submit_scan"),
            (30, "fuel_reserves"),
        ):
            memory.episodic.append(
                _self_state_event(
                    tick=tick,
                    role="IMPOSTOR",
                    room="ELECTRICAL",
                    pending_task_id=pretend,
                    owned_task_ids=window,
                )
            )

        assert "You completed" not in render_for_prompt(memory)

    def test_a_shrinking_impostor_window_would_mint(self) -> None:
        # The perturbation that proves the test above is not vacuous: the ON rule
        # is role-BLIND -- it reads the set, and the impostor is protected only by
        # that set being constant.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=10,
                role="IMPOSTOR",
                room="ELECTRICAL",
                pending_task_id="swipe_card",
                owned_task_ids=("submit_scan", "swipe_card"),
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=20,
                role="IMPOSTOR",
                room="ELECTRICAL",
                pending_task_id="submit_scan",
                owned_task_ids=("submit_scan",),
            )
        )

        view = render_for_prompt(memory)

        assert "[tick 20] You completed swipe_card (you were in ELECTRICAL)." in view

    def test_two_departed_ids_render_one_line_each(self) -> None:
        # Both completions are reported, in a fixed (sorted) order.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=40,
                room="LABS",
                pending_task_id="fuel_reserves",
                owned_task_ids=("fuel_reserves", "swipe_card"),
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=41,
                room="LABS",
                pending_task_id=None,
                owned_task_ids=(),
            )
        )

        view = render_for_prompt(memory, token_budget=8000)

        assert "[tick 41] You completed fuel_reserves (you were in LABS)." in view
        assert "[tick 41] You completed swipe_card (you were in LABS)." in view
        assert view.index("You completed fuel_reserves") < view.index(
            "You completed swipe_card"
        )

    def test_rows_without_the_owned_set_mint_nothing(self) -> None:
        # Fail-closed: a pre-widening recording or a hand-built fixture carries no
        # set, so the rule has no evidence and mints nothing -- a cleared pending
        # id is not, on its own, a completion.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=100, room="ADMIN", pending_task_id="swipe_card")
        )
        memory.episodic.append(
            _self_state_event(tick=130, room="MEDBAY", pending_task_id=None)
        )

        assert "You completed" not in render_for_prompt(memory)

    def test_one_row_without_the_owned_set_mints_nothing(self) -> None:
        # The set has to be readable on BOTH rows: a gap in the evidence is not a
        # completion.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=100,
                room="ADMIN",
                pending_task_id="swipe_card",
                owned_task_ids=("swipe_card",),
            )
        )
        memory.episodic.append(
            _self_state_event(tick=130, room="MEDBAY", pending_task_id=None)
        )
        memory.episodic.append(
            _self_state_event(
                tick=160,
                room="MEDBAY",
                pending_task_id=None,
                owned_task_ids=(),
            )
        )

        assert "You completed" not in render_for_prompt(memory)

    def test_unchanged_owned_set_mints_nothing(self) -> None:
        memory = AgentMemory()
        for tick in (100, 130, 160):
            memory.episodic.append(
                _self_state_event(
                    tick=tick,
                    room="ADMIN",
                    pending_task_id="swipe_card",
                    owned_task_ids=("submit_scan", "swipe_card"),
                )
            )

        assert "You completed" not in render_for_prompt(memory)


class TestSawBodyDeduplication:
    def test_repeated_saw_body_events_render_once(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        for tick in (20, 21, 22, 23):
            memory.episodic.append(
                _saw_body_event(
                    tick=tick,
                    body_id="body-p-2-20",
                    victim_id="p-2",
                    room="MEDBAY",
                )
            )

        view = render_for_prompt(memory)

        assert view.count("You discovered p-2's body in MEDBAY") == 1

    def test_malformed_saw_body_does_not_suppress_later_valid_event(self) -> None:
        """An early ``saw_body`` event with missing/invalid victim or
        room is silently skipped today, but it must not poison the
        dedup set for the same ``body_id``: a later well-formed event
        for that body must still render the discovery.
        """

        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        # First event for body-p-2-20 is malformed (no victim_id).
        memory.episodic.append(
            EpisodicEvent(
                tick=10,
                type="saw_body",
                payload={"body_id": "body-p-2-20", "room": "MEDBAY"},
                provenance="observed",
            )
        )
        # Second event for the same body_id is well-formed.
        memory.episodic.append(
            _saw_body_event(
                tick=20,
                body_id="body-p-2-20",
                victim_id="p-2",
                room="MEDBAY",
            )
        )

        view = render_for_prompt(memory)

        assert "[tick 20] You discovered p-2's body in MEDBAY." in view


class TestLastSeenOnConfirmedDead:
    """L-2 coverage pin (audits/audit-2026-05-16-2239-claude.md §L-2).

    A player whose body has been discovered (``saw_body``) remains
    confirmed-dead, but the agent's ``working.last_seen`` record for
    that player still carries useful timing information (where and
    when the agent last saw them alive). The renderer must surface
    that ``(last seen in ROOM at tick N)`` suffix on the dead player's
    belief line. A future refactor that silently strips ``last_seen``
    for confirmed-dead players would fail this regression.
    """

    def test_last_seen_suffix_renders_for_confirmed_dead_player(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        # Record a sighting of p-2 alive at tick 10 in MEDBAY...
        memory.episodic.append(
            _saw_player_event(tick=10, player_id="p-2", room="MEDBAY", action=None)
        )
        memory.working.record_sighting(player_id="p-2", room="MEDBAY", tick=10)
        # ...then the body discovery at tick 15.
        memory.episodic.append(
            _saw_body_event(
                tick=15, body_id="body-p-2-15", victim_id="p-2", room="MEDBAY"
            )
        )
        # Drive p-2's suspicion off-neutral so the belief line is rendered
        # (the renderer omits neutral beliefs).
        memory.beliefs.adjust_suspicion("p-2", delta=0.4)

        rendered = render_for_prompt(memory, token_budget=8000)

        assert "(last seen in MEDBAY at tick 10)" in rendered
        assert "p-2: suspicion 0.90 (last seen in MEDBAY at tick 10)" in rendered
        # And the body discovery itself is rendered too, so the agent
        # and the reader both see "confirmed dead, last seen here at
        # tick N" together.
        assert "You discovered p-2's body in MEDBAY" in rendered


class TestSalienceCutoffStrictness:
    def test_lower_salience_event_dropped_when_higher_event_does_not_fit(
        self,
    ) -> None:
        """If the highest-salience event does not fit the budget, every
        lower-salience event past that cutoff must also be dropped.
        Otherwise a low-salience sighting could displace a high-salience
        body discovery -- the exact perverse outcome
        "drop by lowest salience first" forbids (DESIGN.md §6.6).
        """

        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.episodic.append(_global_status_event(tick=0, completed=0, total=12))
        # Short low-salience sighting that would individually fit a tight budget.
        memory.episodic.append(
            _saw_player_event(tick=100, player_id="x", room="A", action=None)
        )
        # Long high-salience body line (room name padded to force a large cost).
        memory.episodic.append(
            _saw_body_event(
                tick=200,
                body_id="body-p-1-200",
                victim_id="p-1",
                room="VERY_LONG_ROOM_NAME_FOR_BUDGET_CUTOFF_TEST",
            )
        )

        view = render_for_prompt(memory, token_budget=35)

        assert "You discovered p-1's body" not in view
        assert "You saw x in A" not in view
        assert "## Recent observations" not in view


class TestTokenBudgetIsHardCap:
    """Regression for the 'token-budgeted view' contract: the rendered
    string's estimated tokens must not exceed ``token_budget`` (modulo
    the non-elastic role/tasks/beliefs/contradictions sections, which
    are always retained because they are agent-essential context).
    Verifies the Markdown separators (``\\n\\n`` between blocks and the
    trailing ``\\n``) are all charged against the budget."""

    @staticmethod
    def _estimate_tokens_of(text: str) -> int:
        # Mirror agents.memory.store._estimate_tokens so the test
        # asserts against the same arithmetic the renderer uses.
        if not text:
            return 0
        return (len(text) + 3) // 4

    @pytest.mark.parametrize("budget", [40, 50, 75, 100, 200, 500])
    def test_rendered_view_does_not_exceed_budget(self, budget: int) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.episodic.append(_global_status_event(tick=0, completed=2, total=12))
        for i in range(20):
            memory.episodic.append(
                _saw_player_event(
                    tick=10 + i, player_id=f"p-{i}", room="ADMIN", action=None
                )
            )

        view = render_for_prompt(memory, token_budget=budget)

        actual = self._estimate_tokens_of(view)
        assert actual <= budget, (
            f"budget {budget}: rendered view's estimated token count is "
            f"{actual} (text len {len(view)}). View:\n{view}"
        )

    def test_separators_between_observations_block_and_beliefs_are_charged(
        self,
    ) -> None:
        """With both an observations block and a beliefs block present,
        the ``\\n\\n`` separator between them is part of the rendered
        output. If the budget arithmetic ignored it, the rendered token
        count could exceed the budget at the boundary."""

        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.episodic.append(_global_status_event(tick=0, completed=0, total=12))
        memory.beliefs.adjust_suspicion("p-3", delta=0.4)
        # Twelve sightings of varying tick give the renderer something
        # to thin against the budget.
        for i in range(12):
            memory.episodic.append(
                _saw_player_event(
                    tick=20 + i, player_id=f"p-{i}", room="ADMIN", action=None
                )
            )

        for budget in (60, 80, 120, 200):
            view = render_for_prompt(memory, token_budget=budget)
            assert self._estimate_tokens_of(view) <= budget


class TestBeliefNeutralityEpsilon:
    def test_near_neutral_belief_after_decay_is_omitted(self) -> None:
        """Beliefs that drift to a value rounding to 0.50 carry no
        signal -- the rendered "suspicion 0.50" line just bloats the
        prompt. With an exact-equality neutral filter, repeated decay
        toward 0.5 from a non-neutral starting point can leave float
        residue and surface a meaningless line; the epsilon-based
        filter omits it.
        """

        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        # Push suspicion off neutral, then decay back toward 0.5 many
        # times. With rate < 1 and a non-power-of-two arithmetic, the
        # value asymptotes to 0.5 but never lands exactly on it.
        memory.beliefs.adjust_suspicion("p-3", delta=0.3)
        for _ in range(200):
            memory.beliefs.decay_suspicion("p-3", toward=0.5, rate=0.3)

        suspicion = memory.beliefs.view("p-3").suspicion
        # Sanity: the value is *displayed* as 0.50 but is not exactly 0.5.
        assert f"{suspicion:.2f}" == "0.50"

        view = render_for_prompt(memory)

        assert "p-3" not in view
        assert "## Your current beliefs" not in view


class TestMovementPerceptionRender:
    """Render side of Task 13.5.4 — perceived room transitions + last_seen.

    A ``saw_player_move`` row renders as a first-hand sighting-class line and,
    via the render-time ``record_sighting`` wiring, populates ``last_seen`` so the
    §6.6 belief-line suffix finally appears. These tests inject the rows directly
    to exercise the render path independent of the observation layer (which
    derives them unconditionally since Task 14.9).
    """

    def test_witnessed_move_renders_first_hand_line(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0, agent_id="p-1"))
        memory.episodic.append(
            _saw_player_move_event(
                tick=5, player_id="p-3", from_room="CAFETERIA", to_room="ADMIN"
            )
        )

        view = render_for_prompt(memory)

        assert "[tick 5] You saw p-3 move from CAFETERIA to ADMIN." in view

    def test_witnessed_move_wires_last_seen_suffix_on_belief_line(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0, agent_id="p-1"))
        # A belief on p-3 so the belief row renders, then the witnessed move that
        # wires the "last seen" suffix onto it.
        memory.beliefs.adjust_suspicion("p-3", delta=0.3)
        memory.episodic.append(
            _saw_player_move_event(
                tick=8, player_id="p-3", from_room="CAFETERIA", to_room="ADMIN"
            )
        )

        view = render_for_prompt(memory)

        assert memory.working.last_seen("p-3") is not None
        assert "last seen in ADMIN at tick 8" in view

    def test_last_seen_takes_most_recent_transition(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0, agent_id="p-1"))
        memory.beliefs.adjust_suspicion("p-3", delta=0.3)
        memory.episodic.append(
            _saw_player_move_event(
                tick=4, player_id="p-3", from_room="CAFETERIA", to_room="ADMIN"
            )
        )
        memory.episodic.append(
            _saw_player_move_event(
                tick=9, player_id="p-3", from_room="ADMIN", to_room="STORAGE"
            )
        )

        view = render_for_prompt(memory)

        last_seen = memory.working.last_seen("p-3")
        assert last_seen is not None
        assert (last_seen.room, last_seen.tick) == ("STORAGE", 9)
        assert "last seen in STORAGE at tick 9" in view
        assert "last seen in ADMIN at tick 4" not in view

    def test_repeated_render_is_idempotent_after_two_moves(self) -> None:
        # Codex P1: render is called repeatedly (meeting turns, vote prompts, the
        # 13.5.5 per-turn re-render). With two transitions for one player, a second
        # render must not trip ``record_sighting``'s non-decreasing-tick guard on
        # the replayed OLDER row -- it stays the latest-per-subject value.
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0, agent_id="p-1"))
        memory.beliefs.adjust_suspicion("p-3", delta=0.3)
        memory.episodic.append(
            _saw_player_move_event(
                tick=4, player_id="p-3", from_room="CAFETERIA", to_room="ADMIN"
            )
        )
        memory.episodic.append(
            _saw_player_move_event(
                tick=9, player_id="p-3", from_room="ADMIN", to_room="STORAGE"
            )
        )

        first = render_for_prompt(memory)
        second = render_for_prompt(memory)  # must not raise on the replayed tick-4

        assert first == second
        assert "last seen in STORAGE at tick 9" in second

    def test_teammate_move_into_kill_window_room_is_suppressed(self) -> None:
        # §4.7 firewall (Codex P2): an impostor that witnessed a TEAMMATE move into
        # a room where it also saw a fresh body must NOT surface that as a last-seen
        # suffix (nor a movement line) -- the teammate-at-scene own-goal the
        # sighting render already suppresses. last_seen must be suppressed too.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=0, role="IMPOSTOR", agent_id="p-9", fellow_impostor_ids=("p-1",)
            )
        )
        memory.beliefs.adjust_suspicion("p-1", delta=0.3)  # a belief row exists
        memory.episodic.append(
            _saw_player_move_event(
                tick=8, player_id="p-1", from_room="CAFETERIA", to_room="ADMIN"
            )
        )
        memory.episodic.append(
            _saw_body_event(tick=8, body_id="b", victim_id="p-3", room="ADMIN")
        )

        view = render_for_prompt(memory)

        assert memory.working.last_seen("p-1") is None  # suppressed, not wired
        assert "last seen in ADMIN" not in view
        assert "You saw p-1 move" not in view  # the movement line is suppressed too

    def test_movement_line_outranks_reconstructed_transition_salience(self) -> None:
        # A directly-witnessed transit is first-hand class and ranks above a bare
        # ``saw_player`` snapshot: under a tight budget the move survives and the
        # plain sighting is shed.
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0, agent_id="p-1"))
        memory.episodic.append(
            _saw_player_event(tick=10, player_id="p-9", room="MEDBAY", action=None)
        )
        memory.episodic.append(
            _saw_player_move_event(
                tick=10, player_id="p-3", from_room="CAFETERIA", to_room="ADMIN"
            )
        )

        # Budget for exactly one observation line.
        for budget in (40, 55, 70):
            view = render_for_prompt(memory, token_budget=budget)
            if "You saw p-3 move from CAFETERIA to ADMIN." in view:
                if "You saw p-9 in MEDBAY" not in view:
                    break
        else:  # pragma: no cover - defensive
            raise AssertionError(
                "no budget isolated the movement line above the snapshot"
            )

    def test_self_subject_move_row_is_suppressed(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0, agent_id="p-1"))
        memory.episodic.append(
            _saw_player_move_event(
                tick=5, player_id="p-1", from_room="CAFETERIA", to_room="ADMIN"
            )
        )

        view = render_for_prompt(memory)

        assert "You saw p-1 move" not in view
        assert memory.working.last_seen("p-1") is None

    def test_render_without_movement_rows_carries_no_movement_artifacts(self) -> None:
        # A store with no ``saw_player_move`` row (the observer witnessed no
        # transition) renders with no movement line and no last_seen suffix --
        # the artifacts come only from witnessed-movement rows.
        baseline = AgentMemory()
        baseline.episodic.append(_self_state_event(tick=0, agent_id="p-1"))
        baseline.beliefs.adjust_suspicion("p-3", delta=0.3)
        baseline_view = render_for_prompt(baseline)

        assert "move from" not in baseline_view
        assert "last seen in" not in baseline_view

    def test_render_is_deterministic_across_repeated_calls(self) -> None:
        # The render-time ``record_sighting`` writer is idempotent: re-rendering
        # replays the same rows in non-decreasing tick order without error and
        # yields a byte-identical view.
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0, agent_id="p-1"))
        memory.beliefs.adjust_suspicion("p-3", delta=0.3)
        memory.episodic.append(
            _saw_player_move_event(
                tick=6, player_id="p-3", from_room="CAFETERIA", to_room="ADMIN"
            )
        )

        first = render_for_prompt(memory)
        second = render_for_prompt(memory)

        assert first == second

    def test_rendered_movement_view_is_leak_clean(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0, agent_id="p-1"))
        memory.beliefs.adjust_suspicion("p-3", delta=0.3)
        memory.episodic.append(
            _saw_player_move_event(
                tick=5, player_id="p-3", from_room="CAFETERIA", to_room="ADMIN"
            )
        )

        view = render_for_prompt(memory)

        _scan_rendered_view(view)


# --------------------------------------------------------------------------- #
# The self-location trail (AILIBI_SELF_LOCATION_TRAIL, default-OFF).           #
# --------------------------------------------------------------------------- #

_TRAIL_ON: Mapping[str, str] = {ENV_SELF_LOCATION_TRAIL: "1"}
_TRAIL_HEADER = "## Where you were:"
_TRAIL_TRUNCATED = "- Earlier parts of your route are not listed."
_TRAIL_ROUTE_PREFIX = "- Your route (t = tick): "
_TRAIL_GAP_STEP = "(no record)"
_OBS_ID_IN_VIEW = re.compile(r"\[obs ([^\]]+)\]")


def _meeting_boundary_event(*, tick: int) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="meeting_boundary",
        payload={},
        provenance="inferred",
    )


def _trail_steps(view: str) -> list[tuple[int, int, str]]:
    """The rendered route parsed back into ``(start, end, where)`` steps.

    Reading the line the way a model would -- split the chain, then read each
    step's place and tick range -- is what makes the assertions below check the
    route's SEMANTICS rather than one formatting string. ``(no record)`` steps
    claim nothing and are dropped here.
    """

    steps: list[tuple[int, int, str]] = []
    for line in view.splitlines():
        if not line.startswith(_TRAIL_ROUTE_PREFIX):
            continue
        for step in line[len(_TRAIL_ROUTE_PREFIX) :].split(" -> "):
            if step == _TRAIL_GAP_STEP:
                continue
            where, _, ticks = step.rpartition(" ")
            assert ticks.startswith("t"), f"unreadable route step {step!r}"
            start, _, end = ticks[1:].partition("-")
            steps.append((int(start), int(end or start), where))
    return steps


def _trail_ticks(view: str) -> list[int]:
    """Every tick the rendered trail claims, oldest first."""

    return [
        tick for start, end, _ in _trail_steps(view) for tick in range(start, end + 1)
    ]


def _trail_block(view: str) -> list[str]:
    lines = view.splitlines()
    start = lines.index(_TRAIL_HEADER)
    end = start + 1
    while end < len(lines) and lines[end].startswith("- "):
        end += 1
    return lines[start:end]


def _walk(*rows: tuple[int, str]) -> AgentMemory:
    """A memory holding one ``self_state`` row per (tick, room) pair."""

    memory = AgentMemory()
    for tick, room in rows:
        memory.episodic.append(_self_state_event(tick=tick, room=room, agent_id="p-1"))
    return memory


class TestSelfLocationTrail:
    """The agent's own route, rendered from its own record.

    Unconditional since the baseline-7 record.
    """

    def test_the_trail_is_unconditional(self) -> None:
        for env in ({}, {ENV_SELF_LOCATION_TRAIL: "0"}, None):
            assert self_location_trail_enabled(env) is True

    def test_the_golden_comparison_bites(self) -> None:
        # The perturbation craft rule 2 asks for: one altered byte in the
        # expectation must fail the comparison the golden tests make.
        fixture, expected = _load_fixture("crewmate_basic")
        memory = _build_memory_from_fixture(fixture)
        perturbed = expected.replace("## Your role:", "## Your ROLE:", 1)

        assert perturbed != expected
        assert (
            render_for_prompt(memory, token_budget=int(fixture["token_budget"]))
            != perturbed
        )

    def test_render_matches_the_trail_golden(self) -> None:
        fixture, expected = _load_fixture("self_location_trail")
        memory = _build_memory_from_fixture(fixture)

        rendered = render_for_prompt(memory, token_budget=int(fixture["token_budget"]))

        assert rendered == expected, (
            f"---- expected ----\n{expected}---- rendered ----\n{rendered}"
        )
        # The gate bites: drop the row that DATES the completion and both the
        # route and the completion line move, so the golden is a real comparison
        # rather than a snapshot of whatever the renderer happens to emit.
        thinned = _build_memory_from_fixture(
            {
                **fixture,
                "events": [
                    event
                    for event in fixture["events"]
                    if not (event["tick"] == 9 and event["type"] == "self_state")
                ],
            }
        )
        assert (
            render_for_prompt(thinned, token_budget=int(fixture["token_budget"]))
            != expected
        )

    def test_adjacent_ticks_in_one_room_coalesce_and_a_lone_tick_stands_alone(
        self,
    ) -> None:
        memory = _walk((12, "REACTOR"), (13, "REACTOR"), (14, "REACTOR"), (17, "ADMIN"))

        view = render_for_prompt(memory)

        assert _trail_block(view) == [
            _TRAIL_HEADER,
            "- Your route (t = tick): REACTOR t12-14 -> (no record) -> ADMIN t17",
        ]
        assert _trail_steps(view) == [(12, 14, "REACTOR"), (17, 17, "ADMIN")]

    def test_a_gap_in_the_record_breaks_a_span(self) -> None:
        # Tick 14 was never recorded, so the trail may not claim it: two steps
        # with the gap stated between them, not one 13-15 range across a tick the
        # agent has no row for.
        memory = _walk((13, "REACTOR"), (15, "REACTOR"))

        view = render_for_prompt(memory)

        assert _trail_block(view) == [
            _TRAIL_HEADER,
            "- Your route (t = tick): REACTOR t13 -> (no record) -> REACTOR t15",
        ]
        assert 14 not in _trail_ticks(view)

    def test_a_meeting_boundary_does_not_break_a_span(self) -> None:
        # A meeting freezes movement (DESIGN.md §5.1), so the resume tick's room
        # continues the pre-meeting span -- the one place this walk deliberately
        # differs from the OTHERS-sighting transition walk, which must break here.
        memory = _walk((13, "REACTOR"), (14, "REACTOR"))
        memory.episodic.append(_meeting_boundary_event(tick=14))

        view = render_for_prompt(memory)

        assert _trail_block(view) == [
            _TRAIL_HEADER,
            "- Your route (t = tick): REACTOR t13-14",
        ]
        assert "p-" not in _trail_block(view)[1]

    def test_the_block_sits_between_the_fixed_lines_and_the_observations(self) -> None:
        memory = _walk((4, "REACTOR"))
        memory.episodic.append(_global_status_event(tick=4, completed=1, total=9))
        memory.episodic.append(
            _saw_player_event(tick=4, player_id="p-3", room="REACTOR", action=None)
        )

        view = render_for_prompt(memory)

        assert view.startswith("## Your role: CREWMATE\n")
        assert view.index("## Tasks completed") < view.index(_TRAIL_HEADER)
        assert view.index(_TRAIL_HEADER) < view.index("## Recent observations")

    def test_the_trail_renders_for_every_role_and_marks_vent_ticks(self) -> None:
        def _memory(role: str) -> AgentMemory:
            memory = AgentMemory()
            memory.episodic.append(
                _self_state_event(tick=6, role=role, room="ELECTRICAL", agent_id="p-1")
            )
            memory.episodic.append(
                _self_state_event(
                    tick=7,
                    role=role,
                    room="ELECTRICAL",
                    agent_id="p-1",
                    in_vent=True,
                )
            )
            return memory

        crew = render_for_prompt(_memory("CREWMATE"))
        impostor = render_for_prompt(_memory("IMPOSTOR"))

        for view in (crew, impostor):
            # Entering the vent breaks the span: the two ticks are not the same
            # placement, and an in-vent step says so inline rather than reading as
            # an ordinary room stay.
            assert _trail_block(view) == [
                _TRAIL_HEADER,
                "- Your route (t = tick): ELECTRICAL t6 -> a vent in ELECTRICAL t7",
            ]
            assert _trail_steps(view) == [
                (6, 6, "ELECTRICAL"),
                (7, 7, "a vent in ELECTRICAL"),
            ]

    def test_trail_lines_carry_no_ids_and_every_rendered_id_is_the_store_s(
        self,
    ) -> None:
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=3, room="ADMIN", agent_id="p-1", observation_id="p-1:3:0"
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=4, room="MEDBAY", agent_id="p-1", observation_id="p-1:4:0"
            )
        )
        memory.episodic.append(
            EpisodicEvent(
                tick=4,
                type="saw_player",
                payload={"player_id": "p-3", "room": "MEDBAY", "action": None},
                provenance="observed",
                observation_id="p-1:4:1",
            )
        )

        view = render_for_prompt(memory)

        own_ids = {
            event.observation_id
            for event in memory.episodic.recent(since_tick=0)
            if event.observation_id is not None
        }
        rendered_ids = set(_OBS_ID_IN_VIEW.findall(view))
        # The same set ``meetings.manager._normalize_ballot_observation_id``
        # validates a ballot citation against: nothing rendered may fall outside it.
        assert rendered_ids and rendered_ids <= own_ids
        assert all("[obs " not in line for line in _trail_block(view)[1:])

    def test_the_cap_drops_the_oldest_spans_and_says_so_in_plain_english(self) -> None:
        rows = [(tick, f"ROOM_{tick}") for tick in range(40)]
        memory = _walk(*rows)

        view = render_for_prompt(memory, token_budget=8000)

        block = _trail_block(view)
        notice = _TRAIL_TRUNCATED
        assert block[1] == notice
        assert len(block) == 3
        steps = _trail_steps(view)
        assert len(steps) == SELF_LOCATION_TRAIL_MAX_SPANS
        # The RECENT route survives; the far end is what went.
        assert steps[-1] == (39, 39, "ROOM_39")
        assert (0, 0, "ROOM_0") not in steps
        # Craft rule 4: the truncation line carries no ids and no arithmetic.
        assert not any(char.isdigit() for char in notice)
        assert "obs" not in notice

    def test_a_tight_budget_sheds_the_oldest_trail_steps_not_the_newest(
        self,
    ) -> None:
        walk = [(tick, f"ROOM_{tick}") for tick in range(10, 22)]
        memory = AgentMemory()
        for tick, room in walk:
            memory.episodic.append(
                _self_state_event(tick=tick, room=room, agent_id="p-1")
            )
            memory.episodic.append(
                _saw_player_event(
                    tick=tick, player_id=f"p-{tick}", room=room, action=None
                )
            )
        memory.episodic.append(_global_status_event(tick=21, completed=1, total=9))
        full = [(tick, tick, room) for tick, room in walk]

        seen_shed = False
        for budget in range(20, 260):
            view = render_for_prompt(memory, token_budget=budget)
            # The block never overflows the budget onto anything else.
            assert _estimate_tokens_of(view) <= budget
            if _TRAIL_HEADER not in view:
                continue
            block = _trail_block(view)
            steps = _trail_steps(view)
            # Whatever survives is the RECENT end of the route, and a shortened
            # route always says so.
            assert steps == full[len(full) - len(steps) :]
            if len(steps) < len(full):
                seen_shed = True
                assert _TRAIL_TRUNCATED in block
        # The gate bites only if the shedding branch was actually exercised.
        assert seen_shed

    def test_a_malformed_in_vent_row_raises_instead_of_placing_the_agent(
        self,
    ) -> None:
        # AGENTS.md "no silent fallbacks", and the same boundary-contract rule the
        # tactical reader applies: an absent flag means "not in a vent", a
        # present-but-non-bool one is a wiring bug, not a room stay.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=5, room="ADMIN", agent_id="p-1", in_vent=True)
        )
        assert "a vent in ADMIN" in render_for_prompt(memory)

        # An absent key is the pre-11.1 shape and means "not in a vent"; a
        # present one must be a bool, explicit null included.
        for malformed in ("yes", None, 1):
            broken = AgentMemory()
            broken.episodic.append(
                EpisodicEvent(
                    tick=5,
                    type="self_state",
                    payload={
                        "room": "ADMIN",
                        "role": "CREWMATE",
                        "in_vent": malformed,
                    },
                    provenance="observed",
                )
            )

            with pytest.raises(ValueError, match="non-bool in_vent"):
                render_for_prompt(broken)

    def test_the_completed_task_line_is_dated_and_placed_by_one_row(self) -> None:
        # The completion names the room on the row that DATES it (tick 21,
        # ADMIN), never the room the agent had already left.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=20,
                room="EAST_HALL",
                pending_task_id="wiring",
                owned_task_ids=("swipe_card", "wiring"),
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=21,
                room="ADMIN",
                pending_task_id="swipe_card",
                owned_task_ids=("swipe_card",),
            )
        )

        view = render_for_prompt(memory)

        assert "[tick 21] You completed wiring (you were in ADMIN)." in view
        assert "you were in EAST_HALL" not in view
        _assert_completions_agree_with_the_trail(view)

    def test_the_completion_row_is_placed_by_the_row_that_stamps_its_citation(
        self,
    ) -> None:
        # Same-tick rows are not a production shape (perception writes one
        # self_state per packet). Where they agree about the room, each completion
        # still names the room of the row whose observation_id it carries, and the
        # route says the same thing.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=1,
                room="EAST_HALL",
                pending_task_id="wiring",
                owned_task_ids=("submit_scan", "swipe_card", "wiring"),
                observation_id="p-1:1:0",
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=2,
                room="ADMIN",
                pending_task_id="swipe_card",
                owned_task_ids=("submit_scan", "swipe_card"),
                observation_id="p-1:2:0",
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=2,
                room="ADMIN",
                pending_task_id="submit_scan",
                owned_task_ids=("submit_scan",),
                observation_id="p-1:2:1",
            )
        )

        view = render_for_prompt(memory)

        assert (
            "[obs p-1:2:0] [tick 2] You completed wiring (you were in ADMIN)." in view
        )
        assert (
            "[obs p-1:2:1] [tick 2] You completed swipe_card (you were in ADMIN)."
            in view
        )
        _assert_completions_agree_with_the_trail(view)

    def test_same_tick_rows_that_disagree_raise_instead_of_splitting_the_evidence(
        self,
    ) -> None:
        # The route has no sub-tick step, so two rows that put the agent in two
        # rooms at one tick cannot both be rendered: collapsing them would let a
        # completion placed by its own row name ADMIN while the route says MEDBAY,
        # in the same prompt (AGENTS.md "no silent fallbacks").
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=2,
                room="ADMIN",
                pending_task_id="swipe_card",
                observation_id="p-1:2:0",
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=2,
                room="MEDBAY",
                pending_task_id="submit_scan",
                observation_id="p-1:2:1",
            )
        )

        for env in (_TRAIL_ON, None):
            with pytest.raises(ValueError, match="disagree about tick 2"):
                render_for_prompt(
                    memory,
                )

    def test_the_completed_task_room_agrees_with_the_trail_for_its_tick(self) -> None:
        fixture, _ = _load_fixture("self_location_trail")
        memory = _build_memory_from_fixture(fixture)

        view = render_for_prompt(memory)

        _assert_completions_agree_with_the_trail(view)

    def test_the_trail_view_passes_the_canonical_leak_scanners(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=6, role="IMPOSTOR", room="ELECTRICAL", agent_id="p-1"
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=7, role="IMPOSTOR", room="ELECTRICAL", agent_id="p-1", in_vent=True
            )
        )
        memory.beliefs.adjust_suspicion("p-3", delta=0.4)

        view = render_for_prompt(memory)

        assert _TRAIL_HEADER in view
        _scan_rendered_view(view)


def _estimate_tokens_of(text: str) -> int:
    """Mirror ``agents.memory.store._estimate_tokens`` (the budget arithmetic)."""

    if not text:
        return 0
    return (len(text) + 3) // 4


_COMPLETED_LINE = re.compile(
    r"\[tick (?P<tick>\d+)\] You completed \S+ \(you were in (?P<room>[^)]+)\)\."
)


def _assert_completions_agree_with_the_trail(view: str) -> None:
    """Every completion line names the room the trail gives for the tick it states."""

    rooms_by_tick: dict[int, str] = {}
    for start, end, where in _trail_steps(view):
        for tick in range(start, end + 1):
            rooms_by_tick[tick] = where
    for match in _COMPLETED_LINE.finditer(view):
        tick = int(match.group("tick"))
        stated = rooms_by_tick.get(tick)
        if stated is None:
            # The route was cut back past this tick (and the block says so, or
            # the budget took the whole block): showing nothing is not a
            # contradiction, and the line is still placed by its own row.
            assert _TRAIL_TRUNCATED in view or _TRAIL_HEADER not in view, (
                f"the trail is silent about tick {tick} without saying so:\n{view}"
            )
            continue
        assert stated == match.group("room"), (
            f"completion at tick {tick} disagrees with the trail:\n{view}"
        )


# One ``self_state`` row per tick is the production invariant: perception writes
# exactly one per ingested packet (``agents.perception.ingest_packet``), which is
# what lets the trail's per-tick record and the completion line's own row be the
# same answer.
_TRAIL_TICKS = st.lists(
    st.tuples(
        st.integers(min_value=0, max_value=40),
        st.sampled_from(["REACTOR", "ADMIN", "MEDBAY", "EAST_HALL"]),
    ),
    max_size=24,
    unique_by=lambda row: row[0],
)


class TestSelfLocationTrailProperties:
    """Generated event streams: the spans partition exactly the recorded ticks."""

    @settings(max_examples=120)
    @given(rows=_TRAIL_TICKS)
    def test_spans_partition_the_recorded_ticks_exactly(
        self, rows: list[tuple[int, str]]
    ) -> None:
        memory = AgentMemory()
        recorded: dict[int, str] = {}
        for tick, room in sorted(rows):
            memory.episodic.append(
                _self_state_event(tick=tick, room=room, agent_id="p-1")
            )
            recorded[tick] = room
        if not recorded:
            return

        view = render_for_prompt(memory, token_budget=8000)

        claimed = _trail_ticks(view)
        # No overlap, oldest first, and nothing outside the recorded set.
        assert claimed == sorted(claimed)
        assert len(claimed) == len(set(claimed))
        assert set(claimed) <= set(recorded)
        # Nothing may go missing unless the render SAID the route was cut.
        if _TRAIL_TRUNCATED not in view:
            assert set(claimed) == set(recorded)
        for start, end, where in _trail_steps(view):
            assert {recorded[tick] for tick in range(start, end + 1)} == {where}

    @settings(max_examples=120)
    @given(rows=_TRAIL_TICKS)
    def test_a_completion_line_never_disagrees_with_the_trail(
        self, rows: list[tuple[int, str]]
    ) -> None:
        if not rows:
            return
        memory = AgentMemory()
        for index, (tick, room) in enumerate(sorted(rows)):
            memory.episodic.append(
                _self_state_event(
                    tick=tick,
                    room=room,
                    pending_task_id=f"task_{index % 3}",
                    agent_id="p-1",
                )
            )

        view = render_for_prompt(memory, token_budget=8000)

        _assert_completions_agree_with_the_trail(view)


# --------------------------------------------------------------------------- #
# The coalesced render (AILIBI_COALESCED_MEMORY_RENDER, default-OFF).          #
# --------------------------------------------------------------------------- #

_SPAN_ROW = re.compile(
    r"^- (?:\[obs [^\]]+\] )?(?:\[tick (?P<tick>\d+)\] )?You saw (?P<subject>p-\d+) "
    r"(?:(?P<action>task|report) )?in (?P<room>[A-Z_]+)"
    r"(?: ticks (?P<start>\d+)-(?P<end>\d+))?"
    r"(?: \(with (?P<with>[^)]+)\))?"
)
_SPAWN_ROW = re.compile(
    r"^- (?:\[obs [^\]]+\] )?(?:\[tick 0\] )?You saw every other player in "
    r"(?P<room>[A-Z_]+)(?: ticks 0-(?P<end>\d+))?: (?P<subjects>.+)\.$"
)
_TESTIMONY_ROW = "[meeting] CLAIM by "
_OBSERVATIONS_HEADER = "## Recent observations (most salient first):"


def _observation_rows(view: str) -> list[str]:
    """The rendered observation bullets, in the order the model reads them."""

    lines = view.splitlines()
    if _OBSERVATIONS_HEADER not in lines:
        return []
    start = lines.index(_OBSERVATIONS_HEADER) + 1
    end = start
    while end < len(lines) and lines[end].startswith("- "):
        end += 1
    return lines[start:end]


def _sighting_facts(view: str) -> set[tuple[int, str, str, str | None, frozenset[str]]]:
    """Every ``(tick, subject, room, action, companions)`` the render claims.

    A span is expanded back to one entry per tick it names and the spawn summary to
    one per subject it lists, so a coalesced render and a per-row render can be
    compared as the SETS OF FACTS they state rather than as strings.
    """

    facts: set[tuple[int, str, str, str | None, frozenset[str]]] = set()
    for row in _observation_rows(view):
        spawn = _SPAWN_ROW.match(row)
        if spawn is not None:
            subjects = [part.strip() for part in spawn.group("subjects").split(",")]
            for tick in range(int(spawn.group("end") or 0) + 1):
                for subject in subjects:
                    facts.add(
                        (
                            tick,
                            subject,
                            spawn.group("room"),
                            None,
                            frozenset(subjects) - {subject},
                        )
                    )
            continue
        match = _SPAN_ROW.match(row)
        if match is None:
            continue
        companions = frozenset(
            part.strip() for part in (match.group("with") or "").split(",") if part
        )
        if match.group("start") is not None:
            ticks = range(int(match.group("start")), int(match.group("end")) + 1)
        else:
            ticks = range(int(match.group("tick")), int(match.group("tick")) + 1)
        for tick in ticks:
            facts.add(
                (
                    tick,
                    match.group("subject"),
                    match.group("room"),
                    match.group("action"),
                    companions,
                )
            )
    return facts


def _seen(*rows: tuple[int, str, str]) -> AgentMemory:
    """A memory for ``p-1`` holding one ``saw_player`` row per (tick, subject, room)."""

    memory = AgentMemory()
    by_tick: dict[int, list[EpisodicEvent]] = {}
    for tick in sorted({tick for tick, _, _ in rows}):
        by_tick[tick] = [_self_state_event(tick=tick, room="CAFETERIA", agent_id="p-1")]
    for tick, player_id, room in rows:
        by_tick[tick].append(
            _saw_player_event(tick=tick, player_id=player_id, room=room)
        )
    for tick in sorted(by_tick):
        for event in by_tick[tick]:
            memory.episodic.append(event)
    return memory


class TestCoalescedMemoryRender:
    """Routine sightings fold into spans and testimony outranks them.

    Unconditional since the baseline-7 record.
    """

    def test_the_fold_is_unconditional(self) -> None:
        for env in ({}, {ENV_COALESCED_MEMORY_RENDER: "0"}, None):
            assert coalesced_memory_render_enabled(env) is True

    def test_render_matches_the_coalesced_golden(self) -> None:
        fixture, expected = _load_fixture("coalesced_memory_render")
        memory = _build_memory_from_fixture(fixture)
        budget = int(fixture["token_budget"])

        rendered = render_for_prompt(memory, token_budget=budget)

        assert rendered == expected, (
            f"---- expected ----\n{expected}---- rendered ----\n{rendered}"
        )
        # The gate bites: the fold is what keeps eleven rows' worth of facts under
        # eighteen rows, so a memory whose runs are broken by one extra companion
        # per tick renders MORE rows than the golden does.
        broken = _build_memory_from_fixture(
            {
                **fixture,
                "events": [
                    row
                    for event in fixture["events"]
                    for row in (
                        [event]
                        if event["type"] != "saw_player"
                        else [
                            event,
                            {
                                **event,
                                "payload": {**event["payload"], "player_id": "p-7"},
                            },
                        ]
                    )
                ],
            }
        )
        assert len(
            _observation_rows(render_for_prompt(broken, token_budget=budget))
        ) > len(_observation_rows(rendered))

    def test_consecutive_identical_sightings_become_one_span(self) -> None:
        memory = _seen(
            (1, "p-9", "CAFETERIA"),
            (1, "p-8", "CAFETERIA"),
            (2, "p-9", "CAFETERIA"),
            (2, "p-8", "CAFETERIA"),
            (3, "p-9", "CAFETERIA"),
            (3, "p-8", "CAFETERIA"),
        )

        rows = _observation_rows(render_for_prompt(memory))

        assert "- You saw p-9 in CAFETERIA ticks 1-3 (with p-8)." in rows
        assert "- You saw p-8 in CAFETERIA ticks 1-3 (with p-9)." in rows

    def test_a_new_room_breaks_the_run(self) -> None:
        memory = _seen(
            (1, "p-9", "CAFETERIA"),
            (2, "p-9", "ADMIN"),
            (3, "p-9", "ADMIN"),
            (4, "p-9", "ADMIN"),
        )

        rows = _observation_rows(render_for_prompt(memory))

        assert "- [tick 1] You saw p-9 in CAFETERIA." in rows
        assert any(row.startswith("- You saw p-9 in ADMIN ticks 2-4") for row in rows)

    def test_the_span_carries_the_terminal_breadcrumb(self) -> None:
        # The "moved from …" suffix lands on a subject's most-recent sighting only
        # and describes the whole stay, so it rides the span rather than splitting
        # a tick off the end of it.
        memory = _seen(
            (1, "p-9", "CAFETERIA"),
            (2, "p-9", "ADMIN"),
            (3, "p-9", "ADMIN"),
            (4, "p-9", "ADMIN"),
        )

        rows = _observation_rows(render_for_prompt(memory))

        assert (
            "- You saw p-9 in ADMIN ticks 2-4 "
            "(moved from CAFETERIA, last seen there at tick 1)." in rows
        )

    def test_a_new_action_breaks_the_run(self) -> None:
        memory = _seen((1, "p-9", "ADMIN"), (2, "p-9", "ADMIN"))
        memory.episodic.append(
            _saw_player_event(tick=3, player_id="p-9", room="ADMIN", action="task")
        )

        rows = _observation_rows(render_for_prompt(memory))

        assert "- You saw p-9 in ADMIN ticks 1-2." in rows
        assert "- [tick 3] You saw p-9 task in ADMIN." in rows

    def test_a_changed_companion_set_breaks_the_run(self) -> None:
        # p-8 leaves at tick 3, so who p-9 was standing with is NEW information and
        # may not be folded into the earlier span.
        memory = _seen(
            (1, "p-9", "ADMIN"),
            (1, "p-8", "ADMIN"),
            (2, "p-9", "ADMIN"),
            (2, "p-8", "ADMIN"),
            (3, "p-9", "ADMIN"),
        )

        rows = _observation_rows(render_for_prompt(memory))

        assert "- You saw p-9 in ADMIN ticks 1-2 (with p-8)." in rows
        assert "- [tick 3] You saw p-9 in ADMIN." in rows

    def test_a_tick_the_agent_holds_no_row_for_breaks_the_run(self) -> None:
        memory = _seen((1, "p-9", "ADMIN"), (2, "p-9", "ADMIN"), (4, "p-9", "ADMIN"))

        rows = _observation_rows(render_for_prompt(memory))

        assert "- You saw p-9 in ADMIN ticks 1-2." in rows
        assert "- [tick 4] You saw p-9 in ADMIN." in rows
        assert not any("ticks 1-4" in row for row in rows)

    def test_a_lone_sighting_renders_exactly_as_it_does_off(self) -> None:
        memory = _seen((4, "p-9", "ADMIN"))

        on = render_for_prompt(memory)

        assert "- [tick 4] You saw p-9 in ADMIN." in _observation_rows(on)

    def test_a_full_roster_tick_zero_group_collapses_to_one_line(self) -> None:
        memory = _seen(
            (0, "p-2", "CAFETERIA"),
            (0, "p-3", "CAFETERIA"),
            (0, "p-4", "CAFETERIA"),
            (1, "p-2", "ADMIN"),
        )

        rows = _observation_rows(render_for_prompt(memory))

        assert (
            "- [tick 0] You saw every other player in CAFETERIA: p-2, p-3, p-4." in rows
        )
        assert not any("[tick 0] You saw p-2 in CAFETERIA" in row for row in rows)

    def test_a_partial_tick_zero_view_keeps_its_rows(self) -> None:
        # p-4 is a known roster id (the agent saw it later) but was NOT in the
        # spawn room, and that absence is real information: no summary line.
        memory = _seen(
            (0, "p-2", "CAFETERIA"),
            (0, "p-3", "CAFETERIA"),
            (1, "p-4", "ADMIN"),
        )

        rows = _observation_rows(render_for_prompt(memory))

        assert not any("every other player" in row for row in rows)
        assert "- [tick 0] You saw p-2 in CAFETERIA (with p-3)." in rows
        assert "- [tick 0] You saw p-3 in CAFETERIA (with p-2)." in rows

    def test_a_roster_that_stayed_together_summarises_its_whole_span(self) -> None:
        memory = _seen(
            (0, "p-2", "CAFETERIA"),
            (0, "p-3", "CAFETERIA"),
            (1, "p-2", "CAFETERIA"),
            (1, "p-3", "CAFETERIA"),
        )

        rows = _observation_rows(render_for_prompt(memory))

        assert "- You saw every other player in CAFETERIA ticks 0-1: p-2, p-3." in rows

    def test_the_summary_covers_only_the_ticks_the_whole_group_shared(self) -> None:
        # p-2 starts a task at tick 1 while p-3 stands there unchanged. The group
        # was still whole at tick 0, so it still collapses -- the summary covers the
        # shared tick only, and what each subject did afterwards keeps its own row.
        memory = _seen(
            (0, "p-2", "CAFETERIA"),
            (0, "p-3", "CAFETERIA"),
            (1, "p-3", "CAFETERIA"),
        )
        memory.episodic.append(
            _saw_player_event(tick=1, player_id="p-2", room="CAFETERIA", action="task")
        )

        rows = _observation_rows(render_for_prompt(memory))

        assert "- [tick 0] You saw every other player in CAFETERIA: p-2, p-3." in rows
        assert "- [tick 1] You saw p-2 task in CAFETERIA (with p-3)." in rows
        assert "- [tick 1] You saw p-3 in CAFETERIA (with p-2)." in rows
        assert not any("[tick 0] You saw p-3 in CAFETERIA" in row for row in rows)

    def test_testimony_outranks_bare_co_presence_and_hard_evidence_outranks_it(
        self,
    ) -> None:
        memory = _seen((4, "p-9", "ADMIN"))
        memory.episodic.append(
            _saw_player_event(tick=5, player_id="p-8", room="ADMIN", action="vent")
        )
        memory.episodic.append(
            EpisodicEvent(
                tick=6,
                type="reported_testimony",
                payload={
                    "speaker": "p-3",
                    "subject": "p-9",
                    "kind": "saw_player",
                    "room": "STORAGE",
                    "from_tick": 2,
                },
                provenance="reported",
            )
        )

        rows = _observation_rows(render_for_prompt(memory))
        order = [
            next(index for index, row in enumerate(rows) if "vent in ADMIN" in row),
            next(index for index, row in enumerate(rows) if _TESTIMONY_ROW in row),
            next(
                index for index, row in enumerate(rows) if "You saw p-9 in ADMIN" in row
            ),
        ]

        assert order == sorted(order)

    def test_salience_is_a_sort_key_not_a_filter(self) -> None:
        # At an unbounded budget the folded render states every fact the committed
        # fixture holds -- the same subjects, rooms, ticks and companions, re-shaped
        # rather than dropped.
        fixture, expected = _load_fixture("coalesced_memory_render")
        memory = _build_memory_from_fixture(fixture)

        generous = render_for_prompt(memory, token_budget=8000)

        assert _sighting_facts(generous) == _sighting_facts(expected)
        assert _sighting_facts(generous)

    def test_a_dropped_fact_fails_the_same_comparison(self) -> None:
        # The gate bites: a render missing one tick of a span is not the same set.
        full = f"{_OBSERVATIONS_HEADER}\n- You saw p-9 in ADMIN ticks 1-3 (with p-8).\n"
        short = full.replace("ticks 1-3", "ticks 1-2")

        assert _sighting_facts(full) != _sighting_facts(short)
        assert len(_sighting_facts(full)) == 3

    def test_every_rendered_citation_id_is_one_the_agent_stores(self) -> None:
        memory = AgentMemory()
        for tick in range(6):
            memory.episodic.append(
                _self_state_event(
                    tick=tick,
                    room="CAFETERIA",
                    agent_id="p-1",
                    observation_id=f"p-1:{tick}:0",
                )
            )
            for index, subject in enumerate(("p-2", "p-3"), start=1):
                memory.episodic.append(
                    EpisodicEvent(
                        tick=tick,
                        type="saw_player",
                        payload={
                            "player_id": subject,
                            "room": "CAFETERIA",
                            "action": None,
                        },
                        provenance="observed",
                        observation_id=f"p-1:{tick}:{index}",
                    )
                )

        view = render_for_prompt(memory, token_budget=8000)

        stored = {
            event.observation_id for event in memory.episodic.recent(since_tick=0)
        }
        cited = set(_OBS_ID_IN_VIEW.findall(view))
        assert cited
        assert cited <= stored

    def test_the_reported_band_survives_a_budget_that_sheds_it_off(self) -> None:
        memory = _seen(*[(tick, "p-9", "ADMIN") for tick in range(1, 12)])
        memory.episodic.append(
            EpisodicEvent(
                tick=12,
                type="reported_testimony",
                payload={"speaker": "p-3", "subject": "p-9", "kind": "accusation"},
                provenance="reported",
            )
        )

        # The reported band outranks bare co-presence, so a budget that sheds
        # eleven ticks of routine sighting still carries the claim.
        tight = 90
        assert _TESTIMONY_ROW in render_for_prompt(memory, token_budget=tight)
        # The gate bites: at a budget too small for either, nothing survives.
        assert _TESTIMONY_ROW not in render_for_prompt(memory, token_budget=30)


_SPAN_IN_PROMPT = re.compile(
    r"^- \[obs (?P<id>[^\]]+)\] You saw \S+ (?:\w+ )?in [A-Z_]+ ticks \d+-\d+",
    re.MULTILINE,
)
_SPAWN_IN_PROMPT = re.compile(
    r"^- \[obs (?P<id>[^\]]+)\] (?:\[tick 0\] )?You saw every other player in [A-Z_]+",
    re.MULTILINE,
)
# An id no agent can hold: the shape is valid, the owner does not exist.
_FABRICATED_OBSERVATION_ID: Final[str] = "p-99:999:0"


class _UniverseCapturingRunner:
    """A meeting runner that records each voter's stored citation universe.

    The universe is read through ``observation_ids_for_meeting()`` -- the same
    accessor ``orchestrator.game`` threads onto ``MeetingParticipant.observation_ids``
    and the manager validates a ballot against -- so the assertions below hold the
    render to the agent's OWN STORE rather than to the ids the render printed.
    """

    def __init__(self, inner: DefaultMeetingRunner) -> None:
        self._inner = inner
        self.universes: list[dict[str, frozenset[str]]] = []

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[str, AgentInterface],
    ) -> MeetingArtifacts:
        self.universes.append(
            {
                player_id: frozenset(agent.observation_ids_for_meeting())
                for player_id, agent in agents.items()
                if state.players[player_id].alive
                and isinstance(agent, MeetingAwareAgent)
            }
        )
        return await self._inner.run_meeting(
            meeting_id=meeting_id, trigger=trigger, state=state, agents=agents
        )


class _CitingFakeProvider:
    """The deterministic fake, except that its ballots cite a coalesced row.

    :class:`~llm.fake_provider.FakeProvider` builds a MINIMAL valid instance of
    the schema, so every ballot it returns carries a null
    ``primary_reason_observation_id`` -- which leaves the production citation
    path (participant construction -> the manager's validator -> the recorded
    ballot) unexercised by any fake-provider game. This answers exactly as the
    fake does except on a :class:`VoteBallot` call, where it copies the FIRST
    coalesced row the voter's own prompt offers into that field, or
    ``fabricated_id`` when one is given -- the perturbation that proves the
    production path validates rather than passes ids through.
    """

    def __init__(self, *, fabricated_id: str | None = None) -> None:
        self._inner = FakeProvider()
        self._fabricated_id = fabricated_id
        self.citations_offered = 0

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        response = await self._inner.complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )
        if schema is not VoteBallot or agent_id is None:
            return response
        coalesced = _coalesced_ids(prompt)
        if not coalesced:
            return response
        payload = cast(dict[str, Any], json.loads(response.text))
        payload["primary_reason_observation_id"] = (
            self._fabricated_id if self._fabricated_id is not None else coalesced[0]
        )
        self.citations_offered += 1
        return LLMResponse(
            text=json.dumps(payload),
            usage=response.usage,
            cost_usd=response.cost_usd,
            model=response.model,
        )


def _cited_ids(pattern: re.Pattern[str], prompt: str) -> list[str]:
    return [match.group("id") for match in pattern.finditer(prompt)]


def _coalesced_ids(prompt: str) -> list[str]:
    """The ids the FOLDED rows carry: every span, then the spawn summaries."""

    return _cited_ids(_SPAN_IN_PROMPT, prompt) + _cited_ids(_SPAWN_IN_PROMPT, prompt)


def _run_lever_on_game(
    *, tmp_path: Path, client: _CitingFakeProvider, seed: int = 3
) -> tuple[list[MeetingReplayEntry], list[dict[str, frozenset[str]]]]:
    """Play one fake-provider 9p2i game and return its meetings + universes."""

    runner = _UniverseCapturingRunner(
        build_default_meeting_runner(
            llm_client=client, budget=GameBudget(max_cost_usd=1.00)
        )
    )
    game = HeadlessGame(
        seed=seed,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=tmp_path / "replay.jsonl",
        audit_log_path=tmp_path / "audit.jsonl",
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=DEFAULT_TASKS_PER_CREWMATE,
        scheduler=TickScheduler(max_ticks=200),
        meeting_runner=runner,
    )
    result = game.run()
    meetings = [
        entry
        for entry in read_all_entries(result.replay_path)
        if isinstance(entry, MeetingReplayEntry)
    ]
    assert meetings, "the seed must reach a meeting for this to test anything"
    assert len(runner.universes) == len(meetings)
    return meetings, runner.universes


@pytest.mark.slow
def test_a_lever_on_game_carries_its_coalesced_citations_through_the_meeting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A fake-provider 9p2i game with the lever ON, read end to end.

    The unit pins above prove the fold's shapes; this proves the shapes reach a
    real meeting, that what they cite is real, and that a coalesced citation
    survives the PRODUCTION ballot path into the recorded result. The lever is
    set in the process environment, so the production render seam
    (``TacticalAgent.render_memory_for_meeting``) resolves it exactly as a
    recorded game would; the runner wrapper captures each voter's STORED
    observation-id set as participant construction reads it; and the ballots the
    replay carries are the manager's own output, validated against the
    participant the orchestrator wired, not against anything this test built.
    """

    monkeypatch.setenv(ENV_COALESCED_MEMORY_RENDER, "1")
    client = _CitingFakeProvider()
    meetings, universes_per_meeting = _run_lever_on_game(
        tmp_path=tmp_path, client=client
    )

    spans = spawn_rows = cited = 0
    landed = 0
    for entry, universes in zip(meetings, universes_per_meeting, strict=True):
        offered_by_voter: dict[str, frozenset[str]] = {}
        for call in entry.llm_calls:
            span_ids = _cited_ids(_SPAN_IN_PROMPT, call.prompt)
            spawn_ids = _cited_ids(_SPAWN_IN_PROMPT, call.prompt)
            spans += len(span_ids)
            spawn_rows += len(spawn_ids)
            rendered = frozenset(_OBS_ID_IN_VIEW.findall(call.prompt))
            cited += len(rendered)
            if not rendered:
                continue
            agent_id = call.agent_id
            assert agent_id is not None, "a prompt citing observations names its agent"
            universe = universes[agent_id]
            assert universe, f"{agent_id} entered the meeting with no citable ids"
            # The authority is the voter's STORE, not the render: every id the
            # coalesced prompt offers -- coalesced rows included -- must be one
            # participant construction would accept.
            assert rendered <= universe, (
                f"{agent_id} was offered ids it does not hold: "
                f"{sorted(rendered - universe)}"
            )
            offered = frozenset(span_ids) | frozenset(spawn_ids)
            assert offered <= universe
            offered_by_voter[agent_id] = offered_by_voter.get(
                agent_id, frozenset()
            ) | frozenset(offered)

        # The production path, end to end: the manager validated these ballots
        # against the participant the orchestrator wired, so a coalesced id in
        # the RECORDED result is one the voter's own store entitled it to.
        for ballot in entry.ballots:
            observation_id = ballot.primary_reason_observation_id
            if observation_id is None:
                continue
            landed += 1
            assert observation_id in offered_by_voter[ballot.voter], (
                f"{ballot.voter} cited {observation_id}, which no folded row offered"
            )
            assert observation_id in universes[ballot.voter]
            assert (
                INVALID_OBSERVATION_ID_MARKER.format(observation_id=observation_id)
                not in ballot.rationale_text
            )

    # The lever really reached the live render: both folded shapes are in the
    # recorded prompts, the meeting still produced ballots, and a folded row's
    # citation is what the recorded ballots carry.
    assert spans > 0 and spawn_rows > 0 and cited > 0
    assert all(entry.ballots for entry in meetings)
    assert client.citations_offered > 0
    assert landed > 0, "no coalesced citation reached a recorded ballot"


@pytest.mark.slow
def test_a_fabricated_citation_does_not_survive_the_same_meeting_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The perturbation for the gate above: the same game, the same wiring, but
    # every ballot cites an id no agent holds. If the production path let
    # citations through unvalidated, the fabrication would land exactly like a
    # coalesced id does -- instead every recorded ballot comes back nulled and
    # marked, so the test above is checking entitlement, not shape.
    monkeypatch.setenv(ENV_COALESCED_MEMORY_RENDER, "1")
    client = _CitingFakeProvider(fabricated_id=_FABRICATED_OBSERVATION_ID)
    meetings, universes_per_meeting = _run_lever_on_game(
        tmp_path=tmp_path, client=client
    )

    marker = INVALID_OBSERVATION_ID_MARKER.format(
        observation_id=_FABRICATED_OBSERVATION_ID
    )
    marked = 0
    for entry, universes in zip(meetings, universes_per_meeting, strict=True):
        for universe in universes.values():
            assert _FABRICATED_OBSERVATION_ID not in universe
        for ballot in entry.ballots:
            assert ballot.primary_reason_observation_id is None
            if marker in ballot.rationale_text:
                marked += 1

    assert client.citations_offered > 0, "the perturbation never cited anything"
    assert marked > 0, "the nulled citation left no audit marker"
