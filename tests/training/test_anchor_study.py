"""Task 18.5 — the anchor study: λ sweep + filtered-BC anchor refinement.

CI-scale coverage of ``training/anchor_study.py``: the substrate sha, the
verified corpus decision-stream walk, the deterministic filtered-BC fit (the
Fo6Logistic recipe: zeros init, fixed epochs/lr, no RNG), the offline
FSM-agreement/divergence evaluation, the ci-budget end-to-end driver, and the
pure-file-read pins on the SHIPPED study artifacts (the committed-state
section — no rollouts, the test_bakeoff_harness.py Section-9 idiom).
"""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import pytest

from training.anchor_study import (
    ANCHOR_STUDY_ARTIFACT_ROOT,
    CORPUS_DIR,
    FILTERED_BC_ENTRANT,
    HIGH_FLAG_FLOOR,
    LAMBDA_GRID,
    AnchorStudyReport,
    CorpusDecision,
    CorpusGameFacts,
    CorpusWalkError,
    compute_substrate_sha,
    historical_compute_substrate_sha,
    corpus_seeds,
    evaluate_anchor_offline,
    fit_filtered_bc_anchor,
    run_anchor_study,
    walk_corpus_game,
)
from training.bakeoff.harness import (
    BAKEOFF_BASELINE_ID,
    BakeoffProtocolConfig,
    load_candidate_weights,
)
from training.bakeoff.utility_es import OPTION_FEATURE_NAMES, utility_genome_length

# Task 19.27: campaign tier (training/README.md §2 FREEZE — co-evolution / campaign machinery).
# Excluded from the default gate; runs weekly in CI's campaign-tier job and
# at phase close via `-m campaign`.
pytestmark = pytest.mark.campaign

_COMMITTED_CHAMPION_DIR = Path("training/artifacts/impostor/utility-es")
_SEED_1000_REPLAY = CORPUS_DIR / "replay-seed-1000.jsonl"
# Seed 1002 holds a meeting at tick 10 and an impostor (p-4) whose tick-11 resume
# decision reads the post-meeting fold. It is the walk's fold regression subject.
_SEED_1002_REPLAY = CORPUS_DIR / "replay-seed-1002.jsonl"


# --------------------------------------------------------------------------- #
# 1. The substrate sha.                                                        #
# --------------------------------------------------------------------------- #


def test_substrate_sha_is_stable_and_moves_with_the_corpus_bytes(
    tmp_path: Path,
) -> None:
    committed = compute_substrate_sha()
    assert committed == compute_substrate_sha()
    assert len(committed) == 64

    # A re-recorded corpus (different MANIFEST bytes) must move the sha — the
    # 18.24 stale-seed refusal's trigger.
    drifted_dir = tmp_path / "9p2i"
    shutil.copytree(CORPUS_DIR, drifted_dir)
    assert compute_substrate_sha(drifted_dir) == committed
    manifest = (CORPUS_DIR / "MANIFEST.md").read_text()
    (drifted_dir / "MANIFEST.md").write_text(manifest + "\ndrifted\n")
    assert compute_substrate_sha(drifted_dir) != committed


def test_substrate_sha_moves_with_the_replay_bytes_alone(tmp_path: Path) -> None:
    # A corpus refresh that changes RECORDED GAME bytes but (wrongly) leaves
    # MANIFEST.md/splits.json untouched must still move the sha — the
    # filtered-BC anchor is fitted from the replay bytes (Codex review on
    # PR #292).
    def build(replay_suffix: str) -> Path:
        # The SAME leaf directory name under different parents: corpus_set
        # (the dir name) is part of the sha payload, so a differing leaf name
        # would make this test pass even if the replay-byte digest regressed
        # (Codex review on PR #292) — only the replay bytes may differ.
        corpus = tmp_path / f"variant{len(replay_suffix)}" / "9p2i"
        corpus.mkdir(parents=True)
        shutil.copy(CORPUS_DIR / "MANIFEST.md", corpus / "MANIFEST.md")
        shutil.copy(CORPUS_DIR / "splits.json", corpus / "splits.json")
        shutil.copy(CORPUS_DIR / "roster.json", corpus / "roster.json")
        replay = _SEED_1000_REPLAY.read_text() + replay_suffix
        (corpus / "replay-seed-1000.jsonl").write_text(replay)
        return corpus

    pristine = build("")
    drifted = build("\n")
    assert compute_substrate_sha(pristine) != compute_substrate_sha(drifted)


def test_corpus_seeds_lists_the_committed_150_games() -> None:
    seeds = corpus_seeds()
    assert len(seeds) == 150
    assert seeds[0] == 1000
    assert seeds[-1] == 1149
    assert seeds == tuple(sorted(seeds))


