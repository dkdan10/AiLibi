// Tournament Dashboard view (Task 12.10; design/phase-12/stage-1-design.md §3.6,
// slice 8; DESIGN.md §11.3). The "Tournament" top-level view the App.tsx route
// mounts (`<TournamentDashboard/>`), refreshed onto the Playful cream/ink system.
//
// It renders the merged `TournamentEvalReport`: the balance outcome, the four
// Phase 5 metrics (vote correctness, accusation calibration, alibi fabrication,
// cost), and — newly surfaced — the typed `conversion` + `gate_metrics` blocks.
// An interestingness histogram (from `/eval/rubric`) deep-links each score bucket
// into the Highlights reel via the SHARED filter keys 12.9 reads
// (`view=highlights` · `set` · `scoreBucket`), never an invented param.
//
// Binding honesty rule ("no false precision", design/phase-12/claude-design-brief
// .md): every under-powered / sentinel number renders its caveat ATTACHED — the
// small-n vote-correctness flag, the low-power / populated-bins calibration
// badges, and the conversion / gate sentinels each carry their qualifier in
// place, never as a bare metric.
//
// Split (mirrors the sibling chrome slices): `TournamentDashboard` is the
// connected component (store + rubric fetch); `TournamentDashboardView` is the
// pure presentational surface the Storybook story drives.

import { useCallback, useEffect, useState } from "react";
import type { ReactNode } from "react";

import { useTournamentStore } from "../store/tournamentStore";
import type {
  CostDashboard,
  GameReport,
  RubricView,
  TournamentEvalReport,
} from "../types/api";
import { CalibrationCurve } from "./CalibrationCurve";
import { MetricCaveat } from "./MetricCaveat";
import { StatTile } from "./StatTile";

// ---------------------------------------------------------------------------
// Formatting helpers (null-safe: a missing/undefined rate is "n/a", never NaN)
// ---------------------------------------------------------------------------

function formatPct(value: number | null): string {
  return value === null ? "n/a" : `${(value * 100).toFixed(1)}%`;
}

function formatUsd(value: number): string {
  return `$${value.toFixed(4)}`;
}

function formatInt(value: number): string {
  return value.toLocaleString("en-US");
}

// ---------------------------------------------------------------------------
// Interestingness score (0–100) → the SHARED `scoreBucket` filter key 12.9 reads
// (low/med/high). Even thirds — a neutral split (see the PR ## Decisions). The
// histogram's buckets ARE the deep-link units, so they map 1:1 onto `scoreBucket`.
// ---------------------------------------------------------------------------

export type ScoreBucket = "low" | "med" | "high";

const SCORE_BUCKET_LOW_MAX = 100 / 3; // < 33.3 → low
const SCORE_BUCKET_HIGH_MIN = 200 / 3; // >= 66.7 → high

function scoreBucketOf(score: number): ScoreBucket {
  if (score < SCORE_BUCKET_LOW_MAX) return "low";
  if (score < SCORE_BUCKET_HIGH_MIN) return "med";
  return "high";
}

const BUCKET_ORDER: readonly ScoreBucket[] = ["low", "med", "high"];
const BUCKET_LABEL: Record<ScoreBucket, string> = {
  low: "Low",
  med: "Med",
  high: "High",
};
const BUCKET_RANGE: Record<ScoreBucket, string> = {
  low: "0–33",
  med: "33–67",
  high: "67–100",
};

// Deep-link to the Highlights reel built from the SHARED query keys 12.9 reads —
// `view=highlights` + the current `set` + `scoreBucket` — NOT an invented
// `?bucket=`. It targets the shell ROUTE (present since the 12.4 shell), so it
// degrades gracefully to an unfiltered reel if 12.9 lands second (the route still
// resolves; only the filter no-ops until 12.9 reads `scoreBucket`).
function highlightsHref(set: string, bucket: ScoreBucket): string {
  const params = new URLSearchParams();
  params.set("view", "highlights");
  if (set !== "") {
    params.set("set", set);
  }
  params.set("scoreBucket", bucket);
  const base = typeof window !== "undefined" ? window.location.pathname : "/";
  return `${base}?${params.toString()}`;
}

