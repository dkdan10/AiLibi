"""The meeting training table — the surrogate's supervised substrate (Task 15.11).

For every committed meeting this module reconstructs, OFFLINE (LLM-free,
replay-deterministic), the per-(meeting, voter) feature rows the ballot surrogate
(Task 15.13) trains on and every meeting model is judged against
(:mod:`training.surrogate.fidelity`). It joins the reconstructed features to the
ACTUAL recorded ballots ``{voter, target, confidence, primary_reason_id}`` and to
roles ground truth (audits/post-phase-14-ML-training-signal.md §5.4, §7.2).

Reconstruction recipe (MIRRORS ``eval.funnel._walk_game`` /
``api.replay_loader._walk`` — the loader is API-tier and carries serving concerns,
so the re-seed / advance / apply / hash-verify loop is mirrored here, NOT imported):
re-seed each game from its roster, feed the recorded actions through
:func:`engine.tick.advance_tick`, verify every per-tick ``state_hash`` and each
meeting row's ``state_hash_before`` / ``state_hash_after``, and on a MEETING tick
rebuild the :class:`~meetings.schemas.MeetingResult` and apply it via
:func:`orchestrator.game.apply_meeting_result`. A corrupted or drifted set fails
loud (:class:`MeetingTableReconstructionError`) rather than silently mis-building
(AGENTS.md "no silent fallbacks").

The single biggest feature over FO-6's six raw counts
(``experiments/lab/ml_spike/fo6_learned_vote_surrogate.py``) is the **pre-meeting
belief-fold rendered suspicion**. The belief fold in ``agents/memory/beliefs.py`` is
deterministic over recorded events and needs no LLM;
:func:`meetings.manager.extract_belief_evidence` re-derives each meeting's public
evidence (accused / corroborated / contradicted / testimony — the
``derive_belief_evidence`` derivation, roster read off ``result.ballots``,
``meetings/manager.py``). Folding that evidence over PRIOR meetings through the
real :func:`agents.memory.beliefs.apply_meeting_evidence_rules` (the exact persistent
post-meeting absorb the orchestrator runs, ``phase=None``) reconstructs the
per-voter cross-meeting suspicion accumulator the LLM votes on — WITHOUT this
meeting's transcript (a training-time surrogate has no LLM, hence no current
transcript), so it is the honest pre-meeting graph. The perception-time hard pins
(witnessed vent → the ``vent_sighting`` flag column; kill-proximity → the
``seen_at_kill`` column) are surfaced as their own first-class feature columns
rather than folded into the single suspicion scalar, so a linear/tree surrogate can
weight each channel independently (see the module ``## Decisions`` in the PR).

Row grain is one row per (meeting, voter); the roster is read off ``result.ballots``
(every living participant casts exactly one ballot — ``meetings/manager.py``), which
fixes the candidate universe. Each row carries the voter's per-candidate feature
view (:class:`CandidateFeatures`, one per living player) plus the voter's actual
ballot. EVERY recorded ballot joins exactly one row (100% join rate, asserted by
:func:`build_meeting_table` against the set's assembled tournament report).

The builder takes ANY replay-set directory and reads a committed ``splits.json``
when present (:func:`load_splits`), so it runs identically on the 15.12 corpus.

Pure and offline: no network, no ``AILIBI_*`` env, no LLM call; the only engine
imports are the reconstruction path (seeder + ``advance_tick`` + the orchestrator's
``apply_meeting_result``), mirroring the committed 15.3 / 15.8 folds.

Public surface (stable — downstream tasks import these): :class:`MeetingTableRow`,
:class:`CandidateFeatures`, :class:`MeetingTable`, :class:`SurrogateSplits`,
:func:`build_meeting_table`, :func:`load_splits`.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError

from agents.memory.beliefs import BeliefState, apply_meeting_evidence_rules
from engine.actions import Action
from engine.entities import PlayerId, Role, RoomId
from engine.events import (
    KilledEvent,
    MeetingTriggeredEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.tick import advance_tick
from engine.world import Map, WorldState, load_canonical_map
from eval.validity import (
    assemble_tournament_report,
    resolve_roster_knobs,
    roles_by_seed,
    seeds_on_disk,
)
from meetings.manager import extract_belief_evidence
from meetings.schemas import ContradictionRef, MeetingOutcome, MeetingResult
from meetings.transcript import MeetingTriggerKind, is_weak_contradiction
from orchestrator.game import apply_meeting_result
from orchestrator.replay import (
    MeetingReplayEntry,
    ReplayEntry,
    _state_hash,
    read_all_entries,
)
from orchestrator.seeder import seed_initial_state

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)

# The kill-scene co-presence window (FO-6 parity: ``0 <= tick - kill_tick <= 2``).
# A candidate co-located in the kill room within this many ticks of a resolved kill
# is "seen at the kill" — the strongest LLM-free physical placement.
SEEN_AT_KILL_WINDOW_TICKS: int = 2

# The committed ``splits.json`` filename the builder reads when present (Task 15.12
# writes it; the baseline sets ship none, so folds are derived by the harness).
SPLITS_FILENAME: str = "splits.json"


class MeetingTableReconstructionError(RuntimeError):
    """A recorded state hash did not reconstruct — the set is corrupt/drifted.

    Raised during the walk when a per-tick ``state_hash`` or a meeting row's
    ``state_hash_before`` / ``state_hash_after`` disagrees with the engine
    reconstruction, so a drifted or corrupted replay set fails loud rather than
    silently building a wrong table (AGENTS.md "no silent fallbacks"). Mirrors
    :class:`eval.funnel.FunnelReconstructionError`.
    """


class CandidateFeatures(BaseModel):
    """One living candidate's reconstructed features, from a voter's view (frozen).

    All columns derive OFFLINE from the committed bytes. The suspicion/trust pair is
    the voter-specific pre-meeting belief-fold state (folded over PRIOR meetings'
    public evidence; the candidate's OWN row is never held about the voter, so a
    ``is_self`` candidate reads the neutral 0.5 prior). The contradiction-flag
    counts (``strong_flags`` / ``weak_flags`` / ``vent_flags``), sighting counts
    (``witnessed`` / ``isolation``), ``seen_at_kill``, ``body_proximity``,
    ``is_reporter``, ``task_submissions`` and ``move_count`` are voter-INDEPENDENT
    meeting/window facts (identical across a meeting's voters), so a meeting-level
    ranker (FO-6) reads them off any row. ``is_ejected`` / ``is_impostor`` are labels
    (roles ground truth), never predictive inputs.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    candidate: PlayerId
    role: Role
    is_self: bool
    is_impostor: bool
    is_ejected: bool
    is_reporter: bool
    # Voter-specific pre-meeting belief-fold state (prior meetings only).
    belief_suspicion: float
    belief_trust: float
    # THIS meeting's contradiction-flag structure naming the candidate.
    strong_flags: int
    weak_flags: int
    vent_flags: int
    # Physical reconstruction over the pre-meeting play window (FO-6 parity).
    witnessed: int
    isolation: int
    seen_at_kill: bool
    # VOTER-LOCAL role-proving eyewitness pins (Codex review): this row's VOTER
    # personally witnessed the candidate kill (+1.0) / vent (+0.5) — the exact
    # belief-store pins, exposed only to the witness, never the co-presence proxy.
    witnessed_kill: bool
    witnessed_vent: bool
    body_proximity: bool
    # Cross-game cadence signals.
    task_submissions: int
    move_count: int


class MeetingTableRow(BaseModel):
    """One (meeting, voter) training row (Task 15.11 public type; frozen).

    Carries the meeting/voter identity, the voter's ACTUAL recorded ballot (the
    join target — ``ballot_target`` / ``ballot_confidence`` /
    ``ballot_primary_reason_id``), the meeting-level outcome + ejected target
    (labels), and the voter's per-candidate feature view (:class:`CandidateFeatures`,
    one per LIVING player incl. the voter, sorted by id). ``candidates`` is the full
    living roster so a meeting's candidate set is identical across its voters, which
    the fidelity harness reads off any row. Signature is stable per the task
    contract.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: int
    game_id: str
    meeting_id: str
    meeting_index: int
    tick: int
    trigger: MeetingTriggerKind
    reporter: PlayerId
    outcome: MeetingOutcome
    ejected_player_id: PlayerId | None
    voter: PlayerId
    voter_role: Role
    voter_is_impostor: bool
    ballot_target: PlayerId | str
    ballot_confidence: float
    ballot_primary_reason_id: str | None
    candidates: tuple[CandidateFeatures, ...]


class SurrogateSplits(BaseModel):
    """A committed by-GAME train/val/test split over a replay set (frozen).

    Read from ``splits.json`` when present (:func:`load_splits`). The lists hold
    game SEEDS (never meeting ids — by-game CV is the anti-leakage discipline,
    §5.5). Task 15.12 commits this alongside the corpus; the baseline sets ship
    none, so the fidelity harness derives K folds itself.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    train: tuple[int, ...]
    val: tuple[int, ...] = ()
    test: tuple[int, ...] = ()


class MeetingTable(BaseModel):
    """The reconstructed meeting training table over one replay set (frozen).

    ``rows`` is every (meeting, voter) row, sorted deterministically (by seed,
    meeting_index, voter). The count aggregates are DERIVED from the set's assembled
    tournament report (:func:`eval.validity.assemble_tournament_report`), not
    hard-coded, and asserted equal to the reconstruction — the sets are baseline 3
    by this task's dependency order. ``model_dump_json()`` is byte-stable across
    rebuilds (the determinism pin).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    replay_set_dir: str
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    games_total: int
    meetings_total: int
    ejections_total: int
    skips_total: int
    ballots_total: int
    splits: SurrogateSplits | None
    rows: tuple[MeetingTableRow, ...]

    def game_seeds(self) -> tuple[int, ...]:
        """The distinct game seeds present in the table, sorted."""

        return tuple(sorted({row.seed for row in self.rows}))


def load_splits(sample_dir: Path) -> SurrogateSplits | None:
    """Read a committed ``splits.json`` from ``sample_dir`` when present.

    Returns ``None`` when the file is absent (the baseline sets). A present but
    malformed file raises (fail loud — a typo'd split silently ignored would leak
    games across folds). The 15.12 corpus commits this; the schema is
    :class:`SurrogateSplits`.
    """

    path = sample_dir / SPLITS_FILENAME
    if not path.is_file():
        return None
    try:
        return SurrogateSplits.model_validate_json(path.read_text())
    except ValidationError as exc:
        raise ValueError(f"malformed {path}: {exc}") from exc


def _deserialize_actions(raw_actions: Sequence[Mapping[str, object]]) -> list[Action]:
    return [_ACTION_ADAPTER.validate_python(dict(raw)) for raw in raw_actions]


def _meeting_result_from_entry(entry: MeetingReplayEntry) -> MeetingResult:
    return MeetingResult(
        meeting_id=entry.meeting_id,
        triggered_by=entry.triggered_by,
        trigger_tick=entry.tick,
        outcome=entry.outcome,
        ejected_player_id=entry.ejected_player_id,
        ballots=entry.ballots,
        contradictions=entry.contradictions,
        transcript=entry.transcript,
    )


def _flag_counts(
    contradictions: Sequence[ContradictionRef],
) -> dict[PlayerId, tuple[int, int, int]]:
    """Per-subject ``(strong, weak, vent)`` flag counts for one meeting.

    ``vent_sighting`` (Task 15.4, the new role-proving vent flag) is counted in its
    OWN band — it is always strong but is the load-bearing LLM-free signal, so the
    surrogate sees it separately from an alibi-based strong flag. A weak
    ``alibi_*`` flag (:func:`meetings.transcript.is_weak_contradiction`) is the
    down-weighted band; every other flag is strong.
    """

    counts: dict[PlayerId, tuple[int, int, int]] = defaultdict(lambda: (0, 0, 0))
    for flag in contradictions:
        for subject in flag.subjects:
            strong, weak, vent = counts[subject]
            if flag.kind == "vent_sighting":
                counts[subject] = (strong, weak, vent + 1)
            elif is_weak_contradiction(flag):
                counts[subject] = (strong, weak + 1, vent)
            else:
                counts[subject] = (strong + 1, weak, vent)
    return counts


class _WindowStats:
    """Per-player physical accumulators over the current inter-meeting window.

    Sighting/kill-proximity/body-proximity reset each meeting (FO-6 "recent
    activity" parity); ``task_submissions`` / ``moves`` accumulate over the whole
    game (a player who has completed no tasks all game is a game-long cadence
    signal).

    ``witnessed_kill`` / ``witnessed_vent`` are the EXACT role-proving eyewitness
    pins from ``KilledEvent`` / vent-event witnesses (Codex review), mapping a
    KILLER/VENTER to the set of CREW WITNESSES who saw the act. Production only
    stamps ``action="kill"`` / ``"vent"`` for the WITNESSING agent before that
    agent's own belief update, so the pin is VOTER-LOCAL: exposed only for a row
    whose voter is in the witness set. Both are persistent (role-proving knowledge
    the crew never unlearns, mirroring the +1.0 / +0.5 belief pins the store folds),
    so they do NOT reset. All updates read only reconstructed engine truth.
    """

    def __init__(self) -> None:
        self.witnessed: dict[PlayerId, int] = defaultdict(int)
        self.isolation: dict[PlayerId, int] = defaultdict(int)
        self.seen_at_kill: dict[PlayerId, bool] = defaultdict(bool)
        self.witnessed_kill: dict[PlayerId, set[PlayerId]] = defaultdict(set)
        self.witnessed_vent: dict[PlayerId, set[PlayerId]] = defaultdict(set)
        self.body_proximity: dict[PlayerId, bool] = defaultdict(bool)
        self.task_submissions: dict[PlayerId, int] = defaultdict(int)
        self.moves: dict[PlayerId, int] = defaultdict(int)
        self._pending_kills: list[tuple[int, RoomId]] = []

    def count_submissions(self, raw_actions: Sequence[Mapping[str, object]]) -> None:
        for raw in raw_actions:
            actor = raw.get("actor")
            if not isinstance(actor, str):
                continue
            if raw.get("type") == "do_task":
                self.task_submissions[actor] += 1
            elif raw.get("type") == "move":
                self.moves[actor] += 1

    def absorb_tick(
        self,
        state: WorldState,
        events: Sequence[object],
        roles: Mapping[PlayerId, Role],
    ) -> None:
        by_room: dict[RoomId, list[PlayerId]] = {}
        for pid, player in state.players.items():
            if player.alive and not player.in_vent:
                by_room.setdefault(player.room, []).append(pid)
        for occupants in by_room.values():
            if len(occupants) >= 2:
                for pid in occupants:
                    self.witnessed[pid] += 1
            else:
                self.isolation[occupants[0]] += 1
        for event in events:
            if isinstance(event, KilledEvent):
                self._pending_kills.append((event.tick, event.room))
                # The EXACT witnessed-kill pin (Codex review): production stamps
                # ``action="kill"`` for the killer's CREW witnesses, who each take
                # the +1.0 hard pin in their OWN belief before voting
                # (agents/memory/beliefs.py). Read the witness set straight off
                # ``event.actor`` + ``event.witnesses`` (crew only — a
                # fellow-impostor witness generates no crew evidence, §4.7); it is
                # voter-local, never the co-presence proxy, so a witnessed killer who
                # moved or was alone is not missed and a bystander is never
                # mismarked, and the pin does not leak to non-witness voters.
                crew_witnesses = {
                    w for w in event.witnesses if roles.get(w) == "CREWMATE"
                }
                if crew_witnesses:
                    self.witnessed_kill[event.actor].update(crew_witnesses)
            elif isinstance(event, (VentEnteredEvent, VentExitedEvent)):
                # The witnessed-VENT pin (Codex review): a crew member who SAW an
                # impostor vent takes the +0.5 role-proving pin at perception
                # (VENTING_SUSPICION_DELTA), persisting into the pre-meeting graph
                # even when no grounded ``vent_sighting`` contradiction is spoken.
                # Witnesses = the source-room ∪ destination-room witness sets the
                # engine records (:mod:`eval.funnel`), crew only, voter-local.
                vent_witnesses = {
                    w
                    for w in (*event.source_witnesses, *event.destination_witnesses)
                    if roles.get(w) == "CREWMATE"
                }
                if vent_witnesses:
                    self.witnessed_vent[event.actor].update(vent_witnesses)
        for kill_tick, kill_room in self._pending_kills:
            if 0 <= state.tick - kill_tick <= SEEN_AT_KILL_WINDOW_TICKS:
                occupants = by_room.get(kill_room, [])
                if len(occupants) >= 2:
                    for pid in occupants:
                        self.seen_at_kill[pid] = True
        for body in state.bodies.values():
            for pid in by_room.get(body.room, []):
                if pid != body.player_id:
                    self.body_proximity[pid] = True

    def reset_window(self) -> None:
        self.witnessed.clear()
        self.isolation.clear()
        self.seen_at_kill.clear()
        self.body_proximity.clear()
        self._pending_kills.clear()


def _fold_meeting_into_beliefs(
    beliefs: dict[PlayerId, BeliefState],
    *,
    result: MeetingResult,
    trigger_kind: MeetingTriggerKind,
    roles: Mapping[PlayerId, Role],
    roster: frozenset[PlayerId],
    voters: Sequence[PlayerId],
) -> None:
    """Fold one resolved meeting's public evidence into each voter's beliefs.

    The EXACT persistent post-meeting absorb the orchestrator runs
    (:func:`agents.memory.store.absorb_meeting_evidence` →
    :func:`agents.memory.beliefs.apply_meeting_evidence_rules` with ``phase=None``):
    one :func:`meetings.manager.extract_belief_evidence` reduction (roster off
    ``result.ballots``), then the composed accusation-bump / Rule-3 corroboration /
    Rule-5 decay fold per living voter, so suspicion carries into the NEXT meeting's
    pre-meeting graph. An impostor voter's fold drops fellow-impostor subjects (the
    §4.7 firewall); ``roster`` is the full co-spawned player set (the store's
    ``_known_roster_ids`` is a no-op on real-player data — every player co-spawns).
    """

    evidence = extract_belief_evidence(result, trigger_kind=trigger_kind)
    impostor_ids = frozenset(pid for pid, role in roles.items() if role == "IMPOSTOR")
    for voter in voters:
        teammates = (
            tuple(sorted(impostor_ids - {voter}))
            if roles.get(voter) == "IMPOSTOR"
            else ()
        )
        beliefs[voter] = apply_meeting_evidence_rules(
            beliefs[voter],
            own_id=voter,
            accused=evidence.accused,
            corroborated=evidence.corroborated,
            contradicted=evidence.contradicted,
            fellow_impostor_ids=teammates,
            roster=roster,
        )


def _candidate_features(
    candidate: PlayerId,
    *,
    voter: PlayerId,
    beliefs: BeliefState,
    roles: Mapping[PlayerId, Role],
    reporter: PlayerId,
    ejected: PlayerId | None,
    flags: Mapping[PlayerId, tuple[int, int, int]],
    stats: _WindowStats,
) -> CandidateFeatures:
    strong, weak, vent = flags.get(candidate, (0, 0, 0))
    belief = beliefs.view(candidate)
    return CandidateFeatures(
        candidate=candidate,
        role=roles[candidate],
        is_self=candidate == voter,
        is_impostor=roles[candidate] == "IMPOSTOR",
        is_ejected=ejected is not None and candidate == ejected,
        is_reporter=candidate == reporter,
        belief_suspicion=belief.suspicion,
        belief_trust=belief.trust,
        strong_flags=strong,
        weak_flags=weak,
        vent_flags=vent,
        witnessed=stats.witnessed.get(candidate, 0),
        isolation=stats.isolation.get(candidate, 0),
        seen_at_kill=stats.seen_at_kill.get(candidate, False),
        # Voter-local: the pin is exposed only when THIS row's voter is in the
        # candidate's witness set (production stamps the act only for its witnesses).
        witnessed_kill=voter in stats.witnessed_kill.get(candidate, set()),
        witnessed_vent=voter in stats.witnessed_vent.get(candidate, set()),
        body_proximity=stats.body_proximity.get(candidate, False),
        task_submissions=stats.task_submissions.get(candidate, 0),
        move_count=stats.moves.get(candidate, 0),
    )


def _walk_game(
    replay_path: Path,
    *,
    seed: int,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    roles: Mapping[PlayerId, Role],
    game_map: Map,
) -> list[MeetingTableRow]:
    """Re-seed + replay one game into its per-(meeting, voter) rows.

    Mirrors :func:`eval.funnel._walk_game`: re-seed, advance every recorded tick
    with state-hash verification, and on a MEETING tick build the rows from the
    PRE-meeting belief state + window physical stats, then fold the meeting into the
    beliefs and apply it to the engine (verifying ``state_hash_after``) before
    resuming. A meeting row missing from the replay fails loud rather than
    under-building.
    """

    game_id = f"headless-seed-{seed}"
    entries = read_all_entries(replay_path)
    tick_entries = [entry for entry in entries if isinstance(entry, ReplayEntry)]
    meeting_by_tick: dict[int, MeetingReplayEntry] = {
        entry.tick: entry for entry in entries if isinstance(entry, MeetingReplayEntry)
    }

    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    roster = frozenset(state.players)
    beliefs: dict[PlayerId, BeliefState] = {pid: BeliefState() for pid in roster}
    stats = _WindowStats()
    rows: list[MeetingTableRow] = []
    meeting_index = 0

    for entry in tick_entries:
        stats.count_submissions(entry.actions)
        actions = _deserialize_actions(entry.actions)
        state, events = advance_tick(state, actions, game_map=game_map)
        actual = _state_hash(state)
        if actual != entry.state_hash:
            raise MeetingTableReconstructionError(
                f"{game_id}: tick {entry.tick} reconstructed {actual!r} != recorded "
                f"{entry.state_hash!r} (roster mismatch or engine non-determinism)"
            )
        stats.absorb_tick(state, events, roles)

        if state.phase == "GAME_OVER":
            break
        if state.phase != "MEETING":
            continue

        trigger_event = next(
            (e for e in events if isinstance(e, MeetingTriggeredEvent)), None
        )
        if trigger_event is None:
            raise MeetingTableReconstructionError(
                f"{game_id}: tick {entry.tick} entered MEETING with no "
                "MeetingTriggeredEvent in the reconstructed events"
            )
        meeting_entry = meeting_by_tick.get(entry.tick)
        if meeting_entry is None:
            raise MeetingTableReconstructionError(
                f"{game_id}: tick {entry.tick} entered MEETING but the replay carries "
                "no meeting row for that tick (partial recording) — refusing to "
                "silently under-build"
            )
        if meeting_entry.state_hash_before != actual:
            raise MeetingTableReconstructionError(
                f"{game_id}: meeting at tick {entry.tick} recorded state_hash_before "
                f"{meeting_entry.state_hash_before!r} != reconstructed pre-meeting "
                f"state {actual!r}"
            )

        result = _meeting_result_from_entry(meeting_entry)
        trigger_kind: MeetingTriggerKind = trigger_event.trigger
        reporter = meeting_entry.triggered_by
        ejected = meeting_entry.ejected_player_id
        # Roster off the recorded ballots: every living participant casts exactly one
        # ballot (meetings/manager.py :2823), so the ballot voters ARE the living
        # candidate universe. Sorted for deterministic candidate/row order.
        voters = sorted(ballot.voter for ballot in result.ballots)
        living = tuple(voters)
        flags = _flag_counts(result.contradictions)

        by_voter = {ballot.voter: ballot for ballot in result.ballots}
        for voter in living:
            ballot = by_voter[voter]
            candidate_features = tuple(
                _candidate_features(
                    candidate,
                    voter=voter,
                    beliefs=beliefs[voter],
                    roles=roles,
                    reporter=reporter,
                    ejected=ejected,
                    flags=flags,
                    stats=stats,
                )
                for candidate in living
            )
            rows.append(
                MeetingTableRow(
                    seed=seed,
                    game_id=game_id,
                    meeting_id=meeting_entry.meeting_id,
                    meeting_index=meeting_index,
                    tick=entry.tick,
                    trigger=trigger_kind,
                    reporter=reporter,
                    outcome=meeting_entry.outcome,
                    ejected_player_id=ejected,
                    voter=voter,
                    voter_role=roles[voter],
                    voter_is_impostor=roles[voter] == "IMPOSTOR",
                    ballot_target=ballot.target,
                    ballot_confidence=ballot.confidence,
                    ballot_primary_reason_id=ballot.primary_reason_id,
                    candidates=candidate_features,
                )
            )

        _fold_meeting_into_beliefs(
            beliefs,
            result=result,
            trigger_kind=trigger_kind,
            roles=roles,
            roster=roster,
            voters=living,
        )

        state, post_events = apply_meeting_result(
            state,
            result,
            game_map=game_map,
            triggering_body_id=trigger_event.body_id,
        )
        after = _state_hash(state)
        if after != meeting_entry.state_hash_after:
            raise MeetingTableReconstructionError(
                f"{game_id}: meeting at tick {entry.tick} reconstructed {after!r} != "
                f"recorded {meeting_entry.state_hash_after!r}"
            )
        stats.reset_window()
        meeting_index += 1
        if state.phase == "GAME_OVER":
            break

    return rows


def build_meeting_table(
    sample_dir: Path, *, splits_path: Path | None = None
) -> MeetingTable:
    """Build the per-(meeting, voter) training table for a replay-set directory.

    Re-seeds every game from the set's roster (``roster.json`` via
    :func:`eval.validity.resolve_roster_knobs`; the flat 4p1i default otherwise),
    recovers roles ground truth from the set's assembled tournament report
    (:func:`eval.validity.assemble_tournament_report` — the report carries per-game
    ``roles``; raw replays are role-free by firewall design), and walks each recorded
    action stream through the engine (:func:`_walk_game`) into rows. The count
    aggregates are read off the SAME assembled report, and the reconstruction is
    asserted to reproduce them exactly — every recorded ballot joins exactly one row
    (100% join rate). Runs on any replay-set directory + both roster presets; reads
    a committed ``splits.json`` when present. Pure and offline.
    """

    if not sample_dir.is_dir():
        raise NotADirectoryError(f"replay-set directory not found: {sample_dir}")
    seeds = seeds_on_disk(sample_dir)
    if not seeds:
        raise ValueError(f"no replay-seed-*.jsonl found under {sample_dir}")

    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    game_map = load_canonical_map()
    per_seed_roles = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )

    # Roles ground truth + the count aggregates come from the set's assembled
    # tournament report (the report carries per-game roles + meeting/ballot rows),
    # NOT hard-coded. The re-seeded roles are byte-identical to the report's (both
    # re-seed the same deterministic recipe); the table asserts against the report.
    report = assemble_tournament_report(sample_dir)
    report_roles = {game.seed: dict(game.roles) for game in report.games}
    report_meetings = [meeting for game in report.games for meeting in game.meetings]
    ejections_total = sum(1 for m in report_meetings if m.outcome == "EJECTED")
    skips_total = sum(1 for m in report_meetings if m.outcome == "SKIPPED")
    ballots_total = sum(len(m.ballots) for m in report_meetings)

    rows: list[MeetingTableRow] = []
    for seed in seeds:
        roles = report_roles.get(seed, per_seed_roles[seed])
        rows.extend(
            _walk_game(
                sample_dir / f"replay-seed-{seed}.jsonl",
                seed=seed,
                num_players=num_players,
                num_impostors=num_impostors,
                tasks_per_crewmate=tasks_per_crewmate,
                roles=roles,
                game_map=game_map,
            )
        )

    rows.sort(key=lambda row: (row.seed, row.meeting_index, row.voter))

    # Every recorded ballot MUST join exactly one row (the 100% join assertion): the
    # table's row count equals the tournament report's ballot total, and its meeting
    # count equals the report's meeting count.
    reconstructed_meetings = len({(row.seed, row.meeting_id) for row in rows})
    if reconstructed_meetings != len(report_meetings):
        raise MeetingTableReconstructionError(
            f"{sample_dir}: reconstructed {reconstructed_meetings} meetings != report "
            f"{len(report_meetings)} (a meeting failed to join)"
        )
    if len(rows) != ballots_total:
        raise MeetingTableReconstructionError(
            f"{sample_dir}: reconstructed {len(rows)} ballot rows != report "
            f"{ballots_total} ballots (join rate < 100%)"
        )

    # A committed split: an explicit ``splits_path`` (e.g. a 15.12 corpus file staged
    # outside the read-only replay dir) takes precedence; otherwise the set's own
    # ``splits.json`` when present. The baseline sets ship none, so the harness
    # derives its folds.
    splits: SurrogateSplits | None
    if splits_path is not None:
        splits = SurrogateSplits.model_validate_json(splits_path.read_text())
    else:
        splits = load_splits(sample_dir)

    return MeetingTable(
        replay_set_dir=str(sample_dir),
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        games_total=len(seeds),
        meetings_total=len(report_meetings),
        ejections_total=ejections_total,
        skips_total=skips_total,
        ballots_total=ballots_total,
        splits=splits,
        rows=tuple(rows),
    )


__all__ = [
    "SEEN_AT_KILL_WINDOW_TICKS",
    "SPLITS_FILENAME",
    "CandidateFeatures",
    "MeetingTable",
    "MeetingTableReconstructionError",
    "MeetingTableRow",
    "SurrogateSplits",
    "build_meeting_table",
    "load_splits",
]
