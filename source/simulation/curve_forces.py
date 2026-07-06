from dataclasses import dataclass

from source.objects.position import TruckPosition
from source.objects.yard import Yard
from source.shared.types import Float


@dataclass(frozen=True)
class LateralForceResult:
    curvature: Float
    lateral_acceleration: Float
    lateral_force: Float

    # stub diagnostics for tuning
    flange_squeal: Float
    derailment_risk: Float
    stringlining_risk: Float


def curve_lateral_force(
    yard: Yard, position: TruckPosition | None, mass: Float, velocity: Float
) -> LateralForceResult:
    curvature = yard.curvature_at_position(position)

    lateral_acceleration = velocity**2 * curvature
    lateral_force = mass * lateral_acceleration
    return LateralForceResult(
        curvature=curvature,
        lateral_acceleration=lateral_acceleration,
        lateral_force=lateral_force,
        flange_squeal=estimate_flange_squeal(curvature, velocity),
        derailment_risk=estimate_derailment_risk(lateral_acceleration),
        stringlining_risk=0.0,
    )


def estimate_flange_squeal(curvature: Float, velocity: Float) -> Float:
    # stub:grow with curvature and speed
    return abs(curvature) * abs(velocity)


def estimate_derailment_risk(lateral_acceleration: Float) -> Float:
    # stub, should depend on mass, loading gauge, wheelbase, flange
    return abs(lateral_acceleration) / 9.81


def estimate_stringlining_risk(coupler_force: Float, curvature: Float) -> Float:
    return abs(coupler_force) * abs(curvature)
