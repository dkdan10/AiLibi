// One captured LLM call (DESIGN.md §6.6, §7; api.schemas.LLMCallView, which
// shadows orchestrator.replay.LLMCallRecord). Header chip + model + template
// id, a token/cost stats row, and collapsed-by-default prompt + response
// sections. Native <details> keeps open/closed state out of React, matching the
// read-only spectator surface (the meeting cards use the same pattern).
//
// Task 6.7 windowing (audit K-K-1 / G-G-5, DESIGN.md §11.4): the prompt/response
// bodies are stripped from the bulk store payload, so they arrive empty here.
// Each card lazy-fetches its meeting on first expand via the store's
// `fetchMeeting`, then resolves its own body from the cached transcript. Props
// stay stable (`call: LLMCallView`) so the Phase 7 redesign can swap this file
// in place; the meeting/game context is read from the store, since the only
// renderer (ThoughtStream) is gated on a selected meeting.

import { useReplayStore } from "../store/replayStore";
import type { LLMCallView } from "../types/api";

const PREVIEW_LEN = 200;

// Kind chip colors are descriptive (meeting vs triggered check), not role-coded.
const KIND_STYLES: Record<LLMCallView["call_kind"], string> = {
  meeting: "bg-indigo-900/60 text-indigo-200 ring-indigo-600/60",
  trigger: "bg-teal-900/60 text-teal-200 ring-teal-600/60",
};

// Identify the same call inside a freshly-fetched (un-windowed) meeting. The
// windowed card retains every scalar field except the two text bodies, so the
// stable tuple below pins it to its transcript counterpart; calls identical on
// all of these have identical token/cost/template and are interchangeable.
function isSameCall(a: LLMCallView, b: LLMCallView): boolean {
  return (
    a.agent_id === b.agent_id &&
    a.call_kind === b.call_kind &&
    a.model === b.model &&
    a.prompt_template_id === b.prompt_template_id &&
    a.input_tokens === b.input_tokens &&
    a.output_tokens === b.output_tokens &&
    a.cost_usd === b.cost_usd
  );
}

// Collapsed: a 200-char preview + "show more". Expanded: the full text in a
// scrollable monospace block, no truncation. `group-open:` swaps the preview
// for the full block so the teaser never doubles up with the expanded text.
// `body` is undefined until the meeting is lazy-fetched; expanding triggers the
// fetch (onExpand) and shows a loading placeholder until it lands.
function CollapsibleText({
  label,
  body,
  onExpand,
}: {
  label: string;
  body: string | undefined;
  onExpand: () => void;
}) {
  const loaded = body !== undefined;
  const truncated = loaded && body.length > PREVIEW_LEN;
  const preview = loaded ? (truncated ? body.slice(0, PREVIEW_LEN) : body) : "";

  return (
    <details
      className="group mt-2 rounded border border-neutral-700 bg-neutral-900/60"
      onToggle={(event) => {
        if (event.currentTarget.open) {
          onExpand();
        }
      }}
    >
      <summary className="cursor-pointer select-none px-2 py-1 text-xs">
        <span className="font-semibold uppercase tracking-wide text-neutral-400">
          {label}
        </span>
        <span className="ml-2 text-sky-400 group-open:hidden">show more</span>
        <span className="ml-2 hidden text-sky-400 group-open:inline">show less</span>
        <span className="mt-1 block whitespace-pre-wrap break-words font-mono text-neutral-400 group-open:hidden">
          {preview}
          {truncated ? "…" : ""}
        </span>
      </summary>
      <pre className="max-h-80 overflow-auto whitespace-pre-wrap break-words border-t border-neutral-700 px-2 py-2 font-mono text-xs text-neutral-200">
        {loaded ? body : "Loading…"}
      </pre>
    </details>
  );
}

export function LLMCallCard({ call }: { call: LLMCallView }) {
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const cachedMeeting = useReplayStore((s) =>
    meetingId === null ? undefined : s.meetingCache[meetingId],
  );
  const fetchMeeting = useReplayStore((s) => s.fetchMeeting);

  // The full (un-windowed) counterpart once its meeting has been fetched.
  const fullCall = cachedMeeting?.llm_calls.find((other) => isSameCall(other, call));

  const onExpand = () => {
    if (meetingId !== null) {
      void fetchMeeting(meetingId);
    }
  };

  return (
    <article className="rounded-lg border border-neutral-700 bg-neutral-800/40 p-3">
      <header className="flex flex-wrap items-center gap-2">
        <span
          className={
            "inline-flex items-center rounded px-1.5 py-0.5 text-xs font-semibold uppercase tracking-wide ring-1 " +
            KIND_STYLES[call.call_kind]
          }
        >
          {call.call_kind}
        </span>
        <span className="font-mono text-xs text-neutral-300">{call.model}</span>
        <span className="font-mono text-xs text-neutral-500">
          {call.prompt_template_id}
        </span>
      </header>

      <dl className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-neutral-400">
        <div>
          <span className="text-neutral-500">in</span>{" "}
          <span className="font-mono text-neutral-200">{call.input_tokens}</span> tok
        </div>
        <div>
          <span className="text-neutral-500">out</span>{" "}
          <span className="font-mono text-neutral-200">{call.output_tokens}</span> tok
        </div>
        <div>
          <span className="text-neutral-500">cost</span>{" "}
          <span className="font-mono text-neutral-200">
            ${call.cost_usd.toFixed(4)}
          </span>
        </div>
      </dl>

      <CollapsibleText label="Prompt" body={fullCall?.prompt_text} onExpand={onExpand} />
      <CollapsibleText
        label="Response"
        body={fullCall?.response_text}
        onExpand={onExpand}
      />
    </article>
  );
}
