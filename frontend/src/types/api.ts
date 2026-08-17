// GENERATED FILE — do not edit by hand.
//
// Regenerate with:  uv run python scripts/gen_frontend_types.py
//
// Source of truth: the Pydantic view-model DTOs in `api/schemas.py` (plus the
// served eval report `eval.meeting_quality.TournamentEvalReport`). The
// versioned view-model contract (DESIGN.md §7) ends the hand-mirror drift:
// `scripts/check.sh` regenerates this file and fails CI on any difference, so
// the TS types cannot drift from the Python contract.
//
// Pydantic serializes `tuple[X, ...]` as JSON arrays (typed `X[]`) and
// `X | None` as `X | null` (a required-but-nullable field, matching
// tsconfig `exactOptionalPropertyTypes`). Discriminated unions carry the
// literal `type` discriminant so a `switch (e.type)` narrows to the member.

// The view-model contract version (`api.schemas.VIEW_MODEL_VERSION`,
// DESIGN.md §7) the server stamps on every payload that carries one.
// `src/api/client.ts` REJECTS a response whose `viewModelVersion`
// differs from this, so a drifted contract fails loudly at the seam
// instead of mis-rendering; client and server can only move together,
// through this generated line.
export const VIEW_MODEL_VERSION = "1";

export type PlayerRole = "CREWMATE" | "IMPOSTOR";
export type AgentAction = "IDLE" | "MOVING" | "TASK" | "KILL" | "VENT" | "REPORT" | "SABOTAGE";
export type Winner = "CREWMATES" | "IMPOSTORS";
export type TriggerKind = "body" | "emergency";
export type MeetingOutcome = "EJECTED" | "SKIPPED";
export type ContradictionKind = "alibi_conflict" | "alibi_vs_sighting" | "alibi_vs_physical" | "vent_sighting";
export type TurnKind = "opening" | "reply" | "opt_in";

export interface ReplayView {
  viewModelVersion: string;
  metadata: ReplayMetadataView;
  map: MapLayoutView;
  players: PlayerView[];
  ticks: TickView[];
  meetings: MeetingView[];
  failed_calls: FailedCallView[];
  finale: GameFinale | null;
}

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

export interface MapLayoutView {
  rooms: RoomView[];
  vents: VentView[];
  edges: EdgeView[];
}

export interface RoomView {
  id: string;
  name: string;
  position: PositionView;
  size: SizeView;
}

export interface PositionView {
  x: number;
  y: number;
}

