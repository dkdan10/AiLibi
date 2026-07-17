"""Unit tests for scripts/run_tournament.py ``--candidate-artifact`` (Task 17.14).

The multi-finalist recorder productizes the phase-15 pause's uncommitted
per-finalist driver (audits/audit-phase-15-pause.md:145-184) as a thin loader
parameter beside the committed champion: ``--candidate-artifact
training/artifacts/impostor/<entrant>`` loads an ARBITRARY committed candidate
artifact by path, sha-verifies its genome against the sidecar (a mismatch fails
loud BEFORE any spend), rebuilds the inference policy through the committed
builder its ``encoder_version`` selects, and AUTO-STAMPS every recording from the
artifact's OWN ``stamp.json`` — never the committed champion's constants.

These tests pin the DoD axes: (1) the recorder loads an arbitrary candidate with
sha verification and the stamp fields are EXACT (read back from the recorded
bytes, never echoed); (2) a mismatch — weights-vs-sidecar OR stamp-vs-sidecar
(the conflation guard) — fails loud before any game runs; (3) the loader binds
ONE candidate per invocation (mutually exclusive with ``--agent-factory
learned-champion``; an explicit ``--tactical-policy-stamp`` must match the
artifact stamp field-for-field); (4) the default (no ``--candidate-artifact``)
path stays byte-identical to the pre-17.14 CLI. The fake LLM provider comes from
the root ``tests/conftest.py`` autouse fixture — no network.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Sequence
from pathlib import Path

import pytest

import run_tournament as rt
from agents.tactical.learned.factory import LearnedAgentFactory
from eval.balance_eval import run_tournament_eval as _real_run_tournament_eval
from eval.report_schema import TournamentReport
from orchestrator.game import AgentFactory
from orchestrator.replay import (
    TacticalPolicyStamp,
    read_tactical_policy_stamp,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARTIFACTS = _REPO_ROOT / "training" / "artifacts" / "impostor"
_UTILITY_ES = _ARTIFACTS / "utility-es"
_POLICY_ES = _ARTIFACTS / "policy-es"


def _artifact_stamp(entrant_dir: Path) -> TacticalPolicyStamp:
    """The committed five-field stamp read straight from the artifact's stamp.json."""

    raw = (entrant_dir / "stamp.json").read_text(encoding="utf-8")
    return TacticalPolicyStamp.model_validate_json(raw)


def _sidecar_digest(entrant_dir: Path) -> str:
    """The committed weights sha256 sidecar digest (first token)."""

    return (entrant_dir / "weights.json.sha256").read_text(encoding="utf-8").split()[0]


def _copy_artifact(src: Path, dst: Path) -> Path:
    """Copy a committed artifact dir to a writable tmp copy for corruption fixtures."""

    shutil.copytree(src, dst)
    return dst


def _install_factory_capturing_spy(
    monkeypatch: pytest.MonkeyPatch, captured: dict[str, object]
) -> None:
    """Patch ``run_tournament.run_tournament_eval`` to capture the candidate seam.

    Mirrors the 15.21 learned-path spy: a keyword-only ``agent_factory:
    AgentFactory`` with NO default, so ``main`` failing to thread the candidate
    factory also fails loud (TypeError). Records the factory + stamp ``main``
    threads, then delegates to the real harness so ``main`` still produces a
    valid report end-to-end.
    """

    def spy(
        *,
        seeds: Sequence[int],
        output_dir: Path,
        agent_factory: AgentFactory,
        num_players: int,
        num_impostors: int,
        tasks_per_crewmate: int,
        max_ticks: int,
        force: bool,
        tactical_policy_stamp: TacticalPolicyStamp | None = None,
    ) -> TournamentReport:
        captured["agent_factory"] = agent_factory
        captured["tactical_policy_stamp"] = tactical_policy_stamp
        return _real_run_tournament_eval(
            seeds=seeds,
            output_dir=output_dir,
            agent_factory=agent_factory,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            max_ticks=max_ticks,
            force=force,
            tactical_policy_stamp=tactical_policy_stamp,
        )

    monkeypatch.setattr(rt, "run_tournament_eval", spy)


