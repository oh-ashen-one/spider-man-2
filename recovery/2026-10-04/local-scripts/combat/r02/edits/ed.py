import re,sys
class Ed:
    def __init__(s,p): s.p=p; s.s=open(p).read()
    def rep(s,a,b,cnt=1):
        lines=a.strip('\n').split('\n')
        pat='\n'.join(r'[ \t]*'+re.escape(l.lstrip('\t ')) for l in lines)
        m=list(re.finditer(pat,s.s))
        if len(m)!=cnt: raise SystemExit('MATCH %d != %d for: %s'%(len(m),cnt,a[:100]))
        s.s=s.s[:m[0].start()]+b.strip('\n')+s.s[m[0].end():]
    def save(s): open(s.p,'w').write(s.s)
