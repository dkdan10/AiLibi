// One link of the impostor vent ring: a dotted ink line between two rooms'
// centres (Task 12.5; design/phase-12/stage-1-design.md §3.2, §8.3 — "vent
// network is a static graph, not a polygon"; the 02-map render). Geometry comes
// from the two `RoomView`s out of `MapLayoutView.vents`; the shared `scale`/
// `offset` map the abstract grid into the canvas (see MapView).
//
// The whole ring is OMNISCIENT-only — MapView never renders VentEdge under the
// As-agent fog (the vent network is the impostor's private topology; revealing it
// would leak). Colour + weight flow through `tokens.ts` via `pixiHex` (ink-500,
// the reserved-channel-free neutral the converge used for vents).

import type { Graphics } from "pixi.js";

import { pixiHex, tokens } from "../tokens";
import type { RoomView } from "../types/api";

interface VentEdgeProps {
  fromRoom: RoomView;
  toRoom: RoomView;
  scale: number;
  offsetX: number;
  offsetY: number;
}

const VENT_COLOR = pixiHex(tokens.ink[500]);
const VENT_WIDTH = 2.4;
const VENT_ALPHA = 0.85;
// Dotted (round-capped short dashes) so the ring reads as distinct from the solid
// ink corridors — matches the converge's `stroke-dasharray: 2 9` vent styling.
const DASH_LENGTH = 0.5;
const DASH_GAP = 9;

function roomCenterX(room: RoomView, scale: number, offsetX: number): number {
  return offsetX + (room.position.x + room.size.width / 2) * scale;
}

function roomCenterY(room: RoomView, scale: number, offsetY: number): number {
  return offsetY + (room.position.y + room.size.height / 2) * scale;
}

// PixiJS strokes have no native dash, so emit the dotted line as a sequence of
// round-capped sub-segments; the caller strokes once after this builds the path.
function dottedPath(
  graphics: Graphics,
  x1: number,
  y1: number,
  x2: number,
  y2: number,
): void {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const length = Math.hypot(dx, dy);
  if (length === 0) {
    return;
  }
  const ux = dx / length;
  const uy = dy / length;
  const stride = DASH_LENGTH + DASH_GAP;
  for (let dist = 0; dist <= length; dist += stride) {
    const end = Math.min(dist + DASH_LENGTH, length);
    graphics.moveTo(x1 + ux * dist, y1 + uy * dist);
    graphics.lineTo(x1 + ux * end, y1 + uy * end);
  }
}

export function VentEdge({
  fromRoom,
  toRoom,
  scale,
  offsetX,
  offsetY,
}: VentEdgeProps) {
  const x1 = roomCenterX(fromRoom, scale, offsetX);
  const y1 = roomCenterY(fromRoom, scale, offsetY);
  const x2 = roomCenterX(toRoom, scale, offsetX);
  const y2 = roomCenterY(toRoom, scale, offsetY);

  return (
    <pixiGraphics
      draw={(graphics: Graphics) => {
        graphics.clear();
        dottedPath(graphics, x1, y1, x2, y2);
        graphics.stroke({
          width: VENT_WIDTH,
          color: VENT_COLOR,
          alpha: VENT_ALPHA,
          cap: "round",
        });
      }}
    />
  );
}
