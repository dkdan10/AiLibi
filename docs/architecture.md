# Architecture (as built)

The current-architecture note `AGENTS.md` routes to — authoritative for the
system's layering, its enforced boundaries, and its determinism contracts **as
built**. `DESIGN.md` is the historical design record (a v0.1 draft reconciled to
HEAD as of the Phase 6 close, 2026-05-30): rationale and history, not current
shape. Written from the code under Task 19.1; **current as of Phase 19 (2026-08)**.

## Layering

![The layering as built: engine, the observation firewall, agents and meetings with llm beside them, the orchestrator, and the privileged readers](media/architecture.svg)

The same layering in text, for anywhere the picture does not render:

```text
  engine/             pure deterministic tick; owns ALL hidden state
    v
  observation/        THE FIREWALL: packets + public map, stripped and audited
    v
  agents/  meetings/  engine-free reasoning; ActionIntent out, MeetingResult back
    ^                 llm/ sits beside them: LLMClient Protocol + 4 adapters
  orchestrator/       wires both sides; ActionIntent -> Action; replay JSONL
    v
  eval/   api/        privileged readers; api/ -> frontend/ on GENERATED types
```

Arrows are data flow; imports run the other way — `orchestrator/` is the wiring
layer nothing behind the firewall imports.

## Packages

**`engine/`** — the pure simulation: `tick.py::advance_tick` is a function of
state and actions (no wall clock, no globals, frozen dataclasses). It owns all
hidden state — roles, kill attribution, vent occupancy — and the seeded RNG
whose full Mersenne state serializes into every committed `state_hash`
(`rng.py`; the default `FULL` policy is load-bearing for byte-identity).

**`observation/`** — the firewall. `service.py` builds each player's
`ObservationPacket` from engine state through `engine/visibility.py`, strips
every hidden field, and appends the serialized packet to an on-disk audit log
(`audit.py`). The package defines the engine-free schemas agents consume:
`ObservationPacket`, `PublicMapView` (`public_map.py` — one shared topology
view, projected from the engine map by
`orchestrator/boundary.py::public_map_from_engine_map`), and `ActionIntent` —
the only vocabulary agents may emit. It imports none of `agents/`, `meetings/`,
`llm/`.

**`agents/`** — two-tier reasoning. `tactical/`: deterministic per-tick FSM
policies plus the opt-in learned movers. `strategic/`: the meeting-time LLM
surface, per-model-family Jinja prompt sets loaded strict-undefined. `memory/`:
the typed episodic store and the derived belief state (suspicion graph, alibi
map) those prompts render. `agents/runtime.py` is a TEST-ONLY Phase-2 harness —
the production agent is `orchestrator/game.py::TacticalAgent`.

**`meetings/`** — the protocol state machine (`manager.py`): opening turn ->
reactive accusation chain (the accused answers next; it ends on no new
accusation, a cycle, or the living-player cap) -> opt-in info-share -> roll-call
round (unconditional since baseline 6) -> voting -> resolution, contradictions
recomputed over the full transcript before ballots render. It never mutates
engine state; it returns a `MeetingResult` the orchestrator applies.

**`llm/`** — the provider-neutral surface: `client.py`'s `LLMClient` Protocol,
four adapters implementing it (`fake_provider.py` — deterministic, offline, CI's
default; `provider.py` for Anthropic; `ollama_client.py`;
`featherless_client.py`) selected by `AILIBI_LLM_PROVIDER`, and `budget.py` /
`budgeted_client.py` layered above the Protocol. Featherless is the
canonical eval provider since Phase 14 (`Qwen/Qwen3.6-27B`, locked 2026-07-12 at
Task 16.2, non-thinking). A true leaf — it imports nothing else in the repo; the
detail is in `llm/README.md`.

**`orchestrator/`** — the privileged wiring layer: `game.py::HeadlessGame` runs
the tick loop, dispatches meetings and applies the result
(`apply_meeting_result`); `boundary.py` + `action_ordering.py` translate
`ActionIntent` -> engine `Action` deterministically; `replay.py` writes the replay
JSONL (per-tick actions + a SHA-256 state hash) and owns the substrate-lever registry.

**`eval/`** — the eval harness, hubbed on `report_schema.py`'s typed
`TournamentReport`. The tournament runner
(`balance_eval.py::run_tournament_eval`) folds each just-written replay JSONL
into a typed `GameReport` (`_game_report_from_replay`) and collects the
tournament report; from there the pure analyzers (vote correctness, accusation
calibration, cost dashboard, and more) consume the typed report and never
re-scrape the JSONL. Also home to the determinism and leak tests and the
prompt-regression close gate. Privileged — roles come from the in-memory game
result, never the replay.

**`api/`** — the FastAPI spectator surface (`main.py`, `routes/`) over sanitized DTOs
(`schemas.py`). Privileged by design — a post-game GM view: role, kill attribution and
vent usage are intentionally exposed; `tests/api/test_leak.py` pins the DTO inventory
rather than redacting. Unauthenticated, hence loopback-only (`docs/deployment.md`).

