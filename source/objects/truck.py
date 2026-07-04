from dataclasses import dataclass

from source.objects.position import TruckPosition
from source.shared.types import Float


@dataclass
class Truck:
    offset_from_centre: Float
    wheelbase: Float
    axle_count: int
    rolling_resistance_per_axle: Float

    can_swivel: bool = True
    swivel_angle: Float | None = None
    max_swivel_angle: Float | None = None


@dataclass
class TruckState:
    truck: Truck
    truck_position: TruckPosition | None = None
    applied_force: Float = 0.0
    is_derailed: bool = False
