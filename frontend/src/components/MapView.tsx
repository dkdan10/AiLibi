// The map stage: the MapToolbar chrome (perspective switcher) over a hand-coded
// PixiJS canvas that renders the canonical_1 floorplan in the Playful cream/ink
// style for the current replay + tick (Task 12.5; design/phase-12/stage-1-design
// §3.2, §5, slice 3; the 02-map + 03-two-truths renders;
// canonical_1-map-reference.svg). Layers, bottom→top: rooms, the vent ring
// (Omniscient), bodies, agent tokens (tweened) + vent-escape travellers, kill
// flashes, and the sabotage layer.
//
// Rooms come from the real `(x,y)`+size in `MapLayoutView` — the fixed 10-room /
// 11-corridor / 6-vent layout, never invented/moved/renamed. A single uniform
// fit-to-canvas transform (scale + offset) is computed from the room bounding box
// and threaded to children; per-token jitter, body rings, radii and fonts stay in
// screen pixels so they read consistently regardless of scale.
//
// The SVG asset set under `assets/map/` is drawn into Pixi as VECTOR geometry
// (`Graphics.svg`) and tinted at render time; every colour/space flows through
// `tokens.ts` via `pixiHex` — zero magic constants on the canvas.
//
// FIREWALL (As-agent fog): when `perspective.mode === "agent"` the canvas dims to
// EXACTLY that agent's per-tick `AgentVisibilityView` (Task 12.3) — its lit rooms
// are only those holding something it saw; unseen rooms fog over; only the self +
// `visible_players` / `visible_bodies` render; the vent ring, role badges,
// vent-escape, kill flashes and the privileged sabotage countdown are all
// suppressed. No token/body the agent could not see is ever painted (the 12.3
// leak guard). Visibility is NEVER re-derived client-side — it is read from the
// firewall-filtered projection the loader serves.

import { Application, extend, useTick } from "@pixi/react";
import { Container, Graphics, Text } from "pixi.js";
import { useEffect, useMemo, useRef, useState } from "react";

import { ACTION_GLYPH, GLYPH_SVG, paintGlyph } from "../assets/map/glyphs";
import { usePlayback } from "../hooks/usePlayback";
import { useReplayStore } from "../store/replayStore";
import { pixiHex, tokens } from "../tokens";
import type {
  AgentTickStateView,
  PlayerView,
  RoomView,
  TickView,
  VentView,
} from "../types/api";
import { AgentToken } from "./AgentToken";
import { BodyMarker } from "./BodyMarker";
import { MapToolbar } from "./MapToolbar";
import { ROOM_PALETTE, RoomRect } from "./RoomRect";
import { SabotageOverlay } from "./SabotageOverlay";
import { VentEdge } from "./VentEdge";

extend({ Container, Graphics, Text });

const CANVAS_WIDTH = 920;
const CANVAS_HEIGHT = 450;
const CANVAS_PADDING = 44;
const BACKGROUND_COLOR = ROOM_PALETTE.PAPER_1;
const KILL = pixiHex(tokens.kill);
const VENT_TRAVEL_MS = 900; // dive → travel → emerge, one-shot per escape

interface MapTransform {
  scale: number;
  offsetX: number;
  offsetY: number;
}

interface VentEdgeSpec {
  key: string;
  fromRoom: RoomView;
  toRoom: RoomView;
}

interface VentSegment {
  actorId: string;
  enterTick: number;
  exitTick: number;
  fromRoomId: string;
  toRoomId: string;
}

interface BodySpec {
  victimId: string;
  roomId: string;
  isDiscovered: boolean;
}

const NO_BODIES: readonly BodySpec[] = [];
const prefersReducedMotion =
  typeof window !== "undefined" &&
  typeof window.matchMedia === "function" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Trigger one re-render once the web fonts finish loading so Pixi re-rasterises
