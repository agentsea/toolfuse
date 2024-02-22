import pytest
from enum import Enum
from agent_tools.function.parsers.enum_parser import EnumParser
from agent_tools.function.parsers.int_parser import IntParser
from agent_tools.function.func import BrokenSchemaError


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


@pytest.fixture
def enum_parser():
    return EnumParser(argtype=Color, rec_parsers=[IntParser])


def test_parses_enum_correctly(enum_parser):
    assert enum_parser.parse_value("RED") == Color.RED
    assert enum_parser.parse_value("GREEN") == Color.GREEN
    assert enum_parser.parse_value("BLUE") == Color.BLUE


def test_raises_error_on_invalid_enum_value(enum_parser):
    with pytest.raises(BrokenSchemaError):
        enum_parser.parse_value("YELLOW")


def test_raises_error_on_non_string_input(enum_parser):
    with pytest.raises(BrokenSchemaError):
        enum_parser.parse_value(1)
    with pytest.raises(BrokenSchemaError):
        enum_parser.parse_value(None)
    with pytest.raises(BrokenSchemaError):
        enum_parser.parse_value(3.14)
    with pytest.raises(BrokenSchemaError):
        enum_parser.parse_value(["RED", "GREEN"])
