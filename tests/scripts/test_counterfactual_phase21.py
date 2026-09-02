"""Pins for the Phase-21 offline counterfactual and the memo it publishes.

Six things are pinned, each with a case proving it bites:

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
5. **The memo cannot drift from the instrument.** Every published table in
   ``audits/audit-phase-21-counterfactual.md`` -- the cell rows per set and
   pooled, the injustice ledger with its recorded tallies and its class totals,
   the whole ballot census, all eight rows of the reduction census, every leg of
   the render census and the advisory markers -- is parsed and compared against
   a live four-set run, the size of each join included, and the memo carries no
   bar, no target and no decision rule. Perturbed copies prove each check bites,
   including a moved tally and a deleted zero-count row.
6. **The tripwire readers.** The elicitation marker is read off the shipped
   template and appears nowhere in the reader's own source; a spoken kill moves
   an impostor prompt's BYTES while offering it no block; a template whose
   crew-only guard is stripped takes T-9b off zero through the real walk; the
   first-meeting budget catches a difference the whole-run total nets away; and
   the spoken-kill split of bar 1's cell counts a planted conviction that the
   committed bytes, which hold no spoken kill, could never exercise.
"""

from __future__ import annotations

import functools
import os
import re
import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final

import pytest

from agents.strategic.prompts.loader import build_prompt_renderers
from meetings.schemas import (
    ContradictionRef,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    SawKillObservation,
)
from orchestrator.replay import (
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    env_var_for_lever,
    substrate_flag_snapshot,
)

import counterfactual_phase21 as cf

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
_MEMO: Final[Path] = _REPO_ROOT / "audits" / "audit-phase-21-counterfactual.md"
_FAST_SET: Final[str] = "samples/4p1i"

# A published table is never rewritten, so a figure that moves after publication
# is re-derived in an appended errata block. Rows the errata republishes are the
# authoritative pin; rows it does not are still pinned by the recorded table.
_ERRATA_HEADING: Final[str] = "## Errata"

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

# Every kind the reduction can carry. The memo advertises an eight-kind census,
# so the drift gate holds it to eight rows whatever the counts are.
_REPORTED_KINDS: Final[tuple[str, ...]] = (
    "saw_player",
    "saw_vent",
    "saw_kill",
    "whereabouts",
    "saw_move",
    "alibi",
    "accusation",
    "corroboration",
)

