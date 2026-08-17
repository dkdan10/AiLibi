// The app shell (Task 12.4; design/phase-12/stage-1-design.md §2.1, §2.3, §4).
// Two levels of PRE-DECLARED mount points so every Wave-B surface plugs in
// WITHOUT ever editing this file (the parallel-dispatch guarantee):
//
//   (a) a top-level view container — `view` lives in the store and is URL-synced
//       (no router) — for Replays + Highlights (→ 12.9), Tournament (→ 12.10),
//       and the Replay Workspace.
//   (b) within the workspace, named slots per §2.3. Each slot mounts an existing
//       component at its STABLE path; the Wave-B PR that owns a surface rewrites
//       that component (its own scope) and the shell picks it up automatically.
//
// SLOT ↔ SURFACE CHECKLIST (every 12.5–12.10 + transport/advantage/timeline has
// a mount; none requires an App.tsx edit):
//   • Replays route          → <ReplayPicker/>        (12.9 — browser)
//   • Highlights route        → <ReplayPicker/>        (12.9 — view-aware reel)
//   • Tournament route        → <TournamentDashboard/> (12.10)
//   • Workspace · perspective → <PerspectiveBanner/>   (12.4 shell; 12.5 switcher
//                                                        lands inside its stage)
//   • Workspace · roster      → <RosterRail/>          (12.4 shell, hand-coded)
//   • Workspace · stage(map)  → <MapView/>             (12.5)
//   • Workspace · stage(meet) → <MeetingView/>         (12.7 — map↔meeting morph)
//   • Workspace · mind        → <ThoughtStream/>       (12.8)
//   • Workspace · belief      → <BeliefMatrix/>        (12.6 — overlay/full toggle)
//   • Workspace · advantage   → <AdvantageGraph/>      (12.4)
//   • Workspace · timeline    → <EventTimeline/>       (12.4)
//   • Workspace · transport   → <ReplayControls/>      (12.4)
//
// `currentTick` stays the array index (the frozen store contract every mounted
// surface reads); the index↔engine-tick mapping lives once in `lib/playback`.
//
// Task 12.11 (design §8, §9, slice 9) owned the shell-level polish and was, in
// Phase 12, the one task that legitimately edited App.tsx. It added: lazy route
// boundaries for the Pixi map / Dashboard / browser (the code-split that kills
// the 859 kB chunk); a responsive layout where the rails collapse to drawers
// while the map + transport stay the irreducible core; keyboard-operable
// transport shortcuts; the first-run GuidedTour mount; and a measured
// `--transport-h` so the fixed overlays reserve exactly the transport's height
// (no magic numbers, no bleed).
//
// Phase 19 re-opens the file deliberately (tasks/phase-19.md lists App.tsx under
// 19.10 → 19.17): Task 19.10 adds the playback-coherence surfaces — the header's
// outcome gate, the roster's pre/post-vote labeling, the meeting pause bar in
// the transport region, and the finale card overlay. Task 19.17 then MOUNTS the
// two additive surfaces at the tail of that chain — <CostChips/> in the stage's
// pill row and <EventTicker/> under it. Mounting only: both are self-contained
// sections in the ordinary document flow, so they claim no z-index, no
// `--transport-h`, and nothing 19.10's pause/finale flow depends on.

import { Suspense, lazy, useEffect, useRef, useState } from "react";
import type { RefObject } from "react";

import { BeliefMatrix } from "./components/BeliefMatrix";
import { CostChips } from "./components/CostChips";
import { EventTicker } from "./components/EventTicker";
import { GuidedTour, openGuidedTour } from "./components/GuidedTour";
import { MeetingPill } from "./components/MeetingPill";
import { MeetingView } from "./components/MeetingView";
import {
  AdvantageGraph,
  EventTimeline,
  ReplayControls,
} from "./components/ReplayControls";
import { ThoughtStream } from "./components/ThoughtStream";
import { usePlayback, usePlaybackEngine } from "./hooks/usePlayback";
import { OMNISCIENT, type ViewId } from "./lib/playback";
import { useReplayStore } from "./store/replayStore";
import type { FinaleAgentRecapView, FinaleEventView } from "./types/api";
import { PlayerSwatch } from "./ui/PlayerSwatch";
import { SectionLabel } from "./ui/SectionLabel";

// Route-level + Pixi-heavy surfaces are lazy-loaded (Task 12.11; design §9) so
// the initial download is just the shell, not one 859 kB monolith. MapView pulls
// in ALL of Pixi, so deferring it keeps the canvas vendor off the critical path
// until a replay opens; the Dashboard and the replay browser / Highlights reel
// load on their own routes.
const MapView = lazy(() =>
  import("./components/MapView").then((m) => ({ default: m.MapView })),
);
const TournamentDashboard = lazy(() =>
  import("./components/TournamentDashboard").then((m) => ({
    default: m.TournamentDashboard,
  })),
);
const ReplayPicker = lazy(() =>
  import("./components/ReplayPicker").then((m) => ({ default: m.ReplayPicker })),
);

// The single side-effecting playback driver (timer + auto-follow + URL sync),
// isolated in a render-null leaf so its store subscriptions don't re-render the
// whole shell on every tick.
function PlaybackEngine() {
  usePlaybackEngine();
  return null;
}

// A calm route-transition placeholder for the lazy boundaries above.
function RouteFallback() {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex items-center gap-3 rounded-lg border-2 border-ink-900 bg-paper-0 px-4 py-3 font-mono text-sm text-ink-700 shadow-chrome-1"
    >
      <span
        aria-hidden
        className="motion-safe:animate-spin inline-block h-4 w-4 rounded-full border-2 border-ink-200 border-t-ink-700"
      />
      Loading…
    </div>
  );
}

