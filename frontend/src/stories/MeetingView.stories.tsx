// Storybook story for the meeting transcript surface (Task 12.7;
// design/phase-12/stage-1-design.md §3.4, slice 5; the committed 05-meeting
// render). Renders <MeetingView/> against meeting fixtures that mirror the served
// `ReplayView` DTO, seeded into the Zustand store the component reads from. The
// required states are covered:
//
//   • Chain      — the 05-meeting hero: a threaded accusation waterfall (indented
//                  by reply_to), one flag per Task-19.11 evidence category
//                  (role proof / cross-statement contradiction / weak signal),
//                  ballots with rewrite-marker chips, and a §4.6 EJECTED verdict.
//   • SingleTurn — one opening turn, no replies (the un-threaded case).
//   • Skipped    — a below-threshold gate (leader < 0.6) → SKIPPED, role-neutral.
//   • Ejected    — a clean plurality + ≥ 0.6 ejection with the post-hoc reveal.
//   • ChainAsAgentFog — the same hero under As-agent fog: correctness + the
//                  post-hoc role reveal are suppressed (firewall).
//   • GuardChip{Omniscient,AsAgentFogUnrevealed,AsAgentFogRevealed} — Task
//                  19.11's role-disclosing `teammate_coerced` chip in all three
//                  states: visible in Omniscient, hidden under As-agent fog with
//                  the outcome reveal BOTH off and on.
//
// The §4.6 verdict in every fixture is the REAL rule (plurality + a leader ballot
// ≥ 0.6; tie / SKIP → SKIP), NEVER the converge mock's "simple majority" copy.

import { useLayoutEffect, useState } from "react";

import type { Meta, StoryObj } from "@storybook/react-vite";

import { MeetingView } from "../components/MeetingView";
import type { Perspective } from "../lib/playback";
import { OMNISCIENT } from "../lib/playback";
import { useReplayStore } from "../store/replayStore";
import { tokens } from "../tokens";
import type {
  BallotView,
  ContradictionView,
  GateView,
  MapLayoutView,
  MeetingView as MeetingViewDTO,
  PlayerView,
  ReplayView,
  StatementClaimView,
  TurnView,
} from "../types/api";

// p-2 + p-5 are the impostors (matching the converge render). Identity colour is
// the Playful identity palette — never role/guilt.
const IMPOSTORS = new Set(["p-2", "p-5"]);
const PLAYERS: PlayerView[] = Array.from({ length: 9 }, (_, i) => ({
  agent_id: `p-${i}`,
  display_name: `Agent ${i}`,
  role: IMPOSTORS.has(`p-${i}`) ? "IMPOSTOR" : "CREWMATE",
  color: tokens.identity[i]!,
}));

const EMPTY_MAP: MapLayoutView = { rooms: [], vents: [], edges: [] };

function accusation(against: string, confidence: number, reason: string): StatementClaimView {
  return { type: "accusation", against, confidence, reason };
}

function alibi(subject: string, from_tick: number, to_tick: number, room: string): StatementClaimView {
  return { type: "alibi", subject, from_tick, to_tick, room, evidence: [] };
}

function turn(partial: Partial<TurnView> & Pick<TurnView, "turn_id" | "speaker" | "free_text">): TurnView {
  return {
    turn_index: 0,
    turn_kind: "opening",
    reply_to: null,
    observations: [],
    claims: [],
    fabricated_opening: false,
    ...partial,
  };
}

function ballot(
  voter: string,
  target: string,
  confidence: number,
  rationale: string,
  rewrite_reasons: string[] = [],
  // Task 16.7.1: the voter's own-episodic-observation citation, display-only.
  primary_reason_observation_id: string | null = null,
): BallotView {
  return {
    voter,
    target,
    confidence,
    primary_reason_id: null,
    primary_reason_observation_id,
    considered_alternatives: [],
    rationale_text: rationale,
    rewrite_reasons,
    rationale_text_clean: rationale,
  };
}

