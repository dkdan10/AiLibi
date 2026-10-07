// HighlightCard (Task 12.9; design/phase-12/stage-1-design.md §3.1, slice 7; the
// firewall rules in design/phase-12/claude-design-brief.md).
//
// PRESENTATIONAL ONLY: one card per game, built from the game's entry in the
// set's game-shape profile joined to its replay metadata. Clicking it calls
// `onOpen(gameId)` — the connected `<ReplayPicker/>` turns that into "load this
// replay + open the workspace".
//
// It shows the seed, a role-neutral outcome tag, the shelves the game sits on as
// chips, the eyewitness chip on the meeting it marks, a tripwire's plain label,
// a facet line and a small timeline of kills and meetings. There is no score and
// no rank: a card describes its game and orders nothing.
//
// Firewall (BINDING): the chips and the timeline are role-neutral ink — they
// never reuse the suspicion (amber) / trust (blue) / kill (red) channels, and the
// winner is a neutral label, never a guilt hue. A set may ship no profile at all,
// and the four-player set holds games with no meeting, so the no-profile and
// zero-meeting states are first-class here.
//
// REVEAL GATING (Task 19.10): this grid renders BEFORE anything is opened, so it
// is the corpus's biggest pre-play spoiler surface. The card takes a `reveal`
// prop and, while it is false, emits NO outcome-derived DOM: the winner chip
// reads "Outcome hidden", and no reveal-only shelf, ending, distance, sabotage or
// ejection annotation renders. The facets shown before the reveal describe
// structure the viewer already shows elsewhere (the length, the meetings, the
// kills).

import { PROFILE_COPY, fmt } from "../lib/copy";
import type {
  GameFacetsView,
  ReplayMetadataView,
  RevealFacetsView,
  Winner,
} from "../types/api";

/** One game's entry in the set's game-shape profile, as a card shows it. */
export interface CardProfile {
  readonly facets: GameFacetsView;
  /** The reveal facets, or `null` when the profile serves none for the game. */
  readonly revealFacets: RevealFacetsView | null;
  /** The shelves before the reveal the game sits on, in the profile's order. */
  readonly shelves: readonly string[];
  /** The reveal-only shelves the game sits on, the pair's halves included. */
  readonly revealShelves: readonly string[];
  /** The meeting indexes the eyewitness chip marks. */
  readonly eyewitness: readonly number[];
}

/** One card's data: the game's profile entry (when served) and its metadata. */
export interface HighlightCardData {
  /** Stable React key. */
  readonly key: string;
  /** `headless-seed-{seed}` — what `onOpen` loads. */
  readonly gameId: string;
  readonly seed: number;
  /** From replay metadata; role-neutral display only. `null` when unknown. */
  readonly winner: Winner | null;
  readonly completionStatus?: ReplayMetadataView["completion_status"];
  readonly totalTicks: number | null;
  /** `null` = the set ships no current profile. */
  readonly profile: CardProfile | null;
}

/** A shelf's title by the name the served profile gives it. */
export function shelfTitle(name: string): string {
  const entry = (PROFILE_COPY.shelves as Readonly<Record<string, { title: string }>>)[
    name
  ];
  if (entry === undefined) {
    throw new Error(`the game-shape profile names a shelf this build has no words for: ${name}`);
  }
  return entry.title;
}

function winnerLabel(
  winner: Winner | null,
  completionStatus: ReplayMetadataView["completion_status"],
): string {
  if (winner === "CREWMATES") return "Crew win";
  if (winner === "IMPOSTORS") return "Impostor win";
  if (completionStatus === "aborted") return "Aborted";
  if (completionStatus === "tick_limited") return "Tick limit";
  return "Unfinished";
}

// The reveal control withholds both winning teams and recorded stop reasons.
// Older bundles omit stop classification, so a missing winner stays unfinished.
function WinnerTag({
  winner,
  completionStatus,
  hidden,
}: {
  winner: Winner | null;
  completionStatus: ReplayMetadataView["completion_status"];
  hidden: boolean;
}) {
  const glyph = hidden
    ? "·"
    : winner === "IMPOSTORS"
      ? "◆"
      : winner === "CREWMATES"
        ? "▲"
        : "·";
  return (
    <span
      title={hidden ? "Hidden until you reveal outcomes" : undefined}
      className="inline-flex items-center gap-1 rounded-pill border border-ink-300 px-2 py-0.5 font-mono text-3xs text-ink-600"
    >
      <span aria-hidden>{glyph}</span>
      {hidden ? "Outcome hidden" : winnerLabel(winner, completionStatus)}
    </span>
  );
}

