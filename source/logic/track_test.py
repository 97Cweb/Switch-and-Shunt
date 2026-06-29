from source.logic.track import NodeRoute, TrackNode, BufferNode, ExitNode, PortRef, Track


def track_test():
    yard_exit = ExitNode("exit_west", "West Exit")

    sw1 = TrackNode(
        id="sw1",
        name="Switch 1",
        routes=(
            NodeRoute("straight", "root", "straight"),
            NodeRoute("diverging", "root", "diverging"),
        ),
        current_position="straight",
    )

    t1 = Track(
        id="t1",
        a=PortRef(yard_exit.id, yard_exit.routes[0].a),
        b=PortRef(sw1.id, "straight"),
    )
    print(t1)
    print(sw1.can_pass("root", "straight"))
    print(sw1.can_pass("root", "diverging"))

    sw1.set_position("diverging")

    print(sw1.can_pass("root", "straight"))
    print(sw1.can_pass("root", "diverging"))
