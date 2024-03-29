import pytest
from toolfuse.function.parsers.str_parser import StringParser
from toolfuse.function.func import BrokenSchemaError


@pytest.fixture
def str_parser():
    return StringParser(argtype=str, rec_parsers=[])


def test_parses_string_values(str_parser):
    assert str_parser.parse_value("test") == "test"
    assert str_parser.parse_value("") == ""


def test_raises_error_on_non_string_input(str_parser):
    non_string_values = [0, 1.0, False, True, [], {}]
    for value in non_string_values:
        with pytest.raises(BrokenSchemaError):
            str_parser.parse_value(value)
