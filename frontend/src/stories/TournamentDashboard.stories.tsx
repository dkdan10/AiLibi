// Stories for the tournament dashboard (Task 12.10;
// design/phase-12/stage-1-design.md §3.6, slice 8). They drive the PRESENTATIONAL
// <TournamentDashboardView/> — the connected <TournamentDashboard/> only adds the
// store wiring + the `/eval/rubric` fetch, which Storybook can't host — with mock
// DTOs in the exact served shape, so each state + honesty requirement is visible
// in isolation:
//   • loading / loaded / no-report (the contract's state set);
//   • the typed `conversion` + `gate_metrics` blocks render;
//   • the honesty caveats ride ATTACHED — small-n (vote correctness), low-power /
//     populated-bins (calibration curves), and the conversion / gate sentinels;
//   • the interestingness histogram + its deep-link buckets, plus the absent
//     (4p1i) and stale rubric states.

import type { Meta, StoryObj } from "@storybook/react-vite";

import {
  TournamentDashboardView,
  type RubricState,
} from "../components/TournamentDashboard";
import type {
  CalibrationBin,
  RubricGameView,
  RubricView,
  TournamentEvalReport,
} from "../types/api";

// ── mock builders (realistic 9p2i numbers; see replays/samples/9p2i) ──────────

function makeBin(index: number, count: number, hits: number): CalibrationBin {
  const lo = index / 10;
  const hi = (index + 1) / 10;
  const midpoint = (lo + hi) / 2;
  return {
    bin_index: index,
    lo,
    hi,
    midpoint,
    count,
    impostor_hits: hits,
    actual_impostor_rate: count > 0 ? hits / count : null,
    mean_confidence: count > 0 ? midpoint : null,
  };
}

// 10 bins, only some populated (the rest empty → draw nothing).
function calibrationBins(
  populated: ReadonlyArray<readonly [index: number, count: number, hits: number]>,
): CalibrationBin[] {
  const byIndex = new Map(populated.map(([i, c, h]) => [i, makeBin(i, c, h)]));
  return Array.from({ length: 10 }, (_, i) => byIndex.get(i) ?? makeBin(i, 0, 0));
}

const WIN_SHAPES = [
  "eject-decided",
  "stopwatch-some-eject",
  "stopwatch-no-eject",
  "impostor-win",
] as const;

function rubricGame(seed: number, score: number): RubricGameView {
  const shape = WIN_SHAPES[seed % WIN_SHAPES.length] ?? "stopwatch-no-eject";
  return {
    seed,
    score,
    reason: score >= 67 ? "CREWMATE_EJECT" : "CREWMATE_TASKS",
    n_meetings: score >= 67 ? 3 : score >= 33 ? 2 : 1,
    win_shape: shape,
    ejected_impostors: score >= 67 ? 2 : score >= 33 ? 1 : 0,
    accused_impostors: score >= 50 ? 2 : 1,
    survived_accused: score >= 67 ? 0 : 1,
    r1_decisive: Math.min(1, score / 100 + 0.2),
    r2_deception: Math.max(0, score / 100 - 0.2),
    r3_arcs: score / 100,
    r7_legible: Math.min(1, score / 100 + 0.1),
  };
}

// A distribution skewed toward Med (real mean ≈ 45): 7 low · 12 med · 5 high.
const RUBRIC_SCORES: number[] = [
  12, 18, 22, 27, 29, 31, 33, // low (< 33.3) — 27/29/31 land low, 33 is med edge
  36, 38, 41, 42, 44, 47, 49, 52, 55, 58, 61, 64, // med
  70, 74, 79, 84, 91, // high (>= 66.7)
];

const RUBRIC_VIEW: RubricView = {
  viewModelVersion: "12.2.0",
  seedset: "9p2i",
  git_head: "1e48c40",
  manifest_sha: "1e48c40",
  stale: false,
  per_game: RUBRIC_SCORES.map((score, i) => rubricGame(i * 2 + 5, score)).sort(
    (a, b) => b.score - a.score,
  ),
};

