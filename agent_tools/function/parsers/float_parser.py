"""Parser for float types"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ..exceptions import BrokenSchemaError
from .atomic_type_parser import AtomicParser

if TYPE_CHECKING:
    from ..json_type import JsonType


class FloatParser(AtomicParser[float]):
    """Parser for float types"""

    _type = float
    schema_type_name: str = "number"

    def parse_value(self, value: JsonType) -> float:
        if not isinstance(value, (float, int)):
            raise BrokenSchemaError(value, self.argument_schema)
        return float(value)
