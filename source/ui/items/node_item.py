from PySide6 import QtCore, QtWidgets, QtGui

from source.objects.node import Node
from source.objects.yard import Yard
from source.ui.rendering.drawing import DrawingHelpers


class NodeItem(QtWidgets.QGraphicsItemGroup):
    def __init__(self, yard: Yard, node: Node, pens):
        super().__init__()
        routes = node.routes

        active_routes = node.active_routes()

        ports = node.port_geometries(yard.loading_gauge)

        for route in routes:
            if route.a not in ports or route.b not in ports:
                continue
            if route in active_routes:
                continue

            self.add_route(node, route, yard.loading_gauge, pens["inactive_route_pen"])

        for route in active_routes:
            if route.a not in ports or route.b not in ports:
                continue

            self.add_route(node, route, yard.loading_gauge, pens["active_route_pen"])

    def add_route(self, node, route, loading_gauge, pen):
        path = DrawingHelpers.get_bezier_path(*node.get_route_geometry(route, loading_gauge))

        route_item = QtWidgets.QGraphicsPathItem(path)
        route_item.setPen(pen)

        self.addToGroup(route_item)


class SwitchItem(NodeItem):
    def __init__(self, yard: Yard, node: Node, pens, brushes):
        super().__init__(yard, node, pens)

        r = yard.loading_gauge / 2.0

        visible = QtWidgets.QGraphicsEllipseItem(
            node.centre.x - r,
            node.centre.y - r,
            r * 2.0,
            r * 2.0,
        )
        visible.setPen(pens["node_pen"])
        visible.setBrush(brushes["node_brush"])

        hit_r = r * 1.35
        hit = QtWidgets.QGraphicsEllipseItem(
            node.centre.x - hit_r,
            node.centre.y - hit_r,
            hit_r * 2.0,
            hit_r * 2.0,
        )
        hit.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        hit.setBrush(brushes["hit_brush"])
        hit.setData(0, node.id)
        hit.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        hit.setCursor(QtCore.Qt.PointingHandCursor)

        self.addToGroup(visible)
        self.addToGroup(hit)


class BufferItem(NodeItem):
    def __init__(self, yard: Yard, node: Node, pens):
        super().__init__(yard, node, pens)

        line = QtCore.QLineF(
            QtCore.QPointF(0, -yard.loading_gauge / 2),
            QtCore.QPointF(0, yard.loading_gauge / 2),
        )
        transform = QtGui.QTransform()
        transform.translate(node.centre.x, node.centre.y)
        transform.rotate(node.rotation_degrees)

        line = transform.map(line)
        line_item = QtWidgets.QGraphicsLineItem(line)
        line_item.setPen(pens["track_pen"])

        self.addToGroup(line_item)


class ExitItem(NodeItem):
    def __init__(self, yard: Yard, node: Node, pens, brushes):
        super().__init__(yard, node, pens)
        triangle_length = yard.track_width * 2
        triangle_half_height = yard.track_width

        triangle = QtGui.QPolygonF(
            [
                QtCore.QPointF(-triangle_length / 3, -triangle_half_height),
                QtCore.QPointF(triangle_length * 2 / 3, 0),
                QtCore.QPointF(-triangle_length / 3, triangle_half_height),
            ]
        )

        transform = QtGui.QTransform()
        transform.translate(node.centre.x, node.centre.y)
        transform.rotate(node.rotation_degrees)
        transform.translate(yard.track_width * 2, 0)

        triangle = transform.map(triangle)
        triangle_item = QtWidgets.QGraphicsPolygonItem(triangle)

        triangle_item.setPen(pens["good_pen"])
        triangle_item.setBrush(brushes["good_brush"])

        self.addToGroup(triangle_item)
