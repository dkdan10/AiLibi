#!/usr/bin/env python3
"""Check the README's figures against the committed files they come from.

Seconds, offline, no model calls. Each check recomputes a figure from the file
that owns it, and every mismatch is reported, not only the first.

1. **Sample provenance.** The README's samples paragraph dates each sample set,
   names the recording model, links each set's manifest and the record of its
   era (``eval/eras.py``), and states each set's game count and impostor win
   rate. All of it is recomputed from ``replays/samples/<set>/MANIFEST.md``.
   Every ``<rate>% (<set>)`` claim and every dated claim elsewhere in the
   README is held to the same manifests, except in the results table's Before
   column, which is held to the frozen before cells (:data:`_RESULTS_BEFORE`).
2. **The .env.example registries.** Each live substrate lever and each meeting
   experiment switch appears as a commented example showing its default, never
   as an active assignment. Graduated levers are named in the graduated note and
   never assigned, and no unregistered ``AILIBI_*`` name is advertised. Both
   registries come from the live imports, never from ``--repo-root``.
3. **The results table.** The replay count is recounted from the replay files,
   the citation row from the pinned assertions in
   ``tests/eval/test_vj_instruments.py``, the vent and proof rows from the
   shown 9p2i set's column of ``docs/gameplay-census.md``, and the four process
   rows from that set's table on ``docs/process-scorecard.md``. The process
   rows' Before cells come from that page's before column; the win-rate and
   proof Before cells from the frozen before cells, values copied once from the
   records and pinned here by their sha256. The other Before cells are not
   checked.
4. **The real-report example.** Its three ejection counts come from the
   ``vote_correctness`` block of the committed 9p2i report.
5. **The prose figures.** The top-suspect sentence, the vent sentence, the
   cited-vote count, the demo's game count, the import-contract count and the
   install block's recording count are each recomputed from their source.
6. **The ML results table.** ``docs/ml-program.md``'s table is recomputed from
   ``training/reports/results-finalist-eval.jsonl``.

Relative links are ``scripts/check_links.py``'s job.

``--repo-root`` points the reads at another tree; the tests perturb a copy.
Exit 0 when everything matches, 1 with every failure printed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import Final, NamedTuple

from markdown_it import MarkdownIt
from markdown_it.token import Token
from pydantic import BaseModel, ConfigDict, model_validator

_REPO_ROOT: Final = Path(__file__).resolve().parents[1]
_SCRIPTS_DIR: Final = Path(__file__).resolve().parent
# Make both the top-level packages (``orchestrator``) and the sibling script
# modules (``_manifest_writer``, a top-level name per ``mypy_path = "scripts"``)
# importable under ``uv run python scripts/check_doc_facts.py``. Mirrors
# scripts/build_sample_report.py.
for _bootstrap_path in (_REPO_ROOT, _SCRIPTS_DIR):
    if str(_bootstrap_path) not in sys.path:
        sys.path.insert(0, str(_bootstrap_path))

from _manifest_writer import parse_manifest  # noqa: E402
from _verify_samples import sample_paths  # noqa: E402
from paired_stats import compute_paired_stats  # noqa: E402

from api.replay_loader import SetLoaderRegistry  # noqa: E402
from eval.eras import Era, era_of  # noqa: E402
from eval.report_io import REPORT_FILENAME, open_report_text  # noqa: E402
from meetings.evidence_profile import (  # noqa: E402
    EXPERIMENT_ENV_NAMES,
    MeetingEvidenceProfile,
)
from orchestrator.recording_fingerprint import (  # noqa: E402
    REPLAY_FILENAME_GLOB,
    replay_seed_from_filename,
)
from orchestrator.replay import (  # noqa: E402
    SUBSTRATE_FLAG_KEYS,
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    substrate_flag_snapshot,
)

_README: Final = "README.md"
_ENV_EXAMPLE: Final = ".env.example"
_SAMPLE_SETS: Final[tuple[str, ...]] = ("4p1i", "9p2i")
_MANIFEST_PATH: Final = "replays/samples/{name}/MANIFEST.md"
_SAMPLE_REPLAY_DIR: Final = "replays/samples/{name}"
# The set the vent, proof and process rows read, and how the census and the
# scorecard page label it.
_SHOWN_SET: Final = "9p2i"
_SET_LABEL: Final = "samples/{name}"

# The ``winner`` cell a manifest row carries when the impostors took the game.
_IMPOSTOR_WINNER: Final = "IMPOSTORS"
# ``refreshed_at`` is ISO ``YYYY-MM-DD``, so lexicographic max is chronological.
_ISO_DATE: Final = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
# The README's samples paragraph is anchored on this clause; the refresh-date
# claim is parsed from it rather than sought file-wide, so a stale paragraph
# cannot be alibied by the correct date elsewhere.
_REGENERATED_DATE: Final = re.compile(r"regenerated (\d{4}-\d{2}-\d{2})")
# Any "<rate>% (<set>)" claim, wherever it appears, must match the manifest.
_WIN_RATE_CLAIM: Final = re.compile(r"(\d+)% \((4p1i|9p2i)\)")
# The two other shapes the README dates a recording in. An unnumbered one is
# about a current recording and is held to the manifest of the set it names; a
# numbered one ("reference recording 6, <date>") is about an older recording
# and is left alone.
_RECORDING_DATE_CLAIM: Final = re.compile(
    r"reference recording(?:\s+(\d+))?,?\s+(?:made\s+)?(\d{4}-\d{2}-\d{2})"
)
_RECORD_DATE_CLAIM: Final = re.compile(r"the (\d{4}-\d{2}-\d{2}) record\b")
# The sample sets were recorded on different days, so a date claim names the
# set it dates in the parentheses directly after it: "the 2026-10-09 record
# (9p2i)". A claim naming no set, or a set recorded on another day, is drift.
_CLAIM_SETS: Final = re.compile(r"\s*\(([^)]*)\)")
# A prompt stamp the samples paragraph names, backticked or not: an arm token
# (``route_lines_v1``) or a bare version (``v6``). The paragraph leaves the
# stamps to the manifests it links, so one it does name must be recorded.
_STAMP_TOKEN: Final = re.compile(r"\b\w*_v\d+\b|\bv\d+\b")
_SET_NAME: Final = re.compile(r"\b(4p1i|9p2i)\b")

# The .env.example section whose AILIBI_*= assignments must all resolve to a
# live registry key, delimited by the repo's dashed section banners.
_LEVER_SECTION_TITLE: Final = "# Belief-substrate levers"
# The second registry section: the independently versioned meeting experiments,
# whose env switches meetings.evidence_profile owns.
_EXPERIMENT_SECTION_TITLE: Final = "# Independently versioned experiments"
_SECTION_RULE: Final = re.compile(r"^# -{20,}[ \t]*$", re.MULTILINE)
# The forms a .env loader reads as the SAME assignment: an `export` prefix and
# padding around the `=` are both stripped by python-dotenv and by `set -a;
# . .env`, so a rule that only saw `AILIBI_X=` let `export AILIBI_X=1` turn a
# switch on with the gate green.
_EXPORT_PREFIX: Final = r"(?:export[ \t]+)?"
_ENV_ASSIGNMENT: Final = re.compile(
    rf"^#?[ \t]*{_EXPORT_PREFIX}(AILIBI_[A-Z0-9_]+)[ \t]*=", re.MULTILINE
)
# The graduated note is the contiguous comment block opening with this marker;
# the graduated/always-ON labels must live IN it, not merely near it.
_GRADUATED_NOTE_MARKER: Final = "# GRADUATED LEVERS"
_BLANK_LINE: Final = re.compile(r"\n[ \t]*\n")

# The results table, located by its header row rather than by heading text, so
# a section rename does not silently disable the checks that read it.
_RESULTS_TABLE_HEADER: Final[tuple[str, str]] = ("What", "Figure")
# The column carrying each row's value at the recording that set replaced. Its
# cells are history: they are held to what that recording read, never to
# today's committed bytes.
_BEFORE_COLUMN_HEADER: Final = "Before"
# A markdown link reduced to its text, so a cell may carry a link and still be
# matched by name.
_LINK_TEXT: Final = re.compile(r"\[([^\]]*)\]\([^)\s]+\)")
_TABLE_RULE_CELL: Final = re.compile(r"\A:?-{2,}:?\Z")
_HEADING: Final = re.compile(r"^#{1,6}[ \t]+(.+?)[ \t]*$", re.MULTILINE)
_EMPHASIS: Final = re.compile(r"[*`]")

# The results rows this module recomputes, each named by its first cell.
_REPLAY_COUNT_CLAIM: Final = "Sample games that replay byte for byte"
_CITATION_INSTRUMENT: Final = "tests/eval/test_vj_instruments.py"
_CITATION_CLAIM: Final = (
    "Eject ballots with a valid citation of a statement or sighting (9p2i)"
)
# The instrument's pinned assertions, read as the committed source of the
# citation figure: ``assert nine.<field> == <n>``.
_CITATION_PIN: Final = re.compile(r"^\s*assert nine\.(\w+) == (\d+)\s*$", re.MULTILINE)
_CITATION_PIN_NAMES: Final[tuple[str, ...]] = (
    "eject_ballots",
    "cited_eject_ballots",
    "turn_citations_dangling",
    "observation_citations_dangling",
)
_VENT_CLAIM: Final = (
    "Impostors ejected after a reported sighting of them venting (9p2i)"
)
_PROOF_CLAIM: Final = (
    "Impostors among those ejected, with and without proof of their role (9p2i)"
)
# The injustice clause the proof row carries beside its two figures. Both
# halves are required: the count AND where those ejections landed, because the
# count alone is satisfied by a row that puts them in the wrong cell.
_INJUSTICE_CLAIM: Final = (
    "{count} of {count} innocent ejections sit in the no-proof cell"
)

# The generated census page. The shown set's column of its vent-proof table
# owns the vent row, the proof row and the vent sentence. The vent band (the
# ejections a vent-sighting flag names) is the proof row's "with proof" half;
# on the shown set it holds the same ejections as the eval report's
# proof-present cell, compared one by one on 2026-10-13.
_CENSUS_PAGE: Final = "docs/gameplay-census.md"
_CENSUS_SECTION: Final = "### Vent proof at meetings"
_CENSUS_FIRST_HEADER: Final = "cell"
# A census cell opens with ``k/n``; a cell reading "n/a" is no count at all.
_CENSUS_FRACTION: Final = re.compile(r"\A(\d+)/(\d+)\b")
_CENSUS_MEETINGS: Final = "Meetings with vent proof"
_CENSUS_BAND_IMPOSTORS: Final = "Impostor ejections in the vent band"
_CENSUS_BAND_CREW: Final = "Crewmate ejections in the vent band"
_CENSUS_UNFLAGGED: Final = "Ejections without vent proof that removed an impostor"

# The win-rate and proof rows' before cells, copied once from the records that
# published them and pinned by their sha256: a before cell is history and is
# never recomputed. A re-record appends an entry and moves the pin.
_RESULTS_BEFORE: Final = "docs/results-before.json"
_RESULTS_BEFORE_SHA256: Final = (
    "cf8467b44381e2849566e203ac58166423c6c12cfe6f71072aee64ddc5ff344b"
)
# The recording each era's sample sets replaced, by era id. The frozen before
# cells and the scorecard page's before column both describe that recording.
_REPLACED_ERAS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "baseline-9": "baseline-8",
        "stage-b-r2": "baseline-9",
        "stage-b-r3": "stage-b-r2",
    }
)

# The four rows the results table leads with: how each vote was cast, read off
# the shown set's table on the GENERATED scorecard page. The markdown page, never
# its JSON, which no component reads (``eval/process_scorecard.py``'s
# ``NO_CONSUMER_NOTE``). Each pair is the row's claim and the page's row label.
_SCORECARD_PAGE: Final = "docs/process-scorecard.md"
_GROUNDED_EJECT_CLAIM: Final = (
    "Eject ballots citing what the voter saw or heard about the accused (9p2i)"
)
_DEVIATING_EJECT_CLAIM: Final = (
    "Crew eject ballots naming someone other than the voter's top suspect (9p2i)"
)
_UNEXPLAINED_CLAIM: Final = "Ballots with no stated reason (9p2i)"
_AUTHORED_CLAIM: Final = "Ballots whose target is the one their voter wrote (9p2i)"
_PROCESS_ROWS: Final[tuple[tuple[str, str], ...]] = (
    (_GROUNDED_EJECT_CLAIM, "grounded-decision rate, EJECT"),
    (_DEVIATING_EJECT_CLAIM, "argmax-independence: deviating EJECTs"),
    (_UNEXPLAINED_CLAIM, "unexplained-decision rate"),
    (_AUTHORED_CLAIM, "agent-authored share"),
)
# The authored share's residual on the shown set is the teammate firewall: the
# impostor votes against a partner the meeting layer turned into skips. The
# row-7 detail line names it by its typed rewrite reason.
_TEAMMATE_REASON: Final = "teammate_coerced"
# The page's own shapes: the set's section heading, the table's first two header
# cells, the before column's header (it names the era whose frozen block it
# reads), the value column, and the row-7 detail line's typed rewrites.
_SCORECARD_SET_HEADING: Final = "### {label}"
_SCORECARD_HEADER: Final[tuple[str, str]] = ("#", "row")
_SCORECARD_BEFORE_HEADER: Final = "before: {era},"
_SCORECARD_VALUE_HEADER: Final = "value"
_SCORECARD_REWRITES: Final = "Row 7 detail: typed guard rewrites "
_SCORECARD_REWRITE_ENTRY: Final = re.compile(r"\A(\w+) (\d+)\Z")
_SCORECARD_NO_REWRITES: Final = "none"
# A scorecard page cell as the generated page prints it, ``k/n = rate``; its two
# counts are what the table restates in its own form.
_SCORECARD_FRACTION: Final = re.compile(r"\A(\d+)/(\d+) = \d*\.?\d+%?\Z")

# The README's PROSE figures: the sentences that retell a scorecard cell, the
# census's vent cells, a file population or a config. Each claim shape is held
# wherever the README states it, so a stale copy beside a correct one fails as
# surely as a stale sole copy, and a sentence that stops stating its figure
# fails rather than leaving the source bound to nothing.
#
# How crew eject ballots for and against the voter's top suspect fared, from the
# shown set's row-2 role-correct cell on the scorecard page: followers,
# deviators and the chance rate.
_ROLE_CORRECT_ROW: Final = "argmax-independence: role-correct, followers vs deviators"
_ROLE_CORRECT_CELL: Final = re.compile(
    r"\A(\d+)/(\d+) = [\d.]+% vs (\d+)/(\d+) = [\d.]+% \(chance ([\d.]+)%\)\Z"
)
_FOLLOWER_PROSE: Final = re.compile(
    r"\bhit an impostor (\d+) of (\d+) times \((\d+)%\)"
)
_DEVIATOR_PROSE: Final = re.compile(
    r"\bthe (\d+) against it hit one (\w+(?: times)?) \((\d+)%\)"
)
_CHANCE_PROSE: Final = re.compile(r"\bchance is about one in (\w+)\b")
# Any other "k of <followers>" claim: the follower figure retold in other words,
# which must still name the role-correct count.
_FOLLOWER_COUNT_PROSE: Final = r"\b(\d+) of {followers}\b"
_REPEAT_WORDS: Final[Mapping[int, str]] = MappingProxyType({1: "once", 2: "twice"})
# The vent cells retold under the vent headline: the meetings with vent proof
# and their clean record, then the meetings without, the impostor share of
# their ejections and their innocent ejections.
_VENT_FLAGGED_PROSE: Final = re.compile(
    r"\bin the (\d+) meetings with one\b", re.IGNORECASE
)
_VENT_UNFLAGGED_PROSE: Final = re.compile(
    r"\bin the (\d+) without, (\d+) of (\d+) did and (\d+) removed crewmates\b",
    re.IGNORECASE,
)
_VENT_UNFLAGGED_SHARE_PROSE: Final = r"\b(\d+) of {ejections}\b"
_VENT_INNOCENT_PROSE: Final = re.compile(r"\b(\d+) removed crewmates\b")
# The clean record of the meetings with vent proof, stated twice: true only
# while none of them ejected a crewmate.
_VENT_CLEAN_RECORD_PROSE: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"\bnever ejected a crewmate\b", re.IGNORECASE),
    re.compile(r"\bevery ejection removed an impostor\b", re.IGNORECASE),
)
# The cited-vote figure retold in prose, held to the scorecard cell its results
# row restates.
_GROUNDED_EJECT_PROSE: Final = re.compile(r"\b(\d+) of (\d+) votes to eject\b")
# The demo's game count, held to the games the bundle builder bakes: every set
# directory under the samples root, not only the sets this checker names.
_DEMO_GAMES_PROSE: Final = re.compile(r"\bcarries all (\d+) games\b")
_DEMO_SAMPLES_ROOT: Final = "replays/samples"
# The import contracts, counted as the contract sections of the linter's config.
_IMPORT_LINTER: Final = ".importlinter"
_IMPORT_CONTRACT_SECTION: Final = re.compile(
    r"^\[importlinter:[^\]\n]+\]", re.MULTILINE
)
_IMPORT_CONTRACT_PROSE: Final = re.compile(
    r"\bof (\w+) import contracts\b", re.IGNORECASE
)
# The recordings a bare ``scripts/verify_samples.sh`` re-runs: each set directory
# under the samples root and each ``<round>/<set>/`` under the candidates root.
# The README states this count inside its install block, so it is read raw.
_VERIFIED_SET_GLOBS: Final[tuple[tuple[str, str], ...]] = (
    ("replays/samples", "*"),
    ("replays/candidates", "*/*"),
)
_VERIFIED_RECORDINGS_PROSE: Final = re.compile(
    r"\b(\d+) sample and candidate recordings\b"
)
_NUMBER_WORDS: Final[tuple[str, ...]] = (
    "no",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
)

# The committed report the README hands a reader instead of the empty one a
# fake-provider run produces, and the phrase that anchors its paragraph.
_POPULATED_REPORT: Final = "replays/samples/9p2i/" + REPORT_FILENAME
_EXAMPLE_ANCHOR: Final = "fake provider's report is empty on purpose"
# What the example states, as ``(label, report key, wording)``: the three counts
# the report's own ``vote_correctness`` block carries, each in what it counts.
_REPORT_EXAMPLE_CLAIMS: Final[tuple[tuple[str, str, str], ...]] = (
    ("ejections", "total_ejections", "{total_ejections:d} ejections"),
    (
        "impostor ejections",
        "impostor_ejections",
        "{impostor_ejections:d} removed an impostor",
    ),
    (
        "evidence-backed impostor ejections",
        "evidence_backed_impostor_ejections",
        "{evidence_backed_impostor_ejections:d} of those {impostor_ejections:d} "
        "with evidence against that player",
    ),
)
_VOTE_CORRECTNESS_KEY: Final = '"vote_correctness":'
# The reports run to tens of megabytes; the blocks read out of them are a dozen
# scalar fields at most, so a runaway scan means the report format drifted
# rather than a bigger block.
_REPORT_BLOCK_MAX_LINES: Final = 64

# The ML page's results table and the committed measurement it is derived from.
# The table is located by its own header cells, so renaming the section above it
# does not disable the derivation.
_ML_PAGE: Final = "docs/ml-program.md"
_FINALIST_JSONL: Final = "training/reports/results-finalist-eval.jsonl"
_ML_TABLE_HEADER: Final[tuple[str, str]] = ("policy", "impostor win")
# Every row label opens with its identity in backticks — an arm's committed sha
# prefix, or the comparator's entrant name. The identity is matched WHOLE (the
# capture is anchored on the backticks), because a substring test would accept a
# ``fake-p18-fsm-comparator`` row as the comparator.
_ML_ROW_IDENTITY: Final = re.compile(r"`([^`]+)`")
_ML_ARM_SHA: Final = re.compile(r"\A([0-9a-f]{6,})…\Z")
_ML_ARM_ENTRANT: Final = "p18-imp-{sha}"
_ML_COMPARATOR_LABEL: Final = "p18-fsm-comparator"
# ``<k>/<n> = <rate>`` — the rate is checked at the precision the cell prints,
# so a table may round as it likes but may not round to a different number.
_ML_FRACTION: Final = re.compile(r"(\d+)\s*/\s*(\d+)\s*=\s*(\d*\.(\d+))")
# The leading decimal of a p cell. Leading, because the Bonferroni alpha is
# stated after the p on one row and must not be mistaken for it.
_ML_P_VALUE: Final = re.compile(r"(\d*\.(\d+))")
# The referee column's two verdicts, held to ``watchability.referee_passed`` in
# the same committed JSONL — the adoption gate the whole page turns on. The cell
# must BE one of these once markdown emphasis is stripped, not merely contain
# one: "not a FAIL" contains FAIL and means the opposite.
_ML_REFEREE_PASS: Final = "PASS"
_ML_REFEREE_FAIL: Final = "FAIL"
# The published width of the results table: policy, win, comparator, p, referee.
_ML_TABLE_COLUMNS: Final = 5


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the README's figures against the files they come from."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=_REPO_ROOT,
        help=(
            "Tree whose documents and sources are read (default: this "
            "checkout). The lever and experiment registries always come from "
            "the live imports, never from this tree."
        ),
    )
    args = parser.parse_args(argv)
    repo_root: Path = args.repo_root

    errors = check_facts(repo_root)
    if errors:
        print("Doc-fact check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Doc facts verified: {_README}'s samples paragraph, results table, "
        "real-report example and prose figures agree with the "
        f"{len(_SAMPLE_SETS)} sample manifests, the committed replays, "
        f"{_CITATION_INSTRUMENT}, {_CENSUS_PAGE}, {_SCORECARD_PAGE}, "
        f"{_RESULTS_BEFORE}, {_POPULATED_REPORT}, {_IMPORT_LINTER} and the "
        f"candidate replays; {_ENV_EXAMPLE} agrees with the "
        f"{len(SUBSTRATE_FLAG_KEYS)}-lever substrate registry and the "
        f"{len(EXPERIMENT_ENV_NAMES)}-switch experiment registry; {_ML_PAGE}'s "
        f"results table recomputes from {_FINALIST_JSONL}."
    )
    return 0


def check_facts(repo_root: Path) -> list[str]:
    """Every checked-fact failure under ``repo_root``, in check order."""

    errors: list[str] = []
    before = before_cells(repo_root, errors)
    readme = read_document(repo_root, _README, errors)
    if readme is not None:
        check_sample_provenance(repo_root, readme, before, errors)
        check_result_sources(repo_root, readme, before, errors)
        check_process_rows(repo_root, readme, errors)
        check_populated_report_example(repo_root, readme, errors)
        check_role_correct_prose(repo_root, readme, errors)
        check_vent_prose(repo_root, readme, errors)
        check_grounded_prose(repo_root, readme, errors)
        check_demo_game_count(repo_root, readme, errors)
        check_import_contract_count(repo_root, readme, errors)
        check_verified_recording_count(repo_root, readme, errors)
    # One read for both registry checks, so a missing template is reported
    # once rather than once per registry it would have been audited against.
    environment = read_document(repo_root, _ENV_EXAMPLE, errors)
    if environment is not None:
        check_lever_registry(environment, errors)
        check_experiment_registry(environment, errors)
    check_ml_results_table(repo_root, errors)
    return errors


# ── 1. Sample provenance ─────────────────────────────────────────────────────


class _SetFacts(NamedTuple):
    """One sample set's provenance, re-derived from its own ``MANIFEST.md``."""

    wins: int
    total: int
    #: The newest ISO ``refreshed_at`` its rows carry, or ``None`` when none does.
    date: str | None
    #: The recorded era ``eval/eras.py`` files the set under.
    era: Era


