# Playful design-space — in-repo reference (Wave-0b, chosen direction)

The deterministic in-repo reference for the **chosen Playful direction**, vendored from the Claude Design space export so
every build session (web or local) has it WITHOUT the transient/authenticated Claude Design share URL.

- **`playful-system.dc.html`** + **`support.js`** — the Wave-0b **converge** deliverable (the full Playful system: token
  sheet, both viewing modes, the Belief/Truth/Error 9×9 matrix, the meeting view). Serve this folder and open the HTML to
  render it live; the component code inside (`renderMap` / `renderMatrix` / accusation-chain / ballots / `verdict`) is the
  reference for slices **12.5 (map), 12.6 (belief×truth), 12.7 (meeting)**. (`support.js` = the Claude Design runtime;
  needed only to render the HTML.)
- **`playful-render.png`** — a rendered screenshot of the Playful (cream) skin = the **visual target** (screenshot-diff
  reference; **12.1's Storybook + cream theme should match it**). It's the 0a composite render; the fuller system is the
  `.dc.html`.
- **`design-chat.md`** — the design-session transcript (rationale / prompts; provenance).

The **actionable token extract is `../tokens-seed.md`** — what 12.1 transcribes into `frontend/src/tokens.ts`.

Notes:
- The rejected directions (Forensic/dark, Telemetry/light) are intentionally NOT vendored — they'd mislead the build
  toward the wrong skin; they're recorded in `design-chat.md` + the stage docs.
- Do NOT point build agents at the Claude Design share URL (`api.anthropic.com/v1/design/h/…`): it returns a gzip-tar of
  the whole space in Claude Design's internal format. These committed files are the clean, pinned source — re-export from
  Claude Design if the design changes.
