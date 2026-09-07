"""Generate ``frontend/src/types/api.ts`` from the Pydantic view-model DTOs.

Phase 12, Task 12.2 (DESIGN.md §7, §9.5; stage-0 §0.5 / §3.3). This kills the
hand-mirrored ``types/api.ts`` and its documented drift (e.g. the dashboard's
``conversion`` / ``gate_metrics`` arriving untyped): the Pydantic models in
``api.schemas`` are the single source of truth, and this script projects them
to TypeScript deterministically. ``scripts/check.sh`` regenerates and diffs
(via ``tests/api/test_view_model.py::test_generated_frontend_types_are_committed``),
so any DTO change that is not regenerated fails CI.

Design choices (a small bespoke script, not a heavy dependency — implementation
hint):

* **Discriminated unions narrow.** ``TickEventView`` / ``ObservationClaimView``
  / ``StatementClaimView`` are emitted as named unions of interfaces, each
  carrying its literal ``type`` discriminant, so a TS ``switch (e.type)``
  narrows to the concrete member (the codegen's riskiest spot; pinned by the
  fidelity fixture this script also emits — see ``_render_fidelity``).
* **The contract version is emitted as a runtime constant** (Task 19.24), not
  only as the ``viewModelVersion: string`` field type. ``api.schemas`` stamps
  :data:`api.schemas.VIEW_MODEL_VERSION` onto the served payloads, and
  ``frontend/src/api/client.ts`` rejects a response whose stamp differs — a check
  that is only meaningful if both sides read the SAME constant, which is what
  emitting it here guarantees. A bumped version that is not regenerated fails the
  drift gate exactly like a DTO change.
* **Eval report tree is cut at the deliberate stubs.** The served
  ``/eval/tournament-report`` wrapper (``eval.meeting_quality.TournamentEvalReport``)
  is generated so the metric blocks (incl. ``conversion`` / ``gate_metrics``)
  stay in sync, but its ``report`` sub-tree is cut at ``TournamentReport`` /
  ``GameReport`` STUBS (matching the prior hand-written contract): mirroring the
  full ``GameReport`` would replicate the entire internal meeting-transcript
  graph (``MeetingReport`` → ``MeetingTranscript`` → …) the spectator DTO
  firewall deliberately keeps OUT of ``api.schemas``. The dashboard reads only
  the metric blocks + the per-game stub fields, so the stub is faithful to what
  it consumes.

Usage:
    uv run python scripts/gen_frontend_types.py          # write the files
    uv run python scripts/gen_frontend_types.py --check   # exit 1 if stale
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import tempfile
import types as _pytypes
from collections.abc import Mapping
from pathlib import Path
from typing import Annotated, Any, Final, Literal, Union, get_args, get_origin

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pydantic import BaseModel  # noqa: E402

import api.schemas as schemas  # noqa: E402
from api.schemas import (  # noqa: E402
    VIEW_MODEL_VERSION,
    AgentMemoryView,
    BeliefFrameView,
    EvalCostSummaryView,
    PublicResultsView,
    ReplayView,
    RubricView,
    SuspicionGraphView,
)
from eval.meeting_quality import TournamentEvalReport  # noqa: E402

_OUT_TYPES: Final[Path] = _REPO_ROOT / "frontend" / "src" / "types" / "api.ts"
_OUT_FIDELITY: Final[Path] = (
    _REPO_ROOT / "frontend" / "src" / "types" / "api.fidelity.ts"
)

# Top-level served payloads. Every other DTO is reached transitively from these
# (in field-definition order, so the walk is deterministic).
_ROOTS: Final[tuple[type[BaseModel], ...]] = (
    ReplayView,
    AgentMemoryView,
    BeliefFrameView,
    EvalCostSummaryView,
    PublicResultsView,
    SuspicionGraphView,
    RubricView,
    TournamentEvalReport,
)

# Shared string-literal sets hoisted to named TS aliases (kept identical to the
# prior hand-authored file so existing component imports — e.g. ``PlayerRole``
# in MemoryPanel — keep resolving). A field whose ``Literal[...]`` value set
# matches one of these emits the alias name; any other literal is inlined.
_ENUM_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    "PlayerRole": ("CREWMATE", "IMPOSTOR"),
    "CurrentAction": (
        "IDLE",
        "MOVING",
        "TASK",
        "KILL",
        "VENT",
        "REPORT",
        "SABOTAGE",
        "PRETEND_TASK",
        "EMERGENCY",
        "REPAIR",
        "BLOCKED",
    ),
    "Winner": ("CREWMATES", "IMPOSTORS"),
    "TriggerKind": ("body", "emergency"),
    "MeetingOutcome": ("EJECTED", "SKIPPED"),
    "ContradictionKind": (
        "alibi_conflict",
        "alibi_vs_sighting",
        "alibi_vs_physical",
        "vent_sighting",
    ),
    "TurnKind": ("opening", "reply", "opt_in"),
    "TurnAnnotationLabel": (
        "invalid_accusation_target",
        "invalid_alibi_subject",
        "invalid_corroboration_supports",
        "fabricated_opening",
        "opening_degraded_unsure",
    ),
}
_ENUM_BY_VALUES: Final[dict[frozenset[str], str]] = {
    frozenset(values): name for name, values in _ENUM_ALIASES.items()
}

# Discriminated-union aliases: named unions of interfaces (each member carries a
# literal ``type``). A model-union field whose member set matches one emits the
# alias name (so the union is referenced by name and narrows in TS).
_UNION_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    "TickEventView": (
        "KillEventView",
        "ReportBodyEventView",
        "SabotageEventView",
        "TaskCompletedEventView",
        "MeetingTriggeredEventView",
        "VentEventView",
    ),
    "ObservationClaimView": (
        "SawPlayerView",
        "CompletedTaskObsView",
        "FoundBodyObsView",
        "SawVentObservationView",
        "SawKillObservationView",
        "WhereaboutsClaimView",
        "SawMoveObservationView",
        "TaskActivityAccountView",
    ),
    "StatementClaimView": (
        "AlibiClaimView",
        "AccusationClaimView",
        "CorroborationClaimView",
    ),
}
_UNION_BY_MEMBERS: Final[dict[frozenset[str], str]] = {
    frozenset(members): name for name, members in _UNION_ALIASES.items()
}

# Eval report sub-tree cut points: emitted as fixed stubs instead of expanding
# the full internal meeting graph (see module docstring). Bodies match the prior
# hand-authored contract; ``Winner`` is the only enum they reference.
_PROVENANCE_STUB_FIELDS: Final[str] = (
    '  agent_factory_kind?: "scripted" | "experimental" | "custom" | null;\n'
    "  experiment_config?: ExperimentConfigView | null;\n"
    "  substrate_flags?: Record<string, boolean> | null;\n"
    "  tactical_policy?: TacticalPolicyView | null;\n"
    "  crew_tactical_policy?: TacticalPolicyView | null;"
)

_STUB_BODIES: Final[dict[str, str]] = {
    "GameReport": (
        "  game_id: string;\n"
        "  seed: number;\n"
        "  winner: Winner | null;\n"
        "  reason: string;\n"
        "  final_tick: number | null;\n"
        '  completion_status?: "completed" | "aborted" | "tick_limited" | "unfinished";\n'
        "  outcome_verified?: boolean;\n" + _PROVENANCE_STUB_FIELDS
    ),
    "TournamentReport": (
        "  format_version: number;\n  games: GameReport[];\n  seeds_used: number[];\n"
        "  provenance_groups?: ReportProvenanceGroup[] | null;"
    ),
    "ReportProvenanceGroup": _PROVENANCE_STUB_FIELDS + "\n  game_ids: string[];",
}


@dataclasses.dataclass
class _Generator:
    """Collects models reachable from the roots and renders them to TypeScript."""

    models: dict[str, type[BaseModel]] = dataclasses.field(default_factory=dict)
    used_enums: set[str] = dataclasses.field(default_factory=set)
    used_unions: set[str] = dataclasses.field(default_factory=set)
    used_stubs: set[str] = dataclasses.field(default_factory=set)

    def register(self, model: type[BaseModel]) -> None:
        name = model.__name__
        if name in _STUB_BODIES:
            self.used_stubs.add(name)
            return
        if name in self.models:
            return
        self.models[name] = model
        for field in model.model_fields.values():
            # Resolve nested models in field order (deterministic walk).
            self._ts_type(field.annotation)

    def _ts_type(self, annotation: Any) -> str:
        tp = _strip_annotated(annotation)
        if tp is type(None):
            return "null"
        if tp is str:
            return "string"
        if tp in (int, float):
            return "number"
        if tp is bool:
            return "boolean"

        origin = get_origin(tp)
        if origin is Literal:
            return self._ts_literal(get_args(tp))
        if origin in (Union, _pytypes.UnionType):
            return self._ts_union(get_args(tp))
        if origin in (tuple, list):
            elem = get_args(tp)[0]
            inner = self._ts_type(elem)
            return f"({inner})[]" if "|" in inner else f"{inner}[]"
        if origin in (dict, Mapping) or origin is _abc_mapping():
            value = get_args(tp)[1]
            return f"Record<string, {self._ts_type(value)}>"
        if isinstance(tp, type) and issubclass(tp, BaseModel):
            self.register(tp)
            return tp.__name__
        raise TypeError(f"unsupported annotation for TS codegen: {annotation!r}")

    def _ts_literal(self, values: tuple[Any, ...]) -> str:
        alias = (
            _ENUM_BY_VALUES.get(frozenset(values))
            if all(isinstance(value, str) for value in values)
            else None
        )
        if alias is not None:
            self.used_enums.add(alias)
            return alias
        return " | ".join(
            _ts_string_literal(value) if isinstance(value, str) else json.dumps(value)
            for value in values
        )

    def _ts_union(self, args: tuple[Any, ...]) -> str:
        model_members = [
            a.__name__ for a in args if isinstance(a, type) and issubclass(a, BaseModel)
        ]
        if len(model_members) > 1:
            alias = _UNION_BY_MEMBERS.get(frozenset(model_members))
            for arg in args:
                if isinstance(arg, type) and issubclass(arg, BaseModel):
                    self.register(arg)
            members = (
                list(_UNION_ALIASES[alias]) if alias is not None else model_members
            )
            rendered = " | ".join(members)
            if alias is not None:
                self.used_unions.add(alias)
                rendered = alias
            extra = [self._ts_type(a) for a in args if a is type(None)]
            return " | ".join([rendered, *extra])
        parts: list[str] = []
        for arg in args:
            rendered = self._ts_type(arg)
            if rendered not in parts:
                parts.append(rendered)
        return " | ".join(parts)

    def render_interface(self, model: type[BaseModel]) -> str:
        lines = [f"export interface {model.__name__} {{"]
        for name, field in model.model_fields.items():
            # FastAPI serializes responses by_alias, so the wire key is the
            # serialization_alias when set (e.g. view_model_version ->
            # viewModelVersion, the contract name); fall back to the field name.
            wire_name = field.serialization_alias or name
            # Older static bundles omit these additive reader fields.
            optional = (
                "?"
                if (model.__name__, name)
                in {
                    ("ReplayMetadataView", "completion_status"),
                    ("ReplayMetadataView", "outcome_verified"),
                    ("ReplayMetadataView", "agent_factory_kind"),
                    ("ReplayMetadataView", "experiment_config"),
                    ("ReplayMetadataView", "substrate_flags"),
                    ("ReplayMetadataView", "tactical_policy"),
                    ("ReplayMetadataView", "crew_tactical_policy"),
                    ("GateView", "threshold_source"),
                    ("PublicResultsView", "provenance_groups"),
                    ("ObservationReferenceView", "source_tick"),
                    ("ObservationReferenceView", "observation_phase"),
                    ("ObservationReferenceView", "observation_order"),
                    ("ObservationReferenceView", "observer_room"),
                    ("ObservationReferenceView", "observer_in_vent"),
                    ("ReplayView", "llm_bodies_included"),
                    ("AgentMemoryView", "observation_references"),
                    ("AgentMemoryView", "investigation_plan"),
                    ("AgentTickStateView", "investigation_plan"),
                    ("ExperimentConfigView", "investigation_version"),
                    ("ExperimentConfigView", "contextual_self_report_version"),
                }
                else ""
            )
            lines.append(f"  {wire_name}{optional}: {self._ts_type(field.annotation)};")
        lines.append("}")
        return "\n".join(lines)


def _abc_mapping() -> Any:
    import collections.abc

    return collections.abc.Mapping


def _strip_annotated(annotation: Any) -> Any:
    if get_origin(annotation) is Annotated:
        return get_args(annotation)[0]
    return annotation


def _ts_string_literal(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


_HEADER: Final[str] = """\
// GENERATED FILE — do not edit by hand.
//
// Regenerate with:  uv run python scripts/gen_frontend_types.py
//
// Source of truth: the Pydantic view-model DTOs in `api/schemas.py` (plus the
// served eval report `eval.meeting_quality.TournamentEvalReport`). The
// versioned view-model contract (DESIGN.md §7) ends the hand-mirror drift:
// `scripts/check.sh` regenerates this file and fails CI on any difference, so
// the TS types cannot drift from the Python contract.
//
// Pydantic serializes `tuple[X, ...]` as JSON arrays (typed `X[]`) and
// `X | None` as `X | null` (a required-but-nullable field, matching
// tsconfig `exactOptionalPropertyTypes`). Discriminated unions carry the
// literal `type` discriminant so a `switch (e.type)` narrows to the member.
"""


def _render_version_constant() -> str:
    """Emit the view-model contract version as a runtime TS constant (Task 19.24).

    The one VALUE in an otherwise type-only module. It exists so the client's
    runtime rejection of a mismatched ``viewModelVersion`` compares against the
    server's own constant rather than a hand-copied literal: bump
    ``api.schemas.VIEW_MODEL_VERSION`` and the only way to get a green CI is to
    regenerate, which moves both sides at once.
    """

    return (
        "// The view-model contract version (`api.schemas.VIEW_MODEL_VERSION`,\n"
        "// DESIGN.md §7) the server stamps on every payload that carries one.\n"
        "// `src/api/client.ts` rejects unsupported versions and checks the\n"
        "// explicitly compatible historical version's audio before use.\n"
        f"export const VIEW_MODEL_VERSION = {_ts_string_literal(VIEW_MODEL_VERSION)};"
    )


def render_types() -> str:
    gen = _Generator()
    for root in _ROOTS:
        gen.register(root)

    sections: list[str] = [_HEADER.rstrip("\n"), _render_version_constant()]

    # Enum aliases (only the ones actually referenced), in config order.
    enum_lines = [
        f"export type {name} = "
        + " | ".join(_ts_string_literal(v) for v in _ENUM_ALIASES[name])
        + ";"
        for name in _ENUM_ALIASES
        if name in gen.used_enums
    ]
    if enum_lines:
        sections.append("\n".join(enum_lines))

    # Interfaces, in deterministic encounter order.
    for model in gen.models.values():
        sections.append(gen.render_interface(model))

    # Union aliases (referenced), in config order.
    union_lines = [
        f"export type {name} = " + " | ".join(_UNION_ALIASES[name]) + ";"
        for name in _UNION_ALIASES
        if name in gen.used_unions
    ]
    if union_lines:
        sections.append("\n".join(union_lines))

    # Eval report stubs, in config order. A stub referenced only inside another
    # stub's (hand-written) body — e.g. `GameReport` inside `TournamentReport` —
    # is never hit by the model walk, so close over body references. The bodies
    # reference `Winner`, pulled in via `ReplayMetadataView.winner` already.
    needed_stubs = set(gen.used_stubs)
    changed = True
    while changed:
        changed = False
        for name, body in _STUB_BODIES.items():
            if name in needed_stubs:
                continue
            if any(name in _STUB_BODIES[used] for used in needed_stubs):
                needed_stubs.add(name)
                changed = True
    sections.extend(
        f"export interface {name} {{\n{_STUB_BODIES[name]}\n}}"
        for name in _STUB_BODIES
        if name in needed_stubs
    )

    return "\n\n".join(sections) + "\n"


# ---------------------------------------------------------------------------
# Fidelity fixture — the codegen FIDELITY gate (DoD). A REAL served payload
# (from the loader) type-checks against the generated types, and the
# discriminated unions narrow EXHAUSTIVELY. Compiled by `npm run tsc:check`
# (tsconfig `include: ["src"]`); never imported by app code, so vite does not
# bundle it.
# ---------------------------------------------------------------------------


def _real_replay_payload() -> str:
    """A real ReplayView, JSON-serialized, from a tiny deterministic game.

    Built through the production ``ReplayLog`` writer + ``ReplayLoader`` (not a
    hand-authored literal) so the fixture round-trips an ACTUAL served payload —
    the whole DTO tree, with every additive Phase-12 projection — through the
    generated types.
    """

    import json

    from engine.tick import advance_tick
    from engine.world import load_canonical_map
    from orchestrator.replay import ReplayLog
    from orchestrator.seeder import seed_initial_state
    from tests.api.fixtures.sample_replay import finish_replay_with_kills

    from api.replay_loader import ReplayLoader

    with tempfile.TemporaryDirectory(prefix="ailibi-fidelity-") as tmp:
        game_map = load_canonical_map()
        path = Path(tmp) / "replay-seed-0.jsonl"
        log = ReplayLog(path=path, game_id="headless-seed-0")
        state = seed_initial_state(
            seed=0, game_map=game_map, num_players=4, num_impostors=1
        )
        for _ in range(3):
            input_tick = state.tick
            state, _events = advance_tick(state, [], game_map=game_map)
            log.record_tick(input_tick, [], state)
        finish_replay_with_kills(log, state, game_map)
        loader = ReplayLoader(path.parent)
        replay = loader.load_replay("headless-seed-0")
    # by_alias mirrors FastAPI's response serialization (so the fixture key is
    # ``viewModelVersion``, matching the generated interface).
    payload = replay.model_dump(mode="json", by_alias=True)
    # ``created_at`` is the replay file's mtime (env/clock-dependent) — normalize
    # it so the fidelity fixture is byte-deterministic across regenerations (the
    # drift gate compares the committed file to a fresh render). The field is
    # ``str | None``, so null is a valid placeholder.
    payload["metadata"]["created_at"] = None
    return json.dumps(payload, indent=2, sort_keys=True)


def _narrow_block(union: str, members: tuple[str, ...]) -> str:
    cases = "\n".join(
        f"    case {_member_literal(member)}:\n      return e satisfies {member};"
        for member in members
    )
    return (
        f"// Exhaustive narrowing of {union}: each discriminant resolves to its\n"
        f"// member (the `satisfies`), and an unhandled member is a compile error\n"
        f"// (the `never` default) — the codegen's discriminated-union fidelity.\n"
        f"export function _narrow_{union}(e: {union}): {union} {{\n"
        f"  switch (e.type) {{\n"
        f"{cases}\n"
        f"    default: {{\n"
        f"      const _exhaustive: never = e;\n"
        f"      return _exhaustive;\n"
        f"    }}\n"
        f"  }}\n"
        f"}}"
    )


# The discriminant literal for each union member, read off the model's ``type``
# field so the fixture cannot drift from the schema.
def _member_literal(member: str) -> str:
    model = getattr(schemas, member)
    field = model.model_fields["type"]
    (value,) = get_args(_strip_annotated(field.annotation))
    return _ts_string_literal(str(value))


def render_fidelity() -> str:
    imports = sorted({"ReplayView", *_UNION_ALIASES})
    member_imports = sorted(
        {member for members in _UNION_ALIASES.values() for member in members}
    )
    import_line = (
        "import type {\n  "
        + ",\n  ".join([*imports, *member_imports])
        + ',\n} from "./api";'
    )
    payload = _real_replay_payload()
    narrows = "\n\n".join(
        _narrow_block(union, members) for union, members in _UNION_ALIASES.items()
    )
    return (
        "// GENERATED FILE — do not edit by hand.\n"
        "//\n"
        "// Codegen FIDELITY gate (Task 12.2, DESIGN.md §7). A REAL served\n"
        "// ReplayView payload (produced by the loader) type-checks against the\n"
        "// generated `./api` types, and every discriminated union narrows\n"
        "// exhaustively. `npm run tsc:check` compiles this (tsconfig includes\n"
        "// `src`); it is never imported by app code, so vite does not bundle it.\n"
        "//\n"
        "// Regenerate with: uv run python scripts/gen_frontend_types.py\n"
        "\n"
        f"{import_line}\n"
        "\n"
        f"export const _fidelityReplay: ReplayView = {payload};\n"
        "void _fidelityReplay;\n"
        "\n"
        f"{narrows}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the committed files are stale (no write)",
    )
    args = parser.parse_args()

    rendered = {_OUT_TYPES: render_types(), _OUT_FIDELITY: render_fidelity()}

    if args.check:
        stale = [
            path
            for path, content in rendered.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            names = ", ".join(str(p.relative_to(_REPO_ROOT)) for p in stale)
            print(
                f"Generated frontend types are stale: {names}. "
                "Run: uv run python scripts/gen_frontend_types.py",
                file=sys.stderr,
            )
            return 1
        return 0

    for path, content in rendered.items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(_REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
