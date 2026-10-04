import sys,subprocess,numpy as np
v=sys.argv[1]; w,h=480,270
p=subprocess.Popen(['ffmpeg','-v','error','-i',v,'-vf',f'scale={w}:{h},format=gray','-f','rawvideo','-'],stdout=subprocess.PIPE)
fr=[]
while True:
    b=p.stdout.read(w*h)
    if len(b)<w*h:break
    fr.append(np.frombuffer(b,np.uint8).astype(np.float32))
fr=np.array(fr); np.save(sys.argv[2],fr); print(fr.shape)
