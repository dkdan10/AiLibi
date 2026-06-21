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
required DTO *names* contain a forbidden name as a prefix
(``MeetingTriggeredEventView`` contains ``MeetingTrigger``; ``AlibiClaimView``
contains ``AlibiClaim``; ``AccusationClaimView`` contains ``AccusationClaim``),
and the DoD
also requires each DTO docstring to *name* the source type it shadows. So we
parse the module with ``ast`` and inspect only field/alias *annotations*
(never docstrings or class names), tokenized on identifier boundaries. This is
the "import_linter-style assertion" the DoD offers as the alternative to grep,
and it is both stricter (catches ``x: WorldState``) and free of false
positives.
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
import re
from pathlib import Path
from typing import Final, cast

import pydantic
import pytest

import api.schemas
from api.replay_loader import ReplayLoader
from engine.entities import SabotageState
from engine.world import Map, load_canonical_map
from eval.leak_test import (
    JsonValue,
    _assert_no_role_bearing_values,
    _format_json_path,
    _walk_json,
)
from eval.meeting_quality import TournamentEvalReport
from observation.service import ObservationService
from tests._helpers.world_state import scripted_initial_world_state

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
        # Phase-12 (Task 12.3) per-tick As-agent fog projection (DESIGN.md §3.2,
        # §7). The container plus its firewall-clean sub-views (the agent-facing
        # shapes — no role / killed_by / colour):
        "AgentVisibilityView",
        "VisiblePlayerView",
        "VisibleBodyView",
        "AudibleEventView",
        "KillEventView",
        "ReportBodyEventView",
        "SabotageEventView",
        "TaskCompletedEventView",
        "MeetingTriggeredEventView",
        # Phase-12 (Task 12.2) additive per-tick projections (DESIGN.md §7):
        "VentEventView",
        "BodyView",
        "SabotageDetailView",
        "AdvantageView",
        "TickView",
        "SawPlayerView",
        "CompletedTaskObsView",
        "FoundBodyObsView",
        "AlibiClaimView",
        "AccusationClaimView",
        "CorroborationClaimView",
        "TurnView",
        "ContradictionView",
        "BallotView",
        "LLMCallView",
        # Phase-12 per-meeting §4.6 gate verdict (DESIGN.md §3.4, §4.6):
        "GateView",
        "MeetingView",
        "BeliefEntryView",
        # Phase-12 per-meeting belief × truth hero surface (DESIGN.md §3.3):
        "BeliefErrorView",
        "BeliefFrameView",
        "AgentMemoryView",
        "SuspicionEntryView",
        "SuspicionGraphView",
        "ReplayMetadataView",
        "FailedCallView",
        "FailedCallEvalView",
        "ReplayView",
        "EvalCostSummaryView",
        # Phase-12 per-set rubric surface (DESIGN.md §3.1, §7):
        "RubricGameView",
        "RubricView",
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
# ``rendered_vote_max`` (Task 10.12) is the rendered §4.6 max suspicion a
# DEFAULTED vote prompt computed over the voter's living ejection candidates,
# persisted onto ``FailedCallReplayEntry`` so a defaulted ballot's MUST-vote /
# MUST-skip verdict is classifiable (audit H-H-2). It is a single quantized
# float with no role / player-id / transcript content — the same rendered
# suspicion magnitude the report already surfaces elsewhere — so it exposes no
# engine/role state and stays out of ``FORBIDDEN_EVAL_ENGINE_FIELDS``.
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
#
# The Phase 8 (Task 8.7/8.10) meeting accusation-chain reshape replaced the
# ``MeetingTranscript`` ``(reports, statements)`` pair with one ordered ``turns``
# list of ``meetings.schemas.MeetingTurn``. That dropped ``reports`` /
# ``statements`` / ``statement_id`` / ``round_index`` from the recursive set and
# added ``turns`` / ``turn_id`` / ``turn_index`` / ``turn_kind`` / ``reply_to``.
# All five are pure transcript-structure fields (no roles or engine state), so
# they stay out of ``FORBIDDEN_EVAL_ENGINE_FIELDS``. ``speaker`` / ``observations``
# / ``claims`` / ``target`` / ``agent_id`` survive (now reached via ``MeetingTurn``
# / ``VoteBallot`` / ``LLMCallRecord`` rather than the old report-statement split).
#
# The Task 8.17 kill-gifted accounting (DESIGN.md §3.5; audit gp-4) adds three
# per-game ``GameReport`` facts (``kill_gifted`` / ``instances_dropped`` /
# ``instances_complete_at_win``) and three ``TournamentReport`` roll-ups
# (``kill_gifted_wins`` / ``instances_dropped_total`` /
# ``mean_instances_complete_at_win``). All six are pure derived counts / flags /
# a rate with no engine, role, or determinism state, so they stay out of
# ``FORBIDDEN_EVAL_ENGINE_FIELDS`` (the §3.5 drop magnitude is gameplay
# accounting, not engine internals the firewall guards).
#
# The Task 9.6 metric hygiene (DESIGN.md §11.3, §5.5; audit gp-2) adds the
# ``conversion`` block (``eval.meeting_quality.ConversionReport``): the two
# Wave-1 conversion leads (``ejection_accuracy`` — already in this set — plus
# ``impostor_accused_meetings`` / ``impostor_accused_conversions`` /
# ``impostor_accused_conversion_rate``) and the SKIP sentinels
# (``skip_ballots`` / ``correct_skip_ballots`` / ``missed_skip_ballots`` /
# ``unclassified_skip_ballots`` / ``missed_skip_impostor_voters`` /
# ``missed_skip_teammate_coerced`` / ``missed_skip_invalid_target`` /
# ``threshold_inversions``). All are pure aggregate counts and rates (no
# roles, transcripts, or engine types), so they stay out of
# ``FORBIDDEN_EVAL_ENGINE_FIELDS``.
#
# The Task 10.4 Phase-10 gate metrics (DESIGN.md §11.3; audit
# audit-2026-06-10-1820 gp-7) add the ``gate_metrics`` block
# (``eval.meeting_quality.GateMetricsReport``): the nested
# ``genuine_class_conversion`` PRIMARY gate
# (``eval.vote_correctness.GenuineClassConversionReport``: ``supplied`` /
# ``converted`` / ``conversion_rate`` / ``note`` — the ``note`` is a pinned
# documentation literal, not data), the lost-opening / cap-default split
# (``lost_opening_accusations`` / ``cap_defaulted_turns``), and the D-D-2
# deception-control survival partition (``accused_impostor_events`` /
# ``accused_impostor_survivals`` / ``survivals_rendered_met`` /
# ``survivals_sheltered_sub_gate`` / ``survivals_unevidenced``). All are pure
# aggregate counts, rates, and a pinned string (no roles, transcripts, or
# engine types), so they stay out of ``FORBIDDEN_EVAL_ENGINE_FIELDS``.
EXPECTED_EVAL_REPORT_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "accusation_calibration",
        "accusation_claim_bins",
        "accusation_claim_ece",
        "accusation_claim_low_power",
        "accusation_claim_populated_bins",
        "accusation_claim_total",
        "accused_impostor_events",
        "accused_impostor_survivals",
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
        "cap_defaulted_turns",
        "claims",
        "co_present",
        "confidence",
        "considered_alternatives",
        "contradiction_id",
        "contradictions",
        "contradictions_flagged_but_ignored",
        "conversion",
        "conversion_rate",
        "converted",
        "correct_skip_ballots",
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
        "gate_metrics",
        "genuine_class_conversion",
        "hi",
        "impostor_accused_conversion_rate",
        "impostor_accused_conversions",
        "impostor_accused_meetings",
        "impostor_ejections",
        "impostor_hits",
        "input_tokens",
        "instances_complete_at_win",
        "instances_dropped",
        "instances_dropped_total",
        "kill_gifted",
        "kill_gifted_wins",
        "kind",
        "llm_calls",
        "lo",
        "lost_opening_accusations",
        "mean_confidence",
        "mean_cost_per_game",
        "mean_instances_complete_at_win",
        "meeting_id",
        "meeting_rate",
        "meetings",
        "meetings_total",
        "midpoint",
        "missed_skip_ballots",
        "missed_skip_impostor_voters",
        "missed_skip_invalid_target",
        "missed_skip_teammate_coerced",
        "model",
        "n_bins",
        "note",
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
        "reply_to",
        "rendered_vote_max",
        "report",
        "response_text",
        "roles",
        "room",
        "seed",
        "seeds_used",
        "skip_ballots",
        "skipped_meetings",
        "speaker",
        "subject",
        "subjects",
        "supplied",
        "supports",
        "survival_rate",
        "survivals_rendered_met",
        "survivals_sheltered_sub_gate",
        "survivals_unevidenced",
        "survived",
        "target",
        "task_id",
        "template_name",
        "threshold_inversions",
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
        "turn_id",
        "turn_index",
        "turn_kind",
        "turns",
        "type",
        "unclassified_skip_ballots",
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


