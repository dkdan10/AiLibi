// First-run guided mode (Task 12.11; design/phase-12/stage-1-design.md §8 —
// "First-run / guided mode: annotated walkthrough on a high-interestingness seed
// teaching the perspective switcher + the two-truth grammar"). Hand-coded from
// tokens (no Claude Design pass — see tasks/phase-12.md Wave-B note).
//
// On the first visit it auto-opens, loads the head of the hand-curated FEATURED
// list for 9p2i (Task 19.9 — so the walkthrough has real drama to point at),
// and steps through the viewer's load-bearing ideas: the two-truth grammar, the
// perspective switcher + fog firewall, the Belief × Truth hero, and the
// keyboard-operable transport. It is dismissible and remembers that via
// localStorage; the header "Tour" button re-opens it on demand without yanking
// the replay you are already watching.
//
// Honesty + firewall stay intact even in the teaching legend: identity ≠ guilt
// (the impostor reveal is an ICON, never a hue), suspicion is a bucketed heat
// ramp, trust↔distrust is blue↔orange, and every swatch is paired with a LABEL
// (never hue-only — the design §8 a11y rule).

import { useCallback, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";

import { getRubric, getSets, listReplays } from "../api/client";
import { OVERLAY_RANK, useFocusTrap } from "../hooks/useFocusTrap";
import { useReplayStore } from "../store/replayStore";
import { tokens } from "../tokens";

const SEEN_KEY = "ailibi.guidedTourSeen.v1";
const OPEN_EVENT = "ailibi:open-guided-tour";
// 9p2i is the curated spectator set (and, since Task 19.9, the server default);
// 4p1i is the fast fixture — at most one meeting per game, no rubric. Teach on
// 9p2i so the walkthrough lands on a game with meetings in it.
const TARGET_SET = "9p2i";

/** Re-open the guided tour from anywhere in the shell (the header "Tour" button). */
export function openGuidedTour(): void {
  window.dispatchEvent(new CustomEvent(OPEN_EVENT));
}

// Best-effort: open the head of the CURATED featured list for the target set
// (Task 19.9). It used to open the rubric's top-ranked game, but the rubric is an
// internal pacing/structure heuristic whose ordering both Phase-19 audits found
// inverts the human-interest tails — a fresh re-score clears staleness, it does
// not validate watchability. The curated head is a hand-read game; the rubric's
// best-ranked game is the fallback when the served set carries no featured seed,
// and the first replay when it ships no rubric either. Any error → nothing loads
// (the legend still teaches the grammar).
//
// Cancellation (Task 12.11 review): `/sets` + `/replays` are async, so re-check
// the live store right before the navigation and bail if the user moved on —
// dismissed the tour, opened a replay, or switched the set — so a slow load can't
// yank them back to the teaching seed and clobber their URL/workspace state.
async function loadCuratedSeed(): Promise<void> {
  const store = useReplayStore.getState();
  const aborted = (set: string): boolean => {
    const now = useReplayStore.getState();
    return !now.guidedTourOpen || now.currentReplay !== null || now.seedSet !== set;
  };
  try {
    const { sets, default: defaultSet } = await getSets();
    const set = sets.includes(TARGET_SET) ? TARGET_SET : defaultSet;
    if (useReplayStore.getState().currentReplay !== null) {
      return; // user already opened a replay before /sets resolved
    }
    store.setSeedSet(set);
    const [list, rubric] = await Promise.all([
      listReplays(set),
      getRubric(set).catch(() => null),
    ]);
    if (list.length === 0 || aborted(set)) {
      return;
    }
    let gameId = list[0]!.game_id;
    if (rubric !== null && rubric.per_game.length > 0) {
      const bestSeed = rubric.per_game[0]!.seed;
      const match = list.find((meta) => meta.seed === bestSeed);
      if (match !== undefined) {
        gameId = match.game_id;
      }
    }
    // The curated head wins over the rubric head where the set has one. The
    // featured list is imported DYNAMICALLY: App.tsx lazy-loads ReplayPicker, and
    // a static import here would pull the whole browser into the entry chunk.
    const { featuredForSet } = await import("./ReplayPicker");
    for (const game of featuredForSet(set)) {
      const match = list.find((meta) => meta.seed === game.seed);
      if (match !== undefined) {
        gameId = match.game_id;
        break;
      }
    }
    if (aborted(set)) {
      return;
    }
    await store.selectReplay(gameId);
  } catch {
    // Best-effort — the tour still teaches the grammar without a loaded replay.
  }
}

// A labelled swatch for the legend. The label is what keeps every cue readable
// without colour (never hue-only); `shape` carries an optional glyph/marker.
function Swatch({
  color,
  label,
  shape,
  ghost,
}: {
  color: string;
  label: string;
  shape?: ReactNode;
  ghost?: boolean;
}) {
  return (
    <span className="inline-flex items-center gap-1.5 text-[11px] text-ink-700">
      <span
        aria-hidden
        className="inline-flex h-4 w-4 items-center justify-center rounded-sm border-2 border-ink-900"
        style={{ backgroundColor: color, opacity: ghost ? 0.45 : 1 }}
      >
        {shape}
      </span>
      {label}
    </span>
  );
}

function TwoTruthLegend() {
  return (
    <div className="flex flex-col gap-2 rounded-md border border-ink-200 bg-paper-1 p-3">
      <div className="flex flex-wrap gap-x-4 gap-y-1.5">
        <Swatch color={tokens.identity[5]!} label="ground truth (solid)" />
        <Swatch color={tokens.identity[5]!} label="belief (ghosted)" ghost />
        <Swatch
          color={tokens.ink[900]}
          label="impostor = icon, not a hue"
          shape={<span className="text-[9px] font-bold text-paper-0">†</span>}
        />
      </div>
      <div className="flex flex-wrap gap-x-4 gap-y-1.5">
        <Swatch color={tokens.suspicion[0]!} label="suspicion low" />
        <Swatch color={tokens.suspicion[2]!} label="med" />
        <Swatch color={tokens.suspicion[4]!} label="high" />
        <Swatch color={tokens.trust.strong} label="trust" />
        <Swatch color={tokens.distrust.strong} label="distrust" />
        <Swatch color={tokens.kill} label="kill" />
      </div>
    </div>
  );
}

function KeyCap({ children }: { children: ReactNode }) {
  return (
    <kbd className="rounded border border-ink-400 bg-paper-1 px-1.5 py-0.5 font-mono text-[10px] text-ink-900">
      {children}
    </kbd>
  );
}

interface Step {
  readonly title: string;
  readonly body: ReactNode;
}

const STEPS: readonly Step[] = [
  {
    title: "Welcome — investigate a recorded decision",
    body: (
      <>
        <p className="mb-2 text-sm text-ink-700">
          AiLibi asks whether AI agents can reason from what they actually saw.
          You are watching saved games, not making live model calls. Daniel Keinan
          directs the project; Claude Code and Codex agents write code and supporting
          material, with separate AI review. <a className="underline" href="https://github.com/dkdan10/AiLibi" target="_blank" rel="noreferrer">Read the source and ownership case study.</a>
        </p>
        <p className="mb-2 text-sm text-ink-700">
          Players move one room edge per tick. Crew complete tasks or eject every
          impostor; impostors kill, deceive, and sabotage, winning at parity or an
          unresolved sabotage. Body reports and emergency calls begin discussion
          and voting. Movement is rule-based; models deliberate at meetings.
        </p>
        <p className="mb-2 text-sm text-ink-700">
          Start at <strong>Results &amp; cases</strong> for three decisions to investigate.
          A ballot citation opens its exact source, scene, and meeting memory.
          Missing evidence is labelled; a real citation can still be irrelevant.
          Ground truth is solid; attributed belief is ghosted.
        </p>
        <TwoTruthLegend />
      </>
    ),
  },
  {
    title: "Perspective switcher + the fog firewall",
    body: (
      <p className="text-sm text-ink-700">
        The map toolbar (top-right of the stage) flips between{" "}
        <strong>Omniscient</strong> and <strong>As-agent</strong>. In As-agent
        fog the map dims to <em>only</em> what that one agent could see — role
        badges and the impostor reveal disappear, because that agent never knew
        them. Identity colour is identity only; it never encodes guilt.
      </p>
    ),
  },
  {
    title: "Belief × Truth — who suspected whom",
    body: (
      <p className="text-sm text-ink-700">
        Open the <strong>Belief × Truth</strong> hero from the perspective banner
        (top, beside the perspective toggle) for the suspicion matrix — a bucketed
        heat ramp (Low / Med / High) you can flip to Ground-Truth or Error.
        Confidently-wrong cells are drawn loud (fill + border + ✗), and “no belief
        yet” is a hatched cell, never a 0.
      </p>
    ),
  },
  {
    title: "Open a mind",
    body: (
      <p className="text-sm text-ink-700">
        Click any agent — on the <strong>map</strong> or in the{" "}
        <strong>roster</strong> — to open the <strong>Mind inspector</strong>: its
        belief, the exact prompt + response the LLM saw, its memory, and the flags
        against it, snapped to that agent’s latest meeting. Before an agent’s first
        meeting you’ll see an honest “no deliberation yet” — never invented data.
      </p>
    ),
  },
  {
    title: "Drive the replay",
    body: (
      <div className="space-y-2 text-sm text-ink-700">
        <p>Scrub, step, and jump to the drama from the transport at the bottom — or by keyboard:</p>
        <div className="flex flex-wrap gap-2">
          <span className="inline-flex items-center gap-1">
            <KeyCap>Space</KeyCap> play / pause
          </span>
          <span className="inline-flex items-center gap-1">
            <KeyCap>←</KeyCap>
            <KeyCap>→</KeyCap> step ±1 (with <KeyCap>Shift</KeyCap> ±10)
          </span>
          <span className="inline-flex items-center gap-1">
            <KeyCap>,</KeyCap>
            <KeyCap>.</KeyCap> prev / next event
          </span>
          <span className="inline-flex items-center gap-1">
            <KeyCap>[</KeyCap>
            <KeyCap>]</KeyCap> prev / next meeting
          </span>
          <span className="inline-flex items-center gap-1">
            <KeyCap>n</KeyCap> next key moment
          </span>
        </div>
      </div>
    ),
  },
];

export function GuidedTour() {
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState(0);

  const finish = useCallback(() => {
    try {
      localStorage.setItem(SEEN_KEY, "1");
    } catch {
      /* private mode / storage disabled — the tour just won't be remembered */
    }
    setOpen(false);
  }, []);

  // First-run auto-open: show the tour and load the curated 9p2i seed so the
  // walkthrough has a real game behind it. A first-time visitor who
  // arrived via a SHARED deep link (a `game_id` in the URL) keeps that moment —
  // the tour still opens to annotate it, but it must NOT clobber the shared
  // replay with its own seed (the URL hydration in usePlaybackEngine owns that).
  useEffect(() => {
    let seen = false;
    try {
      seen = localStorage.getItem(SEEN_KEY) === "1";
    } catch {
      seen = false;
    }
    if (seen) {
      return;
    }
    setStep(0);
    setOpen(true);
    // Only auto-load the teaching seed on a truly EMPTY URL. ANY shared query
    // state is an explicit destination the visitor opened — a deep-linked game
    // (`game_id`/`tick`), OR a shared view/filter/set (`view`/`winner`/
    // `scoreBucket`/`set`/…). `loadCuratedSeed()` calls `selectReplay()`,
    // which forces `view=workspace`, and the URL sync would then clobber that
    // shared page/filter. Leave any such URL in place (its hydration owns it) and
    // just open the tour to annotate it.
    const hasUrlState =
      [...new URLSearchParams(window.location.search).keys()].length > 0;
    if (!hasUrlState) {
      void loadCuratedSeed();
    }
  }, []);

  // Publish the open state to the store so the global transport shortcuts can be
  // suppressed, and the meeting/belief overlays can yield Escape, while the tour
  // is up. (Explicit store state — not a module-level flag — per AGENTS.md.)
  const setGuidedTourOpen = useReplayStore((s) => s.setGuidedTourOpen);
  useEffect(() => {
    setGuidedTourOpen(open);
    return () => {
      setGuidedTourOpen(false);
    };
  }, [open, setGuidedTourOpen]);

  // Re-open on demand (header "Tour" button). Does NOT reload the replay — it
  // annotates whatever the user is already watching.
  useEffect(() => {
    const onOpen = (): void => {
      setStep(0);
      setOpen(true);
    };
    window.addEventListener(OPEN_EVENT, onOpen);
    return () => {
      window.removeEventListener(OPEN_EVENT, onOpen);
    };
  }, []);

  const lastStep = STEPS.length - 1;
  const stepRef = useRef<HTMLDivElement>(null);

  // Tab stays inside the card, and the tour is the TOP-MOST overlay: when it
  // opens over a meeting or over the Belief × Truth matrix, its rank makes it
  // the one trap that answers a Tab, so the ring below runs Skip → Back → Next
  // instead of two traps tearing focus between them.
  useFocusTrap(stepRef, open, OVERLAY_RANK.guidedTour);

  // A step change swaps the card's content and can DISABLE the control that has
  // focus (Back, on the way back to the first step), so move focus to the card
  // and let the ring restart from the top. Focus on OPEN and its restore on
  // close belong to `useFocusTrap`.
  useEffect(() => {
    stepRef.current?.focus();
  }, [step]);

  // Escape closes the tour. It owns the key while open — the meeting/belief
  // overlays gate their own Escape on `guidedTourOpen` — so one Escape closes
  // only the tour, not a meeting hydrated behind it.
  useEffect(() => {
    if (!open) {
      return;
    }
    const onKey = (event: KeyboardEvent): void => {
      if (event.key !== "Escape") {
        return;
      }
      event.preventDefault();
      finish();
    };
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("keydown", onKey);
    };
  }, [open, finish]);

  if (!open) {
    return null;
  }

  const current = STEPS[Math.min(step, lastStep)]!;
  const isLast = step >= lastStep;

  return (
    // A light scrim (not an opaque cover) so the surfaces being described stay
    // visible behind the card. Above the transport (z-70) and meeting (z-50) but
    // below nothing else — it is the top-most teaching layer.
    <div
      className="fixed inset-0 z-[90] flex items-end justify-center p-4 sm:items-center"
      onClick={finish}
    >
      <div className="absolute inset-0 bg-ink-900/30" aria-hidden />
      <div
        ref={stepRef}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-labelledby="guided-tour-title"
        className="relative w-full max-w-lg rounded-lg border-2 border-ink-900 bg-paper-0 p-5 shadow-chrome-2 outline-none"
        onClick={(event) => {
          event.stopPropagation();
        }}
      >
        <div className="mb-3 flex items-start justify-between gap-3">
          <div>
            <div className="font-mono text-[10px] uppercase tracking-widest text-ink-500">
              Guided tour · {step + 1}/{STEPS.length}
            </div>
            <h2 id="guided-tour-title" className="text-xl">
              {current.title}
            </h2>
          </div>
          <button
            type="button"
            onClick={finish}
            aria-label="Close the guided tour"
            className="rounded-md border-2 border-ink-900 bg-paper-0 px-2.5 py-1 text-sm font-semibold text-ink-900 hover:bg-paper-2"
          >
            Skip
          </button>
        </div>

        <div className="min-h-[7rem]">{current.body}</div>

        <div className="mt-4 flex items-center justify-between gap-2">
          {/* Step dots — paired with the "n/N" label above so progress reads
              without relying on the dot fill alone (never hue-only). */}
          <div className="flex items-center gap-1.5" aria-hidden>
            {STEPS.map((_, index) => (
              <span
                key={index}
                className={
                  "h-2 w-2 rounded-full border border-ink-900 " +
                  (index === step ? "bg-ink-900" : "bg-paper-2")
                }
              />
            ))}
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={step === 0}
              onClick={() => {
                setStep((value) => Math.max(0, value - 1));
              }}
              className="rounded-md border-2 border-ink-900 bg-paper-0 px-3 py-1.5 text-sm font-semibold text-ink-900 transition-colors hover:bg-paper-2 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Back
            </button>
            <button
              type="button"
              onClick={() => {
                if (isLast) {
                  finish();
                } else {
                  setStep((value) => Math.min(lastStep, value + 1));
                }
              }}
              className="rounded-md border-2 border-ink-900 bg-ink-900 px-3 py-1.5 text-sm font-semibold text-paper-0 transition-colors hover:bg-ink-700"
            >
              {isLast ? "Start exploring" : "Next"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
