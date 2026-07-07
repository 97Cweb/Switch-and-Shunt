from math import isclose

from source.domain.infrastructure.position import TrackPosition
from source.simulation.curve_forces import (
    curve_bite_from_intertruck_swivel,
    curve_bite_from_wheelbase,
    curve_lateral_force,
)
from source.simulation.physics import update_rolling_stock_state

from source.simulation.physics import (
    apply_gravity_forces,
    apply_pitch_load_transfer,
    apply_roll_load_transfer,
    apply_yaw_moment_from_trucks,
    check_for_derail,
)
from source.simulation.constants import DERAIL_THRESHOLD, GRAVITY


def test_car_accelerates_when_force_applied(yard, straight_car_state):
    straight_car_state.longitudinal_force = 1000.0
    update_rolling_stock_state(yard, straight_car_state, dt=1.0)

    assert straight_car_state.acceleration > 0.0
    assert straight_car_state.velocity > 0.0
    for truck_state in straight_car_state.trucks:
        assert truck_state.truck_position.distance_along > 0.0


def test_rolling_resistance_slows_car_down(yard, straight_car_state):
    straight_car_state.velocity = 1.0

    update_rolling_stock_state(yard, straight_car_state, dt=1.0)

    assert straight_car_state.acceleration < 0.0
    assert straight_car_state.velocity < 1.0


def test_handbrake_slows_car_down(yard, straight_car_state):
    straight_car_state.velocity = 1.0
    straight_car_state.handbrake_force = 500.0
    update_rolling_stock_state(yard, straight_car_state, dt=1.0)

    assert straight_car_state.acceleration < 0.0
    assert straight_car_state.velocity > 0.0
    for truck_state in straight_car_state.trucks:
        assert truck_state.truck_position.distance_along > 0.0


def test_force_is_cleared_after_update(yard, straight_car_state):
    straight_car_state.longitudinal_force = 1000.0

    update_rolling_stock_state(yard, straight_car_state, dt=1.0)
    assert straight_car_state.longitudinal_force == 0.0


def test_zero_force_car_stays_still(yard, straight_car_state):
    update_rolling_stock_state(yard, straight_car_state, dt=1.0)
    for truck_state in straight_car_state.trucks:
        assert truck_state.truck_position.distance_along == 0.0


def test_negative_force_goes_backwards(yard, straight_car_state):
    straight_car_state.longitudinal_force = -1000.0

    update_rolling_stock_state(yard, straight_car_state, dt=1.0)
    assert straight_car_state.acceleration < 0.0
    assert straight_car_state.velocity < 0.0

    for truck_state in straight_car_state.trucks:
        assert truck_state.truck_position.distance_along > 0.0


def test_rolling_resistance_does_not_start_car(yard, straight_car_state):
    straight_car_state.velocity = 0.0

    update_rolling_stock_state(yard, straight_car_state, dt=1.0)

    assert straight_car_state.acceleration == 0.0
    assert straight_car_state.velocity == 0.0

    for truck_state in straight_car_state.trucks:
        assert truck_state.truck_position.distance_along == 0.0


def test_curve_lateral_force_is_zero_when_track_is_straight(yard):
    force = curve_lateral_force(
        yard=yard,
        position=TrackPosition(track_id="t1", distance_along=0.0),
        mass=1000.0,
        velocity=10.0,
    )
    assert isclose(force, 0.0, abs_tol=0.000001)


def test_curve_lateral_force_increases_with_velocity_squared(yard):
    position = TrackPosition(track_id="t3", distance_along=10.0)

    slow_force = curve_lateral_force(yard=yard, position=position, mass=1000.0, velocity=1.0)

    fast_force = curve_lateral_force(yard=yard, position=position, mass=1000.0, velocity=2.0)
    if slow_force != 0.0:
        assert isclose(fast_force, slow_force * 4.0, rel_tol=0.000001)
    else:
        raise ValueError("bad test, no curve")


def test_wheelbase_curve_bite_opposes_forward_velocity(yard, curved_car_state):
    curved_car_state.velocity = 1.0

    bite_force = curve_bite_from_wheelbase(yard, curved_car_state)

    assert bite_force < 0.0


