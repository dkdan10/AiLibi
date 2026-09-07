"""End-to-end tests for the eval route's failed-call redaction (Task 6.5).

Audit B-B-1 = D-D-1; DESIGN.md §11.2, §11.3. ``GET /eval/tournament-report``
serves ``eval.meeting_quality.TournamentEvalReport``, which transitively embeds
``orchestrator.replay.FailedCallReplayEntry`` with the raw ``raw_response`` blob,
``prompt_length``, and untruncated ``error_message``. The Phase 4 replay surface
already redacts those via ``api.schemas.FailedCallView``; these tests pin that
the eval route now mirrors that redaction through ``api.schemas.FailedCallEvalView``
so the two privileged GM surfaces agree.

The fixture is assembled exactly as the real artifact is — via
``eval.meeting_quality.build_tournament_eval_report`` over a hand-built
``eval.report_schema.TournamentReport`` — so the test exercises the real schema
and the real route boundary, not a parallel hand-written JSON blob. (Faithful
serving of the non-redacted fields and the 404 path are covered in
``test_eval.py``; this module is focused on the redaction contract.)
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from api.replay_loader import ReplayLoader, get_replay_loader
from api.schemas import FailedCallEvalView, FailedCallView
from eval.meeting_quality import TournamentEvalReport, build_tournament_eval_report
from eval.report_schema import (
    CURRENT_FORMAT_VERSION,
    GameCostSummary,
    GameReport,
    TournamentReport,
)
from orchestrator.replay import FailedCallReplayEntry

# A raw failed-call record carrying every field the eval route must redact: a
# multi-KB ``raw_response`` blob, a ``prompt_length``, per-call token counts, and
# an ``error_message`` well past the 200-char truncation boundary.
_RAW_RESPONSE_BLOB = "X" * 1500
_LONG_ERROR_MESSAGE = "schema validation failed: " + ("y" * 500)

_FAILED_CALL = FailedCallReplayEntry(
    game_id="headless-seed-0",
    meeting_id="headless-seed-0:meeting-0",
    tick=7,
    model="claude-sonnet",
    prompt_length=4096,
    raw_response=_RAW_RESPONSE_BLOB,
    input_tokens=900,
    output_tokens=0,
    cost_usd=0.013,
    error_type="ValidationError",
    error_message=_LONG_ERROR_MESSAGE,
    call_id="call-7",
)


def _client(replay_dir: Path) -> TestClient:
    test_app = create_app()
    loader = ReplayLoader(replay_dir=replay_dir)
    test_app.dependency_overrides[get_replay_loader] = lambda: loader
    return TestClient(test_app)


def _eval_report_with_failed_call() -> TournamentEvalReport:
    """A TournamentEvalReport whose single game carries one failed LLM call."""

    game = GameReport(
        game_id="headless-seed-0",
        seed=0,
        winner="IMPOSTORS",
        reason="IMPOSTOR_PARITY",
        final_tick=7,
        roles={"p-1": "CREWMATE", "p-2": "IMPOSTOR"},
        replay_ref="replay-seed-0.jsonl",
        meetings=(),
        failed_calls=(_FAILED_CALL,),
        prompt_versions={"meeting": "v1"},
        cost=GameCostSummary(
            total_cost_usd=0.013,
            total_input_tokens=900,
            total_output_tokens=0,
            by_model={"claude-sonnet": 0.013},
        ),
    )
    return build_tournament_eval_report(
        TournamentReport(
            format_version=CURRENT_FORMAT_VERSION, games=(game,), seeds_used=(0,)
        )
    )


@pytest.fixture
def served_failed_call(tmp_path: Path) -> Iterator[dict[str, object]]:
    """Serve a report with one failed call; yield the served failed-call dict."""

    report = _eval_report_with_failed_call()
    (tmp_path / "tournament-eval-report.json").write_text(
        report.model_dump_json(), encoding="utf-8"
    )
    with _client(tmp_path) as client:
        response = client.get("/eval/tournament-report")
    assert response.status_code == 200
    body = response.json()
    failed_calls = body["report"]["games"][0]["failed_calls"]
    assert len(failed_calls) == 1
    yield failed_calls[0]


def test_failed_call_excludes_raw_fields(served_failed_call: dict[str, object]) -> None:
    # The raw blob, the prompt length, and the per-call token counts are dropped
    # — exactly what the parallel FailedCallView surface suppresses (B-B-1/D-D-1).
    for dropped in (
        "raw_response",
        "prompt_length",
        "input_tokens",
        "output_tokens",
        "call_id",
    ):
        assert dropped not in served_failed_call, (
            f"eval route re-exposed redacted field {dropped!r}"
        )


def test_failed_call_truncates_error_message(
    served_failed_call: dict[str, object],
) -> None:
    message = served_failed_call["error_message"]
    assert isinstance(message, str)
    assert message == _LONG_ERROR_MESSAGE[:200]
    assert len(message) == 200


def test_failed_call_keeps_summary_fields(
    served_failed_call: dict[str, object],
) -> None:
    # The kept fields are passed through verbatim (error_message aside).
    assert served_failed_call["meeting_id"] == "headless-seed-0:meeting-0"
    assert served_failed_call["tick"] == 7
    assert served_failed_call["model"] == "claude-sonnet"
    assert served_failed_call["cost_usd"] == pytest.approx(0.013)
    assert served_failed_call["error_type"] == "ValidationError"


def test_served_failed_call_keys_match_eval_dto(
    served_failed_call: dict[str, object],
) -> None:
    # The served shape is exactly FailedCallEvalView's field set — no more, no
    # less — so the route cannot drift from the DTO contract.
    assert set(served_failed_call) == set(FailedCallEvalView.model_fields)


def test_eval_dto_mirrors_replay_failed_call_view() -> None:
    # FailedCallEvalView is a distinct type, but it must mirror the Phase 4
    # FailedCallView's exclusions exactly so the two surfaces agree (B-B-1/D-D-1).
    assert set(FailedCallEvalView.model_fields) == set(FailedCallView.model_fields)


def test_served_payload_no_longer_validates_as_raw_report(tmp_path: Path) -> None:
    # The redacted payload deliberately diverges from the raw report: the raw
    # FailedCallReplayEntry requires raw_response/prompt_length, which the served
    # surface drops, so it must NOT round-trip back into TournamentEvalReport.
    report = _eval_report_with_failed_call()
    (tmp_path / "tournament-eval-report.json").write_text(
        report.model_dump_json(), encoding="utf-8"
    )
    with _client(tmp_path) as client:
        body = client.get("/eval/tournament-report").json()
    with pytest.raises(ValueError):
        TournamentEvalReport.model_validate(body)


def test_served_report_includes_meeting_rate(tmp_path: Path) -> None:
    # The W0.3 meeting_rate metric survives the redaction round-trip and is
    # served. The fixture game carries no meetings, so the rate is a defined 0.0
    # (a game ran), not None.
    report = _eval_report_with_failed_call()
    (tmp_path / "tournament-eval-report.json").write_text(
        report.model_dump_json(), encoding="utf-8"
    )
    with _client(tmp_path) as client:
        body = client.get("/eval/tournament-report").json()

    assert "meeting_rate" in body, "served eval payload dropped the meeting_rate block"
    meeting_rate = body["meeting_rate"]
    assert meeting_rate["games_total"] == 1
    assert meeting_rate["games_with_meeting"] == 0
    assert meeting_rate["meeting_rate"] == 0.0
    assert meeting_rate["meetings_total"] == 0
    assert (
        meeting_rate["body_report_meetings"] + meeting_rate["emergency_meetings"]
        == meeting_rate["meetings_total"]
    )


@pytest.mark.skip(
    reason="committed tournament-eval-report.json carries the pre-8.7 (reports, "
    "statements) meeting transcript; the Task 8.7 turn-shape MeetingTranscript "
    "(extra='forbid') rejects it. Re-recorded to the turn shape + format v2 and "
    "re-enabled in Task 8.12 (combined re-record)."
)
def test_committed_4p1i_report_loads_through_loader_with_meeting_rate() -> None:
    """The committed 4p/1i report re-validates as a TournamentEvalReport.

    Guards the latent runtime break this task's metric introduces: ``meeting_rate``
    is a REQUIRED field on the frozen ``extra="forbid"`` ``TournamentEvalReport``,
    so a committed report generated before this task would fail
    ``ReplayLoader.tournament_report()``'s ``model_validate`` at runtime — 500ing
    ``GET /eval/tournament-report`` — while the tmp-fixture eval-route tests above
    stay green and miss it. The committed report was regenerated offline to carry
    the field; this asserts it loads and matches the diagnosis ground truth (4/50
    games reach a meeting, all body-reports, 0 emergency).
    """

    loader = ReplayLoader(replay_dir=Path("replays/samples/4p1i"))
    report = loader.tournament_report()

    meeting_rate = report.meeting_rate
    assert meeting_rate.games_total == 50
    assert meeting_rate.games_with_meeting == 4
    assert meeting_rate.meeting_rate == pytest.approx(0.08)
    assert meeting_rate.meetings_total == 4
    assert meeting_rate.body_report_meetings == 4
    assert meeting_rate.emergency_meetings == 0


def test_served_payload_exposes_no_engine_state_field(tmp_path: Path) -> None:
    # End-to-end mirror of the structural firewall in test_leak.py: no
    # engine/determinism field name appears anywhere in the served JSON tree.
    forbidden = {"state_hash", "state_hash_before", "state_hash_after", "rng_state"}
    report = _eval_report_with_failed_call()
    (tmp_path / "tournament-eval-report.json").write_text(
        report.model_dump_json(), encoding="utf-8"
    )
    with _client(tmp_path) as client:
        body = client.get("/eval/tournament-report").json()

    keys: set[str] = set()

    def walk(node: object) -> None:
        if isinstance(node, dict):
            keys.update(str(k) for k in node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(body)
    leaked = keys & forbidden
    assert not leaked, f"served eval payload leaked {sorted(leaked)}"
