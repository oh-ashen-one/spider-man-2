# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""ORIGINAL hero suit, round 08 ("Tessera").  Procedural, evaluated per texel in rest-pose object space (x = character's left,
y up, z forward, metres), so there is no hand-drawn source art and nothing is copied from any existing suit.

Design language (written up in docs/night1/characters/round-08/SUIT_ORIGINALITY.md):
  * palette: slate TEAL body, DEEP ink-teal panels, AMBER accents, STITCH light-teal dashes.  No red / blue blocking, no white emblem.
  * asymmetric cross-balance: the character's RIGHT arm and right greave carry the amber "light" side, the LEFT thigh an amber net, the other limbs the dark side.
  * a tilted amber bandolier sash (a plane slice of the torso, front and back differ) instead of a symmetric chest graphic.
  * joint sleeves: DEEP slabs between two planes perpendicular to the limb axis with amber rings at the shoulders (raglan caps), elbows and knees
    (plane cuts, not sphere cuts: a sphere cut of the faceted low-poly mesh zig-zags).
  * net: a diamond net of two opposite helices wound around each body segment (helix_dist), hairline dark on the TEAL panels, amber with raised knots on the
    right upper arm and the left thigh; no radial / orb web and no spider figure anywhere.  Hexagonal honeycomb on the crown and the jaw vent.
  * chest badge: a hexagon ring with three gaps and three kite vanes around a hex core (a net junction), on the sternum; a plain broken ring on the back.
  * dashed top-stitching beside the piping lines, raised piping / grooves in the height map, per-panel roughness.
  * the mask: DEEP hood (plane cut at the neck, inside the neck cylinder), TEAL_D crown cap with an amber piping arc, two amber brow flashes, honeycomb jaw vent,
    dorsal seam; the eyes are separate geometry (tools/ue_char/hero_lens_r8.py).
