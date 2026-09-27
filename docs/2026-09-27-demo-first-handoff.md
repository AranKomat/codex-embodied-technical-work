# Codex Embodied Technical Work: Demo-First Handoff

Date: 2026-09-27

## Purpose

This document gives the next research agent a self-contained account of the
current EmbodiedSWE project, the evidence already obtained, the claims that are
and are not justified, and the next experiments. It follows the superseding
demo-first plan in `CODEX_EMBODIED_DEMO_FIRST_HANDOFF_20260927.md`.

The near-term objective is one clear autonomous technical-work demonstration:

```text
diagnose an unhealthy training node
-> identify a physical GPU fault
-> write and execute robot control code
-> seat the GPU card
-> rerun diagnostics
-> independently verify the physical and digital result
```

The first privileged-simulator version of that demonstration now works. The
next work should package it clearly and add one bounded realism result, not
expand the architecture.

## Repository and Runtime

- Public repository: `https://github.com/AranKomat/codex-embodied-technical-work`
- Local outer repository: `/Users/macbookpro/Developer/random/gpu/embodied-technical-work`
- Primary upstream: EmbodiedSWE at `d34837e99e5016525f0e9b6bb84791eb3d4b8162`
- Current GPU host: one RTX 4090 at `root@85.218.235.6`, SSH port `36259`
- Remote checkout: `/workspace/codex-embodied-technical-work/EmbodiedSWE`
- Simulator: Isaac Sim 5.1.0 / Isaac Lab 2.3.2
- GPU driver: `580.178.04`
- Main critical-run model: `gpt-6-astra`

The nested EmbodiedSWE checkout contains intentional uncommitted capability-mode
changes for server repair. Do not reset or overwrite them wholesale.

## Model Decision

### Astra

Use GPT-6 Astra for benchmark-critical agent runs and the visible hero demo.
Astra produced the corrected server-repair program that passed the integrated
replay, the three-environment holdout, and subsequent frozen grading.

### Opus 5.5

Opus 5.5 was tested as a cheaper exploration and debugging model. It was useful
for iterative work but did not produce a verified end-to-end bulb success in
the observed trial. That evidence is enough for an operational decision, not a
claim that Astra dominates on every task:

- use Opus 5.5 for lower-cost exploration when failure is acceptable;
- use Astra for final benchmark-critical solving and recovery;
- do not spend more GPU time on a broad model tournament before packaging the
  already-qualified demo.

Luna is not part of the active plan.

## Qualified Results

### 1. Persistent live-session substrate

The outer repository implements a persistent execution service under
`live_session/`:

- one server process owns the simulator backend;
- independent clients issue bounded commands over a Unix socket;
- every request receives a session ID, monotonic sequence number, and receipt;
- an append-only JSONL trace records accepted and rejected requests;
- realistic mode withholds exact task-object poses and hidden success state.

Two independent clients were verified to address the same persistent simulator
session and observe progressed state without a reset. The test suite currently
contains four passing tests covering process sharing, RGB-D deprojection,
invalid depth, and `locate_measure` validation.

### 2. Flagship server repair

The corrected Astra-generated program completed a fresh integrated replay:

- diagnosis identified the missing GPU;
- stage 1 grasped and lifted the card;
- stage 2 moved it into a clear case-interior alignment pose;
- stage 3 confirmed alignment, slid rearward, pressed to seat, released, and
  retracted the gripper;
- the physical evaluator reported the card seated and no longer grasped;
- the digital healthcheck reported `PASS`.

The crucial controller correction was geometric staging. The earlier path
descended into the case before alignment. The successful path first aligned in
clear interior space, then performed the rearward insertion and press.

Primary artifacts:

- `artifacts/server_repair_demo_20260927/`
- `artifacts/server_repair_demo_20260927/frozen_solution/`
- `docs/2026-09-27-demo-first-progress.md`
- `docs/2026-09-27-phase1-server-repair.md`

The artifact folder includes the frozen `solve.py`, controller helpers, stage
modules, raw logs, and a ten-frame visual trace.

### 3. Frozen generalization

The frozen program was graded without additional model calls:

