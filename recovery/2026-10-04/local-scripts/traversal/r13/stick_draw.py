import json, sys
from PIL import Image, ImageDraw
d = json.load(open(sys.argv[1])); out = sys.argv[2]
names = sys.argv[3].split(",")
frames = ["0", "8", "12", "16", "18", "22", "30"]
W = 160; img = Image.new("RGB", (W * len(frames), 2 * W * len(names)), "white"); dr = ImageDraw.Draw(img)
for r, n in enumerate(names):
    for c, f in enumerate(frames):
        bones = d[n][f]; hip = bones["hips"][0]
        for view in (0, 1):  # 0 side (y fwd->x, z up), 1 front (x, z)
            ox, oy = c * W + W // 2, (2 * r + view) * W + W // 2
            for b, (h, t) in bones.items():
                col = (200, 0, 0) if b.endswith(".R") else (0, 0, 200) if b.endswith(".L") else (0, 0, 0)
                def P(p):
                    u = -(p[1] - hip[1]) if view == 0 else (p[0] - hip[0])
                    return (ox + u * 70, oy - (p[2] - hip[2]) * 70)
                dr.line([P(h), P(t)], fill=col, width=3)
            dr.text((c * W + 4, (2 * r + view) * W + 4), "%s f%s %s" % (n[4:], f, "side" if view == 0 else "front"), fill=(0, 0, 0))
img.save(out); print("saved", out)