# ---------------------------------------------------------------------------
# Packet-API role-invariance (Task 11.6, DESIGN.md §1.3, §8.3)
# ---------------------------------------------------------------------------
#
# The structural guards above pin the spectator DTO surface. This complements
# them on the agent-facing packet API: ``ObservationService.build_packet`` must
# project the public GlobalView repair channel (``sabotage_repair_rooms`` /
# ``sabotage_is_gating``, Task 11.5) identically for every role, so the crew
# repair routing (Task 11.6) reads a role-blind target with no engine coupling.


def test_global_view_repair_channel_is_role_invariant_through_packet_api(
    tmp_path: Path,
) -> None:
    # Build packets for the crewmates AND the impostor on the SAME sabotage-active
    # world state (the scripted roster is 3 crew + 1 impostor); the two new
    # GlobalView fields must be byte-identical across roles (public / role-blind)
    # and carry no role-bearing substring.
    game_map = load_canonical_map()
    state = dataclasses.replace(
        scripted_initial_world_state(seed=11),
        sabotage=SabotageState(
            kind="reactor", remaining_ticks=5, affected_rooms=(), active=True
        ),
    )
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )

    channels: set[tuple[tuple[str, ...], bool]] = set()
    roles_seen: set[str] = set()
    for player_id, player in state.players.items():
        if not player.alive:
            continue
        packet = service.build_packet(
            world_state=state, agent_id=player_id, engine_events=[]
        )
        _assert_no_role_bearing_values(cast(JsonValue, packet.model_dump(mode="json")))
        roles_seen.add(packet.self_state.role)
        channels.add(
            (
                packet.global_state.sabotage_repair_rooms,
                packet.global_state.sabotage_is_gating,
            )
        )
    service.close()

    # Both roles were exercised, and they share one identical repair channel.
    assert roles_seen == {"CREWMATE", "IMPOSTOR"}
    assert channels == {(("REACTOR", "ENGINEERING"), True)}


