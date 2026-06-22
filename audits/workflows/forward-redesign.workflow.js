// Forward-Redesign Workflow.
//
// Ground-up redesign ANALYSIS of the AiLibi social-deduction game across the
// five fundamental issues an adversarial review surfaced (and the owner agreed
// with):
//   A — the vote is a deterministic gate the LLM merely transcribes
//   B — deception is mechanically impossible (no info-asymmetry, unpersuadable crew)
//   C — the social "soul" layer is frozen + mediocre (ML trains only the physical layer)
//   D — "interesting" can't be a fitness scalar (Goodhart; outcomes != persuasion/swing)
//   E — determinism-for-ML vs rich social deduction
//
// It is evidence-grounded (Phase 0 assembles real cited cases), prior-art-informed
// (Phase 0 surveys Werewolf/Cicero/generative-agents/multi-agent-RL via WebSearch),
// and de-risked (every option carries a real-case citation + a $0 validation sketch;
// C carries data-source + cost). It produces OPTIONS + RECOMMENDATIONS + a sequenced
// forward path — NOT draft task contracts (decision-support only).
//
// READ-ONLY (modeled on restructure-impact-map.workflow.js): lenses read/grep and
// never edit; only the final synthesis agent writes (the report markdown).
//
// Invoke from a Claude Code session (after review):
//   Workflow({scriptPath: "audits/workflows/forward-redesign.workflow.js"})
//
// Output: audits/audit-YYYY-MM-DD-HHMM-forward-redesign.md + the structured
// forward plan returned to the caller.

export const meta = {
  name: 'forward-redesign',
  description: 'Ground-up redesign analysis across the five fundamental issues (A vote-decides, B deception-craft, C unfreeze-social, D judge-not-fitness, E determinism-decomposition): per-group options + recommendations, a determinism verdict, an integrated architecture + interaction matrix, blindspots, and a recommended sequenced forward path. Evidence-grounded, prior-art-informed, decision-support.',
  whenToUse: 'When deciding how to make the social-deduction simulation fundamentally sound + interesting before committing the ML phase — to turn a diagnosis into evidence-grounded options + a recommended path.',
  phases: [
    { title: 'Ground', detail: 'Evidence (real cited cases) + Prior-art (cross-domain) packs the design phase reasons from' },
    { title: 'Design', detail: '4 parallel groups (A/B/C/D) each produce 2-3 options + a minimal baseline + a recommendation' },
    { title: 'Determinism', detail: 'Decompose engine-determinism vs the meeting gate; room for BOTH a strong social layer AND smart ML' },
    { title: 'Integrate', detail: 'Target architecture, A×E interaction matrix, minimal-vs-full scoping, sequencing' },
    { title: 'Stress-test', detail: 'Adversarial skeptics per recommendation + a blindspot agent' },
    { title: 'Synthesis', detail: 'Target state + roadmap reconciliation + recommended path; write the report' },
  ],
}

// ---------------------------------------------------------------------------
// Shared context (no literal backticks inside these template strings)
// ---------------------------------------------------------------------------

const CRITIQUES = `
AiLibi is an LLM-driven Among Us-style social-deduction game (cwd). A deterministic FSM engine runs
the physical game; a hand-coded (eventually ML) tactical policy drives per-tick actions; a FROZEN LLM
(qwen3.5:9b for the $0 eval / claude-sonnet-4-6 by default) acts ONLY in MEETINGS (deduction + deception).
The goal is an INTERESTING, MEASURABLE game, to eventually train ML tactical agents against the frozen
social layer.

An adversarial review identified FIVE fundamental issues (owner-agreed) that this workflow must turn into
an evidence-grounded forward plan:
- A — THE VOTE IS A DETERMINISTIC GATE THE LLM TRANSCRIBES. The §4.6 gate verdict is pre-computed in Jinja
  and handed to the model as "you MUST vote to eject / MUST skip"; the model complies ~97%; 64% of eject
  votes come from players who never accused. Reasoning has almost no causal path to the eject outcome.
- B — DECEPTION IS MECHANICALLY IMPOSSIBLE. The impostor's memory is poisoned ("you found the body here"),
  so a faithful reasoner self-incriminates (a frontier model is WORSE: 81% vs the 9B's 69%); the impostor
  has no tools to construct a false narrative; the crew's belief is a mechanical function of flags, not
  persuadable. A great liar is mechanically ~identical to a bad one.
- C — THE SOCIAL "SOUL" LAYER IS FROZEN + MEDIOCRE. "Interesting" lives in the meeting, but that layer is the
  frozen LLM; ML trains only the physical layer. The social game can never improve and is capped at a frozen
  9B that parrots prior speakers (~10% of turns) and confabulates (reasons time runs backwards).
- D — "INTERESTING" CAN'T BE A FITNESS SCALAR. Goodhart: the cleanest suspicion separator in the data is
  mechanical vent-visibility, so a naive optimizer learns visibility-avoidance. The rubric scores OUTCOMES
  (the shadow), not persuasion/swing (the substance, which lives in the language + the counterfactual space).
- E — DETERMINISM-FOR-ML vs RICH SOCIAL DEDUCTION. The constraints that make it a clean ML substrate are
  what hollow out the deduction.
`