# --------------------------------------------------------------------------- #
# 2. The corpus decision-stream walk (verified reconstruction).                #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def seed_1000_walk() -> tuple[CorpusGameFacts, tuple[CorpusDecision, ...]]:
    """One verified corpus walk shared by the fit/eval tests (expensive-ish)."""

    return walk_corpus_game(_SEED_1000_REPLAY)


# Task 18.13 (the baseline-6 ML-corpus re-record) moved both the corpus replay
# bytes and the corpus MANIFEST/splits digests that compute_substrate_sha() folds
# in; Task 18.14 then re-ran the study on the baseline-6 substrate (the re-run
# 18.13 deferred, folded into the BAKEOFF_BASELINE_ID flip so both stale inputs to
# the substrate identity moved at once). The seed-1000 harvest pins are
# CORPUS-derived and re-pinned LIVE below; the committed study ARTIFACT is now the
# baseline-6 re-run, so its recorded substrate_sha MATCHES the live substrate — the
# positive pin further down, which replaced 18.13's self-clearing hybrid tripwire.


def test_walk_corpus_game_verifies_and_harvests(
    seed_1000_walk: tuple[CorpusGameFacts, tuple[CorpusDecision, ...]],
) -> None:
    facts, decisions = seed_1000_walk
    # Committed-bytes pins for seed 1000 (2 meetings, 1 persisted flag,
    # recorded winner CREWMATES) — a drift in any of these means the corpus
    # bytes or the walk changed. Re-pinned at Task 18.13's baseline-6 re-record
    # (was 5 meetings / 2 flags at baseline 5). These are CORPUS-derived, so they
    # are re-derivable from the new bytes and stay LIVE, and the committed STUDY
    # ARTIFACT is now the baseline-6 re-run (Task 18.14), so its substrate fence
    # below matches the live substrate (PR #301 review: don't xfail what you can
    # honestly re-pin).
    assert facts.winner == "CREWMATES"
    assert facts.crew_winning is True
    assert facts.meetings == 2
    assert facts.persisted_flags == 1
    assert facts.high_flag is False
    assert facts.flags_per_meeting < HIGH_FLAG_FLOOR
    assert facts.decisions == len(decisions) > 0
    assert facts.fsm_offmenu_decisions == 0
    for decision in decisions:
        assert decision.seed == 1000
        assert len(decision.features) == len(decision.option_intent_keys)
        assert len(decision.features) == len(decision.option_kinds)
        for row in decision.features:
            assert len(row) == len(OPTION_FEATURE_NAMES)
        assert decision.fsm_option_index is not None
        assert (
            decision.option_intent_keys[decision.fsm_option_index]
            == decision.fsm_intent_key
        )


def test_walk_corpus_game_fails_loud_on_drifted_bytes(tmp_path: Path) -> None:
    # Tamper one recorded action: the engine walk then diverges, and either the
    # per-decision FSM verification or the state-hash chain must refuse it.
    lines = _SEED_1000_REPLAY.read_text().splitlines()
    first = json.loads(lines[0])
    first["actions"][0]["payload"]["to_room"] = "CAFETERIA"
    lines[0] = json.dumps(first)
    drifted = tmp_path / "replay-seed-1000.jsonl"
    drifted.write_text("\n".join(lines) + "\n")
    with pytest.raises(CorpusWalkError):
        walk_corpus_game(drifted)


def test_the_walk_replays_the_meeting_fold_on_the_resume_tick() -> None:
    """A post-meeting resume decision re-derives only when the fold is replayed.

    ``absorb_reported_testimony`` mints the ``meeting_boundary`` episodic marker
    that ``ImpostorPolicy._pre_meeting_subjects`` reads to drop stale and ejected
    leads before ranking. Without the fold the marker never lands, the subject
    set is empty, and the impostor chases a lead the live agent had already
    dropped — seed 1002's p-4 walks to ADMIN at tick 11 where the recording says
    CAFETERIA. This walk is the regression: it raises without the fold and is
    clean with it.
    """

    facts, decisions = walk_corpus_game(_SEED_1002_REPLAY)
    assert facts.seed == 1002
    assert facts.meetings == 3
    assert facts.decisions == len(decisions) > 0
    # Decisions are harvested past the tick-10 meeting, so the resume tick the
    # fold repairs is inside the verified stream rather than beyond its end.
    assert max(decision.tick for decision in decisions) > 10


