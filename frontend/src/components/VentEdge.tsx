// One vent link: a thin dashed gray line between two rooms' centers
// (DESIGN.md §7, §8.3 — "Vent network is a static graph, not a polygon").
// Geometry comes from the two `RoomView`s; the shared `scale`/`offset` map the
// abstract grid coordinates into the canvas (see MapView). Dashed + low-opacity
// so the vent network reads as distinct from solid room/door geometry.

import type { Graphics } from "pixi.js";

import type { RoomView } from "../types/api";

interface VentEdgeProps {
  fromRoom: RoomView;
  toRoom: RoomView;
  scale: number;
  offsetX: number;
  offsetY: number;
}

const VENT_COLOR = 0x94a3b8;
const VENT_WIDTH = 2;
const VENT_ALPHA = 0.5;
const DASH_LENGTH = 8;
const DASH_GAP = 6;

function roomCenterX(room: RoomView, scale: number, offsetX: number): number {
  return offsetX + (room.position.x + room.size.width / 2) * scale;
}

function roomCenterY(room: RoomView, scale: number, offsetY: number): number {
  return offsetY + (room.position.y + room.size.height / 2) * scale;
}

// Emit a dashed line as a sequence of short sub-segments; PixiJS strokes have no
// native dash. Caller applies the stroke once after this builds the path.
function dashedPath(
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
  for (let dist = 0; dist < length; dist += stride) {
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
        dashedPath(graphics, x1, y1, x2, y2);
        graphics.stroke({
          width: VENT_WIDTH,
          color: VENT_COLOR,
          alpha: VENT_ALPHA,
        });
      }}
    />
  );
}
