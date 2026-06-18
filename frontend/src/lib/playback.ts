// Pure playback derivations (Task 12.4; design/phase-12/stage-1-design.md §4 —
// the time model). This module is the SINGLE home for the tick↔frame mapping and
// every navigation/seek computation, so the transport, advantage scrubber, event
// timeline, and URL sync all agree on one source of truth — the engine tick.
//
// Background: the loader injects a synthetic `tick = -1` "Start" frame as
// `ticks[0]` (api/replay_loader.py: the pre-game spawn state), so a frame's
// ARRAY INDEX and its ENGINE TICK NUMBER differ. Before 12.4 that mapping was
// re-derived ad hoc in ReplayControls, MeetingPill, and MapView (the recurring
// off-by-one). Here it lives once: `tickNumberAt` (index → engine tick) and
// `frameIndexForTick` (engine tick → index) are the only two resolvers, and the
// `tick = -1` Start is treated as a real pre-game value, never a "no data"
// sentinel.
//
// No React, no store, no side effects — everything is a pure function of the
// already-loaded view-model, which keeps it deterministic and trivially
// testable. The store/hook own state; this module only computes.

import type {
  MeetingView,
  TickEventView,
  TickView,
} from "../types/api";

// The engine tick of the loader's synthetic pre-game frame. A REAL value (the
// state before tick 0), not a sentinel — surfaces label it "Start" but treat it
// as a navigable frame you can seek to and step from.
export const START_TICK = -1;

// ─────────────────────────────────────────────────────────────────────────────
// Shared view/overlay state types (consumed by the store, the hook, and 12.5 /
// 12.6 later). Defined here — not in the store — so `lib/` stays the dependency
// sink (the store imports these; this module imports nothing from the store).
// ─────────────────────────────────────────────────────────────────────────────

/** Top-level view container (URL-synced; no router dependency). */
export type ViewId = "replays" | "highlights" | "tournament" | "workspace";

/** Belief-panel data toggle (consumed by 12.6). Same layout, swapped data. */
export type BeliefViewMode = "belief" | "truth" | "error";

/**
 * Map perspective overlay (consumed by 12.5). The base is always ground truth;
 * `omniscient` reveals all, `agent` applies that agent's fog of war. Role/guilt
 * is never encoded here — this is a view selector, not identity.
 */
export type Perspective =
  | { readonly mode: "omniscient" }
  | { readonly mode: "agent"; readonly agentId: string };

/** The default perspective (reveal everything). */
export const OMNISCIENT: Perspective = { mode: "omniscient" };

// ─────────────────────────────────────────────────────────────────────────────
// The one tick↔frame mapping.
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Frame ARRAY INDEX → ENGINE TICK NUMBER (the single index→tick resolver).
 * `ticks[0]` is the synthetic Start frame (engine tick -1). Out-of-range indices
 * clamp into the array; an empty timeline yields {@link START_TICK}.
 */
export function tickNumberAt(ticks: readonly TickView[], index: number): number {
  if (ticks.length === 0) {
    return START_TICK;
  }
  const clamped = Math.max(0, Math.min(index, ticks.length - 1));
  return ticks[clamped]?.tick ?? START_TICK;
}

/**
 * ENGINE TICK NUMBER → frame ARRAY INDEX (the single tick→index resolver, the
 * inverse of {@link tickNumberAt}). Returns the index of the frame whose engine
 * tick equals `tickNumber`; for a tick between recorded frames or out of range it
 * clamps to the nearest frame AT OR BEFORE it (never below 0). Recorded frames
 * are in ascending engine-tick order (Start frame first), so a single forward
 * scan suffices — game timelines are bounded to hundreds of ticks.
 */
export function frameIndexForTick(
  ticks: readonly TickView[],
  tickNumber: number,
): number {
  if (ticks.length === 0) {
    return 0;
  }
  let best = 0;
  for (let i = 0; i < ticks.length; i++) {
    const frame = ticks[i];
    if (frame === undefined) {
      continue;
    }
    if (frame.tick === tickNumber) {
      return i;
    }
    if (frame.tick < tickNumber) {
      best = i;
    } else {
      break; // ascending order: every later frame is also > tickNumber
    }
  }
  return best;
}

/** True iff `index` resolves to the synthetic pre-game Start frame. */
export function isStartIndex(ticks: readonly TickView[], index: number): boolean {
  return tickNumberAt(ticks, index) === START_TICK;
}

// ─────────────────────────────────────────────────────────────────────────────
// Event / meeting / key-moment navigation (drives the jump controls). Everything
// compares ENGINE TICK NUMBERS, never array indices.
// ─────────────────────────────────────────────────────────────────────────────

