// Typed client for the Phase 4 spectator API. Every method maps to one 4.1
// endpoint and returns a parsed, typed response. HTTP and network failures are
// surfaced as `ApiError` rather than silently swallowed.
//
// Requests target the `/api` prefix, which the Vite dev server proxies to the
// FastAPI app on :8000 (stripping `/api`). See `vite.config.ts`.
//
// TWO DATA SOURCES, ONE CLIENT (Task 19.13). A normal build talks to the live
// FastAPI app. The STATIC-DEMO build — the artifact `scripts/build_demo_bundle.py`
// produces — has no API process at all: the same calls read pre-baked JSON that
// ships beside the bundle's `index.html`. That is the whole seam; there is no
// parallel client, no second set of methods, and nothing downstream of
// `apiUrl()` knows which mode it is in.

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

// The bundle's baked data root, RELATIVE to the served document — so the artifact
// works from a server root, from a subdirectory, or off a `file://`-adjacent
// static host without being rebuilt for its URL.
const STATIC_BASE = "./data";

/**
 * True in a build produced by `scripts/build_demo_bundle.py`.
 *
 * `import.meta.env.VITE_*` is substituted at BUILD time, so in a normal build
 * this is the literal `false` and every static-mode branch below is dropped from
 * the bundle by dead-code elimination. (The builder relies on that: it asserts
 * the emitted JS carries the static data root, which only a static-mode build
 * can contain.)
 */
const STATIC_DATA_MODE: boolean =
  import.meta.env.VITE_AILIBI_STATIC_DATA === "1";

// The recorded set a static bundle serves for a request that omits `set`.
//
// This is NOT the hard-coded default that `withSet`'s note below forbids. That
// rule exists because the live server resolves its default from what is on disk, so
// only `GET /sets`.default can answer it. A bundle has no server and a fixed
// directory tree, so the builder RESOLVES the same answer at build time (through
// the same `DEFAULT_SET`-preferring rule) and stamps it in. The client still
// never guesses — it reads a resolution someone else made.
const STATIC_DEFAULT_SET = String(
  import.meta.env.VITE_AILIBI_STATIC_DEFAULT_SET ?? "",
);

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

