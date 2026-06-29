from dataclasses import dataclass

type NodeId = str
type PortId = str


@dataclass(frozen=True)
class PortRef:
    node_id: NodeId
    port_id: PortId


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class TrackGeometry:
    points: tuple[Point, ...]


@dataclass(frozen=True)
class Track:
    id: str
    a: PortRef
    b: PortRef
    geometry: TrackGeometry | None = None


@dataclass(frozen=True)
class NodeRoute:
    position: str
    a: PortId
    b: PortId


@dataclass
class Node:
    id: NodeId
    name: str


@dataclass
class TrackNode(Node):
    routes: tuple[NodeRoute, ...]
    current_position: str

    def active_routes(self) -> tuple[NodeRoute, ...]:
        return tuple(route for route in self.routes if route.position == self.current_position)

    def valid_positions(self) -> set[str]:
        return {route.position for route in self.routes}

    def set_position(self, position: str) -> None:
        if position not in self.valid_positions():
            raise ValueError(f"{self.name} does not support position {position}")
        self.current_position = position

    def can_pass(self, from_port: PortId, to_port: PortId) -> bool:
        for route in self.active_routes():
            if (route.a == from_port and route.b == to_port) or (
                route.a == to_port and route.b == from_port
            ):
                return True
        return False


@dataclass
class BufferNode(TrackNode):
    def __init__(self, id: NodeId, name: str) -> None:
        super().__init__(
            id=id,
            name=name,
            routes=(NodeRoute("blocked", "end", "__null__"),),
            current_position="blocked",
        )


class ExitNode(TrackNode):
    def __init__(self, id: NodeId, name: str) -> None:
        super().__init__(
            id=id,
            name=name,
            routes=(NodeRoute("exit", "exit", "__exit__"),),
            current_position="exit",
        )
