from PySide6 import QtCore, QtWidgets, QtGui

from source.ui.YardView import YardView

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
