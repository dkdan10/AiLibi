# Agent Prompt — 12.8 Mind inspector

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-12.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 12.8 — Mind inspector, anchored to design/phase-12/stage-1-design.md §3.5, slice 6; the firewall + Omniscient-gating rules in `design/phase-12/claude-design-brief.md`. NO converge screen exists for this surface — it needs a NEW Claude-Design pass (grounded on the brief + `tokens-seed`, via the §9.5 handoff; not a sync).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-12.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-12-mind-inspector`
**Depends on:** 12.1, 12.2, 12.3, 12.4
**Section refs:** design/phase-12/stage-1-design.md §3.5, slice 6; the firewall + Omniscient-gating rules in `design/phase-12/claude-design-brief.md`. NO converge screen exists for this surface — it needs a NEW Claude-Design pass (grounded on the brief + `tokens-seed`, via the §9.5 handoff; not a sync).
**Complexity:** Integration
**Files in scope:**
- frontend/src/components/MindInspector.tsx
- frontend/src/components/ThoughtStream.tsx
- frontend/src/components/MemoryPanel.tsx
- frontend/src/components/LLMCallCard.tsx
- frontend/src/components/AgentSelector.tsx
- frontend/src/stories/MindInspector.stories.tsx
**Files NOT in scope:**
- frontend/src/App.tsx — the mind slot already mounts `<ThoughtStream/>`; keep that export and render `MindInspector` inside it, don't edit the shell (Wave-B mount discipline)
- api/ and the loader — `LLMCallView` (`prompt_text` / `response_text`), `AgentMemoryView`, `ContradictionView`, and the omniscient ground truth (`PlayerView.role`, `KillEventView`) already ship; no DTO change, no re-record
- the map / meeting / belief surfaces — other Wave-B slices

Rebuild the mind slot: keep the `ThoughtStream` export (the slot the App.tsx workspace mounts) and have it render a new
`MindInspector` — a tabbed per-agent panel. **Belief** (this agent's suspicion / trust of each other player, with the
meeting steps — the per-agent reasoning *detail*, complementary to 12.6's cross-agent matrix, NOT a duplicate) ·
**Prompt** (`LLMCallView.prompt_text` — the exact text the LLM saw, mono) · **Response** (`LLMCallView.response_text`,
mono) · **Memory** (`AgentMemoryView` episodic feed: saw_player / saw_body / heard_* / `own_kill`) · **Flags**
(contradictions / markers affecting them, from `ContradictionView`) — plus a **Thought → Action → Observation** trail per
decision. A **"show what they saw"** control drives the store (`setPerspective(agent)` + `selectAgent`) so the 12.5 map
fogs to that agent — no map edit, the map already reacts. **Impostor extras** (`fellow_impostor_ids`, the `own_kill` memory line, and the cover-task marked **fabricated**) are
gated **Omniscient OR when the perspective lens IS the inspected agent itself** — an impostor viewing its own mind is its
own knowledge, not a leak, so "show what they saw" on an impostor (which flips to As-agent-self) correctly keeps its
secrets visible. They are suppressed ONLY when inspecting an impostor through a DIFFERENT agent's eyes (a real leak). They
derive from the omniscient ground truth already in the view-model (the roster's roles → fellow impostors; `KillEventView`
→ own kills).
Consolidate the existing `MemoryPanel` / `LLMCallCard` / `AgentSelector` into the tabs. This surface has no converge
reference, so its chrome comes from a NEW focused Claude-Design pass: *"Design the agent mind-inspector (tabbed: Belief /
Prompt / Response / Memory / Flags) with a reasoning trail and a 'what they saw' toggle; mono for prompt / response /
JSON; states living / dead / impostor (Omniscient) / impostor-viewing-itself / no-agent-selected; firewall — impostor-only
fields appear in Omniscient or when the lens is that impostor itself, cover-tasks labelled 'fabricated'; presentational
only, tokens only"* → Share → Handoff to Claude Code →
integrate.
**Definition of done:** the tabbed Belief / Prompt / Response / Memory / Flags inspector renders via the existing
`ThoughtStream` slot (App.tsx unchanged); Prompt / Response read `LLMCallView` (mono); Memory reads `AgentMemoryView`; the
Thought → Action → Observation trail renders; "show what they saw" switches the map to that agent's fog (store-driven, no
map edit); impostor extras appear in Omniscient OR when the perspective lens is the inspected impostor itself, and are
suppressed only when inspecting an impostor through a different agent's perspective; cover-tasks are labelled fabricated; a Storybook story covers living / dead / impostor (Omniscient) / no-agent-selected; `npm run tsc:check` +
`npm run build` pass and `scripts/check.sh` is green; `App.tsx` is untouched.

## Implementation hint
keep the `ThoughtStream` export (the slot) and have it render the new `MindInspector`; fold `MemoryPanel` / `LLMCallCard`
/ `AgentSelector` into the tabs. Prompt / Response tabs read `LLMCallView.prompt_text` / `response_text` (mono, verbatim).
"Show what they saw" is just `setPerspective(agent)` + `selectAgent` — the 12.5 map already fogs to the selected agent, so
no map edit. Derive impostor extras from the omniscient ground truth (roles → fellow impostors; `KillEventView` → own
kills) and gate every one of them on perspective = Omniscient.

## Integration risk
the firewall gate is Omniscient OR self-perspective — an impostor's secrets (`fellow_impostor_ids` / `own_kill` /
fabricated-cover) show to Omniscient and to As-agent-of-that-same-impostor (the agent's own knowledge), but MUST disappear
when inspecting an impostor through a DIFFERENT agent's eyes (the real leak). A blanket "suppress in all As-agent" is
WRONG — it would hide an impostor's own team from its own perspective. Prompt / Response are the agent's actual LLM I/O — render them
mono + verbatim. This is the per-agent belief *detail*; 12.6's matrix is the cross-agent overview — don't duplicate it.
There is no converge screen, so verify the chrome against the brief's firewall rules, not a screenshot. Don't edit
`App.tsx` (mount discipline).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-12-mind-inspector` with a title like `task 12.8: mind inspector`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing design/phase-12/stage-1-design.md §3.5, slice 6; the firewall + Omniscient-gating rules in `design/phase-12/claude-design-brief.md`. NO converge screen exists for this surface — it needs a NEW Claude-Design pass (grounded on the brief + `tokens-seed`, via the §9.5 handoff; not a sync).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
