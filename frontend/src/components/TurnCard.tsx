// One turn of the reactive accusation chain, rebuilt in the Playful cream/ink
// style (Task 12.7; design/phase-12/stage-1-design.md §3.4, slice 5; the
// 05-meeting render). A card carrying a speaker chip + tick/kind tag, the
// foregrounded free-text line, the turn's SIGHTINGS as hoverable chips (the
// claim↔map cross-highlight device), and a collapsed-by-default structured
// detail (observations + claims). Contradictions implicating the turn surface
// as role-neutral markers (weak = dashed ink / strong = solid fuchsia — never
// hue-only). Threading: the card is indented by `depth` (computed from the
// `reply_to` chain in MeetingView) and a reply cue names the parent turn.
//
// THE CROSS-HIGHLIGHT (firewall-safe): hovering a "saw p-5 in Reactor" chip sets
// `highlightedSighting = {agentId, roomId}` from the PUBLIC referent the
// transcript already names; `MapView` lights that room ONLY when the current
// perspective already shows it, so the hover never reveals a fogged position.

import {
  dedupeContradictions,
  findContradictions,
  turnClaimEventId,
  turnObsEventId,
} from "../lib/contradictions";
import { useReplayStore } from "../store/replayStore";
import { tokens } from "../tokens";
import type {
  ContradictionView,
  PlayerView,
  SawPlayerView,
  TurnView,
} from "../types/api";
import { ClaimLine } from "../ui/ClaimLine";
import { ObservationLine } from "../ui/ObservationLine";

interface TurnCardProps {
  turn: TurnView;
  players: PlayerView[];
  contradictions: readonly ContradictionView[];
  // Threading depth from the `reply_to` chain (0 = opening / unthreaded).
  depth: number;
  // The meeting tick, shown in the per-turn tag (the turn carries no own tick).
  meetingTick: number;
}

const TURN_KIND_LABELS: Record<TurnView["turn_kind"], string> = {
  opening: "opening",
  reply: "reply",
  opt_in: "opt-in",
};

const INDENT_PX = 22;
const MAX_DEPTH = 6;

function playerColor(agentId: string, players: PlayerView[]): string {
  return players.find((p) => p.agent_id === agentId)?.color ?? tokens.ink[400];
}

function playerName(agentId: string, players: PlayerView[]): string {
  return players.find((p) => p.agent_id === agentId)?.display_name ?? agentId;
}

// A small filled identity disc with the agent id — the Playful speaker token.
function SpeakerDisc({
  agentId,
  players,
}: {
  agentId: string;
  players: PlayerView[];
}) {
  return (
    <span
      aria-hidden
      className="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 border-ink-900 font-mono text-4xs font-bold text-paper-0"
      style={{ backgroundColor: playerColor(agentId, players) }}
    >
      {agentId.replace(/^p-/, "")}
    </span>
  );
}

function SpeakerChip({
  agentId,
  players,
}: {
  agentId: string;
  players: PlayerView[];
}) {
  return (
    <span className="inline-flex min-w-0 items-center gap-2">
      <SpeakerDisc agentId={agentId} players={players} />
      <span className="font-mono text-sm font-bold text-ink-900">{agentId}</span>
      <span className="min-w-0 truncate text-xs text-ink-500">
        {playerName(agentId, players)}
      </span>
    </span>
  );
}

// Role-neutral contradiction marker: weak = thin dashed ink, strong = bold solid
// fuchsia (the reserved contradiction channel). Paired with a label so it never
// reads by hue alone (firewall).
function ContradictionMarker({
  contradiction,
}: {
  contradiction: ContradictionView;
}) {
  const strong = contradiction.severity === "strong";
  return (
    <span
      title={contradiction.description}
      className={
        "inline-flex items-center gap-2 rounded-md border px-1.5 py-1 font-mono text-3xs font-bold uppercase tracking-wide " +
        (strong
          ? "border-contradiction-strong text-contradiction-strong"
          : "border-ink-200 text-ink-500")
      }
    >
      <svg width="22" height="8" aria-hidden className="shrink-0">
        <line
          x1="1"
          y1="4"
          x2="21"
          y2="4"
          stroke={strong ? tokens.contradiction : tokens.ink[300]}
          strokeWidth={strong ? 3 : 1.6}
          strokeDasharray={strong ? undefined : "4 4"}
        />
      </svg>
      {strong ? "strong" : "weak"}
    </span>
  );
}

// The eye glyph that marks a recorded sighting (matches the converge legend).
function EyeGlyph() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" aria-hidden className="shrink-0">
      <path
        d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.2"
      />
      <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" strokeWidth="2.2" />
    </svg>
  );
}

// One hoverable sighting chip — the cross-highlight trigger. Hover/focus lights
// the named room + agent on the map (public referent; firewall-safe). Keyboard
// accessible via focus/blur so the device is not mouse-only.
function SightingChip({
  sighting,
  players,
}: {
  sighting: SawPlayerView;
  players: PlayerView[];
}) {
  const setHighlightedSighting = useReplayStore((s) => s.setHighlightedSighting);
  const light = () => {
    setHighlightedSighting({ agentId: sighting.subject, roomId: sighting.room });
  };
  const clear = () => {
    setHighlightedSighting(null);
  };
  return (
    <button
      type="button"
      onMouseEnter={light}
      onMouseLeave={clear}
      onFocus={light}
      onBlur={clear}
      title="Hover to light this sighting on the map"
      className="inline-flex items-center gap-2 rounded-md border border-ink-200 bg-paper-2 px-2 py-1 text-xs text-ink-700 transition-colors hover:border-ink-900 hover:bg-paper-3 focus:border-ink-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-ink-900"
    >
      <span className="text-ink-500">
        <EyeGlyph />
      </span>
      <span className="font-mono">
        saw <span className="font-bold text-ink-900">{sighting.subject}</span> in{" "}
        <span className="font-bold text-ink-900">{sighting.room}</span>
        <span className="text-ink-500"> · t{sighting.tick}</span>
      </span>
    </button>
  );
}

