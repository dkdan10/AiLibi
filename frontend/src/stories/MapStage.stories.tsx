// Storybook story for the map stage (Task 12.5; design/phase-12/stage-1-design
// §3.2, the 02-map + 03-two-truths renders). Renders <MapView/> in both viewing
// modes against a faithful canonical_1 fixture — the fixed 10-room / 11-corridor
// / 6-vent layout — seeded into the Zustand store the component reads from:
//
//   • Omniscient — the spectator sees everything: every token + role badge, the
//     vent ring, p-7's body, p-5's vent-escape (Reactor → Storage), the kill
//     flash, and the reactor sabotage countdown + repair race.
//   • As-agent (p-3) — the fog of war: dims to EXACTLY p-3's AgentVisibilityView
//     (the cafeteria/engineering/admin it could see from East Hallway); unseen
//     rooms fog over; the vent ring, role badges, body, and vent-escape vanish —
//     proving the firewall is simulated on the canvas, not leaked.
//
// The fixture mirrors the served `ReplayView` DTO exactly (it is the same shape
// the loader emits), so the story exercises the real render paths.

import { useLayoutEffect, useState } from "react";

import type { Meta, StoryObj } from "@storybook/react-vite";

import { MapView } from "../components/MapView";
import type { Perspective } from "../lib/playback";
import { OMNISCIENT } from "../lib/playback";
import { useReplayStore } from "../store/replayStore";
import { tokens } from "../tokens";
import type {
  AgentTickStateView,
  AgentVisibilityView,
  MapLayoutView,
  PlayerView,
  ReplayView,
  TickView,
} from "../types/api";

// ── canonical_1 layout (the fixed reference; never invented/moved/renamed) ──
const ROOMS: MapLayoutView["rooms"] = [
  { id: "CAFETERIA", name: "Cafeteria", position: { x: 36, y: 4 }, size: { width: 16, height: 10 } },
  { id: "UPPER_HALL", name: "Upper Hall", position: { x: 38, y: 16 }, size: { width: 12, height: 4 } },
  { id: "ADMIN", name: "Admin", position: { x: 36, y: 22 }, size: { width: 16, height: 8 } },
  { id: "EAST_HALL", name: "East Hallway", position: { x: 56, y: 12 }, size: { width: 4, height: 14 } },
  { id: "ENGINEERING", name: "Engineering", position: { x: 64, y: 14 }, size: { width: 14, height: 10 } },
  { id: "REACTOR", name: "Reactor", position: { x: 82, y: 16 }, size: { width: 10, height: 8 } },
  { id: "STORAGE", name: "Storage", position: { x: 64, y: 26 }, size: { width: 14, height: 6 } },
  { id: "WEST_HALL", name: "West Hallway", position: { x: 30, y: 12 }, size: { width: 4, height: 14 } },
  { id: "MEDBAY", name: "MedBay", position: { x: 14, y: 14 }, size: { width: 14, height: 10 } },
  { id: "LABS", name: "Labs", position: { x: 0, y: 16 }, size: { width: 10, height: 8 } },
];

const VENTS: MapLayoutView["vents"] = [
  { id: "REACTOR_VENT", room_id: "REACTOR", connected_room_ids: ["STORAGE", "ADMIN"] },
  { id: "STORAGE_VENT", room_id: "STORAGE", connected_room_ids: ["REACTOR", "ENGINEERING"] },
  { id: "ENGINEERING_VENT", room_id: "ENGINEERING", connected_room_ids: ["STORAGE", "LABS"] },
  { id: "ADMIN_VENT", room_id: "ADMIN", connected_room_ids: ["REACTOR", "MEDBAY"] },
  { id: "MEDBAY_VENT", room_id: "MEDBAY", connected_room_ids: ["ADMIN", "LABS"] },
  { id: "LABS_VENT", room_id: "LABS", connected_room_ids: ["ENGINEERING", "MEDBAY"] },
];

const EDGE_PAIRS: ReadonlyArray<[string, string]> = [
  ["CAFETERIA", "UPPER_HALL"],
  ["UPPER_HALL", "ADMIN"],
  ["CAFETERIA", "EAST_HALL"],
  ["EAST_HALL", "ENGINEERING"],
  ["ENGINEERING", "REACTOR"],
  ["ENGINEERING", "STORAGE"],
  ["ADMIN", "EAST_HALL"],
  ["CAFETERIA", "WEST_HALL"],
  ["WEST_HALL", "MEDBAY"],
  ["MEDBAY", "LABS"],
  ["ADMIN", "WEST_HALL"],
];

const MAP: MapLayoutView = {
  rooms: ROOMS,
  vents: VENTS,
  edges: EDGE_PAIRS.map(([a, b]) => ({ from_room_id: a, to_room_id: b, is_door: true })),
};

