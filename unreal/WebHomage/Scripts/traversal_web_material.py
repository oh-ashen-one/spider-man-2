# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Piece P3 (traversal), round 25: /Game/Traversal/Materials/M_TravWeb -- the web strand look.
#
# Critic r24 biggest gap (SPEC T5 / T6): the rope must read on every web_on frame of the swing chain, 2-4 px wide, its mean luminance
# >= 25/255 off a 6 px band either side, over dark glass AND pale facades. History: r07 emissive beam bloomed, r08 pale lit line vanished on
# pale facades, r09-r24 dark lit line vanished on dark glass.
#
# M_TravWeb: an UNLIT, translucent (opacity 1 inside the strand, a soft half-pixel edge) two-tone strand on the cylinder segments the pawn
# draws (AWebTravCharacter::UpdateWebs). Across the strand the cylinder's view-facing coordinate u (0 at the centre line, 1 at the silhouette)
# picks a bright CORE (u < c) or a dark RIM. The core share c follows the luminance of the scene right behind the strand (4 scene-colour
# taps ~5 px out, exposure-applied): over a dark background (glass, shadow) the bright core fills CoreDark of the width; over a bright one
# (sky, pale stone) only CoreBright and the dark rim carries the line; the switch sits at Pivot. The output is divided by the eye
# adaptation (EyeAdaptationInverse), so the displayed level is CoreLvl / RimLvl whatever the exposure: no HDR emissive, no bloom.
# No fog on the strand (Apply Fogging off), responsive AA (thin moving line), not lit, casts no shadow (set on the component).
#
# Run from build_traversal.py (materials section), or alone as a commandlet with your editor closed:
#   UnrealEditor <abs uproject> -run=pythonscript -script=<abs path to this file> -unattended -nullrhi
import unreal

MAT_DIR = "/Game/Traversal/Materials"
NAME = "M_TravWeb"

WEB_CODE = r"""
float3 a = normalize(A);
float3 v = normalize(V);
float3 vp = v - a * dot(v, a);
float lv = length(vp);
float u = 0.0;
if (lv > 1e-3)
{
	vp /= lv;
	float nv = saturate(abs(dot(normalize(N), vp)));
	u = sqrt(saturate(1.0 - nv * nv));
}
float inv = max(Inv.x, 1e-8);
float lb = dot((S0.rgb + S1.rgb + S2.rgb + S3.rgb) * 0.25, float3(0.2126, 0.7152, 0.0722)) / inv;
float dark = 1.0 - smoothstep(Pivot * 0.95, Pivot * 1.05, lb);
float lvl;
if (Solid > 0.5)
{
	// build 2: ONE tone across the whole strand -- bright over a dark background, near-black over a bright one (a two-tone core/rim
	// averaged back to the background's level once the 3-4 px strand was resolved)
	lvl = lerp(RimLvl, CoreLvl, dark);
}
else
{
	float c = lerp(CoreBright, CoreDark, dark);
	float core = 1.0 - smoothstep(c - 0.05, c + 0.05, u);
	lvl = lerp(RimLvl, CoreLvl, core);
}
float alpha = 1.0 - smoothstep(0.92, 1.0, u);
// build 2: the strand draws after motion blur (no engine depth test there) -- test against the opaque scene depth by hand
alpha *= (SD < PD - Occ) ? 0.0 : 1.0;
return float4(lvl, lvl, lvl, alpha);
"""

PARAMS = [("CoreBright", 0.30), ("CoreDark", 0.86), ("Pivot", 0.20), ("CoreLvl", 1.6), ("RimLvl", 0.004), ("Solid", 1.0), ("Occ", 25.0)]


def _set(obj, prop, value):
    try:
        obj.set_editor_property(prop, value)
        return True
    except Exception as e:  # noqa: BLE001 -- report and go on (an engine-version property rename must not abort the content build)
        unreal.log_warning(f"TRAVWEB: could not set {prop} on {obj.get_name()}: {e}")
        return False


