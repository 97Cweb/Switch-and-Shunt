from dataclasses import dataclass

from source.objects.position import NodePosition, TrackPosition, TruckPosition
from source.objects.track import NodeId, Track
from source.objects.node import Node, PortId

from source.shared.geometry import get_bezier_length_from_points_and_angles
from source.shared.types import Float


@dataclass
class Yard:
    nodes: dict[NodeId, Node]
    tracks: dict[str, Track]
    loading_gauge: Float = 40.0
    track_width: Float = 4

    def drawable_tracks(self) -> tuple[Track, ...]:
        return tuple(self.tracks.values())

    def drawable_track_nodes(self) -> tuple[Node, ...]:
        return tuple(self.nodes.values())

    def get_connected_track_id_from_port_id(self, node_id, port_id) -> str | None:
        for track_id, track in self.tracks.items():
            if track.a.node_id == node_id and track.a.port_id == port_id:
                return track_id
            elif track.b.node_id == node_id and track.b.port_id == port_id:
                return track_id

        return None

    def next_track_from_boundary(self, track_id: str, at_end: str) -> str | None:
        track = self.tracks[track_id]

        if at_end == "a":
            node_id = track.a.node_id
            entered_port = track.a.port_id

        elif at_end == "b":
            node_id = track.b.node_id
            entered_port = track.b.port_id

        else:
            raise ValueError(f"Invalid track end {at_end}")

        node = self.nodes[node_id]
        exit_port_id = node.next_port(entered_port)

        if exit_port_id is None:
            return None
        return self.get_connected_track_id_from_port_id(node_id, exit_port_id)

    def track_length(self, track_id: str) -> Float:

        return get_bezier_length_from_points_and_angles(*self.get_track_geometry(track_id))

    def get_track_geometry(self, track_id: str) -> tuple:

        track = self.tracks[track_id]

        a_node = self.nodes[track.a.node_id]
        b_node = self.nodes[track.b.node_id]

        a_pos = a_node.port_point(track.a.port_id, self.loading_gauge)
        a_angle = a_node.port_angle(track.a.port_id, self.loading_gauge)

        b_pos = b_node.port_point(track.b.port_id, self.loading_gauge)
        b_angle = b_node.port_angle(track.b.port_id, self.loading_gauge)
        return (a_pos, a_angle, b_pos, b_angle)

    def node_route_length_from_port(self, node_id: NodeId, port_id: PortId) -> Float | None:
        node = self.nodes[node_id]
        route = node.active_route_from_port(port_id)

        if route is None:
            return None
        return get_bezier_length_from_points_and_angles(
            *node.get_route_geometry(route, self.loading_gauge)
        )

    def track_grade(self, track_id: str) -> Float:
        track = self.tracks[track_id]

        a_node = self.node[track.a.node_id]
        b_node = self.nodes[track.b.node_id]

        length = self.track_length(track_id)

        if length == 0.0:
            return 0.0

        return (b_node.altitude - a_node.altitude) / length

    def node_route_grade_from_port(self, node_id: NodeId, port_id: PortId) -> Float:

        return 0.0

    def grade_at_position(self, position: TruckPosition | None) -> Float:
        if position is None:
            return 0.0
        if isinstance(position, TrackPosition):
            return self.track_grade(position.track_id)

        if isinstance(position, NodePosition):
            return self.node_route_grade_from_port(position.node_id, position.entered_from_port_id)
        return 0.0
