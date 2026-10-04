# offline model of the r23 vertical recovery (U along the run, N off the wall), foot ankle positions in leg lengths
import math
Ll=0.88; Sig=0.40; Top=0.42; Bot=0.96
def ease(x): x=min(max(x,0),1); return x*x*(3-2*x)
def foot(phi, Kt=0.45, Otr=0.80, Sw=0.34):
    OTd=-Top*Ll; OTo=-Bot*Ll
    if phi<Sig:
        k=phi/Sig; return OTd+(OTo-OTd)*k, 0.02
    k=(phi-Sig)/(1-Sig)
    if k<Kt: O=OTo+(-Otr*Ll-OTo)*ease(k/Kt)
    else: O=-Otr*Ll+(OTd+Otr*Ll)*ease((k-Kt)/(1-Kt))
    off=0.02+Sw*math.sin(math.pi*k)**0.8
    return O,off
def run(cad=6.0, **kw):
    dt=1/60; ph=0; seps=[]; offs=[]
    for i in range(int(2/dt)):
        ph=(ph+dt*cad*0.5)%1
        oL,fL=foot(ph,**kw); oR,fR=foot((ph+0.5)%1,**kw)
        seps.append(abs(oL-oR)); offs.append(max(fL,fR))
    # crossings below .15 and above .35 (alternations)
    st=None; n=0
    for s in seps:
        if s<0.15 and st!='lo': n+= st is not None; st='lo'
        elif s>0.35 and st!='hi': n+= st is not None; st='hi'
    print(kw, f"cad {cad}: sep {min(seps):.2f}-{max(seps):.2f}, alternations/s {n/2:.1f}")
for kw in [dict(),dict(Otr=0.7),dict(Otr=0.9),dict(Kt=0.3)]:
    run(**kw); run(cad=5.6,**kw)
