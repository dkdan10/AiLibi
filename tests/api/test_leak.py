"""Leak tests for the spectator DTO surface (DESIGN.md §1.3, §7).

The spectator API is a privileged surface: it intentionally exposes role,
kill attribution, and impostor-only state (that is what makes a replay
watchable). These tests do NOT redact those fields. Their job is to assert
every DTO field is *intentional* and to keep ``api/schemas.py`` from
accidentally embedding an engine / meetings / orchestrator internal type
(``WorldState``, ``ReplayEntry``, ``MeetingResult``, ...), which would couple
the frontend to engine shape and re-introduce leakage paths via copy-paste.

Implementation note — why AST, not a raw source grep. The DoD sketch suggests
``inspect.getsource(api.schemas) | grep`` for forbidden type names. A literal
whole-source substring grep is unworkable with this DTO inventory: several
required DTO *names* contain a forbidden name as a prefix (``StatementView``
contains ``Statement``; ``MeetingTriggeredEventView`` contains
``MeetingTrigger``; ``AlibiClaimView`` contains ``AlibiClaim``), and the DoD
also requires each DTO docstring to *name* the source type it shadows. So we
parse the module with ``ast`` and inspect only field/alias *annotations*
(never docstrings or class names), tokenized on identifier boundaries. This is
the "import_linter-style assertion" the DoD offers as the alternative to grep,
and it is both stricter (catches ``x: WorldState``) and free of false
positives.
"""

from __future__ import annotations

import ast
import inspect
import re
from typing import Final

import pydantic

import api.schemas
from eval.meeting_quality import TournamentEvalReport

# The concrete spectator DTOs. Adding or removing a DTO must update BOTH this
# set AND ``api.schemas.__all__`` AND the "Public types introduced" section of
# the PR — keeping accidental surface changes visible in review. The three
# discriminated-union aliases (TickEventView, ObservationClaimView,
# StatementClaimView) are public importable symbols but are intentionally not
# inventoried here: they are compositions of the DTOs below, not standalone
# DTOs.
EXPECTED_DTOS: Final[frozenset[str]] = frozenset(
    {
        "PositionView",
        "SizeView",
        "RoomView",
        "VentView",
        "EdgeView",
        "MapLayoutView",
        "PlayerView",
        "AgentTickStateView",
        "KillEventView",
        "ReportBodyEventView",
        "SabotageEventView",
        "TaskCompletedEventView",
        "MeetingTriggeredEventView",
        "TickView",
        "SawPlayerView",
        "CompletedTaskObsView",
        "FoundBodyObsView",
        "AlibiClaimView",
        "AccusationClaimView",
        "CorroborationClaimView",
        "ReportView",
        "StatementView",
        "ContradictionView",
        "BallotView",
        "LLMCallView",
        "MeetingView",
        "BeliefEntryView",
        "AgentMemoryView",
        "SuspicionEntryView",
        "SuspicionGraphView",
        "ReplayMetadataView",
        "FailedCallView",
        "FailedCallEvalView",
        "ReplayView",
        "EvalCostSummaryView",
    }
)

# Internal engine / meetings / orchestrator types that must never appear in a
# DTO field annotation. DTOs *shadow* these (re-declare the spectator-relevant
# slice); they must not embed them.
FORBIDDEN_TYPES: Final[frozenset[str]] = frozenset(
    {
        "WorldState",
        "PlayerState",
        "BodyState",
        "TaskState",
        "SabotageState",
        "ReplayEntry",
        "MeetingReplayEntry",
        "LLMCallRecord",
        "GameEndReplayEntry",
        "FailedCallReplayEntry",
        "MeetingResult",
        "MeetingTrigger",
        "Action",
        "Statement",
        "ReportDocument",
        "VoteBallot",
        "ContradictionRef",
        "AlibiClaim",
        "AccusationClaim",
        "CorroborationClaim",
    }
)

