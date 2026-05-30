// The map canvas: one PixiJS Application rendering the full spectator view for
// the currently-selected replay at the current tick (DESIGN.md §7, §8.3).
// Layers, bottom to top: rooms, the static vent network, body markers from past
// kills, living agent tokens (tweened between adjacent ticks), and a sabotage
// tint. Live game streaming, camera controls, and vent-traversal animation are
// out of scope (replay-only spectator).
//
// Rooms are positioned in abstract grid units (see engine/maps/canonical_1.yaml),
// so we compute a single uniform fit-to-canvas transform (scale + offset) from
// the room bounding box and thread it through to children. Token jitter, body
// offsets, radius, border, and label font stay in screen pixels so they read
// consistently regardless of the scale.
//
// Performance (Task 6.7; audit K-K-2 / G-G-1, DESIGN.md §11.4): every value that
// depends only on the loaded replay — the lookup Maps, color map, vent edges,
// fit transform, and the per-tick cumulative body state — is memoized on
// `currentReplay` identity, so a tick step rebuilds none of it. Body discovery
// is precomputed into a tick-indexed array (one forward pass per replay) and
// read in O(1), replacing the former 0..currentTick re-scan on every render.

import { Application, extend } from "@pixi/react";
import { Container, Graphics, Text } from "pixi.js";
import { useEffect, useMemo, useRef } from "react";

import { useReplayStore } from "../store/replayStore";
import type { RoomView, TickView, VentView } from "../types/api";
import { AgentToken } from "./AgentToken";
import { BodyMarker } from "./BodyMarker";
import { RoomRect } from "./RoomRect";
import { SabotageOverlay } from "./SabotageOverlay";
import { VentEdge } from "./VentEdge";

// Register the PixiJS display classes used as @pixi/react JSX elements
// (<pixiContainer>, <pixiGraphics>, <pixiText>).
extend({ Container, Graphics, Text });

const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 600;
const CANVAS_PADDING = 32;
const BACKGROUND_COLOR = 0x0f172a;

interface MapTransform {
  scale: number;
  offsetX: number;
  offsetY: number;
}

interface VentEdgeSpec {
  key: string;
  fromRoom: RoomView;
  toRoom: RoomView;
}

interface BodySpec {
  victimId: string;
  roomId: string;
  isDiscovered: boolean;
}

const NO_BODIES: readonly BodySpec[] = [];

// Uniform transform that fits the rooms' bounding box into the padded canvas,
// preserving aspect ratio and centering the content.
function computeTransform(rooms: readonly RoomView[]): MapTransform {
  if (rooms.length === 0) {
    return { scale: 1, offsetX: 0, offsetY: 0 };
  }

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const room of rooms) {
    minX = Math.min(minX, room.position.x);
    minY = Math.min(minY, room.position.y);
    maxX = Math.max(maxX, room.position.x + room.size.width);
    maxY = Math.max(maxY, room.position.y + room.size.height);
  }

  const contentWidth = maxX - minX;
  const contentHeight = maxY - minY;
  const availWidth = CANVAS_WIDTH - 2 * CANVAS_PADDING;
  const availHeight = CANVAS_HEIGHT - 2 * CANVAS_PADDING;
  const scale = Math.min(availWidth / contentWidth, availHeight / contentHeight);
  const offsetX =
    CANVAS_PADDING + (availWidth - contentWidth * scale) / 2 - minX * scale;
  const offsetY =
    CANVAS_PADDING + (availHeight - contentHeight * scale) / 2 - minY * scale;
  return { scale, offsetX, offsetY };
}

