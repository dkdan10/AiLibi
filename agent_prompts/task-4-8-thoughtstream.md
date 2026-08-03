# Agent Prompt — 4.8 ThoughtStream (per-agent memory + LLM call viewer)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.8 — ThoughtStream (per-agent memory + LLM call viewer), anchored to DESIGN.md §6, DESIGN.md §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-thoughtstream`
**Depends on:** 4.4 merged + mid-phase DTO audit passed + **4.6 merged** (for App.tsx slot ordering) + **4.7 merged** (for per-call `agent_id` attribution)
**Section refs:** DESIGN.md §6, DESIGN.md §7
**Complexity:** Medium

Per-agent reasoning viewer. Spectator selects an agent (in addition
to a meeting); sees that agent's rendered memory view + every LLM
call that agent originated during the selected meeting. Memory comes
from the existing `AgentMemoryView` endpoint (cached in the store);
LLM calls come from `MeetingView.llm_calls` filtered by `agent_id`
(which 4.7 added).

**Privileged spectator note.** Per the 4.1 privilege model and the
mid-phase audit's Class A summary, the agent's `role` is
intentionally exposed in `AgentMemoryView.role` because the
spectator IS privileged (post-game replay). The `rendered_memory_
text` correctly carries only the *selected* agent's role, not other
agents' roles (cross-agent contamination check passed in both
audits). ThoughtStream therefore renders the role badge without
guarding — it's an authorized view by design.

