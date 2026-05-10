from __future__ import annotations

import pytest

from agents.memory.beliefs import (
    AlibiClaim,
    BeliefState,
    ContradictionRef,
    PlayerBelief,
)
from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.working import Goal, LastSeen, WorkingMemory


def _event(
    *, tick: int = 0, type: str = "saw_player", provenance: str = "observed"
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=type,
        payload={"detail": "value"},
        provenance=provenance,
    )


class TestEpisodicMemory:
    def test_episodic_event_is_frozen(self) -> None:
        event = _event()

        with pytest.raises(Exception):
            event.tick = 99  # type: ignore[misc]

    def test_append_and_recent_returns_events_in_order(self) -> None:
        store = MemoryStore()
        e0 = _event(tick=0)
        e1 = _event(tick=5)
        e2 = _event(tick=10)

        store.append(e0)
        store.append(e1)
        store.append(e2)

        assert store.recent(since_tick=0) == (e0, e1, e2)

    def test_recent_filters_by_since_tick(self) -> None:
        store = MemoryStore()
        e0 = _event(tick=0)
        e5 = _event(tick=5)
        e10 = _event(tick=10)
        store.append(e0)
        store.append(e5)
        store.append(e10)

        assert store.recent(since_tick=5) == (e5, e10)
        assert store.recent(since_tick=11) == ()

    def test_append_rejects_out_of_order_ticks(self) -> None:
        store = MemoryStore()
        store.append(_event(tick=10))

        with pytest.raises(ValueError, match="non-decreasing"):
            store.append(_event(tick=9))

    def test_append_allows_equal_tick_for_simultaneous_events(self) -> None:
        store = MemoryStore()
        e1 = _event(tick=5, type="saw_player")
        e2 = _event(tick=5, type="heard_vent")

        store.append(e1)
        store.append(e2)

        assert store.recent(since_tick=5) == (e1, e2)

    def test_len_reports_number_of_events(self) -> None:
        store = MemoryStore()
        assert len(store) == 0

        store.append(_event(tick=0))
        store.append(_event(tick=1))

        assert len(store) == 2

    def test_provenance_is_preserved_verbatim(self) -> None:
        store = MemoryStore()
        observed = _event(tick=0, provenance="observed")
        reported = _event(tick=1, provenance="reported")

        store.append(observed)
        store.append(reported)

        provenances = tuple(e.provenance for e in store.recent(since_tick=0))
        assert provenances == ("observed", "reported")


class TestWorkingMemory:
    def test_initial_state_is_empty(self) -> None:
        memory = WorkingMemory()

        assert memory.goal is None
        assert memory.path == ()
        assert memory.last_seen("p2") is None

    def test_set_and_clear_goal(self) -> None:
        memory = WorkingMemory()
        goal = Goal(kind="do_task", target="swipe_card")

        memory.set_goal(goal)
        assert memory.goal == goal

        memory.clear_goal()
        assert memory.goal is None

    def test_set_path_overwrites_previous_path(self) -> None:
        memory = WorkingMemory()

        memory.set_path(("CAFETERIA", "ADMIN"))
        assert memory.path == ("CAFETERIA", "ADMIN")

        memory.set_path(("ADMIN", "STORAGE"))
        assert memory.path == ("ADMIN", "STORAGE")

    def test_set_path_rejects_empty_path(self) -> None:
        memory = WorkingMemory()

        with pytest.raises(ValueError, match="non-empty"):
            memory.set_path(())

    def test_clear_path_resets_to_empty_tuple(self) -> None:
        memory = WorkingMemory()
        memory.set_path(("CAFETERIA", "ADMIN"))

        memory.clear_path()

        assert memory.path == ()

    def test_record_sighting_overwrites_with_more_recent_tick(self) -> None:
        memory = WorkingMemory()
        memory.record_sighting(player_id="p2", room="ADMIN", tick=10)
        memory.record_sighting(player_id="p2", room="ELECTRICAL", tick=20)

        assert memory.last_seen("p2") == LastSeen(tick=20, room="ELECTRICAL")

    def test_record_sighting_rejects_negative_tick(self) -> None:
        memory = WorkingMemory()

        with pytest.raises(ValueError, match="non-negative"):
            memory.record_sighting(player_id="p2", room="ADMIN", tick=-1)

    def test_record_sighting_rejects_out_of_order_ticks_per_player(self) -> None:
        memory = WorkingMemory()
        memory.record_sighting(player_id="p2", room="ADMIN", tick=10)

        with pytest.raises(ValueError, match="non-decreasing"):
            memory.record_sighting(player_id="p2", room="ELECTRICAL", tick=9)

    def test_record_sighting_tracks_separate_players_independently(self) -> None:
        memory = WorkingMemory()
        memory.record_sighting(player_id="p2", room="ADMIN", tick=10)
        memory.record_sighting(player_id="p3", room="STORAGE", tick=5)

        assert memory.last_seen("p2") == LastSeen(tick=10, room="ADMIN")
        assert memory.last_seen("p3") == LastSeen(tick=5, room="STORAGE")


