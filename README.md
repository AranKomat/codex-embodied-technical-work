# Codex Embodied Technical Work

Simulation-first benchmark for coding-agent technical work across a digital diagnostic interface and a physical robot.

The project uses [EmbodiedSWE](https://github.com/EmbodiedSWE/EmbodiedSWE) as its primary substrate. K1, RoboCode, and GPT-Policy are pinned sibling references. See [`EXPERIMENT_MANIFEST.md`](EXPERIMENT_MANIFEST.md) for provenance and the execution sequence.

The first task is intentionally narrow: diagnose a simulated unhealthy server, physically reseat a GPU or DIMM, rerun diagnostics, and finish only after the hidden grader and terminal-like health check agree.

This repository is not yet the modified EmbodiedSWE implementation. Phase 0 reproduction comes first.
