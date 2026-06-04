// Restructure impact-map Workflow.
//
// Maps the full CODE BLAST RADIUS of the "next-baseline" restructure
// (per-player tasks + 9p/2i roster + meeting-protocol redesign) so the
// DESIGN.md rewrite and the task decomposition are grounded in fact, not
// guesswork. READ-ONLY analysis: lenses read/grep the codebase and never edit;
// only the final synthesis agent writes (the impact-map markdown).
//
// Structure: a Scope pre-phase (one agent digests the current cross-cutting
// seams — WorldState.tasks shape, the meeting protocol, the determinism/leak/
// format machinery — so the lenses share an anchor) -> 6 parallel impact lenses
// (task-model re-key, meeting redesign, roster+leak, determinism+format, test
// census, DESIGN.md/docs/mirrors) -> 2 completeness critics that independently
// grep for missed consumers/tests/couplings -> synthesis that dedupes into a
// touchpoint inventory + invariant risks + a SEQUENCED TASK BREAKDOWN and writes
// the report to audits/.
//
// Invoke from a Claude Code session (after review):
//   Workflow({scriptPath: "audits/workflows/restructure-impact-map.workflow.js"})
//
// Output: audits/restructure-impact-map-YYYY-MM-DD-HHMM.md + the structured
// task breakdown returned to the caller.

export const meta = {
  name: 'restructure-impact-map',
  description: 'Map the code blast radius of the next-baseline restructure (per-player tasks + 9p/2i roster + meeting-protocol redesign): every touchpoint, broken test, at-risk invariant, and a sequenced, dependency-ordered task breakdown to dispatch.',
  whenToUse: 'Before a large substrate restructure, to scope what it touches/breaks across engine, replay/determinism, leak firewall, eval, tests, and docs, and to produce a dispatchable task breakdown.',
  phases: [
    { title: 'Scope', detail: 'One agent digests the current cross-cutting seams into a shared anchor' },
    { title: 'Analyze', detail: '6 parallel lenses map the blast radius of each change dimension' },
    { title: 'Verify', detail: '2 completeness critics independently grep for missed consumers/tests/couplings' },
    { title: 'Synthesis', detail: 'Dedupe into a touchpoint inventory + invariant risks + a sequenced task breakdown; write the report' },
  ],
}

// ---------------------------------------------------------------------------
// The restructure being mapped (shared context for every agent)
// ---------------------------------------------------------------------------

const RESTRUCTURE = `
The restructure being mapped (the "next baseline"), CONFIRMED by the owner:

1. PER-PLAYER TASKS. Re-key task ownership so multiple crewmates can hold the same
   task type/location, each with INDEPENDENT progress (the real Among-Us model).
   Today \`WorldState.tasks\` is a single dict keyed by \`TaskId\` (with
   \`TaskState.id == dict key\`), and the seeder (\`orchestrator/seeder.py::_build_tasks\`)
   deals DISTINCT ids with a fail-loud cap (\`num_crewmates * tasks_per_crewmate <=
   len(game_map.tasks)\` = 12). The change removes that cap (tasks become
   per-(player, task), or task-lists hang off \`PlayerState\`) and adjusts task
   progress + the task-win count.

2. 9p/2i ROSTER (was 7p/2i). Parity now = 5 crew deaths (7 crew). Interacts with the
   leak firewall (2 impostors among 9), the eval gates, balance, the per-player task
   pool, and spatial crowding on the canonical map.

3. MEETING REDESIGN. Replace the parallel N-reports + fixed N-statement-round + N-vote
   protocol with a conversational accusation CHAIN: the body-reporter states findings
   and accuses someone (or says "unsure"); the accused responds with a counter-claim/
   counter-accusation; the chain continues up to N turns but terminates EARLY on
   convergence (no new accusation / a re-accusation cycle); then an OPT-IN info-share
   for players who did not speak; then all vote. Fewer LLM calls; changes the meeting
   record format.

CONSEQUENCE (owner-accepted): this RESETS the eval substrate. The WorldState re-key +
the meeting-format change mean BOTH committed sets (4p/1i AND 7p/2i) stop reconstructing
byte-identically and are RE-RECORDED; the replay format_version bumps; and the "frozen
4p/1i reference" is re-baselined (the owner has confirmed it is OK to re-record it).

Your job is to map the CODE BLAST RADIUS so the DESIGN.md rewrite and the task breakdown
are accurate. This is strictly READ-ONLY: read/grep the code, do NOT edit anything. Cite
a concrete file:symbol (or test file::name) for every touchpoint; never assert a touchpoint
you did not locate in the code.
`

