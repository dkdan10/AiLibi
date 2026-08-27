"""No eval or training module may re-derive a recorded meeting's flags.

Production hands ``meetings.transcript.detect_contradictions`` the meeting's
trigger kind and all three private grounding channels -- vent witness records,
move witness records, per-speaker sighting records -- and the flags it returns
are what the meeting priced, what the ballots cited and what the replay
persisted. None of those channels survive into the recorded transcript, so a
call passing ``roster=`` and nothing else answers a question about a different
game: on ``replays/ml_corpus/9p2i`` that re-derivation loses 43 of the 120
recorded non-vent flags and mints 46 the record never carried, and 61 of the
corpus's meetings come back with a different flag id-set.

The instruments read the record instead --
:func:`eval.meeting_quality.recorded_contradiction_flags`, mirrored in
``training/conviction/dataset.py`` where the firewall forbids an ``eval.*``
import. This module is the structural gate that keeps it that way: it walks
``eval/`` and ``training/`` with :mod:`ast` and fails on any
``detect_contradictions`` call whose keyword set is exactly ``{"roster"}``.

The walk is restricted to those two packages by construction, not by an
allowlist. ``scripts/counterfactual_phase20.py`` and
``audits/workflows/extract_gameplay_facts.py`` both re-derive on purpose -- a
counterfactual is exactly what they are for -- and both live outside the swept
roots, so no entry can rot into covering the sites this gate forbids. The
allowlist below is empty and is expected to stay that way.

The gate ships with a planted counter-case in a temp tree, plus a threaded call
asserted clean by the same predicate, so it discriminates on the keyword set
rather than on the function name.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Final

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]

#: The packages whose instruments must read the record. Everything outside them
#: is free to re-derive; see the module docstring for why that is deliberate.
_SWEPT_PACKAGES: Final[tuple[str, ...]] = ("eval", "training")

#: Sites permitted to re-derive inside the swept packages, as
#: ``"<path>::<line>"``. Empty: every instrument reads the record. An entry here
#: needs a reason in the PR that adds it.
_ALLOWED_REDERIVATIONS: Final[frozenset[str]] = frozenset()


def _callee_name(func: ast.expr) -> str | None:
    """The bare callee name, through an attribute access (``mod.fn`` -> ``fn``)."""

    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def record_free_rederivations(source: str) -> list[int]:
    """Line numbers of the record-free ``detect_contradictions`` calls in ``source``.

    A call is reported when its callee resolves to ``detect_contradictions``, it
    passes no ``**kwargs``, and its keyword set is exactly ``{"roster"}`` -- the
    shape that reaches the detector with every grounding channel defaulted to
    ``None``. A call that threads any record channel (``trigger_kind``,
    ``vent_witness_records``, ``move_witness_records``, ``sighting_records``) is
    reconstructing the recording rather than discarding it and is never
    reported; so is a bare call with no keywords at all, which cannot be a
    roster-scoped instrument read.
    """

    found: list[int] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        if _callee_name(node.func) != "detect_contradictions":
            continue
        if any(keyword.arg is None for keyword in node.keywords):
            continue  # **kwargs: the keyword set is not statically known
        if {keyword.arg for keyword in node.keywords} == {"roster"}:
            found.append(node.lineno)
    return found


def test_no_eval_or_training_module_re_derives_a_recorded_census() -> None:
    offenders: list[str] = []
    for package in _SWEPT_PACKAGES:
        for path in sorted((_REPO_ROOT / package).rglob("*.py")):
            relative = path.relative_to(_REPO_ROOT)
            for line in record_free_rederivations(path.read_text(encoding="utf-8")):
                site = f"{relative}::{line}"
                if site not in _ALLOWED_REDERIVATIONS:
                    offenders.append(site)
    assert offenders == [], (
        "an instrument must read the RECORDED contradictions "
        "(eval.meeting_quality.recorded_contradiction_flags), never re-derive "
        f"them from the transcript alone: {offenders}"
    )


def test_the_allowlist_is_empty() -> None:
    # An allowlist that grows to cover the sites the gate was written to forbid
    # is prose. If an entry is ever needed it comes with a PR reason, and this
    # assertion is what forces that conversation.
    assert _ALLOWED_REDERIVATIONS == frozenset()


def test_the_gate_bites_on_a_planted_rederivation(tmp_path: Path) -> None:
    # The perturbation: a module carrying exactly the record-free shape must be
    # REPORTED, or the sweep above is prose.
    planted = tmp_path / "planted_instrument.py"
    planted.write_text(
        "from meetings.transcript import detect_contradictions\n"
        "\n"
        "\n"
        "def census(meeting):\n"
        "    roster = frozenset(b.voter for b in meeting.ballots)\n"
        "    return len(detect_contradictions(meeting.transcript, roster=roster))\n",
        encoding="utf-8",
    )

    assert record_free_rederivations(planted.read_text(encoding="utf-8")) == [6]


def test_the_gate_bites_through_a_module_qualified_call(tmp_path: Path) -> None:
    # The evasion a bare-name match invites: reach the detector through its
    # module. The attribute spelling is the same defect and is reported too.
    qualified = tmp_path / "qualified_instrument.py"
    qualified.write_text(
        "from meetings import transcript\n"
        "\n"
        "\n"
        "def census(meeting, roster):\n"
        "    return transcript.detect_contradictions(\n"
        "        meeting.transcript, roster=roster\n"
        "    )\n",
        encoding="utf-8",
    )

    assert record_free_rederivations(qualified.read_text(encoding="utf-8")) == [5]


def test_the_gate_leaves_a_threaded_reconstruction_alone(tmp_path: Path) -> None:
    # The discrimination half: a call that threads the record channels is
    # reconstructing the recording, not discarding it. Reporting it would make
    # the gate a ban on the detector's name.
    threaded = tmp_path / "threaded_instrument.py"
    threaded.write_text(
        "from meetings.transcript import detect_contradictions\n"
        "\n"
        "\n"
        "def census(meeting, roster, vents, moves, sightings):\n"
        "    return detect_contradictions(\n"
        "        meeting.transcript,\n"
        "        roster=roster,\n"
        "        trigger_kind=meeting.trigger,\n"
        "        vent_witness_records=vents,\n"
        "        move_witness_records=moves,\n"
        "        sighting_records=sightings,\n"
        "    )\n",
        encoding="utf-8",
    )

    assert record_free_rederivations(threaded.read_text(encoding="utf-8")) == []
