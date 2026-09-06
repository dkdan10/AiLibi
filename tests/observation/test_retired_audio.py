from __future__ import annotations

import pytest
from pydantic import ValidationError

from api.schemas import AudibleEventView
from observation.packet import AudibleEvent


@pytest.mark.parametrize("kind", ["vent_use_heard", "invented_alarm"])
def test_current_audio_schemas_refuse_unsupported_kinds(kind: str) -> None:
    payload = {"kind": kind, "room": "ADMIN"}
    for schema in (AudibleEvent, AudibleEventView):
        with pytest.raises(ValidationError, match="literal_error"):
            schema.model_validate(payload)


def test_alarm_survives_both_wire_boundaries() -> None:
    payload = {"kind": "sabotage_alarm", "room": None}
    packet_event = AudibleEvent.model_validate(payload)
    view = AudibleEventView.model_validate(packet_event.model_dump())
    assert view.model_dump() == payload