// One edge per unique room pair: a vent declared A->B and its mirror B->A
// collapse to a single line. Edges referencing an unknown room are skipped.
function buildVentEdges(
  vents: readonly VentView[],
  roomsById: ReadonlyMap<string, RoomView>,
): VentEdgeSpec[] {
  const seen = new Set<string>();
  const edges: VentEdgeSpec[] = [];
  for (const vent of vents) {
    for (const connectedRoomId of vent.connected_room_ids) {
      const a = vent.room_id;
      const b = connectedRoomId;
      if (a === b) {
        continue;
      }
      const key = a < b ? `${a}|${b}` : `${b}|${a}`;
      if (seen.has(key)) {
        continue;
      }
      seen.add(key);
      const fromRoom = roomsById.get(a);
      const toRoom = roomsById.get(b);
      if (fromRoom === undefined || toRoom === undefined) {
        continue;
      }
      edges.push({ key, fromRoom, toRoom });
    }
  }
  return edges;
}

// One forward pass over the whole replay yields the bodies visible at each tick:
// `result[t]` is the body set as of tick `t` — one per victim killed at or
// before `t`, flagged discovered once a report_body event has fired for that
// victim. Kill events carry the room directly (privileged spectator DTO; see the
// mid-phase DTO audit). The set changes only on kill / report_body events, so
// the same array reference is shared across the unchanged runs between them; the
// render path then indexes `result[currentTick]` in O(1) instead of re-scanning
// 0..currentTick on every step (Task 6.7; audit K-K-2 / G-G-1).
function buildBodyStatesByTick(ticks: readonly TickView[]): BodySpec[][] {
  const result: BodySpec[][] = new Array<BodySpec[]>(ticks.length);
  const killRoomByVictim = new Map<string, string>();
  const discovered = new Set<string>();
  let current: BodySpec[] = [];

  for (let t = 0; t < ticks.length; t++) {
    const tick = ticks[t];
    let changed = false;
    if (tick !== undefined) {
      for (const event of tick.events) {
        if (event.type === "kill") {
          killRoomByVictim.set(event.victim_id, event.room_id);
          changed = true;
        } else if (event.type === "report_body" && !discovered.has(event.body_of)) {
          discovered.add(event.body_of);
          changed = true;
        }
      }
    }
    if (changed) {
      current = [...killRoomByVictim.entries()].map(([victimId, roomId]) => ({
        victimId,
        roomId,
        isDiscovered: discovered.has(victimId),
      }));
    }
    result[t] = current;
  }
  return result;
}

