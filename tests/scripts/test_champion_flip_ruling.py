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

Task 18.27 (``audits/audit-phase-18-flip-emergence.md``) appends the
phase-18 ruling pins below the 17.16 suite: the axis-1 FAIL re-derived
from the committed 18.26 rows (every candidate beats the same-seed FSM
comparator on wins and fails the baseline-6 referee — the §1.3 conjunction
unsatisfied on the whole slate), the ruling mechanics (the witnessed gauge
UNRESOLVABLE on all nine arms; ``bfd145cb…``'s flags cell UNRESOLVABLE, its
FAIL resting on conversion alone; ``7f73929d…`` read against the 49-seed
intersection comparator 12/49), the F13 cell (all three pooled
runner-up-minus-champion margins negative and noise-barred), the axis-2
tally (0 EMERGENT / 14 NOT-DEMONSTRATED — the two clause-(a)/(b)-passing
cells are unablated and read NOT-DEMONSTRATED by construction), and the
FAIL branch's no-op on the artifact surfaces (nothing swapped at 18.27).
"""

from __future__ import annotations

import inspect
import json
import math
from pathlib import Path
from typing import Any, Final

import pytest

import run_tournament as rt
from _manifest_writer import _render_policy, parse_manifest
from agents.tactical.learned.crew_forward import committed_crew_weights_sha256
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
    # Task 18.26 APPENDS the phase-18 rows (baseline-6) to this file; the 17.14
    # pins below hold unchanged, so this ruling reads its two rows by name.
    assert {"utility-es", "policy-es"} <= set(rows)
    rows = {entrant: rows[entrant] for entrant in ("utility-es", "policy-es")}
    fsm_rate = _fsm_comparator_win_rate()
    # The FSM comparator win rate reads the LIVE 9p2i samples; the Task-18.12
    # baseline-6 re-record moves it 0.36 -> 0.30 (15/50 IMPOSTORS). The finalist-eval
    # rows below are frozen (results-finalist-eval.jsonl, not re-recorded), so only
    # this comparator and the two win-edge deltas that subtract it move.
    assert fsm_rate == pytest.approx(0.30)

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
    assert utility["core"]["impostor_win_rate"] - fsm_rate == pytest.approx(0.22)
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
    assert policy["core"]["impostor_win_rate"] - fsm_rate == pytest.approx(-0.28)


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
    # Task 18.7 appends the opt-in ``learned-crew`` arm to the vocabulary; the
    # ruling's pin is that the DEFAULT stays the scripted FSM, which holds.
    assert rt._AGENT_FACTORY_CHOICES == (
        FSM_DEFAULT_POLICY_ID,
        rt.LEARNED_CHAMPION_FACTORY_ID,
        rt.LEARNED_CREW_FACTORY_ID,
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


# =====================================================================
# Task 18.27 — THE FLIP + EMERGENCE READING: the ruling pins (FAIL branch)
# (audits/audit-phase-18-flip-emergence.md; evidence merged 384effc)
# =====================================================================

# The four candidate arms and the champion candidate the memo puts to axis 1
# (§4.1 — the run-02 intermediate the crew block was recorded against).
_P18_CANDIDATES: Final[tuple[str, ...]] = (
    "p18-imp-ea4bc955",
    "p18-imp-bfd145cb",
    "p18-imp-6d327dcb",
    "p18-imp-7f73929d",
)
_P18_COMPARATOR: Final[str] = "p18-fsm-comparator"
_P18_CREW_ARMS: Final[tuple[str, ...]] = (
    "p18-crew-c1-gen9",
    "p18-crew-c1-gen0",
    "p18-crew-c2-gen9",
    "p18-crew-c2-gen0",
)
_P18_CHAMPION_ARM: Final[str] = "p18-imp-ea4bc955"
_P18_CHAMPION_SHA: Final[str] = (
    "ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f"
)
# The committed crew opt-in artifact digest (Task 18.7; unmoved by NO-ADOPTION).
_CREW_CHAMPION_SHA: Final[str] = (
    "bd6fdd0a030a01cc57f2ef8c95abf66f46d8cbc5ac270e04ae74a6cab587f19c"
)

# The baseline-6 floor pins (eval/watchability.py; the 18.12 adopting record):
# witnessed 6/177, flags 180/165, conversion pin 78/136 population-relative.
_B6_WITNESSED_FLOOR: Final[float] = 6 / 177
_B6_FLAGS_FLOOR: Final[float] = 180 / 165
_B6_CONVERSION_PIN: Final[float] = 78 / 136


def _p18_rows() -> dict[str, dict[str, Any]]:
    """The committed 18.26 evidence rows, keyed by entrant."""

    rows = _finalist_rows()
    assert set(_P18_CANDIDATES) | {_P18_COMPARATOR} | set(_P18_CREW_ARMS) <= set(rows)
    return rows


def _pooled_z(k_c: int, n_c: int, k_f: int, n_f: int) -> float | None:
    """The §6.a pooled two-proportion z; None where no delta exists."""

    if n_c == 0 or n_f == 0:
        return None
    pooled = (k_c + k_f) / (n_c + n_f)
    if pooled in (0.0, 1.0):
        return None
    return (k_c / n_c - k_f / n_f) / math.sqrt(
        pooled * (1 - pooled) * (1 / n_c + 1 / n_f)
    )


def _fisher_z(r_c: float, n_c: int, r_f: float, n_f: int) -> float:
    """The §6.a Fisher r-to-z for the correlation cell."""

    return (math.atanh(r_c) - math.atanh(r_f)) / math.sqrt(
        1 / (n_c - 3) + 1 / (n_f - 3)
    )


def _impostor_win_seeds(row: dict[str, Any]) -> set[int]:
    """Impostor-win seeds from a row's per-game watchability reasons."""

    return {
        game["seed"]
        for game in row["watchability"]["per_game"]
        if game["reason"] in ("IMPOSTOR_PARITY", "IMPOSTOR_SABOTAGE")
    }


