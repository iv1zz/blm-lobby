"""BLM block A1, 1st floor — geometry from the 1:50 drawing (electrical project, 2023-10-27).
Units: mm. X, Y as in the lobby concept plan (stair along the far wall). Origin = inner SW corner, finished floor = 0.
Heights (3000 clear, stair rise, doors, windows) are assumptions: the plan gives no vertical dimensions."""
import json, math

S = 9.33  # mm per plan pixel (corridor 150 px = 1400 mm)
def X(px): return int(round((px - 75) * S / 10) * 10)
def Y(py): return int(round((712 - py) * S / 10) * 10)
H = 3000

MATS = {  # name: (r,g,b,alpha)
    'floor': (228, 226, 221, 1), 'wall': (216, 208, 198, 1), 'wall_dark': (212, 204, 194, 1), 'wall_grey': (198, 190, 180, 1),
    'accent': (30, 72, 190, 1), 'ceil': (36, 84, 170, 1), 'metal': (128, 131, 135, 1), 'terrazzo': (178, 178, 176, 1), 'white': (242, 242, 240, 1), 'chair': (196, 188, 176, 1),
    'steel': (28, 28, 30, 1), 'slab': (242, 242, 240, 1), 'concrete': (118, 120, 122, 1),
    'wood': (150, 106, 72, 1), 'wood_dark': (78, 60, 46, 1), 'marble': (205, 205, 208, 1),
    'stone': (86, 86, 90, 1), 'fabric': (224, 224, 222, 1), 'door': (62, 62, 64, 1),
    'glass': (170, 200, 215, 0.3), 'green': (62, 122, 60, 1), 'pot': (208, 203, 194, 1),
    'alu': (44, 45, 48, 1), 'rug': (62, 56, 48, 1),
    'z_arrive': (150, 185, 225, 1), 'z_recep': (232, 200, 150, 1), 'z_wait': (165, 210, 170, 1), 'z_lug': (240, 215, 130, 1),
    'z_office': (200, 185, 225, 1), 'z_staff': (170, 215, 215, 1), 'screen': (20, 30, 45, 1), 'asphalt': (70, 72, 76, 1), 'line': (235, 235, 230, 1), 'barrier': (215, 40, 40, 1), 'board': (238, 236, 228, 1),
    'el_lamp': (245, 205, 40, 1), 'el_socket': (235, 120, 30, 1), 'el_switch': (40, 110, 220, 1),
    'el_out': (200, 50, 160, 1), 'el_fan': (30, 160, 160, 1), 'el_panel': (190, 30, 30, 1), 'gravel': (186, 183, 173, 1), 'art': (242, 242, 240, 1),
}
prims = []

def add(name, tag, mat, faces):
    prims.append({'name': name, 'tag': tag, 'mat': mat,
                  'faces': [[[int(round(c)) for c in p] for p in f] for f in faces]})

def box(name, tag, mat, x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    a, b, c, d = (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)
    e, f, g, h = (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)
    add(name, tag, mat, [[a, d, c, b], [e, f, g, h], [a, b, f, e], [b, c, g, f], [c, d, h, g], [d, a, e, h]])

def pbox(name, tag, mat, px0, px1, py0, py1, z0, z1):
    box(name, tag, mat, X(px0), X(px1), Y(py0), Y(py1), z0, z1)

def cyl(name, tag, mat, cx, cy, r0, r1, z0, z1, n=16):
    ring = lambda r, z: [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z) for i in range(n)]
    b, t = ring(r0, z0), ring(r1, z1)
    faces = [list(reversed(b)), t] + [[b[i], b[(i + 1) % n], t[(i + 1) % n], t[i]] for i in range(n)]
    add(name, tag, mat, faces)

def prism(name, tag, mat, axis, poly, a0, a1):
    """poly: 2D convex polygon; axis 'y' -> poly in (x,z); axis 'x' -> poly in (y,z)."""
    P = {'y': lambda u, v, a: (u, a, v), 'x': lambda u, v, a: (a, u, v), 'z': lambda u, v, a: (u, v, a)}[axis]
    A = [P(u, v, a0) for u, v in poly]; B = [P(u, v, a1) for u, v in poly]
    n = len(poly)
    add(name, tag, mat, [A, list(reversed(B))] + [[A[i], B[i], B[(i + 1) % n], A[(i + 1) % n]] for i in range(n)])


def wall(name, mat, x0, x1, y0, y1, tag='Partitions'):
    box(name, tag, mat, x0, x1, y0, y1, 0, H)

def door_x(name, x0, x1, y0, y1, head=2100):
    """door in a wall running along X: opening x0..x1, wall thickness y0..y1"""
    box(name + ' lintel', 'Partitions', 'wall', x0, x1, y0, y1, head, H)
    leaf(name, 'x', (y0 + y1) / 2, x0, x1, head, 'Doors', 'hi')   # glazed aluminium leaf

def door_y(name, x0, x1, y0, y1, head=2100):
    box(name + ' lintel', 'Partitions', 'wall', x0, x1, y0, y1, head, H)
    leaf(name, 'y', (x0 + x1) / 2, y0, y1, head, 'Doors', 'hi')   # glazed aluminium leaf

def rbox(name, tag, mat, px_, py_, ang, u0, u1, t, z0, z1):
    """box rotated in plan: pivot (px_,py_), runs u0..u1 along direction turned `ang` deg from +Y towards -X."""
    a = math.radians(ang); d = (-math.sin(a), math.cos(a)); n = (math.cos(a), math.sin(a))
    P = lambda u, w: (px_ + u * d[0] + w * n[0], py_ + u * d[1] + w * n[1])
    prism(name, tag, mat, 'z', [P(u0, -t / 2), P(u1, -t / 2), P(u1, t / 2), P(u0, t / 2)], z0, z1)

