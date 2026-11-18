import json, os
M = json.load(open('model.json'))
os.makedirs('out', exist_ok=True)
mats, prims = M['mats'], M['prims']

# ---------- SketchUp Ruby ----------
rb = []
rb.append('''# encoding: UTF-8
# BLM lobby model (reception + lounge + bench niche)
# How to run: SketchUp > Extensions > Developer > Ruby Console, then:
#   load "/full/path/to/BLM_Lobby.rb"
# Units: mm. Each object is a named group on a tag (Structure, Partitions, Glazing,
# Stair, Doors, Aluminium, Service, Zones, Reception, Lounge, Ceiling, and one tag per electrical category: Electrical lamp / socket / switch / out / fan / panel). Hide tag "Ceiling" to look inside.
# Room names are text labels on tag "Rooms", zone labels on tag "Zone labels": double-click a label to rename it.
require 'sketchup.rb'
module BlmLobby
  MATS = {''')
for n, c in mats.items():
    rb.append("    '%s' => [%d, %d, %d, %s]," % (n, c[0], c[1], c[2], c[3]))
rb.append('  }\n  PRIMS = [')
for p in prims:
    faces = '[' + ','.join('[' + ','.join('[%d,%d,%d]' % tuple(v) for v in f) + ']' for f in p['faces']) + ']'
    rb.append("    ['%s','%s','%s',%s]," % (p['name'], p['tag'], p['mat'], faces))
rb.append('  ]\n  TEXTS = [')
for t in M['texts']:
    rb.append("    ['%s', %d, %d, %d, %d, '%s']," % (t['text'], t['x'], t['y'], t['z'], t['h'], t.get('f', 'w')))
rb.append('  ]\n  ROOMS = [')
for r in M['rooms']:
    rb.append("    ['%s', %d, %d, '%s']," % (r['name'], r['x'], r['y'], 'Rooms' if r.get('kind') == 'room' else 'Zone labels'))
rb.append('''  ]

  def self.build
    model = Sketchup.active_model
    model.start_operation('BLM Lobby', true)
    mats = {}
    MATS.each do |name, c|
      m = model.materials[name] || model.materials.add(name)
      m.color = Sketchup::Color.new(c[0], c[1], c[2])
      m.alpha = c[3]
      mats[name] = m
    end
    root = model.active_entities.add_group
    root.name = 'BLM Lobby'
    PRIMS.each do |name, tag, mat, faces|
      layer = model.layers[tag] || model.layers.add(tag)
      g = root.entities.add_group
      g.name = name
      g.layer = layer
      faces.each do |pts|
        begin
          f = g.entities.add_face(pts.map { |p| Geom::Point3d.new(p[0].mm, p[1].mm, p[2].mm) })
          if f
            f.material = mats[mat]
            f.back_material = mats[mat]
          end
        rescue StandardError
        end
      end
    end
    # 3D lettering: face 's' = on a south-facing surface, otherwise on a west-facing one
    TEXTS.each do |text, x, y, z, h, face|
      begin
        g = root.entities.add_group
        g.name = 'Text ' + text
        g.layer = model.layers['Decor'] || model.layers.add('Decor')
        g.entities.add_3d_text(text, TextAlignLeft, 'Arial', true, false, h.mm, 0.0, 0.0, true, 15.mm)
        g.material = mats['steel']
        if face == 's'
          xa, za = Geom::Vector3d.new(1, 0, 0), Geom::Vector3d.new(0, -1, 0)
        else
          xa, za = Geom::Vector3d.new(0, -1, 0), Geom::Vector3d.new(-1, 0, 0)
        end
        g.transformation = Geom::Transformation.axes(Geom::Point3d.new(x.mm, y.mm, z.mm), xa, Geom::Vector3d.new(0, 0, 1), za)
      rescue StandardError
      end
    end
    ROOMS.each do |name, x, y, tag|
      begin
        t = root.entities.add_text(name, Geom::Point3d.new(x.mm, y.mm, 100.mm))
        t.layer = model.layers[tag] || model.layers.add(tag)
      rescue StandardError
      end
    end
    model.commit_operation
    model.active_view.zoom_extents
    root
  end
end
BlmLobby.build
''')
open('out/BLM_Lobby.rb', 'w', encoding='utf-8').write('\n'.join(rb))

