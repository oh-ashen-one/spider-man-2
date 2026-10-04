JOB_ARGS = {}

import unreal
print([p for p in dir(unreal.SkyAtmosphereComponent) if 'aerial' in p.lower() or 'perspective' in p.lower() or 'fog' in p.lower()])