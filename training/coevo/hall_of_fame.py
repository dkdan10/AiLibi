"""The co-evolution hall of fame + PFSP-lite opponent sampler (Task 18.20).

The opponent-pool half of the co-evo track: where
:mod:`training.coevo.factory` / :mod:`training.coevo.rollout` (Task 18.19)
compose ONE dual-role game, this module owns the FROZEN opponents that game is
played against and the deterministic policy for drawing which of them the
moving side faces each generation. It is the seam the audit calls for
(audits/audit-phase-18-planning.md §4 (#8) — a persisted, behaviorally-diverse
opponent pool seeded from the 18.6 MAP-Elites archive — realized with the
§6 AlphaStar/PSRO transfer: prioritized fictitious self-play against a league
of frozen past selves, sized down to a ``<=30``-member pool).

Three doctrines the module mirrors verbatim from committed siblings:

* **Artifact bytes** — every frozen member freezes under
  ``gen-<N>/<weights_sha256>/`` as a float-hex ``weights.json`` + its
  ``<digest>  weights.json`` sidecar, the EXACT byte conventions of
  :func:`training.bakeoff.harness.write_candidate_artifact` (harness.py:1501-1526)
  and :func:`training.bakeoff.map_elites.write_archive_cell_artifacts`. Because a
  founder is re-frozen from the bit-exact ``tuple[float, ...]`` the 18.6 loader
  returns, its bytes and digest are IDENTICAL to the source cell's — the two
  stores agree at the byte level. Everything on disk reloads bit-exactly, and
  ``load`` re-hashes every member EAGERLY (the ``load_archive_cell_genomes``
  two-pass drift posture) so corruption is caught at campaign-resume time.

* **Staleness** — :class:`OpponentStalenessLedger` is the co-evo analogue of
  :class:`training.surrogate.runner.SurrogateUseCounter` (runner.py:105-148): an
  explicit, in-memory, run-scoped meter the 18.21 driver constructs ONCE and
  threads through the alternating-freeze loop, sha-keyed so it can never meter an
  opponent it was not seeded with. Counts are NEVER persisted into
  ``hall_of_fame.json`` — the on-disk index stays a pure function of the frozen
  genomes + provenance, and staleness is a run policy over that store.

* **Fail loud, never paper over** (AGENTS.md) — ``create`` refuses to clobber a
  committed pool, ``load`` fails loud on the full drift matrix, the founder
  ingest arms the 18.6 stale-substrate fence at the ingest point, and the
  sampler refuses a payoff map that does not exactly cover the pool. "Unknown
  provenance" is not representable: a member bred against the fixed scripted FSM
  carries the reserved :data:`TRAINED_AGAINST_FSM` sentinel, never ``None``.

Pure stdlib + pydantic v2 (no numpy — the sampler follows the es.py:25 /
map_elites training-layer RNG doctrine: a pure-Python ``random.Random`` stream
is bit-stable across machines where a numpy reduction is not). No ``engine``
imports (the observation firewall is untouched). No global state.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Final, Literal, TypeGuard

from pydantic import BaseModel, ConfigDict, Field

from agents.tactical.features import weights_from_hex_json, weights_to_hex_json
from training.bakeoff.map_elites import ArchiveCell, load_archive_cell_genomes

Side = Literal["impostor", "crew"]

# --------------------------------------------------------------------------- #
# Module constants.                                                           #
# --------------------------------------------------------------------------- #

# The two campaign sides; a hall is single-side (one instance per side per run).
_SIDES: Final[tuple[Side, ...]] = ("impostor", "crew")

# Restated literals mirroring the harness / map_elites artifact layout (whose
# filename constants are private), so a member subdir looks EXACTLY like a
# champion artifact: a float-hex ``weights.json`` + its sidecar.
_WEIGHTS_FILENAME: Final[str] = "weights.json"
_INDEX_FILENAME: Final[str] = "hall_of_fame.json"

# A 64-lowercase-hex sha256 digest — the member identity + on-disk dir name.
_SHA256_HEX_RE: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{64}")

#: The value the ``trained_against`` provenance field carries for any member
#: bred against the FIXED scripted FSM rather than a frozen opposing-side
#: artifact: every MAP-Elites founder, and any generation-0 champion the driver
#: bred vs the FSM. A reserved label, deliberately NOT a sha256 (visibly not
#: 64-hex), so a reader never confuses it with a real member digest and "unknown
#: provenance" is not representable (AGENTS.md: no silent fallbacks).
TRAINED_AGAINST_FSM: Final[str] = "scripted-fsm"

#: Provenance ``origin`` for a MAP-Elites-ingested founder.
MAP_ELITES_FOUNDER_ORIGIN: Final[str] = "map-elites-founder"

#: PFSP-lite exploration mass added to every member's normalized hardness before
#: probability normalization, so the single easiest member keeps nonzero draw
#: mass (the AlphaStar "still face everyone sometimes" anti-forgetting property,
#: sized for a ``<=30`` pool). The one weighting knob; pass 0.0 for strict
#: PFSP-hard.
DEFAULT_EXPLORATION_FLOOR: Final[float] = 0.05

#: The contract-named campaign artifact root 18.21 passes as ``root`` (a hall's
#: on-disk tree lives at ``<root>/<side>/``). Tests pass a ``tmp_path`` instead.
DEFAULT_COEVO_ARTIFACT_ROOT: Final[Path] = Path("training/artifacts/coevo")


def _sha256_hex(data: bytes) -> str:
    # Restated one-liner mirroring the private ``harness._sha256_hex`` /
    # ``map_elites._sha256_hex``: restating the trivial digest helper is the
    # lesser coupling versus importing a private symbol across the seam.
    return hashlib.sha256(data).hexdigest()


def _is_sha256_hex(value: object) -> TypeGuard[str]:
    """True iff ``value`` is exactly 64 lowercase hex chars (a sha256 digest)."""

    return isinstance(value, str) and _SHA256_HEX_RE.fullmatch(value) is not None


def _is_valid_trained_against(value: object) -> bool:
    """True iff ``value`` is a 64-hex sha OR exactly :data:`TRAINED_AGAINST_FSM`.

    The provenance invariant: ``trained_against`` names either the opposing-side
    artifact a champion was bred against (a member sha) or the reserved
    scripted-FSM sentinel — never an arbitrary string, never ``None``.
    """

    return value == TRAINED_AGAINST_FSM or _is_sha256_hex(value)


# --------------------------------------------------------------------------- #
# The provenance record (crosses into 18.21 -> pydantic per AGENTS.md).        #
# --------------------------------------------------------------------------- #


class HallOfFameMember(BaseModel):
    """One frozen opponent's provenance + on-disk locator (a ``hall_of_fame.json`` row).

    Carries identity + provenance only — NOT the genome floats (those live on
    disk under ``path``/``weights.json``, reloaded on demand via
    :meth:`HallOfFame.load_member_genome`, the harness lazy-reload posture).
    ``weights_sha256`` is the member's stable identity: the staleness ledger keys
    on it, :func:`sample_opponents`' payoff map is keyed by it, and it names the
    member's on-disk directory. ``descriptors`` / ``cell_key`` are populated only
    for MAP-Elites founders (their behavioral coordinate), ``None`` otherwise.
    ``trained_against`` is a required non-empty string — a 64-hex opposing-side
    sha OR :data:`TRAINED_AGAINST_FSM` — validated by the store, so "unknown" is
    unrepresentable.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    weights_sha256: str = Field(min_length=64, max_length=64)
    generation: int = Field(ge=0)
    origin: str = Field(min_length=1)
    trained_against: str = Field(min_length=1)
    descriptors: Mapping[str, float] | None = None
    cell_key: tuple[int, int, int] | None = None
    path: str = Field(min_length=1)


