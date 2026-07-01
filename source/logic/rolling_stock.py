from __future__ import annotations
from dataclasses import dataclass, field

from source.logic.types import Float
from source.logic.cargo import Cargo


@dataclass
class RollingStock:
    id: str
    name: str
    length: Float
    empty_mass: Float
    condition: Float
    handbrake: bool


    rolling_resistance: Float
    automatic_brake_force: Float
    max_automatic_brake_force: Float
    handbrake_force: Float

    brake_pipe_volume: Float
    brake_pipe_pressure: Float

    front_connection: Connection
    rear_connection: Connection

    @property
    def mass(self) -> Float:
        return self.empty_mass


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
    max_fuel_mass: Float
    max_water_mass: Float

    fuel_mass: Float = 0.0
    water_mass: Float = 0.0

    @property
    def mass(self) -> Float:
        return self.empty_mass + self.fuel_mass + self.water_mass


@dataclass
class Locomotive(RollingStock):
    tractive_effort: Float
    tender: Tender | None = None
    independent_brake_force: Float = 0.0
    max_independent_brake_force: Float = 0.0


@dataclass
class Connection:
    a: RollingStock | None = None
    b: RollingStock | None = None
    brake_hose_connected: bool = False
    angle_cock_a_open: bool = False
    angle_cock_b_open: bool = False

    @property
    def can_uncouple(self) -> bool:
        return False

    @property brake_pipe_continuous(self) -> bool:
        return (
            self.brake_hose_connected
            and self.angle_cock_a_open
            and self.angle_cock_b_open
        )


@dataclass
class Coupler(Connection):
    @property
    def can_uncouple(self) -> bool:
        return True


@dataclass
class FixedConnection(Connection):
    @property
    def can_uncouple(self) -> bool:
        return False
