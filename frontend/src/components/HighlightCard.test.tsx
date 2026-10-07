import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import {
  HighlightCard,
  shelfTitle,
  tripwireLabel,
  type CardProfile,
  type HighlightCardData,
} from "./HighlightCard";
import { PROFILE_COPY } from "../lib/copy";

const base: HighlightCardData = {
  key: "partial",
  gameId: "headless-seed-42",
  seed: 42,
  winner: null,
  totalTicks: 2,
  profile: null,
};

/** Seed 19's shape: three report meetings, four kills, one in a regroup's wave. */
const PROFILE: CardProfile = {
  facets: {
    seed: 19,
    ticks: 44,
    meetings: [
      { index: 0, tick: 12, trigger: "report", regrouped: true },
      { index: 1, tick: 31, trigger: "report", regrouped: true },
      { index: 2, tick: 44, trigger: "report", regrouped: false },
    ],
    kills: [
      { tick: 7, in_wave: false },
      { tick: 9, in_wave: false },
      { tick: 20, in_wave: true },
      { tick: 43, in_wave: false },
    ],
    reports: [{ meeting: 0, corpse_age: 3 }],
    bodies_never_found: 1,
    moments: ["struck_after_the_regroup"],
    tripped: [],
  },
  revealFacets: {
    seed: 19,
    ending: "CREWMATE_EJECT",
    distance: { counts: "kills_short_of_parity", steps: 2, start: 5 },
    sabotage_starts: [42],
    tasks_done: 12,
    tasks_assigned: 14,
    ejections: [
      { meeting: 0, right: true },
      { meeting: 2, right: true },
    ],
  },
  shelves: ["the_reporter_saw_it_happen", "slow_burn", "a_third_round"],
  revealShelves: ["caught_venting", "one_line_two_readings", "decided_without_proof_right"],
  eyewitness: [2],
};

const profiled: HighlightCardData = { ...base, seed: 19, gameId: "headless-seed-19", profile: PROFILE };

function card(data: HighlightCardData, reveal: boolean): string {
  return renderToStaticMarkup(<HighlightCard data={data} reveal={reveal} onOpen={() => undefined} />);
}

describe("recording endings on replay cards", () => {
  it.each([
    ["aborted", "Aborted"],
    ["tick_limited", "Tick limit"],
    ["unfinished", "Unfinished"],
    [undefined, "Unfinished"],
  ] as const)("labels %s without inventing a winner", (completionStatus, label) => {
    const data = { ...base, completionStatus };
    const revealed = card(data, true);
    expect(revealed).toContain(label);
    expect(revealed).not.toMatch(/Crew win|Impostor win|Outcome —/);

    const hidden = card(data, false);
    expect(hidden).toContain("Outcome hidden");
    expect(hidden).not.toContain(label);
  });

  it.each([
    ["CREWMATES", "Crew win"],
    ["IMPOSTORS", "Impostor win"],
  ] as const)("preserves the recorded %s outcome", (winner, label) => {
    const html = card({ ...base, winner }, true);
    expect(html).toContain(label);
    expect(html).not.toContain("Unfinished");
  });
});

/** Every reveal-only word a card can carry, for one game's profile entry. */
function revealOnlyWords(profile: CardProfile): readonly string[] {
  return [
    ...profile.revealShelves.map(shelfTitle),
    "Ended:",
    "tasks done",
    "the vote was",
    "A sabotage was in play",
  ];
}

function leakedRevealWords(html: string, profile: CardProfile): readonly string[] {
  return revealOnlyWords(profile).filter((word) => html.includes(word));
}

describe("a card's shelves and facets", () => {
  it("shows the shelves before the reveal, the chip and the facets, and no score", () => {
    const html = card(profiled, false);
    for (const name of PROFILE.shelves) {
      expect(html).toContain(shelfTitle(name));
    }
    expect(html).toContain("An eyewitness voted on it at meeting 3");
    expect(html).toContain("44 ticks");
    expect(html).toContain("3 meetings · 3 reported, 0 called");
    expect(html).toContain("4 kills · 1 soon after a regroup");
    expect(html).toContain("1 bodies never found");
    expect(html).toContain('aria-label="Open replay seed 19"');
    expect(html).not.toMatch(/score|\/100|rank/i);
  });

  it("renders no reveal-only shelf, ending or annotation unrevealed", () => {
    expect(leakedRevealWords(card(profiled, false), PROFILE)).toEqual([]);
  });

  it("shows them once revealed, so the unrevealed check can fail (planted)", () => {
    const html = card(profiled, true);
    expect(leakedRevealWords(html, PROFILE)).toEqual(revealOnlyWords(PROFILE));
    expect(html).toContain("Ended: the crew voted out every impostor");
    expect(html).toContain("The impostors were 2 kills from matching the crew; they started 5 away.");
    expect(html).toContain("12 of 14 tasks done");
    expect(html).toContain("A sabotage was in play from tick 42.");
    expect(html).toContain("Meeting 1: the vote was right");
    expect(html).toContain("Meeting 3: the vote was right");
  });

  it("labels a game a tripwire keeps off the shelves, in plain words", () => {
    const tripped: HighlightCardData = {
      ...profiled,
      profile: {
        ...PROFILE,
        shelves: [],
        revealShelves: [],
        facets: {
          ...PROFILE.facets,
          tripped: [{ tripwire: "decided_by_a_vote_that_held_nothing", meeting: 2 }],
        },
      },
    };
    const html = card(tripped, false);
    expect(html).toContain(
      tripwireLabel("decided_by_a_vote_that_held_nothing", 2).replace(/'/g, "&#x27;"),
    );
    expect(html).toContain("Kept off the shelves: at meeting 3 a player was voted out");
  });

  it("refuses a shelf, a tripwire or an ending this build has no words for", () => {
    expect(() => shelfTitle("a_shelf_from_the_future")).toThrow(/no words for/);
    expect(() => tripwireLabel("a_tripwire_from_the_future", 0)).toThrow(/no words for/);
    const ending = {
      ...profiled,
      profile: { ...PROFILE, revealFacets: { ...PROFILE.revealFacets!, ending: "IMPOSTOR_TIMEOUT" } },
    };
    expect(() => card(ending, true)).toThrow(/no words for: IMPOSTOR_TIMEOUT/);
  });

  it("keeps a game with no profile entry factual", () => {
    const html = card(base, false);
    expect(html).toContain("2 ticks");
    expect(html).not.toContain(PROFILE_COPY.facets.timeline);
  });
});