def prompt_stamp_tokens(cell: str) -> tuple[set[str], set[str], set[str]]:
    """``(families, versions, arms)`` one ``prompt_versions`` cell records.

    A cell is a comma-separated list of ``template.family.version`` entries; a
    template a switched-on arm re-bodies stamps ``template.family.version.arm``,
    and one two arms re-body stamps a composite of those joined by ``+``. Each
    composite is split on ``+`` before its dots are read, so the family is
    always the second segment, the version the third and every further segment
    an arm. The no-meetings sentinel and empty cells carry no dotted part.
    """

    families: set[str] = set()
    versions: set[str] = set()
    arms: set[str] = set()
    for entry in cell.split(","):
        for part in entry.split("+"):
            segments = part.strip().split(".")
            if len(segments) < 3:
                continue
            families.add(segments[1])
            versions.add(segments[2])
            arms.update(segments[3:])
    return families, versions, arms


def check_sample_provenance(
    repo_root: Path,
    readme: str,
    before: Mapping[str, BeforeCells],
    errors: list[str],
) -> None:
    """README's sample refresh dates, win rates and eras, re-derived per set.

    The rate is ``rows won by IMPOSTORS / rows``, rounded to a whole percent —
    the same arithmetic the README paragraph states in prose. A manifest that
    parses to zero rows is a hard failure rather than a vacuous pass: silent
    format drift would otherwise let any claim through.

    The two sample sets sit in two eras (``eval/eras.py``), recorded on different
    days by different records, so each set's date, rate and record are its own:
    the paragraph dates each set with its own ``regenerated <date> (<set>)``
    clause and links each set's era to the record that owns it.

    The claims are checked IN the samples paragraph, not file-wide: a correct
    value surviving somewhere else must not alibi a drifted paragraph. Win-rate
    and date claims found outside the paragraph are held to the same manifests
    by :func:`check_repeated_claims`.
    """

    facts: dict[str, _SetFacts] = {}
    models: set[str] = set()
    prompt_versions: set[str] = set()
    prompt_arms: set[str] = set()
    for name in _SAMPLE_SETS:
        relative_path = _MANIFEST_PATH.format(name=name)
        text = read_document(repo_root, relative_path, errors)
        if text is None:
            continue
        rows = list(parse_manifest(text).values())
        if not rows:
            errors.append(
                f"{relative_path}: parsed zero table rows — the manifest format "
                "drifted away from _manifest_writer.parse_manifest, so neither "
                "the win rate nor the refresh date can be re-derived."
            )
            continue

        impostor_wins = sum(
            1 for row in rows if row.winner.strip().upper() == _IMPOSTOR_WINNER
        )
        models.update(row.model.strip() for row in rows)
        for row in rows:
            _, versions, arms = prompt_stamp_tokens(row.prompt_versions)
            prompt_versions |= versions
            prompt_arms |= arms

        set_dates = [
            row.refreshed_at.strip()
            for row in rows
            if _ISO_DATE.match(row.refreshed_at.strip())
        ]
        if not set_dates:
            errors.append(
                f"{relative_path}: no row carries an ISO refreshed_at date, so "
                "the sample-set refresh date cannot be re-derived."
            )
        facts[name] = _SetFacts(
            wins=impostor_wins,
            total=len(rows),
            date=max(set_dates) if set_dates else None,
            era=era_of(_SAMPLE_REPLAY_DIR.format(name=name)),
        )

    # Before the paragraph check, not after: a README that lost its samples
    # paragraph still states these facts elsewhere, and they are still checked.
    check_repeated_claims(readme, facts, before, errors)

    paragraph = provenance_paragraph(readme)
    if paragraph is None:
        errors.append(
            f"{_README}: expected exactly one sample-provenance paragraph "
            "(anchored on 'replays/samples/' plus a 'regenerated YYYY-MM-DD' "
            "clause) — without it the provenance claims have no home to check."
        )
        return

    for name, fact in facts.items():
        if fact.date is not None:
            dated = f"regenerated {fact.date} ({name})"
            if dated not in paragraph:
                errors.append(
                    f"{_README}: the sample-provenance paragraph does not date "
                    f"the {name} set with {dated!r} — "
                    f"{_MANIFEST_PATH.format(name=name)} records its newest "
                    f"refresh on {fact.date}."
                )
        if f"]({fact.era.record})" not in paragraph:
            errors.append(
                f"{_README}: the sample-provenance paragraph does not link the "
                f"{name} set's era, {fact.era.id}, to the record that owns it "
                f"({fact.era.record}) — each set is named with its own era "
                "(eval/eras.py), never one record for both."
            )

    for name, fact in facts.items():
        claim = f"{round(100 * fact.wins / fact.total)}% ({name})"
        if claim not in paragraph:
            errors.append(
                f"{_README}: the sample-provenance paragraph is missing the "
                f"recorded impostor win rate {claim!r} — "
                f"{_MANIFEST_PATH.format(name=name)} records "
                f"{fact.wins}/{fact.total} games won by the impostors."
            )

    size_claims: dict[str, list[str]] = {}
    for name, fact in facts.items():
        size_claims.setdefault(f"{fact.total}-game", []).append(name)
    for games_claim, names in sorted(size_claims.items()):
        if games_claim not in paragraph:
            errors.append(
                f"{_README}: the sample-provenance paragraph is missing the "
                f"tournament size {games_claim!r} — "
                f"{', '.join(_MANIFEST_PATH.format(name=name) for name in names)} "
                f"hold that many replay rows per set."
            )
    set_sizes = {fact.total for fact in facts.values()}
    for size_match in re.finditer(r"(\d+)-game", paragraph):
        if int(size_match.group(1)) not in set_sizes:
            errors.append(
                f"{_README}: the sample-provenance paragraph claims a "
                f"'{size_match.group(0)}' tournament, but no manifest holds "
                f"that many rows (per-set row counts: "
                f"{', '.join(str(size) for size in sorted(set_sizes))})."
            )
    if len(facts) == len(_SAMPLE_SETS):
        grand_total = sum(fact.total for fact in facts.values())
        replays_claim = f"{grand_total} sample replays"
        if replays_claim not in paragraph:
            errors.append(
                f"{_README}: the sample-provenance paragraph is missing the "
                f"total {replays_claim!r} — the manifests hold {grand_total} "
                "replay rows between them."
            )
        for total_match in re.finditer(r"(\d+) sample replays", paragraph):
            if int(total_match.group(1)) != grand_total:
                errors.append(
                    f"{_README}: the sample-provenance paragraph claims "
                    f"{total_match.group(0)!r}, but the manifests hold "
                    f"{grand_total} replay rows between them."
                )

    if len(models) > 1:
        errors.append(
            f"{_README}: the manifests disagree on the recording model "
            f"({', '.join(sorted(models))}) — a single model claim cannot be "
            "checked; the sample sets should share one recorded model."
        )
    elif models:
        model = next(iter(models))
        if model not in paragraph:
            errors.append(
                f"{_README}: the sample-provenance paragraph does not name "
                f"the recording model {model!r} — the manifest `model` column "
                "records it on every row."
            )
    for name in facts:
        manifest = _MANIFEST_PATH.format(name=name)
        if f"]({manifest})" not in paragraph:
            errors.append(
                f"{_README}: the sample-provenance paragraph does not link "
                f"{manifest} — the paragraph names the model and leaves each "
                "set's prompt stamps to its manifest, so the manifest is linked."
            )
    for match in _STAMP_TOKEN.finditer(paragraph):
        token = match.group(0)
        kind, recorded = (
            ("prompt arm", prompt_arms)
            if "_v" in token
            else ("prompt-set version", prompt_versions)
        )
        if token not in recorded:
            errors.append(
                f"{_README}: the sample-provenance paragraph names the {kind} "
                f"{token!r}, which no row's `prompt_versions` column records "
                f"(recorded: {', '.join(sorted(recorded)) or 'none'})."
            )


