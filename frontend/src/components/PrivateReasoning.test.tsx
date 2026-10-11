import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import { BallotCard, counterKind, rewriteLabel } from "./BallotCard";
import { MeetingView } from "./MeetingView";
import { MindInspectorPanel, type MindInspectorPanelProps } from "./MindInspector";
import { BALLOT_COPY } from "../lib/copy";
import type { BallotView, MeetingView as MeetingDTO, PlayerView, ReplayView } from "../types/api";
import type { Perspective } from "../lib/playback";

const state = vi.hoisted(() => ({
  perspective: { mode: "agent", agentId: "p-2" } as Perspective,
  selectedMeetingId: "meeting-0",
  currentReplay: null as Pick<ReplayView, "players" | "meetings" | "ticks"> | null,
  revealOutcome: false,
  selectedEvidence: null,
  memoryCache: {},
  memoryErrors: {},
}));
vi.mock("../store/replayStore", () => ({ useReplayStore: (selector: (s: typeof state) => unknown) => selector(state) }));
const players: PlayerView[] = [
  { agent_id: "p-1", display_name: "p-1", role: "IMPOSTOR", color: "#ff0000" },
  { agent_id: "p-2", display_name: "p-2", role: "CREWMATE", color: "#0000ff" },
];
// `considered_alternatives` carries BOTH shapes the recordings and the schema
// admit: a served player (which renders as a pill) and a value that is not one
// (which must not). `private-alternative-choice` is also the secret the
// perspective legs below look for — it appears nowhere else in the fixture, so
// finding it in the HTML can only mean the alternatives block rendered.
const ballot: BallotView = { voter: "p-1", target: "p-2", confidence: 0.73, primary_reason_id: "private-statement-choice", primary_reason_observation_id: "private-observation-choice", counter_reason_id: null, considered_alternatives: ["p-2", "private-alternative-choice"], decision_basis: null, grounding_label: null, rationale_text: "I killed them", rationale_text_clean: "I killed them", rewrite_reasons: [] };

/** The alternatives block's inner markup, so a claim about it cannot be
 *  satisfied by the pill the card's HEADER already renders for the target. */
function alternativesBlock(html: string): string {
  return /<div [^>]*data-ballot-alternatives[^>]*>([\s\S]*?)<\/div>/.exec(html)?.[1] ?? "";
}

/** One string per rendered `li`, so a claim about WHICH entry carries a note
 *  cannot be satisfied by that note appearing anywhere in the block. */
function alternativeItems(html: string): string[] {
  return [...alternativesBlock(html).matchAll(/<li[^>]*>([\s\S]*?)<\/li>/g)].map((m) => m[1] ?? "");
}
const meeting: MeetingDTO = {
  meeting_id: "meeting-0", tick: 10, triggered_by: "p-1", trigger_kind: "body",
  outcome: "EJECTED", ejected_player_id: "p-2", turns: [], contradictions: [], llm_calls: [], prompt_versions: {}, total_cost_usd: 0,
  ballots: [ballot, { ...ballot, voter: "p-3", confidence: 0.42 }, { ...ballot, voter: "p-2", target: "SKIP", confidence: 0.21 }],
  gate: { leader: "p-2", leader_max_confidence: 0.73, threshold: 0.6, passed: true },
};
const mind: MindInspectorPanelProps = {
  players, selectedAgentId: "p-1", meeting: undefined, memoryError: null,
  memory: { agent_id: "p-1", tick: 10, role: "IMPOSTOR", tasks_completed: 0, tasks_assigned: 0,
    observations: [{ type: "saw_player", subject: "private-subject", room: "private-room", tick: 9, co_present: [] }],
    beliefs: [{ subject: "private-belief", suspicion: 0.81, confidence: 0.74, snapshot_tick: 10 }],
    open_contradictions: [{ contradiction_id: "private-flag", kind: "alibi_conflict", event_a_id: "a", event_b_id: "b", subjects: ["p-2"], description: "private flag description", weak: false, severity: "strong", category: "cross_statement" }],
    rendered_memory_text: "private rendered memory" },
  isAlive: true, ownKills: [], coverTasks: [], perspective: { mode: "agent", agentId: "p-2" },
  onSelectAgent: () => {}, onShowWhatTheySaw: () => {},
};