**Meeting + agent selection coupling.** ThoughtStream is meaningful
only when BOTH `selectedMeetingId !== null` and `selectedAgentId
!== null`. When either is null, the panel renders a hint ("Open a
meeting and pick an agent to see their reasoning"). The
`AgentSelector` is the new affordance for picking — a button row
showing every player in `currentReplay.players` keyed by color
swatch + agent_id. Clicking selects that agent.

**Out of scope** (explicit decisions deferred):

- **Between-meeting memory.** MVP exposes `AgentMemoryView` only at
  meeting boundaries (4.1 decision). ThoughtStream therefore only
  shows memory snapshots paired with the currently-selected meeting.
  Per-tick memory streams are a Phase 5 concern.
- **Diff view between meetings.** "How did p-2's beliefs change
  between meeting 1 and meeting 2?" is a compelling feature but out
  of MVP scope — it would need cross-meeting state coordination.
- **LLM call rerun / replay.** No "re-run this prompt" button. The
  view is read-only.
- **Inline prompt-template source view.** The prompt_template_id is
  shown as text (e.g. `crewmate_report.v1`); a link to the
  underlying jinja2 template is out of scope.
- **Filter / search over many LLM calls.** A typical meeting has 12
  LLM calls (3 reports + 6 statements + 3 votes); too few to warrant
  search.

**Files in scope:**
- frontend/src/components/ThoughtStream.tsx
- frontend/src/components/AgentSelector.tsx
- frontend/src/components/MemoryPanel.tsx
- frontend/src/components/BeliefRow.tsx
- frontend/src/components/LLMCallCard.tsx
- frontend/src/App.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- api/
- frontend/src/store/replayStore.ts (already has selectAgent + fetchMemoryView)
- frontend/src/api/client.ts (frozen)
- frontend/src/types/api.ts (frozen — 4.7 added agent_id; 4.8 only consumes)
- frontend/src/components/MapView.tsx
- frontend/src/components/MeetingView.tsx (lands in 4.6)
- frontend/src/components/RoomRect.tsx
- frontend/src/components/AgentToken.tsx
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/TickStepper.tsx
- frontend/package.json (locked)
- DESIGN.md
- AGENT_IMPLEMENTATION.md
- pyproject.toml
- uv.lock
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- scripts/
- tests/

**Definition of done:**
- [ ] **AgentSelector visible when `selectedMeetingId !== null`.** Renders one button per `currentReplay.players` entry. Each button: color swatch + `display_name` + `agent_id` + a small "(IMPOSTOR)" / "(CREWMATE)" badge in muted text (role is privileged-spectator info). Click → `selectAgent(agent_id)`. The selected button is visually highlighted. When `selectedMeetingId === null`, the selector is hidden.
- [ ] **ThoughtStream panel visible when both selections present.** Layout: AgentSelector at top, then MemoryPanel, then a divider, then the LLM call list. Panel docks to a side (right rail, ~30% viewport width) so MapView + MeetingView remain visible if open. Implementing agent picks layout; document.
- [ ] **MemoryPanel renders `AgentMemoryView`.** Fetched via `fetchMemoryView(meetingId, agentId)`; loading state shows a spinner; error state shows the cached error. Fields rendered: role badge, `tasks_completed / tasks_assigned` (formatted `7 / 12`), observations as a list (newest first, discriminated by `type`), beliefs as a `BeliefRow` per `BeliefEntryView` (subject + suspicion bar + confidence pill), open_contradictions as inline `ContradictionBadge` entries (component shared with 4.6 — implementing agent: if 4.6 already merged, reuse; otherwise define locally and refactor in a follow-up).
- [ ] **`rendered_memory_text` collapsible.** Below the structured memory: a `<details>` block (closed by default) labeled "Raw rendered memory (sent to LLM)". When expanded, shows the raw `rendered_memory_text` in a monospace preformatted block. Useful for debugging prompt-render decisions.
- [ ] **LLM call list filtered to agent.** `meeting.llm_calls.filter(c => c.agent_id === selectedAgentId)` — depends on 4.7. Render each remaining call as an `LLMCallCard`.
- [ ] **`LLMCallCard` content.** Header: `call_kind` chip + `model` + `prompt_template_id`. Stats row: input tokens, output tokens, `cost_usd` (formatted `$0.0042`). Prompt section: collapsible (closed by default), monospace preformatted, no truncation when expanded — first 200 chars shown when collapsed with a "show more" hint. Response section: same pattern.
- [ ] **Fallback for old replays without `agent_id`.** When `selectedAgentId !== null` but `meeting.llm_calls` contains entries with `agent_id === null` (pre-4.7 replays), render a single "Older replay — per-call agent attribution unavailable" notice instead of an empty list. Do not crash.
- [ ] **No new npm dependencies.** Reuse what 4.3/4.4/4.5/4.6 already pinned.
- [ ] **TypeScript strict.** No `any`, no `// @ts-ignore`.
- [ ] **`npm run build` succeeds** with zero warnings.
- [ ] **Screenshots attached to PR.** Minimum: (a) AgentSelector visible with one agent highlighted, (b) ThoughtStream panel populated showing role badge, beliefs, and at least one expanded LLM call card with prompt + response visible.
- [ ] **Manual smoke documented.** PR description states the replay used (any of `replays/replay-seed-{22,24,26,49}.jsonl`), the meeting + agent selected, and confirms memory loads + at least 3 LLM calls render attributed to the picked agent.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Memory fetch pattern using the existing store:

```tsx
export function ThoughtStream() {
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const agentId = useReplayStore((s) => s.selectedAgentId);
  const memoryCache = useReplayStore((s) => s.memoryCache);
  const fetchMemoryView = useReplayStore((s) => s.fetchMemoryView);
  const replay = useReplayStore((s) => s.currentReplay);

  useEffect(() => {
    if (meetingId && agentId) fetchMemoryView(meetingId, agentId);
  }, [meetingId, agentId, fetchMemoryView]);

  if (!meetingId || !agentId) {
    return <Hint>Open a meeting and pick an agent to see their reasoning.</Hint>;
  }
  const memory = memoryCache[`${meetingId}:${agentId}`];
  if (!memory) return <Spinner />;
  const meeting = replay?.meetings.find((m) => m.meeting_id === meetingId);
  const calls = meeting?.llm_calls.filter((c) => c.agent_id === agentId) ?? [];

  return (
    <aside className="...">
      <RoleBadge role={memory.role} />
      <TaskProgress completed={memory.tasks_completed} assigned={memory.tasks_assigned} />
      <ObservationsList observations={memory.observations} />
      <BeliefsList beliefs={memory.beliefs} />
      <ContradictionsList contradictions={memory.open_contradictions} />
      <RenderedMemoryDetails text={memory.rendered_memory_text} />
      <LLMCallList calls={calls} agentId={agentId} meeting={meeting} />
    </aside>
  );
}
```

Belief row visualization — suspicion as a horizontal bar:

```tsx
function BeliefRow({ belief }: { belief: BeliefEntryView }) {
  return (
    <div className="flex items-center gap-2">
      <span className="font-mono">{belief.subject}</span>
      <div className="flex-1 h-2 bg-neutral-700 rounded">
        <div
          className="h-full rounded"
          style={{
            width: `${belief.suspicion * 100}%`,
            background: belief.suspicion > 0.5 ? "var(--color-red)" : "var(--color-green)",
          }}
        />
      </div>
      <span className="text-xs text-neutral-400">{belief.suspicion.toFixed(2)}</span>
    </div>
  );
}
```

LLM call collapsible content — use native `<details>` to avoid managing open/closed state:

```tsx
function LLMCallCard({ call }: { call: LLMCallView }) {
  return (
    <div className="border rounded p-2 my-2">
      <header>...stats...</header>
      <details>
        <summary>Prompt ({truncate(call.prompt_text, 80)})</summary>
        <pre className="whitespace-pre-wrap">{call.prompt_text}</pre>
      </details>
      <details>
        <summary>Response ({truncate(call.response_text, 80)})</summary>
        <pre className="whitespace-pre-wrap">{call.response_text}</pre>
      </details>
    </div>
  );
}
```

For the contradiction badge shared with 4.6: if 4.6's `ContradictionBadge` component already exists at merge time, import and reuse. If 4.6 has not yet merged, define a local copy and note in `## Decisions` that a refactor follow-up will deduplicate. Don't block on inter-task ordering — both tasks can dispatch in parallel after 4.7 and the audit clear.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.main"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-4-thoughtstream` with a title like `task 4.8: thoughtstream (per-agent memory + llm call viewer)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §6, DESIGN.md §7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
