"""EmbodiedSWE bulb adapter for the persistent session.

This module intentionally keeps Isaac imports inside ``build_bulb``.  The session server can
therefore be imported and contract-tested on a normal Python installation.  ``mode=privileged``
is a development condition: it may include exact bulb/socket poses in ``state``.  The realistic
condition returns robot/proprioceptive data only and reports unavailable sensors explicitly.
"""

from __future__ import annotations

import math
import os
from typing import Any


def _json(value: Any) -> Any:
    """Convert torch/numpy scalars and tensors without exposing simulator objects."""
    if hasattr(value, "detach"):
        value = value.detach().cpu().tolist()
    elif hasattr(value, "tolist"):
        value = value.tolist()
    if isinstance(value, tuple):
        return [_json(item) for item in value]
    if isinstance(value, list):
        return [_json(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json(item) for key, item in value.items()}
    return value


def _qmul(a, b):
    aw, ax, ay, az = a.unbind(-1)
    bw, bx, by, bz = b.unbind(-1)
    import torch

    return torch.stack(
        [
            aw * bw - ax * bx - ay * by - az * bz,
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
        ],
        -1,
    )


def _qconj(q):
    return q * q.new_tensor([1.0, -1.0, -1.0, -1.0])


def _qapply(q, vector):
    import torch

    qv = torch.cat([torch.zeros_like(vector[..., :1]), vector], -1)
    return _qmul(_qmul(q, qv), _qconj(q))[..., 1:]


def _rotvec(q):
    """Shortest quaternion-to-rotation-vector conversion for one torch quaternion."""
    import torch

    if float(q[0]) < 0:
        q = -q
    vector = q[1:]
    sine = vector.norm()
    if float(sine) < 1e-8:
        return torch.zeros(3, device=q.device)
    angle = 2.0 * math.atan2(float(sine), float(q[0]))
    return vector / sine * angle


class BulbBackend:
    """A single live bulb environment owned by one session server."""

    def __init__(self, env: Any, *, mode: str = "privileged", max_delta: float = 1.0) -> None:
        if mode not in {"privileged", "realistic"}:
            raise ValueError("mode must be privileged or realistic")
        self.env = env
        self.observation_mode = mode
        self.max_delta = float(max_delta)
        if self.max_delta <= 0:
            raise ValueError("max_delta must be positive")
        self._ee_index = env.robot.articulation.body_names.index("panda_hand")
        self._bulb = env.scene.bulbs[0]
        self._socket = env.scene.sockets[0]
        self._gripper = 0.04
        self._actions = 0

    @property
    def _device(self):
        return self.env.device

    def _robot_observation(self) -> dict[str, Any]:
        art = self.env.robot.articulation
        ee = self._ee_index
        return {
            "joint_position": _json(art.data.joint_pos[0]),
            "joint_velocity": _json(art.data.joint_vel[0]),
            "ee_position_m": _json(art.data.body_pos_w[0, ee]),
            "ee_quaternion_wxyz": _json(art.data.body_quat_w[0, ee]),
            "gripper_position_m": _json(art.data.joint_pos[0, 7:9]),
        }

    def _state(self) -> dict[str, Any]:
        result = {
            "observation_mode": self.observation_mode,
            "robot": self._robot_observation(),
            "action_count": self._actions,
        }
        if self.observation_mode == "privileged":
            result["privileged_scene"] = {
                "bulb_position_m": _json(self._bulb.data.root_pos_w[0]),
                "bulb_quaternion_wxyz": _json(self._bulb.data.root_quat_w[0]),
                "socket_position_m": _json(self._socket.data.root_pos_w[0]),
            }
        return result

    def _action(self, arm_delta: list[float] | None = None) -> Any:
        import torch

        action = torch.zeros(1, 8, device=self._device)
        if arm_delta is not None:
            action[0, :6] = torch.tensor(arm_delta, device=self._device)
        action[0, 6:8] = self._gripper
        return action

    def dispatch(self, command: str, args: dict[str, Any]) -> Any:
        if command == "state":
            return self._state()
        if command == "observe":
            return {
                "observation_mode": self.observation_mode,
                "timestamp_ns": __import__("time").time_ns(),
                "robot": self._robot_observation(),
                "cameras": [],
                "depth": [],
                "available": False,
                "reason": "camera provider is not wired in this session build",
            }
        if command == "contact":
            return {
                "available": False,
                "quality": "unavailable",
                "reason": "contact V0 is not yet exposed by the backend",
            }
        if command == "move_delta":
            delta = list(args["delta"])
            if any(abs(value) > self.max_delta for value in delta):
                raise ValueError(f"delta components must be within +/-{self.max_delta}")
            for _ in range(args["steps"]):
                self.env.step(self._action(delta))
            self._actions += args["steps"]
            return self._state()
        if command == "gripper":
            value = args["value"]
            self._gripper = {"open": 0.04, "close": 0.0}.get(value, float(value) * 0.04)
            for _ in range(args["steps"]):
                self.env.step(self._action())
            self._actions += args["steps"]
            return self._state()
        if command == "hold":
            for _ in range(args["steps"]):
                self.env.step(self._action())
            self._actions += args["steps"]
            return self._state()
        if command == "move_ee":
            return self._move_ee(args)
        if command == "stop":
            return {"stopped": True, "state": self._state()}
        raise ValueError(f"unsupported command {command!r}")

    def _move_ee(self, args: dict[str, Any]) -> dict[str, Any]:
        import torch

        target = torch.tensor(args["position_m"], device=self._device)
        target_q = torch.tensor(args["quaternion_wxyz"], device=self._device)
        reached = False
        position_error = float("inf")
        rotation_error = float("inf")
        for _ in range(args["max_steps"]):
            art = self.env.robot.articulation
            ee = self._ee_index
            current = art.data.body_pos_w[0, ee]
            current_q = art.data.body_quat_w[0, ee]
            position = target - current
            rotation = _rotvec(_qmul(target_q, _qconj(current_q)))
            position_error = float(position.norm())
            rotation_error = float(rotation.norm())
            if position_error < 0.003 and rotation_error < 0.03:
                reached = True
                break
            linear = torch.clamp(position / 0.02, -1.0, 1.0)
            angular = torch.clamp(rotation / 0.097, -1.0, 1.0)
            self.env.step(self._action(torch.cat([linear, angular]).tolist()))
            self._actions += 1
        return {
            "reached": reached,
            "position_error_m": position_error,
            "rotation_error_rad": rotation_error,
            "state": self._state(),
        }

    def close(self) -> None:
        self.env.close()


def build_bulb(*, mode: str = "privileged", control_mode: str = "osc", **_: Any) -> BulbBackend:
    """Launch one bulb env. Must run on the Isaac host, not in a normal unit-test process."""
    from isaaclab.app import AppLauncher

    AppLauncher(headless=True).app
    import robobench

    robobench.discover()
    from robobench.core.registries import ENVS

    env = ENVS.get(f"assembly.bulb.franka.{control_mode}")().build(num_envs=1, room=None)
    return BulbBackend(env, mode=mode)
