// Public ballot targets remain visible. Private rationale, confidence and citations
// require the voter’s perspective or omniscient mode. Outcome reveal is separate.

import { useId } from "react";

import { EvidenceLink } from "./EvidencePanel";
import { useReplayStore } from "../store/replayStore";
import { BALLOT_COPY, showsBallotCorrectness } from "../lib/copy";
import { tokens } from "../tokens";
import type { BallotView, PlayerView } from "../types/api";

/** Private ballot reasoning is not spoken to the table. */
export function visibleRationale(
  ballot: BallotView,
  omniscient: boolean,
  observerId: string | null = null,
): string {
  return omniscient || observerId === ballot.voter ? ballot.rationale_text_clean.trim() : "";
}

/** Explain the applied decision without treating an adjustment as model intent. */
function rewriteLabel(reason: string): string {
  switch (reason) {
    case "invalid_target": return "Invalid target changed to skip";
    case "teammate_coerced": return "Teammate vote changed to skip";
    case "under_gate_redirect": return "Vote redirected by the meeting rule";
    case "invalid_reason_id": return "Unknown statement citation removed";
    case "invalid_observation_id": return "Unknown observation citation removed";
    case "uncited_coerced": return "Unsupported vote changed to skip";
    case "off_target_coerced": return "Off-target citation changed vote to skip";
    case "invalid_basis": return "Unreadable stated basis removed";
    case "parse_default": return "Unreadable ballot replaced with skip";
    default: return "Recorded vote adjustment";
  }
}

/**
 * The meeting's own one-word finding about this ballot's basis, in plain language.
 *
 * A DESCRIPTION, not an adjustment, which is why it renders apart from
 * `rewriteLabel`'s ↻ chips: the meeting layer writes this label and never moves
 * a target, and the tally never reads it, so the vote shown above the chip is
 * the one the voter cast. An unrecognised value renders nothing rather than a
 * guess — a label this build has not been taught is not a label it may narrate.
 *
 * Every committed recording predates the field and carries `null`, so the chip
 * is absent from the shipped tour until the re-record.
 */
function groundingLabelText(label: string | null): string | null {
  if (label === null) return null;
  const labels: Record<string, string> = BALLOT_COPY.groundingLabels;
  return labels[label] ?? null;
}

interface BallotCardProps {
  ballot: BallotView;
  players: PlayerView[];
  // Omniscient gates the role-disclosing rewrite chips (firewall) and is half of
  // the correctness-mark gate.
  omniscient: boolean;
  // The spectator's outcome reveal — the other half of the correctness-mark
  // gate. Required, not optional: an omitted spoiler gate must be a compile
  // error, never a silent default to "show everything".
  revealOutcome: boolean;
}

function playerColor(agentId: string, players: PlayerView[]): string {
  return players.find((p) => p.agent_id === agentId)?.color ?? tokens.ink[400];
}

function PlayerPill({
  agentId,
  players,
}: {
  agentId: string;
  players: PlayerView[];
}) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-md border border-ink-200 bg-paper-0 px-2 py-0.5">
      <span
        aria-hidden
        className="inline-block h-3 w-3 shrink-0 rounded-full border border-ink-900"
        style={{ backgroundColor: playerColor(agentId, players) }}
      />
      <span className="font-mono text-xs font-bold text-ink-900">{agentId}</span>
    </span>
  );
}

/**
 * The note an entry earns when the card's HEADER already shows it, or `null`.
 *
 * The recorded list is not a list of OTHER players, and the bytes say so: over
 * `replays/samples/9p2i`, 27 of 869 ballots list the voter itself and 22 list
 * the target the vote applied to (`scripts/measure_featured_criterion.py
 * --alternatives`). Such an entry renders a second pill identical to one in the
 * header, which without a note reads as a different player at the table. The
 * entry is kept — the block is the record — and named instead.
 *
 * The voter wins a tie, so an entry that is somehow both is the voter: a vote is
 * cast BY that ballot and the header's left pill is the one it duplicates.
 */
function alternativeNote(entry: string, voter: string, target: string): string | null {
  if (entry === voter) return BALLOT_COPY.alternativesSelfNote;
  if (entry === target) return BALLOT_COPY.alternativesTargetNote;
  return null;
}