/** Markup as text: tags and React's text-joining comments dropped. */
function textOf(html: string): string {
  return html.replace(/<!--[\s\S]*?-->/g, "").replace(/<[^>]*>/g, "");
}

/** The Resolution card's readout sentence, as a reader sees it. */
function readoutOf(html: string): string {
  const match = /<p data-vote-readout[^>]*>([\s\S]*?)<\/p>/.exec(html);
  if (match === null) throw new Error("no vote readout rendered");
  return (match[1] ?? "").replace(/<!--[\s\S]*?-->/g, "").replace(/<[^>]*>/g, "").replaceAll("&lt;", "<").replaceAll("&gt;", ">").replaceAll("&amp;", "&");
}

/** The retired readout's terms and signs: plurality, the cut, the raw outcome, a comparison. */
const RETIRED_READOUT = /plurality|threshold|top ballot|your ballot|EJECTED|SKIPPED|[<>≥≤=→]/;

/**
 * What a readout carries beyond plain words: a digit once each player id is
 * removed (a confidence, a cut point), or a retired term or sign. Empty when it
 * reads in words alone.
 */
function readoutProblems(readout: string): readonly string[] {
  const problems: string[] = [];
  const digit = /\d+(?:\.\d+)?/.exec(readout.replace(/p-\d+/g, ""));
  if (digit !== null) problems.push(`a number: ${digit[0]}`);
  const retired = RETIRED_READOUT.exec(readout);
  if (retired !== null) problems.push(`a retired term: ${retired[0]}`);
  return problems;
}

/** Every perspective the meeting can be read from: all roles, and each voter's own. */
const PERSPECTIVES: readonly Perspective[] = [
  { mode: "omniscient" },
  { mode: "agent", agentId: "p-1" },
  { mode: "agent", agentId: "p-2" },
  { mode: "agent", agentId: "p-3" },
];

function renderMeeting(perspective: Perspective, shown: MeetingDTO = meeting): string {
  state.perspective = perspective;
  state.currentReplay = { players, meetings: [shown], ticks: [] };
  return renderToStaticMarkup(<MeetingView />);
}

/** The planted meeting with its vote failed (leader set) or tied (no leader). */
function skipped(leader: string | null): MeetingDTO {
  return {
    ...meeting, outcome: "SKIPPED", ejected_player_id: null,
    ballots: meeting.ballots.map((entry) => entry.voter === "p-1" ? { ...entry, confidence: 0.53 } : entry),
    gate: { ...meeting.gate, leader, passed: false, leader_max_confidence: 0.53 },
  };
}

