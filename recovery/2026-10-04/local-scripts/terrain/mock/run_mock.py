import sys, os
sys.path.insert(0, '/Users/midir/sm2-n1/_scratch/terrain/mock')
import unreal
src = '/Users/midir/sm2-n1/terrain/unreal/WebHomage/Scripts/build_terrain.py'
ns = {'__file__': src, '__name__': '__main__'}
exec(compile(open(src).read(), src, 'exec'), ns)
