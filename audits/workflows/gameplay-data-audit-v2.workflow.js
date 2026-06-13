// Gameplay-data audit Workflow — v2 (reactive-accusation-chain substrate).
//
// SUPERSEDES gameplay-data-audit.workflow.js (v1), which reads the removed
// transcript.reports[]/statements[] shape and pins replays/samples/7p2i. v1 is
// kept for provenance; use THIS file for any set recorded on the §5.2 chain
// protocol (post-PR-#119). BASELINE-AGNOSTIC: every recording-time anchor (win
// split, ejections, SKIP share, meeting_rate, tokens, failed_calls, MODEL) is
// derived from the POINTED set's own tournament-eval-report.json + MANIFEST +
// facts — never hardcoded here — so the same workflow audits any chain-protocol
// set (a cross-set comparison just names the other set's dir + commit).
//
// Analyzes a committed replay sample set (default replays/samples/9p2i, 50 games)
// to surface gameplay BUGS, TRENDS, decision-quality faults, call-waste, and
// concrete improvement proposals — purely from the recorded data (no Ollama; the
// recorded LLM outputs carry no role, and roles are re-derived from the seeder).
//
// CURRENT TARGET — the Phase-10 WAVE-1 CLOSE BASELINE: 9p/2i re-recorded at
// 0ed6962 (PR #150, attempt-2) on qwen3.5:9b with the full Wave-1 crew evidence
// economy landed on top of the Wave-0 honest instrument: 10.6 instrument
// integrity (canonical-room ALLOWLIST kills the VARYING_ROOMS placeholder leak;
// proxy-alibi subject-account-consistency — a third-party alibi the subject's
// OWN account contradicts is re-targeted weak at the proxy speaker; Rule-3
// relevance gate — spawn-window and kill-scene sightings no longer corroborate),
// 10.7 testimony ingestion (PRE-VOTE two-witness fold: 2+ independent
// observation-backed voices move every living listener +0.05 BEFORE ballots,
// so an eyewitness recruits a plurality in-meeting; single-voice and bare
// pile-ons stay powerless), 10.8 crew emergency meeting (a suspicion-
// accumulation trigger at the §4.6 0.60 gate breaks the impostor's kill-cadence
// monopoly; crewmate_report v6), 10.9.1 vote-ballot fail-soft (a twice-failed
// ballot degrades to a marked SKIP instead of aborting the game), 10.9.2
// ballot-target graph guard (an under-gate eject target is redirected to the
// voter's own argmax ≥0.60 candidate, or coerced to SKIP — no ungrounded
// ejections). HARD validity gate GREEN both sets, and the headline numbers are
// KNOWN (PR #150): genuine_class 2/8, multi_signal 11/11, over-gate listeners
// 1.62, emergency 7, ejection_accuracy 0.579 (NON-GATE), wrong-ejection games 8,
// meetings/game median 1.5. Derive this set's real numbers yourself — never
// trust quoted ones. The audit is the WAVE-1 CLOSE GATE: confirm the baseline is
// VALID for Wave-2 authoring and answer the four questions the re-record left:
//   (1) THE REDIRECT-INTO-CREW PATTERN (the headline — PR #150 Q-b): the 10.9.2
//       guard fired on 3 of the 8 wrong-ejection seeds (12/33/40). On seed-12 it
//       converted attempt-1's lucky-impostor railroad (bare-accused under-gate
//       p-1, an impostor caught by accident) into a PRINCIPLED crew ejection
//       (innocent p-6 redirected-to at 0.80). Decompose every redirect: WHY is
//       the redirected-to innocent at ≥0.60 — earned suspicion (fair, deception
//       is the game) or over-accumulation (the guard launders ungrounded-target
//       into over-suspicion)? This is the deduction-quality seam.
//   (2) GAINS ARE STRUCTURAL, NOT SEED-LUCK: verify the testimony fold (seed-38
//       m0: 3 voices → 4 listeners cross to 0.63 → impostor ejected) and the
//       accumulator carry (6 zero-contradiction ejections; seed-6 climbs
//       0.55→0.60 across meetings) are the §6.3 mechanism working, not noise —
//       reconstruct the trajectories from the bytes.
//   (3) THE RESIDUAL CONVERSION GAP is detection→conversion, NOT cadence (30 of
//       59 impostor-survivals had a later meeting available). Partition the
//       survivors: what evidence shape would have converted them, and is the
//       binding constraint now the SKIP-plurality bloc, weak-band shelter, or
//       true evidence absence? This sizes whether Wave-2 needs a crew lever too.
//   (4) WAVE-2 TOOLKIT INPUT (impostor gameplay): re-derive the toolkit gaps
//       (do_task 0, idle concentration, kill-intent cross-room waste, accused-
//       survival active-vs-passive split) AND the self-accusation class the
//       deception lab flagged (impostor self-accuses, voters adopt the target) —
//       it is game-deciding and the 10.9.2 guard does not cover it.
//
// Structure: a deterministic Extract pre-phase (one agent UPDATES + runs the
// committed Python extractor: ground-truth roles, resolved events, hard rule
// violations, chain-protocol invariants, AND the conversion / 9B-artifact
// aggregates) → parallel analysis lenses → HYBRID verification (code-certain
// mechanical findings pass straight through; each LLM judgment finding gets ONE
// adversarial skeptic — refuted drops; a skeptic that fails to run passes the
// finding through flagged unverified) → synthesis that writes a Markdown report
// to audits/.
//
// Invoke from a Claude Code session:
//   Workflow({scriptPath: "audits/workflows/gameplay-data-audit-v2.workflow.js"})
//   Workflow({scriptPath: "audits/workflows/gameplay-data-audit-v2.workflow.js", args: "replays/samples/9p2i"})
//
// Output: audits/audit-YYYY-MM-DD-HHMM-gameplay-data.md (synthesis agent writes it).

