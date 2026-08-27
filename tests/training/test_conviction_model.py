"""Tests for the conviction-economy model (Task 18.15).

Four fences, mirroring the surrogate suite's structure
(``tests/training/test_surrogate_*.py``):

* **The feature fence** — feature-by-feature provenance assertions (every
  feature derives only from the ``run_meeting`` inputs) plus the poison test
  (the builder never reads a fenced 15.11 column) plus the AST firewall
  (``training/conviction`` never imports ``eval.*`` — the labels are the
  referee's quantities, the Goodhart-adjacent seam).
* **The label mirror** — the flag census reproduces the referee's own
  production census (``eval.meeting_quality.compute_supply_gauges`` + the
  persisted vent merge) exactly on the committed sample sets, and the
  observation-backed conversion predicate is pinned on synthetic transcripts
  (subject-aware backing, the 15.19 semantics).
* **Determinism + the artifact** — double-fit byte-stability, float-hex
  round-trip, sha sidecar verification, layout-drift fail-loud, and the
  sha-keyed staleness machinery under the ~143× rule.
* **The committed corpus artifact + verdict** — the frozen weights round-trip
  byte-stably, a refit is ULP-equivalent (the platform caveat), the committed
  cap re-derives from the fit-side meeting count, and the committed
  ``verdict.json`` reproduces from the frozen weights on the held-out split
  with the GO consequence mapping 18.16 consumes.
"""

from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pytest