def glazed(name, axis, c, a0, a1, z0, z1, posts, tag='Glazing', mat='steel', t=60):
    """glazing strip: axis 'x' = runs along X at y=c, axis 'y' = runs along Y at x=c; posts = mullion positions"""
    B = (lambda u0, u1, w, zz0, zz1, m, n: box(n, tag, m, u0, u1, c - w, c + w, zz0, zz1)) if axis == 'x' else \
        (lambda u0, u1, w, zz0, zz1, m, n: box(n, tag, m, c - w, c + w, u0, u1, zz0, zz1))
    for p in posts: B(p - 25, p + 25, t, z0, z1, mat, name + ' mullion')
    B(a0, a1, t, z0, z0 + 60, mat, name + ' rail'); B(a0, a1, t, z1 - 60, z1, mat, name + ' rail')
    B(a0, a1, 5, z0 + 60, z1 - 60, 'glass', name + ' glass')

def leaf(name, axis, c, a0, a1, zt, tag, handle_at):
    """closed glazed aluminium door leaf"""
    B = (lambda u0, u1, w, z0, z1, m: box(name, tag, m, u0, u1, c - w, c + w, z0, z1)) if axis == 'x' else \
        (lambda u0, u1, w, z0, z1, m: box(name, tag, m, c - w, c + w, u0, u1, z0, z1))
    B(a0, a0 + 60, 22, 0, zt, 'alu'); B(a1 - 60, a1, 22, 0, zt, 'alu')
    B(a0 + 60, a1 - 60, 22, 0, 90, 'alu'); B(a0 + 60, a1 - 60, 22, zt - 80, zt, 'alu'); B(a0 + 60, a1 - 60, 5, 90, zt - 80, 'glass')
    h = a1 - 45 if handle_at == 'hi' else a0 + 15
    B(h, h + 30, 55, 800, 1400, 'steel')

# ---------------- Envelope (from the drawing) ----------------
XW, XE, YS, YN = -320, 12560, -320, 5790          # outer faces
XI, YI = 12390, 5490                               # inner faces (east glazing line, north wall)
box('Floor slab', 'Structure', 'floor', XW, XE, YS, YN, -150, 0)
box('North wall', 'Structure', 'wall_dark', XW, XE, YI, YN, 0, H)
box('West wall', 'Structure', 'wall_dark', XW, 0, YS, YI, 0, H)
box('South wall W', 'Structure', 'wall_dark', 0, 2570, YS, 0, 0, H)
box('South wall head', 'Structure', 'wall_dark', 2570, 4375, YS, 0, 2600, H)   # linen window: from the floor, same head height as the entrance
box('South wall pier', 'Structure', 'wall_dark', 4375, 5450, YS, 0, 0, H)
box('Entrance lintel', 'Structure', 'wall_dark', 5450, 7815, YS, 0, 2600, H)
box('South wall E', 'Structure', 'wall_dark', 7815, XE, YS, 0, 0, H)
box('East wall corner', 'Structure', 'wall_dark', XI, XE, YS, 0, 0, H)
glazed('Window', 'x', -160, 2570, 4375, 0, 2600, [2595, 3215, 4350])
glazed('Entrance sidelight', 'x', -160, 5450, 6110, 0, 2600, [5475, 6085])
glazed('Entrance sidelight', 'x', -160, 7060, 7815, 0, 2600, [7085, 7790])
box('Entrance door transom', 'Glazing', 'steel', 6110, 7060, -220, -100, 2400, 2600)
leaf('Entrance door', 'x', -160, 6110, 7060, 2400, 'Glazing', 'hi')
xe = (XI + XE) / 2
glazed('East facade', 'y', xe, 0, 3695, 0, H, [25, 730, 1880, 2770, 3670])
glazed('East window', 'y', xe, 4795, YI, 0, H, [4820, 5465])
box('East door transom', 'Glazing', 'steel', xe - 60, xe + 60, 3695, 4795, 2400, H)
leaf('East door', 'y', xe, 3695, 4795, 2400, 'Glazing', 'lo')

# ---------------- Existing partitions (from the drawing) ----------------
wall('Wall room 1 / corridor', 'wall', 0, 2335, 3830, 3990)
door_x('Door room 1', 2335, 3236, 3830, 3990)
wall('Wall WC south', 'wall', 3236, 3590, 3830, 3990)
door_x('Door WC', 3590, 4485, 3830, 3990)
wall('Wall WC south', 'wall', 4485, 4800, 3830, 3990)
wall('Wall room 1 / WC', 'wall', 3285, 3440, 3990, YI)
wall('Wall WC east', 'wall', 4640, 4800, 3990, YI)
wall('Corridor end stub', 'wall', 1926, 2076, 3430, 3830)
door_y('Door corridor end', 1926, 2076, 2530, 3430)
wall('Corridor end stub', 'wall', 1926, 2076, 2300, 2530)
wall('Wall corridor / room 3', 'wall', 2076, 5385, 2300, 2460)
wall('Wall room 3 / lobby', 'wall', 4730, 4880, 0, 2300)   # solid wall (confirmed on site; the drawing shows a glazed symbol)
wall('Security west wall', 'wall', 9530, 9690, 0, 2810)   # existing solid wall, kept as is: no door, no window to the lobby
wall('Security north wall', 'wall', 9690, 10490, 2650, 2810)
door_x('Door security', 10490, 11390, 2650, 2810)
wall('Security north wall', 'wall', 11390, XI, 2650, 2810)

