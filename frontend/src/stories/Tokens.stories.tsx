import type { Meta, StoryObj } from "@storybook/react-vite";
import type { ReactNode } from "react";

import { suspicionBucketOf, tokens } from "../tokens";

// The full Playful token sheet, rendered from `src/tokens.ts` — the visual
// target is design/phase-12/playful-system/screens/01-foundations.png (cream/ink
// chunky-sticker). Everything composes from the tokens: the chrome surfaces use
// the 2.5px ink border + hard offset shadow (`shadow-chrome-1`), the dense data
// chips use the 1px hairline (`shadow-data`), and the swatch colours read the
// `tokens` object directly (it is the source, not a magic constant).

function Card({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="rounded-lg border-[2.5px] border-ink-900 bg-paper-0 p-4 shadow-chrome-1">
      <h2 className="mb-3 font-display text-lg font-semibold text-ink-900">{title}</h2>
      {children}
    </section>
  );
}

function Swatch({ name, hex, dark = false }: { name: string; hex: string; dark?: boolean }) {
  return (
    <div className="flex flex-col gap-1">
      <div
        className="h-12 w-full rounded-md border-[1.5px] border-ink-900/30"
        style={{ backgroundColor: hex }}
      />
      <div className={dark ? "text-paper-0" : "text-ink-900"}>
        <div className="font-display text-xs font-semibold leading-tight">{name}</div>
        <div className="font-mono text-[10px] text-ink-500">{hex}</div>
      </div>
    </div>
  );
}

// One status row: a colour ALWAYS paired with a shape/glyph (never hue-only).
function StatusRow({
  glyph,
  label,
  note,
  swatch,
}: {
  glyph: ReactNode;
  label: string;
  note: string;
  swatch: ReactNode;
}) {
  return (
    <li className="flex items-center gap-3">
      <span className="flex h-8 w-8 shrink-0 items-center justify-center">{glyph}</span>
      <div className="min-w-0">
        <div className="font-display text-sm font-semibold text-ink-900">{label}</div>
        <div className="font-mono text-[11px] text-ink-500">{note}</div>
      </div>
      <span className="ml-auto">{swatch}</span>
    </li>
  );
}

const aliveFill = tokens.identity[2] ?? "#14A06E";
const groundExample = tokens.identity[6] ?? "#8350D6";
const hazard = `repeating-linear-gradient(45deg, ${tokens.ink[900]} 0 5px, transparent 5px 10px)`;
const hatch = `repeating-linear-gradient(45deg, ${tokens.ink[300]} 0 2px, transparent 2px 6px)`;

