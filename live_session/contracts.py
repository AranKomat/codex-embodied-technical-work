"""Wire-contract validation for the persistent robot session."""

from __future__ import annotations

import math
import time
import uuid
from dataclasses import dataclass
from typing import Any


PROTOCOL_VERSION = 1
COMMANDS = {
    "status",
    "observe",
    "state",
    "contact",
    "locate_measure",
    "move_ee",
    "move_delta",
    "gripper",
    "hold",
    "stop",
}


class ContractError(ValueError):
    """A request violates the public robot-session contract."""


def now_ns() -> int:
    return time.time_ns()


def _finite_vector(value: Any, *, name: str, length: int) -> list[float]:
    if not isinstance(value, list) or len(value) != length:
        raise ContractError(f"{name} must be a list of {length} numbers")
    out = [float(item) for item in value]
    if not all(math.isfinite(item) for item in out):
        raise ContractError(f"{name} must contain only finite numbers")
    return out


@dataclass(frozen=True)
class Request:
    request_id: str
    command: str
    args: dict[str, Any]
    protocol_version: int = PROTOCOL_VERSION

    @classmethod
    def parse(cls, payload: Any) -> "Request":
        if not isinstance(payload, dict):
            raise ContractError("request must be a JSON object")
        version = payload.get("protocol_version", PROTOCOL_VERSION)
        if version != PROTOCOL_VERSION:
            raise ContractError(
                f"protocol_version must be {PROTOCOL_VERSION}, got {version!r}"
            )
        command = payload.get("command")
        if command not in COMMANDS:
            raise ContractError(f"unknown command {command!r}")
        request_id = payload.get("request_id") or str(uuid.uuid4())
        if not isinstance(request_id, str) or not request_id:
            raise ContractError("request_id must be a non-empty string")
        args = payload.get("args", {})
        if not isinstance(args, dict):
            raise ContractError("args must be a JSON object")
        return cls(request_id=request_id, command=command, args=args, protocol_version=version)

    def validated_args(self) -> dict[str, Any]:
        args = dict(self.args)
        if self.command == "move_delta":
            args["delta"] = _finite_vector(args.get("delta"), name="delta", length=6)
            args["steps"] = bounded_int(args.get("steps", 1), name="steps", low=1, high=250)
        elif self.command == "move_ee":
            args["position_m"] = _finite_vector(
                args.get("position_m"), name="position_m", length=3
            )
            args["quaternion_wxyz"] = _finite_vector(
                args.get("quaternion_wxyz"), name="quaternion_wxyz", length=4
            )
            norm = math.sqrt(sum(item * item for item in args["quaternion_wxyz"]))
            if norm < 1e-8:
                raise ContractError("quaternion_wxyz must have non-zero norm")
            args["quaternion_wxyz"] = [item / norm for item in args["quaternion_wxyz"]]
            mode = args.get("mode", "linear")
            if mode not in {"linear", "plan"}:
                raise ContractError("mode must be 'linear' or 'plan'")
            args["mode"] = mode
            args["max_steps"] = bounded_int(
                args.get("max_steps", 200), name="max_steps", low=1, high=500
            )
        elif self.command == "gripper":
            value = args.get("value")
            if isinstance(value, str):
                if value not in {"open", "close"}:
                    raise ContractError("gripper value must be open, close, or a fraction")
            else:
                value = float(value)
                if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                    raise ContractError("gripper fraction must be between 0 and 1")
            args["value"] = value
            args["steps"] = bounded_int(args.get("steps", 20), name="steps", low=1, high=250)
        elif self.command == "hold":
            args["steps"] = bounded_int(args.get("steps", 1), name="steps", low=1, high=500)
        elif self.command == "observe":
            cameras = args.get("cameras", [])
            if not isinstance(cameras, list) or not all(isinstance(item, str) for item in cameras):
                raise ContractError("cameras must be a list of names")
            args["cameras"] = cameras
            args["depth"] = bool(args.get("depth", True))
        elif self.command == "locate_measure":
            observation = args.get("observation")
            if not isinstance(observation, dict):
                raise ContractError("observation must be a camera calibration object")
            for name in ("fx", "fy", "cx", "cy"):
                value = float(observation.get(name))
                if not math.isfinite(value):
                    raise ContractError(f"observation {name} must be finite")
            args["observation"] = observation
            for name in ("u", "v", "depth_m"):
                value = float(args.get(name))
                if not math.isfinite(value):
                    raise ContractError(f"{name} must be finite")
                args[name] = value
            if args["depth_m"] <= 0:
                raise ContractError("depth_m must be positive")
        return args


def bounded_int(value: Any, *, name: str, low: int, high: int) -> int:
    if isinstance(value, bool):
        raise ContractError(f"{name} must be an integer")
    result = int(value)
    if result != value or not low <= result <= high:
        raise ContractError(f"{name} must be an integer in [{low}, {high}]")
    return result


def response(
    request: Request,
    *,
    session_id: str,
    sequence: int,
    started_ns: int,
    result: Any = None,
    error: str | None = None,
) -> dict[str, Any]:
    finished_ns = now_ns()
    return {
        "protocol_version": PROTOCOL_VERSION,
        "request_id": request.request_id,
        "session_id": session_id,
        "sequence": sequence,
        "command": request.command,
        "ok": error is None,
        "started_ns": started_ns,
        "finished_ns": finished_ns,
        "duration_ms": (finished_ns - started_ns) / 1_000_000,
        "result": result if error is None else None,
        "error": error,
    }
