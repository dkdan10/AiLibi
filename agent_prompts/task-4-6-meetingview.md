# Agent Prompt — 4.6 MeetingView (reports, statements, ballots, contradictions)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.6 — MeetingView (reports, statements, ballots, contradictions), anchored to DESIGN.md §5, DESIGN.md §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-meetingview`
**Depends on:** 4.4 merged + mid-phase DTO audit passed
**Section refs:** DESIGN.md §5, DESIGN.md §7
**Complexity:** Medium

Transcript renderer for one meeting: reports + accusation-round
statements + ballots + contradiction flags + a small metadata footer
(prompt versions, total cost). Activated when the spectator selects
a meeting via the store's `selectedMeetingId`. The store already
holds `selectMeeting(id | null)` from 4.3; this task wires the UI.

**Layout choice — overlay vs replace.** The MeetingView is a focused
reading surface — there's no reason to render alongside the map at
small viewport widths. Recommendation: render as a modal-style
overlay (full-canvas dim + centered panel) when `selectedMeetingId
!== null`, with a close button that clears the selection. This keeps
MapView's PixiJS canvas un-touched (no unmount cost) and gives the
reading surface the screen real estate it needs. The implementing
agent may pick the side-by-side split-view alternative if the
viewport calculation justifies it; document the choice in `##
Decisions`.

**Meeting-trigger discovery.** A "Meeting" pill / button appears
next to TickStepper when `currentReplay.meetings.some(m => m.tick
=== currentTick)`. Clicking it calls `selectMeeting(m.meeting_id)`.
This is the primary UI affordance for opening a meeting; users can
also scroll to a meeting tick first (via TickStepper) and then click
the pill. 4.11 (ReplayControls) adds a "next meeting" snap-to button
that calls both `setCurrentTick(m.tick)` and `selectMeeting(m.id)`
in one action.

**Out of scope** (explicit decisions deferred):

- **Meeting search / filter UI.** N meetings per game is typically
  ≤ 3 in MVP scope; pagination / search would be premature.
- **Inline LLM call drilldown.** The meeting metadata footer lists
  `total_cost_usd` and `llm_call` count; the actual prompt / response
  text drilldown happens in 4.8 (ThoughtStream), keyed by
  `selectedAgentId`. Don't duplicate the LLM call rendering here.
- **Contradiction graph view.** Contradictions render as inline
  badges inside the affected statements / reports; a separate
  contradiction-network visualization is out of scope.
- **Editable / interactive transcript.** Read-only render. The
  spectator does not vote, accuse, or annotate.
- **Translations / TTS.** Free text renders as-is.

