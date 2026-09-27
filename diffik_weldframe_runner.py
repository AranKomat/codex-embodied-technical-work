from isaaclab.app import AppLauncher

app = AppLauncher(headless=True).app
import os
import sys

sys.path.insert(0, "/workspace/solution")
import robobench

robobench.discover()
import torch
from isaaclab.utils.math import quat_apply, quat_apply_inverse
from checkpoint_tree import CheckpointTree
from control import command, card_state, hand_state
from robobench.core.registries import ENVS

env = ENVS.get("assembly.server_repair.franka.diff_ik")().build(num_envs=1, room=None)
tree = CheckpointTree(env)
tree.plan(["card securely gripped and lifted", "card fully seated and diagnostic PASS"])
tree.goto("n3")
card, _ = card_state(env)
hand, hold_q = hand_state(env)
rel_p_hand = quat_apply_inverse(hold_q.view(1, 4), (card - hand).view(1, 3))[0]
case_pos = env.scene.case.data.root_pos_w[0]
seat = case_pos + torch.tensor(env.scene.cfg.seat_pos, device=env.device)
board_z = case_pos[2]
place = seat.clone(); place[0] -= 0.028
cross = place.clone(); cross[2] = board_z + 0.240
slide = place.clone(); slide[2] = board_z + 0.0165
slot_aligned = seat.clone(); slot_aligned[2] = board_z + 0.0165
press = seat.clone(); press[2] = seat[2] - 0.0005

def move(target, steps):
    hand_target = target - quat_apply(hold_q.view(1, 4), rel_p_hand.view(1, 3))[0]
    command(env, hand_target, 0.0175, rot=hold_q, steps=steps, gain=1.0)

for name, target, steps in (("cross", cross, 220), ("drop", slide, 220),
                            ("slide", slot_aligned, 180), ("press", press, 220)):
    move(target, steps)
    print(name, card_state(env)[0].tolist(), card_state(env)[1].tolist(),
          "target", target.tolist(), "depth", env.scene.engaged().tolist(),
          "seated", env.scene.seated().tolist(), flush=True)
    if bool(env.scene.seated()[0]):
        break
command(env, hand_state(env)[0][0], 0.04, rot=hold_q, steps=45, gain=1.0)
print("FINAL", card_state(env)[0].tolist(), card_state(env)[1].tolist(),
      env.scene.engaged().tolist(), env.scene.seated().tolist(), flush=True)
os._exit(0)