**`frontend/`** — the React + Vite + Tailwind + PixiJS spectator UI, running on
`frontend/src/types/api.ts`: **generated** from the `api.schemas` DTOs by
`scripts/gen_frontend_types.py`, committed, and pinned by `tests/api/test_view_model.py`
— an unregenerated DTO change fails CI. It never imports Python.

**`training/`** — the ML program (Phases 15–18): rollout environment, shaped
rewards, the shared ES core (`bakeoff/es.py`), the ballot surrogate and
conviction models, the co-evolution driver. `numpy` is confined here by contract
— BLAS reduction order is not bit-stable across machines, and the `agents/`
inference path must be. Phase 18 closed NO-FLIP: the scripted FSM stays the
default mover; learned arms stay opt-in.

**`experiments/`** — read-only harnesses; outputs are artifacts, not behavior.
Only the spikes listed in `pyproject.toml`'s `[tool.mypy] exclude` skip the
strict gate (along with `design/`, the one-off design-artifact generators).

`meetings/manager.py` and `orchestrator/game.py` are the two large modules here:
each is a single state machine whose steps share one piece of mutable run state,
so splitting either before it has characterization tests would trade a long file
for a wrong one — the decomposition is on the recorded backlog
(`audits/audit-phase-19-planning.md` §5), not overlooked.

## Enforced boundaries

Four `import-linter` contracts (`.importlinter`, run by `uv run lint-imports` in
`scripts/check.sh`): **agents must not import engine** (the observation
firewall, direct or transitive); **agents must not import training** (keeps
`numpy` off the inference path); **agents must not import meetings.manager**
(agents may use meeting schemas and constants, never the runner); and
**observation must not import agents, meetings, or llm**. `meetings/` and `llm/`
are engine-free in fact, without a contract of their own. Every root package
that ships is on `.importlinter`'s `root_packages` list, so a route out of
`agents/` through `orchestrator/`, `api/`, `eval/` or `scripts/` is walked to its
end; a package left off that list is a hole in the transitive claim, not an
exemption from it.

Backing them: `tests/test_firewall.py` copies the source tree into a throwaway
directory, plants a bad import *there* and asserts `lint-imports` rejects it —
nothing synthetic is ever written inside the checkout, so a concurrent run cannot
see a planted violation; `tests/observation/test_leak_property.py` runs
every packet from Hypothesis-generated games recursively through the
`eval/leak_scan.py` scanners (`eval/leak_test.py` is the pytest wrapper that
owns the scripted sweeps and the planted-leak self-tests); `mypy --strict` runs
repo-wide; and
`eval/determinism_test.py` replays every scripted fixture twice, byte for byte.

## Determinism and the substrate ladder

A seed, a game config (roster, map, tick budget — the run setup
`scripts/run_game.py` builds), an agent factory, and the provider's responses
determine the bytes.
Under the deterministic fake provider a seed alone reproduces byte-identical
replay JSONL, and a committed recording reconstructs byte-identically under any
provider; fresh hosted generation is non-deterministic, so for real providers
the recording — not the seed — is the determinism boundary (the README's
"Three reproducibility scopes" states the exact claims). That is what makes
every metric attributable and every regression bisectable. Behavioral changes to the belief substrate land as
**levers**, registered in `orchestrator/replay.py`: `SUBSTRATE_FLAG_KEYS` is
twenty-one graduated levers (`_RETIRED_ALWAYS_ON_LEVERS` — env gates deleted,
unconditionally ON, kept in the stamp for provenance) plus four live toggles
(`TOGGLEABLE_SUBSTRATE_FLAG_KEYS` — `impostor_roll_call`,
`reporter_reasoning`, `corroboration_discipline`, `testimony_shapes`; each its
own `AILIBI_*` variable, default OFF; `.env.example` documents them). Every recording stamps the snapshot
onto its `game_over` record and into the set's `MANIFEST.md` `flags` column, and
the loader refuses a recording made under a different substrate. Graduating a
lever also carries the prose-sweep obligation in `AGENTS.md`.

**Baselines are adopting records**, not tags: a baseline is the recording that
adopts a substrate. The ladder tip is baseline 8 — the maintenance re-record on
the corrected substrate (`audits/audit-phase-21-rerecord.md`), no bars by
design. Beneath it, baseline 7 (`audits/audit-phase-20-baseline-7.md`): its
pre-registered rule returned **FINDING** and the owner adopted it anyway, by
explicit override; §6.1 holds the ruling. The three reproducibility
scopes this project claims — replay integrity, same-runtime repeatability, and
cross-platform optimizer portability (designed for, not yet confirmed) — are
stated under the README's "Three reproducibility scopes"; never restate them
stronger elsewhere.