// A small mixed balance roster (9 crew / 5 impostor / 2 tick-budget wins).
const GAMES: TournamentEvalReport["report"]["games"] = Array.from(
  { length: 16 },
  (_, i) => ({
    game_id: `g-${i}`,
    seed: i * 3 + 1,
    winner: i < 9 ? "CREWMATES" : i < 14 ? "IMPOSTORS" : null,
    reason: i < 9 ? "CREWMATE_EJECT" : i < 14 ? "IMPOSTOR_PARITY" : "TICK_BUDGET",
    final_tick: 300 + i * 7,
  }),
);

function baseReport(): TournamentEvalReport {
  return {
    report: {
      format_version: 3,
      games: GAMES,
      seeds_used: Array.from({ length: 50 }, (_, i) => i * 2 + 1),
    },
    vote_correctness: {
      total_ejections: 39,
      impostor_ejections: 33,
      crewmate_ejections: 6,
      evidence_backed_impostor_ejections: 22,
      vote_correctness_rate: 22 / 33,
      ejection_accuracy: 33 / 39,
      vote_correctness_small_n: false,
      contradictions_flagged_but_ignored: 23,
    },
    accusation_calibration: {
      n_bins: 10,
      // 6 populated bins → adequately powered (>= 5).
      accusation_claim_bins: calibrationBins([
        [2, 18, 3],
        [3, 41, 9],
        [4, 52, 17],
        [5, 39, 18],
        [6, 31, 19],
        [7, 26, 20],
      ]),
      accusation_claim_total: 207,
      accusation_claim_ece: 0.248,
      accusation_claim_populated_bins: 6,
      accusation_claim_low_power: false,
      // 4 populated bins → low power (< 5).
      vote_ballot_bins: calibrationBins([
        [5, 88, 41],
        [6, 102, 58],
        [7, 96, 64],
        [8, 63, 47],
      ]),
      vote_ballot_total: 349,
      vote_ballot_ece: 0.103,
      vote_ballot_populated_bins: 4,
      vote_ballot_low_power: true,
    },
    alibi_fabrication: {
      total_impostor_alibis: 41,
      survived: 29,
      survival_rate: 29 / 41,
    },
    cost_dashboard: {
      total_cost_usd: 9.7421,
      total_input_tokens: 1_840_220,
      total_output_tokens: 210_540,
      game_count: 50,
      mean_cost_per_game: 0.1948,
      by_model: { "qwen2.5:7b-instruct": 0.0, "claude-haiku-4-5": 9.7421 },
      per_prompt_version: [
        {
          template_name: "meeting_ballot",
          version: "v3",
          total_cost_usd: 4.81,
          game_count: 50,
        },
        {
          template_name: "crewmate_report",
          version: "v5",
          total_cost_usd: 4.93,
          game_count: 50,
        },
      ],
    },
    meeting_rate: {
      games_total: 50,
      games_with_meeting: 50,
      meeting_rate: 1.0,
      meetings_total: 114,
      body_report_meetings: 94,
      emergency_meetings: 20,
      skipped_meetings: 75,
      ejected_meetings: 39,
    },
    conversion: {
      total_ejections: 39,
      impostor_ejections: 33,
      ejection_accuracy: 33 / 39,
      impostor_accused_meetings: 99,
      impostor_accused_conversions: 32,
      impostor_accused_conversion_rate: 32 / 99,
      skip_ballots: 410,
      correct_skip_ballots: 388,
      missed_skip_ballots: 22,
      unclassified_skip_ballots: 0,
      citation_coerced_skip_ballots: 0,
      missed_skip_impostor_voters: 18,
      missed_skip_teammate_coerced: 2,
      missed_skip_invalid_target: 4,
      threshold_inversions: 0,
    },
    gate_metrics: {
      genuine_class_conversion: {
        supplied: 20,
        converted: 9,
        conversion_rate: 0.45,
        note: "genuine_class_conversion is the PRIMARY Phase-10 progress gate. Raw ejection_accuracy comparisons against pre-repair eras are INVALID: the artifact-era 0.63 was built on detector artifacts, so parity with those numbers would be railroading regained, not detection recovered.",
      },
      supplied_channel_conversion: {
        supplied: 14,
        converted: 9,
        conversion_rate: 9 / 14,
        witnessed_vent_supplied: 9,
        witnessed_vent_converted: 6,
        sighting_contradiction_supplied: 3,
        sighting_contradiction_converted: 2,
        whereabouts_lie_supplied: 4,
        whereabouts_lie_converted: 1,
        // The legacy_alibi_* cells mirror the genuine_class fixture above.
        legacy_alibi_supplied: 20,
        legacy_alibi_converted: 9,
        legacy_alibi_conversion_rate: 0.45,
        note: "supplied_channel_conversion is the Task-17.6 successor of genuine_class_conversion and the ONLY canary-eligible genuine-class cell from baseline 5 onward … it reads the RECORDED contradiction rows — witnessed vents, sighting contradictions, and whereabouts-lies — and measures the same question as the legacy cell: supplied hard evidence against a true impostor → that impostor's ejection. …",
        legacy_note: "legacy_alibi_* is the Phase-10 alibi-anchored genuine-class cell … STARVED on this substrate and NEVER a canary. …",
      },
      lost_opening_accusations: 3,
      cap_defaulted_turns: 3,
      accused_impostor_events: 101,
      accused_impostor_survivals: 75,
      survivals_rendered_met: 63,
      survivals_sheltered_sub_gate: 4,
      survivals_unevidenced: 8,
    },
  };
}

