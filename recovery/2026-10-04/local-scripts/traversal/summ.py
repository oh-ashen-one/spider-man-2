import csv, sys
rows = list(csv.DictReader(open(sys.argv[1])))
step = int(sys.argv[2]) if len(sys.argv) > 2 else 15
print(len(rows), "rows")
for r in rows[::step]:
    print(f"t={float(r['t']):6.2f} {r['mode']:6s} {r['sub']:12s} pos=({float(r['x_m']):7.1f},{float(r['y_m']):6.1f},{float(r['z_m']):6.1f}) v={float(r['speed_mps']):5.1f} vz={float(r['vz']):6.1f} hf={float(r['height_above_floor_m']):6.1f} rope={float(r['rope_m']):5.1f} chain={r['chain']} trick={r['trick']} fov={float(r['cam_vfov_deg']):5.1f} camd={float(r['cam_dist_m']):4.1f} zt={r['zip_target']}")
