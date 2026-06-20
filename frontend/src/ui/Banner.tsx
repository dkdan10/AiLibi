// Banner — the shared inline notice (Task 12.13 cross-surface consistency;
// design/phase-12/stage-1-design.md §6, §8). One source for the bordered notice
// strip used for load errors (dismissable), the per-set "not scored" caveat, and
// other inline messages, replacing the per-surface restatements. Compose from
// tokens; no hardcoded hex.
//
// `tone` is role-neutral chrome, never an identity/guilt hue. `error` uses the
// reserved kill red ONLY as the alert channel (paired with text, never hue-only).

import type { ReactNode } from "react";

type BannerTone = "error" | "info" | "caveat";

const TONE_CLASS: Record<BannerTone, string> = {
  // kill red = the alert channel (paired with the message text, not hue-only).
  error: "border-ink-900 bg-kill text-paper-0",
  info: "border-ink-900 bg-paper-0 text-ink-900",
  caveat: "border-ink-300 bg-paper-2 text-ink-900",
};

export function Banner({
  tone = "info",
  children,
  onDismiss,
  role = "status",
  className = "",
}: {
  tone?: BannerTone;
  children: ReactNode;
  onDismiss?: () => void;
  role?: "status" | "alert";
  className?: string;
}) {
  return (
    <div
      role={role}
      aria-live={role === "alert" ? "assertive" : "polite"}
      className={
        "flex items-start gap-3 rounded-lg border-2 px-3 py-2 text-sm shadow-data " +
        TONE_CLASS[tone] +
        " " +
        className
      }
    >
      <div className="min-w-0 flex-1">{children}</div>
      {onDismiss !== undefined && (
        <button
          type="button"
          onClick={onDismiss}
          aria-label="Dismiss"
          className="-mr-1 shrink-0 rounded-md border-2 border-current px-2 text-xs font-bold leading-5 opacity-80 transition-opacity hover:opacity-100"
        >
          ✕
        </button>
      )}
    </div>
  );
}
