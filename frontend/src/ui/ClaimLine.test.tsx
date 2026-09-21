// An alibi is a ROUTE, and the spectator serves exactly the surface each claim
// arrived on. These cover both: a route claim renders its legs in order (the
// seed-41 shape, where the envelope render used to show only ENGINEERING and
// hide the three rooms the speaker itemised), and a claim recorded before the
// change — the flat one-room envelope every committed recording carries —
// renders exactly as it always did.

import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { StatementClaimView } from "../types/api";
import { ClaimLine } from "./ClaimLine";

const route: StatementClaimView = {
  type: "alibi",
  subject: "p-9",
  route: [
    { room: "ENGINEERING", from_tick: 12, to_tick: 12 },
    { room: "EAST_HALL", from_tick: 13, to_tick: 13 },
    { room: "ADMIN", from_tick: 14, to_tick: 14 },
    { room: "WEST_HALL", from_tick: 15, to_tick: 15 },
  ],
  evidence: ["saw p-7 in ENGINEERING @ tick 12"],
};

const envelope: StatementClaimView = {
  type: "alibi",
  subject: "p-9",
  from_tick: 12,
  to_tick: 15,
  room: "ENGINEERING",
  evidence: [],
};

describe("alibi routes on the transcript", () => {
  it("renders every leg of a route, in order", () => {
    const html = renderToStaticMarkup(<ClaimLine claim={route} />);
    for (const room of ["ENGINEERING", "EAST_HALL", "ADMIN", "WEST_HALL"]) {
      expect(html).toContain(room);
    }
    expect(html).toContain("ticks 14–14");
    expect(html).toContain("saw p-7 in ENGINEERING @ tick 12");
    expect(html.indexOf("EAST_HALL")).toBeLessThan(html.indexOf("ADMIN"));
  });

  it("renders a recorded one-room envelope the way it always read", () => {
    const html = renderToStaticMarkup(<ClaimLine claim={envelope} />);
    expect(html).toContain("in ENGINEERING (ticks 12–15)");
    expect(html).not.toContain("→");
    expect(html).not.toContain("no route stated");
  });
});
