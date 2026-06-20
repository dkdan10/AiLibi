// A dead agent's body on the map, in the Playful style (Task 12.5;
// design/phase-12/stage-1-design.md §3.2, the 02-map / 03-two-truths renders). A
// paper disc + the hand-authored `body` glyph (an X-in-circle from the locked SVG
// set), placed on a fixed-radius ring off the room centre (golden-angle spread)
// so it never sits under a living token and multiple bodies in a room fan out.
//
// Two states, by the truth grammar: an UNDISCOVERED body is GHOSTED (dashed disc,
// muted ink tint) — present but not yet officially found; a DISCOVERED body is
// SOLID (kill-tinted glyph + a kill ring) once a `report_body` has fired. The
// victim id is shown (the agent who sees a body knows whose it is); the killer
// (`killed_by`) is NEVER drawn here — kill attribution is privileged and, under
// fog, MapView only ever feeds this component bodies the agent actually saw.

import type { Graphics } from "pixi.js";

import { paintGlyph } from "../assets/map/glyphs";
import { pixiHex, tokens } from "../tokens";
import type { RoomView } from "../types/api";

interface BodyMarkerProps {
  room: RoomView;
  placementIndex: number;
  isDiscovered: boolean;
  victimLabel: string;
  // The persisted spectator-only killer attribution (TickView.bodies[].killed_by),
  // shown beneath the victim id. `null` under fog (the As-agent view must never
  // expose who killed whom — VisibleBodyView carries no killed_by).
  killedBy: string | null;
  glyph: string;
  scale: number;
  offsetX: number;
  offsetY: number;
}

const DISC_RADIUS = 13;
const GLYPH_SIZE = 18;
const GOLDEN_ANGLE_DEG = 137.50776405003785;

const INK_700 = pixiHex(tokens.ink[700]);
const INK_500 = pixiHex(tokens.ink[500]);
const PAPER_2 = pixiHex(tokens.paper[2]);
const PAPER_3 = pixiHex(tokens.paper[3]);
const KILL = pixiHex(tokens.kill);

export function BodyMarker({
  room,
  placementIndex,
  isDiscovered,
  victimLabel,
  killedBy,
  glyph,
  scale,
  offsetX,
  offsetY,
}: BodyMarkerProps) {
  const centerX = offsetX + (room.position.x + room.size.width / 2) * scale;
  const centerY = offsetY + (room.position.y + room.size.height / 2) * scale;
  const w = room.size.width * scale;
  const h = room.size.height * scale;
  // Task 12.11 dead-end de-clutter: the old fixed 46px ring threw bodies outside
  // small rooms (Reactor / Storage) and onto their labels + the kill ✕. Scale the
  // fan radius to the room and bias it UPWARD, so bodies sit in the upper area —
  // clear of the agent tokens, which now cluster below the room centre — and the
  // † / victim labels no longer stack on the kill flash + room name.
  const radius = Math.min(40, Math.min(w, h) * 0.3);
  const angle = (placementIndex * GOLDEN_ANGLE_DEG * Math.PI) / 180;
  const x = centerX + Math.cos(angle) * radius;
  const y = centerY + Math.sin(angle) * radius - h * 0.14;
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
            // Outer kill ring marks a freshly reported body.
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
        text={victimLabel}
        anchor={0.5}
        x={x}
        y={y + DISC_RADIUS + 9}
        style={{
          fill: isDiscovered ? KILL : INK_500,
          fontSize: 9,
          fontFamily: tokens.type.mono,
          fontWeight: "700",
        }}
      />
      {killedBy !== null && (
        // Spectator-only kill attribution (dagger + killer id), persists with the
        // body after the kill event scrolls off the current tick.
        <pixiText
          text={`† ${killedBy}`}
          anchor={0.5}
          x={x}
          y={y + DISC_RADIUS + 20}
          style={{ fill: INK_500, fontSize: 8, fontFamily: tokens.type.mono }}
        />
      )}
    </>
  );
}
