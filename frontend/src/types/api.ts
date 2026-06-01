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

// ---------------------------------------------------------------------------
// Tournament eval report (Task 5.7, DESIGN.md §11.3)
//
// Hand-mirrored from the frozen Pydantic models the `/eval/tournament-report`
// endpoint serves directly: `eval.meeting_quality.TournamentEvalReport` plus
// its four nested metric models (`eval.vote_correctness`,
// `eval.accusation_calibration`, `eval.alibi_fabrication`,
// `eval.cost_dashboard`) and the `eval.report_schema.TournamentReport` fields
// the dashboard reads. Keep the nullable fields faithful — `number | null`
// where the Pydantic model is `float | None` — or the dashboard silently
// renders `undefined` (see `## Decisions`: TypeScript/Pydantic drift).
// ---------------------------------------------------------------------------

// `eval.report_schema.GameCostSummary` — per-game cost roll-up. Carried on each
// GameReport; the dashboard reads the pre-aggregated `CostDashboard` instead,
// but the shape is mirrored for faithfulness.
export interface GameCostSummary {
  total_cost_usd: number;
  total_input_tokens: number;
  total_output_tokens: number;
  by_model: Record<string, number>;
}

// `eval.report_schema.GameReport` — the dashboard reads only the per-game
// outcome (`winner`, and `seed`/`final_tick`/`reason` for the per-game detail
// table). The source model also carries `roles`, `replay_ref`, `meetings`,
// `failed_calls`, `prompt_versions`, and `cost`; those feed the Python metric
// analyzers (already pre-aggregated into the metric blocks below) and are not
// read by the dashboard, so they are intentionally omitted from this mirror to
// avoid mirroring the entire meeting-transcript graph (`## Decisions`).
export interface GameReport {
  game_id: string;
  seed: number;
  winner: Winner | null;
  reason: string;
  final_tick: number | null;
}

// `eval.report_schema.TournamentReport` — the top-level artifact. `winner ===
// null` is the non-decisive tick-budget bucket (mirrors `WinnerSide | None`).
export interface TournamentReport {
  format_version: number;
  games: GameReport[];
  seeds_used: number[];
}

// `eval.vote_correctness.VoteCorrectnessReport`. `vote_correctness_rate` is
// `null` (undefined, not 0.0) when there were no impostor ejections; it is the
// evidence-backed share over the impostor-ejection denominator ONLY, so pair it
// with `ejection_accuracy` (impostor_ejections / total_ejections, the full
// denominator — `null` when there were no ejections at all) for honest accuracy.
// `vote_correctness_small_n` flags an under-powered rate (few impostor
// ejections); `contradictions_flagged_but_ignored` counts SKIPPED meetings that
// carried a contradiction yet ejected no one (audit C-C-4 / F-F-2 / gp-7).
export interface VoteCorrectnessReport {
  total_ejections: number;
  impostor_ejections: number;
  crewmate_ejections: number;
  evidence_backed_impostor_ejections: number;
  vote_correctness_rate: number | null;
  ejection_accuracy: number | null;
  vote_correctness_small_n: boolean;
  contradictions_flagged_but_ignored: number;
}

// `eval.accusation_calibration.CalibrationBin`. `actual_impostor_rate` and
// `mean_confidence` are `null` (not 0.0, not NaN) for an empty bin.
export interface CalibrationBin {
  bin_index: number;
  lo: number;
  hi: number;
  midpoint: number;
  count: number;
  impostor_hits: number;
  actual_impostor_rate: number | null;
  mean_confidence: number | null;
}

// `eval.accusation_calibration.AccusationCalibrationReport` — claim and ballot
// curves reported separately, never pooled. Each `*_ece` is `null` when the
// curve binned no accusations. Each `*_populated_bins` counts how many bins held
// a sample and `*_low_power` is `true` when that count is below the power
// threshold — an ECE from a near-degenerate (clustered) distribution is
// statistically weak (audit F-F-3 / gp-7).
export interface AccusationCalibrationReport {
  n_bins: number;
  accusation_claim_bins: CalibrationBin[];
  accusation_claim_total: number;
  accusation_claim_ece: number | null;
  accusation_claim_populated_bins: number;
  accusation_claim_low_power: boolean;
  vote_ballot_bins: CalibrationBin[];
  vote_ballot_total: number;
  vote_ballot_ece: number | null;
  vote_ballot_populated_bins: number;
  vote_ballot_low_power: boolean;
}

// `eval.alibi_fabrication.AlibiFabricationReport`. `survival_rate` is `0.0`
// (vacuous, division-safe) when there are no impostor alibis; gate
// interpretation on `total_impostor_alibis > 0`.
export interface AlibiFabricationReport {
  total_impostor_alibis: number;
  survived: number;
  survival_rate: number;
}

// `eval.cost_dashboard.PromptVersionCost`. The per-version totals OVERLAP (the
// full game cost is attributed once per template the game ran), so they do not
// sum to the tournament total — see the source module docstring.
export interface PromptVersionCost {
  template_name: string;
  version: string;
  total_cost_usd: number;
  game_count: number;
}

// `eval.cost_dashboard.CostDashboard`.
export interface CostDashboard {
  total_cost_usd: number;
  total_input_tokens: number;
  total_output_tokens: number;
  game_count: number;
  mean_cost_per_game: number;
  by_model: Record<string, number>;
  per_prompt_version: PromptVersionCost[];
}

// `eval.meeting_quality.MeetingRateReport` — Phase 7 W0.3 enablement-gate
// metric. `meeting_rate` is `null` (undefined, not 0.0) when there were no
// games; keep it `number | null` faithful to `float | None` or the dashboard
// silently renders `undefined` (see the header `## Decisions` note). The
// trigger breakdown partitions exactly: `body_report_meetings +
// emergency_meetings === meetings_total`. `emergency_meetings` is a catch-all
// (derived, not a positively-identified emergency-button count) — see the
// Python `MeetingRateReport` docstring. The OUTCOME breakdown
// (`skipped_meetings` + `ejected_meetings === meetings_total`) pairs with
// `meeting_rate` so "reached a meeting" is not mistaken for "the meeting
// resolved anything" — most meetings skip (audit F-F-5 / gp-7).
export interface MeetingRateReport {
  games_total: number;
  games_with_meeting: number;
  meeting_rate: number | null;
  meetings_total: number;
  body_report_meetings: number;
  emergency_meetings: number;
  skipped_meetings: number;
  ejected_meetings: number;
}

// `eval.meeting_quality.TournamentEvalReport` — the wrapper the endpoint serves.
export interface TournamentEvalReport {
  report: TournamentReport;
  vote_correctness: VoteCorrectnessReport;
  accusation_calibration: AccusationCalibrationReport;
  alibi_fabrication: AlibiFabricationReport;
  cost_dashboard: CostDashboard;
  meeting_rate: MeetingRateReport;
}
