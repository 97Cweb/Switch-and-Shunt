import sys
from PySide6 import QtCore, QtWidgets, QtGui

from source.ui.YardView import YardView


class MainMenu(QtWidgets.QWidget):
    start_game = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        title = QtWidgets.QLabel("Switch and Shunt", alignment=QtCore.Qt.AlignCenter)
        start_button = QtWidgets.QPushButton("Start")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(start_button)

        start_button.clicked.connect(self.start_game.emit)


class GameWidget(QtWidgets.QWidget):
    back_to_menu = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.scene = QtWidgets.QGraphicsScene()
        self.view = YardView(self.scene)

        back_button = QtWidgets.QPushButton("Back to Menu")
        back_button.clicked.connect(self.back_to_menu.emit)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.addWidget(back_button)

        self.make_test_yard()

    def activate(self):
        self.view.setFocus()

    def make_test_yard(self):
        self.scene.setSceneRect(0, 0, 1000, 600)

        track_pen = QtGui.QPen(QtCore.Qt.black)
        track_pen.setWidth(4)

        # Main track
        self.scene.addLine(50, 300, 950, 300, track_pen)

        # Curved-ish siding using QPainterPath
        path = QtGui.QPainterPath()
        path.moveTo(250, 300)
        path.cubicTo(350, 250, 500, 250, 650, 300)

        self.scene.addPath(path, track_pen)

        # A simple car rectangle
        car = self.scene.addRect(100, 280, 60, 30)
        car.setBrush(QtGui.QBrush(QtCore.Qt.darkGray))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.back_to_menu.emit()
            event.accept()
        else:
            super().keyPressEvent(event)


class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.stack = QtWidgets.QStackedWidget()
        self.menu = MainMenu()
        self.game = GameWidget()

        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.game)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.stack)

        self.menu.start_game.connect(self.show_game)
        self.game.back_to_menu.connect(self.show_menu)

    @QtCore.Slot()
    def show_game(self):
        self.stack.setCurrentWidget(self.game)
        self.game.activate()

    @QtCore.Slot()
    def show_menu(self):
        self.stack.setCurrentWidget(self.menu)
        self.menu.setFocus()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            sys.exit()
        else:
            super().keyPressEvent(event)


def main() -> None:
    app = QtWidgets.QApplication([])

    main_widget = MainWidget()
    main_widget.resize(800, 600)
    main_widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
