// BeliefMatrix — the CONNECTED Belief × Truth hero (Task 12.6;
// design/phase-12/stage-1-design.md §3.3, slice 4). It mounts into the workspace
// `belief` slot 12.4 pre-declares (App.tsx is untouched — Wave-B mount
// discipline) and wires the presentational <BeliefPanel/> to:
//   • the store's `beliefView` (the Belief / Ground-Truth / Error toggle, so the
//     active layer round-trips through the URL) and `perspective` (Omniscient ↔
//     As-agent fog → the firewall: ground-truth markers vanish in fog);
//   • the per-meeting `BeliefFrameView[]` snapshots served at
//     `GET /replays/{id}/beliefs` (12.2's projection — `BeliefErrorView.error` is
//     the signed Belief − Truth, `has_belief` flags "no belief yet" ≠ 0).
//
// The panel is an overlay/full-screen toggle (the slot's contract): a launcher
// pill opens it on demand, so the hero never blocks the map and never forces the
// MeetingView modal open (selecting a meeting does). The step control inside
// walks the meetings locally.
//
// Data path note (scope): the store + api/client are NOT in this task's scope, so
// the BeliefFrameView[] is fetched here directly (with the store's
// in-flight-replay guard mirrored) rather than via a new store action — the shape
// is exactly the served DTO, so a later store-backed fetch is a drop-in swap.

import { useEffect, useState } from "react";

import { useReplayStore } from "../store/replayStore";
import type { BeliefFrameView } from "../types/api";
import { BeliefPanel } from "./BeliefPanel";

async function fetchBeliefFrames(gameId: string): Promise<BeliefFrameView[]> {
  const res = await fetch(`/api/replays/${encodeURIComponent(gameId)}/beliefs`, {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    throw new Error(`belief frames request failed (status ${res.status})`);
  }
  return (await res.json()) as BeliefFrameView[];
}

export function BeliefMatrix() {
  const replay = useReplayStore((s) => s.currentReplay);
  const perspective = useReplayStore((s) => s.perspective);
  const beliefView = useReplayStore((s) => s.beliefView);
  const setBeliefView = useReplayStore((s) => s.setBeliefView);

  const [open, setOpen] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [frames, setFrames] = useState<BeliefFrameView[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const gameId = replay?.metadata.game_id ?? null;

  // Reset the cached frames whenever the replay changes, so an open panel can't
  // show the previous game's beliefs for a frame.
  useEffect(() => {
    setFrames(null);
    setError(null);
  }, [gameId]);

  // Fetch the per-meeting frames lazily — only once the hero is opened. The
  // cancellation + game-id guard mirrors the store's async-ordering discipline so
  // a stale response can't land after the replay switches.
  useEffect(() => {
    if (!open || gameId === null) {
      return;
    }
    let cancelled = false;
    setError(null);
    fetchBeliefFrames(gameId)
      .then((data) => {
        if (!cancelled) {
          setFrames(data);
        }
      })
      .catch((cause: unknown) => {
        if (!cancelled) {
          setError(cause instanceof Error ? cause.message : String(cause));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [open, gameId]);

  // Close the overlay on Escape (consistent with the MeetingView modal).
  useEffect(() => {
    if (!open) {
      return;
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  if (replay === null) {
    return null;
  }

  // Firewall: the Belief × Truth matrix is an OMNISCIENT cross-agent overview — it
  // aggregates EVERY observer's private belief state. Showing it in As-agent fog
  // would leak suspicions the chosen agent never had, so the whole hero (launcher
  // included) is hidden in fog; the per-agent belief view belongs to the mind
  // inspector. (Hooks above always run; this gate is after them.)
  if (perspective.mode === "agent") {
    return null;
  }

  const meetingCount = replay.metadata.meeting_count;

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => {
          setOpen(true);
        }}
        aria-label="Open the Belief × Truth matrix"
        title="Belief × Truth — who suspects whom, vs ground truth"
        className="fixed right-4 top-1/2 z-[60] flex -translate-y-1/2 items-center gap-2 rounded-md border-2 border-ink-900 bg-paper-0 px-3 py-2 text-sm font-semibold text-ink-900 shadow-chrome-1 transition-colors hover:bg-paper-2"
      >
        <span aria-hidden className="font-mono text-base leading-none">⊞</span>
        Belief × Truth
        <span className="rounded-pill bg-paper-2 px-1.5 font-mono text-[10px] text-ink-500">
          {meetingCount} mtg
        </span>
      </button>
    );
  }

  // Roster order matches the loader's `sorted(...)` so the matrix axes are stable.
  const players = [...replay.players].sort((a, b) => a.agent_id.localeCompare(b.agent_id));

  // Per-meeting liveness from the replay tick state — the /beliefs DTO snapshots
  // dead players as observers too, so the panel can't infer liveness from rows
  // (Codex review). For each frame's meeting tick, the agents alive at that tick;
  // BeliefPanel freezes anyone absent here.
  const aliveByMeeting: Record<string, string[]> = {};
  for (const frame of frames ?? []) {
    const tickFrame = replay.ticks.find((t) => t.tick === frame.tick);
    if (tickFrame !== undefined) {
      aliveByMeeting[frame.meeting_id] = tickFrame.agent_states
        .filter((s) => s.is_alive)
        .map((s) => s.agent_id);
    }
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Belief × Truth matrix"
      className="fixed inset-0 z-[80] flex items-center justify-center overflow-auto bg-ink-900/50 p-4"
      onClick={() => {
        setOpen(false);
      }}
    >
      {/* Stop backdrop clicks from closing when interacting with the panel. */}
      <div onClick={(event) => event.stopPropagation()} className="contents">
        <BeliefPanel
          players={players}
          frames={frames ?? []}
          layer={beliefView}
          onLayerChange={setBeliefView}
          omniscient
          aliveByMeeting={aliveByMeeting}
          loading={frames === null && error === null}
          error={error}
          onClose={() => {
            setOpen(false);
          }}
          isFullscreen={fullscreen}
          onToggleFullscreen={() => {
            setFullscreen((value) => !value);
          }}
        />
      </div>
    </div>
  );
}
