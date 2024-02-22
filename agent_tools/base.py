from abc import ABC, abstractmethod
from typing import List, Callable, Any, Dict, Optional
from inspect import getdoc
import re

from .function import FunctionWrapper


class Action:
    """
    Represents an action that an agent can perform in an environment.

    This class is used to encapsulate information about an action, including its
    name, the method that implements the action, the schema that defines the
    structure of the action's parameters, and a human-readable description of the
    action.

    Attributes:
        name (str): The name of the action. This is typically a unique identifier.
        method (Callable): The callable method that is executed when the action is taken.
        schema (Dict): A dictionary that defines the structure and types of the parameters
                       that the action expects.
        description (str): A human-readable description of what the action does and its
                           purpose within the context of the agent's environment.

    Methods:
        __call__(*args, **kwargs) -> Any:
            Allows the Action instance to be called like a function, which will in turn
            call the method associated with this action, passing through any arguments
            and keyword arguments.
    """

    def __init__(self, name: str, method: Callable, schema: Dict, description: str):
        """
        Initializes a new instance of the Action class.

        Args:
            name (str): The name of the action.
            method (Callable): The callable method that implements the action.
            schema (Dict): The schema defining the structure of the action's parameters.
            description (str): A description of the action.
        """
        self.name = name
        self.method = method
        self.schema = schema
        self.description = description

    def __call__(self, *args, **kwargs) -> Any:
        """
        Executes the action's method with the given arguments and keyword arguments.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The result of the action method execution.
        """
        return self.method(*args, **kwargs)


class Observation(Action):
    """
    Represents an observation that an agent can make in an environment.

    This class is used to encapsulate information about an observation, including its
    name, the method that implements the observation, the schema that defines the
    structure of the observation's data, and a human-readable description of the
    observation.

    Attributes:
        name (str): The name of the observation. This is typically a unique identifier.
        method (Callable): The callable method that is executed to obtain the observation.
        schema (Dict): A dictionary that defines the structure and types of the data
                       that the observation returns.
        description (str): A human-readable description of what the observation represents
                           and its purpose within the context of the agent's environment.

    Methods:
        __call__(*args, **kwargs) -> Any:
            Allows the Observation instance to be called like a function, which will in turn
            call the method associated with this observation, passing through any arguments
            and keyword arguments.
    """

    def __init__(self, name: str, method: Callable, schema: Dict, description: str):
        """
        Initializes a new instance of the Observation class.

        Args:
            name (str): The name of the observation.
            method (Callable): The callable method that implements the observation.
            schema (Dict): The schema defining the structure of the observation's data.
            description (str): A description of the observation.
        """
        self.name = name
        self.method = method
        self.schema = schema
        self.description = description

    def __call__(self, *args, **kwargs) -> Any:
        """
        Executes the observation's method with the given arguments and keyword arguments.

        This method allows the observation to be obtained in a manner similar to calling
        a function, with the observation's method determining the exact data returned.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The result of the observation method execution, typically data about the
            environment or the agent's state within it.
        """
        return self.method(*args, **kwargs)


def action(method: Callable) -> Callable:
    """
    A decorator that marks a method as an action within the Tool.

    This decorator adds a special attribute to the method indicating that it
    should be treated as an action. Actions are potential operations that an
    agent can perform in its environment.

    Args:
        method (Callable): The method to be marked as an action.

    Returns:
        Callable: The original method with the added '_is_action' attribute.
    """
    method._is_action = True
    return method


def observation(method: Callable) -> Callable:
    """
    A decorator that marks a method as an observation within the Tool.

    This decorator adds a special attribute to the method indicating that it
    should be treated as an observation. Observations are pieces of information
    that an agent can gather from its environment to inform its decision-making
    process.

    Args:
        method (Callable): The method to be marked as an observation.

    Returns:
        Callable: The original method with the added '_is_observation' attribute.
    """
    method._is_observation = True
    return method