/**
 * One entry of `considered_alternatives`, which is a recorded list of STRINGS.
 *
 * A served player renders as the same pill the target does; anything else — an
 * id no longer in the game, or the literal `SKIP` the ballot schema also admits
 * (tests/api/test_schemas.py) — renders as a plain mono token instead. The
 * distinction is the point: a pill carries an identity colour and reads as "a
 * player at this table", so a value that is not one must not be able to wear it.
 *
 * `note` is plain text inside the same `li`, so a screen reader reads it with
 * the entry it qualifies rather than as a separate item.
 */
function AlternativeEntry({
  entry,
  players,
  note,
}: {
  entry: string;
  players: PlayerView[];
  note: string | null;
}) {
  const token = players.some((player) => player.agent_id === entry) ? (
    <PlayerPill agentId={entry} players={players} />
  ) : (
    <span className="inline-flex items-center rounded-md border border-dashed border-ink-200 bg-paper-2 px-2 py-0.5 font-mono text-xs text-ink-500">
      {entry}
    </span>
  );
  if (note === null) return token;
  return (
    <span className="inline-flex items-center gap-1">
      {token}
      <span className="font-mono text-[10px] text-ink-400">({note})</span>
    </span>
  );
}

export function BallotCard({
  ballot,
  players,
  omniscient,
  revealOutcome,
}: BallotCardProps) {
  const alternativesLabelId = useId();
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const perspective = useReplayStore((s) => s.perspective);
  const observerId = perspective.mode === "agent" ? perspective.agentId : null;
  const privateVisible = omniscient || observerId === ballot.voter;
  const isSkip = ballot.target === "SKIP";
  const confidence = Math.max(0, Math.min(1, ballot.confidence));
  const pct = Math.round(confidence * 100);
  const rationale = visibleRationale(ballot, omniscient, observerId);
  const rewriteReasons = privateVisible ? ballot.rewrite_reasons : [];
  // Same private class as the citations and the weighed list: the label reports
  // what the voter cited, and `not_assessed` names a firewall coercion, so it
  // rides the perspective gate rather than sitting beside the public target.
  const grounding = groundingLabelText(ballot.grounding_label);

  // Correctness: a non-SKIP vote is "correct" iff its target was actually an
  // impostor. SKIP has no correctness. Per ballot the mark names the impostors
  // before the game does, so it needs the reveal as well as the perspective —
  // see `showsBallotCorrectness`.
  const targetRole = isSkip
    ? null
    : (players.find((p) => p.agent_id === ballot.target)?.role ?? null);
  const correct = targetRole === null ? null : targetRole === "IMPOSTOR";
  const showCorrectness = showsBallotCorrectness(omniscient, revealOutcome);

  return (
    <article className="rounded-lg border border-ink-100 bg-paper-1 p-3 shadow-data">
      <header className="mb-2 flex flex-wrap items-center gap-2">
        <PlayerPill agentId={ballot.voter} players={players} />
        <span aria-hidden className="font-mono text-xs text-ink-400">
          →
        </span>
        {isSkip ? (
          <span className="rounded-md border border-ink-200 bg-paper-2 px-2 py-0.5 font-mono text-xs font-bold uppercase tracking-wide text-ink-500">
            skip
          </span>
        ) : (
          <PlayerPill agentId={ballot.target} players={players} />
        )}
        {showCorrectness && correct !== null && (
          <span
            className="ml-auto inline-flex items-center gap-1 rounded-md border border-ink-300 px-1.5 py-0.5 font-mono text-[10px] font-bold uppercase tracking-wide text-ink-700"
            title={
              correct
                ? "this vote targeted an impostor"
                : "this vote targeted a crewmate"
            }
          >
            <span aria-hidden>{correct ? "✓" : "✗"}</span>
            {correct ? "correct" : "incorrect"}
          </span>
        )}
      </header>

      {privateVisible && <div className="mb-2 flex items-center gap-2">
        <span className="w-20 shrink-0 font-mono text-[10px] uppercase tracking-wide text-ink-400">
          confidence
        </span>
        <div className="h-2 flex-1 overflow-hidden rounded-pill bg-paper-3">
          <div className="h-full rounded-pill bg-ink-700" style={{ width: `${pct}%` }} />
        </div>
        <span className="w-10 shrink-0 text-right font-mono text-xs text-ink-700">
          {ballot.confidence.toFixed(2)}
        </span>
      </div>}

      {rewriteReasons.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-1.5">
          {rewriteReasons.map((reason, index) => (
            <span
              key={`rewrite-${index}`}
              className="inline-flex items-center gap-1 rounded-md border border-ink-200 bg-paper-3 px-1.5 py-0.5 font-mono text-[10px] font-bold text-ink-700"
            >
              <span aria-hidden>↻</span>
              {rewriteLabel(reason)}
            </span>
          ))}
        </div>
      )}

      {privateVisible && <div className="mb-2 flex flex-wrap gap-2">
        {ballot.primary_reason_id !== null && meetingId !== null && <EvidenceLink target={{ kind: "statement", id: ballot.primary_reason_id, meetingId, observerId: ballot.voter }}>Cited statement · {ballot.primary_reason_id}</EvidenceLink>}
        {ballot.primary_reason_observation_id !== null && (meetingId !== null ? <EvidenceLink target={{ kind: "observation", id: ballot.primary_reason_observation_id, meetingId, observerId: ballot.voter }}>Cited observation · {ballot.primary_reason_observation_id}</EvidenceLink> : <span className="text-xs">{ballot.primary_reason_observation_id}</span>)}
      </div>}

      {/* The one weighing artefact already on disk: who this voter wrote down
          while choosing. Same private class as the citations above it — the
          model wrote it, the table never heard it, and an impostor's list can
          expose whether it weighed its teammate — so it lives behind the same
          gate rather than beside the public target. An entry the header already
          shows is annotated by `alternativeNote`, never dropped.

          A block rather than an inline row on purpose: the substrate wave stacks
          on this component. The meeting-written grounding label now sits next to
          this heading, and the weighing card adds a counter-evidence link beside
          the two citation links above. */}
      {privateVisible && (
        <div className="mb-2" data-ballot-alternatives>
          <span
            id={alternativesLabelId}
            className="font-mono text-[10px] uppercase tracking-wide text-ink-400"
          >
            {BALLOT_COPY.alternativesLabel}
          </span>
          {grounding !== null && (
            <span
              data-ballot-grounding
              className="ml-2 inline-flex items-center rounded-md border border-ink-200 bg-paper-2 px-1.5 py-0.5 font-mono text-[10px] text-ink-700"
              title={BALLOT_COPY.groundingLabel}
            >
              {grounding}
            </span>
          )}
          {ballot.considered_alternatives.length > 0 ? (
            // Recorded order, whatever the length: the list is two ids wide in
            // every committed recording today and the render must not bake that
            // in, so it wraps instead of truncating.
            <ul
              aria-labelledby={alternativesLabelId}
              className="mt-1 flex flex-wrap items-center gap-1.5"
            >
              {ballot.considered_alternatives.map((entry, index) => (
                <li key={`alt-${index}-${entry}`}>
                  <AlternativeEntry
                    entry={entry}
                    players={players}
                    note={alternativeNote(entry, ballot.voter, ballot.target)}
                  />
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-1 font-mono text-xs italic text-ink-400">
              {BALLOT_COPY.alternativesEmpty}
            </p>
          )}
        </div>
      )}

      {privateVisible && ballot.rewrite_reasons.includes("under_gate_redirect") && (
        <p className="mb-1 text-xs text-ink-500">The recorded explanation describes the original choice, before the vote was redirected.</p>
      )}
      {!privateVisible ? (
        <p className="text-xs text-ink-500">Private ballot reasoning. View {ballot.voter}’s perspective to inspect it.</p>
      ) : rationale !== "" ? (
        <p className="whitespace-pre-wrap break-words text-sm leading-relaxed text-ink-900">
          {rationale}
        </p>
      ) : (
        <p className="font-mono text-xs italic text-ink-400">
          no rationale recorded
        </p>
      )}
    </article>
  );
}
