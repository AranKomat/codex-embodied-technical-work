import torch
from payload import PayloadMotion,execute_phase,quat_apply
from precision import Precision

def run(env):
    m=PayloadMotion(env);s=env.scene
    q=s.case.data.root_quat_w.clone()
    seat=s.case.data.root_pos_w+quat_apply(q,m.tensor(s.cfg.seat_pos))
    # Re-establish the held pose so this stage is portable across checkpoint restores.
    inside=seat+quat_apply(q,m.tensor((-.145,0,.014)))
    if not execute_phase(m,inside,q,'confirm interior alignment'):return
    if not execute_phase(m,seat+quat_apply(q,m.tensor((0,0,.014))),q,'rearward slide'):return
    for t in range(300):
        offset=.014-min(.015,(t+1)*.00015)
        env.step(m.card_action(seat+quat_apply(q,m.tensor((0,0,offset))),q))
        if t>103 and bool(s.seated().all()):break
    m.report('pressed to seat')
    if not bool(s.seated().all()):return
    hp,hq=m.pose()
    # The slot now supports the card. Cancel the previous filtered payload-support
    # command through the action interface while opening the fingers.
    act=torch.zeros((env.num_envs,8),device=env.device)
    ctrl=env.robot.controller.controllers[0]
    alpha=ctrl.cfg.ema_factor
    act[:,:6]=-(1-alpha)/alpha*ctrl.get_state()['prev_action']
    act[:,6:]=.04
    env.step(act)
    m=Precision(env,support='unloaded')
    for t in range(50):env.step(m.action(hp,hq,.04))
    m.report('released seated card')
    for t in range(150):
        env.step(m.action(hp+m.tensor((0,0,.15))*min(1,(t+1)/75),hq,.04))
    m.report('gripper clear')

def check(env):
    s=env.scene;art=env.robot.articulation
    hand=art.body_names.index('panda_hand')
    clearance=art.data.body_pos_w[:,hand,2]-s.card.data.root_pos_w[:,2]
    return bool(s.seated().all() and not s.grasp_held.any() and (clearance>.28).all())
