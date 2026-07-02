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
from typing import Any, cast

import pytest

from agents.memory.beliefs import ContradictionRef
from agents.memory.episodic import EpisodicEvent
from agents.memory.store import (
    DEFAULT_TOKEN_BUDGET,
    AgentMemory,
    render_for_prompt,
)
from eval.leak_test import (
    JsonValue,
    _assert_no_recursive_hidden_fields,
    _assert_no_role_bearing_values,
)

_FIXTURE_DIR = Path("tests/fixtures/memory_rendering")
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
) -> EpisodicEvent:
    payload: dict[str, Any] = {
        "room": room,
        "role": role,
        "pending_task_id": pending_task_id,
    }
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

        view = render_for_prompt(memory, token_budget=40)

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


class TestCompletedTaskInference:
    def test_pending_task_clearing_emits_completed_task_observation(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=100,
                room="ADMIN",
                pending_task_id="wiring_admin",
            )
        )
        memory.episodic.append(
            _self_state_event(tick=120, room="ADMIN", pending_task_id=None)
        )

        view = render_for_prompt(memory)

        assert "[tick 120] You completed wiring_admin (you were in ADMIN)." in view

    def test_first_self_state_does_not_emit_completed_task(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=0, pending_task_id="wiring_admin")
        )

        view = render_for_prompt(memory)

        assert "You completed" not in view

    def test_pending_rollover_to_next_map_id_emits_completion(self) -> None:
        # Multi-task 9p/2i loadout: completing the first task rolls
        # ``pending_task_id`` from one map id to the NEXT (not to ``None``). The
        # finished task's completion alibi must still render -- the pending id
        # changes only when the previous pending task completed (PR #109 review).
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=100, room="ADMIN", pending_task_id="swipe_card")
        )
        memory.episodic.append(
            _self_state_event(tick=130, room="MEDBAY", pending_task_id="submit_scan")
        )

        view = render_for_prompt(memory)

        assert "[tick 130] You completed swipe_card (you were in ADMIN)." in view
        # The NEW pending task is not yet completed, so it is not reported.
        assert "You completed submit_scan" not in view

    def test_consecutive_task_completions_each_emit(self) -> None:
        # A full multi-task loadout (rollover then final clear) renders BOTH
        # completion alibis: swipe_card -> submit_scan (rollover) then
        # submit_scan -> None (final clear).
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=100, room="ADMIN", pending_task_id="swipe_card")
        )
        memory.episodic.append(
            _self_state_event(tick=130, room="MEDBAY", pending_task_id="submit_scan")
        )
        memory.episodic.append(
            _self_state_event(tick=160, room="MEDBAY", pending_task_id=None)
        )

        view = render_for_prompt(memory, token_budget=8000)

        assert "[tick 130] You completed swipe_card (you were in ADMIN)." in view
        assert "[tick 160] You completed submit_scan (you were in MEDBAY)." in view

    def test_unchanged_pending_task_does_not_emit_completion(self) -> None:
        # Continuing the SAME multi-tick task (pending id unchanged) must not
        # spuriously report a completion -- the regression guard for inferring
        # completion from a non-None rollover.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=100, room="ADMIN", pending_task_id="swipe_card")
        )
        memory.episodic.append(
            _self_state_event(tick=130, room="ADMIN", pending_task_id="swipe_card")
        )

        view = render_for_prompt(memory)

        assert "You completed" not in view


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
