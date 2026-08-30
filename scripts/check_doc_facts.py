#!/usr/bin/env python3
"""Check the front door's generated facts against their sources (Task 19.1).

The cheap half of the front-door truth sweep: seconds, no network, no LLM, no
engine playback. Every *checked fact* README.md and .env.example carry is
re-derived here from the committed bytes that own it, and any drift between the
prose and its source fails loud. ``scripts/verify_samples.sh`` proves the replay
bytes still reconstruct; this proves the prose still describes them — the drift
class the 19.1 sweep cleaned (a stale refresh date, a stale win rate, a stale
ladder tip, a graduated lever still documented as a live knob) is exactly what
regenerates silently otherwise.

Twenty checks. Each accumulates precise errors; all of them are reported
together, so one run names every drifted fact rather than the first.

1. **Sample provenance.** ``replays/samples/<set>/MANIFEST.md`` owns each sample
   set's outcomes and refresh date. The impostor win rate is recomputed from the
   ``winner`` column (rounded to a whole percent) and the newest ``refreshed_at``
   is taken across both sets. The claims are bound to the README's ONE
   sample-provenance paragraph (anchored on ``replays/samples/`` plus a
   ``regenerated YYYY-MM-DD`` clause): its stated date must equal the newest
   ``refreshed_at``, and it must carry each recomputed rate as the exact
   substring ``"<rate>% (<set>)"`` — a correct value elsewhere in the file
   cannot satisfy a drifted paragraph. EVERY ``regenerated YYYY-MM-DD`` clause
   in the paragraph and EVERY ``"<rate>% (<set>)"`` claim in the file — inside
   the paragraph or out — must match, so a stale duplicate cannot hide beside
   the correct value. The paragraph's count claims are re-derived from the
   same rows — the per-set tournament size (``"<rows>-game"``) and the total
   (``"<sum> sample replays"``), with every count-shaped claim in the
   paragraph held to the row totals — and the recording model plus the
   prompt-set family/version tokens the ``model`` / ``prompt_versions``
   columns record must be named in the paragraph as well. Both claim shapes
   are then scanned across every document allowed to repeat them — README.md,
   docs/history.md, docs/glossary.md, audits/README.md,
   docs/reading-guide.md and docs/ml-program.md — because a figure the front
   door states twice rots in the copy nobody re-reads. The results tables'
   ``At baseline 6`` column is the one span held to a different source: its
   cells state what the previous recording read, and the record's own
   win-split table owns them.
2. **Ladder tip.** The audit that adopted the current recording owns which
   baseline the substrate ladder stands at. Every front-door sentence naming
   the "ladder tip" — the whole sentence, however long — must name that
   baseline, and no other. The audits index is scanned with the front door: it
   is where a reader is sent to find the record.
3. **Lever registry vs .env.example.** ``orchestrator.replay`` owns the live
   substrate-lever registry. Every still-toggleable lever must be documented
   IN the belief-substrate section with a commented example line showing its
   bare-environment default — and ONLY that way: an active (uncommented)
   export anywhere in the template fails, because a copied .env would flip
   the substrate away from the committed record. Every graduated
   lever must be named by its registry key inside the section's GRADUATED
   LEVERS note — the contiguous comment block, not merely the section or the
   file — whose wording must keep saying "always ON" and never drift back to
   default-OFF phrasing; and no graduated lever may appear as an
   ``AILIBI_*=`` assignment, commented or not — its env gate was deleted at
   graduation, so an assignment line would hand out a knob this build does not
   read. The belief-substrate section may not advertise any ``AILIBI_*=``
   assignment whose key is absent from the registry either: a misspelled or
   never-registered knob is as much a no-op as a graduated one.
4. **Vote-correctness stamps vs the committed reports.**
   ``eval/vote_correctness.py`` documents what ``vote_correctness_rate`` reads
   on each recorded set. Every ``<set>/tournament-eval-report.json`` owns those
   numbers: the rate is re-derived here as
   ``evidence_backed_impostor_ejections / impostor_ejections`` — never a
   literal in this file, so a re-record only re-stamps the module — and the
   module must carry exactly one line naming that set, stamped with the
   recomputed ``"<numerator>/<denominator> = <rate>"`` — or ``"0/0 = n/a"``
   for a set that ejected no impostor, whose rate is undefined rather than
   zero. A report whose own ``vote_correctness_rate`` field disagrees with its
   counts fails too. The substrate those rates are attributed to is checked
   with them: the baseline comes from the ladder-tip audit above, the model,
   the prompt-set token and the substrate-flag stamp from the four
   ``MANIFEST.md`` files; the sets must agree on all three, and the module must
   name the baseline, the model and the prompt set (the flag stamp is thirteen
   keys wide — held to agreement, not copied into prose). Finally, while any
   recorded set reads below 1.0 the module may not call the rate
   structurally pinned: a zero-flag EJECT that cites a transcript turn or a
   private observation id is legal by design
   (``meetings.manager.guard_ballot_citation``), so the pin would be prose the
   committed bytes refute. Frontend copy is deliberately NOT scanned — the
   spectator surface has its own owner.
5. **Private dialect on the front door.** Nothing in README.md may require
   another document to parse. Every term in :data:`_DIALECT_TERMS` either does
   not appear in README.md at all, or its FIRST occurrence sits inside a link
   to its own ``docs/glossary.md`` entry — and that entry must exist, as a
   heading whose GitHub anchor the link names.
6. **The phase table and the history account for every phase.** Every
   ``tasks/phase-*.md`` must be linked from README.md or docs/history.md, so a
   new phase document cannot appear without reaching the front door.
7. **The audits index is complete.** ``audits/README.md`` must link every
   top-level ``audits/*.md`` exactly once, link nothing that no longer exists,
   and name every subdirectory of ``audits/`` as a unit.
8. **The results table agrees with the reading guide.** The numbers are stated
   once: every row of README.md's results table must appear in
   docs/reading-guide.md's numbers table with the SAME figure and the same
   ``At baseline 6`` cell, so a later edit cannot drift one from the other, and
   neither table may state one claim twice.
9. **The results figures are re-derived from their sources.** Agreement between
   two documents cannot catch a figure edited identically in both, so every row
   whose source is cheap to read is recomputed instead: the replay count from
   the verifier's own file population, the citation figure from the committed
   instrument's pinned assertions, the vent headline as arithmetic over the
   reading guide's cross-tab cells, and the proof-vs-inference conviction pair
   from BOTH recordings that measured it — the current one's pre-registered
   bar read for the published figure, the phase-19 close audit's own partition
   table for the ``At baseline 6`` cell. Each is checked against itself first
   (an accuracy cell fixes its own injustice count), and the published row must
   still say every innocent ejection sits in the no-proof cell, with the count
   the record read. The win rates are re-derived in check 1.
10. **The real-report example matches that report.** README.md hands a reader a
    populated eval report because the default fake provider produces an empty
    one; its ejection count and two rates come from that report's own
    ``vote_correctness`` block, never from prose.
11. **Volatile counts carry an as-of stamp.** A count that changes without any
    commit touching the prose (merged pull requests, commits, tests) must be
    stated with ``as of YYYY-MM-DD`` in its own sentence. The stamp's presence
    and shape are checked, never its value: no doc check may reach the network.
12. **The reading guide carries no ``file.ext:NN`` citations.** Line numbers rot
    on the next edit; the guide cites heading anchors and symbols instead.
13. **Every relative link resolves.** Across README.md, docs/history.md,
    docs/glossary.md, audits/README.md, docs/reading-guide.md, docs/lessons.md
    and audits/review-2026-08-19/README.md, each relative markdown target
    (fragment stripped) must name a path that exists.
14. **The ML page's results table is re-derived from the finalist-eval JSONL.**
    docs/ml-program.md publishes the program's headline table — per arm, its
    wins, the same-seed comparator's wins, the paired exact-McNemar p, and the
    referee verdict that decided adoption. Each is recomputed here from
    ``training/reports/results-finalist-eval.jsonl``: the win cells and the p
    through ``scripts/paired_stats.py``, the verdict from each row's own
    ``watchability.referee_passed``. No published row is skipped and no
    measured arm may be missing, so a moved cell, a flipped verdict, an
    invented row and a quietly dropped arm all fail.
15. **The reading guide's narrative matches its tables' pins.** Its §3
    cross-tab is what the README's vent headline is derived from, so the
    table's cells are bound to ``tests/eval/test_deduction_metrics.py``'s
    pinned assertions — and so are the sentences that narrate them, the
    eject-ballot count and the meeting total. Prose is where a recording's
    drift survives: a table gets re-quoted row by row and a paragraph does not.
16. **The reading guide's exhibits are games the spectator features.** Every
    ``<set> seed <n>`` the guide names must appear in ``FEATURED_GAMES``
    (frontend/src/components/ReplayPicker.tsx), the committed curated list; a
    guide naming a seed the strip dropped points a reader at a card that does
    not exist.
17. **The verdict figures survive being retold.** The front door recounts the
    record's two decided bars in prose as well as in its table, so every prose
    ``k of n = rate`` is held to its own arithmetic at the precision it prints,
    and every sentence naming a wrongful or innocent ejection must name the
    count the record read — or the count the recording before it read, which
    is what the before column is for.
18. **The published review index accounts for every finding, and its map
    resolves.** Every register id named on a ``**Section refs:**`` line of
    ``tasks/phase-20.md`` must appear somewhere in
    ``audits/review-2026-08-19/README.md`` — mapped to its fix, retracted, or
    listed as not acted on — so a dropped row fails instead of quietly shrinking
    the index. Every row of that index's finding -> task -> pull-request table
    must then credit a task that exists as a contract AND whose contract
    actually names that finding, cite this repository's pull-request URL with a
    label matching it, and appear exactly once. Whether the number was merged,
    and whether it belongs to the row's own task, is resolved in the unit tests,
    which need full git history and skip rather than pass without it.
19. **The front-door pages stay inside their word budgets.** Each of README.md,
    docs/reading-guide.md, docs/ml-program.md and docs/lessons.md carries one
    enforceable budget — a ceiling, plus a floor on the page written to a range.
    A ceiling may be lowered by any contract that trims a page; raising one
    takes an owner-ratified contract.
20. **The ML corpus's headline disclosures are re-derived from the reports.**
    ``replays/ml_corpus/README.md``'s capability-disclosures section states a
    meeting total and eight roll-call coverage pairs; each is recomputed from
    the recorded sets' own ``tournament-eval-report.json``, so the section
    cannot be relabelled onto a new substrate with the previous substrate's
    arithmetic still in it.

``--repo-root`` points the document and source reads at another tree (the unit
tests perturb a copy); it defaults to this checkout. The lever registry ALWAYS
comes from the live import, never from ``--repo-root``: the registry is code,
and a doc copy is checked against the levers this build actually ships.

Exit 0 when every checked fact matches, 1 with every failure printed.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
from collections.abc import Callable, Iterator, Sequence
from datetime import date
from pathlib import Path
from typing import Final

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

from orchestrator.replay import (  # noqa: E402
    SUBSTRATE_FLAG_KEYS,
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    substrate_flag_snapshot,
)

_README: Final = "README.md"
_ENV_EXAMPLE: Final = ".env.example"
_LADDER_TIP_AUDIT: Final = "audits/audit-phase-20-baseline-7.md"
_GLOSSARY: Final = "docs/glossary.md"
_HISTORY: Final = "docs/history.md"
_READING_GUIDE: Final = "docs/reading-guide.md"
_AUDITS_INDEX: Final = "audits/README.md"
_AUDITS_DIR: Final = "audits"
_TASKS_DIR: Final = "tasks"
_PHASE_GLOB: Final = "phase-*.md"
# The front door, as a set of documents: every relative link in any of them must
# resolve, and the phase/results/dialect checks read from this same set.
_LINKED_DOCUMENTS: Final[tuple[str, ...]] = (
    _README,
    _HISTORY,
    _GLOSSARY,
    _AUDITS_INDEX,
    _READING_GUIDE,
)
# The two pages published alongside the front door: the lessons essay and the
# curated index of the review it came out of. Their links are held to the same
# resolution rule; the index's acted-on map is held to the phase contract.
_LESSONS: Final = "docs/lessons.md"
_REVIEW_INDEX: Final = "audits/review-2026-08-19/README.md"
_PUBLISHED_DOCUMENTS: Final[tuple[str, ...]] = (_LESSONS, _REVIEW_INDEX)
_PHASE_20_CONTRACT: Final = "tasks/phase-20.md"
# The documents that between them must account for every phase contract.
_PHASE_DOCUMENTS: Final[tuple[str, ...]] = (_README, _HISTORY)
# The documents allowed to repeat a claim the committed bytes own — a win rate,
# the recording's date. A figure the front door states more than once is checked
# everywhere it is stated: the README is where such a claim is first written,
# never the only place it rots.
_ML_PAGE: Final = "docs/ml-program.md"
_CLAIM_DOCUMENTS: Final[tuple[str, ...]] = _LINKED_DOCUMENTS + (_ML_PAGE,)
# Every document allowed to state which baseline the ladder stands at. All of
# them are scanned, so a recording that moves the tip moves them together.
_LADDER_TIP_DOCUMENTS: Final[tuple[str, ...]] = (
    _README,
    _GLOSSARY,
    _HISTORY,
    _READING_GUIDE,
    _AUDITS_INDEX,
)
_SAMPLE_SETS: Final[tuple[str, ...]] = ("4p1i", "9p2i")
_MANIFEST_PATH: Final = "replays/samples/{name}/MANIFEST.md"

# The module whose prose owns what ``vote_correctness_rate`` reads, and the
# recorded sets that own the numbers. The set directory doubles as the stamp
# token, so "replays/samples/9p2i" and "replays/ml_corpus/9p2i" cannot be
# confused for each other.
_VOTE_CORRECTNESS_MODULE: Final = "eval/vote_correctness.py"
_RECORDED_SETS: Final[tuple[str, ...]] = (
    "replays/samples/4p1i",
    "replays/samples/9p2i",
    "replays/ml_corpus/4p1i",
    "replays/ml_corpus/9p2i",
)
_EVAL_REPORT_PATH: Final = "{set_dir}/tournament-eval-report.json"
_SET_MANIFEST_PATH: Final = "{set_dir}/MANIFEST.md"
_VOTE_CORRECTNESS_KEY: Final = '"vote_correctness":'
# The stamp a set with no impostor ejections carries: the rate is undefined
# there, and printing a number for it would be the drift this check exists
# to catch.
_NO_RATE: Final = "0/0 = n/a"
# The reports run to tens of megabytes; the blocks read out of them are a dozen
# scalar fields at most, so a runaway scan means the report format drifted
# rather than a bigger block.
_REPORT_BLOCK_MAX_LINES: Final = 64
# Prose that would reassert the pin the committed rates refute.
_STRUCTURAL_PIN_PHRASES: Final[tuple[str, ...]] = (
    "structurally pinned",
    "pinned to 1.0",
    "pins it to 1.0",
)

# The ``winner`` cell a manifest row carries when the impostors took the game.
_IMPOSTOR_WINNER: Final = "IMPOSTORS"
# ``refreshed_at`` is ISO ``YYYY-MM-DD``, so lexicographic max is chronological.
_ISO_DATE: Final = re.compile(r"\d{4}-\d{2}-\d{2}\Z")

_AUDIT_LADDER_TIP: Final = re.compile(
    r"ladder tip stands at \*{0,2}baseline (\d+)", re.IGNORECASE
)
_LADDER_TIP_PHRASE: Final = re.compile(r"ladder tip", re.IGNORECASE)
_BASELINE_MENTION: Final = re.compile(r"baseline[ -](\d+)", re.IGNORECASE)
# A sentence boundary: a period followed by whitespace or end of text, so
# version numbers and decimals ("18.12", "0.8646") do not end a sentence.
_SENTENCE_END: Final = re.compile(r"\.(?=\s|\Z)")

# The README's sample-provenance paragraph is anchored on this clause; the
# refresh-date claim is parsed from it rather than sought file-wide, so a
# stale paragraph cannot be alibied by the correct date elsewhere.
_REGENERATED_DATE: Final = re.compile(r"regenerated (\d{4}-\d{2}-\d{2})")
# Any "<rate>% (<set>)" claim, wherever it appears, must match the manifest.
_WIN_RATE_CLAIM: Final = re.compile(r"(\d+)% \((4p1i|9p2i)\)")
# The two other shapes the front door dates the current recording in. Both are
# held to the manifests' newest ``refreshed_at``; a NUMBERED claim naming an
# older recording is history and is left alone. The number is optional because
# the front door also dates the recording without numbering it ("the current
# reference recording, made <date>"), and an unnumbered claim is always about
# the current one.
_RECORDING_DATE_CLAIM: Final = re.compile(
    r"reference recording(?:\s+(\d+))?,?\s+(?:made\s+)?(\d{4}-\d{2}-\d{2})"
)
_RECORD_DATE_CLAIM: Final = re.compile(r"the (\d{4}-\d{2}-\d{2}) record\b")

# The .env.example section whose AILIBI_*= assignments must all resolve to a
# live registry key, delimited by the repo's dashed section banners.
_LEVER_SECTION_TITLE: Final = "# Belief-substrate levers"
_SECTION_RULE: Final = re.compile(r"^# -{20,}[ \t]*$", re.MULTILINE)
_ENV_ASSIGNMENT: Final = re.compile(r"^#?[ \t]*(AILIBI_[A-Z0-9_]+)=", re.MULTILINE)
# The graduated note is the contiguous comment block opening with this marker;
# the graduated/always-ON labels must live IN it, not merely near it.
_GRADUATED_NOTE_MARKER: Final = "# GRADUATED LEVERS"
_BLANK_LINE: Final = re.compile(r"\n[ \t]*\n")

# Every private-dialect term the front door may not use without defining, as
# (label, occurrence pattern, the glossary anchor its first use must link).
# Adding a term is one line here plus its glossary heading. The first six were
# counted in README.md by the 2026-08-19 portfolio review; the rest were
# defined nowhere in the tree at all.
_DIALECT_TERMS: Final[tuple[tuple[str, str, str], ...]] = (
    ("baseline", r"\bbaselines?\b", "baseline-n-the-reference-recording"),
    (
        "adopting record",
        r"\badopting record\b",
        "adopting-record-the-recording-that-adopts-a-change",
    ),
    ("ladder tip", r"\bladder tip\b", "the-ladder-tip-the-newest-reference-recording"),
    (
        "graduated",
        r"\bgraduat(?:e|es|ed|ing|ion)\b",
        "graduated-lever-a-setting-deleted-into-the-default",
    ),
    (
        "NO-FLIP",
        r"\bNO-FLIP\b|\bno mover flip\b",
        "no-flip-the-scripted-policy-stays-the-default",
    ),
    (
        "canary denominator",
        r"\bcanary denominator\b",
        "canary-denominator-the-held-out-monitoring-corpus",
    ),
    ("referee", r"\breferees?\b", "referee-the-selection-gate"),
    ("slate", r"\bslates?\b", "slate-the-set-of-arms-in-a-campaign"),
    ("arm", r"\barms?\b", "arm-one-measured-configuration"),
    ("mover", r"\bmovers?\b", "mover-the-tactical-policy"),
    ("champion", r"\bchampions?\b", "champion-the-best-arm-kept-opt-in"),
    (
        "conviction economy",
        r"\bconviction[- ]econom\w+",
        "conviction-economy-what-a-meeting-does-with-evidence",
    ),
    (
        "supply and conversion floors",
        r"\b(?:supply|conversion) floors?\b",
        "supply-and-conversion-floors",
    ),
    ("absence prior", r"\babsence prior\b", "absence-prior"),
    (
        "roll-call round",
        r"\broll-call round\b",
        "roll-call-round-the-whereabouts-round",
    ),
    (
        "endpoint-band whereabouts exemption",
        r"\bendpoint-band\b",
        "endpoint-band-whereabouts-exemption",
    ),
    (
        "flag-minting",
        r"\bflag-mint\w*",
        "flag-minting-stamping-a-contradiction-into-the-transcript",
    ),
    ("starved-economy shape", r"\bstarved-econom\w+", "starved-economy-shape"),
    ("screening-tier shortlist", r"\bscreening-tier\b", "screening-tier-shortlist"),
    ("two-axis owner ruling", r"\btwo-axis owner ruling\b", "two-axis-owner-ruling"),
    (
        "training-time-runner tier",
        r"\btraining-time-runner\b",
        "training-time-runner-tier",
    ),
    (
        "evidence-gated default flip",
        r"\bevidence-gated default flip\b",
        "evidence-gated-default-flip",
    ),
)
# A markdown link whose target is the glossary, with the anchor it names and the
# span of its link TEXT — the only place a dialect term counts as defined.
_GLOSSARY_LINK: Final = re.compile(rf"\[([^\]]*)\]\({re.escape(_GLOSSARY)}#([\w-]+)\)")
# Any markdown (or image) link, with its target. Targets are checked for
# resolution; absolute and in-page ones are skipped by :func:`relative_targets`.
_MARKDOWN_LINK: Final = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_ABSOLUTE_TARGET: Final = re.compile(r"\A(?:[a-z][a-z0-9+.-]*:|//)", re.IGNORECASE)
# GitHub's heading-anchor rule, reduced to what this tree's headings need:
# lowercase, drop everything but word characters, spaces and hyphens, then
# spaces become hyphens.
_ANCHOR_STRIP: Final = re.compile(r"[^\w\- ]")
_HEADING: Final = re.compile(r"^#{1,6}[ \t]+(.+?)[ \t]*$", re.MULTILINE)

# Counts that change without any commit touching the prose. Each must be stated
# with an as-of stamp in its own sentence; the VALUE is never checked, because
# no doc check may reach the network to learn the true one.
_VOLATILE_COUNTS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    (
        "merged pull requests",
        re.compile(r"\d[\d,]*\+?\s+merged\s+(?:pull requests|PRs)\b", re.IGNORECASE),
    ),
    ("commits", re.compile(r"\d[\d,]*\+?\s+commits\b", re.IGNORECASE)),
    ("tests", re.compile(r"\d[\d,]*\+?\s+tests\b", re.IGNORECASE)),
)
_AS_OF: Final = re.compile(r"as of (\d{4}-\d{2}-\d{2})")

# The review index's acted-on map, located by its header cells. A row is one
# review finding, the claim in a line, the phase task that closed it and the
# merged pull request that carries it.
_REVIEW_MAP_HEADER: Final[tuple[str, ...]] = (
    "Finding",
    "What it claimed",
    "Closed by",
    "Pull request",
)
_REVIEW_FINDING: Final = re.compile(r"\A`([GC]-\d{1,3})`\Z")
_REVIEW_TASK: Final = re.compile(r"\A(\d+\.\d+)\Z")
# The repository whose pull requests this index may cite. Pinned rather than
# captured: a row pointing at someone else's fork would resolve against a number
# this history happens to carry and read as verified.
_REVIEW_REPOSITORY: Final = "dkdan10/AiLibi"
_REVIEW_PULL_REQUEST: Final = re.compile(
    rf"\A\[#(\d+)\]\(https://github\.com/{re.escape(_REVIEW_REPOSITORY)}/pull/(\d+)\)\Z"
)
_PHASE_TASK_HEADING: Final = re.compile(r"^### Task (\d+\.\d+) — ", re.MULTILINE)
# A review register id, and the contract line that declares which ones a task
# acts on. The index must account for every id the phase's contracts declare.
_FINDING_ID: Final = re.compile(r"\b([GC]-\d{1,3})\b")
_SECTION_REFS_PREFIX: Final = "**Section refs:**"

# A `path.ext:NN` citation — the shape that rots on the next edit of the file it
# names. The extensions are the ones this tree's prose actually cites.
_LINE_CITATION: Final = re.compile(
    r"\b[\w./-]*\w\.(?:py|md|ts|tsx|js|json|jsonl|j2|sh|yml|yaml|toml|cfg|txt):\d+"
)

# The results tables, located by their header row rather than by heading text,
# so a section rename does not silently disable the agreement check.
_RESULTS_TABLE_HEADER: Final[tuple[str, str]] = ("What", "Figure")
# The column carrying each row's value at the recording this one replaced. Its
# cells are HISTORY: the claim-shaped scans hold them to what the record itself
# says the old value was, never to today's committed bytes.
_BEFORE_COLUMN_HEADER: Final = "At baseline 6"
# A markdown link reduced to its text, so a column header may carry its glossary
# link and still be matched by name.
_LINK_TEXT: Final = re.compile(r"\[([^\]]*)\]\([^)\s]+\)")
# Below this the README table is a stub, and row-by-row agreement would pass
# vacuously — a check that cannot fail is not a gate.
_MIN_RESULT_ROWS: Final = 4
_TABLE_RULE_CELL: Final = re.compile(r"\A:?-{2,}:?\Z")

# The results rows whose figures are RE-DERIVED rather than compared between
# the two tables: agreement catches a one-sided edit, not the same wrong figure
# written into both. Each claim string is the row's first cell.
_SAMPLE_REPLAY_DIR: Final = "replays/samples/{name}"
_REPLAY_COUNT_CLAIM: Final = (
    "Committed sample replays that reconstruct byte-identically"
)
_CITATION_INSTRUMENT: Final = "tests/eval/test_vj_instruments.py"
_CITATION_CLAIM: Final = (
    "Eject ballots carrying a valid citation, a turn or an observation id (9p2i)"
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
_VENT_CLAIM: Final = "Correct 9p ejections riding an ejectee-specific vent sighting"
_VENT_TABLE_HEADER: Final = "Meeting contains a vent flag"
# The reading guide's §3 cross-tab, and the committed instrument whose pinned
# assertions own its cells. The guide's table is where the README's vent
# headline is derived FROM, so leaving it unbound would leave the headline
# resting on prose; these pins are what it rests on instead.
_DEDUCTION_INSTRUMENT: Final = "tests/eval/test_deduction_metrics.py"
# ``assert cross_tab.<field> == <n>`` — the samples-9p2i partitions, which are
# the only ones the instrument reads through a bare ``cross_tab`` name. A
# trailing comment is allowed: these pins carry their previous value in one.
_CROSSTAB_PIN: Final = re.compile(
    r"^\s*assert cross_tab\.(\w+) == (\d+)\s*(?:#.*)?$", re.MULTILINE
)
# What the guide's cross-tab states, as (pinned field, how the guide states it).
_CROSSTAB_MEETING_TOTAL: Final = "meetings_total"
_CROSSTAB_ROW_FIELDS: Final[tuple[tuple[str, str, str], ...]] = (
    ("yes", "flagged_ejections_impostor", "flagged_ejections_innocent"),
    ("no", "unflagged_ejections_impostor", "unflagged_ejections_innocent"),
)
_CROSSTAB_ROW_MEETINGS: Final[dict[str, str]] = {
    "yes": "flagged_meetings",
    "no": "unflagged_meetings",
}
# The guide's PROSE figures — the sentences that narrate the tables. They rot
# where the tables do not: a record moves the table and leaves the paragraph.
_GUIDE_BALLOT_PROSE: Final = re.compile(r"all (\d+) eject\s+ballots")
_GUIDE_MEETING_PROSE: Final = re.compile(r"all (\d+)\s+committed 9p2i meetings")
# The unflagged half read as a ratio in the paragraph under the cross-tab: the
# most-quoted sentence on the page, and the one a reader takes away.
_GUIDE_NO_PROOF_PROSE: Final = re.compile(r"coin flip[^.]*?(\d+) of (\d+)")
_VENT_ROW_MEETINGS: Final = re.compile(r"\|\s*(yes|no)\s*\((\d+) meetings\)")
# The guide's own row for the teammate firewall, whose denominator moved with
# the recording. The zero is the firewall holding; the total is a pinned count
# of the impostor ballots it held over.
_PARTNER_BALLOT_CLAIM: Final = "Impostor ballots cast against a partner (9p2i)"
_PARTNER_BALLOT_FIGURE: Final = "0 of {total}"
_PARTNER_BALLOT_PIN: Final = re.compile(
    r"samples\.model_partner_naming_ballots,\s*samples\.impostor_ballots\)\s*"
    r"==\s*\(\d+,\s*(\d+)\)"
)

# The curated featured list the spectator opens, as committed data. Any game the
# guide names as an exhibit must be on it, or the guide sends a reader looking
# for a card that is not there.
_PICKER: Final = "frontend/src/components/ReplayPicker.tsx"
_FEATURED_BLOCK: Final = re.compile(
    r"FEATURED_GAMES: readonly FeaturedGame\[\] = \[(.*?)\n\];", re.DOTALL
)
_FEATURED_ENTRY: Final = re.compile(r'set: "([^"]+)",\s*\n\s*seed: (\d+),')
# Emphasis-independent on purpose: the rule binds every game the guide names,
# and an unbolded mention names one just as loudly.
_GUIDE_EXHIBIT: Final = re.compile(r"\b(4p1i|9p2i) seed (\d+)")
# Below this the guide names too few exhibits for the binding to mean anything,
# and a paragraph that quietly lost its seeds would pass vacuously.
_MIN_EXHIBIT_SEEDS: Final = 2
# The conviction partition. The BEFORE column is the phase-19 close audit's own
# per-set table, whose four data columns sum to the pooled pair; the AFTER
# column is the current record's pre-registered read, which measured the same
# cells on the new bytes and publishes them pooled.
_PROOF_PARTITION_AUDIT: Final = "audits/audit-phase-19-close.md"
# Each bar of the record's read is its own section, and the pooled row of the
# table inside it is the cell the front door quotes. Located by the heading, so
# the four ``| set | before | after |`` tables cannot be confused for each other.
_RECORD_BAR_HEADING: Final = re.compile(r"^#{2,4} +Bar (\d+)\b", re.MULTILINE)
_BEFORE_AFTER_HEADER: Final[tuple[str, str]] = ("set", "before")
_RECORD_POOLED_LABEL: Final = "pooled"
_ACCURACY_BAR: Final = 1
_INNOCENT_BAR: Final = 2
# The direct-proof half is stated in the accuracy bar's prose rather than in its
# table, which reports the non-direct cell per set.
_DIRECT_PROOF_POOLED: Final = re.compile(
    r"direct-proof cell[^|]*?\*\*(\d+)/(\d+) = [\d.]+\*\* pooled"
)
# The record's win-split table: the baseline-6 rate each set carried, which is
# what a before-column win-rate claim is held to.
_WIN_SPLIT_HEADER: Final[tuple[str, str]] = ("set", "baseline-6 impostor rate")
_WIN_SPLIT_ROW: Final = "samples/{name}"
_PROOF_CLAIM: Final = (
    "Ejection accuracy with engine-certified proof of the ejectee's role, "
    "against without"
)
_PROOF_TABLE_HEADER: Final = "cell"
# The four rows read out of that table, by their own labels (emphasis stripped,
# lowercased), so a reordered table derives the same figures and a renamed row
# fails loud instead of deriving a silent half-sum.
_PROOF_ROW: Final = "direct-proof accuracy"
_NON_PROOF_ROW: Final = "non-direct accuracy"
_INNOCENT_ROW: Final = "innocent ejections (all in the non-direct cell)"
_PROOF_INNOCENT_ROW: Final = "proof-present innocent ejections"
_PROOF_ROW_LABELS: Final[tuple[str, ...]] = (
    _PROOF_ROW,
    _NON_PROOF_ROW,
    _INNOCENT_ROW,
    _PROOF_INNOCENT_ROW,
)
# One reading of the conviction partition: the direct-proof accuracy, the
# non-direct accuracy, the innocent ejections and the innocent ejections that
# landed in the direct-proof cell.
_Partition = tuple[tuple[int, int], tuple[int, int], int, int]
_RATIO_CELL: Final = re.compile(r"(\d+)\s*/\s*(\d+)")
_COUNT_CELL: Final = re.compile(r"(\d+)")
_EMPHASIS: Final = re.compile(r"[*`]")
# The injustice claim the proof row carries beside its two accuracies. Both
# halves are required: the count AND where those ejections landed, because the
# count alone is satisfied by a row that puts them in the wrong cell.
_INJUSTICE_CLAIM: Final = (
    "{count} of {count} innocent ejections sit in the no-proof cell"
)
# A results row whose history cell this checker RE-DERIVES from the audit that
# owns it, rather than only comparing the two tables' copies.
_WIN_RATE_ROW_CLAIM: Final = "Impostor win rate, committed samples"
_DERIVED_BEFORE_CLAIMS: Final[frozenset[str]] = frozenset(
    {_WIN_RATE_ROW_CLAIM, _PROOF_CLAIM}
)
# ...and the ones it only compares, because their baseline-6 values live in
# audit prose no parser here reads. Naming them is the point: a row that moves
# without landing in one of these two sets fails, so the unchecked set cannot
# grow by accident.
_QUOTED_BEFORE_CLAIMS: Final[frozenset[str]] = frozenset(
    {
        _CITATION_CLAIM,
        _VENT_CLAIM,
        _PARTNER_BALLOT_CLAIM,
    }
)
# A whole integer, so a count is matched as a number and not as a run of digits
# inside a longer one.
_WHOLE_NUMBER: Final = re.compile(r"\b\d+\b")
# Every front-door sentence about wrongful convictions names the count the
# record read, the way every "ladder tip" sentence names the baseline.
_INJUSTICE_SENTENCE: Final = re.compile(
    r"\b(?:wrongful|innocent) ejections?\b", re.IGNORECASE
)
# ``k of n = rate`` / ``k / n = rate`` — checked against its own arithmetic at
# the precision it prints, wherever the front door writes one.
_RATE_CLAIM: Final = re.compile(r"(\d+)\s*(?:of|/)\s*(\d+)\s*=\s*(0\.\d+|1\.0+)")

# The ML page's results table and the committed measurement it is derived from.
# The table is located by its own header cells, so renaming the section above it
# does not disable the derivation.
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
# The cross-tab's rows are read by their own label, flagged first, so a
# reordered table cannot silently swap the two populations.
_VENT_ROW_LABELS: Final[tuple[str, str]] = ("yes", "no")

# The committed report the README hands a reader instead of the empty one a
# fake-provider run produces, and the phrase that anchors its paragraph.
_POPULATED_REPORT: Final = "replays/samples/9p2i/tournament-eval-report.json"
_EXAMPLE_ANCHOR: Final = "fake provider's report is empty on purpose"

# One word budget per front-door page, as ``(document, floor, ceiling)`` —
# ``None`` where a page has no floor. Measured with ``wc -w`` semantics:
# whitespace-separated runs over the raw markdown, so the number in the gate is
# the number a reader gets from the shell.
#
# A ceiling may be LOWERED by any contract that trims the page — that direction
# is the point of having one. RAISING one takes an owner-ratified contract,
# because a budget that moves up to meet its page is not a budget. These four
# were priced just above their counts at the ratifying contract, so the ruling
# grants headroom rather than demanding a trim.
_FRONT_DOOR_BUDGETS: Final[tuple[tuple[str, int | None, int], ...]] = (
    (_README, None, 3_550),
    (_READING_GUIDE, None, 1_350),
    (_ML_PAGE, None, 2_150),
    (_LESSONS, 800, 1_500),
)

# The ML corpus's capability-disclosures section and the four recorded sets its
# headline cells are re-derived from. Each cell is located by the label the
# prose writes immediately before it, so a cell is bound to its own claim rather
# than to a position in a sentence that may be rewritten.
_CORPUS_README: Final = "replays/ml_corpus/README.md"
_DISCLOSURE_SETS: Final[tuple[tuple[str, str], ...]] = (
    ("S9", "replays/samples/9p2i"),
    ("C9", "replays/ml_corpus/9p2i"),
    ("S4", "replays/samples/4p1i"),
    ("C4", "replays/ml_corpus/4p1i"),
)
_COVERAGE_KEY: Final = '"public_response_coverage":'
# Each role's ``(numerator, denominator)`` field pair in that block.
_COVERAGE_ROLES: Final[tuple[tuple[str, str, str], ...]] = (
    ("crew", "crew_turns_with_whereabouts", "crew_turns"),
    ("impostor", "impostor_turns_with_whereabouts", "impostor_turns"),
)
_DISCLOSURE_MEETINGS_LABEL: Final = "meetings crew-triggered"
# The report's per-game trigger evidence, streamed rather than decoded: one
# ``roles`` map per game, then one ``triggered_by`` per meeting row. Both keys
# are unique to their nesting level, so the scan reads the trigger side without
# pulling in the embedded transcripts that make these files tens of megabytes.
_GAME_ID_LINE: Final = re.compile(r'^\s*"game_id":\s*"')
_ROLES_LINE: Final = re.compile(r'^\s*"roles":\s*\{\s*$')
_TRIGGERED_BY_LINE: Final = re.compile(r'^\s*"triggered_by":\s*"([^"]+)"\s*,?\s*$')
_CREW_ROLE: Final = "CREWMATE"
# The section's substrate label. It is held to the ladder-tip audit because a
# one-word relabel — the substrate name advanced, every number left as recorded
# on the previous one — is exactly how this section went wrong.
_DISCLOSURE_SUBSTRATE: Final = re.compile(r"baseline-(\d+)\s+substrate")
# A labelled bold ``**<k>/<n>``-shaped cell. The label's words are joined by
# ``\s+`` so a cell still matches when markdown re-wraps the sentence across
# lines; the counts are written with thousands separators, stripped before the
# comparison.
_DISCLOSURE_CELL: Final = r"\s+\*\*([\d,]+)/([\d,]+)"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check README.md and .env.example against the committed bytes that "
            "own their facts (Task 19.1)."
        )
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=_REPO_ROOT,
        help=(
            "Tree whose documents and sources are read (default: this "
            "checkout). The substrate-lever registry always comes from the "
            "live import, never from this tree."
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
        f"Doc facts verified: {_README} and {_ENV_EXAMPLE} agree with "
        f"{len(_SAMPLE_SETS)} sample manifests, {_LADDER_TIP_AUDIT}, and the "
        f"{len(SUBSTRATE_FLAG_KEYS)}-lever substrate registry; "
        f"{_VOTE_CORRECTNESS_MODULE} agrees with {len(_RECORDED_SETS)} "
        "recorded eval reports."
    )
    print(
        f"Front door verified: {len(_DIALECT_TERMS)} private-dialect terms are "
        f"absent from {_README} or linked to {_GLOSSARY}; the phase table and "
        f"{_HISTORY} account for every {_TASKS_DIR}/{_PHASE_GLOB}; "
        f"{_AUDITS_INDEX} indexes every top-level {_AUDITS_DIR}/*.md once; the "
        f"{_README} results figures are re-derived from their sources and equal "
        f"{_READING_GUIDE}'s, before column included; the real-report example "
        f"matches {_POPULATED_REPORT}; every volatile count is as-of stamped; "
        f"{_READING_GUIDE} carries no file:line citation, narrates the cells "
        f"{_DEDUCTION_INSTRUMENT} pins, and names only games {_PICKER} "
        f"features; the claim-shaped facts hold across "
        f"{len(_CLAIM_DOCUMENTS)} documents; every relative link in "
        f"{len(_LINKED_DOCUMENTS) + len(_PUBLISHED_DOCUMENTS)} front-door and "
        f"published documents resolves; and {_REVIEW_INDEX} accounts for every "
        f"finding {_PHASE_20_CONTRACT} names, each mapped row crediting a "
        "contract that names it back."
    )
    print(
        f"{_ML_PAGE} verified: every published arm's wins, comparator wins, "
        f"paired exact-McNemar p and referee verdict recompute from "
        f"{_FINALIST_JSONL}."
    )
    print(
        f"Budgets verified: {len(_FRONT_DOOR_BUDGETS)} front-door pages sit "
        f"inside their word budgets; {_CORPUS_README}'s headline disclosure "
        f"cells recompute from {len(_DISCLOSURE_SETS)} recorded eval reports."
    )
    return 0


def check_facts(repo_root: Path) -> list[str]:
    """Every checked-fact failure under ``repo_root``, in check order."""

    errors: list[str] = []
    readme = read_document(repo_root, _README, errors)
    if readme is not None:
        check_sample_provenance(repo_root, readme, errors)
        check_dialect_terms(repo_root, readme, errors)
        check_results_agreement(repo_root, readme, errors)
        check_result_sources(repo_root, readme, errors)
        check_populated_report_example(repo_root, readme, errors)
        check_volatile_stamps(readme, errors)
    check_ladder_tip(repo_root, errors)
    check_lever_registry(repo_root, errors)
    check_vote_correctness_sentinel(repo_root, errors)
    check_phase_coverage(repo_root, errors)
    check_audits_index(repo_root, errors)
    check_guide_line_citations(repo_root, errors)
    check_guide_narrative(repo_root, errors)
    check_verdict_figures(repo_root, errors)
    check_featured_exhibits(repo_root, errors)
    check_relative_links(repo_root, errors)
    check_review_map(repo_root, errors)
    check_ml_results_table(repo_root, errors)
    check_front_door_budgets(repo_root, errors)
    check_corpus_disclosures(repo_root, errors)
    return errors


def check_front_door_budgets(repo_root: Path, errors: list[str]) -> None:
    """Every front-door page against its committed word budget.

    A ceiling may be lowered by any contract that trims a page, and raised only
    by an owner-ratified one — the asymmetry is what makes it a budget. The
    floor matters as much as the ceiling on a page written to a range: a range
    budget with only a ceiling is half a gate, and an essay that shrinks out of
    its band has stopped being the thing the band described.

    ``wc -w`` semantics: whitespace-separated runs over the raw markdown.
    """

    for document, floor, ceiling in _FRONT_DOOR_BUDGETS:
        text = read_document(repo_root, document, errors)
        if text is None:
            continue
        words = len(text.split())
        if words > ceiling:
            errors.append(
                f"{document}: {words} words, over its {ceiling}-word ceiling by "
                f"{words - ceiling} — trim the page, or raise the ceiling in an "
                "owner-ratified contract."
            )
        if floor is not None and words < floor:
            errors.append(
                f"{document}: {words} words, under its {floor}-word floor by "
                f"{floor - words} — the page is written to a "
                f"{floor}–{ceiling}-word band."
            )


def check_corpus_disclosures(repo_root: Path, errors: list[str]) -> None:
    """The ML corpus's headline disclosure cells, re-derived from the reports.

    ``replays/ml_corpus/README.md``'s capability-disclosures section may not
    state a headline cell the recorded bytes do not give: the crew-triggered
    meeting cell and the eight roll-call coverage pairs. Every side of every
    cell is re-derived from the recorded sets' ``tournament-eval-report.json``,
    never from a literal here, so a re-record only re-states the section. The
    meeting cell's NUMERATOR is counted from the meeting rows' own
    ``triggered_by`` against each game's role map — the claim is that no meeting
    was impostor-triggered, and a numerator synthesised from the denominator
    would make that claim unfalsifiable.

    The section's substrate LABEL is bound to the ladder-tip audit as well.
    Re-deriving the numbers is not enough on its own: this section went wrong by
    being relabelled onto a new substrate with the previous substrate's
    arithmetic left in place, and a check that reads only the numbers would pass
    that relabel again the moment the reports were replaced with it.

    Each cell is found by the label the prose writes before it, EVERY occurrence
    of that label is held to the same value — a stale duplicate beside the
    correct one is drift too — and a disagreement is reported with the README
    line it sits on.
    """

    readme = read_document(repo_root, _CORPUS_README, errors)
    if readme is None:
        return

    check_disclosure_substrate(repo_root, readme, errors)

    crew_triggered = 0
    meetings = 0
    cells: list[tuple[str, int, int]] = []
    for tag, set_dir in _DISCLOSURE_SETS:
        report = _EVAL_REPORT_PATH.format(set_dir=set_dir)
        facts = read_disclosure_facts(repo_root, report, errors)
        if facts is None:
            return
        crew_triggered += facts[0]
        meetings += facts[1]
        block = facts[2]
        try:
            for role, answered_field, turns_field in _COVERAGE_ROLES:
                cells.append(
                    (
                        f"{role} {tag}",
                        int(str(block[answered_field])),
                        int(str(block[turns_field])),
                    )
                )
        except (KeyError, ValueError) as exc:
            errors.append(
                f"{report}: {_COVERAGE_KEY} is missing an integer field "
                f"({exc}) — the disclosure cells have no source."
            )
            return

    cells.insert(0, (_DISCLOSURE_MEETINGS_LABEL, crew_triggered, meetings))
    for label, numerator, denominator in cells:
        pattern = r"\s+".join(re.escape(word) for word in label.split())
        found = list(re.finditer(pattern + _DISCLOSURE_CELL, readme))
        if not found:
            errors.append(
                f"{_CORPUS_README}: no '{label}' cell — the capability "
                "disclosures no longer state it in the labelled "
                "'**<numerator>/<denominator>' shape this check reads, which is "
                "the one way the check stops being able to fail."
            )
            continue
        for cell in found:
            stated = (
                int(cell.group(1).replace(",", "")),
                int(cell.group(2).replace(",", "")),
            )
            if stated != (numerator, denominator):
                errors.append(
                    f"{_CORPUS_README}:{line_number(readme, cell.start())}: the "
                    f"'{label}' cell reads {stated[0]}/{stated[1]}, but the "
                    f"recorded reports give {numerator}/{denominator}."
                )


def check_disclosure_substrate(repo_root: Path, readme: str, errors: list[str]) -> None:
    """The disclosures' substrate label, against the tip AND the recorded sets.

    Two bindings, because either alone leaves the drift reachable. The LABEL is
    held to the ladder-tip audit, so the section cannot be advanced to a
    substrate the tree has not adopted. The recorded SETS are then held to the
    live lever registry, so the label cannot be advanced to a tip the disclosed
    bytes predate: a substrate advances here by graduating a lever, and a set
    recorded before that graduation does not carry the graduated key in its
    stamp. Checking only the label would pass a relabel onto a newly adopted
    tip while the disclosed numbers still came from the older recording.

    A section that names NO substrate fails too: the numbers below it are only
    meaningful against a stated one.
    """

    tip = recorded_ladder_tip(repo_root, errors)
    if tip is None:
        return
    labels = list(_DISCLOSURE_SUBSTRATE.finditer(readme))
    if not labels:
        errors.append(
            f"{_CORPUS_README}: names no 'baseline-N substrate' at all — the "
            "disclosed numbers have no substrate to be true of, and the label "
            f"must name baseline {tip} ({_LADDER_TIP_AUDIT})."
        )
    for label in labels:
        if label.group(1) == tip:
            continue
        errors.append(
            f"{_CORPUS_README}:{line_number(readme, label.start())}: labelled "
            f"baseline-{label.group(1)} substrate, but {_LADDER_TIP_AUDIT} "
            f"records the ladder tip at baseline {tip} — relabelling this "
            "section without re-deriving it is the drift these checks exist to "
            "end."
        )

    retired = set(SUBSTRATE_FLAG_KEYS) - set(TOGGLEABLE_SUBSTRATE_FLAG_KEYS)
    for _, set_dir in _DISCLOSURE_SETS:
        relative_path = _SET_MANIFEST_PATH.format(set_dir=set_dir)
        text = read_document(repo_root, relative_path, errors)
        if text is None:
            continue
        rows = list(parse_manifest(text).values())
        if not rows:
            errors.append(
                f"{relative_path}: parsed zero table rows — the manifest format "
                "drifted, so this set proves nothing about the substrate the "
                "disclosures are attributed to."
            )
            continue
        for row in rows:
            stamped = {flag.strip() for flag in row.flags.split(",") if flag.strip()}
            missing = sorted(retired - stamped)
            if missing:
                errors.append(
                    f"{relative_path}: a recorded row stamps graduated "
                    f"lever(s) {missing} OFF, so this set predates the "
                    f"substrate baseline {tip} names — the disclosures derived "
                    "from it cannot be labelled with the current tip."
                )
                break


def read_disclosure_facts(
    repo_root: Path, relative_path: str, errors: list[str]
) -> tuple[int, int, dict[str, object]] | None:
    """``(crew-triggered, total, coverage)`` from one eval report, in ONE pass.

    Streamed, not decoded: the reports reach tens of megabytes because they
    embed every transcript, and this needs only each game's ``roles`` map, each
    meeting row's ``triggered_by``, and the ``public_response_coverage`` block.
    All three are collected on a single walk of the file — the trigger side has
    to reach the end of the ``report`` block anyway, so picking the coverage
    block up on the way costs nothing, where a second opener would re-scan the
    prefix on every one of this module's runs.

    A trigger is resolved against ITS OWN game's map and no other. The map is
    dropped at every ``game_id`` — a game boundary — so a game that omitted its
    roles cannot borrow the previous game's, where the same ``p-1`` is a
    different player with a possibly different role. A trigger with no map, a
    trigger naming nobody in it, and a report with no meeting rows at all are
    each format drift reported as such, never silently resolved to "not crew"
    (AGENTS.md, no silent fallbacks): every one of them would understate the
    numerator and could pass a false cell.
    """

    path = repo_root / relative_path
    roles: dict[str, str] | None = None
    coverage: dict[str, object] | None = None
    crew = 0
    meetings = 0
    unresolved: list[str] = []
    block: list[str] | None = None
    reading_coverage = False
    depth = 0
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if block is not None:
                    depth += line.count("{") - line.count("}")
                    block.append(line)
                    if depth > 0 and len(block) <= _REPORT_BLOCK_MAX_LINES:
                        continue
                    decoded, _ = json.JSONDecoder().raw_decode("".join(block))
                    if reading_coverage:
                        coverage = decoded if isinstance(decoded, dict) else None
                    else:
                        roles = {str(k): str(v) for k, v in decoded.items()}
                    block = None
                    continue
                if coverage is None and line.strip().startswith(_COVERAGE_KEY):
                    block, reading_coverage, depth = ["{"], True, 1
                    continue
                if _GAME_ID_LINE.match(line):
                    roles = None
                    continue
                if _ROLES_LINE.match(line):
                    block, reading_coverage, depth = ["{"], False, 1
                    continue
                trigger = _TRIGGERED_BY_LINE.match(line)
                if trigger is not None:
                    meetings += 1
                    actor = trigger.group(1)
                    role = None if roles is None else roles.get(actor)
                    if role is None:
                        unresolved.append(actor)
                    elif role == _CREW_ROLE:
                        crew += 1
    except (OSError, ValueError) as exc:
        errors.append(
            f"{relative_path}: the per-game trigger rows do not read "
            f"({exc}) — the crew-triggered meeting cell has no source."
        )
        return None

    # Every defect is reported before returning: one drifted report should name
    # everything the disclosures lost with it, not the first thing noticed.
    if coverage is None:
        errors.append(
            f"{relative_path}: no {_COVERAGE_KEY} key — the eval-report format "
            "drifted, so the prose derived from that block has no source."
        )
    if meetings == 0:
        errors.append(
            f"{relative_path}: no meeting rows — 0 meeting rows means the "
            "eval-report format drifted, so the crew-triggered meeting cell "
            "would be derived from nothing."
        )
    elif unresolved:
        errors.append(
            f"{relative_path}: {len(unresolved)} meeting trigger(s) "
            f"{sorted(set(unresolved))} resolve to no role in their own game's "
            "map — a game with no roles, or a trigger naming nobody in it. "
            "Counting them as non-crew would understate the numerator."
        )
    if coverage is None or meetings == 0 or unresolved:
        return None
    return crew, meetings, coverage


def check_sample_provenance(repo_root: Path, readme: str, errors: list[str]) -> None:
    """README's sample refresh date + win rates, re-derived from the MANIFESTs.

    The rate is ``rows won by IMPOSTORS / rows``, rounded to a whole percent —
    the same arithmetic the README paragraph states in prose. A manifest that
    parses to zero rows is a hard failure rather than a vacuous pass: silent
    format drift would otherwise let any claim through.

    The claims are checked IN the sample-provenance paragraph, not file-wide:
    a correct value surviving somewhere else (a historical note, another
    section's date) must not alibi a drifted paragraph. Win-rate claims found
    outside the paragraph are held to the same manifest arithmetic.
    """

    dates: list[str] = []
    rates: dict[str, tuple[int, int]] = {}
    models: set[str] = set()
    prompt_families: set[str] = set()
    prompt_versions: set[str] = set()
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
        rates[name] = (impostor_wins, len(rows))

        models.update(row.model.strip() for row in rows)
        for row in rows:
            # Entries are ``template.family.version``; the no-meetings
            # sentinel and empty cells have no dotted shape and are skipped.
            for entry in row.prompt_versions.split(","):
                segments = entry.strip().split(".")
                if len(segments) >= 3:
                    prompt_families.add(segments[-2])
                    prompt_versions.add(segments[-1])

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
        dates.extend(set_dates)

    # Before the paragraph check, not after: the front door's other documents
    # repeat these facts on their own account, and a README that lost its
    # provenance paragraph must not take their gate down with it.
    check_repeated_claims(repo_root, rates, max(dates) if dates else None, errors)

    paragraph = provenance_paragraph(readme)
    if paragraph is None:
        errors.append(
            f"{_README}: expected exactly one sample-provenance paragraph "
            "(anchored on 'replays/samples/' plus a 'regenerated YYYY-MM-DD' "
            "clause) — without it the provenance claims have no home to check."
        )
        return

    if dates:
        newest = max(dates)
        # EVERY regenerated-date clause in the paragraph must match — a stale
        # duplicate beside the correct clause is drift, same as the win rates.
        for stated in _REGENERATED_DATE.findall(paragraph):
            if stated != newest:
                errors.append(
                    f"{_README}: the sample-provenance paragraph claims "
                    f"'regenerated {stated}', but the newest "
                    f"refresh date {newest!r} is what "
                    f"{', '.join(_MANIFEST_PATH.format(name=name) for name in _SAMPLE_SETS)}"
                    " record."
                )

    for name, (impostor_wins, total) in rates.items():
        claim = f"{round(100 * impostor_wins / total)}% ({name})"
        if claim not in paragraph:
            errors.append(
                f"{_README}: the sample-provenance paragraph is missing the "
                f"recorded impostor win rate {claim!r} — "
                f"{_MANIFEST_PATH.format(name=name)} records "
                f"{impostor_wins}/{total} games won by the impostors."
            )

    size_claims: dict[str, list[str]] = {}
    for name, (_, total) in rates.items():
        size_claims.setdefault(f"{total}-game", []).append(name)
    for games_claim, names in sorted(size_claims.items()):
        if games_claim not in paragraph:
            errors.append(
                f"{_README}: the sample-provenance paragraph is missing the "
                f"tournament size {games_claim!r} — "
                f"{', '.join(_MANIFEST_PATH.format(name=name) for name in names)} "
                f"hold that many replay rows per set."
            )
    set_sizes = {total for _, total in rates.values()}
    for size_match in re.finditer(r"(\d+)-game", paragraph):
        if int(size_match.group(1)) not in set_sizes:
            errors.append(
                f"{_README}: the sample-provenance paragraph claims a "
                f"'{size_match.group(0)}' tournament, but no manifest holds "
                f"that many rows (per-set row counts: "
                f"{', '.join(str(size) for size in sorted(set_sizes))})."
            )
    if len(rates) == len(_SAMPLE_SETS):
        grand_total = sum(total for _, total in rates.values())
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
    for kind, tokens in (
        ("prompt-set family", prompt_families),
        ("prompt-set version", prompt_versions),
    ):
        for token in sorted(tokens):
            if token not in paragraph:
                errors.append(
                    f"{_README}: the sample-provenance paragraph does not "
                    f"name the {kind} {token!r} — the manifest "
                    "`prompt_versions` column records it."
                )


def check_repeated_claims(
    repo_root: Path,
    rates: dict[str, tuple[int, int]],
    newest_date: str | None,
    errors: list[str],
) -> None:
    """The win rates and the recording's date, everywhere the front door says them.

    The README is where a claim like "24% (9p2i)" is first written; it is not
    the only place it rots. The reading guide repeats both figures in its own
    numbers table and the ML page dates the recording its comparator now sits
    against, so all of them are held to the manifests here.

    The results tables' before column is the one exception, and it is checked
    rather than skipped: those cells state what the value was at the recording
    this one replaced, so they are held to the record's own win-split table.
    A live figure written into a history cell, or a history figure written into
    a live one, fails either way.
    """

    historical_rates = record_win_rates(repo_root, rates, errors)
    # Which recording is current is the ladder tip's own question, and
    # :func:`check_ladder_tip` already reports it when the audit cannot answer.
    tip = recorded_ladder_tip(repo_root, [])
    for document in _CLAIM_DOCUMENTS:
        text = read_document(repo_root, document, errors)
        if text is None:
            continue
        for number, unit, historical in claim_units(text):
            expected_rates = historical_rates if historical else rates
            for match in _WIN_RATE_CLAIM.finditer(unit):
                name = match.group(2)
                if name not in expected_rates:
                    continue
                wins, total = expected_rates[name]
                expected = round(100 * wins / total)
                if int(match.group(1)) == expected:
                    continue
                source = (
                    f"{_LADDER_TIP_AUDIT}'s win-split table"
                    if historical
                    else _MANIFEST_PATH.format(name=name)
                )
                where = " in the before column" if historical else ""
                errors.append(
                    f"{document}:{number}: win-rate claim {match.group(0)!r}"
                    f"{where} disagrees with {source} "
                    f"({wins}/{total} = {expected}%)."
                )
            if historical or newest_date is None:
                continue
            for stated, claim in current_record_dates(unit, tip):
                if stated == newest_date:
                    continue
                errors.append(
                    f"{document}:{number}: {claim!r} dates the current "
                    f"reference recording {stated!r}, but "
                    f"{', '.join(_MANIFEST_PATH.format(name=name) for name in _SAMPLE_SETS)}"
                    f" record {newest_date!r}."
                )


def current_record_dates(text: str, tip: str | None) -> Iterator[tuple[str, str]]:
    """Each ``(date, claim)`` in ``text`` that dates the CURRENT recording.

    A claim NUMBERING an older recording is history and is not yielded:
    "reference recording 6, 2026-07-20" is a true sentence about a recording
    this tree no longer ships, and holding it to today's manifests would force
    the front door to forget what it replaced. Everything else — an unnumbered
    "reference recording, made <date>", "the <date> record", "regenerated
    <date>" — is about the current one.
    """

    for match in _RECORDING_DATE_CLAIM.finditer(text):
        numbered = match.group(1)
        if numbered is None or numbered == tip:
            yield match.group(2), " ".join(match.group(0).split())
    for pattern in (_RECORD_DATE_CLAIM, _REGENERATED_DATE):
        for match in pattern.finditer(text):
            yield match.group(1), match.group(0)


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


def record_win_rates(
    repo_root: Path, rates: dict[str, tuple[int, int]], errors: list[str]
) -> dict[str, tuple[int, int]]:
    """Each sample set's PREVIOUS impostor win rate, from the record's own table.

    The record publishes both columns of the split it measured, so the front
    door's before column has a committed source rather than a memory. The after
    column is checked against the manifests while we are here: a record that
    disagreed with the bytes it recorded would make every before/after pair on
    the front door meaningless.
    """

    audit = read_document(repo_root, _LADDER_TIP_AUDIT, errors)
    if audit is None:
        return {}
    rows = labelled_table_rows(audit, _WIN_SPLIT_HEADER)
    if rows is None:
        errors.append(
            f"{_LADDER_TIP_AUDIT}: no win-split table with a "
            f"'{' | '.join(_WIN_SPLIT_HEADER)}' header row — the front door's "
            "before-column win rates have no committed source."
        )
        return {}
    previous: dict[str, tuple[int, int]] = {}
    for name in _SAMPLE_SETS:
        cells = rows.get(_WIN_SPLIT_ROW.format(name=name))
        if cells is None or len(cells) < 2:
            errors.append(
                f"{_LADDER_TIP_AUDIT}: the win-split table has no "
                f"{_WIN_SPLIT_ROW.format(name=name)!r} row, so the before-column "
                f"win rate for {name} cannot be re-derived."
            )
            continue
        before, after = _RATIO_CELL.search(cells[0]), _RATIO_CELL.search(cells[1])
        if before is None or after is None:
            errors.append(
                f"{_LADDER_TIP_AUDIT}: the win-split row for {name} holds no "
                "before/after pair of the shape '<wins>/<games>'."
            )
            continue
        previous[name] = (int(before.group(1)), int(before.group(2)))
        recorded = (int(after.group(1)), int(after.group(2)))
        if name in rates and recorded != rates[name]:
            errors.append(
                f"{_LADDER_TIP_AUDIT}: the win-split table records "
                f"{recorded[0]}/{recorded[1]} for {name}, but "
                f"{_MANIFEST_PATH.format(name=name)} holds "
                f"{rates[name][0]}/{rates[name][1]}."
            )
    return previous


def labelled_table_rows(
    markdown: str, header: tuple[str, ...]
) -> dict[str, list[str]] | None:
    """The table under ``header``, keyed on each row's own first cell.

    Emphasis and backticks are stripped from the label so a bolded or
    code-spanned row name reads the same as a bare one. ``None`` when no table
    carries that header row — format drift the caller reports.
    """

    rows: dict[str, list[str]] | None = None
    for line in markdown.splitlines():
        cells = table_cells(line)
        if cells is None or len(cells) < len(header):
            if rows is not None:
                break
            continue
        if rows is None:
            if (
                tuple(_EMPHASIS.sub("", cell).strip() for cell in cells[: len(header)])
                == header
            ):
                rows = {}
            continue
        if all(_TABLE_RULE_CELL.match(cell) for cell in cells):
            continue
        rows[_EMPHASIS.sub("", cells[0]).strip()] = cells[1:]
    return rows


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


def check_ladder_tip(repo_root: Path, errors: list[str]) -> None:
    """No front-door "ladder tip" sentence may name a baseline but the tip.

    The tip itself is parsed from the audit :data:`_LADDER_TIP_AUDIT` names —
    the record that adopted the current recording, which is where the ladder's
    standing is written down; whitespace is collapsed first because the audit
    wraps its prose mid-sentence.

    Every document that may state the tip is scanned, not only README.md: the
    glossary defines the term and the history narrates it, so a recording that
    moves the tip has to move all of them together. Headings are skipped —
    "the ladder tip" as a glossary heading is a label, not a claim about which
    baseline is current.
    """

    tip = recorded_ladder_tip(repo_root, errors)
    if tip is None:
        return
    for document in _LADDER_TIP_DOCUMENTS:
        text = read_document(repo_root, document, errors)
        if text is None:
            continue
        for phrase in _LADDER_TIP_PHRASE.finditer(text):
            if text[text.rfind("\n", 0, phrase.start()) + 1 :].startswith("#"):
                continue
            sentence = sentence_around(text, phrase.start(), phrase.end())
            mentions = _BASELINE_MENTION.findall(sentence)
            if not mentions:
                errors.append(
                    f"{document}:{line_number(text, phrase.start())}: a 'ladder "
                    "tip' sentence names no baseline at all — every ladder-tip "
                    f"claim must name baseline {tip} ({_LADDER_TIP_AUDIT}) — "
                    f"“{sentence.strip()}”."
                )
                continue
            for number in mentions:
                if number == tip:
                    continue
                errors.append(
                    f"{document}:{line_number(text, phrase.start())}: a 'ladder "
                    f"tip' sentence names baseline {number}, but "
                    f"{_LADDER_TIP_AUDIT} records the ladder tip at baseline "
                    f"{tip} — “{sentence.strip()}”."
                )


def recorded_ladder_tip(repo_root: Path, errors: list[str]) -> str | None:
    """The baseline the substrate ladder stands at, per the close audit.

    The one committed source for "which baseline is this". ``None`` with an
    error recorded when the audit names none or names several — both are drift
    the callers report rather than guess through. Whitespace is collapsed
    first because the audit wraps its prose mid-sentence.
    """

    audit = read_document(repo_root, _LADDER_TIP_AUDIT, errors)
    if audit is None:
        return None
    recorded = _AUDIT_LADDER_TIP.findall(re.sub(r"\s+", " ", audit))
    if not recorded:
        errors.append(
            f"{_LADDER_TIP_AUDIT}: no 'the ladder tip stands at baseline N' "
            "sentence — the ladder tip has no committed source to check against."
        )
        return None
    if len(set(recorded)) > 1:
        named = ", ".join(f"baseline {tip}" for tip in sorted(set(recorded)))
        errors.append(
            f"{_LADDER_TIP_AUDIT}: disagreeing ladder-tip records ({named}); "
            "the audit must record one tip."
        )
        return None
    return str(recorded[0])


def check_lever_registry(repo_root: Path, errors: list[str]) -> None:
    """.env.example against the live substrate-lever registry.

    Toggleable levers must be documented with a commented example line showing
    the value this build resolves under a bare environment. Graduated levers
    must be named by their registry key — the recording stamp and the MANIFEST
    ``flags`` cell still carry them — but must never appear as an ``AILIBI_*=``
    assignment: their env gate is gone, so such a line documents nothing.
    """

    text = read_document(repo_root, _ENV_EXAMPLE, errors)
    if text is None:
        return
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
        active = re.compile(rf"^[ \t]*{re.escape(variable)}=", re.MULTILINE)
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


def check_vote_correctness_sentinel(repo_root: Path, errors: list[str]) -> None:
    """``eval/vote_correctness.py``'s stamps, re-derived from the eval reports.

    Each recorded set owns one stamp line in the module: the line naming that
    set must carry ``"<evidence_backed>/<impostor_ejections> = <rate>"`` with
    the rate re-derived here, so a re-record re-stamps the module instead of
    rotting it. A report whose own ``vote_correctness_rate`` disagrees with its
    two counts fails as well — the drift would otherwise hide behind a stamp
    that still matched the counts.

    The provenance the stamps are attributed to is checked with them
    (:func:`check_vote_correctness_provenance`): a rate is only meaningful
    beside the substrate that produced it, so the model and prompt-set tokens
    come from the four ``MANIFEST.md`` files, never from this file.

    While any set reads below 1.0 the module may not call the rate structurally
    pinned. That claim was true of a substrate where the only eject path ran
    through the contradiction detector; since the citation gate it is not, and
    the committed reports are what say so.
    """

    module = read_document(repo_root, _VOTE_CORRECTNESS_MODULE, errors)
    if module is None:
        return

    check_vote_correctness_provenance(repo_root, module, errors)
    stamp_lines = module.splitlines()
    sets_below_one: list[str] = []
    for set_dir in _RECORDED_SETS:
        relative_path = _EVAL_REPORT_PATH.format(set_dir=set_dir)
        block = read_vote_correctness_block(repo_root, relative_path, errors)
        if block is None:
            continue
        numerator = block.get("evidence_backed_impostor_ejections")
        denominator = block.get("impostor_ejections")
        recorded = block.get("vote_correctness_rate")
        if (
            not isinstance(numerator, int)
            or not isinstance(denominator, int)
            or isinstance(numerator, bool)
            or isinstance(denominator, bool)
            or numerator < 0
            or denominator < 0
            or numerator > denominator
        ):
            errors.append(
                f"{relative_path}: the vote_correctness block does not carry a "
                "well-formed count pair — evidence-backed must be a "
                "non-negative integer no larger than impostor_ejections "
                f"(read {numerator!r} of {denominator!r}), the same invariant "
                "VoteCorrectnessReport enforces, so the rate cannot be "
                "re-derived."
            )
            continue

        if denominator == 0:
            # A set that ejected no impostor has an UNDEFINED rate, not a zero
            # one — the analyzer records ``None``. Stamp it as such so the
            # module cannot quietly print a number for it.
            if numerator != 0 or recorded is not None:
                errors.append(
                    f"{relative_path}: no impostor ejections, so the rate is "
                    f"undefined — but the block records {numerator} "
                    f"evidence-backed and a rate of {recorded!r}."
                )
            check_stamp(stamp_lines, set_dir, relative_path, _NO_RATE, errors)
            continue

        rate = numerator / denominator
        if not isinstance(recorded, (int, float)) or isinstance(recorded, bool):
            errors.append(
                f"{relative_path}: vote_correctness_rate is {recorded!r}, not a "
                f"number — its own counts read {numerator}/{denominator}."
            )
        elif abs(float(recorded) - rate) > 1e-9:
            errors.append(
                f"{relative_path}: the recorded vote_correctness_rate "
                f"{recorded!r} disagrees with its own counts "
                f"({numerator}/{denominator} = {rate:.4f})."
            )
        if rate < 1.0:
            sets_below_one.append(f"{set_dir} ({numerator}/{denominator})")

        claim = f"{numerator}/{denominator} = {rate:.4f}"
        check_stamp(stamp_lines, set_dir, relative_path, claim, errors)

    if not sets_below_one:
        return
    for phrase in _STRUCTURAL_PIN_PHRASES:
        if phrase in module:
            errors.append(
                f"{_VOTE_CORRECTNESS_MODULE}: still claims {phrase!r}, but "
                f"{', '.join(sets_below_one)} records a rate below 1.0 — a "
                "zero-flag eject that cites a turn or an observation id is "
                "legal (meetings.manager.guard_ballot_citation), so the pin is "
                "prose the committed bytes refute."
            )


def check_stamp(
    stamp_lines: Sequence[str],
    set_dir: str,
    relative_path: str,
    claim: str,
    errors: list[str],
) -> None:
    """One recorded set's stamp line in the module, bound to its own report.

    Exactly one module line may name the set: a second would let a stale
    duplicate hide beside the correct value, the drift class this whole file
    exists to catch.
    """

    stamped = [line for line in stamp_lines if set_dir in line]
    if len(stamped) != 1:
        errors.append(
            f"{_VOTE_CORRECTNESS_MODULE}: expected exactly one line naming "
            f"{set_dir!r} (its vote-correctness stamp), found {len(stamped)} — "
            "the checked claim has no unambiguous home."
        )
    elif claim not in stamped[0]:
        errors.append(
            f"{_VOTE_CORRECTNESS_MODULE}: the {set_dir} stamp reads "
            f"{stamped[0].strip()!r}, but {relative_path} records {claim}."
        )


def provenance_lead_in(module: str) -> str | None:
    """The paragraph directly above the module's per-set rate stamps.

    The stamps are a contiguous run of lines naming the recorded sets; the
    lead-in is the paragraph immediately preceding them, and it is the only
    place the substrate claims count. Binding the claims to it is what stops a
    correct model or baseline token elsewhere in the file from alibiing a wrong
    attribution. ``None`` when no stamp line is found (format drift the caller
    reports).
    """

    lines = module.splitlines()
    first_stamp = next(
        (
            index
            for index, line in enumerate(lines)
            if any(set_dir in line for set_dir in _RECORDED_SETS)
        ),
        None,
    )
    if first_stamp is None:
        return None
    end = first_stamp
    while end > 0 and not lines[end - 1].strip():
        end -= 1
    start = end
    while start > 0 and lines[start - 1].strip():
        start -= 1
    return "\n".join(lines[start:end])


def check_vote_correctness_provenance(
    repo_root: Path, module: str, errors: list[str]
) -> None:
    """The substrate the vote-correctness stamps are attributed to.

    A rate means nothing without the recording it came from. Three columns of
    every recorded set's ``MANIFEST.md`` own that recording — ``model``,
    ``prompt_versions`` and the substrate ``flags`` — and EVERY set must supply
    all three and agree on them: a set that establishes nothing (a manifest
    with no dotted prompt entry, say) must not be carried by its siblings, and
    one provenance line cannot describe two substrates. The baseline comes from
    the ladder-tip audit.

    The baseline, the model and the prompt-set token (``<family>.<version>``)
    are short enough to be named in the module and are required there — inside
    the provenance lead-in that introduces the stamps
    (:func:`provenance_lead_in`), never merely somewhere in the file, so a
    correct token in an unrelated comment cannot alibi a wrong lead-in. The
    flags stamp is tens of keys wide, so it is held to agreement only: naming
    it in prose would be a second copy to rot.
    """

    models: set[str] = set()
    prompt_tokens: set[str] = set()
    flag_stamps: set[str] = set()
    for set_dir in _RECORDED_SETS:
        relative_path = _SET_MANIFEST_PATH.format(set_dir=set_dir)
        text = read_document(repo_root, relative_path, errors)
        if text is None:
            continue
        rows = list(parse_manifest(text).values())
        if not rows:
            errors.append(
                f"{relative_path}: parsed zero table rows — the manifest format "
                "drifted, so the recorded substrate cannot be re-derived."
            )
            continue
        set_models = {row.model.strip() for row in rows if row.model.strip()}
        set_prompt_tokens: set[str] = set()
        set_flag_stamps: set[str] = set()
        for row in rows:
            # Entries are ``template.family.version``; the no-meetings sentinel
            # and empty cells have no dotted shape and are skipped.
            for entry in row.prompt_versions.split(","):
                segments = entry.strip().split(".")
                if len(segments) >= 3:
                    set_prompt_tokens.add(f"{segments[-2]}.{segments[-1]}")
            # Order-insensitive: the stamp is the SET of flags a row was
            # recorded under, not the order the writer happened to render.
            set_flag_stamps.add(
                ", ".join(
                    sorted(
                        flag.strip() for flag in row.flags.split(",") if flag.strip()
                    )
                )
            )
        for label, supplied in (
            ("recording model", set_models),
            ("prompt set", set_prompt_tokens),
            ("substrate flags", set_flag_stamps),
        ):
            if not supplied:
                errors.append(
                    f"{relative_path}: records no {label} on any row, so this "
                    "set establishes nothing about the substrate the "
                    f"{_VOTE_CORRECTNESS_MODULE} stamps are attributed to — a "
                    "sibling manifest must not vouch for it."
                )
        models |= set_models
        prompt_tokens |= set_prompt_tokens
        flag_stamps |= set_flag_stamps

    lead_in = provenance_lead_in(module)
    if lead_in is None:
        errors.append(
            f"{_VOTE_CORRECTNESS_MODULE}: the vote-correctness stamps carry no "
            "provenance lead-in (the paragraph directly above them) — the "
            "substrate claims have no home to check."
        )
        lead_in = ""

    tip = recorded_ladder_tip(repo_root, errors)
    if tip is not None and f"baseline-{tip}" not in lead_in:
        errors.append(
            f"{_VOTE_CORRECTNESS_MODULE}: the stamps' provenance lead-in does "
            f"not name 'baseline-{tip}', the baseline {_LADDER_TIP_AUDIT} "
            "records the substrate ladder standing at — a rate attributed to "
            "the wrong baseline is a wrong claim even when its arithmetic "
            "checks out."
        )

    for label, tokens, name_in_lead_in in (
        ("recording model", models, True),
        ("prompt set", prompt_tokens, True),
        ("substrate flags", flag_stamps, False),
    ):
        if len(tokens) > 1:
            errors.append(
                f"{_VOTE_CORRECTNESS_MODULE}: the recorded sets disagree on the "
                f"{label} ({' | '.join(sorted(tokens))}) — one provenance line "
                f"cannot describe them; {', '.join(_RECORDED_SETS)} should share "
                "one substrate."
            )
            continue
        if not name_in_lead_in:
            continue
        for token in tokens:
            if token not in lead_in:
                errors.append(
                    f"{_VOTE_CORRECTNESS_MODULE}: the stamps' provenance lead-in "
                    f"does not name the {label} {token!r} they were recorded "
                    f"on — {_SET_MANIFEST_PATH.format(set_dir=_RECORDED_SETS[0])} "
                    "and its siblings record it on every row."
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
        with path.open(encoding="utf-8") as handle:
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


def check_dialect_terms(repo_root: Path, readme: str, errors: list[str]) -> None:
    """No private-dialect term may sit undefined on the front door.

    The rule the portfolio review asked for: nothing in README.md may require
    another document to parse. A term either does not appear at all, or its
    FIRST occurrence is inside a link to its own glossary entry — first,
    because that is where a reader meets it, and a definition offered after the
    fact is a definition the reader has already needed.

    Both halves bite. An occurrence outside a glossary link fails, and the
    glossary entry is required for EVERY term on the list whether or not the
    README currently uses it: the list is the set of words the front door may
    not use undefined, so deleting an entry would quietly re-open the door to
    the term it defines.
    """

    glossary = read_document(repo_root, _GLOSSARY, errors)
    anchors = heading_anchors(glossary) if glossary is not None else set()
    links = {
        (match.start(1), match.end(1)): match.group(2)
        for match in _GLOSSARY_LINK.finditer(readme)
    }

    for label, pattern, anchor in _DIALECT_TERMS:
        if glossary is not None and anchor not in anchors:
            errors.append(
                f"{_GLOSSARY}: no entry anchored '#{anchor}' for the "
                f"private-dialect term {label!r} — every term the front door "
                "may not use undefined needs its definition to exist, whether "
                f"or not {_README} happens to use it today."
            )
        first = re.search(pattern, readme, re.IGNORECASE)
        if first is None:
            continue
        covering = [
            named
            for (start, end), named in links.items()
            if start <= first.start() and first.end() <= end
        ]
        if anchor in covering:
            continue
        errors.append(
            f"{_README}:{line_number(readme, first.start())}: the "
            f"private-dialect term {label!r} first appears as "
            f"{first.group(0)!r} outside a glossary link — its first "
            f"occurrence must read [{label} …]({_GLOSSARY}#{anchor}), or the "
            "term must not appear on the front door at all."
        )


def check_phase_coverage(repo_root: Path, errors: list[str]) -> None:
    """Every phase contract is reachable from the front door.

    The README's phase table and ``docs/history.md`` split the work — the table
    links a close audit where one exists, the history always links the contract
    — so neither alone accounts for the phases. Together they must: a phase
    document nobody linked is a phase the front door silently forgot.
    """

    phase_files = sorted((repo_root / _TASKS_DIR).glob(_PHASE_GLOB))
    if not phase_files:
        errors.append(
            f"{_TASKS_DIR}/{_PHASE_GLOB}: no phase contracts found — the phase "
            "coverage check has nothing to check, which is drift rather than a "
            "pass."
        )
        return

    linked: set[Path] = set()
    for document in _PHASE_DOCUMENTS:
        text = read_document(repo_root, document, errors)
        if text is None:
            continue
        linked.update(
            resolved for _, resolved in relative_targets(repo_root, document, text)
        )

    for path in phase_files:
        if path in linked:
            continue
        errors.append(
            f"{_TASKS_DIR}/{path.name}: linked from neither "
            f"{' nor '.join(_PHASE_DOCUMENTS)} — every phase contract must be "
            "reachable from the front door, its close audit or its own file."
        )


def check_audits_index(repo_root: Path, errors: list[str]) -> None:
    """``audits/README.md`` indexes the audit corpus exactly, both ways.

    An un-indexed audit is an orphan (the state this index was written to end);
    an indexed audit that no longer exists is a dead link a reader follows. A
    second row for the same file is drift too — two lines describing one record
    are two lines to keep in step.

    Directories under ``audits/`` are named as units rather than expanded: the
    review directory alone holds dozens of files, and enumerating them here
    would be a second index to rot.
    """

    index = read_document(repo_root, _AUDITS_INDEX, errors)
    if index is None:
        return
    audits_dir = repo_root / _AUDITS_DIR
    on_disk = {
        path.name
        for path in audits_dir.glob("*.md")
        if path.name != Path(_AUDITS_INDEX).name
    }
    if not on_disk:
        errors.append(
            f"{_AUDITS_DIR}/*.md: no audits found beside {_AUDITS_INDEX} — the "
            "index check has nothing to check."
        )
        return

    indexed: dict[str, int] = {}
    for target, _ in relative_targets(repo_root, _AUDITS_INDEX, index):
        if "/" in target or not target.endswith(".md"):
            continue
        indexed[target] = indexed.get(target, 0) + 1

    for name in sorted(on_disk - set(indexed)):
        errors.append(
            f"{_AUDITS_INDEX}: {name} is not indexed — every top-level audit "
            "needs a row, or the corpus goes back to being unnavigable."
        )
    for name in sorted(set(indexed) - on_disk):
        errors.append(
            f"{_AUDITS_INDEX}: indexes {name}, which no longer exists in "
            f"{_AUDITS_DIR}/."
        )
    for name, count in sorted(indexed.items()):
        if count > 1:
            errors.append(
                f"{_AUDITS_INDEX}: {name} is indexed {count} times — one record, "
                "one row, or the two descriptions drift apart."
            )

    for directory in sorted(
        path.name for path in audits_dir.iterdir() if path.is_dir()
    ):
        if f"{directory}/" not in index:
            errors.append(
                f"{_AUDITS_INDEX}: does not name the {directory}/ directory — "
                "sub-directories are indexed as units, but they are indexed."
            )


def check_results_agreement(repo_root: Path, readme: str, errors: list[str]) -> None:
    """The results are stated once: two tables, one set of figures.

    The reading guide's numbers table is canonical and the README quotes from
    it. Matching row by row on the claim text means a figure edited in one file
    and not the other fails here rather than shipping as two answers to the
    same question. A table that states one claim twice is rejected before the
    comparison: a stale row left beside a corrected one would otherwise satisfy
    the comparison while showing the reader two numbers.
    """

    guide = read_document(repo_root, _READING_GUIDE, errors)
    if guide is None:
        return
    readme_rows = results_rows(readme)
    guide_rows = results_rows(guide)
    if readme_rows is None or guide_rows is None:
        missing = _README if readme_rows is None else _READING_GUIDE
        errors.append(
            f"{missing}: no results table with a "
            f"'{' | '.join(_RESULTS_TABLE_HEADER)}' header row — the two "
            "tables cannot be compared, so the figures have no shared source."
        )
        return
    if len(readme_rows) < _MIN_RESULT_ROWS:
        errors.append(
            f"{_README}: the results table holds {len(readme_rows)} rows, "
            f"fewer than the {_MIN_RESULT_ROWS} this check needs to mean "
            "anything — agreement over a stub is not agreement."
        )
    reject_repeated_claims(_README, readme_rows, errors)
    guide_figures = reject_repeated_claims(_READING_GUIDE, guide_rows, errors)
    # Over the rows, not the de-duplicated mapping: when a claim IS repeated,
    # both copies are compared, so a stale duplicate is named twice over rather
    # than hidden behind whichever copy happened to come last.
    for claim, figure in readme_rows:
        if claim not in guide_figures:
            errors.append(
                f"{_README}: the results row {claim!r} has no matching row in "
                f"{_READING_GUIDE}'s numbers table, which owns the canonical "
                "statement of every figure."
            )
        elif guide_figures[claim] != figure:
            errors.append(
                f"{_README}: the results row {claim!r} reads {figure!r}, but "
                f"{_READING_GUIDE} records {guide_figures[claim]!r} for the "
                "same claim."
            )
    check_before_columns(readme, guide, errors)


def check_before_columns(readme: str, guide: str, errors: list[str]) -> None:
    """The two tables' before columns, held to each other the way the figures are.

    A figure and the value it moved from are one statement, so the history half
    is stated once too. Both tables must carry the column, every row must have
    a cell in it, and the shared rows must agree.
    """

    columns: dict[str, dict[str, str]] = {}
    for document, text in ((_README, readme), (_READING_GUIDE, guide)):
        before = results_before_column(text)
        if before is None:
            errors.append(
                f"{document}: its results table has no "
                f"{_BEFORE_COLUMN_HEADER!r} column — every row states what the "
                "recording before this one read, including the rows nothing "
                "moved."
            )
            continue
        columns[document] = before
    if len(columns) < 2:
        return
    # Every row of BOTH tables, not only the shared ones: the guide carries
    # rows the README does not, and a row with no history cell states a moved
    # figure with nothing to read it against.
    for document, before in columns.items():
        for claim, stated in before.items():
            if not stated.strip():
                errors.append(
                    f"{document}: the results row {claim!r} has no "
                    f"{_BEFORE_COLUMN_HEADER!r} cell — it is empty, or the row "
                    "is not as wide as the header."
                )
    check_unowned_history(readme, guide, columns, errors)
    for claim, stated in columns[_README].items():
        recorded = columns[_READING_GUIDE].get(claim)
        if recorded is None:
            continue  # the missing row is already reported against the figure
        if strip_links(recorded) != strip_links(stated):
            errors.append(
                f"{_README}: the {_BEFORE_COLUMN_HEADER!r} cell of results row "
                f"{claim!r} reads {stated!r}, but {_READING_GUIDE} records "
                f"{recorded!r} for the same claim."
            )


def check_unowned_history(
    readme: str, guide: str, columns: dict[str, dict[str, str]], errors: list[str]
) -> None:
    """No row may claim its figure moved unless something owns the old value.

    Agreement between the two tables catches a one-sided edit of a history
    cell; it cannot catch the same edit made in both, which is the failure the
    before/after column exists to prevent. So each row whose history cell
    differs from its figure — the rows claiming something moved — must be one
    this module re-derives, or one it names as only compared. A row in neither
    set fails, which is what keeps the unchecked set from growing by accident.

    Only rows the two tables already agree on are examined: where they disagree
    the agreement checks report it, and reporting it twice for one drift would
    name the wrong cause the second time.
    """

    figures = {
        _README: dict(results_rows(readme) or []),
        _READING_GUIDE: dict(results_rows(guide) or []),
    }
    owned = _DERIVED_BEFORE_CLAIMS | _QUOTED_BEFORE_CLAIMS
    for claim, stated in columns[_README].items():
        if claim in owned or not stated.strip():
            continue
        agreed = (
            columns[_READING_GUIDE].get(claim),
            figures[_READING_GUIDE].get(claim),
        )
        if agreed != (stated, figures[_README].get(claim)):
            continue  # a one-sided edit, reported where it is one
        if strip_links(stated) == strip_links(figures[_README].get(claim, "")):
            continue  # nothing moved, so the figure's own source covers it
        errors.append(
            f"{_README}: the results row {claim!r} states a moved figure, but "
            f"its {_BEFORE_COLUMN_HEADER!r} cell {stated!r} is neither "
            "re-derived here nor named as one this module only compares — a "
            "history cell nothing owns is the drift the column exists to stop."
        )


def check_result_sources(repo_root: Path, readme: str, errors: list[str]) -> None:
    """The results figures, re-derived from the bytes that own them.

    Agreement between the two front-door tables catches a one-sided edit; it
    cannot catch a figure edited identically in both. So each row whose source
    is cheap to read is recomputed here instead of compared:

    * the committed-replay count, from the replay files on disk;
    * the citation-compliance figure, from the pinned assertions in the
      committed instrument test;
    * the vent-sighting headline, as arithmetic over the reading guide's own
      cross-tab cells, so the headline cannot drift from the table under it;
    * the proof-vs-inference conviction pair, as the column sums of the
      phase-19 close audit's partition table — together with the injustice
      claim riding in the same row, which holds only while that table's
      proof-present innocent-ejection row is zero.

    What this check does NOT re-derive is deliberate: that the 100 replays
    still *reconstruct* is ``scripts/verify_samples.sh``'s answer, and the
    citation counts come from a full pass over the 9p2i corpus that
    ``tests/eval/test_vj_instruments.py`` already makes. This module is the
    cheap half — seconds, no engine playback — so it binds the document cells
    to those instruments' own pins rather than repeating their work.

    The impostor win rates are re-derived from the manifests by
    :func:`check_sample_provenance`, file-wide, so they need nothing here.
    """

    rows = results_rows(readme)
    if rows is None:
        return  # check_results_agreement reports the missing table
    figures = dict(rows)

    # The verifier's own population, not a glob of the directory: an audit
    # sidecar or a hand-named debug file is a .jsonl that
    # ``scripts/verify_samples.sh`` never reconstructs, and counting it would
    # inflate the figure this row claims was verified.
    replays = sum(
        len(sample_paths(repo_root / _SAMPLE_REPLAY_DIR.format(name=name)))
        for name in _SAMPLE_SETS
    )
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
            f"{replays} of {replays}",
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
            expected = f"{pins['cited_eject_ballots']} / {pins['eject_ballots']}, " + (
                "zero dangling" if dangling == 0 else f"{dangling} dangling"
            )
            compare_result_figure(
                _CITATION_CLAIM,
                figures,
                expected,
                f"the pins in {_CITATION_INSTRUMENT}",
                errors,
            )

    guide = read_document(repo_root, _READING_GUIDE, errors)
    if guide is not None:
        crosstab = vent_crosstab(guide)
        if crosstab is None:
            errors.append(
                f"{_READING_GUIDE}: no vent cross-tab with a "
                f"'{_VENT_TABLE_HEADER}' header row and its two outcome rows — "
                f"the {_README} vent figure has nothing to be derived from."
            )
        else:
            (flagged, _), (unflagged, _) = crosstab
            correct = flagged + unflagged
            expected = f"{flagged} / {correct} = {round(100 * flagged / correct)}%"
            compare_result_figure(
                _VENT_CLAIM,
                figures,
                expected,
                f"the cross-tab in {_READING_GUIDE}",
                errors,
            )

    check_conviction_partition(repo_root, readme, figures, errors)


def check_conviction_partition(
    repo_root: Path, readme: str, figures: dict[str, str], errors: list[str]
) -> None:
    """The proof-vs-inference row, both columns, each from the record that owns it.

    The row is the front door's headline pair, and after a recording it is two
    measurements rather than one: the current record's own pre-registered read
    of those cells, and the read the recording before it published. Each column
    is derived from its own audit and neither is copied from the other, so a
    re-record that moved the figure and left the history behind — or the
    reverse — fails here.
    """

    before = audit_partition(
        repo_root, _PROOF_PARTITION_AUDIT, phase_19_partition, errors
    )
    after = audit_partition(repo_root, _LADDER_TIP_AUDIT, record_partition, errors)
    if before is not None:
        check_partition_arithmetic(*before, errors)
        compare_before_figure(
            readme,
            _PROOF_CLAIM,
            partition_figure(before[0], before[1]),
            f"the partition table in {_PROOF_PARTITION_AUDIT}",
            errors,
        )
    if after is not None:
        proof, non_proof, innocent, proof_innocent = after
        check_record_partition_arithmetic(non_proof, innocent, errors)
        compare_result_figure(
            _PROOF_CLAIM,
            figures,
            partition_figure(proof, non_proof),
            f"the pre-registered read in {_LADDER_TIP_AUDIT}",
            errors,
        )
        check_injustice_cell(readme, innocent, proof_innocent, errors)


def partition_figure(proof: tuple[int, int], non_proof: tuple[int, int]) -> str:
    """One conviction-partition cell, as the front door states it."""

    return (
        f"{proof[0]} / {proof[1]} = {proof[0] / proof[1]:.4f} vs "
        f"{non_proof[0]} / {non_proof[1]} = {non_proof[0] / non_proof[1]:.4f}"
    )


def check_partition_arithmetic(
    proof: tuple[int, int],
    non_proof: tuple[int, int],
    innocent: int,
    proof_innocent: int,
    errors: list[str],
) -> None:
    """The partition table against itself, before either half is published.

    An ejection is either correct or it convicted an innocent, so each accuracy
    row already fixes its own injustice count: ``n - k``. The table states that
    count separately, which makes the two rows checkable against each other —
    and worth checking, because agreeing the front door with a drifted audit
    would otherwise publish an internally contradictory table.
    """

    for label, (correct, total), stated in (
        ("no-proof", non_proof, innocent),
        ("proof-present", proof, proof_innocent),
    ):
        implied = total - correct
        if implied != stated:
            errors.append(
                f"{_PROOF_PARTITION_AUDIT}: the {label} cell reads "
                f"{correct}/{total}, so {implied} of its ejections convicted an "
                f"innocent, but the table's own {label} innocent-ejection row "
                f"totals {stated}."
            )


def check_record_partition_arithmetic(
    non_proof: tuple[int, int], innocent: int, errors: list[str]
) -> None:
    """The record's two decided bars against each other.

    The accuracy bar and the wrongful-ejection bar are read from different
    instruments on the same bytes, and every wrongful ejection sits in the
    non-direct cell — so one bar's ``n - k`` is the other bar's count. A record
    whose two headline bars disagreed would put a contradiction on the front
    door under one date.
    """

    implied = non_proof[1] - non_proof[0]
    if implied != innocent:
        errors.append(
            f"{_LADDER_TIP_AUDIT}: its non-direct accuracy bar reads "
            f"{non_proof[0]}/{non_proof[1]}, so {implied} of those ejections "
            f"convicted an innocent, but its wrongful-ejection bar reads "
            f"{innocent}."
        )


def check_injustice_cell(
    readme: str, innocent: int, proof_innocent: int, errors: list[str]
) -> None:
    """The proof row's own injustice claim, held to the same partition table.

    The row does not only state two accuracies: it states that every innocent
    ejection landed in the cell without proof. That is a claim about a
    different pair of table rows, so it is checked against them — an audit that
    ever records a proof-present innocent ejection must not leave the front
    door still saying there were none.

    The required wording carries the placement, not just the count. A row
    reading "79 of 79 innocent ejections sit in the proof-present cell" states
    the same number and the opposite finding, so matching the count alone would
    be a gate on shape rather than on meaning.
    """

    row = results_row(readme, _PROOF_CLAIM)
    if row is None:
        return  # compare_result_figure already reported the missing row
    if proof_innocent:
        errors.append(
            f"{_README}: the results row {_PROOF_CLAIM!r} says every innocent "
            f"ejection sits in the no-proof cell, but {_LADDER_TIP_AUDIT} "
            f"records {proof_innocent} proof-present innocent ejection(s)."
        )
        return
    stated = _INJUSTICE_CLAIM.format(count=innocent)
    if stated not in " | ".join(row):
        errors.append(
            f"{_README}: the results row {_PROOF_CLAIM!r} does not state "
            f"{stated!r} — {_LADDER_TIP_AUDIT}'s pre-registered read counts "
            f"{innocent} innocent ejections and zero proof-present ones, so "
            "both the count and the cell they landed in have to be stated here."
        )


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


def compare_result_figure(
    claim: str,
    figures: dict[str, str],
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
    readme: str, claim: str, expected: str, source: str, errors: list[str]
) -> None:
    """One README results row's before cell, held to the recording that owns it.

    The README's table is the one checked here; the guide's is held to it, cell
    for cell, by :func:`check_before_columns`.
    """

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
        before.setdefault(cells[0], cells[index] if len(cells) == width else "")
    return before


def vent_crosstab(guide: str) -> tuple[tuple[int, int], tuple[int, int]] | None:
    """The (impostor, innocent) ejection counts of the vent cross-tab's rows.

    Keyed on each row's own ``yes`` / ``no`` label rather than on its position:
    reading the rows by order would silently swap the flagged and unflagged
    populations if the table were ever reordered, and the derived headline
    would then contradict the table it was derived from. Flagged row first.
    ``None`` when the table is absent, mislabelled, or its cells are not a pair
    of integers apiece — format drift the caller reports.
    """

    labelled: dict[str, tuple[int, int]] = {}
    seen_header = False
    for line in guide.splitlines():
        cells = table_cells(line)
        if cells is None or len(cells) < 3:
            if seen_header and labelled:
                break
            continue
        if not seen_header:
            seen_header = cells[0].startswith(_VENT_TABLE_HEADER)
            continue
        if all(_TABLE_RULE_CELL.match(cell) for cell in cells):
            continue
        label = cells[0].split()[0].lower() if cells[0].split() else ""
        if label not in _VENT_ROW_LABELS or label in labelled:
            return None
        try:
            labelled[label] = (int(cells[1]), int(cells[2]))
        except ValueError:
            return None
    if set(labelled) != set(_VENT_ROW_LABELS):
        return None
    return labelled[_VENT_ROW_LABELS[0]], labelled[_VENT_ROW_LABELS[1]]


def phase_19_partition(audit: str) -> _Partition | None:
    """The conviction partition, pooled across the audit table's four sets.

    The recording this one replaced measured these cells per set; pooling its
    columns is what the front door's before column states. Each accuracy cell
    contributes its own ``k/n`` — the leading ratio
    of the cell, ahead of any interval or advisory note — so a set that
    recorded no cell at all (``0/0``) pools as the nothing it is. Rows are
    keyed on their own labels, so reordering the table changes nothing while
    renaming a row fails loud. ``None`` when the table is absent, mislabelled,
    or a cell holds no number: format drift the caller reports rather than
    pools a half-sum through.
    """

    rows: dict[str, list[str]] = {}
    seen_header = False
    for line in audit.splitlines():
        cells = table_cells(line)
        if cells is None or len(cells) < 5:
            if seen_header and rows:
                break
            continue
        if not seen_header:
            seen_header = _EMPHASIS.sub("", cells[0]).strip() == _PROOF_TABLE_HEADER
            continue
        if all(_TABLE_RULE_CELL.match(cell) for cell in cells):
            continue
        label = _EMPHASIS.sub("", cells[0]).strip().lower()
        if label in rows:
            return None
        rows[label] = cells[1:5]
    if set(_PROOF_ROW_LABELS) - set(rows):
        return None

    def ratio(label: str) -> tuple[int, int] | None:
        pooled = [0, 0]
        for cell in rows[label]:
            match = _RATIO_CELL.search(cell)
            if match is None:
                return None
            pooled[0] += int(match.group(1))
            pooled[1] += int(match.group(2))
        return (pooled[0], pooled[1]) if pooled[1] else None

    def total(label: str) -> int | None:
        pooled = 0
        for cell in rows[label]:
            match = _COUNT_CELL.search(cell)
            if match is None:
                return None
            pooled += int(match.group(1))
        return pooled

    proof, non_proof = ratio(_PROOF_ROW), ratio(_NON_PROOF_ROW)
    innocent, proof_innocent = total(_INNOCENT_ROW), total(_PROOF_INNOCENT_ROW)
    if proof is None or non_proof is None:
        return None
    if innocent is None or proof_innocent is None:
        return None
    return proof, non_proof, innocent, proof_innocent


def record_partition(audit: str) -> _Partition | None:
    """The same four cells, read off the record's pre-registered bar sections.

    The record measures them on the new bytes and publishes each bar's pooled
    row; the direct-proof half sits in the accuracy bar's prose, because that
    bar's table reports the non-direct cell per set. ``None`` when a bar, its
    pooled row or the direct-proof sentence is missing — a record whose read
    cannot be located is drift the caller reports rather than guesses through.
    """

    non_proof = bar_pooled_ratio(audit, _ACCURACY_BAR)
    innocent = bar_pooled_count(audit, _INNOCENT_BAR)
    section = bar_section(audit, _ACCURACY_BAR)
    direct = None if section is None else _DIRECT_PROOF_POOLED.search(section)
    if non_proof is None or innocent is None or direct is None:
        return None
    proof = (int(direct.group(1)), int(direct.group(2)))
    return proof, non_proof, innocent, proof[1] - proof[0]


def bar_section(audit: str, bar: int) -> str | None:
    """The record's section for one pre-registered bar, heading to next heading."""

    for match in _RECORD_BAR_HEADING.finditer(audit):
        if int(match.group(1)) != bar:
            continue
        following = _RECORD_BAR_HEADING.search(audit, match.end())
        return audit[match.start() : following.start() if following else len(audit)]
    return None


def bar_pooled_cells(audit: str, bar: int) -> list[str] | None:
    """The ``before`` / ``after`` cells of one bar's pooled row."""

    section = bar_section(audit, bar)
    if section is None:
        return None
    rows = labelled_table_rows(section, _BEFORE_AFTER_HEADER)
    if rows is None:
        return None
    return rows.get(_RECORD_POOLED_LABEL)


def bar_pooled_ratio(audit: str, bar: int) -> tuple[int, int] | None:
    """One bar's pooled ``k/n`` on the new bytes."""

    cells = bar_pooled_cells(audit, bar)
    if cells is None or len(cells) < 2:
        return None
    match = _RATIO_CELL.search(cells[1])
    return None if match is None else (int(match.group(1)), int(match.group(2)))


def bar_pooled_count(audit: str, bar: int) -> int | None:
    """One bar's pooled count on the new bytes."""

    cells = bar_pooled_cells(audit, bar)
    if cells is None or len(cells) < 2:
        return None
    match = _COUNT_CELL.search(cells[1])
    return None if match is None else int(match.group(1))


def audit_partition(
    repo_root: Path,
    relative_path: str,
    parse: Callable[[str], _Partition | None],
    errors: list[str],
) -> _Partition | None:
    """One audit's conviction partition, or ``None`` with the drift reported."""

    audit = read_document(repo_root, relative_path, errors)
    if audit is None:
        return None
    partition = parse(audit)
    if partition is None:
        errors.append(
            f"{relative_path}: its conviction-partition cells cannot be located "
            f"— the {_README} results row {_PROOF_CLAIM!r} has nothing to be "
            "derived from."
        )
    return partition


def check_populated_report_example(
    repo_root: Path, readme: str, errors: list[str]
) -> None:
    """The README's real-report example, held to that report's own numbers.

    The front door hands a reader a populated report precisely because the
    default fake provider produces an empty one. Copying its headline scalars
    into prose would put them one re-record away from being someone else's
    numbers, so each is re-derived from the report's own
    ``vote_correctness`` block.
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
    for label, key, expected in (
        ("ejections", "total_ejections", "{value:d} ejections"),
        ("vote correctness", "vote_correctness_rate", "vote correctness {value:.3f}"),
        ("ejection accuracy", "ejection_accuracy", "ejection accuracy {value:.3f}"),
    ):
        value = block.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(
                f"{_POPULATED_REPORT}: {key} is {value!r}, not a number — the "
                f"{_README} example's {label} claim cannot be re-derived."
            )
            continue
        claim = expected.format(value=value)
        if claim not in paragraph:
            errors.append(
                f"{_README}: the real-report example does not state "
                f"{claim!r} — {_POPULATED_REPORT} records {key} as {value!r}."
            )


def reject_repeated_claims(
    document: str, rows: Sequence[tuple[str, str]], errors: list[str]
) -> dict[str, str]:
    """Claim -> figure for ``rows``, with every repeated claim reported.

    The first figure wins the mapping, so a repeat is reported AND its copy is
    still compared against the canonical table by the caller.
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


def check_volatile_stamps(readme: str, errors: list[str]) -> None:
    """Every count that ages without an edit is stated with an as-of date.

    "364 merged pull requests" is true on the day it is written and quietly
    false afterwards. Requiring the stamp in the SAME sentence keeps the reader
    from having to guess how old the number is, and keeps a later editor from
    updating a count while leaving a two-month-old date beside it.

    The stamp's shape is checked, never its value: reading the true count means
    reaching the network, which no doc check may do.
    """

    for label, pattern in _VOLATILE_COUNTS:
        for match in pattern.finditer(readme):
            sentence = sentence_around(readme, match.start(), match.end())
            stamps = _AS_OF.findall(sentence)
            if not stamps:
                errors.append(
                    f"{_README}:{line_number(readme, match.start())}: the "
                    f"{label} count {match.group(0)!r} carries no 'as of "
                    "YYYY-MM-DD' stamp in its own sentence — a bare count of "
                    "something that changes daily is stale the week after it "
                    f"is written — “{sentence.strip()}”."
                )
                continue
            for stamp in stamps:
                try:
                    date.fromisoformat(stamp)
                except ValueError:
                    errors.append(
                        f"{_README}:{line_number(readme, match.start())}: the "
                        f"{label} count is stamped 'as of {stamp}', which is "
                        "not a calendar date."
                    )


def check_guide_line_citations(repo_root: Path, errors: list[str]) -> None:
    """The reading guide cites anchors and symbols, never line numbers.

    A ``file.ext:NN`` citation is correct only until the next edit of the file
    it names, and the guide carried two dozen of them. The zero is pinned here
    so they cannot come back one at a time.
    """

    guide = read_document(repo_root, _READING_GUIDE, errors)
    if guide is None:
        return
    for match in _LINE_CITATION.finditer(guide):
        errors.append(
            f"{_READING_GUIDE}:{line_number(guide, match.start())}: the "
            f"line-number citation {match.group(0)!r} — cite a heading anchor "
            "or a symbol instead; a line number is wrong on the next edit of "
            "the file it names."
        )


def check_guide_narrative(repo_root: Path, errors: list[str]) -> None:
    """The reading guide's cross-tab and the sentences that narrate it.

    The guide is where the README's vent headline is derived from, so its §3
    cross-tab is bound here to the committed instrument's pinned cells rather
    than left as the root of a chain nothing checks. Its PROSE is bound with
    it: the paragraphs that narrate a table are what a recording leaves behind,
    because a table gets re-quoted row by row and a sentence does not.
    """

    guide = read_document(repo_root, _READING_GUIDE, errors)
    if guide is None:
        return
    pins = crosstab_pins(repo_root, errors)
    ballots = citation_pins(repo_root, errors)
    if "eject_ballots" in ballots:
        compare_narrative_figure(
            guide,
            _GUIDE_BALLOT_PROSE,
            ballots["eject_ballots"],
            f"the pins in {_CITATION_INSTRUMENT}",
            errors,
        )
    check_partner_ballot_row(repo_root, guide, errors)
    if not pins:
        return
    compare_narrative_figure(
        guide,
        _GUIDE_MEETING_PROSE,
        pins[_CROSSTAB_MEETING_TOTAL],
        f"the pins in {_DEDUCTION_INSTRUMENT}",
        errors,
    )
    compare_narrative_ratio(
        guide,
        _GUIDE_NO_PROOF_PROSE,
        (
            pins["unflagged_ejections_impostor"],
            pins["unflagged_ejections_impostor"] + pins["unflagged_ejections_innocent"],
        ),
        errors,
    )
    crosstab = vent_crosstab(guide)
    if crosstab is None:
        return  # check_result_sources reports the unlocatable table
    for (label, impostor_field, innocent_field), row in zip(
        _CROSSTAB_ROW_FIELDS, crosstab
    ):
        expected = (pins[impostor_field], pins[innocent_field])
        if row != expected:
            errors.append(
                f"{_READING_GUIDE}: the cross-tab's {label!r} row reads "
                f"{row[0]} impostor / {row[1]} innocent, but "
                f"{_DEDUCTION_INSTRUMENT} pins {expected[0]} / {expected[1]}."
            )
    labelled: set[str] = set()
    for match in _VENT_ROW_MEETINGS.finditer(guide):
        labelled.add(match.group(1))
        expected_meetings = pins[_CROSSTAB_ROW_MEETINGS[match.group(1)]]
        if int(match.group(2)) != expected_meetings:
            errors.append(
                f"{_READING_GUIDE}:{line_number(guide, match.start())}: the "
                f"cross-tab's {match.group(1)!r} row is labelled "
                f"{match.group(2)} meetings, but {_DEDUCTION_INSTRUMENT} pins "
                f"{expected_meetings}."
            )
    # Each row must CARRY its population, not merely agree when it has one: a
    # row that dropped its "(N meetings)" label would otherwise stop being
    # checked while still reading as a complete table.
    for label in sorted(set(_CROSSTAB_ROW_MEETINGS) - labelled):
        errors.append(
            f"{_READING_GUIDE}: the cross-tab's {label!r} row carries no "
            f"'(N meetings)' population, so the "
            f"{_DEDUCTION_INSTRUMENT} pin for it is checked against nothing."
        )


def check_partner_ballot_row(repo_root: Path, guide: str, errors: list[str]) -> None:
    """The teammate-firewall row, held to the ballot count it is taken over.

    The row lives only in the guide's numbers table, so the README agreement
    check cannot reach it; its denominator moves with every recording, and the
    instrument that counts those ballots owns it.
    """

    instrument = read_document(repo_root, _DEDUCTION_INSTRUMENT, errors)
    if instrument is None:
        return
    pin = _PARTNER_BALLOT_PIN.search(instrument)
    if pin is None:
        errors.append(
            f"{_DEDUCTION_INSTRUMENT}: no pinned impostor-ballot total — the "
            f"{_READING_GUIDE} row {_PARTNER_BALLOT_CLAIM!r} has no committed "
            "source to be checked against."
        )
        return
    rows = results_rows(guide)
    figures = dict(rows) if rows is not None else {}
    expected = _PARTNER_BALLOT_FIGURE.format(total=pin.group(1))
    stated = figures.get(_PARTNER_BALLOT_CLAIM)
    if stated is None:
        errors.append(
            f"{_READING_GUIDE}: its numbers table has no "
            f"{_PARTNER_BALLOT_CLAIM!r} row — the teammate firewall's own "
            "figure is the one row nothing else on the front door repeats."
        )
    elif stated != expected:
        errors.append(
            f"{_READING_GUIDE}: the row {_PARTNER_BALLOT_CLAIM!r} reads "
            f"{stated!r}, but {_DEDUCTION_INSTRUMENT} pins {expected!r}."
        )


def compare_narrative_ratio(
    guide: str,
    pattern: re.Pattern[str],
    expected: tuple[int, int],
    errors: list[str],
) -> None:
    """One narrated ``k of n``, held to the cross-tab cells it is read off."""

    found = False
    for match in pattern.finditer(guide):
        found = True
        stated = (int(match.group(1)), int(match.group(2)))
        if stated == expected:
            continue
        errors.append(
            f"{_READING_GUIDE}:{line_number(guide, match.start())}: the "
            f"narrated ratio {stated[0]} of {stated[1]} disagrees with the "
            f"cross-tab's own unflagged row, which {_DEDUCTION_INSTRUMENT} "
            f"pins at {expected[0]} of {expected[1]}."
        )
    if not found:
        errors.append(
            f"{_READING_GUIDE}: no sentence matching {pattern.pattern!r} — the "
            "unflagged half of the cross-tab is no longer narrated anywhere, "
            "so nothing binds that reading to the table."
        )


def compare_narrative_figure(
    guide: str, pattern: re.Pattern[str], expected: int, source: str, errors: list[str]
) -> None:
    """Every occurrence of one narrated figure, held to the pin that owns it."""

    found = False
    for match in pattern.finditer(guide):
        found = True
        if int(match.group(1)) == expected:
            continue
        errors.append(
            f"{_READING_GUIDE}:{line_number(guide, match.start())}: the "
            f"narrated figure {' '.join(match.group(0).split())!r} disagrees "
            f"with {source} ({expected})."
        )
    if not found:
        errors.append(
            f"{_READING_GUIDE}: no sentence matching {pattern.pattern!r} — the "
            f"figure {source} owns is no longer narrated anywhere, so nothing "
            "binds the prose to it."
        )


def crosstab_pins(repo_root: Path, errors: list[str]) -> dict[str, int]:
    """The samples-9p2i cross-tab cells, from the instrument's own assertions."""

    instrument = read_document(repo_root, _DEDUCTION_INSTRUMENT, errors)
    if instrument is None:
        return {}
    pins: dict[str, int] = {}
    for match in _CROSSTAB_PIN.finditer(instrument):
        field, value = match.group(1), int(match.group(2))
        if pins.setdefault(field, value) != value:
            errors.append(
                f"{_DEDUCTION_INSTRUMENT}: pins {field} at both "
                f"{pins[field]} and {value} — the reading guide's cross-tab "
                "cannot be held to two answers."
            )
    wanted = (
        _CROSSTAB_MEETING_TOTAL,
        *_CROSSTAB_ROW_MEETINGS.values(),
        *(field for _, *fields in _CROSSTAB_ROW_FIELDS for field in fields),
    )
    missing = [field for field in wanted if field not in pins]
    if missing:
        errors.append(
            f"{_DEDUCTION_INSTRUMENT}: no pinned assertion for "
            f"{', '.join(missing)} — the {_READING_GUIDE} cross-tab has no "
            "committed source to be checked against."
        )
        return {}
    return pins


def citation_pins(repo_root: Path, errors: list[str]) -> dict[str, int]:
    """The 9p2i ballot-citation cells, from the instrument's own assertions."""

    instrument = read_document(repo_root, _CITATION_INSTRUMENT, errors)
    if instrument is None:
        return {}
    return {
        match.group(1): int(match.group(2))
        for match in _CITATION_PIN.finditer(instrument)
    }


def check_verdict_figures(repo_root: Path, errors: list[str]) -> None:
    """The record's two decided bars, wherever the front door recounts them.

    The verdict passage is the most-read prose in this repository and it states
    the same two cells the results row states — a conviction accuracy and a
    wrongful-ejection count. Both are held to the record here, so an account of
    why the recording returned a finding cannot contradict the finding.

    Two rules, deliberately different in shape. Every ``k of n = rate`` claim
    in PROSE must be its own arithmetic at the precision it prints — that
    catches a moved numerator, denominator or rate; table rows are skipped
    because each table already has a per-cell check that names the drift more
    precisely. And every sentence about wrongful convictions must name the
    count the record read, the way every "ladder tip" sentence must name the
    baseline; a sentence about the recording before it says that count instead.
    """

    # Both partitions are located by :func:`check_conviction_partition`, which
    # already reports a record whose read cannot be found; a second report here
    # would name the same drift twice.
    partition = audit_partition(repo_root, _LADDER_TIP_AUDIT, record_partition, [])
    previous = audit_partition(
        repo_root, _PROOF_PARTITION_AUDIT, phase_19_partition, []
    )
    if partition is None or previous is None:
        return
    counts = {str(partition[2]), str(previous[2])}
    # The four conviction cells, keyed by denominator: a prose fraction over one
    # of these populations is one of these cells, so an internally consistent
    # rewrite of it ("62 of 103 = 0.6019") still has to be the recorded one.
    recorded = {cell[1]: cell for cell in (*partition[:2], *previous[:2])}
    for document in _CLAIM_DOCUMENTS:
        text = read_document(repo_root, document, errors)
        if text is None:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if table_cells(line) is not None:
                continue  # every table has a per-cell check of its own
            for match in _RATE_CLAIM.finditer(line):
                numerator, denominator = int(match.group(1)), int(match.group(2))
                printed = match.group(3)
                if not denominator:
                    continue
                recomputed = f"{numerator / denominator:.{len(printed) - 2}f}"
                if recomputed != printed:
                    errors.append(
                        f"{document}:{number}: the claim "
                        f"{match.group(0)!r} does not recompute — "
                        f"{numerator}/{denominator} is {recomputed} at the "
                        "precision it prints."
                    )
                cell = recorded.get(denominator)
                if cell is not None and cell[0] != numerator:
                    errors.append(
                        f"{document}:{number}: the claim "
                        f"{match.group(0)!r} is over a conviction population "
                        f"{_LADDER_TIP_AUDIT} and {_PROOF_PARTITION_AUDIT} "
                        f"record, whose cell is {cell[0]}/{cell[1]}."
                    )
        for match in _INJUSTICE_SENTENCE.finditer(text):
            sentence = sentence_around(text, match.start(), match.end())
            if counts & set(_WHOLE_NUMBER.findall(sentence)):
                continue
            errors.append(
                f"{document}:{line_number(text, match.start())}: a "
                "wrongful-ejection sentence names neither the count the record "
                f"read ({partition[2]}) nor the one before it ({previous[2]}) "
                f"— “{' '.join(sentence.split())}”."
            )


def check_featured_exhibits(repo_root: Path, errors: list[str]) -> None:
    """Every game the reading guide names is one the spectator actually features.

    The guide points a reader at named seeds and the spectator opens a curated
    strip; if the two drift, the guide sends people looking for a card that is
    not there. The picker's list is the committed data, so it is the one that
    decides.
    """

    guide = read_document(repo_root, _READING_GUIDE, errors)
    picker = read_document(repo_root, _PICKER, errors)
    if guide is None or picker is None:
        return
    block = _FEATURED_BLOCK.search(picker)
    if block is None:
        errors.append(
            f"{_PICKER}: no FEATURED_GAMES list — the reading guide's named "
            "exhibits have nothing to be checked against."
        )
        return
    featured = {
        (set_name, int(seed))
        for set_name, seed in _FEATURED_ENTRY.findall(block.group(1))
    }
    named = [
        (match.group(1), int(match.group(2)), line_number(guide, match.start()))
        for match in _GUIDE_EXHIBIT.finditer(guide)
    ]
    if len(named) < _MIN_EXHIBIT_SEEDS:
        errors.append(
            f"{_READING_GUIDE}: names {len(named)} featured games, fewer than "
            f"the {_MIN_EXHIBIT_SEEDS} this check needs to mean anything — a "
            "paragraph that lost its exhibits would otherwise pass vacuously."
        )
    for set_name, seed, number in named:
        if (set_name, seed) not in featured:
            errors.append(
                f"{_READING_GUIDE}:{number}: names {set_name} seed {seed} as an "
                f"exhibit, but {_PICKER}'s curated list does not carry it — the "
                "guide would point a reader at a game the spectator never opens."
            )


def check_relative_links(repo_root: Path, errors: list[str]) -> None:
    """Every relative link on the front door and the published pages resolves.

    Offline by construction: the fragment is stripped and the path is stat-ed.
    External URLs are not this check's business — nothing here reaches the
    network — but a broken relative link is the front door telling a reader to
    go somewhere that does not exist.
    """

    for document in _LINKED_DOCUMENTS + _PUBLISHED_DOCUMENTS:
        text = read_document(repo_root, document, errors)
        if text is None:
            continue
        for target, resolved in relative_targets(repo_root, document, text):
            if resolved.exists():
                continue
            shown = (
                resolved.relative_to(repo_root)
                if resolved.is_relative_to(repo_root)
                else resolved
            )
            errors.append(
                f"{document}: the relative link {target!r} resolves to {shown}"
                ", which does not exist."
            )


def relative_targets(
    repo_root: Path, document: str, text: str
) -> Iterator[tuple[str, Path]]:
    """Each relative markdown target in ``text``, with the path it names.

    Absolute URLs and in-page anchors are skipped — neither names a file. The
    fragment is dropped before resolution, so ``docs/glossary.md#term`` is the
    glossary file; whether the anchor exists is
    :func:`check_dialect_terms`'s question, not this one.
    """

    base = posixpath.dirname(document)
    for match in _MARKDOWN_LINK.finditer(text):
        target = match.group(1)
        if target.startswith("#") or _ABSOLUTE_TARGET.match(target):
            continue
        path = target.split("#", 1)[0]
        if not path:
            continue
        yield target, repo_root / posixpath.normpath(posixpath.join(base, path))


def check_review_map(repo_root: Path, errors: list[str]) -> None:
    """The review index accounts for every finding, and its map resolves.

    Two halves. **Coverage**: every finding id the phase's contracts declare
    they act on must appear somewhere in the index — mapped to its fix,
    retracted, or listed as not acted on — so a deleted row is a failure rather
    than a quiet omission, which is the difference between an index and a
    highlight reel. **Resolution**: each map row is held to the contract that
    owns the change, whose section must actually cite the finding, because a row
    moved to a neighbouring task would otherwise read as true. The pull-request
    number's own resolution needs full git history, so it lives in the unit
    tests, which can skip on a shallow clone rather than pass on one.
    """

    index = read_document(repo_root, _REVIEW_INDEX, errors)
    contract = read_document(repo_root, _PHASE_20_CONTRACT, errors)
    if index is None or contract is None:
        return
    rows = review_map_cells(index)
    if not rows:
        errors.append(
            f"{_REVIEW_INDEX}: no acted-on map rows found under the "
            f"{' | '.join(_REVIEW_MAP_HEADER)} header — that table is what links "
            "each published finding to the change that closed it."
        )
        return

    declared = phase_finding_ids(contract)
    if not declared:
        errors.append(
            f"{_PHASE_20_CONTRACT}: no '{_SECTION_REFS_PREFIX}' line names a "
            "review finding — the index's coverage cannot be checked against a "
            "contract document that parses to nothing."
        )
    named = set(_FINDING_ID.findall(index))
    for missing in sorted(declared - named, key=finding_order):
        errors.append(
            f"{_REVIEW_INDEX}: {missing} is named by a {_PHASE_20_CONTRACT} "
            "contract but appears nowhere in the index — every finding the phase "
            "touched is mapped to its fix, retracted, or listed as not acted on."
        )

    sections = phase_task_sections(contract)
    mapped: dict[str, int] = {}
    for number, cells in rows:
        finding = _REVIEW_FINDING.match(cells[0])
        task = _REVIEW_TASK.match(cells[2])
        pull_request = _REVIEW_PULL_REQUEST.match(cells[3])
        if finding is None or task is None or pull_request is None:
            errors.append(
                f"{_REVIEW_INDEX}:{number}: the map row {cells[0]!r} does not "
                "parse — a row is a `G-n`/`C-n` finding, a claim, a bare task id "
                "and one [#N](…/pull/N) link."
            )
            continue
        if pull_request.group(1) != pull_request.group(2):
            errors.append(
                f"{_REVIEW_INDEX}:{number}: the {finding.group(1)} row shows "
                f"#{pull_request.group(1)} but links pull request "
                f"#{pull_request.group(2)}."
            )
        section = sections.get(task.group(1))
        if section is None:
            errors.append(
                f"{_REVIEW_INDEX}:{number}: the {finding.group(1)} row credits "
                f"task {task.group(1)}, which is not a contract in "
                f"{_PHASE_20_CONTRACT}."
            )
            continue
        if re.search(rf"\b{re.escape(finding.group(1))}\b", section) is None:
            errors.append(
                f"{_REVIEW_INDEX}:{number}: the {finding.group(1)} row credits "
                f"task {task.group(1)}, whose contract in {_PHASE_20_CONTRACT} "
                f"never names {finding.group(1)}."
            )
        first = mapped.setdefault(finding.group(1), number)
        if first != number:
            errors.append(
                f"{_REVIEW_INDEX}:{number}: {finding.group(1)} is mapped twice "
                f"(also at line {first}) — one finding, one closing change, or "
                "the two rows drift apart."
            )


def phase_finding_ids(contract: str) -> set[str]:
    """Every review finding id the phase's contracts declare they act on.

    Read from the ``**Section refs:**`` lines rather than from whole sections: a
    contract's section-reference line is where it states what it addresses, and
    the surrounding prose cites neighbouring findings as context.
    """

    return {
        finding
        for line in contract.splitlines()
        if line.startswith(_SECTION_REFS_PREFIX)
        for finding in _FINDING_ID.findall(line)
    }


def finding_order(finding: str) -> tuple[str, int]:
    """``G-7`` before ``G-12``: sort a register id by number, not by string."""

    register, _, number = finding.partition("-")
    return register, int(number)


def review_map_cells(index: str) -> list[tuple[int, list[str]]] | None:
    """``(line, cells)`` for each acted-on map row, or ``None`` with no table.

    Located by its header cells rather than by the heading above it, so renaming
    the section cannot silently disable the check.
    """

    rows: list[tuple[int, list[str]]] | None = None
    width = len(_REVIEW_MAP_HEADER)
    for number, line in enumerate(index.splitlines(), 1):
        cells = table_cells(line)
        if cells is None or len(cells) != width:
            if rows is not None:
                break
            continue
        if rows is None:
            if tuple(cells) == _REVIEW_MAP_HEADER:
                rows = []
            continue
        if all(_TABLE_RULE_CELL.match(cell) for cell in cells):
            continue
        rows.append((number, cells))
    return rows


def review_map_rows(index: str) -> list[tuple[int, str, str, int]]:
    """``(line, finding, task id, pull request)`` for each parseable map row."""

    parsed: list[tuple[int, str, str, int]] = []
    for number, cells in review_map_cells(index) or []:
        finding = _REVIEW_FINDING.match(cells[0])
        task = _REVIEW_TASK.match(cells[2])
        pull_request = _REVIEW_PULL_REQUEST.match(cells[3])
        if finding is None or task is None or pull_request is None:
            continue
        parsed.append(
            (number, finding.group(1), task.group(1), int(pull_request.group(2)))
        )
    return parsed


def phase_task_sections(contract: str) -> dict[str, str]:
    """Each ``### Task N.M — …`` section of a phase contract, keyed by task id."""

    headings = list(_PHASE_TASK_HEADING.finditer(contract))
    return {
        match.group(1): contract[
            match.start() : (
                headings[index + 1].start()
                if index + 1 < len(headings)
                else len(contract)
            )
        ]
        for index, match in enumerate(headings)
    }


def heading_anchors(markdown: str) -> set[str]:
    """The GitHub anchor of every heading in ``markdown``."""

    return {
        _ANCHOR_STRIP.sub("", heading).strip().lower().replace(" ", "-")
        for heading in _HEADING.findall(markdown)
    }


def results_rows(markdown: str) -> list[tuple[str, str]] | None:
    """The ``What`` / ``Figure`` rows of the document's results table, in order.

    Located by its header cells rather than by the heading above it, so
    renaming the section does not silently disable the agreement check. A list
    rather than a mapping, because a repeated claim is itself a finding and
    collapsing it here would erase the evidence for it. ``None`` when no such
    table exists (format drift the caller reports).
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
        rows.append((cells[0], cells[1]))
    return rows


def results_row(markdown: str, claim: str) -> list[str] | None:
    """Every cell of the results row stating ``claim``, or ``None``.

    :func:`results_rows` keeps only the two compared cells; a row whose source
    column carries a claim of its own needs the whole row.
    """

    for line in markdown.splitlines():
        cells = table_cells(line)
        if cells is not None and cells and cells[0] == claim:
            return cells
    return None


def table_cells(line: str) -> list[str] | None:
    """The cells of one markdown table row, or ``None`` if it is not one."""

    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def lever_section(text: str) -> str | None:
    """.env.example's belief-substrate section, or ``None`` if unlocatable.

    The section runs from the dashed rule closing its title banner to the
    dashed rule opening the next section's banner (or end of file).
    """

    title = text.find(_LEVER_SECTION_TITLE)
    if title == -1:
        return None
    rules = [m for m in _SECTION_RULE.finditer(text) if m.start() > title]
    if not rules:
        return None
    start = rules[0].end()
    end = rules[1].start() if len(rules) > 1 else len(text)
    return text[start:end]


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


def sentence_around(text: str, start: int, end: int) -> str:
    """The whole sentence containing ``text[start:end]``, however long.

    Bounded first by the PARAGRAPH — a run of non-blank lines — then clipped to
    the nearest sentence boundary, a period followed by whitespace, on each
    side. The paragraph rather than the line, because the front door mixes
    unwrapped prose (README.md, one line per paragraph) with hard-wrapped prose
    (the glossary, the history), and a sentence broken across two wrapped lines
    is still one sentence. No length cap: a claim hundreds of characters from
    its subject is still the same sentence, and truncating would hide it.
    """

    paragraph_start = 0
    for blank in _BLANK_LINE.finditer(text, 0, start):
        paragraph_start = blank.end()
    following = _BLANK_LINE.search(text, end)
    paragraph_end = len(text) if following is None else following.start()

    left = text[paragraph_start:start]
    boundaries = list(_SENTENCE_END.finditer(left))
    if boundaries:
        left = left[boundaries[-1].end() :]
    right = text[end:paragraph_end]
    boundary = _SENTENCE_END.search(right)
    if boundary is not None:
        right = right[: boundary.start()]
    return left + text[start:end] + right


def line_number(text: str, offset: int) -> int:
    """The 1-indexed line ``offset`` falls on."""

    return text.count("\n", 0, offset) + 1


def read_document(repo_root: Path, relative_path: str, errors: list[str]) -> str | None:
    """``repo_root/relative_path``'s text, or ``None`` with an error recorded."""

    try:
        return (repo_root / relative_path).read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{relative_path}: unreadable ({exc}).")
        return None


if __name__ == "__main__":
    raise SystemExit(main())
