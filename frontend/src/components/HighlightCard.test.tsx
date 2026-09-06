import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { HighlightCard, type HighlightCardData } from "./HighlightCard";

const base: HighlightCardData = {
  key: "partial",
  gameId: "headless-seed-42",
  seed: 42,
  winner: null,
  totalTicks: 2,
  rubric: null,
};

describe("recording endings on replay cards", () => {
  it.each([
    ["aborted", "Aborted"],
    ["tick_limited", "Tick limit"],
    ["unfinished", "Unfinished"],
    [undefined, "Unfinished"],
  ] as const)("labels %s without inventing a winner", (completionStatus, label) => {
    const data = { ...base, completionStatus };
    const revealed = renderToStaticMarkup(
      <HighlightCard data={data} reveal onOpen={() => undefined} />,
    );
    expect(revealed).toContain(label);
    expect(revealed).not.toMatch(/Crew win|Impostor win|Outcome —/);

    const hidden = renderToStaticMarkup(
      <HighlightCard data={data} reveal={false} onOpen={() => undefined} />,
    );
    expect(hidden).toContain("Outcome hidden");
    expect(hidden).not.toContain(label);
  });

  it.each([
    ["CREWMATES", "Crew win"],
    ["IMPOSTORS", "Impostor win"],
  ] as const)("preserves the recorded %s outcome", (winner, label) => {
    const html = renderToStaticMarkup(
      <HighlightCard data={{ ...base, winner }} reveal onOpen={() => undefined} />,
    );
    expect(html).toContain(label);
    expect(html).not.toContain("Unfinished");
  });
});
