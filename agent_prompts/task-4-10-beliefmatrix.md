# Agent Prompt — 4.10 BeliefMatrix (who-suspects-whom heatmap)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.10 — BeliefMatrix (who-suspects-whom heatmap), anchored to DESIGN.md §6.3, DESIGN.md §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-beliefmatrix`
**Depends on:** 4.4 merged + mid-phase DTO audit passed + **4.8 merged** (App.tsx slot ordering) + **4.9 merged** (for `snapshot_tick` field rename)
**Section refs:** DESIGN.md §6.3, DESIGN.md §7
**Complexity:** Medium

N×N heatmap of who suspects whom at a meeting boundary. Rows are
observers, columns are subjects, cell color encodes suspicion
intensity (green→yellow→red). Derived client-side from per-agent
`AgentMemoryView` snapshots; the BeliefMatrix is visible only when
a meeting is selected, mirroring ThoughtStream's meeting-boundary
constraint.

**Why meeting-boundary-only, not per-tick.** The mid-phase DTO
audit's Section 6 substrate report confirmed `SuspicionGraphView`
is a declared DTO with NO endpoint today. Two paths existed:

1. **Add a backend endpoint** (`GET /replays/{game_id}/suspicion/
   {tick}`) that walks all agents' belief stores per-tick and
   serializes the graph. Widens 4.10 into a backend-and-frontend
   task; adds a loader method; touches `api/routes/`, `api/replay_
   loader.py`, and `api/schemas.py` (the SuspicionGraphView DTO
   already exists). Costs: ~3x the task surface; introduces
   per-tick memory reconstruction outside meeting boundaries
   (currently the loader only reconstructs at meeting boundaries
   per the substrate audit).

2. **Derive client-side from per-agent `AgentMemoryView`** fetched
   at the currently-selected meeting boundary. Each agent's
   `AgentMemoryView.beliefs[*]` already carries `(subject,
   suspicion, confidence, snapshot_tick)`. Aggregating N agents'
   beliefs gives the full N×N matrix at that meeting. No backend
   changes; reuses the existing `fetchMemoryView` action and
   memory cache.

This task picks Option 2 — keeps the scope at
`frontend/src/components/`, no backend touch. Per-tick coverage is
a Phase 5 expansion if the UX session shows it matters; meeting-
boundary coverage is sufficient for the merge gate (a non-technical
viewer following a game can see the suspicion landscape at every
decision point — i.e., every meeting).

**Out of scope** (explicit decisions deferred):

- **Per-tick suspicion graphs.** Per the design choice above.
- **Trust matrix variant.** DESIGN.md §6.3 distinguishes trust and
  suspicion as separate scores. The MVP heatmap renders suspicion
  only; a trust matrix is a Phase 5 expansion if useful.
- **Belief-edge animation between meetings.** A "watch beliefs
  shift from meeting 1 to meeting 2" view is compelling but out of
  scope.
- **Cell click → ThoughtStream pivot.** Clicking a cell could
  select the row agent and jump to ThoughtStream. Nice-to-have; out
  of MVP scope. Pivot via existing AgentSelector + BeliefMatrix
  side-by-side is fine.

