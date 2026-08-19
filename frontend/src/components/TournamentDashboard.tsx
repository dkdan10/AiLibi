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
// COPY LIVES IN `lib/copy.ts`. Every prose string on this surface is a value
// there, checked against the dialect matcher by `lib/copy.test.ts` — this is
// the tab the review found citing design-doc sections and task numbers at a
// visitor. Tile values, report-derived hints and layout stay here.
//
// Split (mirrors the sibling chrome slices): `TournamentDashboard` is the
// connected component (store + rubric fetch); `TournamentDashboardView` is the
// pure presentational surface the Storybook story drives.

import { useCallback, useEffect, useState } from "react";
import type { ReactNode } from "react";

import { apiUrl } from "../api/client";
import { DASHBOARD_COPY, missedSkipsHint } from "../lib/copy";
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
      description={DASHBOARD_COPY.balanceDescription}
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
      small-n
    </MetricCaveat>
  ) : undefined;

  return (
    <MetricSection
      title="Vote correctness"
      description={DASHBOARD_COPY.voteCorrectnessDescription}
    >
      <TileGrid>
        <StatTile
          label="Evidence-backed share"
          value={formatPct(report.vote_correctness_rate)}
          hint={`${formatInt(report.evidence_backed_impostor_ejections)} / ${formatInt(report.impostor_ejections)} evidence-backed`}
          caveat={
            <MetricCaveat
              tone="note"
              title={DASHBOARD_COPY.voteCorrectnessRateCaveatTitle}
            >
              {DASHBOARD_COPY.voteCorrectnessRateCaveat}
            </MetricCaveat>
          }
        />
        <StatTile label="Total ejections" value={formatInt(report.total_ejections)} />
        <StatTile
          label="Impostor ejections"
          value={formatInt(report.impostor_ejections)}
          caveat={smallN}
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
  // `missed_skip_ballots` is not a down-is-good metric — it partitions into
  // impostor voters (adversarial play, working as intended), invalid targets
  // (normalized hallucinations) and threshold inversions (a crew voter
  // declining a met bar, which the non-directive vote gate allows). The caveat
  // carries that "read the partition, not the total" note in place.
  return (
    <MetricSection
      title="Conversion"
      description={DASHBOARD_COPY.conversionDescription}
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
          hint={missedSkipsHint(
            formatInt(report.missed_skip_impostor_voters),
            formatInt(report.missed_skip_invalid_target),
            formatInt(report.threshold_inversions),
          )}
          caveat={
            <MetricCaveat tone="note" title={DASHBOARD_COPY.missedSkipsCaveatTitle}>
              {DASHBOARD_COPY.missedSkipsCaveat}
            </MetricCaveat>
          }
        />
        <StatTile
          label="Threshold inversions"
          value={formatInt(report.threshold_inversions)}
          hint="crew declines at the advisory line"
          caveat={
            report.threshold_inversions > 0 ? (
              <MetricCaveat
                tone="note"
                title={DASHBOARD_COPY.thresholdInversionCaveatTitle}
              >
                discretionary — nonzero intended
              </MetricCaveat>
            ) : (
              <MetricCaveat tone="note">no declines recorded</MetricCaveat>
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
  const scc = report.supplied_channel_conversion;
  return (
    <MetricSection
      title="Gate metrics"
      description={DASHBOARD_COPY.gateMetricsDescription}
    >
      <TileGrid>
        <StatTile
          lead
          label="Supplied-channel conversion"
          value={formatPct(scc.conversion_rate)}
          hint={`${formatInt(scc.converted)} / ${formatInt(scc.supplied)} supplied impostors ejected · vent ${formatInt(scc.witnessed_vent_converted)}/${formatInt(scc.witnessed_vent_supplied)} · sighting ${formatInt(scc.sighting_contradiction_converted)}/${formatInt(scc.sighting_contradiction_supplied)} · whereabouts ${formatInt(scc.whereabouts_lie_converted)}/${formatInt(scc.whereabouts_lie_supplied)}`}
          caveat={
            <MetricCaveat
              tone="note"
              title={scc.note}
            >
              canary — the successor cell
            </MetricCaveat>
          }
        />
        <StatTile
          label="Genuine-class conversion (historical)"
          value={formatPct(gcc.conversion_rate)}
          hint={`${formatInt(gcc.converted)} / ${formatInt(gcc.supplied)} alibi-anchored flags — the Phase-10 cell`}
          caveat={
            <MetricCaveat
              tone="note"
              title={scc.legacy_note}
            >
              historical — starved, never a canary
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
// Proof vs inference — the deduction instrument
// ---------------------------------------------------------------------------

// `n/a` when the denominator is 0 (the None-not-0.0 convention the eval package
// uses); otherwise the rate with its Wilson 95% interval, because the honest
// reading of a rare cell IS the interval.
function formatCellRate(cell: WilsonRateCell): string {
  return formatPct(cell.rate);
}

function formatCellInterval(cell: WilsonRateCell): string {
  if (cell.wilson_low === null || cell.wilson_high === null) return "no data";
  return `95% CI ${formatPct(cell.wilson_low)}–${formatPct(cell.wilson_high)}`;
}

// The rare-cell badge. `advisory` is the eval module's own flag (numerator ≤ 7),
// so the UI never re-derives the threshold — it renders the recorded verdict.
function advisoryCaveat(cell: WilsonRateCell) {
  return cell.advisory ? (
    <MetricCaveat
      tone="warn"
      title={`Rare cell: the numerator is ${cell.numerator}. The point rate is statistically fragile at this scale — read the Wilson interval (${formatCellInterval(cell)}), not the percentage.`}
    >
      rare — read the interval
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
      title={`Co-occurrence inside one meeting, not causation: the cell says no role-proof flag NAMED the ejected player, not that the vote ignored evidence. ${formatCellInterval(cell)}.`}
    >
      proof-present ≠ proof-driven
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
    meetingFlag.flagged_ejections_impostor + meetingFlag.flagged_ejections_innocent;
  const unflaggedEjections =
    meetingFlag.unflagged_ejections_impostor +
    meetingFlag.unflagged_ejections_innocent;

  return (
    <MetricSection
      title="Proof vs inference"
      description={DASHBOARD_COPY.deductionDescription}
    >
      <div className="flex flex-col gap-4">
        <PartitionGroup
          heading="Partition A · meeting-flag"
          unit={`the unit is the MEETING (${formatInt(meetingFlag.meetings_total)} meetings)`}
        >
          <StatTile
            label="Flagged-meeting accuracy"
            value={formatCellRate(meetingFlag.flagged_meeting_accuracy)}
            hint={`${formatInt(meetingFlag.flagged_ejections_impostor)} / ${formatInt(flaggedEjections)} ejections in the ${formatInt(meetingFlag.flagged_meetings)} meetings that carried role proof`}
            caveat={advisoryCaveat(meetingFlag.flagged_meeting_accuracy)}
          />
          <StatTile
            label="Unflagged-meeting accuracy"
            value={formatCellRate(meetingFlag.unflagged_meeting_accuracy)}
            hint={`${formatInt(meetingFlag.unflagged_ejections_impostor)} / ${formatInt(unflaggedEjections)} ejections in the ${formatInt(meetingFlag.unflagged_meetings)} meetings with no role proof at all`}
            lead
            caveat={advisoryCaveat(meetingFlag.unflagged_meeting_accuracy)}
          />
          <StatTile
            label="Innocents ejected"
            value={`${formatInt(meetingFlag.flagged_ejections_innocent)} / ${formatInt(meetingFlag.unflagged_ejections_innocent)}`}
            hint="flagged / unflagged meetings"
          />
        </PartitionGroup>

        <PartitionGroup
          heading="Partition B · ejectee-specific proof"
          unit={`the unit is the EJECTION (${formatInt(ejecteeProof.ejections_total)} ejections)`}
        >
          <StatTile
            label="Direct-proof accuracy"
            value={formatCellRate(ejecteeProof.direct_proof_accuracy)}
            hint={`${formatInt(ejecteeProof.proof_present_impostor)} / ${formatInt(ejecteeProof.proof_present_ejections)} ejections where a vent sighting named the ejected player`}
            caveat={advisoryCaveat(ejecteeProof.direct_proof_accuracy)}
          />
          <StatTile
            label="Non-direct accuracy"
            value={formatCellRate(ejecteeProof.non_direct_accuracy)}
            hint={`${formatInt(ejecteeProof.non_direct_impostor)} / ${formatInt(ejecteeProof.non_direct_ejections)} ejections with NO proof naming the ejected player`}
            lead
            caveat={
              <>
                {advisoryCaveat(ejecteeProof.non_direct_accuracy)}
                {nonCausationCaveat(ejecteeProof.non_direct_accuracy)}
              </>
            }
          />
          <StatTile
            label="Proof-present share"
            value={formatPct(
              ejecteeProof.ejections_total > 0
                ? ejecteeProof.proof_present_ejections / ejecteeProof.ejections_total
                : null,
            )}
            hint={`${formatInt(ejecteeProof.proof_present_ejections)} / ${formatInt(ejecteeProof.ejections_total)} ejections had ejectee-specific proof on the record`}
          />
        </PartitionGroup>

        <PartitionGroup
          heading="Supporting instrument"
          unit="each cell carries its own denominator"
        >
          <StatTile
            label="Weak-flag-only convictions"
            value={`${formatInt(weak.weak_flag_only_convictions)} / ${formatInt(weak.flag_named_ejections)}`}
            hint={`${formatInt(weak.weak_flag_only_innocent)} of them ejected an innocent`}
            caveat={advisoryCaveat(weak.weak_flag_only_rate)}
          />
          <StatTile
            label="Turn → ballot consistency"
            value={formatPct(report.turn_ballot_consistency.consistency_rate)}
            hint={`${formatInt(report.turn_ballot_consistency.consistent_ballots)} / ${formatInt(report.turn_ballot_consistency.accusing_ballots)} accusing voters voted their accusation`}
            caveat={
              <MetricCaveat
                tone="note"
                title="Follow-through, not virtue: an honest mid-meeting revision scores as an inconsistency, and a SKIP counts against the voter only when someone they accused was votable."
              >
                follow-through, not correctness
              </MetricCaveat>
            }
          />
          <StatTile
            label="Roll-call coverage"
            value={`${formatPct(coverage.crew_pooled_coverage)} / ${formatPct(coverage.impostor_pooled_coverage)}`}
            hint={`crew ${formatInt(coverage.crew_turns_with_whereabouts)}/${formatInt(coverage.crew_turns)} vs impostor ${formatInt(coverage.impostor_turns_with_whereabouts)}/${formatInt(coverage.impostor_turns)} turns (pooled)`}
            caveat={
              <MetricCaveat
                tone="note"
                title={`A behavioural tell from the templates' role-differentiated output contract — NOT an observation-firewall leak. Estimator matters: the per-meeting macro-average reads ${formatPct(coverage.impostor_macro_average_coverage)} for impostors against the pooled ${formatPct(coverage.impostor_pooled_coverage)}.`}
              >
                pooled — macro differs
              </MetricCaveat>
            }
          />
          <StatTile
            label="Engine-redirected ballots"
            value={formatPct(report.redirected_ballots.redirected_ballot_share)}
            hint={`${formatInt(report.redirected_ballots.redirected_ballots)} / ${formatInt(report.redirected_ballots.ballots_total)} ballots · ${formatInt(report.redirected_ballots.redirected_eject_ballots)} still ejected`}
          />
          <StatTile
            label="Kill-scene evidence supply"
            value={
              supply === null
                ? "n/a"
                : `${formatInt(supply.crew_witnessed_kills)} / ${formatInt(supply.kills_total)}`
            }
            hint={
              supply === null
                ? "not supplied with this report"
                : `crew-witnessed kills · ${formatInt(supply.co_present_crew_kills)} with a crewmate co-present`
            }
            caveat={
              supply === null ? (
                <MetricCaveat
                  tone="note"
                  title="The kill-craft fold needs a state-hash-verified walk over the committed replay directory, so a live tournament report carries no supply cells. Rebuild via scripts/build_sample_report.py to populate them."
                >
                  not supplied
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
  // survival_rate is null EXACTLY when no impostor alibis were filed (the
  // eval-side None-iff-undefined convention), so formatPct's "n/a" already
  // covers the empty case — no frontend denominator special-case needed.
  return (
    <MetricSection
      title="Alibi fabrication"
      description={DASHBOARD_COPY.alibiDescription}
    >
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        <StatTile
          label="Survival rate"
          value={formatPct(report.survival_rate)}
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
      description="Distribution of the rubric's 0–100 score (9p2i) — an internal pacing/structure heuristic, not a human rating. Click a bucket to open those seeds in the Highlights reel."
      action={staleAction}
    >
      {rubric.status === "loading" ? (
        <p className="text-sm text-ink-500">Loading the interestingness rubric…</p>
      ) : rubric.status === "absent" ? (
        // Post-flip copy (Task 19.13, sweeping what Task 19.9's default flip
        // falsified). This panel used to say the DEFAULT-served set was 4p1i and
        // that its games were "mostly zero-meeting" — both wrong now: the default
        // is the curated 9p2i, which ships a rubric, and 4p1i's games are mostly
        // ONE-meeting (39 of 50 hold exactly one, 11 hold none). So this state is
        // reached by an explicit switch onto an unscored set, and it says which.
        <div className="rounded-lg border border-ink-200 bg-paper-1 px-4 py-6 text-center shadow-data">
          <p className="font-semibold text-ink-900">No interestingness rubric.</p>
          <p className="mt-1 text-sm text-ink-500">
            The selected set ships no rubric — expected for 4p1i, the fast
            technical fixture (median 12 ticks, at most one meeting per game).
            Switch back to the default 9p2i set, which ships one, or run{" "}
            <code className="font-mono text-xs">
              experiments/lab/rubric_score.py
            </code>{" "}
            over this set to populate the histogram.
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
              <span className="font-mono text-3xs text-ink-500">
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
      description={DASHBOARD_COPY.costDescription}
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
    <main aria-label="Tournament dashboard" className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm text-ink-500">{DASHBOARD_COPY.intro}</p>
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
          Loading tournament report…
        </p>
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
          <p className="mt-2 font-mono text-xs text-ink-500">{error}</p>
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
  // Refresh; `seedSet` re-triggers it on a live set switch. The URL comes from
  // `api/client`'s `apiUrl` seam (Task 19.13), so this panel reads the live API
  // in a normal build and the pre-baked JSON in the static demo bundle.
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
    fetch(apiUrl("/eval/rubric", seedSet), {
      headers: { Accept: "application/json" },
    })
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
