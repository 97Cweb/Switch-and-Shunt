from PySide6 import QtCore, QtGui

from source.objects.node import Node
from source.ui.items.node_item import BufferItem, ExitItem, SwitchItem
from source.ui.items.track_item import TrackItem


class YardSceneBuilder:
    def __init__(self, scene, yard, palette):
        self.scene = scene
        self.palette = palette
        self.yard = yard

        bg = self.palette.color(QtGui.QPalette.ColorRole.Base)

        active_col = QtCore.Qt.black
        inactive_col = bg.darker(135)

        self.track_pen = QtGui.QPen(active_col)
        self.track_pen.setWidth(self.yard.track_width)
        self.track_pen.setJoinStyle(QtCore.Qt.RoundJoin)

        inactive_route_pen = QtGui.QPen(inactive_col)
        inactive_route_pen.setWidth(self.yard.track_width)
        inactive_route_pen.setJoinStyle(QtCore.Qt.RoundJoin)

        active_route_pen = QtGui.QPen(QtCore.Qt.black)
        active_route_pen.setWidth(self.yard.track_width)
        active_route_pen.setJoinStyle(QtCore.Qt.RoundJoin)

        node_pen = QtGui.QPen(QtCore.Qt.darkGray)
        node_pen.setWidth(1)

        node_brush = QtGui.QBrush(QtCore.Qt.NoBrush)
        hit_brush = QtGui.QBrush(QtCore.Qt.transparent)

        good_pen = QtGui.QPen(QtCore.Qt.darkGreen)
        good_brush = QtGui.QBrush(QtCore.Qt.darkGreen)

        self.pens = {
            "track_pen": self.track_pen,
            "inactive_route_pen": inactive_route_pen,
            "active_route_pen": active_route_pen,
            "node_pen": node_pen,
            "good_pen": good_pen,
        }
        self.brushes = {"node_brush": node_brush, "hit_brush": hit_brush, "good_brush": good_brush}

    def draw(self):
        self.scene.clear()
        self.scene.setSceneRect(0, 0, 1000, 600)

        self.draw_tracks()
        self.draw_nodes()

    def draw_tracks(self) -> None:

        for track in self.yard.drawable_tracks():
            self.scene.addItem(TrackItem(self.yard, track.id, self.track_pen))

    def draw_nodes(self):
        for node in self.yard.drawable_track_nodes():
            if node.get_num_positions() > 1:
                self.scene.addItem(SwitchItem(self.yard, node, self.pens, self.brushes))
            elif node.routes[0].position == "blocked":
                self.scene.addItem(BufferItem(self.yard, node, self.pens))
            elif node.routes[0].position == "exit":
                self.scene.addItem(ExitItem(self.yard, node, self.pens, self.brushes))
