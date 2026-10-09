import { isValidElement, type ReactNode } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import {
  ReplayBrowserView,
  activeProfile,
  browserState,
  buildCards,
  cardProfiles,
  matchesFilters,
  reelSections,
  settledProfile,
  type ReelSection,
  type ReplayBrowserViewProps,
} from "./ReplayPicker";
import {
  EMPTY_FILTERS,
  ReplayFilters,
  parseFilterParams,
  writeFilterParams,
  type ReplayFilterState,
} from "./ReplayFilters";
import { shelfTitle } from "./HighlightCard";
import { ApiError } from "../api/client";
import { DASHBOARD_COPY, PICKER_COPY, PROFILE_COPY } from "../lib/copy";
import type { GameFacetsView, GameProfileView, ReplayMetadataView } from "../types/api";

function facets(seed: number, tripped = false): GameFacetsView {
  return {
    seed,
    ticks: 30 + seed,
    meetings: [{ index: 0, tick: 10, trigger: "report", regrouped: true }],
    kills: [{ tick: 5, in_wave: false }],
    reports: [{ meeting: 0, corpse_age: 5 }],
    bodies_never_found: 0,
    moments: [],
    tripped: tripped ? [{ tripwire: "decided_by_a_vote_that_held_nothing", meeting: 0 }] : [],
  };
}

function member(seed: number) {
  return { seed, meetings: [0], kill_ticks: [] };
}

/** Three games: seed 3 and seed 7 on shelves, seed 26 kept off them. */
const PROFILE: GameProfileView = {
  viewModelVersion: "6",
  rubric_version: 2,
  era: "stage-b-r3", // was stage-b-r2
  manifest_key: "641b4254", // was 43b5ee45
  source_fingerprint: "sha256:0",
  seedset: "9p2i",
  stale: false,
  constants: {
    slow_burn_ticks: 20,
    wave_slack_ticks: 4,
    close_call_margin: 1,
    third_round_meetings: 3,
    down_to_the_wire_start: 3,
    runaway_share: "1/2",
    leak_p_level: "0.05",
    saturation_share: "3/4",
  },
  catalogue: [],
  pre_reveal: {
    shelves: [
      { name: "the_reporter_saw_it_happen", members: [member(7)] },
      { name: "double_kill", members: [member(3), member(7)] },
      { name: "a_third_round", members: [] },
    ],
    chips: [{ name: "an_eyewitness_voted_on_it", members: [{ seed: 7, meetings: [0] }] }],
    games: [facets(3), facets(7), facets(26, true)],
    tripwires: {
      readings: [
        {
          name: "decisive",
          tripwire: "decided_by_a_vote_that_held_nothing",
          governs: true,
          entries: [{ seed: 26, meeting: 0 }],
        },
      ],
      alibi_flags: 1,
      alibi_flags_evaluable: 0,
    },
  },
  reveal: {
    shelves: [
      { name: "caught_venting", members: [member(3)] },
      { name: "runaway", members: [member(7)] },
    ],
    decided_without_proof: {
      right: { name: "decided_without_proof_right", members: [member(7)] },
      wrong: { name: "decided_without_proof_wrong", members: [] },
    },
    games: [3, 7, 26].map((seed) => ({
      seed,
      ending: "IMPOSTOR_PARITY",
      distance: { counts: "tasks_left" as const, steps: 4, start: 14 },
      sabotage_starts: [],
      tasks_done: 10,
      tasks_assigned: 14,
      ejections: seed === 3 ? [] : [{ meeting: 0, right: seed === 7 }],
    })),
    class_tables: [],
  },
};

function meta(seed: number): ReplayMetadataView {
  return {
    game_id: `headless-seed-${seed}`,
    seed,
    total_ticks: 30 + seed,
    winner: "IMPOSTORS",
    winner_reason: "IMPOSTOR_PARITY",
    meeting_count: 1,
    total_cost_usd: 0,
    prompt_versions: {},
    created_at: null,
  };
}

const LIST = [3, 7, 26].map(meta);
const CARDS = buildCards(PROFILE, LIST);

