# Codex Embodied Technical Work: Experiment Handoff

**Date:** 2026-09-27  
**Project:** `codex-embodied-technical-work`  
**Purpose:** Give another research agent a self-contained, evidence-based status of the EmbodiedSWE technical-work campaign.

## Executive Summary

The project is promising, but it has not yet demonstrated the flagship result. We have shown that a coding agent can diagnose a simulated hardware fault, write a physically coupled manipulation program, recover from a grasp failure, and complete a bulb task under a fresh reset. We have not yet completed the server-repair task, measured frozen-program generalization on that task, or run the prior-code/trace/keyframe ablations.

The main lesson so far is that the high-level coding-agent approach is viable, while the final contact-sensitive motion is the bottleneck. Classical controllers remain useful. Diff-IK improved orientation tracking over the default operational-space controller, but the server-repair insertion still missed the final Cartesian seat by several millimetres. The current bulb solution passed one nominal run and holdout 1, but failed holdout 2 after losing the bulb during regrasp. Holdout 3 is now running under the agent's official sequence. Do not call the bulb solution generally robust.

## Provenance and Environment

| Item | Value |
|---|---|
| Outer repository | `codex-embodied-technical-work` |
| Current outer commit | `c3688a6` (`record diff ik comparison`) |
| EmbodiedSWE reference | `d34837e99e5016525f0e9b6bb84791eb3d4b8162` |
| EmbodiedSWE branch | `exp/technical-worker-server-repair` |
| Simulator | Isaac Sim 5.1.0 / Isaac Lab 2.3.2 |
| Host | Vast.ai, one RTX 4090 |
| Driver | `580.178.04` |
| Codex CLI | `0.157.1` on the experiment host |
| Current model | `gpt-6-astra` |
| Reasoning setting | No explicit flag in the upstream runner; host model metadata reported Astra default as `medium` |

The upstream runner uses `codex exec` with the model name, sandbox, and prompt, but does not explicitly set reasoning effort. The exact effective setting must therefore be recorded from the CLI configuration or made explicit in a future reproducibility run.

## What the Upstream Benchmark Provides

EmbodiedSWE is primarily a privileged-simulation coding-agent benchmark. The agent can inspect simulator state and use generic rendering and controller interfaces. Its arm controller choices include:

- operational-space control, the default for arm evaluations;
- differential IK, available for arm evaluations;
- Pink IK, used for humanoid evaluations;
- task-space impedance and direct joint targets.

The benchmark does not present GraspNet, GraspGen-X, Flux, or SAM as benchmark baselines. The paper's separate learning experiments use PPO with simulator state, SmolVLA in simulation, and pi0.5-DROID for a real lamp experiment. The coauthor's observation that perception becomes a bottleneck on real robots is relevant, but should not be confused with the privileged simulator result.

## Completed and Partially Completed Experiments

### Phase 0: Upstream reproduction and bulb capability

#### Initial Sol bulb run

- Task: `assembly.bulb.franka.osc`.
- Model: `gpt-6-sol`.
- Fresh grade: score `0.6667`, task success `false`.
- Lift and hold: passed.
- Socket approach/alignment: passed.
- Final threading/seating: failed.
- Runtime: approximately 348 seconds for 815 simulation steps.

This established that the environment, agent runner, controller, and grader work together, but the final threaded contact phase is difficult.

#### Astra adaptive controller

The Astra run initially found a working adaptive bulb controller. A development comparison found that an uncentered regrasp preserved accumulated lateral grasp error:

```text
approximately 1 mm -> 11 mm -> 18 mm -> 56 mm
```

The bulb was eventually lost. The fix was to recenter the grasp from the measured bulb center before each regrasp.

Comparison from the same development origin:

| Variant | Score | Result |
|---|---:|---|
| Centered regrasp, body-tilt feedback | `0.0269687 +/- 0.000045` | winner, `3/3` in the comparison |
| Centered regrasp plus absolute hand leveling | `0.360325 +/- 0.4714` | worse, `2/3` under the strict threshold |

The centered-only replay then passed:

- stage-2 checkpoint `n2` saved;
- final bulb height `26.99 mm` against a `27 mm` threshold;
- bulb upright;
- gripper open and clear;
- `scene_success=True`.

The fresh integrated nominal run also passed:

- both stages passed;
- `seated=True`;
- final height `26.99 mm`;
- upright axis approximately `[0.0003, 0.0001, 1.0]`;
- gripper opening `0.04 m`;
- runtime approximately `1350 s`.

#### Bulb held-out tests

Holdout 1 completed successfully:

- origin: fresh;
- instance: `holdout_1`;
- physics parameters: `(friction=0.008, glass=0.36, socket=0.65)`;
- both stages passed;
- final `seated=True` after gripper withdrawal;
- runtime `1063.9 s`.

Holdout 2 completed with a failure:

