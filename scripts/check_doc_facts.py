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

Four checks. Each accumulates precise errors; all of them are reported
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
   columns record must be named in the paragraph as well.
2. **Ladder tip.** ``audits/audit-phase-18-close.md`` owns which baseline the
   substrate ladder stands at. Every README sentence naming the "ladder tip" —
   the whole sentence, however long — must name that baseline, and no other.
3. **Lever registry vs .env.example.** ``orchestrator.replay`` owns the live
   substrate-lever registry. Every still-toggleable lever must be documented
   IN the belief-substrate section with a commented example line showing its
   bare-environment default — and ONLY that way: an active (uncommented)
   export anywhere in the template fails, because a copied .env would flip
   the substrate away from the committed baseline-6 record. Every graduated
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
   recomputed ``"<numerator>/<denominator> = <rate>"``. A report whose own
   ``vote_correctness_rate`` field disagrees with its counts fails too. The
   substrate those rates are attributed to is checked with them: the model, the
   prompt-set token and the substrate-flag stamp come from the four
   ``MANIFEST.md`` files, the sets must agree on all three, and the module must
   name the first two (the flag stamp is thirteen keys wide — held to agreement,
   not copied into prose). Finally, while any recorded set reads below 1.0 the
   module may not call the rate
   structurally pinned: a zero-flag EJECT that cites a transcript turn or a
   private observation id is legal by design
   (``meetings.manager.guard_ballot_citation``), so the pin would be prose the
   committed bytes refute. Frontend copy is deliberately NOT scanned — the
   spectator surface has its own owner.

``--repo-root`` points the document and source reads at another tree (the unit
tests perturb a copy); it defaults to this checkout. The lever registry ALWAYS
comes from the live import, never from ``--repo-root``: the registry is code,
and a doc copy is checked against the levers this build actually ships.

Exit 0 when every checked fact matches, 1 with every failure printed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
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

from orchestrator.replay import (  # noqa: E402
    SUBSTRATE_FLAG_KEYS,
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    substrate_flag_snapshot,
)

_README: Final = "README.md"
_ENV_EXAMPLE: Final = ".env.example"
_LADDER_TIP_AUDIT: Final = "audits/audit-phase-18-close.md"
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
# The reports run to tens of megabytes; the block is eight scalar fields, so a
# runaway scan means the report format drifted rather than a bigger block.
_VOTE_CORRECTNESS_BLOCK_MAX_LINES: Final = 64
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

# The .env.example section whose AILIBI_*= assignments must all resolve to a
# live registry key, delimited by the repo's dashed section banners.
_LEVER_SECTION_TITLE: Final = "# Belief-substrate levers"
_SECTION_RULE: Final = re.compile(r"^# -{20,}[ \t]*$", re.MULTILINE)
_ENV_ASSIGNMENT: Final = re.compile(r"^#?[ \t]*(AILIBI_[A-Z0-9_]+)=", re.MULTILINE)
# The graduated note is the contiguous comment block opening with this marker;
# the graduated/always-ON labels must live IN it, not merely near it.
_GRADUATED_NOTE_MARKER: Final = "# GRADUATED LEVERS"
_BLANK_LINE: Final = re.compile(r"\n[ \t]*\n")


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
    return 0


def check_facts(repo_root: Path) -> list[str]:
    """Every checked-fact failure under ``repo_root``, in check order."""

    errors: list[str] = []
    readme = read_document(repo_root, _README, errors)
    if readme is not None:
        check_sample_provenance(repo_root, readme, errors)
        check_ladder_tip(repo_root, readme, errors)
    check_lever_registry(repo_root, errors)
    check_vote_correctness_sentinel(repo_root, errors)
    return errors


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

    for claim_match in _WIN_RATE_CLAIM.finditer(readme):
        name = claim_match.group(2)
        if name not in rates:
            continue
        impostor_wins, total = rates[name]
        expected = round(100 * impostor_wins / total)
        if int(claim_match.group(1)) != expected:
            errors.append(
                f"{_README}:{line_number(readme, claim_match.start())}: win-rate "
                f"claim {claim_match.group(0)!r} disagrees with "
                f"{_MANIFEST_PATH.format(name=name)} "
                f"({impostor_wins}/{total} = {expected}%)."
            )


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


