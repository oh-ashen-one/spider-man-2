import json, sys, os
base='/Users/midir/sm2-n1/traversal/docs/night1/traversal/scripts/city/'
def mk(name, dx, dy, tag):
    j=json.load(open(base+name+'.json'))
    j['spawn']['pos'][0]+=dx; j['spawn']['pos'][1]+=dy
    d='/Users/midir/sm2-n1/_scratch/traversal/r16/scripts/'+tag
    os.makedirs(d, exist_ok=True)
    json.dump(j, open(d+'/'+name+'.json','w'), indent=1)
    return d
if __name__=='__main__':
    name=sys.argv[1]; dx=float(sys.argv[2]); dy=float(sys.argv[3]); print(mk(name,dx,dy,sys.argv[4]))