def _install_default_path_spy(
    monkeypatch: pytest.MonkeyPatch, captured: dict[str, object]
) -> None:
    """Patch with the pre-17.14 no-``agent_factory``-kwarg seam (byte-identity pin).

    If ``main`` threaded ``agent_factory`` on the default (no candidate) path this
    call would raise TypeError, so reaching rc == 0 with a ``None`` stamp is the
    pin that the default path is untouched.
    """

    def spy(
        *,
        seeds: Sequence[int],
        output_dir: Path,
        num_players: int,
        num_impostors: int,
        tasks_per_crewmate: int,
        max_ticks: int,
        force: bool,
        tactical_policy_stamp: TacticalPolicyStamp | None = None,
    ) -> TournamentReport:
        captured["tactical_policy_stamp"] = tactical_policy_stamp
        return _real_run_tournament_eval(
            seeds=seeds,
            output_dir=output_dir,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            max_ticks=max_ticks,
            force=force,
            tactical_policy_stamp=tactical_policy_stamp,
        )

    monkeypatch.setattr(rt, "run_tournament_eval", spy)


# -- parse layer --------------------------------------------------------------


def test_parse_candidate_artifact_defaults_none(tmp_path: Path) -> None:
    """The flag omitted parses to ``None`` — the recorder is opt-in."""

    args = rt._parse_args(["--output-dir", str(tmp_path)])
    assert args.candidate_artifact is None


def test_parse_candidate_artifact_accepts_path(tmp_path: Path) -> None:
    """``--candidate-artifact`` parses to a ``Path``."""

    args = rt._parse_args(
        ["--output-dir", str(tmp_path), "--candidate-artifact", str(_UTILITY_ES)]
    )
    assert args.candidate_artifact == _UTILITY_ES


# -- resolve layer (the loader) -----------------------------------------------


@pytest.mark.parametrize("entrant_dir", [_UTILITY_ES, _POLICY_ES])
def test_resolve_candidate_builds_factory_and_exact_stamp(entrant_dir: Path) -> None:
    """Each committed finalist resolves to a factory + its OWN five-field stamp.

    The stamp comes from the artifact's ``stamp.json`` (never the champion's
    constants), and its ``weights_sha256`` equals the committed sidecar digest —
    the sha-verified provenance the 50-game finalist eval reads back.
    """

    factory, stamp = rt._resolve_agent_factory(
        "fsm-default", candidate_artifact=entrant_dir
    )
    assert callable(factory)
    # The candidate factory is the bake-off closure, NOT the champion factory.
    assert not isinstance(factory, LearnedAgentFactory)
    assert stamp == _artifact_stamp(entrant_dir)
    assert stamp is not None and stamp.weights_sha256 == _sidecar_digest(entrant_dir)


def test_resolve_candidate_utility_and_policy_stamps_differ() -> None:
    """Two finalists never share a stamp — the 17.14 conflation guard, positively.

    One candidate per invocation, and the stamp NAMES it: the utility-es and
    policy-es stamps differ on ``policy_id``/``method``/``encoder_version``/
    ``weights_sha256``, so no recording can wear the other mover's label.
    """

    _, util_stamp = rt._resolve_agent_factory(
        "fsm-default", candidate_artifact=_UTILITY_ES
    )
    _, policy_stamp = rt._resolve_agent_factory(
        "fsm-default", candidate_artifact=_POLICY_ES
    )
    assert util_stamp is not None and policy_stamp is not None
    assert util_stamp.policy_id == "utility-es"
    assert policy_stamp.policy_id == "policy-es"
    assert util_stamp != policy_stamp
    assert util_stamp.encoder_version != policy_stamp.encoder_version
    assert util_stamp.weights_sha256 != policy_stamp.weights_sha256


def test_resolve_candidate_mutually_exclusive_with_learned_champion() -> None:
    """A candidate artifact + ``--agent-factory learned-champion`` is rejected loudly.

    The artifact selects the impostor policy; combining it with a second
    non-default factory would conflate two movers in one recording.
    """

    with pytest.raises(SystemExit, match="mutually exclusive"):
        rt._resolve_agent_factory("learned-champion", candidate_artifact=_UTILITY_ES)


def test_resolve_candidate_missing_dir_fails_loud(tmp_path: Path) -> None:
    """A non-directory artifact path fails loud (no silent fallback)."""

    with pytest.raises(SystemExit, match="not a directory"):
        rt._resolve_agent_factory("fsm-default", candidate_artifact=tmp_path / "nope")


