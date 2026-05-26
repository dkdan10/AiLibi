// Manual tick navigation (DESIGN.md §7): prev / next buttons plus a
// "Tick: N / last" label. Buttons clamp at 0 and the last tick index and are
// disabled at the bounds. Play/pause, scrubbing, and auto-advance are 4.8.

import { useReplayStore } from "../store/replayStore";

export function TickStepper() {
  const currentReplay = useReplayStore((s) => s.currentReplay);
  const currentTick = useReplayStore((s) => s.currentTick);
  const setCurrentTick = useReplayStore((s) => s.setCurrentTick);

  if (currentReplay === null) {
    return null;
  }

  const lastTick = currentReplay.ticks.length - 1;
  const canPrev = currentTick > 0;
  const canNext = currentTick < lastTick;

  const buttonClass =
    "rounded border border-slate-700 bg-slate-800 px-4 py-2 transition-colors " +
    "hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-40";

  return (
    <section className="flex items-center gap-4">
      <button
        type="button"
        disabled={!canPrev}
        onClick={() => {
          setCurrentTick(Math.max(0, currentTick - 1));
        }}
        className={buttonClass}
      >
        ← prev
      </button>
      <span className="font-mono text-slate-200">
        Tick: {currentTick} / {lastTick}
      </span>
      <button
        type="button"
        disabled={!canNext}
        onClick={() => {
          setCurrentTick(Math.min(lastTick, currentTick + 1));
        }}
        className={buttonClass}
      >
        next →
      </button>
    </section>
  );
}
