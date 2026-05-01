import pytest


@pytest.mark.skip(reason="implemented in phase 1")
def test_no_observation_leaks_hidden_information() -> None:
    """TODO: implement the DESIGN.md §11.2 observation-leak assertion contract."""
    # Phase 1 should run a headless game with a packet-recording agent and
    # inspect only ObservationPacket/audit-log data, without importing engine
    # internals here. For every observed non-self player, packet fields must
    # omit hidden information such as role and kill attribution.
    pass
