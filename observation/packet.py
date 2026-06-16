from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

BodyId: TypeAlias = str
PlayerId: TypeAlias = str
Role: TypeAlias = Literal["CREWMATE", "IMPOSTOR"]
RoomId: TypeAlias = str
TaskId: TypeAlias = str


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class OwnKillView(_FrozenModel):
    """A kill the recipient itself committed this tick (DESIGN.md §1.3, §6.2).

    This rides the privileged self channel where ``role`` and
    ``fellow_impostor_ids`` live (Task 11.3): the engine excludes a killer from
    its own kill's witnesses (``engine/rules.py``), so the kill is never logged
    through the witness-gated ``visible_players`` channel and the body the
    killer made surfaces only as an ordinary ``saw_body`` sighting -- the killer
    narrating finding the body it created. Surfacing the kill here (legibility
    only -- the memory-fix probe FALSIFIED it as a survival lever,
    ``experiments/lab/report-memory-fix-probe.md``) lets the §6.2 renderer state
    the act plainly and suppress the self-victim "discovered body" line.

    It is populated ONLY for the killer (the entitled recipient) and is NEVER
    mirrored into the crew-visible ``PlayerView`` channel: a ``PlayerView`` kill
    action would fail the leak test, which requires every visible kill to be
    witness-permitted (``eval/leak_test.py``). ``victim_id`` is leak-allowed per
    the ``BodyView`` precedent; the field names carry no role information.
    """

    victim_id: PlayerId = Field(min_length=1)
    room: RoomId


class SelfView(_FrozenModel):
    room: RoomId
    role: Role
    # The agent's own next pending task, as the MAP task id (a ``game_map.tasks``
    # key), never the per-player instance id ``"{owner}:{map_task_id}"`` (DESIGN.md
    # §3.2). It is always the recipient's OWN task -- ``ObservationService`` scopes
    # it by owner, so it carries no other player's task and no ownership (§1.3). The
    # engine resolves ``(actor, pending_task_id)`` back to the agent's own instance,
    # so the map id round-trips through ``do_task`` and ``task_locations`` unchanged.
    pending_task_id: TaskId | None
    # Identities of the recipient's fellow impostor(s), excluding its own id.
    # This rides the already-privileged self channel where ``role`` lives: an
    # agent entitled to know its own role is, by the same logic, entitled to
    # know its own team (locked decision 3). It is populated ONLY for impostor
    # recipients (``()`` for every crewmate and for a sole impostor) and is
    # never mirrored into the crew-visible ``PlayerView`` channel, so the
    # DESIGN.md §1.3 observation firewall holds. Sorted for replay stability.
    fellow_impostor_ids: tuple[PlayerId, ...] = ()
    # Whether the recipient is currently inside a vent (DESIGN.md §3.4). This is
    # a non-role-bearing self-state bool: a player always knows its own position,
    # and a vented player is HIDDEN from every other agent's ``visible_players``
    # (engine/visibility.py), so this never appears on the crew-visible channel
    # and the §1.3 firewall holds. The impostor policy reads it to drive the
    # in-vent vent-exit branch (Task 11.1). Defaults ``False`` for crewmates and
    # for any player not in a vent.
    in_vent: bool = False
    # The kill the recipient itself committed this tick, or ``None`` (Task
    # 11.3). Like ``role`` / ``fellow_impostor_ids``, it rides the privileged
    # self channel and is populated ONLY for the actor: the engine excludes a
    # killer from its own kill's witnesses, so this is by construction never in
    # any other agent's packet (crewmate AND fellow impostor get ``None``) and
    # the §1.3 firewall holds. It is never mirrored into ``PlayerView``. Carries
    # no role-bearing field names; ``victim_id`` is leak-allowed per BodyView.
    own_kill: OwnKillView | None = None


class PlayerView(_FrozenModel):
    id: PlayerId
    room: RoomId
    action: str | None


class BodyView(_FrozenModel):
    """A body visible to the observer.

    ``victim_id`` formalizes the body's victim player id at the
    observation boundary (DESIGN.md §1.3 / Appendix A). It carries the
    same information that was previously inferrable from the
    ``body-{victim_id}-{tick}`` id format emitted by ``engine/rules.py``,
    so exposing it does not weaken the firewall -- it removes the
    agent→engine string coupling flagged as R-4 in
    ``audits/audit-2026-05-16-0036-reconciled.md``.
    """

    id: BodyId
    room: RoomId
    victim_id: PlayerId = Field(min_length=1)


class AudibleEvent(_FrozenModel):
    kind: Literal["vent_use_heard", "sabotage_alarm"]
    room: RoomId | None = None


class GlobalView(_FrozenModel):
    # ``tasks_completed`` / ``tasks_total`` count per-player task INSTANCES, not
    # map tasks (DESIGN.md §3.2): the denominator scales with the roster (9p/2i is
    # 14 instances over 12 map tasks) and equals the engine's win-condition total.
    tasks_completed: int
    tasks_total: int
    task_completion_percent: float
    sabotage_active: bool
    sabotage_kind: str | None
    # Public, role-blind repair channel for the active sabotage (DESIGN.md §8.3,
    # Task 11.5). Populated ONLY while a sabotage is active, from the map's
    # ``SabotageDefinition`` — identical across every role (leak-clean) so the
    # crew policy (11.6) can route to a repair room without ``agents/``->``engine/``
    # coupling. Default empty/false keeps non-sabotage and lights-era packets
    # byte-stable; ``sabotage_is_gating`` distinguishes a task-gating kind
    # (``reactor``) from a non-gating one (``lights``).
    sabotage_repair_rooms: tuple[RoomId, ...] = ()
    sabotage_is_gating: bool = False


class ObservationPacket(_FrozenModel):
    tick: int
    agent_id: PlayerId
    self_state: SelfView
    visible_players: tuple[PlayerView, ...]
    visible_bodies: tuple[BodyView, ...]
    audible_events: tuple[AudibleEvent, ...]
    global_state: GlobalView
    cooldown: int | None
