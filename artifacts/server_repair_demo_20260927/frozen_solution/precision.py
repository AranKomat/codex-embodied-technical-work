import torch
from motion import Motion, quat_apply, quat_mul, quat_conjugate, axis_angle_from_quat

class Precision(Motion):
    def __init__(self,env,ids=None,support='integral'):
        super().__init__(env,ids)
        self.support=support
        self.ri_gain=.025
        prev=env.robot.controller.controllers[0].get_state()['prev_action'][self.ids]
        if support=='integral':
            self.pi=prev[:,:3].clone()*.02
            self.ri=prev[:,3:6].clone()*.097
    def action(self,p,q,g=.012):
        hp,hq=self.pose()
        pe=p-hp
        qe=quat_mul(q,quat_conjugate(hq));qe=torch.where(qe[:,:1]<0,-qe,qe)
        re=axis_angle_from_quat(qe)
        self.pi=(self.pi+pe*.035).clamp(-.3,.3)
        self.ri=(self.ri+re*self.ri_gain).clamp(-2.,2.)
        err=torch.cat((pe+self.pi,re+self.ri),dim=-1)
        if self.support=='gravity':
            view=self.art.root_physx_view
            j=view.get_jacobians()[self.ids,self.h-1,:,:7]
            mm=view.get_generalized_mass_matrices()[self.ids,:7,:7]
            tau=view.get_gravity_compensation_forces()[self.ids,:7].clone()
            force=self.tensor((0,0,9.81))*self.env.scene.grasp_held[self.ids,:1].float()*self.env.scene.cfg.card_mass
            lever=self.env.scene.card.data.root_com_pos_w[self.ids]-hp
            wrench=torch.cat((force,torch.cross(lever,force,dim=-1)),dim=-1)
            tau=tau+(j.transpose(1,2)@wrench.unsqueeze(-1)).squeeze(-1)
            accel=(j@torch.linalg.solve(mm,tau.unsqueeze(-1))).squeeze(-1)
            err=err+accel/self.tensor((100,100,100,30,30,30))
        act=torch.zeros((self.n,8),device=self.dev)
        act[:,:6]=(err/self.tensor((.02,.02,.02,.097,.097,.097))).clamp(-15,15)
        act[:,6:]=g
        return act
    def card_action(self,p,q,g=.012):
        hp,hq=self.pose();s=self.env.scene
        cp=s.card.data.root_pos_w[self.ids];cq=s.card.data.root_quat_w[self.ids]
        dq=quat_mul(q,quat_conjugate(cq))
        return self.action(p+quat_apply(dq,hp-cp),quat_mul(dq,hq),g)
    def error(self,p,q):
        s=self.env.scene
        pe=(p-s.card.data.root_pos_w[self.ids]).norm(dim=-1)
        qe=quat_mul(q,quat_conjugate(s.card.data.root_quat_w[self.ids]));qe=torch.where(qe[:,:1]<0,-qe,qe)
        return pe,axis_angle_from_quat(qe).norm(dim=-1)

    def phase(self,p,q,label,ptol=.0005,rtol=.004,maxsteps=420):
        start=self.env.scene.card.data.root_pos_w[self.ids].clone()
        count=0
        for t in range(maxsteps):
            # Translation ramp stays above the table while moving into the chassis.
            alpha=min(1.,(t+1)/max(1.,float((p-start).norm(dim=-1).max())/.0015))
            yield self.card_action(start+(p-start)*alpha,q)
            pe,re=self.error(p,q)
            if alpha>=1 and bool(((pe<ptol)&(re<rtol)).all()):count+=1
            else:count=0
            if count>=20:break
        print('PHASE',self.support,label,'steps',t+1,'poserr',pe.tolist(),'roterr',re.tolist(),'held',self.env.scene.grasp_held[self.ids].tolist(),flush=True)
        return count>=20

def insert(env,ids,support):
    m=Precision(env,ids,support);s=env.scene
    seat=s.case.data.root_pos_w[ids]+quat_apply(s.case.data.root_quat_w[ids],m.tensor(s.cfg.seat_pos))
    q=s.case.data.root_quat_w[ids].clone()
    for label,offset in [('over',(-.04,0,.23)),('inside',(-.04,0,.012)),('slide',(0,0,.012))]:
        okay=yield from m.phase(seat+quat_apply(q,m.tensor(offset)),q,label)
        if not okay:
            print('STOP alignment gate',support,label,flush=True)
            return
    for t in range(260):
        offset=.012-min(.013,(t+1)*.00015)
        yield m.card_action(seat+quat_apply(q,m.tensor((0,0,offset))),q)
        if t>90 and bool(s.seated()[ids].all()):break
    print('PRESS',support,s.seated()[ids].tolist(),s.engaged()[ids].tolist(),flush=True)
    if not bool(s.seated()[ids].all()):return
    hp,hq=m.pose()
    for t in range(60):yield m.action(hp,hq,.04)
    for t in range(150):yield m.action(hp+m.tensor((0,0,.15))*min(1,(t+1)/75),hq,.04)
    print('END',support,'success',s.success()[ids].tolist(),'card',s.card.data.root_pos_w[ids].tolist(),flush=True)
