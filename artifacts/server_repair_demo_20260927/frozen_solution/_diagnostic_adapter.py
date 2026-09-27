"""A physically coupled terminal-like diagnostic interface for the server task.

The initial capability condition intentionally keeps this adapter transparent and simple. The
reported health is derived from the scene's public physical success predicate; later realistic
conditions can replace the backend while preserving this command contract.
"""

from __future__ import annotations

TOOL = {
    "name": "server_diagnostics",
    "description": (
        "Run a small terminal-like diagnostic command against the simulated training node. "
        "The result changes when the graphics card is physically seated."
    ),
    "exports": ("server_exec",),
    "prompt_doc": "tools/server_diagnostics.md",
}


def _healthy(env) -> bool:
    status = env.scene.success()
    return bool(status.all().item() if hasattr(status, "all") else status)


def server_exec(env, command: str) -> str:
    """Run one supported diagnostic command and return terminal-like text."""
    command = " ".join(str(command).strip().lower().split())
    healthy = _healthy(env)
    if command == "nvidia-smi":
        return "$ nvidia-smi\nGPU 0: healthy\nGPU 1: " + ("healthy" if healthy else "NOT DETECTED")
    if command == "lspci":
        return "$ lspci\n00:01.0 VGA compatible controller: " + ("RTX 2060" if healthy else "device absent")
    if command == "memory-status":
        return "$ memory-status\nECC: clean\nDIMM population: 2/2\nGPU enumeration: " + ("pass" if healthy else "fail")
    if command == "healthcheck":
        return "$ healthcheck\n" + ("PASS" if healthy else "FAIL: GPU 1 not detected")
    raise ValueError("unsupported diagnostic; choose nvidia-smi, lspci, memory-status, or healthcheck")

