// The Tournament view: the merged `TournamentEvalReport` rendered as balance
// outcome, vote correctness, the conversion + gate surface, the
// proof-vs-inference deduction instrument, calibration, alibi fabrication, an
// interestingness histogram (from `/eval/rubric`, whose buckets deep-link into
// the Highlights reel through the SHARED `view` · `set` · `scoreBucket` filter
// keys) and the cost roll-up.
//
// BINDING HONESTY RULE ("no false precision"): an under-powered or
// narrowly-scoped number is never shown bare — its caveat renders ATTACHED to
// the tile it qualifies, not in a distant footnote. The "Proof vs inference"
// panel is the same rule at panel scale: the meeting-flag and ejectee-proof
// cuts of the same bytes have DIFFERENT denominators, so they render as two
// labelled partitions and are never mixed into one row.
//
// COPY LIVES IN `lib/copy.ts`. Every prose string this surface renders —
// section titles and descriptions, tile labels, hints, caveat chips and their
// tooltips — is a value there, and `lib/copy.test.ts` walks the whole tree
// plus this file's stripped source, so a literal typed back into the JSX
// fails the gate. Counted hints keep their WORDS there too, as `{n}`
// templates filled by `fmt`. Only the report's own numbers are formatted
// here. This is the tab the review found citing design-doc sections and task
// numbers at a visitor.
//
// Split (mirrors the sibling chrome slices): `TournamentDashboard` is the
// connected component (store + rubric fetch); `TournamentDashboardView` is the
// pure presentational surface the Storybook story drives.

import { useCallback, useEffect, useState } from "react";
import { balanceCounts } from "../lib/completion";
import type { ReactNode } from "react";

import { ApiError, getRubric } from "../api/client";
import { DASHBOARD_COPY, fmt } from "../lib/copy";
import { useReplayStore } from "../store/replayStore";
import { useTournamentStore } from "../store/tournamentStore";
import type {
  CostDashboard,
  GameReport,
  RubricView,
  TournamentEvalReport,
  WilsonRateCell,
} from "../types/api";
import { CalibrationCurve } from "./CalibrationCurve";
import { MetricCaveat } from "./MetricCaveat";
import { SetSelector } from "./ReplayPicker";
import { StatTile } from "./StatTile";

/**
 * True in a build produced by `scripts/build_demo_bundle.py`.
 *
 * The same read `api/client.ts` makes for its `STATIC_DATA_MODE` seam, kept
 * local rather than imported so a rendering decision on this surface does not
 * become part of the client's public shape. `import.meta.env.VITE_*` is
 * substituted at BUILD time, so this is a literal `true` or `false` and only one
 * arm of the branch below is emitted. (The copy strings themselves live in one
 * frozen object and ship in both builds; it is the markup that is dropped.)
 *
 * The bundle has no eval directory and no tournament runner to point a reader
 * at, so the guidance that fits a local checkout is wrong there; the demo says
 * what it ships and where the rest lives instead.
 */
const STATIC_BUNDLE_BUILD: boolean =
  import.meta.env.VITE_AILIBI_STATIC_DATA === "1";

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
  low: DASHBOARD_COPY.bucketLabelLow,
  med: DASHBOARD_COPY.bucketLabelMed,
  high: DASHBOARD_COPY.bucketLabelHigh,
};
const BUCKET_RANGE: Record<ScoreBucket, string> = {
  low: DASHBOARD_COPY.bucketRangeLow,
  med: DASHBOARD_COPY.bucketRangeMed,
  high: DASHBOARD_COPY.bucketRangeHigh,
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
// `absent` is the 404 an UNSCORED set answers with (no rubric → first-class
// empty histogram). Since Task 19.9 the default set is the curated 9p2i, which
// ships a rubric, so the 404 is now reached only by an explicit `?set=` onto an
// unscored set — 4p1i, the fast fixture, and both ml_corpus sets.
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
  const { crewWins, impostorWins, tickBudget, aborted, unfinished, unverified, decisive } =
    balanceCounts(games);
  const crewShare = decisive > 0 ? crewWins / decisive : null;

  return (
    <MetricSection
      title={DASHBOARD_COPY.balanceTitle}
      description={DASHBOARD_COPY.balanceDescription}
    >
      <TileGrid>
        <StatTile
          label={DASHBOARD_COPY.balanceGames}
          value={formatInt(total)}
          hint={fmt(
            seedsAttempted !== total
              ? DASHBOARD_COPY.balanceSeedsAttempted
              : DASHBOARD_COPY.balanceSeeds,
            { n: formatInt(seedsAttempted) },
          )}
        />
        <StatTile
          label={DASHBOARD_COPY.balanceCrewWins}
          value={formatInt(crewWins)}
        />
        <StatTile
          label={DASHBOARD_COPY.balanceImpostorWins}
          value={formatInt(impostorWins)}
        />
        <StatTile
          label={DASHBOARD_COPY.balanceTickBudget}
          value={formatInt(tickBudget)}
          hint={DASHBOARD_COPY.balanceTickBudgetHint}
        />
        <StatTile
          label={DASHBOARD_COPY.balanceAborted}
          value={formatInt(aborted)}
        />
        <StatTile
          label={DASHBOARD_COPY.balanceUnfinished}
          value={formatInt(unfinished)}
        />
        <StatTile
          label={DASHBOARD_COPY.balanceUnverified}
          value={formatInt(unverified)}
          hint={DASHBOARD_COPY.balanceUnverifiedHint}
        />
        <StatTile
          label={DASHBOARD_COPY.balanceCrewWinRate}
          value={formatPct(crewShare)}
          hint={fmt(DASHBOARD_COPY.balanceCrewWinRateHint, { n: formatInt(decisive) })}
        />
      </TileGrid>
    </MetricSection>
  );
}

