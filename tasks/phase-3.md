# Phase 3 — Strategic Agents And Meetings

## Goal
LLM-driven meetings work end-to-end. Reports, accusations, votes. Cost stays under budget.

## Parallelism
Sequential foreground through meeting, LLM, and memory rendering. Prompt templates can run in parallel after 3.2 merges.

## Tasks
### Task 3.1 — LLM client
**Branch:** `phase-3-llm-client`
**Depends on:** Phase 2 merged
**Section refs:** DESIGN.md §4.4, DESIGN.md §7

llm/client.py, llm/claude_provider.py or provider equivalent, cache, budget.

**Files in scope:**
- llm/client.py
- llm/claude_provider.py
- llm/cache.py
- llm/budget.py

**Files NOT in scope:**
- agents/tactical/
- engine/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] LLMClient protocol exists.
- [ ] Provider adapter is behind LLMClient protocol.
- [ ] Prompt cache and per-game budget support exist.
- [ ] No LLM calls are added to agents/tactical/.
- [ ] mypy --strict passes on touched files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-3-1-llm-client.md`

### Task 3.2 — Output schemas
**Branch:** `phase-3-output-schemas`
**Depends on:** 3.1 merged
**Section refs:** DESIGN.md §5.3, DESIGN.md Appendix A

agents/strategic/output_schemas.py - ReportDocument, Statement, VoteBallot per §5.3 + §A.

**Files in scope:**
- agents/strategic/output_schemas.py

**Files NOT in scope:**
- engine/
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] ReportDocument, Statement, and VoteBallot schemas match DESIGN.md §5.3 and Appendix A.
- [ ] Schemas are suitable for structured LLM output.
- [ ] No imports from engine/ under agents/.
- [ ] mypy --strict agents/ passes for touched files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-3-2-output-schemas.md`

### Task 3.3 — Memory rendering
**Branch:** `phase-3-memory-rendering`
**Depends on:** 3.2 merged
**Section refs:** DESIGN.md §6.6

agents/memory/store.py::render_for_prompt per §6.6.

**Files in scope:**
- agents/memory/store.py

**Files NOT in scope:**
- engine/
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] render_for_prompt produces a token-budgeted structured view per DESIGN.md §6.6.
- [ ] Rendered memory comes from structured memory, not raw chat as source of truth.
- [ ] Salience ordering is deterministic.
- [ ] No imports from engine/ under agents/.
- [ ] mypy --strict agents/ passes for touched files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-3-3-memory-rendering.md`

### Task 3.4 — Meeting state machine
**Branch:** `phase-3-meeting-state-machine`
**Depends on:** 3.3 merged
**Section refs:** DESIGN.md §5.1, DESIGN.md §5.2

meetings/manager.py and meetings/transcript.py per §5.1 + §5.2.

**Files in scope:**
- meetings/manager.py
- meetings/transcript.py

**Files NOT in scope:**
- engine/ core rule changes
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] MeetingManager follows trigger lifecycle in DESIGN.md §5.1.
- [ ] Protocol implements report intake, accusation rounds, voting, and resolution per DESIGN.md §5.2.
- [ ] Missed deadlines yield default no-statement behavior as specified.
- [ ] Relevant meeting tests pass.
- [ ] mypy --strict passes on touched files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-3-4-meeting-state-machine.md`

### Task 3.5 — Strategic reasoner
**Branch:** `phase-3-strategic-reasoner`
**Depends on:** 3.4 merged
**Section refs:** DESIGN.md §4.4

agents/strategic/reasoner.py - wires render_for_prompt -> LLM -> parsed output.

**Files in scope:**
- agents/strategic/reasoner.py

**Files NOT in scope:**
- engine/
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Strategic reasoner calls render_for_prompt, invokes LLMClient, and parses structured outputs.
- [ ] Strategic calls occur only at meeting or specified trigger points.
- [ ] No imports from engine/ under agents/.
- [ ] No LLM calls in agents/tactical/.
- [ ] mypy --strict agents/ passes for touched files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-3-5-strategic-reasoner.md`

### Task 3.6 — Voting
**Branch:** `phase-3-voting`
**Depends on:** 3.5 merged
**Section refs:** DESIGN.md §5.5

meetings/voting.py per §5.5.

**Files in scope:**
- meetings/voting.py

**Files NOT in scope:**
- engine/ core rule changes
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Voting tally and skip behavior match DESIGN.md §5.5.
- [ ] VoteBallot structured output is parsed and tallied.
- [ ] Ballots are publicly logged after meeting resolution.
- [ ] Relevant voting tests pass.
- [ ] mypy --strict passes on touched files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-3-6-voting.md`