// any text it first drew with a fallback (Fredoka / Space Mono load via
// @fontsource in index.css). This is a redraw NUDGE, never a render gate — the
// canvas (rooms / tokens / labels) always renders so nothing depends on it.
function useFontNudge(): void {
  const [, bump] = useState(0);
  useEffect(() => {
    let cancelled = false;
    const fonts = document.fonts;
    if (fonts === undefined) return;
    void Promise.all([fonts.load("600 14px Fredoka"), fonts.load('700 12px "Space Mono"')])
      .then(() => fonts.ready)
      .then(
        () => {
          if (!cancelled) bump((n) => n + 1);
        },
        () => {
          /* font load failed — keep the fallback, never block the canvas */
        },
      );
    return () => {
      cancelled = true;
    };
  }, []);
}

// Uniform transform fitting the rooms' bounding box into the padded canvas,
// preserving aspect ratio and centering (unchanged from Phase 4).
function computeTransform(rooms: readonly RoomView[]): MapTransform {
  if (rooms.length === 0) {
    return { scale: 1, offsetX: 0, offsetY: 0 };
  }
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const room of rooms) {
    minX = Math.min(minX, room.position.x);
    minY = Math.min(minY, room.position.y);
    maxX = Math.max(maxX, room.position.x + room.size.width);
    maxY = Math.max(maxY, room.position.y + room.size.height);
  }
  const contentWidth = maxX - minX;
  const contentHeight = maxY - minY;
  const availWidth = CANVAS_WIDTH - 2 * CANVAS_PADDING;
  const availHeight = CANVAS_HEIGHT - 2 * CANVAS_PADDING;
  const scale = Math.min(availWidth / contentWidth, availHeight / contentHeight);
  const offsetX = CANVAS_PADDING + (availWidth - contentWidth * scale) / 2 - minX * scale;
  const offsetY = CANVAS_PADDING + (availHeight - contentHeight * scale) / 2 - minY * scale;
  return { scale, offsetX, offsetY };
}

// One edge per unordered room pair (A→B and B→A collapse). Unknown rooms skipped.
function buildVentEdges(
  vents: readonly VentView[],
  roomsById: ReadonlyMap<string, RoomView>,
): VentEdgeSpec[] {
  const seen = new Set<string>();
  const edges: VentEdgeSpec[] = [];
  for (const vent of vents) {
    for (const connectedRoomId of vent.connected_room_ids) {
      const a = vent.room_id;
      const b = connectedRoomId;
      if (a === b) continue;
      const key = a < b ? `${a}|${b}` : `${b}|${a}`;
      if (seen.has(key)) continue;
      seen.add(key);
      const fromRoom = roomsById.get(a);
      const toRoom = roomsById.get(b);
      if (fromRoom === undefined || toRoom === undefined) continue;
      edges.push({ key, fromRoom, toRoom });
    }
  }
  return edges;
}

// Each `enter` (dive) vent event fully describes the escape (engine emits both
// endpoints + traversal); pair it with `enter + traversal_ticks` as the emerge
// tick so the map animates dive→travel→emerge (DESIGN.md §3.2).
function buildVentSegments(ticks: readonly TickView[]): VentSegment[] {
  const segments: VentSegment[] = [];
  for (const tick of ticks) {
    for (const event of tick.events) {
      if (event.type === "vent" && event.phase === "enter") {
        segments.push({
          actorId: event.actor_id,
          enterTick: event.tick,
          exitTick: event.tick + Math.max(1, event.traversal_ticks),
          fromRoomId: event.from_room_id,
          toRoomId: event.to_room_id,
        });
      }
    }
  }
  return segments;
}

// One forward pass yields the cumulative body set as of each tick index
// (Omniscient ground truth): one per victim killed at/before the tick, flagged
// discovered once a report_body fires. Shared by reference across unchanged runs.
function buildBodyStatesByTick(ticks: readonly TickView[]): BodySpec[][] {
  const result: BodySpec[][] = new Array<BodySpec[]>(ticks.length);
  const killRoomByVictim = new Map<string, string>();
  const discovered = new Set<string>();
  let current: BodySpec[] = [];
  for (let t = 0; t < ticks.length; t++) {
    const tick = ticks[t];
    let changed = false;
    if (tick !== undefined) {
      for (const event of tick.events) {
        if (event.type === "kill") {
          killRoomByVictim.set(event.victim_id, event.room_id);
          changed = true;
        } else if (event.type === "report_body" && !discovered.has(event.body_of)) {
          discovered.add(event.body_of);
          changed = true;
        }
      }
    }
    if (changed) {
      current = [...killRoomByVictim.entries()].map(([victimId, roomId]) => ({
        victimId,
        roomId,
        isDiscovered: discovered.has(victimId),
      }));
    }
    result[t] = current;
  }
  return result;
}