// ---------------------------------------------------------------------------
// Schemas
// ---------------------------------------------------------------------------

const TOUCHPOINT = {
  type: 'object',
  properties: {
    file: { type: 'string', description: 'Path, e.g. engine/world.py' },
    symbol: { type: 'string', description: 'Function/class/field, e.g. WorldState.tasks or _serialize_world_state' },
    change: {
      type: 'string',
      enum: ['modify', 'breaks', 'new', 'verify'],
      description: 'modify=edit this; breaks=an invariant/test/format breaks here; new=net-new code; verify=must re-check (e.g. leak/determinism) even if no edit',
    },
    note: { type: 'string', description: 'What changes / why — one line' },
    risk: { type: 'string', enum: ['high', 'medium', 'low'] },
  },
  required: ['file', 'symbol', 'change', 'note'],
}

const LENS_SCHEMA = {
  type: 'object',
  properties: {
    lens_key: { type: 'string', description: 'Letter identifying the lens' },
    lens_name: { type: 'string' },
    touchpoints: { type: 'array', items: TOUCHPOINT },
    invariants_at_risk: {
      type: 'array',
      description: 'Named invariants this lens sees threatened, e.g. "byte-identical reconstruction", "leak: a crewmate never sees another player\'s task ownership".',
      items: { type: 'string' },
    },
    tests_affected: {
      type: 'array',
      description: 'test file::name (or fixture path) + HOW it changes (assertion update / fixture regenerate / committed-data reset / new test needed).',
      items: { type: 'string' },
    },
    open_questions: {
      type: 'array',
      description: 'Design decisions this lens surfaces that DESIGN.md must lock before any task is dispatched.',
      items: { type: 'string' },
    },
    coverage_note: { type: 'string', description: 'What this lens examined; what it deliberately left to another lens.' },
  },
  required: ['lens_key', 'lens_name', 'touchpoints', 'coverage_note'],
}

const COMPLETENESS_SCHEMA = {
  type: 'object',
  properties: {
    missed_touchpoints: {
      type: 'array',
      description: 'Consumers/sites the lenses missed (found by independent grep). Empty if the lens coverage was complete.',
      items: TOUCHPOINT,
    },
    missed_tests: { type: 'array', items: { type: 'string' } },
    missed_couplings: {
      type: 'array',
      description: 'Cross-change interactions the per-lens view missed (e.g. the meeting-format change AND the determinism reset must land in one format_version bump).',
      items: { type: 'string' },
    },
    note: { type: 'string' },
  },
  required: ['missed_touchpoints', 'note'],
}

const SYNTHESIS_SCHEMA = {
  type: 'object',
  properties: {
    task_breakdown: {
      type: 'array',
      description: 'The dispatchable implementation units, dependency-ordered. The PRIMARY deliverable.',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'e.g. R-1, R-2' },
          title: { type: 'string' },
          scope: { type: 'string', description: 'One-paragraph what + the key files' },
          files: { type: 'array', items: { type: 'string' } },
          depends_on: { type: 'array', items: { type: 'string' }, description: 'Task ids that must land first (empty if none)' },
          complexity: { type: 'string', enum: ['Small', 'Medium', 'Integration'] },
          sequence_note: { type: 'string', description: 'Why it lands where it does (e.g. "land + unit-test before the combined re-record")' },
        },
        required: ['id', 'title', 'scope', 'depends_on', 'complexity'],
      },
    },
    invariant_risks: {
      type: 'array',
      description: 'The load-bearing invariants this restructure threatens + how each is preserved/re-established (determinism, leak firewall, format-version, frozen-baseline reset).',
      items: { type: 'string' },
    },
    cross_change_couplings: { type: 'array', items: { type: 'string' } },
    open_design_decisions: {
      type: 'array',
      description: 'What DESIGN.md must lock BEFORE any task is dispatched (e.g. the chain termination rule, the per-player-task win-count semantics, the 9p/2i task count).',
      items: { type: 'string' },
    },
    summary: { type: 'string', description: 'Final written report path + one-paragraph outcome.' },
    report_markdown: { type: 'string', description: 'Full Markdown report body, ready to write to audits/. Sections per the synthesis prompt.' },
  },
  required: ['task_breakdown', 'invariant_risks', 'open_design_decisions', 'summary', 'report_markdown'],
}

