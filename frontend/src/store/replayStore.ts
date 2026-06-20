// The single Zustand store every Phase 4 component consumes (DESIGN.md §7).
// The state + actions shape below is the contract frozen at Task 4.3; adding a
// field after this merges requires a follow-up task touching all consumers
// (4.4, 4.4.5, 4.5, 4.6, 4.7, 4.8). Task 6.7 additively extends it with a lazy
// meeting cache to window the bulk payload (DESIGN.md §11.4); existing consumers
// are unaffected because none read the new field.
//
// Task 12.4 (design/phase-12/stage-1-design.md §4, §2.3) additively extends it
// again with the playback/shell backbone: the top-level `view`, the URL-synced
// `seedSet` / `perspective` / `beliefView`, the shared `hoverTick` crosshair, and
// `autoFollow`. `currentTick` stays the ARRAY INDEX into `currentReplay.ticks`
// (the frozen contract every existing consumer reads); the index↔engine-tick
// mapping lives once in `lib/playback.ts` and the `usePlayback` hook, so no
// existing consumer changes. The store keeps its async-ordering guards + payload
// windowing intact.

import { create } from "zustand";

import * as api from "../api/client";
import type {
  BeliefViewMode,
  Perspective,
  ViewId,
} from "../lib/playback";
import { OMNISCIENT } from "../lib/playback";
import type {
  AgentMemoryView,
  MeetingView,
  ReplayMetadataView,
  ReplayView,
} from "../types/api";

export type PlaybackSpeed = 0.5 | 1 | 2 | 4;

// Task 12.7: the claim↔map cross-highlight. A meeting TurnCard sets this on hover
// of a sighting ("saw p-5 in Reactor"); `MapView` reads it to light the claim's
// PUBLIC referent — the NAMED room + agent, which the transcript already states
// in the clear, so it is safe in any perspective. The highlight is strictly
// additive: the map lights this room ONLY when the current perspective already
// shows it (Omniscient, or lit under the selected agent's fog), so a hover never
// reveals a position the As-agent fog has hidden (the firewall / leak class).
export interface HighlightedSighting {
  // The agent named as seen ("saw <agentId> …"); matches `PlayerView.agent_id`.
  agentId: string;
  // The room named in the sighting (`SawPlayerView.room`). This is a model-authored
  // label, so its casing/spacing is not guaranteed canonical; `MapView`
  // normalises it to resolve the canonical `RoomView`.
  roomId: string;
}

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

  // Whether the Belief × Truth hero panel is open (Task 12.13). Held here — the
  // explicit shared-state object — so the launcher can be re-anchored into chrome
  // (a tab beside the perspective toggle, off the map's room cells) while the
  // panel itself lives in BeliefMatrix. Ephemeral UI state, not URL-synced.
  beliefOpen: boolean;

  // Memory cache (sparse — only meeting-boundary snapshots),
  // keyed by `${meetingId}:${agentId}`.
  memoryCache: Record<string, AgentMemoryView>;

  // Meeting cache (Task 6.7 windowing): full meeting transcripts — including the
  // LLM prompt/response bodies stripped from the bulk payload — fetched lazily
  // on demand (e.g. when an LLMCallCard is expanded), keyed by meeting id.
  meetingCache: Record<string, MeetingView>;

  // ── Task 12.4: playback / shell backbone (DESIGN.md §4, §2.3) ──────────────

  // Top-level view container (URL-synced; no router). Selecting a replay opens
  // the workspace; replays/highlights/tournament are the other top-level routes.
  view: ViewId;

  // The active replay set id (Task 12.12). URL-synced via `usePlayback` (the
  // `set` key ↔ this field); the set selector drives it through `setSeedSet`, and
  // the browser + dashboard re-fetch `/replays` + `/eval/*` for it. `null` =
  // unknown (before `/sets` resolves a default).
  seedSet: string | null;

  // The available recorded sets (`GET /sets`), populated on load; AUTO-GROWS as
  // new sets are recorded. The set selector renders from this list.
  availableSets: string[];
  availableSetsError: string | null;

  // Map perspective overlay (Omniscient ↔ As-agent fog). Consumed by 12.5; added
  // now so the URL + store contract is stable for the parallel chrome PRs. Never
  // encodes role/guilt — it is a view selector, not identity.
  perspective: Perspective;

  // Belief-panel data toggle (Belief / Ground-Truth / Error). Consumed by 12.6.
  beliefView: BeliefViewMode;

  // Shared crosshair: the ENGINE TICK under the cursor on the advantage graph /
  // event timeline, or `null` when not hovering. Ephemeral; drives the synced
  // crosshair across those two surfaces (DESIGN.md §4).
  hoverTick: number | null;

  // Auto-follow: while playing, follow the action (select the meeting when a
  // meeting tick is reached). Interruptible — a user override is respected (see
  // `usePlaybackEngine`). Exposed as a transport toggle.
  autoFollow: boolean;

  // Whether the first-run GuidedTour modal is open (Task 12.11). Held here — the
  // explicit shared-state object — rather than a module-level flag (AGENTS.md: no
  // module-level mutable state). The global keyboard transport reads it to
  // suppress its shortcuts while the tour owns the keyboard, and the meeting /
  // belief overlays read it to yield Escape to the tour.
  guidedTourOpen: boolean;

  // ── Task 12.7: meeting ↔ map cross-highlight (DESIGN.md §3.4, slice 5) ──────
  // The sighting under the cursor in the open meeting transcript, or `null`.
  // Ephemeral hover state (like `hoverTick`); drives the additive map highlight.
  highlightedSighting: HighlightedSighting | null;
}

