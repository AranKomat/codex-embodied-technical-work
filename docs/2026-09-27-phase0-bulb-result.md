# Phase 0 Bulb Result

Date: 2026-09-27

The first fresh-reset technical-worker trial used `assembly.bulb.franka.osc`
on one RTX 4090 with Isaac Sim 5.1.0 / Isaac Lab 2.3.2 and `gpt-6-sol` via
the authenticated Codex transport.

The agent discovered a working grasp/lift controller. The independent grader
confirmed:

| Stage | Result |
| --- | --- |
| Lifted and held | pass |
| Engaged/aligned with socket | pass |
| Threaded/seated | fail |

The fresh grade was seed `0`, one environment, score `0.6667`, task success
`false`, with `815` simulation steps and about `348` seconds wall time. This
is a meaningful partial result, not a full task solve.

A follow-up that reversed the yaw direction and reduced the rotation increment
also scored `0.6667`; its bulb axis alignment degraded during the sweep. The
failure is therefore localized to the final contact-aware threading phase,
not the initial grasp or approach.

The grading path also required three reproducibility repairs: writable asset
lock/output directories for the non-root grader, selection of the run-local
asset mirror, and empty-articulation velocity handling in checkpoint health.
Those repairs are recorded in the EmbodiedSWE experiment branch as local
commit `da97e5a`; the upstream EmbodiedSWE remote currently rejects pushes
from this account, so that branch remains local until an authorized remote is
available.

Next: instrument the public socket-relative depth and axis state during the
screw phase, use small alternating yaw increments with alignment recovery,
rerun the same seed, and only then test a held-out seed.

