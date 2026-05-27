import { useEffect } from "react";

import { BeliefMatrix } from "./components/BeliefMatrix";
import { MapView } from "./components/MapView";
import { MeetingPill } from "./components/MeetingPill";
import { MeetingView } from "./components/MeetingView";
import { ReplayPicker } from "./components/ReplayPicker";
import { ThoughtStream } from "./components/ThoughtStream";
import { TickStepper } from "./components/TickStepper";
import { useReplayStore } from "./store/replayStore";

// Phase 4.4 vertical slice (DESIGN.md §7): pick a replay, see the map, step
// through ticks and watch agents move. Top: ReplayPicker. Middle: the PixiJS
// MapView canvas. Bottom: TickStepper + a MeetingPill at meeting ticks. Phase
// 4.6 (DESIGN.md §5) adds the MeetingView transcript overlay, mounted at the
// app root above all other content. Phase 4.8 (DESIGN.md §6) adds the
// ThoughtStream right rail, which mounts alongside an open meeting. Phase 4.10
// (DESIGN.md §6.3) adds the BeliefMatrix who-suspects-whom heatmap as a left
// rail above the MeetingView modal, also gated on a selected meeting.
export default function App() {
  const loadReplayList = useReplayStore((s) => s.loadReplayList);

  useEffect(() => {
    void loadReplayList();
  }, [loadReplayList]);

  return (
    <div className="min-h-screen bg-slate-900 p-6 text-slate-100">
      <header className="mb-4">
        <h1 className="text-2xl font-bold">AiLibi — Replay Viewer</h1>
        <p className="text-sm text-slate-400">
          Pick a replay, then step through ticks to watch agents move between
          rooms.
        </p>
      </header>

      <main className="flex flex-col gap-4">
        <ReplayPicker />
        <div className="flex justify-center">
          <MapView />
        </div>
        <div className="flex flex-wrap items-center gap-4">
          <TickStepper />
          <MeetingPill />
        </div>
      </main>

      <MeetingView />
      <BeliefMatrix />
      <ThoughtStream />
    </div>
  );
}
