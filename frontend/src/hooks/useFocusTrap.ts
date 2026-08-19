// Focus management for a modal dialog (role="dialog" aria-modal). While
// `active`: moves focus into `ref` on open, TRAPS Tab within the dialog's
// focusable descendants (aria-modal alone does NOT constrain focus — without
// this a keyboard/SR user tabs straight past the dialog into the nav /
// transport / roster behind the scrim), and restores focus to the
// previously-focused element on close/unmount.
//
// ONE OWNER PER KEYPRESS. Overlays stack — the guided tour opens over a meeting
// or over the Belief × Truth matrix — and a trap has to listen on `window` to
// see a Tab that starts outside its own subtree. Without an owner rule both
// traps then answer the SAME keypress and fight: the lower one pulls focus into
// itself, the upper one yanks it back to its own first control, and the ring
// never advances past that first control. `rank` orders the overlays exactly as
// their z-index contract does, and only the top-most active trap acts; the rest
// stand down for as long as it is mounted. This is the Tab half of the
// single-owner rule the overlays already apply to Escape by yielding it to the
// guided tour.
//
// The container passed via `ref` must be focusable — give it `tabIndex={-1}`.
// Escape is intentionally NOT handled here: each overlay owns its own Escape
// (and yields it to the guided tour), so the caller keeps that logic.

import { useEffect, useId, type RefObject } from "react";
import { create } from "zustand";

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

/**
 * Overlay ranks, ordered like the shell's z-index contract: the guided tour
 * (z-90) opens over the Belief × Truth matrix (z-80) and over the meeting modal
 * (z-50).
 *
 * The two workspace overlays share one rank because they are mutually exclusive
 * — the matrix returns null while a meeting is open — so the tour is the only
 * surface that ever stacks a second trap on top of a live one. Sharing the rank
 * is also what lets both call sites keep their two-argument call.
 */
export const OVERLAY_RANK = {
  workspace: 0,
  guidedTour: 1,
} as const;

export type OverlayRank = (typeof OVERLAY_RANK)[keyof typeof OVERLAY_RANK];

interface TrapEntry {
  readonly id: string;
  readonly rank: OverlayRank;
}

/**
 * The traps that are currently active, in registration order.
 *
 * Explicit shared state rather than a module-level flag, for the same reason the
 * guided tour's open state lives in the replay store: "who owns the keyboard" is
 * a fact two components disagree about, so it needs one readable home.
 */
interface TrapRegistry {
  readonly entries: readonly TrapEntry[];
  readonly acquire: (id: string, rank: OverlayRank) => void;
  readonly release: (id: string) => void;
}

const useTrapRegistry = create<TrapRegistry>((set) => ({
  entries: [],
  acquire: (id, rank) =>
    set((state) => ({
      entries: [...state.entries.filter((entry) => entry.id !== id), { id, rank }],
    })),
  release: (id) =>
    set((state) => ({ entries: state.entries.filter((entry) => entry.id !== id) })),
}));

/**
 * The trap that owns the keyboard: highest rank wins, ties go to the most
 * recently registered — which is what DOM stacking does for equal z-index.
 */
function ownerId(entries: readonly TrapEntry[]): string | null {
  let owner: TrapEntry | null = null;
  for (const entry of entries) {
    if (owner === null || entry.rank >= owner.rank) {
      owner = entry;
    }
  }
  return owner === null ? null : owner.id;
}

export function useFocusTrap(
  ref: RefObject<HTMLElement | null>,
  active: boolean,
  rank: OverlayRank = OVERLAY_RANK.workspace,
): void {
  const id = useId();

  // Publish this trap while it is open so the owner rule can see it.
  useEffect(() => {
    if (!active) {
      return;
    }
    useTrapRegistry.getState().acquire(id, rank);
    return () => {
      useTrapRegistry.getState().release(id);
    };
  }, [active, id, rank]);

  // Focus the dialog on open; restore the prior focus on close/unmount.
  useEffect(() => {
    if (!active) {
      return;
    }
    const previouslyFocused = document.activeElement as HTMLElement | null;
    ref.current?.focus();
    return () => {
      previouslyFocused?.focus?.();
    };
  }, [active, ref]);

  // Cycle Tab within the dialog while open AND while this trap owns the
  // keyboard. A trap under an open guided tour reads the registry, sees it is
  // not the owner, and leaves the keypress alone.
  useEffect(() => {
    if (!active) {
      return;
    }
    const onKey = (event: KeyboardEvent): void => {
      if (event.key !== "Tab") {
        return;
      }
      if (ownerId(useTrapRegistry.getState().entries) !== id) {
        return;
      }
      const dialog = ref.current;
      if (dialog === null) {
        return;
      }
      const focusable = Array.from(dialog.querySelectorAll<HTMLElement>(FOCUSABLE));
      if (focusable.length === 0) {
        event.preventDefault();
        dialog.focus();
        return;
      }
      const first = focusable[0]!;
      const last = focusable[focusable.length - 1]!;
      const activeEl = document.activeElement;
      if (event.shiftKey) {
        if (activeEl === first || activeEl === dialog || !dialog.contains(activeEl)) {
          event.preventDefault();
          last.focus();
        }
      } else if (activeEl === last || !dialog.contains(activeEl)) {
        event.preventDefault();
        first.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("keydown", onKey);
    };
  }, [active, id, ref]);
}
