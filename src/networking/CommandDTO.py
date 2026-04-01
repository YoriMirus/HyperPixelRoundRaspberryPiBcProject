from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass(frozen=True)
class CommandDTO:
    name: str
    args: Tuple[str, ...] = ()
    ip: Optional[str] = None

