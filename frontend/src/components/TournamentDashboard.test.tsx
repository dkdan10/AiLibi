import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { MomentsPanel, activeMoments, momentsState, type ProfileState } from "./TournamentDashboard";
import { ApiError } from "../api/client";
import { shelfTitle } from "./HighlightCard";
import { DASHBOARD_COPY } from "../lib/copy";
import type { GameFacetsView, GameProfileView } from "../types/api";

function facets(seed: number, meetings: number, kills: number, unfound: number): GameFacetsView {
  return {
    seed,
    ticks: 40,
    meetings: Array.from({ length: meetings }, (_, index) => ({
      index,
      tick: 10 * (index + 1),
      trigger: "report" as const,
      regrouped: true,
    })),
    kills: Array.from({ length: kills }, (_, index) => ({ tick: 3 + index, in_wave: false })),
    reports: [],
    bodies_never_found: unfound,
    moments: [],
    tripped: [],
  };
}

function member(seed: number) {
  return { seed, meetings: [0], kill_ticks: [] };
}

const VIEW: GameProfileView = {
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
      { name: "the_reporter_saw_it_happen", members: [member(1), member(2), member(3)] },
      { name: "double_kill", members: [member(2)] },
    ],
    chips: [],
    games: [facets(1, 1, 2, 0), facets(2, 2, 2, 1), facets(3, 2, 4, 1)],
    tripwires: { readings: [] },
  },
  reveal: {
    shelves: [{ name: "caught_venting", members: [member(1), member(3)] }],
    decided_without_proof: {
      right: { name: "decided_without_proof_right", members: [member(3)] },
      wrong: { name: "decided_without_proof_wrong", members: [] },
    },
    games: [],
  },
};

function panel(profile: ProfileState, reveal = false): string {
  return renderToStaticMarkup(<MomentsPanel profile={profile} reveal={reveal} />);
}

/** The text of every row of the panel's tables, cell by cell. */
function rows(html: string): string[] {
  return [...html.matchAll(/<tr>(.*?)<\/tr>/g)].map((match) =>
    [...(match[1] ?? "").matchAll(/<td[^>]*>(.*?)<\/td>/g)].map((cell) => cell[1]).join(" | "),
  );
}

const REVEAL_ONLY = [
  "caught_venting",
  "decided_without_proof_wrong",
  "decided_without_proof_right",
] as const;