function meetingFixture(meeting: MeetingViewDTO): ReplayView {
  return {
    viewModelVersion: "story-fixture",
    metadata: {
      game_id: "story-meeting",
      seed: 4242,
      total_ticks: meeting.tick,
      winner: null,
      winner_reason: null,
      meeting_count: 1,
      total_cost_usd: meeting.total_cost_usd,
      prompt_versions: {},
      created_at: null,
    },
    map: EMPTY_MAP,
    players: PLAYERS,
    ticks: [],
    meetings: [meeting],
    failed_calls: [],
    // No recorded finale: these fixtures isolate ONE meeting, and their metadata
    // already says `winner: null` (Task 19.10 — `GameFinale` is nullable exactly
    // so a partial/never-ended replay states that instead of inventing an ending).
    finale: null,
  };
}

// ── Chain: the 05-meeting hero (threaded, contradictions, EJECTED p-5) ──
const CHAIN_TURNS: TurnView[] = [
  turn({
    turn_id: "t-1",
    turn_index: 0,
    speaker: "p-3",
    turn_kind: "opening",
    free_text: "I saw p-5 head toward Reactor around tick 312.",
    observations: [
      { type: "saw_player", tick: 312, subject: "p-5", room: "REACTOR", co_present: [] },
    ],
    claims: [accusation("p-5", 0.8, "spotted heading to the kill room")],
  }),
  turn({
    turn_id: "t-2",
    turn_index: 1,
    speaker: "p-5",
    turn_kind: "reply",
    reply_to: "t-1",
    free_text: "Nope — I was on reactor repair in Engineering the whole time.",
    claims: [alibi("p-5", 300, 315, "ENGINEERING")],
  }),
  turn({
    turn_id: "t-3",
    turn_index: 2,
    speaker: "p-2",
    turn_kind: "reply",
    reply_to: "t-2",
    free_text: "Could've been p-8 — they were near Labs.",
    claims: [accusation("p-8", 0.4, "near Labs around the time")],
  }),
  turn({
    turn_id: "t-4",
    turn_index: 3,
    speaker: "p-8",
    turn_kind: "reply",
    reply_to: "t-3",
    free_text: "I was in Labs alone — no one to vouch. But I didn't move.",
    claims: [alibi("p-8", 305, 315, "LABS")],
  }),
  turn({
    turn_id: "t-5",
    turn_index: 4,
    speaker: "p-4",
    turn_kind: "opt_in",
    free_text:
      "Body was in Reactor. That lines up with p-3, not p-5 — and I watched p-5 drop into the Reactor vent.",
    observations: [
      { type: "found_body", tick: 316, body_of: "p-7", room: "REACTOR" },
      // Task 19.11: the role-proving sighting. Grounded against p-4's own
      // vent-witness record, it mints the self-linked `vent_sighting` flag
      // below — the fixture's ROLE-PROOF exhibit.
      { type: "saw_vent", tick: 314, subject: "p-5", room: "REACTOR" },
    ],
  }),
];

// One flag per Task-19.11 evidence category, so the hero covers the whole
// taxonomy: role proof renders as PROOF from a single source (never `p-X ↔ p-X`
// — its two event ids reference the SAME observation by design), the
// cross-statement conflict keeps the fuchsia contradiction channel, and the
// weak-stamped flag is subordinated (smaller, muted, listed last).
const CHAIN_CONTRADICTIONS: ContradictionView[] = [
  {
    contradiction_id: "c-strong",
    kind: "alibi_vs_sighting",
    event_a_id: "turn:t-1:obs:0",
    event_b_id: "turn:t-2:claim:0",
    subjects: ["p-5", "p-3"],
    description: "p-5's Engineering alibi conflicts with p-3's Reactor sighting.",
    weak: false,
    severity: "strong",
    category: "cross_statement",
  },
  {
    contradiction_id: "c-weak",
    kind: "alibi_conflict",
    event_a_id: "turn:t-3:claim:0",
    event_b_id: "turn:t-4:claim:0",
    subjects: ["p-8"],
    description: "The redirect to p-8 is unsupported by any new evidence.",
    weak: true,
    severity: "weak",
    category: "weak_signal",
  },
  {
    contradiction_id: "c-proof",
    kind: "vent_sighting",
    // SELF-LINKED on purpose: both ids reference p-4's one spoken vent
    // observation (meetings/schemas.py:442-456), which is why rendering it as
    // `A ↔ B` produced the `p-4 (opt-in) ↔ p-4 (opt-in)` nonsense this task fixes.
    event_a_id: "turn:t-5:obs:1",
    event_b_id: "turn:t-5:obs:1",
    subjects: ["p-5"],
    description:
      "p-4 witnessed p-5 vent in REACTOR at tick 314; venting is impostor-only, and the spoken observation matches the witness's own record.",
    weak: false,
    severity: "strong",
    category: "role_proof",
  },
];