// ---------------------------------------------------------------------------
// Vote correctness — a bug check on the recorded evidence, not a quality score
// ---------------------------------------------------------------------------

function VoteCorrectness({
  report,
}: {
  report: TournamentEvalReport["vote_correctness"];
}) {
  // Two caveats, each ATTACHED to the number it actually qualifies (never a bare
  // metric). StatTile takes ONE caveat node per tile, so they are placed where
  // they belong rather than stacked: the small-n flag rides on "Impostor
  // ejections" — that tile IS the denominator, so the n lives there — while the
  // rate tile carries the scope note that says what the rate is for.
  //
  // The rate is NOT structurally 1.0, whatever this file used to tell a reader:
  // the committed 9p2i report records 72 evidence-backed of 78 impostor
  // ejections (0.923). So the copy says what a value below 1 means and stops
  // short of naming a cause.
  const smallN = report.vote_correctness_small_n ? (
    <MetricCaveat tone="warn" title={DASHBOARD_COPY.voteCorrectnessSmallNTitle}>
      {DASHBOARD_COPY.voteCorrectnessSmallN}
    </MetricCaveat>
  ) : undefined;

  return (
    <MetricSection
      title={DASHBOARD_COPY.voteCorrectnessTitle}
      description={DASHBOARD_COPY.voteCorrectnessDescription}
    >
      <TileGrid>
        <StatTile
          label={DASHBOARD_COPY.voteCorrectnessRate}
          value={formatPct(report.vote_correctness_rate)}
          hint={fmt(DASHBOARD_COPY.voteCorrectnessRateHint, {
            backed: formatInt(report.evidence_backed_impostor_ejections),
            total: formatInt(report.impostor_ejections),
          })}
          caveat={
            <MetricCaveat
              tone="note"
              title={DASHBOARD_COPY.voteCorrectnessRateCaveatTitle}
            >
              {DASHBOARD_COPY.voteCorrectnessRateCaveat}
            </MetricCaveat>
          }
        />
        <StatTile
          label={DASHBOARD_COPY.voteCorrectnessTotalEjections}
          value={formatInt(report.total_ejections)}
        />
        <StatTile
          label={DASHBOARD_COPY.voteCorrectnessImpostorEjections}
          value={formatInt(report.impostor_ejections)}
          caveat={smallN}
        />
        <StatTile
          label={DASHBOARD_COPY.voteCorrectnessCrewmateEjections}
          value={formatInt(report.crewmate_ejections)}
        />
        <StatTile
          label={DASHBOARD_COPY.voteCorrectnessIgnored}
          value={formatInt(report.contradictions_flagged_but_ignored)}
          caveat={
            <MetricCaveat
              tone="note"
              title={DASHBOARD_COPY.voteCorrectnessIgnoredCaveatTitle}
            >
              {DASHBOARD_COPY.voteCorrectnessIgnoredCaveat}
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

function ConversionSection({
  report,
}: {
  report: TournamentEvalReport["conversion"];
}) {
  // `missed_skip_ballots` is not a down-is-good metric — it partitions into
  // impostor voters (adversarial play, working as intended), invalid targets
  // (normalized hallucinations) and threshold inversions (a crew voter
  // declining a met bar, which the non-directive vote gate allows). The caveat
  // carries that "read the partition, not the total" note in place.
  return (
    <MetricSection
      title={DASHBOARD_COPY.conversionTitle}
      description={DASHBOARD_COPY.conversionDescription}
    >
      <TileGrid>
        <StatTile
          label={DASHBOARD_COPY.conversionAccuracy}
          value={formatPct(report.ejection_accuracy)}
          hint={fmt(DASHBOARD_COPY.conversionAccuracyHint, {
            hit: formatInt(report.impostor_ejections),
            total: formatInt(report.total_ejections),
          })}
        />
        <StatTile
          label={DASHBOARD_COPY.conversionAccused}
          value={formatPct(report.impostor_accused_conversion_rate)}
          hint={fmt(DASHBOARD_COPY.conversionAccusedHint, {
            converted: formatInt(report.impostor_accused_conversions),
            meetings: formatInt(report.impostor_accused_meetings),
          })}
        />
        <StatTile
          label={DASHBOARD_COPY.conversionCorrectSkips}
          value={`${formatInt(report.correct_skip_ballots)} / ${formatInt(report.skip_ballots)}`}
          hint={DASHBOARD_COPY.conversionCorrectSkipsHint}
        />
        <StatTile
          label={DASHBOARD_COPY.conversionMissedSkips}
          value={formatInt(report.missed_skip_ballots)}
          hint={fmt(DASHBOARD_COPY.conversionMissedSkipsHint, {
            impostorVoters: formatInt(report.missed_skip_impostor_voters),
            invalidTargets: formatInt(report.missed_skip_invalid_target),
            crewDeclined: formatInt(report.threshold_inversions),
          })}
          caveat={
            <MetricCaveat
              tone="note"
              title={DASHBOARD_COPY.conversionMissedSkipsCaveatTitle}
            >
              {DASHBOARD_COPY.conversionMissedSkipsCaveat}
            </MetricCaveat>
          }
        />
        <StatTile
          label={DASHBOARD_COPY.conversionInversions}
          value={formatInt(report.threshold_inversions)}
          hint={DASHBOARD_COPY.conversionInversionsHint}
          caveat={
            report.threshold_inversions > 0 ? (
              <MetricCaveat
                tone="note"
                title={DASHBOARD_COPY.conversionInversionsCaveatTitle}
              >
                {DASHBOARD_COPY.conversionInversionsCaveat}
              </MetricCaveat>
            ) : (
              <MetricCaveat tone="note">
                {DASHBOARD_COPY.conversionInversionsNone}
              </MetricCaveat>
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

// The two cells' tooltips are OURS, not the report's. `supplied_channel
// _conversion.note` / `.legacy_note` are maintainer notes — they cite task ids,
// audit paths and internal channel names — and rendering them verbatim put that
// dialect on the product surface through the back door. The eval package still
// carries them for anyone reading the JSON.
function GateMetricsSection({
  report,
}: {
  report: TournamentEvalReport["gate_metrics"];
}) {
  const gcc = report.genuine_class_conversion;
  const scc = report.supplied_channel_conversion;
  return (
    <MetricSection
      title={DASHBOARD_COPY.gateTitle}
      description={DASHBOARD_COPY.gateDescription}
    >
      <TileGrid>
        <StatTile
          lead
          label={DASHBOARD_COPY.gateSupplied}
          value={formatPct(scc.conversion_rate)}
          hint={fmt(DASHBOARD_COPY.gateSuppliedHint, {
            converted: formatInt(scc.converted),
            supplied: formatInt(scc.supplied),
            ventConverted: formatInt(scc.witnessed_vent_converted),
            ventSupplied: formatInt(scc.witnessed_vent_supplied),
            sightingConverted: formatInt(scc.sighting_contradiction_converted),
            sightingSupplied: formatInt(scc.sighting_contradiction_supplied),
            whereaboutsConverted: formatInt(scc.whereabouts_lie_converted),
            whereaboutsSupplied: formatInt(scc.whereabouts_lie_supplied),
          })}
          caveat={
            <MetricCaveat
              tone="note"
              title={DASHBOARD_COPY.gateSuppliedCaveatTitle}
            >
              {DASHBOARD_COPY.gateSuppliedCaveat}
            </MetricCaveat>
          }
        />
        <StatTile
          label={DASHBOARD_COPY.gateGenuine}
          value={formatPct(gcc.conversion_rate)}
          hint={fmt(DASHBOARD_COPY.gateGenuineHint, {
            converted: formatInt(gcc.converted),
            supplied: formatInt(gcc.supplied),
          })}
          caveat={
            <MetricCaveat
              tone="note"
              title={DASHBOARD_COPY.gateGenuineCaveatTitle}
            >
              {DASHBOARD_COPY.gateGenuineCaveat}
            </MetricCaveat>
          }
        />
        <StatTile
          label={DASHBOARD_COPY.gateLostOpenings}
          value={formatInt(report.lost_opening_accusations)}
          hint={DASHBOARD_COPY.gateLostOpeningsHint}
        />
        <StatTile
          label={DASHBOARD_COPY.gateCapDefaults}
          value={formatInt(report.cap_defaulted_turns)}
          hint={DASHBOARD_COPY.gateCapDefaultsHint}
        />
        <StatTile
          label={DASHBOARD_COPY.gateSurvivals}
          value={`${formatInt(report.accused_impostor_survivals)} / ${formatInt(report.accused_impostor_events)}`}
          hint={fmt(DASHBOARD_COPY.gateSurvivalsHint, {
            met: formatInt(report.survivals_rendered_met),
            sheltered: formatInt(report.survivals_sheltered_sub_gate),
            unevidenced: formatInt(report.survivals_unevidenced),
          })}
          caveat={
            <MetricCaveat
              tone="note"
              title={DASHBOARD_COPY.gateSurvivalsCaveatTitle}
            >
              {DASHBOARD_COPY.gateSurvivalsCaveat}
            </MetricCaveat>
          }
        />
      </TileGrid>
    </MetricSection>
  );
}

// ---------------------------------------------------------------------------
// Proof vs inference — the deduction instrument
// ---------------------------------------------------------------------------

// `n/a` when the denominator is 0 (the None-not-0.0 convention the eval package
// uses); otherwise the rate with its Wilson 95% interval, because the honest
// reading of a rare cell IS the interval.
function formatCellRate(cell: WilsonRateCell): string {
  return formatPct(cell.rate);
}

function formatCellInterval(cell: WilsonRateCell): string {
  if (cell.wilson_low === null || cell.wilson_high === null) {
    return DASHBOARD_COPY.deductionIntervalMissing;
  }
  return fmt(DASHBOARD_COPY.deductionInterval, {
    low: formatPct(cell.wilson_low),
    high: formatPct(cell.wilson_high),
  });
}

// The rare-cell badge. `advisory` is the eval module's own flag (numerator ≤ 7),
// so the UI never re-derives the threshold — it renders the recorded verdict.
function advisoryCaveat(cell: WilsonRateCell) {
  return cell.advisory ? (
    <MetricCaveat
      tone="warn"
      title={fmt(DASHBOARD_COPY.deductionRareCaveatTitle, {
        numerator: formatInt(cell.numerator),
        interval: formatCellInterval(cell),
      })}
    >
      {DASHBOARD_COPY.deductionRareCaveat}
    </MetricCaveat>
  ) : undefined;
}

// The non-causation note. It rides on the non-direct tile ALWAYS, never as an
// either/or with the rare-cell badge: StatTile's caveat slot is a wrap-friendly
// row, so both render together. The two say different things — one is about
// sample size, the other about what "proof-present" means — and dropping the
// semantic one whenever a set happens to be small is exactly how the committed
// samples-4p1i report (non-direct 1/3) ended up rendered with the causal
// reading the backend definition rejects.
function nonCausationCaveat(cell: WilsonRateCell) {
  return (
    <MetricCaveat
      tone="note"
      title={fmt(DASHBOARD_COPY.deductionNonCausationCaveatTitle, {
        interval: formatCellInterval(cell),
      })}
    >
      {DASHBOARD_COPY.deductionNonCausationCaveat}
    </MetricCaveat>
  );
}

// A labelled sub-group inside the deduction panel. Each partition gets its own
// heading and its own denominators; the two are NEVER mixed in one row, which is
// the whole point of the panel (the C5 define-before-counting lesson: the audits'
// counts differed only by definition, and the fourth planning round caught the
// two denominators being blended into one sentence).
function PartitionGroup({
  heading,
  unit,
  children,
}: {
  heading: string;
  unit: string;
  children: ReactNode;
}) {
  return (
    <div className="mt-1 first:mt-0">
      <div className="mb-2 flex flex-wrap items-baseline gap-2">
        <h4 className="font-mono text-[11px] uppercase tracking-wide text-ink-900">
          {heading}
        </h4>
        <span className="text-[11px] text-ink-500">{unit}</span>
      </div>
      <TileGrid>{children}</TileGrid>
    </div>
  );
}

function DeductionSection({
  report,
}: {
  report: TournamentEvalReport["deduction"];
}) {
  const meetingFlag = report.meeting_flag_cross_tab;
  const ejecteeProof = report.ejectee_proof_cross_tab;
  const weak = report.weak_flag_conviction;
  const coverage = report.public_response_coverage;
  const supply = report.witnessed_supply;
  const flaggedEjections =
    meetingFlag.flagged_ejections_impostor +
    meetingFlag.flagged_ejections_innocent;
  const unflaggedEjections =
    meetingFlag.unflagged_ejections_impostor +
    meetingFlag.unflagged_ejections_innocent;

  return (
    <MetricSection
      title={DASHBOARD_COPY.deductionTitle}
      description={DASHBOARD_COPY.deductionDescription}
    >
      <div className="flex flex-col gap-4">
        <PartitionGroup
          heading={DASHBOARD_COPY.deductionPartitionA}
          unit={fmt(DASHBOARD_COPY.deductionPartitionAUnit, {
            meetings: formatInt(meetingFlag.meetings_total),
          })}
        >
          <StatTile
            label={DASHBOARD_COPY.deductionFlagged}
            value={formatCellRate(meetingFlag.flagged_meeting_accuracy)}
            hint={fmt(DASHBOARD_COPY.deductionFlaggedHint, {
              impostor: formatInt(meetingFlag.flagged_ejections_impostor),
              total: formatInt(flaggedEjections),
              meetings: formatInt(meetingFlag.flagged_meetings),
            })}
            caveat={advisoryCaveat(meetingFlag.flagged_meeting_accuracy)}
          />
          <StatTile
            label={DASHBOARD_COPY.deductionUnflagged}
            value={formatCellRate(meetingFlag.unflagged_meeting_accuracy)}
            hint={fmt(DASHBOARD_COPY.deductionUnflaggedHint, {
              impostor: formatInt(meetingFlag.unflagged_ejections_impostor),
              total: formatInt(unflaggedEjections),
              meetings: formatInt(meetingFlag.unflagged_meetings),
            })}
            lead
            caveat={advisoryCaveat(meetingFlag.unflagged_meeting_accuracy)}
          />
          <StatTile
            label={DASHBOARD_COPY.deductionInnocents}
            value={`${formatInt(meetingFlag.flagged_ejections_innocent)} / ${formatInt(meetingFlag.unflagged_ejections_innocent)}`}
            hint={DASHBOARD_COPY.deductionInnocentsHint}
          />
        </PartitionGroup>

        <PartitionGroup
          heading={DASHBOARD_COPY.deductionPartitionB}
          unit={fmt(DASHBOARD_COPY.deductionPartitionBUnit, {
            ejections: formatInt(ejecteeProof.ejections_total),
          })}
        >
          <StatTile
            label={DASHBOARD_COPY.deductionDirect}
            value={formatCellRate(ejecteeProof.direct_proof_accuracy)}
            hint={fmt(DASHBOARD_COPY.deductionDirectHint, {
              impostor: formatInt(ejecteeProof.proof_present_impostor),
              total: formatInt(ejecteeProof.proof_present_ejections),
            })}
            caveat={advisoryCaveat(ejecteeProof.direct_proof_accuracy)}
          />
          <StatTile
            label={DASHBOARD_COPY.deductionNonDirect}
            value={formatCellRate(ejecteeProof.non_direct_accuracy)}
            hint={fmt(DASHBOARD_COPY.deductionNonDirectHint, {
              impostor: formatInt(ejecteeProof.non_direct_impostor),
              total: formatInt(ejecteeProof.non_direct_ejections),
            })}
            lead
            caveat={
              <>
                {advisoryCaveat(ejecteeProof.non_direct_accuracy)}
                {nonCausationCaveat(ejecteeProof.non_direct_accuracy)}
              </>
            }
          />
          <StatTile
            label={DASHBOARD_COPY.deductionProofShare}
            value={formatPct(
              ejecteeProof.ejections_total > 0
                ? ejecteeProof.proof_present_ejections /
                    ejecteeProof.ejections_total
                : null,
            )}
            hint={fmt(DASHBOARD_COPY.deductionProofShareHint, {
              present: formatInt(ejecteeProof.proof_present_ejections),
              total: formatInt(ejecteeProof.ejections_total),
            })}
          />
        </PartitionGroup>

        <PartitionGroup
          heading={DASHBOARD_COPY.deductionSupporting}
          unit={DASHBOARD_COPY.deductionSupportingUnit}
        >
          <StatTile
            label={DASHBOARD_COPY.deductionWeakFlag}
            value={`${formatInt(weak.weak_flag_only_convictions)} / ${formatInt(weak.flag_named_ejections)}`}
            hint={fmt(DASHBOARD_COPY.deductionWeakFlagHint, {
              innocent: formatInt(weak.weak_flag_only_innocent),
            })}
            caveat={advisoryCaveat(weak.weak_flag_only_rate)}
          />
          <StatTile
            label={DASHBOARD_COPY.deductionConsistency}
            value={formatPct(report.turn_ballot_consistency.consistency_rate)}
            hint={fmt(DASHBOARD_COPY.deductionConsistencyHint, {
              consistent: formatInt(
                report.turn_ballot_consistency.consistent_ballots,
              ),
              accusing: formatInt(
                report.turn_ballot_consistency.accusing_ballots,
              ),
            })}
            caveat={
              <MetricCaveat
                tone="note"
                title={DASHBOARD_COPY.deductionConsistencyCaveatTitle}
              >
                {DASHBOARD_COPY.deductionConsistencyCaveat}
              </MetricCaveat>
            }
          />
          <StatTile
            label={DASHBOARD_COPY.deductionCoverage}
            value={`${formatPct(coverage.crew_pooled_coverage)} / ${formatPct(coverage.impostor_pooled_coverage)}`}
            hint={fmt(DASHBOARD_COPY.deductionCoverageHint, {
              crewWith: formatInt(coverage.crew_turns_with_whereabouts),
              crewTotal: formatInt(coverage.crew_turns),
              impostorWith: formatInt(coverage.impostor_turns_with_whereabouts),
              impostorTotal: formatInt(coverage.impostor_turns),
            })}
            caveat={
              <MetricCaveat
                tone="note"
                title={fmt(DASHBOARD_COPY.deductionCoverageCaveatTitle, {
                  macro: formatPct(coverage.impostor_macro_average_coverage),
                  pooled: formatPct(coverage.impostor_pooled_coverage),
                })}
              >
                {DASHBOARD_COPY.deductionCoverageCaveat}
              </MetricCaveat>
            }
          />
          <StatTile
            label={DASHBOARD_COPY.deductionRedirected}
            value={formatPct(report.redirected_ballots.redirected_ballot_share)}
            hint={fmt(DASHBOARD_COPY.deductionRedirectedHint, {
              redirected: formatInt(
                report.redirected_ballots.redirected_ballots,
              ),
              total: formatInt(report.redirected_ballots.ballots_total),
              ejected: formatInt(
                report.redirected_ballots.redirected_eject_ballots,
              ),
            })}
          />
          <StatTile
            label={DASHBOARD_COPY.deductionSupply}
            value={
              supply === null
                ? "n/a"
                : `${formatInt(supply.crew_witnessed_kills)} / ${formatInt(supply.kills_total)}`
            }
            hint={
              supply === null
                ? DASHBOARD_COPY.deductionSupplyMissing
                : fmt(DASHBOARD_COPY.deductionSupplyHint, {
                    coPresent: formatInt(supply.co_present_crew_kills),
                  })
            }
            caveat={
              supply === null ? (
                <MetricCaveat
                  tone="note"
                  title={DASHBOARD_COPY.deductionSupplyMissingCaveatTitle}
                >
                  {DASHBOARD_COPY.deductionSupplyMissingCaveat}
                </MetricCaveat>
              ) : (
                advisoryCaveat(supply.crew_witnessed_kill_rate)
              )
            }
          />
        </PartitionGroup>
      </div>
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
      title={DASHBOARD_COPY.calibrationTitle}
      description={DASHBOARD_COPY.calibrationDescription}
    >
      <div className="grid gap-4 lg:grid-cols-2">
        <CalibrationCurve
          title={DASHBOARD_COPY.calibrationClaims}
          bins={report.accusation_claim_bins}
          total={report.accusation_claim_total}
          ece={report.accusation_claim_ece}
          populatedBins={report.accusation_claim_populated_bins}
          lowPower={report.accusation_claim_low_power}
          nBins={report.n_bins}
        />
        <CalibrationCurve
          title={DASHBOARD_COPY.calibrationBallots}
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
  // survival_rate is null EXACTLY when no impostor alibis were filed (the
  // eval-side None-iff-undefined convention), so formatPct's "n/a" already
  // covers the empty case — no frontend denominator special-case needed.
  return (
    <MetricSection
      title={DASHBOARD_COPY.alibiTitle}
      description={DASHBOARD_COPY.alibiDescription}
    >
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        <StatTile
          label={DASHBOARD_COPY.alibiSurvivalRate}
          value={formatPct(report.survival_rate)}
          hint={fmt(DASHBOARD_COPY.alibiSurvivalRateHint, {
            survived: formatInt(report.survived),
            total: formatInt(report.total_impostor_alibis),
          })}
        />
        <StatTile
          label={DASHBOARD_COPY.alibiTotal}
          value={formatInt(report.total_impostor_alibis)}
        />
        <StatTile
          label={DASHBOARD_COPY.alibiSurvived}
          value={formatInt(report.survived)}
        />
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
        title={DASHBOARD_COPY.interestingnessStaleCaveatTitle}
      >
        {DASHBOARD_COPY.interestingnessStaleCaveat}
      </MetricCaveat>
    ) : undefined;

  return (
    <MetricSection
      title={DASHBOARD_COPY.interestingnessTitle}
      description={DASHBOARD_COPY.interestingnessDescription}
      action={staleAction}
    >
      {rubric.status === "loading" ? (
        <p className="text-sm text-ink-500">
          {DASHBOARD_COPY.interestingnessLoading}
        </p>
      ) : rubric.status === "absent" ? (
        // Post-flip copy (Task 19.13, sweeping what Task 19.9's default flip
        // falsified). This panel used to say the DEFAULT-served set was 4p1i and
        // that its games were "mostly zero-meeting" — both wrong now: the default
        // is the curated 9p2i, which ships a rubric, and 4p1i's games are mostly
        // ONE-meeting (39 of 50 hold exactly one, 11 hold none). So this state is
        // reached by an explicit switch onto an unscored set, and it says which.
        <div className="rounded-lg border border-ink-200 bg-paper-1 px-4 py-6 text-center shadow-data">
          <p className="font-semibold text-ink-900">
            {DASHBOARD_COPY.interestingnessAbsentTitle}
          </p>
          <p className="mt-1 text-sm text-ink-500">
            {DASHBOARD_COPY.interestingnessAbsentLead}{" "}
            <code className="font-mono text-xs">
              experiments/lab/rubric_score.py
            </code>{" "}
            {DASHBOARD_COPY.interestingnessAbsentTail}
          </p>
        </div>
      ) : rubric.status === "error" ? (
        <p className="text-sm text-ink-500">
          {DASHBOARD_COPY.interestingnessError} {rubric.message}
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
        {DASHBOARD_COPY.interestingnessEmpty}
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
              aria-label={fmt(DASHBOARD_COPY.interestingnessBucketLink, {
                count: formatInt(count),
                bucket: BUCKET_LABEL[bucket],
                plural: count === 1 ? "" : "s",
                range: BUCKET_RANGE[bucket],
              })}
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
              <span className="font-mono text-3xs text-ink-500">
                {DASHBOARD_COPY.interestingnessScorePrefix}{" "}
                {BUCKET_RANGE[bucket]}
              </span>
            </a>
          );
        })}
      </div>
      <p className="mt-3 text-xs text-ink-500">
        {fmt(DASHBOARD_COPY.interestingnessFooter, {
          games: formatInt(total),
          set: view.seedset,
        })}
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
      title={DASHBOARD_COPY.costTitle}
      description={DASHBOARD_COPY.costDescription}
    >
      <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatTile
          label={DASHBOARD_COPY.costTotal}
          value={formatUsd(dashboard.total_cost_usd)}
        />
        <StatTile
          label={DASHBOARD_COPY.costMean}
          value={formatUsd(dashboard.mean_cost_per_game)}
          hint={DASHBOARD_COPY.costMeanHint}
        />
        <StatTile
          label={DASHBOARD_COPY.costGames}
          value={formatInt(dashboard.game_count)}
        />
        <StatTile
          label={DASHBOARD_COPY.costTokens}
          value={`${formatInt(dashboard.total_input_tokens)} / ${formatInt(dashboard.total_output_tokens)}`}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div>
          <h4 className="mb-1 text-ink-900">{DASHBOARD_COPY.costPerModel}</h4>
          {byModel.length === 0 ? (
            <p className="text-sm text-ink-500">
              {DASHBOARD_COPY.costPerModelEmpty}
            </p>
          ) : (
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase tracking-wide text-ink-500">
                <tr>
                  <th className="py-1 pr-2 font-medium">
                    {DASHBOARD_COPY.costColModel}
                  </th>
                  <th className="py-1 text-right font-medium">
                    {DASHBOARD_COPY.costColCost}
                  </th>
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
          <h4 className="mb-1 text-ink-900">{DASHBOARD_COPY.costPerPrompt}</h4>
          {dashboard.per_prompt_version.length === 0 ? (
            <p className="text-sm text-ink-500">
              {DASHBOARD_COPY.costPerPromptEmpty}
            </p>
          ) : (
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase tracking-wide text-ink-500">
                <tr>
                  <th className="py-1 pr-2 font-medium">
                    {DASHBOARD_COPY.costColTemplate}
                  </th>
                  <th className="py-1 pr-2 font-medium">
                    {DASHBOARD_COPY.costColVersion}
                  </th>
                  <th className="py-1 text-right font-medium">
                    {DASHBOARD_COPY.costColGames}
                  </th>
                  <th className="py-1 text-right font-medium">
                    {DASHBOARD_COPY.costColCost}
                  </th>
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
                    <td className="py-1 text-right">
                      {formatInt(row.game_count)}
                    </td>
                    <td className="py-1 text-right">
                      {formatUsd(row.total_cost_usd)}
                    </td>
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
    <main aria-label={DASHBOARD_COPY.ariaLabel} className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm text-ink-500">{DASHBOARD_COPY.intro}</p>
        <button
          type="button"
          onClick={onRefresh}
          disabled={isLoading}
          className="rounded-md border-2 border-ink-900 bg-paper-0 px-3 py-1.5 text-sm font-semibold text-ink-900 shadow-chrome-1 transition-colors hover:bg-paper-2 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? DASHBOARD_COPY.refreshBusy : DASHBOARD_COPY.refresh}
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
          <DeductionSection report={report.deduction} />
          <GateMetricsSection report={report.gate_metrics} />
          <AccusationCalibration report={report.accusation_calibration} />
          <AlibiFabrication report={report.alibi_fabrication} />
          <InterestingnessHistogram rubric={rubric} />
          <CostDashboardView dashboard={report.cost_dashboard} />
        </>
      ) : isLoading || error === null ? (
        // Loading: a fetch is in flight, or we are still initializing (no report,
        // no error yet) — never flash the no-report panel before the first fetch.
        <p role="status" aria-live="polite" className="text-ink-500">
          {DASHBOARD_COPY.loadingReport}
        </p>
      ) : (
        // No-report state: a definitive failure with no report. Every word here
        // is app-authored. The transport error is deliberately NOT rendered:
        // `ApiError` folds the RESPONSE BODY into its message, and a file server
        // answers a missing file with its own HTML error page — so printing the
        // message put a raw `<!DOCTYPE HTML PUBLIC …>` document inside the card.
        <div className="rounded-lg border-2 border-ink-900 bg-paper-0 px-4 py-6 shadow-chrome-1">
          <p className="font-semibold text-ink-900">
            {DASHBOARD_COPY.noReportTitle}
          </p>
          {STATIC_BUNDLE_BUILD ? (
            <p className="mt-1 text-sm text-ink-500">
              {DASHBOARD_COPY.noReportBundle}
            </p>
          ) : (
            <p className="mt-1 text-sm text-ink-500">
              {DASHBOARD_COPY.noReportLead}{" "}
              <code className="font-mono text-xs">
                tournament-eval-report.json
              </code>{" "}
              {DASHBOARD_COPY.noReportMiddle}{" "}
              <code className="font-mono text-xs">
                scripts/run_tournament.py
              </code>{" "}
              {DASHBOARD_COPY.noReportTail}
            </p>
          )}
        </div>
      )}
    </main>
  );
}

// ---------------------------------------------------------------------------
// Connected dashboard — store (report) + the `/eval/rubric` fetch (histogram)
// ---------------------------------------------------------------------------

export function TournamentDashboard() {
  const report = useTournamentStore((s) => s.report);
  const isLoading = useTournamentStore((s) => s.isLoading);
  const error = useTournamentStore((s) => s.error);
  const loadReport = useTournamentStore((s) => s.loadReport);

  // The active set is shared via useReplayStore (Task 12.12): the dashboard's
  // report + rubric fetches follow it, and its own selector drives it (live, no
  // reload). `setSeedSet` is URL-synced by usePlayback (the existing `set` key).
  const seedSet = useReplayStore((s) => s.seedSet);
  const availableSets = useReplayStore((s) => s.availableSets);
  const setSeedSet = useReplayStore((s) => s.setSeedSet);
  const loadSets = useReplayStore((s) => s.loadSets);

  // The rubric is fetched here (not via the tournament store, which is frozen to
  // the report) — a load-time projection served per set, 404 when the SELECTED
  // set ships none (4p1i and the ml_corpus sets; not the 9p2i default, which
  // ships one since Task 19.9's flip). `reloadNonce` re-triggers the fetch on
  // Refresh; `seedSet` re-triggers it on a live set switch. It goes through
  // `api/client`'s `getRubric`, so this panel reads the live API in a normal
  // build and the pre-baked JSON in the static demo bundle — and gets the
  // view-model version gate, which a hand-rolled fetch of this stamped payload
  // silently skipped.
  const [rubric, setRubric] = useState<RubricState>({ status: "loading" });
  const [reloadNonce, setReloadNonce] = useState(0);

  // Populate the set list so the selector works even when the dashboard is the
  // first view visited; adopts the server default into `seedSet` when unset.
  useEffect(() => {
    void loadSets();
  }, [loadSets]);

  useEffect(() => {
    let cancelled = false;
    setRubric({ status: "loading" });
    getRubric(seedSet ?? undefined)
      .then((view: RubricView) => {
        if (!cancelled) {
          setRubric({ status: "ready", view });
        }
      })
      .catch((cause: unknown) => {
        if (cancelled) {
          return;
        }
        // A set that ships no rubric is a first-class empty state, not an error
        // — the same 404 read `ReplayPicker` uses for the Highlights reel.
        if (cause instanceof ApiError && cause.status === 404) {
          setRubric({ status: "absent" });
          return;
        }
        // An HTTP failure is reported by STATUS, never by `ApiError.message`:
        // that folds the response BODY in, and a file server answers with its
        // own HTML error page — the same reason the no-report panel below
        // refuses to print a transport error. Any other error (a view-model
        // contract mismatch) is app-authored and says something useful.
        const message =
          cause instanceof ApiError
            ? `rubric request failed (status ${cause.status})`
            : cause instanceof Error
              ? cause.message
              : String(cause);
        setRubric({ status: "error", message });
      });
    return () => {
      cancelled = true;
    };
  }, [reloadNonce, seedSet]);

  // Load the report for the active set on mount + on each live set switch, so the
  // view always reflects the selected set's latest report.
  useEffect(() => {
    void loadReport(seedSet ?? undefined);
  }, [loadReport, seedSet]);

  const handleRefresh = useCallback(() => {
    void loadReport(seedSet ?? undefined);
    setReloadNonce((n) => n + 1);
  }, [loadReport, seedSet]);

  return (
    <div className="flex flex-col gap-4">
      <SetSelector sets={availableSets} value={seedSet} onChange={setSeedSet} />
      <TournamentDashboardView
        report={report}
        isLoading={isLoading}
        error={error}
        onRefresh={handleRefresh}
        rubric={rubric}
      />
    </div>
  );
}