describe("the moments panel", () => {
  it("lists each shelf before the reveal with the number of games it lists", () => {
    const html = panel({ status: "ready", view: VIEW });
    expect(html).toContain(DASHBOARD_COPY.momentsTitle);
    const listed = rows(html);
    expect(listed).toContain(`${shelfTitle("the_reporter_saw_it_happen")} | 3`);
    expect(listed).toContain(`${shelfTitle("double_kill")} | 1`);
  });

  it("lists each facet's games per value, in value order", () => {
    const listed = rows(panel({ status: "ready", view: VIEW }));
    // Meetings per game: one game with 1, two with 2; kills: two with 2, one with 4.
    expect(listed).toEqual(
      expect.arrayContaining(["1 | 1", "2 | 2", "4 | 1", "0 | 1"]),
    );
    const html = panel({ status: "ready", view: VIEW });
    expect(html).toContain(DASHBOARD_COPY.momentsFacetMeetings);
    expect(html).toContain(DASHBOARD_COPY.momentsFacetKills);
    expect(html).toContain(DASHBOARD_COPY.momentsFacetUnfound);
    expect(html.split(`>${DASHBOARD_COPY.momentsGamesColumn}</th>`).length - 1).toBeGreaterThan(1);
    expect(html).toContain(`<th class="font-normal">${DASHBOARD_COPY.momentsShelfColumn}</th>`);
    expect(html).toContain(`<th class="font-normal">${DASHBOARD_COPY.momentsValueColumn}</th>`);
  });

  it("shows no reveal-only shelf, name or size before the reveal", () => {
    const html = panel({ status: "ready", view: VIEW });
    for (const name of REVEAL_ONLY) {
      expect(html).not.toContain(shelfTitle(name));
    }
    expect(html).toContain(DASHBOARD_COPY.momentsRevealHint);
  });

  it("shows them once revealed, wrong beside right, so the check above can fail", () => {
    const html = panel({ status: "ready", view: VIEW }, true);
    const listed = rows(html);
    expect(listed).toContain(`${shelfTitle("caught_venting")} | 2`);
    expect(listed).toContain(`${shelfTitle("decided_without_proof_wrong")} | 0`);
    expect(listed).toContain(`${shelfTitle("decided_without_proof_right")} | 1`);
    expect(html.indexOf(shelfTitle("decided_without_proof_wrong"))).toBeLessThan(
      html.indexOf(shelfTitle("decided_without_proof_right")),
    );
    expect(html).not.toContain(DASHBOARD_COPY.momentsRevealHint);
  });

  it("draws no mean, no bucket and no link", () => {
    for (const reveal of [false, true]) {
      const html = panel({ status: "ready", view: VIEW }, reveal).replace(
        DASHBOARD_COPY.momentsDescription,
        "",
      );
      expect(html).not.toMatch(/<a\b/);
      expect(html).not.toMatch(/\bmean\b|\bmedian\b|\bLow\b|\bMed\b|\bHigh\b|score/i);
    }
  });

  it("renders the absent, stale, loading and error states in their own words", () => {
    const absent = panel({ status: "absent" });
    expect(absent).toContain(DASHBOARD_COPY.momentsAbsentTitle);
    expect(absent).toContain(DASHBOARD_COPY.momentsAbsentBody);
    const stale = panel({ status: "ready", view: { ...VIEW, stale: true } });
    expect(stale).toContain(DASHBOARD_COPY.momentsStaleCaveat);
    expect(stale).toContain(`>${DASHBOARD_COPY.momentsStaleCaveatTitle}</p>`);
    expect(rows(stale)).toEqual([]);
    expect(panel({ status: "loading" })).toContain(DASHBOARD_COPY.momentsLoading);
    const error = panel({ status: "error", message: "profile request failed (status 500)" });
    expect(error).toContain(DASHBOARD_COPY.momentsError.replace("'", "&#x27;"));
    expect(error).toContain("status 500");
  });
});

describe("the panel's request", () => {
  it("is ready on a profile, absent on a 404, and an error by status otherwise", async () => {
    expect(await momentsState(Promise.resolve(VIEW))).toEqual({ status: "ready", view: VIEW });
    const missing = new ApiError(404, "/eval/game-profile", "not found");
    expect(await momentsState(Promise.reject(missing))).toEqual({ status: "absent" });
    const failed = new ApiError(500, "/eval/game-profile", "<html>a server page</html>");
    expect(await momentsState(Promise.reject(failed))).toEqual({
      status: "error",
      message: "profile request failed (status 500)",
    });
    expect(await momentsState(Promise.reject(new Error("version 7")))).toEqual({
      status: "error",
      message: "version 7",
    });
    expect(await momentsState(Promise.reject("plain"))).toEqual({ status: "error", message: "plain" });
  });

  it("reads loading until the current request settles, after a set switch or a refresh", () => {
    const ready: ProfileState = { status: "ready", view: VIEW };
    expect(activeMoments(null, "9p2i#0")).toEqual({ status: "loading" });
    expect(activeMoments({ request: "9p2i#0", state: ready }, "9p2i#0")).toBe(ready);
    expect(activeMoments({ request: "9p2i#0", state: ready }, "4p1i#0")).toEqual({ status: "loading" });
    expect(activeMoments({ request: "9p2i#0", state: ready }, "9p2i#1")).toEqual({ status: "loading" });
  });
});
