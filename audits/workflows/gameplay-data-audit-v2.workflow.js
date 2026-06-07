// Gameplay-data audit Workflow — v2 (Phase-8 chain-protocol substrate).
//
// SUPERSEDES gameplay-data-audit.workflow.js for sets recorded on the Phase-8
// substrate (per-player task instances, 9p/2i roster, reactive accusation-chain
// meetings, report format v2). The v1 workflow reads transcript.reports[]/
// statements[] and prices R=2 statement rounds — both removed by Task 8.7 — and
// its committed extractor pins replays/samples/7p2i. v1 is kept for provenance;
// use THIS file for any set recorded after PR #119.
//
// Analyzes a committed replay sample set (default replays/samples/9p2i, 50 games)
// to surface gameplay BUGS, TRENDS, decision-quality faults, call-waste, and
// concrete improvement proposals — purely from the recorded data (no Ollama; the
// recorded LLM outputs are model-agnostic and roles are re-derived from the seeder).
//
// Headline question this revision exists to answer: the recording-time report
// shows 0 ejections across ~91 meetings (~93% SKIP ballots) on a crew-favored
// 37/13 split — WHERE does the detection→ejection pipeline break, and is the
// flipped balance substrate-healthy or a new degeneracy?
//
// Structure: a deterministic Extract pre-phase (one agent UPDATES + runs the
// committed Python extractor: ground-truth roles, resolved events, hard rule
// violations, and the new chain-protocol invariants) → 7 parallel analysis
// lenses → HYBRID verification (code-certain mechanical findings pass straight
// through; each LLM judgment finding gets ONE adversarial skeptic — refuted
// drops; a skeptic that fails to run passes the finding through flagged
// unverified) → synthesis that writes a Markdown report to audits/.
//
// Invoke from a Claude Code session:
//   Workflow({scriptPath: "audits/workflows/gameplay-data-audit-v2.workflow.js"})
//   Workflow({scriptPath: "audits/workflows/gameplay-data-audit-v2.workflow.js", args: "replays/samples/9p2i"})
//
// Output: audits/audit-YYYY-MM-DD-HHMM-gameplay-data.md (synthesis agent writes it).

export const meta = {
  name: 'gameplay-data-audit-v2',
  description: 'Structured audit of a committed replay set on the Phase-8 substrate (9p/2i, per-player tasks, accusation-chain meetings): deterministic rule + chain-protocol checks, 7 analysis lenses, adversarial verify, synthesis. Output is a findings + improvement-proposal report.',
  whenToUse: 'After a chain-protocol eval set is recorded (post-PR-#119 substrate); analyzes gameplay data to find bugs/trends/faults — centrally the detection→ejection conversion gap — and propose improvements before Wave-1 agent-intelligence work.',
  phases: [
    { title: 'Extract', detail: 'One agent updates + runs the committed extractor: roles, resolved events, hard-rule + chain-protocol violations into a facts JSON' },
    { title: 'Analyze', detail: '7 parallel lenses over the facts + transcripts' },
    { title: 'Verify', detail: 'Mechanical findings pass through; each judgment finding gets one skeptic (refuted drops; a failed skeptic passes it through flagged unverified)' },
    { title: 'Synthesis', detail: 'Group findings, decompose the conversion pipeline, propose improvements, write report' },
  ],
}

// args = sample dir to audit; defaults to the canonical 9p/2i set.
const SAMPLE_DIR = typeof args === 'string' && args.trim() ? args.trim() : 'replays/samples/9p2i'

// ---------------------------------------------------------------------------
// Schemas (unchanged from v1 — the finding/verdict/synthesis shapes still fit)
// ---------------------------------------------------------------------------

const FINDING_ITEM = {
  type: 'object',
  properties: {
    id: { type: 'string', description: 'Unique within this lens, e.g. B-1, B-2' },
    severity: {
      type: 'string',
      enum: ['blocking', 'high', 'medium', 'low', 'informational'],
    },
    title: { type: 'string', description: 'One-line summary' },
    claim: { type: 'string', description: 'The bug / trend / fault / waste' },
    evidence: { type: 'string', description: 'Concrete citation: "seed N tick T" or "seed N meeting M turn K", with the numbers/roles' },
    repair_hint: { type: 'string', description: 'One-paragraph sketch of the fix or improvement; not a full task contract' },
  },
  required: ['id', 'severity', 'title', 'claim', 'evidence'],
}

const EXTRACT_SCHEMA = {
  type: 'object',
  properties: {
    facts_path: { type: 'string', description: 'Absolute path to the facts JSON file the extractor wrote' },
    games_analyzed: { type: 'integer', description: 'Number of replay-seed-*.jsonl games processed' },
    facts_summary: {
      type: 'string',
      description: 'Human-readable digest of the aggregates (win split + reasons, kills, deaths, meetings, chain shapes, ejections by role, ballot/SKIP totals, failed_calls, token totals) for the analyzer lenses to anchor on',
    },
    mechanical_findings: {
      type: 'array',
      description: 'Code-certain rule/protocol violations found deterministically (these BYPASS adversarial verification). Empty array if none.',
      items: FINDING_ITEM,
    },
  },
  required: ['facts_path', 'games_analyzed', 'facts_summary', 'mechanical_findings'],
}

