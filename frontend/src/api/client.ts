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
  TickView,
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
  const data: unknown = await response.json();
  return data as T;
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