// ---------------------------------------------------------------------------
// Shared analyst preamble
// ---------------------------------------------------------------------------

const preamble = (scopeDigest) => `You are one of 6 parallel analysts mapping the CODE BLAST RADIUS of a large restructure
of the AiLibi social-deduction simulation, so a DESIGN.md rewrite and a task breakdown can
be authored accurately. Your findings feed a completeness pass and a synthesis that produces
the dispatchable task list.

${RESTRUCTURE}

Shared current-architecture digest (from the Scope phase — anchor on this, then read deeper
in your own lens area):
${scopeDigest}

Method: use the read-only tools (grep/Read/Bash for non-mutating commands like \`grep -rn\`,
\`git grep\`) to LOCATE every site your lens covers. Do not edit anything. For each site emit a
touchpoint with the concrete file:symbol, the change kind, and a one-line note. List the
invariants you see at risk, the tests/fixtures that break or move, and any design decision your
lens surfaces that DESIGN.md must resolve first. Stay within your lens; note what you leave to
others. Do not invent a touchpoint you did not locate.

Your lens-specific scope is below.
`

// ---------------------------------------------------------------------------
// Lens definitions
// ---------------------------------------------------------------------------

const LENSES = [
  {
    key: 'A',
    name: 'Per-player task model re-key',
    scope: `Map every consumer of task ownership/state the per-player-task re-key touches. Today
\`WorldState.tasks\` is a single dict keyed by \`TaskId\` with \`TaskState.id == dict key\`
(engine/world.py); the seeder (\`orchestrator/seeder.py::_build_tasks\`) deals DISTINCT ids under
the \`num_crewmates * tasks_per_crewmate <= len(map.tasks)\` cap. Find: where tasks are
read/mutated in the engine tick + rules (DoTask progress/completion — engine/tick.py,
engine/rules.py), the win condition (engine/win_conditions.py task-complete check + the
tasks_done/tasks_total count), the state-hash serialization (orchestrator/replay.py::
_serialize_world_state / _state_hash), what task data reaches agents (observation/service.py,
observation/packet.py, agents/perception.py — does/should a crewmate see ONLY their own tasks?
leak implications), the do_task tactical policy (agents/tactical/crewmate_policy.py,
impostor phantom-tasks for gp-4 later), and any eval/report or frontend task fields. State the
NEW shape (per-(player,task) ownership or task-lists on PlayerState) and EVERY site that changes
to support it. Cite file:symbol.`,
  },
  {
    key: 'B',
    name: 'Meeting-protocol redesign (chain + opt-in)',
    scope: `Map the blast radius of replacing report + fixed-statement-round + vote with the
accusation CHAIN + opt-in. Cover: the meeting state machine + phases (meetings/manager.py —
the report/statement/vote collection, DEFAULT_ROUND_COUNT, MeetingDeadlines, MeetingParticipant),
the strategic reasoner + prompts (agents/strategic/reasoner.py and
agents/strategic/prompts/{crewmate_report,impostor_report,accusation_round,vote_ballot}.j2 ->
chain-turn + opt-in prompts; note the 7.12 teammate firewall + the deterministic guard in
reasoner.py must survive), the record/replay schema (meetings/schemas.py — MeetingTranscript /
Statement / VoteBallot / ReportDocument; orchestrator/replay.py — MeetingReplayEntry;
eval/report_schema.py — MeetingReport), the eval metrics that READ meeting structure
(eval/vote_correctness.py, eval/meeting_quality.py, eval/accusation_calibration.py,
eval/alibi_fabrication.py), and orchestrator wiring (orchestrator/game.py::_run_and_apply_meeting,
_build_meeting_trigger). Call out the DETERMINISTIC termination rule + how a variable-length chain
is recorded and re-walked on replay. Surface the open design questions (termination condition,
opt-in incentive/mechanics, vote informedness, whether reactive deflection favors impostors).
Cite file:symbol.`,
  },
  {
    key: 'C',
    name: 'Roster 9p/2i + leak firewall + balance/eval gates',
    scope: `Map what moving to 9p/2i (from 7p/2i) touches. Cover: roster knobs/presets
(orchestrator/game.py — ROSTER_PRESETS, DEFAULT_NUM_PLAYERS/IMPOSTORS/TASKS_PER_CREWMATE; the
seeder; the CLI + scripts/refresh_samples.sh roster threading; per-set roster.json + the
api.replay_loader RosterConfig), the LEAK firewall at 2 impostors among 9 (eval/leak_test.py;
tests/observation/test_leak_property.py — the fellow_impostor_ids crew-empty invariant + the
num_impostors-parametrized property sweep; tests/observation/test_service.py), the eval GATES
(the meeting_rate floor + the Stage-A / re-record validity / degeneracy-tripwire criteria in
tasks/phase-7.md and the eval code), win-timing/balance (parity = 5 crew deaths now; the
kill-cadence vs task-race interplay), and spatial/map constraints (does engine/maps/canonical_1.yaml
hold 9 players + enough rooms; the per-player task pool removes the 12-task cap — confirm with
Lens A). Note cost/time scaling for the re-records. Cite file:symbol.`,
  },
  {
    key: 'D',
    name: 'Determinism, replay format + the substrate reset',
    scope: `Map the substrate-reset blast radius. Cover: the state hash
(orchestrator/replay.py::_state_hash / _serialize_world_state) — the WorldState re-key changes it
for ALL games; the determinism test (eval/determinism_test.py); byte-identical reconstruction
(api/replay_loader.py::ReplayLoader._walk and the committed-set recon tests in
tests/api/test_replay_loader.py + the committed-7p2i case in tests/eval/test_win_condition_selfcheck.py);
the replay FORMAT_VERSION (orchestrator/replay.py record models + eval/report_schema.py::
CURRENT_FORMAT_VERSION) — what must bump and whether old replays are rejected vs migrated; BOTH
committed sets (replays/samples/ 4p/1i AND replays/samples/7p2i) being re-recorded + the frozen-4p1i
reference retirement; scripts/build_sample_report.py (--check), scripts/refresh_samples.sh, the
MANIFEST/provenance, scripts/verify_samples.sh. State EXACTLY which committed-data-dependent tests
reset and what the new "reference" becomes. Cite file:symbol.`,
  },
  {
    key: 'E',
    name: 'Test-suite + fixture census',
    scope: `Produce a CENSUS of every test and fixture that breaks or moves across the WHOLE
restructure (lenses A-D). Walk tests/ (engine, meetings, agents, orchestrator, observation, eval,
api, scripts) + tests/fixtures/ + any frontend tests. For EACH affected test say HOW it changes:
assertion update / fixture regenerate / committed-data reset / brand-new test needed. Focus on:
tests that pin the OLD global task-dict shape; tests that pin the OLD meeting protocol (round
counts, parallel reports, statement structure); tests pinning the 7p/2i roster or committed-set
byte-identity; and scripted fixtures (tests/fixtures/scripted_game_*.json) that encode the old
protocol or task model. Cite test file::name (or fixture path).`,
  },
  {
    key: 'F',
    name: 'DESIGN.md, docs, task-doc machinery + api/frontend mirrors',
    scope: `Map the non-logic surface. Cover: which DESIGN.md sections must change (the meeting
protocol §5.2 and §5.x report/statement/vote shapes; the task-ownership model; the roster/balance
section; the win-conditions §3.x if the task-win count semantics change), AGENTS.md constraints;
the task-doc machinery (scripts/_task_parser.py, scripts/validate_task_docs.py,
scripts/generate_prompts.py — does anything there assume current shapes, and confirm the validated
contract format the new tasks must follow); and the api/frontend type mirrors that move with the
schema changes (api/schemas.py + api/routes/*, frontend/src/types/api.ts, the meeting/task view
components e.g. frontend/src/components/MeetingView.tsx, ReportCard.tsx, MeetingPill.tsx). State the
DESIGN-thread-owned vs task-owned split (DESIGN.md + the §-reconciliation is design-thread-owned;
tasks implement against it). Cite file:section.`,
  },
]