// Keyboard-operable transport (Task 12.11 a11y; design §8). Mounted only in the
// workspace so the shortcuts are live where a replay is loaded. It reads the
// `usePlayback` hook (stable actions + fresh state via a ref) WITHOUT editing the
// hook or the transport component — the on-screen buttons remain the discoverable
// surface; these are the keyboard accelerators (scrub / step / play / jump). A
// form control (the scrubber, the set <select>) keeps its own key handling, and a
// browser modifier chord is never hijacked.
function KeyboardTransport() {
  const playback = usePlayback();
  const playbackRef = useRef(playback);
  playbackRef.current = playback;
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.ctrlKey || event.metaKey || event.altKey) {
        return;
      }
      // The guided-tour modal owns the keyboard while it is open — don't let the
      // transport shortcuts drive the replay behind it (focus may rest on the
      // dialog container, which the form/activatable checks below don't cover).
      if (useReplayStore.getState().guidedTourOpen) {
        return;
      }
      const target = event.target as HTMLElement | null;
      const tag = target?.tagName;
      if (
        tag === "INPUT" ||
        tag === "TEXTAREA" ||
        tag === "SELECT" ||
        target?.isContentEditable === true
      ) {
        return;
      }
      // Don't fire transport accelerators while focus is on an interactive widget
      // OUTSIDE the transport: Space/Enter activate a button, and arrows are the
      // navigation keys for a tablist (the Mind inspector tabs), so the global
      // shortcuts must not seek/toggle underneath a focused control. The transport
      // region is the exception — its own controls keep the accelerators live —
      // except Space, which must still trigger a focused button's native action
      // rather than double-firing play/pause.
      const role = target?.getAttribute("role");
      const isActivatable =
        tag === "BUTTON" ||
        tag === "A" ||
        tag === "SUMMARY" ||
        role === "button" ||
        role === "tab" ||
        role === "link";
      if (isActivatable) {
        const inTransport = target?.closest("[data-transport-region]") != null;
        if (!inTransport || event.key === " ") {
          return;
        }
      }
      const p = playbackRef.current;
      if (!p.hasReplay) {
        return;
      }
      switch (event.key) {
        case " ":
        case "k":
          p.togglePlay();
          break;
        case "ArrowLeft":
          p.stepBy(event.shiftKey ? -10 : -1);
          break;
        case "ArrowRight":
          p.stepBy(event.shiftKey ? 10 : 1);
          break;
        case ",":
          p.jumpToEvent(-1);
          break;
        case ".":
          p.jumpToEvent(1);
          break;
        case "[":
          p.jumpToMeeting(-1);
          break;
        case "]":
          p.jumpToMeeting(1);
          break;
        case "n":
          p.nextKeyMoment();
          break;
        case "Home":
          p.seekToIndex(0);
          break;
        case "End":
          p.seekToIndex(p.lastIndex);
          break;
        default:
          return;
      }
      event.preventDefault();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
    };
  }, []);
  return null;
}

const TABS: ReadonlyArray<{ id: Exclude<ViewId, "workspace">; label: string }> = [
  { id: "replays", label: "Replays" },
  { id: "highlights", label: "Highlights" },
  { id: "tournament", label: "Tournament" },
];

function TopNav() {
  const view = useReplayStore((s) => s.view);
  const setView = useReplayStore((s) => s.setView);
  // The workspace is reached by selecting a replay, so it keeps the Replays tab
  // lit as its parent route.
  const active: ViewId = view === "workspace" ? "replays" : view;
  return (
    <nav className="flex flex-wrap items-center gap-2" aria-label="Spectator views">
      {TABS.map((tab) => {
        const isActive = tab.id === active;
        return (
          <button
            key={tab.id}
            type="button"
            aria-current={isActive ? "page" : undefined}
            onClick={() => {
              setView(tab.id);
            }}
            className={
              "rounded-md border-2 border-ink-900 px-4 py-2 text-sm font-semibold transition-colors " +
              (isActive
                ? "bg-ink-900 text-paper-0 shadow-chrome-1"
                : "bg-paper-0 text-ink-900 hover:bg-paper-2")
            }
          >
            {tab.label}
          </button>
        );
      })}
      {/* Re-open the first-run guided tour at will (design §8 first-run). */}
      <button
        type="button"
        onClick={() => {
          openGuidedTour();
        }}
        title="Guided tour — perspective switcher + the two-truth grammar"
        aria-label="Open the guided tour"
        className="rounded-md border-2 border-ink-900 bg-paper-0 px-3 py-2 text-sm font-semibold text-ink-900 transition-colors hover:bg-paper-2"
      >
        <span aria-hidden>?</span> Tour
      </button>
    </nav>
  );
}

