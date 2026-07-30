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


# public entry point
def update_rolling_stock_state(yard: Yard, state: RollingStockState, dt: Float) -> None:

    if any(truck.is_derailed for truck in state.trucks):
        return

    begin_physics_step(state)

    # baseline loads and grade reaction
    apply_gravity_and_static_loads(yard, state)

    # forces parallel and perpendicular to track
    apply_longitudinal_forces(state)
    apply_curve_forces(yard, state)

    # convert truck reactions into moments on car body
    calculate_body_moments(state)

    # moments modify wheel loading
    apply_load_transfer(yard, state)

    if check_for_derail(state):
        end_physics_step(state)
        return

    # advance body velocity and move along track
    integrate_body_motion(state, dt)
    move_trucks_with_body(yard, state, dt)

    end_physics_step(state)


# physics lifecycle
def begin_physics_step(state: RollingStockState) -> None:
    clear_truck_reactions(state)
    clear_derived_body_moments(state)


def end_physics_step(state: RollingStockState) -> None:
    state.longitudinal_force = 0.0


def clear_truck_reactions(state: RollingStockState) -> None:
    for truck_state in state.trucks:
        truck_state.longitudinal_force = 0.0
        truck_state.lateral_force = 0.0
        truck_state.left_vertical_force = 0.0
        truck_state.right_vertical_force = 0.0


def clear_derived_body_moments(state: RollingStockState) -> None:
    state.pitch_moment = 0.0
    state.yaw_moment = 0.0
    state.roll_moment = 0.0


# static loading and gravity
def apply_gravity_and_static_loads(yard: Yard, state: RollingStockState) -> None:
    for truck_state in state.trucks:
        grade = yard.grade_at_position(truck_state.truck_position)
        support_mass = truck_support_mass(state, truck_state)

        grade_scale = sqrt(1.0 + grade * grade)
        sin_grade = grade / grade_scale
        cos_grade = 1.0 / grade_scale

        grade_force = support_mass * GRAVITY * sin_grade
        vertical_force = support_mass * GRAVITY * cos_grade

        truck_state.set_vertical_force(vertical_force)
        truck_state.longitudinal_force -= grade_force


# longitudinal forces
def apply_longitudinal_forces(state: RollingStockState) -> None:
    distribute_applied_body_force(state)
    distribute_brake_force(state)
    apply_rolling_resistance(state)


def distribute_applied_body_force(state: RollingStockState) -> None:
    for truck_state in state.trucks:
        share = truck_axle_share(state, truck_state)
        truck_state.longitudinal_force += state.longitudinal_force * share


def distribute_brake_force(state: RollingStockState) -> None:
    if state.velocity == 0.0:
        return

    braking_force = state.handbrake_force

    if state.brakes is not None:
        braking_force += state.brakes.brake_force

    direction = -sign(state.velocity)

    for truck_state in state.trucks:
        share = truck_axle_share(state, truck_state)
        truck_state.longitudinal_force += direction * braking_force * share


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


# Curve forces
def apply_curve_forces(yard: Yard, state: RollingStockState) -> None:
    apply_curve_bite_force(yard, state)
    apply_lateral_curve_force(yard, state)


def apply_curve_bite_force(yard: Yard, state: RollingStockState) -> None:

    wheelbase_bite = curve_bite_from_wheelbase(yard, state)
    swivel_bite = curve_bite_from_intertruck_swivel(yard, state)
    total_bite_force = wheelbase_bite + swivel_bite

    for truck_state in state.trucks:
        share = truck_axle_share(state, truck_state)
        truck_state.longitudinal_force += total_bite_force * share


def apply_lateral_curve_force(yard: Yard, state: RollingStockState) -> None:

    for truck_state in state.trucks:
        support_mass = truck_support_mass(state, truck_state)

        truck_state.lateral_force += curve_lateral_force(
            yard, truck_state.truck_position, support_mass, state.velocity
        )


# body moments
def calculate_body_moments(state: RollingStockState) -> None:
    calculate_pitch_moment(state)
    calculate_roll_moment(state)
    # TODO distribute yaw moment into truck lateral reactions
    calculate_yaw_moment(state)


def calculate_pitch_moment(state: RollingStockState) -> None:
    total_longitudinal_force = sum(truck_state.longitudinal_force for truck_state in state.trucks)

    state.pitch_moment = state.stock.com_height * total_longitudinal_force


def calculate_roll_moment(state: RollingStockState) -> None:
    total_lateral_force = sum(truck_state.lateral_force for truck_state in state.trucks)
    state.roll_moment = state.stock.com_height * total_lateral_force


def calculate_yaw_moment(state: RollingStockState) -> None:
    state.yaw_moment = sum(
        truck_state.lateral_force * truck_state.truck.offset_from_centre
        for truck_state in state.trucks
    )


# Load Transfer
def apply_load_transfer(yard: Yard, state: RollingStockState) -> None:
    # pitch changes truck's total vertical load
    apply_pitch_moment_distribution(state)

    # roll divides lateral load using those updated loads
    apply_roll_load_transfer(yard, state)


def apply_pitch_moment_distribution(state: RollingStockState) -> None:
    if len(state.trucks) < 2:
        return

    denominator = 0.0

    for truck_state in state.trucks:
        stiffness = truck_state.truck.vertical_stiffness
        distance = truck_state.truck.offset_from_centre
        denominator += stiffness * distance * distance

    if denominator == 0.0:
        return

    for truck_state in state.trucks:
        stiffness = truck_state.truck.vertical_stiffness
        distance = truck_state.truck.offset_from_centre

        load_delta = state.pitch_moment * stiffness * distance / denominator

        truck_state.add_vertical_force(-load_delta)


def apply_roll_load_transfer(yard: Yard, state: RollingStockState) -> None:
    total_vertical_force = sum(truck_state.vertical_force for truck_state in state.trucks)
    if total_vertical_force <= 0.0:
        return
    total_transfer = state.roll_moment / yard.loading_gauge

    for truck_state in state.trucks:
        share = truck_state.vertical_force / total_vertical_force
        transfer = total_transfer * share
        truck_state.shift_vertical_force(transfer / 2.0)


# Derailment
def check_for_derail(state: RollingStockState) -> bool:
    derailed = False

    for truck_state in state.trucks:
        if truck_state.wheel_climb_ratio > DERAIL_THRESHOLD:
            truck_state.is_derailed = True
            derailed = True
    return derailed


# Motion integration
def integrate_body_motion(state: RollingStockState, dt: Float) -> None:
    total_longitudinal_force = sum(truck_state.longitudinal_force for truck_state in state.trucks)

    if state.stock.mass <= 0.0:
        state.acceleration = 0.0
        return

    state.acceleration = total_longitudinal_force / state.stock.mass
    state.velocity += state.acceleration * dt


def move_trucks_with_body(yard: Yard, state: RollingStockState, dt: Float) -> None:
    distance_delta = state.velocity * dt
    for truck_state in state.trucks:
        move_truck_state(yard, truck_state, distance_delta)


# Track position movement
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


# shared helpers
def truck_axle_share(state: RollingStockState, truck_state: TruckState) -> Float:
    total_axles = sum(current.truck.axle_count for current in state.trucks)
    if total_axles <= 0:
        return 1.0 / max(state.truck_count, 1)

    return truck_state.truck.axle_count / total_axles


def truck_support_mass(state: RollingStockState, truck_state: TruckState) -> Float:
    return state.stock.mass * truck_axle_share(state, truck_state)
