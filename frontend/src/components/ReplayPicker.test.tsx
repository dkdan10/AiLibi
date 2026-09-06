import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { ReplayBrowserView, type ReplayBrowserViewProps } from "./ReplayPicker";
import { EMPTY_FILTERS } from "./ReplayFilters";

const props: ReplayBrowserViewProps = {
  view: "replays", status: "ready", error: null,
  cards: [{ key: "23", gameId: "headless-seed-23", seed: 23, winner: "CREWMATES", totalTicks: 18, rubric: null }],
  totalCount: 1, filters: EMPTY_FILTERS, winShapeOptions: [], set: "9p2i",
  stale: false, rubricMissing: false, reveal: false,
  onFiltersChange: () => {}, onReveal: () => {}, onOpen: () => {}, onBrowseReplays: () => {},
};

describe("rubric provenance in replay cards", () => {
  it("explains withheld stale scores once without claiming the rubric is absent", () => {
    const html = renderToStaticMarkup(<ReplayBrowserView {...props} stale />);
    expect(html).toContain("Earlier scores");
    expect(html).toContain("cannot be verified");
    expect(html).toContain("18 ticks");
    expect(html).toContain("Open replay seed 23");
    expect(html).not.toContain("ships no");
    expect(html).not.toContain("Not scored");
  });
  it("describes a genuinely absent rubric at set level and keeps cards factual", () => {
    const html = renderToStaticMarkup(<ReplayBrowserView {...props} rubricMissing set="4p1i" />);
    expect(html).toContain("ships no");
    expect(html).toContain("18 ticks");
    expect(html).not.toContain("Earlier scores");
    expect(html).not.toContain("Not scored");
  });
  it("keeps an individual missing score distinct from a set without a rubric", () => {
    const html = renderToStaticMarkup(<ReplayBrowserView {...props} />);
    expect(html).toContain("No score available for this recording");
    expect(html).not.toContain("ships no");
  });
  it("keeps stale and absent highlight empty states distinct", () => {
    const stale = renderToStaticMarkup(<ReplayBrowserView {...props} view="highlights" stale />);
    expect(stale).toContain("No current highlight scores");
    expect(stale).not.toContain("ships no");
    const absent = renderToStaticMarkup(<ReplayBrowserView {...props} view="highlights" rubricMissing set="4p1i" />);
    expect(absent).toContain("No interestingness rubric for this set");
    expect(absent).toContain("Browse all replays");
    expect(absent).not.toContain("9p2i, is scored");
    expect(absent).not.toContain("Earlier scores");
  });
});
