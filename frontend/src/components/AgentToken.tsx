// One agent on the map, in the Playful chunky-sticker style (Task 12.5;
// design/phase-12/stage-1-design.md §3.2, the 02-map render). A filled disc in
// the agent's role-neutral IDENTITY colour (never guilt — firewall) with the
// p-id in mono, a small `current_action` glyph chip (cream sticker + ink glyph),
// and an OMNISCIENT-ONLY impostor role badge (ink disc + cream dagger). The
// per-agent jitter spreads co-located tokens so they don't fully overlap.
//
// Movement between adjacent ticks is tweened (kept from Phase 4): when `room`
// changes and `animate` is true, the token slides from its current interpolated
// position to the new room centre over TWEEN_DURATION_MS via PixiJS's Ticker. The
// tween always resumes from the live position, so a tick change mid-tween
// re-targets cleanly. When `animate` is false (scrub / snap / fresh mount) it
// jumps straight to the target.
//
// `actionGlyph` / `roleBadge` are pre-resolved Pixi textures threaded down by
// MapView (which owns the glyph registry + the Omniscient gate). A `null` texture
// simply draws no chip/badge — so IDLE tokens stay clean and fog suppresses the
// role badge without this component knowing the firewall rules.

import { useTick } from "@pixi/react";
import { useCallback, useEffect, useRef, useState } from "react";

import type { Graphics } from "pixi.js";

import { paintGlyph } from "../assets/map/glyphs";
import { pixiHex, tokens } from "../tokens";
import type { RoomView } from "../types/api";

interface AgentTokenProps {
  room: RoomView;
  jitterIndex: number;
  color: string;
  label: string;
  actionGlyph: string | null;
  roleBadge: string | null;
  scale: number;
  offsetX: number;
  offsetY: number;
  animate: boolean;
}

interface Point {
  x: number;
  y: number;
}

// Tween duration for a single-tick move (kept from Phase 4).
export const TWEEN_DURATION_MS = 250;

const TOKEN_RADIUS = 12;
const INK_900 = pixiHex(tokens.ink[900]);
const PAPER_0 = pixiHex(tokens.paper[0]);

const CHIP_RADIUS = 7.5;
const CHIP_OFFSET = 12; // screen px from the token centre to the chip centre
const GLYPH_SIZE = 11;

// Nine deterministic offsets around a room centre (screen pixels), so all NINE
// co-located tokens fan out instead of stacking (Task 12.11: the old six-slot
// table piled p-6/7/8 onto p-0/1/2 at the Cafeteria spawn). Every offset is at or
// BELOW the centre (`dy >= 8`) so a token never rides up onto the room-name label
// (which sits at the room's TOP edge) — fixing the token↔label overlap from the
// token side without touching the label. Ordered centre-out so a lone token in a
// small dead-end gets a central slot; the two rows fan across the wide Cafeteria.
const JITTER_OFFSETS: ReadonlyArray<{ dx: number; dy: number }> = [
  { dx: 0, dy: 8 },
  { dx: -30, dy: 8 },
  { dx: 30, dy: 8 },
  { dx: -15, dy: 34 },
  { dx: 15, dy: 34 },
  { dx: -45, dy: 34 },
  { dx: 45, dy: 34 },
  { dx: -60, dy: 8 },
  { dx: 60, dy: 8 },
];

function targetPoint(props: AgentTokenProps): Point {
  const { room, jitterIndex, scale, offsetX, offsetY } = props;
  const centerX = offsetX + (room.position.x + room.size.width / 2) * scale;
  const centerY = offsetY + (room.position.y + room.size.height / 2) * scale;
  const offset = JITTER_OFFSETS[jitterIndex % JITTER_OFFSETS.length] ?? {
    dx: 0,
    dy: 0,
  };
  return { x: centerX + offset.dx, y: centerY + offset.dy };
}

export function AgentToken(props: AgentTokenProps) {
  const { room, color, label, actionGlyph, roleBadge, animate } = props;
  const target = targetPoint(props);

  const [pos, setPos] = useState<Point>(target);
  const posRef = useRef<Point>(target);
  const fromRef = useRef<Point>(target);
  const toRef = useRef<Point>(target);
  const progressRef = useRef<number>(1);

  // Re-target when the room changes (tween) or the snap/tween mode flips (snap).
  useEffect(() => {
    if (animate) {
      fromRef.current = posRef.current;
      toRef.current = target;
      progressRef.current = 0;
    } else {
      fromRef.current = target;
      toRef.current = target;
      posRef.current = target;
      progressRef.current = 1;
      setPos(target);
    }
    // `target` is a pure function of `room.id` (jitter + transform are fixed), so
    // re-run only when the destination room changes or the mode flips.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [room.id, animate]);

  const advance = useCallback((ticker: { deltaMS: number }) => {
    if (progressRef.current >= 1) {
      return;
    }
    progressRef.current = Math.min(
      1,
      progressRef.current + ticker.deltaMS / TWEEN_DURATION_MS,
    );
    const from = fromRef.current;
    const to = toRef.current;
    const p = progressRef.current;
    const next: Point = {
      x: from.x + (to.x - from.x) * p,
      y: from.y + (to.y - from.y) * p,
    };
    posRef.current = next;
    setPos(next);
  }, []);

  useTick(advance);

  const tokenColor = pixiHex(color);
  const chipX = pos.x + CHIP_OFFSET;
  const chipBottomY = pos.y + CHIP_OFFSET;
  const badgeTopY = pos.y - CHIP_OFFSET;

  return (
    <>
      <pixiGraphics
        draw={(graphics: Graphics) => {
          graphics.clear();
          // Token disc.
          graphics.circle(pos.x, pos.y, TOKEN_RADIUS);
          graphics.fill(tokenColor);
          graphics.stroke({ width: 2.2, color: INK_900 });
          // Action chip background (cream sticker), only when there is a glyph.
          if (actionGlyph !== null) {
            graphics.circle(chipX, chipBottomY, CHIP_RADIUS);
            graphics.fill(PAPER_0);
            graphics.stroke({ width: 1.6, color: INK_900 });
          }
          // Role badge background (ink disc), Omniscient-only via the texture gate.
          if (roleBadge !== null) {
            graphics.circle(chipX, badgeTopY, CHIP_RADIUS);
            graphics.fill(INK_900);
            graphics.stroke({ width: 1.6, color: PAPER_0 });
          }
        }}
      />
      <pixiText
        text={label}
        anchor={0.5}
        x={pos.x}
        y={pos.y}
        style={{
          fill: PAPER_0,
          fontSize: 10,
          fontFamily: tokens.type.mono,
          fontWeight: "700",
        }}
      />
      {actionGlyph !== null && (
        <pixiGraphics
          draw={(g: Graphics) => paintGlyph(g, actionGlyph, chipX, chipBottomY, GLYPH_SIZE, INK_900)}
        />
      )}
      {roleBadge !== null && (
        <pixiGraphics
          draw={(g: Graphics) => paintGlyph(g, roleBadge, chipX, badgeTopY, GLYPH_SIZE + 1, PAPER_0)}
        />
      )}
    </>
  );
}
