// One cell of the Belief × Truth matrix (design/phase-12/stage-1-design.md §3.3,
// slice 4; the `renderMatrix` code in
// design/phase-12/playful-system/playful-system.dc.html; the committed
// 04-matrix-{belief,ground-truth,error}.png renders). A directed
// observer → subject cell whose look swaps with the active layer but whose
// position is stable, so the eye compares belief ↔ truth ↔ error cell-for-cell:
//
//   • Belief       — suspicion heat (0–100, mono), bucketed off `tokens` (Low ≤
//                    .35 < Med ≤ .72 < High); confident-high cells read bold.
//   • Ground-Truth — role-neutral: the impostor reveal is a header dagger (an
//                    icon, never a hue — see BeliefPanel), so NOTHING in the cell
//                    encodes guilt; impostor columns get a faint hatch only.
//                    Omniscient-only (the caller forces Belief in fog).
//   • Error        — the signed |Belief − Truth| rendered LOUD: a fuchsia fill +
//                    a ✕ (false accusation) / ◆ (missed impostor) glyph, and a
//                    ring when confidently-wrong. Never hue-only.
//
// Three non-value kinds render identically in every layer: `self` (the diagonal
// N/A cell), `dead` (a frozen row/col for an agent absent at this meeting), and
// `noBelief` — the hatched "no belief yet" cell, deliberately DISTINCT from a low
// suspicion ("no belief yet" ≠ 0, a binding honesty rule keyed on the DTO's
// `has_belief`, never painted as 0).

import type { CSSProperties } from "react";

import { tokens } from "../tokens";
import type { BeliefViewMode } from "../lib/playback";

// Stable per-cell facts the matrix resolves once per frame (see BeliefPanel).
// `suspicion` / `confidence` / `error` are only meaningful for `value` cells;
// `subjectIsImpostor` is the privileged ground truth (rendered only Omniscient).
export type CellKind = "self" | "dead" | "noBelief" | "value";

export interface BeliefCellModel {
  observer: string;
  subject: string;
  kind: CellKind;
  suspicion: number;
  confidence: number;
  error: number; // signed Belief − Truth (DTO `error`)
  subjectIsImpostor: boolean;
}

// Hatches, all token-sourced (no magic hex): "no belief yet" is the lightest, the
// dead/frozen cell a notch heavier, the impostor column (truth layer) the airiest.
const HATCH_NO_BELIEF = `repeating-linear-gradient(45deg, ${tokens.paper[0]}, ${tokens.paper[0]} 3px, ${tokens.paper[2]} 3px, ${tokens.paper[2]} 6px)`;
const HATCH_DEAD = `repeating-linear-gradient(45deg, ${tokens.paper[2]}, ${tokens.paper[2]} 3px, ${tokens.paper[3]} 3px, ${tokens.paper[3]} 6px)`;
const HATCH_IMPOSTOR = `repeating-linear-gradient(45deg, ${tokens.paper[0]}, ${tokens.paper[0]} 4px, ${tokens.paper[2]} 4px, ${tokens.paper[2]} 8px)`;

// Sequential amber heat. The Low/High cut points come from `tokens.suspicionBucket`;
// the 0.15 / 0.55 / 0.85 stops sub-divide the 5-stop ramp for finer heat (faithful
// to the converge's `heat()`), so a paper floor + the five amber tokens give six
// visible levels.
export function heatColor(s: number): string {
  if (s < 0.15) return tokens.paper[2];
  if (s < tokens.suspicionBucket.low) return tokens.suspicion[0];
  if (s < 0.55) return tokens.suspicion[1];
  if (s < tokens.suspicionBucket.high) return tokens.suspicion[2];
  if (s < 0.85) return tokens.suspicion[3];
  return tokens.suspicion[4];
}

// Legible ink on the pale half of the ramp, paper on the hot half.
function heatTextColor(s: number): string {
  return s < 0.55 ? tokens.ink[900] : tokens.paper[0];
}

