# Agent Prompt — 4.3 React + Vite + Tailwind + PixiJS setup

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.3 — React + Vite + Tailwind + PixiJS setup, anchored to DESIGN.md §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-react-vite-tailwind-setup`
**Depends on:** 4.2 merged
**Section refs:** DESIGN.md §7
**Complexity:** Medium

`frontend/` skeleton, type-safe API client mirroring the 4.1 DTOs, and
a Zustand store contract that downstream components (4.4, 4.4.5, 4.5,
4.6, 4.7, 4.8) consume. This task establishes the second contract
boundary of Phase 4 — after the DTO inventory (4.1), the
store/component contract is the load-bearing artifact. Get it right
once; five components depend on it.

**Tooling decisions baked in.** Per DESIGN.md §7:

- **Package manager:** npm with `package-lock.json`. Yarn / pnpm are
  out unless an existing repo choice requires otherwise. (DESIGN.md
  doesn't dictate; npm wins on default familiarity.)
- **Build:** Vite. React + TypeScript template (`@vitejs/plugin-react`
  + `@vitejs/plugin-react-swc` — implementing agent picks; document).
- **Styling:** Tailwind CSS via `@tailwindcss/vite` (Tailwind v4 plug-in
  approach) OR PostCSS pipeline (Tailwind v3) — implementing agent
  picks the current LTS; document the version chosen.
- **State:** Zustand. One store: `useReplayStore`. No Redux, no
  Recoil, no context shenanigans.
- **Graphics:** PixiJS v8+ via `@pixi/react` for React integration
  (or vanilla PixiJS with a `useEffect` mount pattern — implementing
  agent picks; document).
- **TypeScript:** strict mode (`strict: true`, `noUncheckedIndexedAccess:
  true`, `exactOptionalPropertyTypes: true`).

**API type generation.** The Pydantic DTOs in `api/schemas.py` are the
source of truth; TypeScript types in `frontend/src/types/api.ts` MUST
match them. Two paths:

1. **Generated** via `openapi-typescript` against
   `http://localhost:8000/openapi.json` — drift-resistant, requires the
   API to be running at type-gen time. Add a `npm run gen:api`
   script that hits the running API and writes
   `frontend/src/types/api.ts`. Run it as part of `scripts/check.sh`
   when the API is reachable; skip with a warning when it isn't.
2. **Hand-authored** — direct re-implementation of the 4.1 DTOs as
   TypeScript types. Simpler, no codegen dependency. Drift risk:
   adding a DTO field requires editing both Python AND TypeScript.

Recommend path 1 (generated). Path 2 is fine if the implementing
agent finds `openapi-typescript` painful for some reason. Document
the choice in `## Decisions`.

**Store contract — frozen at this task.** The store shape that 4.4–4.8
consume:

```typescript
interface ReplayStoreState {
  // Available replays (loaded once via /replays on app mount)
  replayList: ReplayMetadataView[] | null;
  replayListError: string | null;

  // Currently-selected replay
  currentReplay: ReplayView | null;
  currentReplayError: string | null;

  // Playback state
  currentTick: number;           // index into currentReplay.ticks
  isPlaying: boolean;
  playbackSpeed: 0.5 | 1 | 2 | 4;

  // Selected meeting (for MeetingView overlay)
  selectedMeetingId: string | null;

  // Selected agent (for ThoughtStream)
  selectedAgentId: string | null;

  // Memory cache (sparse — only meeting-boundary snapshots)
  // keyed by `${meeting_id}:${agent_id}`
  memoryCache: Record<string, AgentMemoryView>;
}

interface ReplayStoreActions {
  loadReplayList(): Promise<void>;
  selectReplay(gameId: string): Promise<void>;
  setCurrentTick(tick: number): void;
  setIsPlaying(playing: boolean): void;
  setPlaybackSpeed(speed: 0.5 | 1 | 2 | 4): void;
  selectMeeting(meetingId: string | null): void;
  selectAgent(agentId: string | null): void;
  fetchMemoryView(meetingId: string, agentId: string): Promise<void>;
  clearError(): void;
}
```

