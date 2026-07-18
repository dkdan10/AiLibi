"""Task 17.16 — the evidence-gated default flip, pinned on the RULED (FAIL) branch.

Locked decision 2 (tasks/phase-17.md) flips the default mover iff the
re-selected champion PASSES the baseline-5 referee (supply floors +
population-relative conversion + geomean) AND retains its win edge at the
17.14 real-LLM finalist eval. The committed evidence
(``training/reports/results-finalist-eval.jsonl``;
``training/reports/report-finalist-eval.md`` §3.a/§3.1a/§4) reads FAIL on
both finalists:

* ``utility-es`` — win edge YES (0.52 vs the same-seed FSM 0.36, Δ +0.16)
  but referee FAIL on two supply gauges: ``flags_per_meeting`` 0.4255 <
  floor 0.50279 (90/179) and ``testimony_backed_conversion`` 0.3585 < its
  population-relative derived floor 0.5601 (the 64/135 = 0.4741 pin, lifted
  by the starved flag supply); ``witnessed_event_rate`` 0.2078 clears its
  0.03448 (7/203) floor.
* ``policy-es`` — referee PASS (mean 48.20, every floor clears) but win
  edge NO (0.02, Δ −0.34 — the vent-tell collapse).

Neither satisfies referee-PASS AND retained-win-edge, so the ruled branch
is FAIL: the scripted FSM stays the DEFAULT mover, the champion stays
OPT-IN (the 15.20/15.21 posture), and nothing swaps — the re-selected
finalist (``utility-es``, sha ``6d327dcb…``) is byte-identical to the
already-committed champion artifact (deterministic re-training, 17.12 §0),
so the FAIL branch's referee-dominance swap clause is a no-op by identity.

These are the 17.16 re-pins that the default PROVABLY does not move: the
ruling is re-derived from the committed evidence bytes (never from quoted
prose alone), the default-SELECTOR surfaces (the ``run_tournament`` CLI
default and the orchestrator's default factory selection) still select the
scripted FSM, an unstamped/absent-stamp replay still resolves to the FSM
stamp (``FSM_DEFAULT_POLICY_ID`` and the absent-stamp fallback
interpretation untouched, so recorded history is never re-read as champion
games), and the champion opt-in surface still loads the identical
sha-coherent artifact the evidence evaluated.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any, Final

import pytest

import run_tournament as rt
from _manifest_writer import _render_policy, parse_manifest
from agents.tactical.learned.factory import (
    CHAMPION_ANCHOR_POLICY,
    CHAMPION_METHOD,
    CHAMPION_POLICY_ID,
    LearnedAgentFactory,
)
from agents.tactical.learned.forward import ENCODER_VERSION
from agents.tactical.learned.weights import committed_weights_sha256
from eval import balance_eval
from orchestrator.game import (
    AgentFactory,
    TacticalAgent,
    build_default_agent_factory,
)
from orchestrator.replay import (
    FSM_DEFAULT_POLICY_ID,
    fsm_default_tactical_policy_stamp,
    read_tactical_policy_stamp,
)

# The committed 17.14 evidence (50-seed real-LLM finalist eval, baseline 5).
_RESULTS_PATH: Final[Path] = Path("training/reports/results-finalist-eval.jsonl")

# The committed baseline-5 scripted comparator: seeds 0-49 at the same
# substrate, recorded fsm-default (the 16.17 close re-record).
_SAMPLES_9P2I: Final[Path] = Path("replays/samples/9p2i")

# The committed champion digest (audits/audit-phase-15-pause.md decision 1) —
# unchanged by this task's FAIL ruling, and identical to the re-selected
# 17.12 finalist artifact (the no-op swap).
_CHAMPION_SHA: Final[str] = (
    "6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0"
)


def _finalist_rows() -> dict[str, dict[str, Any]]:
    """The committed 17.14 evidence rows, keyed by entrant."""

    rows: dict[str, dict[str, Any]] = {}
    for line in _RESULTS_PATH.read_text(encoding="utf-8").splitlines():
        row: dict[str, Any] = json.loads(line)
        rows[row["entrant"]] = row
    return rows


def _fsm_comparator_win_rate() -> float:
    """The same-seed scripted-FSM impostor win rate, from committed provenance.

    Derived from the canonical 9p2i MANIFEST's ``winner`` column (18/50 =
    0.36) rather than restated as a bare literal, after asserting every row's
    ``policy`` cell attributes the scripted FSM — the house win-edge
    convention's comparator (report-finalist-eval.md §3.a).
    """

    manifest = parse_manifest(
        (_SAMPLES_9P2I / "MANIFEST.md").read_text(encoding="utf-8")
    )
    assert len(manifest) == 50
    assert {row.policy for row in manifest.values()} == {FSM_DEFAULT_POLICY_ID}
    impostor_wins = sum(1 for row in manifest.values() if row.winner == "IMPOSTORS")
    return impostor_wins / len(manifest)


# -- the evidence gate: locked decision 2 reads FAIL --------------------------


def test_locked_decision_2_reads_fail_on_the_committed_17_14_evidence() -> None:
    """Neither finalist clears referee-PASS AND retained-win-edge (the FAIL branch).

    Re-derives the locked-decision-2 verdict from the committed evidence
    bytes: the referee verdict from each row's ``watchability.referee_passed``
    (baseline-5 floors), the win edge from each row's
    ``core.impostor_win_rate`` against the same-seed FSM comparator. The
    figures the report quotes are pinned exactly, so the ruling this task
    implements cannot drift from the bytes it cites — if a future re-record
    flips either conjunct, this pin fails and the default flip must be
    re-ruled, never silently inherited.
    """

    rows = _finalist_rows()
    assert set(rows) == {"utility-es", "policy-es"}
    fsm_rate = _fsm_comparator_win_rate()
    assert fsm_rate == pytest.approx(0.36)

    for row in rows.values():
        # The stamp-proof precondition: all 50 recordings named the loaded
        # candidate (stamp == committed sidecar) before any cell is trusted.
        assert row["stamp_verified_games"] == 50
        assert row["stamp_equals_committed_sha256"] is True
        assert row["validity_gate"]["passed"] is True
        assert row["watchability"]["baseline_id"] == "baseline-5"
        referee_passed = row["watchability"]["referee_passed"]
        retained_edge = row["core"]["impostor_win_rate"] > fsm_rate
        # Locked decision 2's AND-criterion — FAIL for every finalist.
        assert not (referee_passed and retained_edge)

    # utility-es: win edge YES, referee FAIL (the starved conversion economy).
    utility = rows["utility-es"]
    assert utility["core"]["impostor_win_rate"] == pytest.approx(0.52)
    assert utility["core"]["impostor_win_rate"] - fsm_rate == pytest.approx(0.16)
    assert utility["watchability"]["referee_passed"] is False
    assert utility["watchability"]["mean_score"] == pytest.approx(41.47, abs=0.01)
    gauges = {
        gauge["name"]: gauge for gauge in utility["watchability"]["supply_gauges"]
    }
    witnessed = gauges["witnessed_event_rate"]
    assert witnessed["passed"] is True
    assert witnessed["floor"] == pytest.approx(7 / 203)
    assert witnessed["measured"] == pytest.approx(0.2078, abs=1e-4)
    flags = gauges["flags_per_meeting"]
    assert flags["passed"] is False
    assert flags["floor"] == pytest.approx(90 / 179)
    assert flags["measured"] == pytest.approx(0.4255, abs=1e-4)
    conversion = gauges["testimony_backed_conversion"]
    assert conversion["passed"] is False
    assert conversion["measured"] == pytest.approx(0.3585, abs=1e-4)
    # The population-relative floor RISES to 0.5601 because the starved flag
    # supply lifts it: floor = min(1.0, pin × (flags_floor / measured_flags))
    # with the 64/135 baseline-5 conversion pin (16.11; 17.11 re-pins).
    assert conversion["floor"] == pytest.approx(0.5601, abs=1e-4)
    assert conversion["floor"] == pytest.approx(
        min(1.0, (64 / 135) * ((90 / 179) / flags["measured"]))
    )

    # policy-es: referee PASS on every floor, win edge NO (competitively
    # annihilated — the crew converts the vent tell, which is why the referee
    # is read WITH the win edge, never alone).
    policy = rows["policy-es"]
    assert policy["watchability"]["referee_passed"] is True
    assert policy["watchability"]["mean_score"] == pytest.approx(48.20, abs=0.01)
    gauges = {gauge["name"]: gauge for gauge in policy["watchability"]["supply_gauges"]}
    witnessed = gauges["witnessed_event_rate"]
    assert witnessed["passed"] is True
    assert witnessed["floor"] == pytest.approx(7 / 203)
    assert witnessed["measured"] == pytest.approx(0.1194, abs=1e-4)
    flags = gauges["flags_per_meeting"]
    assert flags["passed"] is True
    assert flags["floor"] == pytest.approx(90 / 179)
    assert flags["measured"] == pytest.approx(1.7748, abs=1e-4)
    conversion = gauges["testimony_backed_conversion"]
    assert conversion["passed"] is True
    assert conversion["measured"] == pytest.approx(0.9417, abs=1e-4)
    # The same population-relative derivation, EASED by the flooded flag
    # supply: the derived floor drops to 0.1343.
    assert conversion["floor"] == pytest.approx(0.1343, abs=1e-4)
    assert conversion["floor"] == pytest.approx(
        min(1.0, (64 / 135) * ((90 / 179) / flags["measured"]))
    )
    assert policy["core"]["impostor_win_rate"] == pytest.approx(0.02)
    assert policy["core"]["impostor_win_rate"] - fsm_rate == pytest.approx(-0.34)


# -- on FAIL the default provably does not move -------------------------------


def test_default_selector_surfaces_still_select_the_scripted_fsm(
    tmp_path: Path,
) -> None:
    """The default-SELECTOR surfaces a PASS would have flipped are unmoved.

    The two surfaces locked decision 2 names: (1) the ``run_tournament``
    default — ``--agent-factory`` still defaults to ``fsm-default``, the
    choices vocabulary is unchanged, and the default resolves to no factory /
    no auto-stamp (``main`` then omits the ``agent_factory`` kwarg, the
    pre-15.21 byte-identity); (2) the orchestrator's default factory
    selection — ``run_tournament_eval``'s omitted-kwarg default is still
    :func:`orchestrator.game.build_default_agent_factory`, which builds the
    bare scripted :class:`TacticalAgent` (exact type, never a learned
    wrapper) for both roles.
    """

    args = rt._parse_args(["--output-dir", str(tmp_path)])
    assert args.agent_factory == FSM_DEFAULT_POLICY_ID
    assert rt._AGENT_FACTORY_CHOICES == (
        FSM_DEFAULT_POLICY_ID,
        rt.LEARNED_CHAMPION_FACTORY_ID,
    )
    assert rt._resolve_agent_factory(FSM_DEFAULT_POLICY_ID) == (None, None)

    parameter = inspect.signature(balance_eval.run_tournament_eval).parameters[
        "agent_factory"
    ]
    assert parameter.default is None  # omitted -> build_default_agent_factory
    factory = build_default_agent_factory()
    impostor = factory("p-0", "IMPOSTOR")
    crewmate = factory("p-1", "CREWMATE")
    assert type(impostor) is TacticalAgent
    assert type(crewmate) is TacticalAgent


def test_unflagged_run_selects_the_default_factory_and_records_no_stamp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unflagged run still uses the scripted default and records absent-stamp bytes.

    Spies on ``eval.balance_eval.build_default_agent_factory`` (delegating to
    the real one) to prove the orchestrator's default factory selection is
    what an unflagged tournament actually exercises, then asserts the
    RECORDED BYTES: every ``game_over`` row omits the ``tactical_policy`` key
    entirely (the pre-15.9 byte-identity), the stamp reads back absent, and
    the absent stamp renders as the ``fsm-default`` MANIFEST label — the flip
    contract's invariant that future defaults may only change what runs
    SELECT, never how recorded bytes are READ.
    """

    calls: list[None] = []

    def spying_default_factory() -> AgentFactory:
        calls.append(None)
        return build_default_agent_factory()

    monkeypatch.setattr(
        balance_eval, "build_default_agent_factory", spying_default_factory
    )

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--start-seed",
            "0",
            "--output-dir",
            str(tmp_path),
            "--max-ticks",
            "200",
        ]
    )

    assert rc == 0
    assert calls  # the scripted default was the selected factory

    replay_path = tmp_path / "replay-seed-0.jsonl"
    rows: list[dict[str, Any]] = [
        json.loads(line)
        for line in replay_path.read_text(encoding="utf-8").splitlines()
    ]
    game_over_rows = [row for row in rows if row.get("kind") == "game_over"]
    assert game_over_rows
    assert all("tactical_policy" not in row for row in game_over_rows)
    assert read_tactical_policy_stamp(replay_path) is None
    assert _render_policy(None) == FSM_DEFAULT_POLICY_ID


