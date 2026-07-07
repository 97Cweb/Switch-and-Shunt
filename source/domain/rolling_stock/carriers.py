from dataclasses import dataclass, field

from source.domain.rolling_stock.cargo import Cargo
from source.domain.rolling_stock.consumable import Consumable
from source.shared.types import Float


@dataclass
class CargoCarrier:
    cargo: list[Cargo] = field(default_factory=list)
    usable_cargo_height: Float = 0.0
    usable_cargo_volume: Float = 0.0
    floor_height: Float = 0.0

    @property
    def cargo_mass(self) -> Float:
        return sum(c.mass for c in self.cargo)

    @property
    def cargo_volume(self) -> Float:
        return sum(c.volume for c in self.cargo)

    @property
    def cargo_fill_fraction(self) -> Float:
        if self.usable_cargo_volume <= 0.0:
            return 0.0
        return min(self.cargo_volume / self.usable_cargo_volume, 1.0)

    @property
    def cargo_com_height_from_floor(self) -> Float:
        if self.cargo_mass <= 0.0:
            return 0.0
        filled_height = self.usable_cargo_height * self.cargo_fill_fraction
        return filled_height / 2.0

    @property
    def cargo_com_height(self) -> Float:
        return self.cargo_com_height_from_floor + self.floor_height


@dataclass
class ConsumableCarrier:
    consumables: list[Consumable] = field(default_factory=list)

    @property
    def consumable_mass(self) -> Float:
        return sum(consumable.mass for consumable in self.consumables)

    @property
    def consumable_com_height(self) -> Float:
        if self.consumable_mass <= 0.0:
            return 0.0
        return (
            sum(consumable.mass * consumable.com_height for consumable in self.consumables)
            / self.consumable_mass
        )
