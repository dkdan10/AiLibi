// The map's vent trips, pinned against the bytes the API serves.
//
// THE INVARIANT. Every dive yields exactly one trip; a trip ends at its exit,
// or, without one, on the last frame where the served `is_venting` still holds
// for its actor. Over the promoted 9p2i set that reproduces the gameplay
// census's own tables (`eval/gameplay_census.py`, `ticks_inside_per_trip` and
// `trips_closed_by_regroup`, published by
// `uv run python scripts/publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout`):
// 140 dives, 72 surfaced trips whose windows read 1 tick 49, 2 ticks 3, 3 ticks
// 15 and 4 ticks 5, and 47 trips a regroup closed.
//
// `retiredPairingRule` below is the NEGATIVE CONTROL: the pairing `MapView.tsx`
// used before, kept verbatim. It runs the same census and fails it — 22 dives
// draw nothing at all and 46 degrade to a one-tick pulse — so the census is a
// gate the shipped rule passes, not prose it satisfies by construction.

import { describe, expect, it } from "vitest";

import {
  corpusDigest,
  readSkeleton,
  type SkeletonFrame,
  type SkeletonGame,
  skeletonSet,
} from "./skeleton.testkit";
import {
  activeTrips,
  IN_VENT_MARKER_SCALE,
  tripPose,
  type VentFrameSlice,
  type VentTrip,
  ventTrips,
} from "./vents";
import type { TickEventView } from "../types/api";

const SKELETON = readSkeleton();

// ── the retired rule, verbatim (the negative control) ───────────────────────

interface RetiredSegment {
  actorId: string;
  enterTick: number;
  exitTick: number;
  fromRoomId: string;
  toRoomId: string;
}

/** `MapView.tsx`'s `buildVentSegments` before this change, kept verbatim. */
function retiredPairingRule(ticks: readonly { readonly events: readonly TickEventView[] }[]): RetiredSegment[] {
  const segments: RetiredSegment[] = [];
  const pendingDive = new Map<string, { enterTick: number; fromRoomId: string }>();
  for (const tick of ticks) {
    for (const event of tick.events) {
      if (event.type !== "vent") continue;
      if (event.phase === "enter") {
        pendingDive.set(event.actor_id, {
          enterTick: event.tick,
          fromRoomId: event.from_room_id,
        });
      } else {
        const dive = pendingDive.get(event.actor_id);
        pendingDive.delete(event.actor_id);
        segments.push({
          actorId: event.actor_id,
          enterTick: dive?.enterTick ?? event.tick - Math.max(1, event.traversal_ticks),
          exitTick: event.tick,
          fromRoomId: dive?.fromRoomId ?? event.from_room_id,
          toRoomId: event.to_room_id,
        });
      }
    }
  }
  for (const [actorId, dive] of pendingDive) {
    segments.push({
      actorId,
      enterTick: dive.enterTick,
      exitTick: dive.enterTick + 1,
      fromRoomId: dive.fromRoomId,
      toRoomId: dive.fromRoomId,
    });
  }
  return segments;
}

// ── the census ──────────────────────────────────────────────────────────────

interface TripCensus {
  dives: number;
  /** Dives no drawn trip starts from. */
  divesWithoutTrip: number;
  /** Trips that end on a frame where their actor is neither exiting nor last seen venting. */
  misplacedEnds: number;
  /** Surfaced trips by ticks inside, restarting at a meeting boundary. */
  ticksInside: Record<string, number>;
  /** Trips with no exit, ended on a meeting frame the game survived, actor not ejected. */
  closedByRegroup: number;
  closedAtGameEnd: number;
  closedByEjection: number;
}

interface DrawnTrip {
  readonly actorId: string;
  readonly enterTick: number;
  readonly endTick: number;
  readonly exited: boolean;
}

function dives(game: SkeletonGame): { actorId: string; tick: number }[] {
  return game.replay.ticks.flatMap((frame) =>
    frame.events.flatMap((event) =>
      event.type === "vent" && event.phase === "enter" ? [{ actorId: event.actor_id, tick: event.tick }] : [],
    ),
  );
}

