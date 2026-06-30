from dataclasses import dataclass
from typing import TypeAlias

Float: TypeAlias = int | float


@dataclass(frozen=True)
class Point:
    x: Float
    y: Float

    def __post_init__(self):
        object.__setattr__(self, "x", float(self.x))
        object.__setattr__(self, "y", float(self.y))
