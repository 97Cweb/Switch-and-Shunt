from math import sqrt

from source.domain.infrastructure.position import NodePosition, TrackPosition, TruckPosition
from source.domain.rolling_stock import RollingStockState
from source.domain.rolling_stock.truck import TruckState
from source.domain.infrastructure.yard import Yard
from source.shared.math import sign
from source.shared.types import Float

from source.shared.geometry import get_bezier_length_from_points_and_angles
from source.simulation.constants import BLOCKED_PORT, DERAIL_THRESHOLD, EXIT_PORT, GRAVITY
from source.simulation.curve_forces import (
    curve_bite_from_intertruck_swivel,
    curve_bite_from_wheelbase,
    curve_lateral_force,
)


def move_truck_state(yard: Yard, truck_state: TruckState, distance_delta: Float) -> None:
    if truck_state.truck_position is None:
        return
    truck_state.truck_position = moved_truck_position(
        yard, truck_state.truck_position, distance_delta
    )


def moved_truck_position(
    yard: Yard, position: TruckPosition, distance_delta: Float
) -> TruckPosition | None:
    if isinstance(position, TrackPosition):
        length = yard.track_length(position.track_id)
        new_distance = position.distance_along + distance_delta

        if 0.0 <= new_distance <= length:
            return TrackPosition(position.track_id, distance_along=new_distance)

        if new_distance > length:
            track = yard.tracks[position.track_id]

            return NodePosition(
                node_id=track.b.node_id,
                entered_from_port_id=track.b.port_id,
                distance_along=new_distance - length,
            )
        if new_distance < 0.0:
            track = yard.tracks[position.track_id]

            node_id = track.a.node_id
            entered_port_id = track.a.port_id

            route_length = yard.node_route_length_from_port(node_id, entered_port_id)
            if route_length is None:
                return None

            return NodePosition(
                node_id=node_id,
                entered_from_port_id=entered_port_id,
                distance_along=route_length + new_distance,
            )

    if isinstance(position, NodePosition):
        node = yard.nodes[position.node_id]

        route = node.active_route_from_port(position.entered_from_port_id)

        if route is None:
            return None

        route_length = get_bezier_length_from_points_and_angles(
            *node.get_route_geometry(route, yard.loading_gauge)
        )

        new_distance = position.distance_along + distance_delta

        if 0.0 <= new_distance <= route_length:
            return NodePosition(
                node_id=position.node_id,
                entered_from_port_id=position.entered_from_port_id,
                distance_along=new_distance,
            )

        exit_port_id = node.next_port(position.entered_from_port_id)

        if exit_port_id is None:
            return None

        if exit_port_id == EXIT_PORT:
            # todo validate train, remove train from yard, bounce otherwise

            return None

        if exit_port_id == BLOCKED_PORT:
            # buffer, hard stop
            return NodePosition(
                node_id=position.node_id,
                entered_from_port_id=position.entered_from_port_id,
                distance_along=route_length,
            )

        next_track_id = yard.get_connected_track_id_from_port_id(position.node_id, exit_port_id)
        if next_track_id is None:
            return None

        if new_distance > route_length:
            return TrackPosition(track_id=next_track_id, distance_along=new_distance - route_length)

        if new_distance < 0.0:
            previous_track_id = yard.get_connected_track_id_from_port_id(
                position.node_id, position.entered_from_port_id
            )

            if previous_track_id is None:
                return None

            previous_track_length = yard.track_length(previous_track_id)

            return TrackPosition(
                track_id=previous_track_id, distance_along=previous_track_length + new_distance
            )

    return None


def update_rolling_stock_state(yard: Yard, state: RollingStockState, dt: Float) -> None:

    if any(truck.is_derailed for truck in state.trucks):
        return

    clear_truck_forces(state)

    apply_body_forces_to_trucks(state)
    apply_track_forces_to_trucks(yard, state)
    apply_body_moments_from_trucks(state)
    apply_load_transfer_from_body_moments(yard, state)

    check_for_derail(state)
    update_body_from_truck_reactions(state, dt)
    move_trucks_with_body(yard, state, dt)
    clear_rolling_stock_forces(state)


def apply_body_forces_to_trucks(state: RollingStockState) -> None:
    distribute_longitudinal_body_force_to_trucks(state)
    distribute_brake_forces_to_trucks(state)


def apply_body_moments_from_trucks(state: RollingStockState) -> None:
    apply_roll_moment_from_lateral_force(state)
    apply_yaw_moment_from_trucks(state)
    apply_pitch_moment_from_longitudinal_force(state)


def apply_track_forces_to_trucks(yard: Yard, state: RollingStockState) -> None:
    apply_gravity_forces(yard, state)
    apply_rolling_resistance(state)
    apply_curve_bite_forces(yard, state)
    apply_centrifugal_forces(yard, state)


def update_body_from_truck_reactions(state: RollingStockState, dt: Float) -> None:
    force = sum(truck_state.longitudinal_force for truck_state in state.trucks)
    state.acceleration = force / state.stock.mass if state.stock.mass > 0.0 else 0.0
    state.velocity += state.acceleration * dt


def apply_load_transfer_from_body_moments(yard: Yard, state: RollingStockState) -> None:
    apply_pitch_load_transfer(state)
    apply_roll_load_transfer(yard, state)


