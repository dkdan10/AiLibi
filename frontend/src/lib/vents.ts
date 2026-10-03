// The map's vent trips, paired from the served frames exactly as the engine
// recorded them.
//
// A trip starts at a dive (a `vent` event with phase `enter`, whose rooms are
// both the dive room) and ends one of two ways:
//
//   • at its EXIT event, whose `to_room_id` is where the impostor came up — the
//     destination is only known there;
//   • without one, at the last frame where the served `is_venting` still holds
//     for that actor. That is a meeting whose regroup pulled the impostor out
//     of the vent (the engine emits no exit event for it), an ejection, or the
//     game's end.
//
// Every dive yields exactly one trip, and a later dive never overwrites an
// earlier one. The rule this replaces kept one pending dive per actor, so a
// trip a regroup closed was overwritten by that actor's next dive and drew
// nothing, and a dive with no exit degraded to a one-tick pulse: an impostor
// inside a vent vanished from the omniscient map for the rest of its trip.
//
// Three shapes come out, and the map draws each differently:
//
//   • "travel" — an exit into another room: a glide from the dive room to the
//     room it came up in, over the whole window;
//   • "stay"   — an exit into the room it dived in (the impostor looked out and
//     came back up): a wait in that room for the whole window, with no travel;
//   • "closed" — no exit: an in-vent marker at the dive room until the trip's
//     last venting frame, with no emergence.
//
// Pure functions over the view-model — no React, no Pixi. The structural slices
// below are satisfied by a real `TickView` and by the committed skeleton dump
// the tests walk (`replay-skeleton.fixture.json`).

import type { TickEventView } from "../types/api";

/** The slice of one agent's frame state this module reads. */
export interface VentAgentSlice {
  readonly agent_id: string;
  readonly is_venting: boolean;
}

/** The slice of a `TickView` this module reads. */
export interface VentFrameSlice {
  readonly tick: number;
  readonly events: readonly TickEventView[];
  readonly agent_states: readonly VentAgentSlice[];
}

export type VentTripShape = "travel" | "stay" | "closed";

/** One vent trip as the map draws it. */
export interface VentTrip {
  readonly actorId: string;
  /** The dive's tick. */
  readonly enterTick: number;
  /** The exit's tick, or the last frame tick on which the actor was still venting. */
  readonly endTick: number;
  /** The dive room. */
  readonly fromRoomId: string;
  /** Where the impostor came up; the dive room for a stay or a closed trip. */
  readonly toRoomId: string;
  readonly shape: VentTripShape;
}

interface OpenDive {
  readonly enterTick: number;
  readonly fromRoomId: string;
  /** The last frame tick on which the actor's `is_venting` held. */
  lastVentingTick: number;
}

/**
 * Every vent trip in the replay, one per dive, in the order they end.
 *
 * Raises on bytes the engine cannot produce: an exit with no open dive, or a
 * second dive while the first is still venting.
 */
export function ventTrips(frames: readonly VentFrameSlice[]): VentTrip[] {
  const trips: VentTrip[] = [];
  const open = new Map<string, OpenDive>();
  const close = (actorId: string, dive: OpenDive): void => {
    open.delete(actorId);
    trips.push({
      actorId,
      enterTick: dive.enterTick,
      endTick: dive.lastVentingTick,
      fromRoomId: dive.fromRoomId,
      toRoomId: dive.fromRoomId,
      shape: "closed",
    });
  };
  for (const frame of frames) {
    const venting = new Set(
      frame.agent_states.filter((state) => state.is_venting).map((state) => state.agent_id),
    );
    // A dive still open from an earlier frame whose actor is no longer venting
    // here ended without an exit on the previous venting frame.
    const exiting = new Set(
      frame.events.flatMap((event) =>
        event.type === "vent" && event.phase === "exit" ? [event.actor_id] : [],
      ),
    );
    for (const [actorId, dive] of [...open]) {
      if (!venting.has(actorId) && !exiting.has(actorId)) {
        close(actorId, dive);
      }
    }
    for (const event of frame.events) {
      if (event.type !== "vent") continue;
      if (event.phase === "enter") {
        if (open.has(event.actor_id)) {
          throw new Error(
            `${event.actor_id} dived at tick ${event.tick} while still inside a vent`,
          );
        }
        open.set(event.actor_id, {
          enterTick: event.tick,
          fromRoomId: event.from_room_id,
          lastVentingTick: event.tick,
        });
        continue;
      }
      const dive = open.get(event.actor_id);
      if (dive === undefined) {
        throw new Error(`${event.actor_id} left a vent at tick ${event.tick} it never entered`);
      }
      open.delete(event.actor_id);
      trips.push({
        actorId: event.actor_id,
        enterTick: dive.enterTick,
        endTick: event.tick,
        fromRoomId: dive.fromRoomId,
        toRoomId: event.to_room_id,
        shape: event.to_room_id === dive.fromRoomId ? "stay" : "travel",
      });
    }
    // Every dive still open here was venting on this frame (the rest were
    // closed above) or began on it.
    for (const dive of open.values()) {
      dive.lastVentingTick = frame.tick;
    }
  }
  for (const [actorId, dive] of [...open]) {
    close(actorId, dive);
  }
  return trips;
}

/** The trips whose window covers `tick`, inclusive of both ends, by actor. */
export function activeTrips(trips: readonly VentTrip[], tick: number): Map<string, VentTrip> {
  const active = new Map<string, VentTrip>();
  for (const trip of trips) {
    if (trip.enterTick <= tick && tick <= trip.endTick) {
      active.set(trip.actorId, trip);
    }
  }
  return active;
}

/** The marker's size, relative to a token, while a held trip is inside the vent. */
export const IN_VENT_MARKER_SCALE = 0.6;

/** Where and how a trip is drawn on one tick of its window. */
export interface TripPose {
  /** 0 at the dive room, 1 where it came up. */
  readonly progress: number;
  /** Whether the actor is still inside the vent on this tick. */
  readonly inVent: boolean;
  /**
   * A held trip's marker size: the in-vent size while inside, full size on the
   * exit tick of a stay. `null` for a travel, whose size follows its glide.
   */
  readonly heldScale: number | null;
}

/**
 * A trip's pose at `tick`. Only a travel moves; a stay and a closed trip hold
 * at the dive room for their whole window. Every trip is inside the vent until
 * its exit tick; a closed trip has no exit, so it never comes up.
 */
export function tripPose(trip: VentTrip, tick: number): TripPose {
  const inVent = trip.shape === "closed" || tick < trip.endTick;
  if (trip.shape !== "travel") {
    return { progress: 0, inVent, heldScale: inVent ? IN_VENT_MARKER_SCALE : 1 };
  }
  const span = trip.endTick - trip.enterTick;
  const progress = span > 0 ? Math.min(1, Math.max(0, (tick - trip.enterTick) / span)) : 1;
  return { progress, inVent, heldScale: null };
}
