from pydantic import BaseModel
from typing import Any


class Programacion(BaseModel):
    id: int
    fields: dict[str, Any]
