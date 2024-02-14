from abc import ABC, abstractmethod
from typing import List, Callable, Any, Dict, Optional
from inspect import getdoc
import re

from .function import FunctionWrapper


class Action:
    """An action an agent can take"""

    def __init__(self, name: str, method: Callable, schema: Dict, description: str):
        self.name = name
        self.method = method
        self.schema = schema
        self.description = description

    def __call__(self, *args, **kwargs) -> Any:
        return self.method(*args, **kwargs)


class Observation:
    """An observation an agent can make"""

    def __init__(self, name: str, method: Callable, schema: Dict, description: str):
        self.name = name
        self.method = method
        self.schema = schema
        self.description = description

    def __call__(self, *args, **kwargs) -> Any:
        return self.method(*args, **kwargs)


def action(method):
    """An action method decorator"""
    method._is_action = True
    return method


def observation(method):
    """An observation method decorator"""
    method._is_observation = True
    return method


class Tool(ABC):
    """A tool is an agents means of interacting with the world"""

    def __init__(self) -> None:
        self._actions_list: List[Action] = []
        self._observations_list: List[Observation] = []
        self._register_methods()

    def _register_methods(self) -> None:
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_is_action"):
                wrapper = FunctionWrapper(attr)
                description = self._parse_docstring(attr)
                action = Action(attr_name, wrapper, wrapper.schema, description)
                self._actions_list.append(action)
            elif callable(attr) and hasattr(attr, "_is_observation"):
                wrapper = FunctionWrapper(attr)
                description = self._parse_docstring(attr)
                observation = Observation(
                    attr_name, wrapper, wrapper.schema, description
                )
                self._observations_list.append(observation)

    def _parse_docstring(self, method: Callable) -> str:
        docstring = getdoc(method)
        if docstring:
            return re.split(r"\.\s+", docstring)[0]
        return ""

    def actions(self) -> List[Action]:
        """Actions the agent can take

        Returns:
            List[Action]: List of actions
        """
        return self._actions_list

    def observations(self) -> List[Observation]:
        """Observations the agent can make

        Returns:
            List[Observation]: List of observations
        """
        return self._observations_list

    def use(self, action: Action, *args, **kwargs) -> Any:
        """Use the tool

        Args:
            action (Action): Action to perform
            args (Any): Args for the action
            kwargs (Any): Kwargs for the action

        Returns:
            Any: Result
        """
        return action(*args, **kwargs)

    def observe(self, observation: Observation, *args, **kwargs) -> Any:
        """Perform an observation

        Args:
            observation (Action): Observation to run
            args (Any): Args for the action
            kwargs (Any): Kwargs for the action

        Returns:
            Any: Result
        """
        return observation(*args, **kwargs)

    def json_schema(self) -> List[Dict[str, Any]]:
        """Tool as a list of JSON schemas

        Returns:
            List[Dict[str, Any]]: A list of function JSON schemas
        """
        out = []
        for action in self.actions():
            out.append(action.schema)
        return out

    def find_action(self, name: str) -> Optional[Action]:
        """Find an action or observation

        Args:
            name (str): Name of the action

        Returns:
            Action: An action
        """
        for action in self.actions():
            if action.name == name:
                return action

        for observation in self.actions():
            if observation.name == name:
                return observation

    @abstractmethod
    def close(self) -> None:
        """Close the tool"""
        pass