const ANCHORS = `
Verified code anchors (cite these; never assert a site you did not locate):
- A (vote gate): pre-computed imperative in agents/strategic/prompts/vote_ballot.j2:131-149; deterministic
  tally meetings/manager.py::_tally:1674-1722 (confidence floor :1720-1722), mirror meetings/voting.py:120-213;
  the override redirect guard_ballot_target_graph manager.py:2315-2407 at call site :1662-1669; the suspicion
  graph _suspicion_graph_with_contradictions manager.py:1830-1942.
- B (deception + firewall): tactical agents/tactical/impostor_policy.py (_scored_targets:937-1009,
  _cover_or_vent:1011, fake-task _idle:1216-1253, _sabotage:1194); the 4-layer fellow-impostor firewall —
  observation observation/service.py:210-227, memory agents/memory/store.py:593-627, turn-claim guard
  manager.py::_guard_teammate_turn_claims:1216-1225, ballot coerce_teammate_ballot_to_skip:2280-2312; prompts
  agents/strategic/prompts/impostor_report.j2 + accusation_round.j2 (cover/deflection directives).
- C (frozen/trainable seam): AgentFactory orchestrator/game.py:91, TacticalAgent.decide:1783; the frozen LLM
  via MeetingRunner game.py:315-340 -> complete() at manager.py:1166 (turns) / :1554 (ballots);
  llm/provider.py:28 DEFAULT_MEETING_MODEL = claude-sonnet-4-6.
- D (rubric): experiments/lab/report-rubric-design.md (proposed D1-D4 geomean), experiments/lab/rubric_score.py:528
  (current additive R1-R7 sum).
- E (determinism): state-hash orchestrator/replay.py:648, seeded RNG engine/rng.py, replay-walk verify
  api/replay_loader.py:716, scripts/verify_samples.sh; dependents = the ML $0 loop, the spectator replay, the
  firewall leak test eval/leak_test.py, and the regression/era-pin baselines.
`

const REFRAME = `
KEY REFRAME the workflow must establish rigorously (do NOT just assume the original adversarial framing
"determinism cripples the game" is fully correct): ENGINE-determinism (state-hash / seeded RNG / replay-walk
verification — required by the ML $0 loop, the spectator replay, the firewall leak test, and the regression
era-pins) and the MEETING §4.6 GATE (an anti-cascade DESIGN CHOICE) are SEPARABLE. The social layer is ALREADY
recorded-not-deterministic (the LLM outputs are journaled; the gate is applied to the recorded claims/ballots).
So A-D operate on the recorded social layer and are LARGELY COMPATIBLE with keeping engine determinism. Test
this; quantify it; do not overstate the tension.
`

const OWNER_DECISIONS = `
Owner decisions framing this analysis: the OUTPUT is DECISION-SUPPORT (options + a recommended path; NOT draft
task contracts). The in-flight REDISTRIBUTE (task 13.10: a dead crewmate's unfinished tasks are re-keyed to a
living crewmate instead of dropped — the physical lever that breaks the "stopwatch") is KEPT. The RE-RECORD
(13.12) is HELD until the A/B social fixes land, so the new baseline captures meetings that actually decide.
The recommended sequenced path must respect both.
`

// ---------------------------------------------------------------------------
// Schemas
// ---------------------------------------------------------------------------

