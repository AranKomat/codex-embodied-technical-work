import unittest

from live_session.rgbd import deproject_pixel, look_at_camera_to_world
from live_session.contracts import Request


class RgbdGeometryTest(unittest.TestCase):
    def test_center_pixel_deprojects_along_camera_forward(self) -> None:
        transform = look_at_camera_to_world((0.0, 0.0, 1.0), (0.0, 0.0, 0.0))
        point = deproject_pixel(
            320.0,
            240.0,
            0.5,
            fx=500.0,
            fy=500.0,
            cx=320.0,
            cy=240.0,
            camera_to_world=transform,
        )
        self.assertEqual(point, [0.0, 0.0, 0.5])

    def test_rejects_invalid_depth(self) -> None:
        with self.assertRaises(ValueError):
            deproject_pixel(
                0,
                0,
                0,
                fx=1,
                fy=1,
                cx=0,
                cy=0,
                camera_to_world=look_at_camera_to_world((0, 0, 1), (0, 0, 0)),
            )

    def test_locate_measure_request_is_bounded(self) -> None:
        request = Request.parse(
            {
                "command": "locate_measure",
                "args": {
                    "u": 10,
                    "v": 20,
                    "depth_m": 0.5,
                    "observation": {"fx": 1, "fy": 1, "cx": 0, "cy": 0},
                },
            }
        )
        self.assertEqual(request.validated_args()["depth_m"], 0.5)


if __name__ == "__main__":
    unittest.main()