**Files in scope:**
- frontend/src/components/BeliefMatrix.tsx
- frontend/src/components/BeliefCell.tsx
- frontend/src/App.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- api/
- frontend/src/store/replayStore.ts (uses existing fetchMemoryView)
- frontend/src/api/client.ts (frozen)
- frontend/src/types/api.ts (frozen — 4.9 already renamed the field)
- frontend/src/components/MapView.tsx
- frontend/src/components/MeetingView.tsx (lands in 4.6)
- frontend/src/components/ThoughtStream.tsx (lands in 4.8)
- frontend/src/components/AgentSelector.tsx (lands in 4.8 — reuse if available)
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
- [ ] **BeliefMatrix visible when `selectedMeetingId !== null`.** When the selection is null, the panel renders nothing (or a small hint similar to ThoughtStream's). Mounted in App.tsx alongside (or below) MeetingView / ThoughtStream depending on layout.
- [ ] **Per-agent memory fetch on mount + selection change.** For every `agent_id` in `currentReplay.players`, call `fetchMemoryView(selectedMeetingId, agent_id)` via the existing store action. The store caches and dedupes; subsequent renders hit the cache. Use a single `useEffect` keyed on `selectedMeetingId`.
- [ ] **Render the N×N matrix.** Rows: each player in `currentReplay.players`. Columns: same. Top row + left column: player color swatch + agent_id labels. Diagonal cell (observer = subject): blank or muted (an agent has no belief about itself).
- [ ] **Cell color encodes suspicion.** For row `i`, column `j` (i ≠ j): look up the row agent's `AgentMemoryView.beliefs.find(b => b.subject === players[j].agent_id)`. If found: cell color = a deterministic mapping of `suspicion ∈ [0,1]` to a heat scale. Recommended: HSL with hue = `120 - 120*suspicion` (green at 0, yellow at 0.5, red at 1.0); lightness adjustable by `confidence`. If not found (no belief recorded): cell is grey/empty.
- [ ] **Cell hover tooltip.** Hovering a cell shows `observer → subject: suspicion=0.72 (confidence=0.44)`. Use a simple title attribute or a Tailwind tooltip pattern (no new dependency).
- [ ] **Snapshot footer.** Below the matrix: a single line "All beliefs as of meeting tick N" derived from the snapshot_tick (4.9). All snapshot_tick values across all rendered cells are identical by construction; assert this in a defensive check (`new Set(allTicks).size === 1`) and log a warning if violated (data integrity hint).
- [ ] **Loading + partial states.** Until all N memory fetches resolve, render a loading state (e.g. "Loading agent memories..."). If any fetch errors, render the matrix with grey cells for missing rows and an error chip near the affected agent's label.
- [ ] **No new npm dependencies.** React 19, Zustand 5, Tailwind v4 are sufficient.
- [ ] **TypeScript strict.** No `any`, no `// @ts-ignore`.
- [ ] **`npm run build` succeeds** with zero warnings.
- [ ] **Screenshots attached to PR.** Minimum: BeliefMatrix populated for a meeting from a real replay, showing varied suspicion across cells (green/yellow/red distribution) and the snapshot tick footer.
- [ ] **Manual smoke documented.** PR description states the replay used and the meeting selected, and confirms the matrix populates with no console errors. Mention any cells that were grey (no belief recorded) so reviewers know that's the expected sparse state.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The matrix is a CSS grid (or a simple table). Pure React + Tailwind; no PixiJS.

Fetching pattern — orchestrate N parallel fetches via the store:

```tsx
export function BeliefMatrix() {
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const replay = useReplayStore((s) => s.currentReplay);
  const memoryCache = useReplayStore((s) => s.memoryCache);
  const fetchMemoryView = useReplayStore((s) => s.fetchMemoryView);

  const players = replay?.players ?? [];

  useEffect(() => {
    if (!meetingId) return;
    for (const p of players) fetchMemoryView(meetingId, p.agent_id);
  }, [meetingId, players, fetchMemoryView]);

  if (!meetingId) return null;
  const memories = players.map((p) => memoryCache[`${meetingId}:${p.agent_id}`]);
  if (memories.some((m) => !m)) return <Loading />;

  return <Matrix players={players} memories={memories} />;
}
```

Cell rendering with HSL heat:

```tsx
function BeliefCell({ observer, subject, belief }: Props) {
  if (observer.agent_id === subject.agent_id) {
    return <div className="bg-neutral-800" />;  // diagonal
  }
  if (!belief) {
    return <div className="bg-neutral-700" title="no belief recorded" />;
  }
  const hue = 120 - 120 * belief.suspicion;          // 120=green, 0=red
  const lightness = 30 + 20 * belief.confidence;     // more confident → lighter
  return (
    <div
      className="w-8 h-8 cursor-help"
      style={{ background: `hsl(${hue}, 70%, ${lightness}%)` }}
      title={`${observer.agent_id} → ${subject.agent_id}: suspicion=${belief.suspicion.toFixed(2)} (conf=${belief.confidence.toFixed(2)})`}
    />
  );
}
```

Belief lookup per `(observer, subject)` pair:

```typescript
function lookupBelief(memory: AgentMemoryView, subjectId: string) {
  return memory.beliefs.find((b) => b.subject === subjectId);
}
```

Defensive snapshot-tick check:

```typescript
const snapshotTicks = memories.flatMap((m) => m.beliefs.map((b) => b.snapshot_tick));
if (new Set(snapshotTicks).size > 1) {
  console.warn("BeliefMatrix: snapshot_tick values diverge across cells", snapshotTicks);
}
const footerTick = memories[0]?.tick ?? "?";
```

`memories[0].tick` is the AgentMemoryView's tick (always the meeting tick) — equivalent to snapshot_tick across all beliefs in this view; use it for the footer.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas.BeliefEntryView"`
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
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-4-beliefmatrix` with a title like `task 4.10: beliefmatrix (who-suspects-whom heatmap)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §6.3, DESIGN.md §7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
