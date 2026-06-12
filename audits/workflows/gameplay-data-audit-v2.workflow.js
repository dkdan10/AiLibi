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
// CURRENT TARGET — the Phase-10 WAVE-0 HONEST BASELINE: 9p/2i re-recorded at
// 59e4111 (PR #143) on qwen3.5:9b with the Wave-0 instrument repairs landed:
// 10.1 detector repairs (room labels canonicalized at claim parse; endpoint
// sightings weak-banded, never full-weight; alibi_conflict weak-classified;
// per-player contradiction deltas deduped/capped so flag stacking cannot run
// suspicion to 1.0; detector-derived corroboration with an independence gate),
// 10.2 claim-subject roster validation (un-gates §6.3 Rule 3 — corroboration
// fires for the first time on this set), 10.3 prompt nudges (crewmate_report v5
// + accusation_round v7: DEAD-marked roster lines + ONE retry of
// validation-failing openings), 10.4 honest gate metrics
// (genuine_class_conversion = the primary conversion ruler; flags re-derived
// through the repaired detector, never trusted from the recording). The
// re-record's HARD validity gate is GREEN and the headline numbers are KNOWN
// (PR #143): artifact flag classes ~0, endpoint flags survive only as weak,
// strong flags ~3, innocents-at-1.0 zero, ejection_accuracy ~0.42, and
// genuine_class_conversion 1/7 — the FIRST genuine conversion ever (seed 24).
// Derive this set's real numbers yourself — never trust quoted ones. The
// audit's job is NOT to re-litigate the artifact era or re-discover the known
// low conversion; it is to produce the WAVE-1 CONTRACT INPUT on honest bytes:
//   (1) TESTIMONY-LEVER SIZING (the 10.6 input): the prior-era audit (e750b40
//       set) found the DOMINANT miss class was spoken testimony that never
//       enters listeners' beliefs — 27 meetings, 22 with the witness voting
//       the impostor and losing plurality. Re-partition every missed
//       conversion on THIS set: does the testimony class stay dominant, how
//       big, and what would ingestion have yielded?
//   (2) FOLD-TIMING DECISION INPUT (owner call pending on 10.6): per
//       testimony-class meeting, would PRE-VOTE ingestion (same meeting) have
//       converted it — and how many INNOCENTS would the same rule have
//       railroaded (the cascade-risk number)? Versus POST-VOTE (next-meeting
//       fold): did a next meeting even exist, or would decay erase the carry?
//   (3) GENUINE-CLASS WALK: every genuine-class flag (per 10.4's re-derived
//       definition) walked end-to-end — the seed-24 conversion verified at
//       byte level, each non-conversion bucketed (sub-gate / plurality lost).
//   (4) RESIDUALS AS WAVE-1/2 INPUT — pacing/evidence supply (meetings per
//       game, accumulator runway, emergency-button absence) for 10.7; the
//       impostor toolkit gaps (do_task, idling, kill-intent waste) for
//       10.9/10.10; 9B artifacts (id-hallucination shape under the DEAD
//       marker, retry yield, defaulted-turn residual).
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
  description: 'Structured audit of a committed chain-protocol replay set (9p/2i, per-player tasks, accusation-chain meetings): deterministic rule + chain-protocol + conversion / artifact checks in Extract, 4 focused analysis lenses (Wave-1 contract input, pacing, impostor toolkit, model artifacts), adversarial verify, synthesis. Baseline-agnostic (derives anchors from the pointed set); model-tiered (Fable on the headline lens + synthesis, Opus elsewhere).',
  whenToUse: 'After a chain-protocol eval set is recorded; validates the baseline and produces the next wave\'s contract input — currently the Phase-10 Wave-0 honest baseline → Wave-1 input (testimony-lever sizing, fold-timing decision table, genuine-class walk, pacing/impostor/artifact residuals).',
  phases: [
    { title: 'Extract', detail: 'One agent updates + runs the committed extractor: roles, resolved events, hard-rule + chain-protocol checks, conversion/testimony aggregates into a facts JSON' },
    { title: 'Analyze', detail: '4 parallel lenses over the facts + transcripts (C Wave-1 input headline on Fable; B pacing, D impostor, H artifacts on Opus)' },
    { title: 'Verify', detail: 'Mechanical findings pass through; each judgment finding gets one skeptic (refuted drops; a failed skeptic passes it through flagged unverified)' },
    { title: 'Synthesis', detail: 'Group findings, decompose the regression, propose Phase-10-input improvements, write report' },
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
- WAVE-1 SUSPICION MECHANICS (DESIGN.md §6.3/§4.6 — load-bearing for every by-design judgment):
  (a) 9.7 detector precision: a contradiction classified WEAK (self-stated alibi — speaker == subject —
  or narrow tick window) carries a reduced delta landing suspicion in [0.5, 0.60) ALONE — suspicious
  but below the eject gate; a second independent signal (another contradiction, body-proximity, vent,
  a prior-meeting accumulator carry) crosses. A lone weak contradiction NOT converting is the DESIGN,
  not a detector failure. NOTE the shape ambiguity: a self-stated alibi contradicted by a sighting is
  BOTH the innocent-reporter railroad shape AND the catch-a-lying-impostor shape — the classifier keys
  on evidence shape, not target guilt. That symmetry is the heart of the regression.
  (b) 9.8 accumulator + decay (PERSISTENT, cross-meeting): being accused in a meeting adds +0.05 to
  every living agent's view of the accused (deduped per meeting — a pile-on cannot multiply it); a
  corroboration lowers −0.05; suspicion with no new evidence decays 25% of the way toward the 0.5
  prior per meeting. THE FOLD RUNS AFTER THE VOTE: a meeting's own accusations NEVER move its own
  ballots — only the NEXT meeting's. Trajectory 0.5→0.55→0.60: crossing requires 2+ reinforcing
  meetings BY DESIGN ("no single round ejects" — owner principle). At ~1.5 meetings/game this rarely
  fires; that is a GAME-LENGTH limitation, not a mechanism bug. Ballots are NOT evidence (never feed
  the accumulator). An impostor never accrues a bump against a fellow impostor (teammate guard).
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
  ejection_accuracy ~0.42 is NOT comparable to the artifact-era ~0.63 (that number was artifact
  railroads at roughly the accusation base rate; never benchmark this set against it).

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
  10.2. Invalid accusation/ballot targets are dropped BY DESIGN — the hallucination RATE is the
  signal, the drop is not a bug. KNOWN-AND-REPORTED on THIS set (PR #143) — your job is to BUILD ON
  these, not re-discover them as findings: genuine_class_conversion ~1/7 and ejection_accuracy ~0.42
  (the honest numbers; LOW conversion is the EXPECTED state — the testimony lever is un-pulled until
  10.6; do not file "conversion is low" as a finding, size its components per your lens scope); the
  hard drop in total contradiction volume vs e750b40 (repair, not regression); endpoint flags
  surviving as weak-banded (the 10.1 decision); Rule-3 corroboration events appearing for the first
  time (10.2 un-gating); a handful of opening-retry calls (10.3 validation, one retry max, by
  design); the remaining fail-soft defaulted turns (no aborts); cross-room/dead-actor same-tick kill
  rejections (engine-correct, informational). Flag only what is genuinely NEW or contradicts the
  PR's self-report (a self-report contradiction IS a high finding).
- No drive-by suggestions: a recommendation must address a cited finding.
- Severity: "blocking" = invalidates this baseline's validity (the set must be re-recorded or the
  engine fixed); "high" = changes the Phase-10 fork decision or its contract; "medium" = worth fixing
  in/before Phase 10; "low" = opportunistic; "informational" = trend/observation only.

Your lens-specific scope is below. Stay within it; do not duplicate other lenses.

`

// ---------------------------------------------------------------------------
// Lens definitions
// ---------------------------------------------------------------------------

const LENSES = [
  {
    key: 'B',
    name: 'Pacing, balance & evidence supply (the 10.7 sizing input)',
    scope: `Characterize the GAME SHAPE that Wave 1's pacing contract (10.7 emergency meeting /
pacing) must change — every number here sizes that contract. Cover: win split + win-REASON breakdown
(derive it; if CREWMATE_TASKS dominates with gap-0 task completion, quantify the stopwatch margin —
how many ticks separate the task win from the kill-clock's parity pace?); game LENGTH distribution
and MEETINGS per game (the evidence-supply numbers: the 9.8 accumulator needs 2+ reinforcing
meetings and within-round corroboration needs 2+ signals per meeting — quantify how often games
supply either: meetings/game histogram, share of games reaching 2+ meetings = the ACCUMULATOR
RUNWAY, evidence-bearing observations per meeting, witnesses per kill); the accumulator's
cross-meeting reality from the trajectory facts (carries that survived to the next meeting vs
erased by the 25% decay first — the decay-rate question 10.7 must answer); kill patterns (rooms,
tick-of-first-kill cluster, witnessed rate, body-report rate + latency, bodies never reported); the
emergency button (0 expected — structural absence vs behavior gap; meetings currently trigger only
on bodies, so impostors control meeting cadence via kill cadence — THE 10.7 lever); per-player task
pacing (front-loading, the §3.5 denominator shrink); role↔outcome correlations. Report NUMBERS;
flag degenerate clusters. Severity informational/low unless a trend exposes a defect.`,
  },
  {
    key: 'C',
    name: 'Wave-1 contract input: testimony lever, fold timing, genuine-class walk',
    scope: `THE HEADLINE LENS. The instrument is now honest (Wave 0 landed; artifact flag classes ~0)
and the headline numbers are KNOWN (PR #143: genuine_class_conversion ~1/7, ejection_accuracy ~0.42)
— do NOT re-discover them; produce the WAVE-1 CONTRACT INPUT. Derive this set's numbers from the
facts first, then answer FOUR asks with per-meeting walks, each cross-referenced with FACTS roles:
(1) MISSED-CONVERSION RE-PARTITION on honest bytes: partition EVERY meeting where a living TRUE
impostor was accused but not ejected into
(a) weak-flag-sub-gate — a structured flag named the impostor but parked suspicion in [0.5,0.60)
with no second signal;
(b1) TESTIMONY CLASS — spoken testimony named the impostor (accusation or sighting claim in a turn)
but no structured flag reached the OTHER listeners' beliefs; check the witness's own ballot
(did they vote their accusation?) and the plurality outcome (use the per-subject testimony records
in the facts: per-voter suspicions, ballots-for-subject, plurality margin);
(b2) true no-evidence — nobody spoke testimony naming them AND no flag: only more evidence supply
(longer games, more witnesses — 10.7 territory) can fix these;
(c) accumulator near-miss — a prior-meeting carry existed and ONE more reinforcing meeting would
have crossed (count games ending exactly one meeting short);
(d) strong-evidence-yet-skipped — should be 0 (genuine inversion; HIGH finding if found).
The prior-era audit (e750b40 set) found b1 DOMINANT: 27 meetings, 22 with witness-ballot
follow-through that lost plurality. State whether b1 stays dominant on honest bytes — its size IS
the 10.6 yield ceiling. Cross-set spot-checks: \`git show e750b40:replays/samples/9p2i/replay-seed-N.jsonl\`.
(2) FOLD-TIMING DECISION TABLE (the pending owner call on 10.6 — this table is the deliverable):
for EACH testimony-class meeting, simulate both ingestion options using the per-voter rendered
suspicions in the facts + the §6.3 quantized rule arithmetic, under the two most plausible ingestion
magnitudes (the 9.8 accusation unit +0.05, deduped per meeting; a weak-band flag-equivalent delta) —
label each result with its assumed magnitude:
PRE-VOTE (testimony moves listener beliefs in the SAME meeting, before ballots): would listeners'
max have crossed 0.60, and would plurality have converted? Then run the SAME rule against testimony
naming INNOCENTS (the facts carry testimony records for every accused subject, both roles): how
many innocent ejections would pre-vote ingestion have created? That cascade-risk count is the cost
column — the owner principle (no single signal/round ejects; corroborate-within-round) is the
constraint any pre-vote rule must satisfy, so also report how yield/cost shift if ingestion requires
TWO independent witnesses in-meeting.
POST-VOTE (next-meeting fold, the existing 9.8 shape): did a next meeting exist at all, and would
the 25%/meeting decay have erased the carry before it folded in? Report yield under pacing-as-is.
End with the side-by-side: pre-vote yield/cascade-cost (per magnitude, with and without the
two-witness requirement) vs post-vote yield — the numbers Daniel decides 10.6 fold timing on.
(3) GENUINE-CLASS WALK (~7 flags expected): every genuine-class flag (per the 10.4 re-derived
definition, in the facts), walked end-to-end. Verify the seed-24 conversion at BYTE level: flag →
delta arithmetic → rendered max >= 0.60 → ballots → plurality → ejection → win attribution; confirm
it is MECHANISM, not coincidence (would the ejection have happened without the flag?). Bucket each
non-conversion: sub-gate weak vs over-gate-but-plurality-failed (votes scattered or outvoted).
(4) DETECTOR HONESTY CONFIRMATION: from the facts flag inventory, confirm the artifact classes are
actually ~0 on these bytes (compound-label, placeholder, full-weight endpoint), confirm stacking
cannot reach 1.0 (per-player max-suspicion distribution), and hunt for any NEW artifact class the
repairs introduced — a canonicalization COLLISION (two genuinely different rooms mapping to one
canonical label, suppressing a real mismatch) would be a HIGH finding.
Reference meetings/transcript.py (the repaired classifier), agents/memory/beliefs.py (the 9.8
rules), eval/vote_correctness.py + eval/meeting_quality.py (the 10.4 metric definitions — the
one-home source). Cite seed+meeting+turn with votes/roles/suspicion values.`,
  },
  {
    key: 'D',
    name: 'Impostor behavior (Wave-2 toolkit input: 10.9 probe / 10.10 contracts)',
    scope: `Assess impostor play from transcripts + FACTS roles — this lens's output is the direct
input to the Wave-2 deception probe (10.9) and toolkit contracts (10.10), so quantify each TOOLKIT
GAP, not just "passive". Prior-era anchors to re-derive on THIS set (do not trust them): 0 do_task
emissions, ~54% of impostor action turns waiting, 2 idlers covering 92/100 top-idle slots.
(1) blending — do impostors emit do_task/report actions at all (exact counts), and what does their
movement look like vs crew (stalking? loitering? the idle concentration); (2) under accusation —
does the reply rebut/deflect/counter-accuse plausibly, does the chain move off them, and how often
does an accused impostor SURVIVE the vote (the deception-effectiveness number); (3) fabricated
alibis under the REPAIRED detector — how many impostor alibis drew a flag at all, weak vs strong
(all fabricated-alibi flags are weak self-stated by construction); quantify how many impostors
survived specifically BECAUSE their only flag was weak-banded (the shelter count — a Wave-1 design
tension to surface, not a bug); (4) misdirection — do impostors steer chains at innocents, exploit
opt_ins, self-report their own kills; did any wrong ejection have impostor votes as the decisive
margin; (5) teammate coordination quality WITHOUT firewall trips (betrayal must be 0 — Extract
checks); (6) kill-intent discipline — the cross-room/timing waste classes (share of kill intents
wasted). Reference observation/service.py, eval/alibi_fabrication.py. Cite seed+meeting+turn.`,
  },
  {
    key: 'H',
    name: 'Model artifacts: 10.3 effectiveness check (qwen3.5:9b)',
    scope: `VERIFY the 10.3 prompt levers against the bytes — your job is the shape and the residual,
not re-discovery. (1) RETRY YIELD: validation-failing openings (narration-only OR guard-emptied
after target validation) get exactly ONE retry. From the facts' retry aggregates + the bytes: how
many openings failed validation, how many retries RECOVERED a usable accusation vs failed again,
what did retries cost (extra calls/tokens), and did any meeting still lose its chain-driving opening
(instant termination)? A second retry or a retry on a non-failing opening would contradict the
design — HIGH finding. (2) DEAD-MARKER residual: the prior era hallucinated mostly DEAD-REAL ids
(17-18 dropped targets, dead players rather than invented names). With roster lines now DEAD-marked
(v5/v7): did the drop count actually fall, and what shape remains (dead-real vs invented like
"imp-2")? Read the rendered prompts for 2-3 dropped cases: does the roster render with correct
DEAD markers (a render bug would be a HIGH finding)? If it renders correctly and the model still
names the dead, conclude prompt-saturation (contained by the fb3cfa5 guard — model artifact, not a
fixable prompt bug). (3) FREE_TEXT DISCIPLINE state: length distribution per turn_kind vs the
~230-char medians of the prior era; for any remaining defaulted turns (2048-cap fail-softs), read
the raw_response tails — still reasoning-relocation ("Wait... actually..."), or a new shape? Do NOT
propose a cap raise (frozen; num_ctx overrun risk). (4) Any genuinely NEW 9B tell on this re-record
(fabricated ticks/rooms passing schema, repetition loops, confidence values outside the quantized
rule-delta lattice). Reference the turn prompts + meetings/manager.py. Cite seed+meeting+turn.`,
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
the 2026-06-10 post-Wave-1 close audit (role re-derivation via orchestrator.seeder, a full
advance_tick + apply_meeting_result re-walk with per-tick state-hash verification, hard-rule
classification, win cross-checks, chain-protocol checks, the SKIP partition via the shared
eval/_suspicion_parse import, the point-6b decomposition aggregates, fail-loud invariants). UPDATE
IT IN PLACE (edit the file; it gets committed alongside the audit report) rather than writing a new
script — most machinery stays; your job is (i) RE-SYNCING every classification to the Wave-0
repaired one-home sources (point 6b) and (ii) ADDING the testimony / genuine-class / trajectory /
retry aggregates (point 6c):

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
// Phase 2: Analyze (4 parallel lenses — C Wave-1-input headline on Fable,
// B/D/H on Opus; the cut lenses' live questions were folded into C/B/H or the
// extractor, see the header)
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
        // The Wave-1 contract input (testimony sizing + fold-timing table)
        // rides on lens C — Fable; the characterization lenses run on Opus.
        model: l.key === 'C' ? 'fable' : 'opus',
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
// finding; C-lens findings get Fable skeptics, the rest Opus)
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
   under low confidence; AND the Wave-1 suspicion mechanics (DESIGN.md §6.3, the audit's known
   layer): a lone WEAK contradiction (self-stated alibi or narrow window) landing in [0.5,0.60)
   without ejecting is the 9.7 DESIGN; an accusation not moving its OWN meeting's ballots is the
   9.8 fold-after-vote DESIGN; a single meeting never ejecting on accumulator alone ("no single
   round ejects") is the OWNER PRINCIPLE; suspicion decaying toward 0.5 across quiet meetings is
   Rule 5; AND the Wave-0 instrument layer (10.1-10.4, landed ON this set): canonicalized room
   labels, endpoint sightings weak-banded, alibi_conflict weak-classified, capped/deduped flag
   deltas (no 1.0 stacking), Rule-3 DOWNWARD corroboration moves, exactly ONE opening-validation
   retry, and a hard drop in total contradiction volume vs the prior era are all BY DESIGN here;
   invalid-target drops are the fb3cfa5 guard working; a metric's documented caveat is not a bug.
   Check DESIGN.md §3.5/§5.2/§6.3, engine/rules.py, meetings/manager.py, meetings/transcript.py,
   agents/memory/beliefs.py, or the metric source before confirming.
3. Context: is there invalidating context elsewhere in the set (other seeds/meetings), a numeric
   error, or a token-proxy time-waste claim presented as a latency claim (no wall-clock exists)?

Refute ONLY with a concrete basis from those checks, cited in your reasoning. If the evidence
cannot be verified either way after honest effort, set refuted=true with reasoning starting
"unverifiable:". Output the structured verdict.`,
      {
        label: `verify:${f.fully_qualified_id}`,
        phase: 'Verify',
        schema: VERDICT_SCHEMA,
        // The headline lens's findings drive the Wave-1 contracts — strongest skeptics.
        model: f.lens_key === 'C' ? 'fable' : 'opus',
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
post-Wave-0 close audit of Phase 10 (9p/2i on qwen3.5:9b @ 59e4111; the Wave-0 instrument repairs
landed, making this the first HONEST baseline — known headline per PR #143: genuine_class_conversion
~1/7, ejection_accuracy ~0.42, artifact flag classes ~0). The audit's purpose is the WAVE-1 CONTRACT
INPUT (10.6 testimony ingestion + 10.7 emergency-meeting/pacing, plus the Wave-2 impostor work): the
verdict is about baseline VALIDITY + whether the analysis surfaced anything NEW, not about
re-reporting the known-low conversion. A deterministic extractor produced code-certain rule/protocol
violations (NOT subject to refutation) plus the decomposition aggregates; the analysis lenses produced
judgment findings; each judgment finding faced ONE adversarial skeptic —
refuted findings were dropped, and any finding whose skeptic failed to run carries unverified:true.
Label unverified findings explicitly in the report ("unverified — skeptic did not run"); never
present them as verified. What remains is the load-bearing finding set.

Input data (JSON):
${JSON.stringify(synthesisInput, null, 2)}

Your output has two parts:
1. Structured synthesis: verdict (CLEAN / MINOR_ISSUES / SIGNIFICANT_ISSUES) + rationale — the
   regression itself is KNOWN and does NOT by itself drive the verdict; judge baseline validity and
   what is NEW; notable_trends (evidence-backed, with numbers); improvement_proposals (group related
   findings; one proposal per group with a reproducible scope sketch — cite the seed+tick/meeting+turn
   to reproduce — and a priority, where "urgent" = invalidates this baseline / must fix before ANY
   next wave, "phase-10-input" = must shape a Phase-10 Wave-1/2 contract (10.6 testimony, 10.7
   pacing, 10.9/10.10 impostor) or a pending owner decision, "opportunistic" = later).
2. report_markdown: the full Markdown report body, to be written to
   audits/audit-YYYY-MM-DD-HHMM-gameplay-data.md. Use this section structure:
   - "# Gameplay Data Audit — YYYY-MM-DD HH:MM (${SAMPLE_DIR}, post-Wave-0 close, Phase 10)"
   - "## 1. Verdict" (CLEAN | MINOR_ISSUES | SIGNIFICANT_ISSUES + 2-3 paragraphs; state explicitly
     whether the baseline is VALID and what the numbers say Wave 1 — 10.6 fold timing + 10.7
     pacing — should do)
   - "## 2. Environment" (timestamp from \`date\`, audited HEAD from \`git log -1 --oneline\`, sample
     dir, games analyzed, mechanical vs judgment finding counts, refute rate)
   - "## 3. Confirmed bugs & rule violations" (mechanical findings first — labelled code-certain —
     then surviving correctness judgment findings; use the verifier-adjusted severity and note
     where severity_adjusted_by_verifier is true; cite evidence + repair hint)
   - "## 4. Wave-1 contract input (headline)" — the four asks with COUNTS: (1) the
     missed-conversion re-partition (weak-sub-gate / TESTIMONY class / true no-evidence /
     accumulator-near-miss / inversion) — state whether the testimony class stays dominant and its
     size, the 10.6 yield ceiling; (2) THE FOLD-TIMING DECISION TABLE — pre-vote yield +
     innocent-cascade cost (per assumed ingestion magnitude, with and without a two-witness
     requirement) vs post-vote yield under pacing-as-is; render it as an actual table — it is the
     owner's 10.6 decision input; (3) the genuine-class walk (seed-24 mechanism-or-coincidence
     verdict; non-conversion buckets); (4) the detector honesty confirmation (artifact classes ~0,
     stacking capped, any NEW artifact class). End with ONE paragraph: what these numbers recommend
     for 10.6 (fold timing + expected yield) and how they size 10.7.
   - "## 5. Pacing, balance & evidence supply (the 10.7 sizing input)" (game length, meetings/game,
     the accumulator runway + decay-erasure counts, evidence/meeting, witnesses/kill, the stopwatch
     margin, the emergency-button structural note)
   - "## 6. Impostor behavior & model artifacts" (the Wave-2 toolkit gaps quantified — the 10.9/10.10
     input; the 10.3 effectiveness check — retry yield, DEAD-marker residual, free_text state)
   - "## 7. Metric & coverage notes" (any metric that would mislead a Wave-1 A/B; seed coverage;
     sentinel states)
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
    // The capstone judgment — the fork recommendation rides on it.
    model: 'fable',
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
