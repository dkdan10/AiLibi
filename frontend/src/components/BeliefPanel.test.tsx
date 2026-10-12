// The belief panel, rendered: it reads by meaning (who suspects whom, the real
// roles, a legend that says what each mark means), one player's perspective
// says so in those words and in no other, numbers sit behind Low / Med / High,
// and the held Error layer keeps its own words.

import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { BeliefPanel, CellDetail, describeChange } from "./BeliefPanel";
import { BELIEF_PANEL_COPY } from "../lib/copy";
import type { BeliefViewMode } from "../lib/playback";
import type { BeliefFrameView, PlayerView } from "../types/api";

const players: PlayerView[] = [
  { agent_id: "p-1", display_name: "p-1", role: "CREWMATE", color: "#0000ff" },
  { agent_id: "p-2", display_name: "p-2", role: "IMPOSTOR", color: "#ff0000" },
];

function entry(observer: string, subject: string, suspicion: number, confidence: number) {
  return { observer, subject, suspicion, confidence, subject_is_impostor: subject === "p-2", error: suspicion - (subject === "p-2" ? 1 : 0), has_belief: true };
}

const frames: BeliefFrameView[] = [
  { meeting_id: "m-0", tick: 10, entries: [entry("p-1", "p-2", 0.68, 0.4), entry("p-2", "p-1", 0.2, 0.3)] },
  { meeting_id: "m-1", tick: 20, entries: [entry("p-1", "p-2", 0.81, 0.55), entry("p-2", "p-1", 0.3, 0.3)] },
];

function render(layer: BeliefViewMode, omniscient: boolean): string {
  return renderToStaticMarkup(
    <BeliefPanel players={players} frames={frames} layer={layer} onLayerChange={() => {}} omniscient={omniscient} />,
  );
}

/** Markup as text: tags and React's text-joining comments dropped. */
function textOf(html: string): string {
  return html.replace(/<!--[\s\S]*?-->/g, "").replace(/<[^>]*>/g, "").replaceAll("&#x27;", "'");
}

/**
 * The retired words for one player's view and for the real roles, anywhere in
 * the markup — text, tooltips and accessible names alike.
 */
function retiredViewWords(html: string): readonly string[] {
  return [...html.replaceAll("&#x27;", "'").matchAll(/\bfog\b|As-agent|[Gg]round[- ][Tt]ruth|GROUND[- ]TRUTH|suspicion matrix/g)].map((match) => match[0]);
}

/** The legend rows as label / description pairs. */
function legendRows(html: string): (readonly [string, string])[] {
  return [...html.matchAll(/<div class="text-xs font-semibold leading-tight text-ink-900">([^<]*)<\/div><div class="mt-1 text-2xs leading-snug text-ink-500">([^<]*)<\/div>/g)].map(
    (match) => [textOf(match[1] ?? ""), textOf(match[2] ?? "")] as const,
  );
}

