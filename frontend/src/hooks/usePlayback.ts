// The playback hook (Task 12.4; design/phase-12/stage-1-design.md §4). All
// playback STATE lives in `replayStore`; this file is where it becomes a usable
// transport. Two exports:
//
//   • `usePlayback()` — derived read-state + stable seek/jump action callbacks.
//     Pure (no effects), so it is safe to call from any number of components
//     (the transport, the advantage scrubber, the timeline). Every seek is
//     expressed in ENGINE TICK NUMBERS and resolved to the store's array index
//     via the one `lib/playback` mapping — never an ad-hoc re-derivation.
//
//   • `usePlaybackEngine()` — the side-effecting driver: the auto-advance timer
//     (lifted out of `ReplayControls` per the DoD), interruptible auto-follow,
//     and the debounced `history.replaceState` URL sync. Mount it EXACTLY ONCE
//     (a single hidden node in the shell) so there is one timer, not one per
//     consumer.

import { useCallback, useEffect, useRef } from "react";

import {
  type BeliefViewMode,
  type Perspective,
  type ViewId,
  eventTickNumbers,
  frameIndexForTick,
  keyMomentTicks,
  meetingTickNumbers,
  nextAfter,
  parsePlaybackParams,
  prevBefore,
  serializePlaybackParams,
  START_TICK,
  tickNumberAt,
} from "../lib/playback";
import { useReplayStore } from "../store/replayStore";
import type { PlaybackSpeed } from "../store/replayStore";
import type { MeetingView, TickView } from "../types/api";

// The base auto-advance cadence; effective interval is BASE / speed (ported
// verbatim from the old ReplayControls timer).
const BASE_TICK_INTERVAL_MS = 500;

// Debounce the URL write so scrubbing does not thrash `history` (DESIGN.md §4).
const URL_DEBOUNCE_MS = 250;

// The query keys this transport owns (mirrors `serializePlaybackParams`). They
// are listed so the write-back can clear+rewrite ONLY its own keys and PRESERVE
// foreign ones — chiefly the Highlights filter keys (winner / winShape /
// scoreBucket / hasEjection) that Task 12.9 round-trips through the same URL.
// Without this, rebuilding the query string from scratch each write would drop
// those keys, breaking the reel's shareable / reload-stable contract.
const PLAYBACK_OWNED_PARAM_KEYS = [
  "set",
  "game_id",
  "tick",
  "perspective",
  "beliefView",
  "selectedAgent",
  "selectedMeeting",
  "view",
] as const;

// Merge the transport's own serialized keys onto the LIVE query string (read at
// write time), preserving any foreign keys. Returns a `?…` string, or "" if empty.
function mergePlaybackSearch(ownedSearch: string): string {
  const merged = new URLSearchParams(window.location.search);
  for (const key of PLAYBACK_OWNED_PARAM_KEYS) {
    merged.delete(key);
  }
  for (const [key, value] of new URLSearchParams(ownedSearch)) {
    merged.set(key, value);
  }
  const query = merged.toString();
  return query === "" ? "" : `?${query}`;
}

const EMPTY_TICKS: readonly TickView[] = [];
const EMPTY_MEETINGS: readonly MeetingView[] = [];

export interface Playback {
  /** Whether a replay is loaded (the transport disables itself otherwise). */
  readonly hasReplay: boolean;
  /** Array index into `currentReplay.ticks` (the store's playback position). */
  readonly frameIndex: number;
  /** Engine tick number at the current frame (-1 = the pre-game Start frame). */
  readonly tickNumber: number;
  /** Engine tick of the first frame (the Start frame, normally -1). */
  readonly firstTickNumber: number;
  /** Engine tick of the last frame. */
  readonly lastTickNumber: number;
  /** Last valid array index (0 when empty). */
  readonly lastIndex: number;
  /** The current frame's view-model, or `null` when no replay is loaded. */
  readonly frame: TickView | null;
  /** The meeting at the current tick, if any (the stage morphs here). */
  readonly meetingAtTick: MeetingView | null;
  readonly isPlaying: boolean;
  readonly speed: PlaybackSpeed;
  readonly isAtStart: boolean;
  readonly isAtEnd: boolean;
  readonly canStepBack: boolean;
  readonly canStepForward: boolean;

  // Actions (all stable across renders).
  play(): void;
  pause(): void;
  togglePlay(): void;
  setSpeed(speed: PlaybackSpeed): void;
  /** Seek by raw array index (the scrubber); clamped into range. */
  seekToIndex(index: number): void;
  /** Seek to an ENGINE TICK NUMBER; resolves to the nearest frame at/before it. */
  seekToTick(tickNumber: number): void;
  /** Step by ±N frames. */
  stepBy(delta: number): void;
  /** Jump to the prev/next jump-event tick (kill/meeting/vent/sabotage). */
  jumpToEvent(direction: 1 | -1): void;
  /** Jump to the prev/next meeting and select it. */
  jumpToMeeting(direction: 1 | -1): void;
  /** Seek to the next key-moment inflection (kill/meeting/ejection/sabotage). */
  nextKeyMoment(): void;
}

