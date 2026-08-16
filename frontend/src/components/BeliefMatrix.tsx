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
// Data path note (scope): the store is NOT in this task's scope, so the
// BeliefFrameView[] is fetched here directly (with the store's in-flight-replay
// guard mirrored) rather than via a new store action — the shape is exactly the
// served DTO, so a later store-backed fetch is a drop-in swap. The URL, however,
// is NOT hand-built: it goes through `api/client`'s `apiUrl` seam (Task 19.13) so
// this panel follows the same data source as every other call — the live API in a
// normal build, the pre-baked JSON in the static demo bundle.

import { useEffect, useRef, useState } from "react";

import { apiUrl, pathSegment } from "../api/client";
import { useReplayStore } from "../store/replayStore";
import { useFocusTrap } from "../hooks/useFocusTrap";
import type { BeliefFrameView } from "../types/api";
import { BeliefPanel } from "./BeliefPanel";

async function fetchBeliefFrames(
  gameId: string,
  set: string | null,
): Promise<BeliefFrameView[]> {
  // Thread the active set (Task 12.12): both committed sets reuse headless-seed-*
  // ids, so omitting the set would fall back to the default — 9p2i since Task
  // 19.9 flipped it off the 4p1i fixture — and show the wrong set's belief frames
  // (or an empty state) against, e.g., a 4p1i replay.
  const url = apiUrl(`/replays/${pathSegment(gameId)}/beliefs`, set);
  const res = await fetch(url, {
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
  const seedSet = useReplayStore((s) => s.seedSet);
  const selectedMeetingId = useReplayStore((s) => s.selectedMeetingId);
  // Open-state is store-owned (Task 12.13) so the launcher can sit in chrome
  // (the perspective banner), off the map's room cells; this component owns only
  // the opened panel + the lazy frame fetch.
  const open = useReplayStore((s) => s.beliefOpen);
  const setOpen = useReplayStore((s) => s.setBeliefOpen);

  const [fullscreen, setFullscreen] = useState(false);
  const dialogRef = useRef<HTMLDivElement>(null);
  const [frames, setFrames] = useState<BeliefFrameView[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const gameId = replay?.metadata.game_id ?? null;

  // Reset the cached frames whenever the replay OR the active set changes, so an
  // open panel can't show the previous game/set's beliefs for a frame.
  useEffect(() => {
    setFrames(null);
    setError(null);
  }, [gameId, seedSet]);

  // Fetch the per-meeting frames lazily — only once the hero is opened. The
  // cancellation + game-id/set guard mirrors the store's async-ordering discipline
  // so a stale response can't land after the replay or set switches.
  useEffect(() => {
    if (!open || gameId === null) {
      return;
    }
    let cancelled = false;
    setError(null);
    fetchBeliefFrames(gameId, seedSet)
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
  }, [open, gameId, seedSet]);

  // Close the overlay on Escape (consistent with the MeetingView modal).
  useEffect(() => {
    if (!open) {
      return;
    }
    const onKeyDown = (event: KeyboardEvent) => {
      // Yield Escape to the guided tour when it is open over the matrix.
      if (event.key === "Escape" && !useReplayStore.getState().guidedTourOpen) {
        setOpen(false);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  // Trap focus inside the matrix dialog while open (aria-modal alone does not
  // constrain focus); focus restores on close. Mirrors the MeetingView dialog.
  useFocusTrap(dialogRef, open);

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

  // Task 12.11 overlay coordination: while a meeting is open the workspace is in
  // "meeting mode" — the masked MeetingView (z-50) + the mind rail (z-55) own the
  // screen. The Belief × Truth hero (opened, its z-[80] modal) would collide with
  // the rail and stack over the meeting, so it steps aside entirely; it is
  // reachable again the moment the meeting closes. (The launcher — re-anchored
  // into the perspective banner in Task 12.13 — applies the same gate there.)
  if (selectedMeetingId !== null) {
    return null;
  }

  // The launcher now lives in the perspective banner (Task 12.13): off the map's
  // room cells, beside the Omniscient/As-agent toggle. When closed, the hero
  // renders nothing here — opening is driven by the banner's launcher.
  if (!open) {
    return null;
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
      ref={dialogRef}
      tabIndex={-1}
      role="dialog"
      aria-modal="true"
      aria-label="Belief × Truth matrix"
      className="fixed inset-0 z-[80] flex items-center justify-center overflow-auto bg-ink-900/50 p-4 outline-none"
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