def apply_pitch_load_transfer(state: RollingStockState) -> None:
    trucks = sorted(state.trucks, key=lambda truck_state: truck_state.truck.offset_from_centre)
    if len(trucks) < 2:
        return

    front = trucks[-1]
    rear = trucks[0]

    wheelbase = front.truck.offset_from_centre - rear.truck.offset_from_centre
    if wheelbase == 0.0:
        return

    load_delta = state.pitch_moment / wheelbase
    front.add_vertical_force(-load_delta)
    rear.add_vertical_force(load_delta)


def apply_roll_load_transfer(yard: Yard, state: RollingStockState) -> None:
    total_vertical_force = sum(truck_state.vertical_force for truck_state in state.trucks)
    if total_vertical_force <= 0.0:
        return
    total_transfer = state.roll_moment / yard.loading_gauge

    for truck_state in state.trucks:
        share = truck_state.vertical_force / total_vertical_force
        transfer = total_transfer * share
        truck_state.shift_vertical_force(transfer / 2.0)


def move_trucks_with_body(yard: Yard, state: RollingStockState, dt: Float) -> None:
    distance_delta = state.velocity * dt
    for truck_state in state.trucks:
        move_truck_state(yard, truck_state, distance_delta)


def distribute_longitudinal_body_force_to_trucks(state: RollingStockState) -> None:

    force_per_truck = state.longitudinal_force / state.truck_count

    for truck_state in state.trucks:
        truck_state.longitudinal_force += force_per_truck


def distribute_brake_forces_to_trucks(state: RollingStockState) -> None:

    braking_force = state.handbrake_force

    if state.brakes is not None:
        braking_force += state.brakes.brake_force

    if state.velocity == 0.0:
        return

    force_per_truck = braking_force / state.truck_count
    brake_direction = -sign(state.velocity)

    for truck_state in state.trucks:
        truck_state.longitudinal_force += brake_direction * force_per_truck


def apply_gravity_forces(yard: Yard, state: RollingStockState) -> None:
    for truck_state in state.trucks:
        grade = yard.grade_at_position(truck_state.truck_position)
        mass = truck_support_mass(state, truck_state)

        truck_state.longitudinal_force -= (
            mass * GRAVITY * grade
        )  # negative due to opposing based on position

        truck_state.set_vertical_force(mass * GRAVITY * sqrt(max(0.0, 1.0 - grade * grade)))


def apply_rolling_resistance(state: RollingStockState) -> None:

    if state.velocity == 0.0:
        return

    resistance_direction = -sign(state.velocity)

    for truck_state in state.trucks:
        truck_state.longitudinal_force += (
            resistance_direction
            * truck_state.truck.rolling_resistance_per_axle
            * truck_state.truck.axle_count
        )


def apply_curve_bite_forces(yard: Yard, state: RollingStockState) -> None:

    bite_force = curve_bite_from_wheelbase(yard, state) + curve_bite_from_intertruck_swivel(
        yard, state
    )
    force_per_truck = bite_force / state.truck_count

    for truck_state in state.trucks:
        truck_state.longitudinal_force += force_per_truck


def apply_centrifugal_forces(yard: Yard, state: RollingStockState) -> None:

    for truck_state in state.trucks:
        mass_per_truck = truck_support_mass(state, truck_state)

        truck_state.lateral_force += curve_lateral_force(
            yard, truck_state.truck_position, mass_per_truck, state.velocity
        )


def apply_roll_moment_from_lateral_force(state: RollingStockState) -> None:
    total_lateral_force = sum(truck.lateral_force for truck in state.trucks)
    state.roll_moment += state.stock.com_height * total_lateral_force


def apply_yaw_moment_from_trucks(state: RollingStockState) -> None:
    for truck_state in state.trucks:
        offset = truck_state.truck.offset_from_centre
        state.yaw_moment += truck_state.lateral_force * offset


def apply_pitch_moment_from_longitudinal_force(state: RollingStockState) -> None:
    total_longitudinal_force = sum(truck_state.longitudinal_force for truck_state in state.trucks)

    state.pitch_moment += state.stock.com_height * total_longitudinal_force


def clear_truck_forces(state: RollingStockState) -> None:
    for truck_state in state.trucks:
        truck_state.longitudinal_force = 0.0
        truck_state.lateral_force = 0.0
        truck_state.left_vertical_force = 0.0
        truck_state.right_vertical_force = 0.0


def clear_rolling_stock_forces(state: RollingStockState) -> None:
    state.longitudinal_force = 0.0
    state.pitch_moment = 0.0
    state.roll_moment = 0.0
    state.yaw_moment = 0.0


def truck_support_mass(state: RollingStockState, truck_state: TruckState) -> Float:
    total_axles = sum(ts.truck.axle_count for ts in state.trucks)

    if total_axles <= 0:
        return state.stock.mass / max(state.truck_count, 1)

    return state.stock.mass * truck_state.truck.axle_count / total_axles


def check_for_derail(state: RollingStockState) -> None:
    for truck_state in state.trucks:
        if truck_state.wheel_climb_ratio > DERAIL_THRESHOLD:
            truck_state.is_derailed = True