- origin: fresh;
- instance: `holdout_2`;
- initial grasp/lift and upright transition passed;
- after the first center turn, the bulb was lost;
- measured relative position jumped to roughly `[0.159, -0.088, 0.005]`;
- finger openings collapsed to `0.0001 m`;
- repeated recentering could not recover the object;
- final `seated=False`;
- runtime `1228.9 s`.

This is a real robustness failure, not merely a checkpoint warning. The centered-regrasp logic is therefore currently `nominal pass + holdout 1 pass + holdout 2 fail`.

Holdout 3 has been launched automatically by the agent after holdout 2. Its final verdict is pending and it is the only active simulator process that should be allowed to use the GPU.

There was one infrastructure mistake during holdout execution: a manual holdout-2 launch overlapped with the agent's automatically launched holdout-2. The manually launched duplicate was terminated; the agent-owned run is the surviving scored run. The duplicate's shutdown diagnostics must not be counted as a controller result. Holdout 3 is being run only by the agent-owned sequence.

### Phase 1: Server-repair capability task

The first capability-mode server-repair task uses an upright GPU card, a hidden diagnostic tool, a Franka arm, and a strict seated grader. The intended sequence is:

```text
diagnose missing GPU
-> grasp card
-> lift
-> carry to case
-> align and seat
-> rerun diagnostic
-> physical grader confirms repair
```

#### Initial server-repair run

- Model: `gpt-6-sol`.
- Diagnosis: passed.
- Grasp correction: passed after fixing grasp width.
- Card grasp and lift: passed.
- Carry/insertion: failed.
- Final diagnostic: `FAIL: GPU 1 not detected`.

The strongest final trace ended near card position `[0.4280, 0.0276, 0.0324]` versus a seat target near `[0.4841, 0.0293, 0.0319]`. The strict gate requires approximately 3 mm XY, 3 degrees orientation, and 4 mm depth. This is a real partial result, not a benchmark success.

The initial controller was operational-space control. Position-only carry actions allowed the card to rotate; late reorientation drove the arm near a joint limit.

#### Diff-IK comparison

The explicit comparison runner uses the registered environment `assembly.server_repair.franka.diff_ik` in [`diffik_weldframe_runner.py`](../diffik_weldframe_runner.py). It starts from the already successful grasp/lift checkpoint and holds the card orientation during carry and insertion.

Compared with OSC, Diff-IK:

- kept the card within roughly 2 degrees of upright;
- reached the press depth;
- avoided the OSC joint-limit warning;
- still stopped approximately 6 mm short in X and 7 mm short in Y.

A measured final-offset replay did not materially change the endpoint. The current diagnosis is final Cartesian calibration/approach, not basic reach, grasping, or orientation control.

#### Infrastructure repair

The keep-going verifier previously failed before calling `solve()` because the read-only benchmark mount lacked a writable `/bench/.cache` lock directory. The local runner was changed to allocate and mount a per-run asset cache. One fresh-run validation is still required before treating the verifier as fully repaired.

## Experimental Matrix Status

The handoff defines the following progression:

| Experiment | Intended condition | Status |
|---|---|---|
| E0 | Scratch, privileged, one known task | Partial/full bulb results; server-repair scratch result is partial |
| E1 | Scratch, privileged, held-out variants | Bulb holdout 1 passed, holdout 2 failed, holdout 3 in progress; server-repair holdout not started |
| E2 | Prior code, privileged, related task | Not started |
| E3 | Prior code plus semantic trace | Not started |
| E4 | Prior code plus trace and selected keyframes | Not started |
| E5 | Scratch, RGB/RGB-D, related task | Not started |
| E6 | Scratch, RGB-D plus K1-style tools | Not started |
| E7 | Best experience condition, RGB-D plus K1, held-out variants | Not started |
| E8 | Best condition on a second embodiment | Not started |

The server-repair task must have one complete repair before E2-E4 become meaningful. Otherwise transfer measurements would be measuring transfer of an incomplete program.

## What Is Promising

1. **The coding-agent loop is real.** The agent can inspect a physical scene, use diagnostics, write controller code, run it, inspect failure, and revise it.
2. **Closed-loop feedback matters.** The centered regrasp fix was discovered from measured grasp drift, not from adding a larger skill library.
3. **Classical control remains sufficient for substantial progress.** Neither a VLA nor GraspGen-X is required to demonstrate grasp, lift, transport, and structured recovery in the current simulator.
4. **Diff-IK is a useful backend improvement.** It materially improves orientation preservation in server repair, even though final insertion remains unsolved.
5. **The program/checkpoint abstraction is useful.** Stage boundaries make it possible to preserve a successful grasp and debug later phases without replaying the entire prefix.
6. **The first held-out bulb result is encouraging.** It shows the centered-regrasp logic is not only a single nominal trace.

## What Has Failed or Remains Weak

