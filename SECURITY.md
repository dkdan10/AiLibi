# Security policy

## Scope: what this project is

AiLibi is a local research testbed for multi-agent reasoning, not a deployed
service. There is no hosted instance, no user accounts, and no production
deployment to compromise. The supported version is whatever is on `main`; there
are no releases and no backported fixes.

Read this before filing anything, because the single most security-relevant
property of this repository is deliberate.

## The spectator API is an unauthenticated GM view — by design

The spectator/control-plane API (`api/`) serves the **full game-master view on
purpose**: player roles, kill attribution, vent state, and the rendered LLM
prompts are all returned with **no authentication**. That is the point — it is
the privileged inspection surface for a local, single-user spectating workflow
(`scripts/run_spectator.sh` + `npm run dev`), and the observation firewall that
protects the *agents* from hidden state is explicitly not applied to it.

So **"the API exposes hidden game state without auth" is not a vulnerability
here — it is the documented design.** The trust boundary is the network, not the
API surface. The API is safe in exactly two configurations, both recorded in
[docs/deployment.md](docs/deployment.md):

1. **Loopback only** — bound to `127.0.0.1`, reachable only from the same
   machine. This is the default and the only supported posture.
   `scripts/run_spectator.sh` passes no `--host` (uvicorn defaults to loopback),
   and `docker-compose.yml` publishes on `127.0.0.1` only.
2. **Behind authentication and network isolation** — fronted by a reverse proxy
   that authenticates and restricts the network path, so the unauthenticated
   origin is never directly reachable.

**Never bind or publish this API on a non-loopback interface (e.g. `0.0.0.0`)
without first putting it behind auth and network isolation.** Doing so hands
every hidden field to anyone who can reach the port. `docs/deployment.md` also
lists the hard prerequisites (an edge rate limiter, a short-TTL negative-lookup
cache) that must be built *before* any network exposure — they are intentionally
not implemented, because the MVP has no exposure path.

CORS is closed by default and additive: cross-origin access requires an explicit
`AILIBI_CORS_ORIGINS` allowlist of exact origins, a literal `*` is rejected at
startup, and no wildcard is ever shipped.

## What is in scope for a report

Things that would still be defects under the loopback-only posture above:

- A default configuration or script that binds or publishes the API beyond
  loopback (a regression against `docs/deployment.md`).
- A hidden-state leak across the **observation firewall** — anything that puts
  role, killer identity, or kill attribution into an `ObservationPacket` or the
  agent-visible surface. This is the firewall the leak test walks recursively;
  a hole in it is a real bug.
- A path that lets replay/eval input (a crafted replay file, a game id) escape
  its directory, execute code, or otherwise do something other than be parsed.
- Credential handling defects — an API key written to a replay, a log, or a
  committed artifact.

Out of scope: the unauthenticated GM view itself, missing rate limiting, and
anything else that only matters once the API is exposed beyond loopback — all
three are documented above and in `docs/deployment.md` as exposure-path work,
not shipped defects.

## How to report

**Use GitHub's private vulnerability reporting** — the *Security* tab of this
repository → *Report a vulnerability*. That keeps the report private while it is
being triaged, which is what you want for anything genuinely sensitive.

If private reporting is unavailable to you and the finding is **not** sensitive
(a documentation-vs-code mismatch, a hardening suggestion, a default-binding
question), open a normal GitHub issue instead. Do not put working exploit
details in a public issue.

Please include what you observed, the file and line if you have it, and how to
reproduce. This is a one-person project built with AI agents: expect a
best-effort, non-commercial response time, and no bug bounty.
