// PlayerSwatch — the per-player identity dot (Task 12.13 cross-surface
// consistency; design/phase-12/stage-1-design.md §6). One source for the small
// round identity swatch hand-restated across the roster rail, the mind
// inspector header, and the meeting/belief surfaces.
//
// FIREWALL: this renders the IDENTITY colour only (greens/teals/purples) — never
// role/guilt (`frontend/CLAUDE.md`). It is decorative (`aria-hidden`): the
// adjacent label carries the agent id for assistive tech.

type SwatchSize = "sm" | "md";

const SIZE_CLASS: Record<SwatchSize, string> = {
  sm: "h-3 w-3 ring-1 ring-ink-900/40",
  md: "h-4 w-4 ring-2 ring-ink-900",
};

export function PlayerSwatch({
  color,
  size = "sm",
  className = "",
}: {
  color: string;
  size?: SwatchSize;
  className?: string;
}) {
  return (
    <span
      aria-hidden
      className={`inline-block shrink-0 rounded-full ${SIZE_CLASS[size]} ${className}`}
      style={{ backgroundColor: color }}
    />
  );
}
