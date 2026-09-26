# Upstream Source Audit

**Date:** 2026-09-27  
**EmbodiedSWE source:** `d34837e99e5016525f0e9b6bb84791eb3d4b8162`  
**Project commit:** pending

## What is already present

The pinned EmbodiedSWE checkout contains the expected Phase 0 substrate:

- `scripts/bootstrap_isaaclab_5_1.sh` for Isaac Sim 5.1 / Isaac Lab 2.3.2.
- `robobench/scripts/smoke.py` with registered-environment listing and headless smoke support.
- `eval/scripts/run_agent.py` and `eval/scripts/run_grade.py` for agent execution and fresh grading.
- PC GPU, RAM, motherboard, GPU+RAM, and combined PC scenes.
- Matching PC graders and smoke scripts.
- Existing controller bindings for operational-space, impedance, differential IK, Pink IK, and joint control.
- An agent contract that already emphasizes fresh resets, closed-loop correction, evidence, and no hidden-state shortcuts.

## Implication for the first implementation

The server-repair task should extend the existing PC task family. The smallest credible V1 is:

1. Start from the existing GPU or RAM scene.
2. Add a hidden physical fault at reset, such as an unseated GPU or DIMM.
3. Add a terminal-like diagnostic tool whose output is derived from the current physical state.
4. Reuse the existing scene, controller, agent, and grader contracts.
5. Keep the hidden fault variable and grader geometry out of the actor interface.

The first capability-mode task can use the existing simulator access while the benchmark mechanics are validated. The realistic RGB/RGB-D and K1-like condition should be a later ablation, after one repair works.

## Not run yet

Static inspection cannot establish that Isaac boots or that the current Codex runner grades successfully. Those remain GPU-host tasks:

- upstream bootstrap;
- PC GPU or RAM smoke;
- one fresh-reset Codex solve;
- one fresh-reset grading pass.

No server-repair code should be written until those checks pass.
