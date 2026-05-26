// One agent: a PixiJS circle drawn at the center of its room, nudged by a
// deterministic per-agent jitter so multiple agents in one room don't fully
// overlap (DESIGN.md §7). The jitter offset is in screen pixels (not scaled),
// so tokens stay readably spread regardless of the map fit-to-canvas scale.
// Color is the agent's `PlayerView.color`. Dead / venting agents are filtered
// out upstream in MapView and never reach this component in the slice.

import type { Graphics } from "pixi.js";

import type { RoomView } from "../types/api";

interface AgentTokenProps {
  room: RoomView;
  jitterIndex: number;
  color: string;
  scale: number;
  offsetX: number;
  offsetY: number;
}

const TOKEN_RADIUS = 10;
const BORDER_COLOR = 0x0f172a;
const BORDER_WIDTH = 2;

// Six deterministic offsets around a room center (screen pixels).
const JITTER_OFFSETS: ReadonlyArray<{ dx: number; dy: number }> = [
  { dx: -20, dy: -20 },
  { dx: 20, dy: -20 },
  { dx: -20, dy: 20 },
  { dx: 20, dy: 20 },
  { dx: 0, dy: -30 },
  { dx: 0, dy: 30 },
];

export function AgentToken({
  room,
  jitterIndex,
  color,
  scale,
  offsetX,
  offsetY,
}: AgentTokenProps) {
  const centerX = offsetX + (room.position.x + room.size.width / 2) * scale;
  const centerY = offsetY + (room.position.y + room.size.height / 2) * scale;
  const offset = JITTER_OFFSETS[jitterIndex % JITTER_OFFSETS.length] ?? {
    dx: 0,
    dy: 0,
  };
  const x = centerX + offset.dx;
  const y = centerY + offset.dy;

  return (
    <pixiGraphics
      draw={(graphics: Graphics) => {
        graphics.clear();
        graphics.circle(x, y, TOKEN_RADIUS);
        graphics.fill(color);
        graphics.stroke({ width: BORDER_WIDTH, color: BORDER_COLOR });
      }}
    />
  );
}
