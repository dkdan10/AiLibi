"""The solvability instrument — who could have done it, from the crew's own eyes.

The project's largest standing admission is that deduction is not demonstrated.
This module supplies the denominator that admission never had. At every
body-triggered meeting it computes, with no LLM call, the set of living players
who COULD have committed the reported kill once every surviving crewmate's own
sighting is pooled. Reading the cells against each other turns the admission
into a measured gap: how often the killer is inside a computable set, how often
that set is a single name and whether it is the right one, and how often the
meeting ejected somebody the crew's own pooled perception had already cleared.

**Eval-privileged: this view is never an agent input.** Nothing in the game
pools perception across agents — each agent holds a private log and the only
cross-agent aggregation is the vote. This module does the pooling offline, over
committed bytes, reading engine state and then narrowing it through each
surviving crewmate's own visibility. That is legitimate for a measurement in
``eval/`` and is exactly what the crew cannot do. A future gameplay lever that
renders any of this into a prompt is a different task under a different record,
and it would have to be built from the agents' RECORDED perception rather than
from engine state — otherwise it is omniscience and the firewall argument
collapses.

The rule, stated before any cell is counted
-------------------------------------------
**Which meetings enter.** Body-triggered meetings only — the walker's
``MeetingOpened.body_id`` is not ``None``. An emergency meeting reports no body,
so there is no kill to reason about; it is excluded from every numerator AND
every denominator here, including the ejection census.

**Which kill anchors a meeting.** The reported body's OWN kill. The engine mints
the body id as ``body-{victim}-{tick}`` when the kill resolves
(``engine.rules.resolve_kill``), so the reported id resolves to exactly one
recorded ``KilledEvent`` and therefore to its killer, victim, room ``R`` and
engine kill tick ``tk``. A meeting whose reported body has no recorded kill is a
reconstruction breach and raises.

**Who counts as an observer.** Every player whose re-seeded role is CREWMATE
that is alive in the pre-advance state of ``tk`` AND alive at the meeting. Both
halves are load-bearing: a crewmate who was dead at ``tk`` saw nothing, and a
crewmate killed between ``tk`` and the meeting is not present to say what it
saw. Impostors never observe here — an impostor's sighting is not something the
crew can pool honestly, and counting it would clear players on the killer's own
word.

**What "could have been in the room" means, and what clears a player.**
``engine.visibility.compute_visibility_for_player`` is evaluated per observer on
the PRE-advance state of ``tk`` — the state the recorded actions of that tick
were decided from. A player ``P`` is CLEARED when some observer ``O`` sees ``P``
there and ``P``'s room at ``tk`` is not ``R``. A player inside a vent is visible
to nobody and is therefore never cleared. The candidate set is every player
alive at the meeting that is not cleared.

**Self-placement does not clear.** ``VisibilityResult.visible_player_ids``
never contains the observer itself, so a player's own uncorroborated placement
can never clear it; clearing always takes a second pair of eyes. This is the
honest reading of "the crew pooled what it saw" — a lone claim about one's own
whereabouts is exactly the claim an impostor makes.

**Which roster the candidates are drawn from.** The living roster AT THE
MEETING, not at the kill tick. The meeting's question is which of the people
still in the room could have done it; a player killed between ``tk`` and the
meeting is no longer ejectable and is not a candidate. The victim is dead at
its own meeting by construction, and :func:`candidate_set_for_body_meeting`
rejects a roster that still contains it rather than silently dropping it.

**What this does NOT measure.** It is an UPPER BOUND on what the crew could
know, because it assumes honest pooling: an impostor lying about co-presence
could falsely clear a teammate, and this module's clearing relation cannot lie.
It also measures a ceiling, not an outcome — no agent ever saw this set, so a
meeting outside it is not evidence any particular agent reasoned badly. And
containment counts a meeting as a miss when the killer was already ejected at an
earlier meeting and so is absent from the living roster: the reported body's
killer is then genuinely not among the people the meeting can eject.

Not the funnel's Stage-1 oracle
-------------------------------
``eval.funnel``'s Stage-1 candidate set answers a different question — what
information EXISTED in the world at the kill — and its rule differs on four
points, each deliberate there and rejected here: it drops the reporter from the
suspect universe (a calibrated prior that the messenger is innocent), it CLEARS
a vented player (a god's-eye vent alibi the crew cannot see), it counts a
witness that died before the meeting (existence, not survival), and it reads the
recorded post-advance positions. This module asks what the SURVIVING crew could
have concluded, so the reporter is a suspect like anyone else, a vented player is
never cleared, a dead witness cannot testify, and the frame is the pre-advance
decision state.

Why the same-tick rule is sound, and where the geometry enters
--------------------------------------------------------------
A kill requires the killer to be in the victim's room
(``engine.rules.resolve_kill``: "kill requires same room") and each player
submits at most one translated action per tick
(``orchestrator.boundary.translate_action_intents_for_tick`` yields one batch
per tick). So a player that a surviving crewmate perceived in a room other than
``R``, in the pre-advance state of ``tk``, cannot have killed at ``tk``: it
spent that tick's single action somewhere else.

No reachability computation is needed for that rule. Doorway adjacency
(``Map.room_neighbors`` over ``engine/maps/canonical_1.yaml``) and the vent
graph (``Map.vent_neighbors`` / ``Map.vent_for_room``, the map's 6-node
network) enter only as the reason the rule is safe — a mover cannot also kill,
and a vented player is perceived by nobody and so is never cleared. Those two
are the machinery a WINDOW variant would need (clearing across a span of ticks
requires knowing what is reachable from where); this module deliberately ships
the same-tick rule alone.

Two clocks, and only one of them is read
----------------------------------------
Every tick in this module is an ENGINE tick, taken from the walker's recorded
rows and pre-advance states. The agent-facing clock runs one ahead: packets are
built from the pre-advance state while ``input_tick = state.tick`` is recorded
beside the POST-advance state (``orchestrator.game``). No agent-recorded row is
consumed here at all, so the +1 never enters — which is itself one of the four
definitional choices below.

Current-HEAD equivalence, called out so it cannot rot
-----------------------------------------------------
A CREWMATE observer resolves to ``same_room_only`` at base visibility (the
role-asymmetric mode in ``engine.visibility``), so "co-present with" and
"visible to" coincide on today's map and today's rules, and an active sabotage
degrade applies to everyone alike. This module calls
``compute_visibility_for_player`` anyway rather than comparing rooms directly,
so the instrument stays honest if that asymmetry ever changes. The equivalence
is a current-HEAD fact, not an assumption the code relies on.

The four choices, and what the rejected alternatives would have produced
------------------------------------------------------------------------
The review's one-sentence rule underdetermines the count, so each choice is
fixed above and its alternative is named here with the cell it produces. All
figures are over the four committed sets (626 body meetings, 354 ejections at
them); the pins live in ``tests/eval/test_solvability.py`` and the recount
command is ``uv run python scripts/measure_baseline.py --solvability``.

* **Kill anchor** — the reported body's own kill (chosen) vs the last recorded
  kill at or before the trigger tick (the review's wording). Containment is
  544/626 under the chosen anchor and 581/626 under the alternative, which the
  report carries as ``killer_in_set_last_kill_anchor`` so the difference stays a
  measured number rather than a claim. The two coincide whenever the freshest
  body is the one reported and diverge when an older body is discovered after a
  newer kill: the alternative then anchors on a kill nobody at the meeting has
  reported, and it is generous exactly there, because the freshest kill's killer
  is the one the same-tick rule is least able to clear.
* **Candidate pool** — the living roster at the meeting (chosen) vs the living
  roster at the kill tick. The alternative is degenerate, not merely different:
  the killer is alive at its own kill tick and the same-tick rule can never
  clear it, so containment is 626/626 by construction. It also admits players
  killed between ``tk`` and the meeting, whom the meeting cannot eject.
* **Self-placement** — never clears (chosen) vs a player's own recorded
  placement clearing it. The alternative collapses the candidate set to
  "whoever was in the body's room": singleton 522/626 and ≤2 626/626 under the
  chosen anchor. It also credits the crew with believing exactly the claim an
  impostor makes.
* **Perception source** — engine perception on the pre-advance state (chosen)
  vs the agents' recorded memory rows. The alternative lands a tick away because
  the agent clock runs +1, and it measures the memory substrate rather than the
  ceiling; it is the right source for a GAMEPLAY lever and the wrong one for a
  ceiling.

The residual against the review, stated rather than shrugged at
----------------------------------------------------------------
The review reports containment 581/626, singleton 109/626 with 103/109 correct,
≤2 208/626, and 61/354 ejections on an already-cleared player. Its oracle is
not committed, so the numbers are re-derived here rather than copied. The kill
anchor accounts for the containment difference EXACTLY: re-scored under the
review's anchor this module returns 581/626, the review's figure to the unit.
The same re-scoring returns singleton 120/626 (114/120 correct), ≤2 228/626 and
59/354 cleared-player ejections, so a residual on the SET-SIZE cells remains
that the anchor does not explain. Two of the three remaining dimensions are
ruled out by measurement — the kill-tick pool forces containment to 626/626 and
self-placement forces singleton to 522/626, and the review's figures are neither
— which leaves a further definitional detail its one sentence does not fix. The
committed pin is this module's own recount under the rule stated above, not the
review's number.

Purity: offline, no network, no ``AILIBI_*`` env read, no LLM call. The report
is a pure function of the committed bytes plus the re-seeded role ground truth,
so two runs over the same bytes produce identical reports.

STABLE JSON report schema (``SolvabilityReport.model_dump()``)::

    {
      "replay_set_dir": str,
      "num_players": int, "num_impostors": int, "tasks_per_crewmate": int,
      "games_total": int,
      "body_meetings": int,
      "ejections_at_body_meetings": int,
      "killer_in_set": WilsonRateCell,                  # of body_meetings
      "singleton_sets": WilsonRateCell,                 # of body_meetings
      "singleton_correct": WilsonRateCell,              # of singleton_sets
      "at_most_two_sets": WilsonRateCell,               # of body_meetings
      "at_most_two_contains_killer": WilsonRateCell,    # of at_most_two_sets
      "cleared_player_ejections": WilsonRateCell,       # of ejections_at_...
      "killer_in_set_last_kill_anchor": WilsonRateCell  # rejected-anchor probe
    }

Every cell is ``eval.deduction_metrics.WilsonRateCell`` (counts + the Wilson 95%
score interval): the 4p1i sets carry 35 and 29 body meetings, which is exactly
why the interval rides beside the rate. The block is count-only — no player ids,
roles, rooms, or transcript text leave this module.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, NoReturn

from pydantic import BaseModel, ConfigDict

from engine.entities import BodyId, PlayerId, Role, RoomId
from engine.events import KilledEvent
from engine.visibility import compute_visibility_for_player
from engine.world import Map, WorldState, load_canonical_map
from eval.deduction_metrics import (
    _RARE_EVENT_ADVISORY_MAX_NUMERATOR,
    WilsonRateCell,
    _wilson_interval,
)
from eval.replay_walk import (
    MeetingOpened,
    ReplayWalkConfig,
    TickAdvanced,
    WalkViolation,
    walk_replay,
)
from eval.validity import resolve_roster_knobs, roles_by_seed, seeds_on_disk


class SolvabilityReconstructionError(RuntimeError):
    """A recording did not reconstruct, or a reported body has no kill.

    An instrument that silently under-measures a truncated recording is worse
    than one that fails loudly (AGENTS.md "no silent fallbacks"), so the walk
    runs the referee-grade check set and every breach raises here naming the
    game and tick: a per-tick ``state_hash`` mismatch, a duplicate meeting row,
    a MEETING tick with no meeting row, a meeting ``state_hash_before`` /
    ``state_hash_after`` mismatch, a replay whose bytes end before GAME_OVER,
    rows trailing the terminal tick, a missing ``game_over`` row, a replay-set
    directory with no ``replay-seed-*.jsonl`` files, and a body-triggered
    meeting whose reported body id matches no recorded ``KilledEvent``.
    """


class _FrozenModel(BaseModel):
    """Frozen, ``extra="forbid"`` base (the ``eval/`` report convention)."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class SolvabilityReport(_FrozenModel):
    """One replay set's solvability ceiling — counts and rate cells only.

    ``killer_in_set`` is containment: the killer of the reported body is inside
    the candidate set. ``singleton_sets`` / ``singleton_correct`` are the sharp
    end — one name, and that name being the killer. ``cleared_player_ejections``
    is the gap: an ejection at a body meeting that landed on a player the pooled
    perception had already cleared. ``killer_in_set_last_kill_anchor`` is the
    rejected kill anchor's containment, carried so the module docstring's
    "would have produced" is a measured number.
    """

    replay_set_dir: str
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    games_total: int
    body_meetings: int
    ejections_at_body_meetings: int
    killer_in_set: WilsonRateCell
    singleton_sets: WilsonRateCell
    singleton_correct: WilsonRateCell
    at_most_two_sets: WilsonRateCell
    at_most_two_contains_killer: WilsonRateCell
    cleared_player_ejections: WilsonRateCell
    killer_in_set_last_kill_anchor: WilsonRateCell


