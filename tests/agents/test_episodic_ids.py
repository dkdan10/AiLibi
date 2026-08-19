"""Stable observation ids + the render lever (Task 16.5, C8).

The unit home for the C8 identity substrate
(audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 C3/C8, DESIGN.md
§5.5 / §6.6):

* the deterministic ``{agent_id}:{tick}:{seq}`` scheme
  (:func:`agents.memory.episodic.derive_observation_id`), stamped at write time
  by :func:`agents.perception.ingest_packet` on every first-hand OBSERVED row and
  guarded for uniqueness by :meth:`agents.memory.episodic.MemoryStore.append`;
* the ``AILIBI_OBSERVATION_ID_RENDERING`` render lever
  (:func:`agents.memory.store.observation_id_rendering_enabled`), graduated to
  unconditional at Task 16.17, which folds ``[obs {id}]`` into each first-hand
  remembered observation line.

This file also hosts the committed-set two-walk determinism pin (added by the
second worker), which walks committed replays twice and asserts the two
reconstructions assign byte-identical ids, and the read-path pins for
:meth:`agents.memory.episodic.MemoryStore.recent` — its equivalence to a linear
filter over random legal logs, its single bisection, and the invalidation of its
whole-log cache on write.
"""

from __future__ import annotations

import random
import re
from bisect import bisect_left
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from agents.memory import episodic
from agents.memory.episodic import (
    EpisodicEvent,
    MemoryStore,
    derive_observation_id,
)
from agents.memory.store import (
    ENV_OBSERVATION_ID_RENDERING,
    AgentMemory,
    absorb_meeting_evidence,
    absorb_reported_testimony,
    observation_id_rendering_enabled,
    render_for_prompt,
)
from agents.perception import (
    EVENT_GLOBAL_STATUS,
    EVENT_REPORTED_TESTIMONY,
    PROVENANCE_INFERRED,
    PROVENANCE_OBSERVED,
    ingest_packet,
)
from meetings.schemas import ReportedStatement
from observation.packet import (
    AudibleEvent,
    BodyView,
    GlobalView,
    MovedPlayerView,
    ObservationPacket,
    OwnKillView,
    PlayerView,
    SelfView,
)


def _global_view(
    *,
    tasks_completed: int = 1,
    tasks_total: int = 4,
) -> GlobalView:
    return GlobalView(
        tasks_completed=tasks_completed,
        tasks_total=tasks_total,
        task_completion_percent=tasks_completed / tasks_total,
        sabotage_active=False,
        sabotage_kind=None,
    )


def _packet(
    *,
    tick: int = 12,
    agent_id: str = "p1",
    role: str = "CREWMATE",
    room: str = "CAFETERIA",
    pending_task_id: str | None = "swipe_card",
    fellow_impostor_ids: tuple[str, ...] = (),
    visible_players: tuple[PlayerView, ...] = (),
    visible_bodies: tuple[BodyView, ...] = (),
    audible_events: tuple[AudibleEvent, ...] = (),
    moved_players: tuple[MovedPlayerView, ...] = (),
    cooldown: int | None = None,
    own_kill: OwnKillView | None = None,
) -> ObservationPacket:
    """Minimal :class:`ObservationPacket` fixture (mirrors test_perception.py)."""

    return ObservationPacket(
        tick=tick,
        agent_id=agent_id,
        self_state=SelfView(
            room=room,
            role=role,  # type: ignore[arg-type]
            pending_task_id=pending_task_id,
            fellow_impostor_ids=fellow_impostor_ids,
            own_kill=own_kill,
        ),
        visible_players=visible_players,
        visible_bodies=visible_bodies,
        audible_events=audible_events,
        moved_players=moved_players,
        global_state=_global_view(),
        cooldown=cooldown,
    )


