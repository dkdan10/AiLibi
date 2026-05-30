# Deployment & exposure posture

This document records the privilege model of the AiLibi spectator API and the
hard prerequisites for ever exposing it beyond the local machine. It is the
durable note for a future deployer; read it before changing any network bind.

Anchors: audit C-C-1, C-C-2, C-C-4; DESIGN.md §1.1 (component diagram, Spectator
API as a *privileged view*), §7 (tech stack — FastAPI, docker-compose dev infra).

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