const props: ReplayBrowserViewProps = {
  view: "highlights",
  status: "ready",
  error: null,
  cards: CARDS,
  totalCount: CARDS.length,
  filters: EMPTY_FILTERS,
  set: "9p2i",
  profile: PROFILE,
  profileMissing: false,
  reveal: false,
  onFiltersChange: () => {},
  onReveal: () => {},
  onOpen: () => {},
  onBrowseReplays: () => {},
};

function render(over: Partial<ReplayBrowserViewProps> = {}): string {
  return renderToStaticMarkup(<ReplayBrowserView {...props} {...over} />);
}

/** Each list's seeds that break seed order. */
function outOfSeedOrder(sections: readonly ReelSection[]): string[] {
  return sections
    .filter((section) => section.seeds.some((seed, i) => i > 0 && seed < section.seeds[i - 1]!))
    .map((section) => section.key);
}

/** The tripped games a shelf lists. */
function trippedOnShelves(sections: readonly ReelSection[], tripped: ReadonlySet<number>): number[] {
  return sections
    .filter((section) => section.kind !== "all")
    .flatMap((section) => section.seeds.filter((seed) => tripped.has(seed)));
}

describe("Browse by moment", () => {
  it("lists the shelves in the profile's order, games in seed order, then All games", () => {
    const sections = reelSections(PROFILE, false);
    expect(sections.map((section) => section.key)).toEqual([
      "shelf-the_reporter_saw_it_happen",
      "shelf-double_kill",
      "shelf-a_third_round",
      "all",
    ]);
    expect(sections.find((s) => s.key === "all")?.seeds).toEqual([3, 7, 26]);
    expect(outOfSeedOrder(sections)).toEqual([]);
    const html = render();
    expect(html).toContain(PROFILE_COPY.heading);
    expect(html.indexOf(shelfTitle("the_reporter_saw_it_happen"))).toBeLessThan(
      html.indexOf(shelfTitle("double_kill")),
    );
    expect(html.indexOf(shelfTitle("double_kill"))).toBeLessThan(html.indexOf(PROFILE_COPY.allGames));
    // A shelf that lists no game here renders nothing, so it states no count
    // that would be false of the whole set in a build that bakes a few games.
    expect(html).not.toContain(`aria-label="${shelfTitle("a_third_round")}"`);
    expect(html.replace(PICKER_COPY.highlightsIntro, "")).not.toMatch(
      /score|ordered by|ranked by/i,
    );
  });

  it("a reel sorted by how many shelves a game holds fails the order check (planted)", () => {
    const held = (seed: number) =>
      PROFILE.pre_reveal.shelves.filter((shelf) => shelf.members.some((m) => m.seed === seed)).length;
    const sorted = reelSections(PROFILE, false).map((section) => ({
      ...section,
      seeds: [...section.seeds].sort((a, b) => held(b) - held(a)),
    }));
    expect(outOfSeedOrder(sorted)).toContain("all");
  });

  it("keeps a tripped game off every shelf and labelled under All games", () => {
    const tripped = new Set([26]);
    for (const reveal of [false, true]) {
      expect(trippedOnShelves(reelSections(PROFILE, reveal), tripped)).toEqual([]);
    }
    const planted = {
      ...PROFILE,
      pre_reveal: {
        ...PROFILE.pre_reveal,
        shelves: [{ name: "double_kill", members: [member(3), member(26)] }],
      },
    };
    expect(trippedOnShelves(reelSections(planted, false), tripped)).toEqual([]);
    const unfiltered = reelSections(planted, false).map((section) =>
      section.key === "shelf-double_kill" ? { ...section, seeds: [3, 26] } : section,
    );
    expect(trippedOnShelves(unfiltered, tripped)).toEqual([26]);
    expect(render()).toContain("Kept off the shelves: at meeting 1");
  });

  it("renders no reveal-only shelf, name or count before the reveal", () => {
    const html = render();
    for (const name of [
      "caught_venting",
      "runaway",
      "decided_without_proof_right",
      "decided_without_proof_wrong",
    ]) {
      expect(html).not.toContain(shelfTitle(name));
    }
    expect(html).not.toContain(PROFILE_COPY.revealHeading);
    expect(html).not.toContain(PROFILE_COPY.pair.heading);
    const revealed = render({ reveal: true });
    expect(revealed).toContain(shelfTitle("caught_venting"));
    expect(revealed).toContain(PROFILE_COPY.revealHeading);
  });

  it("renders wrong beside right, an empty half saying so", () => {
    const html = render({ reveal: true });
    const wrong = html.indexOf(`aria-label="${shelfTitle("decided_without_proof_wrong")}"`);
    const right = html.indexOf(`aria-label="${shelfTitle("decided_without_proof_right")}"`);
    expect(wrong).toBeGreaterThan(-1);
    expect(right).toBeGreaterThan(wrong);
    expect(html).toContain(PROFILE_COPY.pair.emptyHalf);
    expect(html).toContain("A wrong call on believable evidence is part of the game.");
  });

  it("lists each half's games under that half's own heading", () => {
    // Seed 8 is the only game the table got wrong, seed 7 the only one it got
    // right, and neither half is empty.
    const paired: GameProfileView = {
      ...PROFILE,
      pre_reveal: { ...PROFILE.pre_reveal, games: [facets(3), facets(7), facets(8), facets(26, true)] },
      reveal: {
        ...PROFILE.reveal,
        decided_without_proof: {
          right: { name: "decided_without_proof_right", members: [member(7)] },
          wrong: { name: "decided_without_proof_wrong", members: [member(8)] },
        },
      },
    };
    const cards = buildCards(paired, [3, 7, 8, 26].map(meta));
    const html = render({ profile: paired, cards, totalCount: cards.length, reveal: true });
    const wrongAt = html.indexOf(`aria-label="${shelfTitle("decided_without_proof_wrong")}"`);
    const rightAt = html.indexOf(`aria-label="${shelfTitle("decided_without_proof_right")}"`);
    const allAt = html.indexOf(`aria-label="${PROFILE_COPY.allGames}"`);
    expect(wrongAt).toBeGreaterThan(-1);
    expect(rightAt).toBeGreaterThan(wrongAt);
    expect(allAt).toBeGreaterThan(rightAt);
    const wrongHalf = html.slice(wrongAt, rightAt);
    const rightHalf = html.slice(rightAt, allAt);
    const opens = (region: string, seed: number) =>
      region.split(`aria-label="Open replay seed ${seed}"`).length - 1;
    expect([opens(wrongHalf, 8), opens(wrongHalf, 7)]).toEqual([1, 0]);
    expect([opens(rightHalf, 7), opens(rightHalf, 8)]).toEqual([1, 0]);
    expect(html).not.toContain(PROFILE_COPY.pair.emptyHalf);
  });

  it("a wrong half listed alone fails the pair check (planted)", () => {
    // The two halves are one block: wrong immediately followed by right.
    const together = (sections: readonly ReelSection[]) => {
      const names = sections.map((section) => section.name);
      const wrong = names.indexOf("decided_without_proof_wrong");
      return wrong > -1 && names[wrong + 1] === "decided_without_proof_right";
    };
    expect(together(reelSections(PROFILE, true))).toBe(true);
    const alone = reelSections(PROFILE, true).filter(
      (section) => section.name !== "decided_without_proof_right",
    );
    expect(together(alone)).toBe(false);
  });

  it("joins every replay to its profile entry and keeps the eyewitness chip on its meeting", () => {
    const profiles = cardProfiles(PROFILE);
    expect(profiles.get(7)?.shelves).toEqual(["the_reporter_saw_it_happen", "double_kill"]);
    expect(profiles.get(7)?.revealShelves).toEqual(["runaway", "decided_without_proof_right"]);
    expect(profiles.get(7)?.eyewitness).toEqual([0]);
    expect(profiles.get(26)?.shelves).toEqual([]);
    expect(cardProfiles({ ...PROFILE, stale: true }).size).toBe(0);
    expect(cardProfiles(null).size).toBe(0);
  });
});

