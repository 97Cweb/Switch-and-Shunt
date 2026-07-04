from dataclasses import dataclass

from source.objects.rolling_stock import RollingStock
from source.shared.types import Float


@dataclass
class ServiceConnection:
    connected: bool = False


@dataclass
class MUConnection(ServiceConnection):
    pass


@dataclass
class ElectricalConnection(ServiceConnection):
    pass


@dataclass
class SteamConnection(ServiceConnection):
    valve_a_open: bool = False
    valve_b_open: bool = False


@dataclass
class BrakeConnection(ServiceConnection):
    valve_a_open: bool = False
    valve_b_open: bool = False


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
    brakeline: BrakeConnection | None = None
    steam: SteamConnection | None = None
    electrical: ElectricalConnection | None = None
    mu: MUConnection | None = None

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