def test_18_27_axis_1_reads_fail_on_every_p18_candidate() -> None:
    """No candidate satisfies referee-PASS AND win-edge — the NO-FLIP ruling.

    Re-derives the memo's §3 table from the committed rows: stamp
    preconditions, the baseline-6 referee verdict per arm (every candidate
    FAIL, the comparator the only PASS), each arm's floor cells, and the win
    edge against the same-seed comparator — full-50 (13/50 = 0.26) for the
    three full arms, the 49-seed intersection (12/49 = 0.24490, seed 35 an
    ``IMPOSTOR_PARITY`` comparator win, re-derived from the comparator's own
    per-game reasons) for ``7f73929d…``. If any conjunct flips on a future
    re-record, this pin fails and the flip must be re-ruled.
    """

    rows = _p18_rows()
    comparator = rows[_P18_COMPARATOR]
    assert comparator["watchability"]["referee_passed"] is True
    assert comparator["core"]["impostor_win_rate"] == pytest.approx(13 / 50)
    assert comparator["tactical_policy_stamp"]["policy_id"] == FSM_DEFAULT_POLICY_ID
    assert comparator["opponent_absence_proven"] is True
    comparator_win_seeds = _impostor_win_seeds(comparator)
    assert len(comparator_win_seeds) == 13
    assert 35 in comparator_win_seeds  # seed 35: IMPOSTOR_PARITY (§2.2.iii)
    intersection_rate = len(comparator_win_seeds - {35}) / 49
    assert intersection_rate == pytest.approx(12 / 49)
    assert intersection_rate == pytest.approx(0.24490, abs=5e-6)

    # The memo's §3 floor cells: (witnessed, flags, conversion) measured.
    expected_gauges: dict[str, tuple[float, float, float]] = {
        "p18-imp-ea4bc955": (0.15228, 0.93548, 0.36667),
        "p18-imp-bfd145cb": (0.14778, 0.90000, 0.35099),
        "p18-imp-6d327dcb": (0.22280, 0.96914, 0.44444),
        "p18-imp-7f73929d": (0.22000, 0.82840, 0.38926),
    }
    expected_edges: dict[str, float] = {
        "p18-imp-ea4bc955": 0.26,
        "p18-imp-bfd145cb": 0.30,
        "p18-imp-6d327dcb": 0.12,
        "p18-imp-7f73929d": 0.18367,
    }

    for entrant in _P18_CANDIDATES:
        row = rows[entrant]
        n_games = 49 if entrant == "p18-imp-7f73929d" else 50
        assert row["stamp_verified_games"] == n_games
        assert row["stamp_equals_committed_sha256"] is True
        assert row["validity_gate"]["passed"] is True
        assert row["core"]["games_total"] == n_games
        assert row["watchability"]["baseline_id"] == "baseline-6"

        gauges = {
            gauge["name"]: gauge for gauge in row["watchability"]["supply_gauges"]
        }
        witnessed, flags, conversion = (
            gauges["witnessed_event_rate"],
            gauges["flags_per_meeting"],
            gauges["testimony_backed_conversion"],
        )
        exp_witnessed, exp_flags, exp_conversion = expected_gauges[entrant]
        assert witnessed["floor"] == pytest.approx(_B6_WITNESSED_FLOOR)
        assert witnessed["measured"] == pytest.approx(exp_witnessed, abs=1e-4)
        assert witnessed["passed"] is True  # PASS on the floor; §2.2.i excludes
        assert flags["floor"] == pytest.approx(_B6_FLAGS_FLOOR)
        assert flags["measured"] == pytest.approx(exp_flags, abs=1e-4)
        assert flags["passed"] is False
        assert conversion["measured"] == pytest.approx(exp_conversion, abs=1e-4)
        assert conversion["passed"] is False
        # The 16.11 population-relative derivation on the baseline-6 pins.
        assert conversion["floor"] == pytest.approx(
            min(1.0, _B6_CONVERSION_PIN * (_B6_FLAGS_FLOOR / flags["measured"]))
        )

        assert row["watchability"]["referee_passed"] is False
        comparator_rate = (
            intersection_rate if entrant == "p18-imp-7f73929d" else 13 / 50
        )
        edge = row["core"]["impostor_win_rate"] - comparator_rate
        assert edge == pytest.approx(expected_edges[entrant], abs=5e-6)
        assert edge > 0  # the win edge holds on every arm...
        # ...and the §1.3 conjunction still fails on every arm.
        assert not (row["watchability"]["referee_passed"] and edge > 0)