def test_committed_canonical_replay_still_resolves_to_the_fsm_stamp() -> None:
    """The absent-stamp fallback interpretation is untouched on committed bytes.

    The canonical 9p2i set was recorded under the scripted default and
    carries NO ``tactical_policy`` stamp — per-record truth that predates any
    learned mover. Moving ``FSM_DEFAULT_POLICY_ID`` or the absent-stamp
    interpretation would re-read that history as champion games, so this
    fixture pins the read path on the committed bytes themselves: seed 0's
    replay reads back an absent stamp, the explicit stand-in is the
    five-field FSM stamp verbatim, and the MANIFEST attributes every row to
    ``fsm-default``.
    """

    assert read_tactical_policy_stamp(_SAMPLES_9P2I / "replay-seed-0.jsonl") is None

    assert FSM_DEFAULT_POLICY_ID == "fsm-default"
    stand_in = fsm_default_tactical_policy_stamp()
    assert stand_in.policy_id == "fsm-default"
    assert stand_in.method == "scripted-fsm"
    assert stand_in.encoder_version == "none"
    assert stand_in.weights_sha256 == "none"
    assert stand_in.anchor_policy == "fsm-default"

    manifest = parse_manifest(
        (_SAMPLES_9P2I / "MANIFEST.md").read_text(encoding="utf-8")
    )
    assert {row.policy for row in manifest.values()} == {FSM_DEFAULT_POLICY_ID}


