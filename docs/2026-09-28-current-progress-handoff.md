# Embodied Technical Work: Current Progress Handoff

Date: 2026-09-28

This document is a self-contained handoff for the next research agent. It
summarizes the current EmbodiedSWE-based project, the evidence collected so
far, the remaining limitations, and the next experiments. It supersedes no
implementation; it is a status and experiment guide.

## Project

The project tests whether a coding agent can diagnose and repair a simulated
server through physical robot interaction, then reuse verified programs and
experience. The current primary demonstration is a faulty GPU card that must
be diagnosed, grasped, staged, seated, released, and digitally verified.

Repositories and runtime:

- Public repository: `https://github.com/AranKomat/codex-embodied-technical-work`
- Local outer repository: `/Users/macbookpro/Developer/random/gpu/embodied-technical-work`
- Upstream simulator: EmbodiedSWE at commit `d34837e99e5016525f0e9b6bb84791eb3d4b8162`
- Remote GPU host: one RTX 4090 at `85.218.235.6`, SSH port `36259`
- Remote upstream checkout: `/workspace/codex-embodied-technical-work/EmbodiedSWE`
- Simulator: Isaac Sim 5.1.0 / Isaac Lab 2.3.2
- GPU driver: `580.178.04`
- Critical-run model: `gpt-6-astra`

The nested EmbodiedSWE checkout contains intentional, uncommitted
capability-mode changes for server repair. Do not reset or overwrite that
checkout wholesale.

## Executive Status

### Strongly demonstrated

1. GPT-6 Astra generated a complete privileged-simulator server-repair
   program that passed independent physical and digital checks.
2. The frozen program passed `6/6` same-fixture randomized grader trajectories
   across seeds 0 and 1, with score `1.0` in every trajectory.
3. The same frozen program passed a deliberate 10 mm loose-card XY reset-jitter
   holdout, `3/3`, with score `1.0`.
4. A persistent live-session service, RGB-D observation contract, calibrated
   deprojection path, and task-specific realistic server-repair observation
   bridge are implemented and tested.

### Partially demonstrated

1. A no-privilege RGB-D-driven server-repair path can capture observations and
   issue bounded actions, but the current localization baseline is too
   inaccurate for manipulation. Post-hoc error was `7.85 cm` to the hidden card
   root.
2. OSC and Diff-IK controller comparisons were useful for diagnosis but neither
   reached the sensor-derived hover target. Longer Diff-IK execution did not
   remove the position residual, so controller-cap sweeps are stopped.
3. The bulb task showed capability but not robust generalization: an initial
   Sol run scored `0.6667`, Astra produced one nominal success, and the held-out
   Astra result was `1/3`.

### Still open

- A formal matched R2 comparison between frozen and interactive recovery.
- Interactive recovery with prior successful artifacts supplied as experience.
- Recompiling an interactive recovery into a new frozen program and retesting.
- Different faulty components, layouts, and robot initializations for R1.
- Realistic manipulation without privileged object pose, contact, or clearance.
- Transfer to a different embodiment or a real robot.

## Model Decision

Use GPT-6 Astra for benchmark-critical solving, recovery, and the visible hero
demo. Astra produced the qualified server-repair program and is the only model
with the current strong end-to-end evidence.

Opus 5.5 was useful for cheaper exploration and debugging, but the observed
trial did not produce a verified end-to-end bulb success. This is an operational
choice, not a universal ranking claim:

- use Opus 5.5 when exploratory failure is acceptable;
- use Astra for final solving, recovery, and claims;
- do not spend another broad model tournament before completing the R2
  experiment sequence.

GPT-6 Luna is removed from the active plan. No result should be described as
an Astra result unless the run command and artifact identify `gpt-6-astra`.

## Completed Work and Evidence

### Phase 0: upstream and smoke reproduction

The upstream EmbodiedSWE substrate was inspected and reproduced sufficiently
to establish the environment and run the initial bulb smoke. The historical
bulb smoke scored `0.6667`. The project then moved to a deliberately small
server-repair capability experiment rather than expanding the architecture.

Relevant source and reports:

- `EXPERIMENT_MANIFEST.md`
- `docs/2026-09-27-demo-first-handoff.md`
- `docs/2026-09-27-r1-status.md`

### Phase 1: privileged server-repair demo

The server-repair capability mode adds a faulty GPU-card condition, a
diagnostic interface, and a grader alias. The successful Astra program used
this sequence:

1. diagnose the missing or unseated GPU;
2. grasp and lift the card;
3. stage it in clear interior space;
4. align with the slot;
5. slide rearward and press to seat;
6. release and retract;
7. rerun the digital healthcheck.

The key correction was geometric staging. Earlier paths descended into the
case before the card was aligned and failed insertion. The successful program
aligned in clear interior space first, then inserted and pressed.

