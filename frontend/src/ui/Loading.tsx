// Loading — the shared in-flight cue (Task 12.13 cross-surface consistency;
// design/phase-12/stage-1-design.md §6, §8). One source for the spinner + label
// hand-restated across the route fallback, the mind inspector memory gate, and
// the set/replay fetches. Carries `role="status"` so assistive tech announces it.
// Honours reduced motion (the spin is `motion-safe`). Compose from tokens.

export function Loading({
  label = "Loading…",
  className = "",
}: {
  label?: string;
  className?: string;
}) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={"flex items-center gap-2 text-sm text-ink-500 " + className}
    >
      <span
        aria-hidden
        className="motion-safe:animate-spin inline-block h-4 w-4 shrink-0 rounded-full border-2 border-ink-200 border-t-ink-700"
      />
      {label}
    </div>
  );
}