def candidate_set_for_body_meeting(
    *,
    kill_state: WorldState,
    game_map: Map,
    roles: Mapping[PlayerId, Role],
    body_room: RoomId,
    victim: PlayerId,
    living_at_meeting: frozenset[PlayerId],
) -> frozenset[PlayerId]:
    """Who the crew's own pooled sightings cannot rule out for this kill.

    ``kill_state`` is the PRE-advance world state of the kill tick — the state
    the recorded actions of that tick were decided from. Every player alive at
    the meeting is a candidate unless some surviving crewmate OTHER than that
    player perceived it, in ``kill_state``, in a room other than ``body_room``.
    The module docstring is the full rule; the short form is: crew eyes only,
    both endpoints alive, vents clear nobody, and nobody clears itself.
    """

    if victim in living_at_meeting:
        raise SolvabilityReconstructionError(
            f"victim {victim!r} is alive at its own body meeting — the meeting "
            "is mis-anchored (a victim cannot be its own killer)"
        )

    cleared: set[PlayerId] = set()
    for observer in sorted(living_at_meeting):
        if roles.get(observer) != "CREWMATE":
            continue
        observer_state = kill_state.players.get(observer)
        if observer_state is None or not observer_state.alive:
            continue
        visible = compute_visibility_for_player(
            observer_id=observer,
            world_state=kill_state,
            game_map=game_map,
        ).visible_player_ids
        for seen in visible:
            # ``visible_player_ids`` excludes the observer itself, the dead, and
            # anyone in a vent, so self-placement never clears and a vented
            # player is never cleared.
            if kill_state.players[seen].room != body_room:
                cleared.add(seen)

    return living_at_meeting - cleared