def check_repeated_claims(
    readme: str,
    facts: Mapping[str, _SetFacts],
    before: Mapping[str, BeforeCells],
    errors: list[str],
) -> None:
    """The win rates and the recordings' dates, everywhere the README states them.

    The samples paragraph is where a claim like "34% (9p2i)" is first written,
    not the only place it rots, so every claim of that shape is held to its own
    set's manifest. A claim in the results table's Before column states what
    the set's replaced recording read, so it is held to the frozen before cells
    instead: a live figure written into a history cell, or a history figure
    written into a live one, fails either way.

    A dated claim names the set it dates and must equal that set's newest
    refresh date; a claim naming no set is refused, since no one date is true
    of both sets.
    """

    rates = {name: (fact.wins, fact.total) for name, fact in facts.items()}
    previous = {
        name: (cells.impostor_wins, cells.games) for name, cells in before.items()
    }
    for number, unit, historical in claim_units(readme):
        for match in _WIN_RATE_CLAIM.finditer(unit):
            name = match.group(2)
            expected_rates = previous if historical else rates
            if name not in expected_rates:
                continue
            wins, total = expected_rates[name]
            expected = round(100 * wins / total)
            if int(match.group(1)) == expected:
                continue
            source, where = (
                (_RESULTS_BEFORE, " in the before column")
                if historical
                else (_MANIFEST_PATH.format(name=name), "")
            )
            errors.append(
                f"{_README}:{number}: win-rate claim {match.group(0)!r}{where} "
                f"disagrees with {source} ({wins}/{total} = {expected}%)."
            )
        if historical:
            continue
        for stated, claim, named in current_record_dates(unit):
            if not named:
                errors.append(
                    f"{_README}:{number}: {claim!r} names no sample set — the two "
                    "sets were recorded on different days ("
                    + ", ".join(f"{name} {fact.date}" for name, fact in facts.items())
                    + "), so a dated claim names the set it dates, as "
                    f"'{claim} (9p2i)'."
                )
                continue
            for name in named:
                if name not in facts or facts[name].date == stated:
                    continue
                errors.append(
                    f"{_README}:{number}: {claim!r} dates the {name} recording "
                    f"{stated!r}, but {_MANIFEST_PATH.format(name=name)} records "
                    f"{facts[name].date!r}."
                )


def current_record_dates(text: str) -> Iterator[tuple[str, str, tuple[str, ...]]]:
    """Each ``(date, claim, sets)`` in ``text`` that dates a current recording.

    A claim numbering a recording ("reference recording 6, 2026-07-20") is
    about an older one and is not yielded. Every other — "reference recording,
    made <date>", "the <date> record", "regenerated <date>" — is yielded with
    the sample sets named in the parentheses right after it
    (:data:`_CLAIM_SETS`), empty when it names none.
    """

    for match in _RECORDING_DATE_CLAIM.finditer(text):
        if match.group(1) is None:
            claim = " ".join(match.group(0).split())
            yield match.group(2), claim, claim_sets(text, match.end())
    for pattern in (_RECORD_DATE_CLAIM, _REGENERATED_DATE):
        for match in pattern.finditer(text):
            yield match.group(1), match.group(0), claim_sets(text, match.end())


def claim_sets(text: str, end: int) -> tuple[str, ...]:
    """The sample sets the parentheses at ``text[end:]`` name, in order."""

    parentheses = _CLAIM_SETS.match(text, end)
    if parentheses is None:
        return ()
    return tuple(_SET_NAME.findall(parentheses.group(1)))


def claim_units(markdown: str) -> Iterator[tuple[int, str, bool]]:
    """``(line, text, historical)`` for every span a claim scan may read.

    A document is scanned line by line, except inside the results table: there
    each cell is its own unit, because one column of it — the before column —
    holds the previous recording's values and must not be held to the current
    bytes. Everything else, including every other cell of those same rows, is a
    live claim.
    """

    before_index: int | None = None
    for number, line in enumerate(markdown.splitlines(), 1):
        cells = table_cells(line)
        if cells is None:
            before_index = None
            yield number, line, False
            continue
        if tuple(cells[:2]) == _RESULTS_TABLE_HEADER:
            plain = [strip_links(cell) for cell in cells]
            before_index = (
                plain.index(_BEFORE_COLUMN_HEADER)
                if _BEFORE_COLUMN_HEADER in plain
                else None
            )
        if before_index is None:
            yield number, line, False
            continue
        for index, cell in enumerate(cells):
            yield number, cell, index == before_index


def strip_links(text: str) -> str:
    """``text`` with every markdown link reduced to its link text."""

    return _LINK_TEXT.sub(r"\1", text).strip()


def provenance_paragraph(readme: str) -> str | None:
    """The README's single sample-provenance paragraph.

    ``None`` when the anchor is missing or ambiguous — both are format drift
    the caller reports rather than papering over.
    """

    matches = [
        paragraph
        for paragraph in readme.split("\n\n")
        if "replays/samples/" in paragraph and _REGENERATED_DATE.search(paragraph)
    ]
    if len(matches) != 1:
        return None
    return matches[0]


# ── The frozen before cells ──────────────────────────────────────────────────


class BeforeCellsError(ValueError):
    """The frozen before cells do not read as pinned."""


