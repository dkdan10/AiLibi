// The meeting transcript surface, rebuilt in the Playful cream/ink style
// (Task 12.7; design/phase-12/stage-1-design.md §3.4, slice 5; the committed
// 05-meeting render; the accusation-chain / ballots / verdict code in
// playful-system.dc.html). Mounts iff `selectedMeetingId !== null` and the
// meeting exists in the current replay, as the App.tsx overlay slot (the
// map↔meeting morph) — the shell is never edited (Wave-B mount discipline).
//
// Layout mirrors 05-meeting: a left "Accusation chain & transcript" panel (a
// chain summary + the threaded TurnCard waterfall, indented by `reply_to`) and a
// right column of "Ballots" + the dark "Resolution · §4.6" verdict.
//
// THE §4.6 VERDICT renders from `GateView` — the REAL rule (plurality + at least
// one leader ballot ≥ threshold 0.6; tie / SKIP-plurality → SKIP). The converge
// mock's "simple majority of living voters" copy is WRONG and is NOT replicated.
//
// FIREWALL: the outcome banner + vote correctness are ROLE-NEUTRAL (shape /
// label, never red-vs-green); role-revealing extras (correctness, the post-hoc
// impostor reveal) are Omniscient-only. The claim↔map cross-highlight (wired in
// TurnCard → store → MapView) lights only the PUBLIC referent a sighting names.

import { useEffect, useRef } from "react";
import type { ReactNode } from "react";

import { useReplayStore } from "../store/replayStore";
import { useFocusTrap } from "../hooks/useFocusTrap";
import { tokens } from "../tokens";
import type {
  BallotView,
  ContradictionView,
  GateView,
  MeetingView as MeetingViewDTO,
  PlayerView,
  TurnView,
} from "../types/api";
import { BallotCard } from "./BallotCard";
import { TurnCard } from "./TurnCard";

function playerColor(agentId: string, players: PlayerView[]): string {
  return players.find((p) => p.agent_id === agentId)?.color ?? tokens.ink[400];
}

function Panel({
  title,
  badge,
  children,
}: {
  title: string;
  badge?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section
      aria-label={title}
      className="overflow-hidden rounded-lg border-2 border-ink-900 bg-paper-0 shadow-chrome-1"
    >
      <div className="flex items-center justify-between border-b-2 border-ink-900 bg-paper-2 px-4 py-3">
        <h3 className="text-base">{title}</h3>
        {badge}
      </div>
      <div className="p-4">{children}</div>
    </section>
  );
}

function Empty({ children }: { children: ReactNode }) {
  return <p className="font-mono text-xs italic text-ink-500">{children}</p>;
}

// Threading depth per turn, following the `reply_to` → `turn_id` chain. Cycle-
// and orphan-safe (an unknown / self parent resolves to depth 0).
function buildDepths(turns: readonly TurnView[]): Map<string, number> {
  const byId = new Map(turns.map((t) => [t.turn_id, t] as const));
  const memo = new Map<string, number>();
  const depthOf = (turn: TurnView, guard: Set<string>): number => {
    const cached = memo.get(turn.turn_id);
    if (cached !== undefined) return cached;
    const parentId = turn.reply_to;
    if (parentId === null || parentId === turn.turn_id || guard.has(turn.turn_id)) {
      memo.set(turn.turn_id, 0);
      return 0;
    }
    const parent = byId.get(parentId);
    if (parent === undefined) {
      memo.set(turn.turn_id, 0);
      return 0;
    }
    guard.add(turn.turn_id);
    const depth = depthOf(parent, guard) + 1;
    memo.set(turn.turn_id, depth);
    return depth;
  };
  for (const turn of turns) depthOf(turn, new Set());
  return memo;
}