| Grade | Environments | Result | Mean score |
|---|---:|---:|---:|
| Seed 0 | 3 | 3/3 | 1.0 |
| Seed 1 | 3 | 3/3 | 1.0 |
| Combined | 6 | 6/6 | 1.0 |

All trajectories passed grasped, aligned, pressed, final seating, gripper
release, and healthcheck criteria. Artifacts are under
`artifacts/r1_frozen_grade_seed0/` and
`artifacts/r1_frozen_grade_seed1/`.

This is strong evidence inside one fixture family. It is not yet evidence for a
different component, deliberate layout offset, staging-position shift, or
initial robot configuration.

A deliberate structural holdout then registered
`assembly.server_repair_jitter.franka.osc`, preserving the fixture while
applying up to 10 mm of loose-card XY reset jitter. The unchanged frozen
solution passed:

- seed 2;
- three environments;
- `3/3` success;
- score mean/min/max `1.0 / 1.0 / 1.0`.

The receipt is archived under
`artifacts/r1_frozen_grade_jitter10mm_seed2/`. The first attempt was blocked
before simulation by root-only staged USD permissions; the build path now
normalizes permissions after the complete extraction/boot-repair loop, and a
permission-check build confirmed readable mode `0644`. This adds evidence for
small initial-state variation, but different components, chassis layouts, and
robot configurations remain untested.

### 4. Realistic RGB-D substrate

The realistic live backend now launches Isaac with cameras enabled and returns:

- `480 x 640 x 4` RGB;
- `480 x 640` depth;
- explicit intrinsics and camera-to-world transform;
- robot proprioception;
- no exact bulb/socket pose and no hidden task-success predicate.

`live_session/rgbd.py` provides calibrated pixel deprojection. A synthetic
center-pixel sample at 1 m produced `[0.6611, -0.7119, 0.8560]` m, consistent
with the declared camera pose. `locate_measure` exposes the measurement contract
without silently substituting simulator truth.

Artifacts and report:

- `artifacts/realistic_bridge_20260927/`
- `docs/2026-09-27-realistic-bridge.md`

Important limitation: the retained realistic frame comes from the bulb backend.
This qualifies the sensor and geometry substrate, not a no-privilege server
repair. Contact remains unavailable.

The same boundary has now been probed on the server-repair fixture. The
no-motion probe returned RGB-D, calibration, and proprioception while
withholding exact card/case poses; contact remained unavailable. Its receipt is
under `artifacts/realistic_server_repair_20260928/`, with details in
`docs/2026-09-28-realistic-server-repair-bridge.md`. This closes the
task-specific observation-substrate check, not the realistic repair task.

A transparent RGB-plus-depth baseline then generated a plausible card-region
candidate at pixel `(315.1, 408.1)` and, after correcting the axial-depth and
image-Y conventions, deprojected it to `[0.2881, -0.3388, -0.0444]` m through
the public measurement path. This used zero motion and no privileged pose; it
is a candidate anchor, not an independently verified localization success.
The earlier, superseded geometry receipts remain archived for provenance.

One bounded hover action then used that measured point without privileged state.
The arm moved toward a target 20 cm above the candidate for 80 capped steps,
but ended with `0.0596 m` position error and `0.679 rad` rotation error. No
contact or clearance certification was available. This is a concrete realistic
bridge failure, not a benchmark failure: the current motion helper does not
yet preserve orientation/reachability well enough for a sensor-derived action.

A matched Diff-IK hover comparison preserved orientation (`0.00061 rad` error)
but ended at `0.2504 m` position error, versus OSC's `0.0596 m` position and
`0.679 rad` rotation error. This separates the realistic blocker into a
position/reach or target-frame issue plus an OSC orientation issue; it does not
justify adding a learned policy before the motion contract is clarified.

A 250-step Diff-IK run still ended `0.0579 m` from the target with `0.060 rad`
rotation error. Longer execution therefore did not solve the position residual;
stop spending time on cap sweeps. The remaining realistic question is whether
the RGB-D point is biased, the direct path meets unobserved geometry, or the
motion helper has a reachability/frame defect. Contact and clearance evidence
are required to distinguish these cases.

