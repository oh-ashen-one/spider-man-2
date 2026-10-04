import json,struct,sys
def load(p):
    b=open(p,'rb').read()
    n=struct.unpack('<I',b[12:16])[0]
    return json.loads(b[20:20+n])
for p in sys.argv[1:]:
    g=load(p)
    print('==',p)
    for m in g.get('meshes',[]):
        for pr in m['primitives']:
            a=pr['attributes']; acc=g['accessors']
            tris=acc[pr['indices']]['count']//3 if 'indices' in pr else None
            print(' mesh',m.get('name'),'verts',acc[a['POSITION']]['count'],'tris',tris,'attrs',sorted(a), 'mat',pr.get('material'))
    for i,mt in enumerate(g.get('materials',[])):
        pb=mt.get('pbrMetallicRoughness',{})
        print(' mat',i,mt.get('name'),'bc' if 'baseColorTexture' in pb else '-','mr' if 'metallicRoughnessTexture' in pb else '-','n' if 'normalTexture' in mt else '-','o' if 'occlusionTexture' in mt else '-', 'mf',pb.get('metallicFactor'),'rf',pb.get('roughnessFactor'), mt.get('extensions',{}).keys())
    for im in g.get('images',[]): print(' img',im.get('name'),im.get('mimeType'))
    sk=g.get('skins',[])
    for s in sk: print(' skin joints',len(s['joints']))
    an=g.get('animations',[])
    print(' anims',len(an))
    # fps estimate
    import itertools
    fpss=[]
    buf=open(p,'rb').read()
    n=struct.unpack('<I',buf[12:16])[0]; off=20+n+8
    for a in an[:200]:
        s=a['samplers'][0]; acc=g['accessors'][s['input']]
        bv=g['bufferViews'][acc['bufferView']]
        st=off+bv.get('byteOffset',0)+acc.get('byteOffset',0)
        t=struct.unpack('<%df'%acc['count'],buf[st:st+4*acc['count']])
        if len(t)>2:
            d=sorted(set(round(t[i+1]-t[i],5) for i in range(len(t)-1)))
            fpss.append((a.get('name'),len(t),round(t[-1],3),d[:3]))
    for f in fpss: print('  ',f)