// Dominant mode banner (§2.3): seed/roster context + the persistent perspective
// indicator. The basic Omniscient/As-agent picker here keeps `perspective`
// exercisable and URL-round-trippable now; 12.5 lands the richer switcher inside
// the stage's map toolbar (this banner is the shell-level mode indicator).
function PerspectiveBanner() {
  const replay = useReplayStore((s) => s.currentReplay);
  const perspective = useReplayStore((s) => s.perspective);
  const setPerspective = useReplayStore((s) => s.setPerspective);
  const setView = useReplayStore((s) => s.setView);
  const setBeliefOpen = useReplayStore((s) => s.setBeliefOpen);
  const selectedMeetingId = useReplayStore((s) => s.selectedMeetingId);
  // Outcome reveal (Task 19.10) — a SECOND, independent axis from `perspective`
  // above. Perspective governs what the CURRENT FRAME may show (the fog);
  // reveal governs whether the FUTURE — how this game ends — may reach the DOM.
  // Nothing here couples them: entering fog does not hide the outcome, and
  // revealing the outcome does not change who you are watching as.
  const revealOutcome = useReplayStore((s) => s.revealOutcome);

  const meta = replay?.metadata ?? null;
  const meetingCount = meta?.meeting_count ?? 0;
  // This shell banner is the read-only PERSPECTIVE INDICATOR; the interactive
  // As-agent switcher lives in the stage's map toolbar (MapToolbar, 12.5). The
  // panels now gate every secret to Omniscient-or-self
  // (MindInspector / MeetingView / BeliefMatrix), so fog is safe to enter — the
  // earlier "entering here would leak" rationale is obsolete. We keep a one-way
  // "Exit fog" as a convenience so the shell always offers a quick return to
  // Omniscient.
  const inFog = perspective.mode === "agent";

  return (
    <header className="flex flex-wrap items-center justify-between gap-3 rounded-lg border-2 border-ink-900 bg-paper-0 px-4 py-3 shadow-chrome-1">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={() => {
            setView("replays");
          }}
          className="rounded-md border-2 border-ink-900 bg-paper-0 px-3 py-1 text-sm font-medium text-ink-900 hover:bg-paper-2"
        >
          ‹ Replays
        </button>
        {/* The shell's context line USED to print the winner from frame zero —
            the single loudest spoiler in the app, shown before a tick had played
            (Task 19.10). Unrevealed it now says so in words: no winner value
            reaches the DOM at all, not even as a hidden attribute. There is
            deliberately NO reveal toggle here — this banner is a read-only
            indicator (the same reason the As-agent switcher lives in the map
            toolbar, not here), and the reveal affordance belongs where the
            question is actually asked: on the finale card at the end of the
            replay, and on the browser's filter bar. Two toggles for one state
            would just make it ambiguous which one is authoritative. */}
        <span className="font-mono text-sm text-ink-700">
          {meta === null
            ? "No replay selected"
            : revealOutcome
              ? `seed ${meta.seed} · ${replay?.players.length ?? 0}p · ${meta.winner ?? "—"}`
              : `seed ${meta.seed} · ${replay?.players.length ?? 0}p · outcome hidden`}
        </span>
      </div>
      <div className="flex items-center gap-2">
        <span className="font-mono text-3xs uppercase tracking-wide text-ink-500">
          Perspective
        </span>
        <span
          aria-label={`Perspective: ${inFog ? `As ${perspective.agentId}` : "Omniscient"}`}
          className="rounded-md border-2 border-ink-900 bg-paper-0 px-2 py-1 font-mono text-sm text-ink-900"
        >
          {inFog ? `As ${perspective.agentId} · fog` : "Omniscient"}
        </span>
        {inFog && (
          <button
            type="button"
            onClick={() => {
              setPerspective(OMNISCIENT);
            }}
            title="Return to the Omniscient view (enter As-agent from the map toolbar)"
            className="rounded-md border-2 border-ink-900 bg-paper-0 px-3 py-1 text-sm font-medium text-ink-900 hover:bg-paper-2"
          >
            Exit fog
          </button>
        )}
        {/* Belief × Truth launcher — re-anchored into chrome (Task 12.13): a tab
            beside the perspective toggle, never floating over the Reactor cell.
            Firewall: the matrix is an Omniscient cross-agent overview, so the
            launcher hides in fog and while a meeting owns the screen (matching
            BeliefMatrix's gates). Greyed with a tooltip when the game has no
            meetings (nothing to compare). */}
        {!inFog && selectedMeetingId === null && (
          <>
            <span aria-hidden className="mx-1 h-5 w-px bg-ink-200" />
            <button
              type="button"
              disabled={meetingCount === 0}
              onClick={() => {
                setBeliefOpen(true);
              }}
              aria-label="Open the Belief × Truth matrix"
              title={
                meetingCount === 0
                  ? "No meetings in this game — no beliefs to compare against ground truth"
                  : "Belief × Truth — who suspects whom, vs ground truth"
              }
              className={
                "flex items-center gap-2 rounded-md border-2 border-ink-900 px-3 py-1 text-sm font-semibold shadow-chrome-1 transition-colors " +
                (meetingCount === 0
                  ? "cursor-not-allowed bg-paper-2 text-ink-500 opacity-60"
                  : "bg-paper-0 text-ink-900 hover:bg-paper-2")
              }
            >
              <span aria-hidden className="font-mono text-base leading-none">
                ⊞
              </span>
              Belief × Truth
              <span className="rounded-pill bg-paper-2 px-1.5 font-mono text-3xs text-ink-500">
                {meetingCount} mtg
              </span>
            </button>
          </>
        )}
      </div>
    </header>
  );
}