class TestObservationIdScheme:
    def test_ids_follow_scheme_in_ingestion_order(self) -> None:
        # A packet that exercises the OBSERVED write sites in the documented
        # append order (self_state, saw_player*, saw_player_move, saw_body, heard):
        # each row's id is a dense ``{agent}:{tick}:{k}`` with k running 0..n-1,
        # and the trailing inferred global_status row carries no id.
        store = MemoryStore()
        ingest_packet(
            packet=_packet(
                tick=7,
                agent_id="p1",
                visible_players=(
                    PlayerView(id="p2", room="ADMIN", action="task"),
                    PlayerView(id="p4", room="ADMIN", action=None),
                ),
                moved_players=(
                    MovedPlayerView(id="p5", from_room="CAFETERIA", to_room="ADMIN"),
                ),
                visible_bodies=(
                    BodyView(id="p3-body", room="ELECTRICAL", victim_id="p3"),
                ),
                audible_events=(AudibleEvent(kind="sabotage_alarm"),),
            ),
            memory=store,
        )

        events = store.recent(since_tick=0)
        observed = [e for e in events if e.provenance == PROVENANCE_OBSERVED]
        assert [e.observation_id for e in observed] == [
            f"p1:7:{k}" for k in range(len(observed))
        ]
        # The trailing inferred aggregate is not first-hand citable evidence.
        assert events[-1].type == EVENT_GLOBAL_STATUS
        assert events[-1].provenance == PROVENANCE_INFERRED
        assert events[-1].observation_id is None

    def test_cooldown_and_own_kill_sites_get_dense_ids(self) -> None:
        # The impostor-only sites (own_kill, cooldown) are stamped in order too:
        # self_state(0), own_kill(1), cooldown(2), global_status(None).
        store = MemoryStore()
        ingest_packet(
            packet=_packet(
                tick=3,
                agent_id="p9",
                role="IMPOSTOR",
                cooldown=5,
                own_kill=OwnKillView(victim_id="p2", room="CAFETERIA"),
            ),
            memory=store,
        )

        observed = [
            e for e in store.recent(since_tick=0) if e.provenance == PROVENANCE_OBSERVED
        ]
        assert [(e.type, e.observation_id) for e in observed] == [
            ("self_state", "p9:3:0"),
            ("own_kill", "p9:3:1"),
            ("cooldown_status", "p9:3:2"),
        ]

    def test_two_fresh_stores_yield_identical_id_streams(self) -> None:
        # Determinism: the identical packet sequence into two fresh stores
        # regenerates the identical (tick, type, observation_id) stream.
        def _ingest_all() -> MemoryStore:
            store = MemoryStore()
            for tick in (4, 9):
                ingest_packet(
                    packet=_packet(
                        tick=tick,
                        agent_id="p1",
                        visible_players=(
                            PlayerView(id="p2", room="ADMIN", action=None),
                        ),
                        visible_bodies=(
                            BodyView(id="p3-body", room="ADMIN", victim_id="p3"),
                        ),
                    ),
                    memory=store,
                )
            return store

        stream_a = [
            (e.tick, e.type, e.observation_id)
            for e in _ingest_all().recent(since_tick=0)
        ]
        stream_b = [
            (e.tick, e.type, e.observation_id)
            for e in _ingest_all().recent(since_tick=0)
        ]
        assert stream_a == stream_b

    def test_ids_survive_filtered_reads(self) -> None:
        # The id is stamped at write, never derived from read-time position: a
        # ``recent(since_tick=...)`` filter that drops earlier ticks leaves each
        # surviving row's id unchanged (so the tick-10 rows keep seq 0.. even
        # though they are no longer at index 0 of the full log).
        store = MemoryStore()
        ingest_packet(
            packet=_packet(
                tick=5,
                agent_id="p1",
                visible_players=(PlayerView(id="p2", room="ADMIN", action=None),),
            ),
            memory=store,
        )
        ingest_packet(
            packet=_packet(
                tick=10,
                agent_id="p1",
                visible_players=(PlayerView(id="p2", room="ADMIN", action=None),),
            ),
            memory=store,
        )

        recent = store.recent(since_tick=10)
        assert all(e.tick == 10 for e in recent)
        observed = [e for e in recent if e.provenance == PROVENANCE_OBSERVED]
        assert [e.observation_id for e in observed] == ["p1:10:0", "p1:10:1"]

    def test_repeated_same_tick_ingest_continues_seq(self) -> None:
        # Production delivers one packet per (agent, tick), but the store tolerates
        # repeated same-tick ingestion; ``seq`` continues from the existing
        # id-stamped count so the two calls produce dense, non-colliding seq values
        # (and never trip the append-time duplicate-id guard).
        store = MemoryStore()
        ingest_packet(
            packet=_packet(
                tick=2,
                agent_id="p1",
                visible_players=(PlayerView(id="p2", room="ADMIN", action=None),),
            ),
            memory=store,
        )
        ingest_packet(
            packet=_packet(
                tick=2,
                agent_id="p1",
                visible_players=(PlayerView(id="p4", room="ADMIN", action=None),),
            ),
            memory=store,
        )

        observed_ids = [
            e.observation_id
            for e in store.recent(since_tick=0)
            if e.provenance == PROVENANCE_OBSERVED
        ]
        # First call: self_state(0), saw_player(1). Second call CONTINUES: 2, 3.
        assert observed_ids == ["p1:2:0", "p1:2:1", "p1:2:2", "p1:2:3"]
        assert len(observed_ids) == len(set(observed_ids))