def test_the_fold_does_not_soften_the_walk_on_the_resume_tick(
    tmp_path: Path,
) -> None:
    """The planted case: a corrupted resume-tick action still refuses.

    The fold makes MORE decisions re-derivable, so the guard it repairs has to
    keep biting — tamper p-4's tick-11 move, the one the fold fixed, and the
    per-decision verification must still raise.
    """

    lines = _SEED_1002_REPLAY.read_text().splitlines()
    tampered = 0
    for index, line in enumerate(lines):
        row = json.loads(line)
        if row.get("kind") != "tick" or row.get("tick") != 11:
            continue
        for action in row["actions"]:
            if action["actor"] == "p-4":
                assert action["payload"]["to_room"] == "CAFETERIA"
                action["payload"]["to_room"] = "STORAGE"
                tampered += 1
        lines[index] = json.dumps(row)
    assert tampered == 1
    corrupted = tmp_path / "replay-seed-1002.jsonl"
    corrupted.write_text("\n".join(lines) + "\n")
    with pytest.raises(CorpusWalkError, match="drifted from the recording"):
        walk_corpus_game(corrupted)


def test_walk_rejects_off_convention_filenames(tmp_path: Path) -> None:
    stray = tmp_path / "game-1000.jsonl"
    stray.write_text("")
    with pytest.raises(ValueError, match="replay-seed-"):
        walk_corpus_game(stray)


def test_walk_fails_loud_when_an_alive_impostor_action_is_missing(
    tmp_path: Path,
) -> None:
    # Dropping an alive impostor's recorded action row must raise rather than
    # silently thin the verified stream — a dropped ``wait`` may not even trip
    # the state-hash check (Codex review on PR #292). Seed 1000's impostors
    # are p-6/p-8 (the re-seeded roles).
    lines = _SEED_1000_REPLAY.read_text().splitlines()
    first = json.loads(lines[0])
    impostor_actors = {"p-6", "p-8"}
    # ``action_dispositions`` is POSITIONAL (orchestrator/replay.py:245-252), so
    # the perturbation drops each row's disposition with it — otherwise the row
    # fails the length validator before the fence under test can speak.
    keep = [raw["actor"] not in impostor_actors for raw in first["actions"]]
    first["action_dispositions"] = [
        disposition
        for disposition, kept in zip(first["action_dispositions"], keep, strict=True)
        if kept
    ]
    first["actions"] = [
        raw for raw, kept in zip(first["actions"], keep, strict=True) if kept
    ]
    assert len(first["actions"]) == len(keep) - 2
    lines[0] = json.dumps(first)
    drifted = tmp_path / "replay-seed-1000.jsonl"
    drifted.write_text("\n".join(lines) + "\n")
    with pytest.raises(CorpusWalkError, match="no recorded action"):
        walk_corpus_game(drifted)


def test_walk_fails_loud_on_a_truncated_replay_without_game_over(
    tmp_path: Path,
) -> None:
    # A replay missing its terminal game_over row is a partial recording; the
    # walk must refuse it rather than enter a winner-less game into the
    # filter/fit (Codex review on PR #292).
    lines = _SEED_1000_REPLAY.read_text().splitlines()
    assert json.loads(lines[-1])["kind"] == "game_over"
    truncated = tmp_path / "replay-seed-1000.jsonl"
    truncated.write_text("\n".join(lines[:-1]) + "\n")
    with pytest.raises(CorpusWalkError, match="no terminal game_over"):
        walk_corpus_game(truncated)


def test_walk_fails_loud_on_an_unvisited_meeting_row(tmp_path: Path) -> None:
    # A stale extra meeting row at a tick the engine never enters is never
    # hash-verified, yet it would move the flags census — the walk must
    # refuse it (Codex review on PR #292).
    lines = _SEED_1000_REPLAY.read_text().splitlines()
    meeting_line = next(
        line for line in lines if json.loads(line).get("kind") == "meeting"
    )
    stale = json.loads(meeting_line)
    stale["tick"] = 1  # a PLAY tick the walk never enters as a meeting
    corrupted = tmp_path / "replay-seed-1000.jsonl"
    corrupted.write_text("\n".join(lines[:-1] + [json.dumps(stale), lines[-1]]) + "\n")
    with pytest.raises(CorpusWalkError, match="never entered"):
        walk_corpus_game(corrupted)