const OPTION = {
  type: 'object',
  properties: {
    name: { type: 'string' },
    mechanism: { type: 'string', description: 'How it works, concretely' },
    changed_loci: { type: 'array', items: { type: 'string' }, description: 'file:line sites it would touch' },
    real_case: { type: 'string', description: 'A specific real game/meeting from the evidence pack where the problem manifests AND where this fix would change the outcome (cite seed N meeting M, file:line, or a metric)' },
    validation_sketch: { type: 'string', description: 'The $0/cheap fake-sim or one-smoke that confirms it works BEFORE committing' },
    data_source: { type: 'string', description: 'For C only: where labeled training data comes from (committed replays / synthetic self-play / human-rated). Otherwise "n/a".' },
    pros: { type: 'array', items: { type: 'string' } },
    cons: { type: 'array', items: { type: 'string' } },
    cost: { type: 'string', description: 'Effort + $ + compute (for C give GPU-hours / $ / #examples / wall-clock)' },
    risk: { type: 'string', enum: ['high', 'medium', 'low'] },
    determinism_firewall_impact: { type: 'string', description: 'Whether it touches engine determinism or the 4-layer firewall, and how' },
  },
  required: ['name', 'mechanism', 'real_case', 'validation_sketch', 'pros', 'cons', 'cost', 'risk', 'determinism_firewall_impact'],
}

const GROUP_OPTIONS = {
  type: 'object',
  properties: {
    group: { type: 'string', description: 'A / B / C / D' },
    goal: { type: 'string' },
    independent_view: { type: 'string', description: 'Your own ground-up framing of this problem before the options' },
    options: { type: 'array', items: OPTION, description: '2-3 real options' },
    minimal_baseline: { ...OPTION, description: 'The cheapest/skeptical do-little option (is this even necessary?) in the same OPTION shape' },
    recommendation: {
      type: 'object',
      properties: { choice: { type: 'string' }, why: { type: 'string' } },
      required: ['choice', 'why'],
    },
    blindspots: { type: 'array', items: { type: 'string' } },
  },
  required: ['group', 'goal', 'options', 'minimal_baseline', 'recommendation'],
}

const EVIDENCE_PACK = {
  type: 'object',
  properties: {
    cases: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          area: { type: 'string', description: 'which critique it grounds: A/B/C/D/E' },
          title: { type: 'string' },
          locus: { type: 'string', description: 'seed N meeting M / file:line / metric' },
          what_happened: { type: 'string' },
          why_it_matters: { type: 'string' },
        },
        required: ['area', 'title', 'locus', 'what_happened'],
      },
    },
    summary: { type: 'string' },
  },
  required: ['cases', 'summary'],
}

const PRIOR_ART = {
  type: 'object',
  properties: {
    systems: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          domain: { type: 'string' },
          technique: { type: 'string', description: 'how it handles deduction / deception / belief / persuasion / co-evolution' },
          what_to_borrow: { type: 'string', description: 'the specific transferable idea for AiLibi' },
          relevance: { type: 'string', enum: ['A', 'B', 'C', 'D', 'E', 'general'] },
          citation: { type: 'string' },
        },
        required: ['name', 'technique', 'what_to_borrow', 'relevance'],
      },
    },
    summary: { type: 'string' },
  },
  required: ['systems', 'summary'],
}

const DETERMINISM_VERDICT = {
  type: 'object',
  properties: {
    engine_determinism_requires: { type: 'array', items: { type: 'string' }, description: 'what genuinely depends on byte-determinism, each with its anchor' },
    gate_is_a_choice: { type: 'boolean', description: 'is the §4.6 meeting gate an anti-cascade choice separable from engine determinism?' },
    per_option_impact: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          option: { type: 'string' },
          breaks_engine_determinism: { type: 'string', enum: ['no', 'partly', 'yes'] },
          note: { type: 'string' },
        },
        required: ['option', 'breaks_engine_determinism', 'note'],
      },
    },
    pure_determinism_still_needed: { type: 'string', description: 'is PURE determinism still necessary after the new features land — the verdict' },
    room_for_both: { type: 'string', description: 'is there room for BOTH a strong social layer AND smart ML agents, and how' },
    spectator_ui_impact: { type: 'string' },
    recommendation: { type: 'string' },
  },
  required: ['engine_determinism_requires', 'gate_is_a_choice', 'pure_determinism_still_needed', 'room_for_both', 'recommendation'],
}

