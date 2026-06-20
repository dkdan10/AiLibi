// ThoughtStream — the mind SLOT the App.tsx workspace mounts (Task 12.8;
// design/phase-12/stage-1-design.md §3.5, slice 6). The export name is preserved
// (App.tsx mounts <ThoughtStream/>); the slot owns the right-rail chrome + the
// meeting gate and renders the new <MindInspector/> inside it.
//
// The rail mounts iff a meeting is selected: the per-agent memory + LLM I/O the
// inspector reads are meeting-boundary snapshots, so outside a meeting there is
// no inspector context and the rail stays hidden rather than floating empty over
// the map.
//
// Task 12.11 overlay coordination: the rail is part of ONE meeting-mode layout,
// not a colliding `fixed` overlay. It sits at z-[55] (above the masked meeting at
// z-50, below the transport at z-70) and stops at the MEASURED `--transport-h`
// so it never slides under the transport. At xl+ it is a persistent 24rem rail
// that lands in the gutter the MeetingView reserves (`xl:pr-[26rem]`), so it
// never overlaps the Ballots column. Below xl there is no room beside the
// transcript, so it collapses to a slide-in drawer toggled by an edge tab.

import { useEffect, useState } from "react";

import { useReplayStore } from "../store/replayStore";
import { MindInspector } from "./MindInspector";

export function ThoughtStream() {
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const replay = useReplayStore((s) => s.currentReplay);
  const [mobileOpen, setMobileOpen] = useState(false);
  // Track the xl breakpoint (Tailwind default 80rem) so the closed drawer can be
  // made `inert` ONLY below xl — at xl+ the rail is a persistent, interactive
  // column and must never be inert.
  const [isXl, setIsXl] = useState(
    () =>
      typeof window !== "undefined" &&
      window.matchMedia("(min-width: 80rem)").matches,
  );
  useEffect(() => {
    const mq = window.matchMedia("(min-width: 80rem)");
    const onChange = (): void => {
      setIsXl(mq.matches);
    };
    onChange();
    mq.addEventListener("change", onChange);
    return () => {
      mq.removeEventListener("change", onChange);
    };
  }, []);

  // Reset the narrow-screen drawer whenever the open meeting changes, so jumping
  // to a new meeting doesn't leave a stale drawer open over the fresh transcript.
  useEffect(() => {
    setMobileOpen(false);
  }, [meetingId]);

  if (meetingId === null || replay === null) {
    return null;
  }

  // Closed on narrow (slide off-screen), always shown on xl+. Open → shown.
  const railTransform = mobileOpen
    ? "translate-x-0"
    : "translate-x-full xl:translate-x-0";
  // Below xl, a closed drawer is only translated off-screen — keep its still-
  // mounted controls out of the focus order (and the a11y tree) so keyboard users
  // can't tab into the invisible panel; never inert at xl+, where it is visible.
  const drawerInert = !isXl && !mobileOpen;

  return (
    <>
      {/* Narrow-screen toggle (an edge tab). Hidden at xl+, where the rail is
          persistent. */}
      <button
        type="button"
        onClick={() => {
          setMobileOpen((value) => !value);
        }}
        aria-expanded={mobileOpen}
        aria-controls="mind-inspector-rail"
        className="fixed right-0 top-1/2 z-[56] -translate-y-1/2 rounded-l-md border-2 border-r-0 border-ink-900 bg-paper-0 px-2 py-3 text-xs font-semibold text-ink-900 shadow-chrome-1 [writing-mode:vertical-rl] hover:bg-paper-2 xl:hidden"
      >
        {mobileOpen ? "Close mind ›" : "‹ Mind inspector"}
      </button>

      <aside
        id="mind-inspector-rail"
        aria-label="Mind inspector — agent reasoning"
        inert={drawerInert}
        style={{ bottom: "var(--transport-h, 16rem)" }}
        className={
          "fixed right-0 top-0 z-[55] flex w-full max-w-[24rem] flex-col overflow-y-auto border-l-2 border-ink-900 bg-paper-1 p-4 text-ink-900 shadow-chrome-2 transition-transform duration-200 motion-reduce:transition-none " +
          railTransform
        }
      >
        <header className="mb-3 flex items-start justify-between gap-2">
          <div>
            <h2 className="font-display text-lg font-semibold text-ink-900">
              Mind inspector
            </h2>
            <p className="text-xs text-ink-500">
              Per-agent belief, prompt, response, memory, and flags for the
              selected meeting.
            </p>
          </div>
          <button
            type="button"
            onClick={() => {
              setMobileOpen(false);
            }}
            aria-label="Close the mind inspector"
            className="shrink-0 rounded-md border-2 border-ink-900 bg-paper-0 px-2 py-0.5 text-xs font-semibold text-ink-900 hover:bg-paper-2 xl:hidden"
          >
            Close
          </button>
        </header>

        <MindInspector meetingId={meetingId} />
      </aside>
    </>
  );
}