@dataclass(frozen=True)
class _KillFact:
    """One recorded kill, keyed by the body id the engine minted for it."""

    tick: int
    killer: PlayerId
    victim: PlayerId
    room: RoomId


@dataclass(frozen=True)
class _MeetingRow:
    """One body-triggered meeting's folded facts (counts only leave the module)."""

    killer_in_set: bool
    set_size: int
    singleton_correct: bool
    ejected_outside_set: bool | None
    killer_in_set_last_kill_anchor: bool


@dataclass
class _GameFold:
    rows: list[_MeetingRow] = field(default_factory=list)


def compute_solvability_report(sample_dir: Path) -> SolvabilityReport:
    """Compute the solvability ceiling over one committed replay set.

    Pure + offline: resolve the roster, recover per-seed role ground truth by
    re-seeding, walk every committed game under the referee-grade profile, and
    fold one row per body-triggered meeting. Fails loud
    (:class:`SolvabilityReconstructionError`) on any reconstruction
    disagreement — never silently under-measures.
    """

    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    game_map = load_canonical_map()
    per_seed_roles = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    seeds = seeds_on_disk(sample_dir)
    if not seeds:
        raise SolvabilityReconstructionError(
            f"{sample_dir}: no replay-seed-*.jsonl files found — not a replay set "
            "(wrong path?); refusing to report a zero-game measurement"
        )

    rows: list[_MeetingRow] = []
    for seed in seeds:
        rows.extend(
            _walk_game(
                sample_dir / f"replay-seed-{seed}.jsonl",
                seed=seed,
                num_players=num_players,
                num_impostors=num_impostors,
                tasks_per_crewmate=tasks_per_crewmate,
                roles=per_seed_roles[seed],
                game_map=game_map,
            ).rows
        )

    body_meetings = len(rows)
    ejection_rows = [row for row in rows if row.ejected_outside_set is not None]
    singletons = [row for row in rows if row.set_size == 1]
    at_most_two = [row for row in rows if row.set_size <= 2]

    return SolvabilityReport(
        replay_set_dir=str(sample_dir),
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        games_total=len(seeds),
        body_meetings=body_meetings,
        ejections_at_body_meetings=len(ejection_rows),
        killer_in_set=_cell(sum(1 for row in rows if row.killer_in_set), body_meetings),
        singleton_sets=_cell(len(singletons), body_meetings),
        singleton_correct=_cell(
            sum(1 for row in singletons if row.singleton_correct), len(singletons)
        ),
        at_most_two_sets=_cell(len(at_most_two), body_meetings),
        at_most_two_contains_killer=_cell(
            sum(1 for row in at_most_two if row.killer_in_set), len(at_most_two)
        ),
        cleared_player_ejections=_cell(
            sum(1 for row in ejection_rows if row.ejected_outside_set),
            len(ejection_rows),
        ),
        killer_in_set_last_kill_anchor=_cell(
            sum(1 for row in rows if row.killer_in_set_last_kill_anchor),
            body_meetings,
        ),
    )


