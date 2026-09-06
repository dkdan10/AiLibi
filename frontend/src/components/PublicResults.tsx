import { useEffect, useState } from "react";
import { getPublicResults } from "../api/client";
import { serializePlaybackParams, OMNISCIENT } from "../lib/playback";
import type { PublicCaseView, PublicResultsView as PublicResultsDTO } from "../types/api";

function CaseCard({ example, setName }: { example: PublicCaseView; setName: string }) {
  const [revealed, setRevealed] = useState(false);
  const href = serializePlaybackParams({ set: setName, gameId: example.game_id, tick: example.meeting_tick, perspective: OMNISCIENT, beliefView: "belief", selectedAgent: null, selectedMeeting: example.meeting_id, view: "workspace", reveal: false, evidence: { kind: example.observation_id !== null ? "observation" : "statement", id: example.observation_id ?? example.turn_id ?? "missing", meetingId: example.meeting_id, observerId: example.observer_id } });
  return <article className="flex flex-col gap-3 rounded-lg border-2 border-ink-900 bg-paper-0 p-4 shadow-chrome-1">
    <h3 className="text-lg">{example.title}</h3>
    <p className="text-sm leading-relaxed">{example.setup}</p>
    <a className="w-fit rounded border-2 border-ink-900 bg-ink-900 px-3 py-2 text-sm font-bold text-paper-0" href={href}>Inspect the meeting</a>
    <button className="w-fit text-left text-sm underline" type="button" aria-expanded={revealed} onClick={() => setRevealed(!revealed)}>{revealed ? "Hide analysis" : "Reveal case analysis (spoilers)"}</button>
    {revealed && <p className="text-sm leading-relaxed">{example.explanation}</p>}
    <a className="text-xs underline" href={example.source_url} target="_blank" rel="noreferrer">Pinned recording source</a>
  </article>;
}

function Fraction({ n, d }: { n: number; d: number }) {
  return <strong className="font-mono">{n}/{d}{d > 0 ? ` (${Math.round(100 * n / d)}%)` : " (no eligible records)"}</strong>;
}

export function PublicResultsView({ results }: { results: PublicResultsDTO }) {
  return <section aria-label="Recorded results and cases" className="space-y-5 text-ink-900">
    <header>
      <h2 className="text-2xl">What the recordings show</h2>
      <p className="mt-2 max-w-3xl text-sm leading-relaxed">These are recorded games, not live AI responses. Results cover all {results.games} games in {results.set_name}; the replay browser may offer a smaller featured selection. The engine reconstructed each recording before these outcomes were counted.</p>
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
        <h3 className="mb-2 text-base">Correct ejections</h3>
        <Fraction n={results.impostor_ejections} d={results.ejections} />
        <p className="mt-2 text-xs">Impostors / all ejected players across {results.meetings} resolved meetings. {results.innocent_ejections} innocent ejections; skips are excluded.</p>
      </div>
    </div>
    <div className="rounded-lg border-2 border-ink-900 bg-paper-2 p-4">
      <h3 className="text-lg">Separate direct proof from uncertain inference</h3>
      <div className="my-3 flex flex-wrap gap-x-8 gap-y-2 text-sm">
        <p>With role proof: <Fraction n={results.proof_backed_correct} d={results.proof_backed_ejections} />
        </p>
        <p>Without role proof: <Fraction n={results.proof_free_correct} d={results.proof_free_ejections} />
        </p>
      </div>
      <p className="max-w-3xl text-xs leading-relaxed">Each fraction counts impostors among ejected players in that group. “Role proof” means the meeting contained a certified role-revealing observation about the ejectee, such as witnessed venting. Its presence does not prove it caused the vote. These groups describe this recording set; they are not a controlled comparison or a general measure of model reasoning.</p>
    </div>
    {results.cases.length > 0 ? <div>
      <h3 className="mb-3 text-xl">Three decisions to investigate</h3>
      <div className="grid gap-4 lg:grid-cols-3">{results.cases.map((example) => <CaseCard key={example.case_id} example={example} setName={results.set_name} />)}</div>
    </div> : <p className="text-sm">No source-matched editorial cases are published for this set.</p>}
    <details className="rounded-lg border border-ink-300 bg-paper-0 p-4">
      <summary className="cursor-pointer text-sm font-bold">Recording provenance and reported usage</summary>
      <div className="mt-3 space-y-2 break-words text-xs">
        <p>Manifest recording dates: {results.recorded_from ?? "not recorded"}{results.recorded_until !== results.recorded_from ? ` – ${results.recorded_until ?? "not recorded"}` : ""}.</p>
        <p>Models: {results.models.join(", ") || "no model calls recorded"}.</p>
        <p>Prompt versions: {results.prompt_versions.join(", ") || "not recorded"}.</p>
        <p>Reported call usage, including incomplete attempts: {results.input_tokens.toLocaleString()} input tokens · {results.output_tokens.toLocaleString()} output tokens · ${results.reported_cost_usd.toFixed(4)}. This is recorded usage, not a bill: a flat-rate adapter can report $0 and an interrupted call may lack provider usage. Outcome verification does not certify billing completeness.</p>
        <p className="font-mono">Source fingerprint: {results.source_fingerprint}</p>{results.source_url && <a className="inline-block underline" href={results.source_url} target="_blank" rel="noreferrer">Inspect this pinned source set and manifest</a>}</div>
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
