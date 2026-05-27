// One Phase-1 report (DESIGN.md §5.3): reporter + tick header, foregrounded
// free text, and collapsed-by-default structured observations + claims. Any
// observation/claim implicated in a contradiction shows a badge inline; the
// union of those badges is also surfaced in the header so it stays visible
// while the detail is collapsed.

import type {
  ContradictionView,
  ObservationClaimView,
  PlayerView,
  ReportView,
} from "../types/api";
import {
  ClaimLine,
  ContradictionBadge,
  dedupeContradictions,
  findContradictions,
  PlayerChip,
  reportClaimEventId,
  reportObsEventId,
} from "./ContradictionBadge";

interface ReportCardProps {
  report: ReportView;
  players: PlayerView[];
  contradictions: readonly ContradictionView[];
}

function ObservationLine({ obs }: { obs: ObservationClaimView }) {
  switch (obs.type) {
    case "saw_player":
      return (
        <span>
          <span className="font-semibold text-amber-300">saw</span> {obs.subject} in{" "}
          {obs.room} at tick {obs.tick}
          {obs.co_present.length > 0 && (
            <span className="text-neutral-400"> (with {obs.co_present.join(", ")})</span>
          )}
        </span>
      );
    case "completed_task":
      return (
        <span>
          <span className="font-semibold text-amber-300">completed</span>{" "}
          {obs.task_id} in {obs.room} at tick {obs.tick}
        </span>
      );
    case "found_body":
      return (
        <span>
          <span className="font-semibold text-amber-300">found body</span> of{" "}
          {obs.body_of} in {obs.room} at tick {obs.tick}
        </span>
      );
  }
}

export function ReportCard({ report, players, contradictions }: ReportCardProps) {
  const observations = report.observations.map((obs, index) => ({
    obs,
    contras: findContradictions(reportObsEventId(report, index), contradictions),
  }));
  const claims = report.claims.map((claim, index) => ({
    claim,
    contras: findContradictions(reportClaimEventId(report, index), contradictions),
  }));
  const flagged = dedupeContradictions([
    ...observations.flatMap((o) => o.contras),
    ...claims.flatMap((c) => c.contras),
  ]);
  const detailCount = observations.length + claims.length;

  return (
    <article className="rounded-lg border border-neutral-700 bg-neutral-800/60 p-4">
      <header className="mb-2 flex flex-wrap items-center gap-x-3 gap-y-1">
        <PlayerChip agentId={report.agent_id} players={players} />
        <span className="font-mono text-xs text-neutral-400">tick {report.tick}</span>
        {flagged.map((c) => (
          <ContradictionBadge key={c.contradiction_id} contradiction={c} />
        ))}
      </header>

      <p className="whitespace-pre-wrap text-base leading-relaxed text-neutral-100">
        {report.free_text}
      </p>

      {detailCount > 0 && (
        <details className="mt-3 text-sm text-neutral-300">
          <summary className="cursor-pointer select-none text-neutral-400">
            Structured detail ({observations.length} observation
            {observations.length === 1 ? "" : "s"}, {claims.length} claim
            {claims.length === 1 ? "" : "s"})
          </summary>
          <div className="mt-2 space-y-3">
            {observations.length > 0 && (
              <ul className="space-y-1">
                {observations.map(({ obs, contras }, index) => (
                  <li
                    key={`obs-${index}`}
                    className="flex flex-wrap items-center gap-2"
                  >
                    <span className="text-neutral-500">•</span>
                    <ObservationLine obs={obs} />
                    {contras.map((c) => (
                      <ContradictionBadge
                        key={c.contradiction_id}
                        contradiction={c}
                      />
                    ))}
                  </li>
                ))}
              </ul>
            )}
            {claims.length > 0 && (
              <ul className="space-y-1">
                {claims.map(({ claim, contras }, index) => (
                  <li
                    key={`claim-${index}`}
                    className="flex flex-wrap items-center gap-2"
                  >
                    <span className="text-neutral-500">•</span>
                    <ClaimLine claim={claim} />
                    {contras.map((c) => (
                      <ContradictionBadge
                        key={c.contradiction_id}
                        contradiction={c}
                      />
                    ))}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </details>
      )}
    </article>
  );
}