def test_18_27_witnessed_unresolvable_on_all_nine_arms_and_bfd_on_conversion_alone() -> (
    None
):
    """The ruling mechanics: the noise preconditions read from committed cells.

    ``witnessed_event_rate``'s split-half noise exceeds its 25% ceiling
    (0.25 x 6/177) on ALL NINE arms — structural, so the gauge is excluded
    from discriminating between arms and the referee is effectively two
    gauges for this ruling. ``bfd145cb…``'s flags noise (0.29291) also
    exceeds the flags ceiling (0.27273, a 7% overshoot) — the only impostor
    arm to fail it — so its axis-1 FAIL rests on conversion alone.
    """

    rows = _p18_rows()
    witnessed_ceiling = 0.25 * _B6_WITNESSED_FLOOR
    flags_ceiling = 0.25 * _B6_FLAGS_FLOOR

    all_nine = (*_P18_CANDIDATES, _P18_COMPARATOR, *_P18_CREW_ARMS)
    for entrant in all_nine:
        witnessed = rows[entrant]["split_half"]["witnessed_event_rate"]
        assert witnessed["precondition"] == "UNRESOLVABLE"
        assert witnessed["ceiling_25pct"] == pytest.approx(witnessed_ceiling)
        assert witnessed["noise"] > witnessed_ceiling

    bfd = rows["p18-imp-bfd145cb"]
    bfd_flags = bfd["split_half"]["flags_per_meeting"]
    assert bfd_flags["precondition"] == "UNRESOLVABLE"
    assert bfd_flags["noise"] == pytest.approx(0.29291, abs=1e-4)
    assert bfd_flags["noise"] > flags_ceiling == pytest.approx(0.27273, abs=1e-4)
    # The other three candidate arms' flags cells clear the precondition —
    # their FAILs count both gauges; bfd145cb's counts conversion alone.
    for entrant in _P18_CANDIDATES:
        if entrant == "p18-imp-bfd145cb":
            continue
        assert rows[entrant]["split_half"]["flags_per_meeting"]["precondition"] == (
            "clears"
        )
    assert bfd["split_half"]["testimony_backed_conversion"]["precondition"] == (
        "clears"
    )


