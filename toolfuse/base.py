import inspect
import re
from abc import ABC
from importlib.metadata import version as pkgversion
from inspect import getdoc, getmodule
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from jsonschema import ValidationError, validate
from toolcore import FunctionWrapper

from .models import V1ToolRef


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
    method._is_action = True  # type: ignore
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
    method._is_observation = True  # type: ignore
    return method


T = TypeVar("T")


class Tool(ABC):
    """
    A Tool is an abstract base class that defines the interface for agent tools.

    Agent tools are the primary means by which an agent interacts with its environment.
    They encapsulate actions that an agent can perform and observations that an agent
    can make to understand the state of the environment. This class provides the necessary
    infrastructure for registering and managing these actions and observations.
    """

    def __init__(self, wraps: Optional["Tool"] = None) -> None:
        """
        Initializes a new instance of the Tool class, setting up the lists for actions and observations
        and registering the methods defined in the subclass.

        Args:
            wraps (Tool): An optional Tool instance that this Tool instance should wrap.
        """
        self._actions_list: List[Action] = []
        self._observations_list: List[Observation] = []
        self._register_methods()
        self.wraps = wraps

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
        out = self._actions_list
        if self.wraps:
            out.extend(self.wraps._actions_list)
        return out

    def observations(self) -> List[Observation]:
        """
        Returns a list of all registered observations that the agent can make.

        Each observation represents a piece of information that the agent can gather from its environment
        to inform its decision-making process.

        Returns:
            List[Observation]: A list of Observation instances representing the available observations.
        """
        out = self._observations_list
        if self.wraps:
            out.extend(self.wraps._observations_list)
        return out

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
        self._validate_parameters(action.schema, kwargs)
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
        self._validate_parameters(observation.schema, kwargs)
        if not isinstance(observation, Observation):
            raise ValueError(
                "Actions are not observable. Use the 'use' method to perform an action."
            )
        return observation(*args, **kwargs)

    def json_schema(
        self, actions_only: bool = False, exclude_names: List[str] = []
    ) -> List[Dict[str, Any]]:
        """
        Returns a list of JSON schemas representing the tool's actions and, optionally, observations,
        excluding any actions or observations with names listed in 'exclude_names'.

        Each schema provides a structured description of an action's or observation's interface, including its name,
        expected arguments, and other metadata.

        Args:
            actions_only (bool, optional): If True, only the action schemas will be returned. Defaults to False.
            exclude_names (List[str], optional): A list of action or observation names to exclude from the schema output.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing the JSON schema of an action or observation not excluded.
        """
        out = []
        for action in self.actions():
            if action.name not in exclude_names:
                out.append(action.schema)
        if not actions_only:
            for observation in self.observations():
                if observation.name not in exclude_names:
                    out.append(observation.schema)
        return out

    def _validate_parameters(
        self, schema: Dict[str, Any], parameters: Dict[str, Any]
    ) -> None:
        """
        Validates the provided parameters against the given schema.

        Args:
            schema (Dict[str, Any]): The schema defining the structure of the parameters.
            parameters (Dict[str, Any]): The parameters to validate.

        Raises:
            ValidationError: If the parameters do not conform to the schema.
        """
        try:
            validate(instance=parameters, schema=schema)
        except ValidationError as e:
            raise ValueError(f"Parameter validation error: {e.message}")

    def find_action(self, name: str) -> Optional[Action]:
        """
        Searches for an action or observation by name and returns it if found.

        This method checks both the actions and observations lists for a match.

        Args:
            name (str): The name of the action or observation to find.

        Returns:
            Optional[Action]: The Action or Observation instance with the matching name, or None if not found.
        """

        if self.wraps:
            for action in self.wraps.actions():
                if action.name == name:
                    return action

            for observation in self.wraps.observations():
                if observation.name == name:
                    return observation

        for action in self.actions():
            if action.name == name:
                return action

        for observation in self.observations():
            if observation.name == name:
                return observation

    def close(self) -> None:
        """
        A method that should be implemented by subclasses to handle the closing of the tool.

        This method is intended to provide a way to release any resources or perform any cleanup necessary
        when the tool is no longer needed.
        """
        return

    def context(self) -> str:
        """LLM context fork the tool

        Returns:
            str: LLM context for the tool
        """
        return self.__doc__  # type: ignore

    @classmethod
    def type(cls) -> str:
        """Tool type

        Returns:
            str: Tool type
        """
        return cls.__name__

    def ref(self) -> V1ToolRef:
        """Tool reference"""
        module = getmodule(self)
        if not module:
            raise ValueError("Tool not associated with a module")
        mod_parts = module.__name__.split(".")
        version = None
        try:
            version = pkgversion(mod_parts[0])
        except:
            pass
        return V1ToolRef(module=module.__name__, type=self.type(), version=version)

    def add_action(self, method: Callable) -> None:
        """
        Adds a new action to the tool using only the method provided. Name, schema,
        and description are derived automatically.

        Args:
            method (Callable): The callable method that implements the action.
        """
        name = method.__name__
        schema = self._generate_schema(
            method
        )  # Assuming a method to generate schema automatically
        description = self._parse_docstring(method)

        action = Action(name, method, schema, description)
        self._actions_list.append(action)

    def add_observation(self, method: Callable) -> None:
        """
        Adds a new observation to the tool using only the method provided. Name, schema,
        and description are derived automatically.

        Args:
            method (Callable): The callable method that implements the observation.
        """
        name = method.__name__
        schema = self._generate_schema(
            method
        )  # Assuming a method to generate schema automatically
        description = self._parse_docstring(method)

        observation = Observation(name, method, schema, description)
        self._observations_list.append(observation)

    def _generate_schema(self, method: Callable) -> Dict[str, Any]:
        """
        Generates a schema based on the method signature. This can be as simple or as
        complex as needed depending on how parameters are to be handled.

        Args:
            method (Callable): The method for which to generate a schema.

        Returns:
            Dict[str, Any]: A schema representing the parameters and their types.
        """
        # Example implementation using inspect to generate parameter types
        params = inspect.signature(method).parameters
        return {param: str(ptype.annotation) for param, ptype in params.items()}

    def add_actions(self, methods: List[Callable]) -> None:
        """
        Adds multiple actions to the tool using a list of methods. Each method's name, schema,
        and description are derived automatically.

        Args:
            methods (List[Callable]): A list of callable methods that implement actions.
        """
        for method in methods:
            self.add_action(method)

    def add_observations(self, methods: List[Callable]) -> None:
        """
        Adds multiple observations to the tool using a list of methods. Each method's name, schema,
        and description are derived automatically.

        Args:
            methods (List[Callable]): A list of callable methods that implement observations.
        """
        for method in methods:
            self.add_observation(method)

    def _add_action(
        self,
        method: Callable,
        name: Optional[str] = None,
        schema: Optional[Dict] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Adds a new action to the tool using the provided method.
        If the action with the same name already exists, it won't add it again.
        """
        if not name:
            name = method.__name__
        if any(action.name == name for action in self._actions_list):
            return  # Prevent duplicate actions
        action = Action(
            name, method, schema or {}, description or self._parse_docstring(method)
        )
        self._actions_list.append(action)

    def _add_observation(
        self,
        method: Callable,
        name: Optional[str] = None,
        schema: Optional[Dict] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Adds a new observation to the tool using the provided method.
        """
        if not name:
            name = method.__name__
        if any(obs.name == name for obs in self._observations_list):
            return  # Prevent duplicate observations
        observation = Observation(
            name, method, schema or {}, description or self._parse_docstring(method)
        )
        self._observations_list.append(observation)

    def merge(self, other: "Tool") -> None:
        """
        Merges the actions and observations from another tool into this tool.

        Args:
            other (Tool): The tool to merge into this tool.
        """
        for action in other.actions():
            self._add_action(
                action.method, action.name, action.schema, action.description
            )
        for observation in other.observations():
            self._add_observation(
                observation.method,
                observation.name,
                observation.schema,
                observation.description,
            )


def tool_from_cls(cls: Type[T]) -> Type[Tool]:
    """
    Dynamically creates a subclass of `Tool` that integrates methods from a given class `cls` as actions.

    Args:
        cls (Type[T]): The class from which to create a Tool, integrating its methods as actions.

    Returns:
        Type[Tool]: A new subclass of Tool that includes actions derived from `cls` methods.
    """

    class Combined(Tool, cls):
        """
        A combined class that inherits from both Tool and a user-defined class (cls).

        This class is dynamically created to combine the functionality of a user-defined class
        with the Tool class, allowing methods from the user-defined class to be registered as actions
        within the Tool framework. It initializes both parent classes and registers the user-defined
        class's methods as actions.

        Attributes:
            Inherits all attributes from the Tool class and the user-defined class (cls).

        Methods:
            __init__(*args, **kwargs): Initializes the Combined class, the Tool part of the class,
                                       and registers methods from the user-defined class as actions.
            type(): Returns the type of the class.
            _register_methods_from_cls(): Registers public methods from the user-defined class as actions.
        """

        def __init__(self, *args, **kwargs):
            """
            Initializes the Combined class by initializing both the user-defined class part and the Tool class part.
            It also registers the methods from the user-defined class (cls) as actions within the Tool framework.

            Args:
                *args: Variable length argument list passed to the user-defined class initializer.
                **kwargs: Arbitrary keyword arguments passed to the user-defined class initializer.
            """
            cls.__init__(
                self, *args, **kwargs  # type: ignore
            )  # Initialize the user-defined part of the combined class
            Tool.__init__(self)  # Initialize the Tool part of the combined class
            self._register_methods_from_cls()  # Register methods from cls as actions

        @classmethod
        def type(cls) -> str:
            """
            Returns the type of the class.

            Returns:
                str: The type of the class.
            """
            return cls.__name__

        def _register_methods_from_cls(self):
            """
            Registers all public methods from the user-defined class (cls) as actions.

            This method iterates over all public methods of cls and registers them as actions,
            allowing them to be utilized within the Tool framework.
            """
            for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
                # Skip private and protected methods, skip methods from Tool or object class
                if (
                    name.startswith("_")
                    or inspect.getmodule(method) == inspect.getmodule(Tool)
                    or inspect.getmodule(method) == inspect.getmodule(object)
                ):
                    continue

                # Wrap the method to get its schema
                wrapper = FunctionWrapper(method)

                # Use the existing method to create a description based on the method's docstring
                description = self._parse_docstring(method)

                # Use the schema generated by FunctionWrapper
                schema = wrapper.schema

                # Create an Action instance for the method
                action = Action(name, method, schema, description)

                # Add the Action to the tool's actions list
                self._actions_list.append(action)

    Combined.__name__ = f"{cls.__name__}Tool"
    return Combined


def tool_from_function(function: Callable) -> Type[Tool]:
    """
    Dynamically creates a subclass of `Tool` that encapsulates a given function as an action.

    Args:
        function (Callable): The function to be encapsulated as an action in the Tool.

    Returns:
        Type[Tool]: A new subclass of Tool that includes the given function as an action.
    """

    class FunctionTool(Tool):
        """
        A subclass of `Tool` designed to encapsulate a single function as an actionable method within the Tool framework.

        This class takes a function upon initialization and registers it as an action, making it callable within the context of the Tool's environment. The primary purpose of this class is to allow standalone functions to be seamlessly integrated into the Tool framework, providing a straightforward way to extend functionality with custom actions.

        Attributes:
            function (Callable): The function that is encapsulated as an action within the Tool.

        Methods:
            __init__(self, function: Callable): Initializes a new instance of the FunctionTool class, registering the provided function as an action.
            _register_function_as_action(self, function: Callable): Registers the provided function as an action for the Tool.
        """

        def __init__(self):
            """
            Initializes a new instance of the FunctionTool class.

            This constructor method takes a function as an argument and calls the internal method to register it as an action within the Tool.

            Args:
                function (Callable): The function to be encapsulated as an action in the Tool.
            """
            super().__init__()
            self._register_function_as_action(function)

        def _register_function_as_action(self, function: Callable):
            """
            Registers the provided function as an action for the Tool.

            This method wraps the given function to extract its schema and documentation, creating an Action instance that encapsulates the function. This allows the function to be called as an action within the Tool's environment.

            Args:
                function (Callable): The function to be registered as an action.
            """
            # Wrap the function to get its schema
            wrapper = FunctionWrapper(function)

            # Generate a description from the function's docstring
            description = self._parse_docstring(function)

            # Use the schema generated by FunctionWrapper
            schema = wrapper.schema

            # Extract the name of the function to use as the action name
            name = function.__name__

            # Create an Action instance for the function
            action = Action(name, function, schema, description)

            # Add the Action to the tool's actions list
            self._actions_list.append(action)

    FunctionTool.__name__ = f"{function.__name__}_tool"
    return FunctionTool


def tool_from_object(obj: Any) -> Tool:
    """
    Dynamically creates a subclass of `Tool` that encapsulates the methods of a given object instance as actions.

    Args:
        obj (Any): The object instance whose methods are to be encapsulated as actions in the Tool.

    Returns:
        Tool: A new subclass of Tool that includes the object's methods as actions.
    """

    class ObjectTool(Tool):
        """
        A subclass of `Tool` that encapsulates the methods of a given object instance as actions.

        This class dynamically creates actions based on the public methods of the provided object instance. Each method is wrapped as an `Action` object, allowing it to be invoked within the Tool's environment.

        Attributes:
            obj_instance (Any): The object instance whose methods are to be encapsulated as actions.

        Methods:
            __init__(self, obj_instance: Any): Initializes a new instance of `ObjectTool` with the given object.
            _register_methods_from_object(self): Registers all public methods of `obj_instance` as actions.
        """

        def __init__(self, obj_instance: Any):
            """
            Initializes a new instance of `ObjectTool`.

            This constructor method takes an object instance as an argument and calls the internal method to register its public methods as actions within the Tool.

            Args:
                obj_instance (Any): The object instance whose methods are to be encapsulated as actions.
            """
            super().__init__()
            self.obj_instance = obj_instance
            self._register_methods_from_object()

        def _register_methods_from_object(self):
            """
            Registers all public methods of the object instance as actions for the Tool.

            This method iterates over all public methods of the provided object instance, excluding private, protected, and dunder methods. Each method is wrapped as an `Action` object and added to the tool's actions list.
            """
            for name, method in inspect.getmembers(
                self.obj_instance, predicate=inspect.ismethod
            ):
                # Skip private and protected methods, and skip dunder methods
                if name.startswith("_"):
                    continue

                # Skip methods not defined in the class of obj_instance (e.g., inherited from object)
                if inspect.getmodule(method.__func__) != inspect.getmodule(
                    self.obj_instance.__class__
                ):
                    continue

                # Wrap the method to get its schema
                wrapper = FunctionWrapper(method)

                # Generate a description from the method's docstring
                description = self._parse_docstring(method)

                # Use the schema generated by FunctionWrapper
                schema = wrapper.schema

                # Create an Action instance for the method
                action = Action(name, method, schema, description)

                # Add the Action to the tool's actions list
                self._actions_list.append(action)

    ObjectTool.__name__ = f"{obj.__class__.__name__}Tool"
    # Return an instance of ObjectTool instead of the class itself, as we need to pass the object instance to it
    return ObjectTool(obj)  # type: ignore


def tool(input: Union[Type, Callable, Any]) -> Union[Type[Tool], Tool]:
    """
    Dynamically creates a Tool instance or class based on the type of the input.

    This function determines whether the input is a class, a function, or an object instance
    and then calls the appropriate tool creation function (`tool_from_cls`, `tool_from_function`,
    or `tool_from_object`).

    Args:
        input (Union[Type, Callable, Any]): The input for which to create a Tool. This can be
                                            a class, a function, or an object instance.

    Returns:
        Union[Type[Tool], Tool]: A Tool class if the input is a class or function, or a Tool
                                 instance if the input is an object instance.
    """
    if inspect.isclass(input):
        # Input is a class, so we use tool_from_cls
        return tool_from_cls(input)
    elif inspect.isfunction(input):
        # Input is a function, so we use tool_from_function
        return tool_from_function(input)
    else:
        # Assume the input is an object instance, so we use tool_from_object
        return tool_from_object(input)