1. **The flagship server repair is not complete.** The card still misses the strict seat gate.
2. **Contact-sensitive insertion is fragile.** Small lateral and orientation errors compound during threaded or constrained insertion.
3. **One held-out bulb result is not enough.** Holdout 2 currently shows a likely drop during regrasp, pending final verdict.
4. **The first stage checkpoint can be saved while angular velocity is still nonzero.** This is currently logged as an unsafe boundary warning. It may be harmless for the final centered controller, but should be treated as a protocol defect if it affects replay.
5. **The current capability task is privileged.** Exact object poses, hidden contact predicates, and simulator geometry are not available on a real robot.
6. **No experience-amortization result exists yet.** We have not compared scratch versus prior code, trace, or keyframes on a genuinely related held-out repair.
7. **No realistic RGB/RGB-D result exists yet.** SAM, GraspGen-X, and K1-style tools have not been justified as the next bottleneck for this project.

## Interpretation of Privileged versus Realistic Execution

The high-level recipe is potentially reusable in the real world:

```text
observe -> diagnose -> act -> measure -> recover -> verify
```

However, the current source is not directly deployable because it reads simulator-local poses and success state. A realistic adapter must replace those with:

- calibrated RGB/RGB-D pose estimates;
- object identity and track confidence;
- uncertainty and observation age;
- robot joint and gripper telemetry;
- force/torque or contact evidence;
- independent visual and system-level verification;
- safety limits, watchdogs, and collision handling.

The correct progression is to validate capability with privileged state, then expose a sensor-derived observation facade, then add noise, latency, occlusion, and K1-style metric tools. Do not claim real-world transfer from the current simulator result.

## Distillation and Learned Policies

VLA distillation is not a prerequisite for the current benchmark. The upstream paper reports useful but bounded results:

- SmolVLA average success rose from 18% with 10 demonstrations to 69% with 400 demonstrations.
- Mean rubric score rose from 0.32 to 0.76.
- Agent-aided diversified data improved held-out performance over script-only data.
- In the real lamp task, a pi0.5-DROID policy trained only on simulated coding-agent demonstrations reached 100% shade grasp, 80% placement, 30% bulb grasp, and 20% bulb extraction over 10 trials; the pretrained baseline scored 0% at all stages.

These results show that generated programs can be useful teachers. They do not show that the full coding-agent capability has been distilled into a general policy. The paper explicitly leaves end-to-end distillation as an open limitation.

## Immediate Next Actions

1. Let the agent-owned holdout 3 finish; archive its final verdict and images.
2. Treat the three-holdout result as a robustness gate. If the final result is not strong, make one phase-level regrasp decision rather than launching a long parameter sweep.
3. Run one clean fresh-reset server-repair evaluation through the corrected per-run cache mount.
4. Use Diff-IK as the comparison backend, but address final Cartesian insertion with one controlled approach strategy rather than more perception work.
5. Complete one server repair before running prior-code, semantic-trace, or keyframe ablations.
6. Freeze the completed repair program and evaluate 2-3 held-out server configurations without LLM calls.
7. Compare scratch, prior-code, prior-code-plus-trace, and prior-code-plus-keyframes using matched budgets and at least three replicates where feasible.
8. Only after those results, remove privileged state and evaluate RGB/RGB-D plus K1-style tools.
9. Add a learned motor policy only if a specific residual failure remains after classical control and sensor-derived feedback are adequate.

## Decision Rules

- Do not equate component passes with completion of a phase.
- Do not add SAM, GraspGen-X, or a VLA merely because they are available.
- Do not tune held-out runs.
- Do not treat the duplicate holdout process as scientific evidence.
- Do not claim the server-repair benchmark is solved until the hidden diagnostic and physical seat grader both pass.
- Do not claim real-world usefulness until the program runs through a sensor-derived interface without privileged object state.

## Artifacts

- Handoff checklist: [`codex_embodied_technical_work_handoff.md`](../../codex_embodied_technical_work_handoff.md)
- Project manifest: [`EXPERIMENT_MANIFEST.md`](../EXPERIMENT_MANIFEST.md)
- Phase 0 audit: [`2026-09-27-phase0-audit.md`](2026-09-27-phase0-audit.md)
- Bulb result: [`2026-09-27-phase0-bulb-result.md`](2026-09-27-phase0-bulb-result.md)
- Server-repair result: [`2026-09-27-phase1-server-repair.md`](2026-09-27-phase1-server-repair.md)
- Upstream source audit: [`2026-09-27-upstream-source-audit.md`](2026-09-27-upstream-source-audit.md)
- Diff-IK runner: [`diffik_weldframe_runner.py`](../diffik_weldframe_runner.py)
- Alternative shifted-base runner: [`shifted_diffik_runner.py`](../shifted_diffik_runner.py)

## Bottom Line

The project has passed the feasibility stage but not the flagship stage. The strongest verified claim today is:

> A Codex coding agent can generate and refine a closed-loop simulator program that completes a nontrivial bulb manipulation task, and the same centered-regrasp logic passed one held-out instance.

The strongest unresolved claim is:

> Whether a coding agent can complete and then reuse a physically coupled technical repair program across held-out server configurations without privileged state.

That is the next meaningful experiment, and it should remain the priority over further model or perception shopping.