const CHAIN_BALLOTS: BallotView[] = [
  ballot("p-0", "p-5", 0.72, "The Reactor sighting plus the body location point at p-5."),
  ballot("p-1", "SKIP", 0.3, "Not confident enough to eject anyone yet.", [
    "no new evidence",
  ]),
  // Task 19.11: the ROLE-DISCLOSING guard ballot, in the shape Task 19.15 gives
  // it (no COMMITTED replay carries this sentinel — 19.15 post-dates them all).
  // p-2 and p-5 are the fixture's impostor pair, so the teammate firewall guard
  // (meetings.manager, Task 7.12) coerced p-2's ballot to SKIP. TWO things then
  // announce that pairing, and both are Omniscient-only: the `teammate_coerced`
  // chip, and the rationale BODY — Task 19.15 replaces the model's text with
  // this exact sentinel sentence (`TEAMMATE_COERCED_VOTE_RATIONALE`), whose only
  // writer is that guard, so it appears on coerced ballots and nowhere else.
  // The two fog stories below pin that BOTH stay hidden under As-agent fog with
  // the outcome reveal OFF and ON.
  ballot(
    "p-2",
    "SKIP",
    0.4,
    "[rationale redacted by the vote guard; recorded reason: no confident read this round]",
    ["teammate_coerced"],
  ),
  // Task 16.7.1: a firsthand vote — the voter cites its own episodic
  // observation, giving the "cites" chip visual story coverage.
  ballot("p-3", "p-5", 0.81, "I saw them go to Reactor myself.", [], "p-3:312:0"),
  ballot("p-4", "p-5", 0.78, "The body in Reactor breaks p-5's alibi.", ["alibi broken"]),
  ballot("p-5", "p-8", 0.55, "p-8 had no alibi."),
  ballot("p-6", "p-5", 0.66, "Two independent accounts agree on p-5."),
  ballot("p-8", "p-5", 0.59, "The Engineering claim doesn't hold."),
];

const CHAIN_GATE: GateView = {
  leader: "p-5",
  leader_max_confidence: 0.81,
  threshold: 0.6,
  passed: true,
};

const CHAIN_MEETING: MeetingViewDTO = {
  meeting_id: "m-chain",
  tick: 315,
  triggered_by: "p-4",
  trigger_kind: "body",
  outcome: "EJECTED",
  ejected_player_id: "p-5",
  turns: CHAIN_TURNS,
  ballots: CHAIN_BALLOTS,
  contradictions: CHAIN_CONTRADICTIONS,
  llm_calls: [],
  prompt_versions: {},
  total_cost_usd: 0.0123,
  gate: CHAIN_GATE,
};

// ── SingleTurn: one opening turn, no replies ──
const SINGLE_MEETING: MeetingViewDTO = {
  meeting_id: "m-single",
  tick: 120,
  triggered_by: "p-1",
  trigger_kind: "emergency",
  outcome: "EJECTED",
  ejected_player_id: "p-6",
  turns: [
    turn({
      turn_id: "s-1",
      turn_index: 0,
      speaker: "p-1",
      turn_kind: "opening",
      free_text: "Emergency — I saw p-6 vent out of MedBay at tick 118.",
      observations: [
        { type: "saw_player", tick: 118, subject: "p-6", room: "MEDBAY", co_present: [] },
      ],
      claims: [accusation("p-6", 0.9, "witnessed a vent")],
    }),
  ],
  ballots: [
    ballot("p-0", "p-6", 0.7, "p-1's account is firsthand."),
    ballot("p-2", "p-6", 0.64, "No reason to doubt the report."),
    ballot("p-3", "SKIP", 0.3, "Could be a mistake."),
    ballot("p-4", "p-6", 0.61, "Vent sightings are decisive."),
  ],
  contradictions: [],
  llm_calls: [],
  prompt_versions: {},
  total_cost_usd: 0.004,
  gate: { leader: "p-6", leader_max_confidence: 0.7, threshold: 0.6, passed: true },
};

