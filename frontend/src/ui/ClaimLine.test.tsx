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

describe("an accusation's confidence on the transcript", () => {
  it.each([
    [0.73, "High"],
    [0.72, "Med"],
    [0.35, "Low"],
  ])("reads %s as %s, the number on hover and for a screen reader", (confidence, word) => {
    const claim: StatementClaimView = { type: "accusation", against: "p-4", confidence, reason: "seen near the body" };
    const html = renderToStaticMarkup(<ClaimLine claim={claim} />);
    const number = confidence.toFixed(2);
    expect(html).toContain(`<span data-bucket="true" title="${number}">confidence ${word}<span class="sr-only">, ${number}</span></span>`);
    // The face, with what only a screen reader reads set aside, carries no figure.
    const face = html.replace(/<span class="sr-only">[^<]*<\/span>/g, "").replace(/<!--[\s\S]*?-->/g, "").replace(/<[^>]*>/g, "");
    expect(face).toBe(`accusation · against p-4 (confidence ${word}) — seen near the body`);
  });
});
