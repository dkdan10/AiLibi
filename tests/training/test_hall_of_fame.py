"""Tests for the co-evolution hall of fame + PFSP-lite sampler (Task 18.20).

Style follows the 18.6 MAP-Elites cell-persistence block of
``test_bakeoff_methods.py``: CHEAP, no game rollouts anywhere. Founder sources
are hand-built archives persisted through the public 18.6 writer
(:func:`training.bakeoff.map_elites.write_archive_cell_artifacts`) whose cell
keys are DERIVED from descriptor values via the public configuration (amendment
A6), never hardcoded; champion-style members are added directly with arbitrary
short genome tuples; payoff maps and seeds are hand-pinned. Every fixture-pinned
tuple/count below was obtained by running the code under the fixed seed and then
hard-pinned here, so a change in the deterministic ``random.Random`` draw order
or the byte conventions trips the assertion.

Tests import ONLY the public surface of :mod:`training.coevo.hall_of_fame` plus
the public 18.6 symbols the founder source needs. ``mypy --strict`` / ``ruff`` /
``lint-imports`` clean.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from agents.tactical.features import (
    TacticalFeatureEncoder,
    TacticalFeatureEncoderV3,
    weights_from_hex_json,
    weights_to_hex_json,
)
from engine.world import load_canonical_map
from training.bakeoff.harness import load_candidate_weights
from training.bakeoff.map_elites import (
    BEHAVIOR_DESCRIPTOR_CONFIGURATION,
    ArchiveCell,
    bakeoff_substrate_sha,
    load_archive_cell_genomes,
    map_elites_budget,
    write_archive_cell_artifacts,
)
from training.bakeoff.policy_es import TARGET_KILL_SLOTS, policy_genome_length
from training.coevo import hall_of_fame
from training.coevo.hall_of_fame import (
    MAP_ELITES_FOUNDER_ORIGIN,
    TRAINED_AGAINST_FSM,
    HallOfFame,
    HallOfFameMember,
    LoadableArtifactMetadata,
    OpponentStalenessCap,
    OpponentStalenessExceededError,
    OpponentStalenessLedger,
    sample_opponents,
    write_loadable_artifact,
)
from training.crew.options import OwnedTaskOptionBasis, crew_genome_length

# Task 19.27: campaign tier (training/README.md §2 FREEZE — co-evolution / campaign machinery).
# Excluded from the default gate; runs weekly in CI's campaign-tier job and
# at phase close via `-m campaign`.
pytestmark = pytest.mark.campaign

# ``scripts/`` is a bare-module namespace (no ``__init__.py``): the loadable-
# freeze pin (Task 18.31) needs the CONSUMING entry point
# ``run_tournament._load_candidate_policy``, so put ``scripts/`` on sys.path the
# way tests/scripts/conftest.py and scripts/measure_baseline.py:76-78 do.
_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import run_tournament  # noqa: E402

# A valid 64-lowercase-hex substrate for store-fidelity tests that do not need
# the real corpus substrate (founder tests use ``bakeoff_substrate_sha()``).
_SUBSTRATE = "ab" * 32
# A stand-in opposing-side sha for a champion bred against a frozen member.
_OPPONENT_SHA = "cd" * 32

# The two impostor families the 18.31 loadable-freeze pin exercises: the
# committed 19-gene utility scorer and the 18.22 encoder-v3 masked MLP.
_UTILITY_ARTIFACT = Path("training/artifacts/impostor/utility-es")
_UTILITY_ENCODER = "impostor-option-features-v1"
_V3_HIDDEN = 8


def _synthetic_archive() -> dict[tuple[int, int, int], ArchiveCell]:
    """Three cells in DISTINCT behavior bins, keys derived from descriptors (A6).

    ``bin_values`` under the default behavior configuration maps the three
    descriptor triples to ``(0, 0, 0)`` / ``(2, 2, 2)`` / ``(5, 3, 3)`` — distinct
    cells with distinct short genomes (so distinct member shas), the exact founder
    source the writer persists.
    """

    specs = [
        (
            {"kill_count": 0.0, "witness_exposure_rate": 0.0, "vent_usage": 0.0},
            (0.1, -0.2, 0.3),
            1.0,
        ),
        (
            {"kill_count": 2.0, "witness_exposure_rate": 0.3, "vent_usage": 4.0},
            (0.4, 0.5, -0.6),
            2.0,
        ),
        (
            {"kill_count": 5.0, "witness_exposure_rate": 0.9, "vent_usage": 7.0},
            (-0.7, 0.8, 0.9),
            3.0,
        ),
    ]
    archive: dict[tuple[int, int, int], ArchiveCell] = {}
    for descriptors, genome, fitness in specs:
        cell_key = BEHAVIOR_DESCRIPTOR_CONFIGURATION.bin_values(descriptors)
        archive[cell_key] = ArchiveCell(
            genome=genome, fitness=fitness, descriptors=descriptors
        )
    return archive


def _persist_two_cell_archive(
    artifact_dir: Path, first: tuple[float, ...], second: tuple[float, ...]
) -> Path:
    """Persist a TWO-cell archive whose sorted cell-key order is (first, second).

    Ingestion walks ``sorted(archive)``, so putting the offending genome second
    is what makes a per-member refusal visible as a partial mutation.
    """

    specs = [
        ({"kill_count": 0.0, "witness_exposure_rate": 0.0, "vent_usage": 0.0}, first),
        ({"kill_count": 5.0, "witness_exposure_rate": 0.9, "vent_usage": 7.0}, second),
    ]
    archive: dict[tuple[int, int, int], ArchiveCell] = {}
    for index, (descriptors, genome) in enumerate(specs):
        cell_key = BEHAVIOR_DESCRIPTOR_CONFIGURATION.bin_values(descriptors)
        archive[cell_key] = ArchiveCell(
            genome=genome, fitness=float(index + 1), descriptors=descriptors
        )
    assert sorted(archive) == list(archive), "cell-key order must match spec order"
    return _persist_archive(archive, artifact_dir)


def _persist_archive(
    archive: dict[tuple[int, int, int], ArchiveCell], artifact_dir: Path
) -> Path:
    """Persist ``archive`` through the public 18.6 writer (records the real substrate)."""

    return write_archive_cell_artifacts(
        archive,
        artifact_dir,
        config=map_elites_budget("ci"),
        descriptor_configuration=BEHAVIOR_DESCRIPTOR_CONFIGURATION,
    )


def _add_champions(hall: HallOfFame) -> dict[str, tuple[float, ...]]:
    """Add a canonical sequence of champion members; return {sha: genome}.

    Two FSM-bred champions and one bred against a frozen opposing-side sha, at
    mixed generations — a deterministic add sequence reused across the store
    round-trip / determinism / drift tests.
    """

    specs: list[tuple[tuple[float, ...], int, str]] = [
        ((0.1, -0.2), 0, TRAINED_AGAINST_FSM),
        ((0.3, 0.4, 0.5), 4, _OPPONENT_SHA),
        ((-0.6, 0.7), 2, TRAINED_AGAINST_FSM),
    ]
    added: dict[str, tuple[float, ...]] = {}
    for genome, generation, trained_against in specs:
        member = hall.add_member(
            genome,
            generation=generation,
            origin="champion",
            trained_against=trained_against,
        )
        added[member.weights_sha256] = genome
    return added


def _sampler_member(char: str, *, generation: int = 0) -> HallOfFameMember:
    """A synthetic member whose sha is ``char * 64`` (for sampler-only tests)."""

    sha = char * 64
    return HallOfFameMember(
        weights_sha256=sha,
        generation=generation,
        origin="champion",
        trained_against=TRAINED_AGAINST_FSM,
        path=f"gen-{generation}/{sha}",
    )


# --------------------------------------------------------------------------- #
# Store fidelity.                                                              #
# --------------------------------------------------------------------------- #


def test_hall_of_fame_create_and_reload_round_trips(tmp_path: Path) -> None:
    """A created + populated pool reloads with identical members + genomes (18.20).

    ``create`` an empty pool, ``add_member`` a few, then ``load`` returns the
    identical ``members`` (provenance intact) sorted by sha, the same
    ``substrate_sha256`` / ``side`` / ``member_shas``, and ``load_member_genome``
    reloads each genome bit-exactly.
    """

    hall = HallOfFame.create(tmp_path, "impostor", substrate_sha256=_SUBSTRATE)
    genomes = _add_champions(hall)

    reloaded = HallOfFame.load(tmp_path, "impostor")
    assert reloaded.members == hall.members
    assert reloaded.member_shas == hall.member_shas == tuple(sorted(genomes))
    assert reloaded.side == "impostor"
    assert reloaded.substrate_sha256 == _SUBSTRATE
    for sha, genome in genomes.items():
        assert reloaded.load_member_genome(sha) == genome


def test_hall_of_fame_index_and_tree_are_byte_deterministic(tmp_path: Path) -> None:
    """The same add sequence into two roots yields byte-identical trees (18.20).

    Sorted-by-sha members + ``sort_keys`` JSON + trailing newline + float-hex
    weights make ``hall_of_fame.json`` AND every member's on-disk bytes a pure
    function of the member set: every relative path and every file's bytes match
    across two independent builds.
    """

    first = HallOfFame.create(tmp_path / "a", "impostor", substrate_sha256=_SUBSTRATE)
    _add_champions(first)
    second = HallOfFame.create(tmp_path / "b", "impostor", substrate_sha256=_SUBSTRATE)
    _add_champions(second)

    first_side = tmp_path / "a" / "impostor"
    second_side = tmp_path / "b" / "impostor"
    assert (first_side / "hall_of_fame.json").read_bytes() == (
        second_side / "hall_of_fame.json"
    ).read_bytes()

    first_files = sorted(
        p.relative_to(first_side) for p in first_side.rglob("*") if p.is_file()
    )
    second_files = sorted(
        p.relative_to(second_side) for p in second_side.rglob("*") if p.is_file()
    )
    assert first_files == second_files
    assert first_files  # the tree is non-empty
    for rel in first_files:
        assert (first_side / rel).read_bytes() == (second_side / rel).read_bytes()


def test_hall_of_fame_member_sidecar_byte_format(tmp_path: Path) -> None:
    """Each member's sidecar is the committed harness byte format (18.20).

    ``weights.json.sha256`` is exactly ``<sha256(weights bytes)>  weights.json\\n``
    and ``weights.json`` ends in a trailing newline — byte-identical to
    :func:`training.bakeoff.harness.write_candidate_artifact`.
    """

    hall = HallOfFame.create(tmp_path, "impostor", substrate_sha256=_SUBSTRATE)
    _add_champions(hall)

    for member in hall.members:
        member_dir = tmp_path / "impostor" / member.path
        weights_bytes = (member_dir / "weights.json").read_bytes()
        assert weights_bytes.endswith(b"\n")
        digest = hashlib.sha256(weights_bytes).hexdigest()
        sidecar = (member_dir / "weights.json.sha256").read_text()
        assert sidecar == f"{digest}  weights.json\n"
        assert digest == member.weights_sha256


def test_hall_of_fame_records_full_provenance(tmp_path: Path) -> None:
    """Index rows carry the full provenance key set; a real sha is recorded (18.20).

    Every row carries ``generation`` / ``weights_sha256`` / ``origin`` /
    ``trained_against`` / ``descriptors`` / ``cell_key`` / ``path``; a champion
    added with ``trained_against=<64-hex sha>`` records THAT sha (not the FSM
    sentinel); the member dir is named by the full sha and
    ``path == "gen-<generation>/<sha>"``.
    """

    hall = HallOfFame.create(tmp_path, "impostor", substrate_sha256=_SUBSTRATE)
    champion = hall.add_member(
        (0.3, 0.4, 0.5),
        generation=4,
        origin="champion",
        trained_against=_OPPONENT_SHA,
    )
    founder_like = hall.add_member(
        (0.1, -0.2, 0.3),
        generation=0,
        origin=MAP_ELITES_FOUNDER_ORIGIN,
        trained_against=TRAINED_AGAINST_FSM,
        descriptors={
            "kill_count": 1.0,
            "witness_exposure_rate": 0.2,
            "vent_usage": 3.0,
        },
        cell_key=(2, 0, 1),
    )

    index = json.loads((tmp_path / "impostor" / "hall_of_fame.json").read_text())
    assert sorted(index) == ["members", "side", "substrate_sha256"]
    rows = {row["weights_sha256"]: row for row in index["members"]}
    assert set(rows[champion.weights_sha256]) == {
        "cell_key",
        "descriptors",
        "generation",
        "origin",
        "path",
        "trained_against",
        "weights_sha256",
    }

    champion_row = rows[champion.weights_sha256]
    assert champion_row["trained_against"] == _OPPONENT_SHA
    assert champion_row["trained_against"] != TRAINED_AGAINST_FSM
    assert champion_row["generation"] == 4
    assert champion_row["descriptors"] is None
    assert champion_row["cell_key"] is None
    assert champion_row["path"] == f"gen-4/{champion.weights_sha256}"
    assert (tmp_path / "impostor" / champion_row["path"]).is_dir()

    founder_row = rows[founder_like.weights_sha256]
    assert founder_row["descriptors"] == {
        "kill_count": 1.0,
        "vent_usage": 3.0,
        "witness_exposure_rate": 0.2,
    }
    assert founder_row["cell_key"] == [2, 0, 1]

    # Provenance is READ-ONLY: the descriptors mapping refuses in-place mutation
    # (the store re-serialises retained members on every add, so a mutable dict
    # would let a caller silently alter persisted provenance — the Codex-review
    # frozen-descriptors guard).
    descriptors = founder_like.descriptors
    assert descriptors is not None
    with pytest.raises(TypeError):
        descriptors["kill_count"] = 9.9  # type: ignore[index]


def test_create_refuses_over_existing_pool(tmp_path: Path) -> None:
    """``create`` never clobbers a committed pool and validates its inputs (18.20).

    A second ``create`` on a side that already has ``hall_of_fame.json`` raises
    :class:`FileExistsError` rather than silently re-initialising it; a
    ``substrate_sha256`` that is not 64 lowercase hex fails loud BEFORE any write
    (amendment A1); and a side dir holding stray ``gen-*`` member artifacts
    WITHOUT an index (an interrupted/half-deleted tree) is refused rather than
    silently adopted under a fresh empty index (the Codex-review dirty-root
    guard).
    """

    with pytest.raises(ValueError, match="64 lowercase hex"):
        HallOfFame.create(tmp_path, "impostor", substrate_sha256="not-a-sha")
    assert not (tmp_path / "impostor").exists()  # the refusal wrote nothing

    HallOfFame.create(tmp_path, "impostor", substrate_sha256=_SUBSTRATE)
    with pytest.raises(FileExistsError):
        HallOfFame.create(tmp_path, "impostor", substrate_sha256=_SUBSTRATE)

    # Stray member artifacts without an index: refused, and no index written.
    dirty_side = tmp_path / "dirty" / "impostor"
    (dirty_side / "gen-0" / ("e" * 64)).mkdir(parents=True)
    with pytest.raises(ValueError, match="stray member artifacts"):
        HallOfFame.create(tmp_path / "dirty", "impostor", substrate_sha256=_SUBSTRATE)
    assert not (dirty_side / "hall_of_fame.json").exists()


def test_add_member_fail_loud_matrix(tmp_path: Path) -> None:
    """``add_member`` fails loud on the committed matrix (18.20).

    A duplicate ``weights_sha256`` (an identical genome re-added), an empty
    genome, a ``trained_against`` that is neither 64-hex nor
    :data:`TRAINED_AGAINST_FSM`, and a target member dir that already exists on
    disk but is not in the index (amendment A5 — on-disk drift) each raise
    :class:`ValueError`.
    """

    hall = HallOfFame.create(tmp_path, "impostor", substrate_sha256=_SUBSTRATE)
    hall.add_member(
        (0.1, -0.2),
        generation=0,
        origin="champion",
        trained_against=TRAINED_AGAINST_FSM,
    )
    with pytest.raises(ValueError, match="already a member"):
        hall.add_member(
            (0.1, -0.2),
            generation=0,
            origin="champion",
            trained_against=TRAINED_AGAINST_FSM,
        )
    with pytest.raises(ValueError, match="empty genome"):
        hall.add_member(
            [], generation=0, origin="champion", trained_against=TRAINED_AGAINST_FSM
        )
    with pytest.raises(ValueError, match="neither a 64-hex"):
        hall.add_member(
            (0.9,), generation=0, origin="champion", trained_against="not-a-sha"
        )

    # A5: the target dir pre-exists on disk (NOT in the index) — refuse loudly
    # rather than overwrite. The dir name is the genome's own digest, computed
    # via the same committed byte convention the store freezes with.
    stray_genome = (0.5, 0.5)
    stray_bytes = (weights_to_hex_json(stray_genome) + "\n").encode("utf-8")
    stray_sha = hashlib.sha256(stray_bytes).hexdigest()
    (tmp_path / "impostor" / "gen-0" / stray_sha).mkdir(parents=True)
    with pytest.raises(ValueError, match="already exists on disk"):
        hall.add_member(
            stray_genome,
            generation=0,
            origin="champion",
            trained_against=TRAINED_AGAINST_FSM,
        )


# --------------------------------------------------------------------------- #
# Founder ingestion.                                                          #
# --------------------------------------------------------------------------- #


def test_founder_ingestion_from_map_elites_cells(tmp_path: Path) -> None:
    """MAP-Elites cells ingest as founders with honest provenance (18.20).

    Persist a synthetic archive at ``bakeoff_substrate_sha()``, ``create`` a hall
    at the SAME substrate, ingest at gen 0. Members carry
    ``origin == map-elites-founder``, ``trained_against == TRAINED_AGAINST_FSM``,
    ``generation == 0``, the cell's ``descriptors`` (verbatim keys) and
    ``cell_key``, ingested in sorted cell-key order; each founder's ``weights.json``
    bytes AND ``weights_sha256`` equal the source cell's (the byte cross-check
    between the two stores); ``load_member_genome`` is bit-exact vs the archive.
    """

    archive = _synthetic_archive()
    cells_dir = _persist_archive(archive, tmp_path / "me")
    substrate = bakeoff_substrate_sha()
    hall = HallOfFame.create(tmp_path / "root", "impostor", substrate_sha256=substrate)

    founders = hall.ingest_map_elites_founders(tmp_path / "me", generation=0)

    # Frozen + returned in sorted cell-key order (amendment A2).
    assert [member.cell_key for member in founders] == sorted(archive)
    reloaded_archive = load_archive_cell_genomes(tmp_path / "me")
    for member in founders:
        assert member.origin == MAP_ELITES_FOUNDER_ORIGIN
        assert member.trained_against == TRAINED_AGAINST_FSM
        assert member.generation == 0
        cell_key = member.cell_key
        assert cell_key is not None
        assert member.descriptors == archive[cell_key].descriptors

        # Byte cross-check: the re-frozen founder equals the source cell exactly.
        source = cells_dir / f"{cell_key[0]}-{cell_key[1]}-{cell_key[2]}"
        founder_dir = tmp_path / "root" / "impostor" / member.path
        source_bytes = (source / "weights.json").read_bytes()
        assert (founder_dir / "weights.json").read_bytes() == source_bytes
        assert member.weights_sha256 == hashlib.sha256(source_bytes).hexdigest()
        assert hall.load_member_genome(member.weights_sha256) == (
            reloaded_archive[cell_key].genome
        )

    # The members property stays sha-sorted regardless of ingestion order.
    assert hall.member_shas == tuple(sorted(hall.member_shas))


def test_founder_ingestion_substrate_mismatch_refused(tmp_path: Path) -> None:
    """A mismatched substrate refuses ingestion before any write (18.20).

    A hall created at a mismatched ``substrate_sha256`` refuses ingestion with
    :class:`ValueError` matching ``adopted substrate`` (raised inside
    :func:`load_archive_cell_genomes`), and NO member dir / gen-0 tree is written
    (the fence trips before pool build). A hall at the matching sha ingests
    cleanly — proving the fence trips only on genuine drift.
    """

    archive = _synthetic_archive()
    _persist_archive(archive, tmp_path / "me")

    mismatched = "deadbeef" * 8  # a valid 64-hex that is NOT the corpus substrate
    assert mismatched != bakeoff_substrate_sha()
    stale_hall = HallOfFame.create(
        tmp_path / "stale", "impostor", substrate_sha256=mismatched
    )
    with pytest.raises(ValueError, match="adopted substrate"):
        stale_hall.ingest_map_elites_founders(tmp_path / "me")
    # No genome was frozen: the side dir holds only the (empty) index.
    stale_side = tmp_path / "stale" / "impostor"
    assert not any(child.name.startswith("gen-") for child in stale_side.iterdir())
    assert stale_hall.member_shas == ()

    fresh_hall = HallOfFame.create(
        tmp_path / "fresh", "impostor", substrate_sha256=bakeoff_substrate_sha()
    )
    founders = fresh_hall.ingest_map_elites_founders(tmp_path / "me")
    assert len(founders) == len(archive)


def test_founder_ingestion_is_all_or_nothing(tmp_path: Path) -> None:
    """A duplicate founder refuses the WHOLE ingest before any write (18.20).

    The Codex-review partial-mutation guard: with a hall already holding a
    member whose genome matches one of the archive's cells, ingestion raises
    :class:`ValueError` during the preflight and the pool is UNTOUCHED — no
    earlier cell frozen, no index rewrite — so a retry starts from the same
    hall. Two cells carrying the identical genome likewise refuse up front.
    """

    archive = _synthetic_archive()
    _persist_archive(archive, tmp_path / "me")
    hall = HallOfFame.create(
        tmp_path / "root", "impostor", substrate_sha256=bakeoff_substrate_sha()
    )
    # Pre-freeze the genome of one of the LATER cells in sorted cell-key order,
    # so a non-preflighted loop would have frozen earlier cells before raising.
    last_cell = sorted(archive)[-1]
    hall.add_member(
        archive[last_cell].genome,
        generation=3,
        origin="champion",
        trained_against=TRAINED_AGAINST_FSM,
    )
    members_before = hall.members
    index_bytes_before = (
        tmp_path / "root" / "impostor" / "hall_of_fame.json"
    ).read_bytes()

    with pytest.raises(ValueError, match="all-or-nothing"):
        hall.ingest_map_elites_founders(tmp_path / "me")

    assert hall.members == members_before  # no founder was frozen
    assert (
        tmp_path / "root" / "impostor" / "hall_of_fame.json"
    ).read_bytes() == index_bytes_before
    reloaded = HallOfFame.load(tmp_path / "root", "impostor")  # tree still clean
    assert reloaded.members == members_before

    # Two cells carrying the IDENTICAL genome refuse up front too.
    twin_specs = [
        {"kill_count": 0.0, "witness_exposure_rate": 0.0, "vent_usage": 0.0},
        {"kill_count": 5.0, "witness_exposure_rate": 0.9, "vent_usage": 7.0},
    ]
    twin_archive: dict[tuple[int, int, int], ArchiveCell] = {
        BEHAVIOR_DESCRIPTOR_CONFIGURATION.bin_values(descriptors): ArchiveCell(
            genome=(0.25, -0.75), fitness=1.0, descriptors=descriptors
        )
        for descriptors in twin_specs
    }
    _persist_archive(twin_archive, tmp_path / "twins")
    twin_hall = HallOfFame.create(
        tmp_path / "twin-root", "impostor", substrate_sha256=bakeoff_substrate_sha()
    )
    with pytest.raises(ValueError, match="identical genome"):
        twin_hall.ingest_map_elites_founders(tmp_path / "twins")
    assert twin_hall.member_shas == ()


# --------------------------------------------------------------------------- #
# Reload drift matrix (mirrors test_map_elites_cell_loader_fails_loud).        #
# --------------------------------------------------------------------------- #


def test_reload_fails_loud_on_weights_drift(tmp_path: Path) -> None:
    """A tampered member's weights fail loud on load AND lazy reload (18.20).

    Tampering a member's ``weights.json`` with DIFFERENT but VALID float-hex (so
    the loader must REACH the sha cross-check, not merely fail to parse) makes
    both ``load`` and ``load_member_genome`` raise :class:`ValueError` matching
    ``hashes to``.
    """

    hall = HallOfFame.create(tmp_path, "impostor", substrate_sha256=_SUBSTRATE)
    _add_champions(hall)
    victim = hall.members[0]
    weights_file = tmp_path / "impostor" / victim.path / "weights.json"
    tampered = json.loads(weights_file.read_text())
    tampered[0] = float(float.fromhex(tampered[0]) + 1.0).hex()
    weights_file.write_text(json.dumps(tampered) + "\n")

    with pytest.raises(ValueError, match="hashes to"):
        HallOfFame.load(tmp_path, "impostor")
    with pytest.raises(ValueError, match="hashes to"):
        hall.load_member_genome(victim.weights_sha256)


def test_reload_fails_loud_on_index_digest_drift(tmp_path: Path) -> None:
    """A consistent-on-disk member the index mis-records fails loud (18.20).

    With ``weights.json`` + its sidecar tampered CONSISTENTLY (both re-hash to a
    new digest) but the index row still recording the ORIGINAL sha, ``load``
    reaches the second cross-check and raises :class:`ValueError` matching
    ``index records``.
    """

    hall = HallOfFame.create(tmp_path, "impostor", substrate_sha256=_SUBSTRATE)
    _add_champions(hall)
    victim = hall.members[0]
    member_dir = tmp_path / "impostor" / victim.path

    weights_file = member_dir / "weights.json"
    tampered = json.loads(weights_file.read_text())
    tampered[0] = float(float.fromhex(tampered[0]) + 1.0).hex()
    new_bytes = json.dumps(tampered) + "\n"
    weights_file.write_text(new_bytes)
    new_digest = hashlib.sha256(new_bytes.encode("utf-8")).hexdigest()
    (member_dir / "weights.json.sha256").write_text(f"{new_digest}  weights.json\n")

    with pytest.raises(ValueError, match="index records"):
        HallOfFame.load(tmp_path, "impostor")


def test_reload_fails_loud_on_dir_drift(tmp_path: Path) -> None:
    """A missing OR a stray member dir fails loud on load (18.20).

    Deleting a member dir the index still references, and adding a stray
    ``gen-9/<ghost>/`` dir the index does NOT list, each make the on-disk member
    set disagree with the index and raise :class:`ValueError` matching ``do not
    match the index``.
    """

    missing_root = tmp_path / "missing"
    hall = HallOfFame.create(missing_root, "impostor", substrate_sha256=_SUBSTRATE)
    _add_champions(hall)
    victim = hall.members[0]
    victim_dir = missing_root / "impostor" / victim.path
    (victim_dir / "weights.json").unlink()
    (victim_dir / "weights.json.sha256").unlink()
    victim_dir.rmdir()
    with pytest.raises(ValueError, match="do not match the index"):
        HallOfFame.load(missing_root, "impostor")

    stray_root = tmp_path / "stray"
    stray_hall = HallOfFame.create(stray_root, "impostor", substrate_sha256=_SUBSTRATE)
    _add_champions(stray_hall)
    (stray_root / "impostor" / "gen-9" / ("0" * 64)).mkdir(parents=True)
    with pytest.raises(ValueError, match="do not match the index"):
        HallOfFame.load(stray_root, "impostor")


def test_reload_fails_loud_on_side_and_path_mismatch(tmp_path: Path) -> None:
    """A side disagreement and a self-inconsistent path each fail loud (18.20).

    An index whose recorded ``side`` disagrees with the requested side, and a row
    whose ``path`` is not ``gen-<generation>/<weights_sha256>``, each raise
    :class:`ValueError`.
    """

    # (a) side mismatch: an impostor-side index loaded as the crew side.
    source = HallOfFame.create(
        tmp_path / "src", "impostor", substrate_sha256=_SUBSTRATE
    )
    _add_champions(source)
    crew_dir = tmp_path / "src" / "crew"
    crew_dir.mkdir()
    (crew_dir / "hall_of_fame.json").write_text(
        (tmp_path / "src" / "impostor" / "hall_of_fame.json").read_text()
    )
    with pytest.raises(ValueError, match="records side"):
        HallOfFame.load(tmp_path / "src", "crew")

    # (b) path self-inconsistency: a row whose path names the wrong generation.
    path_root = tmp_path / "path"
    hall = HallOfFame.create(path_root, "impostor", substrate_sha256=_SUBSTRATE)
    _add_champions(hall)
    index_path = path_root / "impostor" / "hall_of_fame.json"
    index = json.loads(index_path.read_text())
    sha = index["members"][0]["weights_sha256"]
    index["members"][0]["path"] = f"gen-5/{sha}"
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="imply"):
        HallOfFame.load(path_root, "impostor")


# --------------------------------------------------------------------------- #
# Sampler (PFSP-lite).                                                        #
# --------------------------------------------------------------------------- #


def test_sample_opponents_deterministic_under_seed() -> None:
    """The sampler is a pure function of its inputs (18.20).

    Identical ``(members, payoffs, slate_size, seed)`` produce the identical slate
    (the exact returned tuple is pinned under ``seed=1234``); the caller's member
    iteration order does not perturb the result (canonicalized by sha); a
    different seed generally differs. Members ``a``/``b``/``c`` carry payoffs
    ``{a: 0.0, b: 2.0, c: -1.0}`` — ``c`` is the hardest, so it dominates the
    slate.
    """

    a, b, c = _sampler_member("a"), _sampler_member("b"), _sampler_member("c")
    payoffs = {"a" * 64: 0.0, "b" * 64: 2.0, "c" * 64: -1.0}

    slate = sample_opponents([a, b, c], payoffs, slate_size=6, seed=1234)
    assert [member.weights_sha256 for member in slate] == [
        "c" * 64,
        "c" * 64,
        "a" * 64,
        "c" * 64,
        "c" * 64,
        "c" * 64,
    ]
    shuffled = sample_opponents([c, b, a], payoffs, slate_size=6, seed=1234)
    assert shuffled == slate
    other_seed = sample_opponents([a, b, c], payoffs, slate_size=6, seed=9999)
    assert other_seed != slate


def test_sample_opponents_weights_toward_hard_members() -> None:
    """Harder (lower-fitness) members draw more mass; the floor keeps easy present (18.20).

    Member ``a`` is hard (fitness ``-5.0``), ``b`` easy (fitness ``5.0``); over a
    200-draw slate at ``seed=7`` the exact per-member counts are pinned
    (``a`` = 190, ``b`` = 10): the hard member dominates while the easy member is
    rare-but-present via the default ``exploration_floor``.
    """

    a, b = _sampler_member("a"), _sampler_member("b")
    payoffs = {"a" * 64: -5.0, "b" * 64: 5.0}
    slate = sample_opponents([a, b], payoffs, slate_size=200, seed=7)
    counts = Counter(member.weights_sha256 for member in slate)
    assert counts == Counter({"a" * 64: 190, "b" * 64: 10})
    assert counts["a" * 64] > counts["b" * 64] > 0


def test_sample_opponents_all_equal_payoffs_uniform() -> None:
    """Equal payoffs give a uniform slate (18.20).

    With ``hi == lo`` there is no hardness gradient, so the slate is uniform
    independent of the floor; the exact per-member counts are pinned under
    ``seed=42`` (``a`` = 111, ``b`` = 94, ``c`` = 95 over 300 draws).
    """

    a, b, c = _sampler_member("a"), _sampler_member("b"), _sampler_member("c")
    payoffs = {"a" * 64: 1.0, "b" * 64: 1.0, "c" * 64: 1.0}
    slate = sample_opponents([a, b, c], payoffs, slate_size=300, seed=42)
    counts = Counter(member.weights_sha256 for member in slate)
    assert counts == Counter({"a" * 64: 111, "b" * 64: 94, "c" * 64: 95})


def test_sample_opponents_cold_start_empty_payoffs_uniform() -> None:
    """An empty payoff map is a DEFINED cold-start uniform (18.20).

    ``payoffs == {}`` (generation 1: nothing played yet) draws uniformly — the
    pinned counts match the all-equal branch under the same ``seed=42``.
    """

    a, b, c = _sampler_member("a"), _sampler_member("b"), _sampler_member("c")
    slate = sample_opponents([a, b, c], {}, slate_size=300, seed=42)
    counts = Counter(member.weights_sha256 for member in slate)
    assert counts == Counter({"a" * 64: 111, "b" * 64: 94, "c" * 64: 95})


def test_sample_opponents_single_member() -> None:
    """A one-member pool yields that member ``slate_size`` times (18.20)."""

    only = _sampler_member("a")
    slate = sample_opponents([only], {"a" * 64: 3.0}, slate_size=5, seed=0)
    assert slate == (only,) * 5


def test_sample_opponents_fail_loud_matrix() -> None:
    """The sampler fails loud on the committed matrix (18.20).

    An empty member set, a non-empty ``payoffs`` that is missing a member OR
    carries an extra sha, ``slate_size < 1``, ``exploration_floor < 0``, and a
    non-finite payoff entry each raise :class:`ValueError` (the mismatch is
    named — no hidden default). The NaN case pins the exact silent failure the
    Codex review flagged: ``[1.0, NaN, 1.0]`` would otherwise read as a
    no-gradient uniform pool because ``min``/``max`` both skip past the NaN.
    """

    a, b = _sampler_member("a"), _sampler_member("b")
    with pytest.raises(ValueError, match="empty hall of fame"):
        sample_opponents([], {}, slate_size=3, seed=0)
    with pytest.raises(ValueError, match="exactly cover"):
        sample_opponents([a, b], {"a" * 64: 1.0}, slate_size=3, seed=0)
    with pytest.raises(ValueError, match="exactly cover"):
        sample_opponents(
            [a, b],
            {"a" * 64: 1.0, "b" * 64: 1.0, "c" * 64: 1.0},
            slate_size=3,
            seed=0,
        )
    with pytest.raises(ValueError, match="slate_size"):
        sample_opponents([a, b], {}, slate_size=0, seed=0)
    with pytest.raises(ValueError, match="exploration_floor"):
        sample_opponents([a, b], {}, slate_size=3, seed=0, exploration_floor=-0.1)

    c = _sampler_member("c")
    nan_payoffs = {"a" * 64: 1.0, "b" * 64: float("nan"), "c" * 64: 1.0}
    with pytest.raises(ValueError, match="finite"):
        sample_opponents([a, b, c], nan_payoffs, slate_size=3, seed=0)
    with pytest.raises(ValueError, match="finite"):
        sample_opponents(
            [a, b], {"a" * 64: float("inf"), "b" * 64: 1.0}, slate_size=3, seed=0
        )


def test_sample_opponents_strict_hard_floor_zero() -> None:
    """``exploration_floor=0.0`` recovers strict PFSP-hard, safely (18.20).

    With a hardness gradient and floor 0 the EASIEST member's weight is exactly
    0, so it never appears (pinned: ``a`` = 200, ``b`` absent under ``seed=7``);
    with all-equal payoffs and floor 0 the uniform branch still applies (no
    division by zero), reproducing the pinned uniform counts.
    """

    a, b = _sampler_member("a"), _sampler_member("b")
    gradient = {"a" * 64: -5.0, "b" * 64: 5.0}
    slate = sample_opponents(
        [a, b], gradient, slate_size=200, seed=7, exploration_floor=0.0
    )
    counts = Counter(member.weights_sha256 for member in slate)
    assert counts["b" * 64] == 0
    assert counts["a" * 64] == 200

    c = _sampler_member("c")
    equal = {"a" * 64: 1.0, "b" * 64: 1.0, "c" * 64: 1.0}
    uniform = sample_opponents(
        [a, b, c], equal, slate_size=300, seed=42, exploration_floor=0.0
    )
    uniform_counts = Counter(member.weights_sha256 for member in uniform)
    assert uniform_counts == Counter({"a" * 64: 111, "b" * 64: 94, "c" * 64: 95})


# --------------------------------------------------------------------------- #
# Staleness ledger (mirrors SurrogateUseCounter).                             #
# --------------------------------------------------------------------------- #


def test_staleness_ledger_caps_per_member() -> None:
    """A member exhausts its cap after N generations; members accrue independently (18.20).

    With ``max_generations=3``, ``record_generation_use`` returns 1, 2, 3 for a
    member then raises :class:`OpponentStalenessExceededError` naming the sha
    prefix + the cap on the 4th call; a second member accrues on its own count.
    """

    cap = OpponentStalenessCap(max_generations=3, unit="generations")
    sha_a, sha_b = "a" * 64, "b" * 64
    ledger = OpponentStalenessLedger(cap, [sha_a, sha_b])

    assert [ledger.record_generation_use(weights_sha256=sha_a) for _ in range(3)] == [
        1,
        2,
        3,
    ]
    assert ledger.uses(weights_sha256=sha_a) == 3
    with pytest.raises(OpponentStalenessExceededError, match=f"{sha_a[:12]}"):
        ledger.record_generation_use(weights_sha256=sha_a)
    with pytest.raises(OpponentStalenessExceededError, match="cap of 3"):
        ledger.record_generation_use(weights_sha256=sha_a)

    # The other member is unaffected — counts are per-sha.
    assert ledger.record_generation_use(weights_sha256=sha_b) == 1
    assert ledger.uses(weights_sha256=sha_b) == 1


def test_staleness_ledger_sha_keying_and_register() -> None:
    """The ledger meters only shas it was seeded with; register admits new ones (18.20).

    ``record_generation_use`` / ``uses`` for an untracked sha raise
    :class:`ValueError` (the phantom-opponent guard); ``register`` admits a new
    sha at 0 (then it meters normally); a double ``register`` raises
    :class:`ValueError`; and ``OpponentStalenessCap(max_generations=0, ...)`` is
    rejected by pydantic at construction.
    """

    cap = OpponentStalenessCap(max_generations=5, unit="generations")
    seeded, fresh = "a" * 64, "b" * 64
    ledger = OpponentStalenessLedger(cap, [seeded])

    with pytest.raises(ValueError, match="not seeded"):
        ledger.record_generation_use(weights_sha256=fresh)
    with pytest.raises(ValueError, match="not seeded"):
        ledger.uses(weights_sha256=fresh)

    ledger.register(weights_sha256=fresh)
    assert ledger.uses(weights_sha256=fresh) == 0
    assert ledger.record_generation_use(weights_sha256=fresh) == 1
    with pytest.raises(ValueError, match="already tracked"):
        ledger.register(weights_sha256=fresh)

    with pytest.raises(ValidationError):
        OpponentStalenessCap(max_generations=0, unit="generations")


# --------------------------------------------------------------------------- #
# The four-file loadable freeze (Task 18.31).                                  #
# --------------------------------------------------------------------------- #
#
# These extend the module's cheap-fixture doctrine one step: the loadability
# pin needs the CONSUMER (``scripts/run_tournament.py`` ``_load_candidate_policy``,
# imported through the established bare-module bootstrap — the same one
# tests/scripts/conftest.py and scripts/measure_baseline.py:76-78 use), and a
# genome each policy family actually accepts. Still no game rollouts: loading a
# policy rebuilds an object, it plays nothing.


def _masked_mlp_genome_length(encoder_version: str, hidden: int) -> int:
    """The masked-MLP family's exact genome length on the canonical map.

    ``v2`` is the pre-18.22 encoder with NO per-target KILL head; ``v3`` is the
    18.22 encoder-v3 vector feeding a :data:`TARGET_KILL_SLOTS`-wide head. These
    mirror ``policy_es._encoder_for_version``'s two arms.
    """

    from orchestrator.boundary import public_map_from_engine_map

    encoder, target_slots = (
        (TacticalFeatureEncoderV3(), TARGET_KILL_SLOTS)
        if encoder_version == "v3"
        else (TacticalFeatureEncoder(), 0)
    )
    return policy_genome_length(
        public_map_from_engine_map(load_canonical_map()),
        hidden=hidden,
        encoder=encoder,
        target_slots=target_slots,
    )


def _v3_genome_length() -> int:
    """The 18.22 encoder-v3 + per-target-head family's exact genome length."""

    return _masked_mlp_genome_length("v3", _V3_HIDDEN)


