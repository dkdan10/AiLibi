# Security policy

## Scope: what this project is

AiLibi is a local research testbed for multi-agent reasoning, not a deployed
service. Its one hosted copy is the static demo at
<https://dkdan10.github.io/AiLibi/>: recorded games, with no backend, no
accounts and no API. The API runs only on loopback, on the machine that starts
it. The supported version is whatever is on `main`; there are no releases and
no backported fixes.

## The spectator API is an unauthenticated game-master view, by design

The API (`api/`) returns player roles, kill attribution, vent state and the
rendered model prompts with no authentication: it is the inspection surface for
one person spectating on their own machine, so the trust boundary is the
network. It binds to loopback by default (`scripts/run_spectator.sh` passes no
`--host`; `docker-compose.yml` publishes on `127.0.0.1` only), CORS stays closed
unless `AILIBI_CORS_ORIGINS` lists exact origins, and it must never be exposed
beyond loopback without authentication and network isolation in front of it.
[docs/deployment.md](docs/deployment.md) records the posture and what any
exposure would need first.

## What is in scope for a report

Defects even under the loopback-only posture:

- A default configuration or script that exposes the API beyond loopback.
- A hidden-state leak across the **observation firewall**: another player's
  role, killer identity or kill attribution reaching an `ObservationPacket` or
  anything else agents see.
- Replay or eval input (a crafted replay file, a game id) that escapes its
  directory, executes code, or does anything other than be parsed.
- An API key written to a replay, a log or a committed artifact.

Out of scope: the unauthenticated view itself, missing rate limiting, and
anything else that matters only once the API is exposed beyond loopback.

## How to report

**Use GitHub's private vulnerability reporting** (the *Security* tab, then
*Report a vulnerability*) when the repository has it switched on; the owner
enables it under *Settings*, *Code security*. If it is unavailable to you and
the finding is **not** sensitive, open a normal issue instead, without working
exploit details.

Include what you observed, the file and line if you have it, and how to
reproduce. This is a one-person project built with AI agents: expect a
best-effort response and no bug bounty.
