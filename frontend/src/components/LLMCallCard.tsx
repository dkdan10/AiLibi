// One captured LLM call, rendered as a single FIELD (Task 12.8; the mind
// inspector's Prompt / Response tabs). The header carries the role-neutral
// call-kind chip + model + template id + the token/cost stats; the body is the
// VERBATIM `LLMCallView.prompt_text` or `response_text` in a mono block — the
// exact text the LLM saw / returned, never truncated or paraphrased (the brief's
// "mono for prompt / response / JSON"). The connected inspector fetches the
// un-windowed meeting (Task 6.7 windowing strips the bodies from the bulk
// payload, DESIGN.md §11.4), so when `body` is the windowed empty string this
// card shows a "loading" placeholder rather than a blank pre.

import { tokens } from "../tokens";
import type { LLMCallView } from "../types/api";

// Kind chip label is descriptive (meeting vs triggered check), not role-coded —
// it carries no crew/impostor signal (firewall: never encode guilt in chrome).
const KIND_LABEL: Record<LLMCallView["call_kind"], string> = {
  meeting: "meeting",
  trigger: "trigger",
};

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="text-ink-500">{label}</span>{" "}
      <span className="font-mono text-ink-900">{value}</span>
    </div>
  );
}

export function LLMCallCard({
  call,
  field,
}: {
  call: LLMCallView;
  field: "prompt" | "response";
}) {
  const body = field === "prompt" ? call.prompt_text : call.response_text;
  const loaded = body !== "";

  return (
    <article className="rounded-md border-2 border-ink-900 bg-paper-0 shadow-chrome-1">
      <header className="flex flex-wrap items-center gap-2 border-b-2 border-ink-900 px-3 py-2">
        <span
          className="inline-flex items-center rounded-pill border-2 border-ink-900 px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wide text-ink-900"
          style={{ background: tokens.paper[2] }}
        >
          {KIND_LABEL[call.call_kind]}
        </span>
        <span className="font-mono text-xs text-ink-700">{call.model}</span>
        <span className="truncate font-mono text-[10px] text-ink-400">
          {call.prompt_template_id}
        </span>
      </header>

      <dl className="flex flex-wrap gap-x-4 gap-y-1 border-b border-ink-200 px-3 py-1.5 text-[11px] text-ink-700">
        <Stat label="in" value={`${call.input_tokens} tok`} />
        <Stat label="out" value={`${call.output_tokens} tok`} />
        <Stat label="cost" value={`$${call.cost_usd.toFixed(4)}`} />
      </dl>

      {loaded ? (
        <pre className="max-h-[28rem] overflow-auto whitespace-pre-wrap break-words px-3 py-2 font-mono text-xs leading-relaxed text-ink-900">
          {body}
        </pre>
      ) : (
        <p className="flex items-center gap-2 px-3 py-3 text-xs italic text-ink-500">
          <span
            aria-hidden
            className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-ink-200 border-t-ink-700"
          />
          Loading {field}…
        </p>
      )}
    </article>
  );
}
