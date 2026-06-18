// The app shell (Task 12.4; design/phase-12/stage-1-design.md §2.1, §2.3, §4).
// Two levels of PRE-DECLARED mount points so every Wave-B surface plugs in
// WITHOUT ever editing this file (the parallel-dispatch guarantee):
//
//   (a) a top-level view container — `view` lives in the store and is URL-synced
//       (no router) — for Replays + Highlights (→ 12.9), Tournament (→ 12.10),
//       and the Replay Workspace.
//   (b) within the workspace, named slots per §2.3. Each slot mounts an existing
//       component at its STABLE path; the Wave-B PR that owns a surface rewrites
//       that component (its own scope) and the shell picks it up automatically.
//
// SLOT ↔ SURFACE CHECKLIST (every 12.5–12.10 + transport/advantage/timeline has
// a mount; none requires an App.tsx edit):
//   • Replays route          → <ReplayPicker/>        (12.9 — browser)
//   • Highlights route        → <ReplayPicker/>        (12.9 — view-aware reel)
//   • Tournament route        → <TournamentDashboard/> (12.10)
//   • Workspace · perspective → <PerspectiveBanner/>   (12.4 shell; 12.5 switcher
//                                                        lands inside its stage)
//   • Workspace · roster      → <RosterRail/>          (12.4 shell, hand-coded)
//   • Workspace · stage(map)  → <MapView/>             (12.5)
//   • Workspace · stage(meet) → <MeetingView/>         (12.7 — map↔meeting morph)
//   • Workspace · mind        → <ThoughtStream/>       (12.8)
//   • Workspace · belief      → <BeliefMatrix/>        (12.6 — overlay/full toggle)
//   • Workspace · advantage   → <AdvantageGraph/>      (12.4)
//   • Workspace · timeline    → <EventTimeline/>       (12.4)
//   • Workspace · transport   → <ReplayControls/>      (12.4)
//
// `currentTick` stays the array index (the frozen store contract every mounted
// surface reads); the index↔engine-tick mapping lives once in `lib/playback`.

import { useEffect } from "react";

import { BeliefMatrix } from "./components/BeliefMatrix";
import { MapView } from "./components/MapView";
import { MeetingPill } from "./components/MeetingPill";
import { MeetingView } from "./components/MeetingView";
import {
  AdvantageGraph,
  EventTimeline,
  ReplayControls,
} from "./components/ReplayControls";
import { ReplayPicker } from "./components/ReplayPicker";
import { ThoughtStream } from "./components/ThoughtStream";
import { TournamentDashboard } from "./components/TournamentDashboard";
import { usePlayback, usePlaybackEngine } from "./hooks/usePlayback";
import { OMNISCIENT, type ViewId } from "./lib/playback";
import { useReplayStore } from "./store/replayStore";

// The single side-effecting playback driver (timer + auto-follow + URL sync),
// isolated in a render-null leaf so its store subscriptions don't re-render the
// whole shell on every tick.
function PlaybackEngine() {
  usePlaybackEngine();
  return null;
}

const TABS: ReadonlyArray<{ id: Exclude<ViewId, "workspace">; label: string }> = [
  { id: "replays", label: "Replays" },
  { id: "highlights", label: "Highlights" },
  { id: "tournament", label: "Tournament" },
];

function TopNav() {
  const view = useReplayStore((s) => s.view);
  const setView = useReplayStore((s) => s.setView);
  // The workspace is reached by selecting a replay, so it keeps the Replays tab
  // lit as its parent route.
  const active: ViewId = view === "workspace" ? "replays" : view;
  return (
    <nav className="flex gap-2" aria-label="Spectator views">
      {TABS.map((tab) => {
        const isActive = tab.id === active;
        return (
          <button
            key={tab.id}
            type="button"
            aria-current={isActive ? "page" : undefined}
            onClick={() => {
              setView(tab.id);
            }}
            className={
              "rounded-md border-2 border-ink-900 px-4 py-2 text-sm font-semibold transition-colors " +
              (isActive
                ? "bg-ink-900 text-paper-0 shadow-chrome-1"
                : "bg-paper-0 text-ink-900 hover:bg-paper-2")
            }
          >
            {tab.label}
          </button>
        );
      })}
    </nav>
  );
}