describe("the no-profile and stale states", () => {
  // The absent state names no set as the one expected to ship a profile and
  // states no per-set count, so it reads true on any set served without one.
  const assertSetNeutral = (text: string) => {
    expect(text).not.toContain("4p1i");
    expect(text).not.toMatch(/fixture/i);
    expect(text).not.toMatch(/ships one|which ships|is scored|default 9p2i/i);
    expect(text).not.toMatch(/\b\d+ of (?:its )?\d+\b/);
    expect(text).not.toMatch(/median \d+ ticks/);
  };

  it("words a set without a profile without naming another set", () => {
    for (const view of ["replays", "highlights"] as const) {
      for (const reveal of [false, true]) {
        const html = render({
          view,
          reveal,
          profile: null,
          profileMissing: true,
          cards: buildCards(null, LIST),
        });
        expect(html).toContain("ships no game-shape profile");
        expect(html).toContain("9p2i");
        assertSetNeutral(html);
      }
    }
    expect(DASHBOARD_COPY.momentsAbsentBody).toContain("ships no game-shape profile");
    assertSetNeutral(DASHBOARD_COPY.momentsAbsentBody);
    expect(DASHBOARD_COPY.momentsAbsentBody).not.toContain("9p2i");
  });

  it("a set named as the profiled one or a per-set count fails the neutrality check (planted)", () => {
    // Each line breaks one rule of the check, so a rule dropped from it lets
    // its line through.
    for (const planted of [
      "This set ships no game-shape profile; the four-player 4p1i does the same.",
      "This set ships no game-shape profile, as a fixture would.",
      "This set ships no game-shape profile; the other one ships one.",
      "This set ships no game-shape profile, unlike the set which ships it.",
      "This set ships no game-shape profile; the nine-player set is scored.",
      "This set ships no game-shape profile, unlike the default 9p2i.",
      "This set ships no game-shape profile; 12 of 50 games hold a shelf elsewhere.",
      "This set ships no game-shape profile; its games run a median 41 ticks.",
    ]) {
      expect(() => assertSetNeutral(planted)).toThrow();
    }
  });

  it("keeps the stale and absent states distinct", () => {
    const stale = render({ profile: { ...PROFILE, stale: true } });
    expect(stale).toContain(PROFILE_COPY.staleTitle);
    expect(stale).not.toContain("ships no game-shape profile");
    const absent = render({ profile: null, profileMissing: true });
    expect(absent).toContain(PROFILE_COPY.absentTitle);
    expect(absent).toContain(PROFILE_COPY.browseReplays);
    expect(absent).not.toContain(PROFILE_COPY.staleTitle);
  });

  it("keeps a replay card factual without a profile", () => {
    const html = render({ view: "replays", profile: null, profileMissing: true, cards: buildCards(null, LIST) });
    expect(html).toContain("33 ticks");
    expect(html).toContain("Open replay seed 3");
  });
});

