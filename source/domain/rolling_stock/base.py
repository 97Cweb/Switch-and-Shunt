from abc import ABC
from dataclasses import dataclass, field

from source.domain.rolling_stock.coupling import Coupling
from source.domain.rolling_stock.equipment import (
    BrakeEquipment,
    BrakeState,
    ElectricalEquipment,
    ElectricalState,
    MUEquipment,
    MUState,
    SteamEquipment,
    SteamState,
)
from source.domain.rolling_stock.truck import Truck, TruckState
from source.shared.types import Float


def weighted_com_height(*items: tuple[Float, Float]) -> Float:
    valid_items = [(mass, height) for mass, height in items if mass > 0.0]
    total_mass = sum(mass for mass, _height in valid_items)

    if total_mass <= 0.0:
        return 0.0

    return sum(mass * height for mass, height in valid_items) / total_mass


@dataclass
class RollingStock(ABC):
    id: str
    name: str
    length: Float
    empty_mass: Float
    empty_com_height: Float

    rolling_resistance: Float

    max_handbrake_force: Float

    front_coupling: Coupling
    rear_coupling: Coupling

    brakes: BrakeEquipment | None = None
    steam: SteamEquipment | None = None
    electrical: ElectricalEquipment | None = None
    mu: MUEquipment | None = None

    trucks: list[Truck] = field(default_factory=list)

    @property
    def mass(self) -> Float:
        return self.empty_mass

    @property
    def com_height(self) -> Float:
        return self.empty_com_height


@dataclass
class RollingStockState:
    stock: RollingStock
    trucks: list[TruckState] = field(default_factory=list)
    condition: Float = 1.0
    handbrake_force: Float = 0.0
    velocity: Float = 0.0
    acceleration: Float = 0.0
    pitch_moment: Float = 0.0
    yaw_moment: Float = 0.0
    roll_moment: Float = 0.0

    brakes: BrakeState | None = None
    steam: SteamState | None = None
    electrical: ElectricalState | None = None
    mu: MUState | None = None

    longitudinal_force: Float = 0.0

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
