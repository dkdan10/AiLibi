// One agent: a PixiJS circle drawn at the center of its room, nudged by a
// deterministic per-agent jitter so multiple agents in one room don't fully
// overlap (DESIGN.md §7). The jitter offset is in screen pixels (not scaled),
// so tokens stay readably spread regardless of the map fit-to-canvas scale.
// Color is the agent's `PlayerView.color`. Dead / venting agents are filtered
// out upstream in MapView and never reach this component.
//
// Movement between adjacent ticks is tweened: when `room` changes and `animate`
// is true, the token slides from its current interpolated position to the new
// room center over TWEEN_DURATION_MS (driven by PixiJS's Ticker via useTick).
// The tween always starts from wherever the token currently sits, so a tick
// change mid-tween interrupts cleanly and re-targets without desyncing. When
// `animate` is false (multi-tick scrub / snap-to-meeting, or a fresh mount), the
// token jumps straight to the target with no interpolation.

import { useTick } from "@pixi/react";
import { useCallback, useEffect, useRef, useState } from "react";

import type { Graphics, Ticker } from "pixi.js";

import type { RoomView } from "../types/api";

interface AgentTokenProps {
  room: RoomView;
  jitterIndex: number;
  color: string;
  scale: number;
  offsetX: number;
  offsetY: number;
  animate: boolean;
}

interface Point {
  x: number;
  y: number;
}

// Tween duration for a single-tick move. Exported so a future ReplayControls
// (task 4.11) can coordinate interpolation with playback speed if needed.
export const TWEEN_DURATION_MS = 250;

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
  const { room, color, animate } = props;
  const target = targetPoint(props);

  // Current interpolated position (ref mirrors state so the tween can resume
  // from the live position when interrupted; state drives the redraw).
  const [pos, setPos] = useState<Point>(target);
  const posRef = useRef<Point>(target);
  const fromRef = useRef<Point>(target);
  const toRef = useRef<Point>(target);
  // Start "complete" so a freshly-mounted token sits still at its target.
  const progressRef = useRef<number>(1);

  // Re-target whenever the agent's room changes. (The map transform is fixed
  // per the single canonical map, so room.id changing is the only trigger.)
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
    // `target` is read from this render's closure — it's a pure function of
    // `room.id` since jitter and the map transform are fixed. Re-run when the
    // destination room changes OR when the snap/tween mode flips, so a
    // multi-tick jump (animate=false) snaps immediately even when it lands in
    // the room the token was already tweening toward.
  }, [room.id, animate]);

  const advance = useCallback((ticker: Ticker) => {
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

  return (
    <pixiGraphics
      draw={(graphics: Graphics) => {
        graphics.clear();
        graphics.circle(pos.x, pos.y, TOKEN_RADIUS);
        graphics.fill(color);
        graphics.stroke({ width: BORDER_WIDTH, color: BORDER_COLOR });
      }}
    />
  );
}