function Chip({ text, revealOnly }: { text: string; revealOnly?: boolean }) {
  return (
    <li
      className={
        "rounded-pill border-2 px-2 py-0.5 font-mono text-3xs font-medium text-ink-900 " +
        (revealOnly ? "border-dashed border-ink-500 bg-paper-1" : "border-ink-900 bg-paper-2")
      }
    >
      {text}
    </li>
  );
}

function count(template: string, value: number): string {
  return fmt(template, { count: String(value) });
}

// The structure line: length, meetings by what opened them, kills and the wave,
// bodies never found. Every value is a plain count of the recording.
function FacetLine({ facets }: { facets: GameFacetsView }) {
  const reported = facets.meetings.filter((meeting) => meeting.trigger === "report").length;
  const wave = facets.kills.filter((kill) => kill.in_wave).length;
  const parts = [
    fmt(PROFILE_COPY.facets.ticks, { ticks: String(facets.ticks) }),
    facets.meetings.length === 0
      ? PROFILE_COPY.facets.noMeetings
      : fmt(PROFILE_COPY.facets.meetings, {
          count: String(facets.meetings.length),
          reported: String(reported),
          called: String(facets.meetings.length - reported),
        }),
    facets.kills.length === 0
      ? PROFILE_COPY.facets.noKills
      : fmt(PROFILE_COPY.facets.kills, {
          count: String(facets.kills.length),
          wave: String(wave),
        }),
    count(PROFILE_COPY.facets.bodiesNeverFound, facets.bodies_never_found),
  ];
  return <p className="font-mono text-xs text-ink-700">{parts.join(" · ")}</p>;
}

// A tick-by-tick strip: a mark per kill (a wave kill hollow) and per meeting.
// Neutral ink only; positions are the ticks themselves over the game's length.
function Timeline({ facets }: { facets: GameFacetsView }) {
  const length = Math.max(facets.ticks, 1);
  const left = (tick: number) => `${Math.min(100, (tick / length) * 100)}%`;
  return (
    <div
      role="img"
      aria-label={PROFILE_COPY.facets.timeline}
      className="relative h-4 w-full rounded-sm bg-paper-3 shadow-data"
    >
      {facets.meetings.map((meeting) => (
        <span
          key={`m-${meeting.index}`}
          title={fmt(PROFILE_COPY.facets.timelineMeeting, {
            meeting: String(meeting.index + 1),
            tick: String(meeting.tick),
          })}
          className="absolute top-0 h-4 w-0.5 bg-ink-900"
          style={{ left: left(meeting.tick) }}
        />
      ))}
      {facets.kills.map((kill, index) => (
        <span
          key={`k-${index}-${kill.tick}`}
          title={fmt(
            kill.in_wave ? PROFILE_COPY.facets.timelineWaveKill : PROFILE_COPY.facets.timelineKill,
            { tick: String(kill.tick) },
          )}
          className={
            "absolute top-1 h-2 w-2 -translate-x-1 rounded-full border-2 border-ink-700 " +
            (kill.in_wave ? "bg-paper-0" : "bg-ink-700")
          }
          style={{ left: left(kill.tick) }}
        />
      ))}
    </div>
  );
}

function endingWords(ending: string): string {
  const words = (PROFILE_COPY.revealFacets.endings as Readonly<Record<string, string>>)[ending];
  if (words === undefined) {
    throw new Error(`the game-shape profile names an ending this build has no words for: ${ending}`);
  }
  return words;
}

/** A tripwire's plain label at the meeting it trips, counted from one. */
export function tripwireLabel(tripwire: string, meeting: number): string {
  const template = (PROFILE_COPY.tripwires as Readonly<Record<string, string>>)[tripwire];
  if (template === undefined) {
    throw new Error(`the game-shape profile names a tripwire this build has no words for: ${tripwire}`);
  }
  return fmt(template, { meeting: String(meeting + 1) });
}