// ---------------------------------------------------------------------------
// Rubric fetch state (the `/eval/rubric` surface; staleness-guarded per set).
// `absent` is the 4p1i-default 404 (no rubric → first-class empty histogram).
// ---------------------------------------------------------------------------

export type RubricState =
  | { readonly status: "loading" }
  | { readonly status: "ready"; readonly view: RubricView }
  | { readonly status: "absent" }
  | { readonly status: "error"; readonly message: string };

// ---------------------------------------------------------------------------
// Presentational section primitives
// ---------------------------------------------------------------------------

function MetricSection({
  title,
  description,
  action,
  children,
}: {
  title: string;
  description: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="rounded-lg border-2 border-ink-900 bg-paper-0 p-4 shadow-chrome-1">
      <div className="mb-3 flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="text-lg text-ink-900">{title}</h3>
          <p className="mt-0.5 text-sm text-ink-500">{description}</p>
        </div>
        {action ? <div className="shrink-0">{action}</div> : null}
      </div>
      {children}
    </section>
  );
}

function TileGrid({ children }: { children: ReactNode }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
      {children}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Balance outcome summary (from the report's per-game winners)
// ---------------------------------------------------------------------------

function BalanceSummary({
  games,
  seedsAttempted,
}: {
  games: GameReport[];
  seedsAttempted: number;
}) {
  const total = games.length;
  // `winner === "CREWMATES" | "IMPOSTORS" | null`; null is the non-decisive
  // tick-budget bucket (mirrors WinnerSide | None).
  const crewWins = games.filter((g) => g.winner === "CREWMATES").length;
  const impostorWins = games.filter((g) => g.winner === "IMPOSTORS").length;
  const tickBudget = games.filter((g) => g.winner === null).length;
  const decisive = crewWins + impostorWins;
  const crewShare = decisive > 0 ? crewWins / decisive : null;

  return (
    <MetricSection
      title="Balance outcome"
      description="Crew / impostor / tick-budget split across the tournament's recorded games (DESIGN.md §11.3)."
    >
      <TileGrid>
        <StatTile
          label="Games recorded"
          value={formatInt(total)}
          hint={
            seedsAttempted !== total
              ? `${formatInt(seedsAttempted)} seeds attempted`
              : `${formatInt(seedsAttempted)} seeds`
          }
        />
        <StatTile label="Crew wins" value={formatInt(crewWins)} />
        <StatTile label="Impostor wins" value={formatInt(impostorWins)} />
        <StatTile label="Tick budget" value={formatInt(tickBudget)} hint="non-decisive" />
        <StatTile
          label="Crew win rate"
          value={formatPct(crewShare)}
          hint="of decisive games"
        />
      </TileGrid>
    </MetricSection>
  );
}

// ---------------------------------------------------------------------------
// Vote correctness — with the small-n + contradictions-ignored honesty caveats
// ---------------------------------------------------------------------------

function VoteCorrectness({
  report,
}: {
  report: TournamentEvalReport["vote_correctness"];
}) {
  // The small-n flag rides ATTACHED to the rate it qualifies (never a bare
  // number): the rate over too few impostor ejections is under-powered as a gate.
  const smallN = report.vote_correctness_small_n ? (
    <MetricCaveat
      tone="warn"
      title="Under-powered: too few impostor ejections (n < 10) to trust this rate as a gate."
    >
      small-n
    </MetricCaveat>
  ) : undefined;

  return (
    <MetricSection
      title="Vote correctness"
      description="Share of impostor ejections actually driven by real evidence (a naming contradiction or a kill-witness chain). 'n/a' when no impostors were ejected."
    >
      <TileGrid>
        <StatTile
          label="Correctness rate"
          value={formatPct(report.vote_correctness_rate)}
          hint={`${formatInt(report.evidence_backed_impostor_ejections)} / ${formatInt(report.impostor_ejections)} evidence-backed`}
          caveat={smallN}
        />
        <StatTile label="Total ejections" value={formatInt(report.total_ejections)} />
        <StatTile
          label="Impostor ejections"
          value={formatInt(report.impostor_ejections)}
        />
        <StatTile
          label="Crewmate ejections"
          value={formatInt(report.crewmate_ejections)}
        />
        <StatTile
          label="Contradictions ignored"
          value={formatInt(report.contradictions_flagged_but_ignored)}
          caveat={
            <MetricCaveat
              tone="note"
              title="Skipped meetings that carried ≥1 structured contradiction yet ejected no one — the deduction signal was present but unused."
            >
              skipped w/ a flag
            </MetricCaveat>
          }
        />
      </TileGrid>
    </MetricSection>
  );
}

// ---------------------------------------------------------------------------
// Conversion — Wave-1 leads + the SKIP-ballot sentinels (typed by 12.2)
// ---------------------------------------------------------------------------

function ConversionSection({ report }: { report: TournamentEvalReport["conversion"] }) {
  // `missed_skip_ballots` is a SENTINEL, not a down-is-good metric — it
  // partitions into impostor-voter (sanctioned adversarial play) + invalid-target
  // (normalized hallucinations) + threshold-inversions (the real gate bug). The
  // caveat carries that "read the partition, not the total" warning in place.
  return (
    <MetricSection
      title="Conversion"
      description="Did accusations convert into impostor ejections, and were the SKIPs correct? (Task 9.6 / 10.x; typed on the wire by 12.2.)"
    >
      <TileGrid>
        <StatTile
          label="Ejection accuracy"
          value={formatPct(report.ejection_accuracy)}
          hint={`${formatInt(report.impostor_ejections)} / ${formatInt(report.total_ejections)} ejections hit an impostor`}
        />
        <StatTile
          label="Accused → eject"
          value={formatPct(report.impostor_accused_conversion_rate)}
          hint={`${formatInt(report.impostor_accused_conversions)} / ${formatInt(report.impostor_accused_meetings)} accused-impostor meetings`}
        />
        <StatTile
          label="Correct skips"
          value={`${formatInt(report.correct_skip_ballots)} / ${formatInt(report.skip_ballots)}`}
          hint="below-threshold SKIPs"
        />
        <StatTile
          label="Missed skips"
          value={formatInt(report.missed_skip_ballots)}
          hint={`imp-voter ${formatInt(report.missed_skip_impostor_voters)} · invalid ${formatInt(report.missed_skip_invalid_target)} · inversion ${formatInt(report.threshold_inversions)}`}
          caveat={
            <MetricCaveat
              tone="note"
              title="A sentinel, not a down-is-good metric: most missed skips are sanctioned impostor-voter play or normalized invalid targets. Read the partition; only threshold_inversions is a real crew gate bug."
            >
              sentinel — read the split
            </MetricCaveat>
          }
        />
        <StatTile
          label="Threshold inversions"
          value={formatInt(report.threshold_inversions)}
          hint="crew gate-obedience"
          caveat={
            report.threshold_inversions > 0 ? (
              <MetricCaveat
                tone="warn"
                title="A crew voter shown a met §4.6 threshold over a living target who SKIPped anyway, with no by-design excuse — a gate-render/obedience bug, expected ~0."
              >
                gate bug — expect 0
              </MetricCaveat>
            ) : (
              <MetricCaveat tone="note">clean (0 expected)</MetricCaveat>
            )
          }
        />
      </TileGrid>
    </MetricSection>
  );
}

// ---------------------------------------------------------------------------
// Gate metrics — the Phase-10 A/B gate surface (typed by 12.2)
// ---------------------------------------------------------------------------

function GateMetricsSection({
  report,
}: {
  report: TournamentEvalReport["gate_metrics"];
}) {
  const gcc = report.genuine_class_conversion;
  return (
    <MetricSection
      title="Gate metrics"
      description="The Phase-10 progress gate surface (Task 10.4). The PRIMARY gate is genuine-class conversion — raw ejection-accuracy parity with pre-repair eras is an invalid comparison."
    >
      <TileGrid>
        <StatTile
          lead
          label="Genuine-class conversion"
          value={formatPct(gcc.conversion_rate)}
          hint={`${formatInt(gcc.converted)} / ${formatInt(gcc.supplied)} genuine-class flags converted`}
          caveat={
            <MetricCaveat
              tone="note"
              title={gcc.note}
            >
              primary gate · why not ejection-accuracy?
            </MetricCaveat>
          }
        />
        <StatTile
          label="Lost opening accusations"
          value={formatInt(report.lost_opening_accusations)}
          hint="chain died on turn 0"
        />
        <StatTile
          label="Cap-defaulted turns"
          value={formatInt(report.cap_defaulted_turns)}
          hint="deadline/token-cap truncations"
        />
        <StatTile
          label="Accused-impostor survivals"
          value={`${formatInt(report.accused_impostor_survivals)} / ${formatInt(report.accused_impostor_events)}`}
          hint={`met ${formatInt(report.survivals_rendered_met)} · sheltered ${formatInt(report.survivals_sheltered_sub_gate)} · unevidenced ${formatInt(report.survivals_unevidenced)}`}
          caveat={
            <MetricCaveat
              tone="note"
              title="The survival partition is a deception-vs-under-conversion split. 'met' survivals are CREW-conversion failures (a voter was shown a met threshold yet the table failed to eject) — NOT impostor deception; only 'sheltered' counts conversion-controlled deception credit."
            >
              met ≠ deception
            </MetricCaveat>
          }
        />
      </TileGrid>
    </MetricSection>
  );
}

// ---------------------------------------------------------------------------
// Accusation calibration — two curves, each with its own low-power caveat
// ---------------------------------------------------------------------------

function AccusationCalibration({
  report,
}: {
  report: TournamentEvalReport["accusation_calibration"];
}) {
  return (
    <MetricSection
      title="Accusation calibration"
      description="Per-confidence-bin actual-impostor rate. A well-calibrated population tracks the dashed y=x diagonal. Mid-meeting accusation claims and final vote ballots are shown separately (they are different acts)."
    >
      <div className="grid gap-4 lg:grid-cols-2">
        <CalibrationCurve
          title="Accusation claims"
          bins={report.accusation_claim_bins}
          total={report.accusation_claim_total}
          ece={report.accusation_claim_ece}
          populatedBins={report.accusation_claim_populated_bins}
          lowPower={report.accusation_claim_low_power}
          nBins={report.n_bins}
        />
        <CalibrationCurve
          title="Vote ballots"
          bins={report.vote_ballot_bins}
          total={report.vote_ballot_total}
          ece={report.vote_ballot_ece}
          populatedBins={report.vote_ballot_populated_bins}
          lowPower={report.vote_ballot_low_power}
          nBins={report.n_bins}
        />
      </div>
    </MetricSection>
  );
}

// ---------------------------------------------------------------------------
// Alibi fabrication
// ---------------------------------------------------------------------------

function AlibiFabrication({
  report,
}: {
  report: TournamentEvalReport["alibi_fabrication"];
}) {
  // survival_rate is a division-safe 0.0 when there are no impostor alibis, but
  // the rate is semantically undefined then — gate on the denominator and show
  // "n/a" so an empty tournament does not read as "0% survived".
  const rate = report.total_impostor_alibis > 0 ? report.survival_rate : null;
  return (
    <MetricSection
      title="Alibi fabrication"
      description="Share of impostor-authored alibis that survived §5.4 contradiction detection (a conservative lower bound). High = impostors getting away with fabricated cover; low = the detector catching it. 'n/a' when no impostor alibis were filed."
    >
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        <StatTile
          label="Survival rate"
          value={formatPct(rate)}
          hint={`${formatInt(report.survived)} / ${formatInt(report.total_impostor_alibis)} survived`}
        />
        <StatTile
          label="Impostor alibis"
          value={formatInt(report.total_impostor_alibis)}
        />
        <StatTile label="Survived" value={formatInt(report.survived)} />
      </div>
    </MetricSection>
  );
}

// ---------------------------------------------------------------------------
// Interestingness histogram (from /eval/rubric) — buckets deep-link to Highlights
// ---------------------------------------------------------------------------

function InterestingnessHistogram({ rubric }: { rubric: RubricState }) {
  const staleAction =
    rubric.status === "ready" && rubric.view.stale ? (
      <MetricCaveat
        tone="warn"
        title="The rubric's git_head no longer matches the served set's manifest — these scores may be stale. Re-run experiments/lab/rubric_score.py to refresh."
      >
        scores may be stale
      </MetricCaveat>
    ) : undefined;

  return (
    <MetricSection
      title="Interestingness"
      description="Distribution of the rubric's 0–100 interestingness score (9p2i). Click a bucket to open those seeds in the Highlights reel."
      action={staleAction}
    >
      {rubric.status === "loading" ? (
        <p className="text-sm text-ink-500">Loading the interestingness rubric…</p>
      ) : rubric.status === "absent" ? (
        <div className="rounded-lg border border-ink-200 bg-paper-1 px-4 py-6 text-center shadow-data">
          <p className="font-semibold text-ink-900">No interestingness rubric.</p>
          <p className="mt-1 text-sm text-ink-500">
            The default-served 4p1i set has no rubric (its games are mostly
            zero-meeting). Serve the 9p2i set, or run{" "}
            <code className="font-mono text-xs">
              experiments/lab/rubric_score.py
            </code>
            , to populate this histogram.
          </p>
        </div>
      ) : rubric.status === "error" ? (
        <p className="text-sm text-ink-500">
          Couldn&apos;t load the rubric: {rubric.message}
        </p>
      ) : (
        <HistogramBars view={rubric.view} />
      )}
    </MetricSection>
  );
}

function HistogramBars({ view }: { view: RubricView }) {
  const counts: Record<ScoreBucket, number> = { low: 0, med: 0, high: 0 };
  for (const game of view.per_game) {
    counts[scoreBucketOf(game.score)] += 1;
  }
  const total = view.per_game.length;
  const max = Math.max(1, counts.low, counts.med, counts.high);

  if (total === 0) {
    return (
      <p className="text-sm text-ink-500">
        The rubric is present but scored no games for this set.
      </p>
    );
  }

  return (
    <div>
      <div className="flex items-end gap-4">
        {BUCKET_ORDER.map((bucket) => {
          const count = counts[bucket];
          const heightPct = count > 0 ? Math.max((count / max) * 100, 6) : 2;
          return (
            <a
              key={bucket}
              href={highlightsHref(view.seedset, bucket)}
              aria-label={`Open ${count} ${BUCKET_LABEL[bucket]}-interestingness game${count === 1 ? "" : "s"} (score ${BUCKET_RANGE[bucket]}) in the Highlights reel`}
              className="group flex flex-1 flex-col items-center gap-1 rounded-md p-1 focus:outline-none focus-visible:ring-2 focus-visible:ring-ink-900"
            >
              <span className="font-mono text-xs text-ink-500">{count}</span>
              <div className="flex h-28 w-full items-end">
                <div
                  className="w-full rounded-t-md border-2 border-ink-900 bg-ink-700 transition-colors group-hover:bg-ink-900"
                  style={{ height: `${heightPct}%` }}
                />
              </div>
              <span className="text-sm font-semibold text-ink-900">
                {BUCKET_LABEL[bucket]}
              </span>
              <span className="font-mono text-[10px] text-ink-400">
                score {BUCKET_RANGE[bucket]}
              </span>
            </a>
          );
        })}
      </div>
      <p className="mt-3 text-xs text-ink-500">
        {formatInt(total)} games scored on{" "}
        <span className="font-mono">{view.seedset}</span> · click a bucket to open
        it in the Highlights reel →
      </p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Cost dashboard
// ---------------------------------------------------------------------------

function CostDashboardView({ dashboard }: { dashboard: CostDashboard }) {
  const byModel = Object.entries(dashboard.by_model);
  return (
    <MetricSection
      title="Cost dashboard"
      description="Tournament LLM spend roll-up (DESIGN.md §10.4). Per-(template, version) totals OVERLAP — the full game cost is attributed once per template a game ran — so they do not sum to the tournament total."
    >
      <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatTile label="Total cost" value={formatUsd(dashboard.total_cost_usd)} />
        <StatTile
          label="Mean / game"
          value={formatUsd(dashboard.mean_cost_per_game)}
          hint="target ≈ $0.20/game"
        />
        <StatTile label="Games" value={formatInt(dashboard.game_count)} />
        <StatTile
          label="Tokens (in / out)"
          value={`${formatInt(dashboard.total_input_tokens)} / ${formatInt(dashboard.total_output_tokens)}`}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div>
          <h4 className="mb-1 text-ink-900">Per model</h4>
          {byModel.length === 0 ? (
            <p className="text-sm text-ink-500">No model spend recorded.</p>
          ) : (
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase tracking-wide text-ink-500">
                <tr>
                  <th className="py-1 pr-2 font-medium">Model</th>
                  <th className="py-1 text-right font-medium">Cost</th>
                </tr>
              </thead>
              <tbody className="font-mono text-ink-900">
                {byModel.map(([model, cost]) => (
                  <tr key={model} className="border-t border-ink-100">
                    <td className="py-1 pr-2 break-all">{model}</td>
                    <td className="py-1 text-right">{formatUsd(cost)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div>
          <h4 className="mb-1 text-ink-900">Per prompt (template · version)</h4>
          {dashboard.per_prompt_version.length === 0 ? (
            <p className="text-sm text-ink-500">No prompt-version breakdown.</p>
          ) : (
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase tracking-wide text-ink-500">
                <tr>
                  <th className="py-1 pr-2 font-medium">Template</th>
                  <th className="py-1 pr-2 font-medium">Version</th>
                  <th className="py-1 text-right font-medium">Games</th>
                  <th className="py-1 text-right font-medium">Cost</th>
                </tr>
              </thead>
              <tbody className="font-mono text-ink-900">
                {dashboard.per_prompt_version.map((row) => (
                  <tr
                    key={`${row.template_name} ${row.version}`}
                    className="border-t border-ink-100"
                  >
                    <td className="py-1 pr-2 break-all">{row.template_name}</td>
                    <td className="py-1 pr-2 break-all">{row.version}</td>
                    <td className="py-1 text-right">{formatInt(row.game_count)}</td>
                    <td className="py-1 text-right">{formatUsd(row.total_cost_usd)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </MetricSection>
  );
}

// ---------------------------------------------------------------------------
// Presentational dashboard (the surface the Storybook story drives)
// ---------------------------------------------------------------------------

export function TournamentDashboardView({
  report,
  isLoading,
  error,
  onRefresh,
  rubric,
}: {
  report: TournamentEvalReport | null;
  isLoading: boolean;
  error: string | null;
  onRefresh: () => void;
  rubric: RubricState;
}) {
  return (
    <main className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm text-ink-500">
          The latest tournament eval report (DESIGN.md §11.3): balance outcome plus
          the Phase 5 metrics, the typed conversion / gate surface, and the
          interestingness distribution.
        </p>
        <button
          type="button"
          onClick={onRefresh}
          disabled={isLoading}
          className="rounded-md border-2 border-ink-900 bg-paper-0 px-3 py-1.5 text-sm font-semibold text-ink-900 shadow-chrome-1 transition-colors hover:bg-paper-2 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? "Loading…" : "Refresh"}
        </button>
      </div>

      {report !== null ? (
        <>
          <BalanceSummary
            games={report.report.games}
            seedsAttempted={report.report.seeds_used.length}
          />
          <VoteCorrectness report={report.vote_correctness} />
          <ConversionSection report={report.conversion} />
          <GateMetricsSection report={report.gate_metrics} />
          <AccusationCalibration report={report.accusation_calibration} />
          <AlibiFabrication report={report.alibi_fabrication} />
          <InterestingnessHistogram rubric={rubric} />
          <CostDashboardView dashboard={report.cost_dashboard} />
        </>
      ) : isLoading || error === null ? (
        // Loading: a fetch is in flight, or we are still initializing (no report,
        // no error yet) — never flash the no-report panel before the first fetch.
        <p className="text-ink-500">Loading tournament report…</p>
      ) : (
        // No-report state: a definitive failure with no report. A 404 means no
        // tournament-eval-report.json exists in the configured eval dir yet; the
        // transport detail is surfaced beneath the guidance.
        <div className="rounded-lg border-2 border-ink-900 bg-paper-0 px-4 py-6 shadow-chrome-1">
          <p className="font-semibold text-ink-900">No tournament report.</p>
          <p className="mt-1 text-sm text-ink-500">
            A 404 means no{" "}
            <code className="font-mono text-xs">tournament-eval-report.json</code>{" "}
            exists in the configured eval directory yet — run a tournament with{" "}
            <code className="font-mono text-xs">scripts/run_tournament.py</code> to
            produce one.
          </p>
          <p className="mt-2 font-mono text-xs text-ink-400">{error}</p>
        </div>
      )}
    </main>
  );
}

// ---------------------------------------------------------------------------
// Connected dashboard — store (report) + the `/eval/rubric` fetch (histogram)
// ---------------------------------------------------------------------------

const RUBRIC_ENDPOINT = "/api/eval/rubric";

export function TournamentDashboard() {
  const report = useTournamentStore((s) => s.report);
  const isLoading = useTournamentStore((s) => s.isLoading);
  const error = useTournamentStore((s) => s.error);
  const loadReport = useTournamentStore((s) => s.loadReport);

  // The rubric is fetched here (not via the tournament store, which is frozen to
  // the report) — a load-time projection served per set, 404 when absent (the
  // 4p1i default). `reloadNonce` re-triggers the fetch on Refresh.
  const [rubric, setRubric] = useState<RubricState>({ status: "loading" });
  const [reloadNonce, setReloadNonce] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setRubric({ status: "loading" });
    fetch(RUBRIC_ENDPOINT, { headers: { Accept: "application/json" } })
      .then(async (response) => {
        if (cancelled) {
          return;
        }
        if (response.status === 404) {
          setRubric({ status: "absent" });
          return;
        }
        if (!response.ok) {
          setRubric({
            status: "error",
            message: `rubric request failed (status ${response.status})`,
          });
          return;
        }
        const view = (await response.json()) as RubricView;
        if (!cancelled) {
          setRubric({ status: "ready", view });
        }
      })
      .catch((cause: unknown) => {
        if (!cancelled) {
          const message = cause instanceof Error ? cause.message : String(cause);
          setRubric({ status: "error", message });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [reloadNonce]);

  // Fetch on mount (i.e. when the dashboard tab is first selected, and on each
  // re-mount) so the view reflects the latest report.
  useEffect(() => {
    void loadReport();
  }, [loadReport]);

  const handleRefresh = useCallback(() => {
    void loadReport();
    setReloadNonce((n) => n + 1);
  }, [loadReport]);

  return (
    <TournamentDashboardView
      report={report}
      isLoading={isLoading}
      error={error}
      onRefresh={handleRefresh}
      rubric={rubric}
    />
  );
}
