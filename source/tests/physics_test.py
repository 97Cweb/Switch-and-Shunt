from source.simulation.physics import update_rolling_stock

from source.objects.rolling_stock import RollingStock, RollingStockState, Coupler


def make_test_car_state() -> RollingStockState:
    car = RollingStock(
        id="boxcar_1",
        name="Test Boxcar",
        length=12.0,
        empty_mass=10000.0,
        rolling_resistance=50.0,
        max_handbrake_force=2000.0,
        front_connection=Coupler(),
        rear_connection=Coupler(),
    )
    return RollingStockState(
        stock=car,
        condition=1.0,
        handbrake_force=0.0,
        track_id="t1",
    )


def test_car_accelerates_when_force_applied():
    state = make_test_car_state()
    state.applied_force = 1000.0
    update_rolling_stock(state, dt=1.0)

    assert state.acceleration > 0.0
    assert state.velocity > 0.0
    assert state.distance > 0.0
    print_status(state)


def test_rolling_resistance_slows_car_down():
    state = make_test_car_state()
    state.velocity = 1.0

    update_rolling_stock(state, dt=1.0)

    assert state.acceleration < 0.0
    assert state.velocity < 1.0

    print_status(state)


def test_handbrake_slows_car_down():
    state = make_test_car_state()
    state.velocity = 1.0
    state.handbrake_force = 500.0
    update_rolling_stock(state, dt=1.0)

    assert state.acceleration < 0.0
    assert state.velocity > 0.0
    assert state.distance > 0.0

    print_status(state)


def test_force_is_cleared_after_update():
    state = make_test_car_state()
    state.applied_force = 1000.0

    update_rolling_stock(state, dt=1.0)
    assert state.applied_force == 0.0

    print_status(state)


def test_zero_force_car_stays_still():
    state = make_test_car_state()
    update_rolling_stock(state, dt=1.0)
    assert state.distance == 0.0

    print_status(state)


def test_negative_force_goes_backwards():
    state = make_test_car_state()
    state.applied_force = -1000.0

    update_rolling_stock(state, dt=1.0)
    assert state.acceleration < 0.0
    assert state.velocity < 0.0
    assert state.distance < 0.0

    print_status(state)


def test_rolling_resistance_does_not_start_car():
    state = make_test_car_state()
    state.velocity = 0.0

    update_rolling_stock(state, dt=1.0)

    assert state.acceleration == 0.0
    assert state.velocity == 0.0
    assert state.distance == 0.0
    print_status(state)


def print_status(state):
    print(f"a={state.acceleration:.3f}, v={state.velocity:.3f}, x={state.distance:.3f}")


def test_all():
    test_car_accelerates_when_force_applied()
    test_force_is_cleared_after_update()
    test_handbrake_slows_car_down()
    test_rolling_resistance_slows_car_down()
    test_zero_force_car_stays_still()
    test_negative_force_goes_backwards()
    test_rolling_resistance_does_not_start_car()
