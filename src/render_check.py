import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
M=json.load(open('model.json'))
def render(fn, eye, tgt, fov=60, hide=('Ceiling',), W=1400, Hh=800):
    eye=np.array(eye,float); tgt=np.array(tgt,float)
    f=tgt-eye; f/=np.linalg.norm(f); r=np.cross(f,[0,0,1]); r/=np.linalg.norm(r); u=np.cross(r,f)
    L=np.array([0.4,-0.5,0.75]); L/=np.linalg.norm(L)
    polys=[];cols=[];depth=[]
    k=1/np.tan(np.radians(fov)/2)
    for p in M['prims']:
        if p['tag'] in hide: continue
        c=np.array(M['mats'][p['mat']][:3])/255; a=M['mats'][p['mat']][3]
        for face in p['faces']:
            P=np.array(face,float)-eye
            z=P@f
            if (z<50).any(): continue
            n=np.cross(P[1]-P[0],P[2]-P[0]); n/= (np.linalg.norm(n) or 1)
            sh=0.55+0.45*abs(n@L)
            polys.append(np.c_[k*(P@r)/z, k*(P@u)/z]); cols.append((*np.clip(c*sh,0,1),a)); depth.append(z.mean())
    o=np.argsort(depth)[::-1]
    fig=plt.figure(figsize=(W/100,Hh/100)); ax=fig.add_axes([0,0,1,1])
    ax.add_collection(PolyCollection([polys[i] for i in o],facecolors=[cols[i] for i in o],edgecolors=(0,0,0,.5),linewidths=.3))
    ax.set_xlim(-W/Hh,W/Hh); ax.set_ylim(-1,1); ax.axis('off'); fig.savefig(fn,dpi=100); plt.close(fig)
