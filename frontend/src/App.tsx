import { useEffect } from "react";

import { MapView } from "./components/MapView";
import { ReplayPicker } from "./components/ReplayPicker";
import { TickStepper } from "./components/TickStepper";
import { useReplayStore } from "./store/replayStore";

// Phase 4.4 vertical slice (DESIGN.md §7): pick a replay, see the map, step
// through ticks and watch agents move. Top: ReplayPicker. Middle: the PixiJS
// MapView canvas. Bottom: TickStepper.
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
        <TickStepper />
      </main>
    </div>
  );
}
