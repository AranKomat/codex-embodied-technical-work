"""No-motion RGB-D/proprioception probe for the server-repair scene."""

from __future__ import annotations

import json
from pathlib import Path

from live_session.embodiedswe_backend import build_server_repair


def main() -> None:
    output = Path("realistic_server_repair_probe.json")
    backend = build_server_repair(mode="realistic")
    try:
        result = {
            "task": "server_repair",
            "mode": backend.observation_mode,
            "state": backend.dispatch("state", {}),
            "observe": backend.dispatch("observe", {"cameras": [], "depth": True}),
            "contact": backend.dispatch("contact", {}),
            "motion_actions": backend._actions,
        }
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    finally:
        backend.close()


if __name__ == "__main__":
    main()
