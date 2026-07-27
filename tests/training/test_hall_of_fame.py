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
import sys
from collections import Counter
from pathlib import Path

import pytest
from pydantic import ValidationError

from agents.tactical.features import TacticalFeatureEncoderV3, weights_to_hex_json
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


def _v3_genome_length() -> int:
    """The 18.22 encoder-v3 + per-target-head family's exact genome length."""

    from orchestrator.boundary import public_map_from_engine_map

    return policy_genome_length(
        public_map_from_engine_map(load_canonical_map()),
        hidden=_V3_HIDDEN,
        encoder=TacticalFeatureEncoderV3(),
        target_slots=TARGET_KILL_SLOTS,
    )


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

    genome = (0.25, -0.5, 0.75)
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
    assert config["genome_length"] == 3
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


def test_write_loadable_artifact_fail_loud_matrix(tmp_path: Path) -> None:
    """Empty genome, bad stamp token, bad hidden, owned config key, clobber."""

    with pytest.raises(ValueError, match="empty genome"):
        write_loadable_artifact(
            tmp_path / "a",
            (),
            policy_id="p",
            method="m",
            encoder_version="v2",
            hidden=8,
        )
    with pytest.raises(ValueError, match="non-blank"):
        write_loadable_artifact(
            tmp_path / "b", (0.1,), policy_id="  ", method="m", encoder_version="v2"
        )
    with pytest.raises(ValueError, match="MANIFEST-safe"):
        write_loadable_artifact(
            tmp_path / "c", (0.1,), policy_id="a|b", method="m", encoder_version="v2"
        )
    with pytest.raises(ValueError, match="hidden must be >= 1"):
        write_loadable_artifact(
            tmp_path / "d",
            (0.1,),
            policy_id="p",
            method="m",
            encoder_version="v2",
            hidden=0,
        )
    with pytest.raises(ValueError, match="owned by write_loadable_artifact"):
        write_loadable_artifact(
            tmp_path / "e",
            (0.1,),
            policy_id="p",
            method="m",
            encoder_version="v2",
            hidden=8,
            config={"hidden": 4},
        )
    # No partial artifact survives any of the refusals above.
    for name in ("a", "b", "c", "d", "e"):
        assert not (tmp_path / name).exists() or not list((tmp_path / name).iterdir())

    # And the writer never clobbers: a second write into the same dir raises.
    write_loadable_artifact(
        tmp_path / "f",
        (0.1,),
        policy_id="p",
        method="m",
        encoder_version=_UTILITY_ENCODER,
    )
    with pytest.raises(FileExistsError):
        write_loadable_artifact(
            tmp_path / "f",
            (0.2,),
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

    metadata = _metadata(hidden=8, encoder_version="v3", anchor_weight=4.0)
    assert (
        metadata.policy_id_for(origin="exploiter-probe", generation=10)
        == "coevo-run-01-utility-champion-exploiter-probe-gen10"
    )
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
    assert stamp["policy_id"] == (
        "coevo-run-01-utility-champion-alternating-freeze-champion-gen9"
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
