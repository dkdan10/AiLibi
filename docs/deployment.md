# Deployment & exposure posture

This document records the privilege model of the AiLibi spectator API and the
hard prerequisites for ever exposing it beyond the local machine. It is the
durable note for a future deployer; read it before changing any network bind.

Anchors: audit C-C-1, C-C-2, C-C-4; DESIGN.md §1.1 (component diagram, Spectator
API as a *privileged view*), §7 (tech stack — FastAPI, docker-compose dev infra);
audits/audit-phase-19-triage.md §7 item 14 (the shippable-artifact gap Task 19.13
closed).

**The one-line summary.** There is exactly one sanctioned way to put AiLibi in
front of someone who is not the local operator: build the **static demo bundle**
(below) and serve that. The live API is never it.

## The API is an unauthenticated GM view

The spectator/control-plane API (`api/`) serves the **full game-master view by
deliberate design**: every hidden-information field — player roles, kill
attribution, vent state, and the rendered LLM prompts — is returned with **no
authentication**. This is intentional for the MVP's local, single-user
spectating workflow (`scripts/run_spectator.sh` + `npm run dev`). The engine is
the single source of truth and *contains* hidden info; the spectator API is the
privileged consumer that exposes it for inspection (DESIGN.md §1.1, §3.6).

Because there is no authentication and no per-field redaction of hidden state on
this surface, the API is **safe only when it is unreachable by anyone but the
local operator**. Concretely, it is safe in exactly two configurations:

1. **Loopback only** — bound to `127.0.0.1`, reachable solely from the same
   machine. This is the default and the only supported MVP posture.
2. **Behind authentication + network isolation** — fronted by a reverse proxy
   (or equivalent) that enforces authentication and restricts the network path,
   so that the unauthenticated origin is never directly reachable.

**Never bind or publish this API on a non-loopback interface (e.g. `0.0.0.0`)
without first putting it behind auth + network isolation.** Doing so exposes
every hidden field to anyone on the network (audit C-C-1, the single
highest-urgency operational finding).

### Default binds (safe by default)

* `scripts/run_spectator.sh` runs `uvicorn api.main:app --port 8000` with **no
  `--host`**, so uvicorn defaults to `127.0.0.1` (loopback). Correct as-is.
* `docker-compose.yml` publishes the API on the **host loopback only**:
  `ports: ["127.0.0.1:${AILIBI_API_PORT:-8000}:8000"]`. The container-internal
  `uvicorn --host 0.0.0.0` is required so Docker's published-port forwarding can
  reach the process (a container process bound to the container's own
  `127.0.0.1` is unreachable through a published port); host exposure is gated
  by the loopback-scoped publish, **not** by the container bind flag. A bare
  `"8000:8000"` would publish on `0.0.0.0` on the host and expose the GM view to
  the LAN — do not revert to it.
* The compose service also forwards `AILIBI_CORS_ORIGINS` into the container
  (empty by default). Compose does not propagate host/`.env` variables into a
  container automatically, so this passthrough is what makes the allowlist below
  actually configurable on the compose path; set it on the host or in `.env`.

## The static demo bundle — the ONLY sanctioned public artifact

The rule above ("safe only when unreachable by anyone but the local operator")
used to leave the project with no way at all to show the spectator to anyone.
`scripts/build_demo_bundle.py` is the answer, and it resolves the tension by
removing the API rather than by protecting it:

```bash
uv run python scripts/build_demo_bundle.py            # → frontend/dist/demo-bundle
python -m http.server -d frontend/dist/demo-bundle 8080
```

The output is one directory — `index.html`, its asset chunks, and a `data/`
tree — and **it contains no server**. `frontend/src/api/client.ts` carries a
data-source seam: built with `VITE_AILIBI_STATIC_DATA=1`, every call that would
have gone to `/api/<path>?set=<set>` reads the file `data/<set>/<path>.json`
instead. Any static file server, object store, or CDN is therefore a sufficient
host, and there is no process to bind, no port to expose, and nothing to
authenticate.

**Why this is safe to publish when the API is not.** The bundle is a set of
pre-rendered ANSWERS, not a query surface. It ships:

* the hand-curated featured replays only (`FEATURED_GAMES` in
  `frontend/src/components/ReplayPicker.tsx`), not the 100-replay corpus;
* the per-set rubric rows for exactly those games;
* no `tournament-eval-report.json` (the 9p2i one is 29 MB — that is the corpus,
  not a demo), so the Dashboard tab renders a card written for this artifact:
  what the demo ships, and where the eval report lives. That card renders no
  part of the failed request. It has to be said explicitly, because the natural
  implementation gets it wrong: `ApiError` folds the response BODY into its
  message, and a file server answers a missing file with its own HTML error
  page, so a panel that printed the error printed a raw
  `<!DOCTYPE HTML PUBLIC …>` document at the visitor. The copy is
  `noReportBundle` in `frontend/src/lib/copy.ts`, and
  `scripts/build_demo_bundle.py` fails the build unless the emitted JS both
  carries it and has dropped the local-checkout arm — so no bundle ships with
  that card deleted, or with the arm that tells a visitor to run a tournament.

It carries the same **post-game GM view** of those specific games that the local
spectator shows — roles, kill attribution, vent usage — because that is what the
spectator IS (`docs/architecture.md`, `api/` — privileged by design). Publishing
the bundle therefore publishes the recorded outcomes of the curated games, which
are already committed to this repository in `replays/samples/`. What it does NOT
publish is a live, unauthenticated, unbounded-work endpoint over whatever the
host happens to have on disk. That distinction — a fixed set of already-public
bytes vs. an open query surface into the operator's filesystem — is the whole
reason one of these is publishable and the other is not.

