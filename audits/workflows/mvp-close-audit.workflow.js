// MVP-close audit Workflow.
//
// Invoked once after Phase 5 closes (post-2026-05-29). Spawns 10 parallel
// class auditors over the entire project; runs adversarial verification on
// every finding; synthesizes survivors into a single Markdown audit report
// that the orchestrator writes to audits/.
//
// Invoke from a Claude Code session:
//   Workflow({scriptPath: "audits/workflows/mvp-close-audit.workflow.js"})
//
// Expected cost: $17-28 in token spend (capped by Workflow runtime).
// Expected wall-clock: ~30-35 minutes.
// Output: audits/audit-YYYY-MM-DD-HHMM-mvp-close.md (synthesis agent writes it).

export const meta = {
  name: 'mvp-close-audit',
  description: 'MVP-close audit: 10 parallel class auditors + adversarial verify + synthesis. Output is a forward-looking repair task list.',
  whenToUse: 'After Phase 5 closes; produces the final pre-post-MVP audit ratification + repair list',
  phases: [
    { title: 'Class audits', detail: '10 parallel auditors, one per lens' },
    { title: 'Adversarial verify', detail: '3 skeptics per finding, majority required to survive' },
    { title: 'Synthesis', detail: 'Group findings, propose repair tasks, write report' },
  ],
}

// ---------------------------------------------------------------------------
// Schemas
// ---------------------------------------------------------------------------

const FINDINGS_SCHEMA = {
  type: 'object',
  properties: {
    class_key: { type: 'string', description: 'Letter A through J identifying the audit class' },
    class_name: { type: 'string', description: 'Human-readable class name' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'Unique within this class, e.g. A-1, A-2' },
          severity: {
            type: 'string',
            enum: ['blocking', 'high', 'medium', 'low', 'informational'],
          },
          title: { type: 'string', description: 'One-line summary of the finding' },
          file: { type: 'string', description: 'Primary file path; empty if cross-cutting' },
          line: { type: 'integer', description: 'Line number in file; -1 if not file-specific' },
          claim: { type: 'string', description: 'What is the defect or drift' },
          evidence: { type: 'string', description: 'Citation: file:line excerpt, shell output, or grep result' },
          repair_hint: { type: 'string', description: 'One-paragraph sketch of the fix; not a full task contract' },
        },
        required: ['id', 'severity', 'title', 'claim', 'evidence'],
      },
    },
    coverage_note: {
      type: 'string',
      description: 'What this class auditor examined; what was deliberately not examined',
    },
  },
  required: ['class_key', 'class_name', 'findings', 'coverage_note'],
}

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    refuted: {
      type: 'boolean',
      description: 'true if the finding is wrong, intentional, or unverifiable; false only if confirmed real',
    },
    reasoning: { type: 'string', description: 'Citation-backed reasoning, file:line where applicable' },
    severity_adjusted: {
      type: 'string',
      enum: ['blocking', 'high', 'medium', 'low', 'informational', 'unchanged'],
      description: 'If not refuted, the verifier may downgrade severity. "unchanged" keeps the original.',
    },
  },
  required: ['refuted', 'reasoning'],
}

const SYNTHESIS_SCHEMA = {
  type: 'object',
  properties: {
    verdict: {
      type: 'string',
      enum: ['SUBSTRATE_CLEAN', 'MINOR_REPAIRS_NEEDED', 'SIGNIFICANT_REPAIRS_NEEDED'],
    },
    verdict_rationale: { type: 'string' },
    repair_task_proposals: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          proposed_task_id: { type: 'string', description: 'e.g. 6.0.1 or post-mvp-1' },
          title: { type: 'string' },
          finding_ids: { type: 'array', items: { type: 'string' } },
          scope_sketch: { type: 'string' },
          priority: { type: 'string', enum: ['urgent', 'pre-phase-6', 'opportunistic'] },
        },
        required: ['proposed_task_id', 'title', 'finding_ids', 'scope_sketch', 'priority'],
      },
    },
    forward_looking_observations: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
    report_markdown: {
      type: 'string',
      description: 'The full Markdown audit report body, ready to write to audits/. Should include all sections: Verdict, Environment, Per-class findings, Adversarial-verify outcomes, Repair task proposals, Forward-looking, Required closing fields.',
    },
  },
  required: ['verdict', 'repair_task_proposals', 'summary', 'report_markdown'],
}

