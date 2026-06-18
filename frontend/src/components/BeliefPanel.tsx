// BeliefPanel — the presentational chrome of the Belief × Truth hero
// (design/phase-12/stage-1-design.md §3.3, slice 4; the committed
// 04-matrix-{belief,ground-truth,error}.png renders; the Claude-Design handoff).
// PURE: it takes the roster + the per-meeting `BeliefFrameView` snapshots + the
// active layer and renders the matrix, the segmented toggle, the per-meeting step
// control, the layer legend, and the cell-detail (cross-meeting trajectory +
// "what changed this meeting" diff). It fetches nothing — BeliefMatrix wires it
// to the store — so Storybook can drive every state from props.
//
// Firewall (binding, enforced HERE):
//   • the ground-truth impostor reveal is a header DAGGER (an icon, never a hue)
//     and is Omniscient-only — suppressed in fog;
//   • Ground-Truth and Error are role-derived, so in fog the panel forces the
//     Belief layer and disables those toggle options (no role leak);
//   • Error reads by shape + glyph (✕ / ◆) + a LOUD ring, never hue alone;
//   • "no belief yet" is a distinct hatched cell, never painted as 0.

import { useState } from "react";
import type { CSSProperties, ReactNode } from "react";

import { tokens } from "../tokens";
import type { BeliefViewMode } from "../lib/playback";
import type { BeliefErrorView, BeliefFrameView, PlayerView } from "../types/api";
import { BeliefRow } from "./BeliefRow";
import type { BeliefCellModel } from "./BeliefCell";

// Matrix geometry (px) — shared so the header row, body rows, and the footer line
// up. Kept calm/dense per the brief's density rule (borrow restraint for data).
const CELL = 38;
const ROW_HEADER_W = 42;
const COL_HEADER_H = 44;

const LAYERS: ReadonlyArray<{ id: BeliefViewMode; label: string }> = [
  { id: "belief", label: "Belief" },
  { id: "truth", label: "Ground-truth" },
  { id: "error", label: "Error" },
];

interface BeliefPanelProps {
  players: PlayerView[];
  frames: BeliefFrameView[];
  layer: BeliefViewMode;
  onLayerChange: (layer: BeliefViewMode) => void;
  omniscient: boolean;
  // Per-meeting liveness, keyed by meeting_id → alive agent ids, derived from the
  // replay's tick state (NOT from belief-row presence: the /beliefs DTO snapshots
  // every player as an observer at every meeting, dead included). Absent ⇒ treat
  // all as alive (no freezing).
  aliveByMeeting?: Readonly<Record<string, readonly string[]>>;
  // Overlay chrome (BeliefMatrix passes these; the isolated story omits them).
  loading?: boolean;
  error?: string | null;
  onClose?: () => void;
  isFullscreen?: boolean;
  onToggleFullscreen?: () => void;
}