const INTEGRATION = {
  type: 'object',
  properties: {
    target_architecture: { type: 'string', description: 'the coherent end-state the recommendations imply together' },
    dependency_graph: {
      type: 'array',
      items: {
        type: 'object',
        properties: { from: { type: 'string' }, to: { type: 'string' }, why: { type: 'string' } },
        required: ['from', 'to', 'why'],
      },
    },
    interaction_matrix: {
      type: 'array',
      description: 'over the pairs A×B A×C A×D A×E B×C B×D B×E C×D C×E D×E',
      items: {
        type: 'object',
        properties: {
          pair: { type: 'string' },
          interaction: { type: 'string' },
          kind: { type: 'string', enum: ['synergy', 'conflict', 'neutral'] },
        },
        required: ['pair', 'interaction', 'kind'],
      },
    },
    minimal_vs_full: {
      type: 'object',
      properties: {
        minimal_fix: { type: 'string', description: 'the SMALLEST change that makes the game fundamentally sound' },
        full_redesign: { type: 'string' },
        recommendation: { type: 'string' },
      },
      required: ['minimal_fix', 'full_redesign', 'recommendation'],
    },
    sequencing: { type: 'array', items: { type: 'string' } },
  },
  required: ['target_architecture', 'interaction_matrix', 'minimal_vs_full', 'sequencing'],
}

const VERDICT = {
  type: 'object',
  properties: {
    target: { type: 'string', description: 'which group recommendation (A/B/C/D/E)' },
    holds: { type: 'string', enum: ['yes', 'partly', 'no'] },
    hidden_costs: { type: 'array', items: { type: 'string' } },
    conflicts: { type: 'array', items: { type: 'string' }, description: 'conflicts with other groups / the firewall / engine determinism' },
    note: { type: 'string' },
  },
  required: ['target', 'holds', 'note'],
}

const BLINDSPOT = {
  type: 'object',
  properties: {
    blindspots: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          description: { type: 'string' },
          severity: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
        required: ['title', 'description'],
      },
    },
    cross_domain_ideas: { type: 'array', items: { type: 'string' } },
    overreach_check: { type: 'string', description: 'is the whole redesign over-reaching / solving the wrong problem?' },
    summary: { type: 'string' },
  },
  required: ['blindspots', 'summary'],
}

const SYNTHESIS_SCHEMA = {
  type: 'object',
  properties: {
    target_state: { type: 'string', description: 'a MEASURABLE definition of "fundamentally sound + interesting"' },
    recommended_path: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          step: { type: 'string' },
          what: { type: 'string' },
          effort: { type: 'string' },
          depends_on: { type: 'string' },
        },
        required: ['step', 'what'],
      },
    },
    minimal_vs_full_recommendation: { type: 'string' },
    roadmap_reconciliation: { type: 'string', description: 'how this integrates the deferred memory items (b1=27 testimony-ingestion, BotC misinformation, two-phase reasoning, the ML/Phase-C plan)' },
    open_owner_decisions: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string', description: 'the written report path + one-paragraph outcome' },
    report_markdown: { type: 'string', description: 'the full report body for audits/, sections per the synthesis prompt' },
  },
  required: ['target_state', 'recommended_path', 'minimal_vs_full_recommendation', 'roadmap_reconciliation', 'open_owner_decisions', 'summary', 'report_markdown'],
}

// ---------------------------------------------------------------------------
// Phase 0: Ground (Evidence + Prior-art, parallel)
// ---------------------------------------------------------------------------

phase('Ground')
log('Assembling the evidence pack (real cases) + the prior-art pack (cross-domain) in parallel.')

