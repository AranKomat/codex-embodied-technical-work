# Demo-First Progress: Server Repair

Date: 2026-09-27

## Result

The first complete Astra replay of the clearance-aware repair path passed end to end in the fresh Isaac container `rb_phase1_server_repair_single_phase1_codex_astra_demo`.

The run started from the repaired-card checkpoint `n1`, executed the staged path, and produced:

- Stage 1: card grasped and lifted clear of the holder: passed.
- Stage 2: card aligned in the clear case interior: passed.
- Stage 3: card seated and gripper clear: passed.
- Physical evaluator: `seated=True`, `grasp_held=False`.
- Digital healthcheck: `PASS`.
- Final checkpoint: `n3`.
- Replay attempt: `a6`.

The subsequent fresh holdout verifier also passed in all three environments:

- physical evaluator: all three cards seated;
- grippers: released in all three environments;
- final healthcheck: `PASS`.

The holdout log and visual trace are under [`../artifacts/server_repair_demo_20260927/holdout/`](../artifacts/server_repair_demo_20260927/holdout/).

The complete frozen program, including stage modules and controller helpers, is
preserved under [`../artifacts/server_repair_demo_20260927/frozen_solution/`](../artifacts/server_repair_demo_20260927/frozen_solution/). This makes R1 reproducible without reconstructing the agent workspace.

The complete raw log and ten-frame visual trace are archived under [`../artifacts/server_repair_demo_20260927/`](../artifacts/server_repair_demo_20260927/). The exact integrated stage module used by the replay is [`../artifacts/server_repair_demo_20260927/stage_3.py`](../artifacts/server_repair_demo_20260927/stage_3.py).

## What changed from the failed path

The original insertion path descended into the case before the card was sufficiently aligned. The corrected path:

1. moves the held card into a clear interior staging position;
2. confirms alignment there;
3. slides rearward while maintaining the card pose;
4. presses to seat;
5. releases the card; and
6. retracts the gripper before the final healthcheck.

This is a measured controller correction, not evidence that the full robotics stack is solved. The clearance sweep motivated the path, and this fresh integrated replay is the first run that verifies the entire chain.

## Model choice

Opus 5.5 was tested as a lower-cost exploration/debugging model. It was useful for iterative work but did not produce a verified end-to-end bulb success. Astra remains the model for benchmark-critical and hero-demo runs. Luna is not part of the active plan.

## Next sequence

1. Package the successful replay as a short hero demo, retaining the uncut trace and exact provenance.
2. Run one bounded realism bridge using only the permitted RGB-D/proprioceptive interface, without making privileged state a control input.
3. Record what the realism bridge can and cannot reproduce.
4. Only after those artifacts are complete, resume broader perception, retrieval, VLA, or tactile experiments.

The realism bridge is a credibility experiment; it is not required to invalidate the already-qualified privileged demo. Avoid reopening settled model-search and micro-diagnostic branches unless the bridge produces a concrete failure that requires one.
