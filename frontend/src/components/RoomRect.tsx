// One room of the map: a filled PixiJS rectangle plus its name as text
// (DESIGN.md §7). Geometry comes straight from the `RoomView` (position +
// size); the shared `scale`/`offset` map the map's abstract grid coordinates
// into the 800x600 canvas (see MapView). The fill is a deterministic hash of
// the room id, so the same room is always the same color across renders.

import type { Graphics } from "pixi.js";

import type { RoomView } from "../types/api";

interface RoomRectProps {
  room: RoomView;
  scale: number;
  offsetX: number;
  offsetY: number;
}

const ROOM_SATURATION = 0.5;
const ROOM_LIGHTNESS = 0.28;
const BORDER_COLOR = 0x0f172a;
const BORDER_WIDTH = 2;
const LABEL_COLOR = 0xe2e8f0;
const LABEL_FONT_SIZE = 13;
const LABEL_PADDING = 6;

function hashString(value: string): number {
  let hash = 0;
  for (let i = 0; i < value.length; i++) {
    hash = (hash * 31 + value.charCodeAt(i)) >>> 0;
  }
  return hash;
}

function hslToHex(hue: number, saturation: number, lightness: number): number {
  const chroma = (1 - Math.abs(2 * lightness - 1)) * saturation;
  const huePrime = hue / 60;
  const second = chroma * (1 - Math.abs((huePrime % 2) - 1));
  const match = lightness - chroma / 2;

  let r = 0;
  let g = 0;
  let b = 0;
  if (huePrime < 1) {
    [r, g, b] = [chroma, second, 0];
  } else if (huePrime < 2) {
    [r, g, b] = [second, chroma, 0];
  } else if (huePrime < 3) {
    [r, g, b] = [0, chroma, second];
  } else if (huePrime < 4) {
    [r, g, b] = [0, second, chroma];
  } else if (huePrime < 5) {
    [r, g, b] = [second, 0, chroma];
  } else {
    [r, g, b] = [chroma, 0, second];
  }

  const toByte = (channel: number): number => Math.round((channel + match) * 255);
  return (toByte(r) << 16) | (toByte(g) << 8) | toByte(b);
}

/** Stable per-room color: same room id always maps to the same fill. */
function roomColor(roomId: string): number {
  return hslToHex(hashString(roomId) % 360, ROOM_SATURATION, ROOM_LIGHTNESS);
}

export function RoomRect({ room, scale, offsetX, offsetY }: RoomRectProps) {
  const x = offsetX + room.position.x * scale;
  const y = offsetY + room.position.y * scale;
  const width = room.size.width * scale;
  const height = room.size.height * scale;
  const fill = roomColor(room.id);

  return (
    <>
      <pixiGraphics
        draw={(graphics: Graphics) => {
          graphics.clear();
          graphics.rect(x, y, width, height);
          graphics.fill(fill);
          graphics.stroke({ width: BORDER_WIDTH, color: BORDER_COLOR });
        }}
      />
      <pixiText
        text={room.name}
        x={x + LABEL_PADDING}
        y={y + LABEL_PADDING}
        style={{
          fill: LABEL_COLOR,
          fontSize: LABEL_FONT_SIZE,
          fontFamily: "sans-serif",
        }}
      />
    </>
  );
}