# ---------------- Stair (plan from the drawing: 14 goings of 240, width 1090) ----------------
x0, yS, yN = 5990, 4400, YI
RISE, GO, NT = 200, 240, 14
for i in range(1, NT + 1):
    xa = x0 + (i - 1) * GO
    box('Tread %d' % i, 'Stair', 'steel', xa, xa + 260, yS, yN, i * RISE - 12, i * RISE)   # steel plate treads as built
xt = x0 + NT * GO
top = lambda x: 160 + (x - x0 - 120) * RISE / GO
poly = [(x0 - 72, 0), (x0 + 192, 0), (xt, top(xt) - 220), (xt, top(xt))]
prism('Stringer', 'Stair', 'steel', 'y', poly, yS + 60, yS + 110)
prism('Stringer', 'Stair', 'steel', 'y', poly, yN - 110, yN - 60)

# ---------------- New: stair wall, pivot door, storage under the stair ----------------
wall('Stair wall (existing, grey plaster)', 'wall_grey', 5990, 9495, 4290, 4390)
box('Stair door lintel', 'Partitions', 'wall', 4800, 5990, 4290, 4390, 2450, H)
yd = 4340; ja, jb = 4800, 5990
box('Pivot door jamb', 'Aluminium', 'alu', ja, ja + 40, yd - 50, yd + 50, 0, 2450)
box('Pivot door jamb', 'Aluminium', 'alu', jb - 40, jb, yd - 50, yd + 50, 0, 2450)
box('Pivot door head', 'Aluminium', 'alu', ja, jb, yd - 50, yd + 50, 2400, 2450)
LW = jb - ja - 80 - 10; PIV = 250; ANG = -90 - 22
px_ = ja + 45 + PIV
for u0, u1, z0, z1, m, t in [(-PIV, -PIV + 60, 0, 2390, 'alu', 45), (LW - PIV - 60, LW - PIV, 0, 2390, 'alu', 45),
                              (-PIV + 60, LW - PIV - 60, 0, 90, 'alu', 45), (-PIV + 60, LW - PIV - 60, 2310, 2390, 'alu', 45),
                              (-PIV + 60, LW - PIV - 60, 90, 2310, 'glass', 10)]:
    rbox('Pivot door leaf', 'Aluminium', m, px_, yd, ANG, u0, u1, t, z0, z1)
_a = math.radians(ANG)
rbox('Pivot door handle', 'Aluminium', 'steel', px_ + 45 * math.cos(_a), yd + 45 * math.sin(_a), ANG, LW - PIV - 45, LW - PIV - 15, 30, 800, 1400)
wall('Under-stair wall (new)', 'wall', 9395, 9495, 4390, 4550)
door_y('Storage door', 9395, 9495, 4550, 5350)
wall('Under-stair wall (new)', 'wall', 9395, 9495, 5350, YI)

# ---------------- New: aluminium glazed partition closing the lounge ----------------
xp = 9610; p0, p1 = 2810, 4290; DW = 900
for yy in (p0 + 25, p0 + 50 + DW + 25, p1 - 25):
    box('Lounge partition post', 'Aluminium', 'alu', xp - 40, xp + 40, yy - 25, yy + 25, 0, H)
box('Lounge partition head rail', 'Aluminium', 'alu', xp - 40, xp + 40, p0, p1, H - 50, H)
box('Lounge partition transom', 'Aluminium', 'alu', xp - 40, xp + 40, p0, p1, 2400, 2450)
box('Lounge partition bottom rail', 'Aluminium', 'alu', xp - 40, xp + 40, p0 + 100 + DW, p1, 0, 50)
box('Lounge partition glass', 'Aluminium', 'glass', xp - 5, xp + 5, p0 + 100 + DW, p1 - 50, 50, 2400)
box('Lounge partition glass top', 'Aluminium', 'glass', xp - 5, xp + 5, p0 + 50, p1 - 50, 2450, H - 50)
leaf('Lounge partition door', 'y', xp, p0 + 50, p0 + 50 + DW, 2400, 'Aluminium', 'hi')

# ---------------- Ceiling (separate tag) ----------------
for a, b, c, d in [(XW, 5990, YS, YN), (9395, XE, YS, YN), (5990, 9395, YS, 4390)]:
    box('Ceiling slab', 'Ceiling', 'slab', a, b, c, d, H, H + 150)
for bx, y1 in ((2070, YI), (5070, YI), (8070, 4290), (9670, YI)):
    box('Beam', 'Ceiling', 'steel', bx - 75, bx + 75, 0, y1, H - 250, H)

for a, b, c, d in [(0, XI, 0, 4290), (0, 5990, 4290, YI), (9395, XI, 4290, YI)]:
    box('Ceiling finish', 'Ceiling', 'ceil', a, b, c, d, H - 12, H - 2)

# ---------------- Reception: opposite the entrance door (X 6110-7060), facing the parking; back to the stair wall ----------------
dx0, dx1, dS, dN = 6100, 8300, 2740, 3390
DXL = 7600                                   # east 700 mm of the desk is a lower wood counter
box('Desk body', 'Reception', 'metal', dx0, DXL, dS, dN, 0, 1080)
box('Desk top edge', 'Reception', 'steel', dx0 - 20, DXL, dS - 40, dN, 1080, 1100)
prism('Desk wood front', 'Reception', 'wood', 'y', [(dx0 + 700, 0), (DXL, 0), (DXL, 1000)], dS - 20, dS)   # wood triangle on the brushed metal front
box('Desk low counter', 'Reception', 'wood', DXL, dx1, dS - 250, dN, 0, 760)
box('Desk low counter top', 'Reception', 'wood', DXL - 150, dx1 + 60, dS - 310, dN, 760, 800)
box('Desk worktop', 'Reception', 'wood_dark', dx0 + 150, DXL - 100, dN, dN + 350, 700, 740)
# back wall on the existing stair wall: terrazzo panel with a TV, wood slats on both sides
box('Terrazzo feature wall', 'Reception', 'terrazzo', 6550, 8250, 4230, 4290, 0, H - 250)
box('TV', 'Reception', 'screen', 6950, 7850, 4195, 4230, 1350, 1900)
for xs in list(range(6010, 6540, 60)) + list(range(8260, 9470, 60)):
    box('Wood slat', 'Reception', 'wood', xs, xs + 35, 4250, 4290, 0, H - 250)