// The accusation-chain summary at the top of the transcript panel: one segment
// per turn carrying an accusation (speaker → target), in chain order. Direction
// (who points at whom) uses distrust orange, exactly as the converge render.
function AccusationChainSummary({
  turns,
  players,
}: {
  turns: readonly TurnView[];
  players: PlayerView[];
}) {
  const segments = turns.flatMap((turn) => {
    const accusation = turn.claims.find((c) => c.type === "accusation");
    if (accusation === undefined) return [];
    return [
      {
        key: turn.turn_id,
        speaker: turn.speaker,
        target: accusation.against,
        verb: turn.turn_kind === "reply" ? "redirects" : "accuses",
      },
    ];
  });

  if (segments.length === 0) {
    return null;
  }

  const Disc = ({ agentId }: { agentId: string }) => (
    <span
      className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 border-ink-900 font-mono text-3xs font-bold text-paper-0"
      style={{ backgroundColor: playerColor(agentId, players) }}
    >
      {agentId}
    </span>
  );

  return (
    <div className="mb-3 flex flex-wrap items-center gap-x-3 gap-y-2 border-b border-ink-100 pb-3">
      {segments.map((seg) => (
        <span key={seg.key} className="flex items-center gap-3">
          <Disc agentId={seg.speaker} />
          <span className="flex flex-col items-center">
            {/* Label TEXT is ink for contrast (Task 12.13 sweep); the orange
                ARROW below stays the distrust channel. */}
            <span className="font-mono text-4xs font-bold uppercase tracking-wide text-ink-900">
              {seg.verb}
            </span>
            <svg width="48" height="10" aria-hidden>
              <line x1="2" y1="5" x2="40" y2="5" stroke={tokens.distrust.strong} strokeWidth="2.5" />
              <path d="M40 1 L46 5 L40 9 Z" fill={tokens.distrust.strong} />
            </svg>
          </span>
          <Disc agentId={seg.target} />
        </span>
      ))}
      <span className="ml-auto max-w-[14rem] text-xs leading-snug text-ink-500">
        Accusation edges use <span className="font-semibold text-distrust-strong">distrust orange</span> —
        direction = who points at whom.
      </span>
    </div>
  );
}