// ---------------------------------------------------------------------------
// Class definitions
// ---------------------------------------------------------------------------

const COMMON_PREAMBLE = `You are one of 10 parallel auditors performing the MVP-close audit of
the AiLibi project. Your output will go through adversarial verification (3 skeptics per finding
will try to refute each one) and then synthesis with the other 9 auditors' outputs.

Constraints applicable to every audit class:
- Read-only. Do not edit any source file, test, fixture, configuration, task doc, agent prompt,
  or memory file. You may run any non-mutating shell command.
- Every finding must cite a file:line OR a reproducible shell command and its output.
- No drive-by suggestions. If a recommendation does not address a cited defect, omit it.
- Phase boundaries: phases 0-5 are merged on main; Phase 5 closed 2026-05-29 declaring MVP complete.
- Out of scope for THIS audit: re-running pytest/mypy/ruff (mechanical CI gates;
  trust the existing checks), re-evaluating prompt behavior (Phase 5's regression suite handles
  this), re-auditing the Phase 4 mid-phase DTO surface (already audited and passed).
- Severity calibration: "blocking" only if it stops the project; "high" if it shapes immediate
  post-MVP work; "medium" if it should land before Phase 6; "low" if opportunistic; "informational"
  if worth recording but no action expected.

Your class-specific scope is below. Output ONLY findings within your class's scope; do not
attempt to be comprehensive across other classes' surfaces.

`

