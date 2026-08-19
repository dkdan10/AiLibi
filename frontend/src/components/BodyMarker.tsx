// A dead agent's body on the map, in the Playful style (Task 12.5;
// design/phase-12/stage-1-design.md §3.2, the 02-map / 03-two-truths renders). A
// paper disc + the hand-authored `body` glyph (an X-in-circle from the locked SVG
// set).
//
// Layout (Task 12.13 admin-cluster fix): bodies in a room lay out in a
// NON-OVERLAPPING horizontal grid in a band BELOW the reserved room-title band
// (so a pile never garbles the room name), with bottom padding for the victim
// label. MapView assigns each body a per-room `slotIndex` / `slotCount`; past
// `BODY_CAP` the whole pile collapses to a single "✕ ×N" marker
// (`collapsedCount`) so a mass grave stays legible.
//
// PRESENCE: a marker is drawn only for a body the engine still has on the floor
// — the served `TickView.bodies` rows for that tick (`lib/bodies.ts`). A corpse
// consumed by its body-report meeting stops being drawn on that frame.
//
// Two states, by the truth grammar: an UNDISCOVERED body is GHOSTED (dashed disc,
// muted ink tint) — present but not yet officially found; a DISCOVERED body is
// SOLID (kill-tinted glyph + a kill ring) once a `report_body` has fired for it.
// The victim id is shown (the agent who sees a body knows whose it is); the
// killer (`killed_by`) is shown only for a lone body — kill attribution is
// privileged and, under fog, MapView only ever feeds this component bodies the
// agent saw.

import type { Graphics } from "pixi.js";

import { paintGlyph } from "../assets/map/glyphs";
import { pixiHex, tokens } from "../tokens";
import type { RoomView } from "../types/api";

interface BodyMarkerProps {
  room: RoomView;
  // Position within this room's body grid + the room's body count.
  slotIndex: number;
  slotCount: number;
  // When set (> 0), render the collapsed "✕ ×N" overflow marker instead of one
  // body — past capacity, MapView feeds a single marker per room.
  collapsedCount?: number;
  isDiscovered: boolean;
  victimLabel: string;
  // The persisted spectator-only killer attribution (TickView.bodies[].killed_by),
  // shown beneath a LONE body. `null` under fog (the As-agent view must never
  // expose who killed whom — VisibleBodyView carries no killed_by).
  killedBy: string | null;
  glyph: string;
  scale: number;
  offsetX: number;
  offsetY: number;
}

// Max individual bodies drawn per room before collapsing to "✕ ×N".
export const BODY_CAP = 3;

const DISC_RADIUS = 12;
const GLYPH_SIZE = 16;
// Reserved title band (screen px): the room name sits at the cell TOP, so the
// body grid starts below it.
const TITLE_BAND = 16;
const MIN_STEP = 2 * DISC_RADIUS + 6;

// Whether `count` bodies fit non-overlapping in this room's body band (the row
// needs `(count-1) * MIN_STEP` of inner width). Narrow canonical rooms — the
// 4-unit EAST_HALL/WEST_HALL — cannot, so MapView collapses those piles to a
// single "✕ ×N" marker instead of letting the discs overlap (Task 12.13 review).
export function bodiesFit(room: RoomView, scale: number, count: number): boolean {
  if (count <= 1) {
    return true;
  }
  const innerW = Math.max(0, room.size.width * scale - 2 * (DISC_RADIUS + 4));
  return (count - 1) * MIN_STEP <= innerW;
}

const INK_700 = pixiHex(tokens.ink[700]);
const INK_500 = pixiHex(tokens.ink[500]);
const PAPER_2 = pixiHex(tokens.paper[2]);
const PAPER_3 = pixiHex(tokens.paper[3]);
const KILL = pixiHex(tokens.kill);

// The screen-space anchor for a body slot: a centred horizontal row in the band
// directly below the reserved title band. The y is pinned just under the title
// (never clamped UPWARD into it) so a body never covers the room name even in a
// shallow room — the old `Math.min` clamp let the bottom branch win in a 4-unit
// room (e.g. UPPER_HALL) and pulled the disc over the label (Task 12.13 review).
// The disc still fits the cell for every canonical room (min height 4 units).
function slotAnchor(
  room: RoomView,
  scale: number,
  offsetX: number,
  offsetY: number,
  slotIndex: number,
  slotCount: number,
): { x: number; y: number } {
  const cellLeft = offsetX + room.position.x * scale;
  const cellTop = offsetY + room.position.y * scale;
  const w = room.size.width * scale;
  const cx = cellLeft + w / 2;
  const y = cellTop + TITLE_BAND + DISC_RADIUS;
  const innerW = Math.max(0, w - 2 * (DISC_RADIUS + 4));
  const step = slotCount > 1 ? Math.min(MIN_STEP, innerW / (slotCount - 1)) : 0;
  const startX = cx - (step * (slotCount - 1)) / 2;
  return { x: startX + slotIndex * step, y };
}

export function BodyMarker({
  room,
  slotIndex,
  slotCount,
  collapsedCount,
  isDiscovered,
  victimLabel,
  killedBy,
  glyph,
  scale,
  offsetX,
  offsetY,
}: BodyMarkerProps) {
  const collapsed = collapsedCount !== undefined && collapsedCount > 0;
  const { x, y } = slotAnchor(room, scale, offsetX, offsetY, slotIndex, slotCount);
  const glyphTint = isDiscovered ? KILL : INK_500;

  return (
    <>
      <pixiGraphics
        draw={(graphics: Graphics) => {
          graphics.clear();
          graphics.circle(x, y, DISC_RADIUS);
          graphics.fill(isDiscovered ? PAPER_2 : PAPER_3);
          if (isDiscovered) {
            graphics.stroke({ width: 2.4, color: KILL });
            // Outer kill ring: this body has been reported and is still on the
            // floor.
            graphics.circle(x, y, DISC_RADIUS + 4);
            graphics.stroke({ width: 1.6, color: KILL, alpha: 0.7 });
          } else {
            // Ghosted: a dotted ink-700 outline (present but not yet found).
            for (let a = 0; a < Math.PI * 2; a += Math.PI / 9) {
              graphics.moveTo(x + Math.cos(a) * DISC_RADIUS, y + Math.sin(a) * DISC_RADIUS);
              graphics.lineTo(
                x + Math.cos(a + Math.PI / 18) * DISC_RADIUS,
                y + Math.sin(a + Math.PI / 18) * DISC_RADIUS,
              );
            }
            graphics.stroke({ width: 2, color: INK_700, alpha: 0.8 });
          }
        }}
      />
      <pixiGraphics
        draw={(g: Graphics) =>
          paintGlyph(g, glyph, x, y, GLYPH_SIZE, glyphTint, isDiscovered ? 1 : 0.75)
        }
      />
      <pixiText
        text={collapsed ? `✕ ×${collapsedCount}` : victimLabel}
        anchor={0.5}
        x={x}
        y={y + DISC_RADIUS + 8}
        style={{
          fill: isDiscovered ? KILL : INK_500,
          fontSize: 9,
          fontFamily: tokens.type.mono,
          fontWeight: "700",
        }}
      />
      {!collapsed && slotCount === 1 && killedBy !== null && (
        // Spectator-only kill attribution (dagger + killer id) for a lone body;
        // suppressed in a cluster to keep the stacked labels legible.
        <pixiText
          text={`† ${killedBy}`}
          anchor={0.5}
          x={x}
          y={y + DISC_RADIUS + 19}
          style={{ fill: INK_500, fontSize: 8, fontFamily: tokens.type.mono }}
        />
      )}
    </>
  );
}
