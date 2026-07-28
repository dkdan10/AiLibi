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
  A hall constructed WITH :class:`LoadableArtifactMetadata` freezes the full
  FOUR-file loadable artifact instead (Task 18.31 —
  :func:`write_loadable_artifact`: the two byte-identical weight files plus a
  five-field ``stamp.json`` and a provenance ``config.json``), so every frozen
  member loads through ``scripts/run_tournament.py``'s
  ``_load_candidate_policy`` without a hand-stamping pass. ``encoder_version``
  and ``hidden`` come from that metadata — declared per family by the campaign
  configuration, NEVER re-derived from genome length (the 18.24 campaign report
  §12 Errata item 1 is what a length-guessed stamp costs: two 1442-gene v3
  intermediates stamped as the 19-gene utility family, unloadable until
  review caught them).

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
import math
import random
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final, Literal, TypeGuard

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

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
# champion artifact: a float-hex ``weights.json`` + its sidecar. ``stamp.json``
# / ``config.json`` complete the FOUR-file loadable artifact
# ``scripts/run_tournament.py:492-493`` reads (its own constants are private
# there too — the same restated-literal idiom).
_WEIGHTS_FILENAME: Final[str] = "weights.json"
_INDEX_FILENAME: Final[str] = "hall_of_fame.json"
_STAMP_FILENAME: Final[str] = "stamp.json"
_CONFIG_FILENAME: Final[str] = "config.json"

#: The stamp label for a policy anchored on the scripted FSM proposal itself
#: (the ``TacticalPolicyStamp.anchor_policy`` default every committed impostor
#: artifact carries). The 18.5 filtered-BC seam names its artifact instead.
DEFAULT_ANCHOR_POLICY: Final[str] = "fsm-default"

#: The five ``TacticalPolicyStamp`` fields a loadable ``stamp.json`` carries —
#: the exact set ``scripts/run_tournament.py`` ``_read_candidate_stamp``
#: requires, restated here so a reload can verify the WHOLE stamp.
_STAMP_FIELDS: Final[tuple[str, ...]] = (
    "anchor_policy",
    "encoder_version",
    "method",
    "policy_id",
    "weights_sha256",
)

#: Keys :func:`write_loadable_artifact` OWNS in ``config.json`` — derived from
#: the genome + the declared family, never accepted from a caller's provenance
#: mapping (a caller-supplied duplicate is a fail-loud contradiction, not a
#: silent override).
_WRITER_OWNED_CONFIG_KEYS: Final[tuple[str, ...]] = (
    "encoder_version",
    "genome_length",
    "hidden",
)

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


def _validate_stamp_token(name: str, value: str) -> None:
    """Fail loud on a stamp string the committed stamp reader would reject.

    Restates the :class:`~orchestrator.replay.TacticalPolicyStamp` field rules
    (non-blank, no ``|`` / newline / CR — replay.py:211-254) rather than
    importing them: this module stays pure stdlib + pydantic (no ``engine`` /
    ``orchestrator`` graph), the same restated-literal idiom the filename
    constants above use. ``training.realpath.RealPathCandidate`` restates the
    identical rule set for the same reason.
    """

    if not value.strip():
        raise ValueError(f"{name} must be a non-blank stamp token; got {value!r}")
    for forbidden, human in (("|", "pipe"), ("\n", "newline"), ("\r", "CR")):
        if forbidden in value:
            raise ValueError(
                f"{name} must be MANIFEST-safe (no {human}); got {value!r}"
            )


# --------------------------------------------------------------------------- #
# The loadable four-file artifact (Task 18.31).                                #
# --------------------------------------------------------------------------- #