// ── one vent-escape traveller: a one-shot dive→travel→emerge along the route ──
interface VentTravelerProps {
  fromRoom: RoomView;
  toRoom: RoomView;
  color: string;
  label: string;
  glyph: string;
  scale: number;
  offsetX: number;
  offsetY: number;
  playKey: string;
}

function VentTraveler({
  fromRoom,
  toRoom,
  color,
  label,
  glyph,
  scale,
  offsetX,
  offsetY,
  playKey,
}: VentTravelerProps) {
  const [progress, setProgress] = useState(prefersReducedMotion ? 1 : 0);
  const elapsedRef = useRef(0);
  useEffect(() => {
    elapsedRef.current = 0;
    setProgress(prefersReducedMotion ? 1 : 0);
  }, [playKey]);
  useTick((ticker: { deltaMS: number }) => {
    if (prefersReducedMotion || elapsedRef.current >= VENT_TRAVEL_MS) return;
    elapsedRef.current = Math.min(VENT_TRAVEL_MS, elapsedRef.current + ticker.deltaMS);
    setProgress(elapsedRef.current / VENT_TRAVEL_MS);
  });

  const fx = offsetX + (fromRoom.position.x + fromRoom.size.width / 2) * scale;
  const fy = offsetY + (fromRoom.position.y + fromRoom.size.height / 2) * scale;
  const tx = offsetX + (toRoom.position.x + toRoom.size.width / 2) * scale;
  const ty = offsetY + (toRoom.position.y + toRoom.size.height / 2) * scale;

  // Three phases: dive (0–0.2, shrink into the source vent), travel (0.2–0.8,
  // glide the route), emerge (0.8–1, pop out at the destination).
  const travel = Math.min(1, Math.max(0, (progress - 0.2) / 0.6));
  const x = fx + (tx - fx) * travel;
  const y = fy + (ty - fy) * travel;
  const capsuleScale =
    progress < 0.2 ? 1 - (progress / 0.2) * 0.55 : progress > 0.8 ? 0.45 + ((progress - 0.8) / 0.2) * 0.55 : 0.45;
  const tokenColor = pixiHex(color);
  const inkLine = pixiHex(tokens.ink[500]);

  return (
    <>
      <pixiGraphics
        draw={(g: Graphics) => {
          g.clear();
          // The dotted travel trail already covered.
          const ux = tx - fx;
          const uy = ty - fy;
          const len = Math.hypot(ux, uy) || 1;
          const nx = ux / len;
          const ny = uy / len;
          for (let d = 0; d < len * travel; d += 9) {
            g.moveTo(fx + nx * d, fy + ny * d);
            g.lineTo(fx + nx * Math.min(d + 0.5, len * travel), fy + ny * Math.min(d + 0.5, len * travel));
          }
          g.stroke({ width: 2.4, color: inkLine, alpha: 0.85, cap: "round" });
          // The capsule (ghosted identity disc, dashed-feel via alpha).
          g.circle(x, y, 11 * capsuleScale);
          g.fill({ color: tokenColor, alpha: 0.92 });
          g.stroke({ width: 2, color: pixiHex(tokens.ink[900]), alpha: 0.9 });
        }}
      />
      <pixiGraphics
        draw={(g: Graphics) =>
          paintGlyph(g, glyph, x, y, 12 * capsuleScale, pixiHex(tokens.paper[0]), 0.95)
        }
      />
      <pixiText
        text={`${label} ⇡`}
        anchor={0.5}
        x={x}
        y={y - 18}
        alpha={0.85}
        style={{ fill: inkLine, fontSize: 9, fontFamily: tokens.type.mono, fontWeight: "700" }}
      />
    </>
  );
}

