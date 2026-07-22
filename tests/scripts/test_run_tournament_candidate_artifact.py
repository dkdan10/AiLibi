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

The opt-in learned CREW arm (Task 18.7; audits/audit-phase-18-planning.md §4 #7)
adds its own guard section below: ``--agent-factory learned-crew`` resolves to a
:class:`~agents.tactical.learned.factory.LearnedCrewAgentFactory` plus a crew
:class:`~orchestrator.replay.CrewTacticalPolicyStamp` whose ``weights_sha256`` is
the committed crew sidecar digest (read back from the recorded bytes, never
echoed), its ``policy_id`` / ``weights_sha256`` asserted DISJOINT from the
impostor champion's — the 18.7 conflation guard, positively AND (via a
monkeypatched collision on the guard's ``CHAMPION_POLICY_ID`` import site)
mechanically. ``main`` threads that factory beside the crew stamp and an ABSENT
impostor tactical stamp, so a crew recording carries its own provenance in a
distinct schema slot; the fsm-default path threads NEITHER (the byte-identity
pin, on-disk edition: no ``crew_tactical_policy`` key), and the crew arm rejects a
combined ``--candidate-artifact`` (an impostor mover) or a contradicting explicit
champion ``--tactical-policy-stamp`` loudly.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Sequence
from pathlib import Path

import pytest

import run_tournament as rt
from agents.tactical.learned.factory import (
    LearnedAgentFactory,
    LearnedCrewAgentFactory,
)
from eval.balance_eval import run_tournament_eval as _real_run_tournament_eval
from eval.report_schema import TournamentReport
from orchestrator.game import AgentFactory
from orchestrator.replay import (
    CrewTacticalPolicyStamp,
    TacticalPolicyStamp,
    read_crew_tactical_policy_stamp,
    read_policy_stamps,
    read_tactical_policy_stamp,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARTIFACTS = _REPO_ROOT / "training" / "artifacts" / "impostor"
_UTILITY_ES = _ARTIFACTS / "utility-es"
_POLICY_ES = _ARTIFACTS / "policy-es"

# The committed CREW artifact source (Task 18.19): the frozen training-side
# ``crew-owned-tasks-es`` genome the ``--crew-artifact`` fixtures copy from. It
# carries weights.json + its sidecar but NOT (yet) a stamp.json — 18.23's
# recording session writes that — so the fixtures synthesize one (``_make_crew_artifact``).
_CREW_OWNED_TASKS = (
    _REPO_ROOT / "training" / "artifacts" / "crew" / "crew-owned-tasks-es"
)

# The committed CREW artifact (Task 18.7): the agents-side copy of the frozen
# training-side ``crew-owned-tasks-es`` genome. Both sidecars record the SAME
# digest — the never-echoed provenance the crew stamp names and the on-disk
# read-back verifies against.
_CREW_WEIGHTS_DIGEST = (
    "bd6fdd0a030a01cc57f2ef8c95abf66f46d8cbc5ac270e04ae74a6cab587f19c"
)
_AGENTS_CREW_SIDECAR = (
    _REPO_ROOT / "agents" / "tactical" / "learned" / "crew_weights.json.sha256"
)
_TRAINING_CREW_SIDECAR = (
    _REPO_ROOT
    / "training"
    / "artifacts"
    / "crew"
    / "crew-owned-tasks-es"
    / "weights.json.sha256"
)


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


def _make_crew_artifact(tmp_path: Path) -> Path:
    """Build a ``--crew-artifact`` fixture dir from the committed crew genome (18.19).

    The committed ``training/artifacts/crew/crew-owned-tasks-es`` dir carries the
    frozen 27-weight owned-task genome + its sidecar but NOT (yet) a ``stamp.json``
    (18.23's recording session writes them), so the fixture copies it to a writable
    tmp dir and synthesizes the five-field crew ``stamp.json`` — its
    ``weights_sha256`` the HONEST committed sidecar digest (read at fixture time,
    never echoed), its ``encoder_version`` the ``crew-option-features-v2`` owned-task
    tag the genome rebuilds through.
    """

    dst = tmp_path / "crew-owned-tasks-es"
    shutil.copytree(_CREW_OWNED_TASKS, dst)
    digest = _sidecar_digest(dst)
    stamp = {
        "policy_id": "crew-owned-tasks-es",
        "method": "crew-utility-scorer-es",
        "encoder_version": "crew-option-features-v2",
        "weights_sha256": digest,
        "anchor_policy": "fsm-default",
    }
    (dst / "stamp.json").write_text(
        json.dumps(stamp, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return dst


def _crew_fixture_stamp(crew_dir: Path) -> CrewTacticalPolicyStamp:
    """The five-field crew stamp read straight from a fixture's synthesized stamp.json."""

    raw = (crew_dir / "stamp.json").read_text(encoding="utf-8")
    return CrewTacticalPolicyStamp.model_validate_json(raw)


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


def _install_crew_factory_capturing_spy(
    monkeypatch: pytest.MonkeyPatch, captured: dict[str, object]
) -> None:
    """Patch ``run_tournament.run_tournament_eval`` to capture the CREW seam (18.7).

    The crew twin of :func:`_install_factory_capturing_spy`: keyword-only
    ``agent_factory`` AND ``crew_policy_stamp``, BOTH with no default, so ``main``
    failing to thread EITHER the crew factory or the crew stamp also fails loud
    (TypeError). Records the factory + both stamps ``main`` threads, then delegates
    to the real harness so ``main`` still produces a valid report end-to-end.
    """

    def spy(
        *,
        seeds: Sequence[int],
        output_dir: Path,
        agent_factory: AgentFactory,
        crew_policy_stamp: CrewTacticalPolicyStamp,
        num_players: int,
        num_impostors: int,
        tasks_per_crewmate: int,
        max_ticks: int,
        force: bool,
        tactical_policy_stamp: TacticalPolicyStamp | None = None,
    ) -> TournamentReport:
        captured["agent_factory"] = agent_factory
        captured["crew_policy_stamp"] = crew_policy_stamp
        captured["tactical_policy_stamp"] = tactical_policy_stamp
        return _real_run_tournament_eval(
            seeds=seeds,
            output_dir=output_dir,
            agent_factory=agent_factory,
            crew_policy_stamp=crew_policy_stamp,
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
    """``--candidate-artifact`` threads the bake-off factory + the artifact stamp.

    Doubles as the Task-18.19 byte-identity pin for the candidate-only path: the
    spy's keyword-only signature has NO ``crew_policy_stamp`` param, so if ``main``
    threaded a crew stamp on a candidate-only run (it must not — that path is the
    single-side impostor recorder, unchanged by the 18.19 dual arm) this call would
    raise TypeError. Reaching rc == 0 is the proof the candidate-only path is
    untouched.
    """

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


# -- the opt-in learned CREW arm (Task 18.7) ----------------------------------


def _read_game_over_line(replay_path: Path) -> dict[str, object]:
    """The raw ``game_over`` JSON object from a replay (the on-disk byte inspector).

    Reads the recorded bytes directly — not through the typed reader — so a test
    can assert the ABSENCE of a key (``crew_tactical_policy``) that the writer
    OMITS when the stamp is ``None`` (the byte-identity discipline in
    :meth:`orchestrator.replay.ReplayLog.record_game_end`), which a typed reader
    would silently normalize away.
    """

    for line in replay_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if isinstance(record, dict) and record.get("kind") == "game_over":
            return record
    raise AssertionError(f"no game_over record in {replay_path}")


def test_resolve_learned_crew_factory_builds_factory_and_exact_stamp() -> None:
    """``learned-crew`` resolves to the crew factory + its EXACT five-field stamp.

    The crew twin of :func:`test_resolve_candidate_builds_factory_and_exact_stamp`:
    the factory is the committed :class:`LearnedCrewAgentFactory`, and the crew
    stamp's ``weights_sha256`` equals BOTH the agents-side crew sidecar digest and
    the frozen training-side ``crew-owned-tasks-es`` sidecar — the sha-verified
    provenance a learned-crew recording reads back from bytes.
    """

    factory, stamp = rt._resolve_learned_crew_factory()
    assert isinstance(factory, LearnedCrewAgentFactory)
    assert (
        stamp.policy_id,
        stamp.method,
        stamp.encoder_version,
        stamp.weights_sha256,
        stamp.anchor_policy,
    ) == (
        "crew-owned-tasks-es",
        "crew-utility-scorer-es",
        "crew-option-features-v2",
        _CREW_WEIGHTS_DIGEST,
        "fsm-default",
    )
    assert (
        stamp.weights_sha256
        == _AGENTS_CREW_SIDECAR.read_text(encoding="utf-8").split()[0]
    )
    assert (
        stamp.weights_sha256
        == _TRAINING_CREW_SIDECAR.read_text(encoding="utf-8").split()[0]
    )


def test_learned_crew_stamp_namespaces_are_disjoint_from_the_impostor_champion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The crew and impostor-champion stamps never share a namespace (18.7 guard).

    Positively: the crew stamp's ``policy_id`` / ``weights_sha256`` differ from the
    ``learned-champion`` auto-stamp's — the conflation guard's factual basis (a
    crew recording can never be re-read as an impostor-champion game). Mechanically:
    monkeypatching the guard's ``CHAMPION_POLICY_ID`` import site into a collision
    with the crew ``policy_id`` makes the arm fail loud, so the guard is a LIVE
    check, not a comment.
    """

    _, crew_stamp = rt._resolve_learned_crew_factory()
    _, champion_stamp = rt._resolve_agent_factory("learned-champion")
    assert champion_stamp is not None
    assert crew_stamp.policy_id != champion_stamp.policy_id
    assert crew_stamp.weights_sha256 != champion_stamp.weights_sha256

    # Force a collision on the impostor champion's policy_id namespace: the guard
    # reads ``CHAMPION_POLICY_ID`` from agents.tactical.learned.factory at call
    # time (a function-local import), so patching that import site trips it.
    monkeypatch.setattr(
        "agents.tactical.learned.factory.CHAMPION_POLICY_ID", "crew-owned-tasks-es"
    )
    with pytest.raises(SystemExit, match="conflation guard"):
        rt._resolve_learned_crew_factory()


def test_main_learned_crew_threads_factory_and_crew_stamp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--agent-factory learned-crew`` threads the crew factory + the crew stamp.

    The crew twin of :func:`test_main_candidate_threads_factory_and_auto_stamp`:
    the spy's keyword-only ``crew_policy_stamp`` (no default) makes a missing crew
    stamp fail loud, and the impostor-side ``tactical_policy_stamp`` stays ``None``
    (impostors remain the scripted FSM).
    """

    captured: dict[str, object] = {}
    _install_crew_factory_capturing_spy(monkeypatch, captured)

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--start-seed",
            "1004",
            "--max-ticks",
            "30",
            "--output-dir",
            str(tmp_path),
            "--agent-factory",
            "learned-crew",
            "--force",
        ]
    )

    assert rc == 0
    assert isinstance(captured["agent_factory"], LearnedCrewAgentFactory)
    crew_stamp = captured["crew_policy_stamp"]
    assert isinstance(crew_stamp, CrewTacticalPolicyStamp)
    assert crew_stamp.weights_sha256 == _CREW_WEIGHTS_DIGEST
    assert captured["tactical_policy_stamp"] is None


def test_main_learned_crew_stamps_replay_on_disk_read_back_never_echoed(
    tmp_path: Path,
) -> None:
    """The DoD e2e: a real crew run stamps the crew provenance on disk (exact).

    No spy — the production seam runs end-to-end and lands a ``game_over`` record.
    The crew stamp is asserted from the RECORDED BYTES via
    :func:`read_crew_tactical_policy_stamp`, its ``weights_sha256`` equal to the
    committed crew sidecar digest READ FROM THE SIDECAR FILE (the never-echoed
    discipline), while the impostor side records the absent = FSM default
    (:func:`read_tactical_policy_stamp` is ``None``).
    """

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--start-seed",
            "1004",
            "--output-dir",
            str(tmp_path),
            "--max-ticks",
            "200",
            "--agent-factory",
            "learned-crew",
        ]
    )

    assert rc == 0
    replay = tmp_path / "replay-seed-1004.jsonl"
    crew_stamp = read_crew_tactical_policy_stamp(replay)
    assert crew_stamp is not None
    assert (
        crew_stamp.weights_sha256
        == _AGENTS_CREW_SIDECAR.read_text(encoding="utf-8").split()[0]
    )
    assert (
        crew_stamp.policy_id,
        crew_stamp.method,
        crew_stamp.encoder_version,
        crew_stamp.anchor_policy,
    ) == (
        "crew-owned-tasks-es",
        "crew-utility-scorer-es",
        "crew-option-features-v2",
        "fsm-default",
    )
    # The impostor side is the scripted FSM (an absent tactical stamp).
    assert read_tactical_policy_stamp(replay) is None


def test_main_default_path_threads_no_crew_stamp_and_writes_no_crew_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The default path threads NO crew stamp and writes NO crew key (byte-identity).

    The crew edition of :func:`test_main_candidate_omitted_is_default_path`: the
    default-path spy has no ``crew_policy_stamp`` parameter, so ``main`` threading
    one would raise TypeError. Reaching rc == 0 pins that the fsm-default arm never
    threads it; then the on-disk ``game_over`` line carries no
    ``crew_tactical_policy`` key (the writer omits it when the stamp is ``None``)
    and :func:`read_crew_tactical_policy_stamp` returns ``None``.
    """

    captured: dict[str, object] = {}
    _install_default_path_spy(monkeypatch, captured)

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
    assert captured["tactical_policy_stamp"] is None
    replay = tmp_path / "replay-seed-0.jsonl"
    assert "crew_tactical_policy" not in _read_game_over_line(replay)
    assert read_crew_tactical_policy_stamp(replay) is None


def test_main_learned_crew_rejects_candidate_artifact(tmp_path: Path) -> None:
    """``learned-crew`` + ``--candidate-artifact`` is rejected loudly (mutual excl.).

    The artifact records an IMPOSTOR policy while the crew arm scores crewmates —
    combining them would conflate two movers in one recording, so the crew arm
    rejects the pairing before any game runs (mirroring the champion-vs-artifact
    mutual exclusion).
    """

    with pytest.raises(SystemExit, match="mutually exclusive"):
        rt.main(
            [
                "--num-games",
                "1",
                "--output-dir",
                str(tmp_path),
                "--max-ticks",
                "2",
                "--agent-factory",
                "learned-crew",
                "--candidate-artifact",
                str(_UTILITY_ES),
            ]
        )


def test_main_learned_crew_rejects_contradicting_explicit_stamp(
    tmp_path: Path,
) -> None:
    """An explicit impostor-champion stamp contradicts the crew arm's FSM impostor.

    The crew arm records the impostor side as the scripted FSM default (its
    ``auto_stamp`` is ``None``), so an explicit ``--tactical-policy-stamp`` carrying
    the utility-es champion fields contradicts that reference (first differing on
    ``policy_id``) and fails loud before any game runs.
    """

    stamp_path = tmp_path / "champion.json"
    stamp_path.write_text(
        _artifact_stamp(_UTILITY_ES).model_dump_json(), encoding="utf-8"
    )

    with pytest.raises(SystemExit, match="policy_id"):
        rt.main(
            [
                "--num-games",
                "1",
                "--output-dir",
                str(tmp_path),
                "--max-ticks",
                "2",
                "--agent-factory",
                "learned-crew",
                "--tactical-policy-stamp",
                str(stamp_path),
            ]
        )


# -- the dual-role co-evo arm (Task 18.19) ------------------------------------


def test_parse_crew_artifact_defaults_none(tmp_path: Path) -> None:
    """The flag omitted parses to ``None`` — the co-evo recorder is opt-in."""

    args = rt._parse_args(["--output-dir", str(tmp_path)])
    assert args.crew_artifact is None


def test_parse_crew_artifact_accepts_path(tmp_path: Path) -> None:
    """``--crew-artifact`` parses to a ``Path``."""

    crew = _make_crew_artifact(tmp_path)
    args = rt._parse_args(["--output-dir", str(tmp_path), "--crew-artifact", str(crew)])
    assert args.crew_artifact == crew


def test_load_crew_artifact_policy_builds_scorer_and_exact_stamp(
    tmp_path: Path,
) -> None:
    """``_load_crew_artifact_policy`` returns a v2 crew scorer + its OWN five-field stamp.

    The crew twin of :func:`test_resolve_candidate_builds_factory_and_exact_stamp`:
    the genome rebuilds through ``build_crew_scorer`` with an ``OwnedTaskOptionBasis``
    (the ``crew-option-features-v2`` 27-weight owned-task family), and the stamp
    comes from the artifact's OWN ``stamp.json`` with ``weights_sha256`` equal to the
    committed sidecar digest — the sha-verified provenance a co-evo recording reads
    back.
    """

    crew = _make_crew_artifact(tmp_path)
    policy, stamp = rt._load_crew_artifact_policy(crew)

    assert policy.encoder_version == "crew-option-features-v2"
    assert stamp == _crew_fixture_stamp(crew)
    assert stamp.weights_sha256 == _sidecar_digest(crew)
    assert (
        stamp.policy_id,
        stamp.method,
        stamp.encoder_version,
        stamp.anchor_policy,
    ) == (
        "crew-owned-tasks-es",
        "crew-utility-scorer-es",
        "crew-option-features-v2",
        "fsm-default",
    )


def test_load_crew_artifact_missing_stamp_fails_loud(tmp_path: Path) -> None:
    """A crew artifact without a ``stamp.json`` fails loud (the committed-dir case).

    The committed ``training/artifacts/crew`` dirs do NOT yet carry a ``stamp.json``,
    so the arm fails loud on a raw committed copy until 18.23 writes one.
    """

    raw = _copy_artifact(_CREW_OWNED_TASKS, tmp_path / "crew-owned-tasks-es")

    with pytest.raises(SystemExit, match="cannot read"):
        rt._load_crew_artifact_policy(raw)


def test_load_crew_artifact_sha_mismatch_fails_loud(tmp_path: Path) -> None:
    """A crew sidecar digest that does not match ``weights.json`` fails loud on load.

    The genome sha verification (the SAME shared ``load_candidate_weights`` the
    impostor arm uses) trips BEFORE any policy is built or any game runs.
    """

    crew = _make_crew_artifact(tmp_path)
    (crew / "weights.json.sha256").write_text(f"{'0' * 64}  weights.json\n")

    with pytest.raises(SystemExit, match="load/verify failed"):
        rt._load_crew_artifact_policy(crew)


def test_load_crew_artifact_stamp_sidecar_conflation_guard(tmp_path: Path) -> None:
    """A crew ``stamp.json`` naming a different digest than the sidecar fails loud.

    Weights + sidecar stay consistent (the genome loads), but the stamp's
    ``weights_sha256`` no longer equals the sidecar — the recording would carry a
    stamp that does not name the bytes it produced. The 18.19 conflation guard
    rejects it before any spend.
    """

    crew = _make_crew_artifact(tmp_path)
    stamp = json.loads((crew / "stamp.json").read_text(encoding="utf-8"))
    stamp["weights_sha256"] = "a" * 64
    (crew / "stamp.json").write_text(json.dumps(stamp, indent=2, sort_keys=True))

    with pytest.raises(SystemExit, match="conflation guard"):
        rt._load_crew_artifact_policy(crew)


def test_load_crew_artifact_impostor_dir_fails_loud() -> None:
    """An IMPOSTOR artifact handed to ``--crew-artifact`` fails loud, naming the families.

    The committed ``utility-es`` dir HAS a ``stamp.json`` — but its
    ``impostor-option-features-v1`` encoder names no rebuildable CREW family, so it
    fails HERE (before any game runs), pointing the operator at
    ``--candidate-artifact``. This is the impostor-in-crew-slot pin (the crew twin of
    the crew-in-impostor-slot guard below).
    """

    with pytest.raises(SystemExit, match="rebuildable crew family"):
        rt._load_crew_artifact_policy(_UTILITY_ES)


def test_resolve_candidate_rejects_crew_artifact(tmp_path: Path) -> None:
    """A CREW artifact handed to ``--candidate-artifact`` fails loud (crew-in-impostor).

    The vice-versa 18.19 guard: a crew ``stamp.json`` (its encoder in the ``crew-``
    namespace) in the impostor slot fails loud on the namespace BEFORE any spend,
    via ``_resolve_candidate_artifact`` / ``_resolve_agent_factory``, pointing the
    operator at ``--crew-artifact``.
    """

    crew = _make_crew_artifact(tmp_path)

    with pytest.raises(SystemExit, match="CREW policy"):
        rt._resolve_agent_factory("fsm-default", candidate_artifact=crew)


def test_main_crew_artifact_mutually_exclusive_with_learned_crew(
    tmp_path: Path,
) -> None:
    """``--crew-artifact`` + ``--agent-factory learned-crew`` is rejected loudly.

    The crew artifact selects the crew policy for a co-evo recording; the single-side
    ``learned-crew`` arm selects the committed crew champion — combining them would
    conflate two crew movers, so the arm rejects the pairing before any game runs.
    """

    crew = _make_crew_artifact(tmp_path)

    with pytest.raises(SystemExit, match="mutually exclusive"):
        rt.main(
            [
                "--num-games",
                "1",
                "--output-dir",
                str(tmp_path / "out"),
                "--max-ticks",
                "2",
                "--crew-artifact",
                str(crew),
                "--agent-factory",
                "learned-crew",
            ]
        )


def test_main_crew_artifact_mutually_exclusive_with_learned_champion(
    tmp_path: Path,
) -> None:
    """``--crew-artifact`` + ``--agent-factory learned-champion`` is rejected loudly.

    The mutual-exclusion guard covers BOTH single-side ``--agent-factory`` arms: a
    dual-role co-evo recording composes the impostor side through
    ``--candidate-artifact``, never through ``--agent-factory``.
    """

    crew = _make_crew_artifact(tmp_path)

    with pytest.raises(SystemExit, match="mutually exclusive"):
        rt.main(
            [
                "--num-games",
                "1",
                "--output-dir",
                str(tmp_path / "out"),
                "--max-ticks",
                "2",
                "--crew-artifact",
                str(crew),
                "--agent-factory",
                "learned-champion",
            ]
        )


def test_crew_artifact_cross_stamp_policy_id_collision_fails_loud(
    tmp_path: Path,
) -> None:
    """A dual recording whose two identities share a ``policy_id`` fails loud.

    The cross-stamp conflation guard: the crew fixture's ``stamp.json`` ``policy_id``
    is rewritten to collide with the ``utility-es`` impostor stamp (the digest stays
    HONEST so the loader still passes its own stamp/sidecar guard). Loaded on a dual
    ``--crew-artifact`` + ``--candidate-artifact`` recording, the two identities
    collide on ``policy_id`` and the guard rejects it before any game runs — the two
    movers on one recording must be DISTINCT.

    (The guard's ``weights_sha256`` arm is unreachable end-to-end with honest
    artifacts: each side's ``weights_sha256`` is forced to equal its own sidecar
    digest — which is the sha of its own weights bytes — so two distinct genomes can
    never share a digest; the collision can only ever be a ``policy_id`` one.)
    """

    crew = _make_crew_artifact(tmp_path)
    stamp = json.loads((crew / "stamp.json").read_text(encoding="utf-8"))
    stamp["policy_id"] = "utility-es"
    (crew / "stamp.json").write_text(json.dumps(stamp, indent=2, sort_keys=True))

    with pytest.raises(SystemExit, match="conflation"):
        rt._resolve_crew_artifact_arm(
            crew_artifact=crew, candidate_artifact=_UTILITY_ES
        )


def test_main_crew_artifact_dual_threads_factory_and_both_stamps(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A dual co-evo run threads the coevo factory + BOTH stamps (the spy pin).

    Both artifact flags: the crew spy's keyword-only ``crew_policy_stamp`` (no
    default) makes a missing crew stamp fail loud, and ``main`` threads the impostor
    ``tactical_policy_stamp`` (the ``utility-es`` artifact stamp) beside the crew
    stamp (the fixture stamp) — the dual-stamp co-evo recording's two identities, in
    distinct slots. Budget ``--num-games 1 --max-ticks 2``.
    """

    crew = _make_crew_artifact(tmp_path)
    captured: dict[str, object] = {}
    _install_crew_factory_capturing_spy(monkeypatch, captured)

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--output-dir",
            str(tmp_path / "out"),
            "--max-ticks",
            "2",
            "--crew-artifact",
            str(crew),
            "--candidate-artifact",
            str(_UTILITY_ES),
        ]
    )

    assert rc == 0
    assert callable(captured["agent_factory"])
    assert captured["tactical_policy_stamp"] == _artifact_stamp(_UTILITY_ES)
    assert captured["crew_policy_stamp"] == _crew_fixture_stamp(crew)