/** Read-state + stable actions. Pure — call it anywhere, any number of times. */
export function usePlayback(): Playback {
  const replay = useReplayStore((s) => s.currentReplay);
  const frameIndex = useReplayStore((s) => s.currentTick);
  const isPlaying = useReplayStore((s) => s.isPlaying);
  const speed = useReplayStore((s) => s.playbackSpeed);

  const ticks = replay?.ticks ?? EMPTY_TICKS;
  const meetings = replay?.meetings ?? EMPTY_MEETINGS;
  const lastIndex = Math.max(0, ticks.length - 1);
  const tickNumber = tickNumberAt(ticks, frameIndex);
  const firstTickNumber = tickNumberAt(ticks, 0);
  const lastTickNumber = tickNumberAt(ticks, lastIndex);
  const frame = ticks.length === 0 ? null : (ticks[Math.min(frameIndex, lastIndex)] ?? null);
  const meetingAtTick = meetings.find((m) => m.tick === tickNumber) ?? null;

  // Actions read fresh state via `getState()` and call only stable store
  // setters + pure `lib/playback` helpers, so they never need to change identity
  // — consumers can list them in effect deps without churn.
  const seekToIndex = useCallback((index: number) => {
    const store = useReplayStore.getState();
    const current = store.currentReplay;
    if (current === null) {
      return;
    }
    const max = current.ticks.length - 1;
    if (max < 0) {
      return;
    }
    store.setCurrentTick(Math.max(0, Math.min(index, max)));
  }, []);

  const seekToTick = useCallback(
    (target: number) => {
      const current = useReplayStore.getState().currentReplay;
      if (current === null) {
        return;
      }
      seekToIndex(frameIndexForTick(current.ticks, target));
    },
    [seekToIndex],
  );

  const stepBy = useCallback(
    (delta: number) => {
      seekToIndex(useReplayStore.getState().currentTick + delta);
    },
    [seekToIndex],
  );

  const play = useCallback(() => {
    useReplayStore.getState().setIsPlaying(true);
  }, []);

  const pause = useCallback(() => {
    useReplayStore.getState().setIsPlaying(false);
  }, []);

  const togglePlay = useCallback(() => {
    const store = useReplayStore.getState();
    store.setIsPlaying(!store.isPlaying);
  }, []);

  const setSpeed = useCallback((next: PlaybackSpeed) => {
    useReplayStore.getState().setPlaybackSpeed(next);
  }, []);

  const jumpToEvent = useCallback(
    (direction: 1 | -1) => {
      const current = useReplayStore.getState().currentReplay;
      if (current === null) {
        return;
      }
      const here = tickNumberAt(current.ticks, useReplayStore.getState().currentTick);
      const events = eventTickNumbers(current.ticks);
      const target = direction === 1 ? nextAfter(events, here) : prevBefore(events, here);
      if (target !== null) {
        seekToTick(target);
      }
    },
    [seekToTick],
  );

  const jumpToMeeting = useCallback(
    (direction: 1 | -1) => {
      const current = useReplayStore.getState().currentReplay;
      if (current === null) {
        return;
      }
      const here = tickNumberAt(current.ticks, useReplayStore.getState().currentTick);
      const meetingTicks = meetingTickNumbers(current.meetings);
      const target =
        direction === 1 ? nextAfter(meetingTicks, here) : prevBefore(meetingTicks, here);
      if (target === null) {
        return;
      }
      seekToTick(target);
      // Explicit user intent to view that meeting: select it directly (auto-
      // follow would also catch it, but jumping should never miss the open).
      const meeting = current.meetings.find((m) => m.tick === target);
      if (meeting !== undefined) {
        useReplayStore.getState().selectMeeting(meeting.meeting_id);
      }
    },
    [seekToTick],
  );

  const nextKeyMoment = useCallback(() => {
    const current = useReplayStore.getState().currentReplay;
    if (current === null) {
      return;
    }
    const here = tickNumberAt(current.ticks, useReplayStore.getState().currentTick);
    const target = nextAfter(keyMomentTicks(current.ticks, current.meetings), here);
    if (target !== null) {
      seekToTick(target);
    }
  }, [seekToTick]);

  return {
    hasReplay: replay !== null,
    frameIndex,
    tickNumber,
    firstTickNumber,
    lastTickNumber,
    lastIndex,
    frame,
    meetingAtTick,
    isPlaying,
    speed,
    isAtStart: tickNumber === START_TICK,
    isAtEnd: frameIndex >= lastIndex,
    canStepBack: frameIndex > 0,
    canStepForward: frameIndex < lastIndex,
    play,
    pause,
    togglePlay,
    setSpeed,
    seekToIndex,
    seekToTick,
    stepBy,
    jumpToEvent,
    jumpToMeeting,
    nextKeyMoment,
  };
}

