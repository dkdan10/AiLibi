// Stories for the Belief × Truth hero (Task 12.6; the committed
// 04-matrix-{belief,ground-truth,error}.png renders). They drive the
// PRESENTATIONAL <BeliefPanel/> — the connected <BeliefMatrix/> only adds the
// store wiring + the launcher/overlay, which Storybook can't host — with mock
// per-meeting `BeliefFrameView[]` snapshots (the exact served DTO shape), so each
// firewall + state requirement is visible in isolation:
//   • Belief / Ground-truth / Error layers (same layout, swapped data);
//   • the ground-truth dagger reveal is Omniscient-only (the Fog story proves it
//     vanishes + the Truth/Error toggles disable);
//   • Error cells render LOUD (fill + ring + ✕/◆ glyph), never hue-only;
//   • "no belief yet" is a hatched cell, distinct from 0;
//   • the per-meeting step control + the empty (no-meeting) state.

import { useEffect, useState } from "react";
import type { ComponentProps } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";

import { BeliefPanel } from "../components/BeliefPanel";
import type { BeliefViewMode } from "../lib/playback";
import { tokens } from "../tokens";
import type { BeliefErrorView, BeliefFrameView, PlayerView } from "../types/api";

// Realistic 9p2i roster (brief: real ids p-0…p-8, never lorem). Identity colours
// are the firewall-safe palette — crew and impostor chips look identical.
const IMPOSTORS = new Set(["p-2", "p-5"]);
const PLAYERS: PlayerView[] = Array.from({ length: 9 }, (_, i) => ({
  agent_id: `p-${i}`,
  display_name: `p-${i}`,
  role: IMPOSTORS.has(`p-${i}`) ? "IMPOSTOR" : "CREWMATE",
  color: tokens.identity[i] ?? "#888888",
}));
const ALL_IDS = PLAYERS.map((p) => p.agent_id);

// A small deterministic 0–1 hash so the synthetic matrix is varied yet stable.
function hash(seed: string, salt: number): number {
  let h = salt >>> 0;
  for (let i = 0; i < seed.length; i++) {
    h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return (h % 1000) / 1000;
}

// A few crewmates who get confidently (and wrongly) accused — the ✕ LOUD cells.
const FALSE_ACCUSATIONS = new Set(["p-0→p-4", "p-3→p-4", "p-8→p-6", "p-4→p-0", "p-1→p-6"]);

interface Belief {
  suspicion: number;
  confidence: number;
}

// One believer's view of one subject at meeting `m` (0-based) — or null for "no
// belief yet" (sparse early game). The grammar each layer needs:
//   • p-5 (impostor) is increasingly caught → high suspicion (Error: aligned);
//   • p-2 (impostor) gets away → most under-suspect it (Error: LOUD ◆);
//   • crewmates mostly trusted (aligned), a few confidently mis-accused (✕).
function beliefAt(m: number, obs: string, subj: string): Belief | null {
  const noBeliefCut = m === 0 ? 0.16 : m === 1 ? 0.07 : 0;
  if (hash(`${obs}|${subj}|nb`, 11) < noBeliefCut) {
    return null;
  }
  const jitter = (hash(`${obs}|${subj}`, 3) - 0.5) * 0.08;
  const pair = `${obs}→${subj}`;

  if (subj === "p-5") {
    const misses = hash(`${obs}|p5`, 5) < 0.22; // a minority never catch on
    const suspicion = misses ? 0.12 + jitter : Math.min(0.95, 0.45 + m * 0.2 + jitter);
    return { suspicion, confidence: 0.62 + m * 0.1 };
  }
  if (subj === "p-2") {
    const suspects = hash(`${obs}|p2`, 9) < 0.18; // a rare few are onto p-2
    const suspicion = suspects ? Math.min(0.9, 0.5 + m * 0.18) : 0.08 + Math.max(0, jitter);
    return { suspicion, confidence: 0.78 + m * 0.05 };
  }
  if (FALSE_ACCUSATIONS.has(pair)) {
    return { suspicion: Math.min(0.85, 0.55 + m * 0.12), confidence: 0.8 + m * 0.04 };
  }
  // A trusted crewmate: low suspicion, modest confidence (Error: aligned/pale).
  return { suspicion: Math.max(0.02, 0.12 + jitter), confidence: 0.45 + m * 0.08 };
}

function makeFrame(meetingId: string, tick: number, m: number, present: string[]): BeliefFrameView {
  const entries: BeliefErrorView[] = [];
  for (const observer of present) {
    for (const subject of ALL_IDS) {
      const subjImp = IMPOSTORS.has(subject);
      const truth = subjImp ? 1 : 0;
      const base = { observer, subject, subject_is_impostor: subjImp };
      const belief = observer === subject ? null : beliefAt(m, observer, subject);
      if (belief === null) {
        entries.push({
          ...base,
          suspicion: 0.5,
          confidence: 0,
          error: 0.5 - truth,
          has_belief: false,
        });
      } else {
        const suspicion = Math.max(0, Math.min(1, belief.suspicion));
        entries.push({
          ...base,
          suspicion,
          confidence: Math.max(0, Math.min(1, belief.confidence)),
          error: suspicion - truth,
          has_belief: true,
        });
      }
    }
  }
  return { meeting_id: meetingId, tick, entries };
}

// Three meetings; by the last one p-7 is dead → a frozen row & column.
const FRAMES: BeliefFrameView[] = [
  makeFrame("m-1", 118, 0, ALL_IDS),
  makeFrame("m-2", 264, 1, ALL_IDS),
  makeFrame("m-3", 391, 2, ALL_IDS.filter((id) => id !== "p-7")),
];

// Wrap the controlled panel with local layer state so the toggle works live; in
// fog the panel forces Belief (Truth/Error disabled), kept coherent here too.
function Interactive(args: ComponentProps<typeof BeliefPanel>) {
  const [layer, setLayer] = useState<BeliefViewMode>(args.layer);
  useEffect(() => {
    setLayer(args.layer);
  }, [args.layer]);
  return (
    <div className="flex min-h-screen items-start justify-center bg-paper-1 p-6">
      <BeliefPanel
        {...args}
        layer={args.omniscient ? layer : "belief"}
        onLayerChange={setLayer}
      />
    </div>
  );
}

const meta = {
  title: "Components/Belief × Truth",
  component: BeliefPanel,
  parameters: { layout: "fullscreen" },
  args: {
    players: PLAYERS,
    frames: FRAMES,
    layer: "belief",
    omniscient: true,
    onLayerChange: () => {},
  },
  render: (args) => <Interactive {...args} />,
} satisfies Meta<typeof BeliefPanel>;

export default meta;
type Story = StoryObj<typeof meta>;

// Suspicion heat (0–100), bucketed; no-belief hatches; self diagonal.
export const Belief: Story = { args: { layer: "belief" } };

// Same layout, the ground-truth reveal: impostor daggers (p-2, p-5) + frozen
// dead row/col. An icon, never a hue.
export const GroundTruth: Story = { args: { layer: "truth" } };

// Signed Belief − Truth, LOUD: ✕ false accusations, ◆ missed impostors, a ring
// on confidently-wrong cells; aligned cells stay pale.
export const ErrorLayer: Story = { args: { layer: "error" } };

// As-agent fog: the dagger reveal vanishes and Ground-truth / Error disable, so
// no role leaks — only the agent-neutral Belief layer remains.
export const Fog: Story = { args: { omniscient: false, layer: "belief" } };

// A zero-meeting game (the default-served 4p1i set is mostly zero-meeting): the
// first-class empty state, not a blank panel.
export const Empty: Story = { args: { frames: [] } };
