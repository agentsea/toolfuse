import pytest
from toolfuse.function.parsers.int_parser import IntParser
from toolfuse.function.func import BrokenSchemaError


@pytest.fixture
def int_parser():
    return IntParser(argtype=int, rec_parsers=[])


def test_parses_int_values(int_parser):
    assert int_parser.parse_value(1) == 1
    assert int_parser.parse_value(0) == 0
    assert int_parser.parse_value(-123) == -123


def test_raises_error_on_bool_input(int_parser):
    with pytest.raises(BrokenSchemaError):
        int_parser.parse_value(True)
    with pytest.raises(BrokenSchemaError):
        int_parser.parse_value(False)


def test_raises_error_on_invalid_input(int_parser):
    with pytest.raises(BrokenSchemaError):
        int_parser.parse_value("not an int")
    with pytest.raises(BrokenSchemaError):
        int_parser.parse_value(1.0)
    with pytest.raises(BrokenSchemaError):
        int_parser.parse_value(None)
    with pytest.raises(BrokenSchemaError):
        int_parser.parse_value([])
    with pytest.raises(BrokenSchemaError):
        int_parser.parse_value({})
