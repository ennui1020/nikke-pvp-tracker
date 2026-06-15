# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('static', 'static'), ('data', 'data'), ('avatars', 'avatars')],
    hiddenimports=['zhconv'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Not used: numpy, cryptography, jedi, IPython
        'numpy', 'numpy.*',
        'cryptography', 'cryptography.*',
        'jedi', 'jedi.*',
        'IPython', 'IPython.*',
        # Not used: scipy, matplotlib
        'scipy', 'scipy.*',
        'matplotlib', 'matplotlib.*',
        'typing_extensions',
        # CLI/dev tools not needed
        'setuptools', 'wheel', 'pip', 'distutils',
        'test', 'unittest', 'doctest',
        'ensurepip',
        # Web framework not needed beyond flask
        'aiohttp', 'asyncio',
        # Database/ORM not used
        'sqlalchemy', 'django',
        # Not used by requests (we don't do streaming/big uploads)
        'chardet',
    ],
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
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
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
    upx=False,
    upx_exclude=[],
    name='nikke-pvp-tracker',
)