def test_resolve_candidate_sha_mismatch_fails_loud(tmp_path: Path) -> None:
    """A sidecar digest that does not match ``weights.json`` fails loud on load.

    The genome sha verification (reused from ``load_candidate_weights``) trips
    BEFORE any policy is built or any game runs.
    """

    corrupt = _copy_artifact(_UTILITY_ES, tmp_path / "utility-es")
    (corrupt / "weights.json.sha256").write_text(f"{'0' * 64}  weights.json\n")

    with pytest.raises(SystemExit, match="load/verify failed"):
        rt._resolve_agent_factory("fsm-default", candidate_artifact=corrupt)


def test_resolve_candidate_stamp_sidecar_conflation_guard(tmp_path: Path) -> None:
    """A ``stamp.json`` naming a different artifact's digest fails loud.

    Weights + sidecar stay consistent (the genome loads), but the stamp's
    ``weights_sha256`` no longer equals the sidecar — the recording would carry a
    stamp that does not name the bytes it produced. The conflation guard rejects
    it before any spend.
    """

    corrupt = _copy_artifact(_UTILITY_ES, tmp_path / "utility-es")
    stamp = json.loads((corrupt / "stamp.json").read_text(encoding="utf-8"))
    stamp["weights_sha256"] = "a" * 64
    (corrupt / "stamp.json").write_text(json.dumps(stamp, indent=2, sort_keys=True))

    with pytest.raises(SystemExit, match="conflation guard"):
        rt._resolve_agent_factory("fsm-default", candidate_artifact=corrupt)


def test_resolve_candidate_missing_stamp_fails_loud(tmp_path: Path) -> None:
    """An artifact without a ``stamp.json`` fails loud."""

    corrupt = _copy_artifact(_UTILITY_ES, tmp_path / "utility-es")
    (corrupt / "stamp.json").unlink()

    with pytest.raises(SystemExit, match="cannot read"):
        rt._resolve_agent_factory("fsm-default", candidate_artifact=corrupt)


def test_resolve_candidate_blank_stamp_field_fails_loud(tmp_path: Path) -> None:
    """A malformed (blank) stamp field is rejected by the stamp validator."""

    corrupt = _copy_artifact(_UTILITY_ES, tmp_path / "utility-es")
    stamp = json.loads((corrupt / "stamp.json").read_text(encoding="utf-8"))
    stamp["method"] = "   "
    (corrupt / "stamp.json").write_text(json.dumps(stamp))

    with pytest.raises(SystemExit, match="not a valid TacticalPolicyStamp"):
        rt._resolve_agent_factory("fsm-default", candidate_artifact=corrupt)


def test_resolve_candidate_masked_mlp_missing_hidden_fails_loud(
    tmp_path: Path,
) -> None:
    """The masked-MLP family needs an integer ``hidden`` in config.json — fail loud.

    policy-es (the ``v2`` family) rebuilds through
    ``build_masked_mlp_policy(..., hidden=...)``; dropping ``hidden`` from
    config.json is a fail-loud error, not a hard-coded default.
    """

    corrupt = _copy_artifact(_POLICY_ES, tmp_path / "policy-es")
    config = json.loads((corrupt / "config.json").read_text(encoding="utf-8"))
    del config["hidden"]
    (corrupt / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True))

    with pytest.raises(SystemExit, match="integer 'hidden'"):
        rt._resolve_agent_factory("fsm-default", candidate_artifact=corrupt)


# -- main() candidate path (opt-in factory + auto-stamp) -----------------------


