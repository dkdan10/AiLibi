"""The recorded experiment settings an instrument reads, and the refusal for the rest.

A replay-walk profile that sets ``supports_experiments`` accepts every recorded
setting that existed before the Stage-B wave, and each later setting only in a
layer it names in ``threaded_layers`` (:mod:`eval.replay_walk`). That is a
statement about layers. An instrument reviewed for the wave also states, field
by field, which recorded settings it reads: a subset of
:data:`READABLE_SETTINGS`, the wave's eight fields plus the engine's
task-redistribution rule and its recorded kill cooldown, under the first
settings format.
:func:`read_recorded_settings` wraps the instrument's walk and refuses every
other recorded setting at the walk's first tick, before its first advance,
naming the reader and the field. Why each named field is read, and why a field
a reader leaves out is left out, is in that instrument's own module docstring.

The walk still threads what it reads: engine settings reach the seeding, every
advance and every applied meeting through
:func:`orchestrator.experiment_config.engine_arguments`, which refuses an engine
setting it does not thread, and the meeting reset reaches every applied meeting.
This module adds no threading; it only refuses.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Final

from eval.replay_walk import ReplayWalkEvent, TickOpened
from orchestrator.experiment_config import (
    FIELD_LAYER,
    ConfigLayer,
    RecordedExperimentConfig,
    normalize_experiment_config,
)

#: The most a reviewed instrument may read: the Stage-B wave's eight fields, the
#: engine's task-redistribution rule and its recorded kill cooldown. Every other
#: recorded setting, a settings format other than the first, and temporal
#: delivery stay refused.
READABLE_SETTINGS: Final[frozenset[str]] = frozenset(
    {
        "redistribution_policy",
        "kill_cooldown_ticks",
        "vent_witness_rule",
        "vent_exit_policy",
        "vent_entry_policy",
        "meeting_reset",
        "bounded_rebuttal_version",
        "report_body_handle_version",
        "ballot_kill_row_version",
        "impostor_ballot_version",
    }
)


def layers_read(reads: frozenset[str]) -> frozenset[ConfigLayer]:
    """The walk layers besides the engine that ``reads`` covers.

    A profile declares these as its ``threaded_layers``, so the walk's layer
    check and the field list below come from one declaration.
    """

    return frozenset(
        FIELD_LAYER[field] for field in reads if FIELD_LAYER[field] != "engine"
    )


def refuse_unread_settings(
    config: RecordedExperimentConfig | None,
    *,
    reader: str,
    reads: frozenset[str],
) -> None:
    """Raise, naming ``reader`` and the field, for a recorded setting it does not read.

    ``config`` is the recording's own settings (``None`` for a recording made
    without any). A setting at its default is never refused. ``reads`` must be a
    subset of :data:`READABLE_SETTINGS`.
    """

    outside = sorted(reads - READABLE_SETTINGS)
    if outside:
        raise ValueError(
            f"{reader} names settings no reader is reviewed for: {outside}"
        )
    recorded = normalize_experiment_config(config)
    if recorded is None:
        return
    if recorded.format_version != 1:
        raise ValueError(
            f"{reader} does not read the recorded "
            f"format_version={recorded.format_version!r}: it reads recordings made "
            "in the first settings format only"
        )
    for field, info in RecordedExperimentConfig.model_fields.items():
        if field == "format_version" or field in reads:
            continue
        value = getattr(recorded, field)
        if value != info.default:
            scope = (
                "a recording's own settings only for " + ", ".join(sorted(reads))
                if reads
                else "only recordings made without experiment settings"
            )
            raise ValueError(
                f"{reader} does not read the recorded {field}={value!r}: it reads "
                + scope
            )


def read_recorded_settings(
    events: Iterable[ReplayWalkEvent],
    *,
    reader: str,
    reads: frozenset[str],
) -> Iterator[ReplayWalkEvent]:
    """Yield ``events``, refusing unread recorded settings at the first tick.

    The first :class:`eval.replay_walk.TickOpened` comes before the walk's first
    advance, so a refused recording never advances. Every tick row carries the
    same settings, which the walk has already checked, so the first row speaks
    for the recording.
    """

    checked = False
    for event in events:
        if not checked and isinstance(event, TickOpened):
            refuse_unread_settings(
                event.entry.experiment_config, reader=reader, reads=reads
            )
            checked = True
        yield event


__all__ = [
    "READABLE_SETTINGS",
    "layers_read",
    "read_recorded_settings",
    "refuse_unread_settings",
]