// Per-target tally (the DTO ships no precomputed tally): group by target, always
// surface a SKIP bucket, order by descending count with SKIP last.
function tallyBallots(ballots: readonly BallotView[]): { target: string; count: number }[] {
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

// The REAL §4.6 readout from `GateView` (NEVER the mock's "simple majority"):
// plurality + at least one leader ballot ≥ threshold; tie / SKIP-plurality → SKIP.
function gateReadout(gate: GateView): string {
  const conf = gate.leader_max_confidence.toFixed(2);
  const thr = gate.threshold.toFixed(2);
  if (gate.leader === null) {
    return `no plurality leader (tie or SKIP led) → SKIPPED`;
  }
  if (gate.passed) {
    return `plurality leader ${gate.leader}, top ballot ${conf} ≥ ${thr} threshold → EJECTED`;
  }
  return `plurality leader ${gate.leader}, top ballot ${conf} < ${thr} threshold → SKIPPED`;
}

// The dark §4.6 resolution panel: tally, the real gate readout, a role-neutral
// outcome banner, and (Omniscient only) the post-hoc impostor reveal.
function VerdictPanel({
  meeting,
  players,
  omniscient,
}: {
  meeting: MeetingViewDTO;
  players: PlayerView[];
  omniscient: boolean;
}) {
  const tally = tallyBallots(meeting.ballots)
    .filter((row) => row.count > 0 || row.target === "SKIP")
    .map((row) => `${row.target === "SKIP" ? "skip" : row.target} ×${row.count}`)
    .join(" · ");

  const ejected = meeting.outcome === "EJECTED" ? meeting.ejected_player_id : null;
  const ejectedRole =
    ejected === null
      ? null
      : (players.find((p) => p.agent_id === ejected)?.role ?? null);

  return (
    <section className="overflow-hidden rounded-lg border-2 border-ink-900 bg-ink-900 text-paper-0 shadow-chrome-1">
      <div className="flex items-center justify-between border-b border-ink-700 px-4 py-3">
        <h3 className="text-base text-paper-0">Resolution</h3>
        <span className="font-mono text-3xs font-bold text-paper-2">§4.6</span>
      </div>
      <div className="space-y-3 p-4">
        <div className="flex flex-wrap items-baseline gap-2">
          <span className="font-mono text-3xs uppercase tracking-wide text-ink-300">tally</span>
          <span className="font-mono text-sm font-bold text-paper-1">{tally}</span>
        </div>

        <p className="font-mono text-2xs leading-relaxed text-ink-300">
          §4.6 — {gateReadout(meeting.gate)}
        </p>

        {/* Role-neutral outcome banner: never coloured by guilt. */}
        <div className="flex items-center gap-3 rounded-lg border-2 border-ink-700 bg-ink-700/40 px-3 py-3">
          <span
            aria-hidden
            className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full border-2 border-ink-300 bg-ink-500 font-mono text-xs text-paper-0"
          >
            {ejected !== null ? "⏏" : "—"}
          </span>
          <div className="min-w-0">
            <div className="text-base text-paper-0">
              {ejected !== null ? `Ejected — ${ejected}` : "Skipped — no ejection"}
            </div>
            <div className="font-mono text-3xs text-ink-300">
              outcome is role-neutral · guilt is never coloured in
            </div>
          </div>
        </div>

        {/* Post-hoc reveal is role ground truth → Omniscient only (an explicit,
            hideable badge — never a hue; suppressed under As-agent fog). */}
        {omniscient && ejected !== null && ejectedRole !== null && (
          <div className="inline-flex items-center gap-2 rounded-md border border-ink-700 bg-ink-700/40 px-2 py-1 font-mono text-3xs text-paper-2">
            <span aria-hidden>⌖</span>
            post-hoc: {ejected} was {ejectedRole === "IMPOSTOR" ? "impostor" : "crewmate"}
          </div>
        )}
      </div>
    </section>
  );
}

function TranscriptPanel({
  meeting,
  players,
}: {
  meeting: MeetingViewDTO;
  players: PlayerView[];
}) {
  const depths = buildDepths(meeting.turns);
  return (
    <Panel title="Accusation chain & transcript">
      <AccusationChainSummary turns={meeting.turns} players={players} />
      {meeting.turns.length === 0 ? (
        <Empty>No turns in this meeting.</Empty>
      ) : (
        <div className="space-y-2.5">
          {meeting.turns.map((turn) => (
            <TurnCard
              key={turn.turn_id}
              turn={turn}
              players={players}
              contradictions={meeting.contradictions}
              depth={depths.get(turn.turn_id) ?? 0}
              meetingTick={meeting.tick}
            />
          ))}
        </div>
      )}
      <ContradictionsSection
        contradictions={meeting.contradictions}
        turns={meeting.turns}
      />
    </Panel>
  );
}

const TURN_KIND_LABEL: Record<TurnView["turn_kind"], string> = {
  opening: "opening",
  reply: "reply",
  opt_in: "opt-in",
};

// A contradiction event id is `turn:<turn_id>:claim:<i>` / `turn:<turn_id>:obs:<i>`
// (mirrors meetings/transcript.py). Pull the turn id out so the link can name the
// turn it references; greedy `.+` captures the whole id before the final suffix.
function eventTurnId(eventId: string): string | null {
  const match = /^turn:(.+):(?:claim|obs):\d+$/.exec(eventId);
  return match ? match[1]! : null;
}

// Contradiction LINKS: weak = thin dashed ink / strong = bold solid fuchsia (from
// `ContradictionView.weak` via `severity`), each paired with a label so it never
// reads by hue alone (firewall). The link is made explicit by resolving
// `event_a_id` / `event_b_id` to the two TurnCards they connect (speaker + kind),
// so the reader can tell WHICH turns the flag links; it falls back to `subjects`
// when an endpoint can't be resolved. Role-neutral throughout.
function ContradictionsSection({
  contradictions,
  turns,
}: {
  contradictions: readonly ContradictionView[];
  turns: readonly TurnView[];
}) {
  if (contradictions.length === 0) {
    return null;
  }
  const turnById = new Map(turns.map((t) => [t.turn_id, t] as const));
  const endpoint = (eventId: string): string | null => {
    const turn = turnById.get(eventTurnId(eventId) ?? "");
    return turn === undefined
      ? null
      : `${turn.speaker} (${TURN_KIND_LABEL[turn.turn_kind]})`;
  };

  return (
    <div className="mt-4 border-t border-ink-100 pt-3">
      <h4 className="mb-2 font-mono text-2xs uppercase tracking-wide text-ink-500">
        Contradictions ({contradictions.length})
      </h4>
      <ul className="space-y-2">
        {contradictions.map((c) => {
          const strong = c.severity === "strong";
          const a = endpoint(c.event_a_id);
          const b = endpoint(c.event_b_id);
          // Prefer the resolved turn endpoints; fall back to the subject ids.
          const link =
            a !== null && b !== null
              ? `${a} ↔ ${b}`
              : c.subjects.length > 0
                ? c.subjects.join(" ↔ ")
                : null;
          return (
            <li key={c.contradiction_id} className="flex flex-wrap items-center gap-2 text-sm">
              <span
                className={
                  "inline-flex items-center gap-2 rounded-md border px-1.5 py-1 font-mono text-3xs font-bold uppercase tracking-wide " +
                  (strong
                    ? "border-contradiction-strong text-contradiction-strong"
                    : "border-ink-200 text-ink-500")
                }
              >
                <svg width="30" height="8" aria-hidden className="shrink-0">
                  <line
                    x1="1"
                    y1="4"
                    x2="29"
                    y2="4"
                    stroke={strong ? tokens.contradiction : tokens.ink[300]}
                    strokeWidth={strong ? 3 : 1.6}
                    strokeDasharray={strong ? undefined : "4 4"}
                  />
                </svg>
                {strong ? "strong" : "weak"}
              </span>
              {link !== null && (
                <span className="font-mono text-2xs font-bold text-ink-700">{link}</span>
              )}
              <span className="min-w-0 break-words text-ink-900">{c.description}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function BallotsPanel({
  meeting,
  players,
  omniscient,
}: {
  meeting: MeetingViewDTO;
  players: PlayerView[];
  omniscient: boolean;
}) {
  return (
    <Panel title={`Ballots (${meeting.ballots.length})`}>
      {meeting.ballots.length === 0 ? (
        <Empty>No ballots were cast.</Empty>
      ) : (
        <div className="space-y-2.5">
          {meeting.ballots.map((ballot, index) => (
            <BallotCard
              key={`${ballot.voter}#${index}`}
              ballot={ballot}
              players={players}
              omniscient={omniscient}
            />
          ))}
        </div>
      )}
    </Panel>
  );
}

export function MeetingView() {
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const replay = useReplayStore((s) => s.currentReplay);
  const selectMeeting = useReplayStore((s) => s.selectMeeting);
  const perspective = useReplayStore((s) => s.perspective);
  const setHighlightedSighting = useReplayStore((s) => s.setHighlightedSighting);
  const dialogRef = useRef<HTMLDivElement>(null);

  const meeting =
    meetingId !== null && replay !== null
      ? replay.meetings.find((m) => m.meeting_id === meetingId)
      : undefined;
  const isOpen = meetingId !== null && replay !== null && meeting !== undefined;
  const omniscient = perspective.mode === "omniscient";

  // Trap focus inside the dialog while open (aria-modal alone does not constrain
  // focus); focus moves in on open and is restored on close. The guided tour,
  // when open over this, runs its own trap.
  useFocusTrap(dialogRef, isOpen);

  // Clear a stale selection (the replay switched out from under an open overlay)
  // in an effect, never during render.
  useEffect(() => {
    if (meetingId !== null && replay !== null && meeting === undefined) {
      selectMeeting(null);
    }
  }, [meetingId, replay, meeting, selectMeeting]);

  // Close on Escape while open; clear any lingering map highlight on close.
  useEffect(() => {
    if (!isOpen) {
      return;
    }
    const onKeyDown = (event: KeyboardEvent) => {
      // Yield Escape to the guided tour when it is open over this meeting, so a
      // single Escape closes only the tour — not the meeting hydrated behind it.
      if (event.key === "Escape" && !useReplayStore.getState().guidedTourOpen) {
        selectMeeting(null);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [isOpen, selectMeeting]);

  // Drop the cross-highlight when the overlay closes/unmounts AND when the open
  // meeting changes. Keying on `meetingId` matters: a meeting jump / auto-follow
  // can swap the selection (unmounting the hovered TurnCard) without ever firing
  // a mouseleave/blur, which would otherwise strand the previous meeting's
  // sighting ring on the map for a turn no longer in the visible transcript.
  useEffect(() => {
    if (!isOpen) {
      setHighlightedSighting(null);
    }
    return () => {
      setHighlightedSighting(null);
    };
  }, [isOpen, meetingId, setHighlightedSighting]);

  if (!isOpen || meeting === undefined || replay === null) {
    return null;
  }

  const close = () => {
    setHighlightedSighting(null);
    selectMeeting(null);
  };

  return (
    // Task 12.11 overlay coordination: an open meeting MASKS the workspace (a
    // heavy ink scrim — no readable background bleed) while the cross-highlight's
    // bright room still glows through. It is one coordinated layout, not three
    // colliding `fixed` overlays:
    //   • the meeting sits at z-50 with NO phantom left gutter; at xl+ it reserves
    //     a right gutter exactly matching the mind rail (24rem) so the inspector
    //     never overlaps the Ballots column;
    //   • the mind rail (ThoughtStream) sits at z-[55] in that reserved gutter;
    //   • the BeliefMatrix hero steps aside entirely while a meeting is open.
    // The bottom transport (z-70) stays reachable: every overlay reserves the
    // MEASURED `--transport-h` instead of a magic px constant.
    <div
      ref={dialogRef}
      tabIndex={-1}
      role="dialog"
      aria-modal="true"
      aria-label={`Meeting at tick ${meeting.tick}`}
      className="fixed inset-0 z-50 overflow-auto bg-ink-900/80 p-4 outline-none xl:pr-[26rem]"
      style={{ paddingBottom: "var(--transport-h, 16rem)" }}
      onClick={close}
    >
      <div
        className="relative mx-auto my-4 max-w-6xl"
        onClick={(event) => {
          event.stopPropagation();
        }}
      >
        <div className="mb-3 flex items-center justify-between gap-3">
          <span className="rounded-lg border-2 border-ink-900 bg-paper-0 px-3 py-1.5 font-mono text-xs font-bold uppercase tracking-widest text-ink-900 shadow-chrome-1">
            Meeting · t{meeting.tick}
          </span>
          <span className="font-mono text-xs text-ink-600">
            triggered by{" "}
            <span className="font-bold text-ink-900">{meeting.triggered_by}</span> (
            {meeting.trigger_kind})
          </span>
          <button
            type="button"
            aria-label="Close meeting"
            onClick={close}
            className="rounded-md border-2 border-ink-900 bg-paper-0 px-3 py-1.5 text-sm font-semibold text-ink-900 shadow-chrome-1 transition-colors hover:bg-paper-2"
          >
            Close
          </button>
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1.4fr_1fr]">
          <TranscriptPanel meeting={meeting} players={replay.players} />
          <div className="flex flex-col gap-4">
            <BallotsPanel
              meeting={meeting}
              players={replay.players}
              omniscient={omniscient}
            />
            <VerdictPanel
              meeting={meeting}
              players={replay.players}
              omniscient={omniscient}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