# Backend packages the DTO module must never import from. ``api/schemas.py``
# needs only ``pydantic`` + stdlib typing.
FORBIDDEN_IMPORT_ROOTS: Final[frozenset[str]] = frozenset(
    {
        "engine",
        "observation",
        "orchestrator",
        "meetings",
        "agents",
        "llm",
        "eval",
    }
)

# Discriminated-union aliases: public + importable, but excluded from __all__.
_UNION_ALIASES: Final[frozenset[str]] = frozenset(
    {"TickEventView", "ObservationClaimView", "StatementClaimView"}
)

_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _schemas_ast() -> ast.Module:
    return ast.parse(inspect.getsource(api.schemas))


def _imported_roots() -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(_schemas_ast()):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def _annotation_identifiers() -> set[str]:
    """Identifiers used in field/alias annotations (not docstrings or names).

    Walks every ``AnnAssign`` (class fields + the module-level union-alias
    declarations) and every ``Assign`` value, unparses the annotation/value
    expression, and tokenizes it on identifier boundaries. Docstrings (bare
    string ``Expr`` statements) and ``ClassDef`` names are never read.
    """

    identifiers: set[str] = set()
    for node in ast.walk(_schemas_ast()):
        if isinstance(node, ast.AnnAssign):
            identifiers.update(_IDENTIFIER.findall(ast.unparse(node.annotation)))
            if node.value is not None:
                identifiers.update(_IDENTIFIER.findall(ast.unparse(node.value)))
        elif isinstance(node, ast.Assign) and node.value is not None:
            identifiers.update(_IDENTIFIER.findall(ast.unparse(node.value)))
    return identifiers


def test_dto_inventory_matches_expected() -> None:
    actual = frozenset(api.schemas.__all__)
    assert actual == EXPECTED_DTOS, (
        "api.schemas.__all__ drifted from the documented DTO inventory. "
        "Adding/removing a DTO requires updating EXPECTED_DTOS in this test, "
        "api.schemas.__all__, AND the PR's 'Public types introduced' section."
    )


def test_schemas_imports_no_backend_package() -> None:
    leaked = _imported_roots() & FORBIDDEN_IMPORT_ROOTS
    assert not leaked, (
        f"api/schemas.py imports from backend package(s) {sorted(leaked)}; "
        "DTOs must shadow internal types, not import them."
    )


def test_no_forbidden_types_in_field_annotations() -> None:
    leaked = _annotation_identifiers() & FORBIDDEN_TYPES
    assert not leaked, (
        f"api/schemas.py references internal type(s) {sorted(leaked)} in a field "
        "annotation. DTOs must shadow these, not embed them."
    )


def test_every_inventoried_dto_is_a_frozen_model() -> None:
    for name in EXPECTED_DTOS:
        obj = getattr(api.schemas, name)
        assert isinstance(obj, type) and issubclass(obj, pydantic.BaseModel), (
            f"{name} is inventoried but is not a Pydantic model."
        )
        assert obj.model_config.get("frozen") is True, f"{name} must be frozen."
        assert obj.model_config.get("extra") == "forbid", (
            f"{name} must forbid extra fields."
        )


def test_union_aliases_are_importable_but_not_inventoried() -> None:
    for name in _UNION_ALIASES:
        assert hasattr(api.schemas, name), f"{name} must be importable."
        assert name not in api.schemas.__all__, (
            f"{name} is a union alias and must stay out of __all__."
        )


# ---------------------------------------------------------------------------
# Eval-report surface firewall (Task 6.5, audit B-B-2 = D-D-2; DESIGN.md §11.2,
# §11.3)
# ---------------------------------------------------------------------------
#
# The structural firewall above pins only ``api.schemas``. The Phase 5 eval
# route ``GET /eval/tournament-report`` serves
# ``eval.meeting_quality.TournamentEvalReport`` — its three-level report tree
# (tournament -> game -> meeting), the reused meeting/replay leaf types, and the
# four §11.3 metric reports — which all ride entirely outside that guard. These
# tests extend the firewall to that surface: a snapshot of its recursive field
# set plus an assertion that no engine-state field is reachable, so a future
# engine-state field added to any leaf type fails loudly here instead of
# silently widening the served payload (B-B-2 = D-D-2).