class TestDuplicateIdGuard:
    def test_duplicate_non_none_id_append_raises(self) -> None:
        store = MemoryStore()
        store.append(
            EpisodicEvent(
                tick=1,
                type="saw_player",
                payload={"player_id": "p2", "room": "ADMIN", "action": None},
                provenance=PROVENANCE_OBSERVED,
                observation_id="p1:1:0",
            )
        )
        with pytest.raises(ValueError, match="duplicate observation id"):
            store.append(
                EpisodicEvent(
                    tick=1,
                    type="saw_player",
                    payload={"player_id": "p4", "room": "ADMIN", "action": None},
                    provenance=PROVENANCE_OBSERVED,
                    observation_id="p1:1:0",
                )
            )

    def test_repeated_none_ids_never_trip_the_guard(self) -> None:
        # A None id means "not a first-hand citable observation" and never enters
        # the uniqueness set, so any number of None-id rows append freely.
        store = MemoryStore()
        for _ in range(3):
            store.append(
                EpisodicEvent(
                    tick=1,
                    type="global_status",
                    payload={},
                    provenance=PROVENANCE_INFERRED,
                    observation_id=None,
                )
            )
        assert len(store) == 3


class TestReportedTestimonyCarriesNoId:
    def test_absorbed_testimony_row_has_no_observation_id(self) -> None:
        # Reported rows are meeting content, not first-hand perception: they carry
        # no observation id by design (only ``ingest_packet`` stamps ids).
        memory = AgentMemory()
        ingest_packet(
            packet=_packet(
                tick=20,
                agent_id="p1",
                visible_players=(
                    PlayerView(id="p3", room="ADMIN", action=None),
                    PlayerView(id="p5", room="ADMIN", action=None),
                ),
            ),
            memory=memory.episodic,
        )
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(
                    speaker="p3",
                    kind="saw_player",
                    subject="p5",
                    from_tick=12,
                    to_tick=12,
                    room="ELECTRICAL",
                ),
            ),
        )

        reported = [
            e
            for e in memory.episodic.recent(since_tick=0)
            if e.type == EVENT_REPORTED_TESTIMONY
        ]
        assert len(reported) == 1
        assert reported[0].observation_id is None


class TestDeriveObservationId:
    def test_scheme_is_a_pure_function(self) -> None:
        # No RNG, no hash, no floats: a pure function of the three coordinates.
        assert derive_observation_id(agent_id="p3", tick=410, seq=2) == "p3:410:2"
        assert derive_observation_id(agent_id="p3", tick=410, seq=2) == "p3:410:2"


