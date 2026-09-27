# Phase 1 Server-Repair Result

The first valid Codex run was `phase1_codex_sol_02` on the sibling
EmbodiedSWE checkout, branch `exp/technical-worker-server-repair`, commit
`0a82517`. The run used the capability-mode server-repair fixture: a Franka,
an upright GPU card in a holder, a hidden diagnostic tool, and a strict seated
grader. The earlier `phase1_codex_sol_01` run is invalid because it used the
default condition and did not receive the server-diagnostics tool.

## Outcome

The agent successfully diagnosed the initial fault, corrected a grasp-width
mistake, welded onto the card at a 36.4 mm aperture, and lifted it. The complete
repair did not pass: later carry/insertion attempts reached the case interior
but failed the strict 3 mm XY, 3 degree orientation, and 4 mm depth seat gate.
The final diagnostic remained `FAIL: GPU 1 not detected`.

The strongest final trace ended at card position approximately
`[0.4280, 0.0276, 0.0324]` versus a seat target near
`[0.4841, 0.0293, 0.0319]`, with an invalid orientation and `seated=False`.
This is a real partial capability result, not a benchmark success.

## Diagnosis

The current blocker is the coupled Franka OSC carry/insertion maneuver. Position-
only actions allow the welded card to rotate; late reorientation drives the arm
near a joint limit and does not restore the required pose. A fixed-orientation
carry improved entry into the case but still did not maintain the seat pose.
The next justified test is one registered `diff_ik` controller comparison using
the already-successful grasp geometry. Do not expand perception or train a VLA
until this capability slice either succeeds or is formally blocked.

That comparison was run on the same reset. `diff_ik` was materially better than
OSC: the card stayed within roughly 2 degrees of upright, reached the press
depth, and avoided the OSC joint-limit warning. It nevertheless stopped about
6 mm short in X and 7 mm short in Y. One measured final-offset correction was
replayed from the saved lift checkpoint; it did not materially change the
endpoint. The capability slice is therefore still incomplete, but the main
controller bottleneck is now narrowed to final Cartesian calibration/approach,
not basic grasping, reach, or orientation tracking.

## Infrastructure

The keep-going verifier independently failed before calling `solve()` because
the read-only benchmark mount lacked a writable `/bench/.cache` lock directory.
`eval/scripts/run_agent.py` now allocates and mounts a per-run `asset-cache`,
matching the grading runner's existing behavior. This needs one fresh-run
validation before verifier failures are treated as experiment results.

## Subsequent corrected result

The historical result above was superseded by a clearance-aware staged insertion
path. The corrected path first moved the held card into a clear interior staging
pose, confirmed alignment, slid rearward, pressed to seat, released, and
withdrew the gripper. A fresh integrated replay passed all three stages, physical
seating, gripper clearance, and the digital healthcheck. A separate three-
environment holdout also passed all of those gates. The complete evidence is
archived in [`../artifacts/server_repair_demo_20260927/`](../artifacts/server_repair_demo_20260927/).

This does not remove the historical failure: it records why the original path
failed and why the corrected controller is a meaningful measured update rather
than a claim that the general robotics stack is solved.
