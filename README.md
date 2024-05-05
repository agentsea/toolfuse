<!-- PROJECT LOGO -->
<br />
<p align="center">
  <!-- <a href="https://github.com/agentsea/skillpacks">
    <img src="https://project-logo.png" alt="Logo" width="80">
  </a> -->

  <h1 align="center">ToolFuse</h1>

  <p align="center">
    A common protocol for AI agent tools
    <br />
    <a href="https://github.com/agentsea/toolfuse"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/agentsea/toolfuse">View Demo</a>
    ·
    <a href="https://github.com/agentsea/toolfuse/issues">Report Bug</a>
    ·
    <a href="https://github.com/agentsea/toolfuse/issues">Request Feature</a>
  </p>
  <br>
</p>

ToolFuse provides a common protocol for AI agent tools, use them with your favorite agent framework or model.

## Installation

```
pip install toolfuse
```

## Usage

A simple weather logger tool

```python
from toolfuse import Tool, action, observation
from selenium import webdriver


class WeatherLogger(Tool):
  """A simple weather logger."""

    @action
    def log(self, message: str) -> None:
        """Logs a message to the log file."""

        with open("weather.txt", "a") as file:
            file.write("***\n" + message + "\n")

    @observation
    def weather(self, location: str) -> str:
        """Checks the current weather from the internet using wttr.in."""

        weather_api_url = f"http://wttr.in/{location}?format=%l:+%C+%t"
        response = requests.get(weather_api_url)
        response.raise_for_status()
        return response.text

```

The functions to be made available to the agent as

- `@action` if they mutate the environment
- `@observation` if they are read only.

Use the tool in a prompt

```python
weather_logger = WeatherLogger()

msg = f"Please select the appropriate action from {weather_logger.json_schema()}"
```

Create a tool from an existing class

```python
from toolfuse import tool

class Foo:
  def echo(self, txt: str) -> str:
    return txt


foo_tool = tool(Foo())
```

Create a tool from an existing function

```python
from toolfuse import tool

def echo(txt: str) -> str:
  return txt

echo_tool = tool(echo)
```

### Function Calling

Use a tool with OpenAI function calling

```python
from openai import OpenAI

client = OpenAI()

weatherlogger = WeatherLogger()
schemas = weatherlogger.json_schema()

messages = []
messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
messages.append({"role": "user", "content": "What is the weather in Paris?"})

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + openai.api_key,
}
json_data = {"model": model, "messages": messages, "tools": schemas}
response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers=headers,
    json=json_data,
)

assistant_message = response.json()["choices"][0]["message"]
messages.append(assistant_message)
assistant_message
```

```json
{
  "role": "assistant",
  "tool_calls": [
    {
      "id": "call_RYXaDjxpUCfWmpXU7BZEYVqS",
      "type": "function",
      "function": {
        "name": "weather",
        "arguments": "{\n  \"location\": \"Paris\"}"
      }
    }
  ]
}
```

Then to use this action

```python
for tool in assistant_message["tool_calls"]:
    action = weatherlogger.find_action(tool["function"]["name"])
    args = json.loads(tool["function"]["arguments"])
    resp = weatherlogger.use(action, **args)
```

## MultiTool

Combine tools with MultiTool

```python
from toolfuse import Tool, MultiTool

class Chat(Tool):
  """A simple chat tool"""

    @action
    def send_message(self, message: str) -> None:
        """Logs a message to the log file."""

        with open("chat.txt", "a") as file:
            file.write("***\n" + message + "\n")


multitool = MultiTool(tools=[WeatherLogger(), Chat()])
multitool.json_schema()
```

Merge one tools actions into another

```python
chat_tool = Chat()
chat_tool.merge(WeatherLogger())
```

Add an action to a tool

```python
def echo(txt: str) -> str:
  return txt

weather_tool = WeatherLogger()
weather_tool.add_action(echo)
```

## Available Tools

:computer: [AgentDesk](https://github.com/agentsea/agentdesk) provides AI agents with a full GUI desktop locally or in the cloud.

:wrench: [AgentUtils](https://github.com/agentsea/toolfuse/blob/main/toolfuse/util.py) provides some basic utilities for agentic tool use

## Roadmap

- [ ] Integrate with langchain
- [ ] Integrate with babyagi
- [ ] Integrate with autogen
- [ ] Integrate with llamaindex
