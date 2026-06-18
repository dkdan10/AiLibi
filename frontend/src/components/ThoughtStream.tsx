// ThoughtStream — the mind SLOT the App.tsx workspace mounts (Task 12.8;
// design/phase-12/stage-1-design.md §3.5, slice 6). The export name is preserved
// (App.tsx is out of scope — Wave-B mount discipline); the slot itself now just
// owns the right-rail chrome + the meeting gate and renders the new
// <MindInspector/> inside it.
//
// The rail mounts iff a meeting is selected: the per-agent memory + LLM I/O the
// inspector reads are meeting-boundary snapshots, so outside a meeting there is
// no inspector context and the rail stays hidden rather than floating empty over
// the map. It sits above the meeting modal (z-[60]) so the map + meeting overlay
// stay visible while drilling into an agent.

import { useReplayStore } from "../store/replayStore";
import { MindInspector } from "./MindInspector";

export function ThoughtStream() {
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const replay = useReplayStore((s) => s.currentReplay);

  if (meetingId === null || replay === null) {
    return null;
  }

  return (
    <aside
      aria-label="Mind inspector — agent reasoning"
      className="fixed right-0 top-0 z-[60] flex h-screen w-[30vw] min-w-[320px] max-w-[24rem] flex-col overflow-y-auto border-l-2 border-ink-900 bg-paper-1 p-4 text-ink-900 shadow-chrome-2"
    >
      <header className="mb-3">
        <h2 className="font-display text-lg font-semibold text-ink-900">
          Mind inspector
        </h2>
        <p className="text-xs text-ink-500">
          Per-agent belief, prompt, response, memory, and flags for the selected
          meeting.
        </p>
      </header>

      <MindInspector meetingId={meetingId} />
    </aside>
  );
}