// ---------------------------------------------------------------------------
// Phase 1: Scope (shared current-architecture digest)
// ---------------------------------------------------------------------------

phase('Scope')
log('Digesting the current cross-cutting seams the lenses share.')

const scopeDigest = await agent(
  `You are the Scope phase of a code-impact mapping workflow for the AiLibi simulation.
${RESTRUCTURE}

Read just enough to write a CONCISE shared digest (prose, ~250-400 words) of the CURRENT
architecture seams the parallel lenses will all lean on — so they don't each re-derive the basics.
Cover, with concrete file:symbol: (1) how task ownership is represented today (WorldState.tasks dict
keyed by TaskId; the seeder's distinct-deal + 12-cap); (2) the meeting protocol's current phases +
record types (meetings/manager.py phases, meetings/schemas.py shapes, orchestrator/replay.py
MeetingReplayEntry); (3) the determinism/replay machinery (state_hash + _serialize_world_state,
the determinism test, ReplayLoader._walk reconstruction, format_version locations, the two committed
sets + build_sample_report --check); (4) the leak-firewall machinery (eval/leak_test.py, the property
sweep, the fellow_impostor_ids crew invariant); (5) where the roster knobs live. Do NOT edit anything.
Return ONLY the digest text.`,
  { label: 'scope:current-seams', phase: 'Scope' }
)