def write_loadable_artifact(
    artifact_dir: Path,
    genome: Sequence[float],
    *,
    policy_id: str,
    method: str,
    encoder_version: str,
    anchor_policy: str = DEFAULT_ANCHOR_POLICY,
    hidden: int | None = None,
    config: Mapping[str, object] | None = None,
) -> str:
    """Freeze one genome as the FOUR-file artifact its consumer can load (18.31).

    The four files, in the exact committed byte conventions:

    * ``weights.json`` — the float-hex genome
      (:func:`agents.tactical.features.weights_to_hex_json` + a trailing
      newline), byte-identical to
      :func:`training.bakeoff.harness.write_candidate_artifact`;
    * ``weights.json.sha256`` — the ``<digest>  weights.json`` sidecar;
    * ``stamp.json`` — EXACTLY the five
      :class:`~orchestrator.replay.TacticalPolicyStamp` fields
      (``policy_id`` / ``method`` / ``encoder_version`` / ``weights_sha256`` /
      ``anchor_policy``), with ``weights_sha256`` computed from the bytes just
      written, so the 17.14 conflation guard
      (``scripts/run_tournament.py:620-631``: stamp sha == sidecar digest)
      holds by construction;
    * ``config.json`` — the provenance mapping plus the writer-owned
      ``encoder_version`` / ``genome_length`` / ``hidden``. ``hidden`` is what
      ``_read_candidate_hidden`` needs to rebuild a masked-MLP family.

    ``encoder_version`` and ``hidden`` are DECLARED by the caller (the campaign
    side config), never re-derived from ``len(genome)``: length collisions
    between future families are exactly the ambiguity a stamp exists to remove,
    and the 18.24 report's §12 Errata item 1 is the cost of guessing wrong
    (two 1442-gene v3 genomes stamped ``impostor-option-features-v1``, refused
    by the loader's genome-length check until repaired).

    Fails loud on: an empty genome; a stamp token that is blank or
    MANIFEST-unsafe; ``hidden < 1`` when declared; a ``config`` mapping that
    carries any writer-owned key; and any pre-existing CONTENT in
    ``artifact_dir`` — not merely a collision with one of the four filenames.
    An artifact directory holding a stray or stale file would otherwise be
    silently adopted and freeze as a five-or-more-file bundle (Codex review on
    PR #314); the no-clobber discipline is that an artifact dir is written once,
    whole, never patched in place. Returns the ``weights_sha256`` digest.
    """

    if not genome:
        raise ValueError("cannot freeze an empty genome as a loadable artifact")
    for name, token in (
        ("policy_id", policy_id),
        ("method", method),
        ("encoder_version", encoder_version),
        ("anchor_policy", anchor_policy),
    ):
        _validate_stamp_token(name, token)
    if hidden is not None and hidden < 1:
        raise ValueError(f"hidden must be >= 1 when declared; got {hidden!r}")
    provenance = dict(config) if config is not None else {}
    clashing = sorted(key for key in _WRITER_OWNED_CONFIG_KEYS if key in provenance)
    if clashing:
        raise ValueError(
            f"config.json keys {clashing} are owned by write_loadable_artifact "
            "(derived from the genome bytes + the declared family); pass them as "
            "the encoder_version / hidden arguments instead of a provenance entry"
        )

    weights_json = weights_to_hex_json(tuple(genome)) + "\n"
    digest = _sha256_hex(weights_json.encode("utf-8"))
    provenance["encoder_version"] = encoder_version
    provenance["genome_length"] = len(genome)
    if hidden is not None:
        provenance["hidden"] = hidden
    stamp = {
        "anchor_policy": anchor_policy,
        "encoder_version": encoder_version,
        "method": method,
        "policy_id": policy_id,
        "weights_sha256": digest,
    }

    if artifact_dir.exists():
        existing = sorted(child.name for child in artifact_dir.iterdir())
        if existing:
            raise FileExistsError(
                f"refusing to freeze into non-empty artifact dir {artifact_dir} "
                f"(holds {existing}); a loadable artifact is written once and "
                "whole, never merged into whatever is already there"
            )
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for filename, payload in (
        (_WEIGHTS_FILENAME, weights_json),
        (f"{_WEIGHTS_FILENAME}.sha256", f"{digest}  {_WEIGHTS_FILENAME}\n"),
        (_STAMP_FILENAME, json.dumps(stamp, indent=2, sort_keys=True) + "\n"),
        (_CONFIG_FILENAME, json.dumps(provenance, indent=2, sort_keys=True) + "\n"),
    ):
        with (artifact_dir / filename).open("x", encoding="utf-8") as handle:
            handle.write(payload)
    return digest


