// Client contract tests (Task 19.24): the runtime view-model version gate.
//
// WHY THIS FILE EXISTS. `getJson` ends in `data as T` — a compile-time claim
// about bytes nobody validated. That is fine for a shape the server and this
// build agree on, and useless the moment they do not: a server on a different
// view-model contract answers 200 with a payload that satisfies no invariant the
// components rely on, and the UI mis-renders it silently. The generated
// `VIEW_MODEL_VERSION` (from `api.schemas.VIEW_MODEL_VERSION`, emitted by
// `scripts/gen_frontend_types.py`) is what the client checks against, and a
// mismatch must FAIL LOUDLY rather than flow into a cast.
//
// The gate is only worth its line count if it is executable, so these cases
// drive the real `getJson` path through a stubbed `fetch` — a stubbed CLIENT
// would prove nothing about the client.
//
// WHY NO DOM: `fetch`, `Response` and the client are all plain values; nothing
// here renders. `vitest.config.ts` runs `environment: "node"` for exactly this
// reason.

import { readFileSync, readdirSync } from "node:fs";
import { dirname, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

import { afterEach, describe, expect, it, vi } from "vitest";

import { VIEW_MODEL_VERSION } from "../types/api";
import {
  ApiError,
  ViewModelVersionError,
  getBeliefFrames,
  getReplay,
  getRubric,
  getSets,
} from "./client";

/** A 200 carrying `body` as JSON — what a healthy API answers with. */
function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

/** Stub `fetch` with a single canned response. */
function stubFetch(response: Response): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(() => Promise.resolve(response)),
  );
}

/**
 * A minimal `ReplayView`-shaped payload stamped with `version`.
 *
 * Deliberately NOT a full replay: the version gate runs before any field is
 * read, so a fixture that mirrored the whole DTO tree would only add ways for
 * this file to go stale.
 */
function stampedReplay(version: string): Record<string, unknown> {
  return {
    viewModelVersion: version,
    metadata: { game_id: "headless-seed-0", seed: 0 },
    ticks: [],
    meetings: [],
  };
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("the view-model version gate", () => {
  it("rejects a payload stamped with a different contract version", async () => {
    stubFetch(jsonResponse(stampedReplay("99-from-the-future")));

    await expect(getReplay("headless-seed-0")).rejects.toBeInstanceOf(
      ViewModelVersionError,
    );
  });

  it("names both versions and the url in the failure", async () => {
    // The error is what an operator reads when a stale bundle meets a new API,
    // so it has to say what it got, what it wanted, and where from.
    stubFetch(jsonResponse(stampedReplay("99-from-the-future")));

    const error = await getReplay("headless-seed-0").catch(
      (caught: unknown) => caught,
    );

    expect(error).toBeInstanceOf(ViewModelVersionError);
    const mismatch = error as ViewModelVersionError;
    expect(mismatch.received).toBe("99-from-the-future");
    expect(mismatch.expected).toBe(VIEW_MODEL_VERSION);
    expect(mismatch.url).toContain("/replays/headless-seed-0");
    expect(mismatch.message).toContain("99-from-the-future");
    expect(mismatch.message).toContain("gen_frontend_types.py");
    // Not an ApiError: the request succeeded, the CONTRACT did not — retrying
    // is not the fix, so the two must stay distinguishable.
    expect(mismatch).not.toBeInstanceOf(ApiError);
  });

  it("accepts the version this build was generated against", async () => {
    stubFetch(jsonResponse(stampedReplay(VIEW_MODEL_VERSION)));

    const replay = await getReplay("headless-seed-0");

    expect(replay.viewModelVersion).toBe(VIEW_MODEL_VERSION);
  });

  it("passes through a payload the server does not stamp", async () => {
    // `GET /sets` (like ticks, meetings and memory) carries no version field and
    // never did. The rule is "if it is stamped, it must match" — an unstamped
    // payload is not a mismatch, and treating it as one would break every
    // endpoint but two.
    stubFetch(jsonResponse({ sets: ["9p2i", "4p1i"], default: "9p2i" }));

    await expect(getSets()).resolves.toEqual({
      sets: ["9p2i", "4p1i"],
      default: "9p2i",
    });
  });

  it("rejects a stamp that is present but not a string", async () => {
    // `viewModelVersion: string` is the contract; a number that happens to
    // stringify to the expected value is still a different contract.
    stubFetch(
      jsonResponse({
        ...stampedReplay(VIEW_MODEL_VERSION),
        viewModelVersion: 1,
      }),
    );

    await expect(getReplay("headless-seed-0")).rejects.toBeInstanceOf(
      ViewModelVersionError,
    );
  });

  it("leaves transport and HTTP failures as ApiError", async () => {
    // The gate runs after the status check, so a 404 is still an ApiError with
    // its status intact — the Highlights reel's "no rubric" empty state reads
    // `status === 404` and must not start seeing a contract error instead.
    stubFetch(new Response("no such replay", { status: 404 }));

    const error = await getReplay("headless-seed-0").catch(
      (caught: unknown) => caught,
    );

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).status).toBe(404);
  });
});

