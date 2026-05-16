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

from agents.memory.beliefs import AlibiClaim, ContradictionRef
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
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="self_state",
        payload={
            "room": room,
            "role": role,
            "pending_task_id": pending_task_id,
        },
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

        view = render_for_prompt(memory, token_budget=38)

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
        memory = AgentMemory()
        memory.episodic.append(_self_state_event(tick=0))
        memory.beliefs.record_alibi(
            AlibiClaim(player_id="p-9", tick=10, room="ADMIN", source="p-9")
        )

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
