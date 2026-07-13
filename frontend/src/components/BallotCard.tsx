// One vote ballot, rebuilt in the Playful cream/ink style (Task 12.7;
// design/phase-12/stage-1-design.md §3.4, slice 5; the 05-meeting render):
// voter → target (a chip or the neutral literal "SKIP"), a role-neutral
// confidence bar (0.0–1.0), the cleaned rationale, the rewrite-marker chips the
// meeting layer prepended (`rewrite_reasons`), and — Omniscient only — the vote's
// correctness.
//
// FIREWALL: the confidence bar is INK (role-neutral) — never trust/suspicion, so
// it cannot be read as alignment. Correctness reveals the target's role, so it is
// Omniscient-only and rendered by SHAPE + LABEL (✓ / ✗ + "correct" / "incorrect")
// in ink — never red-vs-green. Under As-agent fog it is suppressed entirely.

import { tokens } from "../tokens";
import type { BallotView, PlayerView } from "../types/api";

interface BallotCardProps {
  ballot: BallotView;
  players: PlayerView[];
  // Omniscient gates the role-revealing correctness marker (firewall).
  omniscient: boolean;
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

export function BallotCard({ ballot, players, omniscient }: BallotCardProps) {
  const isSkip = ballot.target === "SKIP";
  const confidence = Math.max(0, Math.min(1, ballot.confidence));
  const pct = Math.round(confidence * 100);
  // The cleaned rationale (markers stripped by the loader). When a vote fails to
  // parse, the loader intentionally leaves this empty because the raw
  // `rationale_text` is only the internal audit marker (the rewrite chip carries
  // the parse-default reason) — so do NOT fall back to the raw text here; show an
  // explicit empty-rationale state instead.
  const rationale = ballot.rationale_text_clean.trim();

  // Correctness (Omniscient only): a non-SKIP vote is "correct" iff its target
  // was actually an impostor. SKIP has no correctness.
  const targetRole = isSkip
    ? null
    : (players.find((p) => p.agent_id === ballot.target)?.role ?? null);
  const correct = targetRole === null ? null : targetRole === "IMPOSTOR";

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
        {omniscient && correct !== null && (
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

      {ballot.rewrite_reasons.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-1.5">
          {ballot.rewrite_reasons.map((reason, index) => (
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

      {/* Task 16.7.1: the voter's own-episodic-observation citation
          (`VoteBallot.primary_reason_observation_id`), display-only — the
          manager already validated it against the voter's memory, so the chip
          just surfaces the raw `{agent_id}:{tick}:{seq}` id (mono, role-neutral,
          no linking logic). */}
      {ballot.primary_reason_observation_id !== null && (
        <div className="mb-2 flex flex-wrap items-center gap-1.5">
          <span
            className="inline-flex items-center gap-1 rounded-md border border-ink-200 bg-paper-2 px-1.5 py-0.5 font-mono text-[10px] font-bold text-ink-700"
            title="the voter cited this observation from its own memory"
          >
            <span className="uppercase tracking-wide text-ink-400">cites</span>
            {ballot.primary_reason_observation_id}
          </span>
        </div>
      )}

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
