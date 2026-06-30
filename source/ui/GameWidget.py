import math
from PySide6 import QtCore, QtWidgets, QtGui

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

        back_button = QtWidgets.QPushButton("Back to Menu")
        back_button.clicked.connect(self.back_to_menu.emit)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.addWidget(back_button)

        self.make_test_yard()

    def activate(self) -> None:
        self.view.setFocus()

    def make_test_yard(self) -> None:
        yard = make_test_yard()
        self.draw_yard(yard)

    def draw_yard(self, yard) -> None:
      self.scene.clear()
      self.scene.setSceneRect(0, 0, 1000, 600)

      track_pen = QtGui.QPen(QtCore.Qt.black)
      track_pen.setWidth(self.track_width)

      node_pen = QtGui.QPen(QtCore.Qt.darkGray)
      node_pen.setWidth(1)

      node_brush = QtGui.QBrush(QtCore.Qt.lightGray)

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

          self.scene.addPath(path, track_pen)

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

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.back_to_menu.emit()
            event.accept()
        else:
            super().keyPressEvent(event)