// p-2 + p-5 are the impostors (matching the converge render). Identity colour is
// the Playful identity palette — never role/guilt.
const IMPOSTORS = new Set(["p-2", "p-5"]);
const PLAYERS: PlayerView[] = ROOMS.map((_, i) => i).slice(0, 9).map((i) => ({
  agent_id: `p-${i}`,
  display_name: `Agent ${i}`,
  role: IMPOSTORS.has(`p-${i}`) ? "IMPOSTOR" : "CREWMATE",
  color: tokens.identity[i]!,
}));

const EMPTY_VIS: AgentVisibilityView = {
  visible_players: [],
  visible_bodies: [],
  audible_events: [],
};

// p-3's firewall-filtered field of view from East Hallway: the adjacent
// cafeteria / engineering / admin it can see, plus the global sabotage alarm it
// can hear. It CANNOT see the reactor (body, kill, p-5's vent) — those fog over.
const P3_VIS: AgentVisibilityView = {
  visible_players: [
    { id: "p-0", room: "CAFETERIA", action: null },
    { id: "p-6", room: "CAFETERIA", action: null },
    { id: "p-2", room: "ENGINEERING", action: null },
    { id: "p-4", room: "ADMIN", action: null },
  ],
  visible_bodies: [],
  audible_events: [{ kind: "sabotage_alarm", room: null }],
};

interface Spawn {
  id: string;
  room: string | null;
  alive: boolean;
  venting: boolean;
  action: AgentTickStateView["current_action"];
}

// The seven crewmates whose positions are stable across the demo window; the
// impostor p-5 (the killer/venter) and victim p-7 vary by tick below.
const STABLE: Spawn[] = [
  { id: "p-0", room: "CAFETERIA", alive: true, venting: false, action: "IDLE" },
  { id: "p-1", room: "MEDBAY", alive: true, venting: false, action: "TASK" },
  { id: "p-2", room: "ENGINEERING", alive: true, venting: false, action: "TASK" },
  { id: "p-3", room: "EAST_HALL", alive: true, venting: false, action: "MOVING" },
  { id: "p-4", room: "ADMIN", alive: true, venting: false, action: "TASK" },
  { id: "p-6", room: "CAFETERIA", alive: true, venting: false, action: "IDLE" },
  { id: "p-8", room: "LABS", alive: true, venting: false, action: "TASK" },
];

const P7_DEAD: Spawn = { id: "p-7", room: null, alive: false, venting: false, action: "IDLE" };

function agentState(spawn: Spawn): AgentTickStateView {
  return {
    agent_id: spawn.id,
    room_id: spawn.room,
    is_alive: spawn.alive,
    is_venting: spawn.venting,
    task_progress: spawn.alive && !IMPOSTORS.has(spawn.id) ? 0.5 : null,
    current_action: spawn.action,
    visibility: !spawn.alive ? null : spawn.id === "p-3" ? P3_VIS : EMPTY_VIS,
  };
}

const REACTOR_BODY = { body_id: "b-7", victim_id: "p-7", room_id: "REACTOR", killed_by: "p-5" };
const REACTOR_SABOTAGE = {
  kind: "reactor" as const,
  remaining_ticks: 4,
  affected_rooms: ["REACTOR", "ENGINEERING"],
  repair_progress: { ENGINEERING: 2 },
};

function playStates(p5: Spawn): AgentTickStateView[] {
  return [...STABLE, p5, P7_DEAD].map(agentState);
}

// The vent escape spans real engine events: a KILL (t313), then the dive
// (VentEntered t314 — from == to, the dive room) and the emerge (VentExited t315
// — REACTOR → STORAGE, the real cross-room travel). The map pairs enter+exit so
// the animation glides the true route. The stories render the in-vent tick (t314).
const T_KILL = 313;
const T_ENTER = 314;
const T_EXIT = 315;

// `meeting_resolution: null` on every frame below (Task 19.10): this fixture holds
// no meetings (`FIXTURE.meetings: []`), and the label is present ONLY on a frame
// whose meeting has resolved — it is what tells the UI that such a frame's
// `agent_states` are the PRE-vote roster while its `advantage` is already
// post-vote. Null here is the honest value, not a placeholder.

const TICK_KILL: TickView = {
  tick: T_KILL,
  agent_states: playStates({ id: "p-5", room: "REACTOR", alive: true, venting: false, action: "KILL" }),
  events: [{ type: "kill", tick: T_KILL, killer_id: "p-5", victim_id: "p-7", room_id: "REACTOR" }],
  sabotage_active: ["reactor"],
  tasks_completed_total: 5,
  tasks_required_total: 14,
  bodies: [REACTOR_BODY],
  sabotage: REACTOR_SABOTAGE,
  advantage: { crew_alive: 6, impostors_alive: 2, tasks_completed: 5, tasks_required: 14, tasks_required_total: 14, advantage: -0.12 },
  meeting_resolution: null,
};