const FINDINGS_SCHEMA = {
  type: 'object',
  properties: {
    lens_key: { type: 'string', description: 'Letter identifying the lens (matches the assigned lens)' },
    lens_name: { type: 'string', description: 'Human-readable lens name' },
    findings: { type: 'array', items: FINDING_ITEM },
    coverage_note: { type: 'string', description: 'What this lens examined; what it deliberately did not' },
  },
  required: ['lens_key', 'lens_name', 'findings', 'coverage_note'],
}

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    refuted: {
      type: 'boolean',
      description: 'true if the finding is wrong, intentional/by-design, or unverifiable from the data; false only if confirmed real',
    },
    reasoning: { type: 'string', description: 'Evidence-backed reasoning citing seed/tick/meeting/turn or a rule/metric source file' },
    severity_adjusted: {
      type: 'string',
      enum: ['blocking', 'high', 'medium', 'low', 'informational', 'unchanged'],
      description: 'If not refuted, the verifier may adjust severity. "unchanged" keeps the original.',
    },
  },
  required: ['refuted', 'reasoning'],
}

const SYNTHESIS_SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['CLEAN', 'MINOR_ISSUES', 'SIGNIFICANT_ISSUES'] },
    verdict_rationale: { type: 'string' },
    notable_trends: {
      type: 'array',
      description: 'Evidence-backed gameplay trends worth recording (numbers included)',
      items: { type: 'string' },
    },
    improvement_proposals: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          proposed_id: { type: 'string', description: 'e.g. gp-1, gp-2' },
          title: { type: 'string' },
          finding_ids: { type: 'array', items: { type: 'string' } },
          scope_sketch: { type: 'string' },
          priority: { type: 'string', enum: ['urgent', 'pre-wave-1', 'opportunistic'] },
        },
        required: ['proposed_id', 'title', 'finding_ids', 'scope_sketch', 'priority'],
      },
    },
    summary: { type: 'string', description: 'Final written report path + one-paragraph outcome' },
    report_markdown: {
      type: 'string',
      description: 'Full Markdown audit report body, ready to write to audits/. Sections per the synthesis prompt.',
    },
  },
  required: ['verdict', 'improvement_proposals', 'summary', 'report_markdown'],
}

// ---------------------------------------------------------------------------
// Shared analyzer preamble (data audit, Phase-8 substrate)
// ---------------------------------------------------------------------------

