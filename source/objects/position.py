from dataclasses import dataclass

from source.objects.node import NodeId, PortId
from source.shared.types import Float


@dataclass(frozen=True)
class TrackPosition:
    track_id: str
    distance_along: Float


@dataclass(frozen=True)
class NodePosition:
    node_id: NodeId
    entered_from_port_id: PortId
    distance_along: Float


type TruckPosition = TrackPosition | NodePosition
