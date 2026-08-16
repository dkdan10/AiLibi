// Store tests (Task 19.12): the async-ordering guards and the error-field split.
//
// WHY NO DOM: every guard under test is a plain closure inside the store's
// factory — a monotonic request token, or a post-await comparison of the
// in-flight game id / set against the live selection. None of it involves React,
// so the tests drive the store directly through `getState()` and resolve the
// mocked API promises OUT OF ORDER by hand. That is the only way to write these
// deterministically: rendering a component and hoping the responses interleave
// the wrong way is not a test, it is a coin flip.
//
// The store is a module singleton (one `create(...)` call), so each test restores
// the pristine state captured at import time. The request TOKENS are deliberately
// not reset — they are monotonic by design, and a test that depended on them
// starting at 0 would be testing the harness.

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import * as api from "../api/client";
import type {
  AgentMemoryView,
  MeetingView,
  ReplayMetadataView,
  ReplayView,
} from "../types/api";
import { useReplayStore } from "./replayStore";

vi.mock("../api/client", () => ({
  getSets: vi.fn(),
  listReplays: vi.fn(),
  getReplay: vi.fn(),
  getTick: vi.fn(),
  getMeeting: vi.fn(),
  getMemory: vi.fn(),
  getEvalCostSummary: vi.fn(),
  getTournamentReport: vi.fn(),
  getRubric: vi.fn(),
}));

const mocked = vi.mocked(api);

// ── fixtures + helpers ───────────────────────────────────────────────────────

/** A promise whose settlement this test controls — the whole point of the file. */
function deferred<T>(): {
  promise: Promise<T>;
  resolve: (value: T) => void;
  reject: (error: unknown) => void;
} {
  let resolve!: (value: T) => void;
  let reject!: (error: unknown) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  // Nothing in these tests leaves a rejection unobserved, but a deferred that is
  // rejected before the store awaits it would otherwise trip Node's
  // unhandled-rejection warning on the tick between creation and await.
  promise.catch(() => undefined);
  return { promise, resolve, reject };
}

