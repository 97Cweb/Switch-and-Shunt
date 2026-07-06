from dataclasses import dataclass

from source.objects.position import TruckPosition
from source.shared.types import Float


@dataclass
class Truck:
    offset_from_centre: Float
    wheel_diameter: Float
    axle_spacing: Float
    axle_count: int
    rolling_resistance_per_axle: Float

    max_swivel_angle: Float

    def __post_init__(self):
        if self.wheel_diameter <= 0.0:
            raise ValueError("wheel_diameter must be greater than 0")
        if self.axle_count < 1:
            raise ValueError("axle_counte must be at least 1")
        if self.axle_spacing < self.wheel_diameter and self.axle_count > 1:
            raise ValueError("axle_spacing must be at least wheel_diameter or wheels will overlap")

    @property
    def wheelbase(self) -> Float:
        if self.axle_count <= 1:
            return 0.0
        return self.axle_spacing * (self.axle_count - 1)


@dataclass
class TruckState:
    truck: Truck
    truck_position: TruckPosition | None = None
    longitudinal_force: Float = 0.0
    lateral_force: Float = 0.0
    vertical_force: Float = 0.0
    swivel_angle: Float | None = None
    is_derailed: bool = False

    @property
    def wheel_climb_ratio(self) -> Float:
        return abs(self.lateral_force) / self.vertical_force