def test_corpus_seeds_rejects_a_bad_split_partition(tmp_path: Path) -> None:
    # A duplicated seed would double-weight its game in the fit; a listed-but
    # -missing or present-but-unlisted replay would drop/shadow a game while
    # the substrate sha still hashes the bytes (Codex review on PR #292).
    corpora = iter(range(10))

    def build(splits: dict[str, object], seeds_on_disk: list[int]) -> Path:
        corpus = tmp_path / f"corpus-{next(corpora)}"
        corpus.mkdir()
        (corpus / "splits.json").write_text(json.dumps(splits))
        for seed in seeds_on_disk:
            (corpus / f"replay-seed-{seed}.jsonl").write_text("")
        return corpus

    duplicated = build({"train": [1, 2], "val": [2], "test": [3]}, [1, 2, 3])
    with pytest.raises(ValueError, match="more than one bucket"):
        corpus_seeds(duplicated)
    missing = build({"train": [1], "val": [2], "test": [3]}, [1, 2])
    with pytest.raises(ValueError, match="listed-but-missing"):
        corpus_seeds(missing)
    unlisted = build({"train": [1], "val": [2], "test": [3]}, [1, 2, 3, 4])
    with pytest.raises(ValueError, match="present-but-unlisted"):
        corpus_seeds(unlisted)


def test_walk_fails_loud_on_a_duplicate_meeting_row(tmp_path: Path) -> None:
    # Collapsing duplicate meeting rows would let the surviving row (honest
    # state hashes, forged contradictions) pass the visited check AND move the
    # flags census (Codex review on PR #292).
    lines = _SEED_1000_REPLAY.read_text().splitlines()
    meeting_line = next(
        line for line in lines if json.loads(line).get("kind") == "meeting"
    )
    corrupted = tmp_path / "replay-seed-1000.jsonl"
    corrupted.write_text("\n".join(lines[:-1] + [meeting_line, lines[-1]]) + "\n")
    with pytest.raises(CorpusWalkError, match="duplicate meeting rows"):
        walk_corpus_game(corrupted)


def test_walk_fails_loud_on_a_ghost_actor_row(tmp_path: Path) -> None:
    # A non-roster actor's row is engine-rejected without moving the state
    # hash — bytes no orchestrator run could have produced must not pass as
    # verified (Codex review on PR #292).
    lines = _SEED_1000_REPLAY.read_text().splitlines()
    first = json.loads(lines[0])
    first["actions"].append({"actor": "ghost", "payload": {}, "type": "wait"})
    # The positional disposition tuple grows with the row it describes.
    first["action_dispositions"].append("applied")
    lines[0] = json.dumps(first)
    corrupted = tmp_path / "replay-seed-1000.jsonl"
    corrupted.write_text("\n".join(lines) + "\n")
    with pytest.raises(CorpusWalkError, match="outside the living roster"):
        walk_corpus_game(corrupted)


def test_walk_fails_loud_on_tick_rows_after_game_over(tmp_path: Path) -> None:
    # The GAME_OVER break stops validating, so trailing forged tick rows would
    # otherwise ride along unverified (Codex review on PR #292).
    lines = _SEED_1000_REPLAY.read_text().splitlines()
    last_tick_line = next(
        line for line in reversed(lines) if json.loads(line).get("kind") == "tick"
    )
    forged = json.loads(last_tick_line)
    forged["tick"] = forged["tick"] + 1
    corrupted = tmp_path / "replay-seed-1000.jsonl"
    corrupted.write_text("\n".join(lines[:-1] + [json.dumps(forged), lines[-1]]) + "\n")
    with pytest.raises(CorpusWalkError, match="after the terminal GAME_OVER"):
        walk_corpus_game(corrupted)


def test_walk_fails_loud_on_duplicate_action_rows(tmp_path: Path) -> None:
    # The orchestrator submits one action per living actor; a duplicated row
    # (which duplicate ``wait``s may hide from the hash check) must raise
    # (Codex review on PR #292).
    lines = _SEED_1000_REPLAY.read_text().splitlines()
    first = json.loads(lines[0])
    first["actions"].append(first["actions"][0])
    # The positional disposition tuple grows with the row it describes.
    first["action_dispositions"].append(first["action_dispositions"][0])
    lines[0] = json.dumps(first)
    corrupted = tmp_path / "replay-seed-1000.jsonl"
    corrupted.write_text("\n".join(lines) + "\n")
    with pytest.raises(CorpusWalkError, match="duplicate action rows"):
        walk_corpus_game(corrupted)


# --------------------------------------------------------------------------- #
# 3. The filtered-BC fit (the Fo6Logistic deterministic recipe).               #
# --------------------------------------------------------------------------- #


def test_fit_filtered_bc_anchor_is_deterministic(
    seed_1000_walk: tuple[CorpusGameFacts, tuple[CorpusDecision, ...]],
) -> None:
    _, decisions = seed_1000_walk
    first = fit_filtered_bc_anchor(decisions)
    second = fit_filtered_bc_anchor(decisions)
    # Zeros init + full-batch + no RNG: an in-process double fit is
    # bit-identical (the cross-PLATFORM caveat is documented on the module,
    # per the surrogate precedent).
    assert first == second
    assert len(first) == utility_genome_length()
    # The trailing bias slot is structurally 0.0: a shared per-option constant
    # cancels in the softmax, so the fold writes exactly zero there.
    assert first[-1] == 0.0