// Token hex ("#RRGGBB") → an `rgba()` string, so the Error fill (and the legend
// swatch) ramps the fuchsia `contradiction` token by opacity without a second
// hardcoded colour. Exported so the legend swatch reads the same token.
export function rgba(hex: string, alpha: number): string {
  const n = hex.replace(/^#/, "");
  const r = Number.parseInt(n.slice(0, 2), 16);
  const g = Number.parseInt(n.slice(2, 4), 16);
  const b = Number.parseInt(n.slice(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

interface CellLook {
  background: string;
  content: string | null;
  color: string;
  bold: boolean;
  ring: boolean; // the LOUD confidently-wrong inset ring (Error layer)
}

// The diagonal self cell — an agent holds no suspicion file on itself.
function selfLook(): CellLook {
  return { background: tokens.paper[2], content: "•", color: tokens.ink[300], bold: false, ring: false };
}

// A frozen row/column for a player absent (dead) at this meeting.
function deadLook(): CellLook {
  return { background: HATCH_DEAD, content: null, color: tokens.ink[300], bold: false, ring: false };
}

// "No belief yet" — hatched, NEVER painted as a low/0 suspicion.
function noBeliefLook(): CellLook {
  return { background: HATCH_NO_BELIEF, content: "·", color: tokens.ink[200], bold: false, ring: false };
}

function beliefValueLook(s: number): CellLook {
  return {
    background: heatColor(s),
    content: String(Math.round(s * 100)),
    color: heatTextColor(s),
    bold: s >= tokens.suspicionBucket.high,
    ring: false,
  };
}

function truthValueLook(subjectIsImpostor: boolean): CellLook {
  // Role-neutral: impostor columns get a faint hatch (the dagger badge in the
  // header carries the actual reveal); everything else is blank ground.
  return {
    background: subjectIsImpostor ? HATCH_IMPOSTOR : tokens.paper[0],
    content: null,
    color: tokens.ink[300],
    bold: false,
    ring: false,
  };
}

// Error magnitude below which a cell reads "aligned" (a calm dot) rather than a
// LOUD miss/false-accusation. Shared by the visual look AND the aria-label so the
// screen-reader description never disagrees with what's drawn.
const ERROR_ALIGNED_MAX = 0.32;

function errorValueLook(model: BeliefCellModel): CellLook {
  // |error| is the badness magnitude: for an impostor subject it is how far the
  // belief UNDER-shoots the truth (trust extended to a true impostor → ◆), for a
  // crewmate subject how far it OVER-shoots (suspicion at a real crewmate → ✕).
  const mag = Math.abs(model.error);
  if (mag < ERROR_ALIGNED_MAX) {
    // Aligned — belief matches truth; kept calm and pale.
    return { background: tokens.paper[0], content: "·", color: tokens.ink[200], bold: false, ring: false };
  }
  const loud = mag >= 0.6 && model.confidence >= 0.7;
  const alpha = Math.min(0.92, 0.18 + mag * 0.9);
  return {
    background: rgba(tokens.contradiction, alpha),
    content: model.subjectIsImpostor ? "◆" : "✕",
    color: mag > 0.5 ? tokens.paper[0] : tokens.ink[900],
    bold: loud,
    ring: loud,
  };
}

function lookFor(model: BeliefCellModel, layer: BeliefViewMode, omniscient: boolean): CellLook {
  switch (model.kind) {
    case "self":
      return selfLook();
    case "dead":
      return deadLook();
    case "noBelief":
      return noBeliefLook();
    case "value":
      // Fog forces the Belief layer (the caller also disables the toggle), so the
      // role-derived Truth/Error looks never render under fog — a belt-and-braces
      // firewall guard alongside BeliefPanel's `effectiveLayer`.
      if (!omniscient) return beliefValueLook(model.suspicion);
      if (layer === "truth") return truthValueLook(model.subjectIsImpostor);
      if (layer === "error") return errorValueLook(model);
      return beliefValueLook(model.suspicion);
  }
}

interface BeliefCellProps {
  model: BeliefCellModel;
  layer: BeliefViewMode;
  omniscient: boolean;
  size: number;
  selected: boolean;
  onSelect: () => void;
}

export function BeliefCell({ model, layer, omniscient, size, selected, onSelect }: BeliefCellProps) {
  const look = lookFor(model, layer, omniscient);
  const interactive = model.kind === "value" || model.kind === "noBelief";

  const boxShadow = look.ring ? `inset 0 0 0 2px ${tokens.contradiction}` : undefined;
  const inner: CSSProperties = {
    width: size,
    height: size,
    background: look.background,
    color: look.color,
    fontWeight: look.bold ? 700 : 400,
    outline: selected ? `2px solid ${tokens.ink[900]}` : undefined,
    outlineOffset: -2,
    ...(boxShadow ? { boxShadow } : {}),
  };

  const label = ariaLabel(model, layer, omniscient);

  return (
    <td className="border border-ink-200 p-0 align-middle">
      {interactive ? (
        <button
          type="button"
          onClick={onSelect}
          aria-label={label}
          aria-pressed={selected}
          className="flex cursor-pointer items-center justify-center font-mono text-[10px] leading-none focus:outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-ink-900"
          style={inner}
        >
          {look.content}
        </button>
      ) : (
        <div
          aria-label={label}
          className="flex items-center justify-center font-mono text-[11px] leading-none"
          style={inner}
        >
          {look.content}
        </div>
      )}
    </td>
  );
}

function ariaLabel(model: BeliefCellModel, layer: BeliefViewMode, omniscient: boolean): string {
  const pair = `${model.observer} → ${model.subject}`;
  switch (model.kind) {
    case "self":
      return `${model.observer}: self (no belief about itself)`;
    case "dead":
      return `${pair}: agent absent this meeting`;
    case "noBelief":
      return `${pair}: no belief yet (not 0)`;
    case "value": {
      if (omniscient && layer === "truth") {
        return `${pair}: ${model.subjectIsImpostor ? "subject is the impostor" : "subject is a crewmate"}`;
      }
      if (omniscient && layer === "error") {
        const signed = `${model.error >= 0 ? "+" : ""}${model.error.toFixed(2)}`;
        // Key the description off the SAME magnitude bucket as the visual: a
        // small |error| renders as the calm "aligned" dot, so say so — never call
        // a correctly-suspected impostor a "missed impostor".
        if (Math.abs(model.error) < ERROR_ALIGNED_MAX) {
          return `${pair}: error ${signed} (aligned — belief matches truth)`;
        }
        const kind = model.subjectIsImpostor ? "missed impostor" : "false accusation";
        return `${pair}: error ${signed} (${kind})`;
      }
      return `${pair}: suspicion ${Math.round(model.suspicion * 100)} of 100, confidence ${model.confidence.toFixed(2)}`;
    }
  }
}