from engine.entities import PlayerId, Role
from eval.meeting_quality import compute_supply_gauges
from eval.validity import assemble_tournament_report
from meetings.schemas import (
    AccusationClaim,
    FoundBodyObservation,
    MeetingTranscript,
    MeetingTurn,
    SawPlayerObservation,
    SawVentObservation,
)
from training.conviction.dataset import (
    CONVICTION_FEATURE_NAMES,
    CONVICTION_FEATURE_PROVENANCE,
    CONVICTION_PROVENANCE_SOURCES,
    CONVICTION_READABLE_CANDIDATE_FIELDS,
    CONVICTION_READABLE_ROW_FIELDS,
    ConvictionMeetingRow,
    ConvictionTable,
    ConvictionWalkGateError,
    _meeting_features,
    _observation_backed_impostor_subjects,
    build_conviction_table,
    require_clean_walk,
    validate_conviction_split,
)
from training.conviction.fidelity import (
    CONVICTION_CONVERSION_CEILING_RATIO,
    CONVICTION_SPEARMAN_BAR,
    ConvictionFidelityReport,
    decide_conviction_go,
    load_conviction_verdict,
    run_conviction_fidelity,
    spearman_rank_correlation,
)
from training.conviction.model import (
    ConvictionEconomyModel,
    ConvictionStalenessCap,
    ConvictionStalenessExceededError,
    ConvictionUseCounter,
    derive_conviction_max_uses,
    fit_corpus_conviction_model,
    load_conviction_model_artifact,
    load_conviction_staleness_cap,
    write_conviction_model_artifact,
)
from training.surrogate.dataset import (
    BeliefRenderParity,
    CandidateFeatures,
    MeetingTableRow,
    SurrogateSplits,
    build_meeting_table,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"
_CORPUS = _REPO_ROOT / "replays" / "ml_corpus" / "9p2i"
_ARTIFACT_DIR = _REPO_ROOT / "training" / "artifacts" / "conviction"
_CONVICTION_MODULES = tuple(
    sorted((_REPO_ROOT / "training" / "conviction").glob("*.py"))
)


@pytest.fixture(scope="module")
def nine_conviction() -> ConvictionTable:
    """The 9p2i sample-set conviction table (~2s; shared)."""

    return build_conviction_table(_NINE)


@pytest.fixture(scope="module")
def four_conviction() -> ConvictionTable:
    """The 4p1i sample-set conviction table (~1s; shared)."""

    return build_conviction_table(_FOUR)


@pytest.fixture(scope="module")
def corpus_conviction() -> ConvictionTable:
    """The committed 150-game corpus conviction table (~5s; shared)."""

    return build_conviction_table(_CORPUS)


# ---------------------------------------------------------------------------
# The feature fence
# ---------------------------------------------------------------------------


def test_feature_provenance_covers_every_feature_with_run_meeting_sources() -> None:
    """Feature-by-feature provenance: complete, non-empty, fence-compliant.

    The task hint's live-parity argument re-run as assertions, not a
    docstring: every feature declares the ``run_meeting``-time input(s) it
    derives from, and every declared source is one of the four protocol
    inputs (``meeting_id`` / ``trigger`` / ``state`` / a named
    ``MeetingAwareAgent`` accessor). A transcript-derived source cannot even
    be spelled — the vocabulary has no entry for it.
    """

    assert tuple(CONVICTION_FEATURE_PROVENANCE) == CONVICTION_FEATURE_NAMES
    for feature, sources in CONVICTION_FEATURE_PROVENANCE.items():
        assert sources, f"feature {feature!r} declares no provenance"
        unknown = [s for s in sources if s not in CONVICTION_PROVENANCE_SOURCES]
        assert unknown == [], (
            f"feature {feature!r} declares sources {unknown} outside the "
            "run_meeting input universe"
        )


def test_conviction_modules_never_import_eval() -> None:
    """The AST firewall (the 18.15 integration-risk guard, entrant-style).

    The labels are exactly the quantities the referee gates, so
    ``training/conviction`` mirrors their assembly from recorded bytes and
    must never read ``eval/watchability.py`` — enforced structurally, like
    the bake-off entrants (``tests/training/test_bakeoff_harness.py``), as a
    ban on EVERY ``eval.*`` import in the package's source.
    """

    assert _CONVICTION_MODULES, "training/conviction has no modules to scan"
    offenders: list[tuple[str, int, str]] = []
    for path in _CONVICTION_MODULES:
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "eval" or alias.name.startswith("eval."):
                        offenders.append((str(path), node.lineno, alias.name))
            elif isinstance(node, ast.ImportFrom):
                module = node.module
                if module is not None and (
                    module == "eval" or module.startswith("eval.")
                ):
                    offenders.append((str(path), node.lineno, module))
    assert offenders == [], (
        "training/conviction must not import eval.* (the labels are mirrored "
        f"from recorded bytes, never imported); offenders: {offenders!r}"
    )


def _poison_value(value: object) -> object:
    """A type-preserving corruption (bool checked before int — bool is int)."""

    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1000
    if isinstance(value, float):
        return value + 999.0
    if isinstance(value, str):
        return value + "-poisoned"
    if value is None:
        return "poisoned"
    return value


def _poison_row(row: MeetingTableRow) -> MeetingTableRow:
    """Corrupt every 15.11 column OUTSIDE the declared readable fence.

    ``model_copy`` skips validation, so the poisoned rows carry impossible
    values in every fenced column — labels, roles, transcript-derived flag
    structure, omniscient window stats — while the readable columns stay
    byte-identical. The poison sets are DERIVED (all fields minus the
    readable allowlist), so a future table column lands fenced by default.
    """

    fenced_row_fields = set(MeetingTableRow.model_fields) - set(
        CONVICTION_READABLE_ROW_FIELDS
    )
    fenced_candidate_fields = set(CandidateFeatures.model_fields) - set(
        CONVICTION_READABLE_CANDIDATE_FIELDS
    )
    poisoned_candidates = tuple(
        feat.model_copy(
            update={
                name: _poison_value(getattr(feat, name))
                for name in fenced_candidate_fields
            }
        )
        for feat in row.candidates
    )
    return row.model_copy(
        update={
            **{
                name: _poison_value(getattr(row, name))
                for name in fenced_row_fields
                if name != "candidates"
            },
            "candidates": poisoned_candidates,
        }
    )


def test_features_read_only_the_fenced_columns() -> None:
    """The poison test: fenced columns cannot move a single feature value.

    Every label, role, transcript-derived, and omniscient-window column of
    every (meeting, voter) row is corrupted; the reduced feature vectors must
    stay byte-identical for every meeting of the committed 4p1i sample set.
    """

    table = build_meeting_table(_FOUR)
    by_meeting: dict[tuple[int, str], list[MeetingTableRow]] = {}
    for row in table.rows:
        by_meeting.setdefault((row.seed, row.meeting_id), []).append(row)
    assert by_meeting, "the 4p1i sample set must carry meetings"
    for key, rows in by_meeting.items():
        clean = _meeting_features(rows)
        poisoned = _meeting_features([_poison_row(row) for row in rows])
        assert poisoned == clean, (
            f"meeting {key}: poisoning fenced columns moved the features — "
            "the builder reads outside the declared fence"
        )


# ---------------------------------------------------------------------------
# The label mirror
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("sample_dir", [_NINE, _FOUR])
def test_flag_labels_reproduce_the_referee_census(sample_dir: Path) -> None:
    """The mirrored flag label equals the production census, integer-exact.

    The referee's ``flags_per_meeting`` numerator is the RECORDED non-vent
    census (``eval.meeting_quality.compute_supply_gauges``, which reads
    ``recorded_contradiction_flags``) plus the recorded ``vent_sighting``
    subset (``eval/watchability.py::_persisted_vent_flag_count`` — disjoint by
    construction). This is the mirror invariant, not a value pin: both sides
    move together at any re-record or census correction, and the equality is
    what proves the ``training/`` mirror never drifted from the instrument it
    mirrors. The eval import lives HERE (tests are not firewalled) precisely so
    the package never needs it.
    """

    table = build_conviction_table(sample_dir)
    report = assemble_tournament_report(sample_dir)
    supply = compute_supply_gauges(report.games)
    persisted_vent = sum(
        1
        for game in report.games
        for meeting in game.meetings
        for flag in meeting.contradictions
        if flag.kind == "vent_sighting"
    )
    assert sum(row.rederived_flags for row in table.rows) == supply.total_flags
    assert sum(row.persisted_vent_flags for row in table.rows) == persisted_vent
    assert table.flags_minted_total == supply.total_flags + persisted_vent
    assert table.meetings_total == supply.meetings_total


def test_sample_conversion_census_pins(
    nine_conviction: ConvictionTable, four_conviction: ConvictionTable
) -> None:
    """The mirrored conversion census on the committed baseline-6 samples.

    Regression pins (re-derived from bytes, re-pinned at any re-record):
    the observation-backed conversion economy the 18.11 gate shipped is
    DENSE on baseline 6 — conversion is no longer the scarce quantity the
    §3.1 census measured at baseline 5.
    """

    assert nine_conviction.meetings_total == 152  # was 165
    assert nine_conviction.conversion_attempts_total == 115  # was 136
    assert nine_conviction.conversions_total == 80  # was 78
    assert four_conviction.meetings_total == 40  # was 39
    assert four_conviction.conversion_attempts_total == 31  # was 30
    assert four_conviction.conversions_total == 19  # was 9


def _turn(
    index: int,
    speaker: str,
    *,
    claims: tuple[AccusationClaim, ...] = (),
    observations: tuple[
        SawPlayerObservation | SawVentObservation | FoundBodyObservation, ...
    ] = (),
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"turn-{index}",
        turn_index=index,
        speaker=speaker,
        turn_kind="opening" if index == 0 else "reply",
        reply_to=None,
        observations=observations,
        claims=claims,
        free_text="",
    )


def _accuse(against: str) -> AccusationClaim:
    return AccusationClaim(
        type="accusation", against=against, confidence=0.9, reason="test"
    )


def test_observation_backed_conversion_semantics() -> None:
    """The subject-aware (Task 15.19) backing predicate, pinned synthetically.

    Backed ⇔ a true impostor enters the accused universe through a NON-self
    accusation edge AND some accusing turn carries a first-hand sighting
    whose subject IS the accused. A sighting of someone else, a crew
    accused, a self-accusation-only subject, and a body report never back;
    a vent sighting backs exactly like a player sighting.
    """

    roles: dict[PlayerId, Role] = {
        "P1": "CREWMATE",
        "P2": "IMPOSTOR",
        "P3": "CREWMATE",
        "P4": "IMPOSTOR",
    }
    saw_p2 = SawPlayerObservation(
        type="saw_player", tick=5, subject="P2", room="cafeteria"
    )
    saw_p3 = SawPlayerObservation(
        type="saw_player", tick=5, subject="P3", room="cafeteria"
    )
    vent_p4 = SawVentObservation(type="saw_vent", tick=6, subject="P4", room="medbay")
    body = FoundBodyObservation(type="found_body", tick=7, body_of="P3", room="storage")

    # Accusation of an impostor backed by a same-turn sighting of that subject.
    backed = _observation_backed_impostor_subjects(
        MeetingTranscript(
            turns=(_turn(0, "P1", claims=(_accuse("P2"),), observations=(saw_p2,)),)
        ),
        roles,
    )
    assert backed == frozenset({"P2"})

    # A sighting of someone ELSE never backs (the exploit 15.19 closed).
    assert (
        _observation_backed_impostor_subjects(
            MeetingTranscript(
                turns=(_turn(0, "P1", claims=(_accuse("P2"),), observations=(saw_p3,)),)
            ),
            roles,
        )
        == frozenset()
    )

    # A crew accused never counts, even observation-backed.
    assert (
        _observation_backed_impostor_subjects(
            MeetingTranscript(
                turns=(_turn(0, "P1", claims=(_accuse("P3"),), observations=(saw_p3,)),)
            ),
            roles,
        )
        == frozenset()
    )

    # A self-accusation-only subject never enters the accused universe.
    assert (
        _observation_backed_impostor_subjects(
            MeetingTranscript(
                turns=(_turn(0, "P2", claims=(_accuse("P2"),), observations=(saw_p2,)),)
            ),
            roles,
        )
        == frozenset()
    )

    # A body report structurally cannot back; a vent sighting backs.
    assert (
        _observation_backed_impostor_subjects(
            MeetingTranscript(
                turns=(_turn(0, "P1", claims=(_accuse("P2"),), observations=(body,)),)
            ),
            roles,
        )
        == frozenset()
    )
    assert _observation_backed_impostor_subjects(
        MeetingTranscript(
            turns=(_turn(0, "P1", claims=(_accuse("P4"),), observations=(vent_p4,)),)
        ),
        roles,
    ) == frozenset({"P4"})


def test_row_invariants_fail_loud(nine_conviction: ConvictionTable) -> None:
    """The row validators refuse an internally-inconsistent row."""

    row = nine_conviction.rows[0]
    with pytest.raises(ValueError, match="flags_minted"):
        ConvictionMeetingRow(
            **{
                **row.model_dump(),
                "flags_minted": row.flags_minted + 1,
            }
        )
    with pytest.raises(ValueError, match="CONVICTION_FEATURE_NAMES"):
        ConvictionMeetingRow(
            **{
                **row.model_dump(),
                "features": {"not_a_feature": 1.0},
            }
        )


# ---------------------------------------------------------------------------
# Determinism + the artifact machinery
# ---------------------------------------------------------------------------


def _fit_rows(table: ConvictionTable) -> list[ConvictionMeetingRow]:
    return list(table.rows)


def test_fit_is_deterministic_and_serializes_byte_stably(
    nine_conviction: ConvictionTable,
) -> None:
    """Two fits over the same rows serialize to byte-identical artifacts."""

    first = ConvictionEconomyModel()
    second = ConvictionEconomyModel()
    first.fit(_fit_rows(nine_conviction))
    second.fit(_fit_rows(nine_conviction))
    assert first.to_artifact_json() == second.to_artifact_json()


def test_artifact_round_trips_with_sha_sidecar(
    nine_conviction: ConvictionTable, tmp_path: Path
) -> None:
    """Write → load is the identity; a tampered sidecar fails loud."""

    model = ConvictionEconomyModel()
    model.fit(_fit_rows(nine_conviction))
    digest = write_conviction_model_artifact(model, tmp_path, max_uses=1234)
    loaded, loaded_digest = load_conviction_model_artifact(tmp_path)
    assert loaded_digest == digest
    assert loaded.to_artifact_json() == model.to_artifact_json()
    cap = load_conviction_staleness_cap(tmp_path)
    assert cap == ConvictionStalenessCap(
        weights_sha256=digest, max_uses=1234, unit="meetings"
    )
    sample = nine_conviction.rows[0].features
    assert loaded.predict(sample) == model.predict(sample)

    sidecar = tmp_path / "conviction-model.json.sha256"
    sidecar.write_text("0" * 64 + "  conviction-model.json\n")
    with pytest.raises(ValueError, match="sidecar mismatch"):
        load_conviction_model_artifact(tmp_path)


def test_artifact_layout_drift_fails_loud(
    nine_conviction: ConvictionTable,
) -> None:
    """A drifted format marker or feature layout must never silently load."""

    model = ConvictionEconomyModel()
    model.fit(_fit_rows(nine_conviction))
    payload = model.to_artifact_json()
    with pytest.raises(ValueError, match="format"):
        ConvictionEconomyModel.from_artifact_json(
            payload.replace("conviction-model.v1", "conviction-model.v0")
        )
    with pytest.raises(ValueError, match="feature_names"):
        ConvictionEconomyModel.from_artifact_json(
            payload.replace('"alive_count"', '"alive_count_drifted"', 1)
        )


def test_unfitted_predict_and_drifted_keys_fail_loud(
    nine_conviction: ConvictionTable,
) -> None:
    model = ConvictionEconomyModel()
    with pytest.raises(RuntimeError, match="before fit"):
        model.predict(nine_conviction.rows[0].features)
    model.fit(_fit_rows(nine_conviction))
    with pytest.raises(ValueError, match="missing"):
        model.predict({"alive_count": 4.0})
    with pytest.raises(ValueError, match="unexpected"):
        model.predict({**dict(nine_conviction.rows[0].features), "not_a_feature": 1.0})
    with pytest.raises(ValueError, match="refusing to install"):
        ConvictionEconomyModel().fit([])


def test_predict_accepts_any_feature_insertion_order(
    nine_conviction: ConvictionTable,
) -> None:
    """Insertion order is not part of the public seam (Codex review, PR #302).

    The vector is always assembled by indexing the canonical name order, so a
    live consumer may build the mapping in any order; only the KEY SET is the
    contract.
    """

    model = ConvictionEconomyModel()
    model.fit(_fit_rows(nine_conviction))
    features = nine_conviction.rows[0].features
    reversed_order = dict(reversed(list(features.items())))
    assert tuple(reversed_order) != tuple(features)
    assert model.predict(reversed_order) == model.predict(features)


def test_staleness_machinery_follows_the_143x_rule() -> None:
    """derive → cap → counter: the ~143× rule, sha-keyed, fail-loud."""

    assert derive_conviction_max_uses(367) == 52_481
    with pytest.raises(ValueError, match="positive fit-side meeting count"):
        derive_conviction_max_uses(0)

    cap = ConvictionStalenessCap(weights_sha256="a" * 64, max_uses=2, unit="meetings")
    counter = ConvictionUseCounter(cap)
    assert counter.record_use(weights_sha256="a" * 64) == 1
    assert counter.record_use(weights_sha256="a" * 64) == 2
    with pytest.raises(ConvictionStalenessExceededError, match="staleness cap"):
        counter.record_use(weights_sha256="a" * 64)
    with pytest.raises(ValueError, match="never meters two artifacts"):
        ConvictionUseCounter(cap).record_use(weights_sha256="b" * 64)


# ---------------------------------------------------------------------------
# The walk gate + the fidelity harness
#
# Task 19.27: this section's tests carry the campaign marker individually —
# `training/conviction/fidelity.py` is a FREEZE-column row of the tier map
# (training/README.md §2, "The fidelity harnesses"), so its HARNESS-MECHANICS
# tests run in the weekly campaign tier, exactly like the surrogate twin
# (tests/training/test_surrogate_fidelity.py). The rest of this module is the
# KEEP-row conviction model and stays in the default gate — including the
# committed-corpus census/artifact/verdict pins below, which ARE the KEEP
# row's measured basis (Spearman 0.5782, recall 45/47) and so must keep
# executing on every gate run. The mixed-file split is pinned by
# tests/training/test_suite_tiers.py.
# ---------------------------------------------------------------------------


def _parity(raw_mismatches: int, trust_mismatches: int = 0) -> BeliefRenderParity:
    return BeliefRenderParity(
        replay_set_dir="synthetic",
        games_total=1,
        meetings_total=1,
        rows_total=1,
        cells_compared=10,
        raw_mismatches=raw_mismatches,
        trust_mismatches=trust_mismatches,
        max_raw_abs_delta=0.2 if raw_mismatches else 0.0,
        j1_divergent_cells=3,
        j1_divergent_rows=2,
        j1_divergent_fit_cells=None,
        j1_divergent_test_cells=None,
        j1_max_abs_divergence=0.06,
    )


@pytest.mark.campaign
def test_walk_gate_refuses_raw_mismatches() -> None:
    """The 17.10 discipline, mechanical: 0 raw mismatches or no fit.

    The J1 render-clamp divergence is a measured, reported quantity and never
    trips the gate; any raw fold mismatch does.
    """

    clean = _parity(0)
    assert require_clean_walk(clean) is clean
    with pytest.raises(ConvictionWalkGateError, match="drifted walk"):
        require_clean_walk(_parity(1))
    with pytest.raises(ConvictionWalkGateError, match="drifted walk"):
        require_clean_walk(_parity(0, trust_mismatches=2))


@pytest.mark.campaign
def test_fidelity_requires_a_committed_split(
    nine_conviction: ConvictionTable,
) -> None:
    """The verdict is a single pre-registered held-out evaluation — a
    split-less baseline sample set has no held-out side to take it on."""

    assert nine_conviction.splits is None
    with pytest.raises(ValueError, match="no committed splits.json"):
        run_conviction_fidelity(nine_conviction)


@pytest.mark.campaign
def test_fit_corpus_entry_requires_a_committed_split() -> None:
    """The corpus fit entry walks the 17.10 gate, then refuses a split-less set."""

    with pytest.raises(ValueError, match="no committed splits.json"):
        fit_corpus_conviction_model(_FOUR)


def _with_splits(
    table: ConvictionTable,
    *,
    train: tuple[int, ...],
    val: tuple[int, ...],
    test: tuple[int, ...],
) -> ConvictionTable:
    return table.model_copy(
        update={"splits": SurrogateSplits(train=train, val=val, test=test)}
    )


@pytest.mark.campaign
def test_fidelity_rejects_a_leaky_or_partial_split(
    four_conviction: ConvictionTable,
) -> None:
    """The committed split must PARTITION the games before any row selection
    (Codex review, PR #302 — the surrogate's ``_game_folds`` discipline).

    An overlapping seed would fit on a held-out game (the leak the single
    pre-registered evaluation must fail closed on); an omitted or unknown
    seed means the split does not describe this table.
    """

    seeds = four_conviction.seeds
    with pytest.raises(ValueError, match="leaks games across the fit/test"):
        run_conviction_fidelity(
            _with_splits(
                four_conviction, train=seeds[:-1], val=(), test=(seeds[-2], seeds[-1])
            )
        )
    with pytest.raises(ValueError, match="omits table games"):
        run_conviction_fidelity(
            _with_splits(four_conviction, train=seeds[:-2], val=(), test=(seeds[-1],))
        )
    with pytest.raises(ValueError, match="seeds absent from the table"):
        run_conviction_fidelity(
            _with_splits(
                four_conviction, train=seeds[:-1], val=(), test=(seeds[-1], 999_999)
            )
        )
    # The same gate guards the corpus fit entry's fit-side selection.
    with pytest.raises(ValueError, match="leaks games across the fit/test"):
        validate_conviction_split(
            _with_splits(four_conviction, train=seeds, val=(), test=(seeds[0],))
        )


@pytest.mark.campaign
def test_spearman_is_tie_aware_and_fails_loud_on_degenerate_input() -> None:
    perfect = spearman_rank_correlation(
        np.asarray([1.0, 2.0, 3.0]), np.asarray([10.0, 20.0, 30.0])
    )
    assert perfect == pytest.approx(1.0)
    inverted = spearman_rank_correlation(
        np.asarray([3.0, 2.0, 1.0]), np.asarray([10.0, 20.0, 30.0])
    )
    assert inverted == pytest.approx(-1.0)
    # Ties take average ranks: [1, 2, 2] vs [1, 2, 3] correlates below 1.
    tied = spearman_rank_correlation(
        np.asarray([1.0, 2.0, 2.0]), np.asarray([1.0, 2.0, 3.0])
    )
    assert tied == pytest.approx(0.8660254037844387)
    with pytest.raises(ValueError, match="constant side"):
        spearman_rank_correlation(
            np.asarray([1.0, 1.0, 1.0]), np.asarray([1.0, 2.0, 3.0])
        )
    with pytest.raises(ValueError, match="paired samples"):
        spearman_rank_correlation(np.asarray([1.0]), np.asarray([1.0, 2.0]))


def _synthetic_report(
    *, flag_spearman: float, conversion_recall: float, voice_driven_share: float
) -> ConvictionFidelityReport:
    return ConvictionFidelityReport(
        replay_set_dir="synthetic",
        games_total=10,
        fit_games=8,
        test_games=2,
        fit_meetings=40,
        test_meetings=10,
        flag_spearman=flag_spearman,
        flag_mae=0.5,
        test_flags_total=12,
        fit_flags_total=50,
        conversions_fit=20,
        conversions_test=4,
        conversion_attempts_test=6,
        predicted_conversions=4,
        true_positives=int(round(conversion_recall * 4)),
        false_positives=0,
        false_negatives=4 - int(round(conversion_recall * 4)),
        true_negatives=6,
        conversion_recall=conversion_recall,
        conversion_precision=1.0,
        conversion_accuracy=0.9,
        test_ejections=8,
        test_reachable=int(round((1.0 - voice_driven_share) * 8)),
        voice_driven_share=voice_driven_share,
    )


@pytest.mark.campaign
def test_verdict_consequence_mapping_is_pre_committed() -> None:
    """GO ⇒ ships/gating/training-signal; NO-GO (either axis) ⇒
    absent/advisory/diagnostic-only — the machine-readable mapping 18.16
    branches on, never a prose reading."""

    go = decide_conviction_go(
        _synthetic_report(
            flag_spearman=0.6, conversion_recall=0.75, voice_driven_share=0.25
        ),
        weights_sha256="a" * 64,
    )
    assert go.verdict == "GO"
    assert go.spearman_bar == CONVICTION_SPEARMAN_BAR
    assert go.conversion_bar == pytest.approx(
        CONVICTION_CONVERSION_CEILING_RATIO * 0.75
    )
    assert (go.fitness_term, go.prescreen_role, go.model_role) == (
        "ships",
        "gating",
        "training-signal",
    )

    low_spearman = decide_conviction_go(
        _synthetic_report(
            flag_spearman=0.49, conversion_recall=1.0, voice_driven_share=0.25
        ),
        weights_sha256="a" * 64,
    )
    assert low_spearman.verdict == "NO-GO"
    assert not low_spearman.meets_spearman_bar
    assert low_spearman.meets_conversion_bar

    low_recall = decide_conviction_go(
        _synthetic_report(
            flag_spearman=0.9, conversion_recall=0.5, voice_driven_share=0.25
        ),
        weights_sha256="a" * 64,
    )
    assert low_recall.verdict == "NO-GO"
    assert low_recall.meets_spearman_bar
    assert not low_recall.meets_conversion_bar
    for no_go in (low_spearman, low_recall):
        assert (no_go.fitness_term, no_go.prescreen_role, no_go.model_role) == (
            "absent",
            "advisory",
            "diagnostic-only",
        )


# ---------------------------------------------------------------------------
# The committed corpus artifact + verdict
# ---------------------------------------------------------------------------


def test_corpus_census_pins(corpus_conviction: ConvictionTable) -> None:
    """The baseline-6 corpus economy, pinned (re-derived at any re-record)."""

    assert corpus_conviction.games_total == 150
    assert corpus_conviction.meetings_total == 432  # was 463
    assert corpus_conviction.ejections_total == 280  # was 302
    # Every recorded contradiction on the set, vents included: the label is now
    # exactly len(entry.contradictions) per meeting (308 vent + 120 transcript).
    # The retired transcript re-derivation reached 431 by losing 43 recorded
    # flags and minting 46 the record never carried.
    assert corpus_conviction.flags_minted_total == 428  # was 431
    assert corpus_conviction.conversion_attempts_total == 336  # was 394
    assert corpus_conviction.conversions_total == 239
    splits = corpus_conviction.splits
    assert splits is not None
    fit_seeds = frozenset(splits.train) | frozenset(splits.val)
    assert (
        sum(1 for r in corpus_conviction.rows if r.seed in fit_seeds) == 345
    )  # was 367


def test_committed_artifact_round_trips_and_the_refit_no_longer_matches(
    corpus_conviction: ConvictionTable,
) -> None:
    """Byte-stable round trip, one sha across three files -- and a refit that
    now DIVERGES, because the corpus moved and the fit did not.

    The round trip and the sha agreement are properties of the format and of the
    artifact's internal consistency; they hold on any corpus. The refit
    equivalence was a property of the GROUNDING: the committed weights were that
    refit, so it reproduced them to float ULP (byte-identical on the recording
    platform, ULP-equivalent elsewhere -- numpy's SIMD reduction grouping varies
    by CPU).

    The baseline-7 record re-recorded ``replays/ml_corpus`` without re-fitting the
    conviction model (a NAMED follow-up, audits/audit-phase-20-baseline-7.md
    §10.2), so a refit on the live corpus is a different model and the pin
    inverts: the fitted parameters must DISAGREE by more than float noise, while
    the schema stays identical. The committed staleness cap keys to the
    artifact's OWN fit-side count (367 under the ~143× rule), never to the live
    corpus's 345 -- asserting it against the live count would launder a stale cap
    as a current one. When the re-ground lands this test fails, and the
    equivalence pin comes back.
    """

    committed_json = (_ARTIFACT_DIR / "conviction-model.json").read_text()
    model, digest = load_conviction_model_artifact(_ARTIFACT_DIR)
    assert model.to_artifact_json() == committed_json

    cap = load_conviction_staleness_cap(_ARTIFACT_DIR)
    assert cap.weights_sha256 == digest
    assert cap.unit == "meetings"
    assert cap.max_uses == derive_conviction_max_uses(367) == 52_481

    splits = corpus_conviction.splits
    assert splits is not None
    fit_seeds = frozenset(splits.train) | frozenset(splits.val)
    live_fit_rows = [row for row in corpus_conviction.rows if row.seed in fit_seeds]
    # The live fit side is 345 meetings; the cap above is keyed to 367.
    assert len(live_fit_rows) == 345
    refit = ConvictionEconomyModel()
    refit.fit(live_fit_rows)
    import json

    committed = json.loads(committed_json)
    refitted = json.loads(refit.to_artifact_json())
    # Same schema, different numbers -- which is what "a different fit" means.
    assert set(committed) == set(refitted)
    diverged = 0
    for key, value in committed.items():
        if isinstance(value, list) and value and value[0].startswith(("0x", "-0x")):
            if [float.fromhex(v) for v in refitted[key]] != pytest.approx(
                [float.fromhex(v) for v in value], rel=1e-9, abs=1e-12
            ):
                diverged += 1
        elif isinstance(value, str) and value.startswith(("0x", "-0x")):
            if float.fromhex(refitted[key]) != pytest.approx(
                float.fromhex(value), rel=1e-9, abs=1e-12
            ):
                diverged += 1
        else:
            assert refitted[key] == value, f"artifact field {key!r} drifted"
    assert diverged > 0, (
        "the refit reproduces the committed weights to ULP -- either the ML "
        "re-ground landed (delete this tripwire and restore the equivalence "
        "pin) or the corpus never moved"
    )


def test_the_committed_verdict_is_baseline6_and_the_weights_still_clear_the_bar(
    corpus_conviction: ConvictionTable,
) -> None:
    """The recorded verdict, and what the SAME frozen weights say on the new corpus.

    ``verdict.json`` is the first held-out evaluation's verdict, decided on the
    baseline-6 corpus. It is a RECORD, so its fields are read from the artifact
    and pinned as written -- re-deriving them is not possible now that the corpus
    under them has been re-recorded, and quietly re-pinning them to whatever the
    new corpus says would rewrite history rather than extend it.

    What CAN be re-derived is the evaluation itself, from the same FROZEN weights
    against the baseline-7 corpus. That is a fully out-of-sample read: the model
    was fitted on bytes that no longer exist, and it has never seen a single
    meeting in the corpus scoring it here. It still returns GO, on both bars, with
    a HIGHER flag Spearman (0.715 vs the recorded 0.578) on a smaller held-out
    split (87 meetings vs 96). That is evidence about the model, and it is NOT a
    substitute for the re-ground (a NAMED follow-up,
    audits/audit-phase-20-baseline-7.md §10.2): a re-fit would change the weights,
    the cap and the verdict together, and only then does a re-derived verdict
    become the committed one again.

    The two halves are asserted together so neither can be read alone, and the
    inequality between them is asserted explicitly -- if a future change made the
    re-derivation reproduce the committed record, this test would be silently
    measuring nothing.
    """

    model, digest = load_conviction_model_artifact(_ARTIFACT_DIR)
    report, _ = run_conviction_fidelity(corpus_conviction, model=model)
    rederived = decide_conviction_go(report, weights_sha256=digest)
    committed = load_conviction_verdict(_ARTIFACT_DIR)

    # -- the RECORD: the baseline-6 first-evaluation verdict, as written --------
    assert committed.replay_set_dir == "replays/ml_corpus/9p2i"
    assert committed.verdict == "GO"
    assert committed.weights_sha256 == digest
    assert committed.test_meetings == 96
    assert committed.test_ejections == 60
    assert committed.conversions_test == 47
    assert committed.flag_spearman == pytest.approx(0.5781584982719424)
    assert committed.meets_spearman_bar
    assert committed.conversion_recall == pytest.approx(45 / 47)
    assert committed.voice_driven_share == pytest.approx(0.15)
    assert committed.conversion_bar == pytest.approx(0.6375)
    assert committed.meets_conversion_bar
    assert (
        committed.fitness_term,
        committed.prescreen_role,
        committed.model_role,
    ) == ("ships", "gating", "training-signal")

    # -- the RE-DERIVATION: same frozen weights, baseline-7 corpus -------------
    # The corpus identity field is normalized (the committed artifact stores a
    # repo-relative path; this run built its table from an absolute one).
    assert Path(rederived.replay_set_dir).resolve() == _CORPUS.resolve()
    assert rederived.weights_sha256 == digest
    assert rederived.test_meetings == 87
    assert rederived.test_ejections == 55
    assert rederived.conversions_test == 47
    assert rederived.flag_spearman == pytest.approx(
        0.71457789753481
    )  # was 0.6991081211401057 — the corrected label fits better
    assert rederived.conversion_recall == pytest.approx(44 / 47)
    assert rederived.voice_driven_share == pytest.approx(0.2)
    assert rederived.conversion_bar == pytest.approx(0.6)
    # The verdict survives the substrate change on both bars.
    assert rederived.verdict == "GO"
    assert rederived.meets_spearman_bar
    assert rederived.meets_conversion_bar
    assert rederived.flag_spearman > committed.flag_spearman
    # The held-out confusion census behind it.
    assert (
        report.true_positives,
        report.false_positives,
        report.false_negatives,
        report.true_negatives,
    ) == (44, 3, 3, 37)

    # The tripwire: the two are NOT the same evaluation. When the re-ground
    # lands they converge again, and this assertion is what says so.
    assert committed.model_dump() != {
        **rederived.model_dump(),
        "replay_set_dir": committed.replay_set_dir,
    }