function exitTicks(game: SkeletonGame): Set<string> {
  return new Set(
    game.replay.ticks.flatMap((frame) =>
      frame.events.flatMap((event) =>
        event.type === "vent" && event.phase === "exit" ? [`${event.actor_id}@${event.tick}`] : [],
      ),
    ),
  );
}

function venting(frame: SkeletonFrame, actorId: string): boolean {
  return frame.agent_states.some((state) => state.agent_id === actorId && state.is_venting);
}

function census(games: readonly SkeletonGame[], draw: (game: SkeletonGame) => DrawnTrip[]): TripCensus {
  const total: TripCensus = {
    dives: 0,
    divesWithoutTrip: 0,
    misplacedEnds: 0,
    ticksInside: {},
    closedByRegroup: 0,
    closedAtGameEnd: 0,
    closedByEjection: 0,
  };
  for (const game of games) {
    const frames = game.replay.ticks;
    const meetings = game.replay.meetings;
    const last = frames[frames.length - 1];
    if (last === undefined) throw new Error(`${game.gameId} has no frames`);
    const drawn = draw(game);
    const exits = exitTicks(game);
    for (const dive of dives(game)) {
      total.dives += 1;
      if (!drawn.some((trip) => trip.actorId === dive.actorId && trip.enterTick === dive.tick)) {
        total.divesWithoutTrip += 1;
      }
    }
    for (const trip of drawn) {
      if (trip.exited) {
        if (!exits.has(`${trip.actorId}@${trip.endTick}`)) total.misplacedEnds += 1;
        const anchor = Math.max(
          trip.enterTick,
          ...meetings.filter((meeting) => meeting.tick < trip.endTick).map((meeting) => meeting.tick),
        );
        const key = String(trip.endTick - anchor);
        total.ticksInside[key] = (total.ticksInside[key] ?? 0) + 1;
        continue;
      }
      const index = frames.findIndex((frame) => frame.tick === trip.endTick);
      const endFrame = frames[index];
      const next = frames[index + 1];
      if (endFrame === undefined || !venting(endFrame, trip.actorId) || (next !== undefined && venting(next, trip.actorId))) {
        total.misplacedEnds += 1;
        continue;
      }
      // The census's order: an ejection at that meeting, then a regroup (a
      // meeting the game survives), then the game's end.
      const meeting = meetings.find((candidate) => candidate.tick === trip.endTick);
      if (meeting !== undefined && meeting.ejected === trip.actorId) {
        total.closedByEjection += 1;
      } else if (meeting !== undefined && endFrame !== last) {
        total.closedByRegroup += 1;
      } else if (endFrame === last) {
        total.closedAtGameEnd += 1;
      } else {
        total.misplacedEnds += 1;
      }
    }
  }
  return total;
}

const shipped = (game: SkeletonGame): DrawnTrip[] =>
  ventTrips(game.replay.ticks).map((trip) => ({
    actorId: trip.actorId,
    enterTick: trip.enterTick,
    endTick: trip.endTick,
    exited: trip.shape !== "closed",
  }));

// The retired rule's segments, read back the way it drew them: a segment whose
// exit tick carries the actor's real exit event surfaced; any other is the
// one-tick pulse its unmatched branch drew.
function retired(game: SkeletonGame): DrawnTrip[] {
  const exits = exitTicks(game);
  return retiredPairingRule(game.replay.ticks).map((segment) => {
    const exited = exits.has(`${segment.actorId}@${segment.exitTick}`);
    return {
      actorId: segment.actorId,
      enterTick: segment.enterTick,
      endTick: segment.exitTick,
      exited,
    };
  });
}

function pulses(game: SkeletonGame): number {
  const exits = exitTicks(game);
  return retiredPairingRule(game.replay.ticks).filter(
    (segment) => !exits.has(`${segment.actorId}@${segment.exitTick}`),
  ).length;
}

