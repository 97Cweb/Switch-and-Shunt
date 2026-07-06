import pytest

from source.objects.position import NodePosition, TrackPosition
from source.objects.rolling_stock import Truck, TruckState
from source.simulation import physics
from source.tests.track_test import make_test_yard


@pytest.fixture
def yard():
    return make_test_yard()


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
