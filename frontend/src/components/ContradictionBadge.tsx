// Contradiction badge plus the small transcript-render primitives the meeting
// cards share (DESIGN.md §5.3, §5.4). `PlayerChip`, `ClaimLine`, the
// contradiction event-id matchers and `findContradictions` live here because
// Task 4.6's file scope is exactly the six meeting components plus App.tsx — a
// dedicated util module would be out of scope, and routing these helpers
// through MeetingView.tsx (which imports the cards) would create an import
// cycle. ContradictionBadge imports no sibling component, so it is the natural
// leaf every card can depend on without a cycle.

import type {
  ContradictionView,
  PlayerView,
  ReportView,
  StatementClaimView,
  StatementView,
} from "../types/api";

const FALLBACK_COLOR = "#888888";

function playerColor(agentId: string, players: PlayerView[]): string {
  return players.find((p) => p.agent_id === agentId)?.color ?? FALLBACK_COLOR;
}

function playerName(agentId: string, players: PlayerView[]): string {
  return players.find((p) => p.agent_id === agentId)?.display_name ?? agentId;
}

interface PlayerChipProps {
  agentId: string;
  players: PlayerView[];
}

// Color swatch + readable display name + the raw agent id. The DoD references
// the agent/voter id explicitly, so it is always shown alongside the name.
export function PlayerChip({ agentId, players }: PlayerChipProps) {
  return (
    <span className="inline-flex min-w-0 max-w-full items-center gap-1.5 align-middle">
      <span
        aria-hidden
        className="inline-block h-3 w-3 shrink-0 rounded-full ring-1 ring-black/50"
        style={{ backgroundColor: playerColor(agentId, players) }}
      />
      <span className="min-w-0 break-words font-medium text-neutral-100">
        {playerName(agentId, players)}
      </span>
      <span className="min-w-0 break-all font-mono text-xs text-neutral-400">
        {agentId}
      </span>
    </span>
  );
}

// Discriminated render of one structured claim (shared by reports + statements;
// both expose `StatementClaimView[]`). TypeScript narrows each `case` exhaustively.
export function ClaimLine({ claim }: { claim: StatementClaimView }) {
  switch (claim.type) {
    case "alibi":
      return (
        <span className="min-w-0 break-words">
          <span className="font-semibold text-sky-300">alibi</span> · {claim.subject}{" "}
          in {claim.room} (ticks {claim.from_tick}–{claim.to_tick})
          {claim.evidence.length > 0 && (
            <span className="text-neutral-400">
              {" "}
              · evidence: {claim.evidence.join(", ")}
            </span>
          )}
        </span>
      );
    case "accusation":
      return (
        <span className="min-w-0 break-words">
          <span className="font-semibold text-rose-300">accusation</span> · against{" "}
          {claim.against} (confidence {claim.confidence.toFixed(2)}) — {claim.reason}
        </span>
      );
    case "corroboration":
      return (
        <span className="min-w-0 break-words">
          <span className="font-semibold text-emerald-300">corroboration</span> ·
          supports {claim.supports} at tick {claim.on_tick} — {claim.reason}
        </span>
      );
  }
}

// Event-id construction mirrors `meetings/transcript.py` exactly: contradictions
// reference the structured artifact that produced them, not the bare statement
// id. (The task hint's `statement_id === event_a_id` shorthand never matches the
// real `stmt:<id>:claim:<index>` / `report:<agent>@<tick>:<claim|obs>:<index>`
// format, so we reconstruct those ids and match on them.)
export function reportClaimEventId(report: ReportView, index: number): string {
  return `report:${report.agent_id}@${report.tick}:claim:${index}`;
}

export function reportObsEventId(report: ReportView, index: number): string {
  return `report:${report.agent_id}@${report.tick}:obs:${index}`;
}

export function statementClaimEventId(
  statement: StatementView,
  index: number,
): string {
  return `stmt:${statement.statement_id}:claim:${index}`;
}

export function findContradictions(
  eventId: string,
  contradictions: readonly ContradictionView[],
): ContradictionView[] {
  return contradictions.filter(
    (c) => c.event_a_id === eventId || c.event_b_id === eventId,
  );
}

// A single contradiction can implicate two events on one card (e.g. two
// conflicting alibi claims in the same report); dedupe by id for the always-on
// card-header summary.
export function dedupeContradictions(
  items: readonly ContradictionView[],
): ContradictionView[] {
  const seen = new Set<string>();
  const out: ContradictionView[] = [];
  for (const c of items) {
    if (!seen.has(c.contradiction_id)) {
      seen.add(c.contradiction_id);
      out.push(c);
    }
  }
  return out;
}

// Kind is color-coded but role-neutral — the colors do not encode crew/impostor.
const KIND_STYLES: Record<ContradictionView["kind"], string> = {
  alibi_conflict: "bg-amber-900/60 text-amber-200 ring-amber-600/60",
  alibi_vs_sighting: "bg-fuchsia-900/60 text-fuchsia-200 ring-fuchsia-600/60",
};

const KIND_LABELS: Record<ContradictionView["kind"], string> = {
  alibi_conflict: "alibi conflict",
  alibi_vs_sighting: "alibi vs sighting",
};

export function ContradictionBadge({
  contradiction,
}: {
  contradiction: ContradictionView;
}) {
  return (
    <span
      title={contradiction.description}
      className={
        "inline-flex items-center rounded px-1.5 py-0.5 text-xs font-semibold uppercase tracking-wide ring-1 " +
        KIND_STYLES[contradiction.kind]
      }
    >
      {KIND_LABELS[contradiction.kind]}
    </span>
  );
}
