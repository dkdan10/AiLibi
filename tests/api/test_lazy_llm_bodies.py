"""Model text is omitted on the wire while full detail and accounting survive."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from api.replay_loader import ReplayLoader, get_replay_loader
from api.schemas import ReplayView
from llm.budget import GameBudget
from orchestrator.game import build_default_meeting_runner
from orchestrator.replay import LLMCallRecord
from tests.api.fixtures.sample_replay import write_meeting_replay, write_sample_replay

_PROMPT = "DISTINCTIVE_PROMPT_BODY_" * 300
_RESPONSE = "DISTINCTIVE_RESPONSE_BODY_" * 200


def _assert_no_bodies(payload: bytes) -> None:
    assert _PROMPT.encode() not in payload
    assert _RESPONSE.encode() not in payload
    parsed = json.loads(payload)
    assert parsed["llm_bodies_included"] is False
    for meeting in parsed["meetings"]:
        for call in meeting["llm_calls"]:
            assert call["prompt_text"] == call["response_text"] == ""


def _record(path: Path, seed: int) -> str:
    expected = write_meeting_replay(
        path,
        seed=seed,
        llm_calls=(
            LLMCallRecord(
                call_kind="meeting",
                model="injected",
                prompt=_PROMPT,
                response_text=_RESPONSE,
                input_tokens=91,
                output_tokens=17,
                cost_usd=0.125,
                agent_id="p-2",
            ),
        ),
    )
    return expected.meeting_id


def test_live_lean_projection_preserves_full_default_detail_and_accounting(
    tmp_path: Path,
) -> None:
    meeting_id = _record(tmp_path / "replay-seed-0.jsonl", 0)
    loader = ReplayLoader(tmp_path)
    app = create_app(replay_dir=tmp_path)
    app.dependency_overrides[get_replay_loader] = lambda: loader
    with TestClient(app) as client:
        lean = client.get("/replays/headless-seed-0?include_llm_bodies=false")
        full = client.get("/replays/headless-seed-0")
        explicit = client.get("/replays/headless-seed-0?include_llm_bodies=true")
        detail = client.get(f"/replays/headless-seed-0/meetings/{meeting_id}")
    assert lean.status_code == full.status_code == detail.status_code == 200
    _assert_no_bodies(lean.content)
    with pytest.raises(AssertionError):
        _assert_no_bodies(full.content)
    assert full.content == explicit.content
    assert len(lean.content) < len(full.content) * 0.75
    original, projected = full.json(), lean.json()
    assert original["llm_bodies_included"] is True
    original["llm_bodies_included"] = False
    for meeting in original["meetings"]:
        for call in meeting["llm_calls"]:
            call["prompt_text"] = call["response_text"] = ""
    assert projected == original
    assert detail.json() == full.json()["meetings"][0]
    call = detail.json()["llm_calls"][0]
    assert (call["prompt_text"], call["response_text"]) == (_PROMPT, _RESPONSE)
    assert (call["input_tokens"], call["output_tokens"], call["cost_usd"]) == (
        91,
        17,
        0.125,
    )
    assert loader.cost_summary().total_cost_usd == 0.125
    # Returning a projection cannot poison the full-view cache.
    assert (
        loader.load_replay("headless-seed-0").meetings[0].llm_calls[0].prompt_text
        == _PROMPT
    )


def test_no_meeting_and_legacy_view_remain_readable(tmp_path: Path) -> None:
    write_sample_replay(tmp_path / "replay-seed-2.jsonl", seed=2)
    loader = ReplayLoader(tmp_path)
    lean = loader.load_replay("headless-seed-2", include_llm_bodies=False)
    assert lean.meetings == ()
    assert not lean.llm_bodies_included
    legacy = loader.load_replay("headless-seed-2").model_dump()
    legacy.pop("llm_bodies_included")
    assert ReplayView.model_validate(legacy).llm_bodies_included


def test_projection_keeps_identity_isolated_and_missing_detail_is_404(
    tmp_path: Path,
) -> None:
    parent = tmp_path / "sets"
    for name, seed in (("first", 0), ("second", 1)):
        directory = parent / name
        directory.mkdir(parents=True)
        _record(directory / f"replay-seed-{seed}.jsonl", seed)
    with TestClient(create_app(replay_dir=parent)) as client:
        for name, seed in (("first", 0), ("second", 1)):
            response = client.get(
                f"/replays/headless-seed-{seed}?set={name}&include_llm_bodies=false"
            )
            assert response.status_code == 200
            assert response.json()["metadata"]["seed"] == seed
            _assert_no_bodies(response.content)
        assert (
            client.get(
                "/replays/headless-seed-0?set=second&include_llm_bodies=false"
            ).status_code
            == 404
        )
        assert (
            client.get(
                "/replays/headless-seed-0/meetings/missing?set=first"
            ).status_code
            == 404
        )


def test_paid_failure_prefix_keeps_accounting_in_both_projections(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "scripts"))
    from tests.orchestrator.test_aborted_meeting_records import _InjectedProvider, _game

    provider = _InjectedProvider(abort_at=3, invalid_at=frozenset({1}))
    budget = GameBudget(
        max_cost_usd=1.0, max_input_tokens=100_000, max_output_tokens=100_000
    )
    path = tmp_path / "replay-seed-2026.jsonl"
    runner = build_default_meeting_runner(llm_client=provider, budget=budget)
    with pytest.raises(RuntimeError, match="injected transport failure"):
        _game(path, runner).run()
    (tmp_path / "roster.json").write_text(
        json.dumps({"num_players": 4, "num_impostors": 1, "tasks_per_crewmate": 2})
    )
    loader = ReplayLoader(tmp_path)
    full = loader.load_replay("headless-seed-2026")
    lean = loader.load_replay("headless-seed-2026", include_llm_bodies=False)
    assert lean.metadata == full.metadata
    assert lean.failed_calls == full.failed_calls
    assert lean.failed_calls
    assert lean.metadata.completion_status == "aborted"
    assert not lean.metadata.outcome_verified
    assert loader.cost_summary().total_cost_usd == pytest.approx(
        budget.snapshot().cost_usd
    )
    assert budget.snapshot().cost_usd > 0