const groundResults = await parallel([
  () =>
    agent(
      `You are the EVIDENCE phase of a forward-redesign analysis of the AiLibi social-deduction game (cwd).
${CRITIQUES}

Assemble a pack of SPECIFIC, real, cited cases the design phase will reason from — so options are grounded in
data, not abstraction. Sources (READ-ONLY): the committed replays replays/samples/9p2i/replay-seed-*.jsonl (meeting
rows carry llm_calls with the actual prompt + response_text, transcript turns, contradictions, ballots; roles in
replays/samples/9p2i/tournament-eval-report.json); the prior diagnostic audits/audit-2026-06-22-0446-ground-up.md
(re-use AND verify its cited cases against the raw data). The committed extractor audits/workflows/extract_gameplay_facts.py
may be run for facts (PYTHONPATH=. uv run python audits/workflows/extract_gameplay_facts.py) but the raw replays are
sufficient.

Find concrete cases for EACH area:
- A: a meeting where the §4.6 gate / guard_ballot_target_graph changed or overrode the LLM's intended vote (e.g. the
  seed-16 stale-prior override of a fresh eyewitness catch); a meeting where 64%-of-ejects-from-non-accusers shows.
- B: an impostor alibi that SURVIVED vs one that FAILED; a case proving deception was luck (alibi happened not to clash)
  not skill; the poisoned-memory self-incrimination.
- C: a transcript turn showing the model parroting/confabulating; a case where STRONGER reasoning would self-incriminate.
- D: a game the current rubric would mis-rank; a genuinely contested/swing meeting vs a flat one.
- E: the seed-49 two-1.00-sightings loss; the 16 vote-split SKIPs; the ~10% echoed/contaminated turns.
For each: area, a title, the locus (seed N meeting M / file:line / metric), what happened, why it matters. Cite real
loci — do not invent. Return the structured evidence pack.`,
      { label: 'ground:evidence', phase: 'Ground', schema: EVIDENCE_PACK }
    ),
  () =>
    agent(
      `You are the PRIOR-ART phase of a forward-redesign of the AiLibi social-deduction game.
${CRITIQUES}

Use WebSearch (load it via ToolSearch with query "select:WebSearch" if its schema is not loaded) to survey how OTHER
systems solve the problems AiLibi faces — so the design phase stands on proven approaches, not first principles. Research,
with citations: (1) LLM social-deduction agents — Werewolf / Mafia / Avalon LLM papers (belief modeling, persuasion,
deception, making the vote meaningful); (2) Meta CICERO (Diplomacy) — belief/intent modeling + grounded dialogue + how it
couples a planning layer with a language layer (directly relevant to A/B/C); (3) generative-agents / believable-agent
memory + belief architectures; (4) multi-agent RL co-evolution + self-play — how to co-train without collapse (AiLibi already
observed naive 2-pop co-evolution collapse, so this is load-bearing for C); (5) RLHF / fine-tuning SMALL models for
reasoning or deception, and the data requirements. For EACH system: name, domain, the technique, the SPECIFIC transferable
idea for AiLibi (tagged A/B/C/D/E), and a citation. Be concrete. Return the structured prior-art pack.`,
      { label: 'ground:prior-art', phase: 'Ground', schema: PRIOR_ART }
    ),
])

const evidence = groundResults[0] || { cases: [], summary: '(evidence pack unavailable)' }
const priorArt = groundResults[1] || { systems: [], summary: '(prior-art pack unavailable)' }
log(`Ground complete: ${evidence.cases.length} evidence cases, ${priorArt.systems.length} prior-art systems.`)

// ---------------------------------------------------------------------------
// Shared design preamble (injects evidence + prior-art)
// ---------------------------------------------------------------------------

const preamble = (ev, pa) => `You are one of 4 parallel ground-up DESIGN analysts for the AiLibi social-deduction game (cwd).
The owner agrees the game has five fundamental issues and wants, for YOUR assigned issue, 2-3 concrete OPTIONS + a
recommendation that are evidence-grounded and de-risked.

${CRITIQUES}
${ANCHORS}
${REFRAME}
${OWNER_DECISIONS}

EVIDENCE PACK (real cited cases — every option MUST cite at least one real case from here where the problem manifests AND
where your fix would change the outcome):
${JSON.stringify(ev, null, 1)}

PRIOR-ART PACK (proven approaches from other systems — reference these, especially for B and C):
${JSON.stringify(pa, null, 1)}

Produce for your group: an independent_view (your own ground-up framing); 2-3 options PLUS a minimal/skeptical baseline
option (is this even necessary?), each option with mechanism, changed_loci (file:line), a real_case citation (from the
evidence pack), a $0/cheap validation_sketch (this project validates PHYSICAL levers with a fake-provider sweep and SOCIAL
levers with a small real-LLM smoke), pros/cons, cost, risk, and determinism_firewall_impact; then a recommendation
(which option + why) and blindspots. Method: read the anchors + the relevant code (read-only grep/Read); do NOT edit;
do NOT invent a locus you did not locate.

Your group-specific scope:
`

// ---------------------------------------------------------------------------
// Phase 1: Design (4 parallel groups A/B/C/D)
// ---------------------------------------------------------------------------

phase('Design')

