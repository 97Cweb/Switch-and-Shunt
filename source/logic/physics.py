from source.logic.rolling_stock import RollingStockState
from source.logic.types import Float


def sign(value: Float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def update_rolling_stock(state: RollingStockState, dt: Float) -> None:
    stock = state.stock

    force = state.applied_force

    if state.velocity != 0:
        # rolling resistance opposes motion
        force -= sign(state.velocity) * stock.rolling_resistance

        # handbrake opposes motion
        force -= sign(state.velocity) * state.handbrake_force

    state.acceleration = force / stock.mass
    state.velocity += state.acceleration * dt
    state.distance += state.velocity * dt

    state.applied_force = 0.0