class LoadableArtifactMetadata(BaseModel):
    """The per-hall stamp-grade metadata every freeze writes (18.31; frozen).

    A hall is single-side AND single-family per campaign, so the stamp fields a
    frozen member needs are campaign constants, not per-``add_member``
    arguments: the store carries them once and
    :meth:`HallOfFame.add_member` composes each member's ``policy_id`` +
    provenance from them. ``encoder_version`` / ``hidden`` are DECLARED here
    (from the campaign side config), never re-derived from genome length.

    ``run_label`` is the stamp-grade run name (e.g.
    ``"run-01-utility-champion"``) that rides ``policy_id``, ``campaign``,
    ``entrant`` and ``source_lineage`` — the provenance the 18.24 record had to
    be hand-stamped with after the fact. ``anchor_weight`` is optional campaign
    provenance (``None`` omits the key rather than recording a zero-ghost).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    run_label: str
    method: str
    encoder_version: str
    anchor_policy: str = DEFAULT_ANCHOR_POLICY
    hidden: int | None = None
    anchor_weight: float | None = None
    policy_id_prefix: str = "coevo"

    @model_validator(mode="after")
    def _validate(self) -> LoadableArtifactMetadata:
        for name, token in (
            ("run_label", self.run_label),
            ("method", self.method),
            ("encoder_version", self.encoder_version),
            ("anchor_policy", self.anchor_policy),
            ("policy_id_prefix", self.policy_id_prefix),
        ):
            _validate_stamp_token(name, token)
        if self.hidden is not None and self.hidden < 1:
            raise ValueError(f"hidden must be >= 1 when declared; got {self.hidden!r}")
        if self.anchor_weight is not None and not math.isfinite(self.anchor_weight):
            raise ValueError(
                f"anchor_weight must be finite when declared; got {self.anchor_weight!r}"
            )
        return self

    def policy_id_for(self, *, origin: str, generation: int) -> str:
        """The member's ``stamp.json`` ``policy_id`` (the committed 18.24 shape).

        ``<prefix>-<run_label>-<origin>-gen<generation>`` — e.g.
        ``coevo-run-03-utility-bcanchor-exploiter-probe-gen10``, exactly the
        shape the campaign's frozen members carry.
        """

        return f"{self.policy_id_prefix}-{self.run_label}-{origin}-gen{generation}"

    def provenance(
        self,
        *,
        side: Side,
        generation: int,
        origin: str,
        trained_against: str,
        path: str,
    ) -> dict[str, object]:
        """The member's ``config.json`` provenance (writer-owned keys excluded)."""

        provenance: dict[str, object] = {
            "campaign": self.run_label,
            "entrant": f"{self.run_label}/{side}/{path}",
            "generation": generation,
            "hall_origin": origin,
            "side": side,
            "source_lineage": self.run_label,
            "trained_against": trained_against,
        }
        if self.anchor_weight is not None:
            provenance["anchor_weight"] = self.anchor_weight
        return provenance


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
    unrepresentable. ``descriptors`` is stored as a read-only mapping proxy over
    a private copy: ``frozen=True`` alone would leave the underlying dict
    mutable through the attribute, and the store re-serialises retained members
    into ``hall_of_fame.json`` on every ``add_member``, so a caller-side
    mutation would otherwise silently alter persisted provenance.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    weights_sha256: str = Field(min_length=64, max_length=64)
    generation: int = Field(ge=0)
    origin: str = Field(min_length=1)
    trained_against: str = Field(min_length=1)
    descriptors: Mapping[str, float] | None = None
    cell_key: tuple[int, int, int] | None = None
    path: str = Field(min_length=1)

    @field_validator("descriptors", mode="after")
    @classmethod
    def _freeze_descriptors(
        cls, value: Mapping[str, float] | None
    ) -> Mapping[str, float] | None:
        # A proxy over a PRIVATE copy: immune to both in-place mutation through
        # the attribute AND later mutation of the caller's source dict.
        return None if value is None else MappingProxyType(dict(value))

    @field_serializer("descriptors")
    def _serialize_descriptors(
        self, value: Mapping[str, float] | None
    ) -> dict[str, float] | None:
        # pydantic cannot serialise a mappingproxy; hand it a plain dict.
        return None if value is None else dict(value)


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
        artifact_metadata: LoadableArtifactMetadata | None = None,
    ) -> None:
        self._side = side
        self._side_dir = side_dir
        self._substrate_sha256 = substrate_sha256
        self._artifact_metadata = artifact_metadata
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
    def artifact_metadata(self) -> LoadableArtifactMetadata | None:
        """The stamp-grade freeze metadata, or ``None`` for a weights-only pool.

        Set ⇒ every :meth:`add_member` freeze writes the FOUR-file loadable
        artifact (Task 18.31). ``None`` ⇒ the historic two-file member (weights
        + sidecar): the pool is still a valid genome store, but its members
        carry no stamp and do not load through ``_load_candidate_policy``.

        The value is PERSISTED into ``hall_of_fame.json`` and restored by
        :meth:`load`, so the two modes are a property of the POOL rather than of
        whoever happens to open it — a reloaded loadable pool cannot silently
        start freezing unstamped members.
        """

        return self._artifact_metadata

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
    def create(
        cls,
        root: Path,
        side: Side,
        *,
        substrate_sha256: str,
        artifact_metadata: LoadableArtifactMetadata | None = None,
    ) -> HallOfFame:
        """Initialise a FRESH empty pool at the given campaign substrate.

        Writes the (empty) index and returns the store. Validates ``side`` and
        that ``substrate_sha256`` is exactly 64 lowercase hex chars (fail loud
        early, Task 18.20 amendment A1). Refuses loudly
        (:class:`FileExistsError`) if ``<root>/<side>/hall_of_fame.json`` already
        exists — a ``create`` never clobbers a committed pool — and
        (:class:`ValueError`) if the side dir holds stray ``gen-*`` member
        artifacts WITHOUT an index (an interrupted or half-deleted tree):
        initialising an empty index beside them would present a dirty root as a
        fresh pool until the next ``load`` trips the drift check — papering
        over, never allowed.

        ``artifact_metadata`` (Task 18.31) makes every freeze on this pool write
        the FOUR-file loadable artifact; the 18.21 driver always supplies it
        from the campaign side config.
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
        if side_dir.exists():
            stray = sorted(
                child.name
                for child in side_dir.iterdir()
                if child.name.startswith("gen-")
            )
            if stray:
                raise ValueError(
                    f"cannot create a fresh {side} hall of fame at {side_dir}: "
                    f"stray member artifacts {stray} exist without an index — a "
                    "dirty tree is never silently adopted (clean the root or "
                    "restore its hall_of_fame.json)"
                )
        side_dir.mkdir(parents=True, exist_ok=True)
        hall = cls(
            side=side,
            side_dir=side_dir,
            substrate_sha256=substrate_sha256,
            members=(),
            artifact_metadata=artifact_metadata,
        )
        hall._write_index()
        return hall

    @classmethod
    def load(
        cls,
        root: Path,
        side: Side,
        *,
        artifact_metadata: LoadableArtifactMetadata | None = None,
    ) -> HallOfFame:
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

        ``artifact_metadata`` (Task 18.31) is RESTORED from the index when the
        pool recorded one, so a reloaded loadable pool keeps freezing loadable
        members — reloading can never silently downgrade a four-file pool to
        two-file adds (Codex review on PR #314). Passing it explicitly is
        allowed only when it AGREES with the recorded one (a disagreement is
        loud drift, never a silent override); a pool with no recorded metadata
        adopts the passed one.
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
        raw_metadata = index.get("artifact_metadata")
        resolved_metadata = artifact_metadata
        if raw_metadata is not None:
            if not isinstance(raw_metadata, dict):
                raise ValueError(
                    f"hall of fame index at {index_path} has a malformed "
                    f"artifact_metadata block {raw_metadata!r} (expected an object)"
                )
            # Building the model runs the same fail-loud validation ``create``
            # ran; a corrupted block is drift, not a reason to freeze unstamped.
            recorded = LoadableArtifactMetadata(**raw_metadata)
            if artifact_metadata is not None and artifact_metadata != recorded:
                raise ValueError(
                    f"hall of fame index at {index_path} records artifact "
                    f"metadata {recorded.model_dump(mode='json')} but was loaded "
                    f"with {artifact_metadata.model_dump(mode='json')}; the pool's "
                    "own freeze identity is never silently overridden"
                )
            resolved_metadata = recorded

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

        # Pass 2: read + double-verify every member's genome digest, and — for a
        # pool that advertises itself as LOADABLE — the stamp/config half of the
        # artifact too. Restoring the metadata without checking the files it
        # promises would hand back a hall whose members only fail at
        # ``_load_candidate_policy``, long after resume time (Codex review on
        # PR #314); the module's eager two-pass posture is that corruption
        # surfaces HERE.
        for member in members:
            cls._verify_member_bytes(side_dir, member)
            if resolved_metadata is not None:
                cls._verify_member_stamp(side_dir, member, resolved_metadata)

        return cls(
            side=side,
            side_dir=side_dir,
            substrate_sha256=substrate_sha256,
            members=tuple(members),
            artifact_metadata=resolved_metadata,
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

        With :attr:`artifact_metadata` set (Task 18.31) the member freezes as the
        FOUR-file loadable artifact through :func:`write_loadable_artifact` —
        the same weights bytes plus ``stamp.json`` / ``config.json``, so the
        member loads through ``scripts/run_tournament.py``'s
        ``_load_candidate_policy`` with no hand-stamping pass. Without it the
        historic two-file member is written unchanged.
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

        metadata = self._artifact_metadata
        if metadata is None:
            member_dir.mkdir(parents=True)
            (member_dir / _WEIGHTS_FILENAME).write_text(weights_json)
            (member_dir / f"{_WEIGHTS_FILENAME}.sha256").write_text(
                f"{digest}  {_WEIGHTS_FILENAME}\n"
            )
        else:
            written = write_loadable_artifact(
                member_dir,
                genome,
                policy_id=metadata.policy_id_for(origin=origin, generation=generation),
                method=metadata.method,
                encoder_version=metadata.encoder_version,
                anchor_policy=metadata.anchor_policy,
                hidden=metadata.hidden,
                config=metadata.provenance(
                    side=self._side,
                    generation=generation,
                    origin=origin,
                    trained_against=trained_against,
                    path=path,
                ),
            )
            if written != digest:  # pragma: no cover - both digest the same bytes
                raise ValueError(
                    f"loadable artifact digest {written} != member digest {digest} "
                    "for the same genome bytes (the two digests are the same "
                    "function of the same float-hex payload — refusing to index "
                    "a member the artifact does not name)"
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
        ``cell_key`` copied verbatim (the behavioral-diversity provenance).
        Re-freezing writes the SAME float-hex bytes, so each founder's
        ``weights.json`` and digest equal the source cell's.

        Ingestion is ALL-OR-NOTHING: every founder digest is preflighted against
        the existing members AND the batch itself BEFORE any write, so a
        duplicate genome (a cell already frozen in the hall, or two cells
        carrying the identical genome) raises :class:`ValueError` with the pool
        untouched — a failed ingest never leaves a partially-mutated hall for a
        retry to compound (:meth:`add_member`'s own guards remain the backstop).

        Returns the newly-frozen members in sorted cell-key order (the
        :attr:`members` property stays sha-sorted).
        """

        archive = load_archive_cell_genomes(
            cell_artifact_dir, expected_substrate_sha=self._substrate_sha256
        )
        # Preflight the whole batch before the first write (all-or-nothing): the
        # digest is a pure function of the genome bytes, so computing it here is
        # exactly the digest add_member will re-derive.
        existing = set(self.member_shas)
        batch: dict[str, tuple[int, int, int]] = {}
        for cell_key in sorted(archive):
            weights_json = weights_to_hex_json(tuple(archive[cell_key].genome)) + "\n"
            digest = _sha256_hex(weights_json.encode("utf-8"))
            if digest in existing:
                raise ValueError(
                    f"cell {cell_key} duplicates the already-frozen member "
                    f"{digest} in the {self._side} hall of fame; refusing the "
                    "whole ingest before any write (all-or-nothing)"
                )
            if digest in batch:
                raise ValueError(
                    f"cells {batch[digest]} and {cell_key} carry the identical "
                    f"genome ({digest}); refusing the whole ingest before any "
                    "write (all-or-nothing)"
                )
            batch[digest] = cell_key

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

    @staticmethod
    def _verify_member_stamp(
        side_dir: Path, member: HallOfFameMember, metadata: LoadableArtifactMetadata
    ) -> None:
        """Verify the stamp/config half of a LOADABLE member's artifact (18.31).

        A pool that records :class:`LoadableArtifactMetadata` promises every
        member loads through ``_load_candidate_policy``. That promise rests on
        four files, so a reload verifies four: ``stamp.json`` and
        ``config.json`` must exist and parse, the stamp's ``weights_sha256``
        must name THIS member (the 17.14 conflation guard), and its
        ``encoder_version`` must match the pool's declared family — a member
        stamped for another family is exactly the §12 Errata item-1 defect,
        caught at resume time instead of at spend time.
        """

        member_dir = side_dir / member.path
        try:
            stamp = json.loads((member_dir / _STAMP_FILENAME).read_text())
            config = json.loads((member_dir / _CONFIG_FILENAME).read_text())
        except OSError as exc:
            raise ValueError(
                f"member {member.weights_sha256} is missing part of its loadable "
                f"artifact under {member_dir} ({exc}); this pool records "
                "artifact metadata, so every member is a four-file freeze"
            ) from exc
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"member {member.weights_sha256} has a malformed loadable "
                f"artifact under {member_dir}: {exc}"
            ) from exc
        # The WHOLE five-field stamp: a member missing ``method`` (or any other
        # field) is rejected by ``_read_candidate_stamp`` downstream, so an
        # eager load that checked only the sha would still defer the corruption
        # to spend time (Codex review on PR #314).
        missing = sorted(field for field in _STAMP_FIELDS if field not in stamp)
        if missing:
            raise ValueError(
                f"{member_dir / _STAMP_FILENAME} is missing stamp fields {missing}; "
                f"a loadable freeze carries all five ({list(_STAMP_FIELDS)})"
            )
        for field in _STAMP_FIELDS:
            value = stamp[field]
            if not isinstance(value, str):
                raise ValueError(
                    f"{member_dir / _STAMP_FILENAME} field {field!r} is "
                    f"{value!r}; every stamp field is a string"
                )
            _validate_stamp_token(f"{field} in {member_dir / _STAMP_FILENAME}", value)
        if stamp["weights_sha256"] != member.weights_sha256:
            raise ValueError(
                f"{member_dir / _STAMP_FILENAME} names weights_sha256 "
                f"{stamp['weights_sha256']!r} but the index records "
                f"{member.weights_sha256} (the 17.14 conflation guard)"
            )
        for source, name in ((stamp, _STAMP_FILENAME), (config, _CONFIG_FILENAME)):
            recorded = source.get("encoder_version")
            if recorded != metadata.encoder_version:
                raise ValueError(
                    f"{member_dir / name} records encoder_version {recorded!r} but "
                    f"the pool declares {metadata.encoder_version!r}; a hall stays "
                    "single-family per campaign"
                )
        # IDENTITY, not just syntax. The pool's metadata plus the member's own
        # row reconstruct every remaining stamp field exactly, so checking only
        # that they are MANIFEST-safe strings would accept a member re-stamped
        # for another campaign, method, or anchor and let it carry that false
        # provenance into every recording it seeds — the §12 Errata item-1
        # defect wearing a syntactically valid name (Codex review on PR #314).
        for field, expected in (
            ("method", metadata.method),
            ("anchor_policy", metadata.anchor_policy),
            (
                "policy_id",
                metadata.policy_id_for(
                    origin=member.origin, generation=member.generation
                ),
            ),
        ):
            if stamp[field] != expected:
                raise ValueError(
                    f"{member_dir / _STAMP_FILENAME} records {field} "
                    f"{stamp[field]!r} but this pool's member reconstructs to "
                    f"{expected!r}; a member's stamp names the campaign that bred "
                    "it, and false provenance is never loaded"
                )
        # The family-specific reconstruction field: a masked-MLP consumer reads
        # ``hidden`` from config.json, so a missing or drifted width is exactly
        # as unloadable as a wrong encoder tag.
        recorded_hidden = config.get("hidden")
        if recorded_hidden != metadata.hidden:
            raise ValueError(
                f"{member_dir / _CONFIG_FILENAME} records hidden "
                f"{recorded_hidden!r} but the pool declares {metadata.hidden!r}; "
                "the consumer rebuilds the policy at that width"
            )

    def _write_index(self) -> None:
        """Rewrite ``hall_of_fame.json`` as a pure function of the members.

        The ``members`` list is sorted by sha; ``json.dumps(..., indent=2,
        sort_keys=True) + "\\n"`` (the map_elites index convention) sorts the
        top-level keys AND every descriptor mapping's keys, so the bytes are
        deterministic and every row carries the same key set (absent optionals
        serialise ``null``).

        ``artifact_metadata`` is persisted ONLY when the pool declares one
        (Task 18.31): a weights-only pool's index bytes are unchanged, and a
        loadable pool carries its own freeze identity so a later
        :meth:`load` cannot silently drop it and freeze a two-file member into
        a four-file pool (Codex review on PR #314).
        """

        index: dict[str, Any] = {
            "members": [member.model_dump(mode="json") for member in self._members],
            "side": self._side,
            "substrate_sha256": self._substrate_sha256,
        }
        if self._artifact_metadata is not None:
            index["artifact_metadata"] = self._artifact_metadata.model_dump(mode="json")
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
               every payoff must be finite                      # NaN/inf, else ValueError
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
    ``payoffs == {}`` is the unambiguous cold-start "no data" signal. A
    non-finite payoff (NaN/inf) raises: the payoff matrix is EXACT deterministic
    fitness, so a non-finite entry is a corrupted row, and NaN would otherwise
    poison ``min``/``max`` silently (``[1.0, NaN, 1.0]`` reads as a uniform
    no-gradient pool — papering over, never allowed).
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
        non_finite = sorted(
            sha for sha, fitness in payoffs.items() if not math.isfinite(fitness)
        )
        if non_finite:
            raise ValueError(
                "sample_opponents payoffs must be finite (the exact deterministic "
                f"payoff entries); non-finite entries for {non_finite}"
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
    "DEFAULT_ANCHOR_POLICY",
    "DEFAULT_COEVO_ARTIFACT_ROOT",
    "DEFAULT_EXPLORATION_FLOOR",
    "MAP_ELITES_FOUNDER_ORIGIN",
    "TRAINED_AGAINST_FSM",
    "HallOfFame",
    "HallOfFameMember",
    "LoadableArtifactMetadata",
    "OpponentStalenessCap",
    "OpponentStalenessExceededError",
    "OpponentStalenessLedger",
    "Side",
    "sample_opponents",
    "write_loadable_artifact",
]