Adding a field after 4.3 merges requires a follow-up task touching all
five consumer components. Implementing agent: do not invent fields
the consumer tasks don't explicitly need; the inventory above is
complete for MVP.

**Out of scope** (explicit decisions deferred):

- **Authentication / authorization.** API is local-dev only in MVP.
- **Routing (React Router etc.).** Single-page app; URL state is not
  load-bearing in MVP. Add when there's a second page.
- **Internationalization.** English-only in MVP.
- **Service worker / offline support.** Not in MVP scope.
- **Production build / deployment config.** `vite build` produces
  output but deployment infra (Docker, CDN, etc.) is Phase 5+.
- **Component implementations.** This task ships the skeleton ONLY —
  `App.tsx` renders a "loading replay list..." stub. MapView,
  MeetingView etc. land in 4.4+.

**Files in scope:**
- frontend/package.json
- frontend/package-lock.json
- frontend/vite.config.ts
- frontend/tailwind.config.js (or `tailwind.config.ts`)
- frontend/postcss.config.js (if Tailwind v3)
- frontend/tsconfig.json
- frontend/tsconfig.node.json
- frontend/index.html
- frontend/src/main.tsx
- frontend/src/App.tsx
- frontend/src/api/client.ts
- frontend/src/store/replayStore.ts
- frontend/src/types/api.ts
- frontend/src/index.css
- frontend/.gitignore
- scripts/setup_env.sh
- scripts/check.sh
- .gitignore

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- api/ (beyond consuming the contract)
- frontend/src/components/ (downstream tasks own these)
- .github/workflows/ci.yml (Phase 5 concern)
- DESIGN.md
- AGENT_IMPLEMENTATION.md
- pyproject.toml
- uv.lock
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- tests/