describe("the routes that used to build their own URL", () => {
  it("runs the version gate on the rubric the dashboard reads", async () => {
    // `RubricView` is one of only two stamped payloads. The Tournament
    // dashboard re-implemented this call with a bare `fetch`, so on the first
    // contract bump a stale build would have rendered a thousand lines of
    // statistics from foreign bytes while the picker — same endpoint, one route
    // away — threw. Both go through `getRubric` now.
    stubFetch(
      jsonResponse({ viewModelVersion: "99-from-the-future", per_game: [] }),
    );

    await expect(getRubric("9p2i")).rejects.toBeInstanceOf(
      ViewModelVersionError,
    );
  });

  it("keeps the rubric's 404 an ApiError so the absent state still reads it", async () => {
    // The dashboard's "no rubric for this set" panel is a first-class state,
    // selected on `err instanceof ApiError && err.status === 404`.
    stubFetch(new Response("no rubric", { status: 404 }));

    const error = await getRubric("4p1i").catch((caught: unknown) => caught);

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).status).toBe(404);
  });

  it("passes the belief frames through as the bare array the server sends", async () => {
    // Stated rather than implied: `GET /replays/{id}/beliefs` answers a bare
    // ARRAY, and `assertViewModelVersion` returns early on an array — so the
    // version guard is a NO-OP on this payload today. What routing through the
    // client buys here is the URL seam, the static-bundle data source and a
    // typed `ApiError`; the guard arms itself if the route ever gains a stamp.
    stubFetch(jsonResponse([{ meeting_id: "m-0", entries: [] }]));

    await expect(
      getBeliefFrames("headless-seed-0", "9p2i"),
    ).resolves.toHaveLength(1);
  });

  it("runs the same gate on the belief route the moment it is stamped", async () => {
    // Proves the ROUTING, which the array case cannot: `getBeliefFrames` is
    // `getJson`, not a second hand-rolled fetch. A bare `fetch` would resolve
    // this payload happily.
    stubFetch(jsonResponse({ viewModelVersion: "99-from-the-future" }));

    await expect(
      getBeliefFrames("headless-seed-0", "9p2i"),
    ).rejects.toBeInstanceOf(ViewModelVersionError);
  });

  it("surfaces a non-200 from the belief route as ApiError, not a bare Error", async () => {
    // The hand-rolled version threw `new Error("belief frames request failed
    // (status 500)")`, which no caller can branch on.
    stubFetch(new Response("boom", { status: 500 }));

    const error = await getBeliefFrames("headless-seed-0", "9p2i").catch(
      (caught: unknown) => caught,
    );

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).status).toBe(500);
  });
});

// ── the client is the only place that calls fetch ────────────────────────────
//
// The version gate lives inside `getJson`, so a component that calls `fetch`
// directly opts out of it — silently, and only visibly once the contract moves.
// This scan is the standing guard: it ships as an executable test rather than a
// lint rule so it can be aimed at a planted string and shown to bite.

const SRC_DIR = resolve(dirname(fileURLToPath(import.meta.url)), "..");

/** The one file allowed to call `fetch`, by path relative to `src/`. */
const FETCH_OWNER = "api/client.ts";

/**
 * `source` with the contents of comments and string literals blanked to spaces,
 * line breaks kept.
 *
 * A scan of raw text is not a scan of code: this file's own prose says "fetch"
 * a dozen times, and two components mention "the … fetch (…)" in a comment. This
 * is what makes the scan below about calls rather than about the word.
 */
function codeOnly(source: string): string {
  const out: string[] = [];
  let quote: string | null = null;
  let comment: "line" | "block" | null = null;
  for (let i = 0; i < source.length; i += 1) {
    const ch = source[i]!;
    const pair = source.slice(i, i + 2);
    const blank = ch === "\n" ? "\n" : " ";
    if (comment === "line") {
      if (ch === "\n") comment = null;
      out.push(blank);
    } else if (comment === "block") {
      if (pair === "*/") {
        comment = null;
        out.push("  ");
        i += 1;
      } else out.push(blank);
    } else if (quote !== null) {
      // Quoted text is not code — except a template literal, whose `${…}` holes
      // are, so backticks suppress comment/quote parsing without blanking.
      if (ch === "\\") {
        out.push(quote === "`" ? "\\ " : "  ");
        i += 1;
      } else if (ch === quote) {
        quote = null;
        out.push(ch);
      } else {
        out.push(quote === "`" ? ch : blank);
      }
    } else if (pair === "//" || pair === "/*") {
      comment = pair === "//" ? "line" : "block";
      out.push("  ");
      i += 1;
    } else if (ch === "'" || ch === '"' || ch === "`") {
      quote = ch;
      out.push(ch);
    } else {
      out.push(ch);
    }
  }
  return out.join("");
}

