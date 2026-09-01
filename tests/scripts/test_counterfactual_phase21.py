"""Pins for the Phase-21 offline counterfactual and the memo it publishes.

Five things are pinned, each with a case proving it bites:

1. **The slate.** Three Wave-2 keys with the file-swapping arm OFF, every one of
   them still a live toggle that reads OFF under an empty environment. A fourth
   key is refused.
2. **The guard, in both environments.** A graduated lever refuses; a stale
   ``AILIBI_*`` export in the ambient process refuses and names the variable.
   Planted cases point the guard at an already-graduated key and at the live
   toggle, so the refusal is a real predicate over the live registry.
3. **Environment purity.** The process environment is byte-identical across a
   whole run and the ambient snapshot still reports every Wave-2 key OFF
   afterwards.
4. **The OFF column IS the committed record.** The fast slice's OFF cells equal
   the record audit's published cells and the committed instrument pins, and the
   four corroboration cells FIRST become an assertion here.
5. **The memo cannot drift from the instrument.** Every table row in
   ``audits/audit-phase-21-counterfactual.md`` is parsed and compared against a
   live four-set run, and the memo carries no bar, no target and no decision
   rule. A perturbed copy of the memo proves both checks bite.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final

import pytest

from orchestrator.replay import (
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    env_var_for_lever,
    substrate_flag_snapshot,
)

import counterfactual_phase21 as cf

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
_MEMO: Final[Path] = _REPO_ROOT / "audits" / "audit-phase-21-counterfactual.md"
_FAST_SET: Final[str] = "samples/4p1i"

# A lever the tree already graduated, used as the planted case for the
# graduation half of the guard.
_GRADUATED_LEVER: Final[str] = "reporter_exculpation"

# Every table row the memo publishes: ``| p-N | cell | a | b | c |`` for a
# per-set row and ``| cell | a | b | c |`` for a pooled one. A cell id is a
# letter, a dash, digits and an optional suffix letter.
_CELL_ID: Final[re.Pattern[str]] = re.compile(r"^[A-Z]-\d+[a-z]?$")
_PAIR: Final[re.Pattern[str]] = re.compile(r"^(\d+)/(\d+)")

# The vocabulary a bar, a target or a decision rule is written in. The memo
# precedes the pre-registration in the DAG, so none of it may appear.
_BAR_WORDS: Final[tuple[str, ...]] = (
    "the bar is",
    "the target is",
    "must reach",
    "must exceed",
    "must remain below",
    "must remain above",
    "must stay below",
    "must stay above",
    "pass/fail",
    "we will accept if",
    "the decision rule is",
)

# A decision the memo is not the document to make.
_DECISION_VERB: Final[re.Pattern[str]] = re.compile(
    r"\b(?:adopt|reject|abandon|ship|accept|stop|gate)\b\s+"
    r"(?:only\s+)?(?:if|when|unless|on)\b"
)

# A published cell id followed closely by a comparison — a threshold attached to
# a Wave-2 cell, whatever words surround it. Deliberately NOT triggered by bare
# "below"/"above", which the memo uses for cross-references.
_CELL_THRESHOLD: Final[re.Pattern[str]] = re.compile(
    r"\b[A-Z]-\d+[a-z]?\b[^|\n]{0,40}?"
    r"(?:>=|<=|>|<|≥|≤|\bat least\b|\bat most\b|\bno more than\b|\bno fewer than\b)"
)


# --------------------------------------------------------------------------- #
# 1. The slate.                                                                #
# --------------------------------------------------------------------------- #


def test_the_slate_is_the_three_wave_2_levers() -> None:
    assert cf.WAVE_2_LEVERS == (
        "reporter_reasoning",
        "corroboration_discipline",
        "testimony_shapes",
    )
    # The file-swapping arm is a live toggle and is deliberately NOT priced: it
    # serves a body neither sibling's block reaches.
    assert cf.NON_WAVE_2_LEVER in TOGGLEABLE_SUBSTRATE_FLAG_KEYS
    assert cf.NON_WAVE_2_LEVER not in cf.WAVE_2_LEVERS
    assert set(cf.WAVE_2_LEVERS) <= set(TOGGLEABLE_SUBSTRATE_FLAG_KEYS)


def test_every_priced_lever_reads_off_under_an_empty_env() -> None:
    # The premise of the whole table, asserted rather than assumed: passing an
    # empty env -- the OFF leg's own argument -- returns False for all three.
    snapshot = substrate_flag_snapshot({})
    assert [snapshot[key] for key in cf.WAVE_2_LEVERS] == [False, False, False]


def test_a_fourth_key_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cf, "WAVE_2_LEVERS", (*cf.WAVE_2_LEVERS, cf.NON_WAVE_2_LEVER))
    with pytest.raises(SystemExit) as excinfo:
        cf._assert_slate_is_the_three_wave_2_keys()
    assert "accusation_round.j2" in str(excinfo.value)


# --------------------------------------------------------------------------- #
# 2. The guard, in both environments.                                          #
# --------------------------------------------------------------------------- #


def test_the_guard_passes_on_the_live_slate() -> None:
    # Not an unconditional raise: on the slate this build actually carries, the
    # guard is silent.
    cf._assert_live_slate("in the live case")


def test_the_guard_refuses_a_graduated_lever(monkeypatch: pytest.MonkeyPatch) -> None:
    # The planted case: point the guard at a key the tree already graduated and
    # the refusal fires, names the lever, names its variable, and says where the
    # frozen memo lives.
    monkeypatch.setattr(cf, "WAVE_2_LEVERS", (_GRADUATED_LEVER,))
    with pytest.raises(SystemExit) as excinfo:
        cf._assert_live_slate("in the planted case")
    message = str(excinfo.value)
    assert "the OFF column cannot be produced in the planted case" in message
    assert _GRADUATED_LEVER in message
    assert env_var_for_lever(_GRADUATED_LEVER) in message
    assert "audits/audit-phase-21-counterfactual.md" in message


def test_the_guard_refuses_a_stale_ambient_export(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The load-bearing half. Seven consumers re-derive the meeting reduction
    # with no env argument, so a stale export would make every IMPORTED
    # instrument's OFF column an ON column while the empty-mapping check above
    # sailed through green.
    variable = env_var_for_lever("testimony_shapes")
    monkeypatch.setenv(variable, "1")
    assert substrate_flag_snapshot({})["testimony_shapes"] is False
    with pytest.raises(SystemExit) as excinfo:
        cf._assert_live_slate("in the stale-export case")
    message = str(excinfo.value)
    assert "the ambient environment is not the record's substrate" in message
    assert variable in message
    assert "Unset" in message


# --------------------------------------------------------------------------- #
# 3. Environment purity + the CLI contract, on the fast slice.                 #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def fast_run() -> dict[str, object]:
    """One run over the smallest committed set, reused by every fast pin."""

    return cf.run([_FAST_SET])


def test_a_whole_run_writes_nothing_to_the_environment() -> None:
    before = dict(os.environ)
    cf.run([_FAST_SET])
    assert dict(os.environ) == before
    ambient = substrate_flag_snapshot()
    assert [ambient[key] for key in cf.WAVE_2_LEVERS] == [False, False, False]


def test_the_cli_runs_one_set_and_prints_the_table(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cf.main(["--sets", _FAST_SET]) == 0
    printed = capsys.readouterr().out
    assert f"== {_FAST_SET}" in printed
    assert "== POOLED" in printed
    assert "RECORDED-OFF" in printed and "RECONSTRUCTED-OFF" in printed
    # The no-bar discipline reaches the terminal too.
    assert "writes no bar, no target and no decision rule" in printed


def test_the_cli_emits_the_same_table_as_json(
    capsys: pytest.CaptureFixture[str],
) -> None:
    import json

    assert cf.main(["--sets", _FAST_SET, "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["levers"] == list(cf.WAVE_2_LEVERS)
    assert payload["held_off"] == cf.NON_WAVE_2_LEVER
    assert _FAST_SET in payload["sets"]


def test_the_withhold_leg_names_a_wave_2_lever() -> None:
    with pytest.raises(SystemExit) as excinfo:
        cf.run([_FAST_SET], withhold="impostor_roll_call")
    assert "is not a Wave-2 lever" in str(excinfo.value)


# --------------------------------------------------------------------------- #
# 4. The OFF column IS the committed record.                                   #
# --------------------------------------------------------------------------- #


def test_the_off_column_equals_the_committed_record(
    fast_run: Mapping[str, object],
) -> None:
    block = _set_block(fast_run, _FAST_SET)
    assert block["innocent_ejections"] == cf.COMMITTED_INNOCENT_EJECTIONS[_FAST_SET]
    rows = {row["cell"]: row for row in block["rows"]}
    # Both OFF readings of the shared population agree, which is the premise
    # every ON number below rests on.
    assert rows["P-2"]["recorded_off"] == rows["P-2"]["reconstructed_off"]
    assert rows["P-2"]["recorded_off"][0] == cf.COMMITTED_INNOCENT_EJECTIONS[_FAST_SET]
    # The reporter instrument's own re-derivation is this lever's OFF column.
    assert rows["R-1"]["recorded_off"] == rows["R-1"]["reconstructed_off"]
    # No cell may print an ON value while its two OFF readings disagree.
    assert block["disagreeing_cells"] == []
    for row in block["rows"]:
        if row["recorded_off"] and row["reconstructed_off"]:
            assert row["recorded_off"] == row["reconstructed_off"], row["cell"]


def test_a_reconstruction_that_misses_the_record_refuses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The planted case for the OFF-equals-the-record gate: move the committed
    # pin and the run must refuse rather than publish an untraceable number.
    monkeypatch.setattr(
        cf,
        "COMMITTED_INNOCENT_EJECTIONS",
        {**cf.COMMITTED_INNOCENT_EJECTIONS, _FAST_SET: 999},
    )
    with pytest.raises(SystemExit) as excinfo:
        cf.run([_FAST_SET])
    message = str(excinfo.value)
    assert "DEFECT IN THIS SCRIPT" in message
    assert "audits/audit-phase-21-rerecord.md" in message


def test_the_impossible_transit_net_is_committed_and_labelled() -> None:
    # The verifier's ruling, executed rather than paraphrased: the regex lives
    # in the script, it catches the charge, and the paragraph under it says what
    # it is. An attribute docstring is not readable at runtime, so the source is.
    assert cf.IMPOSSIBLE_TRANSIT_PATTERN.search("that is a teleport, not a walk")
    assert cf.IMPOSSIBLE_TRANSIT_PATTERN.search("you cannot walk that in one tick")
    assert cf.IMPOSSIBLE_TRANSIT_PATTERN.search("p-4's story is impossible")
    assert not cf.IMPOSSIBLE_TRANSIT_PATTERN.search("p-4 was in Reactor at tick 3")
    source = Path(cf.__file__).read_text(encoding="utf-8")
    declaration = source.index("IMPOSSIBLE_TRANSIT_PATTERN: Final")
    assert "A JUDGMENT NET" in source[declaration : declaration + 2000]
    # And the memo quotes it as one wherever it appears.
    assert "JUDGMENT NET" in _MEMO.read_text(encoding="utf-8")


def test_the_ledger_row_names_its_judgment_tag_separately() -> None:
    row = cf.InjusticeLedgerRow(
        set_name="samples/4p1i",
        seed=1,
        meeting_index=0,
        meeting_id="m",
        victim="p-2",
        trigger_kind="body_report",
        tally={"p-2": 3},
        reporter_convicted=True,
        boomerang=False,
        impostor_rides=False,
        endgame=False,
        flagged=False,
        weak_flag_only=False,
        guard_redirected=False,
        impossible_transit=True,
    )
    assert row.tags == ("RC", "PIT")
    assert row.payload()["judgment_tag"] == "PIT"


# --------------------------------------------------------------------------- #
# 5. The memo cannot drift from the instrument, and carries no bar.            #
# --------------------------------------------------------------------------- #


def test_the_memo_declares_its_no_bar_status_in_its_opening() -> None:
    text = _MEMO.read_text(encoding="utf-8")
    opening = text.split("## ", 2)[0] + text.split("## ", 2)[1]
    assert "no bar" in opening.lower()
    assert "scripts/counterfactual_phase21.py" in text


def test_the_memo_attaches_no_threshold_to_a_wave_2_cell() -> None:
    assert _bar_language(_MEMO.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize(
    "planted",
    [
        "The bar is 0.60 non-direct accuracy; the decision rule is ADOPT.",
        "Adopt if R-3 >= 50%.",
        "R-3 must remain below 35.",
        "Reject when T-7 is nonzero.",
        "We abandon if C-1 <= 400/1525.",
        "R-4 at most 3%.",
        "Ship only if T-6 ≥ 100%.",
        "Gate on P-2 no more than 35.",
    ],
)
def test_the_no_bar_pin_bites_on_a_perturbed_memo(planted: str, tmp_path: Path) -> None:
    # The perturbed copies craft rule 2 asks for: eight spellings of a bar, each
    # of which must fail the check that says memos here carry none. A gate that
    # caught only the phrase this task happened to avoid would be prose.
    perturbed = tmp_path / "memo.md"
    perturbed.write_text(
        f"{_MEMO.read_text(encoding='utf-8')}\n\n{planted}\n", encoding="utf-8"
    )
    assert _bar_language(perturbed.read_text(encoding="utf-8")) != []


def _bar_language(text: str) -> list[str]:
    """Every bar, target or decision rule the memo's own DAG position forbids.

    Three nets, because one is a spelling and the invariant is semantic: the
    named phrases, a decision verb ("adopt if", "reject when", "abandon if"),
    and a published cell id followed closely by a comparison — which is what a
    threshold attached to a Wave-2 cell actually looks like.
    """

    lowered = text.lower()
    hits = [phrase for phrase in _BAR_WORDS if phrase in lowered]
    hits.extend(match.group(0) for match in _DECISION_VERB.finditer(lowered))
    hits.extend(match.group(0) for match in _CELL_THRESHOLD.finditer(text))
    return hits


def test_the_memo_table_parses_into_rows() -> None:
    per_set, pooled = _memo_tables()
    assert pooled, "the memo publishes no pooled table"
    assert per_set, "the memo publishes no per-set rows"
    assert {name for name, _ in per_set} == set(cf.CANONICAL_SETS)


def test_the_table_comparison_bites_on_a_perturbed_memo(tmp_path: Path) -> None:
    # Perturb ONE published value and the parse must differ from the original,
    # which is what makes the four-set comparison below a real gate.
    original_per_set, original_pooled = _memo_tables()
    perturbed = tmp_path / "memo.md"
    perturbed.write_text(
        _perturb_first_published_value(_MEMO.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    parsed_per_set, parsed_pooled = _parse_tables(perturbed.read_text(encoding="utf-8"))
    assert (parsed_per_set, parsed_pooled) != (original_per_set, original_pooled)


def _perturb_first_published_value(text: str) -> str:
    """Move the numerator of the first published table row by one."""

    lines = text.splitlines()
    for index, line in enumerate(lines):
        fields = [field.strip() for field in line.strip().strip("|").split("|")]
        if len(fields) != 5:
            continue
        if not (
            _CELL_ID.match(fields[0])
            or (fields[0] in cf.CANONICAL_SETS and _CELL_ID.match(fields[1]))
        ):
            continue
        match = _PAIR.match(fields[2])
        if match is None:
            continue
        bumped = f"{int(match.group(1)) + 1}/{match.group(2)}"
        fields[2] = bumped
        lines[index] = "| " + " | ".join(fields) + " |"
        return "\n".join(lines) + "\n"
    raise AssertionError("the memo publishes no parseable table row to perturb")


def test_the_pooled_on_column_is_withdrawn_when_any_set_disagrees() -> None:
    """The aggregation half of the reconstruction-fidelity refusal.

    Withdrawing one set's ON pair is not enough: summing the sets that DID
    reproduce publishes a pooled row over a silently reduced denominator, which
    is the opposite of what the refusal exists to do. Planted both ways.
    """

    totals = {
        "X-1|l|recorded_off|n": 3,
        "X-1|l|recorded_off|d": 100,
        "X-1|l|on|n": 7,
        "X-1|l|on|d": 100,
    }
    kwargs: dict[str, Any] = {
        "key": "X-1|l",
        "cell_id": "X-1",
        "label": "l",
        "population": "p",
        "note": "n",
        "on_slate": "s",
        "totals": totals,
    }
    kept = cf._pooled_row(**kwargs, withdrawn=set())
    assert kept["on"] == [7, 100]
    assert kept["on_withdrawn"] is False

    pulled = cf._pooled_row(**kwargs, withdrawn={"X-1"})
    assert pulled["on"] is None
    assert pulled["on_withdrawn"] is True
    assert "WITHDRAWN" in str(pulled["note"])
    # The OFF columns survive: the reader still gets the record's own reading.
    assert pulled["recorded_off"] == [3, 100]


def test_the_advisory_label_keys_on_the_rows_own_denominator(
    fast_run: Mapping[str, object],
) -> None:
    block = _set_block(fast_run, _FAST_SET)
    rows = {row["cell"]: row for row in block["rows"]}
    # A cell read over a handful of turns is fragile however large the set is.
    assert rows["T-8"]["advisory"] is True
    # And a cell read over the whole ballot population is not.
    assert rows["C-9"]["advisory"] is False


def test_the_memo_marks_every_advisory_cell(fast_run: Mapping[str, object]) -> None:
    marked = _memo_advisory_cells()
    block = _set_block(fast_run, _FAST_SET)
    expected = {row["cell"] for row in block["rows"] if row["advisory"]}
    assert expected, "the fast slice flags no advisory row — the check is vacuous"
    assert {(_FAST_SET, cell) for cell in expected} <= marked


def test_the_advisory_marker_check_bites_on_a_stripped_memo(tmp_path: Path) -> None:
    # Drop the marker from ONE per-set row and the comparison must notice; the
    # gate is a per-cell join, not a "the memo mentions [ADV] somewhere" check.
    original = _memo_advisory_cells()
    assert original, "the memo marks no advisory cell — the check is vacuous"
    stripped = tmp_path / "memo.md"
    stripped.write_text(_strip_one_advisory_marker(), encoding="utf-8")
    parsed = _advisory_cells(stripped.read_text(encoding="utf-8"))
    assert parsed != original
    assert len(parsed) == len(original) - 1


def _strip_one_advisory_marker() -> str:
    lines = _MEMO.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        fields = [field.strip() for field in line.strip().strip("|").split("|")]
        if len(fields) == 5 and fields[0] in cf.CANONICAL_SETS:
            if cf.ADVISORY_MARK in line:
                lines[index] = line.replace(cf.ADVISORY_MARK, "")
                return "\n".join(lines) + "\n"
    raise AssertionError("the memo marks no per-set advisory cell to strip")


@pytest.mark.slow
def test_the_memo_table_equals_a_live_four_set_run() -> None:
    """The document cannot drift from the instrument.

    Every published row -- per set and pooled -- is re-derived here and compared
    against the memo's own table, as are the two censuses the memo publishes as
    tables of their own rather than as cell rows. This is also where the four
    corroboration cells become an assertion: Task 21.19 shipped a walk that
    prints them and deliberately asserts no figure.
    """

    payload = cf.run(list(cf.CANONICAL_SETS))
    pins = payload["corroboration_pins"]
    assert isinstance(pins, dict) and pins["checked"] is True
    for cell, expected in cf.COMMITTED_CORROBORATION_CELLS.items():
        assert tuple(pins["measured"][cell]) == expected, cell

    memo_per_set, memo_pooled = _memo_tables()
    live_per_set, live_pooled = _run_tables(payload)
    assert memo_pooled == live_pooled
    assert memo_per_set == live_per_set

    # The two prose tables that carry cells, against the pooled censuses the
    # payload now emits: nothing published exists only as hand-written prose.
    text = _MEMO.read_text(encoding="utf-8")
    ballots = payload["pooled_ballot_census"]
    assert isinstance(ballots, dict)
    assert _memo_citation_mix(text) == ballots["citation_mix"]
    testimony = payload["pooled_testimony_census"]
    assert isinstance(testimony, dict)
    assert _memo_kind_census(text) == (
        testimony["statements_off"],
        testimony["statements_on"],
    )

    # Every advisory cell the instrument flags carries its marker in the memo.
    sets = payload["sets"]
    assert isinstance(sets, dict)
    flagged = {
        (set_name, row["cell"])
        for set_name, block in sets.items()
        for row in block["rows"]
        if row["advisory"]
    }
    assert flagged <= _advisory_cells(text)


# --------------------------------------------------------------------------- #
# Helpers.                                                                     #
# --------------------------------------------------------------------------- #


def _set_block(payload: Mapping[str, object], set_name: str) -> Any:
    sets = payload["sets"]
    assert isinstance(sets, dict)
    return sets[set_name]


def _memo_tables() -> tuple[
    dict[tuple[str, str], tuple[Any, ...]], dict[str, tuple[Any, ...]]
]:
    return _parse_tables(_MEMO.read_text(encoding="utf-8"))


def _parse_tables(
    text: str,
) -> tuple[dict[tuple[str, str], tuple[Any, ...]], dict[str, tuple[Any, ...]]]:
    """Every published cell in the memo, keyed per set and pooled.

    Both tables are five columns whose last three are the value columns; a
    per-set row leads with the set directory and a pooled row with the cell id,
    so one parser reads both and the two tables cannot be written to different
    conventions.
    """

    per_set: dict[tuple[str, str], tuple[Any, ...]] = {}
    pooled: dict[str, tuple[Any, ...]] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        fields = [field.strip() for field in stripped.strip("|").split("|")]
        if len(fields) != 5:
            continue
        if fields[0] in cf.CANONICAL_SETS and _CELL_ID.match(fields[1]):
            per_set[(fields[0], fields[1])] = _values(fields[2:5])
        elif _CELL_ID.match(fields[0]):
            pooled[fields[0]] = _values(fields[2:5])
    return per_set, pooled


def _memo_advisory_cells() -> set[tuple[str, str]]:
    return _advisory_cells(_MEMO.read_text(encoding="utf-8"))


def _advisory_cells(text: str) -> set[tuple[str, str]]:
    """Every ``(set, cell)`` the memo's per-set tables mark advisory."""

    marked: set[tuple[str, str]] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or cf.ADVISORY_MARK not in stripped:
            continue
        fields = [field.strip() for field in stripped.strip("|").split("|")]
        if len(fields) == 5 and fields[0] in cf.CANONICAL_SETS:
            marked.add((fields[0], fields[1]))
    return marked


