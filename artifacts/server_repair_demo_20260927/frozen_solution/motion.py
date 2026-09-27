import torch
from isaaclab.utils.math import quat_apply, quat_mul, quat_conjugate, axis_angle_from_quat

class Motion:
    def __init__(self, env, ids=None):
        self.env=env
        self.ids=ids if ids is not None else torch.arange(env.num_envs,device=env.device)
        self.n=len(self.ids)
        self.art=env.robot.articulation
        self.h=self.art.body_names.index('panda_hand')
        self.dev=env.device
        self.pi=torch.zeros((self.n,3),device=self.dev)
        self.ri=torch.zeros_like(self.pi)
        self.down=self.tensor((0.,0.,1.,0.))
    def tensor(self,x):
        return torch.tensor(x,device=self.dev,dtype=torch.float32).expand(self.n,-1).clone()
    def pose(self):
        return self.art.data.body_pos_w[self.ids,self.h].clone(), self.art.data.body_quat_w[self.ids,self.h].clone()
    def action(self,p,q,g=.04):
        cp,cq=self.pose()
        pe=p-cp
        qe=quat_mul(q,quat_conjugate(cq))
        qe=torch.where(qe[:,:1]<0,-qe,qe)
        re=axis_angle_from_quat(qe)
        self.pi=(self.pi+pe*.035).clamp(-.16,.16)
        self.ri=(self.ri+re*.025).clamp(-1.5,1.5)
        act=torch.zeros((self.n,8),device=self.dev)
        act[:,:3]=((pe+self.pi)/.02).clamp(-5,5)
        act[:,3:6]=((re+self.ri)/.097).clamp(-5,5)
        act[:,6:]=g
        return act
    def step(self,p,q,g=.04):
        self.env.step(self.action(p,q,g))
    def move(self,p,q=None,g=.04,n=150,label='move'):
        if q is None:q=self.down
        for i in range(n): self.step(p,q,g)
        self.report(label,p,q)
    def report(self,label,p=None,q=None):
        hp,hq=self.pose();s=self.env.scene
        print(label,'hand',hp.tolist(),'quat',hq.tolist(),'card',s.card.data.root_pos_w.tolist(), 'cq',s.card.data.root_quat_w.tolist(),'held',s.grasp_held.tolist(),'depth',s.engaged().tolist(),'success',s.success().tolist(),flush=True)
        print('finger joints',self.art.data.joint_pos[:,-2:].tolist(),flush=True)
        viewer=getattr(self.env,'debug_viewer',None)
        if viewer is not None:viewer.snapshot(label)
    def card_move(self,p,q,g=.012,n=150,label='card'):
        for i in range(n):
            hp,hq=self.pose()
            cp=self.env.scene.card.data.root_pos_w
            cq=self.env.scene.card.data.root_quat_w
            dq=quat_mul(q,quat_conjugate(cq))
            targetp=p+quat_apply(dq,hp-cp)
            targetq=quat_mul(dq,hq)
            self.step(targetp,targetq,g)
        self.report(label)
