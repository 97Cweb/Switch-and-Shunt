import sys
from PySide6 import QtWidgets

from source.ui.MainWindow import MainWindow

def main() -> None:
    app = QtWidgets.QApplication([])

    main_window = MainWindow()
    main_window.resize(800, 600)
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
