// CalibrationCurve — actual-impostor-rate vs stated-confidence (Task 12.10;
// design/phase-12/stage-1-design.md §3.6; DESIGN.md §11.3). Presentational.
//
// A well-calibrated population tracks the dashed y = x diagonal. The plot area is
// a 100×100 square (y inverted) so the diagonal sits at 45°; x = confidence (bin
// midpoint), bar height = actual impostor rate. Empty bins (rate === null) draw
// nothing; populated bins draw a bar plus a dot, so a populated rate-0 bin (dot
// at the baseline) is distinguishable from an empty bin (nothing).
//
// Firewall / honesty: the chart is meta-analytics, not a game semantic, so it is
// drawn in NEUTRAL ink — it must not borrow the reserved suspicion/trust/kill
// hues. The `low-power` / `populated-bins` caveat rides ATTACHED in the header
// (the binding "no false precision" rule): a curve over too few populated bins is
// flagged in place, never shown as if it were a trustworthy calibration.

import { tokens } from "../tokens";
import type { CalibrationBin } from "../types/api";
import { MetricCaveat } from "./MetricCaveat";

function formatEce(value: number | null): string {
  return value === null ? "n/a" : value.toFixed(3);
}

export function CalibrationCurve({
  title,
  bins,
  total,
  ece,
  populatedBins,
  lowPower,
  nBins,
}: {
  title: string;
  bins: CalibrationBin[];
  total: number;
  ece: number | null;
  populatedBins: number;
  lowPower: boolean;
  nBins: number;
}) {
  const n = bins.length;
  const barWidth = n > 0 ? (100 / n) * 0.7 : 0;

  return (
    <div className="rounded-lg border border-ink-200 bg-paper-0 p-3 shadow-data">
      <div className="mb-1 flex items-baseline justify-between gap-2">
        <h4 className="text-ink-900">{title}</h4>
        <span
          className="font-mono text-xs text-ink-500"
          title="Expected Calibration Error (lower is better)"
        >
          ECE {formatEce(ece)}
        </span>
      </div>

      {/* Honesty caveat, ATTACHED to the curve: how many of its bins held a
          sample, and a louder badge when that count is too low to trust. */}
      <div className="mb-2 flex flex-wrap gap-1">
        <MetricCaveat
          tone={lowPower ? "warn" : "note"}
          title={
            `${populatedBins} of ${nBins} confidence bins held a sample.` +
            (lowPower
              ? " Too few to trust the calibration — read the ECE with care."
              : "")
          }
        >
          {populatedBins}/{nBins} bins populated{lowPower ? " · low power" : ""}
        </MetricCaveat>
      </div>

      <div className="flex gap-2">
        <div className="flex flex-col justify-between py-1 text-right text-[10px] text-ink-400">
          <span>1.0</span>
          <span>rate</span>
          <span>0.0</span>
        </div>
        <div className="aspect-square w-full max-w-xs">
          <svg
            viewBox="0 0 100 100"
            className="h-full w-full rounded-md"
            style={{ backgroundColor: tokens.paper[1] }}
            role="img"
            aria-label={`${title}: actual impostor rate versus stated confidence, ${total} accusations`}
          >
            {/* Perfect-calibration reference diagonal (y = x). */}
            <line
              x1="0"
              y1="100"
              x2="100"
              y2="0"
              stroke={tokens.ink[300]}
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
                    fill={tokens.ink[700]}
                    opacity={0.5}
                  >
                    <title>{tooltip}</title>
                  </rect>
                  <circle cx={cx} cy={100 - barHeight} r="1.6" fill={tokens.ink[900]}>
                    <title>{tooltip}</title>
                  </circle>
                </g>
              );
            })}
          </svg>
        </div>
      </div>
      <div className="mt-1 pl-7 text-[10px] text-ink-400">
        confidence (bin midpoint) 0 → 1
      </div>
      <p className="mt-1 text-xs text-ink-500">
        {total === 0
          ? "No accusations recorded — empty calibration curve."
          : `${total.toLocaleString("en-US")} accusations across ${populatedBins} populated bins.`}
      </p>
    </div>
  );
}