describe("the panel's names", () => {
  it("is headed by who suspects whom, its toggle naming the real roles", () => {
    const html = render("belief", true);
    expect(html).toContain(">Who suspects whom</h2>");
    expect(textOf(html)).toContain(BELIEF_PANEL_COPY.rowsColumns);
    const toggles = [...html.matchAll(/<button type="button" aria-pressed="(?:true|false)"[^>]*>([^<]*)<\/button>/g)].map((match) => match[1]);
    expect(toggles).toEqual(["Belief", "Real roles", "Error"]);
    expect(html).toContain('aria-label="Belief / Real roles / Error layer"');
    expect(retiredViewWords(html)).toEqual([]);
    expect(html).not.toMatch(/rows = believer|×2 suspicion|2×2/);
  });

  it("names one player's perspective in those words, in text, tooltips and the note", () => {
    const html = render("belief", false);
    const chip = /<span data-perspective-chip="true"[^>]*>([^<]*)<\/span>/.exec(html)?.[1] ?? "";
    expect(textOf(chip)).toBe(BELIEF_PANEL_COPY.perspectiveChip);
    expect(textOf(chip)).toBe("One player's perspective · real roles hidden");
    expect(html).toContain(`title="Hidden in one player&#x27;s perspective, because it would show real roles"`);
    expect(textOf(html)).toContain("One player's perspective: real roles and error are hidden (they would show who the impostor is).");
    // The two hidden layers stay disabled; Error keeps its word.
    expect(html.match(/disabled="" title="Hidden in one player&#x27;s perspective/g)).toHaveLength(2);
    expect(html).toContain(">Error</button>");
    expect(retiredViewWords(html)).toEqual([]);
  });

  it("catches the retired words restored in the chip, the tooltip or the note (planted)", () => {
    const html = render("belief", false);
    expect(retiredViewWords(html.replace(BELIEF_PANEL_COPY.perspectiveChip.replace("'", "&#x27;"), "fog · ground-truth hidden"))).toEqual(["fog", "ground-truth"]);
    expect(retiredViewWords(html.replace("Hidden in one player&#x27;s perspective, because it would show real roles", "Hidden in fog (reveals ground truth)"))).toEqual(["fog", "ground truth"]);
    expect(retiredViewWords(html.replace("One player&#x27;s perspective: real roles", "As-agent fog: ground truth"))).toEqual(["As-agent", "fog", "ground truth"]);
    expect(retiredViewWords(render("belief", true).replace(">Real roles<", ">Ground-truth<"))).toEqual(["Ground-truth"]);
  });
});

describe("the legend", () => {
  it("says what each belief mark means", () => {
    const html = render("belief", true);
    expect(html).toContain(">READING: BELIEF</div>");
    expect(legendRows(html)).toEqual([
      ["Suspicion", "How much the row's player suspects the column's player: Low, Med or High. Hover a cell for the number."],
      ["No belief yet", "Hatched: this player has formed no view yet, which is not the same as no suspicion."],
      ["Self", "The diagonal: a player holds no suspicion of themselves."],
    ]);
  });

  it("says what each real-roles mark means, the dagger first", () => {
    const html = render("truth", true);
    expect(html).toContain(">READING: REAL ROLES</div>");
    expect(legendRows(html)).toEqual([
      ["Dagger", "A real impostor, all-roles view only."],
      ["Impostor column", "A faint hatch on a real impostor's column."],
      ["Dead", "A frozen row and column: this player was dead at this meeting."],
    ]);
  });

  it.each(["belief", "truth"] as const)("carries no design note in the %s legend", (layer) => {
    const legend = legendRows(render(layer, true)).flat().join("\n");
    expect(legend).not.toMatch(/hue|mono|\bfile\b|role-neutral/);
  });

  it("keeps the held Error layer's words byte for byte", () => {
    const html = render("error", true);
    expect(html).toContain(">READING: ERROR</div>");
    expect(legendRows(html)).toEqual([
      ["Confidently wrong", "LOUD fuchsia + ring: a high-confidence belief that disagrees with truth."],
      ["False accusation", "Suspicion aimed at a real crewmate."],
      ["Missed impostor", "Trust extended to a true impostor."],
      ["Aligned", "Belief matches truth — kept calm and pale."],
    ]);
  });
});

describe("the panel's numbers", () => {
  it("shows a cell's suspicion as its word, the number on hover and in its name", () => {
    const html = render("belief", true);
    expect(html).toContain('aria-label="p-1 → p-2: suspicion High (81 of 100), confidence Med (0.55)"');
    expect(html).toMatch(/title="suspicion 81 of 100"[^>]*>High<\/button>/);
    expect(html).toMatch(/title="suspicion 30 of 100"[^>]*>Low<\/button>/);
    expect(html).not.toMatch(/>81<|>30</);
  });

  it("shows the cell detail's meetings as words, the number on hover", () => {
    const html = renderToStaticMarkup(
      <CellDetail players={players} frames={frames} step={1} selected={{ observer: "p-1", subject: "p-2" }} omniscient layer="belief" impostorIds={new Set(["p-2"])} onClose={() => {}} />,
    );
    expect(html).toContain('title="suspicion 68 of 100">Med<span class="sr-only"> (68)</span>');
    expect(html).toContain('title="suspicion 81 of 100">High<span class="sr-only"> (81)</span>');
    expect(html).toContain('title="+13 points, from 68 to 81 of 100">Suspicion rose from Med to High since the previous meeting.</div>');
  });

  it.each([
    [0.68, 0.81, "Suspicion rose from Med to High since the previous meeting.", "+13 points, from 68 to 81 of 100"],
    [0.81, 0.4, "Suspicion fell from High to Med since the previous meeting.", "-41 points, from 81 to 40 of 100"],
    [0.4, 0.45, "Suspicion rose but stayed Med since the previous meeting.", "+5 points, from 40 to 45 of 100"],
    [0.3, 0.1, "Suspicion fell but stayed Low since the previous meeting.", "-20 points, from 30 to 10 of 100"],
  ])("reads a change from %s to %s as the move between words", (before, after, text, title) => {
    const change = describeChange({ present: true, hasBelief: true, suspicion: after }, { present: true, hasBelief: true, suspicion: before });
    expect(change).toEqual({ text, title });
    // The points live on hover, never on the face.
    expect(change.text).not.toMatch(/\d/);
  });

  it("catches points on the face (planted)", () => {
    expect("Suspicion rose +5 since the previous meeting.").toMatch(/\d/);
    expect(describeChange({ present: true, hasBelief: true, suspicion: 0.45 }, { present: true, hasBelief: true, suspicion: 0.4 }).text).not.toContain("+5");
  });
});