# ================= v4: functional fit-out (reception, management, security, check-in, luggage, valuables) =================
SV = 'Service'
# --- luggage trolley parked by the entrance door for guard 2 (greets guests, carries luggage)
box('Luggage trolley deck', SV, 'steel', 7150, 7750, 150, 1050, 180, 220)
for xx, yy in ((7170, 170), (7700, 170), (7170, 1000), (7700, 1000)):
    cyl('Luggage trolley wheel', SV, 'steel', xx + 15, yy + 15, 60, 60, 0, 180, 8)
for yy in (170, 1000):
    box('Luggage trolley post', SV, 'el_lamp', 7710, 7740, yy, yy + 30, 220, 1750)
box('Luggage trolley rail', SV, 'el_lamp', 7710, 7740, 170, 1030, 1720, 1750)
# --- reception desk seats: guard 2 at the west end next to the stair door (entrance to the 2nd floor), receptionist at the east end
for xx in (6350, 7000):
    box('Desk chair seat', SV, 'accent', xx, xx + 500, 3520, 4000, 420, 500)
    box('Desk chair back', SV, 'accent', xx, xx + 500, 3950, 4000, 500, 950)
# --- tall black cabinet for keys and parcels, left of the terrazzo panel (as on the renders)
box('Cabinet (keys, parcels)', SV, 'steel', 6000, 6500, 3960, 4250, 0, 2100)
# --- site map of the 30 townhouses, first thing seen on the left of the door
box('Site map frame', SV, 'steel', 9515, 9530, 2000, 2760, 980, 2120)      # on the security wall next to the sofa and the luggage door
box('Site map board', SV, 'board', 9505, 9515, 2040, 2720, 1020, 2080)
# --- guest waiting zone in the freed corner by the solid security wall: sofa + bar counter with charging stations
def armchair(x0, y0, face):
    """existing grey tub armchair 750 x 750; face = side the sitter looks to: 'w' or 'n'"""
    box('Armchair seat', SV, 'chair', x0, x0 + 750, y0, y0 + 750, 0, 420)
    if face == 'w':
        box('Armchair back', SV, 'chair', x0 + 570, x0 + 750, y0, y0 + 750, 420, 760)
        box('Armchair arm', SV, 'chair', x0, x0 + 570, y0, y0 + 130, 420, 620); box('Armchair arm', SV, 'chair', x0, x0 + 570, y0 + 620, y0 + 750, 420, 620)
    else:
        box('Armchair back', SV, 'chair', x0, x0 + 750, y0, y0 + 180, 420, 760)
        box('Armchair arm', SV, 'chair', x0, x0 + 130, y0 + 180, y0 + 750, 420, 620); box('Armchair arm', SV, 'chair', x0 + 620, x0 + 750, y0 + 180, y0 + 750, 420, 620)
# straight 3-seat sofa on the security wall; its north end stops at 2150 so the passage to the luggage room stays free
SY0, SY1 = 250, 2150
box('Sofa base', SV, 'accent', 8680, 9530, SY0, SY1, 0, 420)
box('Sofa back', SV, 'accent', 9330, 9530, SY0, SY1, 420, 800)
box('Sofa arm', SV, 'accent', 8680, 9330, SY0, SY0 + 170, 420, 620); box('Sofa arm', SV, 'accent', 8680, 9330, SY1 - 170, SY1, 420, 620)
for yy in (SY0 + 190, SY0 + 700, SY0 + 1210):
    box('Sofa cushion', SV, 'accent', 8700, 9320, yy, yy + 500, 420, 500)
box('Sofa pillow', SV, 'fabric', 9150, 9330, SY1 - 620, SY1 - 220, 500, 800)
box('Coffee table white', SV, 'white', 7830, 8300, 500, 1300, 0, 400)
box('Coffee table wood', SV, 'wood', 7830, 8300, 1300, 1900, 0, 260)
for yy in (520, 980, 1440):                                  # three pictures above the sofa
    box('Picture', SV, 'board', 9512, 9530, yy, yy + 400, 1350, 2150)
for zz in (1450, 1800):                                      # two sconces on the existing wall-light outputs
    cyl('Sconce', SV, 'el_lamp', 9500, 330, 70, 70, zz, zz + 40, 10)
# niche of the Warehouse Linen wall (500 deep, measured): blue pill panels, two white armchairs, a side table
NX = 4880
for k, yy in enumerate(range(70, 2250, 275)):
    for z0, z1 in ([(120, 1300), (1400, 2700)] if k % 2 == 0 else [(120, 700), (800, 1950), (2050, 2700)]):
        box('Pill panel', SV, 'accent', NX, NX + 30, yy, yy + 235, z0, z1)
