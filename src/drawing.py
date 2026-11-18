"""2D plans for the designer from model.json: DXF per floor (mm, 1:1, layers) and one PDF (A3, 1:50, a sheet per floor)."""
import json, math
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.backends.backend_pdf import PdfPages
M = json.load(open('model.json')); F2 = M.get('f2', 3150); V = M['version']
LAY1 = {'Structure': 'A-WALL', 'Partitions': 'A-WALL', 'Doors': 'A-DOOR', 'Glazing': 'A-GLAZ', 'Aluminium': 'A-GLAZ',
        'Stair': 'A-STAIR', 'Reception': 'A-FURN', 'Service': 'A-FURN', 'Site': 'A-SITE'}
LAY2 = {'F2 Structure': 'A-WALL', 'F2 Partitions': 'A-WALL', 'F2 Glazing': 'A-GLAZ', 'F2 Spa': 'A-FURN', 'Stair': 'A-STAIR'}
def footprint(p):
    vs = [v for f in p['faces'] for v in f]; zmax = max(v[2] for v in vs)
    for f in p['faces']:
        if all(abs(v[2] - zmax) < 1 for v in f) and len(f) >= 3: return [(v[0], v[1]) for v in f]
    xs = [v[0] for v in vs]; ys = [v[1] for v in vs]
    return [(min(xs), min(ys)), (max(xs), min(ys)), (max(xs), max(ys)), (min(xs), max(ys))]
def collect(floor):
    lay_map, base = (LAY1, 0) if floor == 1 else (LAY2, F2)
    cut = base + 1200; items = []
    for p in M['prims']:
        if p['tag'] not in lay_map: continue
        zs = [v[2] for f in p['faces'] for v in f]; z0, z1 = min(zs), max(zs); lay = lay_map[p['tag']]
        if lay == 'A-WALL':
            if z1 <= base + 5: continue
            if not (z0 < cut < z1): lay = 'A-OVERHEAD' if z0 >= cut else 'A-SILL'
        if p['tag'] == 'Site' and 'Barrier' not in p['name']: continue
        if lay == 'A-FURN' and p['name'].startswith('Curtain'): lay = 'A-CURTAIN'
        items.append((lay, footprint(p)))
    return items
def dims(floor): return [d for d in M['dims'] if d.get('f', 1) == floor and abs(d['a'][2] - d['b'][2]) < 1]
def rooms(floor): return [r for r in M['rooms'] if r.get('f', 1) == floor]
TITLE = {1: 'floor 1, lobby', 2: 'floor 2, spa'}
NOTE = 'Units: mm. Plan after the 1:50 drawing; heights assumed. Verify all dimensions on site.'

def dxf(floor, fn):
    out = ['0', 'SECTION', '2', 'ENTITIES']
    def line(l, a, b): out.extend(['0', 'LINE', '8', l, '10', '%.1f' % a[0], '20', '%.1f' % a[1], '30', '0', '11', '%.1f' % b[0], '21', '%.1f' % b[1], '31', '0'])
    def text(l, x, y, h, s, ang=0): out.extend(['0', 'TEXT', '8', l, '10', '%.1f' % x, '20', '%.1f' % y, '30', '0', '40', '%d' % h, '1', s, '50', '%.1f' % ang])
    for lay, poly in collect(floor):
        for i in range(len(poly)): line(lay, poly[i], poly[(i + 1) % len(poly)])
    for d in dims(floor):
        a, b = d['a'], d['b']; line('A-DIMS', a, b)
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy); tx, ty = -dy / L * 100, dx / L * 100
        for p in (a, b): line('A-DIMS', (p[0] - tx, p[1] - ty), (p[0] + tx, p[1] + ty))
        ang = 90 if abs(dx) < 1 else 0
        text('A-DIMS', (a[0] + b[0]) / 2 + (-140 if ang else -200), (a[1] + b[1]) / 2 + (-200 if ang else 60), 110, d['t'], ang)
    for r in rooms(floor):
        text('A-ROOM-NAME' if r['kind'] == 'room' else 'A-ZONE-NAME', r['x'] - 40 * len(r['name']), r['y'], 130, r['name'])
    if floor == 1:
        EL = {'lamp': 'E-LIGHT', 'socket': 'E-SOCKET', 'switch': 'E-SWITCH', 'out': 'E-OUTLET', 'fan': 'E-FAN', 'panel': 'E-PANEL'}
        for e in M['elec']: out.extend(['0', 'CIRCLE', '8', EL[e['t']], '10', '%.1f' % e['x'], '20', '%.1f' % e['y'], '30', '0', '40', '60.0'])
    text('A-NOTE', 0, -1700, 150, 'BLM Lobby, block A1, %s - version %s. %s' % (TITLE[floor], V, NOTE))
    out += ['0', 'ENDSEC', '0', 'EOF']; open(fn, 'w').write('\n'.join(out) + '\n')

