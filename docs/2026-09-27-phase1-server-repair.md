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

## Infrastructure

The keep-going verifier independently failed before calling `solve()` because
the read-only benchmark mount lacked a writable `/bench/.cache` lock directory.
`eval/scripts/run_agent.py` now allocates and mounts a per-run `asset-cache`,
matching the grading runner's existing behavior. This needs one fresh-run
validation before verifier failures are treated as experiment results.