const CLASSES = [
  {
    key: 'A',
    name: 'Architecture coherence',
    scope: `Compare DESIGN.md's stated architectural claims against the actual code state at
HEAD. For each claim in DESIGN.md (§0 Design Stance, §1 Architecture, §3 Engine, §4 Agent System,
§5 Meeting System, §6 Memory, §7 Tech Stack, §8 MVP Scope, §11 Eval Strategy), verify it is true.
Drift between DESIGN.md and code IS the finding. Look especially for: invariants that DESIGN.md
asserts but no test enforces; abstractions DESIGN.md describes that have been bypassed in practice;
tech choices DESIGN.md names that have changed (e.g. Tailwind version).

Read DESIGN.md fully, then walk through each numbered section verifying claims against engine/,
agents/, llm/, meetings/, observation/, orchestrator/, api/, frontend/, eval/.`,
  },
  {
    key: 'B',
    name: 'Cross-phase consistency',
    scope: `Audit the assumptions each phase makes about earlier phases' substrates. Specifically:
Phase 4 (api/, frontend/) consumes Phase 3 (meetings/) DTOs and Phase 1 (engine/) state via
engine-playback; do those assumptions still hold? Phase 5 (eval/) consumes Phase 4 (api/schemas.py)
and Phase 3 (meetings/schemas.py); is the wire correct? Look for: silent contract drift; fields
added in one phase that another phase still doesn't consume; renames that updated some call sites
but not all; backward-compat shims that should now be removed.

Walk all 82 PR commits via git log; look for cross-phase touches and verify the touched substrate
still holds.`,
  },
  {
    key: 'C',
    name: 'Security review',
    scope: `Local-only API today, but assess what would break if the spectator UI were deployed
behind any auth/network surface. Specifically: secret handling (ANTHROPIC_API_KEY paths, .env
discipline, sample replay file LLM-call prompts containing memory state); CORS posture; input
validation on API routes; replay file path traversal; npm dependency known-CVE check (npm audit);
how would multi-tenant deployment break the spectator privilege model.

Read api/, frontend/src/api/, .env.example, .gitignore, scripts/run_spectator.sh, and any
auth-relevant config.`,
  },
  {
    key: 'D',
    name: 'Leak risk re-walk',
    scope: `Re-verify the observation firewall + spectator privilege scoping holds end-to-end at
MVP close. Do not duplicate the Phase 4 mid-phase DTO audit (that scope is out). Instead: focus
on the NEW Phase 5 DTOs (eval/report_schema.py if present, eval metric outputs, the tournament
dashboard's API surface), the LLM call records' prompt text (does it accidentally embed the
victim's role for other observers?), and any new endpoints added in Phase 5.

Read eval/, api/routes/eval.py (and any new eval routes), api/schemas.py focusing on additions
since the Phase 4 mid-phase audit's HEAD reference 934986d.`,
  },
  {
    key: 'E',
    name: 'Schema integrity',
    scope: `Audit Pydantic schemas vs TypeScript types vs replay JSONL format vs Phase 5 eval
report schema for drift. Specifically: every Pydantic model in api/schemas.py should have a
matching TypeScript type in frontend/src/types/api.ts; the eval/report_schema.py format_version
should be enforced at read time; the replay JSONL discriminator-based ReplayLogEntry should
validate cleanly. Run "uv run python scripts/generate_prompts.py --check" and verify the type
sync stays clean.

Read api/schemas.py, frontend/src/types/api.ts, eval/report_schema.py (or equivalent),
orchestrator/replay.py, meetings/schemas.py.`,
  },
  {
    key: 'F',
    name: 'Documentation drift',
    scope: `Compare every project documentation surface against reality. README.md (status table,
load-bearing decisions, audit count, test count), AGENTS.md (conventions for dispatched agents),
DESIGN.md (mostly covered by Class A; flag doc-only issues here), MEMORY.md contents at
/Users/danielkeinan/.claude/projects/.../memory/, and any task contract addendums. Flag:
stale numbers, broken file paths, removed code still referenced, conventions documented but
not followed in recent tasks, missing documentation of decisions that affect future agents.

Read README.md, AGENTS.md, AGENT_IMPLEMENTATION.md (if present), DESIGN.md (cross-ref Class A's
findings; report only doc-only issues here), MEMORY.md, .env.example, scripts/check.sh comments.`,
  },
  {
    key: 'G',
    name: 'Performance under realistic input',
    scope: `Task 5.9 hit the laptop-benchmark target (≥1 game/min headless). This audit goes
broader: what happens at 200-game tournaments? 10 concurrent spectator UI viewers hitting the
same API? Loading a replay JSONL with 10000+ ticks? Memory pressure from the engine-playback
LRU cache? Look for: hardcoded limits that would break at scale, unbounded data structures,
N+1-query patterns in the loader, frontend rendering bottlenecks (PixiJS Application reuse,
React render churn). DO NOT actually run a 200-game tournament (that's $4); reason from code.

Read api/replay_loader.py (especially the LRU cache + engine-playback loop), eval/balance_eval.py,
scripts/run_tournament.py, frontend/src/components/MapView.tsx, frontend/src/store/.`,
  },
  {
    key: 'H',
    name: 'Pre-scale architectural concerns',
    scope: `AiLibi is asyncio in single process per DESIGN.md §7. What architectural concerns
surface when moving to multiple workers + Redis pubsub (DESIGN.md's named scale path)?
Specifically: global state that's process-local today (LRU caches, module-level imports with
side effects); file-system writes that assume single-writer (ReplayLog, MANIFEST.md updates);
asyncio assumptions (single event loop); shared port assumptions (8000, 5173). Flag what would
break and what would need to change.

Read api/main.py, api/replay_loader.py, orchestrator/game.py, orchestrator/replay.py,
scripts/run_spectator.sh, scripts/refresh_samples.sh (if 4.17 landed).`,
  },
  {
    key: 'I',
    name: 'Test invariant gaps',
    scope: `Not test-coverage as a metric; rather, INVARIANTS that should be enforced by tests
but aren't. Walk the test suite (tests/) and ask: for each module under engine/, agents/, llm/,
meetings/, observation/, orchestrator/, api/, eval/, what's the load-bearing invariant that
would silently break if a future task introduced a bug? Is there a test that would catch it?
Flag specifically: invariants that ARE in DESIGN.md but have no test (cross-ref with Class A
findings; report test-gap issues here), tests that only cover happy path, missing property-based
tests where they'd help, missing fail-loud tests (e.g. ReplayLog corruption detection from 4.16).

Read tests/ recursively. Cross-reference each module under engine/, agents/, etc. with its test
file. Flag gaps where an invariant has no enforcement.`,
  },
  {
    key: 'J',
    name: 'Agent-intelligence substrate gaps',
    scope: `The Phase 6+ direction is making the game more "interesting": better agent reasoning,
smarter lying during meetings, richer task variety, deeper contradiction detection, more
sophisticated impostor strategy. Class J specifically scrutinizes what current substrate
constraints LIMIT or BLOCK that direction. Output is gaps, not feature proposals — the audit
finds what's missing; a separate Phase 6 design exploration proposes what to add.

Read these behavioral evidence sources to identify failure modes that better substrate could fix:
- replays/samples/replay-seed-22.jsonl, replay-seed-24.jsonl, replay-seed-26.jsonl,
  replay-seed-49.jsonl (the four meeting-bearing samples from the Phase 3 closing eval)
- audits/audit-2026-05-25-2320-seed-23-deep-debug.md (deep behavioral debug)
- audits/audit-2026-05-26-0325-pre-phase-4-real-provider-eval.md §9 (closing observations,
  including the seed-24 subject="p-0" and seed-49 subject="p-self" findings)

For each behavioral failure mode you observe, identify the substrate constraint that caused it.
Specifically look for:

- Schema limits. AlibiClaim has 3 variants (alibi, accusation, corroboration). Is that limited
  vocabulary blocking richer agent expression? E.g. no "calling-bluff", "partial-corroboration",
  "hedged-accusation", or "request-for-clarification" claim type. PlayerId as bare str
  (per Task 3.20 finding b) — has it actually bitten the system at MVP close?
- Prompt template gaps. Read agents/strategic/prompts/impostor_report.j2,
  agents/strategic/prompts/accusation_round.j2, agents/strategic/prompts/crewmate_report.j2.
  Are these leaving capabilities the model could exercise on the floor? Look for: weak
  instructions on lying (impostor template), thin contradiction-handling guidance (accusation
  template), missing explicit deception-strategy framing.
- FSM tactical-layer limits. agents/tactical/ FSMs are scripted. Do they constrain meeting-
  relevant data that the strategic LLM layer needs (e.g. uncertainty about what an agent saw,
  ambiguity in alibis that could be exploited)?
- Contradiction detection rules. meetings/transcript.py contradiction detection. What classes
  of contradiction can the system NOT detect today? E.g. temporal impossibilities, location-
  topology violations, mutual-witness contradictions across multiple speakers.
- Memory rendering. agents/memory/store.py render_for_prompt output. What does the rendered
  view omit that would help the LLM lie better or detect lies better?
- Belief rules. agents/memory/beliefs.py implements DESIGN.md §6.3 belief rules 1 and 4 today.
  Rules 2 (alibi-contradiction), 3 (verifiable-shared-task trust), and 5 (time-decay) are
  deferred. Which are agent-intelligence-relevant prerequisites for "smarter" agents vs.
  opportunistic polish?
- Task model. engine/world.py + engine/entities.py task model is visit-and-wait. What richer
  task patterns would change agent behavior — timed sequences, multi-room dependencies,
  publicly-witnessable vs invisible tasks, sabotage-able tasks? Identify what would have to
  change at the engine layer.
- Meeting dynamics. Currently fixed 2 accusation rounds. Does the round count constraint cap
  agent deception games (e.g. impostors that need a third round to redirect a vote, crewmates
  that need a third round to combine observations)?
- Win-condition. The impostor-elimination gap (per memory project_win_condition_impostor_
  elimination_gap.md) is an agent-intelligence-relevant defect: current incentive structure is
  wrong post-last-impostor; agents have no signal to "stop suspecting" once impostors are gone.

For each finding, indicate which agent-intelligence direction it unblocks (smarter lying,
richer claims, deeper contradiction detection, better task variety, adaptive meetings, fixed
incentives). Severity by impact: "blocking" if it's a hard prerequisite for any meaningful
agent-intelligence work; "high" if it shapes the near-term direction; "medium" if worth doing
alongside; "low" if opportunistic; "informational" if observation-only.

Out of scope for THIS class (covered elsewhere or de-prioritized):
- Phase 6 human-player-seat per DESIGN.md §9 (de-prioritized; project direction is
  agent-intelligence)
- Positional gameplay (separate axis from agent intelligence)
- ML agent policies (separate axis from prompt+schema improvements)
- Multi-process scaling (covered in Class H)
- General code quality findings (other classes)`,
  },
  {
    key: 'K',
    name: 'UI/UX gaps',
    scope: `Audit the spectator frontend for user-facing defects that block a polished Phase 6+
visual redesign (Claude Design pass). This class finds defects in the current UI; design
proposals are not in scope. The output feeds the redesign brief with concrete things to fix
or avoid before the redesign starts.

Specifically look for:

- UI state machine gaps. For each component (MapView, MeetingView, ThoughtStream, BeliefMatrix,
  ReplayControls, TournamentDashboard if present, ReplayPicker, App.tsx): does it handle empty
  state, loading state, error state, and edge cases (dead agents, no-meeting ticks, partial
  replays without game_over records, zero-replay state)? Find cases where the UI shows a blank,
  undefined, NaN, or unstyled fallback rather than a meaningful indicator.
- Accessibility gaps. Color-only state encoding (suspicion heatmap without numeric fallback,
  alive/dead state without aria label, role indicator using color only). Missing keyboard
  navigation. Missing aria labels on interactive controls. Low contrast (text on dark Tailwind
  default background). Walk every component file for these patterns.
- Large-replay performance. The largest current sample is ~163KB. What happens at 5x or 10x
  that size? Read api/replay_loader.py's LRU cache size + frontend/src/store/replayStore.ts;
  what is the memory footprint of one loaded ReplayView? Is the per-tick rendering bounded?
  Are there N+1 re-renders or React render churns visible (e.g. components subscribing to
  store fields that change every tick)? DO NOT load a giant replay; reason from code.
- Missing error states. What does the app show when the API is down? When a replay file is
  corrupted (Task 4.16 now raises ReplayLog.CorruptedFileError; does the UI surface this
  gracefully)? When the network is slow? Look for try/catch blocks that swallow errors silently
  in frontend/src/api/client.ts and frontend/src/store/replayStore.ts.
- TypeScript drift affecting UI behavior. Grep for "any", "@ts-ignore", "@ts-expect-error",
  and non-null assertions ("!.") in frontend/src/. Any of these can hide type issues that
  affect runtime UI behavior. Run "cd frontend && npx tsc --noEmit" to confirm clean compile;
  flag any compiler warnings.
- Layout / responsive behavior. Tailwind v4 in use; what happens at narrow viewports (< 768px)?
  At 4K displays? Task 4.15 fixed a MeetingView overflow finding; look for analogous issues in
  ThoughtStream, BeliefMatrix, TournamentDashboard. Identify which breakpoints each component
  handles vs. which assumes desktop-only.
- Animation / motion polish. PixiJS tween logic in MapView; React transitions elsewhere. Are
  any animations janky, dropped frames, inconsistent easing? These shape the redesign brief
  for motion language.
- Component-level encapsulation. Are component prop contracts clean enough that Claude Design
  can swap implementations file-by-file? Do components have implicit dependencies on the
  Zustand store that would make per-component redesign awkward? Are there components that
  reach across files via shared state instead of props?
- Branding / identity surface area. Does the project have a wordmark / logo / consistent color
  signature visible in the UI today? If not, that's not a defect per se, but worth flagging as
  redesign-brief input.

For each finding, name which component(s) are affected and what severity:
"blocking" if it would embarrass during a polished demo;
"high" if it shapes the redesign brief substantially;
"medium" if it should land alongside redesign work;
"low" if opportunistic;
"informational" if observation-only.

Read: frontend/src/App.tsx, frontend/src/components/ (all files), frontend/src/store/
replayStore.ts, frontend/src/api/client.ts, frontend/src/types/api.ts, frontend/tailwind.
config.* (whichever exists), frontend/src/index.css if present. Skim recently-merged UI tasks
(4.13 TickView synthesis, 4.14 belief-rule wiring, 4.15 MeetingView overflow) for context on
what's been recently fixed.

Out of scope for THIS class: data leak risk (covered in Class D), security (Class C), per-tick
backend performance (Class G), pre-scale architectural (Class H), agent-intelligence (Class J).
Findings here are PURELY about user-facing UI behavior and Claude Design enablement.`,
  },
]

