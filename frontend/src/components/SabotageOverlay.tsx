// The sabotage layer (Task 12.5; design/phase-12/stage-1-design.md §3.2, §8.3).
// Projects the per-tick `SabotageDetailView` onto the map: the LIGHTS sabotage as
// a global visibility dim; the REACTOR sabotage as a kill-tinted warning on its
// affected rooms (REACTOR + ENGINEERING) plus a genuine per-room REPAIR RACE
// (`repair_progress` per room, drawn as filling pips) and a COUNTDOWN
// (`remaining_ticks`). Rendered above rooms/vents/bodies/tokens.
//
// Firewall (fog): `remaining_ticks` is spectator-privileged (api/schemas.py marks
// it "firewalled from agents"), so the countdown + per-room repair detail render
// ONLY in Omniscient. Under the As-agent fog the agent still EXPERIENCES the
// outage (the lights dim) and HEARS the alarm — but only when its own
// `audible_events` carried a `sabotage_alarm` (`agentAware`); the privileged
// numbers stay hidden. Every colour flows through `tokens.ts` via `pixiHex`.

import type { Graphics } from "pixi.js";

import { paintGlyph } from "../assets/map/glyphs";
import { pixiHex, tokens } from "../tokens";
import type { RoomView, SabotageDetailView } from "../types/api";

interface SabotageOverlayProps {
  width: number;
  height: number;
  sabotage: SabotageDetailView | null;
  roomsById: ReadonlyMap<string, RoomView>;
  scale: number;
  offsetX: number;
  offsetY: number;
  reactorGlyph: string;
  lightsGlyph: string;
  omniscient: boolean;
  agentAware: boolean;
}

const INK_900 = pixiHex(tokens.ink[900]);
const PAPER_0 = pixiHex(tokens.paper[0]);
const KILL = pixiHex(tokens.kill);

const LIGHTS_DIM_ALPHA = 0.4;
const HUD_PAD = 12;

// A horizontal row of repair pips at the room's bottom edge: one filled pip per
// accumulated repair tick (no DTO threshold to divide by, so this is an honest
// count, not a fabricated %). Capped so a long repair never overflows the room.
const MAX_PIPS = 8;

function drawRepairPips(
  graphics: Graphics,
  room: RoomView,
  progress: number,
  scale: number,
  offsetX: number,
  offsetY: number,
): void {
  const count = Math.min(progress, MAX_PIPS);
  if (count <= 0) {
    return;
  }
  const roomW = room.size.width * scale;
  const cx = offsetX + (room.position.x + room.size.width / 2) * scale;
  const bottomY = offsetY + (room.position.y + room.size.height) * scale - 9;
  const pipW = 6;
  const gap = 3;
  const totalW = count * pipW + (count - 1) * gap;
  const startX = cx - Math.min(totalW, roomW - 12) / 2;
  const drawW = Math.min(totalW, roomW - 12);
  const step = count > 0 ? drawW / count : 0;
  for (let i = 0; i < count; i++) {
    const px = startX + i * step;
    graphics.roundRect(px, bottomY, Math.max(3, step - gap), 4, 1.5);
    graphics.fill(KILL);
  }
}

export function SabotageOverlay({
  width,
  height,
  sabotage,
  roomsById,
  scale,
  offsetX,
  offsetY,
  reactorGlyph,
  lightsGlyph,
  omniscient,
  agentAware,
}: SabotageOverlayProps) {
  if (sabotage === null) {
    return null;
  }
  // Under fog, show the sabotage only if the agent could perceive it.
  if (!omniscient && !agentAware) {
    return null;
  }

  const isLights = sabotage.kind === "lights";
  const glyph = isLights ? lightsGlyph : reactorGlyph;
  // Omniscient names the room + countdown; fog shows only what the agent perceives
  // — the darkness (lights) or a non-located alarm (reactor) — never the location.
  const hudText = omniscient
    ? `${isLights ? "LIGHTS" : "REACTOR"} · t-${sabotage.remaining_ticks}`
    : isLights
      ? "LIGHTS · DARK"
      : "SABOTAGE · ALARM";
  const chipW = 156;
  const chipH = 30;
  const chipX = width - HUD_PAD - chipW;
  const chipY = HUD_PAD;
  const glyphX = chipX + 16;
  const textX = chipX + 31;

  return (
    <>
      <pixiGraphics
        draw={(graphics: Graphics) => {
          graphics.clear();

          // Lights → global visibility dim (the outage everyone feels, both modes).
          if (isLights) {
            graphics.rect(0, 0, width, height);
            graphics.fill({ color: INK_900, alpha: LIGHTS_DIM_ALPHA });
          }

          // The affected-room tint + per-room repair race expose the sabotage
          // LOCATION and the privileged repair detail → Omniscient ONLY (drawing
          // them under fog would leak where the sabotage is + its repair state).
          if (omniscient) {
            if (!isLights) {
              for (const roomId of sabotage.affected_rooms) {
                const room = roomsById.get(roomId);
                if (room === undefined) continue;
                graphics.roundRect(
                  offsetX + room.position.x * scale,
                  offsetY + room.position.y * scale,
                  room.size.width * scale,
                  room.size.height * scale,
                  tokens.radius.lg,
                );
                graphics.fill({ color: KILL, alpha: 0.12 });
                graphics.stroke({ width: 2, color: KILL, alpha: 0.65 });
              }
            }
            for (const [roomId, progress] of Object.entries(sabotage.repair_progress)) {
              const room = roomsById.get(roomId);
              if (room !== undefined) {
                drawRepairPips(graphics, room, progress, scale, offsetX, offsetY);
              }
            }
          }

          // Status HUD chip (top-right).
          graphics.roundRect(chipX, chipY, chipW, chipH, tokens.radius.md);
          graphics.fill(PAPER_0);
          graphics.stroke({ width: 2, color: KILL });
          graphics.circle(glyphX, chipY + chipH / 2, 9);
          graphics.fill(KILL);
        }}
      />
      <pixiGraphics
        draw={(g: Graphics) => paintGlyph(g, glyph, glyphX, chipY + chipH / 2, 13, PAPER_0)}
      />
      <pixiText
        text={hudText}
        anchor={{ x: 0, y: 0.5 }}
        x={textX}
        y={chipY + chipH / 2}
        style={{ fill: INK_900, fontSize: 11, fontFamily: tokens.type.mono, fontWeight: "700" }}
      />
    </>
  );
}
