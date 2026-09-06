"""Recorded money survives rejected outcomes without entering verified win rates."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from api.replay_loader import ReplayLoader
from engine.world import load_canonical_map
from eval.balance_eval import load_tournament_report
from eval.meeting_quality import build_tournament_eval_report
from llm.budget import GameBudget
from orchestrator.game import build_default_meeting_runner
from orchestrator.replay import compute_cost_usd
from orchestrator.seeder import seed_initial_state
from tests.api.fixtures.sample_replay import write_meeting_replay, write_sample_replay


@pytest.mark.parametrize("mutation", ["winner", "hash", "substrate"])
def test_invalid_claim_keeps_paid_recording_but_cannot_change_verified_split(
    tmp_path: Path,
    mutation: str,
) -> None:
    valid = tmp_path / "replay-seed-0.jsonl"
    bad = tmp_path / "replay-seed-1.jsonl"
    write_meeting_replay(valid, seed=0)
    write_meeting_replay(bad, seed=1)
    write_sample_replay(tmp_path / "replay-seed-2.jsonl", seed=2)
    cost = compute_cost_usd(bad)
    assert cost > 0
    rows = [json.loads(line) for line in bad.read_text().splitlines()]
    if mutation == "winner":
        rows[-1]["winner"] = "CREWMATES"
    elif mutation == "hash":
        rows[0]["state_hash"] = "0" * 64
    else:
        key = next(iter(rows[-1]["substrate_flags"]))
        rows[-1]["substrate_flags"][key] = False
    bad.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    loader = ReplayLoader(tmp_path)
    summary = loader.cost_summary()
    assert summary.total_cost_usd == pytest.approx(2 * cost)
    assert summary.decisive_split == {"CREWMATES": 0.0, "IMPOSTORS": 1.0}
    assert summary.accounting_complete
    assert summary.total_replays == 3
    assert summary.verified_replays == 2  # genuine winner plus an unfinished prefix
    assert summary.verified_outcomes == 1
    bad_row = summary.recordings[1]
    assert bad_row.total_cost_usd == pytest.approx(cost)
    assert bad_row.recorded_winner is not None
    assert bad_row.verified_winner is None
    assert bad_row.integrity_status == (
        "unverified" if mutation == "substrate" else "invalid"
    )
    assert summary.recordings[2].completion_status == "unfinished"
    if mutation == "substrate":
        # A deliberate analysis override does not weaken the accounting contract.
        override_loader = ReplayLoader(tmp_path, allow_substrate_mismatch=True)
        assert override_loader.cost_summary().verified_outcomes == 1
        assert (
            override_loader.load_replay("headless-seed-1").metadata.outcome_verified
            is False
        )
        assert (
            next(
                row
                for row in override_loader.list_replays()
                if row.game_id == "headless-seed-1"
            ).outcome_verified
            is False
        )


def test_real_adapter_abort_retains_budget_spend_without_certifying_outcome(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "scripts"))
    from tests.orchestrator.test_aborted_meeting_records import _InjectedProvider, _game

    path = tmp_path / "replay-seed-2026.jsonl"
    provider = _InjectedProvider(abort_at=2)
    budget = GameBudget(
        max_cost_usd=1.0, max_input_tokens=100_000, max_output_tokens=100_000
    )
    runner = build_default_meeting_runner(llm_client=provider, budget=budget)
    with pytest.raises(RuntimeError, match="injected transport failure"):
        _game(path, runner).run()
    (tmp_path / "roster.json").write_text(
        json.dumps({"num_players": 4, "num_impostors": 1, "tasks_per_crewmate": 2})
    )
    summary = ReplayLoader(tmp_path).cost_summary()
    assert summary.total_cost_usd == pytest.approx(compute_cost_usd(path))
    assert summary.total_cost_usd == pytest.approx(budget.snapshot().cost_usd)
    assert summary.total_cost_usd > 0
    assert summary.verified_replays == 1
    assert summary.verified_outcomes == 0
    assert summary.decisive_split == {}
    assert summary.recordings[0].completion_status == "aborted"


def test_unreadable_cost_is_explicitly_unknown(tmp_path: Path) -> None:
    (tmp_path / "replay-seed-0.jsonl").write_text("{broken\n")
    summary = ReplayLoader(tmp_path).cost_summary()
    assert not summary.accounting_complete
    assert summary.unreadable_replays == summary.invalid_replays == 1
    assert summary.total_replays == 0
    assert summary.recordings[0].total_cost_usd is None
    assert summary.recordings[0].completion_status is None


@pytest.mark.parametrize(
    "mutation",
    [
        "none",
        "winner",
        "tick",
        "status",
        "identity",
        "duplicate",
        "duplicate_groups_mismatch",
        "missing_source",
    ],
)
def test_api_rebinds_serialized_verification_to_actual_recording(
    tmp_path: Path,
    mutation: str,
) -> None:
    replay = tmp_path / "replay-seed-0.jsonl"
    write_meeting_replay(replay, seed=0)
    state = seed_initial_state(
        seed=0,
        game_map=load_canonical_map(),
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
    )
    report = build_tournament_eval_report(
        load_tournament_report(
            tmp_path,
            roles_by_seed={
                0: {pid: player.role for pid, player in state.players.items()}
            },
            tasks_per_crewmate=1,
        )
    )
    raw = report.model_dump(mode="json")
    game = raw["report"]["games"][0]
    game["outcome_verified"] = True  # an untrusted persisted assertion
    if mutation == "winner":
        game["winner"] = "CREWMATES"
    elif mutation == "tick":
        game["final_tick"] += 1
    elif mutation == "status":
        game["completion_status"] = "tick_limited"
        # This remains parseable; the source is what establishes stop status.
        game["outcome_verified"] = False
    elif mutation == "identity":
        game["replay_ref"] = "replay-seed-99.jsonl"
    elif mutation in ("duplicate", "duplicate_groups_mismatch"):
        raw["report"]["games"].append(dict(game))
        if mutation == "duplicate":
            # Keep the report shape consistent so this tests source identity,
            # independently of the aggregate-membership schema guard.
            raw["report"]["provenance_groups"][0]["game_ids"].append(game["game_id"])
    elif mutation == "missing_source":
        replay.unlink()
    (tmp_path / "tournament-eval-report.json").write_text(json.dumps(raw))
    if mutation == "duplicate_groups_mismatch":
        with pytest.raises(ValidationError, match="provenance groups disagree"):
            ReplayLoader(tmp_path).tournament_report()
        return
    served = ReplayLoader(tmp_path).tournament_report()
    assert all(
        item.outcome_verified == (mutation == "none") for item in served.report.games
    )
    assert served.report.games[0].cost == report.report.games[0].cost
    assert served.vote_correctness == report.vote_correctness
    if mutation == "status":
        assert served.report.games[0].completion_status == "completed"
    if mutation == "duplicate":
        assert served.report.provenance_groups is not None
        assert served.report.provenance_groups[0].game_ids == (
            game["game_id"],
            game["game_id"],
        )
