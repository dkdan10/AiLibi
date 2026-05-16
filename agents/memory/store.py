"""Composite memory surface and prompt rendering (DESIGN.md §6.1, §6.6).

Aggregates the three stores introduced in Task 2.3 (`agents/memory/episodic.py`,
`agents/memory/working.py`, `agents/memory/beliefs.py`) into a single
:class:`AgentMemory` surface. ``render_for_prompt`` reads from all three
components to produce the token-budgeted Markdown view per DESIGN.md §6.6.

This composite is the integration point Phase 3 strategic agents import
through (audit R-6, `audits/audit-2026-05-15-0225-reconciled.md`).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Final, TypeAlias

from agents.memory.beliefs import (
    AlibiClaim,
    BeliefState,
    ContradictionRef,
    PlayerBelief,
)
from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.working import LastSeen, WorkingMemory

PlayerId: TypeAlias = str
RoomId: TypeAlias = str
TaskId: TypeAlias = str

DEFAULT_TOKEN_BUDGET: Final[int] = 1500

# 4 chars/token is the widely-cited heuristic for English BPE
# tokenizers. The renderer does not depend on a provider tokenizer:
# the budget arithmetic must be deterministic across providers so
# golden tests pin behavior, not the provider's tokenizer choice.
_CHARS_PER_TOKEN: Final[int] = 4

# Salience weights per renderable event type. Higher = more salient
# (more likely to survive a tight token budget). Matches the priority
# in DESIGN.md §6.2: body discoveries, kills, vent observations,
# sightings, task completions, routine status.
_SALIENCE_FOUND_BODY: Final[int] = 100
_SALIENCE_KILL_WITNESSED: Final[int] = 95
_SALIENCE_VENT_WITNESSED: Final[int] = 85
_SALIENCE_VENT_HEARD: Final[int] = 75
_SALIENCE_SABOTAGE_HEARD: Final[int] = 65
_SALIENCE_SAW_PLAYER_ACTIVE: Final[int] = 55
_SALIENCE_SAW_PLAYER: Final[int] = 50
_SALIENCE_COMPLETED_TASK: Final[int] = 30
_SALIENCE_COOLDOWN_STATUS: Final[int] = 10

_EVENT_SAW_BODY: Final[str] = "saw_body"
_EVENT_SAW_PLAYER: Final[str] = "saw_player"
_EVENT_HEARD_VENT_USE: Final[str] = "heard_vent_use"
_EVENT_HEARD_SABOTAGE_ALARM: Final[str] = "heard_sabotage_alarm"
_EVENT_SELF_STATE: Final[str] = "self_state"
_EVENT_GLOBAL_STATUS: Final[str] = "global_status"
_EVENT_COOLDOWN_STATUS: Final[str] = "cooldown_status"

_ACTIVE_PLAYER_ACTIONS: Final[frozenset[str]] = frozenset({"report", "task"})


@dataclass
class AgentMemory:
    """Composite memory surface for a single agent (DESIGN.md §6.1).

    Aggregates references to the three Task-2.3 stores. The composite
    does not copy state: callers mutate the underlying stores directly
    and the composite reflects every change. ``render_for_prompt``
    reads from all three components (R-6 acceptance gate).
    """

    episodic: MemoryStore = field(default_factory=MemoryStore)
    working: WorkingMemory = field(default_factory=WorkingMemory)
    beliefs: BeliefState = field(default_factory=BeliefState)


@dataclass(frozen=True)
class _Observation:
    """One renderable observation line with the data needed to sort and budget it."""

    salience: int
    tick: int
    line: str


def render_for_prompt(
    memory: AgentMemory,
    *,
    token_budget: int = DEFAULT_TOKEN_BUDGET,
) -> str:
    """Produce a token-budgeted Markdown view of agent memory (DESIGN.md §6.6).

    Reads from every component in ``memory``:

    * episodic → role line, tasks-completed line, observation lines.
    * beliefs  → ``Your current beliefs`` and ``Open contradictions``.
    * working  → last-seen suffixes on belief lines.

    Salience ordering is deterministic: events are sorted by salience
    descending, tick descending, then line text ascending for stable
    tie-breaks. Events past ``token_budget`` are dropped by lowest
    salience first; the role line, tasks-completed line, beliefs, and
    contradictions are always retained because they are agent-essential
    context that the LLM cannot work around.

    Raises :class:`ValueError` if ``token_budget`` is non-positive or
    if no ``self_state`` event has been recorded. A render call before
    perception has run is a wiring bug, not a normal state, so we
    fail loud (AGENTS.md "no silent fallbacks").
    """

    if token_budget <= 0:
        raise ValueError(f"token_budget must be positive, got {token_budget}")

    role = _latest_role(memory.episodic)
    if role is None:
        raise ValueError(
            "cannot render memory: no self_state event has been recorded; "
            "perception must run at least once before rendering."
        )

    tasks_summary = _latest_tasks_summary(memory.episodic)
    observations = sorted(
        _build_observations(memory.episodic),
        key=lambda obs: (-obs.salience, -obs.tick, obs.line),
    )
    beliefs_lines = _build_belief_lines(memory.beliefs, memory.working)
    contradiction_lines = _build_contradiction_lines(memory.beliefs)

    return _assemble_view(
        role=role,
        tasks_summary=tasks_summary,
        observations=observations,
        beliefs_lines=beliefs_lines,
        contradiction_lines=contradiction_lines,
        token_budget=token_budget,
    )


def _estimate_tokens(text: str) -> int:
    """Approximate BPE token count from character length.

    Uses ceiling division so the estimate never undercounts the true
    token cost of a string. The contract for ``render_for_prompt`` is
    "actual rendered token count <= token_budget"; floor division
    would let a 5-char string score as 1 token even though most BPE
    tokenizers split it into 2, and the rendered view could quietly
    overrun the budget. Ceiling is conservative — we may pack one
    fewer observation than strictly necessary, but we never overshoot.
    The 4 chars/token ratio is the standard heuristic for English text
    in BPE-style tokenizers.
    """

    if not text:
        return 0
    return (len(text) + _CHARS_PER_TOKEN - 1) // _CHARS_PER_TOKEN


def _latest_role(episodic: MemoryStore) -> str | None:
    role: str | None = None
    for event in episodic.recent(since_tick=0):
        if event.type != _EVENT_SELF_STATE:
            continue
        value = event.payload.get("role")
        if isinstance(value, str):
            role = value
    return role


def _latest_tasks_summary(episodic: MemoryStore) -> str | None:
    summary: str | None = None
    for event in episodic.recent(since_tick=0):
        if event.type != _EVENT_GLOBAL_STATUS:
            continue
        completed = event.payload.get("tasks_completed")
        total = event.payload.get("tasks_total")
        if isinstance(completed, int) and isinstance(total, int):
            summary = f"{completed} / {total}"
    return summary


def _build_observations(episodic: MemoryStore) -> list[_Observation]:
    observations: list[_Observation] = []
    seen_body_ids: set[str] = set()
    last_pending_task: str | None = None
    last_pending_task_room: str | None = None
    first_self_state = True

    for event in episodic.recent(since_tick=0):
        if event.type == _EVENT_SELF_STATE:
            pending = event.payload.get("pending_task_id")
            room = event.payload.get("room")
            if (
                not first_self_state
                and isinstance(last_pending_task, str)
                and pending is None
            ):
                completed_room = (
                    last_pending_task_room
                    if isinstance(last_pending_task_room, str)
                    else "an unknown room"
                )
                observations.append(
                    _Observation(
                        salience=_SALIENCE_COMPLETED_TASK,
                        tick=event.tick,
                        line=(
                            f"[tick {event.tick}] You completed "
                            f"{last_pending_task} (you were in "
                            f"{completed_room})."
                        ),
                    )
                )
            last_pending_task = pending if isinstance(pending, str) else None
            last_pending_task_room = room if isinstance(room, str) else None
            first_self_state = False
            continue

        if event.type == _EVENT_SAW_BODY:
            body_id = event.payload.get("body_id")
            if not isinstance(body_id, str):
                continue
            if body_id in seen_body_ids:
                continue
            victim_id = event.payload.get("victim_id")
            room = event.payload.get("room")
            if not isinstance(victim_id, str) or not isinstance(room, str):
                # Don't mark the body as seen yet -- a later well-formed
                # event for the same body_id should still surface its
                # discovery.
                continue
            seen_body_ids.add(body_id)
            observations.append(
                _Observation(
                    salience=_SALIENCE_FOUND_BODY,
                    tick=event.tick,
                    line=(
                        f"[tick {event.tick}] You discovered {victim_id}'s "
                        f"body in {room}."
                    ),
                )
            )
            continue

        if event.type == _EVENT_SAW_PLAYER:
            obs = _render_saw_player(event)
            if obs is not None:
                observations.append(obs)
            continue

        if event.type == _EVENT_HEARD_VENT_USE:
            obs = _render_heard(
                event,
                salience=_SALIENCE_VENT_HEARD,
                noun="vent use",
            )
            if obs is not None:
                observations.append(obs)
            continue

        if event.type == _EVENT_HEARD_SABOTAGE_ALARM:
            obs = _render_heard(
                event,
                salience=_SALIENCE_SABOTAGE_HEARD,
                noun="sabotage alarm",
            )
            if obs is not None:
                observations.append(obs)
            continue

        if event.type == _EVENT_COOLDOWN_STATUS:
            cooldown = event.payload.get("cooldown")
            if isinstance(cooldown, int) and cooldown > 0:
                observations.append(
                    _Observation(
                        salience=_SALIENCE_COOLDOWN_STATUS,
                        tick=event.tick,
                        line=(
                            f"[tick {event.tick}] Your kill cooldown is "
                            f"{cooldown} ticks."
                        ),
                    )
                )

    return observations


def _render_saw_player(event: EpisodicEvent) -> _Observation | None:
    player_id = event.payload.get("player_id")
    room = event.payload.get("room")
    if not isinstance(player_id, str) or not isinstance(room, str):
        return None
    action = event.payload.get("action")
    action_str: str | None = action if isinstance(action, str) else None
    if action_str == "vent":
        return _Observation(
            salience=_SALIENCE_VENT_WITNESSED,
            tick=event.tick,
            line=(f"[tick {event.tick}] You witnessed {player_id} vent in {room}."),
        )
    if action_str == "kill":
        return _Observation(
            salience=_SALIENCE_KILL_WITNESSED,
            tick=event.tick,
            line=(f"[tick {event.tick}] You witnessed {player_id} kill in {room}."),
        )
    if action_str in _ACTIVE_PLAYER_ACTIONS:
        return _Observation(
            salience=_SALIENCE_SAW_PLAYER_ACTIVE,
            tick=event.tick,
            line=(f"[tick {event.tick}] You saw {player_id} {action_str} in {room}."),
        )
    return _Observation(
        salience=_SALIENCE_SAW_PLAYER,
        tick=event.tick,
        line=f"[tick {event.tick}] You saw {player_id} in {room}.",
    )


def _render_heard(
    event: EpisodicEvent,
    *,
    salience: int,
    noun: str,
) -> _Observation | None:
    room = event.payload.get("room")
    if isinstance(room, str):
        line = f"[tick {event.tick}] You heard a {noun} in {room}."
    elif room is None:
        line = f"[tick {event.tick}] You heard a {noun}."
    else:
        return None
    return _Observation(salience=salience, tick=event.tick, line=line)


def _build_belief_lines(beliefs: BeliefState, working: WorkingMemory) -> list[str]:
    lines: list[str] = []
    for player_id in sorted(beliefs.known_players()):
        belief = beliefs.view(player_id)
        belief_text = _format_belief_score(belief)
        if belief_text is None:
            continue
        suffix = _format_last_seen_suffix(working.last_seen(player_id))
        if suffix:
            lines.append(f"{player_id}: {belief_text} ({suffix})")
        else:
            lines.append(f"{player_id}: {belief_text}")
    return lines


def _format_belief_score(belief: PlayerBelief) -> str | None:
    suspicion_dev = abs(belief.suspicion - 0.5)
    trust_dev = abs(belief.trust - 0.5)
    # Anything within half of the displayed precision (0.01) rounds to
    # "0.50" in the rendered line and carries no signal, so treat it as
    # neutral. Float accumulation from repeated ``decay_suspicion``
    # toward 0.5 can otherwise leave a non-zero residue that escapes an
    # exact equality check and bloats the prompt with empty belief
    # rows.
    if suspicion_dev < 0.005 and trust_dev < 0.005:
        return None
    if suspicion_dev >= trust_dev:
        return f"suspicion {belief.suspicion:.2f}"
    return f"trust {belief.trust:.2f}"


def _format_last_seen_suffix(last_seen: LastSeen | None) -> str:
    if last_seen is None:
        return ""
    return f"last seen in {last_seen.room} at tick {last_seen.tick}"


def _build_contradiction_lines(beliefs: BeliefState) -> list[str]:
    seen: set[tuple[str, str, str]] = set()
    contradictions: list[ContradictionRef] = []
    for player_id in sorted(beliefs.known_players()):
        belief = beliefs.view(player_id)
        for contradiction in belief.inconsistencies:
            key = (
                contradiction.summary,
                contradiction.left_ref,
                contradiction.right_ref,
            )
            if key in seen:
                continue
            seen.add(key)
            contradictions.append(contradiction)
    contradictions.sort(key=lambda c: (c.summary, c.left_ref, c.right_ref))
    return [c.summary for c in contradictions]


def _assemble_view(
    *,
    role: str,
    tasks_summary: str | None,
    observations: list[_Observation],
    beliefs_lines: list[str],
    contradiction_lines: list[str],
    token_budget: int,
) -> str:
    """Assemble the final Markdown view, enforcing token budget on observations.

    The role line, tasks-completed line, beliefs, and contradictions are
    treated as fixed (always rendered) because they are essential context.
    Observations are the elastic section: they fill the remaining budget,
    dropped from lowest salience first if the budget is tight.

    The budget arithmetic charges every character that lands in the
    final output, including the Markdown separators (``"\\n\\n"`` between
    blocks and the trailing ``"\\n"``), so the rendered view's actual
    token estimate cannot exceed ``token_budget``.
    """

    fixed_lines: list[str] = [f"## Your role: {role}"]
    if tasks_summary is not None:
        fixed_lines.append(f"## Tasks completed (global): {tasks_summary}")

    beliefs_block: list[str] = []
    if beliefs_lines:
        beliefs_block.append("## Your current beliefs:")
        beliefs_block.extend(f"- {line}" for line in beliefs_lines)

    contradictions_block: list[str] = []
    if contradiction_lines:
        contradictions_block.append("## Open contradictions:")
        contradictions_block.extend(f"- {line}" for line in contradiction_lines)

    non_elastic_blocks: list[list[str]] = [fixed_lines]
    if beliefs_block:
        non_elastic_blocks.append(beliefs_block)
    if contradictions_block:
        non_elastic_blocks.append(contradictions_block)
    non_elastic_text = (
        "\n\n".join("\n".join(block) for block in non_elastic_blocks) + "\n"
    )
    non_elastic_cost = _estimate_tokens(non_elastic_text)

    observations_header = "## Recent observations (most salient first):"
    # The observations block is inserted as a new top-level block, so
    # adding it costs one ``"\n\n"`` separator plus the header line.
    header_with_separator = "\n\n" + observations_header
    header_cost = _estimate_tokens(header_with_separator)

    remaining = token_budget - non_elastic_cost
    if remaining < header_cost:
        return non_elastic_text

    kept = _select_within_budget(
        observations=observations,
        budget=remaining - header_cost,
    )

    if not kept:
        return non_elastic_text

    blocks: list[list[str]] = [fixed_lines]
    observation_block = [observations_header]
    observation_block.extend(f"- {obs.line}" for obs in kept)
    blocks.append(observation_block)
    if beliefs_block:
        blocks.append(beliefs_block)
    if contradictions_block:
        blocks.append(contradictions_block)

    return "\n\n".join("\n".join(block) for block in blocks) + "\n"


def _select_within_budget(
    *,
    observations: Iterable[_Observation],
    budget: int,
) -> list[_Observation]:
    """Include observations in salience order until one cannot fit.

    ``observations`` must already be sorted by salience descending. As
    soon as an observation does not fit, we stop: every observation
    past the cutoff is at lower-or-equal salience, so allowing any of
    them through would violate "drop by lowest salience first"
    (DESIGN.md §6.6, DoD bullet 1). The kept set is therefore always a
    salience-ordered prefix of the input.

    Each observation line is preceded by a ``"\\n- "`` separator inside
    the observations block (the line is joined to the previous bullet
    line with ``"\\n"`` and prefixed with ``"- "``), so the budget cost
    of inserting it is computed against ``"\\n- " + obs.line``.
    """

    kept: list[_Observation] = []
    remaining = budget
    for obs in observations:
        line_with_separator = "\n- " + obs.line
        cost = _estimate_tokens(line_with_separator)
        if cost > remaining:
            break
        kept.append(obs)
        remaining -= cost
    return kept


__all__ = [
    "AgentMemory",
    "AlibiClaim",
    "BeliefState",
    "ContradictionRef",
    "DEFAULT_TOKEN_BUDGET",
    "EpisodicEvent",
    "MemoryStore",
    "PlayerBelief",
    "PlayerId",
    "RoomId",
    "TaskId",
    "WorkingMemory",
    "render_for_prompt",
]
