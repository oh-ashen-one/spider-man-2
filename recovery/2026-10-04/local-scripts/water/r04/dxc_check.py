"""offline HLSL syntax/semantic check of the water custom-node code with UE's own libdxcompiler (ctypes COM)."""
import ctypes, sys, uuid
L = ctypes.CDLL('/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/ThirdParty/ShaderConductor/Mac/libdxcompiler.dylib')
class GUID(ctypes.Structure):
    _fields_ = [('b', ctypes.c_ubyte * 16)]
def guid(s):
    g = GUID(); g.b[:] = list(uuid.UUID(s).bytes_le); return g
CLSID = guid('73e22d93-e6ce-47f3-b5bf-f0664f39c1b0'); IID3 = guid('228B4687-5A6A-4730-900C-9702B2203F54'); IIDR = guid('58346CDA-DDE7-4497-9461-6F87AF5E0659')
L.DxcCreateInstance.restype = ctypes.c_int32
comp = ctypes.c_void_p()
hr = L.DxcCreateInstance(ctypes.byref(CLSID), ctypes.byref(IID3), ctypes.byref(comp)); assert hr == 0, hr
def vt(obj, i, restype, *argtypes):
    vtbl = ctypes.cast(ctypes.cast(obj, ctypes.POINTER(ctypes.c_void_p))[0], ctypes.POINTER(ctypes.c_void_p))
    return ctypes.CFUNCTYPE(restype, ctypes.c_void_p, *argtypes)(vtbl[i])
class DxcBuffer(ctypes.Structure):
    _fields_ = [('Ptr', ctypes.c_void_p), ('Size', ctypes.c_size_t), ('Encoding', ctypes.c_uint32)]
def compile(src, entry='main', prof='ps_6_0', vt_off=5):
    b = src.encode(); buf = ctypes.create_string_buffer(b)
    db = DxcBuffer(ctypes.cast(buf, ctypes.c_void_p), len(b), 65001)
    args = ['-E', entry, '-T', prof, '-HV', '2018']
    arr = (ctypes.c_wchar_p * len(args))(*args)
    res = ctypes.c_void_p()
    f = vt(comp, vt_off, ctypes.c_int32, ctypes.POINTER(DxcBuffer), ctypes.POINTER(ctypes.c_wchar_p), ctypes.c_uint32, ctypes.c_void_p, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p))
    hr = f(comp, ctypes.byref(db), arr, len(args), None, ctypes.byref(IIDR), ctypes.byref(res)); assert hr == 0, hex(hr & 0xffffffff)
    st = ctypes.c_int32(); vt(res, vt_off, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32))(res, ctypes.byref(st))
    eb = ctypes.c_void_p(); vt(res, vt_off + 2, ctypes.c_int32, ctypes.POINTER(ctypes.c_void_p))(res, ctypes.byref(eb))
    msg = ''
    if eb.value:
        p = vt(eb, vt_off, ctypes.c_void_p)(eb); n = vt(eb, vt_off + 1, ctypes.c_size_t)(eb)
        msg = ctypes.string_at(p, n).decode(errors='replace') if p and n else ''
    return st.value, msg
if __name__ == '__main__':
    code = open(sys.argv[1]).read()
    st, msg = compile(code, prof=sys.argv[2] if len(sys.argv) > 2 else 'ps_6_0')
    print('status', hex(st & 0xffffffff)); print(msg[:6000])
