// The map stage chrome: the floorplan legend + the PERSPECTIVE SWITCHER
// (Omniscient ↔ As-agent [agent picker]) (Task 12.5; the Claude-Design map-chrome
// prompt in tasks/phase-12.md, design/phase-12/stage-1-design.md §2.2, §3.2).
//
// This is the one piece of the map stage that is presentational chrome (the
// canvas below it is hand-coded Pixi). It composes purely from `tokens.ts` (the
// Tailwind `@theme` utilities) — no hardcoded hex — and drives the Zustand store
// (`setPerspective`) WITHOUT editing the shell: the persistent App-level
// `PerspectiveBanner` reads the same `perspective` field and reflects the change
// (Wave-B mount discipline — the switcher mounts inside the stage, never the
// shell).
//
// Perspective is the dominant, persistent two-truth mode cue: Omniscient reads
// SOLID / authoritative (open eye); As-agent reads GHOSTED / fogged (eye-off +
// a dashed "FOG OF WAR" treatment). States: no-replay / omniscient / agent.

import { useMemo } from "react";

import { usePlayback } from "../hooks/usePlayback";
import { OMNISCIENT } from "../lib/playback";
import { useReplayStore } from "../store/replayStore";
import type { MapLayoutView } from "../types/api";

// Inline chrome icons (DOM SVG — distinct from the Pixi map asset set). Open eye
// = omniscient (sees all); eye-off = the fog of war.
function EyeIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function EyeOffIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M17.94 17.94A10 10 0 0 1 12 20C5 20 1 13 1 13a18 18 0 0 1 5.06-5.94M9.9 4.24A9 9 0 0 1 12 4c7 0 11 7 11 7a18 18 0 0 1-2.16 3.19M1 1l22 22" />
    </svg>
  );
}

// One de-duplicated edge per unordered room pair → the vent-ring count for the
// legend (matches buildVentEdges in MapView).
function ventRingCount(map: MapLayoutView): number {
  const seen = new Set<string>();
  for (const vent of map.vents) {
    for (const other of vent.connected_room_ids) {
      if (other === vent.room_id) continue;
      const key = vent.room_id < other ? `${vent.room_id}|${other}` : `${other}|${vent.room_id}`;
      seen.add(key);
    }
  }
  return seen.size;
}

export function MapToolbar() {
  const replay = useReplayStore((s) => s.currentReplay);
  const perspective = useReplayStore((s) => s.perspective);
  const setPerspective = useReplayStore((s) => s.setPerspective);
  const { frame } = usePlayback();

  // First living agent at the current tick — the sensible default subject when
  // entering fog (a dead agent has no field of view).
  const defaultAgentId = useMemo(() => {
    const living = frame?.agent_states.find((s) => s.is_alive);
    return living?.agent_id ?? replay?.players[0]?.agent_id ?? null;
  }, [frame, replay]);

  if (replay === null) {
    return (
      <div className="flex items-center justify-between gap-3 rounded-t-xl border-2 border-b-0 border-ink-900 bg-paper-0 px-4 py-3">
        <span className="font-display text-sm font-semibold text-ink-900">Map</span>
        <span className="font-mono text-xs text-ink-500">no replay — select one to view the map</span>
      </div>
    );
  }

  const inFog = perspective.mode === "agent";
  const fogAgentId = inFog ? perspective.agentId : null;
  const ring = ventRingCount(replay.map);

  const enterFog = () => {
    if (defaultAgentId !== null) {
      setPerspective({ mode: "agent", agentId: defaultAgentId });
    }
  };

  return (
    <div
      className={
        "flex flex-wrap items-center justify-between gap-3 rounded-t-xl border-2 border-b-0 border-ink-900 px-4 py-3 transition-colors " +
        (inFog ? "bg-paper-3" : "bg-paper-0")
      }
    >
      {/* Legend (left) */}
      <div className="flex items-center gap-2.5">
        <span className="rounded-md border-2 border-ink-900 bg-ink-900 px-2 py-1 font-mono text-2xs font-bold uppercase tracking-wider text-paper-0">
          canonical_1
        </span>
        <span className="font-mono text-2xs text-ink-500">
          {replay.map.rooms.length} rooms · {replay.map.edges.length} corridors · {ring}-vent ring
        </span>
      </div>

      {/* Perspective switcher (right) — the dominant two-truth mode cue */}
      <div className="flex items-center gap-2" role="group" aria-label="Map perspective">
        <span className="font-mono text-3xs uppercase tracking-wide text-ink-500">Perspective</span>
        <div className="flex overflow-hidden rounded-lg border-2 border-ink-900 shadow-chrome-1">
          <button
            type="button"
            aria-pressed={!inFog}
            onClick={() => setPerspective(OMNISCIENT)}
            className={
              "flex items-center gap-2 px-3 py-1.5 text-sm font-semibold transition-colors " +
              (!inFog ? "bg-ink-900 text-paper-0" : "bg-paper-0 text-ink-700 hover:bg-paper-2")
            }
          >
            <EyeIcon />
            Omniscient
          </button>
          <button
            type="button"
            aria-pressed={inFog}
            onClick={enterFog}
            disabled={defaultAgentId === null}
            className={
              "flex items-center gap-2 border-l-2 border-ink-900 px-3 py-1.5 text-sm font-semibold transition-colors " +
              (inFog
                ? "bg-ink-900 text-paper-0"
                : "bg-paper-0 text-ink-700 hover:bg-paper-2 disabled:opacity-40")
            }
          >
            <EyeOffIcon />
            As-agent
          </button>
        </div>

        {inFog && (
          <label
            className="flex items-center gap-2 rounded-lg border-2 border-dashed border-ink-700 bg-paper-0 px-2 py-1"
            title="Choose whose field of view to simulate (fog of war)"
          >
            <span className="font-mono text-4xs uppercase tracking-wide text-ink-500">fog of war · as</span>
            <select
              aria-label="Perspective agent"
              value={fogAgentId ?? ""}
              onChange={(e) => setPerspective({ mode: "agent", agentId: e.target.value })}
              className="rounded-md border border-ink-300 bg-paper-0 px-1.5 py-1 font-mono text-xs font-bold text-ink-900"
            >
              {replay.players.map((player) => (
                <option key={player.agent_id} value={player.agent_id}>
                  {player.agent_id}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>
    </div>
  );
}