def test_fit_improves_fsm_agreement_over_the_zero_genome(
    seed_1000_walk: tuple[CorpusGameFacts, tuple[CorpusDecision, ...]],
) -> None:
    _, decisions = seed_1000_walk
    genome = fit_filtered_bc_anchor(decisions)
    fitted = evaluate_anchor_offline(genome, decisions, label="fitted")
    zeros = evaluate_anchor_offline(
        tuple(0.0 for _ in range(utility_genome_length())), decisions, label="zeros"
    )
    assert fitted.agreement > zeros.agreement
    assert fitted.mean_anchor_ce < zeros.mean_anchor_ce


def test_fit_weighting_and_validation(
    seed_1000_walk: tuple[CorpusGameFacts, tuple[CorpusDecision, ...]],
) -> None:
    _, decisions = seed_1000_walk
    with pytest.raises(ValueError, match="sample_weights length"):
        fit_filtered_bc_anchor(decisions, sample_weights=[1.0])
    with pytest.raises(ValueError, match="not positive"):
        fit_filtered_bc_anchor(
            decisions, sample_weights=[0.0] + [1.0] * (len(decisions) - 1)
        )
    with pytest.raises(ValueError, match="no on-menu decisions"):
        fit_filtered_bc_anchor(())
    # Uniform re-weighting is likelihood-neutral: doubling EVERY weight scales
    # the loss and its normalizer together, so the fit is unchanged.
    doubled = fit_filtered_bc_anchor(decisions, sample_weights=[2.0] * len(decisions))
    assert doubled == fit_filtered_bc_anchor(decisions)


def _synthetic_decision(*, fsm_on_menu: bool) -> CorpusDecision:
    """A two-option decision with hand-checkable features/keys."""

    kill_features = tuple(
        1.0 if name in ("kind_kill_now", "isolation") else 0.0
        for name in OPTION_FEATURE_NAMES
    )
    wait_features = tuple(
        1.0 if name == "kind_wait" else 0.0 for name in OPTION_FEATURE_NAMES
    )
    return CorpusDecision(
        seed=1,
        tick=0,
        actor="p-6",
        option_kinds=("kill_now", "wait"),
        option_intent_keys=("kill:p-1", "wait"),
        features=(kill_features, wait_features),
        fsm_intent_key="kill:p-1" if fsm_on_menu else "report:b-1",
        fsm_option_index=0 if fsm_on_menu else None,
    )


def test_fit_excludes_offmenu_decisions_and_refuses_an_offmenu_only_stream() -> None:
    with pytest.raises(ValueError, match="no on-menu decisions"):
        fit_filtered_bc_anchor((_synthetic_decision(fsm_on_menu=False),))
    genome = fit_filtered_bc_anchor(
        (
            _synthetic_decision(fsm_on_menu=True),
            _synthetic_decision(fsm_on_menu=False),
        )
    )
    assert len(genome) == utility_genome_length()


# --------------------------------------------------------------------------- #
# 4. The offline evaluation semantics.                                         #
# --------------------------------------------------------------------------- #


def test_evaluate_anchor_offline_hand_checked_semantics() -> None:
    decision = _synthetic_decision(fsm_on_menu=True)
    # A genome preferring wait: agreement 0, one (kill -> wait) divergence
    # cell, and the anchor-CE is the exact grouped-softmax log-loss.
    wait_index = OPTION_FEATURE_NAMES.index("kind_wait")
    genome = tuple(
        1.0 if index == wait_index else 0.0 for index in range(utility_genome_length())
    )
    result = evaluate_anchor_offline(genome, (decision,), label="hand")
    assert result.decisions == 1
    assert result.agreement == 0.0
    assert result.fsm_offmenu_decisions == 0
    assert result.divergence[0].fsm_intent_kind == "kill"
    assert result.divergence[0].anchor_intent_kind == "wait"
    assert result.per_kind_agreement == {"kill": (1, 0)}
    expected_ce = -math.log(1.0 / (1.0 + math.e))
    assert result.mean_anchor_ce == pytest.approx(expected_ce)

    # The FSM-preferring genome agrees and its per-kind bucket says so.
    kill_index = OPTION_FEATURE_NAMES.index("kind_kill_now")
    agreeing = tuple(
        1.0 if index == kill_index else 0.0 for index in range(utility_genome_length())
    )
    agreeing_result = evaluate_anchor_offline(agreeing, (decision,), label="hand")
    assert agreeing_result.agreement == 1.0
    assert agreeing_result.divergence == ()
    assert agreeing_result.per_kind_agreement == {"kill": (1, 1)}