/**
 * A call to the GLOBAL fetch: bare, or reached through one of the three names
 * that denote the global object. `window.fetch(…)` bypasses `getJson` exactly as
 * a bare call does, so the gate has to see it.
 *
 * The lookbehind anchors the whole match, which is what keeps an unrelated
 * method out: `store.prefetch(…)` and `client.fetch(…)` are not the global.
 */
const GLOBAL_FETCH_CALL =
  /(?<![\w$.])(?:(?:window|globalThis|self)\.)?fetch\s*\(/;

/**
 * 1-based line numbers in `source` that call the global fetch directly.
 *
 * Pure — takes the path and the text, reads nothing — so the scan below can be
 * pointed at a planted fixture.
 */
function rawFetchLines(relPath: string, source: string): number[] {
  if (relPath === FETCH_OWNER) {
    return [];
  }
  return codeOnly(source)
    .split("\n")
    .map((line, index) => (GLOBAL_FETCH_CALL.test(line) ? index + 1 : 0))
    .filter((line) => line > 0);
}

/** Every `.ts` / `.tsx` under `src/`, test files excluded, as `[relPath, text]`. */
function sources(dir: string): Array<[string, string]> {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      return sources(full);
    }
    // A test may stub `fetch` — that is exercising the client, not bypassing it.
    if (!/\.tsx?$/.test(entry.name) || /\.test\.tsx?$/.test(entry.name)) {
      return [];
    }
    return [
      [
        relative(SRC_DIR, full).split(sep).join("/"),
        readFileSync(full, "utf8"),
      ],
    ];
  });
}

describe("no component reaches past the client", () => {
  const SOURCES = sources(SRC_DIR);

  it("scans a real set of files (the check is only as good as its input)", () => {
    expect(SOURCES.length).toBeGreaterThan(30);
    expect(SOURCES.map(([path]) => path)).toContain(FETCH_OWNER);
  });

  it("finds no direct fetch outside the client", () => {
    const offenders = SOURCES.flatMap(([path, text]) =>
      rawFetchLines(path, text).map((line) => `${path}:${line}`),
    );

    expect(offenders).toEqual([]);
  });

  it("bites on a planted call, and only on a real one", () => {
    expect(
      rawFetchLines("components/Planted.tsx", "const r = await fetch(url);"),
    ).toEqual([1]);
    expect(rawFetchLines(FETCH_OWNER, "const r = await fetch(url);")).toEqual(
      [],
    );
    expect(
      rawFetchLines("components/Planted.tsx", "void store.prefetch(id);"),
    ).toEqual([]);
    expect(
      rawFetchLines("components/Planted.tsx", "await client.fetch(url);"),
    ).toEqual([]);
  });

  it("bites on the global reached by name, not only on a bare call", () => {
    // `window.fetch(…)` skips `getJson` — the version gate, the static-bundle
    // URL seam and `ApiError` — exactly as a bare call does.
    expect(
      rawFetchLines("components/Planted.tsx", "await window.fetch(url);"),
    ).toEqual([1]);
    expect(
      rawFetchLines("components/Planted.tsx", "await globalThis.fetch(url);"),
    ).toEqual([1]);
    expect(
      rawFetchLines("components/Planted.tsx", "await self.fetch(url);"),
    ).toEqual([1]);
    // …and still not an unrelated method that happens to be called `fetch`.
    expect(
      rawFetchLines("components/Planted.tsx", "await store.window.fetch(url);"),
    ).toEqual([]);
  });

  it("would flag the client's own call but for the allow-list", () => {
    // Aims the scan at real committed source rather than a fixture: it proves
    // the walk reaches `client.ts`, that `codeOnly` does not blank a real call
    // out of a real file, and that the allow-list is the ONLY thing exempting
    // it — so an empty result above cannot be an empty scan.
    const client = SOURCES.find(([path]) => path === FETCH_OWNER)?.[1] ?? "";

    expect(rawFetchLines("api/not-the-client.ts", client)).toHaveLength(1);
  });

  it("reads code, not prose — and still sees a call after one", () => {
    const planted = [
      "// gate the BODIES fetch (the verbatim text rides the gate)",
      "/* a block comment mentioning fetch (x) */",
      'const label = "call fetch(url) here";',
      "await fetch(apiUrl(`/replays/${id}`));",
    ].join("\n");

    expect(rawFetchLines("components/Planted.tsx", planted)).toEqual([4]);
  });
});