const GROUPS = [
  {
    key: 'A',
    name: 'Let the vote decide',
    scope: `GROUP A — make the LLM's reasoning actually DECIDE the ejection instead of transcribing a pre-computed gate. Today
the gate (vote_ballot.j2:131-149) hands the model a MUST-vote/MUST-skip imperative; the tally (_tally manager.py:1674-1722)
and the redirect (guard_ballot_target_graph:2315-2407 at :1662-1669) override the model. Design options to let the LLM vote from
its own belief — e.g. a non-binding recommendation; a deliberation/discussion round then a free vote; a self-applied
confidence/evidence bar replacing the deterministic floor — WHILE preserving the teammate firewall (coerce_teammate_ballot_to_skip)
and the recorded-ballot replay (so ENGINE determinism is untouched; cite the REFRAME). Crucially, address WHY the gate exists
(anti-cascade / railroad prevention, an owner principle: innocents are ejectable but not at RANDOM) and what replaces that
protection. Cite the A evidence cases.`,
  },
  {
    key: 'B',
    name: 'Make deception a craft',
    scope: `GROUP B — make deception a SKILL that can be exercised, via information SYMMETRY + a persuadable crew belief +
impostor narrative tools. Today the impostor's memory is poisoned, it has no narrative tools, and the crew's belief is a
mechanical flag-delta (not persuadable). Draw on the prior-art pack (Werewolf/Cicero/belief-modeling). Options might: give
impostors legit tasks near bodies / ambiguous sightings / a self-report tool / an in-firewall coordination SIGNAL so a grounded
alibi is SOMETIMES innocent; and/or make a listener's belief update from ARGUMENTS (the LLM weighing whom to believe) not just
structured-claim flag-deltas. You MUST respect the 4-layer firewall (never leak teammate identity — cite the anchors). Cite the
B evidence cases.`,
  },
  {
    key: 'C',
    name: 'Unfreeze the soul',
    scope: `GROUP C — let the social/deduction agency IMPROVE (today it is a frozen, mediocre LLM; ML trains only the physical
layer). The owner is a model-tuning NOVICE, so give multiple paths, EACH with its DATA SOURCE (where labeled deduction/deception
training data comes from — the committed replays? synthetic self-play? human-rated?) and CONCRETE cost/effort (GPU-hours, $,
#examples, wall-clock): (1) a stronger frozen model (claude-sonnet-4-6 is already wired at llm/provider.py:28); (2) fine-tune the
open model (SFT / LoRA / RL) on deduction+deception; (3) co-train a LEARNED social policy (the FO-6 physical-suspicion-rank -> a
learned vote/accuse prior) alongside the frozen prose, at the AgentFactory/MeetingRunner seam (game.py:91 / :315-340); (4) a
hybrid. Use the prior-art pack (Cicero, multi-agent-RL self-play, small-model RLHF). FLAG the co-evolution-collapse risk the
project already observed. Give novice-friendly guidance + a recommendation. Cite the C evidence cases.`,
  },
  {
    key: 'D',
    name: 'Judge, not fitness',
    scope: `GROUP D — measure/cultivate "interesting" without Goodharting it (today the rubric is an additive R1-R7 scalar
rubric_score.py:528 measuring outcomes, not persuasion/swing). Options: rubric-as-FILTER (surface interesting games for a
human/judge, not a gradient target); an LLM-judge of interestingness; human-in-the-loop curation; a truth-shadow oracle for
MEASUREMENT (kept OUT of the play path to preserve the firewall — to score detector precision/recall and tell a real lie from a
confabulation); an explicit SWING axis (did the eject-plurality leader change across turns / could the deciding ballot have
flipped). Relate to the proposed D1-D4 geomean (report-rubric-design.md). Be explicit which options serve ML-FITNESS vs
human-CURATION. Cite the D evidence cases.`,
  },
]

const designResults = await parallel(
  GROUPS.map((g) => () =>
    agent(
      preamble(evidence, priorArt) + `\nGroup ${g.key} — ${g.name}\n\n${g.scope}\n\nReturn a structured map with group="${g.key}".`,
      { label: `design:${g.key}-${g.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 24)}`, phase: 'Design', schema: GROUP_OPTIONS, effort: 'high' }
    )
  )
)

const designs = designResults.filter(Boolean)
log(`Design complete: ${designs.length}/4 groups.`)

const recsBrief = (d) => ({ group: d.group, goal: d.goal, recommendation: d.recommendation })

// ---------------------------------------------------------------------------
// Phase 2: Determinism (E) — consumes the A-D options
// ---------------------------------------------------------------------------

