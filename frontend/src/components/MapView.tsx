// The map canvas: one PixiJS Application rendering the rooms + agent tokens for
// the currently-selected replay at the current tick (DESIGN.md §7). This is the
// vertical-slice view — rooms and living agents only. Sabotage, vents, bodies,
// and tweening land in 4.4.5.
//
// Rooms are positioned in abstract grid units (see engine/maps/canonical_1.yaml),
// so we compute a single uniform fit-to-canvas transform (scale + offset) from
// the room bounding box and thread it through to children. Token jitter, radius,
// border, and label font stay in screen pixels so they read consistently
// regardless of the scale.

import { Application, extend } from "@pixi/react";
import { Container, Graphics, Text } from "pixi.js";

import { useReplayStore } from "../store/replayStore";
import type { RoomView } from "../types/api";
import { AgentToken } from "./AgentToken";
import { RoomRect } from "./RoomRect";

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

export function MapView() {
  const currentReplay = useReplayStore((s) => s.currentReplay);
  const currentTick = useReplayStore((s) => s.currentTick);

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
  const { scale, offsetX, offsetY } = computeTransform(rooms);

  const roomsById = new Map(rooms.map((room) => [room.id, room]));
  const playerIndexById = new Map(
    currentReplay.players.map((player, index) => [player.agent_id, index]),
  );
  const colorById = new Map(
    currentReplay.players.map((player) => [player.agent_id, player.color]),
  );

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
      {tokens}
    </Application>
  );
}