def test_evaluate_anchor_offline_tallies_an_offmenu_fsm_choice() -> None:
    decision = _synthetic_decision(fsm_on_menu=False)
    genome = tuple(0.0 for _ in range(utility_genome_length()))
    result = evaluate_anchor_offline(genome, (decision,), label="offmenu")
    assert result.fsm_offmenu_decisions == 1
    # A structural off-menu decision necessarily clamps too.
    assert result.ce_clamped_decisions == 1
    assert result.agreement == 0.0
    # The clamped log-loss, exactly the harness's ANCHOR_CE_EPSILON semantics.
    assert result.mean_anchor_ce == pytest.approx(-math.log(1e-6))


def test_evaluate_anchor_offline_separates_the_clamp_from_offmenu() -> None:
    # An ON-menu FSM choice a sharp genome drives below the epsilon is
    # CE-clamped but NOT off-menu (Codex review on PR #292): the walk's
    # "0 off-menu" verification must stay true for any genome.
    decision = _synthetic_decision(fsm_on_menu=True)
    wait_index = OPTION_FEATURE_NAMES.index("kind_wait")
    sharp = tuple(
        20.0 if index == wait_index else 0.0 for index in range(utility_genome_length())
    )
    result = evaluate_anchor_offline(sharp, (decision,), label="sharp")
    # softmax mass at the FSM's kill option is 1/(1+e^20) ~ 2e-9 < 1e-6.
    assert result.fsm_offmenu_decisions == 0
    assert result.ce_clamped_decisions == 1
    assert result.mean_anchor_ce == pytest.approx(-math.log(1e-6))


def test_evaluate_anchor_offline_validation() -> None:
    with pytest.raises(ValueError, match="genome length"):
        evaluate_anchor_offline(
            (0.0,), (_synthetic_decision(fsm_on_menu=True),), label="x"
        )
    with pytest.raises(ValueError, match="empty stream"):
        evaluate_anchor_offline(
            tuple(0.0 for _ in range(utility_genome_length())), (), label="x"
        )


# --------------------------------------------------------------------------- #
# 5. The ci-budget end-to-end driver.                                          #
# --------------------------------------------------------------------------- #


def test_run_anchor_study_ci_budget(tmp_path: Path) -> None:
    """Exercise the tiny study with explicitly historical conviction scoring."""

    artifact_root = tmp_path / "artifacts"
    report_path = tmp_path / "report.md"
    report = run_anchor_study(
        budget="ci",
        lambda_grid=(1.0,),
        corpus_seed_subset=(1000,),
        artifact_root=artifact_root,
        protocol=BakeoffProtocolConfig(
            eval_seeds=(1004,),
            determinism_seeds=(1004,),
            leak_seeds=(0,),
            surrogate_artifact_dir=None,
            evidence_scope="historical",
        ),
        report_path=report_path,
    )

    # The sweep row carries every definition-of-done metric.
    assert len(report.sweep_rows) == 1
    assert report.evaluation_evidence_scope == "historical"
    row = report.sweep_rows[0]
    assert row.entrant == "lambda-1.0"
    assert math.isfinite(row.inner_fitness_real)
    assert math.isfinite(row.anchor_cross_entropy)
    assert 0.0 <= row.impostor_win_rate <= 1.0
    assert row.take_rate is None or 0.0 <= row.take_rate <= 1.0
    assert set(row.descriptor_footprint) == {
        "kill_count",
        "witness_exposure_rate",
        "vent_usage",
        "meeting_count",
        "meeting_trigger_rate",
        "do_task_emissions",
        "do_task_cadence",
        "median_kill_tick",
    }

    # The λ=1.0 cross-check RUNS at ci budget but is not enforced (a
    # 1-generation champion is legitimately a different genome).
    check = report.determinism_cross_check
    assert check is not None
    assert len(check.committed_weights_sha256) == 64
    assert len(check.sweep_weights_sha256) == 64

    # Frozen artifacts: float-hex weights + sha sidecar + substrate-sha config
    # per entrant, plus the deterministic study index.
    substrate_sha = compute_substrate_sha()
    assert report.substrate_sha == substrate_sha
    for entrant in ("lambda-1.0", FILTERED_BC_ENTRANT):
        entrant_dir = artifact_root / entrant
        weights = load_candidate_weights(entrant_dir)  # sha-verified reload
        assert len(weights) == utility_genome_length()
        config = json.loads((entrant_dir / "config.json").read_text())
        assert config["substrate_sha"] == substrate_sha
        assert config["study"] == "anchor-study"
        # Config-driven identity matches the directory name (Codex review on
        # PR #292): a λ cell is addressable without its path.
        assert config["entrant"] == entrant
    assert (
        json.loads((artifact_root / "lambda-1.0" / "config.json").read_text())[
            "base_entrant"
        ]
        == "utility-es"
    )
    assert (
        json.loads((artifact_root / "lambda-1.0" / "config.json").read_text())[
            "evaluation_evidence_scope"
        ]
        == "historical"
    )
    index = json.loads((artifact_root / "study.json").read_text())
    round_trip = AnchorStudyReport.model_validate(index)
    assert round_trip == report

    # The rendered report carries the cell (the sweep table's canonical λ
    # header + its weights sha — NOT just the recommendation section, which
    # only names Pareto survivors), the anchor, and the substrate sha.
    rendered = report_path.read_text()
    assert "λ=1.0" in rendered
    assert row.weights_sha256[:12] in rendered
    assert FILTERED_BC_ENTRANT in rendered
    assert substrate_sha in rendered
    assert "Evaluation evidence scope:** historical" in rendered
    # The render names the budget the run ACTUALLY used, never "full" prose
    # over a ci run.
    assert "--budget ci" in rendered
    assert 'utility_es_budget("ci"' in rendered
    assert "20 gen × 12 pop" not in rendered

    # The recommendation always names the refined anchor (the 18.16 seam's
    # entrant), and every named seed is a frozen artifact dir.
    assert FILTERED_BC_ENTRANT in report.recommended_campaign_seeds
    for name in report.recommended_campaign_seeds:
        assert (artifact_root / name / "weights.json").exists()


