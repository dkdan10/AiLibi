"""Generated literal types preserve their JSON primitive type."""

from typing import Literal

from gen_frontend_types import _Generator


def test_numeric_contract_version_is_not_a_string_literal() -> None:
    generator = _Generator()
    assert generator._ts_type(Literal[1]) == "1"
    assert generator._ts_type(Literal["1"]) == '"1"'
    assert generator._ts_type(Literal[True, False]) == "true | false"