# Engine-internal / determinism fields that must never surface on the eval
# report. ``state_hash`` (per-tick replay record) and ``state_hash_before`` /
# ``state_hash_after`` (per-meeting record) exist on the replay *records* but are
# intentionally dropped by the eval ``MeetingReport`` / ``GameReport`` shadows;
# ``rng_state`` stands in for any future engine-state field name. None is
# reachable today — these assertions keep it that way.
FORBIDDEN_EVAL_ENGINE_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "state_hash",
        "state_hash_before",
        "state_hash_after",
        "rng_state",
    }
)

# Snapshot of every field name reachable in the recursive JSON schema of
# ``TournamentEvalReport``. Adding a field anywhere in the tree (the report
# wrapper, a leaf DTO, or a metric report) changes this set and trips
# ``test_eval_report_field_set_snapshot`` — forcing an explicit, reviewed update
# rather than silently growing the served eval payload (D-D-2). Regenerate only
# after confirming the new field is intentional and exposes no engine/role state.
#
# ``raw_response`` and ``prompt_length`` appear here because they live on the
# underlying ``orchestrator.replay.FailedCallReplayEntry`` data model. The eval
# ROUTE redacts them on the served payload via ``api.schemas.FailedCallEvalView``
# (covered end-to-end in ``test_eval_routes.py``); this structural snapshot is
# over the report TYPE, which still carries them, so they are listed.
#
# The Phase 7 W0.3 meeting-rate fields (``meeting_rate``, ``meetings_total``,
# ``games_total``, ``games_with_meeting``, ``body_report_meetings``,
# ``emergency_meetings``) come from ``eval.meeting_quality.MeetingRateReport``.
# They are pure aggregate counts + a rate (no roles, transcripts, or engine
# types), so they expose no engine/role state and stay out of
# ``FORBIDDEN_EVAL_ENGINE_FIELDS``.
#
# The Phase 7 W0.5 (Task 7.11) eval-reporting-hardening fields are likewise pure
# derived counts / flags / rates with no engine/role state, so they too stay out
# of ``FORBIDDEN_EVAL_ENGINE_FIELDS``:
#   * ``ejection_accuracy``, ``vote_correctness_small_n``,
#     ``contradictions_flagged_but_ignored`` — ``eval.vote_correctness``.
#   * ``accusation_claim_populated_bins`` / ``accusation_claim_low_power`` /
#     ``vote_ballot_populated_bins`` / ``vote_ballot_low_power`` —
#     ``eval.accusation_calibration``.
#   * ``skipped_meetings`` / ``ejected_meetings`` —
#     ``eval.meeting_quality.MeetingRateReport``.
# (The ``first_zero_impostor_tick == game_over_tick`` self-check lives in
# ``eval.win_condition_selfcheck`` and is NOT a served report field, so it does
# not appear in this snapshot.)
EXPECTED_EVAL_REPORT_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "accusation_calibration",
        "accusation_claim_bins",
        "accusation_claim_ece",
        "accusation_claim_low_power",
        "accusation_claim_populated_bins",
        "accusation_claim_total",
        "actual_impostor_rate",
        "against",
        "agent_id",
        "alibi_fabrication",
        "ballots",
        "bin_index",
        "body_of",
        "body_report_meetings",
        "by_model",
        "call_kind",
        "claims",
        "co_present",
        "confidence",
        "considered_alternatives",
        "contradiction_id",
        "contradictions",
        "contradictions_flagged_but_ignored",
        "cost",
        "cost_dashboard",
        "cost_usd",
        "count",
        "crewmate_ejections",
        "description",
        "ejected_meetings",
        "ejected_player_id",
        "ejection_accuracy",
        "emergency_meetings",
        "error_message",
        "error_type",
        "event_a_id",
        "event_b_id",
        "evidence",
        "evidence_backed_impostor_ejections",
        "failed_calls",
        "final_tick",
        "format_version",
        "free_text",
        "from_tick",
        "game_count",
        "game_id",
        "games",
        "games_total",
        "games_with_meeting",
        "hi",
        "impostor_ejections",
        "impostor_hits",
        "input_tokens",
        "kind",
        "llm_calls",
        "lo",
        "mean_confidence",
        "mean_cost_per_game",
        "meeting_id",
        "meeting_rate",
        "meetings",
        "meetings_total",
        "midpoint",
        "model",
        "n_bins",
        "observations",
        "on_tick",
        "outcome",
        "output_tokens",
        "per_prompt_version",
        "primary_reason_id",
        "prompt",
        "prompt_length",
        "prompt_versions",
        "rationale_text",
        "raw_response",
        "reason",
        "replay_ref",
        "report",
        "reports",
        "response_text",
        "roles",
        "room",
        "round_index",
        "seed",
        "seeds_used",
        "skipped_meetings",
        "speaker",
        "statement_id",
        "statements",
        "subject",
        "subjects",
        "supports",
        "survival_rate",
        "survived",
        "target",
        "task_id",
        "template_name",
        "tick",
        "to_tick",
        "total_cost_usd",
        "total_ejections",
        "total_impostor_alibis",
        "total_input_tokens",
        "total_output_tokens",
        "transcript",
        "trigger",
        "triggered_by",
        "type",
        "version",
        "vote_ballot_bins",
        "vote_ballot_ece",
        "vote_ballot_low_power",
        "vote_ballot_populated_bins",
        "vote_ballot_total",
        "vote_correctness",
        "vote_correctness_rate",
        "vote_correctness_small_n",
        "voter",
        "winner",
    }
)