def test_substrate_sha_follows_the_protocol_baseline(tmp_path: Path) -> None:
    # A re-pinned baseline must move the frozen provenance WITH the scoring
    # protocol, never trail the module default (Codex review on PR #292).
    # An EMPTY λ grid keeps this seconds-scale: no training, no
    # evaluate_candidate call (whose referee would reject an unknown
    # baseline), just the walk + fit + freeze.
    report = run_anchor_study(
        budget="ci",
        lambda_grid=(),
        corpus_seed_subset=(1000,),
        artifact_root=tmp_path / "artifacts",
        protocol=BakeoffProtocolConfig(
            eval_seeds=(1004,),
            baseline_id="baseline-x",
            surrogate_artifact_dir=None,
        ),
        high_flag_floor=0.9,
    )
    assert report.baseline_id == "baseline-x"
    assert report.substrate_sha == compute_substrate_sha(
        baseline_id="baseline-x", high_flag_floor=0.9
    )
    assert report.substrate_sha != compute_substrate_sha()
    # The floor actually used flows into the frozen census and config, not
    # the module default (the post-adoption re-fit path).
    assert report.filtered_bc.filter_summary.high_flag_floor == 0.9
    config = json.loads(
        (tmp_path / "artifacts" / FILTERED_BC_ENTRANT / "config.json").read_text()
    )
    assert config["substrate_sha"] == report.substrate_sha
    assert config["filter"]["high_flag_floor"] == 0.9
    assert report.sweep_rows == ()
    assert report.determinism_cross_check is None
    assert report.recommended_campaign_seeds == (FILTERED_BC_ENTRANT,)


def test_sweep_refuses_a_non_harness_corpus(tmp_path: Path) -> None:
    # The λ sweep trains through the committed utility_es_budget, whose seeds
    # bind to the harness corpus — sweeping against a different corpus dir
    # would stamp artifacts with one corpus while training on another (Codex
    # review on PR #292). A fit-only study (empty grid) stays free.
    with pytest.raises(ValueError, match="bind to the harness corpus"):
        run_anchor_study(
            budget="ci",
            lambda_grid=(1.0,),
            corpus_dir=tmp_path / "9p2i",
            artifact_root=tmp_path / "artifacts",
        )


def test_lambda_1_cross_check_raises_on_a_drifted_full_budget_champion() -> None:
    # The fail-loud guard the definition of done hinges on: a full-budget
    # λ=1.0 champion that does NOT byte-match the committed artifact must
    # refuse the whole sweep. Exercised directly on the private helper (the
    # full 285 s training is never paid in CI).
    from training.anchor_study import _cross_check_committed_champion
    from training.bakeoff.harness import TrainedCandidate
    from training.bakeoff.utility_es import build_utility_scorer_policy

    drifted_genome = tuple(float(i) for i in range(utility_genome_length()))
    drifted = TrainedCandidate(
        entrant="lambda-1.0",
        policy=build_utility_scorer_policy(drifted_genome),
        weights=drifted_genome,
        config={},
    )
    with pytest.raises(RuntimeError, match="byte-identically"):
        _cross_check_committed_champion(drifted, enforce=True)
    # The ci-budget path compares WITHOUT enforcement: the mismatch is
    # reported, never raised.
    check = _cross_check_committed_champion(drifted, enforce=False)
    assert check.byte_identical is False
    assert check.committed_weights_sha256 != check.sweep_weights_sha256

    # And the committed genome itself passes the enforced check.
    committed_genome = load_candidate_weights(_COMMITTED_CHAMPION_DIR)
    committed = TrainedCandidate(
        entrant="lambda-1.0",
        policy=build_utility_scorer_policy(committed_genome),
        weights=committed_genome,
        config={},
    )
    passing = _cross_check_committed_champion(committed, enforce=True)
    assert passing.byte_identical is True
    assert passing.committed_weights_sha256 == passing.sweep_weights_sha256