# --------------------------------------------------------------------------- #
# The store.                                                                   #
# --------------------------------------------------------------------------- #


class HallOfFame:
    """A per-side (``impostor`` | ``crew``) ``hall_of_fame.json``-indexed frozen genome store.

    On-disk root is ``<root>/<side>/``. Members freeze under
    ``gen-<N>/<weights_sha256>/`` with the EXACT committed byte conventions
    (float-hex ``weights.json`` + ``<digest>  weights.json`` sidecar). The index
    carries the campaign substrate sha and every member's provenance. Every
    mutation rewrites the index (sorted by sha, ``sort_keys`` JSON, trailing
    newline), so the tree is always a pure function of the members. Two instances
    per campaign — one per side. ``create`` / ``load`` are the disk entry points;
    the constructor is low-level.
    """

    def __init__(
        self,
        *,
        side: Side,
        side_dir: Path,
        substrate_sha256: str,
        members: tuple[HallOfFameMember, ...],
    ) -> None:
        self._side = side
        self._side_dir = side_dir
        self._substrate_sha256 = substrate_sha256
        # The canonical order everywhere: sorted by the member identity sha, so
        # the index bytes and every drift check are insertion-order-independent.
        self._members = tuple(sorted(members, key=lambda member: member.weights_sha256))

    # -- read-only surface -------------------------------------------------- #

    @property
    def side(self) -> Side:
        return self._side

    @property
    def side_dir(self) -> Path:
        return self._side_dir

    @property
    def substrate_sha256(self) -> str:
        return self._substrate_sha256

    @property
    def members(self) -> tuple[HallOfFameMember, ...]:
        """Every frozen member, sorted by ``weights_sha256``."""

        return self._members

    @property
    def member_shas(self) -> tuple[str, ...]:
        """Every member's sha, sorted — seeds the ledger + the sampler population."""

        return tuple(member.weights_sha256 for member in self._members)

    # -- disk entry points -------------------------------------------------- #

    @classmethod
    def create(cls, root: Path, side: Side, *, substrate_sha256: str) -> HallOfFame:
        """Initialise a FRESH empty pool at the given campaign substrate.

        Writes the (empty) index and returns the store. Validates ``side`` and
        that ``substrate_sha256`` is exactly 64 lowercase hex chars (fail loud
        early, Task 18.20 amendment A1). Refuses loudly
        (:class:`FileExistsError`) if ``<root>/<side>/hall_of_fame.json`` already
        exists — a ``create`` never clobbers a committed pool.
        """

        if side not in _SIDES:
            raise ValueError(f"side must be one of {_SIDES!r}; got {side!r}")
        if not _is_sha256_hex(substrate_sha256):
            raise ValueError(
                f"substrate_sha256 must be exactly 64 lowercase hex chars; got "
                f"{substrate_sha256!r}"
            )
        side_dir = root / side
        index_path = side_dir / _INDEX_FILENAME
        if index_path.exists():
            raise FileExistsError(
                f"a hall of fame already exists at {index_path}; create never "
                "clobbers a committed pool (load it instead)"
            )
        side_dir.mkdir(parents=True, exist_ok=True)
        hall = cls(
            side=side,
            side_dir=side_dir,
            substrate_sha256=substrate_sha256,
            members=(),
        )
        hall._write_index()
        return hall

    @classmethod
    def load(cls, root: Path, side: Side) -> HallOfFame:
        """Reload + fully verify the pool (EAGER two-pass, the ``load_archive_cell_genomes`` posture).

        A missing ``hall_of_fame.json`` raises :class:`FileNotFoundError`
        naturally (the ``load_candidate_weights`` posture); every integrity
        violation fails loud with :class:`ValueError`.

        Pass 1 validates each row (shape, ``trained_against`` is sha-or-sentinel,
        ``path`` == ``gen-<generation>/<weights_sha256>``, no duplicate sha),
        collects the declared path set, and cross-checks it against the on-disk
        ``gen-*/*`` member-dir set — a stray OR a missing dir is loud drift, not a
        bare :class:`FileNotFoundError` in the read loop. Pass 2 re-hashes each
        member's ``weights.json`` and double-checks the digest against BOTH the
        sidecar first token AND the index row.
        """

        if side not in _SIDES:
            raise ValueError(f"side must be one of {_SIDES!r}; got {side!r}")
        side_dir = root / side
        index_path = side_dir / _INDEX_FILENAME
        index: Any = json.loads(index_path.read_text())

        if not isinstance(index, dict):
            raise ValueError(f"hall of fame index at {index_path} is not an object")
        recorded_side = index.get("side")
        if recorded_side != side:
            raise ValueError(
                f"hall of fame index at {index_path} records side "
                f"{recorded_side!r} but was loaded as side {side!r}"
            )
        substrate_sha256 = index.get("substrate_sha256")
        if not _is_sha256_hex(substrate_sha256):
            raise ValueError(
                f"hall of fame index at {index_path} has a malformed "
                f"substrate_sha256 {substrate_sha256!r} (expected 64 lowercase hex)"
            )
        raw_members = index.get("members")
        if not isinstance(raw_members, list):
            raise ValueError(
                f"hall of fame index at {index_path} has a malformed members list"
            )

        # Pass 1: validate rows, self-check path, collect the declared path set.
        members: list[HallOfFameMember] = []
        declared_paths: set[str] = set()
        seen_shas: set[str] = set()
        for row in raw_members:
            if not isinstance(row, dict):
                raise ValueError(
                    f"hall of fame index at {index_path} has a malformed member "
                    f"row {row!r} (expected an object)"
                )
            # Building the model runs pydantic's fail-loud validation (types,
            # min/max length, extra="forbid"); ValidationError is a ValueError.
            member = HallOfFameMember(**row)
            if not _is_valid_trained_against(member.trained_against):
                raise ValueError(
                    f"member {member.weights_sha256} has trained_against "
                    f"{member.trained_against!r} which is neither a 64-hex sha "
                    f"nor {TRAINED_AGAINST_FSM!r}"
                )
            expected_path = f"gen-{member.generation}/{member.weights_sha256}"
            if member.path != expected_path:
                raise ValueError(
                    f"member {member.weights_sha256} records path {member.path!r} "
                    f"but its generation/sha imply {expected_path!r}"
                )
            if member.weights_sha256 in seen_shas:
                raise ValueError(
                    f"hall of fame index at {index_path} has a duplicate "
                    f"weights_sha256 {member.weights_sha256}"
                )
            seen_shas.add(member.weights_sha256)
            members.append(member)
            declared_paths.add(member.path)

        on_disk = {
            f"{gen_dir.name}/{child.name}"
            for gen_dir in side_dir.iterdir()
            if gen_dir.is_dir() and gen_dir.name.startswith("gen-")
            for child in gen_dir.iterdir()
            if child.is_dir()
        }
        if on_disk != declared_paths:
            raise ValueError(
                f"on-disk member dirs {sorted(on_disk)} do not match the index's "
                f"member paths {sorted(declared_paths)} at {side_dir}"
            )

        # Pass 2: read + double-verify every member's genome digest.
        for member in members:
            cls._verify_member_bytes(side_dir, member)

        return cls(
            side=side,
            side_dir=side_dir,
            substrate_sha256=substrate_sha256,
            members=tuple(members),
        )

    # -- mutation ----------------------------------------------------------- #

    def add_member(
        self,
        genome: Sequence[float],
        *,
        generation: int,
        origin: str,
        trained_against: str,
        descriptors: Mapping[str, float] | None = None,
        cell_key: tuple[int, int, int] | None = None,
    ) -> HallOfFameMember:
        """Freeze one genome under ``gen-<generation>/<sha>/`` + append its row; rewrite the index.

        Returns the created member. Fails loud (:class:`ValueError`) on: an empty
        genome; a ``trained_against`` that is neither 64-hex nor exactly
        :data:`TRAINED_AGAINST_FSM`; a duplicate ``weights_sha256`` already in the
        pool (the sha is the member identity — never silently coalesce); a target
        member dir that already exists on disk (drift/collision guard, amendment
        A5). A negative ``generation`` is caught by the model.
        """

        if not genome:
            raise ValueError("cannot freeze an empty genome as a hall of fame member")
        if not _is_valid_trained_against(trained_against):
            raise ValueError(
                f"trained_against {trained_against!r} is neither a 64-hex sha nor "
                f"{TRAINED_AGAINST_FSM!r}"
            )

        weights_json = weights_to_hex_json(tuple(genome)) + "\n"
        digest = _sha256_hex(weights_json.encode("utf-8"))
        if digest in self.member_shas:
            raise ValueError(
                f"weights_sha256 {digest} is already a member of the "
                f"{self._side} hall of fame; the sha is the member identity and "
                "is never silently overwritten"
            )
        path = f"gen-{generation}/{digest}"
        member_dir = self._side_dir / path
        if member_dir.exists():
            raise ValueError(
                f"member dir {member_dir} already exists on disk but is not in the "
                "index — refusing to overwrite (on-disk drift)"
            )

        # Build the record BEFORE any file I/O so pydantic validation (origin
        # non-empty, generation >= 0, cell_key shape) cannot leave a partial write.
        member = HallOfFameMember(
            weights_sha256=digest,
            generation=generation,
            origin=origin,
            trained_against=trained_against,
            descriptors=descriptors,
            cell_key=cell_key,
            path=path,
        )

        member_dir.mkdir(parents=True)
        (member_dir / _WEIGHTS_FILENAME).write_text(weights_json)
        (member_dir / f"{_WEIGHTS_FILENAME}.sha256").write_text(
            f"{digest}  {_WEIGHTS_FILENAME}\n"
        )

        self._members = tuple(
            sorted(
                (*self._members, member),
                key=lambda existing: existing.weights_sha256,
            )
        )
        self._write_index()
        return member

    def load_member_genome(self, weights_sha256: str) -> tuple[float, ...]:
        """Reload one member's genome bit-exactly, cross-checking the digest.

        Verifies the re-hash against BOTH the sidecar first token AND the index
        row (the ``load_candidate_weights`` drift posture — the driver's lazy
        per-opponent reload). :class:`KeyError` if the sha is not a member;
        :class:`ValueError` on any drift.
        """

        member = self._member_by_sha(weights_sha256)
        return self._verify_member_bytes(self._side_dir, member)

    def ingest_map_elites_founders(
        self, cell_artifact_dir: Path, *, generation: int = 0
    ) -> tuple[HallOfFameMember, ...]:
        """Ingest 18.6 MAP-Elites cells as behaviorally-diverse founders.

        The stale-seed fence lives HERE: cells load via
        ``load_archive_cell_genomes(cell_artifact_dir,
        expected_substrate_sha=self.substrate_sha256)`` — a substrate mismatch
        refuses ingestion loudly (:class:`ValueError` matching ``adopted
        substrate``) BEFORE any member is written or sampled. Each cell is frozen
        (in sorted cell-key order — the deterministic ingestion order, amendment
        A2) with ``origin`` :data:`MAP_ELITES_FOUNDER_ORIGIN`, ``trained_against``
        :data:`TRAINED_AGAINST_FSM` (honest provenance: cells were bred/scored vs
        the fixed FSM, never a hall member), and the cell's ``descriptors`` +
        ``cell_key`` copied verbatim (the behavioral-diversity provenance). A cell
        whose genome duplicates an already-frozen member fails loud via
        :meth:`add_member` (never a silently dropped founder). Re-freezing writes
        the SAME float-hex bytes, so each founder's ``weights.json`` and digest
        equal the source cell's.

        Returns the newly-frozen members in sorted cell-key order (the
        :attr:`members` property stays sha-sorted).
        """

        archive = load_archive_cell_genomes(
            cell_artifact_dir, expected_substrate_sha=self._substrate_sha256
        )
        founders: list[HallOfFameMember] = []
        for cell_key in sorted(archive):
            cell: ArchiveCell = archive[cell_key]
            founders.append(
                self.add_member(
                    cell.genome,
                    generation=generation,
                    origin=MAP_ELITES_FOUNDER_ORIGIN,
                    trained_against=TRAINED_AGAINST_FSM,
                    descriptors=cell.descriptors,
                    cell_key=cell_key,
                )
            )
        return tuple(founders)

    # -- internals ---------------------------------------------------------- #

    @property
    def _index_path(self) -> Path:
        return self._side_dir / _INDEX_FILENAME

    def _member_by_sha(self, weights_sha256: str) -> HallOfFameMember:
        for member in self._members:
            if member.weights_sha256 == weights_sha256:
                return member
        raise KeyError(
            f"{weights_sha256} is not a member of the {self._side} hall of fame"
        )

    @staticmethod
    def _verify_member_bytes(
        side_dir: Path, member: HallOfFameMember
    ) -> tuple[float, ...]:
        """Re-hash a member's ``weights.json`` and double-check the digest.

        Cross-checks against the sidecar first token (``hashes to``) AND the
        index-recorded sha (``index records``) — the load_candidate_weights drift
        posture applied per member.
        """

        weights_path = side_dir / member.path / _WEIGHTS_FILENAME
        raw = weights_path.read_text()
        actual = _sha256_hex(raw.encode("utf-8"))
        sidecar = (
            (side_dir / member.path / f"{_WEIGHTS_FILENAME}.sha256")
            .read_text()
            .split()[0]
        )
        if actual != sidecar:
            raise ValueError(
                f"{weights_path} hashes to {actual} but the sidecar records {sidecar}"
            )
        if actual != member.weights_sha256:
            raise ValueError(
                f"{weights_path} hashes to {actual} but the index records "
                f"{member.weights_sha256}"
            )
        return weights_from_hex_json(raw)

    def _write_index(self) -> None:
        """Rewrite ``hall_of_fame.json`` as a pure function of the members.

        The ``members`` list is sorted by sha; ``json.dumps(..., indent=2,
        sort_keys=True) + "\\n"`` (the map_elites index convention) sorts the
        top-level keys AND every descriptor mapping's keys, so the bytes are
        deterministic and every row carries the same key set (absent optionals
        serialise ``null``).
        """

        index = {
            "members": [member.model_dump(mode="json") for member in self._members],
            "side": self._side,
            "substrate_sha256": self._substrate_sha256,
        }
        self._index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")


