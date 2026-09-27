# Persistent Live Session Prototype

**Date:** 2026-09-27  
**Scope:** Phase 2 of `CODEX_EMBODIED_REALISTIC_INTERACTIVE_HANDOFF_20260927.md`

## Implementation

The outer project now contains a small persistent execution substrate under
[`live_session/`](../live_session/):

- `server.py` owns one backend and serializes commands over a Unix-domain socket.
- `client.py` sends one bounded request per client process.
- `contracts.py` validates commands, numeric bounds, request IDs, and protocol version.
- `fake_backend.py` provides a deterministic non-GPU backend for process-boundary tests.
- `embodiedswe_backend.py` lazily launches an EmbodiedSWE bulb environment on an Isaac host.

The initial public command surface is:

```text
status, observe, state, contact,
move_ee, move_delta, gripper, hold, stop
```

Each accepted or rejected request receives a receipt containing the session ID,
monotonic sequence number, timestamps, duration, and error/result status. The
server appends the request and receipt to a JSONL trace and flushes it before
returning. A second client therefore addresses the same backend state rather
than constructing a fresh simulator.

## Observation boundary

The adapter has an explicit `mode`:

- `privileged`: development-only state may include exact bulb and socket poses.
- `realistic`: returns robot/proprioceptive data but does not include exact object
  poses, hidden grader state, or task-success predicates.

The current adapter reports camera frames and contact as unavailable. It does not
silently substitute simulator truth for either modality. This is deliberate:
camera/RGB-D and Contact V0 must be implemented as measured or sensor-derived
signals before the realistic condition is claimed complete.

`move_delta` uses the existing six-dimensional relative end-effector action and
preserves the current gripper target. `move_ee` closes the loop on the robot's
end-effector pose using bounded relative actions; it is a backend motion helper,
not a task-specific bulb command.

## Verification performed

The standard-library test
[`tests/test_live_session.py`](../tests/test_live_session.py) starts the server,
uses one client to move the fake robot, uses a separate client to read state, and
verifies:

- the session ID is unchanged;
- the second client sees the first client's updated position;
- action count persists;
- receipts are ordered `1..4` across status, movement, state, and stop;
- all requests are present in the append-only trace.

Syntax compilation and `git diff --check` also pass.

## Not yet complete

The following are still required before Phase 2 exits:

1. Launch `embodiedswe_backend:build_bulb` on the GPU host.
2. Run two independently generated client scripts against that live process.
3. Deliberately change the bulb state, terminate the first client, and prove the
   second client continues from that same state.
4. Add camera/RGB-D capture and Contact V0 as separate observation providers.
5. Keep hidden grading outside the client-visible observation contract.

The current running Claude bulb probe is being preserved as an interactive
development artifact. It is not evidence that this new persistent server passes
the Phase 2 exit criterion.