for yy in (330, 1230):
    box('Armchair seat', SV, 'white', NX + 60, NX + 760, yy, yy + 700, 250, 430)
    box('Armchair back', SV, 'white', NX + 60, NX + 200, yy, yy + 700, 430, 800)
    for ay in (yy, yy + 620):
        box('Armchair arm', SV, 'white', NX + 200, NX + 760, ay, ay + 80, 430, 600)
    for lx, ly in ((NX + 80, yy + 20), (NX + 720, yy + 20), (NX + 80, yy + 660), (NX + 720, yy + 660)):
        box('Armchair leg', SV, 'steel', lx, lx + 20, ly, ly + 20, 0, 250)
cyl('Side table', SV, 'wood_dark', NX + 350, 2060, 190, 190, 0, 620, 14)
# --- luggage room: racks (3 tiers) on the north wall and by the east glazing
def rack(name, x0, x1, y0, y1):
    for z in (150, 900, 1650):
        box(name + ' shelf', SV, 'wood', x0, x1, y0, y1, z, z + 30)
    for xx in (x0, x1 - 40):
        for yy in (y0, y1 - 40):
            box(name + ' post', SV, 'steel', xx, xx + 40, yy, yy + 40, 0, 1950)
rack('Luggage rack N', 10400, 12300, 4940, 5440)
rack('Luggage rack E', 11850, 12350, 2850, 3600)
# --- valuables: 30 safe-deposit boxes in the tall end of the cupboard under the stairs
box('Safe deposit cabinet', SV, 'steel', 8500, 9350, 5090, 5490, 0, 1800)
for i in range(1, 6):
    box('Safe deposit grid', SV, 'concrete', 8500 + i * 141, 8500 + i * 141 + 6, 5084, 5090, 60, 1740)
for z in (360, 660, 960, 1260, 1560):
    box('Safe deposit grid', SV, 'concrete', 8500, 9350, 5084, 5090, z, z + 6)
# --- security room = CCTV post of guard 1: cameras and radio only, never leaves the post without relief, room is never empty.
#     Desk in the SE corner (monitors, barrier visible through the corner glazing), camera above the guard, server cabinet by the existing sockets.
box('Guard 1 desk', SV, 'wood', 11600, 12300, 150, 1700, 720, 750)
box('Guard 1 desk legs', SV, 'steel', 11620, 12280, 170, 210, 0, 720); box('Guard 1 desk legs', SV, 'steel', 11620, 12280, 1640, 1680, 0, 720)
for zz in (800, 1200):                                   # two monitors stacked, clear of the service hatch
    box('CCTV monitor', SV, 'screen', 12230, 12270, 900, 1420, zz, zz + 350)
# service hatch to the guard in the 1st glazing bay, before the barrier, so drivers talk to him before the arm
HY0, HY1, HZ0, HZ1 = 80, 680, 1000, 1800
_xe = (XI + XE) / 2
for a, b_, c, d in ((HY0, HY1, HZ0, HZ0 + 45), (HY0, HY1, HZ1 - 45, HZ1), (HY0, HY0 + 45, HZ0, HZ1), (HY1 - 45, HY1, HZ0, HZ1)):
    box('Service hatch frame', 'Aluminium', 'alu', _xe - 45, _xe + 45, a, b_, c, d)
box('Service hatch shelf', 'Aluminium', 'wood', _xe - 220, _xe + 220, HY0, HY1, HZ0 - 40, HZ0)
rbox('Service hatch sash (open)', 'Aluminium', 'glass', _xe + 45, HY1 - 45, 215, 0, HY1 - HY0 - 90, 12, HZ0 + 45, HZ1 - 45)   # hinged on the barrier side, opens towards arriving cars
box('Radio base station', SV, 'steel', 11700, 11900, 1450, 1650, 750, 900)
box('Guard 1 chair seat', SV, 'fabric', 10950, 11450, 650, 1150, 420, 500)
box('Guard 1 chair back', SV, 'fabric', 10950, 11000, 650, 1150, 500, 950)
box('Camera over guard 1', SV, 'el_panel', 10500, 10620, 840, 960, H - 130, H)
box('CCTV / server cabinet', SV, 'steel', 9720, 10120, 60, 460, 0, 1800)

# --- site context (assumed geometry): parking along the long wall with the door, barrier to the villas at the corner of the security room
box('Parking', 'Site', 'asphalt', XW - 600, XE + 5000, YS - 5500, YS, -150, -20)
for xs in range(0, 12501, 2500):
    box('Parking line', 'Site', 'line', xs - 50, xs + 50, YS - 5000, YS - 400, -20, -14)
box('Lane to villas', 'Site', 'asphalt', XE, XE + 5000, YS, YN + 1500, -150, -20)
BY = 730                                                   # barrier moved one glazing bay in, to the first mullion
box('Barrier housing', 'Site', 'barrier', XE + 250, XE + 600, BY - 175, BY + 175, -20, 1050)
for i in range(7):
    box('Barrier arm', 'Site', 'barrier' if i % 2 == 0 else 'line', XE + 600 + i * 500, XE + 1100 + i * 500, BY - 35, BY + 35, 850, 950)

# --- floor zones (thin coloured plates, tag Zones)
for nm, m, a, b, c, d in [
    ('Zone arrival', 'z_arrive', 6000, 7900, 0, 1300), ('Zone waiting', 'z_wait', 4880, 6000, 0, 2300), ('Zone reception', 'z_recep', 5990, 8450, 2600, 4290),
    ('Zone waiting', 'z_wait', 7900, 9530, 0, 2650),
    ('Zone luggage', 'z_lug', 9690, 12390, 2810, 5490), ('Zone valuables', 'z_lug', 5990, 9395, 4390, 5490),
    ('Zone CCTV post', 'z_office', 9690, 12390, 0, 2650),
    ('Zone staff', 'z_staff', 0, 3285, 3990, 5490), ('Zone staff', 'z_staff', 0, 1926, 0, 3830), ('Zone staff', 'z_staff', 1926, 4730, 0, 2300)]:
    box(nm, 'Zones', m, a, b, c, d, 2, 8)