phase('Determinism')

const determinism = await agent(
  `You are the DETERMINISM (E) analyst for the AiLibi forward-redesign.
${CRITIQUES}
${ANCHORS}
${REFRAME}

The four design groups produced these options (focus on each option's determinism_firewall_impact + the recommendations):
${JSON.stringify(
    designs.map((d) => ({
      group: d.group,
      options: (d.options || []).map((o) => ({ name: o.name, determinism_firewall_impact: o.determinism_firewall_impact })),
      recommendation: d.recommendation,
    })),
    null,
    1
  )}

Rigorously answer the owner's core E question. Decompose what EXACTLY requires byte-determinism (cite the dependents — the ML
$0 loop, the spectator replay api/replay_loader.py:716, the firewall leak test eval/leak_test.py, the regression/era-pins) vs
what is the §4.6 meeting GATE (an anti-cascade choice). For EACH design recommendation above, judge whether it breaks ENGINE
determinism (no/partly/yes) — remembering the social layer is recorded-not-deterministic. Then answer: is PURE determinism
still necessary after the new features land? Is there room for BOTH a strong social layer AND smart ML agents, and HOW (e.g.
engine stays byte-deterministic, the meeting stays recorded, ML trains on recorded actions + a surrogate)? Include the
spectator / Phase-12-UI implications (a loosened gate changes replay rendering; impostor role-leak rationales surface in the
mind-inspector). Read-only; cite anchors. Return the structured verdict.`,
  { label: 'determinism:E', phase: 'Determinism', schema: DETERMINISM_VERDICT, effort: 'high' }
)
log('Determinism verdict ready.')

// ---------------------------------------------------------------------------
// Phase 3: Integrate — architecture, interaction matrix, minimal-vs-full
// ---------------------------------------------------------------------------

phase('Integrate')

const integration = await agent(
  `You are the INTEGRATION analyst for the AiLibi forward-redesign. You have the 4 group designs (A-D) and the determinism (E)
verdict. Produce the coherent picture.
${OWNER_DECISIONS}

GROUP RECOMMENDATIONS:
${JSON.stringify(designs.map(recsBrief), null, 1)}

DETERMINISM VERDICT:
${JSON.stringify(determinism, null, 1)}

Produce: (1) target_architecture the recommendations imply together; (2) a dependency_graph (does A enable B? does B need A's
persuadable vote? does C need D's judge as a selection gate?); (3) an explicit interaction_matrix over the pairs A×B A×C A×D
A×E B×C B×D B×E C×D C×E D×E, each marked synergy/conflict/neutral with a one-line interaction; (4) minimal_vs_full — the SMALLEST
change that makes the game fundamentally sound (consider: just close the testimony->belief loop per the prior audit) vs the full
A-E redesign, with a recommendation; (5) a sequencing of steps respecting redistribute-kept + re-record-held-until-A/B. Return
the structured integration.`,
  { label: 'integrate', phase: 'Integrate', schema: INTEGRATION, effort: 'high' }
)
log('Integration ready.')

// ---------------------------------------------------------------------------
// Phase 4: Stress-test (skeptics per recommendation + a blindspot agent)
// ---------------------------------------------------------------------------

phase('Stress-test')

const stressTargets = [
  ...designs.map((d) => ({ key: d.group, rec: d.recommendation })),
  { key: 'E', rec: { choice: determinism.recommendation, why: determinism.pure_determinism_still_needed } },
]

const stress = await parallel([
  ...stressTargets.map((t) => () =>
    agent(
      `You are an adversarial skeptic for the AiLibi forward-redesign. A design group (${t.key}) recommended:
${JSON.stringify(t.rec, null, 1)}

Stress-test it against the code + the real game data (read-only grep/Read). Does it actually WORK mechanically? Hidden costs?
Does it CONFLICT with another group's direction, the 4-layer firewall, or engine determinism? Default to skepticism; flag
anything not concretely grounded. Output the verdict with target="${t.key}".`,
      { label: `stress:${t.key}`, phase: 'Stress-test', schema: VERDICT, effort: 'low' }
    )
  ),
  () =>
    agent(
      `You are the BLINDSPOT analyst for the AiLibi forward-redesign — find what the owner and the design groups are likely MISSING.
${CRITIQUES}

The designs + determinism + integration so far:
${JSON.stringify({ designs: designs.map(recsBrief), determinism: determinism.recommendation, integration: integration.target_architecture, minimal_vs_full: integration.minimal_vs_full }, null, 1)}

Surface: second-order effects, failure modes, cross-domain ideas (social-deduction game design, multi-agent RL, LLM-agent
research) that NONE of the groups raised, and an honest overreach check (is the whole redesign solving the wrong problem / too
ambitious vs a targeted fix). Be specific. Return the structured blindspot result.`,
      { label: 'stress:blindspot', phase: 'Stress-test', schema: BLINDSPOT, effort: 'low' }
    ),
])

