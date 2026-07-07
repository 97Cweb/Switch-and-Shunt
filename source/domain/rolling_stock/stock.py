from __future__ import annotations
from dataclasses import dataclass

from source.domain.rolling_stock.base import RollingStock, weighted_com_height
from source.domain.rolling_stock.carriers import CargoCarrier, ConsumableCarrier
from source.domain.rolling_stock.equipment import AirEquipment
from source.shared.types import Float


@dataclass
class Car(CargoCarrier, RollingStock):
    @property
    def mass(self) -> Float:
        return self.empty_mass + self.cargo_mass

    @property
    def com_height(self) -> Float:
        return weighted_com_height(
            (self.empty_mass, self.empty_com_height), (self.cargo_mass, self.cargo_com_height)
        )


@dataclass
class Locomotive(ConsumableCarrier, RollingStock):
    air: AirEquipment | None = None
    tractive_effort: Float = 0.0
    independent_brake_force: Float = 0.0
    max_independent_brake_force: Float = 0.0

    tender: Tender | None = None

    @property
    def mass(self) -> Float:
        return self.empty_mass + self.consumable_mass

    @property
    def com_height(self) -> Float:
        return weighted_com_height(
            (self.empty_mass, self.empty_com_height),
            (self.consumable_mass, self.consumable_com_height),
        )


@dataclass
class Tender(ConsumableCarrier, RollingStock):
    @property
    def mass(self) -> Float:
        return self.empty_mass + self.consumable_mass

    @property
    def com_height(self) -> Float:
        return weighted_com_height(
            (self.empty_mass, self.empty_com_height),
            (self.consumable_mass, self.consumable_com_height),
        )


@dataclass
class Caboose(RollingStock):
    pass
