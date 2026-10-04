import json, os, struct, subprocess, tempfile

def convert(src, dst):
    """Rewrite a GLB so every EXT_texture_webp image becomes an embedded PNG (sips), extension removed."""
    b = open(src, "rb").read()
    L = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + L])
    off = 20 + L
    BL = struct.unpack("<I", b[off:off + 4])[0]
    binc = b[off + 8: off + 8 + BL]
    views = j["bufferViews"]
    blobs = {i: binc[v.get("byteOffset", 0): v.get("byteOffset", 0) + v["byteLength"]] for i, v in enumerate(views)}
    tmp = tempfile.mkdtemp()
    for ii, im in enumerate(j.get("images", [])):
        if im.get("mimeType") == "image/webp":
            wp, pp = os.path.join(tmp, "i%d.webp" % ii), os.path.join(tmp, "i%d.png" % ii)
            open(wp, "wb").write(blobs[im["bufferView"]])
            subprocess.run(["sips", "-s", "format", "png", wp, "--out", pp], check=True, capture_output=True)
            blobs[im["bufferView"]] = open(pp, "rb").read()
            im["mimeType"] = "image/png"
    for t in j.get("textures", []):
        ext = t.get("extensions", {}).pop("EXT_texture_webp", None)
        if ext is not None:
            t["source"] = ext["source"]
        if "extensions" in t and not t["extensions"]:
            del t["extensions"]
    for k in ("extensionsUsed", "extensionsRequired"):
        if k in j:
            j[k] = [e for e in j[k] if e != "EXT_texture_webp"]
            if not j[k]:
                del j[k]
    out = bytearray()
    for i, v in enumerate(views):
        while len(out) % 4:
            out.append(0)
        v["byteOffset"] = len(out)
        v["byteLength"] = len(blobs[i])
        out += blobs[i]
    while len(out) % 4:
        out.append(0)
    j["buffers"][0]["byteLength"] = len(out)
    js = json.dumps(j, separators=(",", ":")).encode()
    while len(js) % 4:
        js += b" "
    total = 12 + 8 + len(js) + 8 + len(out)
    with open(dst, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack("<II", len(out), 0x004E4942)); f.write(out)
    return dst

if __name__ == "__main__":
    import sys
    print(convert(sys.argv[1], sys.argv[2]))