@lru_cache(maxsize=None)
def _rebuildable_genome(
    encoder_version: str, hidden: int | None = None
) -> tuple[float, ...]:
    """A genome the CONSUMER's own builder actually accepts for this family.

    The 18.31 writer proves loadability by REBUILDING the genome before it
    freezes anything (Codex review on PR #314), so a toy two-gene stand-in is no
    longer a valid fixture for ANY family — it names a shape no builder has, and
    a fixture like that is exactly the artifact the guard exists to refuse.
    Every length here comes from the family's own public length helper rather
    than a literal, so an encoder change moves these fixtures with it instead of
    silently pinning a stale width.
    """

    if encoder_version in {"v2", "v3"}:
        if hidden is None:
            raise AssertionError(f"{encoder_version!r} needs a hidden width")
        return (0.0,) * _masked_mlp_genome_length(encoder_version, hidden)
    if hidden is not None:
        raise AssertionError(f"{encoder_version!r} takes no hidden width")
    if encoder_version == _UTILITY_ENCODER:
        return load_candidate_weights(_UTILITY_ARTIFACT)
    if encoder_version == "crew-option-features-v1":
        return (0.0,) * crew_genome_length()
    if encoder_version == "crew-option-features-v2":
        return (0.0,) * OwnedTaskOptionBasis().genome_length()
    raise AssertionError(f"no rebuildable fixture for {encoder_version!r}")