export function BeliefPanel({
  players,
  frames,
  layer,
  onLayerChange,
  omniscient,
  aliveByMeeting,
  loading = false,
  error = null,
  onClose,
  isFullscreen = false,
  onToggleFullscreen,
}: BeliefPanelProps) {
  // Default to the most recent meeting (the "after" state); the step control
  // walks backward to "before". Clamped against the live frame count.
  const [stepIndex, setStepIndex] = useState<number>(Number.MAX_SAFE_INTEGER);
  const [selected, setSelected] = useState<{ observer: string; subject: string } | null>(null);

  const total = frames.length;
  const clampedStep = total === 0 ? 0 : Math.min(Math.max(stepIndex, 0), total - 1);
  const activeFrame: BeliefFrameView | undefined = frames[clampedStep];

  // Fog forces Belief (Truth/Error are role-derived → would leak).
  const effectiveLayer: BeliefViewMode = omniscient ? layer : "belief";

  const n = players.length;
  const impostorIds = new Set(
    players.filter((p) => p.role === "IMPOSTOR").map((p) => p.agent_id),
  );

  // Liveness comes from the replay's per-meeting tick state (passed in), NOT from
  // belief-row presence: the /beliefs DTO snapshots EVERY player as an observer at
  // every meeting (a dead agent's beliefs are frozen at death), so row presence
  // can't distinguish alive from dead. Without the tick-derived alive set a dead
  // player's row/column would render active instead of the frozen state the legend
  // advertises. Absent liveness ⇒ treat all as alive (degrade to no freezing).
  const aliveList = activeFrame ? aliveByMeeting?.[activeFrame.meeting_id] : undefined;
  const aliveSet =
    aliveList !== undefined ? new Set(aliveList) : new Set(players.map((p) => p.agent_id));

  // Cell VALUES come from the frame entries (living cells); the alive set above
  // drives the frozen dead row/column.
  const lookup = new Map<string, Map<string, BeliefErrorView>>();
  for (const entry of activeFrame?.entries ?? []) {
    let row = lookup.get(entry.observer);
    if (row === undefined) {
      row = new Map();
      lookup.set(entry.observer, row);
    }
    row.set(entry.subject, entry);
  }

  function modelFor(observer: PlayerView, subject: PlayerView): BeliefCellModel {
    const oId = observer.agent_id;
    const sId = subject.agent_id;
    const subjImp = impostorIds.has(sId);
    const truth = subjImp ? 1 : 0;
    const base = { observer: oId, subject: sId, subjectIsImpostor: subjImp };
    if (!aliveSet.has(oId) || !aliveSet.has(sId)) {
      return { ...base, kind: "dead", suspicion: 0.5, confidence: 0, error: 0.5 - truth };
    }
    if (oId === sId) {
      return { ...base, kind: "self", suspicion: 0.5, confidence: 0, error: 0.5 - truth };
    }
    const entry = lookup.get(oId)?.get(sId);
    if (entry === undefined || !entry.has_belief) {
      return {
        ...base,
        kind: "noBelief",
        suspicion: entry?.suspicion ?? 0.5,
        confidence: entry?.confidence ?? 0,
        error: entry?.error ?? 0.5 - truth,
      };
    }
    return {
      ...base,
      kind: "value",
      suspicion: entry.suspicion,
      confidence: entry.confidence,
      error: entry.error,
    };
  }

  function pickLayer(next: BeliefViewMode) {
    // Truth/Error are disabled in fog; ignore the click defensively.
    if (!omniscient && next !== "belief") return;
    onLayerChange(next);
  }

  const containerClass = isFullscreen
    ? "fixed inset-2 z-[80] flex flex-col overflow-hidden rounded-lg border-2 border-ink-900 bg-paper-0 shadow-chrome-2"
    : "flex max-h-[88vh] w-full max-w-5xl flex-col overflow-hidden rounded-lg border-2 border-ink-900 bg-paper-0 shadow-chrome-2";

  return (
    <section className={containerClass} aria-label="Belief × Truth matrix">
      <Header
        n={n}
        layer={effectiveLayer}
        omniscient={omniscient}
        onPick={pickLayer}
        {...(onClose ? { onClose } : {})}
        isFullscreen={isFullscreen}
        {...(onToggleFullscreen ? { onToggleFullscreen } : {})}
      />

      <div className="min-h-0 flex-1 overflow-auto p-4">
        {loading ? (
          <Loading />
        ) : error !== null ? (
          <ErrorState message={error} />
        ) : total === 0 ? (
          <EmptyState />
        ) : (
          <>
            {total > 1 && activeFrame !== undefined && (
              <StepControl
                frames={frames}
                step={clampedStep}
                onStep={(i) => {
                  setStepIndex(i);
                }}
              />
            )}
            <div className="mt-3 flex flex-wrap items-start gap-6">
              <Matrix
                players={players}
                impostorIds={impostorIds}
                aliveSet={aliveSet}
                layer={effectiveLayer}
                omniscient={omniscient}
                modelFor={modelFor}
                selected={selected}
                onSelectCell={(observer, subject) => {
                  setSelected((prev) =>
                    prev !== null && prev.observer === observer && prev.subject === subject
                      ? null
                      : { observer, subject },
                  );
                }}
              />
              <div className="min-w-[220px] max-w-[300px] flex-1">
                {selected === null ? (
                  <Legend layer={effectiveLayer} omniscient={omniscient} />
                ) : (
                  <CellDetail
                    players={players}
                    frames={frames}
                    step={clampedStep}
                    selected={selected}
                    omniscient={omniscient}
                    impostorIds={impostorIds}
                    onClose={() => {
                      setSelected(null);
                    }}
                  />
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </section>
  );
}

// ── header (title + segmented toggle + overlay chrome) ─────────────────────────

function Header({
  n,
  layer,
  omniscient,
  onPick,
  onClose,
  isFullscreen,
  onToggleFullscreen,
}: {
  n: number;
  layer: BeliefViewMode;
  omniscient: boolean;
  onPick: (l: BeliefViewMode) => void;
  onClose?: () => void;
  isFullscreen: boolean;
  onToggleFullscreen?: () => void;
}) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-3 border-b-2 border-ink-900 bg-paper-1 px-4 py-3">
      <div>
        <h2 className="text-base leading-tight">{n}×{n} suspicion matrix</h2>
        <p className="font-mono text-[11px] text-ink-500">rows = believer · columns = subject</p>
      </div>
      <div className="flex items-center gap-3">
        {!omniscient && (
          <span className="rounded-md border border-ink-300 px-2 py-1 font-mono text-[10px] uppercase tracking-wide text-ink-500">
            fog · ground-truth hidden
          </span>
        )}
        <div
          role="group"
          aria-label="Belief / Ground-truth / Error layer"
          className="flex gap-1.5 rounded-md border-2 border-ink-900 bg-paper-1 p-1"
        >
          {LAYERS.map((opt) => {
            const active = opt.id === layer;
            const disabled = !omniscient && opt.id !== "belief";
            return (
              <button
                key={opt.id}
                type="button"
                aria-pressed={active}
                disabled={disabled}
                title={disabled ? "Hidden in fog (reveals ground truth)" : undefined}
                onClick={() => {
                  onPick(opt.id);
                }}
                className={
                  "rounded-md border-2 border-ink-900 px-3 py-1 font-mono text-xs font-semibold transition-colors " +
                  (active
                    ? "bg-ink-900 text-paper-0"
                    : disabled
                      ? "cursor-not-allowed border-ink-200 text-ink-300"
                      : "bg-transparent text-ink-500 hover:bg-paper-2")
                }
              >
                {opt.label}
              </button>
            );
          })}
        </div>
        {onToggleFullscreen && (
          <button
            type="button"
            onClick={onToggleFullscreen}
            title={isFullscreen ? "Collapse" : "Full screen"}
            className="rounded-md border-2 border-ink-900 bg-paper-0 px-2 py-1 font-mono text-xs text-ink-900 hover:bg-paper-2"
          >
            {isFullscreen ? "⤡" : "⤢"}
          </button>
        )}
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            aria-label="Close belief matrix"
            className="rounded-md border-2 border-ink-900 bg-paper-0 px-2 py-1 font-mono text-xs text-ink-900 hover:bg-paper-2"
          >
            ✕
          </button>
        )}
      </div>
    </header>
  );
}