describe("the outcome filters", () => {
  it("act only once outcomes are revealed", () => {
    const byWinner = { ...EMPTY_FILTERS, winner: "CREWMATES" as const };
    for (const card of CARDS) {
      expect(matchesFilters(card, byWinner, false)).toBe(true);
      expect(matchesFilters(card, byWinner, true)).toBe(false);
    }
  });

  it("read that someone was voted out, from the profile's reveal facets", () => {
    const voted = { ...EMPTY_FILTERS, hasEjection: true };
    const kept = CARDS.filter((card) => matchesFilters(card, voted, true)).map((c) => c.seed);
    expect(kept).toEqual([7, 26]);
    expect(CARDS.every((card) => matchesFilters(card, voted, false))).toBe(true);
    const bare = buildCards(null, LIST);
    expect(bare.some((card) => matchesFilters(card, voted, true))).toBe(false);
  });

  it("keep two URL keys, and the retired score and win-shape keys read nothing", () => {
    expect(parseFilterParams("?winner=IMPOSTORS&hasEjection=1&scoreBucket=high&winShape=x")).toEqual({
      winner: "IMPOSTORS",
      hasEjection: true,
    });
    expect(writeFilterParams("?set=9p2i", { winner: "CREWMATES", hasEjection: true })).toBe(
      "?set=9p2i&winner=CREWMATES&hasEjection=1",
    );
    expect(writeFilterParams("?set=9p2i&winner=CREWMATES", EMPTY_FILTERS)).toBe("?set=9p2i");
  });

  it("let every game through once revealed while the ejection filter is off", () => {
    for (const card of CARDS) {
      expect(matchesFilters(card, EMPTY_FILTERS, true)).toBe(true);
    }
  });
});

