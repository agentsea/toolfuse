from typing import Optional

from pydantic import BaseModel


class V1ToolRef(BaseModel):
    """A reference to a tool or device"""

    module: str
    type: str
    version: Optional[str] = None
    package: Optional[str] = None
