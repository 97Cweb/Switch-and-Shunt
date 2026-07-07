from source.domain.infrastructure.node import (
    NodeRoute,
    SwitchNode,
    BufferNode,
    ExitNode,
    Point,
)
from source.domain.infrastructure.track import PortRef, Track
from source.domain.infrastructure.yard import Yard


def make_test_yard() -> Yard:
    yard_exit_w = ExitNode("exit_west", "West Exit", Point(20, 500), 0, 180)
    yard_exit_e = ExitNode("exit_east", "East Exit", Point(980, 500), 0, 0)
    buffer = BufferNode("buffer_1", "Buffer 1", Point(300, 470), 0, 0)

    sw1 = SwitchNode(
        id="sw1",
        name="Switch 1",
        centre=Point(200, 500),
        altitude=0,
        rotation_degrees=0,
        routes=(
            NodeRoute("straight", "root", "straight"),
            NodeRoute("diverging", "root", "diverging"),
        ),
        current_position="straight",
        diverging_degrees=-30,
    )

    t1 = Track(
        id="t1",
        a=PortRef(yard_exit_w.id, "exit"),
        b=PortRef(sw1.id, "root"),
    )

    t2 = Track(
        id="t2",
        a=PortRef(sw1.id, "straight"),
        b=PortRef(yard_exit_e.id, "exit"),
    )

    t3 = Track(
        id="t3",
        a=PortRef(sw1.id, "diverging"),
        b=PortRef(buffer.id, "end"),
    )

    return Yard(
        nodes={
            yard_exit_w.id: yard_exit_w,
            yard_exit_e.id: yard_exit_e,
            sw1.id: sw1,
            buffer.id: buffer,
        },
        tracks={
            t1.id: t1,
            t2.id: t2,
            t3.id: t3,
        },
    )