// ── Skipped: a below-threshold gate (leader < 0.6) → SKIPPED ──
const SKIPPED_MEETING: MeetingViewDTO = {
  meeting_id: "m-skip",
  tick: 88,
  triggered_by: "p-0",
  trigger_kind: "emergency",
  outcome: "SKIPPED",
  ejected_player_id: null,
  turns: [
    turn({
      turn_id: "k-1",
      turn_index: 0,
      speaker: "p-0",
      turn_kind: "opening",
      free_text: "Something feels off, but I don't have anything concrete.",
      claims: [accusation("p-3", 0.45, "a hunch, no evidence")],
    }),
    turn({
      turn_id: "k-2",
      turn_index: 1,
      speaker: "p-3",
      turn_kind: "reply",
      reply_to: "k-1",
      free_text: "That's not fair — I was doing tasks in Admin all round.",
      claims: [alibi("p-3", 70, 88, "ADMIN")],
    }),
  ],
  ballots: [
    ballot("p-0", "p-3", 0.45, "Just a hunch."),
    ballot("p-1", "SKIP", 0.4, "No evidence."),
    ballot("p-2", "SKIP", 0.5, "Wait for more."),
    // A parse-default ballot: the loader empties `rationale_text_clean` and
    // carries the reason on the rewrite chip — the card shows the empty-rationale
    // state, never the raw audit marker.
    {
      voter: "p-4",
      target: "p-3",
      confidence: 0.4,
      primary_reason_id: null,
      primary_reason_observation_id: null,
      considered_alternatives: [],
      rationale_text: "[[VOTE_PARSE_DEFAULT]]",
      rewrite_reasons: ["vote did not parse"],
      rationale_text_clean: "",
    },
  ],
  contradictions: [],
  llm_calls: [],
  prompt_versions: {},
  total_cost_usd: 0.003,
  // Plurality leader is p-3, but the top ballot (0.45) is below the 0.6 threshold
  // → SKIPPED. NOT a "majority" tally.
  gate: { leader: "p-3", leader_max_confidence: 0.45, threshold: 0.6, passed: false },
};

// ── Ejected: a clean plurality + ≥ 0.6 ejection, no contradictions ──
const EJECTED_MEETING: MeetingViewDTO = {
  meeting_id: "m-eject",
  tick: 204,
  triggered_by: "p-2",
  trigger_kind: "body",
  outcome: "EJECTED",
  ejected_player_id: "p-2",
  turns: [
    turn({
      turn_id: "e-1",
      turn_index: 0,
      speaker: "p-6",
      turn_kind: "opening",
      free_text: "p-2 was the only one near Storage when p-1 died.",
      observations: [
        { type: "saw_player", tick: 200, subject: "p-2", room: "STORAGE", co_present: [] },
        { type: "found_body", tick: 203, body_of: "p-1", room: "STORAGE" },
      ],
      claims: [accusation("p-2", 0.85, "sole opportunity")],
    }),
    turn({
      turn_id: "e-2",
      turn_index: 1,
      speaker: "p-2",
      turn_kind: "reply",
      reply_to: "e-1",
      free_text: "I was passing through — that proves nothing.",
    }),
  ],
  ballots: [
    ballot("p-0", "p-2", 0.7, "Opportunity is clear."),
    ballot("p-3", "p-2", 0.82, "Storage proximity + body."),
    ballot("p-4", "p-2", 0.66, "Agreed."),
    ballot("p-6", "p-2", 0.9, "I saw them there."),
    ballot("p-5", "SKIP", 0.4, "Could be circumstantial."),
  ],
  contradictions: [],
  llm_calls: [],
  prompt_versions: {},
  total_cost_usd: 0.006,
  gate: { leader: "p-2", leader_max_confidence: 0.9, threshold: 0.6, passed: true },
};