def _metadata(**overrides: object) -> LoadableArtifactMetadata:
    base: dict[str, object] = {
        "run_label": "run-01-utility-champion",
        "method": "alternating-freeze-es",
        "encoder_version": _UTILITY_ENCODER,
    }
    base.update(overrides)
    return LoadableArtifactMetadata(**base)  # type: ignore[arg-type]


def test_write_loadable_artifact_writes_the_four_committed_files(
    tmp_path: Path,
) -> None:
    """The writer emits weights + sidecar + five-field stamp + config (18.31).

    Byte conventions are the committed ones: float-hex weights with a trailing
    newline, a ``<digest>  weights.json`` sidecar, and 2-space key-sorted JSON.
    The stamp carries EXACTLY the five ``TacticalPolicyStamp`` fields with
    ``weights_sha256`` computed from the bytes just written; ``config.json``
    carries the declared family plus the caller's provenance.
    """

    genome = _rebuildable_genome(_UTILITY_ENCODER)
    artifact_dir = tmp_path / "member"
    digest = write_loadable_artifact(
        artifact_dir,
        genome,
        policy_id="coevo-run-01-swap-champion-gen3",
        method="alternating-freeze-es",
        encoder_version=_UTILITY_ENCODER,
        config={"campaign": "task-18.31", "trained_against": TRAINED_AGAINST_FSM},
    )

    weights_bytes = (artifact_dir / "weights.json").read_bytes()
    assert weights_bytes == (weights_to_hex_json(genome) + "\n").encode("utf-8")
    assert digest == hashlib.sha256(weights_bytes).hexdigest()
    assert (artifact_dir / "weights.json.sha256").read_text() == (
        f"{digest}  weights.json\n"
    )

    stamp_text = (artifact_dir / "stamp.json").read_text()
    assert stamp_text.endswith("\n")
    stamp = json.loads(stamp_text)
    assert set(stamp) == {
        "anchor_policy",
        "encoder_version",
        "method",
        "policy_id",
        "weights_sha256",
    }
    assert stamp["weights_sha256"] == digest
    assert stamp["anchor_policy"] == "fsm-default"
    assert stamp["encoder_version"] == _UTILITY_ENCODER

    config = json.loads((artifact_dir / "config.json").read_text())
    assert config["encoder_version"] == _UTILITY_ENCODER
    assert config["genome_length"] == len(genome)
    assert "hidden" not in config  # never a zero-ghost for a no-hidden family
    assert config["campaign"] == "task-18.31"
    assert config["trained_against"] == TRAINED_AGAINST_FSM


