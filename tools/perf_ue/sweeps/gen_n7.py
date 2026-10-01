# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Round 04 night skyline sweep (critic round 03, secondary 1): night S4 window points on >= 3 % of the frame and city median Y <= 42 (round 03: 0.96 % / 58, "day-for-night").
Levers: the moonlight / sky light / city-glow fills that light the facades (down), the window emission (MPC_City InteriorGain / EmissiveScale, up), exposure bias.
Shots S1, S4, S5, S6 (street views keep L3 / L13 / L14).  Every variant sets every key.  usage: gen_n7.py [outdir] -> v_n7.json"""
import json, os, sys
MPC = '/Game/City/Materials/MPC_City.MPC_City'
BASE = dict(moon=16.0, sky=2.5, glow=1.0, ig=1.3, es=12.0, sg=1.6, bias=-0.25)
GLOW = dict(West=3.4, North=0.765, South=0.765, East=0.51)
def N(**k):
    d = dict(BASE); d.update(k)
    return ['set Moon - Intensity %g' % d['moon'], 'set SkyLight - Intensity %g' % d['sky']] + ['set CityGlow%s - Intensity %g' % (n, l * d['glow']) for n, l in GLOW.items()] + [
            'mpc %s InteriorGain %g' % (MPC, d['ig']), 'mpc %s EmissiveScale %g' % (MPC, d['es']), 'mpc %s ShopGain %g' % (MPC, d['sg']), 'post AutoExposureBias %g' % d['bias']]
V = {
    'n0_v2': N(),
    'n1_dark': N(moon=6, sky=1.2, glow=0.5),
    'n2_dark_win': N(moon=6, sky=1.2, glow=0.5, ig=2.6, es=20),
    'n3_dark_win2': N(moon=6, sky=1.2, glow=0.5, ig=4.0, es=28),
    'n4_darker_win2': N(moon=3, sky=0.7, glow=0.35, ig=4.0, es=28),
    'n5_dark_win2_b': N(moon=6, sky=1.2, glow=0.5, ig=4.0, es=28, bias=-0.6),
    'n6_dark_win3': N(moon=6, sky=1.2, glow=0.5, ig=6.0, es=40),
    'n7_mid_win2': N(moon=10, sky=1.8, glow=0.75, ig=4.0, es=28, bias=-0.45),
}
if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ.get('SM2_LOOK_SCRATCH', '/Users/midir/sm2-n1/_scratch/look'), 'eval7')
    os.makedirs(out, exist_ok=True); p = os.path.join(out, 'v_n7.json'); json.dump({'variants': V}, open(p, 'w'), indent=1); print('wrote', p, len(V))
