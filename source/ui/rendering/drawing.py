from PySide6 import QtGui

from source.shared.types import Float, Point
from source.shared.geometry import get_bezier_points


class DrawingHelpers:
    @staticmethod
    def get_bezier_path(
        a_pos: Point, a_angle: Float, b_pos: Point, b_angle: Float
    ) -> QtGui.QPainterPath:

        p0, p1, p2, p3 = get_bezier_points(a_pos, a_angle, b_pos, b_angle)
        path = QtGui.QPainterPath()
        path.moveTo(p0.x, p0.y)
        path.cubicTo(
            p1.x,
            p1.y,
            p2.x,
            p2.y,
            p3.x,
            p3.y,
        )

        return path
