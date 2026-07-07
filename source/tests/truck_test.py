import pytest
from math import isclose

from source.domain.infrastructure.position import NodePosition, TrackPosition
from source.domain.rolling_stock import Truck, TruckState
from source.simulation import physics
from source.tests.track_test import make_test_yard


@pytest.fixture
def yard():
    return make_test_yard()

def make_truck_state() -> TruckState:
    return TruckState(
        truck=Truck(
            offset_from_centre=0.0,
            wheel_diameter=1.0,
            axle_spacing=2.5,
            axle_count=2,
            max_swivel_angle=5,
            rolling_resistance_per_axle=500,
        )
    )


def test_truck_rolls_from_track_onto_node(yard):
    state = TruckState(
        truck=Truck(
            offset_from_centre=0.0,
            wheel_diameter=1.0,
            axle_spacing=2.5,
            axle_count=2,
            max_swivel_angle=5,
            rolling_resistance_per_axle=500,
        ),
        truck_position=TrackPosition(track_id="t1", distance_along=145.0),
    )

    physics.move_truck_state(yard, state, 2.0)

    assert isinstance(state.truck_position, NodePosition)
    assert state.truck_position.node_id == "sw1"
    assert state.truck_position.entered_from_port_id == "root"


def test_truck_rolls_from_node_to_next_track(yard):

    state = TruckState(
        truck=Truck(
            offset_from_centre=0.0,
            wheel_diameter=1.0,
            axle_spacing=2.5,
            axle_count=2,
            max_swivel_angle=5,
            rolling_resistance_per_axle=500,
        ),
        truck_position=NodePosition(node_id="sw1", entered_from_port_id="root", distance_along=1.0),
    )
    physics.move_truck_state(yard, state, -2.0)
    assert isinstance(state.truck_position, TrackPosition)
    assert state.truck_position.track_id == "t1"


def test_car_rolls_two_trucks_across_tracks():
    pass


def test_vertical_force_is_sum_of_left_and_right():
    state = make_truck_state()

    state.left_vertical_force = 10.0
    state.right_vertical_force = 15.0

    assert state.vertical_force == 25.0


def test_vertical_forces_cannot_go_negative():
    state = make_truck_state()

    state.left_vertical_force = -10.0
    state.right_vertical_force = -20.0

    assert state.left_vertical_force == 0.0
    assert state.right_vertical_force == 0.0
    assert state.vertical_force == 0.0


def test_set_vertical_force_splits_evenly():
    state = make_truck_state()

    state.set_vertical_force(100.0)

    assert state.left_vertical_force == 50.0
    assert state.right_vertical_force == 50.0
    assert state.vertical_force == 100.0


def test_add_vertical_force_changes_total_by_delta():
    state = make_truck_state()
    state.set_vertical_force(100.0)

    state.add_vertical_force(40.0)

    assert state.left_vertical_force == 70.0
    assert state.right_vertical_force == 70.0
    assert state.vertical_force == 140.0


def test_shift_vertical_force_moves_load_side_to_side():
    state = make_truck_state()
    state.set_vertical_force(100.0)

    state.shift_vertical_force(10.0)

    assert state.left_vertical_force == 40.0
    assert state.right_vertical_force == 60.0
    assert state.vertical_force == 100.0


def test_wheel_climb_uses_climbing_side_load():
    state = make_truck_state()
    state.left_vertical_force = 25.0
    state.right_vertical_force = 75.0
    state.lateral_force = 50.0

    assert isclose(state.wheel_climb_ratio, 2.0)
