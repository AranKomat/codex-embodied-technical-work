"""Deterministic backend used to verify persistence without a simulator."""

from __future__ import annotations

from typing import Any


class FakeBackend:
    observation_mode = "test"

    def __init__(self, *, initial_position: list[float] | None = None) -> None:
        self.position = list(initial_position or [0.0, 0.0, 0.0])
        self.gripper_fraction = 1.0
        self.action_count = 0

    def dispatch(self, command: str, args: dict[str, Any]) -> Any:
        if command in {"state", "observe"}:
            return self._state()
        if command == "contact":
            return {
                "available": False,
                "quality": "unavailable",
                "reason": "fake backend has no physical contact sensor",
            }
        if command == "move_delta":
            for axis in range(3):
                self.position[axis] += args["delta"][axis] * args["steps"]
            self.action_count += args["steps"]
            return self._state()
        if command == "move_ee":
            self.position = list(args["position_m"])
            self.action_count += 1
            return self._state()
        if command == "gripper":
            value = args["value"]
            self.gripper_fraction = {"open": 1.0, "close": 0.0}.get(value, value)
            self.action_count += args["steps"]
            return self._state()
        if command == "hold":
            self.action_count += args["steps"]
            return self._state()
        if command == "stop":
            return {"stopped": True, **self._state()}
        raise ValueError(f"unsupported command {command!r}")

    def _state(self) -> dict[str, Any]:
        return {
            "position_m": list(self.position),
            "gripper_fraction": self.gripper_fraction,
            "action_count": self.action_count,
        }

    def close(self) -> None:
        return None


def build_fake(**kwargs: Any) -> FakeBackend:
    return FakeBackend(**kwargs)
