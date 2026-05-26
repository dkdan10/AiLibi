// Replay list + selection (DESIGN.md §7). Reads the store's `replayList` and
// renders one button per replay; clicking selects it. The replay list itself is
// loaded once on mount by App. Loading, empty, and error states all render
// meaningfully so the spectator can tell whether the API connection works.

import type { ReactNode } from "react";

import { useReplayStore } from "../store/replayStore";

export function ReplayPicker() {
  const replayList = useReplayStore((s) => s.replayList);
  const replayListError = useReplayStore((s) => s.replayListError);
  const selectReplay = useReplayStore((s) => s.selectReplay);
  const currentReplay = useReplayStore((s) => s.currentReplay);
  const currentReplayError = useReplayStore((s) => s.currentReplayError);

  const selectedGameId = currentReplay?.metadata.game_id ?? null;

  let body: ReactNode;
  if (replayListError !== null) {
    body = (
      <p className="rounded border border-red-700 bg-red-950 px-4 py-2 text-red-200">
        Failed to load replays: {replayListError}
      </p>
    );
  } else if (replayList === null) {
    body = <p className="text-slate-400">Loading replays…</p>;
  } else if (replayList.length === 0) {
    body = (
      <p className="text-slate-400">
        No replays found in the configured replay directory.
      </p>
    );
  } else {
    body = (
      <ul className="flex flex-wrap gap-2">
        {replayList.map((replay) => {
          const isSelected = replay.game_id === selectedGameId;
          return (
            <li key={replay.game_id}>
              <button
                type="button"
                onClick={() => {
                  void selectReplay(replay.game_id);
                }}
                aria-pressed={isSelected}
                className={
                  "rounded border px-4 py-2 font-mono text-sm transition-colors " +
                  (isSelected
                    ? "border-emerald-500 bg-emerald-900 text-emerald-100"
                    : "border-slate-700 bg-slate-800 text-slate-100 hover:bg-slate-700")
                }
              >
                seed {replay.seed} — winner {replay.winner ?? "—"} — ticks{" "}
                {replay.total_ticks}
              </button>
            </li>
          );
        })}
      </ul>
    );
  }

  return (
    <section className="flex flex-col gap-2">
      <h2 className="text-lg font-semibold">Replays</h2>
      {body}
      {currentReplayError !== null && (
        <p className="rounded border border-red-700 bg-red-950 px-4 py-2 text-red-200">
          Failed to load replay: {currentReplayError}
        </p>
      )}
    </section>
  );
}
