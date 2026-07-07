from dataclasses import dataclass

from source.domain.infrastructure.position import TruckPosition
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
    _left_vertical_force: Float = 0.0
    _right_vertical_force: Float = 0.0
    swivel_angle: Float | None = None
    is_derailed: bool = False

    @property
    def wheel_climb_ratio(self) -> Float:
        vertical_force = self.climbing_side_vertical_force
        if vertical_force <= 0.0:
            return 0.0
        return abs(self.lateral_force) / vertical_force

    @property
    def climbing_side_vertical_force(self) -> Float:
        if self.lateral_force > 0.0:
            return self.left_vertical_force
        if self.lateral_force < 0.0:
            return self.right_vertical_force
        return self.vertical_force

    @property
    def vertical_force(self) -> Float:
        return self.left_vertical_force + self.right_vertical_force

    @property
    def left_vertical_force(self) -> Float:
        return self._left_vertical_force

    @left_vertical_force.setter
    def left_vertical_force(self, value: Float) -> None:
        self._left_vertical_force = max(0.0, value)

    @property
    def right_vertical_force(self) -> Float:
        return self._right_vertical_force

    @right_vertical_force.setter
    def right_vertical_force(self, value: Float) -> None:
        self._right_vertical_force = max(0.0, value)

    def set_vertical_force(self, total_force: Float) -> None:
        force = max(0.0, total_force) / 2.0
        self.left_vertical_force = force
        self.right_vertical_force = force

    def add_vertical_force(self, delta) -> None:
        self.left_vertical_force += delta / 2.0
        self.right_vertical_force += delta / 2.0

    def shift_vertical_force(self, delta) -> None:
        self.left_vertical_force -= delta
        self.right_vertical_force += delta