const preamble = (factsPath) => `You are one of 7 parallel analysts auditing the GAMEPLAY DATA of the AiLibi
social-deduction simulation — the committed sample set at ${SAMPLE_DIR} (50 recorded games on the
Phase-8 substrate). A deterministic Extract phase already ran: it derived ground-truth player roles
(re-seeded from the roster — roles are firewalled OUT of the replays), reconstructed the resolved
per-game events, and code-checked both the hard engine rules AND the chain-protocol invariants. Your
findings will go through adversarial verification (a skeptic tries to refute each) and synthesis with
the other analysts.

THE SUBSTRATE (Phase 8 — DESIGN.md §3.2/§3.3/§3.5/§5.2 are the rule sources):
- Roster 9 players / 2 impostors. Tasks are PER-PLAYER instances keyed "{owner}:{map_task_id}"
  (2 per crewmate over the 12 map tasks; agents see map ids only). A victim's incomplete instances
  are dropped on death (§3.5), so the task-win denominator shrinks as crew die.
- Meetings are a reactive ACCUSATION CHAIN (§5.2): an opening turn by the reporter, then a reply
  chain where the next speaker is always the player the previous turn accused, terminated
  deterministically when ANY of: (a) the current turn names no new accusation, (b) the named target
  already took a turn this chain, (c) turn count == living-player count. Then terminal opt_in turns
  (eligible non-speakers with a relevant observation; an opt_in may accuse but CANNOT extend the
  chain), then all living players vote. Termination/next-speaker are pure functions of the recorded
  turns — a short chain is the RULE working, not inherently a defect.
- transcript.turns[] is the ONLY meeting record (MeetingTurn: turn_index, turn_id
  "{meeting_id}:turn-{N}", speaker, turn_kind opening|reply|opt_in, reply_to, observations, claims,
  free text). The reporter's found_body/saw_player observations live on the opening turn. Ballots
  carry primary_reason_id referencing a turn_id. There are NO reports[]/statements[] keys — any
  analysis habit from the pre-8.7 shape is invalid.

Inputs available to you:
- FACTS JSON at: ${factsPath} — READ THIS FIRST. Per game: roles by player; kills (killer + victim +
  their roles); deaths; meetings (trigger, outcome, ejected player + role, per-turn chain facts —
  turn kinds, accusations with both parties' roles, the re-derived termination condition, opt-in
  usage — ballots with target + primary_reason_id, contradiction counts); win reason; per-call
  tokens; failed_calls; plus cross-game aggregates.
- Raw replays at: ${SAMPLE_DIR}/replay-seed-{N}.jsonl (N=0..49) — consult these ONLY for
  transcript-level detail the facts JSON doesn't carry (read the facts JSON FIRST). Each line is a
  JSON record with a "kind" field (tick | meeting | game_over | failed_call). Meeting records carry
  transcript.turns[], ballots[], contradictions[].

Constraints for every lens:
- Read-only. Do not edit any file. You may run non-mutating shell commands (grep, jq, python to slice
  the facts JSON or replays).
- Roles are NOT in the replays — ALWAYS take roles from the FACTS JSON (never infer a role from behavior).
- Every finding MUST cite concrete evidence: a seed + tick (or seed + meeting id + turn index), with
  the numbers.
- TIME-WASTE CAVEAT: the replays record token counts per LLM call but NO wall-clock duration.
  Measure waste via token sinks + call counts, never latency.
- ANCHOR HONESTY: do NOT trust any baseline number quoted in planning docs or this prompt — they go
  stale at every re-record. Derive the recording-time claims yourself from
  ${SAMPLE_DIR}/tournament-eval-report.json (win split, meetings, ejections, SKIP share,
  failed_calls) plus the MANIFEST git_sha, and treat THOSE as the briefed anchors. Cross-check them
  against the facts JSON; a facts-vs-report disagreement is itself a high-severity finding. Any
  cross-set comparison you make must name the other set's sample dir + commit.
- Recently FIXED — do NOT re-flag as new defects unless a game in THIS set still exhibits them: the
  win-condition impostor-elimination gap (Phase 6); hollow-meeting timeouts (Wave 0); impostor
  friendly-fire kills (Wave 0.5 — teammate-aware kill + engine guard); impostor betrayal
  ballots/accusations (7.12 — the firewall now wraps every turn kind and ballots); meeting
  STARVATION (the Phase-8 substrate itself raised meeting_rate to ~0.96). Flag only if the DATA
  shows them recurring.
- No drive-by suggestions: a recommendation must address a cited finding.
- Severity: "blocking" = invalidates this baseline's validity (the set must be re-recorded or the
  engine fixed); "high" = shapes the Wave-1 crew-intel contract; "medium" = worth fixing before
  Wave 1; "low" = opportunistic; "informational" = trend/observation only.

Your lens-specific scope is below. Stay within it; do not duplicate other lenses.

`

// ---------------------------------------------------------------------------
// Lens definitions
// ---------------------------------------------------------------------------