describe("vent trips over the committed served payloads", () => {
  it.each(["9p2i", "4p1i"])("%s: the skeleton dump still matches the committed corpus", (name) => {
    const set = skeletonSet(SKELETON, name);
    expect(corpusDigest(name)).toBe(set.corpusSha256);
    expect(set.games).toHaveLength(50);
  });

  it("9p2i: every dive is one trip, and the census's tables come back", () => {
    const set = skeletonSet(SKELETON, "9p2i");
    expect(set.meetingReset).toBe("hub_with_grace");
    expect(census(set.games, shipped)).toEqual({
      dives: 140,
      divesWithoutTrip: 0,
      misplacedEnds: 0,
      // `ticks_inside_per_trip`: 72 surfaced trips.
      ticksInside: { "1": 49, "2": 3, "3": 15, "4": 5 },
      // `trips_closed_by_regroup`: 47 of 140.
      closedByRegroup: 47,
      // The other 21 trips with no exit, which the census leaves to subtraction:
      // 19 actors ejected by the meeting that found them inside a vent, and 2
      // still inside when the game ended (this walk's split).
      closedByEjection: 19,
      closedAtGameEnd: 2,
    });
    const trips = set.games.flatMap((game) => ventTrips(game.replay.ticks));
    expect(trips).toHaveLength(140);
    expect(trips.filter((trip) => trip.shape === "stay")).toHaveLength(44);
    expect(trips.filter((trip) => trip.shape === "travel")).toHaveLength(28);
    expect(trips.filter((trip) => trip.shape === "closed")).toHaveLength(68);
  });

  it("9p2i: the retired pairing rule fails the same census", () => {
    const set = skeletonSet(SKELETON, "9p2i");
    const result = census(set.games, retired);
    expect(result.divesWithoutTrip).toBe(22);
    expect(set.games.reduce((sum, game) => sum + pulses(game), 0)).toBe(46);
    // Its pulses end a tick after the dive, wherever the trip really ended.
    expect(result.misplacedEnds).toBeGreaterThan(0);
    expect(result.closedByRegroup).toBeLessThan(47);
  });

  it("4p1i: every dive is one trip, and a dive with no exit holds its marker", () => {
    const set = skeletonSet(SKELETON, "4p1i");
    expect(set.meetingReset).toBe("preserve");
    const result = census(set.games, shipped);
    expect(result.dives).toBe(44);
    expect(result.divesWithoutTrip).toBe(0);
    expect(result.misplacedEnds).toBe(0);
    // Nothing regroups on a preserve recording.
    expect(result.closedByRegroup).toBe(0);
    const trips = set.games.flatMap((game) => ventTrips(game.replay.ticks));
    expect(trips).toHaveLength(44);
    const closed = trips.filter((trip) => trip.shape === "closed");
    expect(closed).toHaveLength(result.closedAtGameEnd + result.closedByEjection);
    // The retired rule drew those as a one-tick pulse each.
    expect(set.games.reduce((sum, game) => sum + pulses(game), 0)).toBe(closed.length);
  });
});

// ── hand-built frames: the rules the corpus cannot isolate ──────────────────

function dive(actor: string, tick: number, room: string): TickEventView {
  return { type: "vent", tick, actor_id: actor, phase: "enter", from_room_id: room, to_room_id: room, traversal_ticks: 0 };
}

function exit(actor: string, tick: number, from: string, to: string): TickEventView {
  return { type: "vent", tick, actor_id: actor, phase: "exit", from_room_id: from, to_room_id: to, traversal_ticks: 1 };
}

function frame(tick: number, events: readonly TickEventView[], inVent: readonly string[]): VentFrameSlice {
  return {
    tick,
    events,
    agent_states: ["p-1", "p-2"].map((agentId) => ({ agent_id: agentId, is_venting: inVent.includes(agentId) })),
  };
}

