// Hand-authored TypeScript mirror of the Phase 4.1 spectator DTOs defined in
// `api/schemas.py`. The Pydantic models are the source of truth; every type
// here shadows one of them one-for-one. See `## Decisions` in the task PR for
// why these are hand-authored rather than generated via `openapi-typescript`.
//
// Pydantic serializes `tuple[X, ...]` as JSON arrays, so collections are typed
// as `X[]`. `X | None` Pydantic fields become `X | null` here (required, but
// nullable). Discriminated unions mirror the `Field(discriminator="type")`
// aliases in the source.

export type PlayerRole = "CREWMATE" | "IMPOSTOR";

export type AgentAction =
  | "IDLE"
  | "MOVING"
  | "TASK"
  | "KILL"
  | "VENT"
  | "REPORT"
  | "SABOTAGE";

export type Winner = "CREWMATES" | "IMPOSTORS";

export type TriggerKind = "body" | "emergency";

export type MeetingOutcome = "EJECTED" | "SKIPPED";

export type ContradictionKind = "alibi_conflict" | "alibi_vs_sighting";

// ---------------------------------------------------------------------------
// Map + roster DTOs
// ---------------------------------------------------------------------------

export interface PositionView {
  x: number;
  y: number;
}

export interface SizeView {
  width: number;
  height: number;
}

export interface RoomView {
  id: string;
  name: string;
  position: PositionView;
  size: SizeView;
}

export interface VentView {
  id: string;
  room_id: string;
  connected_room_ids: string[];
}

export interface EdgeView {
  from_room_id: string;
  to_room_id: string;
  is_door: boolean;
}

export interface MapLayoutView {
  rooms: RoomView[];
  vents: VentView[];
  edges: EdgeView[];
}

export interface PlayerView {
  agent_id: string;
  display_name: string;
  role: PlayerRole;
  color: string;
}

// ---------------------------------------------------------------------------
// Per-tick state DTOs
// ---------------------------------------------------------------------------

export interface AgentTickStateView {
  agent_id: string;
  room_id: string | null;
  is_alive: boolean;
  is_venting: boolean;
  task_progress: number | null;
  current_action: AgentAction;
}

export interface KillEventView {
  type: "kill";
  tick: number;
  killer_id: string;
  victim_id: string;
  room_id: string;
}

export interface ReportBodyEventView {
  type: "report_body";
  tick: number;
  reporter_id: string;
  body_of: string;
  room_id: string;
}

export interface SabotageEventView {
  type: "sabotage";
  tick: number;
  kind: "lights";
  room_id: string | null;
  actor_id: string;
}

export interface TaskCompletedEventView {
  type: "task_completed";
  tick: number;
  agent_id: string;
  task_id: string;
  room_id: string;
}

export interface MeetingTriggeredEventView {
  type: "meeting_triggered";
  tick: number;
  meeting_id: string;
  triggered_by: string;
  trigger_kind: TriggerKind;
}

export type TickEventView =
  | KillEventView
  | ReportBodyEventView
  | SabotageEventView
  | TaskCompletedEventView
  | MeetingTriggeredEventView;

export interface TickView {
  tick: number;
  agent_states: AgentTickStateView[];
  events: TickEventView[];
  sabotage_active: string[];
  tasks_completed_total: number;
  tasks_required_total: number;
}

// ---------------------------------------------------------------------------
// Meeting DTOs
// ---------------------------------------------------------------------------

export interface SawPlayerView {
  type: "saw_player";
  tick: number;
  subject: string;
  room: string;
  co_present: string[];
}

export interface CompletedTaskObsView {
  type: "completed_task";
  tick: number;
  task_id: string;
  room: string;
}

export interface FoundBodyObsView {
  type: "found_body";
  tick: number;
  body_of: string;
  room: string;
}

export type ObservationClaimView =
  | SawPlayerView
  | CompletedTaskObsView
  | FoundBodyObsView;

export interface AlibiClaimView {
  type: "alibi";
  subject: string;
  from_tick: number;
  to_tick: number;
  room: string;
  evidence: string[];
}

export interface AccusationClaimView {
  type: "accusation";
  against: string;
  confidence: number;
  reason: string;
}

export interface CorroborationClaimView {
  type: "corroboration";
  supports: string;
  on_tick: number;
  reason: string;
}

export type StatementClaimView =
  | AlibiClaimView
  | AccusationClaimView
  | CorroborationClaimView;

export interface ReportView {
  agent_id: string;
  tick: number;
  observations: ObservationClaimView[];
  claims: StatementClaimView[];
  free_text: string;
}

export interface StatementView {
  statement_id: string;
  speaker: string;
  tick: number;
  round_index: number;
  target: string | null;
  claims: StatementClaimView[];
  free_text: string;
}

export interface ContradictionView {
  contradiction_id: string;
  kind: ContradictionKind;
  event_a_id: string;
  event_b_id: string;
  subjects: string[];
  description: string;
}

export interface BallotView {
  voter: string;
  target: string;
  confidence: number;
  primary_reason_id: string | null;
  considered_alternatives: string[];
  rationale_text: string;
}

export interface LLMCallView {
  call_kind: "meeting" | "trigger";
  model: string;
  prompt_template_id: string;
  prompt_text: string;
  response_text: string;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  agent_id: string | null;
}

export interface MeetingView {
  meeting_id: string;
  tick: number;
  triggered_by: string;
  trigger_kind: TriggerKind;
  outcome: MeetingOutcome;
  ejected_player_id: string | null;
  reports: ReportView[];
  statements: StatementView[];
  ballots: BallotView[];
  contradictions: ContradictionView[];
  llm_calls: LLMCallView[];
  prompt_versions: Record<string, string>;
  total_cost_usd: number;
}

// ---------------------------------------------------------------------------
// Memory + suspicion DTOs (meeting-boundary only for MVP)
// ---------------------------------------------------------------------------

export interface BeliefEntryView {
  subject: string;
  suspicion: number;
  confidence: number;
  snapshot_tick: number;
}

export interface AgentMemoryView {
  agent_id: string;
  tick: number;
  role: PlayerRole;
  tasks_completed: number;
  tasks_assigned: number;
  observations: ObservationClaimView[];
  beliefs: BeliefEntryView[];
  open_contradictions: ContradictionView[];
  rendered_memory_text: string;
}

export interface SuspicionEntryView {
  observer: string;
  subject: string;
  suspicion: number;
}

export interface SuspicionGraphView {
  tick: number;
  entries: SuspicionEntryView[];
}

// ---------------------------------------------------------------------------
// Replay-level DTOs
// ---------------------------------------------------------------------------

export interface ReplayMetadataView {
  game_id: string;
  seed: number;
  total_ticks: number;
  winner: Winner | null;
  winner_reason: string | null;
  meeting_count: number;
  total_cost_usd: number;
  prompt_versions: Record<string, string>;
  created_at: string | null;
}

export interface FailedCallView {
  meeting_id: string;
  tick: number;
  model: string;
  cost_usd: number;
  error_type: string;
  error_message: string;
}

export interface ReplayView {
  metadata: ReplayMetadataView;
  map: MapLayoutView;
  players: PlayerView[];
  ticks: TickView[];
  meetings: MeetingView[];
  failed_calls: FailedCallView[];
}

// ---------------------------------------------------------------------------
// Eval DTO
// ---------------------------------------------------------------------------

export interface EvalCostSummaryView {
  total_replays: number;
  total_cost_usd: number;
  mean_cost_per_replay: number;
  max_cost_per_replay: number;
  decisive_split: Record<string, number>;
}