STYLE = {'A-WALL': dict(fc='#3a3a3a', ec='k', lw=.5, z=5), 'A-SILL': dict(fc='#c9c9c9', ec='k', lw=.3, z=3),
         'A-OVERHEAD': dict(fc='none', ec='#888', lw=.3, ls=(0, (4, 3)), z=6), 'A-DOOR': dict(fc='#9ec3d6', ec='k', lw=.4, z=7),
         'A-GLAZ': dict(fc='#9ec3d6', ec='k', lw=.3, z=7), 'A-STAIR': dict(fc='none', ec='#555', lw=.4, z=2),
         'A-FURN': dict(fc='#efe7da', ec='#6b5a48', lw=.4, z=4), 'A-CURTAIN': dict(fc='none', ec='#b06a2c', lw=.8, ls=(0, (2, 1.5)), z=8),
         'A-SITE': dict(fc='#e06a5f', ec='k', lw=.3, z=2)}
def sheet(floor):
    W, Hh = 420, 297
    fig = plt.figure(figsize=(W / 25.4, Hh / 25.4)); mx0, my0, mw, mh = 15, 30, 390, 255
    ax = fig.add_axes([mx0 / W, my0 / Hh, mw / W, mh / Hh]); x0, y0 = -2600, -4200
    ax.set_xlim(x0, x0 + mw * 50); ax.set_ylim(y0, y0 + mh * 50); ax.set_aspect('equal'); ax.axis('off')
    for lay, poly in collect(floor):
        st = STYLE[lay]; ax.add_patch(Polygon(poly, closed=True, fc=st['fc'], ec=st['ec'], lw=st['lw'], ls=st.get('ls', '-'), zorder=st['z']))
    for d in dims(floor):
        a, b = d['a'], d['b']; dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy); tx, ty = -dy / L * 90, dx / L * 90
        ax.plot([a[0], b[0]], [a[1], b[1]], color='#c0392b', lw=.5, zorder=9)
        for p in (a, b): ax.plot([p[0] - tx, p[0] + tx], [p[1] - ty, p[1] + ty], color='#c0392b', lw=.5, zorder=9)
        vert = abs(dx) < 1
        ax.text((a[0] + b[0]) / 2 - (70 if vert else 0), (a[1] + b[1]) / 2 + (0 if vert else 60), d['t'], color='#c0392b', fontsize=5.5,
                rotation=90 if vert else 0, ha='right' if vert else 'center', va='center' if vert else 'bottom', zorder=10, bbox=dict(fc='white', ec='none', pad=.4, alpha=.8))
    for r in rooms(floor):
        room = r['kind'] == 'room'
        ax.text(r['x'], r['y'], r['name'].upper() if room else r['name'], fontsize=6.2 if room else 4.8, ha='center', va='center', zorder=11,
                fontweight='bold' if room else 'normal', color='k' if room else '#44607a', bbox=dict(fc='white', ec='none', pad=.5, alpha=.75))
    fig.text(15 / W, 20 / Hh, 'BLM LOBBY - block A1, %s' % TITLE[floor], fontsize=13, fontweight='bold')
    fig.text(15 / W, 13 / Hh, 'Version %s  |  Scale 1:50 on A3  |  Dimensions in mm  |  Plan after the 1:50 electrical drawing (2023-10-27); heights assumed; verify on site' % V, fontsize=7.5)
    fig.text(15 / W, 7 / Hh, 'Dark fill = walls cut at 1.2 m   |   dashed grey = lintels overhead   |   blue = glass   |   beige = furniture and equipment   |   dashed orange = curtains   |   red = dimensions', fontsize=6.5, color='#444')
    sb = fig.add_axes([300 / W, 9 / Hh, 100 / W, 6 / Hh]); sb.set_xlim(0, 5000); sb.set_ylim(0, 1); sb.axis('off')
    for i in range(5): sb.add_patch(plt.Rectangle((i * 1000, .25), 1000, .5, fc='k' if i % 2 == 0 else 'w', ec='k', lw=.5))
    for i in range(6): fig.text((300 + i * 20) / W, 17 / Hh, '%d m' % i, fontsize=6, ha='center')
    return fig
if __name__ == '__main__':
    dxf(1, 'out/BLM_Lobby_plan_F1.dxf'); dxf(2, 'out/BLM_Lobby_plan_F2.dxf')
    with PdfPages('out/BLM_Lobby_plans_A3_1-50.pdf') as pdf:
        for fl in (1, 2):
            fig = sheet(fl); pdf.savefig(fig)
            if fl == 2: fig.savefig('plan_check2.png', dpi=110)
            plt.close(fig)
    print('drawings ok')