# ---------------- Electrical points (positions from the power and lighting plans) ----------------
ELEC = []
def el(t, x, y, z):
    ELEC.append({'t': t, 'x': int(round(x)), 'y': int(round(y)), 'z': int(z)})
    m = 'el_' + t
    if t in ('lamp', 'fan'): cyl('El ' + t, 'Electrical ' + t, m, x, y, 70, 70, H - 40, H - 5, 12)
    else: box('El ' + t, 'Electrical ' + t, m, x - 50, x + 50, y - 50, y + 50, z - 50, z + 50)
E = json.load(open('dwg/elec.json'))
tick = lambda c: c['w'] < 100 and c['h'] < 100 and c['n'] <= 4
for c in E['lamps']: el('lamp', c['x'], c['y'], H)
for c in E['power']:
    if tick(c): continue
    x, y, w, h, n = c['x'], c['y'], c['w'], c['h'], c['n']
    if w > 450: el('panel', x - 130, y, 1500); el('panel', x + 130, y, 1500)
    elif 60 <= n <= 70 and max(w, h) < 260: el('out', x, y, 300)
    elif max(w, h) > 550: [el('socket', x + (d if w > h else 0), y + (0 if w > h else d), 300) for d in (-200, 0, 200)]
    elif max(w, h) > 350: [el('socket', x + (d if w > h else 0), y + (0 if w > h else d), 300) for d in (-100, 100)]
    else: el('socket', x, y, 300)
sw = [c for c in E['switch'] if not tick(c) and not (c['w'] < 100 and c['n'] <= 4)]
for c in sw:
    x, y, w, h, n = c['x'], c['y'], c['w'], c['h'], c['n']
    if n == 2 and 190 < w < 215 and 190 < h < 215: el('fan', x, y, H)
    elif 60 <= n <= 70: el('out', x, y, 1500)
    elif w > 220 and h < 130 and y > 5400: el('panel', x, y, 1500)
    else: el('switch', x, y, 1200 if n == 22 else 1000)


# ================= v5: 2nd floor, spa (all old partitions removed except the stair enclosure) =================
F = H + 150; H2 = 2700                      # 2nd floor level and assumed clear height
def b2(name, tag, mat, x0, x1, y0, y1, z0, z1): box(name, tag, mat, x0, x1, y0, y1, F + z0, F + z1)
FS, FP, FG, FF = 'F2 Structure', 'F2 Partitions', 'F2 Glazing', 'F2 Spa'
# --- envelope from the 2nd floor drawing (window heights assumed)
b2('F2 North wall', FS, 'wall_dark', XW, XE, YI, YN, 0, H2)
b2('F2 West wall', FS, 'wall_dark', XW, 0, YS, YI, 0, H2)
for a, b in ((0, 2580), (4370, 5480), (7800, XE)):
    b2('F2 South wall', FS, 'wall_dark', a, b, YS, 0, 0, H2)
for a, b, posts in ((2580, 4370, [2605, 4130, 4345]), (5480, 7800, [5505, 6195, 7775])):   # floor to ceiling; middle mullion on the cabin partition
    glazed('F2 Window', 'x', -160, a, b, F, F + H2, posts, tag=FG)
glazed('F2 East facade', 'y', xe, 0, YI, F, F + H2, [25, 1100, 2200, 3300, 4400, 5465], tag=FG)
# --- existing: stair enclosure (kept) and the shaft box at the north wall
b2('F2 Stair enclosure (existing)', FS, 'wall_grey', 5100, 5240, 4250, YI, 0, H2)
b2('F2 Stair enclosure (existing)', FS, 'wall_grey', 5240, 9500, 4250, 4390, 0, H2)
b2('F2 Shaft (per drawing)', FS, 'wall', 3180, 5100, 5050, YI, 0, H2)

T75 = 75
def door2(name, axis, c, a0, a1):
    """solid door leaf + lintel in a 75 mm partition; axis 'x' = wall along X at y=c"""
    if axis == 'x':
        b2(name + ' lintel', FP, 'wall', a0, a1, c - T75 / 2, c + T75 / 2, 2100, H2); b2(name, FP, 'door', a0, a1, c - 20, c + 20, 0, 2100)
    else:
        b2(name + ' lintel', FP, 'wall', c - T75 / 2, c + T75 / 2, a0, a1, 2100, H2); b2(name, FP, 'door', c - 20, c + 20, a0, a1, 0, 2100)
def wallx2(name, y, x0, x1, doors=()):
    cur = x0
    for a, b in sorted(doors):
        b2(name, FP, 'wall', cur, a, y - T75 / 2, y + T75 / 2, 0, H2); door2(name + ' door', 'x', y, a, b); cur = b
    b2(name, FP, 'wall', cur, x1, y - T75 / 2, y + T75 / 2, 0, H2)
def wally2(name, x, y0, y1):
    b2(name, FP, 'wall', x - T75 / 2, x + T75 / 2, y0, y1, 0, H2)
def table(name, x0, y0):
    b2(name, FF, 'board', x0, x0 + 700, y0, y0 + 1900, 620, 700); b2(name + ' base', FF, 'wood_dark', x0 + 100, x0 + 600, y0 + 250, y0 + 1650, 0, 620)

# --- south row: 6 massage cabins with doors, 2065 wide on axes (about 1990 clear) x 2100
NB = 6; BW = XI / NB; BD = 2100
for i in range(1, NB):
    wally2('Cabin divider', i * BW, 0, BD)
