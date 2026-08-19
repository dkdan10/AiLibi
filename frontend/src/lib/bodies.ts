// The map's body layer: which corpses are on the floor on a given frame, and how
// each one reads.
//
// PRESENCE IS ENGINE TRUTH. Every body comes from the served `TickView.bodies`,
// which projects `WorldState.bodies` — and `orchestrator/game.py` DELETES the
// corpse that triggered a body-report meeting when that meeting resolves. So a
// body leaves the map on the frame the engine drops it, and nothing is
// accumulated client-side.
//
// ATTRIBUTION IS SERVED. `killedBy` is read straight off `TickView.bodies[]
// .killed_by`, the privileged spectator field the DTO carries for exactly this
// layer — never re-derived from the kill event.
//
// DISCOVERY IS THE ONE DERIVED BIT. No `discovered` flag is served, so
// `isDiscovered` is the forward-accumulated set of `report_body` events. That is
// the same signal the engine writes (`engine/tick.py::_apply_report` sets
// `discovered_by` from the report action and nothing else), so the derivation
// and the engine agree by construction.
//
// FIREWALL (As-agent fog): the agent layer maps `AgentVisibilityView
// .visible_bodies` and only that. `VisibleBodyView` carries no killer, so
// `killedBy` is null, and `isDiscovered` is false — the fog states "a body this
// agent SEES", not the global report state. No `TickView.bodies` row can reach
// it: `visibleBodiesForTick` is not given one.
//
// Pure functions over the view-model — no React, no Pixi, no render state. The
// per-room grid and the `BODY_CAP` collapse need the canvas `scale` and stay in
// `MapView`; this module is what `lib/bodies.test.ts` can import and pin.

import type { AgentVisibilityView, BodyView, TickEventView } from "../types/api";

/** One body as the map draws it. */
export interface BodySpec {
  victimId: string;
  roomId: string;
  isDiscovered: boolean;
  killedBy: string | null; // spectator-only attribution; null under fog
}

/** The empty layer: the shared out-of-range fallback for a frame index. */
export const NO_BODIES: readonly BodySpec[] = [];

/**
 * The served body fields this layer reads. Derived from `BodyView` so a DTO
 * rename breaks the build; `body_id` is deliberately absent — the map keys
 * markers by victim.
 */
export type BodyRow = Pick<BodyView, "victim_id" | "room_id" | "killed_by">;

/**
 * The slice of a `TickView` this layer reads. Structural on purpose: a real
 * `TickView` satisfies it, and so does the committed served-payload dump the
 * test walks.
 */
export interface BodyTickSlice {
  readonly events: readonly TickEventView[];
  readonly bodies: readonly BodyRow[];
}

/**
 * The bodies on the floor on one frame, given the victims reported so far
 * (including this frame's reports).
 */
export function bodiesForTick(
  tick: BodyTickSlice,
  reportedVictimIds: ReadonlySet<string>,
): BodySpec[] {
  return tick.bodies.map((body) => ({
    victimId: body.victim_id,
    roomId: body.room_id,
    isDiscovered: reportedVictimIds.has(body.victim_id),
    killedBy: body.killed_by,
  }));
}

/**
 * One forward pass yielding the Omniscient body layer for every frame index.
 *
 * The only thing threaded forward is the `report_body` set; presence and
 * attribution are re-read from each frame's own served rows.
 */
export function bodyStatesByTick(ticks: readonly BodyTickSlice[]): BodySpec[][] {
  const result: BodySpec[][] = new Array<BodySpec[]>(ticks.length);
  const reportedVictimIds = new Set<string>();
  for (const [t, tick] of ticks.entries()) {
    for (const event of tick.events) {
      if (event.type === "report_body") {
        reportedVictimIds.add(event.body_of);
      }
    }
    result[t] = bodiesForTick(tick, reportedVictimIds);
  }
  return result;
}

/**
 * The As-agent body layer: exactly the bodies this agent's visibility packet
 * lists, killer-free and never flagged discovered. `null` visibility (dead,
 * unspawned, or Omniscient-only frames) lights nothing.
 */
export function visibleBodiesForTick(visibility: AgentVisibilityView | null): BodySpec[] {
  if (visibility === null) {
    return [];
  }
  return visibility.visible_bodies.map((body) => ({
    victimId: body.victim_id,
    roomId: body.room,
    isDiscovered: false,
    killedBy: null,
  }));
}
