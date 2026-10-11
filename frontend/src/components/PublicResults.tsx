import { useEffect, useState } from "react";
import { getPublicResults } from "../api/client";
import { ADOPTED_RULES, holdsAdoptedValue } from "../lib/adoptedRules";
import { fmt, PUBLIC_RESULTS_COPY as COPY, setOptionLabel } from "../lib/copy";
import { serializePlaybackParams, OMNISCIENT } from "../lib/playback";
import type { ExperimentConfigView, PublicCaseView, PublicResultsView as PublicResultsDTO, ReportProvenanceGroupView } from "../types/api";

/** A recorded config's settings, sorted by what the owner made of them. */
export interface RecordedSettings {
  /** The adopted rules the config holds, in plain words. */
  readonly adopted: readonly string[];
  /** Settings these recordings carry that are neither adopted nor experiments. */
  readonly setForRecordings: readonly string[];
  /** Every other setting off its default. */
  readonly experiments: readonly string[];
}

export function recordedSettings(config: ExperimentConfigView | null | undefined): RecordedSettings {
  if (!config) return { adopted: [], setForRecordings: [], experiments: [] };
  const adopted = ADOPTED_RULES.filter((rule) => holdsAdoptedValue(config, rule)).map((rule) => COPY.adoptedRules[rule.field]);
  const setForRecordings: string[] = [];
  if (config.vent_exit_policy === "look_and_wait") setForRecordings.push(COPY.ventExitWaits);
  // A missing or null cooldown is the map's own value; any recorded value is named.
  if (config.kill_cooldown_ticks != null) setForRecordings.push(fmt(config.kill_cooldown_ticks === 1 ? COPY.killCooldownOne : COPY.killCooldownMany, { ticks: String(config.kill_cooldown_ticks) }));
  // Recorded only at version 1; a missing or null key is the field off.
  if (config.route_lines_version === 1) setForRecordings.push(COPY.routeLines);
  const experiments: string[] = [];
  if (config.evidence_reasoning_version) experiments.push(fmt(COPY.evidenceReasoning, { version: String(config.evidence_reasoning_version) }));
  if (config.investigation_version) experiments.push(COPY.investigation);
  if (config.contextual_self_report_version) experiments.push(COPY.contextualSelfReport);
  if (config.public_account_version) experiments.push(COPY.publicAccount);
  if (config.attributed_testimony_version) experiments.push(COPY.attributedTestimony);
  if (config.crew_idle_policy !== "hub_wait" || (config.vent_exit_policy !== "target_distance" && config.vent_exit_policy !== "look_and_wait") || config.post_meeting_retarget || config.self_report || config.sabotage_threshold !== "six_sevenths") experiments.push(COPY.movementPolicies);
  if (config.redistribution_policy !== "lowest_id") experiments.push(COPY.roundRules);
  return { adopted, setForRecordings, experiments };
}

// An older payload may omit the factory kind; it reads as not recorded.
const FACTORY_LABELS = { custom: COPY.factoryCustom, experimental: COPY.factoryBuiltInWithSettings, scripted: COPY.factoryScripted, unrecorded: COPY.factoryUnknown } as const;

/**
 * The observation clock a group ran on: its recorded version, the standard
 * timing when the recorded settings show timed observations off, and unknown
 * only when the record cannot say.
 */
export function observationClock(group: ReportProvenanceGroupView): string {
  if (group.temporal_observation_version !== null) return fmt(COPY.clockVersion, { version: String(group.temporal_observation_version) });
  return group.substrate_flags?.temporal_observations === false ? COPY.clockStandard : COPY.unknown;
}

/**
 * What a group's absent policy stamp means: the built-in scripted policy
 * (`orchestrator/replay.py`), except under a custom factory, whose agents are
 * not the built-in ones and whose unstamped policy the record cannot name.
 */
export function absentPolicy(factory: ReportProvenanceGroupView["agent_factory_kind"]): string {
  return factory === "custom" ? COPY.unknown : COPY.defaultPolicy;
}

