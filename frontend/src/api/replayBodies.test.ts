import { afterEach, describe, expect, it, vi } from "vitest";

import { VIEW_MODEL_VERSION } from "../types/api";

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.resetModules();
});

describe("on-demand model text", () => {
  it.each(["2", "3", VIEW_MODEL_VERSION])("reads old and current static payloads while retaining the audio gate (%s)", async (version) => {
    vi.stubEnv("VITE_AILIBI_STATIC_DATA", "1");
    vi.stubEnv("VITE_AILIBI_STATIC_DEFAULT_SET", "9p2i");
    vi.resetModules();
    const client = await import("./client");
    const replay = {
      viewModelVersion: version,
      ticks: [{ agent_states: [{ visibility: { audible_events: [
        { kind: "sabotage_alarm", room: null },
      ] } }] }],
      meetings: [],
    };
    const fetch = vi.fn<typeof globalThis.fetch>(() => Promise.resolve(new Response(JSON.stringify(replay), { status: 200 })));
    vi.stubGlobal("fetch", fetch);
    await expect(client.getReplay("headless-seed-23")).resolves.toEqual(replay);
    expect(fetch.mock.calls[0]?.[0]).toBe("./data/9p2i/replays/headless-seed-23.json");
    const corrupted = {
      ...replay,
      ticks: [{ agent_states: [{ visibility: { audible_events: [
        { kind: "vent_use_heard", room: "ADMIN" },
      ] } }] }],
    };
    fetch.mockImplementation(() => Promise.resolve(new Response(JSON.stringify(corrupted), { status: 200 })));
    await expect(client.getReplay("headless-seed-23")).rejects.toThrow("Unsupported audio cue");
  });

  it.each([false, true])("uses a lean live request or stable static filename (static=%s)", async (isStatic) => {
    vi.stubEnv("VITE_AILIBI_STATIC_DATA", isStatic ? "1" : "0");
    vi.stubEnv("VITE_AILIBI_STATIC_DEFAULT_SET", "9p2i");
    vi.resetModules();
    const client = await import("./client");
    // Historical bundles omit the inclusion marker and contain full bodies.
    const legacy = {
      viewModelVersion: VIEW_MODEL_VERSION,
      meetings: [{ llm_calls: [{ prompt_text: "original prompt", response_text: "original response" }] }],
    };
    const fetch = vi.fn<typeof globalThis.fetch>(() => Promise.resolve(new Response(JSON.stringify(legacy), { status: 200 })));
    vi.stubGlobal("fetch", fetch);

    const replay = await client.getReplay("headless-seed-23", "9p2i");
    expect(replay).toEqual(legacy);
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch.mock.calls[0]?.[0]).toBe(isStatic
      ? "./data/9p2i/replays/headless-seed-23.json"
      : "/api/replays/headless-seed-23?include_llm_bodies=false&set=9p2i");

    const meeting = await client.getMeeting("headless-seed-23", "headless-seed-23:meeting-0", "9p2i");
    expect(meeting).toEqual(legacy);
    expect(fetch.mock.calls[1]?.[0]).toBe(isStatic
      ? "./data/9p2i/replays/headless-seed-23/meetings/headless-seed-23_meeting-0.json"
      : "/api/replays/headless-seed-23/meetings/headless-seed-23%3Ameeting-0?set=9p2i");
  });

  it("surfaces unavailable meeting bodies rather than inventing empty success", async () => {
    const client = await import("./client");
    vi.stubGlobal("fetch", vi.fn(() => Promise.resolve(new Response("missing", { status: 404 }))));
    await expect(client.getMeeting("game", "missing")).rejects.toMatchObject({ status: 404 });
  });

  it.each([1, 2, "1"])("checks the compact summary's own format version (%s)", async (version) => {
    const client = await import("./client");
    vi.stubGlobal("fetch", vi.fn(() => Promise.resolve(new Response(JSON.stringify({ format_version: version }), { status: 200 }))));
    const request = client.getPublicResults("9p2i");
    if (version === 1) {
      await expect(request).resolves.toEqual({ format_version: 1 });
    } else {
      await expect(request).rejects.toThrow("Unsupported results format");
    }
  });
});
