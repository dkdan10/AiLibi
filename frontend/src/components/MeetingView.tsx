// The meeting transcript overlay (DESIGN.md §5, §7). Mounts iff
// `selectedMeetingId !== null` and the meeting exists in the current replay.
// Renders as a modal-style overlay (dim backdrop + centered panel) above the
// PixiJS map canvas via fixed positioning + z-index, leaving MapView untouched.
// Pure React + Tailwind; no PixiJS.

import { useEffect } from "react";
import type { ReactNode } from "react";

import { useReplayStore } from "../store/replayStore";
import type {
  BallotView,
  ContradictionView,
  MeetingView as MeetingViewDTO,
  PlayerView,
  ReportView,
  StatementView,
} from "../types/api";
import { BallotCard } from "./BallotCard";
import { ContradictionBadge, PlayerChip } from "./ContradictionBadge";
import { ReportCard } from "./ReportCard";
import { StatementCard } from "./StatementCard";

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="mb-6">
      <h3 className="mb-3 border-b border-neutral-700 pb-1 text-lg font-bold text-neutral-200">
        {title}
      </h3>
      {children}
    </section>
  );
}

function Empty({ children }: { children: ReactNode }) {
  return <p className="text-sm italic text-neutral-500">{children}</p>;
}

// Outcome color is role-neutral by design: encoding EJECTED green/red would leak
// whether the ejected player was the impostor. Only the ejected player's own
// color swatch (via PlayerChip) carries color.
function OutcomeBanner({
  meeting,
  players,
}: {
  meeting: MeetingViewDTO;
  players: PlayerView[];
}) {
  return (
    <header className="mb-6 rounded-lg border border-neutral-600 bg-neutral-800 p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h2 className="text-3xl font-extrabold tracking-tight text-neutral-100">
          {meeting.outcome}
        </h2>
        <span className="min-w-0 break-words text-sm text-neutral-400">
          triggered by{" "}
          <span className="font-medium text-neutral-200">{meeting.triggered_by}</span>{" "}
          ({meeting.trigger_kind})
        </span>
      </div>
      {meeting.outcome === "EJECTED" && meeting.ejected_player_id !== null ? (
        <div className="mt-3 flex flex-wrap items-center gap-2 text-lg">
          <span className="text-neutral-400">ejected:</span>
          <PlayerChip agentId={meeting.ejected_player_id} players={players} />
        </div>
      ) : (
        <p className="mt-3 text-sm text-neutral-400">No player was ejected.</p>
      )}
    </header>
  );
}

function ReportsSection({
  reports,
  contradictions,
  players,
}: {
  reports: readonly ReportView[];
  contradictions: readonly ContradictionView[];
  players: PlayerView[];
}) {
  return (
    <Section title={`Reports (${reports.length})`}>
      {reports.length === 0 ? (
        <Empty>No reports.</Empty>
      ) : (
        <div className="space-y-3">
          {reports.map((report, index) => (
            <ReportCard
              key={`${report.agent_id}@${report.tick}#${index}`}
              report={report}
              players={players}
              contradictions={contradictions}
            />
          ))}
        </div>
      )}
    </Section>
  );
}

