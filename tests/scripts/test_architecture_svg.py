"""The architecture picture stays hand-authored, legible text.

``docs/media/architecture.svg`` is checked as committed bytes: it parses, embeds
nothing, says what the layering is, follows the reader's theme, and every text
class clears a contrast floor on the ground it is painted on, in both palettes
and over both page colours. Each check runs against the committed file and
against a planted defect that has to make it fire.
"""

from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]

_ARCHITECTURE_SVG = "docs/media/architecture.svg"
# A hand-authored diagram bigger than this is a raster export in disguise, or has
# stopped being one picture.
_SVG_BYTE_CEILING = 60_000

# What the picture must SAY, not merely how it is built: the packages of the
# layering, the protocol the reasoning layer reaches a model through, the
# firewall contract by name, and the legend that stops arrows being read as
# imports. Matched against the concatenated <text> content, so labels flattened
# into outlined paths fail here too.
_SVG_REQUIRED_LABELS = (
    "engine/",
    "observation/",
    "agents/",
    "meetings/",
    "llm/",
    "orchestrator/",
    "eval/",
    "api/",
    "frontend/",
    "LLMClient Protocol",
    "ObservationPacket",
    "ActionIntent",
    "GENERATED",
    "Agents must not",
    "import engine",
    "import-linter",
    "Arrows are data flow",
    "imports run the other way",
)
_DARK_THEME_BLOCK = "@media (prefers-color-scheme: dark)"
_HEX_COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}\b")
_COLOUR_KEYWORD = re.compile(r"\b(?:black|white)\b", re.IGNORECASE)
_CSS_URL = re.compile(r"url\(\s*['\"]?([^'\")]*)")

