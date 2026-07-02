from dataclasses import dataclass

from source.shared.types import Float


@dataclass
class Cargo:
    name: str
    mass: Float
    health: Float = 1.0
    fragility: Float = 0.5
