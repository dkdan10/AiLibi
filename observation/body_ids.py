"""Public body handles use only the already disclosed victim identity."""

from __future__ import annotations


def public_body_id(victim_id: str) -> str:
    """Return a stable handle without encoding a death tick or kill attribution."""

    if not victim_id:
        raise ValueError("a public body handle requires a victim identity")
    return f"body-{victim_id}"