def test_main_candidate_threads_factory_and_auto_stamp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--candidate-artifact`` threads the bake-off factory + the artifact stamp."""

    captured: dict[str, object] = {}
    _install_factory_capturing_spy(monkeypatch, captured)

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--output-dir",
            str(tmp_path),
            "--max-ticks",
            "2",
            "--candidate-artifact",
            str(_UTILITY_ES),
        ]
    )

    assert rc == 0
    assert callable(captured["agent_factory"])
    assert captured["tactical_policy_stamp"] == _artifact_stamp(_UTILITY_ES)


@pytest.mark.parametrize("entrant_dir", [_UTILITY_ES, _POLICY_ES])
def test_main_candidate_auto_stamps_replay_on_disk(
    entrant_dir: Path, tmp_path: Path
) -> None:
    """The DoD e2e: a real candidate run auto-stamps the replay on disk (exact).

    No spy — the production seam runs end-to-end at ``--max-ticks 200`` on the
    4p/1i seed 0 roster, which lands a ``game_over`` record. The stamp is asserted
    from the RECORDED BYTES via ``read_tactical_policy_stamp``, never the launch
    config, and equals the artifact's own ``stamp.json`` — the finalist-eval proof
    that the loaded candidate, not the FSM wearing a label, produced the bytes.
    The fake provider comes from the root conftest autouse fixture.
    """

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
            "--candidate-artifact",
            str(entrant_dir),
        ]
    )

    assert rc == 0
    stamp = read_tactical_policy_stamp(tmp_path / "replay-seed-0.jsonl")
    assert stamp == _artifact_stamp(entrant_dir)
    assert stamp is not None
    assert stamp.weights_sha256 == _sidecar_digest(entrant_dir)


def test_main_candidate_omitted_is_default_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Omitting ``--candidate-artifact`` keeps the default no-factory-kwarg path.

    The default-path spy has no ``agent_factory`` parameter, so if ``main``
    threaded one this run would raise TypeError. Reaching rc == 0 with a ``None``
    stamp is the byte-identity pin for the pre-17.14 CLI.
    """

    captured: dict[str, object] = {}
    _install_default_path_spy(monkeypatch, captured)

    rc = rt.main(
        ["--num-games", "1", "--output-dir", str(tmp_path), "--max-ticks", "2"]
    )

    assert rc == 0
    assert captured["tactical_policy_stamp"] is None


# -- main() mis-stamp guard on the candidate path -----------------------------


def test_main_candidate_rejects_contradicting_explicit_stamp(tmp_path: Path) -> None:
    """An explicit stamp that contradicts the artifact stamp is rejected, named.

    The two-direction 15.21 guard applies to the candidate path too: the artifact
    stamp is authoritative, so an explicit ``--tactical-policy-stamp`` that
    differs (here the FSM default, first differing on ``policy_id``) fails loud
    before any game runs.
    """

    with pytest.raises(SystemExit, match="policy_id"):
        rt.main(
            [
                "--num-games",
                "1",
                "--output-dir",
                str(tmp_path),
                "--max-ticks",
                "2",
                "--candidate-artifact",
                str(_UTILITY_ES),
                "--tactical-policy-stamp",
                "fsm-default",
            ]
        )


def test_main_candidate_accepts_matching_explicit_stamp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A field-for-field restatement of the artifact stamp is accepted (idempotent)."""

    stamp_path = tmp_path / "restate.json"
    stamp_path.write_text(
        _artifact_stamp(_UTILITY_ES).model_dump_json(), encoding="utf-8"
    )

    captured: dict[str, object] = {}
    _install_factory_capturing_spy(monkeypatch, captured)

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--output-dir",
            str(tmp_path),
            "--max-ticks",
            "2",
            "--candidate-artifact",
            str(_UTILITY_ES),
            "--tactical-policy-stamp",
            str(stamp_path),
        ]
    )

    assert rc == 0
    assert captured["tactical_policy_stamp"] == _artifact_stamp(_UTILITY_ES)


def test_main_candidate_sha_mismatch_fails_before_recording(tmp_path: Path) -> None:
    """A sha mismatch fails loud BEFORE any replay is written (before any spend)."""

    corrupt = _copy_artifact(_UTILITY_ES, tmp_path / "artifact")
    (corrupt / "weights.json.sha256").write_text(f"{'0' * 64}  weights.json\n")
    out_dir = tmp_path / "out"

    with pytest.raises(SystemExit, match="load/verify failed"):
        rt.main(
            [
                "--num-games",
                "1",
                "--output-dir",
                str(out_dir),
                "--max-ticks",
                "2",
                "--candidate-artifact",
                str(corrupt),
            ]
        )

    # Fail loud BEFORE any spend: no replay bytes were written.
    if out_dir.exists():
        assert not list(out_dir.glob("replay-seed-*.jsonl"))
