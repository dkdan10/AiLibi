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
``detect_contradictions`` call that does not SUPPLY all three private grounding
channels.

Requiring all three, rather than banning one known-bad keyword shape, is what
makes the gate hold. The defect is the ABSENCE of the channels, so every way of
spelling that absence has to fail: ``roster=`` alone, a bare call with no
keywords at all, positional arguments, a partial thread that supplies
``trigger_kind=`` while leaving the private channels defaulted, and the channel
keywords spelled but assigned the literal ``None`` -- which the detector reads
as an absent channel, so it grounds nothing while looking like compliance. A
``**kwargs`` splat is reported too: the gate cannot see what it contains, and a
check that waves through what it cannot verify is not a check.

The walk is restricted to those two packages by construction, not by an
allowlist. ``audits/workflows/extract_gameplay_facts.py`` re-derives on purpose
-- a counterfactual is exactly what it is for -- and lives outside the swept
roots, so no entry can rot into covering the sites this gate forbids.
``scripts/counterfactual_phase20.py`` is outside the roots too and would be
clean anyway: it threads all three channels (only ``trigger_kind`` is left off,
deliberately). The recorded-input allowlist below remains empty. The reasoning
scorecard also contains synthetic detector probes, classified narrowly by their
module, function, direct fixture builder, literal Boolean input and explicit
candidate/legacy profile. This does not exempt its recorded-corpus analysis or
any other detector call in the same function.

The gate ships with planted counter-cases in a temp tree for every shape of the
absence above, plus a fully-threaded reconstruction asserted clean by the same
predicate, so it discriminates on the channels rather than on the function name.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Final

import pytest

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]

#: The packages whose instruments must read the record. Everything outside them
#: is free to re-derive; see the module docstring for why that is deliberate.
_SWEPT_PACKAGES: Final[tuple[str, ...]] = ("eval", "training")

#: Sites permitted to re-derive inside the swept packages, as
#: ``"<path>::<line>"``. Empty: every instrument reads the record. An entry here
#: needs a reason in the PR that adds it.
_ALLOWED_REDERIVATIONS: Final[frozenset[str]] = frozenset()

#: This offline probe constructs synthetic transcripts; it does not read a
#: recording. Its exact call/input shape is checked below, never the whole file.
_SYNTHETIC_PROBE_SCOPE: Final[tuple[str, str, str]] = (
    "eval/reasoning_evidence.py",
    "run_scorecard",
    "marker_fixture",
)

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


def _is_literal_none(value: ast.expr) -> bool:
    """Whether the argument is the literal ``None`` written at the call site.

    ``detect_contradictions`` reads ``None`` as an ABSENT channel, so spelling
    the keyword and assigning ``None`` grounds nothing — it only looks grounded.
    The gate has to judge the value, not the keyword name.
    """

    return isinstance(value, ast.Constant) and value.value is None


def _binds_name(node: ast.AST, name: str) -> bool:
    """Conservatively recognize binding/shadowing, including non-Name targets."""

    if isinstance(node, ast.Name):
        return node.id == name and isinstance(node.ctx, ast.Store | ast.Del)
    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
        return node.name == name
    if isinstance(node, ast.arg):
        return node.arg == name
    if isinstance(node, ast.alias):
        return (node.asname or node.name.split(".")[0]) == name
    if isinstance(node, ast.ExceptHandler | ast.MatchAs | ast.MatchStar):
        return node.name == name
    if isinstance(node, ast.MatchMapping):
        return node.rest == name
    if isinstance(node, ast.Global | ast.Nonlocal):
        return name in node.names
    return False


