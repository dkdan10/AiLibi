import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import { BallotCard } from "./BallotCard";
import { MeetingView } from "./MeetingView";
import { MindInspectorPanel, type MindInspectorPanelProps } from "./MindInspector";
import { BALLOT_COPY } from "../lib/copy";
import type { BallotView, MeetingView as MeetingDTO, PlayerView, ReplayView } from "../types/api";
import type { Perspective } from "../lib/playback";

const state = vi.hoisted(() => ({
  perspective: { mode: "agent", agentId: "p-2" } as Perspective,
  selectedMeetingId: "meeting-0",
  currentReplay: null as Pick<ReplayView, "players" | "meetings"> | null,
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
const ballot: BallotView = { voter: "p-1", target: "p-2", confidence: 0.73, primary_reason_id: "private-statement-choice", primary_reason_observation_id: "private-observation-choice", considered_alternatives: ["p-2", "private-alternative-choice"], decision_basis: null, grounding_label: null, rationale_text: "I killed them", rationale_text_clean: "I killed them", rewrite_reasons: [] };

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

describe("private reasoning perspective", () => {
  it.each([false, true])("keeps another ballot's confidence out of Resolution, outcome reveal=%s", (revealOutcome) => {
    state.perspective = { mode: "agent", agentId: "p-2" };
    state.currentReplay = { players, meetings: [meeting] };
    state.revealOutcome = revealOutcome;
    const html = renderToStaticMarkup(<MeetingView />);
    expect(html).toContain("Resolution");
    expect(html).toContain("Ejected — p-2");
    expect(html).not.toContain("0.73");
    expect(html).not.toContain("0.42");
    expect(html).not.toContain("top ballot");
  });
  it.each([["p-1", "0.73"], ["p-3", "0.42"]])("Resolution shows only %s's own leader ballot", (observerId, confidence) => {
    state.perspective = { mode: "agent", agentId: observerId };
    state.currentReplay = { players, meetings: [meeting] };
    const html = renderToStaticMarkup(<MeetingView />);
    expect(html).toContain(`your ballot ${confidence}`);
    expect(html).not.toContain("top ballot");
    if (observerId === "p-3") expect(html).not.toContain("0.73");
  });
  it("retains the aggregate Resolution confidence only in omniscient mode", () => {
    state.perspective = { mode: "omniscient" };
    state.currentReplay = { players, meetings: [meeting] };
    const html = renderToStaticMarkup(<MeetingView />);
    expect(html).toContain("top ballot 0.73");
    expect(html).not.toContain("your ballot");
  });
  it.each(["p-2", null])("does not expose confidence when the gate fails or ties, leader=%s", (leader) => {
    state.perspective = { mode: "agent", agentId: "p-2" };
    state.currentReplay = { players, meetings: [{
      ...meeting, outcome: "SKIPPED", ejected_player_id: null,
      ballots: meeting.ballots.map((entry) => entry.voter === "p-1" ? { ...entry, confidence: 0.53 } : entry),
      gate: { ...meeting.gate, leader, passed: false, leader_max_confidence: 0.53 },
    }] };
    const html = renderToStaticMarkup(<MeetingView />);
    expect(html).toContain("SKIPPED");
    expect(html).not.toContain("0.53");
    expect(html).not.toContain("0.42");
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
    // --alternatives`, 27 of 869 ballots list the VOTER itself and 22 list the
    // target the vote APPLIED to. Either renders a pill identical to one in the
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
    expect(html).not.toContain("before the vote was redirected");
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
    ["off_target_coerced", "Off-target citation changed vote to skip"],
    ["invalid_basis", "Unreadable stated basis removed"],
  ])("names the %s adjustment instead of falling back to the generic chip", (reason, copy) => {
    // Review round 3: the two `rewriteLabel` cases the substrate wave added.
    // Neither appears on a committed recording — `off_target_coerced` never
    // fired at all, and `invalid_basis` first mints at the re-record — so
    // deleting either case left the suite green while the chip silently
    // degraded to the default "Recorded vote adjustment".
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, rewrite_reasons: [reason] }} players={players} omniscient revealOutcome={false} />);
    expect(html).toContain(copy);
    expect(html).not.toContain("Recorded vote adjustment");
    expect(html).not.toContain(reason);
  });
  it("explains redirected votes without presenting the original rationale as the applied choice", () => {
    const html = renderToStaticMarkup(<BallotCard ballot={{ ...ballot, rewrite_reasons: ["under_gate_redirect"] }} players={players} omniscient revealOutcome={false} />);
    expect(html).toContain("Vote redirected by the meeting rule");
    expect(html).toContain("before the vote was redirected");
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