# --------------------------------------------------------------------------- #
# 6. Pins on the SHIPPED study artifacts (pure file reads, no rollouts).       #
# --------------------------------------------------------------------------- #


def test_committed_lambda_1_artifact_reproduces_the_champion_byte_for_byte() -> None:
    committed = (_COMMITTED_CHAMPION_DIR / "weights.json").read_bytes()
    sweep = (ANCHOR_STUDY_ARTIFACT_ROOT / "lambda-1.0" / "weights.json").read_bytes()
    assert sweep == committed


def test_committed_study_artifacts_are_the_baseline8_fit() -> None:
    """The committed anchor-study artifacts ARE the baseline-8 re-run (Task 21.17).

    The utility-es λ sweep is SUBSTRATE-INDEPENDENT (deterministic fake-provider
    rollouts off ``seed`` + the canonical map, no corpus read), so the λ cell
    genomes — and the λ=1.0-vs-committed-champion byte identity pinned above —
    reproduce unchanged; only the corpus-derived filtered-BC anchor is re-fit on
    the live replay bytes, and every cell's ``config.json`` substrate sha plus the
    study index's ``substrate_sha`` are re-stamped to the live substrate. So the
    committed artifact's recorded substrate MATCHES ``historical_compute_substrate_sha()``
    and reads the adopted baseline id.

    The λ grid itself is deliberately NOT re-searched: those rows are a recording
    of a search made under the pre-Task-21.16 fitness objective, and
    ``historical_compute_substrate_sha``'s payload covers the corpus and the flag floor but
    not the objective — so the fence below cannot see that difference, and the
    report says so in §1.1 rather than leaving it to be inferred.
    """

    index = json.loads((ANCHOR_STUDY_ARTIFACT_ROOT / "study.json").read_text())
    report = AnchorStudyReport.model_validate(index)
    assert report.evaluation_evidence_scope is None
    assert "evaluation_evidence_scope" not in json.loads(report.to_json())
    # Re-grounded: the recorded substrate MATCHES the live substrate and reads
    # the adopted baseline id.
    assert report.substrate_sha == historical_compute_substrate_sha()
    assert report.baseline_id == BAKEOFF_BASELINE_ID == "baseline-8"
    # The substrate-independent structure holds (not what the re-ground moved): the
    # full λ grid and the λ=1.0 champion byte-identity cross-check.
    assert report.lambda_grid == LAMBDA_GRID
    check = report.determinism_cross_check
    assert check is not None and check.byte_identical is True
    expected_entrants = [f"lambda-{value}" for value in LAMBDA_GRID] + [
        FILTERED_BC_ENTRANT
    ]
    for entrant in expected_entrants:
        entrant_dir = ANCHOR_STUDY_ARTIFACT_ROOT / entrant
        weights = load_candidate_weights(entrant_dir)  # sha-verified reload
        assert len(weights) == utility_genome_length()
        config = json.loads((entrant_dir / "config.json").read_text())
        # Every cell agrees with the study index's (historical) substrate sha.
        assert config["substrate_sha"] == report.substrate_sha
        assert config["entrant"] == entrant
        if entrant != FILTERED_BC_ENTRANT:
            assert config["base_entrant"] == "utility-es"
    for name in report.recommended_campaign_seeds:
        assert (ANCHOR_STUDY_ARTIFACT_ROOT / name / "weights.json").exists()


def test_committed_report_quotes_the_study_index() -> None:
    index = json.loads((ANCHOR_STUDY_ARTIFACT_ROOT / "study.json").read_text())
    report = AnchorStudyReport.model_validate(index)
    rendered = Path("training/reports/report-anchor-study.md").read_text()
    assert report.substrate_sha in rendered
    for row in report.sweep_rows:
        assert row.weights_sha256[:12] in rendered
    assert (
        report.filtered_bc.weights_sha256
        == (
            (ANCHOR_STUDY_ARTIFACT_ROOT / FILTERED_BC_ENTRANT / "weights.json.sha256")
            .read_text()
            .split()[0]
        )
    )
