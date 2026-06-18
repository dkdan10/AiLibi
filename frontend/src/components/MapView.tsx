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
import { AgentToken, TWEEN_DURATION_MS } from "./AgentToken";
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
  killedBy: string | null; // spectator-only attribution; null under fog
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

// The vent-escape route is split across two events: `enter` (dive) carries
// from==to == the dive room (engine/rules.py: the entered vent must be IN the
// actor's room), and the actual cross-room travel is only known at the matching
// `exit` (its `to_room_id` is where the impostor emerges). Pair them per actor so
// the animation shows the real dive→travel→emerge over the in-vent window, not an
// in-place entry pulse. An unmatched dive (a meeting interrupted the vent before
// emergence) degrades to a brief in-place pulse at the dive room.
function buildVentSegments(ticks: readonly TickView[]): VentSegment[] {
  const segments: VentSegment[] = [];
  const pendingDive = new Map<string, { enterTick: number; fromRoomId: string }>();
  for (const tick of ticks) {
    for (const event of tick.events) {
      if (event.type !== "vent") continue;
      if (event.phase === "enter") {
        pendingDive.set(event.actor_id, {
          enterTick: event.tick,
          fromRoomId: event.from_room_id,
        });
      } else {
        const dive = pendingDive.get(event.actor_id);
        pendingDive.delete(event.actor_id);
        segments.push({
          actorId: event.actor_id,
          enterTick: dive?.enterTick ?? event.tick - Math.max(1, event.traversal_ticks),
          exitTick: event.tick,
          fromRoomId: dive?.fromRoomId ?? event.from_room_id,
          toRoomId: event.to_room_id, // the emerge room — the real destination
        });
      }
    }
  }
  for (const [actorId, dive] of pendingDive) {
    segments.push({
      actorId,
      enterTick: dive.enterTick,
      exitTick: dive.enterTick + 1,
      fromRoomId: dive.fromRoomId,
      toRoomId: dive.fromRoomId,
    });
  }
  return segments;
}

// One forward pass yields the cumulative body set as of each tick index
// (Omniscient ground truth): one per victim killed at/before the tick, flagged
// discovered once a report_body fires. Shared by reference across unchanged runs.
function buildBodyStatesByTick(ticks: readonly TickView[]): BodySpec[][] {
  const result: BodySpec[][] = new Array<BodySpec[]>(ticks.length);
  const killRoomByVictim = new Map<string, string>();
  // The kill event carries the killer; persist it so the body keeps its
  // attribution after the kill event scrolls off the current tick (the role the
  // `killed_by` view-model field plays — re-derived here from the kill event).
  const killerByVictim = new Map<string, string>();
  const discovered = new Set<string>();
  let current: BodySpec[] = [];
  for (let t = 0; t < ticks.length; t++) {
    const tick = ticks[t];
    let changed = false;
    if (tick !== undefined) {
      for (const event of tick.events) {
        if (event.type === "kill") {
          killRoomByVictim.set(event.victim_id, event.room_id);
          killerByVictim.set(event.victim_id, event.killer_id);
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
        killedBy: killerByVictim.get(victimId) ?? null,
      }));
    }
    result[t] = current;
  }
  return result;
}

// ── one vent-escape traveller: a capsule gliding the dive→emerge route ──
// Position is TICK-ANCHORED: `progress` is `(tick - enterTick)/(exitTick -
// enterTick)` (0 at the dive room, 1 at the emerge room), so a paused/scrubbed
// frame always shows the impostor where the replay actually places it — never a
// future room. Within a single-tick step it tweens the rendered position toward
// the target over TWEEN_DURATION_MS (mirroring AgentToken), so playback still
// shows a smooth glide rather than a snap. Reduced-motion snaps instead.
interface VentTravelerProps {
  fromRoom: RoomView;
  toRoom: RoomView;
  color: string;
  label: string;
  glyph: string;
  progress: number;
  animate: boolean;
  scale: number;
  offsetX: number;
  offsetY: number;
}

interface XY {
  x: number;
  y: number;
}