def _lever_memory() -> AgentMemory:
    """A rendered memory with one first-hand sighting, body, and heard event.

    Ingested at tick 5 for agent ``p1`` so the id-stamped rows are, in append
    order: self_state(seq 0), saw_player p2(1), saw_player p4(2), saw_body(3),
    heard(4). A meeting accusation gives ``p2`` a rendered belief line, and a
    reported accusation gives a reported (no-id) observation line -- so the render
    carries a belief line, a role line, and a reported line that must all stay
    un-prefixed when the lever is ON.
    """

    memory = AgentMemory()
    ingest_packet(
        packet=_packet(
            tick=5,
            agent_id="p1",
            room="CAFETERIA",
            visible_players=(
                PlayerView(id="p2", room="ADMIN", action="task"),
                PlayerView(id="p4", room="ELECTRICAL", action=None),
            ),
            visible_bodies=(BodyView(id="p3-body", room="ELECTRICAL", victim_id="p3"),),
            audible_events=(AudibleEvent(kind="sabotage_alarm", room="STORAGE"),),
        ),
        memory=memory.episodic,
    )
    absorb_meeting_evidence(memory, accused=["p2"])
    absorb_reported_testimony(
        memory,
        statements=(ReportedStatement(speaker="p2", kind="accusation", subject="p4"),),
    )
    return memory


