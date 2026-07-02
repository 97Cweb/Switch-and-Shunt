from PySide6 import QtWidgets, QtGui

from source.objects.yard import Yard
from source.ui.rendering.drawing import DrawingHelpers


class TrackItem(QtWidgets.QGraphicsPathItem):
    def __init__(self, yard: Yard, track_id: str, pen: QtGui.QPen):
        track_poss_and_angles = yard.get_track_poss_and_angles(track_id)
        path = DrawingHelpers.get_bezier_path(*track_poss_and_angles)
        super().__init__(path)
        self.setPen(pen)