### Task 3.7 — Contradiction detection
**Branch:** `phase-3-contradiction-detection`
**Depends on:** 3.6 merged
**Section refs:** DESIGN.md §5.4, DESIGN.md §6.4

meetings/transcript.py::detect_contradictions per §5.4 + §6.4.

**Files in scope:**
- meetings/transcript.py

**Files NOT in scope:**
- engine/
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] detect_contradictions flags incompatible alibi and saw-player claims.
- [ ] Contradiction flags are information, not verdicts.
- [ ] Detected contradictions can be surfaced to rendered memory.
- [ ] Relevant transcript tests pass.
- [ ] mypy --strict passes on touched files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-3-7-contradiction-detection.md`

### Task 3.P1 — Crewmate report prompt
**Branch:** `phase-3-crewmate-report-prompt`
**Depends on:** 3.2 merged
**Section refs:** DESIGN.md §5.3, DESIGN.md §6.6

agents/strategic/prompts/crewmate_report.j2.

**Files in scope:**
- agents/strategic/prompts/crewmate_report.j2

**Files NOT in scope:**
- engine/
- agents/tactical/
- llm/ client code
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Crewmate report prompt exists and targets the ReportDocument schema.
- [ ] Prompt uses rendered memory view and public transcript inputs only.
- [ ] Prompt includes a version marker.
- [ ] No code outside the prompt file is modified.

**Ready-to-paste prompt:** `codex_prompts/task-3-p1-crewmate-report-prompt.md`

### Task 3.P2 — Impostor report prompt
**Branch:** `phase-3-impostor-report-prompt`
**Depends on:** 3.2 merged
**Section refs:** DESIGN.md §4.5, DESIGN.md §5.3, DESIGN.md §6.6

agents/strategic/prompts/impostor_report.j2.

**Files in scope:**
- agents/strategic/prompts/impostor_report.j2

**Files NOT in scope:**
- engine/
- agents/tactical/
- llm/ client code
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Impostor report prompt exists and targets the ReportDocument schema.
- [ ] Prompt frames deception as a game rule without exposing hidden engine state.
- [ ] Prompt uses rendered memory view and public transcript inputs only.
- [ ] Prompt includes a version marker.
- [ ] No code outside the prompt file is modified.

**Ready-to-paste prompt:** `codex_prompts/task-3-p2-impostor-report-prompt.md`

### Task 3.P3 — Accusation round prompt
**Branch:** `phase-3-accusation-round-prompt`
**Depends on:** 3.2 merged
**Section refs:** DESIGN.md §5.2, DESIGN.md §5.3

agents/strategic/prompts/accusation_round.j2.

**Files in scope:**
- agents/strategic/prompts/accusation_round.j2

**Files NOT in scope:**
- engine/
- agents/tactical/
- llm/ client code
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Accusation round prompt exists and targets the Statement schema.
- [ ] Prompt uses rendered memory view, transcript-so-far, and contradiction flags only.
- [ ] Prompt includes a version marker.
- [ ] No code outside the prompt file is modified.

**Ready-to-paste prompt:** `codex_prompts/task-3-p3-accusation-round-prompt.md`

### Task 3.P4 — Vote ballot prompt
**Branch:** `phase-3-vote-ballot-prompt`
**Depends on:** 3.2 merged
**Section refs:** DESIGN.md §5.5

agents/strategic/prompts/vote_ballot.j2.

**Files in scope:**
- agents/strategic/prompts/vote_ballot.j2

**Files NOT in scope:**
- engine/
- agents/tactical/
- llm/ client code
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Vote ballot prompt exists and targets the VoteBallot schema.
- [ ] Prompt receives rendered memory, transcript, contradiction flags, and suspicion graph.
- [ ] Prompt includes uncertainty-aware skip behavior.
- [ ] Prompt includes a version marker.
- [ ] No code outside the prompt file is modified.

**Ready-to-paste prompt:** `codex_prompts/task-3-p4-vote-ballot-prompt.md`

## Merge Criteria
- 50-game eval: full-LLM games complete end-to-end.
- Impostor win rate in [25%, 65%] band.
- Cost per game <= $0.30 or provider equivalent.
- Meeting transcripts are human-readable.