// ---------------------------------------------------------------------------
// Phase 1: parallel class audits
// ---------------------------------------------------------------------------

phase('Class audits')
log(`Spawning ${CLASSES.length} parallel auditors. Budget remaining: ${budget.total ? `$${Math.round(budget.remaining() / 1000)}k tokens` : 'unlimited'}.`)

const classReports = await parallel(
  CLASSES.map((c) => () =>
    agent(
      COMMON_PREAMBLE + `\nClass ${c.key} — ${c.name}\n\n${c.scope}\n\n` +
        `Output: a structured findings list with class_key="${c.key}" and class_name="${c.name}". ` +
        `If no findings in this class, return an empty findings array and a coverage_note explaining what you examined.`,
      {
        label: `audit:${c.key}-${c.name.toLowerCase().replace(/\s+/g, '-').slice(0, 30)}`,
        phase: 'Class audits',
        schema: FINDINGS_SCHEMA,
      }
    )
  )
)

const allFindings = classReports
  .filter(Boolean)
  .flatMap((r) =>
    r.findings.map((f) => ({
      ...f,
      class_key: r.class_key,
      class_name: r.class_name,
      fully_qualified_id: `${r.class_key}-${f.id}`,
    }))
  )

log(`Class audits complete. ${allFindings.length} raw findings across ${classReports.filter(Boolean).length} classes.`)

