# Codex Embodied Technical Work

Simulation-first benchmark for coding-agent technical work across a digital diagnostic interface and a physical robot.

The project uses [EmbodiedSWE](https://github.com/EmbodiedSWE/EmbodiedSWE) as its primary substrate. K1, RoboCode, and GPT-Policy are pinned sibling references. See [`EXPERIMENT_MANIFEST.md`](EXPERIMENT_MANIFEST.md) for provenance and the execution sequence.

The first task is intentionally narrow: diagnose a simulated unhealthy server, physically reseat a GPU or DIMM, rerun diagnostics, and finish only after the hidden grader and terminal-like health check agree.

The first capability-mode implementation is now developed in the pinned sibling
checkout. Its phase-1 result is summarized in
[`docs/2026-09-27-phase1-server-repair.md`](docs/2026-09-27-phase1-server-repair.md);
the full source remains isolated in the sibling checkout so upstream history is
not silently vendored into this project.
