import { useEffect, type ReactNode } from "react";

import { useReplayStore } from "./store/replayStore";

// Phase 4.3 skeleton. This stub proves the API -> store -> UI wiring works:
// on mount it loads the replay list and renders it (or a loading / error
// state). The PixiJS map, meeting overlay, and belief views land in 4.4+.
export default function App() {
  const replayList = useReplayStore((s) => s.replayList);
  const replayListError = useReplayStore((s) => s.replayListError);
  const loadReplayList = useReplayStore((s) => s.loadReplayList);
  const selectReplay = useReplayStore((s) => s.selectReplay);
  const currentReplay = useReplayStore((s) => s.currentReplay);
  const currentReplayError = useReplayStore((s) => s.currentReplayError);

  useEffect(() => {
    void loadReplayList();
  }, [loadReplayList]);

  let replaysBody: ReactNode;
  if (replayListError !== null) {
    replaysBody = (
      <p className="rounded border border-red-700 bg-red-950 px-4 py-2 text-red-200">
        Failed to load replays: {replayListError}
      </p>
    );
  } else if (replayList === null) {
    replaysBody = <p className="text-slate-400">Loading replays…</p>;
  } else if (replayList.length === 0) {
    replaysBody = (
      <p className="text-slate-400">
        No replays found in the configured replay directory.
      </p>
    );
  } else {
    replaysBody = (
      <ul className="flex flex-col gap-2">
        {replayList.map((replay) => (
          <li key={replay.game_id}>
            <button
              type="button"
              onClick={() => {
                void selectReplay(replay.game_id);
              }}
              className="w-full rounded border border-slate-700 bg-slate-800 px-4 py-2 text-left transition-colors hover:bg-slate-700"
            >
              <span className="font-mono">seed {replay.seed}</span>
              {" · "}
              {replay.winner ?? "unfinished"}
              {" · "}
              {replay.total_ticks} ticks
            </button>
          </li>
        ))}
      </ul>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 p-6 text-slate-100">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">AiLibi — Replay Viewer</h1>
        <p className="text-sm text-slate-400">
          Phase 4 skeleton. Map, meeting, and belief views arrive in later tasks.
        </p>
      </header>

      <main className="max-w-2xl">
        <section>
          <h2 className="mb-2 text-lg font-semibold">Replays</h2>
          {replaysBody}
        </section>

        {(currentReplay !== null || currentReplayError !== null) && (
          <section className="mt-6">
            {currentReplayError !== null ? (
              <p className="rounded border border-red-700 bg-red-950 px-4 py-2 text-red-200">
                Failed to load replay: {currentReplayError}
              </p>
            ) : currentReplay !== null ? (
              <p className="text-emerald-300">
                Loaded{" "}
                <span className="font-mono">{currentReplay.metadata.game_id}</span>{" "}
                — {currentReplay.ticks.length} ticks,{" "}
                {currentReplay.meetings.length} meetings.
              </p>
            ) : null}
          </section>
        )}
      </main>
    </div>
  );
}