// Hand-coded roster rail (12.4) with the §2.3 advantage bar. Role badge is shown
// in Omniscient only — hidden under the As-agent fog (the firewall, simulated in
// the UI). Alive/dead comes from the current frame.
//
// Responsive (Task 12.11; design §8): the rail is a persistent column at lg+ and
// collapses to a disclosure drawer below it, so the map + transport stay the
// irreducible core on narrow screens. The role / liveness / alive-count facts
// stay Omniscient-gated in both layouts.
function RosterRail() {
  const replay = useReplayStore((s) => s.currentReplay);
  const perspective = useReplayStore((s) => s.perspective);
  const selectAgent = useReplayStore((s) => s.selectAgent);
  const selectedAgentId = useReplayStore((s) => s.selectedAgentId);
  const { frame } = usePlayback();
  const [open, setOpen] = useState(false);

  if (replay === null) {
    return null;
  }

  const aliveById = new Map<string, boolean>();
  for (const state of frame?.agent_states ?? []) {
    aliveById.set(state.agent_id, state.is_alive);
  }
  const adv = frame?.advantage ?? null;
  // The labeled meeting frame (Task 19.10). The loader deliberately serves ONE
  // frame per engine tick, so a resolved meeting's frame mixes two vintages: its
  // `agent_states` are the PRE-vote roster the table deliberated over, while its
  // `advantage` already carries the POST-vote counts (the outcome inflection the
  // advantage graph needs). That mix used to be silent, and this rail was its
  // face: the roster listed the ejected player as alive while the crew count had
  // already dropped them. `meeting_resolution` is the backend's explicit label for
  // exactly that frame, so the rail can now SAY which number is which instead of
  // showing two clocks and no timestamps. `?? null` because the API client casts
  // unvalidated JSON — a pre-19.10 backend yields undefined here.
  const resolution = frame?.meeting_resolution ?? null;
  // Firewall, simulated in the UI: in As-agent fog an agent does NOT know hidden
  // deaths, the living-crew count, or the impostor count — only the GLOBAL task
  // counter (DESIGN.md §1.2 broadcasts that to every agent). So gate the
  // omniscient-only facts (crew/impostor counts, per-player alive/dead, role) to
  // Omniscient; the task progress is agent-visible and shows in both modes.
  const omniscient = perspective.mode === "omniscient";
  // The label rides on the SAME firewall gate as the counts it annotates: it is a
  // statement about crew/impostor arithmetic, which an agent in fog cannot see, so
  // it must not appear in fog either (a lone "after vote" chip over a hidden count
  // would leak that the vote changed the arithmetic at all).
  const labeled = omniscient && resolution !== null;
  // Display denominator is the FIXED game-start task total (DESIGN.md §4;
  // Phase-12 close-audit), NOT the live ``tasks_required`` which shrinks as
  // crewmates die — so the meter + bar stay stable and monotonic.
  const taskPct =
    adv !== null && adv.tasks_required_total > 0
      ? Math.round((adv.tasks_completed / adv.tasks_required_total) * 100)
      : 0;

  return (
    <aside className="w-full shrink-0 rounded-lg border-2 border-ink-900 bg-paper-0 p-3 shadow-chrome-1 lg:w-60">
      <div className="flex items-center justify-between">
        <h2 className="text-lg">Roster</h2>
        <button
          type="button"
          onClick={() => {
            setOpen((value) => !value);
          }}
          aria-expanded={open}
          aria-controls="roster-body"
          className="rounded-md border-2 border-ink-900 bg-paper-0 px-2 py-1 text-xs font-semibold text-ink-900 hover:bg-paper-2 lg:hidden"
        >
          {open ? "Hide ▴" : "Show ▾"}
        </button>
      </div>
      {/* Compact summary on the collapsed roster bar (Task 12.13 narrow-820): keep
          the crew/imp/tasks facts visible when the rail is collapsed on narrow
          screens. Firewall: crew/imp counts only in Omniscient; tasks always. */}
      {adv !== null && !open && (
        <div className="mt-1 font-mono text-3xs text-ink-500 lg:hidden">
          {/* Same "after vote" qualifier as the expanded rail below — the
              collapsed bar shows the same two counts, so it must carry the same
              caveat or the narrow layout is the one that lies (Task 19.10). */}
          {omniscient &&
            `crew ${adv.crew_alive} · imp ${adv.impostors_alive}${labeled ? " after vote" : ""} · `}
          tasks {adv.tasks_completed}/{adv.tasks_required_total}
        </div>
      )}
      <div id="roster-body" className={open ? "mt-2 block" : "mt-2 hidden lg:block"}>
        {adv !== null && (
          <div className="mb-3 rounded-md border border-ink-200 p-2 font-mono text-2xs text-ink-700">
            {omniscient && (
              <div className="mb-2 flex items-center justify-between gap-2">
                <span>crew {adv.crew_alive}</span>
                {labeled && (
                  <span className="rounded-pill border border-ink-300 px-1.5 font-mono text-3xs uppercase tracking-wide text-ink-500">
                    after vote
                  </span>
                )}
                <span>imp {adv.impostors_alive}</span>
              </div>
            )}
            {/* One line of prose, only on a labeled frame: the chip says WHICH
                vintage the counts are, this says which vintage the roster is.
                Role-neutral — it names the timing, never who was right. */}
            {labeled && (
              <p className="mb-2 text-3xs leading-snug text-ink-500">
                Counts are after the vote; the roster below is the pre-vote
                deliberation roster.
              </p>
            )}
            <div className="h-1.5 overflow-hidden rounded-pill bg-paper-3">
              <div className="h-full bg-trust-strong" style={{ width: `${taskPct}%` }} />
            </div>
            <div className="mt-1 text-ink-500">
              tasks {adv.tasks_completed}/{adv.tasks_required_total}
            </div>
          </div>
        )}
        <ul className="flex flex-col gap-1">
          {replay.players.map((player) => {
            const alive = aliveById.get(player.agent_id) ?? true;
            const selected = selectedAgentId === player.agent_id;
            // On a labeled frame this player's `is_alive` is the PRE-vote value,
            // so the vote's own subject would otherwise read "alive" beside a
            // crew count that has already dropped them. Say "ejected" instead —
            // it is the one row where the two vintages visibly disagree. Note the
            // gate: `resolution !== null` means RESOLVED (a SKIPPED meeting is
            // labeled too, with a null ejected id), so the chip additionally
            // requires an actual ejected player.
            const ejected =
              labeled && resolution?.ejected_player_id === player.agent_id;
            return (
              <li key={player.agent_id}>
                {/* Roster row → open this agent's mind (Task 12.13): inspection is
                    reachable from the roster, not only inside a meeting. */}
                <button
                  type="button"
                  onClick={() => {
                    // The store re-aims the fog to this agent in As-agent mode
                    // (firewall invariant); Omniscient just selects.
                    selectAgent(player.agent_id);
                  }}
                  aria-pressed={selected}
                  title={`Inspect ${player.agent_id}'s mind`}
                  className={
                    "flex w-full items-center gap-2 rounded-md border px-2 py-1 text-left transition-colors " +
                    (selected
                      ? "border-ink-900 bg-paper-2"
                      : "border-ink-100 hover:border-ink-900 hover:bg-paper-2")
                  }
                >
                  <PlayerSwatch color={player.color} size="sm" />
                  <span className="min-w-0 flex-1 truncate font-mono text-xs text-ink-900">
                    {player.agent_id}
                  </span>
                  {omniscient && (
                    <span className="rounded-sm border border-ink-300 px-1 text-4xs uppercase tracking-wide text-ink-500">
                      {player.role}
                    </span>
                  )}
                  {omniscient && (
                    <span
                      // Role-neutral: solid ink, never a guilt hue — "ejected"
                      // says the table voted, not that the table was right.
                      title={
                        ejected
                          ? "Ejected by this meeting's vote (the roster row is the pre-vote state)"
                          : undefined
                      }
                      className={
                        "rounded-sm px-1 text-4xs font-semibold uppercase " +
                        (ejected
                          ? "bg-ink-900 text-paper-0"
                          : alive
                            ? "text-ink-500"
                            : "bg-dead text-paper-0")
                      }
                    >
                      {ejected ? "ejected" : alive ? "alive" : "dead"}
                    </span>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    </aside>
  );
}

// The shared secondary-button chrome for the two Task 19.10 surfaces below —
// the same variant PerspectiveBanner's "‹ Replays" / "Exit fog" use, so the new
// controls read as the shell's own chrome rather than a bolted-on widget.
const ACTION_BUTTON =
  "rounded-md border-2 border-ink-900 bg-paper-0 px-3 py-1 text-sm font-medium " +
  "text-ink-900 transition-colors hover:bg-paper-2";

// ── the meeting pause bar (Task 19.10) ───────────────────────────────────────
//
// A meeting occupies exactly ONE frame (`MeetingView` carries a single `tick`, no
// span), so at 1× autoplay flashes an entire deliberation past in 500 ms. The
// playback hook now stops the transport on entering a meeting tick — and an
// automatic stop with no on-screen cause reads as a bug, so this bar names it and
// offers the way out.
//
// The PAUSE case is keyed on the FRAME (`meetingAtTick`), never on
// `selectedMeetingId`: auto-follow can be switched off, in which case the pause
// fires with no meeting modal opening, and that is precisely the case where an
// unexplained stop is most confusing. One additional render case DOES read the
// selection — the stale-meeting-at-End signpost (see `staleMeetingAtEnd`
// below), where an explicitly opened meeting from an earlier tick is the thing
// standing between the user and the finale card.
//
// MOUNT (load-bearing, not cosmetic): it lives INSIDE the `[data-transport-region]`
// container, as the first child of its inner column. Three properties come from
// that and nowhere else — (a) `useTransportHeight`'s ResizeObserver measures the
// bar, so the fixed overlays keep reserving the right `--transport-h` as it
// appears and disappears; (b) the region sits at z-70, above the meeting modal's
// z-50 scrim, so Resume stays VISIBLE while a meeting owns the screen — visible,
// not Tab-reachable: the modal's focus trap cycles inside its own dialog, so
// while a meeting is open these buttons are pointer-only and the keyboard route
// is the meeting's own Escape/Close (or Space, which still toggles play while
// focus rests on the dialog container); (c) the KeyboardTransport accelerator
// carve-out keeps arrows / `n` / `[` / `]` live for buttons inside this region,
// which they would not be anywhere else on the page.
//
// `role="status"` because the pause is otherwise silent: the transport's single
// Play/Pause toggle just flips its own label, which announces nothing.
function MeetingPauseBar() {
  const {
    hasReplay,
    meetingAtTick,
    isPlaying,
    isAtEnd,
    finale,
    play,
    nextKeyMoment,
  } = usePlayback();
  const selectedMeetingId = useReplayStore((s) => s.selectedMeetingId);
  const selectMeeting = useReplayStore((s) => s.selectMeeting);

  // Second render case (Task 19.10 review): the playhead is at the END with a
  // finale to show, but a meeting the user EXPLICITLY opened earlier (pill /
  // meeting jump — auto-follow never clears an explicit selection, by design)
  // still owns the screen from a previous tick. The finale card yields to any
  // open meeting, and with no meeting on the current frame the bar would not
  // render either — leaving the promised End/scrub finale invisible with no
  // signpost. Auto-closing the user's own transcript would be exactly the yank
  // the auto-follow refs exist to prevent, so instead the bar renders and
  // offers the same explicit "Show finale" hand-off the ejection ending has.
  const staleMeetingAtEnd =
    meetingAtTick === null &&
    isAtEnd &&
    selectedMeetingId !== null &&
    finale !== null;

  if (!hasReplay || isPlaying || (meetingAtTick === null && !staleMeetingAtEnd)) {
    return null;
  }
  return (
    <div
      role="status"
      className="flex flex-wrap items-center gap-2 rounded-md border-2 border-ink-900 bg-paper-0 px-3 py-1.5 shadow-data"
    >
      <span className="rounded-pill bg-paper-2 px-1.5 font-mono text-3xs uppercase tracking-wide text-ink-500">
        {meetingAtTick !== null ? "paused" : "end"}
      </span>
      <span className="font-mono text-xs text-ink-900">
        {meetingAtTick !== null
          ? `Meeting at tick ${meetingAtTick.tick} — playback paused`
          : "End of replay — a meeting from an earlier tick is open"}
      </span>
      <div className="ml-auto flex items-center gap-2">
        {isAtEnd ? (
          // At the end there is nothing to resume to, so the one useful move is
          // to dismiss the open meeting and let the finale card — which yields
          // the screen to any open meeting — take it. This covers BOTH end
          // cases: the last frame IS the meeting frame (an ejection ending),
          // and the stale-meeting case above (an explicitly opened meeting from
          // an earlier tick still holding the screen at End). Offered only when
          // a meeting is actually open (with auto-follow off the finale is
          // already showing) AND a finale exists to hand off to: a partial
          // recording whose walk ends on a resolved meeting has no game_over
          // row, `finale === null`, and no card can ever appear — a button
          // promising one would be a dead end.
          selectedMeetingId !== null &&
          finale !== null && (
            <button
              type="button"
              onClick={() => {
                selectMeeting(null);
              }}
              className={ACTION_BUTTON}
            >
              Show finale
            </button>
          )
        ) : (
          <>
            <button
              type="button"
              onClick={play}
              title="Resume playback (the pause is edge-triggered, so this advances past the meeting)"
              className={ACTION_BUTTON}
            >
              <span aria-hidden>▶</span> Resume
            </button>
            <button
              type="button"
              onClick={nextKeyMoment}
              title="Skip to the next key moment (kill / meeting / ejection / sabotage)"
              className={ACTION_BUTTON}
            >
              Next beat <span aria-hidden>→</span>
            </button>
          </>
        )}
      </div>
    </div>
  );
}

// ── the finale card (Task 19.10) ─────────────────────────────────────────────

// `winner_reason` is a RAW recorded string, not a closed enum on the wire, so the
// humanising map is a best-effort lookup with a mandatory fallback: an unmapped
// reason (the fidelity fixture records `all_tasks_complete`, and older recordings
// may carry anything) renders verbatim in mono rather than being swallowed or
// mislabelled. Never invent a reason we did not record.
const WINNER_REASON_LABEL: Record<string, string> = {
  CREWMATE_TASKS: "all tasks completed",
  CREWMATE_EJECT: "every impostor ejected",
  IMPOSTOR_PARITY: "impostors reached parity",
  IMPOSTOR_SABOTAGE: "sabotage unresolved",
};

// Role-neutral copy per decisive beat. No hue, no blame: "ejected" says the table
// voted, not that the table was right — the recap rows below are where ground
// truth and belief are set side by side.
function decisiveEventText(event: FinaleEventView): string {
  switch (event.kind) {
    case "kill":
      return `${event.actor_id ?? "someone"} killed ${event.subject_id ?? "someone"}`;
    case "ejection":
      return `${event.subject_id ?? "someone"} ejected`;
    case "meeting_skipped":
      return "meeting — no ejection";
    case "game_end":
      return "game over";
  }
}

/** One "what they knew vs the truth" row: ground truth solid, ballot ghosted. */
function RecapRow({
  recap,
  color,
}: {
  recap: FinaleAgentRecapView;
  color: string;
}) {
  const vote =
    recap.final_vote_target === null
      ? "no vote"
      : recap.final_vote_target === "SKIP"
        ? "voted SKIP"
        : `voted ${recap.final_vote_target}`;
  // A REWRITTEN ballot's target is the engine's tally, not the voter's authored
  // choice (redirect / coercion / parse default — the recorded rationale can
  // explicitly oppose it), so it must not read as "what they knew". The row
  // says so in words and the backend already withholds the ✓/✗ judgment
  // (`final_vote_named_impostor` is null for a rewritten ballot). The label is
  // deliberately generic — WHY the engine adjusted it is reason-level detail
  // (the ballot chips' territory), and one of those reasons discloses the
  // impostor pairing, which reveal must never do.
  const adjusted = recap.final_vote_rewritten;
  return (
    <li className="flex flex-wrap items-center gap-2 rounded-md border border-ink-200 px-2 py-1">
      <PlayerSwatch color={color} size="sm" />
      <span className="font-mono text-xs text-ink-900">{recap.agent_id}</span>
      {/* GROUND TRUTH — solid outline, full opacity (the two-truth grammar's
          `ground` half). Role-neutral ink: the badge is the reveal, never a hue. */}
      <span className="rounded-sm border-2 border-ink-900 px-1 text-4xs font-semibold uppercase tracking-wide text-ink-900">
        {recap.role}
      </span>
      <span className="rounded-sm px-1 text-4xs font-semibold uppercase text-ink-500">
        {recap.alive_at_end ? "survived" : "eliminated"}
      </span>
      {/* BELIEF — the same grammar's ghosted half at the token's 0.5 opacity, and
          attributed (it is this agent's ballot, not a fact about the game). The
          final vote is the only decision-level evidence of what they believed
          that lives on the bulk path; the per-agent belief walk is a separate,
          expensive request. */}
      <span className="ml-auto flex items-center gap-1.5 font-mono text-2xs text-ink-700 opacity-50">
        {vote}
        {adjusted && (
          <span
            title="The meeting layer rewrote this ballot's target, so the tallied vote is not the voter's authored choice — no belief judgment is shown for it"
            className="rounded-sm border border-ink-300 px-1 text-4xs uppercase tracking-wide text-ink-500"
          >
            engine-adjusted
          </span>
        )}
        {recap.final_vote_named_impostor !== null && (
          <span className="text-ink-900">
            {recap.final_vote_named_impostor ? (
              <>
                <span aria-hidden>✓</span> named an impostor
              </>
            ) : (
              <>
                <span aria-hidden>✗</span> missed
              </>
            )}
          </span>
        )}
      </span>
    </li>
  );
}

// The end-of-replay card. Reaching the last frame produced NO state change before
// this: the timer stopped, the Play button greyed out (it is disabled at the last
// frame), and the screen sat there. This is the fourth participant in the
// overlay z-order documented on Workspace below — z-60, above the meeting tier at
// z-50 and below the transport at z-70 — and, like its siblings, it reserves the
// MEASURED `--transport-h` so it never covers the transport it depends on.
//
// It exists whenever the playhead is ON the finale (position-derived, so autoplay,
// `End`, and a scrub to the far right all land on it identically); `revealOutcome`
// selects its CONTENT, not its existence. That split is the whole point: the fact
// that the game is over is not a spoiler, and hiding the card entirely would leave
// the unspoiled viewer on a dead screen with a disabled Play button.
//
// PRECEDENCE: it yields to an open meeting (`selectedMeetingId === null`). A game
// that ends on an ejection has the meeting and the finale on the SAME frame, and
// stacking a second card over a focus-trapped modal would be unreachable by
// keyboard. The hand-off out of the meeting is two-path: the pause bar's "Show
// finale" for the pointer (the bar is visible above the scrim but sits OUTSIDE
// the modal's focus trap, so Tab cannot reach it while the meeting is open), and
// the meeting's own Escape/Close for the keyboard — either way the meeting
// closes, `selectedMeetingId` clears, and this card takes the frame.
function FinaleCard() {
  const { finale, seekToIndex } = usePlayback();
  const replay = useReplayStore((s) => s.currentReplay);
  const selectedMeetingId = useReplayStore((s) => s.selectedMeetingId);
  const revealOutcome = useReplayStore((s) => s.revealOutcome);
  const setRevealOutcome = useReplayStore((s) => s.setRevealOutcome);
  // Dismissal is pure UI state, deliberately NOT in the store and NOT URL-synced:
  // it is "I have read this card", not part of the shared moment. It resets when
  // the finale goes away (scrubbing off the last frame, or loading another
  // replay) AND whenever a meeting takes the screen — so the pause bar's "Show
  // finale" hand-off always lands: dismiss the card, re-open the meeting from
  // the pill, click "Show finale" again, and the card returns instead of the
  // stale dismissal eating the click.
  const [dismissed, setDismissed] = useState(false);
  const cardRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (finale === null || selectedMeetingId !== null) {
      setDismissed(false);
    }
  }, [finale, selectedMeetingId]);

  const open = finale !== null && selectedMeetingId === null && !dismissed;
  // Move focus to the card when it appears — but ONLY when nothing else holds it.
  // The card is a fixed overlay outside the document flow, so the courtesy focus
  // is what makes it immediately operable by keyboard; the guard is because the
  // last frame is reachable by driving the scrubber (a range input) or the
  // graph's slider, and yanking focus mid-drag would be worse than the walk. It
  // is NOT a focus trap either way — nothing is masked, and Tab walks straight on
  // into the transport region, which is the next node in DOM order.
  useEffect(() => {
    if (!open) {
      return;
    }
    const active = document.activeElement;
    if (active === null || active === document.body) {
      cardRef.current?.focus({ preventScroll: true });
    }
  }, [open]);

  if (finale === null || !open) {
    return null;
  }

  const colorById = new Map<string, string>(
    (replay?.players ?? []).map((p) => [p.agent_id, p.color]),
  );
  const winnerGlyph = finale.winner === "IMPOSTORS" ? "◆" : "▲";
  const winnerLabel = finale.winner === "IMPOSTORS" ? "Impostor win" : "Crew win";
  const reason = WINNER_REASON_LABEL[finale.winner_reason];

  return (
    // `pointer-events-none` on the frame, `auto` on the card: this is an
    // ANNOUNCEMENT, not a modal. The map, the roster and the transport behind it
    // all stay clickable — the card is dismissed by its own ✕ or by scrubbing off
    // the last frame, never by trapping the page.
    <div
      className="pointer-events-none fixed inset-0 z-[60] flex items-center justify-center p-4"
      style={{ paddingBottom: "var(--transport-h, 16rem)" }}
    >
      <div
        ref={cardRef}
        tabIndex={-1}
        role="region"
        aria-label="End of replay"
        className="pointer-events-auto flex max-h-full w-full max-w-xl flex-col gap-3 overflow-y-auto rounded-lg border-2 border-ink-900 bg-paper-0 p-4 shadow-chrome-2 outline-none"
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex flex-col gap-0.5">
            <SectionLabel as="h2">End of replay</SectionLabel>
            {revealOutcome ? (
              <span className="font-display text-xl leading-tight text-ink-900">
                <span aria-hidden className="mr-1.5 font-mono">
                  {winnerGlyph}
                </span>
                {winnerLabel}
              </span>
            ) : (
              <span className="font-display text-xl leading-tight text-ink-900">
                The game is over
              </span>
            )}
          </div>
          <button
            type="button"
            onClick={() => {
              setDismissed(true);
            }}
            aria-label="Dismiss the end-of-replay card"
            className="shrink-0 rounded-md border-2 border-ink-900 bg-paper-0 px-2 py-0.5 text-xs font-bold text-ink-900 hover:bg-paper-2"
          >
            ✕
          </button>
        </div>

        {revealOutcome ? (
          <>
            <p className="font-mono text-xs text-ink-700">
              {reason === undefined ? (
                // Unmapped recorded reason: show the bytes, verbatim, rather
                // than a guess (AGENTS.md — no silent fallbacks).
                <span className="text-ink-900">{finale.winner_reason}</span>
              ) : (
                reason
              )}
              <span className="text-ink-300"> · </span>
              final tick {finale.final_tick}
            </p>

            <section className="flex flex-col gap-1">
              <SectionLabel as="h3">Decisive events</SectionLabel>
              {/* Pre-sorted server-side (ascending tick, kill → ejection →
                  game_end within a tick) — rendered in the order received, never
                  re-sorted here. */}
              <ol className="flex flex-col gap-1">
                {finale.decisive_events.map((event, index) => (
                  <li
                    key={`${event.tick}-${event.kind}-${index}`}
                    className="flex items-center gap-2 rounded-md border border-ink-200 px-2 py-1"
                  >
                    <span className="shrink-0 rounded-pill bg-paper-2 px-1.5 font-mono text-3xs text-ink-500">
                      t{event.tick}
                    </span>
                    <span className="font-mono text-2xs text-ink-900">
                      {decisiveEventText(event)}
                    </span>
                  </li>
                ))}
              </ol>
            </section>

            <section className="flex flex-col gap-1">
              <SectionLabel as="h3">What they knew vs the truth</SectionLabel>
              <ul className="flex flex-col gap-1">
                {finale.agent_recaps.map((recap) => (
                  <RecapRow
                    key={recap.agent_id}
                    recap={recap}
                    // Unknown identity → no colour, rather than a borrowed one.
                    color={colorById.get(recap.agent_id) ?? "transparent"}
                  />
                ))}
              </ul>
            </section>
          </>
        ) : (
          <p className="text-sm text-ink-700">
            The outcome is hidden — spectate unspoiled, or reveal how it ended.
          </p>
        )}

        <div className="flex flex-wrap items-center gap-2">
          {revealOutcome ? (
            <button
              type="button"
              onClick={() => {
                setRevealOutcome(false);
              }}
              className={ACTION_BUTTON}
            >
              Hide outcome
            </button>
          ) : (
            <button
              type="button"
              onClick={() => {
                setRevealOutcome(true);
              }}
              title="Show the winner, the decisive events, and every agent's final ballot"
              className={ACTION_BUTTON}
            >
              Reveal the outcome
            </button>
          )}
          <button
            type="button"
            // Seek only — deliberately NOT `play()`. The transport's Play button
            // is DISABLED at the last frame, so the card must own the restart;
            // but auto-starting playback would take the transport away from a
            // reader who only wanted to get back to the top, and the pause bar
            // would then fire at the first meeting anyway. One button, one
            // effect: the playhead goes to frame 0 and stays there.
            onClick={() => {
              seekToIndex(0);
            }}
            className={ACTION_BUTTON}
          >
            Watch again
          </button>
        </div>
      </div>
    </div>
  );
}

// Measure the bottom transport region and publish its height as `--transport-h`
// so the fixed overlays (meeting modal, mind rail) reserve EXACTLY that space —
// no magic px constants, and it adapts as the timeline / controls reflow on
// narrow widths. Reset to 0 when the workspace (and its transport) is unmounted.
function useTransportHeight(): RefObject<HTMLDivElement | null> {
  const ref = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    const node = ref.current;
    const reset = (): void => {
      document.documentElement.style.setProperty("--transport-h", "0px");
    };
    if (node === null) {
      reset();
      return reset;
    }
    const set = (height: number): void => {
      document.documentElement.style.setProperty(
        "--transport-h",
        `${Math.ceil(height)}px`,
      );
    };
    set(node.getBoundingClientRect().height);
    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry !== undefined) {
        set(entry.contentRect.height);
      }
    });
    observer.observe(node);
    return () => {
      observer.disconnect();
      reset();
    };
  }, []);
  return ref;
}