# ---------------------------------------------------------------------------
# As-agent fog projection leak test (Task 12.3; DESIGN.md §3.2 fog, §1.3, §7)
# ---------------------------------------------------------------------------
#
# The per-tick per-living-agent visibility projection (``AgentVisibilityView``)
# lets the spectator view the replay *As* one agent — simulating the firewall
# rather than inheriting it. This mirrors ``eval/leak_test.py``'s recursive
# hidden-field walk on the SERVED projection across the committed 9p2i set and,
# additionally, cross-checks the served fog against the ground truth the same
# payload carries (every agent's room per tick) so it can never expose a player,
# body, or field the agent could not have perceived at that tick: other-room
# presence, role, ``fellow_impostor_ids``, kill attribution.

_NINE_P_TWO_I: Final[Path] = (
    Path(__file__).resolve().parents[2] / "replays" / "samples" / "9p2i"
)

# Field NAMES the As-agent fog must never carry (the recursive walk, mirroring
# eval/leak_test.py). The visual/audio channels structurally exclude them, so a
# hit means the projection regressed — e.g. re-exposed the privileged spectator
# ``BodyView.killed_by`` or ``PlayerView.role`` / ``color``, or any self-channel
# field. ``player_id`` is the engine body-state name the agent-facing BodyView
# renames to ``victim_id``.
_FOG_FORBIDDEN_FIELD_NAMES: Final[frozenset[str]] = frozenset(
    {
        "role",
        "killed_by",
        "kill_attribution",
        "player_id",
        "fellow_impostor_ids",
        "color",
        "cooldown",
        "own_kill",
        "pending_task_id",
    }
)


def _assert_fog_hides_hidden_fields(dump: JsonValue) -> None:
    """Recursive hidden-field-NAME walk over one fog frame (mirrors eval/leak_test)."""

    for path, _ in _walk_json(dump):
        if not path:
            continue
        field_name = path[-1]
        if isinstance(field_name, str) and field_name in _FOG_FORBIDDEN_FIELD_NAMES:
            raise AssertionError(
                f"As-agent fog leaked hidden field {field_name!r} at "
                f"{_format_json_path(path)}"
            )


def _seen_rooms(
    observer_room: str,
    observer_role: str,
    sabotage_kind: str | None,
    game_map: Map,
) -> set[str]:
    """The rooms an observer in ``observer_room`` can see (the engine rule).

    Mirrors ``engine.visibility._resolve_observer_visibility_mode`` +
    ``visible_rooms_for_player`` using the REAL map adjacency + sabotage config
    (never a hardcoded topology), so the cross-room check cannot drift from the
    map. Asymmetric visibility (Task 13.8): at BASE visibility a CREWMATE is
    room-only while an IMPOSTOR keeps same-room-and-adjacent; an ACTIVE sabotage
    degrade (e.g. lights -> same_room_only) collapses EVERYONE to same-room-only.
    """

    base = game_map.visibility_defaults.base
    mode = base
    if sabotage_kind is not None:
        mode = game_map.sabotages[sabotage_kind].affected_visibility
    if mode == base and observer_role != "IMPOSTOR":
        mode = "same_room_only"
    if mode == "same_room_only":
        return {observer_room}
    return {observer_room, *game_map.room_neighbors(observer_room)}


