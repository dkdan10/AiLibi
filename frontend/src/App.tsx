import { useEffect, useState } from "react";

import { BeliefMatrix } from "./components/BeliefMatrix";
import { MapView } from "./components/MapView";
import { MeetingPill } from "./components/MeetingPill";
import { MeetingView } from "./components/MeetingView";
import { ReplayControls } from "./components/ReplayControls";
import { ReplayPicker } from "./components/ReplayPicker";
import { ThoughtStream } from "./components/ThoughtStream";
import { TournamentDashboard } from "./components/TournamentDashboard";
import { useReplayStore } from "./store/replayStore";

// Phase 4.4 vertical slice (DESIGN.md §7): pick a replay, see the map, step
// through ticks and watch agents move. Top: ReplayPicker. Middle: the PixiJS
// MapView canvas. A MeetingPill surfaces at meeting ticks. Phase 4.11
// (DESIGN.md §11.4) adds ReplayControls — the primary playback bar (scrubber,
// speed, play/pause, snap-to-meeting) pinned to the bottom of the viewport;
// it subsumes the 4.4 TickStepper. Phase 4.6 (DESIGN.md §5) adds the
// MeetingView transcript overlay, mounted at the app root above all other
// content. Phase 4.8 (DESIGN.md §6) adds the ThoughtStream right rail, which
// mounts alongside an open meeting. Phase 4.10 (DESIGN.md §6.3) adds the
// BeliefMatrix who-suspects-whom heatmap as a left rail above the MeetingView
// modal, also gated on a selected meeting.
//
// Phase 5.7 (DESIGN.md §11.3) adds a SECOND top-level view — the Tournament
// Dashboard — reached by tab navigation (tabs, not a router: the app is
// single-page and a router is dead weight for two views). One view renders at
// a time; the dashboard is backed by its own `useTournamentStore`, independent
// of the frozen Phase 4 replay store.

type TabId = "replay" | "dashboard";

const TABS: ReadonlyArray<{ id: TabId; label: string }> = [
  { id: "replay", label: "Replay Viewer" },
  { id: "dashboard", label: "Tournament Dashboard" },
];

export default function App() {
  const loadReplayList = useReplayStore((s) => s.loadReplayList);
  const [activeTab, setActiveTab] = useState<TabId>("replay");

  useEffect(() => {
    void loadReplayList();
  }, [loadReplayList]);

  return (
    <div className="min-h-screen bg-slate-900 p-6 text-slate-100">
      <header className="mb-4">
        <h1 className="text-2xl font-bold">AiLibi</h1>
        <nav
          className="mt-3 flex gap-2"
          role="tablist"
          aria-label="Spectator views"
        >
          {TABS.map((tab) => {
            const isActive = tab.id === activeTab;
            return (
              <button
                key={tab.id}
                type="button"
                role="tab"
                aria-selected={isActive}
                onClick={() => {
                  setActiveTab(tab.id);
                }}
                className={
                  "rounded-t border-b-2 px-4 py-2 text-sm font-medium transition-colors " +
                  (isActive
                    ? "border-emerald-500 text-emerald-100"
                    : "border-transparent text-slate-400 hover:text-slate-200")
                }
              >
                {tab.label}
              </button>
            );
          })}
        </nav>
      </header>

      {activeTab === "replay" ? (
        <>
          {/* Bottom padding clears the fixed ReplayControls bar so the last row
              stays visible when scrolled to the end. */}
          <main className="flex flex-col gap-4 pb-28">
            <ReplayPicker />
            <div className="flex justify-center">
              <MapView />
            </div>
            <div className="flex flex-wrap items-center gap-4">
              <MeetingPill />
            </div>
          </main>

          <MeetingView />
          <BeliefMatrix />
          <ThoughtStream />
          <ReplayControls />
        </>
      ) : (
        <TournamentDashboard />
      )}
    </div>
  );
}