An evaluator-only post-hoc comparison then measured the actor-side RGB-D
candidate against the hidden card root: `0.0785 m` world error and roughly
`(5.85, 13.86)` pixel projection error. The hidden pose was read only after
the actor measurement and never used for control. This closes the current
realistic-bridge diagnosis: the simple localization baseline is insufficient,
so motion-cap sweeps stop here. A future realistic branch needs stronger
localization; otherwise the project should package this limitation and proceed
to R2, the interactive-versus-frozen recovery comparison.

## Negative and Partial Results

### Bulb task

- Initial Sol run: score `0.6667`, final threading failed.
- Astra produced one nominal success.
- Held-out Astra result: `1/3` successes.
- The dominant failure was loss of the bulb during regrasp, not high-level task
  misunderstanding.

The bulb result demonstrates capability but is not robust enough to be the
flagship claim.

### Early server-repair paths

- Sol diagnosed, grasped, lifted, and carried the card but did not seat it.
- The original OSC path allowed orientation drift.
- Diff-IK improved orientation tracking but still stopped several millimetres
  from the required final pose.
- The final successful Astra program used the staged clearance-aware path
  described above.

### Structural jitter holdout attempt

A registered `assembly.server_repair_jitter.franka.osc` variant now exists in
the working tree. It preserves the fixture but applies up to 10 mm of loose-card
XY reset jitter. The experiment boot validation passed.

The first frozen grade, seed 2 with three environments, did **not** evaluate the
controller. The grading container stopped while hashing an unrelated vendored
asset:

```text
PermissionError: [Errno 13] Permission denied:
/bench/robobench/suites/assembly/assets/allen_bolt/allen_bolt_m16.usd
```

Therefore this is an infrastructure-blocked attempt, not a failed
generalization result. Remote diagnostic artifacts currently reside at:

- `/workspace/r1_grade_jitter10mm_seed2/`
- `/workspace/codex-embodied-technical-work/EmbodiedSWE/experiments/r1_server_repair_jitter10mm/`

## What Is Settled for Now

- The coding-agent approach can produce a complete physically coupled repair in
  this simulator.
- Classical task-space control is sufficient for the current flagship; a VLA,
  GraspGen-X, SAM, or a new skill architecture is not required for the demo.
- Staged programs and checkpoints are useful for preserving successful prefixes
  and debugging later physical phases.
- Compact, explicit execution interfaces are preferable to a large library of
  task-specific skills.
- Astra is the current critical-run choice; Opus 5.5 is a cost-saving exploration
  option.
- The qualified demo is privileged-simulation evidence. It must not be described
  as a realistic-perception or real-robot result.

## Immediate Next Actions

Follow this order.

1. **Package the hero demo.** Produce a concise, readable sequence showing the
   user instruction, terminal diagnosis, generated robot program, measured
   physical stages, final seating, and healthcheck pass. Preserve the uncut log
   and exact provenance alongside any edited presentation.
2. **Run one bounded observation-driven action or stronger localization check.**
   Use only the server-repair RGB-D, calibration, and proprioception signals;
   keep clearance and target identity explicit. A cleanly localized failure is
   useful; do not expose simulator poses.
3. **Stop broadening after that attempt.** Package the result before starting
   contact sensing, SAM, K1, GraspGen-X, VLA training, or a new embodiment.

After those items, the longer research order is:

```text
R1 structural frozen-program generalization
-> R2 matched frozen vs interactive recovery
-> R3 experience/memory amortization
-> R4 realistic perception variants
-> R5 contact/force ablation
-> R6 second embodiment or physical hardware
-> R7 learned motor policy only for a measured residual
```

## Claim Boundary

Safe current claim:

> In an EmbodiedSWE privileged-simulation condition, GPT-6 Astra generated a
> staged robot program that diagnosed and repaired a simulated unseated GPU,
> passed independent physical and digital checks, and replayed successfully in
> six same-fixture grader trajectories. A separate realistic interface now
> exposes calibrated RGB-D and proprioception without exact object poses, but a
> sensor-derived server repair has not yet been demonstrated.

Do not currently claim:

- robust transfer across layouts or components;
- a successful no-privilege server repair;
- contact-aware manipulation;
- real-robot validation;
- that Opus 5.5 is generally inferior to Astra;
- that the 10 mm jitter variant failed the controller.

## Verification Commands

From the outer repository:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q live_session scripts
git diff --check
```

Expected current unit-test result: four tests pass.
