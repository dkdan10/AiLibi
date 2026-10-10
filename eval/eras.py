"""The committed replay sets and the recorded era each one belongs to.

Since the promotion of candidate round 3 (2026-10-09) the tree holds two eras.
``replays/samples/9p2i`` holds the round-3 recording: the seven adopted Stage-B
arms, the kept vent exit, a six-tick kill cooldown and the route lines, recorded
once under one declared experiment config. The other three committed sets keep
the baseline-9 process re-record. An era is the recorded identity a group of
games shares: its settings, temporal delivery, substrate stamp and prompt stamps
(:class:`eval.gameplay_census.EraKey`). Two eras are never pooled.

This module is the one place a committed set's era is named. Every instrument
that walks more than one committed set (the process scorecard, the gameplay
census, the counterfactual, the watchability referee's default floors, the
front door's fact checker) and the recorder's target rule read it; none of them
names a set's era on its own. The registry states, per era, its id, the record
that owns it, the date its sets were recorded and its declared config file, or
none. ``tests/eval/test_eras.py`` holds the registry to the bytes: each set's
games fold to one census era key, the sets of one era id share it, ids differ
where keys differ, and every game of an era with a declared config recorded
exactly that config. It also holds :data:`ERAS` to the eras the registry names
(:func:`registered_eras`).

The substrate ladder tip stays at baseline 9: no substrate lever moved, and
baseline 10 is reserved for the full re-record that re-freezes the corpus.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class Era:
    """One recorded era.

    ``record`` is the repository path of the record that owns the era's sets;
    ``recorded_on`` is the ``refreshed_at`` date its MANIFEST rows carry;
    ``declared_config`` is the repository path of the experiment config every
    game of the era recorded, or ``None`` for an era recorded with every
    experimental switch off.
    """

    id: str
    record: str
    recorded_on: str
    declared_config: str | None


@dataclass(frozen=True)
class CommittedSet:
    """One committed replay set, named by its repository path, and its era."""

    path: str
    era: Era

    @property
    def name(self) -> str:
        """The set's roster directory name, for example ``9p2i``."""

        return self.path.rsplit("/", 1)[-1]

    @property
    def label(self) -> str:
        """The set's path below ``replays/``, for example ``samples/9p2i``."""

        return self.path.removeprefix("replays/")


#: The process re-record that adopted the substrate wave; the ladder tip.
BASELINE_9: Final[Era] = Era(
    id="baseline-9",
    record="audits/audit-2026-09-22-process-rerecord.md",
    recorded_on="2026-09-22",
    declared_config=None,
)

#: Candidate round 2, the shown 9-player set from 2026-10-02 to 2026-10-09. It
#: owns no committed set: its bytes are the candidate copy
#: ``replays/candidates/stage-b-r2``, read with this declared config there.
STAGE_B_R2: Final[Era] = Era(
    id="stage-b-r2",
    record="audits/audit-2026-10-01-stage-b-r2.md",
    recorded_on="2026-10-01",
    declared_config="replays/candidates/stage-b-r2/experiment-config.json",
)

#: Candidate round 3, promoted as the shown 9-player set on 2026-10-09 (the
#: round's record, section 12).
STAGE_B_R3: Final[Era] = Era(
    id="stage-b-r3",
    record="audits/audit-2026-10-09-stage-b-r3.md",
    recorded_on="2026-10-09",
    declared_config="replays/samples/9p2i/experiment-config.json",
)

#: Every era a committed set belongs to, oldest first. ``tests/eval/test_eras.py``
#: holds it equal to :func:`registered_eras` of the registry below.
ERAS: Final[tuple[Era, ...]] = (BASELINE_9, STAGE_B_R3)

#: The era the substrate ladder tip stands at. A directory the registry does not
#: name (a candidate round, a scratch copy, a training evaluation) is measured
#: against it unless its caller names another.
LADDER_TIP_ERA: Final[Era] = BASELINE_9

#: The four committed sets, in publication order.
COMMITTED_SETS: Final[tuple[CommittedSet, ...]] = (
    CommittedSet("replays/ml_corpus/9p2i", BASELINE_9),
    CommittedSet("replays/samples/9p2i", STAGE_B_R3),
    CommittedSet("replays/ml_corpus/4p1i", BASELINE_9),
    CommittedSet("replays/samples/4p1i", BASELINE_9),
)


def committed_set(
    path: str, *, registry: Sequence[CommittedSet] = COMMITTED_SETS
) -> CommittedSet:
    """The registry entry for ``path`` (``replays/...``); an unnamed path raises."""

    for entry in registry:
        if entry.path == path:
            return entry
    raise ValueError(
        f"{path} is not a committed set; the era registry names "
        + ", ".join(entry.path for entry in registry)
    )


def era_of(path: str, *, registry: Sequence[CommittedSet] = COMMITTED_SETS) -> Era:
    """The era ``path``'s committed set belongs to; an unnamed path raises."""

    return committed_set(path, registry=registry).era


def era_groups(
    paths: Sequence[str], *, registry: Sequence[CommittedSet] = COMMITTED_SETS
) -> tuple[tuple[Era, tuple[str, ...]], ...]:
    """``paths`` grouped by era, eras in first-appearance order, paths in order.

    Every path must be a committed set the registry names; an instrument pools
    only within one of these groups.
    """

    groups: dict[str, tuple[Era, list[str]]] = {}
    for path in paths:
        era = era_of(path, registry=registry)
        groups.setdefault(era.id, (era, []))[1].append(path)
    return tuple((era, tuple(members)) for era, members in groups.values())


def sets_in(
    era: Era, *, registry: Sequence[CommittedSet] = COMMITTED_SETS
) -> tuple[str, ...]:
    """The committed sets of ``era``, in publication order."""

    return tuple(entry.path for entry in registry if entry.era == era)


def registered_eras(
    registry: Sequence[CommittedSet] = COMMITTED_SETS,
) -> tuple[Era, ...]:
    """The distinct eras ``registry`` names, oldest first.

    Ordered by recording date, eras of one date in first-appearance order. Two
    different eras filed under one id raise: an id names one recorded era.
    """

    distinct: dict[str, Era] = {}
    for entry in registry:
        if distinct.setdefault(entry.era.id, entry.era) != entry.era:
            raise ValueError(
                f"the era registry files two different eras under the id {entry.era.id}"
            )
    return tuple(sorted(distinct.values(), key=lambda era: era.recorded_on))


__all__ = [
    "BASELINE_9",
    "COMMITTED_SETS",
    "ERAS",
    "LADDER_TIP_ERA",
    "STAGE_B_R2",
    "STAGE_B_R3",
    "CommittedSet",
    "Era",
    "committed_set",
    "era_groups",
    "era_of",
    "registered_eras",
    "sets_in",
]
