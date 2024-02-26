import pytest
from typing import Union
from opentool.function.parsers.union_parser import UnionParser
from opentool.function.parsers.int_parser import IntParser
from opentool.function.parsers.str_parser import StringParser
from opentool.function.func import BrokenSchemaError


@pytest.fixture
def union_parser():
    return UnionParser(argtype=Union[int, str], rec_parsers=[IntParser, StringParser])


def test_parses_union_of_int_and_str(union_parser):
    assert union_parser.parse_value(1) == 1
    assert union_parser.parse_value("test") == "test"


def test_raises_error_on_invalid_union_type(union_parser):
    with pytest.raises(BrokenSchemaError):
        union_parser.parse_value(1.5)
    with pytest.raises(BrokenSchemaError):
        union_parser.parse_value([])
    with pytest.raises(BrokenSchemaError):
        union_parser.parse_value({})
    with pytest.raises(BrokenSchemaError):
        union_parser.parse_value(None)


def test_raises_error_on_complex_union_type(union_parser):
    with pytest.raises(BrokenSchemaError):
        union_parser.parse_value([1, "two"])
    with pytest.raises(BrokenSchemaError):
        union_parser.parse_value({"key": "value"})
