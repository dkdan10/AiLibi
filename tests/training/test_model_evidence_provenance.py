"""Input mutation gates; no fitted artifact or recorded corpus is rewritten."""

from __future__ import annotations

import json
import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from training.provenance import (
    DEFAULT_CORPUS,
    SOURCE_ROOT,
    derivation_files,
    fit_corpus_fingerprint,
    historical_fit_corpus_fingerprint,
    validate_evidence_scope,
    verify_fit_identity,
)
from training.surrogate.runner import load_surrogate_runner_factory
from training.bakeoff.harness import _load_conviction_bundle


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    target = tmp_path / "9p2i"
    target.mkdir()
    for name in ("roster.json", "MANIFEST.md", "splits.json", "replay-seed-1000.jsonl"):
        shutil.copyfile(DEFAULT_CORPUS / name, target / name)
    return target


def test_roster_mutation_moves_only_current_identity(corpus: Path) -> None:
    old = historical_fit_corpus_fingerprint(corpus)
    current = fit_corpus_fingerprint(corpus)
    roster = corpus / "roster.json"
    roster.write_text(
        roster.read_text().replace('"tasks_per_crewmate": 2', '"tasks_per_crewmate": 3')
    )
    assert historical_fit_corpus_fingerprint(corpus) == old
    assert fit_corpus_fingerprint(corpus) != current
    with pytest.raises(ValueError, match="drifted"):
        verify_fit_identity(
            artifact_dir=corpus.parent,
            corpus_dir=corpus,
            fingerprint_version=2,
            corpus_sha256=current,
            scope="current",
        )


def test_actual_derivation_change_moves_identity(corpus: Path, tmp_path: Path) -> None:
    root = tmp_path / "source"
    paths = [
        *derivation_files(),
        *(
            SOURCE_ROOT / name
            for name in ("engine/maps/canonical_1.yaml", "pyproject.toml", "uv.lock")
        ),
    ]
    for path in paths:
        dest = root / path.relative_to(SOURCE_ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
    before = fit_corpus_fingerprint(corpus, source_root=root)
    assert before == fit_corpus_fingerprint(corpus)
    feature_path = root / "training/surrogate/dataset.py"
    text = feature_path.read_text()
    assert "belief_suspicion=belief.suspicion" in text
    feature_path.write_text(
        text.replace(
            "belief_suspicion=belief.suspicion",
            "belief_suspicion=belief.suspicion + 0.125",
            1,
        )
    )
    assert fit_corpus_fingerprint(corpus, source_root=root) != before


def test_inert_report_is_not_a_fit_input(corpus: Path) -> None:
    before = fit_corpus_fingerprint(corpus)
    (corpus / "tournament-eval-report.json").write_text('{"invented":123}')
    assert fit_corpus_fingerprint(corpus) == before


def test_current_identity_has_explicit_positive_control(corpus: Path) -> None:
    verify_fit_identity(
        artifact_dir=corpus.parent,
        corpus_dir=corpus,
        fingerprint_version=2,
        corpus_sha256=fit_corpus_fingerprint(corpus),
        scope="current",
    )


@pytest.mark.parametrize("model", ["surrogate", "conviction"])
def test_current_loader_refuses_historical_fit(model: str) -> None:
    with pytest.raises(ValueError, match="historical version-one"):
        if model == "surrogate":
            load_surrogate_runner_factory(SOURCE_ROOT / "training/artifacts/surrogate")
        else:
            _load_conviction_bundle(SOURCE_ROOT / "training/artifacts/conviction", None)


def test_historical_diagnostic_restores_committed_models() -> None:
    assert callable(
        load_surrogate_runner_factory(
            SOURCE_ROOT / "training/artifacts/surrogate", evidence_scope="historical"
        )
    )
    model, _, _, _ = _load_conviction_bundle(
        SOURCE_ROOT / "training/artifacts/conviction", None, evidence_scope="historical"
    )
    assert model is not None


def test_historical_label_cannot_install_training_runner() -> None:
    with pytest.raises(ValueError, match="current model evidence"):
        load_surrogate_runner_factory(
            SOURCE_ROOT / "training/artifacts/surrogate",
            evidence_scope="historical",
            install_role="training-time-runner",
        )


def test_conviction_corpus_fence_cannot_be_omitted(tmp_path: Path) -> None:
    artifact = tmp_path / "conviction"
    shutil.copytree(SOURCE_ROOT / "training/artifacts/conviction", artifact)
    path = artifact / "fit-corpus.json"
    raw = json.loads(path.read_text())
    raw["corpus_sha256"] = "0" * 64
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="drifted"):
        _load_conviction_bundle(artifact, None, evidence_scope="historical")


