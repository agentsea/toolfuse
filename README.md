# Agent Tools

A common protocol for AI agent tools

## Installation

```
pip install agent-tool
```

## Usage

Let's define a simplified Selenium web browser tool

```python
from agent_tools import Tool, action, observation
from selenium import webdriver


class SeleniumBrowser(Tool):
    """Selenium browser as a tool"""

    def __init__(self, headless: bool = True) -> None:
        super().__init__()
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

    @action
    def open_url(self, url: str) -> None:
        """Open a URL in the browser

        Args:
            url (str): URL to open
        """
        self.driver.get(url)

    @action
    def click_element(self, selector: str, selector_type: str = "css_selector") -> None:
        """Click an element identified by a CSS selector

        Args:
            selector (str): CSS selector
            selector_type (str, optional): Selector type. Defaults to "css_selector".
        """
        element = self.driver.find_element(selector_type, selector)
        element.click()

    @observation
    def get_html(self) -> str:
        """Get the entire HTML of the current page.

        Returns:
            str: Page HTML
        """
        return self.driver.page_source

    def close(self) -> None:
        """Close the tool"""
        self.driver.quit()

```

We mark the functions to be made available to the agent as `@action` if they mutate the environment, and `@observation` if they are read only.

Now we can use this tool with an agent such as openai function calling

```python
from openai import OpenAI

client = OpenAI()

browser = SeleniumBrowser()
schemas = browser.json_schema()

messages = []
messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
messages.append({"role": "user", "content": "Get the HTML for the front page of wikipedia"})

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
        "name": "open_url",
        "arguments": "{\n  \"url\": \"https://wikipedia.org\"}"
      }
    },
    {
      "id": "call_TJIWlknwdoinfWEMFNss",
      "type": "function",
      "function": {
        "name": "get_html",
        "arguments": ""
      }
    }
  ]
}
```

Then to use this action

```python
for tool in assistant_message["tool_calls"]:
    action = browser.find_action(tool["function"]["name"])
    args = json.loads(tool["function"]["arguments"])
    resp = browser.use(action, **args)
```

Tools can be used locally or spun up on a server and used remotely (In progress)

## Share (In progress)

Register a tool with the AgentSea hub so others can find and use it.

```python
pip install agentsea
```

Create a repo to publish

```
agentsea create tool
```

Add your tool to the `tool.py` in the repo, fill in the `README.md` and add your dependencies using Poetry

Publish to the hub

```
agentsea publish .
```

## Roadmap

- Integrate with langchain, babyagi, autogpt, etc
