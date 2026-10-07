import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import {
  ReplayBrowserView,
  buildCards,
  cardProfiles,
  matchesFilters,
  reelSections,
  type ReelSection,
  type ReplayBrowserViewProps,
} from "./ReplayPicker";
import { EMPTY_FILTERS, parseFilterParams, writeFilterParams } from "./ReplayFilters";
import { shelfTitle } from "./HighlightCard";
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
  era: "stage-b-r2",
  manifest_key: "43b5ee45",
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
    expect(html).toContain(PROFILE_COPY.emptyShelf);
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
  it("words a set without a profile without naming another set", () => {
    const assertSetNeutral = (text: string) => {
      expect(text).not.toContain("4p1i");
      expect(text).not.toMatch(/fixture/i);
      expect(text).not.toMatch(/ships one|which ships|default 9p2i/i);
      expect(text).not.toMatch(/\b\d+ of (?:its )?\d+\b/);
    };
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
});
