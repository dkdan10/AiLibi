// ESLint flat config (Task 19.12). Until now this package carried TWO
// `eslint-disable-next-line react-hooks/exhaustive-deps` comments
// (`src/components/MapView.tsx`, `src/components/AgentToken.tsx`) and NO linter
// at all — no config, no dependency. The suppressions named a rule nothing
// enforced, so they proved nothing and hid nothing.
//
// This config closes that: `react-hooks/exhaustive-deps` is enabled as an ERROR,
// so those two comments now suppress a rule that is genuinely on. And
// `linterOptions.reportUnusedDisableDirectives: "error"` below is what keeps
// them honest in BOTH directions — if the rule were ever turned off, or the two
// effects were rewritten so the rule no longer fires there, the now-pointless
// directive fails the lint run instead of quietly rotting. A disable comment in
// this package is therefore always live evidence of a real, reviewed exception.
//
// Scope: `src/` + `e2e/` + the repo's own config/script files. Type-aware
// linting (`recommendedTypeChecked`) is deliberately NOT enabled — `npm run
// tsc:check` already runs the full strict type-check in the same gate, and a
// second full type build would double `scripts/check.sh`'s frontend cost for
// rules the compiler mostly already covers.

import js from "@eslint/js";
import reactHooks from "eslint-plugin-react-hooks";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    // Build output, vendored deps, and the Playwright run artifacts (which
    // `playwright.config.ts` writes under `e2e/`). Listed first: a top-level
    // `ignores`-only object is the flat-config equivalent of `.eslintignore`.
    ignores: [
      "dist/**",
      "node_modules/**",
      "storybook-static/**",
      "e2e/.artifacts/**",
      "e2e/.report/**",
    ],
  },
  {
    linterOptions: {
      // The load-bearing setting for this task (see the header note): an
      // `eslint-disable` for a rule that is off — or that no longer fires — is
      // an error, not a warning.
      reportUnusedDisableDirectives: "error",
    },
  },
  js.configs.recommended,
  tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: { ...globals.browser },
    },
    plugins: { "react-hooks": reactHooks },
    rules: {
      // The two rules the pre-existing suppressions depend on. `exhaustive-deps`
      // is an ERROR (not the upstream default `warn`) so `eslint .` exits
      // non-zero on a new violation — a warning in a CI gate is a violation
      // nobody reads.
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "error",
      // `_`-prefixed bindings are the documented "deliberately unused" idiom
      // (destructured rest, placeholder callback args). Caught errors are NOT
      // exempt — the codebase already writes a bare `catch {}` where it means
      // "ignore this", so an unread `catch (error)` binding is a real smell.
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrors: "all",
        },
      ],
    },
  },
  {
    // Node-side files: the token generator, the Vite/Vitest/Playwright configs,
    // and the e2e specs all run under Node, not the browser.
    files: [
      "*.{js,ts}",
      "scripts/**/*.ts",
      "e2e/**/*.ts",
      "src/**/*.test.ts",
    ],
    languageOptions: {
      globals: { ...globals.node },
    },
  },

  // ── legacy-findings ledger (Task 19.12) ────────────────────────────────────
  //
  // A LEDGER, not a silencer. Turning the linter on for the first time surfaced
  // exactly four findings, all pre-existing, each in a component this task's
  // contract pins as behavior-unchanged (tasks/phase-19.md 19.12, "Files NOT in
  // scope: frontend/src/components/"). Suppressing them inline would mean
  // editing those files; deleting the rules would mean losing the coverage on
  // every file that IS clean. So they are enumerated here — file, rule, and what
  // the finding actually is — so the debt is READABLE and the next task that
  // legitimately opens one of these files can clear its line and delete it.
  //
  // Adding a line here is a reviewable act. New code stays fully covered.
  {
    // `setOpen` is `useReplayStore((s) => s.setBeliefOpen)` — a Zustand action
    // with a stable identity, so the Escape-handler effect is correct as
    // written and listing it would be a no-op. Real fix: add the dep (or a
    // justified inline disable) whenever this file is next in scope.
    files: ["src/components/BeliefMatrix.tsx"],
    rules: { "react-hooks/exhaustive-deps": "off" },
  },
  {
    // `no-useless-assignment`: both are the same deliberate
    // initialize-then-narrow idiom — `let seen = false` before a
    // localStorage try/catch, and `let next = index` before a roving-tabindex
    // switch whose `default` returns early. Correct code, redundant initializer.
    files: ["src/components/GuidedTour.tsx", "src/components/MindInspector.tsx"],
    rules: { "no-useless-assignment": "off" },
  },
  {
    // The one finding here that is genuine dead code: `SightingChip` destructures
    // a `players` prop it never reads (the chip renders from `sighting` alone).
    // Removing it touches the prop type AND its single call site at :327 — a
    // behavior-neutral edit, but an edit to a file this task must not open.
    files: ["src/components/TurnCard.tsx"],
    rules: { "@typescript-eslint/no-unused-vars": "off" },
  },
);