def test_main_crew_artifact_dual_stamps_replay_on_disk(tmp_path: Path) -> None:
    """The DoD e2e: a real dual co-evo run stamps BOTH identities on disk (exact).

    No spy — the production seam runs end-to-end at ``--max-ticks 200`` on the 4p/1i
    ``--start-seed 0`` roster, which lands a ``game_over`` record (empirically pinned:
    the committed ``utility-es`` impostor + the ``crew-owned-tasks-es`` crew pair
    resolve to an IMPOSTORS win well under 200 ticks; seed 1004 truncates for this
    pair, so seed 0 is chosen — the existing tests' "lands a game_over record"
    idiom). ``read_policy_stamps`` recovers BOTH five-field stamps from the RECORDED
    BYTES in DISTINCT typed slots; the two identities are DISTINCT on ``policy_id``
    AND ``weights_sha256``, and each ``weights_sha256`` equals the respective sidecar
    FILE read at test time (never an echoed constant). The fake provider comes from
    the root conftest autouse fixture.
    """

    crew = _make_crew_artifact(tmp_path)
    out_dir = tmp_path / "out"

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--start-seed",
            "0",
            "--output-dir",
            str(out_dir),
            "--max-ticks",
            "200",
            "--crew-artifact",
            str(crew),
            "--candidate-artifact",
            str(_UTILITY_ES),
        ]
    )

    assert rc == 0
    replay = out_dir / "replay-seed-0.jsonl"
    stamps = read_policy_stamps(replay)
    tactical = stamps.tactical
    crew_stamp = stamps.crew
    assert tactical is not None
    assert crew_stamp is not None

    # Both identities read back exact, from the recorded bytes.
    assert tactical == _artifact_stamp(_UTILITY_ES)
    assert crew_stamp == _crew_fixture_stamp(crew)

    # DISTINCT identities: the two movers on one recording can never be conflated.
    assert tactical.policy_id != crew_stamp.policy_id
    assert tactical.weights_sha256 != crew_stamp.weights_sha256

    # Each weights_sha256 equals the respective sidecar FILE read at test time.
    assert tactical.weights_sha256 == _sidecar_digest(_UTILITY_ES)
    assert crew_stamp.weights_sha256 == _sidecar_digest(crew)

    # The two sibling readers agree with the combined reader (same distinct slots).
    assert read_tactical_policy_stamp(replay) == tactical
    assert read_crew_tactical_policy_stamp(replay) == crew_stamp


def test_main_crew_artifact_crew_only_stamps_replay_on_disk(tmp_path: Path) -> None:
    """The DoD e2e: a crew-only ``--crew-artifact`` run stamps the crew side only.

    ``--crew-artifact`` alone at the same ``--start-seed 0 --max-ticks 200`` budget:
    the crew stamp is present in the recorded bytes (``read_policy_stamps`` /
    ``read_crew_tactical_policy_stamp``), while the impostor side records the absent =
    scripted-FSM default (``read_tactical_policy_stamp`` is ``None``).
    """

    crew = _make_crew_artifact(tmp_path)
    out_dir = tmp_path / "out"

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--start-seed",
            "0",
            "--output-dir",
            str(out_dir),
            "--max-ticks",
            "200",
            "--crew-artifact",
            str(crew),
        ]
    )

    assert rc == 0
    replay = out_dir / "replay-seed-0.jsonl"
    stamps = read_policy_stamps(replay)
    assert stamps.tactical is None
    assert stamps.crew is not None
    assert stamps.crew == _crew_fixture_stamp(crew)
    assert read_tactical_policy_stamp(replay) is None
    assert read_crew_tactical_policy_stamp(replay) == stamps.crew