Independent evaluation passed both the physical seating/release criteria and
the digital healthcheck. The primary artifacts are:

- `artifacts/server_repair_demo_20260927/`
- `artifacts/server_repair_demo_20260927/frozen_solution/`
- `docs/2026-09-27-demo-first-progress.md`
- `docs/2026-09-27-phase1-server-repair.md`

This is a valid privileged-simulation success. It is not a realistic RGB-D
success and is not evidence of real-robot transfer.

### Phase 2: frozen-program grading and initial generalization

The generated program was frozen and graded without additional model calls:

| Evaluation | Result | Score |
| --- | ---: | ---: |
| Seed 0, three environments | `3/3` | `1.0` mean/min/max |
| Seed 1, three environments | `3/3` | `1.0` mean/min/max |
| Combined | `6/6` | `1.0` everywhere |

The same frozen program then passed a structural reset-jitter variant with up
to 10 mm XY jitter applied to the loose card:

- registered task: `assembly.server_repair_jitter.franka.osc`;
- seed 2, three environments;
- result: `3/3`, score mean/min/max `1.0 / 1.0 / 1.0`;
- artifact: `artifacts/r1_frozen_grade_jitter10mm_seed2/`.

This is useful initial-state robustness evidence, but it is still one fixture
family. Different components, chassis layouts, robot starts, and broader
distribution shifts remain untested. A staged-USD permission issue blocked an
earlier attempt; the build path now normalizes completed staged assets to
readable permissions, and the successful retry is authoritative.

### Persistent live-session substrate

The outer repository contains `live_session/`, which provides a persistent
simulator process and bounded client commands. It includes:

- one server process owning the simulator backend;
- independent clients sharing one session without reset;
- session IDs and monotonic request sequence numbers;
- append-only JSONL request traces;
- realistic mode that withholds exact task-object poses and hidden success;
- RGB-D, calibration, proprioception, and measurement validation.

The local test suite currently has five passing tests. Run:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q live_session scripts
git diff --check
```

### Realistic RGB-D bridge

The realistic backend now supports both bulb and server-repair scenes through
the public observation contract. A no-motion server-repair probe returned:

- RGB shape `480 x 640 x 4`;
- depth shape `480 x 640`;
- explicit intrinsics and camera-to-world transform;
- joint position/velocity, end-effector pose, and gripper state;
- no exact card/case pose;
- no contact signal;
- zero motion actions.

Depth and image geometry were corrected during this work:

- use `distance_to_image_plane`, not Euclidean `distance_to_camera`, for the
  axial-depth deprojection helper;
- image-down maps to negative camera-Y in `live_session/rgbd.py`;
- an off-center deprojection regression test covers the sign convention.

The bridge is therefore a real sensor-contract result, but not a successful
realistic manipulation result. Details are in:

- `docs/2026-09-28-realistic-server-repair-bridge.md`
- `artifacts/realistic_server_repair_20260928/`

### Realistic localization and controller probe

A transparent RGB-plus-depth baseline selected a plausible card-colored region
without using hidden pose:

- candidate pixel center approximately `(315.1, 408.1)`;
- median axial depth `1.8048 m`;
- deprojected point `[0.2881, -0.3388, -0.0444]` m;
- zero motion during localization.

Using that point as a hover target produced the following bounded results:

| Controller | Steps | Position error | Rotation error | Reached |
| --- | ---: | ---: | ---: | --- |
| OSC | 80 | `5.96 cm` | `0.679 rad` | no |
| Diff-IK | 80 | `25.04 cm` | `0.00061 rad` | no |
| Diff-IK | 250 | `5.79 cm` | `0.060 rad` | no |

The longer Diff-IK run rules out a simple action-cap explanation. It does not
identify whether the remaining problem is target-frame bias, localization
error, an unobserved obstacle, or motion-law behavior. Contact and clearance
are unavailable, so the run must not be interpreted as a collision or grasp
failure.

An evaluator-only post-hoc comparison read the hidden card pose only after the
actor-side candidate had been computed. The candidate was `0.0785 m` from the
card root, with projected pixel error about `(5.85, 13.86)` pixels. Hidden pose
was not used for control. This is sufficient evidence that the current simple
localization baseline is inadequate; do not continue motion-cap micro-sweeps.

### Bulb task and cheaper-model exploration

The bulb task was useful as a substrate smoke and model exploration task, but
not as the headline result:

- Sol initial run: score `0.6667`, with final threading failure;
- Astra: one nominal success;
- held-out Astra: `1/3` successes;
- dominant observed failure: bulb loss during regrasp.

Opus 5.5 helped with debugging and exploration but did not produce a verified
end-to-end bulb success in the observed trial. This supports using it as a
cheap exploration model and Astra for claims, while avoiding an unsupported
claim that the model comparison is fully benchmarked.

## R2 Exploratory Run (Archived)

A fresh bounded Astra run was launched for exploratory interactive comparison
and has now been archived before stopping the GPU instance:

```text
experiment: experiments/phase1_server_repair_single
run:        r2_codex_astra_fresh
model:      gpt-6-astra
budget:     20 minutes
command:
.venv/bin/python eval/scripts/run_agent.py \
  experiments/phase1_server_repair_single \
  --agent codex \
  --model gpt-6-astra \
  --budget-min 20 \
  --auto-submit-min 5 \
  --keep-going \
  --run r2_codex_astra_fresh
