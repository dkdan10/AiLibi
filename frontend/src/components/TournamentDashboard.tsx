// Tournament Dashboard view (Task 5.7, DESIGN.md §11.3, §7). The second
// top-level view of the spectator app (reached by the App.tsx tab nav), backed
// by its own `useTournamentStore` and the `/eval/tournament-report` endpoint.
//
// It renders the merged `TournamentEvalReport`: the balance outcome summary
// (from the report's per-game winners) plus the four Phase 5 metrics — vote
// correctness, accusation calibration (claim + ballot curves, shown
// separately), alibi-fabrication survival, and the cost dashboard. Per the
// task contract these are plain React + CSS/SVG data widgets (tables, bars, a
// rate-vs-confidence calibration curve, a cost breakdown) — NOT PixiJS, which
// is the map renderer, and no new charting dependency. Every metric's
// `null`/empty state renders an explicit "n/a"/"no data" rather than NaN.

import { useEffect } from "react";
import type { ReactNode } from "react";

import { useTournamentStore } from "../store/tournamentStore";
import type {
  CalibrationBin,
  CostDashboard,
  GameReport,
  TournamentEvalReport,
} from "../types/api";

// ---------------------------------------------------------------------------
// Formatting helpers (null-safe: a missing/undefined rate is "n/a", never NaN)
// ---------------------------------------------------------------------------

function formatPct(value: number | null): string {
  if (value === null) {
    return "n/a";
  }
  return `${(value * 100).toFixed(1)}%`;
}

function formatUsd(value: number): string {
  return `$${value.toFixed(4)}`;
}

function formatInt(value: number): string {
  return value.toLocaleString("en-US");
}

function formatEce(value: number | null): string {
  return value === null ? "n/a" : value.toFixed(3);
}

// ---------------------------------------------------------------------------
// Presentational primitives
// ---------------------------------------------------------------------------

function MetricSection({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <section className="rounded-lg border border-slate-700 bg-slate-800/40 p-4">
      <h3 className="text-lg font-semibold text-slate-100">{title}</h3>
      <p className="mb-3 text-sm text-slate-400">{description}</p>
      {children}
    </section>
  );
}