def _cell(numerator: int, denominator: int) -> WilsonRateCell:
    """Build a :class:`WilsonRateCell` over the imported Wilson helper."""

    rate, low, high = _wilson_interval(numerator, denominator)
    return WilsonRateCell(
        numerator=numerator,
        denominator=denominator,
        rate=rate,
        wilson_low=low,
        wilson_high=high,
        advisory=numerator <= _RARE_EVENT_ADVISORY_MAX_NUMERATOR,
    )


# --------------------------------------------------------------------------- #
# The reconstruction walk (eval.replay_walk under the 'solvability' profile).  #
# --------------------------------------------------------------------------- #


def _walk_game(
    replay_path: Path,
    *,
    seed: int,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    roles: Mapping[PlayerId, Role],
    game_map: Map,
) -> _GameFold:
    """Re-seed + replay one game, folding one row per body-triggered meeting.

    Two things come off the walk: on ``TickAdvanced`` the pre-advance state of
    each tick and every ``KilledEvent`` keyed by the body id the engine minted
    for it; on ``MeetingOpened`` the reported body, resolved back to that kill
    and scored against the meeting's living roster.
    """

    fold = _GameFold()
    game_id = f"headless-seed-{seed}"
    pre_state_by_tick: dict[int, WorldState] = {}
    kill_by_body: dict[BodyId, _KillFact] = {}
    kills_in_order: list[_KillFact] = []

    for walk_event in walk_replay(
        replay_path,
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
        config=_WALK_CONFIG,
    ):
        if isinstance(walk_event, TickAdvanced):
            pre_state_by_tick[walk_event.entry.tick] = walk_event.pre_state
            for event in walk_event.events:
                if isinstance(event, KilledEvent):
                    fact = _KillFact(
                        tick=event.tick,
                        killer=event.actor,
                        victim=event.target,
                        room=event.room,
                    )
                    # The id the engine mints at ``resolve_kill``; it is what a
                    # reported body carries back to this kill.
                    kill_by_body[f"body-{event.target}-{event.tick}"] = fact
                    kills_in_order.append(fact)
        elif isinstance(walk_event, MeetingOpened):
            if walk_event.body_id is None:
                continue  # emergency meeting: no reported body, nothing to solve
            kill = kill_by_body.get(walk_event.body_id)
            if kill is None:
                raise SolvabilityReconstructionError(
                    f"{game_id}: meeting at tick {walk_event.entry.tick} reports "
                    f"body {walk_event.body_id!r} with no recorded kill event"
                )
            fold.rows.append(
                _meeting_row(
                    game_id=game_id,
                    entry_tick=walk_event.entry.tick,
                    meeting_state=walk_event.state,
                    ejected=(
                        walk_event.entry.ejected_player_id
                        if walk_event.entry.outcome == "EJECTED"
                        else None
                    ),
                    kill=kill,
                    last_kill=_last_kill_at_or_before(
                        kills_in_order, walk_event.entry.tick
                    ),
                    pre_state_by_tick=pre_state_by_tick,
                    roles=roles,
                    game_map=game_map,
                )
            )

    return fold


