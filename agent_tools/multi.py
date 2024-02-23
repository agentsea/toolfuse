from typing import List

from .base import Tool, action


class MultiTool(Tool):
    """A multi-tool selects the right tool for the job"""

    def __init__(self, options: List[Tool]) -> None:
        self.options = options

    @action
    def select_tool(self, task: str) -> Tool:
        pass
