// A dead agent's body: an X glyph at the kill room's center (DESIGN.md §7).
// Bodies render directly from privileged `KillEventView`s (post-game spectator;
// see the mid-phase DTO audit). The marker is offset from the room center by a
// deterministic per-victim amount so it never sits on top of living tokens
// (which cluster within AgentToken's jitter radius) or other bodies. Once the
// body has been reported (`ReportBodyEventView` for the same victim), the marker
// swaps to a "discovered" style — a color shift plus an outline ring.

import type { Graphics } from "pixi.js";

import type { RoomView } from "../types/api";

interface BodyMarkerProps {
  room: RoomView;
  victimId: string;
  isDiscovered: boolean;
  scale: number;
  offsetX: number;
  offsetY: number;
}

const ARM = 9;
const STROKE_WIDTH = 3;
const UNDISCOVERED_COLOR = 0x991b1b;
const DISCOVERED_COLOR = 0xfca5a5;
const DISCOVERED_RING_COLOR = 0xfacc15;
const DISCOVERED_RING_WIDTH = 2;
// Bodies sit on a ring well outside AgentToken's ±30px jitter cluster so a
// marker never overlaps a living token sharing the room.
const RING_RADIUS = 46;

function hashString(value: string): number {
  let hash = 0;
  for (let i = 0; i < value.length; i++) {
    hash = (hash * 31 + value.charCodeAt(i)) >>> 0;
  }
  return hash;
}

// Deterministic per-victim placement: an angle on a fixed-radius ring, so each
// body lands in a stable spot and distinct victims spread around the room.
function bodyOffset(victimId: string): { dx: number; dy: number } {
  const angle = ((hashString(victimId) % 360) * Math.PI) / 180;
  return { dx: Math.cos(angle) * RING_RADIUS, dy: Math.sin(angle) * RING_RADIUS };
}

export function BodyMarker({
  room,
  victimId,
  isDiscovered,
  scale,
  offsetX,
  offsetY,
}: BodyMarkerProps) {
  const centerX = offsetX + (room.position.x + room.size.width / 2) * scale;
  const centerY = offsetY + (room.position.y + room.size.height / 2) * scale;
  const offset = bodyOffset(victimId);
  const x = centerX + offset.dx;
  const y = centerY + offset.dy;
  const color = isDiscovered ? DISCOVERED_COLOR : UNDISCOVERED_COLOR;

  return (
    <pixiGraphics
      draw={(graphics: Graphics) => {
        graphics.clear();
        graphics.moveTo(x - ARM, y - ARM);
        graphics.lineTo(x + ARM, y + ARM);
        graphics.moveTo(x + ARM, y - ARM);
        graphics.lineTo(x - ARM, y + ARM);
        graphics.stroke({ width: STROKE_WIDTH, color });
        if (isDiscovered) {
          graphics.circle(x, y, ARM + 4);
          graphics.stroke({
            width: DISCOVERED_RING_WIDTH,
            color: DISCOVERED_RING_COLOR,
          });
        }
      }}
    />
  );
}
