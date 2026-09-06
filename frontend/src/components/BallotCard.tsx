// One vote ballot: voter → target (a chip or the neutral literal "SKIP"), a
// role-neutral confidence bar (0.0–1.0), the cleaned rationale, the
// rewrite-marker chips the meeting layer prepended (`rewrite_reasons`), and the
// vote's correctness mark.
//
// FIREWALL: the confidence bar is INK (role-neutral) — never trust/suspicion, so
// it cannot be read as alignment. The correctness mark reveals the target's role
// and, said per ballot, names the impostors before the game does — so it renders
// only when the perspective is Omniscient AND the spectator has revealed
// outcomes (`showsBallotCorrectness` in `lib/copy.ts`), by SHAPE + LABEL (✓ / ✗ +
// "correct" / "incorrect") in ink, never red-vs-green.
// Superseded: the mark used to be gated on perspective alone, on the reasoning
// that reveal governs outcome and perspective governs what a frame may know.
//
// FIREWALL: one rewrite-reason chip is role-disclosing and IS gated on
// perspective alone — see `isRoleDisclosingRewriteReason` below. Reveal must
// never widen what fog hides, and it does not.

import { EvidenceLink } from "./EvidencePanel";
import { useReplayStore } from "../store/replayStore";
import { showsBallotCorrectness } from "../lib/copy";
import { tokens } from "../tokens";
import type { BallotView, PlayerView } from "../types/api";

// Rewrite reasons whose mere PRESENCE discloses ground-truth roles, so the chip
// is Omniscient-only (`api.replay_loader._BALLOT_PREFIX_MARKERS` is the label
// registry; the guard itself lives in `meetings.manager`).
//
// `teammate_coerced` fires ONLY when the voter targeted a fellow impostor, so
// the chip announces two roles at once — the voter's and the coerced target's —
// i.e. the impostor pairing. Every other label (`invalid_target`,
// `under_gate_redirect`, `invalid_reason_id`, `invalid_observation_id`,
// `uncited_coerced`, `parse_default`) is a parse/gate audit fact that carries no
// role information, so it renders in every perspective.
//
// Gated on PERSPECTIVE alone, deliberately never on `revealOutcome`: reveal
// governs OUTCOME information, perspective governs what the current frame may
// know (`store/replayStore.ts`). A spectator who revealed the ending is still
// standing behind one agent's eyes, and the impostor pairing is not part of the
// ending — so reveal must never WIDEN what fog hides here. Suppressed SILENTLY:
// a "1 chip hidden" placeholder would leak exactly the fact being withheld.
//
// MODULE-PRIVATE AND FROZEN, exposed only through the pure predicate below.
// `ReadonlySet` would be a compile-time view over a runtime-mutable `Set`: an
// exported one could be emptied through a cast or from plain JS, and every
// later as-agent render would then disclose the pairing — a firewall gate must
// not be a mutable global anyone can switch off (AGENTS.md "no module-level
// mutable state"). `Object.freeze` makes the list immutable in fact, and not
// exporting it means there is no handle to reach for in the first place.
const ROLE_DISCLOSING_REWRITE_REASONS: readonly string[] = Object.freeze([
  "teammate_coerced",
]);

/**
 * Whether a rewrite-reason label discloses ground-truth roles.
 *
 * The exported form of the policy is this pure predicate rather than the
 * collection itself — callers (including Task 19.12's Vitest baseline) can ask
 * the question without holding anything they could mutate.
 */
export function isRoleDisclosingRewriteReason(reason: string): boolean {
  return ROLE_DISCLOSING_REWRITE_REASONS.includes(reason);
}

/**
 * The rewrite-reason chips this perspective may see.
 *
 * Exported as a pure function (not inlined in the render) so the gate is
 * directly assertable: the stories pin the three rendered states — Omniscient,
 * As-agent fog with the outcome reveal OFF, As-agent fog with it ON — and the
 * rule itself is a unit any test can call with no DOM. Note it takes NO reveal
 * argument: reveal cannot widen this, by construction.
 */