def test_synthetic_scope_never_claims_corpus_provenance(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="outside the source"):
        validate_evidence_scope(
            "synthetic-test", SOURCE_ROOT / "training/artifacts/conviction"
        )
    validate_evidence_scope("synthetic-test", tmp_path)
    (tmp_path / "fit-corpus.json").write_text("{}")
    with pytest.raises(ValueError, match="fabricated"):
        validate_evidence_scope("synthetic-test", tmp_path)


def test_campaign_checks_source_definition_before_work(tmp_path: Path) -> None:
    from tests.training.test_coevo_driver import _make_config
    from training.bakeoff.map_elites import bakeoff_substrate_sha
    from training.coevo.driver import _validate_config

    config = replace(
        _make_config(tmp_path),
        evidence_scope="current",
        substrate_sha_kind="bakeoff_substrate_sha.v2",
        substrate_sha256=bakeoff_substrate_sha(),
    )
    _validate_config(config)
    assert not config.work_dir.exists()

    for bad in (
        replace(config, substrate_sha256="ab" * 32),
        replace(config, substrate_sha_kind="compute_substrate_sha.v2"),
        replace(config, substrate_sha_kind="bakeoff_substrate_sha"),
    ):
        with pytest.raises(ValueError, match="source definition|version-two"):
            _validate_config(bad)
    assert not config.work_dir.exists()


def test_conviction_columns_have_explicit_historical_exchange() -> None:
    from training.conviction.dataset import ConvictionMeetingRow, build_conviction_table

    row = build_conviction_table(SOURCE_ROOT / "replays/samples/4p1i").rows[0]
    current = row.model_dump_json()
    assert '"recorded_non_vent_flags"' in current
    assert '"rederived_flags"' not in current
    historical = row.to_historical_json()
    assert '"rederived_flags"' in historical
    assert ConvictionMeetingRow.from_historical_json(historical) == row
    with pytest.raises(ValueError):
        ConvictionMeetingRow.model_validate_json(historical)
    with pytest.raises(ValueError, match="historical conviction row"):
        ConvictionMeetingRow.from_historical_json(current)


@pytest.mark.parametrize(
    "variable",
    [
        "AILIBI_TESTIMONY_SHAPES",
        "AILIBI_TEMPORAL_OBSERVATIONS",
        "AILIBI_EVIDENCE_REASONING",
        "AILIBI_BOUNDED_REBUTTAL",
    ],
)
def test_current_campaign_refuses_unbound_runtime_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, variable: str
) -> None:
    from dataclasses import replace
    from tests.training.test_coevo_driver import _make_config
    from training.bakeoff.map_elites import bakeoff_substrate_sha
    from training.coevo.driver import _validate_config

    config = replace(
        _make_config(tmp_path),
        evidence_scope="current",
        substrate_sha_kind="bakeoff_substrate_sha.v2",
        substrate_sha256=bakeoff_substrate_sha(),
    )
    _validate_config(config)
    monkeypatch.setenv(variable, "1")
    with pytest.raises(ValueError, match="baseline .* profile"):
        _validate_config(config)
    assert not config.work_dir.exists()


def test_explicit_campaign_rollout_profile_survives_later_environment_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from orchestrator.replay import read_all_entries, recorded_experiment_config
    from training.coevo.rollout import rollout_coevo
    from training.provenance import current_campaign_environment

    frozen = current_campaign_environment()
    monkeypatch.setenv("AILIBI_EVIDENCE_REASONING", "1")
    monkeypatch.setenv("AILIBI_TESTIMONY_SHAPES", "1")
    rollout_coevo(
        None,
        None,
        3,
        output_dir=tmp_path,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
        max_ticks=100,
        environment=frozen,
    )
    entries = read_all_entries(tmp_path / "replay-seed-3.jsonl")
    assert recorded_experiment_config(entries) is None
    from orchestrator.replay import GameEndReplayEntry

    stop = entries[-1]
    assert isinstance(stop, GameEndReplayEntry)
    assert stop.substrate_flags is not None
    assert stop.substrate_flags["testimony_shapes"] is False