# --------------------------------------------------------------------------- #
# The PFSP-lite sampler (a pure free function).                               #
# --------------------------------------------------------------------------- #


def sample_opponents(
    members: Sequence[HallOfFameMember],
    payoffs: Mapping[str, float],
    *,
    slate_size: int,
    seed: int,
    exploration_floor: float = DEFAULT_EXPLORATION_FLOOR,
) -> tuple[HallOfFameMember, ...]:
    """Deterministic PFSP-lite opponent sampler, a PURE function of its inputs.

    ``payoffs`` is keyed by ``weights_sha256`` -> the MOVING side's exact
    deterministic fitness against that member THIS generation (LOWER fitness =>
    harder => more weight). No hidden state; re-normalized each call. Returns a
    length-``slate_size`` slate drawn WITH replacement.

    The weighting function (kept small + documented — the contract; a linear
    PFSP-lite with ONE knob, deliberately resisting the meta-Nash rabbit hole,
    sized for a ``<=30``-member pool)::

        0. sort members by weights_sha256 -> m_1..m_n           (order-free determinism)
        1. n == 0            -> ValueError   (cannot sample an empty hall)
           slate_size < 1    -> ValueError
           exploration_floor < 0 -> ValueError
        2. payoffs == {}                                        # COLD START (gen 1)
               weights = [1.0] * n                              # DEFINED uniform
           else:
               {m.weights_sha256} must == set(payoffs)          # exact cover, else ValueError
               f  = [payoffs[m_i.weights_sha256]]
               lo, hi = min(f), max(f)
               if hi == lo:                                      # no hardness gradient
                   weights = [1.0] * n                           # DEFINED uniform
               else:
                   weights = [(1 - (f_i - lo)/(hi - lo)) + exploration_floor]
        3. slate = random.Random(seed).choices(m_1..m_n, weights=weights, k=slate_size)

    Hardness is min-max-normalized easiness ``(f - lo)/(hi - lo)``, hardness
    ``= 1 - easiness``, so the hardest member (lowest fitness) gets the largest
    weight; min-max makes the weighting SCALE-FREE (an impostor range ``[-3, 5]``
    and a crew range ``[0, 1]`` concentrate identically). ``exploration_floor``
    (the AlphaStar anti-forgetting mass) keeps every member reachable — the
    easiest member's weight is exactly ``exploration_floor``; ``0.0`` recovers
    strict PFSP-hard (easiest -> weight 0 -> never drawn) and is safe because the
    two uniform branches guarantee a positive weight-sum. A non-empty ``payoffs``
    that does not EXACTLY cover the member set raises (no hidden default fitness);
    ``payoffs == {}`` is the unambiguous cold-start "no data" signal.
    """

    ordered = sorted(members, key=lambda member: member.weights_sha256)
    n = len(ordered)
    if n == 0:
        raise ValueError("cannot sample opponents from an empty hall of fame")
    if slate_size < 1:
        raise ValueError(f"slate_size must be >= 1; got {slate_size}")
    if exploration_floor < 0.0:
        raise ValueError(f"exploration_floor must be >= 0; got {exploration_floor}")

    weights: list[float]
    if not payoffs:
        weights = [1.0] * n
    else:
        member_shas = {member.weights_sha256 for member in ordered}
        payoff_shas = set(payoffs)
        if member_shas != payoff_shas:
            raise ValueError(
                "sample_opponents payoffs must exactly cover the member set; "
                f"missing {sorted(member_shas - payoff_shas)}, "
                f"extra {sorted(payoff_shas - member_shas)}"
            )
        fitnesses = [payoffs[member.weights_sha256] for member in ordered]
        lo = min(fitnesses)
        hi = max(fitnesses)
        if hi == lo:
            weights = [1.0] * n
        else:
            span = hi - lo
            weights = [
                (1.0 - (fitness - lo) / span) + exploration_floor
                for fitness in fitnesses
            ]

    slate = random.Random(seed).choices(ordered, weights=weights, k=slate_size)
    return tuple(slate)