def _is_synthetic_probe(
    call: ast.Call, *, source_path: str, parents: dict[ast.AST, ast.AST]
) -> bool:
    """Recognize only the reviewed fixture/profile call, with no recorded input.

    This is a structural scope check, not arbitrary Python value analysis. A
    fixture supplied through a variable, a splat, or a nonliteral configuration
    is refused. The one permitted loop binds its input directly to False/True
    and cannot rebind it. Local shadowing of the fixture builder is also refused.
    """

    module, function, fixture_name = _SYNTHETIC_PROBE_SCOPE
    if source_path != module or len(call.args) != 1:
        return False
    if call.keywords and not (
        len(call.keywords) == 1
        and call.keywords[0].arg == "evidence_reasoning_version"
        and isinstance(call.keywords[0].value, ast.Constant)
        and type(call.keywords[0].value.value) is int
        and call.keywords[0].value.value == 1
    ):
        return False
    fixture = call.args[0]
    if not (
        isinstance(fixture, ast.Call)
        and isinstance(fixture.func, ast.Name)
        and fixture.func.id == fixture_name
        and not fixture.args
        and len(fixture.keywords) == 1
        and fixture.keywords[0].arg == "injected"
    ):
        return False
    ancestors: list[ast.AST] = []
    node: ast.AST = call
    while node in parents:
        node = parents[node]
        ancestors.append(node)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            if node.name != function or any(
                _binds_name(child, fixture_name) for child in ast.walk(node)
            ):
                return False
            break
    else:
        return False
    value = fixture.keywords[0].value
    if isinstance(value, ast.Constant) and type(value.value) is bool:
        return True
    if not isinstance(value, ast.Name):
        return False
    for ancestor in ancestors:
        if not (
            isinstance(ancestor, ast.For)
            and isinstance(ancestor.target, ast.Name)
            and ancestor.target.id == value.id
        ):
            continue
        # The nearest binding owns the value. An outer literal loop cannot
        # excuse an inner record-derived loop or any rebinding in its body.
        return (
            isinstance(ancestor.iter, ast.Tuple)
            and len(ancestor.iter.elts) == 2
            and all(
                isinstance(item, ast.Constant) and type(item.value) is bool
                for item in ancestor.iter.elts
            )
            and not any(
                _binds_name(child, value.id)
                for statement in ancestor.body
                for child in ast.walk(statement)
            )
        )
    return False


def record_free_rederivations(source: str, *, source_path: str = "") -> list[int]:
    """Line numbers of the record-free ``detect_contradictions`` calls in ``source``.

    A call whose callee resolves to ``detect_contradictions`` is reported unless
    it SUPPLIES every name in :data:`_RECORD_CHANNELS` — spelled as a keyword
    AND given something other than the literal ``None``, which the detector
    reads as an absent channel. That is the whole rule, and it is deliberately
    about what is present: the defect is the absent grounding, so ``roster=``
    alone, a bare call, a positional call, a partial thread that stops at
    ``trigger_kind=``, and all three channels spelled but set to ``None`` fail
    the same way rather than needing a pattern each.

    A ``**kwargs`` splat is reported: its contents are not statically knowable,
    and a gate that passes what it cannot verify is prose. Spell the channels,
    or add the site to :data:`_ALLOWED_REDERIVATIONS` with a reason.

    A channel bound to a NAME the walk cannot resolve counts as supplied: the
    gate is a structural check on the call site, not a value analysis, and the
    committed reconstructions all pass names. Only the literal ``None`` — the
    one spelling that is provably absent from the source alone — is refused.
    Only the explicitly scoped synthetic fixture probe is classified separately;
    recorded inputs remain subject to exactly the same channel requirement.
    """

    found: list[int] = []
    tree = ast.parse(source)
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _callee_name(node.func) != "detect_contradictions":
            continue
        supplied = {
            keyword.arg
            for keyword in node.keywords
            if keyword.arg is not None and not _is_literal_none(keyword.value)
        }
        if not _RECORD_CHANNELS <= supplied and not _is_synthetic_probe(
            node, source_path=source_path, parents=parents
        ):
            found.append(node.lineno)
    return found


def test_no_eval_or_training_module_re_derives_a_recorded_census() -> None:
    offenders: list[str] = []
    walked = 0
    for package in _SWEPT_PACKAGES:
        for path in sorted((_REPO_ROOT / package).rglob("*.py")):
            walked += 1
            relative = path.relative_to(_REPO_ROOT)
            for line in record_free_rederivations(
                path.read_text(encoding="utf-8"), source_path=relative.as_posix()
            ):
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


def test_only_actual_synthetic_scorecard_calls_are_classified() -> None:
    module, _, _ = _SYNTHETIC_PROBE_SCOPE
    source = (_REPO_ROOT / module).read_text(encoding="utf-8")
    # Both the candidate Boolean loop and legacy literal control need the exact
    # scope. The same source in an ordinary census module gets no exemption.
    assert len(record_free_rederivations(source)) == 2
    assert record_free_rederivations(source, source_path=module) == []
    assert len(record_free_rederivations(source, source_path="eval/census.py")) == 2


@pytest.mark.parametrize("injected", ["True", "False"])
@pytest.mark.parametrize("profile", ["", ", evidence_reasoning_version=1"])
def test_literal_synthetic_profiles_are_classified(injected: str, profile: str) -> None:
    source = (
        "def run_scorecard(root):\n"
        f"    return detect_contradictions(marker_fixture(injected={injected}){profile})\n"
    )
    assert (
        record_free_rederivations(source, source_path="eval/reasoning_evidence.py")
        == []
    )