def _memo_citation_mix(text: str) -> dict[str, int]:
    """The §4.3 citation table, keyed by the census's own channel names."""

    names = {
        "hearsay": "hearsay",
        "own observation": "own_obs",
        "own turn": "own_turn",
        "another player's observation": "other_obs",
        "nothing": "none",
    }
    mix: dict[str, int] = {}
    for line in text.splitlines():
        fields = [field.strip() for field in line.strip().strip("|").split("|")]
        if len(fields) != 3 or fields[0] not in names:
            continue
        count = re.search(r"\*\*(\d+)\*\*", fields[1])
        assert count is not None, fields
        mix[names[fields[0]]] = int(count.group(1))
    return mix


def _memo_kind_census(text: str) -> tuple[dict[str, int], dict[str, int]]:
    """The §5.2 eight-kind reduction table, as ``(OFF, ON)`` counters."""

    off: dict[str, int] = {}
    on: dict[str, int] = {}
    for line in text.splitlines():
        fields = [field.strip() for field in line.strip().strip("|").split("|")]
        if len(fields) != 4:
            continue
        if not (fields[0].startswith("`") and fields[0].endswith("`")):
            continue
        off_value = _first_int(fields[1])
        on_value = _first_int(fields[2])
        if off_value is None or on_value is None:
            continue
        # A kind nobody ever spoke is absent from the census's counters, not
        # present at zero, so the memo's zeros are dropped the same way.
        kind = fields[0].strip("`")
        if off_value:
            off[kind] = off_value
        if on_value:
            on[kind] = on_value
    return off, on