class BeforeCells(BaseModel):
    """One sample set's before cells: what the recording its bytes replaced read.

    ``proof`` and ``no_proof`` are the proof row's two halves, ``(impostors,
    ejections)``, on the shown set only. ``read_from`` and ``commit`` say where
    the values were copied from.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    set: str
    replaced: str
    impostor_wins: int
    games: int
    proof: tuple[int, int] | None = None
    no_proof: tuple[int, int] | None = None
    read_from: str
    commit: str

    @model_validator(mode="after")
    def _counts(self) -> BeforeCells:
        pairs = [(self.impostor_wins, self.games)]
        pairs += [pair for pair in (self.proof, self.no_proof) if pair is not None]
        for part, whole in pairs:
            if not 0 <= part <= whole or whole == 0:
                raise ValueError(f"{part} of {whole} is not a count of a population")
        return self


def read_before_cells(repo_root: Path) -> tuple[BeforeCells, ...]:
    """The pinned before cells, read and validated; any drift raises."""

    data = (repo_root / _RESULTS_BEFORE).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != _RESULTS_BEFORE_SHA256:
        raise BeforeCellsError(
            f"reads sha256 {digest}, not the pinned {_RESULTS_BEFORE_SHA256}; a "
            "before cell is history and is never edited"
        )
    payload = json.loads(data)
    if not isinstance(payload, list):
        raise BeforeCellsError("must hold one JSON list")
    entries = tuple(BeforeCells.model_validate(entry) for entry in payload)
    keys = [(entry.set, entry.replaced) for entry in entries]
    if len(set(keys)) != len(keys):
        raise BeforeCellsError("names one replaced recording twice")
    return entries


def before_cells(repo_root: Path, errors: list[str]) -> dict[str, BeforeCells]:
    """Each sample set's before cells, for the recording its bytes replaced.

    A set whose cells cannot be read is reported here once and left out, so
    the checks that read the cells do not report it again.
    """

    try:
        entries = read_before_cells(repo_root)
    except (OSError, ValueError) as error:
        errors.append(f"{_RESULTS_BEFORE}: {error}")
        return {}
    cells: dict[str, BeforeCells] = {}
    for name in _SAMPLE_SETS:
        path = _SAMPLE_REPLAY_DIR.format(name=name)
        try:
            replaced = replaced_era(era_of(path))
        except KeyError as error:
            errors.append(f"{_RESULTS_BEFORE}: {error.args[0]}")
            continue
        found = [
            entry
            for entry in entries
            if entry.set == path and entry.replaced == replaced
        ]
        if not found:
            errors.append(
                f"{_RESULTS_BEFORE}: holds no before cells for {path} at the "
                f"{replaced} recording it replaced."
            )
            continue
        cells[name] = found[0]
    return cells


def replaced_era(era: Era) -> str:
    """The id of the recording ``era``'s sets replaced; an unnamed era raises."""

    if era.id not in _REPLACED_ERAS:
        raise KeyError(f"no replaced era is named for the {era.id} era")
    return _REPLACED_ERAS[era.id]


# ── 2. The .env.example registries ───────────────────────────────────────────


def active_assignment(variable: str) -> re.Pattern[str]:
    """An uncommented assignment of ``variable``, in every form a loader reads.

    Both registry checks allow their switch only as a commented example.
    ``export AILIBI_X=1`` and ``AILIBI_X = 1`` set it exactly as the bare form
    does, so both have to be refused for that rule to mean what it says.
    """

    return re.compile(
        rf"^[ \t]*{_EXPORT_PREFIX}{re.escape(variable)}[ \t]*=", re.MULTILINE
    )


def check_lever_registry(text: str, errors: list[str]) -> None:
    """``text``, the .env.example body, against the live substrate registry.

    Toggleable levers must be documented with a commented example line showing
    the value this build resolves under a bare environment. Graduated levers
    must be named by their registry key — the recording stamp and the MANIFEST
    ``flags`` cell still carry them — but must never appear as an ``AILIBI_*=``
    assignment: their env gate is gone, so such a line documents nothing.

    "Active" is read through :func:`active_assignment`, so an ``export``
    prefix or padding around the ``=`` is refused with the bare form; all
    three are the same assignment to whatever loads the template.
    """

    section = lever_section(text)
    if section is None:
        errors.append(
            f"{_ENV_EXAMPLE}: missing the {_LEVER_SECTION_TITLE!r} section "
            "banner — the belief-substrate section cannot be located, so its "
            "claims cannot be audited against the registry."
        )
        return
    bare_defaults = substrate_flag_snapshot({})

    for key in TOGGLEABLE_SUBSTRATE_FLAG_KEYS:
        variable = env_var_for(key)
        if variable not in section:
            errors.append(
                f"{_ENV_EXAMPLE}: live toggle {key!r} is undocumented — "
                f"{variable} appears nowhere in the belief-substrate section, "
                "so the one substrate knob this build still reads is invisible "
                "to anyone copying the template."
            )
            continue
        default = "1" if bare_defaults.get(key, False) else "0"
        example = re.compile(
            rf"^#[ \t]*{re.escape(variable)}={default}[ \t]*$", re.MULTILINE
        )
        if example.search(section) is None:
            errors.append(
                f"{_ENV_EXAMPLE}: live toggle {key!r} has no commented example "
                f"line '# {variable}={default}' in the belief-substrate "
                "section showing its bare-environment default in this build — "
                "an example elsewhere in the file is not where a reader copying "
                "the lever section looks."
            )
        active = active_assignment(variable)
        if active.search(text) is not None:
            errors.append(
                f"{_ENV_EXAMPLE}: active export of live toggle {key!r} — an "
                f"uncommented '{variable}=' line would flip anyone who copies "
                "the template away from the bare baseline-6 substrate; the "
                "toggle may appear only as the commented bare-default example."
            )

    note = graduated_note(section)
    if note is None:
        errors.append(
            f"{_ENV_EXAMPLE}: missing the {_GRADUATED_NOTE_MARKER!r} note in "
            "the belief-substrate section — the graduated/always-ON labels "
            "have no home, so they cannot be audited against the registry."
        )
    else:
        # The note's WORDING is the load-bearing label, not just the key
        # names: it must keep saying always-ON, and must never drift back to
        # describing a graduated lever as default-OFF/switchable.
        if "always ON" not in note:
            errors.append(
                f"{_ENV_EXAMPLE}: the graduated-levers note no longer says "
                "'always ON' — the graduated state is the note's one "
                "load-bearing label."
            )
        stale_wording = re.search(r"default[-\s]?off", note, re.IGNORECASE)
        if stale_wording is not None:
            errors.append(
                f"{_ENV_EXAMPLE}: the graduated-levers note contains "
                f"{stale_wording.group(0)!r} — graduated levers are "
                "unconditionally ON; default-OFF wording in the note is the "
                "exact drift class the graduation-sweep convention "
                "(AGENTS.md) exists to prevent."
            )

    toggleable = set(TOGGLEABLE_SUBSTRATE_FLAG_KEYS)
    for key in SUBSTRATE_FLAG_KEYS:
        if key in toggleable:
            continue
        if note is not None and re.search(rf"\b{re.escape(key)}\b", note) is None:
            errors.append(
                f"{_ENV_EXAMPLE}: graduated lever {key!r} is missing from the "
                "graduated-levers note; orchestrator.replay still stamps it "
                "into every recording, so the note must keep naming it — a "
                "mention elsewhere in the file or section does not label the "
                "lever graduated/always-ON."
            )
        assignment = f"{env_var_for(key)}="
        if assignment in text:
            errors.append(
                f"{_ENV_EXAMPLE}: {assignment!r} documents a knob that no "
                f"longer exists — {key!r} graduated to unconditionally ON and "
                "its env gate was deleted, so setting the variable does nothing."
            )

    registry = set(SUBSTRATE_FLAG_KEYS)
    for assigned in _ENV_ASSIGNMENT.finditer(section):
        key = assigned.group(1).removeprefix("AILIBI_").lower()
        if key in registry:
            continue  # toggleable: the active check above; graduated: rejected
        errors.append(
            f"{_ENV_EXAMPLE}: the belief-substrate section advertises "
            f"'{assigned.group(1)}=', but {key!r} is not in the live lever "
            "registry — a misspelled or never-registered knob this build does "
            "not read."
        )


def check_experiment_registry(text: str, errors: list[str]) -> None:
    """``text``, the .env.example body, against the experiment registry.

    The four meeting-experiment switches are as much a lever register as the
    substrate keys, and .env.example is the one place that states them, their
    prerequisites and their conflicts. Until this check existed the register
    was unguarded: all four lines could be deleted, renamed or misspelled with
    every gate green, while dropping one substrate lever failed loudly.

    Each switch must appear in the experiments section as a commented example
    line showing the value a bare environment resolves -- read from
    :class:`~meetings.evidence_profile.MeetingEvidenceProfile` itself, never
    typed here -- and never as an active export anywhere in the template: a
    copied .env that turned a candidate ON would move meeting behaviour that
    stays default-OFF until an adopting record. An ``AILIBI_*=`` line in the
    section that no registry name claims is a knob this build does not read.

    "Active" is read through :func:`active_assignment` and the unregistered-name
    scan through :data:`_ENV_ASSIGNMENT`, so an ``export`` prefix or padding
    around the ``=`` is refused with the bare form; all three are the same
    assignment to whatever loads the template.
    """

    section = experiment_section(text)
    if section is None:
        errors.append(
            f"{_ENV_EXAMPLE}: missing the {_EXPERIMENT_SECTION_TITLE!r} section "
            "banner — the experiment register cannot be located, so its claims "
            "cannot be audited against meetings.evidence_profile."
        )
        return
    bare = MeetingEvidenceProfile.from_environment({})
    for variable, field in EXPERIMENT_ENV_NAMES.items():
        if variable not in section:
            errors.append(
                f"{_ENV_EXAMPLE}: experiment switch {variable} is undocumented "
                "— it appears nowhere in the independently-versioned-experiments "
                "section, so the one register naming this build's meeting "
                "experiments is invisible to anyone copying the template."
            )
            continue
        default = "0" if getattr(bare, field) is None else "1"
        example = re.compile(
            rf"^#[ \t]*{re.escape(variable)}={default}[ \t]*$", re.MULTILINE
        )
        if example.search(section) is None:
            errors.append(
                f"{_ENV_EXAMPLE}: experiment switch {variable} has no commented "
                f"example line '# {variable}={default}' in the "
                "independently-versioned-experiments section showing the value "
                "a bare environment resolves for it in this build."
            )
        active = active_assignment(variable)
        if active.search(text) is not None:
            errors.append(
                f"{_ENV_EXAMPLE}: active export of experiment switch {variable} "
                "— an uncommented line would turn a candidate ON for anyone who "
                "copies the template, and every candidate stays default-OFF "
                "until an adopting record; it may appear only as the commented "
                "bare-default example."
            )

    for assigned in _ENV_ASSIGNMENT.finditer(section):
        if assigned.group(1) in EXPERIMENT_ENV_NAMES:
            continue
        errors.append(
            f"{_ENV_EXAMPLE}: the independently-versioned-experiments section "
            f"advertises '{assigned.group(1)}=', which is not in "
            "meetings.evidence_profile's experiment registry — a renamed, "
            "misspelled or never-registered switch this build does not read."
        )


def banner_section(text: str, title: str) -> str | None:
    """One .env.example section body, or ``None`` if unlocatable.

    The section runs from the dashed rule closing its title banner to the
    dashed rule opening the next section's banner (or end of file).
    """

    heading = text.find(title)
    if heading == -1:
        return None
    rules = [m for m in _SECTION_RULE.finditer(text) if m.start() > heading]
    if not rules:
        return None
    start = rules[0].end()
    end = rules[1].start() if len(rules) > 1 else len(text)
    return text[start:end]


def lever_section(text: str) -> str | None:
    """.env.example's belief-substrate section, or ``None`` if unlocatable."""

    return banner_section(text, _LEVER_SECTION_TITLE)


def experiment_section(text: str) -> str | None:
    """.env.example's independently-versioned-experiments section."""

    return banner_section(text, _EXPERIMENT_SECTION_TITLE)


def graduated_note(section: str) -> str | None:
    """The graduated-levers note inside the belief-substrate section.

    The note is the contiguous comment block opening with
    :data:`_GRADUATED_NOTE_MARKER` and ending at the first blank line — the
    one place the graduated/always-ON labels count. ``None`` when the marker
    is missing (format drift the caller reports).
    """

    marker = section.find(_GRADUATED_NOTE_MARKER)
    if marker == -1:
        return None
    rest = section[marker:]
    blank = _BLANK_LINE.search(rest)
    return rest if blank is None else rest[: blank.start()]


def env_var_for(key: str) -> str:
    """The ``AILIBI_*`` variable a substrate-lever registry key derives."""

    return f"AILIBI_{key.upper()}"


# ── 3. The results table ─────────────────────────────────────────────────────


