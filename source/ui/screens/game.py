from PySide6 import QtCore, QtWidgets

from source.ui.rendering.yard_scene_builder import YardSceneBuilder
from source.ui.views.panning_graphics_view import PanningGraphicsView
from source.tests.track_test import make_test_yard


class Game(QtWidgets.QWidget):
    back_to_menu = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.scene = QtWidgets.QGraphicsScene()
        self.view = PanningGraphicsView(self.scene)
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
        self.scene_builder = YardSceneBuilder(self.scene, self.yard, self.palette())
        self.draw_yard()

    def draw_yard(self) -> None:
        if self.yard is None:
            return

        self.scene_builder.draw()

    def cycle_node_position(self, node_id: str) -> None:
        if self.yard is None:
            return
        node = self.yard.nodes[node_id]
        positions = node.positions_ordered()

        if node.get_num_positions() <= 1:
            return
        current_index = positions.index(node.current_position)
        next_index = (current_index + 1) % len(positions)
        node.set_position(positions[next_index])
        self.draw_yard()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.back_to_menu.emit()
            event.accept()
        else:
            super().keyPressEvent(event)
