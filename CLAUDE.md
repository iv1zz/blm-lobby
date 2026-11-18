# BLM Lobby — instructions for Claude

You are continuing a shared 3D model of a small two-storey building (block A1): a lobby with reception and security on floor 1 and a spa on floor 2. Several people work on it from their own Claude chats. This file is the common ground: read it before changing anything.

Reply to people in the language they write in. The site itself is in English.

## What is where

| Path | What it is |
|---|---|
| `index.html` | The live site, always the current version. Served at https://iv1zz.github.io/blm-lobby/ |
| `v6/` | Current version: viewer copy, SketchUp files (`.rb`, `.dae`), plans (PDF A3 1:50, DXF per floor) |
| `v5/`, `v4/`, `v3/` | Frozen versions. Never edit them |
| `src/model.py` | The model. All geometry, labels, dimensions and the version number live here |
| `src/viewer_template.html` | The web viewer (three.js r128 from cdnjs, own orbit controls) |
| `src/export.py` | Writes the viewer page, the SketchUp Ruby script and the COLLADA file |
| `src/drawing.py` | Writes the 2D plans: DXF per floor and a two-sheet PDF |
| `src/dwg/elec.json` | Electrical points of floor 1, extracted from the 1:50 electrical drawing |
| `src/smoke.js` | Smoke test of the viewer logic with stub DOM and stub three.js |
| `src/render_check.py` | Rough perspective render to PNG for checking geometry by eye |
| `src/build.sh` | Rebuilds everything and places it in the site root and the version folder |

## How to make a change

1. Edit `src/model.py` (geometry, labels, dimensions) or `src/viewer_template.html` (interface).
2. Run `bash src/build.sh`. It builds, runs the smoke test, copies the results and fails if the forbidden name is present.
3. Check the geometry: render a view with `render_check.py` or read the plan PNG that `drawing.py` writes, and look at it. You cannot see the real page in a browser from a cloud session, so say so in your reply instead of claiming it works.
4. Commit and push to `main`. GitHub Pages redeploys in a minute or two.
5. Tell the person what changed, what you assumed, and what they still have to decide.

Pull before you start (`git pull --ff-only`): someone else may have pushed.

## Model conventions

- Units are millimetres. X runs along the long side of the building, Y across it, Z up.
- Origin is the inner south-west corner of floor 1 at finished floor level. The long wall with the entrance door and the parking is at Y = 0. The glazed end wall with the barrier is at the high-X end.
- Inner size is about 12390 × 5490. Outer faces are `XW, XE, YS, YN`; inner faces are `XI, YI`.
- Floor 2 starts at `F = H + 150`. Use the `b2(...)` helper, which adds `F` to the heights.
- Every object is a named primitive with a tag and a material: `box`, `cyl`, `prism`, plus helpers such as `wall`, `door_x`, `door_y`, `glazed`, `leaf`, `rbox`.
- Tags become SketchUp tags and viewer layers. Floor 1: `Structure`, `Partitions`, `Doors`, `Glazing`, `Aluminium`, `Stair`, `Reception`, `Service`, `Zones`, `Site`, `Ceiling`, `Electrical <type>`. Floor 2 tags start with `F2`.
- Labels are in `ROOMS` (floor 1) and `ROOMS2` (floor 2). A label is a room name or a zone label; the viewer shows them with two mutually exclusive buttons.
- Dimension lines are in `_D` (floor 1) and `_D2` (floor 2).
- Labels of kind `stock` (list `STOCK`) mark where materials already on site are used; the viewer shows them with the button Stock materials, exclusive with room names and zones.
- Colour palettes for the viewer slider are in `PALETTES`: each one overrides material colours by name. The first palette is the base design; the SketchUp and DAE exports always use the base colours. Use the materials `accent` and `ceil` for anything that should follow the palette.
- Plan dimensions come from a 1:50 drawing and from site measurements. Do not move existing walls unless the person gives a measurement or says the wall is different on site.

## Rules set by the project owner

- **Function first.** Judge every change by how people will work in the room: passages, door swings, access to rooms, sight lines, where power is. If a request breaks one of these, say so before or while you make it.
- **Change carefully.** Do what was asked and nothing more. Do not redesign neighbouring areas on your own initiative.
- **Versions.** A new version is started only when the admin says so directly. Frozen versions are never changed. The working version is edited in place while it is being discussed.
- **New openings in existing walls** (doors, windows, hatches) go into the model only after the person confirms them.
- **The developer's brand name must not appear** anywhere on the site or in this repository. The name used here is BLM. The build script checks this.
- **The interface is in English.** By default the viewer shows room names and, from the electrical layer, only lights.
- **State your assumptions.** Anything you did not get from the drawing, a photo or a measurement must be called assumed in your reply.

## Assumed values, not yet measured

- The steel beams (size and positions); floor 2 clear height 2700. Floor 1 clear height is 2700, given by the owner.
- Stair rise: 15 equal risers from floor to floor, about 190 (the going of 240 and the width are from the drawing).
- Entrance door and window head heights on both floors; mullion positions of the floor 2 windows.
- The route of the drive at the barrier and everything else outdoors.
- Heights of the electrical points (positions in plan are from the drawing).
- That the shaft box on floor 2 holds plumbing risers.

## State of version 6

Version 6 follows the interior designer's renders and SketchUp layout. Versions 3 to 5 are frozen.

Floor 1, lobby for a complex of 30 townhouses:
- Reception desk opposite the entrance door, backed by the existing stair wall: brushed metal front with a wood triangle and the lettering PALM STREET (the name on the designer's renders), a lower wood counter at its east end. Behind it a terrazzo panel with a TV, wood slats on both sides and a tall black cabinet for keys and parcels.
- Guard 2 sits at the west end of the desk next to the glass door to the stair; he greets guests and helps with luggage.
- Guard 1 sits in the security room at the barrier corner: cameras and radio only, never leaves the post, the room is never left empty. The wall between that room and the lobby stays solid. An opening hatch in the first glazing bay lets drivers talk to him before the barrier.
- Waiting zone: a straight three-seat sofa on the security wall with pictures and two sconces above it, a white and wood coffee table. In the recess of the linen store wall (500 deep, measured): blue pill-shaped wall panels, two white armchairs and a side table. The charging bar of version 5 is gone.
- Blue ceiling with black beams, beige walls, light floor. The viewer has a palette slider that recolours the accent and the ceiling.
- Luggage room with racks; safe-deposit boxes in the cupboard under the stair.

Materials already on site, as used so far (sizes estimated from photos, not measured): six glass panels about 1100 x 2300 as frosted lights in the spa corridor wall, one beside each cabin door; white boards for the lobby coffee table and for the spa lockers, linen shelves and tea console.

Floor 2, spa (test layout):
- Six massage cabins with doors along the window wall, a waiting zone at the stair exit, a staff and linen room, a WC and two showers above the floor 1 toilet.
- All old partitions are removed except the existing enclosure around the stair.

## Open questions

- Whether the outdoor security booth is dropped, and how the guard sees and operates the barrier.
- Where the management company sits.
- Power for the reception desk; where phones are charged now that the charging bar is gone.
- Whether the lettering on the desk stays PALM STREET.
- Measurements still needed: ceiling and beam heights, entrance door height, the stock of glass panels.
- Whether the cross wall under the stair already exists.
- Spa: number of cabins, privacy for the floor-to-ceiling windows, ventilation, air conditioning and electrics.

## Do not

- Do not commit the source drawing, site photos, people's names or contact details. This repository is public.
- Do not edit `v3/`, `v4/` or `v5/`.
- Do not report a page as checked in a browser unless you really opened it.
