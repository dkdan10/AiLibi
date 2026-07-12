"""Role-neutral persona bank + deterministic assignment (Task 16.9).

The Voice track (audit §4.1) gives each seat a distinct *voice* so a
nine-seat game stops rendering as "one analyst times nine". This module
is that substrate: it loads the committed, role-neutral persona bank and
assigns one card per seat as a pure function of the game seed. It is inert
until Task 16.16 — the assigned text fills :attr:`MeetingParticipant.persona`
and no template reads it yet, so rendered prompt bytes are unchanged
(DESIGN.md §1.4 determinism discipline; DESIGN.md §5.1 meeting inputs; the
Task 16.3 golden proves the byte-identity).

Assignment samples WITHOUT replacement: a single seeded permutation of the
sorted bank (a Fisher–Yates shuffle keyed by the game seed), with seat ``i``
taking the ``i``-th shuffled card. This guarantees (a) reproducibility — a
replay reconstructs the same voices — and (b) disjointness: no persona
repeats within a game. The naive alternative ``bank[hash(seed, seat) %
len(bank)]`` (independent per-seat hashing) is explicitly REJECTED: its
per-seat hashes collide (the birthday problem), handing two seats the same
persona and re-introducing the very homogeneity personas exist to break
(audits/post-phase-14-Voice-and-Judgment-planning.md §4.1).

Role-neutrality is guaranteed two ways. By construction: assignment is a
pure function of ``(seed, roster)`` computed with no reference to roles —
roles never enter this module, so a card cannot encode or correlate with
one. By test: the committed-seed sweep in
``tests/orchestrator/test_personas.py`` pins the assignment and scans the
bank's reviewed fields for role/mechanic vocabulary.

Assignment is over the FULL fixed roster (dead seats included), mirroring
:func:`orchestrator.seeder.seed_initial_state`'s fixed ``p-1 … p-N`` ids, so
a player's persona is stable across every meeting of a game regardless of
deaths — the ``i``-th sorted player id always draws the ``i``-th shuffled
card whether or not that player is still alive.
"""

from __future__ import annotations

import random
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator

from engine.entities import PlayerId

PERSONA_BANK_MIN_SIZE: Final[int] = 12
"""Committed floor on bank size.

At exactly nine cards every 9p2i game would seat the whole bank and only
seat ORDER would vary game-to-game; at twelve-plus the bank COMPOSITION
varies too (each game draws a different nine of the fourteen committed
cards), which is what makes the voices feel game-specific rather than a
fixed cast reshuffled.
"""

# ASCII "PERSONA" as a fixed namespace offset for the persona rng seed.
#
# Load-bearing, two reasons:
#   (a) The persona stream must never share or perturb the seeder's
#       ``random.Random(seed)`` draws — replay byte-identity depends on the
#       seeder stream staying untouched. A fresh ``Random`` instance already
#       guarantees that on its own (separate PRNG object, separate state).
#   (b) An UN-offset ``random.Random(seed)`` would seed the persona
#       Fisher–Yates with the exact integer the seeder feeds its
#       role-assignment shuffle. On the committed seed range that happens to
#       decorrelate anyway — the role shuffle permutes a 4/9-element list,
#       the bank shuffle a 14-element one, and the measured association stays
#       at chance level (chi² ≈ 20.9 on the 9p2i sweep, inside the null
#       band) — but that is an accident of list lengths and the generator,
#       not a property the design may lean on. The offset makes the
#       decorrelation BY CONSTRUCTION, and the seed-0/seed-42 golden pins in
#       ``tests/orchestrator/test_personas.py`` fix the derivation so
#       removing the offset trips loudly THERE: the chi-square sweep has no
#       power against so subtle a change (it exists to catch gross
#       persona↔role coupling, which its planted-leak test proves it does).
_PERSONA_SEED_NAMESPACE: Final[int] = 0x504552534F4E41

_PERSONA_BANK_PATH: Final[Path] = (
    Path(__file__).resolve().parent.parent / "data" / "personas.json"
)


