"""Role-neutral persona bank + deterministic assignment tests (Task 16.9).

These pin the pure-function contract of :mod:`orchestrator.personas` — a
deterministic, without-replacement, role-NEUTRAL persona assignment — and the
inert :func:`orchestrator.game._build_participants` fill that nothing renders
until Task 16.16. The golden pins follow the ``tests/orchestrator/test_seeder``
style (plain functions, explanatory docstrings, ``pytest.raises(match=...)``);
the role-neutrality sweep (:func:`test_role_neutrality_sweep_9p2i` /
``_4p1i``) is the load-bearing extension of the leak suite.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

import pytest

from engine.entities import PlayerId, Role
from engine.world import WorldState, load_canonical_map
from meetings.manager import SuspicionEntry
from meetings.schemas import VentWitnessRecord
from orchestrator.game import _build_participants  # noqa: PLC2701
from orchestrator.personas import (
    PERSONA_BANK_MIN_SIZE,
    PersonaCard,
    assign_personas,
    load_persona_bank,
)
from orchestrator.seeder import seed_initial_state

# The committed seed range. seeds 0..49 are the replayed sample sets under
# ``replays/samples/9p2i`` and ``replays/samples/4p1i``; the sweeps below cover
# exactly this range so a regression trips against the committed corpus.
COMMITTED_SEEDS = range(50)

# The committed role-neutral roster ids (mirrors seeder's fixed p-1 … p-N).
_ROSTER_9: tuple[PlayerId, ...] = tuple(f"p-{i}" for i in range(1, 10))
_ROSTER_4: tuple[PlayerId, ...] = tuple(f"p-{i}" for i in range(1, 5))

# The committed bank size. This is a DELIBERATE pin (updated only when a card
# is intentionally added/removed), distinct from the floor assertion below.
COMMITTED_BANK_SIZE = 14

# Role/mechanic vocabulary a reviewed persona card must never contain. The
# first three mirror ``eval/leak_test.py._FORBIDDEN_VALUE_SUBSTRINGS`` (the
# packet role-value scanner); the rest pin the cards to diction/disposition
# only — no game action, object, or team identity may leak into a voice.
_FORBIDDEN_TEXT_SUBSTRINGS: tuple[str, ...] = (
    "impostor",
    "crewmate",
    "crew",
    "kill",
    "vent",
    "murder",
    "eject",
    "sabot",
    "body",
    "corpse",
    "guilt",
    "innocen",
    "role",
    "task",
    "suspect",
)


def _assert_bank_text_role_neutral(text: str) -> None:
    """Fail loud if any forbidden role/mechanic substring appears in ``text``.

    Factored out so :func:`test_persona_bank_text_is_role_neutral` can run it
    over the committed JSON and :func:`test_role_neutral_scanner_bites` can
    prove it still bites on a planted leak. Case-insensitive: a leak is a leak
    regardless of casing.
    """

    lowered = text.lower()
    for forbidden in _FORBIDDEN_TEXT_SUBSTRINGS:
        assert forbidden not in lowered, (
            f"forbidden role/mechanic substring {forbidden!r} in persona text"
        )


def _card_dict(index: int) -> dict[str, object]:
    """A synthetic, role-neutral card dict for building tmp banks."""

    return {
        "id": f"synthetic-{index:02d}",
        "disposition": f"A synthetic voice number {index}.",
        "diction": [f"note a for {index}", f"note b for {index}"],
    }


def _synthetic_card(index: int) -> PersonaCard:
    return PersonaCard.model_validate(_card_dict(index))


def _write_bank(path: Path, cards: list[dict[str, object]]) -> Path:
    path.write_text(json.dumps(cards), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# 1. Determinism
# --------------------------------------------------------------------------- #


def test_assign_personas_is_deterministic_across_committed_seeds() -> None:
    """Two calls at the same seed return byte-identical mappings.

    Swept over every committed seed for both the 9-seat and the 4-seat roster:
    assignment is a pure function of ``(seed, roster)``, so repeated calls must
    never diverge (no hidden global rng state, no clock, no set-iteration
    order leaking in).
    """

    for roster in (_ROSTER_9, _ROSTER_4):
        for seed in COMMITTED_SEEDS:
            first = assign_personas(seed=seed, roster=roster)
            second = assign_personas(seed=seed, roster=roster)
            assert first == second


# --------------------------------------------------------------------------- #
# 2. Golden pins
# --------------------------------------------------------------------------- #


def test_assign_personas_seed0_seed42_golden_9p() -> None:
    """Pin the EXACT {player_id: card_id} mapping for seed 0 and seed 42 (9p).

    Like the ``test_seeder`` pinned permutations, this fixes the pure function
    of ``(seed, roster)`` end to end: an accidental reorder of the committed
    bank, a change to ``_PERSONA_SEED_NAMESPACE``, or a shuffle-algorithm swap
    all move these ids and trip this test loudly. Card ids (not the mutable
    text) are pinned so wording edits to a card stay free.
    """

    seed0 = {
        pid: card.id for pid, card in assign_personas(seed=0, roster=_ROSTER_9).items()
    }
    assert seed0 == {
        "p-1": "aggressive-accuser",
        "p-2": "peacemaker-mediator",
        "p-3": "methodical-analyst",
        "p-4": "contrarian",
        "p-5": "anxious-rambler",
        "p-6": "cautious-hedger",
        "p-7": "quiet-observer",
        "p-8": "skeptic",
        "p-9": "rapid-fire-interrogator",
    }

    seed42 = {
        pid: card.id for pid, card in assign_personas(seed=42, roster=_ROSTER_9).items()
    }
    assert seed42 == {
        "p-1": "aggressive-accuser",
        "p-2": "skeptic",
        "p-3": "courteous-formalist",
        "p-4": "rapid-fire-interrogator",
        "p-5": "blunt-minimalist",
        "p-6": "quiet-observer",
        "p-7": "folksy-proverb-user",
        "p-8": "jokester",
        "p-9": "anxious-rambler",
    }


# --------------------------------------------------------------------------- #
# 3. Without replacement
# --------------------------------------------------------------------------- #


def test_assign_personas_never_repeats_a_card_within_a_game() -> None:
    """No two seats in one game share a card id, for every committed seed.

    Sampling WITHOUT replacement is the whole point of the single-permutation
    design (vs the rejected per-seat hash, which collides). The distinct-count
    equals the roster size for both roster shapes across the full sweep.
    """

    for roster in (_ROSTER_9, _ROSTER_4):
        for seed in COMMITTED_SEEDS:
            cards = assign_personas(seed=seed, roster=roster)
            card_ids = [card.id for card in cards.values()]
            assert len(set(card_ids)) == len(roster)


# --------------------------------------------------------------------------- #
# 4. Full-bank coverage + composition variance
# --------------------------------------------------------------------------- #


def test_bank_is_fully_covered_and_composition_varies_9p() -> None:
    """With 14 cards and 9 seats, the committed sweep (a) touches every card and
    (b) draws at least two DIFFERENT 9-card subsets.

    This is the twelve-plus rationale from the task contract made mechanical:
    at exactly nine cards only seat ORDER could vary; at fourteen the bank
    COMPOSITION varies game-to-game (each 9p game seats a different nine of the
    fourteen), which is what makes the cast feel game-specific.
    """

    assigned_ids: set[str] = set()
    subsets: set[frozenset[str]] = set()
    for seed in COMMITTED_SEEDS:
        cards = assign_personas(seed=seed, roster=_ROSTER_9)
        subset = frozenset(card.id for card in cards.values())
        assigned_ids |= subset
        subsets.add(subset)

    committed_ids = {card.id for card in load_persona_bank()}
    assert assigned_ids == committed_ids  # every one of the 14 cards appears
    assert len(subsets) >= 2  # composition varies across games


# --------------------------------------------------------------------------- #
# 5. Bank-size floor
# --------------------------------------------------------------------------- #


def test_persona_bank_min_size_is_twelve() -> None:
    assert PERSONA_BANK_MIN_SIZE == 12


def test_committed_bank_meets_floor_and_pins_size() -> None:
    """The committed bank clears the floor, and its exact size is pinned.

    The floor assertion is the invariant; the exact ``== 14`` is the separate
    deliberate pin (a card added or removed must edit this line consciously).
    """

    bank = load_persona_bank()
    assert len(bank) >= PERSONA_BANK_MIN_SIZE
    assert len(bank) == COMMITTED_BANK_SIZE


def test_load_persona_bank_rejects_below_floor(tmp_path: Path) -> None:
    """An 11-card file is below the committed floor and fails loud."""

    path = _write_bank(tmp_path / "eleven.json", [_card_dict(i) for i in range(11)])
    with pytest.raises(ValueError, match="below the committed floor"):
        load_persona_bank(path)


def test_load_persona_bank_rejects_duplicate_ids(tmp_path: Path) -> None:
    """A duplicate card id fails loud even in a bank that clears the floor."""

    cards = [_card_dict(i) for i in range(13)]
    cards.append(_card_dict(0))  # re-introduce synthetic-00's id
    path = _write_bank(tmp_path / "dup.json", cards)
    with pytest.raises(ValueError, match="duplicate card ids"):
        load_persona_bank(path)


# --------------------------------------------------------------------------- #
# 6. assign_personas fail-loud
# --------------------------------------------------------------------------- #


def test_assign_personas_rejects_empty_roster() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        assign_personas(seed=0, roster=())


def test_assign_personas_rejects_duplicate_roster_ids() -> None:
    with pytest.raises(ValueError, match="duplicate player ids"):
        assign_personas(seed=0, roster=("p-1", "p-2", "p-1"))


def test_assign_personas_rejects_roster_larger_than_bank() -> None:
    """A 15-seat roster over the 14-card bank fails loud, naming both sizes."""

    roster = tuple(f"p-{i}" for i in range(1, 16))
    with pytest.raises(ValueError, match=r"15 seats exceeds persona bank of 14"):
        assign_personas(seed=0, roster=roster)


def test_assign_personas_rejects_caller_bank_below_floor() -> None:
    """A caller-supplied under-floor bank takes the SAME validation path."""

    under_floor = tuple(_synthetic_card(i) for i in range(11))
    with pytest.raises(ValueError, match="below the committed floor"):
        assign_personas(seed=0, roster=_ROSTER_4, bank=under_floor)


# --------------------------------------------------------------------------- #
# 7. Role-neutrality sweep (the load-bearing leak-suite extension)
# --------------------------------------------------------------------------- #


_AssignFn = Callable[
    [int, tuple[PlayerId, ...], WorldState], Mapping[PlayerId, PersonaCard]
]


def _committed_assign(
    seed: int, roster: tuple[PlayerId, ...], state: WorldState
) -> Mapping[PlayerId, PersonaCard]:
    """The real assignment under test; ``state`` (and so roles) deliberately unused."""

    return assign_personas(seed=seed, roster=roster)


def _chi2_persona_role_independence(
    *,
    num_players: int,
    num_impostors: int,
    chance_rate: float,
    assign: _AssignFn = _committed_assign,
) -> tuple[int, int, float, float, dict[str, tuple[int, int]]]:
    """Sweep the committed seeds and measure persona↔impostorhood independence.

    For each seed the seeder assigns roles and ``assign`` assigns cards over
    the same fixed roster (both pure functions of the seed). We accumulate,
    per card id ``k``: ``n_k`` = games the card was seated and ``x_k`` = of
    those, how many landed on an impostor. Under the null hypothesis (persona
    independent of role, which holds BY CONSTRUCTION for the real assignment —
    roles never enter the persona module) each seated card is impostor with
    probability ``chance_rate`` = num_impostors / num_players.

    ``assign`` defaults to the real :func:`assign_personas`; the planted-leak
    test swaps in a role-COUPLED assigner to prove the chi-square gate can
    fail (a gate that cannot fail is not a gate).

    Returns (total_appearances, total_impostor_slots, chi2, worst_abs_dev,
    per_card_counts) so the caller can pin the sanity totals and the thresholds.
    """

    game_map = load_canonical_map()
    n_counts: Counter[str] = Counter()
    x_counts: Counter[str] = Counter()
    total_app = 0
    total_imp = 0
    for seed in COMMITTED_SEEDS:
        state = seed_initial_state(
            seed=seed,
            game_map=game_map,
            num_players=num_players,
            num_impostors=num_impostors,
        )
        roster = tuple(sorted(state.players))
        cards = assign(seed, roster, state)
        for player_id, card in cards.items():
            n_counts[card.id] += 1
            total_app += 1
            if state.players[player_id].role == "IMPOSTOR":
                x_counts[card.id] += 1
                total_imp += 1

    chi2 = 0.0
    worst_dev = 0.0
    per_card: dict[str, tuple[int, int]] = {}
    for card_id, n_k in n_counts.items():
        x_k = x_counts[card_id]
        per_card[card_id] = (n_k, x_k)
        expected_imp = n_k * chance_rate
        expected_crew = n_k * (1.0 - chance_rate)
        chi2 += (x_k - expected_imp) ** 2 / expected_imp
        chi2 += ((n_k - x_k) - expected_crew) ** 2 / expected_crew
        worst_dev = max(worst_dev, abs(x_k / n_k - chance_rate))
    return total_app, total_imp, chi2, worst_dev, per_card


# alpha=0.001 chi-square critical value for df = 14 cards - 1 = 13. The sweep
# certifies the definition-of-done property — persona↔role association at
# chance level over the committed corpus — and has power against GROSS
# coupling: an assignment computed FROM roles blows past this by an order of
# magnitude (the planted-leak test below proves the gate can fail). It has NO
# power against subtle derivation changes — the measured un-offset-namespace
# variant lands at chi² ≈ 20.9 (9p2i) / 13.1 (4p1i), inside the null band —
# so the seed-0/seed-42 golden pins above, not this sweep, are the
# derivation guard.
_CHI2_CRITICAL_DF13 = 34.53
# A wide, documented per-card band: even if the aggregate chi2 were diluted, a
# single card correlated with role would breach this.
_PER_CARD_DEV_BAND = 0.30


def test_role_neutrality_sweep_9p2i() -> None:
    """Persona assignment is statistically independent of role over 9p2i.

    The load-bearing role-neutrality guard. Chance impostor rate is p = 2/9.
    Sanity: 50 seeds x 9 seats = 450 appearances, 50 x 2 = 100 impostor slots.
    """

    total_app, total_imp, chi2, worst_dev, _ = _chi2_persona_role_independence(
        num_players=9, num_impostors=2, chance_rate=2.0 / 9.0
    )
    assert total_app == 450
    assert total_imp == 100
    assert chi2 < _CHI2_CRITICAL_DF13
    assert worst_dev <= _PER_CARD_DEV_BAND


def test_role_neutrality_sweep_4p1i() -> None:
    """Persona assignment is statistically independent of role over 4p1i.

    Same guard on the 4-player sample set. Chance impostor rate is p = 1/4.
    Sanity: 50 seeds x 4 seats = 200 appearances, 50 x 1 = 50 impostor slots.
    The df is still 13 (14-card bank), so the same critical value applies.
    """

    total_app, total_imp, chi2, worst_dev, _ = _chi2_persona_role_independence(
        num_players=4, num_impostors=1, chance_rate=1.0 / 4.0
    )
    assert total_app == 200
    assert total_imp == 50
    assert chi2 < _CHI2_CRITICAL_DF13
    assert worst_dev <= _PER_CARD_DEV_BAND


def test_role_neutrality_sweep_bites_on_role_coupled_assignment() -> None:
    """The sweep gate can fail: a role-COUPLED assignment blows past both
    thresholds (the leak-suite planted-leak pattern, applied to the statistic).

    The planted assigner hands the lexicographically first bank cards to the
    impostors every game — the gross persona→role coupling class this sweep
    guards against. The impostor-held cards are then impostor 100% of the time
    (per-card deviation 1 - 2/9 ≈ 0.78, chi² in the hundreds), so both the
    chi-square threshold and the per-card band trip. This proves the
    role-neutrality assertions are a live gate, not a tautology over whatever
    the implementation happens to produce.
    """

    bank = sorted(load_persona_bank(), key=lambda card: card.id)

    def role_leaking_assign(
        seed: int, roster: tuple[PlayerId, ...], state: WorldState
    ) -> Mapping[PlayerId, PersonaCard]:
        impostors = [p for p in roster if state.players[p].role == "IMPOSTOR"]
        others = [p for p in roster if state.players[p].role != "IMPOSTOR"]
        return {pid: bank[i] for i, pid in enumerate(impostors + others)}

    _, _, chi2, worst_dev, _ = _chi2_persona_role_independence(
        num_players=9,
        num_impostors=2,
        chance_rate=2.0 / 9.0,
        assign=role_leaking_assign,
    )
    assert chi2 > _CHI2_CRITICAL_DF13
    assert worst_dev > _PER_CARD_DEV_BAND


# --------------------------------------------------------------------------- #
# 8. Role-suggestive text scan (the reviewed-field guard)
# --------------------------------------------------------------------------- #


def test_persona_bank_text_is_role_neutral() -> None:
    """The committed JSON carries no role/mechanic vocabulary, and every card is
    structurally well-formed (2 non-empty diction notes, non-empty scalars)."""

    raw = (Path(__file__).resolve().parents[2] / "data" / "personas.json").read_text(
        encoding="utf-8"
    )
    _assert_bank_text_role_neutral(raw)

    for card in load_persona_bank():
        assert card.id
        assert card.disposition
        assert len(card.diction) == 2
        for note in card.diction:
            assert note


# --------------------------------------------------------------------------- #
# 9. The scanner bites (leak_test planted-leak pattern)
# --------------------------------------------------------------------------- #


def test_role_neutral_scanner_bites() -> None:
    """The reviewed-field scanner still bites: a planted card text carrying
    ``impostor`` must trip ``_assert_bank_text_role_neutral``. Real cards never
    do this; it is planted here exactly like the leak_test planted-leak tests."""

    poisoned = "A calm voice. Names the impostor outright. Speaks briefly."
    with pytest.raises(AssertionError, match="impostor"):
        _assert_bank_text_role_neutral(poisoned)


# --------------------------------------------------------------------------- #
# 10. PersonaCard.text
# --------------------------------------------------------------------------- #


def test_persona_card_text_joins_disposition_and_diction() -> None:
    """``.text`` is ``disposition + ' ' + diction[0] + ' ' + diction[1]``."""

    card = PersonaCard.model_validate(
        {
            "id": "hand-built",
            "disposition": "A test disposition.",
            "diction": ["first note.", "second note."],
        }
    )
    assert card.text == "A test disposition. first note. second note."


def test_every_committed_card_text_is_non_empty() -> None:
    for card in load_persona_bank():
        assert card.text


# --------------------------------------------------------------------------- #
# 11. The _build_participants fill (integration)
# --------------------------------------------------------------------------- #


@dataclass
class _MeetingAwareStub:
    """Minimal ``MeetingAwareAgent`` for participant construction — it only
    needs to render a role-bearing memory string and empty graphs."""

    _agent_id: PlayerId
    _role: Role

    @property
    def agent_id(self) -> PlayerId:
        return self._agent_id

    @property
    def role(self) -> Role:
        return self._role

    def render_memory_for_meeting(
        self,
        *,
        token_budget: int = 1500,
        suspicion_override: Mapping[PlayerId, float] | None = None,
    ) -> str:
        return f"## Your role: {self._role}\nmemory for {self._agent_id}"

    def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]:
        return ()

    def vent_witness_records_for_meeting(self) -> tuple[VentWitnessRecord, ...]:
        return ()


def test_build_participants_fills_persona_from_deterministic_bank() -> None:
    """The wiring guard: ``_build_participants`` fills ``persona`` from the
    deterministic bank, keyed by the game seed and full roster.

    Each living participant's ``persona`` equals the committed-bank card text
    for its seat under ``assign_personas(seed=state.seed, roster=sorted ids)``,
    and is non-empty. Nothing renders this field until Task 16.16 (the Task
    16.3 byte-golden proves rendered prompt bytes are unchanged); this test is
    only the fill-plumbing check.
    """

    state = seed_initial_state(seed=7, game_map=load_canonical_map(), num_players=4)
    agents: dict[PlayerId, object] = {
        pid: _MeetingAwareStub(_agent_id=pid, _role=player.role)
        for pid, player in state.players.items()
    }
    participants = _build_participants(
        state=state,
        agents=agents,  # type: ignore[arg-type]
        token_budget=1500,
    )

    expected = assign_personas(seed=state.seed, roster=tuple(sorted(state.players)))
    assert participants  # non-empty roster produced participants
    for participant in participants:
        assert participant.persona == expected[participant.agent_id].text
        assert participant.persona
