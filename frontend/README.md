# frontend — the spectator viewer

The replay viewer for AiLibi games: an omniscient view of the ground truth and
an as-agent view limited to what one chosen player could see. It reads the
spectator API in development and pre-baked JSON in the static demo bundle
(`scripts/build_demo_bundle.py`).

## Stack

React 19 and TypeScript on Vite, Tailwind v4 for the page chrome, PixiJS 8
(through `@pixi/react`) for the map, and zustand for state. Vitest runs the
unit tests, Playwright the browser journeys in `e2e/`, ESLint the lint, and
Storybook the component stories in `src/stories/`.

## Scripts

Run `bash scripts/setup_env.sh` from the repository root once (it runs `npm ci`
here), then from this folder:

| Command | What it does |
| --- | --- |
| `npm run dev` | Vite on port 5173, proxying `/api/*` to the API on port 8000 |
| `npm run build` | Typecheck, then the production build |
| `npm run tsc:check` | Typecheck the app, the Node configs and the e2e suite |
| `npm run test` / `test:watch` | Vitest once, or watching |
| `npm run lint` | ESLint |
| `npm run e2e` | Playwright journeys; starts the API and dev server itself |
| `npm run preview` | Serve the production build |
| `npm run gen:tokens` | Regenerate the `@theme` block in `src/index.css` |
| `npm run storybook` / `build-storybook` | Storybook on port 6006, or a static build |

`bash scripts/check.sh` runs lint, `tsc:check`, `test` and `build`. The e2e
suite needs a browser (`npx playwright install chromium`) and runs in CI.

## Generated API types

`src/types/api.ts` and `src/types/api.fidelity.ts` are generated from the
Pydantic view models in `api/schemas.py`; after a schema change, run
`uv run python scripts/gen_frontend_types.py` from the repository root rather
than editing them. `tests/api/test_view_model.py` fails when they are stale, and
`tsc:check` type-checks a real served replay against them through the fidelity
file.

## Tokens

`src/tokens.ts` is the single source of every colour, spacing, radius, type,
elevation and motion value: the DOM reads it through the generated `@theme`
block and the Pixi layer through `pixiHex()`. Components compose from tokens,
never a hardcoded hex. `src/tokens.test.ts` checks that every utility a
component uses is declared and that the generated block matches.

## Colour rules

These keep the hidden-information game honest; breaking one leaks a secret or
misleads the viewer. They come from the
[phase-12 design brief](../process/design/phase-12/claude-design-brief.md).

1. A player's identity colour is identity only: never encode role, guilt or
   alignment in it.
2. The ground-truth impostor reveal is an explicit icon or badge, never a hue,
   and it is hideable (hidden in the as-agent view).
3. Suspicion is a sequential heat ramp, distinct from identity hues and
   bucketed Low, Med and High.
4. Trust and distrust are blue and orange, not red and green: colour-blind safe,
   and red is reserved for kills.
5. Outcomes (ejected, skipped) use role-neutral colours, since colouring by
   guilt would leak who the impostor was.
6. Never hue alone: pair every status with a shape or text.
