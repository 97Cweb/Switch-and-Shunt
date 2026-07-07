from math import isclose

from source.domain.infrastructure.position import TrackPosition
from source.simulation.curve_forces import (
    curve_bite_from_intertruck_swivel,
    curve_bite_from_wheelbase,
    curve_lateral_force,
)
from source.simulation.physics import update_rolling_stock_state


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
