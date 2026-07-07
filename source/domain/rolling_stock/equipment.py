from dataclasses import dataclass

from source.shared.types import Float


@dataclass
class CarEquipment:
    pass


@dataclass
class CarEquipmentState:
    pass


@dataclass
class AirEquipment(CarEquipment):
    max_air_pressure: Float = 0.0
    atmos_volume_per_second_fill: Float = 0.0


@dataclass
class BrakeEquipment(CarEquipment):
    max_brake_force: Float = 0.0
    brake_pipe_volume: Float = 0.0


@dataclass
class AirBrakeEquipment(BrakeEquipment):
    reservoir_size: Float = 0.0


@dataclass
class StraightBrakeEquipment(BrakeEquipment):
    pass


@dataclass
class BrakeState(CarEquipmentState):
    brake_pipe_pressure: Float = 0.0
    brake_force: Float = 0.0


@dataclass
class AirBrakeState(BrakeState):
    pass


@dataclass
class StraightBrakeState(BrakeState):
    pass


@dataclass
class SteamEquipment(CarEquipment):
    max_pressure: Float


@dataclass
class SteamState(CarEquipmentState):
    pressure: Float = 0.0


@dataclass
class ElectricalEquipment(CarEquipment):
    max_voltage: Float


@dataclass
class ElectricalState(CarEquipmentState):
    voltage: Float = 0.0
    breaker_closed: bool = False


@dataclass
class MUEquipment(CarEquipment):
    pass


@dataclass
class MUState(CarEquipmentState):
    pass