def check_result_sources(
    repo_root: Path,
    readme: str,
    before: Mapping[str, BeforeCells],
    errors: list[str],
) -> None:
    """The results figures, re-derived from the bytes that own them.

    * the replay count, from the replay files the verifier reconstructs;
    * the citation figure, from the pinned assertions in the committed
      instrument test;
    * the vent row and the proof row, from the shown set's column of the
      census's vent-proof table (:func:`check_proof_row`).

    That the replays still *reconstruct* is ``scripts/verify_samples.sh``'s
    answer, and the citation counts come from a full pass over the 9p2i set
    that ``tests/eval/test_vj_instruments.py`` already makes. This module is
    the cheap half, so it binds the README to those instruments' pins rather
    than repeating their work. The win rates are re-derived by
    :func:`check_sample_provenance` and the process rows by
    :func:`check_process_rows`.
    """

    rows = results_rows(readme)
    if rows is None:
        errors.append(
            f"{_README}: no results table with a "
            f"'{' | '.join(_RESULTS_TABLE_HEADER)}' header row — its figures have "
            "nothing to be checked against."
        )
        return
    figures = reject_repeated_claims(_README, rows, errors)

    # The verifier's own population, not a glob of the directory: an audit
    # sidecar or a hand-named debug file is a .jsonl that
    # ``scripts/verify_samples.sh`` never reconstructs, and counting it would
    # inflate the figure this row claims was verified.
    replays = committed_sample_replays(repo_root)
    if not replays:
        # A vacuous pass is the one outcome this check must not have: an empty
        # corpus would otherwise let any replay figure stand.
        errors.append(
            "replays/samples/: no committed replays found, so the "
            f"{_REPLAY_COUNT_CLAIM!r} figure cannot be re-derived."
        )
    else:
        compare_result_figure(
            _REPLAY_COUNT_CLAIM,
            figures,
            fraction_figure(replays, replays),
            f"the {replays} committed replays under replays/samples/",
            errors,
        )

    pins = citation_pins(repo_root, errors)
    if pins:
        missing = [name for name in _CITATION_PIN_NAMES if name not in pins]
        if missing:
            errors.append(
                f"{_CITATION_INSTRUMENT}: no pinned assertion for "
                f"{', '.join(missing)} — the {_README} citation figure has no "
                "committed source to re-derive it from."
            )
        else:
            dangling = (
                pins["turn_citations_dangling"] + pins["observation_citations_dangling"]
            )
            cited = fraction_figure(pins["cited_eject_ballots"], pins["eject_ballots"])
            expected = f"{cited}, " + (
                "zero dangling" if dangling == 0 else f"{dangling} dangling"
            )
            compare_result_figure(
                _CITATION_CLAIM,
                figures,
                expected,
                f"the pins in {_CITATION_INSTRUMENT}",
                errors,
            )

    try:
        vent = census_vent_cells((repo_root / _CENSUS_PAGE).read_text(encoding="utf-8"))
    except (OSError, CensusPageError) as error:
        errors.append(
            f"{_CENSUS_PAGE}: {error} — the {_README} vent and proof rows have "
            "nothing to be derived from."
        )
        return
    compare_result_figure(
        _VENT_CLAIM,
        figures,
        fraction_figure(*vent.band_impostors),
        census_source(),
        errors,
    )
    check_proof_row(readme, figures, vent, before.get(_SHOWN_SET), errors)


def committed_sample_replays(repo_root: Path) -> int:
    """How many replays the verifier reconstructs across the two sample sets.

    The verifier's own population, not a glob of the directory: an audit
    sidecar or a hand-named debug file is a .jsonl that
    ``scripts/verify_samples.sh`` never reconstructs.
    """

    return sum(
        len(sample_paths(repo_root / _SAMPLE_REPLAY_DIR.format(name=name)))
        for name in _SAMPLE_SETS
    )


def citation_pins(repo_root: Path, errors: list[str]) -> dict[str, int]:
    """The 9p2i ballot-citation cells, from the instrument's own assertions."""

    instrument = read_document(repo_root, _CITATION_INSTRUMENT, errors)
    if instrument is None:
        return {}
    return {
        match.group(1): int(match.group(2))
        for match in _CITATION_PIN.finditer(instrument)
    }


def check_proof_row(
    readme: str,
    figures: Mapping[str, str],
    vent: VentCells,
    before: BeforeCells | None,
    errors: list[str],
) -> None:
    """The proof row: figure and injustice clause from the census, before cell frozen.

    The vent band is the row's "with proof" half and every other ejection is
    the "without" half, so both figures come from the band's impostor and
    crewmate cells. The row also says every innocent ejection sits in the
    no-proof half, which holds only while the band holds no crewmate.
    """

    (band, impostors), (crew_band, crew) = vent.band_impostors, vent.band_crew
    no_proof = impostors - band
    compare_result_figure(
        _PROOF_CLAIM,
        figures,
        partition_figure(
            (band, band + crew_band), (no_proof, no_proof + crew - crew_band)
        ),
        census_source(),
        errors,
    )
    check_injustice_cell(readme, crew, crew_band, errors)
    if before is None:
        return  # before_cells reports the missing entry
    if before.proof is None or before.no_proof is None:
        errors.append(
            f"{_RESULTS_BEFORE}: the {before.set} entry carries no proof cells, so "
            f"the {_PROOF_CLAIM!r} before cell has no source."
        )
        return
    compare_before_figure(
        readme,
        _PROOF_CLAIM,
        partition_figure(before.proof, before.no_proof),
        _RESULTS_BEFORE,
        errors,
    )


def check_injustice_cell(
    readme: str, innocent: int, proof_innocent: int, errors: list[str]
) -> None:
    """The proof row's injustice clause, held to the census's crewmate cells.

    The row does not only state two figures: it states that every innocent
    ejection landed in the cell without proof. The required wording carries the
    placement, not just the count. A row reading "15 of 15 innocent ejections
    sit in the proof-present cell" states the same number and the opposite
    finding, so matching the count alone would gate shape rather than meaning.
    """

    row = results_row(readme, _PROOF_CLAIM)
    if row is None:
        return  # compare_result_figure already reported the missing row
    if proof_innocent:
        errors.append(
            f"{_README}: the results row {_PROOF_CLAIM!r} says every innocent "
            f"ejection sits in the no-proof cell, but {census_source()} puts "
            f"{proof_innocent} crewmate ejection(s) in the vent band."
        )
        return
    stated = _INJUSTICE_CLAIM.format(count=innocent)
    if stated not in " | ".join(row):
        errors.append(
            f"{_README}: the results row {_PROOF_CLAIM!r} does not state "
            f"{stated!r} — {census_source()} counts {innocent} crewmate "
            "ejections, none of them in the vent band."
        )


class CensusPageError(ValueError):
    """The census page lacks the section, table, column or cell the README reads."""


class VentCells(NamedTuple):
    """The shown set's vent-proof cells on the census page, each ``(k, n)``.

    ``meetings``: meetings with vent proof, of all meetings. ``band_impostors``
    and ``band_crew``: impostor and crewmate ejections in the vent band, of all
    impostor and all crewmate ejections. ``unflagged``: ejections in meetings
    without vent proof that removed an impostor, of all those ejections.
    """

    meetings: tuple[int, int]
    band_impostors: tuple[int, int]
    band_crew: tuple[int, int]
    unflagged: tuple[int, int]


def census_vent_cells(page: str) -> VentCells:
    """The shown set's column of the census's vent-proof table.

    The section runs from its heading to the next heading; its table is the
    first one whose header opens with ``cell``, and the column is the one whose
    header names the shown set. Raises :class:`CensusPageError` naming a missing
    section, table, column or row, or a cell that is not ``k/n``.
    """

    label = _SET_LABEL.format(name=_SHOWN_SET)
    lines = page.splitlines()
    if _CENSUS_SECTION not in lines:
        raise CensusPageError(f"no {_CENSUS_SECTION!r} section")
    header: list[str] | None = None
    rows: dict[str, list[str]] = {}
    for line in lines[lines.index(_CENSUS_SECTION) + 1 :]:
        cells = table_cells(line)
        if _HEADING.match(line) or (cells is None and header is not None):
            break
        if cells is None:
            continue
        if header is None:
            header = cells if cells[0] == _CENSUS_FIRST_HEADER else None
        elif not all(_TABLE_RULE_CELL.match(cell) for cell in cells):
            rows[cells[0]] = cells
    if header is None:
        raise CensusPageError(f"the {_CENSUS_SECTION!r} section has no table")
    columns = [index for index, cell in enumerate(header) if cell.startswith(label)]
    if len(columns) != 1:
        raise CensusPageError(f"the {_CENSUS_SECTION!r} table has no {label} column")

    def cell(row: str) -> tuple[int, int]:
        cells = rows.get(row)
        match = None
        if cells is not None and len(cells) == len(header):
            match = _CENSUS_FRACTION.match(cells[columns[0]])
        if match is None:
            raise CensusPageError(
                f"the {_CENSUS_SECTION!r} table has no {label} {row!r} cell "
                "reading 'k/n'"
            )
        return int(match.group(1)), int(match.group(2))

    return VentCells(
        meetings=cell(_CENSUS_MEETINGS),
        band_impostors=cell(_CENSUS_BAND_IMPOSTORS),
        band_crew=cell(_CENSUS_BAND_CREW),
        unflagged=cell(_CENSUS_UNFLAGGED),
    )


def shown_set_vent_cells(repo_root: Path) -> VentCells | None:
    """The census cells :func:`check_result_sources` reads, or ``None``.

    ``None`` when the page cannot be read: that check reports it by name, so
    the prose check that reads the same cells after it does not report it again.
    """

    try:
        page = (repo_root / _CENSUS_PAGE).read_text(encoding="utf-8")
        return census_vent_cells(page)
    except (OSError, CensusPageError):
        return None


def census_source() -> str:
    """How an error names the census cells it was held to."""

    label = _SET_LABEL.format(name=_SHOWN_SET)
    return f"the {label} column of {_CENSUS_PAGE}'s vent-proof table"


def partition_figure(proof: tuple[int, int], non_proof: tuple[int, int]) -> str:
    """The proof row's figure, its two halves as the README states them."""

    return f"{fraction_figure(*proof)} vs {fraction_figure(*non_proof)}"


def fraction_figure(numerator: int, denominator: int) -> str:
    """One fraction as the results table states it: ``k of n (p%)``.

    The percentage is rounded the way the win rates are, ``round(100 * k / n)``,
    so every percentage the table prints follows one rule. A fraction over no
    population has no percentage and raises rather than printing one.
    """

    if denominator <= 0:
        raise ValueError(
            f"{numerator} of {denominator}: a fraction over no population has no "
            "percentage to state"
        )
    return f"{numerator} of {denominator} ({round(100 * numerator / denominator)}%)"


def compare_result_figure(
    claim: str,
    figures: Mapping[str, str],
    expected: str,
    source: str,
    errors: list[str],
) -> None:
    """One results row, held to the figure its source recomputes to."""

    stated = figures.get(claim)
    if stated is None:
        errors.append(
            f"{_README}: the results table has no {claim!r} row — the figure "
            f"{source} recomputes to ({expected!r}) has nowhere to be stated, "
            "so nothing is being checked."
        )
    elif stated != expected:
        errors.append(
            f"{_README}: the results row {claim!r} reads {stated!r}, but "
            f"{source} recomputes to {expected!r}."
        )


def compare_before_figure(
    readme: str,
    claim: str,
    expected: str,
    source: str,
    errors: list[str],
) -> None:
    """One results row's before cell, held to the recording that owns it."""

    before = results_before_column(readme)
    if before is None:
        errors.append(
            f"{_README}: the results table has no {_BEFORE_COLUMN_HEADER!r} "
            "column — every figure a recording moved states what it moved from, "
            "so the column is the page's own before/after."
        )
        return
    stated = before.get(claim)
    if stated is None:
        errors.append(
            f"{_README}: the results row {claim!r} has no "
            f"{_BEFORE_COLUMN_HEADER!r} cell."
        )
    elif strip_links(stated) != expected:
        errors.append(
            f"{_README}: the {_BEFORE_COLUMN_HEADER!r} cell of results row "
            f"{claim!r} reads {stated!r}, but {source} recomputes to "
            f"{expected!r}."
        )


