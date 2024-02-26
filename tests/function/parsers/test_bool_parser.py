import pytest
from opentool.function.parsers.bool_parser import BoolParser
from opentool.function.func import BrokenSchemaError


@pytest.fixture
def bool_parser():
    return BoolParser(argtype=bool, rec_parsers=[])


def test_parses_boolean_values(bool_parser):
    values = [True, False]
    for value in values:
        assert bool_parser.parse_value(value) is value


def test_raises_error_on_invalid_input(bool_parser):
    non_boolean_values = [
        1,
        0,
        "true",
        "false",
        "True",
        "False",
        "1",
        "0",
        "not a boolean",
        "yes",
        "no",
        2,
        -1,
        [],
    ]
    for value in non_boolean_values:
        with pytest.raises(BrokenSchemaError):
            bool_parser.parse_value(value)