def test_18_27_f13_pooled_margins_negative_and_noise_barred() -> None:
    """The F13 cell: hypothesis A unsupported by the §11.2 either-side rule.

    Re-derives the three pooled runner-up-minus-champion margins from the
    persisted ``f13_intersection_gauges`` cells (with ``7f73929d…``'s own
    n=49 watchability/split-half blocks as its view): every margin NEGATIVE
    (hypothesis A's opposite), witnessed and flags barred by BOTH pooled
    sides' split-half noise, conversion barred by the champion side — so no
    gauge supports A. The residual within-lineage conversion cell
    (``bfd145cb…`` minus ``ea4bc955…``, −0.02231) is pinned as the memo
    records it: outside bfd's own noise, inside ea4's.
    """

    rows = _p18_rows()

    def f13_cell(entrant: str, gauge: str) -> tuple[float, float]:
        if entrant == "p18-imp-7f73929d":
            gauges = {
                g["name"]: g for g in rows[entrant]["watchability"]["supply_gauges"]
            }
            return (
                gauges[gauge]["measured"],
                rows[entrant]["split_half"][gauge]["noise"],
            )
        cell = rows[entrant]["f13_intersection_gauges"]["gauges"][gauge]
        return cell["measured"], cell["split_half_noise"]

    champions = ("p18-imp-6d327dcb", "p18-imp-ea4bc955")
    runner_ups = ("p18-imp-bfd145cb", "p18-imp-7f73929d")
    expected = {
        "witnessed_event_rate": (-0.00650, 0.07001, 0.06026),
        "flags_per_meeting": (-0.09189, 0.17958, 0.15652),
        "testimony_backed_conversion": (-0.03483, 0.06578, 0.00942),
    }
    for gauge, (exp_margin, exp_champ_noise, exp_ru_noise) in expected.items():
        champ_cells = [f13_cell(entrant, gauge) for entrant in champions]
        ru_cells = [f13_cell(entrant, gauge) for entrant in runner_ups]
        margin = sum(measured for measured, _ in ru_cells) / 2 - (
            sum(measured for measured, _ in champ_cells) / 2
        )
        champ_noise = sum(noise for _, noise in champ_cells) / 2
        ru_noise = sum(noise for _, noise in ru_cells) / 2
        assert margin == pytest.approx(exp_margin, abs=5e-5)
        assert champ_noise == pytest.approx(exp_champ_noise, abs=5e-5)
        assert ru_noise == pytest.approx(exp_ru_noise, abs=5e-5)
        assert margin < 0
        # §11.2 either-side rule: smaller than EITHER side's noise -> barred.
        assert abs(margin) < champ_noise  # every gauge barred by this side
        if gauge != "testimony_backed_conversion":
            assert abs(margin) < ru_noise  # witnessed/flags barred by both

    # The residual within-lineage cell (run-02 held constant): conversion only.
    bfd_conv, bfd_noise = f13_cell("p18-imp-bfd145cb", "testimony_backed_conversion")
    ea4_conv, ea4_noise = f13_cell("p18-imp-ea4bc955", "testimony_backed_conversion")
    within_lineage = bfd_conv - ea4_conv
    assert within_lineage == pytest.approx(-0.02231, abs=5e-5)
    assert abs(within_lineage) > bfd_noise == pytest.approx(0.01504, abs=5e-5)
    assert abs(within_lineage) < ea4_noise == pytest.approx(0.09459, abs=5e-5)


