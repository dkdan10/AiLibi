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
// CURRENT TARGET — the Phase-10 WAVE-2 / PHASE-CLOSE BASELINE: 9p/2i re-recorded
// at 2fd1ace (PR #158) on qwen3.5:9b with the FULL Wave-2 bundle landed on top of
// the Wave-1 crew economy: 10.14 impostor toolkit (do_task BLENDING via a pretend
// task that makes NO real progress — surfaced only on SelfView, never a
// WorldState.tasks instance, so the win denominator can't see it; idle budget
// toward crew wait-share; same-room kill-intent gating; impostor_report v5
// anticipatory cover = the policy places the impostor in a sheltered room post-kill
// and the v5 directive builds the alibi from it), 10.15 crew belief-spread (a
// SINGLE observation-backed witness INFORMS listeners +0.05 pre-vote — a baseline
// 0.50 listener reaches 0.55, UNDER the gate, so it informs-never-ejects-alone;
// echo-dedup kills fake independence), 10.16 Wave-2 metrics (conversion_per_meeting,
// effective_deflection, indistinguishability, the inform attribution channel),
// 10.11.1 deterministic emergency-no-body backstop (retry-once-then-STRIP any
// found_body from an emergency opening — the v7 fail-loud guard is now unreachable).
// HARD validity gate GREEN both sets, and the headline is KNOWN AND ADVERSE
// (PR #158): every mechanical goal LANDED — genuine_class 2/8->7/8,
// conversion_per_meeting 0.125->0.250, multi_signal 11->20, do_task 0->371,
// wait_share 0.52->0.09, inform conversions 0->14 (above the +6 floor), emergency
// 7->16 (0 v7 crashes), wrong-ejection 8->3, unattributed 0 — BUT BALANCE
// CRATERED: impostor win rate ~2% (1/50), R1 ejection-DECIDED wins 0/50,
// effective_deflection 9->6. Derive this set's real numbers yourself. This is the
// PHASE-10 CLOSE AUDIT: the verdict is whether to LAND-AS-IS or do a targeted
// retune, and it must answer the crater + the load-bearing question:
//   (1) THE BALANCE-CRATER DECOMPOSITION (the headline). The wave worked
//       mechanically yet impostors crater. Decompose WHY from the bytes: the crew
//       side (detector + 10.15 inform, 14 conversions vs the +6 floor) OVERSHOT
//       the impostor buff — impostors now BLEND (do_task/low-wait) but do NOT
//       DEFLECT (effective_deflection 9->6), so they look busy yet get caught the
//       same; AND the crew out-TASKS (stopwatch) before ejecting the 2nd impostor,
//       so the meeting layer EJECTS-but-does-not-DECIDE. Quantify each: blend-without-
//       deflect rate, eject-decided vs stopwatch wins, the 2nd-impostor survival.
//   (2) IS THE MEETING LAYER LOAD-BEARING (R1)? Ejections work (24/27 across 96
//       meetings) but 0 games are eject-DECIDED. Decompose: of the games crew won,
//       how many had BOTH impostors ejected vs the stopwatch firing first with an
//       impostor still alive? This is the phase's whole-point verdict.
//   (3) THE TARGETED-RETUNE DECISION (owner input). Weigh the candidates from the
//       bytes: SOFTEN the 10.15 inform (the crew lever over-delivered 14 vs +6),
//       STRENGTHEN 10.14 deflection (make impostors credible under accusation, not
//       just blending), or the deeper STOPWATCH dominance (crew out-tasks — touches
//       the frozen task clock, a bigger call). Which most cheaply un-craters balance
//       without re-breaking R4? Size each.
//   (4) DID THE WINS COME CLEAN (R4 + firewall)? inform conversions 14, wrong-
//       ejection 3, unattributed 0 — verify no railroading crept in with the
//       stronger crew lever, betrayal stayed 0, and the do_task blending never
//       advanced the real task-win counter (the 10.14 integrity invariant) on the
//       recorded bytes.
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
  description: 'Structured PHASE-CLOSE audit of a committed chain-protocol replay set (9p/2i, per-player tasks, accusation-chain meetings): deterministic rule + integrity + crater checks in Extract, 6 analysis lenses (balance-crater + load-bearing headline, pacing/stopwatch + cross-era trajectory, blend-vs-deflect + tuning-vs-model fork, COUNTERFACTUAL retune simulation, single-game narrative read, frame-questioning/structural altitude), adversarial + retune-skeptic verify, prescriptive synthesis. Baseline-agnostic; runs on Opus 4.8 throughout (Fable 5 suspended; the headline lens C + synthesis were the Fable tier).',
  whenToUse: 'After a chain-protocol eval set is recorded — currently the Phase-10 CLOSE AUDIT on the Wave-2 baseline: decompose the balance crater (crew overshoot: blend-without-deflect + stopwatch-still-decides), answer whether the meeting layer is load-bearing (R1), and produce the targeted-retune decision input that closes the phase.',
  phases: [
    { title: 'Extract', detail: 'One agent updates + runs the committed extractor: roles, resolved events, hard-rule + chain-protocol checks, crater/conversion/blend-deflect aggregates into a facts JSON' },
    { title: 'Analyze', detail: '6 parallel lenses over the facts + transcripts on Opus 4.8 (C balance-crater + load-bearing headline; B pacing/stopwatch + cross-era trajectory; D blend-vs-deflect + tuning-vs-model fork; E counterfactual retune simulation; F single-game narrative read; G frame-questioning/structural altitude)' },
    { title: 'Verify', detail: 'Mechanical findings pass through; each judgment finding gets one skeptic (refuted drops; a failed skeptic passes it through flagged unverified)' },
    { title: 'Synthesis', detail: 'Group findings, decompose the balance crater, judge load-bearing (R1) + clean-wins (R4), recommend the targeted retune, write the phase-close report' },
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
    global cooldown), trigger_kind "emergency", crewmate_report v7 (the v6 emergency branch + the
    10.11 no-found_body fix). An emergency meeting has NO found_body. 10.11.1 adds a DETERMINISTIC
    backstop: any found_body the 9B still emits on an emergency opening is retried-once-then-STRIPPED
    (the v7 fail-loud guard is now unreachable) — a stripped emergency body is BY DESIGN, not a defect.
  - 10.9.1 VOTE-BALLOT FAIL-SOFT: a vote completion that fails to parse twice degrades to a SKIP
    stamped VOTE_PARSE_DEFAULT_MARKER (a defaulted-ballot), the game CONTINUES. A defaulted SKIP is
    NEVER a threshold_inversion and never a silent missed_skip — by design.
  - 10.9.2 BALLOT-TARGET GRAPH GUARD: an eject ballot under a MUST-vote verdict that names a target
    the voter's own rendered graph carries BELOW 0.60 (or no row for) is REDIRECTED to the voter's
    argmax-rendered ≥0.60 eligible candidate (ties lowest id; teammate-only-over-gate → SKIP), stamped
    BALLOT_TARGET_REDIRECT_MARKER. The redirect is BY DESIGN — it kills ungrounded-target ejections.
    A redirect that lands on an INNOCENT (the argmax happened to be crew) is graph-consistent, NOT a
    railroad; whether the redirected-to innocent's ≥0.60 is EARNED is a deduction-quality question,
    not a mechanical defect. A redirected eject is never a threshold_inversion.
  (e) WAVE-2 IMPOSTOR TOOLKIT + CREW BELIEF-SPREAD (10.14-10.16, landed ON this set — the layer that
  PRODUCED the crater; load-bearing for every crater judgment):
  - 10.14 IMPOSTOR TOOLKIT: an idle impostor emits a fake do_task that consumes the tick and RENDERS
    as do_task but makes NO real progress — the pretend task is surfaced only on the impostor's
    SelfView and is NEVER a WorldState.tasks instance, so the engine win denominator cannot see it
    (the integrity invariant: a fake task can never help the crew win). The idle budget trends
    impostor wait-share toward the crew level; same-room kill-intent gating drops cross-room kill
    no-ops. impostor_report v5 ANTICIPATORY COVER: the policy physically routes the impostor to a
    sheltered task room after a kill and the v5 directive builds the alibi from that real location,
    pinned/reused (not regenerated). do_task>0 and a low impostor wait-share are BY DESIGN here, NOT a
    leak. The 7.12 firewall + betrayal==0 stay inviolate.
  - 10.15 CREW SINGLE-WITNESS INFORM: a SINGLE observation-backed relevance-passing witness moves
    every living listener +0.05 PRE-VOTE against the subject (REUSES the 9.8 unit, no new magnitude) —
    a separate band from the 10.7 two-witness fold. A baseline 0.50 listener reaches 0.55, UNDER the
    0.60 gate, so the inform INFORMS-NEVER-EJECTS-ALONE; crossing still needs the listener's own prior
    (corroboration). Echo-dedup collapses near-identical rationales across distinct voters (the H-4
    fake-independence fix) and applies to BOTH bands. A listener informed over 0.60 by a prior +0.05 is
    the MECHANISM, not an inversion. NOTE: this is the lever that OVER-DELIVERED (14 conversions vs the
    +6 offline floor) — its strength relative to the impostor buff is the crater's crew-side half.
  - 10.16 WAVE-2 METRICS: conversion_per_meeting (impostor ejections / meetings — pacing-inversion
    proof); effective_deflection (of accused-impostor ACTIVE survivals, the subcount where plurality
    actually moved OFF the impostor — deception SKILL, distinct from SKIP-saved survival); the
    indistinguishability gauges (impostor vs crew wait-share, do_task-by-role, idler concentration);
    and the INFORM attribution channel in the ejection decomposition (mass-attributed: credits the
    inform only when its +0.05 quantum is visible in the persistent mass, so crew-lever conversions are
    separable from the toolkit's effects in this ONE confounded combined re-record). The win split is a
    GUARDRAIL, never a signal — attribution is via the decomposition.

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
  not a bug. ALSO repaired/known and NOT new defects: the VARYING_ROOMS leak (10.6 allowlist, expect
  0); the vote-truncation abort (10.9.1 defaulted SKIP); the redirect-into-crew laundering (10.10
  proxy-intra-turn guard); the emergency fabricated-body (10.11 + 10.11.1 deterministic strip — a
  stripped emergency body is by-design, NOT a defect or a crash); do_task>0 + low impostor wait-share
  (the 10.14 blending toolkit working, NOT a leak — but VERIFY no fake task advanced the real win
  counter). KNOWN-AND-REPORTED on THIS set (PR #158) — your job is to DECOMPOSE these, not re-discover
  them as findings: every MECHANICAL goal LANDED (genuine_class ~7/8, conversion_per_meeting ~0.25,
  multi_signal ~20, do_task ~371, wait_share ~0.09, inform conversions ~14, emergency ~16, 0 v7
  crashes, wrong-ejection ~3, unattributed 0) AND the BALANCE CRATERED (impostor win rate ~2%, R1
  ejection-decided wins ~0, effective_deflection ~6) — do NOT file "impostors lost" or "balance is
  off" as a finding; DECOMPOSE the crater (crew overshoot: blend-without-deflect + stopwatch-decides)
  and size the targeted retune, per the headline lens. The owner has ADJUDICATED this set as the W2
  baseline pending this audit's retune recommendation — the verdict is land-as-is vs targeted retune,
  NOT baseline-invalid. Flag only what is genuinely NEW or contradicts the PR's self-report (a
  self-report contradiction IS a high finding).
- No drive-by suggestions: a recommendation must address a cited finding.
- Severity: "blocking" = the substrate is broken / the set must be re-recorded or the engine fixed
  (the bytes are HARD-green, so this should be empty); "high" = changes the targeted-retune decision
  or a pending owner call; "medium" = worth fixing in the retune; "low" = opportunistic;
  "informational" = trend/observation only.

Your lens-specific scope is below. Stay within it; do not duplicate other lenses.

`

// ---------------------------------------------------------------------------
// Lens definitions
// ---------------------------------------------------------------------------

const LENSES = [
  {
    key: 'B',
    name: 'Pacing, the stopwatch & why ejection does not decide (crater-support)',
    scope: `Characterize the GAME SHAPE that makes the meeting layer EJECT-BUT-NOT-DECIDE — this lens
supplies the stopwatch half of lens C's R1 verdict and the retune sizing. Cover: (1) THE STOPWATCH
(the load-bearing question): win-REASON breakdown — if CREWMATE_TASKS still dominates (~98%), quantify
HOW the crew wins: at the task win, how many impostors were still alive, and how many ticks separated
the task-completion from the 2nd-impostor ejection that never came? Compute the stopwatch margin
(ticks between the task win and the kill-clock parity pace) — the lab found it a HAIR-TRIGGER (~6
ticks of slowdown flips ~25% of outcomes), so REPORT it precisely as the retune-(iii) input, do NOT
propose tuning the frozen clock. Cross meetings-count against win-reason: did MORE meetings still
correlate with impostor wins (the persistent inversion), or did the toolkit change it? (2) EMERGENCY
CHANNEL at scale (10.8 + 10.11.1): ~16 emergency meetings — break down callers/roles/triggering
suspicion, confirm 0 v7 fail-loud crashes (the 10.11.1 backstop validated), and whether any emergency
opening still emitted a found_body that was STRIPPED (by-design) vs assumed downstream. Did emergency
meetings add cross-round runway, and did that runway convert or just add ejections that did not
decide? (3) PACING/RUNWAY: meetings/game histogram + share reaching 2+; meeting_rate; is the layer
now meeting-RICH but conversion-decisive-POOR? (4) SUPPLY: evidence-bearing observations per meeting,
witnesses per kill, kill patterns (rooms, first-kill tick cluster, witnessed rate, body-report rate +
latency), per-player task pacing + the §3.5 denominator shrink, role↔outcome correlations.
(5) THE CROSS-ERA TRAJECTORY (new — overshoot vs trend): plot the key metrics across the THREE
committed eras — W0 @ 59e4111, W1 @ 0ed6962, W2 @ 2fd1ace (read the prior sets via
\`git show <sha>:replays/samples/9p2i/tournament-eval-report.json\` or the committed corrected_w0/w1
baseline fixtures): impostor win rate, R1 ejection-decided wins, effective_deflection, genuine/multi
conversion, meetings/game. Is the crater a ONE-WAVE OVERSHOOT (a metric that jumped this wave and a
retune walks back) or a TREND (impostors monotonically declining across all three — a structural
signal that no single retune fixes)? This shapes whether the close recommends a targeted retune or a
deeper rethink. Report NUMBERS; flag degenerate clusters. Severity informational/low unless a trend
exposes a defect or directly shapes the retune.`,
  },
  {
    key: 'C',
    name: 'The balance crater + load-bearing verdict + targeted-retune decision (PHASE-CLOSE HEADLINE)',
    scope: `THE HEADLINE LENS — the PHASE-10 CLOSE verdict. The wave worked MECHANICALLY (genuine_class
~7/8, do_task ~371, inform ~14, emergency ~16) yet BALANCE CRATERED (impostor win ~2%, R1 ejection-
decided wins ~0, effective_deflection ~6). Do NOT re-discover those numbers — DECOMPOSE the crater and
recommend the retune. Derive this set's numbers from the facts first, then answer FOUR asks with
per-game/per-meeting byte walks, each cross-referenced with FACTS roles:
(1) THE CRATER DECOMPOSITION (the deliverable). Two mechanisms are hypothesized; quantify EACH from
the bytes and say which dominates. (a) BLEND-WITHOUT-DEFLECT: the 10.14 toolkit made impostors LOOK
busy (do_task up, wait down) but did it make them HARDER TO CATCH? Cross do_task/wait-share against
accused-impostor OUTCOMES: of impostors accused, how many actively DEFLECTED (effective_deflection,
plurality moved off them) vs were caught anyway? Compare the impostor catch rate to the W1 baseline —
if blending rose but catch rate did NOT fall (or rose), the toolkit gave visibility-of-busyness
without deception, and the crew's stronger detection+inform simply converts the now-more-active
impostor. (b) CREW OVERSHOOT: the 10.15 inform delivered ~14 conversions vs the +6 offline floor —
walk the inform-channel ejections (the 10.16 mass-attributed channel); are they CLEAN (real
observation-backed witnesses informing a real majority) or did the stronger lever simply out-pace the
impostor buff? Report the inform's true conversion count and whether any were marginal/over-eager.
State the crater's dominant cause: impostor-buff-too-weak (deflection), crew-lever-too-strong (inform),
or both.
(2) IS THE MEETING LAYER LOAD-BEARING (R1 — the phase's whole-point verdict)? Ejections WORK
(~24/27 impostor ejections across ~96 meetings) but ~0 games are ejection-DECIDED. Partition the crew
wins: how many ended with BOTH impostors removed by the meeting layer vs the task STOPWATCH firing
first with an impostor still alive? Quantify the 2nd-impostor survival-to-stopwatch rate. If the crew
out-tasks before the 2nd ejection in nearly every game, the meeting layer EJECTS-BUT-DOES-NOT-DECIDE —
state that plainly as the R1 verdict, and identify what would make ejection decide (faster conversion,
slower stopwatch, or fewer tasks-per-crewmate).
(3) THE TARGETED-RETUNE DECISION (the owner's input). Size each candidate from the bytes and give a
recommendation: (i) SOFTEN the 10.15 inform (e.g. require 2 informers, or shrink its reach) — how many
of the ~14 inform conversions would it remove, and does that restore impostor breathing room without
re-opening the SKIP-plurality bloc? (ii) STRENGTHEN 10.14 deflection (make impostors credible under
accusation) — the deception lab showed the 9B performs a scripted deflection; is the toolkit's cover
directive reaching the reply turns, or only the opening? (iii) the STOPWATCH (crew out-tasks) — this
touches the FROZEN task clock / tasks-per-crewmate, the biggest call; quantify the stopwatch margin
but flag it as owner-only. Rank by "un-craters balance most cheaply without re-breaking R4."
(4) DID THE WINS COME CLEAN (R4 + integrity)? With the stronger crew lever, verify no railroading
crept back: wrong-ejection games ~3 (down from 8) all graph-consistent, threshold_inversions 0,
innocents-at-1.0 0, unattributed ejections 0; betrayal 0; and the 10.14 INTEGRITY INVARIANT — no fake
do_task advanced the real task-win denominator (spot-check the recorded task-progress vs impostor
do_task emissions). Any breach here is a HIGH/blocking finding that overrides the land-as-is verdict.
Reference meetings/transcript.py + meetings/manager.py + agents/memory/beliefs.py (the inform/fold),
agents/tactical/impostor_policy.py (the toolkit), eval/meeting_quality.py (conversion_per_meeting /
effective_deflection / the inform channel). Cite seed+meeting+turn with votes/roles/suspicion values.`,
  },
  {
    key: 'D',
    name: 'Impostor behavior: blend-vs-deflect (the toolkit half of the crater)',
    scope: `Assess whether the 10.14 toolkit made impostors CREDIBLE or merely BUSY — this lens is the
impostor half of the crater and the input to the retune-(ii) decision. The deception lab thesis: the
9B performs SCRIPTED deflection but does not invent it. The toolkit shipped blending (do_task) +
anticipatory cover; the crater suggests it gave busyness, not deception. Quantify from the bytes:
(1) BLENDING (did it land): do_task / report emission counts by role (expect impostor do_task ~371,
up from 0 — confirm it RENDERS as do_task and VERIFY no fake task advanced the real task counter, the
10.14 integrity invariant); impostor wait-share vs crew (~0.09 vs ~0.10 — the fingerprint erased?);
idler concentration. (2) DEFLECTION — THE TUNING-vs-MODEL-CEILING FORK (the crater driver AND the most decision-relevant
distinction in the whole audit): the effective_deflection subcount (~6, DOWN from 9) — of impostors
accused, how many actively moved the plurality OFF themselves? Walk 4-6 accused-impostor reply turns
and classify the gap as ONE of two kinds, because they imply OPPOSITE retunes: (i) TUNING GAP — the
v5 cover reaches only the OPENING, not the REPLY turns (the accusation_round path), so the impostor
has a prepared alibi but no instruction to DEPLOY it under accusation; or the cover directive is
present but the policy does not route it to the reply. This is FIXABLE by 10.14 tuning (wire the cover
into the reply). (ii) MODEL-CEILING GAP — the directive IS reaching the reply and the 9B still folds
(goes quiet, confesses-shaped, fails to counter-accuse coherently) under accusation. The deception lab
showed the 9B performs a SCRIPTED deflection in isolation; does it sustain one IN-GAME under a real
accusation chain, or does the chain pressure break it? If the latter, NO 10.14 tuning fixes the crater
and the answer is a model question (bigger model / different impostor design) — a phase-boundary
finding. State which kind dominates with cited reply-turn evidence; this fork decides retune-10.14 vs
reopen-the-model.
(3) COVER QUALITY: of impostor fabricated alibis, how many drew a flag (weak vs strong); did the
pinned-cover (battery-2 P1) hold across turns or drift; the shelter count (survived because the only
flag was weak). (4) THE 2nd IMPOSTOR: in crew-win games, what was the surviving impostor DOING while
its teammate was ejected and the stopwatch ran — blending idly, or actively protecting itself? (the
"busy but passive" pattern). (5) MISDIRECTION + self-accusation residual (does an impostor steer
chains / self-name; did impostor-vote decide any of the ~3 wrong ejections). (6) TEAMMATE COORDINATION
without firewall trips (betrayal 0 — Extract checks). (7) KILL-INTENT discipline (cross-room/timing
waste — the 10.14 gating should have cut the ~15% MECH-B-1 class; confirm). Reference
agents/tactical/impostor_policy.py, observation/service.py, eval/alibi_fabrication.py. Cite
seed+meeting+turn.`,
  },
  {
    key: 'E',
    name: 'Counterfactual retune simulation (the PRESCRIPTIVE lens — predict, do not just describe)',
    scope: `THE NEW ANGLE. Lens C decomposes WHY balance cratered; this lens PREDICTS what each retune
would DO, by re-simulating it against the recorded bytes — turning the audit from "here is the crater"
into "here is the retune that un-craters it, with a predicted number." For each candidate, state
whether it is OFFLINE-PREDICTABLE (re-derivable from the recorded per-voter graphs / timelines — like
the tally lab's 6/37 yield) or GENERATIVE (depends on what the model WOULD do, not re-derivable from
old bytes), and give the number or the honest boundary. VALIDATE THE ORACLE FIRST: re-derive the W2
ACTUAL win split + R1 + effective_deflection from the bytes and confirm it reproduces the recorded
values (the tally-lab V0 self-check discipline) before layering any counterfactual — a counterfactual
on an oracle that does not reproduce the actuals is worthless.
(1) SOFTEN THE 10.15 INFORM (offline-predictable). The inform's +0.05 listener lift is re-derivable
from the recorded vote-prompt graphs. Simulate variants: (a) require 2 independent informers (not 1);
(b) shrink the inform reach. For each, RE-DERIVE which of the ~14 inform-channel conversions disappear,
RE-TALLY under the frozen equal-votes+tie→SKIP rule, and report the predicted impostor win rate / R1
eject-decided / wrong-ejection delta. The question: does softening restore impostor breathing room
WITHOUT re-opening the SKIP-plurality bloc (the W1 problem)? Give the predicted-balance row per variant.
(2) THE STOPWATCH (offline-predictable). Reuse the stopwatch-lab logic on the W2 bytes: for a task-clock
slowdown Δ (or a tasks-per-crewmate bump), how many CREWMATE_TASKS wins flip to "2nd impostor ejected
first" or to an impostor parity win? This isolates whether the crater is fixable by giving the meeting
layer TIME to decide vs needing a behavior change. REPORT the curve (Δ → predicted win split); flag the
frozen-clock owner-call, do NOT propose tuning it — just price it.
(3) STRENGTHEN 10.14 DEFLECTION (GENERATIVE — the honest boundary). You CANNOT re-derive "the impostor
deflects better" from old bytes (the reply turns are what the model actually said). So do NOT fake a
number — instead scope the CHEAPEST way to estimate it: a focused scratch micro-set (5-10 games with
the strengthened cover directive on a throwaway branch) or a deception-probe battery extension. State
what it would cost and what it would measure (effective_deflection lift), so the owner can decide
whether to spend it before committing to the deflection retune.
(4) THE COMBINED FRONT. The crater came from TWO adversarial changes; a retune may need to move BOTH
(soften crew AND strengthen impostor). Where offline-predictable, simulate the soften-inform +
stopwatch COMBINATION and report the predicted balance — the single most decision-relevant number for
"land a retune in one more re-record." Rank all candidates by predicted-balance-improvement per unit
of risk (R4 re-break, SKIP-bloc reopening, frozen-constant cost).
Reference the tally lab + stopwatch lab patterns (experiments/lab/*.py — the offline-simulation
machinery already exists), eval/meeting_quality.py (the metric definitions), the recorded per-voter
graphs in the facts. (The 10.11.1 backstop validation, the do_task integrity invariant, and the
model-artifact residuals are now Extract mechanical/self-checks — this lens is purely prescriptive.)
Cite seed+meeting+turn and show the re-derivation arithmetic for every predicted number.`,
  },
  {
    key: 'F',
    name: 'Single-game narrative read (the qualitative complement the aggregates flatten)',
    scope: `Read THREE full games end-to-end as STORIES — the angle the four quantitative lenses cannot
reach, because the crater is fundamentally "the game is not interesting" and that lives in the
beat-by-beat dynamics statistics average away. Pick: (1) THE IMPOSTOR WIN — the ~1 game impostors won;
narrate exactly how (which kills, which meeting did NOT catch them, what the surviving impostor did);
this is the existence proof of what impostor success looks like on this baseline. (2) A REPRESENTATIVE
STOPWATCH WIN — a typical CREWMATE_TASKS game; narrate the boring default beat by beat: do the crew
rush tasks while a meeting ejects ONE impostor and simply ignores the second until the clock fires?
what does a spectator actually SEE — tension or bookkeeping? (3) THE MOST-INTERESTING / NEAR-MISS game
— a game where the meeting layer ALMOST decided, or a genuine suspicion arc / dramatic reversal
occurred; narrate the arc. For each: the actual sequence (kills→bodies→meetings→accusations→suspicion
trajectories→the decisive moment or its absence), what a SPECTATOR would experience (R7 legibility +
the interestingness verdict), and the ONE dynamic the aggregates hid. Do NOT re-derive metrics — this
lens reads transcripts as narrative and reports what the numbers cannot show. The synthesis uses these
as the concrete stories behind the verdict. Cite the full beat sequence per game (seed + ticks +
meeting turns).`,
  },
  {
    key: 'G',
    name: 'Frame-questioning: is a targeted retune the right altitude, or is this structural?',
    scope: `THE "NEW ANGLES" LENS — step OUTSIDE the three local retune candidates (soften-inform /
strengthen-deflection / stopwatch) and ask whether they are local optima on a game that is
STRUCTURALLY a task race where deduction is decorative. The signal: R1 ejection-decided wins ~0 across
W0->W1->W2 (1/46 -> 1/50 -> 0/50) — every wave bolted more deduction machinery onto a game whose
outcome the stopwatch decides. Honestly weigh structural levers the local retunes CANNOT reach, each
with the bytes that motivate it: (a) THE WIN-CONDITION BALANCE — crew wins by TASKS (~45) vs EJECTION
(~1); is the task win simply too easy/fast relative to the ejection path, and would re-balancing the
two win conditions (not the §4.6 gate — the win-condition weighting) do more than any suspicion
retune? Also flag the DEFERRED win-condition-elimination gap ([[project_win_condition_impostor_elimination_gap]] —
game continues past the last impostor, repro seed 49) as a related correctness item that surfaces here.
(b) TASK STRUCTURE — tasks-per-crewmate / the clock (FROZEN, owner-only — price it, do not propose
tuning). (c) THE DEEPER ON-RECORD QUESTIONS — does the crater point at the model ceiling (lens D's
fork) or at the heterogeneous/adapting-agents direction (the meta-game upside)? The DELIVERABLE is the
altitude verdict, stated honestly: is a targeted Wave-2.5 retune SUFFICIENT to make the meeting layer
load-bearing, or is Phase 10's whole approach (deduction machinery on a stopwatch race) hitting a
ceiling that a structural change addresses better? This is NOT a mandate to do a structural change —
it is the check that prevents anchoring on "just retune," and it feeds the Phase-11 / post-Phase-10
direction. Reference engine/win_conditions.py, DESIGN.md §3, and the cross-era trajectory (lens B /
the 6f aggregate). Cite the cross-era numbers + the win-reason split.`,
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
the 2026-06-13 Wave-1 close audit (role re-derivation via orchestrator.seeder, a full advance_tick +
apply_meeting_result re-walk with per-tick state-hash verification, hard-rule classification, win
cross-checks, chain-protocol checks, the SKIP partition via the shared eval/_suspicion_parse import,
the point-6b/6c/6d decomposition + redirect/fold/emergency/self-accusation aggregates, the 10.6
retarget exclusion, the ballot confidence field, fail-loud invariants). UPDATE IT IN PLACE (edit the
file; it gets committed alongside the audit report) rather than writing a new script — most machinery
stays; your job is (i) RE-SYNCING every classification to the one-home repaired sources (point 6b —
unchanged, the detector source did not move for Wave 2) and (ii) ADDING the WAVE-2 CRATER aggregates
the close lenses need (point 6e below): actions-by-role + the do_task integrity check, effective
deflection, inform-channel conversions, and the win-decision (eject-decided vs stopwatch) attribution
— plus the 10.11.1 emergency-strip telemetry on the existing emergency aggregate (6d, updated above):

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
   - WAVE-2 INTEGRITY (code-certain, absorbed from the dropped model-artifact lens — these are the two
     things that override the land-as-is verdict, so they are mechanical not judgment):
     (a) EMERGENCY-BACKSTOP LEAK (10.11.1): any meeting with trigger_kind "emergency" whose FINAL
     recorded opening turn still carries a found_body observation — the retry-then-strip backstop
     leaked; blocking finding citing seed+meeting. (A found_body the backstop STRIPPED is gone from
     the recorded turn, so its presence = leak.) Also report the residual-fabrication COUNT (emergency
     openings that needed the strip) as an aggregate, not a finding.
     (b) FAKE-TASK PROGRESS (10.14): any impostor do_task that advanced a REAL task instance (cross
     the impostor do_task actions against the walked task-progress state) — the integrity invariant
     breach; blocking finding. A fake task must consume the tick and render as do_task while moving NO
     real task counter; one advance is blocking.
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
     from the failed_call records — the 9B turn-verbosity truncations (the residual model-artifact
     signal, now an aggregate rather than a full lens).
   - free_text length distribution per turn_kind (median / p95 / max chars) over NON-defaulted turns
     (the catastrophic-tail check the 10.12 unsure-guard should have cut — report the max, flag a
     3000+ char opening as a residual artifact aggregate, not a lens).

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
   - EMERGENCY MEETINGS (10.8 + 10.11.1): every meeting with trigger_kind "emergency" {seed, meeting,
     caller, caller_role, the caller's rendered max suspicion at call time if recoverable, whether
     the OPENING TURN carried a found_body observation (10.11.1 STRIPS it — so on the final recorded
     transcript this MUST be none; a found_body that SURVIVED onto an emergency opening turn is a
     blocking finding = the backstop leaked), and whether a retry/strip telemetry marker is present
     (the residual-fabrication signal — how often the 9B still tried), outcome}. Aggregate emergency
     count + body-report count (should partition the meeting total) + emergency-strip count.
   - SELF-ACCUSATIONS (the emergence class): every accusation where speaker == accused {seed, meeting,
     speaker, speaker_role, whether any OTHER voter then targeted that speaker (adoption)}.

6e. ADD THE WAVE-2 CRATER AGGREGATES (NEW this audit — the headline lens depends on these; import the
   10.16 helpers + the 10.14/10.15 markers, never hardcode):
   - ACTIONS BY ROLE (the blending census): per-role counts of do_task / report / wait / move / kill
     from the replay tick stream (reuse eval.action_ingest.tally_actions_by_role); impostor do_task
     count, impostor vs crew wait-share, idler concentration. INTEGRITY CHECK: cross every impostor
     do_task against the recorded task-progress — confirm NO impostor do_task advanced a real task
     instance (the 10.14 invariant); a single advance is a blocking finding.
   - EFFECTIVE-DEFLECTION RECORDS: for each accused living impostor, classify the outcome —
     ACTIVE-DEFLECTED (the impostor counter-accused/rebutted AND the plurality moved OFF them to a
     third party or their named target), PASSIVE-SURVIVED (survived via SKIP-plurality, not skill),
     or CAUGHT (ejected). Reuse eval.meeting_quality.compute_effective_deflection. This is the
     blend-vs-deflect split — the toolkit-half of the crater.
   - INFORM-CHANNEL CONVERSIONS: every impostor ejection whose 10.16 channel decomposition credits
     the single-witness inform (mass-attributed, WITNESS_INFORM_REASON) {seed, meeting, subject,
     the informing witnesses + their backing observations, the listeners the inform lifted over 0.60,
     whether the conversion is clean (real observation-backed) or marginal}. Count vs the +6 offline
     floor — the crew-overshoot half of the crater.
   - WIN-DECISION ATTRIBUTION (the R1 verdict input): per game {winner, reason, impostors_alive_at_end,
     n_impostor_ejections, was_eject_DECIDED (both impostors removed by the meeting layer) vs
     STOPWATCH (CREWMATE_TASKS fired with an impostor still alive), and for stopwatch wins the tick
     margin between task completion and the would-be 2nd ejection}. Aggregate: eject-decided count,
     2nd-impostor survival-to-stopwatch rate — the load-bearing numbers.

6f. ADD THE CROSS-ERA + RUBRIC INPUTS (so lenses B/E don't each re-read prior eras):
   - CROSS-ERA TRAJECTORY: read the committed corrected_w0_baseline.json + corrected_w1_baseline.json
     fixtures (and/or \`git show 59e4111:.../tournament-eval-report.json\` and 0ed6962) and emit a
     W0->W1->W2 comparison row for: impostor win rate, R1 ejection-decided wins, effective_deflection,
     genuine/multi conversion, conversion_per_meeting, meetings/game. The overshoot-vs-trend signal.
   - RUBRIC SCORE: shell out to experiments/lab/rubric_score.py on THIS facts file (or replicate its
     R1-R7 computation) and embed the scorecard, so lens C can name the highest-leverage R-item the
     retune should move. (rubric_score reads the same facts JSON; one home.)

7. SELF-CHECK INVARIANTS (keep the existing fail-loud set: per-seed impostor count == roster,
   games_analyzed == file count, meeting-record count match, kill-victim/death consistency,
   state-hash matches) and ADD: every meeting's transcript.turns is non-empty with exactly one
   opening at index 0; ballot voters are alive at the meeting tick; AND the COUNTERFACTUAL ORACLE
   self-check — the extractor's re-derived W2 win split + R1 + effective_deflection must reproduce the
   recorded tournament-eval-report values (a counterfactual built on an oracle that does not reproduce
   the actuals is worthless; lens E depends on this). Print each check; RAISE on any failure — a
   silent extraction bug poisons the whole audit.

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
        // phase-close headline (balance-crater + load-bearing verdict + the
        // targeted-retune decision) is lens C; when Fable returns, restore the
        // tier: l.key === 'C' ? 'fable' : 'opus'.
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
   candidate is the 10.9.2 DESIGN; AND THE WAVE-2 LAYER (10.14-10.16, 10.11.1, landed ON this set):
   impostor do_task emissions + a low impostor wait-share are the 10.14 blending toolkit working (NOT
   a leak — UNLESS a fake task advanced the real task-win counter, which IS a breach); a SINGLE
   observation-backed witness moving listeners +0.05 pre-vote is the 10.15 inform DESIGN (a baseline
   0.50 listener reaching 0.55 stays under-gate — informs, never ejects alone; a listener informed
   over 0.60 by a prior carry is the mechanism, not an inversion); a found_body STRIPPED from an
   emergency opening is the 10.11.1 backstop DESIGN; the BALANCE CRATER itself (impostors lose ~98%)
   is the KNOWN adverse outcome the owner adjudicated — refute any finding that merely re-states
   "impostors lost" or "balance is off" (the audit DECOMPOSES it, it does not re-discover it). The
   invalid-target drop is the fb3cfa5 guard; a metric's documented caveat is not a bug. Check
   DESIGN.md §3.5/§5.2/§6.3, engine/rules.py, meetings/manager.py, meetings/transcript.py,
   agents/memory/beliefs.py, agents/tactical/impostor_policy.py, or the metric source before confirming.
3. Context: is there invalidating context elsewhere in the set (other seeds/meetings), a numeric
   error, or a token-proxy time-waste claim presented as a latency claim (no wall-clock exists)?
4. RETUNE-PROPOSAL angle (for lens-E counterfactual / retune findings): if the finding PROPOSES or
   PREDICTS a retune outcome, refute it as a SKEPTIC OF THE RETUNE, not just of the claim — (a) is the
   prediction OFFLINE-DERIVABLE or did the lens fake a number for a GENERATIVE change (a "softening
   the inform yields X wins" number is legitimate if re-derived from the recorded graphs; a
   "strengthening deflection yields X" number from old bytes is NOT derivable and must be refuted as
   fabricated); (b) does the re-tally honor the FROZEN equal-votes+tie→SKIP rule and the §4.6 gate;
   (c) does the proposed retune RE-BREAK a held invariant — re-open the SKIP-plurality bloc (the W1
   problem), raise wrong-ejection games (R4), or overshoot impostors past a sane band? A retune
   prediction that ignores its own cascade/overshoot cost is refuted. Verify the re-derivation
   arithmetic the finding shows; if it shows none for a number, refute it.

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
  `You are synthesizing the PHASE-10 CLOSE AUDIT of AiLibi's committed replay set ${SAMPLE_DIR} — the
Wave-2 baseline (9p/2i on qwen3.5:9b @ 2fd1ace; the full Wave-2 bundle landed — 10.14 impostor toolkit,
10.15 crew single-witness inform, 10.16 metrics, 10.11.1 emergency-no-body backstop, on top of the
Wave-0/1 instrument + crew economy). The headline is KNOWN AND ADVERSE (PR #158): every MECHANICAL
goal landed (genuine_class ~7/8, do_task ~371, inform ~14, emergency ~16, 0 v7 crashes, wrong-ejection
~3) BUT BALANCE CRATERED (impostor win ~2%, R1 ejection-decided wins ~0, effective_deflection ~6); the
owner has ADJUDICATED this set as the W2 baseline pending THIS audit's retune recommendation. The
audit is the PHASE-10 CLOSE: the verdict is LAND-AS-IS vs a TARGETED RETUNE — decompose the crater,
answer whether the meeting layer is load-bearing (R1), and recommend the retune; do NOT re-report the
known crater. A deterministic extractor produced code-certain rule/protocol violations (NOT subject to
refutation) plus the crater aggregates; the analysis lenses produced judgment findings; each judgment
finding faced ONE adversarial skeptic — refuted findings were dropped, and any finding whose skeptic
failed to run carries unverified:true. Label unverified findings explicitly ("unverified — skeptic did
not run"); never present them as verified. What remains is the load-bearing finding set.

Input data (JSON):
${JSON.stringify(synthesisInput, null, 2)}

Your output has two parts:
1. Structured synthesis: verdict (CLEAN / MINOR_ISSUES / SIGNIFICANT_ISSUES) + rationale — the substrate
   is HARD-green so "blocking" should be empty; the verdict reflects whether the crater is a clean
   retune-and-ship (MINOR) or exposes something structural like the stopwatch dominance (SIGNIFICANT);
   state explicitly whether the baseline LANDS-AS-IS or needs a targeted retune, and whether the
   meeting layer is load-bearing (R1). notable_trends (evidence-backed, with numbers);
   improvement_proposals (group related findings; one proposal per group with a reproducible scope
   sketch citing seed+tick/meeting+turn — and a priority, where "urgent" = a substrate/integrity breach
   that overrides land-as-is (e.g. a fake do_task that advanced the win counter, a railroad regression),
   "phase-10-input" = the targeted-retune candidates (soften 10.15 inform / strengthen 10.14 deflection /
   the stopwatch owner-call) or a Phase-11 input, "opportunistic" = later).
2. report_markdown: the full Markdown report body, to be written to
   audits/audit-YYYY-MM-DD-HHMM-gameplay-data.md. Use this section structure:
   - "# Gameplay Data Audit — YYYY-MM-DD HH:MM (${SAMPLE_DIR}, Phase-10 CLOSE, Wave-2 baseline)"
   - "## 1. Verdict" (CLEAN | MINOR_ISSUES | SIGNIFICANT_ISSUES + 2-3 paragraphs; state plainly: is
     the meeting layer LOAD-BEARING (R1)? does the baseline LAND-AS-IS or need a targeted retune, and
     which one? is Phase 10 ready to CLOSE?)
   - "## 2. Environment" (timestamp from \`date\`, audited HEAD from \`git log -1 --oneline\`, sample
     dir, games analyzed, mechanical vs judgment finding counts, refute rate)
   - "## 3. Confirmed bugs & rule violations" (mechanical findings first — labelled code-certain —
     then surviving correctness judgment findings; verifier-adjusted severity noted; the 10.14
     integrity invariant (no fake do_task advanced the win counter) verified here — a breach is the
     one thing that overrides land-as-is)
   - "## 4. The balance crater, the load-bearing verdict & the PREDICTED retune (headline)" — with
     COUNTS: (1) THE CRATER DECOMPOSITION — blend-without-deflect vs crew-overshoot, which dominates
     (the toolkit catch-rate vs the inform's 14-vs-+6), AND the tuning-vs-model-ceiling fork on
     deflection (fixable by 10.14 wiring vs a 9B ceiling — the retune-vs-reopen-model decider);
     (2) R1 LOAD-BEARING — eject-decided vs stopwatch wins, the 2nd-impostor survival-to-stopwatch
     rate, the plain verdict; (3) THE PREDICTED-RETUNE TABLE (the prescriptive deliverable) — render
     a table: candidate (soften-inform variants / stopwatch Δ / strengthen-deflection / the combined
     front) × {offline-predictable? · predicted impostor-win-rate · predicted R1 · R4/SKIP-bloc cost ·
     frozen-constant cost}, with the re-derivation arithmetic cited and the GENERATIVE candidate marked
     "needs a scratch micro-set, not a number"; rank and recommend; (4) CLEAN-WINS — R4 (wrong-ejection,
     inversions, unattributed) + firewall + the do_task integrity invariant + the cross-era trajectory
     (overshoot vs trend). End with ONE paragraph: land-as-is or retune, the single recommended move,
     and its PREDICTED rebalanced number.
   - "## 5. Pacing, the stopwatch & why ejection does not decide" (the stopwatch margin + the Δ→win-split
     curve REPORTED not tuned; the emergency channel at scale incl. 10.11.1 strips + 0 crashes;
     meeting-rich vs conversion-decisive-poor; the cross-era trajectory)
   - "## 6. Impostor blend-vs-deflect + the counterfactual retune detail" (the tuning-vs-model fork with
     reply-turn evidence; do_task landed / deflection cratered / cover-in-opening-vs-reply; the full
     per-candidate retune simulations behind the §4 table, with arithmetic; the 10.11.1 residual-
     fabrication rate + any v5/v7 artifact aggregates)
   - "## 6b. Narrative reads (what the aggregates flatten)" (lens F — the impostor win, a stopwatch
     win, and the most-interesting game narrated beat by beat; the one hidden dynamic per game; the
     spectator-experience / R7 read)
   - "## 6c. Altitude check: targeted retune vs structural (the new-angles verdict)" (lens G — is a
     Wave-2.5 retune SUFFICIENT to make the meeting layer load-bearing, or does the cross-era
     stopwatch-dominance call for a structural lever (win-condition balance, task structure, the
     deferred elimination gap, the model/heterogeneous-agents direction)? State the altitude verdict
     and what it implies for post-Phase-10)
   - "## 7. Metric & coverage notes" (the corrected_w2 baseline; any metric that would mislead a
     retune A/B; seed coverage; sentinel states)
   - "## 8. Improvement proposals / retune candidates" (one subsection each: proposed_id, title,
     finding ids, scope sketch with a reproduction citation, priority)
   - "## 9. Lens coverage notes" (per-lens what-was-examined)
   - "## 10. Phase-11 inputs" (the front-end rework inputs this close surfaces: the new data surfaces
     to visualize, deferred plumbing, the rubric_score interestingness baseline — see
     [[project_phase_11_frontend_rework]])

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