export function TurnCard({
  turn,
  players,
  contradictions,
  depth,
  meetingTick,
}: TurnCardProps) {
  const observations = turn.observations.map((obs, index) => ({
    obs,
    contras: findContradictions(turnObsEventId(turn, index), contradictions),
  }));
  const claims = turn.claims.map((claim, index) => ({
    claim,
    contras: findContradictions(turnClaimEventId(turn, index), contradictions),
  }));
  const flagged = dedupeContradictions([
    ...observations.flatMap((o) => o.contras),
    ...claims.flatMap((c) => c.contras),
  ]);
  const detailCount = observations.length + claims.length;

  // The sightings (saw_player observations) are the cross-highlight targets, so
  // they are surfaced as always-visible chips rather than hidden in the detail.
  const sightings = turn.observations.filter(
    (obs): obs is SawPlayerView => obs.type === "saw_player",
  );

  // The chain's accusation target (first accusation claim), shown as a chip.
  const accusation = turn.claims.find((claim) => claim.type === "accusation");
  const target = accusation?.against ?? null;

  // A flagged turn gets a fuchsia left accent; otherwise the speaker's identity
  // colour (identity ≠ guilt — it only ties the card to its speaker).
  const accent = flagged.length > 0 ? tokens.contradiction : playerColor(turn.speaker, players);
  const indent = Math.min(depth, MAX_DEPTH) * INDENT_PX;

  return (
    <article
      style={{ marginLeft: indent, borderLeftColor: accent }}
      className="rounded-xl border border-ink-100 border-l-4 bg-paper-1 p-3 shadow-data"
    >
      <header className="mb-2 flex flex-wrap items-center gap-x-3 gap-y-1">
        <SpeakerChip agentId={turn.speaker} players={players} />
        <span className="font-mono text-3xs text-ink-500">
          t{meetingTick} · {TURN_KIND_LABELS[turn.turn_kind]}
        </span>
        {turn.fabricated_opening && (
          // Role-neutral chip for an emergency opening whose fabricated found_body
          // was stripped (the dev-jargon marker is dropped server-side). Ink/paper
          // only — no reserved hue — paired with the label (firewall: not hue-only).
          <span
            title="This emergency opening fabricated a found body; it was stripped (DESIGN.md §5.2)."
            className="inline-flex items-center rounded-md border border-ink-300 bg-paper-2 px-1.5 py-1 font-mono text-4xs font-bold uppercase tracking-wide text-ink-700"
          >
            fabricated
          </span>
        )}
        {target !== null && (
          // distrust-strong is the channel for the accusation EDGE (the arrow);
          // the label text stays ink-900 for contrast (Task 12.13 contrast sweep).
          <span className="inline-flex items-center gap-1 font-mono text-2xs text-ink-900">
            <span aria-hidden className="text-distrust-strong">
              →
            </span>
            accuses
            <span className="font-bold">{target}</span>
          </span>
        )}
        {turn.reply_to !== null && (
          <span className="inline-flex items-center gap-1 font-mono text-3xs text-ink-500">
            <span aria-hidden>↳</span> reply
          </span>
        )}
        <span className="ml-auto flex flex-wrap items-center gap-2">
          {flagged.map((c) => (
            <ContradictionMarker key={c.contradiction_id} contradiction={c} />
          ))}
        </span>
      </header>

      <p className="whitespace-pre-wrap break-words text-[15px] leading-relaxed text-ink-900">
        {turn.free_text}
      </p>

      {sightings.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-2">
          {sightings.map((sighting, index) => (
            <SightingChip
              key={`sighting-${index}`}
              sighting={sighting}
              players={players}
            />
          ))}
        </div>
      )}

      {detailCount > 0 && (
        <details className="mt-2 text-sm text-ink-700">
          <summary className="cursor-pointer select-none font-mono text-2xs text-ink-500">
            structured detail ({observations.length} observation
            {observations.length === 1 ? "" : "s"}, {claims.length} claim
            {claims.length === 1 ? "" : "s"})
          </summary>
          <div className="mt-2 space-y-2">
            {observations.length > 0 && (
              <ul className="space-y-1">
                {observations.map(({ obs, contras }, index) => (
                  <li
                    key={`obs-${index}`}
                    className="flex flex-wrap items-center gap-2 text-ink-700"
                  >
                    <span className="text-ink-500">•</span>
                    <ObservationLine obs={obs} />
                    {contras.map((c) => (
                      <ContradictionMarker key={c.contradiction_id} contradiction={c} />
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
                    className="flex flex-wrap items-center gap-2 text-ink-700"
                  >
                    <span className="text-ink-500">•</span>
                    <ClaimLine claim={claim} />
                    {contras.map((c) => (
                      <ContradictionMarker key={c.contradiction_id} contradiction={c} />
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
