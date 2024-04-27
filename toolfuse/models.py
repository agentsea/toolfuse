from typing import Optional

from pydantic import BaseModel


class V1ToolRef(BaseModel):
    """A reference to a tool or device"""

    module: str
    name: str
    version: Optional[str] = None