def _recursive_field_names(model: type[pydantic.BaseModel]) -> frozenset[str]:
    """Every property name reachable in ``model``'s recursive JSON schema.

    ``model_json_schema`` inlines every nested model into ``$defs`` with a
    ``properties`` block per object type; collecting those keys across the whole
    tree yields the recursive field set. Dynamic mapping value-types
    (``Mapping[str, X]``) render as ``additionalProperties`` with no
    ``properties`` block, so their runtime keys never pollute the set — only
    declared field names are collected.
    """

    names: set[str] = set()
    _collect_field_names(model.model_json_schema(), names)
    return frozenset(names)


def _collect_field_names(node: object, acc: set[str]) -> None:
    if isinstance(node, dict):
        props = node.get("properties")
        if isinstance(props, dict):
            acc.update(str(key) for key in props)
        for value in node.values():
            _collect_field_names(value, acc)
    elif isinstance(node, list):
        for item in node:
            _collect_field_names(item, acc)


def test_eval_report_surface_exposes_no_engine_state_field() -> None:
    leaked = _recursive_field_names(TournamentEvalReport) & FORBIDDEN_EVAL_ENGINE_FIELDS
    assert not leaked, (
        f"TournamentEvalReport (the /eval/tournament-report surface) reaches "
        f"engine-state field(s) {sorted(leaked)}. The eval report must shadow "
        "engine/determinism state, not embed it; drop the field from the leaf "
        "DTO or its eval shadow."
    )


def test_eval_report_field_set_snapshot() -> None:
    actual = _recursive_field_names(TournamentEvalReport)
    added = sorted(actual - EXPECTED_EVAL_REPORT_FIELDS)
    removed = sorted(EXPECTED_EVAL_REPORT_FIELDS - actual)
    assert actual == EXPECTED_EVAL_REPORT_FIELDS, (
        "The recursive field set of TournamentEvalReport changed "
        f"(added={added}, removed={removed}). A field was added to the eval "
        "report, one of its leaf DTOs, or a metric report. Confirm the new field "
        "is intentional and exposes no engine/role state, then update "
        "EXPECTED_EVAL_REPORT_FIELDS (and FORBIDDEN_EVAL_ENGINE_FIELDS if it is "
        "engine-internal). This tripwire is the durable value (D-D-2)."
    )
