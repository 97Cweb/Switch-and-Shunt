from source.shared.types import Float


def sign(value: Float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def lerp(a: Float, b: Float, fraction: Float) -> Float:
    diff = b - a
    return a + fraction * diff
