from dataclasses import dataclass

from source.logic.types import Float


@dataclass
class Cargo:
    name: str
    mass: Float
    health: Float = 1.0
    fragility: Float = 0.5