// Dominant mode banner (§2.3): seed/roster context + the persistent perspective
// indicator. The basic Omniscient/As-agent picker here keeps `perspective`
// exercisable and URL-round-trippable now; 12.5 lands the richer switcher inside
// the stage's map toolbar (this banner is the shell-level mode indicator).
function PerspectiveBanner() {
  const replay = useReplayStore((s) => s.currentReplay);
  const perspective = useReplayStore((s) => s.perspective);
  const setPerspective = useReplayStore((s) => s.setPerspective);
  const setView = useReplayStore((s) => s.setView);

  const meta = replay?.metadata ?? null;
  // The interactive As-agent SWITCHER is 12.5's (it lands with the map fog +
  // toolbar). 12.4 only stands up the mode INDICATOR + the `perspective` store
  // field / URL round-trip. Crucially we do NOT expose a user-facing way to
  // ENTER As-agent here: the meeting / mind / belief panels are still omniscient
  // (they show every role + private memory), so switching into fog now would
  // leak through them. A deep link can still set As-agent (so 12.5 can develop
  // against it); for that case we offer a one-way "Exit fog" back to the safe,
  // consistent Omniscient view.
  const inFog = perspective.mode === "agent";

  return (
    <header className="flex flex-wrap items-center justify-between gap-3 rounded-lg border-2 border-ink-900 bg-paper-0 px-4 py-3 shadow-chrome-1">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={() => {
            setView("replays");
          }}
          className="rounded-md border-2 border-ink-900 bg-paper-0 px-2.5 py-1 text-sm font-medium text-ink-900 hover:bg-paper-2"
        >
          ‹ Replays
        </button>
        <span className="font-mono text-sm text-ink-700">
          {meta === null
            ? "No replay selected"
            : `seed ${meta.seed} · ${replay?.players.length ?? 0}p · ${meta.winner ?? "—"}`}
        </span>
      </div>
      <div className="flex items-center gap-2">
        <span className="font-mono text-[10px] uppercase tracking-wide text-ink-500">
          Perspective
        </span>
        <span
          aria-label={`Perspective: ${inFog ? `As ${perspective.agentId}` : "Omniscient"}`}
          className="rounded-md border-2 border-ink-900 bg-paper-0 px-2 py-1 font-mono text-sm text-ink-900"
        >
          {inFog ? `As ${perspective.agentId} · fog` : "Omniscient"}
        </span>
        {inFog && (
          <button
            type="button"
            onClick={() => {
              setPerspective(OMNISCIENT);
            }}
            title="Return to the Omniscient view (the As-agent switcher arrives with the map)"
            className="rounded-md border-2 border-ink-900 bg-paper-0 px-2.5 py-1 text-sm font-medium text-ink-900 hover:bg-paper-2"
          >
            Exit fog
          </button>
        )}
      </div>
    </header>
  );
}

