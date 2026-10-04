import cv2, numpy as np, sys
def wall_edge(im):
    mx=im.max(2); mn=im.min(2); ch=(mx-mn)/np.maximum(mx,1); Y=0.2126*im[...,2]+0.7152*im[...,1]+0.0722*im[...,0]
    H=im.shape[0]; e=np.full(H,-1.0)
    for y in range(H):
        m=((ch[y]>0.42)&(Y[y]>40)).astype(int); c=np.convolve(m,np.ones(12,int),'valid'); xs=np.where(c>=12)[0]
        if len(xs): e[y]=xs[0]
    return e, Y
def band(im, thr=180.0):
    e,Y=wall_edge(im)
    ok=e>=0; ys=np.arange(len(e))
    # robust line fit of the edge (the bulkhead is straight in this framing)
    A=np.polyfit(ys[ok],e[ok],1); r=np.abs(e-np.polyval(A,ys)); keep=ok&(r<8); A=np.polyfit(ys[keep],e[keep],1)
    edge=np.polyval(A,ys)
    W=[]
    for y in ys:
        x=int(edge[y]); 
        # pixels at Y>=thr within [x-60, x+2]: the band = longest run of >= thr ending within 6 px of the edge
        seg=Y[y,max(0,x-80):x+3][::-1]
        run=0; started=False; gap=0
        for i,v in enumerate(seg):
            if v>=thr: run=i+1; started=True; gap=0
            else:
                if started: gap+=1
                if (started and gap>3) or (not started and i>8): break
        W.append(run if started else 0)
    W=np.array(W)
    return dict(edge_fit=[round(A[0],4),round(A[1],1)], band_px_median=float(np.median(W)), rows_ge12_pct=round(float((W>=12).mean()*100),1), band_px_p75=float(np.percentile(W,75)))
if __name__=='__main__':
    for f in sys.argv[1:]: print(f.split('/')[-2], band(cv2.imread(f).astype(np.float32)))
