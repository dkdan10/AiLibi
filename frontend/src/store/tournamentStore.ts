// Sibling Zustand store for the Tournament Dashboard view (Task 5.7,
// DESIGN.md §11.3). Deliberately NOT an extension of `useReplayStore`: the
// Phase 4 replay store is frozen (adding a field there forces a follow-up
// touching every Phase 4 consumer), and the dashboard's state is independent —
// one fetched report, no playback. Keeping it separate bounds the blast radius
// of this task to the dashboard. This store must never import or mutate
// `useReplayStore`.

import { create } from "zustand";

import * as api from "../api/client";
import type { TournamentEvalReport } from "../types/api";

export interface TournamentStoreState {
  // The latest tournament eval report (loaded via /eval/tournament-report).
  // `null` until a successful load; a failed/absent (404) load leaves it `null`
  // and sets `error`.
  report: TournamentEvalReport | null;
  isLoading: boolean;
  error: string | null;
}

export interface TournamentStoreActions {
  // `set` selects which recorded set's report to load (Task 12.12); the connected
  // dashboard passes the active `seedSet` read from `useReplayStore`. Optional so
  // a call that omits it resolves the server's default set. This store still never
  // imports `useReplayStore` — the set arrives as an argument.
  loadReport(set?: string): Promise<void>;
  clearError(): void;
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

export const useTournamentStore = create<
  TournamentStoreState & TournamentStoreActions
>((set) => {
  // Monotonic token guarding loadReport against out-of-order responses (newest
  // call wins), scoped to this store instance — mirrors `useReplayStore`. A
  // stale completion that resolves after a newer call started is dropped so it
  // can't clobber newer state.
  let latestReportRequest = 0;

  return {
    report: null,
    isLoading: false,
    error: null,

    async loadReport(set_?: string) {
      const requestToken = ++latestReportRequest;
      set({ isLoading: true, error: null });
      try {
        const report = await api.getTournamentReport(set_);
        if (requestToken !== latestReportRequest) {
          return;
        }
        set({ report, isLoading: false, error: null });
      } catch (error) {
        if (requestToken !== latestReportRequest) {
          return;
        }
        set({ report: null, isLoading: false, error: errorMessage(error) });
      }
    },

    clearError() {
      set({ error: null });
    },
  };
});