wallx2('Corridor wall S', BD + T75 / 2, 0, XI, doors=[(i * BW + 60, i * BW + 760) for i in range(NB)])
for i in range(NB):
    table('Massage table', i * BW + 800, 80)
    b2('Cabin shelf', FF, 'wood', (i + 1) * BW - 37 - 300, (i + 1) * BW - 37, BD - 500, BD, 0, 800)
# --- corridor about 1050 wide, then the north line
CN = 3262                                   # axis of the north corridor partition
wallx2('Corridor wall N', CN, 0, 5175, doors=[(1400, 2100), (2450, 3150 - 40), (3500, 4100), (4475, 5075)])
wally2('Room divider', 2212, CN, YI)                       # staff room | WC
wally2('Wet divider', 3187, CN, 5050)                      # WC | shower 1
wally2('Wet divider', 4162, CN, 5050)                      # shower 1 | shower 2
b2('Wet block east wall', FP, 'wall', 5100, 5175, CN - T75 / 2, 4250, 0, H2)
# staff / linen room (2175 x 2190): shelving and a work table
for z in (300, 900, 1500, 2000):
    b2('Linen shelf', FF, 'wood', 0, 450, 3400, 5400, z, z + 30)
b2('Staff table', FF, 'wood', 1300, 2100, 4700, 5400, 720, 750)
# WC and two showers sit above the 1st floor toilet and next to the shaft
b2('WC pan', FF, 'board', 2500, 2900, 4880, 5420, 0, 420); b2('WC basin', FF, 'board', 2260, 2560, 3950, 4350, 780, 850)
for sx0, sx1 in ((3225, 4125), (4200, 5100)):
    b2('Shower tray', FF, 'marble', sx0, sx1, 4150, 5050, 0, 60)
    b2('Shower screen', FF, 'glass', sx0 + 300, sx1, 4145, 4155, 60, 2000)
    b2('Changing bench', FF, 'wood', sx0, sx0 + 250, 3350, 4050, 0, 450)
# --- waiting zone at the stair exit, by the glazing: armchairs, table, tea console
def armchair2(x0, y0, face):
    b2('Armchair seat', FF, 'chair', x0, x0 + 750, y0, y0 + 750, 0, 420)
    if face == 's':     # back to the north wall
        b2('Armchair back', FF, 'chair', x0, x0 + 750, y0 + 570, y0 + 750, 420, 760)
        b2('Armchair arm', FF, 'chair', x0, x0 + 130, y0, y0 + 570, 420, 620); b2('Armchair arm', FF, 'chair', x0 + 620, x0 + 750, y0, y0 + 570, 420, 620)
    else:               # 'w': back to the east glazing
        b2('Armchair back', FF, 'chair', x0 + 570, x0 + 750, y0, y0 + 750, 420, 760)
        b2('Armchair arm', FF, 'chair', x0, x0 + 570, y0, y0 + 130, 420, 620); b2('Armchair arm', FF, 'chair', x0, x0 + 570, y0 + 620, y0 + 750, 420, 620)
armchair2(10250, 4720, 's'); armchair2(11050, 4720, 's')
armchair2(11620, 3780, 'w'); armchair2(11620, 2980, 'w')
cyl('Waiting table', FF, 'wood_dark', 10900, 4050, 300, 300, F + 380, F + 420, 16); cyl('Waiting table leg', FF, 'steel', 10900, 4050, 30, 30, F, F + 380, 8)
b2('Tea console', FF, 'wood', 11300, 12300, 2190, 2590, 0, 900)   # against the corridor wall, clear of the route from the stair
# --- along the stair enclosure: lockers and a bench for changing shoes
b2('Lockers', FF, 'wood_dark', 5400, 7600, 3830, 4250, 0, 1800)
for xx in range(5400 + 367, 7600, 367):
    b2('Locker joint', FF, 'steel', xx - 3, xx + 3, 3824, 3830, 40, 1760)
b2('Bench', FF, 'wood', 7800, 9300, 3800, 4250, 0, 450); b2('Bench cushion', FF, 'fabric', 7820, 9280, 3820, 4230, 450, 520)

ROOMS2 = [('m%d' % (i + 1), 'Massage %d' % (i + 1), i * BW + BW / 2, 1150) for i in range(NB)] + [
    ('staff', 'Staff / linen', 1090, 4400), ('wait2', 'Waiting', 10900, 3500), ('wc2', 'WC', 2700, 4500),
    ('sh1', 'Shower 1', 3675, 4500), ('sh2', 'Shower 2', 4650, 4500), ('spacor', 'Spa corridor', 5500, 2700),
    ('lock', 'Lockers', 6500, 3600), ('land', 'Stair landing', 9950, 4950), ('shaft', 'Shaft', 4140, 5270)]

TEXTS = [{'text': 'PALM', 'x': dx0 + 130, 'y': dS - 20, 'z': 770, 'h': 150, 'f': 's', 'c': '#f4f4f2'},
         {'text': 'STREET', 'x': dx0 + 130, 'y': dS - 20, 'z': 540, 'h': 150, 'f': 's', 'c': '#f4f4f2'}]  # f='s': on a south-facing surface, x = left edge
