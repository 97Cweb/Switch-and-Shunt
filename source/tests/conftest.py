import pytest

from source.objects.coupling import Coupling
from source.objects.position import TrackPosition
from source.objects.rolling_stock import RollingStock, RollingStockState
from source.objects.truck import Truck
from source.tests.track_test import make_test_yard


@pytest.fixture
def yard():
    return make_test_yard()


def make_test_car_state(track_id: str) -> RollingStockState:
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
                wheel_diameter=1.0,
                axle_spacing=2.5,
                axle_count=3,
                max_swivel_angle=5,
                rolling_resistance_per_axle=500,
            ),
            Truck(
                offset_from_centre=-50,
                wheel_diameter=1.0,
                axle_spacing=2.5,
                axle_count=3,
                max_swivel_angle=5,
                rolling_resistance_per_axle=500,
            ),
        ],
    )

    state = RollingStockState(stock=car, condition=1.0, handbrake_force=0.0)

    for truck_state in state.trucks:
        truck_state.truck_position = TrackPosition(
            track_id=track_id,
            distance_along=0.0,
        )

    return state


@pytest.fixture
def straight_car_state():
    return make_test_car_state("t1")


@pytest.fixture
def curved_car_state():
    return make_test_car_state("t3")

