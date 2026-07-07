from dataclasses import dataclass

from source.shared.math import lerp
from source.shared.types import Float


@dataclass
class Consumable:
    name: str
    mass: Float
    max_mass: Float
    empty_com_height: Float
    full_com_height: float

    @property
    def fill_fraction(self) -> Float:
        if self.max_mass <= 0.0:
            return 0.0
        return min(self.mass / self.max_mass, 1.0)

    @property
    def com_height(self) -> Float:
        return lerp(self.empty_com_height, self.full_com_height, self.fill_fraction)