const verdicts = stress.slice(0, stressTargets.length).filter(Boolean)
const blindspot = stress[stressTargets.length] || { blindspots: [], summary: '(blindspot pass unavailable)' }
log(`Stress-test complete: ${verdicts.length} verdicts, ${blindspot.blindspots.length} blindspots.`)

// ---------------------------------------------------------------------------
// Phase 5: Synthesis (write the forward-plan report)
// ---------------------------------------------------------------------------

phase('Synthesis')

const synthInput = {
  designs,
  determinism,
  integration,
  verdicts,
  blindspot,
  evidence_summary: evidence.summary,
  prior_art_summary: priorArt.summary,
}

const synthesis = await agent(
  `You are synthesizing the FORWARD-REDESIGN plan for the AiLibi social-deduction game. Four group designs (A-D), a determinism
verdict (E), an integration pass, adversarial skeptics, and a blindspot pass are below. Produce the owner's decision-support
document. Weight recommendations by the skeptics' verdicts (discount 'no'/'partly'); foreground 'yes'.
${OWNER_DECISIONS}

INPUT (JSON):
${JSON.stringify(synthInput, null, 1)}

Produce TWO things:
1. Structured output: target_state (a MEASURABLE definition of "fundamentally sound + interesting" — concrete numbers, e.g.
   eject-decided share, swing rate, deception-success-that-is-skill-not-luck); recommended_path (sequenced steps with effort +
   depends_on, respecting redistribute-kept + re-record-held-until-A/B); minimal_vs_full_recommendation; roadmap_reconciliation
   (how this integrates the deferred memory items: b1=27 testimony-ingestion, BotC-style crew misinformation, two-phase reasoning,
   the ML/Phase-C plan — integrate, don't orphan); open_owner_decisions; summary.
2. report_markdown: the full report body for audits/, with these sections:
   - "# Forward-Redesign — AiLibi (LLM-driven Among Us)" then bold Date / Method / Headline lines
   - "## 1. The target state (measurable)"
   - "## 2. Group A — let the vote decide" (goal; options each with real-case + validation + cost; recommendation; minimal baseline)
   - "## 3. Group B — make deception a craft"
   - "## 4. Group C — unfreeze the soul" (each path with its data-source + concrete cost)
   - "## 5. Group D — judge, not fitness"
   - "## 6. Determinism verdict (E)" (engine-determinism vs the meeting gate; room for both; spectator impact)
   - "## 7. Integrated architecture + A×E interaction matrix"
   - "## 8. Minimal-viable fix vs full redesign"
   - "## 9. Roadmap reconciliation"
   - "## 10. Blindspots"
   - "## 11. Recommended sequenced path" (effort/cost per step; redistribute kept, re-record HELD until A/B land)
   - "## 12. Open owner decisions"

Then write the report to disk in THIS EXACT ORDER (do NOT reorder; do NOT hardcode or guess a date):
- Step 1: run  date '+%Y-%m-%d-%H%M'  via the Bash tool and CAPTURE its stdout.
- Step 2: compute path = audits/audit-{captured-stdout}-forward-redesign.md
- Step 3: use the Write tool to write report_markdown to that path.
Report the final written path in the summary field.`,
  { label: 'synthesize', phase: 'Synthesis', schema: SYNTHESIS_SCHEMA, effort: 'high' }
)

log(`Synthesis complete. ${synthesis.recommended_path.length} path steps, ${synthesis.open_owner_decisions.length} open decisions.`)

return {
  target_state: synthesis.target_state,
  recommended_path: synthesis.recommended_path,
  minimal_vs_full: synthesis.minimal_vs_full_recommendation,
  roadmap_reconciliation: synthesis.roadmap_reconciliation,
  open_owner_decisions: synthesis.open_owner_decisions,
  summary: synthesis.summary,
  tokens_spent: budget.spent(),
}
