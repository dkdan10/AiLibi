// Gameplay-data audit Workflow.
//
// Analyzes a committed replay sample set (default replays/samples/7p2i, 50 games)
// to surface gameplay BUGS, TRENDS, decision-quality faults, time-wasters, and
// concrete improvement proposals — purely from the recorded data (no Ollama; the
// recorded LLM outputs are model-agnostic and roles are re-derived from the seeder).
//
// Structure: a deterministic Extract pre-phase (one agent writes+runs a Python
// extractor that derives ground-truth roles, reconstructs resolved events, and
// code-checks the hard rule violations) → 6 parallel analysis lenses → HYBRID
// verification (code-certain mechanical findings pass straight through; LLM
// judgment findings get 3 adversarial skeptics, majority-refute drops) → synthesis
// that writes a Markdown report to audits/.
//
// Invoke from a Claude Code session:
//   Workflow({scriptPath: "audits/workflows/gameplay-data-audit.workflow.js"})
//   Workflow({scriptPath: "audits/workflows/gameplay-data-audit.workflow.js", args: "replays/samples/7p2i"})
//
// Output: audits/audit-YYYY-MM-DD-HHMM-gameplay-data.md (synthesis agent writes it).

export const meta = {
  name: 'gameplay-data-audit',
  description: 'Structured audit of a committed replay set: deterministic rule-checks + 6 analysis lenses (trends, bugs, crew/impostor decisions, time-waste, metrics) + adversarial verify + synthesis. Output is a findings + improvement-proposal report.',
  whenToUse: 'After a meeting-heavy eval set is recorded; analyzes gameplay data to find bugs/trends/faults and propose improvements before agent-intelligence work.',
  phases: [
    { title: 'Extract', detail: 'One agent derives roles + resolved events + code-certain rule violations into a facts JSON' },
    { title: 'Analyze', detail: '6 parallel lenses over the facts + transcripts' },
    { title: 'Verify', detail: 'Mechanical findings pass through; judgment findings get 3 skeptics (majority refutes to drop)' },
    { title: 'Synthesis', detail: 'Group findings, propose improvements, write report' },
  ],
}

// args = sample dir to audit; defaults to the canonical 7p/2i set.
const SAMPLE_DIR = typeof args === 'string' && args.trim() ? args.trim() : 'replays/samples/7p2i'

