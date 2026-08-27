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
``detect_contradictions`` call that does not thread ALL THREE private grounding
channels.

Requiring all three, rather than banning one known-bad keyword shape, is what
makes the gate hold. The defect is the ABSENCE of the channels, so every way of
spelling that absence has to fail: ``roster=`` alone, a bare call with no
keywords at all, positional arguments, and a partial thread that supplies
``trigger_kind=`` while still leaving the private channels defaulted to
``None``. A ``**kwargs`` splat is reported too -- the gate cannot see what it
contains, and a check that waves through what it cannot verify is not a check.

The walk is restricted to those two packages by construction, not by an
allowlist. ``audits/workflows/extract_gameplay_facts.py`` re-derives on purpose
-- a counterfactual is exactly what it is for -- and lives outside the swept
roots, so no entry can rot into covering the sites this gate forbids.
``scripts/counterfactual_phase20.py`` is outside the roots too and would be
clean anyway: it threads all three channels (only ``trigger_kind`` is left off,
deliberately). The allowlist below is empty and is expected to stay that way.

The gate ships with planted counter-cases in a temp tree for every shape of the
absence above, plus a fully-threaded reconstruction asserted clean by the same
predicate, so it discriminates on the channels rather than on the function name.
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

#: The private grounding channels the recording-time call held. A caller that
#: threads all three is reconstructing the recording; one that omits any of them
#: is scoring a different game, whatever else it passes.
_RECORD_CHANNELS: Final[frozenset[str]] = frozenset(
    {"vent_witness_records", "move_witness_records", "sighting_records"}
)


def _callee_name(func: ast.expr) -> str | None:
    """The bare callee name, through an attribute access (``mod.fn`` -> ``fn``)."""

    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def record_free_rederivations(source: str) -> list[int]:
    """Line numbers of the record-free ``detect_contradictions`` calls in ``source``.

    A call whose callee resolves to ``detect_contradictions`` is reported unless
    it threads every name in :data:`_RECORD_CHANNELS` as an explicit keyword.
    That is the whole rule, and it is deliberately about what is PRESENT: the
    defect is the absent grounding, so ``roster=`` alone, a bare call, a
    positional call and a partial thread that stops at ``trigger_kind=`` all
    fail the same way rather than needing a pattern each.

    A ``**kwargs`` splat is reported: its contents are not statically knowable,
    and a gate that passes what it cannot verify is prose. Spell the channels,
    or add the site to :data:`_ALLOWED_REDERIVATIONS` with a reason.
    """

    found: list[int] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        if _callee_name(node.func) != "detect_contradictions":
            continue
        threaded = {keyword.arg for keyword in node.keywords if keyword.arg is not None}
        if not _RECORD_CHANNELS <= threaded:
            found.append(node.lineno)
    return found


def test_no_eval_or_training_module_re_derives_a_recorded_census() -> None:
    offenders: list[str] = []
    walked = 0
    for package in _SWEPT_PACKAGES:
        for path in sorted((_REPO_ROOT / package).rglob("*.py")):
            walked += 1
            relative = path.relative_to(_REPO_ROOT)
            for line in record_free_rederivations(path.read_text(encoding="utf-8")):
                site = f"{relative}::{line}"
                if site not in _ALLOWED_REDERIVATIONS:
                    offenders.append(site)
    # Non-vacuity: a mistyped package name would make rglob find nothing and the
    # sweep pass on an empty walk while the planted cases below stayed green.
    assert walked > 50, f"the sweep only reached {walked} modules — check the roots"
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


def test_the_gate_bites_on_a_partially_threaded_call(tmp_path: Path) -> None:
    # The near-miss a keyword-set match would wave through: the caller threads
    # the trigger kind, which looks like reconstruction work, while all three
    # private channels stay defaulted to None. The census is just as record-free
    # as the roster-only shape, so it is reported the same way.
    partial = tmp_path / "partial_instrument.py"
    partial.write_text(
        "from meetings.transcript import detect_contradictions\n"
        "\n"
        "\n"
        "def census(meeting, roster):\n"
        "    return detect_contradictions(\n"
        "        meeting.transcript,\n"
        "        roster=roster,\n"
        "        trigger_kind=meeting.trigger,\n"
        "        vent_witness_records=None,\n"
        "    )\n",
        encoding="utf-8",
    )

    assert record_free_rederivations(partial.read_text(encoding="utf-8")) == [5]


def test_the_gate_bites_on_a_bare_and_a_positional_call(tmp_path: Path) -> None:
    # Absence spelled two more ways: no keywords at all, and the arguments
    # passed positionally. Both reach the detector with every grounding channel
    # defaulted, so a rule about what is PRESENT catches them without needing a
    # pattern for each.
    bare = tmp_path / "bare_instrument.py"
    bare.write_text(
        "from meetings.transcript import detect_contradictions\n"
        "\n"
        "\n"
        "def census(meeting, roster):\n"
        "    a = detect_contradictions(meeting.transcript)\n"
        "    b = detect_contradictions(meeting.transcript, roster)\n"
        "    return len(a) + len(b)\n",
        encoding="utf-8",
    )

    assert record_free_rederivations(bare.read_text(encoding="utf-8")) == [5, 6]


def test_the_gate_bites_on_a_kwargs_splat(tmp_path: Path) -> None:
    # A splat hides its contents from the walk. Waving it through would leave
    # the one evasion that needs no new spelling at all, so the gate reports it
    # and the caller either spells the channels or takes an allowlist entry.
    splat = tmp_path / "splat_instrument.py"
    splat.write_text(
        "from meetings.transcript import detect_contradictions\n"
        "\n"
        "\n"
        "def census(meeting, **channels):\n"
        "    return detect_contradictions(meeting.transcript, **channels)\n",
        encoding="utf-8",
    )

    assert record_free_rederivations(splat.read_text(encoding="utf-8")) == [5]


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


def test_the_gate_leaves_the_counterfactual_shape_alone(tmp_path: Path) -> None:
    # The calibration this rule is set to: ``scripts/counterfactual_phase20.py``
    # threads all three private channels and deliberately leaves ``trigger_kind``
    # off. It lives outside the swept roots, but the predicate must not depend on
    # that — a gate keyed on trigger_kind would ban the repo's own best
    # reconstruction the moment anyone moved it.
    counterfactual = tmp_path / "counterfactual_instrument.py"
    counterfactual.write_text(
        "from meetings.transcript import detect_contradictions\n"
        "\n"
        "\n"
        "def census(meeting, roster, vents, moves, sightings):\n"
        "    return detect_contradictions(\n"
        "        meeting.transcript,\n"
        "        roster=roster,\n"
        "        vent_witness_records=vents,\n"
        "        move_witness_records=moves,\n"
        "        sighting_records=sightings,\n"
        "    )\n",
        encoding="utf-8",
    )

    assert record_free_rederivations(counterfactual.read_text(encoding="utf-8")) == []