// Behind the reveal: the ending, the losing side's distance, the sabotages in
// play and each ejection's annotation.
function RevealFacetLines({ facets }: { facets: RevealFacetsView }) {
  const lines = [fmt(PROFILE_COPY.revealFacets.ending, { ending: endingWords(facets.ending) })];
  if (facets.distance !== null) {
    lines.push(
      fmt(
        facets.distance.counts === "tasks_left"
          ? PROFILE_COPY.revealFacets.tasksLeft
          : PROFILE_COPY.revealFacets.killsShort,
        { steps: String(facets.distance.steps), start: String(facets.distance.start) },
      ),
    );
  }
  lines.push(
    fmt(PROFILE_COPY.revealFacets.tasks, {
      done: String(facets.tasks_done),
      assigned: String(facets.tasks_assigned),
    }),
  );
  lines.push(
    ...facets.sabotage_starts.map((tick) =>
      fmt(PROFILE_COPY.revealFacets.sabotage, { tick: String(tick) }),
    ),
  );
  lines.push(
    ...facets.ejections.map((ejection) =>
      fmt(
        ejection.right
          ? PROFILE_COPY.revealFacets.ejectionRight
          : PROFILE_COPY.revealFacets.ejectionWrong,
        { meeting: String(ejection.meeting + 1) },
      ),
    ),
  );
  return (
    <ul className="flex flex-col gap-0.5 font-mono text-3xs text-ink-600">
      {lines.map((line) => (
        <li key={line}>{line}</li>
      ))}
    </ul>
  );
}

interface HighlightCardProps {
  data: HighlightCardData;
  onOpen: (gameId: string) => void;
  // Outcome reveal (Task 19.10). Required, not optional: an omitted spoiler gate
  // must be a compile error, never a silent default to "show everything".
  reveal: boolean;
}

export function HighlightCard({ data, onOpen, reveal }: HighlightCardProps) {
  const { profile } = data;
  return (
    <button
      type="button"
      onClick={() => {
        onOpen(data.gameId);
      }}
      aria-label={`Open replay seed ${data.seed}`}
      className="flex w-full flex-col gap-3 rounded-lg border-2 border-ink-900 bg-paper-0 p-4 text-left shadow-chrome-1 transition-transform hover:-translate-y-0.5 hover:shadow-chrome-2 focus-visible:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink-900"
    >
      <div className="flex items-center justify-between gap-2">
        <span className="font-mono text-xs font-semibold text-ink-900">
          seed {data.seed}
        </span>
        <WinnerTag
          winner={data.winner}
          completionStatus={data.completionStatus}
          hidden={!reveal}
        />
      </div>

      {profile === null ? (
        data.totalTicks !== null && (
          <span className="font-mono text-[11px] text-ink-500">
            {fmt(PROFILE_COPY.facets.ticks, { ticks: String(data.totalTicks) })}
          </span>
        )
      ) : (
        <>
          {profile.facets.tripped.map((label) => (
            <p
              key={`${label.tripwire}-${label.meeting}`}
              className="rounded-md border border-dashed border-ink-500 bg-paper-1 px-2 py-1 text-xs text-ink-700"
            >
              {tripwireLabel(label.tripwire, label.meeting)}
            </p>
          ))}
          {(profile.shelves.length > 0 ||
            profile.eyewitness.length > 0 ||
            (reveal && profile.revealShelves.length > 0)) && (
            <ul className="flex flex-wrap gap-1.5" aria-label="Shelves this game sits on">
              {profile.shelves.map((name) => (
                <Chip key={name} text={shelfTitle(name)} />
              ))}
              {profile.eyewitness.map((meeting) => (
                <Chip
                  key={`eye-${meeting}`}
                  text={fmt(PROFILE_COPY.chip.atMeeting, { meeting: String(meeting + 1) })}
                />
              ))}
              {reveal &&
                profile.revealShelves.map((name) => (
                  <Chip key={name} text={shelfTitle(name)} revealOnly />
                ))}
            </ul>
          )}
          <FacetLine facets={profile.facets} />
          <Timeline facets={profile.facets} />
          {reveal && profile.revealFacets !== null && (
            <RevealFacetLines facets={profile.revealFacets} />
          )}
        </>
      )}
    </button>
  );
}
