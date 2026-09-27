# Realistic Bridge Probe

Date: 2026-09-27

## Scope

This was the first bounded realism-bridge probe after the privileged server-repair demo. It launched the bulb backend in `mode=realistic`, performed no robot motion, and queried the actor-facing `state`, `observe`, and `contact` interfaces.

## Initial boundary

- Proprioception was available: joint positions/velocities, end-effector pose, and gripper position were returned.
- Exact bulb and socket poses were absent from the returned state.
- RGB-D was initially unavailable because the backend launched Isaac without the
  camera extension and then had a response-field mismatch after capture.
- Contact V0 was unavailable: `available=false`, `quality=unavailable`.
- Motion action count remained zero.

The raw probe output is archived under [`../artifacts/realistic_bridge_20260927/`](../artifacts/realistic_bridge_20260927/).

## Interpretation

This initial result was a useful adapter diagnosis, not a failed robotics trial.
The camera-launch and response-contract issues were fixed in the existing
backend. A repeat of the same no-motion probe then returned `available=true`
with a 640x480 RGB frame and 640x480 depth frame, both stored in one `.npz`
observation record, while still withholding exact bulb/socket poses. The
repeat's JSON and frame are archived alongside the initial result.

The bridge is therefore one step further along but not complete: camera data is
now available, while contact sensing, calibration validation, target/slot
localization, and a sensor-derived repair attempt remain open. Contact,
segmentation, K1, GraspGen-X, and VLA infrastructure remain out of scope until
the RGB-D-derived geometry path is measured.