const LENSES = [
  {
    key: 'A',
    name: 'Engine rule-correctness',
    scope: `The Extract phase already flagged the HARD, code-certain violations (engine-rule breaches
surfaced as ActionRejected, impostor-victim kills, win-condition anomalies, chain-protocol rule
breaks) — those go straight to synthesis. YOUR job is twofold:
(1) Interpret each mechanical flag: true BUG or intended-by-design? Confirm against roles + the rule
source (engine/rules.py, meetings/manager.py).
(2) Find SUBTLER correctness issues the mechanical pass cannot: win attributions that disagree with
the final state — note the §3.5 semantics: state.tasks holds per-player instances and the kill
handler already drops a victim's incomplete instances, so CREWMATE_TASKS means "every remaining
instance complete", and CREWMATE_EJECT (alive impostors == 0) is ordered BEFORE the task check in
engine/win_conditions.py; meetings that triggered with no valid trigger; bodies created but never
reportable; any game that continued past the last impostor's elimination (must be zero — flag
loudly if not); per-player task anomalies (an instance progressed by a non-owner, a dead owner's
instance completing after death). Reference engine/win_conditions.py and engine/rules.py. Cite
seed+tick.`,
  },
  {
    key: 'B',
    name: 'Gameplay trends & pacing',
    scope: `From the facts aggregates, characterize gameplay across the 50 games (informational/low
severity unless a trend exposes a defect). Cover: win split + win-REASON distribution (the report
claims CREW 37 all CREWMATE_TASKS / IMP 13 all IMPOSTOR_PARITY — verify, then characterize); game
LENGTH and the restructure's core intent — did 9p/2i lengthen the race (game_over tick distribution;
parity needs 5 crew deaths now) and where does the task-clock sit vs the kill-clock when games end
(stopwatch-race profile)?; kill patterns (rooms, ticks-into-game, witnessed rate, body-report rate,
bodies never reported); meeting patterns (per-game meeting counts, when they happen, 91 body-report /
0 emergency — is the emergency button ever exercised, and is its absence a behavior gap or a
structural one?); per-player task completion pacing (instances/crewmate completed over time, the
§3.5 denominator shrink on deaths); role↔outcome correlations. Report the NUMBERS for each trend.
Flag any degenerate cluster (one win-reason dominating, kills always in one room, all games ending
in a narrow tick band).`,
  },
  {
    key: 'C',
    name: 'Crew conversion failure (detection→ejection)',
    scope: `THE HEADLINE LENS. The report claims 0 ejections across ~91 meetings with ~93% SKIP — the
detection-works/conversion-fails gap is now total. Decompose the pipeline stage by stage WITH COUNTS,
from the facts + transcripts cross-referenced with FACTS roles:
(1) Detection: how many meetings carry contradictions? How many turns' observations/claims actually
reference impostor-incriminating facts (a contradicted alibi, a sighting near the body)?
(2) Accusation: how often does any turn accuse a TRUE impostor (vs an innocent, vs no accusation)?
Does the opening turn (the reporter) accuse at all, or open "unsure" — and when it opens unsure,
does the chain terminate immediately (condition (a) on turn 0)?
(3) Convergence: when a chain does run, does it converge on one target or scatter?
(4) Ballot: do ballots follow the chain — what fraction of ballots' primary_reason_id cite a turn
that accused the ballot's target? Why SKIP ~93% — is the §4.6 skip-confidence rule (as carried into
vote_ballot.j2 v3) the binding constraint at 9 voters, are confidences genuinely low, or do voters
ignore the chain's evidence?
(5) Ejection: with 9 voters, what plurality would an ejection need and how close do real ballots get?
Identify the SINGLE stage where the most conversions die, with numbers — that is Wave-1's target.
Reference eval/vote_correctness.py and the §4.6 rule in agents/strategic/prompts/vote_ballot.j2.
Cite seed+meeting+turn with the votes/roles.`,
  },
  {
    key: 'D',
    name: 'Impostor behavior & chain exploitation',
    scope: `Assess impostor play from transcripts + FACTS roles. Impostors won only ~13/50, all by
parity — characterize whether they are merely passive stopwatch-runners or actively deceptive. Under
the chain protocol: when an impostor is ACCUSED, does the reply rebut/deflect/counter-accuse
plausibly — and does the chain then move off them? Do impostors steer chains toward innocents? Do
they exploit opt_in turns (volunteering misdirection) or stay silent? Do they corroborate/defend a
teammate WITHOUT tripping the 7.12 firewall (betrayal must be 0 — Extract checks it; your job is the
softer coordination quality)? Are fabricated alibis plausible + effective under chain confrontation
(read the alibi-survival figure from the facts/report — don't assume; it is set-specific)? Do
impostors ever vent or sabotage (likely never — confirm the behavioral gap from the action data;
that is the known gp-4 toolkit gap, quantify it for this set)? Do impostor reporters self-report
their own kills' bodies as misdirection? Reference observation/service.py (fellow_impostor_ids
firewall) and eval/alibi_fabrication.py. Cite seed+meeting+turn.`,
  },
  {
    key: 'E',
    name: 'Call economics & waste',
    scope: `CAVEAT: no wall-clock duration is recorded — reason from token sinks + call counts only.
The chain protocol changed the meeting cost model: calls/meeting = 1 opening + (chain length - 1)
replies + opt_in turns + N ballots (no more fixed R=2 statement rounds). From the facts: the
calls-per-meeting distribution and its drivers (chain length vs opt-in count vs roster size); how
that compares to the old protocol's cost at the same roster (old: N reports + 2×N statements + N
votes — is the chain actually cheaper per meeting, as designed?); the biggest token sinks; meetings
that run a long chain + full opt-ins and then SKIP anyway (deliberation that buys nothing — quantify
the wasted calls); opt_in turns that add no new observations/claims (pure pass-throughs — eligible
players who had nothing to say; is the eligibility gate too loose?); failed_calls (the report claims
0 — verify; any non-zero is high-severity given the parse-tolerance work in 8.9); token totals
(~1.50M in / ~85.5K out claimed — verify). Propose concrete reductions (each with the call/token
savings). Cite seed + counts.`,
  },
  {
    key: 'F',
    name: 'Metric soundness, coverage & balance',
    scope: `Three sub-checks. (1) Metric soundness ON THE NEW SUBSTRATE: the metrics were re-pointed to
transcript.turns in 8.10 — sanity-check the tournament-report metrics (meeting_rate,
vote_correctness, accusation_calibration, alibi_fabrication, cost_dashboard) against the raw facts.
Do any mislead a Wave-1 A/B? Specifically: with 0 ejections, vote_correctness_rate and
ejection_accuracy are null/small_n — what is the usable Wave-1 LEAD METRIC and its denominator (the
gp-3 metric-hygiene successor question: a contradiction→ballot conversion rate? accusation
precision?); meeting_rate at 0.96 is near ceiling — does it still discriminate?; does the
body/emergency trigger split read correctly now that triggers are recorded? (2) Seed coverage /
representativeness: do the 50 seeds cover diverse situations (kill counts, meeting counts, chain
lengths, room spread) or cluster degenerately? (3) Balance: is CREW 74% — all by task-stopwatch,
none by deduction — a healthy pre-Wave-1 baseline or a new degeneracy mirror-imaging the old
impostor-favored one? Is IMPOSTOR_PARITY-only winning evidence the impostor side lacks any other
viable path (ties to the gp-4 toolkit gap)? Reference eval/*.py. Cite numbers.`,
  },
  {
    key: 'G',
    name: 'Chain-protocol dynamics',
    scope: `The protocol as a MECHANISM (rule VIOLATIONS are Extract's job; you judge whether the
protocol produces good deliberation). From the per-meeting chain facts: the chain-length
distribution and the termination-condition mix — what fraction end by (a) no-new-accusation, (b)
re-accusation cycle, (c) the living-player cap? If (a) on the opening turn dominates (reporter opens
"unsure" → instant termination → straight to opt-ins/vote), the chain never engages — quantify how
often the protocol's reactive core actually runs. When the chain DOES run: does the accused actually
rebut the accusation made against them (responsive replies) or talk past it? Do re-accusation cycles
(condition b) represent genuine convergence (two players locked on each other) or ping-pong noise?
Opt-in usage: how many eligible non-speakers exist per meeting, how many speak, do their
observations add NEW information (facts not already in the chain), and do ballots cite opt_in turns?
Does speaking ORDER shape outcomes (is the opening speaker's accusation disproportionately followed
in ballots)? Propose protocol-level tunings only where a cited dynamic warrants one (e.g. eligibility
gate, opening-turn prompt shape) — prompt-level fixes belong to Wave 1. Cite seed+meeting+turn.`,
  },
]

