import pytest
from unittest.mock import Mock
from toolfuse.base import Action, Observation, Tool, action, observation


def test_action_initialization_and_call():
    mock_method = Mock(return_value="action_result")
    action_instance = Action(
        "test_action",
        mock_method,
        {"schema_key": "schema_value"},
        "Test action description",
    )
    assert action_instance.name == "test_action"
    assert action_instance.schema == {"schema_key": "schema_value"}
    assert action_instance.description == "Test action description"
    result = action_instance("arg1", kwarg1="kwarg1")
    mock_method.assert_called_with("arg1", kwarg1="kwarg1")
    assert result == "action_result"


def test_observation_initialization_and_call():
    mock_method = Mock(return_value="observation_result")
    observation_instance = Observation(
        "test_observation",
        mock_method,
        {"schema_key": "schema_value"},
        "Test observation description",
    )
    assert observation_instance.name == "test_observation"
    assert observation_instance.schema == {"schema_key": "schema_value"}
    assert observation_instance.description == "Test observation description"
    result = observation_instance("arg1", kwarg1="kwarg1")
    mock_method.assert_called_with("arg1", kwarg1="kwarg1")
    assert result == "observation_result"


def test_action_decorator():
    @action
    def mock_action():
        pass

    assert hasattr(mock_action, "_is_action")


def test_observation_decorator():
    @observation
    def mock_observation():
        pass

    assert hasattr(mock_observation, "_is_observation")


class MockTool(Tool):
    @action
    def mock_action(self):
        """Mock action method"""
        return "action_performed"

    @observation
    def mock_observation(self):
        """Mock observation method"""
        return "observation_made"

    def close(self):
        pass


@pytest.fixture
def tool():
    return MockTool()


def test_register_methods(tool):
    assert len(tool._actions_list) == 1
    assert len(tool._observations_list) == 1


def test_actions_method(tool):
    actions = tool.actions()
    assert len(actions) == 1
    assert all(isinstance(action, Action) for action in actions)


def test_observations_method(tool):
    observations = tool.observations()
    assert len(observations) == 1
    assert isinstance(observations[0], Observation)


def test_use_action(tool):
    result = tool.use(tool._actions_list[0])
    assert result == "action_performed"


def test_use_observation(tool):
    result = tool.use(tool._observations_list[0])
    assert result == "observation_made"


def test_observe_action(tool):
    with pytest.raises(ValueError):
        tool.observe(tool._actions_list[0])


def test_observe_observation(tool):
    result = tool.observe(tool._observations_list[0])
    assert result == "observation_made"


def test_json_schema_method(tool):
    schemas = tool.json_schema()
    print("schemas:", schemas)
    assert len(schemas) == 2
    assert all(isinstance(schema, dict) for schema in schemas)


def test_find_action(tool):
    action_found = tool.find_action("mock_action")
    assert action_found is not None
    assert action_found.name == "mock_action"

    observation_found = tool.find_action("mock_observation")
    assert observation_found is not None
    assert observation_found.name == "mock_observation"

    not_found = tool.find_action("non_existent")
    assert not_found is None


def test_parse_docstring(tool):
    action_description = tool._parse_docstring(tool.mock_action)
    assert action_description == "Mock action method"

    observation_description = tool._parse_docstring(tool.mock_observation)
    assert observation_description == "Mock observation method"