function TokenSheet() {
  return (
    <div className="min-h-screen bg-paper-1 p-6 font-body text-ink-900">
      <header className="mb-6 flex flex-wrap items-baseline gap-3">
        <span className="rounded-pill bg-ink-900 px-3 py-1 font-mono text-xs uppercase tracking-widest text-paper-0">
          01 · foundations
        </span>
        <h1 className="font-display text-3xl font-semibold">AiLibi — Playful tokens</h1>
        <span className="font-mono text-xs text-ink-500">src/tokens.ts → Tailwind @theme + pixiHex</span>
      </header>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Paper & ink — neutral ramp">
          <div className="grid grid-cols-4 gap-2">
            {Object.entries(tokens.paper).map(([step, hex]) => (
              <Swatch key={`paper-${step}`} name={`paper-${step}`} hex={hex} />
            ))}
          </div>
          <div className="mt-2 grid grid-cols-4 gap-2 sm:grid-cols-7">
            {Object.entries(tokens.ink).map(([step, hex]) => (
              <Swatch key={`ink-${step}`} name={`ink-${step}`} hex={hex} />
            ))}
          </div>
        </Card>

        <Card title="Reserved meaning channels — never cross-used">
          <p className="mb-2 font-display text-xs font-semibold text-ink-700">
            suspicion — sequential amber heat
          </p>
          <div className="grid grid-cols-5 gap-2">
            {tokens.suspicion.map((hex, i) => (
              <Swatch key={`susp-${i}`} name={`susp-${i + 1}`} hex={hex} />
            ))}
          </div>
          <div className="mt-2 flex flex-wrap gap-2 font-mono text-[11px] text-ink-700">
            {[0.2, 0.5, 0.9].map((v) => (
              <span
                key={v}
                className="rounded border border-ink-900/20 px-1.5 py-0.5"
                style={{ boxShadow: "var(--shadow-data)" }}
              >
                {v.toFixed(2)} → {suspicionBucketOf(v).toUpperCase()}
              </span>
            ))}
            <span className="text-ink-400">(low ≤ .35 &lt; med ≤ .72 &lt; high)</span>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
            <Swatch name="trust.strong" hex={tokens.trust.strong} />
            <Swatch name="trust.soft" hex={tokens.trust.soft} />
            <Swatch name="distrust.strong" hex={tokens.distrust.strong} />
            <Swatch name="distrust.soft" hex={tokens.distrust.soft} />
            <Swatch name="kill" hex={tokens.kill} />
            <Swatch name="contradiction" hex={tokens.contradiction} />
          </div>
        </Card>

        <Card title="Status — never hue-only">
          <ul className="space-y-3">
            <StatusRow
              label="alive · disc"
              note="fill = player identity colour"
              glyph={
                <span
                  className="h-5 w-5 rounded-full ring-2 ring-ink-900"
                  style={{ backgroundColor: aliveFill }}
                />
              }
              swatch={<span className="font-mono text-[11px] text-ink-500">identity[]</span>}
            />
            <StatusRow
              label="dead · ✕"
              note="role-neutral"
              glyph={<span className="text-xl text-ink-500">✕</span>}
              swatch={<span className="font-mono text-[11px] text-ink-500">{tokens.status.dead.fill}</span>}
            />
            <StatusRow
              label="sabotage · ⚡"
              note="ink hazard stripes, no reserved hue"
              glyph={
                <span
                  className="flex h-6 w-6 items-center justify-center rounded text-paper-0"
                  style={{ background: hazard }}
                >
                  ⚡
                </span>
              }
              swatch={<span className="font-mono text-[11px] text-ink-500">hazard</span>}
            />
            <StatusRow
              label="contradiction · weak"
              note="dashed · 1.5px"
              glyph={
                <span
                  className="w-7"
                  style={{
                    borderTop: `${tokens.status.contradictionWeak.weight}px dashed ${tokens.status.contradictionWeak.stroke}`,
                  }}
                />
              }
              swatch={<span className="font-mono text-[11px] text-ink-500">ink-300</span>}
            />
            <StatusRow
              label="contradiction · strong"
              note="solid · 3px"
              glyph={
                <span
                  className="w-7"
                  style={{
                    borderTop: `${tokens.status.contradictionStrong.weight}px solid ${tokens.status.contradictionStrong.stroke}`,
                  }}
                />
              }
              swatch={<span className="font-mono text-[11px] text-ink-500">contradiction</span>}
            />
          </ul>
        </Card>

        <Card title="Identity palette — identity ONLY">
          <div className="grid grid-cols-3 gap-3 sm:grid-cols-5">
            {tokens.identity.map((hex, i) => (
              <div key={`id-${i}`} className="flex flex-col items-center gap-1">
                <span
                  className="flex h-12 w-12 items-center justify-center rounded-full border-[2.5px] border-ink-900 font-display text-sm font-semibold text-paper-0 shadow-chrome-1"
                  style={{ backgroundColor: hex }}
                >
                  p-{i}
                </span>
                <span className="font-mono text-[10px] text-ink-500">{hex}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Type scale">
          <div className="space-y-3">
            <p className="font-display text-3xl font-semibold">Meeting at tick 312</p>
            <p className="font-body text-base">
              I saw p-5 head toward Reactor around tick 312 — they had no alibi.
            </p>
            <p className="font-mono text-sm text-ink-700">
              p-5 · suspicion 0.82 · tick 312 · {"{ vote: \"p-5\" }"}
            </p>
          </div>
        </Card>

        <Card title="Spacing · radii · elevation">
          <p className="mb-1 font-display text-xs font-semibold text-ink-700">space (px)</p>
          <div className="flex flex-wrap items-end gap-2">
            {tokens.space.map((v, i) => (
              <div key={`space-${i}`} className="flex flex-col items-center gap-1">
                <span className="bg-ink-900" style={{ width: v, height: v }} />
                <span className="font-mono text-[10px] text-ink-500">{v}</span>
              </div>
            ))}
          </div>
          <p className="mb-1 mt-3 font-display text-xs font-semibold text-ink-700">radii</p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(tokens.radius).map(([name, v]) => (
              <div key={name} className="flex flex-col items-center gap-1">
                <span
                  className="h-10 w-10 border-[2.5px] border-ink-900 bg-paper-2"
                  style={{ borderRadius: v }}
                />
                <span className="font-mono text-[10px] text-ink-500">{name}</span>
              </div>
            ))}
          </div>
          <p className="mb-1 mt-3 font-display text-xs font-semibold text-ink-700">elevation</p>
          <div className="flex flex-wrap gap-4 pb-2 pr-2">
            <span className="rounded-md bg-paper-0 px-3 py-2 font-mono text-[11px] shadow-chrome-1">
              chrome-1
            </span>
            <span className="rounded-md bg-paper-0 px-3 py-2 font-mono text-[11px] shadow-chrome-2">
              chrome-2
            </span>
            <span className="rounded-md bg-paper-0 px-3 py-2 font-mono text-[11px] shadow-data">
              data (hairline)
            </span>
          </div>
        </Card>

        <Card title="Motion — purposeful only">
          <ul className="space-y-1 font-mono text-sm text-ink-700">
            <li>quick · {tokens.motion.quick}ms</li>
            <li>base · {tokens.motion.base}ms</li>
            <li>slow · {tokens.motion.slow}ms</li>
            <li className="text-ink-500">chromeEase · {tokens.motion.chromeEase}</li>
            <li className="text-ink-500">dataEase · {tokens.motion.dataEase}</li>
            <li className="text-ink-400">{tokens.motion.reducedMotion}</li>
          </ul>
        </Card>

        <Card title="Two-truth grammar">
          <div className="flex flex-wrap gap-4">
            <div className="flex flex-col items-center gap-1">
              <span
                className="flex h-14 w-14 items-center justify-center rounded-md font-display text-xs font-semibold text-paper-0"
                style={{ backgroundColor: groundExample, outline: tokens.truth.ground.outline }}
              >
                ground
              </span>
              <span className="font-mono text-[10px] text-ink-500">solid · authoritative</span>
            </div>
            <div className="flex flex-col items-center gap-1">
              <span
                className="flex h-14 w-14 items-center justify-center rounded-md font-display text-xs font-semibold text-ink-900"
                style={{
                  backgroundColor: groundExample,
                  opacity: tokens.truth.belief.opacity,
                  outline: tokens.truth.belief.outline,
                }}
              >
                belief
              </span>
              <span className="font-mono text-[10px] text-ink-500">ghosted · attributed</span>
            </div>
            <div className="flex flex-col items-center gap-1">
              <span
                className="flex h-14 w-14 items-center justify-center rounded-md border-[1.5px] border-ink-300 font-display text-[11px] text-ink-500"
                style={{ background: hatch }}
              >
                none
              </span>
              <span className="font-mono text-[10px] text-ink-500">no belief yet (≠ 0%)</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

const meta = {
  title: "Design/Tokens",
  parameters: { layout: "fullscreen" },
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

export const Sheet: Story = {
  render: () => <TokenSheet />,
};