// ---------------------------------------------------------------------------
// Phase 1: Extract (deterministic facts + code-certain rule/protocol checks)
// ---------------------------------------------------------------------------

phase('Extract')
log(`Extracting deterministic facts + rule/protocol checks from ${SAMPLE_DIR}.`)

const extract = await agent(
  `You are the deterministic Extract phase of a gameplay-data audit on the Phase-8 substrate. Build a
structured FACTS file and code-check the hard violations for the committed replay set at ${SAMPLE_DIR}
(replay-seed-0.jsonl .. replay-seed-49.jsonl). Roles are firewalled OUT of the replays, so you must
re-derive them. (Unlike the read-only analysis lenses that follow, THIS Extract phase MAY write — it
updates the extractor script and writes the facts JSON to a temp path.)

START FROM THE COMMITTED EXTRACTOR: audits/workflows/extract_gameplay_facts.py. It was written for the
pre-Phase-8 7p/2i set and is structurally sound (role re-derivation via orchestrator.seeder, a full
advance_tick + apply_meeting_result re-walk with per-tick state-hash verification, hard-rule
classification via ActionRejected reasons, win cross-checks, fail-loud invariants). UPDATE IT IN PLACE
(edit the file; it gets committed alongside the audit report) rather than writing a new script:

1. RE-POINT: SAMPLE_DIR / SEEDSET constants -> "${SAMPLE_DIR}" and its basename. The roster.json read
   already parameterizes players/impostors/tasks, so 9p/2i seeds correctly.

2. VERIFY THE WALK AGAINST THE 8.7 SCHEMA: the MeetingResult(...) construction from each
   MeetingReplayEntry must match the current meetings/schemas.py (transcript is now the turns-based
   MeetingTranscript; check field-by-field, including the trigger field). The state-hash self-checks
   (per-tick and post-meeting) stay — they are the audit's trust anchor.

3. KEEP every existing per-game fact and hard-rule check (kills with roles, deaths, ActionRejected
   classification, impostor-victim kills, the win-condition-gap check, the recorded-winner vs
   final-state cross-check — note engine/win_conditions.py orders CREWMATE_EJECT (alive impostors
   == 0) BEFORE the task check, and state.tasks already excludes dead owners' incomplete instances,
   so the existing done==total comparison remains valid).

4. ADD PER-MEETING CHAIN FACTS (the v2 reason-for-being). For each meeting, from
   transcript.turns: n_turns; counts by turn_kind (opening/reply/opt_in); chain_length (opening +
   replies); the re-derived TERMINATION CONDITION — re-walk the recorded chain turns against the
   3-condition rule in meetings/manager.py (DESIGN.md §5.2 PHASE 2: (a) no new accusation named,
   (b) named target already took a turn this chain, (c) turn count == living players) and record
   which condition fired; accusations as [{turn_index, speaker, speaker_role, accused,
   accused_role}] (roles from the re-seeded ground truth); opt_in speakers + whether each opt_in
   turn carries any observations/claims (vs an empty pass); ballots as [{voter, voter_role, target,
   target_role, primary_reason_id}]; skip_count; and ballot_follows_chain — for each non-skip
   ballot, whether primary_reason_id cites a turn that accused that ballot's target.

5. ADD CHAIN-PROTOCOL MECHANICAL CHECKS (code-certain; each real violation -> one
   mechanical_findings entry citing "seed N meeting M turn K" + roles):
   - TERMINATION violation: the recorded chain continues past a turn where a termination condition
     had fired, or stops while none had fired (re-derive from the turns; the rule is deterministic).
   - TURN-ID/ORDER violation: turn_index not contiguous from 0; turn_id != "{meeting_id}:turn-{index}";
     turn 0 not turn_kind=="opening"; meetings/transcript.py::is_canonically_ordered false.
   - REPLY_TO integrity: a reply whose reply_to is not an EARLIER turn_id of this meeting; an
     opening/opt_in turn with a non-null reply_to.
   - OPT-IN containment: any reply turn after the first opt_in turn (opt-ins are terminal and cannot
     extend the chain); an opt_in by a player who already took a chain turn this meeting.
   - FIREWALL (7.12, per-turn): any turn of ANY kind where an impostor's accusation names a fellow
     impostor, or any ballot where an impostor's target is a fellow impostor. Must be 0.
   - PRIMARY_REASON_ID dangling: a ballot referencing a turn_id that does not exist in this
     meeting's transcript.
   - Dead speakers: any turn whose speaker is dead at the meeting's tick, or a ballot from a dead
     voter.
   If a category has zero violations, do not invent a finding for it.

6. EXTEND THE AGGREGATES: everything existing PLUS total ballots, skip ballots (count + share),
   ejections by role, chain-length histogram, termination-condition counts, opening-turn-accusation
   count (how many openings name an accusation at all), accusations at impostors vs at innocents
   (totals), opt_in totals (eligible-spoke-substantive if derivable), ballot_follows_chain totals,
   and contradiction totals.

7. SELF-CHECK INVARIANTS (keep the existing fail-loud set: per-seed impostor count == roster,
   games_analyzed == file count, meeting-record count match, kill-victim/death consistency,
   state-hash matches) and ADD: every meeting's transcript.turns is non-empty with exactly one
   opening at index 0; ballot voters are alive at the meeting tick. Print each check; RAISE on any
   failure — a silent extraction bug poisons the whole audit.

Run it with: PYTHONPATH=<repo root> uv run python audits/workflows/extract_gameplay_facts.py
The facts JSON goes to $TMPDIR/ailibi-gameplay-facts-<seedset>.json (absolute path).

Return: facts_path (absolute), games_analyzed, a facts_summary (the aggregates in prose, with numbers
— including the chain/ballot aggregates), and mechanical_findings (code-certain only; empty array if
the set is clean). Severity: "blocking" for eval-invalidating violations (impostor-victim kill,
dead-player action/turn/ballot, wrong win attribution, state-hash mismatch, firewall breach),
"high" for protocol-rule breaks (termination/opt-in/turn-id/reply_to/dangling-reason violations),
"informational" for dead-or-unknown-player action rejections (same-tick kill races, per the v1
convention).`,
  {
    label: 'extract:facts-and-protocol-check',
    phase: 'Extract',
    schema: EXTRACT_SCHEMA,
  }
)