// The Replay Workspace (§2.3). The fixed overlays (MeetingView modal, Belief /
// ThoughtStream rails, and — since Task 19.10 — the FinaleCard) self-position and
// reserve `--transport-h` at the bottom so the transport region stays reachable;
// they no longer collide (Task 12.11): an open meeting masks the workspace, the
// mind rail sits in its own reserved gutter beside the ballots, and the belief
// hero steps aside while a meeting is open (see those components). The z-order
// contract, top to bottom: transport z-70 > finale z-60 > mind rail z-55 >
// meeting z-50.
function Workspace() {
  const transportRef = useTransportHeight();
  return (
    <>
      <section
        className="flex flex-col gap-4"
        style={{ paddingBottom: "var(--transport-h, 16rem)" }}
      >
        <PerspectiveBanner />
        <div className="flex flex-col gap-4 lg:flex-row">
          <RosterRail />
          {/* Stage slot — the map (12.5). The meeting morph (12.7) is the
              MeetingView overlay below. The map fills the stage width. */}
          <div className="min-w-0 flex-1">
            <Suspense fallback={<RouteFallback />}>
              <MapView />
            </Suspense>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <MeetingPill />
              {/* Task 19.17. Frame-bounded model spend — cumulative to the
                  current frame, never the game total (a total is an
                  outcome-shape leak under unspoiled mode). It shares the pill
                  row because it is a chip strip, not a panel. */}
              <CostChips />
            </div>
            {/* Task 19.17. The running feed of kills / reports / meetings /
                ejections / vents, rendered through the SAME perspective
                projection the map above it enforces — the served event views
                carry privileged kill attribution and vent routes, so the fog is
                the firewall, not the unspoiled-mode gate. */}
            <EventTicker />
          </div>
        </div>
      </section>

      {/* Self-positioned slots: meeting morph (12.7), belief panel (12.6), mind
          panel (12.8). Each renders null until its selection gate opens; Task
          12.11 coordinates their z-order + gutters so they never collide. */}
      <MeetingView />
      <BeliefMatrix />
      <ThoughtStream />

      {/* The fourth self-positioned overlay (Task 19.10): the end-of-replay card
          at z-60 — above the meeting tier (z-50) so it is never buried, below the
          transport (z-70) so playback stays reachable. It renders null until the
          playhead is on the finale AND no meeting owns the screen. */}
      <FinaleCard />

      <KeyboardTransport />

      {/* Bottom transport region: advantage graph · event timeline · transport.
          Fixed above the overlays (z-70 > the meeting modal) so playback stays
          reachable; its measured height feeds `--transport-h`. */}
      <div
        ref={transportRef}
        data-transport-region
        className="fixed inset-x-0 bottom-0 z-[70] border-t-2 border-ink-900 bg-paper-1/95 backdrop-blur"
      >
        <div className="mx-auto flex max-w-[1600px] flex-col gap-2 p-3">
          {/* FIRST child of the measured column on purpose (Task 19.10) — see
              MeetingPauseBar's own note: it must be inside this region for the
              ResizeObserver, the z-order above the meeting scrim, and the
              keyboard-accelerator carve-out. It renders null off a meeting frame,
              so it costs the transport nothing the rest of the time. */}
          <MeetingPauseBar />
          <AdvantageGraph />
          <div className="max-h-40 overflow-y-auto pr-1">
            <EventTimeline />
          </div>
          <ReplayControls />
        </div>
      </div>
    </>
  );
}

export default function App() {
  const loadReplayList = useReplayStore((s) => s.loadReplayList);
  const view = useReplayStore((s) => s.view);
  // Hide the shell header while a meeting overlay is open: the meeting scrim is
  // translucent, so at 820px the nav bled through over the "triggered by" line.
  // Hiding it covers all breakpoints AND keeps the nav out of the meeting's
  // focus-trap; the meeting's own header (with Close) stands in.
  const meetingOpen = useReplayStore((s) => s.selectedMeetingId !== null);

  useEffect(() => {
    void loadReplayList();
  }, [loadReplayList]);

  return (
    <div className="min-h-screen bg-paper-1 p-4 text-ink-900 sm:p-6">
      <PlaybackEngine />
      <GuidedTour />
      {!meetingOpen && (
        <header className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-2xl">AiLibi</h1>
          <TopNav />
        </header>
      )}

      <Suspense fallback={<RouteFallback />}>
        {view === "tournament" ? (
          <TournamentDashboard />
        ) : view === "workspace" ? (
          <Workspace />
        ) : (
          // Replays + Highlights routes both mount the browser; 12.9 makes it
          // view-aware (it reads `view` from the store) and surfaces the reel.
          <ReplayPicker />
        )}
      </Suspense>
    </div>
  );
}
