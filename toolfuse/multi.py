from typing import List

from .base import Tool


class MultiTool(Tool):
    """Multiple tools actions combined as one tool"""

    def __init__(self, tools: List[Tool]):
        """
        Initializes a new instance of MultiTool, inheriting from Tool and aggregating functionalities from multiple tools.

        Args:
            tools (List[Tool]): A list of Tool instances to be aggregated.
        """
        self.tools = tools
        super().__init__()

    def _register_methods(self) -> None:
        """
        Overrides the _register_methods of Tool to aggregate methods from sub-tools rather than looking at its own methods.
        """
        # Clear any existing actions and observations
        self._actions_list = []
        self._observations_list = []

        # Aggregate actions and observations from all contained tools
        for tool in self.tools:
            self._actions_list.extend(tool.actions())
            self._observations_list.extend(tool.observations())