def test_loadable_artifact_loads_through_candidate_policy_both_families(
    tmp_path: Path,
) -> None:
    """Both impostor families load END TO END through ``_load_candidate_policy``.

    The §11 defect-4 / F14 pin: the 18.24 shortlist could not load through its
    consuming entry point at all. A utility genome and a v3 masked-MLP genome —
    the two shapes the campaign froze — now rebuild through the committed
    loader with the stamp the writer wrote, and the loader's own 17.14
    conflation guard (stamp sha == sidecar digest) passes by construction.
    ``hidden`` comes from ``config.json``, which is exactly what the v3 family
    needs and what §12 Errata item 1 records the absence of.
    """

    utility_dir = tmp_path / "utility"
    utility_digest = write_loadable_artifact(
        utility_dir,
        load_candidate_weights(_UTILITY_ARTIFACT),
        policy_id="coevo-utility-champion",
        method="alternating-freeze-es",
        encoder_version=_UTILITY_ENCODER,
    )
    utility_policy, utility_stamp = run_tournament._load_candidate_policy(utility_dir)
    assert utility_policy.encoder_version == _UTILITY_ENCODER
    assert utility_stamp.weights_sha256 == utility_digest
    assert utility_stamp.policy_id == "coevo-utility-champion"

    v3_dir = tmp_path / "v3"
    v3_digest = write_loadable_artifact(
        v3_dir,
        (0.0,) * _v3_genome_length(),
        policy_id="coevo-freepolicy-v3-gen1",
        method="alternating-freeze-es",
        encoder_version="v3",
        hidden=_V3_HIDDEN,
    )
    assert json.loads((v3_dir / "config.json").read_text())["hidden"] == _V3_HIDDEN
    v3_policy, v3_stamp = run_tournament._load_candidate_policy(v3_dir)
    assert v3_policy.encoder_version == "v3"
    assert v3_stamp.weights_sha256 == v3_digest
    assert v3_stamp.encoder_version == "v3"