```

The container was stopped intentionally at about 17 minutes, before the
20-minute budget and before a formal grader verdict. It exited with code 143.
The local archive is:

- `artifacts/r2_codex_astra_fresh_20260928/`
- archive SHA-256:
  `c0a48b370ed8b1af1801a8114b301d0583d07874782809d1cff985ca1396dd0c`

The snapshot contains six failed attempts, checkpoints, assessments, footage,
and the latest candidate solution. The latest attempt reached the card but
closed over its top edge without lifting it; the assessment recommended using
the measured slab aperture and maintaining the pinch. Earlier attempts included
a joint-limit failure and an empty-air closure. No successful submission or
fresh-reset grade was produced.

This is exploratory failure evidence, not an R2 completion result. Full details
are in `artifacts/r2_codex_astra_fresh_20260928/README.md`.

## Intended R2 Design

The formal comparison is:

| Condition | Input to the agent |
| --- | --- |
| Frozen | prewritten `solve()` only |
| Interactive | Astra observes and emits bounded recovery code/actions |
| Interactive + prior experience | interactive agent also receives prior successful artifacts |
| Recompiled | interactive recovery integrated into a new frozen program and retested |

The current fresh Astra run is not automatically a formal ablation. It is a
fresh solve on the baseline fixture and may differ in budget, prompt history,
or available artifacts. Report it as exploratory unless matched controls are
recorded.

Recommended order after the current run:

1. preserve and grade the fresh interactive run;
2. run the matched frozen baseline under the same fixture and budget policy;
3. run interactive recovery with the same initial condition;
4. repeat with the prior successful repair artifact supplied explicitly;
5. freeze the recovered program and grade it without further model calls;
6. compare success, repair latency, number of retries, action count, and
   whether the recovery generalizes beyond the original fixture.

Do not call R2 complete from the current run alone.

## What Is Blocked and Why

The central realistic blocker is not currently the choice of grasp generator or
VLA policy. It is evidence quality at the perception/control boundary:

- RGB-D capture and calibration work;
- the simple visual candidate is biased by `7.85 cm` relative to hidden truth;
- OSC and Diff-IK expose different residuals but neither reaches the target;
- contact and external clearance are not available through the legal actor
  interface;
- therefore a manipulation success cannot yet be attributed cleanly to
  perception, reachability, collision avoidance, or grasp control.

The project should not claim realistic no-privilege server repair, contact-aware
manipulation, robust transfer across layouts, or real-robot validation.

The privileged path is not blocked: it already has a credible demo and initial
frozen generalization. The next high-value result is a disciplined R2
interactive-versus-frozen comparison, not another sequence of tiny controller
or prompt sweeps.

## Recommended Next Actions

1. Resume from the archived Astra exploratory snapshot only when a GPU is
   available, using its aperture diagnosis rather than restarting the same
   failed grasp probes.
2. Update `EXPERIMENT_MANIFEST.md` with any resumed run ID, model, budget,
   outcome, and artifact path.
3. Run the matched frozen baseline and interactive comparison under the same
   fixture and budget policy.
4. Repeat interactive recovery with the prior successful repair artifact
   supplied explicitly, then freeze and grade the recovered program.
5. Run the local tests and syntax checks listed above.
6. Commit and push the report and any new artifacts.
7. Only then choose between completing the matched R2 sequence or packaging
   the realistic localization blocker as a boundary result.

## Claim Boundary

The strongest defensible current claim is:

> In privileged EmbodiedSWE simulation, GPT-6 Astra generated a staged robot
> program that diagnosed and repaired a simulated unseated GPU, passed
> independent physical and digital checks, and replayed successfully in six
> same-fixture trajectories plus a deliberate 10 mm card-reset holdout. A
> realistic RGB-D/proprioceptive bridge now works, but simple localization is
> insufficient for reliable sensor-derived manipulation and contact/clearance
> remain unavailable.

Do not claim that the realistic bridge repaired the server, that R2 is complete,
that Opus is equivalent to Astra, or that the system transfers to real robots.
