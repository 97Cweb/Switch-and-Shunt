from source.objects.coupling import Coupling
from source.objects.position import TrackPosition
from source.objects.truck import Truck
from source.simulation.physics import update_rolling_stock_state

from source.objects.rolling_stock import RollingStock, RollingStockState
from source.tests.track_test import make_test_yard


def make_test_car_state() -> RollingStockState:
    car = RollingStock(
        id="boxcar_1",
        name="Test Boxcar",
        length=12.0,
        empty_mass=10000.0,
        rolling_resistance=50.0,
        max_handbrake_force=2000.0,
        front_coupling=Coupling(),
        rear_coupling=Coupling(),
        trucks=[
            Truck(
                offset_from_centre=50,
                wheelbase=5,
                axle_count=3,
                rolling_resistance_per_axle=500,
            ),
            Truck(
                offset_from_centre=-50, wheelbase=5, axle_count=3, rolling_resistance_per_axle=500
            ),
        ],
    )
    state = RollingStockState(stock=car, condition=1.0, handbrake_force=0.0)
    for truck_state in state.trucks:
        truck_state.truck_position = TrackPosition(track_id="t1", distance_along=0.0)

    return state


def test_car_accelerates_when_force_applied():
    state = make_test_car_state()
    yard = make_test_yard()
    state.applied_force = 1000.0
    update_rolling_stock_state(yard, state, dt=1.0)

    assert state.acceleration > 0.0
    assert state.velocity > 0.0
    for truck_state in state.trucks:
        assert truck_state.truck_position.distance_along > 0.0
    print_status(state)


def test_rolling_resistance_slows_car_down():
    state = make_test_car_state()
    yard = make_test_yard()
    state.velocity = 1.0

    update_rolling_stock_state(yard, state, dt=1.0)

    assert state.acceleration < 0.0
    assert state.velocity < 1.0

    print_status(state)


def test_handbrake_slows_car_down():
    state = make_test_car_state()
    yard = make_test_yard()
    state.velocity = 1.0
    state.handbrake_force = 500.0
    update_rolling_stock_state(yard, state, dt=1.0)

    assert state.acceleration < 0.0
    assert state.velocity > 0.0
    for truck_state in state.trucks:
        assert truck_state.truck_position.distance_along > 0.0

    print_status(state)


def test_force_is_cleared_after_update():
    state = make_test_car_state()
    yard = make_test_yard()
    state.applied_force = 1000.0

    update_rolling_stock_state(yard, state, dt=1.0)
    assert state.applied_force == 0.0

    print_status(state)


def test_zero_force_car_stays_still():
    state = make_test_car_state()
    yard = make_test_yard()
    update_rolling_stock_state(yard, state, dt=1.0)
    for truck_state in state.trucks:
        assert truck_state.truck_position.distance_along == 0.0

    print_status(state)


def test_negative_force_goes_backwards():
    state = make_test_car_state()
    yard = make_test_yard()
    state.applied_force = -1000.0

    update_rolling_stock_state(yard, state, dt=1.0)
    assert state.acceleration < 0.0
    assert state.velocity < 0.0

    for truck_state in state.trucks:
        assert truck_state.truck_position.distance_along > 0.0

    print_status(state)


def test_rolling_resistance_does_not_start_car():
    state = make_test_car_state()
    yard = make_test_yard()
    state.velocity = 0.0

    update_rolling_stock_state(yard, state, dt=1.0)

    assert state.acceleration == 0.0
    assert state.velocity == 0.0

    for truck_state in state.trucks:
        assert truck_state.truck_position.distance_along == 0.0
    print_status(state)


def print_status(state):
    print(
        f"a={state.acceleration:.3f}, v={state.velocity:.3f}, x={state.trucks[0].truck_position.distance_along:.3f}"
    )


def test_all():
    test_car_accelerates_when_force_applied()
    test_force_is_cleared_after_update()
    test_handbrake_slows_car_down()
    test_rolling_resistance_slows_car_down()
    test_zero_force_car_stays_still()
    test_negative_force_goes_backwards()
    test_rolling_resistance_does_not_start_car()
