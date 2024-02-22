import pytest
import inspect
from collections import OrderedDict
from agent_tools.function.func import (
    FunctionWrapper,
    WrapperConfig,
    ArgSchemaParser,
    CannotParseTypeError,
    BrokenSchemaError,
)


def mock_function(a: str, b: int, c: str) -> str:
    return f"Result: {a}, {b}, {c}"


class MockArgSchemaParser(ArgSchemaParser):
    @classmethod
    def can_parse(cls, annotation):
        return True

    def parse_value(self, value):
        return value

    @property
    def argument_schema(self):
        return {"type": "string"}


def test_function_wrapper_initialization():
    wrapper = FunctionWrapper(func=mock_function)
    assert wrapper.func == mock_function
    assert isinstance(wrapper.config, WrapperConfig)


def test_function_wrapper_schema():
    wrapper = FunctionWrapper(func=mock_function)
    schema = wrapper.schema
    assert schema["name"] == "mock_function"
    assert "parameters" in schema


def test_parse_argument():
    wrapper = FunctionWrapper(func=mock_function)
    param = next(iter(inspect.signature(mock_function).parameters.values()))
    parser = wrapper.parse_argument(param)
    assert parser is not None


def test_parse_argument_unparseable():
    def function_with_unparseable_types(a, b: int, c: str = "default") -> str:
        return f"Result: {a}, {b}, {c}"

    wrapper = FunctionWrapper(func=function_with_unparseable_types)
    with pytest.raises(CannotParseTypeError):
        wrapper.schema


def test_parse_arguments():
    wrapper = FunctionWrapper(func=mock_function)
    parsed_args = wrapper.parse_arguments({"a": "test", "b": 123, "c": "default"})
    assert parsed_args == OrderedDict([("a", "test"), ("b", 123), ("c", "default")])


def test_parse_arguments_missing():
    wrapper = FunctionWrapper(func=mock_function)
    with pytest.raises(BrokenSchemaError):
        wrapper.parse_arguments({"a": "test"})


def test_call():
    wrapper = FunctionWrapper(func=mock_function)
    result = wrapper(
        {"a": "value1", "b": 2, "c": "default"}
    )  # TODO: should work without 'c'
    assert result == "Result: value1, 2, default"


def test_invalid_argument_types():
    wrapper = FunctionWrapper(func=mock_function)
    with pytest.raises(BrokenSchemaError):
        wrapper.parse_arguments({"a": 1, "b": "not an int"})


def test_missing_required_arguments():
    wrapper = FunctionWrapper(func=mock_function)
    with pytest.raises(BrokenSchemaError):
        wrapper.parse_arguments({"b": 123})


def test_extra_unexpected_arguments():
    wrapper = FunctionWrapper(func=mock_function)
    with pytest.raises(BrokenSchemaError):
        wrapper.parse_arguments({"a": "test", "b": 123, "d": "unexpected"})


def test_parse_arguments_with_default():
    def mock_function_with_default(a: str, b: int, c: str = "default") -> str:
        return f"Result: {a}, {b}, {c}"

    wrapper = FunctionWrapper(func=mock_function_with_default)
    with pytest.raises(BrokenSchemaError):
        wrapper.parse_arguments({"a": "test", "b": 123})


def test_function_with_no_return_value():
    def no_return_func(a, b):
        pass

    wrapper = FunctionWrapper(
        func=no_return_func, config=WrapperConfig(parsers=[MockArgSchemaParser])
    )
    result = wrapper({"a": "test", "b": 123})
    assert result is None


def test_function_that_raises_exception():
    def raises_exception(a, b):
        raise ValueError("An error occurred")

    wrapper = FunctionWrapper(
        func=raises_exception, config=WrapperConfig(parsers=[MockArgSchemaParser])
    )
    with pytest.raises(ValueError):
        wrapper({"a": "test", "b": 123})


def test_function_that_is_a_generator():
    def generator_func(a, b):
        yield a
        yield b

    wrapper = FunctionWrapper(
        func=generator_func, config=WrapperConfig(parsers=[MockArgSchemaParser])
    )
    gen = wrapper({"a": "test", "b": 123})
    assert next(gen) == "test"
    assert next(gen) == 123
