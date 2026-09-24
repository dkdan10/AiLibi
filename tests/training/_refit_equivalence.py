"""The refit-equivalence comparison both committed-fit pins share.

The ballot surrogate and the conviction model keep version-one fit records, so
their derivation is certified by measurement rather than by a source digest: a
refit by the committed recipe on the live fit-side rows must reproduce every
committed parameter. The fits are numpy full-batch gradient descent,
byte-identical on the host that produced them and equal to float ULP elsewhere,
so float-hex parameters compare at ``rel=1e-9, abs=1e-12`` and every other field
(format marker, feature names, epochs) compares exactly.
"""

from __future__ import annotations

import json

import pytest

_REL = 1e-9
_ABS = 1e-12


def _is_float_hex(value: object) -> bool:
    return isinstance(value, str) and value.startswith(("0x", "-0x"))


def assert_refit_reproduces_committed(refit_json: str, committed_json: str) -> None:
    """Raise ``AssertionError`` unless the refit reproduces the committed artifact.

    Both arguments are artifact JSON texts. The key sets must agree; a list whose
    first element is a float-hex string and a lone float-hex string compare to
    ULP tolerance; anything else compares exactly. The failing key is named.
    """

    refit = json.loads(refit_json)
    committed = json.loads(committed_json)
    assert refit.keys() == committed.keys()
    for key, committed_value in committed.items():
        refit_value = refit[key]
        if (
            isinstance(committed_value, list)
            and committed_value
            and _is_float_hex(committed_value[0])
        ):
            assert [float.fromhex(item) for item in refit_value] == pytest.approx(
                [float.fromhex(item) for item in committed_value], rel=_REL, abs=_ABS
            ), key
        elif _is_float_hex(committed_value):
            assert float.fromhex(refit_value) == pytest.approx(
                float.fromhex(committed_value), rel=_REL, abs=_ABS
            ), key
        else:
            assert refit_value == committed_value, f"artifact field {key!r} drifted"
