# -*- mode: python ; coding: utf-8 -*-

import os

# manually include python3.dll (PyInstaller auto-detection misses it)
_python3_dll = os.path.expanduser("~/.wine/drive_c/Python312/python3.dll")
_extra_bins = []
if os.path.exists(_python3_dll):
    _extra_bins.append((_python3_dll, "."))

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=_extra_bins,
    datas=[
        ('data/nikke_characters.json', 'data'),
        ('static\\*', 'static'),
        ('avatars\\*', 'avatars'),
    ],
    hiddenimports=['flask', 'requests', 'PIL'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='nikke-pvp-tracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='nikke-pvp-tracker',
)