// ---------------------------------------------------------------------------
// Schemas
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
    evidence: { type: 'string', description: 'Concrete citation: "seed N tick T" or "seed N meeting M", with the numbers/roles' },
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
      description: 'Human-readable digest of the aggregates (win split + reasons, kills, deaths, meetings, ejections by role, failed_calls, token totals) for the analyzer lenses to anchor on',
    },
    mechanical_findings: {
      type: 'array',
      description: 'Code-certain rule violations found deterministically (these BYPASS adversarial verification). Empty array if none.',
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
    reasoning: { type: 'string', description: 'Evidence-backed reasoning citing seed/tick/meeting or a rule/metric source file' },
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
// Shared analyzer preamble (data audit)
// ---------------------------------------------------------------------------

const preamble = (factsPath) => `You are one of 6 parallel analysts auditing the GAMEPLAY DATA of the AiLibi
social-deduction simulation — the committed sample set at ${SAMPLE_DIR} (50 recorded games). A
deterministic Extract phase already ran: it derived ground-truth player roles (re-seeded from the
roster — roles are firewalled OUT of the replays), reconstructed the resolved per-game events, and
code-checked the hard rule violations. Your findings will go through adversarial verification
(skeptics try to refute each) and synthesis with the other analysts.

Inputs available to you:
- FACTS JSON at: ${factsPath} — READ THIS FIRST. Per game: roles by player; kills (killer + victim +
  their roles); deaths; meetings (outcome, ejected player + their role, ballots, contradictions);
  win reason; per-call tokens/cost; failed_calls; plus cross-game aggregates.
- Raw replays at: ${SAMPLE_DIR}/replay-seed-{N}.jsonl (N=0..49) — consult these ONLY for
  transcript-level detail the facts JSON doesn't carry (read the facts JSON FIRST). Each line is a
  JSON record with a "kind" field (tick | meeting | game_over | failed_call). Meeting records carry
  transcript.reports[], transcript.statements[], ballots[], contradictions[].

Constraints for every lens:
- Read-only. Do not edit any file. You may run non-mutating shell commands (grep, jq, python to slice
  the facts JSON or replays).
- Roles are NOT in the replays — ALWAYS take roles from the FACTS JSON (never infer a role from behavior).
- Every finding MUST cite concrete evidence: a seed + tick (or seed + meeting id), with the numbers.
- TIME-WASTE CAVEAT: the replays record token counts + cost per LLM call but NO wall-clock duration.
  Measure time-waste via token sinks + call/round counts, never latency.
- No drive-by suggestions: a recommendation must address a cited finding.
- Recently FIXED — do NOT re-flag as new defects unless a game in THIS set still exhibits them: the
  win-condition impostor-elimination gap (closed Phase 6, 2026-05-30, with contradiction-detection
  wiring) and the hollow-meeting timeouts (fixed at Wave-0 close via sequential meeting-collection +
  num_ctx). Flag only if the DATA shows them recurring.
- Severity: "blocking" = corrupts the eval set's validity; "high" = shapes Wave-1 work; "medium" =
  worth fixing before Wave 1; "low" = opportunistic; "informational" = trend/observation only.

Your lens-specific scope is below. Stay within it; do not duplicate other lenses.

`

// ---------------------------------------------------------------------------
// Lens definitions
// ---------------------------------------------------------------------------

const LENSES = [
  {
    key: 'A',
    name: 'Engine rule-correctness',
    scope: `The Extract phase already flagged the HARD, code-certain rule violations (impostor-victim
kills, dead-player actions, kill cooldown/same-room breaches, non-adjacent moves, win-condition
anomalies) — those go straight to synthesis. YOUR job is twofold:
(1) Interpret each mechanical flag: is it a true BUG or intended-by-design? E.g. should an impostor be
able to kill a fellow impostor at all (check engine/rules.py kill validator)? Confirm against roles.
(2) Find SUBTLER correctness issues the mechanical pass cannot: win attributions that disagree with the
final state (winner=CREWMATES while impostors alive + tasks incomplete; winner=IMPOSTORS without parity/
sabotage); the GameOver.reason not matching the state; meetings that triggered with no valid trigger;
bodies that were created but never reportable; any game that CONTINUED after the last impostor was
eliminated (the 6.3 win-condition gap — should be zero now; flag loudly if not).
Reference engine/win_conditions.py (the 5-way order) and engine/rules.py. Cite seed+tick.`,
  },
  {
    key: 'B',
    name: 'Gameplay trends',
    scope: `From the facts aggregates, characterize gameplay trends across the 50 games (informational/
low severity unless a trend exposes a defect). Cover: win split (crew / impostor / tick-budget) and the
win-REASON distribution (CREWMATE_TASKS vs CREWMATE_EJECT vs IMPOSTOR_PARITY vs IMPOSTOR_SABOTAGE); kill
patterns (rooms, ticks-into-game, witnessed rate, body-report rate, bodies never reported); meeting
patterns (trigger type, when meetings happen, eject-vs-skip rate, votes-per-meeting); task-completion
timing and whether games end too early/late; role↔outcome correlations. Report the NUMBERS for each
trend. Flag any trend that looks degenerate (e.g. one win-reason dominating, kills always in one room).`,
  },
  {
    key: 'C',
    name: 'Crew decision quality',
    scope: `Read meeting transcripts + ballots (raw replays) cross-referenced with FACTS roles. Assess
crew social-deduction quality: WHY did the wrong (crewmate) ejections happen — a cascade despite the
§4.6 skip-confidence-threshold (0.60), or over-trusting a confident liar? Are accusations and votes
GROUNDED in real observations/contradictions, or noise? Why is the accusation-calibration ECE the
value it is (read the actual ECE from the facts/report — don't assume)? Is voting SKIP-heavy or scattered vs piling onto the strongest case? Does the §4.6 threshold
help (avoids wrong ejects) or hurt (lets impostors survive)? Reference eval/vote_correctness.py,
eval/accusation_calibration.py, and the §4.6 rule in agents/strategic/prompts/vote_ballot.j2. Cite
seed+meeting with the votes/roles.`,
  },
  {
    key: 'D',
    name: 'Impostor behavior & coordination',
    scope: `Assess impostor play from transcripts + FACTS roles. Do impostors USE their team knowledge
(fellow_impostor_ids): do they avoid accusing each other, corroborate/defend a teammate — or do they
accuse fellow impostors and play uncoordinated (a Wave-2 gap to quantify with counts)? Are their
fabricated alibis plausible + effective (read the alibi-survival figure from the facts JSON / eval report — don't assume a number; it is set-specific)? Do impostors ever vent or
sabotage at all (likely never — confirm the behavioral gap from the action data)? Reference
observation/service.py (fellow_impostor_ids firewall) and eval/alibi_fabrication.py. Cite seed+meeting.`,
  },
  {
    key: 'E',
    name: 'Performance & time-waste',
    scope: `CAVEAT: no wall-clock duration is recorded — reason from token sinks + call/round counts only.
Find: the failed_call chronology bug (qwen emits non-chronological alibis from_tick>to_tick → schema
reject → aborted/degraded meetings — previously observed in seed 36; find ALL instances across the set
and quantify occurrences + meetings lost (don't stop at the known case)); the biggest
token sinks (the R=2 statement phase is N×2 calls/meeting — does round 2 earn its cost? do round-2
statements actually change votes vs round-1?); meetings that fully deliberate then SKIP (wasted rounds);
any residual empty / "missed deadline" entries. Propose concrete reductions (each with the token/call
savings). Cite seed + counts.`,
  },
  {
    key: 'F',
    name: 'Metric soundness, coverage & balance',
    scope: `Three sub-checks. (1) Metric soundness: sanity-check the 5 tournament-report metrics (meeting_rate,
vote_correctness, accusation_calibration, alibi_fabrication, cost_dashboard) against the raw facts — do
any have caveats that mislead a Wave-1 A/B (e.g. alibi_fabrication is a conservative lower-bound; the
body/emergency trigger split is heuristic; calibration binning edge cases)? (2) Seed coverage /
representativeness: do the 50 seeds cover diverse situations (kill counts, meeting counts, room spread)
or cluster degenerately? (3) Balance: is the crew-win split (read the actual figure from the facts) a
healthy pre-Wave-2 baseline or degenerate? Reference eval/*.py. Cite numbers.`,
  },
]

// ---------------------------------------------------------------------------
// Phase 1: Extract (deterministic facts + code-certain rule checks)
// ---------------------------------------------------------------------------

phase('Extract')
log(`Extracting deterministic facts + rule-checks from ${SAMPLE_DIR}.`)

const extract = await agent(
  `You are the deterministic Extract phase of a gameplay-data audit. Build a structured FACTS file and
code-check the hard rule violations for the committed replay set at ${SAMPLE_DIR} (replay-seed-0.jsonl
.. replay-seed-49.jsonl). Roles are firewalled OUT of the replays, so you must re-derive them. (Unlike the read-only analysis
lenses that follow, THIS Extract phase MAY write — it creates its Python script and the facts JSON at a
temp path.)

Write and run a Python script (uv run python) that, for each seed present in ${SAMPLE_DIR}:

1. DERIVE GROUND-TRUTH ROLES (the validated recipe):
   - from engine.world import load_canonical_map
   - from orchestrator.seeder import seed_initial_state
   - read ${SAMPLE_DIR}/roster.json -> num_players, num_impostors, tasks_per_crewmate
   - state = seed_initial_state(seed=SEED, game_map=load_canonical_map(), num_players=..., num_impostors=..., tasks_per_crewmate=...)
   - roles = {pid: player.role for pid, player in state.players.items()}
   - VALIDATE: each seed must have exactly num_impostors impostors; abort/flag if not.
   (Run with PYTHONPATH=<repo root> uv run python so the engine/orchestrator/api packages import.)

2. RECONSTRUCT RESOLVED EVENTS per game. Prefer api.replay_loader.ReplayLoader (it re-runs the engine and
   surfaces resolved events incl. Killed actor/target/room and ActionRejected) — read api/replay_loader.py
   for its interface. If simpler, read the raw replay JSONL directly: tick records carry actions[]
   (move/do_task/kill/vent/report/emergency/sabotage/wait with actor+target/room fields); meeting records
   carry outcome, ejected_player_id, ballots[], contradictions[], transcript; game_over carries winner +
   reason; failed_call carries error_type/error_message/model/tokens. (See orchestrator/replay.py for the
   record schemas and engine/events.py for event types.)

3. EMIT a FACTS JSON to an absolute temp path (e.g. under $TMPDIR or /tmp, name it
   ailibi-gameplay-facts-<seedset>.json). Per game include: seed, roles, winner + reason, kills
   [{tick, killer, killer_role, victim, victim_role, room}], deaths, meetings [{meeting_id, tick,
   triggered_by, outcome, ejected_player_id, ejected_role, ballots, n_contradictions}], per-call token
   totals (input/output/cost) and failed_calls. Also top-level fields: "git_head" (the output of
git rev-parse HEAD) and "sample_dir", plus an "aggregates" object (win split + reason
   counts, total kills, impostor-victim kills, total meetings, ejections by ejected-role, total/failed
   calls, token totals).

4. CODE-CHECK these HARD rule violations (deterministic, exhaustive). Each real violation -> one entry in
   mechanical_findings (cite "seed N tick T" + the roles):
   - a kill whose victim_role == IMPOSTOR (impostor killed impostor)
   - any action attributed to an already-dead player
   - a kill that ignored cooldown or was cross-room (compare against engine/rules.py)
   - a move to a non-adjacent room
   - a body reported by a dead/ineligible player
   - a game whose recorded winner/reason contradicts the final alive-roles + tasks state, OR a game that
     continued past the tick where alive impostors hit 0 (win-condition gap)
   If a category has zero violations, do not invent a finding for it.

5. SELF-CHECK INVARIANTS (print each result; FAIL LOUD / raise on any mismatch — the entire audit trusts
   this facts file, so a silent extraction bug poisons everything): per seed, impostors found ==
   roster.num_impostors; games_analyzed == count of replay-seed-*.jsonl files in the set; total meetings
   in the facts == total "kind":"meeting" records across the replays; every kill recorded with a death
   has its victim in that game's deaths. Surface these counts in facts_summary so the lenses can trust it.

Return: facts_path (absolute), games_analyzed, a facts_summary (the aggregates in prose, with numbers),
and mechanical_findings (code-certain only; empty array if the set is clean). Use severity "blocking"
for eval-invalidating violations (impostor-victim kill, dead-player action, wrong win attribution),
"high"/"medium" otherwise.`,
  {
    label: 'extract:facts-and-rulecheck',
    phase: 'Extract',
    schema: EXTRACT_SCHEMA,
  }
)

const factsPath = extract.facts_path
const mechanicalFindings = (extract.mechanical_findings || []).map((f, i) => ({
  ...f,
  lens_key: 'A',
  lens_name: 'Engine rule-correctness (mechanical)',
  mechanical: true,
  fully_qualified_id: `MECH-${f.id || i + 1}`,
}))

log(`Extract complete: ${extract.games_analyzed} games. ${mechanicalFindings.length} code-certain rule violations. Facts at ${factsPath}.`)

// ---------------------------------------------------------------------------
// Phase 2: Analyze (6 parallel lenses)
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
        label: `analyze:${l.key}-${l.name.toLowerCase().replace(/\s+/g, '-').slice(0, 28)}`,
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
    parallel(
      Array.from({ length: 3 }, (_, lensIndex) => () =>
        agent(
          `You are verifying-by-trying-to-refute a gameplay-data audit finding for AiLibi. The data is the
recorded replay set at ${SAMPLE_DIR}; the facts JSON is at ${factsPath}; roles come from the facts JSON
(firewalled out of the replays).

Finding:
  Lens: ${f.lens_key} - ${f.lens_name}
  ID: ${f.fully_qualified_id}
  Severity: ${f.severity}
  Title: ${f.title}
  Claim: ${f.claim}
  Evidence: ${f.evidence}
  Repair/improvement hint: ${f.repair_hint || '(none)'}

Your job: try to refute it. Default to refuted=true if uncertain. Verify by reading the cited seed's
replay (and the facts JSON for roles), or the cited metric/rule source. Common refutation grounds:
- The cited seed/tick/meeting does not show what the finding claims.
- The roles are misread (check the facts JSON, not behavior).
- The behavior is intentional/by-design (documented in DESIGN.md, a rule in engine/rules.py, the §4.6
  skip rule, or a metric's stated caveat) rather than a bug.
- It's a token-proxy time-waste claim presented as a latency claim (no wall-clock exists) — refute if it
  overclaims.
- The evidence does not actually support the claim, or the numbers are wrong.

Lens index ${lensIndex + 1} of 3: ${
            lensIndex === 0
              ? 'Read the cited replay/facts literally — does the data state what the finding claims (roles, ticks, votes)?'
              : lensIndex === 1
                ? 'Check whether the behavior is intentional/by-design (a rule, the §4.6 threshold, a metric caveat, DESIGN.md).'
                : 'Look for invalidating context elsewhere in the set (other seeds) or a numeric error.'
          }

Output the structured verdict.`,
          {
            label: `verify:${f.fully_qualified_id}-l${lensIndex + 1}`,
            phase: 'Verify',
            schema: VERDICT_SCHEMA,
          }
        )
      )
    ).then((votes) => {
      const valid = votes.filter(Boolean)
      const refuteCount = valid.filter((v) => v.refuted).length
      const survived = refuteCount < 2 // majority (2/3) must refute to drop
      // Consume the verifiers' severity_adjusted: among non-refuting verifiers, adopt a severity
      // (other than "unchanged") only if >=2 of them agree on it; otherwise keep the lens's original.
      const adjVotes = valid
        .filter((v) => !v.refuted && v.severity_adjusted && v.severity_adjusted !== 'unchanged')
        .map((v) => v.severity_adjusted)
      const counts = {}
      for (const s of adjVotes) counts[s] = (counts[s] || 0) + 1
      let effective = f.severity
      let best = 1
      for (const s of Object.keys(counts)) {
        if (counts[s] >= 2 && counts[s] > best) {
          best = counts[s]
          effective = s
        }
      }
      return {
        ...f,
        survived,
        effective_severity: effective,
        severity_changed: effective !== f.severity,
        verifier_votes: valid,
        refute_count: refuteCount,
      }
    })
  )
)