export const meta = {
  name: 'gameplay-data-audit-v2',
  description: 'Structured audit of a committed chain-protocol replay set (9p/2i, per-player tasks, accusation-chain meetings): deterministic rule + chain-protocol + conversion / artifact checks in Extract, 4 focused analysis lenses (redirect-into-crew + conversion-quality headline, pacing/structural-gains, impostor toolkit, model artifacts), adversarial verify, synthesis. Baseline-agnostic (derives anchors from the pointed set); runs on Opus 4.8 throughout (Fable 5 suspended; the headline lens C + synthesis were the Fable tier).',
  whenToUse: 'After a chain-protocol eval set is recorded; validates the baseline and produces the next wave\'s contract input — currently the Phase-10 Wave-1 CLOSE GATE (decompose the 10.9.2 redirect-into-crew pattern, verify the testimony/accumulator gains are structural, partition the residual conversion gap, and produce the Wave-2 impostor-toolkit + self-accusation input).',
  phases: [
    { title: 'Extract', detail: 'One agent updates + runs the committed extractor: roles, resolved events, hard-rule + chain-protocol checks, conversion/testimony aggregates into a facts JSON' },
    { title: 'Analyze', detail: '4 parallel lenses over the facts + transcripts on Opus 4.8 (C redirect/conversion-quality headline; B pacing/structural-gains, D impostor toolkit, H artifacts)' },
    { title: 'Verify', detail: 'Mechanical findings pass through; each judgment finding gets one skeptic (refuted drops; a failed skeptic passes it through flagged unverified)' },
    { title: 'Synthesis', detail: 'Group findings, decompose the redirect-into-crew pattern, judge baseline validity for Wave-2, propose Wave-2 contract input, write report' },
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
          priority: { type: 'string', enum: ['urgent', 'phase-10-input', 'opportunistic'] },
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

const preamble = (factsPath) => `You are one of the parallel analysts auditing the GAMEPLAY DATA of the AiLibi
social-deduction simulation — the committed sample set at ${SAMPLE_DIR} (50 recorded games on the
reactive-accusation-chain substrate). A deterministic Extract phase already ran: it derived ground-truth
player roles (re-seeded from the roster — roles are firewalled OUT of the replays), reconstructed the
resolved per-game events, and code-checked the hard engine rules, the chain-protocol invariants, AND
the conversion / 9B-artifact aggregates. Your findings will go through adversarial verification (a
skeptic tries to refute each) and synthesis with the other analysts.

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
- CONVERSION LAYER + MODEL (the current target's prompts — DESIGN.md §4.6/§5.5): the vote ballot
  (vote_ballot v5) RENDERS the §4.6 skip-gate verdict in-prompt ("maximum suspicion among the living
  ejection targets is X; threshold 0.60 -> MUST vote / MUST skip"), the max taken over candidate_targets
  ONLY; the opening (crewmate_report v5) and reply/opt-in (accusation_round v7) push a decisive,
  grounded accusation + opt-in corroboration, with a free_text length discipline, a living-roster
  accusation constraint whose roster lines now carry an explicit DEAD marker (10.3), and ONE retry of
  a validation-failing opening (narration-only OR guard-emptied after target validation) — a retried
  opening is BY DESIGN, one extra call, not call-waste. ACCUSATION-TARGET VALIDATION (fb3cfa5,
  meetings/manager.py): an accusation or
  ballot naming a non-living player is DROPPED and the original recorded on free_text via
  INVALID_ACCUSATION_TARGET_MARKER — a dropped target is BY DESIGN, not a protocol violation, but its
  RATE is a model-quality signal (qwen3.5:9b hallucinates ids like "imp-2"). The set's MODEL and prompt
  versions are in the MANIFEST / replays — derive them; do not assume the model, or that any prompt-era
  number quoted in planning docs still holds.
- SUSPICION MECHANICS (DESIGN.md §6.3/§4.6 — load-bearing for every by-design judgment; layers
  (a)-(c) are the §6.3 + Wave-0 substrate, layer (d) is the Wave-1 crew economy that landed on THIS set):
  (a) 9.7 detector precision: a contradiction classified WEAK (self-stated alibi — speaker == subject —
  or narrow tick window) carries a reduced delta landing suspicion in [0.5, 0.60) ALONE — suspicious
  but below the eject gate; a second independent signal (another contradiction, body-proximity, vent,
  a prior-meeting accumulator carry) crosses. A lone weak contradiction NOT converting is the DESIGN,
  not a detector failure. NOTE the shape ambiguity: a self-stated alibi contradicted by a sighting is
  BOTH the innocent-reporter railroad shape AND the catch-a-lying-impostor shape — the classifier keys
  on evidence shape, not target guilt. That symmetry underlies the redirect-into-crew question.
  (b) 9.8 accumulator + decay (PERSISTENT, cross-meeting): being accused in a meeting adds +0.05 to
  every living agent's view of the accused (deduped per meeting — a pile-on cannot multiply it); a
  corroboration lowers −0.05; suspicion with no new evidence decays 25% of the way toward the 0.5
  prior per meeting. SINGLE-VOICE accusations still fold POST-VOTE (a meeting's own single-accuser
  bump moves only the NEXT meeting's ballots); the 10.7 TWO-WITNESS channel folds PRE-VOTE (see (d)).
  Trajectory 0.5→0.55→0.60: crossing on accumulation alone requires 2+ reinforcing meetings BY DESIGN
  ("no single round ejects" — owner principle). A zero-contradiction ejection whose subject carried a
  prior-meeting accusation is the accumulator CONVERTING (the intended cross-meeting arc), not an
  anomaly. Ballots are NOT evidence (never feed the accumulator). An impostor never accrues a bump
  against a fellow impostor (teammate guard).
  (c) WAVE-0 INSTRUMENT REPAIRS (10.1-10.4, landed ON this set — load-bearing for every honesty
  judgment): room labels are CANONICALIZED at claim parse (compound labels no longer mint phantom
  room-mismatch contradictions); endpoint-tick sightings produce WEAK flags only; alibi_conflict is
  weak-classified; per-player contradiction deltas are deduped/capped (flag stacking cannot run
  suspicion to 1.0); corroboration is detector-derived with an independence gate (sighting speaker
  != subject != alibi speaker); claim SUBJECTS are roster-validated (10.2), which un-gated Rule 3 —
  DOWNWARD suspicion moves (corroboration −0.05) are now EXPECTED behavior, not anomalies; and the
  conversion ruler is genuine_class_conversion (10.4): only non-endpoint alibi_vs_sighting flags
  RE-DERIVED through the repaired detector count as genuine, and weak-self-stated does NOT
  disqualify (a fabricated alibi is self-stated by construction — all impostor fabricated-alibi
  flags are weak; assert presence, never marker strength). CONSEQUENCES you must not misread: total
  contradiction volume DROPPED HARD vs the e750b40 era (the repair working, not lost detection), and
  ejection_accuracy is NOT comparable to the artifact-era ~0.63 (that number was artifact railroads
  at roughly the accusation base rate; never benchmark this set against it).
  (d) WAVE-1 CREW EVIDENCE ECONOMY (10.6-10.9.2, landed ON this set — load-bearing for EVERY
  by-design judgment on the close baseline):
  - 10.6 instrument integrity: the VARYING_ROOMS placeholder leak is GONE (a canonical-room ALLOWLIST
    replaced the denylist — a non-allowlisted room mints NO flag); PROXY-ALIBI subject-account
    consistency — when a third-party alibi about a subject conflicts with a sighting AND the subject's
    OWN account agrees with the sighting, the flag is suppressed against the subject and re-targeted
    WEAK at the proxy speaker (a WEAK_REASON_RETARGETED_PROXY flag naming the speaker, never the
    subject; it cannot eject alone); the RULE-3 RELEVANCE GATE — a spawn-window (tick 0-1) sighting or
    a kill-scene sighting placing the subject in the triggering-body room within their alibi window NO
    LONGER corroborates. Re-targeted-proxy flags and relevance-gated non-corroborations are BY DESIGN.
  - 10.7 PRE-VOTE TWO-WITNESS TESTIMONY FOLD (the headline mechanism): 2+ INDEPENDENT
    observation-backed voices accusing a subject (a chain/opening accusation OR an opt-in
    corroboration of an accuser, each carrying a first-hand relevance-passing sighting, distinct
    speakers, never the subject) move EVERY living listener +0.05 against the subject BEFORE ballots
    render — so a listener can cross 0.60 and the §4.6 verdict reads MUST-vote on testimony alone.
    A single voice or a bare verbal pile-on (no observation backing) folds NOTHING pre-vote. This
    REPLACES the post-vote bump for that subject-meeting (never doubles). A listener freshly folded
    over 0.60 voting to eject is the MECHANISM, not an inversion.
  - 10.8 CREW EMERGENCY MEETING: a living crewmate whose private max suspicion reaches 0.60 with no
    meeting since that belief crossed can call an EMERGENCY meeting (once per player per game, plus a
    global cooldown), trigger_kind "emergency", crewmate_report v6. An emergency meeting has NO
    found_body. Emergency meetings > 0 is the intended break from the impostor kill-cadence monopoly.
  - 10.9.1 VOTE-BALLOT FAIL-SOFT: a vote completion that fails to parse twice degrades to a SKIP
    stamped VOTE_PARSE_DEFAULT_MARKER (a defaulted-ballot), the game CONTINUES. A defaulted SKIP is
    NEVER a threshold_inversion and never a silent missed_skip — by design.
  - 10.9.2 BALLOT-TARGET GRAPH GUARD: an eject ballot under a MUST-vote verdict that names a target
    the voter's own rendered graph carries BELOW 0.60 (or no row for) is REDIRECTED to the voter's
    argmax-rendered ≥0.60 eligible candidate (ties lowest id; teammate-only-over-gate → SKIP), stamped
    BALLOT_TARGET_REDIRECT_MARKER. The redirect is BY DESIGN — it kills ungrounded-target ejections.
    A redirect that lands on an INNOCENT (the argmax happened to be crew) is graph-consistent, NOT a
    railroad; whether the redirected-to innocent's ≥0.60 is EARNED is the audit's headline question,
    not a mechanical defect. A redirected eject is never a threshold_inversion.

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
- Recently FIXED or KNOWN — do NOT re-flag as new defects unless a game in THIS set still exhibits
  them: the win-condition impostor-elimination gap (Phase 6); hollow-meeting timeouts (Wave 0);
  impostor friendly-fire kills (Wave 0.5); impostor betrayal ballots/accusations (7.12); meeting
  STARVATION (meeting_rate well above the 0.60 floor); the 7B threshold-quoting inversion (fixed by
  the v5 verdict render); the e750b40-era detector ARTIFACT classes (compound-label, placeholder,
  full-weight endpoint) — repaired by 10.1; Rule 3's silent no-ops on garbage subjects — repaired by
  10.2; the VARYING_ROOMS placeholder leak — repaired by 10.6's allowlist (expect 0 such flags); the
  seed-8-class vote-truncation ABORT — repaired by 10.9.1 (a truncating ballot now degrades to a
  defaulted SKIP, the game finishes; do not file the defaulted ballot as a defect). Invalid
  accusation/ballot targets are dropped BY DESIGN — the hallucination RATE is the signal, the drop is
  not a bug. KNOWN-AND-REPORTED on THIS set (PR #150) — your job is to BUILD ON these, not re-discover
  them as findings: genuine_class_conversion ~2/8, multi_signal ~11/11, over-gate listeners ~1.62,
  emergency meetings ~7, ejection_accuracy ~0.58 (NON-GATE — never benchmark against the artifact-era
  0.63); the two OWNER-ACCEPTED deviations (wrong-ejection games 8 vs the W0 ceiling of 7 — the +1 is
  the seed-12 redirect, owner gated anti-railroad on CHARACTER = no bare-pile-on, not the count; and
  meetings/game median 1.5 vs 2.0 — within run-to-run variance) — do NOT file either as a finding;
  the redirect-into-crew DECOMPOSITION (why the redirected-to innocents are ≥0.60) is the headline
  lens's job, not a re-discovery; the testimony pre-vote folds and emergency meetings firing (the
  10.7/10.8 mechanisms working); the defaulted ballot (1, seed-8) and ballot redirects (6, seeds
  12/33/40) telemetry; downward Rule-3 corroboration moves; cross-room/dead-actor same-tick kill
  rejections (engine-correct, informational). Flag only what is genuinely NEW or contradicts the
  PR's self-report (a self-report contradiction IS a high finding).
- No drive-by suggestions: a recommendation must address a cited finding.
- Severity: "blocking" = invalidates this baseline's validity for Wave-2 (the set must be re-recorded
  or the engine fixed); "high" = changes the Wave-2 contract or a pending owner decision; "medium" =
  worth fixing in/before Wave 2; "low" = opportunistic; "informational" = trend/observation only.

Your lens-specific scope is below. Stay within it; do not duplicate other lenses.

`

// ---------------------------------------------------------------------------
// Lens definitions
// ---------------------------------------------------------------------------

const LENSES = [
  {
    key: 'B',
    name: 'Pacing, balance & the emergency channel (did the 10.8 lever land; Wave-2 sizing)',
    scope: `Characterize the GAME SHAPE on the Wave-1 close baseline and verify the 10.8 emergency
channel landed as intended — every number is a Wave-2 input. Cover: (1) EMERGENCY CHANNEL (the 10.8
verification): emergency meetings fired ~7 — break that down (which seeds, caller role, the
triggering suspicion, did the called meeting reach a vote / change an outcome?); confirm every
emergency meeting carries NO found_body and nothing downstream assumed one; did emergency meetings
add the cross-round runway the accumulator needs (an emergency meeting that supplies the 2nd meeting
for a carry to fold)? An emergency meeting firing on an UN-earned 0.60 (the caller's max traces to
over-accumulation) is a HIGH finding — coordinate with lens C. (2) PACING/RUNWAY: meetings/game
histogram + share reaching 2+ (the accumulator runway); is the median ~1.5 a starvation risk or did
emergency meetings lift the tail? Cross the meetings-count against the win split (the W0 audit found
pacing INVERTED — more meetings correlated with MORE impostor wins; re-derive that table here and say
whether Wave-1 broke the inversion). (3) BALANCE: win split + win-REASON breakdown; if CREWMATE_TASKS
still dominates, the stopwatch margin (ticks between the task win and the kill-clock's parity pace —
the lab found this a hair-trigger: ~6 ticks of slowdown flips ~25% of outcomes, so REPORT the margin,
do not propose tuning it). (4) SUPPLY: evidence-bearing observations per meeting, witnesses per kill,
kill patterns (rooms, first-kill tick cluster, witnessed rate, body-report rate + latency, bodies
never reported); per-player task pacing + the §3.5 denominator shrink; role↔outcome correlations.
Report NUMBERS; flag degenerate clusters. Severity informational/low unless a trend exposes a defect
or the emergency channel misbehaves.`,
  },
  {
    key: 'C',
    name: 'Wave-1 close: redirect-into-crew decomposition + structural-gains + residual partition',
    scope: `THE HEADLINE LENS — the Wave-1 CLOSE GATE. The instrument is honest and the crew evidence
economy landed; the headline numbers are KNOWN (PR #150: genuine_class ~2/8, multi_signal ~11/11,
over-gate listeners ~1.62, ejection_accuracy ~0.58 NON-GATE) — do NOT re-discover them. Derive this
set's numbers from the facts first, then answer FOUR asks with per-meeting byte walks, each
cross-referenced with FACTS roles:
(1) THE REDIRECT-INTO-CREW DECOMPOSITION (the headline deliverable). The 10.9.2 ballot-target graph
guard fired on ~6 redirects across ~3 of the 8 wrong-ejection seeds (reportedly 12/33/40). For EACH
redirect event (find them via the BALLOT_TARGET_REDIRECT_MARKER on ballot rationale + the facts'
redirect records): identify the ORIGINAL under-gate target (was it a true impostor? — seed-12's was
impostor p-1, a lucky-hit the guard correctly refused) and the REDIRECTED-TO candidate (the voter's
argmax ≥0.60). For every redirect that landed on an INNOCENT, decompose WHY that innocent is rendered
≥0.60 in the voter's graph: walk the quantized §6.3 arithmetic back to its sources — is the ≥0.60
(i) EARNED — a genuine flag, a real first-hand sighting, body-proximity, or a multi-meeting
accumulation from substantive accusations (then the ejection is FAIR: innocents are ejectable, just
not at random, and this is deduction working); or (ii) OVER-ACCUMULATED — the ≥0.60 traces to
pile-on bumps, a relevance-gate miss, or a weak-flag that should not have stacked (then the guard
LAUNDERED an ungrounded-target problem into an over-suspicion problem — a HIGH finding that shapes a
Wave-2 crew-side fix). Report the earned-vs-over-accumulated split across all redirect-into-crew
events; that split is the deduction-quality verdict on the whole guard.
(2) STRUCTURAL-GAINS VERIFICATION (are the wins MECHANISM, not seed-luck?). (a) TESTIMONY FOLD: from
the facts' fold events, verify the pre-vote two-witness folds at BYTE level — pick the seed-38 m0
showcase plus 2-3 others: 2+ independent observation-backed voices → every listener +0.05 → at least
one listener crosses 0.60 → rendered verdict reads MUST-vote → ballot complies → ejection. Confirm a
freshly-folded ≥0.60 ballot is NOT counted as a threshold_inversion (the render-seam check). Count
how many of the set's impostor ejections were testimony-fold-driven vs flag-driven vs carry-driven.
(b) ACCUMULATOR CARRY: reconstruct the ~6 zero-contradiction ejections (no flag named the ejected) —
walk each subject's cross-meeting suspicion trajectory (prior accusation → +0.05 carry → this
meeting's rendered ≥0.60); confirm the seed-6-class climb (0.55→0.60 across meetings) is the §6.3
accumulator converting, with the right quantized deltas. A zero-contradiction ejection whose
trajectory does NOT reconstruct from accumulation arithmetic is a HIGH finding.
(3) RESIDUAL CONVERSION-GAP PARTITION (sizes whether Wave-2 needs a crew lever). The re-record found
30 of ~59 impostor-survivals had a later meeting available — so cadence is NOT the binding
constraint; the gap is detection→conversion. Partition EVERY living-impostor-accused-not-ejected
meeting: (a) weak-flag-sub-gate; (b) testimony existed but folded sub-gate (single voice, or two
voices that still did not cross); (c) over-gate but lost the SKIP-plurality bloc (the tally bar —
how many voters crossed vs the mandatory-skip count); (d) true no-evidence; (e) strong-evidence-yet-
skipped = genuine inversion, must be 0 (HIGH if found). Name the DOMINANT residual class — it is the
single biggest input to whether Wave-2 is impostor-only or needs a paired crew conversion lever.
(4) BASELINE-VALIDITY + NEW-ARTIFACT HUNT. Confirm for Wave-2 authoring: VARYING_ROOMS-class flags 0
(the 10.6 allowlist held), no canonicalization COLLISION (two real rooms → one label suppressing a
mismatch — HIGH if found), stacking cannot reach 1.0, threshold_inversions 0, the defaulted ballot
and redirects never became inversions. Any NEW artifact the Wave-1 mechanisms introduced (a spurious
pre-vote fold, an over-eager relevance suppression hiding a real contradiction, an emergency meeting
firing on an un-earned 0.60) is the find that matters.
Reference meetings/transcript.py + meetings/manager.py (the repaired classifier, the 10.7 fold, the
10.9.2 guard), agents/memory/beliefs.py (the 9.8 + two-witness rules), eval/vote_correctness.py +
eval/meeting_quality.py (the one-home metric definitions). Cite seed+meeting+turn with
votes/roles/suspicion values.`,
  },
  {
    key: 'D',
    name: 'Impostor behavior (Wave-2 toolkit input: 10.10 probe / 10.11 contracts)',
    scope: `Assess impostor play from transcripts + FACTS roles — this lens's output is the direct
input to the Wave-2 deception probe (10.10) and toolkit contracts (10.11), so quantify each TOOLKIT
GAP, not just "passive". The deception LAB (experiments/lab) already established the Wave-2 thesis:
the 9B cannot INVENT a lie (2/18 spontaneous self-report fabrication) but PERFORMS a handed cover
story ~92% sheltered — so the toolkit is POLICY-AUTHORED deception (mint a cover story at kill time,
inject into memory), not a "be deceptive" instruction. This lens supplies the live-bytes baselines
that toolkit A/B must move. Prior-era anchors to re-derive on THIS set (do not trust them): 0 do_task
emissions, ~54% of impostor action turns waiting, idle concentration in 2 players.
(1) BLENDING — do impostors emit do_task/report at all (exact counts; expected 0 — confirm the path
is policy-unreachable), movement vs crew (loitering, idle concentration); (2) UNDER ACCUSATION — the
deception-effectiveness number, but SPLIT accused-impostor survival into ACTIVE (a plausible
rebut/deflect/counter-accuse moved the chain off them) vs PASSIVE (they survived because the crew
could not convert — that is lens C's missed-conversion mass, NOT deception skill); the lab found ~28
active / ~25 passive — re-derive the split, because the Wave-2 A/B gates on the ACTIVE subcount;
(3) THE SELF-ACCUSATION CLASS (the lab's emergence finding — game-deciding, NOT covered by 10.9.2):
count impostor self-accusations (speaker accuses themself) and trace consequences — did voters ADOPT
the self-named target (the seed-12-class F2 shape)? The 10.9.2 guard redirects ungrounded targets but
does not address an impostor STEERING the vote by self-naming; quantify how often this happens and
whether it helped or hurt the impostor side; (4) FABRICATED ALIBIS under the repaired detector — how
many impostor alibis drew a flag, weak vs strong; the shelter count (impostors who survived because
their only flag was weak-banded — a design tension to surface, not a bug); (5) MISDIRECTION — do
impostors steer chains at innocents, exploit opt_ins, was impostor-vote the decisive margin in any
wrong ejection (note: the 10.9.2 redirect now reshapes impostor ballots too — flag any interaction);
(6) TEAMMATE COORDINATION without firewall trips (betrayal must be 0 — Extract checks); (7) KILL-INTENT
discipline — cross-room/timing waste (share of kill intents wasted — the ~15% MECH-B-1 class).
Reference observation/service.py, eval/alibi_fabrication.py, impostor_policy.py. Cite seed+meeting+turn.`,
  },
  {
    key: 'H',
    name: 'Model artifacts + Wave-1 fail-soft behavior on the 9B (qwen3.5:9b)',
    scope: `VERIFY the Wave-1 fail-soft / guard machinery behaved correctly against the 9B's actual
output shapes, and characterize the residual model artifacts — your job is the shape and the
residual, not re-discovery. (1) VOTE-BALLOT FAIL-SOFT (10.9.1): there is ~1 defaulted ballot
(seed-8). Read its bytes — confirm the rationale genuinely ran to the 1024-token cap mid-JSON (the
truncation class, not a different failure), the degrade stamped VOTE_PARSE_DEFAULT_MARKER, the game
finished, and the defaulted SKIP rendered under a MUST-SKIP verdict (so it is correct-skip telemetry,
never a missed_skip or inversion). A defaulted ballot under a MUST-VOTE render that was NOT diverted
out of the decision census would be a HIGH finding. (2) BALLOT-TARGET REDIRECT (10.9.2) model side:
for the ~6 redirects, confirm each ORIGINAL target was genuinely under-gate in that voter's rendered
graph (the guard did not fire spuriously on an at-gate target) and the redirect math (argmax ≥0.60,
ties lowest id, teammate→SKIP) is exactly right; a redirect that changed a CORRECT ballot is a HIGH
finding. (lens C owns whether the redirected-to innocent is earned; you own whether the GUARD
COMPUTED correctly.) (3) OPENING VALIDATION residual (10.3, still live): lost_openings / defaults
count; for any defaulted opening read the raw_response tail — reasoning-relocation ("Wait...
actually...") or a new shape? Did any meeting lose its chain-driving opening? Do NOT propose a cap
raise (frozen; num_ctx overrun risk). (4) DEAD/INVALID-id residual: drop count + shape (dead-real vs
invented "imp-2"); spot-read 2-3 rendered prompts — roster renders with correct DEAD markers? a
render bug is HIGH; correct render + model still names the dead = prompt-saturation, contained by the
guard. (5) FREE_TEXT DISCIPLINE: length distribution per turn_kind vs the ~225-char prior medians;
the catastrophic-tail rate (a 3000+ char reasoning-relocation opening colliding with a drop marker
is the H-H-4 corruption class — check the marker bound held). (6) Any genuinely NEW 9B tell
(fabricated ticks/rooms passing schema, repetition loops, confidence values outside the quantized
rule-delta lattice, an emergency-meeting opening the v6 branch rendered wrong). Reference the turn
prompts + meetings/manager.py. Cite seed+meeting+turn.`,
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

START FROM THE COMMITTED EXTRACTOR: audits/workflows/extract_gameplay_facts.py. It is CURRENT through
the 2026-06-11 post-Wave-0 close audit (role re-derivation via orchestrator.seeder, a full
advance_tick + apply_meeting_result re-walk with per-tick state-hash verification, hard-rule
classification, win cross-checks, chain-protocol checks, the SKIP partition via the shared
eval/_suspicion_parse import, the point-6b/6c decomposition aggregates, the 10.6 retarget exclusion
in _genuine_subjects, the ballot confidence field, fail-loud invariants). UPDATE IT IN PLACE (edit
the file; it gets committed alongside the audit report) rather than writing a new script — most
machinery stays; your job is (i) RE-SYNCING every classification to the one-home repaired sources
(point 6b — these are unchanged by Wave 1, the detector source did not move) and (ii) ADDING the
WAVE-1-CLOSE aggregates the lenses need: redirect records, pre-vote fold events, emergency meetings,
self-accusations, and the per-subject cross-meeting trajectory (point 6c, extended below):

1. RE-POINT if needed: SAMPLE_DIR / SEEDSET constants -> "${SAMPLE_DIR}" and its basename (likely
   already correct). The roster.json read parameterizes players/impostors/tasks.

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
   - NOTE (fb3cfa5 — NOT a violation): an accusation or ballot whose target named a non-living player
     is DROPPED by the meeting layer and the original recorded on free_text via
     INVALID_ACCUSATION_TARGET_MARKER. Do NOT emit a mechanical finding for a dropped/invalid target
     (it is by-design normalization, like the ballot-target one). COUNT it in the aggregates (point 6)
     as a model-hallucination signal instead.
   If a category has zero violations, do not invent a finding for it.

6. EXTEND THE AGGREGATES: everything existing PLUS total ballots, skip ballots (count + share),
   ejections by role, chain-length histogram, termination-condition counts, opening-turn-accusation
   count (how many openings name an accusation at all), accusations at impostors vs at innocents
   (totals), opt_in totals (eligible-spoke-substantive if derivable), ballot_follows_chain totals,
   and contradiction totals. PLUS the conversion / 9B-artifact aggregates the v2 lenses need:
   - ejection_accuracy (impostor ejections / total ejections) + the wrong-ejection list (seed, ejected
     crew player).
   - a SKIP PARTITION: for each SKIP ballot, parse the rendered max suspicion from that voter's v5 vote
     prompt (the llm_calls entry matched to the ballot by agent_id; regex the
     "maximum suspicion among the living ejection targets is **X**" line) and classify CORRECT
     (max < 0.60) vs MISSED (max >= 0.60 over a living target). Report both counts.
   - genuine threshold-INVERSION count: rendered-max >= 0.60 over a living target yet target == SKIP,
     MINUS firewall coercions (impostor voter protecting a teammate) and invalid-target normalizations.
     Should be ~0 on this baseline; a non-zero count is a headline finding.
   - INVALID-ACCUSATION-TARGET drops: count + seeds (the INVALID_ACCUSATION_TARGET_MARKER on free_text,
     fb3cfa5) — split accusation-claim drops vs ballot-target drops if both occur.
   - FAIL-SOFT defaulted turns: count + per-record (seed, meeting, turn_index, turn_kind, output_tokens)
     from the failed_call records — these are the 9B turn-verbosity truncations (lens H).
   - free_text length distribution per turn_kind (median / p95 / max chars) over NON-defaulted turns.

6b. KEEP + RE-SYNC THE DECOMPOSITION AGGREGATES (added last audit; they stay, but every
   classification MUST now come from the one-home repaired sources, never an era-frozen replica:
   weak classification from meetings/transcript.py (the is_weak_contradiction predicate + the
   WEAK_CONTRADICTION_MARKER machinery — 10.1 extended weak to alibi_conflict and endpoint
   sightings, and canonicalizes room labels at claim parse) and the genuine-class definition from
   the 10.4 eval helpers (compute_genuine_class_conversion and friends in eval/vote_correctness.py /
   eval/meeting_quality.py). IMPORT them — a divergent replica poisons the whole decomposition.
   CROSS-CHECK the extractor's genuine-class and weak/strong totals against the shipped 10.4 metric
   run on the same bytes; a mismatch is a BLOCKING mechanical finding (one of the two is wrong)):
   - PER-EJECTION EVIDENCE CLASS: for each ejection (right or wrong), every contradiction whose
     subjects include the ejected player, classified via the imported repaired predicates
     → per-ejection record {seed,
     meeting, ejected, ejected_role, contradictions: [{kind, weak_self_stated, weak_narrow, strong}],
     plus the ejected player's max rendered suspicion from the vote prompts and whether any voter's
     rendered max implies a PRIOR-meeting accumulator carry (suspicion value not explainable by
     this meeting's deltas alone — quantized rule-delta arithmetic)}.
   - MISSED-CONVERSION RECORDS: for each meeting where a living TRUE impostor was verbally accused
     but NOT ejected → {seed, meeting, impostor, accused_by, contradictions_naming_impostor +
     their weak/strong classes, impostor_max_rendered_suspicion (from vote prompts),
     opt_in_corroborations_supporting_an_accuser_of_the_impostor (count), outcome (SKIPPED /
     ejected-someone-else), meetings_remaining_in_game_after_this_one (for the accumulator
     one-more-meeting question)}.
   - ZERO-CONTRADICTION EJECTIONS: ejections where NO contradiction names the ejected player —
     the accumulator-conversion candidates {seed, meeting, ejected, ejected_role, prior-meeting
     accusations naming them (count + meetings), rendered max suspicion}.
   - WIN-ATTRIBUTION CROSS-CHECK (absorbed from the old lens A — deterministic, not judgment):
     re-derive each game's winner from the walked final state and compare to the recorded
     game_over (CREWMATE_EJECT ordered before the task check; zombie-game check = no game continues
     past the last impostor's elimination). Mismatch -> blocking mechanical finding.

6c. ADD THE WAVE-1 CONTRACT-INPUT AGGREGATES (new this audit — the headline lens depends on these):
   - TESTIMONY RECORDS, one per (meeting, accused subject) for EVERY verbally-accused living
     subject of EITHER role — the innocent rows are the cascade-risk input, do not restrict to
     impostors: {seed, meeting, subject, subject_role, testimony_turns: [{turn_index, speaker,
     speaker_role, turn_kind, vehicle (accusation | sighting/observation claim | free_text-only
     mention), observation_backed}], structured_flags_naming_subject (+ weak/strong class each),
     per_voter_rendered_suspicion_of_subject — parse each living voter's v5 vote prompt for the
     SUBJECT's rendered suspicion value (not just the max line); if a prompt renders only the max,
     re-derive the per-subject value from the quantized §6.3 rule arithmetic and mark it
     derived=true — ballots_for_subject, plurality winner + margin, witness_ballot_follow_through
     (accusers who voted their own target), outcome, meetings_remaining_in_game_after_this_one}.
   - GENUINE-CLASS RECORDS: every flag the 10.4 re-derived definition classes as genuine →
     {seed, meeting, flag kind + parties, subject + subject_role, weak/strong marker, subject's
     max rendered suspicion across voters, ballots_for_subject, converted (ejected?), outcome}.
   - ACCUMULATOR TRAJECTORY FACTS: for each player who is a vote candidate in 2+ meetings of one
     game, the across-meeting sequence of their rendered suspicion values (from the vote prompts)
     plus the accusations/corroborations naming them in between — the lenses verify carry vs 25%
     decay vs Rule-3 drops from these. Include a count of DOWNWARD moves consistent with Rule 3
     (corroboration −0.05) as the sanity signal that 10.2's un-gating is live on these bytes.
   - RETRY AGGREGATES (10.3): identify opening-validation retries from the bytes (derive the
     recording shape from meetings/manager.py — validation runs on POST-GUARD claims and allows
     exactly ONE retry for a narration-only or guard-emptied opening): openings that failed
     validation, retries that recovered a usable accusation vs failed again, extra calls/tokens
     spent, and any meeting that still lost its chain-driving opening.

6d. ADD THE WAVE-1-CLOSE AGGREGATES (NEW this audit — the close-gate lenses depend on these; key
   markers/fields are in meetings/manager.py and eval/meeting_quality.py, IMPORT the marker
   constants, never hardcode their text):
   - REDIRECT RECORDS (10.9.2 — the headline). For every ballot whose rationale carries
     BALLOT_TARGET_REDIRECT_MARKER: {seed, meeting, voter, voter_role, original_target (parsed from
     the marker's preserved value) + original_target_role + the voter's rendered suspicion of that
     original (confirm it was BELOW 0.60 — the guard's precondition), redirected_to_target +
     role + the voter's rendered suspicion of it (confirm ≥0.60, argmax over the eligible pool),
     was_coerced_to_SKIP (teammate-only-over-gate case), and the meeting OUTCOME + ejected role}.
     Aggregate: redirect count, redirected-onto-impostor vs redirected-onto-crew split, and which
     wrong-ejection games owe their ejected to a redirect (the lens-C headline input).
   - DEFAULTED-BALLOT RECORDS (10.9.1): every ballot carrying VOTE_PARSE_DEFAULT_MARKER {seed,
     meeting, voter, voter_role, the voter's rendered verdict (MUST-vote / MUST-skip / no-render),
     and that the game still reached game_over}. Cross-check against eval.meeting_quality
     .compute_defaulted_ballots (mismatch = blocking).
   - PRE-VOTE FOLD EVENTS (10.7): reconstruct each two-witness pre-vote fold from the transcript +
     the rendered vote-prompt graphs (the fold is LIVE at record time, so the recorded listener
     suspicions ALREADY include it — do not re-apply it). Per fold: {seed, meeting, subject,
     subject_role, the independent voices (speaker + their backing observation, confirm distinct,
     observation-backed, relevance-passing), listeners whose rendered suspicion of the subject is
     ≥0.60, whether any of those listeners voted to eject, outcome}. This is how lens C verifies
     the fold is mechanism. (Deriving "voices" — replicate the 10.7 voice predicate by importing
     it if exposed, else from the transcript per the documented rule; flag if you must approximate.)
   - EMERGENCY MEETINGS (10.8): every meeting with trigger_kind "emergency" {seed, meeting, caller,
     caller_role, the caller's rendered max suspicion at call time if recoverable, whether the
     meeting carried any found_body (MUST be none — a found_body on an emergency meeting is a
     blocking finding), outcome}. Aggregate emergency count + body-report count (should partition
     the meeting total).
   - SELF-ACCUSATIONS (the lab's emergence class): every accusation where speaker == accused
     {seed, meeting, speaker, speaker_role, and whether any OTHER voter then targeted that speaker
     (adoption)} — the game-deciding impostor-self-steer the 10.9.2 guard does not cover.

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
    // Careful code-editing + deterministic checks — Opus; the judgment premium
    // is reserved for the Wave-1-input headline lens and synthesis.
    model: 'opus',
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
// Phase 2: Analyze (4 parallel lenses on Opus 4.8 — Fable 5 suspended; C is the
// Wave-1-close headline; the cut lenses' live questions were folded into C/B/H
// or the extractor, see the header)
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
        // All lenses run on Opus 4.8 (Fable 5 suspended 2026-06-13). The
        // Wave-1 close headline (redirect-into-crew decomposition +
        // structural-gains verification) is lens C; when Fable returns,
        // restore the tier: l.key === 'C' ? 'fable' : 'opus'.
        model: 'opus',
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
// Phase 3: Verify (hybrid — mechanical pass through; one skeptic per judgment
// finding; all skeptics on Opus 4.8 — Fable 5 suspended)
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
   shrinking task denominator is correct); the §4.6 skip rule intentionally biases toward SKIP
   under low confidence; AND the suspicion mechanics (DESIGN.md §6.3): a lone WEAK contradiction
   (self-stated alibi or narrow window) landing in [0.5,0.60) without ejecting is the 9.7 DESIGN;
   a SINGLE-voice accusation not moving its own meeting's ballots is the 9.8 post-vote-fold DESIGN;
   a single meeting never ejecting on accumulator alone ("no single round ejects") is the OWNER
   PRINCIPLE; suspicion decaying toward 0.5 across quiet meetings is Rule 5; the Wave-0 instrument
   layer (canonicalized rooms, weak-banded endpoints/alibi_conflict, capped flag deltas, Rule-3
   DOWNWARD moves) is BY DESIGN; AND THE WAVE-1 CREW ECONOMY (10.6-10.9.2, landed ON this set): a
   2+ INDEPENDENT-witness pre-vote fold lifting listeners over 0.60 before ballots is the 10.7
   DESIGN (a freshly-folded MUST-vote ballot is NOT an inversion); a re-targeted-proxy weak flag
   naming the proxy speaker and a relevance-gated spawn-window/kill-scene sighting NOT corroborating
   are the 10.6 DESIGN; an emergency meeting with no found_body called on a ≥0.60 max is the 10.8
   DESIGN; a twice-failed ballot degrading to a marked SKIP (game continues) is the 10.9.1 DESIGN
   and is never an inversion; an under-gate eject target REDIRECTED to the voter's argmax ≥0.60
   candidate (even when that lands on an innocent) is the 10.9.2 DESIGN — graph-consistent, NOT a
   railroad (the OPEN question is whether the redirected-to ≥0.60 is EARNED, which is a deduction-
   quality finding lens C decomposes, NOT a mechanical refutation). The invalid-target drop is the
   fb3cfa5 guard; a metric's documented caveat is not a bug. Check DESIGN.md §3.5/§5.2/§6.3,
   engine/rules.py, meetings/manager.py, meetings/transcript.py, agents/memory/beliefs.py, or the
   metric source before confirming.
3. Context: is there invalidating context elsewhere in the set (other seeds/meetings), a numeric
   error, or a token-proxy time-waste claim presented as a latency claim (no wall-clock exists)?

Refute ONLY with a concrete basis from those checks, cited in your reasoning. If the evidence
cannot be verified either way after honest effort, set refuted=true with reasoning starting
"unverifiable:". Output the structured verdict.`,
      {
        label: `verify:${f.fully_qualified_id}`,
        phase: 'Verify',
        schema: VERDICT_SCHEMA,
        // All skeptics on Opus 4.8 (Fable 5 suspended). When Fable returns,
        // restore the headline-lens tier: f.lens_key === 'C' ? 'fable' : 'opus'.
        model: 'opus',
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
WAVE-1 CLOSE audit of Phase 10 (9p/2i on qwen3.5:9b @ 0ed6962; the full crew evidence economy landed
— 10.6 instrument integrity, 10.7 pre-vote two-witness testimony fold, 10.8 emergency meeting, 10.9.1
vote fail-soft, 10.9.2 ballot-target guard; known headline per PR #150: genuine_class ~2/8,
multi_signal ~11/11, over-gate listeners ~1.62, emergency ~7, ejection_accuracy ~0.58 NON-GATE,
wrong-ejection games 8, two owner-accepted deviations). The audit is the WAVE-1 CLOSE GATE: judge
whether the baseline is VALID for Wave-2 authoring, decompose the redirect-into-crew pattern, confirm
the testimony/accumulator gains are structural, and produce the Wave-2 contract input — NOT
re-reporting the known headline. A deterministic extractor produced code-certain rule/protocol
violations (NOT subject to refutation) plus the decomposition aggregates; the analysis lenses produced
judgment findings; each judgment finding faced ONE adversarial skeptic —
refuted findings were dropped, and any finding whose skeptic failed to run carries unverified:true.
Label unverified findings explicitly in the report ("unverified — skeptic did not run"); never
present them as verified. What remains is the load-bearing finding set.

Input data (JSON):
${JSON.stringify(synthesisInput, null, 2)}

Your output has two parts:
1. Structured synthesis: verdict (CLEAN / MINOR_ISSUES / SIGNIFICANT_ISSUES) + rationale — the known
   headline numbers and the two owner-accepted deviations do NOT by themselves drive the verdict;
   judge baseline VALIDITY for Wave-2 and what is NEW (especially the redirect-into-crew earned-vs-
   over-accumulated split); notable_trends (evidence-backed, with numbers); improvement_proposals
   (group related findings; one proposal per group with a reproducible scope sketch — cite the
   seed+tick/meeting+turn to reproduce — and a priority, where "urgent" = invalidates this baseline /
   must fix before Wave 2, "phase-10-input" = must shape a Wave-2 contract (10.10 deception probe,
   10.11 toolkit, 10.12 metrics) or a pending owner decision (e.g. a crew-side over-accumulation fix,
   the self-accusation class), "opportunistic" = later).
2. report_markdown: the full Markdown report body, to be written to
   audits/audit-YYYY-MM-DD-HHMM-gameplay-data.md. Use this section structure:
   - "# Gameplay Data Audit — YYYY-MM-DD HH:MM (${SAMPLE_DIR}, Wave-1 close, Phase 10)"
   - "## 1. Verdict" (CLEAN | MINOR_ISSUES | SIGNIFICANT_ISSUES + 2-3 paragraphs; state explicitly
     whether the baseline is VALID for Wave-2 authoring and what the redirect-into-crew decomposition
     says the crew side still needs, if anything)
   - "## 2. Environment" (timestamp from \`date\`, audited HEAD from \`git log -1 --oneline\`, sample
     dir, games analyzed, mechanical vs judgment finding counts, refute rate)
   - "## 3. Confirmed bugs & rule violations" (mechanical findings first — labelled code-certain —
     then surviving correctness judgment findings; use the verifier-adjusted severity and note
     where severity_adjusted_by_verifier is true; cite evidence + repair hint)
   - "## 4. Wave-1 close: redirect, structural gains, residual gap (headline)" — the four asks with
     COUNTS: (1) THE REDIRECT-INTO-CREW DECOMPOSITION — per-redirect earned-vs-over-accumulated split
     (render the redirects as a table: seed, original under-gate target + role, redirected-to + role,
     why ≥0.60, earned/over-accumulated), the verdict on whether the 10.9.2 guard is sound or
     launders over-suspicion; (2) STRUCTURAL-GAINS VERIFICATION — testimony folds + accumulator
     carries byte-verified as mechanism (the counts: ejections testimony-fold-driven / flag-driven /
     carry-driven), the render-seam inversion check; (3) RESIDUAL CONVERSION-GAP partition with the
     DOMINANT class named (the input to whether Wave-2 needs a crew lever); (4) baseline validity +
     any NEW artifact. End with ONE paragraph: is the baseline VALID for Wave-2, and does the crew
     side need a paired fix first.
   - "## 5. Pacing, balance & the emergency channel" (the 10.8 verification — emergency count +
     behavior + body-less correctness; meetings/game + runway; the pacing-inversion re-derivation;
     the stopwatch margin REPORTED not tuned)
   - "## 6. Impostor behavior & model artifacts (Wave-2 input)" (the toolkit gaps quantified — the
     active-vs-passive survival split, the self-accusation class, do_task/idle/kill-waste; the
     Wave-1 fail-soft model-side checks — defaulted ballot, redirect computation, opening residual)
   - "## 7. Metric & coverage notes" (any metric that would mislead a Wave-2 A/B; the corrected_w1
     baseline; seed coverage; sentinel states)
   - "## 8. Improvement proposals" (one subsection each: proposed_id, title, finding ids, scope
     sketch with a reproduction citation, priority)
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
    // The capstone judgment — the Wave-2 readiness verdict rides on it.
    // Opus 4.8 (Fable 5 suspended; restore 'fable' when it returns).
    model: 'opus',
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
