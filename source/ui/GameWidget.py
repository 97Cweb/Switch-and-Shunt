import math
from PySide6 import QtCore, QtWidgets, QtGui

from source.logic.track import TrackNode
from source.ui.drawing import DrawingHelpers
from source.ui.YardView import YardView
from source.logic.track_test import make_test_yard


class GameWidget(QtWidgets.QWidget):
    back_to_menu = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.track_width = 4
        self.scene = QtWidgets.QGraphicsScene()
        self.view = YardView(self.scene)
        self.view.node_clicked.connect(self.cycle_node_position)

        back_button = QtWidgets.QPushButton("Back to Menu")
        back_button.clicked.connect(self.back_to_menu.emit)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.addWidget(back_button)

        self.make_test_yard()

    def activate(self) -> None:
        self.view.setFocus()

    def make_test_yard(self) -> None:
        self.yard = make_test_yard()
        self.draw_yard()

    def draw_yard(self) -> None:
        if self.yard is None:
            return
        yard = self.yard
        self.scene.clear()
        self.scene.setSceneRect(0, 0, 1000, 600)
        bg = self.palette().color(QtGui.QPalette.ColorRole.Base)

        active_col = QtCore.Qt.black
        inactive_col = bg.darker(135)

        track_pen = QtGui.QPen(active_col)
        track_pen.setWidth(self.track_width)
        track_pen.setCapStyle(QtCore.Qt.RoundCap)
        track_pen.setJoinStyle(QtCore.Qt.RoundJoin)

        inactive_route_pen = QtGui.QPen(inactive_col)
        inactive_route_pen.setWidth(self.track_width)
        inactive_route_pen.setJoinStyle(QtCore.Qt.RoundJoin)

        active_route_pen = QtGui.QPen(QtCore.Qt.black)
        active_route_pen.setWidth(self.track_width)
        active_route_pen.setJoinStyle(QtCore.Qt.RoundJoin)

        node_pen = QtGui.QPen(QtCore.Qt.darkGray)
        node_pen.setWidth(1)

        node_brush = QtGui.QBrush(QtCore.Qt.NoBrush)
        hit_brush = QtGui.QBrush(QtCore.Qt.transparent)

        self.draw_tracks(yard, track_pen)

        # draw all node routes
        for node in yard.drawable_track_nodes():
            self.draw_node_routes(node, inactive_route_pen)

        for node in yard.drawable_track_nodes():
            self.draw_node_routes(node, active_route_pen, active_only=True)

        for node in yard.drawable_track_nodes():
            r = yard.loading_gauge / 2.0

            self.scene.addEllipse(
                node.centre.x - r,
                node.centre.y - r,
                r * 2.0,
                r * 2.0,
                node_pen,
                node_brush,
            )

            # Bigger invisible click target, especially nice once the drawing gets dense.
            hit_r = r * 1.35
            hit_item = self.scene.addEllipse(
                node.centre.x - hit_r,
                node.centre.y - hit_r,
                hit_r * 2.0,
                hit_r * 2.0,
                QtGui.QPen(QtCore.Qt.NoPen),
                hit_brush,
            )
            positions = self.position_order(node)
            if len(positions) > 1:
                hit_item.setData(0, node.id)
                hit_item.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
                hit_item.setCursor(QtCore.Qt.PointingHandCursor)

    def draw_tracks(self, yard, pen: QtGui.QPen) -> None:

        for track in yard.drawable_tracks():
            a_node = yard.nodes[track.a.node_id]
            b_node = yard.nodes[track.b.node_id]

            a_pos = a_node.port_point(track.a.port_id, yard.loading_gauge)
            a_angle = a_node.port_angle(track.a.port_id, yard.loading_gauge)

            b_pos = b_node.port_point(track.b.port_id, yard.loading_gauge)
            b_angle = b_node.port_angle(track.b.port_id, yard.loading_gauge)

            path = DrawingHelpers.get_bezier_path(
                a_pos,
                a_angle,
                b_pos,
                b_angle,
            )

            self.scene.addPath(path, pen)

    def draw_node_routes(
        self,
        node: TrackNode,
        pen: QtGui.QPen,
        active_only: bool = False,
    ) -> None:
        if self.yard is None:
            return

        routes = None
        if active_only:
            routes = node.active_routes()
        else:
            routes = node.routes

        ports = node.port_geometries(self.yard.loading_gauge)

        for route in routes:
            if route.a not in ports or route.b not in ports:
                continue

            a_pos = node.port_point(route.a, self.yard.loading_gauge)
            b_pos = node.port_point(route.b, self.yard.loading_gauge)

            a_angle = node.port_angle(route.a, self.yard.loading_gauge) + 180.0
            b_angle = node.port_angle(route.b, self.yard.loading_gauge) + 180.0

            path = DrawingHelpers.get_bezier_path(a_pos, a_angle, b_pos, b_angle)
            self.scene.addPath(path, pen)

    def cycle_node_position(self, node_id: str) -> None:
        if self.yard is None:
            return
        node = self.yard.nodes[node_id]
        positions = self.position_order(node)

        if len(positions) <= 1:
            return
        current_index = positions.index(node.current_position)
        next_index = (current_index + 1) % len(positions)
        node.set_position(positions[next_index])
        self.draw_yard()

    def position_order(self, node: TrackNode) -> tuple[str, ...]:
        ordered = []
        for route in node.routes:
            if route.position not in ordered:
                ordered.append(route.position)
        return tuple(ordered)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.back_to_menu.emit()
            event.accept()
        else:
            super().keyPressEvent(event)
