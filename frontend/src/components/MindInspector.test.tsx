// The mind inspector's belief tab, rendered: the trail of what the player did at
// the meeting reads Said / Claimed / Voted / Result, in that order, and every
// confidence it shows is a word with its number on hover.

import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import { MindInspectorPanel, type MindInspectorPanelProps } from "./MindInspector";
import { INSPECTOR_COPY } from "../lib/copy";
import type { MeetingView as MeetingDTO, PlayerView } from "../types/api";

vi.mock("../store/replayStore", () => ({ useReplayStore: () => undefined }));

const players: PlayerView[] = [
  { agent_id: "p-1", display_name: "p-1", role: "CREWMATE", color: "#0000ff" },
  { agent_id: "p-2", display_name: "p-2", role: "IMPOSTOR", color: "#ff0000" },
];

// p-1 speaks once (free text and an accusation), then votes with a written reason.
const meeting: MeetingDTO = {
  meeting_id: "meeting-0",
  tick: 10,
  triggered_by: "p-1",
  trigger_kind: "body",
  outcome: "EJECTED",
  ejected_player_id: "p-2",
  turns: [
    {
      turn_id: "meeting-0:turn-0",
      turn_index: 0,
      speaker: "p-1",
      turn_kind: "opening",
      reply_to: null,
      observations: [],
      claims: [{ type: "accusation", against: "p-2", confidence: 0.81, reason: "spoken-reason" }],
      free_text: "spoken-line",
      annotations: [],
      fabricated_opening: false,
    },
  ],
  ballots: [
    { voter: "p-1", target: "p-2", confidence: 0.6, primary_reason_id: null, primary_reason_observation_id: null, counter_reason_id: null, considered_alternatives: [], decision_basis: null, grounding_label: null, rationale_text: "ballot-reason", rationale_text_clean: "ballot-reason", rewrite_reasons: [] },
  ],
  contradictions: [],
  llm_calls: [],
  prompt_versions: {},
  total_cost_usd: 0,
  gate: { leader: "p-2", leader_max_confidence: 0.73, threshold: 0.6, passed: true },
};

const panel: MindInspectorPanelProps = {
  players,
  selectedAgentId: "p-1",
  meeting,
  memory: {
    agent_id: "p-1", tick: 10, role: "CREWMATE", tasks_completed: 0, tasks_assigned: 0, observations: [],
    beliefs: [{ subject: "p-2", suspicion: 0.81, confidence: 0.55, snapshot_tick: 10 }],
    open_contradictions: [], rendered_memory_text: "",
  },
  memoryError: null,
  isAlive: true,
  ownKills: [],
  coverTasks: [],
  perspective: { mode: "omniscient" },
  tab: "belief",
  onSelectAgent: () => {},
  onShowWhatTheySaw: () => {},
};

/** Markup as text: tags and React's text-joining comments dropped. */
function textOf(html: string): string {
  return html.replace(/<!--[\s\S]*?-->/g, "").replace(/<[^>]*>/g, "");
}

/** Text with what only a screen reader reads (the `sr-only` spans) set aside. */
function faceOf(html: string): string {
  return textOf(html.replace(/<span class="sr-only">[^<]*<\/span>/g, ""));
}

/** The trail's steps, each as [label, text], in rendered order. */
function trailOf(html: string): (readonly [string, string])[] {
  const list = /<ol[^>]*>([\s\S]*?)<\/ol>/.exec(html)?.[1] ?? "";
  return [...list.matchAll(/<li[^>]*><span[^>]*>([^<]*)<\/span><span[^>]*>([\s\S]*?)<\/span><\/li>/g)].map(
    (match) => [match[1] ?? "", faceOf(match[2] ?? "")] as const,
  );
}

describe("the belief tab's trail", () => {
  it("reads Said, Claimed, Voted, Voted, Result in order", () => {
    const html = renderToStaticMarkup(<MindInspectorPanel {...panel} />);
    expect(textOf(html)).toContain(INSPECTOR_COPY.trailHeading);
    expect(textOf(html)).toContain("Said / Claimed / Voted / Result");
    expect(trailOf(html)).toEqual([
      ["Said", "spoken-line"],
      ["Claimed", "accused p-2 — spoken-reason · confidence High"],
      // The written reason is the ballot's, which the table never heard.
      ["Voted", "ballot-reason"],
      ["Voted", "voted to eject p-2 · confidence Med"],
      ["Result", "Meeting: p-2 was ejected"],
    ]);
    expect(html).not.toMatch(/Thought|Action|Observation</);
  });

  it("reads an alibi and a corroboration as Claimed, with no confidence word", () => {
    // Only an accusation records a confidence; the other two claim kinds carry
    // none, so their Claimed steps show no confidence at all.
    const claims: MeetingDTO["turns"][number]["claims"] = [
      { type: "alibi", subject: "p-1", route: [{ room: "Cafeteria", from_tick: 1, to_tick: 4 }], evidence: [] },
      // A claim recorded before routes carries one room and its ticks instead.
      { type: "alibi", subject: "p-1", route: null, room: "Admin", from_tick: 5, to_tick: 6, evidence: [] },
      { type: "alibi", subject: "p-1", route: null, evidence: [] },
      { type: "corroboration", supports: "p-2", on_tick: 7, reason: "seen-together" },
    ];
    const told: MeetingDTO = { ...meeting, turns: meeting.turns.map((turn) => ({ ...turn, free_text: "", claims })) };
    const steps = trailOf(renderToStaticMarkup(<MindInspectorPanel {...panel} meeting={told} />));
    expect(steps.slice(0, 4)).toEqual([
      ["Claimed", "alibi for p-1: Cafeteria, ticks 1–4"],
      ["Claimed", "alibi for p-1: Admin, ticks 5–6"],
      ["Claimed", "alibi for p-1: no route stated"],
      ["Claimed", "corroborated p-2 on tick 7 — seen-together"],
    ]);
  });

  it("closes on the plain no-ejection form when no one was ejected", () => {
    const skipped: MeetingDTO = { ...meeting, outcome: "SKIPPED", ejected_player_id: null };
    const steps = trailOf(renderToStaticMarkup(<MindInspectorPanel {...panel} meeting={skipped} />));
    expect(steps.at(-1)).toEqual(["Result", "Meeting: no one was ejected"]);
  });
});

describe("the belief tab's numbers", () => {
  it("shows each confidence as its word, the number on hover and for a screen reader", () => {
    const html = renderToStaticMarkup(<MindInspectorPanel {...panel} />);
    // The trail's two confidences: the claim's and the ballot's.
    expect(html).toMatch(/<span data-bucket="true" title="0.81">confidence High<span class="sr-only"> \(0.81\)<\/span><\/span>/);
    expect(html).toMatch(/<span data-bucket="true" title="0.60">confidence Med<span class="sr-only"> \(0.60\)<\/span><\/span>/);
    // The belief bar's confidence pill.
    expect(html).toContain('title="confidence 0.55 · snapshot tick 10"');
    expect(html).toContain(">confidence Med</span><span class=\"sr-only\"> (0.55)</span>");
    // No figure on any face of the tab.
    expect(faceOf(html)).not.toMatch(/conf \d|\d\.\d\d/);
  });
});
