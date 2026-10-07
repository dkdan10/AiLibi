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
    expect(html).toContain("Meeting 1: the body was found 3 ticks after the kill");
    expect(html).toContain(`title="${PROFILE_COPY.chip.description}"`);
    expect(html).toContain('aria-label="Open replay seed 19"');
    expect(html).not.toMatch(/score|\/100|rank/i);
  });

  it("counts the meetings by what opened them", () => {
    const opened = (meetings: CardProfile["facets"]["meetings"]) =>
      card({ ...profiled, profile: { ...PROFILE, facets: { ...PROFILE.facets, meetings } } }, false);
    const two = opened([
      { index: 0, tick: 12, trigger: "report", regrouped: true },
      { index: 1, tick: 31, trigger: "emergency", regrouped: true },
    ]);
    expect(two).toContain("2 meetings · 1 reported, 1 called");
    expect(two).toContain('title="Meeting 1 at tick 12"');
    expect(two).toContain('title="Meeting 2 at tick 31"');
    // One report and two called meetings, so a count of the called meetings
    // as reported reads differently from the true line.
    const three = opened([
      { index: 0, tick: 12, trigger: "emergency", regrouped: true },
      { index: 1, tick: 31, trigger: "report", regrouped: true },
      { index: 2, tick: 40, trigger: "emergency", regrouped: false },
    ]);
    expect(three).toContain("3 meetings · 1 reported, 2 called");
    expect(three).toContain('title="Meeting 3 at tick 40"');
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
    // A dashed box, the same mark a hidden-until-revealed chip carries.
    expect(html).toContain(
      '<p class="rounded-md border border-dashed border-ink-500 bg-paper-1 px-2 py-1 text-xs text-ink-700">' +
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

describe("the card's timeline", () => {
  const share = (tick: number) => `left:${Math.min(100, (tick / 44) * 100)}%`;

  it("is one labelled image with a mark per meeting and per kill at its tick's share", () => {
    const html = card(profiled, false);
    expect(html).toContain(
      `role="img" aria-label="${PROFILE_COPY.facets.timeline}" class="relative h-4 w-full rounded-sm bg-paper-3 shadow-data"`,
    );
    for (const meeting of PROFILE.facets.meetings) {
      expect(html).toContain(
        `title="Meeting ${meeting.index + 1} at tick ${meeting.tick}" class="absolute top-0 h-4 w-0.5 bg-ink-900" style="${share(meeting.tick)}"`,
      );
    }
    // A kill in a regroup's wave is a hollow mark, any other kill a solid one.
    const mark = "absolute top-1 h-2 w-2 -translate-x-1 rounded-full border-2 border-ink-700";
    for (const kill of PROFILE.facets.kills) {
      const fill = kill.in_wave ? "bg-paper-0" : "bg-ink-700";
      expect(html).toMatch(
        new RegExp(`title="Kill at tick ${kill.tick}[^"]*" class="${mark} ${fill}" style="${share(kill.tick)}"`),
      );
    }
  });

  it("draws a reveal-only chip dashed and a chip before the reveal solid", () => {
    const html = card(profiled, true);
    const chip = "rounded-pill border-2 px-2 py-0.5 font-mono text-3xs font-medium text-ink-900";
    expect(html).toContain(`<li class="${chip} border-ink-900 bg-paper-2">${shelfTitle("slow_burn")}</li>`);
    expect(html).toContain(
      `<li class="${chip} border-dashed border-ink-500 bg-paper-1">${shelfTitle("caught_venting")}</li>`,
    );
  });

  it("has words for every ending a game can record", () => {
    // The engine's win results, then its stop reasons.
    for (const ending of [
      "CREWMATE_EJECT",
      "CREWMATE_TASKS",
      "IMPOSTOR_PARITY",
      "IMPOSTOR_SABOTAGE",
      "TICK_BUDGET_REACHED",
      "MEETING_PHASE_REACHED",
    ]) {
      const ended: HighlightCardData = {
        ...profiled,
        profile: { ...PROFILE, revealFacets: { ...PROFILE.revealFacets!, ending } },
      };
      expect(card(ended, true)).toContain("Ended: ");
    }
  });

  it("lists the eyewitness chip on a game that sits on no shelf", () => {
    const chipOnly: HighlightCardData = {
      ...profiled,
      profile: { ...PROFILE, shelves: [], revealShelves: [] },
    };
    const html = card(chipOnly, false);
    expect(html).toContain(`aria-label="${PROFILE_COPY.cardShelves}"`);
    expect(html).toContain("An eyewitness voted on it at meeting 3");
  });
});
