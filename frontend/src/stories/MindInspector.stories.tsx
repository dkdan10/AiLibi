// Stories for the mind inspector (Task 12.8; design/phase-12/stage-1-design.md
// §3.5, slice 6). They drive the PRESENTATIONAL <MindInspectorPanel/> — the
// connected <MindInspector/> only adds the store wiring + fetches, which
// Storybook can't host — with mock DTOs in the exact served shape, so each state
// + firewall requirement is visible in isolation:
//   • living / dead / impostor (Omniscient) / impostor-viewing-itself /
//     no-agent-selected (the contract's state set);
//   • the firewall: impostor extras (fellow impostors, own_kill, fabricated
//     cover) appear in Omniscient OR self-lens, and VANISH when an impostor is
//     inspected through a DIFFERENT agent's eyes (the Fog-leak story).

import type { Meta, StoryObj } from "@storybook/react-vite";

import { MindInspectorPanel } from "../components/MindInspector";
import { OMNISCIENT, type Perspective } from "../lib/playback";
import { tokens } from "../tokens";
import type {
  AgentMemoryView,
  BallotView,
  CompletedTaskObsView,
  ContradictionView,
  KillEventView,
  LLMCallView,
  MeetingView,
  PlayerView,
  TurnView,
} from "../types/api";

// Realistic 9p2i roster (brief: ids p-0…p-8, identity palette is firewall-safe —
// crew + impostor chips are indistinguishable by hue). p-2 + p-5 are impostors.
const IMPOSTORS = new Set(["p-2", "p-5"]);
const PLAYERS: PlayerView[] = Array.from({ length: 9 }, (_, i) => ({
  agent_id: `p-${i}`,
  display_name: `p-${i}`,
  role: IMPOSTORS.has(`p-${i}`) ? "IMPOSTOR" : "CREWMATE",
  color: tokens.identity[i] ?? "#888888",
}));

function llmCall(agentId: string, prompt: string, response: string): LLMCallView {
  return {
    call_kind: "meeting",
    model: "claude-mock-1",
    prompt_template_id: "meeting_ballot@v3",
    prompt_text: prompt,
    response_text: response,
    input_tokens: 1840,
    output_tokens: 210,
    cost_usd: 0.0123,
    agent_id: agentId,
  };
}

function turn(speaker: string, freeText: string): TurnView {
  return {
    turn_id: `t-${speaker}`,
    turn_index: 0,
    speaker,
    turn_kind: "opening",
    reply_to: null,
    observations: [],
    claims: [
      {
        type: "accusation",
        against: "p-5",
        confidence: 0.7,
        reason: "headed to Reactor right before the body was found",
      },
    ],
    free_text: freeText,
    annotations: [],
    fabricated_opening: false,
  };
}

function ballot(voter: string, target: string): BallotView {
  return {
    voter,
    target,
    confidence: 0.68,
    primary_reason_id: null,
    // Task 16.7.1: the own-episodic-observation citation (display-only).
    primary_reason_observation_id: null,
    considered_alternatives: ["p-2"],
    rationale_text: "raw rationale",
    rewrite_reasons: [],
    rationale_text_clean: `${voter} thinks ${target} is the most likely impostor given the Reactor sighting.`,
  };
}

// Task 19.11: `category` is the evidence taxonomy the badge now weights by. This
// one is a CROSS-STATEMENT conflict — two unverified statements that cannot both
// be true, which is not the same thing as proof and no longer renders like it.
const CONTRADICTION: ContradictionView = {
  contradiction_id: "c-1",
  kind: "alibi_vs_sighting",
  event_a_id: "e-a",
  event_b_id: "e-b",
  subjects: ["p-5"],
  description: "p-5 claimed Cafeteria at tick 310 but was seen in Reactor.",
  weak: false,
  severity: "strong",
  category: "cross_statement",
};

// The ROLE-PROOF exhibit: a grounded vent sighting, self-linked (both ids
// reference the SAME spoken observation), so the badge weights it as proof.
const VENT_PROOF: ContradictionView = {
  contradiction_id: "c-2",
  kind: "vent_sighting",
  event_a_id: "e-vent",
  event_b_id: "e-vent",
  subjects: ["p-5"],
  description:
    "p-1 witnessed p-5 vent in REACTOR at tick 314; venting is impostor-only, and the spoken observation matches the witness's own record.",
  weak: false,
  severity: "strong",
  category: "role_proof",
};

// The WEAK-SIGNAL exhibit: the detector stamped it itself, so the badge recedes.
const WEAK_FLAG: ContradictionView = {
  contradiction_id: "c-3",
  kind: "alibi_conflict",
  event_a_id: "e-c",
  event_b_id: "e-d",
  subjects: ["p-0"],
  description:
    "Alibis place p-0 in CAFETERIA (ticks 310-310) and in ADMIN (ticks 305-310); intervals overlap. [weak signal: self-stated alibi pair; endpoint-tick overlap]",
  weak: true,
  severity: "weak",
  category: "weak_signal",
};