class TestObservationIdRenderLever:
    def test_env_is_ignored_and_ids_always_render(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # UNCONDITIONAL since Task 16.17: env=None (unset), env={}, an explicit
        # "0", and an explicit "1" all render IDENTICALLY, and every render carries
        # the ``[obs `` prefix -- the lever ignores its env argument.
        monkeypatch.delenv(ENV_OBSERVATION_ID_RENDERING, raising=False)
        memory = _lever_memory()
        default = render_for_prompt(memory)
        empty = render_for_prompt(memory, env={})
        zero = render_for_prompt(memory, env={ENV_OBSERVATION_ID_RENDERING: "0"})
        one = render_for_prompt(memory, env={ENV_OBSERVATION_ID_RENDERING: "1"})
        assert default == empty == zero == one
        assert "[obs " in default

    def test_prefixes_each_first_hand_observation_with_its_id(self) -> None:
        # The fold puts ``[obs {agent}:{tick}:{seq}]`` into each first-hand
        # observation line with the EXACT id of its source event; the belief line,
        # the role line, and the reported-testimony line carry none.
        memory = _lever_memory()
        rendered = render_for_prompt(memory)
        assert "[obs p1:5:1] [tick 5] You saw p2 task in ADMIN." in rendered
        assert "[obs p1:5:2] [tick 5] You saw p4 in ELECTRICAL." in rendered
        assert (
            "[obs p1:5:3] [tick 5] You discovered p3's body in ELECTRICAL." in rendered
        )
        assert (
            "[obs p1:5:4] [tick 5] You heard a sabotage alarm in STORAGE." in rendered
        )
        # Exactly the four first-hand observations are prefixed -- the belief,
        # role, and reported-testimony lines are not.
        assert rendered.count("[obs ") == 4
        assert "## Your role: CREWMATE" in rendered
        assert "## Your current beliefs:" in rendered
        assert "[meeting] CLAIM by p2 (unverified): accused p4." in rendered

    def test_resolver_is_unconditionally_on(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Graduated to unconditional at Task 16.17 (mirrors the 16.4 lever's
        # graduation): the resolver ignores its env and always returns True -- a
        # bare mapping, an explicit "0", junk, the truthy tokens, and the ambient
        # process environment all read ON.
        assert observation_id_rendering_enabled() is True
        assert observation_id_rendering_enabled({}) is True
        monkeypatch.delenv(ENV_OBSERVATION_ID_RENDERING, raising=False)
        assert observation_id_rendering_enabled() is True
        for value in ("0", "garbage", "1", "true", "on", ""):
            assert (
                observation_id_rendering_enabled({ENV_OBSERVATION_ID_RENDERING: value})
                is True
            )

    def test_ids_survive_a_tight_token_budget_shed(self) -> None:
        # The id is folded BEFORE the salience sort and budget shed, so a surviving
        # line keeps its ORIGINAL id even when lower-salience lines are dropped. The
        # highest-salience body line (salience 100) survives with its id under a
        # tight budget; some lower-salience observations are shed.
        memory = _lever_memory()
        full = render_for_prompt(memory)
        assert full.count("[obs ") == 4
        tight = render_for_prompt(memory, token_budget=70)
        assert 0 < tight.count("[obs ") < 4
        assert "[obs p1:5:3] [tick 5] You discovered p3's body in ELECTRICAL." in tight


_REPO_ROOT = Path(__file__).resolve().parents[2]
# The two committed baseline-3 sets; the first 2 seeds of each keep the twin
# walk ~1 min while pinning against the real corpus (Task 16.5 determinism DoD).
_COMMITTED_SETS = ("4p1i", "9p2i")

# {(set_name, seed, meeting_id, agent_id): participant.observation_ids}
_IdMap = dict[tuple[str, int, str, str], tuple[str, ...]]


class TestObservationIdsAreReconstructionStable:
    """Two reconstructions of a committed replay mint byte-identical ids (Task
    16.5, C8 determinism DoD).

    The ``{agent_id}:{tick}:{seq}`` scheme is a pure function of the append
    history and carries no RNG / hash / float, so walking the SAME committed
    replay twice through the real reconstruction pipeline must assign every
    participant the identical id tuple. The reuse surface is the 16.4 precedent
    (tests/agents/test_beliefs_hard_evidence_gate.py):
    :func:`tests.meetings.test_prompt_byte_golden.walk_replay_meetings` re-seeds,
    re-walks and rebuilds each agent's memory in lockstep, then threads
    ``observation_ids_for_meeting`` onto every reconstructed
    :class:`~meetings.manager.MeetingParticipant` via
    :func:`orchestrator.game._build_participants`. A SMALL deterministic subset
    (first 2 seeds of each set) is walked TWICE; the class-scoped fixture runs
    each walk exactly once.
    """

    @staticmethod
    def _walk_ids() -> _IdMap:
        from engine.world import load_canonical_map
        from tests.meetings.test_prompt_byte_golden import (
            _canonical_renderers,  # noqa: PLC2701
            _seed_paths,  # noqa: PLC2701
            walk_replay_meetings,
        )

        game_map = load_canonical_map()
        renderers = _canonical_renderers()
        ids: _IdMap = {}
        for set_name in _COMMITTED_SETS:
            set_dir = _REPO_ROOT / "replays" / "samples" / set_name
            for path in _seed_paths(set_dir)[:2]:
                for meeting in walk_replay_meetings(
                    path, game_map=game_map, renderers_for_set=renderers
                ):
                    for participant in meeting.participants:
                        key = (
                            set_name,
                            meeting.seed,
                            meeting.meeting_id,
                            participant.agent_id,
                        )
                        ids[key] = participant.observation_ids
        return ids

    @pytest.fixture(scope="class")
    def walks(self) -> tuple[_IdMap, _IdMap]:
        # Two full reconstructions; each walk runs once for the whole class.
        return (self._walk_ids(), self._walk_ids())

    def test_two_walks_assign_identical_ids(self, walks: tuple[_IdMap, _IdMap]) -> None:
        first, second = walks
        assert first, "the committed subset produced no reconstructed participants"
        # Two reconstructions regenerate every participant's id tuple byte-for-byte.
        assert first == second

    def test_ids_are_well_shaped_nonempty_and_unique(
        self, walks: tuple[_IdMap, _IdMap]
    ) -> None:
        first, _ = walks
        for (set_name, seed, meeting_id, agent_id), observation_ids in first.items():
            where = f"{set_name} seed {seed} {meeting_id} {agent_id}"
            # Non-empty for every living participant: the id-stamped self_state
            # row is always present by meeting time.
            assert observation_ids, f"{where}: participant cited no observation"
            # Every id is the participant's OWN {agent_id}:{tick}:{seq}.
            pattern = re.compile(rf"^{re.escape(agent_id)}:\d+:\d+$")
            for observation_id in observation_ids:
                assert pattern.match(observation_id), (
                    f"{where}: id {observation_id!r} is not {agent_id}:{{tick}}:{{seq}}"
                )
            # Unique within the participant's tuple (the store's append-time
            # duplicate-id guard enforces uniqueness within an agent's memory).
            assert len(observation_ids) == len(set(observation_ids)), (
                f"{where}: duplicate ids in {observation_ids!r}"
            )


# --------------------------------------------------------------------------- #
# The read path: recent() locates its window by bisection                     #
# --------------------------------------------------------------------------- #

# Legal append sequences the equivalence property draws from: ticks are sorted
# on the way in (``append`` requires non-decreasing), the small tick range makes
# duplicates and gaps common, and the empty log is in range.
_WINDOW_EXAMPLES = 1_000
_LOG_TICKS = st.lists(st.integers(min_value=0, max_value=30), max_size=24)
_SINCE_TICK = st.integers(min_value=-9, max_value=39)


def _row(*, tick: int, index: int = 0) -> EpisodicEvent:
    """A minimal observed row; only its tick and identity matter to a window."""

    return EpisodicEvent(
        tick=tick,
        type="saw_player",
        payload={"index": index},
        provenance=PROVENANCE_OBSERVED,
    )


def _linear_recent(
    events: tuple[EpisodicEvent, ...], since_tick: int
) -> tuple[EpisodicEvent, ...]:
    """The reference answer: filter the whole log, the shape ``recent`` had."""

    return tuple(event for event in events if event.tick >= since_tick)


def _store_of(ticks: list[int]) -> tuple[MemoryStore, tuple[EpisodicEvent, ...]]:
    """A store filled with one legal (tick-sorted) append sequence, and its rows."""

    events = tuple(_row(tick=tick, index=index) for index, tick in enumerate(ticks))
    store = MemoryStore()
    for event in events:
        store.append(event)
    return store, events


def _tick_index(store: MemoryStore) -> list[int]:
    """The store's private bisection key, read to pin it against the log itself."""

    return store._ticks  # noqa: SLF001


class TestRecentMatchesTheLinearReference:
    """The bisected window answers exactly what the full-log filter answered.

    ``append`` keeps ticks non-decreasing, so ``tick >= since_tick`` always
    selects a suffix — the invariant that lets one bisection replace the scan.
    The property runs over generated legal logs (duplicate ticks, gaps, the
    empty log) and window bounds that include negative and past-the-end values.
    """

    @settings(max_examples=_WINDOW_EXAMPLES)
    @given(ticks=_LOG_TICKS, since_tick=_SINCE_TICK)
    def test_generated_logs_agree_event_for_event(
        self, ticks: list[int], since_tick: int
    ) -> None:
        store, events = _store_of(sorted(ticks))
        assert store.recent(since_tick=since_tick) == _linear_recent(events, since_tick)

    def test_all_three_window_shapes_are_covered(self) -> None:
        # The property above is only worth its examples if they are not all one
        # trivial shape: over the same generators, the three shapes a window can
        # take (whole log, proper suffix, empty) all occur.
        rng = random.Random(2019)
        shapes: set[str] = set()
        for _ in range(_WINDOW_EXAMPLES):
            ticks = sorted(rng.randint(0, 30) for _ in range(rng.randint(0, 24)))
            store, events = _store_of(ticks)
            window = store.recent(since_tick=rng.randint(-9, 39))
            if not events:
                continue
            if not window:
                shapes.add("empty")
            elif len(window) == len(events):
                shapes.add("whole")
            else:
                shapes.add("partial")
        assert shapes == {"whole", "partial", "empty"}

    def test_the_reference_disagrees_with_a_broken_window(self) -> None:
        # The comparison bites: an off-by-one window (the failure mode a
        # bisect_right / bisect_left slip would produce) is caught by it.
        events = (_row(tick=1), _row(tick=4, index=1), _row(tick=4, index=2))
        store = MemoryStore()
        for event in events:
            store.append(event)
        assert store.recent(since_tick=4) == _linear_recent(events, 4)
        assert store.recent(since_tick=4) != events[2:]


class TestRecentBisectsExactlyOnce:
    def test_one_bisect_left_call_per_read(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Structural: the window is located, not scanned — one bisection per
        # call, whatever the window's shape, and none anywhere else.
        calls: list[int] = []

        def counting(sequence: list[int], value: int) -> int:
            calls.append(value)
            return bisect_left(sequence, value)

        monkeypatch.setattr(episodic, "bisect_left", counting)
        store = MemoryStore()
        for tick in (0, 0, 3, 9):
            store.append(_row(tick=tick))
        assert calls == []  # appends bisect nothing
        for index, since_tick in enumerate((0, 3, 99, -1)):
            store.recent(since_tick=since_tick)
            assert len(calls) == index + 1
        assert calls == [0, 3, 99, -1]


class TestWholeLogCacheIsInvalidatedOnWrite:
    """The cached whole-log tuple never outlives the write that follows it."""

    def test_a_write_between_reads_lengthens_the_window(self) -> None:
        store = MemoryStore()
        first = _row(tick=1)
        store.append(first)
        before = store.recent(since_tick=0)
        second = _row(tick=4, index=1)
        store.append(second)
        after = store.recent(since_tick=0)
        assert before == (first,)
        assert after == (first, second)

    def test_reads_without_a_write_reuse_one_tuple(self) -> None:
        # It is a cache, not a rebuild: the same object until the next append,
        # and a different one after it.
        store = MemoryStore()
        store.append(_row(tick=1))
        cached = store.recent(since_tick=0)
        assert store.recent(since_tick=0) is cached
        store.append(_row(tick=2, index=1))
        assert store.recent(since_tick=0) is not cached

    def test_a_handed_out_window_is_a_snapshot(self) -> None:
        # A caller holding an earlier window keeps the log as it was; the cache
        # is replaced, never mutated.
        store = MemoryStore()
        first = _row(tick=1)
        store.append(first)
        held = store.recent(since_tick=0)
        store.append(_row(tick=2, index=1))
        assert held == (first,)

    def test_a_rejected_out_of_order_append_changes_nothing(self) -> None:
        store = MemoryStore()
        rows = (_row(tick=3), _row(tick=7, index=1))
        for row in rows:
            store.append(row)
        # Warm the cache first, so the post-rejection read is the SAME object:
        # an invalidation that ran before the guard would rebuild an equal tuple
        # and slip past an equality-only check.
        warmed = store.recent(since_tick=0)
        with pytest.raises(ValueError, match="non-decreasing"):
            store.append(_row(tick=2, index=2))
        assert len(store) == 2
        assert store.recent(since_tick=0) is warmed
        assert warmed == rows
        assert _tick_index(store) == [3, 7]
        # The index is still aligned with the log, so a later legal append
        # windows correctly rather than off by the rejected row.
        late = _row(tick=12, index=3)
        store.append(late)
        assert store.recent(since_tick=12) == (late,)
        assert store.recent(since_tick=7) == (rows[1], late)

    def test_a_rejected_duplicate_id_append_changes_nothing(self) -> None:
        store = MemoryStore()
        first = EpisodicEvent(
            tick=2,
            type="saw_player",
            payload={"index": 0},
            provenance=PROVENANCE_OBSERVED,
            observation_id=derive_observation_id(agent_id="p1", tick=2, seq=0),
        )
        store.append(first)
        warmed = store.recent(since_tick=0)
        with pytest.raises(ValueError, match="duplicate observation id"):
            store.append(first)
        assert len(store) == 1
        # Same object, not merely an equal one: the guard raised before any
        # derived view moved.
        assert store.recent(since_tick=0) is warmed
        assert warmed == (first,)
        assert _tick_index(store) == [2]