function BehaviorIdentity({ group }: { group: ReportProvenanceGroupView }) {
  const settings = recordedSettings(group.experiment_config);
  const factory = FACTORY_LABELS[group.agent_factory_kind ?? "unrecorded"];
  const count = group.game_ids.length;
  const nothingRecorded = settings.adopted.length === 0 && settings.setForRecordings.length === 0 && settings.experiments.length === 0;
  const unstamped = absentPolicy(group.agent_factory_kind);
  return <li className="rounded border border-ink-300 p-3">
    <p><strong>{factory}</strong> · {fmt(count === 1 ? COPY.recordingCountOne : COPY.recordingCountMany, { count: String(count) })}.</p>
    {settings.adopted.length > 0 && <p>{fmt(COPY.adoptedLead, { rules: settings.adopted.join(COPY.sentenceSeparator) })}</p>}
    {settings.setForRecordings.length > 0 && <p>{fmt(COPY.setForRecordingsLead, { settings: settings.setForRecordings.join(COPY.ruleSeparator) })}</p>}
    {settings.experiments.length > 0 && <p>{fmt(COPY.experimentsLead, { experiments: settings.experiments.join(COPY.experimentSeparator) })}</p>}
    {nothingRecorded && <p>{COPY.noRecordedSettings}</p>}
    <p>{fmt(COPY.policyLine, { impostor: group.tactical_policy?.method ?? unstamped, crew: group.crew_tactical_policy?.method ?? unstamped, rules: group.substrate_flags ? COPY.recorded : COPY.unknown })}</p>
    {/* Two groups can differ by the observation clock alone; without this line the
        mixed-configuration banner fires above cards that read identically. */}
    <p>{fmt(COPY.clockLine, { clock: observationClock(group) })}</p>
  </li>;
}

function CaseCard({ example, setName }: { example: PublicCaseView; setName: string }) {
  const [revealed, setRevealed] = useState(false);
  const href = serializePlaybackParams({ set: setName, gameId: example.game_id, tick: example.meeting_tick, perspective: OMNISCIENT, beliefView: "belief", selectedAgent: null, selectedMeeting: example.meeting_id, view: "workspace", reveal: false, evidence: { kind: example.observation_id !== null ? "observation" : "statement", id: example.observation_id ?? example.turn_id ?? "missing", meetingId: example.meeting_id, observerId: example.observer_id } });
  return <article className="flex flex-col gap-3 rounded-lg border-2 border-ink-900 bg-paper-0 p-4 shadow-chrome-1">
    <h3 className="text-lg">{example.title}</h3>
    <p className="text-sm leading-relaxed">{example.setup}</p>
    <a className="w-fit rounded border-2 border-ink-900 bg-ink-900 px-3 py-2 text-sm font-bold text-paper-0" href={href}>{COPY.inspectMeeting}</a>
    <button className="w-fit text-left text-sm underline" type="button" aria-expanded={revealed} onClick={() => setRevealed(!revealed)}>{revealed ? COPY.hideAnalysis : COPY.revealAnalysis}</button>
    {revealed && <p className="text-sm leading-relaxed">{example.explanation}</p>}
    <a className="text-xs underline" href={example.source_url} target="_blank" rel="noreferrer">{COPY.rawRecording}</a>
  </article>;
}

function Fraction({ n, d, plain = false }: { n: number; d: number; plain?: boolean }) {
  const text = `${n}/${d}${d > 0 ? ` (${Math.round(100 * n / d)}%)` : " (no eligible records)"}`;
  return plain ? <span className="font-mono">{text}</span> : <strong className="font-mono">{text}</strong>;
}

/**
 * Impostors among ejected players, split by whether a vent sighting named them:
 * a role read, so it sits after the cases in the page's body style and says why
 * its first half measures no deduction.
 */
function ProofRow({ results }: { results: PublicResultsDTO }) {
  const count = results.proof_free_ejections;
  return <section aria-label={COPY.proofHeading} data-proof-row className="space-y-2 text-sm">
    <h3 className="text-base">{COPY.proofHeading}</h3>
    <p>{COPY.proofWith} <Fraction plain n={results.proof_backed_correct} d={results.proof_backed_ejections} /> · {COPY.proofWithout} <Fraction plain n={results.proof_free_correct} d={results.proof_free_ejections} /></p>
    <p className="max-w-3xl text-xs leading-relaxed">{COPY.proofCaptionLead} {fmt(count === 1 ? COPY.proofCaptionOne : COPY.proofCaptionMany, { count: String(count) })} {COPY.proofCaptionTail}</p>
  </section>;
}

/** What the recorded usage cost: a zero is the flat-rate service, anything else keeps its figure. */
export function usageCost(cost: number): string {
  return cost === 0 ? COPY.costZero : fmt(COPY.costValue, { cost: `$${cost.toFixed(4)}` });
}