function VentTraveler({
  fromRoom,
  toRoom,
  color,
  label,
  glyph,
  progress,
  animate,
  scale,
  offsetX,
  offsetY,
}: VentTravelerProps) {
  const fx = offsetX + (fromRoom.position.x + fromRoom.size.width / 2) * scale;
  const fy = offsetY + (fromRoom.position.y + fromRoom.size.height / 2) * scale;
  const tx = offsetX + (toRoom.position.x + toRoom.size.width / 2) * scale;
  const ty = offsetY + (toRoom.position.y + toRoom.size.height / 2) * scale;
  const target: XY = { x: fx + (tx - fx) * progress, y: fy + (ty - fy) * progress };

  const [pos, setPos] = useState<XY>(target);
  const posRef = useRef<XY>(target);
  const fromRef = useRef<XY>(target);
  const toRef = useRef<XY>(target);
  const tweenRef = useRef<number>(1);

  useEffect(() => {
    if (animate && !prefersReducedMotion) {
      fromRef.current = posRef.current;
      toRef.current = target;
      tweenRef.current = 0;
    } else {
      fromRef.current = target;
      toRef.current = target;
      posRef.current = target;
      tweenRef.current = 1;
      setPos(target);
    }
    // Re-tween when the tick-derived progress changes (or the snap/tween mode
    // flips); `target` is a pure function of `progress` + the fixed transform.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [progress, animate]);

  useTick((ticker: { deltaMS: number }) => {
    if (tweenRef.current >= 1) return;
    tweenRef.current = Math.min(1, tweenRef.current + ticker.deltaMS / TWEEN_DURATION_MS);
    const f = fromRef.current;
    const t = toRef.current;
    const p = tweenRef.current;
    const next: XY = { x: f.x + (t.x - f.x) * p, y: f.y + (t.y - f.y) * p };
    posRef.current = next;
    setPos(next);
  });

  // Capsule shrinks mid-route (in the vent) and is full size at both ends, keyed
  // off how far along the route the RENDERED position sits — so it reads as
  // dive→travel→emerge during the tween without drifting from replay time.
  const routeLen = Math.hypot(tx - fx, ty - fy) || 1;
  const travelled = Math.min(1, Math.max(0, Math.hypot(pos.x - fx, pos.y - fy) / routeLen));
  const capsuleScale = 1 - 0.4 * Math.sin(travelled * Math.PI);
  const inkLine = pixiHex(tokens.ink[500]);

  return (
    <>
      <pixiGraphics
        draw={(g: Graphics) => {
          g.clear();
          // Dotted trail from the dive room to the current position.
          const nx = (tx - fx) / routeLen;
          const ny = (ty - fy) / routeLen;
          const drawn = routeLen * travelled;
          for (let d = 0; d < drawn; d += 9) {
            g.moveTo(fx + nx * d, fy + ny * d);
            g.lineTo(fx + nx * Math.min(d + 0.5, drawn), fy + ny * Math.min(d + 0.5, drawn));
          }
          g.stroke({ width: 2.4, color: inkLine, alpha: 0.85, cap: "round" });
          g.circle(pos.x, pos.y, 11 * capsuleScale);
          g.fill({ color: pixiHex(color), alpha: 0.92 });
          g.stroke({ width: 2, color: pixiHex(tokens.ink[900]), alpha: 0.9 });
        }}
      />
      <pixiGraphics
        draw={(g: Graphics) =>
          paintGlyph(g, glyph, pos.x, pos.y, 12 * capsuleScale, pixiHex(tokens.paper[0]), 0.95)
        }
      />
      <pixiText
        text={`${label} ⇡`}
        anchor={0.5}
        x={pos.x}
        y={pos.y - 18}
        alpha={0.85}
        style={{ fill: inkLine, fontSize: 9, fontFamily: tokens.type.mono, fontWeight: "700" }}
      />
    </>
  );
}

// ── sighting highlight: an additive "look here" cue lighting BOTH public
// referents a meeting sighting NAMES — the room and the agent (Task 12.7).
// Strictly additive — it only emphasises a room the current perspective ALREADY
// renders (the caller passes a room only when it is Omniscient-visible or lit
// under the selected agent's fog), so it never reveals a fogged position. The
// agent is marked AT the named room from the PUBLIC claim — never the agent's
// live tick position (that would be a ground-truth peek / leak): the badge
// annotates "the sighting names p-5 here", it does not assert where p-5 is now.
// The ring is role-NEUTRAL (ink outline + a soft paper glow); the agent badge
// carries the player's identity colour (identity ≠ guilt — public + safe).
// Static (no pulse) — a focus cue, not a drama beat — so no reduced-motion path.
function SightingHighlight({
  room,
  agentId,
  agentColor,
  scale,
  offsetX,
  offsetY,
}: {
  room: RoomView;
  agentId: string;
  agentColor: string | null;
  scale: number;
  offsetX: number;
  offsetY: number;
}) {
  const x = offsetX + room.position.x * scale;
  const y = offsetY + room.position.y * scale;
  const w = room.size.width * scale;
  const h = room.size.height * scale;
  const ink = pixiHex(tokens.ink[900]);
  const glow = pixiHex(tokens.paper[0]);
  const paper = pixiHex(tokens.paper[0]);
  const disc = agentColor === null ? pixiHex(tokens.ink[400]) : pixiHex(agentColor);
  // The agent badge sits just above the room ring so it reads as a tag on the
  // claim, distinct from the live tokens jittered inside the room.
  const badgeX = x + w / 2;
  const badgeY = y - 16;
  return (
    <>
      <pixiGraphics
        draw={(g: Graphics) => {
          g.clear();
          // Soft brighten over the named room (focus, channel-safe).
          g.roundRect(x, y, w, h, tokens.radius.lg);
          g.fill({ color: glow, alpha: 0.28 });
          // A bold ink ring just outside the room outline so it pops against the
          // existing 2.4px sticker stroke without recolouring it.
          g.roundRect(x - 5, y - 5, w + 10, h + 10, tokens.radius.xl);
          g.stroke({ width: 4, color: ink, alpha: 0.95 });
          // The named-agent badge: an identity disc on a cream sticker.
          g.circle(badgeX, badgeY, 11);
          g.fill(disc);
          g.stroke({ width: 2, color: ink });
        }}
      />
      <pixiText
        text={agentId.replace(/^p-/, "")}
        anchor={0.5}
        x={badgeX}
        y={badgeY}
        style={{ fill: paper, fontSize: 10, fontFamily: tokens.type.mono, fontWeight: "700" }}
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

// An agent's OWN action (uppercase AgentAction) → its glyph; IDLE shows none to
// keep the map calm.
function selfActionGlyph(action: AgentTickStateView["current_action"]): string | null {
  return action === "IDLE" ? null : GLYPH_SVG[ACTION_GLYPH[action]];
}

// A witnessed action on an As-agent SIGHTING is the server's firewall-gated
// `"kill"` / `"vent"` string (observation.packet.PlayerView.action), or null for
// an ordinary co-location. Show the matching glyph so the fog view keeps the
// kill / vent the selected agent actually saw — not just a plain sighting.
function witnessedActionGlyph(action: string | null): string | null {
  if (action === "kill") return GLYPH_SVG.kill;
  if (action === "vent") return GLYPH_SVG.vent;
  return null;
}

export function MapView() {
  const currentReplay = useReplayStore((s) => s.currentReplay);
  const currentTick = useReplayStore((s) => s.currentTick);
  const perspective = useReplayStore((s) => s.perspective);
  const highlightedSighting = useReplayStore((s) => s.highlightedSighting);
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

  // ── Task 12.7 cross-highlight: light the room a meeting sighting NAMES, but
  // ONLY when this perspective already renders it (Omniscient, or lit under the
  // selected agent's fog). Gating on `litRoomIds` keeps the highlight from
  // revealing a position the As-agent fog has hidden — a hover must never become
  // a leak. Purely additive: it reads the store and adds a ring; the fog / token
  // / body logic above is untouched.
  const highlightRoom =
    highlightedSighting !== null &&
    (omniscient || litRoomIds.has(highlightedSighting.roomId))
      ? (roomsById.get(highlightedSighting.roomId) ?? null)
      : null;

  // Active vent escapes at this engine tick (Omniscient only). The window is
  // INCLUSIVE of the exit tick so the traveller renders the emergence frame
  // (and the normal token is suppressed there — the traveller IS the emerged
  // token at that tick), keeping position tied to replay time, never ahead of it.
  const activeVentByActor = new Map<string, VentSegment>();
  if (omniscient) {
    for (const seg of ventSegments) {
      if (seg.enterTick <= tickNumber && tickNumber <= seg.exitTick) {
        activeVentByActor.set(seg.actorId, seg);
      }
    }
  }

  // ── tokens ──
  const tokenSpecs: Array<{
    id: string;
    room: RoomView;
    color: string;
    actionGlyph: string | null;
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
        actionGlyph: selfActionGlyph(state.current_action),
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
          actionGlyph: selfActionGlyph(selfState.current_action),
          showRoleBadge: false,
        });
      }
    }
    // Other players ONLY where this agent saw them (the projection's room), with
    // the WITNESSED action it saw (a firewall-gated kill / vent) — never the role.
    for (const vp of visibility.visible_players) {
      const room = roomsById.get(vp.room);
      const player = playerById.get(vp.id);
      if (room === undefined || player === undefined) continue;
      tokenSpecs.push({
        id: vp.id,
        room,
        color: player.color,
        actionGlyph: witnessedActionGlyph(vp.action),
        showRoleBadge: false,
      });
    }
  }

  const tokens_ = tokenSpecs.map((spec) => {
    const actionGlyph = spec.actionGlyph;
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
          killedBy: null, // firewall: the As-agent view never exposes the killer
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
        killedBy={body.killedBy}
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
        // Tick-anchored progress along the route (0 = dive room, 1 = emerge room).
        const span = seg.exitTick - seg.enterTick;
        const progress = span > 0 ? Math.min(1, Math.max(0, (tickNumber - seg.enterTick) / span)) : 1;
        return [
          <VentTraveler
            key={`${seg.actorId}:${seg.enterTick}`}
            fromRoom={fromRoom}
            toRoom={toRoom}
            color={player.color}
            label={seg.actorId}
            glyph={GLYPH_SVG.vent}
            progress={progress}
            animate={animate}
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
          {highlightRoom !== null && highlightedSighting !== null && (
            <SightingHighlight
              room={highlightRoom}
              agentId={highlightedSighting.agentId}
              agentColor={playerById.get(highlightedSighting.agentId)?.color ?? null}
              scale={scale}
              offsetX={offsetX}
              offsetY={offsetY}
            />
          )}
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