class TestBeliefState:
    def test_view_for_unknown_player_returns_neutral_default(self) -> None:
        beliefs = BeliefState()

        view = beliefs.view("p7")

        assert view == PlayerBelief()
        assert view.trust == 0.5
        assert view.suspicion == 0.5
        assert view.alibis == ()
        assert view.inconsistencies == ()

    def test_unknown_player_view_does_not_create_entry(self) -> None:
        beliefs = BeliefState()

        beliefs.view("p7")

        assert beliefs.known_players() == ()

    def test_adjust_suspicion_updates_and_clamps_high(self) -> None:
        beliefs = BeliefState()

        beliefs.adjust_suspicion("p2", delta=0.3)
        assert beliefs.view("p2").suspicion == pytest.approx(0.8)

        beliefs.adjust_suspicion("p2", delta=0.5)
        assert beliefs.view("p2").suspicion == 1.0

    def test_adjust_suspicion_clamps_low(self) -> None:
        beliefs = BeliefState()

        beliefs.adjust_suspicion("p2", delta=-1.0)

        assert beliefs.view("p2").suspicion == 0.0

    def test_adjust_trust_updates_and_clamps(self) -> None:
        beliefs = BeliefState()

        beliefs.adjust_trust("p1", delta=0.4)
        assert beliefs.view("p1").trust == pytest.approx(0.9)

        beliefs.adjust_trust("p1", delta=0.5)
        assert beliefs.view("p1").trust == 1.0

        beliefs.adjust_trust("p1", delta=-2.0)
        assert beliefs.view("p1").trust == 0.0

    def test_record_alibi_appends_in_order(self) -> None:
        beliefs = BeliefState()
        c1 = AlibiClaim(player_id="p4", tick=400, room="STORAGE", source="p4")
        c2 = AlibiClaim(player_id="p4", tick=410, room="STORAGE", source="p4")

        beliefs.record_alibi(c1)
        beliefs.record_alibi(c2)

        assert beliefs.view("p4").alibis == (c1, c2)

    def test_record_contradiction_appends_to_inconsistencies(self) -> None:
        beliefs = BeliefState()
        contradiction = ContradictionRef(
            summary="alibi disagreement",
            left_ref="alibi:p4@400",
            right_ref="sighting:p6:p4@405",
        )

        beliefs.record_contradiction("p4", contradiction)

        assert beliefs.view("p4").inconsistencies == (contradiction,)

    def test_decay_suspicion_pulls_toward_baseline(self) -> None:
        beliefs = BeliefState()
        beliefs.adjust_suspicion("p2", delta=0.5)
        assert beliefs.view("p2").suspicion == 1.0

        beliefs.decay_suspicion("p2", toward=0.5, rate=0.5)

        assert beliefs.view("p2").suspicion == pytest.approx(0.75)

    def test_decay_suspicion_with_rate_zero_is_no_op(self) -> None:
        beliefs = BeliefState()
        beliefs.adjust_suspicion("p2", delta=0.3)
        before = beliefs.view("p2").suspicion

        beliefs.decay_suspicion("p2", rate=0.0)

        assert beliefs.view("p2").suspicion == before

    def test_decay_suspicion_with_rate_one_snaps_to_target(self) -> None:
        beliefs = BeliefState()
        beliefs.adjust_suspicion("p2", delta=0.4)

        beliefs.decay_suspicion("p2", toward=0.5, rate=1.0)

        assert beliefs.view("p2").suspicion == 0.5

    def test_decay_suspicion_rejects_rate_outside_unit_interval(self) -> None:
        beliefs = BeliefState()

        with pytest.raises(ValueError, match=r"\[0, 1\]"):
            beliefs.decay_suspicion("p2", rate=1.5)

        with pytest.raises(ValueError, match=r"\[0, 1\]"):
            beliefs.decay_suspicion("p2", rate=-0.1)

    def test_known_players_lists_only_touched_players(self) -> None:
        beliefs = BeliefState()
        beliefs.adjust_suspicion("p2", delta=0.1)
        beliefs.adjust_trust("p3", delta=0.1)
        beliefs.record_alibi(
            AlibiClaim(player_id="p4", tick=10, room="ADMIN", source="p4")
        )

        assert set(beliefs.known_players()) == {"p2", "p3", "p4"}

    def test_view_returns_immutable_snapshot(self) -> None:
        beliefs = BeliefState()
        beliefs.record_alibi(
            AlibiClaim(player_id="p2", tick=10, room="ADMIN", source="p2")
        )
        snapshot = beliefs.view("p2")

        beliefs.record_alibi(
            AlibiClaim(player_id="p2", tick=20, room="STORAGE", source="p2")
        )

        assert len(snapshot.alibis) == 1
        assert len(beliefs.view("p2").alibis) == 2
