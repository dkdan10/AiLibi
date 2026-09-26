"""Candidate rounds: their declared shape, and the checks CI runs on each.

``replays/candidates/README.md`` defines a candidate round: a README carrying
one ``candidate-declaration`` block, the declared ``experiment-config.json`` and
one directory per set, each holding exactly its declared seeds, a MANIFEST
naming one recording sha, a roster and the report built from its recordings.
:func:`round_problems` checks one round against that shape, through the gate's
own library checks (no second implementation) and the shared cached report
check in ``tests/_helpers/committed.py``. The committed leg walks every round
the tree holds; the planted legs build a fake round in ``tmp_path`` and perturb
it one way at a time.

This module also holds the two publication cases (the API's set lookup and the
demo bundle never read a candidate) and the plain-copy scan over the card's new
messages.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import shutil
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Final

import pytest

import _declared_experiment as de
import _manifest_writer
import _verify_samples
import build_sample_report
import run_tournament
import validity_gate
from api.main import _resolve_replay_dir
from api.replay_loader import SetLoaderRegistry
from eval import kill_craft
from eval.balance_eval import run_tournament_eval
from eval.report_io import REPORT_FILENAME, read_report_text, write_report_text
from eval.validity import (
    SetInventory,
    assemble_tournament_report,
    experiment_config_violations,
    read_set_inventory,
    recording_sha_violations,
    seed_set_violations,
)
from orchestrator.experiment_config import RecordedExperimentConfig
from tests._helpers.committed import (
    CANDIDATES_ROOT,
    candidate_report_check,
    candidate_rounds,
    repo_root,
)

#: The info string of a round README's declaration block.
DECLARATION_INFO: Final[str] = "candidate-declaration"
#: What a round holds besides its set directories.
ROUND_FILES: Final[frozenset[str]] = frozenset({"README.md", de.CONFIG_FILENAME})
#: What a set holds besides its replays.
SET_FILES: Final[frozenset[str]] = frozenset(
    {"MANIFEST.md", "roster.json", REPORT_FILENAME}
)
_SET_LINE: Final[re.Pattern[str]] = re.compile(
    r"(?P<name>\S+) seeds (?P<first>\d+)-(?P<last>\d+)"
)
_FAMILY_README: Final[str] = "README.md"


def declaration_blocks(text: str) -> list[list[str]]:
    """The body lines of every fenced block whose info string is the declaration's.

    Fences are tracked in order, and, as in Markdown, only a bare fence closes
    one: a declaration opener inside another fenced block is that block's text,
    not a declaration.
    """

    blocks: list[list[str]] = []
    body: list[str] | None = None
    fenced = False
    for line in text.splitlines():
        stripped = line.strip()
        if fenced and stripped == "```":
            fenced = False
            if body is not None:
                blocks.append(body)
                body = None
        elif not fenced and stripped.startswith("```"):
            fenced = True
            body = [] if stripped[3:].strip() == DECLARATION_INFO else None
        elif body is not None:
            body.append(stripped)
    if fenced:
        blocks.append(["<an unterminated fence>"])
    return blocks


@dataclass(frozen=True)
class Declaration:
    """A round's declaration: the config's sha256 line and each set's seeds."""

    config_line: str
    sets: Mapping[str, frozenset[int]]


def parse_declaration(block: list[str]) -> tuple[Declaration, list[str]]:
    """The declaration a block states, and the problems with its lines."""

    problems: list[str] = []
    sets: dict[str, frozenset[int]] = {}
    for line in block[1:]:
        match = _SET_LINE.fullmatch(line)
        if (
            match is None
            or de.CANDIDATE_NAME.fullmatch(match["name"]) is None
            or int(match["first"]) > int(match["last"])
            or match["name"] in sets
        ):
            problems.append(
                f"declaration line {line!r} is not one '<set> seeds <first>-<last>'"
            )
            continue
        sets[match["name"]] = frozenset(
            range(int(match["first"]), int(match["last"]) + 1)
        )
    if not sets:
        problems.append("the declaration names no set")
    return Declaration(config_line=block[0] if block else "", sets=sets), problems


