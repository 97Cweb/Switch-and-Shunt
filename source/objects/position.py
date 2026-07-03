from dataclasses import dataclass

from source.objects.node import NodeId
from source.shared.types import Float


@dataclass(frozen=True)
class TrackPosition:
    track_id: str
    distance_along: Float


@dataclass(frozen=True)
class NodePosition:
    node_id: NodeId
    distance_along: Float


type TruckPosition = TrackPosition | NodePosition