function MeetingStoryHarness({
  replay,
  meetingId,
  perspective,
  // Task 19.10's outcome reveal, seeded explicitly so the Task-19.11 firewall
  // stories can pin that the role-disclosing guard chip is gated by PERSPECTIVE
  // and is unaffected by reveal in either state.
  revealOutcome = false,
}: {
  replay: ReplayView;
  meetingId: string;
  perspective: Perspective;
  revealOutcome?: boolean;
}) {
  const [ready, setReady] = useState(false);
  useLayoutEffect(() => {
    useReplayStore.setState({
      currentReplay: replay,
      // The three split error slots (Task 19.12) — seeded explicitly so a story
      // always starts from the clean state, whatever a previously rendered story
      // left in the shared store.
      replayLoadError: null,
      memoryErrors: {},
      meetingErrors: {},
      currentTick: 0,
      isPlaying: false,
      selectedMeetingId: meetingId,
      perspective,
      revealOutcome,
      view: "workspace",
      highlightedSighting: null,
    });
    setReady(true);
  }, [replay, meetingId, perspective, revealOutcome]);
  return <div className="min-h-[820px] bg-paper-1">{ready ? <MeetingView /> : null}</div>;
}

const meta: Meta<typeof MeetingStoryHarness> = {
  title: "Meeting/MeetingView",
  component: MeetingStoryHarness,
  parameters: { layout: "fullscreen" },
};
export default meta;

type Story = StoryObj<typeof MeetingStoryHarness>;

export const Chain: Story = {
  args: { replay: meetingFixture(CHAIN_MEETING), meetingId: "m-chain", perspective: OMNISCIENT },
};

export const SingleTurn: Story = {
  args: { replay: meetingFixture(SINGLE_MEETING), meetingId: "m-single", perspective: OMNISCIENT },
};

export const Skipped: Story = {
  args: { replay: meetingFixture(SKIPPED_MEETING), meetingId: "m-skip", perspective: OMNISCIENT },
};

export const Ejected: Story = {
  args: { replay: meetingFixture(EJECTED_MEETING), meetingId: "m-eject", perspective: OMNISCIENT },
};

// The hero under As-agent fog: correctness, the post-hoc role reveal, and the
// role-disclosing `teammate_coerced` guard chip all vanish (firewall — those read
// role ground truth). The public transcript / ballots / §4.6 readout remain.
export const ChainAsAgentFog: Story = {
  args: {
    replay: meetingFixture(CHAIN_MEETING),
    meetingId: "m-chain",
    perspective: { mode: "agent", agentId: "p-3" },
    revealOutcome: false,
  },
};

// ── Task 19.11: the guard-chip perspective gate, pinned in all three states ──
//
// `teammate_coerced` in `ballot.rewrite_reasons` discloses the impostor PAIRING
// (the guard only fires on a ballot that targeted a fellow impostor). It is
// gated by PERSPECTIVE and nothing else: reveal governs OUTCOME information,
// perspective governs what the current frame may know, so a revealed ending must
// not expose the pairing through fog. p-2's SKIP ballot carries the chip.

// Omniscient — the chip renders (the spectator is the GM).
export const GuardChipOmniscient: Story = {
  args: {
    replay: meetingFixture(CHAIN_MEETING),
    meetingId: "m-chain",
    perspective: OMNISCIENT,
    revealOutcome: false,
  },
};

// As-agent fog, outcome NOT revealed — the chip is suppressed (silently: a
// "hidden" placeholder would leak the very fact being withheld).
export const GuardChipAsAgentFogUnrevealed: Story = {
  args: {
    replay: meetingFixture(CHAIN_MEETING),
    meetingId: "m-chain",
    perspective: { mode: "agent", agentId: "p-3" },
    revealOutcome: false,
  },
};

// As-agent fog, outcome REVEALED — still suppressed. Revealing who won says
// nothing about who was partnered with whom in this frame.
export const GuardChipAsAgentFogRevealed: Story = {
  args: {
    replay: meetingFixture(CHAIN_MEETING),
    meetingId: "m-chain",
    perspective: { mode: "agent", agentId: "p-3" },
    revealOutcome: true,
  },
};
