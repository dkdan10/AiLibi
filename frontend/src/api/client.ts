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

// Multi-set serving (Task 12.12; design/phase-12/stage-1-design.md §2.1, §7). The
// backend serves all recorded sets in one run; the `set` query param selects which
// (`<parent>/<set>/`), defaulting server-side to the flat 4p1i baseline so a call
// that omits it still resolves. `set` is threaded through `/replays`,
// `/replays/{game_id}/*`, `/eval/rubric`, and `/eval/tournament-report`.
function withSet(path: string, set?: string): string {
  if (set === undefined || set === "") {
    return path;
  }
  const sep = path.includes("?") ? "&" : "?";
  return `${path}${sep}set=${encodeURIComponent(set)}`;
}

// The available recorded sets + the default-served one (`GET /sets`). Auto-grows:
// a newly-recorded `replays/samples/<set>/` appears here with no code change.
export interface SetsResponse {
  sets: string[];
  default: string;
}

export function getSets(): Promise<SetsResponse> {
  return getJson<SetsResponse>("/sets");
}

export function listReplays(set?: string): Promise<ReplayMetadataView[]> {
  return getJson<ReplayMetadataView[]>(withSet("/replays", set));
}

export function getReplay(gameId: string, set?: string): Promise<ReplayView> {
  return getJson<ReplayView>(withSet(`/replays/${seg(gameId)}`, set));
}

export function getTick(
  gameId: string,
  tick: number,
  set?: string,
): Promise<TickView> {
  return getJson<TickView>(withSet(`/replays/${seg(gameId)}/ticks/${tick}`, set));
}

export function getMeeting(
  gameId: string,
  meetingId: string,
  set?: string,
): Promise<MeetingView> {
  return getJson<MeetingView>(
    withSet(`/replays/${seg(gameId)}/meetings/${seg(meetingId)}`, set),
  );
}

export function getMemory(
  gameId: string,
  meetingId: string,
  agentId: string,
  set?: string,
): Promise<AgentMemoryView> {
  return getJson<AgentMemoryView>(
    withSet(
      `/replays/${seg(gameId)}/meetings/${seg(meetingId)}/memory/${seg(agentId)}`,
      set,
    ),
  );
}

export function getEvalCostSummary(): Promise<EvalCostSummaryView> {
  return getJson<EvalCostSummaryView>("/eval/cost-summary");
}

// The latest tournament eval report served by the privileged eval surface
// (Task 5.7), per served set (Task 12.12). The eval router is mounted at `/eval`,
// so the path mirrors `/eval/cost-summary`; raises `ApiError` (404 → no report
// present) like the sibling methods.
export function getTournamentReport(
  set?: string,
): Promise<TournamentEvalReport> {
  return getJson<TournamentEvalReport>(withSet("/eval/tournament-report", set));
}

// The per-set interestingness rubric served by the eval surface (Task 12.2,
// DESIGN.md §3.1, §7). The rubric is per served set and staleness-guarded; a set
// with no co-located `results-rubric-score.json` (the 4p1i default) yields a
// 404, surfaced as `ApiError` with `status === 404` so the Highlights reel can
// render its first-class "no rubric" empty state rather than an error.
export function getRubric(set?: string): Promise<RubricView> {
  return getJson<RubricView>(withSet("/eval/rubric", set));
}