const READY_RUBRIC: RubricState = { status: "ready", view: RUBRIC_VIEW };

const meta: Meta<typeof TournamentDashboardView> = {
  title: "Dashboard/TournamentDashboard",
  component: TournamentDashboardView,
  parameters: { layout: "fullscreen" },
  args: {
    onRefresh: () => {},
  },
  decorators: [
    (Story) => (
      <div className="min-h-screen bg-paper-1 p-6 text-ink-900">
        <Story />
      </div>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof TournamentDashboardView>;

// The headline state: every metric block + the attached honesty caveats + the
// deep-linking interestingness histogram.
export const Loaded: Story = {
  args: {
    report: baseReport(),
    isLoading: false,
    error: null,
    rubric: READY_RUBRIC,
  },
};

// The same surface with the warn caveats lit: small-n vote correctness and both
// calibration curves low-power, plus a non-zero threshold inversion (sanctioned
// crew discretion since 13.13 — a note, not a warn).
export const UnderPowered: Story = {
  args: {
    report: ((): TournamentEvalReport => {
      const base = baseReport();
      return {
        ...base,
        vote_correctness: {
          ...base.vote_correctness,
          impostor_ejections: 4,
          evidence_backed_impostor_ejections: 3,
          vote_correctness_rate: 3 / 4,
          vote_correctness_small_n: true,
        },
        accusation_calibration: {
          ...base.accusation_calibration,
          accusation_claim_populated_bins: 3,
          accusation_claim_low_power: true,
        },
        conversion: { ...base.conversion, threshold_inversions: 2 },
      };
    })(),
    isLoading: false,
    error: null,
    rubric: READY_RUBRIC,
  },
};

// Loaded report, but the served set has no rubric (the 4p1i 404) — the histogram
// shows its first-class empty state.
export const NoRubric: Story = {
  args: {
    report: baseReport(),
    isLoading: false,
    error: null,
    rubric: { status: "absent" },
  },
};

// Loaded report, rubric present but stale (git_head ≠ manifest) — the histogram
// renders with a "scores may be stale" badge instead of passing them off as fresh.
export const StaleRubric: Story = {
  args: {
    report: baseReport(),
    isLoading: false,
    error: null,
    rubric: {
      status: "ready",
      view: { ...RUBRIC_VIEW, stale: true, git_head: "deadbee" },
    },
  },
};

export const Loading: Story = {
  args: {
    report: null,
    isLoading: true,
    error: null,
    rubric: { status: "loading" },
  },
};

// No tournament-eval-report.json in the eval dir yet (a 404), with the transport
// detail surfaced beneath the guidance.
export const NoReport: Story = {
  args: {
    report: null,
    isLoading: false,
    error: "API request to /api/eval/tournament-report failed (status 404): not found",
    rubric: { status: "absent" },
  },
};
