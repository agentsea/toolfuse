import pytest
from agent_tools.function.parsers.dict_parser import DictParser
from agent_tools.function.parsers.int_parser import IntParser
from agent_tools.function.parsers.str_parser import StringParser
from agent_tools.function.func import BrokenSchemaError


@pytest.fixture
def dict_parser():
    return DictParser(argtype=dict[str, int], rec_parsers=[IntParser, StringParser])


def test_parses_dict_correctly(dict_parser):
    input_data = {"key1": 1, "key2": 2}
    result = dict_parser.parse_value(input_data)
    assert isinstance(result, dict)
    assert result == input_data


def test_raises_error_on_non_dict_input(dict_parser):
    with pytest.raises(BrokenSchemaError):
        dict_parser.parse_value([1, 2])
    with pytest.raises(BrokenSchemaError):
        dict_parser.parse_value("not a dict")
    with pytest.raises(BrokenSchemaError):
        dict_parser.parse_value(None)


def test_raises_error_on_invalid_dict_values(dict_parser):
    with pytest.raises(BrokenSchemaError):
        dict_parser.parse_value({"key1": "one", "key2": 2})
    with pytest.raises(BrokenSchemaError):
        dict_parser.parse_value({"key1": 1, "key2": "two"})


def test_raises_error_on_invalid_dict_keys(dict_parser):
    with pytest.raises(BrokenSchemaError):
        dict_parser.parse_value({1: "one", 2: "two"})
    with pytest.raises(BrokenSchemaError):
        dict_parser.parse_value({True: 1, False: 2})