/** The first `<input>` element in a rendered tree, read without a DOM. */
function firstInput(node: ReactNode): { onChange: (event: unknown) => void } | null {
  if (Array.isArray(node)) {
    for (const child of node as readonly ReactNode[]) {
      const hit = firstInput(child);
      if (hit !== null) return hit;
    }
    return null;
  }
  if (!isValidElement(node)) return null;
  const props = node.props as { children?: ReactNode; onChange?: (event: unknown) => void };
  if (node.type === "input" && props.onChange !== undefined) {
    return { onChange: props.onChange };
  }
  return firstInput(props.children);
}

describe("the ejection filter", () => {
  const bar = (filters: ReplayFilterState, onChange: (next: ReplayFilterState) => void) => ({
    filters,
    onChange,
    set: "9p2i",
    resultCount: 2,
    totalCount: 3,
    reveal: true,
    onReveal: () => {},
  });

  it("is a checkbox in plain words that shows its state and can be disabled", () => {
    const on = { ...EMPTY_FILTERS, hasEjection: true };
    const html = renderToStaticMarkup(<ReplayFilters {...bar(on, () => {})} disabled />);
    expect(html).toContain(
      `<input type="checkbox" class="accent-ink-900" disabled="" checked=""/>${PROFILE_COPY.filterVotedOut}`,
    );
    const off = renderToStaticMarkup(<ReplayFilters {...bar(EMPTY_FILTERS, () => {})} />);
    expect(off).toContain('<input type="checkbox" class="accent-ink-900"/>');
  });

  it("turns on when ticked", () => {
    const seen: ReplayFilterState[] = [];
    const input = firstInput(ReplayFilters(bar(EMPTY_FILTERS, (next) => seen.push(next))));
    expect(input).not.toBeNull();
    input?.onChange({ target: { checked: true } });
    expect(seen).toEqual([{ ...EMPTY_FILTERS, hasEjection: true }]);
  });
});

describe("what each list renders", () => {
  const opens = (html: string, seed: number) =>
    html.split(`aria-label="Open replay seed ${seed}"`).length - 1;

  it("describes each shelf and lists its games as cards", () => {
    const html = render();
    expect(html).toContain(
      `<p class="text-sm text-ink-700">${PROFILE_COPY.shelves.double_kill.description}</p>`,
    );
    // Seed 7: the reporter shelf, double kill and All games; seed 3: double kill and All games.
    expect(opens(html, 7)).toBe(3);
    expect(opens(html, 3)).toBe(2);
    expect(html).toContain(`<p class="text-sm text-ink-700">${PROFILE_COPY.allGamesNote}</p>`);
  });

  it("heads the revealed half and the pair, and lists the pair's games", () => {
    const html = render({ reveal: true });
    expect(html).toContain(`>${PROFILE_COPY.revealHeading}</h3>`);
    expect(html).toContain(`>${PROFILE_COPY.revealNote.replace(/'/g, "&#x27;")}</p>`);
    expect(html).toContain(`>${PROFILE_COPY.pair.heading}</h3>`);
    expect(html).toContain(`>${PROFILE_COPY.pair.note}</p>`);
    // Seed 7 adds runaway and the right half once revealed.
    expect(opens(html, 7)).toBe(5);
  });

  it("puts the reveal-only shelves in the profile's order before the pair", () => {
    expect(reelSections(PROFILE, true).map((section) => section.key)).toEqual([
      "shelf-the_reporter_saw_it_happen",
      "shelf-double_kill",
      "shelf-a_third_round",
      "reveal-caught_venting",
      "reveal-runaway",
      "reveal-decided_without_proof_wrong",
      "reveal-decided_without_proof_right",
      "all",
    ]);
  });

  it("lists a shelf's games in seed order whatever order they are served in", () => {
    const shuffled = {
      ...PROFILE,
      pre_reveal: {
        ...PROFILE.pre_reveal,
        shelves: [{ name: "double_kill", members: [member(7), member(3)] }],
      },
    };
    expect(reelSections(shuffled, false)[0]?.seeds).toEqual([3, 7]);
  });

  it("names the region, the load failure and the stale state in their own words", () => {
    expect(render()).toContain(`<section aria-label="${PROFILE_COPY.heading}"`);
    expect(render({ view: "replays" })).toContain('<section aria-label="Replay browser"');
    expect(render({ status: "error", error: "boom" })).toContain(`${PROFILE_COPY.loadError} boom`);
    expect(render({ profile: { ...PROFILE, stale: true } })).toContain(
      `<p>${PROFILE_COPY.staleBody}</p>`,
    );
    expect(render({ status: "loading", set: null })).toContain(PROFILE_COPY.loading);
    expect(render()).toContain(`>${PROFILE_COPY.heading}</h2>`);
    expect(render({ profile: { ...PROFILE, stale: true } })).toContain(
      `>${PROFILE_COPY.browseReplays}</button>`,
    );
    expect(render({ view: "replays", cards: [], totalCount: 0 })).toContain(
      "No replays in the configured replay directory.",
    );
  });
});

