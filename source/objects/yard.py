from dataclasses import dataclass

from source.objects.track import NodeId, Track
from source.objects.node import Node
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

    def track_length(self, track_id: str) -> Float:

        return get_bezier_length_from_points_and_angles(*self.get_track_poss_and_angles(track_id))

    def get_track_geometry(self, track_id: str) -> tuple:

        track = self.tracks[track_id]

        a_node = self.nodes[track.a.node_id]
        b_node = self.nodes[track.b.node_id]

        a_pos = a_node.port_point(track.a.port_id, self.loading_gauge)
        a_angle = a_node.port_angle(track.a.port_id, self.loading_gauge)

        b_pos = b_node.port_point(track.b.port_id, self.loading_gauge)
        b_angle = b_node.port_angle(track.b.port_id, self.loading_gauge)
        return (a_pos, a_angle, b_pos, b_angle)