// Deferred URL state the hydration path applies AFTER the replay loads (because
// `selectReplay` resets the replay-scoped fields).
interface PendingHydration {
  readonly gameId: string;
  readonly tick: number | null;
  readonly perspective: Perspective;
  readonly beliefView: BeliefViewMode;
  readonly selectedAgent: string | null;
  readonly selectedMeeting: string | null;
  // selectReplay forces view=workspace, so the parsed top-level view is restored
  // here too — otherwise a shared `game_id=…&view=tournament` URL would snap back
  // to the workspace on reload.
  readonly view: ViewId | null;
}

/**
 * The single side-effecting playback driver. Mount once. Owns:
 *  1. the auto-advance timer (lifted out of ReplayControls),
 *  2. interruptible auto-follow (select the meeting on entering its tick),
 *  3. URL hydration on mount + debounced `replaceState` write-back.
 */
export function usePlaybackEngine(): void {
  const replay = useReplayStore((s) => s.currentReplay);
  const isPlaying = useReplayStore((s) => s.isPlaying);
  const speed = useReplayStore((s) => s.playbackSpeed);
  const frameIndex = useReplayStore((s) => s.currentTick);
  const autoFollow = useReplayStore((s) => s.autoFollow);
  const seedSet = useReplayStore((s) => s.seedSet);
  const view = useReplayStore((s) => s.view);
  const perspective = useReplayStore((s) => s.perspective);
  const beliefView = useReplayStore((s) => s.beliefView);
  const selectedAgentId = useReplayStore((s) => s.selectedAgentId);
  const selectedMeetingId = useReplayStore((s) => s.selectedMeetingId);
  const currentReplayError = useReplayStore((s) => s.currentReplayError);

  // ── 1. Auto-advance timer ───────────────────────────────────────────────
  // `currentTick` is read fresh inside the interval (not closed over) so the
  // effect needn't depend on it — depending on it would tear down + re-register
  // the interval every tick, compounding drift (the original ReplayControls
  // note). Stepping is frame-based (index + 1) and stops at the last frame.
  // Gated on the workspace view: off it (Replays/Highlights/Tournament) the
  // transport is unmounted, so — like the old ReplayControls-owned timer that
  // unmounted with the replay tab — playback freezes rather than silently
  // advancing the tick/URL in the background, and resumes on returning.
  useEffect(() => {
    if (!isPlaying || replay === null || view !== "workspace") {
      return;
    }
    const intervalMs = BASE_TICK_INTERVAL_MS / speed;
    const lastIndex = replay.ticks.length - 1;
    const id = window.setInterval(() => {
      const store = useReplayStore.getState();
      const next = store.currentTick + 1;
      if (next > lastIndex) {
        store.setIsPlaying(false);
      } else {
        store.setCurrentTick(next);
      }
    }, intervalMs);
    return () => {
      window.clearInterval(id);
    };
  }, [isPlaying, speed, replay, view]);

  // ── 2. Interruptible auto-follow ─────────────────────────────────────────
  // While ON, the meeting selection TRACKS the current tick — select the meeting
  // when its tick is reached, and CLEAR it on leaving the span so the stage
  // morphs back to the map (DESIGN.md §4: show the meeting only while
  // tick ∈ meeting.span). Two refs keep it from yanking the user:
  //   • lastFollowedTickRef fires the logic once per tick change, so a manual
  //     dismissal at a meeting tick sticks until playback moves.
  //   • autoSelectedRef remembers the meeting auto-follow ITSELF opened, so on
  //     leaving we clear only that — never a user- or URL-restored selection.
  const lastFollowedTickRef = useRef<number | null>(null);
  const autoSelectedRef = useRef<string | null>(null);
  useEffect(() => {
    if (replay === null) {
      lastFollowedTickRef.current = null;
      autoSelectedRef.current = null;
      return;
    }
    const tickNumber = tickNumberAt(replay.ticks, frameIndex);
    if (lastFollowedTickRef.current === tickNumber) {
      return; // already handled this tick; respect a manual dismissal
    }
    lastFollowedTickRef.current = tickNumber;
    if (!autoFollow) {
      return;
    }
    const store = useReplayStore.getState();
    const meeting = replay.meetings.find((m) => m.tick === tickNumber) ?? null;
    if (meeting !== null) {
      // Entered a meeting span. Claim ownership ONLY when auto-follow itself
      // opens it: if the user (jumpToMeeting) or the URL already selected this
      // meeting, leave autoSelectedRef clear so we never auto-close a selection
      // the user explicitly made when they step / resume past the tick.
      if (store.selectedMeetingId !== meeting.meeting_id) {
        store.selectMeeting(meeting.meeting_id);
        autoSelectedRef.current = meeting.meeting_id;
      } else {
        autoSelectedRef.current = null;
      }
    } else if (
      autoSelectedRef.current !== null &&
      store.selectedMeetingId === autoSelectedRef.current
    ) {
      // Left the span and the open meeting is the one we opened: morph back.
      store.selectMeeting(null);
      autoSelectedRef.current = null;
    } else {
      // The selection is the user's / URL's (or already changed): leave it.
      autoSelectedRef.current = null;
    }
  }, [replay, frameIndex, autoFollow]);

  // ── 3a. URL hydration (once on mount) ────────────────────────────────────
  const hydratedRef = useRef(false);
  const pendingRef = useRef<PendingHydration | null>(null);
  useEffect(() => {
    if (hydratedRef.current) {
      return;
    }
    hydratedRef.current = true;
    const parsed = parsePlaybackParams(window.location.search);
    const store = useReplayStore.getState();
    if (parsed.set !== null) {
      store.setSeedSet(parsed.set);
    }
    store.setBeliefView(parsed.beliefView);
    if (parsed.view !== null) {
      store.setView(parsed.view);
    }
    if (parsed.gameId !== null) {
      // selectReplay resets perspective/tick/selection, so defer the rest of the
      // shared moment until the matching replay has loaded (effect 3b).
      pendingRef.current = {
        gameId: parsed.gameId,
        tick: parsed.tick,
        perspective: parsed.perspective,
        beliefView: parsed.beliefView,
        selectedAgent: parsed.selectedAgent,
        selectedMeeting: parsed.selectedMeeting,
        view: parsed.view,
      };
      void store.selectReplay(parsed.gameId);
    } else {
      store.setPerspective(parsed.perspective);
    }
  }, []);

  // ── 3b. Apply deferred moment once the URL's replay is loaded ─────────────
  // Also drop the pending hydration if the deep-linked replay can never arrive —
  // a load error (e.g. a 404 game_id) or a different replay superseding it —
  // otherwise `pendingRef` would stay set and effect 3c's guard would disable
  // URL sync for the rest of the session.
  useEffect(() => {
    const pending = pendingRef.current;
    if (pending === null) {
      return;
    }
    if (replay === null) {
      // Still loading keeps pending; a surfaced load error clears it.
      if (currentReplayError !== null) {
        pendingRef.current = null;
      }
      return;
    }
    if (replay.metadata.game_id !== pending.gameId) {
      // A different replay superseded the deep-linked one: discard the stale
      // moment so write-back resumes for the replay that actually loaded.
      pendingRef.current = null;
      return;
    }
    const store = useReplayStore.getState();
    store.setPerspective(pending.perspective);
    store.setBeliefView(pending.beliefView);
    if (pending.tick !== null) {
      store.setCurrentTick(frameIndexForTick(replay.ticks, pending.tick));
    }
    if (pending.selectedMeeting !== null) {
      store.selectMeeting(pending.selectedMeeting);
    }
    if (pending.selectedAgent !== null) {
      store.selectAgent(pending.selectedAgent);
    }
    // Restore the parsed top-level view AFTER selectReplay's workspace default,
    // so a shared non-workspace view round-trips even with a replay loaded.
    if (pending.view !== null) {
      store.setView(pending.view);
    }
    pendingRef.current = null;
  }, [replay, currentReplayError]);

  // ── 3c. Debounced URL write-back ─────────────────────────────────────────
  // Skip until initial hydration completes, and while a deferred apply is still
  // pending, so we never clobber the URL's own tick before reading it back.
  useEffect(() => {
    if (!hydratedRef.current || pendingRef.current !== null) {
      return;
    }
    const handle = window.setTimeout(() => {
      const gameId = replay?.metadata.game_id ?? null;
      const tick = replay === null ? null : tickNumberAt(replay.ticks, frameIndex);
      const owned = serializePlaybackParams({
        set: seedSet,
        gameId,
        tick,
        perspective,
        beliefView,
        selectedAgent: selectedAgentId,
        selectedMeeting: selectedMeetingId,
        view,
      });
      // Preserve foreign keys (e.g. Task 12.9's Highlights filters) rather than
      // clobbering the whole query string with only the transport's keys.
      const search = mergePlaybackSearch(owned);
      const url = `${window.location.pathname}${search}${window.location.hash}`;
      window.history.replaceState(null, "", url);
    }, URL_DEBOUNCE_MS);
    return () => {
      window.clearTimeout(handle);
    };
  }, [
    replay,
    frameIndex,
    seedSet,
    view,
    perspective,
    beliefView,
    selectedAgentId,
    selectedMeetingId,
  ]);
}