const survivedLens = verifiedLens.filter((v) => v.survived)
const refutedLens = verifiedLens.filter((v) => !v.survived)
// Mechanical findings are code-certain — they bypass verification.
const allSurviving = [...mechanicalFindings, ...survivedLens]

log(`Verify complete. ${survivedLens.length}/${lensFindings.length} judgment findings survived (${refutedLens.length} refuted); ${mechanicalFindings.length} mechanical passed through. ${allSurviving.length} total.`)

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
  surviving_findings: allSurviving.map((f) => ({
    lens: f.lens_key,
    id: f.fully_qualified_id,
    mechanical: !!f.mechanical,
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
  `You are synthesizing a gameplay-data audit of AiLibi's committed replay set ${SAMPLE_DIR}. A
deterministic extractor produced code-certain rule violations (these are NOT subject to refutation); 6
analysis lenses produced judgment findings; adversarial verification dropped the ones 2-of-3 skeptics
refuted. What remains is the load-bearing finding set.

Input data (JSON):
${JSON.stringify(synthesisInput, null, 2)}

Your output has two parts:
1. Structured synthesis: verdict (CLEAN / MINOR_ISSUES / SIGNIFICANT_ISSUES) + rationale; notable_trends
   (evidence-backed, with numbers); improvement_proposals (group related findings; one proposal per
   group with a reproducible scope sketch — cite the seed+tick to reproduce — and a priority, where
   "urgent" means blocking: address before Wave 1 starts).
2. report_markdown: the full Markdown report body, to be written to audits/audit-YYYY-MM-DD-HHMM-gameplay-data.md.
   Use this section structure:
   - "# Gameplay Data Audit — YYYY-MM-DD HH:MM (${SAMPLE_DIR})"
   - "## 1. Verdict" (CLEAN | MINOR_ISSUES | SIGNIFICANT_ISSUES + 2-3 paragraphs)
   - "## 2. Environment" (timestamp from \`date\`, audited HEAD from \`git log -1 --oneline\`, sample dir,
     games analyzed, mechanical vs judgment finding counts, refute rate)
   - "## 3. Confirmed bugs & rule violations" (mechanical findings first — labelled code-certain — then
     surviving engine/correctness judgment findings; use the (verifier-adjusted) "severity" and note where severity_adjusted_by_verifier is true; cite evidence seed+tick + repair hint)
   - "## 4. Gameplay trends" (the notable_trends, with numbers)
   - "## 5. Decision-quality findings" (crew + impostor lenses)
   - "## 6. Time-waste findings" (with the no-wall-clock caveat stated explicitly)
   - "## 7. Metric soundness, coverage & balance"
   - "## 8. Improvement proposals" (one subsection each: proposed_id, title, finding ids, scope sketch
     with a reproduction seed+tick, priority)
   - "## 9. Lens coverage notes" (per-lens what-was-examined)

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
  improvement_proposals: synthesis.improvement_proposals,
  notable_trends: synthesis.notable_trends,
  summary: synthesis.summary,
  tokens_spent: budget.spent(),
}