# -- the champion stays opt-in, sha-coherent, named exactly -------------------


def test_champion_opt_in_surface_is_unchanged_and_names_the_evidence_artifact() -> None:
    """The champion stays opt-in as the identical sha-coherent utility-es artifact.

    The FAIL branch's referee-dominance swap clause is a no-op by identity:
    the 17.12 re-run re-selected the same genome (deterministic training), so
    the finalist the 17.14 evidence evaluated IS the committed champion —
    pinned by digest equality between the evidence row and the agents-side
    artifact the opt-in factory sha-verifies on load. The stamp constants
    name the policy exactly, and the ``learned-champion`` opt-in still
    resolves to the factory whose auto-stamp equals the evidence row's stamp
    field-for-field.
    """

    assert CHAMPION_POLICY_ID == "utility-es"
    assert CHAMPION_METHOD == "utility-scorer-es"
    assert CHAMPION_ANCHOR_POLICY == FSM_DEFAULT_POLICY_ID
    assert ENCODER_VERSION == "impostor-option-features-v1"
    assert committed_weights_sha256() == _CHAMPION_SHA

    utility = _finalist_rows()["utility-es"]
    assert utility["committed_weights_sha256"] == _CHAMPION_SHA
    assert utility["tactical_policy_stamp"] == {
        "policy_id": CHAMPION_POLICY_ID,
        "method": CHAMPION_METHOD,
        "encoder_version": ENCODER_VERSION,
        "weights_sha256": _CHAMPION_SHA,
        "anchor_policy": CHAMPION_ANCHOR_POLICY,
    }

    factory, stamp = rt._resolve_agent_factory(rt.LEARNED_CHAMPION_FACTORY_ID)
    assert isinstance(factory, LearnedAgentFactory)
    assert stamp is not None
    assert stamp.model_dump() == utility["tactical_policy_stamp"]