**Definition of done:**
- [ ] **`frontend/` skeleton compiles.** `cd frontend && npm install && npm run build` succeeds. `npm run dev` boots Vite at `http://localhost:5173` and connects to API at `http://localhost:8000` via Vite proxy (`/api/*` proxied; CORS not needed in dev).
- [ ] **TypeScript strict mode.** `tsconfig.json` enables `strict: true`, `noUncheckedIndexedAccess: true`, `exactOptionalPropertyTypes: true`. No `// @ts-ignore` or `any` types in the codebase.
- [ ] **API client (`src/api/client.ts`).** Exposes typed methods matching each 4.1 endpoint: `listReplays() -> Promise<ReplayMetadataView[]>`, `getReplay(gameId) -> Promise<ReplayView>`, `getTick(gameId, tick)`, `getMeeting(gameId, meetingId)`, `getMemory(gameId, meetingId, agentId)`, `getEvalCostSummary()`. All return parsed-typed responses. Error handling: HTTP errors are surfaced as typed exceptions, not silently swallowed.
- [ ] **Type module (`src/types/api.ts`).** Either generated (via `openapi-typescript`) or hand-authored to mirror every 4.1 DTO. Choice documented in `## Decisions`. If generated, the `npm run gen:api` script is committed.
- [ ] **Zustand store (`src/store/replayStore.ts`).** Implements the `ReplayStoreState` + `ReplayStoreActions` interface above. Verify by importing it from a smoke test that all action methods exist and the state shape matches.
- [ ] **`App.tsx` stub renders meaningfully.** On mount: calls `loadReplayList()`; displays "Loading replays..." while pending; displays the list with clickable items when loaded; displays an error message on failure. No PixiJS, no MapView yet — those are 4.4. The acceptance is "user can see the API connection works" (a populated list or an error).
- [ ] **Tailwind classes work.** `App.tsx` uses at least three Tailwind utility classes; `tsc` + `vite build` produces CSS with those classes resolved.
- [ ] **PixiJS installs cleanly.** `@pixi/react` (or vanilla PixiJS — document) is listed in `package.json`; importing it from a smoke file compiles without TypeScript errors. No PixiJS usage in `App.tsx` yet.
- [ ] **`scripts/setup_env.sh` installs frontend deps.** Idempotent: re-running doesn't break anything. Detects if `frontend/package.json` exists; runs `npm install` from `frontend/` if so. Does not modify the Python setup behavior.
- [ ] **`scripts/check.sh` runs frontend checks.** Adds a frontend block that runs `cd frontend && npm run tsc:check && npm run build` (or equivalent). Failures cause `scripts/check.sh` to exit non-zero. Skipped with a warning if `frontend/package.json` doesn't exist (graceful degradation for branches that don't include 4.3 yet).
- [ ] **`frontend/.gitignore`** excludes `node_modules/`, `dist/`, `.vite/`, `coverage/`. Root `.gitignore` already excludes `node_modules/` from prior phases; verify no duplication.
- [ ] **`package-lock.json` committed.** No `yarn.lock` or `pnpm-lock.yaml`.
- [ ] No imports from `engine/`, `agents/`, `llm/`, `meetings/`, `observation/`, `orchestrator/` (the Python firewall doesn't extend to TypeScript but the architectural rule does). The frontend talks to the API, not to Python modules.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (Python tests unaffected).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally (including the new frontend block when `frontend/` exists).

## Implementation hint

`package.json` skeleton (illustrative; pin exact versions when implementing):

```json
{
  "name": "ailibi-frontend",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc --noEmit && vite build",
    "tsc:check": "tsc --noEmit",
    "gen:api": "openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "pixi.js": "^8.0.0",
    "@pixi/react": "^8.0.0",
    "zustand": "^4.5.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react-swc": "^3.7.0",
    "openapi-typescript": "^7.4.0",
    "tailwindcss": "^4.0.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0"
  }
}
```

Resolve to the current LTS at task-execution time; the implementing agent should not pin to versions that are already stale. Document the resolved versions in `## Decisions`.

`vite.config.ts` proxy block (illustrative):

```typescript
// frontend/vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
```

The proxy lets the frontend make requests to `/api/replays` which Vite forwards to `http://localhost:8000/replays`. No CORS configuration needed; production deployment can configure CORS at the API layer (Phase 5+).

Zustand store skeleton (illustrative):

```typescript
// frontend/src/store/replayStore.ts
import { create } from "zustand";
import * as api from "../api/client";

export const useReplayStore = create<ReplayStoreState & ReplayStoreActions>((set, get) => ({
  replayList: null,
  replayListError: null,
  currentReplay: null,
  currentReplayError: null,
  currentTick: 0,
  isPlaying: false,
  playbackSpeed: 1,
  selectedMeetingId: null,
  selectedAgentId: null,
  memoryCache: {},

  async loadReplayList() {
    try {
      const list = await api.listReplays();
      set({ replayList: list, replayListError: null });
    } catch (e) {
      set({ replayListError: e instanceof Error ? e.message : String(e) });
    }
  },

  // ... other actions ...
}));
```

For `scripts/check.sh`, the addition is a guarded block:

```bash
# scripts/check.sh — illustrative addition
if [ -f frontend/package.json ]; then
  echo "Running frontend checks..."
  ( cd frontend && npm run tsc:check && npm run build )
else
  echo "Skipping frontend checks (frontend/package.json not present)."
fi
```

This preserves existing Python check behavior for branches that don't include 4.3.

## Public types this task introduces
- `frontend/src/store/replayStore.ts::useReplayStore`
- `frontend/src/types/api.ts::*` (every DTO from 4.1, mirrored)`
- `frontend/src/api/client.ts::listReplays`
- `frontend/src/api/client.ts::getReplay`
- `frontend/src/api/client.ts::getTick`
- `frontend/src/api/client.ts::getMeeting`
- `frontend/src/api/client.ts::getMemory`
- `frontend/src/api/client.ts::getEvalCostSummary`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import api.main"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-4-react-vite-tailwind-setup` with a title like `task 4.3: react + vite + tailwind + pixijs setup`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
