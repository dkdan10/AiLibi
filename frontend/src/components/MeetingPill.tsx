// The primary affordance for opening a meeting (DESIGN.md §5.1): a pill shown
// next to TickStepper only when the current replay has a meeting at the current
// tick. Clicking sets `selectedMeetingId`; it deliberately does NOT change the
// current tick (auto-seek is owned by 4.11). Hidden — not greyed-out — when no
// meeting sits at the current tick.

import { useReplayStore } from "../store/replayStore";

export function MeetingPill() {
  const replay = useReplayStore((s) => s.currentReplay);
  const currentTick = useReplayStore((s) => s.currentTick);
  const selectMeeting = useReplayStore((s) => s.selectMeeting);

  if (replay === null) {
    return null;
  }

  // currentTick is an index into replay.ticks; ticks[0] is the synthesized
  // tick=-1 "Start" frame, so match on the engine tick NUMBER at this index.
  const currentTickNumber = replay.ticks[currentTick]?.tick ?? -1;
  const meetingsHere = replay.meetings.filter((m) => m.tick === currentTickNumber);
  if (meetingsHere.length === 0) {
    return null;
  }

  return (
    <>
      {meetingsHere.map((meeting) => (
        <button
          key={meeting.meeting_id}
          type="button"
          onClick={() => {
            selectMeeting(meeting.meeting_id);
          }}
          className="rounded-full border border-amber-500 bg-amber-900/40 px-4 py-2 text-sm font-semibold text-amber-100 transition-colors hover:bg-amber-800/60"
        >
          Meeting @ tick {meeting.tick}
        </button>
      ))}
    </>
  );
}