# ---------- COLLADA ----------
def tris_by_mat():
    out = {}
    for p in prims:
        pos, nor = out.setdefault(p['mat'], ([], []))
        for f in p['faces']:
            a, b, c = f[0], f[1], f[2]
            u = [b[i] - a[i] for i in range(3)]; v = [c[i] - a[i] for i in range(3)]
            n = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
            l = (n[0]**2 + n[1]**2 + n[2]**2) ** .5 or 1
            n = [x / l for x in n]
            for i in range(1, len(f) - 1):
                for v_ in (f[0], f[i], f[i + 1]):
                    pos.extend(v_); nor.extend(n)
    return out
T = tris_by_mat()
d = ['<?xml version="1.0" encoding="utf-8"?>',
     '<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">',
     '<asset><unit name="millimeter" meter="0.001"/><up_axis>Z_UP</up_axis></asset>', '<library_effects>']
for n, c in mats.items():
    tr = '' if c[3] >= 1 else '<transparent opaque="A_ONE"><color>1 1 1 1</color></transparent><transparency><float>%s</float></transparency>' % c[3]
    d.append('<effect id="fx_%s"><profile_COMMON><technique sid="common"><lambert><diffuse><color>%.3f %.3f %.3f 1</color></diffuse>%s</lambert></technique></profile_COMMON></effect>' % (n, c[0]/255, c[1]/255, c[2]/255, tr))
d.append('</library_effects><library_materials>')
for n in mats:
    d.append('<material id="m_%s" name="%s"><instance_effect url="#fx_%s"/></material>' % (n, n, n))
d.append('</library_materials><library_geometries>')
for n, (pos, nor) in T.items():
    nv = len(pos) // 3
    d.append('<geometry id="g_%s" name="%s"><mesh>' % (n, n))
    d.append('<source id="g_%s_p"><float_array id="g_%s_pa" count="%d">%s</float_array><technique_common><accessor source="#g_%s_pa" count="%d" stride="3"><param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/></accessor></technique_common></source>' % (n, n, len(pos), ' '.join(str(x) for x in pos), n, nv))
    d.append('<source id="g_%s_n"><float_array id="g_%s_na" count="%d">%s</float_array><technique_common><accessor source="#g_%s_na" count="%d" stride="3"><param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/></accessor></technique_common></source>' % (n, n, len(nor), ' '.join('%.3f' % x for x in nor), n, nv))
    d.append('<vertices id="g_%s_v"><input semantic="POSITION" source="#g_%s_p"/></vertices>' % (n, n))
    d.append('<triangles material="mat" count="%d"><input semantic="VERTEX" source="#g_%s_v" offset="0"/><input semantic="NORMAL" source="#g_%s_n" offset="0"/><p>%s</p></triangles>' % (nv // 3, n, n, ' '.join(str(i) for i in range(nv))))
    d.append('</mesh></geometry>')
d.append('</library_geometries><library_visual_scenes><visual_scene id="scene" name="BLM Lobby">')
for n in T:
    d.append('<node id="n_%s" name="%s"><instance_geometry url="#g_%s"><bind_material><technique_common><instance_material symbol="mat" target="#m_%s"/></technique_common></bind_material></instance_geometry></node>' % (n, n, n, n))
d.append('</visual_scene></library_visual_scenes><scene><instance_visual_scene url="#scene"/></scene></COLLADA>')
open('out/BLM_Lobby.dae', 'w').write('\n'.join(d))

# ---------- viewer ----------
html = open('viewer_template.html').read().replace('/*MODEL*/null', json.dumps(M, separators=(',', ':'), ensure_ascii=False))
open('out/index.html', 'w', encoding='utf-8').write(html)
import xml.dom.minidom; xml.dom.minidom.parse('out/BLM_Lobby.dae')
print({f: os.path.getsize('out/' + f) for f in os.listdir('out')})
