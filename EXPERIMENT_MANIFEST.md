# Codex Embodied Technical Work

This workspace is a separate research project built from the 2026-09-27 handoff. The existing Physical Harness and BEHAVIOR work are intentionally not vendored here.

## Objective

Test whether a coding agent can diagnose and repair a simulated server through both digital diagnostics and physical robot interaction, and whether verified prior programs reduce the cost of solving related tasks.

## Upstream snapshots

| Project | Repository | Commit | Role | License / status |
| --- | --- | --- | --- | --- |
| EmbodiedSWE | `https://github.com/EmbodiedSWE/EmbodiedSWE` | `d34837e99e5016525f0e9b6bb84791eb3d4b8162` | Primary simulator and agent substrate | Apache-2.0 |
| Robo-Harness K1 | `https://github.com/Robo-Harness/k1` | `40e6633b4d52daa026eb8a8395948387a3cb6d3c` | Spatial-tool reference | MIT |
| RoboCode | `https://github.com/tomsilver/robocode` | `ebd43b96b61cbb0adcd82b321a439e0b0a7c4eee` | Frozen-program evaluation methodology | MIT |
| GPT-Policy | `https://github.com/cheng-haha/GPT-Policy` | `ab970d88bc5570d80a7b4f3e8d3ad97ebe65a007` | Internal-only experience packaging reference | License unresolved; do not redistribute copied code |

## Working state

- EmbodiedSWE branch: `exp/technical-worker-server-repair`
- Date initialized: 2026-09-27
- Python: to be recorded during Phase 0
- CUDA / driver: to be recorded on the experiment host
- Isaac Sim / Isaac Lab: to be recorded during Phase 0
- Codex CLI / model / auth mode: to be recorded before agent runs
- Machine / GPU: to be recorded before GPU experiments

## Guardrails

- Reproduce upstream before modifying it.
- Keep outer harness development separate from inner-agent evaluation.
- Use only development instances for outer-loop changes; reserve held-out instances before evaluation.
- Do not expose hidden fault variables, evaluation seeds, grader geometry, or direct state mutation to the actor.
- Do not add Physical Harness, Agmina, ROS, Intrinsic, Microsoft tooling, or VLA training without a measured failure that justifies it.
- Preserve full logs, run IDs, source SHAs, and concise progress reports.

## Initial sequence

1. Reproduce one EmbodiedSWE PC smoke and one fresh-reset Codex solve/grading run.
2. Inspect existing PC scenes, tools, graders, and control contracts.
3. Add the smallest physically coupled server-diagnosis interface and `gpu_unseated` or `ram_unseated` task.
4. Obtain one scratch-Codex repair using privileged capability-mode state.
5. Freeze the generated program and measure held-out generalization.
6. Measure transfer with prior code, semantic trace, and selected keyframes.
7. Only then add the realistic RGB/RGB-D and K1-like tool condition.

