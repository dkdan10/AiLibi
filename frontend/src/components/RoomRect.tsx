// One room of the canonical_1 floorplan, rendered in the Playful cream/ink
// chunky-sticker style (Task 12.5; design/phase-12/stage-1-design.md §3.2,
// design/phase-12/canonical_1-map-reference.svg, the 02-map render). Geometry is
// the real `(x,y)`+size from the `MapLayoutView` DTO; the shared `scale`/`offset`
// (computed once in MapView) maps the abstract grid into the canvas. The fixed
// layout is never invented/moved/renamed — only restyled.
//
// Every colour flows through `tokens.ts` via `pixiHex` — zero magic constants.
//
// `RoomView` carries no `kind` (and api/ is out of 12.5's scope — no DTO change),
// so the "hallways subordinate" treatment (§3.2) is derived GEOMETRICALLY from the
// DTO size: a corridor is an extreme-aspect rectangle (the canonical halls are
// 3:1–3.5:1; task rooms are ~1.4–1.6:1). Corridors get a lighter fill/stroke and,
// when tall-and-narrow, a rotated label. No invented id→kind mapping.
//
// `visible` is the As-agent fog gate: when false the room is unseen — it renders
// as a muted, hatched, dashed-outline "FOG" cell with NO name and NO contents
// (the firewall, simulated in the UI: an unseen room reveals nothing).

import type { Graphics } from "pixi.js";

import { pixiHex, tokens } from "../tokens";
import type { RoomView } from "../types/api";

interface RoomRectProps {
  room: RoomView;
  scale: number;
  offsetX: number;
  offsetY: number;
  visible: boolean;
}

// Aspect ratio at/above which a room reads as a corridor (subordinate). The
// canonical halls are 3:1–3.5:1; the squarest task room is ~1.6:1, so 2.2 cleanly
// separates them from the DTO size alone.
// A corridor is a THIN elongated connector. The canonical halls are 4 grid units
// thick; every task / utility room is ≥ 6 thick (Storage is 14×6 — elongated but
// NOT thin), so gating on the short side first keeps Storage (a crime-scene room)
// out of the muted hallway styling. The aspect check is a secondary guard so a
// hypothetical thin-but-square cell isn't muted.
const CORRIDOR_MAX_THICKNESS = 4;
const CORRIDOR_ASPECT = 2.2;
const ROOM_RADIUS = tokens.radius.lg; // 14 — the sticker corner radius
const NAME_FONT_SIZE = 14;
const NAME_TOP_PAD = 15; // screen px from the room's top edge to the name baseline
// Pixi builds its own canvas font shorthand from fontWeight + fontSize +
// fontFamily, so `fontFamily` must be the bare family — NOT the `tokens.type.*`
// CSS shorthand (`600 'Fredoka'`), which would yield an invalid `14px 600
// 'Fredoka'` and silently fall back. Strip the leading weight, keeping tokens.ts
// as the single source of the family name.
const DISPLAY_FAMILY = tokens.type.display.replace(/^\d+\s+/, "");

// Resolved token colours (hex string → 0xRRGGBB once per module).
const INK_900 = pixiHex(tokens.ink[900]);
const INK_300 = pixiHex(tokens.ink[300]);
const INK_400 = pixiHex(tokens.ink[400]);
const INK_200 = pixiHex(tokens.ink[200]);
const PAPER_0 = pixiHex(tokens.paper[0]);
const PAPER_1 = pixiHex(tokens.paper[1]);
const PAPER_2 = pixiHex(tokens.paper[2]);
const PAPER_3 = pixiHex(tokens.paper[3]);

function isCorridor(room: RoomView): boolean {
  const { width, height } = room.size;
  const long = Math.max(width, height);
  const short = Math.min(width, height);
  return short > 0 && short <= CORRIDOR_MAX_THICKNESS && long / short >= CORRIDOR_ASPECT;
}