describe("the profile request and the browser's status", () => {
  const ready = { status: "ready", profile: PROFILE, error: null } as const;
  const loading = { status: "loading", profile: null, error: null } as const;
  const state = (over: Partial<Parameters<typeof browserState>[0]>) =>
    browserState({
      view: "highlights",
      seedSet: "9p2i",
      availableSetsError: null,
      profile: ready,
      replayList: LIST,
      replayListError: null,
      ...over,
    });

  it("settles ready on a profile, absent on a 404 and failed otherwise", async () => {
    expect(await settledProfile(Promise.resolve(PROFILE))).toEqual(ready);
    const missing = new ApiError(404, "/eval/game-profile", "not found");
    expect(await settledProfile(Promise.reject(missing))).toEqual({
      status: "absent",
      profile: null,
      error: null,
    });
    expect(await settledProfile(Promise.reject(new Error("version 7")))).toEqual({
      status: "error",
      profile: null,
      error: "version 7",
    });
    expect(await settledProfile(Promise.reject("plain"))).toEqual({
      status: "error",
      profile: null,
      error: "plain",
    });
  });

  it("reads loading until a request made for the active set settles", () => {
    expect(activeProfile(null, "9p2i")).toEqual(loading);
    expect(activeProfile({ set: "9p2i", load: ready }, "9p2i")).toBe(ready);
    expect(activeProfile({ set: "9p2i", load: ready }, "4p1i")).toEqual(loading);
    expect(activeProfile({ set: "9p2i", load: ready }, null)).toEqual(loading);
  });

  it("drives the reel by the sets, the profile and the replay list, in that order", () => {
    expect(state({})).toEqual({ status: "ready", error: null });
    expect(state({ seedSet: null, availableSetsError: "sets down" })).toEqual({
      status: "error",
      error: "sets down",
    });
    expect(state({ availableSetsError: "sets down" })).toEqual({ status: "ready", error: null });
    expect(
      state({ profile: { status: "error", profile: null, error: "boom" }, replayListError: "list" }),
    ).toEqual({ status: "error", error: "boom" });
    expect(state({ replayListError: "list down" })).toEqual({ status: "error", error: "list down" });
    expect(state({ profile: loading })).toEqual({ status: "loading", error: null });
    expect(state({ replayList: null })).toEqual({ status: "loading", error: null });
  });

  it("drives the Replays browser by the replay list alone", () => {
    const replays = (over: Partial<Parameters<typeof browserState>[0]>) =>
      state({ view: "replays", ...over });
    expect(replays({ profile: loading })).toEqual({ status: "ready", error: null });
    expect(replays({ profile: { status: "error", profile: null, error: "boom" } })).toEqual({
      status: "ready",
      error: null,
    });
    expect(replays({ replayList: null })).toEqual({ status: "loading", error: null });
    expect(replays({ replayListError: "list down" })).toEqual({ status: "error", error: "list down" });
  });
});