@pytest.mark.parametrize(
    "statement",
    [
        "detect_contradictions(meeting.transcript)",
        "detect_contradictions(marker_fixture(injected=meeting.injected))",
        "detect_contradictions(marker_fixture(injected=unknown))",
        "detect_contradictions(marker_fixture(**meeting.settings))",
        "detect_contradictions(marker_fixture(injected=True), **meeting.settings)",
        "detect_contradictions(marker_fixture(injected=True), evidence_reasoning_version=True)",
        "detect_contradictions(marker_fixture(injected=True), evidence_reasoning_version=version)",
    ],
)
def test_synthetic_scope_still_refuses_recorded_or_unknown_inputs(
    statement: str,
) -> None:
    source = f"def run_scorecard(meeting):\n    return {statement}\n"
    assert record_free_rederivations(
        source, source_path="eval/reasoning_evidence.py"
    ) == [2]


def test_other_functions_in_the_scorecard_are_not_exempt() -> None:
    source = (
        "def census(meeting):\n"
        "    return detect_contradictions(marker_fixture(injected=True))\n"
    )
    assert record_free_rederivations(
        source, source_path="eval/reasoning_evidence.py"
    ) == [2]


def test_record_derived_loop_does_not_qualify_as_a_synthetic_probe() -> None:
    source = (
        "def run_scorecard(meeting):\n"
        "    for injected in (False, meeting.injected):\n"
        "        detect_contradictions(marker_fixture(injected=injected))\n"
    )
    assert record_free_rederivations(
        source, source_path="eval/reasoning_evidence.py"
    ) == [3]


@pytest.mark.parametrize(
    "body",
    [
        "injected = meeting.injected\n        ",
        "for injected in meeting.values:\n            ",
        "with meeting as injected:\n            ",
        "import meeting_data as injected\n        ",
        "if (injected := meeting.injected):\n            ",
    ],
)
def test_recorded_rebinding_inside_literal_loop_is_refused(body: str) -> None:
    source = (
        "def run_scorecard(meeting):\n"
        "    for injected in (False, True):\n"
        f"        {body}detect_contradictions(marker_fixture(injected=injected))\n"
    )
    assert (
        len(record_free_rederivations(source, source_path="eval/reasoning_evidence.py"))
        == 1
    )


def test_locally_replaced_fixture_builder_is_refused() -> None:
    source = (
        "def run_scorecard(meeting):\n"
        "    marker_fixture = lambda **kwargs: meeting.transcript\n"
        "    detect_contradictions(marker_fixture(injected=True))\n"
    )
    assert record_free_rederivations(
        source, source_path="eval/reasoning_evidence.py"
    ) == [3]


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


def test_the_gate_bites_on_channels_spelled_but_set_to_none(tmp_path: Path) -> None:
    # The evasion a name-only check invites, and the one that would look most
    # like compliance in review: all three channels spelled, every one of them
    # None. The detector reads None as an absent channel, so this call performs
    # exactly the record-free reconstruction the gate exists to forbid.
    nulled = tmp_path / "nulled_instrument.py"
    nulled.write_text(
        "from meetings.transcript import detect_contradictions\n"
        "\n"
        "\n"
        "def census(meeting, roster):\n"
        "    return detect_contradictions(\n"
        "        meeting.transcript,\n"
        "        roster=roster,\n"
        "        trigger_kind=meeting.trigger,\n"
        "        vent_witness_records=None,\n"
        "        move_witness_records=None,\n"
        "        sighting_records=None,\n"
        "    )\n",
        encoding="utf-8",
    )

    assert record_free_rederivations(nulled.read_text(encoding="utf-8")) == [5]


def test_the_gate_bites_when_one_channel_alone_is_nulled(tmp_path: Path) -> None:
    # The subtler half: two channels really supplied, one quietly None. The
    # census is still missing a channel, so it is still a different game.
    partly_nulled = tmp_path / "partly_nulled_instrument.py"
    partly_nulled.write_text(
        "from meetings.transcript import detect_contradictions\n"
        "\n"
        "\n"
        "def census(meeting, roster, vents, moves):\n"
        "    return detect_contradictions(\n"
        "        meeting.transcript,\n"
        "        roster=roster,\n"
        "        vent_witness_records=vents,\n"
        "        move_witness_records=moves,\n"
        "        sighting_records=None,\n"
        "    )\n",
        encoding="utf-8",
    )

    assert record_free_rederivations(partly_nulled.read_text(encoding="utf-8")) == [5]


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