function metadata(gameId: string, seed: number): ReplayMetadataView {
  return {
    game_id: gameId,
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

function replay(gameId: string, seed = 0): ReplayView {
  return {
    viewModelVersion: "1.0",
    metadata: metadata(gameId, seed),
    map: { rooms: [], vents: [], edges: [] },
    players: [
      { agent_id: "p-0", display_name: "P0", role: "CREWMATE", color: "#5DA83A" },
      { agent_id: "p-1", display_name: "P1", role: "IMPOSTOR", color: "#2BA45E" },
    ],
    ticks: [],
    meetings: [],
    failed_calls: [],
    finale: null,
  };
}

function meetingView(meetingId: string): MeetingView {
  return {
    meeting_id: meetingId,
    tick: 20,
    triggered_by: "p-1",
    trigger_kind: "body",
    outcome: "SKIPPED",
    ejected_player_id: null,
    turns: [],
    ballots: [],
    contradictions: [],
    llm_calls: [],
    prompt_versions: {},
    total_cost_usd: 0,
    gate: { leader: null, leader_max_confidence: 0, threshold: 0.6, passed: false },
  };
}

function memoryView(agentId: string): AgentMemoryView {
  return {
    agent_id: agentId,
    meeting_id: "m-1",
    tick: 20,
    events: [],
    beliefs: [],
    flags: [],
  } as unknown as AgentMemoryView;
}

const PRISTINE = useReplayStore.getState();

beforeEach(() => {
  // `replace: true` restores the actions along with the state, so each test sees
  // the same store the app boots with.
  useReplayStore.setState(PRISTINE, true);
});

afterEach(() => {
  vi.resetAllMocks();
});

// ── selectReplay: newest call wins ───────────────────────────────────────────

describe("selectReplay race guards", () => {
  it("drops a STALE SUCCESS that resolves after a newer selection", async () => {
    const slow = deferred<ReplayView>();
    const fast = deferred<ReplayView>();
    mocked.getReplay.mockReturnValueOnce(slow.promise).mockReturnValueOnce(fast.promise);

    const first = useReplayStore.getState().selectReplay("g-old");
    const second = useReplayStore.getState().selectReplay("g-new");

    // Out of order on purpose: the NEWER request lands first, then the older one.
    fast.resolve(replay("g-new"));
    await second;
    slow.resolve(replay("g-old"));
    await first;

    expect(useReplayStore.getState().currentReplay?.metadata.game_id).toBe("g-new");
  });

  it("drops a STALE FAILURE that rejects after a newer selection succeeded", async () => {
    const slow = deferred<ReplayView>();
    const fast = deferred<ReplayView>();
    mocked.getReplay.mockReturnValueOnce(slow.promise).mockReturnValueOnce(fast.promise);

    const first = useReplayStore.getState().selectReplay("g-old");
    const second = useReplayStore.getState().selectReplay("g-new");

    fast.resolve(replay("g-new"));
    await second;
    slow.reject(new Error("g-old exploded"));
    await first;

    const state = useReplayStore.getState();
    expect(state.currentReplay?.metadata.game_id).toBe("g-new");
    // The killer case: without the token guard the stale rejection would null the
    // replay AND raise a banner for a game nobody is watching.
    expect(state.replayLoadError).toBeNull();
  });

  it("drops a stale SUCCESS from a set the user switched away from", async () => {
    // The request token alone cannot catch this: changing the Set selector does
    // not start a new selectReplay, so the in-flight call is still the newest.
    useReplayStore.setState({ seedSet: "9p2i", availableSets: ["9p2i", "4p1i"] });
    const pending = deferred<ReplayView>();
    mocked.getReplay.mockReturnValueOnce(pending.promise);

    const call = useReplayStore.getState().selectReplay("g-1");
    useReplayStore.getState().setSeedSet("4p1i"); // mid-flight switch
    pending.resolve(replay("g-1"));
    await call;

    expect(useReplayStore.getState().currentReplay).toBeNull();
    expect(useReplayStore.getState().view).toBe("replays");
  });

  it("SUPPRESSES a stale failure for a set switched away from, but SURFACES one whose set was normalized away", async () => {
    // Two different stale-failure cases, and the store must treat them
    // differently: a live switch to another AVAILABLE set means the user moved
    // on (suppress); a request whose set is null or no longer available is the
    // deep-link case whose error the URL hydration is waiting on (surface).
    useReplayStore.setState({ seedSet: "9p2i", availableSets: ["9p2i", "4p1i"] });
    const switched = deferred<ReplayView>();
    mocked.getReplay.mockReturnValueOnce(switched.promise);
    const suppressed = useReplayStore.getState().selectReplay("g-1");
    useReplayStore.getState().setSeedSet("4p1i");
    switched.reject(new Error("boom"));
    await suppressed;
    expect(useReplayStore.getState().replayLoadError).toBeNull();

    useReplayStore.setState({ seedSet: "gone", availableSets: ["9p2i", "4p1i"] });
    const normalized = deferred<ReplayView>();
    mocked.getReplay.mockReturnValueOnce(normalized.promise);
    const surfaced = useReplayStore.getState().selectReplay("g-2");
    useReplayStore.getState().setSeedSet("9p2i"); // loadSets normalized it away
    normalized.reject(new Error("404 no such game"));
    await surfaced;
    expect(useReplayStore.getState().replayLoadError).toContain("404 no such game");
  });

  it("resets the replay-scoped overlays on a successful selection", async () => {
    useReplayStore.setState({
      perspective: { mode: "agent", agentId: "p-1" },
      revealOutcome: true,
      currentTick: 12,
      selectedMeetingId: "m-9",
      selectedAgentId: "p-3",
      hoverTick: 7,
    });
    mocked.getReplay.mockResolvedValueOnce(replay("g-1"));
    await useReplayStore.getState().selectReplay("g-1");

    const state = useReplayStore.getState();
    expect(state.perspective).toEqual({ mode: "omniscient" });
    expect(state.revealOutcome).toBe(false);
    expect(state.currentTick).toBe(0);
    expect(state.selectedMeetingId).toBeNull();
    expect(state.selectedAgentId).toBeNull();
    expect(state.hoverTick).toBeNull();
    expect(state.view).toBe("workspace");
  });
});

// ── loadReplayList / loadSets: newest call wins ──────────────────────────────

describe("loadReplayList race guards", () => {
  it("keeps the NEWEST list when an older request resolves last", async () => {
    const slow = deferred<ReplayMetadataView[]>();
    const fast = deferred<ReplayMetadataView[]>();
    mocked.listReplays.mockReturnValueOnce(slow.promise).mockReturnValueOnce(fast.promise);

    const first = useReplayStore.getState().loadReplayList();
    const second = useReplayStore.getState().loadReplayList();

    fast.resolve([metadata("g-new", 1)]);
    await second;
    slow.resolve([metadata("g-old", 0)]);
    await first;

    expect(useReplayStore.getState().replayList?.map((m) => m.game_id)).toEqual([
      "g-new",
    ]);
  });

  it("does not let a stale FAILURE null out a newer successful list", async () => {
    const slow = deferred<ReplayMetadataView[]>();
    const fast = deferred<ReplayMetadataView[]>();
    mocked.listReplays.mockReturnValueOnce(slow.promise).mockReturnValueOnce(fast.promise);

    const first = useReplayStore.getState().loadReplayList();
    const second = useReplayStore.getState().loadReplayList();

    fast.resolve([metadata("g-new", 1)]);
    await second;
    slow.reject(new Error("stale /replays failure"));
    await first;

    const state = useReplayStore.getState();
    expect(state.replayList).not.toBeNull();
    expect(state.replayListError).toBeNull();
  });

  it("clears the previous set's list while the new one loads", async () => {
    useReplayStore.setState({ replayList: [metadata("g-old", 0)] });
    const pending = deferred<ReplayMetadataView[]>();
    mocked.listReplays.mockReturnValueOnce(pending.promise);

    const call = useReplayStore.getState().loadReplayList();
    // In flight: the OLD cards must not sit under the new selector.
    expect(useReplayStore.getState().replayList).toBeNull();
    pending.resolve([metadata("g-new", 1)]);
    await call;
    expect(useReplayStore.getState().replayList).toHaveLength(1);
  });
});

describe("loadSets race guards", () => {
  it("keeps the NEWEST sets response when an older one resolves last", async () => {
    const slow = deferred<{ sets: string[]; default: string }>();
    const fast = deferred<{ sets: string[]; default: string }>();
    mocked.getSets.mockReturnValueOnce(slow.promise).mockReturnValueOnce(fast.promise);

    const first = useReplayStore.getState().loadSets();
    const second = useReplayStore.getState().loadSets();

    fast.resolve({ sets: ["9p2i"], default: "9p2i" });
    await second;
    slow.resolve({ sets: ["stale"], default: "stale" });
    await first;

    const state = useReplayStore.getState();
    expect(state.availableSets).toEqual(["9p2i"]);
    expect(state.seedSet).toBe("9p2i");
  });

  it("keeps an already-chosen set the server still serves", async () => {
    useReplayStore.setState({ seedSet: "4p1i" });
    mocked.getSets.mockResolvedValueOnce({ sets: ["9p2i", "4p1i"], default: "9p2i" });
    await useReplayStore.getState().loadSets();
    expect(useReplayStore.getState().seedSet).toBe("4p1i");
  });
});

// ── keyed cache fetches: the in-flight game + set comparison ─────────────────

describe("fetchMemoryView race guards", () => {
  beforeEach(() => {
    useReplayStore.setState({ currentReplay: replay("g-1"), seedSet: "9p2i" });
  });

  it("drops a snapshot that lands after the selected replay changed", async () => {
    const pending = deferred<AgentMemoryView>();
    mocked.getMemory.mockReturnValueOnce(pending.promise);

    const call = useReplayStore.getState().fetchMemoryView("m-1", "p-0");
    // The user opened another game while the snapshot was in flight.
    useReplayStore.setState({ currentReplay: replay("g-2") });
    pending.resolve(memoryView("p-0"));
    await call;

    // Landing here would ALSO poison the cache: the key is meeting+agent, so the
    // stale snapshot would become a cache HIT for game 2 and never re-fetch.
    expect(useReplayStore.getState().memoryCache).toEqual({});
  });

  it("drops a snapshot that lands after a live SET switch", async () => {
    const pending = deferred<AgentMemoryView>();
    mocked.getMemory.mockReturnValueOnce(pending.promise);

    const call = useReplayStore.getState().fetchMemoryView("m-1", "p-0");
    useReplayStore.setState({ seedSet: "4p1i" }); // same seed-based game_id, other set
    pending.resolve(memoryView("p-0"));
    await call;

    expect(useReplayStore.getState().memoryCache).toEqual({});
  });

  it("drops an ERROR for a replay no longer selected", async () => {
    const pending = deferred<AgentMemoryView>();
    mocked.getMemory.mockReturnValueOnce(pending.promise);

    const call = useReplayStore.getState().fetchMemoryView("m-1", "p-0");
    useReplayStore.setState({ currentReplay: replay("g-2") });
    pending.reject(new Error("memory 500"));
    await call;

    expect(useReplayStore.getState().memoryError).toBeNull();
  });

  it("caches a snapshot that lands while its replay is still selected", async () => {
    mocked.getMemory.mockResolvedValueOnce(memoryView("p-0"));
    await useReplayStore.getState().fetchMemoryView("m-1", "p-0");
    expect(useReplayStore.getState().memoryCache["m-1:p-0"]).toBeDefined();
  });

  it("does not re-fetch a key already in the cache", async () => {
    mocked.getMemory.mockResolvedValueOnce(memoryView("p-0"));
    await useReplayStore.getState().fetchMemoryView("m-1", "p-0");
    await useReplayStore.getState().fetchMemoryView("m-1", "p-0");
    expect(mocked.getMemory).toHaveBeenCalledTimes(1);
  });

  it("lets concurrent fetches for DIFFERENT keys on one replay coexist", async () => {
    // The token idiom used by selectReplay would be wrong here: these are keyed
    // cache writes, and "newest call wins" would throw away the first agent's
    // snapshot for no reason.
    const a = deferred<AgentMemoryView>();
    const b = deferred<AgentMemoryView>();
    mocked.getMemory.mockReturnValueOnce(a.promise).mockReturnValueOnce(b.promise);

    const first = useReplayStore.getState().fetchMemoryView("m-1", "p-0");
    const second = useReplayStore.getState().fetchMemoryView("m-1", "p-1");
    b.resolve(memoryView("p-1"));
    await second;
    a.resolve(memoryView("p-0"));
    await first;

    expect(Object.keys(useReplayStore.getState().memoryCache).sort()).toEqual([
      "m-1:p-0",
      "m-1:p-1",
    ]);
  });
});

describe("fetchMeeting race guards", () => {
  beforeEach(() => {
    useReplayStore.setState({ currentReplay: replay("g-1"), seedSet: "9p2i" });
  });

  it("drops a transcript that lands after the selected replay changed", async () => {
    const pending = deferred<MeetingView>();
    mocked.getMeeting.mockReturnValueOnce(pending.promise);

    const call = useReplayStore.getState().fetchMeeting("m-1");
    useReplayStore.setState({ currentReplay: replay("g-2") });
    pending.resolve(meetingView("m-1"));
    await call;

    expect(useReplayStore.getState().meetingCache).toEqual({});
  });

  it("drops an ERROR for a set no longer active", async () => {
    const pending = deferred<MeetingView>();
    mocked.getMeeting.mockReturnValueOnce(pending.promise);

    const call = useReplayStore.getState().fetchMeeting("m-1");
    useReplayStore.setState({ seedSet: "4p1i" });
    pending.reject(new Error("meeting 500"));
    await call;

    expect(useReplayStore.getState().meetingError).toBeNull();
  });

  it("caches a transcript that lands while its replay is still selected", async () => {
    mocked.getMeeting.mockResolvedValueOnce(meetingView("m-1"));
    await useReplayStore.getState().fetchMeeting("m-1");
    expect(useReplayStore.getState().meetingCache["m-1"]).toBeDefined();
  });
});

// ── the error-field split (Task 19.12) ───────────────────────────────────────

describe("the three error fields are independent", () => {
  it("a REPLAY-LOAD failure writes only replayLoadError", async () => {
    mocked.getReplay.mockRejectedValueOnce(new Error("replay 500"));
    await useReplayStore.getState().selectReplay("g-1");

    const state = useReplayStore.getState();
    expect(state.replayLoadError).toContain("replay 500");
    expect(state.memoryError).toBeNull();
    expect(state.meetingError).toBeNull();
  });

  it("a MEMORY failure writes only memoryError", async () => {
    useReplayStore.setState({ currentReplay: replay("g-1"), seedSet: "9p2i" });
    mocked.getMemory.mockRejectedValueOnce(new Error("memory 404"));
    await useReplayStore.getState().fetchMemoryView("m-1", "p-0");

    const state = useReplayStore.getState();
    expect(state.memoryError?.message).toContain("memory 404");
    // Before the split this same failure raised "Failed to load replay: …" in
    // the browser AND dropped `usePlaybackEngine`'s pending deep-link hydration.
    expect(state.replayLoadError).toBeNull();
    expect(state.meetingError).toBeNull();
  });

  it("a MEETING failure writes only meetingError", async () => {
    useReplayStore.setState({ currentReplay: replay("g-1"), seedSet: "9p2i" });
    mocked.getMeeting.mockRejectedValueOnce(new Error("meeting 502"));
    await useReplayStore.getState().fetchMeeting("m-1");

    const state = useReplayStore.getState();
    expect(state.meetingError?.message).toContain("meeting 502");
    expect(state.replayLoadError).toBeNull();
    expect(state.memoryError).toBeNull();
  });

  it("tags each keyed failure with the request it belongs to", async () => {
    useReplayStore.setState({ currentReplay: replay("g-1"), seedSet: "9p2i" });
    mocked.getMemory.mockRejectedValueOnce(new Error("memory 404"));
    mocked.getMeeting.mockRejectedValueOnce(new Error("meeting 502"));
    await useReplayStore.getState().fetchMemoryView("m-1", "p-0");
    await useReplayStore.getState().fetchMeeting("m-1");

    // The key is what lets a consumer ask "is this MY error?" — without it the
    // error is a replay-wide scalar that outlives the request that produced it.
    expect(useReplayStore.getState().memoryError?.key).toBe("m-1:p-0");
    expect(useReplayStore.getState().meetingError?.key).toBe("m-1");
  });

  it("a SUCCESSFUL retry clears its own failure and leaves other keys' alone", async () => {
    useReplayStore.setState({
      currentReplay: replay("g-1"),
      seedSet: "9p2i",
      memoryError: { key: "m-9:p-9", message: "someone else's failure" },
    });
    mocked.getMeeting
      .mockRejectedValueOnce(new Error("meeting 502"))
      .mockResolvedValueOnce(meetingView("m-1"));

    await useReplayStore.getState().fetchMeeting("m-1");
    expect(useReplayStore.getState().meetingError?.key).toBe("m-1");

    // Retry the SAME meeting; it works this time.
    await useReplayStore.getState().fetchMeeting("m-1");
    expect(useReplayStore.getState().meetingError).toBeNull();
    // …and a pending failure for a different key is still true, so it stands.
    expect(useReplayStore.getState().memoryError?.key).toBe("m-9:p-9");
  });

  it("a failure for one meeting never captions ANOTHER meeting's loaded bodies", async () => {
    // The consumer-side half of the same guarantee, and the exact case a bare
    // scalar got wrong: meeting A fails, meeting B succeeds, and B's transcript
    // must render its bodies rather than A's error. Nothing clears A's failure
    // here — B simply is not A, and the key is what says so.
    useReplayStore.setState({ currentReplay: replay("g-1"), seedSet: "9p2i" });
    mocked.getMeeting
      .mockRejectedValueOnce(new Error("meeting A 502"))
      .mockResolvedValueOnce(meetingView("m-B"));

    await useReplayStore.getState().fetchMeeting("m-A");
    await useReplayStore.getState().fetchMeeting("m-B");

    const state = useReplayStore.getState();
    expect(state.meetingCache["m-B"]).toBeDefined();
    expect(state.meetingError?.key).toBe("m-A");
    // The assertion that matters: B's panel asks "is this error mine?" and the
    // answer is no.
    expect(state.meetingError?.key === "m-B").toBe(false);
  });

  it("a memory failure for one agent never explains another agent's snapshot", async () => {
    useReplayStore.setState({ currentReplay: replay("g-1"), seedSet: "9p2i" });
    mocked.getMemory
      .mockRejectedValueOnce(new Error("memory 404"))
      .mockResolvedValueOnce(memoryView("p-1"));

    await useReplayStore.getState().fetchMemoryView("m-1", "p-0");
    await useReplayStore.getState().fetchMemoryView("m-1", "p-1");

    const state = useReplayStore.getState();
    expect(state.memoryCache["m-1:p-1"]).toBeDefined();
    expect(state.memoryError?.key).toBe("m-1:p-0");
    expect(state.memoryError?.key === "m-1:p-1").toBe(false);
  });

  it("three failures coexist, each readable by its own surface", async () => {
    useReplayStore.setState({ currentReplay: replay("g-1"), seedSet: "9p2i" });
    mocked.getMemory.mockRejectedValueOnce(new Error("memory 404"));
    mocked.getMeeting.mockRejectedValueOnce(new Error("meeting 502"));
    await useReplayStore.getState().fetchMemoryView("m-1", "p-0");
    await useReplayStore.getState().fetchMeeting("m-1");
    useReplayStore.setState({ replayLoadError: "replay 500" });

    const state = useReplayStore.getState();
    expect(state.replayLoadError).toBe("replay 500");
    expect(state.memoryError?.message).toContain("memory 404");
    expect(state.meetingError?.message).toContain("meeting 502");
  });

  it("clearReplayLoadError clears ONLY the load error", () => {
    useReplayStore.setState({
      replayListError: "list boom",
      replayLoadError: "load boom",
      memoryError: { key: "m-1:p-0", message: "memory boom" },
      meetingError: { key: "m-1", message: "meeting boom" },
    });
    useReplayStore.getState().clearReplayLoadError();

    const state = useReplayStore.getState();
    expect(state.replayLoadError).toBeNull();
    expect(state.replayListError).toBe("list boom");
    expect(state.memoryError?.message).toBe("memory boom");
    expect(state.meetingError?.message).toBe("meeting boom");
  });

  it("clearError clears every surfaced error", () => {
    useReplayStore.setState({
      replayListError: "list boom",
      replayLoadError: "load boom",
      memoryError: { key: "m-1:p-0", message: "memory boom" },
      meetingError: { key: "m-1", message: "meeting boom" },
    });
    useReplayStore.getState().clearError();

    const state = useReplayStore.getState();
    expect(state.replayListError).toBeNull();
    expect(state.replayLoadError).toBeNull();
    expect(state.memoryError).toBeNull();
    expect(state.meetingError).toBeNull();
  });

  it("a successful selection clears all three (they are replay-scoped)", async () => {
    useReplayStore.setState({
      replayLoadError: "load boom",
      memoryError: { key: "m-1:p-0", message: "memory boom" },
      meetingError: { key: "m-1", message: "meeting boom" },
    });
    mocked.getReplay.mockResolvedValueOnce(replay("g-1"));
    await useReplayStore.getState().selectReplay("g-1");

    const state = useReplayStore.getState();
    expect(state.replayLoadError).toBeNull();
    expect(state.memoryError).toBeNull();
    expect(state.meetingError).toBeNull();
  });

  it("a FAILED selection clears the other two and raises only the load error", async () => {
    useReplayStore.setState({
      memoryError: { key: "m-1:p-0", message: "memory boom" },
      meetingError: { key: "m-1", message: "meeting boom" },
    });
    mocked.getReplay.mockRejectedValueOnce(new Error("replay 500"));
    await useReplayStore.getState().selectReplay("g-1");

    const state = useReplayStore.getState();
    expect(state.replayLoadError).toContain("replay 500");
    expect(state.memoryError).toBeNull();
    expect(state.meetingError).toBeNull();
  });
});

// ── the firewall invariants the store itself owns ────────────────────────────

describe("fog/inspector firewall invariants", () => {
  it("selecting another agent while in fog RE-AIMS the fog to that agent", () => {
    useReplayStore.setState({ perspective: { mode: "agent", agentId: "p-0" } });
    useReplayStore.getState().selectAgent("p-1");

    const state = useReplayStore.getState();
    expect(state.selectedAgentId).toBe("p-1");
    expect(state.perspective).toEqual({ mode: "agent", agentId: "p-1" });
  });

  it("clearing the selection never changes the lens", () => {
    useReplayStore.setState({
      perspective: { mode: "agent", agentId: "p-0" },
      selectedAgentId: "p-0",
    });
    useReplayStore.getState().selectAgent(null);
    expect(useReplayStore.getState().perspective).toEqual({
      mode: "agent",
      agentId: "p-0",
    });
  });

  it("omniscient selection is unconstrained", () => {
    useReplayStore.getState().selectAgent("p-1");
    expect(useReplayStore.getState().perspective).toEqual({ mode: "omniscient" });
  });

  it("changing the fog SUBJECT re-aims an open inspector", () => {
    useReplayStore.setState({ selectedAgentId: "p-0" });
    useReplayStore.getState().setPerspective({ mode: "agent", agentId: "p-1" });
    expect(useReplayStore.getState().selectedAgentId).toBe("p-1");
  });

  it("returning to Omniscient leaves the inspector selection intact", () => {
    useReplayStore.setState({
      selectedAgentId: "p-0",
      perspective: { mode: "agent", agentId: "p-0" },
    });
    useReplayStore.getState().setPerspective({ mode: "omniscient" });
    expect(useReplayStore.getState().selectedAgentId).toBe("p-0");
  });
});

// ── payload windowing (the store's other silent contract) ────────────────────

describe("windowing", () => {
  it("strips the LLM prompt/response bodies from the bulk payload", async () => {
    const withBodies = replay("g-1");
    withBodies.meetings = [
      {
        ...meetingView("m-1"),
        llm_calls: [
          {
            prompt_text: "a very long rendered memory view",
            response_text: "a very long response",
          } as unknown as MeetingView["llm_calls"][number],
        ],
      },
    ];
    mocked.getReplay.mockResolvedValueOnce(withBodies);
    await useReplayStore.getState().selectReplay("g-1");

    const call = useReplayStore.getState().currentReplay?.meetings[0]?.llm_calls[0];
    expect(call?.prompt_text).toBe("");
    expect(call?.response_text).toBe("");
  });
});