**Files in scope:**
- frontend/src/components/MeetingView.tsx
- frontend/src/components/ReportCard.tsx
- frontend/src/components/StatementCard.tsx
- frontend/src/components/BallotCard.tsx
- frontend/src/components/ContradictionBadge.tsx
- frontend/src/components/MeetingPill.tsx
- frontend/src/App.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- api/
- frontend/src/store/replayStore.ts (frozen)
- frontend/src/api/client.ts (frozen)
- frontend/src/types/api.ts (frozen)
- frontend/src/components/MapView.tsx
- frontend/src/components/AgentToken.tsx
- frontend/src/components/RoomRect.tsx
- frontend/src/components/VentEdge.tsx (lands in 4.5)
- frontend/src/components/BodyMarker.tsx (lands in 4.5)
- frontend/src/components/SabotageOverlay.tsx (lands in 4.5)
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/TickStepper.tsx
- frontend/package.json (locked at 4.3)
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
- [ ] **MeetingPill in TickStepper-adjacent slot.** When the current replay has a meeting at `currentTick`, a button labeled `Meeting @ tick N` is visible and clickable. Click → `selectMeeting(meeting_id)`. When no meeting is at currentTick, the pill is hidden (not greyed-out).
- [ ] **MeetingView mounts iff `selectedMeetingId !== null`.** The view fetches the meeting from `currentReplay.meetings.find(m => m.meeting_id === selectedMeetingId)`. If the meeting isn't found (e.g. stale selection after replay switch), call `selectMeeting(null)` and render nothing. Renders an overlay with a close button (`selectMeeting(null)`) and the transcript.
- [ ] **Reports section.** One `ReportCard` per item in `meeting.reports`. Card header: `agent_id` + reporter color swatch (from `currentReplay.players[].color`) + tick. Body: `free_text` foregrounded in a larger / readable font. Below: collapsed-by-default structured detail — observations list (one row per `ObservationClaimView`, discriminated render: `saw_player` shows subject + room + co_present; `completed_task` shows task_id + room; `found_body` shows body_of + room) and claims list (one row per `StatementClaimView`, similarly discriminated).
- [ ] **Statements section, grouped by round.** Group `meeting.statements` by `round_index`. Render rounds in numeric order. Within a round, statements in their original order (one per speaker per round). Each `StatementCard` shows: speaker (with color swatch), target (if non-null, as a chip; if null, "general" or omitted), `free_text` foregrounded, claims collapsed-by-default. Contradictions reference a `contradiction_id` — render a small `ContradictionBadge` inline next to any claim implicated.
- [ ] **Ballots section.** One `BallotCard` per item in `meeting.ballots`. Voter color swatch + voter id; target (player id with color swatch, or the literal text "SKIP" with neutral styling); confidence rendered as a horizontal bar (0.0–1.0 width); `rationale_text` foregrounded. Tally summary at the section header: e.g. `p-2: 2 votes · p-5: 1 vote · SKIP: 0 votes`.
- [ ] **Contradictions inline + summary.** Each `ContradictionView` renders as a `ContradictionBadge` (small chip with `kind` color-coded). The badge appears (a) inline next to any report / statement whose `event_a_id` or `event_b_id` matches, and (b) in a `Contradictions` summary section at the bottom of the meeting overlay, listing all contradictions with their `description` text and involved `subjects`.
- [ ] **Outcome banner.** Top of the overlay: large prominent banner showing `outcome` (`EJECTED` or `SKIPPED`) and, if ejected, the player name + color. Includes triggered-by (`triggered_by` agent + `trigger_kind`).
- [ ] **Metadata footer.** Small footer (collapsible / muted styling): `meeting_id`, `tick`, `total_cost_usd` (formatted as `$0.0123`), `prompt_versions` rendered as a `key: value` list (e.g. `crewmate_report: crewmate_report.v1`, one per line). `llm_call` count rendered as `N LLM calls (drill into ThoughtStream for details)`.
- [ ] **App.tsx layout updated.** Pill rendered near TickStepper. Overlay mounted at the App root (above all other content via z-index or React Portal). Pre-existing MapView / ReplayPicker / TickStepper remain intact.
- [ ] **No new npm dependencies.** React 19, Zustand 5, Tailwind v4 from 4.3 are sufficient. No PixiJS in this component (it's pure DOM).
- [ ] **TypeScript strict.** No `any`, no `// @ts-ignore`.
- [ ] **`npm run build` succeeds** with zero warnings.
- [ ] **Screenshots attached to PR.** Minimum: (a) MeetingPill visible on the map view at a meeting tick, (b) the open MeetingView overlay for that meeting showing at least one report, statements across both rounds, ballots with a clear tally, and the outcome banner.
- [ ] **Manual smoke documented.** PR description states the replay used (any of `replays/replay-seed-{22,24,26,49}.jsonl` from the Phase 3 eval — those are the 4 games with meetings; pick whichever is in `$AILIBI_REPLAY_DIR`), the meeting opened, and confirms all four card types render without console errors.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

MeetingView is pure React + Tailwind — no PixiJS. The overlay pattern:

```tsx
export function MeetingView() {
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const replay = useReplayStore((s) => s.currentReplay);
  const selectMeeting = useReplayStore((s) => s.selectMeeting);
  if (!meetingId || !replay) return null;
  const meeting = replay.meetings.find((m) => m.meeting_id === meetingId);
  if (!meeting) {
    selectMeeting(null);
    return null;
  }
  return (
    <div className="fixed inset-0 bg-black/70 z-50 overflow-auto">
      <div className="max-w-4xl mx-auto my-8 bg-neutral-900 rounded p-6">
        <OutcomeBanner meeting={meeting} players={replay.players} />
        <ReportsSection reports={meeting.reports} players={replay.players} />
        <StatementsSection statements={meeting.statements} contradictions={meeting.contradictions} players={replay.players} />
        <BallotsSection ballots={meeting.ballots} players={replay.players} />
        <ContradictionsSection contradictions={meeting.contradictions} />
        <MetadataFooter meeting={meeting} />
      </div>
    </div>
  );
}
```

Grouping statements by round:

```tsx
function StatementsSection({ statements, contradictions, players }: Props) {
  const byRound = new Map<number, StatementView[]>();
  for (const s of statements) {
    if (!byRound.has(s.round_index)) byRound.set(s.round_index, []);
    byRound.get(s.round_index)!.push(s);
  }
  const rounds = [...byRound.keys()].sort((a, b) => a - b);
  return rounds.map((r) => (
    <RoundSection key={r} round={r} statements={byRound.get(r)!} ... />
  ));
}
```

Contradiction-to-statement linking: build a `Set<string>` of contradiction event ids; check each statement's `statement_id` against `event_a_id` / `event_b_id`.

Color swatch helper — re-use the deterministic-hash pattern from 4.4's `RoomRect`:

```typescript
function playerColor(agentId: string, players: PlayerView[]) {
  return players.find((p) => p.agent_id === agentId)?.color ?? "#888";
}
```

Discriminated-union render for ObservationClaimView:

```tsx
function ObservationLine({ obs }: { obs: ObservationClaimView }) {
  switch (obs.type) {
    case "saw_player": return <span>saw {obs.subject} in {obs.room} (with {obs.co_present.join(", ")})</span>;
    case "completed_task": return <span>completed {obs.task_id} in {obs.room}</span>;
    case "found_body": return <span>found body of {obs.body_of} in {obs.room}</span>;
  }
}
```

TypeScript's discriminated union narrowing makes this exhaustive.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import api.main"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-4-meetingview` with a title like `task 4.6: meetingview (reports, statements, ballots, contradictions)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5, DESIGN.md §7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