def test_as_agent_fog_leaks_no_unseen_player_body_or_field() -> None:
    """The As-agent fog never exposes an entity/field the agent could not perceive.

    Mirrors ``eval/leak_test.py`` for the spectator's per-tick visibility
    projection across the committed 9p2i set: a recursive hidden-field walk + the
    role-bearing-value walk on every living agent's served field of view, plus a
    cross-room presence check against the ground truth the same payload carries.
    The visual field is held to strict co-location; witnessed kill/vent actions
    and audio cues are the firewall's witness / audio channels (gated by
    ``ObservationService.build_packet``, which ``eval/leak_test.py`` validates),
    so they are field-hygiene-checked, not re-derived against co-location (a
    witness may move the same tick). Coverage counters assert the run actually
    exercised every channel — else the test proves nothing.
    """

    if not _NINE_P_TWO_I.is_dir():
        pytest.skip("committed 9p2i sample set not present")

    game_map = load_canonical_map()
    loader = ReplayLoader(replay_dir=_NINE_P_TWO_I)
    games = visual = witnessed = bodies = audibles = 0
    for meta in loader.list_replays():
        games += 1
        replay = loader.load_replay(meta.game_id)
        # The spectator roster exposes role (privileged); asymmetric visibility
        # (Task 13.8) makes the engine sight rule role-dependent, so the
        # cross-room expectation must key on each observer's role.
        role_by_player = {player.agent_id: player.role for player in replay.players}
        for tick in replay.ticks:
            room_by_player = {a.agent_id: a.room_id for a in tick.agent_states}
            alive = {a.agent_id for a in tick.agent_states if a.is_alive}
            venting = {a.agent_id for a in tick.agent_states if a.is_venting}
            sabotage_kind = tick.sabotage.kind if tick.sabotage is not None else None
            for state in tick.agent_states:
                fog = state.visibility
                if fog is None:
                    # Only a DEAD agent lacks a field of view.
                    assert not state.is_alive, (
                        f"living {state.agent_id} has no fog at tick {tick.tick}"
                    )
                    continue
                assert state.is_alive
                observer_room = room_by_player[state.agent_id]
                assert observer_room is not None
                seen = _seen_rooms(
                    observer_room,
                    role_by_player[state.agent_id],
                    sabotage_kind,
                    game_map,
                )

                fog_dump = cast(JsonValue, fog.model_dump(mode="json"))
                _assert_fog_hides_hidden_fields(fog_dump)
                _assert_no_role_bearing_values(fog_dump)

                served_ids: set[str] = set()
                for vp in fog.visible_players:
                    assert set(vp.model_dump().keys()) == {"id", "room", "action"}
                    assert vp.id != state.agent_id  # never self
                    served_ids.add(vp.id)
                    if vp.action in ("kill", "vent"):
                        # Witness channel: the agent saw the ACT (build_packet's
                        # witness gate, validated by eval/leak_test.py), so it is
                        # field-hygiene-checked only, not co-location-derived.
                        witnessed += 1
                        continue
                    # Pure visual field: genuinely co-visible — in a seen room,
                    # alive, not vented, at the room ground truth reports.
                    visual += 1
                    assert vp.room in seen, (
                        f"fog shows {vp.id} in unseen {vp.room} to {state.agent_id}"
                    )
                    assert room_by_player[vp.id] == vp.room
                    assert vp.id in alive
                    assert vp.id not in venting

                # No UNDER-report either: every co-visible peer is present (as a
                # plain sighting or a co-located actor), so the fog is the agent's
                # FULL field of view, not a leak-trimmed subset that masks a bug.
                expected_visual = {
                    pid
                    for pid in alive
                    if pid != state.agent_id
                    and pid not in venting
                    and room_by_player[pid] in seen
                }
                assert expected_visual <= served_ids

                for vb in fog.visible_bodies:
                    assert set(vb.model_dump().keys()) == {"id", "room", "victim_id"}
                    # Bodies have no witness channel — they come purely from the
                    # visibility solve, so a visible body's room is ALWAYS in seen.
                    assert vb.room in seen, (
                        f"fog shows a body in unseen {vb.room} to {state.agent_id}"
                    )
                    bodies += 1

                for ae in fog.audible_events:
                    assert set(ae.model_dump().keys()) == {"kind", "room"}
                    assert ae.kind in ("vent_use_heard", "sabotage_alarm")
                    audibles += 1

    assert games > 0, "expected committed 9p2i replays"
    # The run actually exercised every fog channel (else it proves nothing).
    assert visual > 0 and witnessed > 0 and bodies > 0 and audibles > 0, (
        f"under-covered: visual={visual} witnessed={witnessed} "
        f"bodies={bodies} audibles={audibles}"
    )
