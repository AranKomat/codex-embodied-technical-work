"""Client API and CLI for the persistent robot session."""

from __future__ import annotations

import argparse
import json
import socket
import uuid
from pathlib import Path
from typing import Any

from .contracts import PROTOCOL_VERSION


class RobotClient:
    def __init__(self, socket_path: str | Path, *, timeout_s: float = 300.0) -> None:
        self.socket_path = str(socket_path)
        self.timeout_s = timeout_s

    def call(self, command: str, **args: Any) -> dict[str, Any]:
        request = {
            "protocol_version": PROTOCOL_VERSION,
            "request_id": str(uuid.uuid4()),
            "command": command,
            "args": args,
        }
        connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        connection.settimeout(self.timeout_s)
        try:
            connection.connect(self.socket_path)
            stream = connection.makefile("rwb")
            stream.write(json.dumps(request).encode("utf-8") + b"\n")
            stream.flush()
            line = stream.readline()
        finally:
            connection.close()
        if not line:
            raise RuntimeError("session closed without a response")
        receipt = json.loads(line)
        if not receipt.get("ok"):
            raise RuntimeError(receipt.get("error") or "session command failed")
        return receipt

    def status(self) -> dict[str, Any]:
        return self.call("status")

    def state(self) -> dict[str, Any]:
        return self.call("state")

    def observe(self, *, cameras: list[str] | None = None, depth: bool = True) -> dict[str, Any]:
        return self.call("observe", cameras=cameras or [], depth=depth)

    def contact(self) -> dict[str, Any]:
        return self.call("contact")

    def move_delta(self, delta: list[float], *, steps: int = 1) -> dict[str, Any]:
        return self.call("move_delta", delta=delta, steps=steps)

    def move_ee(
        self,
        position_m: list[float],
        quaternion_wxyz: list[float],
        *,
        mode: str = "linear",
        max_steps: int = 200,
    ) -> dict[str, Any]:
        return self.call(
            "move_ee",
            position_m=position_m,
            quaternion_wxyz=quaternion_wxyz,
            mode=mode,
            max_steps=max_steps,
        )

    def gripper(self, value: str | float, *, steps: int = 20) -> dict[str, Any]:
        return self.call("gripper", value=value, steps=steps)

    def hold(self, *, steps: int = 1) -> dict[str, Any]:
        return self.call("hold", steps=steps)

    def stop(self) -> dict[str, Any]:
        return self.call("stop")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket", type=Path, required=True)
    parser.add_argument("command")
    parser.add_argument("--args", default="{}", help="JSON object")
    args = parser.parse_args()
    kwargs = json.loads(args.args)
    if not isinstance(kwargs, dict):
        parser.error("--args must decode to a JSON object")
    print(json.dumps(RobotClient(args.socket).call(args.command, **kwargs), indent=2))


if __name__ == "__main__":
    main()