**What the bundle does not change.** Nothing above. The live API's posture is
untouched by this document's addition: no `StaticFiles` mount was added to
`api/`, the compose publish stays loopback-scoped, and the prohibitions in the
previous section stand exactly as written. If you find yourself wanting to expose
the API because the bundle is missing something, the answer is to bake more into
the bundle — not to move the bind.

## Publishing the bundle: the GitHub Pages route

`.github/workflows/pages.yml` is the sanctioned way to put the artifact above in
front of the world. On every push to `main` — and on manual dispatch, never on a
pull request, which would hand a fork's head commit a deployment of the
project's public face — it runs the builder's tests, builds
`frontend/dist/demo-bundle`, uploads it as the Pages artifact, and deploys it.
Because Pages rebuilds on push, re-recording the featured games refreshes the
live demo with no further work.

Least privilege is `ci.yml`'s rule: the workflow's token is `contents: read`,
and `pages: write` + `id-token: write` are granted to the deploy job alone.
Deployments run in a `pages` concurrency group with `cancel-in-progress: false`,
because each run publishes a whole site and cancelling one mid-flight can leave
the live site half-swapped.

**This changes nothing about the live API.** No `StaticFiles` mount was added to
`api/`, the compose publish stays loopback-scoped, and every prohibition above
stands as written. What Pages hosts is a directory of files; no AiLibi process
runs anywhere in it.

### The one-time setup (owner)

These are repository settings, so the workflow cannot do them itself — and its
"Configure Pages" step fails until step 1 is done.

1. **Enable Pages with the workflow as its source**: Settings → Pages → Build
   and deployment → Source: *GitHub Actions*.
2. **Set the repository description** (≤ 350 characters):

   > Deterministic social-deduction sim (Among-Us-style) with LLM agents behind
   > an enforced observation firewall — built by directing AI coding agents
   > against written contracts: 350 PRs, 19 phases, byte-identical replays,
   > honest negative ML results.

3. **Set the topics**: `multi-agent`, `llm-agents`, `social-deduction`,
   `deterministic-simulation`, `agentic-coding`, `claude-code`, `evaluation`,
   `among-us`, `python`, `fastapi`, `react`, `pixijs`.
4. **Set the homepage** to the Pages URL the first successful deployment prints.

### Re-verifying a deployment

Two checks, answering two different questions.

* **Is the deployed site up?** The workflow asks on every run: its last step
  requests the deployment's own `page_url` and fails on anything other than HTTP
  200, so a green Pages run *is* that answer, and the URL is in that step's log
  and on the run's `github-pages` environment. By hand:

  ```bash
  curl -sSL -o /dev/null -w '%{http_code}\n' <the Pages URL>
  ```

* **Does the artifact still play with no API?** `frontend/e2e/bundle.spec.ts`
  drives the BUILT bundle in a browser with every `/api` request aborted at the
  network layer. Point it at a directory you built rather than letting it build
  its own:

  ```bash
  uv run python scripts/build_demo_bundle.py     # → frontend/dist/demo-bundle
  cd frontend
  AILIBI_DEMO_BUNDLE_DIR="$PWD/dist/demo-bundle" \
    npx playwright test e2e/bundle.spec.ts
  ```

  Read that plainly: the spec starts its own file server over that DIRECTORY. It
  never fetches the Pages URL and says nothing about the remote host. What it
  proves is that the bytes the workflow uploads are bytes that work — the
  `curl` above is what says they arrived.

## CORS posture (audit C-C-2)

CORS is **closed by default** and additive:

* **Same-origin serving needs no CORS.** Under `npm run dev`, the Vite dev
  server proxies API calls so the browser sees a single origin; production
  same-origin static serving (UI and API behind one origin) is likewise
  same-origin. Neither needs any CORS middleware, and the default app installs
  none.
* **Cross-origin requires an explicit, closed allowlist.** Set
  `AILIBI_CORS_ORIGINS` to a comma-separated list of exact origins (e.g.
  `https://spectator.internal,https://ops.internal`). Only then does
  `api.main.create_app()` install `CORSMiddleware`, scoped to exactly those
  origins.
* **No wildcard, ever.** `allow_origins=["*"]` is never shipped. A literal `*`
  in `AILIBI_CORS_ORIGINS` is rejected at startup, and an
  explicitly-set-but-empty value is treated as "no cross-origin access" (no
  middleware installed), not "allow all" — consistent with the project's
  no-silent-fallback discipline.

Because cross-origin access is only relevant once the API is reachable from
another origin, configuring `AILIBI_CORS_ORIGINS` is itself a step on the
exposure path and must be paired with the auth + network isolation requirements
above.

## Prerequisites before any network exposure (audit C-C-4)

The following are **hard prerequisites** that must be built *before* the API is
exposed on any network path beyond loopback. They are documented here as
exposure-gating requirements and are intentionally **not implemented yet** — the
MVP is loopback-only, so there is no exposure path to protect. Implement them as
part of building the exposure path, not before:

1. **An edge rate limiter.** The replay/eval endpoints perform unbounded
   filesystem and parsing work per request; without an edge rate limiter, a
   network client can trivially exhaust the single-process server. A rate
   limiter belongs at the reverse-proxy/edge tier that also enforces auth.
2. **A short-TTL negative-lookup cache.** Repeated lookups for missing or
   non-existent replay/game ids should be absorbed by a short-TTL negative
   cache so that misses (including hostile id-scanning) do not translate into
   repeated full-directory scans. This pairs with the loader-efficiency work and
   lives behind the same "exposed beyond localhost" boundary.

Both items touch `api/replay_loader.py`, which is owned by separate loader-
efficiency work — they are recorded here as the exposure contract and coded when
the exposure path is actually built, not in the hardening change that produced
this note.