function StatTile({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <div className="rounded border border-slate-700 bg-slate-900/60 px-4 py-3">
      <div className="text-xs uppercase tracking-wide text-slate-400">
        {label}
      </div>
      <div className="font-mono text-2xl text-slate-100">{value}</div>
      {hint !== undefined && (
        <div className="mt-0.5 text-xs text-slate-500">{hint}</div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Balance outcome summary (from the report's per-game winners)
// ---------------------------------------------------------------------------

function BalanceSummary({ games, seedsAttempted }: {
  games: GameReport[];
  seedsAttempted: number;
}) {
  const total = games.length;
  // `winner === "CREWMATES" | "IMPOSTORS" | null`; null is the non-decisive
  // tick-budget bucket (mirrors WinnerSide | None). This is exactly how the
  // tournament runner's BalanceReport buckets reduce out of `winner`.
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
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        <StatTile label="Games recorded" value={formatInt(total)} hint={
          seedsAttempted !== total
            ? `${formatInt(seedsAttempted)} seeds attempted`
            : `${formatInt(seedsAttempted)} seeds`
        } />
        <StatTile label="Crew wins" value={formatInt(crewWins)} />
        <StatTile label="Impostor wins" value={formatInt(impostorWins)} />
        <StatTile label="Tick budget" value={formatInt(tickBudget)} hint="non-decisive" />
        <StatTile
          label="Crew win rate"
          value={formatPct(crewShare)}
          hint="of decisive games"
        />
      </div>
    </MetricSection>
  );
}

// ---------------------------------------------------------------------------
// Vote correctness
// ---------------------------------------------------------------------------

function VoteCorrectness({
  report,
}: {
  report: TournamentEvalReport["vote_correctness"];
}) {
  return (
    <MetricSection
      title="Vote correctness"
      description="Share of impostor ejections actually driven by real evidence (a naming contradiction or a kill-witness chain). 'n/a' when no impostors were ejected."
    >
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        <StatTile
          label="Correctness rate"
          value={formatPct(report.vote_correctness_rate)}
          hint={`${formatInt(report.evidence_backed_impostor_ejections)} / ${formatInt(report.impostor_ejections)} evidence-backed`}
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
          label="Evidence-backed"
          value={formatInt(report.evidence_backed_impostor_ejections)}
        />
      </div>
    </MetricSection>
  );
}

// ---------------------------------------------------------------------------
// Accusation calibration curve (rate vs confidence)
// ---------------------------------------------------------------------------

function CalibrationCurve({
  title,
  bins,
  total,
  ece,
}: {
  title: string;
  bins: CalibrationBin[];
  total: number;
  ece: number | null;
}) {
  // Plot area is a 100×100 square (y inverted); a square container keeps the
  // y=x perfect-calibration diagonal at 45°. x = confidence (bin midpoint),
  // y (bar height) = actual impostor rate. Empty bins (rate === null) draw
  // nothing; populated bins draw a bar plus a dot, so a populated rate-0 bin
  // (dot at the baseline) is distinguishable from an empty bin (nothing).
  const n = bins.length;
  const barWidth = n > 0 ? (100 / n) * 0.7 : 0;
  const populated = bins.filter((b) => b.actual_impostor_rate !== null).length;

  return (
    <div className="rounded border border-slate-700 bg-slate-900/60 p-3">
      <div className="mb-2 flex items-baseline justify-between gap-2">
        <h4 className="font-semibold text-slate-200">{title}</h4>
        <span className="font-mono text-xs text-slate-400">ECE {formatEce(ece)}</span>
      </div>
      <div className="flex gap-2">
        <div className="flex flex-col justify-between py-1 text-right text-[10px] text-slate-500">
          <span>1.0</span>
          <span>rate</span>
          <span>0.0</span>
        </div>
        <div className="aspect-square w-full max-w-xs">
          <svg
            viewBox="0 0 100 100"
            className="h-full w-full rounded bg-slate-950/60"
            role="img"
            aria-label={`${title}: actual impostor rate versus stated confidence, ${total} accusations`}
          >
            {/* Perfect-calibration reference diagonal (y = x). */}
            <line
              x1="0"
              y1="100"
              x2="100"
              y2="0"
              stroke="#475569"
              strokeWidth="0.6"
              strokeDasharray="3 3"
            />
            {bins.map((bin) => {
              const rate = bin.actual_impostor_rate;
              if (rate === null) {
                return null;
              }
              const cx = bin.midpoint * 100;
              const barHeight = rate * 100;
              const tooltip =
                `conf [${bin.lo.toFixed(2)}–${bin.hi.toFixed(2)}${bin.bin_index === n - 1 ? "]" : ")"}: ` +
                `rate ${rate.toFixed(2)} (${bin.impostor_hits}/${bin.count})` +
                (bin.mean_confidence !== null
                  ? `, mean conf ${bin.mean_confidence.toFixed(2)}`
                  : "");
              return (
                <g key={bin.bin_index}>
                  <rect
                    x={cx - barWidth / 2}
                    y={100 - barHeight}
                    width={barWidth}
                    height={barHeight}
                    fill="#0ea5e9"
                    opacity={0.55}
                  >
                    <title>{tooltip}</title>
                  </rect>
                  <circle cx={cx} cy={100 - barHeight} r="1.6" fill="#38bdf8">
                    <title>{tooltip}</title>
                  </circle>
                </g>
              );
            })}
          </svg>
        </div>
      </div>
      <div className="mt-1 pl-7 text-[10px] text-slate-500">
        confidence (bin midpoint) 0 → 1
      </div>
      <p className="mt-2 text-xs text-slate-400">
        {total === 0
          ? "No accusations recorded — empty calibration curve."
          : `${formatInt(total)} accusations across ${formatInt(populated)} populated bins.`}
      </p>
    </div>
  );
}

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
        />
        <CalibrationCurve
          title="Vote ballots"
          bins={report.vote_ballot_bins}
          total={report.vote_ballot_total}
          ece={report.vote_ballot_ece}
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
          <h4 className="mb-1 font-semibold text-slate-200">Per model</h4>
          {byModel.length === 0 ? (
            <p className="text-sm text-slate-500">No model spend recorded.</p>
          ) : (
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase tracking-wide text-slate-400">
                <tr>
                  <th className="py-1 pr-2 font-medium">Model</th>
                  <th className="py-1 text-right font-medium">Cost</th>
                </tr>
              </thead>
              <tbody className="font-mono text-slate-200">
                {byModel.map(([model, cost]) => (
                  <tr key={model} className="border-t border-slate-800">
                    <td className="py-1 pr-2 break-all">{model}</td>
                    <td className="py-1 text-right">{formatUsd(cost)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div>
          <h4 className="mb-1 font-semibold text-slate-200">
            Per prompt (template · version)
          </h4>
          {dashboard.per_prompt_version.length === 0 ? (
            <p className="text-sm text-slate-500">No prompt-version breakdown.</p>
          ) : (
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase tracking-wide text-slate-400">
                <tr>
                  <th className="py-1 pr-2 font-medium">Template</th>
                  <th className="py-1 pr-2 font-medium">Version</th>
                  <th className="py-1 text-right font-medium">Games</th>
                  <th className="py-1 text-right font-medium">Cost</th>
                </tr>
              </thead>
              <tbody className="font-mono text-slate-200">
                {dashboard.per_prompt_version.map((row) => (
                  <tr
                    key={`${row.template_name} ${row.version}`}
                    className="border-t border-slate-800"
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
// Top-level dashboard
// ---------------------------------------------------------------------------

export function TournamentDashboard() {
  const report = useTournamentStore((s) => s.report);
  const isLoading = useTournamentStore((s) => s.isLoading);
  const error = useTournamentStore((s) => s.error);
  const loadReport = useTournamentStore((s) => s.loadReport);

  // Fetch on mount (i.e. when the dashboard tab is first selected, and on each
  // re-mount) so the view reflects the latest tournament-eval-report.json.
  useEffect(() => {
    void loadReport();
  }, [loadReport]);

  return (
    <main className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm text-slate-400">
          The latest tournament eval report (DESIGN.md §11.3): balance outcome
          plus the four Phase 5 metrics.
        </p>
        <button
          type="button"
          onClick={() => {
            void loadReport();
          }}
          disabled={isLoading}
          className="rounded border border-slate-700 bg-slate-800 px-3 py-1.5 text-sm text-slate-100 transition-colors hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? "Loading…" : "Refresh"}
        </button>
      </div>

      {error !== null && (
        <div className="rounded border border-red-700 bg-red-950 px-4 py-3 text-red-200">
          <p className="font-semibold">Failed to load tournament report.</p>
          <p className="mt-1 text-sm">{error}</p>
          <p className="mt-1 text-xs text-red-300/80">
            A 404 means no <code>tournament-eval-report.json</code> exists in the
            configured eval directory yet — run a tournament with{" "}
            <code>scripts/run_tournament.py</code> to produce one.
          </p>
        </div>
      )}

      {report === null ? (
        error === null && (
          <p className="text-slate-400">Loading tournament report…</p>
        )
      ) : (
        <>
          <BalanceSummary
            games={report.report.games}
            seedsAttempted={report.report.seeds_used.length}
          />
          <VoteCorrectness report={report.vote_correctness} />
          <AccusationCalibration report={report.accusation_calibration} />
          <AlibiFabrication report={report.alibi_fabrication} />
          <CostDashboardView dashboard={report.cost_dashboard} />
        </>
      )}
    </main>
  );
}
