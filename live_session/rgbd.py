"""Small, task-agnostic RGB-D geometry helpers."""

from __future__ import annotations

import math
from typing import Sequence


def deproject_pixel(
    u: float,
    v: float,
    depth_m: float,
    *,
    fx: float,
    fy: float,
    cx: float,
    cy: float,
    camera_to_world: Sequence[Sequence[float]],
) -> list[float]:
    """Convert one camera pixel/depth sample to a world-frame point."""
    if depth_m <= 0 or not math.isfinite(depth_m):
        raise ValueError("depth_m must be finite and positive")
    if fx <= 0 or fy <= 0:
        raise ValueError("focal lengths must be positive")
    x = (float(u) - cx) * depth_m / fx
    y = (float(v) - cy) * depth_m / fy
    camera_point = [x, y, depth_m, 1.0]
    return [
        sum(float(camera_to_world[row][col]) * camera_point[col] for col in range(4))
        for row in range(3)
    ]


def look_at_camera_to_world(
    eye: Sequence[float], target: Sequence[float], *, up: Sequence[float] = (0.0, 0.0, 1.0)
) -> list[list[float]]:
    """Build a right-handed camera-to-world matrix for a camera looking along +Z."""
    def normalize(vector: Sequence[float]) -> list[float]:
        norm = math.sqrt(sum(float(value) ** 2 for value in vector))
        if norm <= 1e-9:
            raise ValueError("camera basis is degenerate")
        return [float(value) / norm for value in vector]

    def cross(a: Sequence[float], b: Sequence[float]) -> list[float]:
        return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]

    forward = normalize([target[i] - eye[i] for i in range(3)])
    if abs(sum(forward[i] * float(up[i]) for i in range(3))) > 0.99:
        up = (0.0, 1.0, 0.0)
    right = normalize(cross(forward, up))
    true_up = normalize(cross(right, forward))
    return [
        [right[0], true_up[0], forward[0], float(eye[0])],
        [right[1], true_up[1], forward[1], float(eye[1])],
        [right[2], true_up[2], forward[2], float(eye[2])],
    ]
