# Server Repair Demo Artifact

Fresh integrated replay from the Astra demo run on 2026-09-27.

The run passed all three stages, physical seating, gripper clearance, and the digital healthcheck. `replay_clearance.log` is the authoritative execution record. The PNG sequence in `clearance_replay/` is the retained visual trace; `stage_3.py` is the exact integrated stage module copied from the active container.

The complete frozen `solution/` tree used for the fresh and holdout checks is preserved in `frozen_solution/` for the R1 generalization experiments.
