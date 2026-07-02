from math import hypot, sin, cos, radians

from source.shared.types import Float, Point


def distance_between(a: Point, b: Point) -> Float:
    return hypot(b.x - a.x, b.y - a.y)


def generate_control_point(point: Point, angle_deg: Float, control_distance: Float) -> Point:
    a = radians(angle_deg)
    return Point(
        point.x + control_distance * cos(a),
        point.y + control_distance * sin(a),
    )


def get_bezier_control_distance(a: Point, b: Point) -> Float:
    distance = distance_between(a, b)
    return max(25.0, min(distance / 3.0, 120.0))


def get_bezier_points(
    a_pos: Point, a_angle: Float, b_pos: Point, b_angle: Float
) -> tuple[Point, Point, Point, Point]:
    control_distance = get_bezier_control_distance(a_pos, b_pos)

    return (
        a_pos,
        generate_control_point(a_pos, a_angle, control_distance),
        generate_control_point(b_pos, b_angle, control_distance),
        b_pos,
    )


def get_bezier_point(
    p0: Point,
    p1: Point,
    p2: Point,
    p3: Point,
    t: Float,
) -> Point:
    u = 1.0 - t

    return Point(
        u**3 * p0.x + 3 * u**2 * t * p1.x + 3 * u * t**2 * p2.x + t**3 * p3.x,
        u**3 * p0.y + 3 * u**2 * t * p1.y + 3 * u * t**2 * p2.y + t**3 * p3.y,
    )


def get_bezier_length_from_points(
    p0: Point, p1: Point, p2: Point, p3: Point, samples: int = 64
) -> Float:
    length = 0.0
    previous = p0

    for i in range(1, samples + 1):
        t = i / samples
        current = get_bezier_point(p0, p1, p2, p3, t)
        length += distance_between(previous, current)
        previous = current
    return length


def get_bezier_length_from_points_and_angles(
    a_pos: Point,
    a_angle: Float,
    b_pos: Point,
    b_angle: Float,
) -> Float:
    return get_bezier_length_from_points(
        *get_bezier_points(a_pos, a_angle, b_pos, b_angle)  # * to unpack tuple to individuals
    )