def set_problems(
    set_dir: Path,
    seeds: frozenset[int],
    config: RecordedExperimentConfig,
    *,
    report_check: Callable[[Path], int],
) -> list[str]:
    """Where one declared set departs from its declaration."""

    wanted = {f"replay-seed-{seed}.jsonl" for seed in seeds} | SET_FILES
    held = {path.name for path in set_dir.iterdir()}
    problems = [f"unexpected {name!r}" for name in sorted(held - wanted)]
    problems += [f"missing {name!r}" for name in sorted(wanted - held)]
    inventory = read_set_inventory(set_dir)
    problems += seed_set_violations(inventory, seeds)
    problems += recording_sha_violations(inventory)
    problems += experiment_config_violations(
        assemble_tournament_report(set_dir).games, config
    )
    problems += [
        failure.render() for failure in _verify_samples.verify_samples(set_dir)
    ]
    if report_check(set_dir) != 0:
        problems.append(
            f"{REPORT_FILENAME} differs from a rebuild from the set's recordings"
        )
    return problems


def round_problems(
    round_dir: Path, *, report_check: Callable[[Path], int] = candidate_report_check
) -> list[str]:
    """Where one candidate round departs from the family's declared shape."""

    problems: list[str] = []
    if de.CANDIDATE_NAME.fullmatch(round_dir.name) is None:
        problems.append(f"{round_dir.name!r} is not a round name")
    try:
        declared = de.load_declared_config(round_dir / de.CONFIG_FILENAME)
    except de.DeclaredExperimentError as exc:
        return [*problems, str(exc)]
    if declared.normalized is None:
        problems.append(f"{de.CONFIG_FILENAME} turns no experimental switch on")
    readme = round_dir / "README.md"
    if not readme.is_file():
        return [*problems, "the round has no README.md"]
    blocks = declaration_blocks(readme.read_text(encoding="utf-8"))
    if len(blocks) != 1:
        return [
            *problems,
            f"README.md holds {len(blocks)} {DECLARATION_INFO} blocks; one is required",
        ]
    declaration, line_problems = parse_declaration(blocks[0])
    problems += line_problems
    expected_line = f"{declared.sha256}  {de.CONFIG_FILENAME}"
    if declaration.config_line != expected_line:
        problems.append(
            f"the declaration's first line is {declaration.config_line!r}, but "
            f"shasum -a 256 prints {expected_line!r}"
        )
    held = {path.name for path in round_dir.iterdir()}
    wanted = ROUND_FILES | set(declaration.sets)
    problems += [f"undeclared {name!r} in the round" for name in sorted(held - wanted)]
    problems += [f"missing {name!r}" for name in sorted(wanted - held)]
    for name, seeds in sorted(declaration.sets.items()):
        set_dir = round_dir / name
        if not set_dir.is_dir():
            continue
        problems += [
            f"{name}: {problem}"
            for problem in set_problems(
                set_dir, seeds, declared.config, report_check=report_check
            )
        ]
    return problems


def family_problems(root: Path) -> list[str]:
    """What the family root holds besides its README and round directories."""

    if not root.is_dir():
        return [f"{root} is not a directory"]
    problems = [
        f"{path.name!r} is neither the family README nor a round directory"
        for path in sorted(root.iterdir())
        if not (
            (path.name == _FAMILY_README and path.is_file())
            or (path.is_dir() and de.CANDIDATE_NAME.fullmatch(path.name) is not None)
        )
    ]
    if not (root / _FAMILY_README).is_file():
        problems.append("the family has no README.md")
    return problems


# --------------------------------------------------------------------------- #
# The committed leg                                                            #
# --------------------------------------------------------------------------- #


def test_every_committed_round_holds_its_declared_shape() -> None:
    """Every round the tree holds, through the enumerator and the cached check.

    The family root holds its README and round directories only. When no round
    is committed the walk covers none, and the family check still runs.
    """

    assert family_problems(CANDIDATES_ROOT) == []
    assert candidate_rounds() == tuple(
        path for path in sorted(CANDIDATES_ROOT.iterdir()) if path.is_dir()
    )
    problems = {
        round_dir.name: round_problems(round_dir) for round_dir in candidate_rounds()
    }
    assert all(not found for found in problems.values()), problems