async function getJson<T>(url: string): Promise<T> {
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

/**
 * One path segment carrying an untrusted id (a game id, a meeting id, an agent
 * id).
 *
 * Live: URL-encoded, as it always was. Static: reduced to a FILE-NAME-safe token,
 * because in a bundle a path segment is not a route parameter — it is a file on
 * disk. Meeting ids are `headless-seed-2:meeting-0`, and a `%3A` in a URL is a
 * `:` in a filename on the other side of any static server that percent-decodes
 * (all of them), which is portable nowhere. `scripts/build_demo_bundle.py`
 * applies the SAME rule when it names the baked files and fails loud if two ids
 * ever collapse onto one name, so the two sides cannot drift.
 */
export function pathSegment(value: string): string {
  return STATIC_DATA_MODE
    ? value.replace(/[^A-Za-z0-9._-]/g, "_")
    : encodeURIComponent(value);
}

// Multi-set serving (Task 12.12; design/phase-12/stage-1-design.md §2.1, §7). The
// backend serves all recorded sets in one run; the `set` query param selects which
// (`<parent>/<set>/`), defaulting server-side to the CURATED 9p2i set (Task 19.9 —
// flipped from the flat 4p1i fixture) so a call that omits it still resolves, now
// onto the set that has meetings and a rubric. `set` is threaded through
// `/replays`, `/replays/{game_id}/*`, `/eval/rubric`, and `/eval/tournament-report`.
// The server default is resolved from what is on disk, so `GET /sets`.default is
// the authority — never hard-code a set name as "the default" on this side.
function withSet(path: string, set?: string): string {
  if (set === undefined || set === "") {
    return path;
  }
  const sep = path.includes("?") ? "&" : "?";
  return `${path}${sep}set=${encodeURIComponent(set)}`;
}

/**
 * THE data-source seam (Task 19.13): the one function that turns an endpoint
 * path into the URL this build actually fetches.
 *
 * Live build — `/api<path>` with `?set=` appended, exactly as before.
 *
 * Static build — `./data/<set>/<path>.json`. The bundle mirrors the API's URL
 * space as a directory tree, so `GET /replays/x/meetings/y?set=9p2i` is the file
 * `data/9p2i/replays/x/meetings/y.json` and any static file server is a
 * sufficient backend. `GET /sets` is the one endpoint that is not per-set; the
 * builder writes an identical copy of it into every set directory rather than
 * buying a special case here.
 *
 * A `set` of `undefined`, `null` or `""` means "the request omits `set`" — the
 * live API then resolves its own default and a bundle reads the set the builder
 * stamped in. A static build with no stamped default RAISES rather than guessing
 * (AGENTS.md: no silent fallbacks); it can only happen if something other than
 * `scripts/build_demo_bundle.py` produced the bundle.
 */
export function apiUrl(path: string, set?: string | null): string {
  if (!STATIC_DATA_MODE) {
    return `${API_BASE}${withSet(path, set ?? undefined)}`;
  }
  const setDir =
    set === undefined || set === null || set === "" ? STATIC_DEFAULT_SET : set;
  if (setDir === "") {
    throw new Error(
      "static-data build carries no VITE_AILIBI_STATIC_DEFAULT_SET — rebuild " +
        "the demo bundle with scripts/build_demo_bundle.py",
    );
  }
  return `${STATIC_BASE}/${pathSegment(setDir)}${path}.json`;
}

// The available recorded sets + the default-served one (`GET /sets`). Auto-grows:
// a newly-recorded `replays/samples/<set>/` appears here with no code change.
export interface SetsResponse {
  sets: string[];
  default: string;
}

export function getSets(): Promise<SetsResponse> {
  return getJson<SetsResponse>(apiUrl("/sets"));
}

export function listReplays(set?: string): Promise<ReplayMetadataView[]> {
  return getJson<ReplayMetadataView[]>(apiUrl("/replays", set));
}

export function getReplay(gameId: string, set?: string): Promise<ReplayView> {
  return getJson<ReplayView>(apiUrl(`/replays/${pathSegment(gameId)}`, set));
}

export function getTick(
  gameId: string,
  tick: number,
  set?: string,
): Promise<TickView> {
  return getJson<TickView>(
    apiUrl(`/replays/${pathSegment(gameId)}/ticks/${tick}`, set),
  );
}

export function getMeeting(
  gameId: string,
  meetingId: string,
  set?: string,
): Promise<MeetingView> {
  return getJson<MeetingView>(
    apiUrl(
      `/replays/${pathSegment(gameId)}/meetings/${pathSegment(meetingId)}`,
      set,
    ),
  );
}

export function getMemory(
  gameId: string,
  meetingId: string,
  agentId: string,
  set?: string,
): Promise<AgentMemoryView> {
  return getJson<AgentMemoryView>(
    apiUrl(
      `/replays/${pathSegment(gameId)}/meetings/${pathSegment(meetingId)}` +
        `/memory/${pathSegment(agentId)}`,
      set,
    ),
  );
}

export function getEvalCostSummary(): Promise<EvalCostSummaryView> {
  return getJson<EvalCostSummaryView>(apiUrl("/eval/cost-summary"));
}

// The latest tournament eval report served by the privileged eval surface
// (Task 5.7), per served set (Task 12.12). The eval router is mounted at `/eval`,
// so the path mirrors `/eval/cost-summary`; raises `ApiError` (404 → no report
// present) like the sibling methods. The static demo bundle deliberately bakes NO
// report (the 9p2i one is 29 MB — the corpus, not a demo), so in a bundle this
// 404s onto the dashboard's existing first-class "No tournament report" panel.
export function getTournamentReport(
  set?: string,
): Promise<TournamentEvalReport> {
  return getJson<TournamentEvalReport>(apiUrl("/eval/tournament-report", set));
}

// The per-set interestingness rubric served by the eval surface (Task 12.2,
// DESIGN.md §3.1, §7). The rubric is per served set and staleness-guarded; a set
// with no co-located `results-rubric-score.json` — 4p1i, the fast fixture, which
// an omitted `set` no longer resolves to (Task 19.9: the default is 9p2i, which
// ships one) — yields a 404, surfaced as `ApiError` with `status === 404` so the
// Highlights reel can render its first-class "no rubric" empty state rather than
// an error. The score itself is an internal pacing/structure heuristic, not a
// human rating: render it labelled, and never as a watchability ranking.
export function getRubric(set?: string): Promise<RubricView> {
  return getJson<RubricView>(apiUrl("/eval/rubric", set));
}
