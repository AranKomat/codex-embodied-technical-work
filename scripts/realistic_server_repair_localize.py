"""Bounded RGB-D candidate localization for the server-repair bridge.

This is deliberately a weak, transparent baseline: it uses only RGB color
contrast and finite depth from the actor-facing observation. The output is a
candidate point, never a privileged object pose or a motion authorization.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from live_session.embodiedswe_backend import build_server_repair


def _candidate(rgb: np.ndarray, depth: np.ndarray) -> dict:
    # The card's exposed board/backplate is more chromatic than the neutral
    # table/case in this fixture. Keep the heuristic bounded to the lower work
    # surface and require measured depth.
    saturation = rgb.astype(np.int16).max(axis=2) - rgb.astype(np.int16).min(axis=2)
    yy = np.indices(saturation.shape)[0]
    mask = (saturation >= 30) & (yy >= 250) & np.isfinite(depth) & (depth > 0)
    ys, xs = np.where(mask)
    if len(xs) == 0:
        raise RuntimeError("no finite high-contrast candidate pixels")
    weights = saturation[ys, xs].astype(np.float64)
    return {
        "pixel": [float(np.average(xs, weights=weights)), float(np.average(ys, weights=weights))],
        "bbox_xyxy": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
        "pixel_count": int(len(xs)),
        "depth_m_median": float(np.median(depth[ys, xs])),
    }


def main() -> None:
    output = Path("realistic_server_repair_localization.json")
    backend = build_server_repair(mode="realistic")
    try:
        observation = backend.dispatch("observe", {"cameras": [], "depth": True})
        camera = observation["cameras"][0]
        data = np.load(camera["frame_path"])
        candidate = _candidate(data["rgb"][..., :3], data["depth"])
        u, v = candidate["pixel"]
        # Use the public request path, rather than accessing simulator state.
        measured = backend.dispatch(
            "locate_measure",
            {
                "observation": camera,
                "u": u,
                "v": v,
                "depth_m": candidate["depth_m_median"],
            },
        )
        result = {
            "task": "server_repair",
            "mode": "realistic",
            "method": "rgb_saturation_plus_finite_depth",
            "candidate": candidate,
            "measurement": measured,
            "motion_actions": backend._actions,
            "privileged_pose_used": False,
        }
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    finally:
        backend.close()


if __name__ == "__main__":
    main()
    import os
    os._exit(0)
