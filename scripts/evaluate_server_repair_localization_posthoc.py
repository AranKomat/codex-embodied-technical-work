"""Post-hoc evaluator diagnostic; hidden pose is never used for control.

The actor-side candidate is computed from RGB-D first. Only afterward is the
simulator card pose read to quantify localization error and projected-pixel
alignment. This is not a realistic-condition input or a control path.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

from live_session.embodiedswe_backend import build_server_repair


def rgb_candidate(rgb: np.ndarray, depth: np.ndarray) -> tuple[float, float, float]:
    saturation = rgb.astype(np.int16).max(axis=2) - rgb.astype(np.int16).min(axis=2)
    yy = np.indices(saturation.shape)[0]
    mask = (saturation >= 30) & (yy >= 250) & np.isfinite(depth) & (depth > 0)
    ys, xs = np.where(mask)
    if len(xs) == 0:
        raise RuntimeError("no finite candidate pixels")
    weights = saturation[ys, xs].astype(np.float64)
    return (
        float(np.average(xs, weights=weights)),
        float(np.average(ys, weights=weights)),
        float(np.median(depth[ys, xs])),
    )


def project(point: list[float], camera: dict) -> list[float]:
    matrix = np.asarray(camera["camera_to_world"], dtype=float)
    rotation = matrix[:, :3]
    eye = matrix[:, 3]
    camera_point = rotation.T @ (np.asarray(point, dtype=float) - eye)
    return [
        float(camera["cx"] + camera_point[0] * camera["fx"] / camera_point[2]),
        float(camera["cy"] - camera_point[1] * camera["fy"] / camera_point[2]),
        float(camera_point[2]),
    ]


def main() -> None:
    output = Path("server_repair_localization_posthoc.json")
    backend = build_server_repair(mode="realistic")
    try:
        observation = backend.dispatch("observe", {"cameras": [], "depth": True})
        camera = observation["cameras"][0]
        data = np.load(camera["frame_path"])
        u, v, depth_m = rgb_candidate(data["rgb"][..., :3], data["depth"])
        measured = backend.dispatch(
            "locate_measure",
            {"observation": camera, "u": u, "v": v, "depth_m": depth_m},
        )
        candidate_point = np.asarray(measured["point_world_m"], dtype=float)

        # Evaluator-only read, after actor-side observation and measurement.
        card_point = backend._object.data.root_pos_w[0].detach().cpu().tolist()
        projected_card = project(card_point, camera)
        result = {
            "actor_candidate": {
                "pixel": [u, v],
                "depth_m": depth_m,
                "point_world_m": measured["point_world_m"],
            },
            "evaluator_posthoc": {
                "card_root_world_m": card_point,
                "card_root_projected_pixel_depth": projected_card,
                "world_error_m": float(np.linalg.norm(candidate_point - np.asarray(card_point))),
                "pixel_error": [u - projected_card[0], v - projected_card[1]],
            },
            "privileged_pose_used_for_control": False,
            "motion_actions": backend._actions,
            "warning": "post-hoc diagnostic only; hidden pose was read after measurement",
        }
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    finally:
        os._exit(0)


if __name__ == "__main__":
    main()