def check_ladder_tip(repo_root: Path, readme: str, errors: list[str]) -> None:
    """No README "ladder tip" sentence may name a baseline other than the tip.

    The tip itself is parsed from the phase-18 close audit, which is where the
    ladder's standing is recorded; whitespace is collapsed first because the
    audit wraps its prose mid-sentence.
    """

    audit = read_document(repo_root, _LADDER_TIP_AUDIT, errors)
    if audit is None:
        return
    recorded = _AUDIT_LADDER_TIP.findall(re.sub(r"\s+", " ", audit))
    if not recorded:
        errors.append(
            f"{_LADDER_TIP_AUDIT}: no 'the ladder tip stands at baseline N' "
            "sentence — the ladder tip has no committed source to check against."
        )
        return
    if len(set(recorded)) > 1:
        named = ", ".join(f"baseline {tip}" for tip in sorted(set(recorded)))
        errors.append(
            f"{_LADDER_TIP_AUDIT}: disagreeing ladder-tip records ({named}); "
            "the audit must record one tip."
        )
        return

    tip = recorded[0]
    for phrase in _LADDER_TIP_PHRASE.finditer(readme):
        sentence = sentence_around(readme, phrase.start(), phrase.end())
        mentions = _BASELINE_MENTION.findall(sentence)
        if not mentions:
            errors.append(
                f"{_README}:{line_number(readme, phrase.start())}: a 'ladder "
                "tip' sentence names no baseline at all — every ladder-tip "
                f"claim must name baseline {tip} ({_LADDER_TIP_AUDIT}) — "
                f"“{sentence.strip()}”."
            )
            continue
        for number in mentions:
            if number == tip:
                continue
            errors.append(
                f"{_README}:{line_number(readme, phrase.start())}: a 'ladder "
                f"tip' sentence names baseline {number}, but "
                f"{_LADDER_TIP_AUDIT} records the ladder tip at baseline "
                f"{tip} — “{sentence.strip()}”."
            )


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
            or denominator <= 0
        ):
            errors.append(
                f"{relative_path}: the vote_correctness block does not carry a "
                "positive impostor_ejections beside an integer "
                f"evidence_backed_impostor_ejections (read {numerator!r} of "
                f"{denominator!r}), so the rate cannot be re-derived."
            )
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
        stamped = [line for line in stamp_lines if set_dir in line]
        if len(stamped) != 1:
            errors.append(
                f"{_VOTE_CORRECTNESS_MODULE}: expected exactly one line naming "
                f"{set_dir!r} (its vote-correctness stamp), found "
                f"{len(stamped)} — the checked claim has no unambiguous home."
            )
        elif claim not in stamped[0]:
            errors.append(
                f"{_VOTE_CORRECTNESS_MODULE}: the {set_dir} stamp reads "
                f"{stamped[0].strip()!r}, but {relative_path} records {claim}."
            )

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


def check_vote_correctness_provenance(
    repo_root: Path, module: str, errors: list[str]
) -> None:
    """The substrate the vote-correctness stamps are attributed to.

    A rate means nothing without the recording it came from. Three columns of
    every recorded set's ``MANIFEST.md`` own that recording — ``model``,
    ``prompt_versions`` and the substrate ``flags`` — and all three must agree
    across the sets: one provenance line cannot describe two substrates, so a
    split fails here rather than silently describing whichever set happened to
    be read first. The model and the prompt-set token (``<family>.<version>``)
    are short enough to be named in the module and are required there; the
    flags stamp is thirteen keys wide, so it is held to agreement only —
    naming it in prose would be a second copy to rot.
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
        models.update(row.model.strip() for row in rows)
        for row in rows:
            # Entries are ``template.family.version``; the no-meetings sentinel
            # and empty cells have no dotted shape and are skipped.
            for entry in row.prompt_versions.split(","):
                segments = entry.strip().split(".")
                if len(segments) >= 3:
                    prompt_tokens.add(f"{segments[-2]}.{segments[-1]}")
            # Order-insensitive: the stamp is the SET of flags a row was
            # recorded under, not the order the writer happened to render.
            flag_stamps.add(
                ", ".join(
                    sorted(
                        flag.strip() for flag in row.flags.split(",") if flag.strip()
                    )
                )
            )

    for label, tokens, name_in_module in (
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
        if not name_in_module:
            continue
        for token in tokens:
            if token not in module:
                errors.append(
                    f"{_VOTE_CORRECTNESS_MODULE}: the vote-correctness stamps do "
                    f"not name the {label} {token!r} they were recorded on — "
                    f"{_SET_MANIFEST_PATH.format(set_dir=_RECORDED_SETS[0])} and "
                    "its siblings record it on every row."
                )


def read_vote_correctness_block(
    repo_root: Path, relative_path: str, errors: list[str]
) -> dict[str, object] | None:
    """The report's ``vote_correctness`` object, without parsing the document.

    The committed reports reach tens of megabytes, so the block is decoded from
    its own key rather than by loading the whole file. Format drift (no such
    key, or a block that never closes) is reported, never papered over.
    """

    path = repo_root / relative_path
    block: list[str] = []
    try:
        with path.open(encoding="utf-8") as handle:
            depth = 0
            for line in handle:
                if not block:
                    if not line.strip().startswith(_VOTE_CORRECTNESS_KEY):
                        continue
                    block.append("{")
                    depth = 1
                    continue
                depth += line.count("{") - line.count("}")
                block.append(line)
                if depth <= 0 or len(block) > _VOTE_CORRECTNESS_BLOCK_MAX_LINES:
                    break
    except OSError as exc:
        errors.append(f"{relative_path}: unreadable ({exc}).")
        return None

    if not block:
        errors.append(
            f"{relative_path}: no {_VOTE_CORRECTNESS_KEY} key — the eval-report "
            "format drifted, so the vote-correctness stamps have no source."
        )
        return None
    try:
        decoded, _ = json.JSONDecoder().raw_decode("".join(block))
    except ValueError as exc:
        decoded = None
        errors.append(
            f"{relative_path}: the {_VOTE_CORRECTNESS_KEY} block does not parse "
            f"as one JSON object ({exc})."
        )
    if not isinstance(decoded, dict):
        if decoded is not None:
            errors.append(
                f"{relative_path}: {_VOTE_CORRECTNESS_KEY} is not a JSON object."
            )
        return None
    return decoded


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

    Bounded first by the line (README paragraphs are single long lines, so a
    sentence never spans one), then clipped to the nearest sentence boundary —
    a period followed by whitespace — on each side. No length cap: a claim
    hundreds of characters from its subject is still the same sentence, and
    truncating would hide it.
    """

    line_start = text.rfind("\n", 0, start) + 1
    newline = text.find("\n", end)
    line_end = len(text) if newline == -1 else newline

    left = text[line_start:start]
    boundaries = list(_SENTENCE_END.finditer(left))
    if boundaries:
        left = left[boundaries[-1].end() :]
    right = text[end:line_end]
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