// ── per-meeting step control (small-multiples, not animation) ──────────────────

function StepControl({
  frames,
  step,
  onStep,
}: {
  frames: BeliefFrameView[];
  step: number;
  onStep: (i: number) => void;
}) {
  const active = frames[step];
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="font-mono text-[10px] uppercase tracking-wide text-ink-500">Meeting</span>
      <button
        type="button"
        disabled={step <= 0}
        onClick={() => {
          onStep(step - 1);
        }}
        className="rounded-md border-2 border-ink-900 bg-paper-0 px-2 py-0.5 font-mono text-xs text-ink-900 hover:bg-paper-2 disabled:cursor-not-allowed disabled:border-ink-200 disabled:text-ink-300"
      >
        ‹ before
      </button>
      <div className="flex items-center gap-1">
        {frames.map((frame, i) => (
          <button
            key={frame.meeting_id}
            type="button"
            aria-current={i === step ? "true" : undefined}
            title={`meeting ${i + 1} · tick ${frame.tick}`}
            onClick={() => {
              onStep(i);
            }}
            className={
              "h-6 w-6 rounded-md border-2 font-mono text-[10px] " +
              (i === step
                ? "border-ink-900 bg-ink-900 text-paper-0"
                : "border-ink-900 bg-paper-0 text-ink-700 hover:bg-paper-2")
            }
          >
            {i + 1}
          </button>
        ))}
      </div>
      <button
        type="button"
        disabled={step >= frames.length - 1}
        onClick={() => {
          onStep(step + 1);
        }}
        className="rounded-md border-2 border-ink-900 bg-paper-0 px-2 py-0.5 font-mono text-xs text-ink-900 hover:bg-paper-2 disabled:cursor-not-allowed disabled:border-ink-200 disabled:text-ink-300"
      >
        after ›
      </button>
      {active !== undefined && (
        <span className="font-mono text-[11px] text-ink-500">
          {step + 1} / {frames.length} · tick {active.tick}
        </span>
      )}
    </div>
  );
}

