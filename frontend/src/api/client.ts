// Typed client for the Phase 4 spectator API. Every method maps to one 4.1
// endpoint and returns a parsed, typed response. HTTP and network failures are
// surfaced as `ApiError` rather than silently swallowed.
//
// Requests target the `/api` prefix, which the Vite dev server proxies to the
// FastAPI app on :8000 (stripping `/api`). See `vite.config.ts`.

import type {
  AgentMemoryView,
  EvalCostSummaryView,
  MeetingView,
  ReplayMetadataView,
  ReplayView,
  RubricView,
  TickView,
  TournamentEvalReport,
} from "../types/api";

const API_BASE = "/api";

/** Raised on any non-2xx response or transport-level failure. */
export class ApiError extends Error {
  readonly status: number;
  readonly url: string;
  readonly body: string;

  constructor(status: number, url: string, body: string) {
    super(`API request to ${url} failed (status ${status}): ${body}`);
    this.name = "ApiError";
    this.status = status;
    this.url = url;
    this.body = body;
  }
}

async function getJson<T>(path: string): Promise<T> {
  const url = `${API_BASE}${path}`;
  let response: Response;
  try {
    response = await fetch(url, { headers: { Accept: "application/json" } });
  } catch (cause) {
    const message = cause instanceof Error ? cause.message : String(cause);
    throw new ApiError(0, url, message);
  }
  if (!response.ok) {
    const body = await response.text().catch(() => "");
    throw new ApiError(response.status, url, body);
  }
  try {
    const data: unknown = await response.json();
    return data as T;
  } catch (cause) {
    const message = cause instanceof Error ? cause.message : String(cause);
    throw new ApiError(response.status, url, `invalid JSON response: ${message}`);
  }
}

function seg(value: string): string {
  return encodeURIComponent(value);
}

export function listReplays(): Promise<ReplayMetadataView[]> {
  return getJson<ReplayMetadataView[]>("/replays");
}

export function getReplay(gameId: string): Promise<ReplayView> {
  return getJson<ReplayView>(`/replays/${seg(gameId)}`);
}

export function getTick(gameId: string, tick: number): Promise<TickView> {
  return getJson<TickView>(`/replays/${seg(gameId)}/ticks/${tick}`);
}

export function getMeeting(
  gameId: string,
  meetingId: string,
): Promise<MeetingView> {
  return getJson<MeetingView>(
    `/replays/${seg(gameId)}/meetings/${seg(meetingId)}`,
  );
}

export function getMemory(
  gameId: string,
  meetingId: string,
  agentId: string,
): Promise<AgentMemoryView> {
  return getJson<AgentMemoryView>(
    `/replays/${seg(gameId)}/meetings/${seg(meetingId)}/memory/${seg(agentId)}`,
  );
}

export function getEvalCostSummary(): Promise<EvalCostSummaryView> {
  return getJson<EvalCostSummaryView>("/eval/cost-summary");
}

// The latest tournament eval report served by the privileged eval surface
// (Task 5.7). The eval router is mounted at `/eval`, so the path mirrors
// `/eval/cost-summary`; raises `ApiError` (404 → no report present) like the
// sibling methods.
export function getTournamentReport(): Promise<TournamentEvalReport> {
  return getJson<TournamentEvalReport>("/eval/tournament-report");
}

// The per-set interestingness rubric served by the eval surface (Task 12.2,
// DESIGN.md §3.1, §7). The rubric is per served set and staleness-guarded; a set
// with no co-located `results-rubric-score.json` (the 4p1i default) yields a
// 404, surfaced as `ApiError` with `status === 404` so the Highlights reel can
// render its first-class "no rubric" empty state rather than an error.
export function getRubric(): Promise<RubricView> {
  return getJson<RubricView>("/eval/rubric");
}
