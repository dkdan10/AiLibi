// The primary playback control surface (DESIGN.md §7, §11.4). Subsumes the
// minimal 4.4 TickStepper: a scrubber for arbitrary seek, a discrete speed
// selector, play/pause auto-advance, ±1-tick step buttons, and snap-to-meeting
// navigation. Every control drives the Zustand store; the rest of the UI
// re-renders against it. Mounts as a fixed bottom bar above every overlay
// (MeetingView z-50, BeliefMatrix z-[55], ThoughtStream z-[60]) so playback
// stays reachable while a meeting is open.

import { useEffect } from "react";

import { useReplayStore } from "../store/replayStore";
import type { PlaybackSpeed } from "../store/replayStore";
import type { MeetingView } from "../types/api";

const BASE_TICK_INTERVAL_MS = 500;

const SPEEDS: readonly PlaybackSpeed[] = [0.5, 1, 2, 4];

function findNextMeeting(
  meetings: readonly MeetingView[],
  currentTick: number,
): MeetingView | null {
  return meetings.find((m) => m.tick > currentTick) ?? null;
}

function findPrevMeeting(
  meetings: readonly MeetingView[],
  currentTick: number,
): MeetingView | null {
  for (let i = meetings.length - 1; i >= 0; i--) {
    const meeting = meetings[i];
    if (meeting !== undefined && meeting.tick < currentTick) {
      return meeting;
    }
  }
  return null;
}

const buttonClass =
  "rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm transition-colors " +
  "hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-40";

export function ReplayControls() {
  const replay = useReplayStore((s) => s.currentReplay);
  const currentTick = useReplayStore((s) => s.currentTick);
  const isPlaying = useReplayStore((s) => s.isPlaying);
  const playbackSpeed = useReplayStore((s) => s.playbackSpeed);
  const setCurrentTick = useReplayStore((s) => s.setCurrentTick);
  const setIsPlaying = useReplayStore((s) => s.setIsPlaying);
  const setPlaybackSpeed = useReplayStore((s) => s.setPlaybackSpeed);
  const selectMeeting = useReplayStore((s) => s.selectMeeting);

  // Auto-advance: while playing, step one tick every BASE/speed ms. currentTick
  // is read fresh from the store inside the interval (not closed over) so the
  // effect needn't depend on it — depending on currentTick would tear down and
  // re-register the interval every tick, causing drift / compound intervals.
  useEffect(() => {
    if (!isPlaying || replay === null) {
      return;
    }
    const intervalMs = BASE_TICK_INTERVAL_MS / playbackSpeed;
    const lastTick = replay.ticks.length - 1;
    const id = setInterval(() => {
      const nextTick = useReplayStore.getState().currentTick + 1;
      if (nextTick > lastTick) {
        setIsPlaying(false);
      } else {
        setCurrentTick(nextTick);
      }
    }, intervalMs);
    return () => {
      clearInterval(id);
    };
  }, [isPlaying, playbackSpeed, replay, setCurrentTick, setIsPlaying]);

  if (replay === null || replay.ticks.length === 0) {
    return null;
  }

  const lastTick = replay.ticks.length - 1;
  const canStepBack = currentTick > 0;
  const canStepForward = currentTick < lastTick;
  const isAtMeeting = replay.meetings.some((m) => m.tick === currentTick);

  const nextMeeting = findNextMeeting(replay.meetings, currentTick);
  const prevMeeting = findPrevMeeting(replay.meetings, currentTick);

  function snapTo(meeting: MeetingView | null): void {
    if (meeting === null) {
      return;
    }
    setCurrentTick(meeting.tick);
    selectMeeting(meeting.meeting_id);
  }

  return (
    <section
      aria-label="Replay controls"
      className="fixed bottom-0 left-0 right-0 z-[65] flex flex-wrap items-center gap-3 border-t border-slate-700 bg-slate-900/95 px-4 py-3 backdrop-blur"
    >
      {/* Transport: snap / step / play-pause / step / snap. */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          disabled={prevMeeting === null}
          onClick={() => {
            snapTo(prevMeeting);
          }}
          title="Snap to previous meeting"
          aria-label="Snap to previous meeting"
          className={buttonClass}
        >
          ⏮ Meeting
        </button>
        <button
          type="button"
          disabled={!canStepBack}
          onClick={() => {
            setCurrentTick(Math.max(0, currentTick - 1));
          }}
          title="Step back one tick"
          aria-label="Step back one tick"
          className={buttonClass}
        >
          −1
        </button>
        <button
          type="button"
          disabled={!canStepForward}
          onClick={() => {
            setIsPlaying(!isPlaying);
          }}
          className={
            buttonClass + " min-w-[5.5rem] font-semibold"
          }
        >
          {isPlaying ? "⏸ Pause" : "▶ Play"}
        </button>
        <button
          type="button"
          disabled={!canStepForward}
          onClick={() => {
            setCurrentTick(Math.min(lastTick, currentTick + 1));
          }}
          title="Step forward one tick"
          aria-label="Step forward one tick"
          className={buttonClass}
        >
          +1
        </button>
        <button
          type="button"
          disabled={nextMeeting === null}
          onClick={() => {
            snapTo(nextMeeting);
          }}
          title="Snap to next meeting"
          aria-label="Snap to next meeting"
          className={buttonClass}
        >
          Meeting ⏭
        </button>
      </div>

      {/* Scrubber + tick label. Grows to fill the row; wraps on narrow. */}
      <div className="flex min-w-[12rem] flex-1 items-center gap-3">
        <input
          type="range"
          min={0}
          max={lastTick}
          value={currentTick}
          aria-label="Seek tick"
          onInput={(e) => {
            setCurrentTick(Number(e.currentTarget.value));
          }}
          onChange={(e) => {
            setCurrentTick(Number(e.currentTarget.value));
          }}
          className="w-full cursor-pointer accent-emerald-500"
        />
        <span className="whitespace-nowrap font-mono text-sm text-slate-200">
          Tick {currentTick} / {lastTick}
          {isAtMeeting && (
            <span className="ml-2 rounded-full border border-amber-500 bg-amber-900/40 px-2 py-0.5 text-xs font-semibold text-amber-100">
              meeting
            </span>
          )}
        </span>
      </div>

      {/* Discrete speed selector. */}
      <div className="flex items-center gap-1">
        <span className="mr-1 text-xs uppercase tracking-wide text-slate-400">
          Speed
        </span>
        {SPEEDS.map((speed) => {
          const isActive = playbackSpeed === speed;
          return (
            <button
              key={speed}
              type="button"
              aria-pressed={isActive}
              onClick={() => {
                setPlaybackSpeed(speed);
              }}
              className={
                "rounded border px-3 py-2 text-sm font-mono transition-colors " +
                (isActive
                  ? "border-emerald-500 bg-emerald-900 text-emerald-100"
                  : "border-slate-700 bg-slate-800 text-slate-100 hover:bg-slate-700")
              }
            >
              {speed}×
            </button>
          );
        })}
      </div>
    </section>
  );
}