// ── one kill flash: a pulsing kill ring around the kill room (Omniscient) ──
function KillFlash({
  room,
  scale,
  offsetX,
  offsetY,
}: {
  room: RoomView;
  scale: number;
  offsetX: number;
  offsetY: number;
}) {
  const [alpha, setAlpha] = useState(0.9);
  const tRef = useRef(0);
  useTick((ticker: { deltaMS: number }) => {
    if (prefersReducedMotion) {
      setAlpha(0.85);
      return;
    }
    tRef.current += ticker.deltaMS;
    // killpulse: 0.25 ↔ 0.95 on a ~2.6s sine (matches the converge keyframe).
    setAlpha(0.6 + 0.35 * Math.sin((tRef.current / 2600) * Math.PI * 2));
  });
  const x = offsetX + room.position.x * scale;
  const y = offsetY + room.position.y * scale;
  return (
    <pixiGraphics
      draw={(g: Graphics) => {
        g.clear();
        g.roundRect(x - 4, y - 4, room.size.width * scale + 8, room.size.height * scale + 8, tokens.radius.xl);
        g.stroke({ width: 2.8, color: KILL, alpha });
      }}
    />
  );
}

export function MapView() {
  const currentReplay = useReplayStore((s) => s.currentReplay);
  const currentTick = useReplayStore((s) => s.currentTick);
  const perspective = useReplayStore((s) => s.perspective);
  const { tickNumber } = usePlayback();
  useFontNudge();

  const gameId = currentReplay?.metadata.game_id ?? null;
  const prevTickRef = useRef(currentTick);
  const prevGameIdRef = useRef<string | null>(gameId);
  const prevTick = prevTickRef.current;
  const sameReplay = prevGameIdRef.current === gameId;
  useEffect(() => {
    prevTickRef.current = currentTick;
  }, [currentTick]);
  useEffect(() => {
    prevGameIdRef.current = gameId;
  }, [gameId]);

  // Per-replay invariants, memoized on `currentReplay` identity (Task 6.7).
  const transform = useMemo(
    () => computeTransform(currentReplay?.map.rooms ?? []),
    [currentReplay],
  );
  const roomsById = useMemo<ReadonlyMap<string, RoomView>>(
    () => new Map((currentReplay?.map.rooms ?? []).map((r) => [r.id, r])),
    [currentReplay],
  );
  const playerById = useMemo<ReadonlyMap<string, PlayerView>>(
    () => new Map((currentReplay?.players ?? []).map((p) => [p.agent_id, p])),
    [currentReplay],
  );
  const playerIndexById = useMemo<ReadonlyMap<string, number>>(
    () => new Map((currentReplay?.players ?? []).map((p, i) => [p.agent_id, i])),
    [currentReplay],
  );
  const ventEdges = useMemo<VentEdgeSpec[]>(
    () => buildVentEdges(currentReplay?.map.vents ?? [], roomsById),
    [currentReplay, roomsById],
  );
  const ventSegments = useMemo<VentSegment[]>(
    () => buildVentSegments(currentReplay?.ticks ?? []),
    [currentReplay],
  );
  const bodyStatesByTick = useMemo<BodySpec[][]>(
    () => buildBodyStatesByTick(currentReplay?.ticks ?? []),
    [currentReplay],
  );

  if (currentReplay === null) {
    return (
      <div className="w-full max-w-[960px]">
        <MapToolbar />
        <div
          className="flex items-center justify-center rounded-b-xl rounded-tr-xl border-2 border-ink-900 bg-paper-0 font-mono text-sm text-ink-400 shadow-chrome-1"
          style={{ width: CANVAS_WIDTH, height: CANVAS_HEIGHT }}
        >
          Select a replay to view the map.
        </div>
      </div>
    );
  }

  const rooms = currentReplay.map.rooms;
  const tick = currentReplay.ticks[currentTick];
  const { scale, offsetX, offsetY } = transform;
  const bodyIndex = Math.min(currentTick, currentReplay.ticks.length - 1);
  const omniscientBodies = bodyStatesByTick[bodyIndex] ?? NO_BODIES;
  const agentStates = tick?.agent_states ?? [];
  const animate = sameReplay && Math.abs(currentTick - prevTick) === 1;

  const omniscient = perspective.mode === "omniscient";
  const fogAgentId = perspective.mode === "agent" ? perspective.agentId : null;

  // ── As-agent fog: dim to EXACTLY this agent's AgentVisibilityView (Task 12.3).
  const selfState: AgentTickStateView | null =
    fogAgentId === null
      ? null
      : (agentStates.find((s) => s.agent_id === fogAgentId) ?? null);
  const visibility = selfState?.visibility ?? null;
  // A dead / unspawned agent has no field of view: nothing is lit.
  const fogNoView = fogAgentId !== null && (selfState === null || !selfState.is_alive || visibility === null);

  const litRoomIds = new Set<string>();
  if (fogAgentId !== null && !fogNoView && visibility !== null) {
    if (selfState?.room_id != null) litRoomIds.add(selfState.room_id);
    for (const vp of visibility.visible_players) litRoomIds.add(vp.room);
    for (const vb of visibility.visible_bodies) litRoomIds.add(vb.room);
  }
  const agentAware =
    visibility !== null && visibility.audible_events.some((e) => e.kind === "sabotage_alarm");

  // Active vent escapes at this engine tick (Omniscient only).
  const activeVentByActor = new Map<string, VentSegment>();
  if (omniscient) {
    for (const seg of ventSegments) {
      if (seg.enterTick <= tickNumber && tickNumber < seg.exitTick) {
        activeVentByActor.set(seg.actorId, seg);
      }
    }
  }

  // ── tokens ──
  const tokenSpecs: Array<{
    id: string;
    room: RoomView;
    color: string;
    action: AgentTickStateView["current_action"] | null;
    showRoleBadge: boolean;
  }> = [];

  if (omniscient) {
    for (const state of agentStates) {
      if (!state.is_alive) continue;
      if (activeVentByActor.has(state.agent_id)) continue; // rendered as a traveller
      if (state.is_venting || state.room_id === null) continue;
      const room = roomsById.get(state.room_id);
      const player = playerById.get(state.agent_id);
      if (room === undefined || player === undefined) continue;
      tokenSpecs.push({
        id: state.agent_id,
        room,
        color: player.color,
        action: state.current_action,
        showRoleBadge: player.role === "IMPOSTOR",
      });
    }
  } else if (fogAgentId !== null && !fogNoView && visibility !== null) {
    // Self (the agent always sees itself); role badge suppressed under fog.
    if (selfState !== null && selfState.room_id !== null) {
      const room = roomsById.get(selfState.room_id);
      const player = playerById.get(fogAgentId);
      if (room !== undefined && player !== undefined && !selfState.is_venting) {
        tokenSpecs.push({
          id: fogAgentId,
          room,
          color: player.color,
          action: selfState.current_action,
          showRoleBadge: false,
        });
      }
    }
    // Other players ONLY where this agent saw them (the projection's room).
    for (const vp of visibility.visible_players) {
      const room = roomsById.get(vp.room);
      const player = playerById.get(vp.id);
      if (room === undefined || player === undefined) continue;
      tokenSpecs.push({
        id: vp.id,
        room,
        color: player.color,
        action: null, // witnessed-action glyphs stay omniscient; sighting only
        showRoleBadge: false,
      });
    }
  }

  const tokens_ = tokenSpecs.map((spec) => {
    const actionGlyph =
      spec.action !== null && spec.action !== "IDLE"
        ? GLYPH_SVG[ACTION_GLYPH[spec.action]]
        : null;
    const roleBadge = spec.showRoleBadge ? GLYPH_SVG.impostor : null;
    return (
      <AgentToken
        key={spec.id}
        room={spec.room}
        jitterIndex={playerIndexById.get(spec.id) ?? 0}
        color={spec.color}
        label={spec.id}
        actionGlyph={actionGlyph}
        roleBadge={roleBadge}
        scale={scale}
        offsetX={offsetX}
        offsetY={offsetY}
        animate={animate}
      />
    );
  });

  // ── bodies ──
  const bodySpecs: BodySpec[] = omniscient
    ? [...omniscientBodies]
    : visibility === null
      ? []
      : visibility.visible_bodies.map((vb) => ({
          victimId: vb.victim_id,
          roomId: vb.room,
          isDiscovered: false, // fog: "a body the agent sees", not the global report state
        }));

  const bodyMarkers = bodySpecs.flatMap((body) => {
    const room = roomsById.get(body.roomId);
    if (room === undefined) return [];
    return [
      <BodyMarker
        key={body.victimId}
        room={room}
        placementIndex={playerIndexById.get(body.victimId) ?? 0}
        isDiscovered={body.isDiscovered}
        victimLabel={body.victimId}
        glyph={GLYPH_SVG.body}
        scale={scale}
        offsetX={offsetX}
        offsetY={offsetY}
      />,
    ];
  });

  // ── vent escapes + kill flashes (Omniscient only) ──
  const ventTravelers = omniscient
    ? [...activeVentByActor.values()].flatMap((seg) => {
        const fromRoom = roomsById.get(seg.fromRoomId);
        const toRoom = roomsById.get(seg.toRoomId);
        const player = playerById.get(seg.actorId);
        if (fromRoom === undefined || toRoom === undefined || player === undefined) return [];
        return [
          <VentTraveler
            key={`${seg.actorId}:${seg.enterTick}`}
            playKey={`${seg.actorId}:${seg.enterTick}`}
            fromRoom={fromRoom}
            toRoom={toRoom}
            color={player.color}
            label={seg.actorId}
            glyph={GLYPH_SVG.vent}
            scale={scale}
            offsetX={offsetX}
            offsetY={offsetY}
          />,
        ];
      })
    : [];

  const killFlashes = omniscient
    ? (tick?.events ?? []).flatMap((event, i) => {
        if (event.type !== "kill") return [];
        const room = roomsById.get(event.room_id);
        if (room === undefined) return [];
        return [
          <KillFlash
            key={`kill-${event.room_id}-${i}`}
            room={room}
            scale={scale}
            offsetX={offsetX}
            offsetY={offsetY}
          />,
        ];
      })
    : [];

  // Corridors (the public floorplan topology — shown in BOTH modes) as thick ink
  // links centre-to-centre, drawn FIRST so the opaque rooms mask their interiors
  // and only the between-room connectors read (matches canonical_1-map-reference).
  const corridorLayer = (
    <pixiGraphics
      draw={(g: Graphics) => {
        g.clear();
        for (const edge of currentReplay.map.edges) {
          const a = roomsById.get(edge.from_room_id);
          const b = roomsById.get(edge.to_room_id);
          if (a === undefined || b === undefined) continue;
          g.moveTo(
            offsetX + (a.position.x + a.size.width / 2) * scale,
            offsetY + (a.position.y + a.size.height / 2) * scale,
          );
          g.lineTo(
            offsetX + (b.position.x + b.size.width / 2) * scale,
            offsetY + (b.position.y + b.size.height / 2) * scale,
          );
        }
        g.stroke({ width: 6, color: ROOM_PALETTE.INK_900, cap: "round", join: "round" });
      }}
    />
  );

  return (
    <div className="w-full max-w-[960px]">
      <MapToolbar />
      <div className="overflow-hidden rounded-b-xl rounded-tr-xl border-2 border-ink-900 shadow-chrome-1">
        <Application width={CANVAS_WIDTH} height={CANVAS_HEIGHT} background={BACKGROUND_COLOR} antialias>
          {corridorLayer}
          {omniscient &&
            ventEdges.map((edge) => (
              <VentEdge
                key={edge.key}
                fromRoom={edge.fromRoom}
                toRoom={edge.toRoom}
                scale={scale}
                offsetX={offsetX}
                offsetY={offsetY}
              />
            ))}
          {rooms.map((room) => (
            <RoomRect
              key={room.id}
              room={room}
              scale={scale}
              offsetX={offsetX}
              offsetY={offsetY}
              visible={omniscient || litRoomIds.has(room.id)}
            />
          ))}
          {bodyMarkers}
          {tokens_}
          {ventTravelers}
          {killFlashes}
          <SabotageOverlay
            width={CANVAS_WIDTH}
            height={CANVAS_HEIGHT}
            sabotage={tick?.sabotage ?? null}
            roomsById={roomsById}
            scale={scale}
            offsetX={offsetX}
            offsetY={offsetY}
            reactorGlyph={GLYPH_SVG.reactor}
            lightsGlyph={GLYPH_SVG.lights}
            omniscient={omniscient}
            agentAware={agentAware}
          />
        </Application>
      </div>
    </div>
  );
}