export function visibleRewriteReasons(
  reasons: readonly string[],
  omniscient: boolean,
): readonly string[] {
  return omniscient
    ? reasons
    : reasons.filter((reason) => !isRoleDisclosingRewriteReason(reason));
}

/**
 * The rationale body this perspective may see.
 *
 * Hiding the chip is not enough. When the teammate guard coerces a ballot it
 * also REPLACES the model's rationale with one fixed sentinel sentence
 * (`meetings.manager.TEAMMATE_COERCED_VOTE_RATIONALE`) — and that guard is its
 * only writer, so the sentence appears on coerced ballots and nowhere else. It
 * is the rationale BODY, not a marker, so the loader's marker strip leaves it in
 * `rationale_text_clean` and the card would print it as the voter's stated
 * reason: the same impostor pairing disclosed in prose instead of in a chip.
 *
 * So a fogged ballot carrying a role-disclosing reason shows NO rationale at
 * all, and falls through to the card's ordinary empty-rationale state — the
 * state the card already renders for a ballot whose rationale did not survive
 * the loader's marker strip, rather than a bespoke "hidden" affordance that
 * would itself announce that something was withheld.
 */
export function visibleRationale(ballot: BallotView, omniscient: boolean): string {
  const roleDisclosing = ballot.rewrite_reasons.some(isRoleDisclosingRewriteReason);
  return !omniscient && roleDisclosing ? "" : ballot.rationale_text_clean.trim();
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

export function BallotCard({
  ballot,
  players,
  omniscient,
  revealOutcome,
}: BallotCardProps) {
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const isSkip = ballot.target === "SKIP";
  const confidence = Math.max(0, Math.min(1, ballot.confidence));
  const pct = Math.round(confidence * 100);
  // The cleaned rationale (markers stripped by the loader). When a vote fails to
  // parse, the loader intentionally leaves this empty because the raw
  // `rationale_text` is only the internal audit marker (the rewrite chip carries
  // the parse-default reason) — so do NOT fall back to the raw text here; show an
  // explicit empty-rationale state instead. Under As-agent fog the guard's
  // sentinel body drops out too (see the two helpers above): suppressing the
  // chip without it would just move the disclosure into a sentence.
  const rationale = visibleRationale(ballot, omniscient);
  const rewriteReasons = visibleRewriteReasons(ballot.rewrite_reasons, omniscient);

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

      <div className="mb-2 flex items-center gap-2">
        <span className="w-20 shrink-0 font-mono text-[10px] uppercase tracking-wide text-ink-400">
          confidence
        </span>
        <div className="h-2 flex-1 overflow-hidden rounded-pill bg-paper-3">
          <div className="h-full rounded-pill bg-ink-700" style={{ width: `${pct}%` }} />
        </div>
        <span className="w-10 shrink-0 text-right font-mono text-xs text-ink-700">
          {ballot.confidence.toFixed(2)}
        </span>
      </div>

      {rewriteReasons.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-1.5">
          {rewriteReasons.map((reason, index) => (
            <span
              key={`rewrite-${index}`}
              className="inline-flex items-center gap-1 rounded-md border border-ink-200 bg-paper-3 px-1.5 py-0.5 font-mono text-[10px] font-bold text-ink-700"
            >
              <span aria-hidden>↻</span>
              {reason}
            </span>
          ))}
        </div>
      )}

      <div className="mb-2 flex flex-wrap gap-2">
        {ballot.primary_reason_id !== null && meetingId !== null && <EvidenceLink target={{ kind: "statement", id: ballot.primary_reason_id, meetingId, observerId: ballot.voter }}>Cited statement · {ballot.primary_reason_id}</EvidenceLink>}
        {ballot.primary_reason_observation_id !== null && (meetingId !== null ? <EvidenceLink target={{ kind: "observation", id: ballot.primary_reason_observation_id, meetingId, observerId: ballot.voter }}>Cited observation · {ballot.primary_reason_observation_id}</EvidenceLink> : <span className="text-xs">{ballot.primary_reason_observation_id}</span>)}
      </div>

      {rationale !== "" ? (
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