def test_the_enumerator_lists_rounds_only_and_reads_an_absent_root(
    tmp_path: Path,
) -> None:
    (tmp_path / "b-round").mkdir()
    (tmp_path / "a-round").mkdir()
    (tmp_path / "README.md").write_text("family\n")
    assert candidate_rounds(tmp_path) == (tmp_path / "a-round", tmp_path / "b-round")
    assert candidate_rounds(tmp_path / "absent") == ()


# --------------------------------------------------------------------------- #
# The planted round                                                            #
# --------------------------------------------------------------------------- #

#: The declared test config: arms that exist today, since the pending guard
#: refuses the wave's new values.
_TEST_CONFIG_JSON: Final[str] = (
    '{"format_version": 1, "meeting_reset": "hub_with_grace", '
    '"vent_exit_policy": "observed_risk", "bounded_rebuttal_version": 1}\n'
)
_SET: Final[str] = "4p1i"
_SEEDS: Final[tuple[int, ...]] = (0, 1)
_SHA: Final[str] = "abc1234"


def _kill_craft_reads_the_test_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Let the report's kill-craft walk read the test config's recordings.

    Kill-craft refuses every experiment recording until the readers card
    widens its profile; the test config sets only settings that existed before
    the Stage-B wave, which ``supports_experiments`` alone covers. Once kill-craft
    reads them itself this does nothing, and it should then be deleted.
    """

    if not kill_craft._WALK_CONFIG.supports_experiments:
        monkeypatch.setattr(
            kill_craft,
            "_WALK_CONFIG",
            replace(kill_craft._WALK_CONFIG, supports_experiments=True),
        )


@pytest.fixture(autouse=True)
def _report_reads_the_planted_rounds(monkeypatch: pytest.MonkeyPatch) -> None:
    _kill_craft_reads_the_test_config(monkeypatch)


def _readme(sha256: str, sets: Mapping[str, str]) -> str:
    lines = "\n".join(f"{name} seeds {seeds}" for name, seeds in sets.items())
    return (
        "# A planted round\n\n"
        f"```{DECLARATION_INFO}\n{sha256}  {de.CONFIG_FILENAME}\n{lines}\n```\n"
    )


def _build_round(root: Path) -> Path:
    """A fake candidate round recorded on the test config, in the declared shape."""

    round_dir = root / "planted-r1"
    set_dir = round_dir / _SET
    set_dir.mkdir(parents=True)
    config_path = round_dir / de.CONFIG_FILENAME
    config_path.write_text(_TEST_CONFIG_JSON, encoding="utf-8")
    declared = de.load_declared_config(config_path)
    run_tournament_eval(
        seeds=_SEEDS,
        output_dir=set_dir,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
        experiment_config=declared.config,
    )
    for audit in set_dir.glob("*.audit.jsonl"):
        audit.unlink()
    _manifest_writer.ensure_roster_descriptor(
        set_dir, num_players=4, num_impostors=1, tasks_per_crewmate=1
    )
    _manifest_writer.update_manifest(
        set_dir / "MANIFEST.md",
        set_dir,
        _SEEDS,
        git_sha=_SHA,
        refreshed_at="2026-09-26",
        model_override="fake-meeting",
    )
    build_sample_report.write_report(set_dir)
    (round_dir / "README.md").write_text(
        _readme(declared.sha256, {_SET: f"{_SEEDS[0]}-{_SEEDS[-1]}"}), encoding="utf-8"
    )
    (root / _FAMILY_README).write_text("The planted family.\n", encoding="utf-8")
    return round_dir


@pytest.fixture(scope="module")
def planted_round(tmp_path_factory: pytest.TempPathFactory) -> Path:
    with pytest.MonkeyPatch.context() as monkeypatch:
        _kill_craft_reads_the_test_config(monkeypatch)
        return _build_round(tmp_path_factory.mktemp("family"))


def _copy_family(planted_round: Path, tmp_path: Path) -> Path:
    """A fresh copy of the planted family, so each perturbation is its own path."""

    family = Path(shutil.copytree(planted_round.parent, tmp_path / "family"))
    return family / planted_round.name


def test_the_planted_round_holds_its_declared_shape(planted_round: Path) -> None:
    assert round_problems(planted_round) == []
    assert family_problems(planted_round.parent) == []


def _only(problems: list[str], fragment: str) -> None:
    assert problems, "the perturbation went unnoticed"
    assert any(fragment in problem for problem in problems), problems


def test_one_byte_of_the_config_fails_the_declared_sha(
    planted_round: Path, tmp_path: Path
) -> None:
    round_dir = _copy_family(planted_round, tmp_path)
    config = round_dir / de.CONFIG_FILENAME
    config.write_text(
        _TEST_CONFIG_JSON.replace('"format_version": 1', '"format_version":\t1')
    )
    assert len(config.read_bytes()) == len(_TEST_CONFIG_JSON.encode())
    _only(round_problems(round_dir), "the declaration's first line is")


@pytest.mark.parametrize("copies", [0, 2])
def test_a_missing_or_doubled_block_fails(
    planted_round: Path, tmp_path: Path, copies: int
) -> None:
    round_dir = _copy_family(planted_round, tmp_path)
    readme = round_dir / "README.md"
    text = readme.read_text(encoding="utf-8")
    block = text[text.index(f"```{DECLARATION_INFO}") :]
    readme.write_text(text.replace(block, block * copies), encoding="utf-8")
    assert round_problems(round_dir) == [
        f"README.md holds {copies} {DECLARATION_INFO} blocks; one is required"
    ]


def test_an_undeclared_set_directory_fails(planted_round: Path, tmp_path: Path) -> None:
    round_dir = _copy_family(planted_round, tmp_path)
    shutil.copytree(round_dir / _SET, round_dir / "9p2i")
    _only(round_problems(round_dir), "undeclared '9p2i' in the round")


def test_a_missing_seed_fails(planted_round: Path, tmp_path: Path) -> None:
    round_dir = _copy_family(planted_round, tmp_path)
    (round_dir / _SET / "replay-seed-1.jsonl").unlink()
    problems = round_problems(round_dir)
    _only(problems, "missing 'replay-seed-1.jsonl'")
    _only(problems, "the replay files do not hold exactly the declared seeds")


def test_a_foreign_recording_sha_fails(planted_round: Path, tmp_path: Path) -> None:
    round_dir = _copy_family(planted_round, tmp_path)
    manifest = round_dir / _SET / "MANIFEST.md"
    lines = manifest.read_text(encoding="utf-8").splitlines()
    manifest.write_text(
        "\n".join(
            line.replace(f"| {_SHA} |", "| def5678 |")
            if line.startswith("| 1 |")
            else line
            for line in lines
        )
        + "\n",
        encoding="utf-8",
    )
    _only(round_problems(round_dir), "MANIFEST.md names 2 recording shas")


def test_a_mixed_config_fails(planted_round: Path, tmp_path: Path) -> None:
    round_dir = _copy_family(planted_round, tmp_path)
    path = round_dir / _SET / "replay-seed-0.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    for row in rows:
        if row["kind"] in ("tick", "game_over"):
            row["experiment_config"]["bounded_rebuttal_version"] = None
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    _only(round_problems(round_dir), "headless-seed-0: recorded experiment config")


def test_one_edited_report_cell_fails(planted_round: Path, tmp_path: Path) -> None:
    round_dir = _copy_family(planted_round, tmp_path)
    report = round_dir / _SET / REPORT_FILENAME
    payload = json.loads(read_report_text(report))
    payload["report"]["games"][0]["final_tick"] += 1
    write_report_text(report, json.dumps(payload))
    assert json.loads(gzip.decompress(report.read_bytes())) == payload
    assert round_problems(round_dir) == [
        f"{_SET}: {REPORT_FILENAME} differs from a rebuild from the set's recordings"
    ]


def test_a_stray_file_in_the_family_root_fails(
    planted_round: Path, tmp_path: Path
) -> None:
    round_dir = _copy_family(planted_round, tmp_path)
    (round_dir.parent / "notes.txt").write_text("stray\n")
    assert family_problems(round_dir.parent) == [
        "'notes.txt' is neither the family README nor a round directory"
    ]
    (round_dir.parent / _FAMILY_README).unlink()
    assert "the family has no README.md" in family_problems(round_dir.parent)


def test_a_config_turning_no_switch_on_fails(
    planted_round: Path, tmp_path: Path
) -> None:
    round_dir = _copy_family(planted_round, tmp_path)
    config = round_dir / de.CONFIG_FILENAME
    config.write_text('{"format_version": 1}\n')
    readme = round_dir / "README.md"
    readme.write_text(
        _readme(hashlib.sha256(config.read_bytes()).hexdigest(), {_SET: "0-1"})
    )
    problems = round_problems(round_dir)
    _only(problems, "turns no experimental switch on")
    # Its games still recorded the test config, which the declared file is not.
    _only(problems, "recorded experiment config")


@pytest.mark.parametrize(
    "line",
    [
        "4p1i seeds 1-0",
        "4p1i seeds 0 to 1",
        ".hidden seeds 0-1",
        "4p1i seeds 0-1 extra",
    ],
)
def test_a_malformed_declaration_line_fails(line: str) -> None:
    _declaration, problems = parse_declaration([f"{'0' * 64}  x", line])
    assert problems[0] == (
        f"declaration line {line!r} is not one '<set> seeds <first>-<last>'"
    )


def test_a_declaration_names_a_set_once_and_at_least_one() -> None:
    _declaration, problems = parse_declaration(
        [f"{'0' * 64}  x", "4p1i seeds 0-1", "4p1i seeds 2-3"]
    )
    assert problems == [
        "declaration line '4p1i seeds 2-3' is not one '<set> seeds <first>-<last>'"
    ]
    _declaration, problems = parse_declaration([f"{'0' * 64}  x"])
    assert problems == ["the declaration names no set"]


def test_a_declaration_inside_another_fence_is_not_read() -> None:
    text = (
        "```text\n```candidate-declaration\n```\n"
        f"```{DECLARATION_INFO}\nsha  experiment-config.json\n4p1i seeds 0-1\n```\n"
    )
    assert declaration_blocks(text) == [
        ["sha  experiment-config.json", "4p1i seeds 0-1"]
    ]
    assert declaration_blocks(f"```{DECLARATION_INFO}\nsha\n") == [
        ["<an unterminated fence>"]
    ]


def test_the_family_readme_declares_nothing() -> None:
    text = (CANDIDATES_ROOT / _FAMILY_README).read_text(encoding="utf-8")
    assert declaration_blocks(text) == []
    assert DECLARATION_INFO in text


# --------------------------------------------------------------------------- #
# Publication: the API's set lookup and the demo bundle never read a round     #
# --------------------------------------------------------------------------- #


def _hermetic_tree(anchor: Path) -> None:
    sample = repo_root / "replays" / "samples" / "9p2i" / "replay-seed-0.jsonl"
    (anchor / "replays" / "samples" / "9p2i").mkdir(parents=True)
    shutil.copy(sample, anchor / "replays" / "samples" / "9p2i")


def test_a_candidate_round_changes_neither_the_resolved_root_nor_its_sets(
    tmp_path: Path,
) -> None:
    _hermetic_tree(tmp_path)
    samples = tmp_path / "replays" / "samples"
    assert _resolve_replay_dir(anchor=tmp_path) == samples
    before = SetLoaderRegistry(samples).available_sets()

    planted = tmp_path / "replays" / "candidates" / "r" / "9p2i"
    planted.mkdir(parents=True)
    shutil.copy(samples / "9p2i" / "replay-seed-0.jsonl", planted)
    assert _resolve_replay_dir(anchor=tmp_path) == samples
    assert SetLoaderRegistry(samples).available_sets() == before == ["9p2i"]

    # Perturbed: the same set one level below replays/ is what the lookup reads.
    shutil.move(planted, tmp_path / "replays" / "9p2i")
    assert _resolve_replay_dir(anchor=tmp_path) == tmp_path / "replays"


# --------------------------------------------------------------------------- #
# The copy this card adds is plain                                             #
# --------------------------------------------------------------------------- #

_TASK_OR_AUDIT_ID: Final[re.Pattern[str]] = re.compile(r"\bTask \d|\baudit-")
_THRESHOLD_ARITHMETIC: Final[re.Pattern[str]] = re.compile(
    r"[<>≤≥]=?\s*\d|\d\s*[<>≤≥]|\b\d+\s*/\s*\d+\b"
)


def copy_problems(text: str) -> list[str]:
    """Task or audit identifiers and bare threshold arithmetic in ``text``."""

    return [
        f"{label}: {match.group(0)!r}"
        for label, pattern in (
            ("identifier", _TASK_OR_AUDIT_ID),
            ("threshold arithmetic", _THRESHOLD_ARITHMETIC),
        )
        for match in pattern.finditer(text)
    ]


def _help_from(text: str, first_option: str) -> str:
    """``text`` from the line naming ``first_option`` to the next help section."""

    lines = text.splitlines()
    start = next(
        i for i, line in enumerate(lines) if line.lstrip().startswith(first_option)
    )
    return "\n".join(lines[start:])


def _new_copy(
    capsys: pytest.CaptureFixture[str], planted_inventory: SetInventory
) -> dict[str, str]:
    """Every message and help text this card adds, rendered."""

    copy: dict[str, str] = {
        f"template {index}": template
        for index, template in enumerate(de.USER_FACING_TEMPLATES)
    }
    copy["family README"] = (CANDIDATES_ROOT / _FAMILY_README).read_text(
        encoding="utf-8"
    )
    for name, parse in (
        ("run_tournament --help", run_tournament._parse_args),
        ("validity_gate --help", validity_gate.main),
    ):
        with pytest.raises(SystemExit):
            parse(["--help"])
        copy[name] = capsys.readouterr().out
    copy["run_tournament --help"] = _help_from(
        copy["run_tournament --help"], "--experiment-config"
    )
    copy["validity_gate --help"] = _help_from(
        copy["validity_gate --help"], "--expected-experiment-config"
    )
    refresh = (repo_root / "scripts" / "refresh_samples.sh").read_text(encoding="utf-8")
    usage = refresh[refresh.index("  --experiment-config FILE") :]
    copy["refresh_samples --help"] = usage[: usage.index("  -h, --help")]
    copy["refresh_samples echoes"] = "\n".join(
        line
        for line in refresh.splitlines()
        if "echo" in line
        and ("experiment config" in line or "experiment-config" in line)
    )
    verify = (repo_root / "scripts" / "verify_samples.sh").read_text(encoding="utf-8")
    copy["verify_samples echo"] = "\n".join(
        line
        for line in verify.splitlines()
        if "candidate set" in line and "echo" in line
    )
    copy["gate violations"] = "\n".join(
        [
            *seed_set_violations(planted_inventory, frozenset({0, 1, 2})),
            *recording_sha_violations(
                replace(planted_inventory, manifest_shas=((0, "a"), (1, "b")))
            ),
            *recording_sha_violations(replace(planted_inventory, manifest_seeds=None)),
        ]
    )
    return copy


def test_the_new_copy_carries_no_identifier_and_no_threshold_arithmetic(
    planted_round: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    set_dir = planted_round / _SET
    copy = _new_copy(capsys, read_set_inventory(set_dir))
    copy["gate config violation"] = "\n".join(
        experiment_config_violations(assemble_tournament_report(set_dir).games, None)
    )
    assert all(text.strip() for text in copy.values()), [
        name for name, text in copy.items() if not text.strip()
    ]
    problems = {name: copy_problems(text) for name, text in copy.items()}
    assert all(not found for found in problems.values()), problems


@pytest.mark.parametrize(
    "planted",
    [
        "Refused: see Task 20.33 for the recorder rule.",
        "Refused: read audits/audit-phase-21-close.md first.",
        "Refused: the rate must stay >= 0.6 here.",
        "Refused: 6/7 of the tasks are done.",
    ],
)
def test_the_copy_scan_catches_a_planted_identifier_or_threshold(planted: str) -> None:
    assert copy_problems(planted)
    assert copy_problems("Refused: the recorder rule, stated plainly.") == []