def results_before_column(markdown: str) -> dict[str, str] | None:
    """Claim -> before cell for the results table, or ``None`` if it has none.

    A row whose width does not match the header's maps to the empty string
    rather than dropping out or reading a neighbour's cell: a truncated row has
    no history cell, which is the same finding as an empty one, and a row that
    dropped a delimiter would otherwise be checked against the wrong column.
    Claims are keyed with their links reduced to text, as :func:`results_rows`
    keys them.
    """

    before: dict[str, str] | None = None
    index = width = 0
    for line in markdown.splitlines():
        cells = table_cells(line)
        if cells is None or len(cells) < 2:
            if before is not None:
                break
            continue
        if before is None:
            plain = [strip_links(cell) for cell in cells]
            if tuple(cells[:2]) == _RESULTS_TABLE_HEADER:
                if _BEFORE_COLUMN_HEADER not in plain:
                    return None
                before, index, width = (
                    {},
                    plain.index(_BEFORE_COLUMN_HEADER),
                    len(cells),
                )
            continue
        if all(_TABLE_RULE_CELL.match(cell) for cell in cells):
            continue
        before.setdefault(
            strip_links(cells[0]), cells[index] if len(cells) == width else ""
        )
    return before


def reject_repeated_claims(
    document: str, rows: Sequence[tuple[str, str]], errors: list[str]
) -> dict[str, str]:
    """Claim -> figure for ``rows``, with every repeated claim reported.

    The first figure wins the mapping, so a stale copy left beside a corrected
    row is reported rather than silently read in its place.
    """

    figures: dict[str, str] = {}
    for claim, figure in rows:
        if claim in figures:
            errors.append(
                f"{document}: the results table states {claim!r} twice "
                f"({figures[claim]!r}, then {figure!r}) — one claim, one row, "
                "or the page answers the same question two ways."
            )
            continue
        figures[claim] = figure
    return figures


def results_rows(markdown: str) -> list[tuple[str, str]] | None:
    """The ``What`` / ``Figure`` rows of the document's results table, in order.

    Located by its header cells rather than by the heading above it, so
    renaming the section does not silently disable the checks. A list rather
    than a mapping, because a repeated claim is itself a finding and collapsing
    it here would erase the evidence for it. A claim is read with its links
    reduced to their text, so a row may link a term to the glossary and still
    state the same claim. ``None`` when no such table exists (format drift the
    caller reports).
    """

    rows: list[tuple[str, str]] | None = None
    for line in markdown.splitlines():
        cells = table_cells(line)
        if cells is None or len(cells) < 2:
            if rows is not None:
                break
            continue
        if rows is None:
            if tuple(cells[:2]) == _RESULTS_TABLE_HEADER:
                rows = []
            continue
        if all(_TABLE_RULE_CELL.match(cell) for cell in cells):
            continue
        rows.append((strip_links(cells[0]), cells[1]))
    return rows


def results_row(markdown: str, claim: str) -> list[str] | None:
    """Every cell of the results row stating ``claim``, or ``None``.

    :func:`results_rows` keeps only the two compared cells; a row whose source
    column carries a claim of its own needs the whole row.
    """

    for line in markdown.splitlines():
        cells = table_cells(line)
        if cells is not None and cells and strip_links(cells[0]) == claim:
            return cells
    return None


def table_cells(line: str) -> list[str] | None:
    """The cells of one markdown table row, or ``None`` if it is not one."""

    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    return [cell.strip() for cell in stripped.strip("|").split("|")]


# ── The process rows, read off the scorecard page ────────────────────────────


class ScorecardPageError(ValueError):
    """The scorecard page lacks a section, table, column, row or line the README reads."""


class _ProcessCells(NamedTuple):
    """One set's process cells on the scorecard page.

    ``rows`` maps each process row's page label to its ``(value, before)`` cells,
    verbatim; ``teammate_coerced`` is the row-7 detail line's teammate count.
    """

    rows: dict[str, tuple[str, str]]
    teammate_coerced: int


def check_process_rows(repo_root: Path, readme: str, errors: list[str]) -> None:
    """The four process rows, held to the scorecard page.

    The README leads with how each vote was cast: on a line its voter held,
    with or against its own top suspect, with a reason, and as its voter wrote
    it. Each row's figure and before cell is the shown set's own cell on
    ``docs/process-scorecard.md``, restated in the table's ``k of n (p%)`` form
    (:func:`scorecard_fraction`) — the generated markdown, which
    ``scripts/publish_process_scorecard.py --check`` recomputes from the
    recordings — and its before cell is the page's frozen before column, the
    block of the era the shown set's recording replaced. The authored share
    carries the teammate firewall's count beside it, from the row-7 detail
    line. A page that lacks the section, the table, a row, the before column or
    the detail line is refused by name rather than read around.
    """

    page = read_document(repo_root, _SCORECARD_PAGE, errors)
    if page is None:
        return
    path = _SAMPLE_REPLAY_DIR.format(name=_SHOWN_SET)
    label = _SET_LABEL.format(name=_SHOWN_SET)
    try:
        cells = scorecard_process_cells(page, label, replaced_era(era_of(path)))
        expected = {
            claim: (
                scorecard_fraction(cells.rows[row][0]),
                scorecard_fraction(cells.rows[row][1]),
            )
            for claim, row in _PROCESS_ROWS
        }
    except (KeyError, ScorecardPageError) as error:
        errors.append(
            f"{_SCORECARD_PAGE}: {error.args[0]} — the four process rows the "
            "results table leads with have no committed source to be held to."
        )
        return
    value, before = expected[_AUTHORED_CLAIM]
    expected[_AUTHORED_CLAIM] = (
        f"{value}; {coerced_clause(cells.teammate_coerced)}",
        before,
    )
    source = f"the {label} table of {_SCORECARD_PAGE}"
    rows = results_rows(readme)
    if rows is None:
        return  # check_result_sources reports the missing table
    figures = dict(rows)
    for claim, (figure, history) in expected.items():
        compare_result_figure(claim, figures, figure, source, errors)
        if claim in figures:
            compare_before_figure(readme, claim, history, source, errors)


def scorecard_process_cells(page: str, label: str, before_era: str) -> _ProcessCells:
    """The process cells of ``label``'s table on the generated scorecard page.

    The section runs from the ``### <label>`` heading to the next heading. Its
    table is the one whose header opens ``| # | row |``; the before column is
    the one whose header names ``before_era``, the era the set's recording
    replaced, so a page whose frozen block belongs to another era is refused
    rather than quoted. Raises :class:`ScorecardPageError` naming the missing
    section, table, column, row or detail line.
    """

    heading = _SCORECARD_SET_HEADING.format(label=label)
    header, table, section = scorecard_set_table(page, label)
    marker = _SCORECARD_BEFORE_HEADER.format(era=before_era)
    before = [index for index, cell in enumerate(header) if cell.startswith(marker)]
    if not before:
        raise ScorecardPageError(
            f"the {heading!r} table has no before column naming the {before_era} era"
        )
    if _SCORECARD_VALUE_HEADER not in header:
        raise ScorecardPageError(
            f"the {heading!r} table has no {_SCORECARD_VALUE_HEADER!r} column"
        )
    value = header.index(_SCORECARD_VALUE_HEADER)
    rows: dict[str, tuple[str, str]] = {}
    for _, row in _PROCESS_ROWS:
        cells = table.get(row)
        if cells is None or len(cells) != len(header):
            raise ScorecardPageError(f"the {heading!r} table has no {row!r} row")
        rows[row] = (cells[value], cells[before[0]])
    detail = [line for line in section if line.startswith(_SCORECARD_REWRITES)]
    if not detail:
        raise ScorecardPageError(
            f"the {heading!r} section has no {_SCORECARD_REWRITES.strip()!r} line"
        )
    stated = detail[0][len(_SCORECARD_REWRITES) :].split(";", 1)[0].strip()
    counts: dict[str, int] = {}
    if stated != _SCORECARD_NO_REWRITES:
        for entry in stated.split(", "):
            match = _SCORECARD_REWRITE_ENTRY.match(entry)
            if match is None:
                raise ScorecardPageError(
                    f"the {heading!r} section's row-7 detail reads {stated!r}, "
                    "not a list of typed rewrite reasons with their counts"
                )
            counts[match.group(1)] = int(match.group(2))
    return _ProcessCells(rows, counts.get(_TEAMMATE_REASON, 0))


def scorecard_set_table(
    page: str, label: str
) -> tuple[list[str], dict[str, list[str]], list[str]]:
    """``label``'s section on the generated scorecard page, and its table.

    The section runs from the ``### <label>`` heading to the next heading; its
    table is the one whose header opens ``| # | row |``. Returns the header
    cells, the table's rows keyed by their ``row`` cell, and the section's
    lines. Raises :class:`ScorecardPageError` naming a missing section or table.
    """

    heading = _SCORECARD_SET_HEADING.format(label=label)
    lines = page.splitlines()
    if heading not in lines:
        raise ScorecardPageError(f"no {heading!r} section")
    section: list[str] = []
    for line in lines[lines.index(heading) + 1 :]:
        if _HEADING.match(line):
            break
        section.append(line)
    header: list[str] | None = None
    table: dict[str, list[str]] = {}
    for line in section:
        cells = table_cells(line)
        if cells is None:
            if header is not None:
                break
            continue
        if header is None:
            if tuple(cells[: len(_SCORECARD_HEADER)]) == _SCORECARD_HEADER:
                header = cells
            continue
        if all(_TABLE_RULE_CELL.match(cell) for cell in cells):
            continue
        table[cells[1] if len(cells) > 1 else ""] = cells
    if header is None:
        raise ScorecardPageError(
            f"the {heading!r} section has no '| {' | '.join(_SCORECARD_HEADER)} |' table"
        )
    return header, table, section


def shown_set_values(repo_root: Path) -> dict[str, str] | None:
    """Each row's value cell in the shown set's table on the scorecard page.

    ``None`` when the page, the set's section, its table or the value column
    cannot be read: :func:`check_process_rows` reads the same table first and
    reports each of those by name, so the prose checks that read it after do
    not report it again.
    """

    try:
        page = (repo_root / _SCORECARD_PAGE).read_text(encoding="utf-8")
        header, table, _ = scorecard_set_table(page, _SET_LABEL.format(name=_SHOWN_SET))
    except (OSError, ScorecardPageError):
        return None
    if _SCORECARD_VALUE_HEADER not in header:
        return None
    value = header.index(_SCORECARD_VALUE_HEADER)
    return {
        row: cells[value] for row, cells in table.items() if len(cells) == len(header)
    }


def coerced_clause(count: int) -> str:
    """The teammate firewall's count, as the authored-share row states it."""

    if count == 1:
        return "1 impostor vote against a partner turned into a skip"
    return f"{count} impostor votes against a partner turned into skips"


def scorecard_fraction(cell: str) -> str:
    """A scorecard page cell, ``k/n = rate``, restated as the results table states it.

    The page is generated and stays as it is printed; its two counts are read
    and handed to :func:`fraction_figure`. Raises :class:`ScorecardPageError`
    for a cell of any other shape, so a page format change is named rather than
    read around.
    """

    match = _SCORECARD_FRACTION.match(cell.strip())
    if match is None:
        raise ScorecardPageError(f"the cell {cell!r} is not a 'k/n = rate' fraction")
    return fraction_figure(int(match.group(1)), int(match.group(2)))


# ── 4. The real-report example ───────────────────────────────────────────────


def check_populated_report_example(
    repo_root: Path, readme: str, errors: list[str]
) -> None:
    """The README's real-report example, held to that report's own numbers.

    The front door hands a reader a populated report precisely because the
    default fake provider produces an empty one. Copying its headline counts
    into prose would put them one re-record away from being someone else's
    numbers, so each is re-derived from the report's own
    ``vote_correctness`` block: every ejection, those that removed an impostor,
    and those whose meeting carried evidence naming the player ejected. The
    paragraph states counts, not the two rates taken over them.
    """

    paragraph = next(
        (
            block
            for block in readme.split("\n\n")
            if _POPULATED_REPORT in block and _EXAMPLE_ANCHOR in block
        ),
        None,
    )
    if paragraph is None:
        errors.append(
            f"{_README}: no paragraph naming {_POPULATED_REPORT} beside "
            f"'{_EXAMPLE_ANCHOR}' — the real-report example has no home to "
            "check, so its numbers are unverified prose."
        )
        return
    block = read_vote_correctness_block(repo_root, _POPULATED_REPORT, errors)
    if block is None:
        return
    counts: dict[str, int] = {}
    for label, key, _ in _REPORT_EXAMPLE_CLAIMS:
        value = block.get(key)
        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(
                f"{_POPULATED_REPORT}: {key} is {value!r}, not a count — the "
                f"{_README} example's {label} claim cannot be re-derived."
            )
            continue
        counts[key] = value
    if len(counts) != len(_REPORT_EXAMPLE_CLAIMS):
        return  # a wording naming a count the report lacks cannot be filled in
    for _, key, expected in _REPORT_EXAMPLE_CLAIMS:
        claim = expected.format_map(counts)
        if claim not in paragraph:
            errors.append(
                f"{_README}: the real-report example does not state "
                f"{claim!r} — {_POPULATED_REPORT} records {key} as {counts[key]!r}."
            )


