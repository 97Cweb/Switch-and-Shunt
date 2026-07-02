import sys
from PySide6 import QtCore, QtWidgets

from source.ui.screens.main_menu import MainMenu
from source.ui.screens.game import Game


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.stack = QtWidgets.QStackedWidget()
        self.menu = MainMenu()
        self.game = Game()

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

    main_window = MainWindow()
    main_window.resize(800, 600)
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