export function PublicResultsView({ results }: { results: PublicResultsDTO }) {
  return <section aria-label="Recorded results and cases" className="space-y-5 text-ink-900">
    <header>
      <h2 className="text-2xl">What the recordings show</h2>
      <p className="mt-2 max-w-3xl text-sm leading-relaxed">{fmt(COPY.intro, { games: String(results.games), set: setOptionLabel(results.set_name) })}</p>
      {(results.provenance_groups?.length ?? 0) > 1 && <p className="mt-2 text-sm font-bold">This set mixes recorded behavior configurations. Its totals are descriptive; inspect the groups below before comparing policies.</p>}
    </header>
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <div className="rounded-lg border border-ink-300 bg-paper-0 p-4">
        <h3 className="mb-2 text-base">Completed games</h3>
        <Fraction n={results.completed} d={results.games} />
        <p className="mt-2 text-xs">Verified endings / all recordings. {results.aborted} aborted · {results.tick_limited} tick limited · {results.unfinished} unfinished.</p>
      </div>
      <div className="rounded-lg border border-ink-300 bg-paper-0 p-4">
        <h3 className="mb-2 text-base">Crew wins</h3>
        <Fraction n={results.crew_wins} d={results.completed} />
        <p className="mt-2 text-xs">Crew victories / verified completed games. {results.impostor_wins} impostor wins; {results.task_wins} crew victories by tasks.</p>
      </div>
      <div className="rounded-lg border border-ink-300 bg-paper-0 p-4">
        <h3 className="mb-2 text-base">{COPY.ejectionsHeading}</h3>
        <Fraction n={results.impostor_ejections} d={results.ejections} />
        <p className="mt-2 text-xs">{fmt(COPY.ejectionsDescription, { meetings: String(results.meetings), innocent: String(results.innocent_ejections) })}</p>
      </div>
    </div>
    {results.cases.length > 0 ? <div>
      <h3 className="mb-3 text-xl">Decisions to investigate</h3>
      <div className="grid gap-4 lg:grid-cols-3">{results.cases.map((example) => <CaseCard key={example.case_id} example={example} setName={results.set_name} />)}</div>
    </div> : <p data-no-cases className="text-sm">{COPY.noCases}</p>}
    <ProofRow results={results} />
    <details className="rounded-lg border border-ink-300 bg-paper-0 p-4">
      <summary className="cursor-pointer text-sm font-bold">Recording provenance and reported usage</summary>
      <div className="mt-3 space-y-2 break-words text-xs">
        {results.provenance_groups?.length ? <ul className="space-y-2" aria-label="Recorded behavior groups">{results.provenance_groups.map((group, index) => <BehaviorIdentity key={index} group={group} />)}</ul> : <p>Behavior provenance is unavailable in this bundle; the agent factory and experiment settings are unknown.</p>}
        <p>Manifest recording dates: {results.recorded_from ?? "not recorded"}{results.recorded_until !== results.recorded_from ? ` – ${results.recorded_until ?? "not recorded"}` : ""}.</p>
        <p>Models: {results.models.join(", ") || "no model calls recorded"}.</p>
        <p>{fmt(COPY.usageLine, { input: results.input_tokens.toLocaleString(), output: results.output_tokens.toLocaleString(), cost: usageCost(results.reported_cost_usd) })}</p>
        <div data-technical-identifiers className="space-y-2">
          <p className="font-bold">{COPY.technicalHeading}</p>
          <p>{fmt(COPY.promptVersions, { versions: results.prompt_versions.join(", ") || COPY.promptVersionsNone })}</p>
          <p className="font-mono">{fmt(COPY.fingerprint, { fingerprint: results.source_fingerprint })}</p>{results.source_url && <a className="inline-block underline" href={results.source_url} target="_blank" rel="noreferrer">Inspect this pinned source set and manifest</a>}
        </div></div>
    </details>
  </section>;
}

export function PublicResults({ seedSet }: { seedSet: string | null }) {
  const [state, setState] = useState<{ results: PublicResultsDTO | null; error: boolean }>({ results: null, error: false });
  useEffect(() => {
    let cancelled = false;
    setState({ results: null, error: false });
    getPublicResults(seedSet ?? undefined).then((results) => { if (!cancelled) setState({ results, error: false }); }).catch(() => { if (!cancelled) setState({ results: null, error: true }); });
    return () => { cancelled = true; };
  }, [seedSet]);
  return state.results ? <PublicResultsView key={state.results.source_fingerprint} results={state.results} /> : <p role="status" className="rounded border border-ink-300 bg-paper-0 p-4 text-sm">{state.error ? "Verified public results are unavailable for this source. An older static bundle may not include them." : "Validating recorded results…"}</p>;
}
