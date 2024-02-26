import pytest
from dataclasses import dataclass
from opentool.function.parsers.dataclass_parser import DataclassParser
from opentool.function.parsers.int_parser import IntParser
from opentool.function.parsers.str_parser import StringParser
from opentool.function.parsers.bool_parser import BoolParser
from opentool.function.func import BrokenSchemaError


@dataclass
class DemoClass:
    id: int
    name: str
    active: bool


@pytest.fixture
def dataclass_parser():
    return DataclassParser(
        argtype=DemoClass, rec_parsers=[IntParser, StringParser, BoolParser]
    )


def test_parses_dataclass_correctly(dataclass_parser):
    input_data = {"id": 1, "name": "Test", "active": True}
    result = dataclass_parser.parse_value(input_data)
    assert isinstance(result, DemoClass)
    assert result.id == 1
    assert result.name == "Test"
    assert result.active is True


def test_raises_error_on_non_dict_input(dataclass_parser):
    with pytest.raises(BrokenSchemaError):
        dataclass_parser.parse_value([1, "Test", True])
    with pytest.raises(BrokenSchemaError):
        dataclass_parser.parse_value("not a dict")
    with pytest.raises(BrokenSchemaError):
        dataclass_parser.parse_value(None)


def test_raises_error_on_missing_required_fields(dataclass_parser):
    with pytest.raises(BrokenSchemaError):
        dataclass_parser.parse_value({"id": 1, "active": True})
    with pytest.raises(BrokenSchemaError):
        dataclass_parser.parse_value({"name": "Test", "active": True})


def test_raises_error_on_additional_fields(dataclass_parser):
    with pytest.raises(BrokenSchemaError):
        dataclass_parser.parse_value(
            {"id": 1, "name": "Test", "active": True, "extra": "field"}
        )


def test_raises_error_on_invalid_field_types(dataclass_parser):
    with pytest.raises(BrokenSchemaError):
        dataclass_parser.parse_value({"id": "one", "name": "Test", "active": True})
    with pytest.raises(BrokenSchemaError):
        dataclass_parser.parse_value({"id": 1, "name": 123, "active": "yes"})
