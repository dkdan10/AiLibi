// Focus management for a modal data dialog (role="dialog" aria-modal). Factored
// from GuidedTour's inline trap (task 12.13 a11y) so the meeting + belief
// overlays share ONE implementation. While `active`: moves focus into `ref` on
// open, TRAPS Tab within the dialog's focusable descendants (aria-modal alone
// does NOT constrain focus — without this a keyboard/SR user tabs straight past
// the dialog into the nav / transport / roster behind the scrim), and restores
// focus to the previously-focused element on close/unmount.
//
// The container passed via `ref` must be focusable — give it `tabIndex={-1}`.
// Escape is intentionally NOT handled here: each overlay owns its own Escape
// (and yields it to the guided tour), so the caller keeps that logic.

import { useEffect, type RefObject } from "react";

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

export function useFocusTrap(ref: RefObject<HTMLElement | null>, active: boolean): void {
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

  // Cycle Tab within the dialog while open.
  useEffect(() => {
    if (!active) {
      return;
    }
    const onKey = (event: KeyboardEvent): void => {
      if (event.key !== "Tab") {
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
  }, [active, ref]);
}