export interface ReplayStoreActions {
  loadSets(): Promise<void>;
  loadReplayList(): Promise<void>;
  selectReplay(gameId: string): Promise<void>;
  setCurrentTick(tick: number): void;
  setIsPlaying(playing: boolean): void;
  setPlaybackSpeed(speed: PlaybackSpeed): void;
  selectMeeting(meetingId: string | null): void;
  selectAgent(agentId: string | null): void;
  setBeliefOpen(open: boolean): void;
  fetchMemoryView(meetingId: string, agentId: string): Promise<void>;
  fetchMeeting(meetingId: string): Promise<void>;
  clearError(): void;
  clearReplayLoadError(): void;

  // ── Task 12.4 actions ─────────────────────────────────────────────────────
  setView(view: ViewId): void;
  setSeedSet(seedSet: string | null): void;
  setPerspective(perspective: Perspective): void;
  setBeliefView(beliefView: BeliefViewMode): void;
  setHoverTick(tick: number | null): void;
  setAutoFollow(autoFollow: boolean): void;
  setGuidedTourOpen(open: boolean): void;

  // ── Task 12.7 action ───────────────────────────────────────────────────────
  setHighlightedSighting(sighting: HighlightedSighting | null): void;
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
    let latestSetsRequest = 0;

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
      beliefOpen: false,
      memoryCache: {},
      meetingCache: {},
      view: "replays",
      seedSet: null,
      availableSets: [],
      availableSetsError: null,
      perspective: OMNISCIENT,
      beliefView: "belief",
      hoverTick: null,
      autoFollow: true,
      guidedTourOpen: false,
      highlightedSighting: null,

      async loadSets() {
        // Fetch the available sets (Task 12.12) and, when no set is active yet
        // (no `set` URL key hydrated by usePlayback), adopt the server's default
        // so the selector shows a selection and every fetch is explicit. A set
        // already chosen (deep link / selector) is left untouched.
        const requestToken = ++latestSetsRequest;
        try {
          const { sets, default: defaultSet } = await api.getSets();
          if (requestToken !== latestSetsRequest) {
            return;
          }
          const current = get().seedSet;
          const next =
            current !== null && sets.includes(current) ? current : defaultSet;
          set({
            availableSets: sets,
            availableSetsError: null,
            seedSet: next,
          });
        } catch (error) {
          if (requestToken !== latestSetsRequest) {
            return;
          }
          set({ availableSetsError: errorMessage(error) });
        }
      },

