from math import radians

from source.domain.infrastructure.position import TruckPosition
from source.domain.rolling_stock import RollingStockState
from source.domain.infrastructure.yard import Yard
from source.shared.math import sign
from source.shared.types import Float
from source.simulation.constants import CURVE_BITE_COEFFICIENT


def curve_lateral_force(
    yard: Yard, position: TruckPosition | None, mass: Float, velocity: Float
) -> Float:
    curvature = yard.curvature_at_position(position)

    lateral_acceleration = velocity**2 * curvature
    lateral_force = mass * lateral_acceleration
    return lateral_force


def curve_bite_from_wheelbase(yard: Yard, state: RollingStockState) -> Float:
    direction = -sign(state.velocity)
    total_bite_force = 0.0

    for truck_state in state.trucks:
        curvature = yard.curvature_at_position(truck_state.truck_position)

        truck = truck_state.truck

        # angle needed for truck to fit curve
        required_angle = abs(curvature) * truck.wheelbase

        bite_force = direction * required_angle * CURVE_BITE_COEFFICIENT * truck.axle_count

        total_bite_force += bite_force

    return total_bite_force


def curve_bite_from_intertruck_swivel(yard: Yard, state: RollingStockState) -> Float:
    direction = -sign(state.velocity)

    truck_states = sorted(
        state.trucks, key=lambda truck_state: truck_state.truck.offset_from_centre
    )
    if len(truck_states) < 2:  # only 1 truck, no intertruck forces
        return 0.0

    # get curvature at all trucks
    curvatures = [
        yard.curvature_at_position(truck_state.truck_position) for truck_state in state.trucks
    ]

    if not curvatures:
        return 0.0

    average_curvature = abs(sum(curvatures) / len(curvatures))

    total_excess_angle = 0.0

    for index, truck_state in enumerate(truck_states):
        truck = truck_state.truck

        required_angle = 0.0

        # check against previous truck
        if index > 0:
            previous_truck = truck_states[index - 1].truck

            previous_offset = previous_truck.offset_from_centre
            current_offset = truck.offset_from_centre

            previous_span = abs(current_offset - previous_offset)

            required_angle += (
                average_curvature * previous_span / 2.0
            )  # get angle needed to fit the truck span, divide by 2 as next truck will take the other half

        # span to next truck
        if index < len(truck_states) - 1:
            next_truck = truck_states[index + 1].truck

            current_offset = truck.offset_from_centre
            next_offset = next_truck.offset_from_centre

            next_span = abs(next_offset - current_offset)

            required_angle += (
                average_curvature * next_span / 2.0
            )  # get angle needed to fit the truck span, divide by 2 as next previous truck will take the other half

        max_angle = radians(truck.max_swivel_angle)

        excess_angle = max(0.0, required_angle - max_angle)
        total_excess_angle += excess_angle

    return direction * total_excess_angle * CURVE_BITE_COEFFICIENT