export function MapView() {
  const currentReplay = useReplayStore((s) => s.currentReplay);
  const currentTick = useReplayStore((s) => s.currentTick);

  // Track the previously-rendered tick and replay so we can tell a single-step
  // advance (tween) from a multi-tick jump or a replay switch (both snap). Both
  // refs lag the current render by one commit (updated in effects below).
  const gameId = currentReplay?.metadata.game_id ?? null;
  const prevTickRef = useRef(currentTick);
  const prevGameIdRef = useRef<string | null>(gameId);
  const prevTick = prevTickRef.current;
  // selectReplay resets currentTick to 0, which could read as a 1->0 single
  // step; gate animation on the replay being unchanged so a switch always snaps
  // (otherwise reused-by-agent_id tokens would tween from the prior game).
  const sameReplay = prevGameIdRef.current === gameId;
  useEffect(() => {
    prevTickRef.current = currentTick;
  }, [currentTick]);
  useEffect(() => {
    prevGameIdRef.current = gameId;
  }, [gameId]);

  // Per-replay invariants, memoized on `currentReplay` identity so a tick step
  // never rebuilds them (Task 6.7; audit K-K-2 / G-G-1). They collapse to empty
  // defaults when no replay is loaded, keeping the hooks unconditional ahead of
  // the null guard below (rules of hooks).
  const transform = useMemo<MapTransform>(
    () => computeTransform(currentReplay?.map.rooms ?? []),
    [currentReplay],
  );
  const roomsById = useMemo<ReadonlyMap<string, RoomView>>(
    () => new Map((currentReplay?.map.rooms ?? []).map((room) => [room.id, room])),
    [currentReplay],
  );
  const playerIndexById = useMemo<ReadonlyMap<string, number>>(
    () =>
      new Map(
        (currentReplay?.players ?? []).map((player, index) => [
          player.agent_id,
          index,
        ]),
      ),
    [currentReplay],
  );
  const colorById = useMemo<ReadonlyMap<string, string>>(
    () =>
      new Map(
        (currentReplay?.players ?? []).map((player) => [
          player.agent_id,
          player.color,
        ]),
      ),
    [currentReplay],
  );
  const ventEdges = useMemo<VentEdgeSpec[]>(
    () => buildVentEdges(currentReplay?.map.vents ?? [], roomsById),
    [currentReplay, roomsById],
  );
  const bodyStatesByTick = useMemo<BodySpec[][]>(
    () => buildBodyStatesByTick(currentReplay?.ticks ?? []),
    [currentReplay],
  );

  if (currentReplay === null) {
    return (
      <div
        className="flex items-center justify-center rounded border border-slate-700 bg-slate-950 text-slate-400"
        style={{ width: CANVAS_WIDTH, height: CANVAS_HEIGHT }}
      >
        Select a replay to view the map.
      </div>
    );
  }

  const rooms = currentReplay.map.rooms;
  const tick = currentReplay.ticks[currentTick];
  const { scale, offsetX, offsetY } = transform;

  // O(1) lookup into the precomputed cumulative body state. Mirrors the former
  // scan's `min(currentTick, ticks.length - 1)` clamp exactly: an out-of-range
  // (or, defensively, negative) index falls through to no bodies, just as the
  // old 0..lastTick loop yielded an empty set.
  const bodyIndex = Math.min(currentTick, currentReplay.ticks.length - 1);
  const bodies = bodyStatesByTick[bodyIndex] ?? NO_BODIES;
  const sabotageActive = tick?.sabotage_active ?? [];
  // A single-tick step within the same replay animates; scrubs / snap-to-meeting
  // jumps and replay switches snap instantly.
  const animate = sameReplay && Math.abs(currentTick - prevTick) === 1;

  const agentStates = tick?.agent_states ?? [];
  const tokens = agentStates
    .filter((agent) => agent.is_alive && agent.room_id !== null && !agent.is_venting)
    .flatMap((agent) => {
      const room = agent.room_id === null ? undefined : roomsById.get(agent.room_id);
      const color = colorById.get(agent.agent_id);
      const jitterIndex = playerIndexById.get(agent.agent_id);
      if (room === undefined || color === undefined || jitterIndex === undefined) {
        return [];
      }
      return [
        <AgentToken
          key={agent.agent_id}
          room={room}
          jitterIndex={jitterIndex}
          color={color}
          scale={scale}
          offsetX={offsetX}
          offsetY={offsetY}
          animate={animate}
        />,
      ];
    });

  const bodyMarkers = bodies.flatMap((body) => {
    const room = roomsById.get(body.roomId);
    if (room === undefined) {
      return [];
    }
    return [
      <BodyMarker
        key={body.victimId}
        room={room}
        placementIndex={playerIndexById.get(body.victimId) ?? 0}
        isDiscovered={body.isDiscovered}
        scale={scale}
        offsetX={offsetX}
        offsetY={offsetY}
      />,
    ];
  });

  return (
    <Application
      width={CANVAS_WIDTH}
      height={CANVAS_HEIGHT}
      background={BACKGROUND_COLOR}
    >
      {rooms.map((room) => (
        <RoomRect
          key={room.id}
          room={room}
          scale={scale}
          offsetX={offsetX}
          offsetY={offsetY}
        />
      ))}
      {ventEdges.map((edge) => (
        <VentEdge
          key={edge.key}
          fromRoom={edge.fromRoom}
          toRoom={edge.toRoom}
          scale={scale}
          offsetX={offsetX}
          offsetY={offsetY}
        />
      ))}
      {bodyMarkers}
      {tokens}
      <SabotageOverlay
        width={CANVAS_WIDTH}
        height={CANVAS_HEIGHT}
        activeKinds={sabotageActive}
      />
    </Application>
  );
}