"""
import copy
import numpy as np

SQ3 = 1.7320508075688772

# ------------------------------------------------------------------------------------------------ style (round 11: the suit generator)
# Every design decision of Tessera is a field of one style dict; DEFAULT_STYLE reproduces round 08 texel for texel.  New suits are JSON overrides of it
# (tools/ue_char/suits/suits.json -> gen_suits.py): palette, panel layout (wedges, trunks, sash kind), net kind, chest / back glyph, hood pattern,
# accent placement.  Nothing in a style names or copies an existing suit.
DEFAULT_STYLE = dict(
    id='tessera', name='Tessera',
    palette=dict(body='#0f4452', crown='#0b3441', deep='#071a21', ink='#050d11', accent='#e0780c', accent_d='#ad5c08', stitch='#9cc0c6', sole='#0d1012'),
    flip=False,                                       # mirror the whole layout left <-> right (the accent arm becomes the character's left)
    net=dict(kind='diamond', scale=1.0, width=1.0),    # diamond | hex | rib | square | chevron | brick | none
    sash=dict(kind='slash', n=[0.36, 0.88, 0.30], c_y=1.27, half=0.035, curve=0.0, gap=0.09, fold=False, along=[0.925, -0.379, 0.0]),   # slash | vee | double | yoke | placket | none
    wedge=dict(on=True, base=0.088, flare=0.10),
    trunks=dict(on=True, slope=0.62, y0=0.80),
    belt=dict(on=True, buckle='hex'),                  # hex | round | bar | none
    spine=True,
    arm=dict(upper='deep', fore='sleeve', other_fore='bands'),     # accent arm: upper deep | body ; fore sleeve | deep | body; other forearm: bands | sleeve | body
    greave='accent',                                   # accent | none   (the accent-side shin)
    thigh_deep=True,                                   # the other thigh is a DEEP panel with an accent net
    sleeves=True,
    glyph=dict(kind='hexvane', size=1.0, y=1.372, x=0.0),    # hexvane | orbit | tally | lattice | gate | keystone | ladder | chevrons
    crown=dict(kind='honeycomb', edge=True),           # honeycomb | racing | chevron | plain
    brow='flash',                                      # flash | tick | none
    vent='hex',                                        # hex | slots | none
    hood='deep', glove='deep', boot='deep',            # colour role of the mask, gloves and boots: deep | body | accent_d
    mott=1.0,
    fuzz=[0.50, 0.62, 0.68],                           # cloth sheen tint (material parameter, not painted)
)


def merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict): out[k] = merge(out[k], v)
        else: out[k] = copy.deepcopy(v)
    return out


def resolve(style=None):
    return merge(DEFAULT_STYLE, style) if style else copy.deepcopy(DEFAULT_STYLE)


def srgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255.0


TEAL = srgb('#0f4452')   # (round 08 constants; paint() takes its colours from the style palette)
TEAL_D = srgb('#0b3441')
DEEP = srgb('#071a21')
INK = srgb('#050d11')
AMBER = srgb('#e0780c')
AMBER_D = srgb('#ad5c08')
BONE = srgb('#e6dfc9')
STITCH = srgb('#9cc0c6')
SOLE = srgb('#0d1012')


# ------------------------------------------------------------------------------------------------ helpers
def ss(x, a, b):
    t = np.clip((x - a) / (b - a + 1e-12), 0, 1)
    return t * t * (3 - 2 * t)


def cover(d, aa):
    """Anti-aliased coverage of a signed distance d (metres, negative inside) with texel footprint aa."""
    return np.clip(0.5 - d / aa, 0, 1)


def band(dist, half, aa):
    return cover(np.abs(dist) - half, aa)


def stitch(d, along, aa, off=0.0030, period=0.0048, hw=0.00038, duty=0.58):
    """Two rows of dashed top-stitching at +-off (metres) from a seam line.  d = signed distance to the line, along = coordinate along it (metres)."""
    ph = np.abs((along / period) % 1.0 - 0.5) * 2.0                                # 0 at the dash centre, 1 at the gap centre
    on = 1.0 - ss(ph, duty - 0.12, duty + 0.04)
    return band(np.abs(d) - off, hw, aa) * on


def mix(a, b, t):
    return a * (1 - t[..., None]) + b * t[..., None]


def hex_d(u, v, apothem, pointy=True):
    """Signed distance-ish of a regular hexagon (negative inside), apothem = centre-to-flat distance."""
    if not pointy: u, v = v, u
    d = np.maximum(np.maximum(np.abs(u), np.abs(0.5 * u + 0.5 * SQ3 * v)), np.abs(-0.5 * u + 0.5 * SQ3 * v))
    return d - apothem


def hex_cell_edge(u, v, R):
    """Distance to the nearest edge of a pointy-top hexagonal lattice with circumradius R (>= 0)."""
    q = (SQ3 / 3 * u - v / 3) / R; r = (2 / 3 * v) / R
    x, z = q, r; y = -x - z
    rx, ry, rz = np.round(x), np.round(y), np.round(z)
    dx, dy, dz = np.abs(rx - x), np.abs(ry - y), np.abs(rz - z)
    m1 = (dx > dy) & (dx > dz); m2 = (~m1) & (dy > dz)
    rx = np.where(m1, -ry - rz, rx); rz = np.where((~m1) & (~m2), -rx - ry, rz)
    cu = R * SQ3 * (rx + rz / 2); cv = R * 1.5 * rz
    a = R * SQ3 / 2
    return a - hex_d(u - cu, v - cv, 0.0)


def noise3(P, f, seed=0):
    """Cheap smooth 3D value-ish noise (sum of sines), range about [-1, 1]."""
    r = np.random.RandomState(seed)
    k = r.randn(4, 3); ph = r.rand(4) * 6.28
    acc = 0
    for i in range(4):
        acc = acc + np.sin((P @ (k[i] * f / 1.3)) + ph[i])
    return acc / 2.0


def unit(v):
    v = np.asarray(v, np.float64); return v / np.linalg.norm(v)


def seg_coords(P, A, B, e1=None):
    """(s metres along A->B, theta around it with theta = 0 facing e1 (default +z))."""
    A = np.asarray(A, np.float32); B = np.asarray(B, np.float32)
    d = (B - A); d = d / np.linalg.norm(d)
    if e1 is None: e1 = np.array([0, 0, 1.0], np.float32)
    e1 = e1 - d * float(np.dot(e1, d)); e1 = (e1 / np.linalg.norm(e1)).astype(np.float32)
    e2 = np.cross(d, e1).astype(np.float32)
    rel = P - A
    return rel @ d, np.arctan2(rel @ e2, rel @ e1)


def helix_dist(P, A, B, R, cell, K=None, phase=0.0, e1=None, nodes=False):
    """Distance (metres, on the surface) to the nearest line of a diamond net wound around the segment A->B: two helix families of opposite
    hand, 45 degrees to the axis, K cells around (integer so the net closes), `cell` metres along the axis per diamond half-period."""
    A = np.asarray(A, np.float32); B = np.asarray(B, np.float32)
    d = (B - A); L = float(np.linalg.norm(d)); d = d / L
    if e1 is None: e1 = np.array([0, 0, 1.0], np.float32)
    e1 = e1 - d * float(np.dot(e1, d)); e1 = (e1 / np.linalg.norm(e1)).astype(np.float32)
    e2 = np.cross(d, e1).astype(np.float32)
    rel = P - A
    s = rel @ d
    r1 = rel @ e1; r2 = rel @ e2
    th = np.arctan2(r2, r1)
    if K is None: K = max(3, int(round(2 * np.pi * R / cell)))
    u = s / cell + K * th / (2 * np.pi) + phase
    v = s / cell - K * th / (2 * np.pi) + phase
    k = cell / np.sqrt(2.0)
    du = np.abs(u - np.round(u)); dv = np.abs(v - np.round(v))
    if nodes: return np.minimum(du, dv) * k, np.sqrt(du * du + dv * dv) * k
    return np.minimum(du, dv) * k



# ------------------------------------------------------------------------------------------------ net kinds (round 11)
def hex_lattice(u, v, R):
    """Pointy-top hexagonal lattice, circumradius R: (distance to the nearest cell edge >= 0, distance to the nearest cell centre)."""
    q = (SQ3 / 3 * u - v / 3) / R; r = (2 / 3 * v) / R
    x, z = q, r; y = -x - z
    rx, ry, rz = np.round(x), np.round(y), np.round(z)
    dx, dy, dz = np.abs(rx - x), np.abs(ry - y), np.abs(rz - z)
    m1 = (dx > dy) & (dx > dz); m2 = (~m1) & (dy > dz)
    rx = np.where(m1, -ry - rz, rx); rz = np.where((~m1) & (~m2), -rx - ry, rz)
    cu = R * SQ3 * (rx + rz / 2); cv = R * 1.5 * rz
    a = R * SQ3 / 2
    du, dv = u - cu, v - cv
    hn = np.maximum(np.maximum(np.abs(du), np.abs(0.5 * du + 0.5 * SQ3 * dv)), np.abs(-0.5 * du + 0.5 * SQ3 * dv))
    return a - hn, np.sqrt(du * du + dv * dv)


def netd(P, A, B, R, cell, kind='diamond', phase=0.0, scale=1.0, nodes=False):
    """Distance (metres, on the surface) to the nearest line of a surface net wound around the segment A->B (radius R), and with nodes=True also the
    distance to the nearest knot.  kind: diamond (two opposite helices: the round-08 net) | hex (honeycomb, integer columns so it closes around the
    limb) | rib (rings) | square (rings + meridians) | chevron (V rings, cusp at the front and the back) | brick (rings + staggered verticals) | none."""
    cell = cell * scale
    if kind == 'diamond':
        return helix_dist(P, A, B, R, cell, phase=phase, nodes=nodes)
    A = np.asarray(A, np.float32); B = np.asarray(B, np.float32)
    s, th = seg_coords(P, A, B)
    far = np.full(s.shape, 1.0, np.float32)
    if kind == 'none':
        return (far, far) if nodes else far
    circ = 2 * np.pi * R
    arc = R * th
    ring = s / cell + phase
    d_ring = np.abs(ring - np.round(ring)) * cell
    if kind == 'rib':
        return (d_ring, far) if nodes else d_ring
    if kind == 'square':
        K = max(4, int(round(circ / (cell * 1.15))))
        m = th * K / (2 * np.pi)
        d_mer = np.abs(m - np.round(m)) * (circ / K)
        d = np.minimum(d_ring, d_mer)
        return (d, np.sqrt(d_ring ** 2 + d_mer ** 2)) if nodes else d
    if kind == 'chevron':
        t = 0.9
        u = (s + np.abs(arc) * t) / cell + phase
        d = np.abs(u - np.round(u)) * cell / np.sqrt(1 + t * t)
        return (d, far) if nodes else d
    if kind == 'brick':
        K = max(4, int(round(circ / (cell * 1.6))))
        rows = np.floor(ring)
        m = th * K / (2 * np.pi) + 0.5 * (rows % 2)
        d_mer = np.abs(m - np.round(m)) * (circ / K)
        d = np.minimum(d_ring, d_mer)
        return (d, np.sqrt(d_ring ** 2 + d_mer ** 2)) if nodes else d
    if kind == 'hex':
        K = max(4, int(round(circ / (SQ3 * cell))))
        Rh = circ / (K * SQ3)
        e, c = hex_lattice(arc, s + phase * cell, Rh)
        return (e, c) if nodes else e
    raise KeyError('net kind %s' % kind)


# ------------------------------------------------------------------------------------------------ chest / back glyphs (round 11, all original abstract marks)
def glyph(kind, x, y, cx, cy, size, aa):
    """(line, solid) anti-aliased masks of an abstract glyph centred at (cx, cy); size 1 = about 9 cm across.  None of them is a spider, bat, star, shield,
    crescent, letter or any existing emblem: they are geometric marks built from rings, bars, rhombi and arches."""
    u = (x - cx) / size; v = (y - cy) / size
    a = aa / size
    zero = np.zeros_like(u)
    if kind == 'orbit':
        r = np.hypot(u, v); ang = np.arctan2(v, u)
        da = np.abs((ang - 0.9 + np.pi) % (2 * np.pi) - np.pi)
        line = band(r - 0.043, 0.0024, a) * (1 - cover(da - 0.42, a / 0.043))
        solid = np.maximum(cover(np.hypot(u - 0.007, v + 0.004) - 0.0165, a), cover(np.hypot(u - 0.043 * np.cos(0.9), v - 0.043 * np.sin(0.9)) - 0.0048, a))
        return line, solid
    if kind == 'tally':
        solid = zero.copy()
        us = u - 0.28 * (v + 0.03)                                  # sheared bars
        for i in range(4):
            xi = (i - 1.5) * 0.0165; hi = 0.020 + 0.0135 * i
            d = np.maximum(np.abs(us - xi) - 0.0030, np.maximum(-0.030 - v, v - (-0.030 + hi)))
            solid = np.maximum(solid, cover(d, a))
        line = band(v + 0.037, 0.0016, a) * cover(np.abs(u) - 0.042, a)
        return line, solid
    if kind == 'lattice':
        ka = 1.0 / np.sqrt(1 / 0.040 ** 2 + 1 / 0.052 ** 2)
        d_out = (np.abs(u) / 0.040 + np.abs(v) / 0.052 - 1.0) * ka
        d_in = (np.abs(u) / 0.020 + np.abs(v) / 0.026 - 1.0) * ka * 0.5
        diag = band((0.78 * u - 0.62 * v) * 1.0, 0.0017, a) * cover(d_out + 0.004, a)
        line = np.maximum(band(d_out + 0.0022, 0.0023, a), np.maximum(band(d_in, 0.0018, a) * 0.0, diag))
        solid = cover((np.abs(u) / 0.010 + np.abs(v) / 0.013 - 1.0) * ka * 0.3, a) * 1.0
        return line, solid
    if kind == 'gate':
        top = np.hypot(u, v - 0.010) - 0.033
        side = np.abs(u) - 0.033
        d = np.where(v > 0.010, top, side)
        line = band(d + 0.0018, 0.0023, a) * cover(-0.040 - v, a)          # open at the bottom (v < -0.040)
        solid = np.maximum(cover(np.maximum(np.abs(u) - 0.013, np.abs(v + 0.004) - 0.0030), a), cover(np.hypot(u, v - 0.016) - 0.0058, a))
        return line, solid
    if kind == 'keystone':
        hw = 0.031 + 0.009 * (v / 0.032)
        d = np.maximum((np.abs(u) - hw) * 0.99, np.abs(v) - 0.032)
        line = band(d + 0.0019, 0.0023, a)
        solid = cover(np.maximum(np.abs(u) - 0.0036, np.maximum(-0.019 - v, v - 0.013)), a)
        return line, solid
    if kind == 'ladder':
        rails = np.maximum(cover(np.maximum(np.abs(np.abs(u) - 0.020) - 0.0030, np.abs(v) - 0.034), a), 0)
        line = zero.copy()
        for k in (-0.022, -0.007, 0.008, 0.023):
            line = np.maximum(line, cover(np.maximum(np.abs(v - k) - 0.0026, np.abs(u) - 0.019), a))
        return line, rails
    if kind == 'chevrons':
        line = zero.copy()
        for i in range(3):
            c = 0.026 - 0.018 * i
            d = np.abs(v - (c - 0.82 * np.abs(u))) / np.sqrt(1 + 0.82 ** 2)
            line = np.maximum(line, band(d, 0.0028, a) * cover(np.abs(u) - (0.036 - 0.004 * i), a))
        return line, zero
    raise KeyError('glyph kind %s' % kind)


# ------------------------------------------------------------------------------------------------ the suit
class Canvas:
    """Layered texel canvas: colour, height (mm), roughness, occlusion."""
    def __init__(self, shape, base):
        self.col = np.tile(base, shape + (1,)).astype(np.float32)
        self.h = np.zeros(shape, np.float32)
        self.rough = np.full(shape, 0.74, np.float32)
        self.ao = np.ones(shape, np.float32)

    def lay(self, alpha, c, h=None, rough=None, ao=None, hmode='set'):
        a = np.clip(alpha, 0, 1).astype(np.float32)
        c = np.asarray(c, np.float32)
        self.col = self.col * (1 - a[..., None]) + (c if c.ndim > 1 else c[None, None, :]) * a[..., None]
        if h is not None:
            self.h = self.h + (np.asarray(h, np.float32) - self.h) * a if hmode == 'set' else self.h + a * np.asarray(h, np.float32)
        if rough is not None: self.rough = self.rough + (rough - self.rough) * a
        if ao is not None: self.ao = self.ao + (ao - self.ao) * a


def paint(P, N, G, mpt, gi, jp, style=None):
    """P, N (r, n, 3) float32 rest-pose positions / normals; G (r, n, 9) group weights; mpt (r, n) metres per texel (AA footprint);
    gi = {group name: index}; jp = {joint name: (x, y, z)}; style = override dict of DEFAULT_STYLE (None = Tessera).
    Returns dict(col (r, n, 3) sRGB 0..1, h mm, rough, ao)."""
    S = resolve(style)
    pal = {k: srgb(v) for k, v in S['palette'].items()}
    TEAL, TEAL_D, DEEP, INK = pal['body'], pal['crown'], pal['deep'], pal['ink']
    AMBER, AMBER_D, STITCH, SOLE = pal['accent'], pal['accent_d'], pal['stitch'], pal['sole']
    if S['flip']:       # evaluate the mirrored suit: x -> -x on positions and normals (the body is bilaterally symmetric, joints are looked up by the mirrored side)
        P = P * np.array([-1, 1, 1], np.float32); N = N * np.array([-1, 1, 1], np.float32)
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    ax = np.abs(x)
    aa = np.maximum(mpt, 6e-5).astype(np.float32) * 1.2
    g = lambda k: G[..., gi[k]]
    sharp = lambda w: ss(w, 0.42, 0.58)
    head = g('head'); torso = g('torso'); shoulder = g('shoulder'); armU = sharp(g('armU')); armF = sharp(g('armF')); hand = sharp(g('hand'))
    thigh = sharp(g('thigh')); shin = sharp(g('shin')); foot = sharp(g('foot'))
    nx, ny, nz = N[..., 0], N[..., 1], N[..., 2]
    C = Canvas(x.shape, TEAL)
    r_neck = np.hypot(x, z + 0.022)
    neck_ok = np.where(y < 1.54, cover(r_neck - 0.080, aa), 1.0).astype(np.float32)     # below the ear line only the neck cylinder (not the trapezius) belongs to the hood
    is_head = cover(1.480 - y, aa) * neck_ok * ss(head, 0.05, 0.15)            # hood: straight plane cut at the neck (the skin-weight ramp is soft and uneven)
    shoulder_arm = shoulder * ss(ax, 0.10, 0.17)
    arm_w = np.clip(armU + armF + hand + shoulder_arm, 0, 1)
    tors_w = sharp(np.clip(torso + shoulder * (1 - ss(ax, 0.10, 0.17)), 0, 1))
    leg_w = np.clip(thigh + shin + foot, 0, 1)
    trunk_w = sharp(np.clip(g('torso') + g('thigh') + g('shoulder') * (1 - ss(ax, 0.10, 0.17)), 0, 1))
    body_w = 1 - is_head
    R_ = (x < 0).astype(np.float32)               # the character's RIGHT (amber arm, dark leg)
    L_ = 1 - R_
    sgn = np.where(x < 0, -1.0, 1.0).astype(np.float32)
    front = ss(nz, 0.15, 0.55); back = ss(-nz, 0.15, 0.55)

    def D(c): return np.sqrt((x - c[0]) ** 2 + (y - c[1]) ** 2 + (z - c[2]) ** 2)
    def pdot(v, c=(0.0, 0.0, 0.0)): return P @ np.asarray(v, np.float32) - np.float32(np.dot(v, c))
    def J(n): return np.asarray(jp[n], np.float32)

    # ------------------------------------------------------------------ colour blocking
    # 1. torso side panels: a DEEP wedge that widens toward the waist
    wd = S['wedge']
    xb = wd['base'] + wd['flare'] * ss(y, 1.06, 1.33)
    m_side = tors_w * body_w * cover(xb - ax, aa) * ss(y, 1.00, 1.04) * (1.0 if wd['on'] else 0.0)
    C.lay(m_side, DEEP, rough=0.80)
    # 2. waist belt band + trunks (DEEP) above a diagonal hip-wrap cut across the thighs
    tk = S['trunks']
    belt_d = np.abs(y - 1.055) - 0.024
    if S['belt']['on']:
        C.lay(body_w * tors_w * cover(belt_d, aa), DEEP, rough=0.80)
    cut_norm = np.sqrt(1 + tk['slope'] ** 2)
    cut_d = (y - (tk['y0'] + tk['slope'] * x)) / cut_norm            # > 0 above the diagonal
    cut_along = (x + tk['slope'] * y) / (1.176 if abs(tk['slope'] - 0.62) < 1e-9 else cut_norm)
    if tk['on']:
        m_trunk = body_w * trunk_w * cover(np.maximum(y - 1.03, -cut_d), aa)
        C.lay(m_trunk, DEEP, rough=0.80)
    # back spine stripe (under the sash)
    back = ss(-nz, 0.15, 0.55)
    if S['spine']:
        m_spine = back * tors_w * body_w * cover(np.abs(x) - 0.013, aa) * cover(y - 1.44, aa) * cover(1.085 - y, aa) * cover(y - 1.335, aa)
        C.lay(m_spine, DEEP, rough=0.8)
    # 3. sash: a plane slice of the torso (slash), a folded plane (vee), two parallel slices (double), a curved yoke, or a vertical placket (front and back differ)
    sa = S['sash']
    zone_s = None
    if sa['kind'] != 'none':
        n_s = unit(sa['n'])
        Pf = np.stack([ax, y, z], -1) if sa['fold'] else P
        d_s = Pf @ np.asarray(n_s, np.float32) - np.float32(np.dot(n_s, (0.0, sa['c_y'], 0.0)))
        if sa['curve']: d_s = d_s + np.float32(sa['curve']) * x * x
        if sa['kind'] == 'placket':
            d_s = ax - 0.0 * y                                           # vertical band down the sternum
        y_lo, y_hi = (1.045, 1.44) if sa['kind'] != 'yoke' else (1.20, 1.50)
        zone_s = tors_w * body_w * ss(y, y_lo, y_lo + 0.045) * (1 - ss(y, y_hi, y_hi + 0.03)) * cover(ax - 0.160, aa)
        if sa['kind'] == 'placket': zone_s = tors_w * body_w * front * cover(1.083 - y, aa) * cover(y - 1.43, aa)      # hard ends: belt to collar
        hw = sa['half']
        offs = [0.0] if sa['kind'] != 'double' else [-sa['gap'] * 0.5, sa['gap'] * 0.5]
        t_s = np.asarray(sa['along'], np.float32)
        for o in offs:
            C.lay(zone_s * band(d_s - o, hw, aa), DEEP, rough=0.8)
            C.lay(zone_s * band(d_s - o, hw - 0.004, aa), AMBER, h=0.25, rough=0.50)
    # 5. arms.  Right arm = the amber "light" side, left arm = teal / dark side
    ar = S['arm']
    Rb = (x < 0)
    E_R, W_R = J('forearm.R'), J('hand.R'); E_L, W_L = J('forearm.L'), J('hand.L')
    def arm_t(E, W): d = W - E; return pdot(d / np.linalg.norm(d), E) / float(np.linalg.norm(d))
    t_fore_R, t_fore_L = arm_t(E_R, W_R), arm_t(E_L, W_L)
    t_fore = np.where(Rb, t_fore_R, t_fore_L)
    arm_tot = np.maximum(armU + shoulder_arm + armF + hand, 1e-3)
    upper_deep = ar['upper'] == 'deep'
    if upper_deep:
        C.lay(arm_w * R_ * ss(ax, 0.17, 0.22), DEEP, rough=0.80)                      # right upper arm + shoulder: DEEP
    if ar['fore'] == 'sleeve':
        C.lay(arm_w * R_ * (armF / arm_tot) * ss(t_fore, -0.02, 0.02), AMBER, rough=0.55)   # right forearm sleeve: amber
    elif ar['fore'] == 'deep':
        C.lay(arm_w * R_ * (armF / arm_tot) * ss(t_fore, -0.02, 0.02), DEEP, rough=0.78)
    if ar['other_fore'] == 'bands':
        for tc in (0.66, 0.76, 0.86):                                                  # left forearm: three amber wrist bands (cord wraps)
            C.lay(arm_w * L_ * armF * band(t_fore - tc, 0.0034, aa), AMBER, h=0.40, rough=0.5)
    elif ar['other_fore'] == 'sleeve':
        C.lay(arm_w * L_ * (armF / arm_tot) * ss(t_fore, 0.30, 0.34), AMBER_D, rough=0.55)
    ROLE = dict(deep=DEEP, body=TEAL, accent_d=AMBER_D, crown=TEAL_D)
    C.lay(hand * body_w, ROLE[S['glove']], rough=0.68)                                         # gloves
    for nm_, tw in (('R', t_fore_R), ('L', t_fore_L)):                                # amber wrist ring between sleeve and glove
        C.lay(band(tw - 1.02, 0.0042, aa) * arm_w * (x < 0 if nm_ == 'R' else x > 0), AMBER, h=0.4, rough=0.5)
    # 6. legs.  Left leg = amber side accents, right leg = dark side
    y_top = 0.40 + 0.5 * z
    greave_on = 1.0 if S['greave'] == 'accent' else 0.0
    m_greaveR = shin * R_ * cover(y - y_top, aa) * cover(0.10 - y, aa) * greave_on             # right shin: amber greave, slanted top edge
    C.lay(m_greaveR, AMBER, rough=0.52)
    if S['thigh_deep']:
        C.lay(thigh * L_ * ss(y, 0.52, 0.56), DEEP, rough=0.80)
    lat = np.abs(z - 0.0) - 0.011                                                   # outer seam stripe
    m_stripe = leg_w * np.clip(thigh + shin * ss(y, 0.42, 0.50), 0, 1) * cover(lat, aa) * ss(-sgn * nx, 0.4, 0.8)
    C.lay(m_stripe * R_ * (1 - m_greaveR), AMBER, h=0.35, rough=0.5)
    C.lay(m_stripe * L_, TEAL, h=0.35, rough=0.7)
    for yc in (0.175, 0.205):                                                       # left shin ankle bands
        C.lay(shin * L_ * band(y - yc, 0.0040, aa), AMBER, h=0.4, rough=0.5)
    m_boot = foot * body_w                                                          # boots: DEEP upper, INK toe cap, sole, amber welt
    C.lay(m_boot, ROLE[S['boot']], rough=0.72)
    C.lay(m_boot * ss(z, 0.085, 0.092), INK, rough=0.6)
    C.lay(foot * cover(y - 0.022, aa), SOLE, h=0.0, rough=0.88)
    C.lay(foot * band(y - 0.0265, 0.0015, aa), AMBER, h=0.3, rough=0.5)

    # ------------------------------------------------------------------ joint sleeves: DEEP slabs between planes perpendicular to the limb axis + amber rings
    # (plane slices, not sphere cuts: a plane slice of the faceted mesh is a clean curve, a sphere cut zig-zags +-1.5 mm on the low-poly shoulder)
    plate_m = np.zeros(x.shape, np.float32)
    def sleeve(A, B, s0, s1, zone):
        nonlocal plate_m
        s_, th_ = seg_coords(P, J(A), J(B))
        inside = cover(np.abs(s_ - 0.5 * (s0 + s1)) - 0.5 * (s1 - s0), aa)
        C.lay(inside * zone, DEEP, h=0.35, rough=0.60, ao=0.85)
        for sb in (s0 - 0.0035, s1 + 0.0035):
            C.lay(band(s_ - sb, 0.0017, aa) * zone, AMBER, h=0.55, rough=0.45)
            C.lay(stitch(s_ - sb, th_ * 0.055, aa, off=0.0042) * zone, STITCH, h=0.12, rough=0.7)
        plate_m = np.maximum(plate_m, inside * zone)
    for side_, nm in ((1.0, 'L'), (-1.0, 'R')):
        sidew = (sgn == side_).astype(np.float32)
        A_, B_ = J('deltoid.' + nm), J('forearm.' + nm)
        d_ = (B_ - A_) / np.linalg.norm(B_ - A_)
        rel_ = P - A_; s_a = rel_ @ d_; rr = np.linalg.norm(rel_ - s_a[..., None] * d_, axis=-1)
        if S['sleeves']:
            z_sh = sidew * body_w * (1 - is_head) * cover(rr - 0.108, aa) * 1.0
            sleeve('deltoid.' + nm, 'forearm.' + nm, -0.050, 0.075, z_sh)
            C.lay(band(rr - 0.108, 0.0010, aa) * sidew * body_w * (1 - is_head) * cover(np.abs(s_a - 0.0125) - 0.0625, aa), INK, h=-0.3, rough=0.9)
            z_el = sidew * body_w * np.clip(armU + armF, 0, 1)
            sleeve('deltoid.' + nm, 'forearm.' + nm, 0.262, 0.322, z_el)
            z_kn = sidew * body_w * np.clip(thigh + shin, 0, 1)
            sleeve('thigh.' + nm, 'shin.' + nm, 0.405, 0.470, z_kn)

    # ------------------------------------------------------------------ surface net (diamond / hex / rib / square / chevron / brick, wound around each body segment)
    nk, nsc = S['net']['kind'], S['net']['scale']
    def segnet(name_a, name_b, R, cell, phase=0.0):
        return netd(P, J(name_a), J(name_b), R, cell, kind=nk, phase=phase, scale=nsc)
    netw_a = 0.0015 * S['net']['width']      # half width of an amber net line
    netw_d = 0.0011 * S['net']['width']      # half width of a dark hairline
    nd_armU_R, nn_armU_R = netd(P, J('deltoid.R'), J('forearm.R'), 0.050, 0.052, kind=nk, scale=nsc, nodes=True); nd_armU_L = segnet('deltoid.L', 'forearm.L', 0.050, 0.052)
    nd_armF_R = segnet('forearm.R', 'hand.R', 0.040, 0.046); nd_armF_L = segnet('forearm.L', 'hand.L', 0.040, 0.046)
    tor_a, tor_b = np.array([0, 0.95, -0.012], np.float32), np.array([0, 1.52, -0.012], np.float32)
    nd_tor = netd(P, tor_a, tor_b, 0.14, 0.056, kind=nk, scale=nsc)
    nd_thR = segnet('thigh.R', 'shin.R', 0.078, 0.062); nd_thL, nn_thL = netd(P, J('thigh.L'), J('shin.L'), 0.078, 0.062, kind=nk, scale=nsc, nodes=True)
    nd_shR = segnet('shin.R', 'foot.R', 0.052, 0.050); nd_shL = segnet('shin.L', 'foot.L', 0.052, 0.050)
    z_up = tors_w * body_w * ss(y, 1.30, 1.38) * (1 - m_side)
    knots = nk in ('diamond', 'square', 'brick', 'hex')
    # amber net on the DEEP right upper arm; DEEP hairline net on the amber right forearm
    zR = arm_w * R_ * (armU + shoulder_arm) * ss(ax, 0.17, 0.22) * (1 - plate_m) * (1.0 if upper_deep else 0.0)
    C.lay(cover(nd_armU_R - netw_a, aa) * zR, AMBER, h=0.30, rough=0.5)
    if knots: C.lay(cover(nn_armU_R - 0.0032, aa) * zR, AMBER, h=0.55, rough=0.42)
    sF_R, thF_R = seg_coords(P, J('forearm.R'), J('hand.R'))
    if ar['fore'] == 'sleeve':
        top_R = cover(np.abs((thF_R - np.pi / 2 + np.pi) % (2 * np.pi) - np.pi) * 0.040 - 0.0035, aa)             # dorsal DEEP stripe on the amber forearm
        C.lay(top_R * arm_w * R_ * (armF / arm_tot) * ss(t_fore, 0.03, 0.08) * (1 - plate_m), DEEP, h=-0.30, rough=0.8)
        for tc in (0.25, 0.50):                                                                                  # two DEEP cross seams
            C.lay(band(t_fore - tc, 0.0016, aa) * arm_w * R_ * (armF / arm_tot) * (1 - plate_m), DEEP, h=-0.30, rough=0.8)
    # dark hairline net on the TEAL panels: upper chest / shoulders / back yoke, the whole left arm, left shin, right thigh
    C.lay(cover(nd_tor - netw_d, aa) * z_up * 0.85, DEEP, h=-0.25, rough=0.82)
    C.lay(cover(nd_armU_L - netw_d, aa) * arm_w * L_ * (armU + shoulder_arm) * (1 - plate_m) * 0.85, DEEP, h=-0.25, rough=0.82)
    C.lay(cover(nd_armF_L - netw_d, aa) * arm_w * L_ * armF * (1 - plate_m) * 0.85 * (1 - ss(t_fore, 0.55, 0.6)), DEEP, h=-0.25, rough=0.82)
    C.lay(cover(nd_shL - netw_d, aa) * shin * L_ * (1 - plate_m) * ss(y, 0.22, 0.26) * 0.85, DEEP, h=-0.25, rough=0.82)
    C.lay(cover(nd_thR - netw_d, aa) * thigh * R_ * (1 - plate_m) * ss(y, 0.60, 0.66) * 0.85, DEEP, h=-0.25, rough=0.82)
    # amber net on the DEEP left thigh and dark net on the amber greave
    zL = thigh * L_ * ss(y, 0.56, 0.60) * (1 - plate_m) * ss(0.78 - y, -0.03, 0.03) * (1.0 if S['thigh_deep'] else 0.0)
    C.lay(cover(nd_thL - netw_a * 0.9, aa) * zL, AMBER_D, h=0.25, rough=0.55)
    if knots: C.lay(cover(nn_thL - 0.0034, aa) * zL, AMBER, h=0.55, rough=0.42)
    sS_R, thS_R = seg_coords(P, J('shin.R'), J('foot.R'))
    C.lay(cover(np.abs((thS_R - 0.0 + np.pi) % (2 * np.pi) - np.pi) * 0.045 - 0.0035, aa) * m_greaveR * (1 - plate_m), DEEP, h=-0.30, rough=0.8)   # shin-front DEEP stripe

    # ------------------------------------------------------------------ chest badge (front) and back mark
    gl = S['glyph']
    def badge(cx, cy, outer_a):
        u = (x - cx); v = (y - cy)
        ring = band(hex_d(u, v, outer_a, pointy=True) + 0.0020, 0.0024, aa)
        ang = np.arctan2(v, u)
        gap = np.zeros_like(ang)
        for a0 in (np.pi / 6, 5 * np.pi / 6, -np.pi / 2):        # 3 gaps in the ring
            da = np.abs((ang - a0 + np.pi) % (2 * np.pi) - np.pi)
            gap = np.maximum(gap, cover(da - 0.16, aa / max(outer_a, 1e-3)))
        ring = ring * (1 - gap)
        vanes = np.zeros_like(ang)                                # 3 kite vanes pointing at 90, 210, 330 deg
        for a0 in (np.pi / 2, np.pi / 2 + 2 * np.pi / 3, np.pi / 2 + 4 * np.pi / 3):
            c, s_ = np.cos(a0), np.sin(a0)
            along = u * c + v * s_; perp = -u * s_ + v * c
            half = 0.0075 * np.clip(1 - (along / (outer_a * 0.68)), 0, 1) * np.clip(along / 0.006, 0, 1) + 0.0004
            vanes = np.maximum(vanes, cover(np.abs(perp) - half, aa) * cover(along - outer_a * 0.68, aa) * cover(-along + 0.004, aa))
        core = cover(hex_d(u, v, outer_a * 0.20, pointy=False), aa)
        return ring, vanes, core
    f_ = front * tors_w * body_w
    b_ = back * tors_w * body_w
    if gl['kind'] == 'hexvane':
        ring, vanes, core = badge(gl['x'], gl['y'], 0.046 * gl['size'])
        C.lay(f_ * ring, AMBER, h=0.45, rough=0.40)
        C.lay(f_ * np.maximum(vanes, core), AMBER, h=0.40, rough=0.40)
        ring_b, _, core_b = badge(0.0, gl['y'] + 0.023, 0.042 * gl['size'])
        C.lay(b_ * ring_b, AMBER, h=0.45, rough=0.40)
        C.lay(b_ * core_b, AMBER, h=0.40, rough=0.40)
    else:
        ln, so = glyph(gl['kind'], x, y, gl['x'], gl['y'], gl['size'], aa)
        C.lay(f_ * ln, AMBER, h=0.45, rough=0.40)
        C.lay(f_ * so, AMBER, h=0.40, rough=0.40)
        ln_b, so_b = glyph(gl['kind'], x, y, 0.0, gl['y'] + 0.023, gl['size'] * 0.8, aa)
        C.lay(b_ * ln_b, AMBER, h=0.45, rough=0.40)
        C.lay(b_ * so_b, AMBER, h=0.40, rough=0.40)
    # belt buckle
    bkind = S['belt']['buckle']
    if bkind == 'hex':
        bk = hex_d(x, y - 1.055, 0.021, pointy=False)
        C.lay(front * tors_w * body_w * cover(bk, aa), AMBER, h=0.5, rough=0.4)
        C.lay(front * tors_w * body_w * cover(hex_d(x, y - 1.055, 0.011, pointy=False), aa), DEEP, h=0.2, rough=0.6)
    elif bkind == 'round':
        rb = np.hypot(x, y - 1.055)
        C.lay(front * tors_w * body_w * cover(rb - 0.021, aa), AMBER, h=0.5, rough=0.4)
        C.lay(front * tors_w * body_w * cover(rb - 0.011, aa), DEEP, h=0.2, rough=0.6)
    elif bkind == 'bar':
        bk = np.maximum(np.abs(x) - 0.030, np.abs(y - 1.055) - 0.0075)
        C.lay(front * tors_w * body_w * cover(bk, aa), AMBER, h=0.5, rough=0.4)

    # ------------------------------------------------------------------ piping (amber hairlines) along the main cuts
    pip = 0.0014
    C.lay(body_w * tors_w * band(y - 1.0795, pip, aa), AMBER, h=0.45, rough=0.45)
    C.lay(body_w * tors_w * band(y - 1.0305, pip, aa), AMBER, h=0.45, rough=0.45)
    if tk['on']:
        C.lay(body_w * np.clip(tors_w + thigh, 0, 1) * band(cut_d, pip * 1.3, aa) * ss(1.03 - y, -0.002, 0.004), AMBER, h=0.45, rough=0.45)
    C.lay(m_side * band(xb - ax, pip, aa) * ss(y, 1.06, 1.12), AMBER_D, h=0.35, rough=0.5)
    # top-stitching beside the piping (dashed, light teal): belt, hip-wrap cut, sash edges, side wedge
    STa = 0.85
    C.lay(body_w * tors_w * np.maximum(stitch(y - 1.0795, x, aa), stitch(y - 1.0305, x, aa)) * STa, STITCH, h=0.12, rough=0.7)
    if tk['on']:
        C.lay(body_w * np.clip(tors_w + thigh, 0, 1) * stitch(cut_d, cut_along, aa, off=0.0034) * ss(1.03 - y, -0.002, 0.004) * STa, STITCH, h=0.12, rough=0.7)
    if zone_s is not None:
        for o in offs:
            hw_ = sa['half']
            C.lay(zone_s * np.maximum(stitch(d_s - o - hw_, P @ t_s, aa, off=0.0030) * (d_s - o > 0.0), stitch(d_s - o + hw_, P @ t_s, aa, off=0.0030) * (d_s - o < 0.0)) * STa, STITCH, h=0.12, rough=0.7)
    C.lay(m_side * stitch(xb - ax, y, aa, off=0.0030) * ss(y, 1.06, 1.12) * STa, STITCH, h=0.12, rough=0.7)

    # ------------------------------------------------------------------ mask / hood
    yb = 1.662 + 0.46 * z
    crown = is_head * cover(yb - y, aa)                         # above the boundary
    C.lay(is_head, ROLE[S['hood']], rough=0.80)
    C.lay(crown, TEAL_D, rough=0.74)
    if S['crown']['edge']:
        C.lay(is_head * band(y - yb, 0.0018, aa), AMBER, h=0.5, rough=0.45)
    ck = S['crown']['kind']
    if ck == 'honeycomb':           # crown honeycomb (hairline, projected from above)
        hc = hex_cell_edge(x, z, 0.014)
        C.lay(crown * ss(y, 1.72, 1.76) * cover(0.0009 - hc, aa) * 0.9 + 0.0 * crown, DEEP, h=-0.25, rough=0.85)
    elif ck == 'racing':            # two accent stripes over the crown, front to back
        for s_ in (-1.0, 1.0):
            C.lay(crown * ss(y, 1.70, 1.74) * band(x - s_ * 0.016, 0.0042, aa), AMBER, h=0.35, rough=0.5)
            C.lay(crown * ss(y, 1.70, 1.74) * band(x - s_ * 0.016, 0.0052, aa) * 0.0, INK)
    elif ck == 'chevron':           # nested forward-pointing Vs over the crown
        for k_ in range(4):
            dch = np.abs(z * 1.0 + 0.9 * np.abs(x) - (0.045 - 0.020 * k_)) / np.sqrt(1.81)
            C.lay(crown * ss(y, 1.70, 1.74) * band(dch, 0.0024, aa), AMBER_D, h=0.30, rough=0.5)
    C.lay(is_head * cover(np.abs(x) - 0.0011, aa) * cover(-z, aa), INK, h=-0.3, rough=0.9)       # dorsal seam
    if S['brow'] != 'none':
        for s_ in (-1.0, 1.0):                                                                          # brow flashes (front projection)
            cx, cy = s_ * 0.036, 1.716
            ang = np.radians(22.0)
            u = (x - cx) * s_; v = (y - cy)
            ca, sa_ = np.cos(ang), np.sin(ang)
            along = u * ca + v * sa_; perp = -u * sa_ + v * ca
            if S['brow'] == 'flash':
                halfw = 0.0030 * np.clip(1 - np.abs(along) / 0.017, 0, 1) + 0.0004
                fl = cover(np.abs(perp) - halfw, aa) * cover(np.abs(along) - 0.017, aa)
            else:   # tick: a short bar above the outer corner of each eye
                fl = cover(np.maximum(np.abs(along - 0.004) - 0.010, np.abs(perp) - 0.0022), aa)
            C.lay(is_head * front * fl, AMBER, h=0.45, rough=0.45)
    # jaw vents under the lens line
    if S['vent'] == 'hex':          # honeycomb (INK hairlines on DEEP)
        cell = hex_cell_edge(x, y, 0.0062)
        ell = np.sqrt((x / 0.040) ** 2 + ((y - 1.606) / 0.021) ** 2)
        vent_zone = is_head * front * cover(ell - 1.0, aa / 0.02)
        C.lay(vent_zone * 0.85 * cover(cell - 0.0009, aa) * 0 + vent_zone * cover(0.0011 - cell, aa), AMBER_D, h=0.3, rough=0.5)
        C.lay(vent_zone * cover(cell - 0.0011, aa) * 0.0, INK)
    elif S['vent'] == 'slots':      # three horizontal slots
        ell = np.sqrt((x / 0.040) ** 2 + ((y - 1.606) / 0.021) ** 2)
        vent_zone = is_head * front * cover(ell - 1.0, aa / 0.02)
        for yc_ in (1.596, 1.606, 1.616):
            C.lay(vent_zone * band(y - yc_, 0.0017, aa), AMBER_D, h=0.3, rough=0.5)
    C.lay(neck_ok * ss(head, 0.05, 0.15) * band(y - 1.4765, 0.0013, aa), AMBER, h=0.4, rough=0.45)                                   # collar piping

    # ------------------------------------------------------------------ fabric mottling and occlusion in the grooves
    mott = 0.035 * noise3(P, 22.0, 1) + 0.02 * noise3(P, 140.0, 2)
    C.col = np.clip(C.col * (1 + S['mott'] * mott[..., None]), 0, 1)
    C.ao = np.clip(C.ao - 0.25 * np.clip(-C.h, 0, 1), 0, 1)
    return dict(col=C.col, h=C.h, rough=C.rough, ao=C.ao)