def _last_kill_at_or_before(kills: list[_KillFact], tick: int) -> _KillFact | None:
    """The rejected anchor: the latest recorded kill at or before ``tick``."""

    candidates = [kill for kill in kills if kill.tick <= tick]
    return candidates[-1] if candidates else None


def _meeting_row(
    *,
    game_id: str,
    entry_tick: int,
    meeting_state: WorldState,
    ejected: PlayerId | None,
    kill: _KillFact,
    last_kill: _KillFact | None,
    pre_state_by_tick: Mapping[int, WorldState],
    roles: Mapping[PlayerId, Role],
    game_map: Map,
) -> _MeetingRow:
    """Score one body-triggered meeting against both kill anchors."""

    living = frozenset(
        player_id for player_id, player in meeting_state.players.items() if player.alive
    )
    candidates = _candidates_for_kill(
        game_id=game_id,
        entry_tick=entry_tick,
        kill=kill,
        pre_state_by_tick=pre_state_by_tick,
        roles=roles,
        game_map=game_map,
        living=living,
    )
    alternative: frozenset[PlayerId] = frozenset()
    if last_kill is not None:
        alternative = _candidates_for_kill(
            game_id=game_id,
            entry_tick=entry_tick,
            kill=last_kill,
            pre_state_by_tick=pre_state_by_tick,
            roles=roles,
            game_map=game_map,
            living=living,
        )

    return _MeetingRow(
        killer_in_set=kill.killer in candidates,
        set_size=len(candidates),
        singleton_correct=candidates == frozenset({kill.killer}),
        ejected_outside_set=None if ejected is None else ejected not in candidates,
        killer_in_set_last_kill_anchor=(
            last_kill is not None and last_kill.killer in alternative
        ),
    )


