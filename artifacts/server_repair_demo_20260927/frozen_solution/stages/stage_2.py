from payload import PayloadMotion,execute_phase,quat_apply

def run(env):
    m=PayloadMotion(env);s=env.scene
    q=s.case.data.root_quat_w.clone()
    seat=s.case.data.root_pos_w+quat_apply(q,m.tensor(s.cfg.seat_pos))
    for label,offset in [('over clear interior',(-.145,0,.23)),('aligned in clear interior',(-.145,0,.014))]:
        if not execute_phase(m,seat+quat_apply(q,m.tensor(offset)),q,label):return

def check(env):
    import torch
    s=env.scene
    err=s._card_offset_in_case()-torch.tensor((-.145,0,.014),device=env.device)
    return bool(s.grasp_held.all() and (err.norm(dim=-1)<.001).all() and (s._axis_cos(2)>.99999).all() and (s._axis_cos(0)>.99999).all() and (s.card.data.root_lin_vel_w.norm(dim=-1)<.02).all())