def _first_int(field: str) -> int | None:
    match = re.search(r"(\d[\d,]*)", field)
    return int(match.group(1).replace(",", "")) if match else None


def _values(fields: list[str]) -> tuple[Any, ...]:
    return tuple(_value(field) for field in fields)


def _value(field: str) -> tuple[int, int] | None:
    match = _PAIR.match(field.replace(" ", "").replace(",", ""))
    if match is None:
        return None
    return (int(match.group(1)), int(match.group(2)))


def _run_tables(
    payload: Mapping[str, object],
) -> tuple[dict[tuple[str, str], tuple[Any, ...]], dict[str, tuple[Any, ...]]]:
    per_set: dict[tuple[str, str], tuple[Any, ...]] = {}
    sets = payload["sets"]
    assert isinstance(sets, dict)
    for set_name, block in sets.items():
        for row in block["rows"]:
            per_set[(set_name, row["cell"])] = _columns(row)
    pooled_rows = payload["pooled"]
    assert isinstance(pooled_rows, list)
    pooled = {row["cell"]: _columns(row) for row in pooled_rows}
    return per_set, pooled


def _columns(row: Mapping[str, object]) -> tuple[Any, ...]:
    return tuple(
        tuple(value) if isinstance(value, list) else None
        for value in (
            row["recorded_off"],
            row["reconstructed_off"],
            row["on"],
        )
    )
