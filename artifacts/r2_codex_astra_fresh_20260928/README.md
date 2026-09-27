# R2 Astra Exploratory Snapshot

Date: 2026-09-28

## Run identity

- Experiment: `experiments/phase1_server_repair_single`
- Run: `r2_codex_astra_fresh`
- Model: `gpt-6-astra`
- Budget: 20 minutes
- Container: `rb_phase1_server_repair_single_r2_codex_astra_fresh`
- Source: remote `/workspace` snapshot from the single RTX 4090 host
- Snapshot archive SHA-256: `c0a48b370ed8b1af1801a8114b301d0583d07874782809d1cff985ca1396dd0c`

## Status

This was an exploratory fresh Astra run, not a matched R2 ablation. The
container was stopped at about 17 minutes so the GPU instance could be stopped
without losing the work. It exited with code `143`; this is an intentional
stop, not an agent or grader verdict.

The run produced six failed attempts and no saved checkpoint or successful
submission. The latest attempt reached a plausible grasp pose and closed the
fingers, but the card remained at the table. The assessment identified the
remaining issue as over-closing on the card's top edge and recommended using
the measured slab aperture while maintaining the pinch. Earlier attempts
included a wrist/joint-limit failure and a reachable pose with no firm pinch.

Important interpretation: this snapshot is useful failure evidence for the
interactive exploration path, but it does not show that Astra cannot solve the
task. It stopped before the configured 20-minute budget and did not complete a
fresh-reset grader run.

## Preserved contents

- `.agent/stderr.log`: agent and simulator output;
- `.assessments/reviews.jsonl`: six assessment records;
- `.checkpoints/`: checkpoint tree and six failed attempt programs/logs;
- `.footage/`: captured before/after/grasp images;
- `.psearch/`: grasp sweep registry and result;
- `baseline.log`, `grasp.log`, `replay.log`, `aperture.log`;
- `solution/`: latest candidate code and stage file;
- `test.py` through `test4.py`: generated development probes;
- `r2_codex_astra_fresh_snapshot_20260928.tar.gz`: exact compressed backup.

## Next use

Do not count this run as R2 completion. If resumed on a GPU, start from this
artifact's diagnosis: inspect the latest grasp aperture/orientation and run a
single fresh integrated candidate before any broader sweep. The formal next
comparison still requires matched frozen, interactive, interactive-plus-prior,
and recompiled conditions with explicit budgets and fresh-reset verification.
