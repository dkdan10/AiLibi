import { useEffect, useRef, useState } from "react";
import { evidenceDomId, observationSource, statementSource, type EvidenceSelection } from "../lib/evidence";
import { useReplayStore } from "../store/replayStore";
import { ClaimLine } from "../ui/ClaimLine";
import { ObservationLine } from "../ui/ObservationLine";

export function EvidenceLink({ target, children }: { target: EvidenceSelection; children: React.ReactNode }) {
  const select = useReplayStore((s) => s.selectEvidence);
  return <button type="button" className="rounded border border-ink-300 bg-paper-0 px-2 py-1 text-left text-xs text-ink-900 underline underline-offset-2 hover:bg-paper-2" onClick={() => select(target)}>{children}</button>;
}

/** The same evidence context follows a viewer out of the meeting onto the map. */
export function EvidencePanel({ inMeeting = false }: { inMeeting?: boolean }) {
  const target = useReplayStore((s) => s.selectedEvidence);
  const replay = useReplayStore((s) => s.currentReplay);
  const selectedMeeting = useReplayStore((s) => s.selectedMeetingId);
  const perspective = useReplayStore((s) => s.perspective);
  const cache = useReplayStore((s) => s.memoryCache);
  const errors = useReplayStore((s) => s.memoryErrors);
  const fetchMemory = useReplayStore((s) => s.fetchMemoryView);
  const panel = useRef<HTMLElement>(null);
  const [showMemory, setShowMemory] = useState(false);
  const meeting = replay?.meetings.find((m) => m.meeting_id === target?.meetingId);
  const source = target && meeting ? statementSource(meeting, target) : null;
  const observer = target?.kind === "observation" ? target.observerId : source?.turn.speaker ?? null;
  const canInspect = perspective.mode === "omniscient" || perspective.agentId === observer;
  const key = target && observer ? `${target.meetingId}:${observer}` : "";
  const memory = cache[key];
  const observation = target ? observationSource(memory, target) : null;
  const visible = target !== null && (inMeeting ? selectedMeeting !== null : selectedMeeting === null);

  useEffect(() => { if (visible) panel.current?.focus(); }, [target, visible]);
  useEffect(() => {
    if (visible && target && meeting && observer && canInspect) void fetchMemory(target.meetingId, observer);
  }, [visible, target, meeting, observer, canInspect, fetchMemory]);
  if (!visible || !target || !replay) return null;
  const sceneTick = target.kind === "observation" ? observation?.scene_tick ?? null : source ? meeting?.tick ?? null : null;
  // An evidence link may only seek an exact recorded frame, never a nearby one.
  const sceneIndex = sceneTick === null ? -1 : replay.ticks.findIndex((frame) => frame.tick === sceneTick);
  const missing = meeting === undefined || (target.kind !== "observation" && source === null) || (target.kind === "observation" && canInspect && memory !== undefined && observation === null);
  const store = useReplayStore.getState();
  const goToMeeting = () => {
    if (!meeting) return;
    const index = replay.ticks.findIndex((frame) => frame.tick === meeting.tick);
    if (index >= 0) store.setCurrentTick(index);
    store.selectMeeting(meeting.meeting_id);
  };
  return <section ref={panel} tabIndex={-1} aria-label="Selected evidence" className="mb-4 rounded-lg border-2 border-ink-900 bg-paper-0 p-4 text-ink-900 shadow-chrome-1 outline-none">
    <div className="flex items-start justify-between gap-3">
      <h3 className="text-lg">Check the source</h3>
      <button type="button" className="text-sm underline" onClick={() => store.selectEvidence(null)}>Close evidence</button>
    </div>
    <p className="mt-1 break-all font-mono text-xs">{target.id}</p>
    <p className="my-2 text-xs text-ink-500">A resolved citation identifies a source. It does not establish that the source supports the accusation.</p>
    {missing ? <p role="status">Reference unavailable in this recording and meeting. No substitute was selected.</p> : target.kind === "observation" ? !canInspect ? <p>This is {observer ?? "another agent"}'s private observation. Your current perspective stays unchanged.</p> : errors[key] ? <p role="status">Observation snapshot unavailable. <button type="button" className="underline" onClick={() => observer && void fetchMemory(target.meetingId, observer)}>Retry snapshot</button>
    </p> : !memory ? <p role="status">Loading the cited observation…</p> : observation ? <div>
      <p className="text-xs font-semibold">{observation.observer_id} · observation tick {observation.observation_tick} · {observation.provenance}</p>
      <p className="my-2 whitespace-pre-wrap">{observation.text}</p>
      <p className="text-xs text-ink-500">Scene frame {observation.scene_tick ?? "unavailable"}. Observation time and replay input-frame time use different boundaries.</p>
    </div> : null : source ? <div>
      <p className="text-xs font-semibold">{source.turn.speaker} · public {source.turn.turn_kind === "opt_in" ? "opt-in" : source.turn.turn_kind} · meeting tick {meeting?.tick}</p>{source.kind === "statement" ? <p className="my-2 whitespace-pre-wrap">{source.turn.free_text}</p> : source.kind === "claim" ? <ClaimLine claim={source.value} /> : <ObservationLine obs={source.value} />}</div> : null}
    <div className="mt-3 flex flex-wrap gap-2">
      {sceneIndex >= 0 && (target.kind !== "observation" || canInspect) && <button type="button" className="rounded border border-ink-900 px-3 py-1 text-sm" onClick={() => { store.setCurrentTick(sceneIndex); store.selectMeeting(null); }}>View scene frame {sceneTick}</button>}
      {meeting && <button type="button" className="rounded border border-ink-900 px-3 py-1 text-sm" onClick={goToMeeting}>Return to meeting and ballots</button>}
      {source && inMeeting && <button type="button" className="rounded border border-ink-900 px-3 py-1 text-sm" onClick={() => { const element = document.getElementById(evidenceDomId(target.id)); if (!element) return; let parent: HTMLElement | null = element.parentElement; while (parent) { if (parent instanceof HTMLDetailsElement) parent.open = true; parent = parent.parentElement; } element.scrollIntoView({ block: "center", behavior: "smooth" }); element.focus(); }}>Locate in transcript</button>}
      {observer && meeting && !canInspect && <button type="button" className="rounded border border-ink-900 px-3 py-1 text-sm" onClick={() => { store.setPerspective({ mode: "agent", agentId: observer }); store.selectAgent(observer); }}>Switch to {observer}'s perspective</button>}
      {observer && meeting && canInspect && <button type="button" aria-expanded={showMemory} className="rounded border border-ink-900 px-3 py-1 text-sm" onClick={() => setShowMemory(!showMemory)}>{showMemory ? "Hide" : "Open"} {observer}'s meeting memory</button>}
    </div>
    {showMemory && canInspect && observer && <div className="mt-3">
      <p className="text-xs font-semibold">{observer}'s memory at meeting tick {meeting?.tick}; this is what was available at that boundary, not at the earlier scene.</p>{memory ? <pre className="mt-2 max-h-80 overflow-auto whitespace-pre-wrap break-words rounded bg-paper-2 p-3 text-xs">{memory.rendered_memory_text}</pre> : <p role="status">Memory snapshot unavailable or loading.</p>}</div>}
  </section>;
}