// Append a 45° hatch clipped to the rect [x, x+w]×[y, y+h] — the fog texture for
// unseen rooms. Lines satisfy `px - py = k`; for each k we take the (≤2) edge
// intersections inside the rect and stroke between them. No mask needed.
function appendHatch(
  graphics: Graphics,
  x: number,
  y: number,
  w: number,
  h: number,
  gap: number,
): void {
  const x1 = x + w;
  const y1 = y + h;
  const kMin = x - y1;
  const kMax = x1 - y;
  for (let k = Math.ceil(kMin / gap) * gap; k <= kMax; k += gap) {
    const pts: Array<[number, number]> = [];
    const topX = y + k; // py = y  → px = y + k
    if (topX >= x && topX <= x1) pts.push([topX, y]);
    const botX = y1 + k; // py = y1 → px = y1 + k
    if (botX >= x && botX <= x1) pts.push([botX, y1]);
    const leftY = x - k; // px = x  → py = x - k
    if (leftY > y && leftY < y1) pts.push([x, leftY]);
    const rightY = x1 - k; // px = x1 → py = x1 - k
    if (rightY > y && rightY < y1) pts.push([x1, rightY]);
    if (pts.length >= 2) {
      const [ax, ay] = pts[0]!;
      const [bx, by] = pts[1]!;
      graphics.moveTo(ax, ay);
      graphics.lineTo(bx, by);
    }
  }
}

export function RoomRect({ room, scale, offsetX, offsetY, visible }: RoomRectProps) {
  const x = offsetX + room.position.x * scale;
  const y = offsetY + room.position.y * scale;
  const width = room.size.width * scale;
  const height = room.size.height * scale;
  const corridor = isCorridor(room);
  const rotated = corridor && height > width; // tall-and-narrow → vertical label
  const cx = x + width / 2;
  const cy = y + height / 2;

  if (!visible) {
    // Fog cell: muted fill + subtle hatch + dashed ghost outline + "FOG".
    return (
      <>
        <pixiGraphics
          draw={(graphics: Graphics) => {
            graphics.clear();
            graphics.roundRect(x, y, width, height, ROOM_RADIUS);
            graphics.fill(PAPER_2);
            appendHatch(graphics, x, y, width, height, 9);
            graphics.stroke({ width: 1.4, color: INK_200, alpha: 0.9 });
            graphics.roundRect(x, y, width, height, ROOM_RADIUS);
            graphics.stroke({ width: 2, color: INK_300, alpha: 0.85 });
          }}
        />
        <pixiText
          text="FOG"
          anchor={0.5}
          x={cx}
          y={cy}
          style={{
            fill: INK_300,
            fontSize: 11,
            fontFamily: tokens.type.mono,
            letterSpacing: 2,
          }}
        />
      </>
    );
  }

  const fill = corridor ? PAPER_1 : PAPER_0;
  const strokeColor = corridor ? INK_400 : INK_900;
  const strokeWidth = corridor ? 2 : 2.4;

  return (
    <>
      <pixiGraphics
        draw={(graphics: Graphics) => {
          graphics.clear();
          // Hard offset shadow first (the chunky-sticker elevation), then the cell.
          graphics.roundRect(x + 2.5, y + 3, width, height, ROOM_RADIUS);
          graphics.fill({ color: INK_900, alpha: corridor ? 0.07 : 0.14 });
          graphics.roundRect(x, y, width, height, ROOM_RADIUS);
          graphics.fill(fill);
          graphics.stroke({ width: strokeWidth, color: strokeColor });
        }}
      />
      <pixiText
        text={room.name}
        anchor={0.5}
        x={rotated ? cx : cx}
        y={rotated ? cy : y + NAME_TOP_PAD}
        rotation={rotated ? -Math.PI / 2 : 0}
        style={{
          fill: corridor ? INK_400 : INK_900,
          fontSize: rotated ? 12 : NAME_FONT_SIZE,
          fontFamily: DISPLAY_FAMILY,
          fontWeight: "600",
        }}
      />
    </>
  );
}

// Re-exported palette so MapView can paint the stage background from the same
// resolved tokens without re-deriving them (zero magic constants).
export const ROOM_PALETTE = { INK_900, PAPER_0, PAPER_1, PAPER_3 } as const;