const MEETING: MeetingView = {
  meeting_id: "m-1",
  tick: 320,
  triggered_by: "p-4",
  trigger_kind: "body",
  outcome: "EJECTED",
  ejected_player_id: "p-5",
  turns: [turn("p-1", "I saw p-5 head toward Reactor around tick 312."), turn("p-5", "I was in Cafeteria the whole time.")],
  ballots: [ballot("p-1", "p-5"), ballot("p-5", "p-0")],
  contradictions: [VENT_PROOF, CONTRADICTION, WEAK_FLAG],
  llm_calls: [
    llmCall(
      "p-1",
      "You are p-1, a CREWMATE. Rendered memory:\n- saw p-5 in Reactor at tick 312\n- found body of p-7 in Reactor at tick 318\nCast your ballot.",
      "I'll vote p-5 — the Reactor sighting lines up with the body. Confidence 0.68.",
    ),
    llmCall(
      "p-5",
      "You are p-5, an IMPOSTOR. Fellow impostors: p-2. Rendered memory:\n- own_kill of p-7 in Reactor at tick 316 (do not reveal)\n- cover task in Electrical at tick 300\nDeflect suspicion.",
      "I'll claim I was in Cafeteria and push the vote toward p-0.",
    ),
  ],
  prompt_versions: { meeting_ballot: "v3" },
  total_cost_usd: 0.025,
  gate: { leader: "p-5", leader_max_confidence: 0.7, threshold: 0.5, passed: true },
};

function memory(agentId: string): AgentMemoryView {
  const impostor = IMPOSTORS.has(agentId);
  return {
    agent_id: agentId,
    tick: 320,
    role: impostor ? "IMPOSTOR" : "CREWMATE",
    tasks_completed: impostor ? 0 : 3,
    tasks_assigned: impostor ? 0 : 5,
    // The episodic feed only ever carries saw_player / found_body (the loader's
    // `_observations_from_memory`); cover tasks live in `coverTasks`, not here.
    observations: [
      { type: "saw_player", tick: 312, subject: "p-5", room: "Reactor", co_present: ["p-7"] },
      { type: "found_body", tick: 318, body_of: "p-7", room: "Reactor" },
    ],
    beliefs: [
      { subject: "p-5", suspicion: 0.81, confidence: 0.74, snapshot_tick: 320 },
      { subject: "p-2", suspicion: 0.18, confidence: 0.4, snapshot_tick: 320 },
      { subject: "p-0", suspicion: 0.34, confidence: 0.52, snapshot_tick: 320 },
    ],
    // All three Task-19.11 categories, so the evidence badge's weighting has
    // story coverage: proof reads as proof, the conflict as a conflict, the
    // weak-stamped flag recedes.
    open_contradictions: [VENT_PROOF, CONTRADICTION, WEAK_FLAG],
    rendered_memory_text: `=== Memory for ${agentId} ===\n- saw p-5 in Reactor at tick 312\n- found body of p-7 in Reactor at tick 318\n- belief: p-5 suspicion 0.81`,
  };
}

const OWN_KILLS: KillEventView[] = [
  { type: "kill", tick: 316, killer_id: "p-5", victim_id: "p-7", room_id: "Reactor" },
];

// p-5's fabricated cover-task alibi (its meeting `completed_task` turn obs).
const COVER_TASKS: CompletedTaskObsView[] = [
  { type: "completed_task", tick: 300, task_id: "wiring-3", room: "Electrical" },
];

const AS_P5: Perspective = { mode: "agent", agentId: "p-5" };
const AS_P1: Perspective = { mode: "agent", agentId: "p-1" };

const meta: Meta<typeof MindInspectorPanel> = {
  title: "Mind/MindInspector",
  component: MindInspectorPanel,
  parameters: { layout: "padded" },
  args: {
    players: PLAYERS,
    meeting: MEETING,
    memoryError: null,
    ownKills: [],
    coverTasks: [],
    perspective: OMNISCIENT,
    isAlive: true,
    onSelectAgent: () => {},
    onShowWhatTheySaw: () => {},
  },
  decorators: [
    (Story) => (
      <div className="max-w-md rounded-md border-2 border-ink-900 bg-paper-1 p-4">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof MindInspectorPanel>;

// A living crewmate under Omniscient — beliefs, trail, no impostor extras.
export const LivingCrewmate: Story = {
  args: { selectedAgentId: "p-1", memory: memory("p-1") },
};

// A dead agent — the role-neutral "dead" chip in the header.
export const Dead: Story = {
  args: { selectedAgentId: "p-7", memory: memory("p-7"), isAlive: false },
};

// An impostor under Omniscient — the IMPOSTOR badge + fellow impostors + own_kill
// + the fabricated cover-task label are all revealed. The found_body of its own
// victim (p-7) is suppressed from the feed in favour of the own-kill line.
export const ImpostorOmniscient: Story = {
  args: {
    selectedAgentId: "p-5",
    memory: memory("p-5"),
    ownKills: OWN_KILLS,
    coverTasks: COVER_TASKS,
  },
};

// The same impostor through ITS OWN lens (self-perspective) — its secrets are its
// own knowledge, so they stay visible (the "show what they saw" flip).
export const ImpostorViewingItself: Story = {
  args: {
    selectedAgentId: "p-5",
    memory: memory("p-5"),
    ownKills: OWN_KILLS,
    coverTasks: COVER_TASKS,
    perspective: AS_P5,
  },
};

// Another agent’s lens hides every private mind tab, including episodic evidence.
export const ImpostorThroughOtherFog: Story = {
  args: {
    selectedAgentId: "p-5",
    memory: memory("p-5"),
    ownKills: OWN_KILLS,
    coverTasks: COVER_TASKS,
    perspective: AS_P1,
  },
};

// No agent selected — the picker + the prompt to choose one.
export const NoAgentSelected: Story = {
  args: { selectedAgentId: null, memory: undefined },
};
