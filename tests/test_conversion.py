import pytest
from toolfuse import (
    tool,
    Tool,
    Action,
)  # Adjust the import based on your actual module name and structure


class MyClass:
    def my_method(self, x: int):
        return x * 2


def my_function(x: int):
    return x + 2


my_object = MyClass()


def test_tool_from_class():
    MyClassTool = tool(MyClass)
    assert issubclass(
        MyClassTool, Tool
    ), "The returned type should be a subclass of Tool"
    my_class_tool_instance = MyClassTool()
    assert hasattr(
        my_class_tool_instance, "my_method"
    ), "The tool should have the 'my_method' action"
    action_result = my_class_tool_instance.use(my_class_tool_instance.actions()[0], 5)
    assert (
        action_result == 10
    ), "The action should correctly execute the original method"


def test_tool_from_function():
    MyFunctionTool = tool(my_function)
    assert MyFunctionTool.name() == "my_function_tool"
    assert issubclass(
        MyFunctionTool, Tool
    ), "The returned type should be a subclass of Tool"
    my_function_tool_instance = MyFunctionTool()
    action_result = my_function_tool_instance.use(
        my_function_tool_instance.actions()[0], 3
    )
    assert (
        action_result == 5
    ), "The action should correctly execute the original function"


def test_tool_from_object():
    MyObjectTool = tool(my_object)
    assert isinstance(
        MyObjectTool, Tool
    ), "The returned instance should be of type Tool"
    print("actions: ", MyObjectTool.actions())
    actions = MyObjectTool.actions()
    assert len(actions) == 1
    assert actions[0].name == "my_method"
    action_result = MyObjectTool.use(MyObjectTool.actions()[0], 5)
    assert (
        action_result == 10
    ), "The action should correctly execute the original object's method"


def test_tool_input_type_detection():
    # Ensuring that the tool function correctly identifies input types and returns the appropriate Tool type or instance
    assert issubclass(
        tool(MyClass), Tool
    ), "tool should return a subclass of Tool for class input"
    assert issubclass(
        tool(my_function), Tool
    ), "tool should return a subclass of Tool for function input"
    assert isinstance(
        tool(my_object), Tool
    ), "tool should return a Tool instance for object input"
