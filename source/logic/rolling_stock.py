from __future__ import annotations
from _typeshed import DataclassInstance
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

    trucks: list[Truck] = field(default_factory=list)

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
    fuel_mass: Float = 0.0
    water_mass: Float = 0.0

    max_fuel_mass: Float = 0.0
    max_water_mass: Float = 0.0

    @property
    def mass(self) -> Float:
        return self.empty_mass + self.fuel_mass + self.water_mass


@dataclass
class Locomotive(RollingStock):
    tractive_effort: Float = 0.0
    tender: Tender | None = None
    independent_brake_force: Float = 0.0
    max_independent_brake_force: Float = 0.0


@dataclass
class ServiceConnection:
    connected: bool = False


@dataclass
class BrakeLine(ServiceConnection):
    valve_a_open: bool = False
    valve_b_open: bool = False


@dataclass
class SteamLine(ServiceConnection):
    valve_a_open: bool = False
    valve_b_open: bool = False


@dataclass
class ElectricalJumper(ServiceConnection):
    voltage: Float = 0.0
    breaker_closed: bool = False


@dataclass
class MUJumper(ServiceConnection):
    connected: bool = False


@dataclass
class Connection:
    a: RollingStock | None = None
    b: RollingStock | None = None
    slack: Float = 0.025  # m
    position: Float = 0.0
    max_tension_force: Float = 0.0
    max_compression_force: Float = 0.0
    a_knuckle_open: bool = True  # whether connections are open. knuckle open or not
    b_knucle_open: bool = True  # whether connections are open. knuckle open or not
    brakeline: BrakeLine | None = None
    steam: SteamLine | None = None
    electrical: ElectricalJumper | None = None
    mu: MUJumper | None = None

    @property
    def can_uncouple(self) -> bool:
        return False

    @property
    def brake_pipe_continuous(self) -> bool:
        if self.brakeline:
            return (
                self.brakeline.connected
                and self.brakeline.valve_a_open
                and self.brakeline.valve_b_open
            )
        else:
            return False


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


@dataclass
class Truck:
    offset: Float
    wheelbase: Float
    axle_count: int

    can_swivel: bool = True
    swivel_angle: Float | None = None
    max_swivel_angle: Float | None = None
