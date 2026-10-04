import sys
from unittest.mock import MagicMock
class _M(MagicMock):
    pass
m = _M()
m.EditorAssetLibrary.does_asset_exist.return_value = True
m.EditorAssetLibrary.does_directory_exist.return_value = False
sds = m.get_engine_subsystem.return_value
sds.add_new_subobject.return_value = (1, 2)
sds.k2_gather_subobject_data_for_instance.return_value = [1]
sys.modules[__name__] = m