log('Scope digest ready. Fanning out the 6 impact lenses.')

// ---------------------------------------------------------------------------
// Phase 2: Analyze (6 parallel lenses)
// ---------------------------------------------------------------------------

phase('Analyze')

const lensReports = await parallel(
  LENSES.map((l) => () =>
    agent(
      preamble(scopeDigest) +
        `\nLens ${l.key} — ${l.name}\n\n${l.scope}\n\n` +
        `Output a structured map with lens_key="${l.key}" and lens_name="${l.name}".`,
      {
        label: `lens:${l.key}-${l.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 28)}`,
        phase: 'Analyze',
        schema: LENS_SCHEMA,
      }
    )
  )
)

const lenses = lensReports.filter(Boolean)
const allTouchpoints = lenses.flatMap((r) =>
  (r.touchpoints || []).map((t) => ({ ...t, lens: r.lens_key }))
)
log(`Analyze complete: ${lenses.length}/6 lenses, ${allTouchpoints.length} touchpoints.`)

// ---------------------------------------------------------------------------
// Phase 3: Verify (2 completeness critics over the union)
// ---------------------------------------------------------------------------

phase('Verify')

const unionForCritic = JSON.stringify(
  {
    touchpoints: allTouchpoints.map((t) => ({ lens: t.lens, file: t.file, symbol: t.symbol, change: t.change })),
    tests_affected: lenses.flatMap((r) => r.tests_affected || []),
    invariants_at_risk: lenses.flatMap((r) => r.invariants_at_risk || []),
  },
  null,
  2
)

const CRITICS = [
  {
    key: 'code',
    focus: `Find CODE consumers the lenses MISSED. Independently grep the repo for references the map
should contain but doesn't — e.g. \`grep -rn "\\.tasks" engine orchestrator observation agents eval\`,
references to TaskState / TaskId, every reader of MeetingReplayEntry / MeetingTranscript / the meeting
metrics, every site that constructs or serializes WorldState, every CURRENT_FORMAT_VERSION / format_version
use, and every num_players/num_impostors/tasks_per_crewmate threading point. Report only sites NOT already
in the union below, as missed_touchpoints.`,
  },
  {
    key: 'tests-couplings',
    focus: `Find MISSED TESTS/FIXTURES and MISSED CROSS-CHANGE COUPLINGS. Grep tests/ + tests/fixtures/ for
anything pinning the old task-dict shape, the old meeting protocol, the 7p/2i roster, or committed-set
byte-identity that the union's tests_affected list omits. Separately, name interactions BETWEEN the change
dimensions that a per-lens view misses (e.g. "the per-player-task re-key and the meeting-format change must
share ONE format_version bump and ONE combined re-record", or "the leak sweep must be re-parametrized for
9 players AND the new per-player task visibility at once").`,
  },
]

