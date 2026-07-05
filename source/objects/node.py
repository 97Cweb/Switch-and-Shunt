from dataclasses import dataclass
from math import cos, sin, tan, radians

from source.shared.types import Float, Point
from source.simulation.constants import BLOCKED_PORT, EXIT_PORT


type NodeId = str
type PortId = str


def point_from_angle(origin: Point, angle_degrees: Float, distance: Float) -> Point:
    a = radians(angle_degrees)
    return Point(
        origin.x + distance * cos(a),
        origin.y + distance * sin(a),
    )


@dataclass(frozen=True)
class PortGeometry:
    point: Point
    angle: Float


@dataclass(frozen=True)
class NodeRoute:
    position: str
    a: PortId
    b: PortId


@dataclass
class Node:
    id: NodeId
    name: str
    centre: Point
    altitude: Float
    rotation_degrees: Float
    routes: tuple[NodeRoute, ...]
    current_position: str

    def positions_ordered(self) -> tuple[str, ...]:
        ordered = []
        for route in self.routes:
            if route.position not in ordered:
                ordered.append(route.position)
        return tuple(ordered)

    def get_num_positions(self):
        return len(self.positions_ordered())

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

    def next_port(self, from_port: PortId) -> PortId | None:
        for route in self.active_routes():
            if route.a == from_port:
                return route.b
            if route.b == from_port:
                return route.a
        return None

    def active_route_from_port(self, port_id: PortId) -> NodeRoute | None:
        for route in self.active_routes():
            if route.a == port_id or route.b == port_id:
                return route
        return None

    def port_geometries(self, loading_gauge: Float) -> dict[PortId, PortGeometry]:
        raise NotImplementedError

    def port_geometry(self, port_id: PortId, loading_gauge: Float) -> PortGeometry:
        ports = self.port_geometries(loading_gauge)

        if port_id not in ports:
            raise ValueError(f"{self.name} has no port {port_id}")

        return ports[port_id]

    def port_point(self, port_id: PortId, loading_gauge: Float) -> Point:
        geometry = self.port_geometry(port_id, loading_gauge)
        return self.transform_local_point(geometry.point)

    def port_angle(self, port_id: PortId, loading_gauge: Float) -> Float:
        geometry = self.port_geometry(port_id, loading_gauge)
        return self.rotation_degrees + geometry.angle

    def transform_local_point(self, point: Point) -> Point:
        angle = radians(self.rotation_degrees)

        x = point.x * cos(angle) - point.y * sin(angle)
        y = point.x * sin(angle) + point.y * cos(angle)

        return Point(
            self.centre.x + x,
            self.centre.y + y,
        )

    def get_route_geometry(self, route: NodeRoute, loading_gauge: Float):
        if route.b == EXIT_PORT or route.b == BLOCKED_PORT:
            a_pos = self.port_point(route.a, loading_gauge)
            a_angle = self.port_angle(route.a, loading_gauge)

            b_pos = point_from_angle(a_pos, a_angle, loading_gauge)
            b_angle = a_angle

            return (a_pos, a_angle, b_pos, b_angle)
        a_pos = self.port_point(route.a, loading_gauge)
        b_pos = self.port_point(route.b, loading_gauge)

        a_angle = self.port_angle(route.a, loading_gauge) + 180
        b_angle = self.port_angle(route.b, loading_gauge) + 180

        return (a_pos, a_angle, b_pos, b_angle)


@dataclass
class BufferNode(Node):
    def __init__(
        self, id: NodeId, name: str, centre: Point, altitude: Float, rotation_degrees: Float
    ) -> None:
        super().__init__(
            id=id,
            name=name,
            centre=centre,
            altitude=altitude,
            rotation_degrees=rotation_degrees,
            routes=(NodeRoute("blocked", "end", BLOCKED_PORT),),
            current_position="blocked",
        )

    def port_geometries(self, loading_gauge: Float) -> dict[PortId, PortGeometry]:
        return {
            "end": PortGeometry(Point(0.0, 0.0), 180.0),
        }


class ExitNode(Node):
    def __init__(
        self, id: NodeId, name: str, centre: Point, altitude: Float, rotation_degrees: Float
    ) -> None:
        super().__init__(
            id=id,
            name=name,
            centre=centre,
            altitude=altitude,
            rotation_degrees=rotation_degrees,
            routes=(NodeRoute("exit", "exit", EXIT_PORT),),
            current_position="exit",
        )

    def port_geometries(self, loading_gauge: Float) -> dict[PortId, PortGeometry]:
        return {
            "exit": PortGeometry(Point(0.0, 0.0), 180.0),
        }


@dataclass
class SwitchNode(Node):
    diverging_degrees: Float = 20.0

    def port_geometries(self, loading_gauge: Float) -> dict[PortId, PortGeometry]:
        angle = abs(self.diverging_degrees)

        if angle == 0:
            length = loading_gauge * 2.0
        else:
            length = loading_gauge / tan(radians(angle))

        half = length / 2.0

        straight = Point(half, 0.0)
        root = Point(-half, 0.0)
        diverging = point_from_angle(
            Point(0.0, 0.0),
            self.diverging_degrees,
            half,
        )

        return {
            "root": PortGeometry(root, 180.0),
            "straight": PortGeometry(straight, 0.0),
            "diverging": PortGeometry(diverging, self.diverging_degrees),
        }
