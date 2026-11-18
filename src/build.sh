#!/usr/bin/env bash
# Rebuild the current version from the sources and place it in the site root and its vN folder.
# Usage: bash src/build.sh      (needs python3 with matplotlib, and node for the smoke test)
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out
python3 model.py
python3 export.py
python3 drawing.py
node smoke.js
V=$(python3 -c "import json;print(json.load(open('model.json'))['version'])")
ROOT=..
mkdir -p "$ROOT/$V"
cp out/index.html "$ROOT/index.html"
sed -e "s#href=\"$V/#href=\"#g" -e 's#href="\(v[0-9][0-9]*\)/"#href="../\1/"#g' out/index.html > "$ROOT/$V/index.html"
cp out/BLM_Lobby.rb  "$ROOT/$V/BLM_Lobby_$V.rb"
cp out/BLM_Lobby.dae "$ROOT/$V/BLM_Lobby_$V.dae"
cp out/BLM_Lobby_plan_F1.dxf out/BLM_Lobby_plan_F2.dxf out/BLM_Lobby_plans_A3_1-50.pdf "$ROOT/$V/"
# the developer's brand name must not appear anywhere on the site (owner's rule)
P="sw"; P="${P}oi"
if grep -rilE "$P" "$ROOT" --exclude-dir=.git; then echo "ERROR: the brand name was found in the files above, remove it"; exit 1; fi
echo "built $V -> site root and /$V/"