def read_vote_correctness_block(
    repo_root: Path, relative_path: str, errors: list[str]
) -> dict[str, object] | None:
    """The report's ``vote_correctness`` object, without parsing the document."""

    return read_report_block(repo_root, relative_path, _VOTE_CORRECTNESS_KEY, errors)


def read_report_block(
    repo_root: Path, relative_path: str, key: str, errors: list[str]
) -> dict[str, object] | None:
    """One named object out of an eval report, without parsing the document.

    The committed reports reach tens of megabytes, so the block is decoded from
    its own ``"<name>":`` key rather than by loading the whole file. Format
    drift (no such key, or a block that never closes) is reported, never
    papered over.
    """

    path = repo_root / relative_path
    block: list[str] = []
    try:
        # Gzipped since 2026-09-22, and still STREAMED: the archive iterates
        # line by line exactly as the plain file did, so the whole document is
        # never loaded to read one block.
        with open_report_text(path) as handle:
            depth = 0
            for line in handle:
                if not block:
                    if not line.strip().startswith(key):
                        continue
                    block.append("{")
                    depth = 1
                    continue
                depth += line.count("{") - line.count("}")
                block.append(line)
                if depth <= 0 or len(block) > _REPORT_BLOCK_MAX_LINES:
                    break
    except OSError as exc:
        errors.append(f"{relative_path}: unreadable ({exc}).")
        return None

    if not block:
        errors.append(
            f"{relative_path}: no {key} key — the eval-report format drifted, so "
            "the prose derived from that block has no source."
        )
        return None
    try:
        decoded, _ = json.JSONDecoder().raw_decode("".join(block))
    except ValueError as exc:
        decoded = None
        errors.append(
            f"{relative_path}: the {key} block does not parse as one JSON "
            f"object ({exc})."
        )
    if not isinstance(decoded, dict):
        if decoded is not None:
            errors.append(f"{relative_path}: {key} is not a JSON object.")
        return None
    return decoded


# ── 5. The prose figures ─────────────────────────────────────────────────────


class _ProseClaim(NamedTuple):
    """One claim shape the README may state, and the figures it must state.

    ``expected`` holds one value per capture group of ``pattern``, compared
    case-insensitively; a ``required`` claim must be stated at least once.
    """

    pattern: re.Pattern[str]
    expected: tuple[str, ...]
    required: bool = True


def check_prose_claims(
    blocks: Sequence[tuple[int, str]],
    claims: Sequence[_ProseClaim],
    source: str,
    errors: list[str],
) -> None:
    """Every statement of each claim shape in ``blocks``, held to ``source``.

    ``blocks`` are ``(line, text)`` pairs of the README. Claims are scanned in
    order, and a later claim's match inside text an earlier claim already
    matched is the same statement, reported once: a narrow refusal ("k of n")
    listed after the sentence it sits in does not re-report that sentence.
    """

    found = [False] * len(claims)
    for number, text in blocks:
        taken: list[tuple[int, int]] = []
        for index, claim in enumerate(claims):
            wanted = tuple(value.casefold() for value in claim.expected)
            for match in claim.pattern.finditer(text):
                if any(
                    start < match.end() and match.start() < end for start, end in taken
                ):
                    continue
                taken.append(match.span())
                found[index] = True
                if tuple(group.casefold() for group in match.groups()) == wanted:
                    continue
                errors.append(
                    f"{_README}:{number}: the claim {match.group(0)!r} disagrees "
                    f"with {source}, which makes it "
                    f"{restated_claim(match, claim.expected)!r}."
                )
    for claim, seen in zip(claims, found, strict=True):
        if claim.required and not seen:
            errors.append(
                f"{_README}: no sentence matching {claim.pattern.pattern!r} — what "
                f"{source} gives is no longer stated, so nothing binds the prose "
                "to it."
            )


def restated_claim(match: re.Match[str], values: Sequence[str]) -> str:
    """``match``'s text with each capture group replaced by its derived value."""

    text, offset = match.group(0), match.start()
    pieces: list[str] = []
    cursor = 0
    for group, value in enumerate(values, start=1):
        start, end = match.span(group)
        pieces += [text[cursor : start - offset], value]
        cursor = end - offset
    return "".join(pieces) + text[cursor:]


def percent(numerator: int, denominator: int) -> str:
    """A share as the front door prints it, rounded as :func:`fraction_figure`."""

    return str(round(100 * numerator / denominator))


def repeat_word(count: int) -> str:
    """How often, as the README says it: "once", "twice", "three times"."""

    return _REPEAT_WORDS.get(count, f"{number_word(count)} times")


def number_word(count: int) -> str:
    """A small count as the front door spells it, or as digits beyond the list."""

    return _NUMBER_WORDS[count] if count < len(_NUMBER_WORDS) else str(count)


def check_role_correct_prose(repo_root: Path, readme: str, errors: list[str]) -> None:
    """The README's account of votes for and against the voter's top suspect.

    The shown set's row-2 role-correct cell on the scorecard page owns the
    figures: how many crew eject ballots followed the top suspect and how many
    of those hit an impostor, the same for the ballots against it, and the
    chance rate. The README must state them as "hit an impostor k of n times
    (p%)", "the n against it hit one <k> (p%)" and "chance is about one in
    <N>", and any other "k of <followers>" claim must name the same count, so a
    re-record that moves the cell cannot leave the sentence telling the old one.
    """

    values = shown_set_values(repo_root)
    if values is None:
        return  # check_process_rows reports the unreadable page
    label = _SET_LABEL.format(name=_SHOWN_SET)
    cell = values.get(_ROLE_CORRECT_ROW)
    if cell is None:
        errors.append(
            f"{_SCORECARD_PAGE}: the {label} table has no {_ROLE_CORRECT_ROW!r} "
            f"row — the {_README} sentence on votes for and against the top "
            "suspect has no committed source."
        )
        return
    match = _ROLE_CORRECT_CELL.match(cell.strip())
    counts = (
        None if match is None else [int(match.group(index)) for index in range(1, 5)]
    )
    chance = None if match is None else float(match.group(5))
    if counts is None or chance is None or not (counts[1] and counts[3] and chance):
        errors.append(
            f"{_SCORECARD_PAGE}: the {label} {_ROLE_CORRECT_ROW!r} cell reads "
            f"{cell!r}, not 'k/n = p% vs k/n = p% (chance p%)' over two non-empty "
            f"populations — the {_README} sentence on votes for and against the "
            "top suspect cannot be derived from it."
        )
        return
    hits, followers, deviator_hits, deviators = counts
    source = f"the {label} role-correct cell of {_SCORECARD_PAGE} ({cell.strip()})"
    claims = (
        _ProseClaim(
            _FOLLOWER_PROSE,
            (str(hits), str(followers), percent(hits, followers)),
        ),
        _ProseClaim(
            _DEVIATOR_PROSE,
            (
                str(deviators),
                repeat_word(deviator_hits),
                percent(deviator_hits, deviators),
            ),
        ),
        _ProseClaim(_CHANCE_PROSE, (number_word(round(100 / chance)),)),
        _ProseClaim(
            re.compile(_FOLLOWER_COUNT_PROSE.format(followers=followers)),
            (str(hits),),
            required=False,
        ),
    )
    check_prose_claims(list(prose_blocks(readme)), claims, source, errors)


def check_vent_prose(repo_root: Path, readme: str, errors: list[str]) -> None:
    """The README's vent sentence, held to the census's vent-proof cells.

    The sentence says how many meetings carried vent proof and that none of
    them ejected a crewmate, then how many did not, how many of their
    ejections removed an impostor and how many removed a crewmate. The clean
    record is refused outright once a meeting with vent proof ejected a
    crewmate: every crewmate ejection not in a meeting without vent proof is in
    one with it.
    """

    vent = shown_set_vent_cells(repo_root)
    if vent is None:
        return  # check_result_sources reports the unreadable page
    impostors, ejections = vent.unflagged
    innocent = ejections - impostors
    flagged_innocent = vent.band_crew[1] - innocent
    source = census_source()
    blocks = list(prose_blocks(readme))
    claims = [
        _ProseClaim(_VENT_FLAGGED_PROSE, (str(vent.meetings[0]),)),
        _ProseClaim(
            _VENT_UNFLAGGED_PROSE,
            (
                str(vent.meetings[1] - vent.meetings[0]),
                str(impostors),
                str(ejections),
                str(innocent),
            ),
        ),
        _ProseClaim(
            re.compile(_VENT_UNFLAGGED_SHARE_PROSE.format(ejections=ejections)),
            (str(impostors),),
            required=False,
        ),
        _ProseClaim(_VENT_INNOCENT_PROSE, (str(innocent),), required=False),
    ]
    if flagged_innocent < 0:
        errors.append(
            f"{source}: the vent-proof table's crew cells disagree: "
            f"{vent.band_crew[1]} crewmate(s) ejected in all, {innocent} of them "
            "in meetings without vent proof."
        )
    elif flagged_innocent == 0:
        claims += [_ProseClaim(pattern, ()) for pattern in _VENT_CLEAN_RECORD_PROSE]
    else:
        for number, text in blocks:
            for pattern in _VENT_CLEAN_RECORD_PROSE:
                errors.extend(
                    f"{_README}:{number}: the claim {match.group(0)!r} is refuted by "
                    f"{source}: meetings with vent proof ejected "
                    f"{flagged_innocent} crewmate(s)."
                    for match in pattern.finditer(text)
                )
    check_prose_claims(blocks, claims, source, errors)


def check_grounded_prose(repo_root: Path, readme: str, errors: list[str]) -> None:
    """The cited-vote count in prose, held to the cell its results row restates.

    The row ``Eject ballots citing what the voter saw or heard about the
    accused`` is the shown set's grounded EJECT cell on the scorecard page
    (:func:`check_process_rows`), and the sentence that retells it in prose is
    read off that same cell, so prose and row state one figure and move
    together on a re-record.
    """

    values = shown_set_values(repo_root)
    row = dict(_PROCESS_ROWS)[_GROUNDED_EJECT_CLAIM]
    cell = None if values is None else values.get(row)
    fraction = None if cell is None else _SCORECARD_FRACTION.match(cell.strip())
    if cell is None or fraction is None:
        return  # check_process_rows reports the unreadable page, row or cell
    check_prose_claims(
        list(prose_blocks(readme)),
        (_ProseClaim(_GROUNDED_EJECT_PROSE, (fraction.group(1), fraction.group(2))),),
        f"the {_SET_LABEL.format(name=_SHOWN_SET)} {row!r} cell of "
        f"{_SCORECARD_PAGE} ({cell.strip()}), which the results row "
        f"{_GROUNDED_EJECT_CLAIM!r} restates",
        errors,
    )


def demo_bundle_games(repo_root: Path) -> tuple[tuple[str, int], ...]:
    """Every ``(set, seed)`` the demo bundle bakes, ordered by set, then seed.

    The same rule as ``recorded_games`` in scripts/build_demo_bundle.py, which
    is restated rather than imported so this checker does not load the
    builder's results module: each set the live API lists under the samples
    root, and one game per seed among its recording files. The two must agree
    on every tree the builder accepts (the builder also refuses a respelled
    file name); tests/scripts/test_check_doc_facts.py holds them equal over the
    committed samples.
    """

    root = repo_root / _DEMO_SAMPLES_ROOT
    games: list[tuple[str, int]] = []
    for set_name in SetLoaderRegistry(root).available_sets():
        seeds = {
            seed
            for path in (root / set_name).glob(REPLAY_FILENAME_GLOB)
            if path.is_file()
            and (seed := replay_seed_from_filename(path.name)) is not None
        }
        games.extend((set_name, seed) for seed in sorted(seeds))
    return tuple(games)