export interface SizeView {
  width: number;
  height: number;
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

export interface PlayerView {
  agent_id: string;
  display_name: string;
  role: PlayerRole;
  color: string;
}

export interface TickView {
  tick: number;
  agent_states: AgentTickStateView[];
  events: TickEventView[];
  sabotage_active: string[];
  tasks_completed_total: number;
  tasks_required_total: number;
  bodies: BodyView[];
  sabotage: SabotageDetailView | null;
  advantage: AdvantageView;
  meeting_resolution: MeetingResolutionView | null;
}

export interface AgentTickStateView {
  agent_id: string;
  room_id: string | null;
  is_alive: boolean;
  is_venting: boolean;
  task_progress: number | null;
  current_action: AgentAction;
  visibility: AgentVisibilityView | null;
}

export interface AgentVisibilityView {
  visible_players: VisiblePlayerView[];
  visible_bodies: VisibleBodyView[];
  audible_events: AudibleEventView[];
}

export interface VisiblePlayerView {
  id: string;
  room: string;
  action: string | null;
}

export interface VisibleBodyView {
  id: string;
  room: string;
  victim_id: string;
}

export interface AudibleEventView {
  kind: "vent_use_heard" | "sabotage_alarm";
  room: string | null;
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
  kind: "lights" | "reactor";
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

export interface VentEventView {
  type: "vent";
  tick: number;
  actor_id: string;
  phase: "enter" | "exit";
  from_room_id: string;
  to_room_id: string;
  traversal_ticks: number;
}

export interface BodyView {
  body_id: string;
  victim_id: string;
  room_id: string;
  killed_by: string;
}

export interface SabotageDetailView {
  kind: "lights" | "reactor";
  remaining_ticks: number;
  affected_rooms: string[];
  repair_progress: Record<string, number>;
}

export interface AdvantageView {
  crew_alive: number;
  impostors_alive: number;
  tasks_completed: number;
  tasks_required: number;
  tasks_required_total: number;
  advantage: number;
}

export interface MeetingResolutionView {
  meeting_id: string;
  ejected_player_id: string | null;
  pre_advantage: AdvantageView;
}

export interface MeetingView {
  meeting_id: string;
  tick: number;
  triggered_by: string;
  trigger_kind: TriggerKind;
  outcome: MeetingOutcome;
  ejected_player_id: string | null;
  turns: TurnView[];
  ballots: BallotView[];
  contradictions: ContradictionView[];
  llm_calls: LLMCallView[];
  prompt_versions: Record<string, string>;
  total_cost_usd: number;
  gate: GateView;
}

export interface TurnView {
  turn_id: string;
  turn_index: number;
  speaker: string;
  turn_kind: TurnKind;
  reply_to: string | null;
  observations: ObservationClaimView[];
  claims: StatementClaimView[];
  free_text: string;
  fabricated_opening: boolean;
}

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

export interface SawVentObservationView {
  type: "saw_vent";
  tick: number;
  subject: string;
  room: string;
}

export interface WhereaboutsClaimView {
  type: "whereabouts";
  tick: number;
  room: string;
}

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

export interface BallotView {
  voter: string;
  target: string;
  confidence: number;
  primary_reason_id: string | null;
  primary_reason_observation_id: string | null;
  considered_alternatives: string[];
  rationale_text: string;
  rewrite_reasons: string[];
  rationale_text_clean: string;
}

export interface ContradictionView {
  contradiction_id: string;
  kind: ContradictionKind;
  event_a_id: string;
  event_b_id: string;
  subjects: string[];
  description: string;
  weak: boolean;
  severity: "weak" | "strong";
  category: "role_proof" | "cross_statement" | "weak_signal";
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

export interface GateView {
  leader: string | null;
  leader_max_confidence: number;
  threshold: number;
  passed: boolean;
}

export interface FailedCallView {
  meeting_id: string;
  tick: number;
  model: string;
  cost_usd: number;
  error_type: string;
  error_message: string;
}

export interface GameFinale {
  winner: Winner;
  winner_reason: string;
  final_tick: number;
  decisive_events: FinaleEventView[];
  agent_recaps: FinaleAgentRecapView[];
}

export interface FinaleEventView {
  tick: number;
  kind: "kill" | "ejection" | "meeting_skipped" | "game_end";
  actor_id: string | null;
  subject_id: string | null;
}

export interface FinaleAgentRecapView {
  agent_id: string;
  role: PlayerRole;
  alive_at_end: boolean;
  final_vote_target: string | null;
  final_vote_named_impostor: boolean | null;
  final_vote_rewritten: boolean;
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

export interface BeliefEntryView {
  subject: string;
  suspicion: number;
  confidence: number;
  snapshot_tick: number;
}

export interface BeliefFrameView {
  meeting_id: string;
  tick: number;
  entries: BeliefErrorView[];
}

export interface BeliefErrorView {
  observer: string;
  subject: string;
  suspicion: number;
  confidence: number;
  subject_is_impostor: boolean;
  error: number;
  has_belief: boolean;
}

export interface EvalCostSummaryView {
  total_replays: number;
  total_cost_usd: number;
  mean_cost_per_replay: number;
  max_cost_per_replay: number;
  decisive_split: Record<string, number>;
}

export interface SuspicionGraphView {
  tick: number;
  entries: SuspicionEntryView[];
}

export interface SuspicionEntryView {
  observer: string;
  subject: string;
  suspicion: number;
}

export interface RubricView {
  viewModelVersion: string;
  seedset: string;
  git_head: string | null;
  manifest_sha: string | null;
  stale: boolean;
  per_game: RubricGameView[];
}

export interface RubricGameView {
  seed: number;
  score: number;
  reason: string;
  n_meetings: number;
  win_shape: string;
  ejected_impostors: number;
  accused_impostors: number;
  survived_accused: number;
  r1_decisive: number;
  r2_deception: number;
  r3_arcs: number;
  r7_legible: number;
}

export interface TournamentEvalReport {
  report: TournamentReport;
  vote_correctness: VoteCorrectnessReport;
  accusation_calibration: AccusationCalibrationReport;
  alibi_fabrication: AlibiFabricationReport;
  cost_dashboard: CostDashboard;
  meeting_rate: MeetingRateReport;
  conversion: ConversionReport;
  gate_metrics: GateMetricsReport;
  deduction: DeductionMetricsReport;
}

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

export interface AlibiFabricationReport {
  total_impostor_alibis: number;
  survived: number;
  survival_rate: number | null;
}

export interface CostDashboard {
  total_cost_usd: number;
  total_input_tokens: number;
  total_output_tokens: number;
  game_count: number;
  mean_cost_per_game: number;
  by_model: Record<string, number>;
  per_prompt_version: PromptVersionCost[];
}

export interface PromptVersionCost {
  template_name: string;
  version: string;
  total_cost_usd: number;
  game_count: number;
}

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

export interface ConversionReport {
  total_ejections: number;
  impostor_ejections: number;
  ejection_accuracy: number | null;
  impostor_accused_meetings: number;
  impostor_accused_conversions: number;
  impostor_accused_conversion_rate: number | null;
  skip_ballots: number;
  correct_skip_ballots: number;
  missed_skip_ballots: number;
  unclassified_skip_ballots: number;
  citation_coerced_skip_ballots: number;
  missed_skip_impostor_voters: number;
  missed_skip_teammate_coerced: number;
  missed_skip_invalid_target: number;
  threshold_inversions: number;
}

export interface GateMetricsReport {
  genuine_class_conversion: GenuineClassConversionReport;
  supplied_channel_conversion: SuppliedChannelConversionReport;
  lost_opening_accusations: number;
  cap_defaulted_turns: number;
  accused_impostor_events: number;
  accused_impostor_survivals: number;
  survivals_rendered_met: number;
  survivals_sheltered_sub_gate: number;
  survivals_unevidenced: number;
}

export interface GenuineClassConversionReport {
  supplied: number;
  converted: number;
  conversion_rate: number | null;
  note: string;
}

export interface SuppliedChannelConversionReport {
  supplied: number;
  converted: number;
  conversion_rate: number | null;
  witnessed_vent_supplied: number;
  witnessed_vent_converted: number;
  sighting_contradiction_supplied: number;
  sighting_contradiction_converted: number;
  whereabouts_lie_supplied: number;
  whereabouts_lie_converted: number;
  legacy_alibi_supplied: number;
  legacy_alibi_converted: number;
  legacy_alibi_conversion_rate: number | null;
  note: string;
  legacy_note: string;
}

export interface DeductionMetricsReport {
  games_total: number;
  meetings_total: number;
  ejections_total: number;
  ballots_total: number;
  turns_total: number;
  evidence_taxonomy: EvidenceTaxonomyCensus;
  meeting_flag_cross_tab: MeetingFlagCrossTab;
  ejectee_proof_cross_tab: EjecteeProofCrossTab;
  weak_flag_conviction: WeakFlagConvictionCells;
  turn_ballot_consistency: TurnBallotConsistencyCells;
  public_response_coverage: PublicResponseCoverageCells;
  redirected_ballots: RedirectedBallotCells;
  scaffold_leakage: ScaffoldLeakageCells;
  witnessed_supply: WitnessedSupplyCells | null;
}

export interface EvidenceTaxonomyCensus {
  flags_total: number;
  role_proof_flags: number;
  cross_statement_flags: number;
  weak_signal_flags: number;
  meetings_with_any_flag: number;
  weak_signal_share: number | null;
}

export interface MeetingFlagCrossTab {
  meetings_total: number;
  flagged_meetings: number;
  unflagged_meetings: number;
  flagged_ejections_impostor: number;
  flagged_ejections_innocent: number;
  unflagged_ejections_impostor: number;
  unflagged_ejections_innocent: number;
  flagged_meeting_accuracy: WilsonRateCell;
  unflagged_meeting_accuracy: WilsonRateCell;
}

export interface WilsonRateCell {
  numerator: number;
  denominator: number;
  rate: number | null;
  wilson_low: number | null;
  wilson_high: number | null;
  advisory: boolean;
}

export interface EjecteeProofCrossTab {
  ejections_total: number;
  proof_present_ejections: number;
  proof_present_impostor: number;
  proof_present_innocent: number;
  non_direct_ejections: number;
  non_direct_impostor: number;
  non_direct_innocent: number;
  direct_proof_accuracy: WilsonRateCell;
  non_direct_accuracy: WilsonRateCell;
}

export interface WeakFlagConvictionCells {
  flag_named_ejections: number;
  weak_flag_only_convictions: number;
  weak_flag_only_impostor: number;
  weak_flag_only_innocent: number;
  weak_flag_only_rate: WilsonRateCell;
  weak_flag_only_innocent_share: WilsonRateCell;
}

export interface TurnBallotConsistencyCells {
  accusations_total: number;
  accusations_of_non_votable_targets: number;
  accusing_ballots: number;
  consistent_ballots: number;
  inconsistent_skip_ballots: number;
  inconsistent_other_target_ballots: number;
  inconsistent_invalid_target_ballots: number;
  excluded_no_votable_target_ballots: number;
  guard_rewritten_ballots_unwound: number;
  consistency_rate: number | null;
}

export interface PublicResponseCoverageCells {
  crew_turns: number;
  crew_turns_with_whereabouts: number;
  crew_pooled_coverage: number | null;
  crew_macro_average_coverage: number | null;
  crew_macro_meetings: number;
  impostor_turns: number;
  impostor_turns_with_whereabouts: number;
  impostor_pooled_coverage: number | null;
  impostor_macro_average_coverage: number | null;
  impostor_macro_meetings: number;
}

export interface RedirectedBallotCells {
  ballots_total: number;
  redirected_ballots: number;
  redirected_eject_ballots: number;
  redirect_coerced_skip_ballots: number;
  redirected_ballot_share: number | null;
}

export interface ScaffoldLeakageCells {
  ballots_total: number;
  impostor_ballots: number;
  crew_ballots: number;
  turns_total: number;
  model_partner_naming_ballots: number;
  model_role_statement_ballots: number;
  model_self_kill_disclosure_ballots: number;
  model_omniscient_ballots: number;
  crew_partner_naming_ballots: number;
  crew_omniscient_control_ballots: number;
  player_visible_leak_turns: number;
  model_partner_naming_rate: WilsonRateCell;
  model_omniscient_rate: WilsonRateCell;
  model_machinery_quotation_ballots: number;
  model_machinery_vocabulary_ballots: number;
  model_machinery_quotation_share: number | null;
  model_source_pre_guard_ballots: number;
  model_source_unavailable_ballots: number;
  guard_provenance_verified_ballots: number;
  guard_provenance_unverifiable_ballots: number;
  guard_marked_ballots: number;
  guard_target_rewrite_ballots: number;
  guard_preserved_omniscient_ballots: number;
  guard_preserved_omniscient_rate: WilsonRateCell;
  guard_marked_ballot_share: number | null;
}

export interface WitnessedSupplyCells {
  kills_total: number;
  crew_witnessed_kills: number;
  co_present_crew_kills: number;
  crew_witnessed_kill_rate: WilsonRateCell;
  co_present_crew_kill_rate: WilsonRateCell;
}

export type TickEventView = KillEventView | ReportBodyEventView | SabotageEventView | TaskCompletedEventView | MeetingTriggeredEventView | VentEventView;
export type ObservationClaimView = SawPlayerView | CompletedTaskObsView | FoundBodyObsView | SawVentObservationView | WhereaboutsClaimView;
export type StatementClaimView = AlibiClaimView | AccusationClaimView | CorroborationClaimView;

export interface GameReport {
  game_id: string;
  seed: number;
  winner: Winner | null;
  reason: string;
  final_tick: number | null;
}

export interface TournamentReport {
  format_version: number;
  games: GameReport[];
  seeds_used: number[];
}