// Jump-event beats (DESIGN.md §4): kill / meeting / vent / sabotage. report_body
// and task_completed are NOT jump-event targets.
const JUMP_EVENT_TYPES: ReadonlySet<TickEventView["type"]> = new Set([
  "kill",
  "meeting_triggered",
  "vent",
  "sabotage",
]);

/** Ascending, de-duplicated engine ticks that carry a jump-event beat. */
export function eventTickNumbers(ticks: readonly TickView[]): number[] {
  const set = new Set<number>();
  for (const frame of ticks) {
    for (const event of frame.events) {
      if (JUMP_EVENT_TYPES.has(event.type)) {
        set.add(frame.tick);
      }
    }
  }
  return [...set].sort((a, b) => a - b);
}

/** Ascending engine ticks at which a meeting occurs. */
export function meetingTickNumbers(meetings: readonly MeetingView[]): number[] {
  return meetings.map((meeting) => meeting.tick).sort((a, b) => a - b);
}

/** The first tick in `sorted` strictly greater than `current`, else `null`. */
export function nextAfter(
  sorted: readonly number[],
  current: number,
): number | null {
  for (const value of sorted) {
    if (value > current) {
      return value;
    }
  }
  return null;
}

/** The last tick in `sorted` strictly less than `current`, else `null`. */
export function prevBefore(
  sorted: readonly number[],
  current: number,
): number | null {
  let found: number | null = null;
  for (const value of sorted) {
    if (value < current) {
      found = value;
    } else {
      break;
    }
  }
  return found;
}

// "Next key moment" = the next advantage-graph INFLECTION (DESIGN.md §4): a
// drama beat distinct from the raw step / jump-event controls. The four beats are
// kill, body-report/meeting, ejection, and sabotage start, ranked kill → meeting
// → ejection so that when several land on one tick the highest-priority beat
// labels it. (sabotage ranks last — the quietest of the four.)
export type KeyMomentKind = "kill" | "meeting" | "ejection" | "sabotage";

const KEY_MOMENT_RANK: Record<KeyMomentKind, number> = {
  kill: 0,
  meeting: 1,
  ejection: 2,
  sabotage: 3,
};

export interface KeyMoment {
  readonly tick: number;
  readonly kind: KeyMomentKind;
}

/** Ascending key-moment inflections, one per tick (ranked when they collide). */
export function keyMoments(
  ticks: readonly TickView[],
  meetings: readonly MeetingView[],
): KeyMoment[] {
  const byTick = new Map<number, KeyMomentKind>();
  const consider = (tick: number, kind: KeyMomentKind): void => {
    const existing = byTick.get(tick);
    if (existing === undefined || KEY_MOMENT_RANK[kind] < KEY_MOMENT_RANK[existing]) {
      byTick.set(tick, kind);
    }
  };
  for (const frame of ticks) {
    for (const event of frame.events) {
      if (event.type === "kill") {
        consider(frame.tick, "kill");
      } else if (event.type === "meeting_triggered") {
        consider(frame.tick, "meeting");
      } else if (event.type === "sabotage") {
        consider(frame.tick, "sabotage");
      }
    }
  }
  for (const meeting of meetings) {
    consider(meeting.tick, "meeting");
    if (meeting.outcome === "EJECTED") {
      consider(meeting.tick, "ejection");
    }
  }
  return [...byTick.entries()]
    .map(([tick, kind]) => ({ tick, kind }))
    .sort((a, b) => a.tick - b.tick);
}

/** Ascending key-moment ticks (the navigation target list). */
export function keyMomentTicks(
  ticks: readonly TickView[],
  meetings: readonly MeetingView[],
): number[] {
  return keyMoments(ticks, meetings).map((moment) => moment.tick);
}

// ─────────────────────────────────────────────────────────────────────────────
// Advantage graph + event timeline derivations.
// ─────────────────────────────────────────────────────────────────────────────

export interface AdvantagePoint {
  readonly index: number; // frame array index (x-axis is shared with the timeline)
  readonly tick: number; // engine tick number
  readonly advantage: number; // [-1, 1]; positive favours the crew
}

/** The clickable advantage scrubber's series (one point per frame). */
export function advantageSeries(ticks: readonly TickView[]): AdvantagePoint[] {
  return ticks.map((frame, index) => ({
    index,
    tick: frame.tick,
    advantage: frame.advantage.advantage,
  }));
}

// Event-timeline lane markers: kill / meeting / vent / sabotage placed on the
// ACTOR's lane (DESIGN.md §2.3, "lanes: 1/agent").
export type TimelineKind = "kill" | "meeting" | "vent" | "sabotage";

export interface TimelineMarker {
  readonly key: string;
  readonly tick: number;
  readonly agentId: string; // which lane
  readonly kind: TimelineKind;
}

