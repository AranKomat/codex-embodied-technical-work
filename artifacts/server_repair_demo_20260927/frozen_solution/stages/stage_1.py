from motion import Motion, quat_apply, quat_mul

def run(env):
    m=Motion(env);s=env.scene
    cp=s.card.data.root_pos_w.clone()
    cq=s.card.data.root_quat_w.clone()
    p=cp+quat_apply(cq,m.tensor((0.,.0154,.2039)))
    q=quat_mul(cq,m.down)
    m.move(p+m.tensor((0,0,.12)),q,n=180,label='above pick')
    cp=s.card.data.root_pos_w.clone();cq=s.card.data.root_quat_w.clone()
    p=cp+quat_apply(cq,m.tensor((0.,.0154,.2039)))
    q=quat_mul(cq,m.down)
    m.move(p,q,n=160,label='at grip')
    m.move(p,q,g=.012,n=100,label='pinch')
    if not s.grasp_held.all():return
    m.move(p+m.tensor((0,0,.23)),q,g=.012,n=180,label='lifted')

def check(env):
    s=env.scene
    return bool(s.grasp_held.all() and (s.card.data.root_pos_w[:,2]>.15).all() and (s.card.data.root_lin_vel_w.norm(dim=-1)<.02).all())