@pytest.mark.parametrize(
    ("encoder_version", "hidden", "side"),
    [
        (_UTILITY_ENCODER, None, "impostor"),
        ("v3", _V3_HIDDEN, "impostor"),
        ("crew-option-features-v1", None, "crew"),
        ("crew-option-features-v2", None, "crew"),
    ],
)
def test_read_loadable_artifact_round_trips_every_family(
    tmp_path: Path, encoder_version: str, hidden: int | None, side: str
) -> None:
    """The reader recovers exactly what the writer froze (Task 18.32).

    ``training/`` had a writer for the four-file artifact and no reader — the
    only readers were ``scripts/run_tournament.py``'s private pair, and
    ``training/`` must never import ``scripts/``. The 18.32 crew re-rank arm
    installs a frozen opponent from such a directory, so the reader lives beside
    its writer here and every check the CLI performs is performed by the format's
    own owner: the sha sidecar, the 17.14 stamp/digest binding, the width
    contract, and the proof that the genome rebuilds.
    """

    genome = _rebuildable_genome(encoder_version, hidden)
    artifact_dir = tmp_path / "artifact"
    digest = write_loadable_artifact(
        artifact_dir,
        genome,
        policy_id="coevo-frozen-champion",
        method="alternating-freeze-es",
        encoder_version=encoder_version,
        hidden=hidden,
    )

    artifact = hall_of_fame.read_loadable_artifact(artifact_dir)
    assert artifact.genome == genome
    assert artifact.weights_sha256 == digest
    assert artifact.encoder_version == encoder_version
    assert artifact.hidden == hidden
    assert artifact.policy_id == "coevo-frozen-champion"
    assert artifact.method == "alternating-freeze-es"
    assert artifact.anchor_policy == hall_of_fame.DEFAULT_ANCHOR_POLICY
    # The SIDE is derived from the family, so no caller re-derives which slot an
    # artifact belongs in — the 18.19 conflation guard's precondition.
    assert artifact.side == side


def test_read_loadable_artifact_fail_loud_matrix(tmp_path: Path) -> None:
    """Every way a committed artifact can fail to name its own bytes (18.32).

    A frozen opponent is loaded BEFORE a 30-40 h crew leg spends anything, so
    each of these is a refusal rather than a discovery made halfway through.
    """

    genome = _rebuildable_genome(_UTILITY_ENCODER)

    def _freeze(name: str) -> Path:
        artifact_dir = tmp_path / name
        write_loadable_artifact(
            artifact_dir,
            genome,
            policy_id="coevo-frozen-champion",
            method="alternating-freeze-es",
            encoder_version=_UTILITY_ENCODER,
        )
        return artifact_dir

    with pytest.raises(ValueError, match="is not a directory"):
        hall_of_fame.read_loadable_artifact(tmp_path / "nowhere")

    missing_stamp = _freeze("no-stamp")
    (missing_stamp / "stamp.json").unlink()
    with pytest.raises(ValueError, match="cannot read"):
        hall_of_fame.read_loadable_artifact(missing_stamp)

    bad_json = _freeze("bad-json")
    (bad_json / "stamp.json").write_text("{oops", encoding="utf-8")
    with pytest.raises(ValueError, match="is not valid JSON"):
        hall_of_fame.read_loadable_artifact(bad_json)

    short_stamp = _freeze("short-stamp")
    stamp = json.loads((short_stamp / "stamp.json").read_text(encoding="utf-8"))
    del stamp["anchor_policy"]
    (short_stamp / "stamp.json").write_text(json.dumps(stamp), encoding="utf-8")
    with pytest.raises(ValueError, match="EXACTLY the five stamp fields"):
        hall_of_fame.read_loadable_artifact(short_stamp)

    blank_stamp = _freeze("blank-stamp")
    stamp = json.loads((blank_stamp / "stamp.json").read_text(encoding="utf-8"))
    stamp["policy_id"] = "   "
    (blank_stamp / "stamp.json").write_text(json.dumps(stamp), encoding="utf-8")
    with pytest.raises(ValueError, match="non-blank stamp token"):
        hall_of_fame.read_loadable_artifact(blank_stamp)

    # The genome no longer hashes to what the sidecar records.
    drifted = _freeze("drifted")
    weights = json.loads((drifted / "weights.json").read_text(encoding="utf-8"))
    weights[0] = "0x1.0000000000000p+0"
    (drifted / "weights.json").write_text(json.dumps(weights) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="weights load/verify failed"):
        hall_of_fame.read_loadable_artifact(drifted)

    # The stamp names OTHER bytes than the sidecar records (the 17.14 guard).
    mis_stamped = _freeze("mis-stamped")
    stamp = json.loads((mis_stamped / "stamp.json").read_text(encoding="utf-8"))
    stamp["weights_sha256"] = "0" * 64
    (mis_stamped / "stamp.json").write_text(json.dumps(stamp), encoding="utf-8")
    with pytest.raises(ValueError, match="17.14 conflation guard"):
        hall_of_fame.read_loadable_artifact(mis_stamped)

    # A width-free family may not declare a masked-MLP width …
    wide = _freeze("wide")
    config = json.loads((wide / "config.json").read_text(encoding="utf-8"))
    config["hidden"] = 8
    (wide / "config.json").write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="takes no hidden width"):
        hall_of_fame.read_loadable_artifact(wide)

    # … and a masked-MLP family must.
    narrow = tmp_path / "narrow"
    write_loadable_artifact(
        narrow,
        _rebuildable_genome("v3", _V3_HIDDEN),
        policy_id="coevo-frozen-v3",
        method="alternating-freeze-es",
        encoder_version="v3",
        hidden=_V3_HIDDEN,
    )
    config = json.loads((narrow / "config.json").read_text(encoding="utf-8"))
    del config["hidden"]
    (narrow / "config.json").write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="must carry an integer 'hidden'"):
        hall_of_fame.read_loadable_artifact(narrow)


def test_write_loadable_artifact_fail_loud_matrix(tmp_path: Path) -> None:
    """Empty genome, bad stamp token, bad hidden, owned config key, clobber.

    Every arm that is NOT about the genome shape carries a genome the builder
    accepts, so each refusal is provably the one named in the ``match`` and not
    the reconstruction guard firing first on a toy fixture.
    """

    v2_genome = _rebuildable_genome("v2", _V3_HIDDEN)
    utility_genome = _rebuildable_genome(_UTILITY_ENCODER)

    with pytest.raises(ValueError, match="empty genome"):
        write_loadable_artifact(
            tmp_path / "a",
            (),
            policy_id="p",
            method="m",
            encoder_version="v2",
            hidden=_V3_HIDDEN,
        )
    with pytest.raises(ValueError, match="non-blank"):
        write_loadable_artifact(
            tmp_path / "b",
            v2_genome,
            policy_id="  ",
            method="m",
            encoder_version="v2",
            hidden=_V3_HIDDEN,
        )
    with pytest.raises(ValueError, match="MANIFEST-safe"):
        write_loadable_artifact(
            tmp_path / "c",
            v2_genome,
            policy_id="a|b",
            method="m",
            encoder_version="v2",
            hidden=_V3_HIDDEN,
        )
    with pytest.raises(ValueError, match="hidden must be >= 1"):
        write_loadable_artifact(
            tmp_path / "d",
            v2_genome,
            policy_id="p",
            method="m",
            encoder_version="v2",
            hidden=0,
        )
    with pytest.raises(ValueError, match="owned by write_loadable_artifact"):
        write_loadable_artifact(
            tmp_path / "e",
            v2_genome,
            policy_id="p",
            method="m",
            encoder_version="v2",
            hidden=_V3_HIDDEN,
            config={"hidden": 4},
        )
    # A recognised family with a syntactically valid width and a genome the
    # builder cannot rebuild: all four files would have been written and then
    # refused by the consumer at load time (Codex review on PR #314).
    with pytest.raises(ValueError, match="does not rebuild as 'v2' at hidden=8"):
        write_loadable_artifact(
            tmp_path / "g",
            v2_genome[:-1],
            policy_id="p",
            method="m",
            encoder_version="v2",
            hidden=_V3_HIDDEN,
        )
    # Same defect on a width-free family, where only the LENGTH can be wrong.
    with pytest.raises(ValueError, match="does not rebuild as"):
        write_loadable_artifact(
            tmp_path / "h",
            utility_genome + (0.0,),
            policy_id="p",
            method="m",
            encoder_version=_UTILITY_ENCODER,
        )
    # No partial artifact survives any of the refusals above.
    for name in ("a", "b", "c", "d", "e", "g", "h"):
        assert not (tmp_path / name).exists() or not list((tmp_path / name).iterdir())

    # And the writer never clobbers: a second write into the same dir raises.
    write_loadable_artifact(
        tmp_path / "f",
        utility_genome,
        policy_id="p",
        method="m",
        encoder_version=_UTILITY_ENCODER,
    )
    with pytest.raises(FileExistsError):
        write_loadable_artifact(
            tmp_path / "f",
            tuple(-value for value in utility_genome),  # same shape, other bytes
            policy_id="p",
            method="m",
            encoder_version=_UTILITY_ENCODER,
        )


def test_loadable_artifact_metadata_validation() -> None:
    """The per-hall metadata rejects a stamp it could not honestly write."""

    with pytest.raises(ValidationError):
        _metadata(run_label="   ")
    with pytest.raises(ValidationError):
        _metadata(method="a|b")
    with pytest.raises(ValidationError):
        _metadata(hidden=0)
    with pytest.raises(ValidationError):
        _metadata(anchor_weight=float("inf"))
    # A BOOLEAN width, refused before pydantic's lax mode coerces it. `bool` is
    # an `int` subtype, so `True` would have become a silent width of 1 — an
    # inferred width, which is the §12 Errata item-1 ambiguity (Codex on #314).
    # This needs a mode="before" validator: an after-validator only ever sees
    # the already-coerced `1`.
    for boolean in (True, False):
        with pytest.raises(ValidationError, match="non-boolean integer"):
            _metadata(hidden=boolean)

    metadata = _metadata(hidden=8, encoder_version="v3", anchor_weight=4.0)
    # The id is an IDENTITY: side + origin + generation + a weights
    # discriminator. Origin and generation alone collide across every
    # MAP-Elites founder and across the two sides of one run (Codex #314).
    assert (
        metadata.policy_id_for(
            side="impostor",
            origin="exploiter-probe",
            generation=10,
            weights_sha256="6d327dcb" + "0" * 56,
        )
        == "coevo-run-01-utility-champion-impostor-exploiter-probe-gen10-"
        + "6d327dcb"
        + "0" * 56
    )

    # Two founders sharing origin AND generation no longer collide, and the two
    # sides of one run no longer collide with each other — which is what
    # run_tournament.py's 18.19 cross-stamp guard refuses.
    def _pid(side: str, sha: str) -> str:
        return metadata.policy_id_for(
            side=side,  # type: ignore[arg-type]
            origin="map-elites-founder",
            generation=0,
            weights_sha256=sha,
        )

    assert _pid("impostor", "a" * 64) != _pid("impostor", "b" * 64)
    assert _pid("impostor", "a" * 64) != _pid("crew", "a" * 64)
    provenance = metadata.provenance(
        side="impostor",
        generation=10,
        origin="exploiter-probe",
        trained_against=_OPPONENT_SHA,
        path="gen-10/" + _OPPONENT_SHA,
    )
    assert provenance["campaign"] == "run-01-utility-champion"
    assert provenance["entrant"] == (
        f"run-01-utility-champion/impostor/gen-10/{_OPPONENT_SHA}"
    )
    assert provenance["anchor_weight"] == 4.0
    # The writer owns these; the metadata never smuggles them in as provenance.
    assert not {"encoder_version", "genome_length", "hidden"} & set(provenance)