const factsPath = extract.facts_path
const mechanicalFindings = (extract.mechanical_findings || []).map((f, i) => ({
  ...f,
  lens_key: 'A',
  lens_name: 'Engine & protocol correctness (mechanical)',
  mechanical: true,
  fully_qualified_id: `MECH-${f.id || i + 1}`,
}))

log(`Extract complete: ${extract.games_analyzed} games. ${mechanicalFindings.length} code-certain violations. Facts at ${factsPath}.`)

// ---------------------------------------------------------------------------
// Phase 2: Analyze (7 parallel lenses)
// ---------------------------------------------------------------------------

phase('Analyze')
log(`Spawning ${LENSES.length} parallel analysis lenses over the facts + transcripts.`)

const lensReports = await parallel(
  LENSES.map((l) => () =>
    agent(
      preamble(factsPath) +
        `\nLens ${l.key} — ${l.name}\n\n${l.scope}\n\n` +
        `Output a findings list with lens_key="${l.key}" and lens_name="${l.name}". ` +
        `If nothing in scope, return an empty findings array and a coverage_note explaining what you examined.`,
      {
        label: `analyze:${l.key}-${l.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 28)}`,
        phase: 'Analyze',
        schema: FINDINGS_SCHEMA,
      }
    )
  )
)

const lensFindings = lensReports
  .filter(Boolean)
  .flatMap((r) =>
    r.findings.map((f) => ({
      ...f,
      lens_key: r.lens_key,
      lens_name: r.lens_name,
      mechanical: false,
      fully_qualified_id: `${r.lens_key}-${f.id}`,
    }))
  )

log(`Analyze complete. ${lensFindings.length} judgment findings across ${lensReports.filter(Boolean).length} lenses (plus ${mechanicalFindings.length} mechanical).`)

// ---------------------------------------------------------------------------
// Phase 3: Verify (hybrid — mechanical pass through; judgment findings 3-skeptic)
// ---------------------------------------------------------------------------

phase('Verify')