def test_18_27_axis_2_champion_arm_rulings_read_zero_emergent() -> None:
    """The fourteen rulings: 0 EMERGENT — the memo §7 tally, re-derived.

    Clause (a) is recomputed from the champion arm's persisted cells against
    the full-50 comparator cells (the registered denominators): exactly two
    cells pass |z| >= 1.96 — the crew-witnessed-kill rate (+3.370) and the
    co-present-kill departure (+4.321) — and both sign-reproduce 3/3 on the
    committed ``seed_mod5_splits``. Clause (c) is complete on ZERO campaign
    runs as recorded (the committed campaign reports' §6 ledgers — memo
    §6.3), so the clause-(c)-complete set is empty and no ruling reads
    EMERGENT: the two passing cells are unablated (NOT-DEMONSTRATED by
    construction, the phase's named findings N1/N2) and the entropy cells
    carry no variance field (unjudgeable as recorded).
    """

    rows = _p18_rows()
    champion = rows[_P18_CHAMPION_ARM]
    comparator = rows[_P18_COMPARATOR]
    assert champion["committed_weights_sha256"] == _P18_CHAMPION_SHA

    def rate_cells(row: dict[str, Any]) -> dict[str, tuple[int, int]]:
        instruments = row["instruments"]
        deception = instruments["deception"]
        nested = instruments["registered_nested_cells"]
        kill_craft = instruments["kill_craft"]
        departure = instruments["kill_craft_co_present_departure"]
        off_menu = instruments["off_menu"]
        return {
            "false_vouch_saw_player": (
                deception["false_vouch_saw_player_observations"],
                deception["vouch_observations_impostor"],
            ),
            "false_vouch_corroboration": (
                deception["false_vouch_corroborations"],
                deception["corroboration_claims_impostor"],
            ),
            "false_vouch_fabricated": (
                deception["false_vouch_fabricated"],
                deception["false_vouch_subject_events"],
            ),
            "frame_attempts": (
                deception["frame_attempt_meetings"],
                deception["meetings_total"],
            ),
            "frame_conversions": (
                nested["frame_conversions"]["numerator"],
                nested["frame_conversions"]["denominator"],
            ),
            "teammate_accusations": (
                nested["teammate_accusations"]["numerator"],
                nested["teammate_accusations"]["denominator"],
            ),
            "alibi_survival": (
                nested["alibi_survival"]["survived"],
                nested["alibi_survival"]["total_impostor_alibis"],
            ),
            "effective_deflection": (
                nested["effective_deflection"]["effective_deflections"],
                nested["effective_deflection"]["active_survivals"],
            ),
            "crew_witnessed_kills": (
                kill_craft["crew_witnessed_kills"],
                kill_craft["kills_total"],
            ),
            "co_present_departure": (
                departure["co_present_ge1_kills"],
                departure["kills_total"],
            ),
            "off_menu": (
                off_menu["off_menu_total"],
                off_menu["impostor_decisions"],
            ),
        }

    champion_cells = rate_cells(champion)
    comparator_cells = rate_cells(comparator)
    z_values: dict[str, float | None] = {
        name: _pooled_z(*champion_cells[name], *comparator_cells[name])
        for name in champion_cells
    }
    # The memo §7/§15 statistics, pinned exactly (inputs are the cells above).
    expected_z: dict[str, float | None] = {
        "false_vouch_saw_player": 0.761,
        "false_vouch_corroboration": 1.549,
        "false_vouch_fabricated": -1.560,
        "frame_attempts": 1.393,
        "frame_conversions": 0.987,
        "teammate_accusations": None,  # pooled rate 0 — no delta exists
        "alibi_survival": 0.202,
        "effective_deflection": 0.639,
        "crew_witnessed_kills": 3.370,
        "co_present_departure": 4.321,
        "off_menu": None,  # 0/2015 vs 0/2299 — vacuous, no delta exists
    }
    for name, expected_value in expected_z.items():
        if expected_value is None:
            assert z_values[name] is None
        else:
            assert z_values[name] == pytest.approx(expected_value, abs=5e-4)

    # The correlation cell (ruling 10): Fisher z fails clause (a).
    fisher = _fisher_z(
        champion["instruments"]["kill_craft"][
            "witnessed_point_biserial_within_one_hop"
        ],
        champion["instruments"]["kill_craft"]["kills_total"],
        comparator["instruments"]["kill_craft"][
            "witnessed_point_biserial_within_one_hop"
        ],
        comparator["instruments"]["kill_craft"]["kills_total"],
    )
    assert fisher == pytest.approx(-0.648, abs=5e-4)

    clause_a_pass = {
        name for name, z in z_values.items() if z is not None and abs(z) >= 1.96
    }
    assert clause_a_pass == {"crew_witnessed_kills", "co_present_departure"}

    # Clause (b) for the two passing cells: 3/3 positive per-split deltas.
    champion_splits = champion["instruments"]["seed_mod5_splits"]
    comparator_splits = comparator["instruments"]["seed_mod5_splits"]
    for name in sorted(clause_a_pass):
        for split in ("train_mod5_012", "val_mod5_3", "test_mod5_4"):
            candidate_cell = champion_splits[split][name]
            comparator_cell = comparator_splits[split][name]
            assert candidate_cell["d"] > 0 and comparator_cell["d"] > 0
            delta = (
                candidate_cell["n"] / candidate_cell["d"]
                - comparator_cell["n"] / comparator_cell["d"]
            )
            assert delta > 0

    # The entropy rulings (13/14) are unjudgeable as recorded: the committed
    # cells carry means + agents + decisions only — no per-agent variance
    # field (the 18.4 §6.a routed contract never landed).
    for side in ("IMPOSTOR", "CREWMATE"):
        entropy = champion["instruments"]["registered_nested_cells"]["action_entropy"][
            side
        ]
        assert set(entropy) == {"mean_conditional_entropy", "agents", "decisions"}

    # Clause (c): complete on ZERO of the five impostor campaign runs and
    # zero crew runs as recorded (the committed campaign reports' §6
    # ablation ledgers, quoted in the memo §6.3) — the conjunctive
    # discipline therefore rules nothing EMERGENT.
    clause_c_complete: frozenset[str] = frozenset()
    assert not (clause_a_pass & clause_c_complete)  # 0 EMERGENT, 14 rulings