def test_add_member_with_metadata_freezes_a_loadable_artifact(tmp_path: Path) -> None:
    """Every hall freeze writes the four-file artifact and it LOADS (18.31).

    The pool's stamp metadata is a campaign constant (single-side,
    single-family), so ``add_member`` composes each member's ``policy_id`` and
    provenance from it — and the frozen member loads through the consuming
    entry point without a hand-stamping pass.
    """

    hall = HallOfFame.create(
        tmp_path,
        "impostor",
        substrate_sha256=_SUBSTRATE,
        artifact_metadata=_metadata(anchor_weight=1.0),
    )
    assert hall.artifact_metadata is not None
    member = hall.add_member(
        load_candidate_weights(_UTILITY_ARTIFACT),
        generation=9,
        origin="alternating-freeze-champion",
        trained_against=_OPPONENT_SHA,
    )
    member_dir = tmp_path / "impostor" / member.path
    assert sorted(path.name for path in member_dir.iterdir()) == [
        "config.json",
        "stamp.json",
        "weights.json",
        "weights.json.sha256",
    ]
    stamp = json.loads((member_dir / "stamp.json").read_text())
    assert stamp["weights_sha256"] == member.weights_sha256
    # The FULL digest, not a prefix: an 8-char prefix is 32 bits, so two
    # members could collide on it and re-acquire the ambiguity this removes.
    assert stamp["policy_id"] == (
        "coevo-run-01-utility-champion-impostor-alternating-freeze-champion-gen9"
        f"-{member.weights_sha256}"
    )
    config = json.loads((member_dir / "config.json").read_text())
    assert config["hall_origin"] == "alternating-freeze-champion"
    assert config["trained_against"] == _OPPONENT_SHA
    assert config["generation"] == 9
    assert config["side"] == "impostor"

    policy, loaded_stamp = run_tournament._load_candidate_policy(member_dir)
    assert policy.encoder_version == _UTILITY_ENCODER
    assert loaded_stamp.weights_sha256 == member.weights_sha256

    # The index + reload contract is untouched by the extra files.
    reloaded = HallOfFame.load(tmp_path, "impostor")
    assert reloaded.members == hall.members
    assert reloaded.load_member_genome(member.weights_sha256) == load_candidate_weights(
        _UTILITY_ARTIFACT
    )


def test_add_member_without_metadata_keeps_the_two_file_member(tmp_path: Path) -> None:
    """A pool created without stamp metadata freezes exactly as before (18.31).

    The back-compat pin: the 18.20 store is a genome store first, and a caller
    that declares no family gets the historic weights-only member rather than a
    guessed stamp.
    """

    hall = HallOfFame.create(tmp_path, "impostor", substrate_sha256=_SUBSTRATE)
    assert hall.artifact_metadata is None
    member = hall.add_member(
        (0.1, 0.2), generation=1, origin="champion", trained_against=TRAINED_AGAINST_FSM
    )
    member_dir = tmp_path / "impostor" / member.path
    assert sorted(path.name for path in member_dir.iterdir()) == [
        "weights.json",
        "weights.json.sha256",
    ]


def test_artifact_metadata_round_trips_through_the_index(tmp_path: Path) -> None:
    """A loadable pool STAYS loadable across a reload (Codex on PR #314).

    The metadata is not a property of whoever opens the store — it is the
    pool's own freeze identity. Without persistence a reloaded four-file pool
    would silently start freezing two-file members, recreating the exact
    missing-``stamp.json`` defect this task removes.
    """

    genome = _rebuildable_genome(_UTILITY_ENCODER)
    hall = HallOfFame.create(
        tmp_path, "impostor", substrate_sha256=_SUBSTRATE, artifact_metadata=_metadata()
    )
    hall.add_member(
        genome, generation=1, origin="champion", trained_against=TRAINED_AGAINST_FSM
    )
    index = json.loads((tmp_path / "impostor" / "hall_of_fame.json").read_text())
    assert index["artifact_metadata"]["run_label"] == "run-01-utility-champion"

    # Reloaded WITHOUT re-supplying it: the pool still knows its own identity.
    reloaded = HallOfFame.load(tmp_path, "impostor")
    assert reloaded.artifact_metadata == _metadata()
    member = reloaded.add_member(
        tuple(-value for value in genome),
        generation=2,
        origin="champion",
        trained_against=TRAINED_AGAINST_FSM,
    )
    assert sorted(
        path.name for path in (tmp_path / "impostor" / member.path).iterdir()
    ) == ["config.json", "stamp.json", "weights.json", "weights.json.sha256"]

    # Re-supplying a DIFFERENT identity is loud drift, never a silent override.
    with pytest.raises(ValueError, match="never silently overridden"):
        HallOfFame.load(
            tmp_path, "impostor", artifact_metadata=_metadata(run_label="other-run")
        )
    # Agreeing metadata is accepted.
    assert (
        HallOfFame.load(
            tmp_path, "impostor", artifact_metadata=_metadata()
        ).artifact_metadata
        == _metadata()
    )


def test_a_loadable_pool_with_no_metadata_block_is_refused(tmp_path: Path) -> None:
    """A missing metadata block is corruption, not a legacy pool (Codex #314).

    Treating the two alike skipped every stamp/config verification while those
    files sat on disk, returned a hall with ``artifact_metadata=None``, and its
    next ``add_member`` wrote two files — silently mixing formats and losing the
    campaign's freeze identity.
    """

    hall = HallOfFame.create(
        tmp_path, "impostor", substrate_sha256=_SUBSTRATE, artifact_metadata=_metadata()
    )
    member = hall.add_member(
        _rebuildable_genome(_UTILITY_ENCODER),
        generation=1,
        origin="champion",
        trained_against=TRAINED_AGAINST_FSM,
    )
    assert (tmp_path / "impostor" / member.path / "stamp.json").exists()

    index_path = tmp_path / "impostor" / "hall_of_fame.json"
    # Both shapes a corrupted index takes: the key DELETED, and the key present
    # but null. The value check alone would treat the second as legacy too.
    for drop_key in (True, False):
        index: dict[str, Any] = json.loads(index_path.read_text())
        if drop_key:
            del index["artifact_metadata"]
        else:
            index["artifact_metadata"] = None
        index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")
        with pytest.raises(ValueError, match="metadata block is missing or null"):
            HallOfFame.load(tmp_path, "impostor")

    # A genuinely weights-only pool is unaffected: no stamps, no refusal.
    plain = tmp_path / "plain"
    weights_only = HallOfFame.create(plain, "impostor", substrate_sha256=_SUBSTRATE)
    _add_champions(weights_only)
    assert HallOfFame.load(plain, "impostor").artifact_metadata is None


def test_a_residual_config_json_is_loadable_pool_evidence(tmp_path: Path) -> None:
    """``config.json`` alone still proves the pool was loadable (Codex #314).

    My round-13 guard scanned for ``stamp.json`` only, so a corruption that
    removes the stamps but leaves the config sidecars read as a legacy
    weights-only pool: the next ``add_member`` wrote two files and silently
    converted a corrupted loadable pool into a mixed-format one. Neither file is
    ever written by the two-file path, so EITHER one is evidence.
    """

    hall = HallOfFame.create(
        tmp_path, "impostor", substrate_sha256=_SUBSTRATE, artifact_metadata=_metadata()
    )
    member = hall.add_member(
        _rebuildable_genome(_UTILITY_ENCODER),
        generation=1,
        origin="champion",
        trained_against=TRAINED_AGAINST_FSM,
    )
    member_dir = tmp_path / "impostor" / member.path
    (member_dir / "stamp.json").unlink()
    assert (member_dir / "config.json").exists()

    index_path = tmp_path / "impostor" / "hall_of_fame.json"
    index: dict[str, Any] = json.loads(index_path.read_text())
    del index["artifact_metadata"]
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="metadata block is missing or null"):
        HallOfFame.load(tmp_path, "impostor")

    # Still no over-reach: a pool carrying NEITHER file is genuinely legacy.
    plain = tmp_path / "plain"
    weights_only = HallOfFame.create(plain, "impostor", substrate_sha256=_SUBSTRATE)
    _add_champions(weights_only)
    assert HallOfFame.load(plain, "impostor").artifact_metadata is None


def test_a_dangling_loadable_sidecar_is_still_pool_evidence(tmp_path: Path) -> None:
    """Presence is about the directory ENTRY (Codex review on PR #314).

    My round-14 scan used ``.exists()``, which follows symlinks, so a corruption
    leaving a DANGLING ``stamp.json``/``config.json`` read as a legacy
    weights-only pool — the same downgrade the scan exists to prevent, reached
    through a broken link instead of a deleted file.
    """

    for casualty in ("stamp.json", "config.json"):
        root = tmp_path / casualty
        hall = HallOfFame.create(
            root, "impostor", substrate_sha256=_SUBSTRATE, artifact_metadata=_metadata()
        )
        member = hall.add_member(
            _rebuildable_genome(_UTILITY_ENCODER),
            generation=1,
            origin="champion",
            trained_against=TRAINED_AGAINST_FSM,
        )
        member_dir = root / "impostor" / member.path
        # Both sidecars gone as FILES; the reported one left as a broken link.
        for name in ("stamp.json", "config.json"):
            (member_dir / name).unlink()
        (member_dir / casualty).symlink_to(member_dir / "gone.json")
        assert not (member_dir / casualty).exists()
        assert (member_dir / casualty).is_symlink()

        index_path = root / "impostor" / "hall_of_fame.json"
        index: dict[str, Any] = json.loads(index_path.read_text())
        del index["artifact_metadata"]
        index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")
        with pytest.raises(ValueError, match="metadata block is missing or null"):
            HallOfFame.load(root, "impostor")


def test_the_side_family_registry_is_immutable(tmp_path: Path) -> None:
    """``Final`` prevents rebinding, not mutation (Codex review on PR #314).

    A module-level ``dict`` let any code add or replace an allowed side/family
    mapping and change loadability validation globally for every hall created or
    loaded afterwards — validation owned by mutable module state rather than by
    the state passed in. This is the round-6 module-level-mutable-state finding
    reappearing in a registry I added in round 14.
    """

    with pytest.raises(TypeError):
        hall_of_fame._SIDE_ENCODERS["crew"] = frozenset({"v3"})  # type: ignore[index]
    with pytest.raises(AttributeError):
        hall_of_fame._SIDE_ENCODERS.clear()  # type: ignore[attr-defined]

    # And the refusal it backs still holds afterwards.
    with pytest.raises(ValueError, match="belongs to the other side"):
        HallOfFame.create(
            tmp_path, "crew", substrate_sha256=_SUBSTRATE, artifact_metadata=_metadata()
        )


