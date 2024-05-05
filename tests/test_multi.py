import pytest
from toolfuse import Tool, action, observation
from toolfuse.multi import MultiTool


class WeatherTool(Tool):
    @action
    def get_weather(self, location: str) -> str:
        """Simulate getting the weather for a location."""
        return f"Weather at {location} is sunny."

    @observation
    def current_temperature(self) -> str:
        """Simulate getting the current temperature."""
        return "Current temperature is 25°C."


class ChatTool(Tool):
    @action
    def send_message(self, message: str) -> str:
        """Simulate sending a chat message."""
        return f"Message sent"

    @observation
    def last_message(self) -> str:
        """Return the last message sent."""
        return f"Last message was blah"


def test_get_weather():
    weather_tool = WeatherTool()
    location = "New York"
    expected_output = "Weather at New York is sunny."
    assert (
        weather_tool.get_weather(location) == expected_output
    ), "The get_weather method should return the correct weather."


def test_current_temperature():
    weather_tool = WeatherTool()
    expected_temp = "Current temperature is 25°C."
    assert (
        weather_tool.current_temperature() == expected_temp
    ), "The current_temperature method should return the correct temperature."


@pytest.fixture
def weather_tool():
    return WeatherTool()


@pytest.fixture
def chat_tool():
    return ChatTool()


@pytest.fixture
def multitool(weather_tool: WeatherTool, chat_tool: ChatTool):
    return MultiTool([weather_tool, chat_tool])


def test_multitool_aggregates_actions(
    multitool: MultiTool, weather_tool: WeatherTool, chat_tool: ChatTool
):
    # Verify all actions from both tools are aggregated
    actions = multitool.actions()

    action_names = [action.name for action in actions]
    assert "get_weather" in action_names
    assert "send_message" in action_names

    assert len(actions) == 2  # Assuming no other actions are added


def test_multitool_aggregates_observations(
    multitool: MultiTool, weather_tool: WeatherTool, chat_tool: ChatTool
):
    # Verify all observations from both tools are aggregated
    observations = multitool.observations()

    obs_names = [obs.name for obs in observations]
    assert "current_temperature" in obs_names
    assert "last_message" in obs_names

    assert len(observations) == 2  # Assuming no other observations are added


def test_multitool_executes_weather_action(multitool: MultiTool):
    # Test executing a weather action through multitool
    result = multitool.use(
        multitool.actions()[0], "New York"
    )  # Assuming get_weather is the first action
    assert result == "Weather at New York is sunny."


def test_multitool_executes_chat_action(multitool: MultiTool):
    # Test executing a chat action through multitool
    result = multitool.use(
        multitool.actions()[1], "Hello World!"
    )  # Assuming send_message is the second action
    assert result == "Message sent"


def test_multitool_executes_weather_observation(multitool: MultiTool):
    # Test executing a weather observation through multitool
    result = multitool.observe(
        multitool.observations()[0]
    )  # Assuming current_temperature is the first observation
    assert result == "Current temperature is 25°C."


def test_multitool_executes_chat_observation(multitool: MultiTool):
    # Test executing a chat observation through multitool
    result = multitool.observe(
        multitool.observations()[1]
    )  # Assuming last_message is the second observation
    assert result == "Last message was blah"


def test_merge(weather_tool: WeatherTool, chat_tool: ChatTool):
    weather_tool.merge(chat_tool)
    # Verify all actions from both tools are aggregated
    actions = weather_tool.actions()

    action_names = [action.name for action in actions]
    assert "get_weather" in action_names
    assert "send_message" in action_names

    assert len(actions) == 2

    # Verify all observations from both tools are aggregated
    observations = weather_tool.observations()

    obs_names = [obs.name for obs in observations]
    assert "current_temperature" in obs_names
    assert "last_message" in obs_names

    assert len(observations) == 2


def test_add_action(weather_tool: WeatherTool):

    def get_foo(bar: str) -> str:
        return f"Foobar {bar}"

    weather_tool.add_action(get_foo)

    # Verify all actions from both tools are aggregated
    actions = weather_tool.actions()

    action_names = [action.name for action in actions]
    assert "get_weather" in action_names
    assert "get_foo" in action_names

    assert len(actions) == 2

    # Verify all observations from both tools are aggregated
    observations = weather_tool.observations()

    obs_names = [obs.name for obs in observations]
    assert "current_temperature" in obs_names

    assert len(observations) == 1

    action = weather_tool.find_action("get_foo")
    assert action is not None

    result = weather_tool.use(action, bar="baz")
    assert result == "Foobar baz"