# --------------------------------------------------------------------------- #
# Staleness (mirrors SurrogateUseCounter / SurrogateStalenessCap).             #
# --------------------------------------------------------------------------- #


class OpponentStalenessExceededError(RuntimeError):
    """A frozen opponent reached its committed staleness cap and must be refreshed.

    Deliberately NOT silently recoverable (mirrors
    :class:`training.surrogate.runner.SurrogateStalenessExceededError`): the 18.21
    driver must retire/replace the stale opponent — freeze the current champion as
    a fresh member (a fresh sha) and :meth:`OpponentStalenessLedger.register` it —
    never keep serving the capped one.
    """


class OpponentStalenessCap(BaseModel):
    """The committed cap: how many GENERATIONS one frozen member may serve as a live opponent.

    Frozen pydantic (crosses into 18.21), mirroring
    :class:`training.surrogate.ballots.SurrogateStalenessCap` MINUS its single
    ``weights_sha256`` — a hall meters MANY members against one shared limit, so
    the per-member key lives in the ledger's dict (documented divergence).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    max_generations: int = Field(gt=0)
    unit: Literal["generations"]


class OpponentStalenessLedger:
    """The cumulative per-member generation-use counter for one campaign run.

    An explicit object (never module state — AGENTS.md): the 18.21 DRIVER
    constructs it ONCE from the cap + the pool's current member shas and threads
    it across the alternating-freeze loop, exactly as the bake-off threads one
    :class:`training.surrogate.runner.SurrogateUseCounter`. In-memory only —
    counts are NEVER persisted into ``hall_of_fame.json``. Keys every use on
    ``weights_sha256`` so it can never silently meter a sha it was not seeded with
    (the SurrogateUseCounter "one counter never meters two artifacts" guard,
    generalized to the current pool). Differs from ``SurrogateUseCounter`` by
    holding a ``dict[str, int]`` (many members) rather than one scalar.
    """

    def __init__(self, cap: OpponentStalenessCap, member_shas: Sequence[str]) -> None:
        self._cap = cap
        self._uses: dict[str, int] = {sha: 0 for sha in member_shas}

    @property
    def cap(self) -> OpponentStalenessCap:
        return self._cap

    def uses(self, *, weights_sha256: str) -> int:
        """Generations this member has served so far.

        :class:`ValueError` on a sha the ledger was not seeded with.
        """

        if weights_sha256 not in self._uses:
            raise ValueError(
                f"OpponentStalenessLedger was not seeded with {weights_sha256!r}; "
                "register it before metering (the phantom-opponent guard)"
            )
        return self._uses[weights_sha256]

    def register(self, *, weights_sha256: str) -> None:
        """Admit a newly-frozen member (a champion added mid-campaign) at count 0.

        :class:`ValueError` if already tracked. This is how the loop meters
        champions it freezes each generation — and the mechanism of 'refresh': a
        capped member is retired and replaced by a fresh champion (a fresh sha)
        registered here, never an in-place counter reset.
        """

        if weights_sha256 in self._uses:
            raise ValueError(
                f"{weights_sha256!r} is already tracked by this "
                "OpponentStalenessLedger; register admits each member once"
            )
        self._uses[weights_sha256] = 0

    def record_generation_use(self, *, weights_sha256: str) -> int:
        """Record ONE generation of service for a member; return the new count.

        :class:`ValueError` on a sha the ledger was not seeded with (the
        phantom-opponent guard); :class:`OpponentStalenessExceededError` once the
        member is already at ``cap.max_generations``.
        """

        if weights_sha256 not in self._uses:
            raise ValueError(
                f"OpponentStalenessLedger was not seeded with {weights_sha256!r}; "
                "register it before metering (the phantom-opponent guard)"
            )
        if self._uses[weights_sha256] >= self._cap.max_generations:
            raise OpponentStalenessExceededError(
                f"the frozen opponent {weights_sha256[:12]}… has reached its "
                f"committed staleness cap of {self._cap.max_generations} "
                "generations for this run; retire it and freeze the current "
                "champion as a fresh member (a fresh sha) before serving further"
            )
        self._uses[weights_sha256] += 1
        return self._uses[weights_sha256]


__all__ = [
    "DEFAULT_COEVO_ARTIFACT_ROOT",
    "DEFAULT_EXPLORATION_FLOOR",
    "MAP_ELITES_FOUNDER_ORIGIN",
    "TRAINED_AGAINST_FSM",
    "HallOfFame",
    "HallOfFameMember",
    "OpponentStalenessCap",
    "OpponentStalenessExceededError",
    "OpponentStalenessLedger",
    "Side",
    "sample_opponents",
]