def test_a_pool_may_not_declare_the_other_sides_encoder_family(
    tmp_path: Path,
) -> None:
    """A freeze family belongs to a SIDE (Codex review on PR #314).

    ``_refuse_unloadable_family`` proves SOME consumer can rebuild the family
    and says nothing about which, so a crew hall could carry impostor ``v3``
    metadata: every freeze would be proven against the impostor builder and then
    rejected by ``_load_candidate_policy`` when read back as a crew candidate.
    """

    impostor_meta = _metadata()
    with pytest.raises(ValueError, match="belongs to the other side"):
        HallOfFame.create(
            tmp_path / "a",
            "crew",
            substrate_sha256=_SUBSTRATE,
            artifact_metadata=impostor_meta,
        )
    # Refused BEFORE anything durable: no index was committed, so a corrected
    # retry is not blocked by create's own no-clobber guard.
    assert not (tmp_path / "a" / "crew" / "hall_of_fame.json").exists()

    # The same declaration on its OWN side is fine — no over-reach.
    hall = HallOfFame.create(
        tmp_path / "b",
        "impostor",
        substrate_sha256=_SUBSTRATE,
        artifact_metadata=impostor_meta,
    )
    assert hall.artifact_metadata is not None

    # And a hand-edited index carrying the mismatch is refused on the way back
    # in, or the refusal is only as durable as the process that wrote it.
    index_path = tmp_path / "b" / "impostor" / "hall_of_fame.json"
    index: dict[str, Any] = json.loads(index_path.read_text())
    index["side"] = "crew"
    crew_dir = tmp_path / "b" / "crew"
    crew_dir.mkdir(parents=True)
    (crew_dir / "hall_of_fame.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n"
    )
    with pytest.raises(ValueError, match="belongs to the other side"):
        HallOfFame.load(tmp_path / "b", "crew")


def test_weights_only_pool_index_bytes_are_unchanged(tmp_path: Path) -> None:
    """A pool that declares no family records no metadata key (18.31).

    The persistence is additive: a weights-only pool's ``hall_of_fame.json``
    carries exactly the 18.20 key set, so committed pools reload untouched.
    """

    hall = HallOfFame.create(tmp_path, "impostor", substrate_sha256=_SUBSTRATE)
    _add_champions(hall)
    index = json.loads((tmp_path / "impostor" / "hall_of_fame.json").read_text())
    assert set(index) == {"members", "side", "substrate_sha256"}
    assert HallOfFame.load(tmp_path, "impostor").artifact_metadata is None


def test_write_loadable_artifact_refuses_a_nonempty_dir(tmp_path: Path) -> None:
    """A stray file in the target dir refuses the freeze (Codex on PR #314).

    Exclusive opens alone only guard the four known filenames, so a stale or
    unrelated file would be silently adopted into a five-file "artifact".
    """

    artifact_dir = tmp_path / "member"
    artifact_dir.mkdir()
    (artifact_dir / "stale-notes.txt").write_text("left over from an earlier pass")
    with pytest.raises(FileExistsError, match="non-empty artifact dir"):
        write_loadable_artifact(
            artifact_dir,
            _rebuildable_genome(_UTILITY_ENCODER),
            policy_id="p",
            method="m",
            encoder_version=_UTILITY_ENCODER,
        )
    # Nothing was written beside the stray file.
    assert sorted(path.name for path in artifact_dir.iterdir()) == ["stale-notes.txt"]