// ── the matrix table (header row + dagger reveals + BeliefRow body) ────────────

function Matrix({
  players,
  impostorIds,
  aliveSet,
  layer,
  omniscient,
  modelFor,
  selected,
  onSelectCell,
}: {
  players: PlayerView[];
  impostorIds: Set<string>;
  aliveSet: Set<string>;
  layer: BeliefViewMode;
  omniscient: boolean;
  modelFor: (observer: PlayerView, subject: PlayerView) => BeliefCellModel;
  selected: { observer: string; subject: string } | null;
  onSelectCell: (observer: string, subject: string) => void;
}) {
  // The dagger reveal rides the Ground-Truth and Error layers only, Omniscient
  // only (never Belief, never fog).
  const showDaggers = omniscient && layer !== "belief";
  return (
    <div className="relative inline-block overflow-hidden rounded-md border-[1.5px] border-ink-900 bg-paper-0">
      <table className="border-collapse" style={{ borderSpacing: 0 }}>
        <caption className="sr-only">
          Suspicion from each believer (row) toward each subject (column), {layer} layer.
        </caption>
        <thead>
          <tr>
            <th style={{ width: ROW_HEADER_W, height: COL_HEADER_H }} className="bg-paper-0" />
            {players.map((subject) => {
              const dead = !aliveSet.has(subject.agent_id);
              const isImp = showDaggers && impostorIds.has(subject.agent_id);
              return (
                <th
                  key={subject.agent_id}
                  scope="col"
                  style={{ width: CELL, height: COL_HEADER_H }}
                  className="border border-ink-200 bg-paper-0 align-bottom"
                >
                  <div className="flex flex-col items-center justify-end gap-0.5 pb-1">
                    {isImp ? <Dagger /> : null}
                    <span
                      className="font-mono text-[10px] font-bold leading-none"
                      style={{ color: dead ? tokens.ink[300] : tokens.ink[900] }}
                    >
                      {subject.agent_id}
                    </span>
                  </div>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {players.map((observer) => (
            <BeliefRow
              key={observer.agent_id}
              observer={observer}
              rowDead={!aliveSet.has(observer.agent_id)}
              cells={players.map((subject) => ({ subject, model: modelFor(observer, subject) }))}
              layer={layer}
              omniscient={omniscient}
              cellSize={CELL}
              headerWidth={ROW_HEADER_W}
              selected={selected}
              onSelectCell={onSelectCell}
            />
          ))}
        </tbody>
      </table>
      <div className="flex justify-between border-t border-ink-200 px-2.5 py-1.5 font-mono text-[9px] text-ink-400">
        <span>↓ believer</span>
        <span>subject →</span>
      </div>
    </div>
  );
}

// The ground-truth impostor reveal: an icon (dark disc + paper dagger), NEVER a
// hue, and only mounted Omniscient (the caller gates it).
function Dagger() {
  return (
    <svg width={13} height={13} viewBox="-7 -7 14 14" aria-hidden role="img">
      <circle cx={0} cy={0} r={6.4} fill={tokens.ink[900]} />
      <path
        d="M 0 -4 L 1.4 -0.8 L 1.4 1.3 L 2.9 1.3 L 0 4.4 L -2.9 1.3 L -1.4 1.3 L -1.4 -0.8 Z"
        fill={tokens.paper[0]}
      />
    </svg>
  );
}

// ── legend (per layer) ─────────────────────────────────────────────────────────

function Legend({ layer, omniscient }: { layer: BeliefViewMode; omniscient: boolean }) {
  const heading =
    layer === "belief" ? "READING: BELIEF" : layer === "truth" ? "READING: GROUND TRUTH" : "READING: ERROR";
  return (
    <div>
      <div className="mb-3 font-mono text-[10px] font-bold uppercase tracking-[0.08em] text-ink-500">
        {heading}
      </div>
      {layer === "belief" && (
        <>
          <LegendRow
            swatch={<Swatch style={{ background: `linear-gradient(90deg, ${tokens.suspicion[0]}, ${tokens.suspicion[3]})` }} />}
            label="Suspicion heat"
            desc="Cell = believer's suspicion of subject, 0–100 (mono). Bucketed Low / Med / High."
          />
          <LegendRow
            swatch={<Swatch style={{ background: `repeating-linear-gradient(45deg, ${tokens.paper[0]}, ${tokens.paper[0]} 3px, ${tokens.paper[2]} 3px, ${tokens.paper[2]} 6px)` }} />}
            label="No belief yet"
            desc="Hatched — the agent has formed no view. This is not 0%."
          />
          <LegendRow
            swatch={<Swatch style={{ background: tokens.paper[2] }} />}
            label="Self"
            desc="Diagonal; an agent holds no suspicion file on itself."
          />
        </>
      )}
      {layer === "truth" && (
        <>
          <LegendRow
            swatch={
              <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-md" style={{ background: tokens.ink[900] }}>
                <Dagger />
              </span>
            }
            label="Impostor — true"
            desc="Dagger badge marks the real impostors. A badge, never a hue — and hidden in fog."
          />
          <LegendRow
            swatch={<Swatch style={{ background: `repeating-linear-gradient(45deg, ${tokens.paper[0]}, ${tokens.paper[0]} 4px, ${tokens.paper[2]} 4px, ${tokens.paper[2]} 8px)` }} />}
            label="Impostor column"
            desc="A faint hatch marks an impostor's column — role-neutral, no hue."
          />
          <LegendRow
            swatch={<Swatch style={{ background: `repeating-linear-gradient(45deg, ${tokens.paper[2]}, ${tokens.paper[2]} 3px, ${tokens.paper[3]} 3px, ${tokens.paper[3]} 6px)` }} />}
            label="Dead"
            desc="A frozen row & column for an agent dead at this meeting."
          />
        </>
      )}
      {layer === "error" && (
        <>
          <LegendRow
            swatch={<Swatch style={{ background: tokens.contradiction, boxShadow: `inset 0 0 0 2px ${tokens.contradiction}` }} />}
            label="Confidently wrong"
            desc="LOUD fuchsia + ring: a high-confidence belief that disagrees with truth."
          />
          <LegendRow
            swatch={<GlyphSwatch glyph="✕" />}
            label="False accusation"
            desc="Suspicion aimed at a real crewmate."
          />
          <LegendRow
            swatch={<GlyphSwatch glyph="◆" />}
            label="Missed impostor"
            desc="Trust extended to a true impostor."
          />
          <LegendRow
            swatch={<Swatch style={{ background: tokens.paper[0] }} />}
            label="Aligned"
            desc="Belief matches truth — kept calm and pale."
          />
        </>
      )}
      {!omniscient && (
        <p className="mt-3 font-mono text-[10px] leading-snug text-ink-500">
          As-agent fog: ground truth & error are suppressed (they would reveal who the impostor is).
        </p>
      )}
    </div>
  );
}

function LegendRow({ swatch, label, desc }: { swatch: ReactNode; label: string; desc: string }) {
  return (
    <div className="mb-2.5 flex items-start gap-2.5">
      {swatch}
      <div>
        <div className="text-xs font-semibold leading-tight text-ink-900">{label}</div>
        <div className="mt-0.5 text-[11px] leading-snug text-ink-500">{desc}</div>
      </div>
    </div>
  );
}

function Swatch({ style }: { style: CSSProperties }) {
  return <span className="h-5 w-5 shrink-0 rounded-md border border-ink-200" style={style} />;
}

function GlyphSwatch({ glyph }: { glyph: string }) {
  return (
    <span
      className="flex h-5 w-5 shrink-0 items-center justify-center rounded-md border border-ink-200 font-mono text-[11px] font-bold text-paper-0"
      style={{ background: `rgba(214, 36, 158, 0.55)` }}
    >
      {glyph}
    </span>
  );
}

// ── cell detail (the "popover": cross-meeting trajectory + what-changed diff) ──

function CellDetail({
  players,
  frames,
  step,
  selected,
  omniscient,
  impostorIds,
  onClose,
}: {
  players: PlayerView[];
  frames: BeliefFrameView[];
  step: number;
  selected: { observer: string; subject: string };
  omniscient: boolean;
  impostorIds: Set<string>;
  onClose: () => void;
}) {
  const observer = players.find((p) => p.agent_id === selected.observer);
  const subject = players.find((p) => p.agent_id === selected.subject);
  const subjImp = impostorIds.has(selected.subject);

  // Per-meeting trajectory for this pair: absent (dead) / no belief / suspicion.
  const series = frames.map((frame) => {
    const entry = frame.entries.find(
      (e) => e.observer === selected.observer && e.subject === selected.subject,
    );
    return {
      meetingId: frame.meeting_id,
      tick: frame.tick,
      present: entry !== undefined,
      hasBelief: entry?.has_belief ?? false,
      suspicion: entry?.suspicion ?? 0.5,
      error: entry?.error,
    };
  });

  const current = series[step];
  const prev = step > 0 ? series[step - 1] : undefined;
  const changed = describeChange(current, prev);

  return (
    <div className="rounded-md border-2 border-ink-900 bg-paper-1 p-3">
      <div className="mb-2 flex items-start justify-between gap-2">
        <div className="font-mono text-[10px] font-bold uppercase tracking-[0.08em] text-ink-500">
          Cell detail
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Back to legend"
          className="rounded border border-ink-300 px-1.5 font-mono text-[10px] text-ink-700 hover:bg-paper-2"
        >
          ✕
        </button>
      </div>

      <div className="mb-2 flex items-center gap-1.5 text-xs">
        <PairChip player={observer} fallback={selected.observer} />
        <span className="text-ink-400">→</span>
        <PairChip player={subject} fallback={selected.subject} />
      </div>

      {omniscient && (
        <div className="mb-2 flex items-center gap-1.5">
          <span className="font-mono text-[10px] uppercase tracking-wide text-ink-500">subject</span>
          <span className="rounded border border-ink-300 px-1.5 py-0.5 font-mono text-[10px] text-ink-700">
            {subjImp ? "impostor (true)" : "crewmate (true)"}
          </span>
        </div>
      )}

      <div className="mb-1 font-mono text-[10px] uppercase tracking-wide text-ink-500">
        suspicion across meetings
      </div>
      <div className="space-y-1">
        {series.map((point, i) => (
          <div key={point.meetingId} className="flex items-center gap-1.5">
            <span className={"w-5 shrink-0 font-mono text-[10px] " + (i === step ? "font-bold text-ink-900" : "text-ink-400")}>
              {i + 1}
            </span>
            <div className="h-2 flex-1 overflow-hidden rounded-pill bg-paper-3">
              {point.present && point.hasBelief ? (
                <div className="h-full rounded-pill bg-suspicion-4" style={{ width: `${Math.round(point.suspicion * 100)}%` }} />
              ) : null}
            </div>
            <span className="w-12 shrink-0 text-right font-mono text-[10px] text-ink-700">
              {!point.present ? "absent" : !point.hasBelief ? "—" : Math.round(point.suspicion * 100)}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-3 rounded-md border border-ink-200 bg-paper-0 p-2">
        <div className="font-mono text-[10px] uppercase tracking-wide text-ink-500">what changed this meeting</div>
        <div className="mt-0.5 text-xs text-ink-900">{changed}</div>
        {omniscient && current !== undefined && current.present && current.hasBelief && current.error !== undefined && (
          <div className="mt-1 font-mono text-[11px] text-ink-700">
            error {current.error >= 0 ? "+" : ""}
            {current.error.toFixed(2)} ({subjImp ? "vs impostor" : "vs crewmate"})
          </div>
        )}
      </div>
    </div>
  );
}

interface SeriesPoint {
  present: boolean;
  hasBelief: boolean;
  suspicion: number;
}

function describeChange(current: SeriesPoint | undefined, prev: SeriesPoint | undefined): string {
  if (current === undefined || !current.present) return "Agent absent at this meeting.";
  if (!current.hasBelief) return "No belief formed about this subject yet.";
  if (prev === undefined) return "First recorded meeting.";
  if (!prev.present) return "Believer was absent before — first belief here.";
  if (!prev.hasBelief) return "New belief formed this meeting.";
  const delta = current.suspicion - prev.suspicion;
  if (Math.abs(delta) < 0.005) return "No change in suspicion since the previous meeting.";
  const pts = Math.round(delta * 100);
  return `Suspicion ${pts > 0 ? "rose" : "fell"} ${pts > 0 ? "+" : ""}${pts} since the previous meeting.`;
}

function PairChip({ player, fallback }: { player: PlayerView | undefined; fallback: string }) {
  return (
    <span className="inline-flex items-center gap-1">
      <span
        aria-hidden
        className="inline-block h-2.5 w-2.5 shrink-0 rounded-full ring-1 ring-ink-900/40"
        style={{ backgroundColor: player?.color ?? tokens.ink[300] }}
      />
      <span className="font-mono text-[11px] text-ink-900">{player?.agent_id ?? fallback}</span>
    </span>
  );
}

// ── non-data states ────────────────────────────────────────────────────────────

function Loading() {
  return (
    <div className="flex items-center gap-2 py-8 font-mono text-sm text-ink-500">
      <span
        aria-hidden
        className="h-4 w-4 animate-spin rounded-full border-2 border-ink-200 border-t-ink-700"
      />
      Loading per-meeting beliefs…
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded-md border-2 border-kill/60 bg-paper-1 p-4 text-sm text-ink-900">
      <div className="mb-1 font-semibold">Couldn't load belief frames.</div>
      <div className="font-mono text-xs text-ink-500">{message}</div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-12 text-center">
      <div
        aria-hidden
        className="flex h-12 w-12 items-center justify-center rounded-lg border-2 border-dashed border-ink-300 font-mono text-xl text-ink-300"
      >
        ⊞
      </div>
      <div className="text-base font-semibold text-ink-900">No meetings yet</div>
      <p className="max-w-xs text-sm text-ink-500">
        Beliefs are recorded per meeting (they are timeless between meetings). This game holds no
        meetings, so there is no belief × truth snapshot to show.
      </p>
    </div>
  );
}
