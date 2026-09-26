"""Read a declared experiment config and refuse the slates that cannot carry it.

A recording's experimental switches are fields of
:class:`orchestrator.experiment_config.RecordedExperimentConfig`, and a recorder
takes them from one declared JSON file. Both recorders use this module:
``scripts/run_tournament.py --experiment-config FILE`` parses the file here and
refuses the meeting-experiment environment variables beside it, and
``scripts/refresh_samples.sh`` calls this module's command line (``check`` before
any preflight or staging, ``snapshot`` once the stage directory exists).

Three rules live here, each raising :class:`DeclaredExperimentError`:

* **The file.** It must be one JSON object with no repeated key that
  ``RecordedExperimentConfig`` accepts (the model forbids unknown fields and
  validates every value). Its sha256 is taken over the exact bytes read, which
  is what ``shasum -a 256`` prints for the file.
* **The environment.** Any of the four meeting-experiment variables
  (``meetings.evidence_profile.EXPERIMENT_ENV_NAMES``) present in the
  environment, whatever its value, is refused: a declared config is the only
  source of a recording's switches. The sample recorder refuses them with or
  without a config; ``run_tournament.py`` refuses them beside
  ``--experiment-config``.
* **The target.** A config that turns any switch on records only into an
  explicitly named sample directory. Its sample directory and its manifest must
  both lie physically outside ``replays/samples/`` and ``replays/ml_corpus/``;
  inside ``replays/`` the sample directory must be exactly
  ``replays/candidates/<round>/<set>/`` and the manifest must sit directly in
  such a directory, with round and set names that start with a letter or
  digit. Each target has its symlinks and ``..`` resolved first; then its
  place is decided on disk, not by how the path is spelled: its nearest
  existing directory is looked up by device and inode among the directories
  under ``replays/``, and the segments that do not exist yet follow as
  spelled. So a case-variant spelling on a case-insensitive filesystem, a
  macOS firmlink or a second mount of any of those directories reaches the
  same verdict as the plain path. A config holding only the historical
  defaults records nothing new and goes anywhere.

Every message here is user-facing copy: it names the setting and the rule in
plain words (``tests/scripts/test_candidate_sets.py`` scans
:data:`USER_FACING_TEMPLATES`).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pydantic import ValidationError  # noqa: E402

from meetings.evidence_profile import EXPERIMENT_ENV_NAMES  # noqa: E402
from orchestrator.experiment_config import (  # noqa: E402
    RecordedExperimentConfig,
    normalize_experiment_config,
)

#: The name a candidate round gives its declared config.
CONFIG_FILENAME: Final[str] = "experiment-config.json"

#: A round or set directory name the candidate walks can see: the verifier's
#: shell glob skips a name that starts with a dot.
CANDIDATE_NAME: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")

#: The committed trees a config with switches on may never write into, relative
#: to the repository's ``replays/`` directory.
CANONICAL_TREES: Final[tuple[str, ...]] = ("samples", "ml_corpus")

#: The family a candidate round lives in, relative to ``replays/``.
CANDIDATES_TREE: Final[str] = "candidates"

_INVALID_FILE: Final[str] = "Refused: {path} is not a valid experiment config: {detail}"
_AMBIENT_REFRESH: Final[str] = (
    "Refused: the environment exports {names}. A recording takes its "
    "experimental switches only from a declared config file "
    "(--experiment-config), so unset these variables before recording. "
    "Nothing was staged."
)
_AMBIENT_TOURNAMENT: Final[str] = (
    "Refused: --experiment-config is the one source of this run's experimental "
    "switches, but the environment also exports {names}. Unset them and run "
    "again; nothing was written."
)
_FACTORY_FLAGS: Final[str] = (
    "Refused: --experiment-config records the built-in agents with the declared "
    "switches, so it cannot run beside {flags}. Drop them and run again; nothing "
    "was written."
)
_DEFAULT_TARGET: Final[str] = (
    "Refused: a config that turns experimental switches on needs an explicit "
    "AILIBI_SAMPLE_DIR, because the default target is a committed sample set. "
    "Name a candidate round directory or a scratch directory. Nothing was staged."
)
_CANONICAL_TARGET: Final[str] = (
    "Refused: {variable} resolves to {path}, inside {tree}, which holds committed "
    "recordings made with every experimental switch off. Record into "
    "replays/candidates/<round>/<set>/ or a scratch directory outside replays/. "
    "Nothing was staged."
)
_DEPTH_TARGET: Final[str] = (
    "Refused: {variable} resolves to {path}. Inside replays/, a config that turns "
    "experimental switches on records only into a candidate set directory, "
    "replays/candidates/<round>/<set>/. Nothing was staged."
)
_NAME_TARGET: Final[str] = (
    "Refused: {variable} resolves to {path}, whose round or set name {name!r} "
    "must start with a letter or digit and use only letters, digits, '.', '_' "
    "and '-'. Nothing was staged."
)
_CHANGED_FILE: Final[str] = (
    "Refused: {path} changed after it was checked (it now reads sha256 {now}, "
    "the checked copy read {was}). No seed was recorded; check the file and run "
    "again."
)
_CHECKED: Final[str] = "Experiment config: {path} (sha256 {sha})"
_SETTINGS: Final[str] = "Experiment config settings: {settings}"
_NO_SETTINGS: Final[str] = "none: historical defaults"
_UNDECLARED: Final[str] = (
    "Experiment config: none declared; the recording keeps the historical defaults"
)
_NO_EXPORTS: Final[str] = "Experiment switch exports: none"
_SNAPSHOT: Final[str] = (
    "Experiment config snapshot: {dest} (sha256 {sha}); every seed records from "
    "this copy"
)

#: Every template above, for the plain-copy scan.
USER_FACING_TEMPLATES: Final[tuple[str, ...]] = (
    _INVALID_FILE,
    _AMBIENT_REFRESH,
    _AMBIENT_TOURNAMENT,
    _FACTORY_FLAGS,
    _DEFAULT_TARGET,
    _CANONICAL_TARGET,
    _DEPTH_TARGET,
    _NAME_TARGET,
    _CHANGED_FILE,
    _CHECKED,
    _SETTINGS,
    _NO_SETTINGS,
    _UNDECLARED,
    _NO_EXPORTS,
    _SNAPSHOT,
)


class DeclaredExperimentError(ValueError):
    """A declared config, the environment or a target this module refuses."""


@dataclass(frozen=True)
class DeclaredExperiment:
    """One declared config file: the parsed config and the sha256 of its bytes."""

    path: Path
    config: RecordedExperimentConfig
    sha256: str

    @property
    def normalized(self) -> RecordedExperimentConfig | None:
        """``None`` when every setting is a historical default."""

        return normalize_experiment_config(self.config)

    def settings(self) -> tuple[tuple[str, object], ...]:
        """The fields set off their default, in declaration order."""

        return non_default_settings(self.config)


def non_default_settings(
    config: RecordedExperimentConfig | None,
) -> tuple[tuple[str, object], ...]:
    """``(field, value)`` for each field of ``config`` off its default."""

    if normalize_experiment_config(config) is None:
        return ()
    assert config is not None
    return tuple(
        (field, getattr(config, field))
        for field, info in type(config).model_fields.items()
        if getattr(config, field) != info.default
    )


def describe_settings(config: RecordedExperimentConfig | None) -> str:
    """``field=value, ...`` for the settings off their default, or the default."""

    settings = non_default_settings(config)
    if not settings:
        return _NO_SETTINGS
    return ", ".join(f"{field}={value!r}" for field, value in settings)


def _unique_object(pairs: Sequence[tuple[str, object]]) -> dict[str, object]:
    keys = [key for key, _value in pairs]
    repeated = sorted({key for key in keys if keys.count(key) > 1})
    if repeated:
        raise ValueError(f"the key {repeated[0]!r} appears more than once")
    return dict(pairs)


def parse_config_bytes(data: bytes, *, source: str) -> RecordedExperimentConfig:
    """The config ``data`` declares, or :class:`DeclaredExperimentError`."""

    try:
        payload = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, ValueError) as exc:
        raise DeclaredExperimentError(
            _INVALID_FILE.format(path=source, detail=str(exc))
        ) from exc
    if not isinstance(payload, dict):
        raise DeclaredExperimentError(
            _INVALID_FILE.format(path=source, detail="the file must hold one object")
        )
    try:
        return RecordedExperimentConfig.model_validate(payload)
    except ValidationError as exc:
        detail = "; ".join(
            f"{'.'.join(str(part) for part in error['loc']) or 'config'}: "
            f"{error['msg']}"
            for error in exc.errors()
        )
        raise DeclaredExperimentError(
            _INVALID_FILE.format(path=source, detail=detail)
        ) from exc


def load_declared_config(path: Path) -> DeclaredExperiment:
    """Read ``path`` once and parse it; the sha256 covers exactly those bytes."""

    try:
        data = path.read_bytes()
    except OSError as exc:
        raise DeclaredExperimentError(
            _INVALID_FILE.format(path=path, detail=f"it cannot be read ({exc})")
        ) from exc
    return DeclaredExperiment(
        path=path,
        config=parse_config_bytes(data, source=str(path)),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def ambient_experiment_exports(environ: Mapping[str, str]) -> tuple[str, ...]:
    """The meeting-experiment variables present in ``environ``, whatever their value."""

    return tuple(sorted(name for name in EXPERIMENT_ENV_NAMES if name in environ))


def refuse_ambient_exports(environ: Mapping[str, str], *, recorder: str) -> None:
    """Raise when ``environ`` carries any meeting-experiment variable.

    ``recorder`` picks the message: ``"refresh"`` for the sample recorder, which
    refuses them with or without a declared config, and ``"tournament"`` for
    ``run_tournament.py``, which refuses them beside ``--experiment-config``.
    """

    names = ambient_experiment_exports(environ)
    if not names:
        return
    template = {"refresh": _AMBIENT_REFRESH, "tournament": _AMBIENT_TOURNAMENT}[
        recorder
    ]
    raise DeclaredExperimentError(template.format(names=", ".join(names)))


def refuse_factory_flags(flags: Sequence[str]) -> None:
    """Raise when any agent-factory flag is given beside a declared config.

    ``flags`` names each factory flag the caller was given; an empty sequence
    passes.
    """

    if flags:
        raise DeclaredExperimentError(_FACTORY_FLAGS.format(flags=", ".join(flags)))


def _identity(path: Path) -> tuple[int, int]:
    """The device and inode of the directory ``path`` names on disk."""

    status = path.stat()
    return (status.st_dev, status.st_ino)


def _raise_walk_error(error: OSError) -> None:
    raise error


def _replays_places(replays_root: Path) -> dict[tuple[int, int], tuple[str, ...]]:
    """Every directory under ``replays_root``, by device and inode.

    The value is the directory's segments below ``replays_root``. ``os.walk``
    does not enter a symlinked directory, so each directory is listed once,
    under the name it was made with; a directory the walk cannot read raises
    rather than being left out.
    """

    return {
        _identity(Path(directory)): Path(directory).relative_to(replays_root).parts
        for directory, _subdirectories, _files in os.walk(
            replays_root, onerror=_raise_walk_error
        )
    }


def _place_in_replays(
    path: Path, places: Mapping[tuple[int, int], tuple[str, ...]]
) -> tuple[str, ...] | None:
    """``path``'s segments below ``replays/``, or ``None`` when it lies outside.

    ``path`` has its symlinks and ``..`` resolved (:func:`os.path.realpath`).
    Its nearest existing directory is looked up in ``places`` by device and
    inode, not by spelling, and the segments that do not exist yet follow it as
    spelled, which is where a recorder creates them.
    """

    nearest = next(ancestor for ancestor in (path, *path.parents) if ancestor.is_dir())
    place = places.get(_identity(nearest))
    if place is None:
        return None
    return (*place, *path.relative_to(nearest).parts)


def target_problem(
    *,
    variable: str,
    path: Path,
    is_manifest: bool,
    places: Mapping[tuple[int, int], tuple[str, ...]],
) -> str | None:
    """Why ``path`` may not receive a recording that turns switches on, if it may not.

    ``path`` is physical: resolved through every symlink and ``..``. Its place
    in ``replays/`` comes from :func:`_place_in_replays`, on disk, over
    ``places`` (:func:`_replays_places`). A sample directory inside
    ``replays/`` must be exactly a candidate set directory; a manifest must sit
    directly in one.
    """

    place = _place_in_replays(path, places)
    if place is None:
        return None
    if place and place[0] in CANONICAL_TREES:
        return _CANONICAL_TARGET.format(
            variable=variable, path=path, tree=f"replays/{place[0]}/"
        )
    directory = place[:-1] if is_manifest else place
    if len(directory) != 3 or directory[0] != CANDIDATES_TREE:
        return _DEPTH_TARGET.format(variable=variable, path=path)
    for name in directory[1:]:
        if CANDIDATE_NAME.fullmatch(name) is None:
            return _NAME_TARGET.format(variable=variable, path=path, name=name)
    return None


def refuse_unsafe_target(
    config: RecordedExperimentConfig | None,
    *,
    sample_dir: Path,
    manifest: Path,
    sample_dir_explicit: bool,
    repo_root: Path = _REPO_ROOT,
) -> None:
    """Raise when a config with switches on is aimed at a target it may not use.

    A config whose every setting is a historical default passes anywhere.
    """

    if normalize_experiment_config(config) is None:
        return
    if not sample_dir_explicit:
        raise DeclaredExperimentError(_DEFAULT_TARGET)
    places = _replays_places(repo_root / "replays")
    for variable, target, is_manifest in (
        ("AILIBI_SAMPLE_DIR", sample_dir, False),
        ("AILIBI_MANIFEST", manifest, True),
    ):
        problem = target_problem(
            variable=variable,
            path=Path(os.path.realpath(target)),
            is_manifest=is_manifest,
            places=places,
        )
        if problem is not None:
            raise DeclaredExperimentError(problem)


def check_lines(declared: DeclaredExperiment | None) -> tuple[str, ...]:
    """The lines a recorder prints for its declared config and the environment."""

    if declared is None:
        return (_UNDECLARED, _NO_EXPORTS)
    return (
        _CHECKED.format(path=declared.path, sha=declared.sha256),
        _SETTINGS.format(settings=describe_settings(declared.config)),
        _NO_EXPORTS,
    )


def write_snapshot(source: Path, dest: Path, *, expected_sha256: str) -> str:
    """Copy ``source`` to ``dest`` if it still reads as checked; return the line.

    The bytes are read once, compared with the sha256 the check printed,
    validated again and written to a new ``dest``, so every seed records from
    the copy that was checked.
    """

    try:
        data = source.read_bytes()
    except OSError as exc:
        raise DeclaredExperimentError(
            _INVALID_FILE.format(path=source, detail=f"it cannot be read ({exc})")
        ) from exc
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected_sha256:
        raise DeclaredExperimentError(
            _CHANGED_FILE.format(path=source, now=actual, was=expected_sha256)
        )
    parse_config_bytes(data, source=str(source))
    with dest.open("xb") as handle:
        handle.write(data)
    return _SNAPSHOT.format(dest=dest, sha=actual)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check a declared experiment config, the environment and the "
            "recording target, or snapshot the checked config into a stage."
        )
    )
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check")
    check.add_argument("--config", type=Path, default=None)
    check.add_argument("--sample-dir", type=Path, required=True)
    check.add_argument("--manifest", type=Path, required=True)
    check.add_argument("--sample-dir-explicit", action="store_true")
    check.add_argument("--prefix", default="")
    snapshot = commands.add_parser("snapshot")
    snapshot.add_argument("--config", type=Path, required=True)
    snapshot.add_argument("--dest", type=Path, required=True)
    snapshot.add_argument("--expect-sha", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "snapshot":
            print(
                write_snapshot(args.config, args.dest, expected_sha256=args.expect_sha)
            )
            return 0
        refuse_ambient_exports(os.environ, recorder="refresh")
        declared = (
            load_declared_config(args.config) if args.config is not None else None
        )
        refuse_unsafe_target(
            declared.config if declared is not None else None,
            sample_dir=args.sample_dir,
            manifest=args.manifest,
            sample_dir_explicit=args.sample_dir_explicit,
        )
    except DeclaredExperimentError as exc:
        print(exc, file=sys.stderr)
        return 1
    for line in check_lines(declared):
        print(f"{args.prefix}{line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
