#!/usr/bin/env python3
"""Make an anonymised A/B pack for a critic.

  python3 tools/night1/abpack.py <pack_dir> <pairs.json>

pairs.json: [{"id": "street-canyon", "x": "<path ours>", "y": "<path other>", "note": "camera/view description"}]
For each pair the two files are copied to <pack_dir>/<id>/A.<ext> and B.<ext> in random
order. The key (which of A/B was x) goes to <pack_dir>.key.json, OUTSIDE the pack, so the
critic never sees it. <pack_dir>/PAIRS.md lists ids + neutral view notes only.
"""
import json, os, random, shutil, sys

pack, pairs = sys.argv[1], json.load(open(sys.argv[2]))
os.makedirs(pack, exist_ok=True)
key, lines = {}, ["# Pairs", "", "Each folder holds A and B for the same view or movement. Judge each on its own merits.", ""]
for p in pairs:
    d = os.path.join(pack, p["id"])
    os.makedirs(d, exist_ok=True)
    order = [("x", p["x"]), ("y", p["y"])]
    random.shuffle(order)
    for slot, (who, src) in zip("AB", order):
        ext = os.path.splitext(src)[1].lower()
        shutil.copy2(src, os.path.join(d, slot + ext))
        key.setdefault(p["id"], {})[slot] = who
    lines.append(f"- `{p['id']}/` — {p.get('note', '')}")
open(os.path.join(pack, "PAIRS.md"), "w").write("\n".join(lines) + "\n")
json.dump(key, open(pack.rstrip("/") + ".key.json", "w"), indent=1)
print(f"packed {len(pairs)} pairs -> {pack}")
