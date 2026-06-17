import type { Meta, StoryObj } from "@storybook/react-vite";

import { tokens } from "../tokens";
import type { PlayerView } from "../types/api";
import { PlayerChip } from "./PlayerChip";

// Realistic roster (brief: real players p-0…p-8, never lorem ipsum). The swatch
// uses each player's identity colour — the firewall-safe per-player palette,
// which never encodes role/guilt, so crew and impostor chips look identical.
const NAMES = ["Sage", "Fern", "Moss", "Teal", "Cyan", "Iris", "Plum", "Lilac", "Orchid"];
const players: PlayerView[] = NAMES.map((display_name, i) => ({
  agent_id: `p-${i}`,
  display_name,
  role: i === 5 ? "IMPOSTOR" : "CREWMATE",
  color: tokens.identity[i] ?? "#888888",
}));

// The chip currently renders on a dark surface (its cream/ink restyle is a
// Wave-B slice), so the stories sit it on an ink sticker panel to stay legible.
const meta = {
  title: "UI/PlayerChip",
  component: PlayerChip,
  args: { players },
  parameters: { layout: "centered" },
  decorators: [
    (Story) => (
      <div className="rounded-lg border-[2.5px] border-ink-900 bg-ink-900 p-4 shadow-chrome-1">
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof PlayerChip>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = { args: { agentId: "p-3" } };

export const Impostor: Story = { args: { agentId: "p-5" } };

// An id not in the roster falls back to a neutral swatch + the raw id as name.
export const UnknownId: Story = { args: { agentId: "p-99" } };

export const Roster: Story = {
  args: { agentId: "p-0" },
  render: (args) => (
    <div className="flex flex-col gap-2">
      {players.map((p) => (
        <PlayerChip key={p.agent_id} agentId={p.agent_id} players={args.players} />
      ))}
    </div>
  ),
};