def test_wheelbase_curve_bite_opposes_reverse_velocity(yard, curved_car_state):
    curved_car_state.velocity = -1.0

    bite_force = curve_bite_from_wheelbase(yard, curved_car_state)

    assert bite_force > 0.0


def test_intertruck_swivel_bite_is_zero_with_unlimited_swivel(yard, curved_car_state):
    curved_car_state.velocity = 1.0

    for truck_state in curved_car_state.trucks:
        truck_state.truck.max_swivel_angle = 90

    bite_force = curve_bite_from_intertruck_swivel(yard, curved_car_state)

    assert isclose(bite_force, 0.0, abs_tol=0.000001)


def test_intertruck_swivel_bite_opposes_forward_velocity(yard, curved_car_state):
    curved_car_state.velocity = 1.0

    for truck_state in curved_car_state.trucks:
        truck_state.truck.max_swivel_angle = 0.0

    bite_force = curve_bite_from_intertruck_swivel(yard, curved_car_state)

    assert bite_force < 0.0


def test_gravity_sets_even_left_right_vertical_load(yard, straight_car_state):
    apply_gravity_forces(yard, straight_car_state)

    for truck_state in straight_car_state.trucks:
        assert truck_state.vertical_force > 0.0
        assert isclose(
            truck_state.left_vertical_force,
            truck_state.right_vertical_force,
            rel_tol=0.000001,
        )


def test_pitch_load_transfer_moves_weight_between_front_and_rear(straight_car_state):
    front = max(
        straight_car_state.trucks,
        key=lambda truck_state: truck_state.truck.offset_from_centre,
    )
    rear = min(
        straight_car_state.trucks,
        key=lambda truck_state: truck_state.truck.offset_from_centre,
    )

    front.set_vertical_force(100.0)
    rear.set_vertical_force(100.0)

    straight_car_state.pitch_moment = 1000.0
    apply_pitch_load_transfer(straight_car_state)

    assert front.vertical_force < 100.0
    assert rear.vertical_force > 100.0
    assert isclose(front.vertical_force + rear.vertical_force, 200.0, rel_tol=0.000001)


def test_roll_load_transfer_moves_load_left_to_right(yard, straight_car_state):
    for truck_state in straight_car_state.trucks:
        truck_state.set_vertical_force(100.0)

    straight_car_state.roll_moment = yard.loading_gauge * 20.0

    apply_roll_load_transfer(yard, straight_car_state)

    for truck_state in straight_car_state.trucks:
        assert truck_state.left_vertical_force < 50.0
        assert truck_state.right_vertical_force > 50.0
        assert isclose(truck_state.vertical_force, 100.0, rel_tol=0.000001)


def test_derail_uses_left_right_vertical_load(straight_car_state):
    truck_state = straight_car_state.trucks[0]
    truck_state.left_vertical_force = 10.0
    truck_state.right_vertical_force = 1000.0
    truck_state.lateral_force = DERAIL_THRESHOLD * 10.0 + 1.0

    check_for_derail(straight_car_state)

    assert truck_state.is_derailed


def test_yaw_moment_is_created_by_lateral_force_at_offset(straight_car_state):
    front = max(
        straight_car_state.trucks,
        key=lambda truck_state: truck_state.truck.offset_from_centre,
    )
    rear = min(
        straight_car_state.trucks,
        key=lambda truck_state: truck_state.truck.offset_from_centre,
    )

    front.lateral_force = 10.0
    rear.lateral_force = 0.0

    apply_yaw_moment_from_trucks(straight_car_state)

    assert straight_car_state.yaw_moment != 0.0


def test_equal_lateral_forces_on_symmetric_trucks_create_no_yaw(straight_car_state):
    for truck_state in straight_car_state.trucks:
        truck_state.lateral_force = 10.0

    apply_yaw_moment_from_trucks(straight_car_state)

    assert isclose(straight_car_state.yaw_moment, 0.0, abs_tol=0.000001)