/** Per-agent timeline markers across the whole replay. */
export function timelineMarkers(ticks: readonly TickView[]): TimelineMarker[] {
  const markers: TimelineMarker[] = [];
  for (const frame of ticks) {
    let ordinal = 0;
    for (const event of frame.events) {
      let agentId: string | null = null;
      let kind: TimelineKind | null = null;
      switch (event.type) {
        case "kill":
          agentId = event.killer_id;
          kind = "kill";
          break;
        case "vent":
          agentId = event.actor_id;
          kind = "vent";
          break;
        case "sabotage":
          agentId = event.actor_id;
          kind = "sabotage";
          break;
        case "meeting_triggered":
          agentId = event.triggered_by;
          kind = "meeting";
          break;
        default:
          break; // report_body / task_completed: not lane markers
      }
      if (agentId !== null && kind !== null) {
        markers.push({
          key: `${frame.tick}:${ordinal}:${kind}`,
          tick: frame.tick,
          agentId,
          kind,
        });
        ordinal += 1;
      }
    }
  }
  return markers;
}

// ─────────────────────────────────────────────────────────────────────────────
// URL sync (DESIGN.md §2.1, §4) — `history.replaceState` + `URLSearchParams`,
// no router dependency. Seven keys round-trip so every moment is shareable +
// reload-stable: set / game_id / tick / perspective / beliefView /
// selectedAgent / selectedMeeting (plus `view` for the top-level container).
// `tick` is the ENGINE TICK NUMBER (human-meaningful + shareable); the store
// holds the array index and the resolvers above bridge them.
// ─────────────────────────────────────────────────────────────────────────────

export interface PlaybackUrlState {
  readonly set: string | null;
  readonly gameId: string | null;
  readonly tick: number | null;
  readonly perspective: Perspective;
  readonly beliefView: BeliefViewMode;
  readonly selectedAgent: string | null;
  readonly selectedMeeting: string | null;
  readonly view: ViewId | null;
}

const BELIEF_VIEW_MODES: readonly BeliefViewMode[] = ["belief", "truth", "error"];
const VIEW_IDS: readonly ViewId[] = [
  "replays",
  "highlights",
  "tournament",
  "workspace",
];

function isBeliefViewMode(value: string | null): value is BeliefViewMode {
  return value !== null && (BELIEF_VIEW_MODES as readonly string[]).includes(value);
}

function isViewId(value: string | null): value is ViewId {
  return value !== null && (VIEW_IDS as readonly string[]).includes(value);
}

/** Parse a `location.search` string into playback state (inverse of serialize). */
export function parsePlaybackParams(search: string): PlaybackUrlState {
  const params = new URLSearchParams(search);

  let tick: number | null = null;
  const tickRaw = params.get("tick");
  if (tickRaw !== null) {
    const parsed = Number.parseInt(tickRaw, 10);
    if (Number.isFinite(parsed)) {
      tick = parsed;
    }
  }

  const perspectiveRaw = params.get("perspective");
  const perspective: Perspective =
    perspectiveRaw === null ||
    perspectiveRaw === "" ||
    perspectiveRaw === "omniscient"
      ? OMNISCIENT
      : { mode: "agent", agentId: perspectiveRaw };

  const beliefRaw = params.get("beliefView");

  return {
    set: params.get("set"),
    gameId: params.get("game_id"),
    tick,
    perspective,
    beliefView: isBeliefViewMode(beliefRaw) ? beliefRaw : "belief",
    selectedAgent: params.get("selectedAgent"),
    selectedMeeting: params.get("selectedMeeting"),
    view: isViewId(params.get("view")) ? (params.get("view") as ViewId) : null,
  };
}

/**
 * Serialize playback state to a `?…` query string (inverse of parse). Default
 * values are omitted to keep URLs clean; because parse falls back to the same
 * defaults, the round-trip preserves the exact moment regardless.
 */
export function serializePlaybackParams(state: PlaybackUrlState): string {
  const params = new URLSearchParams();
  if (state.set !== null && state.set !== "") {
    params.set("set", state.set);
  }
  if (state.gameId !== null) {
    params.set("game_id", state.gameId);
  }
  if (state.tick !== null) {
    params.set("tick", String(state.tick));
  }
  if (state.perspective.mode === "agent") {
    params.set("perspective", state.perspective.agentId);
  }
  if (state.beliefView !== "belief") {
    params.set("beliefView", state.beliefView);
  }
  if (state.selectedAgent !== null) {
    params.set("selectedAgent", state.selectedAgent);
  }
  if (state.selectedMeeting !== null) {
    params.set("selectedMeeting", state.selectedMeeting);
  }
  if (state.view !== null) {
    params.set("view", state.view);
  }
  const query = params.toString();
  return query === "" ? "" : `?${query}`;
}