def _candidates_for_kill(
    *,
    game_id: str,
    entry_tick: int,
    kill: _KillFact,
    pre_state_by_tick: Mapping[int, WorldState],
    roles: Mapping[PlayerId, Role],
    game_map: Map,
    living: frozenset[PlayerId],
) -> frozenset[PlayerId]:
    kill_state = pre_state_by_tick.get(kill.tick)
    if kill_state is None:
        raise SolvabilityReconstructionError(
            f"{game_id}: meeting at tick {entry_tick} anchors on a kill at tick "
            f"{kill.tick} the walk never reached"
        )
    return candidate_set_for_body_meeting(
        kill_state=kill_state,
        game_map=game_map,
        roles=roles,
        body_room=kill.room,
        victim=kill.victim,
        living_at_meeting=living,
    )


def _raise_walk_violation(violation: WalkViolation) -> NoReturn:
    """The ``solvability`` profile's violation hook — one message per kind."""

    game_id = violation.game_id
    messages: Mapping[str, str] = {
        "duplicate_meeting_rows": (
            "duplicate meeting rows (same tick or meeting id) — the collapsed "
            "duplicate's hashes would never be validated"
        ),
        "tick_hash_mismatch": (
            f"tick {violation.tick} reconstructed {violation.actual!r} != "
            f"recorded {violation.expected!r}"
        ),
        "missing_meeting_row": (
            f"tick {violation.tick} entered MEETING with no recorded meeting row "
            "— the census would silently drop the meeting"
        ),
        "meeting_pre_hash_mismatch": (
            f"meeting at tick {violation.tick} recorded state_hash_before "
            f"{violation.expected!r} != reconstructed {violation.actual!r}"
        ),
        "meeting_post_hash_mismatch": (
            f"meeting at tick {violation.tick} recorded state_hash_after "
            f"{violation.expected!r} != reconstructed {violation.actual!r}"
        ),
        "missing_terminal_tick": (
            f"replay ends at tick {violation.state_tick} in phase "
            f"{violation.phase!r} without reaching GAME_OVER — a truncated "
            "recording would under-count body meetings"
        ),
        "trailing_replay_rows": (
            f"rows recorded after the terminal tick {violation.terminal_tick} — "
            "bytes the walk never validated"
        ),
        "missing_game_end_row": "no terminal game_over row",
    }
    detail = messages.get(violation.kind, f"walk violation {violation.kind!r}")
    raise SolvabilityReconstructionError(f"{game_id}: {detail}")


_WALK_CONFIG: Final[ReplayWalkConfig] = ReplayWalkConfig(
    profile="solvability",
    on_violation=_raise_walk_violation,
    verify_tick_hashes=True,
    reject_duplicate_meeting_rows=True,
    missing_meeting_row="violation",
    verify_meeting_pre_hashes=True,
    verify_meeting_post_hashes=True,
    require_terminal_tick=True,
    reject_trailing_rows=True,
    require_game_end_row=True,
)