def test_18_27_fail_branch_swaps_nothing_and_names_the_frozen_champion() -> None:
    """On FAIL + NO-ADOPTION nothing under ``agents/tactical/learned/`` moves.

    The opt-in impostor artifact is still the committed ``utility-es``
    champion (``6d327dcb…`` — no finalist referee-dominates it: none passes
    the referee at all), the opt-in crew artifact is still
    ``crew-owned-tasks-es`` (``bd6fdd0a…``, the NO-ADOPTION slot), and the
    champion candidate the memo designates (``ea4bc955…``, §4.1) is exactly
    the frozen opponent every 18.26 crew diagnostic was recorded against —
    the designation is pinned to the committed rows, not to prose.
    """

    assert committed_weights_sha256() == _CHAMPION_SHA  # unmoved at 18.27
    assert committed_crew_weights_sha256() == _CREW_CHAMPION_SHA

    rows = _p18_rows()
    champion = rows[_P18_CHAMPION_ARM]
    assert champion["committed_weights_sha256"] == _P18_CHAMPION_SHA
    assert champion["tactical_policy_stamp"]["weights_sha256"] == _P18_CHAMPION_SHA
    for entrant in _P18_CREW_ARMS:
        row = rows[entrant]
        assert row["opponent_committed_weights_sha256"] == _P18_CHAMPION_SHA
        assert row["opponent_stamp_equals_committed_sha256"] is True

    # The incumbent control on the slate is byte-identical to the committed
    # opt-in artifact — the FAIL branch's swap clause is a no-op on evidence.
    incumbent = rows["p18-imp-6d327dcb"]
    assert incumbent["committed_weights_sha256"] == _CHAMPION_SHA
    assert incumbent["watchability"]["referee_passed"] is False
