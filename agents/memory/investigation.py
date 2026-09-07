"""Bounded investigation intentions derived solely from an agent's own memory."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import TYPE_CHECKING, Annotated, Final, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from agents.memory.episodic import EpisodicEvent
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView

if TYPE_CHECKING:
    from agents.memory.store import AgentMemory

MISSING_SIGHTING_TICKS: Final[int] = 4
MAX_SOURCE_AGE_TICKS: Final[int] = 12
SEARCH_DURATION_TICKS: Final[int] = 6
MAX_VISITED_ROOMS: Final[int] = 3

_Identifier = Annotated[str, Field(strict=True, min_length=1)]
_Tick = Annotated[int, Field(strict=True, ge=0)]


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class InvestigationObservation(_FrozenModel):
    """A latest first-hand placement, retaining its actual observation clock."""

    target_id: _Identifier
    source_observation_id: _Identifier
    source_tick: _Tick
    last_known_room: _Identifier
    observation_phase: Literal["snapshot", "event"]
    observation_order: _Tick | None = None

    @model_validator(mode="after")
    def _phase_order(self) -> Self:
        if (self.observation_phase == "event") != (self.observation_order is not None):
            raise ValueError("event sightings require an order; snapshots have none")
        return self


class InvestigationPlan(_FrozenModel):
    """An intention to look, never an observation or a belief about guilt."""

    target_id: _Identifier
    source_observation_id: _Identifier
    source_tick: _Tick
    last_known_room: _Identifier
    started_tick: _Tick
    expires_tick: _Tick
    visited_rooms: tuple[_Identifier, ...] = Field(
        default=(), max_length=MAX_VISITED_ROOMS
    )

    @model_validator(mode="after")
    def _bounds(self) -> Self:
        if self.source_tick > self.started_tick:
            raise ValueError("investigation cannot start before its source")
        if (
            not self.started_tick
            < self.expires_tick
            <= self.started_tick + SEARCH_DURATION_TICKS
        ):
            raise ValueError("investigation expiry exceeds its bounded lifetime")
        if len(set(self.visited_rooms)) != len(self.visited_rooms):
            raise ValueError("visited rooms must be distinct")
        return self


class ConsumedInvestigationSource(_FrozenModel):
    target_id: _Identifier
    source_observation_id: _Identifier
    source_tick: _Tick


class InvestigationEvidence(_FrozenModel):
    known_player_ids: tuple[_Identifier, ...]
    known_dead_ids: tuple[_Identifier, ...] = ()
    sightings: tuple[InvestigationObservation, ...] = ()

    @model_validator(mode="after")
    def _subjects(self) -> Self:
        known = set(self.known_player_ids)
        if len(known) != len(self.known_player_ids):
            raise ValueError("known player identities must be distinct")
        if len(set(self.known_dead_ids)) != len(self.known_dead_ids):
            raise ValueError("known dead identities must be distinct")
        targets = tuple(row.target_id for row in self.sightings)
        if len(set(targets)) != len(targets):
            raise ValueError("evidence must contain at most one sighting per subject")
        if not set(self.known_dead_ids).union(targets) <= known:
            raise ValueError("evidence subjects must belong to known players")
        return self


class InvestigationState(_FrozenModel):
    """One bounded source index and the last decision's complete idempotence key."""

    active_plan: InvestigationPlan | None = None
    consumed_sources: tuple[ConsumedInvestigationSource, ...] = ()
    last_processed_tick: _Tick | None = None
    last_packet_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")] | None = None
    last_intent: ActionIntent | None = None

    @model_validator(mode="after")
    def _complete_state(self) -> Self:
        cache = (self.last_processed_tick, self.last_packet_sha256, self.last_intent)
        if any(value is not None for value in cache) and any(
            value is None for value in cache
        ):
            raise ValueError(
                "decision cache requires tick, packet hash and intent together"
            )
        targets = tuple(row.target_id for row in self.consumed_sources)
        if len(set(targets)) != len(targets):
            raise ValueError("consumed sources must have distinct target identities")
        if self.last_processed_tick is not None:
            if any(
                row.source_tick > self.last_processed_tick
                for row in self.consumed_sources
            ):
                raise ValueError("consumed source cannot come from a future tick")
            if (
                self.active_plan is not None
                and self.active_plan.started_tick > self.last_processed_tick
            ):
                raise ValueError("active plan cannot start after its decision")
        return self


