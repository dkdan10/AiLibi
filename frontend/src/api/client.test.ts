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

import { afterEach, describe, expect, it, vi } from "vitest";

import { VIEW_MODEL_VERSION } from "../types/api";
import { ApiError, ViewModelVersionError, getReplay, getSets } from "./client";

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