def test_loading_a_loadable_pool_verifies_all_four_files(tmp_path: Path) -> None:
    """A pool that advertises loadable members verifies four files, not two.

    Restoring the metadata is a promise that every member loads through
    ``_load_candidate_policy``; checking only weights + sidecar would hand back
    a hall whose members fail at spend time instead of resume time (Codex on
    PR #314). The module's eager two-pass posture is that corruption surfaces
    at load.
    """

    def _fresh(root: Path) -> HallOfFameMember:
        hall = HallOfFame.create(
            root,
            "impostor",
            substrate_sha256=_SUBSTRATE,
            artifact_metadata=_metadata(),
        )
        return hall.add_member(
            _rebuildable_genome(_UTILITY_ENCODER),
            generation=1,
            origin="champion",
            trained_against=TRAINED_AGAINST_FSM,
        )

    # A member whose stamp.json was removed.
    missing = tmp_path / "missing"
    member = _fresh(missing)
    (missing / "impostor" / member.path / "stamp.json").unlink()
    with pytest.raises(ValueError, match="missing part of its loadable artifact"):
        HallOfFame.load(missing, "impostor")

    # A member stamped for a DIFFERENT family than the pool declares.
    wrong_family = tmp_path / "family"
    member = _fresh(wrong_family)
    stamp_path = wrong_family / "impostor" / member.path / "stamp.json"
    stamp = json.loads(stamp_path.read_text())
    stamp["encoder_version"] = "v3"
    stamp_path.write_text(json.dumps(stamp, indent=2, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="a hall stays "):
        HallOfFame.load(wrong_family, "impostor")

    # A member whose stamp names another genome (the 17.14 conflation guard).
    wrong_sha = tmp_path / "sha"
    member = _fresh(wrong_sha)
    stamp_path = wrong_sha / "impostor" / member.path / "stamp.json"
    stamp = json.loads(stamp_path.read_text())
    stamp["weights_sha256"] = "0" * 64
    stamp_path.write_text(json.dumps(stamp, indent=2, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="conflation guard"):
        HallOfFame.load(wrong_sha, "impostor")

    # A healthy loadable pool still reloads cleanly.
    healthy = tmp_path / "healthy"
    _fresh(healthy)
    assert HallOfFame.load(healthy, "impostor").artifact_metadata == _metadata()


def test_loadable_reload_verifies_the_whole_stamp_and_the_width(
    tmp_path: Path,
) -> None:
    """The eager load checks all five stamp fields AND the rebuild width (18.31).

    Checking only the sha and the family still let a member missing ``method``,
    or carrying a drifted ``hidden``, pass reload and fail later inside
    ``_load_candidate_policy`` — deferring artifact corruption to the campaign
    path the eager pass exists to protect (Codex on PR #314).
    """

    def _fresh(root: Path, **overrides: object) -> HallOfFameMember:
        metadata = _metadata(**overrides)
        hall = HallOfFame.create(
            root,
            "impostor",
            substrate_sha256=_SUBSTRATE,
            artifact_metadata=metadata,
        )
        return hall.add_member(
            _rebuildable_genome(metadata.encoder_version, metadata.hidden),
            generation=1,
            origin="champion",
            trained_against=TRAINED_AGAINST_FSM,
        )

    # A stamp missing a required field.
    root = tmp_path / "field"
    member = _fresh(root)
    stamp_path = root / "impostor" / member.path / "stamp.json"
    stamp = json.loads(stamp_path.read_text())
    del stamp["method"]
    stamp_path.write_text(json.dumps(stamp, indent=2, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="missing stamp fields"):
        HallOfFame.load(root, "impostor")

    # A stamp field that is blank (the committed reader would reject it).
    root = tmp_path / "blank"
    member = _fresh(root)
    stamp_path = root / "impostor" / member.path / "stamp.json"
    stamp = json.loads(stamp_path.read_text())
    stamp["policy_id"] = "   "
    stamp_path.write_text(json.dumps(stamp, indent=2, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="non-blank stamp token"):
        HallOfFame.load(root, "impostor")

    # A config whose rebuild width drifted from the pool's declared one.
    root = tmp_path / "width"
    member = _fresh(root, encoder_version="v3", hidden=8)
    config_path = root / "impostor" / member.path / "config.json"
    config = json.loads(config_path.read_text())
    config["hidden"] = 4
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="records hidden"):
        HallOfFame.load(root, "impostor")

    # A v3 pool with an intact artifact still reloads.
    root = tmp_path / "ok"
    _fresh(root, encoder_version="v3", hidden=8)
    reloaded = HallOfFame.load(root, "impostor")
    assert reloaded.artifact_metadata is not None
    assert reloaded.artifact_metadata.hidden == 8


def test_loadable_reload_verifies_stamp_IDENTITY_not_just_syntax(
    tmp_path: Path,
) -> None:
    """A syntactically valid but WRONG stamp is false provenance (Codex on PR #314).

    Round 3 checked that ``method`` / ``anchor_policy`` / ``policy_id`` were
    present, string-typed and MANIFEST-safe — but never that they were the
    values this pool's own metadata reconstructs. So a member re-stamped for
    another campaign, method or anchor reloaded cleanly and carried that false
    provenance into every recording it seeded: the §12 Errata item-1 defect
    wearing a valid name. The pool metadata plus the member row determine all
    three exactly, so there is no reason to accept a mismatch.
    """

    def _fresh(root: Path) -> HallOfFameMember:
        hall = HallOfFame.create(
            root,
            "impostor",
            substrate_sha256=_SUBSTRATE,
            artifact_metadata=_metadata(),
        )
        return hall.add_member(
            _rebuildable_genome(_UTILITY_ENCODER),
            generation=1,
            origin="champion",
            trained_against=TRAINED_AGAINST_FSM,
        )

    for field, forged in (
        ("method", "some-other-method"),
        ("anchor_policy", "some-other-anchor"),
        ("policy_id", "coevo-other-run-champion-gen1"),
    ):
        root = tmp_path / field
        member = _fresh(root)
        stamp_path = root / "impostor" / member.path / "stamp.json"
        stamp = json.loads(stamp_path.read_text())
        assert stamp[field] != forged
        stamp[field] = forged
        stamp_path.write_text(json.dumps(stamp, indent=2, sort_keys=True) + "\n")
        with pytest.raises(ValueError, match=f"records {field} "):
            HallOfFame.load(root, "impostor")

    # A member whose policy_id names the WRONG generation is caught too: the
    # id encodes (run, origin, generation), so drift there mislabels the row.
    root = tmp_path / "generation"
    member = _fresh(root)
    stamp_path = root / "impostor" / member.path / "stamp.json"
    stamp = json.loads(stamp_path.read_text())
    stamp["policy_id"] = stamp["policy_id"].replace("gen1", "gen7")
    stamp_path.write_text(json.dumps(stamp, indent=2, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="records policy_id "):
        HallOfFame.load(root, "impostor")

    # An untampered pool still reloads.
    root = tmp_path / "ok"
    _fresh(root)
    assert HallOfFame.load(root, "impostor").artifact_metadata == _metadata()


def test_loadable_reload_refuses_a_stamp_the_consumer_would_refuse(
    tmp_path: Path,
) -> None:
    """The stamp key set must EQUAL the five, not merely contain them.

    ``_load_candidate_policy`` parses the same file through
    ``TacticalPolicyStamp``, which is ``extra="forbid"``. A subset check let the
    eager verifier certify a member as loadable that the consuming entry point
    rejects — and this task's whole invariant is that the consumer can load
    every freeze (Codex on PR #314).
    """

    hall = HallOfFame.create(
        tmp_path / "pool",
        "impostor",
        substrate_sha256=_SUBSTRATE,
        artifact_metadata=_metadata(),
    )
    member = hall.add_member(
        _rebuildable_genome(_UTILITY_ENCODER),
        generation=1,
        origin="champion",
        trained_against=TRAINED_AGAINST_FSM,
    )
    stamp_path = tmp_path / "pool" / "impostor" / member.path / "stamp.json"
    stamp = json.loads(stamp_path.read_text())
    stamp["surprise_field"] = "valid-looking"
    stamp_path.write_text(json.dumps(stamp, indent=2, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="unexpected stamp fields"):
        HallOfFame.load(tmp_path / "pool", "impostor")


def test_loadable_reload_verifies_config_provenance_against_the_member_row(
    tmp_path: Path,
) -> None:
    """config.json's provenance half is reconstructible, so a mismatch is false history.

    Round 4 verified only ``encoder_version`` and ``hidden`` from config.json,
    leaving ``genome_length``, ``campaign``, ``generation``, ``hall_origin``,
    ``trained_against``, ``entrant`` and ``source_lineage`` unverified — every
    one of them derivable from the verified weights plus the member row (Codex
    on PR #314).
    """

    def _fresh(root: Path) -> HallOfFameMember:
        hall = HallOfFame.create(
            root,
            "impostor",
            substrate_sha256=_SUBSTRATE,
            artifact_metadata=_metadata(),
        )
        return hall.add_member(
            _rebuildable_genome(_UTILITY_ENCODER),
            generation=1,
            origin="champion",
            trained_against=TRAINED_AGAINST_FSM,
        )

    for field, forged in (
        ("genome_length", 99),
        ("campaign", "some-other-campaign"),
        ("generation", 7),
        ("hall_origin", "some-other-origin"),
        ("trained_against", "b" * 64),
        ("entrant", "some-other-entrant"),
        ("source_lineage", "some-other-lineage"),
    ):
        root = tmp_path / field
        member = _fresh(root)
        config_path = root / "impostor" / member.path / "config.json"
        config = json.loads(config_path.read_text())
        assert config[field] != forged
        config[field] = forged
        config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
        with pytest.raises(ValueError, match="provenance disagrees"):
            HallOfFame.load(root, "impostor")

    # An EXTRA key is false history too: verifying only the reconstructible
    # subset let a member carry fabricated audit provenance the hall cannot
    # rebuild, on an artifact it certifies loadable (Codex on PR #314).
    root = tmp_path / "extra-key"
    member = _fresh(root)
    config_path = root / "impostor" / member.path / "config.json"
    config = json.loads(config_path.read_text())
    config["fabricated_lineage_note"] = "bred from a run that never happened"
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="carries unexpected keys"):
        HallOfFame.load(root, "impostor")

    # And a width-free family never carries a null-ghost ``hidden``: the writer
    # OMITS the key, so an explicit JSON null is a file this pool did not write
    # even though its value comparison against ``metadata.hidden`` passes.
    root = tmp_path / "hidden-ghost"
    member = _fresh(root)
    config_path = root / "impostor" / member.path / "config.json"
    config = json.loads(config_path.read_text())
    config["hidden"] = None
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="carries unexpected keys"):
        HallOfFame.load(root, "impostor")

    # A key the writer DOES own, removed, is caught by the same closed set.
    root = tmp_path / "missing-key"
    member = _fresh(root)
    config_path = root / "impostor" / member.path / "config.json"
    config = json.loads(config_path.read_text())
    del config["genome_length"]
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="provenance disagrees|is missing"):
        HallOfFame.load(root, "impostor")

    root = tmp_path / "ok"
    _fresh(root)
    assert HallOfFame.load(root, "impostor").artifact_metadata == _metadata()


def test_a_failed_freeze_leaves_no_partial_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The four-file freeze publishes atomically (Codex on PR #314).

    Writing straight into the destination left a NON-EMPTY partial artifact on
    any mid-way failure; the retry then hit the non-empty-dir refusal while
    ``add_member`` had not indexed the member, so the campaign could not
    recover without a manual delete. Staged and renamed, the destination is
    either absent or complete.
    """

    artifact_dir = tmp_path / "pool" / "gen-1" / "abc"
    genome = _rebuildable_genome("v3", 8)
    real_fsync = os.fsync
    calls = {"n": 0}

    def _fail_on_third(fd: int) -> None:
        calls["n"] += 1
        if calls["n"] == 3:
            raise OSError("disk full")
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", _fail_on_third)
    with pytest.raises(OSError, match="disk full"):
        write_loadable_artifact(
            artifact_dir,
            genome,
            policy_id="p",
            method="m",
            encoder_version="v3",
            hidden=8,
        )
    monkeypatch.undo()

    # Nothing partial was published, and no staging dir was left behind.
    assert not artifact_dir.exists()
    assert list((tmp_path / "pool" / "gen-1").iterdir()) == []

    # The retry now succeeds, which is the whole point.
    write_loadable_artifact(
        artifact_dir,
        genome,
        policy_id="p",
        method="m",
        encoder_version="v3",
        hidden=8,
    )
    assert sorted(p.name for p in artifact_dir.iterdir()) == [
        "config.json",
        "stamp.json",
        "weights.json",
        "weights.json.sha256",
    ]


@pytest.mark.parametrize(
    ("encoder_version", "hidden", "match"),
    [
        ("v3", None, "needs an integer 'hidden'"),
        ("v2", None, "needs an integer 'hidden'"),
        ("impostor-option-features-v1", 8, "takes no hidden width"),
        ("crew-option-features-v1", 8, "takes no hidden width"),
        ("some-unknown-family", None, "not one the consuming entry point"),
        ("v9", 8, "not one the consuming entry point"),
    ],
)
def test_the_public_writer_refuses_an_unloadable_family(
    tmp_path: Path, encoder_version: str, hidden: int | None, match: str
) -> None:
    """``write_loadable_artifact`` validates the family it is publishing.

    The driver preflight already proves loadability for a campaign, but this
    writer is PUBLIC: a caller reaching it directly could publish a v2/v3 freeze
    with no ``hidden`` (which ``_load_candidate_policy`` always rejects) or an
    encoder tag with no builder at all, and a ``HallOfFame`` would then index
    and reload artifacts the consuming entry point cannot load (Codex on
    PR #314).
    """

    artifact_dir = tmp_path / "artifact"
    with pytest.raises(ValueError, match=match):
        write_loadable_artifact(
            artifact_dir,
            (0.1, 0.2),
            policy_id="p",
            method="m",
            encoder_version=encoder_version,
            hidden=hidden,
        )
    # Refused BEFORE anything was published.
    assert not artifact_dir.exists()


def test_founder_ingest_preflights_every_genome_before_any_write(
    tmp_path: Path,
) -> None:
    """A bad founder at position N must not leave 1..N-1 written (Codex #314).

    ``ingest_map_elites_founders`` is all-or-nothing, but the loadable-freeze
    refusals (non-finite genes, a genome the declared family cannot rebuild)
    used to fire from inside its ``add_member`` loop — so the hall ended up
    partially populated, and the driver's create-only retry path refuses that.
    The genome checks now run with the digest checks, before the first write.
    """

    good = _rebuildable_genome(_UTILITY_ENCODER)
    for bad, match in (
        ((float("nan"),) + good[1:], "non-finite genes"),
        (good + (0.0,), "does not rebuild"),
    ):
        root = tmp_path / f"pool-{match.split()[0]}"
        cells = tmp_path / f"cells-{match.split()[0]}"
        # Sorted cell-key order puts the BAD cell second, so a per-member
        # refusal would fire only after the first founder was written.
        _persist_two_cell_archive(cells, good, bad)
        hall = HallOfFame.create(
            root,
            "impostor",
            substrate_sha256=bakeoff_substrate_sha(),
            artifact_metadata=_metadata(),
        )
        with pytest.raises(ValueError, match=match):
            hall.ingest_map_elites_founders(cells)
        # NOTHING was written: no members indexed, no member dirs on disk.
        assert hall.members == ()
        assert HallOfFame.load(root, "impostor").members == ()
        assert (
            sorted(path.name for path in (root / "impostor").iterdir() if path.is_dir())
            == []
        )


def test_a_non_finite_genome_is_refused_before_anything_is_written(
    tmp_path: Path,
) -> None:
    """NaN/inf genes are refused, not frozen (Codex on PR #314).

    They survive the whole pipeline silently: ``weights_to_hex_json`` writes the
    bare tokens ``"nan"`` / ``"inf"``, ``weights_from_hex_json`` rehydrates them
    without complaint, and every builder accepts them — so the reconstruction
    guard CERTIFIES such an artifact as loadable while its policy propagates
    non-finite logits into every evaluation it seeds.
    """

    finite = _rebuildable_genome(_UTILITY_ENCODER)
    # The premise, asserted rather than assumed: the encoding really does
    # round-trip non-finite values, which is why the writer must catch them.
    poisoned = (float("nan"),) + finite[1:]
    assert math.isnan(weights_from_hex_json(weights_to_hex_json(poisoned))[0])

    for bad in (float("nan"), float("inf"), float("-inf")):
        genome = (bad,) + finite[1:]
        artifact_dir = tmp_path / f"artifact-{bad}"
        with pytest.raises(ValueError, match="non-finite genes"):
            write_loadable_artifact(
                artifact_dir,
                genome,
                policy_id="p",
                method="m",
                encoder_version=_UTILITY_ENCODER,
            )
        assert not artifact_dir.exists()

    # The finite genome still freezes.
    assert write_loadable_artifact(
        tmp_path / "ok",
        finite,
        policy_id="p",
        method="m",
        encoder_version=_UTILITY_ENCODER,
    )


def test_metadata_refuses_a_family_no_hall_could_freeze(tmp_path: Path) -> None:
    """An unloadable family is refused BEFORE a hall is persisted (Codex #314).

    ``HallOfFame.create`` commits ``hall_of_fame.json`` from this metadata. When
    the family/width contract was checked only by ``write_loadable_artifact``,
    an index was written, the first ``add_member`` failed, and the retry with
    corrected metadata hit ``create``'s no-clobber guard — an unusable hall only
    a manual delete could clear. That is the round-8 runner-identity deadlock in
    different clothes, and it gets the same answer: refuse before anything
    durable exists.
    """

    for kwargs, match in (
        ({"encoder_version": "v2"}, "needs an integer 'hidden'"),
        ({"encoder_version": "v3"}, "needs an integer 'hidden'"),
        ({"encoder_version": "some-unknown-family"}, "not one the consuming entry"),
        ({"encoder_version": _UTILITY_ENCODER, "hidden": 8}, "takes no hidden width"),
        (
            {"encoder_version": "crew-option-features-v1", "hidden": 8},
            "takes no hidden width",
        ),
    ):
        with pytest.raises(ValidationError, match=match):
            _metadata(**kwargs)

    # Nothing durable is created on the way to that refusal, and a corrected
    # declaration still builds a working hall in the SAME root — the recovery
    # the deadlock denied.
    root = tmp_path / "pool"
    with pytest.raises(ValidationError):
        HallOfFame.create(
            root,
            "impostor",
            substrate_sha256=_SUBSTRATE,
            artifact_metadata=_metadata(encoder_version="v3"),
        )
    assert not (root / "impostor" / "hall_of_fame.json").exists()
    hall = HallOfFame.create(
        root,
        "impostor",
        substrate_sha256=_SUBSTRATE,
        artifact_metadata=_metadata(encoder_version="v3", hidden=_V3_HIDDEN),
    )
    member = hall.add_member(
        _rebuildable_genome("v3", _V3_HIDDEN),
        generation=1,
        origin="champion",
        trained_against=TRAINED_AGAINST_FSM,
    )
    assert sorted(
        path.name for path in (root / "impostor" / member.path).iterdir()
    ) == ["config.json", "stamp.json", "weights.json", "weights.json.sha256"]


def test_the_public_writer_accepts_every_loadable_family(tmp_path: Path) -> None:
    """The guard rejects unloadable combinations, not legitimate ones."""

    for index, (encoder_version, hidden) in enumerate(
        [
            ("v2", 8),
            ("v3", 16),
            ("impostor-option-features-v1", None),
            ("crew-option-features-v1", None),
            ("crew-option-features-v2", None),
        ]
    ):
        artifact_dir = tmp_path / f"ok-{index}"
        write_loadable_artifact(
            artifact_dir,
            _rebuildable_genome(encoder_version, hidden),
            policy_id="p",
            method="m",
            encoder_version=encoder_version,
            hidden=hidden,
        )
        config = json.loads((artifact_dir / "config.json").read_text())
        assert config["encoder_version"] == encoder_version
        assert config.get("hidden") == hidden