describe("ventTrips on hand-built frames", () => {
  it("never lets a later dive overwrite an earlier one a regroup closed", () => {
    // p-1 dives at 1 and is pulled out by the meeting at 3 (no exit event);
    // it dives again at 6 and comes up at 7 elsewhere.
    const trips = ventTrips([
      frame(1, [dive("p-1", 1, "STORAGE")], ["p-1"]),
      frame(2, [], ["p-1"]),
      frame(3, [], ["p-1"]),
      frame(4, [], []),
      frame(5, [], []),
      frame(6, [dive("p-1", 6, "ADMIN")], ["p-1"]),
      frame(7, [exit("p-1", 7, "ADMIN", "CAFETERIA")], []),
    ]);
    expect(trips).toEqual([
      { actorId: "p-1", enterTick: 1, endTick: 3, fromRoomId: "STORAGE", toRoomId: "STORAGE", shape: "closed" },
      { actorId: "p-1", enterTick: 6, endTick: 7, fromRoomId: "ADMIN", toRoomId: "CAFETERIA", shape: "travel" },
    ]);
  });

  it("keeps a preserve trip that spans a meeting as one segment", () => {
    // Under `preserve` the meeting at 2 leaves p-2 inside the vent; it surfaces
    // where it dived at 4. One trip, a stay, over the whole window.
    const trips = ventTrips([
      frame(1, [dive("p-2", 1, "MEDBAY")], ["p-2"]),
      frame(2, [], ["p-2"]),
      frame(3, [], ["p-2"]),
      frame(4, [exit("p-2", 4, "MEDBAY", "MEDBAY")], []),
    ]);
    expect(trips).toEqual([
      { actorId: "p-2", enterTick: 1, endTick: 4, fromRoomId: "MEDBAY", toRoomId: "MEDBAY", shape: "stay" },
    ]);
  });

  it("ends a trip still open at the last frame on that frame", () => {
    const trips = ventTrips([frame(5, [dive("p-1", 5, "LABS")], ["p-1"]), frame(6, [], ["p-1"])]);
    expect(trips).toEqual([
      { actorId: "p-1", enterTick: 5, endTick: 6, fromRoomId: "LABS", toRoomId: "LABS", shape: "closed" },
    ]);
  });

  it("raises on bytes the engine cannot produce", () => {
    expect(() => ventTrips([frame(1, [exit("p-1", 1, "LABS", "ADMIN")], [])])).toThrow(/never entered/);
    expect(() =>
      ventTrips([frame(1, [dive("p-1", 1, "LABS")], ["p-1"]), frame(2, [dive("p-1", 2, "LABS")], ["p-1"])]),
    ).toThrow(/still inside a vent/);
  });

  it("poses each shape on its window", () => {
    const travel: VentTrip = { actorId: "p-1", enterTick: 2, endTick: 6, fromRoomId: "A", toRoomId: "B", shape: "travel" };
    const stay: VentTrip = { ...travel, toRoomId: "A", shape: "stay" };
    const closed: VentTrip = { ...stay, shape: "closed" };
    expect(tripPose(travel, 2)).toEqual({ progress: 0, inVent: true, heldScale: null });
    expect(tripPose(travel, 4)).toEqual({ progress: 0.5, inVent: true, heldScale: null });
    expect(tripPose(travel, 6)).toEqual({ progress: 1, inVent: false, heldScale: null });
    expect(tripPose({ ...travel, endTick: 2 }, 2)).toEqual({ progress: 1, inVent: false, heldScale: null });
    // A stay waits at the in-vent size and comes up full size on its exit tick;
    // a closed trip never comes up.
    expect(tripPose(stay, 4)).toEqual({ progress: 0, inVent: true, heldScale: IN_VENT_MARKER_SCALE });
    expect(tripPose(stay, 6)).toEqual({ progress: 0, inVent: false, heldScale: 1 });
    expect(tripPose(closed, 6)).toEqual({ progress: 0, inVent: true, heldScale: IN_VENT_MARKER_SCALE });
    expect(IN_VENT_MARKER_SCALE).toBeLessThan(1);
    expect([...activeTrips([travel, { ...stay, actorId: "p-2", enterTick: 7, endTick: 8 }], 6).keys()]).toEqual(["p-1"]);
    expect([...activeTrips([travel], 1).keys()]).toEqual([]);
    expect([...activeTrips([travel], 7).keys()]).toEqual([]);
  });
});

