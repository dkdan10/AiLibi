// A dead agent's body: an X glyph at the kill room's center (DESIGN.md §7).
// Bodies render directly from privileged `KillEventView`s (post-game spectator;
// see the mid-phase DTO audit). The marker is offset from the room center by a
// deterministic per-victim amount (the victim's roster index spread by the
// golden angle) so it never sits on top of living tokens (which cluster within
// AgentToken's jitter radius) and so multiple bodies in one room fan out
// instead of overlapping. Once the body has been reported
// (`ReportBodyEventView` for the same victim), the marker swaps to a
// "discovered" style — a color shift plus an outline ring.

import type { Graphics } from "pixi.js";

import type { RoomView } from "../types/api";

interface BodyMarkerProps {
  room: RoomView;
  placementIndex: number;
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
// Golden angle: spacing successive placement indices by ~137.5° keeps every
// pair of bodies in a room well separated (>=32° apart for a 5-7 player roster)
// rather than clustering, which a plain string hash of sequential ids does not.
const GOLDEN_ANGLE_DEG = 137.50776405003785;

// Deterministic per-victim placement: an angle on a fixed-radius ring derived
// from the victim's roster index, so each body lands in a stable, separated
// spot.
function bodyOffset(placementIndex: number): { dx: number; dy: number } {
  const angle = (placementIndex * GOLDEN_ANGLE_DEG * Math.PI) / 180;
  return { dx: Math.cos(angle) * RING_RADIUS, dy: Math.sin(angle) * RING_RADIUS };
}

export function BodyMarker({
  room,
  placementIndex,
  isDiscovered,
  scale,
  offsetX,
  offsetY,
}: BodyMarkerProps) {
  const centerX = offsetX + (room.position.x + room.size.width / 2) * scale;
  const centerY = offsetY + (room.position.y + room.size.height / 2) * scale;
  const offset = bodyOffset(placementIndex);
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
