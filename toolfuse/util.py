import time

from .base import Tool, action


class AgentUtils(Tool):
    """Common tool utilities for agents"""

    @action
    def result(self, value: str) -> str:
        """Return a result to the user

        Args:
            value (str): Value to return

        Returns:
            str: Value returned
        """
        return value

    @action
    def wait(self, seconds: int) -> None:
        """Wait for a certain amount of time

        Args:
            seconds (str): Seconds to wait
        """
        time.sleep(seconds)