// ── the property, over a generated family ───────────────────────────────────

/** A small deterministic generator (mulberry32), so the family is reproducible. */
function generator(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const ROOMS = ["ADMIN", "LABS", "STORAGE", "MEDBAY"];

interface PlannedTrip {
  actorId: string;
  enterTick: number;
  endTick: number;
  fromRoomId: string;
  toRoomId: string;
  shape: VentTrip["shape"];
}

/** Random, engine-shaped trips for two actors, and the frames that record them. */
function family(seed: number): { planned: PlannedTrip[]; frames: VentFrameSlice[] } {
  const random = generator(seed);
  const pick = (n: number): number => Math.floor(random() * n);
  const planned: PlannedTrip[] = [];
  const horizon = 40;
  for (const actorId of ["p-1", "p-2"]) {
    let tick = pick(4);
    while (tick < horizon - 1) {
      const length = 1 + pick(5);
      const end = Math.min(tick + length, horizon - 1);
      const fromRoomId = ROOMS[pick(ROOMS.length)] ?? "ADMIN";
      const kind = pick(3);
      const toRoomId = kind === 0 ? (ROOMS[pick(ROOMS.length)] ?? "ADMIN") : fromRoomId;
      const shape: VentTrip["shape"] =
        kind === 2 ? "closed" : toRoomId === fromRoomId ? "stay" : "travel";
      planned.push({ actorId, enterTick: tick, endTick: end, fromRoomId, toRoomId: shape === "closed" ? fromRoomId : toRoomId, shape });
      // A closed trip's actor leaves the vent on the frame after its end; a
      // surfaced one may dive again from the next tick on.
      tick = end + 1 + pick(4) + (shape === "closed" ? 1 : 0);
    }
  }
  const frames: VentFrameSlice[] = [];
  for (let tick = 0; tick < horizon; tick += 1) {
    const events: TickEventView[] = [];
    const inVent: string[] = [];
    for (const trip of planned) {
      if (trip.enterTick === tick) events.push(dive(trip.actorId, tick, trip.fromRoomId));
      if (trip.shape !== "closed" && trip.endTick === tick) {
        events.push(exit(trip.actorId, tick, trip.fromRoomId, trip.toRoomId));
      } else if (trip.enterTick <= tick && tick <= trip.endTick) {
        inVent.push(trip.actorId);
      }
    }
    frames.push(frame(tick, events, inVent));
  }
  return { planned, frames };
}

describe("every dive yields exactly one trip (a generated family)", () => {
  it("recovers 500 random two-actor schedules trip for trip", () => {
    let checked = 0;
    for (let seed = 1; seed <= 500; seed += 1) {
      const { planned, frames } = family(seed);
      const trips = ventTrips(frames);
      const key = (trip: PlannedTrip | VentTrip): string => `${trip.actorId}@${trip.enterTick}`;
      expect(trips.map(key).sort(), `seed ${seed}`).toEqual(planned.map(key).sort());
      for (const trip of trips) {
        expect(trip, `seed ${seed}`).toEqual(planned.find((candidate) => key(candidate) === key(trip)));
      }
      checked += planned.length;
    }
    // The family is not vacuous: it plans thousands of trips of every shape.
    expect(checked).toBeGreaterThan(2000);
  });

  it("is a family the retired rule fails", () => {
    // The same schedules under the retired pairing lose or truncate trips.
    let lost = 0;
    for (let seed = 1; seed <= 500; seed += 1) {
      const { planned, frames } = family(seed);
      const segments = retiredPairingRule(frames);
      for (const trip of planned) {
        const segment = segments.find(
          (candidate) => candidate.actorId === trip.actorId && candidate.enterTick === trip.enterTick,
        );
        if (segment === undefined || segment.exitTick !== trip.endTick) lost += 1;
      }
    }
    expect(lost).toBeGreaterThan(0);
  });
});