describe("private reasoning perspective", () => {
  it.each([false, true])("keeps another ballot's confidence out of Resolution, outcome reveal=%s", (revealOutcome) => {
    state.revealOutcome = revealOutcome;
    const html = renderMeeting({ mode: "agent", agentId: "p-2" });
    expect(html).toContain("Resolution");
    expect(html).toContain("Ejected — p-2");
    expect(html).not.toContain("0.73");
    expect(html).not.toContain("0.42");
    expect(readoutProblems(readoutOf(html))).toEqual([]);
  });
  it.each([["p-1"], ["p-3"]])("Resolution names no confidence under %s's own lens, its own ballot included", (observerId) => {
    const html = renderMeeting({ mode: "agent", agentId: observerId });
    expect(readoutProblems(readoutOf(html))).toEqual([]);
    expect(readoutOf(html)).toContain("p-2 was ejected");
    if (observerId === "p-3") expect(html).not.toContain("0.73");
  });
  it("names no confidence in the omniscient Resolution either", () => {
    const html = renderMeeting({ mode: "omniscient" });
    expect(readoutProblems(readoutOf(html))).toEqual([]);
    expect(readoutOf(html)).toBe("How the vote resolved: Most votes went to p-2 and a voter was sure enough, so p-2 was ejected.");
  });
  it.each(["p-2", null])("does not expose confidence when the gate fails or ties, leader=%s", (leader) => {
    const html = renderMeeting({ mode: "agent", agentId: "p-2" }, skipped(leader));
    expect(readoutOf(html)).toContain("no one was ejected");
    expect(html).not.toContain("0.53");
    expect(html).not.toContain("0.42");
  });
  it.each(PERSPECTIVES.map((perspective) => [perspective.mode === "agent" ? perspective.agentId : "omniscient", perspective] as const))(
    "reads every way a vote ends in words alone under %s's view",
    (_name, perspective) => {
      for (const shown of [meeting, skipped("p-2"), skipped(null)]) {
        const readout = readoutOf(renderMeeting(perspective, shown));
        expect(readoutProblems(readout), readout).toEqual([]);
      }
    },
  );
  it("catches a number, the old templates and a retired sign in the readout (planted)", () => {
    // A confidence left in the sentence fails while the player ids pass.
    expect(readoutProblems("Most votes went to p-4 and a voter was sure enough, so p-4 was ejected.")).toEqual([]);
    expect(readoutProblems("Most votes went to p-4 and a voter was sure enough (0.73), so p-4 was ejected.")).toEqual(["a number: 0.73"]);
    // The old templates, one per perspective, each fail.
    expect(readoutProblems("plurality leader p-2, top ballot 0.73 ≥ 0.60 threshold → EJECTED")).toEqual(["a number: 0.73", "a retired term: plurality"]);
    expect(readoutProblems("plurality leader p-2, your ballot 0.73, threshold met → EJECTED")).toEqual(["a number: 0.73", "a retired term: plurality"]);
    expect(readoutProblems("plurality leader p-2, threshold met → EJECTED")).toEqual(["a retired term: plurality"]);
    expect(readoutProblems("no plurality leader (tie or SKIP led) → SKIPPED")).toEqual(["a retired term: plurality"]);
    expect(readoutProblems("Most votes went to p-4 → SKIPPED")).toEqual(["a retired term: →"]);
  });
  it.each([false, true])("hides model-authored ballot secrets without relying on guard markers, outcome reveal=%s", (revealOutcome) => {
    state.perspective = { mode: "agent", agentId: "p-2" };
    const html = renderToStaticMarkup(<BallotCard ballot={ballot} players={players} omniscient={false} revealOutcome={revealOutcome} />);
    expect(html).toContain("p-1");
    expect(html).toContain("p-2");
    expect(html).toContain("Private ballot reasoning");
    for (const secret of ["I killed them", "0.73", "private-statement-choice", "private-observation-choice", "private-alternative-choice"]) expect(html).not.toContain(secret);
    expect(html).not.toContain("no rationale recorded");
    // The whole weighing block, heading included — not just its entries. An
    // empty heading through a foreign lens would still disclose that the voter
    // weighed nothing, which is itself private reasoning.
    expect(html).not.toContain(BALLOT_COPY.alternativesLabel);
    expect(alternativesBlock(html)).toBe("");
  });
  it.each([false, true])("shows reasoning from the voter’s lens or omniscient mode: %s", (omniscient) => {
    state.perspective = { mode: "agent", agentId: omniscient ? "p-2" : "p-1" };
    const html = renderToStaticMarkup(<BallotCard ballot={ballot} players={players} omniscient={omniscient} revealOutcome={false} />);
    expect(html).toContain("I killed them");
    expect(html).toContain("private-observation-choice");
    expect(html).toContain("private-alternative-choice");
    expect(html).not.toContain("incorrect");
  });
  it.each([false, true])("renders every considered alternative in its recorded order, omniscient=%s", (omniscient) => {
    state.perspective = { mode: "agent", agentId: omniscient ? "p-2" : "p-1" };
    const html = renderToStaticMarkup(<BallotCard ballot={ballot} players={players} omniscient={omniscient} revealOutcome={false} />);
    const block = alternativesBlock(html);
    // One `li` per recorded entry, however many there are, in the recorded
    // order — the render must not assume today's two-wide lists.
    expect(block.match(/<li/g)).toHaveLength(2);
    expect(block.indexOf("p-2")).toBeLessThan(block.indexOf("private-alternative-choice"));
    // A served player wears the identity pill (its swatch carries the player's
    // own colour); a value that is not a served player gets a plain token, so an
    // unknown id — or the literal SKIP the ballot schema also admits — cannot
    // masquerade as somebody at the table.
    expect(block).toContain("#0000ff");
    expect(block.match(/background-color/g)).toHaveLength(1);
    expect(block).toContain("border-dashed");
    expect(html).not.toContain(BALLOT_COPY.alternativesEmpty);
    // The list is NAMED by the label a viewer can see, not by an invisible one.
    const labelId = new RegExp(`<span id="([^"]+)"[^>]*>${BALLOT_COPY.alternativesLabel}</span>`).exec(block)?.[1];
    expect(labelId).toBeDefined();
    expect(block).toContain(`aria-labelledby="${labelId ?? ""}"`);
  });
  it("names an entry the header already shows rather than passing it off as another player", () => {
    // The recorded list is NOT a list of other players: measured over
    // `replays/samples/9p2i` with `scripts/measure_featured_criterion.py
    // --alternatives`, 27 of 702 ballots list the VOTER itself (28 of 691 on
    // round 2's bytes). None lists the
    // target the vote APPLIED to, which the ballot schema still admits, so that
    // entry is constructed here. Either renders a pill identical to one in the
    // card's header, so it is annotated — and kept, because the block is the
    // record and dropping an entry would make the render disagree with the
    // bytes. This is the enforcing mechanism for that claim.
    state.perspective = { mode: "omniscient" };
    const alternatives = ["p-2", "p-1", "private-alternative-choice"]; // target, voter, neither
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, considered_alternatives: alternatives }} players={players} omniscient revealOutcome={false} />);
    const items = alternativeItems(html);
    expect(items).toHaveLength(3);
    // Each note sits inside the `li` of the entry it qualifies, and nowhere else.
    expect(items[0]).toContain("p-2");
    expect(items[0]).toContain(BALLOT_COPY.alternativesTargetNote);
    expect(items[0]).not.toContain(BALLOT_COPY.alternativesSelfNote);
    expect(items[1]).toContain("p-1");
    expect(items[1]).toContain(BALLOT_COPY.alternativesSelfNote);
    expect(items[1]).not.toContain(BALLOT_COPY.alternativesTargetNote);
    // An entry that is neither carries NO note: the annotation is a statement
    // about the header, not decoration on every row.
    expect(items[2]).toContain("private-alternative-choice");
    expect(items[2]).not.toContain(BALLOT_COPY.alternativesSelfNote);
    expect(items[2]).not.toContain(BALLOT_COPY.alternativesTargetNote);
  });
  it("names a recorded SKIP as the vote cast when the ballot skipped", () => {
    // The note follows the header, not the player list: a SKIP ballot whose
    // recorded list holds the literal `SKIP` (the shape tests/api/
    // test_schemas.py admits) duplicates the header's skip chip, so it is named
    // the same way — and still refused the identity pill.
    state.perspective = { mode: "omniscient" };
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, target: "SKIP", considered_alternatives: ["SKIP"] }} players={players} omniscient revealOutcome={false} />);
    const items = alternativeItems(html);
    expect(items).toHaveLength(1);
    expect(items[0]).toContain("SKIP");
    expect(items[0]).toContain(BALLOT_COPY.alternativesTargetNote);
    expect(items[0]).toContain("border-dashed");
    expect(items[0]).not.toContain("background-color");
  });
  it.each([["SKIP"], ["p-404"]])("does not dress %s as a player at the table", (entry) => {
    state.perspective = { mode: "omniscient" };
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, considered_alternatives: [entry] }} players={players} omniscient revealOutcome={false} />);
    const block = alternativesBlock(html);
    expect(block).toContain(entry);
    expect(block).toContain("border-dashed");
    expect(block).not.toContain("background-color");
  });
  it("says so explicitly when the voter recorded no alternative", () => {
    state.perspective = { mode: "omniscient" };
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, considered_alternatives: [] }} players={players} omniscient revealOutcome={false} />);
    // An empty list is a RECORD — the voter weighed nobody else — so the block
    // still renders and says that, rather than vanishing and leaving a viewer to
    // read the absence as "not shown here".
    expect(html).toContain(BALLOT_COPY.alternativesLabel);
    expect(html).toContain(BALLOT_COPY.alternativesEmpty);
    expect(alternativesBlock(html)).not.toContain("<li");
  });
  it("shows the meeting's grounding label beside the weighed list", () => {
    // The chip the substrate wave adds, and the one claim it may make: it
    // DESCRIBES the basis. The vote itself is the voter's, so the card must not
    // dress the label as an adjustment — no rewrite chip, no redirect note.
    state.perspective = { mode: "omniscient" };
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, grounding_label: "uncited" }} players={players} omniscient revealOutcome={false} />);
    expect(alternativesBlock(html)).toContain(BALLOT_COPY.groundingLabels.uncited);
    expect(html).not.toContain("grounding_label");
    expect(html).not.toContain("uncited\"");
    expect(html).not.toContain(BALLOT_COPY.redirectNote);
  });
  it.each(Object.entries(BALLOT_COPY.groundingLabels))("renders %s in plain language", (label, copy) => {
    state.perspective = { mode: "omniscient" };
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, grounding_label: label }} players={players} omniscient revealOutcome={false} />);
    expect(alternativesBlock(html)).toContain(copy);
    // The raw token is machine vocabulary and never reaches the page.
    expect(html).not.toContain(`>${label}<`);
  });
  it("renders nothing for a recording that predates the label, or a value it has not been taught", () => {
    // Every committed recording carries `null` here, so the shipped tour must
    // look exactly as it did; an unrecognised value is not narrated either,
    // because a label this build cannot name is one it must not describe.
    state.perspective = { mode: "omniscient" };
    const before = renderToStaticMarkup(<BallotCard ballot={ballot} players={players} omniscient revealOutcome={false} />);
    expect(before).not.toContain("data-ballot-grounding");
    const unknown = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, grounding_label: "something_new" }} players={players} omniscient revealOutcome={false} />);
    expect(unknown).not.toContain("data-ballot-grounding");
    expect(unknown).not.toContain("something_new");
  });
  it("keeps the grounding label behind the same perspective gate as the citations", () => {
    state.perspective = { mode: "agent", agentId: "p-2" };
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, grounding_label: "not_assessed" }} players={players} omniscient={false} revealOutcome={false} />);
    expect(html).not.toContain(BALLOT_COPY.groundingLabels.not_assessed);
    expect(html).not.toContain("data-ballot-grounding");
  });
  it.each([
    ["off_target_coerced", "Vote citing evidence about someone else changed to skip"],
    ["invalid_basis", "Unreadable stated reason removed"],
  ])("names the %s adjustment instead of falling back to the generic chip", (reason, copy) => {
    // Review round 3: the two `rewriteLabel` cases the substrate wave added.
    // Neither appears on a committed recording — `off_target_coerced` never
    // fired at all, and `invalid_basis` first mints at the re-record — so
    // deleting either case left the suite green while the chip silently
    // degraded to the fallback.
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, rewrite_reasons: [reason] }} players={players} omniscient revealOutcome={false} />);
    expect(html).toContain(copy);
    expect(html).not.toContain(BALLOT_COPY.rewriteFallback);
    expect(html).not.toContain(reason);
  });
  it.each(Object.entries(BALLOT_COPY.rewriteLabels))("renders the %s chip in its own plain words", (reason, copy) => {
    // One render per reason the ballot copy names: dropping a reason from the
    // copy turns its chip into the fallback, which this fails on.
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, rewrite_reasons: [reason] }} players={players} omniscient revealOutcome={false} />);
    expect(html).toContain(copy);
    expect(html).not.toContain(BALLOT_COPY.rewriteFallback);
    expect(html).not.toContain(`>${reason}<`);
    expect(rewriteLabel(reason)).toBe(copy);
  });
  it.each(["something_new", "constructor", "toString"])("reads a reason it was never taught, %s, as the fallback", (reason) => {
    expect(rewriteLabel(reason)).toBe(BALLOT_COPY.rewriteFallback);
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, rewrite_reasons: [reason] }} players={players} omniscient revealOutcome={false} />);
    expect(html).toContain(BALLOT_COPY.rewriteFallback);
  });
  it("links the counter citation beside the two the voter reasoned from", () => {
    // Ruling D5 of 2026-09-19: what the voter itself named as pointing AWAY
    // from its vote. Both id shapes are admissible, and which link kind each
    // resolves to is the point — a turn id is a statement, an observation id
    // is an observation.
    state.perspective = { mode: "omniscient" };
    const turnCited = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, counter_reason_id: "meeting-0:turn-3" }} players={players} omniscient revealOutcome={false} />);
    expect(turnCited).toContain(BALLOT_COPY.counterLabel);
    expect(turnCited).toContain("meeting-0:turn-3");
    expect(counterKind("meeting-0:turn-3")).toBe("statement");
    expect(counterKind("p-1:12:0")).toBe("observation");
    const obsCited = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, counter_reason_id: "p-1:12:0" }} players={players} omniscient revealOutcome={false} />);
    expect(obsCited).toContain("p-1:12:0");
    expect(textOf(obsCited)).toContain(`${BALLOT_COPY.counterLabel} · What p-1 saw at tick 12`);
  });
  it("names each citation by what it points at, the exact id on hover", () => {
    // The speaker comes from the meeting's public turn with that id; the turn
    // number, the observer and the tick from the id itself.
    state.perspective = { mode: "omniscient" };
    state.selectedMeetingId = "meeting-0";
    const reply: MeetingDTO["turns"][number] = { turn_id: "meeting-0:turn-3", turn_index: 3, speaker: "p-3", turn_kind: "reply", reply_to: null, observations: [], claims: [], free_text: "", annotations: [], fabricated_opening: false };
    state.currentReplay = { players, meetings: [{ ...meeting, turns: [reply] }], ticks: [] };
    const cited: BallotView = { ...ballot, primary_reason_id: "meeting-0:turn-3", primary_reason_observation_id: "p-1:12:0", counter_reason_id: "meeting-0:turn-3" };
    const html = renderToStaticMarkup(<BallotCard ballot={cited} players={players} omniscient revealOutcome={false} />);
    expect(html).toContain('title="meeting-0:turn-3"');
    expect(html).toContain('title="p-1:12:0"');
    expect(html).toContain(">Statement by p-3 (turn 3)</button>");
    expect(html).toContain(">What p-1 saw at tick 12</button>");
    expect(textOf(html)).toContain(`${BALLOT_COPY.counterLabel} · Statement by p-3 (turn 3)`);
    expect(html).not.toMatch(/Cited (?:statement|observation)/);
    // A statement id this meeting does not hold says so instead of naming anyone.
    const stray = renderToStaticMarkup(<BallotCard ballot={{ ...cited, primary_reason_id: "meeting-0:turn-9" }} players={players} omniscient revealOutcome={false} />);
    expect(stray).toContain(">Statement (turn 9), not found in this meeting</button>");
    state.currentReplay = null;
  });
  it("names an observation citation in words when no meeting is selected to link it to", () => {
    // With no meeting selected the citations cannot select anything, so they
    // render as plain spans; they still name what they point at, each with
    // its exact id on hover, and the counter slot still reads its id's kind.
    state.perspective = { mode: "omniscient" };
    state.selectedMeetingId = null as unknown as string;
    try {
      const cited: BallotView = { ...ballot, primary_reason_observation_id: "p-1:12:0", counter_reason_id: "p-1:12:0" };
      const html = renderToStaticMarkup(<BallotCard ballot={cited} players={players} omniscient revealOutcome={false} />);
      const spans = [...html.matchAll(/<span class="text-xs" title="([^"]*)">([\s\S]*?)<\/span>/g)].map((match) => [match[1], textOf(match[2] ?? "")]);
      expect(spans).toEqual([
        ["p-1:12:0", "What p-1 saw at tick 12"],
        ["p-1:12:0", `${BALLOT_COPY.counterLabel} · What p-1 saw at tick 12`],
      ]);
      expect(html).not.toContain("<button");
      // Two different ids, so each span's words and hover read its own slot.
      const apart = renderToStaticMarkup(<BallotCard ballot={{ ...cited, counter_reason_id: "p-3:7:1" }} players={players} omniscient revealOutcome={false} />);
      expect([...apart.matchAll(/<span class="text-xs" title="([^"]*)">([\s\S]*?)<\/span>/g)].map((match) => [match[1], textOf(match[2] ?? "")])).toEqual([
        ["p-1:12:0", "What p-1 saw at tick 12"],
        ["p-3:7:1", `${BALLOT_COPY.counterLabel} · What p-3 saw at tick 7`],
      ]);
    } finally {
      state.selectedMeetingId = "meeting-0";
    }
  });
  it("leads the grounding chip with its label, in view", () => {
    state.perspective = { mode: "omniscient" };
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, grounding_label: "uncited" }} players={players} omniscient revealOutcome={false} />);
    const chip = /<span data-ballot-grounding[^>]*>([\s\S]*?)<\/span>/.exec(html)?.[1] ?? "";
    expect(textOf(chip)).toBe(`Basis on the record: ${BALLOT_COPY.groundingLabels.uncited}`);
    expect(html).not.toMatch(/data-ballot-grounding[^>]*title=/);
  });
  it("shows a ballot's confidence as its word, the number on hover and in the meter's spoken value", () => {
    state.perspective = { mode: "omniscient" };
    for (const [confidence, word] of [[0.73, "High"], [0.72, "Med"], [0.21, "Low"]] as const) {
      const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, confidence }} players={players} omniscient revealOutcome={false} />);
      const face = /<span data-bucket="true" title="([^"]*)"[^>]*>([^<]*)<\/span>/.exec(html);
      expect(face?.[1]).toBe(confidence.toFixed(2));
      expect(face?.[2]).toBe(word);
      expect(html).toContain(`aria-valuetext="${word} (${confidence.toFixed(2)})"`);
      expect(html).toContain(">confidence</span>");
    }
  });
  it("renders no counter link for a recording that predates the field", () => {
    // Every committed recording carries `null` here, so the shipped tour must
    // look exactly as it did, and a null counter is not narrated as an absence.
    state.perspective = { mode: "omniscient" };
    const html = renderToStaticMarkup(<BallotCard ballot={ballot} players={players} omniscient revealOutcome={false} />);
    expect(html).not.toContain(BALLOT_COPY.counterLabel);
  });
  it("words the counter chip as the voter's own act, never as a correction", () => {
    // Review round 3: the label is asserted through the constant everywhere
    // else, so its WORDING was unobservable — a chip re-worded "Citation
    // removed" would have read as a guard's verdict on the ballot, which is
    // the one thing this slot is not. The property is pinned instead of the
    // literal, so the copy can still be edited.
    expect(BALLOT_COPY.counterLabel).not.toMatch(/remov|invalid|unknown|error|reject/i);
    expect(BALLOT_COPY.counterLabel.toLowerCase()).toContain("against");
  });
  it("keeps the counter citation behind the same perspective gate as the others", () => {
    state.perspective = { mode: "agent", agentId: "p-2" };
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, counter_reason_id: "meeting-0:turn-3" }} players={players} omniscient={false} revealOutcome={false} />);
    expect(html).not.toContain(BALLOT_COPY.counterLabel);
    expect(html).not.toContain("meeting-0:turn-3");
  });
  it("names the unresolvable counter citation instead of the generic chip", () => {
    // The layer nulls a counter it cannot resolve and chips the ballot; the
    // chip must say WHICH slot, or a reader reads it as a lost basis.
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, rewrite_reasons: ["invalid_counter_reason_id"] }} players={players} omniscient revealOutcome={false} />);
    expect(html).toContain("The evidence it weighed against the vote was not found, so it was removed");
    expect(html).not.toContain(BALLOT_COPY.rewriteFallback);
    expect(html).not.toContain("invalid_counter_reason_id");
  });
  it("explains redirected votes without presenting the original rationale as the applied choice", () => {
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, rewrite_reasons: ["under_gate_redirect"] }} players={players} omniscient revealOutcome={false} />);
    expect(html).toContain("Vote changed by the vote rule");
    expect(html).toContain("before the vote rule changed the vote");
    expect(html).not.toContain("under_gate_redirect");
  });
  it.each(["belief", "memory", "flags", "prompt", "response"] as const)("hides cached private %s through another lens", (tab) => {
    const html = renderToStaticMarkup(<MindInspectorPanel {...mind} tab={tab} />);
    expect(html).toContain("memory and reasoning are private");
    expect(html).toContain("Show what they saw");
    for (const secret of ["private-room", "private-belief", "private flag description", "private rendered memory"]) expect(html).not.toContain(secret);
  });
  it.each(["belief", "memory", "flags"] as const)("keeps real %s available to the observer", (tab) => {
    const html = renderToStaticMarkup(<MindInspectorPanel {...mind} perspective={{ mode: "agent", agentId: "p-1" }} tab={tab} />);
    expect(html).not.toContain("memory and reasoning are private");
    expect(html).toContain(tab === "belief" ? "private-belief" : tab === "memory" ? "private-room" : "private flag description");
  });
});
