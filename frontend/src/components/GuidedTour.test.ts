// The first visit's teaching game: it starts playing, and it holds auto-follow
// off until the tour closes.
//
// WHY NO DOM: both halves are plain store transactions around the mocked API —
// `loadCuratedSeed` picks the curated game, loads it, and decides whether to
// start it; `releaseTeachingHold` gives auto-follow back. The browser-only half
// (the card on screen, focus, Escape) is the journey's first-visit test.

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import * as api from "../api/client";
import { useReplayStore } from "../store/replayStore";
import type { MeetingView, ReplayMetadataView, ReplayView, TickView } from "../types/api";
import { loadCuratedSeed, prefersReducedMotion, releaseTeachingHold } from "./GuidedTour";
import { featuredForSet } from "./ReplayPicker";

vi.mock("../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../api/client")>()),
  getSets: vi.fn(),
  listReplays: vi.fn(),
  getReplay: vi.fn(),
}));

const mocked = vi.mocked(api);

const SET = "9p2i";
const MEETING_TICK = 12;

/** The seed the curated list puts first for the teaching set, read rather than typed. */
function curatedSeed(): number {
  const head = featuredForSet(SET)[0];
  if (head === undefined) throw new Error("the teaching set has no curated game");
  return head.seed;
}

function metadata(seed: number): ReplayMetadataView {
  return {
    game_id: `g-${String(seed)}`,
    seed,
    total_ticks: 40,
    winner: "CREWMATES",
    winner_reason: "CREWMATE_EJECT",
    meeting_count: 1,
    total_cost_usd: 0,
    prompt_versions: {},
    created_at: null,
  };
}

/** A game whose frames run Start, 0, 1, … with one meeting at `MEETING_TICK`. */
function replay(seed: number): ReplayView {
  const ticks = Array.from({ length: 20 }, (_, index) => ({ tick: index - 1 }) as unknown as TickView);
  const meeting = { meeting_id: "m-1", tick: MEETING_TICK, llm_calls: [] } as unknown as MeetingView;
  return {
    viewModelVersion: "1.0",
    metadata: metadata(seed),
    map: { rooms: [], vents: [], edges: [] },
    players: [],
    ticks,
    meetings: [meeting],
    failed_calls: [],
    finale: null,
  };
}

/** The frame index that shows engine tick `tick` in `replay()`'s timeline. */
const frameOf = (tick: number): number => tick + 1;

function stubMotion(reduced: boolean): void {
  vi.stubGlobal("window", {
    matchMedia: (query: string) => ({
      matches: reduced && query === "(prefers-reduced-motion: reduce)",
    }),
  });
}

/** Serve the teaching set with the curated game among two others. */
function serveTeachingSet(): number {
  const seed = curatedSeed();
  mocked.getSets.mockResolvedValue({ sets: [SET, "4p1i"], default: SET });
  mocked.listReplays.mockResolvedValue([metadata(seed + 1), metadata(seed), metadata(seed + 2)]);
  mocked.getReplay.mockImplementation((gameId) =>
    Promise.resolve(replay(Number(gameId.replace("g-", "")))),
  );
  return seed;
}

const PRISTINE = useReplayStore.getState();

beforeEach(() => {
  useReplayStore.setState(PRISTINE, true);
  // The tour publishes this before it asks for the teaching game.
  useReplayStore.setState({ guidedTourOpen: true });
});

afterEach(() => {
  vi.resetAllMocks();
  vi.unstubAllGlobals();
});

describe("the first visit's teaching game", () => {
  it("opens the curated game, starts it playing and holds auto-follow off", async () => {
    stubMotion(false);
    const seed = serveTeachingSet();

    expect(await loadCuratedSeed()).toBe(true);

    const state = useReplayStore.getState();
    expect(state.currentReplay?.metadata.seed).toBe(seed);
    expect(state.view).toBe("workspace");
    expect(state.isPlaying).toBe(true);
    expect(state.autoFollow).toBe(false);
  });

  it("loads the game but starts nothing under reduced motion", async () => {
    stubMotion(true);
    const seed = serveTeachingSet();

    expect(await loadCuratedSeed()).toBe(false);

    const state = useReplayStore.getState();
    expect(state.currentReplay?.metadata.seed).toBe(seed);
    expect(state.isPlaying).toBe(false);
    expect(state.autoFollow).toBe(true);
  });

  it("starts nothing, and takes no hold, when the tour closed while the game loaded", async () => {
    stubMotion(false);
    serveTeachingSet();
    mocked.getReplay.mockImplementation((gameId) => {
      // The visitor skips the tour while the game is on the wire.
      useReplayStore.getState().setGuidedTourOpen(false);
      return Promise.resolve(replay(Number(gameId.replace("g-", ""))));
    });

    expect(await loadCuratedSeed()).toBe(false);

    const state = useReplayStore.getState();
    expect(state.currentReplay).not.toBeNull();
    expect(state.isPlaying).toBe(false);
    expect(state.autoFollow).toBe(true);
  });

  it("leaves a replay the visitor already opened alone", async () => {
    stubMotion(false);
    serveTeachingSet();
    useReplayStore.setState({ currentReplay: replay(7), seedSet: SET });

    expect(await loadCuratedSeed()).toBe(false);

    const state = useReplayStore.getState();
    expect(mocked.getReplay).not.toHaveBeenCalled();
    expect(state.currentReplay?.metadata.seed).toBe(7);
    expect(state.isPlaying).toBe(false);
    expect(state.autoFollow).toBe(true);
  });
});

describe("closing the tour gives auto-follow back", () => {
  it("opens the meeting the playhead is parked on", () => {
    useReplayStore.setState({
      currentReplay: replay(1),
      currentTick: frameOf(MEETING_TICK),
      autoFollow: false,
    });

    releaseTeachingHold();

    const state = useReplayStore.getState();
    expect(state.autoFollow).toBe(true);
    expect(state.selectedMeetingId).toBe("m-1");
  });

  it("opens nothing on a frame that is not a meeting's", () => {
    useReplayStore.setState({
      currentReplay: replay(1),
      currentTick: frameOf(MEETING_TICK - 1),
      autoFollow: false,
    });

    releaseTeachingHold();

    const state = useReplayStore.getState();
    expect(state.autoFollow).toBe(true);
    expect(state.selectedMeetingId).toBeNull();
  });

  it("turns auto-follow on even with no game loaded", () => {
    useReplayStore.setState({ currentReplay: null, autoFollow: false });

    releaseTeachingHold();

    expect(useReplayStore.getState().autoFollow).toBe(true);
    expect(useReplayStore.getState().selectedMeetingId).toBeNull();
  });
});

describe("prefersReducedMotion", () => {
  it("reads the system preference each time it is asked", () => {
    stubMotion(true);
    expect(prefersReducedMotion()).toBe(true);
    stubMotion(false);
    expect(prefersReducedMotion()).toBe(false);
  });

  it("is false where the browser cannot answer", () => {
    vi.stubGlobal("window", {});
    expect(prefersReducedMotion()).toBe(false);
  });
});
