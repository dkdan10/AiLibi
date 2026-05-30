// The single Zustand store every Phase 4 component consumes (DESIGN.md §7).
// The state + actions shape below is the contract frozen at Task 4.3; adding a
// field after this merges requires a follow-up task touching all consumers
// (4.4, 4.4.5, 4.5, 4.6, 4.7, 4.8). Task 6.7 additively extends it with a lazy
// meeting cache to window the bulk payload (DESIGN.md §11.4); existing consumers
// are unaffected because none read the new field.

import { create } from "zustand";

import * as api from "../api/client";
import type {
  AgentMemoryView,
  MeetingView,
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

  // Meeting cache (Task 6.7 windowing): full meeting transcripts — including the
  // LLM prompt/response bodies stripped from the bulk payload — fetched lazily
  // on demand (e.g. when an LLMCallCard is expanded), keyed by meeting id.
  meetingCache: Record<string, MeetingView>;
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
  fetchMeeting(meetingId: string): Promise<void>;
  clearError(): void;
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function memoryKey(meetingId: string, agentId: string): string {
  return `${meetingId}:${agentId}`;
}

// Window the bulk replay payload (Task 6.7; audit K-K-1 / G-G-5, DESIGN.md
// §11.4). The per-call LLM prompt/response bodies are the only part of the
// payload that grows with game length — each prompt embeds the full rendered
// memory — so they are stripped from the bulk ReplayView held in the store and
// lazy-fetched per meeting on demand (see `fetchMeeting` + `LLMCallCard`).
// Everything the synchronous consumers read — the tick timeline, roster, map,
// and the (meeting-count-bounded) transcript structure — is retained verbatim,
// so no out-of-scope consumer regresses and the DTO shape is unchanged.
function windowReplay(replay: ReplayView): ReplayView {
  return {
    ...replay,
    meetings: replay.meetings.map((meeting) => ({
      ...meeting,
      llm_calls: meeting.llm_calls.map((call) => ({
        ...call,
        prompt_text: "",
        response_text: "",
      })),
    })),
  };
}

export const useReplayStore = create<ReplayStoreState & ReplayStoreActions>(
  (set, get) => {
    // Monotonic tokens guarding async actions against out-of-order responses,
    // scoped to this store instance (closure-owned, not module-level) so
    // request ordering is isolated per store. When a newer call starts before
    // an older request resolves, the stale completion is dropped so it can't
    // clobber newer state. selectReplay and loadReplayList each use a "newest
    // call wins" token; fetchMemoryView instead compares the in-flight game id
    // to the current selection after the await, so keyed cache writes for
    // distinct meetings/agents on one replay still coexist.
    let latestReplayRequest = 0;
    let latestReplayListRequest = 0;

    return {
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
      meetingCache: {},

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
            currentReplay: windowReplay(replay),
            currentReplayError: null,
            currentTick: 0,
            isPlaying: false,
            selectedMeetingId: null,
            selectedAgentId: null,
            memoryCache: {},
            meetingCache: {},
          });
        } catch (error) {
          if (requestToken !== latestReplayRequest) {
            return;
          }
          // Reset all replay-scoped state too, so a failed selection can't
          // leave stale playback/selection context alongside a null replay.
          set({
            currentReplay: null,
            currentReplayError: errorMessage(error),
            currentTick: 0,
            isPlaying: false,
            selectedMeetingId: null,
            selectedAgentId: null,
            memoryCache: {},
            meetingCache: {},
          });
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
          // Drop the result if the selected replay changed while in flight, so
          // a stale snapshot can't land in (and become a cache hit for)
          // another replay's memoryCache.
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

      async fetchMeeting(meetingId) {
        // Lazy-load a full meeting transcript (with the LLM bodies windowed out
        // of the bulk payload) on demand, e.g. when an LLMCallCard is expanded.
        // Cached by meeting id, so the first expand in a meeting hydrates every
        // card in it. Mirrors fetchMemoryView's in-flight-game guard so a stale
        // response can't land in another replay's cache.
        if (get().meetingCache[meetingId] !== undefined) {
          return;
        }
        const replay = get().currentReplay;
        if (replay === null) {
          return;
        }
        const gameId = replay.metadata.game_id;
        try {
          const meeting = await api.getMeeting(gameId, meetingId);
          if (get().currentReplay?.metadata.game_id !== gameId) {
            return;
          }
          set((state) => ({
            meetingCache: { ...state.meetingCache, [meetingId]: meeting },
          }));
        } catch (error) {
          if (get().currentReplay?.metadata.game_id !== gameId) {
            return;
          }
          set({ currentReplayError: errorMessage(error) });
        }
      },

      clearError() {
        set({ replayListError: null, currentReplayError: null });
      },
    };
  },
);