// ---------------------------------------------------------------------------
// Phase 2: adversarial verify
// ---------------------------------------------------------------------------

phase('Adversarial verify')

if (allFindings.length === 0) {
  log('No findings to verify. Skipping adversarial verify phase.')
}

const verified = await parallel(
  allFindings.map((f) => () =>
    parallel(
      Array.from({ length: 3 }, (_, lensIndex) => () =>
        agent(
          `You are verifying-by-trying-to-refute an MVP-close audit finding for AiLibi.

Finding:
  Class: ${f.class_key} - ${f.class_name}
  ID: ${f.fully_qualified_id}
  Severity: ${f.severity}
  Title: ${f.title}
  File: ${f.file || '(cross-cutting)'}${f.line >= 0 ? `:${f.line}` : ''}
  Claim: ${f.claim}
  Evidence: ${f.evidence}
  Repair hint: ${f.repair_hint || '(none)'}

Your job: try to refute this finding. Default to refuted=true if you are uncertain.
Verify by reading the cited file at the cited line, running the cited shell command, or
searching for counterexamples. Common refutation grounds:
- The cited line does not exist or does not say what the finding claims
- The behavior is intentional and documented in DESIGN.md, a task contract, or a memory entry
- The finding misreads the code (e.g. mistakes a comment for code)
- The evidence does not actually support the claim
- The "drift" is between two files where one is the authoritative source and the other is
  documentation that legitimately describes a future state

Lens index ${lensIndex + 1} of 3: ${
            lensIndex === 0
              ? 'Read the cited evidence literally; does the finding state what is there?'
              : lensIndex === 1
                ? 'Check whether the behavior is intentional (documented in DESIGN.md, memory, task contracts).'
                : 'Search for counterexamples or invalidating context elsewhere in the codebase.'
          }

Output the structured verdict.`,
          {
            label: `verify:${f.fully_qualified_id}-l${lensIndex + 1}`,
            phase: 'Adversarial verify',
            schema: VERDICT_SCHEMA,
          }
        )
      )
    ).then((votes) => {
      const valid = votes.filter(Boolean)
      const refuteCount = valid.filter((v) => v.refuted).length
      const survived = refuteCount < 2 // majority (2/3) must refute to drop
      return {
        ...f,
        survived,
        verifier_votes: valid,
        refute_count: refuteCount,
      }
    })
  )
)

