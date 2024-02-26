import pytest
from opentool.function.parsers.list_parser import ListParser
from opentool.function.parsers.int_parser import IntParser
from opentool.function.func import BrokenSchemaError


@pytest.fixture
def list_parser():
    return ListParser(argtype=list[int], rec_parsers=[IntParser])


def test_parses_list_of_int_values(list_parser):
    assert list_parser.parse_value([1, 2, 3]) == [1, 2, 3]
    assert list_parser.parse_value([]) == []
    assert list_parser.parse_value([0, -1, 100]) == [0, -1, 100]


def test_raises_error_on_non_list_input(list_parser):
    with pytest.raises(BrokenSchemaError):
        list_parser.parse_value(True)
    with pytest.raises(BrokenSchemaError):
        list_parser.parse_value(123)
    with pytest.raises(BrokenSchemaError):
        list_parser.parse_value("not a list")
    with pytest.raises(BrokenSchemaError):
        list_parser.parse_value(None)
    with pytest.raises(BrokenSchemaError):
        list_parser.parse_value({})


def test_raises_error_on_invalid_list_elements(list_parser):
    with pytest.raises(BrokenSchemaError):
        list_parser.parse_value([1, "two", 3])
    with pytest.raises(BrokenSchemaError):
        list_parser.parse_value([1, 2.5, 3])
    with pytest.raises(BrokenSchemaError):
        list_parser.parse_value([1, [2], 3])
