# Playful design-space — in-repo reference (Wave-0b, chosen direction)

The deterministic in-repo reference for the **chosen Playful direction**, vendored from the Claude Design space export so
every build session (web or local) has it WITHOUT the transient/authenticated Claude Design share URL.

- **`playful-system.dc.html`** + **`support.js`** — the Wave-0b **converge** deliverable (the full Playful system: token
  sheet, both viewing modes, the Belief/Truth/Error 9×9 matrix, the meeting view). Serve this folder and open the HTML to
  render it live; the component code inside (`renderMap` / `renderMatrix` / accusation-chain / ballots / `verdict`) is the
  reference for slices **12.5 (map), 12.6 (belief×truth), 12.7 (meeting)**. (`support.js` = the Claude Design runtime;
  needed only to render the HTML.)
- **`screens/`** — rendered screenshots of the 0b deliverable = the **visual targets** for screenshot-diff verification,
  captured from the `.dc.html`:
  - `00-overview.png` — the whole deliverable.
  - `01-foundations.png` — tokens / ramps / identity palette / type / `tokens.ts` → **12.1** target.
  - `02-map.png` — the canonical_1 floorplan → **12.5**.
  - `03-two-truths.png` — Omniscient + As-agent fog → **12.5** (fog).
  - `04-matrix-belief.png` / `04-matrix-ground-truth.png` / `04-matrix-error.png` — the 9×9 matrix's three toggle
    layers (Belief, Ground-truth, Error) → **12.6**.
  - `05-meeting.png` — accusation chain + ballots → **12.7**.
  Any state re-renders from the `.dc.html` (system Chrome, e.g. `uv run --with playwright …`) — a web build agent can do
  the same for verification.

The **actionable token extract is `../tokens-seed.md`** — what 12.1 transcribes into `frontend/src/tokens.ts`.

Do NOT point build agents at the Claude Design share URL (`api.anthropic.com/v1/design/h/…`): it returns a gzip-tar of
the whole space in Claude Design's internal format. These committed files are the clean, pinned source — re-export from
Claude Design if the design changes.
