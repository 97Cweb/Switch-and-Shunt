from PySide6 import QtCore, QtWidgets, QtGui


class YardView(QtWidgets.QGraphicsView):
    node_clicked = QtCore.Signal(str)

    def __init__(self, scene):
        super().__init__(scene)

        self.right_mouse_dragging = False
        self.last_mouse_pos = None

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        self.held_keys = set()
        self.pan_speed = 8

        self.pan_timer = QtCore.QTimer(self)
        self.pan_timer.timeout.connect(self.update_pan)
        self.pan_timer.start(16)  # about 60 FPS

    def wheelEvent(self, event):
        zoom = 1.15

        if event.angleDelta().y() > 0:
            self.scale(zoom, zoom)
        else:
            self.scale(1 / zoom, 1 / zoom)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            super().keyPressEvent(event)
            return

        if not event.isAutoRepeat():
            self.held_keys.add(event.key())

        event.accept()

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            self.held_keys.discard(event.key())
        event.accept()

    def update_pan(self):
        dx = 0
        dy = 0
        if QtCore.Qt.Key_W in self.held_keys:
            dy -= self.pan_speed
        if QtCore.Qt.Key_S in self.held_keys:
            dy += self.pan_speed
        if QtCore.Qt.Key_A in self.held_keys:
            dx -= self.pan_speed
        if QtCore.Qt.Key_D in self.held_keys:
            dx += self.pan_speed

        if dx:
            bar = self.horizontalScrollBar()
            bar.setValue(bar.value() + dx)

        if dy:
            bar = self.verticalScrollBar()
            bar.setValue(bar.value() + dy)

    def mousePressEvent(self, event):
        self.setFocus()

        if event.button() == QtCore.Qt.RightButton:
            self.right_mouse_dragging = True
            self.last_mouse_pos = event.position()
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            event.accept()
            return

        if event.button() == QtCore.Qt.LeftButton:
            scene_pos = self.mapToScene(event.position().toPoint())
            for item in self.scene().items(scene_pos):
                node_id = item.data(0)
                if node_id:
                    self.node_clicked.emit(node_id)
                    event.accept()
                    return
        event.accept()

    def mouseMoveEvent(self, event):
        if self.right_mouse_dragging and self.last_mouse_pos is not None:
            delta = event.position() - self.last_mouse_pos
            self.last_mouse_pos = event.position()

            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(delta.y()))

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.right_mouse_dragging = False
            self.last_mouse_pos = None
            self.setCursor(QtCore.Qt.ArrowCursor)
            event.accept()
            return

        super().mouseReleaseEvent(event)