def check_demo_game_count(repo_root: Path, readme: str, errors: list[str]) -> None:
    """The demo's game count, held to the games the bundle builder bakes."""

    games = len(demo_bundle_games(repo_root))
    if not games:
        return  # check_result_sources reports the empty corpus
    check_prose_claims(
        list(prose_blocks(readme)),
        (_ProseClaim(_DEMO_GAMES_PROSE, (str(games),)),),
        f"the {games} games under {_DEMO_SAMPLES_ROOT}/ the demo bundle bakes",
        errors,
    )


def check_import_contract_count(
    repo_root: Path, readme: str, errors: list[str]
) -> None:
    """The import-contract count, held to the linter config's contract sections."""

    config = read_document(repo_root, _IMPORT_LINTER, errors)
    if config is None:
        return
    contracts = len(_IMPORT_CONTRACT_SECTION.findall(config))
    if not contracts:
        errors.append(
            f"{_IMPORT_LINTER}: no '[importlinter:<name>]' contract section — the "
            f"{_README} contract count has nothing to be derived from."
        )
        return
    check_prose_claims(
        list(prose_blocks(readme)),
        (_ProseClaim(_IMPORT_CONTRACT_PROSE, (number_word(contracts),)),),
        f"the {contracts} contract sections of {_IMPORT_LINTER}",
        errors,
    )


def check_verified_recording_count(
    repo_root: Path, readme: str, errors: list[str]
) -> None:
    """The count of recordings the install block's verifier re-runs.

    A bare ``scripts/verify_samples.sh`` walks every sample set and every
    candidate set; the README's install block says how many recordings that is,
    and the count is the replay files the verifier's own reader accepts there.
    """

    recordings = sum(
        len(sample_paths(directory))
        for root, pattern in _VERIFIED_SET_GLOBS
        for directory in sorted((repo_root / root).glob(pattern))
        if directory.is_dir()
    )
    roots = " and ".join(f"{root}/" for root, _ in _VERIFIED_SET_GLOBS)
    if not recordings:
        errors.append(
            f"{roots}: no replay files found, so the {_README} count of recordings "
            "the verifier re-runs cannot be derived."
        )
        return
    check_prose_claims(
        list(enumerate(readme.splitlines(), start=1)),
        (_ProseClaim(_VERIFIED_RECORDINGS_PROSE, (str(recordings),)),),
        f"the {recordings} replay files under {roots}",
        errors,
    )


def prose_blocks(text: str, *, include_code: bool = True) -> Iterator[tuple[int, str]]:
    """Yield rendered paragraph/heading text, excluding tables and fenced blocks.

    List items are separate paragraphs. Links contribute their visible labels,
    never destination filenames or titles. Inline identifiers remain available
    to metric checks; action-claim checks can exclude quoted code examples.
    """

    in_table = False
    for token in MarkdownIt("commonmark").enable("table").parse(text):
        if token.type == "table_open":
            in_table = True
        elif token.type == "table_close":
            in_table = False
        elif token.type == "inline" and token.map is not None and not in_table:
            parts = inline_prose(token.children or (), include_code=include_code)
            yield token.map[0] + 1, " ".join(parts.split())


def inline_prose(tokens: Sequence[Token], *, include_code: bool) -> str:
    """Extract visible prose without promoting Markdown metadata to a claim."""

    parts: list[str] = []
    for token in tokens:
        if token.type == "text" or (include_code and token.type == "code_inline"):
            parts.append(token.content)
        elif token.type in {"softbreak", "hardbreak"}:
            parts.append(" ")
    return "".join(parts)


# ── 6. The ML results table ──────────────────────────────────────────────────


def check_ml_results_table(repo_root: Path, errors: list[str]) -> None:
    """The ML page's results table, recomputed from the committed JSONL.

    The page presents its table as reproducible from committed bytes by naming
    the command that reproduces it. This runs that command's own library over
    ``training/reports/results-finalist-eval.jsonl`` and holds every published
    cell to it: each arm's wins, its same-seed comparator's wins, and the paired
    exact-McNemar p. Rates are compared at the precision the cell prints, so the
    table may round as it likes but may not round to a different number.

    Coverage is checked in both directions, and no row is skipped. Every data
    row must resolve to an entrant the JSONL carries, and every entrant the
    JSONL carries must have a row — a losing arm quietly dropped, or a
    flattering one invented, would otherwise pass.
    """

    page = read_document(repo_root, _ML_PAGE, errors)
    if page is None:
        return
    rows = ml_results_rows(page)
    if rows is None:
        errors.append(
            f"{_ML_PAGE}: no results table with a "
            f"'{' | '.join(_ML_TABLE_HEADER)}' header row — the published arm "
            "cells have nothing to be derived from."
        )
        return
    try:
        stats = {
            row.entrant: row
            for row in compute_paired_stats(repo_root / _FINALIST_JSONL)
        }
        verdicts = referee_verdicts(repo_root / _FINALIST_JSONL)
    except (ValueError, OSError) as exc:
        errors.append(f"{_FINALIST_JSONL}: unreadable as a finalist eval ({exc}).")
        return

    seen: set[str] = set()
    comparator_rows = 0
    widest = max(stats.values(), key=lambda row: row.n)
    for cells in rows:
        label = cells[0]
        if len(cells) < _ML_TABLE_COLUMNS:
            errors.append(
                f"{_ML_PAGE}: the results row {label!r} holds {len(cells)} cells, "
                f"not the {_ML_TABLE_COLUMNS} the table publishes — a row missing "
                "a column states a figure nothing can be held to."
            )
            continue
        identity = _ML_ROW_IDENTITY.search(label)
        name = identity.group(1) if identity is not None else ""
        if name == _ML_COMPARATOR_LABEL:
            comparator_rows += 1
            compare_ml_cell(
                label, "impostor win", cells[1], widest.baseline_wins, widest.n, errors
            )
            compare_ml_referee(label, cells[4], verdicts, _ML_COMPARATOR_LABEL, errors)
            continue
        match = _ML_ARM_SHA.match(name)
        if match is None:
            errors.append(
                f"{_ML_PAGE}: the results row {label!r} names neither the "
                f"comparator nor an arm sha, so nothing in {_FINALIST_JSONL} "
                "answers for it — every published row states a measured arm."
            )
            continue
        entrant = _ML_ARM_ENTRANT.format(sha=match.group(1))
        arm = stats.get(entrant)
        if arm is None:
            errors.append(
                f"{_ML_PAGE}: the results row {label!r} names {entrant!r}, which "
                f"{_FINALIST_JSONL} does not carry "
                f"(entrants: {', '.join(sorted(stats))})."
            )
            continue
        seen.add(entrant)
        compare_ml_cell(label, "impostor win", cells[1], arm.arm_wins, arm.n, errors)
        compare_ml_cell(label, "comparator", cells[2], arm.baseline_wins, arm.n, errors)
        compare_ml_p(label, cells[3], arm.p_exact, errors)
        compare_ml_referee(label, cells[4], verdicts, entrant, errors)

    if comparator_rows != 1:
        errors.append(
            f"{_ML_PAGE}: the results table holds {comparator_rows} "
            f"{_ML_COMPARATOR_LABEL!r} rows — every arm is measured against "
            "exactly one comparator, so the table states exactly one."
        )
    for entrant in sorted(set(stats) - seen):
        errors.append(
            f"{_ML_PAGE}: {_FINALIST_JSONL} carries the arm {entrant!r}, which the "
            "results table does not state — every measured arm is published, "
            "including the ones that lost."
        )


def compare_ml_cell(
    label: str, column: str, cell: str, wins: int, total: int, errors: list[str]
) -> None:
    """One ``<k>/<n> = <rate>`` cell, held to the recomputed pair."""

    match = _ML_FRACTION.search(cell)
    if match is None:
        errors.append(
            f"{_ML_PAGE}: the {column} cell of results row {label!r} reads "
            f"{cell!r}, which holds no '<wins>/<games> = <rate>' figure to check "
            f"against the recomputed {wins}/{total}."
        )
        return
    stated = (int(match.group(1)), int(match.group(2)))
    if stated != (wins, total):
        errors.append(
            f"{_ML_PAGE}: the {column} cell of results row {label!r} reads "
            f"{stated[0]}/{stated[1]}, but {_FINALIST_JSONL} recomputes to "
            f"{wins}/{total}."
        )
        return
    rate, places = float(match.group(3)), len(match.group(4))
    if round(wins / total, places) != rate:
        errors.append(
            f"{_ML_PAGE}: the {column} cell of results row {label!r} states the "
            f"rate {match.group(3)}, but {wins}/{total} rounds to "
            f"{round(wins / total, places)} at that precision."
        )


def compare_ml_p(label: str, cell: str, p_exact: float, errors: list[str]) -> None:
    """One paired-p cell, held to the recomputed exact McNemar p."""

    match = _ML_P_VALUE.search(cell)
    if match is None:
        errors.append(
            f"{_ML_PAGE}: the p cell of results row {label!r} reads {cell!r}, "
            f"which holds no p-value to check against the recomputed {p_exact}."
        )
        return
    stated, places = float(match.group(1)), len(match.group(2))
    if round(p_exact, places) != stated:
        errors.append(
            f"{_ML_PAGE}: the p cell of results row {label!r} states "
            f"{match.group(1)}, but {_FINALIST_JSONL} recomputes the exact "
            f"McNemar p to {round(p_exact, places)} at that precision."
        )


def compare_ml_referee(
    label: str, cell: str, verdicts: dict[str, bool], entrant: str, errors: list[str]
) -> None:
    """One referee cell, held to ``watchability.referee_passed`` in the JSONL.

    This column is the adoption gate: it is what "none became the default"
    means. The cell must BE one of the two verdicts once markdown emphasis is
    stripped, never merely contain one — "not a FAIL" contains FAIL and states
    its opposite — and a cell that is neither fails as loudly as a wrong one.
    """

    passed = verdicts.get(entrant)
    if passed is None:
        errors.append(
            f"{_ML_PAGE}: the referee cell of results row {label!r} has no "
            f"{entrant!r} verdict in {_FINALIST_JSONL} to check against."
        )
        return
    stated = _EMPHASIS.sub("", cell).strip().upper()
    if stated not in (_ML_REFEREE_PASS, _ML_REFEREE_FAIL):
        errors.append(
            f"{_ML_PAGE}: the referee cell of results row {label!r} reads "
            f"{cell!r}, which is neither {_ML_REFEREE_PASS} nor "
            f"{_ML_REFEREE_FAIL} — this column carries a verdict, not prose."
        )
        return
    recorded = _ML_REFEREE_PASS if passed else _ML_REFEREE_FAIL
    if stated != recorded:
        errors.append(
            f"{_ML_PAGE}: the referee cell of results row {label!r} states "
            f"{stated}, but {_FINALIST_JSONL} records "
            f"watchability.referee_passed = {passed} ({recorded}) for {entrant!r}."
        )


def referee_verdicts(jsonl_path: Path) -> dict[str, bool]:
    """Each entrant's ``watchability.referee_passed`` from the committed JSONL.

    Read here rather than through :func:`compute_paired_stats`, which is about
    the paired win test and carries no gate outcome. ``ValueError`` on a row
    that answers neither question, because a silently skipped row would drop an
    arm's verdict out of the comparison it is supposed to be held to.
    """

    verdicts: dict[str, bool] = {}
    with jsonl_path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {number} is not JSON ({exc})") from exc
            entrant = row.get("entrant")
            watchability = row.get("watchability")
            passed = (
                watchability.get("referee_passed")
                if isinstance(watchability, dict)
                else None
            )
            if not isinstance(entrant, str) or not isinstance(passed, bool):
                raise ValueError(
                    f"line {number} carries no entrant + "
                    "watchability.referee_passed pair"
                )
            verdicts[entrant] = passed
    return verdicts


def ml_results_rows(page: str) -> list[list[str]] | None:
    """Every full row of the ML page's results table, in order.

    Full rows, not the two compared cells :func:`results_rows` keeps: this
    table's arm, comparator and p live in three different columns.
    """

    rows: list[list[str]] | None = None
    for line in page.splitlines():
        cells = table_cells(line)
        if cells is None or len(cells) < 4:
            if rows is not None:
                break
            continue
        if rows is None:
            if tuple(cells[:2]) == _ML_TABLE_HEADER:
                rows = []
            continue
        if all(_TABLE_RULE_CELL.match(cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def read_document(repo_root: Path, relative_path: str, errors: list[str]) -> str | None:
    """``repo_root/relative_path``'s text, or ``None`` with an error recorded."""

    try:
        return (repo_root / relative_path).read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{relative_path}: unreadable ({exc}).")
        return None


if __name__ == "__main__":
    raise SystemExit(main())
