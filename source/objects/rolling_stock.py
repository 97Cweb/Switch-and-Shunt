from __future__ import annotations
from dataclasses import dataclass, field
from sqlite3 import Connection

from source.objects.truck import Truck, TruckState
from source.shared.types import Float
from source.objects.cargo import Cargo


@dataclass
class RollingStock:
    id: str
    name: str
    length: Float
    empty_mass: Float

    rolling_resistance: Float

    max_handbrake_force: Float

    front_connection: Connection
    rear_connection: Connection

    brakes: BrakeEquipment | None = None
    steam: SteamEquipment | None = None
    electrical: ElectricalEquipment | None = None
    mu: MUEquipment | None = None

    trucks: list[Truck] = field(default_factory=list)

    @property
    def mass(self) -> Float:
        return self.empty_mass


@dataclass
class RollingStockState:
    stock: RollingStock
    trucks: list[TruckState] = field(default_factory=list)
    condition: Float = 1.0
    handbrake_force: Float = 0.0
    velocity: Float = 0.0
    acceleration: Float = 0.0

    brakes: BrakeState | None = None
    steam: SteamState | None = None
    electrical: ElectricalState | None = None
    mu: MUState | None = None

    applied_force: Float = 0.0

    @classmethod
    def from_stock(cls, stock: RollingStock) -> "RollingStockState":
        return cls(stock=stock, trucks=[TruckState(truck) for truck in stock.trucks])

    def __post_init__(self):
        if self.stock.brakes is not None and self.brakes is None:
            self.brakes = BrakeState()

        if self.stock.steam is not None and self.steam is None:
            self.steam = SteamState()

        if self.stock.electrical is not None and self.electrical is None:
            self.electrical = ElectricalState()

        if self.stock.mu is not None and self.mu is None:
            self.mu = MUState()

        if self.stock.trucks is not None and len(self.trucks) == 0:
            self.trucks = [TruckState(truck=truck) for truck in self.stock.trucks]

    @property
    def truck_count(self) -> int:
        return len(self.trucks)


@dataclass
class Car(RollingStock):
    cargo: list[Cargo] = field(default_factory=list)

    @property
    def mass(self) -> Float:
        return self.empty_mass + sum(c.mass for c in self.cargo)


@dataclass
class Caboose(Car):
    pass


@dataclass
class Tender(RollingStock):
    fuel_mass: Float = 0.0
    water_mass: Float = 0.0

    max_fuel_mass: Float = 0.0
    max_water_mass: Float = 0.0

    @property
    def mass(self) -> Float:
        return self.empty_mass + self.fuel_mass + self.water_mass


@dataclass
class Locomotive(RollingStock):
    fuel_mass: Float = 0.0
    water_mass: Float = 0.0

    max_fuel_mass: Float = 0.0
    max_water_mass: Float = 0.0
    tractive_effort: Float = 0.0
    tender: Tender | None = None
    independent_brake_force: Float = 0.0
    max_independent_brake_force: Float = 0.0


@dataclass
class CarEquipment:
    pass


@dataclass
class CarEquipmentState:
    pass


@dataclass
class BrakeEquipment(CarEquipment):
    max_brake_force: Float = 0.0
    brake_pipe_volume: Float = 0.0
    reservoir_size: Float = 0.0


@dataclass
class BrakeState(CarEquipmentState):
    brake_pipe_pressure: Float = 0.0
    brake_force: Float = 0.0


@dataclass
class SteamEquipment(CarEquipment):
    max_pressure: Float


@dataclass
class SteamState(CarEquipmentState):
    pressure: Float = 0.0


@dataclass
class ElectricalEquipment(CarEquipment):
    max_voltage: Float


@dataclass
class ElectricalState(CarEquipmentState):
    voltage: Float = 0.0
    breaker_closed: bool = False


@dataclass
class MUEquipment(CarEquipment):
    pass


@dataclass
class MUState(CarEquipmentState):
    pass
