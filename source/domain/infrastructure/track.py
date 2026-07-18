from dataclasses import dataclass

from source.domain.infrastructure.node import NodeId, PortId


@dataclass(frozen=True)
class PortRef:
    node_id: NodeId
    port_id: PortId


@dataclass(frozen=True)
class Track:
    id: str
    a: PortRef
    b: PortRef
    is_electrified: bool = False
