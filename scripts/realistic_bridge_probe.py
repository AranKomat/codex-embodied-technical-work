"""Bounded probe for the actor-facing realistic observation boundary.

This intentionally performs no robot motion.  It answers the first question in
the realism bridge: which observations are actually available when exact bulb
and socket poses are withheld?
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from live_session.embodiedswe_backend import build_bulb


def main() -> None:
    output = Path("realistic_bridge_probe.json")
    backend = build_bulb(mode="realistic")
    try:
        result = {
            "mode": backend.observation_mode,
            "state": backend.dispatch("state", {}),
            "observe": backend.dispatch("observe", {"cameras": [], "depth": True}),
            "contact": backend.dispatch("contact", {}),
            "motion_actions": backend._actions,
        }
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    finally:
        os._exit(0)


if __name__ == "__main__":
    main()