// Hand-coded roster rail (12.4) with the §2.3 advantage bar. Role badge is shown
// in Omniscient only — hidden under the As-agent fog (the firewall, simulated in
// the UI). Alive/dead comes from the current frame.
function RosterRail() {
  const replay = useReplayStore((s) => s.currentReplay);
  const perspective = useReplayStore((s) => s.perspective);
  const { frame } = usePlayback();

  if (replay === null) {
    return null;
  }

  const aliveById = new Map<string, boolean>();
  for (const state of frame?.agent_states ?? []) {
    aliveById.set(state.agent_id, state.is_alive);
  }
  const adv = frame?.advantage ?? null;
  // Firewall, simulated in the UI: in As-agent fog an agent does NOT know hidden
  // deaths, the living-crew count, or the impostor count — only the GLOBAL task
  // counter (DESIGN.md §1.2 broadcasts that to every agent). So gate the
  // omniscient-only facts (crew/impostor counts, per-player alive/dead, role) to
  // Omniscient; the task progress is agent-visible and shows in both modes.
  const omniscient = perspective.mode === "omniscient";
  const taskPct =
    adv !== null && adv.tasks_required > 0
      ? Math.round((adv.tasks_completed / adv.tasks_required) * 100)
      : 0;

  return (
    <aside className="w-60 shrink-0 rounded-lg border-2 border-ink-900 bg-paper-0 p-3 shadow-chrome-1">
      <h2 className="mb-2 text-lg">Roster</h2>
      {adv !== null && (
        <div className="mb-3 rounded-md border border-ink-200 p-2 font-mono text-[11px] text-ink-700">
          {omniscient && (
            <div className="mb-1.5 flex justify-between">
              <span>crew {adv.crew_alive}</span>
              <span>imp {adv.impostors_alive}</span>
            </div>
          )}
          <div className="h-1.5 overflow-hidden rounded-pill bg-paper-3">
            <div className="h-full bg-trust-strong" style={{ width: `${taskPct}%` }} />
          </div>
          <div className="mt-1 text-ink-500">
            tasks {adv.tasks_completed}/{adv.tasks_required}
          </div>
        </div>
      )}
      <ul className="flex flex-col gap-1">
        {replay.players.map((player) => {
          const alive = aliveById.get(player.agent_id) ?? true;
          return (
            <li
              key={player.agent_id}
              className="flex items-center gap-2 rounded-md border border-ink-100 px-2 py-1"
            >
              <span
                aria-hidden
                className="inline-block h-3 w-3 shrink-0 rounded-full ring-1 ring-ink-900/40"
                style={{ backgroundColor: player.color }}
              />
              <span className="min-w-0 flex-1 truncate font-mono text-xs text-ink-900">
                {player.agent_id}
              </span>
              {omniscient && (
                <span className="rounded-sm border border-ink-300 px-1 text-[9px] uppercase tracking-wide text-ink-500">
                  {player.role}
                </span>
              )}
              {omniscient && (
                <span
                  className={
                    "rounded-sm px-1 text-[9px] font-semibold uppercase " +
                    (alive ? "text-ink-500" : "bg-dead text-paper-0")
                  }
                >
                  {alive ? "alive" : "dead"}
                </span>
              )}
            </li>
          );
        })}
      </ul>
    </aside>
  );
}

// The Replay Workspace (§2.3). The fixed overlays (MeetingView modal, Belief /
// ThoughtStream rails) self-position; the bottom transport region is fixed above
// them so playback stays reachable while a meeting is open.
function Workspace() {
  return (
    <>
      <section className="flex flex-col gap-4 pb-[24rem]">
        <PerspectiveBanner />
        <div className="flex flex-wrap gap-4">
          <RosterRail />
          {/* Stage slot — the map (12.5). The meeting morph (12.7) is the
              MeetingView overlay below. */}
          <div className="min-w-0 flex-1">
            <div className="flex justify-center">
              <MapView />
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <MeetingPill />
            </div>
          </div>
        </div>
      </section>

      {/* Self-positioned slots: meeting morph (12.7), belief panel (12.6), mind
          panel (12.8). Each renders null until its selection gate opens. */}
      <MeetingView />
      <BeliefMatrix />
      <ThoughtStream />

      {/* Bottom transport region: advantage graph · event timeline · transport.
          Fixed above the overlays (z-70 > the meeting modal) so playback stays
          reachable. */}
      <div className="fixed inset-x-0 bottom-0 z-[70] border-t-2 border-ink-900 bg-paper-1/95 backdrop-blur">
        <div className="mx-auto flex max-w-[1600px] flex-col gap-2 p-3">
          <AdvantageGraph />
          <div className="max-h-40 overflow-y-auto pr-1">
            <EventTimeline />
          </div>
          <ReplayControls />
        </div>
      </div>
    </>
  );
}

export default function App() {
  const loadReplayList = useReplayStore((s) => s.loadReplayList);
  const view = useReplayStore((s) => s.view);

  useEffect(() => {
    void loadReplayList();
  }, [loadReplayList]);

  return (
    <div className="min-h-screen bg-paper-1 p-6 text-ink-900">
      <PlaybackEngine />
      <header className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl">AiLibi</h1>
        <TopNav />
      </header>

      {view === "tournament" ? (
        <TournamentDashboard />
      ) : view === "workspace" ? (
        <Workspace />
      ) : (
        // Replays + Highlights routes both mount the browser; 12.9 makes it
        // view-aware (it reads `view` from the store) and surfaces the reel.
        <ReplayPicker />
      )}
    </div>
  );
}