function StatementsSection({
  statements,
  contradictions,
  players,
}: {
  statements: readonly StatementView[];
  contradictions: readonly ContradictionView[];
  players: PlayerView[];
}) {
  const byRound = new Map<number, StatementView[]>();
  for (const statement of statements) {
    const group = byRound.get(statement.round_index);
    if (group !== undefined) {
      group.push(statement);
    } else {
      byRound.set(statement.round_index, [statement]);
    }
  }
  const rounds = [...byRound.keys()].sort((a, b) => a - b);

  return (
    <Section title="Statements">
      {rounds.length === 0 ? (
        <Empty>No statements.</Empty>
      ) : (
        <div className="space-y-5">
          {rounds.map((round) => (
            <div key={round}>
              <h4 className="mb-2 text-sm font-semibold uppercase tracking-wide text-neutral-400">
                Round {round}
              </h4>
              <div className="space-y-3">
                {(byRound.get(round) ?? []).map((statement) => (
                  <StatementCard
                    key={statement.statement_id}
                    statement={statement}
                    players={players}
                    contradictions={contradictions}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </Section>
  );
}

// Tally is computed client-side (the DTO ships no precomputed tally): group by
// target, count, and always surface a SKIP bucket (even at zero, per the DoD
// example). Order by descending count, SKIP last, then lexical by id.
function tallyBallots(
  ballots: readonly BallotView[],
): { target: string; count: number }[] {
  const counts = new Map<string, number>();
  for (const ballot of ballots) {
    counts.set(ballot.target, (counts.get(ballot.target) ?? 0) + 1);
  }
  if (!counts.has("SKIP")) {
    counts.set("SKIP", 0);
  }
  return [...counts.entries()]
    .map(([target, count]) => ({ target, count }))
    .sort((a, b) => {
      if (b.count !== a.count) return b.count - a.count;
      if (a.target === "SKIP") return 1;
      if (b.target === "SKIP") return -1;
      return a.target < b.target ? -1 : a.target > b.target ? 1 : 0;
    });
}

function BallotsSection({
  ballots,
  players,
}: {
  ballots: readonly BallotView[];
  players: PlayerView[];
}) {
  const summary = tallyBallots(ballots)
    .map((row) => `${row.target}: ${row.count} vote${row.count === 1 ? "" : "s"}`)
    .join(" · ");

  return (
    <Section title={`Ballots (${ballots.length})`}>
      {ballots.length === 0 ? (
        <Empty>No ballots.</Empty>
      ) : (
        <>
          <p className="mb-3 break-words font-mono text-sm text-neutral-300">{summary}</p>
          <div className="space-y-3">
            {ballots.map((ballot, index) => (
              <BallotCard
                key={`${ballot.voter}#${index}`}
                ballot={ballot}
                players={players}
              />
            ))}
          </div>
        </>
      )}
    </Section>
  );
}

function ContradictionsSection({
  contradictions,
}: {
  contradictions: readonly ContradictionView[];
}) {
  return (
    <Section title={`Contradictions (${contradictions.length})`}>
      {contradictions.length === 0 ? (
        <Empty>None flagged.</Empty>
      ) : (
        <ul className="space-y-2">
          {contradictions.map((contradiction) => (
            <li
              key={contradiction.contradiction_id}
              className="flex flex-wrap items-center gap-2 rounded border border-neutral-700 bg-neutral-800/40 p-2 text-sm"
            >
              <ContradictionBadge contradiction={contradiction} />
              <span className="min-w-0 break-words text-neutral-200">
                {contradiction.description}
              </span>
              {contradiction.subjects.length > 0 && (
                <span className="min-w-0 break-words text-xs text-neutral-400">
                  subjects: {contradiction.subjects.join(", ")}
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </Section>
  );
}

function MetadataFooter({ meeting }: { meeting: MeetingViewDTO }) {
  const versions = Object.entries(meeting.prompt_versions);
  const callCount = meeting.llm_calls.length;

  return (
    <details className="mt-6 border-t border-neutral-700 pt-3 text-xs text-neutral-500">
      <summary className="cursor-pointer select-none">Meeting metadata</summary>
      <dl className="mt-2 space-y-1 break-words">
        <div>
          <span className="text-neutral-400">meeting_id:</span>{" "}
          <span className="font-mono">{meeting.meeting_id}</span>
        </div>
        <div>
          <span className="text-neutral-400">tick:</span>{" "}
          <span className="font-mono">{meeting.tick}</span>
        </div>
        <div>
          <span className="text-neutral-400">total_cost_usd:</span>{" "}
          <span className="font-mono">${meeting.total_cost_usd.toFixed(4)}</span>
        </div>
        <div>
          <span className="text-neutral-400">prompt_versions:</span>
          {versions.length === 0 ? (
            <span className="font-mono"> (none)</span>
          ) : (
            <ul className="ml-4 mt-0.5">
              {versions.map(([key, value]) => (
                <li key={key} className="font-mono">
                  {key}: {value}
                </li>
              ))}
            </ul>
          )}
        </div>
        <div>
          {callCount} LLM call{callCount === 1 ? "" : "s"} (drill into ThoughtStream
          for details)
        </div>
      </dl>
    </details>
  );
}

export function MeetingView() {
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const replay = useReplayStore((s) => s.currentReplay);
  const selectMeeting = useReplayStore((s) => s.selectMeeting);

  const meeting =
    meetingId !== null && replay !== null
      ? replay.meetings.find((m) => m.meeting_id === meetingId)
      : undefined;
  const isOpen = meetingId !== null && replay !== null && meeting !== undefined;

  // Clear a stale selection (e.g. the replay switched out from under an open
  // overlay) in an effect rather than during render, so the store setter is
  // never called mid-render.
  useEffect(() => {
    if (meetingId !== null && replay !== null && meeting === undefined) {
      selectMeeting(null);
    }
  }, [meetingId, replay, meeting, selectMeeting]);

  // Close on Escape while open.
  useEffect(() => {
    if (!isOpen) {
      return;
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        selectMeeting(null);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [isOpen, selectMeeting]);

  if (!isOpen || meeting === undefined || replay === null) {
    return null;
  }

  return (
    // The left BeliefMatrix (z-[55], ≤24rem) and right ThoughtStream (z-[60],
    // ≤20rem) rails mount alongside an open meeting and paint above this z-50
    // overlay. Reserve a gutter wider than each rail (lg+ only) so the centered
    // panel lands in the gap between them instead of being clipped beneath them.
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`Meeting at tick ${meeting.tick}`}
      className="fixed inset-0 z-50 overflow-auto bg-black/70 lg:pl-[25rem] lg:pr-[21rem]"
      onClick={() => {
        selectMeeting(null);
      }}
    >
      <div
        className="relative mx-auto my-8 max-w-4xl rounded-xl bg-neutral-900 p-6 shadow-2xl ring-1 ring-neutral-700"
        onClick={(event) => {
          event.stopPropagation();
        }}
      >
        <button
          type="button"
          aria-label="Close meeting"
          onClick={() => {
            selectMeeting(null);
          }}
          className="absolute right-4 top-4 rounded border border-neutral-600 bg-neutral-800 px-3 py-1 text-sm text-neutral-200 transition-colors hover:bg-neutral-700"
        >
          Close
        </button>

        <OutcomeBanner meeting={meeting} players={replay.players} />
        <ReportsSection
          reports={meeting.reports}
          contradictions={meeting.contradictions}
          players={replay.players}
        />
        <StatementsSection
          statements={meeting.statements}
          contradictions={meeting.contradictions}
          players={replay.players}
        />
        <BallotsSection ballots={meeting.ballots} players={replay.players} />
        <ContradictionsSection contradictions={meeting.contradictions} />
        <MetadataFooter meeting={meeting} />
      </div>
    </div>
  );
}
