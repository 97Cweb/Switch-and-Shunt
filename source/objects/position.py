from dataclasses import dataclass

from source.objects.node import NodeId, PortId
from source.shared.types import Float


@dataclass(frozen=True, kw_only=True)
class TruckPosition:
    distance_along: Float


@dataclass(frozen=True)
class TrackPosition(TruckPosition):
    track_id: str


@dataclass(frozen=True)
class NodePosition(TruckPosition):
    node_id: NodeId
    entered_from_port_id: PortId