if (lensFindings.length === 0) {
  log('No judgment findings to verify. Mechanical findings (if any) pass through.')
}

const verifiedLens = await parallel(
  lensFindings.map((f) => () =>
    agent(
      `You are verifying-by-trying-to-refute a gameplay-data audit finding for AiLibi (Phase-8
substrate: 9p/2i roster, per-player task instances, reactive accusation-chain meetings — transcripts
are an ordered turns[] list, ballots carry primary_reason_id referencing turn ids). The data is the
recorded replay set at ${SAMPLE_DIR}; the facts JSON is at ${factsPath}; roles come from the facts
JSON (firewalled out of the replays). You are this finding's ONLY verifier — work all three angles
below before deciding; your verdict alone keeps or drops it.

Finding:
  Lens: ${f.lens_key} - ${f.lens_name}
  ID: ${f.fully_qualified_id}
  Severity: ${f.severity}
  Title: ${f.title}
  Claim: ${f.claim}
  Evidence: ${f.evidence}
  Repair/improvement hint: ${f.repair_hint || '(none)'}

Your job: try to refute it. Verify by reading the cited seed's replay (and the facts JSON for
roles), or the cited metric/rule source. Work ALL THREE angles:
1. Literal: does the cited seed/tick/meeting/turn actually show what the finding claims (roles,
   ticks, turns, votes, numbers)? Roles come from the facts JSON, never inferred from behavior.
2. By-design: is the behavior intentional rather than a bug — the §5.2 chain termination is
   deterministic (a short chain, an un-extended opt_in accusation, or an immediate opening-turn
   termination is the rule working); §3.5 drops a dead owner's incomplete task instances (a
   shrinking task denominator is correct); the §4.6 skip rule in vote_ballot.j2 intentionally
   biases toward SKIP under low confidence; a metric's stated caveat (null ejection metrics at 0
   ejections, alibi_fabrication's conservative lower-bound) is documented, not a bug. Check
   DESIGN.md §3.5/§5.2, engine/rules.py, meetings/manager.py, or the metric source before
   confirming.
3. Context: is there invalidating context elsewhere in the set (other seeds/meetings), a numeric
   error, or a token-proxy time-waste claim presented as a latency claim (no wall-clock exists)?

Refute ONLY with a concrete basis from those checks, cited in your reasoning. If the evidence
cannot be verified either way after honest effort, set refuted=true with reasoning starting
"unverifiable:". Output the structured verdict.`,
      {
        label: `verify:${f.fully_qualified_id}`,
        phase: 'Verify',
        schema: VERDICT_SCHEMA,
      }
    ).then((verdict) => {
      if (!verdict) {
        // The skeptic died (skipped / terminal API error): pass the finding through
        // UNVERIFIED and flagged — synthesis must label it, never launder it as verified.
        return {
          ...f,
          survived: true,
          unverified: true,
          effective_severity: f.severity,
          severity_changed: false,
          verifier_votes: [],
          refute_count: 0,
        }
      }
      const adjusted =
        verdict.severity_adjusted && verdict.severity_adjusted !== 'unchanged'
          ? verdict.severity_adjusted
          : f.severity
      return {
        ...f,
        survived: !verdict.refuted,
        unverified: false,
        effective_severity: adjusted,
        severity_changed: adjusted !== f.severity,
        verifier_votes: [verdict],
        refute_count: verdict.refuted ? 1 : 0,
      }
    })
  )
)

const survivedLens = verifiedLens.filter((v) => v.survived)
const refutedLens = verifiedLens.filter((v) => !v.survived)
const unverifiedLens = survivedLens.filter((v) => v.unverified)
// Mechanical findings are code-certain — they bypass verification.
const allSurviving = [...mechanicalFindings, ...survivedLens]

log(`Verify complete. ${survivedLens.length}/${lensFindings.length} judgment findings survived (${refutedLens.length} refuted, ${unverifiedLens.length} unverified pass-through); ${mechanicalFindings.length} mechanical passed through. ${allSurviving.length} total.`)

// ---------------------------------------------------------------------------
// Phase 4: Synthesis
// ---------------------------------------------------------------------------

phase('Synthesis')

const synthesisInput = {
  sample_dir: SAMPLE_DIR,
  games_analyzed: extract.games_analyzed,
  facts_summary: extract.facts_summary,
  mechanical_finding_count: mechanicalFindings.length,
  judgment_raw_count: lensFindings.length,
  judgment_refuted_count: refutedLens.length,
  judgment_unverified_count: unverifiedLens.length,
  surviving_findings: allSurviving.map((f) => ({
    lens: f.lens_key,
    id: f.fully_qualified_id,
    mechanical: !!f.mechanical,
    unverified: !!f.unverified,
    severity: f.effective_severity || f.severity,
    severity_original: f.severity,
    severity_adjusted_by_verifier: !!f.severity_changed,
    title: f.title,
    claim: f.claim,
    evidence: f.evidence,
    repair_hint: f.repair_hint,
  })),
  per_lens_coverage: lensReports
    .filter(Boolean)
    .map((r) => ({ lens: r.lens_key, name: r.lens_name, coverage: r.coverage_note })),
}

