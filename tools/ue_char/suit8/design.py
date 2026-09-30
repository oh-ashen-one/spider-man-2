# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""ORIGINAL hero suit design, round 08 ("Tessera" suit).  Procedural, evaluated per texel in rest-pose object space (x = character's left,
y up, z forward, metres), so there is no hand-drawn source art and nothing is copied from any existing suit.

Design language (written up in docs/night1/characters/round-08/SUIT_ORIGINALITY.md):
  * palette: slate TEAL body, DEEP ink-teal panels, AMBER accents, BONE hairline piping.  No red / blue blocking, no white emblem.
  * asymmetric cross-balance: the character's RIGHT arm and LEFT leg carry the amber "light" side, the other pair the dark side.
  * a tilted amber bandolier sash (a plane slice of the torso, front and back differ) instead of a symmetric chest graphic.
  * joint plates: a sphere-cut DEEP plate with an amber ring at both shoulders, elbows and knees (the vocabulary of the suit).
  * net: a triangular "tessera" net made of three families of plane slices through the body (no radial / orb web, no spider figure);
    hairline on the TEAL panels, strong on the amber sleeve; honeycomb vents on the jaw.
  * chest badge: a broken hexagon ring with three kite vanes (a net junction), on the sternum; a plain ring on the back.
  * the mask: DEEP hood, TEAL crown cap with an amber piping arc, two amber brow flashes, honeycomb jaw vents; original lens shape (hero_lens_r8.py).