class Tool(ABC):
    """
    A Tool is an abstract base class that defines the interface for agent tools.

    Agent tools are the primary means by which an agent interacts with its environment.
    They encapsulate actions that an agent can perform and observations that an agent
    can make to understand the state of the environment. This class provides the necessary
    infrastructure for registering and managing these actions and observations.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the Tool class, setting up the lists for actions and observations
        and registering the methods defined in the subclass.
        """
        self._actions_list: List[Action] = []
        self._observations_list: List[Observation] = []
        self._register_methods()

    def _register_methods(self) -> None:
        """
        Scans the Tool instance for methods marked as actions or observations and registers them.

        This method looks for callable attributes of the instance that have either the '_is_action'
        or '_is_observation' attribute set to True, indicating that they should be treated as actions
        or observations, respectively. It then creates Action or Observation instances for these methods
        and adds them to the appropriate list.
        """
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_is_action"):
                wrapper = FunctionWrapper(attr)
                description = self._parse_docstring(attr)
                action = Action(attr_name, attr, wrapper.schema, description)
                self._actions_list.append(action)
            elif callable(attr) and hasattr(attr, "_is_observation"):
                wrapper = FunctionWrapper(attr)
                description = self._parse_docstring(attr)
                observation = Observation(attr_name, attr, wrapper.schema, description)
                self._observations_list.append(observation)

    def _parse_docstring(self, method: Callable) -> str:
        """
        Extracts the first sentence from a method's docstring to use as a description.

        Args:
            method (Callable): The method from which to extract the docstring.

        Returns:
            str: The first sentence of the method's docstring, if available. Otherwise, an empty string.
        """
        docstring = getdoc(method)
        if docstring:
            return re.split(r"\.\s+", docstring)[0]
        return ""

    def actions(self) -> List[Action]:
        """
        Returns a list of all registered actions that the agent can take.

        Each action represents a potential operation that the agent can perform in its environment.

        Returns:
            List[Action]: A list of Action instances representing the available actions.
        """
        return self._actions_list

    def observations(self) -> List[Observation]:
        """
        Returns a list of all registered observations that the agent can make.

        Each observation represents a piece of information that the agent can gather from its environment
        to inform its decision-making process.

        Returns:
            List[Observation]: A list of Observation instances representing the available observations.
        """
        return self._observations_list

    def use(self, action: Action, *args, **kwargs) -> Any:
        """
        Executes an action with the provided arguments and keyword arguments.

        Args:
            action (Action): The Action instance representing the action to perform.
            *args: Variable length argument list for the action.
            **kwargs: Arbitrary keyword arguments for the action.

        Returns:
            Any: The result of the action execution, which can vary depending on the action.
        """
        return action(*args, **kwargs)

    def observe(self, observation: Observation, *args, **kwargs) -> Any:
        """
        Executes an observation with the provided arguments and keyword arguments.

        Args:
            observation (Observation): The Observation instance representing the observation to run.
            *args: Variable length argument list for the observation.
            **kwargs: Arbitrary keyword arguments for the observation.

        Returns:
            Any: The result of the observation execution, which can vary depending on the observation.
        """
        if not isinstance(observation, Observation):
            raise ValueError(
                "Actions are not observable. Use the 'use' method to perform an action."
            )
        return observation(*args, **kwargs)

    def json_schema(self) -> List[Dict[str, Any]]:
        """
        Returns a list of JSON schemas representing the tool's actions.

        Each schema provides a structured description of an action's interface, including its name,
        expected arguments, and other metadata.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing the JSON schema of an action.
        """
        out = []
        for action in self.actions():
            out.append(action.schema)
        for observation in self.observations():
            out.append(observation.schema)
        return out

    def find_action(self, name: str) -> Optional[Action]:
        """
        Searches for an action or observation by name and returns it if found.

        This method checks both the actions and observations lists for a match.

        Args:
            name (str): The name of the action or observation to find.

        Returns:
            Optional[Action]: The Action or Observation instance with the matching name, or None if not found.
        """
        for action in self.actions():
            if action.name == name:
                return action

        for observation in self.observations():
            if observation.name == name:
                return observation

    @abstractmethod
    def close(self) -> None:
        """
        An abstract method that should be implemented by subclasses to handle the closing of the tool.

        This method is intended to provide a way to release any resources or perform any cleanup necessary
        when the tool is no longer needed.
        """
        pass
