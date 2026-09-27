"""One bounded RGB-D-driven hover action for the realistic server-repair bridge."""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

from live_session.embodiedswe_backend import build_server_repair


def candidate(rgb: np.ndarray, depth: np.ndarray) -> tuple[float, float, float]:
    saturation = rgb.astype(np.int16).max(axis=2) - rgb.astype(np.int16).min(axis=2)
    yy = np.indices(saturation.shape)[0]
    mask = (saturation >= 30) & (yy >= 250) & np.isfinite(depth) & (depth > 0)
    ys, xs = np.where(mask)
    if len(xs) == 0:
        raise RuntimeError("no finite RGB-D candidate")
    weights = saturation[ys, xs].astype(np.float64)
    return (
        float(np.average(xs, weights=weights)),
        float(np.average(ys, weights=weights)),
        float(np.median(depth[ys, xs])),
    )


def main() -> None:
    output = Path("realistic_server_repair_hover.json")
    control_mode = os.environ.get("CONTROL_MODE", "osc")
    max_steps = int(os.environ.get("MAX_STEPS", "80"))
    backend = build_server_repair(mode="realistic", control_mode=control_mode)
    try:
        before = backend.dispatch("observe", {"cameras": [], "depth": True})
        camera = before["cameras"][0]
        data = np.load(camera["frame_path"])
        u, v, depth_m = candidate(data["rgb"][..., :3], data["depth"])
        measured = backend.dispatch(
            "locate_measure",
            {"observation": camera, "u": u, "v": v, "depth_m": depth_m},
        )
        point = measured["point_world_m"]
        state = backend.dispatch("state", {})
        orientation = state["robot"]["ee_quaternion_wxyz"]
        hover = [point[0], point[1], point[2] + 0.20]
        action = backend.dispatch(
            "move_ee",
            {
                "position_m": hover,
                "quaternion_wxyz": orientation,
                "mode": "linear",
                "max_steps": max_steps,
            },
        )
        after = backend.dispatch("observe", {"cameras": [], "depth": True})
        result = {
            "task": "server_repair",
            "mode": "realistic",
            "control_mode": control_mode,
            "max_steps": max_steps,
            "input": {
                "pixel": [u, v],
                "depth_m": depth_m,
                "point_world_m": point,
                "hover_target_world_m": hover,
            },
            "action": action,
            "after_observe": after,
            "clearance_certified": False,
            "contact_available": False,
            "privileged_pose_used": False,
        }
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    finally:
        os._exit(0)


if __name__ == "__main__":
    main()