# The slate legs the memo publishes a render census for: the whole set the
# payload carries, so the join below is total rather than a sample.
_RENDER_LEGS: Final[frozenset[str]] = frozenset(
    {
        "OFF",
        *cf.WAVE_2_LEVERS,
        "all-three-ON",
        cf.decomposition_label("testimony_shapes"),
    }
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


@pytest.fixture(scope="module")
def full_run() -> dict[str, object]:
    """One four-set walk, shared by the memo drift gate and the cell pins."""

    return cf.run(list(cf.CANONICAL_SETS))


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


def test_the_census_comparisons_bite_on_a_perturbed_memo(tmp_path: Path) -> None:
    # The census joins are gates, not decoration: move one ballot-census figure
    # and one render-census figure and each parse must change.
    text = _MEMO.read_text(encoding="utf-8")
    ballots = _memo_ballot_census(text)
    render = _memo_render_census(text)
    assert ballots and render

    bent = tmp_path / "memo.md"
    bent.write_text(
        text.replace(
            "| impostor ballots that joined the pile | 40 |",
            "| impostor ballots that joined the pile | 41 |",
        ).replace(
            "| `corroboration_discipline` | `vote_ballot` | 3,631 |",
            "| `corroboration_discipline` | `vote_ballot` | 3,632 |",
        ),
        encoding="utf-8",
    )
    perturbed = bent.read_text(encoding="utf-8")
    assert _memo_ballot_census(perturbed) != ballots
    assert _memo_render_census(perturbed) != render


def test_an_erratum_overrides_the_row_it_republishes() -> None:
    # The fold, asserted on the memo as it stands rather than on a fixture: the
    # recorded §4.4 ballot row and the errata's disagree, and the errata's is
    # what the drift gate reads. A row no erratum republishes still comes from
    # the recorded table, so an errata block pins what it names and nothing else.
    text = _MEMO.read_text(encoding="utf-8")
    record, errata = _split_errata(text)
    assert errata, "the memo publishes an errata block; the fold below needs one"
    recorded = _memo_render_census(record)
    corrected = _memo_render_census(errata)
    folded = _published_render_census(text)
    ballot = ("corroboration_discipline", "vote_ballot")
    assert recorded[ballot] != corrected[ballot]
    assert folded[ballot] == corrected[ballot]
    untouched = ("reporter_reasoning", "accusation_round")
    assert folded[untouched] == recorded[untouched]


def test_a_memo_with_no_errata_folds_to_the_recorded_tables() -> None:
    # The "when present" half: strip the block and every parse is the record's,
    # so the mechanism adds no behaviour to a memo that has never been amended.
    record, _ = _split_errata(_MEMO.read_text(encoding="utf-8"))
    assert _published_render_census(record) == _memo_render_census(record)
    assert _published_tables(record) == _parse_tables(record)


@pytest.mark.parametrize(
    "planted",
    [
        (
            "| `corroboration_discipline` | `vote_ballot` | 3,631 | 3,614 | 26,522 |"
            " 5,676,313 |"
        ),
        "| B-3 | prose lines the slate ADDS, per rendered prompt | — | 0/7262 |"
        " 43537/7262 |",
        "| samples/9p2i | B-3 | — | 0/1738 | 10741/1738 |",
    ],
)
def test_a_wrong_erratum_cannot_pass_the_drift_gate(planted: str) -> None:
    # Craft rule 2 for the mechanism itself. The drift gate asserts the FOLDED
    # parse equals a live run, so an erratum that misstates a figure has to move
    # the fold — otherwise the errata block would be prose that pins nothing.
    # One planted row per published shape: the six-column census, a pooled cell,
    # a per-set cell.
    text = _MEMO.read_text(encoding="utf-8")
    assert text.count(planted) == 1, planted
    bent = text.replace(planted, _bump_last_number(planted))
    assert _published_parses(bent) != _published_parses(text)


def _published_parses(text: str) -> tuple[Any, ...]:
    """Everything the drift gate reads out of the memo, as one comparable value."""

    per_set, pooled = _published_tables(text)
    return (_published_render_census(text), per_set, pooled)


def _bump_last_number(row: str) -> str:
    """The row with its LAST integer moved by one — a one-digit drift."""

    matches = list(re.finditer(r"\d[\d,]*", row))
    assert matches, row
    last = matches[-1]
    moved = str(int(last.group(0).replace(",", "")) + 1)
    return f"{row[: last.start()]}{moved}{row[last.end() :]}"


def test_the_ledger_comparison_covers_the_recorded_tally(tmp_path: Path) -> None:
    # A row whose tags survive an edit to its vote tally is still a drifted row.
    text = _MEMO.read_text(encoding="utf-8")
    original = _memo_ledger_rows(text)
    assert original
    bent = tmp_path / "memo.md"
    bent.write_text(
        text.replace(
            "| samples/9p2i | 1 | m1 | p-5 | WEAKFLAG+REDIRECT | p-5 3, SKIP 2, p-1 1 |",
            "| samples/9p2i | 1 | m1 | p-5 | WEAKFLAG+REDIRECT | p-5 999, SKIP 2, p-1 1 |",
        ),
        encoding="utf-8",
    )
    assert _memo_ledger_rows(bent.read_text(encoding="utf-8")) != original


def test_a_deleted_testimony_kind_row_is_caught(tmp_path: Path) -> None:
    # The zero-count kinds are the ones a memo could quietly stop publishing,
    # so the gate holds the census to all eight rows rather than to its values.
    text = _MEMO.read_text(encoding="utf-8")
    assert set(_memo_kind_census(text)[0]) == set(_REPORTED_KINDS)
    bent = tmp_path / "memo.md"
    bent.write_text(
        "\n".join(
            line for line in text.splitlines() if not line.startswith("| `saw_kill` |")
        )
        + "\n",
        encoding="utf-8",
    )
    assert set(_memo_kind_census(bent.read_text(encoding="utf-8"))[0]) != set(
        _REPORTED_KINDS
    )


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
def test_the_memo_table_equals_a_live_four_set_run(
    full_run: Mapping[str, object],
) -> None:
    """The document cannot drift from the instrument.

    Every published row -- per set and pooled -- is re-derived here and compared
    against the memo's own table, as are the two censuses the memo publishes as
    tables of their own rather than as cell rows. This is also where the four
    corroboration cells become an assertion: Task 21.19 shipped a walk that
    prints them and deliberately asserts no figure.
    """

    payload = full_run
    pins = payload["corroboration_pins"]
    assert isinstance(pins, dict) and pins["checked"] is True
    for cell, expected in cf.COMMITTED_CORROBORATION_CELLS.items():
        assert tuple(pins["measured"][cell]) == expected, cell

    text = _MEMO.read_text(encoding="utf-8")
    memo_per_set, memo_pooled = _published_tables(text)
    live_per_set, live_pooled = _run_tables(payload)
    assert memo_pooled == live_pooled
    assert memo_per_set == live_per_set

    # Every published census, whole: nothing exists only as unchecked prose.
    # Each comparison asserts the SIZE of the join first, so a memo that simply
    # stopped publishing a field could not pass by publishing fewer rows.
    ballots = payload["pooled_ballot_census"]
    assert isinstance(ballots, dict)
    memo_ballots, live_ballots = (
        _memo_ballot_census(text),
        _flatten_ballot_census(ballots),
    )
    assert len(memo_ballots) == len(live_ballots) > 0
    assert memo_ballots == live_ballots

    testimony = payload["pooled_testimony_census"]
    assert isinstance(testimony, dict)
    memo_kinds = _memo_kind_census(text)
    assert set(memo_kinds[0]) == set(_REPORTED_KINDS), (
        "the memo advertises an eight-kind census and must publish all eight, "
        "including the ones nothing was ever spoken in"
    )
    assert memo_kinds == _run_kind_census(testimony)

    render = payload["pooled_render_census"]
    assert isinstance(render, dict)
    memo_render, live_render = (
        _published_render_census(text),
        _flatten_render_census(render),
    )
    assert len(memo_render) == len(live_render) > 0
    assert memo_render == live_render

    # The injustice ledger the memo lists row by row, and its class totals.
    memo_ledger = _memo_ledger_rows(text)
    assert len(memo_ledger) == len(_run_ledger_rows(payload)) > 0
    assert memo_ledger == _run_ledger_rows(payload)
    memo_totals = _memo_class_totals(text)
    assert len(memo_totals) == len(_totals(payload)) - 1 > 0
    assert memo_totals == {
        tag: count for tag, count in _totals(payload).items() if tag != "TOTAL"
    }

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


def _totals(payload: Mapping[str, object]) -> dict[str, int]:
    totals = payload["pooled_ledger_class_totals"]
    assert isinstance(totals, dict)
    return totals


# --------------------------------------------------------------------------- #
# 6. The tripwire readers the ratified pre-registration owed.                  #
# --------------------------------------------------------------------------- #

_PROMPT_SET: Final[str] = "qwen3_6_27b"
_PROMPTS_ROOT: Final[Path] = _REPO_ROOT / "agents" / "strategic" / "prompts"
_SHAPES_ON: Final[dict[str, str]] = {"AILIBI_TESTIMONY_SHAPES": "1"}
_CREW_GUARD: Final[str] = (
    "{% if testimony_shapes is defined and testimony_shapes and not is_impostor %}"
)

# One already-spoken witnessed kill, the shape the arm makes speakable.
_KILL_TURN: Final[MeetingTurn] = MeetingTurn(
    turn_id="m-1:turn-0",
    turn_index=0,
    speaker="p-4",
    turn_kind="opening",
    reply_to=None,
    observations=(
        SawKillObservation(type="saw_kill", tick=11, subject="p-8", room="ADMIN"),
    ),
    claims=(),
    free_text="I watched it happen.",
)


def _statement(
    *, env: Mapping[str, str], transcript: MeetingTranscript, is_impostor: bool
) -> str:
    return build_prompt_renderers(_PROMPT_SET, env=env).statement(
        agent_id="p-3",
        rendered_memory="(memory)",
        transcript=transcript,
        contradictions=(),
        prior_turn=None,
        turn_kind="reply",
        living_ids=("p-1", "p-2"),
        is_impostor=is_impostor,
    )


def _markers() -> frozenset[str]:
    return cf._RendererCache().elicitation_markers(_PROMPT_SET, "reply")


def test_the_elicitation_marker_is_read_off_the_shipped_template() -> None:
    # The reader must not carry a copy of a sentence the templates own: PR #420
    # re-worded this block, and a copied sentence would have gone on matching
    # nothing while reporting every crew turn as having lost the offer.
    markers = _markers()
    assert len(markers) == 2
    template = (_PROMPTS_ROOT / _PROMPT_SET / "accusation_round.j2").read_text(
        encoding="utf-8"
    )
    source = Path(cf.__file__).read_text(encoding="utf-8")
    for marker in markers:
        assert marker in template
        assert marker not in source
    # The reply and opt-in branches offer the same block, so one marker set
    # reads both -- asserted rather than assumed, because the reader keys on
    # the capture's own turn kind.
    assert cf._RendererCache().elicitation_markers(_PROMPT_SET, "opt_in") == markers


def test_a_spoken_kill_moves_the_impostor_bytes_but_offers_it_no_block() -> None:
    # The reason T5 needs a reader rather than a role split of T-9's byte diff.
    # A crew-spoken kill renders the role-blind PUBLIC-TRANSCRIPT row into every
    # later prompt, impostor prompts included, which is correct and pinned by
    # tests/agents/test_bespoke_prompt_sets.py. A role split of the byte diff
    # would read that as an impostor turn being offered the shape and STOP a
    # good record; the elicitation reader reads it as what it is.
    markers = _markers()
    spoken = MeetingTranscript(turns=(_KILL_TURN,))
    for is_impostor, offered in ((True, 0), (False, len(markers))):
        off = _statement(env={}, transcript=spoken, is_impostor=is_impostor)
        on = _statement(env=_SHAPES_ON, transcript=spoken, is_impostor=is_impostor)
        assert on != off, "the byte diff moves for BOTH roles"
        assert (
            cf.elicitation_lines_gained(off_prompt=off, on_prompt=on, markers=markers)
            == offered
        )


def test_only_what_the_arm_adds_counts_as_an_offer() -> None:
    # A sentence a speaker quoted into the transcript stands in both renders, so
    # presence is not an offer. Counting the difference is what makes the
    # impostor half a true zero rather than a substring search.
    marker = sorted(_markers())[0]
    assert (
        cf.elicitation_lines_gained(
            off_prompt=marker, on_prompt=marker, markers=frozenset({marker})
        )
        == 0
    )
    assert (
        cf.elicitation_lines_gained(
            off_prompt=marker, on_prompt=marker * 2, markers=frozenset({marker})
        )
        == 1
    )


def test_the_marker_derivation_refuses_when_the_arm_offers_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The planted case, and the plausible authoring slip rather than a contrived
    # one: a guard that tests only ``is defined`` is always true, because the
    # loader binds the kwarg on both paths. The block then renders with the arm
    # DOWN, so the ON render adds nothing and a reader that shrugged would
    # report every crew turn as missing the block -- an UNREAD tripwire read as
    # a failing one.
    scratch = tmp_path / _PROMPT_SET
    shutil.copytree(_PROMPTS_ROOT / _PROMPT_SET, scratch)
    body = (scratch / "accusation_round.j2").read_text(encoding="utf-8")
    leaked = body.replace(
        _CREW_GUARD, "{% if testimony_shapes is defined and not is_impostor %}"
    )
    assert leaked != body
    (scratch / "accusation_round.j2").write_text(leaked, encoding="utf-8")
    monkeypatch.setattr(
        cf,
        "build_prompt_renderers",
        functools.partial(build_prompt_renderers, root=tmp_path),
    )
    with pytest.raises(SystemExit) as excinfo:
        cf._RendererCache().elicitation_markers(_PROMPT_SET, "reply")
    assert "elicitation block" in str(excinfo.value)


def test_the_impostor_half_bites_on_a_breached_firewall(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The planted case for T5's NEVER-WORSE half, driven through the real walk
    # rather than through one render: strip ``and not is_impostor`` from the
    # crew-only guards -- the exact breach the tripwire exists to catch -- and
    # T-9b must leave zero. The OFF body is byte-identical either way, because
    # the guard's first conjunct is false with the arm down, so the walk still
    # reproduces the record and only the ON column moves.
    scratch = tmp_path / "prompts"
    shutil.copytree(_PROMPTS_ROOT, scratch)
    target = scratch / _PROMPT_SET / "accusation_round.j2"
    body = target.read_text(encoding="utf-8")
    breached = body.replace(
        _CREW_GUARD, "{% if testimony_shapes is defined and testimony_shapes %}"
    )
    assert breached != body
    target.write_text(breached, encoding="utf-8")
    monkeypatch.setattr(
        cf,
        "build_prompt_renderers",
        functools.partial(build_prompt_renderers, root=scratch),
    )
    rows = {
        row["cell"]: row
        for row in _set_block(cf.run([_FAST_SET]), _FAST_SET)["tripwire_rows"]
    }
    # Six of the 39 impostor speech prompts on this set are opt-in turns, which
    # is where the role-blind guard now reaches; the crew half is unmoved.
    assert rows["T-9b"]["on"][0] > 0
    assert rows["T-9a"]["on"] == [39, 39]


def test_a_block_that_renders_in_pieces_refuses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The block is one offer whose lines share a guard, so the reader counts it
    # as a unit. Plant a marker no template renders and the run must refuse
    # rather than silently count half an offer as none.
    real = cf._RendererCache.elicitation_markers

    def phantom(self: Any, set_name: str, turn_kind: str) -> frozenset[str]:
        return real(self, set_name, turn_kind) | {"a line no template renders"}

    monkeypatch.setattr(cf._RendererCache, "elicitation_markers", phantom)
    with pytest.raises(SystemExit) as excinfo:
        cf.run([_FAST_SET])
    assert "gained SOME but not all" in str(excinfo.value)


def test_the_role_join_refuses_a_seat_the_two_derivations_disagree_on() -> None:
    # The split is only as good as the seat it is drawn on. The roster and the
    # render inputs are independent derivations, so a disagreement must stop the
    # read rather than move a crew turn into the impostor column.
    capture = cf._Capture(
        kind=cf._KIND_ACCUSATION_ROUND,
        agent_id="p-3",
        kwargs={"is_impostor": True, "turn_kind": "reply"},
        off_prompt="",
    )
    roles: dict[str, Any] = {"p-3": "CREWMATE"}
    with pytest.raises(SystemExit) as excinfo:
        cf.speaker_role(capture, roles, where="planted")
    assert "role join" in str(excinfo.value)
    # ...and the unperturbed capture still reads, so the gate is not vacuous.
    assert cf.speaker_role(capture, {"p-3": "IMPOSTOR"}, where="planted") == "IMPOSTOR"


def test_a_later_meeting_can_mask_a_first_meeting_budget_difference() -> None:
    # T7's predicate is a first-meeting identity, and the published B-1 sums
    # every captured meeting. Plant the exact case the aggregate cannot see: one
    # row fewer at meeting 1 and one row more later.
    row = "- [obs a] p-2 in ADMIN\n"
    off, on = cf._LegTallies(), cf._LegTallies()
    off.fold_snapshot(row * 3, bucket="<=4", first_meeting=True)
    on.fold_snapshot(row * 2, bucket="<=4", first_meeting=True)
    off.fold_snapshot(row * 2, bucket="<=4", first_meeting=False)
    on.fold_snapshot(row * 3, bucket="<=4", first_meeting=False)
    assert off.rendered_lines == on.rendered_lines == 5, "B-1 sees nothing move"
    assert (off.first_meeting_rendered_lines, on.first_meeting_rendered_lines) == (3, 2)


def _conviction(
    *, ejected: str, transcript: MeetingTranscript, flags: tuple[Any, ...] = ()
) -> MeetingResult:
    return MeetingResult(
        meeting_id="m-1",
        triggered_by="p-1",
        trigger_tick=11,
        outcome="EJECTED",
        ejected_player_id=ejected,
        ballots=(),
        contradictions=flags,
        transcript=transcript,
    )


def test_the_spoken_kill_split_counts_a_planted_conviction() -> None:
    # Baseline 8 holds no spoken kill at all, so the split is empty there and an
    # empty cell proves nothing about the reader. Plant the meeting the record
    # may produce: a kill spoken against the player the table then ejects.
    spoken = MeetingTranscript(turns=(_KILL_TURN,))
    assert cf.spoken_kill_subjects(spoken) == frozenset({"p-8"})
    census = cf._KillNamedConvictions()
    cf._fold_kill_named_conviction(
        result=_conviction(ejected="p-8", transcript=spoken),
        roles={"p-8": "IMPOSTOR"},
        census=census,
    )
    assert (census.non_direct, census.kill_named, census.kill_named_impostor) == (
        1,
        1,
        1,
    )
    # A kill spoken about someone else leaves the conviction in the cell but out
    # of the split -- the subject is the ejectee, never merely the meeting.
    other = cf._KillNamedConvictions()
    cf._fold_kill_named_conviction(
        result=_conviction(ejected="p-2", transcript=spoken),
        roles={"p-2": "CREWMATE"},
        census=other,
    )
    assert (other.non_direct, other.kill_named) == (1, 0)


def test_a_vent_flag_naming_the_ejectee_leaves_bar_1s_cell_entirely() -> None:
    # The split decomposes the NON-DIRECT cell, so it must inherit that cell's
    # own boundary: a ``vent_sighting`` naming the ejectee is direct proof and
    # bar 1 never counted it.
    spoken = MeetingTranscript(turns=(_KILL_TURN,))
    vent = ContradictionRef(
        contradiction_id="c-1",
        kind="vent_sighting",
        event_a_id="o-1",
        event_b_id="o-1",
        subjects=("p-8",),
        description="p-8 was seen venting",
    )
    assert not cf.is_non_direct_ejection((vent,), "p-8")
    census = cf._KillNamedConvictions()
    cf._fold_kill_named_conviction(
        result=_conviction(ejected="p-8", transcript=spoken, flags=(vent,)),
        roles={"p-8": "IMPOSTOR"},
        census=census,
    )
    assert (census.non_direct, census.kill_named) == (0, 0)


def test_a_split_over_the_wrong_population_refuses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The planted case for the denominator: the split is bar 1's own cell, so a
    # partition that stops agreeing with the committed cross-tab must refuse
    # rather than publish "n of 96" over a different n.
    monkeypatch.setattr(cf, "is_non_direct_ejection", lambda *args, **kwargs: True)
    with pytest.raises(SystemExit) as excinfo:
        cf.run([_FAST_SET])
    message = str(excinfo.value)
    assert "non-direct" in message and "EjecteeProofCrossTab" in message


def test_the_baseline_8_tripwire_readings(full_run: Mapping[str, object]) -> None:
    """The three readings the pre-registration's §8.1 and §5 will be read on."""

    rows = {row["cell"]: row for row in _rows(full_run, "pooled_tripwire_rows")}
    published = {row["cell"]: row for row in _rows(full_run, "pooled")}
    # T5, both halves. No `saw_kill` was ever spoken on these bytes.
    assert rows["T-9a"]["on"] == [2023, 2023]
    assert rows["T-9b"]["on"] == [0, 936]
    # The split partitions T-9's own population exactly, which is what makes it
    # a decomposition of that row rather than a second measurement.
    assert (
        rows["T-9a"]["on"][1] + rows["T-9b"]["on"][1]
        == published["T-9"]["on"][1]
        == 2959
    )
    # On THESE bytes the elicitation reading and the byte diff coincide. That is
    # a property of a corpus holding no spoken kill, not an invariant: the first
    # spoken kill at the smoke or the record separates them.
    assert rows["T-9a"]["on"][0] + rows["T-9b"]["on"][0] == published["T-9"]["on"][0]
    # T7: the first meeting reads identical in all three columns.
    assert (
        rows["B-1m1"]["recorded_off"]
        == rows["B-1m1"]["reconstructed_off"]
        == rows["B-1m1"]["on"]
        == [68288, 3368]
    )
    # Bar 1's cell split by a spoken kill: empty, over bar 1's own denominator.
    assert rows["P-1k"]["recorded_off"] == [0, 96]
    assert published["P-1"]["recorded_off"][1] == 96
    assert rows["P-1ka"]["recorded_off"] == [0, 0]


def _rows(payload: Mapping[str, object], key: str) -> list[Any]:
    rows = payload[key]
    assert isinstance(rows, list)
    return rows


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


def _split_errata(text: str) -> tuple[str, str]:
    """The memo as ``(record, errata)`` — the errata empty when there is none."""

    head, marker, tail = text.partition(f"\n{_ERRATA_HEADING}")
    return (head, f"{marker}{tail}" if marker else "")


def _published_tables(
    text: str,
) -> tuple[dict[tuple[str, str], tuple[Any, ...]], dict[str, tuple[Any, ...]]]:
    """Every cell as it now stands: the record, overridden row-by-row by errata."""

    record, errata = _split_errata(text)
    record_per_set, record_pooled = _parse_tables(record)
    errata_per_set, errata_pooled = _parse_tables(errata)
    return (
        {**record_per_set, **errata_per_set},
        {**record_pooled, **errata_pooled},
    )


def _published_render_census(text: str) -> dict[tuple[str, str], tuple[int, ...]]:
    """The render census as it now stands, the same record-then-errata fold."""

    record, errata = _split_errata(text)
    return {**_memo_render_census(record), **_memo_render_census(errata)}


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


# The §4.3 ballot-census table's row labels, mapped to the flattened census key
# each one publishes. A label the census has no key for -- or a key the memo
# never prints -- makes the comparison fail, which is the point.
_BALLOT_CENSUS_LABELS: Final[tuple[tuple[str, str], ...]] = (
    ("ejecting ballots", "ejecting_ballots"),
    ("citation: hearsay", "citation.hearsay"),
    ("citation: own observation", "citation.own_obs"),
    ("citation: own turn", "citation.own_turn"),
    ("citation: another player's observation", "citation.other_obs"),
    ("citation: nothing", "citation.none"),
    ("pile driver a CREWMATE", "driver.CREWMATE"),
    ("pile driver an IMPOSTOR", "driver.IMPOSTOR"),
    ("follower counts on a CREWMATE source", "followers.CREWMATE"),
    ("follower counts on an IMPOSTOR source", "followers.IMPOSTOR"),
    ("ejections with a contradiction naming the ejectee", "ejections.flagged"),
    ("ejections with none", "ejections.unflagged"),
    ("mean stated confidence, flagged", "confidence.flagged"),
    ("mean stated confidence, unflagged", "confidence.unflagged"),
    ("impostor ballots cast in these meetings", "impostor_ballots_cast"),
    ("impostor ballots that joined the pile", "impostor_ballots_joined"),
)


def _memo_ballot_census(text: str) -> dict[str, object]:
    """The §4.3 ballot-census table, flattened to the census's own keys."""

    published: dict[str, object] = {}
    for line in text.splitlines():
        fields = [field.strip() for field in line.strip().strip("|").split("|")]
        if len(fields) != 2:
            continue
        for prefix, key in _BALLOT_CENSUS_LABELS:
            if not fields[0].startswith(prefix):
                continue
            published[key] = _census_value(key, fields[1])
            break
    return published


def _census_value(key: str, field: str) -> object:
    if key.startswith("followers."):
        return {
            int(count.split("x")[0]): int(count.split("x")[1])
            for count in field.split(", ")
        }
    if key.startswith("confidence."):
        return float(field)
    value = _first_int(field)
    assert value is not None, (key, field)
    return value


def _flatten_ballot_census(census: Mapping[str, Any]) -> dict[str, object]:
    flat: dict[str, object] = {
        "ejecting_ballots": census["ejecting_ballots"],
        "impostor_ballots_cast": census["impostor_ballots_cast"],
        "impostor_ballots_joined": census["impostor_ballots_joining_the_pile"],
    }
    for channel, count in census["citation_mix"].items():
        flat[f"citation.{channel}"] = count
    for role, count in census["pile_driver_role"].items():
        flat[f"driver.{role}"] = count
    for role, counts in census["follower_counts"].items():
        flat[f"followers.{role}"] = {int(key): value for key, value in counts.items()}
    for status, count in census["ejections_by_flag_status"].items():
        flat[f"ejections.{status}"] = count
    for status, mean in census["mean_confidence"].items():
        flat[f"confidence.{status}"] = mean
    return flat


def _memo_render_census(text: str) -> dict[tuple[str, str], tuple[int, ...]]:
    """Every render-census row the memo publishes, keyed ``(leg, prompt class)``."""

    rows: dict[tuple[str, str], tuple[int, ...]] = {}
    for line in text.splitlines():
        fields = [field.strip() for field in line.strip().strip("|").split("|")]
        if len(fields) != 6:
            continue
        leg = fields[0].strip("`")
        prompt_class = fields[1].strip("`")
        if leg not in _RENDER_LEGS or not prompt_class.islower():
            continue
        values = tuple(_first_int(field) for field in fields[2:6])
        if any(value is None for value in values):
            continue
        rows[(leg, prompt_class)] = tuple(
            int(value) for value in values if value is not None
        )
    return rows


def _flatten_render_census(
    census: Mapping[str, Any],
) -> dict[tuple[str, str], tuple[int, ...]]:
    return {
        (leg, prompt_class): (
            cells["rendered"],
            cells["changed"],
            cells["added_lines"],
            cells["added_bytes"],
        )
        for leg, block in census.items()
        for prompt_class, cells in block["by_prompt_class"].items()
    }


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
        # Zeros are KEPT: a kind nobody ever spoke is still one of the eight the
        # census advertises, and dropping it here would let the memo silently
        # stop publishing a row.
        kind = fields[0].strip("`")
        off[kind] = off_value
        on[kind] = on_value
    return off, on


def _run_kind_census(
    census: Mapping[str, Any],
) -> tuple[dict[str, int], dict[str, int]]:
    """The pooled reduction census over ALL eight kinds, zeros included.

    The live counters hold only the kinds something was spoken in, so the
    absent ones are filled at zero here rather than dropped from the memo.
    """

    return (
        {kind: census["statements_off"].get(kind, 0) for kind in _REPORTED_KINDS},
        {kind: census["statements_on"].get(kind, 0) for kind in _REPORTED_KINDS},
    )


def _first_int(field: str) -> int | None:
    match = re.search(r"(\d[\d,]*)", field)
    return int(match.group(1).replace(",", "")) if match else None


_LedgerRow = tuple[tuple[str, ...], dict[str, int]]


def _memo_ledger_rows(text: str) -> dict[tuple[str, int, int, str], _LedgerRow]:
    """The §2.3 per-case ledger, keyed by ``(set, seed, meeting, ejectee)``.

    Every published column is carried, the recorded vote tally included: a tally
    is a fact about the case, and a row whose tags survive an edit to its tally
    is still a drifted row.
    """

    rows: dict[tuple[str, int, int, str], _LedgerRow] = {}
    for line in text.splitlines():
        fields = [field.strip() for field in line.strip().strip("|").split("|")]
        if len(fields) != 6 or fields[0] not in cf.CANONICAL_SETS:
            continue
        if not fields[1].isdigit() or not re.fullmatch(r"m\d+", fields[2]):
            continue
        tags = () if fields[4] == "(none)" else tuple(fields[4].split("+"))
        key = (fields[0], int(fields[1]), int(fields[2][1:]), fields[3])
        rows[key] = (tags, _memo_tally(fields[5]))
    return rows


def _memo_tally(field: str) -> dict[str, int]:
    """``p-5 3, SKIP 2, p-1 1`` as the counter the payload publishes."""

    tally: dict[str, int] = {}
    for entry in field.split(","):
        target, _, count = entry.strip().rpartition(" ")
        tally[target] = int(count)
    return tally


def _run_ledger_rows(
    payload: Mapping[str, object],
) -> dict[tuple[str, int, int, str], _LedgerRow]:
    ledger = payload["pooled_injustice_ledger"]
    assert isinstance(ledger, list)
    return {
        (row["set"], row["seed"], row["meeting"], row["victim"]): (
            tuple(row["tags"]),
            dict(row["tally"]),
        )
        for row in ledger
    }


def _memo_class_totals(text: str) -> dict[str, int]:
    """The §2.1 class-total table, keyed by the tag the ledger emits."""

    totals: dict[str, int] = {}
    for line in text.splitlines():
        fields = [field.strip() for field in line.strip().strip("|").split("|")]
        if len(fields) != 4:
            continue
        count = re.fullmatch(r"\*\*(\d+)\*\*", fields[2])
        if count is None or not re.fullmatch(r"[A-Z-]+", fields[1]):
            continue
        totals[fields[1]] = int(count.group(1))
    return totals


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
