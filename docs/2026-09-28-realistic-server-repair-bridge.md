# Realistic Server-Repair Observation Bridge

Date: 2026-09-28

## Scope

This is a bounded, no-motion probe of the server-repair scene through the
actor-facing realistic session interface. It does not claim a repair and does
not expose the card or case pose to control.

## Result

The probe launched `assembly.server_repair.franka.osc` with
`mode=realistic` and returned:

- RGB-D available: `true`;
- RGB shape: `480 x 640 x 4`;
- depth shape: `480 x 640`;
- explicit pinhole intrinsics and camera-to-world transform;
- robot joint position/velocity, end-effector pose, and gripper state;
- exact card pose: withheld;
- exact case pose: withheld;
- contact V0: unavailable;
- motion actions: `0`.

The observation was written to an `.npz` file and the JSON receipt was archived
under [`../artifacts/realistic_server_repair_20260928/`](../artifacts/realistic_server_repair_20260928/).

## Interpretation

This closes the missing task-specific observation-substrate check: the
server-repair fixture can now be exposed through the same realistic RGB-D and
proprioception boundary previously verified on the bulb fixture. It does not
close realistic execution. The next experiment must use only the RGB-D,
calibration, and proprioceptive signals to localize the card and case well
enough for a bounded action, or record a clean localization blocker.

The fixed camera currently views the scene from `[1.3, -1.4, 1.2]` m toward
`[0.0, 0.0, 0.5]` m. Camera coverage and task-specific localization have not yet
been optimized. No privileged evaluator state was used by the probe.

## Bounded localization attempt

A second no-motion pass used only RGB contrast and finite depth as a transparent
baseline. It selected a small chromatic candidate in the lower work surface:

- pixel bounding box: `[288, 388, 343, 420]`;
- weighted pixel center: approximately `(315.1, 408.1)`;
- median axial camera-Z depth: `1.8048 m`;
- corrected public RGB-D deprojection: `[0.2881, -0.3388, -0.0444]` m;
- motion actions: `0`;
- privileged pose used: `false`.

The candidate overlaps the visible card in the retained frame, but there is no
independent target-pose check in this condition. Treat it as a plausible
observation-derived anchor, not a localization success. The authoritative
corrected receipt is `realistic_server_repair_localization_v3.json` in the
artifact directory.

### Geometry correction

The first two receipts are retained for provenance but are superseded. The
provider initially used Euclidean `distance_to_camera` with a helper that
expects axial camera-Z depth, and the helper also used the wrong sign for image
Y. The provider now uses `distance_to_image_plane`, and image-down maps to
negative camera Y. The off-center RGB-D regression test covers the latter.

## Bounded Observation-Driven Action

Using the corrected candidate, a separate run commanded one hover target 20 cm
above the measured point. It preserved the observed end-effector orientation,
allowed at most 80 controller steps, and made no contact/manipulation request.
The result was:

- target: `[0.2930, -0.3347, 0.1525]` m;
- final position error: `0.0596 m`;
- final rotation error: `0.679 rad`;
- controller reached target: `false`;
- actions: `80`;
- clearance certified: `false`;
- contact available: `false`;
- privileged pose used: `false`.

This is a useful bounded failure: the sensor-derived anchor can drive the
existing motion helper toward the work area, but the current helper does not
maintain the requested orientation or reach the hover target within its cap.
Do not increase the action cap or attempt insertion until the motion/clearance
contract is deliberately addressed. The artifact is under
`artifacts/realistic_server_repair_20260928/hover/`.

## Implementation

`live_session/embodiedswe_backend.py` now supports:

```text
build_bulb(mode=...)
build_server_repair(mode=...)
```

Both use the same `BulbBackend` motion/observation contract; only the
development-only privileged labels differ. In realistic mode, neither task
returns hidden object poses.