ROOMS = [('r1', 'Warehouse Chemical', 1500, 4750), ('r2', 'Toilet', 4040, 4750), ('r3', 'Warehouse Linen', 2600, 1150),
         ('cor', 'Corridor', 3300, 3150), ('lobby', 'Lobby', 7900, 1300), ('rec', 'Reception', 7800, 3700),
         ('sec', 'Security / Office 2', 10900, 2100), ('lounge', 'Luggage Room', 10950, 4150), ('stair', 'Stairs Entrance', 5400, 4900),
         ('store', 'The Cupboard Under the Stairs', 7300, 4950),
         ('post', 'Guard 2 (greeter, luggage)', 6500, 3700), ('g1', 'Guard 1 (CCTV, radio)', 11200, 600), ('trolley', 'Luggage trolley', 7450, 600), ('wait', 'Waiting / Taxi', 8400, 2300), ('charge', 'Armchairs', 5400, 1150), ('map', 'Site Map', 9250, 2380),
         ('safe', 'Safe Deposit', 8900, 5250), ('keys', 'Keys, parcels', 6250, 3800),
         ('barrier', 'Barrier to villas', 14300, 1150), ('hatch', 'Guard hatch', 13100, -250), ('parking', 'Parking', 6000, -2800)]
PALETTES = [
    {'name': 'Royal blue', 'mats': {}},
    {'name': 'Teal', 'mats': {'accent': (18, 118, 128), 'ceil': (22, 100, 110)}},
    {'name': 'Forest green', 'mats': {'accent': (34, 98, 70), 'ceil': (36, 84, 62)}},
    {'name': 'Terracotta', 'mats': {'accent': (184, 88, 54), 'ceil': (198, 118, 84)}},
    {'name': 'Graphite and mustard', 'mats': {'accent': (208, 162, 42), 'ceil': (54, 56, 60), 'wall': (206, 204, 200), 'wall_dark': (202, 200, 196)}},
    {'name': 'Sand, white ceiling', 'mats': {'accent': (156, 136, 110), 'ceil': (244, 242, 236)}},
]
ROOM_IDS = {'r1', 'r2', 'r3', 'cor', 'lobby', 'rec', 'sec', 'lounge', 'stair', 'store'}   # the rest are zone / function labels
ROOMS = [{'id': i, 'name': n, 'x': x, 'y': y, 'z': 60, 'f': 1, 'kind': 'room' if i in ROOM_IDS else 'zone'} for i, n, x, y in ROOMS]
ROOMS += [{'id': i, 'name': n, 'x': int(x), 'y': int(y), 'z': F + 60, 'f': 2, 'kind': 'room'} for i, n, x, y in ROOMS2]
DIM = {'x': 4300, 'y0': 2460, 'y1': 3830}
SIZE = {'L': XE - XW, 'W': YN - YS, 'H': H}
# dimension lines for the viewer and the drawing: (x0, y0, x1, y1, note)
_D = [(XW, -900, XE, -900, ''), (-900, YS, -900, YN, ''),                        # overall, outer faces
      (4880, 2250, 9530, 2250, ''), (5700, 0, 5700, 4290, ''),                   # lobby clear width / depth
      (4300, 2460, 4300, 3830, ''),                                              # corridor
      (6110, 180, 7060, 180, 'door'), (6585, 300, 6585, 2650, ''),               # entrance door, door to reception counter
      (8350, 3050, 9530, 3050, ''),                                              # passage desk end - security wall
      (4800, 4150, 5990, 4150, 'door'),                                          # stair entrance opening
      (6250, 4400, 6250, 5490, ''), (5990, 5300, 9350, 5300, '14 x 240'),        # stair width / run
      (9690, 4700, 12390, 4700, ''), (12000, 2810, 12000, 5490, ''),             # luggage room
      (9690, 2350, 12390, 2350, ''), (10600, 0, 10600, 2650, ''),                # security room
      (0, 300, 4730, 300, ''), (900, 0, 900, 3830, ''),                          # warehouse linen
      (0, 5250, 3285, 5250, ''), (300, 3990, 300, 5490, ''),                     # warehouse chemical
      (3440, 5250, 4640, 5250, ''),                                              # toilet
      (4880, 2050, 5380, 2050, 'recess')]                                       # recess of the linen wall
DIMS = [{'f': 1, 'a': [x0, y0, 40], 'b': [x1, y1, 40], 't': ('%d' % round(math.hypot(x1 - x0, y1 - y0))) + ((' ' + n) if n else '')} for x0, y0, x1, y1, n in _D]
DIMS.append({'f': 1, 'a': [XW - 300, YS - 300, 0], 'b': [XW - 300, YS - 300, H], 't': '%d height, assumed' % H})
_D2 = [(37, 300, BW - 37, 300, 'cabin'), (300, 0, 300, BD, ''), (4000, BD + 75, 4000, CN - 37, 'corridor'), (0, 5250, 2175, 5250, ''),
       (300, CN + 37, 300, YI, ''), (2250, 3700, 3150, 3700, ''), (3225, 3700, 4125, 3700, ''), (4200, 3700, 5100, 3700, ''),
       (9500, 5250, XI, 5250, 'waiting'), (12100, BD + 75, 12100, YI, ''), (8600, BD + 75, 8600, 4250, ''), (XW, -900, XE, -900, ''), (-900, YS, -900, YN, '')]
DIMS += [{'f': 2, 'a': [x0, y0, F + 40], 'b': [x1, y1, F + 40], 't': ('%d' % round(math.hypot(x1 - x0, y1 - y0))) + ((' ' + n) if n else '')} for x0, y0, x1, y1, n in _D2]

if __name__ == '__main__':
    import collections
    json.dump({'mats': MATS, 'prims': prims, 'texts': TEXTS, 'rooms': ROOMS, 'elec': ELEC, 'dim': DIM, 'dims': DIMS, 'size': SIZE, 'palettes': PALETTES, 'version': 'v6', 'f2': F}, open('model.json', 'w'), separators=(',', ':'), ensure_ascii=False)
    print(len(prims), 'prims', SIZE, collections.Counter(e['t'] for e in ELEC))
