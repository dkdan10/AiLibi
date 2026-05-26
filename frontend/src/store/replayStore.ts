// The single Zustand store every Phase 4 component consumes (DESIGN.md §7).
// The state + actions shape below is the contract frozen at Task 4.3; adding a
// field after this merges requires a follow-up task touching all consumers
// (4.4, 4.4.5, 4.5, 4.6, 4.7, 4.8).

import { create } from "zustand";

import * as api from "../api/client";
import type {
  AgentMemoryView,
  ReplayMetadataView,
  ReplayView,
} from "../types/api";

export type PlaybackSpeed = 0.5 | 1 | 2 | 4;

export interface ReplayStoreState {
  // Available replays (loaded once via /replays on app mount).
  replayList: ReplayMetadataView[] | null;
  replayListError: string | null;

  // Currently-selected replay.
  currentReplay: ReplayView | null;
  currentReplayError: string | null;

  // Playback state.
  currentTick: number;
  isPlaying: boolean;
  playbackSpeed: PlaybackSpeed;

  // Selected meeting (for MeetingView overlay).
  selectedMeetingId: string | null;

  // Selected agent (for ThoughtStream).
  selectedAgentId: string | null;

  // Memory cache (sparse — only meeting-boundary snapshots),
  // keyed by `${meetingId}:${agentId}`.
  memoryCache: Record<string, AgentMemoryView>;
}

export interface ReplayStoreActions {
  loadReplayList(): Promise<void>;
  selectReplay(gameId: string): Promise<void>;
  setCurrentTick(tick: number): void;
  setIsPlaying(playing: boolean): void;
  setPlaybackSpeed(speed: PlaybackSpeed): void;
  selectMeeting(meetingId: string | null): void;
  selectAgent(agentId: string | null): void;
  fetchMemoryView(meetingId: string, agentId: string): Promise<void>;
  clearError(): void;
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function memoryKey(meetingId: string, agentId: string): string {
  return `${meetingId}:${agentId}`;
}

// Monotonic tokens guarding async actions against out-of-order responses: when
// a newer call starts before an older request resolves, the stale older
// completion is dropped so it can't clobber newer state. selectReplay and
// loadReplayList each keep a "newest call wins" token; fetchMemoryView instead
// compares the in-flight game id to the current selection after the await, so
// keyed cache writes for distinct meetings/agents on one replay still coexist.
let latestReplayRequest = 0;
let latestReplayListRequest = 0;

export const useReplayStore = create<ReplayStoreState & ReplayStoreActions>(
  (set, get) => ({
    replayList: null,
    replayListError: null,
    currentReplay: null,
    currentReplayError: null,
    currentTick: 0,
    isPlaying: false,
    playbackSpeed: 1,
    selectedMeetingId: null,
    selectedAgentId: null,
    memoryCache: {},

    async loadReplayList() {
      const requestToken = ++latestReplayListRequest;
      try {
        const list = await api.listReplays();
        if (requestToken !== latestReplayListRequest) {
          return;
        }
        set({ replayList: list, replayListError: null });
      } catch (error) {
        if (requestToken !== latestReplayListRequest) {
          return;
        }
        set({ replayList: null, replayListError: errorMessage(error) });
      }
    },

    async selectReplay(gameId) {
      const requestToken = ++latestReplayRequest;
      try {
        const replay = await api.getReplay(gameId);
        if (requestToken !== latestReplayRequest) {
          return;
        }
        set({
          currentReplay: replay,
          currentReplayError: null,
          currentTick: 0,
          isPlaying: false,
          selectedMeetingId: null,
          selectedAgentId: null,
          memoryCache: {},
        });
      } catch (error) {
        if (requestToken !== latestReplayRequest) {
          return;
        }
        set({ currentReplay: null, currentReplayError: errorMessage(error) });
      }
    },

    setCurrentTick(tick) {
      set({ currentTick: tick });
    },

    setIsPlaying(playing) {
      set({ isPlaying: playing });
    },

    setPlaybackSpeed(speed) {
      set({ playbackSpeed: speed });
    },

    selectMeeting(meetingId) {
      set({ selectedMeetingId: meetingId });
    },

    selectAgent(agentId) {
      set({ selectedAgentId: agentId });
    },

    async fetchMemoryView(meetingId, agentId) {
      const key = memoryKey(meetingId, agentId);
      if (get().memoryCache[key] !== undefined) {
        return;
      }
      const replay = get().currentReplay;
      if (replay === null) {
        return;
      }
      const gameId = replay.metadata.game_id;
      try {
        const memory = await api.getMemory(gameId, meetingId, agentId);
        // Drop the result if the selected replay changed while in flight, so a
        // stale snapshot can't land in (and become a cache hit for) another
        // replay's memoryCache.
        if (get().currentReplay?.metadata.game_id !== gameId) {
          return;
        }
        set((state) => ({
          memoryCache: { ...state.memoryCache, [key]: memory },
        }));
      } catch (error) {
        // Likewise, don't surface an error for a replay no longer selected.
        if (get().currentReplay?.metadata.game_id !== gameId) {
          return;
        }
        set({ currentReplayError: errorMessage(error) });
      }
    },

    clearError() {
      set({ replayListError: null, currentReplayError: null });
    },
  }),
);
