from PySide6 import QtCore,QtWidgets
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