def build(eal=None, mel=None, tools=None):
    eal = eal or unreal.EditorAssetLibrary
    mel = mel or unreal.MaterialEditingLibrary
    tools = tools or unreal.AssetToolsHelpers.get_asset_tools()
    path = f"{MAT_DIR}/{NAME}"
    if not eal.does_directory_exist(MAT_DIR):
        eal.make_directory(MAT_DIR)
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    m = tools.create_asset(NAME, MAT_DIR, unreal.Material, unreal.MaterialFactoryNew())
    _set(m, "blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    _set(m, "shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    # build 2: after motion blur -- before DOF the camera-speed blur of the background smeared the 3 px strand into it
    if not _set(m, "translucency_pass", unreal.MaterialTranslucencyPass.MTP_AFTER_MOTION_BLUR):
        _set(m, "translucency_pass", unreal.MaterialTranslucencyPass.MTP_BEFORE_DOF)
    _set(m, "use_translucency_vertex_fog", False)   # "Apply Fogging"
    _set(m, "enable_responsive_aa", True)
    _set(m, "two_sided", False)

    def expr(cls, x, y):
        return mel.create_material_expression(m, cls, x, y)

    nrm = expr(unreal.MaterialExpressionVertexNormalWS, -1200, -300)
    cam = expr(unreal.MaterialExpressionCameraVectorWS, -1200, -180)
    zc = expr(unreal.MaterialExpressionConstant3Vector, -1400, -60)
    _set(zc, "constant", unreal.LinearColor(0.0, 0.0, 1.0, 0.0))
    ax = expr(unreal.MaterialExpressionTransform, -1200, -60)
    _set(ax, "transform_source_type", unreal.MaterialVectorCoordTransformSource.TRANSFORMSOURCE_LOCAL)
    _set(ax, "transform_type", unreal.MaterialVectorCoordTransform.TRANSFORM_WORLD)
    mel.connect_material_expressions(zc, "", ax, "")
    # scene colour taps ~5 px out at 1080p (offset fraction of the view)
    taps = []
    for i, (ox, oy) in enumerate(((0.0026, 0.0), (-0.0026, 0.0), (0.0, 0.0046), (0.0, -0.0046))):
        sc = expr(unreal.MaterialExpressionSceneColor, -1200, 80 + i * 120)
        _set(sc, "input_mode", unreal.MaterialSceneAttributeInputMode.OFFSET_FRACTION)
        _set(sc, "const_input", unreal.Vector2D(ox, oy))
        taps.append(sc)
    inv = expr(unreal.MaterialExpressionEyeAdaptationInverse, -1200, 600)
    sd = expr(unreal.MaterialExpressionSceneDepth, -1200, 1500)
    pd = expr(unreal.MaterialExpressionPixelDepth, -1200, 1600)
    pars = {}
    for i, (n, d) in enumerate(PARAMS):
        p = expr(unreal.MaterialExpressionScalarParameter, -1200, 720 + i * 90)
        _set(p, "parameter_name", n)
        _set(p, "default_value", d)
        pars[n] = p
    cu = expr(unreal.MaterialExpressionCustom, -700, 0)
    _set(cu, "code", WEB_CODE)
    _set(cu, "output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT4)
    names = ["N", "V", "A", "S0", "S1", "S2", "S3", "Inv", "SD", "PD"] + [n for n, _ in PARAMS]
    ins = []
    for n in names:
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", n)
        ins.append(ci)
    _set(cu, "inputs", ins)
    ok = True
    ok &= mel.connect_material_expressions(nrm, "", cu, "N")
    ok &= mel.connect_material_expressions(cam, "", cu, "V")
    ok &= mel.connect_material_expressions(ax, "", cu, "A")
    for i, sc in enumerate(taps):
        ok &= mel.connect_material_expressions(sc, "", cu, f"S{i}")
    ok &= mel.connect_material_expressions(inv, "", cu, "Inv")
    ok &= mel.connect_material_expressions(sd, "", cu, "SD")
    ok &= mel.connect_material_expressions(pd, "", cu, "PD")
    for n, p in pars.items():
        ok &= mel.connect_material_expressions(p, "", cu, n)
    rgb = expr(unreal.MaterialExpressionComponentMask, -450, 0)
    for c, v in (("r", True), ("g", True), ("b", True), ("a", False)):
        _set(rgb, c, v)
    al = expr(unreal.MaterialExpressionComponentMask, -450, 200)
    for c, v in (("r", False), ("g", False), ("b", False), ("a", True)):
        _set(al, c, v)
    ok &= mel.connect_material_expressions(cu, "", rgb, "")
    ok &= mel.connect_material_expressions(cu, "", al, "")
    # displayed level = CoreLvl / RimLvl at any exposure: divide by the eye adaptation
    inv2 = expr(unreal.MaterialExpressionEyeAdaptationInverse, -250, 0)
    ok &= mel.connect_material_expressions(rgb, "", inv2, "")
    ok &= mel.connect_material_property(inv2, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    ok &= mel.connect_material_property(al, "", unreal.MaterialProperty.MP_OPACITY)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    unreal.log(f"TRAVWEB: built {path} connections_ok={bool(ok)} expressions={mel.get_num_material_expressions(m)} pass={m.get_editor_property('translucency_pass')}")
    return m


if __name__ == "__main__":
    build()
