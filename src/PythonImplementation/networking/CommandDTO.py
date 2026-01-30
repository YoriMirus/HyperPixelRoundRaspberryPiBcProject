from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class CommandDTO:
    name: str
    args: Tuple[str, ...]
    ip: str

