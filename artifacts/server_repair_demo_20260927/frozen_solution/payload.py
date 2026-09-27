import torch
from precision import Precision,quat_apply,quat_mul,quat_conjugate,axis_angle_from_quat

class PayloadMotion(Precision):
    """Command the OSC's pose deltas to support the measured card payload."""
    def __init__(self,env,ids=None):
        super().__init__(env,ids,support='payload')
    def action(self,p,q,g=.012):
        hp,hq=self.pose()
        pe=p-hp
        qe=quat_mul(q,quat_conjugate(hq));qe=torch.where(qe[:,:1]<0,-qe,qe)
        re=axis_angle_from_quat(qe)
        self.pi=(self.pi+pe*.035).clamp(-.3,.3)
        self.ri=(self.ri+re*.025).clamp(-2,2)
        err=torch.cat((pe+self.pi,re+self.ri),dim=-1)
        view=self.art.root_physx_view
        j=view.get_jacobians()[self.ids,self.h-1,:,:7]
        mm=view.get_generalized_mass_matrices()[self.ids,:7,:7]
        force=self.tensor((0,0,9.81))*self.env.scene.grasp_held[self.ids,:1].float()*self.env.scene.cfg.card_mass
        lever=self.env.scene.card.data.root_com_pos_w[self.ids]-hp
        wrench=torch.cat((force,torch.cross(lever,force,dim=-1)),dim=-1)
        # The arm preset disables its own gravity. Only support the held card.
        tau=(j.transpose(1,2)@wrench.unsqueeze(-1))
        accel=(j@torch.linalg.solve(mm,tau)).squeeze(-1)
        err+=accel/self.tensor((100,100,100,30,30,30))
        act=torch.zeros((self.n,8),device=self.dev)
        act[:,:6]=(err/self.tensor((.02,.02,.02,.097,.097,.097))).clamp(-15,15)
        act[:,6:]=g
        return act
    def phase(self,p,q,label,ptol=.0005,rtol=.004,maxsteps=600):
        start=self.env.scene.card.data.root_pos_w[self.ids].clone()
        duration=max(1.,float((p-start).norm(dim=-1).max())/.0015)
        count=0
        for t in range(maxsteps):
            alpha=min(1,(t+1)/duration)
            yield self.card_action(start+(p-start)*alpha,q)
            pe,re=self.error(p,q)
            if (t+1)%100==0:print('TRACK',label,t+1,pe.tolist(),re.tolist(),flush=True)
            if not self.env.scene.grasp_held[self.ids].all():break
            if alpha>=1 and bool(((pe<ptol)&(re<rtol)).all()):count+=1
            else:count=0
            if count>=20:break
        print('PHASE',label,'steps',t+1,'poserr',pe.tolist(),'roterr',re.tolist(),'held',self.env.scene.grasp_held[self.ids].tolist(),flush=True)
        return count>=20


def execute_phase(m,p,q,label):
    gen=m.phase(p,q,label)
    while True:
        try:
            action=next(gen)
        except StopIteration as done:
            m.report(label)
            return bool(done.value)
        m.env.step(action)
