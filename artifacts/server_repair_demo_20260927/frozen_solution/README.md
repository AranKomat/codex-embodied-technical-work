# Training node 17 repair

Entry point: `solve.py::solve(env)`. All motion uses `env.step` actions; no resets, state restoration, direct pose writes, or direct force application occur in the solution.

The solver diagnoses the missing GPU, pinches its top edge, lifts it clear, aligns it in the case interior, slides it rearward, presses it into the PCIe slot, releases it, and retreats. It reads the current card and hand poses throughout transfer and insertion. Payload compensation is expressed through the existing OSC action interface.

The three stage modules expose `run(env)` and `check(env)`. Failure of a stage check stops further motion and prints diagnostics. The official diagnostic tool is preferred when installed; the bundled adapter is an unchanged copy of the granted diagnostic interface for import-path portability.

## Local validation

- Completed checkpoint-stage replay: healthcheck PASS, seated and released.
- Full entrypoint from fresh reset, with reset/state-setting blocked during solve: PASS.
- Frozen candidate on three fresh starts with independent XY jitter within +/-1.5 mm: 3/3 PASS, all released and grippers clear.
- Final seating depths: 4.9327 mm nominal; 4.9339, 4.9330, 4.9326 mm holdouts.
- Final camera images were opened and inspected. Full integrated, holdout, and stage-replay logs are in `validation/`.

These are local development results; the harness performs its separate fresh-reset grading after handoff.