const critiques = await parallel(
  CRITICS.map((c) => () =>
    agent(
      `You are a completeness critic for a code-impact map of the AiLibi restructure.
${RESTRUCTURE}

${c.focus}

Here is the union the 6 lenses already produced (do NOT repeat anything already here; report only what is
MISSING):
${unionForCritic}

Use read-only grep/Read to verify. Output the structured completeness result.`,
      { label: `verify:${c.key}`, phase: 'Verify', schema: COMPLETENESS_SCHEMA }
    )
  )
)

const critiquesOk = critiques.filter(Boolean)
const missedTouchpoints = critiquesOk.flatMap((c) => c.missed_touchpoints || [])
const missedTests = critiquesOk.flatMap((c) => c.missed_tests || [])
const missedCouplings = critiquesOk.flatMap((c) => c.missed_couplings || [])
log(`Verify complete: ${missedTouchpoints.length} missed touchpoints, ${missedTests.length} missed tests, ${missedCouplings.length} couplings.`)

// ---------------------------------------------------------------------------
// Phase 4: Synthesis (dedupe -> map + task breakdown -> write report)
// ---------------------------------------------------------------------------

phase('Synthesis')

const synthesisInput = {
  restructure: RESTRUCTURE,
  scope_digest: scopeDigest,
  lenses: lenses.map((r) => ({
    lens: r.lens_key,
    name: r.lens_name,
    touchpoints: r.touchpoints,
    invariants_at_risk: r.invariants_at_risk || [],
    tests_affected: r.tests_affected || [],
    open_questions: r.open_questions || [],
    coverage_note: r.coverage_note,
  })),
  completeness: { missedTouchpoints, missedTests, missedCouplings },
}

const synthesis = await agent(
  `You are synthesizing a CODE IMPACT MAP for a large restructure of AiLibi. Six lenses mapped touchpoints
across the change dimensions and two completeness critics added what they missed. Merge it into the
authoritative map + a dispatchable task breakdown.

Input data (JSON):
${JSON.stringify(synthesisInput, null, 2)}

Produce two things:
1. Structured output: a dependency-ordered \`task_breakdown\` (the dispatch units — each a contract-sized
   piece with scope, files, depends_on, complexity, and a sequence_note; LAND the engine pieces with
   unit tests before the combined re-record per the owner's sequencing); the \`invariant_risks\` (determinism,
   leak, format-version, frozen-baseline reset — each with how it is preserved/re-established);
   \`cross_change_couplings\`; and \`open_design_decisions\` (what DESIGN.md must lock BEFORE dispatch).
2. report_markdown: the full report body for audits/, with these sections:
   - "# Restructure Impact Map — YYYY-MM-DD HH:MM"
   - "## 1. Restructure + substrate-reset summary"
   - "## 2. Touchpoint inventory" (grouped by subsystem: task model / meetings / roster+leak / determinism+format / tests / docs+mirrors; deduped; file:symbol + change + note)
   - "## 3. Invariant risks" (determinism, leak firewall, format-version, frozen-baseline reset — and the mitigation for each)
   - "## 4. Cross-change couplings"
   - "## 5. Open DESIGN.md decisions to lock before dispatch"
   - "## 6. Proposed task breakdown" (the dependency-ordered units, with the land-before-re-record sequencing called out)
   - "## 7. Lens coverage notes"

After producing the structured output + report_markdown, write the report to disk in THIS EXACT ORDER
(do NOT reorder; do NOT hardcode or guess a date):
- Step 1: run \`date '+%Y-%m-%d-%H%M'\` via the Bash tool and CAPTURE its stdout.
- Step 2: compute path = audits/restructure-impact-map-{captured-stdout}.md
- Step 3: use the Write tool to write report_markdown to that path.
Report the final written path in the "summary" field.`,
  { label: 'synthesize', phase: 'Synthesis', schema: SYNTHESIS_SCHEMA }
)

log(`Synthesis complete. ${synthesis.task_breakdown.length} tasks, ${synthesis.open_design_decisions.length} open DESIGN decisions.`)

return {
  task_count: synthesis.task_breakdown.length,
  task_breakdown: synthesis.task_breakdown,
  invariant_risks: synthesis.invariant_risks,
  cross_change_couplings: synthesis.cross_change_couplings,
  open_design_decisions: synthesis.open_design_decisions,
  summary: synthesis.summary,
  tokens_spent: budget.spent(),
}