# Legibility is a contrast ratio, not the absence of the two extreme colours: a
# palette of two near-identical mid-tones is unreadable and contains neither.
# The two `svg { … }` blocks are the light palette and the dark one the media
# query swaps in; every ink is measured against every ground it is painted on.
_PALETTE_BLOCK = re.compile(r"svg\s*\{([^}]*)\}")
_CUSTOM_PROPERTY = re.compile(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\s*;")
_CONTRAST_FLOOR = 4.5

# The backdrop is deliberately translucent, so the ground under a label on it is
# not the declared colour but the composite over whatever page carries the image
# — and `prefers-color-scheme` follows the reader's OS while GitHub's own theme
# does not have to, so both pages are live for both palettes. The mismatch case
# (light palette on a dark page) is the one that decides legibility, and reading
# the declared colour instead of the composite is what hid it (Codex, PR #374).
_BACKDROP_OPACITY = re.compile(r'class="backdrop"[^>]*fill-opacity="([\d.]+)"')
_PAGE_GROUNDS = (("a light page", "#ffffff"), ("a dark page", "#0d1117"))

# Which ground each text class is painted on. The BINDING from a class to the
# colour it inks with is read out of the stylesheet, never assumed, so
# repointing `.body` at `--card` fails here instead of rendering invisibly
# (Codex, PR #374). Only the layout — which class sits on which rect — is
# pinned, and the covering assertion below makes that safe by default: a text
# class that is not in this table is unaccounted for and fails.
_TEXT_CLASS_GROUNDS: dict[str, tuple[str, ...]] = {
    "title": ("backdrop",),
    "subtitle": ("backdrop",),
    "legend": ("backdrop",),
    "flow-label": ("backdrop",),
    "fire-label": ("backdrop",),
    "fire-note": ("backdrop",),
    "name": ("card-strong",),
    "name-sm": ("card",),
    "body": ("card", "card-strong"),
}
_CSS_RULE = re.compile(r"\.([\w-]+)\s*\{([^}]*)\}")
_FILL_VARIABLE = re.compile(r"fill:\s*var\(--([\w-]+)\)")
_TEXT_CLASS_ATTR = re.compile(r'<text[^>]*class="([\w-]+)"')


def _committed(name: str) -> str:
    return (_REPO_ROOT / name).read_text(encoding="utf-8")


def _channels(colour: str) -> tuple[int, int, int]:
    digits = colour.lstrip("#")
    if len(digits) in (3, 4):
        digits = "".join(digit * 2 for digit in digits)
    red, green, blue = (int(digits[index : index + 2], 16) for index in (0, 2, 4))
    return red, green, blue


def _relative_luminance(colour: str) -> float:
    """WCAG relative luminance of a `#rgb` / `#rrggbb` colour."""

    linear = [
        value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4
        for value in (channel / 255 for channel in _channels(colour))
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(ink: str, ground: str) -> float:
    luminances = sorted((_relative_luminance(ink), _relative_luminance(ground)))
    return (luminances[1] + 0.05) / (luminances[0] + 0.05)


def _over(colour: str, page: str, alpha: float) -> str:
    """`colour` at `alpha` composited over `page` — the ground a reader sees."""

    return "#" + "".join(
        f"{round(alpha * front + (1 - alpha) * back):02x}"
        for front, back in zip(_channels(colour), _channels(page), strict=True)
    )


def _contrast_problems(text: str) -> list[str]:
    """Every ink/ground pair, in both palettes, that falls under the floor."""

    palettes = _PALETTE_BLOCK.findall(text)
    if len(palettes) != 2:
        return [
            f"{_ARCHITECTURE_SVG}: found {len(palettes)} `svg {{ … }}` palette "
            "blocks, not the light one and the dark one"
        ]
    light = dict(_CUSTOM_PROPERTY.findall(palettes[0]))
    dark = {**light, **dict(_CUSTOM_PROPERTY.findall(palettes[1]))}

    opacity = _BACKDROP_OPACITY.search(text)
    if opacity is None or float(opacity.group(1)) >= 1.0:
        return [
            f"{_ARCHITECTURE_SVG}: the backdrop is opaque; it must let the "
            "reader's page through, so that a light card is never painted flat "
            "over a dark one"
        ]
    alpha = float(opacity.group(1))

    problems: list[str] = []
    used = set(_TEXT_CLASS_ATTR.findall(text))
    unaccounted = used - _TEXT_CLASS_GROUNDS.keys()
    unused = _TEXT_CLASS_GROUNDS.keys() - used
    if unaccounted or unused:
        problems.append(
            f"{_ARCHITECTURE_SVG}: the text classes and the ground table "
            f"disagree — unaccounted {sorted(unaccounted)}, "
            f"unused {sorted(unused)}"
        )

    inks = {
        name: match.group(1)
        for name, body in _CSS_RULE.findall(text)
        if (match := _FILL_VARIABLE.search(body)) is not None
    }
    for name in sorted(used & _TEXT_CLASS_GROUNDS.keys()):
        if name not in inks:
            problems.append(
                f"{_ARCHITECTURE_SVG}: .{name} inks with no `fill: var(--…)`, "
                "so nothing here can measure what it renders as"
            )
            continue
        ink = inks[name]
        for theme, palette in (("light", light), ("dark", dark)):
            for ground_name in _TEXT_CLASS_GROUNDS[name]:
                if ink not in palette or ground_name not in palette:
                    problems.append(
                        f"{_ARCHITECTURE_SVG}: the {theme} palette defines no "
                        f"--{ink} on --{ground_name} pair"
                    )
                    continue
                if ground_name != "backdrop":
                    # Cards are painted opaque, so their fill IS the ground.
                    ratio = _contrast_ratio(palette[ink], palette[ground_name])
                    if ratio < _CONTRAST_FLOOR:
                        problems.append(
                            f"{_ARCHITECTURE_SVG}: .{name} (--{ink}) on "
                            f"--{ground_name} in the {theme} palette contrasts "
                            f"{ratio:.1f}:1, under the {_CONTRAST_FLOOR}:1 floor"
                        )
                    continue
                for where, page in _PAGE_GROUNDS:
                    ground = _over(palette["backdrop"], page, alpha)
                    ratio = _contrast_ratio(palette[ink], ground)
                    if ratio < _CONTRAST_FLOOR:
                        problems.append(
                            f"{_ARCHITECTURE_SVG}: .{name} (--{ink}) on the "
                            f"{theme} backdrop over {where} ({ground}) contrasts "
                            f"{ratio:.1f}:1, under the {_CONTRAST_FLOOR}:1 floor"
                        )
    return problems


def _svg_problems(text: str) -> list[str]:
    """Every way the committed picture stops being hand-authored, legible text."""

    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as exc:
        return [f"{_ARCHITECTURE_SVG}: does not parse as XML ({exc})"]

    problems: list[str] = []
    size = len(text.encode("utf-8"))
    if size > _SVG_BYTE_CEILING:
        problems.append(
            f"{_ARCHITECTURE_SVG}: {size} bytes, over the {_SVG_BYTE_CEILING}-byte "
            "ceiling for a hand-authored diagram"
        )

    tags = {element.tag.rsplit("}", 1)[-1] for element in root.iter()}
    problems.extend(
        f"{_ARCHITECTURE_SVG}: carries <{banned}>; the picture must be "
        "hand-authored SVG, not an embedded raster or a foreign document"
        for banned in ("image", "foreignObject")
        if banned in tags
    )
    if any(
        name.rsplit("}", 1)[-1] == "href"
        for element in root.iter()
        for name in element.attrib
    ):
        problems.append(
            f"{_ARCHITECTURE_SVG}: an element carries an href; the picture must "
            "reference nothing outside itself"
        )
    if "@font-face" in text or "data:" in text:
        problems.append(
            f"{_ARCHITECTURE_SVG}: declares a downloaded or embedded asset; "
            "system font families and inline shapes only"
        )
    problems.extend(
        f"{_ARCHITECTURE_SVG}: url({target!r}) points outside the file"
        for target in _CSS_URL.findall(text)
        if not target.startswith("#")
    )

    for token in _HEX_COLOUR.findall(text):
        digits = token[1:]
        if len(digits) in (3, 4):
            digits = "".join(digit * 2 for digit in digits)
        if digits[:6].lower() in {"000000", "ffffff"}:
            problems.append(
                f"{_ARCHITECTURE_SVG}: uses {token}; pure black and pure white "
                "read as damage in one of the two GitHub themes"
            )
    keyword = _COLOUR_KEYWORD.search(text)
    if keyword is not None:
        problems.append(
            f"{_ARCHITECTURE_SVG}: uses the colour keyword {keyword.group(0)!r}; "
            "pure black and pure white read as damage in one of the two themes"
        )
    if _DARK_THEME_BLOCK not in text:
        problems.append(
            f"{_ARCHITECTURE_SVG}: has no {_DARK_THEME_BLOCK} block, so it cannot "
            "follow the reader's theme"
        )
    problems.extend(_contrast_problems(text))

    spoken = "\n".join(
        element.text or ""
        for element in root.iter()
        if element.tag.rsplit("}", 1)[-1] == "text"
    )
    if not spoken.strip():
        problems.append(
            f"{_ARCHITECTURE_SVG}: holds no <text>; a diagram of outlined paths is "
            "neither searchable nor diffable"
        )
    problems.extend(
        f"{_ARCHITECTURE_SVG}: never says {label!r}"
        for label in _SVG_REQUIRED_LABELS
        if label not in spoken
    )
    return problems


def test_the_committed_picture_is_hand_authored_legible_text() -> None:
    assert _svg_problems(_committed(_ARCHITECTURE_SVG)) == []


@pytest.mark.parametrize(
    ("original", "planted"),
    [
        ('<rect class="backdrop"', '<image href="shot.png" class="backdrop"'),
        ("<defs>", '<foreignObject width="1" height="1"/><defs>'),
        ("--ink: #1f2b36;", "--ink: #000000;"),
        ("--card: #f8fafb;", "--card: white;"),
        (_DARK_THEME_BLOCK, "@media (min-width: 900px)"),
        ("ui-sans-serif", "url(https://fonts.example/f.woff2), ui-sans-serif"),
        (">frontend/<", ">the web app<"),
        # The leading ">" keeps these off the <desc>, whose copy of the same
        # words is not what a reader of the picture sees.
        (">Arrows are data flow;", ">Boxes and lines,"),
        (">Agents must not<", ">Nothing may<"),
    ],
)
def test_a_perturbed_picture_is_rejected(original: str, planted: str) -> None:
    """One defect at a time, each of which has to make the pin fire."""

    committed = _committed(_ARCHITECTURE_SVG)
    perturbed = committed.replace(original, planted, 1)
    assert perturbed != committed, original
    assert _svg_problems(perturbed), planted


def test_an_oversized_picture_is_rejected() -> None:
    bloated = _committed(_ARCHITECTURE_SVG).replace(
        "</svg>", f"<!-- {'p' * _SVG_BYTE_CEILING} -->\n</svg>", 1
    )
    assert any("over the" in problem for problem in _svg_problems(bloated))


def test_an_unparseable_picture_is_rejected() -> None:
    problems = _svg_problems("<svg><rect></svg>")
    assert problems and "does not parse" in problems[0]


def test_a_low_contrast_palette_is_rejected() -> None:
    """The legibility gate measures contrast, not the absence of the extremes."""

    washed_out = _committed(_ARCHITECTURE_SVG).replace(
        "--muted: #485560;", "--muted: #e6eaee;", 1
    )
    problems = _svg_problems(washed_out)
    assert any("under the 4.5:1 floor" in problem for problem in problems), problems
    assert all("pure black" not in problem for problem in problems), problems


def test_an_ink_that_only_fails_composited_is_rejected() -> None:
    """The ground is the composite, not the declared backdrop.

    `#a8452a` clears the floor against the declared `#eef1f5` and falls under it
    once the 90%-opaque backdrop is composited over a dark page — the exact hole
    a check that read the declared colour could not see.
    """

    flat_only = _committed(_ARCHITECTURE_SVG).replace(
        "--fire: #973b21;", "--fire: #a8452a;", 1
    )
    assert _contrast_ratio("#a8452a", "#eef1f5") >= _CONTRAST_FLOOR
    problems = _svg_problems(flat_only)
    assert any("over a dark page" in problem for problem in problems), problems


def test_an_opaque_backdrop_is_rejected() -> None:
    """An opaque light card over a dark page is the failure mode being avoided."""

    painted_flat = _committed(_ARCHITECTURE_SVG).replace(
        'fill-opacity="0.9"', 'fill-opacity="1"', 1
    )
    problems = _svg_problems(painted_flat)
    assert any("backdrop is opaque" in problem for problem in problems), problems


def test_a_text_class_repointed_at_its_own_ground_is_rejected() -> None:
    """The ink of a class is read from the stylesheet, never assumed.

    An ordinary-looking style edit — `.body` inking with the card colour it is
    painted on — renders every card label invisible while changing no palette
    value, so a checker holding hard-coded pairs would see nothing.
    """

    invisible = _committed(_ARCHITECTURE_SVG).replace(
        ".body { fill: var(--muted);", ".body { fill: var(--card);", 1
    )
    problems = _svg_problems(invisible)
    assert any(".body (--card)" in problem for problem in problems), problems


def test_a_text_class_missing_from_the_ground_table_is_rejected() -> None:
    """A class nothing accounts for cannot be reported as legible."""

    renamed = _committed(_ARCHITECTURE_SVG).replace(
        '<text class="legend"', '<text class="footnote"', 1
    )
    problems = _svg_problems(renamed)
    assert any("ground table" in problem for problem in problems), problems
