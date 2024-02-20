import pytest
from agent_tools.function.parsers.float_parser import FloatParser
from agent_tools.function.func import BrokenSchemaError

@pytest.fixture
def float_parser():
    return FloatParser(argtype=float, rec_parsers=[])

def test_parses_float_values(float_parser):
    assert float_parser.parse_value(1.0) == 1.0
    assert float_parser.parse_value(0.0) == 0.0
    assert float_parser.parse_value(-1.23) == -1.23

def test_parses_int_as_float(float_parser):
    assert float_parser.parse_value(1) == 1.0
    assert float_parser.parse_value(0) == 0.0
    assert float_parser.parse_value(-1) == -1.0

def test_raises_error_on_invalid_input(float_parser):
    with pytest.raises(BrokenSchemaError):
        float_parser.parse_value("not a float")
    with pytest.raises(BrokenSchemaError):
        float_parser.parse_value(None)
    with pytest.raises(BrokenSchemaError):
        float_parser.parse_value([])
    with pytest.raises(BrokenSchemaError):
        float_parser.parse_value({})

# Additional tests can be added to cover more cases or specific behaviors.