const survivedFindings = verified.filter((v) => v.survived)
const refutedFindings = verified.filter((v) => !v.survived)

log(`Adversarial verify complete. ${survivedFindings.length} findings survived, ${refutedFindings.length} refuted.`)

// ---------------------------------------------------------------------------
// Phase 3: synthesis
// ---------------------------------------------------------------------------

phase('Synthesis')

const synthesisInput = {
  total_class_audits: classReports.filter(Boolean).length,
  raw_finding_count: allFindings.length,
  surviving_findings: survivedFindings.map((f) => ({
    class: f.class_key,
    id: f.fully_qualified_id,
    severity: f.severity,
    title: f.title,
    file: f.file,
    line: f.line,
    claim: f.claim,
    evidence: f.evidence,
    repair_hint: f.repair_hint,
  })),
  refuted_count: refutedFindings.length,
  per_class_coverage: classReports
    .filter(Boolean)
    .map((r) => ({ class: r.class_key, name: r.class_name, coverage: r.coverage_note })),
}

const synthesis = await agent(
  `You are synthesizing the MVP-close audit of the AiLibi project. 10 parallel class auditors
produced findings; adversarial verification dropped the ones 2-of-3 skeptics could refute.
What remains is the load-bearing finding set.

Input data (JSON):
${JSON.stringify(synthesisInput, null, 2)}

Your output has two parts:
1. Structured synthesis: verdict, grouped repair task proposals (group similar findings; propose
   one task per group with priority + scope sketch), forward-looking observations.
2. report_markdown: the full Markdown audit report body. Write it to be the file content of
   audits/audit-YYYY-MM-DD-HHMM-mvp-close.md. Use this section structure:
   - "# MVP-Close Audit — YYYY-MM-DD HH:MM"
   - "## 1. Verdict" (verbatim one of SUBSTRATE_CLEAN / MINOR_REPAIRS_NEEDED / SIGNIFICANT_REPAIRS_NEEDED, plus 2-3 paragraphs of rationale)
   - "## 2. Environment" (audit run timestamp from \`date\`, audited HEAD from \`git log -1\`, total
     findings, surviving findings, refute rate)
   - "## 3. Findings by class" (one subsection per class A-J that produced findings; list each
     surviving finding with severity, file:line, claim, evidence, repair hint; classes with zero
     surviving findings get one sentence: "Class X — Name: no surviving findings; auditor coverage
     note: ...")
   - "## 4. Adversarial-verify outcomes" (counts: raw findings, survived, refuted; observed
     refute patterns if any)
   - "## 5. Repair task proposals" (one subsection per proposed task; include proposed_task_id,
     title, included finding IDs, scope sketch, priority)
   - "## 6. Forward-looking observations" (what Phase 6+ needs that's missing; from Class J +
     any other class's forward-looking findings)
   - "## 7. Required closing fields" (report path placeholder, verdict, surviving findings count,
     refuted findings count)

After producing the structured synthesis + report_markdown, ALSO write the report to disk:
- Run \`date '+%Y-%m-%d-%H%M'\` via the Bash tool to get the timestamp
- Compute the path: audits/audit-{timestamp}-mvp-close.md
- Use the Write tool to write the report_markdown content to that path

Report the final written path in the "summary" field.`,
  {
    label: 'synthesize',
    phase: 'Synthesis',
    schema: SYNTHESIS_SCHEMA,
  }
)

log(`Synthesis complete. Verdict: ${synthesis.verdict}. ${synthesis.repair_task_proposals.length} repair tasks proposed.`)

return {
  verdict: synthesis.verdict,
  total_findings: allFindings.length,
  surviving_findings: survivedFindings.length,
  refuted_findings: refutedFindings.length,
  repair_task_proposals: synthesis.repair_task_proposals,
  forward_looking: synthesis.forward_looking_observations,
  summary: synthesis.summary,
  tokens_spent: budget.spent(),
}