"""
import numpy as np

SQ3 = 1.7320508075688772


def srgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255.0


TEAL = srgb('#1f6273')
TEAL_D = srgb('#174e5d')
DEEP = srgb('#0c2a33')
INK = srgb('#050d11')
AMBER = srgb('#ee9f1c')
AMBER_D = srgb('#c47d10')
BONE = srgb('#e6dfc9')
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


# ------------------------------------------------------------------------------------------------ the suit
class Canvas:
    """Layered texel canvas: colour, height (mm), roughness, occlusion."""
    def __init__(self, shape):
        self.col = np.tile(TEAL, shape + (1,)).astype(np.float32)
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


def paint(P, N, G, mpt, gi, jp):
    """P, N (r, n, 3) float32 rest-pose positions / normals; G (r, n, 9) group weights; mpt (r, n) metres per texel (AA footprint);
    gi = {group name: index}; jp = {joint name: (x, y, z)}.  Returns dict(col (r, n, 3) sRGB 0..1, h mm, rough, ao)."""
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    ax = np.abs(x)
    aa = np.maximum(mpt, 6e-5).astype(np.float32) * 1.2
    g = lambda k: G[..., gi[k]]
    sharp = lambda w: ss(w, 0.42, 0.58)
    head = g('head'); torso = g('torso'); shoulder = g('shoulder'); armU = sharp(g('armU')); armF = sharp(g('armF')); hand = sharp(g('hand'))
    thigh = sharp(g('thigh')); shin = sharp(g('shin')); foot = sharp(g('foot'))
    nx, ny, nz = N[..., 0], N[..., 1], N[..., 2]
    C = Canvas(x.shape)
    is_head = cover(1.480 - y, aa) * ss(head, 0.25, 0.40)            # hood: straight plane cut at the neck (the skin-weight ramp is soft and uneven)
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
    xb = 0.088 + 0.10 * ss(y, 1.06, 1.33)
    m_side = tors_w * body_w * cover(xb - ax, aa) * ss(y, 1.00, 1.04)
    C.lay(m_side, DEEP, rough=0.80)
    # 2. waist belt band + trunks (DEEP) above a diagonal hip-wrap cut across the thighs
    belt_d = np.abs(y - 1.055) - 0.024
    C.lay(body_w * tors_w * cover(belt_d, aa), DEEP, rough=0.80)
    cut_d = (y - (0.80 + 0.62 * x)) / np.sqrt(1 + 0.62 ** 2)            # > 0 above the diagonal
    m_trunk = body_w * trunk_w * cover(np.maximum(y - 1.03, -cut_d), aa)
    C.lay(m_trunk, DEEP, rough=0.80)
    # back spine stripe (under the sash)
    back = ss(-nz, 0.15, 0.55)
    m_spine = back * tors_w * body_w * cover(np.abs(x) - 0.013, aa) * cover(y - 1.44, aa) * cover(1.085 - y, aa) * cover(y - 1.335, aa)
    C.lay(m_spine, DEEP, rough=0.8)
    # 3. bandolier sash: a tilted plane slice of the torso (front and back differ)
    n_s = unit((0.36, 0.88, 0.30))
    d_s = pdot(n_s, (0.0, 1.27, 0.0))
    zone_s = tors_w * body_w * ss(y, 1.045, 1.09) * (1 - ss(y, 1.44, 1.47)) * cover(ax - 0.160, aa)
    C.lay(zone_s * band(d_s, 0.035, aa), DEEP, rough=0.8)
    C.lay(zone_s * band(d_s, 0.031, aa), AMBER, h=0.25, rough=0.50)
    # 5. arms.  Right arm = the amber "light" side, left arm = teal / dark side
    Rb = (x < 0)
    E_R, W_R = J('forearm.R'), J('hand.R'); E_L, W_L = J('forearm.L'), J('hand.L')
    def arm_t(E, W): d = W - E; return pdot(d / np.linalg.norm(d), E) / float(np.linalg.norm(d))
    t_fore = np.where(Rb, arm_t(E_R, W_R), arm_t(E_L, W_L))
    arm_tot = np.maximum(armU + shoulder_arm + armF + hand, 1e-3)
    C.lay(arm_w * R_ * ss(ax, 0.17, 0.22), DEEP, rough=0.80)                      # right upper arm + shoulder: DEEP
    C.lay(arm_w * R_ * (armF / arm_tot) * ss(t_fore, -0.02, 0.02), AMBER, rough=0.55)   # right forearm sleeve: amber
    for tc in (0.66, 0.76, 0.86):                                                  # left forearm: three amber wrist bands (cord wraps)
        C.lay(arm_w * L_ * armF * band(t_fore - tc, 0.0034, aa), AMBER, h=0.40, rough=0.5)
    C.lay(hand * body_w, DEEP, rough=0.68)                                         # gloves
    # 6. legs.  Left leg = amber side accents, right leg = dark side
    y_top = 0.40 + 0.5 * z
    m_greaveR = shin * R_ * cover(y - y_top, aa) * cover(0.10 - y, aa)             # right shin: amber greave, slanted top edge
    C.lay(m_greaveR, AMBER, rough=0.52)
    C.lay(thigh * L_ * cover(0.0 - cut_d * 0 - (y - 0.0), aa) * 0 + thigh * L_ * ss(y, 0.52, 0.56), DEEP, rough=0.80)
    lat = np.abs(z - 0.0) - 0.011                                                   # outer seam stripe
    m_stripe = leg_w * np.clip(thigh + shin * ss(y, 0.42, 0.50), 0, 1) * cover(lat, aa) * ss(-sgn * nx, 0.4, 0.8)
    C.lay(m_stripe * R_ * (1 - m_greaveR), AMBER, h=0.35, rough=0.5)
    C.lay(m_stripe * L_, TEAL, h=0.35, rough=0.7)
    for yc in (0.175, 0.205):                                                       # left shin ankle bands
        C.lay(shin * L_ * band(y - yc, 0.0040, aa), AMBER, h=0.4, rough=0.5)
    m_boot = foot * body_w                                                          # boots: DEEP upper, INK toe cap, sole, amber welt
    C.lay(m_boot, DEEP, rough=0.72)
    C.lay(m_boot * ss(z, 0.085, 0.092), INK, rough=0.6)
    C.lay(foot * cover(y - 0.022, aa), SOLE, h=0.0, rough=0.88)
    C.lay(foot * band(y - 0.0265, 0.0015, aa), AMBER, h=0.3, rough=0.5)

    # ------------------------------------------------------------------ joint sleeves: DEEP slabs between planes perpendicular to the limb axis + amber rings
    # (plane slices, not sphere cuts: a plane slice of the faceted mesh is a clean curve, a sphere cut zig-zags +-1.5 mm on the low-poly shoulder)
    plate_m = np.zeros(x.shape, np.float32)
    def sleeve(A, B, s0, s1, zone):
        nonlocal plate_m
        s_, _ = seg_coords(P, J(A), J(B))
        inside = cover(np.abs(s_ - 0.5 * (s0 + s1)) - 0.5 * (s1 - s0), aa)
        C.lay(inside * zone, DEEP, h=0.35, rough=0.60, ao=0.85)
        for sb in (s0 - 0.0035, s1 + 0.0035):
            C.lay(band(s_ - sb, 0.0017, aa) * zone, AMBER, h=0.55, rough=0.45)
        plate_m = np.maximum(plate_m, inside * zone)
    for side_, nm in ((1.0, 'L'), (-1.0, 'R')):
        sidew = (sgn == side_).astype(np.float32)
        A_, B_ = J('deltoid.' + nm), J('forearm.' + nm)
        d_ = (B_ - A_) / np.linalg.norm(B_ - A_)
        rel_ = P - A_; s_a = rel_ @ d_; rr = np.linalg.norm(rel_ - s_a[..., None] * d_, axis=-1)
        z_sh = sidew * body_w * (1 - is_head) * cover(rr - 0.108, aa) * cover(1.30 - y, aa * 0 + aa) * 0 + sidew * body_w * (1 - is_head) * cover(rr - 0.108, aa)
        sleeve('deltoid.' + nm, 'forearm.' + nm, -0.050, 0.075, z_sh)
        C.lay(band(rr - 0.108, 0.0010, aa) * sidew * body_w * (1 - is_head) * cover(np.abs(s_a - 0.0125) - 0.0625, aa), INK, h=-0.3, rough=0.9)
        z_el = sidew * body_w * np.clip(armU + armF, 0, 1)
        sleeve('deltoid.' + nm, 'forearm.' + nm, 0.262, 0.322, z_el)
        z_kn = sidew * body_w * np.clip(thigh + shin, 0, 1)
        sleeve('thigh.' + nm, 'shin.' + nm, 0.405, 0.470, z_kn)

    # ------------------------------------------------------------------ diamond net (helix families wound around each body segment)
    def segnet(name_a, name_b, R, cell, phase=0.0):
        return helix_dist(P, J(name_a), J(name_b), R, cell, phase=phase)
    netw_a = 0.0015      # half width of an amber net line
    netw_d = 0.0011      # half width of a dark hairline
    jt = lambda n: J(n)
    nd_armU_R, nn_armU_R = helix_dist(P, J('deltoid.R'), J('forearm.R'), 0.050, 0.052, nodes=True); nd_armU_L = segnet('deltoid.L', 'forearm.L', 0.050, 0.052)
    nd_armF_R = segnet('forearm.R', 'hand.R', 0.040, 0.046); nd_armF_L = segnet('forearm.L', 'hand.L', 0.040, 0.046)
    tor_a, tor_b = np.array([0, 0.95, -0.012], np.float32), np.array([0, 1.52, -0.012], np.float32)
    nd_tor = helix_dist(P, tor_a, tor_b, 0.14, 0.056)
    nd_thR = segnet('thigh.R', 'shin.R', 0.078, 0.062); nd_thL, nn_thL = helix_dist(P, J('thigh.L'), J('shin.L'), 0.078, 0.062, nodes=True)
    nd_shR = segnet('shin.R', 'foot.R', 0.052, 0.050); nd_shL = segnet('shin.L', 'foot.L', 0.052, 0.050)
    z_up = tors_w * body_w * ss(y, 1.30, 1.38) * (1 - m_side)
    # amber net on the DEEP right upper arm; DEEP hairline net on the amber right forearm
    zR = arm_w * R_ * (armU + shoulder_arm) * ss(ax, 0.17, 0.22) * (1 - plate_m)
    C.lay(cover(nd_armU_R - netw_a, aa) * zR, AMBER, h=0.30, rough=0.5)
    C.lay(cover(nn_armU_R - 0.0032, aa) * zR, AMBER, h=0.55, rough=0.42)
    sF_R, thF_R = seg_coords(P, J('forearm.R'), J('hand.R'))
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
    zL = thigh * L_ * ss(y, 0.56, 0.60) * (1 - plate_m) * ss(0.78 - y, -0.03, 0.03)
    C.lay(cover(nd_thL - netw_a * 0.9, aa) * zL, AMBER_D, h=0.25, rough=0.55)
    C.lay(cover(nn_thL - 0.0034, aa) * zL, AMBER, h=0.55, rough=0.42)
    sS_R, thS_R = seg_coords(P, J('shin.R'), J('foot.R'))
    C.lay(cover(np.abs((thS_R - 0.0 + np.pi) % (2 * np.pi) - np.pi) * 0.045 - 0.0035, aa) * m_greaveR * (1 - plate_m), DEEP, h=-0.30, rough=0.8)   # shin-front DEEP stripe

    # ------------------------------------------------------------------ chest badge (front) and back ring
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
    ring, vanes, core = badge(0.0, 1.372, 0.046)
    f_ = front * tors_w * body_w
    C.lay(f_ * ring, AMBER, h=0.45, rough=0.40)
    C.lay(f_ * np.maximum(vanes, core), AMBER, h=0.40, rough=0.40)
    ring_b, _, core_b = badge(0.0, 1.395, 0.042)
    b_ = back * tors_w * body_w
    C.lay(b_ * ring_b, AMBER, h=0.45, rough=0.40)
    C.lay(b_ * core_b, AMBER, h=0.40, rough=0.40)
    # belt buckle: hex plate
    bk = hex_d(x, y - 1.055, 0.021, pointy=False)
    C.lay(front * tors_w * body_w * cover(bk, aa), AMBER, h=0.5, rough=0.4)
    C.lay(front * tors_w * body_w * cover(hex_d(x, y - 1.055, 0.011, pointy=False), aa), DEEP, h=0.2, rough=0.6)

    # ------------------------------------------------------------------ piping (amber hairlines) along the main cuts
    pip = 0.0014
    C.lay(body_w * tors_w * band(y - 1.0795, pip, aa), AMBER, h=0.45, rough=0.45)
    C.lay(body_w * tors_w * band(y - 1.0305, pip, aa), AMBER, h=0.45, rough=0.45)
    C.lay(body_w * np.clip(tors_w + thigh, 0, 1) * band(cut_d, pip * 1.3, aa) * ss(1.03 - y, -0.002, 0.004), AMBER, h=0.45, rough=0.45)
    C.lay(m_side * band(xb - ax, pip, aa) * ss(y, 1.06, 1.12), AMBER_D, h=0.35, rough=0.5)

    # ------------------------------------------------------------------ mask / hood
    yb = 1.662 + 0.46 * z
    crown = is_head * cover(yb - y, aa)                         # above the boundary
    C.lay(is_head, DEEP, rough=0.80)
    C.lay(crown, TEAL_D, rough=0.74)
    C.lay(is_head * band(y - yb, 0.0018, aa), AMBER, h=0.5, rough=0.45)
    # crown honeycomb (hairline, projected from above)
    hc = hex_cell_edge(x, z, 0.014)
    C.lay(crown * ss(y, 1.72, 1.76) * cover(0.0009 - hc, aa) * 0.9 + 0.0 * crown, DEEP, h=-0.25, rough=0.85)
    C.lay(is_head * cover(np.abs(x) - 0.0011, aa) * cover(-z, aa), INK, h=-0.3, rough=0.9)       # dorsal seam
    for s_ in (-1.0, 1.0):                                                                          # brow flashes (front projection)
        cx, cy = s_ * 0.036, 1.716
        ang = np.radians(22.0)
        u = (x - cx) * s_; v = (y - cy)
        ca, sa = np.cos(ang), np.sin(ang)
        along = u * ca + v * sa; perp = -u * sa + v * ca
        halfw = 0.0030 * np.clip(1 - np.abs(along) / 0.017, 0, 1) + 0.0004
        fl = cover(np.abs(perp) - halfw, aa) * cover(np.abs(along) - 0.017, aa)
        C.lay(is_head * front * fl, AMBER, h=0.45, rough=0.45)
    # jaw vents: honeycomb (INK hairlines on DEEP) under the lens line
    cell = hex_cell_edge(x, y, 0.0062)
    ell = np.sqrt((x / 0.040) ** 2 + ((y - 1.606) / 0.021) ** 2)
    vent_zone = is_head * front * cover(ell - 1.0, aa / 0.02)
    C.lay(vent_zone * 0.85 * cover(cell - 0.0009, aa) * 0 + vent_zone * cover(0.0011 - cell, aa), AMBER_D, h=0.3, rough=0.5)
    C.lay(vent_zone * cover(cell - 0.0011, aa) * 0.0, INK)
    C.lay(ss(head, 0.25, 0.40) * band(y - 1.4765, 0.0013, aa), AMBER, h=0.4, rough=0.45)                                   # collar piping

    # ------------------------------------------------------------------ fabric mottling and occlusion in the grooves
    mott = 0.035 * noise3(P, 22.0, 1) + 0.02 * noise3(P, 140.0, 2)
    C.col = np.clip(C.col * (1 + mott[..., None]), 0, 1)
    C.ao = np.clip(C.ao - 0.25 * np.clip(-C.h, 0, 1), 0, 1)
    return dict(col=C.col, h=C.h, rough=C.rough, ao=C.ao)