class PersonaCard(BaseModel):
    """One role-neutral voice: a temperament plus two speech-style notes.

    Every field names ONLY how the character talks and carries themself —
    tone, sentence length, hedging, humor, formality, questioning style,
    vocabulary register. A card never names a game action, mechanic, or
    team/role identity; that neutrality is the reviewed contract the
    committed-seed sweep enforces (audit §4.1).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    """Kebab-case card id, unique within the bank."""

    disposition: str = Field(min_length=1)
    """One sentence naming the temperament."""

    diction: tuple[str, str]
    """Exactly two speech-style notes, each non-empty."""

    @field_validator("diction")
    @classmethod
    def _validate_diction(cls, value: tuple[str, str]) -> tuple[str, str]:
        # tuple[str, str] already fixes the arity at two; the field validator
        # adds the per-entry non-empty guard that Field(min_length=1) gives the
        # scalar strings (fail-loud: a blank note is a malformed card, not a
        # silently-tolerated one).
        for index, note in enumerate(value):
            if not note:
                raise ValueError(f"diction note {index} must be non-empty")
        return value

    @property
    def text(self) -> str:
        """Canonical inert persona text written into ``MeetingParticipant.persona``.

        Task 16.16 refines this card TEXT into the full prompt preamble; the
        card STRUCTURE (disposition + two diction notes) is frozen here, and
        this join is the deterministic string the orchestrator fills today.
        """

        return " ".join((self.disposition, *self.diction))


# Module-level adapter is immutable (a compiled validator, not mutable global
# state), so it is safe to hoist per AGENTS.md "no global state".
_BANK_ADAPTER: Final[TypeAdapter[tuple[PersonaCard, ...]]] = TypeAdapter(
    tuple[PersonaCard, ...]
)


def _validate_bank(bank: Sequence[PersonaCard]) -> None:
    """Enforce the bank invariants shared by both assignment paths.

    Fail-loud (AGENTS.md "no silent fallbacks"): a bank below the committed
    floor or carrying duplicate ids is rejected, whether it came from the
    committed file or was supplied by a caller.
    """

    if len(bank) < PERSONA_BANK_MIN_SIZE:
        raise ValueError(
            f"persona bank has {len(bank)} cards, below the committed floor "
            f"of {PERSONA_BANK_MIN_SIZE}"
        )
    counts = Counter(card.id for card in bank)
    duplicates = sorted(card_id for card_id, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError(f"persona bank has duplicate card ids: {duplicates}")


def load_persona_bank(path: Path | None = None) -> tuple[PersonaCard, ...]:
    """Load and validate the committed persona bank.

    ``path`` of ``None`` loads the committed bank at :data:`_PERSONA_BANK_PATH`.
    A missing file raises :class:`FileNotFoundError` (fail-loud, mirroring
    ``engine.world._load_map_yaml``). The bank is parsed with a pydantic
    :class:`TypeAdapter` and then checked against the shared bank invariants
    (size floor + unique ids).
    """

    bank_path = _PERSONA_BANK_PATH if path is None else path
    if not bank_path.exists():
        raise FileNotFoundError(bank_path)
    bank = _BANK_ADAPTER.validate_json(bank_path.read_text(encoding="utf-8"))
    _validate_bank(bank)
    return bank


def assign_personas(
    *,
    seed: int,
    roster: Sequence[PlayerId],
    bank: Sequence[PersonaCard] | None = None,
) -> dict[PlayerId, PersonaCard]:
    """Assign one distinct persona per seat, deterministically per seed.

    ``bank`` of ``None`` loads the committed bank via :func:`load_persona_bank`;
    a caller-supplied bank passes the SAME validations (size floor + unique
    ids) through the shared :func:`_validate_bank` helper — no path skips them.

    Sampling is WITHOUT replacement via one seeded permutation: a single
    ``random.Random(seed + _PERSONA_SEED_NAMESPACE)`` shuffles a sorted COPY of
    the bank (never the caller's sequence), then seat ``i`` — the ``i``-th
    sorted roster id — takes the ``i``-th shuffled card. Cards past
    ``len(roster)`` are unused this game. Because the roster is the FULL fixed
    roster (dead seats included), a player's card is stable across every
    meeting of the game.

    Fail-loud (AGENTS.md "no silent fallbacks"): an empty roster, a roster with
    duplicate ids, or a roster larger than the bank each raises — without
    replacement needs one distinct card per seat.
    """

    resolved_bank = load_persona_bank() if bank is None else tuple(bank)
    _validate_bank(resolved_bank)

    if not roster:
        raise ValueError("roster must be non-empty")
    roster_counts = Counter(roster)
    roster_duplicates = sorted(
        player_id for player_id, count in roster_counts.items() if count > 1
    )
    if roster_duplicates:
        raise ValueError(f"roster has duplicate player ids: {roster_duplicates}")
    if len(roster) > len(resolved_bank):
        raise ValueError(
            f"roster of {len(roster)} seats exceeds persona bank of "
            f"{len(resolved_bank)} cards: sampling without replacement needs one "
            "distinct card per seat"
        )

    # Mirror the seeder discipline exactly: ONE seeded rng, shuffle a sorted
    # COPY, deal by position. Sorting both the bank and the roster before the
    # shuffle makes the permutation a pure function of (seed, card ids, roster
    # ids), independent of input ordering.
    rng = random.Random(seed + _PERSONA_SEED_NAMESPACE)
    ordered = sorted(resolved_bank, key=lambda card: card.id)
    rng.shuffle(ordered)
    return dict(zip(sorted(roster), ordered, strict=False))


__all__ = [
    "PERSONA_BANK_MIN_SIZE",
    "PersonaCard",
    "assign_personas",
    "load_persona_bank",
]
