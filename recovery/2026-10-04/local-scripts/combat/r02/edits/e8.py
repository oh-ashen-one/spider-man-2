import sys; sys.path.insert(0,'.')
from ed import Ed
b=Ed('/Users/midir/sm2-n1/combat/unreal/WebHomage/Scripts/build_combat.py')
b.rep("""            box(lx - 0.25, y - side * 1.4 - 0.18, 6.5, lx + 0.25, y - side * 1.4 + 0.18, 6.7, 'Lamp%02d_%s_Head' % (i, 'S' if side < 0 else 'N'), lamp, CUBE, 'Furniture')""",
"""            box(lx - 0.25, y - side * 1.4 - 0.18, 6.5, lx + 0.25, y - side * 1.4 + 0.18, 6.7, 'Lamp%02d_%s_Head' % (i, 'S' if side < 0 else 'N'), lamp, CUBE, 'Furniture')
            if abs(lx) <= 48:   # r02 dusk: the lamps near the fight are lit (warm pools on the asphalt, no shadows)
                pl = spawn(unreal.PointLight, (lx * 100, (y - side * 1.4) * 100, 640), label='LampLight%02d_%s' % (i, 'S' if side < 0 else 'N'))
                plc = pl.get_component_by_class(unreal.PointLightComponent)
                plc.set_editor_property('intensity', 9000.0); plc.set_editor_property('attenuation_radius', 1500.0)
                plc.set_editor_property('light_color', unreal.Color(255, 196, 130, 255)); plc.set_editor_property('cast_shadows', False)
                plc.set_editor_property('mobility', unreal.ComponentMobility.MOVABLE)""")
b.rep("""    # ---- lighting: low late-afternoon sun across the street (warm key on the fight, long facade shadows), sky, fog
    sun = spawn(unreal.DirectionalLight, (0, 0, 50000), (0, -24, 128), 'Sun')
    sc = sun.get_component_by_class(unreal.DirectionalLightComponent)
    sc.set_editor_property('intensity', 9.0)
    sc.set_editor_property('light_color', unreal.Color(255, 226, 190, 255))""","""    # ---- lighting (r02 dusk, critic r01: white sky + low contrast flattened the silhouettes): sun 7 deg over the roofs, deep
    # orange, so the street floor is in facade shadow with a warm rim on the fighters; darker sky, thinner fog, lit street lamps
    sun = spawn(unreal.DirectionalLight, (0, 0, 50000), (0, -7, 128), 'Sun')
    sc = sun.get_component_by_class(unreal.DirectionalLightComponent)
    sc.set_editor_property('intensity', 6.0)
    sc.set_editor_property('light_color', unreal.Color(255, 170, 105, 255))""")
b.rep("""    skc.set_editor_property('real_time_capture', True); skc.set_editor_property('mobility', unreal.ComponentMobility.MOVABLE)
    fog = spawn(unreal.ExponentialHeightFog, (0, 0, 0), label='HeightFog')
    fog.get_component_by_class(unreal.ExponentialHeightFogComponent).set_editor_property('fog_density', 0.012)""",
"""    skc.set_editor_property('real_time_capture', True); skc.set_editor_property('mobility', unreal.ComponentMobility.MOVABLE)
    skc.set_editor_property('intensity', 0.6)
    fog = spawn(unreal.ExponentialHeightFog, (0, 0, 0), label='HeightFog')
    fgc = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
    fgc.set_editor_property('fog_density', 0.006)
    try: fgc.set_editor_property('fog_inscattering_luminance', unreal.LinearColor(0.08, 0.07, 0.09, 1.0))
    except Exception as ex: log('fog colour not set: %s' % ex)""")
b.rep("""    ppv = spawn(unreal.PostProcessVolume, (0, 0, 0), label='GlobalPPV'); ppv.set_editor_property('unbound', True)""",
"""    ppv = spawn(unreal.PostProcessVolume, (0, 0, 0), label='GlobalPPV'); ppv.set_editor_property('unbound', True)
    try:
        pps = ppv.get_editor_property('settings')
        for k, v in (('override_auto_exposure_bias', True), ('auto_exposure_bias', -0.6), ('override_vignette_intensity', True), ('vignette_intensity', 0.55),
                     ('override_color_contrast', True), ('color_contrast', unreal.Vector4(1.12, 1.12, 1.12, 1.12)),
                     ('override_color_saturation', True), ('color_saturation', unreal.Vector4(1.08, 1.08, 1.08, 1.0))):
            pps.set_editor_property(k, v)
        ppv.set_editor_property('settings', pps)
    except Exception as ex: log('ppv grade not set: %s' % ex)""")
b.save(); print('ok')
