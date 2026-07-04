from source.objects.position import NodePosition, TrackPosition, TruckPosition
from source.objects.rolling_stock import RollingStockState
from source.objects.truck import TruckState
from source.objects.yard import Yard
from source.shared.types import Float

from source.shared.geometry import get_bezier_length_from_points_and_angles
from source.simulation.constants import GRAVITY


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
            return TrackPosition(position.track_id, new_distance)

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

    distribute_body_force_to_trucks(state)
    apply_brake_forces(state)
    apply_rolling_resistance(state)
    apply_gravity_forces(yard, state)

    force = sum(truck.applied_force for truck in state.trucks or [])

    state_acceleration = force / state.stock.mass if state.stock.mass > 0.0 else 0.0

    state.acceleration = state_acceleration
    state.velocity += state_acceleration * dt
    distance_delta = state.velocity * dt

    for truck_state in state.trucks or []:
        move_truck_state(yard, truck_state, distance_delta=distance_delta)

    clear_truck_forces(state)
    state.applied_force = 0.0


def sign(value: Float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def distribute_body_force_to_trucks(state: RollingStockState) -> None:

    force_per_truck = state.applied_force / state.truck_count

    for truck_state in state.trucks:
        truck_state.applied_force += force_per_truck


def apply_brake_forces(state: RollingStockState) -> None:

    braking_force = state.handbrake_force

    if state.brakes is not None:
        braking_force += state.brakes.brake_force

    if state.velocity == 0.0:
        return

    force_per_truck = braking_force / state.truck_count
    brake_direction = -sign(state.velocity)

    for truck_state in state.trucks:
        truck_state.applied_force += brake_direction * force_per_truck


def apply_gravity_forces(yard: Yard, state: RollingStockState) -> None:
    for truck_state in state.trucks:
        grade = yard.grade_at_position(truck_state.truck_position)
        mass = truck_support_mass(state)

        truck_state.applied_force -= (
            mass * GRAVITY * grade
        )  # negative due to opposing based on position


def apply_rolling_resistance(state: RollingStockState) -> None:

    if state.velocity == 0.0:
        return

    resistance_direction = -sign(state.velocity)

    for truck_state in state.trucks:
        truck_state.applied_force += (
            resistance_direction
            * truck_state.truck.rolling_resistance_per_axle
            * truck_state.truck.axle_count
        )


def clear_truck_forces(state: RollingStockState) -> None:
    for truck_state in state.trucks:
        truck_state.applied_force = 0.0


def truck_support_mass(state: RollingStockState) -> Float:
    return state.stock.mass / state.truck_count
