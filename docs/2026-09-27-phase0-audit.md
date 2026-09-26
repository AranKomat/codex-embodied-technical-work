# Phase 0 Audit

**Date:** 2026-09-27  
**Project commit:** `04f09c6`  
**Status:** Workspace initialized; simulator reproduction not yet run

## Completed

- Created a separate project workspace at `/Users/macbookpro/Developer/random/gpu/embodied-technical-work`.
- Cloned and pinned EmbodiedSWE, Robo-Harness K1, RoboCode, and GPT-Policy at the handoff SHAs.
- Created the EmbodiedSWE branch `exp/technical-worker-server-repair`.
- Confirmed the upstream checkout contains the documented Isaac 5.1 / Isaac Lab 2.3.2 bootstrap script, smoke runner, Codex runner, grading runner, and PC GPU/RAM scenes and graders.

## Not yet run

- Isaac/Isaac Lab bootstrap.
- PC scene smoke.
- Fresh-reset Codex solve.
- Grader validation.

## Current constraint

The last Vast GPU instance is stopped. Phase 0 requires Linux, an NVIDIA GPU, and the upstream Isaac environment, so the actual reproduction waits for a suitable GPU host. No custom task or K1 port should be started before that reproduction passes.

## First host command sequence

Run from the pinned EmbodiedSWE checkout, following the upstream README rather than inventing replacement commands:

```bash
./scripts/bootstrap_isaaclab_5_1.sh
source .venv/bin/activate
export OMNI_KIT_ACCEPT_EULA=YES
python -m robobench.scripts.fetch_assets
python -m robobench.scripts.smoke --list
python -m robobench.scripts.smoke --list | grep -E 'pc_(gpu|ram|motherboard)'
```

Record Python, CUDA/driver, Isaac versions, GPU, Codex CLI/model/auth mode, and the exact smoke/grade receipts before modifying the benchmark.