def investigation_packet_sha256(packet: ObservationPacket) -> str:
    """Bind the cached decision to every entitled input, independent of key order."""

    encoded = json.dumps(
        packet.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _text(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"investigation source requires a nonempty {key}")
    return value


def _identities(payload: Mapping[str, object], key: str) -> tuple[str, ...]:
    value = payload.get(key)
    if not isinstance(value, (list, tuple)) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise ValueError(f"public roster requires {key} identities")
    result = tuple(str(item) for item in value)
    if len(set(result)) != len(result):
        raise ValueError("public roster contains duplicate identities")
    return result


def _sighting(
    row: EpisodicEvent, public_map: PublicMapView
) -> InvestigationObservation:
    payload = row.payload
    source_tick = payload.get("source_tick")
    if type(source_tick) is not int or source_tick != row.tick:
        raise ValueError(
            "investigation requires an actual source tick matching its row"
        )
    room = _text(payload, "to_room" if row.type == "saw_player_move" else "room")
    if room not in public_map.room_ids:
        raise ValueError("investigation sighting names a room outside the public map")
    return InvestigationObservation.model_validate(
        {
            "target_id": _text(payload, "player_id"),
            "source_observation_id": row.observation_id,
            "source_tick": source_tick,
            "last_known_room": room,
            "observation_phase": payload.get("observation_phase"),
            "observation_order": payload.get("observation_order"),
        }
    )


def _clock(row: InvestigationObservation) -> tuple[int, int, int]:
    return (
        row.source_tick,
        int(row.observation_phase == "event"),
        row.observation_order if row.observation_order is not None else -1,
    )


def reduce_investigation_evidence(
    memory: AgentMemory, *, observer_id: str, tick: int, public_map: PublicMapView
) -> InvestigationEvidence:
    """Reduce owned typed sources; public accounts never become private sightings.

    Missing timing on an observed placement is refused: version-1 clocks cannot
    silently acquire version-2 meaning. A public regroup is not a new sighting.
    The caller owns this memory; no current hidden roster or position is accepted.
    """

    if type(tick) is not int or tick < 0 or not observer_id:
        raise ValueError("investigation requires an observer and nonnegative tick")
    known = {observer_id}
    dead: set[str] = set()
    latest: dict[str, InvestigationObservation] = {}
    placements: dict[tuple[str, tuple[int, int, int]], str] = {}
    for row in memory.episodic.recent(since_tick=0):
        if row.tick > tick:
            raise ValueError("investigation memory contains a future source")
        if row.type == "public_meeting_roster" and row.provenance == "public":
            living = _identities(row.payload, "living_ids")
            announced_dead = _identities(row.payload, "dead_ids")
            if set(living) & set(announced_dead):
                raise ValueError("public living and dead identities overlap")
            known.update((*living, *announced_dead))
            dead.update(announced_dead)
        elif row.provenance != "observed":
            continue
        elif row.type == "self_state":
            if _text(row.payload, "agent_id") != observer_id:
                raise ValueError("investigation memory belongs to a different observer")
        elif row.type == "saw_body":
            victim = _text(row.payload, "victim_id")
            known.add(victim)
            dead.add(victim)
        elif row.type in ("saw_player", "saw_player_move"):
            sighting = _sighting(row, public_map)
            known.add(sighting.target_id)
            if sighting.target_id == observer_id:
                continue
            key = sighting.target_id, _clock(sighting)
            prior_room = placements.get(key)
            if prior_room is not None and prior_room != sighting.last_known_room:
                raise ValueError("ambiguous simultaneous sightings disagree on room")
            placements[key] = sighting.last_known_room
            previous = latest.get(sighting.target_id)
            if previous is None or _clock(sighting) > _clock(previous):
                latest[sighting.target_id] = sighting
    for outcome in memory.meeting_history.outcomes:
        if outcome.end_tick > tick:
            raise ValueError("investigation memory contains a future meeting outcome")
        if outcome.ejected_id is not None:
            known.add(outcome.ejected_id)
            dead.add(outcome.ejected_id)
    return InvestigationEvidence(
        known_player_ids=tuple(sorted(known)),
        known_dead_ids=tuple(sorted(dead)),
        sightings=tuple(latest[target] for target in sorted(latest)),
    )