const TICK_ENTER: TickView = {
  tick: T_ENTER,
  agent_states: playStates({ id: "p-5", room: null, alive: true, venting: true, action: "VENT" }),
  events: [
    {
      type: "vent",
      tick: T_ENTER,
      actor_id: "p-5",
      phase: "enter",
      from_room_id: "REACTOR", // dive: from == to (the entered vent is in the room)
      to_room_id: "REACTOR",
      traversal_ticks: 1,
    },
  ],
  sabotage_active: ["reactor"],
  tasks_completed_total: 5,
  tasks_required_total: 14,
  bodies: [REACTOR_BODY],
  sabotage: REACTOR_SABOTAGE,
  advantage: { crew_alive: 6, impostors_alive: 2, tasks_completed: 5, tasks_required: 14, tasks_required_total: 14, advantage: -0.12 },
  meeting_resolution: null,
};

const TICK_EXIT: TickView = {
  tick: T_EXIT,
  agent_states: playStates({ id: "p-5", room: "STORAGE", alive: true, venting: false, action: "IDLE" }),
  events: [
    {
      type: "vent",
      tick: T_EXIT,
      actor_id: "p-5",
      phase: "exit",
      from_room_id: "REACTOR", // emerge: REACTOR → STORAGE, the real travel
      to_room_id: "STORAGE",
      traversal_ticks: 1,
    },
  ],
  sabotage_active: ["reactor"],
  tasks_completed_total: 5,
  tasks_required_total: 14,
  bodies: [REACTOR_BODY],
  sabotage: REACTOR_SABOTAGE,
  advantage: { crew_alive: 6, impostors_alive: 2, tasks_completed: 5, tasks_required: 14, tasks_required_total: 14, advantage: -0.12 },
  meeting_resolution: null,
};

// Everyone spawns alive in the Cafeteria (the loader's synthetic pre-game frame).
const START_SPAWNS: Spawn[] = [...STABLE.map((s) => s.id), "p-5", "p-7"].map(
  (id): Spawn => ({ id, room: "CAFETERIA", alive: true, venting: false, action: "IDLE" }),
);

const START_TICK: TickView = {
  tick: -1,
  agent_states: START_SPAWNS.map(agentState),
  events: [],
  sabotage_active: [],
  tasks_completed_total: 0,
  tasks_required_total: 14,
  bodies: [],
  sabotage: null,
  advantage: { crew_alive: 7, impostors_alive: 2, tasks_completed: 0, tasks_required: 14, tasks_required_total: 14, advantage: 0.05 },
  meeting_resolution: null,
};

// Index 3 = TICK_EXIT (engine tick 315) — p-5 has just emerged, so the traveller
// sits at STORAGE with the full REACTOR → STORAGE route trail (tick-anchored, so
// the position matches replay time), and the reactor body + sabotage persist.
const PLAY_INDEX = 3;

const FIXTURE: ReplayView = {
  viewModelVersion: "story-fixture",
  metadata: {
    game_id: "story-canonical_1",
    seed: 4242,
    total_ticks: T_EXIT,
    winner: null,
    winner_reason: null,
    meeting_count: 0,
    total_cost_usd: 0,
    prompt_versions: {},
    created_at: null,
  },
  map: MAP,
  players: PLAYERS,
  ticks: [START_TICK, TICK_KILL, TICK_ENTER, TICK_EXIT],
  meetings: [],
  failed_calls: [],
  // The fixture is a mid-game slice (it ends on the vent emerge, not on a
  // `game_over`), and its metadata already says `winner: null` — so there is no
  // recorded finale to mirror (Task 19.10).
  finale: null,
};

// Seed the store, then render the stage (the component reads currentReplay /
// currentTick / perspective from the store, exactly as in the app).
function MapStoryHarness({ perspective }: { perspective: Perspective }) {
  const [ready, setReady] = useState(false);
  useLayoutEffect(() => {
    useReplayStore.setState({
      currentReplay: FIXTURE,
      currentReplayError: null,
      currentTick: PLAY_INDEX, // the emergence tick (engine tick 315)
      isPlaying: false,
      perspective,
      view: "workspace",
    });
    setReady(true);
  }, [perspective]);
  return (
    <div className="min-h-[560px] bg-paper-1 p-6">{ready ? <MapView /> : null}</div>
  );
}

const meta: Meta<typeof MapStoryHarness> = {
  title: "Map/MapStage",
  component: MapStoryHarness,
  parameters: { layout: "fullscreen" },
};
export default meta;

type Story = StoryObj<typeof MapStoryHarness>;

export const Omniscient: Story = {
  args: { perspective: OMNISCIENT },
};

export const AsAgentFog: Story = {
  args: { perspective: { mode: "agent", agentId: "p-3" } },
};
