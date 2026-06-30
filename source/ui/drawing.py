from math import cos, sin, radians, hypot

from PySide6 import QtCore, QtWidgets, QtGui

from source.logic.types import Float, Point


class DrawingHelpers:
    @staticmethod
    def get_bezier_path(
        a_pos: Point, a_angle: Float, b_pos: Point, b_angle: Float
    ) -> QtGui.QPainterPath:
        distance = hypot(b_pos.x - a_pos.x, b_pos.y - a_pos.y)
        control_distance = max(25, min(distance / 3, 120))

        c1 = DrawingHelpers.generate_control_point(a_pos, a_angle, control_distance)
        c2 = DrawingHelpers.generate_control_point(b_pos, b_angle, control_distance)

        path = QtGui.QPainterPath()
        path.moveTo(a_pos.x, a_pos.y)
        path.cubicTo(
            c1.x,
            c1.y,
            c2.x,
            c2.y,
            b_pos.x,
            b_pos.y,
        )

        return path

    @staticmethod
    def generate_control_point(point: Point, angle_deg: Float, control_distance: Float) -> Point:
        a = radians(angle_deg)
        return Point(
            point.x + control_distance * cos(a),
            point.y + control_distance * sin(a),
        )
