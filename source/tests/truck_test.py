from source.objects import track, yard
from source.objects.position import NodePosition, TrackPosition
from source.objects.rolling_stock import Truck, TruckState
from source.tests.track_test import make_test_yard


def test_truck_rolls_from_track_onto_node():
    test_yard = make_test_yard()
    state = TruckState(
        truck=Truck(offset_from_centre=0.0, wheelbase=2.0, axle_count=2),
        truck_position=TrackPosition("t1", 145.0),
    )

    print(test_yard.track_length("t1"))
    test_yard.move_truck_state(state, 2.0)

    assert isinstance(state.truck_position, NodePosition)
    assert state.truck_position.node_id == "sw1"
    assert state.truck_position.entered_from_port_id == "root"
    print(state.truck_position.distance_along)


def test_truck_rolls_from_node_to_next_track():

    test_yard = make_test_yard()
    state = TruckState(
        truck=Truck(offset_from_centre=0.0, wheelbase=2.0, axle_count=2),
        truck_position=NodePosition("sw1", "root", 1.0),
    )
    print(test_yard.node_route_length_from_port("sw1", "root"))
    test_yard.move_truck_state(state, -2.0)
    assert isinstance(state.truck_position, TrackPosition)
    assert state.truck_position.track_id == "t1"


def test_car_rolls_two_trucks_across_tracks():
    pass


def test_all():
    test_truck_rolls_from_node_to_next_track()
    test_truck_rolls_from_track_onto_node()