      async loadReplayList() {
        const requestToken = ++latestReplayListRequest;
        // Read the active set at call time so a re-fetch after a set switch lists
        // the new set's replays (the caller re-invokes on seedSet change).
        const activeSet = get().seedSet ?? undefined;
        try {
          const list = await api.listReplays(activeSet);
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
        // Pin the set this selection is for (both sets share seed-based ids).
        // Changing the Set selector does NOT start a new selectReplay, so the
        // token alone wouldn't catch a mid-flight set switch — without this the
        // workspace could open the OLD set's replay under the new `seedSet`, and
        // its memory/meeting fetches would then use the new set (a mismatch). A
        // null activeSet is the UNRESOLVED case (a no-set deep link, before
        // `/sets` lands): it resolves to the server default, so null -> default is
        // not a switch and must not drop the deep-linked replay.
        const activeSet = get().seedSet;
        try {
          const replay = await api.getReplay(gameId, activeSet ?? undefined);
          if (
            requestToken !== latestReplayRequest ||
            (activeSet !== null && get().seedSet !== activeSet)
          ) {
            return;
          }
          // Selecting a replay opens the workspace (DESIGN.md §2.1). Reset the
          // replay-scoped overlays: perspective returns to Omniscient (a fresh
          // game has different agents) and the crosshair clears. `beliefView`,
          // `seedSet`, and `autoFollow` persist across replays (view modes, not
          // replay-scoped). The URL-hydration path re-applies any shared moment
          // AFTER this reset (see usePlaybackEngine), so a deep link still lands.
          set({
            currentReplay: windowReplay(replay),
            currentReplayError: null,
            currentTick: 0,
            isPlaying: false,
            selectedMeetingId: null,
            selectedAgentId: null,
            beliefOpen: false,
            memoryCache: {},
            meetingCache: {},
            view: "workspace",
            perspective: OMNISCIENT,
            hoverTick: null,
            highlightedSighting: null,
          });
        } catch (error) {
          if (requestToken !== latestReplayRequest) {
            return; // superseded by a newer selection
          }
          // A failed load carries no wrong-set DATA to leak, so the set-change
          // decision here is only about WHICH stale failures to surface:
          //   • LIVE switch away from a still-available set (the user picked
          //     another valid set mid-load): suppress — the user moved on, and the
          //     success branch likewise drops the analogous stale success.
          //   • STALE/normalized request set (a no-set deep link, or a ?set=old
          //     that loadSets normalized away — its set is null or no longer in
          //     availableSets): SURFACE it. That is what lets usePlayback's pending
          //     URL hydration clear (it keys off currentReplayError); dropping it
          //     silently would hang hydration forever (URL sync off, no replay).
          const setSwitchedToAvailable =
            activeSet !== null &&
            get().seedSet !== activeSet &&
            get().availableSets.includes(activeSet);
          if (setSwitchedToAvailable) {
            return;
          }
          // Reset all replay-scoped state too, so a failed selection can't
          // leave stale playback/selection context alongside a null replay; drop
          // back to the browser so the picker + error are visible.
          set({
            currentReplay: null,
            currentReplayError: errorMessage(error),
            currentTick: 0,
            isPlaying: false,
            selectedMeetingId: null,
            selectedAgentId: null,
            beliefOpen: false,
            memoryCache: {},
            meetingCache: {},
            view: "replays",
            perspective: OMNISCIENT,
            hoverTick: null,
            highlightedSighting: null,
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

      setBeliefOpen(open) {
        set({ beliefOpen: open });
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
        // Capture the SET too: the committed sets share seed-based game_ids, so a
        // game_id-only guard would let a slow fetch from the previous set land in
        // the new set's cache after a live set switch (Task 12.12) — compare both.
        const activeSet = get().seedSet;
        try {
          const memory = await api.getMemory(
            gameId,
            meetingId,
            agentId,
            activeSet ?? undefined,
          );
          // Drop the result if the selected replay OR the active set changed while
          // in flight, so a stale snapshot can't land in (and become a cache hit
          // for) another replay/set's memoryCache.
          if (
            get().currentReplay?.metadata.game_id !== gameId ||
            (activeSet !== null && get().seedSet !== activeSet)
          ) {
            return;
          }
          set((state) => ({
            memoryCache: { ...state.memoryCache, [key]: memory },
          }));
        } catch (error) {
          // Likewise, don't surface an error for a replay/set no longer selected.
          if (
            get().currentReplay?.metadata.game_id !== gameId ||
            (activeSet !== null && get().seedSet !== activeSet)
          ) {
            return;
          }
          set({ currentReplayError: errorMessage(error) });
        }
      },

      async fetchMeeting(meetingId) {
        // Lazy-load a full meeting transcript (with the LLM bodies windowed out
        // of the bulk payload) on demand, e.g. when an LLMCallCard is expanded.
        // Cached by meeting id, so the first expand in a meeting hydrates every
        // card in it. Mirrors fetchMemoryView's in-flight-game+set guard so a
        // stale response can't land in another replay/set's cache.
        if (get().meetingCache[meetingId] !== undefined) {
          return;
        }
        const replay = get().currentReplay;
        if (replay === null) {
          return;
        }
        const gameId = replay.metadata.game_id;
        // Capture the SET too (committed sets share seed-based game_ids; see
        // fetchMemoryView), and compare both on completion.
        const activeSet = get().seedSet;
        try {
          const meeting = await api.getMeeting(
            gameId,
            meetingId,
            activeSet ?? undefined,
          );
          if (
            get().currentReplay?.metadata.game_id !== gameId ||
            (activeSet !== null && get().seedSet !== activeSet)
          ) {
            return;
          }
          set((state) => ({
            meetingCache: { ...state.meetingCache, [meetingId]: meeting },
          }));
        } catch (error) {
          if (
            get().currentReplay?.metadata.game_id !== gameId ||
            (activeSet !== null && get().seedSet !== activeSet)
          ) {
            return;
          }
          set({ currentReplayError: errorMessage(error) });
        }
      },

      clearError() {
        set({ replayListError: null, currentReplayError: null });
      },

      // Clear ONLY the replay-LOAD error (a failed selectReplay). The dismiss on
      // that banner must not also wipe replayListError — doing so would drop a
      // live /replays failure back into a permanent loading spinner with no retry
      // (Task 12.13 review).
      clearReplayLoadError() {
        set({ currentReplayError: null });
      },

      setView(view) {
        set({ view });
      },

      setSeedSet(seedSet) {
        set({ seedSet });
      },

      setPerspective(perspective) {
        set({ perspective });
      },

      setBeliefView(beliefView) {
        set({ beliefView });
      },

      setHoverTick(tick) {
        set({ hoverTick: tick });
      },

      setAutoFollow(autoFollow) {
        set({ autoFollow });
      },

      setGuidedTourOpen(open) {
        set({ guidedTourOpen: open });
      },

      setHighlightedSighting(sighting) {
        set({ highlightedSighting: sighting });
      },
    };
  },
);