const synthesis = await agent(
  `You are synthesizing a gameplay-data audit of AiLibi's committed replay set ${SAMPLE_DIR} — the
first audit of the Phase-8 substrate (9p/2i, per-player tasks, accusation-chain meetings). A
deterministic extractor produced code-certain rule/protocol violations (NOT subject to refutation); 7
analysis lenses produced judgment findings; each judgment finding faced ONE adversarial skeptic —
refuted findings were dropped, and any finding whose skeptic failed to run carries unverified:true.
Label unverified findings explicitly in the report ("unverified — skeptic did not run"); never
present them as verified. What remains is the load-bearing finding set.

Input data (JSON):
${JSON.stringify(synthesisInput, null, 2)}

Your output has two parts:
1. Structured synthesis: verdict (CLEAN / MINOR_ISSUES / SIGNIFICANT_ISSUES) + rationale;
   notable_trends (evidence-backed, with numbers); improvement_proposals (group related findings; one
   proposal per group with a reproducible scope sketch — cite the seed+tick/meeting+turn to reproduce
   — and a priority, where "urgent" = invalidates this baseline / blocks the Phase-8 close,
   "pre-wave-1" = must shape or precede the Wave-1 crew-intel contract, "opportunistic" = later).
2. report_markdown: the full Markdown report body, to be written to
   audits/audit-YYYY-MM-DD-HHMM-gameplay-data.md. Use this section structure:
   - "# Gameplay Data Audit — YYYY-MM-DD HH:MM (${SAMPLE_DIR}, Phase-8 substrate)"
   - "## 1. Verdict" (CLEAN | MINOR_ISSUES | SIGNIFICANT_ISSUES + 2-3 paragraphs; state explicitly
     whether the new baseline is VALID to anchor Wave-1 work on)
   - "## 2. Environment" (timestamp from \`date\`, audited HEAD from \`git log -1 --oneline\`, sample
     dir, games analyzed, mechanical vs judgment finding counts, refute rate)
   - "## 3. Confirmed bugs & rule violations" (mechanical findings first — labelled code-certain —
     then surviving engine/correctness judgment findings; use the verifier-adjusted severity and note
     where severity_adjusted_by_verifier is true; cite evidence + repair hint)
   - "## 4. The conversion pipeline (headline)" — the stage-by-stage detection→ejection decomposition
     with counts at every stage (contradictions → incriminating turns → accusations at impostors →
     chain convergence → ballots following the chain → ejections), naming the SINGLE stage where most
     conversions die; plus an explicit judgment: is the crew-favored 74%-by-stopwatch split a healthy
     substrate for Wave-1 or a new degeneracy (cite the impostor-passivity evidence either way)?
   - "## 5. Gameplay trends & pacing" (the notable_trends, with numbers — include the
     did-the-restructure-lengthen-the-race answer)
   - "## 6. Decision-quality findings" (crew + impostor lenses)
   - "## 7. Chain-protocol dynamics" (termination mix, chain engagement rate, opt-in usage, order
     effects)
   - "## 8. Call-economics findings" (with the no-wall-clock caveat stated explicitly; the
     old-vs-new protocol cost comparison)
   - "## 9. Metric soundness, coverage & balance" (including the named Wave-1 lead-metric
     recommendation given 0 ejections)
   - "## 10. Improvement proposals" (one subsection each: proposed_id, title, finding ids, scope
     sketch with a reproduction citation, priority)
   - "## 11. Lens coverage notes" (per-lens what-was-examined)

After producing the structured synthesis + report_markdown, write the report to disk in THIS EXACT
ORDER (do NOT reorder; do NOT hardcode or guess a date):
- Step 1: run \`date '+%Y-%m-%d-%H%M'\` via the Bash tool and CAPTURE its stdout.
- Step 2: compute path = audits/audit-{captured-stdout}-gameplay-data.md
- Step 3: use the Write tool to write report_markdown to that path.
Skipping Step 1 or using a hardcoded/guessed timestamp is a failure.

Report the final written path in the "summary" field.`,
  {
    label: 'synthesize',
    phase: 'Synthesis',
    schema: SYNTHESIS_SCHEMA,
  }
)

log(`Synthesis complete. Verdict: ${synthesis.verdict}. ${synthesis.improvement_proposals.length} improvement proposals.`)

return {
  verdict: synthesis.verdict,
  games_analyzed: extract.games_analyzed,
  mechanical_findings: mechanicalFindings.length,
  judgment_findings_surviving: survivedLens.length,
  judgment_findings_refuted: refutedLens.length,
  judgment_findings_unverified: unverifiedLens.length,
  improvement_proposals: synthesis.improvement_proposals,
  notable_trends: synthesis.notable_trends,
  summary: synthesis.summary,
  tokens_spent: budget.spent(),
}
